from __future__ import annotations

import ast
import base64
import json
import mimetypes
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
_MAX_RETRIES = 4
_INITIAL_BACKOFF_SEC = 1.5
_MAX_BACKOFF_SEC = 12.0
_JITTER_SEC = 0.35


def is_gemini_model(model_name: str) -> bool:
    normalized = normalize_gemini_model_name(model_name)
    return normalized.startswith("gemini-")


def normalize_gemini_model_name(model_name: str) -> str:
    value = str(model_name or "").strip()
    if value.startswith("models/"):
        value = value.split("/", 1)[1]
    return value


def get_gemini_api_key() -> str | None:
    for env_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return None


def _supports_thinking_budget_zero(model_name: str) -> bool:
    model = normalize_gemini_model_name(model_name)
    return model.startswith("gemini-2.5-flash")


def _image_part(image_path: Path) -> dict[str, Any]:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if not mime_type:
        mime_type = "image/jpeg"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": data,
        }
    }


def _extract_response_text(response_json: dict[str, Any]) -> str:
    candidates = response_json.get("candidates") or []
    if not candidates:
        error = response_json.get("error")
        if error:
            raise RuntimeError(f"Gemini API error: {error}")
        raise RuntimeError("Gemini API returned no candidates.")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    text_parts = [str(part.get("text", "")).strip() for part in parts if part.get("text")]
    text = "\n".join(part for part in text_parts if part).strip()
    if not text:
        finish_reason = candidates[0].get("finishReason", "unknown")
        raise RuntimeError(f"Gemini API returned no text content. finishReason={finish_reason}")
    return text


def _transient_http_retry_after(exc: urllib.error.HTTPError) -> float | None:
    retry_after = exc.headers.get("Retry-After")
    if retry_after is None:
        return None
    try:
        value = float(retry_after)
    except ValueError:
        return None
    return max(value, 0.0)


def _is_retryable_http_error(exc: urllib.error.HTTPError, body: str) -> bool:
    if exc.code in _TRANSIENT_HTTP_CODES:
        return True
    lowered = body.lower()
    return any(
        marker in lowered
        for marker in (
            "resource_exhausted",
            "rate limit",
            "quota exceeded",
            "backend unavailable",
            "service unavailable",
            "temporarily unavailable",
        )
    )


def _is_retryable_url_error(exc: urllib.error.URLError) -> bool:
    reason = str(exc.reason).lower()
    return any(
        marker in reason
        for marker in (
            "timed out",
            "timeout",
            "temporarily unavailable",
            "temporary failure",
            "connection reset",
            "connection aborted",
            "connection refused",
            "network is unreachable",
            "name or service not known",
            "service unavailable",
        )
    )


def _backoff_delay(attempt_index: int, retry_after: float | None = None) -> float:
    if retry_after is not None:
        return min(max(retry_after, 0.0), _MAX_BACKOFF_SEC)
    delay = min(_INITIAL_BACKOFF_SEC * (2 ** max(attempt_index, 0)), _MAX_BACKOFF_SEC)
    jitter = random.uniform(0.0, _JITTER_SEC)
    return delay + jitter


def _clean_json_text(text: str) -> str:
    cleaned = text.strip().lstrip("\ufeff")
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()
    cleaned = re.sub(r"^\s*json\s*[:\n\r]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = (
        cleaned.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )
    return cleaned


def _extract_json_fragment(text: str) -> str:
    cleaned = _clean_json_text(text)
    if not cleaned:
        raise ValueError("Empty model output.")

    for opening, closing in (("{", "}"), ("[", "]")):
        start = cleaned.find(opening)
        end = cleaned.rfind(closing)
        if start != -1 and end != -1 and end > start:
            fragment = cleaned[start : end + 1].strip()
            if fragment:
                return fragment
    return cleaned


def _repair_json_candidate(text: str) -> str:
    repaired = _clean_json_text(text)
    repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)
    repaired = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)", r'\1"\2"\3', repaired)

    def _replace_bare_value(match: re.Match[str]) -> str:
        prefix, value, suffix = match.groups()
        normalized = value.strip()
        lower_value = normalized.lower()
        if lower_value in {"true", "false", "null"}:
            return f"{prefix}{lower_value}{suffix}"
        if lower_value == "none":
            return f"{prefix}null{suffix}"
        if re.fullmatch(r"-?\d+(?:\.\d+)?", normalized):
            return f"{prefix}{normalized}{suffix}"
        return f'{prefix}"{normalized}"{suffix}'

    repaired = re.sub(r'(:\s*)([A-Za-z_][A-Za-z0-9_.-]*)(\s*[,}\]])', _replace_bare_value, repaired)
    return repaired


def _coerce_schema_string(value: str) -> str:
    text = value.strip().strip(",")
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1]
    return text.strip()


def _salvage_schema_object(text: str, schema: dict[str, Any] | None) -> dict[str, Any] | None:
    if not schema:
        return None
    properties = schema.get("properties")
    if not isinstance(properties, dict) or not properties:
        return None

    cleaned = _clean_json_text(text)
    salvaged: dict[str, Any] = {}
    for key, spec in properties.items():
        if not isinstance(key, str) or not isinstance(spec, dict):
            continue
        pattern = re.compile(
            rf'["\']?{re.escape(key)}["\']?\s*[:=]\s*(.+?)(?=(?:[,}}\n\r]+\s*["\']?[A-Za-z_][A-Za-z0-9_]*["\']?\s*[:=])|(?:\s*$))',
            flags=re.DOTALL,
        )
        match = pattern.search(cleaned)
        if not match:
            continue
        raw_value = match.group(1).strip()
        if spec.get("type") == "boolean":
            lowered = raw_value.strip().strip(",").lower()
            if lowered in {"true", "yes", "1"}:
                salvaged[key] = True
            elif lowered in {"false", "no", "0"}:
                salvaged[key] = False
        else:
            salvaged[key] = _coerce_schema_string(raw_value)

    return salvaged if salvaged else None


def _parse_json_like_text(text: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
    candidates: list[str] = []
    for candidate in (
        _clean_json_text(text),
        _extract_json_fragment(text),
        _repair_json_candidate(text),
        _repair_json_candidate(_extract_json_fragment(text)),
    ):
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
        else:
            if isinstance(value, dict):
                return value
            raise ValueError("Gemini response JSON must be an object.")

        try:
            value = ast.literal_eval(candidate)
        except (SyntaxError, ValueError) as exc:
            last_error = exc
            continue
        if isinstance(value, dict):
            return value
        raise ValueError("Gemini response JSON must be an object.")

    salvaged = _salvage_schema_object(text, schema)
    if isinstance(salvaged, dict):
        return salvaged

    raise ValueError(f"Could not parse Gemini JSON response: {last_error}")


def generate_gemini_json(
    *,
    model_name: str,
    system_instruction: str,
    user_text: str,
    image_paths: list[Path] | None = None,
    max_output_tokens: int,
    temperature: float,
    response_json_schema: dict[str, Any] | None = None,
    timeout_sec: int = 180,
) -> tuple[dict[str, Any], str]:
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY.")

    model = normalize_gemini_model_name(model_name)
    url = GEMINI_API_URL.format(model=urllib.parse.quote(model, safe=""))

    parts: list[dict[str, Any]] = [{"text": user_text}]
    for image_path in image_paths or []:
        parts.append(_image_part(image_path))

    def _request(current_system_instruction: str, current_temperature: float) -> tuple[dict[str, Any], str]:
        payload: dict[str, Any] = {
            "systemInstruction": {
                "parts": [{"text": current_system_instruction}],
            },
            "contents": [
                {
                    "parts": parts,
                }
            ],
            "generationConfig": {
                "temperature": float(current_temperature),
                "maxOutputTokens": int(max_output_tokens),
                "responseMimeType": "application/json",
            },
        }
        if response_json_schema is not None:
            payload["generationConfig"]["responseJsonSchema"] = response_json_schema
        if _supports_thinking_budget_zero(model):
            payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 0}

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )
        last_error: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                with urllib.request.urlopen(request, timeout=timeout_sec) as response:
                    response_json = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                retryable = _is_retryable_http_error(exc, body)
                if not retryable or attempt >= _MAX_RETRIES:
                    raise RuntimeError(f"Gemini API HTTP {exc.code}: {body}") from exc
                delay = _backoff_delay(attempt, _transient_http_retry_after(exc))
                last_error = RuntimeError(
                    f"Gemini API transient HTTP {exc.code}; retry {attempt + 1}/{_MAX_RETRIES} in {delay:.1f}s"
                )
                time.sleep(delay)
            except urllib.error.URLError as exc:
                retryable = _is_retryable_url_error(exc)
                if not retryable or attempt >= _MAX_RETRIES:
                    raise RuntimeError(f"Gemini API request failed: {exc.reason}") from exc
                delay = _backoff_delay(attempt)
                last_error = RuntimeError(
                    f"Gemini API transient request error; retry {attempt + 1}/{_MAX_RETRIES} in {delay:.1f}s: {exc.reason}"
                )
                time.sleep(delay)
        else:
            raise RuntimeError(f"Gemini API retries exhausted: {last_error}")

        text = _extract_response_text(response_json)
        return _parse_json_like_text(text, response_json_schema), text

    try:
        return _request(system_instruction, temperature)
    except ValueError as first_exc:
        strict_system_instruction = (
            f"{system_instruction.rstrip()} "
            "Return only a single JSON object that matches the schema. "
            "Do not include markdown, code fences, or extra prose."
        ).strip()
        if strict_system_instruction == system_instruction.strip() and float(temperature) <= 0.0:
            raise
        try:
            return _request(strict_system_instruction, 0.0)
        except Exception as second_exc:
            raise RuntimeError(
                f"Gemini JSON generation failed after retry: {type(first_exc).__name__}: {first_exc}; "
                f"retry={type(second_exc).__name__}: {second_exc}"
            ) from second_exc
