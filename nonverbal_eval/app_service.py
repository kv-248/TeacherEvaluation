from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .coaching import CoachingConfig, run_coaching_report
from .pipeline import (
    ExperimentArtifacts,
    ExperimentConfig,
    annotate_keyframe,
    evaluate_clip,
    extract_frame,
    log_event,
    save_summary_markdown,
    summarize_frame_metrics,
)
from .semantic import SemanticConfig, run_semantic_extensions


ProgressCallback = Callable[[str, dict[str, Any]], None]


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _markdown_table(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for value in row.tolist():
            if isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _emit(progress_callback: ProgressCallback | None, stage: str, **payload: Any) -> None:
    if progress_callback is not None:
        progress_callback(stage, payload)


def _video_info(video_path: Path) -> dict[str, float]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {
        "fps": fps,
        "frames": frames,
        "duration_sec": frames / fps if fps else 0.0,
        "width": width,
        "height": height,
    }


def build_long_run_artifacts(output_root: Path) -> ExperimentArtifacts:
    run_dir = output_root / f"run_{_timestamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return ExperimentArtifacts(
        root_dir=run_dir,
        clip_path=run_dir / "full_segment_reference.mp4",
        keyframe_path=run_dir / "keyframe_mid.jpg",
        annotated_keyframe_path=run_dir / "keyframe_mid_annotated.jpg",
        debug_video_path=run_dir / "debug_overlay_full.mp4",
        debug_contact_sheet_path=run_dir / "debug_contact_sheet_full.jpg",
        per_frame_csv_path=run_dir / "per_frame_metrics_full.csv",
        summary_json_path=run_dir / "summary_full.json",
        summary_md_path=run_dir / "summary_full.md",
        timeline_plot_path=run_dir / "metric_timelines_full.png",
        events_jsonl_path=run_dir / "events.jsonl",
    )


def _extract_segment_with_fps(
    video_path: Path,
    output_path: Path,
    start_sec: float,
    duration_sec: float,
    target_fps: float,
    events_path: Path,
) -> dict[str, float | str]:
    video_info = _video_info(video_path)
    source_fps = float(video_info["fps"])
    effective_fps = float(target_fps) if target_fps > 0 else source_fps
    end_sec = min(start_sec + duration_sec, float(video_info["duration_sec"]))

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video for extraction: {video_path}")
    cap.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000.0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        effective_fps,
        (int(video_info["width"]), int(video_info["height"])),
    )

    next_write_sec = start_sec
    tolerance = 0.5 / max(source_fps, 1.0)
    frames_written = 0

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        now_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if now_sec > end_sec + tolerance:
            break
        if now_sec + tolerance < next_write_sec:
            continue
        writer.write(frame)
        frames_written += 1
        next_write_sec += 1.0 / effective_fps

    cap.release()
    writer.release()

    clip_info = {
        "source_video": str(video_path),
        "clip_video": str(output_path),
        "start_sec": start_sec,
        "duration_sec_requested": duration_sec,
        "duration_sec_actual": frames_written / effective_fps if effective_fps else 0.0,
        "fps": effective_fps,
        "source_fps": source_fps,
        "width": int(video_info["width"]),
        "height": int(video_info["height"]),
        "frames_written": frames_written,
    }
    log_event(events_path, "segment_extracted_with_fps", **clip_info)
    return clip_info


def _window_slices(clip_duration_sec: float, window_sec: float, step_sec: float) -> list[tuple[float, float]]:
    starts: list[tuple[float, float]] = []
    start = 0.0
    while start < clip_duration_sec - 1e-6:
        end = min(start + window_sec, clip_duration_sec)
        if end - start >= min(window_sec * 0.4, 5.0):
            starts.append((start, end))
        start += step_sec
    return starts


def _save_window_figures(df: pd.DataFrame, score_path: Path, risk_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df["window_start_sec"], df["heuristic_nonverbal_score"], label="Overall", color="#1d3557", linewidth=2.4)
    ax.plot(df["window_start_sec"], df["eye_contact_distribution_score"], label="Eye contact", color="#2a9d8f", linewidth=2.0)
    ax.plot(df["window_start_sec"], df["confidence_presence_score"], label="Confidence", color="#f4a261", linewidth=2.0)
    ax.plot(df["window_start_sec"], df["natural_movement_score"], label="Natural movement", color="#e76f51", linewidth=2.0)
    ax.set_xlim(df["window_start_sec"].min(), df["window_start_sec"].max())
    ax.set_ylim(0, 100)
    ax.set_xlabel("Window start (s)")
    ax.set_ylabel("Score")
    ax.set_title("Long-run score trends across the lecture")
    ax.grid(alpha=0.25, linestyle="--")
    ax.legend(loc="lower left", ncol=2)
    fig.tight_layout()
    fig.savefig(score_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 7))
    width = max(float(df["window_duration_sec"].median()) * 0.22, 1.8)
    ax.bar(df["window_start_sec"] - width, df["static_behavior_risk"], width=width, label="Static", color="#457b9d")
    ax.bar(df["window_start_sec"], df["excessive_animation_risk"], width=width, label="Excessive", color="#d62828")
    ax.bar(df["window_start_sec"] + width, df["rigidity_risk"], width=width, label="Rigidity", color="#6a4c93")
    ax.set_xlim(df["window_start_sec"].min() - width * 2, df["window_start_sec"].max() + width * 2)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Window start (s)")
    ax.set_ylabel("Risk score")
    ax.set_title("Long-run risk trends across the lecture")
    ax.grid(alpha=0.25, linestyle="--", axis="y")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(risk_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_window_markdown(
    output_path: Path,
    video_path: Path,
    clip_duration_sec: float,
    window_sec: float,
    step_sec: float,
    window_df: pd.DataFrame,
) -> None:
    best = window_df.sort_values("heuristic_nonverbal_score", ascending=False).iloc[0]
    worst = window_df.sort_values("heuristic_nonverbal_score", ascending=True).iloc[0]
    md = "# Long-Run Window Summary\n\n"
    md += f"- Source video: `{video_path}`\n"
    md += f"- Full analyzed duration: `{clip_duration_sec:.2f}s`\n"
    md += f"- Window size: `{window_sec:.1f}s`\n"
    md += f"- Step size: `{step_sec:.1f}s`\n"
    md += f"- Best window: `{best['window_start_sec']:.0f}s-{best['window_end_sec']:.0f}s` with overall `{best['heuristic_nonverbal_score']:.1f}`\n"
    md += f"- Weakest window: `{worst['window_start_sec']:.0f}s-{worst['window_end_sec']:.0f}s` with overall `{worst['heuristic_nonverbal_score']:.1f}`\n\n"
    md += "## Window Table\n\n"
    table_df = window_df[
        [
            "window_start_sec",
            "window_end_sec",
            "natural_movement_score",
            "positive_affect_score",
            "confidence_presence_score",
            "eye_contact_distribution_score",
            "alertness_score",
            "static_behavior_risk",
            "excessive_animation_risk",
            "heuristic_nonverbal_score",
        ]
    ].copy()
    md += _markdown_table(table_df)
    md += "\n"
    output_path.write_text(md, encoding="utf-8")


def run_teacher_evaluation(
    *,
    video: Path,
    output_root: Path,
    start_sec: float = 0.0,
    duration_sec: float = 0.0,
    analysis_fps: float = 12.0,
    window_sec: float = 15.0,
    window_step_sec: float = 15.0,
    keyframe_offset_sec: float = -1.0,
    enable_semantic: bool = False,
    semantic_sample_interval_sec: float = 6.0,
    semantic_max_samples: int = 8,
    disable_qwen: bool = False,
    qwen_model: str = "Qwen/Qwen2.5-VL-7B-Instruct",
    qwen_device: str = "cuda:0",
    qwen_device_map: str | None = None,
    qwen_dtype: str = "bfloat16",
    qwen_max_new_tokens: int = 180,
    qwen_temperature: float = 0.1,
    disable_sam2: bool = True,
    sam2_model_cfg: str | None = None,
    sam2_checkpoint: Path | None = None,
    sam2_device: str = "cuda:1",
    enable_coaching: bool = False,
    coach_model: str = "Qwen/Qwen2.5-3B-Instruct",
    coach_device: str = "cuda:1",
    coach_max_windows: int = 6,
    coach_top_actions: int = 3,
    coach_render_pdf: bool = True,
    coach_fallback_template_only: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    video_info = _video_info(video)
    max_duration_sec = max(float(video_info["duration_sec"]) - start_sec, 0.0)
    clip_duration_sec = max_duration_sec if duration_sec <= 0 else min(duration_sec, max_duration_sec)
    if clip_duration_sec <= 0:
        raise RuntimeError("Requested analysis window is empty.")

    _emit(
        progress_callback,
        "start",
        source_video=str(video),
        start_sec=start_sec,
        duration_sec=clip_duration_sec,
        analysis_fps=analysis_fps,
    )

    keyframe_offset = keyframe_offset_sec if keyframe_offset_sec >= 0 else clip_duration_sec / 2.0
    config = ExperimentConfig(
        clip_start_sec=start_sec,
        clip_duration_sec=clip_duration_sec,
        keyframe_offset_sec=keyframe_offset,
    )
    artifacts = build_long_run_artifacts(output_root)
    window_csv = artifacts.root_dir / "window_summary.csv"
    window_json = artifacts.root_dir / "window_summary.json"
    window_md = artifacts.root_dir / "window_summary.md"
    score_plot = artifacts.root_dir / "window_score_trends.png"
    risk_plot = artifacts.root_dir / "window_risk_trends.png"
    run_meta_json = artifacts.root_dir / "run_metadata.json"

    log_event(
        artifacts.events_jsonl_path,
        "long_run_started",
        source_video=str(video),
        start_sec=start_sec,
        duration_sec=clip_duration_sec,
        analysis_fps=analysis_fps,
        window_sec=window_sec,
        window_step_sec=window_step_sec,
        fps=video_info["fps"],
        width=video_info["width"],
        height=video_info["height"],
    )

    timings: dict[str, float] = {}

    _emit(progress_callback, "extract_segment_started")
    t0 = time.perf_counter()
    extracted_clip_info = _extract_segment_with_fps(
        video,
        artifacts.clip_path,
        start_sec,
        clip_duration_sec,
        analysis_fps,
        artifacts.events_jsonl_path,
    )
    timings["extract_segment_sec"] = time.perf_counter() - t0
    _emit(progress_callback, "extract_segment_finished", clip_video=str(artifacts.clip_path))

    _emit(progress_callback, "evaluate_full_clip_started")
    t0 = time.perf_counter()
    frame_metrics_df, summary = evaluate_clip(artifacts.clip_path, artifacts, config)
    timings["evaluate_full_clip_sec"] = time.perf_counter() - t0
    _emit(
        progress_callback,
        "evaluate_full_clip_finished",
        frames=summary["quality_control"]["frames_analyzed"],
        overall_score=summary["scores"]["heuristic_nonverbal_score"],
    )

    _emit(progress_callback, "keyframe_summary_started")
    t0 = time.perf_counter()
    extract_frame(artifacts.clip_path, artifacts.keyframe_path, keyframe_offset, artifacts.events_jsonl_path)
    annotate_keyframe(artifacts.keyframe_path, artifacts.annotated_keyframe_path, summary, config, artifacts.events_jsonl_path)
    save_summary_markdown(summary, artifacts)
    timings["keyframe_and_summary_sec"] = time.perf_counter() - t0
    _emit(progress_callback, "keyframe_summary_finished", summary_md=str(artifacts.summary_md_path))

    semantic_payload: dict[str, Any] | None = None
    if enable_semantic:
        _emit(progress_callback, "semantic_started")
        t0 = time.perf_counter()
        semantic_config = SemanticConfig(
            enabled=True,
            sample_interval_sec=semantic_sample_interval_sec,
            max_samples=semantic_max_samples,
            qwen_enabled=not disable_qwen,
            qwen_model=qwen_model,
            qwen_device=qwen_device,
            qwen_device_map=qwen_device_map,
            qwen_dtype=qwen_dtype,
            qwen_max_new_tokens=qwen_max_new_tokens,
            qwen_temperature=qwen_temperature,
            sam2_enabled=not disable_sam2,
            sam2_model_cfg=sam2_model_cfg,
            sam2_checkpoint=sam2_checkpoint,
            sam2_device=sam2_device,
        )
        log_event(
            artifacts.events_jsonl_path,
            "semantic_extensions_started",
            qwen_enabled=semantic_config.qwen_enabled,
            sam2_enabled=semantic_config.sam2_enabled,
            qwen_model=semantic_config.qwen_model,
            qwen_device=semantic_config.qwen_device,
            qwen_device_map=semantic_config.qwen_device_map,
            sam2_model_cfg=semantic_config.sam2_model_cfg,
            sam2_checkpoint=str(semantic_config.sam2_checkpoint) if semantic_config.sam2_checkpoint else None,
            sam2_device=semantic_config.sam2_device,
            sample_interval_sec=semantic_config.sample_interval_sec,
            max_samples=semantic_config.max_samples,
        )
        semantic_payload = run_semantic_extensions(
            clip_path=artifacts.clip_path,
            frame_metrics_df=frame_metrics_df,
            summary=summary,
            run_dir=artifacts.root_dir,
            config=semantic_config,
            events_path=artifacts.events_jsonl_path,
        )
        timings["semantic_extensions_sec"] = time.perf_counter() - t0
        _emit(progress_callback, "semantic_finished", semantic_summary=semantic_payload["artifacts"]["summary_md"])

    fps = float(summary["clip"]["fps"])
    windows = _window_slices(summary["clip"]["duration_sec_actual"], window_sec, window_step_sec)
    rows: list[dict[str, float | str]] = []

    _emit(progress_callback, "window_aggregation_started")
    t0 = time.perf_counter()
    for local_start_sec, local_end_sec in windows:
        window_df = frame_metrics_df[
            (frame_metrics_df["timestamp_sec"] >= local_start_sec) & (frame_metrics_df["timestamp_sec"] < local_end_sec)
        ].copy()
        if window_df.empty:
            continue
        clip_info = {
            "clip_video": str(video),
            "start_sec": start_sec + local_start_sec,
            "duration_sec_requested": local_end_sec - local_start_sec,
            "fps": fps,
            "frames_written": int(len(window_df)),
        }
        _, window_summary = summarize_frame_metrics(window_df, fps, clip_info)
        row = {
            "window_local_start_sec": float(local_start_sec),
            "window_local_end_sec": float(local_end_sec),
            "window_start_sec": float(start_sec + local_start_sec),
            "window_end_sec": float(start_sec + local_end_sec),
            "window_duration_sec": float(local_end_sec - local_start_sec),
            "pose_coverage": window_summary["quality_control"]["pose_coverage"],
            "face_coverage": window_summary["quality_control"]["face_coverage"],
            "hand_coverage": window_summary["quality_control"]["hand_coverage"],
            "natural_movement_score": window_summary["scores"]["natural_movement_score"],
            "positive_affect_score": window_summary["scores"]["positive_affect_score"],
            "enthusiasm_score": window_summary["scores"]["enthusiasm_score"],
            "posture_stability_score": window_summary["scores"]["posture_stability_score"],
            "confidence_presence_score": window_summary["scores"]["confidence_presence_score"],
            "audience_orientation_score": window_summary["scores"]["audience_orientation_score"],
            "eye_contact_distribution_score": window_summary["scores"]["eye_contact_distribution_score"],
            "alertness_score": window_summary["scores"]["alertness_score"],
            "static_behavior_risk": window_summary["category_feedback"]["gesture_and_facial_expression"]["static_behavior_risk"],
            "excessive_animation_risk": window_summary["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"],
            "tension_hostility_risk": window_summary["category_feedback"]["gesture_and_facial_expression"]["tension_hostility_risk"],
            "rigidity_risk": window_summary["category_feedback"]["gesture_and_facial_expression"]["rigidity_risk"],
            "closed_posture_risk": window_summary["category_feedback"]["posture_and_presence"]["closed_posture_risk"],
            "heuristic_nonverbal_score": window_summary["scores"]["heuristic_nonverbal_score"],
        }
        rows.append(row)
    timings["window_aggregation_sec"] = time.perf_counter() - t0
    if not rows:
        raise RuntimeError("Window aggregation produced no rows.")
    _emit(progress_callback, "window_aggregation_finished", window_count=len(rows))

    window_df = pd.DataFrame(rows).sort_values("window_start_sec")
    window_df.to_csv(window_csv, index=False)
    window_json.write_text(window_df.to_json(orient="records", indent=2), encoding="utf-8")
    _save_window_markdown(window_md, video, summary["clip"]["duration_sec_actual"], window_sec, window_step_sec, window_df)

    _emit(progress_callback, "window_figures_started")
    t0 = time.perf_counter()
    _save_window_figures(window_df, score_plot, risk_plot)
    timings["window_figures_sec"] = time.perf_counter() - t0
    _emit(progress_callback, "window_figures_finished", window_md=str(window_md))

    best = window_df.sort_values("heuristic_nonverbal_score", ascending=False).iloc[0]
    worst = window_df.sort_values("heuristic_nonverbal_score", ascending=True).iloc[0]

    coaching_payload: dict[str, Any] | None = None
    if enable_coaching:
        _emit(progress_callback, "coaching_started")
        t0 = time.perf_counter()
        coaching_config = CoachingConfig(
            enabled=True,
            coach_model=coach_model,
            coach_device=coach_device,
            coach_max_windows=coach_max_windows,
            coach_top_actions=coach_top_actions,
            coach_render_pdf=coach_render_pdf,
            coach_fallback_template_only=coach_fallback_template_only,
            qwen_enabled=not disable_qwen,
            qwen_model=qwen_model,
            qwen_device=qwen_device,
            qwen_device_map=qwen_device_map,
            qwen_dtype=qwen_dtype,
            qwen_max_new_tokens=qwen_max_new_tokens,
            qwen_temperature=qwen_temperature,
        )
        log_event(
            artifacts.events_jsonl_path,
            "coaching_report_started",
            coach_model=coaching_config.coach_model,
            coach_device=coaching_config.coach_device,
            coach_max_windows=coaching_config.coach_max_windows,
            coach_top_actions=coaching_config.coach_top_actions,
            coach_render_pdf=coaching_config.coach_render_pdf,
            coach_fallback_template_only=coaching_config.coach_fallback_template_only,
            qwen_enabled=coaching_config.qwen_enabled,
            qwen_model=coaching_config.qwen_model,
        )
        coaching_payload = run_coaching_report(
            clip_path=artifacts.clip_path,
            frame_metrics_df=frame_metrics_df,
            summary=summary,
            window_df=window_df,
            run_dir=artifacts.root_dir,
            config=coaching_config,
            events_path=artifacts.events_jsonl_path,
            semantic_payload=semantic_payload,
        )
        timings["coaching_report_sec"] = time.perf_counter() - t0
        _emit(progress_callback, "coaching_finished", report_md=coaching_payload["artifacts"]["report_md"])

    metadata = {
        "source_video": str(video),
        "video_info": video_info,
        "extracted_clip_info": extracted_clip_info,
        "summary": summary,
        "windowing": {
            "window_sec": window_sec,
            "window_step_sec": window_step_sec,
            "window_count": int(len(window_df)),
            "best_window": best.to_dict(),
            "worst_window": worst.to_dict(),
        },
        "timings_sec": timings,
        "artifacts": {
            "per_frame_csv": str(artifacts.per_frame_csv_path),
            "summary_json": str(artifacts.summary_json_path),
            "summary_md": str(artifacts.summary_md_path),
            "annotated_keyframe": str(artifacts.annotated_keyframe_path),
            "timeline_plot": str(artifacts.timeline_plot_path),
            "window_csv": str(window_csv),
            "window_json": str(window_json),
            "window_md": str(window_md),
            "window_score_plot": str(score_plot),
            "window_risk_plot": str(risk_plot),
        },
    }
    if semantic_payload is not None:
        metadata["semantic_extensions"] = semantic_payload["summary"]
        metadata["artifacts"]["semantic"] = semantic_payload["artifacts"]
    if coaching_payload is not None:
        metadata["coaching_report"] = coaching_payload["report"]
        metadata["artifacts"]["coaching"] = coaching_payload["artifacts"]
    run_meta_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    log_event(
        artifacts.events_jsonl_path,
        "long_run_finished",
        summary_json=str(artifacts.summary_json_path),
        window_csv=str(window_csv),
        window_score_plot=str(score_plot),
        window_risk_plot=str(risk_plot),
        timings_sec=timings,
        best_window_start_sec=float(best["window_start_sec"]),
        best_window_score=float(best["heuristic_nonverbal_score"]),
        worst_window_start_sec=float(worst["window_start_sec"]),
        worst_window_score=float(worst["heuristic_nonverbal_score"]),
    )
    _emit(progress_callback, "finished", run_dir=str(artifacts.root_dir))
    return {
        "run_dir": str(artifacts.root_dir),
        "summary": summary,
        "window_df": window_df,
        "window_csv": str(window_csv),
        "window_md": str(window_md),
        "score_plot": str(score_plot),
        "risk_plot": str(risk_plot),
        "artifacts": metadata["artifacts"],
        "metadata": metadata,
        "semantic_payload": semantic_payload,
        "coaching_payload": coaching_payload,
        "timings": timings,
    }
