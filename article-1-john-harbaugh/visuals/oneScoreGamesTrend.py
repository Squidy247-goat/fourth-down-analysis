"""
chart showing win rate in close games over the years
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def analyze_one_score_games_year(year):
    """get close game stats for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
        df_reg = df[df['season_type'] == 'REG'].copy()
        
        # Get unique games and their results
        games = df_reg.groupby('game_id').agg({
            'away_team': 'first',
            'home_team': 'first',
            'away_score': 'last',
            'home_score': 'last',
        }).reset_index()
        
        # Determine Ravens score and opponent score
        games['ravens_home'] = games['home_team'] == 'BAL'
        games['ravens_score'] = games.apply(
            lambda x: x['home_score'] if x['ravens_home'] else x['away_score'], axis=1
        )
        games['opponent_score'] = games.apply(
            lambda x: x['away_score'] if x['ravens_home'] else x['home_score'], axis=1
        )
        
        # Calculate margin and outcome
        games['margin'] = games['ravens_score'] - games['opponent_score']
        games['ravens_win'] = games['margin'] > 0
        games['one_score_game'] = games['margin'].abs() <= 8
        
        # Calculate statistics
        one_score_games = games[games['one_score_game']]
        num_one_score = len(one_score_games)
        
        if num_one_score > 0:
            one_score_wins = len(one_score_games[one_score_games['ravens_win']])
            one_score_win_pct = (one_score_wins / num_one_score) * 100
        else:
            one_score_wins = 0
            one_score_win_pct = None
        
        total_wins = len(games[games['ravens_win']])
        total_games = len(games)
        
        return {
            'year': year,
            'one_score_games': num_one_score,
            'one_score_wins': one_score_wins,
            'one_score_win_pct': one_score_win_pct,
            'total_wins': total_wins,
            'total_games': total_games
        }
        
    except FileNotFoundError:
        return None


def create_one_score_trend_visualization():
    """Create trend line visualization for one-score game win percentage."""
    
    # Harbaugh's tenure: 2008-2024
    years = list(range(2008, 2025))
    
    data = []
    for year in years:
        result = analyze_one_score_games_year(year)
        if result and result['one_score_win_pct'] is not None:
            data.append(result)
    
    if not data:
        print("No data available for visualization")
        return
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    print("\nData collected:")
    print(df[['year', 'one_score_wins', 'one_score_games', 'one_score_win_pct']])
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set style
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # Plot the actual data points
    ax.scatter(df['year'], df['one_score_win_pct'], 
               s=150, color='#241773', alpha=0.6, zorder=3, 
               edgecolors='black', linewidth=1.5, label='Actual win %')
    
    # Add connecting line
    ax.plot(df['year'], df['one_score_win_pct'], 
            color='#241773', alpha=0.3, linewidth=2, linestyle='-', zorder=2)
    
    # Add smoothed trend line
    if len(df) > 3:
        # Use polynomial fit for trend
        z = np.polyfit(df['year'], df['one_score_win_pct'], 3)
        p = np.poly1d(z)
        years_smooth = np.linspace(df['year'].min(), df['year'].max(), 100)
        ax.plot(years_smooth, p(years_smooth), 
                color='#D4AF37', linewidth=3, linestyle='--', 
                label='Trend line', zorder=4, alpha=0.8)
    
    # Add 50% reference line (coin flip expectation)
    ax.axhline(y=50, color='red', linestyle='--', linewidth=2, 
               alpha=0.5, label='50% (coin flip)', zorder=1)
    
    # Shade regions
    ax.fill_between(df['year'], 50, 100, alpha=0.05, color='green')
    ax.fill_between(df['year'], 0, 50, alpha=0.05, color='red')
    
    # Highlight specific eras
    # Peak years (2010-2012)
    ax.axvspan(2010, 2012, alpha=0.1, color='gold', label='Peak era (2010-12)')
    
    # Rebuild years (2015-2017)
    ax.axvspan(2015, 2017, alpha=0.1, color='gray', label='Rebuild era (2015-17)')
    
    # Lamar era (2019+)
    ax.axvspan(2019, df['year'].max(), alpha=0.05, color='purple', label='Lamar era (2019+)')
    
    # Annotate notable seasons
    notable_seasons = {
        2010: (66.7, 'Peak: 66.7%\n(8-4)'),
        2011: (71.4, 'Best: 71.4%\n(5-2)'),
        2017: (28.6, 'Worst: 28.6%\n(2-5)'),
        2023: (df[df['year'] == 2023]['one_score_win_pct'].values[0] if 2023 in df['year'].values else None, 
               f"{df[df['year'] == 2023]['one_score_win_pct'].values[0]:.1f}%" if 2023 in df['year'].values else None)
    }
    
    for year, (pct, label) in notable_seasons.items():
        if pct is not None and year in df['year'].values:
            ax.annotate(label, 
                       xy=(year, pct), 
                       xytext=(10, 10) if pct > 50 else (10, -30),
                       textcoords='offset points',
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                               edgecolor='black', alpha=0.8, linewidth=1.5),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                                     color='black', linewidth=1.5))
    
    # Add record labels to each point
    for _, row in df.iterrows():
        record_label = f"{int(row['one_score_wins'])}-{int(row['one_score_games'] - row['one_score_wins'])}"
        ax.annotate(record_label, 
                   (row['year'], row['one_score_win_pct']),
                   xytext=(0, -18), textcoords='offset points',
                   fontsize=7, ha='center', alpha=0.7)
    
    # Labels and title
    ax.set_xlabel('Season', fontsize=14, fontweight='bold')
    ax.set_ylabel('Win Percentage in One-Score Games', fontsize=14, fontweight='bold')
    ax.set_title("John Harbaugh Era: Success in Close Games\n" + 
                 "Win % in Games Decided by 8 Points or Less", 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Set y-axis limits and format
    ax.set_ylim(0, 100)
    ax.set_ylabel('Win Percentage (%)', fontsize=14, fontweight='bold')
    
    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{int(y)}%'))
    
    # X-axis: show every year
    ax.set_xticks(df['year'])
    ax.set_xticklabels(df['year'], rotation=45, ha='right')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Legend
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=9)
    
    # Add context text
    overall_record = f"{df['one_score_wins'].sum()}-{(df['one_score_games'].sum() - df['one_score_wins'].sum())}"
    overall_win_pct = (df['one_score_wins'].sum() / df['one_score_games'].sum() * 100)
    
    context_text = (f"Career one-score record: {overall_record}\n"
                   f"Career win %: {overall_win_pct:.1f}%\n"
                   f"Total one-score games: {int(df['one_score_games'].sum())}")
    
    ax.text(0.02, 0.98, context_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                    edgecolor='#241773', linewidth=2))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    output_dir = Path(__file__).parent.parent / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "oneScoreGamesTrend.png"
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nVisualization saved to: {output_path}")
    plt.close()
    
    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\nOverall (2008-{df['year'].max()}):")
    print(f"  Record: {overall_record}")
    print(f"  Win percentage: {overall_win_pct:.1f}%")
    
    # Era breakdowns
    peak_era = df[(df['year'] >= 2010) & (df['year'] <= 2012)]
    if len(peak_era) > 0:
        peak_record = f"{peak_era['one_score_wins'].sum()}-{int(peak_era['one_score_games'].sum() - peak_era['one_score_wins'].sum())}"
        peak_pct = peak_era['one_score_wins'].sum() / peak_era['one_score_games'].sum() * 100
        print(f"\nPeak Era (2010-2012): {peak_record} ({peak_pct:.1f}%)")
    
    rebuild_era = df[(df['year'] >= 2015) & (df['year'] <= 2017)]
    if len(rebuild_era) > 0:
        rebuild_record = f"{rebuild_era['one_score_wins'].sum()}-{int(rebuild_era['one_score_games'].sum() - rebuild_era['one_score_wins'].sum())}"
        rebuild_pct = rebuild_era['one_score_wins'].sum() / rebuild_era['one_score_games'].sum() * 100
        print(f"Rebuild Era (2015-2017): {rebuild_record} ({rebuild_pct:.1f}%)")
    
    lamar_era = df[df['year'] >= 2019]
    if len(lamar_era) > 0:
        lamar_record = f"{lamar_era['one_score_wins'].sum()}-{int(lamar_era['one_score_games'].sum() - lamar_era['one_score_wins'].sum())}"
        lamar_pct = lamar_era['one_score_wins'].sum() / lamar_era['one_score_games'].sum() * 100
        print(f"Lamar Era (2019+): {lamar_record} ({lamar_pct:.1f}%)")


if __name__ == "__main__":
    create_one_score_trend_visualization()
