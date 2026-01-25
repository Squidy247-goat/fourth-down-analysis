import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def create_epa_bar_chart(output_path='../output/visuals/epa_bar_chart.png'):
    """Create simple EPA per dropback bar chart"""
    
    # Data
    regular_season_epa = 0.0715
    playoff_epa = 0.1495
    league_avg = 0.05
    delta = playoff_epa - regular_season_epa
    percent_improvement = (delta / regular_season_epa) * 100
    
    # Set up figure
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
    ax.set_facecolor('white')
    
    # Bar positions and data
    x_positions = [0.3, 0.7]  # Left and right positions
    bar_width = 0.15
    
    # Create bars
    bars = ax.bar(x_positions, 
                  [regular_season_epa, playoff_epa],
                  width=bar_width,
                  color=['#4a7c9c', '#c83803'],
                  edgecolor='white',
                  linewidth=2,
                  zorder=3)
    
    # Add league average reference line
    ax.axhline(y=league_avg, color='#999999', linestyle='--', 
              linewidth=2, alpha=0.7, zorder=2)
    ax.text(0.95, league_avg + 0.005, 'League Avg', 
           fontsize=11, color='#999999', ha='left')
    
    # Add value labels on top of bars
    ax.text(x_positions[0], regular_season_epa + 0.008, 
           f'{regular_season_epa:.4f}',
           ha='center', fontsize=20, fontweight='bold', color='#2c3e50')
    
    ax.text(x_positions[1], playoff_epa + 0.008,
           f'{playoff_epa:.4f}',
           ha='center', fontsize=20, fontweight='bold', color='#2c3e50')
    
    # Add category labels above bars
    ax.text(x_positions[0], -0.035, 'Regular Season',
           ha='center', fontsize=16, fontweight='bold', color='#4a7c9c')
    ax.text(x_positions[0], -0.045, '16 games',
           ha='center', fontsize=11, color='#7f8c8d')
    
    ax.text(x_positions[1], -0.035, 'Playoffs',
           ha='center', fontsize=16, fontweight='bold', color='#c83803')
    ax.text(x_positions[1], -0.045, '2 games',
           ha='center', fontsize=11, color='#7f8c8d')
    
    # Removed delta indicator for cleaner look
    
    # Set y-axis
    ax.set_ylim(-0.05, 0.20)
    ax.set_ylabel('EPA per Dropback', fontsize=14, fontweight='bold', color='#2c3e50')
    
    # Y-axis ticks and grid
    y_ticks = np.arange(-0.05, 0.21, 0.05)
    ax.set_yticks(y_ticks)
    ax.yaxis.grid(True, color='#e0e0e0', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)
    ax.set_axisbelow(True)
    
    # Format y-axis labels
    ax.set_yticklabels([f'{y:.2f}' for y in y_ticks], fontsize=11, color='#2c3e50')
    
    # Remove x-axis elements
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['left'].set_color('#2c3e50')
    
    # Title
    fig.text(0.5, 0.95, 'Caleb Williams: Playoff Efficiency Surge',
            ha='center', fontsize=24, fontweight='bold', color='#1a2332')
    
    # Caption
    fig.text(0.5, 0.02, '2025 Season | EPA = Expected Points Added per dropback attempt',
            ha='center', fontsize=11, color='#7f8c8d')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.93])
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nEPA bar chart saved to: {output_path}")
    
    plt.close()

def main():
    """Main execution"""
    print("="*70)
    print("SIMPLE EPA BAR CHART")
    print("="*70)
    
    print("\nGenerating clean bar chart...")
    create_epa_bar_chart()
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
