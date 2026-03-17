from __future__ import annotations

import copy
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = REPO_ROOT / "configs"


DEFAULT_BASE_THRESHOLDS: dict[str, Any] = {
    "version": "0.2.0",
    "quality_control": {
        "pose_stable_min": 0.95,
        "face_stable_min": 0.95,
        "hand_stable_min": 0.85,
        "short_clip_sec": 4.5,
    },
    "interpretation_bands": {
        "strong_min": 75.0,
        "moderate_min": 55.0,
    },
    "risk_bands": {
        "high_min": 65.0,
        "moderate_min": 35.0,
    },
    "feedback_strengths": {
        "natural_movement_min": 70.0,
        "positive_affect_min": 55.0,
        "enthusiasm_min": 65.0,
        "upright_posture_min": 75.0,
        "confidence_presence_min": 70.0,
        "eye_distribution_min": 60.0,
        "alertness_min": 65.0,
    },
    "feedback_watch": {
        "static_behavior_risk_min": 35.0,
        "excessive_animation_risk_min": 35.0,
        "tension_hostility_risk_min": 35.0,
        "rigidity_risk_min": 35.0,
        "closed_posture_risk_min": 35.0,
        "eye_distribution_low_max": 50.0,
        "alertness_low_max": 55.0,
    },
    "coaching": {
        "qc_confidence": {
            "high_face_min": 0.92,
            "high_hand_min": 0.85,
            "high_pose_min": 0.97,
            "medium_face_min": 0.70,
            "medium_pose_min": 0.92,
        },
        "overall_pattern": {
            "presence_strong_min": 72.0,
            "posture_strong_min": 75.0,
            "presence_low_max": 60.0,
            "eye_distribution_strong_min": 70.0,
            "eye_distribution_low_max": 55.0,
            "natural_movement_strong_min": 68.0,
            "static_behavior_risk_min": 35.0,
            "excessive_animation_risk_min": 50.0,
            "notes_focus_ratio_min": 0.40,
            "audience_focus_ratio_min": 0.55,
        },
        "reliability": {
            "note_face_max": 0.85,
            "note_hand_max": 0.80,
            "note_short_clip_sec": 30.0,
            "score_pose_min": 0.97,
            "score_face_min": 0.90,
            "score_hand_min": 0.85,
            "score_duration_sec_min": 45.0,
            "high_score_min": 4,
            "medium_score_min": 2,
        },
        "candidate_thresholds": {
            "eye_contact_action_max": 68.0,
            "presence_issue_min": 35.0,
            "movement_issue_min": 35.0,
            "affect_issue_min": 35.0,
            "face_coverage_action_max": 0.85,
        },
        "window_tags": {
            "face_coverage_low_max": 0.85,
            "eye_distribution_low_max": 55.0,
            "audience_orientation_low_max": 55.0,
            "presence_low_max": 60.0,
            "closed_posture_risk_min": 35.0,
            "natural_movement_low_max": 45.0,
            "static_behavior_risk_min": 35.0,
            "excessive_animation_risk_min": 50.0,
            "positive_affect_low_max": 50.0,
            "tension_hostility_risk_min": 35.0,
            "alertness_low_max": 60.0,
            "strength_eye_distribution_min": 70.0,
            "strength_presence_min": 75.0,
            "strength_posture_min": 75.0,
            "strength_natural_movement_min": 65.0,
            "strength_excessive_animation_max": 35.0,
            "strength_positive_affect_min": 55.0,
            "strength_alertness_min": 75.0,
        },
    },
}


DEFAULT_QWEN_PROMPTS: dict[str, Any] = {
    "version": "0.2.0",
    "frame_semantic_review": {
        "model": "Qwen/Qwen2.5-VL-7B-Instruct",
        "temperature": 0.1,
        "max_new_tokens": 180,
        "prompt": (
            "You are reviewing a single frame from a classroom lecture video.\n"
            "Return JSON only with exactly these keys:\n"
            "- teacher_focus: one of [audience, board, screen, notes, ambiguous]\n"
            "- body_action: one of [open_palm_explaining, pointing_board, pointing_screen, writing_board, walking, static_stance, reading_from_notes, ambiguous]\n"
            "- affect_tone: one of [warm, neutral, tense, ambiguous]\n"
            "- posture_signal: one of [upright_open, upright_neutral, closed_or_slouched, ambiguous]\n"
            "- attention_note: short phrase, at most 12 words\n"
            "- evidence_confidence: one of [low, medium, high]\n"
            "- rationale: short phrase, at most 20 words\n"
            "Do not add markdown or explanation outside the JSON object."
        ),
    },
}


DEFAULT_COACHING_PROMPTS: dict[str, Any] = {
    "version": "0.2.0",
    "coaching_synthesis": {
        "model": "Qwen/Qwen2.5-3B-Instruct",
        "fallback": "template",
        "prompt": (
            "You are a teacher coach writing concise, practical feedback from structured nonverbal evidence.\n"
            "Return JSON only with exactly these top-level keys:\n"
            "- executive_summary: string, max 85 words\n"
            "- top_strengths: array of objects with keys [title, evidence, timestamps, confidence]\n"
            "- priority_actions: array of objects with keys [title, why_it_matters, what_we_saw, what_to_try_next, timestamps, confidence]\n"
            "- keep_doing: array of short strings\n"
            "- watch_for: array of short strings\n"
            "- confidence_notes: array of short strings\n"
            "- evidence_moments: array of objects with keys [timestamp, headline, observed_behavior, metric_evidence, qwen_interpretation, coaching_implication]\n\n"
            "Requirements:\n"
            "- Use only the evidence provided by the user message.\n"
            "- Every priority action must cite one or more timestamps already present in the evidence.\n"
            "- Keep the tone direct, respectful, coach-like, and actionable.\n"
            "- Do not assign global teacher-quality labels.\n"
            "- If the evidence is weak, say so in confidence_notes instead of inventing certainty.\n"
            "- Prefer concrete next-lecture experiments over generic advice.\n"
            "Do not add markdown or explanation outside the JSON object."
        ),
    },
    "action_templates": {
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
    },
    "strength_templates": {
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
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _config_path(filename: str) -> Path:
    return CONFIG_DIR / filename


@lru_cache(maxsize=1)
def load_base_thresholds() -> dict[str, Any]:
    return _deep_merge(DEFAULT_BASE_THRESHOLDS, _load_toml(_config_path("base_thresholds.toml")))


@lru_cache(maxsize=1)
def load_qwen_prompt_config() -> dict[str, Any]:
    return _deep_merge(DEFAULT_QWEN_PROMPTS, _load_toml(_config_path("qwen_vlm_prompts.toml")))


@lru_cache(maxsize=1)
def load_coaching_prompt_config() -> dict[str, Any]:
    return _deep_merge(DEFAULT_COACHING_PROMPTS, _load_toml(_config_path("coaching_prompts.toml")))
