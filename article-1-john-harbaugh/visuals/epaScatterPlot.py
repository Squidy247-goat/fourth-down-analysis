"""
scatter plot showing regular season vs playoff offense
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def calculate_epa_for_year(year):
    """get epa for regular season and playoffs"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
        
        # Filter for offensive plays where Ravens have possession and EPA is not null
        offensive_plays = df[(df['posteam'] == 'BAL') & (df['epa'].notna())].copy()
        
        # Separate regular season and playoff data
        regular_season = offensive_plays[offensive_plays['season_type'] == 'REG'].copy()
        playoffs = offensive_plays[offensive_plays['season_type'] == 'POST'].copy()
        
        # Calculate EPA per play
        reg_season_epa = regular_season['epa'].mean() if len(regular_season) > 0 else None
        playoff_epa = playoffs['epa'].mean() if len(playoffs) > 0 else None
        
        # Only return if we have playoff data
        if playoff_epa is not None and reg_season_epa is not None:
            return {
                'year': year,
                'regular_season_epa': reg_season_epa,
                'playoff_epa': playoff_epa,
                'reg_plays': len(regular_season),
                'playoff_plays': len(playoffs)
            }
        else:
            return None
            
    except FileNotFoundError:
        return None


def create_epa_scatter_plot():
    """Create scatter plot of regular season vs playoff EPA."""
    
    # Years to analyze (Ravens playoff years during Harbaugh era)
    years = [2008, 2009, 2010, 2011, 2012, 2014, 2018, 2019, 2020, 2023]
    
    data = []
    for year in years:
        result = calculate_epa_for_year(year)
        if result:
            data.append(result)
    
    if not data:
        print("No data available for visualization")
        return
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    print("Data collected:")
    print(df)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Set style
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # Plot diagonal reference line (where playoff EPA = regular season EPA)
    min_val = min(df['regular_season_epa'].min(), df['playoff_epa'].min()) - 0.02
    max_val = max(df['regular_season_epa'].max(), df['playoff_epa'].max()) + 0.02
    ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.3, linewidth=1.5, 
            label='No change', zorder=1)
    
    # Shade regions
    # Above line = playoff improvement
    ax.fill_between([min_val, max_val], [min_val, max_val], [max_val, max_val], 
                     alpha=0.1, color='green', label='Playoff improvement')
    # Below line = playoff decline
    ax.fill_between([min_val, max_val], [min_val, max_val], [min_val, min_val], 
                     alpha=0.1, color='red', label='Playoff decline')
    
    # Plot all years except 2012
    other_years = df[df['year'] != 2012]
    ax.scatter(other_years['regular_season_epa'], other_years['playoff_epa'], 
               s=200, color='#241773', alpha=0.6, edgecolors='black', linewidth=1.5,
               zorder=3, label='Other playoff seasons')
    
    # Label other years
    for _, row in other_years.iterrows():
        ax.annotate(str(int(row['year'])), 
                   (row['regular_season_epa'], row['playoff_epa']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, fontweight='bold', color='#241773', alpha=0.8)
    
    # Highlight 2012
    df_2012 = df[df['year'] == 2012]
    if not df_2012.empty:
        ax.scatter(df_2012['regular_season_epa'], df_2012['playoff_epa'], 
                   s=500, color='#D4AF37', alpha=1.0, edgecolors='black', linewidth=3,
                   zorder=5, label='2012 Championship', marker='*')
        
        # Add prominent label for 2012
        ax.annotate('2012\nSuper Bowl\nChampions', 
                   (df_2012['regular_season_epa'].values[0], df_2012['playoff_epa'].values[0]),
                   xytext=(15, 15), textcoords='offset points',
                   fontsize=12, fontweight='bold', color='#D4AF37',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8, edgecolor='#D4AF37', linewidth=2),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', 
                                 color='#D4AF37', linewidth=2))
        
        # Add arrow showing the improvement
        reg_epa_2012 = df_2012['regular_season_epa'].values[0]
        playoff_epa_2012 = df_2012['playoff_epa'].values[0]
        
        # Draw vertical arrow showing improvement
        ax.annotate('', xy=(reg_epa_2012, playoff_epa_2012), 
                   xytext=(reg_epa_2012, reg_epa_2012),
                   arrowprops=dict(arrowstyle='->', color='#D4AF37', linewidth=3, alpha=0.7))
        
        # Add text showing the magnitude of improvement
        improvement = playoff_epa_2012 - reg_epa_2012
        ax.text(reg_epa_2012 - 0.015, (playoff_epa_2012 + reg_epa_2012) / 2,
               f'+{improvement:.3f}\nEPA/play', fontsize=10, fontweight='bold',
               color='#D4AF37', ha='right', va='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.6))
    
    # Labels and title
    ax.set_xlabel('Regular Season Offensive EPA per Play', fontsize=14, fontweight='bold')
    ax.set_ylabel('Playoff Offensive EPA per Play', fontsize=14, fontweight='bold')
    ax.set_title('Baltimore Ravens: Regular Season vs Playoff Offensive Performance\n' + 
                 'The 2012 Playoff Surge', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Legend
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10)
    
    # Add context text
    context_text = "Each point represents a Ravens playoff season.\nDistance above the diagonal line shows playoff improvement."
    ax.text(0.02, 0.98, context_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Set equal aspect ratio for better comparison
    ax.set_aspect('equal', adjustable='box')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    output_dir = Path(__file__).parent.parent / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "epaScatterPlot.png"
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nVisualization saved to: {output_path}")
    plt.close()
    
    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    for _, row in df.iterrows():
        improvement = row['playoff_epa'] - row['regular_season_epa']
        print(f"{int(row['year'])}: Regular Season EPA/play = {row['regular_season_epa']:+.4f}, "
              f"Playoff EPA/play = {row['playoff_epa']:+.4f}, "
              f"Difference = {improvement:+.4f}")


if __name__ == "__main__":
    create_epa_scatter_plot()
