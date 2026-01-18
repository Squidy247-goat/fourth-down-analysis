"""
checks how predictable ravens playcalling is
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_predictability(year):
    """gets run pass ratios for different situations"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for Ravens offense (run or pass plays only)
    ravens_plays = df[
        (df['posteam'] == 'BAL') &
        (df['play_type'].isin(['run', 'pass']))
    ].copy()
    
    if len(ravens_plays) == 0:
        print(f"  WARNING: No play data found for {year}")
        return None
    
    # 1st Down plays
    first_down_plays = ravens_plays[ravens_plays['down'] == 1].copy()
    first_down_runs = len(first_down_plays[first_down_plays['play_type'] == 'run'])
    first_down_passes = len(first_down_plays[first_down_plays['play_type'] == 'pass'])
    first_down_total = first_down_runs + first_down_passes
    
    first_down_run_pct = (first_down_runs / first_down_total * 100) if first_down_total > 0 else 0
    first_down_pass_pct = (first_down_passes / first_down_total * 100) if first_down_total > 0 else 0
    
    # 2nd and Long (7+ yards to go)
    second_long = ravens_plays[
        (ravens_plays['down'] == 2) & 
        (ravens_plays['ydstogo'] >= 7)
    ].copy()
    second_long_runs = len(second_long[second_long['play_type'] == 'run'])
    second_long_passes = len(second_long[second_long['play_type'] == 'pass'])
    second_long_total = second_long_runs + second_long_passes
    
    second_long_run_pct = (second_long_runs / second_long_total * 100) if second_long_total > 0 else 0
    second_long_pass_pct = (second_long_passes / second_long_total * 100) if second_long_total > 0 else 0
    
    # 3rd and Short (1-3 yards to go)
    third_short = ravens_plays[
        (ravens_plays['down'] == 3) & 
        (ravens_plays['ydstogo'] >= 1) &
        (ravens_plays['ydstogo'] <= 3)
    ].copy()
    third_short_runs = len(third_short[third_short['play_type'] == 'run'])
    third_short_passes = len(third_short[third_short['play_type'] == 'pass'])
    third_short_total = third_short_runs + third_short_passes
    
    third_short_run_pct = (third_short_runs / third_short_total * 100) if third_short_total > 0 else 0
    third_short_pass_pct = (third_short_passes / third_short_total * 100) if third_short_total > 0 else 0
    
    print(f"  1st Down: {first_down_run_pct:.1f}% run / {first_down_pass_pct:.1f}% pass ({first_down_total} plays)")
    print(f"  2nd & Long: {second_long_run_pct:.1f}% run / {second_long_pass_pct:.1f}% pass ({second_long_total} plays)")
    print(f"  3rd & Short: {third_short_run_pct:.1f}% run / {third_short_pass_pct:.1f}% pass ({third_short_total} plays)")
    
    return {
        'year': year,
        'first_down': {
            'total': first_down_total,
            'runs': first_down_runs,
            'passes': first_down_passes,
            'run_pct': first_down_run_pct,
            'pass_pct': first_down_pass_pct
        },
        'second_long': {
            'total': second_long_total,
            'runs': second_long_runs,
            'passes': second_long_passes,
            'run_pct': second_long_run_pct,
            'pass_pct': second_long_pass_pct
        },
        'third_short': {
            'total': third_short_total,
            'runs': third_short_runs,
            'passes': third_short_passes,
            'run_pct': third_short_run_pct,
            'pass_pct': third_short_pass_pct
        }
    }


def main():
    """Analyze predictability metrics comparing 2019 vs 2023-2025."""
    
    print(f"{'='*80}")
    print("PREDICTABILITY METRICS ANALYSIS")
    print(f"{'='*80}")
    
    # Analyze 2019
    result_2019 = analyze_predictability(2019)
    
    # Analyze 2023-2025
    recent_years = [2023, 2024, 2025]
    recent_results = []
    
    for year in recent_years:
        result = analyze_predictability(year)
        if result:
            recent_results.append(result)
    
    if not result_2019 or not recent_results:
        print("Insufficient data available")
        return
    
    # Calculate 2023-2025 averages
    avg_first_down_run = np.mean([r['first_down']['run_pct'] for r in recent_results])
    avg_first_down_pass = np.mean([r['first_down']['pass_pct'] for r in recent_results])
    
    avg_second_long_run = np.mean([r['second_long']['run_pct'] for r in recent_results])
    avg_second_long_pass = np.mean([r['second_long']['pass_pct'] for r in recent_results])
    
    avg_third_short_run = np.mean([r['third_short']['run_pct'] for r in recent_results])
    avg_third_short_pass = np.mean([r['third_short']['pass_pct'] for r in recent_results])
    
    # Print summary
    print(f"\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("Predictability Metrics\n")
    print("Run-Pass Ratio by Down:\n")
    
    print("1st Down:")
    print(f"2019: {result_2019['first_down']['run_pct']:.1f}% run / {result_2019['first_down']['pass_pct']:.1f}% pass")
    print(f"2023-2025 avg: {avg_first_down_run:.1f}% run / {avg_first_down_pass:.1f}% pass")
    
    print(f"\n2nd and Long (7+ yards):")
    print(f"2019: {result_2019['second_long']['run_pct']:.1f}% run / {result_2019['second_long']['pass_pct']:.1f}% pass")
    print(f"2023-2025 avg: {avg_second_long_run:.1f}% run / {avg_second_long_pass:.1f}% pass")
    
    print(f"\n3rd and Short (1-3 yards):")
    print(f"2019: {result_2019['third_short']['run_pct']:.1f}% run / {result_2019['third_short']['pass_pct']:.1f}% pass")
    print(f"2023-2025 avg: {avg_third_short_run:.1f}% run / {avg_third_short_pass:.1f}% pass")
    
    # Analysis
    print(f"\n{'='*80}")
    print("ANALYSIS & INTERPRETATION")
    print(f"{'='*80}\n")
    
    # Calculate changes
    first_down_run_change = avg_first_down_run - result_2019['first_down']['run_pct']
    second_long_run_change = avg_second_long_run - result_2019['second_long']['run_pct']
    third_short_run_change = avg_third_short_run - result_2019['third_short']['run_pct']
    
    print("Changes in Run Frequency (2019 → 2023-2025):\n")
    
    print(f"1st Down: {first_down_run_change:+.1f} percentage points")
    if abs(first_down_run_change) < 3:
        print("  → Minimal change - maintaining balance")
    elif first_down_run_change > 0:
        print("  → More run-heavy - potentially MORE predictable")
    else:
        print("  → More pass-heavy - potentially LESS predictable")
    
    print(f"\n2nd & Long: {second_long_run_change:+.1f} percentage points")
    if abs(second_long_run_change) < 3:
        print("  → Minimal change - staying consistent")
    elif second_long_run_change > 0:
        print("  → More willing to run on 2nd & long - LESS predictable")
    else:
        print("  → More predictable - defenses expect pass")
    
    print(f"\n3rd & Short: {third_short_run_change:+.1f} percentage points")
    if abs(third_short_run_change) < 5:
        print("  → Minimal change - maintaining approach")
    elif third_short_run_change > 0:
        print("  → More run-heavy - leaning into strength but MORE predictable")
    else:
        print("  → More pass-heavy - keeping defenses honest, LESS predictable")
    
    # Overall predictability assessment
    print(f"\n{'='*80}")
    print("OVERALL PREDICTABILITY ASSESSMENT")
    print(f"{'='*80}\n")
    
    predictability_score = 0
    
    # 1st down - being too run-heavy is predictable
    if result_2019['first_down']['run_pct'] > 55:
        print("2019: Run-heavy on 1st down (predictable)")
        predictability_score += 1
    
    if avg_first_down_run > 55:
        print("2023-2025: Run-heavy on 1st down (predictable)")
        predictability_score += 1
    
    # 2nd & long - should be pass-heavy, running here is unpredictable
    if result_2019['second_long']['pass_pct'] > 70:
        print("2019: Very pass-heavy on 2nd & long (predictable)")
        predictability_score += 1
    
    if avg_second_long_pass > 70:
        print("2023-2025: Very pass-heavy on 2nd & long (predictable)")
        predictability_score += 1
    
    # 3rd & short - balanced is less predictable
    if result_2019['third_short']['run_pct'] > 65:
        print("2019: Very run-heavy on 3rd & short (predictable)")
        predictability_score += 1
    elif result_2019['third_short']['pass_pct'] > 65:
        print("2019: Very pass-heavy on 3rd & short (predictable)")
        predictability_score += 1
    
    if avg_third_short_run > 65:
        print("2023-2025: Very run-heavy on 3rd & short (predictable)")
        predictability_score += 1
    elif avg_third_short_pass > 65:
        print("2023-2025: Very pass-heavy on 3rd & short (predictable)")
        predictability_score += 1
    
    print(f"\nPredictability Indicators: {predictability_score}/6")
    
    if predictability_score <= 2:
        print("✓ UNPREDICTABLE: Ravens maintain good balance across situations")
    elif predictability_score <= 4:
        print("◐ MODERATELY PREDICTABLE: Some tendencies defenses can exploit")
    else:
        print("✗ HIGHLY PREDICTABLE: Clear patterns defenses can key on")
    
    # Detailed breakdown
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR BREAKDOWN (2023-2025)")
    print(f"{'='*80}\n")
    
    for result in recent_results:
        print(f"{result['year']}:")
        print(f"  1st Down: {result['first_down']['run_pct']:.1f}% run / {result['first_down']['pass_pct']:.1f}% pass")
        print(f"  2nd & Long: {result['second_long']['run_pct']:.1f}% run / {result['second_long']['pass_pct']:.1f}% pass")
        print(f"  3rd & Short: {result['third_short']['run_pct']:.1f}% run / {result['third_short']['pass_pct']:.1f}% pass")
        print()


if __name__ == "__main__":
    main()
