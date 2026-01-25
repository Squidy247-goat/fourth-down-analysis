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

def create_comparison_heatmap(zone_stats_2024, zone_stats_2025, qb_name='Caleb Williams', 
                              output_path='../output/visuals/field_zone_comparison_heatmap.png'):
    """
    Create side-by-side comparison heatmap showing Year 1 vs Year 2
    """
    # Define zone layout
    vertical_zones = ['Deep (20+)', 'Intermediate (10-20)', 'Short (0-10)', 'Behind LOS']
    horizontal_zones = ['Left', 'Center', 'Right']
    
    # Create grids for both years (4 rows x 3 columns)
    grid_2024 = np.zeros((4, 3))
    grid_2025 = np.zeros((4, 3))
    attempts_2024 = np.zeros((4, 3))
    attempts_2025 = np.zeros((4, 3))
    completions_2024 = np.zeros((4, 3))
    completions_2025 = np.zeros((4, 3))
    delta_grid = np.zeros((4, 3))
    
    # Fill grids with completion percentages
    for i, vertical in enumerate(vertical_zones):
        for j, horizontal in enumerate(horizontal_zones):
            zone_key = f"{vertical}_{horizontal}"
            
            stats_2024 = zone_stats_2024[zone_key]
            stats_2025 = zone_stats_2025[zone_key]
            
            grid_2024[i, j] = stats_2024['completion_pct']
            grid_2025[i, j] = stats_2025['completion_pct']
            attempts_2024[i, j] = stats_2024['attempts']
            attempts_2025[i, j] = stats_2025['attempts']
            completions_2024[i, j] = stats_2024['completions']
            completions_2025[i, j] = stats_2025['completions']
            
            # Calculate delta (improvement)
            if not np.isnan(grid_2024[i, j]) and not np.isnan(grid_2025[i, j]):
                delta_grid[i, j] = grid_2025[i, j] - grid_2024[i, j]
            else:
                delta_grid[i, j] = np.nan
    
    # Create figure with side-by-side layout (wider for comparison)
    fig = plt.figure(figsize=(20, 7), facecolor='#f8f9fa')
    
    # Create custom colormap (red -> yellow -> green)
    colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('completion', colors, N=n_bins)
    
    # Main title
    fig.text(0.5, 0.96, 'The Transformation: Year 1 vs Year 2 Completion % by Field Zone', 
            ha='center', fontsize=24, fontweight='bold', color='#2c3e50')
    
    # Year 1 (2024) Heatmap - Left side
    ax1 = plt.subplot(1, 2, 1)
    ax1.set_facecolor('#ffffff')
    
    masked_data_2024 = np.ma.masked_where(attempts_2024 < 5, grid_2024)
    im1 = ax1.imshow(masked_data_2024, cmap=cmap, aspect='auto', vmin=0, vmax=100,
                     interpolation='nearest', alpha=0.9)
    
    # Grid lines
    ax1.set_xticks(np.arange(3) - 0.5, minor=True)
    ax1.set_yticks(np.arange(4) - 0.5, minor=True)
    ax1.grid(which='minor', color='white', linestyle='-', linewidth=3)
    
    # Labels
    ax1.set_xticks(np.arange(3))
    ax1.set_yticks(np.arange(4))
    ax1.set_xticklabels(horizontal_zones, fontsize=12, color='#2c3e50')
    ax1.set_yticklabels(vertical_zones, fontsize=12, color='#2c3e50')
    ax1.set_title('Year 1 (2024)', fontsize=16, fontweight='bold', color='#2c3e50', pad=10)
    
    # Annotations for Year 1
    for i in range(4):
        for j in range(3):
            attempts = int(attempts_2024[i, j])
            completions = int(completions_2024[i, j])
            completion_pct = grid_2024[i, j]
            
            if attempts < 5:
                text_color = '#7f8c8d'
                ax1.text(j, i, 'No Data\n(< 5 att)', 
                        ha='center', va='center', fontsize=10, 
                        color=text_color, fontweight='normal')
            else:
                text_color = 'white'
                ax1.text(j, i - 0.15, f'{completion_pct:.1f}%', 
                        ha='center', va='center', fontsize=14, 
                        color=text_color, fontweight='bold')
                ax1.text(j, i + 0.20, f'{completions}/{attempts} att', 
                        ha='center', va='center', fontsize=8, 
                        color=text_color, fontweight='normal', alpha=0.9)
    
    # Year 2 (2025) Heatmap - Right side
    ax2 = plt.subplot(1, 2, 2)
    ax2.set_facecolor('#ffffff')
    
    masked_data_2025 = np.ma.masked_where(attempts_2025 < 5, grid_2025)
    im2 = ax2.imshow(masked_data_2025, cmap=cmap, aspect='auto', vmin=0, vmax=100,
                     interpolation='nearest', alpha=0.9)
    
    # Grid lines
    ax2.set_xticks(np.arange(3) - 0.5, minor=True)
    ax2.set_yticks(np.arange(4) - 0.5, minor=True)
    ax2.grid(which='minor', color='white', linestyle='-', linewidth=3)
    
    # Labels
    ax2.set_xticks(np.arange(3))
    ax2.set_yticks(np.arange(4))
    ax2.set_xticklabels(horizontal_zones, fontsize=12, color='#2c3e50')
    ax2.set_yticklabels(vertical_zones, fontsize=12, color='#2c3e50')
    ax2.set_title('Year 2 (2025)', fontsize=16, fontweight='bold', color='#2c3e50', pad=10)
    
    # Annotations for Year 2 with delta indicators
    for i in range(4):
        for j in range(3):
            attempts = int(attempts_2025[i, j])
            completions = int(completions_2025[i, j])
            completion_pct = grid_2025[i, j]
            delta = delta_grid[i, j]
            
            if attempts < 5:
                text_color = '#7f8c8d'
                ax2.text(j, i, 'No Data\n(< 5 att)', 
                        ha='center', va='center', fontsize=10, 
                        color=text_color, fontweight='normal')
            else:
                text_color = 'white'
                ax2.text(j, i - 0.25, f'{completion_pct:.1f}%', 
                        ha='center', va='center', fontsize=14, 
                        color=text_color, fontweight='bold')
                ax2.text(j, i + 0.05, f'{completions}/{attempts} att', 
                        ha='center', va='center', fontsize=8, 
                        color=text_color, fontweight='normal', alpha=0.9)
                
                # Add delta indicator
                if not np.isnan(delta):
                    if delta > 0:
                        delta_text = f'+{delta:.1f} ▲'
                        delta_color = '#27ae60' if completion_pct < 70 else 'white'
                    elif delta < 0:
                        delta_text = f'{delta:.1f} ▼'
                        delta_color = '#e74c3c' if completion_pct < 70 else 'white'
                    else:
                        delta_text = '—'
                        delta_color = text_color
                    
                    ax2.text(j, i + 0.32, delta_text, 
                            ha='center', va='center', fontsize=9, 
                            color=delta_color, fontweight='bold', alpha=0.95)
                    
                    # Add improvement badge for 15+ point improvements
                    if delta >= 15:
                        circle = plt.Circle((j, i - 0.42), 0.12, color='#27ae60', 
                                          transform=ax2.transData, zorder=10, alpha=0.9)
                        ax2.add_patch(circle)
                        ax2.text(j, i - 0.42, f'+{delta:.0f}', 
                                ha='center', va='center', fontsize=7, 
                                color='white', fontweight='bold', zorder=11)
    
    # Add colorbar at bottom (shared)
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.02])
    cbar = fig.colorbar(im2, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Completion Percentage', fontsize=12, color='#2c3e50', fontweight='normal')
    cbar.ax.tick_params(labelsize=10, colors='#2c3e50')
    cbar.ax.axvline(40, color='white', linewidth=2, alpha=0.7)
    cbar.ax.axvline(60, color='white', linewidth=2, alpha=0.7)
    
    # Calculate overall stats
    overall_attempts_2024 = int(attempts_2024.sum())
    overall_completions_2024 = int(completions_2024.sum())
    overall_comp_pct_2024 = (overall_completions_2024 / overall_attempts_2024 * 100) if overall_attempts_2024 > 0 else 0
    
    overall_attempts_2025 = int(attempts_2025.sum())
    overall_completions_2025 = int(completions_2025.sum())
    overall_comp_pct_2025 = (overall_completions_2025 / overall_attempts_2025 * 100) if overall_attempts_2025 > 0 else 0
    
    overall_improvement = overall_comp_pct_2025 - overall_comp_pct_2024
    
    # Find most improved zone
    max_improvement = np.nanmax(delta_grid)
    max_idx = np.unravel_index(np.nanargmax(delta_grid), delta_grid.shape)
    most_improved_zone = f"{vertical_zones[max_idx[0]].split('(')[0].strip()} {horizontal_zones[max_idx[1]]}"
    
    # Add improvement summary box
    summary_text = f"Overall Improvement: {overall_comp_pct_2024:.1f}% → {overall_comp_pct_2025:.1f}% (+{overall_improvement:.1f})\n"
    summary_text += f"Most Improved: {most_improved_zone} (+{max_improvement:.1f})\n"
    summary_text += f"2025 Total: {overall_completions_2025}/{overall_attempts_2025} attempts"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='#27ae60', linewidth=2.5)
    fig.text(0.98, 0.90, summary_text, transform=fig.transFigure, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props,
            color='#2c3e50', family='monospace', fontweight='normal')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.12, 1, 0.92])
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    print(f"\nComparison heatmap saved to: {output_path}")
    
    plt.close()

def create_single_year2_heatmap(zone_stats_2025, qb_name='Caleb Williams', 
                                output_path='../output/visuals/field_zone_heatmap_2025.png'):
    """
    Create standalone Year 2 heatmap
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
            stats = zone_stats_2025[zone_key]
            
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
                text_color = 'white'
                
                # Main percentage text
                ax.text(j, i - 0.15, f'{completion_pct:.1f}%', 
                       ha='center', va='center', fontsize=16, 
                       color=text_color, fontweight='bold')
                
                # Attempt count text
                ax.text(j, i + 0.20, f'{completions}/{attempts} att', 
                       ha='center', va='center', fontsize=9, 
                       color=text_color, fontweight='normal', alpha=0.9)
    
    # Add title and subtitle
    title_text = f'{qb_name} Year 2: Completion % by Field Zone'
    subtitle_text = '2025 Regular Season & Playoffs (Min. 5 attempts per zone)'
    
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
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.12, 1, 0.90])
    
    # Add subtle drop shadow effect using figure border
    fig.patch.set_edgecolor('#d0d0d0')
    fig.patch.set_linewidth(2)
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    print(f"\nYear 2 heatmap saved to: {output_path}")
    
    plt.close()

def print_comparison_summary(zone_stats_2024, zone_stats_2025):
    """Print detailed comparison summary"""
    print("\n" + "="*70)
    print("YEAR 1 VS YEAR 2 COMPARISON - FIELD ZONE BREAKDOWN")
    print("="*70)
    
    vertical_zones = ['Deep (20+)', 'Intermediate (10-20)', 'Short (0-10)', 'Behind LOS']
    horizontal_zones = ['Left', 'Center', 'Right']
    
    for vertical in vertical_zones:
        print(f"\n{vertical}:")
        print("-" * 70)
        for horizontal in horizontal_zones:
            zone_key = f"{vertical}_{horizontal}"
            stats_2024 = zone_stats_2024[zone_key]
            stats_2025 = zone_stats_2025[zone_key]
            
            if stats_2024['attempts'] >= 5 and stats_2025['attempts'] >= 5:
                delta = stats_2025['completion_pct'] - stats_2024['completion_pct']
                arrow = '▲' if delta > 0 else '▼' if delta < 0 else '—'
                print(f"  {horizontal:8} | 2024: {stats_2024['completion_pct']:5.1f}% → 2025: {stats_2025['completion_pct']:5.1f}% ({delta:+6.1f} {arrow})")
            elif stats_2025['attempts'] >= 5:
                print(f"  {horizontal:8} | 2024: No Data → 2025: {stats_2025['completion_pct']:5.1f}%")
            elif stats_2024['attempts'] >= 5:
                print(f"  {horizontal:8} | 2024: {stats_2024['completion_pct']:5.1f}% → 2025: No Data")
            else:
                print(f"  {horizontal:8} | Insufficient data in both years")

def main():
    """Main execution function"""
    print("="*70)
    print("CALEB WILLIAMS YEAR 1 VS YEAR 2 FIELD ZONE COMPARISON")
    print("="*70)
    
    # Load data for both seasons
    df_2024 = load_season_data(2024)
    df_2025 = load_season_data(2025)
    
    if df_2024 is None or df_2025 is None:
        print("Error: Could not load season data")
        return
    
    # Calculate zone statistics for both years
    print("\n" + "="*70)
    print("CALCULATING YEAR 1 (2024) STATISTICS")
    print("="*70)
    zone_stats_2024 = calculate_zone_stats(df_2024, qb_name='C.Williams')
    
    print("\n" + "="*70)
    print("CALCULATING YEAR 2 (2025) STATISTICS")
    print("="*70)
    zone_stats_2025 = calculate_zone_stats(df_2025, qb_name='C.Williams')
    
    # Print comparison summary
    print_comparison_summary(zone_stats_2024, zone_stats_2025)
    
    # Create visualizations
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    # 1. Side-by-side comparison (primary visualization)
    create_comparison_heatmap(zone_stats_2024, zone_stats_2025, qb_name='Caleb Williams')
    
    # 2. Standalone Year 2 heatmap
    create_single_year2_heatmap(zone_stats_2025, qb_name='Caleb Williams')
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
