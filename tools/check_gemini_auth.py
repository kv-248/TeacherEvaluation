from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def get_api_key() -> str | None:
    for env_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return None


def normalize_model_name(model_name: str) -> str:
    value = str(model_name or "").strip()
    if value.startswith("models/"):
        value = value.split("/", 1)[1]
    return value


def sanitize_error_message(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    lowered = text.lower()
    if any(marker in lowered for marker in ("quota exceeded", "resource_exhausted", "rate limit", "http 429")):
        return "quota exceeded"
    if any(marker in lowered for marker in ("api key", "permission denied", "unauthorized", "http 401", "http 403")):
        return "authentication failed"
    if any(marker in lowered for marker in ("backend unavailable", "service unavailable", "temporarily unavailable", "http 500", "http 502", "http 503", "http 504")):
        return "service unavailable"
    if any(marker in lowered for marker in ("timed out", "timeout")):
        return "request timed out"
    if any(marker in lowered for marker in ("network is unreachable", "connection refused", "connection reset", "request failed")):
        return "request failed"
    if any(marker in lowered for marker in ("not found", "http 404")):
        return "model unavailable"
    return "request failed"


def _http_json(request: urllib.request.Request, timeout_sec: int) -> tuple[int, dict[str, Any]]:
    with urllib.request.urlopen(request, timeout=timeout_sec) as response:
        status = int(getattr(response, "status", 200))
        payload = json.loads(response.read().decode("utf-8"))
    return status, payload


def check_models_endpoint(api_key: str, timeout_sec: int) -> tuple[bool, str]:
    url = f"{MODELS_URL}?key={urllib.parse.quote(api_key, safe='')}"
    request = urllib.request.Request(url, method="GET")
    try:
        status, payload = _http_json(request, timeout_sec)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, f"models endpoint failed: HTTP {exc.code} ({sanitize_error_message(body)})"
    except urllib.error.URLError as exc:
        return False, f"models endpoint failed: {sanitize_error_message(exc.reason)}"

    models = payload.get("models") or []
    return True, f"models endpoint ok: HTTP {status}, discovered {len(models)} models"


def check_generate_content(api_key: str, model_name: str, timeout_sec: int) -> tuple[bool, str]:
    model = normalize_model_name(model_name)
    url = GENERATE_URL.format(model=urllib.parse.quote(model, safe=""))
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": 'Return {"ok": true} as JSON.'},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 32,
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingBudget": -1} if model.startswith("gemini-2.5-pro") else {"thinkingBudget": 0} if model.startswith("gemini-2.5-flash") else None,
        },
    }
    if payload["generationConfig"]["thinkingConfig"] is None:
        payload["generationConfig"].pop("thinkingConfig")

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        status, _payload = _http_json(request, timeout_sec)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, f"generateContent failed for {model}: HTTP {exc.code} ({sanitize_error_message(body)})"
    except urllib.error.URLError as exc:
        return False, f"generateContent failed for {model}: {sanitize_error_message(exc.reason)}"
    return True, f"generateContent ok for {model}: HTTP {status}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether the current Gemini API key is present and valid for a target model.")
    parser.add_argument("--model", default="gemini-2.5-pro", help="Gemini model to probe with a tiny generateContent request.")
    parser.add_argument("--timeout-sec", type=int, default=30, help="HTTP timeout in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = get_api_key()
    if not api_key:
        print("Gemini API key missing: set GEMINI_API_KEY or GOOGLE_API_KEY.", file=sys.stderr)
        return 2

    print("Gemini key present: True")

    models_ok, models_message = check_models_endpoint(api_key, args.timeout_sec)
    print(models_message)
    if not models_ok:
        print("Next step: verify the key value, the project bound to the key, and that the Gemini API is enabled for that project.", file=sys.stderr)
        return 1

    content_ok, content_message = check_generate_content(api_key, args.model, args.timeout_sec)
    print(content_message)
    if not content_ok:
        print(
            "Next step: if the key is valid but this model probe fails, check whether the key/project has access to the requested model "
            f"({normalize_model_name(args.model)}), or temporarily test a different Gemini model.",
            file=sys.stderr,
        )
        return 1

    print("Gemini auth preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
