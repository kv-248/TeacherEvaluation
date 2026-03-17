from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from PIL import Image

from .pipeline import log_event


@dataclass(slots=True)
class SemanticConfig:
    enabled: bool = False
    sample_interval_sec: float = 6.0
    max_samples: int = 8
    qwen_enabled: bool = True
    qwen_model: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    qwen_device: str = "cuda:0"
    qwen_device_map: str | None = None
    qwen_dtype: str = "bfloat16"
    qwen_max_new_tokens: int = 180
    qwen_temperature: float = 0.1
    sam2_enabled: bool = True
    sam2_model_cfg: str | None = None
    sam2_checkpoint: Path | None = None
    sam2_device: str = "cuda:1"


@dataclass(slots=True)
class SemanticArtifacts:
    root_dir: Path
    sampled_frames_dir: Path
    contact_sheet_path: Path
    qwen_annotations_path: Path
    sam2_metrics_path: Path
    summary_json_path: Path
    summary_md_path: Path


@dataclass(slots=True)
class SemanticSample:
    timestamp_sec: float
    reason: str
    image_path: Path
    frame_bgr: np.ndarray
    frame_shape: tuple[int, int, int]


QWEN_PROMPT = """You are reviewing a single frame from a classroom lecture video.
Return JSON only with exactly these keys:
- teacher_focus: one of [audience, board, screen, notes, ambiguous]
- body_action: one of [open_palm_explaining, pointing_board, pointing_screen, writing_board, walking, static_stance, reading_from_notes, ambiguous]
- affect_tone: one of [warm, neutral, tense, ambiguous]
- posture_signal: one of [upright_open, upright_neutral, closed_or_slouched, ambiguous]
- attention_note: short phrase, at most 12 words
- evidence_confidence: one of [low, medium, high]
- rationale: short phrase, at most 20 words
Do not add markdown or explanation outside the JSON object."""

ALLOWED_QWEN_VALUES = {
    "teacher_focus": {"audience", "board", "screen", "notes", "ambiguous"},
    "body_action": {
        "open_palm_explaining",
        "pointing_board",
        "pointing_screen",
        "writing_board",
        "walking",
        "static_stance",
        "reading_from_notes",
        "ambiguous",
    },
    "affect_tone": {"warm", "neutral", "tense", "ambiguous"},
    "posture_signal": {"upright_open", "upright_neutral", "closed_or_slouched", "ambiguous"},
    "evidence_confidence": {"low", "medium", "high"},
}


def build_semantic_artifacts(run_dir: Path) -> SemanticArtifacts:
    root_dir = run_dir / "semantic_extensions"
    sampled_frames_dir = root_dir / "sampled_frames"
    sampled_frames_dir.mkdir(parents=True, exist_ok=True)
    return SemanticArtifacts(
        root_dir=root_dir,
        sampled_frames_dir=sampled_frames_dir,
        contact_sheet_path=root_dir / "semantic_contact_sheet.jpg",
        qwen_annotations_path=root_dir / "qwen_annotations.json",
        sam2_metrics_path=root_dir / "sam2_mask_metrics.json",
        summary_json_path=root_dir / "semantic_summary.json",
        summary_md_path=root_dir / "semantic_summary.md",
    )


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator / denominator)


def _parse_version_tuple(version: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", version)
    return tuple(int(part) for part in parts[:3])


def _version_at_least(version: str, minimum: str) -> bool:
    current = _parse_version_tuple(version)
    baseline = _parse_version_tuple(minimum)
    width = max(len(current), len(baseline))
    current += (0,) * (width - len(current))
    baseline += (0,) * (width - len(baseline))
    return current >= baseline


def _sanitize_short_text(value: Any, max_words: int) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    words = text.split(" ")
    if len(words) > max_words:
        text = " ".join(words[:max_words])
    return text


def _extract_json_blob(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("Empty model output.")
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            text = match.group(0)
    return json.loads(text)


def _choose_timestamps(frame_metrics_df: pd.DataFrame, clip_duration_sec: float, interval_sec: float, max_samples: int) -> list[tuple[float, str]]:
    reason_map: dict[float, list[str]] = {}

    def add_reason(timestamp: float, reason: str) -> None:
        bounded = float(np.clip(timestamp, 0.0, max(clip_duration_sec - 1e-3, 0.0)))
        key = round(bounded, 2)
        if key not in reason_map:
            reason_map[key] = []
        if reason not in reason_map[key]:
            reason_map[key].append(reason)

    add_reason(0.0, "clip_start")
    add_reason(clip_duration_sec / 2.0, "clip_midpoint")
    add_reason(max(clip_duration_sec - 0.25, 0.0), "clip_end")

    if interval_sec > 0:
        current = 0.0
        while current <= clip_duration_sec + 1e-6:
            add_reason(current, "uniform_sample")
            current += interval_sec

    scalar_columns = {
        "gesture_motion": ("peak_gesture_motion", "high"),
        "audience_orientation_score_frame": ("peak_audience_orientation", "high"),
        "smile_proxy": ("peak_smile_proxy", "high"),
        "posture_score_frame": ("peak_posture", "high"),
    }
    for column, (label, mode) in scalar_columns.items():
        if column not in frame_metrics_df.columns or frame_metrics_df[column].dropna().empty:
            continue
        series = frame_metrics_df[column]
        idx = series.idxmax() if mode == "high" else series.idxmin()
        add_reason(float(frame_metrics_df.loc[idx, "timestamp_sec"]), label)

    if "audience_orientation_score_frame" in frame_metrics_df.columns and frame_metrics_df["audience_orientation_score_frame"].dropna().size:
        idx = frame_metrics_df["audience_orientation_score_frame"].idxmin()
        add_reason(float(frame_metrics_df.loc[idx, "timestamp_sec"]), "low_audience_orientation")

    ordered = sorted(reason_map.items(), key=lambda item: item[0])
    merged: list[tuple[float, list[str]]] = []
    for timestamp, reasons in ordered:
        if not merged or abs(timestamp - merged[-1][0]) > max(interval_sec * 0.35, 1.0):
            merged.append((timestamp, list(reasons)))
        else:
            for reason in reasons:
                if reason not in merged[-1][1]:
                    merged[-1][1].append(reason)

    if len(merged) > max_samples:
        indices = np.linspace(0, len(merged) - 1, max_samples, dtype=int)
        merged = [merged[index] for index in sorted(set(indices.tolist()))]

    return [(timestamp, ",".join(reasons)) for timestamp, reasons in merged]


def _extract_frame_at(video_path: Path, timestamp_sec: float) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video for semantic sampling: {video_path}")
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000.0)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not extract frame at {timestamp_sec:.2f}s from {video_path}")
    return frame


def _save_sampled_frames(
    clip_path: Path,
    frame_metrics_df: pd.DataFrame,
    artifacts: SemanticArtifacts,
    config: SemanticConfig,
    events_path: Path,
    clip_duration_sec: float,
) -> list[SemanticSample]:
    selections = _choose_timestamps(frame_metrics_df, clip_duration_sec, config.sample_interval_sec, config.max_samples)
    samples: list[SemanticSample] = []
    for index, (timestamp_sec, reason) in enumerate(selections):
        frame_bgr = _extract_frame_at(clip_path, timestamp_sec)
        image_path = artifacts.sampled_frames_dir / f"frame_{index:02d}_{timestamp_sec:06.2f}s.jpg"
        cv2.imwrite(str(image_path), frame_bgr)
        samples.append(
            SemanticSample(
                timestamp_sec=timestamp_sec,
                reason=reason,
                image_path=image_path,
                frame_bgr=frame_bgr,
                frame_shape=frame_bgr.shape,
            )
        )
    log_event(
        events_path,
        "semantic_samples_selected",
        sample_count=len(samples),
        timestamps_sec=[round(sample.timestamp_sec, 2) for sample in samples],
        reasons=[sample.reason for sample in samples],
    )
    return samples


def _run_qwen(
    samples: list[SemanticSample],
    config: SemanticConfig,
    events_path: Path,
    event_name: str = "semantic_qwen_completed",
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "skipped",
        "reason": "Qwen semantic analysis disabled.",
        "model": config.qwen_model,
        "device": config.qwen_device,
        "device_map": config.qwen_device_map,
        "annotations": [],
        "aggregate": {},
    }
    if not config.qwen_enabled:
        return result

    try:
        import torch
        import transformers as tf
    except Exception as exc:
        result["status"] = "unavailable"
        result["reason"] = f"Missing Qwen dependencies: {type(exc).__name__}: {exc}"
        return result

    try:
        processor_cls = getattr(tf, "AutoProcessor")
        model_cls = None
        for candidate_name in (
            "Qwen2_5_VLForConditionalGeneration",
            "AutoModelForImageTextToText",
            "AutoModelForVision2Seq",
            "AutoModelForCausalLM",
        ):
            if hasattr(tf, candidate_name):
                model_cls = getattr(tf, candidate_name)
                break
        if model_cls is None:
            raise RuntimeError("No compatible transformers vision-language auto-model class was found.")
    except Exception as exc:
        result["status"] = "unavailable"
        result["reason"] = f"Could not resolve transformers Qwen classes: {type(exc).__name__}: {exc}"
        return result

    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    device = config.qwen_device
    torch_dtype = dtype_map.get(config.qwen_dtype.lower(), torch.bfloat16)
    device_map = config.qwen_device_map
    if device.lower() == "auto" and not device_map:
        device_map = "auto"

    def generation_device_for(model: Any, fallback_device: str) -> str:
        hf_device_map = getattr(model, "hf_device_map", None)
        if isinstance(hf_device_map, dict):
            for mapped_device in hf_device_map.values():
                if isinstance(mapped_device, str) and mapped_device not in {"cpu", "disk"}:
                    return mapped_device
        try:
            return str(next(model.parameters()).device)
        except Exception:
            return fallback_device

    try:
        processor = processor_cls.from_pretrained(config.qwen_model, trust_remote_code=True)
        load_kwargs: dict[str, Any] = {
            "dtype": torch_dtype,
            "low_cpu_mem_usage": True,
            "trust_remote_code": True,
        }
        if device_map:
            load_kwargs["device_map"] = device_map
        model = model_cls.from_pretrained(config.qwen_model, **load_kwargs)
        if device_map is None:
            if device.startswith("cuda") and not torch.cuda.is_available():
                device = "cpu"
            model = model.to(device)
        model.eval()
    except Exception as exc:
        result["status"] = "failed"
        result["reason"] = f"Could not load Qwen model: {type(exc).__name__}: {exc}"
        return result

    device_for_inputs = generation_device_for(model, device)

    annotations: list[dict[str, Any]] = []
    try:
        for sample in samples:
            image = Image.open(sample.image_path).convert("RGB")
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": QWEN_PROMPT},
                    ],
                }
            ]
            if hasattr(processor, "apply_chat_template"):
                prompt_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[prompt_text], images=[image], return_tensors="pt")
            else:
                inputs = processor(images=image, text=QWEN_PROMPT, return_tensors="pt")
            model_inputs: dict[str, Any] = {}
            for key, value in inputs.items():
                if hasattr(value, "to"):
                    model_inputs[key] = value.to(device_for_inputs)
                else:
                    model_inputs[key] = value
            with torch.inference_mode():
                generated_ids = model.generate(
                    **model_inputs,
                    do_sample=False if config.qwen_temperature <= 0.0 else True,
                    temperature=max(config.qwen_temperature, 1e-5),
                    max_new_tokens=config.qwen_max_new_tokens,
                )
            prompt_tokens = model_inputs.get("input_ids")
            if prompt_tokens is not None:
                generated_ids = generated_ids[:, prompt_tokens.shape[1] :]
            decoded = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)[0]
            parsed = _extract_json_blob(decoded)
            annotation = {
                "timestamp_sec": sample.timestamp_sec,
                "reason": sample.reason,
                "raw_text": decoded.strip(),
                "teacher_focus": str(parsed.get("teacher_focus", "ambiguous")).strip(),
                "body_action": str(parsed.get("body_action", "ambiguous")).strip(),
                "affect_tone": str(parsed.get("affect_tone", "ambiguous")).strip(),
                "posture_signal": str(parsed.get("posture_signal", "ambiguous")).strip(),
                "attention_note": _sanitize_short_text(parsed.get("attention_note", ""), max_words=12),
                "evidence_confidence": str(parsed.get("evidence_confidence", "medium")).strip(),
                "rationale": _sanitize_short_text(parsed.get("rationale", ""), max_words=20),
            }
            for field, allowed_values in ALLOWED_QWEN_VALUES.items():
                if annotation[field] not in allowed_values:
                    annotation[field] = "ambiguous" if "ambiguous" in allowed_values else "medium"
            annotations.append(annotation)
    except Exception as exc:
        result["status"] = "failed"
        result["reason"] = f"Qwen inference failed: {type(exc).__name__}: {exc}"
        return result
    finally:
        try:
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    focus_counts = pd.Series([row["teacher_focus"] for row in annotations]).value_counts().to_dict()
    action_counts = pd.Series([row["body_action"] for row in annotations]).value_counts().to_dict()
    affect_counts = pd.Series([row["affect_tone"] for row in annotations]).value_counts().to_dict()
    posture_counts = pd.Series([row["posture_signal"] for row in annotations]).value_counts().to_dict()
    annotation_count = max(len(annotations), 1)
    aggregate = {
        "sample_count": len(annotations),
        "audience_focus_ratio": _safe_ratio(focus_counts.get("audience", 0), annotation_count),
        "board_focus_ratio": _safe_ratio(focus_counts.get("board", 0), annotation_count),
        "screen_focus_ratio": _safe_ratio(focus_counts.get("screen", 0), annotation_count),
        "notes_focus_ratio": _safe_ratio(focus_counts.get("notes", 0), annotation_count),
        "open_palm_explaining_ratio": _safe_ratio(action_counts.get("open_palm_explaining", 0), annotation_count),
        "static_stance_ratio": _safe_ratio(action_counts.get("static_stance", 0), annotation_count),
        "pointing_ratio": _safe_ratio(
            action_counts.get("pointing_board", 0) + action_counts.get("pointing_screen", 0), annotation_count
        ),
        "writing_ratio": _safe_ratio(action_counts.get("writing_board", 0), annotation_count),
        "warm_affect_ratio": _safe_ratio(affect_counts.get("warm", 0), annotation_count),
        "tense_affect_ratio": _safe_ratio(affect_counts.get("tense", 0), annotation_count),
        "closed_or_slouched_ratio": _safe_ratio(posture_counts.get("closed_or_slouched", 0), annotation_count),
        "focus_counts": focus_counts,
        "action_counts": action_counts,
        "affect_counts": affect_counts,
        "posture_counts": posture_counts,
    }

    result.update(
        {
            "status": "completed",
            "reason": "Qwen semantic analysis completed.",
            "annotations": annotations,
            "aggregate": aggregate,
        }
    )
    if event_name:
        log_event(
            events_path,
            event_name,
            sample_count=len(annotations),
            focus_counts=focus_counts,
            action_counts=action_counts,
            affect_counts=affect_counts,
        )
    return result


def _pose_prompt_box(image_bgr: np.ndarray) -> np.ndarray | None:
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pose = mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        min_detection_confidence=0.5,
    )
    try:
        results = pose.process(image_rgb)
    finally:
        pose.close()
    if not results.pose_landmarks:
        return None

    height, width = image_bgr.shape[:2]
    coords: list[tuple[float, float]] = []
    for landmark in results.pose_landmarks.landmark:
        visibility = getattr(landmark, "visibility", 1.0)
        if visibility < 0.35:
            continue
        x = float(np.clip(landmark.x, 0.0, 1.0) * width)
        y = float(np.clip(landmark.y, 0.0, 1.0) * height)
        coords.append((x, y))
    if len(coords) < 6:
        return None
    xs, ys = zip(*coords)
    x1 = max(min(xs) - width * 0.08, 0.0)
    y1 = max(min(ys) - height * 0.08, 0.0)
    x2 = min(max(xs) + width * 0.08, width - 1.0)
    y2 = min(max(ys) + height * 0.08, height - 1.0)
    if x2 - x1 < width * 0.12 or y2 - y1 < height * 0.18:
        return None
    return np.array([x1, y1, x2, y2], dtype=np.float32)


def _compute_mask_iou(mask_a: np.ndarray | None, mask_b: np.ndarray | None) -> float:
    if mask_a is None or mask_b is None:
        return float("nan")
    intersection = np.logical_and(mask_a, mask_b).sum()
    union = np.logical_or(mask_a, mask_b).sum()
    if union <= 0:
        return float("nan")
    return float(intersection / union)


def _run_sam2(samples: list[SemanticSample], config: SemanticConfig, events_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "skipped",
        "reason": "SAM2 semantic analysis disabled.",
        "annotations": [],
        "aggregate": {},
    }
    if not config.sam2_enabled:
        return result

    try:
        import torch
    except Exception as exc:
        result["status"] = "unavailable"
        result["reason"] = f"PyTorch is unavailable for SAM2: {type(exc).__name__}: {exc}"
        return result

    if not _version_at_least(torch.__version__, "2.5.1"):
        result["status"] = "unavailable"
        result["reason"] = f"SAM2 requires torch>=2.5.1; current torch is {torch.__version__}."
        return result
    if not config.sam2_model_cfg or not config.sam2_checkpoint:
        result["status"] = "unavailable"
        result["reason"] = "SAM2 needs both --sam2-model-cfg and --sam2-checkpoint."
        return result

    try:
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
    except Exception as exc:
        result["status"] = "unavailable"
        result["reason"] = f"Missing SAM2 package: {type(exc).__name__}: {exc}"
        return result

    try:
        predictor = SAM2ImagePredictor(build_sam2(config.sam2_model_cfg, str(config.sam2_checkpoint), device=config.sam2_device))
    except Exception as exc:
        result["status"] = "failed"
        result["reason"] = f"Could not initialize SAM2: {type(exc).__name__}: {exc}"
        return result

    records: list[dict[str, Any]] = []
    previous_mask: np.ndarray | None = None
    try:
        for sample in samples:
            prompt_box = _pose_prompt_box(sample.frame_bgr)
            if prompt_box is None:
                records.append(
                    {
                        "timestamp_sec": sample.timestamp_sec,
                        "reason": sample.reason,
                        "status": "no_pose_box",
                    }
                )
                continue
            image_rgb = cv2.cvtColor(sample.frame_bgr, cv2.COLOR_BGR2RGB)
            predictor.set_image(image_rgb)
            masks, scores, _ = predictor.predict(box=prompt_box[None, :], multimask_output=False)
            if masks is None or len(masks) == 0:
                records.append(
                    {
                        "timestamp_sec": sample.timestamp_sec,
                        "reason": sample.reason,
                        "status": "no_mask",
                    }
                )
                previous_mask = None
                continue
            mask = masks[0].astype(bool)
            height, width = mask.shape
            ys, xs = np.where(mask)
            if xs.size == 0 or ys.size == 0:
                records.append(
                    {
                        "timestamp_sec": sample.timestamp_sec,
                        "reason": sample.reason,
                        "status": "empty_mask",
                    }
                )
                previous_mask = None
                continue
            area_ratio = float(mask.mean())
            centroid_x = float(xs.mean() / width)
            centroid_y = float(ys.mean() / height)
            edge_margin_x = max(int(width * 0.02), 2)
            edge_margin_y = max(int(height * 0.02), 2)
            touches_left = bool(mask[:, :edge_margin_x].any())
            touches_right = bool(mask[:, width - edge_margin_x :].any())
            touches_top = bool(mask[:edge_margin_y, :].any())
            touches_bottom = bool(mask[height - edge_margin_y :, :].any())
            stability_iou = _compute_mask_iou(previous_mask, mask)
            records.append(
                {
                    "timestamp_sec": sample.timestamp_sec,
                    "reason": sample.reason,
                    "status": "ok",
                    "sam2_score": float(scores[0]) if scores is not None and len(scores) else float("nan"),
                    "mask_area_ratio": area_ratio,
                    "centroid_x_norm": centroid_x,
                    "centroid_y_norm": centroid_y,
                    "stage_zone": "left" if centroid_x < 0.33 else "center" if centroid_x < 0.67 else "right",
                    "touches_left_edge": touches_left,
                    "touches_right_edge": touches_right,
                    "touches_top_edge": touches_top,
                    "touches_bottom_edge": touches_bottom,
                    "frame_cutoff_flag": bool(touches_left or touches_right or touches_top or touches_bottom),
                    "stability_iou_prev": stability_iou,
                }
            )
            previous_mask = mask
    except Exception as exc:
        result["status"] = "failed"
        result["reason"] = f"SAM2 inference failed: {type(exc).__name__}: {exc}"
        return result

    ok_records = [row for row in records if row.get("status") == "ok"]
    if not ok_records:
        result["status"] = "failed"
        result["reason"] = "SAM2 ran but produced no usable masks on sampled frames."
        result["annotations"] = records
        return result

    frame_count = len(ok_records)
    zone_counts = pd.Series([row["stage_zone"] for row in ok_records]).value_counts().to_dict()
    aggregate = {
        "sample_count": frame_count,
        "tracked_sample_ratio": _safe_ratio(frame_count, len(samples)),
        "stage_zone_counts": zone_counts,
        "stage_zone_balance_score": 100.0 * _clip01(len(zone_counts) / 3.0),
        "mean_mask_area_ratio": float(np.mean([row["mask_area_ratio"] for row in ok_records])),
        "mean_cutoff_risk": 100.0
        * float(np.mean([1.0 if row["frame_cutoff_flag"] else 0.0 for row in ok_records])),
        "mean_mask_stability_iou": float(np.nanmean([row["stability_iou_prev"] for row in ok_records])),
    }

    result.update(
        {
            "status": "completed",
            "reason": "SAM2 mask analysis completed.",
            "annotations": records,
            "aggregate": aggregate,
        }
    )
    log_event(
        events_path,
        "semantic_sam2_completed",
        sample_count=frame_count,
        stage_zone_counts=zone_counts,
        tracked_sample_ratio=aggregate["tracked_sample_ratio"],
    )
    return result


def _build_contact_sheet(
    samples: list[SemanticSample],
    qwen_result: dict[str, Any],
    sam2_result: dict[str, Any],
    output_path: Path,
) -> None:
    if not samples:
        return

    qwen_lookup = {round(row["timestamp_sec"], 2): row for row in qwen_result.get("annotations", [])}
    sam2_lookup = {round(row["timestamp_sec"], 2): row for row in sam2_result.get("annotations", [])}
    tile_w = 640
    tile_h = 360
    cols = 2
    rows = int(math.ceil(len(samples) / cols))
    canvas = np.full((rows * tile_h, cols * tile_w, 3), 245, dtype=np.uint8)

    for index, sample in enumerate(samples):
        row_idx = index // cols
        col_idx = index % cols
        tile = cv2.resize(sample.frame_bgr, (tile_w, tile_h))
        overlay = tile.copy()

        qwen_row = qwen_lookup.get(round(sample.timestamp_sec, 2))
        sam2_row = sam2_lookup.get(round(sample.timestamp_sec, 2))
        if sam2_row and sam2_row.get("status") == "ok":
            zone = sam2_row["stage_zone"]
            zone_text = f"SAM2 zone={zone} area={sam2_row['mask_area_ratio']:.3f}"
            cv2.rectangle(overlay, (10, 10), (400, 86), (0, 0, 0), thickness=-1)
            cv2.putText(overlay, zone_text, (22, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(
                overlay,
                f"cutoff={int(bool(sam2_row['frame_cutoff_flag']))} stability={sam2_row['stability_iou_prev']:.2f}",
                (22, 72),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        cv2.rectangle(overlay, (10, tile_h - 110), (tile_w - 10, tile_h - 10), (0, 0, 0), thickness=-1)
        cv2.putText(
            overlay,
            f"t={sample.timestamp_sec:.2f}s  {sample.reason}",
            (22, tile_h - 74),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.68,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        if qwen_row:
            cv2.putText(
                overlay,
                f"Qwen focus={qwen_row['teacher_focus']}  action={qwen_row['body_action']}",
                (22, tile_h - 46),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                overlay,
                f"affect={qwen_row['affect_tone']}  posture={qwen_row['posture_signal']}",
                (22, tile_h - 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
        tile = cv2.addWeighted(overlay, 0.72, tile, 0.28, 0.0)
        y0 = row_idx * tile_h
        x0 = col_idx * tile_w
        canvas[y0 : y0 + tile_h, x0 : x0 + tile_w] = tile

    cv2.imwrite(str(output_path), canvas)


def _base_to_semantic_agreement(summary: dict[str, Any], qwen_result: dict[str, Any]) -> dict[str, Any]:
    if qwen_result.get("status") != "completed":
        return {
            "status": "not_available",
            "reason": "Qwen semantic output was not available.",
        }

    aggregate = qwen_result.get("aggregate", {})
    base_audience_ratio = summary["scores"]["audience_orientation_score"] / 100.0
    qwen_audience_ratio = float(aggregate.get("audience_focus_ratio", 0.0))
    qwen_board_ratio = float(aggregate.get("board_focus_ratio", 0.0)) + float(aggregate.get("screen_focus_ratio", 0.0))
    delta = abs(base_audience_ratio - qwen_audience_ratio)
    if qwen_audience_ratio >= 0.45 and base_audience_ratio >= 0.60:
        label = "aligned"
    elif qwen_board_ratio >= 0.45 and base_audience_ratio <= 0.55:
        label = "aligned"
    elif delta <= 0.20:
        label = "mostly_aligned"
    else:
        label = "review"
    return {
        "status": "available",
        "label": label,
        "base_audience_orientation_ratio": round(base_audience_ratio, 3),
        "qwen_audience_focus_ratio": round(qwen_audience_ratio, 3),
        "difference": round(delta, 3),
        "note": "This agreement check is qualitative and does not change base scores.",
    }


def _build_summary(
    samples: list[SemanticSample],
    summary: dict[str, Any],
    qwen_result: dict[str, Any],
    sam2_result: dict[str, Any],
) -> dict[str, Any]:
    semantic_summary: dict[str, Any] = {
        "sample_count": len(samples),
        "sample_timestamps_sec": [round(sample.timestamp_sec, 2) for sample in samples],
        "sample_reasons": [sample.reason for sample in samples],
        "qwen": {
            "status": qwen_result.get("status"),
            "reason": qwen_result.get("reason"),
            "aggregate": qwen_result.get("aggregate", {}),
        },
        "sam2": {
            "status": sam2_result.get("status"),
            "reason": sam2_result.get("reason"),
            "aggregate": sam2_result.get("aggregate", {}),
        },
        "agreement": _base_to_semantic_agreement(summary, qwen_result),
    }
    if qwen_result.get("status") == "completed":
        qwen_agg = qwen_result["aggregate"]
        semantic_summary["semantic_extensions"] = {
            "audience_focus_ratio_qwen": qwen_agg.get("audience_focus_ratio", 0.0),
            "board_or_screen_focus_ratio_qwen": qwen_agg.get("board_focus_ratio", 0.0)
            + qwen_agg.get("screen_focus_ratio", 0.0),
            "warm_affect_ratio_qwen": qwen_agg.get("warm_affect_ratio", 0.0),
            "tense_affect_ratio_qwen": qwen_agg.get("tense_affect_ratio", 0.0),
            "static_stance_ratio_qwen": qwen_agg.get("static_stance_ratio", 0.0),
            "pointing_ratio_qwen": qwen_agg.get("pointing_ratio", 0.0),
        }
    else:
        semantic_summary["semantic_extensions"] = {}
    if sam2_result.get("status") == "completed":
        semantic_summary["semantic_extensions"].update(
            {
                "stage_zone_balance_score_sam2": sam2_result["aggregate"].get("stage_zone_balance_score", 0.0),
                "tracked_sample_ratio_sam2": sam2_result["aggregate"].get("tracked_sample_ratio", 0.0),
                "mean_cutoff_risk_sam2": sam2_result["aggregate"].get("mean_cutoff_risk", 0.0),
            }
        )
    return semantic_summary


def _summary_markdown(payload: dict[str, Any], summary: dict[str, Any], qwen_result: dict[str, Any], sam2_result: dict[str, Any]) -> str:
    lines = [
        "# Semantic Extensions Summary",
        "",
        "These outputs are additive only. They do not change any of the base nonverbal scores.",
        "",
        "## Base Context",
        "",
        f"- Base overall score: `{summary['scores']['heuristic_nonverbal_score']:.1f}`",
        f"- Base audience-orientation score: `{summary['scores']['audience_orientation_score']:.1f}`",
        f"- Base eye-contact distribution score: `{summary['scores']['eye_contact_distribution_score']:.1f}`",
        f"- Sample count used for semantic review: `{payload['sample_count']}`",
        "",
        "## Qwen",
        "",
        f"- Status: `{qwen_result['status']}`",
        f"- Reason: {qwen_result['reason']}",
    ]
    if qwen_result.get("status") == "completed":
        aggregate = qwen_result["aggregate"]
        lines.extend(
            [
                f"- Audience focus ratio: `{aggregate['audience_focus_ratio']:.2f}`",
                f"- Board focus ratio: `{aggregate['board_focus_ratio']:.2f}`",
                f"- Screen focus ratio: `{aggregate['screen_focus_ratio']:.2f}`",
                f"- Warm affect ratio: `{aggregate['warm_affect_ratio']:.2f}`",
                f"- Tense affect ratio: `{aggregate['tense_affect_ratio']:.2f}`",
                f"- Static stance ratio: `{aggregate['static_stance_ratio']:.2f}`",
                f"- Pointing ratio: `{aggregate['pointing_ratio']:.2f}`",
            ]
        )
    lines.extend(
        [
            "",
            "## SAM2",
            "",
            f"- Status: `{sam2_result['status']}`",
            f"- Reason: {sam2_result['reason']}",
        ]
    )
    if sam2_result.get("status") == "completed":
        aggregate = sam2_result["aggregate"]
        lines.extend(
            [
                f"- Tracked sample ratio: `{aggregate['tracked_sample_ratio']:.2f}`",
                f"- Stage-zone balance score: `{aggregate['stage_zone_balance_score']:.1f}`",
                f"- Mean cutoff risk: `{aggregate['mean_cutoff_risk']:.1f}`",
                f"- Mean mask stability IoU: `{aggregate['mean_mask_stability_iou']:.2f}`",
            ]
        )
    agreement = payload["agreement"]
    lines.extend(
        [
            "",
            "## Agreement Check",
            "",
            f"- Status: `{agreement['status']}`",
        ]
    )
    if agreement["status"] == "available":
        lines.extend(
            [
                f"- Label: `{agreement['label']}`",
                f"- Base audience ratio: `{agreement['base_audience_orientation_ratio']:.2f}`",
                f"- Qwen audience ratio: `{agreement['qwen_audience_focus_ratio']:.2f}`",
                f"- Absolute difference: `{agreement['difference']:.2f}`",
                f"- Note: {agreement['note']}",
            ]
        )
    else:
        lines.append(f"- Reason: {agreement['reason']}")
    return "\n".join(lines) + "\n"


def run_semantic_extensions(
    clip_path: Path,
    frame_metrics_df: pd.DataFrame,
    summary: dict[str, Any],
    run_dir: Path,
    config: SemanticConfig,
    events_path: Path,
) -> dict[str, Any]:
    artifacts = build_semantic_artifacts(run_dir)
    samples = _save_sampled_frames(
        clip_path=clip_path,
        frame_metrics_df=frame_metrics_df,
        artifacts=artifacts,
        config=config,
        events_path=events_path,
        clip_duration_sec=float(summary["clip"]["duration_sec_actual"]),
    )
    qwen_result = _run_qwen(samples, config, events_path)
    sam2_result = _run_sam2(samples, config, events_path)
    payload = _build_summary(samples, summary, qwen_result, sam2_result)

    artifacts.qwen_annotations_path.write_text(
        json.dumps(qwen_result, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    artifacts.sam2_metrics_path.write_text(
        json.dumps(sam2_result, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    artifacts.summary_json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    artifacts.summary_md_path.write_text(
        _summary_markdown(payload, summary, qwen_result, sam2_result),
        encoding="utf-8",
    )
    _build_contact_sheet(samples, qwen_result, sam2_result, artifacts.contact_sheet_path)
    log_event(
        events_path,
        "semantic_extensions_finished",
        qwen_status=qwen_result["status"],
        sam2_status=sam2_result["status"],
        summary_json=str(artifacts.summary_json_path),
        contact_sheet=str(artifacts.contact_sheet_path),
    )
    return {
        "artifacts": {
            "root_dir": str(artifacts.root_dir),
            "sampled_frames_dir": str(artifacts.sampled_frames_dir),
            "contact_sheet": str(artifacts.contact_sheet_path),
            "qwen_annotations": str(artifacts.qwen_annotations_path),
            "sam2_metrics": str(artifacts.sam2_metrics_path),
            "summary_json": str(artifacts.summary_json_path),
            "summary_md": str(artifacts.summary_md_path),
        },
        "summary": payload,
        "qwen": qwen_result,
        "sam2": sam2_result,
    }
