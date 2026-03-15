from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from nonverbal_eval import (
    ExperimentConfig,
    annotate_keyframe,
    evaluate_clip,
    extract_clip,
    extract_frame,
    save_summary_markdown,
)
from nonverbal_eval.pipeline import build_artifacts, log_event


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multiple lecture-clip experiments and aggregate the results.")
    parser.add_argument("--video", type=Path, required=True, help="Path to the source lecture video.")
    parser.add_argument("--output-root", type=Path, default=Path("/workspace/artifacts/nonverbal_eval_batch"), help="Directory for batch artifacts.")
    parser.add_argument("--starts", type=str, default="60,90,120,150", help="Comma-separated clip start times in seconds.")
    parser.add_argument("--duration-sec", type=float, default=5.0, help="Clip duration in seconds.")
    parser.add_argument("--keyframe-offset-sec", type=float, default=2.5, help="Offset within each extracted clip for the keyframe.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    starts = [float(part.strip()) for part in args.starts.split(",") if part.strip()]
    batch_dir = args.output_root / f"batch_{_timestamp()}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    batch_log = batch_dir / "batch_events.jsonl"

    log_event(
        batch_log,
        "batch_started",
        source_video=str(args.video),
        starts=starts,
        duration_sec=args.duration_sec,
        keyframe_offset_sec=args.keyframe_offset_sec,
    )

    rows: list[dict[str, object]] = []
    for start in starts:
        run_root = batch_dir / f"segment_{int(start):03d}s"
        config = ExperimentConfig(
            clip_start_sec=start,
            clip_duration_sec=args.duration_sec,
            keyframe_offset_sec=args.keyframe_offset_sec,
        )
        artifacts = build_artifacts(run_root)
        log_event(batch_log, "segment_started", start_sec=start, run_dir=str(artifacts.root_dir))

        extract_clip(args.video, artifacts.clip_path, config.clip_start_sec, config.clip_duration_sec, artifacts.events_jsonl_path)
        extract_frame(artifacts.clip_path, artifacts.keyframe_path, config.keyframe_offset_sec, artifacts.events_jsonl_path)
        _, summary = evaluate_clip(artifacts.clip_path, artifacts, config)
        annotate_keyframe(artifacts.keyframe_path, artifacts.annotated_keyframe_path, summary, config, artifacts.events_jsonl_path)
        save_summary_markdown(summary, artifacts)

        row = {
            "start_sec": start,
            "run_dir": str(artifacts.root_dir),
            "pose_coverage": summary["quality_control"]["pose_coverage"],
            "face_coverage": summary["quality_control"]["face_coverage"],
            "hand_coverage": summary["quality_control"]["hand_coverage"],
            "natural_movement_score": summary["scores"]["natural_movement_score"],
            "positive_affect_score": summary["scores"]["positive_affect_score"],
            "enthusiasm_score": summary["scores"]["enthusiasm_score"],
            "posture_stability_score": summary["scores"]["posture_stability_score"],
            "confidence_presence_score": summary["scores"]["confidence_presence_score"],
            "audience_orientation_score": summary["scores"]["audience_orientation_score"],
            "eye_contact_distribution_score": summary["scores"]["eye_contact_distribution_score"],
            "alertness_score": summary["scores"]["alertness_score"],
            "static_behavior_risk": summary["category_feedback"]["gesture_and_facial_expression"]["static_behavior_risk"],
            "excessive_animation_risk": summary["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"],
            "rigidity_risk": summary["category_feedback"]["gesture_and_facial_expression"]["rigidity_risk"],
            "heuristic_nonverbal_score": summary["scores"]["heuristic_nonverbal_score"],
        }
        rows.append(row)
        log_event(batch_log, "segment_finished", start_sec=start, run_dir=str(artifacts.root_dir), summary=row)

    comparison = pd.DataFrame(rows).sort_values("start_sec")
    comparison_csv = batch_dir / "comparison.csv"
    comparison_json = batch_dir / "comparison.json"
    comparison_md = batch_dir / "comparison.md"
    comparison.to_csv(comparison_csv, index=False)
    comparison_json.write_text(comparison.to_json(orient="records", indent=2), encoding="utf-8")

    best_row = comparison.sort_values("heuristic_nonverbal_score", ascending=False).iloc[0]
    md = "# Segment Comparison\n\n"
    md += f"- Source video: `{args.video}`\n"
    md += f"- Starts tested: `{starts}`\n"
    md += f"- Duration per segment: `{args.duration_sec:.1f}s`\n"
    md += f"- Best overall segment: `{best_row['start_sec']:.0f}s` with score `{best_row['heuristic_nonverbal_score']:.1f}`\n\n"
    md += "## Comparison Table\n\n"
    table_df = comparison[
        [
            "start_sec",
            "natural_movement_score",
            "positive_affect_score",
            "posture_stability_score",
            "confidence_presence_score",
            "eye_contact_distribution_score",
            "alertness_score",
            "static_behavior_risk",
            "excessive_animation_risk",
            "heuristic_nonverbal_score",
        ]
    ]
    md += _markdown_table(table_df)
    md += "\n"
    comparison_md.write_text(md, encoding="utf-8")

    log_event(
        batch_log,
        "batch_finished",
        comparison_csv=str(comparison_csv),
        comparison_json=str(comparison_json),
        comparison_md=str(comparison_md),
        best_segment_start_sec=float(best_row["start_sec"]),
        best_segment_score=float(best_row["heuristic_nonverbal_score"]),
    )

    print(f"Batch directory: {batch_dir}")
    print(f"Comparison CSV: {comparison_csv}")
    print(f"Comparison Markdown: {comparison_md}")
    print("Top segments:")
    for _, row in comparison.sort_values("heuristic_nonverbal_score", ascending=False).head(3).iterrows():
        print(
            f"- start={row['start_sec']:.0f}s overall={row['heuristic_nonverbal_score']:.2f} "
            f"natural={row['natural_movement_score']:.2f} eye_contact={row['eye_contact_distribution_score']:.2f}"
        )


if __name__ == "__main__":
    main()
