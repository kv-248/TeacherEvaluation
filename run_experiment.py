from __future__ import annotations

import argparse
from pathlib import Path

from nonverbal_eval import (
    ExperimentConfig,
    annotate_keyframe,
    evaluate_clip,
    extract_clip,
    extract_frame,
    render_debug_visuals,
    save_summary_markdown,
)
from nonverbal_eval.pipeline import build_artifacts, log_event


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a nonverbal cue experiment on a short lecture clip.")
    parser.add_argument("--video", type=Path, required=True, help="Path to the source lecture video.")
    parser.add_argument("--output-root", type=Path, default=Path("/workspace/artifacts/nonverbal_eval"), help="Directory for experiment artifacts.")
    parser.add_argument("--start-sec", type=float, default=120.0, help="Start time for the 5s evaluation clip.")
    parser.add_argument("--duration-sec", type=float, default=5.0, help="Clip duration in seconds.")
    parser.add_argument("--keyframe-offset-sec", type=float, default=2.5, help="Offset within the extracted clip for the keyframe.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ExperimentConfig(
        clip_start_sec=args.start_sec,
        clip_duration_sec=args.duration_sec,
        keyframe_offset_sec=args.keyframe_offset_sec,
    )
    artifacts = build_artifacts(args.output_root)

    log_event(
        artifacts.events_jsonl_path,
        "experiment_started",
        source_video=str(args.video),
        output_root=str(artifacts.root_dir),
        clip_start_sec=config.clip_start_sec,
        clip_duration_sec=config.clip_duration_sec,
        keyframe_offset_sec=config.keyframe_offset_sec,
    )

    extract_clip(args.video, artifacts.clip_path, config.clip_start_sec, config.clip_duration_sec, artifacts.events_jsonl_path)
    extract_frame(artifacts.clip_path, artifacts.keyframe_path, config.keyframe_offset_sec, artifacts.events_jsonl_path)
    frame_metrics_df, summary = evaluate_clip(artifacts.clip_path, artifacts, config)
    annotate_keyframe(artifacts.keyframe_path, artifacts.annotated_keyframe_path, summary, config, artifacts.events_jsonl_path)
    render_debug_visuals(artifacts.clip_path, frame_metrics_df, summary, artifacts, config)
    save_summary_markdown(summary, artifacts)

    log_event(
        artifacts.events_jsonl_path,
        "experiment_finished",
        clip_video=str(artifacts.clip_path),
        summary_json=str(artifacts.summary_json_path),
        summary_md=str(artifacts.summary_md_path),
        keyframe=str(artifacts.annotated_keyframe_path),
        debug_video=str(artifacts.debug_video_path),
        debug_contact_sheet=str(artifacts.debug_contact_sheet_path),
        timeline_plot=str(artifacts.timeline_plot_path),
        frames_analyzed=summary["quality_control"]["frames_analyzed"],
        heuristic_nonverbal_score=summary["scores"]["heuristic_nonverbal_score"],
    )

    print(f"Artifacts: {artifacts.root_dir}")
    print(f"Clip: {artifacts.clip_path}")
    print(f"Keyframe: {artifacts.annotated_keyframe_path}")
    print(f"Debug video: {artifacts.debug_video_path}")
    print(f"Debug contact sheet: {artifacts.debug_contact_sheet_path}")
    print(f"Per-frame CSV: {artifacts.per_frame_csv_path}")
    print(f"Summary JSON: {artifacts.summary_json_path}")
    print(f"Summary Markdown: {artifacts.summary_md_path}")
    print(f"Timeline plot: {artifacts.timeline_plot_path}")
    print(f"Pose coverage: {summary['quality_control']['pose_coverage']:.3f}")
    print(f"Face coverage: {summary['quality_control']['face_coverage']:.3f}")
    print(f"Hand coverage: {summary['quality_control']['hand_coverage']:.3f}")
    print(f"Natural movement: {summary['scores']['natural_movement_score']:.2f}")
    print(f"Positive affect: {summary['scores']['positive_affect_score']:.2f}")
    print(f"Confidence/presence: {summary['scores']['confidence_presence_score']:.2f}")
    print(f"Eye-contact distribution: {summary['scores']['eye_contact_distribution_score']:.2f}")
    print(f"Alertness: {summary['scores']['alertness_score']:.2f}")
    print(f"Heuristic nonverbal score: {summary['scores']['heuristic_nonverbal_score']:.2f}")
    if summary["warnings"]:
        print("Warnings:")
        for warning in summary["warnings"]:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
