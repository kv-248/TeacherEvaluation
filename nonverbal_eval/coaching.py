from __future__ import annotations

import ast
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pandas as pd

from .gemini_api import generate_gemini_json, is_gemini_model
from .pipeline import log_event
from .runtime_config import load_base_thresholds, load_coaching_prompt_config, load_qwen_prompt_config
from .semantic import SemanticConfig, SemanticSample, _extract_frame_at, _run_qwen


_BASE_THRESHOLDS = load_base_thresholds()
_QWEN_CONFIG = load_qwen_prompt_config()["frame_semantic_review"]
_COACHING_CONFIG = load_coaching_prompt_config()


@dataclass(slots=True)
class CoachingConfig:
    enabled: bool = False
    coach_model: str = str(_COACHING_CONFIG["coaching_synthesis"]["model"])
    coach_device: str = "cuda:1"
    coach_max_windows: int = 6
    coach_top_actions: int = 3
    coach_render_pdf: bool = True
    coach_fallback_template_only: bool = False
    qwen_enabled: bool = True
    qwen_model: str = str(_QWEN_CONFIG["model"])
    qwen_device: str = "cuda:0"
    qwen_device_map: str | None = None
    qwen_dtype: str = "bfloat16"
    qwen_max_new_tokens: int = int(_QWEN_CONFIG["max_new_tokens"])
    qwen_temperature: float = float(_QWEN_CONFIG["temperature"])


@dataclass(slots=True)
class CoachingArtifacts:
    evidence_json_path: Path
    report_json_path: Path
    report_md_path: Path
    report_pdf_path: Path
    moments_dir: Path


COACHING_PROMPT = str(_COACHING_CONFIG["coaching_synthesis"]["prompt"])
ACTION_TEMPLATES: dict[str, dict[str, str]] = _COACHING_CONFIG["action_templates"]
STRENGTH_TEMPLATES: dict[str, dict[str, str]] = _COACHING_CONFIG["strength_templates"]
REPORT_SHAPE_VERSION = "feedback_first_v1"

COACHING_REPORT_SCHEMA = {
    "type": "object",
    "required": [
        "report_shape_version",
        "executive_summary",
        "no_material_intervention_needed",
        "no_material_intervention_needed_reason",
        "top_strengths",
        "strength_inventory",
        "priority_actions",
        "additional_observation_inventory",
        "low_confidence_watchlist",
        "keep_doing",
        "watch_for",
        "confidence_notes",
        "evidence_moments",
    ],
    "properties": {
        "report_shape_version": {"type": "string", "const": REPORT_SHAPE_VERSION},
        "executive_summary": {"type": "string"},
        "no_material_intervention_needed": {"type": "boolean"},
        "no_material_intervention_needed_reason": {"type": "string"},
        "top_strengths": {"type": "array"},
        "strength_inventory": {"type": "array"},
        "priority_actions": {"type": "array"},
        "additional_observation_inventory": {"type": "array"},
        "low_confidence_watchlist": {"type": "array"},
        "keep_doing": {"type": "array"},
        "watch_for": {"type": "array"},
        "confidence_notes": {"type": "array"},
        "evidence_moments": {"type": "array"},
    },
}
COACHING_GEMINI_SYSTEM_INSTRUCTION = (
    COACHING_PROMPT
    + "\n\nReturn exactly one JSON object that matches this schema, with no markdown or extra text:\n"
    + json.dumps(COACHING_REPORT_SCHEMA, indent=2, ensure_ascii=True)
)
COACHING_TOP_LEVEL_ALIASES: dict[str, tuple[str, ...]] = {
    "executive_summary": ("summary", "coach_summary", "overview"),
    "no_material_intervention_needed": ("no_intervention_needed", "no_action_needed"),
    "no_material_intervention_needed_reason": ("reason", "rationale", "why"),
    "top_strengths": ("strengths", "strength_highlights", "top_highlights"),
    "strength_inventory": ("strengths_inventory", "strength_items"),
    "priority_actions": ("action_items", "actions", "priority_recommendations", "recommendations"),
    "additional_observation_inventory": ("additional_observations", "observation_inventory", "observations"),
    "low_confidence_watchlist": ("watchlist", "watch_items", "low_confidence_items"),
    "keep_doing": ("continue_doing", "maintain", "keep"),
    "watch_for": ("watch_items", "watch_next", "monitor"),
    "confidence_notes": ("reliability_notes", "notes"),
    "evidence_moments": ("moments", "evidence_cards", "moment_cards"),
}
COACHING_ITEM_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "kind": ("category", "type"),
    "title": ("name", "label"),
    "evidence": ("what_we_saw", "support", "detail"),
    "what_to_repeat": ("repeat", "what_to_keep", "how_to_repeat"),
    "why_it_matters": ("why", "reason"),
    "what_we_saw": ("observed_behavior", "what_observed", "behavior"),
    "what_to_try_next": ("what_to_do_next", "next_step", "try_next", "suggested_next_step"),
    "suggested_response": ("what_to_try_next", "what_to_do_next", "next_step"),
    "why_watch": ("reason_to_watch", "watch_reason", "why_it_matters"),
    "what_to_monitor_next": ("what_to_watch", "monitor_next", "what_to_try_next"),
    "observed_behavior": ("what_we_saw", "behavior"),
    "metric_evidence": ("metrics", "metric_support"),
    "qwen_interpretation": ("semantic_interpretation", "qwen_summary", "interpretation"),
    "coaching_implication": ("implication", "next_step", "suggested_response"),
    "confidence": ("evidence_confidence", "confidence_level"),
    "timestamps": ("timestamp", "time", "timecodes", "time_marks"),
}


def build_coaching_artifacts(run_dir: Path) -> CoachingArtifacts:
    moments_dir = run_dir / "coaching_moments"
    moments_dir.mkdir(parents=True, exist_ok=True)
    return CoachingArtifacts(
        evidence_json_path=run_dir / "coaching_evidence.json",
        report_json_path=run_dir / "teacher_coaching_report.json",
        report_md_path=run_dir / "teacher_coaching_report.md",
        report_pdf_path=run_dir / "teacher_coaching_report.pdf",
        moments_dir=moments_dir,
    )


def _fmt_timestamp(seconds: float) -> str:
    total = max(int(round(seconds)), 0)
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


def _window_label(start_sec: float, end_sec: float) -> str:
    return f"{_fmt_timestamp(start_sec)}-{_fmt_timestamp(end_sec)}"


def _confidence_from_qc(face_coverage: float, hand_coverage: float, pose_coverage: float) -> str:
    cfg = _BASE_THRESHOLDS["coaching"]["qc_confidence"]
    if (
        face_coverage >= float(cfg["high_face_min"])
        and hand_coverage >= float(cfg["high_hand_min"])
        and pose_coverage >= float(cfg["high_pose_min"])
    ):
        return "high"
    if face_coverage >= float(cfg["medium_face_min"]) and pose_coverage >= float(cfg["medium_pose_min"]):
        return "medium"
    return "low"


def _unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _metric_band(score: float) -> str:
    if score >= float(_BASE_THRESHOLDS["interpretation_bands"]["strong_min"]):
        return "strong"
    if score >= float(_BASE_THRESHOLDS["interpretation_bands"]["moderate_min"]):
        return "moderate"
    return "limited"


def _risk_band(score: float) -> str:
    if score >= float(_BASE_THRESHOLDS["risk_bands"]["high_min"]):
        return "high"
    if score >= float(_BASE_THRESHOLDS["risk_bands"]["moderate_min"]):
        return "moderate"
    return "low"


def _overall_pattern(summary: dict[str, Any], semantic_payload: dict[str, Any] | None) -> str:
    score = summary["scores"]
    cfg = _BASE_THRESHOLDS["coaching"]["overall_pattern"]
    parts: list[str] = []
    if (
        score["confidence_presence_score"] >= float(cfg["presence_strong_min"])
        and score["posture_stability_score"] >= float(cfg["posture_strong_min"])
    ):
        parts.append("Delivery generally reads as upright and physically settled")
    elif score["confidence_presence_score"] < float(cfg["presence_low_max"]):
        parts.append("Delivery looks less settled in physical presence")

    if score["eye_contact_distribution_score"] >= float(cfg["eye_distribution_strong_min"]):
        parts.append("room engagement appears reasonably distributed")
    elif score["eye_contact_distribution_score"] < float(cfg["eye_distribution_low_max"]):
        parts.append("room engagement looks uneven")

    if (
        score["natural_movement_score"] >= float(cfg["natural_movement_strong_min"])
        and summary["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"]
        < float(cfg["static_behavior_risk_min"])
    ):
        parts.append("gesture use is mostly controlled and explanatory")
    elif (
        summary["category_feedback"]["gesture_and_facial_expression"]["static_behavior_risk"]
        >= float(cfg["static_behavior_risk_min"])
    ):
        parts.append("movement is somewhat limited")
    elif (
        summary["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"]
        >= float(cfg["excessive_animation_risk_min"])
    ):
        parts.append("some motion spikes may be larger than needed")

    if semantic_payload:
        qwen = semantic_payload.get("summary", {}).get("qwen", {})
        if qwen.get("status") == "completed":
            aggregate = qwen.get("aggregate", {})
            if aggregate.get("notes_focus_ratio", 0.0) >= float(cfg["notes_focus_ratio_min"]):
                parts.append("semantic review suggests the clip includes noticeable note-reading")
            elif aggregate.get("audience_focus_ratio", 0.0) >= float(cfg["audience_focus_ratio_min"]):
                parts.append("semantic review sees the instructor mostly addressing the audience")

    if not parts:
        parts.append("The clip is trackable, but the nonverbal pattern is mixed rather than dominated by one clear trait")
    return "; ".join(parts) + "."


def _reliability_notes(summary: dict[str, Any]) -> dict[str, Any]:
    qc = summary["quality_control"]
    clip = summary["clip"]
    cfg = _BASE_THRESHOLDS["coaching"]["reliability"]
    notes: list[str] = []
    if qc["face_coverage"] < float(cfg["note_face_max"]):
        notes.append("Face visibility is limited in parts of the clip, so eye-contact and facial-tone claims are less certain.")
    if qc["hand_coverage"] < float(cfg["note_hand_max"]):
        notes.append("Hand visibility drops in parts of the clip, so gesture labels are less certain.")
    if clip["duration_sec_actual"] < float(cfg["note_short_clip_sec"]):
        notes.append("Short duration limits how confidently the report can generalize beyond this segment.")
    for warning in summary["warnings"]:
        if warning not in notes:
            notes.append(warning)
    if not notes:
        notes.append("Tracking quality is stable enough for formative review, but the outputs remain heuristic proxies rather than direct teaching-quality measures.")

    qc_score = 0
    qc_score += 1 if qc["pose_coverage"] >= float(cfg["score_pose_min"]) else 0
    qc_score += 1 if qc["face_coverage"] >= float(cfg["score_face_min"]) else 0
    qc_score += 1 if qc["hand_coverage"] >= float(cfg["score_hand_min"]) else 0
    qc_score += 1 if clip["duration_sec_actual"] >= float(cfg["score_duration_sec_min"]) else 0
    label = (
        "high"
        if qc_score >= int(cfg["high_score_min"])
        else "medium" if qc_score >= int(cfg["medium_score_min"]) else "low"
    )
    return {
        "label": label,
        "summary": f"Reliability is {label} for this segment based on face, hand, and pose coverage plus clip length.",
        "notes": notes,
    }


def _window_priority_candidates(window_df: pd.DataFrame) -> list[dict[str, Any]]:
    if window_df.empty:
        return []

    candidates: list[dict[str, Any]] = []
    cfg = _BASE_THRESHOLDS["coaching"]["candidate_thresholds"]

    def add_candidate(row: pd.Series, kind: str, reason: str, priority: float) -> None:
        candidates.append(
            {
                "kind": kind,
                "reason": reason,
                "priority": float(priority),
                "row": row.to_dict(),
            }
        )

    add_candidate(window_df.sort_values("heuristic_nonverbal_score", ascending=True).iloc[0], "action", "weakest_overall", 95.0)
    add_candidate(window_df.sort_values("heuristic_nonverbal_score", ascending=False).iloc[0], "strength", "best_overall", 92.0)

    eye_row = window_df.sort_values("eye_contact_distribution_score", ascending=True).iloc[0]
    if float(eye_row["eye_contact_distribution_score"]) < float(cfg["eye_contact_action_max"]):
        add_candidate(eye_row, "action", "low_eye_contact_distribution", 100.0 - float(eye_row["eye_contact_distribution_score"]))

    presence_row = window_df.assign(
        presence_issue=lambda df: np.maximum(
            100.0 - df["confidence_presence_score"],
            df["closed_posture_risk"],
        )
    ).sort_values("presence_issue", ascending=False).iloc[0]
    if float(presence_row["presence_issue"]) >= float(cfg["presence_issue_min"]):
        add_candidate(presence_row, "action", "posture_presence_issue", float(presence_row["presence_issue"]))

    movement_issue_df = window_df.assign(
        movement_issue=lambda df: np.maximum.reduce(
            [
                100.0 - df["natural_movement_score"],
                df["static_behavior_risk"],
                df["excessive_animation_risk"],
            ]
        )
    )
    movement_row = movement_issue_df.sort_values("movement_issue", ascending=False).iloc[0]
    if float(movement_row["movement_issue"]) >= float(cfg["movement_issue_min"]):
        add_candidate(movement_row, "action", "movement_issue", float(movement_row["movement_issue"]))

    affect_issue_df = window_df.assign(
        affect_issue=lambda df: np.maximum(
            100.0 - df["positive_affect_score"],
            df["tension_hostility_risk"],
        )
    )
    affect_row = affect_issue_df.sort_values("affect_issue", ascending=False).iloc[0]
    if float(affect_row["affect_issue"]) >= float(cfg["affect_issue_min"]):
        add_candidate(affect_row, "action", "affect_issue", float(affect_row["affect_issue"]))

    face_row = window_df.sort_values("face_coverage", ascending=True).iloc[0]
    if float(face_row["face_coverage"]) < float(cfg["face_coverage_action_max"]):
        add_candidate(face_row, "reliability", "low_face_coverage", (1.0 - float(face_row["face_coverage"])) * 100.0)

    unique: list[dict[str, Any]] = []
    seen_windows: set[tuple[float, float]] = set()
    for item in sorted(candidates, key=lambda item: item["priority"], reverse=True):
        row = item["row"]
        key = (round(float(row["window_start_sec"]), 2), round(float(row["window_end_sec"]), 2))
        if key in seen_windows:
            continue
        seen_windows.add(key)
        unique.append(item)
    return unique


def _window_base_tags(row: dict[str, Any], kind: str) -> list[str]:
    tags: list[str] = []
    cfg = _BASE_THRESHOLDS["coaching"]["window_tags"]
    if kind != "strength":
        if row["face_coverage"] < float(cfg["face_coverage_low_max"]):
            tags.append("low_face_visibility")
        if row["eye_contact_distribution_score"] < float(cfg["eye_distribution_low_max"]):
            tags.append("uneven_room_scan")
        if row["audience_orientation_score"] < float(cfg["audience_orientation_low_max"]):
            tags.append("low_audience_orientation")
        if (
            row["confidence_presence_score"] < float(cfg["presence_low_max"])
            or row["closed_posture_risk"] >= float(cfg["closed_posture_risk_min"])
        ):
            tags.append("closed_posture")
        if (
            row["natural_movement_score"] < float(cfg["natural_movement_low_max"])
            and row["static_behavior_risk"] >= float(cfg["static_behavior_risk_min"])
        ):
            tags.append("limited_movement")
        if row["excessive_animation_risk"] >= float(cfg["excessive_animation_risk_min"]):
            tags.append("over_animated_delivery")
        if (
            row["face_coverage"] >= float(cfg["affect_face_coverage_min"])
            and row["tension_hostility_risk"] >= float(cfg["tension_hostility_risk_min"])
        ):
            tags.append("tense_or_neutral_affect")
        if row["alertness_score"] < float(cfg["alertness_low_max"]):
            tags.append("reduced_alertness")

    if kind == "strength":
        if row["eye_contact_distribution_score"] >= float(cfg["strength_eye_distribution_min"]):
            tags.append("distributed_room_engagement")
        if (
            row["confidence_presence_score"] >= float(cfg["strength_presence_min"])
            and row["posture_stability_score"] >= float(cfg["strength_posture_min"])
        ):
            tags.append("upright_confident_presence")
        if (
            row["natural_movement_score"] >= float(cfg["strength_natural_movement_min"])
            and row["excessive_animation_risk"] < float(cfg["strength_excessive_animation_max"])
        ):
            tags.append("controlled_expressive_gestures")
        if row["positive_affect_score"] >= float(cfg["strength_positive_affect_min"]):
            tags.append("welcoming_affect")
        if row["alertness_score"] >= float(cfg["strength_alertness_min"]):
            tags.append("alert_room_presence")
    return _unique_strings(tags)


def _primary_tag(tags: list[str], kind: str) -> str:
    if kind == "strength":
        for preferred in (
            "distributed_room_engagement",
            "upright_confident_presence",
            "controlled_expressive_gestures",
            "welcoming_affect",
            "alert_room_presence",
            "open_palm_explaining",
        ):
            if preferred in tags:
                return preferred
    for preferred in (
        "note_reading",
        "uneven_room_scan",
        "low_audience_orientation",
        "closed_posture",
        "limited_movement",
        "over_animated_delivery",
        "tense_or_neutral_affect",
        "reduced_alertness",
        "low_face_visibility",
    ):
        if preferred in tags:
            return preferred
    return tags[0] if tags else ("best_overall" if kind == "strength" else "weakest_overall")


def _window_sample_timestamps(window: dict[str, Any], frame_metrics_df: pd.DataFrame) -> list[float]:
    local_start = float(window["window_local_start_sec"])
    local_end = float(window["window_local_end_sec"])
    segment = frame_metrics_df[
        (frame_metrics_df["timestamp_sec"] >= local_start) & (frame_metrics_df["timestamp_sec"] < local_end)
    ].copy()
    midpoint = local_start + (local_end - local_start) * 0.5
    timestamps = [midpoint]
    if segment.empty:
        return timestamps

    primary_tag = window["primary_tag"]
    try:
        if primary_tag in {"uneven_room_scan", "low_audience_orientation"}:
            idx = segment["audience_orientation_score_frame"].idxmin()
            timestamps.append(float(segment.loc[idx, "timestamp_sec"]))
        elif primary_tag in {"limited_movement"}:
            idx = segment["gesture_motion"].idxmin()
            timestamps.append(float(segment.loc[idx, "timestamp_sec"]))
        elif primary_tag in {"over_animated_delivery"}:
            idx = segment["gesture_motion"].idxmax()
            timestamps.append(float(segment.loc[idx, "timestamp_sec"]))
        elif primary_tag in {"closed_posture"}:
            idx = segment["posture_score_frame"].idxmin()
            timestamps.append(float(segment.loc[idx, "timestamp_sec"]))
        elif primary_tag in {"tense_or_neutral_affect"}:
            idx = segment["smile_proxy"].idxmin()
            timestamps.append(float(segment.loc[idx, "timestamp_sec"]))
        elif primary_tag in {"distributed_room_engagement"}:
            idx = segment["audience_orientation_score_frame"].idxmax()
            timestamps.append(float(segment.loc[idx, "timestamp_sec"]))
        elif primary_tag in {"controlled_expressive_gestures"}:
            idx = segment["gesture_motion"].idxmax()
            timestamps.append(float(segment.loc[idx, "timestamp_sec"]))
    except Exception:
        pass

    unique: list[float] = []
    for value in timestamps:
        clipped = float(np.clip(value, local_start, max(local_end - 1e-3, local_start)))
        if not any(abs(clipped - existing) < 0.35 for existing in unique):
            unique.append(clipped)
    return unique[:2]


def _overlay_moment_frame(frame_bgr: np.ndarray, title: str, window_label: str, metric_lines: list[str]) -> np.ndarray:
    image = frame_bgr.copy()
    height, width = image.shape[:2]
    overlay = image.copy()
    cv2.rectangle(overlay, (18, 18), (min(width - 18, 18 + 520), 140), (12, 18, 26), thickness=-1)
    cv2.addWeighted(overlay, 0.55, image, 0.45, 0.0, image)
    cv2.putText(image, title, (34, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(image, window_label, (34, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.66, (230, 230, 230), 2, cv2.LINE_AA)
    y = 110
    for line in metric_lines[:3]:
        cv2.putText(image, line, (34, y), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (228, 228, 228), 1, cv2.LINE_AA)
        y += 22
    return image


def _build_review_windows(
    clip_path: Path,
    frame_metrics_df: pd.DataFrame,
    window_df: pd.DataFrame,
    artifacts: CoachingArtifacts,
    config: CoachingConfig,
    events_path: Path,
) -> tuple[list[dict[str, Any]], list[SemanticSample]]:
    chosen = _window_priority_candidates(window_df)
    review_windows: list[dict[str, Any]] = []
    qwen_samples: list[SemanticSample] = []

    for index, item in enumerate(chosen[: max(config.coach_max_windows, 1)]):
        row = dict(item["row"])
        tags = _window_base_tags(row, item["kind"])
        primary_tag = _primary_tag(tags, item["kind"])
        absolute_label = _window_label(float(row["window_start_sec"]), float(row["window_end_sec"]))
        local_midpoint = float(row["window_local_start_sec"]) + (float(row["window_local_end_sec"]) - float(row["window_local_start_sec"])) * 0.5
        display_frame = _extract_frame_at(clip_path, local_midpoint)
        metric_lines = [
            f"overall={row['heuristic_nonverbal_score']:.1f}  eye={row['eye_contact_distribution_score']:.1f}",
            f"presence={row['confidence_presence_score']:.1f}  natural={row['natural_movement_score']:.1f}",
            f"excessive={row['excessive_animation_risk']:.1f}  face={row['face_coverage']:.2f}",
        ]
        title = "Strength to preserve" if item["kind"] == "strength" else "Review moment"
        display_path = artifacts.moments_dir / f"moment_{index + 1:02d}_{absolute_label.replace(':', '').replace('-', '_')}.jpg"
        annotated = _overlay_moment_frame(display_frame, title, absolute_label, metric_lines)
        cv2.imwrite(str(display_path), annotated)

        review_window = {
            "id": f"moment_{index + 1:02d}",
            "kind": item["kind"],
            "reason": item["reason"],
            "priority": float(item["priority"]),
            "primary_tag": primary_tag,
            "evidence_tags": tags,
            "window_local_start_sec": float(row["window_local_start_sec"]),
            "window_local_end_sec": float(row["window_local_end_sec"]),
            "window_start_sec": float(row["window_start_sec"]),
            "window_end_sec": float(row["window_end_sec"]),
            "window_label": absolute_label,
            "metrics": {
                "overall_score": float(row["heuristic_nonverbal_score"]),
                "natural_movement_score": float(row["natural_movement_score"]),
                "positive_affect_score": float(row["positive_affect_score"]),
                "confidence_presence_score": float(row["confidence_presence_score"]),
                "eye_contact_distribution_score": float(row["eye_contact_distribution_score"]),
                "alertness_score": float(row["alertness_score"]),
                "static_behavior_risk": float(row["static_behavior_risk"]),
                "excessive_animation_risk": float(row["excessive_animation_risk"]),
                "closed_posture_risk": float(row["closed_posture_risk"]),
                "tension_hostility_risk": float(row["tension_hostility_risk"]),
            },
            "quality_control": {
                "pose_coverage": float(row["pose_coverage"]),
                "face_coverage": float(row["face_coverage"]),
                "hand_coverage": float(row["hand_coverage"]),
                "confidence": _confidence_from_qc(float(row["face_coverage"]), float(row["hand_coverage"]), float(row["pose_coverage"])),
            },
            "display_frame_path": str(display_path),
        }
        review_windows.append(review_window)

        for sample_index, sample_timestamp in enumerate(_window_sample_timestamps(review_window, frame_metrics_df)):
            frame_bgr = _extract_frame_at(clip_path, sample_timestamp)
            image_path = artifacts.moments_dir / (
                f"{review_window['id']}_qwen_{sample_index + 1:02d}_{sample_timestamp:06.2f}s.jpg"
            )
            cv2.imwrite(str(image_path), frame_bgr)
            qwen_samples.append(
                SemanticSample(
                    timestamp_sec=sample_timestamp,
                    reason=f"{review_window['id']}|{review_window['window_label']}|sample_{sample_index + 1}",
                    image_path=image_path,
                    frame_bgr=frame_bgr,
                    frame_shape=frame_bgr.shape,
                )
            )

    log_event(
        events_path,
        "coaching_windows_selected",
        review_window_count=len(review_windows),
        windows=[window["window_label"] for window in review_windows],
        primary_tags=[window["primary_tag"] for window in review_windows],
    )
    return review_windows, qwen_samples


def _summarize_qwen_window(qwen_annotations: list[dict[str, Any]]) -> dict[str, Any]:
    if not qwen_annotations:
        return {
            "status": "not_available",
            "summary": "No targeted semantic interpretation was available for this review window.",
            "aggregate": {},
            "annotations": [],
        }

    focus_counts = pd.Series([row["teacher_focus"] for row in qwen_annotations]).value_counts().to_dict()
    action_counts = pd.Series([row["body_action"] for row in qwen_annotations]).value_counts().to_dict()
    affect_counts = pd.Series([row["affect_tone"] for row in qwen_annotations]).value_counts().to_dict()
    posture_counts = pd.Series([row["posture_signal"] for row in qwen_annotations]).value_counts().to_dict()
    count = max(len(qwen_annotations), 1)

    def ratio(mapping: dict[str, int], key: str) -> float:
        return float(mapping.get(key, 0) / count)

    summary_parts: list[str] = []
    if ratio(focus_counts, "notes") >= 0.5 or ratio(action_counts, "reading_from_notes") >= 0.5:
        summary_parts.append("Semantic review suggests repeated note-reading or notes-focused attention")
    elif ratio(focus_counts, "audience") >= 0.5:
        summary_parts.append("Semantic review suggests the teacher is mainly addressing the audience")
    elif ratio(focus_counts, "board") + ratio(focus_counts, "screen") >= 0.5:
        summary_parts.append("Semantic review suggests the teacher is mainly oriented to board or screen content")

    if ratio(action_counts, "open_palm_explaining") >= 0.5:
        summary_parts.append("open-palm explanatory gestures recur")
    if ratio(action_counts, "static_stance") >= 0.5:
        summary_parts.append("stance is often static")
    if ratio(affect_counts, "tense") >= 0.5:
        summary_parts.append("visible affect leans tense")
    if ratio(posture_counts, "closed_or_slouched") >= 0.5:
        summary_parts.append("posture looks closed or slouched in several samples")

    aggregate = {
        "audience_focus_ratio": ratio(focus_counts, "audience"),
        "board_focus_ratio": ratio(focus_counts, "board"),
        "screen_focus_ratio": ratio(focus_counts, "screen"),
        "notes_focus_ratio": ratio(focus_counts, "notes"),
        "open_palm_explaining_ratio": ratio(action_counts, "open_palm_explaining"),
        "reading_from_notes_ratio": ratio(action_counts, "reading_from_notes"),
        "static_stance_ratio": ratio(action_counts, "static_stance"),
        "warm_affect_ratio": ratio(affect_counts, "warm"),
        "tense_affect_ratio": ratio(affect_counts, "tense"),
        "closed_or_slouched_ratio": ratio(posture_counts, "closed_or_slouched"),
        "focus_counts": focus_counts,
        "action_counts": action_counts,
        "affect_counts": affect_counts,
        "posture_counts": posture_counts,
    }
    return {
        "status": "completed",
        "summary": "; ".join(summary_parts) + "." if summary_parts else "Semantic window review returned mixed or ambiguous evidence.",
        "aggregate": aggregate,
        "annotations": qwen_annotations,
    }


def _augment_tags_with_qwen(tags: list[str], qwen_window: dict[str, Any]) -> list[str]:
    if qwen_window.get("status") != "completed":
        return _unique_strings(tags)
    aggregate = qwen_window["aggregate"]
    if aggregate.get("notes_focus_ratio", 0.0) >= 0.5 or aggregate.get("reading_from_notes_ratio", 0.0) >= 0.5:
        tags.append("note_reading")
    if aggregate.get("open_palm_explaining_ratio", 0.0) >= 0.5:
        tags.append("open_palm_explaining")
    if aggregate.get("static_stance_ratio", 0.0) >= 0.5:
        tags.append("limited_movement")
    if aggregate.get("tense_affect_ratio", 0.0) >= 0.5:
        tags.append("tense_or_neutral_affect")
    if aggregate.get("closed_or_slouched_ratio", 0.0) >= 0.5:
        tags.append("closed_posture")
    if aggregate.get("audience_focus_ratio", 0.0) >= 0.55:
        tags.append("distributed_room_engagement")
    return _unique_strings(tags)


def _merge_qwen_into_window_tags(window: dict[str, Any], qwen_window: dict[str, Any]) -> list[str]:
    tags = list(window.get("evidence_tags", []))
    if qwen_window.get("status") != "completed":
        return _unique_strings(tags)

    aggregate = qwen_window.get("aggregate", {})
    metrics = window.get("metrics", {})
    qc = window.get("quality_control", {})

    if aggregate.get("notes_focus_ratio", 0.0) >= 0.5 or aggregate.get("reading_from_notes_ratio", 0.0) >= 0.5:
        tags.append("note_reading")
    if aggregate.get("open_palm_explaining_ratio", 0.0) >= 0.5:
        tags.append("open_palm_explaining")
    if aggregate.get("audience_focus_ratio", 0.0) >= 0.55:
        tags.append("distributed_room_engagement")
    if (
        aggregate.get("static_stance_ratio", 0.0) >= 0.5
        and float(metrics.get("static_behavior_risk", 0.0)) >= float(_BASE_THRESHOLDS["coaching"]["window_tags"]["static_behavior_risk_min"])
    ):
        tags.append("limited_movement")
    if (
        aggregate.get("tense_affect_ratio", 0.0) >= 0.5
        and float(qc.get("face_coverage", 0.0)) >= float(_BASE_THRESHOLDS["coaching"]["window_tags"]["affect_face_coverage_min"])
        and float(metrics.get("tension_hostility_risk", 0.0)) >= float(_BASE_THRESHOLDS["coaching"]["window_tags"]["tension_hostility_risk_min"])
    ):
        tags.append("tense_or_neutral_affect")
    if (
        aggregate.get("closed_or_slouched_ratio", 0.0) >= 0.5
        and float(metrics.get("closed_posture_risk", 0.0)) >= float(_BASE_THRESHOLDS["coaching"]["window_tags"]["closed_posture_risk_min"])
    ):
        tags.append("closed_posture")

    return _unique_strings(tags)


def _report_shape_thresholds() -> dict[str, Any]:
    return _BASE_THRESHOLDS["coaching"]["report_shape"]


def _window_observation_rows(window_df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in window_df.to_dict(orient="records"):
        pose_coverage = float(row["pose_coverage"])
        face_coverage = float(row["face_coverage"])
        hand_coverage = float(row["hand_coverage"])
        rows.append(
            {
                **row,
                "window_label": _window_label(float(row["window_start_sec"]), float(row["window_end_sec"])),
                "quality_control": {
                    "pose_coverage": pose_coverage,
                    "face_coverage": face_coverage,
                    "hand_coverage": hand_coverage,
                    "confidence": _confidence_from_qc(face_coverage, hand_coverage, pose_coverage),
                },
            }
        )
    return rows


def _candidate_confidence(confidence_labels: list[str], support_count: int) -> str:
    labels = set(confidence_labels)
    if support_count >= 2 and labels == {"high"}:
        return "high"
    if "low" in labels:
        return "low" if support_count <= 1 else "medium"
    if "high" in labels:
        return "medium" if support_count <= 1 else "high"
    return "medium" if labels else "low"


def _action_signal_score(tag: str, row: dict[str, Any]) -> float:
    if tag == "uneven_room_scan":
        return max(0.0, 100.0 - float(row["eye_contact_distribution_score"]))
    if tag == "low_audience_orientation":
        return max(0.0, 100.0 - float(row["audience_orientation_score"]))
    if tag == "closed_posture":
        return max(100.0 - float(row["confidence_presence_score"]), float(row["closed_posture_risk"]))
    if tag == "limited_movement":
        return max(100.0 - float(row["natural_movement_score"]), float(row["static_behavior_risk"]))
    if tag == "over_animated_delivery":
        return float(row["excessive_animation_risk"])
    if tag == "tense_or_neutral_affect":
        return max(100.0 - float(row["positive_affect_score"]), float(row["tension_hostility_risk"]))
    if tag == "reduced_alertness":
        return max(0.0, 100.0 - float(row["alertness_score"]))
    return 0.0


def _strength_signal_score(tag: str, row: dict[str, Any]) -> float:
    if tag == "distributed_room_engagement":
        return float(row["eye_contact_distribution_score"])
    if tag == "upright_confident_presence":
        return min(float(row["confidence_presence_score"]), float(row["posture_stability_score"]))
    if tag == "controlled_expressive_gestures":
        return min(float(row["natural_movement_score"]), 100.0 - float(row["excessive_animation_risk"]))
    if tag == "welcoming_affect":
        return float(row["positive_affect_score"])
    if tag == "alert_room_presence":
        return float(row["alertness_score"])
    return 0.0


def _action_evidence_summary(tag: str, row: dict[str, Any]) -> str:
    label = row["window_label"]
    if tag == "note_reading":
        return f"{label} repeatedly pulled attention down to notes instead of back to the room."
    if tag == "uneven_room_scan":
        return f"{label} stayed more fixed on one part of the room than on a left-center-right sweep."
    if tag == "low_audience_orientation":
        return f"{label} spent longer than needed turned away from the audience after checks."
    if tag == "closed_posture":
        return f"{label} showed a more guarded arm-and-shoulder position between teaching points."
    if tag == "limited_movement":
        return f"{label} stayed physically still through explanation beats that could carry more emphasis."
    if tag == "over_animated_delivery":
        return f"{label} had gesture peaks that looked larger than the teaching point required."
    if tag == "tense_or_neutral_affect":
        return f"{label} showed a flatter or tighter visible facial tone than the rest of the clip."
    if tag == "reduced_alertness":
        return f"{label} showed fewer quick room checks and a less visibly alert scan."
    return f"{label} showed {tag.replace('_', ' ')}."


def _strength_evidence_summary(tag: str, row: dict[str, Any]) -> str:
    label = row["window_label"]
    if tag == "distributed_room_engagement":
        return f"{label} showed attention moving across more than one part of the room."
    if tag == "upright_confident_presence":
        return f"{label} held an upright, settled stance rather than a collapsed or guarded one."
    if tag == "controlled_expressive_gestures":
        return f"{label} used gestures with clear timing and no obvious motion spikes."
    if tag == "welcoming_affect":
        return f"{label} showed a more approachable visible facial tone."
    if tag == "alert_room_presence":
        return f"{label} kept the head and eyes visibly engaged with the room."
    if tag == "open_palm_explaining":
        return f"{label} included open-palm explanatory gestures that supported the explanation."
    return f"{label} showed {tag.replace('_', ' ')}."


def _watch_monitor_hint(tag: str) -> str:
    template = ACTION_TEMPLATES.get(tag, {})
    return str(template.get("monitor") or template.get("try") or "Use the cited timestamps as a manual review point.")


def _strength_repeat_hint(tag: str) -> str:
    template = STRENGTH_TEMPLATES.get(tag, {})
    return str(template.get("repeat") or "Keep this visible pattern available as a default during explanation.")


def _qwen_action_score(window: dict[str, Any], tag: str) -> float:
    aggregate = window.get("qwen", {}).get("aggregate", {})
    if tag == "note_reading":
        return 100.0 * max(
            float(aggregate.get("notes_focus_ratio", 0.0)),
            float(aggregate.get("reading_from_notes_ratio", 0.0)),
        )
    return 0.0


def _qwen_strength_score(window: dict[str, Any], tag: str) -> float:
    aggregate = window.get("qwen", {}).get("aggregate", {})
    if tag == "open_palm_explaining":
        return 100.0 * float(aggregate.get("open_palm_explaining_ratio", 0.0))
    return 0.0


def _classify_action_candidate(
    *,
    clip_duration_sec: float,
    reliability_label: str,
    support_count: int,
    avg_severity: float,
    max_severity: float,
    confidence: str,
) -> tuple[str, str]:
    cfg = _report_shape_thresholds()
    if reliability_label == "low":
        return "watch", "Overall evidence quality is too limited for confident corrective feedback."
    if clip_duration_sec < float(cfg["material_clip_min_sec"]):
        return "watch", "The clip is brief, so the signal is better treated as a watch item than a correction."
    if (
        support_count >= int(cfg["material_support_window_min"])
        and avg_severity >= float(cfg["material_avg_severity_min"])
        and confidence != "low"
    ):
        return "corrective", "The signal repeated across multiple windows strongly enough to justify corrective feedback."
    if (
        clip_duration_sec >= float(cfg["single_window_material_clip_min_sec"])
        and max_severity >= float(cfg["single_window_material_severity_min"])
        and confidence == "high"
    ):
        return "corrective", "One well-supported window was strong enough to justify a targeted correction."
    return "watch", "The signal is visible, but it is not yet sustained enough to justify real corrective feedback."


def _draft_action_candidates(
    window_df: pd.DataFrame,
    review_windows: list[dict[str, Any]],
    clip_duration_sec: float,
    reliability_label: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    watch_threshold = float(_report_shape_thresholds()["watchlist_severity_min"])

    def add_signal(
        *,
        tag: str,
        timestamp: str,
        severity: float,
        confidence: str,
        evidence_text: str,
    ) -> None:
        if tag not in ACTION_TEMPLATES or severity < watch_threshold:
            return
        bucket = grouped.setdefault(
            tag,
            {
                "tag": tag,
                "timestamps": [],
                "confidence_labels": [],
                "evidence_parts": [],
                "severities": [],
            },
        )
        bucket["timestamps"].append(timestamp)
        bucket["confidence_labels"].append(confidence)
        bucket["evidence_parts"].append(evidence_text)
        bucket["severities"].append(float(severity))

    for row in _window_observation_rows(window_df):
        for tag in _window_base_tags(row, "action"):
            if tag not in ACTION_TEMPLATES:
                continue
            add_signal(
                tag=tag,
                timestamp=row["window_label"],
                severity=_action_signal_score(tag, row),
                confidence=row["quality_control"]["confidence"],
                evidence_text=_action_evidence_summary(tag, row),
            )

    for window in review_windows:
        if "note_reading" not in window.get("evidence_tags", []):
            continue
        add_signal(
            tag="note_reading",
            timestamp=window["window_label"],
            severity=_qwen_action_score(window, "note_reading"),
            confidence=window["quality_control"]["confidence"],
            evidence_text=_action_evidence_summary("note_reading", {"window_label": window["window_label"]}),
        )

    def _clip_aware_what_we_saw(bucket: dict[str, Any], avg_sev: float) -> str:
        parts = bucket["evidence_parts"][:2]
        base = " ".join(parts)
        if avg_sev >= 60:
            base += f" This pattern was consistent and strong (severity {avg_sev:.0f}/100)."
        elif avg_sev >= 40:
            base += f" This appeared across multiple windows (severity {avg_sev:.0f}/100)."
        return base

    action_candidates: list[dict[str, Any]] = []
    for tag, bucket in grouped.items():
        timestamps = _unique_strings(bucket["timestamps"])
        support_count = len(timestamps)
        confidence = _candidate_confidence(bucket["confidence_labels"], support_count)
        avg_severity = float(np.mean(bucket["severities"])) if bucket["severities"] else 0.0
        max_severity = float(np.max(bucket["severities"])) if bucket["severities"] else 0.0
        materiality, materiality_reason = _classify_action_candidate(
            clip_duration_sec=clip_duration_sec,
            reliability_label=reliability_label,
            support_count=support_count,
            avg_severity=avg_severity,
            max_severity=max_severity,
            confidence=confidence,
        )
        template = ACTION_TEMPLATES[tag]
        action_candidates.append(
            {
                "tag": tag,
                "title": template["title"],
                "why_it_matters": template["why"],
                "what_we_saw": _clip_aware_what_we_saw(bucket, avg_severity),
                "what_to_try_next": template["try"],
                "what_to_monitor_next": _watch_monitor_hint(tag),
                "timestamps": timestamps,
                "confidence": confidence,
                "priority": max_severity + min(max(support_count - 1, 0) * 8.0, 16.0),
                "support_count": support_count,
                "avg_severity": avg_severity,
                "max_severity": max_severity,
                "materiality": materiality,
                "materiality_reason": materiality_reason,
            }
        )
    action_candidates.sort(
        key=lambda item: (
            item["materiality"] != "corrective",
            -float(item["priority"]),
            -int(item["support_count"]),
        )
    )
    return action_candidates


def _draft_strength_candidates(window_df: pd.DataFrame, review_windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    min_priority = float(_report_shape_thresholds()["strength_inventory_min_priority"])

    def add_signal(
        *,
        tag: str,
        timestamp: str,
        priority: float,
        confidence: str,
        evidence_text: str,
    ) -> None:
        if tag not in STRENGTH_TEMPLATES or priority < min_priority:
            return
        bucket = grouped.setdefault(
            tag,
            {
                "tag": tag,
                "timestamps": [],
                "confidence_labels": [],
                "evidence_parts": [],
                "priorities": [],
            },
        )
        bucket["timestamps"].append(timestamp)
        bucket["confidence_labels"].append(confidence)
        bucket["evidence_parts"].append(evidence_text)
        bucket["priorities"].append(float(priority))

    for row in _window_observation_rows(window_df):
        for tag in _window_base_tags(row, "strength"):
            if tag not in STRENGTH_TEMPLATES:
                continue
            add_signal(
                tag=tag,
                timestamp=row["window_label"],
                priority=_strength_signal_score(tag, row),
                confidence=row["quality_control"]["confidence"],
                evidence_text=_strength_evidence_summary(tag, row),
            )

    for window in review_windows:
        if "open_palm_explaining" not in window.get("evidence_tags", []):
            continue
        add_signal(
            tag="open_palm_explaining",
            timestamp=window["window_label"],
            priority=_qwen_strength_score(window, "open_palm_explaining"),
            confidence=window["quality_control"]["confidence"],
            evidence_text=_strength_evidence_summary("open_palm_explaining", {"window_label": window["window_label"]}),
        )

    strengths: list[dict[str, Any]] = []
    for tag, bucket in grouped.items():
        timestamps = _unique_strings(bucket["timestamps"])
        support_count = len(timestamps)
        confidence = _candidate_confidence(bucket["confidence_labels"], support_count)
        strengths.append(
            {
                "tag": tag,
                "title": STRENGTH_TEMPLATES[tag]["title"],
                "evidence": " ".join(bucket["evidence_parts"][:2]),
                "what_to_repeat": _strength_repeat_hint(tag),
                "timestamps": timestamps,
                "confidence": confidence,
                "priority": float(np.max(bucket["priorities"])) + min(max(support_count - 1, 0) * 6.0, 12.0),
                "support_count": support_count,
            }
        )
    strengths.sort(key=lambda item: (-float(item["priority"]), item["title"]))
    return strengths


def _moment_cards(review_windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for window in review_windows[:6]:
        metric_evidence = (
            f"Overall {window['metrics']['overall_score']:.1f}; "
            f"room scan {window['metrics']['eye_contact_distribution_score']:.1f}; "
            f"presence {window['metrics']['confidence_presence_score']:.1f}; "
            f"natural movement {window['metrics']['natural_movement_score']:.1f}."
        )
        if window["kind"] == "strength":
            implication = _strength_repeat_hint(window["primary_tag"])
        else:
            implication = ACTION_TEMPLATES.get(window["primary_tag"], {}).get(
                "try",
                "Use this window as a manual review point before changing the delivery pattern.",
            )
        cards.append(
            {
                "id": window["id"],
                "timestamp": window["window_label"],
                "headline": window["primary_tag"].replace("_", " ").title(),
                "observed_behavior": " / ".join(tag.replace("_", " ") for tag in window["evidence_tags"][:3]) or "mixed evidence",
                "metric_evidence": metric_evidence,
                "qwen_interpretation": window["qwen"]["summary"],
                "coaching_implication": implication,
                "image_path": Path(window["display_frame_path"]).name,
            }
        )
    return cards


def _no_material_reason(
    action_candidates: list[dict[str, Any]],
    *,
    clip_duration_sec: float,
    reliability_label: str,
) -> str:
    cfg = _report_shape_thresholds()
    if reliability_label == "low":
        return "Evidence quality is too limited to justify corrective feedback in this clip."
    if clip_duration_sec < float(cfg["material_clip_min_sec"]):
        return "This clip is short enough that the visible issues are better treated as watch items than as real corrective feedback."
    if action_candidates:
        top = action_candidates[0]
        return (
            f"The clearest watch item was {top['title'].lower()}, but it appeared in only {top['support_count']} "
            f"window(s) and did not clear the corrective-feedback bar."
        )
    return "No sustained issue repeated strongly enough to justify a corrective action."


def _prefer_maintenance_mode(
    summary: dict[str, Any],
    corrective_actions: list[dict[str, Any]],
    top_strengths: list[dict[str, Any]],
) -> bool:
    if not corrective_actions or not top_strengths:
        return False

    cfg = _report_shape_thresholds()
    scores = summary["scores"]
    strong_foundation = (
        float(scores["heuristic_nonverbal_score"]) >= float(cfg["maintenance_overall_min"])
        and float(scores["confidence_presence_score"]) >= float(cfg["maintenance_presence_min"])
        and float(scores["eye_contact_distribution_score"]) >= float(cfg["maintenance_eye_distribution_min"])
        and float(scores["alertness_score"]) >= float(cfg["maintenance_alertness_min"])
    )
    if not strong_foundation:
        return False

    allowed_tags = {"limited_movement", "tense_or_neutral_affect", "closed_posture"}
    if any(item["tag"] not in allowed_tags for item in corrective_actions):
        return False
    if any(item["confidence"] == "high" for item in corrective_actions):
        return False
    if any(float(item["max_severity"]) >= float(cfg["single_window_material_severity_min"]) for item in corrective_actions):
        return False

    return True


def _build_evidence_payload(
    summary: dict[str, Any],
    window_df: pd.DataFrame,
    review_windows: list[dict[str, Any]],
    semantic_payload: dict[str, Any] | None,
    config: CoachingConfig,
) -> dict[str, Any]:
    reliability = _reliability_notes(summary)
    action_candidates = _draft_action_candidates(
        window_df=window_df,
        review_windows=review_windows,
        clip_duration_sec=float(summary["clip"]["duration_sec_actual"]),
        reliability_label=reliability["label"],
    )
    strength_candidates = _draft_strength_candidates(window_df, review_windows)
    cfg = _report_shape_thresholds()
    corrective_actions = [item for item in action_candidates if item["materiality"] == "corrective"]
    watchlist_candidates = [item for item in action_candidates if item["materiality"] != "corrective"]
    top_strengths = [
        item
        for item in strength_candidates
        if float(item["priority"]) >= float(cfg["top_strength_priority_min"])
    ][: int(cfg["top_strength_limit"])]
    strength_inventory = strength_candidates[: int(cfg["strength_inventory_limit"])]
    priority_actions = corrective_actions[: max(config.coach_top_actions, 1)]
    if _prefer_maintenance_mode(summary, priority_actions, top_strengths):
        priority_actions = []
    no_material_intervention_needed = not priority_actions
    no_material_intervention_needed_reason = (
        _no_material_reason(
            corrective_actions if no_material_intervention_needed and corrective_actions else watchlist_candidates,
            clip_duration_sec=float(summary["clip"]["duration_sec_actual"]),
            reliability_label=reliability["label"],
        )
        if no_material_intervention_needed
        else ""
    )
    low_confidence_watchlist = [
        {
            "title": item["title"],
            "why_watch": item["materiality_reason"],
            "what_we_saw": item["what_we_saw"],
            "what_to_monitor_next": item["what_to_monitor_next"],
            "timestamps": item["timestamps"],
            "confidence": item["confidence"],
        }
        for item in watchlist_candidates[: int(cfg["watchlist_limit"])]
    ]
    additional_observation_inventory: list[dict[str, Any]] = []
    deferred_actions = corrective_actions if no_material_intervention_needed else corrective_actions[max(config.coach_top_actions, 1) :]
    for item in deferred_actions:
        additional_observation_inventory.append(
            {
                "kind": "refinement_observation" if no_material_intervention_needed else "action_opportunity",
                "title": item["title"],
                "evidence": item["what_we_saw"],
                "suggested_response": item["what_to_monitor_next"] if no_material_intervention_needed else item["what_to_try_next"],
                "timestamps": item["timestamps"],
                "confidence": item["confidence"],
            }
        )
    top_strength_tags = {item["tag"] for item in top_strengths}
    for item in strength_inventory:
        if item["tag"] in top_strength_tags:
            continue
        additional_observation_inventory.append(
            {
                "kind": "strength_to_preserve",
                "title": item["title"],
                "evidence": item["evidence"],
                "suggested_response": item["what_to_repeat"],
                "timestamps": item["timestamps"],
                "confidence": item["confidence"],
            }
        )
    for item in low_confidence_watchlist:
        additional_observation_inventory.append(
            {
                "kind": "watch_item",
                "title": item["title"],
                "evidence": item["what_we_saw"],
                "suggested_response": item["what_to_monitor_next"],
                "timestamps": item["timestamps"],
                "confidence": item["confidence"],
            }
        )
    additional_observation_inventory = additional_observation_inventory[: int(cfg["additional_observation_limit"])]
    priority_signals = [
        {
            "tag": item["tag"],
            "priority": item["priority"],
            "title": item["title"],
            "timestamps": item["timestamps"],
            "materiality": item["materiality"],
        }
        for item in action_candidates
    ]
    strength_signals = [
        {
            "tag": item["tag"],
            "priority": item["priority"],
            "title": item["title"],
            "timestamps": item["timestamps"],
        }
        for item in strength_candidates
    ]
    best = window_df.sort_values("heuristic_nonverbal_score", ascending=False).iloc[0].to_dict()
    worst = window_df.sort_values("heuristic_nonverbal_score", ascending=True).iloc[0].to_dict()

    return {
        "run_context": {
            "clip_video": summary["clip"]["clip_video"],
            "start_sec": summary["clip"]["start_sec"],
            "duration_sec_actual": summary["clip"]["duration_sec_actual"],
            "fps": summary["clip"]["fps"],
            "window_count": int(len(window_df)),
        },
        "overall_profile": {
            "overall_score": summary["scores"]["heuristic_nonverbal_score"],
            "pattern_summary": _overall_pattern(summary, semantic_payload),
            "best_window": {
                "label": _window_label(float(best["window_start_sec"]), float(best["window_end_sec"])),
                "score": float(best["heuristic_nonverbal_score"]),
            },
            "weakest_window": {
                "label": _window_label(float(worst["window_start_sec"]), float(worst["window_end_sec"])),
                "score": float(worst["heuristic_nonverbal_score"]),
            },
            "reliability": reliability["label"],
        },
        "score_snapshot": {
            "overall_score": summary["scores"]["heuristic_nonverbal_score"],
            "natural_movement_score": summary["scores"]["natural_movement_score"],
            "positive_affect_score": summary["scores"]["positive_affect_score"],
            "confidence_presence_score": summary["scores"]["confidence_presence_score"],
            "eye_contact_distribution_score": summary["scores"]["eye_contact_distribution_score"],
            "alertness_score": summary["scores"]["alertness_score"],
            "static_behavior_risk": summary["category_feedback"]["gesture_and_facial_expression"]["static_behavior_risk"],
            "excessive_animation_risk": summary["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"],
            "closed_posture_risk": summary["category_feedback"]["posture_and_presence"]["closed_posture_risk"],
        },
        "priority_signals": priority_signals,
        "strength_signals": strength_signals,
        "review_windows": review_windows,
        "qwen_evidence": {
            "global_summary": semantic_payload["summary"] if semantic_payload else None,
            "window_count": sum(1 for window in review_windows if window["qwen"]["status"] == "completed"),
        },
        "quality_warnings": reliability["notes"],
        "recommended_focus_areas": [item["tag"] for item in priority_actions]
        or [item["tag"] for item in top_strengths[:2]]
        or [item["title"] for item in low_confidence_watchlist[:2]],
        "report_shape_version": REPORT_SHAPE_VERSION,
        "no_material_intervention_needed": no_material_intervention_needed,
        "no_material_intervention_needed_reason": no_material_intervention_needed_reason,
        "draft_priority_actions": priority_actions,
        "draft_action_candidates": action_candidates,
        "draft_strength_inventory": strength_inventory,
        "draft_top_strengths": top_strengths,
        "draft_low_confidence_watchlist": low_confidence_watchlist,
        "draft_additional_observation_inventory": additional_observation_inventory,
        "draft_strength_candidates": strength_candidates,
        "moment_cards": _moment_cards(review_windows),
    }


def _has_text(value: Any) -> bool:
    return bool(re.sub(r"\s+", " ", str(value)).strip()) if value is not None else False


def _coerce_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text if text else default


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _coerce_confidence_label(value: Any) -> str:
    text = _coerce_text(value).lower()
    if "high" in text:
        return "high"
    if "medium" in text or "moderate" in text:
        return "medium"
    if "low" in text:
        return "low"
    return "medium" if text else "low"


def _coerce_kind_label(value: Any) -> str:
    text = _coerce_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "observation"


def _maybe_parse_json_container(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if len(text) < 2 or text[0] not in "[{" or text[-1] not in "]}":
        return value
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return value


def _coerce_list_of_strings(values: Any, limit: int) -> list[str]:
    values = _maybe_parse_json_container(values)
    if values is None:
        return []
    if isinstance(values, str):
        pieces = [piece.strip() for piece in re.split(r"[\n;]+", values) if piece.strip()]
        values = pieces or [values]
    elif not isinstance(values, (list, tuple, set)):
        values = [values]

    out: list[str] = []
    for value in values:
        text = _coerce_text(value)
        if text:
            out.append(text)
        if len(out) >= limit:
            break
    return _unique_strings(out)[:limit]


def _coerce_timestamp_list(value: Any, limit: int = 6) -> list[str]:
    value = _maybe_parse_json_container(value)
    if value is None:
        return []
    if isinstance(value, str):
        if any(sep in value for sep in (",", ";", "\n")):
            candidates = [piece.strip() for piece in re.split(r"[\n,;]+", value) if piece.strip()]
        else:
            candidates = [_coerce_text(value)]
    elif isinstance(value, (list, tuple, set)):
        candidates = [_coerce_text(item) for item in value]
    else:
        candidates = [_coerce_text(value)]
    return _unique_strings([item for item in candidates if item])[:limit]


def _coerce_list_of_dicts(
    values: Any,
    fields: list[str],
    limit: int,
    aliases: dict[str, tuple[str, ...]] | None = None,
) -> list[dict[str, Any]]:
    values = _maybe_parse_json_container(values)
    if values is None:
        return []
    if isinstance(values, dict):
        values = [values]
    if not isinstance(values, (list, tuple, set)):
        return []

    aliases = aliases or {}
    out: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, dict):
            continue
        row: dict[str, Any] = {}
        for field in fields:
            raw = value.get(field)
            if raw is None:
                for alias in aliases.get(field, ()):
                    if alias in value:
                        raw = value.get(alias)
                        break
            if field == "timestamps":
                row[field] = _coerce_timestamp_list(raw, limit=6)
            elif field == "confidence":
                row[field] = _coerce_confidence_label(raw)
            elif field == "kind":
                row[field] = _coerce_kind_label(raw)
            else:
                row[field] = _coerce_text(raw)
        if any(_has_text(row[field]) if field != "timestamps" else bool(row[field]) for field in fields):
            out.append(row)
        if len(out) >= limit:
            break
    return out


def _payload_value(payload: dict[str, Any], field: str) -> Any:
    for candidate in (field, *COACHING_TOP_LEVEL_ALIASES.get(field, ())):
        if candidate in payload:
            return payload[candidate]
    return None


def _unwrap_coaching_payload(parsed: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        return {}
    for wrapper_key in ("report", "output", "data", "result", "payload"):
        wrapped = parsed.get(wrapper_key)
        if isinstance(wrapped, dict) and any(key in wrapped for key in ("executive_summary", "priority_actions", "top_strengths", "strength_inventory")):
            return wrapped
    return parsed


def _build_llm_report(
    parsed: dict[str, Any],
    *,
    source_mode: str,
    model_name: str | None,
    evidence: dict[str, Any],
    config: CoachingConfig,
) -> dict[str, Any]:
    payload = _unwrap_coaching_payload(parsed)
    report = {
        "source": {
            "mode": source_mode,
            "model": model_name,
        },
        "report_shape_version": REPORT_SHAPE_VERSION,
        "executive_summary": _coerce_text(_payload_value(payload, "executive_summary"), ""),
        "no_material_intervention_needed": _coerce_bool(_payload_value(payload, "no_material_intervention_needed")),
        "no_material_intervention_needed_reason": _coerce_text(
            _payload_value(payload, "no_material_intervention_needed_reason"),
            evidence["no_material_intervention_needed_reason"] if _coerce_bool(_payload_value(payload, "no_material_intervention_needed")) else "",
        ),
        "top_strengths": _coerce_list_of_dicts(
            _payload_value(payload, "top_strengths"),
            ["title", "evidence", "what_to_repeat", "timestamps", "confidence"],
            int(_report_shape_thresholds()["top_strength_limit"]),
            aliases=COACHING_ITEM_FIELD_ALIASES,
        ),
        "strength_inventory": _coerce_list_of_dicts(
            _payload_value(payload, "strength_inventory"),
            ["title", "evidence", "what_to_repeat", "timestamps", "confidence"],
            int(_report_shape_thresholds()["strength_inventory_limit"]),
            aliases=COACHING_ITEM_FIELD_ALIASES,
        ),
        "priority_actions": _coerce_list_of_dicts(
            _payload_value(payload, "priority_actions"),
            ["title", "why_it_matters", "what_we_saw", "what_to_try_next", "timestamps", "confidence"],
            max(config.coach_top_actions, 1),
            aliases=COACHING_ITEM_FIELD_ALIASES,
        ),
        "additional_observation_inventory": _coerce_list_of_dicts(
            _payload_value(payload, "additional_observation_inventory"),
            ["kind", "title", "evidence", "suggested_response", "timestamps", "confidence"],
            int(_report_shape_thresholds()["additional_observation_limit"]),
            aliases=COACHING_ITEM_FIELD_ALIASES,
        ),
        "low_confidence_watchlist": _coerce_list_of_dicts(
            _payload_value(payload, "low_confidence_watchlist"),
            ["title", "why_watch", "what_we_saw", "what_to_monitor_next", "timestamps", "confidence"],
            int(_report_shape_thresholds()["watchlist_limit"]),
            aliases=COACHING_ITEM_FIELD_ALIASES,
        ),
        "keep_doing": _coerce_list_of_strings(_payload_value(payload, "keep_doing"), 4),
        "watch_for": _coerce_list_of_strings(_payload_value(payload, "watch_for"), 4),
        "confidence_notes": _coerce_list_of_strings(_payload_value(payload, "confidence_notes"), 6),
        "evidence_moments": _coerce_list_of_dicts(
            _payload_value(payload, "evidence_moments"),
            ["timestamp", "headline", "observed_behavior", "metric_evidence", "qwen_interpretation", "coaching_implication"],
            6,
            aliases=COACHING_ITEM_FIELD_ALIASES,
        ),
    }

    # Keep the report schema-compatible if the model expressed "no material intervention needed"
    # but omitted the explanation.
    if report["no_material_intervention_needed"] and not report["no_material_intervention_needed_reason"]:
        report["no_material_intervention_needed_reason"] = evidence["no_material_intervention_needed_reason"]

    if report["no_material_intervention_needed"]:
        report["priority_actions"] = []

    report["top_strengths"] = [item for item in report["top_strengths"] if _has_text(item.get("title"))]
    report["strength_inventory"] = [item for item in report["strength_inventory"] if _has_text(item.get("title"))]
    report["priority_actions"] = [item for item in report["priority_actions"] if _has_text(item.get("title"))]
    report["additional_observation_inventory"] = [
        item for item in report["additional_observation_inventory"] if _has_text(item.get("title"))
    ]
    report["low_confidence_watchlist"] = [item for item in report["low_confidence_watchlist"] if _has_text(item.get("title"))]
    report["evidence_moments"] = [
        item for item in report["evidence_moments"] if _has_text(item.get("timestamp")) and _has_text(item.get("headline"))
    ]
    report["keep_doing"] = _unique_strings(report["keep_doing"])
    report["watch_for"] = _unique_strings(report["watch_for"])
    report["confidence_notes"] = _unique_strings(report["confidence_notes"])

    return report


def _validate_llm_report(report: dict[str, Any]) -> bool:
    if not _has_text(report.get("executive_summary")):
        return False
    if report.get("no_material_intervention_needed") and not _has_text(report.get("no_material_intervention_needed_reason")):
        return False
    if not report.get("no_material_intervention_needed") and not report.get("priority_actions"):
        return False
    if report.get("report_shape_version") != REPORT_SHAPE_VERSION:
        return False
    return True


def _merge_llm_report_with_fallback(
    llm_report: dict[str, Any],
    *,
    evidence: dict[str, Any],
    config: CoachingConfig,
    model_name: str,
) -> dict[str, Any]:
    merged = _fallback_report(evidence, config)
    merged["source"] = {
        "mode": "llm_api_hybrid",
        "model": model_name,
    }
    merged["report_shape_version"] = REPORT_SHAPE_VERSION

    if _has_text(llm_report.get("executive_summary")):
        merged["executive_summary"] = llm_report["executive_summary"]
    if llm_report.get("top_strengths"):
        merged["top_strengths"] = llm_report["top_strengths"]
    if llm_report.get("strength_inventory"):
        merged["strength_inventory"] = llm_report["strength_inventory"]
    if llm_report.get("priority_actions") and not evidence.get("no_material_intervention_needed"):
        merged["priority_actions"] = llm_report["priority_actions"]
    if llm_report.get("additional_observation_inventory"):
        merged["additional_observation_inventory"] = llm_report["additional_observation_inventory"]
    if llm_report.get("low_confidence_watchlist"):
        merged["low_confidence_watchlist"] = llm_report["low_confidence_watchlist"]
    if llm_report.get("keep_doing"):
        merged["keep_doing"] = llm_report["keep_doing"]
    if llm_report.get("watch_for"):
        merged["watch_for"] = llm_report["watch_for"]
    if llm_report.get("confidence_notes"):
        merged["confidence_notes"] = llm_report["confidence_notes"]
    if llm_report.get("evidence_moments"):
        merged["evidence_moments"] = llm_report["evidence_moments"]

    if evidence.get("no_material_intervention_needed"):
        merged["no_material_intervention_needed"] = True
        merged["no_material_intervention_needed_reason"] = evidence["no_material_intervention_needed_reason"]
        merged["priority_actions"] = []
    elif llm_report.get("no_material_intervention_needed") and _has_text(llm_report.get("no_material_intervention_needed_reason")):
        merged["no_material_intervention_needed"] = True
        merged["no_material_intervention_needed_reason"] = llm_report["no_material_intervention_needed_reason"]
        merged["priority_actions"] = []

    return merged


def _fallback_report(evidence: dict[str, Any], config: CoachingConfig) -> dict[str, Any]:
    strengths = evidence["draft_top_strengths"]
    strength_inventory = evidence["draft_strength_inventory"]
    actions = evidence["draft_priority_actions"]
    watchlist = evidence["draft_low_confidence_watchlist"]
    additional_inventory = evidence["draft_additional_observation_inventory"]
    keep_doing = [item["what_to_repeat"] for item in strengths[:2]]
    if not keep_doing:
        keep_doing = ["Keep using the moments that already look most stable and room-facing."]

    watch_for = [f"Watch whether {item['title'].lower()} repeats beyond the cited window(s)." for item in watchlist[:2]]
    confidence_notes = evidence["quality_warnings"][:4]
    if not confidence_notes:
        confidence_notes = ["The evidence is sufficient for formative coaching, but still heuristic."]

    executive_parts: list[str]
    if evidence["no_material_intervention_needed"] and strengths:
        executive_parts = [
            f"This clip is mostly a maintenance case: {strengths[0]['title'].lower()} is already visible.",
            evidence["overall_profile"]["pattern_summary"],
            "No material intervention is required from this segment; use the observation inventory as light refinement guidance.",
        ]
    else:
        executive_parts = [
            evidence["overall_profile"]["pattern_summary"],
            f"Best visible window: {evidence['overall_profile']['best_window']['label']}.",
        ]
        if actions:
            executive_parts.append(f"Highest-priority adjustment: {actions[0]['title'].lower()}.")
        else:
            executive_parts.append("No material intervention needed from this clip; use the watchlist and strengths as maintenance guidance.")

    report = {
        "source": {
            "mode": "template_fallback",
            "model": None,
        },
        "report_shape_version": REPORT_SHAPE_VERSION,
        "executive_summary": " ".join(executive_parts),
        "no_material_intervention_needed": bool(evidence["no_material_intervention_needed"]),
        "no_material_intervention_needed_reason": evidence["no_material_intervention_needed_reason"],
        "top_strengths": [
            {
                "title": item["title"],
                "evidence": item["evidence"],
                "what_to_repeat": item["what_to_repeat"],
                "timestamps": item["timestamps"],
                "confidence": item["confidence"],
            }
            for item in strengths
        ],
        "strength_inventory": [
            {
                "title": item["title"],
                "evidence": item["evidence"],
                "what_to_repeat": item["what_to_repeat"],
                "timestamps": item["timestamps"],
                "confidence": item["confidence"],
            }
            for item in strength_inventory
        ],
        "priority_actions": [
            {
                "title": item["title"],
                "why_it_matters": item["why_it_matters"],
                "what_we_saw": item["what_we_saw"],
                "what_to_try_next": item["what_to_try_next"],
                "timestamps": item["timestamps"],
                "confidence": item["confidence"],
            }
            for item in actions
        ],
        "additional_observation_inventory": additional_inventory,
        "low_confidence_watchlist": watchlist,
        "keep_doing": keep_doing,
        "watch_for": watch_for,
        "confidence_notes": confidence_notes,
        "evidence_moments": [
            {
                "timestamp": card["timestamp"],
                "headline": card["headline"],
                "observed_behavior": card["observed_behavior"],
                "metric_evidence": card["metric_evidence"],
                "qwen_interpretation": card["qwen_interpretation"],
                "coaching_implication": card["coaching_implication"],
            }
            for card in evidence["moment_cards"][:6]
        ],
    }
    return report


def _run_coach_llm(evidence: dict[str, Any], config: CoachingConfig, events_path: Path) -> dict[str, Any] | None:
    if config.coach_fallback_template_only:
        return None

    prompt_payload = {
        "report_shape_version": REPORT_SHAPE_VERSION,
        "overall_profile": evidence["overall_profile"],
        "no_material_intervention_needed": evidence["no_material_intervention_needed"],
        "no_material_intervention_needed_reason": evidence["no_material_intervention_needed_reason"],
        "priority_signals": evidence["priority_signals"],
        "strength_signals": evidence["strength_signals"],
        "review_windows": [
            {
                "window_label": row["window_label"],
                "kind": row["kind"],
                "primary_tag": row["primary_tag"],
                "evidence_tags": row["evidence_tags"],
                "metrics": row["metrics"],
                "quality_control": row["quality_control"],
                "qwen": {
                    "summary": row["qwen"]["summary"],
                    "aggregate": row["qwen"]["aggregate"],
                },
            }
            for row in evidence["review_windows"]
        ],
        "draft_priority_actions": evidence["draft_priority_actions"],
        "draft_action_candidates": evidence["draft_action_candidates"],
        "draft_top_strengths": evidence["draft_top_strengths"],
        "draft_strength_inventory": evidence["draft_strength_inventory"],
        "draft_low_confidence_watchlist": evidence["draft_low_confidence_watchlist"],
        "draft_additional_observation_inventory": evidence["draft_additional_observation_inventory"],
        "draft_strength_candidates": evidence["draft_strength_candidates"],
        "quality_warnings": evidence["quality_warnings"],
        "moment_cards": evidence["moment_cards"],
        "top_action_count": config.coach_top_actions,
    }
    prompt_json = json.dumps(prompt_payload, indent=2, ensure_ascii=True)

    if is_gemini_model(config.coach_model):
        try:
            parsed, _raw_text = generate_gemini_json(
                model_name=config.coach_model,
                system_instruction=COACHING_GEMINI_SYSTEM_INSTRUCTION,
                user_text=prompt_json,
                max_output_tokens=1600,
                temperature=0.0,
                response_json_schema=COACHING_REPORT_SCHEMA,
            )
        except Exception as exc:
            log_event(events_path, "coaching_llm_inference_failed", reason=f"{type(exc).__name__}: {exc}", model=config.coach_model)
            return None

        report = _build_llm_report(
            parsed,
            source_mode="llm_api",
            model_name=config.coach_model,
            evidence=evidence,
            config=config,
        )
        if not _validate_llm_report(report):
            hybrid = _merge_llm_report_with_fallback(
                report,
                evidence=evidence,
                config=config,
                model_name=config.coach_model,
            )
            log_event(
                events_path,
                "coaching_llm_partial_output",
                reason="Schema-valid Gemini output did not satisfy feedback_first_v1 validation; merged onto deterministic fallback.",
                model=config.coach_model,
            )
            return hybrid
        log_event(events_path, "coaching_llm_completed", model=config.coach_model, action_count=len(report["priority_actions"]))
        return report

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as exc:
        log_event(events_path, "coaching_llm_unavailable", reason=f"Missing text-model deps: {type(exc).__name__}: {exc}")
        return None

    device = config.coach_device
    if device.startswith("cuda") and not torch.cuda.is_available():
        device = "cpu"
    torch_dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32

    try:
        tokenizer = AutoTokenizer.from_pretrained(config.coach_model, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            config.coach_model,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        ).to(device)
        model.eval()
    except Exception as exc:
        log_event(events_path, "coaching_llm_load_failed", reason=f"{type(exc).__name__}: {exc}", model=config.coach_model)
        return None

    messages = [
        {"role": "system", "content": COACHING_PROMPT},
        {"role": "user", "content": prompt_json},
    ]

    try:
        if hasattr(tokenizer, "apply_chat_template"):
            prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt_text = COACHING_PROMPT + "\n\n" + prompt_json
        inputs = tokenizer(prompt_text, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                do_sample=True,
                temperature=0.2,
                max_new_tokens=900,
            )
        generated = generated[:, inputs["input_ids"].shape[1] :]
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=True)[0]
        parsed = _extract_json_blob(decoded)
    except Exception as exc:
        event_name = "coaching_llm_invalid_output" if isinstance(exc, (json.JSONDecodeError, ValueError)) else "coaching_llm_inference_failed"
        log_event(events_path, event_name, reason=f"{type(exc).__name__}: {exc}", model=config.coach_model)
        return None
    finally:
        try:
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    report = _build_llm_report(
        parsed,
        source_mode="llm",
        model_name=config.coach_model,
        evidence=evidence,
        config=config,
    )
    if not _validate_llm_report(report):
        log_event(events_path, "coaching_llm_invalid_output", model=config.coach_model)
        return None
    log_event(events_path, "coaching_llm_completed", model=config.coach_model, action_count=len(report["priority_actions"]))
    return report


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _render_markdown(report: dict[str, Any], evidence: dict[str, Any], artifacts: CoachingArtifacts) -> str:
    lines = [
        "# Teacher Coaching Brief",
        "",
        f"- Source clip: `{evidence['run_context']['clip_video']}`",
        f"- Analyzed duration: `{evidence['run_context']['duration_sec_actual']:.2f}s`",
        f"- Window count: `{evidence['run_context']['window_count']}`",
        f"- Report mode: `{report['source']['mode']}`",
        f"- Report shape: `{report.get('report_shape_version', REPORT_SHAPE_VERSION)}`",
        "",
        "## At a Glance",
        "",
        report["executive_summary"],
        "",
        f"Reliability: {evidence['overall_profile']['reliability']}.",
        "",
        "## Top 3 Actions for the Next Lecture",
        "",
    ]

    if report.get("no_material_intervention_needed"):
        lines.extend(
            [
                "- No material intervention needed from this clip.",
                f"- Why: {report.get('no_material_intervention_needed_reason', 'The evidence did not justify a corrective action.')}",
                "",
            ]
        )
    else:
        for index, action in enumerate(report["priority_actions"][:3], start=1):
            timestamps = action.get("timestamps", [])
            if isinstance(timestamps, str):
                timestamps = [timestamps]
            lines.extend(
                [
                    f"### {index}. {action['title']}",
                    "",
                    f"- Why it matters: {action['why_it_matters']}",
                    f"- What we saw: {action['what_we_saw']}",
                    f"- What to try next: {action['what_to_try_next']}",
                    f"- Review at: {', '.join(timestamps)}",
                    f"- Confidence: {action['confidence']}",
                    "",
                ]
            )
        if not report["priority_actions"]:
            lines.append("- No priority actions were generated for this run.")

    lines.extend(["## Strengths to Preserve", ""])
    for item in report["top_strengths"]:
        timestamps = item.get("timestamps", [])
        if isinstance(timestamps, str):
            timestamps = [timestamps]
        lines.extend(
            [
                f"### {item['title']}",
                "",
                f"- Evidence: {item['evidence']}",
                f"- What to repeat: {item.get('what_to_repeat', 'Keep this visible pattern available as a default during explanation.')}",
                f"- Review at: {', '.join(timestamps)}",
                f"- Confidence: {item['confidence']}",
                "",
            ]
        )
    if not report["top_strengths"]:
        lines.append("- No single strength clearly dominated the clip; use the cited windows as manual review anchors.")

    extra_strengths = report.get("strength_inventory", [])[len(report.get("top_strengths", [])) :]
    if extra_strengths:
        lines.extend(["", "## Strength Inventory", ""])
        for item in extra_strengths:
            timestamps = item.get("timestamps", [])
            if isinstance(timestamps, str):
                timestamps = [timestamps]
            lines.append(
                f"- **{item['title']}**: {item['evidence']} Repeat by {item.get('what_to_repeat', 'keeping the same visible pattern available')}"
                f" Review at {', '.join(timestamps)}. Confidence: {item['confidence']}."
            )

    if report.get("additional_observation_inventory"):
        lines.extend(["", "## Additional Observation Inventory", ""])
        for item in report["additional_observation_inventory"]:
            timestamps = item.get("timestamps", [])
            if isinstance(timestamps, str):
                timestamps = [timestamps]
            lines.extend(
                [
                    f"### {item['title']} ({str(item.get('kind', 'observation')).replace('_', ' ')})",
                    "",
                    f"- Evidence: {item['evidence']}",
                    f"- Suggested response: {item['suggested_response']}",
                    f"- Review at: {', '.join(timestamps)}",
                    f"- Confidence: {item['confidence']}",
                    "",
                ]
            )

    if report.get("low_confidence_watchlist"):
        lines.extend(["## Low-Confidence Watchlist", ""])
        for item in report["low_confidence_watchlist"]:
            timestamps = item.get("timestamps", [])
            if isinstance(timestamps, str):
                timestamps = [timestamps]
            lines.extend(
                [
                    f"### {item['title']}",
                    "",
                    f"- Why it stays on the watchlist: {item['why_watch']}",
                    f"- What we saw: {item['what_we_saw']}",
                    f"- What to monitor next: {item['what_to_monitor_next']}",
                    f"- Review at: {', '.join(timestamps)}",
                    f"- Confidence: {item['confidence']}",
                    "",
                ]
            )

    lines.extend(["", "## Moment-by-Moment Evidence", ""])
    moment_lookup = {card["timestamp"]: card for card in evidence["moment_cards"]}
    window_lookup = {window["window_label"]: window for window in evidence["review_windows"]}
    for card in report["evidence_moments"][:6]:
        lines.extend([f"### {card['timestamp']} - {card['headline']}", ""])
        moment = moment_lookup.get(card["timestamp"])
        if moment:
            image_name = moment["image_path"]
            lines.append(f"![Evidence frame](coaching_moments/{image_name})")
            lines.append("")
        lines.extend(
            [
                f"- Observed behavior: {card['observed_behavior']}",
                f"- Metric evidence: {card['metric_evidence']}",
                f"- Semantic interpretation: {card['qwen_interpretation']}",
                f"- Coaching implication: {card['coaching_implication']}",
                "",
            ]
        )
        window = window_lookup.get(card["timestamp"])
        if window:
            lines.append(f"QC confidence: `{window['quality_control']['confidence']}`")
            lines.append("")

    lines.extend(["## Reliability Notes", ""])
    for note in report["confidence_notes"]:
        lines.append(f"- {note}")

    if report["keep_doing"]:
        lines.extend(["", "## Keep Doing", ""])
        for item in report["keep_doing"]:
            lines.append(f"- {item}")

    if report["watch_for"]:
        lines.extend(["", "## Watch For", ""])
        for item in report["watch_for"]:
            lines.append(f"- {item}")

    lines.extend(["", "## Technical Appendix", ""])
    score = evidence["score_snapshot"]
    lines.extend(
        [
            _markdown_table(
                ["Metric", "Value", "Band"],
                [
                    ["Overall score", f"{score['overall_score']:.1f}", _metric_band(float(score["overall_score"]))],
                    ["Natural movement", f"{score['natural_movement_score']:.1f}", _metric_band(float(score["natural_movement_score"]))],
                    ["Eye-contact distribution", f"{score['eye_contact_distribution_score']:.1f}", _metric_band(float(score["eye_contact_distribution_score"]))],
                    ["Confidence/presence", f"{score['confidence_presence_score']:.1f}", _metric_band(float(score["confidence_presence_score"]))],
                ],
            ),
            "",
            "- Raw metric summary: `summary_full.md`",
            "- Window summary: `window_summary.md`",
            "- Semantic summary: `semantic_extensions/semantic_summary.md` if semantic mode was enabled for the run",
            "- Coaching evidence JSON: `coaching_evidence.json`",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _render_pdf(markdown_path: Path, output_path: Path) -> None:
    import markdown
    from weasyprint import CSS, HTML

    text = markdown_path.read_text(encoding="utf-8")
    body_html = markdown.markdown(
        text,
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
        ],
        output_format="html5",
    )
    html = f"""<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Teacher Coaching Brief</title></head>
  <body>{body_html}</body>
</html>
"""
    css = """
    @page {
      size: A4;
      margin: 16mm 16mm 18mm 16mm;
      @bottom-right {
        content: counter(page);
        font-size: 9pt;
        color: #5f6b76;
      }
    }
    body {
      font-family: "DejaVu Serif", Georgia, serif;
      color: #17202a;
      font-size: 10.5pt;
      line-height: 1.45;
    }
    h1, h2, h3 {
      font-family: "DejaVu Sans", Arial, sans-serif;
      color: #103b52;
      page-break-after: avoid;
    }
    h1 {
      font-size: 22pt;
      border-bottom: 3px solid #103b52;
      padding-bottom: 8px;
      margin-bottom: 18px;
    }
    h2 {
      font-size: 15pt;
      margin-top: 22px;
      border-bottom: 1px solid #cbd6de;
      padding-bottom: 4px;
    }
    h3 {
      font-size: 12pt;
      margin-top: 16px;
    }
    p, ul, ol, table, img {
      page-break-inside: avoid;
    }
    img {
      display: block;
      margin: 8px auto 14px auto;
      max-width: 88%;
      border: 1px solid #d5dde3;
    }
    code {
      background: #f4f7f9;
      padding: 1px 3px;
      border-radius: 3px;
      font-family: "DejaVu Sans Mono", monospace;
      font-size: 9pt;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 14px 0;
      font-size: 9.3pt;
    }
    th, td {
      border: 1px solid #c8d4dc;
      padding: 6px 7px;
      vertical-align: top;
    }
    th {
      background: #ecf2f7;
      font-family: "DejaVu Sans", Arial, sans-serif;
      text-align: left;
    }
    strong {
      color: #103b52;
    }
    """
    HTML(string=html, base_url=str(markdown_path.parent.resolve())).write_pdf(
        str(output_path),
        stylesheets=[CSS(string=css)],
    )


def run_coaching_report(
    clip_path: Path,
    frame_metrics_df: pd.DataFrame,
    summary: dict[str, Any],
    window_df: pd.DataFrame,
    run_dir: Path,
    config: CoachingConfig,
    events_path: Path,
    semantic_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    artifacts = build_coaching_artifacts(run_dir)
    review_windows, qwen_samples = _build_review_windows(
        clip_path=clip_path,
        frame_metrics_df=frame_metrics_df,
        window_df=window_df,
        artifacts=artifacts,
        config=config,
        events_path=events_path,
    )

    qwen_by_window: dict[str, dict[str, Any]] = {}
    if config.qwen_enabled and qwen_samples:
        semantic_config = SemanticConfig(
            enabled=True,
            qwen_enabled=True,
            qwen_model=config.qwen_model,
            qwen_device=config.qwen_device,
            qwen_device_map=config.qwen_device_map,
            qwen_dtype=config.qwen_dtype,
            qwen_max_new_tokens=config.qwen_max_new_tokens,
            qwen_temperature=config.qwen_temperature,
            sam2_enabled=False,
        )
        qwen_result = _run_qwen(
            qwen_samples,
            semantic_config,
            events_path,
            event_name="coaching_qwen_batch_completed",
        )
        if qwen_result.get("status") == "completed":
            annotations = qwen_result.get("annotations", [])
            grouped_annotations: dict[str, list[dict[str, Any]]] = {}
            for row in annotations:
                reason = str(row.get("reason", ""))
                window_id = reason.split("|", 1)[0]
                grouped_annotations.setdefault(window_id, []).append(row)
            for window in review_windows:
                qwen_window = _summarize_qwen_window(grouped_annotations.get(window["id"], []))
                window["qwen"] = qwen_window
                window["evidence_tags"] = _merge_qwen_into_window_tags(window, qwen_window)
                window["primary_tag"] = _primary_tag(window["evidence_tags"], window["kind"])
                qwen_by_window[window["id"]] = qwen_window
        else:
            for window in review_windows:
                window["qwen"] = {
                    "status": qwen_result.get("status", "not_available"),
                    "summary": qwen_result.get("reason", "Targeted semantic interpretation was not available for this window."),
                    "aggregate": {},
                    "annotations": [],
                }
                qwen_by_window[window["id"]] = window["qwen"]
        log_event(
            events_path,
            "coaching_qwen_completed",
            window_count=len(review_windows),
            qwen_window_count=sum(1 for window in review_windows if window["qwen"]["status"] == "completed"),
        )
    else:
        for window in review_windows:
            window["qwen"] = {
                "status": "not_available",
                "summary": "Targeted semantic interpretation was not run for this window.",
                "aggregate": {},
                "annotations": [],
            }

    evidence = _build_evidence_payload(
        summary=summary,
        window_df=window_df,
        review_windows=review_windows,
        semantic_payload=semantic_payload,
        config=config,
    )

    report = _run_coach_llm(evidence, config, events_path)
    if report is None:
        report = _fallback_report(evidence, config)

    markdown_text = _render_markdown(report, evidence, artifacts)

    artifacts.evidence_json_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=True), encoding="utf-8")
    artifacts.report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    artifacts.report_md_path.write_text(markdown_text, encoding="utf-8")

    pdf_status = "skipped"
    pdf_reason = "PDF rendering disabled."
    if config.coach_render_pdf:
        try:
            _render_pdf(artifacts.report_md_path, artifacts.report_pdf_path)
            pdf_status = "completed"
            pdf_reason = "PDF rendered successfully."
        except Exception as exc:
            pdf_status = "failed"
            pdf_reason = f"{type(exc).__name__}: {exc}"

    log_event(
        events_path,
        "coaching_report_finished",
        report_json=str(artifacts.report_json_path),
        report_md=str(artifacts.report_md_path),
        report_pdf=str(artifacts.report_pdf_path) if config.coach_render_pdf else None,
        pdf_status=pdf_status,
        pdf_reason=pdf_reason,
        action_count=len(report["priority_actions"]),
        strength_count=len(report["top_strengths"]),
    )
    return {
        "artifacts": {
            "evidence_json": str(artifacts.evidence_json_path),
            "report_json": str(artifacts.report_json_path),
            "report_md": str(artifacts.report_md_path),
            "report_pdf": str(artifacts.report_pdf_path),
            "moments_dir": str(artifacts.moments_dir),
        },
        "evidence": evidence,
        "report": report,
        "pdf_status": pdf_status,
        "pdf_reason": pdf_reason,
        "qwen_windows": qwen_by_window,
    }
