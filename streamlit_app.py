from __future__ import annotations

import json
import os
import shutil
import tempfile
from html import escape
from pathlib import Path
from typing import Any

import cv2
import streamlit as st

from nonverbal_eval.app_service import run_teacher_evaluation
from nonverbal_eval.runtime_config import DEFAULT_GEMINI_MODEL


APP_TITLE = "TeacherEvaluation"
MAX_UPLOAD_DURATION_SEC = 5 * 60
WORK_ROOT = Path("local_data/streamlit")
UPLOAD_ROOT = WORK_ROOT / "uploads"
RUN_ROOT = WORK_ROOT / "runs"
QA_REPORT_JSON_ENV = "TEACHER_EVALUATION_QA_REPORT_JSON"
QA_REPORT_PDF_ENV = "TEACHER_EVALUATION_QA_REPORT_PDF"
SEMANTIC_MODEL_ENV = "TEACHER_EVALUATION_SEMANTIC_MODEL"
LEGACY_SEMANTIC_MODEL_ENV = "TEACHER_EVALUATION_QWEN_MODEL"
COACH_MODEL_ENV = "TEACHER_EVALUATION_COACH_MODEL"

STAGE_LABELS = {
    "start": "Upload accepted",
    "extract_segment_started": "Preparing analysis clip",
    "extract_segment_finished": "Clip prepared",
    "evaluate_full_clip_started": "Running core nonverbal evaluation",
    "evaluate_full_clip_finished": "Core evaluation finished",
    "keyframe_summary_started": "Creating keyframe summary",
    "keyframe_summary_finished": "Technical summary ready",
    "semantic_started": "Running semantic review",
    "semantic_finished": "Semantic review finished",
    "window_aggregation_started": "Aggregating lecture windows",
    "window_aggregation_finished": "Window analysis ready",
    "window_figures_started": "Rendering visual summaries",
    "window_figures_finished": "Visual summaries ready",
    "coaching_started": "Generating coaching report",
    "coaching_finished": "Coaching brief ready",
    "finished": "Evaluation complete",
}

STAGE_DETAILS = {
    "start": "The upload has been accepted and the run workspace is ready.",
    "extract_segment_started": "Preparing a stable analysis clip for the lecture pipeline.",
    "extract_segment_finished": "Clip extraction finished and the full evaluation is about to begin.",
    "evaluate_full_clip_started": "Running the landmark-driven nonverbal metrics over the full clip.",
    "evaluate_full_clip_finished": "Core nonverbal scoring is complete and summary assets are being assembled.",
    "keyframe_summary_started": "Generating the keyframe and technical summary artifacts.",
    "keyframe_summary_finished": "Keyframe summary is ready and the semantic layer can begin.",
    "semantic_started": "Running the contextual review layer to enrich the clip evidence.",
    "semantic_finished": "Contextual evidence is ready and being merged into the run outputs.",
    "window_aggregation_started": "Aggregating the clip into teacher-facing review windows.",
    "window_aggregation_finished": "Window-level evidence is ready for charts and coaching synthesis.",
    "window_figures_started": "Rendering the visual plots and support artifacts.",
    "window_figures_finished": "Visual summaries are ready and the coaching brief is being finalized.",
    "coaching_started": "Generating the teacher-facing coaching brief and export artifacts.",
    "coaching_finished": "Coaching brief is ready and final packaging is in progress.",
    "finished": "Everything is ready, including the report downloads and supporting artifacts.",
}


def _ensure_dirs() -> None:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    RUN_ROOT.mkdir(parents=True, exist_ok=True)


def _video_info(video_path: Path) -> dict[str, float]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open uploaded video: {video_path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {
        "fps": fps,
        "frames": frames,
        "width": width,
        "height": height,
        "duration_sec": frames / fps if fps else 0.0,
    }


def _save_upload(upload) -> Path:
    suffix = Path(upload.name).suffix or ".mp4"
    with tempfile.NamedTemporaryFile(dir=UPLOAD_ROOT, suffix=suffix, delete=False) as handle:
        shutil.copyfileobj(upload, handle)
        return Path(handle.name)


def _load_json(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.exists():
        return None
    return json.loads(file_path.read_text(encoding="utf-8"))


def _semantic_model_name(default: str = DEFAULT_GEMINI_MODEL) -> str:
    return (
        os.getenv(SEMANTIC_MODEL_ENV)
        or os.getenv(LEGACY_SEMANTIC_MODEL_ENV)
        or default
    )


def _inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=EB+Garamond:wght@700;800&display=swap');

        :root {
            --te-bg: #060e20;
            --te-surface: rgba(255, 255, 255, 0.045);
            --te-surface-strong: rgba(255, 255, 255, 0.075);
            --te-border: rgba(255, 255, 255, 0.10);
            --te-blue: #1f4068;
            --te-blue-light: #2d5f9e;
            --te-glow: #5b8fc9;
            --te-text: #ffffff;
            --te-muted: rgba(255, 255, 255, 0.68);
            --te-muted-soft: rgba(255, 255, 255, 0.45);
            --te-shadow: 0 30px 70px rgba(2, 6, 23, 0.45);
            --te-radius-xl: 28px;
            --te-radius-lg: 22px;
            --te-radius-md: 16px;
        }

        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(ellipse at 8% 18%, rgba(31, 64, 104, 0.30) 0%, transparent 42%),
                radial-gradient(ellipse at 92% 28%, rgba(45, 95, 158, 0.20) 0%, transparent 38%),
                radial-gradient(ellipse at 50% 100%, rgba(91, 143, 201, 0.12) 0%, transparent 45%),
                var(--te-bg);
            color: var(--te-text);
        }

        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        [data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }

        [data-testid="stToolbar"],
        [data-testid="stHeaderActionElements"],
        [data-testid="stAppDeployButton"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        #MainMenu {
            display: none !important;
        }

        .block-container {
            position: relative;
            z-index: 2;
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .te-bg-layer,
        .te-grid-bg,
        .te-orb {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
        }

        .te-bg-layer {
            background:
                radial-gradient(ellipse at 5% 40%, rgba(31, 64, 104, 0.22) 0%, transparent 52%),
                radial-gradient(ellipse at 95% 60%, rgba(45, 95, 158, 0.16) 0%, transparent 46%),
                radial-gradient(ellipse at 50% 0%, rgba(91, 143, 201, 0.10) 0%, transparent 42%);
        }

        .te-grid-bg {
            background-image:
                linear-gradient(rgba(45, 95, 158, 0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(45, 95, 158, 0.04) 1px, transparent 1px);
            background-size: 62px 62px;
        }

        .te-orb {
            border-radius: 50%;
            filter: blur(95px);
            opacity: 0.28;
        }

        .te-orb-1 {
            width: 540px;
            height: 540px;
            top: -180px;
            left: -120px;
            background: radial-gradient(circle, rgba(31, 64, 104, 0.70), transparent 68%);
        }

        .te-orb-2 {
            width: 360px;
            height: 360px;
            right: -70px;
            bottom: 10%;
            background: radial-gradient(circle, rgba(45, 95, 158, 0.60), transparent 68%);
        }

        .te-hero {
            position: relative;
            z-index: 1;
            overflow: hidden;
            margin-bottom: 1.4rem;
            padding: 2.3rem 2.4rem 2.1rem;
            border-radius: var(--te-radius-xl);
            border: 1px solid rgba(255, 255, 255, 0.12);
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.03)),
                rgba(5, 13, 31, 0.72);
            box-shadow: var(--te-shadow);
            backdrop-filter: blur(18px);
        }

        .te-hero::before {
            content: "";
            position: absolute;
            inset: auto -8% -35% 48%;
            height: 220px;
            background: radial-gradient(circle, rgba(91, 143, 201, 0.18), transparent 68%);
            pointer-events: none;
        }

        .te-hero h1 {
            margin: 0;
            font-family: "EB Garamond", "Palatino Linotype", Georgia, serif;
            font-size: clamp(2.2rem, 4.2vw, 3.6rem);
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.00;
            color: var(--te-text);
        }

        .te-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1.35rem;
        }

        .te-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.52rem 0.86rem;
            border-radius: 999px;
            border: 1px solid rgba(96, 165, 250, 0.24);
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.88);
            font-size: 0.86rem;
            font-weight: 600;
        }

        .te-section-heading {
            margin-bottom: 0.9rem;
        }

        .te-section-heading h2 {
            margin: 0;
            color: var(--te-text);
            font-size: 1.35rem;
            font-weight: 750;
            letter-spacing: -0.02em;
        }

        .te-section-heading p {
            margin: 0.45rem 0 0;
            color: var(--te-muted-soft);
            font-size: 0.95rem;
            line-height: 1.55;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: var(--te-radius-lg);
            border: 1px solid var(--te-border);
            background: rgba(255, 255, 255, 0.045);
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.22);
            backdrop-filter: blur(14px);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0.2rem 0.1rem;
        }

        div[data-testid="stFileUploaderDropzone"] {
            border-radius: 22px;
            border: 1px dashed rgba(96, 165, 250, 0.34);
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.035)),
                rgba(5, 13, 31, 0.24);
            padding-top: 1.2rem;
            padding-bottom: 1.2rem;
            transition: border-color 0.2s ease, transform 0.2s ease;
        }

        div[data-testid="stFileUploaderDropzone"]:hover {
            border-color: rgba(96, 165, 250, 0.55);
            transform: translateY(-1px);
        }

        /* ── Scorecard grid ─────────────────────────────────────── */
        .te-scorecard-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.8rem;
            margin: 0.6rem 0 1rem;
        }

        .te-score-card {
            padding: 1rem 1.05rem 0.9rem;
            border-radius: var(--te-radius-md);
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(10px);
        }

        .te-score-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.55rem;
        }

        .te-score-label {
            color: var(--te-muted-soft);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .te-score-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 999px;
            flex-shrink: 0;
        }

        .te-score-dot-green  { background: #34d399; box-shadow: 0 0 8px rgba(52,211,153,0.4); }
        .te-score-dot-amber  { background: #fbbf24; box-shadow: 0 0 8px rgba(251,191,36,0.4); }
        .te-score-dot-red    { background: #fb7185; box-shadow: 0 0 8px rgba(251,113,133,0.4); }

        .te-score-number {
            font-size: 1.7rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1;
            color: var(--te-text);
            margin-bottom: 0.45rem;
        }

        .te-score-desc {
            color: var(--te-muted-soft);
            font-size: 0.80rem;
            line-height: 1.45;
        }

        /* ── Verdict strip ──────────────────────────────────────── */
        .te-verdict {
            margin-bottom: 0.8rem;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.07);
            background: rgba(255, 255, 255, 0.03);
            color: rgba(255, 255, 255, 0.80);
            font-size: 0.95rem;
            line-height: 1.55;
            font-style: italic;
        }

        /* ── Container borders — cleaner, less depth ────────────── */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.07);
            background: rgba(255, 255, 255, 0.03);
            box-shadow: 0 4px 24px rgba(2, 6, 23, 0.18);
            backdrop-filter: blur(10px);
        }

        /* ── Buttons ────────────────────────────────────────────── */
        .stButton > button,
        .stDownloadButton > button {
            min-height: 3rem;
            border-radius: 14px;
            border: 1px solid rgba(91, 143, 201, 0.28);
            font-weight: 700;
            letter-spacing: 0.01em;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        }

        .stButton > button[kind="primary"] {
            color: #ffffff;
            background: linear-gradient(135deg, var(--te-blue), var(--te-glow));
            box-shadow: 0 8px 20px rgba(31, 64, 104, 0.38);
        }

        .stButton > button:not([kind="primary"]),
        .stDownloadButton > button {
            color: rgba(255, 255, 255, 0.92);
            background: rgba(255, 255, 255, 0.05);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(91, 143, 201, 0.55);
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.22);
        }

        .stButton > button:disabled,
        .stDownloadButton > button:disabled {
            opacity: 0.55;
        }

        [data-testid="stMetric"] {
            border-radius: var(--te-radius-md);
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
            padding: 1.05rem 1.1rem;
        }

        [data-testid="stMetricLabel"] {
            color: var(--te-muted-soft);
            font-size: 0.84rem;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: var(--te-text);
            font-weight: 780;
            letter-spacing: -0.03em;
        }

        .te-mini-stat {
            height: 100%;
            padding: 1rem 1.05rem;
            border-radius: var(--te-radius-md);
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
        }

        .te-mini-stat-label {
            color: var(--te-muted-soft);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .te-mini-stat-value {
            margin-top: 0.45rem;
            color: var(--te-text);
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.05;
        }

        .te-mini-stat-detail {
            margin-top: 0.45rem;
            color: var(--te-muted-soft);
            font-size: 0.84rem;
            line-height: 1.45;
        }

        .te-inline-note {
            margin-top: 0.8rem;
            color: var(--te-muted-soft);
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .te-status {
            display: flex;
            align-items: flex-start;
            gap: 0.8rem;
            padding: 0.95rem 1rem;
            border-radius: var(--te-radius-md);
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
        }

        .te-status-dot {
            flex: 0 0 0.72rem;
            width: 0.72rem;
            height: 0.72rem;
            border-radius: 999px;
            margin-top: 0.32rem;
            background: var(--te-glow);
            box-shadow: 0 0 18px rgba(96, 165, 250, 0.45);
        }

        .te-status-success .te-status-dot {
            background: #34d399;
            box-shadow: 0 0 18px rgba(52, 211, 153, 0.38);
        }

        .te-status-error .te-status-dot {
            background: #fb7185;
            box-shadow: 0 0 18px rgba(251, 113, 133, 0.38);
        }

        .te-status-label {
            color: var(--te-text);
            font-size: 0.98rem;
            font-weight: 700;
        }

        .te-status-detail {
            margin-top: 0.24rem;
            color: var(--te-muted-soft);
            font-size: 0.9rem;
            line-height: 1.55;
        }

        [data-testid="stProgressBar"] > div > div > div > div {
            background: linear-gradient(135deg, var(--te-blue), var(--te-glow));
        }

        .stAlert {
            border-radius: 18px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.05);
        }

        .stCaption,
        [data-testid="stCaptionContainer"] {
            color: var(--te-muted-soft);
        }

        h1, h2, h3, h4 {
            color: var(--te-text);
            letter-spacing: -0.02em;
        }

        p, li, label {
            color: rgba(255, 255, 255, 0.92);
        }

        div[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(7, 16, 38, 0.94), rgba(7, 16, 38, 0.90)),
                rgba(7, 16, 38, 0.90);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        div[data-testid="stSidebar"] * {
            color: rgba(255, 255, 255, 0.92);
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 1.35rem;
            }

            .te-hero {
                padding: 1.8rem 1.4rem 1.6rem;
                border-radius: 24px;
            }
        }
        </style>
        <div class="te-bg-layer"></div>
        <div class="te-grid-bg"></div>
        <div class="te-orb te-orb-1"></div>
        <div class="te-orb te-orb-2"></div>
        """,
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        f"""
        <section class="te-hero">
            <h1>{escape(APP_TITLE)}</h1>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_section_heading(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="te-section-heading">
            <h2>{escape(title)}</h2>
            <p>{escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _mini_stat_card(label: str, value: str, detail: str) -> str:
    return (
        "<div class='te-mini-stat'>"
        f"<div class='te-mini-stat-label'>{escape(label)}</div>"
        f"<div class='te-mini-stat-value'>{escape(value)}</div>"
        f"<div class='te-mini-stat-detail'>{escape(detail)}</div>"
        "</div>"
    )


def _render_metric_row(cards: list[tuple[str, str, str]]) -> None:
    if not cards:
        return
    cols = st.columns(len(cards))
    for col, (label, value, detail) in zip(cols, cards):
        with col:
            st.markdown(_mini_stat_card(label, value, detail), unsafe_allow_html=True)


def _status_markup(label: str, detail: str, tone: str = "active") -> str:
    tone_class = {
        "active": "te-status-active",
        "success": "te-status-success",
        "error": "te-status-error",
    }.get(tone, "te-status-active")
    return (
        f"<div class='te-status {tone_class}'>"
        "<span class='te-status-dot'></span>"
        "<div>"
        f"<div class='te-status-label'>{escape(label)}</div>"
        f"<div class='te-status-detail'>{escape(detail)}</div>"
        "</div>"
        "</div>"
    )


def _render_status(placeholder, stage: str, label: str, tone: str = "active") -> None:
    detail = STAGE_DETAILS.get(stage, "The evaluation is progressing through the current pipeline stage.")
    placeholder.markdown(_status_markup(label, detail, tone=tone), unsafe_allow_html=True)


def _watch_item_count(report: dict[str, Any]) -> int:
    return len(report.get("additional_observation_inventory", [])) + len(report.get("low_confidence_watchlist", []))


def _strength_count(report: dict[str, Any]) -> int:
    seen_titles: set[str] = set()
    count = 0
    for item in [*report.get("top_strengths", []), *report.get("strength_inventory", [])]:
        title = str(item.get("title", "")).strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            count += 1
    return count


def _as_timestamps(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _build_markdown_report(report: dict[str, Any]) -> str:
    source = report.get("source", {})
    scorecard = report.get("scorecard", {})
    strengths: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for item in [*report.get("top_strengths", []), *report.get("strength_inventory", [])]:
        title = str(item.get("title", "")).strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        strengths.append(item)

    watch_items: list[dict[str, Any]] = []
    for item in report.get("additional_observation_inventory", []):
        watch_items.append(
            {
                "title": item.get("title", "Observation"),
                "why_watch": item.get("evidence", ""),
                "what_we_saw": item.get("evidence", ""),
                "what_to_monitor_next": item.get("suggested_response", ""),
                "timestamps": item.get("timestamps", []),
                "confidence": item.get("confidence", "medium"),
            }
        )
    watch_items.extend(report.get("low_confidence_watchlist", []))

    lines = ["# Teacher Coaching Brief", ""]
    if str(source.get("mode", "")).startswith("template_fallback"):
        lines.extend(["> Showing the structured fallback version of this brief for this run.", ""])

    lines.extend(["## Scorecard", ""])
    if isinstance(scorecard, dict) and scorecard:
        verdict = str(scorecard.get("verdict", "")).strip()
        if verdict:
            lines.append(f"- Verdict: {verdict}")
        badges = scorecard.get("badges", [])
        if badges:
            lines.extend(["", "| Area | Score |", "| --- | ---: |"])
            for item in badges[:5]:
                lines.append(f"| {item.get('label', 'Area')} | {float(item.get('score', 0.0)):.1f} |")
    else:
        lines.append("- Scorecard unavailable.")

    lines.extend(
        [
            "",
            "## At a Glance",
            "",
            str(report.get("executive_summary", "")).strip() or "No executive summary was generated.",
            "",
            "## No Material Intervention Needed",
            "",
            f"- Enabled: `{bool(report.get('no_material_intervention_needed'))}`",
        ]
    )
    reason = str(report.get("no_material_intervention_needed_reason", "")).strip()
    if reason:
        lines.append(f"- Reason: {reason}")

    actions = report.get("priority_actions", [])
    action_count = len(actions[:3])
    lines.extend(["", f"## {'Top Action' if action_count == 1 else f'Top {max(action_count, 1)} Actions'}", ""])
    if actions:
        for index, action in enumerate(actions[:3], start=1):
            timestamps = ", ".join(_as_timestamps(action.get("timestamps")))
            lines.extend(
                [
                    f"### {index}. {action.get('title', 'Untitled action')}",
                    "",
                    f"- Why it matters: {action.get('why_it_matters', '')}",
                    f"- What we saw: {action.get('what_we_saw', '')}",
                    f"- What to try next: {action.get('what_to_try_next', '')}",
                    f"- Review at: {timestamps or 'n/a'}",
                    f"- Confidence: {action.get('confidence', 'n/a')}",
                    "",
                ]
            )
    else:
        lines.append("- No priority actions were generated for this run.")

    lines.extend(["## Strengths", ""])
    if strengths:
        for item in strengths:
            timestamps = ", ".join(_as_timestamps(item.get("timestamps")))
            lines.extend(
                [
                    f"### {item.get('title', 'Untitled strength')}",
                    "",
                    f"- Evidence: {item.get('evidence', '')}",
                    f"- What to repeat: {item.get('what_to_repeat', '')}",
                    f"- Review at: {timestamps or 'n/a'}",
                    f"- Confidence: {item.get('confidence', 'n/a')}",
                    "",
                ]
            )
    else:
        lines.append("- No dominant strengths were generated for this run.")

    lines.extend(["## Watch Items (low confidence)", ""])
    if watch_items:
        for item in watch_items:
            timestamps = ", ".join(_as_timestamps(item.get("timestamps")))
            lines.extend(
                [
                    f"### {item.get('title', 'Untitled watch item')}",
                    "",
                    f"- Why watch: {item.get('why_watch', '')}",
                    f"- What we saw: {item.get('what_we_saw', '')}",
                    f"- What to monitor next: {item.get('what_to_monitor_next', '')}",
                    f"- Review at: {timestamps or 'n/a'}",
                    f"- Confidence: {item.get('confidence', 'n/a')}",
                    "",
                ]
            )
    else:
        lines.append("- No low-confidence watch items were generated.")

    if report.get("evidence_moments"):
        lines.extend(["## Moment-by-Moment Evidence", ""])
        for moment in report["evidence_moments"][:6]:
            lines.extend(
                [
                    f"### {moment.get('timestamp', 'n/a')} - {moment.get('headline', 'Evidence moment')}",
                    "",
                    f"- Observed behavior: {moment.get('observed_behavior', '')}",
                    f"- Metric evidence: {moment.get('metric_evidence', '')}",
                    f"- Semantic interpretation: {moment.get('semantic_interpretation') or moment.get('qwen_interpretation', '')}",
                    f"- Coaching implication: {moment.get('coaching_implication', '')}",
                    "",
                ]
            )

    if report.get("confidence_notes"):
        lines.extend(["## Reliability Notes", ""])
        for note in report["confidence_notes"]:
            lines.append(f"- {note}")

    lines.extend(
        [
        ]
    )

    return "\n".join(lines).strip() + "\n"


def _render_downloads_from_report(report: dict[str, Any]) -> None:
    st.download_button(
        "Download JSON",
        data=json.dumps(report, indent=2, ensure_ascii=True),
        file_name="teacher_coaching_report.json",
        mime="application/json",
        use_container_width=True,
    )
    st.download_button(
        "Download Markdown",
        data=_build_markdown_report(report),
        file_name="teacher_coaching_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
    pdf_path = report.get("_qa_pdf_path")

    if pdf_path and Path(str(pdf_path)).exists():
        pdf_file = Path(str(pdf_path))
        st.download_button(
            "Download PDF",
            data=pdf_file.read_bytes(),
            file_name=pdf_file.name,
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.button("PDF unavailable", disabled=True, use_container_width=True)


def _report_downloads(report_artifacts: dict[str, Any]) -> None:
    report_json_path = Path(report_artifacts["report_json"])
    report_md_path = Path(report_artifacts["report_md"])
    pdf_path = Path(report_artifacts["report_pdf"])

    if report_json_path.exists():
        st.download_button(
            "Download JSON",
            data=report_json_path.read_text(encoding="utf-8"),
            file_name=report_json_path.name,
            mime="application/json",
            use_container_width=True,
        )
    if report_md_path.exists():
        st.download_button(
            "Download Markdown",
            data=report_md_path.read_text(encoding="utf-8"),
            file_name=report_md_path.name,
            mime="text/markdown",
            use_container_width=True,
        )

    if pdf_path.exists():
        st.download_button(
            "Download PDF",
            data=pdf_path.read_bytes(),
            file_name=pdf_path.name,
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.button("PDF unavailable", disabled=True, use_container_width=True)


_SCORECARD_BRIEF: dict[str, str] = {
    "Posture": "Upright, open stance and audience-facing orientation across the clip.",
    "Eye-contact distribution": "Evenness of head-orientation across left, center, and right room zones.",
    "Gesture smoothness": "Fluidity of hand/arm trajectories; penalises erratic or oversized motion.",
    "Positive affect": "Visible smile activity, open-palm gestures, and facial expressiveness.",
    "Stage usage": "Stage area covered and time distributed across zones; penalises prolonged anchoring.",
}


def _score_dot_class(score: float) -> str:
    if score >= 75:
        return "te-score-dot-green"
    if score >= 50:
        return "te-score-dot-amber"
    return "te-score-dot-red"


def _render_scorecard(report: dict[str, Any], summary: dict[str, Any] | None = None) -> None:
    scorecard = report.get("scorecard", {})
    if not scorecard and summary is not None:
        scorecard = {
            "overall_score": summary["heuristic_nonverbal_score"],
            "verdict": "See the detailed coaching sections below.",
            "badges": [
                {"label": "Posture", "score": summary["posture_stability_score"]},
                {"label": "Eye-contact distribution", "score": summary["eye_contact_distribution_score"]},
                {"label": "Gesture smoothness", "score": summary["gesture_smoothness_score"]},
                {"label": "Positive affect", "score": summary["positive_affect_score"]},
                {"label": "Stage usage", "score": summary.get("stage_usage_score", 0.0)},
            ],
        }
    badges = scorecard.get("badges", [])
    if not badges:
        return
    cards_html = ""
    for item in badges[:5]:
        label = str(item.get("label", ""))
        score = float(item.get("score", 0.0))
        dot = _score_dot_class(score)
        desc = _SCORECARD_BRIEF.get(label, "")
        cards_html += (
            "<div class='te-score-card'>"
            "<div class='te-score-header'>"
            f"<span class='te-score-label'>{escape(label)}</span>"
            f"<span class='te-score-dot {dot}'></span>"
            "</div>"
            f"<div class='te-score-number'>{score:.1f}</div>"
            f"<div class='te-score-desc'>{escape(desc)}</div>"
            "</div>"
        )
    st.markdown(f"<div class='te-scorecard-grid'>{cards_html}</div>", unsafe_allow_html=True)


def _render_priority_actions(report: dict[str, Any]) -> None:
    action_count = len(report.get("priority_actions", [])[:3])
    st.subheader("Top Action" if action_count == 1 else f"Top {max(action_count, 1)} Actions")
    actions = report.get("priority_actions", [])
    if not actions:
        st.info("No priority actions were generated for this run.")
        return
    for index, action in enumerate(actions[:3], start=1):
        timestamps = action.get("timestamps", [])
        if isinstance(timestamps, str):
            timestamps = [timestamps]
        with st.container(border=True):
            st.markdown(f"**{index}. {action['title']}**")
            st.write(action["why_it_matters"])
            st.caption(f"Review at: {', '.join(timestamps)} | Confidence: {action['confidence']}")
            st.markdown(f"**What we saw:** {action['what_we_saw']}")
            st.markdown(f"**What to try next:** {action['what_to_try_next']}")


def _render_strengths(report: dict[str, Any]) -> None:
    st.subheader("Strengths")
    strengths = []
    seen_titles: set[str] = set()
    for item in [*report.get("top_strengths", []), *report.get("strength_inventory", [])]:
        title = str(item.get("title", "")).strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        strengths.append(item)
    if not strengths:
        st.info("No dominant strength signals were extracted for this run.")
        return
    for item in strengths:
        timestamps = item.get("timestamps", [])
        if isinstance(timestamps, str):
            timestamps = [timestamps]
        st.markdown(
            f"- **{item['title']}**: {item['evidence']} "
            f"Review at {', '.join(timestamps)}. Confidence: {item['confidence']}."
        )


def _render_no_material_intervention(report: dict[str, Any]) -> None:
    st.subheader("No Material Intervention Needed")
    reason = str(report.get("no_material_intervention_needed_reason", "")).strip()
    if report.get("no_material_intervention_needed"):
        st.success(reason or "No material intervention was needed from this clip.")
        return
    if reason:
        st.info(reason)
    else:
        st.write("This report still recommends follow-up coaching actions.")

def _render_watchlist(report: dict[str, Any]) -> None:
    st.subheader("Watch Items (low confidence)")
    items = []
    for item in report.get("additional_observation_inventory", []):
        items.append(
            {
                "title": item.get("title", "Observation"),
                "why_watch": item.get("evidence", ""),
                "what_we_saw": item.get("evidence", ""),
                "what_to_monitor_next": item.get("suggested_response", ""),
                "timestamps": item.get("timestamps", []),
                "confidence": item.get("confidence", "medium"),
            }
        )
    items.extend(report.get("low_confidence_watchlist", []))
    if not items:
        st.info("No watchlist items were generated for this run.")
        return
    for item in items:
        timestamps = _as_timestamps(item.get("timestamps"))
        with st.container(border=True):
            st.markdown(f"**{item.get('title', 'Untitled watch item')}**")
            st.caption(
                f"Review at: {', '.join(timestamps) if timestamps else 'n/a'} | "
                f"Confidence: {item.get('confidence', 'n/a')}"
            )
            st.markdown(f"**Why watch:** {item.get('why_watch', '')}")
            st.markdown(f"**What we saw:** {item.get('what_we_saw', '')}")
            st.markdown(f"**What to monitor next:** {item.get('what_to_monitor_next', '')}")



def _clean_interpretation(text: str) -> str:
    """Strip internal model-name prefixes from semantic interpretation text."""
    for prefix in ("Qwen sees ", "Qwen: ", "The model sees ", "VLM: "):
        if text.startswith(prefix):
            text = text[len(prefix):]
            text = text[:1].upper() + text[1:]
    return text


def _render_moments(report: dict[str, Any]) -> None:
    moments = report.get("evidence_moments", [])
    if not moments:
        return
    st.subheader("Key Moments from This Session")
    for moment in moments[:6]:
        with st.container(border=True):
            st.markdown(f"**{moment['timestamp']} — {moment['headline']}**")
            st.markdown(f"- Observed: {moment['observed_behavior']}")
            st.markdown(f"- Metrics: {moment['metric_evidence']}")
            interpretation = moment.get("semantic_interpretation") or moment.get("qwen_interpretation", "")
            st.markdown(f"- Interpretation: {_clean_interpretation(str(interpretation))}")
            st.markdown(f"- Take-away: {moment['coaching_implication']}")


def _load_qa_report() -> dict[str, Any] | None:
    report_json = os.getenv(QA_REPORT_JSON_ENV)
    if not report_json:
        return None

    report_path = Path(report_json)
    if not report_path.exists():
        raise FileNotFoundError(f"QA report JSON not found: {report_path}")

    report = _load_json(report_path)
    if report is None:
        raise RuntimeError(f"Could not parse QA report JSON: {report_path}")

    pdf_path = os.getenv(QA_REPORT_PDF_ENV)
    if pdf_path:
        report["_qa_pdf_path"] = pdf_path
    report["_qa_report_path"] = str(report_path)
    return report


def _render_upload_metadata(video_info: dict[str, float]) -> None:
    _render_metric_row(
        [
            ("Duration", f"{video_info['duration_sec']:.1f}s", "Accepted clips are capped at five minutes."),
            ("Frame rate", f"{video_info['fps']:.2f} fps", "Used to size the extracted analysis segment."),
            ("Resolution", f"{int(video_info['width'])} × {int(video_info['height'])}", "Source video dimensions."),
            ("Frames", f"{int(video_info['frames'])}", "Raw frame count before sampling."),
        ]
    )


def _render_report_overview(report: dict[str, Any], summary: dict[str, Any], qc: dict[str, Any]) -> None:
    intervention_state = "Maintenance brief" if report.get("no_material_intervention_needed") else "Action-focused brief"
    _render_metric_row(
        [
            ("Brief status", intervention_state, "How strongly this clip calls for corrective coaching."),
            ("Priority actions", str(len(report.get("priority_actions", [])[:3])), "Top actions surfaced from the current clip."),
            ("Stage usage", f"{summary['stage_usage_score']:.1f}", "Room movement and stage-coverage signal."),
            ("Face coverage", f"{qc['face_coverage']:.2f}", "Quality-control reliability for face-visible cues."),
        ]
    )


def _render_qa_overview(report: dict[str, Any]) -> None:
    intervention_state = "Maintenance brief" if report.get("no_material_intervention_needed") else "Action-focused brief"
    _render_metric_row(
        [
            ("Brief status", intervention_state, "Current coaching posture of the preview brief."),
            ("Strength signals", str(_strength_count(report)), "Distinct strengths surfaced in the brief."),
            ("Watch items", str(_watch_item_count(report)), "Low-confidence observations kept for monitoring."),
            ("Priority actions", str(len(report.get("priority_actions", [])[:3])), "Actions surfaced in the current preview."),
        ]
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    _ensure_dirs()
    _inject_theme()

    qa_report = _load_qa_report()
    _render_hero()
    if qa_report is not None:
        st.sidebar.info("QA fixture mode is active.")
        with st.container(border=True):
            _render_section_heading(
                "Fixture preview",
                "This static QA path uses the same top-level shell as a live run so layout and hierarchy stay easy to review.",
            )
            _render_qa_overview(qa_report)
        st.subheader("Scorecard")
        _render_scorecard(qa_report)
        st.subheader("At a Glance")
        st.write(qa_report.get("executive_summary", "No executive summary was generated."))
        _render_no_material_intervention(qa_report)
        _render_priority_actions(qa_report)
        _render_strengths(qa_report)
        _render_watchlist(qa_report)
        _render_moments(qa_report)
        st.subheader("Downloads")
        _render_downloads_from_report(qa_report)
        return

    with st.container(border=True):
        _render_section_heading(
            "Upload lecture clip",
            "Choose a lecture video up to five minutes long. The app will run the nonverbal evaluation pipeline and produce a coaching brief with downloadable artifacts.",
        )
        upload = st.file_uploader("Upload a lecture video", type=["mp4", "mov", "m4v", "avi"])
        if upload is None:
            st.markdown(
                "<div class='te-inline-note'>Supported formats: MP4, MOV, M4V, and AVI. "
                "The current app is optimized for short classroom or lecture excerpts.</div>",
                unsafe_allow_html=True,
            )

    if upload is None:
        return

    uploaded_path = _save_upload(upload)
    video_info = _video_info(uploaded_path)

    with st.container(border=True):
        _render_section_heading(
            "Clip details",
            "The uploaded clip has been parsed successfully. These values are surfaced early so you can quickly confirm the input before spending inference time.",
        )
        _render_upload_metadata(video_info)

    if video_info["duration_sec"] > MAX_UPLOAD_DURATION_SEC:
        st.error("This frontend accepts videos up to 5 minutes long.")
        return

    if not st.button("Generate report", type="primary", use_container_width=True):
        return

    with st.container(border=True):
        _render_section_heading(
            "Analysis status",
            "Live progress appears here while the landmark pipeline, semantic layer, and coaching brief are being prepared.",
        )
        stage_placeholder = st.empty()
        progress_bar = st.progress(0.0, text="Starting evaluation")

    ordered_stages = [
        "start",
        "extract_segment_started",
        "extract_segment_finished",
        "evaluate_full_clip_started",
        "evaluate_full_clip_finished",
        "keyframe_summary_started",
        "keyframe_summary_finished",
        "semantic_started",
        "semantic_finished",
        "window_aggregation_started",
        "window_aggregation_finished",
        "window_figures_started",
        "window_figures_finished",
        "coaching_started",
        "coaching_finished",
        "finished",
    ]
    stage_to_progress = {stage: index / (len(ordered_stages) - 1) for index, stage in enumerate(ordered_stages)}

    def progress_callback(stage: str, payload: dict[str, Any]) -> None:
        label = STAGE_LABELS.get(stage, stage.replace("_", " ").title())
        progress_bar.progress(stage_to_progress.get(stage, 0.0), text=label)
        _render_status(stage_placeholder, stage, label, tone="active")

    try:
        _render_status(stage_placeholder, "start", STAGE_LABELS["start"], tone="active")
        results = run_teacher_evaluation(
            video=uploaded_path,
            output_root=RUN_ROOT,
            start_sec=0.0,
            duration_sec=video_info["duration_sec"],
            analysis_fps=12.0,
            window_sec=15.0,
            window_step_sec=15.0,
            enable_semantic=True,
            disable_qwen=False,
            qwen_model=_semantic_model_name(),
            enable_coaching=True,
            coach_model=os.getenv(COACH_MODEL_ENV, DEFAULT_GEMINI_MODEL),
            coach_top_actions=3,
            coach_fallback_template_only=False,
            progress_callback=progress_callback,
        )
    except Exception as exc:
        progress_bar.empty()
        _render_status(stage_placeholder, "finished", "Evaluation failed", tone="error")
        st.exception(exc)
        return

    progress_bar.progress(1.0, text="Evaluation complete")
    _render_status(stage_placeholder, "finished", "Evaluation complete", tone="success")

    report_artifacts = results["artifacts"].get("coaching")
    report = _load_json(report_artifacts["report_json"]) if report_artifacts else None
    if report is None:
        st.error("The coaching report could not be loaded from the run artifacts.")
        return

    summary = results["summary"]["scores"]
    qc = results["summary"]["quality_control"]

    st.subheader("Scorecard")
    _render_scorecard(report, summary)
    st.subheader("At a Glance")
    st.write(report["executive_summary"])

    _render_no_material_intervention(report)
    _render_priority_actions(report)
    _render_strengths(report)
    _render_watchlist(report)
    _render_moments(report)

    st.subheader("Downloads")
    _report_downloads(report_artifacts)


if __name__ == "__main__":
    main()
