from __future__ import annotations

from pathlib import Path
from textwrap import fill
import json

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path("/workspace")
DOCS = ROOT / "docs"
FIG_DIR = DOCS / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def latest_dir(base: Path, pattern: str) -> Path:
    dirs = sorted([p for p in base.glob(pattern) if p.is_dir()])
    if not dirs:
        raise FileNotFoundError(f"No directories found in {base} for {pattern}")
    return dirs[-1]


def try_latest_dir(base: Path, pattern: str) -> Path | None:
    dirs = sorted([p for p in base.glob(pattern) if p.is_dir()])
    if not dirs:
        return None
    return dirs[-1]


DEBUG_RUN = latest_dir(ROOT / "artifacts" / "nonverbal_eval_debug3", "run_*")
BATCH_RUN = latest_dir(ROOT / "artifacts" / "nonverbal_eval_batch", "batch_*")
LONG_RUN = try_latest_dir(ROOT / "artifacts" / "nonverbal_eval_long", "run_*")

SUMMARY = json.loads((DEBUG_RUN / "summary.json").read_text(encoding="utf-8"))
COMPARISON = pd.read_csv(BATCH_RUN / "comparison.csv")
LONG_SUMMARY = json.loads((LONG_RUN / "summary_full.json").read_text(encoding="utf-8")) if LONG_RUN else None
LONG_WINDOWS = pd.read_csv(LONG_RUN / "window_summary.csv") if LONG_RUN else None


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titlesize": 16,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }
)


def save_fig(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG_DIR / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_pipeline_overview() -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis("off")

    boxes = [
        ((0.03, 0.67), 0.18, 0.18, "#154c79", "Input\nLecture video\n5 s clip extraction"),
        ((0.28, 0.67), 0.20, 0.18, "#1f6f8b", "Perception layer\nMediaPipe Holistic\nface / pose / hands"),
        ((0.55, 0.67), 0.19, 0.18, "#2e8b57", "Low-level cues\nyaw, gaze sector,\nsmile proxy,\narm span, motion"),
        ((0.79, 0.67), 0.18, 0.18, "#4e9f3d", "Feedback outputs\nscores, risks,\ndebug video,\nsummary report"),
        ((0.18, 0.28), 0.20, 0.18, "#7b2cbf", "Gesture & affect\nnatural movement\npositive affect\nenthusiasm"),
        ((0.42, 0.28), 0.20, 0.18, "#c77dff", "Posture & presence\nupright posture\nconfidence / openness\nmanual grooming review"),
        ((0.66, 0.28), 0.20, 0.18, "#ff7b00", "Eye contact & engagement\naudience orientation\nsector balance\nroom scan / alertness"),
    ]

    for (x, y), w, h, color, text in boxes:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="white", linewidth=2, alpha=0.92))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white", fontsize=12, weight="bold")

    arrows = [
        ((0.21, 0.76), (0.28, 0.76)),
        ((0.48, 0.76), (0.55, 0.76)),
        ((0.74, 0.76), (0.79, 0.76)),
        ((0.64, 0.67), (0.28, 0.46)),
        ((0.64, 0.67), (0.52, 0.46)),
        ((0.64, 0.67), (0.76, 0.46)),
        ((0.28, 0.37), (0.79, 0.70)),
        ((0.62, 0.37), (0.83, 0.67)),
        ((0.86, 0.37), (0.87, 0.67)),
    ]
    for start, end in arrows:
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=18,
                linewidth=2,
                color="#333333",
                connectionstyle="arc3,rad=0.0",
            )
        )

    ax.text(
        0.03,
        0.05,
        "Figure 1. System architecture used in the current prototype. The design is feature-first rather than end-to-end:\n"
        "existing landmark models produce interpretable cues, which are aggregated into feedback categories and debug artifacts.",
        fontsize=11,
        color="#222222",
    )
    save_fig(fig, "figure_01_pipeline_overview.png")


def fig_traceability_matrix() -> None:
    metrics = [
        "Natural movement",
        "Positive affect",
        "Enthusiasm",
        "Posture stability",
        "Confidence / openness",
        "Audience orientation",
        "Eye-contact distribution",
        "Alertness",
        "Pointing / gesture guidance",
        "Manual grooming review",
        "Interpretable feature-first design",
        "Formative-not-high-stakes use",
    ]
    papers = [
        "Tikochinski et al. 2025",
        "Wang et al. 2022",
        "Pi et al. 2020",
        "Kuang et al. 2023",
        "Smidekova et al. 2020",
        "Pi et al. 2019",
        "Beege et al. 2022",
        "Pan et al. 2022",
        "Ahuja et al. 2019",
        "Pang et al. 2023",
        "Renier et al. 2021",
        "Fütterer et al. 2026",
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
            [0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 3, 3, 1, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3],
        ],
        dtype=float,
    )

    fig, ax = plt.subplots(figsize=(16, 9))
    im = ax.imshow(matrix, cmap="YlGnBu", aspect="auto", vmin=0, vmax=3)
    ax.set_xticks(np.arange(len(papers)))
    ax.set_xticklabels(papers, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(metrics)))
    ax.set_yticklabels(metrics)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            text = "" if matrix[i, j] == 0 else {1: "minor", 2: "moderate", 3: "major"}[int(matrix[i, j])]
            ax.text(j, i, text, ha="center", va="center", color="black", fontsize=8)

    ax.set_title("Figure 2. Metric-to-literature traceability matrix")
    cbar = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
    cbar.set_label("Influence on implementation")
    save_fig(fig, "figure_02_traceability_matrix.png")


def fig_automation_boundary() -> None:
    items = [
        ("Natural movement", 0.22, 0.78, "#1f77b4"),
        ("Positive affect", 0.52, 0.78, "#1f77b4"),
        ("Posture stability", 0.78, 0.78, "#1f77b4"),
        ("Eye-contact distribution", 0.22, 0.36, "#1f77b4"),
        ("Alertness", 0.52, 0.36, "#1f77b4"),
        ("Pointing/open palm", 0.78, 0.36, "#1f77b4"),
        ("Grooming / attire", 0.22, 0.10, "#d94841"),
        ("Hostility labeling", 0.52, 0.10, "#d94841"),
        ("High-stakes quality score", 0.78, 0.10, "#d94841"),
    ]

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axhline(0.5, color="#333333", linewidth=1.5)
    ax.axvline(0.5, color="#333333", linewidth=1.5)
    ax.set_xticks([0.25, 0.75])
    ax.set_xticklabels(["Lower fairness / validity risk", "Higher fairness / validity risk"])
    ax.set_yticks([0.25, 0.75])
    ax.set_yticklabels(["Weaker evidence for automation", "Stronger evidence for automation"])
    ax.set_title("Figure 3. Automation boundary used in the prototype")

    quadrant_labels = [
        (0.25, 0.92, "Automate with confidence"),
        (0.75, 0.92, "Automate cautiously"),
        (0.25, 0.42, "Needs more evidence"),
        (0.75, 0.42, "Keep manual or formative only"),
    ]
    for x, y, text in quadrant_labels:
        ax.text(x, y, text, ha="center", va="center", fontsize=12, weight="bold")

    for label, x, y, color in items:
        ax.scatter(x, y, s=260, color=color, alpha=0.88, edgecolor="white", linewidth=1.4)
        ax.text(x, y - 0.045, label, ha="center", va="top", fontsize=10, weight="bold")

    ax.set_frame_on(False)
    save_fig(fig, "figure_03_automation_boundary.png")


def fig_evidence_panel() -> None:
    keyframe = np.array(Image.open(DEBUG_RUN / "keyframe_annotated.jpg").convert("RGB"))
    timelines = np.array(Image.open(DEBUG_RUN / "metric_timelines.png").convert("RGB"))
    contact_sheet = np.array(Image.open(DEBUG_RUN / "debug_contact_sheet.jpg").convert("RGB"))

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes[0, 0].imshow(keyframe)
    axes[0, 0].set_title("A. Annotated keyframe")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(timelines)
    axes[0, 1].set_title("B. Metric timelines over the 5 s clip")
    axes[0, 1].axis("off")

    axes[1, 0].imshow(contact_sheet)
    axes[1, 0].set_title("C. Debug contact sheet")
    axes[1, 0].axis("off")

    axes[1, 1].axis("off")
    lines = [
        f"Best clip used in detailed debugging: start={SUMMARY['clip']['start_sec']:.0f}s, duration={SUMMARY['clip']['duration_sec_actual']:.2f}s",
        f"Pose / face / hand coverage: {SUMMARY['quality_control']['pose_coverage']:.2f} / {SUMMARY['quality_control']['face_coverage']:.2f} / {SUMMARY['quality_control']['hand_coverage']:.2f}",
        f"Natural movement={SUMMARY['scores']['natural_movement_score']:.1f}, positive affect={SUMMARY['scores']['positive_affect_score']:.1f}, confidence/presence={SUMMARY['scores']['confidence_presence_score']:.1f}",
        f"Eye-contact distribution={SUMMARY['scores']['eye_contact_distribution_score']:.1f}, alertness={SUMMARY['scores']['alertness_score']:.1f}, overall={SUMMARY['scores']['heuristic_nonverbal_score']:.1f}",
        "The panel combines the exact local artifacts used to inspect scoring quality and tune the prototype.",
    ]
    axes[1, 1].text(0.02, 0.95, fill("\n".join(lines), 52), va="top", fontsize=12)
    axes[1, 1].set_title("D. Experimental evidence summary")

    fig.suptitle("Figure 4. Empirical evidence package used for manual review and tuning", fontsize=18, y=0.98)
    fig.tight_layout()
    save_fig(fig, "figure_04_evidence_panel.png")


def fig_segment_comparison() -> None:
    df = COMPARISON.sort_values("start_sec").copy()
    fig, ax = plt.subplots(figsize=(12, 7))
    y = np.arange(len(df))
    ax.barh(y - 0.18, df["heuristic_nonverbal_score"], height=0.22, color="#264653", label="Overall")
    ax.barh(y + 0.04, df["eye_contact_distribution_score"], height=0.22, color="#2a9d8f", label="Eye contact")
    ax.barh(y + 0.26, df["natural_movement_score"], height=0.22, color="#e9c46a", label="Natural movement")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{int(v)} s" for v in df["start_sec"]])
    ax.set_xlabel("Score")
    ax.set_title("Figure 5. Segment comparison on major positive dimensions")
    ax.legend(loc="lower right")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    save_fig(fig, "figure_05_segment_comparison.png")


def fig_score_profile() -> None:
    pos_labels = [
        "Natural movement",
        "Positive affect",
        "Enthusiasm",
        "Posture",
        "Confidence",
        "Eye contact",
        "Alertness",
    ]
    pos_values = [
        SUMMARY["scores"]["natural_movement_score"],
        SUMMARY["scores"]["positive_affect_score"],
        SUMMARY["scores"]["enthusiasm_score"],
        SUMMARY["scores"]["posture_stability_score"],
        SUMMARY["scores"]["confidence_presence_score"],
        SUMMARY["scores"]["eye_contact_distribution_score"],
        SUMMARY["scores"]["alertness_score"],
    ]
    risk_labels = ["Static", "Excessive", "Tension", "Rigidity", "Closed posture"]
    risk_values = [
        SUMMARY["category_feedback"]["gesture_and_facial_expression"]["static_behavior_risk"],
        SUMMARY["category_feedback"]["gesture_and_facial_expression"]["excessive_animation_risk"],
        SUMMARY["category_feedback"]["gesture_and_facial_expression"]["tension_hostility_risk"],
        SUMMARY["category_feedback"]["gesture_and_facial_expression"]["rigidity_risk"],
        SUMMARY["category_feedback"]["posture_and_presence"]["closed_posture_risk"],
    ]

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    axes[0].barh(pos_labels, pos_values, color="#1d3557")
    axes[0].set_xlim(0, 100)
    axes[0].invert_yaxis()
    axes[0].set_title("Positive dimensions")
    axes[0].grid(axis="x", linestyle="--", alpha=0.3)

    axes[1].barh(risk_labels, risk_values, color="#d62828")
    axes[1].set_xlim(0, 100)
    axes[1].invert_yaxis()
    axes[1].set_title("Risk flags")
    axes[1].grid(axis="x", linestyle="--", alpha=0.3)

    fig.suptitle("Figure 6. Score profile of the best-debugged 5 s segment", fontsize=17)
    fig.tight_layout()
    save_fig(fig, "figure_06_score_profile.png")


def fig_long_run_scores() -> None:
    if LONG_RUN is None or LONG_WINDOWS is None or LONG_SUMMARY is None:
        return

    df = LONG_WINDOWS.sort_values("window_start_sec").copy()
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df["window_start_sec"], df["heuristic_nonverbal_score"], label="Overall", color="#1d3557", linewidth=2.4)
    ax.plot(df["window_start_sec"], df["eye_contact_distribution_score"], label="Eye contact", color="#2a9d8f", linewidth=2.0)
    ax.plot(df["window_start_sec"], df["confidence_presence_score"], label="Confidence", color="#f4a261", linewidth=2.0)
    ax.plot(df["window_start_sec"], df["natural_movement_score"], label="Natural movement", color="#e76f51", linewidth=2.0)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Window start (s)")
    ax.set_ylabel("Score")
    ax.set_title("Figure 7. Score trends from the extended context-window run")
    ax.grid(alpha=0.25, linestyle="--")
    ax.legend(loc="lower left", ncol=2)

    clip_start = LONG_SUMMARY["clip"]["start_sec"]
    clip_sec = LONG_SUMMARY["clip"]["duration_sec_actual"]
    ax.text(
        0.99,
        0.02,
        f"start={clip_start:.1f}s | duration={clip_sec:.1f}s | windows={len(df)} | overall={LONG_SUMMARY['scores']['heuristic_nonverbal_score']:.1f}",
        ha="right",
        va="bottom",
        transform=ax.transAxes,
        fontsize=10,
        bbox={"facecolor": "white", "alpha": 0.86, "edgecolor": "#cccccc"},
    )
    save_fig(fig, "figure_07_long_run_scores.png")


def fig_long_run_windows() -> None:
    if LONG_RUN is None or LONG_WINDOWS is None:
        return

    df = LONG_WINDOWS.sort_values("heuristic_nonverbal_score", ascending=False).copy()
    top = df.head(5).copy().sort_values("window_start_sec")
    bottom = df.tail(5).copy().sort_values("window_start_sec")

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=False)

    axes[0].barh(
        [f"{int(s)}-{int(e)}s" for s, e in zip(top["window_start_sec"], top["window_end_sec"])],
        top["heuristic_nonverbal_score"],
        color="#2a9d8f",
    )
    axes[0].set_xlim(0, 100)
    axes[0].set_title("Top 5 lecture windows by overall score")
    axes[0].grid(axis="x", linestyle="--", alpha=0.25)

    axes[1].barh(
        [f"{int(s)}-{int(e)}s" for s, e in zip(bottom["window_start_sec"], bottom["window_end_sec"])],
        bottom["heuristic_nonverbal_score"],
        color="#d62828",
    )
    axes[1].set_xlim(0, 100)
    axes[1].set_title("Bottom 5 lecture windows by overall score")
    axes[1].grid(axis="x", linestyle="--", alpha=0.25)

    fig.suptitle("Figure 8. Best and weakest windows from the extended context run", fontsize=17)
    fig.tight_layout()
    save_fig(fig, "figure_08_long_run_windows.png")


def main() -> None:
    fig_pipeline_overview()
    fig_traceability_matrix()
    fig_automation_boundary()
    fig_evidence_panel()
    fig_segment_comparison()
    fig_score_profile()
    fig_long_run_scores()
    fig_long_run_windows()
    print(f"Generated figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
