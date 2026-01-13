"""
looks at how passing game has changed with lamar
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_passing_efficiency(year):
    """gets passing stats for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for Ravens passing plays (pass attempts)
    # Include completions, incompletions, but exclude spikes and other non-standard plays
    ravens_passes = df[
        (df['posteam'] == 'BAL') &
        (df['pass_attempt'] == 1) &
        (df['qb_spike'] != 1)  # Exclude spikes
    ].copy()
    
    if len(ravens_passes) == 0:
        print(f"  WARNING: No passing data found for {year}")
        return None
    
    # Calculate completion percentage
    completions = ravens_passes[ravens_passes['complete_pass'] == 1]
    total_attempts = len(ravens_passes)
    total_completions = len(completions)
    completion_pct = (total_completions / total_attempts * 100) if total_attempts > 0 else 0
    
    # Calculate yards per attempt (total passing yards / attempts)
    total_yards = ravens_passes['yards_gained'].fillna(0).sum()
    yards_per_attempt = total_yards / total_attempts if total_attempts > 0 else 0
    
    # Calculate average air yards (depth of target)
    # Air yards is the distance the ball traveled in the air
    avg_air_yards = ravens_passes['air_yards'].fillna(0).mean()
    
    # Additional metrics for context
    touchdowns = len(ravens_passes[ravens_passes['touchdown'] == 1])
    interceptions = len(ravens_passes[ravens_passes['interception'] == 1])
    sacks = len(df[(df['posteam'] == 'BAL') & (df['sack'] == 1)])
    
    print(f"  Attempts: {total_attempts}")
    print(f"  Completions: {total_completions}")
    print(f"  Completion %: {completion_pct:.1f}%")
    print(f"  Total Yards: {total_yards:.0f}")
    print(f"  Yards per Attempt: {yards_per_attempt:.2f}")
    print(f"  Average Air Yards: {avg_air_yards:.2f}")
    print(f"  TDs: {touchdowns}, INTs: {interceptions}, Sacks: {sacks}")
    
    return {
        'year': year,
        'attempts': total_attempts,
        'completions': total_completions,
        'completion_pct': completion_pct,
        'total_yards': total_yards,
        'yards_per_attempt': yards_per_attempt,
        'avg_air_yards': avg_air_yards,
        'touchdowns': touchdowns,
        'interceptions': interceptions,
        'sacks': sacks
    }


def main():
    """Analyze passing efficiency trends for 2019-2025."""
    
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    
    print(f"{'='*80}")
    print("PASSING EFFICIENCY TRENDS (2019-2025)")
    print(f"{'='*80}")
    
    results = []
    
    for year in years:
        result = analyze_passing_efficiency(year)
        if result:
            results.append(result)
    
    if not results:
        print("No data available")
        return
    
    # Calculate averages and trends
    avg_completion_pct = np.mean([r['completion_pct'] for r in results])
    avg_yards_per_attempt = np.mean([r['yards_per_attempt'] for r in results])
    avg_air_yards_all = np.mean([r['avg_air_yards'] for r in results])
    
    # 2020-2025 average air yards
    recent_results = [r for r in results if r['year'] >= 2020]
    avg_air_yards_2020_2025 = np.mean([r['avg_air_yards'] for r in recent_results]) if recent_results else 0
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY (2019-2025)")
    print(f"{'='*80}\n")
    
    print(f"Average Completion %: {avg_completion_pct:.1f}%")
    print(f"Average Yards per Attempt: {avg_yards_per_attempt:.2f}")
    print(f"Average Air Yards (2019-2025): {avg_air_yards_all:.2f}")
    print(f"Average Air Yards (2020-2025): {avg_air_yards_2020_2025:.2f}")
    
    # Trend analysis
    first_year = results[0]
    last_year = results[-1]
    
    comp_pct_change = last_year['completion_pct'] - first_year['completion_pct']
    ypa_change = last_year['yards_per_attempt'] - first_year['yards_per_attempt']
    air_yards_change = last_year['avg_air_yards'] - first_year['avg_air_yards']
    
    print(f"\nTrends (2019 → {last_year['year']}):")
    print(f"  Completion %: {first_year['completion_pct']:.1f}% → {last_year['completion_pct']:.1f}% ({comp_pct_change:+.1f}%)")
    print(f"  Yards per Attempt: {first_year['yards_per_attempt']:.2f} → {last_year['yards_per_attempt']:.2f} ({ypa_change:+.2f})")
    print(f"  Air Yards: {first_year['avg_air_yards']:.2f} → {last_year['avg_air_yards']:.2f} ({air_yards_change:+.2f})")
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("Passing Efficiency Trends\n")
    
    print("Completion Percentage:")
    for result in results:
        print(f"{result['year']}: {result['completion_pct']:.1f}%")
    
    print(f"\nYards Per Attempt:")
    for result in results:
        print(f"{result['year']}: {result['yards_per_attempt']:.2f}")
    
    print(f"\nAverage Air Yards:")
    for result in results:
        print(f"{result['year']}: {result['avg_air_yards']:.2f}")
    print(f"2020-2025 average: {avg_air_yards_2020_2025:.2f}")
    
    # Analysis and interpretation
    print(f"\n{'='*80}")
    print("ANALYSIS & INTERPRETATION")
    print(f"{'='*80}\n")
    
    # Identify best and worst years
    best_comp_pct = max(results, key=lambda x: x['completion_pct'])
    worst_comp_pct = min(results, key=lambda x: x['completion_pct'])
    best_ypa = max(results, key=lambda x: x['yards_per_attempt'])
    worst_ypa = min(results, key=lambda x: x['yards_per_attempt'])
    
    print(f"Best Completion %: {best_comp_pct['year']} ({best_comp_pct['completion_pct']:.1f}%)")
    print(f"Worst Completion %: {worst_comp_pct['year']} ({worst_comp_pct['completion_pct']:.1f}%)")
    print(f"Best YPA: {best_ypa['year']} ({best_ypa['yards_per_attempt']:.2f})")
    print(f"Worst YPA: {worst_ypa['year']} ({worst_ypa['yards_per_attempt']:.2f})")
    
    # Trend interpretation
    print(f"\nTrend Analysis:")
    
    if comp_pct_change > 0:
        print(f"✓ Completion % IMPROVED by {comp_pct_change:.1f} percentage points")
    else:
        print(f"✗ Completion % DECLINED by {abs(comp_pct_change):.1f} percentage points")
    
    if ypa_change > 0:
        print(f"✓ Yards per Attempt IMPROVED by {ypa_change:.2f}")
    else:
        print(f"✗ Yards per Attempt DECLINED by {abs(ypa_change):.2f}")
    
    if air_yards_change > 0:
        print(f"↑ Air Yards INCREASED by {air_yards_change:.2f} yards (more aggressive)")
    else:
        print(f"↓ Air Yards DECREASED by {abs(air_yards_change):.2f} yards (more conservative)")
    
    # Overall assessment
    print(f"\nOverall Assessment:")
    
    if comp_pct_change > 0 and ypa_change > 0:
        print("✓✓ STRONG DEVELOPMENT: Both completion % and YPA improved - Lamar developed as a passer")
    elif comp_pct_change > 0 or ypa_change > 0:
        print("✓ MODERATE DEVELOPMENT: Some improvement in passing efficiency")
    else:
        print("✗ DECLINE: Passing efficiency metrics have declined - defenses may have adjusted")
    
    # Year-by-year detailed breakdown
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR DETAILED BREAKDOWN")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['year']}:")
        print(f"  Attempts: {result['attempts']}")
        print(f"  Completion %: {result['completion_pct']:.1f}%")
        print(f"  Yards per Attempt: {result['yards_per_attempt']:.2f}")
        print(f"  Air Yards: {result['avg_air_yards']:.2f}")
        print(f"  TDs: {result['touchdowns']}, INTs: {result['interceptions']}, Sacks: {result['sacks']}")
        
        # TD:INT ratio
        td_int_ratio = result['touchdowns'] / result['interceptions'] if result['interceptions'] > 0 else result['touchdowns']
        print(f"  TD:INT Ratio: {td_int_ratio:.2f}:1")
        print()


if __name__ == "__main__":
    main()
