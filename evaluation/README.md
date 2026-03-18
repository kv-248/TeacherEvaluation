# Validation Tooling

This directory contains the batch-validation workflow for `reviewed_validation_manifest.csv`.
That reviewed manifest is now the active default for all batch tooling in this directory. The original `validation_manifest.csv` stays in place and remains available through an explicit `--manifest` override.
The tools keep downloaded media and generated runs under `evaluation/local_data/`, which is already ignored by the repo-level `.gitignore`.

## Manifest Workflow

- Default behavior: batch scripts use `evaluation/reviewed_validation_manifest.csv`.
- Override behavior: pass `--manifest /workspace/TeacherEvaluation/evaluation/validation_manifest.csv` to target the original manifest, or any other manifest copy.
- The reviewed manifest is the curated set documented in `reviewed_validation_notes.md`.

## Directory Layout

- `evaluation/local_data/videos/<clip_id>/source.*` - downloaded source video for each manifest row
- `evaluation/local_data/videos/download_results.csv` - download status log
- `evaluation/local_data/videos/<clip_id>/source_download.json` - downloader metadata for the source file
- `evaluation/local_data/clips/<clip_id>/clip.mp4` - 60s validation clip extracted at 12 fps with OpenCV
- `evaluation/local_data/clips/<clip_id>/clip.json` - extraction metadata for the clip
- `evaluation/local_data/clips/extract_results.csv` - extraction status log
- `evaluation/local_data/runs/<clip_id>/run_<timestamp>/...` - long-run evaluation artifacts from `nonverbal_eval.app_service`
- `evaluation/local_data/batches/batch_<timestamp>/batch_results.csv` - row-level batch output
- `evaluation/local_data/batches/batch_<timestamp>/batch_summary.md` - markdown summary for the batch

## Scripts

### Register pre-cut local clips

```bash
python evaluation/register_local_clips.py --source-dir /workspace/clips
```

This is the fastest way to build a local validation pool when one-minute clips already exist on disk. The script creates `clip.mp4` symlinks under `evaluation/local_data/clips/` and writes a compatible manifest to `evaluation/local_data/local_clip_manifest.csv`.

### Download source videos

```bash
python evaluation/download_validation_videos.py --goldset-only
```

Downloads each selected manifest row with `yt-dlp` when it is available. If `yt-dlp` is missing, the script exits with a clear install message.

### Extract 60s clips

```bash
python evaluation/extract_validation_clips.py --goldset-only
```

Extracts one 60-second clip per downloaded source video at 12 fps using OpenCV only. The default start point is `start_hint_sec`; use `--center-on-hint` if you want the hint positioned near the middle of the clip.

### Run the long evaluation batch

```bash
python evaluation/run_validation_batch.py --goldset-only
```

Runs the existing long evaluation pipeline over the extracted clips, then writes `batch_results.csv` and `batch_summary.md` in the batch output directory. You can filter the manifest with `--clip-ids`, `--priority-tiers`, `--goldset-only`, and `--limit`. If you need the original manifest instead of the reviewed default, pass `--manifest /workspace/TeacherEvaluation/evaluation/validation_manifest.csv`.

### Run a tracked Gemini Flash batch over local clips

```bash
export GEMINI_API_KEY=your_key_here
python evaluation/run_local_clips_gemini_batch.py --source-dir /workspace/clips --limit 2
```

This path is intended for the current Gemini-backed local validation workflow. It registers `/workspace/clips` into the existing `evaluation/local_data/clips/` symlink structure, runs semantic review and coaching with `gemini-2.5-flash`, stores full long-run outputs under `evaluation/local_data/runs/gemini_flash_local/`, and copies only lightweight report artifacts into a tracked batch directory under `evaluation/runtime_batches/`.

## Expected Order

1. Download videos.
2. Extract validation clips.
3. Run the long evaluation batch.
