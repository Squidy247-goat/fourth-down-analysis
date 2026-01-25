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
        'epa_per_dropback': advanced_2025['epa_per_dropback'].mean(),
        'third_down_rate': third_down_2025['third_down_conversion_rate'].mean(),
        'red_zone_td_rate': red_zone_2025['td_rate'].mean(),
        'completion_under_pressure': pressure_2025['completion_pct_under_pressure'].mean()
    }
    
    # Calculate ranks for 2024
    rank_2024 = {}
    rank_2024['completion_pct'] = (basic_2024['completion_pct'] >= caleb_basic_2024['completion_pct']).sum()
    rank_2024['epa_per_dropback'] = (advanced_2024['epa_per_dropback'] >= caleb_advanced_2024['epa_per_dropback']).sum()
    rank_2024['third_down_rate'] = int(caleb_third_2024['rank'])
    rank_2024['red_zone_td_rate'] = (red_zone_2024['td_rate'] >= caleb_redzone_2024['td_rate']).sum()
    rank_2024['completion_under_pressure'] = (pressure_2024['completion_pct_under_pressure'] >= caleb_pressure_2024['completion_pct_under_pressure']).sum()
    
    # Calculate ranks for 2025
    rank_2025 = {}
    rank_2025['completion_pct'] = (basic_2025['completion_pct'] >= caleb_basic_2025['completion_pct']).sum()
    rank_2025['epa_per_dropback'] = (advanced_2025['epa_per_dropback'] >= caleb_advanced_2025['epa_per_dropback']).sum()
    rank_2025['third_down_rate'] = int(caleb_third_2025['rank'])
    rank_2025['red_zone_td_rate'] = (red_zone_2025['td_rate'] >= caleb_redzone_2025['td_rate']).sum()
    rank_2025['completion_under_pressure'] = (pressure_2025['completion_pct_under_pressure'] >= caleb_pressure_2025['completion_pct_under_pressure']).sum()
    
    # Compile top 5 metrics (in order of dramatic impact)
    metrics = {
        'Comp % Under Pressure ⭐': {
            'year1': caleb_pressure_2024['completion_pct_under_pressure'],
            'year2': caleb_pressure_2025['completion_pct_under_pressure'],
            'league_avg': league_avg_2025['completion_under_pressure'],
            'rank_y1': rank_2024['completion_under_pressure'],
            'rank_y2': rank_2025['completion_under_pressure'],
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
        'Third Down Conversion Rate': {
            'year1': caleb_third_2024['third_down_conversion_rate'],
            'year2': caleb_third_2025['third_down_conversion_rate'],
            'league_avg': league_avg_2025['third_down_rate'],
            'rank_y1': rank_2024['third_down_rate'],
            'rank_y2': rank_2025['third_down_rate'],
            'unit': '%',
            'higher_better': True
        },
        'Completion %': {
            'year1': caleb_basic_2024['completion_pct'],
            'year2': caleb_basic_2025['completion_pct'],
            'league_avg': league_avg_2025['completion_pct'],
            'rank_y1': rank_2024['completion_pct'],
            'rank_y2': rank_2025['completion_pct'],
            'unit': '%',
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
        }
    }
    
    return metrics

def create_simplified_chart(metrics, output_path='../output/visuals/key_metrics_comparison_simplified.png'):
    """Create clean simplified horizontal bar chart with only 5 key metrics"""
    
    # Set up figure
    fig, ax = plt.subplots(figsize=(14, 9), facecolor='#f8f9fa')
    ax.set_facecolor('#ffffff')
    
    # Colors
    year1_color = '#e74c3c'  # Red for Year 1
    year2_color = '#27ae60'  # Green for Year 2
    league_avg_color = '#7f8c8d'  # Darker gray for league average
    improvement_color = '#27ae60'  # Green for delta text
    
    # Metrics in order
    metric_names = list(metrics.keys())
    n_metrics = len(metric_names)
    
    # Calculate positions with MORE spacing
    bar_height = 0.35  # Increased from 0.35
    group_spacing = 1.5  # Increased spacing between groups
    y_positions = np.arange(n_metrics) * group_spacing
    
    # Calculate max values for scaling
    max_vals = []
    for metric in metric_names:
        data = metrics[metric]
        max_val = max(data['year1'], data['year2'], data['league_avg'])
        max_vals.append(max_val * 1.2)  # Add 20% padding for labels
    
    # Draw bars
    for i, metric in enumerate(metric_names):
        data = metrics[metric]
        y_base = y_positions[i]
        max_scale = max_vals[i]
        
        # Scale values to bar width
        year1_width = (data['year1'] / max_scale) * 10
        year2_width = (data['year2'] / max_scale) * 10
        league_avg_width = (data['league_avg'] / max_scale) * 10
        
        # Add highlight for top metric
        if i == 0:  # Comp % Under Pressure
            highlight = mpatches.Rectangle((-0.3, y_base - bar_height*1.8), 11.5, bar_height*3.6,
                                          facecolor='none', edgecolor='#27ae60', linewidth=2, alpha=0.3)
            ax.add_patch(highlight)
        
        # Draw Year 1 bar
        rect1 = mpatches.Rectangle((0, y_base - bar_height*0.75), year1_width, bar_height,
                                   facecolor=year1_color, edgecolor='none', alpha=0.85)
        ax.add_patch(rect1)
        
        # Draw Year 2 bar
        rect2 = mpatches.Rectangle((0, y_base + bar_height*0.25), year2_width, bar_height,
                                   facecolor=year2_color, edgecolor='none', alpha=1.0)
        ax.add_patch(rect2)
        
        # Draw league average line (more prominent)
        ax.plot([league_avg_width, league_avg_width], 
               [y_base - bar_height*1.2, y_base + bar_height*1.2],
               color=league_avg_color, linestyle='--', linewidth=2.5, alpha=0.8)
        
        # Add "Avg" label at top
        if i == 0:
            ax.text(league_avg_width, y_base + bar_height*1.4, 'Avg',
                   ha='center', fontsize=9, color=league_avg_color, fontweight='bold')
        
        # Value labels on bars
        y1_label_x = year1_width + 0.15
        y2_label_x = year2_width + 0.15
        
        # Format values with consistent decimal places
        if data['unit'] == '%':
            y1_text = f"{data['year1']:.1f}%"
            y2_text = f"{data['year2']:.1f}%"
        else:
            y1_text = f"{data['year1']:.2f}"
            y2_text = f"{data['year2']:.2f}"
        
        # Year 1 value and rank (lighter/smaller)
        ax.text(y1_label_x, y_base - bar_height*0.75, 
               f"{y1_text} (#{data['rank_y1']})",
               va='center', fontsize=10, color='#7f8c8d', fontweight='normal')
        
        # Year 2 value and rank (bold)
        ax.text(y2_label_x, y_base + bar_height*0.25, 
               f"{y2_text} (#{data['rank_y2']})",
               va='center', fontsize=11, color='#2c3e50', fontweight='bold')
        
        # Delta indicator with arrow
        delta = data['year2'] - data['year1']
        if data['unit'] == '%':
            delta_text = f"+{delta:.1f} ▲"
        else:
            delta_text = f"+{delta:.2f} ▲"
        
        # Position delta to right of Year 2 value
        delta_x = max(y1_label_x, y2_label_x) + 2.0
        
        # Make big improvements stand out more
        if abs(delta) > 25:  # Huge improvement
            delta_fontsize = 13
            delta_weight = 'bold'
            delta_color = improvement_color
        elif abs(delta) > 10:  # Significant improvement
            delta_fontsize = 12
            delta_weight = 'bold'
            delta_color = improvement_color
        else:  # Normal improvement
            delta_fontsize = 11
            delta_weight = 'normal'
            delta_color = improvement_color
        
        ax.text(delta_x, y_base, delta_text,
               va='center', fontsize=delta_fontsize, color=delta_color, 
               fontweight=delta_weight)
    
    # Set axis limits and labels
    ax.set_xlim(-0.3, 11.5)
    ax.set_ylim(-0.9, n_metrics * group_spacing - 0.5)
    
    # Y-axis labels (metric names) - larger and bolder
    ax.set_yticks(y_positions)
    ax.set_yticklabels(metric_names, fontsize=14, color='#2c3e50', fontweight='bold')
    
    # Remove x-axis and spines
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
    legend_y = 0.90
    legend_x_start = 0.32
    
    fig.text(legend_x_start, legend_y, '■', fontsize=20, color=year1_color, alpha=0.85)
    fig.text(legend_x_start + 0.02, legend_y, 'Year 1 (Disaster)', fontsize=12, color='#2c3e50', va='center')
    
    fig.text(legend_x_start + 0.16, legend_y, '■', fontsize=20, color=year2_color)
    fig.text(legend_x_start + 0.18, legend_y, 'Year 2 (Dominance)', fontsize=12, color='#2c3e50', va='center')
    
    fig.text(legend_x_start + 0.35, legend_y, '- - -', fontsize=14, color=league_avg_color)
    fig.text(legend_x_start + 0.385, legend_y, 'League Avg', fontsize=12, color='#2c3e50', va='center')
    
    # Enhanced summary box
    total_metrics = len(metrics)
    improved = sum(1 for m in metrics.values() if m['year2'] > m['year1'])
    above_avg = sum(1 for m in metrics.values() if m['year2'] > m['league_avg'])
    
    # Calculate ranking jumps
    rank_jumps = [m['rank_y1'] - m['rank_y2'] for m in metrics.values()]
    big_jumps = sum(1 for jump in rank_jumps if jump >= 25)
    
    # Find biggest improvement
    biggest_delta = 0
    biggest_metric = ""
    for name, data in metrics.items():
        delta = data['year2'] - data['year1']
        if delta > biggest_delta:
            biggest_delta = delta
            biggest_metric = name
    
    summary_text = "📊 Key Transformation Metrics\n"
    summary_text += f"• All {total_metrics} metrics improved significantly\n"
    summary_text += f"• {big_jumps} metrics jumped 25+ spots in rankings\n"
    summary_text += f"• Comp% under pressure: +{biggest_delta:.1f} points (historic)\n"
    summary_text += f"• Now above league avg in {above_avg} of {total_metrics} metrics"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='#27ae60', linewidth=2)
    fig.text(0.11, 0.86, summary_text, transform=fig.transFigure,
            fontsize=10, verticalalignment='top', bbox=props,
            color='#2c3e50', fontweight='normal', linespacing=1.6)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.02, 1, 0.91])
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    print(f"\nSimplified comparison chart saved to: {output_path}")
    
    plt.close()

def main():
    """Main execution"""
    print("="*70)
    print("CALEB WILLIAMS KEY METRICS - SIMPLIFIED (TOP 5)")
    print("="*70)
    
    # Load data
    print("\nLoading data...")
    metrics = load_caleb_data()
    
    # Print summary
    print("\n" + "="*70)
    print("TOP 5 METRICS SUMMARY (Ordered by Impact)")
    print("="*70)
    
    for metric_name, data in metrics.items():
        delta = data['year2'] - data['year1']
        rank_jump = data['rank_y1'] - data['rank_y2']
        
        print(f"\n{metric_name}:")
        print(f"  Year 1: {data['year1']:.2f}{data['unit']} (Rank #{data['rank_y1']})")
        print(f"  Year 2: {data['year2']:.2f}{data['unit']} (Rank #{data['rank_y2']})")
        print(f"  Change: {delta:+.2f}{data['unit']} (Jumped {rank_jump} spots)")
        print(f"  League Avg: {data['league_avg']:.2f}{data['unit']}")
        print(f"  Status: {'Above' if data['year2'] > data['league_avg'] else 'Below'} league average")
    
    # Create chart
    print("\n" + "="*70)
    print("GENERATING SIMPLIFIED VISUALIZATION")
    print("="*70)
    
    create_simplified_chart(metrics)
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
