from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from validation_tooling import (
    BATCHES_ROOT,
    CLIPS_ROOT,
    RUNS_ROOT,
    add_manifest_args,
    add_selection_args,
    ensure_dir,
    load_manifest,
    markdown_table,
    read_json,
    select_manifest_rows,
    shorten_text,
    timestamp_utc,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the long evaluation pipeline over a validation manifest subset.")
    add_manifest_args(parser)
    add_selection_args(parser)
    parser.add_argument("--clips-root", type=Path, default=CLIPS_ROOT, help="Directory that contains extracted validation clips.")
    parser.add_argument("--runs-root", type=Path, default=RUNS_ROOT, help="Directory that will contain long-run outputs.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Batch output directory. Defaults to evaluation/local_data/batches/batch_<timestamp>.")
    parser.add_argument("--analysis-fps", type=float, default=12.0, help="FPS used by the long evaluation pipeline.")
    parser.add_argument("--window-sec", type=float, default=15.0, help="Window size used by the long evaluation pipeline.")
    parser.add_argument("--window-step-sec", type=float, default=15.0, help="Window stride used by the long evaluation pipeline.")
    parser.add_argument("--report-top-n", type=int, default=5, help="How many top and bottom clips to show in the markdown summary.")
    return parser.parse_args()


def _find_clip(clips_root: Path, clip_id: str) -> Path:
    clip_path = clips_root / clip_id / "clip.mp4"
    if not clip_path.exists():
        raise RuntimeError(f"Missing extracted clip for {clip_id}: {clip_path}")
    return clip_path


def _clip_metadata(clip_path: Path) -> dict[str, object]:
    metadata_path = clip_path.with_suffix(".json")
    if metadata_path.exists():
        return read_json(metadata_path)
    return {
        "status": "unknown",
        "source_video": "",
        "clip_path": str(clip_path),
        "start_sec": "",
        "duration_sec_requested": "",
        "duration_sec_actual": "",
        "target_fps": "",
        "source_fps": "",
        "frames_written": "",
    }


def _failure_row(manifest_row: dict[str, object], clip_path: Path, error: Exception) -> dict[str, object]:
    clip_meta = _clip_metadata(clip_path)
    return {
        **manifest_row,
        "clip_status": clip_meta.get("status", ""),
        "clip_path": str(clip_path),
        "clip_start_sec": clip_meta.get("start_sec", ""),
        "clip_duration_sec_actual": clip_meta.get("duration_sec_actual", ""),
        "clip_target_fps": clip_meta.get("target_fps", ""),
        "run_status": "failed",
        "run_dir": "",
        "summary_json": "",
        "summary_md": "",
        "window_csv": "",
        "window_md": "",
        "window_score_plot": "",
        "window_risk_plot": "",
        "frames_analyzed": "",
        "pose_coverage": "",
        "face_coverage": "",
        "hand_coverage": "",
        "natural_movement_score": "",
        "positive_affect_score": "",
        "enthusiasm_score": "",
        "posture_stability_score": "",
        "confidence_presence_score": "",
        "audience_orientation_score": "",
        "eye_contact_distribution_score": "",
        "alertness_score": "",
        "gesture_smoothness_score": "",
        "stage_usage_score": "",
        "heuristic_nonverbal_score": "",
        "best_window_start_sec": "",
        "best_window_end_sec": "",
        "best_window_score": "",
        "worst_window_start_sec": "",
        "worst_window_end_sec": "",
        "worst_window_score": "",
        "static_behavior_risk": "",
        "excessive_animation_risk": "",
        "tension_hostility_risk": "",
        "rigidity_risk": "",
        "closed_posture_risk": "",
        "error": str(error),
    }


def _success_row(manifest_row: dict[str, object], clip_path: Path, result: dict[str, object]) -> dict[str, object]:
    clip_meta = _clip_metadata(clip_path)
    summary = result["summary"]
    metadata = result["metadata"]
    best = metadata["windowing"]["best_window"]
    worst = metadata["windowing"]["worst_window"]
    risks = summary["category_feedback"]["gesture_and_facial_expression"]
    posture_risks = summary["category_feedback"]["posture_and_presence"]
    scores = summary["scores"]
    qc = summary["quality_control"]
    artifacts = result["artifacts"]
    return {
        **manifest_row,
        "clip_status": clip_meta.get("status", ""),
        "clip_path": str(clip_path),
        "clip_start_sec": clip_meta.get("start_sec", ""),
        "clip_duration_sec_actual": clip_meta.get("duration_sec_actual", ""),
        "clip_target_fps": clip_meta.get("target_fps", ""),
        "run_status": "ok",
        "run_dir": result["run_dir"],
        "summary_json": artifacts["summary_json"],
        "summary_md": artifacts["summary_md"],
        "window_csv": result["window_csv"],
        "window_md": result["window_md"],
        "window_score_plot": result["score_plot"],
        "window_risk_plot": result["risk_plot"],
        "frames_analyzed": qc["frames_analyzed"],
        "pose_coverage": qc["pose_coverage"],
        "face_coverage": qc["face_coverage"],
        "hand_coverage": qc["hand_coverage"],
        "natural_movement_score": scores["natural_movement_score"],
        "positive_affect_score": scores["positive_affect_score"],
        "enthusiasm_score": scores["enthusiasm_score"],
        "posture_stability_score": scores["posture_stability_score"],
        "confidence_presence_score": scores["confidence_presence_score"],
        "audience_orientation_score": scores["audience_orientation_score"],
        "eye_contact_distribution_score": scores["eye_contact_distribution_score"],
        "alertness_score": scores["alertness_score"],
        "gesture_smoothness_score": scores["gesture_smoothness_score"],
        "stage_usage_score": scores["stage_usage_score"],
        "heuristic_nonverbal_score": scores["heuristic_nonverbal_score"],
        "best_window_start_sec": best["window_start_sec"],
        "best_window_end_sec": best["window_end_sec"],
        "best_window_score": best["heuristic_nonverbal_score"],
        "worst_window_start_sec": worst["window_start_sec"],
        "worst_window_end_sec": worst["window_end_sec"],
        "worst_window_score": worst["heuristic_nonverbal_score"],
        "static_behavior_risk": risks["static_behavior_risk"],
        "excessive_animation_risk": risks["excessive_animation_risk"],
        "tension_hostility_risk": risks["tension_hostility_risk"],
        "rigidity_risk": risks["rigidity_risk"],
        "closed_posture_risk": posture_risks["closed_posture_risk"],
        "error": "",
    }


def _summary_markdown(batch_dir: Path, args: argparse.Namespace, selection: pd.DataFrame, results: pd.DataFrame) -> str:
    success_df = results[results["run_status"] == "ok"].copy()
    failed_df = results[results["run_status"] != "ok"].copy()

    md = "# Validation Batch Summary\n\n"
    md += f"- Batch directory: `{batch_dir}`\n"
    md += f"- Manifest: `{args.manifest}`\n"
    md += f"- Selected rows: `{len(selection)}`\n"
    md += f"- Successful runs: `{len(success_df)}`\n"
    md += f"- Failed runs: `{len(failed_df)}`\n"
    md += f"- Selection filters: `clip_ids={args.clip_ids or 'all'}`, `priority_tiers={args.priority_tiers or 'all'}`, `goldset_only={args.goldset_only}`, `limit={args.limit or 'none'}`\n"
    md += f"- Analysis FPS: `{args.analysis_fps:.1f}`\n"
    md += f"- Window size: `{args.window_sec:.1f}s`, step `{args.window_step_sec:.1f}s`\n\n"

    md += "## Status Counts\n\n"
    md += markdown_table(results["run_status"].value_counts().rename_axis("run_status").reset_index(name="count"))
    md += "\n\n"

    if not success_df.empty:
        md += "## Score Summary\n\n"
        score_stats = success_df["heuristic_nonverbal_score"].agg(["count", "mean", "median", "min", "max"]).reset_index()
        score_stats.columns = ["metric", "value"]
        md += markdown_table(score_stats, max_text_length=40)
        md += "\n\n"

        tier_summary = (
            success_df.groupby("priority_tier", dropna=False)["heuristic_nonverbal_score"]
            .agg(["count", "mean", "min", "max"])
            .reset_index()
        )
        md += "## Priority Tier Summary\n\n"
        md += markdown_table(tier_summary)
        md += "\n\n"

        top_df = success_df.sort_values("heuristic_nonverbal_score", ascending=False).head(args.report_top_n).copy()
        top_df["title"] = top_df["title"].map(lambda value: shorten_text(value, 72))
        md += f"## Top {min(args.report_top_n, len(top_df))}\n\n"
        md += markdown_table(top_df[["clip_id", "priority_tier", "goldset_candidate", "heuristic_nonverbal_score", "title"]])
        md += "\n\n"

        bottom_df = success_df.sort_values("heuristic_nonverbal_score", ascending=True).head(args.report_top_n).copy()
        bottom_df["title"] = bottom_df["title"].map(lambda value: shorten_text(value, 72))
        md += f"## Bottom {min(args.report_top_n, len(bottom_df))}\n\n"
        md += markdown_table(bottom_df[["clip_id", "priority_tier", "goldset_candidate", "heuristic_nonverbal_score", "title"]])
        md += "\n\n"
    else:
        md += "## Score Summary\n\n"
        md += "_No successful long-run evaluations were completed._\n\n"

    if not failed_df.empty:
        md += "## Failures\n\n"
        failed_view = failed_df[["clip_id", "clip_path", "error"]].copy()
        failed_view["error"] = failed_view["error"].map(lambda value: shorten_text(value, 120))
        md += markdown_table(failed_view)
        md += "\n\n"

    md += "## Output Files\n\n"
    md += f"- `batch_results.csv`: row-level manifest and evaluation output.\n"
    md += f"- `selected_manifest.csv`: filtered manifest subset used for this batch.\n"
    md += f"- `batch_parameters.json`: captured CLI arguments and resolved selection count.\n"
    md += "\n"
    return md


def main() -> None:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    selection = select_manifest_rows(
        manifest,
        clip_ids=args.clip_ids,
        priority_tiers=args.priority_tiers,
        goldset_only=args.goldset_only,
        limit=args.limit,
    )

    batch_dir = ensure_dir(args.output_dir or (BATCHES_ROOT / f"batch_{timestamp_utc()}"))
    runs_root = ensure_dir(args.runs_root)
    selected_manifest_csv = batch_dir / "selected_manifest.csv"
    batch_parameters_json = batch_dir / "batch_parameters.json"
    batch_results_csv = batch_dir / "batch_results.csv"
    batch_summary_md = batch_dir / "batch_summary.md"

    selection.to_csv(selected_manifest_csv, index=False)
    write_json(
        batch_parameters_json,
        {
            "manifest": str(args.manifest),
            "clips_root": str(args.clips_root),
            "runs_root": str(runs_root),
            "analysis_fps": args.analysis_fps,
            "window_sec": args.window_sec,
            "window_step_sec": args.window_step_sec,
            "clip_ids": args.clip_ids,
            "priority_tiers": args.priority_tiers,
            "goldset_only": args.goldset_only,
            "limit": args.limit,
            "selection_count": len(selection),
        },
    )

    try:
        from nonverbal_eval.app_service import run_teacher_evaluation
    except Exception as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            "Could not import the long evaluation pipeline. Install the evaluation environment "
            "from requirements_eval.txt before running this batch script."
        ) from exc

    rows: list[dict[str, object]] = []
    for _, row in selection.iterrows():
        row_data = row.to_dict()
        clip_id = str(row_data["clip_id"])
        clip_path = args.clips_root / clip_id / "clip.mp4"
        run_root = runs_root / clip_id
        try:
            clip_path = _find_clip(args.clips_root, clip_id)
            result = run_teacher_evaluation(
                video=clip_path,
                output_root=run_root,
                start_sec=0.0,
                duration_sec=0.0,
                analysis_fps=args.analysis_fps,
                window_sec=args.window_sec,
                window_step_sec=args.window_step_sec,
                keyframe_offset_sec=-1.0,
                enable_semantic=False,
                enable_coaching=False,
            )
            rows.append(_success_row(row_data, clip_path, result))
            print(f"{clip_id}: ok -> {result['run_dir']}")
        except Exception as exc:  # pragma: no cover - exercised in real failures
            rows.append(_failure_row(row_data, clip_path, exc))
            print(f"{clip_id}: failed -> {exc}")

    results = pd.DataFrame(rows)
    results.to_csv(batch_results_csv, index=False)
    batch_summary_md.write_text(_summary_markdown(batch_dir, args, selection, results), encoding="utf-8")

    print(f"Batch directory: {batch_dir}")
    print(f"Batch results: {batch_results_csv}")
    print(f"Batch summary: {batch_summary_md}")
    print(f"Selected manifest: {selected_manifest_csv}")


if __name__ == "__main__":
    main()
