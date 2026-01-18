from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mpl-cache"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BACKGROUND_COLOR = "#F7E6CE"
GIANTS_COLOR = "#0B2265"
LEAGUE_COLOR = "#808080"
GRID_COLOR = "#D3D3D3"
DELTA_RED = "#C41E3A"
TEXT_DARK = "#1a1a1a"


def add_value_label(ax, value, y_pos):
    ax.annotate(
        f"{value:.2f}%",
        xy=(value, y_pos),
        xytext=(4, 0),  # 1–2 points of padding (slightly more for readability)
        textcoords="offset points",
        va="center",
        ha="left",
        fontsize=11,
        fontweight="bold",
        color=TEXT_DARK,
        zorder=5,
    )


def add_delta_text(ax, delta_text, x_center, y_center):
    ax.text(
        x_center,
        y_center,
        f"Δ {delta_text}",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color=DELTA_RED,
        zorder=5,
    )


def main():
    panels = [
        {
            "title": "Third Down Conversion %",
            "giants": 32.34,
            "league": 36.30,
            "delta": "-3.96%",
        },
        {
            "title": "Red Zone TD %",
            "giants": 49.89,
            "league": 56.25,
            "delta": "-6.36%",
        },
        {
            "title": "One-Score Game Win %",
            "giants": 42.39,
            "league": 50.00,
            "delta": "-7.61%",
        },
    ]

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            # Use a more modern macOS font stack (falls back safely).
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "axes.labelweight": "bold",
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        }
    )

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)
    fig.subplots_adjust(wspace=0.4, top=0.78, bottom=0.22)
    fig.patch.set_facecolor(BACKGROUND_COLOR)

    # Bar geometry: height=0.35 with 0.15 gap between bars
    bar_height = 0.35
    y_gap = 0.15
    center_distance = bar_height + y_gap  # distance between bar centers
    y_positions = np.array([center_distance / 2, -center_distance / 2])  # Giants top
    y_labels = ["Giants", "League Avg"]

    for ax, panel in zip(axes, panels):
        ax.set_facecolor(BACKGROUND_COLOR)

        ax.barh(
            y_positions[0],
            panel["giants"],
            height=bar_height,
            color=GIANTS_COLOR,
            zorder=3,
        )
        ax.barh(
            y_positions[1],
            panel["league"],
            height=bar_height,
            color=LEAGUE_COLOR,
            zorder=3,
        )

        add_value_label(ax, panel["giants"], y_positions[0])
        add_value_label(ax, panel["league"], y_positions[1])
        add_delta_text(ax, panel["delta"], x_center=32.5, y_center=0.0)

        ax.set_title(panel["title"], pad=10, fontsize=13, fontweight="bold", color="black")
        ax.set_xlim(0, 65)
        ax.set_xticks(range(0, 61, 10))
        ax.set_yticks(y_positions)
        ax.set_yticklabels(y_labels, fontsize=10, color="black", fontweight="bold")
        ax.tick_params(axis="y", length=0, pad=5)
        ax.tick_params(axis="x", labelsize=10)
        for label in ax.get_yticklabels():
            label.set_ha("right")
            label.set_fontweight("bold")
        for label in ax.get_xticklabels():
            label.set_fontweight("bold")

        ax.grid(axis="x", color=GRID_COLOR, linewidth=0.5, alpha=0.6, zorder=0)
        ax.grid(axis="y", visible=False)
        ax.set_axisbelow(True)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(True)

    fig.suptitle(
        "Giants Critical Situation Performance (2016-2025)",
        fontsize=28,
        fontweight="bold",
        color="black",
        y=0.96,
    )
    fig.supxlabel("Percentage (%)", fontsize=13, fontweight="bold", color="black")
    fig.text(
        0.5,
        -0.05,
        "Data represents ~7 wins lost annually due to execution failures",
        ha="center",
        va="bottom",
        fontsize=11,
        fontstyle="italic",
        color="#404040",
        bbox=dict(
            facecolor="#FFFACD",
            edgecolor="none",
            alpha=0.3,
            boxstyle="round,pad=0.45",
        ),
    )

    plt.tight_layout(pad=2.5)

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "giants_critical_situations_three_panel.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
