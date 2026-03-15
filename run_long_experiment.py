from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from nonverbal_eval import (
    ExperimentArtifacts,
    ExperimentConfig,
    annotate_keyframe,
    evaluate_clip,
    extract_frame,
    save_summary_markdown,
    summarize_frame_metrics,
)
from nonverbal_eval.pipeline import log_event


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


def _build_artifacts(output_root: Path) -> ExperimentArtifacts:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run long-form nonverbal cue inference over an extended lecture segment.")
    parser.add_argument("--video", type=Path, required=True, help="Path to the source lecture video.")
    parser.add_argument("--output-root", type=Path, default=Path("/workspace/artifacts/nonverbal_eval_long"), help="Directory for long-run artifacts.")
    parser.add_argument("--start-sec", type=float, default=92.5, help="Start time of the analyzed context window in the source video.")
    parser.add_argument("--duration-sec", type=float, default=60.0, help="Duration of the analyzed context window. Use 0 to continue until the end.")
    parser.add_argument("--analysis-fps", type=float, default=12.0, help="FPS to use for the extracted analysis clip. Use 0 to keep the source FPS.")
    parser.add_argument("--window-sec", type=float, default=15.0, help="Window size for lecture-level summaries.")
    parser.add_argument("--window-step-sec", type=float, default=15.0, help="Window stride for lecture-level summaries.")
    parser.add_argument("--keyframe-offset-sec", type=float, default=-1.0, help="Keyframe offset inside the full analyzed segment. Negative means midpoint.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    video_info = _video_info(args.video)
    max_duration_sec = max(float(video_info["duration_sec"]) - args.start_sec, 0.0)
    clip_duration_sec = max_duration_sec if args.duration_sec <= 0 else min(args.duration_sec, max_duration_sec)
    if clip_duration_sec <= 0:
        raise RuntimeError("Requested analysis window is empty.")
    keyframe_offset_sec = args.keyframe_offset_sec if args.keyframe_offset_sec >= 0 else clip_duration_sec / 2.0
    config = ExperimentConfig(
        clip_start_sec=args.start_sec,
        clip_duration_sec=clip_duration_sec,
        keyframe_offset_sec=keyframe_offset_sec,
    )
    artifacts = _build_artifacts(args.output_root)
    window_csv = artifacts.root_dir / "window_summary.csv"
    window_json = artifacts.root_dir / "window_summary.json"
    window_md = artifacts.root_dir / "window_summary.md"
    score_plot = artifacts.root_dir / "window_score_trends.png"
    risk_plot = artifacts.root_dir / "window_risk_trends.png"
    run_meta_json = artifacts.root_dir / "run_metadata.json"

    log_event(
        artifacts.events_jsonl_path,
        "long_run_started",
        source_video=str(args.video),
        start_sec=args.start_sec,
        duration_sec=clip_duration_sec,
        analysis_fps=args.analysis_fps,
        window_sec=args.window_sec,
        window_step_sec=args.window_step_sec,
        fps=video_info["fps"],
        width=video_info["width"],
        height=video_info["height"],
    )

    timings: dict[str, float] = {}

    t0 = time.perf_counter()
    extracted_clip_info = _extract_segment_with_fps(
        args.video,
        artifacts.clip_path,
        args.start_sec,
        clip_duration_sec,
        args.analysis_fps,
        artifacts.events_jsonl_path,
    )
    timings["extract_segment_sec"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    frame_metrics_df, summary = evaluate_clip(artifacts.clip_path, artifacts, config)
    timings["evaluate_full_clip_sec"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    extract_frame(artifacts.clip_path, artifacts.keyframe_path, keyframe_offset_sec, artifacts.events_jsonl_path)
    annotate_keyframe(artifacts.keyframe_path, artifacts.annotated_keyframe_path, summary, config, artifacts.events_jsonl_path)
    save_summary_markdown(summary, artifacts)
    timings["keyframe_and_summary_sec"] = time.perf_counter() - t0

    fps = float(summary["clip"]["fps"])
    windows = _window_slices(summary["clip"]["duration_sec_actual"], args.window_sec, args.window_step_sec)
    rows: list[dict[str, float | str]] = []

    t0 = time.perf_counter()
    for local_start_sec, local_end_sec in windows:
        window_df = frame_metrics_df[
            (frame_metrics_df["timestamp_sec"] >= local_start_sec) & (frame_metrics_df["timestamp_sec"] < local_end_sec)
        ].copy()
        if window_df.empty:
            continue
        clip_info = {
            "clip_video": str(args.video),
            "start_sec": args.start_sec + local_start_sec,
            "duration_sec_requested": local_end_sec - local_start_sec,
            "fps": fps,
            "frames_written": int(len(window_df)),
        }
        _, window_summary = summarize_frame_metrics(window_df, fps, clip_info)
        row = {
            "window_local_start_sec": float(local_start_sec),
            "window_local_end_sec": float(local_end_sec),
            "window_start_sec": float(args.start_sec + local_start_sec),
            "window_end_sec": float(args.start_sec + local_end_sec),
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

    window_df = pd.DataFrame(rows).sort_values("window_start_sec")
    window_df.to_csv(window_csv, index=False)
    window_json.write_text(window_df.to_json(orient="records", indent=2), encoding="utf-8")
    _save_window_markdown(window_md, args.video, summary["clip"]["duration_sec_actual"], args.window_sec, args.window_step_sec, window_df)

    t0 = time.perf_counter()
    _save_window_figures(window_df, score_plot, risk_plot)
    timings["window_figures_sec"] = time.perf_counter() - t0

    best = window_df.sort_values("heuristic_nonverbal_score", ascending=False).iloc[0]
    worst = window_df.sort_values("heuristic_nonverbal_score", ascending=True).iloc[0]
    metadata = {
        "source_video": str(args.video),
        "video_info": video_info,
        "extracted_clip_info": extracted_clip_info,
        "summary": summary,
        "windowing": {
            "window_sec": args.window_sec,
            "window_step_sec": args.window_step_sec,
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

    print(f"Run directory: {artifacts.root_dir}")
    print(f"Source window: start={args.start_sec:.2f}s duration={clip_duration_sec:.2f}s")
    print(f"Analysis FPS: {summary['clip']['fps']:.2f}")
    print(f"Full duration analyzed: {summary['clip']['duration_sec_actual']:.2f}s")
    print(f"Frames analyzed: {summary['quality_control']['frames_analyzed']}")
    print(f"Overall score: {summary['scores']['heuristic_nonverbal_score']:.2f}")
    print(
        "Best window: "
        f"{best['window_start_sec']:.0f}s-{best['window_end_sec']:.0f}s overall={best['heuristic_nonverbal_score']:.2f}"
    )
    print(
        "Worst window: "
        f"{worst['window_start_sec']:.0f}s-{worst['window_end_sec']:.0f}s overall={worst['heuristic_nonverbal_score']:.2f}"
    )
    for key, value in timings.items():
        print(f"{key}: {value:.2f}s")


if __name__ == "__main__":
    main()
