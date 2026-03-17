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

from .pipeline import log_event
from .semantic import SemanticConfig, SemanticSample, _extract_frame_at, _extract_json_blob, _run_qwen


@dataclass(slots=True)
class CoachingConfig:
    enabled: bool = False
    coach_model: str = "Qwen/Qwen2.5-3B-Instruct"
    coach_device: str = "cuda:1"
    coach_max_windows: int = 6
    coach_top_actions: int = 3
    coach_render_pdf: bool = True
    coach_fallback_template_only: bool = False
    qwen_enabled: bool = True
    qwen_model: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    qwen_device: str = "cuda:0"
    qwen_device_map: str | None = None
    qwen_dtype: str = "bfloat16"
    qwen_max_new_tokens: int = 180
    qwen_temperature: float = 0.1


@dataclass(slots=True)
class CoachingArtifacts:
    evidence_json_path: Path
    report_json_path: Path
    report_md_path: Path
    report_pdf_path: Path
    moments_dir: Path


COACHING_PROMPT = """You are a teacher coach writing concise, practical feedback from structured nonverbal evidence.
Return JSON only with exactly these top-level keys:
- executive_summary: string, max 85 words
- top_strengths: array of objects with keys [title, evidence, timestamps, confidence]
- priority_actions: array of objects with keys [title, why_it_matters, what_we_saw, what_to_try_next, timestamps, confidence]
- keep_doing: array of short strings
- watch_for: array of short strings
- confidence_notes: array of short strings
- evidence_moments: array of objects with keys [timestamp, headline, observed_behavior, metric_evidence, qwen_interpretation, coaching_implication]

Requirements:
- Use only the evidence provided by the user message.
- Every priority action must cite one or more timestamps already present in the evidence.
- Keep the tone direct, respectful, coach-like, and actionable.
- Do not assign global teacher-quality labels.
- If the evidence is weak, say so in confidence_notes instead of inventing certainty.
- Prefer concrete next-lecture experiments over generic advice.
Do not add markdown or explanation outside the JSON object."""


ACTION_TEMPLATES: dict[str, dict[str, str]] = {
    "note_reading": {
        "title": "Reduce extended note-reading",
        "why": "Frequent downward checks can weaken room connection and make delivery feel less direct.",
        "try": "Raise notes closer to eye level and rehearse short glance-return cycles during key explanations.",
    },
    "uneven_room_scan": {
        "title": "Deliberately sweep the room",
        "why": "More even attention across the room helps students feel included and keeps engagement distributed.",
        "try": "At each major point, pause and sweep left-center-right before moving on.",
    },
    "low_audience_orientation": {
        "title": "Turn back toward the audience sooner",
        "why": "Audience-facing body orientation supports perceived connection and makes eye-contact cues more visible.",
        "try": "After each board or note check, reset your shoulders and chin back toward the room.",
    },
    "closed_posture": {
        "title": "Open the stance between points",
        "why": "A more open posture tends to read as more confident and easier to approach.",
        "try": "Let the elbows open slightly and release any folded or guarded arm positions between points.",
    },
    "limited_movement": {
        "title": "Add more purposeful gesture emphasis",
        "why": "Too little movement can flatten emphasis and make key ideas feel less animated.",
        "try": "Choose one or two moments per minute where you deliberately use an open explanatory gesture.",
    },
    "over_animated_delivery": {
        "title": "Tighten the peak size of gestures",
        "why": "Large bursts of motion can distract from the teaching point when they are not tightly timed.",
        "try": "Keep big gestures for true emphasis and use smaller controlled hand movements elsewhere.",
    },
    "tense_or_neutral_affect": {
        "title": "Soften the visible facial tone",
        "why": "A more relaxed facial tone can make explanations feel warmer and less guarded.",
        "try": "Reset the face between sentences and let the expression relax before the next point.",
    },
    "reduced_alertness": {
        "title": "Increase room-checking behavior",
        "why": "Alert room-facing behavior helps the lecture feel more responsive and attentive.",
        "try": "Build in quick audience checks after transitions instead of staying fixed on notes or a single spot.",
    },
}

STRENGTH_TEMPLATES: dict[str, dict[str, str]] = {
    "distributed_room_engagement": {
        "title": "Distributed room engagement",
        "evidence": "Head and gaze behavior are spread across more than one audience sector.",
    },
    "upright_confident_presence": {
        "title": "Upright confident presence",
        "evidence": "Posture and stance read as stable and open rather than collapsed or closed off.",
    },
    "controlled_expressive_gestures": {
        "title": "Controlled expressive gestures",
        "evidence": "Gesture activity looks intentional and explanatory without strong over-animation flags.",
    },
    "welcoming_affect": {
        "title": "Welcoming visible tone",
        "evidence": "Facial-affect proxies suggest a more approachable or positive delivery tone.",
    },
    "alert_room_presence": {
        "title": "Alert room presence",
        "evidence": "Visible eye-open and room-facing cues suggest alert, attentive delivery.",
    },
    "open_palm_explaining": {
        "title": "Open-palm explanatory delivery",
        "evidence": "Semantic review repeatedly identified open-palm explaining rather than closed or static action.",
    },
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
    if face_coverage >= 0.92 and hand_coverage >= 0.85 and pose_coverage >= 0.97:
        return "high"
    if face_coverage >= 0.70 and pose_coverage >= 0.92:
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
    if score >= 75:
        return "strong"
    if score >= 55:
        return "moderate"
    return "limited"


def _risk_band(score: float) -> str:
    if score >= 65:
        return "high"
    if score >= 35:
        return "moderate"
    return "low"


def _overall_pattern(summary: dict[str, Any], semantic_payload: dict[str, Any] | None) -> str:
    score = summary["scores"]
    parts: list[str] = []
    if score["confidence_presence_score"] >= 72 and score["posture_stability_score"] >= 75:
        parts.append("Delivery generally reads as upright and physically settled")
    elif score["confidence_presence_score"] < 60:
        parts.append("Delivery looks less settled in physical presence")

    if score["eye_contact_distribution_score"] >= 70:
        parts.append("room engagement appears reasonably distributed")
    elif score["eye_contact_distribution_score"] < 55:
        parts.append("room engagement looks uneven")

    if score["natural_movement_score"] >= 68 and summary["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"] < 35:
        parts.append("gesture use is mostly controlled and explanatory")
    elif summary["category_feedback"]["gesture_and_facial_expression"]["static_behavior_risk"] >= 35:
        parts.append("movement is somewhat limited")
    elif summary["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"] >= 50:
        parts.append("some motion spikes may be larger than needed")

    if semantic_payload:
        qwen = semantic_payload.get("summary", {}).get("qwen", {})
        if qwen.get("status") == "completed":
            aggregate = qwen.get("aggregate", {})
            if aggregate.get("notes_focus_ratio", 0.0) >= 0.40:
                parts.append("semantic review suggests the clip includes noticeable note-reading")
            elif aggregate.get("audience_focus_ratio", 0.0) >= 0.55:
                parts.append("semantic review sees the instructor mostly addressing the audience")

    if not parts:
        parts.append("The clip is trackable, but the nonverbal pattern is mixed rather than dominated by one clear trait")
    return "; ".join(parts) + "."


def _reliability_notes(summary: dict[str, Any]) -> dict[str, Any]:
    qc = summary["quality_control"]
    clip = summary["clip"]
    notes: list[str] = []
    if qc["face_coverage"] < 0.85:
        notes.append("Face visibility is limited in parts of the clip, so eye-contact and facial-tone claims are less certain.")
    if qc["hand_coverage"] < 0.80:
        notes.append("Hand visibility drops in parts of the clip, so gesture labels are less certain.")
    if clip["duration_sec_actual"] < 30:
        notes.append("Short duration limits how confidently the report can generalize beyond this segment.")
    for warning in summary["warnings"]:
        if warning not in notes:
            notes.append(warning)
    if not notes:
        notes.append("Tracking quality is stable enough for formative review, but the outputs remain heuristic proxies rather than direct teaching-quality measures.")

    qc_score = 0
    qc_score += 1 if qc["pose_coverage"] >= 0.97 else 0
    qc_score += 1 if qc["face_coverage"] >= 0.90 else 0
    qc_score += 1 if qc["hand_coverage"] >= 0.85 else 0
    qc_score += 1 if clip["duration_sec_actual"] >= 45 else 0
    label = "high" if qc_score >= 4 else "medium" if qc_score >= 2 else "low"
    return {
        "label": label,
        "summary": f"Reliability is {label} for this segment based on face, hand, and pose coverage plus clip length.",
        "notes": notes,
    }


def _window_priority_candidates(window_df: pd.DataFrame) -> list[dict[str, Any]]:
    if window_df.empty:
        return []

    candidates: list[dict[str, Any]] = []

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
    if float(eye_row["eye_contact_distribution_score"]) < 68:
        add_candidate(eye_row, "action", "low_eye_contact_distribution", 100.0 - float(eye_row["eye_contact_distribution_score"]))

    presence_row = window_df.assign(
        presence_issue=lambda df: np.maximum(
            100.0 - df["confidence_presence_score"],
            df["closed_posture_risk"],
        )
    ).sort_values("presence_issue", ascending=False).iloc[0]
    if float(presence_row["presence_issue"]) >= 35:
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
    if float(movement_row["movement_issue"]) >= 35:
        add_candidate(movement_row, "action", "movement_issue", float(movement_row["movement_issue"]))

    affect_issue_df = window_df.assign(
        affect_issue=lambda df: np.maximum(
            100.0 - df["positive_affect_score"],
            df["tension_hostility_risk"],
        )
    )
    affect_row = affect_issue_df.sort_values("affect_issue", ascending=False).iloc[0]
    if float(affect_row["affect_issue"]) >= 35:
        add_candidate(affect_row, "action", "affect_issue", float(affect_row["affect_issue"]))

    face_row = window_df.sort_values("face_coverage", ascending=True).iloc[0]
    if float(face_row["face_coverage"]) < 0.85:
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
    if kind != "strength":
        if row["face_coverage"] < 0.85:
            tags.append("low_face_visibility")
        if row["eye_contact_distribution_score"] < 55:
            tags.append("uneven_room_scan")
        if row["audience_orientation_score"] < 55:
            tags.append("low_audience_orientation")
        if row["confidence_presence_score"] < 60 or row["closed_posture_risk"] >= 35:
            tags.append("closed_posture")
        if row["natural_movement_score"] < 45 and row["static_behavior_risk"] >= 35:
            tags.append("limited_movement")
        if row["excessive_animation_risk"] >= 50:
            tags.append("over_animated_delivery")
        if row["positive_affect_score"] < 50 or row["tension_hostility_risk"] >= 35:
            tags.append("tense_or_neutral_affect")
        if row["alertness_score"] < 60:
            tags.append("reduced_alertness")

    if kind == "strength":
        if row["eye_contact_distribution_score"] >= 70:
            tags.append("distributed_room_engagement")
        if row["confidence_presence_score"] >= 75 and row["posture_stability_score"] >= 75:
            tags.append("upright_confident_presence")
        if row["natural_movement_score"] >= 65 and row["excessive_animation_risk"] < 35:
            tags.append("controlled_expressive_gestures")
        if row["positive_affect_score"] >= 55:
            tags.append("welcoming_affect")
        if row["alertness_score"] >= 75:
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
            "summary": "No targeted Qwen interpretation was available for this review window.",
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
        summary_parts.append("Qwen sees repeated note-reading or notes-focused attention")
    elif ratio(focus_counts, "audience") >= 0.5:
        summary_parts.append("Qwen sees the teacher mainly addressing the audience")
    elif ratio(focus_counts, "board") + ratio(focus_counts, "screen") >= 0.5:
        summary_parts.append("Qwen sees the teacher mainly oriented to board or screen content")

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
        "summary": "; ".join(summary_parts) + "." if summary_parts else "Qwen window review returned mixed or ambiguous evidence.",
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


def _draft_action_candidates(review_windows: list[dict[str, Any]], top_actions: int) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for window in review_windows:
        if window["kind"] == "strength":
            continue
        tag = _primary_tag(window["evidence_tags"], "action")
        if tag not in ACTION_TEMPLATES:
            continue
        bucket = grouped.setdefault(
            tag,
            {
                "tag": tag,
                "priority": 0.0,
                "timestamps": [],
                "windows": [],
                "confidence": "low",
                "what_we_saw_parts": [],
            },
        )
        bucket["priority"] = max(float(bucket["priority"]), float(window["priority"]))
        bucket["timestamps"].append(window["window_label"])
        bucket["windows"].append(window["id"])
        bucket["confidence"] = "high" if "high" in (bucket["confidence"], window["quality_control"]["confidence"]) else "medium"
        bucket["what_we_saw_parts"].append(
            f"{window['window_label']} showed {tag.replace('_', ' ')} with overall {window['metrics']['overall_score']:.1f}"
        )

    action_candidates: list[dict[str, Any]] = []
    for tag, bucket in grouped.items():
        template = ACTION_TEMPLATES[tag]
        action_candidates.append(
            {
                "tag": tag,
                "title": template["title"],
                "why_it_matters": template["why"],
                "what_we_saw": "; ".join(bucket["what_we_saw_parts"][:2]) + ".",
                "what_to_try_next": template["try"],
                "timestamps": _unique_strings(bucket["timestamps"]),
                "confidence": bucket["confidence"],
                "priority": float(bucket["priority"]),
            }
        )
    action_candidates.sort(key=lambda item: item["priority"], reverse=True)
    return action_candidates[: max(top_actions, 1) + 2]


def _draft_strength_candidates(review_windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for window in review_windows:
        for tag in window["evidence_tags"]:
            if tag not in STRENGTH_TEMPLATES:
                continue
            bucket = grouped.setdefault(
                tag,
                {
                    "tag": tag,
                    "priority": 0.0,
                    "timestamps": [],
                    "confidence": "low",
                },
            )
            bucket["priority"] = max(float(bucket["priority"]), float(window["priority"]))
            bucket["timestamps"].append(window["window_label"])
            bucket["confidence"] = "high" if window["quality_control"]["confidence"] == "high" else "medium"

    strengths: list[dict[str, Any]] = []
    for tag, bucket in grouped.items():
        template = STRENGTH_TEMPLATES[tag]
        strengths.append(
            {
                "tag": tag,
                "title": template["title"],
                "evidence": template["evidence"],
                "timestamps": _unique_strings(bucket["timestamps"]),
                "confidence": bucket["confidence"],
                "priority": float(bucket["priority"]),
            }
        )
    strengths.sort(key=lambda item: item["priority"], reverse=True)
    return strengths[:4]


def _moment_cards(review_windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for window in review_windows[:6]:
        metric_evidence = (
            f"overall={window['metrics']['overall_score']:.1f}, "
            f"eye={window['metrics']['eye_contact_distribution_score']:.1f}, "
            f"presence={window['metrics']['confidence_presence_score']:.1f}, "
            f"natural={window['metrics']['natural_movement_score']:.1f}"
        )
        cards.append(
            {
                "id": window["id"],
                "timestamp": window["window_label"],
                "headline": window["primary_tag"].replace("_", " ").title(),
                "observed_behavior": " / ".join(tag.replace("_", " ") for tag in window["evidence_tags"][:3]) or "mixed evidence",
                "metric_evidence": metric_evidence,
                "qwen_interpretation": window["qwen"]["summary"],
                "coaching_implication": ACTION_TEMPLATES.get(window["primary_tag"], {}).get(
                    "try",
                    "Preserve this delivery pattern and use it as a reference point in later lectures."
                    if window["kind"] == "strength"
                    else "Use this window as a manual review point before changing the delivery pattern.",
                ),
                "image_path": Path(window["display_frame_path"]).name,
            }
        )
    return cards


def _build_evidence_payload(
    summary: dict[str, Any],
    window_df: pd.DataFrame,
    review_windows: list[dict[str, Any]],
    semantic_payload: dict[str, Any] | None,
    config: CoachingConfig,
) -> dict[str, Any]:
    reliability = _reliability_notes(summary)
    action_candidates = _draft_action_candidates(review_windows, config.coach_top_actions)
    strength_candidates = _draft_strength_candidates(review_windows)
    priority_signals = [
        {
            "tag": item["tag"],
            "priority": item["priority"],
            "title": item["title"],
            "timestamps": item["timestamps"],
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
        "recommended_focus_areas": [item["tag"] for item in action_candidates[: config.coach_top_actions]],
        "draft_action_candidates": action_candidates,
        "draft_strength_candidates": strength_candidates,
        "moment_cards": _moment_cards(review_windows),
    }


def _coerce_list_of_strings(values: Any, limit: int) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()][:limit]


def _coerce_list_of_dicts(values: Any, fields: list[str], limit: int) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        return []
    out: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, dict):
            continue
        row = {field: value.get(field, "") for field in fields}
        out.append(row)
        if len(out) >= limit:
            break
    return out


def _fallback_report(evidence: dict[str, Any], config: CoachingConfig) -> dict[str, Any]:
    strengths = evidence["draft_strength_candidates"][:4]
    actions = evidence["draft_action_candidates"][: max(config.coach_top_actions, 1)]
    keep_doing = [f"Keep {item['title'].lower()} visible in future lectures." for item in strengths[:2]]
    if not keep_doing:
        keep_doing = ["Keep using the moments that already look most stable and room-facing."]

    watch_for = [f"Watch for {item['tag'].replace('_', ' ')} in the windows cited below." for item in actions[:2]]
    confidence_notes = evidence["quality_warnings"][:4]
    if not confidence_notes:
        confidence_notes = ["The evidence is sufficient for formative coaching, but still heuristic."]

    executive_parts = [
        evidence["overall_profile"]["pattern_summary"],
        f"Best visible window: {evidence['overall_profile']['best_window']['label']}.",
    ]
    if actions:
        executive_parts.append(f"Highest-priority adjustment: {actions[0]['title'].lower()}.")

    report = {
        "source": {
            "mode": "template_fallback",
            "model": None,
        },
        "executive_summary": " ".join(executive_parts),
        "top_strengths": [
            {
                "title": item["title"],
                "evidence": item["evidence"],
                "timestamps": item["timestamps"],
                "confidence": item["confidence"],
            }
            for item in strengths
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

    prompt_payload = {
        "overall_profile": evidence["overall_profile"],
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
        "draft_action_candidates": evidence["draft_action_candidates"],
        "draft_strength_candidates": evidence["draft_strength_candidates"],
        "quality_warnings": evidence["quality_warnings"],
        "moment_cards": evidence["moment_cards"],
        "top_action_count": config.coach_top_actions,
    }
    prompt_json = json.dumps(prompt_payload, indent=2, ensure_ascii=True)
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
        log_event(events_path, "coaching_llm_inference_failed", reason=f"{type(exc).__name__}: {exc}", model=config.coach_model)
        return None
    finally:
        try:
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    report = {
        "source": {
            "mode": "llm",
            "model": config.coach_model,
        },
        "executive_summary": str(parsed.get("executive_summary", "")).strip(),
        "top_strengths": _coerce_list_of_dicts(parsed.get("top_strengths"), ["title", "evidence", "timestamps", "confidence"], 4),
        "priority_actions": _coerce_list_of_dicts(
            parsed.get("priority_actions"),
            ["title", "why_it_matters", "what_we_saw", "what_to_try_next", "timestamps", "confidence"],
            max(config.coach_top_actions, 1),
        ),
        "keep_doing": _coerce_list_of_strings(parsed.get("keep_doing"), 4),
        "watch_for": _coerce_list_of_strings(parsed.get("watch_for"), 4),
        "confidence_notes": _coerce_list_of_strings(parsed.get("confidence_notes"), 6),
        "evidence_moments": _coerce_list_of_dicts(
            parsed.get("evidence_moments"),
            ["timestamp", "headline", "observed_behavior", "metric_evidence", "qwen_interpretation", "coaching_implication"],
            6,
        ),
    }
    if not report["executive_summary"] or not report["priority_actions"]:
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

    lines.extend(["## Strengths to Preserve", ""])
    for item in report["top_strengths"]:
        timestamps = item.get("timestamps", [])
        if isinstance(timestamps, str):
            timestamps = [timestamps]
        lines.append(f"- **{item['title']}**: {item['evidence']} Review at {', '.join(timestamps)}. Confidence: {item['confidence']}.")
    if not report["top_strengths"]:
        lines.append("- No single strength clearly dominated the clip; use the cited windows as manual review anchors.")

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
                f"- Qwen interpretation: {card['qwen_interpretation']}",
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
                window["evidence_tags"] = _augment_tags_with_qwen(window["evidence_tags"], qwen_window)
                window["primary_tag"] = _primary_tag(window["evidence_tags"], window["kind"])
                qwen_by_window[window["id"]] = qwen_window
        else:
            for window in review_windows:
                window["qwen"] = {
                    "status": qwen_result.get("status", "not_available"),
                    "summary": qwen_result.get("reason", "Targeted Qwen interpretation was not available for this window."),
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
                "summary": "Targeted Qwen interpretation was not run for this window.",
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
