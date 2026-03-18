from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from register_local_clips import register_local_clips
from validation_tooling import (
    CLIPS_ROOT,
    RUNTIME_BATCHES_ROOT,
    RUNS_ROOT,
    ensure_dir,
    load_manifest,
    markdown_table,
    select_manifest_rows,
    shorten_text,
    timestamp_utc,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the long evaluation pipeline with Gemini Flash over local clips from /workspace/clips."
    )
    parser.add_argument("--source-dir", type=Path, default=Path("/workspace/clips"), help="Directory containing pre-cut local clips.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Tracked batch output directory. Defaults to evaluation/runtime_batches/local_flash_batch_<timestamp>.",
    )
    parser.add_argument(
        "--clips-root",
        type=Path,
        default=CLIPS_ROOT,
        help="Target root for clip.mp4 symlinks or copies.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=RUNS_ROOT / "gemini_flash_local",
        help="Ignored root that will contain full long-run outputs.",
    )
    parser.add_argument("--clip-ids", type=str, default="", help="Comma-separated clip_id values to process.")
    parser.add_argument("--priority-tiers", type=str, default="", help="Comma-separated priority tiers to process.")
    parser.add_argument("--goldset-only", action="store_true", help="Restrict processing to goldset_candidate rows.")
    parser.add_argument("--limit", type=int, default=0, help="Limit the selection to the first N rows after filtering.")
    parser.add_argument("--analysis-fps", type=float, default=12.0, help="FPS used by the long evaluation pipeline.")
    parser.add_argument("--window-sec", type=float, default=15.0, help="Window size used by the long evaluation pipeline.")
    parser.add_argument("--window-step-sec", type=float, default=15.0, help="Window stride used by the long evaluation pipeline.")
    parser.add_argument("--qwen-model", type=str, default="gemini-2.5-flash", help="Semantic review model.")
    parser.add_argument("--coach-model", type=str, default="gemini-2.5-flash", help="Coaching model.")
    parser.add_argument("--goldset-count", type=int, default=12, help="Mark the first N clips as goldset candidates when registering.")
    parser.add_argument("--copy-clips", action="store_true", help="Copy clips into local_data instead of using symlinks.")
    parser.add_argument("--report-top-n", type=int, default=5, help="How many top and bottom clips to show in the markdown summary.")
    parser.add_argument(
        "--include-summary-artifacts",
        action="store_true",
        help="Also copy summary_full.md/json into the tracked batch report directory.",
    )
    return parser.parse_args()


def _batch_dir(args: argparse.Namespace) -> Path:
    if args.output_dir is not None:
        return args.output_dir.resolve()
    return (RUNTIME_BATCHES_ROOT / f"local_flash_batch_{timestamp_utc()}").resolve()


def _safe_read_json(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    candidate = Path(path)
    if not candidate.exists():
        return None
    return json.loads(candidate.read_text(encoding="utf-8"))


def _copy_if_exists(src: str | Path | None, dest: Path) -> str:
    if not src:
        return ""
    src_path = Path(src)
    if not src_path.exists():
        return ""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dest)
    return str(dest)


def _report_dir(batch_dir: Path, clip_id: str) -> Path:
    return batch_dir / "reports" / clip_id


def _tracker_row(
    manifest_row: dict[str, Any],
    *,
    clip_path: Path,
    run_result: dict[str, Any] | None,
    error: Exception | None,
    copied_artifacts: dict[str, str],
) -> dict[str, Any]:
    if run_result is None:
        return {
            **manifest_row,
            "clip_path": str(clip_path),
            "run_status": "failed",
            "run_dir": "",
            "semantic_status": "",
            "coaching_mode": "",
            "top_action_count": "",
            "no_material_intervention_needed": "",
            "confidence_note": "",
            "overall_score": "",
            "audience_score": "",
            "alertness_score": "",
            "reliability": "",
            "copied_semantic_summary_md": copied_artifacts.get("semantic_summary_md", ""),
            "copied_semantic_summary_json": copied_artifacts.get("semantic_summary_json", ""),
            "copied_coaching_report_md": copied_artifacts.get("coaching_report_md", ""),
            "copied_coaching_report_json": copied_artifacts.get("coaching_report_json", ""),
            "copied_coaching_report_pdf": copied_artifacts.get("coaching_report_pdf", ""),
            "copied_summary_md": copied_artifacts.get("summary_md", ""),
            "copied_summary_json": copied_artifacts.get("summary_json", ""),
            "error": str(error) if error else "unknown error",
        }

    summary = run_result["summary"]
    semantic_payload = run_result.get("semantic_payload") or {}
    coaching_payload = run_result.get("coaching_payload") or {}
    semantic_summary = semantic_payload.get("summary") or {}
    coaching_report = coaching_payload.get("report") or {}
    confidence_notes = coaching_report.get("confidence_notes") or []
    return {
        **manifest_row,
        "clip_path": str(clip_path),
        "run_status": "ok",
        "run_dir": run_result["run_dir"],
        "semantic_status": semantic_summary.get("qwen", {}).get("status", ""),
        "coaching_mode": coaching_report.get("source", {}).get("mode", ""),
        "top_action_count": len(coaching_report.get("priority_actions") or []),
        "no_material_intervention_needed": coaching_report.get("no_material_intervention_needed", ""),
        "confidence_note": confidence_notes[0] if confidence_notes else "",
        "overall_score": summary["scores"]["heuristic_nonverbal_score"],
        "audience_score": summary["scores"]["audience_orientation_score"],
        "alertness_score": summary["scores"]["alertness_score"],
        "reliability": summary["quality_control"].get("quality_summary", ""),
        "copied_semantic_summary_md": copied_artifacts.get("semantic_summary_md", ""),
        "copied_semantic_summary_json": copied_artifacts.get("semantic_summary_json", ""),
        "copied_coaching_report_md": copied_artifacts.get("coaching_report_md", ""),
        "copied_coaching_report_json": copied_artifacts.get("coaching_report_json", ""),
        "copied_coaching_report_pdf": copied_artifacts.get("coaching_report_pdf", ""),
        "copied_summary_md": copied_artifacts.get("summary_md", ""),
        "copied_summary_json": copied_artifacts.get("summary_json", ""),
        "error": "",
    }


def _write_tracker_files(batch_dir: Path, rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    tracker_csv = batch_dir / "tracker.csv"
    tracker_json = batch_dir / "tracker.json"
    if rows:
        fieldnames = list(rows[0].keys())
        with tracker_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        tracker_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    else:
        tracker_csv.write_text("", encoding="utf-8")
        tracker_json.write_text("[]\n", encoding="utf-8")
    return tracker_csv, tracker_json


def _write_batch_summary(batch_dir: Path, rows: list[dict[str, Any]], args: argparse.Namespace) -> Path:
    tracker_df = pd.DataFrame(rows)
    summary_path = batch_dir / "batch_summary.md"

    lines = ["# Local Clips Gemini Flash Batch Summary", ""]
    lines.append(f"- Source dir: `{args.source_dir}`")
    lines.append(f"- Tracked batch dir: `{batch_dir}`")
    lines.append(f"- Runs root: `{args.runs_root}`")
    lines.append(f"- Analysis FPS: `{args.analysis_fps:.1f}`")
    lines.append(f"- Window size: `{args.window_sec:.1f}s`, step `{args.window_step_sec:.1f}s`")
    lines.append(f"- Semantic model: `{args.qwen_model}`")
    lines.append(f"- Coaching model: `{args.coach_model}`")
    lines.append(f"- Selected clips: `{len(rows)}`")
    lines.append("")

    if tracker_df.empty:
        lines.append("_No clips have been processed yet._")
        lines.append("")
        summary_path.write_text("\n".join(lines), encoding="utf-8")
        return summary_path

    status_counts = tracker_df["run_status"].value_counts().rename_axis("run_status").reset_index(name="count")
    lines.append("## Status Counts")
    lines.append("")
    lines.append(markdown_table(status_counts))
    lines.append("")

    success_df = tracker_df[tracker_df["run_status"] == "ok"].copy()
    if not success_df.empty:
        numeric_columns = ["overall_score", "audience_score", "alertness_score", "top_action_count"]
        for column in numeric_columns:
            success_df[column] = pd.to_numeric(success_df[column], errors="coerce")

        stats_rows = []
        for column in ("overall_score", "audience_score", "alertness_score"):
            series = success_df[column].dropna()
            if not series.empty:
                stats_rows.append(
                    {
                        "metric": column,
                        "count": int(series.count()),
                        "mean": round(float(series.mean()), 2),
                        "min": round(float(series.min()), 2),
                        "max": round(float(series.max()), 2),
                    }
                )
        if stats_rows:
            lines.append("## Score Summary")
            lines.append("")
            lines.append(markdown_table(pd.DataFrame(stats_rows)))
            lines.append("")

        top_df = success_df.sort_values("overall_score", ascending=False).head(args.report_top_n).copy()
        top_df["title"] = top_df["title"].map(lambda value: shorten_text(value, 72))
        lines.append(f"## Top {min(args.report_top_n, len(top_df))}")
        lines.append("")
        lines.append(markdown_table(top_df[["clip_id", "overall_score", "coaching_mode", "top_action_count", "title"]]))
        lines.append("")

        bottom_df = success_df.sort_values("overall_score", ascending=True).head(args.report_top_n).copy()
        bottom_df["title"] = bottom_df["title"].map(lambda value: shorten_text(value, 72))
        lines.append(f"## Bottom {min(args.report_top_n, len(bottom_df))}")
        lines.append("")
        lines.append(markdown_table(bottom_df[["clip_id", "overall_score", "coaching_mode", "top_action_count", "title"]]))
        lines.append("")

        tracker_view = success_df[
            ["clip_id", "semantic_status", "coaching_mode", "top_action_count", "confidence_note", "reliability"]
        ].copy()
        tracker_view["confidence_note"] = tracker_view["confidence_note"].map(lambda value: shorten_text(value, 96))
        tracker_view["reliability"] = tracker_view["reliability"].map(lambda value: shorten_text(value, 96))
        lines.append("## Completed Clip Tracker")
        lines.append("")
        lines.append(markdown_table(tracker_view))
        lines.append("")

    failed_df = tracker_df[tracker_df["run_status"] != "ok"].copy()
    if not failed_df.empty:
        failed_df["error"] = failed_df["error"].map(lambda value: shorten_text(value, 120))
        lines.append("## Failures")
        lines.append("")
        lines.append(markdown_table(failed_df[["clip_id", "error"]]))
        lines.append("")

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


def main() -> None:
    args = parse_args()
    batch_dir = ensure_dir(_batch_dir(args))
    manifest_path = batch_dir / "local_clip_manifest.csv"
    ensure_dir(batch_dir / "reports")
    ensure_dir(args.runs_root)

    register_local_clips(
        source_dir=args.source_dir,
        manifest_out=manifest_path,
        clips_root=args.clips_root,
        copy_mode=args.copy_clips,
        goldset_count=args.goldset_count,
    )

    manifest_df = load_manifest(manifest_path)
    selection = select_manifest_rows(
        manifest_df,
        clip_ids=args.clip_ids,
        priority_tiers=args.priority_tiers,
        goldset_only=args.goldset_only,
        limit=args.limit,
    )
    selection.to_csv(batch_dir / "selected_manifest.csv", index=False)
    (batch_dir / "batch_parameters.json").write_text(
        json.dumps(
            {
                "source_dir": str(args.source_dir),
                "clips_root": str(args.clips_root),
                "runs_root": str(args.runs_root),
                "analysis_fps": args.analysis_fps,
                "window_sec": args.window_sec,
                "window_step_sec": args.window_step_sec,
                "qwen_model": args.qwen_model,
                "coach_model": args.coach_model,
                "clip_ids": args.clip_ids,
                "priority_tiers": args.priority_tiers,
                "goldset_only": args.goldset_only,
                "limit": args.limit,
                "selection_count": len(selection),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    try:
        from nonverbal_eval.app_service import run_teacher_evaluation
    except Exception as exc:
        raise RuntimeError(
            "Could not import the long evaluation pipeline. Install the evaluation environment "
            "from requirements_eval.txt before running this batch script."
        ) from exc

    tracker_rows: list[dict[str, Any]] = []
    for _, row in selection.iterrows():
        row_data = row.to_dict()
        clip_id = str(row_data["clip_id"])
        clip_path = args.clips_root / clip_id / "clip.mp4"
        report_dir = _report_dir(batch_dir, clip_id)
        copied_artifacts: dict[str, str] = {}
        run_result: dict[str, Any] | None = None
        error: Exception | None = None

        try:
            run_result = run_teacher_evaluation(
                video=clip_path,
                output_root=args.runs_root / clip_id,
                start_sec=0.0,
                duration_sec=0.0,
                analysis_fps=args.analysis_fps,
                window_sec=args.window_sec,
                window_step_sec=args.window_step_sec,
                keyframe_offset_sec=-1.0,
                enable_semantic=True,
                semantic_sample_interval_sec=6.0,
                semantic_max_samples=8,
                disable_qwen=False,
                qwen_model=args.qwen_model,
                disable_sam2=True,
                enable_coaching=True,
                coach_model=args.coach_model,
                coach_fallback_template_only=False,
            )
            coaching_artifacts = (run_result.get("coaching_payload") or {}).get("artifacts") or {}
            semantic_artifacts = (run_result.get("semantic_payload") or {}).get("artifacts") or {}
            copied_artifacts["coaching_report_md"] = _copy_if_exists(
                coaching_artifacts.get("report_md"),
                report_dir / "teacher_coaching_report.md",
            )
            copied_artifacts["coaching_report_json"] = _copy_if_exists(
                coaching_artifacts.get("report_json"),
                report_dir / "teacher_coaching_report.json",
            )
            copied_artifacts["coaching_report_pdf"] = _copy_if_exists(
                coaching_artifacts.get("report_pdf"),
                report_dir / "teacher_coaching_report.pdf",
            )
            copied_artifacts["semantic_summary_md"] = _copy_if_exists(
                semantic_artifacts.get("summary_md"),
                report_dir / "semantic_summary.md",
            )
            copied_artifacts["semantic_summary_json"] = _copy_if_exists(
                semantic_artifacts.get("summary_json"),
                report_dir / "semantic_summary.json",
            )
            if args.include_summary_artifacts:
                copied_artifacts["summary_md"] = _copy_if_exists(
                    run_result["artifacts"].get("summary_md"),
                    report_dir / "summary_full.md",
                )
                copied_artifacts["summary_json"] = _copy_if_exists(
                    run_result["artifacts"].get("summary_json"),
                    report_dir / "summary_full.json",
                )
            print(f"{clip_id}: ok -> {run_result['run_dir']}")
        except Exception as exc:
            error = exc
            print(f"{clip_id}: failed -> {exc}")

        tracker_rows.append(
            _tracker_row(
                row_data,
                clip_path=clip_path,
                run_result=run_result,
                error=error,
                copied_artifacts=copied_artifacts,
            )
        )
        _write_tracker_files(batch_dir, tracker_rows)
        _write_batch_summary(batch_dir, tracker_rows, args)

    tracker_csv, tracker_json = _write_tracker_files(batch_dir, tracker_rows)
    summary_path = _write_batch_summary(batch_dir, tracker_rows, args)
    print(f"Batch directory: {batch_dir}")
    print(f"Tracker CSV: {tracker_csv}")
    print(f"Tracker JSON: {tracker_json}")
    print(f"Batch summary: {summary_path}")


if __name__ == "__main__":
    main()
