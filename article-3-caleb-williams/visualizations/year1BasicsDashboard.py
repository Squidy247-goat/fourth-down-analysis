import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

def load_year1_data():
    """Load basic passing data for 2024 (Year 1)"""
    
    base_path = '../output/cleaning/'
    
    # Load 2024 data
    basic_2024 = pd.read_csv(base_path + 'all_qb_basic_passing_stats_2024.csv')
    advanced_2024 = pd.read_csv(base_path + 'all_qb_advanced_passing_stats_2024.csv')
    
    # Merge
    qb_data = basic_2024.merge(advanced_2024, on='qb_name', how='inner')
    
    # Filter for qualifying QBs (min 250 attempts)
    qb_data = qb_data[qb_data['attempts'] >= 250].copy()
    
    print(f"Loaded {len(qb_data)} qualifying QBs (2024)")
    
    return qb_data

def get_team_colors():
    """Return dict of team primary colors"""
    return {
        'CHI': '#c83803', 'KC': '#e31837', 'BUF': '#00338d', 'CIN': '#fb4f14',
        'BAL': '#241773', 'MIA': '#008e97', 'LAC': '#0080c6', 'SF': '#aa0000',
        'PHI': '#004c54', 'DAL': '#041e42', 'GB': '#203731', 'NYG': '#0b2265',
        'WAS': '#5a1414', 'MIN': '#4f2683', 'DET': '#0076b6', 'NO': '#d3bc8d',
        'ATL': '#a71930', 'CAR': '#0085ca', 'TB': '#d50a0a', 'ARI': '#97233f',
        'LAR': '#003594', 'SEA': '#002244', 'LV': '#000000', 'DEN': '#fb4f14',
        'TEN': '#0c2340', 'IND': '#002c5f', 'HOU': '#03202f', 'JAX': '#006778',
        'CLE': '#311d00', 'PIT': '#ffb612', 'NE': '#002244', 'NYJ': '#125740',
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

def create_year1_basics_dashboard(qb_data, output_path='../output/visuals/year1_basics_dashboard.png'):
    """Create 4-panel Year 1 basic metrics dashboard"""
    
    # Set up figure with 2x2 grid
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), facecolor='white')
    
    # Main title
    fig.suptitle('Caleb Williams Year 1 (2024): The Struggle',
                fontsize=26, fontweight='bold', color='#e74c3c', y=0.98)
    
    # Get team colors and Caleb's data
    team_colors = get_team_colors()
    caleb = qb_data[qb_data['qb_name'] == 'C.Williams'].iloc[0]
    
    # Calculate rankings
    rank_comp_pct = (qb_data['completion_pct'] >= caleb['completion_pct']).sum()
    rank_ypa = (qb_data['yards_per_attempt'] >= caleb['yards_per_attempt']).sum()
    rank_rating = (qb_data['passer_rating'] >= caleb['passer_rating']).sum()
    rank_epa = (qb_data['epa_per_dropback'] >= caleb['epa_per_dropback']).sum()
    total_qbs = len(qb_data)
    
    # Calculate league averages
    league_avg = {
        'comp_pct': qb_data['completion_pct'].mean(),
        'ypa': qb_data['yards_per_attempt'].mean(),
        'rating': qb_data['passer_rating'].mean(),
        'epa': qb_data['epa_per_dropback'].mean()
    }
    
    # ========== PANEL 1: Completion % vs Yards per Attempt ==========
    ax = ax1
    
    # Create gradient background
    x_range = np.linspace(50, 80, 100)
    y_range = np.linspace(4, 10, 100)
    create_gradient_background(ax, x_range, y_range)
    
    # Plot all QBs
    for idx, qb in qb_data.iterrows():
        if qb['qb_name'] != 'C.Williams':
            color = team_colors.get(qb['qb_name'].split('.')[1][:3].upper(), '#7f8c8d')
            ax.scatter(qb['completion_pct'], qb['yards_per_attempt'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb Williams (in red for Year 1 struggle)
    ax.scatter(caleb['completion_pct'], caleb['yards_per_attempt'],
              s=400, c='#e74c3c', marker='X',  # Red X for struggle
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['comp_pct'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['ypa'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Completion Percentage (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Yards per Attempt', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Basic Efficiency: Completion vs Yards',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb['completion_pct']:.1f}% (#{rank_comp_pct}/{total_qbs})\n{caleb['yards_per_attempt']:.2f} Y/A (#{rank_ypa}/{total_qbs})",
                xy=(caleb['completion_pct'], caleb['yards_per_attempt']),
                xytext=(caleb['completion_pct'] - 8, caleb['yards_per_attempt'] + 1.0),
                fontsize=10, fontweight='bold', color='#e74c3c',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#e74c3c', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(74, 9.2, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=35)
    ax.text(54, 4.8, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=35)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(50, 80)
    ax.set_ylim(4, 10)
    
    # ========== PANEL 2: Completion % vs Passer Rating ==========
    ax = ax2
    
    # Create gradient background
    x_range = np.linspace(50, 80, 100)
    y_range = np.linspace(60, 125, 100)
    create_gradient_background(ax, x_range, y_range)
    
    # Plot all QBs
    for idx, qb in qb_data.iterrows():
        if qb['qb_name'] != 'C.Williams':
            color = team_colors.get(qb['qb_name'].split('.')[1][:3].upper(), '#7f8c8d')
            ax.scatter(qb['completion_pct'], qb['passer_rating'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb
    ax.scatter(caleb['completion_pct'], caleb['passer_rating'],
              s=400, c='#e74c3c', marker='X',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['comp_pct'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['rating'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Completion Percentage (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Passer Rating', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Overall Performance: Completion vs Rating',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb['completion_pct']:.1f}% Comp\n{caleb['passer_rating']:.1f} Rating (#{rank_rating}/{total_qbs})",
                xy=(caleb['completion_pct'], caleb['passer_rating']),
                xytext=(caleb['completion_pct'] + 5, caleb['passer_rating'] - 12),
                fontsize=10, fontweight='bold', color='#e74c3c',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#e74c3c', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(74, 118, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=30)
    ax.text(54, 68, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=30)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(50, 80)
    ax.set_ylim(60, 125)
    
    # ========== PANEL 3: Yards per Attempt vs EPA per Dropback ==========
    ax = ax3
    
    # Create gradient background
    x_range = np.linspace(4, 10, 100)
    y_range = np.linspace(-0.3, 0.4, 100)
    create_gradient_background(ax, x_range, y_range)
    
    # Plot all QBs
    for idx, qb in qb_data.iterrows():
        if qb['qb_name'] != 'C.Williams':
            color = team_colors.get(qb['qb_name'].split('.')[1][:3].upper(), '#7f8c8d')
            ax.scatter(qb['yards_per_attempt'], qb['epa_per_dropback'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb
    ax.scatter(caleb['yards_per_attempt'], caleb['epa_per_dropback'],
              s=400, c='#e74c3c', marker='X',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['ypa'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['epa'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Yards per Attempt', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('EPA per Dropback', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Efficiency: Yards vs EPA',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb['yards_per_attempt']:.2f} Y/A\n{caleb['epa_per_dropback']:.3f} EPA (#{rank_epa}/{total_qbs})",
                xy=(caleb['yards_per_attempt'], caleb['epa_per_dropback']),
                xytext=(caleb['yards_per_attempt'] + 1.2, caleb['epa_per_dropback'] + 0.08),
                fontsize=10, fontweight='bold', color='#e74c3c',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#e74c3c', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(9.0, 0.32, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=30)
    ax.text(5.0, -0.22, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=30)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(4, 10)
    ax.set_ylim(-0.3, 0.4)
    
    # ========== PANEL 4: Summary Stats Table ==========
    ax = ax4
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'Year 1 (2024) Base Metrics',
           ha='center', va='top', fontsize=18, fontweight='bold',
           color='#e74c3c', transform=ax.transAxes)
    
    # Table data
    table_data = [
        ['Metric', 'Caleb', 'League Avg', 'Rank', 'Status'],
        ['Completion %',
         f"{caleb['completion_pct']:.2f}%",
         f"{league_avg['comp_pct']:.2f}%",
         f"#{rank_comp_pct}/{total_qbs}",
         'Below Avg'],
        ['Yards per Attempt',
         f"{caleb['yards_per_attempt']:.2f}",
         f"{league_avg['ypa']:.2f}",
         f"#{rank_ypa}/{total_qbs}",
         'Below Avg'],
        ['TD to INT Ratio',
         f"{int(caleb['pass_tds'])}:{int(caleb['interceptions'])}",
         f"{qb_data['td_int_ratio'].mean():.2f}",
         '—',
         'Average'],
        ['Passer Rating',
         f"{caleb['passer_rating']:.2f}",
         f"{league_avg['rating']:.2f}",
         f"#{rank_rating}/{total_qbs}",
         'Below Avg'],
        ['EPA per Dropback',
         f"{caleb['epa_per_dropback']:.3f}",
         f"{league_avg['epa']:.3f}",
         f"#{rank_epa}/{total_qbs}",
         'Below Avg'],
        ['',
         '',
         '',
         '',
         ''],
        ['Year 1 Reality Check', '', '', '', ''],
        ['• Bottom third in most metrics', '', '', '', ''],
        ['• Below league average across board', '', '', '', ''],
        ['• Classic rookie struggles', '', '', '', ''],
    ]
    
    # Create table
    table = ax.table(cellText=table_data, cellLoc='left',
                    loc='center', bbox=[0.05, 0.15, 0.9, 0.70])
    
    # Style table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style header row
    for i in range(5):
        cell = table[(0, i)]
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(weight='bold', color='white', fontsize=12)
    
    # Alternate row colors and styling
    for i in range(1, len(table_data)):
        for j in range(5):
            cell = table[(i, j)]
            
            # Separator row
            if i == 6:
                cell.set_facecolor('#f8f9fa')
                cell.set_edgecolor('#f8f9fa')
                continue
            
            # Reality check section
            if i >= 7:
                cell.set_facecolor('white')
                cell.set_edgecolor('white')
                if j == 0:
                    cell.set_text_props(weight='bold', color='#e74c3c', fontsize=11)
                continue
            
            # Regular data rows
            if i % 2 == 0:
                cell.set_facecolor('#f8f9fa')
            else:
                cell.set_facecolor('white')
            cell.set_edgecolor('#d3d3d3')
            
            # Highlight status column
            if j == 4 and i < 6:
                if 'Below' in table_data[i][j]:
                    cell.set_text_props(weight='bold', color='#e74c3c')
                elif 'Average' in table_data[i][j]:
                    cell.set_text_props(weight='bold', color='#f39c12')
            
            # Highlight rank column
            if j == 3 and '#' in str(table_data[i][j]):
                cell.set_text_props(weight='bold', color='#e74c3c')
    
    # Footnote
    ax.text(0.5, 0.05, "Min. 250 pass attempts for qualifying QBs | This is where the transformation began...",
           ha='center', va='bottom', fontsize=9,
           color='#7f8c8d', style='italic', transform=ax.transAxes)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    plt.subplots_adjust(hspace=0.28, wspace=0.22)
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nYear 1 basics dashboard saved to: {output_path}")
    
    plt.close()

def main():
    """Main execution"""
    print("="*70)
    print("CALEB WILLIAMS YEAR 1 (2024) BASICS DASHBOARD")
    print("="*70)
    
    # Load data
    print("\nLoading Year 1 data...")
    qb_data = load_year1_data()
    
    # Print Caleb's stats
    caleb = qb_data[qb_data['qb_name'] == 'C.Williams'].iloc[0]
    league_avg_comp = qb_data['completion_pct'].mean()
    league_avg_ypa = qb_data['yards_per_attempt'].mean()
    league_avg_rating = qb_data['passer_rating'].mean()
    
    print("\n" + "="*70)
    print("CALEB WILLIAMS YEAR 1 BASE METRICS")
    print("="*70)
    print(f"\nCompletion %: {caleb['completion_pct']:.2f}% (League Avg: {league_avg_comp:.2f}%)")
    print(f"Yards per Attempt: {caleb['yards_per_attempt']:.2f} (League Avg: {league_avg_ypa:.2f})")
    print(f"TD to INT: {int(caleb['pass_tds'])}:{int(caleb['interceptions'])}")
    print(f"Passer Rating: {caleb['passer_rating']:.2f} (League Avg: {league_avg_rating:.2f})")
    print(f"EPA per Dropback: {caleb['epa_per_dropback']:.3f}")
    
    rank_comp = (qb_data['completion_pct'] >= caleb['completion_pct']).sum()
    rank_ypa = (qb_data['yards_per_attempt'] >= caleb['yards_per_attempt']).sum()
    total = len(qb_data)
    
    print(f"\nRankings:")
    print(f"  Completion %: #{rank_comp}/{total}")
    print(f"  Yards per Attempt: #{rank_ypa}/{total}")
    print(f"  Status: Bottom third in most categories")
    
    # Create dashboard
    print("\n" + "="*70)
    print("GENERATING YEAR 1 BASICS DASHBOARD")
    print("="*70)
    
    create_year1_basics_dashboard(qb_data)
    
    print("\n" + "="*70)
    print("COMPLETE - Year 1 showed the struggle before Year 2 transformation")
    print("="*70)

if __name__ == "__main__":
    main()
