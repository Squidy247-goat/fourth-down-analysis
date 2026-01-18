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
RAVENS_COLOR = "#3B2C8E"
LEAGUE_GRAY = "#808080"
TITLE_BLUE = "#0033A0"

TITLE_TEXT = "Giants vs Ravens: A Decade of Divergence (2016-2025)"
ANNOTATION_TEXT = "Giants: 55-109-1 (.336)\nRavens: 103-62 (.624)"


def main():
    years = list(range(2016, 2026))
    giants_values = [11, 3, 5, 4, 6, 4, 9, 6, 3, 4]
    ravens_values = [8, 9, 10, 14, 11, 8, 10, 13, 12, 8]

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.titlesize": 22,
            "axes.titleweight": "bold",
            "axes.labelsize": 14,
            "axes.labelweight": "bold",
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 12,
        }
    )

    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)

    bar_width = 0.35
    group_spacing = 0.1
    x_positions = np.arange(len(years)) * (2 * bar_width + group_spacing)

    giants_bars = ax.bar(
        x_positions - bar_width / 2,
        giants_values,
        width=bar_width,
        color=GIANTS_COLOR,
        label="Giants",
        zorder=2,
    )
    ravens_bars = ax.bar(
        x_positions + bar_width / 2,
        ravens_values,
        width=bar_width,
        color=RAVENS_COLOR,
        label="Ravens",
        zorder=2,
    )

    ax.set_title(TITLE_TEXT, pad=20, color=TITLE_BLUE, fontweight="bold")
    ax.set_xlabel("Season")
    ax.set_ylabel("Regular Season Wins")

    ax.set_xticks(x_positions)
    ax.set_xticklabels(years)
    ax.set_ylim(0, 15)
    ax.set_yticks(range(0, 16, 3))

    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#D3D3D3", linewidth=0.8)
    ax.grid(axis="x", visible=False)

    ax.legend(loc="upper right", frameon=False)
    leg = ax.get_legend()
    if leg:
        for t in leg.get_texts():
            t.set_fontweight("bold")

    for bars in (giants_bars, ravens_bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.2,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold",
            )

    ax.text(
        0.02,
        0.98,
        ANNOTATION_TEXT,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
        bbox=dict(facecolor="#FFFFFF", edgecolor="#D3D3D3", boxstyle="round,pad=0.4"),
    )

    plt.tight_layout(pad=2.0)

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "giants_ravens_wins_grouped_bar.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
