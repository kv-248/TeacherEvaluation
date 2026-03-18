from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2

from validation_tooling import CLIPS_ROOT, ensure_dir


VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Register pre-cut local clips into evaluation/local_data/clips and generate a matching manifest."
    )
    parser.add_argument("--source-dir", type=Path, default=Path("/workspace/clips"), help="Directory that contains local validation clips.")
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=Path("/workspace/TeacherEvaluation/evaluation/local_data/local_clip_manifest.csv"),
        help="Output CSV manifest path.",
    )
    parser.add_argument(
        "--clips-root",
        type=Path,
        default=CLIPS_ROOT,
        help="Target root for clip.mp4 symlinks or copies.",
    )
    parser.add_argument("--copy", action="store_true", help="Copy clips instead of creating symlinks.")
    parser.add_argument(
        "--goldset-count",
        type=int,
        default=12,
        help="Mark the first N clips as goldset_candidate in the generated manifest.",
    )
    return parser.parse_args()


def _video_info(path: Path) -> dict[str, float | int]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open local clip: {path}")
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


def _title_from_stem(stem: str) -> str:
    return stem.replace("_", " ")


def _channel_from_stem(stem: str) -> str:
    parts = stem.split("_")
    if not parts:
        return "local"
    if len(parts) >= 2 and parts[0] == "mit" and parts[1] == "ocw":
        return "MIT OCW"
    if len(parts) >= 2 and parts[0] == "stanford":
        return "Stanford"
    if len(parts) >= 1 and parts[0] == "yale":
        return "Yale"
    if len(parts) >= 1 and parts[0] == "cs50":
        return "CS50"
    return parts[0].upper()


def _register_clip(source_path: Path, target_path: Path, copy_mode: bool) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists() or target_path.is_symlink():
        target_path.unlink()
    if copy_mode:
        target_path.write_bytes(source_path.read_bytes())
    else:
        target_path.symlink_to(source_path)


def register_local_clips(
    *,
    source_dir: Path,
    manifest_out: Path,
    clips_root: Path = CLIPS_ROOT,
    copy_mode: bool = False,
    goldset_count: int = 12,
) -> list[dict[str, object]]:
    source_dir = source_dir.resolve()
    clips_root = ensure_dir(clips_root)
    ensure_dir(manifest_out.parent)
    clips = [path for path in sorted(source_dir.rglob("*")) if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS]
    if not clips:
        raise RuntimeError(f"No local clips found under {source_dir}")

    rows: list[dict[str, object]] = []
    for index, source_path in enumerate(clips, start=1):
        info = _video_info(source_path)
        clip_id = source_path.stem
        target_dir = clips_root / clip_id
        target_path = target_dir / "clip.mp4"
        _register_clip(source_path, target_path, copy_mode=copy_mode)
        metadata = {
            "status": "registered_local_clip",
            "source_video": str(source_path),
            "clip_path": str(target_path),
            "start_sec": 0.0,
            "duration_sec_requested": float(info["duration_sec"]),
            "duration_sec_actual": float(info["duration_sec"]),
            "target_fps": float(info["fps"]),
            "source_fps": float(info["fps"]),
            "frames_written": int(info["frames"]),
            "width": int(info["width"]),
            "height": int(info["height"]),
            "registration_mode": "copy" if copy_mode else "symlink",
        }
        (target_dir / "clip.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        rows.append(
            {
                "clip_id": clip_id,
                "title": _title_from_stem(clip_id),
                "url": f"file://{source_path}",
                "channel": _channel_from_stem(clip_id),
                "duration_sec": round(float(info["duration_sec"]), 2),
                "selection_reason": "workspace_local_clip",
                "priority_tier": "A" if index <= max(goldset_count, 0) else "B",
                "start_hint_sec": 0.0,
                "extraction_policy": "pre_extracted_60s_clip",
                "notes": "Registered from /workspace/clips for fast validation and frontend debugging.",
                "goldset_candidate": index <= max(goldset_count, 0),
            }
        )

    with manifest_out.resolve().open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return rows


def main() -> None:
    args = parse_args()
    rows = register_local_clips(
        source_dir=args.source_dir,
        manifest_out=args.manifest_out,
        clips_root=args.clips_root,
        copy_mode=args.copy,
        goldset_count=args.goldset_count,
    )

    print(f"Registered {len(rows)} local clips.")
    print(f"Manifest: {args.manifest_out}")
    print(f"Clips root: {args.clips_root}")


if __name__ == "__main__":
    main()
