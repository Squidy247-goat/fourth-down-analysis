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
GRID_GRAY = "#D3D3D3"

# Brand / palette
GIANTS_BLUE = "#0B2265"
LEAGUE_GRAY = "#808080"

# Coordinator impact colors
GOOD_BLUE = GIANTS_BLUE
ELITE_GREEN = "#2D7A3E"
AVG_ORANGE = "#F28C28"
POOR_RED = "#C41E3A"
ELITE_DARK_GREEN = "#145A32"


def add_value_label(ax, x, y, text, direction="right"):
    """Place a bold value label at the bar end."""
    pad = 0.004
    if direction == "right":
        t = ax.text(
            x + pad,
            y,
            text,
            ha="left",
            va="center",
            fontsize=14,
            fontweight="bold",
            color="#000000",
            bbox=dict(facecolor=BACKGROUND_COLOR, edgecolor="none", alpha=0.9, pad=0.15),
            zorder=5,
        )
    else:
        t = ax.text(
            x - pad,
            y,
            text,
            ha="right",
            va="center",
            fontsize=14,
            fontweight="bold",
            color="#000000",
            bbox=dict(facecolor=BACKGROUND_COLOR, edgecolor="none", alpha=0.9, pad=0.15),
            zorder=5,
        )
    t.set_fontweight("bold")
    return t


def main():
    # Data
    offense_labels = ["Greg Roman\n(2019-2022)", "Todd Monken\n(2023-2025)"]
    offense_values = [0.083, 0.107]

    defense_labels = ["Pre-Macdonald", "Macdonald Era", "Post-Macdonald"]
    defense_values = [-0.038, -0.082, -0.014]

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            # More expressive font stack (falls back safely)
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.titlecolor": "#000000",
            "axes.titlesize": 18,
            "axes.titleweight": "bold",
            "axes.labelsize": 15,
            "axes.labelweight": "bold",
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 10,
        }
    )

    fig, (ax_off, ax_def) = plt.subplots(
        2,
        1,
        figsize=(12, 8),
        dpi=300,
        gridspec_kw={"height_ratios": [1, 1]},
    )
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax_off.set_facecolor(BACKGROUND_COLOR)
    ax_def.set_facecolor(BACKGROUND_COLOR)
    # Extra separation between panels + push content upward (no main title)
    fig.subplots_adjust(hspace=1.35, top=0.96)

    # -------------------------
    # OFFENSE PANEL
    # -------------------------
    y_off = np.array([1, 0])
    ax_off.barh(
        y_off,
        offense_values,
        height=0.5,
        color=[GOOD_BLUE, ELITE_GREEN],
        edgecolor="#000000",
        linewidth=1.4,
        zorder=3,
    )
    ax_off.set_yticks(y_off)
    ax_off.set_yticklabels(offense_labels, fontweight="bold")

    ax_off.set_xlim(0, 0.12)
    ax_off.set_xticks(np.arange(0, 0.121, 0.02))
    ax_off.set_xlabel("Offensive EPA per Play (Higher = Better)", labelpad=4)
    ax_off.set_title("OFFENSIVE COORDINATOR IMPACT", pad=12)
    ax_off.tick_params(axis="both", labelsize=10)
    for t in ax_off.get_xticklabels() + ax_off.get_yticklabels():
        t.set_fontweight("bold")
        t.set_fontsize(13)

    ax_off.set_axisbelow(True)
    ax_off.grid(axis="x", color=GRID_GRAY, linewidth=1.0, alpha=0.65, zorder=0)
    ax_off.grid(axis="y", visible=False)

    for spine in ["top", "right"]:
        ax_off.spines[spine].set_visible(False)
    ax_off.spines["left"].set_linewidth(1.0)
    ax_off.spines["bottom"].set_linewidth(1.0)

    add_value_label(ax_off, offense_values[0], y_off[0], f"{offense_values[0]:.3f}", direction="right")
    add_value_label(ax_off, offense_values[1], y_off[1], f"{offense_values[1]:.3f}", direction="right")

    # Improvement arrow (+29%)
    ax_off.annotate(
        "",
        xy=(offense_values[1], 0.5),
        xytext=(offense_values[0], 0.5),
        arrowprops=dict(arrowstyle="->", color=ELITE_GREEN, lw=3),
        zorder=4,
    )
    ax_off.text(
        (offense_values[0] + offense_values[1]) / 2,
        0.62,
        "+29%",
        ha="center",
        va="bottom",
        fontsize=14,
        fontweight="bold",
        color=ELITE_GREEN,
        zorder=5,
    )

    # -------------------------
    # DEFENSE PANEL (more negative = better)
    # -------------------------
    y_def = np.array([2, 1, 0])
    ax_def.barh(
        y_def,
        defense_values,
        height=0.5,
        color=[AVG_ORANGE, ELITE_DARK_GREEN, POOR_RED],
        edgecolor="#000000",
        linewidth=1.4,
        zorder=3,
    )
    ax_def.set_yticks(y_def)
    ax_def.set_yticklabels(defense_labels, fontweight="bold")

    ax_def.set_xlim(0, -0.10)
    ax_def.set_xticks(np.arange(0, -0.101, -0.02))
    ax_def.set_xlabel("Defensive EPA per Play (More Negative = Better)", labelpad=4)
    ax_def.set_title("DEFENSIVE COORDINATOR IMPACT", pad=12)
    ax_def.tick_params(axis="both", labelsize=10)
    for t in ax_def.get_xticklabels() + ax_def.get_yticklabels():
        t.set_fontweight("bold")
        t.set_fontsize(13)

    ax_def.set_axisbelow(True)
    ax_def.grid(axis="x", color=GRID_GRAY, linewidth=1.0, alpha=0.65, zorder=0)
    ax_def.grid(axis="y", visible=False)

    for spine in ["top", "right"]:
        ax_def.spines[spine].set_visible(False)
    ax_def.spines["left"].set_linewidth(1.0)
    ax_def.spines["bottom"].set_linewidth(1.0)

    add_value_label(ax_def, defense_values[0], y_def[0], f"{defense_values[0]:.3f}", direction="left")
    add_value_label(ax_def, defense_values[1], y_def[1], f"{defense_values[1]:.3f}", direction="left")
    add_value_label(ax_def, defense_values[2], y_def[2], f"{defense_values[2]:.3f}", direction="left")

    # No main title; keep panels tight and higher on canvas.
    plt.tight_layout(pad=2.0)

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "coordinator_impact_comparison.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

