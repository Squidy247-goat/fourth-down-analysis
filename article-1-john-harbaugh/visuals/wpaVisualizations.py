"""
makes a heatmap showing which parts of the game contribute to wins
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def get_wpa_data():
    """gets the wpa numbers for offense defense and special teams"""
    
    # numbers from the analysis
    wpa_data = {
        2008: {
            'offense': -1.164,
            'defense': 4.783,
            'special_teams': -0.293
        },
        2009: {
            'offense': -0.596,
            'defense': 1.602,
            'special_teams': -0.114
        },
        2010: {
            'offense': -0.050,
            'defense': 3.748,
            'special_teams': 0.287
        },
        2011: {
            'offense': 1.538,
            'defense': 2.655,
            'special_teams': -0.192
        }
    }
    
    return wpa_data


def create_wpa_heatmap():
    """
    Create a heatmap showing WPA contribution by phase across seasons.
    """
    # Get the data
    wpa_data = get_wpa_data()
    
    # Convert to DataFrame for heatmap
    years = sorted(wpa_data.keys())
    phases = ['Offense', 'Defense', 'Special Teams']
    
    # Create matrix for heatmap
    data_matrix = []
    for year in years:
        row = [
            wpa_data[year]['offense'],
            wpa_data[year]['defense'],
            wpa_data[year]['special_teams']
        ]
        data_matrix.append(row)
    
    df = pd.DataFrame(data_matrix, columns=phases, index=years)
    
    # Create the heatmap
    plt.figure(figsize=(10, 6))
    
    # Use a diverging colormap centered at 0
    # Positive = good (green), Negative = bad (red)
    sns.heatmap(df, 
                annot=True, 
                fmt='.2f', 
                cmap='RdYlGn',
                center=0,
                cbar_kws={'label': 'Win Probability Added'},
                linewidths=2,
                linecolor='white',
                vmin=-2,
                vmax=5,
                annot_kws={'size': 14, 'weight': 'bold'})
    
    plt.title('Ravens Win Probability Added by Phase (2008-2011)\nRegular Season Only', 
              fontsize=16, 
              fontweight='bold',
              pad=20)
    plt.xlabel('Game Phase', fontsize=13, fontweight='bold')
    plt.ylabel('Season', fontsize=13, fontweight='bold')
    
    # Rotate y-axis labels to be horizontal
    plt.yticks(rotation=0)
    
    # Add a note about interpretation
    plt.figtext(0.5, -0.05, 
                'Positive values (green) = Contributing to wins | Negative values (red) = Hurting win probability',
                ha='center',
                fontsize=10,
                style='italic',
                wrap=True)
    
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / 'output' / 'visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the figure
    output_path = output_dir / 'wpaHeatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Heatmap saved to: {output_path}")
    
    # Also display summary statistics
    print(f"\n{'='*70}")
    print("WPA SUMMARY STATISTICS")
    print(f"{'='*70}\n")
    
    print("Total WPA by Phase (2008-2011):")
    print(f"  Offense:       {df['Offense'].sum():+.2f}")
    print(f"  Defense:       {df['Defense'].sum():+.2f}")
    print(f"  Special Teams: {df['Special Teams'].sum():+.2f}")
    print(f"  Total:         {df.sum().sum():+.2f}")
    
    print(f"\nAverage WPA per Season:")
    print(f"  Offense:       {df['Offense'].mean():+.2f}")
    print(f"  Defense:       {df['Defense'].mean():+.2f}")
    print(f"  Special Teams: {df['Special Teams'].mean():+.2f}")
    
    print(f"\nBest Season by Phase:")
    for phase in phases:
        best_year = df[phase].idxmax()
        best_value = df[phase].max()
        print(f"  {phase}: {best_year} ({best_value:+.2f})")
    
    print(f"\nWorst Season by Phase:")
    for phase in phases:
        worst_year = df[phase].idxmin()
        worst_value = df[phase].min()
        print(f"  {phase}: {worst_year} ({worst_value:+.2f})")
    
    return df


def main():
    """Generate WPA heatmap visualization."""
    
    print(f"\n{'='*70}")
    print("GENERATING WPA VISUALIZATION")
    print(f"{'='*70}\n")
    
    df = create_wpa_heatmap()
    
    print(f"\n{'='*70}")
    print("KEY INSIGHTS:")
    print(f"{'='*70}\n")
    
    print("1. Defense was consistently the Ravens' strongest phase")
    print("   - Positive WPA in all 4 seasons")
    print(f"   - Best year: 2008 (+4.78 WPA)")
    
    print("\n2. Offense showed steady improvement")
    print("   - Started negative in 2008-2009")
    print("   - Became neutral in 2010")
    print("   - Turned positive in 2011 (+1.54 WPA)")
    
    print("\n3. Special teams were inconsistent")
    print("   - Mostly negative impact except 2010")
    print("   - Average: -0.08 WPA per season")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
