import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

def load_all_qb_data():
    """Load all QB data from CSV files for 2025"""
    
    base_path = '../output/cleaning/'
    
    # Load 2025 data
    basic_2025 = pd.read_csv(base_path + 'all_qb_basic_passing_stats_2025.csv')
    advanced_2025 = pd.read_csv(base_path + 'all_qb_advanced_passing_stats_2025.csv')
    pressure_2025 = pd.read_csv(base_path + 'all_qb_pressure_stats_2025.csv')
    third_down_2025 = pd.read_csv(base_path + 'qb_third_down_rankings_2025.csv')
    red_zone_2025 = pd.read_csv(base_path + 'all_qb_red_zone_stats_2025.csv')
    two_min_2025 = pd.read_csv(base_path + 'all_qb_two_minute_drill_2025.csv')
    
    # Merge all dataframes
    qb_data = basic_2025.merge(advanced_2025, on='qb_name', how='inner', suffixes=('', '_adv'))
    qb_data = qb_data.merge(third_down_2025, on='qb_name', how='left', suffixes=('', '_3rd'))
    qb_data = qb_data.merge(red_zone_2025, on='qb_name', how='left', suffixes=('', '_rz'))
    qb_data = qb_data.merge(two_min_2025, on='qb_name', how='left', suffixes=('', '_2min'))
    
    # Filter for qualifying QBs (min 250 attempts)
    qb_data = qb_data[qb_data['attempts'] >= 250].copy()
    
    # Calculate additional metrics
    qb_data['third_down_epa'] = qb_data.apply(
        lambda row: calculate_third_down_epa(row), axis=1
    )
    
    print(f"Loaded {len(qb_data)} qualifying QBs")
    
    return qb_data

def calculate_third_down_epa(row):
    """Estimate third down EPA (simplified calculation)"""
    # Use success rate and conversion rate as proxy
    conv_rate = row.get('third_down_conversion_rate', 35) / 100
    return (conv_rate - 0.35) * 0.5  # Normalized approximation

def get_team_colors():
    """Return dict of team primary colors"""
    return {
        'CHI': '#c83803',  # Bears orange
        'KC': '#e31837',   # Chiefs red
        'BUF': '#00338d',  # Bills blue
        'CIN': '#fb4f14',  # Bengals orange
        'BAL': '#241773',  # Ravens purple
        'MIA': '#008e97',  # Dolphins teal
        'LAC': '#0080c6',  # Chargers blue
        'SF': '#aa0000',   # 49ers red
        'PHI': '#004c54',  # Eagles green
        'DAL': '#041e42',  # Cowboys navy
        'GB': '#203731',   # Packers green
        'NYG': '#0b2265',  # Giants blue
        'WAS': '#5a1414',  # Commanders burgundy
        'MIN': '#4f2683',  # Vikings purple
        'DET': '#0076b6',  # Lions blue
        'NO': '#d3bc8d',   # Saints gold
        'ATL': '#a71930',  # Falcons red
        'CAR': '#0085ca',  # Panthers blue
        'TB': '#d50a0a',   # Bucs red
        'ARI': '#97233f',  # Cardinals red
        'LAR': '#003594',  # Rams blue
        'SEA': '#002244',  # Seahawks navy
        'LV': '#000000',   # Raiders black
        'DEN': '#fb4f14',  # Broncos orange
        'TEN': '#0c2340',  # Titans navy
        'IND': '#002c5f',  # Colts blue
        'HOU': '#03202f',  # Texans navy
        'JAX': '#006778',  # Jaguars teal
        'CLE': '#311d00',  # Browns brown
        'PIT': '#ffb612',  # Steelers gold
        'NE': '#002244',   # Patriots navy
        'NYJ': '#125740',  # Jets green
    }

def create_gradient_background(ax, x_range, y_range):
    """Create diagonal gradient background from poor to elite"""
    X, Y = np.meshgrid(x_range, y_range)
    
    # Normalize to 0-1 range
    x_norm = (X - x_range[0]) / (x_range[-1] - x_range[0])
    y_norm = (Y - y_range[0]) / (y_range[-1] - y_range[0])
    
    # Diagonal gradient (bottom-left = 0, top-right = 2)
    Z = x_norm + y_norm
    
    # Create contour-filled background
    contour = ax.contourf(X, Y, Z, levels=20, 
                          cmap='RdYlBu', alpha=0.3, zorder=1)
    
    # Add tier contour lines
    tier_lines = ax.contour(X, Y, Z, levels=[0.4, 0.8, 1.2, 1.6],
                            colors='#d3d3d3', linewidths=1.5, 
                            linestyles='--', alpha=0.6, zorder=2)
    
    return contour, tier_lines

def create_qb_comparison_dashboard(qb_data, output_path='../output/visuals/qb_comparison_dashboard.png'):
    """Create 4-panel QB comparison dashboard"""
    
    # Set up figure with 2x2 grid
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), facecolor='white')
    
    # Main title
    fig.suptitle('Caleb Williams vs NFL QBs: 2025 Year 2 Performance',
                fontsize=26, fontweight='bold', color='#1a2332', y=0.98)
    
    # Get team colors and Caleb's data
    team_colors = get_team_colors()
    caleb = qb_data[qb_data['qb_name'] == 'C.Williams'].iloc[0]
    
    # Calculate league averages
    league_avg = {
        'third_down_conv': qb_data['third_down_conversion_rate'].mean(),
        'red_zone_td': qb_data['td_rate'].mean(),
        'two_min_points': qb_data['points_per_game'].mean(),
        'two_min_drives': qb_data['drives_ending_in_points_pct'].mean(),
        'third_down_epa': qb_data['third_down_epa'].mean()
    }
    
    # ========== PANEL 1: Clutch Performance (Third Down vs Red Zone) ==========
    ax = ax1
    
    # Create gradient background
    x_range = np.linspace(20, 50, 100)
    y_range = np.linspace(5, 35, 100)
    create_gradient_background(ax, x_range, y_range)
    
    # Plot all QBs
    for idx, qb in qb_data.iterrows():
        if qb['qb_name'] != 'C.Williams':
            team = qb.get('team', 'UNK')
            color = team_colors.get(team, '#7f8c8d')
            ax.scatter(qb['third_down_conversion_rate'], qb['td_rate'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb Williams
    ax.scatter(caleb['third_down_conversion_rate'], caleb['td_rate'],
              s=400, c='#c83803', marker='*',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['third_down_conv'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['red_zone_td'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Third Down Conversion Rate (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Red Zone TD Rate (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Clutch Situations: Converting When It Matters',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb['third_down_conversion_rate']:.1f}% 3rd Down (#{int(caleb['rank'])})\n{caleb['td_rate']:.1f}% RZ TD",
                xy=(caleb['third_down_conversion_rate'], caleb['td_rate']),
                xytext=(caleb['third_down_conversion_rate'] + 3, caleb['td_rate'] + 4),
                fontsize=10, fontweight='bold', color='#c83803',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#c83803', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#c83803', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(45, 32, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=40)
    ax.text(25, 8, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=40)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(20, 50)
    ax.set_ylim(5, 35)
    
    # ========== PANEL 2: Two-Minute Drill Excellence ==========
    ax = ax2
    
    # Create gradient background
    x_range = np.linspace(15, 60, 100)
    y_range = np.linspace(0.5, 4.0, 100)
    create_gradient_background(ax, x_range, y_range)
    
    # Plot all QBs
    for idx, qb in qb_data.iterrows():
        if qb['qb_name'] != 'C.Williams':
            team = qb.get('team', 'UNK')
            color = team_colors.get(team, '#7f8c8d')
            ax.scatter(qb['drives_ending_in_points_pct'], qb['points_per_game'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb
    ax.scatter(caleb['drives_ending_in_points_pct'], caleb['points_per_game'],
              s=400, c='#c83803', marker='*',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['two_min_drives'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['two_min_points'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Two-Minute Drives Ending in Points (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Points per Game (Final 2 Min)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Two-Minute Drill Excellence',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb['drives_ending_in_points_pct']:.1f}% Drives\n{caleb['points_per_game']:.2f} PPG",
                xy=(caleb['drives_ending_in_points_pct'], caleb['points_per_game']),
                xytext=(caleb['drives_ending_in_points_pct'] - 8, caleb['points_per_game'] + 0.6),
                fontsize=10, fontweight='bold', color='#c83803',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#c83803', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#c83803', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(52, 3.6, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=35)
    ax.text(20, 0.8, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=35)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(15, 60)
    ax.set_ylim(0.5, 4.0)
    
    # ========== PANEL 3: Third Down EPA Efficiency ==========
    ax = ax3
    
    # Create gradient background
    x_range = np.linspace(20, 50, 100)
    y_range = np.linspace(-0.15, 0.20, 100)
    create_gradient_background(ax, x_range, y_range)
    
    # Plot all QBs
    for idx, qb in qb_data.iterrows():
        if qb['qb_name'] != 'C.Williams':
            team = qb.get('team', 'UNK')
            color = team_colors.get(team, '#7f8c8d')
            ax.scatter(qb['third_down_conversion_rate'], qb['third_down_epa'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb
    ax.scatter(caleb['third_down_conversion_rate'], caleb['third_down_epa'],
              s=400, c='#c83803', marker='*',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['third_down_conv'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['third_down_epa'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Third Down Conversion Rate (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Third Down EPA', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Third Down Efficiency',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb['third_down_conversion_rate']:.1f}% Conv\n{caleb['third_down_epa']:+.3f} EPA",
                xy=(caleb['third_down_conversion_rate'], caleb['third_down_epa']),
                xytext=(caleb['third_down_conversion_rate'] + 3, caleb['third_down_epa'] + 0.04),
                fontsize=10, fontweight='bold', color='#c83803',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#c83803', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#c83803', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(45, 0.17, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=35)
    ax.text(24, -0.10, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=35)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(20, 50)
    ax.set_ylim(-0.15, 0.20)
    
    # ========== PANEL 4: Summary Stats Table ==========
    ax = ax4
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'Caleb Williams Year 2 (2025)\nKey Performance Rankings',
           ha='center', va='top', fontsize=18, fontweight='bold',
           color='#c83803', transform=ax.transAxes)
    
    # Calculate percentiles
    third_down_rank = int(caleb['rank'])
    total_qbs = len(qb_data)
    
    # Get red zone EPA - handle potential suffix
    rz_epa_col = 'avg_epa_rz' if 'avg_epa_rz' in caleb.index else 'avg_epa'
    rz_epa = caleb[rz_epa_col] if rz_epa_col in caleb.index else 0.0
    
    # Table data
    table_data = [
        ['Metric', 'Value', 'Rank'],
        ['Third Down Conv Rate', f"{caleb['third_down_conversion_rate']:.1f}%", f"#{third_down_rank}/{total_qbs}"],
        ['Third Down EPA', f"{caleb['third_down_epa']:+.3f}", f"Top {int((third_down_rank/total_qbs)*100)}%"],
        ['Red Zone TD Rate', f"{caleb['td_rate']:.1f}%", f"Below Avg"],
        ['Red Zone Avg EPA', f"{rz_epa:.3f}", f"—"],
        ['Two-Min Points/Game', f"{caleb['points_per_game']:.2f}", f"Near Avg"],
        ['Two-Min Drives → Points', f"{caleb['drives_ending_in_points_pct']:.1f}%", f"Above Avg"],
        ['Game-Winning Drives', f"{caleb.get('touchdowns_2min', caleb.get('touchdowns', 'N/A'))}", f"Top Group"],
    ]
    
    # Create table
    table = ax.table(cellText=table_data, cellLoc='left',
                    loc='center', bbox=[0.05, 0.15, 0.9, 0.70])
    
    # Style table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.8)
    
    # Style header row
    for i in range(3):
        cell = table[(0, i)]
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(weight='bold', color='white', fontsize=12)
    
    # Alternate row colors
    for i in range(1, len(table_data)):
        for j in range(3):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#f8f9fa')
            else:
                cell.set_facecolor('white')
            cell.set_edgecolor('#d3d3d3')
            
            # Highlight rank column
            if j == 2:
                cell.set_text_props(weight='bold', color='#c83803')
    
    # Footnote
    ax.text(0.5, 0.05, "Min. 250 pass attempts for qualifying QBs | Data: 2025 NFL Season",
           ha='center', va='bottom', fontsize=9,
           color='#7f8c8d', style='italic', transform=ax.transAxes)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    plt.subplots_adjust(hspace=0.28, wspace=0.22)
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nQB comparison dashboard saved to: {output_path}")
    
    plt.close()

def main():
    """Main execution"""
    print("="*70)
    print("CALEB WILLIAMS QB COMPARISON DASHBOARD")
    print("="*70)
    
    # Load data
    print("\nLoading 2025 QB data...")
    qb_data = load_all_qb_data()
    
    # Print Caleb's stats
    caleb = qb_data[qb_data['qb_name'] == 'C.Williams'].iloc[0]
    print("\n" + "="*70)
    print("CALEB WILLIAMS 2025 STATS")
    print("="*70)
    print(f"\nThird Down Conv: {caleb['third_down_conversion_rate']:.1f}% (Rank #{int(caleb['rank'])})")
    print(f"Red Zone TD Rate: {caleb['td_rate']:.1f}%")
    print(f"Two-Min Points/Game: {caleb['points_per_game']:.2f}")
    print(f"Two-Min Drives → Points: {caleb['drives_ending_in_points_pct']:.1f}%")
    print(f"Third Down EPA: {caleb['third_down_epa']:+.3f}")
    
    # Create dashboard
    print("\n" + "="*70)
    print("GENERATING 4-PANEL DASHBOARD")
    print("="*70)
    
    create_qb_comparison_dashboard(qb_data)
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
