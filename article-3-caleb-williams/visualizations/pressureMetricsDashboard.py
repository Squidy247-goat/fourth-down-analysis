import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

def load_pressure_data():
    """Load pressure-related QB data for 2025 and 2024"""
    
    base_path = '../output/cleaning/'
    
    # Load 2025 pressure data
    pressure_2025 = pd.read_csv(base_path + 'all_qb_pressure_stats_2025.csv')
    pressure_2024 = pd.read_csv(base_path + 'all_qb_pressure_stats_2024.csv')
    
    # Filter for qualifying QBs (min 250 dropbacks)
    pressure_2025 = pressure_2025[pressure_2025['total_dropbacks'] >= 250].copy()
    
    print(f"Loaded {len(pressure_2025)} qualifying QBs (2025)")
    
    return pressure_2025, pressure_2024

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

def create_gradient_background(ax, x_range, y_range, invert_x=False, invert_y=False):
    """
    Create diagonal gradient background
    invert_x: True if lower X is better (e.g., sack rate, turnover rate)
    invert_y: True if lower Y is better
    """
    X, Y = np.meshgrid(x_range, y_range)
    
    # Normalize to 0-1 range
    x_norm = (X - x_range[0]) / (x_range[-1] - x_range[0])
    y_norm = (Y - y_range[0]) / (y_range[-1] - y_range[0])
    
    # Invert if lower is better
    if invert_x:
        x_norm = 1 - x_norm
    if invert_y:
        y_norm = 1 - y_norm
    
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

def create_pressure_dashboard(pressure_2025, pressure_2024, output_path='../output/visuals/pressure_metrics_dashboard.png'):
    """Create 4-panel pressure metrics comparison dashboard"""
    
    # Set up figure with 2x2 grid
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), facecolor='white')
    
    # Main title
    fig.suptitle('Caleb Williams Under Pressure: 2025 Year 2 Performance',
                fontsize=26, fontweight='bold', color='#1a2332', y=0.98)
    
    # Get team colors and Caleb's data
    team_colors = get_team_colors()
    caleb_2025 = pressure_2025[pressure_2025['qb_name'] == 'C.Williams'].iloc[0]
    caleb_2024 = pressure_2024[pressure_2024['qb_name'] == 'C.Williams'].iloc[0]
    
    # Calculate deltas
    delta_comp_pct = caleb_2025['completion_pct_under_pressure'] - caleb_2024['completion_pct_under_pressure']
    delta_sack_rate = caleb_2025['sack_rate'] - caleb_2024['sack_rate']
    delta_turnover_rate = caleb_2025['turnover_worthy_rate'] - caleb_2024['turnover_worthy_rate']
    
    # Calculate rankings
    rank_comp_pct = (pressure_2025['completion_pct_under_pressure'] >= caleb_2025['completion_pct_under_pressure']).sum()
    rank_sack_rate = (pressure_2025['sack_rate'] <= caleb_2025['sack_rate']).sum()  # Lower is better
    rank_turnover = (pressure_2025['turnover_worthy_rate'] <= caleb_2025['turnover_worthy_rate']).sum()  # Lower is better
    total_qbs = len(pressure_2025)
    
    # Calculate league averages
    league_avg = {
        'comp_pct': pressure_2025['completion_pct_under_pressure'].mean(),
        'sack_rate': pressure_2025['sack_rate'].mean(),
        'time_to_throw': pressure_2025['estimated_time_to_throw'].mean(),
        'turnover_rate': pressure_2025['turnover_worthy_rate'].mean()
    }
    
    # ========== PANEL 1: Comp % Under Pressure vs Sack Rate ==========
    ax = ax1
    
    # Create gradient background (lower sack rate is better, higher comp% is better)
    x_range = np.linspace(0, 50, 100)
    y_range = np.linspace(2, 15, 100)
    create_gradient_background(ax, x_range, y_range, invert_x=False, invert_y=True)
    
    # Plot all QBs
    for idx, qb in pressure_2025.iterrows():
        if qb['qb_name'] != 'C.Williams':
            color = team_colors.get(qb['qb_name'].split('.')[1][:3].upper(), '#7f8c8d')
            ax.scatter(qb['completion_pct_under_pressure'], qb['sack_rate'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb Williams
    ax.scatter(caleb_2025['completion_pct_under_pressure'], caleb_2025['sack_rate'],
              s=400, c='#c83803', marker='*',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['comp_pct'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['sack_rate'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Completion % Under Pressure', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Sack Rate (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Handling Pressure: Completion vs Sack Rate',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb_2025['completion_pct_under_pressure']:.1f}% Comp (#{rank_comp_pct})\n{caleb_2025['sack_rate']:.2f}% Sack Rate (#2!)",
                xy=(caleb_2025['completion_pct_under_pressure'], caleb_2025['sack_rate']),
                xytext=(caleb_2025['completion_pct_under_pressure'] + 5, caleb_2025['sack_rate'] + 1.5),
                fontsize=10, fontweight='bold', color='#c83803',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#c83803', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#c83803', lw=2),
                zorder=6)
    
    # Tier labels (top-right is elite: high comp%, low sack rate)
    ax.text(42, 3.5, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=-30)
    ax.text(8, 13, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=-30)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(0, 50)
    ax.set_ylim(2, 15)
    
    # ========== PANEL 2: Time to Throw vs Turnover-Worthy Rate ==========
    ax = ax2
    
    # Create gradient background (optimal time ~2.4s, lower turnover is better)
    x_range = np.linspace(2.0, 3.0, 100)
    y_range = np.linspace(0, 8, 100)
    create_gradient_background(ax, x_range, y_range, invert_x=False, invert_y=True)
    
    # Plot all QBs
    for idx, qb in pressure_2025.iterrows():
        if qb['qb_name'] != 'C.Williams':
            color = team_colors.get(qb['qb_name'].split('.')[1][:3].upper(), '#7f8c8d')
            ax.scatter(qb['estimated_time_to_throw'], qb['turnover_worthy_rate'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb
    ax.scatter(caleb_2025['estimated_time_to_throw'], caleb_2025['turnover_worthy_rate'],
              s=400, c='#c83803', marker='*',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['time_to_throw'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['turnover_rate'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Time to Throw (seconds)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Turnover-Worthy Play Rate (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Decision Making: Speed vs Risk',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb_2025['estimated_time_to_throw']:.2f}s\n{caleb_2025['turnover_worthy_rate']:.2f}% Turnover Rate (#{rank_turnover})",
                xy=(caleb_2025['estimated_time_to_throw'], caleb_2025['turnover_worthy_rate']),
                xytext=(caleb_2025['estimated_time_to_throw'] - 0.2, caleb_2025['turnover_worthy_rate'] + 1.5),
                fontsize=10, fontweight='bold', color='#c83803',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#c83803', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#c83803', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(2.8, 1.0, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=0)
    ax.text(2.15, 7, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=0)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(2.0, 3.0)
    ax.set_ylim(0, 8)
    
    # ========== PANEL 3: Comp % Under Pressure vs Turnover-Worthy Rate ==========
    ax = ax3
    
    # Create gradient background (higher comp%, lower turnover is better)
    x_range = np.linspace(0, 50, 100)
    y_range = np.linspace(0, 8, 100)
    create_gradient_background(ax, x_range, y_range, invert_x=False, invert_y=True)
    
    # Plot all QBs
    for idx, qb in pressure_2025.iterrows():
        if qb['qb_name'] != 'C.Williams':
            color = team_colors.get(qb['qb_name'].split('.')[1][:3].upper(), '#7f8c8d')
            ax.scatter(qb['completion_pct_under_pressure'], qb['turnover_worthy_rate'],
                      s=80, c=color, alpha=0.5,
                      edgecolors='white', linewidths=0.8, zorder=3)
    
    # Highlight Caleb
    ax.scatter(caleb_2025['completion_pct_under_pressure'], caleb_2025['turnover_worthy_rate'],
              s=400, c='#c83803', marker='*',
              edgecolors='white', linewidths=3.5, zorder=5)
    
    # League average lines
    ax.axvline(league_avg['comp_pct'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    ax.axhline(league_avg['turnover_rate'], color='#7f8c8d',
              linestyle='--', linewidth=2.5, alpha=0.7, zorder=2)
    
    # Labels
    ax.set_xlabel('Completion % Under Pressure', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Turnover-Worthy Play Rate (%)', fontsize=13, fontweight='bold', color='#2c3e50')
    ax.set_title('Pressure Performance: Accuracy vs Ball Security',
                fontsize=18, fontweight='bold', color='#2c3e50', pad=15)
    
    # Caleb annotation
    ax.annotate(f"Caleb Williams\n{caleb_2025['completion_pct_under_pressure']:.1f}% Comp\n{caleb_2025['turnover_worthy_rate']:.2f}% Turnover",
                xy=(caleb_2025['completion_pct_under_pressure'], caleb_2025['turnover_worthy_rate']),
                xytext=(caleb_2025['completion_pct_under_pressure'] + 5, caleb_2025['turnover_worthy_rate'] + 1.2),
                fontsize=10, fontweight='bold', color='#c83803',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                         edgecolor='#c83803', linewidth=2),
                arrowprops=dict(arrowstyle='->', color='#c83803', lw=2),
                zorder=6)
    
    # Tier labels
    ax.text(42, 1.0, 'ELITE', fontsize=13, fontweight='bold',
           color='#2171b5', alpha=0.5, rotation=-25)
    ax.text(8, 7, 'STRUGGLING', fontsize=13, fontweight='bold',
           color='#cb181d', alpha=0.5, rotation=-25)
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#d3d3d3', zorder=0)
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 8)
    
    # ========== PANEL 4: Summary Stats Table ==========
    ax = ax4
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'Pressure Metrics: Year 1 → Year 2',
           ha='center', va='top', fontsize=18, fontweight='bold',
           color='#c83803', transform=ax.transAxes)
    
    # Table data with Year 1 → Year 2 comparison
    table_data = [
        ['Metric', 'Year 1', 'Year 2', 'Δ', 'Rank'],
        ['Comp % Under Pressure', 
         f"{caleb_2024['completion_pct_under_pressure']:.1f}%",
         f"{caleb_2025['completion_pct_under_pressure']:.1f}%",
         f"+{delta_comp_pct:.1f}%",
         f"#{rank_comp_pct}/{total_qbs}"],
        ['Sack Rate',
         f"{caleb_2024['sack_rate']:.2f}%",
         f"{caleb_2025['sack_rate']:.2f}%",
         f"{delta_sack_rate:.2f}%",
         f"#2/{total_qbs} 🔥"],
        ['Time to Throw',
         f"{caleb_2024['estimated_time_to_throw']:.2f}s",
         f"{caleb_2025['estimated_time_to_throw']:.2f}s",
         f"+{caleb_2025['estimated_time_to_throw'] - caleb_2024['estimated_time_to_throw']:.2f}s",
         "—"],
        ['Turnover-Worthy Rate',
         f"{caleb_2024['turnover_worthy_rate']:.2f}%",
         f"{caleb_2025['turnover_worthy_rate']:.2f}%",
         f"{delta_turnover_rate:.2f}%",
         f"#{rank_turnover}/{total_qbs}"],
        ['',
         '',
         '',
         '',
         ''],
        ['Key Takeaways', '', '', '', ''],
        ['• 2nd best sack rate in NFL', '', '', '', ''],
        ['• +16.7% comp under pressure', '', '', '', ''],
        ['• Top 10 ball security', '', '', '', ''],
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
            if i == 5:
                cell.set_facecolor('#f8f9fa')
                cell.set_edgecolor('#f8f9fa')
                continue
            
            # Takeaways section
            if i >= 6:
                cell.set_facecolor('white')
                cell.set_edgecolor('white')
                if j == 0:
                    cell.set_text_props(weight='bold', color='#2c3e50', fontsize=11)
                continue
            
            # Regular data rows
            if i % 2 == 0:
                cell.set_facecolor('#f8f9fa')
            else:
                cell.set_facecolor('white')
            cell.set_edgecolor('#d3d3d3')
            
            # Highlight improvements in delta column
            if j == 3 and i < 5:
                if '+' in table_data[i][j] or (i == 2 and '-' in table_data[i][j]):  # Sack rate decrease is good
                    cell.set_text_props(weight='bold', color='#27ae60')
                elif '-' in table_data[i][j]:
                    cell.set_text_props(weight='bold', color='#27ae60')
            
            # Highlight rank column
            if j == 4 and i < 5:
                cell.set_text_props(weight='bold', color='#c83803')
    
    # Footnote
    ax.text(0.5, 0.05, "Min. 250 dropbacks for qualifying QBs | Δ = Year 2 - Year 1",
           ha='center', va='bottom', fontsize=9,
           color='#7f8c8d', style='italic', transform=ax.transAxes)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    plt.subplots_adjust(hspace=0.28, wspace=0.22)
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nPressure metrics dashboard saved to: {output_path}")
    
    plt.close()

def main():
    """Main execution"""
    print("="*70)
    print("CALEB WILLIAMS PRESSURE METRICS DASHBOARD")
    print("="*70)
    
    # Load data
    print("\nLoading pressure data...")
    pressure_2025, pressure_2024 = load_pressure_data()
    
    # Print Caleb's stats
    caleb_2025 = pressure_2025[pressure_2025['qb_name'] == 'C.Williams'].iloc[0]
    caleb_2024 = pressure_2024[pressure_2024['qb_name'] == 'C.Williams'].iloc[0]
    
    print("\n" + "="*70)
    print("CALEB WILLIAMS PRESSURE STATS")
    print("="*70)
    print(f"\nYear 1 (2024):")
    print(f"  Comp % Under Pressure: {caleb_2024['completion_pct_under_pressure']:.1f}%")
    print(f"  Sack Rate: {caleb_2024['sack_rate']:.2f}%")
    print(f"  Time to Throw: {caleb_2024['estimated_time_to_throw']:.2f}s")
    print(f"  Turnover-Worthy Rate: {caleb_2024['turnover_worthy_rate']:.2f}%")
    
    print(f"\nYear 2 (2025):")
    print(f"  Comp % Under Pressure: {caleb_2025['completion_pct_under_pressure']:.1f}%")
    print(f"  Sack Rate: {caleb_2025['sack_rate']:.2f}% (2nd best!)")
    print(f"  Time to Throw: {caleb_2025['estimated_time_to_throw']:.2f}s")
    print(f"  Turnover-Worthy Rate: {caleb_2025['turnover_worthy_rate']:.2f}%")
    
    print(f"\nImprovements:")
    print(f"  Comp % Under Pressure: +{caleb_2025['completion_pct_under_pressure'] - caleb_2024['completion_pct_under_pressure']:.1f}%")
    print(f"  Sack Rate: {caleb_2025['sack_rate'] - caleb_2024['sack_rate']:.2f}%")
    print(f"  Turnover-Worthy Rate: {caleb_2025['turnover_worthy_rate'] - caleb_2024['turnover_worthy_rate']:.2f}%")
    
    # Create dashboard
    print("\n" + "="*70)
    print("GENERATING 4-PANEL PRESSURE DASHBOARD")
    print("="*70)
    
    create_pressure_dashboard(pressure_2025, pressure_2024)
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
