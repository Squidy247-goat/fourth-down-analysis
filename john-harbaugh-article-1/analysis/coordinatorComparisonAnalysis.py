"""
compares greg roman vs todd monken as offensive coordinators
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_offensive_epa(year):
    """gets offense epa for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for Ravens offensive plays (pass or run)
    ravens_offense = df[
        (df['posteam'] == 'BAL') &
        (df['play_type'].isin(['run', 'pass'])) &
        (df['epa'].notna())  # Only plays with valid EPA
    ].copy()
    
    if len(ravens_offense) == 0:
        print(f"  WARNING: No offensive EPA data found for {year}")
        return None
    
    # Overall offensive EPA
    total_plays = len(ravens_offense)
    total_epa = ravens_offense['epa'].sum()
    epa_per_play = total_epa / total_plays if total_plays > 0 else 0
    
    # Pass EPA
    pass_plays = ravens_offense[ravens_offense['play_type'] == 'pass'].copy()
    pass_total = len(pass_plays)
    pass_epa_total = pass_plays['epa'].sum()
    pass_epa_per_play = pass_epa_total / pass_total if pass_total > 0 else 0
    
    # Rush EPA
    rush_plays = ravens_offense[ravens_offense['play_type'] == 'run'].copy()
    rush_total = len(rush_plays)
    rush_epa_total = rush_plays['epa'].sum()
    rush_epa_per_play = rush_epa_total / rush_total if rush_total > 0 else 0
    
    print(f"  Total plays: {total_plays}")
    print(f"  Overall EPA/play: {epa_per_play:.3f}")
    print(f"  Pass plays: {pass_total}, Pass EPA/play: {pass_epa_per_play:.3f}")
    print(f"  Rush plays: {rush_total}, Rush EPA/play: {rush_epa_per_play:.3f}")
    
    return {
        'year': year,
        'total_plays': total_plays,
        'epa_per_play': epa_per_play,
        'pass_plays': pass_total,
        'pass_epa_per_play': pass_epa_per_play,
        'rush_plays': rush_total,
        'rush_epa_per_play': rush_epa_per_play,
        'total_epa': total_epa,
        'pass_epa_total': pass_epa_total,
        'rush_epa_total': rush_epa_total
    }


def main():
    """Compare Greg Roman (2019-2022) vs Todd Monken (2023-2025)."""
    
    print(f"{'='*80}")
    print("OFFENSIVE COORDINATOR COMPARISON")
    print("Greg Roman (2019-2022) vs Todd Monken (2023-2025)")
    print(f"{'='*80}")
    
    # Greg Roman era (2019-2022)
    roman_years = [2019, 2020, 2021, 2022]
    roman_results = []
    
    print(f"\n{'='*80}")
    print("GREG ROMAN ERA (2019-2022)")
    print(f"{'='*80}")
    
    for year in roman_years:
        result = analyze_offensive_epa(year)
        if result:
            roman_results.append(result)
    
    # Todd Monken era (2023-2025)
    monken_years = [2023, 2024, 2025]
    monken_results = []
    
    print(f"\n{'='*80}")
    print("TODD MONKEN ERA (2023-2025)")
    print(f"{'='*80}")
    
    for year in monken_years:
        result = analyze_offensive_epa(year)
        if result:
            monken_results.append(result)
    
    if not roman_results or not monken_results:
        print("Insufficient data available")
        return
    
    # Calculate averages for Roman era
    roman_total_plays = sum(r['total_plays'] for r in roman_results)
    roman_total_epa = sum(r['total_epa'] for r in roman_results)
    roman_avg_epa = roman_total_epa / roman_total_plays if roman_total_plays > 0 else 0
    
    roman_pass_plays = sum(r['pass_plays'] for r in roman_results)
    roman_pass_epa_total = sum(r['pass_epa_total'] for r in roman_results)
    roman_pass_epa = roman_pass_epa_total / roman_pass_plays if roman_pass_plays > 0 else 0
    
    roman_rush_plays = sum(r['rush_plays'] for r in roman_results)
    roman_rush_epa_total = sum(r['rush_epa_total'] for r in roman_results)
    roman_rush_epa = roman_rush_epa_total / roman_rush_plays if roman_rush_plays > 0 else 0
    
    # Calculate averages for Monken era
    monken_total_plays = sum(r['total_plays'] for r in monken_results)
    monken_total_epa = sum(r['total_epa'] for r in monken_results)
    monken_avg_epa = monken_total_epa / monken_total_plays if monken_total_plays > 0 else 0
    
    monken_pass_plays = sum(r['pass_plays'] for r in monken_results)
    monken_pass_epa_total = sum(r['pass_epa_total'] for r in monken_results)
    monken_pass_epa = monken_pass_epa_total / monken_pass_plays if monken_pass_plays > 0 else 0
    
    monken_rush_plays = sum(r['rush_plays'] for r in monken_results)
    monken_rush_epa_total = sum(r['rush_epa_total'] for r in monken_results)
    monken_rush_epa = monken_rush_epa_total / monken_rush_plays if monken_rush_plays > 0 else 0
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY COMPARISON")
    print(f"{'='*80}\n")
    
    print(f"Greg Roman Era (2019-2022):")
    print(f"  Overall EPA/play: {roman_avg_epa:.3f}")
    print(f"  Pass EPA/play: {roman_pass_epa:.3f}")
    print(f"  Rush EPA/play: {roman_rush_epa:.3f}")
    print(f"  Total plays: {roman_total_plays}")
    
    print(f"\nTodd Monken Era (2023-2025):")
    print(f"  Overall EPA/play: {monken_avg_epa:.3f}")
    print(f"  Pass EPA/play: {monken_pass_epa:.3f}")
    print(f"  Rush EPA/play: {monken_rush_epa:.3f}")
    print(f"  Total plays: {monken_total_plays}")
    
    # Calculate differences
    epa_diff = monken_avg_epa - roman_avg_epa
    pass_epa_diff = monken_pass_epa - roman_pass_epa
    rush_epa_diff = monken_rush_epa - roman_rush_epa
    
    print(f"\nDifferences (Monken - Roman):")
    print(f"  Overall EPA/play: {epa_diff:+.3f}")
    print(f"  Pass EPA/play: {pass_epa_diff:+.3f}")
    print(f"  Rush EPA/play: {rush_epa_diff:+.3f}")
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("Offensive Coordinator Impact:\n")
    print("Greg Roman was fired after the 2022 season. Todd Monken took over in 2023.\n")
    
    print("Offensive EPA/Play:")
    print(f"Under Roman (2019-2022): {roman_avg_epa:.3f}")
    print(f"Under Monken (2023-2025): {monken_avg_epa:.3f}")
    print(f"Difference: {epa_diff:+.3f}")
    
    print(f"\nPass EPA vs Rush EPA:")
    print(f"Roman era: Pass EPA {roman_pass_epa:.3f}, Rush EPA {roman_rush_epa:.3f}")
    print(f"Monken era: Pass EPA {monken_pass_epa:.3f}, Rush EPA {monken_rush_epa:.3f}")
    
    # Analysis and interpretation
    print(f"\n{'='*80}")
    print("ANALYSIS & INTERPRETATION")
    print(f"{'='*80}\n")
    
    if epa_diff > 0.02:
        print(f"✓✓ SIGNIFICANT IMPROVEMENT: Monken's offense is {epa_diff:.3f} EPA/play better")
        print("   The coordinator change was clearly successful.")
    elif epa_diff > 0:
        print(f"✓ SLIGHT IMPROVEMENT: Monken's offense is {epa_diff:.3f} EPA/play better")
        print("   The change helped, but the improvement is modest.")
    elif epa_diff > -0.02:
        print(f"◐ MINIMAL CHANGE: Only {epa_diff:.3f} EPA/play difference")
        print("   The coordinator change didn't significantly impact performance.")
    else:
        print(f"✗ DECLINE: Monken's offense is {abs(epa_diff):.3f} EPA/play worse")
        print("   The offense has regressed under the new coordinator.")
    
    print(f"\nPassing Game Evolution:")
    if pass_epa_diff > 0.05:
        print(f"✓✓ MAJOR PASSING IMPROVEMENT: +{pass_epa_diff:.3f} EPA/play")
        print("   Monken has significantly elevated the passing attack.")
    elif pass_epa_diff > 0:
        print(f"✓ PASSING IMPROVEMENT: +{pass_epa_diff:.3f} EPA/play")
        print("   The passing game has improved under Monken.")
    else:
        print(f"✗ PASSING DECLINE: {pass_epa_diff:.3f} EPA/play")
        print("   The passing game was better under Roman.")
    
    print(f"\nRushing Game Evolution:")
    if rush_epa_diff > 0.02:
        print(f"✓ RUSHING IMPROVEMENT: +{rush_epa_diff:.3f} EPA/play")
        print("   The run game has improved under Monken.")
    elif rush_epa_diff > -0.02:
        print(f"◐ RUSHING STABILITY: {rush_epa_diff:+.3f} EPA/play")
        print("   The run game has remained consistent.")
    else:
        print(f"✗ RUSHING DECLINE: {rush_epa_diff:.3f} EPA/play")
        print("   The run game was better under Roman.")
    
    # Balance analysis
    roman_balance = abs(roman_pass_epa - roman_rush_epa)
    monken_balance = abs(monken_pass_epa - monken_rush_epa)
    
    print(f"\nOffensive Balance:")
    print(f"Roman era gap (Pass EPA - Rush EPA): {roman_balance:.3f}")
    print(f"Monken era gap (Pass EPA - Rush EPA): {monken_balance:.3f}")
    
    if monken_balance < roman_balance:
        print("✓ More balanced under Monken - both facets effective")
    else:
        print("✗ Less balanced under Monken - one facet dominates")
    
    # Year-by-year comparison
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR BREAKDOWN")
    print(f"{'='*80}\n")
    
    print("Greg Roman Era:\n")
    for result in roman_results:
        print(f"{result['year']}: Overall EPA {result['epa_per_play']:.3f}, "
              f"Pass EPA {result['pass_epa_per_play']:.3f}, "
              f"Rush EPA {result['rush_epa_per_play']:.3f}")
    
    print(f"\nTodd Monken Era:\n")
    for result in monken_results:
        print(f"{result['year']}: Overall EPA {result['epa_per_play']:.3f}, "
              f"Pass EPA {result['pass_epa_per_play']:.3f}, "
              f"Rush EPA {result['rush_epa_per_play']:.3f}")
    
    # Best/worst years
    all_results = roman_results + monken_results
    best_year = max(all_results, key=lambda x: x['epa_per_play'])
    worst_year = min(all_results, key=lambda x: x['epa_per_play'])
    
    print(f"\n{'='*80}")
    print("BEST & WORST SEASONS")
    print(f"{'='*80}\n")
    
    print(f"Best offensive season: {best_year['year']} ({best_year['epa_per_play']:.3f} EPA/play)")
    if best_year['year'] in roman_years:
        print("  → Under Greg Roman")
    else:
        print("  → Under Todd Monken")
    
    print(f"\nWorst offensive season: {worst_year['year']} ({worst_year['epa_per_play']:.3f} EPA/play)")
    if worst_year['year'] in roman_years:
        print("  → Under Greg Roman")
    else:
        print("  → Under Todd Monken")


if __name__ == "__main__":
    main()
