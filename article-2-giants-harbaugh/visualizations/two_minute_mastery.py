from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mpl-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BACKGROUND_COLOR = "#F7E6CE"

RAVENS_PURPLE = "#241773"
LEAGUE_GRAY = "#808080"
GRID_GRAY = "#D3D3D3"
EXPECTED_SHADE = "#E8E8E8"
TITLE_BLUE = "#0033A0"

GREEN = "#2D7A3E"
RED = "#C41E3A"


def main():
    # Data
    points_scored = 4.21
    points_allowed = 1.94

    harbaugh_win_pct = 82.6
    expected_low = 75.0
    expected_high = 80.0

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.labelsize": 14,
            "axes.labelweight": "bold",
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 11,
        }
    )

    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(12, 6),
        dpi=300,
        gridspec_kw={"width_ratios": [1, 1], "wspace": 0.3},
    )
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax1.set_facecolor(BACKGROUND_COLOR)
    ax2.set_facecolor(BACKGROUND_COLOR)

    # Panel 1: Points scored vs allowed
    categories = ["Scored", "Allowed"]
    values = [points_scored, points_allowed]
    colors = [GREEN, RED]

    x = [0, 1]
    bars = ax1.bar(x, values, color=colors, width=0.5, zorder=3)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.set_ylim(0, 5.5)
    ax1.set_ylabel("Points Per Game")
    ax1.set_title(
        "Two-Minute Drill Points",
        pad=5,
        fontsize=16,
        fontweight="bold",
        color="black",
        y=0.97,
    )

    ax1.set_axisbelow(True)
    ax1.set_yticks([0, 1, 2, 3, 4, 5])
    ax1.grid(axis="y", color=GRID_GRAY, linewidth=0.5, alpha=0.5, zorder=0)
    ax1.grid(axis="x", visible=False)
    for spine in ["top", "right"]:
        ax1.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax1.spines[spine].set_color("black")
        ax1.spines[spine].set_linewidth(1.0)
    ax1.tick_params(axis="both", colors="black", labelsize=12)
    for label in ax1.get_xticklabels() + ax1.get_yticklabels():
        label.set_fontweight("bold")

    for bar, val in zip(bars, values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.15,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
            color="black",
            zorder=5,
        )

    # Panel 2: Win percentage with expected band
    ax2.axhspan(
        expected_low,
        expected_high,
        color=EXPECTED_SHADE,
        alpha=0.6,
        zorder=1,
    )
    ax2.axhline(expected_low, color=LEAGUE_GRAY, linestyle="--", linewidth=1, zorder=2)
    ax2.axhline(expected_high, color=LEAGUE_GRAY, linestyle="--", linewidth=1, zorder=2)

    bar2 = ax2.bar(
        [0],
        [harbaugh_win_pct],
        color=RAVENS_PURPLE,
        width=0.6,
        edgecolor="black",
        linewidth=1.5,
        zorder=3,
    )
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Win Percentage (%)")
    ax2.set_title(
        "Protecting Leads (Final 2 Min)",
        pad=5,
        fontsize=16,
        fontweight="bold",
        color="black",
        y=0.97,
    )

    ax2.set_axisbelow(True)
    ax2.set_yticks([0, 20, 40, 60, 80, 100])
    ax2.grid(axis="y", color=GRID_GRAY, linewidth=0.5, alpha=0.5, zorder=0)
    ax2.grid(axis="x", visible=False)
    ax2.set_xlim(-0.5, 0.5)
    ax2.set_xticks([0])
    ax2.set_xticklabels(["Harbaugh"])
    for spine in ["top", "right"]:
        ax2.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax2.spines[spine].set_color("black")
        ax2.spines[spine].set_linewidth(1.0)
    ax2.tick_params(axis="both", colors="black", labelsize=12)
    for label in ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontweight("bold")

    ax2.text(
        bar2[0].get_x() + bar2[0].get_width() / 2,
        harbaugh_win_pct + 2.0,
        f"{harbaugh_win_pct:.1f}%",
        ha="center",
        va="bottom",
        fontsize=16,
        fontweight="bold",
        color="black",
        zorder=5,
    )

    ax2.annotate(
        "",
        xy=(0.05, harbaugh_win_pct),
        xytext=(0.25, 77.5),
        arrowprops=dict(arrowstyle="->", color=GREEN, lw=2),
        zorder=5,
    )
    ax2.text(
        0.28,
        77.5,
        "Above Expected",
        ha="left",
        va="center",
        fontsize=13,
        fontweight="bold",
        color=GREEN,
        bbox=dict(facecolor=BACKGROUND_COLOR, edgecolor="none", pad=0.2, alpha=0.9),
        zorder=5,
    )

    # Legend removed to avoid the extra white box.

    fig.suptitle(
        "Harbaugh's Two-Minute Mastery",
        fontsize=34,
        fontweight="bold",
        color=TITLE_BLUE,
        y=0.98,
    )

    plt.tight_layout(pad=2.0)

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "harbaugh_two_minute_mastery.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

