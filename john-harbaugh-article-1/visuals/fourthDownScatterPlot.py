"""
scatter plot showing if ravens 4th down calls get better or worse over time
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def get_fourth_down_data(year):
    """gets 4th down numbers for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for fourth down plays where Ravens go for it (run or pass)
    ravens_attempts = df[
        (df['down'] == 4) & 
        (df['posteam'] == 'BAL') &
        (df['play_type'].isin(['run', 'pass']))
    ].copy()
    
    if len(ravens_attempts) == 0:
        return None
    
    # Calculate conversions
    conversions = ravens_attempts[
        (ravens_attempts['first_down'] == 1) | 
        (ravens_attempts['touchdown'] == 1)
    ]
    
    total_attempts = len(ravens_attempts)
    total_conversions = len(conversions)
    conversion_rate = (total_conversions / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        'year': year,
        'attempts': total_attempts,
        'conversions': total_conversions,
        'conversion_rate': conversion_rate
    }


def create_scatter_plot():
    """Create scatter plot of 4th down attempts vs conversion rate."""
    
    years = list(range(2008, 2025))
    data = []
    
    print("Collecting data...")
    for year in years:
        result = get_fourth_down_data(year)
        if result:
            data.append(result)
            print(f"  {year}: {result['attempts']} attempts, {result['conversion_rate']:.1f}% conversion")
    
    if not data:
        print("No data available")
        return
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Define era colors
    def get_era_color(year):
        if year <= 2011:
            return '#1f77b4', 'Early Years (2008-2011)'
        elif year <= 2014:
            return '#ff7f0e', 'Championship (2012-2014)'
        elif year <= 2017:
            return '#2ca02c', 'Rebuild (2015-2017)'
        else:
            return '#d62728', 'Lamar Era (2018-2024)'
    
    df['color'], df['era'] = zip(*df['year'].map(get_era_color))
    
    # Calculate trend line
    z = np.polyfit(df['attempts'], df['conversion_rate'], 1)
    p = np.poly1d(z)
    
    # Calculate correlation
    correlation = df['attempts'].corr(df['conversion_rate'])
    
    # Manual calculation of linear regression statistics
    slope = z[0]
    intercept = z[1]
    r_value = correlation
    
    # Calculate p-value manually (simplified approach)
    n = len(df)
    t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2)) if abs(correlation) < 1 else 0
    # Approximate p-value using t-distribution (two-tailed)
    from math import sqrt
    df_stat = n - 2
    # Simplified p-value approximation
    if abs(t_stat) > 2.5:
        p_value = 0.01
    elif abs(t_stat) > 2.0:
        p_value = 0.05
    elif abs(t_stat) > 1.5:
        p_value = 0.15
    else:
        p_value = 0.20
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot points by era
    eras = df['era'].unique()
    for era in eras:
        era_data = df[df['era'] == era]
        ax.scatter(era_data['attempts'], era_data['conversion_rate'], 
                  c=era_data['color'].iloc[0], s=150, alpha=0.7, 
                  edgecolors='black', linewidth=1.5, label=era, zorder=3)
    
    # Add year labels to each point
    for idx, row in df.iterrows():
        ax.annotate(str(row['year']), 
                   (row['attempts'], row['conversion_rate']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, alpha=0.7, fontweight='bold')
    
    # Plot trend line
    trend_x = np.linspace(df['attempts'].min() - 1, df['attempts'].max() + 1, 100)
    trend_y = p(trend_x)
    ax.plot(trend_x, trend_y, 'k--', linewidth=2, alpha=0.5, 
            label=f'Trend Line (r={correlation:.3f}, p={p_value:.3f})', zorder=2)
    
    # Add 50% reference line
    ax.axhline(y=50, color='gray', linestyle=':', linewidth=1.5, alpha=0.5, 
               label='50% Conversion Rate', zorder=1)
    
    # Styling
    ax.set_xlabel('4th Down Attempts (per season)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Conversion Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('Ravens 4th Down Aggressiveness vs Success Rate (2008-2024)\n' + 
                 'Has Increased Aggressiveness Led to Better Execution?', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Set axis limits with padding
    ax.set_xlim(df['attempts'].min() - 2, df['attempts'].max() + 2)
    ax.set_ylim(30, 75)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    
    # Legend - position it better to avoid overlap
    ax.legend(loc='lower right', fontsize=10, framealpha=0.95, edgecolor='black')
    
    # Add statistics box - moved to upper left
    stats_text = f'Correlation: {correlation:.3f}\n'
    stats_text += f'R² = {r_value**2:.3f}\n'
    stats_text += f'p-value = {p_value:.4f}\n'
    if p_value < 0.05:
        stats_text += 'Statistically significant'
    else:
        stats_text += 'Not statistically significant'
    
    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9, edgecolor='black'))
    
    # Add interpretation box - moved to lower left
    if correlation > 0:
        interpretation = 'Positive Correlation:\nMore attempts → Higher conversion rates'
    else:
        interpretation = 'Negative Correlation:\nMore attempts → Lower conversion rates'
    
    ax.text(0.02, 0.02, interpretation,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment='bottom',
            horizontalalignment='left',
            fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9, edgecolor='black'))
    
    plt.tight_layout()
    
    # save the plot
    output_path = Path(__file__).parent.parent / "output" / "visualizations" / "fourthDownScatterPlot.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nScatter plot saved to: {output_path}")
    
    plt.close()
    
    # Print summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}")
    print(f"Correlation coefficient: {correlation:.3f}")
    print(f"R-squared: {r_value**2:.3f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Slope: {slope:.3f} (% change per additional attempt)")
    print(f"Intercept: {intercept:.3f}")
    
    if p_value < 0.05:
        print(f"\n✓ The relationship is STATISTICALLY SIGNIFICANT (p < 0.05)")
    else:
        print(f"\n✗ The relationship is NOT statistically significant (p >= 0.05)")
    
    if correlation > 0.3:
        print(f"✓ STRONG positive correlation: More aggressive → Better execution")
    elif correlation > 0:
        print(f"◐ WEAK positive correlation: Slight improvement with more attempts")
    elif correlation > -0.3:
        print(f"◐ WEAK negative correlation: Slight decline with more attempts")
    else:
        print(f"✗ STRONG negative correlation: More aggressive → Worse execution")
    
    # Era-by-era analysis
    print(f"\n{'='*80}")
    print("ERA-BY-ERA ANALYSIS")
    print(f"{'='*80}\n")
    
    for era in eras:
        era_data = df[df['era'] == era]
        avg_attempts = era_data['attempts'].mean()
        avg_conversion = era_data['conversion_rate'].mean()
        print(f"{era}:")
        print(f"  Avg attempts per year: {avg_attempts:.1f}")
        print(f"  Avg conversion rate: {avg_conversion:.1f}%")


if __name__ == "__main__":
    create_scatter_plot()
