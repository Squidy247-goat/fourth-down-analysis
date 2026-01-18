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
LEAGUE_GRAY = "#5F5F5F"
GRID_GRAY = "#C6C6C6"
LABEL_BOX = "#FFF7E8"
GOLD = "#D4AF37"


def main():
    categories = [
        "QB Potential (Jaxson Dart)",
        "WR Production (Malik Nabers)",
        "RB Explosiveness (Cam Skattebo)",
        "OL Anchor (Andrew Thomas)",
        "DL Dominance (Lawrence/Burns/Carter)",
        "Secondary Coverage",
    ]

    giants = [82, 88, 75, 90, 85, 65]
    contender = [85, 80, 75, 82, 80, 78]

    overall_giants = round(sum(giants) / len(giants), 1)  # 80.8
    overall_contender = round(sum(contender) / len(contender), 1)  # 80.0

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": ["Avenir Next", "Avenir", "Helvetica Neue", "DejaVu Sans"],
            "font.weight": "bold",
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        }
    )

    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    giants_values = giants + giants[:1]
    contender_values = contender + contender[:1]

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)

    # Start at top, go clockwise
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Category labels
    ax.set_thetagrids(
        np.degrees(angles[:-1]),
        categories,
        fontsize=12,
        fontweight="bold",
        color="#000000",
    )
    ax.tick_params(axis="x", pad=18)
    for label in ax.get_xticklabels():
        label.set_fontweight("bold")
        # Prevent grid/circle lines from cutting through text
        label.set_bbox(dict(facecolor=LABEL_BOX, edgecolor="none", alpha=0.98, pad=0.25))

    # Radial scale and gridlines
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=10, color=LEAGUE_GRAY, fontweight="bold")
    ax.set_rlabel_position(90)
    # Thicker, clearer rings + spokes
    ax.yaxis.grid(True, color=GRID_GRAY, linewidth=1.2, alpha=0.9)
    ax.xaxis.grid(True, color=GRID_GRAY, linewidth=1.2, alpha=0.9)
    ax.spines["polar"].set_color(GRID_GRAY)
    ax.spines["polar"].set_linewidth(1.6)

    # Series
    ax.plot(
        angles,
        giants_values,
        color=GIANTS_BLUE,
        linewidth=3.0,
        label="Giants Young Core",
        zorder=3,
    )
    ax.fill(angles, giants_values, color=GIANTS_BLUE, alpha=0.33, zorder=2)

    ax.plot(
        angles,
        contender_values,
        color=LEAGUE_GRAY,
        linewidth=2.5,
        linestyle="--",
        label="Playoff Contender Avg",
        zorder=3,
    )

    # Value labels at each point
    for ang, v_g, v_c in zip(angles[:-1], giants, contender):
        ax.text(
            ang,
            v_g + 3,
            f"{v_g}",
            color=GIANTS_BLUE,
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(facecolor=LABEL_BOX, edgecolor="none", alpha=0.95, pad=0.12),
            zorder=5,
        )
        ax.text(
            ang,
            v_c - 6,
            f"{v_c}",
            color=LEAGUE_GRAY,
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(facecolor=LABEL_BOX, edgecolor="none", alpha=0.95, pad=0.12),
            zorder=5,
        )

    # Center annotations
    ax.text(
        0.5,
        0.52,
        f"Overall: {overall_giants}",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=GIANTS_BLUE,
    )
    ax.text(
        0.5,
        0.46,
        f"Playoff Avg: {overall_contender}",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=12,
        color=LEAGUE_GRAY,
        fontweight="bold",
    )

    # Title
    fig.suptitle(
        "Giants' Young Core: Talent in Place",
        fontsize=40,
        fontweight="bold",
        color="#0033A0",
        y=0.91,
    )

    # Legend upper-right outside plot
    leg = ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.22, 1.02),
        frameon=True,
        fontsize=10,
    )
    leg.get_frame().set_edgecolor("#D3D3D3")
    leg.get_frame().set_linewidth(1.0)
    leg.get_frame().set_alpha(1.0)
    leg.get_frame().set_facecolor("#FFFFFF")
    for t in leg.get_texts():
        t.set_fontweight("bold")

    plt.tight_layout(pad=2.0, rect=(0, 0, 1, 0.98))

    output_dir = BASE_DIR / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "giants_young_core_radar.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
