from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import matplotlib.pyplot as plt
import mediapipe as mp
import numpy as np
import pandas as pd
from scipy.fft import fft
from scipy.signal import cheby1, filtfilt


EPS = 1e-6

FACE_NOSE = 1
FACE_LEFT_CHEEK = 234
FACE_RIGHT_CHEEK = 454
FACE_LEFT_MOUTH = 61
FACE_RIGHT_MOUTH = 291
FACE_UPPER_LIP = 13
FACE_LOWER_LIP = 14
FACE_LEFT_BROW = 65
FACE_RIGHT_BROW = 295
FACE_LEFT_EYE = [33, 160, 158, 133, 153, 144]
FACE_RIGHT_EYE = [362, 385, 387, 263, 373, 380]


@dataclass(slots=True)
class ExperimentConfig:
    clip_start_sec: float = 120.0
    clip_duration_sec: float = 5.0
    keyframe_offset_sec: float = 2.5
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    model_complexity: int = 1


@dataclass(slots=True)
class ExperimentArtifacts:
    root_dir: Path
    clip_path: Path
    keyframe_path: Path
    annotated_keyframe_path: Path
    debug_video_path: Path
    debug_contact_sheet_path: Path
    per_frame_csv_path: Path
    summary_json_path: Path
    summary_md_path: Path
    timeline_plot_path: Path
    events_jsonl_path: Path


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_artifacts(output_root: Path) -> ExperimentArtifacts:
    run_dir = output_root / f"run_{_timestamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return ExperimentArtifacts(
        root_dir=run_dir,
        clip_path=run_dir / "clip_5s.mp4",
        keyframe_path=run_dir / "keyframe.jpg",
        annotated_keyframe_path=run_dir / "keyframe_annotated.jpg",
        debug_video_path=run_dir / "debug_overlay.mp4",
        debug_contact_sheet_path=run_dir / "debug_contact_sheet.jpg",
        per_frame_csv_path=run_dir / "per_frame_metrics.csv",
        summary_json_path=run_dir / "summary.json",
        summary_md_path=run_dir / "summary.md",
        timeline_plot_path=run_dir / "metric_timelines.png",
        events_jsonl_path=run_dir / "events.jsonl",
    )


def log_event(events_path: Path, event: str, **payload: Any) -> None:
    record = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": payload,
    }
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _score_linear(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return _clip01((value - low) / (high - low))


def _score_inverse(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return 1.0 - _clip01((value - low) / (high - low))


def _score_peak(value: float, low: float, mid: float, high: float) -> float:
    if not (low < mid < high):
        return 0.0
    if value <= low or value >= high:
        return 0.0
    if value <= mid:
        return _clip01((value - low) / (mid - low))
    return _clip01((high - value) / (high - mid))


def _band(score: float) -> str:
    if score >= 75:
        return "strong"
    if score >= 55:
        return "moderate"
    return "limited"


def _risk_band(score: float) -> str:
    if score >= 65:
        return "high"
    if score >= 35:
        return "moderate"
    return "low"


def _safe_mean(values: pd.Series | np.ndarray | list[float], default: float = 0.0) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        return default
    return float(np.nanmean(arr))


def _safe_std(values: pd.Series | np.ndarray | list[float], default: float = 0.0) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        return default
    return float(np.nanstd(arr))


def _uniformity_score(counts: list[int] | np.ndarray) -> float:
    arr = np.asarray(counts, dtype=float)
    total = arr.sum()
    if total <= 0:
        return 0.0
    probs = arr / total
    entropy = -np.sum([p * np.log(p + EPS) for p in probs if p > 0])
    return float(entropy / np.log(len(arr)))


def _count_transitions(states: pd.Series) -> int:
    values = states.dropna().astype(int).to_numpy()
    if len(values) < 2:
        return 0
    return int(np.sum(values[1:] != values[:-1]))


def _lm_xy(landmarks: list[Any], index: int) -> np.ndarray:
    landmark = landmarks[index]
    return np.array([landmark.x, landmark.y], dtype=np.float32)


def _dist(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def _compute_ear(face_landmarks: list[Any]) -> float:
    def eye_ratio(indices: list[int]) -> float:
        p1, p2, p3, p4, p5, p6 = [_lm_xy(face_landmarks, idx) for idx in indices]
        return (_dist(p2, p6) + _dist(p3, p5)) / (2.0 * (_dist(p1, p4) + EPS))

    return float((eye_ratio(FACE_LEFT_EYE) + eye_ratio(FACE_RIGHT_EYE)) / 2.0)


def _classify_hand_gesture(hand_landmarks: Any) -> dict[str, float]:
    if hand_landmarks is None:
        return {"fist": 0.0, "pointing": 0.0, "open_palm": 0.0}

    coords = hand_landmarks.landmark
    wrist = _lm_xy(coords, 0)

    def finger_extended(tip: int, pip: int) -> bool:
        return _dist(_lm_xy(coords, tip), wrist) > _dist(_lm_xy(coords, pip), wrist) * 1.05

    def finger_curled(tip: int, pip: int) -> bool:
        return _dist(_lm_xy(coords, tip), wrist) < _dist(_lm_xy(coords, pip), wrist) * 0.95

    index_ext = finger_extended(8, 6)
    middle_ext = finger_extended(12, 10)
    ring_ext = finger_extended(16, 14)
    pinky_ext = finger_extended(20, 18)

    index_cur = finger_curled(8, 6)
    middle_cur = finger_curled(12, 10)
    ring_cur = finger_curled(16, 14)
    pinky_cur = finger_curled(20, 18)

    return {
        "fist": 1.0 if index_cur and middle_cur and ring_cur and pinky_cur else 0.0,
        "pointing": 1.0 if index_ext and middle_cur and ring_cur and pinky_cur else 0.0,
        "open_palm": 1.0 if index_ext and middle_ext and ring_ext and pinky_ext else 0.0,
    }


def calculate_ldlj(velocity: np.ndarray, fs: float) -> float:
    if len(velocity) < 5 or fs <= 0:
        return float("nan")

    dt = 1.0 / fs
    duration = len(velocity) * dt
    v_peak = np.max(np.abs(velocity))
    if v_peak == 0:
        return float("-inf")

    jerk = np.diff(velocity, 2) / (dt**2)
    scale = (duration**3) / (v_peak**2 + EPS)
    dj = -scale * np.sum(jerk**2) * dt
    return float(np.log(np.abs(dj) + 1e-8))


def calculate_sal(velocity: np.ndarray, fs: float, fc: float = 10.0, amp_th: float = 0.05) -> float:
    if len(velocity) < 8 or fs <= 0:
        return float("nan")

    nfft = int(2 ** np.ceil(np.log2(len(velocity))))
    freqs = np.arange(0, fs, fs / nfft)
    magnitude = np.abs(fft(velocity, nfft))
    magnitude /= np.max(magnitude) + EPS

    selected = np.where((freqs <= fc) & (magnitude >= amp_th))
    if len(selected[0]) < 2:
        return 0.0

    f_sel = freqs[selected]
    m_sel = magnitude[selected]
    return float(-np.sum(np.sqrt(np.diff(f_sel / (f_sel[-1] + EPS)) ** 2 + np.diff(m_sel) ** 2)))


def extract_clip(video_path: Path, clip_path: Path, start_sec: float, duration_sec: float, events_path: Path) -> dict[str, Any]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps else 0.0

    clip_path.parent.mkdir(parents=True, exist_ok=True)
    cap.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000.0)
    writer = cv2.VideoWriter(
        str(clip_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    written = 0
    end_sec = min(start_sec + duration_sec, duration)
    while cap.isOpened():
        now_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if now_sec >= end_sec:
            break
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(frame)
        written += 1

    cap.release()
    writer.release()
    clip_info = {
        "source_video": str(video_path),
        "clip_video": str(clip_path),
        "start_sec": start_sec,
        "duration_sec_requested": duration_sec,
        "duration_sec_actual": written / fps if fps else 0.0,
        "fps": fps,
        "width": width,
        "height": height,
        "frames_written": written,
    }
    log_event(events_path, "clip_extracted", **clip_info)
    return clip_info


def extract_frame(video_path: Path, output_path: Path, time_sec: float, events_path: Path) -> dict[str, Any]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video for frame extraction: {video_path}")
    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000.0)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not read frame at {time_sec:.2f}s from {video_path}")
    cv2.imwrite(str(output_path), frame)
    result = {"frame_path": str(output_path), "time_sec": time_sec}
    log_event(events_path, "frame_extracted", **result)
    return result


def _extract_frame_metrics(results: Any, pose_landmark_enum: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "pose_detected": 0,
        "face_detected": 0,
        "left_hand_detected": 0,
        "right_hand_detected": 0,
        "any_hand_detected": 0,
        "shoulder_width": np.nan,
        "torso_len": np.nan,
        "mid_hip_x": np.nan,
        "mid_shoulder_x": np.nan,
        "left_wrist_x": np.nan,
        "left_wrist_y": np.nan,
        "right_wrist_x": np.nan,
        "right_wrist_y": np.nan,
        "posture_score_frame": np.nan,
        "audience_orientation_score_frame": np.nan,
        "gesture_extent_frame": np.nan,
        "face_front_score_frame": np.nan,
        "body_front_score_frame": np.nan,
        "signed_yaw_proxy": np.nan,
        "gaze_sector": np.nan,
        "smile_proxy": np.nan,
        "mouth_open_ratio": np.nan,
        "eye_open_ratio": np.nan,
        "brow_eye_ratio": np.nan,
        "face_area": np.nan,
        "arm_span_ratio": np.nan,
        "open_palm_frame": 0.0,
        "pointing_frame": 0.0,
        "fist_frame": 0.0,
    }

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        row["pose_detected"] = 1
        l_shoulder = _lm_xy(lm, pose_landmark_enum.LEFT_SHOULDER.value)
        r_shoulder = _lm_xy(lm, pose_landmark_enum.RIGHT_SHOULDER.value)
        l_hip = _lm_xy(lm, pose_landmark_enum.LEFT_HIP.value)
        r_hip = _lm_xy(lm, pose_landmark_enum.RIGHT_HIP.value)
        nose = _lm_xy(lm, pose_landmark_enum.NOSE.value)
        l_wrist = _lm_xy(lm, pose_landmark_enum.LEFT_WRIST.value)
        r_wrist = _lm_xy(lm, pose_landmark_enum.RIGHT_WRIST.value)

        mid_shoulder = (l_shoulder + r_shoulder) / 2.0
        mid_hip = (l_hip + r_hip) / 2.0
        shoulder_width = _dist(l_shoulder, r_shoulder)
        torso_len = _dist(mid_shoulder, mid_hip)

        shoulder_tilt = abs(l_shoulder[1] - r_shoulder[1]) / (shoulder_width + EPS)
        torso_lean = abs(mid_shoulder[0] - mid_hip[0]) / (torso_len + EPS)
        head_balance = abs(nose[0] - mid_shoulder[0]) / (torso_len + EPS)
        posture_score = 100.0 * (
            0.40 * _score_inverse(shoulder_tilt, 0.02, 0.18)
            + 0.35 * _score_inverse(torso_lean, 0.03, 0.20)
            + 0.25 * _score_inverse(head_balance, 0.05, 0.25)
        )

        body_depth_ratio = abs(lm[pose_landmark_enum.LEFT_SHOULDER.value].z - lm[pose_landmark_enum.RIGHT_SHOULDER.value].z) / (shoulder_width + EPS)
        body_front = _score_inverse(body_depth_ratio, 0.10, 3.00)
        gesture_extent = max(_dist(l_wrist, mid_shoulder), _dist(r_wrist, mid_shoulder)) / (shoulder_width + EPS)
        arm_span_ratio = _dist(l_wrist, r_wrist) / (shoulder_width + EPS)

        row.update(
            {
                "shoulder_width": shoulder_width,
                "torso_len": torso_len,
                "mid_hip_x": float(mid_hip[0]),
                "mid_shoulder_x": float(mid_shoulder[0]),
                "left_wrist_x": float(l_wrist[0]),
                "left_wrist_y": float(l_wrist[1]),
                "right_wrist_x": float(r_wrist[0]),
                "right_wrist_y": float(r_wrist[1]),
                "posture_score_frame": float(posture_score),
                "body_front_score_frame": float(100.0 * body_front),
                "gesture_extent_frame": float(gesture_extent),
                "arm_span_ratio": float(arm_span_ratio),
            }
        )

    if results.face_landmarks:
        face = results.face_landmarks.landmark
        row["face_detected"] = 1
        nose = _lm_xy(face, FACE_NOSE)
        left_cheek = _lm_xy(face, FACE_LEFT_CHEEK)
        right_cheek = _lm_xy(face, FACE_RIGHT_CHEEK)
        face_width = _dist(left_cheek, right_cheek)
        mid_cheek_x = (left_cheek[0] + right_cheek[0]) / 2.0
        signed_yaw = float((2.0 * (nose[0] - mid_cheek_x)) / (face_width + EPS))
        yaw_proxy = abs(signed_yaw)
        left_eye_outer = _lm_xy(face, FACE_LEFT_EYE[0])
        right_eye_outer = _lm_xy(face, FACE_RIGHT_EYE[3])
        eye_symmetry = abs(_dist(nose, left_eye_outer) - _dist(nose, right_eye_outer)) / (face_width + EPS)
        face_front = 0.70 * _score_inverse(eye_symmetry, 0.05, 0.45) + 0.30 * _score_inverse(yaw_proxy, 0.15, 1.20)

        mouth_left = _lm_xy(face, FACE_LEFT_MOUTH)
        mouth_right = _lm_xy(face, FACE_RIGHT_MOUTH)
        upper_lip = _lm_xy(face, FACE_UPPER_LIP)
        lower_lip = _lm_xy(face, FACE_LOWER_LIP)
        mouth_width = _dist(mouth_left, mouth_right)
        mouth_open = _dist(upper_lip, lower_lip) / (mouth_width + EPS)
        smile_proxy = mouth_width / (face_width + EPS)
        eye_open = _compute_ear(face)

        left_brow = _lm_xy(face, FACE_LEFT_BROW)
        right_brow = _lm_xy(face, FACE_RIGHT_BROW)
        left_eye_top = _lm_xy(face, FACE_LEFT_EYE[1])
        right_eye_top = _lm_xy(face, FACE_RIGHT_EYE[1])
        brow_eye_ratio = ((_dist(left_brow, left_eye_top) + _dist(right_brow, right_eye_top)) / 2.0) / (face_width + EPS)

        if signed_yaw <= -0.18:
            gaze_sector = -1
        elif signed_yaw >= 0.18:
            gaze_sector = 1
        else:
            gaze_sector = 0

        xs = np.array([pt.x for pt in face], dtype=np.float32)
        ys = np.array([pt.y for pt in face], dtype=np.float32)
        face_area = float((xs.max() - xs.min()) * (ys.max() - ys.min()))

        row.update(
            {
                "face_front_score_frame": float(100.0 * face_front),
                "signed_yaw_proxy": signed_yaw,
                "gaze_sector": gaze_sector,
                "smile_proxy": float(smile_proxy),
                "mouth_open_ratio": float(mouth_open),
                "eye_open_ratio": float(eye_open),
                "brow_eye_ratio": float(brow_eye_ratio),
                "face_area": face_area,
            }
        )

    left_hand = _classify_hand_gesture(results.left_hand_landmarks)
    right_hand = _classify_hand_gesture(results.right_hand_landmarks)
    row["left_hand_detected"] = int(results.left_hand_landmarks is not None)
    row["right_hand_detected"] = int(results.right_hand_landmarks is not None)
    row["any_hand_detected"] = int(row["left_hand_detected"] or row["right_hand_detected"])
    row["open_palm_frame"] = max(left_hand["open_palm"], right_hand["open_palm"])
    row["pointing_frame"] = max(left_hand["pointing"], right_hand["pointing"])
    row["fist_frame"] = max(left_hand["fist"], right_hand["fist"])

    face_score = row["face_front_score_frame"]
    body_score = row["body_front_score_frame"]
    if np.isfinite(face_score) and np.isfinite(body_score):
        row["audience_orientation_score_frame"] = float(0.70 * face_score + 0.30 * body_score)
    elif np.isfinite(face_score):
        row["audience_orientation_score_frame"] = float(face_score)
    elif np.isfinite(body_score):
        row["audience_orientation_score_frame"] = float(body_score)

    return row


def _compute_motion_signals(df: pd.DataFrame, fps: float) -> tuple[pd.DataFrame, dict[str, float]]:
    motion_df = df.copy()
    for col in [
        "left_wrist_x",
        "left_wrist_y",
        "right_wrist_x",
        "right_wrist_y",
        "shoulder_width",
        "mid_hip_x",
        "arm_span_ratio",
        "signed_yaw_proxy",
    ]:
        motion_df[col] = motion_df[col].interpolate(limit_direction="both")

    left_speed = np.sqrt(
        np.diff(motion_df["left_wrist_x"], prepend=motion_df["left_wrist_x"].iloc[0]) ** 2
        + np.diff(motion_df["left_wrist_y"], prepend=motion_df["left_wrist_y"].iloc[0]) ** 2
    )
    right_speed = np.sqrt(
        np.diff(motion_df["right_wrist_x"], prepend=motion_df["right_wrist_x"].iloc[0]) ** 2
        + np.diff(motion_df["right_wrist_y"], prepend=motion_df["right_wrist_y"].iloc[0]) ** 2
    )
    shoulder_width = motion_df["shoulder_width"].replace(0, np.nan).bfill().ffill().fillna(1.0)
    gesture_motion = ((left_speed + right_speed) / 2.0) / shoulder_width.to_numpy()
    motion_df["gesture_motion"] = gesture_motion

    horizontal_range = motion_df["mid_hip_x"].max() - motion_df["mid_hip_x"].min()
    signal = gesture_motion
    if len(signal) > 15 and fps > 8:
        b, a = cheby1(4, 0.5, 4 / (fps / 2), btype="low")
        filtered = filtfilt(b, a, signal)
    else:
        filtered = signal

    ldlj = calculate_ldlj(filtered, fps)
    sal = calculate_sal(filtered, fps)

    return motion_df, {
        "gesture_motion_mean": float(np.nanmean(gesture_motion)),
        "gesture_motion_peak": float(np.nanmax(gesture_motion)),
        "gesture_motion_std": float(np.nanstd(gesture_motion)),
        "stage_range": float(horizontal_range),
        "ldlj_smoothness_raw": float(ldlj),
        "sal_smoothness_raw": float(sal),
    }


def summarize_frame_metrics(frame_df: pd.DataFrame, fps: float, clip_info: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    if frame_df.empty:
        raise RuntimeError("No frame metrics were provided for summarization.")
    motion_df, motion_stats = _compute_motion_signals(frame_df, fps)
    clip_payload = dict(clip_info)
    if "duration_sec_actual" not in clip_payload:
        clip_payload["duration_sec_actual"] = float(motion_df["timestamp_sec"].max() - motion_df["timestamp_sec"].min())
    summary = _build_summary(motion_df, motion_stats, clip_payload)
    return motion_df, summary


def _build_feedback(summary: dict[str, Any]) -> dict[str, list[str]]:
    strengths: list[str] = []
    watch_items: list[str] = []

    gesture = summary["category_feedback"]["gesture_and_facial_expression"]
    posture = summary["category_feedback"]["posture_and_presence"]
    eye_contact = summary["category_feedback"]["eye_contact_and_engagement"]

    if gesture["natural_movement_score"] >= 70:
        strengths.append("Gesture movement looks natural rather than statue-like or mechanical.")
    if gesture["positive_affect_score"] >= 55:
        strengths.append("Facial affect reads as reasonably welcoming and approachable.")
    if gesture["enthusiasm_score"] >= 65:
        strengths.append("Energy level appears engaged without obvious over-animation.")
    if posture["upright_relaxed_posture_score"] >= 75:
        strengths.append("Posture is upright and stable, supporting a confident classroom presence.")
    if posture["confidence_presence_score"] >= 70:
        strengths.append("Body openness and stance suggest confident delivery rather than closed-off presentation.")
    if eye_contact["eye_contact_distribution_score"] >= 60:
        strengths.append("Head and gaze behavior show some distribution across audience sectors rather than a single fixed target.")
    if eye_contact["alertness_score"] >= 65:
        strengths.append("The instructor appears alert and attentive to the room.")

    if gesture["static_behavior_risk"] >= 35:
        watch_items.append("Movement may be too limited in places; check for stretches of static delivery.")
    if gesture["excessive_animation_risk"] >= 35:
        watch_items.append("Movement may occasionally become more animated than needed for the teaching point.")
    if gesture["tension_hostility_risk"] >= 35:
        watch_items.append("Facial affect looks somewhat tense; verify that expressions do not read as harsh or closed.")
    if gesture["rigidity_risk"] >= 35:
        watch_items.append("Expression and gesture variability are limited enough to risk a rigid presentation style.")
    if posture["closed_posture_risk"] >= 35:
        watch_items.append("Body posture trends somewhat closed; monitor slouching or arm positions that reduce openness.")
    if eye_contact["eye_contact_distribution_score"] < 50:
        watch_items.append("Gaze distribution appears uneven; check whether the lecture favors one audience sector.")
    if eye_contact["alertness_score"] < 55:
        watch_items.append("Alertness cues are weaker than ideal; review eyelid openness and room-facing orientation.")

    if not strengths:
        strengths.append("The clip is technically trackable, but no single nonverbal strength clearly dominates in this short window.")
    if not watch_items:
        watch_items.append("No major risk flags in this short clip; validate on longer spans before drawing conclusions.")

    return {"strengths": strengths, "watch_items": watch_items}


def _build_summary(df: pd.DataFrame, motion_stats: dict[str, float], clip_info: dict[str, Any]) -> dict[str, Any]:
    pose_coverage = float(df["pose_detected"].mean())
    face_coverage = float(df["face_detected"].mean())
    hand_coverage = float(df["any_hand_detected"].mean())
    clip_duration = max(float(clip_info["duration_sec_actual"]), EPS)

    audience_orientation_score = _safe_mean(df["audience_orientation_score_frame"])
    posture_score = _safe_mean(df["posture_score_frame"])
    gesture_extent_mean = _safe_mean(df["gesture_extent_frame"])
    arm_span_mean = _safe_mean(df["arm_span_ratio"])
    open_palm_ratio = _safe_mean(df["open_palm_frame"])
    pointing_ratio = _safe_mean(df["pointing_frame"])
    fist_ratio = _safe_mean(df["fist_frame"])
    facial_smile_mean = _safe_mean(df["smile_proxy"])
    facial_smile_std = _safe_std(df["smile_proxy"])
    mouth_open_mean = _safe_mean(df["mouth_open_ratio"])
    mouth_open_std = _safe_std(df["mouth_open_ratio"])
    eye_open_mean = _safe_mean(df["eye_open_ratio"])
    brow_eye_mean = _safe_mean(df["brow_eye_ratio"])
    signed_yaw_std = _safe_std(df["signed_yaw_proxy"])

    gesture_activity_score = 100.0 * (
        0.45 * _score_linear(gesture_extent_mean, 0.30, 1.10)
        + 0.35 * _score_linear(motion_stats["gesture_motion_mean"], 0.004, 0.035)
        + 0.20 * _clip01(open_palm_ratio * 1.25 + pointing_ratio * 1.50)
    )
    gesture_smoothness_score = 100.0 * (
        0.55 * _score_linear(motion_stats["sal_smoothness_raw"], -6.0, -1.2)
        + 0.45 * _score_linear(motion_stats["ldlj_smoothness_raw"], 4.0, 16.0)
    )
    facial_expressivity_score = 100.0 * (
        0.70 * _score_linear(facial_smile_mean, 0.34, 0.50)
        + 0.30 * _score_linear(facial_smile_std, 0.005, 0.030)
    )
    stage_usage_score = 100.0 * _score_linear(motion_stats["stage_range"], 0.04, 0.30)

    sector_counts = {
        "left": int((df["gaze_sector"] == -1).sum()),
        "center": int((df["gaze_sector"] == 0).sum()),
        "right": int((df["gaze_sector"] == 1).sum()),
    }
    sector_balance_score = 100.0 * _uniformity_score(list(sector_counts.values()))
    gaze_transition_count = _count_transitions(df["gaze_sector"])
    gaze_transition_rate = gaze_transition_count / clip_duration
    room_scan_score = 100.0 * (
        0.65 * _score_peak(gaze_transition_rate, 0.05, 0.45, 1.60)
        + 0.35 * _score_linear(signed_yaw_std, 0.08, 0.28)
    )
    eye_contact_distribution_score = 100.0 * (
        0.45 * (audience_orientation_score / 100.0)
        + 0.35 * (sector_balance_score / 100.0)
        + 0.20 * (room_scan_score / 100.0)
    )

    natural_movement_score = 100.0 * (
        0.40 * _score_peak(motion_stats["gesture_motion_mean"], 0.004, 0.018, 0.050)
        + 0.35 * (gesture_smoothness_score / 100.0)
        + 0.25 * _score_peak(gesture_extent_mean, 0.35, 0.95, 1.70)
    )
    static_behavior_risk = 100.0 * (
        0.65 * _score_inverse(motion_stats["gesture_motion_mean"], 0.004, 0.014)
        + 0.35 * _score_inverse(motion_stats["stage_range"], 0.03, 0.12)
    )
    excessive_animation_risk = 100.0 * (
        0.55 * _score_linear(motion_stats["gesture_motion_peak"], 0.14, 0.28)
        + 0.25 * _score_linear(gesture_extent_mean, 1.40, 2.10)
        + 0.20 * _score_linear(gaze_transition_rate, 1.00, 2.50)
    )
    positive_affect_score = 100.0 * (
        0.60 * _score_linear(facial_smile_mean, 0.32, 0.44)
        + 0.20 * _score_linear(facial_smile_std, 0.006, 0.028)
        + 0.20 * _score_linear(open_palm_ratio, 0.10, 0.75)
    )
    tension_hostility_risk = 100.0 * (
        0.35 * _score_inverse(facial_smile_mean, 0.28, 0.36)
        + 0.20 * _score_inverse(facial_smile_std, 0.006, 0.022)
        + 0.15 * _score_inverse(mouth_open_mean, 0.08, 0.18)
        + 0.15 * _score_linear(fist_ratio, 0.25, 0.70)
        + 0.15 * _score_inverse(brow_eye_mean, 0.035, 0.060)
    )
    rigidity_risk = 100.0 * (
        0.40 * _score_inverse(motion_stats["gesture_motion_std"], 0.006, 0.022)
        + 0.35 * _score_inverse(facial_smile_std, 0.006, 0.022)
        + 0.25 * _score_inverse(mouth_open_std, 0.006, 0.020)
    )
    confidence_presence_score = 100.0 * (
        0.45 * (posture_score / 100.0)
        + 0.25 * _score_linear(arm_span_mean, 0.65, 1.40)
        + 0.30 * (audience_orientation_score / 100.0)
    )
    closed_posture_risk = 100.0 * (
        0.60 * _score_inverse(arm_span_mean, 0.75, 1.10)
        + 0.40 * _score_inverse(audience_orientation_score, 40.0, 75.0)
    )
    alertness_score = 100.0 * (
        0.40 * _score_linear(eye_open_mean, 0.22, 0.33)
        + 0.30 * (audience_orientation_score / 100.0)
        + 0.30 * (posture_score / 100.0)
    )
    enthusiasm_score = 100.0 * (
        0.40 * (natural_movement_score / 100.0)
        + 0.25 * (positive_affect_score / 100.0)
        + 0.20 * (stage_usage_score / 100.0)
        + 0.15 * (eye_contact_distribution_score / 100.0)
    )

    heuristic_nonverbal_score = (
        0.12 * natural_movement_score
        + 0.10 * positive_affect_score
        + 0.10 * enthusiasm_score
        + 0.14 * posture_score
        + 0.12 * confidence_presence_score
        + 0.12 * audience_orientation_score
        + 0.12 * eye_contact_distribution_score
        + 0.10 * alertness_score
        + 0.08 * gesture_smoothness_score
    )
    heuristic_nonverbal_score -= 0.08 * excessive_animation_risk
    heuristic_nonverbal_score -= 0.06 * static_behavior_risk
    heuristic_nonverbal_score -= 0.06 * rigidity_risk
    heuristic_nonverbal_score = float(np.clip(heuristic_nonverbal_score, 0.0, 100.0))

    warnings: list[str] = []
    if pose_coverage < 0.95:
        warnings.append("Pose coverage dropped below 95%; posture and gesture scores are less stable.")
    if face_coverage < 0.95:
        warnings.append("Face coverage dropped below 95%; audience orientation and facial scores are less stable.")
    if hand_coverage < 0.85:
        warnings.append("Hand coverage dropped below 85%; gesture classification is less stable.")
    if clip_info["duration_sec_actual"] < clip_info["duration_sec_requested"] * 0.95:
        warnings.append("Extracted clip is shorter than requested.")
    if clip_duration < 4.5:
        warnings.append("Short clip duration limits any claim about full-lecture eye-contact distribution.")

    summary = {
        "clip": clip_info,
        "quality_control": {
            "pose_coverage": pose_coverage,
            "face_coverage": face_coverage,
            "hand_coverage": hand_coverage,
            "frames_analyzed": int(len(df)),
        },
        "scores": {
            "audience_orientation_score": audience_orientation_score,
            "posture_stability_score": posture_score,
            "gesture_activity_score": gesture_activity_score,
            "gesture_smoothness_score": gesture_smoothness_score,
            "facial_expressivity_score": facial_expressivity_score,
            "stage_usage_score": stage_usage_score,
            "natural_movement_score": natural_movement_score,
            "positive_affect_score": positive_affect_score,
            "enthusiasm_score": enthusiasm_score,
            "confidence_presence_score": confidence_presence_score,
            "eye_contact_distribution_score": eye_contact_distribution_score,
            "alertness_score": alertness_score,
            "heuristic_nonverbal_score": heuristic_nonverbal_score,
        },
        "category_feedback": {
            "gesture_and_facial_expression": {
                "natural_movement_score": natural_movement_score,
                "positive_affect_score": positive_affect_score,
                "enthusiasm_score": enthusiasm_score,
                "static_behavior_risk": static_behavior_risk,
                "excessive_animation_risk": excessive_animation_risk,
                "tension_hostility_risk": tension_hostility_risk,
                "rigidity_risk": rigidity_risk,
            },
            "posture_and_presence": {
                "upright_relaxed_posture_score": posture_score,
                "confidence_presence_score": confidence_presence_score,
                "closed_posture_risk": closed_posture_risk,
                "grooming_assessment": {
                    "status": "manual_review_required",
                    "reason": "A landmark-only pipeline is not a validated or fair way to score grooming or professional appearance.",
                },
            },
            "eye_contact_and_engagement": {
                "audience_orientation_score": audience_orientation_score,
                "eye_contact_distribution_score": eye_contact_distribution_score,
                "room_scan_score": room_scan_score,
                "alertness_score": alertness_score,
                "sector_balance_score": sector_balance_score,
                "sector_distribution": sector_counts,
                "gaze_transition_count": gaze_transition_count,
                "gaze_transition_rate_per_sec": gaze_transition_rate,
            },
            "manual_review_items": [
                "Speech-gesture synchronization is intentionally out of scope in this version.",
                "Professional grooming/appearance requires manual review.",
            ],
        },
        "raw_metrics": {
            "gesture_extent_mean": gesture_extent_mean,
            "arm_span_mean": arm_span_mean,
            "gesture_motion_mean": motion_stats["gesture_motion_mean"],
            "gesture_motion_peak": motion_stats["gesture_motion_peak"],
            "gesture_motion_std": motion_stats["gesture_motion_std"],
            "open_palm_ratio": open_palm_ratio,
            "pointing_ratio": pointing_ratio,
            "fist_ratio": fist_ratio,
            "smile_proxy_mean": facial_smile_mean,
            "smile_proxy_std": facial_smile_std,
            "mouth_open_mean": mouth_open_mean,
            "mouth_open_std": mouth_open_std,
            "eye_open_mean": eye_open_mean,
            "brow_eye_mean": brow_eye_mean,
            "signed_yaw_std": signed_yaw_std,
            "stage_range": motion_stats["stage_range"],
            "ldlj_smoothness_raw": motion_stats["ldlj_smoothness_raw"],
            "sal_smoothness_raw": motion_stats["sal_smoothness_raw"],
        },
        "interpretation": {
            "audience_orientation": _band(audience_orientation_score),
            "posture_stability": _band(posture_score),
            "gesture_activity": _band(gesture_activity_score),
            "gesture_smoothness": _band(gesture_smoothness_score),
            "facial_expressivity": _band(facial_expressivity_score),
            "natural_movement": _band(natural_movement_score),
            "positive_affect": _band(positive_affect_score),
            "enthusiasm": _band(enthusiasm_score),
            "confidence_presence": _band(confidence_presence_score),
            "eye_contact_distribution": _band(eye_contact_distribution_score),
            "alertness": _band(alertness_score),
            "static_behavior_risk": _risk_band(static_behavior_risk),
            "excessive_animation_risk": _risk_band(excessive_animation_risk),
            "tension_hostility_risk": _risk_band(tension_hostility_risk),
            "rigidity_risk": _risk_band(rigidity_risk),
            "closed_posture_risk": _risk_band(closed_posture_risk),
            "overall_nonverbal_signal": _band(heuristic_nonverbal_score),
        },
        "warnings": warnings,
        "notes": [
            "These scores are heuristic nonverbal proxies based on pretrained landmark detectors.",
            "They are suited to reflective feedback, not high-stakes evaluation or causal claims about teaching quality.",
            "Eye-contact distribution is approximated from head/face orientation and sector changes, not true pupil-level gaze.",
        ],
    }
    summary["feedback"] = _build_feedback(summary)
    return summary


def _save_timeline_plot(df: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(5, 1, figsize=(12, 12), sharex=True)

    axes[0].plot(df["timestamp_sec"], df["audience_orientation_score_frame"], color="#1f77b4")
    axes[0].set_ylabel("Audience")
    axes[0].set_ylim(0, 100)

    axes[1].plot(df["timestamp_sec"], df["posture_score_frame"], color="#2ca02c")
    axes[1].set_ylabel("Posture")
    axes[1].set_ylim(0, 100)

    axes[2].plot(df["timestamp_sec"], df["gesture_motion"], color="#d62728")
    axes[2].set_ylabel("Motion")

    axes[3].plot(df["timestamp_sec"], df["smile_proxy"], color="#9467bd")
    axes[3].set_ylabel("Smile")

    axes[4].plot(df["timestamp_sec"], df["signed_yaw_proxy"], color="#8c564b")
    axes[4].axhline(0.0, color="#444444", linewidth=0.8)
    axes[4].set_ylabel("Yaw")
    axes[4].set_xlabel("Seconds")

    fig.tight_layout()
    fig.savefig(output_path, dpi=140)
    plt.close(fig)


def _sector_label(sector: float) -> str:
    if pd.isna(sector):
        return "unknown"
    if int(sector) < 0:
        return "left"
    if int(sector) > 0:
        return "right"
    return "center"


def _draw_text_block(
    image: np.ndarray,
    lines: list[str],
    origin: tuple[int, int],
    font_scale: float = 0.52,
    fg: tuple[int, int, int] = (255, 255, 255),
    bg: tuple[int, int, int] = (18, 18, 18),
    line_gap: int = 22,
) -> None:
    if not lines:
        return
    x, y = origin
    height = 16 + line_gap * len(lines)
    width = max(cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0][0] for line in lines) + 20
    overlay = image.copy()
    cv2.rectangle(overlay, (x - 8, y - 18), (x + width, y + height), bg, -1)
    cv2.addWeighted(overlay, 0.45, image, 0.55, 0, image)
    for idx, line in enumerate(lines):
        yy = y + idx * line_gap
        cv2.putText(image, line, (x, yy), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(image, line, (x, yy), cv2.FONT_HERSHEY_SIMPLEX, font_scale, fg, 1, cv2.LINE_AA)


def _draw_footer_panel(
    image: np.ndarray,
    summary: dict[str, Any],
    row: pd.Series,
) -> np.ndarray:
    footer_h = 130
    h, w = image.shape[:2]
    canvas = np.full((h + footer_h, w, 3), 22, dtype=np.uint8)
    canvas[:h] = image

    legend_line = (
        "Legend: aud=audience orientation | posture=upright/relaxed stance | motion=gesture movement | "
        "smile=positive-affect proxy | yaw=head turn (-left,+right) | eye_open=alertness proxy"
    )
    hand_line = "Hand flags: open_palm=open hand | point=index-pointing gesture | fist=closed hand"

    strengths = summary["feedback"]["strengths"][:2]
    watch_items = summary["feedback"]["watch_items"][:1]
    feedback_parts = []
    if strengths:
        feedback_parts.append("Feedback strengths: " + " | ".join(strengths))
    if watch_items:
        feedback_parts.append("Watch item: " + " | ".join(watch_items))

    frame_summary = (
        f"Frame {row.name}: sector={_sector_label(row['gaze_sector'])}, "
        f"aud={row['audience_orientation_score_frame']:.1f}, posture={row['posture_score_frame']:.1f}, "
        f"motion={row['gesture_motion']:.3f}, smile={row['smile_proxy']:.3f}"
    )

    footer_lines = [legend_line, hand_line, frame_summary] + feedback_parts
    y0 = h + 24
    for idx, line in enumerate(footer_lines):
        y = y0 + idx * 22
        cv2.putText(canvas, line, (14, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(canvas, line, (14, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1, cv2.LINE_AA)

    return canvas


def _draw_sector_guides(image: np.ndarray, current_sector: str) -> None:
    height, width = image.shape[:2]
    third = width // 3
    colors = {
        "left": (120, 80, 20),
        "center": (40, 110, 40),
        "right": (20, 80, 120),
    }
    sectors = [("left", 0, third), ("center", third, 2 * third), ("right", 2 * third, width)]
    overlay = image.copy()
    for name, x1, x2 in sectors:
        alpha = 0.18 if name == current_sector else 0.07
        cv2.rectangle(overlay, (x1, 0), (x2, height), colors[name], -1)
        cv2.putText(overlay, name.upper(), (x1 + 12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(overlay, (x1, 0), (x1, height), (255, 255, 255), 1)
        cv2.addWeighted(overlay, alpha, image, 1.0 - alpha, 0, image)
        overlay = image.copy()
    cv2.line(image, (third, 0), (third, height), (255, 255, 255), 1)
    cv2.line(image, (2 * third, 0), (2 * third, height), (255, 255, 255), 1)


def _draw_gaze_arrow(image: np.ndarray, face_landmarks: Any, signed_yaw: float) -> None:
    if face_landmarks is None or pd.isna(signed_yaw):
        return
    h, w = image.shape[:2]
    coords = face_landmarks.landmark
    nose = _lm_xy(coords, FACE_NOSE)
    left_cheek = _lm_xy(coords, FACE_LEFT_CHEEK)
    right_cheek = _lm_xy(coords, FACE_RIGHT_CHEEK)
    start = (int(nose[0] * w), int(nose[1] * h))
    face_width = max(_dist(left_cheek, right_cheek), 0.05)
    arrow_len = int(np.clip(abs(signed_yaw) / face_width * 16, 30, 140))
    direction = -1 if signed_yaw < 0 else 1
    end = (start[0] + direction * arrow_len, start[1])
    cv2.arrowedLine(image, start, end, (0, 215, 255), 3, cv2.LINE_AA, tipLength=0.22)


def _draw_body_axis(image: np.ndarray, pose_landmarks: Any, pose_landmark_enum: Any) -> None:
    if pose_landmarks is None:
        return
    h, w = image.shape[:2]
    lm = pose_landmarks.landmark
    left_shoulder = _lm_xy(lm, pose_landmark_enum.LEFT_SHOULDER.value)
    right_shoulder = _lm_xy(lm, pose_landmark_enum.RIGHT_SHOULDER.value)
    left_hip = _lm_xy(lm, pose_landmark_enum.LEFT_HIP.value)
    right_hip = _lm_xy(lm, pose_landmark_enum.RIGHT_HIP.value)
    shoulder = ((left_shoulder + right_shoulder) / 2.0 * np.array([w, h])).astype(int)
    hip = ((left_hip + right_hip) / 2.0 * np.array([w, h])).astype(int)
    cv2.line(image, tuple(shoulder), tuple(hip), (80, 255, 120), 3, cv2.LINE_AA)
    cv2.circle(image, tuple(shoulder), 6, (80, 255, 120), -1)
    cv2.circle(image, tuple(hip), 6, (80, 255, 120), -1)


def _save_debug_contact_sheet(frames: list[np.ndarray], labels: list[str], output_path: Path) -> None:
    if not frames:
        return
    thumbs: list[np.ndarray] = []
    card_w, card_h = 640, 360
    for frame, label in zip(frames, labels):
        thumb = cv2.resize(frame, (card_w, card_h))
        canvas = np.full((card_h + 36, card_w, 3), 245, dtype=np.uint8)
        canvas[:card_h] = thumb
        cv2.putText(canvas, label, (12, card_h + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (20, 20, 20), 2, cv2.LINE_AA)
        thumbs.append(canvas)

    cols = 2
    rows = int(np.ceil(len(thumbs) / cols))
    sheet = np.full((rows * (card_h + 36), cols * card_w, 3), 235, dtype=np.uint8)
    for idx, thumb in enumerate(thumbs):
        row = idx // cols
        col = idx % cols
        y = row * (card_h + 36)
        x = col * card_w
        sheet[y : y + thumb.shape[0], x : x + thumb.shape[1]] = thumb
    cv2.imwrite(str(output_path), sheet)


def render_debug_visuals(
    clip_path: Path,
    frame_metrics_df: pd.DataFrame,
    summary: dict[str, Any],
    artifacts: ExperimentArtifacts,
    config: ExperimentConfig,
) -> None:
    mp_holistic = mp.solutions.holistic
    pose_landmark_enum = mp.solutions.pose.PoseLandmark
    drawing_utils = mp.solutions.drawing_utils
    drawing_styles = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(str(clip_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open clip for debug rendering: {clip_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        str(artifacts.debug_video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height + 130),
    )

    sample_count = min(4, len(frame_metrics_df))
    sample_indices = set(np.linspace(0, max(len(frame_metrics_df) - 1, 0), num=sample_count, dtype=int))
    sample_frames: list[np.ndarray] = []
    sample_labels: list[str] = []
    sector_counts = summary["category_feedback"]["eye_contact_and_engagement"]["sector_distribution"]

    with mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=config.model_complexity,
        refine_face_landmarks=True,
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
    ) as holistic:
        frame_idx = 0
        while cap.isOpened() and frame_idx < len(frame_metrics_df):
            ok, frame = cap.read()
            if not ok:
                break

            row = frame_metrics_df.iloc[frame_idx]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(rgb)
            annotated = frame.copy()

            current_sector = _sector_label(row["gaze_sector"])
            _draw_sector_guides(annotated, current_sector)

            if results.face_landmarks:
                drawing_utils.draw_landmarks(
                    annotated,
                    results.face_landmarks,
                    mp_holistic.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=drawing_styles.get_default_face_mesh_tesselation_style(),
                )
            if results.pose_landmarks:
                drawing_utils.draw_landmarks(
                    annotated,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=drawing_styles.get_default_pose_landmarks_style(),
                )
                _draw_body_axis(annotated, results.pose_landmarks, pose_landmark_enum)
            if results.left_hand_landmarks:
                drawing_utils.draw_landmarks(
                    annotated,
                    results.left_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    drawing_styles.get_default_hand_landmarks_style(),
                    drawing_styles.get_default_hand_connections_style(),
                )
            if results.right_hand_landmarks:
                drawing_utils.draw_landmarks(
                    annotated,
                    results.right_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    drawing_styles.get_default_hand_landmarks_style(),
                    drawing_styles.get_default_hand_connections_style(),
                )

            _draw_gaze_arrow(annotated, results.face_landmarks, float(row["signed_yaw_proxy"]))

            panel_left = [
                f"t={row['timestamp_sec']:.2f}s  sector={current_sector}",
                f"aud={row['audience_orientation_score_frame']:.1f}  posture={row['posture_score_frame']:.1f}",
                f"motion={row['gesture_motion']:.3f}  smile={row['smile_proxy']:.3f}",
                f"yaw={row['signed_yaw_proxy']:.3f}  eye_open={row['eye_open_ratio']:.3f}",
                f"open_palm={int(row['open_palm_frame'])}  point={int(row['pointing_frame'])}  fist={int(row['fist_frame'])}",
            ]
            panel_right = [
                f"overall={summary['scores']['heuristic_nonverbal_score']:.1f}",
                f"natural={summary['scores']['natural_movement_score']:.1f}  affect={summary['scores']['positive_affect_score']:.1f}",
                f"presence={summary['scores']['confidence_presence_score']:.1f}  alert={summary['scores']['alertness_score']:.1f}",
                f"sector counts L/C/R = {sector_counts['left']}/{sector_counts['center']}/{sector_counts['right']}",
                "Comment on landmark fit, sector label, and arrow direction.",
            ]
            _draw_text_block(annotated, panel_left, (14, 34))
            _draw_text_block(annotated, panel_right, (width - 360, 34), font_scale=0.48)

            annotated_with_footer = _draw_footer_panel(annotated, summary, row)

            if frame_idx in sample_indices:
                sample_frames.append(annotated_with_footer.copy())
                sample_labels.append(
                    f"{row['timestamp_sec']:.2f}s | sector={current_sector} | aud={row['audience_orientation_score_frame']:.1f} | motion={row['gesture_motion']:.3f}"
                )

            writer.write(annotated_with_footer)
            frame_idx += 1

    cap.release()
    writer.release()
    _save_debug_contact_sheet(sample_frames, sample_labels, artifacts.debug_contact_sheet_path)
    log_event(
        artifacts.events_jsonl_path,
        "debug_visuals_rendered",
        debug_video=str(artifacts.debug_video_path),
        debug_contact_sheet=str(artifacts.debug_contact_sheet_path),
        sample_frames=len(sample_frames),
    )


def evaluate_clip(clip_path: Path, artifacts: ExperimentArtifacts, config: ExperimentConfig) -> tuple[pd.DataFrame, dict[str, Any]]:
    mp_holistic = mp.solutions.holistic
    pose_landmark_enum = mp.solutions.pose.PoseLandmark
    cap = cv2.VideoCapture(str(clip_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open clip: {clip_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    rows: list[dict[str, Any]] = []
    with mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=config.model_complexity,
        refine_face_landmarks=True,
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
    ) as holistic:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            timestamp_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(rgb)
            row = _extract_frame_metrics(results, pose_landmark_enum)
            row["timestamp_sec"] = timestamp_sec
            rows.append(row)
    cap.release()

    if not rows:
        raise RuntimeError(f"No frames were analyzed in clip: {clip_path}")

    df = pd.DataFrame(rows)
    clip_info = {
        "clip_video": str(clip_path),
        "start_sec": config.clip_start_sec,
        "duration_sec_requested": config.clip_duration_sec,
        "fps": fps,
        "frames_written": int(len(df)),
    }
    motion_df, summary = summarize_frame_metrics(df, fps, clip_info)

    motion_df.to_csv(artifacts.per_frame_csv_path, index=False)
    _save_timeline_plot(motion_df, artifacts.timeline_plot_path)
    with artifacts.summary_json_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    log_event(
        artifacts.events_jsonl_path,
        "clip_evaluated",
        clip_video=str(clip_path),
        frames_analyzed=int(len(motion_df)),
        pose_coverage=summary["quality_control"]["pose_coverage"],
        face_coverage=summary["quality_control"]["face_coverage"],
        hand_coverage=summary["quality_control"]["hand_coverage"],
        heuristic_nonverbal_score=summary["scores"]["heuristic_nonverbal_score"],
    )
    return motion_df, summary


def annotate_keyframe(keyframe_path: Path, output_path: Path, summary: dict[str, Any], config: ExperimentConfig, events_path: Path) -> None:
    image = cv2.imread(str(keyframe_path))
    if image is None:
        raise RuntimeError(f"Could not load keyframe: {keyframe_path}")

    mp_holistic = mp.solutions.holistic
    drawing_utils = mp.solutions.drawing_utils
    drawing_styles = mp.solutions.drawing_styles

    with mp_holistic.Holistic(
        static_image_mode=True,
        model_complexity=config.model_complexity,
        refine_face_landmarks=True,
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
    ) as holistic:
        results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    annotated = image.copy()
    if results.face_landmarks:
        drawing_utils.draw_landmarks(
            annotated,
            results.face_landmarks,
            mp_holistic.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_tesselation_style(),
        )
    if results.pose_landmarks:
        drawing_utils.draw_landmarks(
            annotated,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=drawing_styles.get_default_pose_landmarks_style(),
        )
    if results.left_hand_landmarks:
        drawing_utils.draw_landmarks(
            annotated,
            results.left_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            drawing_styles.get_default_hand_landmarks_style(),
            drawing_styles.get_default_hand_connections_style(),
        )
    if results.right_hand_landmarks:
        drawing_utils.draw_landmarks(
            annotated,
            results.right_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            drawing_styles.get_default_hand_landmarks_style(),
            drawing_styles.get_default_hand_connections_style(),
        )

    lines = [
        f"Natural movement: {summary['scores']['natural_movement_score']:.1f}",
        f"Positive affect: {summary['scores']['positive_affect_score']:.1f}",
        f"Posture/confidence: {summary['scores']['posture_stability_score']:.1f} / {summary['scores']['confidence_presence_score']:.1f}",
        f"Eye-contact distribution: {summary['scores']['eye_contact_distribution_score']:.1f}",
        f"Alertness: {summary['scores']['alertness_score']:.1f}",
        f"QC pose/face/hand: {summary['quality_control']['pose_coverage']:.2f} / {summary['quality_control']['face_coverage']:.2f} / {summary['quality_control']['hand_coverage']:.2f}",
    ]
    x, y = 14, 28
    for i, line in enumerate(lines):
        offset = y + i * 26
        cv2.putText(annotated, line, (x, offset), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(annotated, line, (x, offset), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imwrite(str(output_path), annotated)
    log_event(events_path, "keyframe_annotated", keyframe_path=str(output_path))


def save_summary_markdown(summary: dict[str, Any], artifacts: ExperimentArtifacts) -> None:
    score_block = summary["scores"]
    qc = summary["quality_control"]
    raw = summary["raw_metrics"]
    gesture = summary["category_feedback"]["gesture_and_facial_expression"]
    posture = summary["category_feedback"]["posture_and_presence"]
    eye_contact = summary["category_feedback"]["eye_contact_and_engagement"]

    md = f"""# Nonverbal Cue Experiment

## Clip

- Source clip: `{summary['clip']['clip_video']}`
- Start: `{summary['clip']['start_sec']:.2f}s`
- Duration requested: `{summary['clip']['duration_sec_requested']:.2f}s`
- Frames analyzed: `{qc['frames_analyzed']}`
- FPS: `{summary['clip']['fps']:.2f}`

## Quality Control

- Pose coverage: `{qc['pose_coverage']:.3f}`
- Face coverage: `{qc['face_coverage']:.3f}`
- Hand coverage: `{qc['hand_coverage']:.3f}`

## Scores

- Natural movement: `{score_block['natural_movement_score']:.1f}` ({summary['interpretation']['natural_movement']})
- Positive affect: `{score_block['positive_affect_score']:.1f}` ({summary['interpretation']['positive_affect']})
- Enthusiasm: `{score_block['enthusiasm_score']:.1f}` ({summary['interpretation']['enthusiasm']})
- Posture stability: `{score_block['posture_stability_score']:.1f}` ({summary['interpretation']['posture_stability']})
- Confidence/presence: `{score_block['confidence_presence_score']:.1f}` ({summary['interpretation']['confidence_presence']})
- Audience orientation: `{score_block['audience_orientation_score']:.1f}` ({summary['interpretation']['audience_orientation']})
- Eye-contact distribution: `{score_block['eye_contact_distribution_score']:.1f}` ({summary['interpretation']['eye_contact_distribution']})
- Alertness: `{score_block['alertness_score']:.1f}` ({summary['interpretation']['alertness']})
- Gesture smoothness: `{score_block['gesture_smoothness_score']:.1f}` ({summary['interpretation']['gesture_smoothness']})
- Stage usage: `{score_block['stage_usage_score']:.1f}`
- Heuristic nonverbal score: `{score_block['heuristic_nonverbal_score']:.1f}` ({summary['interpretation']['overall_nonverbal_signal']})

## Risks

- Static behavior risk: `{gesture['static_behavior_risk']:.1f}` ({summary['interpretation']['static_behavior_risk']})
- Excessive animation risk: `{gesture['excessive_animation_risk']:.1f}` ({summary['interpretation']['excessive_animation_risk']})
- Tension/hostility risk: `{gesture['tension_hostility_risk']:.1f}` ({summary['interpretation']['tension_hostility_risk']})
- Rigidity risk: `{gesture['rigidity_risk']:.1f}` ({summary['interpretation']['rigidity_risk']})
- Closed-posture risk: `{posture['closed_posture_risk']:.1f}` ({summary['interpretation']['closed_posture_risk']})

## Raw Metrics

- Gesture extent mean: `{raw['gesture_extent_mean']:.3f}`
- Arm span mean: `{raw['arm_span_mean']:.3f}`
- Gesture motion mean: `{raw['gesture_motion_mean']:.4f}`
- Gesture motion peak: `{raw['gesture_motion_peak']:.4f}`
- Gesture motion std: `{raw['gesture_motion_std']:.4f}`
- Open palm ratio: `{raw['open_palm_ratio']:.3f}`
- Pointing ratio: `{raw['pointing_ratio']:.3f}`
- Fist ratio: `{raw['fist_ratio']:.3f}`
- Smile proxy mean: `{raw['smile_proxy_mean']:.3f}`
- Smile proxy std: `{raw['smile_proxy_std']:.4f}`
- Mouth open mean: `{raw['mouth_open_mean']:.4f}`
- Mouth open std: `{raw['mouth_open_std']:.4f}`
- Eye open mean: `{raw['eye_open_mean']:.4f}`
- Brow-eye mean: `{raw['brow_eye_mean']:.4f}`
- Signed yaw std: `{raw['signed_yaw_std']:.4f}`
- Stage range: `{raw['stage_range']:.3f}`
- LDLJ raw: `{raw['ldlj_smoothness_raw']:.3f}`
- SAL raw: `{raw['sal_smoothness_raw']:.3f}`

## Eye-Contact Proxy

- Sector balance score: `{eye_contact['sector_balance_score']:.1f}`
- Room scan score: `{eye_contact['room_scan_score']:.1f}`
- Sector distribution: `left={eye_contact['sector_distribution']['left']}, center={eye_contact['sector_distribution']['center']}, right={eye_contact['sector_distribution']['right']}`
- Gaze transitions: `{eye_contact['gaze_transition_count']}`
- Gaze transition rate/sec: `{eye_contact['gaze_transition_rate_per_sec']:.3f}`

## Feedback

### Strengths
"""
    for item in summary["feedback"]["strengths"]:
        md += f"- {item}\n"

    md += "\n### Watch Items\n"
    for item in summary["feedback"]["watch_items"]:
        md += f"- {item}\n"

    md += "\n## Manual Review\n\n"
    md += f"- Grooming/professional appearance: `{posture['grooming_assessment']['status']}`\n"
    md += f"- Reason: {posture['grooming_assessment']['reason']}\n"
    for item in summary["category_feedback"]["manual_review_items"]:
        md += f"- {item}\n"

    md += "\n## Warnings\n\n"
    if summary["warnings"]:
        for warning in summary["warnings"]:
            md += f"- {warning}\n"
    else:
        md += "- None\n"

    md += "\n## Notes\n\n"
    for note in summary["notes"]:
        md += f"- {note}\n"

    artifacts.summary_md_path.write_text(md, encoding="utf-8")
