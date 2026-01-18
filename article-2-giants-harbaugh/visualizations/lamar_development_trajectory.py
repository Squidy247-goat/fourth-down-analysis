from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mpl-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns


BACKGROUND_COLOR = "#F7E6CE"
GIANTS_BLUE = "#0B2265"
RAVENS_PURPLE = "#241773"
LEAGUE_GRAY = "#808080"

GREEN = "#2D7A3E"
RED = "#C41E3A"
GOLD = "#D4AF37"
GRID_COLOR = "#D3D3D3"


def main():
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    completion_pct = [58.2, 66.1, 64.4, 64.4, 62.3, 67.2, 66.8]
    ypa = [7.0, 7.8, 7.3, 7.4, 7.0, 8.0, 8.1]
    passing_epa = [0.05, 0.25, 0.15, 0.10, 0.06, 0.22, 0.23]

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.titlesize": 26,
            "axes.titleweight": "bold",
            "axes.labelsize": 16,
            "axes.labelweight": "bold",
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 13,
        }
    )

    fig, ax_comp = plt.subplots(figsize=(13, 7), dpi=300)
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax_comp.set_facecolor(BACKGROUND_COLOR)

    # Extra left axis for YPA (keeps "dual y-axis" feel with EPA on the right)
    ax_epa = ax_comp.twinx()
    ax_ypa = ax_comp.twinx()
    ax_ypa.spines["left"].set_position(("outward", 55))
    ax_ypa.spines["left"].set_visible(True)
    ax_ypa.spines["right"].set_visible(False)
    ax_ypa.yaxis.set_label_position("left")
    ax_ypa.yaxis.set_ticks_position("left")

    # Shaded coordinator eras
    ax_comp.axvspan(2019, 2022.5, color=RED, alpha=0.1, zorder=0)
    ax_comp.axvspan(2022.5, 2024.5, color=GREEN, alpha=0.1, zorder=0)

    # Coordinator change marker
    ax_comp.axvline(2022.5, color=RED, linestyle="--", linewidth=2, alpha=0.7, zorder=1)

    # Lines
    common_kwargs = dict(linewidth=2.5, markersize=8, markeredgecolor="black", markeredgewidth=1, zorder=3)
    line_comp, = ax_comp.plot(
        years,
        completion_pct,
        color=GIANTS_BLUE,
        marker="o",
        linestyle="-",
        label="Completion %",
        **common_kwargs,
    )
    line_ypa, = ax_ypa.plot(
        years,
        ypa,
        color=GREEN,
        marker="s",
        linestyle="-",
        label="Yards/Attempt",
        **common_kwargs,
    )
    line_epa, = ax_epa.plot(
        years,
        passing_epa,
        color=RAVENS_PURPLE,
        marker="D",
        linestyle="-",
        label="Passing EPA",
        **common_kwargs,
    )

    # Axes ranges and labels
    ax_comp.set_xlim(2018, 2024)
    ax_comp.set_xticks(years)
    ax_comp.set_xlabel("Season")

    ax_comp.set_ylim(55, 70)
    ax_comp.set_ylabel("Completion % / Yards per Attempt")

    ax_ypa.set_ylim(6.5, 8.5)
    ax_epa.set_ylim(0.0, 0.30)
    ax_epa.set_ylabel("Passing EPA")

    # Grid behind lines
    ax_comp.set_axisbelow(True)
    ax_comp.grid(True, axis="both", color=GRID_COLOR, alpha=0.3, linewidth=0.8, zorder=0)

    # Title
    ax_comp.set_title(
        "Lamar Jackson's Development: The Coordinator Effect",
        pad=22,
        fontweight="bold",
        color="#0033A0",
    )

    # Monken annotation at top of line (rotated)
    ax_comp.text(
        2022.62,
        ax_comp.get_ylim()[1],
        "Monken Hired ->",
        rotation=90,
        color=RED,
        fontsize=13,
        fontweight="bold",
        ha="center",
        va="top",
        bbox=dict(facecolor=BACKGROUND_COLOR, edgecolor="none", alpha=0.85, pad=0.2),
        clip_on=False,
        zorder=4,
    )

    # MVP callouts (2019 and 2023)
    # Place the labels away from the lines with a stronger background to avoid interference.
    mvp_years = [2019, 2023]
    for y in mvp_years:
        idx = years.index(y)

        if y == 2019:
            # Put below the green (YPA) marker in 2019.
            target_ax = ax_ypa
            target_xy = (years[idx], ypa[idx])
            offset = (12, -28)
            va = "top"
        else:
            # Put above the completion marker in 2023.
            target_ax = ax_comp
            target_xy = (years[idx], completion_pct[idx])
            offset = (12, 20)
            va = "bottom"

        target_ax.annotate(
            "MVP *",
            xy=target_xy,
            xytext=offset,
            textcoords="offset points",
            ha="left",
            va=va,
            fontsize=12,
            fontweight="bold",
            color=GOLD,
            bbox=dict(facecolor=BACKGROUND_COLOR, edgecolor="none", alpha=0.95, pad=0.2),
            clip_on=False,
            zorder=6,
        )

    # Legend (combine handles from all axes)
    era_handles = [
        Patch(facecolor=RED, alpha=0.1, edgecolor="none", label="Greg Roman Era"),
        Patch(facecolor=GREEN, alpha=0.1, edgecolor="none", label="Todd Monken Era"),
    ]
    handles = [line_comp, line_ypa, line_epa, *era_handles]
    labels = [h.get_label() for h in handles]
    leg = ax_comp.legend(handles, labels, loc="lower right", frameon=True)
    leg.get_frame().set_edgecolor("#D3D3D3")
    leg.get_frame().set_linewidth(1.0)
    leg.get_frame().set_alpha(1.0)
    for t in leg.get_texts():
        t.set_fontweight("bold")
        t.set_color("#000000")

    # Force tick label bold on all axes (including twins)
    for _ax in (ax_comp, ax_epa, ax_ypa):
        for tick in _ax.get_xticklabels() + _ax.get_yticklabels():
            tick.set_fontweight("bold")

    # Clean spines (keep left/bottom + right EPA + left YPA)
    ax_comp.spines["top"].set_visible(False)
    ax_epa.spines["top"].set_visible(False)
    ax_ypa.spines["top"].set_visible(False)

    plt.tight_layout(pad=2.0)

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "lamar_development_trajectory.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

