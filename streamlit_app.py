from __future__ import annotations

import json
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


def _report_downloads(report_artifacts: dict[str, Any]) -> None:
    json_path = Path(report_artifacts["report_json"])
    md_path = Path(report_artifacts["report_md"])
    pdf_path = Path(report_artifacts["report_pdf"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download JSON",
            data=json_path.read_bytes(),
            file_name=json_path.name,
            mime="application/json",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download Markdown",
            data=md_path.read_bytes(),
            file_name=md_path.name,
            mime="text/markdown",
            use_container_width=True,
        )
    with col3:
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


def _render_reliability(report: dict[str, Any]) -> None:
    st.subheader("Reliability Notes")
    notes = report.get("confidence_notes", [])
    if not notes:
        st.write("No extra reliability notes were generated.")
        return
    for note in notes:
        st.markdown(f"- {note}")


def _render_moments(report: dict[str, Any]) -> None:
    moments = report.get("evidence_moments", [])
    if not moments:
        return
    st.subheader("Moment-by-Moment Evidence")
    for moment in moments[:6]:
        with st.container(border=True):
            st.markdown(f"**{moment['timestamp']} - {moment['headline']}**")
            st.markdown(f"- Observed behavior: {moment['observed_behavior']}")
            st.markdown(f"- Metric evidence: {moment['metric_evidence']}")
            st.markdown(f"- Qwen interpretation: {moment['qwen_interpretation']}")
            st.markdown(f"- Coaching implication: {moment['coaching_implication']}")


def _render_sidebar_controls() -> dict[str, Any]:
    st.sidebar.header("Run Settings")
    enable_semantic = st.sidebar.checkbox("Enable Qwen semantic review", value=False)
    coach_template_only = st.sidebar.checkbox("Template-only coaching", value=True)
    coach_top_actions = st.sidebar.slider("Priority actions", min_value=1, max_value=3, value=3)
    return {
        "enable_semantic": enable_semantic,
        "coach_template_only": coach_template_only,
        "coach_top_actions": coach_top_actions,
    }


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    _ensure_dirs()

    st.title("TeacherEvaluation")
    st.write(
        "Upload a lecture video up to 5 minutes long. The app runs the nonverbal evaluation pipeline and "
        "returns a teacher-facing coaching brief with downloads for JSON, Markdown, and PDF."
    )

    controls = _render_sidebar_controls()
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
            enable_semantic=controls["enable_semantic"],
            disable_qwen=not controls["enable_semantic"],
            disable_sam2=True,
            enable_coaching=True,
            coach_top_actions=controls["coach_top_actions"],
            coach_fallback_template_only=controls["coach_template_only"],
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

    _render_priority_actions(report)
    _render_strengths(report)
    _render_moments(report)
    _render_reliability(report)

    st.subheader("Downloads")
    _report_downloads(report_artifacts)

    with st.expander("Technical references"):
        st.markdown(f"- Run directory: `{results['run_dir']}`")
        st.markdown(f"- Technical summary: `{results['artifacts']['summary_md']}`")
        st.markdown(f"- Window summary: `{results['window_md']}`")
        if results["artifacts"].get("semantic"):
            st.markdown(f"- Semantic summary: `{results['artifacts']['semantic']['summary_md']}`")
        st.markdown(f"- Coaching evidence: `{report_artifacts['evidence_json']}`")


if __name__ == "__main__":
    main()
