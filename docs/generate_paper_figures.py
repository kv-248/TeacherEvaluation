from __future__ import annotations

from pathlib import Path
import json

import cv2
import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path("/workspace")
DOCS = ROOT / "docs"
FIG_DIR = DOCS / "paper_figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

DEBUG_RUN = ROOT / "artifacts" / "nonverbal_eval_debug3" / "run_20260315T193444Z"
BATCH_RUN = ROOT / "artifacts" / "nonverbal_eval_batch" / "batch_20260315T191630Z"
LONG_RUN = ROOT / "artifacts" / "nonverbal_eval_long" / "run_20260315T202856Z"

SUMMARY = json.loads((DEBUG_RUN / "summary.json").read_text(encoding="utf-8"))
COMPARISON = pd.read_csv(BATCH_RUN / "comparison.csv")
LONG_SUMMARY = json.loads((LONG_RUN / "summary_full.json").read_text(encoding="utf-8"))
LONG_WINDOWS = pd.read_csv(LONG_RUN / "window_summary.csv")


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
)

TEXT = "#1d2a33"
BLUE = "#2f5d80"
GREEN = "#5b8a72"
SAND = "#d9c7a2"
RUST = "#b65f3c"
INK = "#37474f"
RED = "#a8403a"


def save_fig(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG_DIR / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        0.01,
        0.98,
        label,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=12,
        fontweight="bold",
        color=TEXT,
        bbox={"facecolor": "white", "edgecolor": "#c5d0d6", "pad": 2.5},
    )


def fig_01_architecture() -> None:
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    ax.axis("off")

    columns = [
        (0.04, 0.22, BLUE, "Input video", ["lecture excerpt", "clip/window selection", "frame sampling"]),
        (0.29, 0.24, GREEN, "Perception", ["face landmarks", "pose landmarks", "hand landmarks"]),
        (0.56, 0.24, SAND, "Derived cues", ["orientation", "posture", "gesture motion", "facial proxies", "sector allocation"]),
        (0.82, 0.14, RUST, "Aggregates", ["scores", "risk flags", "feedback text", "debug artifacts"]),
    ]

    for x, w, color, title, items in columns:
        y, h = 0.38, 0.34
        rect = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            facecolor=color,
            edgecolor="none",
            alpha=0.92,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h - 0.06, title, ha="center", va="center", color="white", fontsize=13, fontweight="bold")
        for idx, item in enumerate(items):
            ax.text(x + 0.02, y + h - 0.12 - idx * 0.055, f"- {item}", ha="left", va="center", color="white", fontsize=10)

    arrows = [(0.26, 0.55, 0.29, 0.55), (0.53, 0.55, 0.56, 0.55), (0.80, 0.55, 0.82, 0.55)]
    for x1, y1, x2, y2 in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops={"arrowstyle": "-|>", "lw": 1.8, "color": INK})

    ax.text(0.05, 0.17, "The pipeline is feature-first: pretrained landmark detectors drive interpretable low-level cues, which are then aggregated into\nteacher-facing nonverbal indicators and diagnostic evidence rather than an opaque end-to-end quality score.", fontsize=10.2, color=TEXT)
    save_fig(fig, "figure_01_architecture.png")


def fig_02_operationalization() -> None:
    fig, ax = plt.subplots(figsize=(13.2, 7.8))
    ax.axis("off")

    left_x, mid_x, right_x = 0.06, 0.39, 0.73
    box_w, box_h = 0.20, 0.11

    left = [
        ("Face landmarks", 0.78, BLUE),
        ("Pose landmarks", 0.58, GREEN),
        ("Hand landmarks", 0.38, RUST),
        ("Temporal traces", 0.18, INK),
    ]
    mid = [
        ("face-front, yaw,\nsmile, eye openness", 0.78, BLUE),
        ("posture, arm span,\nstage range", 0.58, GREEN),
        ("pointing, open palm,\nhand activity", 0.38, RUST),
        ("motion smoothness,\nsector transitions", 0.18, INK),
    ]
    right = [
        ("Audience orientation\nEye-contact distribution\nAlertness", 0.74, BLUE),
        ("Posture stability\nConfidence / presence", 0.53, GREEN),
        ("Natural movement\nPositive affect\nEnthusiasm", 0.32, RUST),
        ("Static / excessive /\nrigidity risk flags", 0.11, RED),
    ]

    def draw_group(items, x, w):
        for label, y, color in items:
            rect = patches.FancyBboxPatch(
                (x, y),
                w,
                box_h,
                boxstyle="round,pad=0.01,rounding_size=0.02",
                facecolor=color,
                edgecolor="none",
                alpha=0.9,
            )
            ax.add_patch(rect)
            ax.text(x + w / 2, y + box_h / 2, label, ha="center", va="center", color="white", fontsize=10.5, fontweight="bold")

    draw_group(left, left_x, box_w)
    draw_group(mid, mid_x, box_w + 0.03)
    draw_group(right, right_x, box_w + 0.04)

    for (_, y1, _), (_, y2, _) in zip(left, mid):
        ax.annotate("", xy=(mid_x, y2 + box_h / 2), xytext=(left_x + box_w, y1 + box_h / 2), arrowprops={"arrowstyle": "-|>", "lw": 1.7, "color": "#546e7a"})
    for (_, y1, _), (_, y2, _) in zip(mid, right):
        ax.annotate("", xy=(right_x, y2 + box_h / 2), xytext=(mid_x + box_w + 0.03, y1 + box_h / 2), arrowprops={"arrowstyle": "-|>", "lw": 1.7, "color": "#546e7a"})

    ax.text(0.06, 0.02, "Operationalization structure used in the manuscript: observable landmark signals are transformed into low-level cues and then into interpretable\nmetric families. The manuscript treats the right-most boxes as heuristic evaluation constructs rather than direct psychometric measurements.", fontsize=10, color=TEXT)
    save_fig(fig, "figure_02_operationalization.png")


def fig_03_traceability() -> None:
    metrics = [
        "Natural movement",
        "Positive affect",
        "Enthusiasm",
        "Posture stability",
        "Confidence / presence",
        "Audience orientation",
        "Eye-contact distribution",
        "Alertness",
        "Gesture guidance",
    ]
    papers = [
        "Tikochinski 2025",
        "Wang 2022",
        "Pi 2020",
        "Kuang 2023",
        "Smidekova 2020",
        "Pi 2019",
        "Beege 2022",
        "Pan 2022",
        "Ahuja 2019",
        "Pang 2023",
        "Renier 2021",
        "Fütterer 2026",
    ]
    matrix = np.array(
        [
            [3, 2, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
            [3, 2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [3, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 3, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 2, 0, 0],
            [0, 0, 3, 3, 2, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 2, 3, 3, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        dtype=float,
    )

    fig, ax = plt.subplots(figsize=(13.8, 8.4))
    im = ax.imshow(matrix, cmap="Blues", aspect="auto", vmin=0, vmax=3)
    ax.set_xticks(np.arange(len(papers)))
    ax.set_xticklabels(papers, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(metrics)))
    ax.set_yticklabels(metrics)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j] > 0:
                ax.text(j, i, int(matrix[i, j]), ha="center", va="center", fontsize=8.5, color="black")
    ax.set_xlabel("Literature sources")
    ax.set_ylabel("Implemented metric families")
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Influence level")
    save_fig(fig, "figure_03_traceability.png")


def fig_04_protocol() -> None:
    fig, ax = plt.subplots(figsize=(13.2, 4.8))
    ax.set_xlim(0, 242.1)
    ax.set_ylim(0, 5)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_yticks([])
    ax.set_xlabel("Source video time (s)")

    ax.hlines(4.2, 0, 242.0, color=INK, linewidth=3)
    ax.text(0, 4.55, "Source lecture excerpt", fontsize=10.5, color=TEXT, fontweight="bold")

    batch_starts = [60, 90, 120, 150]
    for start in batch_starts:
        ax.add_patch(patches.Rectangle((start, 3.25), 5, 0.5, facecolor=GREEN, alpha=0.95))
        ax.text(start + 2.5, 3.9, f"{start}-{start+5}", ha="center", va="bottom", fontsize=8.5, color=TEXT)
    ax.text(0, 3.15, "Four 5 s comparison clips", fontsize=10.5, color=TEXT, fontweight="bold")

    ax.add_patch(patches.Rectangle((120, 2.2), 5, 0.5, facecolor=RUST, alpha=0.98))
    ax.text(122.5, 2.85, "Detailed debug clip", ha="center", va="bottom", fontsize=9, color=TEXT)

    ax.add_patch(patches.Rectangle((92.5, 1.1), 60, 0.5, facecolor=BLUE, alpha=0.92))
    ax.text(122.5, 1.75, "60 s context window at 12 fps", ha="center", va="bottom", fontsize=9.5, color=TEXT)
    for start in [92.5, 107.5, 122.5, 137.5]:
        ax.add_patch(patches.Rectangle((start, 0.15), 15, 0.45, facecolor=SAND, alpha=0.95, edgecolor="white"))
        ax.text(start + 7.5, 0.72, f"{start:.1f}-{start+15:.1f}", ha="center", va="bottom", fontsize=7.8, color=TEXT)
    ax.text(0, 0.08, "Four non-overlapping 15 s analysis windows", fontsize=10, color=TEXT, fontweight="bold")

    ax.set_xticks([0, 60, 90, 120, 150, 180, 210, 240])
    save_fig(fig, "figure_04_protocol.png")


def fig_05_qualitative_panel() -> None:
    keyframe = np.array(Image.open(DEBUG_RUN / "keyframe_annotated.jpg").convert("RGB"))
    timelines = np.array(Image.open(DEBUG_RUN / "metric_timelines.png").convert("RGB"))
    contact_sheet = np.array(Image.open(DEBUG_RUN / "debug_contact_sheet.jpg").convert("RGB"))

    fig, axes = plt.subplots(2, 2, figsize=(15.5, 11.5))
    axes[0, 0].imshow(keyframe)
    axes[0, 0].axis("off")
    panel_label(axes[0, 0], "A")

    axes[0, 1].imshow(timelines)
    axes[0, 1].axis("off")
    panel_label(axes[0, 1], "B")

    axes[1, 0].imshow(contact_sheet)
    axes[1, 0].axis("off")
    panel_label(axes[1, 0], "C")

    axes[1, 1].axis("off")
    panel_label(axes[1, 1], "D")
    text = [
        "5 s debug segment:",
        f"start={SUMMARY['clip']['start_sec']:.0f}s, duration={SUMMARY['clip']['duration_sec_actual']:.2f}s",
        f"pose/face/hand coverage={SUMMARY['quality_control']['pose_coverage']:.2f}/{SUMMARY['quality_control']['face_coverage']:.2f}/{SUMMARY['quality_control']['hand_coverage']:.2f}",
        "",
        "Key clip-level scores:",
        f"natural movement={SUMMARY['scores']['natural_movement_score']:.1f}",
        f"positive affect={SUMMARY['scores']['positive_affect_score']:.1f}",
        f"confidence/presence={SUMMARY['scores']['confidence_presence_score']:.1f}",
        f"eye-contact distribution={SUMMARY['scores']['eye_contact_distribution_score']:.1f}",
        f"alertness={SUMMARY['scores']['alertness_score']:.1f}",
        f"overall={SUMMARY['scores']['heuristic_nonverbal_score']:.1f}",
    ]
    axes[1, 1].text(0.06, 0.94, "\n".join(text), va="top", ha="left", fontsize=11, color=TEXT)

    fig.tight_layout()
    save_fig(fig, "figure_05_qualitative_panel.png")


def fig_06_short_segment_heatmap() -> None:
    df = COMPARISON.sort_values("start_sec").copy()
    cols = [
        "heuristic_nonverbal_score",
        "natural_movement_score",
        "positive_affect_score",
        "eye_contact_distribution_score",
        "alertness_score",
        "excessive_animation_risk",
    ]
    labels = ["Overall", "Natural", "Affect", "Eye contact", "Alertness", "Excessive risk"]
    arr = df[cols].to_numpy()

    fig, ax = plt.subplots(figsize=(9.8, 4.8))
    im = ax.imshow(arr, cmap="YlGnBu", aspect="auto", vmin=0, vmax=100)
    ax.set_yticks(np.arange(len(df)))
    ax.set_yticklabels([f"{int(v)} s" for v in df["start_sec"]])
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            ax.text(j, i, f"{arr[i, j]:.1f}", ha="center", va="center", fontsize=8.5, color="black")
    ax.set_ylabel("5 s segment start time")
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Score")
    save_fig(fig, "figure_06_short_segments.png")


def fig_07_context_trends() -> None:
    df = LONG_WINDOWS.sort_values("window_start_sec").copy()
    x = df["window_start_sec"].to_numpy()

    fig, ax = plt.subplots(figsize=(10.6, 5.4))
    ax.plot(x, df["heuristic_nonverbal_score"], color=BLUE, marker="o", linewidth=2.3, label="Overall")
    ax.plot(x, df["eye_contact_distribution_score"], color=GREEN, marker="s", linewidth=2.0, label="Eye contact")
    ax.plot(x, df["natural_movement_score"], color=RUST, marker="^", linewidth=2.0, label="Natural movement")
    ax.plot(x, df["excessive_animation_risk"], color=RED, marker="D", linewidth=1.8, linestyle="--", label="Excessive risk")
    ax.axvline(120.0, color="#757575", linewidth=1.1, linestyle=":")
    ax.text(120.5, 97, "Detailed 5 s clip region", fontsize=8.5, color="#555555", va="top")
    ax.set_xlim(90, 155)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Source video time (s)")
    ax.set_ylabel("Score")
    ax.legend(loc="lower right", ncol=2, frameon=False)
    ax.grid(alpha=0.25, linestyle="--")
    save_fig(fig, "figure_07_context_trends.png")


def fig_08_context_subwindows() -> None:
    df = LONG_WINDOWS.sort_values("window_start_sec").copy()
    labels = [f"{row.window_start_sec:.1f}-{row.window_end_sec:.1f}" for row in df.itertuples()]
    y = np.arange(len(df))

    fig, ax = plt.subplots(figsize=(11.2, 5.6))
    width = 0.18
    ax.barh(y - 1.5 * width, df["heuristic_nonverbal_score"], height=width, color=BLUE, label="Overall")
    ax.barh(y - 0.5 * width, df["natural_movement_score"], height=width, color=RUST, label="Natural")
    ax.barh(y + 0.5 * width, df["eye_contact_distribution_score"], height=width, color=GREEN, label="Eye contact")
    ax.barh(y + 1.5 * width, df["excessive_animation_risk"], height=width, color=RED, label="Excessive risk")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score")
    ax.set_ylabel("60 s context subwindows")
    ax.legend(loc="lower right", ncol=2, frameon=False)
    ax.grid(axis="x", alpha=0.25, linestyle="--")
    save_fig(fig, "figure_08_context_subwindows.png")


def fig_09_debug_video_outputs() -> None:
    video_path = DEBUG_RUN / "debug_overlay.mp4"
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open debug video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_indices = sorted({0, max(frame_count // 3, 0), max((2 * frame_count) // 3, 0), max(frame_count - 1, 0)})

    frames: list[np.ndarray] = []
    labels: list[str] = []
    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(rgb)
        labels.append(f"{idx / fps:.2f} s")
    cap.release()

    if not frames:
        raise RuntimeError("No frames were extracted from the debug video.")

    fig, axes = plt.subplots(2, 2, figsize=(15.6, 10.2))
    axes = axes.flatten()
    for ax, frame, label, panel in zip(axes, frames, labels, ["A", "B", "C", "D"]):
        ax.imshow(frame)
        ax.axis("off")
        panel_label(ax, panel)
        ax.text(
            0.98,
            0.03,
            label,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="white",
            bbox={"facecolor": "black", "alpha": 0.6, "pad": 3},
        )
    for ax in axes[len(frames):]:
        ax.axis("off")

    fig.tight_layout()
    save_fig(fig, "figure_09_debug_video_outputs.png")


def _first_frame_rgb(video_path: Path) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not read first frame from {video_path}")
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def fig_10_cross_video_first_frames() -> None:
    videos = [
        (
            ROOT / "Lecture_1_cut_1m_to_5m.mp4",
            "A",
            "Lecture_1_cut_1m_to_5m.mp4",
            "Primary lecture benchmark",
        ),
        (
            ROOT / "clipped_precise2.mp4",
            "B",
            "clipped_precise2.mp4",
            "Note-reading dominated stress case",
        ),
        (
            ROOT / "clip_5min.mp4",
            "C",
            "clip_5min.mp4",
            "Longer lecture clip; first 60 s analyzed",
        ),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15.6, 5.5))
    for ax, (video_path, panel, title, subtitle) in zip(axes, videos):
        frame = _first_frame_rgb(video_path)
        ax.imshow(frame)
        ax.axis("off")
        panel_label(ax, panel)
        ax.text(
            0.5,
            -0.08,
            title,
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=10,
            color=TEXT,
            fontweight="bold",
        )
        ax.text(
            0.5,
            -0.17,
            subtitle,
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=8.9,
            color=INK,
        )
    fig.tight_layout()
    save_fig(fig, "figure_10_cross_video_first_frames.png")


def main() -> None:
    fig_01_architecture()
    fig_02_operationalization()
    fig_03_traceability()
    fig_04_protocol()
    fig_05_qualitative_panel()
    fig_06_short_segment_heatmap()
    fig_07_context_trends()
    fig_08_context_subwindows()
    fig_09_debug_video_outputs()
    fig_10_cross_video_first_frames()
    print(f"Generated figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
