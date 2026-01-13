"""
looks at how dominant ravens were in regular season with lamar
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_point_differential(year):
    """gets point differential for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nReading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Get the final score for each game (last play of each game has the final scores)
    games = df.groupby('game_id').last().reset_index()
    
    # Calculate Ravens points scored and allowed
    ravens_points_scored = 0
    ravens_points_allowed = 0
    wins = 0
    losses = 0
    ties = 0
    
    for _, game in games.iterrows():
        home_team = game['home_team']
        away_team = game['away_team']
        home_score = game['home_score']
        away_score = game['away_score']
        
        # Determine if Ravens were home or away
        if home_team == 'BAL':
            ravens_score = home_score
            opponent_score = away_score
        elif away_team == 'BAL':
            ravens_score = away_score
            opponent_score = home_score
        else:
            continue
        
        ravens_points_scored += ravens_score
        ravens_points_allowed += opponent_score
        
        # Count wins/losses
        if ravens_score > opponent_score:
            wins += 1
        elif ravens_score < opponent_score:
            losses += 1
        else:
            ties += 1
    
    total_games = wins + losses + ties
    point_diff = ravens_points_scored - ravens_points_allowed
    ppg = ravens_points_scored / total_games if total_games > 0 else 0
    ppg_allowed = ravens_points_allowed / total_games if total_games > 0 else 0
    
    print(f"\n{year} Ravens Regular Season:")
    print(f"  Record: {wins}-{losses}" + (f"-{ties}" if ties > 0 else ""))
    print(f"  Points Scored: {int(ravens_points_scored)}")
    print(f"  Points Allowed: {int(ravens_points_allowed)}")
    print(f"  Point Differential: {point_diff:+.0f}")
    print(f"  PPG: {ppg:.1f}")
    print(f"  PPG Allowed: {ppg_allowed:.1f}")
    
    return {
        'year': year,
        'wins': wins,
        'losses': losses,
        'ties': ties,
        'points_scored': int(ravens_points_scored),
        'points_allowed': int(ravens_points_allowed),
        'point_diff': int(point_diff),
        'ppg': ppg,
        'ppg_allowed': ppg_allowed,
        'games': total_games
    }


def calculate_expected_wins(points_scored, points_allowed, games_played):
    """
    Calculate expected wins using the Pythagorean expectation formula
    Formula: Expected Win% = Points_Scored^2.37 / (Points_Scored^2.37 + Points_Allowed^2.37)
    The exponent 2.37 is commonly used for NFL
    """
    
    if points_allowed == 0:
        return games_played
    
    exponent = 2.37
    expected_win_pct = (points_scored ** exponent) / (points_scored ** exponent + points_allowed ** exponent)
    expected_wins = expected_win_pct * games_played
    
    return expected_wins


def analyze_expected_vs_actual_wins(year):
    """
    Compare expected wins (based on point differential) to actual wins
    """
    
    result = analyze_point_differential(year)
    
    if not result:
        return None
    
    expected_wins = calculate_expected_wins(
        result['points_scored'],
        result['points_allowed'],
        result['games']
    )
    
    actual_wins = result['wins']
    actual_losses = result['losses']
    difference = actual_wins - expected_wins
    
    print(f"\n{'='*80}")
    print(f"{year} Expected vs Actual Wins:")
    print(f"{'='*80}")
    print(f"Expected Wins: {expected_wins:.1f}")
    print(f"Actual Record: {actual_wins}-{actual_losses}")
    print(f"Difference: {difference:+.1f} wins")
    
    if difference > 0:
        print(f"Analysis: Ravens OUTPERFORMED expectations by {difference:.1f} wins")
    elif difference < 0:
        print(f"Analysis: Ravens UNDERPERFORMED expectations by {abs(difference):.1f} wins")
    else:
        print(f"Analysis: Ravens performed exactly as expected")
    
    return {
        'year': year,
        'expected_wins': expected_wins,
        'actual_wins': actual_wins,
        'actual_losses': actual_losses,
        'difference': difference,
        'point_diff': result['point_diff']
    }


def main():
    """Main analysis function"""
    
    print(f"{'='*80}")
    print("REGULAR SEASON DOMINANCE ANALYSIS - LAMAR JACKSON ERA")
    print(f"{'='*80}")
    
    # 1. Analyze point differential for key years
    print(f"\n{'='*80}")
    print("PART 1: POINT DIFFERENTIAL ANALYSIS")
    print(f"{'='*80}")
    
    years_to_analyze = [2019, 2020, 2021, 2023, 2024]
    point_diff_results = []
    
    for year in years_to_analyze:
        result = analyze_point_differential(year)
        if result:
            point_diff_results.append(result)
    
    # 2. Analyze expected vs actual wins
    print(f"\n{'='*80}")
    print("PART 2: EXPECTED WINS VS ACTUAL WINS")
    print(f"{'='*80}")
    
    # Key years for expected wins analysis
    expected_wins_analysis = []
    
    for year in [2019, 2020, 2023]:
        result = analyze_expected_vs_actual_wins(year)
        if result:
            expected_wins_analysis.append(result)
    
    # 3. Print Blog-Ready Output
    print(f"\n{'='*80}")
    print("BLOG-READY FORMAT:")
    print(f"{'='*80}\n")
    
    print("Point Differential:")
    print("Note: NFL rankings would need to be calculated from league-wide data")
    for result in point_diff_results:
        print(f"{result['year']}: {result['point_diff']:+d} (Rank: [LOOKUP REQUIRED])")
    
    print("\nExpected Wins vs Actual Wins (Based on Point Differential):")
    for result in expected_wins_analysis:
        print(f"{result['year']}: Expected {result['expected_wins']:.1f}, Actual {result['actual_wins']}-{result['actual_losses']}")
    
    # 4. Additional Context
    print(f"\n{'='*80}")
    print("ADDITIONAL INSIGHTS:")
    print(f"{'='*80}")
    
    # Calculate average point differential across Lamar era
    avg_point_diff = sum(r['point_diff'] for r in point_diff_results) / len(point_diff_results)
    
    print(f"\nLamar Era Average (2019-2024, excluding 2022):")
    print(f"  Average Point Differential: {avg_point_diff:+.1f}")
    
    # Analyze over/underperformance trend
    print(f"\nExpected vs Actual Performance:")
    total_difference = sum(r['difference'] for r in expected_wins_analysis)
    avg_difference = total_difference / len(expected_wins_analysis) if expected_wins_analysis else 0
    
    if avg_difference > 0:
        print(f"  On average, Ravens OUTPERFORMED expectations by {avg_difference:.1f} wins")
    else:
        print(f"  On average, Ravens UNDERPERFORMED expectations by {abs(avg_difference):.1f} wins")
    
    # Best and worst point differential years
    best_year = max(point_diff_results, key=lambda x: x['point_diff'])
    print(f"\nBest Point Differential: {best_year['year']} ({best_year['point_diff']:+d})")
    
    # Points per game analysis
    print(f"\nOffensive Firepower (Points Per Game):")
    for result in point_diff_results:
        print(f"  {result['year']}: {result['ppg']:.1f} PPG (Allowed: {result['ppg_allowed']:.1f})")
    
    # Win-Loss records
    print(f"\nWin-Loss Records:")
    for result in point_diff_results:
        ties_str = f"-{result['ties']}" if result.get('ties', 0) > 0 else ""
        print(f"  {result['year']}: {result['wins']}-{result['losses']}{ties_str}")


if __name__ == "__main__":
    main()
