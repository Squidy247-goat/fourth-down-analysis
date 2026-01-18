"""
looks at timeouts penalties and 2 minute drills
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_game_management(year):
    """gets game management stuff for one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # ===== TIMEOUT MANAGEMENT =====
    # Get timeout information from the data
    # We'll track timeouts remaining at the end of each quarter
    
    # Get games
    games = df['game_id'].unique()
    num_games = len(games)
    
    timeout_data = {
        'q1_home': [],
        'q1_away': [],
        'q2_home': [],
        'q2_away': [],
        'q3_home': [],
        'q3_away': [],
        'q4_home': [],
        'q4_away': []
    }
    
    for game_id in games:
        game_df = df[df['game_id'] == game_id].copy()
        home_team = game_df['home_team'].iloc[0]
        is_ravens_home = (home_team == 'BAL')
        
        # Get last play of each quarter
        for qtr in [1, 2, 3, 4]:
            qtr_plays = game_df[game_df['qtr'] == qtr]
            if len(qtr_plays) > 0:
                last_play = qtr_plays.iloc[-1]
                
                home_to = last_play['home_timeouts_remaining'] if pd.notna(last_play['home_timeouts_remaining']) else 3
                away_to = last_play['away_timeouts_remaining'] if pd.notna(last_play['away_timeouts_remaining']) else 3
                
                timeout_data[f'q{qtr}_home'].append(home_to)
                timeout_data[f'q{qtr}_away'].append(away_to)
    
    # Calculate Ravens averages
    ravens_to = {}
    for qtr in [1, 2, 3, 4]:
        home_tos = [timeout_data[f'q{qtr}_home'][i] for i in range(len(games)) 
                   if df[df['game_id'] == games[i]]['home_team'].iloc[0] == 'BAL']
        away_tos = [timeout_data[f'q{qtr}_away'][i] for i in range(len(games))
                   if df[df['game_id'] == games[i]]['away_team'].iloc[0] == 'BAL']
        
        all_tos = home_tos + away_tos
        ravens_to[f'q{qtr}'] = np.mean(all_tos) if all_tos else 3.0
    
    # ===== TWO-MINUTE SITUATIONS =====
    # Points scored/allowed in final 2 minutes of each half
    
    # Final 2 minutes of first half (Q2, <= 120 seconds)
    q2_final_2min = df[(df['qtr'] == 2) & (df['quarter_seconds_remaining'] <= 120)].copy()
    
    # Ravens scoring
    ravens_q2_scoring = q2_final_2min[
        (q2_final_2min['posteam'] == 'BAL') & 
        (q2_final_2min['touchdown'] == 1)
    ]
    ravens_q2_tds = len(ravens_q2_scoring) * 7  # Approximate
    
    ravens_q2_fgs = q2_final_2min[
        (q2_final_2min['posteam'] == 'BAL') &
        (q2_final_2min['field_goal_result'] == 'made')
    ]
    ravens_q2_fg_points = len(ravens_q2_fgs) * 3
    
    ravens_2min_first_half_points = ravens_q2_tds + ravens_q2_fg_points
    
    # Ravens defense (points allowed)
    opp_q2_scoring = q2_final_2min[
        (q2_final_2min['defteam'] == 'BAL') &
        (q2_final_2min['touchdown'] == 1)
    ]
    opp_q2_tds = len(opp_q2_scoring) * 7
    
    opp_q2_fgs = q2_final_2min[
        (q2_final_2min['defteam'] == 'BAL') &
        (q2_final_2min['field_goal_result'] == 'made')
    ]
    opp_q2_fg_points = len(opp_q2_fgs) * 3
    
    opp_2min_first_half_points = opp_q2_tds + opp_q2_fg_points
    
    # Final 2 minutes of second half (Q4, <= 120 seconds)
    q4_final_2min = df[(df['qtr'] == 4) & (df['quarter_seconds_remaining'] <= 120)].copy()
    
    ravens_q4_scoring = q4_final_2min[
        (q4_final_2min['posteam'] == 'BAL') &
        (q4_final_2min['touchdown'] == 1)
    ]
    ravens_q4_tds = len(ravens_q4_scoring) * 7
    
    ravens_q4_fgs = q4_final_2min[
        (q4_final_2min['posteam'] == 'BAL') &
        (q4_final_2min['field_goal_result'] == 'made')
    ]
    ravens_q4_fg_points = len(ravens_q4_fgs) * 3
    
    ravens_2min_second_half_points = ravens_q4_tds + ravens_q4_fg_points
    
    # ===== END-OF-GAME SITUATIONS (Winning/Tied, Final 2 Minutes) =====
    # For each game, check if Ravens were winning or tied at 2-minute mark
    endgame_situations = []
    
    for game_id in games:
        game_df = df[df['game_id'] == game_id].copy()
        
        # Find the score at the 2-minute mark of Q4
        two_min_mark = game_df[(game_df['qtr'] == 4) & (game_df['quarter_seconds_remaining'] <= 120)]
        
        if len(two_min_mark) > 0:
            first_play_at_2min = two_min_mark.iloc[0]
            
            # Determine Ravens score vs opponent score
            home_team = game_df['home_team'].iloc[0]
            is_ravens_home = (home_team == 'BAL')
            
            home_score = first_play_at_2min['total_home_score']
            away_score = first_play_at_2min['total_away_score']
            
            if is_ravens_home:
                ravens_score = home_score
                opp_score = away_score
            else:
                ravens_score = away_score
                opp_score = home_score
            
            # Check if winning or tied
            if ravens_score >= opp_score:
                # Get final score to determine if they won
                final_play = game_df.iloc[-1]
                final_home = final_play['total_home_score']
                final_away = final_play['total_away_score']
                
                if is_ravens_home:
                    final_ravens = final_home
                    final_opp = final_away
                else:
                    final_ravens = final_away
                    final_opp = final_home
                
                did_win = final_ravens > final_opp
                points_allowed_after_2min = final_opp - opp_score
                
                endgame_situations.append({
                    'game_id': game_id,
                    'ravens_score_at_2min': ravens_score,
                    'opp_score_at_2min': opp_score,
                    'final_ravens': final_ravens,
                    'final_opp': final_opp,
                    'won': did_win,
                    'points_allowed': points_allowed_after_2min
                })
    
    endgame_count = len(endgame_situations)
    endgame_wins = sum(1 for s in endgame_situations if s['won'])
    endgame_win_pct = (endgame_wins / endgame_count * 100) if endgame_count > 0 else 0
    endgame_points_allowed = np.mean([s['points_allowed'] for s in endgame_situations]) if endgame_situations else 0
    
    # ===== PENALTIES =====
    # Count penalties by Ravens
    ravens_penalties = df[
        (df['penalty_team'] == 'BAL')
    ].copy()
    
    total_penalties = len(ravens_penalties)
    total_penalty_yards = ravens_penalties['penalty_yards'].fillna(0).sum()
    
    penalties_per_game = total_penalties / num_games if num_games > 0 else 0
    penalty_yards_per_game = total_penalty_yards / num_games if num_games > 0 else 0
    
    print(f"  Games: {num_games}")
    print(f"  Timeouts remaining (avg):")
    print(f"    End Q1: {ravens_to['q1']:.2f}, Q2: {ravens_to['q2']:.2f}, Q3: {ravens_to['q3']:.2f}, Q4: {ravens_to['q4']:.2f}")
    print(f"  2-min scoring:")
    print(f"    First half: {ravens_2min_first_half_points} scored, {opp_2min_first_half_points} allowed")
    print(f"    Second half: {ravens_2min_second_half_points} scored")
    print(f"  End-of-game (winning/tied):")
    print(f"    Situations: {endgame_count}, Wins: {endgame_wins}, Win %: {endgame_win_pct:.1f}%")
    print(f"    Avg points allowed: {endgame_points_allowed:.2f}")
    print(f"  Penalties: {penalties_per_game:.1f} per game, {penalty_yards_per_game:.1f} yards per game")
    
    return {
        'year': year,
        'games': num_games,
        'timeouts_q1': ravens_to['q1'],
        'timeouts_q2': ravens_to['q2'],
        'timeouts_q3': ravens_to['q3'],
        'timeouts_q4': ravens_to['q4'],
        'two_min_first_half_scored': ravens_2min_first_half_points,
        'two_min_first_half_allowed': opp_2min_first_half_points,
        'two_min_second_half_scored': ravens_2min_second_half_points,
        'endgame_situations': endgame_count,
        'endgame_wins': endgame_wins,
        'endgame_win_pct': endgame_win_pct,
        'endgame_points_allowed': endgame_points_allowed,
        'penalties_per_game': penalties_per_game,
        'penalty_yards_per_game': penalty_yards_per_game,
        'total_penalties': total_penalties,
        'total_penalty_yards': total_penalty_yards
    }


def main():
    """Analyze game management for 2019-2025."""
    
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    
    print(f"{'='*80}")
    print("GAME MANAGEMENT ANALYSIS (2019-2025)")
    print(f"{'='*80}")
    
    results = []
    
    for year in years:
        result = analyze_game_management(year)
        if result:
            results.append(result)
    
    if not results:
        print("No data available")
        return
    
    # Calculate averages
    avg_to_q1 = np.mean([r['timeouts_q1'] for r in results])
    avg_to_q2 = np.mean([r['timeouts_q2'] for r in results])
    avg_to_q3 = np.mean([r['timeouts_q3'] for r in results])
    avg_to_q4 = np.mean([r['timeouts_q4'] for r in results])
    
    total_games = sum(r['games'] for r in results)
    total_2min_first_half_scored = sum(r['two_min_first_half_scored'] for r in results)
    total_2min_first_half_allowed = sum(r['two_min_first_half_allowed'] for r in results)
    total_2min_second_half_scored = sum(r['two_min_second_half_scored'] for r in results)
    
    avg_2min_first_scored = total_2min_first_half_scored / total_games if total_games > 0 else 0
    avg_2min_first_allowed = total_2min_first_half_allowed / total_games if total_games > 0 else 0
    avg_2min_second_scored = total_2min_second_half_scored / total_games if total_games > 0 else 0
    
    # End-of-game stats
    total_endgame_situations = sum(r['endgame_situations'] for r in results)
    total_endgame_wins = sum(r['endgame_wins'] for r in results)
    overall_endgame_win_pct = (total_endgame_wins / total_endgame_situations * 100) if total_endgame_situations > 0 else 0
    avg_endgame_points_allowed = np.mean([r['endgame_points_allowed'] for r in results if r['endgame_situations'] > 0])
    
    avg_penalties_pg = np.mean([r['penalties_per_game'] for r in results])
    avg_penalty_yards_pg = np.mean([r['penalty_yards_per_game'] for r in results])
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY (2019-2025)")
    print(f"{'='*80}\n")
    
    print(f"Timeout Management:")
    print(f"  End of Q1: {avg_to_q1:.2f} timeouts remaining")
    print(f"  End of Q2: {avg_to_q2:.2f} timeouts remaining")
    print(f"  End of Q3: {avg_to_q3:.2f} timeouts remaining")
    print(f"  End of Q4: {avg_to_q4:.2f} timeouts remaining")
    
    print(f"\nTwo-Minute Situations:")
    print(f"  Points per game (final 2 min, first half): {avg_2min_first_scored:.2f} scored")
    print(f"  Points per game (final 2 min, first half): {avg_2min_first_allowed:.2f} allowed")
    print(f"  Points per game (final 2 min, second half): {avg_2min_second_scored:.2f} scored")
    
    print(f"\nEnd-of-Game (Winning/Tied, Final 2 Minutes):")
    print(f"  Total situations: {total_endgame_situations}")
    print(f"  Wins: {total_endgame_wins}")
    print(f"  Win %: {overall_endgame_win_pct:.1f}%")
    print(f"  Avg points allowed: {avg_endgame_points_allowed:.2f}")
    
    print(f"\nPenalty Discipline:")
    print(f"  Penalties per game: {avg_penalties_pg:.2f}")
    print(f"  Penalty yards per game: {avg_penalty_yards_pg:.1f}")
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("2.4 Game Management and Clock Control\n")
    
    print("Timeout Management\n")
    print("Average Timeouts Remaining by Quarter:")
    print(f"End of Q1: {avg_to_q1:.2f}")
    print(f"End of Q2: {avg_to_q2:.2f}")
    print(f"End of Q3: {avg_to_q3:.2f}")
    print(f"End of Q4: {avg_to_q4:.2f}")
    print("League average: [Data not available - Ravens only dataset]")
    
    print(f"\nTwo-Minute Situations")
    print("Points Scored (Final 2 Minutes of Half):")
    print(f"2019-2025 average: {avg_2min_first_scored:.2f} points per game (first half)")
    print(f"2019-2025 average: {avg_2min_second_scored:.2f} points per game (second half)")
    print("League average: [Data not available - Ravens only dataset]")
    
    print(f"\nPoints Allowed (Final 2 Minutes of Half):")
    print(f"2019-2025 average: {avg_2min_first_allowed:.2f} points per game")
    print("League average: [Data not available - Ravens only dataset]")
    
    print(f"\nEnd of Game (Winning/Tied, Final 2 Minutes):")
    print(f"Win %: {overall_endgame_win_pct:.1f}% ({total_endgame_wins}/{total_endgame_situations})")
    print(f"Points allowed: {avg_endgame_points_allowed:.2f}")
    
    print(f"\nPenalty Discipline:")
    print(f"Penalties per game (2019-2025): {avg_penalties_pg:.2f}")
    print(f"Penalty yards per game: {avg_penalty_yards_pg:.1f}")
    print("League averages: [Data not available - Ravens only dataset]")
    
    print("\nNote: Challenge success rate and end-of-game win % require more detailed analysis")
    print("of specific game situations not readily available in play-by-play data.")
    
    # Analysis and interpretation
    print(f"\n{'='*80}")
    print("ANALYSIS & INTERPRETATION")
    print(f"{'='*80}\n")
    
    print("Timeout Management:")
    if avg_to_q2 < 1.5:
        print("✗ POOR: Consistently burning timeouts before halftime")
    elif avg_to_q2 < 2.0:
        print("◐ AVERAGE: Some timeout waste, but manageable")
    else:
        print("✓ GOOD: Generally preserves timeouts for two-minute drill")
    
    if avg_to_q4 < 1.0:
        print("✗ POOR: Rarely has timeouts available in crunch time")
    elif avg_to_q4 < 1.5:
        print("◐ AVERAGE: Sometimes short on timeouts late")
    else:
        print("✓ GOOD: Usually has timeouts available for end of game")
    
    print(f"\nTwo-Minute Offense:")
    total_2min_scoring = avg_2min_first_scored + avg_2min_second_scored
    if total_2min_scoring > 3.0:
        print(f"✓✓ EXCELLENT: {total_2min_scoring:.2f} points per game in two-minute situations")
    elif total_2min_scoring > 2.0:
        print(f"✓ GOOD: {total_2min_scoring:.2f} points per game")
    else:
        print(f"◐ AVERAGE: {total_2min_scoring:.2f} points per game")
    
    print(f"\nTwo-Minute Defense:")
    if avg_2min_first_allowed < 1.0:
        print(f"✓✓ EXCELLENT: Only {avg_2min_first_allowed:.2f} PPG allowed before halftime")
    elif avg_2min_first_allowed < 1.5:
        print(f"✓ GOOD: {avg_2min_first_allowed:.2f} PPG allowed")
    else:
        print(f"✗ POOR: {avg_2min_first_allowed:.2f} PPG allowed - giving up easy scores")
    
    print(f"\nEnd-of-Game Execution (Winning/Tied):")
    if overall_endgame_win_pct > 90:
        print(f"✓✓ ELITE: {overall_endgame_win_pct:.1f}% win rate - excellent at closing games")
    elif overall_endgame_win_pct > 85:
        print(f"✓ STRONG: {overall_endgame_win_pct:.1f}% win rate - good closer")
    elif overall_endgame_win_pct > 80:
        print(f"◐ AVERAGE: {overall_endgame_win_pct:.1f}% win rate - occasional blown leads")
    else:
        print(f"✗ POOR: {overall_endgame_win_pct:.1f}% win rate - struggles to close games")
    
    if avg_endgame_points_allowed < 1.0:
        print(f"✓ Defense locks down: Only {avg_endgame_points_allowed:.2f} points allowed in final 2 min")
    elif avg_endgame_points_allowed < 2.0:
        print(f"◐ Moderate defense: {avg_endgame_points_allowed:.2f} points allowed")
    else:
        print(f"✗ Vulnerable: {avg_endgame_points_allowed:.2f} points allowed - gives opponents chances")
    
    print(f"\nPenalty Discipline:")
    if avg_penalties_pg < 5.0:
        print(f"✓✓ EXCELLENT: {avg_penalties_pg:.2f} penalties per game (very disciplined)")
    elif avg_penalties_pg < 6.0:
        print(f"✓ GOOD: {avg_penalties_pg:.2f} penalties per game")
    elif avg_penalties_pg < 7.0:
        print(f"◐ AVERAGE: {avg_penalties_pg:.2f} penalties per game")
    else:
        print(f"✗ POOR: {avg_penalties_pg:.2f} penalties per game (undisciplined)")
    
    # Year-by-year breakdown
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR BREAKDOWN")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['year']}:")
        print(f"  Timeouts: Q1={result['timeouts_q1']:.2f}, Q2={result['timeouts_q2']:.2f}, "
              f"Q3={result['timeouts_q3']:.2f}, Q4={result['timeouts_q4']:.2f}")
        print(f"  2-min: {result['two_min_first_half_scored']} scored, "
              f"{result['two_min_first_half_allowed']} allowed (1st half)")
        print(f"  End-game: {result['endgame_win_pct']:.1f}% win rate "
              f"({result['endgame_wins']}/{result['endgame_situations']}), "
              f"{result['endgame_points_allowed']:.2f} pts allowed")
        print(f"  Penalties: {result['penalties_per_game']:.1f}/game, "
              f"{result['penalty_yards_per_game']:.1f} yards/game")
        print()


if __name__ == "__main__":
    main()
