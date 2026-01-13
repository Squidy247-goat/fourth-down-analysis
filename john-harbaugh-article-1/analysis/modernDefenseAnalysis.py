"""
looks at how ravens defense does against modern pass heavy offenses
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_defense(year):
    """gets defense numbers for one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # ===== PASS RUSH METRICS =====
    # Filter for opponent pass plays where Ravens are on defense
    opp_passes = df[
        (df['defteam'] == 'BAL') &
        (df['pass_attempt'] == 1)
    ].copy()
    
    if len(opp_passes) == 0:
        print(f"  WARNING: No opponent passing data found for {year}")
        return None
    
    total_pass_plays = len(opp_passes)
    
    # Pressure metrics (sacks + QB hits)
    sacks = len(opp_passes[opp_passes['sack'] == 1])
    qb_hits = len(opp_passes[opp_passes['qb_hit'] == 1])
    
    # Sack rate
    sack_rate = (sacks / total_pass_plays * 100) if total_pass_plays > 0 else 0
    
    # QB hit rate (includes sacks)
    qb_hit_rate = (qb_hits / total_pass_plays * 100) if total_pass_plays > 0 else 0
    
    # ===== COVERAGE METRICS =====
    # Completion % allowed
    completions = len(opp_passes[opp_passes['complete_pass'] == 1])
    completion_pct_allowed = (completions / total_pass_plays * 100) if total_pass_plays > 0 else 0
    
    # Yards after catch allowed (average per completion)
    completed_passes = opp_passes[opp_passes['complete_pass'] == 1].copy()
    avg_yac_allowed = completed_passes['yards_after_catch'].fillna(0).mean()
    
    # ===== RUN DEFENSE METRICS =====
    # Filter for opponent run plays where Ravens are on defense
    opp_runs = df[
        (df['defteam'] == 'BAL') &
        (df['play_type'] == 'run')
    ].copy()
    
    total_run_plays = len(opp_runs)
    
    # Stuff rate (0 or negative yards)
    stuffs = opp_runs[opp_runs['yards_gained'] <= 0]
    stuff_count = len(stuffs)
    stuff_rate = (stuff_count / total_run_plays * 100) if total_run_plays > 0 else 0
    
    # Yards before contact (average)
    # This is approximately: yards_gained - yards_after_contact
    # We don't have direct yards_before_contact, so we'll estimate using available data
    # For now, we'll just note this limitation
    avg_yards_per_run = opp_runs['yards_gained'].fillna(0).mean()
    
    print(f"  Pass Defense:")
    print(f"    Total passes faced: {total_pass_plays}")
    print(f"    Sack rate: {sack_rate:.1f}%")
    print(f"    QB hit rate: {qb_hit_rate:.1f}%")
    print(f"    Completion % allowed: {completion_pct_allowed:.1f}%")
    print(f"    Avg YAC allowed: {avg_yac_allowed:.2f}")
    print(f"  Run Defense:")
    print(f"    Total runs faced: {total_run_plays}")
    print(f"    Stuff rate: {stuff_rate:.1f}%")
    print(f"    Avg yards per run: {avg_yards_per_run:.2f}")
    
    return {
        'year': year,
        'total_pass_plays': total_pass_plays,
        'sacks': sacks,
        'sack_rate': sack_rate,
        'qb_hits': qb_hits,
        'qb_hit_rate': qb_hit_rate,
        'completions_allowed': completions,
        'completion_pct_allowed': completion_pct_allowed,
        'avg_yac_allowed': avg_yac_allowed,
        'total_run_plays': total_run_plays,
        'stuff_count': stuff_count,
        'stuff_rate': stuff_rate,
        'avg_yards_per_run': avg_yards_per_run
    }


def main():
    """Analyze Ravens defense in the modern era (2019-2025)."""
    
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    
    print(f"{'='*80}")
    print("RAVENS DEFENSE IN THE PASS-HEAVY ERA (2019-2025)")
    print(f"{'='*80}")
    
    results = []
    
    for year in years:
        result = analyze_defense(year)
        if result:
            results.append(result)
    
    if not results:
        print("No data available")
        return
    
    # Calculate averages
    avg_sack_rate = np.mean([r['sack_rate'] for r in results])
    avg_qb_hit_rate = np.mean([r['qb_hit_rate'] for r in results])
    avg_completion_pct = np.mean([r['completion_pct_allowed'] for r in results])
    avg_yac = np.mean([r['avg_yac_allowed'] for r in results])
    avg_stuff_rate = np.mean([r['stuff_rate'] for r in results])
    avg_yards_per_run = np.mean([r['avg_yards_per_run'] for r in results])
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY (2019-2025)")
    print(f"{'='*80}\n")
    
    print(f"Average Sack Rate: {avg_sack_rate:.1f}%")
    print(f"Average QB Hit Rate: {avg_qb_hit_rate:.1f}%")
    print(f"Average Completion % Allowed: {avg_completion_pct:.1f}%")
    print(f"Average YAC Allowed: {avg_yac:.2f} yards")
    print(f"Average Stuff Rate: {avg_stuff_rate:.1f}%")
    print(f"Average Yards per Run Allowed: {avg_yards_per_run:.2f}")
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("Coverage in the Pass-Happy Era\n")
    
    print("Pass Rush Metrics (Sack Rate & QB Hit Rate):\n")
    for result in results:
        print(f"{result['year']}: {result['sack_rate']:.1f}% sack rate, {result['qb_hit_rate']:.1f}% QB hit rate")
    
    print(f"\nCoverage Success:")
    print(f"Completion % allowed (2019-2025): {avg_completion_pct:.1f}%")
    print(f"Yards after catch allowed: {avg_yac:.2f} yards")
    
    print(f"\nRun Defense:")
    print(f"Stuff rate (% of runs for 0 or negative yards): {avg_stuff_rate:.1f}%")
    print(f"Average yards per run allowed: {avg_yards_per_run:.2f}")
    
    # Analysis and interpretation
    print(f"\n{'='*80}")
    print("ANALYSIS & INTERPRETATION")
    print(f"{'='*80}\n")
    
    # Pass rush assessment
    print(f"Pass Rush Assessment:")
    if avg_sack_rate > 7:
        print(f"✓✓ ELITE PASS RUSH: {avg_sack_rate:.1f}% sack rate (dominant)")
    elif avg_sack_rate > 6:
        print(f"✓ STRONG PASS RUSH: {avg_sack_rate:.1f}% sack rate (above average)")
    else:
        print(f"◐ AVERAGE PASS RUSH: {avg_sack_rate:.1f}% sack rate (league average)")
    
    if avg_qb_hit_rate > 20:
        print(f"✓✓ HIGH PRESSURE: {avg_qb_hit_rate:.1f}% QB hit rate (constant pressure)")
    elif avg_qb_hit_rate > 15:
        print(f"✓ GOOD PRESSURE: {avg_qb_hit_rate:.1f}% QB hit rate")
    else:
        print(f"◐ MODERATE PRESSURE: {avg_qb_hit_rate:.1f}% QB hit rate")
    
    # Trend analysis
    first_year = results[0]
    last_year = results[-1]
    
    sack_trend = last_year['sack_rate'] - first_year['sack_rate']
    hit_trend = last_year['qb_hit_rate'] - first_year['qb_hit_rate']
    completion_trend = last_year['completion_pct_allowed'] - first_year['completion_pct_allowed']
    
    print(f"\nTrends (2019 → {last_year['year']}):")
    print(f"  Sack rate: {first_year['sack_rate']:.1f}% → {last_year['sack_rate']:.1f}% ({sack_trend:+.1f}%)")
    print(f"  QB hit rate: {first_year['qb_hit_rate']:.1f}% → {last_year['qb_hit_rate']:.1f}% ({hit_trend:+.1f}%)")
    print(f"  Completion % allowed: {first_year['completion_pct_allowed']:.1f}% → {last_year['completion_pct_allowed']:.1f}% ({completion_trend:+.1f}%)")
    
    if sack_trend > 0 and hit_trend > 0:
        print("\n✓✓ IMPROVEMENT: Pass rush getting stronger over time")
    elif sack_trend < 0 and hit_trend < 0:
        print("\n✗ DECLINE: Pass rush weakening over time")
    
    # Coverage assessment
    print(f"\nCoverage Assessment:")
    if avg_completion_pct < 63:
        print(f"✓✓ ELITE COVERAGE: {avg_completion_pct:.1f}% completion allowed (well below league average)")
    elif avg_completion_pct < 65:
        print(f"✓ GOOD COVERAGE: {avg_completion_pct:.1f}% completion allowed (below league average)")
    elif avg_completion_pct < 67:
        print(f"◐ AVERAGE COVERAGE: {avg_completion_pct:.1f}% completion allowed (around league average)")
    else:
        print(f"✗ POOR COVERAGE: {avg_completion_pct:.1f}% completion allowed (above league average)")
    
    # Run defense assessment
    print(f"\nRun Defense Assessment:")
    if avg_stuff_rate > 20:
        print(f"✓✓ ELITE RUN DEFENSE: {avg_stuff_rate:.1f}% stuff rate (dominant at line)")
    elif avg_stuff_rate > 18:
        print(f"✓ STRONG RUN DEFENSE: {avg_stuff_rate:.1f}% stuff rate (above average)")
    else:
        print(f"◐ AVERAGE RUN DEFENSE: {avg_stuff_rate:.1f}% stuff rate (league average)")
    
    # Best and worst years
    best_pass_rush = max(results, key=lambda x: x['sack_rate'])
    worst_pass_rush = min(results, key=lambda x: x['sack_rate'])
    best_coverage = min(results, key=lambda x: x['completion_pct_allowed'])
    worst_coverage = max(results, key=lambda x: x['completion_pct_allowed'])
    
    print(f"\n{'='*80}")
    print("BEST & WORST SEASONS")
    print(f"{'='*80}\n")
    
    print(f"Best pass rush: {best_pass_rush['year']} ({best_pass_rush['sack_rate']:.1f}% sack rate)")
    print(f"Worst pass rush: {worst_pass_rush['year']} ({worst_pass_rush['sack_rate']:.1f}% sack rate)")
    print(f"Best coverage: {best_coverage['year']} ({best_coverage['completion_pct_allowed']:.1f}% allowed)")
    print(f"Worst coverage: {worst_coverage['year']} ({worst_coverage['completion_pct_allowed']:.1f}% allowed)")
    
    # Overall assessment
    print(f"\n{'='*80}")
    print("OVERALL ASSESSMENT")
    print(f"{'='*80}\n")
    
    print("Could Harbaugh's defenses adapt to the modern pass-happy era?\n")
    
    overall_score = 0
    if avg_sack_rate > 6:
        overall_score += 1
    if avg_completion_pct < 65:
        overall_score += 1
    if avg_stuff_rate > 18:
        overall_score += 1
    
    if overall_score >= 2:
        print("✓ YES: The Ravens successfully adapted to the modern era")
        print("   Strong metrics across pass rush, coverage, and run defense")
    else:
        print("◐ MIXED: Some strengths but clear weaknesses in modern defensive approach")
    
    # Year-by-year detailed breakdown
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR DETAILED BREAKDOWN")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['year']}:")
        print(f"  Sack rate: {result['sack_rate']:.1f}%, QB hit rate: {result['qb_hit_rate']:.1f}%")
        print(f"  Completion %: {result['completion_pct_allowed']:.1f}%, YAC: {result['avg_yac_allowed']:.2f}")
        print(f"  Stuff rate: {result['stuff_rate']:.1f}%, Yards/run: {result['avg_yards_per_run']:.2f}")
        print()


if __name__ == "__main__":
    main()
