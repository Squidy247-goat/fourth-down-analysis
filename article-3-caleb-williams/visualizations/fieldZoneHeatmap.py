import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

def load_season_data(year):
    """Load play-by-play data for a specific season"""
    file_path = f'../data/play_by_play_{year}.csv'
    try:
        df = pd.read_csv(file_path, low_memory=False)
        print(f"Loaded {year} season data: {len(df)} plays")
        return df
    except Exception as e:
        print(f"Error loading {year} data: {e}")
        return None

def categorize_field_zone(row):
    """
    Categorize each pass into a field zone based on:
    - Vertical: air_yards (deep 20+, intermediate 10-20, short 0-10, behind LOS <0)
    - Horizontal: pass_location (left, middle, right)
    """
    air_yards = row['air_yards']
    pass_location = row['pass_location']
    
    # Vertical zone
    if pd.isna(air_yards):
        return None, None
    
    if air_yards < 0:
        vertical = 'Behind LOS'
    elif 0 <= air_yards < 10:
        vertical = 'Short (0-10)'
    elif 10 <= air_yards < 20:
        vertical = 'Intermediate (10-20)'
    else:  # air_yards >= 20
        vertical = 'Deep (20+)'
    
    # Horizontal zone
    if pd.isna(pass_location) or pass_location not in ['left', 'middle', 'right']:
        return None, None
    
    horizontal_map = {
        'left': 'Left',
        'middle': 'Center',
        'right': 'Right'
    }
    horizontal = horizontal_map.get(pass_location)
    
    return vertical, horizontal

def calculate_zone_stats(df, qb_name='C.Williams'):
    """
    Calculate completion percentage and attempt counts for each field zone
    """
    # Filter for QB's pass attempts (complete or incomplete, exclude spikes)
    qb_passes = df[
        (df['passer_player_name'] == qb_name) &
        ((df['complete_pass'] == 1) | (df['incomplete_pass'] == 1)) &
        (df['qb_spike'] != 1)
    ].copy()
    
    print(f"\nTotal pass attempts by {qb_name}: {len(qb_passes)}")
    
    # Categorize each pass into zones
    qb_passes[['vertical_zone', 'horizontal_zone']] = qb_passes.apply(
        categorize_field_zone, axis=1, result_type='expand'
    )
    
    # Remove passes without zone data
    qb_passes = qb_passes.dropna(subset=['vertical_zone', 'horizontal_zone'])
    
    print(f"Pass attempts with zone data: {len(qb_passes)}")
    
    # Define zone order for proper grid layout
    vertical_order = ['Deep (20+)', 'Intermediate (10-20)', 'Short (0-10)', 'Behind LOS']
    horizontal_order = ['Left', 'Center', 'Right']
    
    # Initialize results dictionary
    zone_stats = {}
    
    for vertical in vertical_order:
        for horizontal in horizontal_order:
            zone_key = f"{vertical}_{horizontal}"
            
            # Filter for this specific zone
            zone_passes = qb_passes[
                (qb_passes['vertical_zone'] == vertical) &
                (qb_passes['horizontal_zone'] == horizontal)
            ]
            
            attempts = len(zone_passes)
            completions = zone_passes['complete_pass'].sum()
            completion_pct = (completions / attempts * 100) if attempts > 0 else np.nan
            
            zone_stats[zone_key] = {
                'vertical': vertical,
                'horizontal': horizontal,
                'attempts': attempts,
                'completions': int(completions),
                'completion_pct': completion_pct
            }
    
    return zone_stats

def create_heatmap(zone_stats, qb_name='Caleb Williams', season=2024, output_path='../output/visualizations/field_zone_heatmap.png'):
    """
    Create a professional football field heatmap showing completion percentage by zone
    """
    # Define zone layout
    vertical_zones = ['Deep (20+)', 'Intermediate (10-20)', 'Short (0-10)', 'Behind LOS']
    horizontal_zones = ['Left', 'Center', 'Right']
    
    # Create grid for heatmap (4 rows x 3 columns)
    grid_data = np.zeros((4, 3))
    attempts_data = np.zeros((4, 3))
    completions_data = np.zeros((4, 3))
    
    # Fill grid with completion percentages
    for i, vertical in enumerate(vertical_zones):
        for j, horizontal in enumerate(horizontal_zones):
            zone_key = f"{vertical}_{horizontal}"
            stats = zone_stats[zone_key]
            
            grid_data[i, j] = stats['completion_pct']
            attempts_data[i, j] = stats['attempts']
            completions_data[i, j] = stats['completions']
    
    # Create figure with specific dimensions
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#f8f9fa')
    ax.set_facecolor('#ffffff')
    
    # Create custom colormap (red -> yellow -> green)
    colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('completion', colors, N=n_bins)
    
    # Create masked array for zones with insufficient data (< 5 attempts)
    masked_data = np.ma.masked_where(attempts_data < 5, grid_data)
    
    # Create heatmap
    im = ax.imshow(masked_data, cmap=cmap, aspect='auto', vmin=0, vmax=100,
                   interpolation='nearest', alpha=0.9)
    
    # Add grid lines (white borders between cells)
    ax.set_xticks(np.arange(3) - 0.5, minor=True)
    ax.set_yticks(np.arange(4) - 0.5, minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=3)
    
    # Set tick positions and labels
    ax.set_xticks(np.arange(3))
    ax.set_yticks(np.arange(4))
    ax.set_xticklabels(horizontal_zones, fontsize=12, fontweight='normal', color='#2c3e50')
    ax.set_yticklabels(vertical_zones, fontsize=12, fontweight='normal', color='#2c3e50')
    
    # Add text annotations to each cell
    for i in range(4):
        for j in range(3):
            attempts = int(attempts_data[i, j])
            completions = int(completions_data[i, j])
            completion_pct = grid_data[i, j]
            
            if attempts < 5:
                # Insufficient data
                text_color = '#7f8c8d'
                ax.text(j, i, 'No Data\n(< 5 att)', 
                       ha='center', va='center', fontsize=11, 
                       color=text_color, fontweight='normal')
            else:
                # Determine text color based on background
                text_color = 'white' if completion_pct < 70 else 'white'
                
                # Main percentage text
                ax.text(j, i - 0.15, f'{completion_pct:.1f}%', 
                       ha='center', va='center', fontsize=16, 
                       color=text_color, fontweight='bold')
                
                # Attempt count text
                ax.text(j, i + 0.20, f'{completions}/{attempts} att', 
                       ha='center', va='center', fontsize=9, 
                       color=text_color, fontweight='normal', alpha=0.9)
    
    # Add title and subtitle
    title_text = f'{qb_name} Year 1: Completion % by Field Zone'
    subtitle_text = f'{season} Regular Season (Min. 5 attempts per zone)'
    
    fig.text(0.5, 0.96, title_text, ha='center', fontsize=20, 
            fontweight='bold', color='#2c3e50')
    fig.text(0.5, 0.92, subtitle_text, ha='center', fontsize=14, 
            color='#7f8c8d')
    
    # Add colorbar legend at bottom
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.03])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Completion Percentage', fontsize=12, color='#2c3e50', fontweight='normal')
    cbar.ax.tick_params(labelsize=10, colors='#2c3e50')
    
    # Add threshold markers on colorbar
    cbar.ax.axvline(40, color='white', linewidth=2, alpha=0.7)
    cbar.ax.axvline(60, color='white', linewidth=2, alpha=0.7)
    
    # Add field context annotation (yard markers on left side)
    field_context_x = -0.7
    for i, zone in enumerate(vertical_zones):
        if 'Deep' in zone:
            yards = '20+ yds'
        elif 'Intermediate' in zone:
            yards = '10-20 yds'
        elif 'Short' in zone:
            yards = '0-10 yds'
        else:
            yards = '< 0 yds'
        
        ax.text(field_context_x, i, yards, ha='right', va='center', 
               fontsize=10, color='#7f8c8d', style='italic')
    
    # Add context box in top-right corner
    overall_attempts = int(attempts_data.sum())
    overall_completions = int(completions_data.sum())
    overall_comp_pct = (overall_completions / overall_attempts * 100) if overall_attempts > 0 else 0
    
    # Find most and least accurate zones (min 5 attempts)
    valid_zones = []
    for i in range(4):
        for j in range(3):
            if attempts_data[i, j] >= 5:
                valid_zones.append({
                    'zone': f"{vertical_zones[i].split('(')[0].strip()} {horizontal_zones[j]}",
                    'pct': grid_data[i, j]
                })
    
    if valid_zones:
        best_zone = max(valid_zones, key=lambda x: x['pct'])
        worst_zone = min(valid_zones, key=lambda x: x['pct'])
        
        context_text = f"Overall: {overall_comp_pct:.1f}% ({overall_completions}/{overall_attempts})\n"
        context_text += f"Best: {best_zone['zone']} ({best_zone['pct']:.1f}%)\n"
        context_text += f"Worst: {worst_zone['zone']} ({worst_zone['pct']:.1f}%)"
        
        # Add text box
        props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#e0e0e0', linewidth=1.5)
        ax.text(0.98, 0.98, context_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right', bbox=props,
               color='#2c3e50', family='monospace')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.12, 1, 0.90])
    
    # Add subtle drop shadow effect using figure border
    fig.patch.set_edgecolor('#d0d0d0')
    fig.patch.set_linewidth(2)
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    print(f"\nHeatmap saved to: {output_path}")
    
    # Also save as SVG for web
    svg_path = output_path.replace('.png', '.svg')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#f8f9fa')
    print(f"SVG version saved to: {svg_path}")
    
    plt.close()

def export_zone_data_csv(zone_stats, output_path='../output/field_zone_completion_data_2024.csv'):
    """Export zone statistics to CSV for reference"""
    data = []
    for zone_key, stats in zone_stats.items():
        data.append({
            'zone': f"{stats['vertical']} - {stats['horizontal']}",
            'vertical_zone': stats['vertical'],
            'horizontal_zone': stats['horizontal'],
            'attempts': stats['attempts'],
            'completions': stats['completions'],
            'completion_pct': round(stats['completion_pct'], 1) if not np.isnan(stats['completion_pct']) else 'N/A'
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values(['vertical_zone', 'horizontal_zone'])
    df.to_csv(output_path, index=False)
    print(f"Zone data exported to: {output_path}")

def main():
    """Main execution function"""
    print("="*70)
    print("CALEB WILLIAMS FIELD ZONE COMPLETION % HEATMAP")
    print("="*70)
    
    # Load 2024 season data
    df_2024 = load_season_data(2024)
    
    if df_2024 is None:
        print("Error: Could not load 2024 season data")
        return
    
    # Calculate zone statistics
    zone_stats = calculate_zone_stats(df_2024, qb_name='C.Williams')
    
    # Print zone breakdown
    print("\n" + "="*70)
    print("FIELD ZONE COMPLETION BREAKDOWN")
    print("="*70)
    
    vertical_zones = ['Deep (20+)', 'Intermediate (10-20)', 'Short (0-10)', 'Behind LOS']
    horizontal_zones = ['Left', 'Center', 'Right']
    
    for vertical in vertical_zones:
        print(f"\n{vertical}:")
        print("-" * 50)
        for horizontal in horizontal_zones:
            zone_key = f"{vertical}_{horizontal}"
            stats = zone_stats[zone_key]
            
            if stats['attempts'] >= 5:
                print(f"  {horizontal:8} | {stats['completion_pct']:5.1f}% ({stats['completions']}/{stats['attempts']} att)")
            else:
                print(f"  {horizontal:8} | No Data (< 5 attempts)")
    
    # Create heatmap visualization
    print("\n" + "="*70)
    print("GENERATING HEATMAP VISUALIZATION")
    print("="*70)
    
    create_heatmap(zone_stats, qb_name='Caleb Williams', season=2024)
    
    # Export data to CSV
    export_zone_data_csv(zone_stats)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
