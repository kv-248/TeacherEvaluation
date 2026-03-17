from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import cv2
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REVIEWED_MANIFEST_PATH = REPO_ROOT / "evaluation" / "reviewed_validation_manifest.csv"
ORIGINAL_MANIFEST_PATH = REPO_ROOT / "evaluation" / "validation_manifest.csv"
MANIFEST_PATH = REVIEWED_MANIFEST_PATH
LOCAL_DATA_ROOT = REPO_ROOT / "evaluation" / "local_data"
VIDEOS_ROOT = LOCAL_DATA_ROOT / "videos"
CLIPS_ROOT = LOCAL_DATA_ROOT / "clips"
RUNS_ROOT = LOCAL_DATA_ROOT / "runs"
BATCHES_ROOT = LOCAL_DATA_ROOT / "batches"

REQUIRED_MANIFEST_COLUMNS = {
    "clip_id",
    "title",
    "url",
    "channel",
    "duration_sec",
    "selection_reason",
    "priority_tier",
    "start_hint_sec",
    "extraction_policy",
    "notes",
    "goldset_candidate",
}


def timestamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> pd.DataFrame:
    df = pd.read_csv(manifest_path)
    missing = sorted(REQUIRED_MANIFEST_COLUMNS.difference(df.columns))
    if missing:
        raise RuntimeError(f"Manifest is missing required columns: {missing}")
    if df["clip_id"].duplicated().any():
        dups = df.loc[df["clip_id"].duplicated(), "clip_id"].tolist()
        raise RuntimeError(f"Manifest contains duplicate clip_id values: {dups}")
    df = df.copy()
    df["manifest_index"] = range(len(df))
    return df


def _parse_csv_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    parts = [item.strip() for item in value.split(",")]
    cleaned = [item for item in parts if item]
    return cleaned or None


def add_manifest_args(parser: Any) -> None:
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Path to the active validation manifest. Defaults to reviewed_validation_manifest.csv.",
    )


def add_selection_args(parser: Any) -> None:
    parser.add_argument("--clip-ids", type=str, default="", help="Comma-separated clip_id values to process.")
    parser.add_argument("--priority-tiers", type=str, default="", help="Comma-separated priority tiers to process.")
    parser.add_argument("--goldset-only", action="store_true", help="Restrict processing to goldset_candidate rows.")
    parser.add_argument("--limit", type=int, default=0, help="Limit the selection to the first N rows after filtering.")


def select_manifest_rows(
    df: pd.DataFrame,
    *,
    clip_ids: str | None = None,
    priority_tiers: str | None = None,
    goldset_only: bool = False,
    limit: int = 0,
) -> pd.DataFrame:
    selected = df.copy()
    requested_ids = _parse_csv_list(clip_ids)
    requested_tiers = _parse_csv_list(priority_tiers)

    if goldset_only:
        selected = selected[selected["goldset_candidate"].astype(bool)]
    if requested_tiers:
        normalized_tiers = {tier.upper() for tier in requested_tiers}
        selected = selected[selected["priority_tier"].astype(str).str.upper().isin(normalized_tiers)]
    if requested_ids:
        order = {clip_id: index for index, clip_id in enumerate(requested_ids)}
        missing = [clip_id for clip_id in requested_ids if clip_id not in set(selected["clip_id"].astype(str))]
        if missing:
            raise RuntimeError(f"Requested clip_id values were not found in the selection: {missing}")
        selected = selected[selected["clip_id"].astype(str).isin(order)].copy()
        selected["_selection_order"] = selected["clip_id"].astype(str).map(order)
        selected = selected.sort_values(["_selection_order", "manifest_index"]).drop(columns=["_selection_order"])

    if limit and limit > 0:
        selected = selected.head(limit)

    if selected.empty:
        raise RuntimeError("The requested manifest selection is empty.")

    return selected.reset_index(drop=True)


def escape_markdown(text: Any) -> str:
    if pd.isna(text):
        return ""
    return str(text).replace("|", "\\|").replace("\n", " ")


def shorten_text(text: Any, max_length: int = 80) -> str:
    if pd.isna(text):
        return ""
    value = str(text).replace("\n", " ").strip()
    if len(value) <= max_length:
        return value
    return value[: max(0, max_length - 1)].rstrip() + "…"


def markdown_table(df: pd.DataFrame, *, max_text_length: int = 80) -> str:
    if df.empty:
        return "_No rows._"
    headers = [escape_markdown(column) for column in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        values: list[str] = []
        for value in row.tolist():
            if isinstance(value, float):
                if pd.isna(value):
                    values.append("")
                else:
                    values.append(f"{value:.2f}")
            elif isinstance(value, (int, bool)):
                values.append(str(value))
            else:
                values.append(escape_markdown(shorten_text(value, max_text_length)))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_yt_dlp_command() -> list[str]:
    exe = shutil.which("yt-dlp")
    if exe:
        return [exe]
    try:
        import yt_dlp  # noqa: F401
    except Exception as exc:  # pragma: no cover - handled in CLI paths
        raise RuntimeError(
            "yt-dlp is not available. Install it with `pip install -r requirements_eval.txt` "
            "or `pip install yt-dlp`."
        ) from exc
    return [sys.executable, "-m", "yt_dlp"]


def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _existing_download(clip_dir: Path) -> Path | None:
    candidates = [
        path
        for path in clip_dir.glob("source.*")
        if path.is_file() and path.suffix not in {".json", ".part"}
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def download_source_video(
    *,
    clip_id: str,
    url: str,
    output_root: Path = VIDEOS_ROOT,
    overwrite: bool = False,
) -> dict[str, Any]:
    clip_dir = ensure_dir(output_root / clip_id)
    existing = _existing_download(clip_dir)
    if existing and not overwrite:
        metadata_path = clip_dir / "source_download.json"
        metadata = read_json(metadata_path) if metadata_path.exists() else {}
        return {
            "clip_id": clip_id,
            "url": url,
            "status": metadata.get("status", "exists"),
            "download_mode": metadata.get("download_mode", "existing"),
            "downloaded_path": str(existing),
            "output_dir": str(clip_dir),
        }

    if overwrite:
        for path in clip_dir.glob("source.*"):
            if path.is_file() and path.suffix != ".part":
                path.unlink()

    command = resolve_yt_dlp_command()
    output_template = str(clip_dir / "source.%(ext)s")
    ffmpeg_available = has_ffmpeg()
    preferred_formats = []
    if ffmpeg_available:
        preferred_formats.append(("merged", "bestvideo*+bestaudio/best"))
    preferred_formats.append(("single_file", "best[ext=mp4]/best"))

    last_error: str | None = None
    for mode_name, format_selector in preferred_formats:
        args = command + [
            "--no-playlist",
            "--no-warnings",
            "--newline",
            "--restrict-filenames",
            "--no-progress",
            "--format",
            format_selector,
            "-o",
            output_template,
            url,
        ]
        if mode_name == "merged" and ffmpeg_available:
            args.extend(["--merge-output-format", "mp4"])

        completed = subprocess.run(args, capture_output=True, text=True)
        if completed.returncode == 0:
            downloaded = _existing_download(clip_dir)
            if downloaded is None:
                raise RuntimeError(
                    f"yt-dlp reported success for {url}, but no source file was found in {clip_dir}."
                )
            metadata = {
                "clip_id": clip_id,
                "url": url,
                "status": "downloaded",
                "download_mode": mode_name,
                "downloaded_path": str(downloaded),
                "output_dir": str(clip_dir),
                "timestamp_utc": timestamp_utc(),
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
            }
            write_json(clip_dir / "source_download.json", metadata)
            return metadata
        last_error = (
            f"yt-dlp failed in {mode_name} mode for {clip_id}.\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
        for path in clip_dir.glob("source.*"):
            if path.is_file() and path.suffix != ".part":
                path.unlink()

    raise RuntimeError(last_error or f"Failed to download {url}")


def _video_info(video_path: Path) -> dict[str, Any]:
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
        "width": width,
        "height": height,
        "duration_sec": frames / fps if fps else 0.0,
    }


def extract_segment_opencv(
    *,
    source_video: Path,
    clip_path: Path,
    start_sec: float,
    duration_sec: float = 60.0,
    target_fps: float = 12.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    if clip_path.exists() and not overwrite:
        metadata_path = clip_path.with_suffix(".json")
        if metadata_path.exists():
            metadata = read_json(metadata_path)
            return metadata
        info = _video_info(clip_path)
        return {
            "status": "exists",
            "source_video": str(source_video),
            "clip_path": str(clip_path),
            "start_sec": start_sec,
            "duration_sec_requested": duration_sec,
            "duration_sec_actual": info["duration_sec"],
            "target_fps": target_fps,
            "source_fps": info["fps"],
            "frames_written": info["frames"],
        }

    source_info = _video_info(source_video)
    source_fps = float(source_info["fps"])
    source_duration = float(source_info["duration_sec"])
    if source_duration <= 0:
        raise RuntimeError(f"Video has zero duration: {source_video}")

    clip_start_sec = max(0.0, min(start_sec, max(source_duration - duration_sec, 0.0)))
    clip_end_sec = min(clip_start_sec + duration_sec, source_duration)
    effective_fps = float(target_fps if target_fps > 0 else source_fps)
    if effective_fps <= 0:
        raise RuntimeError("Target FPS must be greater than zero.")

    cap = cv2.VideoCapture(str(source_video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open source video for extraction: {source_video}")
    cap.set(cv2.CAP_PROP_POS_MSEC, clip_start_sec * 1000.0)

    clip_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(clip_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        effective_fps,
        (int(source_info["width"]), int(source_info["height"])),
    )

    next_write_sec = clip_start_sec
    tolerance = 0.5 / max(source_fps, 1.0)
    frames_written = 0

    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            now_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            if now_sec > clip_end_sec + tolerance:
                break
            if now_sec + tolerance < next_write_sec:
                continue
            writer.write(frame)
            frames_written += 1
            next_write_sec += 1.0 / effective_fps
    finally:
        cap.release()
        writer.release()

    if frames_written <= 0:
        raise RuntimeError(f"No frames were written while extracting {source_video} -> {clip_path}")

    output_info = _video_info(clip_path)
    metadata = {
        "status": "extracted",
        "source_video": str(source_video),
        "clip_path": str(clip_path),
        "start_sec": clip_start_sec,
        "duration_sec_requested": duration_sec,
        "duration_sec_actual": output_info["duration_sec"],
        "target_fps": effective_fps,
        "source_fps": source_fps,
        "frames_written": frames_written,
        "width": output_info["width"],
        "height": output_info["height"],
        "timestamp_utc": timestamp_utc(),
    }
    write_json(clip_path.with_suffix(".json"), metadata)
    return metadata
