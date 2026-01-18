"""
compares ravens defense before during and after macdonald was DC
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_defensive_performance(year):
    """gets defense stats for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # ===== POINTS ALLOWED =====
    # Get all plays where Ravens are on defense
    ravens_defense = df[df['defteam'] == 'BAL'].copy()
    
    # Calculate total points allowed (sum of opponent scoring plays)
    # Points are tracked by total_home_score and total_away_score
    # We need to find the final score for opponents
    games = ravens_defense.groupby('game_id').agg({
        'total_home_score': 'max',
        'total_away_score': 'max',
        'home_team': 'first'
    }).reset_index()
    
    total_points_allowed = 0
    for _, game in games.iterrows():
        if game['home_team'] == 'BAL':
            # Ravens at home, away score is opponent
            total_points_allowed += game['total_away_score']
        else:
            # Ravens away, home score is opponent
            total_points_allowed += game['total_home_score']
    
    num_games = len(games)
    ppg_allowed = total_points_allowed / num_games if num_games > 0 else 0
    
    # ===== YARDS ALLOWED =====
    # Filter for opponent offensive plays (run or pass)
    opp_plays = df[
        (df['defteam'] == 'BAL') &
        (df['play_type'].isin(['run', 'pass']))
    ].copy()
    
    total_yards_allowed = opp_plays['yards_gained'].fillna(0).sum()
    total_plays = len(opp_plays)
    ypg_allowed = total_yards_allowed / num_games if num_games > 0 else 0
    yards_per_play = total_yards_allowed / total_plays if total_plays > 0 else 0
    
    # ===== DEFENSIVE EPA =====
    # EPA for plays where Ravens are on defense
    opp_epa_plays = df[
        (df['defteam'] == 'BAL') &
        (df['play_type'].isin(['run', 'pass'])) &
        (df['epa'].notna())
    ].copy()
    
    defensive_epa_total = opp_epa_plays['epa'].sum()  # Lower is better for defense
    defensive_plays = len(opp_epa_plays)
    defensive_epa_per_play = defensive_epa_total / defensive_plays if defensive_plays > 0 else 0
    
    print(f"  Games: {num_games}")
    print(f"  Points allowed: {total_points_allowed} ({ppg_allowed:.1f} per game)")
    print(f"  Yards allowed: {total_yards_allowed} ({ypg_allowed:.1f} per game)")
    print(f"  Yards per play: {yards_per_play:.2f}")
    print(f"  Defensive EPA/play: {defensive_epa_per_play:.3f} (lower is better)")
    
    return {
        'year': year,
        'games': num_games,
        'points_allowed': total_points_allowed,
        'ppg_allowed': ppg_allowed,
        'yards_allowed': total_yards_allowed,
        'ypg_allowed': ypg_allowed,
        'yards_per_play': yards_per_play,
        'defensive_epa_total': defensive_epa_total,
        'defensive_epa_per_play': defensive_epa_per_play
    }


def main():
    """Analyze the Mike Macdonald Effect (2019-2025)."""
    
    print(f"{'='*80}")
    print("THE MIKE MACDONALD EFFECT")
    print("Defensive Coordinator Analysis")
    print(f"{'='*80}")
    
    # Define eras
    pre_macdonald_years = [2019, 2020, 2021]  # Wink Martindale
    macdonald_years = [2022, 2023]  # Mike Macdonald
    post_macdonald_years = [2024, 2025]  # Post-Macdonald
    
    all_years = pre_macdonald_years + macdonald_years + post_macdonald_years
    results = {}
    
    for year in all_years:
        result = analyze_defensive_performance(year)
        if result:
            results[year] = result
    
    if not results:
        print("No data available")
        return
    
    # Calculate era averages
    def calc_era_averages(years, label):
        era_results = [results[y] for y in years if y in results]
        if not era_results:
            return None
        
        avg_ppg = np.mean([r['ppg_allowed'] for r in era_results])
        avg_ypg = np.mean([r['ypg_allowed'] for r in era_results])
        avg_epa = np.mean([r['defensive_epa_per_play'] for r in era_results])
        
        print(f"\n{label}:")
        print(f"  Points per game: {avg_ppg:.1f}")
        print(f"  Yards per game: {avg_ypg:.1f}")
        print(f"  Defensive EPA/play: {avg_epa:.3f}")
        
        return {
            'label': label,
            'years': years,
            'avg_ppg': avg_ppg,
            'avg_ypg': avg_ypg,
            'avg_epa': avg_epa,
            'results': era_results
        }
    
    print(f"\n{'='*80}")
    print("ERA COMPARISONS")
    print(f"{'='*80}")
    
    pre_mac = calc_era_averages(pre_macdonald_years, "Pre-Macdonald (2019-2021, Wink Martindale)")
    mac = calc_era_averages(macdonald_years, "Macdonald Era (2022-2023)")
    post_mac = calc_era_averages(post_macdonald_years, "Post-Macdonald (2024-2025)")
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("The Mike Macdonald Effect\n")
    
    print("Defensive Rankings:\n")
    
    # For 2022 and 2023, provide detailed stats
    if 2022 in results:
        r = results[2022]
        print(f"2022 (Macdonald Year 1):")
        print(f"  Points allowed: {r['points_allowed']} ({r['ppg_allowed']:.1f} per game)")
        print(f"  Yards allowed: {r['yards_allowed']} ({r['ypg_allowed']:.1f} per game)")
        print(f"  Defensive EPA/play: {r['defensive_epa_per_play']:.3f}")
    
    if 2023 in results:
        r = results[2023]
        print(f"\n2023 (Macdonald Year 2):")
        print(f"  Points allowed: {r['points_allowed']} ({r['ppg_allowed']:.1f} per game)")
        print(f"  Yards allowed: {r['yards_allowed']} ({r['ypg_allowed']:.1f} per game)")
        print(f"  Defensive EPA/play: {r['defensive_epa_per_play']:.3f}")
    
    print(f"\nDefensive EPA/Play:")
    if pre_mac:
        print(f"Pre-Macdonald (2019-2021): {pre_mac['avg_epa']:.3f}")
    if mac:
        print(f"Macdonald era (2022-2023): {mac['avg_epa']:.3f}")
    if post_mac:
        print(f"Post-Macdonald (2024-2025): {post_mac['avg_epa']:.3f}")
    
    # Analysis and interpretation
    print(f"\n{'='*80}")
    print("ANALYSIS & INTERPRETATION")
    print(f"{'='*80}\n")
    
    if mac and pre_mac:
        epa_improvement = pre_mac['avg_epa'] - mac['avg_epa']  # Lower is better, so this should be positive
        ppg_improvement = pre_mac['avg_ppg'] - mac['avg_ppg']
        ypg_improvement = pre_mac['avg_ypg'] - mac['avg_ypg']
        
        print("The Macdonald Transformation:\n")
        print(f"EPA/play change: {epa_improvement:+.3f} (lower is better)")
        print(f"Points per game: {ppg_improvement:+.1f}")
        print(f"Yards per game: {ypg_improvement:+.1f}")
        
        if epa_improvement > 0.02:
            print("\n✓✓ DRAMATIC IMPROVEMENT: Macdonald transformed the defense")
        elif epa_improvement > 0:
            print("\n✓ IMPROVEMENT: Defense got better under Macdonald")
        else:
            print("\n◐ MINIMAL CHANGE: Defense remained similar")
    
    if post_mac and mac:
        post_decline = post_mac['avg_epa'] - mac['avg_epa']
        ppg_post_change = post_mac['avg_ppg'] - mac['avg_ppg']
        ypg_post_change = post_mac['avg_ypg'] - mac['avg_ypg']
        
        print(f"\nPost-Macdonald Impact:\n")
        print(f"EPA/play change: {post_decline:+.3f}")
        print(f"Points per game: {ppg_post_change:+.1f}")
        print(f"Yards per game: {ypg_post_change:+.1f}")
        
        if post_decline > 0.02:
            print("\n✗✗ SIGNIFICANT DECLINE: Defense fell apart without Macdonald")
        elif post_decline > 0:
            print("\n✗ DECLINE: Defense got worse after Macdonald left")
        elif post_decline > -0.02:
            print("\n◐ MAINTAINED: Defense stayed at similar level")
        else:
            print("\n✓ IMPROVED: Defense actually got better after Macdonald")
    
    # 2023 peak analysis
    if 2023 in results:
        best_year = min(results.values(), key=lambda x: x['defensive_epa_per_play'])
        if best_year['year'] == 2023:
            print(f"\n✓ 2023 was the BEST defensive year by EPA ({best_year['defensive_epa_per_play']:.3f})")
        else:
            print(f"\nBest defensive year was {best_year['year']} ({best_year['defensive_epa_per_play']:.3f})")
    
    # Year-by-year breakdown
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR BREAKDOWN")
    print(f"{'='*80}\n")
    
    for year in sorted(results.keys()):
        r = results[year]
        coordinator = ""
        if year in pre_macdonald_years:
            coordinator = "(Wink Martindale)"
        elif year in macdonald_years:
            coordinator = "(Mike Macdonald)"
        else:
            coordinator = "(Post-Macdonald)"
        
        print(f"{year} {coordinator}:")
        print(f"  {r['ppg_allowed']:.1f} PPG, {r['ypg_allowed']:.1f} YPG")
        print(f"  {r['yards_per_play']:.2f} yards/play, {r['defensive_epa_per_play']:.3f} EPA/play")
        print()
    
    # Overall assessment
    print(f"{'='*80}")
    print("OVERALL ASSESSMENT")
    print(f"{'='*80}\n")
    
    print("Did losing Macdonald hurt the defense?\n")
    
    if post_mac and mac:
        if post_decline > 0.02:
            print("✗✗ YES - SIGNIFICANTLY: The defense clearly declined without Macdonald")
            print("   Seattle got a steal, and the Ravens paid the price")
        elif post_decline > 0:
            print("✗ YES - MODERATELY: There's been some decline, but not catastrophic")
        else:
            print("✓ NO: The defense has maintained or even improved its level")
            print("   Macdonald built a sustainable system")


if __name__ == "__main__":
    main()
