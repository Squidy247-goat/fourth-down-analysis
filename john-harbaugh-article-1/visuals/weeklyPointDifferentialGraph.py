"""
line graph showing how much ravens win or lose by each game
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np

def get_game_point_differentials(year):
    """get scores for all games in one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"Reading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Get the final score for each game (last play of each game)
    games = df.groupby('game_id').last().reset_index()
    
    game_data = []
    
    for _, game in games.iterrows():
        home_team = game['home_team']
        away_team = game['away_team']
        home_score = game['home_score']
        away_score = game['away_score']
        week = game['week']
        game_date = game['game_date']
        
        # Determine if Ravens were home or away
        if home_team == 'BAL':
            ravens_score = home_score
            opponent_score = away_score
            opponent = away_team
            location = 'Home'
        elif away_team == 'BAL':
            ravens_score = away_score
            opponent_score = home_score
            opponent = home_team
            location = 'Away'
        else:
            continue
        
        point_diff = ravens_score - opponent_score
        
        game_data.append({
            'year': year,
            'week': week,
            'game_date': game_date,
            'ravens_score': ravens_score,
            'opponent_score': opponent_score,
            'point_diff': point_diff,
            'opponent': opponent,
            'location': location,
            'result': 'W' if point_diff > 0 else ('L' if point_diff < 0 else 'T')
        })
    
    return game_data


def create_point_differential_graph():
    """
    Create line graph of weekly point differential
    """
    
    print("="*80)
    print("CREATING POINT DIFFERENTIAL VISUALIZATION")
    print("="*80)
    
    # Collect data for all years (2008-2025)
    all_game_data = []
    
    for year in range(2008, 2026):
        game_data = get_game_point_differentials(year)
        all_game_data.extend(game_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_game_data)
    
    # Create a continuous game number for x-axis
    df = df.sort_values(['year', 'week']).reset_index(drop=True)
    df['game_number'] = range(1, len(df) + 1)
    
    # Create era labels
    df['era'] = df['year'].apply(lambda x: 'Lamar Era' if x >= 2018 else 'Flacco Era')
    
    # Create the figure with a larger size
    fig, ax = plt.subplots(figsize=(18, 10))
    
    # Split data by era
    flacco_era = df[df['era'] == 'Flacco Era']
    lamar_era = df[df['era'] == 'Lamar Era']
    
    # Plot Flacco Era
    ax.plot(flacco_era['game_number'], flacco_era['point_diff'], 
            linewidth=1.5, color='#241773', alpha=0.7, label='Flacco Era (2008-2017)', 
            marker='o', markersize=3, markerfacecolor='#241773', markeredgecolor='white', markeredgewidth=0.5)
    
    # Plot Lamar Era with thicker, more prominent styling
    ax.plot(lamar_era['game_number'], lamar_era['point_diff'], 
            linewidth=3, color='#9E7C0C', alpha=0.9, label='Lamar Era (2018-2025)', 
            marker='o', markersize=5, markerfacecolor='#FFB612', markeredgecolor='#241773', markeredgewidth=1)
    
    # Add horizontal line at 0
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Even')
    
    # Add vertical line for Lamar's first start (Week 11, 2018)
    lamar_first_start = df[(df['year'] == 2018) & (df['week'] == 11)]
    if not lamar_first_start.empty:
        game_num = lamar_first_start.iloc[0]['game_number']
        ax.axvline(x=game_num, color='gold', linestyle=':', linewidth=2, alpha=0.6)
        ax.text(game_num - 5, ax.get_ylim()[1] * 0.75, "Lamar's\nFirst Start", 
                ha='right', va='top', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='gold', alpha=0.7, edgecolor='darkgoldenrod'))
    
    # Add vertical line for 2019 MVP Season
    mvp_season_start = df[(df['year'] == 2019) & (df['week'] == 1)]
    if not mvp_season_start.empty:
        game_num = mvp_season_start.iloc[0]['game_number']
        ax.axvline(x=game_num, color='gold', linestyle=':', linewidth=2, alpha=0.6)
        ax.text(game_num + 5, ax.get_ylim()[1] * 0.55, "2019 MVP\nSeason", 
                ha='left', va='top', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='gold', alpha=0.7, edgecolor='darkgoldenrod'))
    
    # Highlight biggest win and loss
    max_win = df.loc[df['point_diff'].idxmax()]
    max_loss = df.loc[df['point_diff'].idxmin()]
    
    ax.scatter(max_win['game_number'], max_win['point_diff'], 
               color='green', s=200, zorder=5, edgecolors='darkgreen', linewidths=2, marker='*')
    ax.annotate(f"Biggest Win\n{int(max_win['point_diff'])}pts\nWeek {int(max_win['week'])}, {int(max_win['year'])}", 
                xy=(max_win['game_number'], max_win['point_diff']),
                xytext=(60, 15), textcoords='offset points',
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.85, edgecolor='darkgreen'),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', 
                               color='darkgreen', lw=2))
    
    ax.scatter(max_loss['game_number'], max_loss['point_diff'], 
               color='red', s=200, zorder=5, edgecolors='darkred', linewidths=2, marker='*')
    ax.annotate(f"Biggest Loss\n{int(max_loss['point_diff'])}pts\nWeek {int(max_loss['week'])}, {int(max_loss['year'])}", 
                xy=(max_loss['game_number'], max_loss['point_diff']),
                xytext=(60, 60), textcoords='offset points',
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcoral', alpha=0.85, edgecolor='darkred'),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', 
                               color='darkred', lw=2))
    
    # Add shading for positive and negative differentials
    ax.fill_between(df['game_number'], 0, df['point_diff'], 
                     where=(df['point_diff'] > 0), alpha=0.1, color='green', 
                     interpolate=True, label='_nolegend_')
    ax.fill_between(df['game_number'], 0, df['point_diff'], 
                     where=(df['point_diff'] < 0), alpha=0.1, color='red', 
                     interpolate=True, label='_nolegend_')
    
    # Styling
    ax.set_xlabel('Game Number (Chronological)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Point Differential', fontsize=14, fontweight='bold')
    ax.set_title('Baltimore Ravens: Weekly Point Differential\nJohn Harbaugh Era (2008-2025)', 
                 fontsize=18, fontweight='bold', color='#241773', pad=20)
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_facecolor('#F5F5F5')
    
    # Add legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='black')
    
    # Add tick marks for season boundaries
    season_boundaries = []
    for year in range(2008, 2026):
        year_games = df[df['year'] == year]
        if not year_games.empty:
            first_game = year_games.iloc[0]['game_number']
            season_boundaries.append((first_game, year))
    
    # Add minor ticks for every 16 games (approximate season)
    ax.set_xticks([b[0] for b in season_boundaries[::2]], minor=False)
    ax.set_xticklabels([str(b[1]) for b in season_boundaries[::2]], rotation=45, ha='right')
    
    plt.tight_layout()
    
    # save it
    output_dir = Path(__file__).parent.parent / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    png_path = output_dir / "weeklyPointDifferential.png"
    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nVisualization saved to: {png_path}")
    
    plt.close()
    
    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    flacco_stats = flacco_era['point_diff'].describe()
    lamar_stats = lamar_era['point_diff'].describe()
    
    print("\nFlacco Era (2008-2017):")
    print(f"  Average point differential: {flacco_stats['mean']:.2f}")
    print(f"  Median: {flacco_stats['50%']:.2f}")
    print(f"  Best: {flacco_stats['max']:.0f}")
    print(f"  Worst: {flacco_stats['min']:.0f}")
    print(f"  Standard deviation: {flacco_stats['std']:.2f}")
    print(f"  Games: {flacco_stats['count']:.0f}")
    
    print("\nLamar Era (2018-2025):")
    print(f"  Average point differential: {lamar_stats['mean']:.2f}")
    print(f"  Median: {lamar_stats['50%']:.2f}")
    print(f"  Best: {lamar_stats['max']:.0f}")
    print(f"  Worst: {lamar_stats['min']:.0f}")
    print(f"  Standard deviation: {lamar_stats['std']:.2f}")
    print(f"  Games: {lamar_stats['count']:.0f}")
    
    # Count blowout wins (15+ points)
    flacco_blowouts = len(flacco_era[flacco_era['point_diff'] >= 15])
    lamar_blowouts = len(lamar_era[lamar_era['point_diff'] >= 15])
    
    print(f"\nBlowout Wins (15+ points):")
    print(f"  Flacco Era: {flacco_blowouts} ({flacco_blowouts/len(flacco_era)*100:.1f}%)")
    print(f"  Lamar Era: {lamar_blowouts} ({lamar_blowouts/len(lamar_era)*100:.1f}%)")
    
    # Count blowout losses (15+ points)
    flacco_blowout_losses = len(flacco_era[flacco_era['point_diff'] <= -15])
    lamar_blowout_losses = len(lamar_era[lamar_era['point_diff'] <= -15])
    
    print(f"\nBlowout Losses (15+ points):")
    print(f"  Flacco Era: {flacco_blowout_losses} ({flacco_blowout_losses/len(flacco_era)*100:.1f}%)")
    print(f"  Lamar Era: {lamar_blowout_losses} ({lamar_blowout_losses/len(lamar_era)*100:.1f}%)")
    
    # Winning percentage
    flacco_wins = len(flacco_era[flacco_era['point_diff'] > 0])
    lamar_wins = len(lamar_era[lamar_era['point_diff'] > 0])
    
    print(f"\nWinning Percentage:")
    print(f"  Flacco Era: {flacco_wins/len(flacco_era)*100:.1f}%")
    print(f"  Lamar Era: {lamar_wins/len(lamar_era)*100:.1f}%")
    
    return df


if __name__ == "__main__":
    df = create_point_differential_graph()
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE!")
    print("="*80)
