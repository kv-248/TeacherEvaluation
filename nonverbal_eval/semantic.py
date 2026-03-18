from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pandas as pd

from .gemini_api import generate_gemini_json
from .pipeline import log_event
from .runtime_config import load_qwen_prompt_config


_QWEN_CONFIG = load_qwen_prompt_config()["frame_semantic_review"]


@dataclass(slots=True)
class SemanticConfig:
    enabled: bool = False
    sample_interval_sec: float = 6.0
    max_samples: int = 8
    qwen_enabled: bool = True
    qwen_model: str = str(_QWEN_CONFIG["model"])
    qwen_max_new_tokens: int = int(_QWEN_CONFIG["max_new_tokens"])
    qwen_temperature: float = float(_QWEN_CONFIG["temperature"])


@dataclass(slots=True)
class SemanticArtifacts:
    root_dir: Path
    sampled_frames_dir: Path
    contact_sheet_path: Path
    qwen_annotations_path: Path
    summary_json_path: Path
    summary_md_path: Path


@dataclass(slots=True)
class SemanticSample:
    timestamp_sec: float
    reason: str
    image_path: Path
    frame_bgr: np.ndarray
    frame_shape: tuple[int, int, int]


QWEN_PROMPT = str(_QWEN_CONFIG["prompt"])

ALLOWED_QWEN_VALUES = {
    "teacher_focus": {"audience", "board", "screen", "notes", "ambiguous"},
    "body_action": {
        "open_palm_explaining",
        "pointing_board",
        "pointing_screen",
        "writing_board",
        "walking",
        "static_stance",
        "reading_from_notes",
        "ambiguous",
    },
    "affect_tone": {"warm", "neutral", "tense", "ambiguous"},
    "posture_signal": {"upright_open", "upright_neutral", "closed_or_slouched", "ambiguous"},
    "evidence_confidence": {"low", "medium", "high"},
}


def _json_candidate_text(text: str) -> str:
    cleaned = text.strip().lstrip("\ufeff")
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()
    return cleaned


def _json_fragment(text: str) -> str:
    cleaned = _json_candidate_text(text)
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


def _extract_json_blob(text: str) -> dict[str, Any]:
    candidates: list[str] = []
    for candidate in (_json_candidate_text(text), _json_fragment(text)):
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if isinstance(value, dict):
            return value
        raise ValueError("Model output JSON must be an object.")

    raise ValueError(f"Could not parse JSON blob: {last_error}")


def _gemini_annotation_schema() -> dict[str, Any]:
    properties = {
        "teacher_focus": {
            "type": "string",
            "enum": sorted(ALLOWED_QWEN_VALUES["teacher_focus"]),
            "description": "Primary focus target in the frame.",
        },
        "body_action": {
            "type": "string",
            "enum": sorted(ALLOWED_QWEN_VALUES["body_action"]),
            "description": "Observed body action in the frame.",
        },
        "affect_tone": {
            "type": "string",
            "enum": sorted(ALLOWED_QWEN_VALUES["affect_tone"]),
            "description": "Observed affect tone.",
        },
        "posture_signal": {
            "type": "string",
            "enum": sorted(ALLOWED_QWEN_VALUES["posture_signal"]),
            "description": "Observed posture signal.",
        },
        "attention_note": {
            "type": "string",
            "description": "Short note about attention cues.",
        },
        "evidence_confidence": {
            "type": "string",
            "enum": sorted(ALLOWED_QWEN_VALUES["evidence_confidence"]),
            "description": "Confidence in the annotation.",
        },
        "rationale": {
            "type": "string",
            "description": "Short rationale for the annotation.",
        },
    }
    property_ordering = list(properties.keys())
    return {
        "type": "object",
        "properties": properties,
        "required": property_ordering,
        "additionalProperties": False,
        "propertyOrdering": property_ordering,
    }


def _build_qwen_annotation(sample: SemanticSample, parsed: dict[str, Any], raw_text: str) -> dict[str, Any]:
    annotation = {
        "timestamp_sec": sample.timestamp_sec,
        "reason": sample.reason,
        "raw_text": raw_text.strip(),
        "teacher_focus": str(parsed.get("teacher_focus", "ambiguous")).strip(),
        "body_action": str(parsed.get("body_action", "ambiguous")).strip(),
        "affect_tone": str(parsed.get("affect_tone", "ambiguous")).strip(),
        "posture_signal": str(parsed.get("posture_signal", "ambiguous")).strip(),
        "attention_note": _sanitize_short_text(parsed.get("attention_note", ""), max_words=12),
        "evidence_confidence": str(parsed.get("evidence_confidence", "medium")).strip(),
        "rationale": _sanitize_short_text(parsed.get("rationale", ""), max_words=20),
    }
    for field, allowed_values in ALLOWED_QWEN_VALUES.items():
        if annotation[field] not in allowed_values:
            annotation[field] = "ambiguous" if "ambiguous" in allowed_values else "medium"
    return annotation


def build_semantic_artifacts(run_dir: Path) -> SemanticArtifacts:
    root_dir = run_dir / "semantic_extensions"
    sampled_frames_dir = root_dir / "sampled_frames"
    sampled_frames_dir.mkdir(parents=True, exist_ok=True)
    return SemanticArtifacts(
        root_dir=root_dir,
        sampled_frames_dir=sampled_frames_dir,
        contact_sheet_path=root_dir / "semantic_contact_sheet.jpg",
        qwen_annotations_path=root_dir / "qwen_annotations.json",
        summary_json_path=root_dir / "semantic_summary.json",
        summary_md_path=root_dir / "semantic_summary.md",
    )


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator / denominator)


def _sanitize_short_text(value: Any, max_words: int) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    words = text.split(" ")
    if len(words) > max_words:
        text = " ".join(words[:max_words])
    return text


def _choose_timestamps(frame_metrics_df: pd.DataFrame, clip_duration_sec: float, interval_sec: float, max_samples: int) -> list[tuple[float, str]]:
    reason_map: dict[float, list[str]] = {}

    def add_reason(timestamp: float, reason: str) -> None:
        bounded = float(np.clip(timestamp, 0.0, max(clip_duration_sec - 1e-3, 0.0)))
        key = round(bounded, 2)
        if key not in reason_map:
            reason_map[key] = []
        if reason not in reason_map[key]:
            reason_map[key].append(reason)

    add_reason(0.0, "clip_start")
    add_reason(clip_duration_sec / 2.0, "clip_midpoint")
    add_reason(max(clip_duration_sec - 0.25, 0.0), "clip_end")

    if interval_sec > 0:
        current = 0.0
        while current <= clip_duration_sec + 1e-6:
            add_reason(current, "uniform_sample")
            current += interval_sec

    scalar_columns = {
        "gesture_motion": ("peak_gesture_motion", "high"),
        "audience_orientation_score_frame": ("peak_audience_orientation", "high"),
        "smile_proxy": ("peak_smile_proxy", "high"),
        "posture_score_frame": ("peak_posture", "high"),
    }
    for column, (label, mode) in scalar_columns.items():
        if column not in frame_metrics_df.columns or frame_metrics_df[column].dropna().empty:
            continue
        series = frame_metrics_df[column]
        idx = series.idxmax() if mode == "high" else series.idxmin()
        add_reason(float(frame_metrics_df.loc[idx, "timestamp_sec"]), label)

    if "audience_orientation_score_frame" in frame_metrics_df.columns and frame_metrics_df["audience_orientation_score_frame"].dropna().size:
        idx = frame_metrics_df["audience_orientation_score_frame"].idxmin()
        add_reason(float(frame_metrics_df.loc[idx, "timestamp_sec"]), "low_audience_orientation")

    ordered = sorted(reason_map.items(), key=lambda item: item[0])
    merged: list[tuple[float, list[str]]] = []
    for timestamp, reasons in ordered:
        if not merged or abs(timestamp - merged[-1][0]) > max(interval_sec * 0.35, 1.0):
            merged.append((timestamp, list(reasons)))
        else:
            for reason in reasons:
                if reason not in merged[-1][1]:
                    merged[-1][1].append(reason)

    if len(merged) > max_samples:
        indices = np.linspace(0, len(merged) - 1, max_samples, dtype=int)
        merged = [merged[index] for index in sorted(set(indices.tolist()))]

    return [(timestamp, ",".join(reasons)) for timestamp, reasons in merged]


def _extract_frame_at(video_path: Path, timestamp_sec: float) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video for semantic sampling: {video_path}")
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000.0)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not extract frame at {timestamp_sec:.2f}s from {video_path}")
    return frame


def _save_sampled_frames(
    clip_path: Path,
    frame_metrics_df: pd.DataFrame,
    artifacts: SemanticArtifacts,
    config: SemanticConfig,
    events_path: Path,
    clip_duration_sec: float,
) -> list[SemanticSample]:
    selections = _choose_timestamps(frame_metrics_df, clip_duration_sec, config.sample_interval_sec, config.max_samples)
    samples: list[SemanticSample] = []
    for index, (timestamp_sec, reason) in enumerate(selections):
        frame_bgr = _extract_frame_at(clip_path, timestamp_sec)
        image_path = artifacts.sampled_frames_dir / f"frame_{index:02d}_{timestamp_sec:06.2f}s.jpg"
        cv2.imwrite(str(image_path), frame_bgr)
        samples.append(
            SemanticSample(
                timestamp_sec=timestamp_sec,
                reason=reason,
                image_path=image_path,
                frame_bgr=frame_bgr,
                frame_shape=frame_bgr.shape,
            )
        )
    log_event(
        events_path,
        "semantic_samples_selected",
        sample_count=len(samples),
        timestamps_sec=[round(sample.timestamp_sec, 2) for sample in samples],
        reasons=[sample.reason for sample in samples],
    )
    return samples


def _run_qwen(
    samples: list[SemanticSample],
    config: SemanticConfig,
    events_path: Path,
    event_name: str = "semantic_qwen_completed",
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "skipped",
        "reason": "Semantic model analysis disabled.",
        "model": config.qwen_model,
        "annotations": [],
        "aggregate": {},
    }
    if not config.qwen_enabled:
        return result

    annotations: list[dict[str, Any]] = []
    try:
        for sample in samples:
            parsed, raw_text = generate_gemini_json(
                model_name=config.qwen_model,
                system_instruction=(
                    "You are reviewing a single frame from a classroom lecture video. "
                    "Return only the JSON object that matches the schema. "
                    "Use only the allowed enum values for categorical fields."
                ),
                user_text=QWEN_PROMPT,
                image_paths=[sample.image_path],
                max_output_tokens=max(int(config.qwen_max_new_tokens), 192),
                temperature=0.0,
                response_json_schema=_gemini_annotation_schema(),
            )
            annotations.append(_build_qwen_annotation(sample, parsed, raw_text))
    except Exception as exc:
        result["status"] = "failed"
        result["reason"] = f"Gemini semantic inference failed: {type(exc).__name__}: {exc}"
        return result

    focus_counts = pd.Series([row["teacher_focus"] for row in annotations]).value_counts().to_dict()
    action_counts = pd.Series([row["body_action"] for row in annotations]).value_counts().to_dict()
    affect_counts = pd.Series([row["affect_tone"] for row in annotations]).value_counts().to_dict()
    posture_counts = pd.Series([row["posture_signal"] for row in annotations]).value_counts().to_dict()
    annotation_count = max(len(annotations), 1)
    aggregate = {
        "sample_count": len(annotations),
        "audience_focus_ratio": _safe_ratio(focus_counts.get("audience", 0), annotation_count),
        "board_focus_ratio": _safe_ratio(focus_counts.get("board", 0), annotation_count),
        "screen_focus_ratio": _safe_ratio(focus_counts.get("screen", 0), annotation_count),
        "notes_focus_ratio": _safe_ratio(focus_counts.get("notes", 0), annotation_count),
        "open_palm_explaining_ratio": _safe_ratio(action_counts.get("open_palm_explaining", 0), annotation_count),
        "static_stance_ratio": _safe_ratio(action_counts.get("static_stance", 0), annotation_count),
        "pointing_ratio": _safe_ratio(
            action_counts.get("pointing_board", 0) + action_counts.get("pointing_screen", 0), annotation_count
        ),
        "writing_ratio": _safe_ratio(action_counts.get("writing_board", 0), annotation_count),
        "warm_affect_ratio": _safe_ratio(affect_counts.get("warm", 0), annotation_count),
        "tense_affect_ratio": _safe_ratio(affect_counts.get("tense", 0), annotation_count),
        "closed_or_slouched_ratio": _safe_ratio(posture_counts.get("closed_or_slouched", 0), annotation_count),
        "focus_counts": focus_counts,
        "action_counts": action_counts,
        "affect_counts": affect_counts,
        "posture_counts": posture_counts,
    }
    result.update(
        {
            "status": "completed",
            "reason": "Gemini semantic analysis completed.",
            "device": "gemini_api",
            "annotations": annotations,
            "aggregate": aggregate,
        }
    )
    if event_name:
        log_event(
            events_path,
            event_name,
            sample_count=len(annotations),
            focus_counts=focus_counts,
            action_counts=action_counts,
            affect_counts=affect_counts,
        )
    return result


def _build_contact_sheet(
    samples: list[SemanticSample],
    qwen_result: dict[str, Any],
    output_path: Path,
) -> None:
    if not samples:
        return

    qwen_lookup = {round(row["timestamp_sec"], 2): row for row in qwen_result.get("annotations", [])}
    tile_w = 640
    tile_h = 360
    cols = 2
    rows = int(math.ceil(len(samples) / cols))
    canvas = np.full((rows * tile_h, cols * tile_w, 3), 245, dtype=np.uint8)

    for index, sample in enumerate(samples):
        row_idx = index // cols
        col_idx = index % cols
        tile = cv2.resize(sample.frame_bgr, (tile_w, tile_h))
        overlay = tile.copy()

        qwen_row = qwen_lookup.get(round(sample.timestamp_sec, 2))

        cv2.rectangle(overlay, (10, tile_h - 110), (tile_w - 10, tile_h - 10), (0, 0, 0), thickness=-1)
        cv2.putText(
            overlay,
            f"t={sample.timestamp_sec:.2f}s  {sample.reason}",
            (22, tile_h - 74),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.68,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        if qwen_row:
            cv2.putText(
                overlay,
                f"Semantic focus={qwen_row['teacher_focus']}  action={qwen_row['body_action']}",
                (22, tile_h - 46),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                overlay,
                f"affect={qwen_row['affect_tone']}  posture={qwen_row['posture_signal']}",
                (22, tile_h - 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
        tile = cv2.addWeighted(overlay, 0.72, tile, 0.28, 0.0)
        y0 = row_idx * tile_h
        x0 = col_idx * tile_w
        canvas[y0 : y0 + tile_h, x0 : x0 + tile_w] = tile

    cv2.imwrite(str(output_path), canvas)


def _base_to_semantic_agreement(summary: dict[str, Any], qwen_result: dict[str, Any]) -> dict[str, Any]:
    if qwen_result.get("status") != "completed":
        return {
            "status": "not_available",
            "reason": "Semantic output was not available.",
        }

    aggregate = qwen_result.get("aggregate", {})
    base_audience_ratio = summary["scores"]["audience_orientation_score"] / 100.0
    qwen_audience_ratio = float(aggregate.get("audience_focus_ratio", 0.0))
    qwen_board_ratio = float(aggregate.get("board_focus_ratio", 0.0)) + float(aggregate.get("screen_focus_ratio", 0.0))
    delta = abs(base_audience_ratio - qwen_audience_ratio)
    if qwen_audience_ratio >= 0.45 and base_audience_ratio >= 0.60:
        label = "aligned"
    elif qwen_board_ratio >= 0.45 and base_audience_ratio <= 0.55:
        label = "aligned"
    elif delta <= 0.20:
        label = "mostly_aligned"
    else:
        label = "review"
    return {
        "status": "available",
        "label": label,
        "base_audience_orientation_ratio": round(base_audience_ratio, 3),
        "qwen_audience_focus_ratio": round(qwen_audience_ratio, 3),
        "difference": round(delta, 3),
        "note": "This agreement check is qualitative and does not change base scores.",
    }


def _build_summary(
    samples: list[SemanticSample],
    summary: dict[str, Any],
    qwen_result: dict[str, Any],
) -> dict[str, Any]:
    semantic_summary: dict[str, Any] = {
        "sample_count": len(samples),
        "sample_timestamps_sec": [round(sample.timestamp_sec, 2) for sample in samples],
        "sample_reasons": [sample.reason for sample in samples],
        "qwen": {
            "status": qwen_result.get("status"),
            "reason": qwen_result.get("reason"),
            "aggregate": qwen_result.get("aggregate", {}),
        },
        "agreement": _base_to_semantic_agreement(summary, qwen_result),
    }
    if qwen_result.get("status") == "completed":
        qwen_agg = qwen_result["aggregate"]
        semantic_summary["semantic_extensions"] = {
            "audience_focus_ratio_qwen": qwen_agg.get("audience_focus_ratio", 0.0),
            "board_or_screen_focus_ratio_qwen": qwen_agg.get("board_focus_ratio", 0.0)
            + qwen_agg.get("screen_focus_ratio", 0.0),
            "warm_affect_ratio_qwen": qwen_agg.get("warm_affect_ratio", 0.0),
            "tense_affect_ratio_qwen": qwen_agg.get("tense_affect_ratio", 0.0),
            "static_stance_ratio_qwen": qwen_agg.get("static_stance_ratio", 0.0),
            "pointing_ratio_qwen": qwen_agg.get("pointing_ratio", 0.0),
        }
    else:
        semantic_summary["semantic_extensions"] = {}
    return semantic_summary


def _summary_markdown(payload: dict[str, Any], summary: dict[str, Any], qwen_result: dict[str, Any]) -> str:
    lines = [
        "# Semantic Extensions Summary",
        "",
        "These outputs are additive only. They do not change any of the base nonverbal scores.",
        "",
        "## Base Context",
        "",
        f"- Base overall score: `{summary['scores']['heuristic_nonverbal_score']:.1f}`",
        f"- Base audience-orientation score: `{summary['scores']['audience_orientation_score']:.1f}`",
        f"- Base eye-contact distribution score: `{summary['scores']['eye_contact_distribution_score']:.1f}`",
        f"- Sample count used for semantic review: `{payload['sample_count']}`",
        "",
        "## Semantic Model",
        "",
        f"- Status: `{qwen_result['status']}`",
        f"- Reason: {qwen_result['reason']}",
    ]
    if qwen_result.get("status") == "completed":
        aggregate = qwen_result["aggregate"]
        lines.extend(
            [
                f"- Audience focus ratio: `{aggregate['audience_focus_ratio']:.2f}`",
                f"- Board focus ratio: `{aggregate['board_focus_ratio']:.2f}`",
                f"- Screen focus ratio: `{aggregate['screen_focus_ratio']:.2f}`",
                f"- Warm affect ratio: `{aggregate['warm_affect_ratio']:.2f}`",
                f"- Tense affect ratio: `{aggregate['tense_affect_ratio']:.2f}`",
                f"- Static stance ratio: `{aggregate['static_stance_ratio']:.2f}`",
                f"- Pointing ratio: `{aggregate['pointing_ratio']:.2f}`",
            ]
        )
    agreement = payload["agreement"]
    lines.extend(
        [
            "",
            "## Agreement Check",
            "",
            f"- Status: `{agreement['status']}`",
        ]
    )
    if agreement["status"] == "available":
        lines.extend(
            [
                f"- Label: `{agreement['label']}`",
                f"- Base audience ratio: `{agreement['base_audience_orientation_ratio']:.2f}`",
                f"- Semantic audience ratio: `{agreement['qwen_audience_focus_ratio']:.2f}`",
                f"- Absolute difference: `{agreement['difference']:.2f}`",
                f"- Note: {agreement['note']}",
            ]
        )
    else:
        lines.append(f"- Reason: {agreement['reason']}")
    return "\n".join(lines) + "\n"


def run_semantic_extensions(
    clip_path: Path,
    frame_metrics_df: pd.DataFrame,
    summary: dict[str, Any],
    run_dir: Path,
    config: SemanticConfig,
    events_path: Path,
) -> dict[str, Any]:
    artifacts = build_semantic_artifacts(run_dir)
    samples = _save_sampled_frames(
        clip_path=clip_path,
        frame_metrics_df=frame_metrics_df,
        artifacts=artifacts,
        config=config,
        events_path=events_path,
        clip_duration_sec=float(summary["clip"]["duration_sec_actual"]),
    )
    qwen_result = _run_qwen(samples, config, events_path)
    payload = _build_summary(samples, summary, qwen_result)

    artifacts.qwen_annotations_path.write_text(
        json.dumps(qwen_result, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    artifacts.summary_json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    artifacts.summary_md_path.write_text(
        _summary_markdown(payload, summary, qwen_result),
        encoding="utf-8",
    )
    _build_contact_sheet(samples, qwen_result, artifacts.contact_sheet_path)
    log_event(
        events_path,
        "semantic_extensions_finished",
        qwen_status=qwen_result["status"],
        summary_json=str(artifacts.summary_json_path),
        contact_sheet=str(artifacts.contact_sheet_path),
    )
    return {
        "artifacts": {
            "root_dir": str(artifacts.root_dir),
            "sampled_frames_dir": str(artifacts.sampled_frames_dir),
            "contact_sheet": str(artifacts.contact_sheet_path),
            "qwen_annotations": str(artifacts.qwen_annotations_path),
            "summary_json": str(artifacts.summary_json_path),
            "summary_md": str(artifacts.summary_md_path),
        },
        "summary": payload,
        "qwen": qwen_result,
    }
