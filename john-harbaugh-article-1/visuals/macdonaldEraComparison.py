"""
makes charts comparing defense before/during/after macdonald
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def analyze_macdonald_era(year):
    """get defense numbers for one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        return None
    
    # just regular season games where ravens were on defense
    df = df[df['season_type'] == 'REG'].copy()
    ravens_defense = df[df['defteam'] == 'BAL'].copy()
    
    if len(ravens_defense) == 0:
        return None
    
    # defense EPA number
    defensive_epa = ravens_defense['epa'].mean()
    
    # how many plays
    total_plays = len(ravens_defense)
    
    # figure out how many points they gave up
    games = df['game_id'].unique()
    total_points_allowed = 0
    
    for game_id in games:
        game_df = df[df['game_id'] == game_id].copy()
        if len(game_df) > 0:
            final_play = game_df.iloc[-1]
            home_team = game_df['home_team'].iloc[0]
            is_ravens_home = (home_team == 'BAL')
            
            if is_ravens_home:
                points_allowed = final_play['total_away_score']
            else:
                points_allowed = final_play['total_home_score']
            
            total_points_allowed += points_allowed
    
    ppg_allowed = total_points_allowed / len(games) if len(games) > 0 else 0
    
    return {
        'year': year,
        'defensive_epa': defensive_epa,
        'plays': total_plays,
        'games': len(games),
        'ppg_allowed': ppg_allowed,
        'total_points_allowed': total_points_allowed
    }


def create_macdonald_comparison():
    """make the comparison charts"""
    
    # split up the years into 3 groups
    pre_macdonald = [2019, 2020, 2021]
    macdonald_era = [2022, 2023]
    post_macdonald = [2024, 2025]
    
    print("Analyzing Macdonald era comparison...")
    
    all_results = []
    
    for year in pre_macdonald + macdonald_era + post_macdonald:
        result = analyze_macdonald_era(year)
        if result:
            all_results.append(result)
            print(f"  {year}: EPA = {result['defensive_epa']:.4f}, PPG = {result['ppg_allowed']:.1f}")
    
    if not all_results:
        print("No data available")
        return
    
    # get averages for each era
    pre_results = [r for r in all_results if r['year'] in pre_macdonald]
    mac_results = [r for r in all_results if r['year'] in macdonald_era]
    post_results = [r for r in all_results if r['year'] in post_macdonald]
    
    pre_epa = np.mean([r['defensive_epa'] for r in pre_results]) if pre_results else 0
    mac_epa = np.mean([r['defensive_epa'] for r in mac_results]) if mac_results else 0
    post_epa = np.mean([r['defensive_epa'] for r in post_results]) if post_results else 0
    
    pre_ppg = np.mean([r['ppg_allowed'] for r in pre_results]) if pre_results else 0
    mac_ppg = np.mean([r['ppg_allowed'] for r in mac_results]) if mac_results else 0
    post_ppg = np.mean([r['ppg_allowed'] for r in post_results]) if post_results else 0
    
    # setup the chart
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(3, 2, hspace=0.45, wspace=0.35, top=0.88, bottom=0.10, left=0.08, right=0.95)
    
    # colors for each group
    pre_color = '#7F8C8D'      
    mac_color = '#2ECC71'      
    post_color = '#E74C3C'
    
    # ===== PLOT 1: Defensive EPA/Play by Era =====
    ax1 = fig.add_subplot(gs[0, 0])
    
    eras = ['Pre-Macdonald\n(2019-2021)', 'Macdonald Era\n(2022-2023)', 'Post-Macdonald\n(2024-2025)']
    epa_values = [pre_epa, mac_epa, post_epa]
    colors = [pre_color, mac_color, post_color]
    
    bars1 = ax1.bar(eras, epa_values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    
    # Add value labels on bars
    for bar, val in zip(bars1, epa_values):
        height = bar.get_height()
        y_pos = height - 0.008 if height < 0 else height + 0.003
        ax1.text(bar.get_x() + bar.get_width()/2., y_pos,
                f'{val:.3f}',
                ha='center', va='top' if height < 0 else 'bottom',
                fontsize=13, fontweight='bold')
    
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax1.set_ylabel('Defensive EPA/Play', fontsize=12, fontweight='bold')
    ax1.set_title('Defensive Efficiency by Era', fontsize=14, fontweight='bold', pad=20)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(min(epa_values) * 1.3, max(epa_values) * 0.5)
    
    # Add annotation at the bottom right
    ax1.text(0.98, 0.02, 'Lower is Better (Negative = Good Defense)', 
             transform=ax1.transAxes, ha='right', va='bottom',
             fontsize=9, style='italic', color='#555555')
    
    # ===== PLOT 2: Points Per Game Allowed =====
    ax2 = fig.add_subplot(gs[0, 1])
    
    ppg_values = [pre_ppg, mac_ppg, post_ppg]
    bars2 = ax2.bar(eras, ppg_values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    
    for bar, val in zip(bars2, ppg_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{val:.1f}',
                ha='center', va='bottom',
                fontsize=13, fontweight='bold')
    
    ax2.set_ylabel('Points Per Game Allowed', fontsize=12, fontweight='bold')
    ax2.set_title('Scoring Defense by Era', fontsize=14, fontweight='bold', pad=20)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_ylim(0, max(ppg_values) * 1.2)
    
    ax2.text(0.98, 0.02, 'Lower is Better', 
             transform=ax2.transAxes, ha='right', va='bottom',
             fontsize=9, style='italic', color='#555555')
    
    # ===== PLOT 3: Year-by-Year EPA Trend =====
    ax3 = fig.add_subplot(gs[1, :])
    
    years = [r['year'] for r in all_results]
    year_epa = [r['defensive_epa'] for r in all_results]
    
    # Color each point by era
    point_colors = []
    for year in years:
        if year in pre_macdonald:
            point_colors.append(pre_color)
        elif year in macdonald_era:
            point_colors.append(mac_color)
        else:
            point_colors.append(post_color)
    
    ax3.plot(years, year_epa, marker='o', linewidth=3, markersize=12, 
             color='#34495E', alpha=0.6, zorder=1)
    
    # Overlay colored markers
    for i, (year, epa, color) in enumerate(zip(years, year_epa, point_colors)):
        ax3.scatter(year, epa, s=250, color=color, edgecolor='black', 
                   linewidth=2, zorder=2, alpha=0.9)
        # Position text below the point
        y_offset = -0.018 if epa < 0 else -0.018
        ax3.text(year, epa + y_offset, f'{epa:.3f}', 
                ha='center', va='top', fontsize=10, fontweight='bold')
    
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    # Add shaded regions for eras
    ax3.axvspan(2018.5, 2021.5, alpha=0.1, color=pre_color, label='Pre-Macdonald')
    ax3.axvspan(2021.5, 2023.5, alpha=0.1, color=mac_color, label='Macdonald Era')
    ax3.axvspan(2023.5, 2025.5, alpha=0.1, color=post_color, label='Post-Macdonald')
    
    ax3.set_xlabel('Season', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Defensive EPA/Play', fontsize=12, fontweight='bold')
    ax3.set_title('Year-by-Year Defensive EPA Trend', fontsize=14, fontweight='bold', pad=15)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(loc='lower right', fontsize=11, framealpha=0.95)
    ax3.set_xticks(years)
    # Adjust y-limits to prevent text overlap
    y_min = min(year_epa) - 0.03
    y_max = max(year_epa) + 0.02
    ax3.set_ylim(y_min, y_max)
    
    # ===== PLOT 4: Impact Metrics Table =====
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('tight')
    ax4.axis('off')
    
    # Calculate improvements
    pre_to_mac_epa = mac_epa - pre_epa
    mac_to_post_epa = post_epa - mac_epa
    pre_to_mac_ppg = mac_ppg - pre_ppg
    mac_to_post_ppg = post_ppg - mac_ppg
    
    table_data = [
        ['Era', 'Def EPA/Play', 'PPG Allowed', 'EPA Change', 'PPG Change', 'Assessment'],
        ['Pre-Macdonald\n(2019-2021)', f'{pre_epa:.3f}', f'{pre_ppg:.1f}', '—', '—', 'Solid Defense'],
        ['Macdonald Era\n(2022-2023)', f'{mac_epa:.3f}', f'{mac_ppg:.1f}', 
         f'{pre_to_mac_epa:+.3f}\n({"↓ Better" if pre_to_mac_epa < 0 else "↑ Worse"})', 
         f'{pre_to_mac_ppg:+.1f}\n({"↓ Better" if pre_to_mac_ppg < 0 else "↑ Worse"})',
         '✓✓ ELITE\n#1 Defense'],
        ['Post-Macdonald\n(2024-2025)', f'{post_epa:.3f}', f'{post_ppg:.1f}',
         f'{mac_to_post_epa:+.3f}\n({"↓ Better" if mac_to_post_epa < 0 else "↑ Worse"})',
         f'{mac_to_post_ppg:+.1f}\n({"↓ Better" if mac_to_post_ppg < 0 else "↑ Worse"})',
         '◐ Average\nMajor Decline']
    ]
    
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.18, 0.15, 0.15, 0.15, 0.15, 0.22])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 3.2)
    
    # Style header
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#34495E')
        cell.set_text_props(weight='bold', color='white', fontsize=12)
    
    # Style data rows with era colors
    for row, color in [(1, pre_color), (2, mac_color), (3, post_color)]:
        for col in range(6):
            cell = table[(row, col)]
            cell.set_facecolor(color)
            cell.set_alpha(0.3)
            if col == 0:
                cell.set_text_props(weight='bold', fontsize=11)
    
    # Main title
    fig.suptitle('The Mike Macdonald Effect: Defensive Performance Comparison', 
                 fontsize=18, fontweight='bold', y=0.97)
    fig.text(0.5, 0.925, 'Baltimore Ravens (2019-2025)', 
             ha='center', fontsize=13, style='italic')
    
    # Add key finding annotation
    finding_text = (
        f"Key Finding: Macdonald improved defensive EPA by {abs(pre_to_mac_epa):.3f} EPA/play. "
        f"Post-Macdonald decline: {abs(mac_to_post_epa):.3f} EPA/play loss.\n"
        f"Total impact of losing Macdonald: ~{abs(mac_to_post_epa) * 65:.1f} expected points per season "
        f"(≈{abs(mac_to_post_epa) * 65 / 17:.1f} points per game)"
    )
    
    fig.text(0.5, 0.03, finding_text,
             ha='center', fontsize=10, style='italic', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.4), wrap=True)
    
    # save it
    output_dir = Path(__file__).parent.parent / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "macdonaldEraComparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Visualization saved to: {output_path}")
    
    plt.close()
    
    # Print summary
    print(f"\n{'='*80}")
    print("MACDONALD ERA COMPARISON SUMMARY")
    print(f"{'='*80}\n")
    print(f"Pre-Macdonald (2019-2021):")
    print(f"  Defensive EPA/Play: {pre_epa:.3f}")
    print(f"  Points Per Game:    {pre_ppg:.1f}")
    print(f"\nMacdonald Era (2022-2023):")
    print(f"  Defensive EPA/Play: {mac_epa:.3f}  ({pre_to_mac_epa:+.3f} vs Pre)")
    print(f"  Points Per Game:    {mac_ppg:.1f}  ({pre_to_mac_ppg:+.1f} vs Pre)")
    print(f"\nPost-Macdonald (2024-2025):")
    print(f"  Defensive EPA/Play: {post_epa:.3f}  ({mac_to_post_epa:+.3f} vs Macdonald)")
    print(f"  Points Per Game:    {post_ppg:.1f}  ({mac_to_post_ppg:+.1f} vs Macdonald)")
    print(f"\n{'='*80}")
    print(f"MACDONALD IMPACT:")
    print(f"  Improvement during tenure:  {abs(pre_to_mac_epa):.3f} EPA/play")
    print(f"  Decline after departure:    {abs(mac_to_post_epa):.3f} EPA/play")
    print(f"  Total swing from peak:      {abs(post_epa - mac_epa):.3f} EPA/play")
    print(f"  Points per season impact:   ~{abs(mac_to_post_epa) * 65:.1f} expected points")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    create_macdonald_comparison()
