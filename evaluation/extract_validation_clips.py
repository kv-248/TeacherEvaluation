from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from validation_tooling import (
    CLIPS_ROOT,
    VIDEOS_ROOT,
    add_manifest_args,
    add_selection_args,
    ensure_dir,
    extract_segment_opencv,
    load_manifest,
    select_manifest_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract one 60s clip per validation video at 12 fps using OpenCV.")
    add_manifest_args(parser)
    add_selection_args(parser)
    parser.add_argument("--source-root", type=Path, default=VIDEOS_ROOT, help="Directory that contains the downloaded per-clip source videos.")
    parser.add_argument("--output-root", type=Path, default=CLIPS_ROOT, help="Directory that will contain the extracted validation clips.")
    parser.add_argument("--duration-sec", type=float, default=60.0, help="Clip duration in seconds.")
    parser.add_argument("--target-fps", type=float, default=12.0, help="FPS used when writing the extracted clip.")
    parser.add_argument("--start-offset-sec", type=float, default=0.0, help="Additional offset applied to start_hint_sec before extraction.")
    parser.add_argument("--center-on-hint", action="store_true", help="Center the requested duration on start_hint_sec instead of starting there.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing extracted clips.")
    return parser.parse_args()


def _find_source_video(source_dir: Path) -> Path:
    candidates = [
        path
        for path in source_dir.glob("source.*")
        if path.is_file() and path.suffix not in {".json", ".part"}
    ]
    if not candidates:
        raise RuntimeError(f"No downloaded source video was found in {source_dir}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def main() -> None:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    selected = select_manifest_rows(
        manifest,
        clip_ids=args.clip_ids,
        priority_tiers=args.priority_tiers,
        goldset_only=args.goldset_only,
        limit=args.limit,
    )

    source_root = ensure_dir(args.source_root)
    output_root = ensure_dir(args.output_root)
    rows: list[dict[str, object]] = []

    for _, row in selected.iterrows():
        row_data = row.to_dict()
        clip_id = str(row_data["clip_id"])
        source_dir = source_root / clip_id
        clip_dir = ensure_dir(output_root / clip_id)
        clip_path = clip_dir / "clip.mp4"
        try:
            source_video = _find_source_video(source_dir)
            start_sec = float(row_data["start_hint_sec"])
            if args.center_on_hint:
                start_sec -= args.duration_sec / 2.0
            start_sec += args.start_offset_sec

            extract_result = extract_segment_opencv(
                source_video=source_video,
                clip_path=clip_path,
                start_sec=start_sec,
                duration_sec=args.duration_sec,
                target_fps=args.target_fps,
                overwrite=args.overwrite,
            )
            rows.append(
                {
                    **row_data,
                    "status": extract_result["status"],
                    "source_video_path": extract_result["source_video"],
                    "clip_path": extract_result["clip_path"],
                    "start_sec_used": extract_result["start_sec"],
                    "duration_sec_requested": extract_result["duration_sec_requested"],
                    "duration_sec_actual": extract_result["duration_sec_actual"],
                    "target_fps": extract_result["target_fps"],
                    "source_fps": extract_result["source_fps"],
                    "frames_written": extract_result["frames_written"],
                    "error": "",
                }
            )
            print(f"{clip_id}: extracted -> {clip_path}")
        except Exception as exc:  # pragma: no cover - exercised in real failures
            rows.append(
                {
                    **row_data,
                    "status": "failed",
                    "source_video_path": str(source_dir),
                    "clip_path": str(clip_path),
                    "start_sec_used": "",
                    "duration_sec_requested": args.duration_sec,
                    "duration_sec_actual": "",
                    "target_fps": args.target_fps,
                    "source_fps": "",
                    "frames_written": "",
                    "error": str(exc),
                }
            )
            print(f"{clip_id}: failed -> {exc}")

    results = pd.DataFrame(rows)
    results_csv = output_root / "extract_results.csv"
    results.to_csv(results_csv, index=False)
    print(f"Extraction results: {results_csv}")
    print(f"Processed {len(results)} selected rows from {args.manifest}")


if __name__ == "__main__":
    main()

