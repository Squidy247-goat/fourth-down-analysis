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
GIANTS_BLUE = "#0B2265"
LEAGUE_GRAY = "#808080"
GRID_GRAY = "#D3D3D3"
GREEN = "#2D7A3E"
LIGHT_GREEN = "#90EE90"
RED = "#C41E3A"
LIGHT_BLUE = "#A7C7E7"
TITLE_BLUE = "#0033A0"


def main():
    # DATA
    years_hist = list(range(2016, 2026))
    # Based on Giants records shown (2016-2025): 11-5, 3-13, 5-11, 4-12, 6-10, 4-13, 9-7-1, 6-11, 3-14, 4-13
    wins_hist = [11, 3, 5, 4, 6, 4, 9, 6, 3, 4]

    years_proj = [2026, 2027, 2028]
    wins_proj = [8, 10, 11]
    ci_low = [6, 8, 9]
    ci_high = [10, 12, 13]

    historical_avg = sum(wins_hist) / len(wins_hist)

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            # More emotive font stack (falls back safely)
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.titlesize": 38,
            "axes.titleweight": "bold",
            "axes.labelsize": 16,
            "axes.labelweight": "bold",
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 12,
        }
    )

    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)

    # Confidence interval (2026-2028)
    ax.fill_between(
        years_proj,
        ci_low,
        ci_high,
        color=LIGHT_GREEN,
        alpha=0.3,
        label="Confidence Range",
        zorder=1,
    )

    # Reference lines
    ax.axhline(
        10,
        color=LEAGUE_GRAY,
        linestyle="--",
        linewidth=2,
        label="Playoff Threshold (~10 wins)",
        zorder=0,
    )
    ax.axhline(
        12,
        color=LIGHT_BLUE,
        linestyle="--",
        linewidth=2,
        label="Division Winner Target",
        zorder=0,
    )

    # Historical line
    ax.plot(
        years_hist,
        wins_hist,
        color=GIANTS_BLUE,
        linewidth=3,
        marker="o",
        markersize=9,
        markerfacecolor=GIANTS_BLUE,
        markeredgecolor="black",
        markeredgewidth=1,
        label="Actual Record",
        zorder=3,
    )

    # Connecting dotted line (2025 to 2026)
    ax.plot(
        [2025, 2026],
        [wins_hist[-1], wins_proj[0]],
        color=LEAGUE_GRAY,
        linestyle=":",
        linewidth=2,
        zorder=2,
    )

    # Projected line
    ax.plot(
        years_proj,
        wins_proj,
        color=GREEN,
        linewidth=3,
        linestyle=(0, (5, 3)),
        marker="s",
        markersize=9,
        markerfacecolor=GREEN,
        markeredgecolor="black",
        markeredgewidth=1,
        label="Harbaugh Projection",
        zorder=4,
    )

    # Separator: Harbaugh hired
    ax.axvline(2025.5, color=RED, linestyle="--", linewidth=2, zorder=2)
    ax.text(
        2025.5,
        14.8,
        "Harbaugh Hired ->",
        ha="center",
        va="top",
        fontsize=14,
        fontweight="bold",
        color=RED,
        bbox=dict(facecolor=BACKGROUND_COLOR, edgecolor="none", alpha=0.9, pad=0.2),
        zorder=5,
    )

    # Annotation arrow to 2026 projection
    ax.annotate(
        "Expected 4-5 win improvement",
        xy=(2026, wins_proj[0]),
        xytext=(2026.6, 12.3),
        ha="left",
        va="center",
        fontsize=13,
        fontweight="bold",
        color=GREEN,
        arrowprops=dict(arrowstyle="->", color=GREEN, lw=2.5),
        zorder=6,
    )

    # 2028 endpoint callout
    ax.text(
        2028.15,
        wins_proj[-1],
        "Division Contender\nif QB develops",
        ha="left",
        va="center",
        fontsize=11,
        fontstyle="italic",
        color=GREEN,
        zorder=6,
    )

    # Axes formatting
    all_years = list(range(2016, 2029))
    ax.set_xlim(2016, 2028)
    ax.set_xticks(all_years)
    ax.set_ylim(0, 15)
    ax.set_yticks(list(range(0, 16, 3)))
    ax.set_xlabel("Season")
    ax.set_ylabel("Regular Season Wins")

    ax.set_title("Giants Win Trajectory: The Harbaugh Effect", pad=28, color=TITLE_BLUE, fontweight="bold")

    # Force tick label bold + slightly larger for readability
    ax.tick_params(axis="both", labelsize=13, colors="#000000")
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")

    # Grid (both axes)
    ax.set_axisbelow(True)
    ax.grid(True, axis="y", color=GRID_GRAY, alpha=0.3, linewidth=1.0)
    ax.grid(True, axis="x", color=GRID_GRAY, alpha=0.3, linewidth=1.0)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Legend
    leg = ax.legend(loc="upper left", frameon=True, fontsize=10)
    leg.get_frame().set_edgecolor("#D3D3D3")
    leg.get_frame().set_linewidth(1.0)
    leg.get_frame().set_alpha(1.0)
    leg.get_frame().set_facecolor("#FFFFFF")
    for t in leg.get_texts():
        t.set_fontweight("bold")
        t.set_color("#000000")

    plt.tight_layout(pad=2.0)

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "giants_projected_win_trajectory.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

