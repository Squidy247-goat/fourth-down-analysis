from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".mpl-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns

BACKGROUND_COLOR = "#F7E6CE"
GIANTS_COLORS = ["#0B2265", "#1A3A7A", "#2A4F90", "#3E66A8", "#5B7DC1"]
RAVENS_COLOR = "#241773"
GRID_COLOR = "#D3D3D3"
TITLE_TEXT = "Coaching Stability: Giants Carousel vs Harbaugh Continuity"
SUMMARY_TEXT = "Giants: 5 coaches in 10 years | Ravens: 1 coach, 18 consecutive seasons"


def main():
    # Timeline range
    start_year = 2016
    end_year = 2025

    # Coaching tenures and records (regular season)
    giants_tenures = [
        ("Ben McAdoo", 2016, 2017, "13-15"),
        ("Pat Shurmur", 2018, 2019, "9-23"),
        ("Joe Judge", 2020, 2021, "10-23"),
        ("Brian Daboll", 2022, 2024, "20-40-1"),
        ("Mike Kafka", 2025, 2025, "2-5"),
    ]

    ravens_tenure = ("John Harbaugh", 2016, 2025, "103-62")

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.labelweight": "bold",
            "axes.titlesize": 34,
            "axes.titleweight": "bold",
            "axes.labelsize": 16,
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
        }
    )

    fig, ax = plt.subplots(figsize=(14, 6), dpi=300)
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)

    # Y positions for rows
    bar_height = 0.6
    spacing = 0.8
    ravens_y = 0.0
    giants_y = ravens_y + bar_height + spacing

    for year in range(start_year, end_year + 1):
        ax.axvline(year, linestyle="--", color=GRID_COLOR, alpha=0.5, zorder=0)

    # Giants segmented bars
    for (coach, start, end, record), color in zip(giants_tenures, GIANTS_COLORS):
        duration = end - start + 1
        ax.broken_barh(
            [(start, duration)],
            (giants_y, bar_height),
            facecolors=color,
            edgecolor="black",
            linewidth=1.5,
            zorder=2,
        )
        label = f"{coach}\n({record})"
        text = ax.text(
            start + duration / 2,
            giants_y + bar_height / 2,
            label,
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
            color="white",
            linespacing=1.1,
            multialignment="center",
            zorder=3,
        )
        text.set_path_effects(
            [path_effects.withStroke(linewidth=2, foreground="black")]
        )

    # Ravens continuous bar
    ravens_duration = ravens_tenure[2] - ravens_tenure[1] + 1
    ax.broken_barh(
        [(ravens_tenure[1], ravens_duration)],
        (ravens_y, bar_height),
        facecolors=RAVENS_COLOR,
        edgecolor="black",
        linewidth=1.5,
        zorder=2,
    )
    ravens_text = ax.text(
        ravens_tenure[1] + ravens_duration / 2,
        ravens_y + bar_height / 2,
        f"{ravens_tenure[0]}\n{ravens_tenure[3]}",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color="white",
        linespacing=1.1,
        multialignment="center",
        zorder=3,
    )
    ravens_text.set_path_effects(
        [path_effects.withStroke(linewidth=2, foreground="black")]
    )

    # Axis formatting
    ax.set_ylim(-0.2, giants_y + bar_height + 0.3)
    ax.set_xlim(start_year, end_year + 1)
    ax.set_yticks([giants_y + bar_height / 2, ravens_y + bar_height / 2])
    ax.set_yticklabels(
        ["New York Giants", "Baltimore Ravens"],
        fontweight="bold",
    )
    ax.set_xticks(list(range(start_year, end_year + 1)))
    ax.set_xticklabels(
        list(range(start_year, end_year + 1)),
        fontweight="bold",
    )
    ax.tick_params(axis="x", labelsize=11)
    ax.tick_params(axis="y", labelsize=11)
    ax.set_xlabel("Season", fontsize=22, fontweight="bold")
    ax.set_title(TITLE_TEXT, pad=16, fontweight="bold", color="#0033A0")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    plt.tight_layout(pad=2.0)

    for label in ax.get_xticklabels():
        label.set_fontweight("black")
    for label in ax.get_yticklabels():
        label.set_fontweight("black")

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "coaching_carousel_timeline.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
