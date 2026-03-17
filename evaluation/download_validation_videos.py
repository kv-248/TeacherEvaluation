from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from validation_tooling import (
    VIDEOS_ROOT,
    add_manifest_args,
    add_selection_args,
    download_source_video,
    ensure_dir,
    load_manifest,
    select_manifest_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download validation-source videos into evaluation/local_data/videos.")
    add_manifest_args(parser)
    add_selection_args(parser)
    parser.add_argument("--output-root", type=Path, default=VIDEOS_ROOT, help="Directory that will contain per-clip video folders.")
    parser.add_argument("--overwrite", action="store_true", help="Redownload files even when a source file already exists.")
    return parser.parse_args()


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

    output_root = ensure_dir(args.output_root)
    rows: list[dict[str, object]] = []

    for _, row in selected.iterrows():
        row_data = row.to_dict()
        clip_id = str(row_data["clip_id"])
        try:
            download_result = download_source_video(
                clip_id=clip_id,
                url=str(row_data["url"]),
                output_root=output_root,
                overwrite=args.overwrite,
            )
            rows.append(
                {
                    **row_data,
                    "status": download_result["status"],
                    "download_mode": download_result["download_mode"],
                    "downloaded_path": download_result["downloaded_path"],
                    "download_output_dir": download_result["output_dir"],
                    "error": "",
                }
            )
            print(f"{clip_id}: {download_result['status']} -> {download_result['downloaded_path']}")
        except Exception as exc:  # pragma: no cover - exercised in real failures
            rows.append(
                {
                    **row_data,
                    "status": "failed",
                    "download_mode": "",
                    "downloaded_path": "",
                    "download_output_dir": str(output_root / clip_id),
                    "error": str(exc),
                }
            )
            print(f"{clip_id}: failed -> {exc}")

    results = pd.DataFrame(rows)
    results_csv = output_root / "download_results.csv"
    results.to_csv(results_csv, index=False)
    print(f"Download results: {results_csv}")
    print(f"Processed {len(results)} selected rows from {args.manifest}")


if __name__ == "__main__":
    main()
