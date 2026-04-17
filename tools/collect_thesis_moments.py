from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _timestamp_token(timestamp: str) -> str:
    if "-" not in timestamp:
        return ""
    start_text, end_text = [part.strip() for part in timestamp.split("-", 1)]
    return start_text.replace(":", "") + "_" + end_text.replace(":", "")


def _moment_image_path(run_dir: Path, timestamp: str, index: int) -> Path | None:
    moments_dir = run_dir / "coaching_moments"
    if not moments_dir.exists():
        return None
    token = _timestamp_token(timestamp)
    if token:
        candidates = sorted(moments_dir.glob(f"moment_*_{token}.jpg"))
    else:
        candidates = []
    if not candidates:
        candidates = sorted(moments_dir.glob(f"moment_{index:02d}_*.jpg"))
    for candidate in candidates:
        lower = candidate.name.lower()
        if "_qwen_" not in lower and "_semantic_" not in lower:
            return candidate
    return candidates[0] if candidates else None


def _clip_rows(run_dir: Path) -> list[dict[str, Any]]:
    report_path = run_dir / "teacher_coaching_report.json"
    if not report_path.exists():
        return []

    evidence_path = run_dir / "coaching_evidence.json"
    report = _load_json(report_path)
    evidence = _load_json(evidence_path) if evidence_path.exists() else {}

    clip_id = run_dir.parent.name
    batch_root = run_dir.parent.parent.name
    source = report.get("source", {})
    overall_profile = evidence.get("overall_profile", {})
    review_windows = evidence.get("review_windows", [])
    review_by_label = {
        str(window.get("window_label", "")).strip(): window
        for window in review_windows
        if isinstance(window, dict) and window.get("window_label")
    }

    rows: list[dict[str, Any]] = []
    for index, moment in enumerate(report.get("evidence_moments", []), start=1):
        timestamp = str(moment.get("timestamp", "")).strip()
        review_window = review_by_label.get(timestamp, {})
        image_path = _moment_image_path(run_dir, timestamp, index)
        rows.append(
            {
                "batch_root": batch_root,
                "clip_id": clip_id,
                "run_dir": str(run_dir),
                "source_mode": source.get("mode", ""),
                "source_model": source.get("model", ""),
                "clip_reliability": overall_profile.get("reliability", ""),
                "board_context_review_window_count": overall_profile.get("board_context_review_window_count", ""),
                "timestamp": timestamp,
                "headline": moment.get("headline", ""),
                "observed_behavior": moment.get("observed_behavior", ""),
                "metric_evidence": moment.get("metric_evidence", ""),
                "semantic_interpretation": moment.get("semantic_interpretation", ""),
                "coaching_implication": moment.get("coaching_implication", ""),
                "window_primary_tag": review_window.get("primary_tag", ""),
                "window_reason": review_window.get("reason", ""),
                "window_priority": review_window.get("priority", ""),
                "window_board_context": review_window.get("board_context", ""),
                "window_start_sec": review_window.get("window_start_sec", ""),
                "window_end_sec": review_window.get("window_end_sec", ""),
                "window_overall_score": (
                    review_window.get("metrics", {}).get("overall_score", "")
                    if isinstance(review_window.get("metrics"), dict)
                    else ""
                ),
                "moment_image_path": str(image_path) if image_path else "",
                "report_json_path": str(report_path),
                "report_md_path": str(run_dir / "teacher_coaching_report.md"),
                "manual_selected": "",
                "manual_accuracy": "",
                "manual_thesis_value": "",
                "manual_notes": "",
            }
        )
    return rows


def _collect_rows(roots: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for report_path in sorted(root.glob("*/run_*/teacher_coaching_report.json")):
            rows.extend(_clip_rows(report_path.parent))
    return rows


def _write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "batch_root",
        "clip_id",
        "run_dir",
        "source_mode",
        "source_model",
        "clip_reliability",
        "board_context_review_window_count",
        "timestamp",
        "headline",
        "observed_behavior",
        "metric_evidence",
        "semantic_interpretation",
        "coaching_implication",
        "window_primary_tag",
        "window_reason",
        "window_priority",
        "window_board_context",
        "window_start_sec",
        "window_end_sec",
        "window_overall_score",
        "moment_image_path",
        "report_json_path",
        "report_md_path",
        "manual_selected",
        "manual_accuracy",
        "manual_thesis_value",
        "manual_notes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Thesis Moment Review Sheet")
    lines.append("")
    lines.append("This sheet aggregates `evidence_moments` across the selected evaluation runs.")
    lines.append("Use the blank manual columns in the CSV to mark which moments are accurate enough for the thesis and why.")
    lines.append("")
    lines.append("## Candidate Table")
    lines.append("")
    lines.append("| Clip | Timestamp | Headline | Reliability | Board Context | Primary Tag | Image |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        image_rel = ""
        if row["moment_image_path"]:
            image_rel = Path(os.path.relpath(row["moment_image_path"], output_path.parent)).as_posix()
        image_cell = f"[image]({image_rel})" if image_rel else ""
        lines.append(
            f"| `{row['clip_id']}` | `{row['timestamp']}` | {row['headline']} | `{row['clip_reliability']}` | "
            f"`{row['window_board_context']}` | `{row['window_primary_tag']}` | {image_cell} |"
        )
    lines.append("")
    lines.append("## Detailed Review")
    lines.append("")

    previous_clip = None
    for row in rows:
        clip_id = row["clip_id"]
        if clip_id != previous_clip:
            lines.append(f"### `{clip_id}`")
            lines.append("")
            previous_clip = clip_id
        lines.append(f"#### `{row['timestamp']}` — {row['headline']}")
        lines.append("")
        lines.append(f"- Batch root: `{row['batch_root']}`")
        lines.append(f"- Source: `{row['source_mode']}` via `{row['source_model']}`")
        lines.append(f"- Reliability: `{row['clip_reliability']}`")
        lines.append(f"- Board context: `{row['window_board_context']}`")
        lines.append(f"- Primary tag: `{row['window_primary_tag']}`")
        lines.append(f"- Observed behavior: {row['observed_behavior']}")
        lines.append(f"- Metric evidence: {row['metric_evidence']}")
        lines.append(f"- Semantic interpretation: {row['semantic_interpretation']}")
        lines.append(f"- Coaching implication: {row['coaching_implication']}")
        if row["moment_image_path"]:
            image_path = Path(row["moment_image_path"])
            image_rel = Path(os.path.relpath(image_path, output_path.parent)).as_posix()
            lines.append(f"- Image: [{image_path.name}]({image_rel})")
            lines.append("")
            lines.append(f"![{clip_id} {row['timestamp']}]({image_rel})")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate evidence moments from teacher coaching runs into a thesis review sheet.")
    parser.add_argument(
        "--roots",
        type=Path,
        nargs="+",
        required=True,
        help="One or more batch roots, such as local_data/docker_test_outputs/batch_eval_v2.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        required=True,
        help="Destination CSV for manual cherry-pick review.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        required=True,
        help="Destination markdown gallery for visual review.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = _collect_rows(args.roots)
    rows.sort(key=lambda row: (row["clip_id"], row["timestamp"]))
    _write_csv(rows, args.output_csv)
    _write_markdown(rows, args.output_md)
    print(f"rows={len(rows)}")
    print(args.output_csv)
    print(args.output_md)


if __name__ == "__main__":
    main()
