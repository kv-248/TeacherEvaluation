from __future__ import annotations

import json
import os
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import cv2
import streamlit as st

from nonverbal_eval.app_service import run_teacher_evaluation


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


def _semantic_model_name(default: str = "gemini-2.5-flash") -> str:
    return (
        os.getenv(SEMANTIC_MODEL_ENV)
        or os.getenv(LEGACY_SEMANTIC_MODEL_ENV)
        or default
    )


def _as_timestamps(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _build_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Teacher Coaching Brief",
        "",
        "## At a Glance",
        "",
        str(report.get("executive_summary", "")).strip() or "No executive summary was generated.",
        "",
        "## No Material Intervention Needed",
        "",
        f"- Enabled: `{bool(report.get('no_material_intervention_needed'))}`",
    ]
    reason = str(report.get("no_material_intervention_needed_reason", "")).strip()
    if reason:
        lines.append(f"- Reason: {reason}")

    lines.extend(["", "## Top 3 Actions for the Next Lecture", ""])
    actions = report.get("priority_actions", [])
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

    lines.extend(["## Strengths to Preserve", ""])
    for item in report.get("top_strengths", []):
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

    lines.extend(["## Strength Inventory", ""])
    if report.get("strength_inventory"):
        for item in report["strength_inventory"]:
            timestamps = ", ".join(_as_timestamps(item.get("timestamps")))
            lines.extend(
                [
                    f"- **{item.get('title', 'Untitled strength')}**: {item.get('evidence', '')}",
                    f"  - What to repeat: {item.get('what_to_repeat', '')}",
                    f"  - Review at: {timestamps or 'n/a'}",
                    f"  - Confidence: {item.get('confidence', 'n/a')}",
                    "",
                ]
            )
    else:
        lines.append("- No additional strength inventory was generated.")

    lines.extend(["## Additional Observation Inventory", ""])
    if report.get("additional_observation_inventory"):
        for item in report["additional_observation_inventory"]:
            timestamps = ", ".join(_as_timestamps(item.get("timestamps")))
            lines.extend(
                [
                    f"### {item.get('title', 'Untitled observation')}",
                    "",
                    f"- Kind: {item.get('kind', 'observation')}",
                    f"- Evidence: {item.get('evidence', '')}",
                    f"- Suggested response: {item.get('suggested_response', '')}",
                    f"- Review at: {timestamps or 'n/a'}",
                    f"- Confidence: {item.get('confidence', 'n/a')}",
                    "",
                ]
            )
    else:
        lines.append("- No additional observation inventory was generated.")

    lines.extend(["## Low-Confidence Watchlist", ""])
    if report.get("low_confidence_watchlist"):
        for item in report["low_confidence_watchlist"]:
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
        lines.append("- No low-confidence watchlist items were generated.")

    if report.get("evidence_moments"):
        lines.extend(["## Moment-by-Moment Evidence", ""])
        for moment in report["evidence_moments"][:6]:
            lines.extend(
                [
                    f"### {moment.get('timestamp', 'n/a')} - {moment.get('headline', 'Evidence moment')}",
                    "",
                    f"- Observed behavior: {moment.get('observed_behavior', '')}",
                    f"- Metric evidence: {moment.get('metric_evidence', '')}",
                    f"- Semantic interpretation: {moment.get('qwen_interpretation', '')}",
                    f"- Coaching implication: {moment.get('coaching_implication', '')}",
                    "",
                ]
            )

    if report.get("confidence_notes"):
        lines.extend(["## Reliability Notes", ""])
        for note in report["confidence_notes"]:
            lines.append(f"- {note}")

    return "\n".join(lines).strip() + "\n"


def _render_downloads_from_report(report: dict[str, Any]) -> None:
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
    pdf_path = Path(report_artifacts["report_pdf"])

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


def _render_priority_actions(report: dict[str, Any]) -> None:
    st.subheader("Top 3 Actions for the Next Lecture")
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
    st.subheader("Strengths to Preserve")
    strengths = report.get("top_strengths", [])
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


def _render_strength_inventory(report: dict[str, Any]) -> None:
    st.subheader("Strength Inventory")
    strengths = report.get("strength_inventory", [])
    if not strengths:
        st.info("No broader strength inventory was generated for this run.")
        return
    for item in strengths:
        timestamps = _as_timestamps(item.get("timestamps"))
        with st.container(border=True):
            st.markdown(f"**{item.get('title', 'Untitled strength')}**")
            st.write(item.get("evidence", ""))
            st.caption(
                f"Review at: {', '.join(timestamps) if timestamps else 'n/a'} | "
                f"Confidence: {item.get('confidence', 'n/a')}"
            )
            st.markdown(f"**What to repeat:** {item.get('what_to_repeat', '')}")


def _render_additional_observation_inventory(report: dict[str, Any]) -> None:
    st.subheader("Additional Observation Inventory")
    items = report.get("additional_observation_inventory", [])
    if not items:
        st.info("No additional observations were surfaced for this run.")
        return
    for item in items:
        timestamps = _as_timestamps(item.get("timestamps"))
        with st.container(border=True):
            st.markdown(f"**{item.get('title', 'Untitled observation')}**")
            st.caption(
                f"Kind: {item.get('kind', 'observation')} | "
                f"Review at: {', '.join(timestamps) if timestamps else 'n/a'} | "
                f"Confidence: {item.get('confidence', 'n/a')}"
            )
            st.markdown(f"**Evidence:** {item.get('evidence', '')}")
            st.markdown(f"**Suggested response:** {item.get('suggested_response', '')}")


def _render_watchlist(report: dict[str, Any]) -> None:
    st.subheader("Low-Confidence Watchlist")
    items = report.get("low_confidence_watchlist", [])
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


def _render_reliability(report: dict[str, Any]) -> None:
    st.subheader("Reliability Notes")
    notes = report.get("confidence_notes", [])
    if not notes:
        st.write("No extra reliability notes were generated.")
        return
    for note in notes:
        st.markdown(f"- {note}")


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
            st.markdown(f"- Interpretation: {_clean_interpretation(moment['qwen_interpretation'])}")
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


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    _ensure_dirs()

    st.title("TeacherEvaluation")
    st.write(
        "Upload a lecture video up to 5 minutes long. The app runs the nonverbal evaluation pipeline and "
        "returns a teacher-facing coaching brief with downloads for JSON, Markdown, and PDF."
    )

    qa_report = _load_qa_report()
    if qa_report is not None:
        st.sidebar.info("QA fixture mode is active.")
        st.subheader("At a Glance")
        st.write(qa_report.get("executive_summary", "No executive summary was generated."))
        _render_no_material_intervention(qa_report)
        _render_priority_actions(qa_report)
        _render_strengths(qa_report)
        _render_strength_inventory(qa_report)
        _render_additional_observation_inventory(qa_report)
        _render_watchlist(qa_report)
        _render_moments(qa_report)
        _render_reliability(qa_report)
        st.subheader("Downloads")
        _render_downloads_from_report(qa_report)
        return

    upload = st.file_uploader("Upload a lecture video", type=["mp4", "mov", "m4v", "avi"])

    if upload is None:
        st.info("Choose a video file to begin.")
        return

    uploaded_path = _save_upload(upload)
    video_info = _video_info(uploaded_path)
    st.caption(
        f"Detected video: {video_info['duration_sec']:.1f}s, {video_info['fps']:.2f} fps, "
        f"{video_info['width']}x{video_info['height']}"
    )

    if video_info["duration_sec"] > MAX_UPLOAD_DURATION_SEC:
        st.error("This frontend accepts videos up to 5 minutes long.")
        return

    if not st.button("Generate report", type="primary"):
        return

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
        stage_placeholder.info(label)

    try:
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
            coach_model=os.getenv(COACH_MODEL_ENV, "gemini-2.5-flash"),
            coach_top_actions=3,
            coach_fallback_template_only=False,
            progress_callback=progress_callback,
        )
    except Exception as exc:
        progress_bar.empty()
        stage_placeholder.empty()
        st.exception(exc)
        return

    progress_bar.progress(1.0, text="Evaluation complete")
    stage_placeholder.success("Evaluation complete")

    report_artifacts = results["artifacts"].get("coaching")
    report = _load_json(report_artifacts["report_json"]) if report_artifacts else None
    if report is None:
        st.error("The coaching report could not be loaded from the run artifacts.")
        return

    summary = results["summary"]["scores"]
    qc = results["summary"]["quality_control"]

    st.subheader("At a Glance")
    st.write(report["executive_summary"])
    st.caption(
        f"Overall score: {summary['heuristic_nonverbal_score']:.1f} | "
        f"Eye-contact distribution: {summary['eye_contact_distribution_score']:.1f} | "
        f"Confidence/presence: {summary['confidence_presence_score']:.1f} | "
        f"Face coverage: {qc['face_coverage']:.2f}"
    )

    _render_no_material_intervention(report)
    _render_priority_actions(report)
    _render_strengths(report)
    _render_strength_inventory(report)
    _render_additional_observation_inventory(report)
    _render_watchlist(report)
    _render_moments(report)
    _render_reliability(report)

    st.subheader("Downloads")
    _report_downloads(report_artifacts)


if __name__ == "__main__":
    main()
