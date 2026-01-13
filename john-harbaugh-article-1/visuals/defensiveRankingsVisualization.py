"""
makes line graphs showing ravens defense compared to league average
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def get_defensive_data():
    """gets defense numbers and league averages"""
    
    # defense stats by year
    defensive_data = {
        'years': [2008, 2009, 2010, 2011],
        'ravens_yards_per_game': [261.1, 300.5, 318.9, 288.9],
        'ravens_yards_rank': [2, 3, 10, 3],
        'ravens_points_per_game': [15.3, 16.3, 16.9, 16.6],
        'ravens_points_rank': [3, 3, 3, 3],
        # League averages (estimated from NFL historical data)
        # 2008-2011 league averages were approximately 330-340 yards and 22-23 points
        'league_avg_yards': [331.0, 333.5, 340.2, 337.8],
        'league_avg_points': [22.0, 21.8, 22.3, 22.6]
    }
    
    return defensive_data


def create_defensive_line_graph():
    """
    Create a dual-axis line graph showing Ravens defense vs league average.
    """
    data = get_defensive_data()
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Define Ravens colors
    ravens_purple = '#241773'
    ravens_gold = '#9E7C0C'
    league_gray = '#666666'
    
    # ========== YARDS ALLOWED PLOT ==========
    ax1.plot(data['years'], data['ravens_yards_per_game'], 
             marker='o', markersize=10, linewidth=3, 
             color=ravens_purple, label='Ravens Yards Allowed')
    
    ax1.plot(data['years'], data['league_avg_yards'], 
             marker='s', markersize=8, linewidth=2, 
             linestyle='--', color=league_gray, alpha=0.7,
             label='League Average')
    
    # Fill the area between Ravens and league average
    ax1.fill_between(data['years'], 
                     data['ravens_yards_per_game'], 
                     data['league_avg_yards'],
                     alpha=0.2, color='green')
    
    # Customize yards plot
    ax1.set_ylabel('Yards Per Game', fontsize=13, fontweight='bold')
    ax1.set_title('Ravens Defense: Yards Allowed vs League Average (2008-2011)\nRegular Season Only', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.legend(loc='upper right', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(data['years'])
    
    # Add rank annotations
    for i, (year, yards, rank) in enumerate(zip(data['years'], 
                                                  data['ravens_yards_per_game'], 
                                                  data['ravens_yards_rank'])):
        ax1.annotate(f'#{rank}', 
                    xy=(year, yards), 
                    xytext=(0, -15),
                    textcoords='offset points',
                    ha='center',
                    fontsize=10,
                    fontweight='bold',
                    color=ravens_purple)
    
    # Add difference annotations
    for i, year in enumerate(data['years']):
        diff = data['league_avg_yards'][i] - data['ravens_yards_per_game'][i]
        mid_y = (data['ravens_yards_per_game'][i] + data['league_avg_yards'][i]) / 2
        ax1.annotate(f'-{diff:.1f}', 
                    xy=(year, mid_y), 
                    ha='center',
                    fontsize=9,
                    style='italic',
                    color='darkgreen')
    
    # ========== POINTS ALLOWED PLOT ==========
    ax2.plot(data['years'], data['ravens_points_per_game'], 
             marker='o', markersize=10, linewidth=3, 
             color=ravens_gold, label='Ravens Points Allowed')
    
    ax2.plot(data['years'], data['league_avg_points'], 
             marker='s', markersize=8, linewidth=2, 
             linestyle='--', color=league_gray, alpha=0.7,
             label='League Average')
    
    # Fill the area between Ravens and league average
    ax2.fill_between(data['years'], 
                     data['ravens_points_per_game'], 
                     data['league_avg_points'],
                     alpha=0.2, color='green')
    
    # Customize points plot
    ax2.set_xlabel('Season', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Points Per Game', fontsize=13, fontweight='bold')
    ax2.set_title('Ravens Defense: Points Allowed vs League Average (2008-2011)\nRegular Season Only', 
                  fontsize=16, fontweight='bold', pad=20)
    ax2.legend(loc='upper right', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xticks(data['years'])
    
    # Add rank annotations
    for i, (year, points, rank) in enumerate(zip(data['years'], 
                                                   data['ravens_points_per_game'], 
                                                   data['ravens_points_rank'])):
        ax2.annotate(f'#{rank}', 
                    xy=(year, points), 
                    xytext=(0, -12),
                    textcoords='offset points',
                    ha='center',
                    fontsize=10,
                    fontweight='bold',
                    color=ravens_gold)
    
    # Add difference annotations
    for i, year in enumerate(data['years']):
        diff = data['league_avg_points'][i] - data['ravens_points_per_game'][i]
        mid_y = (data['ravens_points_per_game'][i] + data['league_avg_points'][i]) / 2
        ax2.annotate(f'-{diff:.1f}', 
                    xy=(year, mid_y), 
                    ha='center',
                    fontsize=9,
                    style='italic',
                    color='darkgreen')
    
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / 'output' / 'visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the figure
    output_path = output_dir / 'defensiveRankingsLineGraph.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Defensive Rankings Line Graph saved to: {output_path}")
    
    return data


def print_defensive_summary(data):
    """Print summary statistics for defensive performance."""
    
    print(f"\n{'='*70}")
    print("RAVENS DEFENSIVE RANKINGS SUMMARY (2008-2011)")
    print(f"{'='*70}\n")
    
    # Yards allowed summary
    avg_ravens_yards = np.mean(data['ravens_yards_per_game'])
    avg_league_yards = np.mean(data['league_avg_yards'])
    avg_yards_diff = avg_league_yards - avg_ravens_yards
    
    print("YARDS ALLOWED:")
    for i, year in enumerate(data['years']):
        print(f"  {year}: {data['ravens_yards_per_game'][i]:.1f} yards/game "
              f"(Rank #{data['ravens_yards_rank'][i]}) - "
              f"{data['league_avg_yards'][i] - data['ravens_yards_per_game'][i]:.1f} "
              f"yards better than league avg")
    
    print(f"\n  4-Year Average:")
    print(f"    Ravens: {avg_ravens_yards:.1f} yards/game")
    print(f"    League: {avg_league_yards:.1f} yards/game")
    print(f"    Difference: {avg_yards_diff:.1f} yards better than average")
    
    # Points allowed summary
    avg_ravens_points = np.mean(data['ravens_points_per_game'])
    avg_league_points = np.mean(data['league_avg_points'])
    avg_points_diff = avg_league_points - avg_ravens_points
    
    print("\n" + "="*70)
    print("POINTS ALLOWED:")
    for i, year in enumerate(data['years']):
        print(f"  {year}: {data['ravens_points_per_game'][i]:.1f} points/game "
              f"(Rank #{data['ravens_points_rank'][i]}) - "
              f"{data['league_avg_points'][i] - data['ravens_points_per_game'][i]:.1f} "
              f"points better than league avg")
    
    print(f"\n  4-Year Average:")
    print(f"    Ravens: {avg_ravens_points:.1f} points/game")
    print(f"    League: {avg_league_points:.1f} points/game")
    print(f"    Difference: {avg_points_diff:.1f} points better than average")
    
    # Ranking consistency
    print("\n" + "="*70)
    print("RANKING CONSISTENCY:")
    print(f"  Yards Allowed Rankings: {data['ravens_yards_rank']}")
    print(f"    - Average Rank: {np.mean(data['ravens_yards_rank']):.1f}")
    print(f"    - Top 3 finishes: {sum(1 for r in data['ravens_yards_rank'] if r <= 3)}/4 seasons")
    
    print(f"\n  Points Allowed Rankings: {data['ravens_points_rank']}")
    print(f"    - Average Rank: {np.mean(data['ravens_points_rank']):.1f}")
    print(f"    - Top 3 finishes: {sum(1 for r in data['ravens_points_rank'] if r <= 3)}/4 seasons")


def main():
    """Generate defensive rankings visualization."""
    
    print(f"\n{'='*70}")
    print("GENERATING DEFENSIVE RANKINGS VISUALIZATION")
    print(f"{'='*70}\n")
    
    data = create_defensive_line_graph()
    print_defensive_summary(data)
    
    print(f"\n{'='*70}")
    print("KEY INSIGHTS:")
    print(f"{'='*70}\n")
    
    print("1. Elite Points Defense:")
    print("   - Ranked 3rd in points allowed in ALL 4 seasons (2008-2011)")
    print("   - Averaged 16.3 points allowed per game vs 22.2 league average")
    print("   - Prevented ~6 points per game more than average")
    
    print("\n2. Yards Allowed More Variable:")
    print("   - Rankings: 2nd, 3rd, 10th, 3rd")
    print("   - 2010 was the outlier (10th), but still elite in points (3rd)")
    print("   - Bend-but-don't-break philosophy in 2010")
    
    print("\n3. Consistently Elite:")
    print("   - Top 3 in points allowed: 4/4 seasons (100%)")
    print("   - Top 3 in yards allowed: 3/4 seasons (75%)")
    print("   - Always significantly better than league average")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
