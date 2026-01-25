import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def load_caleb_data():
    """Load Caleb Williams data from all relevant CSV files"""
    
    # File paths
    base_path = '../output/cleaning/'
    
    # Load 2024 data
    basic_2024 = pd.read_csv(base_path + 'all_qb_basic_passing_stats_2024.csv')
    advanced_2024 = pd.read_csv(base_path + 'all_qb_advanced_passing_stats_2024.csv')
    pressure_2024 = pd.read_csv(base_path + 'all_qb_pressure_stats_2024.csv')
    third_down_2024 = pd.read_csv(base_path + 'qb_third_down_rankings_2024.csv')
    red_zone_2024 = pd.read_csv(base_path + 'all_qb_red_zone_stats_2024.csv')
    
    # Load 2025 data
    basic_2025 = pd.read_csv(base_path + 'all_qb_basic_passing_stats_2025.csv')
    advanced_2025 = pd.read_csv(base_path + 'all_qb_advanced_passing_stats_2025.csv')
    pressure_2025 = pd.read_csv(base_path + 'all_qb_pressure_stats_2025.csv')
    third_down_2025 = pd.read_csv(base_path + 'qb_third_down_rankings_2025.csv')
    red_zone_2025 = pd.read_csv(base_path + 'all_qb_red_zone_stats_2025.csv')
    
    # Extract Caleb Williams data
    caleb_basic_2024 = basic_2024[basic_2024['qb_name'] == 'C.Williams'].iloc[0]
    caleb_advanced_2024 = advanced_2024[advanced_2024['qb_name'] == 'C.Williams'].iloc[0]
    caleb_pressure_2024 = pressure_2024[pressure_2024['qb_name'] == 'C.Williams'].iloc[0]
    caleb_third_2024 = third_down_2024[third_down_2024['qb_name'] == 'C.Williams'].iloc[0]
    caleb_redzone_2024 = red_zone_2024[red_zone_2024['qb_name'] == 'C.Williams'].iloc[0]
    
    caleb_basic_2025 = basic_2025[basic_2025['qb_name'] == 'C.Williams'].iloc[0]
    caleb_advanced_2025 = advanced_2025[advanced_2025['qb_name'] == 'C.Williams'].iloc[0]
    caleb_pressure_2025 = pressure_2025[pressure_2025['qb_name'] == 'C.Williams'].iloc[0]
    caleb_third_2025 = third_down_2025[third_down_2025['qb_name'] == 'C.Williams'].iloc[0]
    caleb_redzone_2025 = red_zone_2025[red_zone_2025['qb_name'] == 'C.Williams'].iloc[0]
    
    # Calculate league averages for 2025
    league_avg_2025 = {
        'completion_pct': basic_2025['completion_pct'].mean(),
        'yards_per_attempt': basic_2025['yards_per_attempt'].mean(),
        'epa_per_dropback': advanced_2025['epa_per_dropback'].mean(),
        'success_rate': advanced_2025['success_rate'].mean(),
        'third_down_rate': third_down_2025['third_down_conversion_rate'].mean(),
        'red_zone_td_rate': red_zone_2025['td_rate'].mean(),
        'completion_under_pressure': pressure_2025['completion_pct_under_pressure'].mean(),
        'sack_rate': pressure_2025['sack_rate'].mean(),
        'turnover_rate': pressure_2025['turnover_worthy_rate'].mean(),
        'passer_rating': basic_2025['passer_rating'].mean()
    }
    
    # Calculate ranks for 2024
    rank_2024 = {}
    rank_2024['completion_pct'] = (basic_2024['completion_pct'] >= caleb_basic_2024['completion_pct']).sum()
    rank_2024['yards_per_attempt'] = (basic_2024['yards_per_attempt'] >= caleb_basic_2024['yards_per_attempt']).sum()
    rank_2024['epa_per_dropback'] = (advanced_2024['epa_per_dropback'] >= caleb_advanced_2024['epa_per_dropback']).sum()
    rank_2024['success_rate'] = (advanced_2024['success_rate'] >= caleb_advanced_2024['success_rate']).sum()
    rank_2024['third_down_rate'] = int(caleb_third_2024['rank'])
    rank_2024['red_zone_td_rate'] = (red_zone_2024['td_rate'] >= caleb_redzone_2024['td_rate']).sum()
    rank_2024['completion_under_pressure'] = (pressure_2024['completion_pct_under_pressure'] >= caleb_pressure_2024['completion_pct_under_pressure']).sum()
    rank_2024['sack_rate'] = (pressure_2024['sack_rate'] <= caleb_pressure_2024['sack_rate']).sum()
    rank_2024['turnover_rate'] = (pressure_2024['turnover_worthy_rate'] <= caleb_pressure_2024['turnover_worthy_rate']).sum()
    rank_2024['passer_rating'] = (basic_2024['passer_rating'] >= caleb_basic_2024['passer_rating']).sum()
    
    # Calculate ranks for 2025
    rank_2025 = {}
    rank_2025['completion_pct'] = (basic_2025['completion_pct'] >= caleb_basic_2025['completion_pct']).sum()
    rank_2025['yards_per_attempt'] = (basic_2025['yards_per_attempt'] >= caleb_basic_2025['yards_per_attempt']).sum()
    rank_2025['epa_per_dropback'] = (advanced_2025['epa_per_dropback'] >= caleb_advanced_2025['epa_per_dropback']).sum()
    rank_2025['success_rate'] = (advanced_2025['success_rate'] >= caleb_advanced_2025['success_rate']).sum()
    rank_2025['third_down_rate'] = int(caleb_third_2025['rank'])
    rank_2025['red_zone_td_rate'] = (red_zone_2025['td_rate'] >= caleb_redzone_2025['td_rate']).sum()
    rank_2025['completion_under_pressure'] = (pressure_2025['completion_pct_under_pressure'] >= caleb_pressure_2025['completion_pct_under_pressure']).sum()
    rank_2025['sack_rate'] = (pressure_2025['sack_rate'] <= caleb_pressure_2025['sack_rate']).sum()
    rank_2025['turnover_rate'] = (pressure_2025['turnover_worthy_rate'] <= caleb_pressure_2025['turnover_worthy_rate']).sum()
    rank_2025['passer_rating'] = (basic_2025['passer_rating'] >= caleb_basic_2025['passer_rating']).sum()
    
    # Compile metrics
    metrics = {
        'Completion %': {
            'year1': caleb_basic_2024['completion_pct'],
            'year2': caleb_basic_2025['completion_pct'],
            'league_avg': league_avg_2025['completion_pct'],
            'rank_y1': rank_2024['completion_pct'],
            'rank_y2': rank_2025['completion_pct'],
            'unit': '%',
            'higher_better': True
        },
        'Yards per Attempt': {
            'year1': caleb_basic_2024['yards_per_attempt'],
            'year2': caleb_basic_2025['yards_per_attempt'],
            'league_avg': league_avg_2025['yards_per_attempt'],
            'rank_y1': rank_2024['yards_per_attempt'],
            'rank_y2': rank_2025['yards_per_attempt'],
            'unit': ' yds',
            'higher_better': True
        },
        'EPA per Dropback': {
            'year1': caleb_advanced_2024['epa_per_dropback'],
            'year2': caleb_advanced_2025['epa_per_dropback'],
            'league_avg': league_avg_2025['epa_per_dropback'],
            'rank_y1': rank_2024['epa_per_dropback'],
            'rank_y2': rank_2025['epa_per_dropback'],
            'unit': '',
            'higher_better': True
        },
        'Success Rate': {
            'year1': caleb_advanced_2024['success_rate'],
            'year2': caleb_advanced_2025['success_rate'],
            'league_avg': league_avg_2025['success_rate'],
            'rank_y1': rank_2024['success_rate'],
            'rank_y2': rank_2025['success_rate'],
            'unit': '%',
            'higher_better': True
        },
        'Third Down Rate': {
            'year1': caleb_third_2024['third_down_conversion_rate'],
            'year2': caleb_third_2025['third_down_conversion_rate'],
            'league_avg': league_avg_2025['third_down_rate'],
            'rank_y1': rank_2024['third_down_rate'],
            'rank_y2': rank_2025['third_down_rate'],
            'unit': '%',
            'higher_better': True
        },
        'Red Zone TD Rate': {
            'year1': caleb_redzone_2024['td_rate'],
            'year2': caleb_redzone_2025['td_rate'],
            'league_avg': league_avg_2025['red_zone_td_rate'],
            'rank_y1': rank_2024['red_zone_td_rate'],
            'rank_y2': rank_2025['red_zone_td_rate'],
            'unit': '%',
            'higher_better': True
        },
        'Comp % Under Pressure': {
            'year1': caleb_pressure_2024['completion_pct_under_pressure'],
            'year2': caleb_pressure_2025['completion_pct_under_pressure'],
            'league_avg': league_avg_2025['completion_under_pressure'],
            'rank_y1': rank_2024['completion_under_pressure'],
            'rank_y2': rank_2025['completion_under_pressure'],
            'unit': '%',
            'higher_better': True
        },
        'Sack Rate': {
            'year1': caleb_pressure_2024['sack_rate'],
            'year2': caleb_pressure_2025['sack_rate'],
            'league_avg': league_avg_2025['sack_rate'],
            'rank_y1': rank_2024['sack_rate'],
            'rank_y2': rank_2025['sack_rate'],
            'unit': '%',
            'higher_better': False
        },
        'Turnover-Worthy Rate': {
            'year1': caleb_pressure_2024['turnover_worthy_rate'],
            'year2': caleb_pressure_2025['turnover_worthy_rate'],
            'league_avg': league_avg_2025['turnover_rate'],
            'rank_y1': rank_2024['turnover_rate'],
            'rank_y2': rank_2025['turnover_rate'],
            'unit': '%',
            'higher_better': False
        },
        'Passer Rating': {
            'year1': caleb_basic_2024['passer_rating'],
            'year2': caleb_basic_2025['passer_rating'],
            'league_avg': league_avg_2025['passer_rating'],
            'rank_y1': rank_2024['passer_rating'],
            'rank_y2': rank_2025['passer_rating'],
            'unit': '',
            'higher_better': True
        }
    }
    
    return metrics

def create_comparison_chart(metrics, output_path='../output/visuals/key_metrics_comparison.png'):
    """Create clean horizontal bar chart comparison"""
    
    # Set up figure
    fig, ax = plt.subplots(figsize=(14, 9), facecolor='#f8f9fa')
    ax.set_facecolor('#ffffff')
    
    # Colors
    year1_color = '#e74c3c'  # Red/orange for Year 1
    year2_color = '#27ae60'  # Green for Year 2
    league_avg_color = '#95a5a6'  # Gray for league average
    
    # Metrics in order
    metric_names = list(metrics.keys())
    n_metrics = len(metric_names)
    
    # Calculate positions
    bar_height = 0.35
    group_spacing = 1.0
    y_positions = np.arange(n_metrics) * group_spacing
    
    # Calculate max values for scaling
    max_vals = []
    for metric in metric_names:
        data = metrics[metric]
        max_val = max(data['year1'], data['year2'], data['league_avg'])
        max_vals.append(max_val * 1.15)  # Add 15% padding
    
    # Draw bars
    for i, metric in enumerate(metric_names):
        data = metrics[metric]
        y_base = y_positions[i]
        max_scale = max_vals[i]
        
        # Scale values to bar width
        year1_width = (data['year1'] / max_scale) * 10
        year2_width = (data['year2'] / max_scale) * 10
        league_avg_width = (data['league_avg'] / max_scale) * 10
        
        # Draw Year 1 bar
        rect1 = mpatches.Rectangle((0, y_base - bar_height/2), year1_width, bar_height,
                                   facecolor=year1_color, edgecolor='none', alpha=0.85)
        ax.add_patch(rect1)
        
        # Draw Year 2 bar
        rect2 = mpatches.Rectangle((0, y_base + bar_height/2), year2_width, bar_height,
                                   facecolor=year2_color, edgecolor='none', alpha=1.0)
        ax.add_patch(rect2)
        
        # Draw league average line
        ax.plot([league_avg_width, league_avg_width], 
               [y_base - bar_height*1.2, y_base + bar_height*1.2],
               color=league_avg_color, linestyle='--', linewidth=2, alpha=0.7)
        
        # Value labels on bars
        y1_label_x = year1_width + 0.1
        y2_label_x = year2_width + 0.1
        
        # Format values
        if data['unit'] == '%':
            y1_text = f"{data['year1']:.1f}%"
            y2_text = f"{data['year2']:.1f}%"
        elif data['unit'] == ' yds':
            y1_text = f"{data['year1']:.1f}"
            y2_text = f"{data['year2']:.1f}"
        else:
            y1_text = f"{data['year1']:.3f}"
            y2_text = f"{data['year2']:.3f}"
        
        # Year 1 value and rank
        ax.text(y1_label_x, y_base - bar_height/2, 
               f"{y1_text}  (#{data['rank_y1']})",
               va='center', fontsize=11, color='#2c3e50', fontweight='normal')
        
        # Year 2 value and rank
        ax.text(y2_label_x, y_base + bar_height/2, 
               f"{y2_text}  (#{data['rank_y2']})",
               va='center', fontsize=11, color='#2c3e50', fontweight='bold')
    
    # Set axis limits and labels
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.8, n_metrics * group_spacing - 0.2)
    
    # Y-axis labels (metric names)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(metric_names, fontsize=13, color='#2c3e50', fontweight='bold')
    
    # Remove x-axis
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Add subtle grid lines
    for y_pos in y_positions:
        ax.axhline(y_pos - group_spacing/2, color='#ecf0f1', linewidth=1, alpha=0.5, zorder=0)
    
    # Title and subtitle
    fig.text(0.5, 0.97, 'Year 1 Disaster to Year 2 Dominance: The Numbers',
            ha='center', fontsize=24, fontweight='bold', color='#2c3e50')
    fig.text(0.5, 0.94, 'Key Performance Metrics Comparison (2024 vs 2025)',
            ha='center', fontsize=16, color='#7f8c8d')
    
    # Legend
    legend_y = 0.91
    legend_x_start = 0.35
    
    # Year 1 box
    rect_y1 = mpatches.Rectangle((0.02, 0.02), 0.03, 0.015, transform=fig.transFigure,
                                facecolor=year1_color, edgecolor='none', alpha=0.85)
    fig.patches.append(rect_y1)
    fig.text(legend_x_start, legend_y, '■', fontsize=20, color=year1_color, alpha=0.85)
    fig.text(legend_x_start + 0.02, legend_y, 'Year 1 (2024)', fontsize=12, color='#2c3e50', va='center')
    
    # Year 2 box
    fig.text(legend_x_start + 0.15, legend_y, '■', fontsize=20, color=year2_color)
    fig.text(legend_x_start + 0.17, legend_y, 'Year 2 (2025)', fontsize=12, color='#2c3e50', va='center')
    
    # League average line
    fig.text(legend_x_start + 0.30, legend_y, '- - -', fontsize=14, color=league_avg_color)
    fig.text(legend_x_start + 0.335, legend_y, 'League Avg', fontsize=12, color='#2c3e50', va='center')
    
    # Summary box
    total_metrics = len(metrics)
    improved = sum(1 for m in metrics.values() if (m['year2'] > m['year1'] if m['higher_better'] else m['year2'] < m['year1']))
    above_avg = sum(1 for m in metrics.values() if (m['year2'] > m['league_avg'] if m['higher_better'] else m['year2'] < m['league_avg']))
    
    summary_text = f"Metrics Improved: {improved}/{total_metrics}\n"
    summary_text += f"Above League Average: {above_avg}/{total_metrics}"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='#bdc3c7', linewidth=1.5)
    fig.text(0.12, 0.88, summary_text, transform=fig.transFigure,
            fontsize=11, verticalalignment='top', bbox=props,
            color='#2c3e50', fontweight='normal', family='monospace')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.02, 1, 0.92])
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    print(f"\nComparison chart saved to: {output_path}")
    
    plt.close()

def main():
    """Main execution"""
    print("="*70)
    print("CALEB WILLIAMS KEY METRICS COMPARISON CHART")
    print("="*70)
    
    # Load data
    print("\nLoading data...")
    metrics = load_caleb_data()
    
    # Print summary
    print("\n" + "="*70)
    print("METRICS SUMMARY")
    print("="*70)
    
    for metric_name, data in metrics.items():
        delta = data['year2'] - data['year1']
        direction = "↑" if (delta > 0 and data['higher_better']) or (delta < 0 and not data['higher_better']) else "↓"
        
        print(f"\n{metric_name}:")
        print(f"  Year 1: {data['year1']:.2f}{data['unit']} (Rank #{data['rank_y1']})")
        print(f"  Year 2: {data['year2']:.2f}{data['unit']} (Rank #{data['rank_y2']})")
        print(f"  Change: {delta:+.2f}{data['unit']} {direction}")
        print(f"  League Avg: {data['league_avg']:.2f}{data['unit']}")
    
    # Create chart
    print("\n" + "="*70)
    print("GENERATING VISUALIZATION")
    print("="*70)
    
    create_comparison_chart(metrics)
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
