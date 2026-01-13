"""
makes a table showing how good ravens are at 2 minute drills
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def analyze_clock_management(year):
    """get stats for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    games = df['game_id'].unique()
    num_games = len(games)
    
    if num_games == 0:
        return None
    
    # ===== TWO-MINUTE SITUATIONS (First Half) =====
    q2_final_2min = df[(df['qtr'] == 2) & (df['quarter_seconds_remaining'] <= 120)].copy()
    
    # Count drives ending in scores
    ravens_q2_scoring_plays = q2_final_2min[
        (q2_final_2min['posteam'] == 'BAL') & 
        ((q2_final_2min['touchdown'] == 1) | (q2_final_2min['field_goal_result'] == 'made'))
    ]
    ravens_q2_drives_with_scores = ravens_q2_scoring_plays['drive'].nunique() if len(ravens_q2_scoring_plays) > 0 else 0
    
    # Total two-minute drives in first half
    q2_ravens_drives = q2_final_2min[q2_final_2min['posteam'] == 'BAL']['drive'].nunique()
    
    q2_success_rate = (ravens_q2_drives_with_scores / q2_ravens_drives * 100) if q2_ravens_drives > 0 else 0
    
    # ===== TWO-MINUTE SITUATIONS (Second Half) =====
    q4_final_2min = df[(df['qtr'] == 4) & (df['quarter_seconds_remaining'] <= 120)].copy()
    
    ravens_q4_scoring_plays = q4_final_2min[
        (q4_final_2min['posteam'] == 'BAL') &
        ((q4_final_2min['touchdown'] == 1) | (q4_final_2min['field_goal_result'] == 'made'))
    ]
    ravens_q4_drives_with_scores = ravens_q4_scoring_plays['drive'].nunique() if len(ravens_q4_scoring_plays) > 0 else 0
    
    q4_ravens_drives = q4_final_2min[q4_final_2min['posteam'] == 'BAL']['drive'].nunique()
    
    q4_success_rate = (ravens_q4_drives_with_scores / q4_ravens_drives * 100) if q4_ravens_drives > 0 else 0
    
    # ===== END-OF-GAME SITUATIONS (Winning/Tied, Final 2 Minutes) =====
    endgame_situations = []
    
    for game_id in games:
        game_df = df[df['game_id'] == game_id].copy()
        
        # Find the score at the 2-minute mark of Q4
        two_min_mark = game_df[(game_df['qtr'] == 4) & (game_df['quarter_seconds_remaining'] <= 120)]
        
        if len(two_min_mark) > 0:
            first_play_at_2min = two_min_mark.iloc[0]
            
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
                endgame_situations.append({'won': did_win})
    
    endgame_count = len(endgame_situations)
    endgame_wins = sum(1 for s in endgame_situations if s['won'])
    endgame_win_pct = (endgame_wins / endgame_count * 100) if endgame_count > 0 else 0
    
    # ===== TIMEOUT CONSERVATION =====
    timeout_q2 = []
    timeout_q4 = []
    
    for game_id in games:
        game_df = df[df['game_id'] == game_id].copy()
        home_team = game_df['home_team'].iloc[0]
        is_ravens_home = (home_team == 'BAL')
        
        # Q2 end
        q2_plays = game_df[game_df['qtr'] == 2]
        if len(q2_plays) > 0:
            last_q2 = q2_plays.iloc[-1]
            if is_ravens_home:
                to = last_q2['home_timeouts_remaining']
            else:
                to = last_q2['away_timeouts_remaining']
            if pd.notna(to):
                timeout_q2.append(to)
        
        # Q4 end
        q4_plays = game_df[game_df['qtr'] == 4]
        if len(q4_plays) > 0:
            last_q4 = q4_plays.iloc[-1]
            if is_ravens_home:
                to = last_q4['home_timeouts_remaining']
            else:
                to = last_q4['away_timeouts_remaining']
            if pd.notna(to):
                timeout_q4.append(to)
    
    avg_to_q2 = np.mean(timeout_q2) if timeout_q2 else 0
    avg_to_q4 = np.mean(timeout_q4) if timeout_q4 else 0
    
    return {
        'year': year,
        'games': num_games,
        'q2_2min_drives': q2_ravens_drives,
        'q2_success_rate': q2_success_rate,
        'q4_2min_drives': q4_ravens_drives,
        'q4_success_rate': q4_success_rate,
        'endgame_situations': endgame_count,
        'endgame_wins': endgame_wins,
        'endgame_win_pct': endgame_win_pct,
        'avg_to_q2': avg_to_q2,
        'avg_to_q4': avg_to_q4
    }


def create_clock_management_table():
    """Create a visual table showing clock management success rates."""
    
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    
    print("Analyzing clock management (2019-2025)...")
    
    results = []
    for year in years:
        result = analyze_clock_management(year)
        if result:
            results.append(result)
            print(f"  {year}: ✓")
    
    if not results:
        print("No data available")
        return
    
    # Calculate overall metrics
    total_q2_drives = sum(r['q2_2min_drives'] for r in results)
    total_q4_drives = sum(r['q4_2min_drives'] for r in results)
    
    # Weighted average success rates
    q2_weighted_success = sum(r['q2_success_rate'] * r['q2_2min_drives'] for r in results) / total_q2_drives if total_q2_drives > 0 else 0
    q4_weighted_success = sum(r['q4_success_rate'] * r['q4_2min_drives'] for r in results) / total_q4_drives if total_q4_drives > 0 else 0
    
    total_endgame = sum(r['endgame_situations'] for r in results)
    total_endgame_wins = sum(r['endgame_wins'] for r in results)
    overall_endgame_pct = (total_endgame_wins / total_endgame * 100) if total_endgame > 0 else 0
    
    avg_to_q2 = np.mean([r['avg_to_q2'] for r in results])
    avg_to_q4 = np.mean([r['avg_to_q4'] for r in results])
    
    # Create the table
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Define table data
    table_data = [
        ['Critical Scenario', 'Success Rate', 'Sample Size', 'Performance'],
        ['', '', '', ''],
        ['Two-Minute Drill (1st Half)', f'{q2_weighted_success:.1f}%', f'{total_q2_drives} drives', 
         '✓ Strong' if q2_weighted_success >= 50 else '◐ Average'],
        ['Two-Minute Drill (2nd Half)', f'{q4_weighted_success:.1f}%', f'{total_q4_drives} drives',
         '✓ Strong' if q4_weighted_success >= 50 else '◐ Average'],
        ['Closing Games (Winning/Tied)', f'{overall_endgame_pct:.1f}%', f'{total_endgame} situations',
         '✓✓ Elite' if overall_endgame_pct >= 90 else '✓ Strong' if overall_endgame_pct >= 85 else '◐ Average'],
        ['', '', '', ''],
        ['Timeout Conservation', '', '', ''],
        ['Timeouts at End of Q2', f'{avg_to_q2:.2f} avg', f'{len(results)} seasons',
         '✓ Good' if avg_to_q2 >= 2.0 else '◐ Average'],
        ['Timeouts at End of Q4', f'{avg_to_q4:.2f} avg', f'{len(results)} seasons',
         '✓ Good' if avg_to_q4 >= 1.5 else '◐ Average']
    ]
    
    # Create table
    table = ax.table(cellText=table_data, cellLoc='left', loc='center',
                     colWidths=[0.35, 0.2, 0.25, 0.2])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style header row
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#1f77b4')
        cell.set_text_props(weight='bold', color='white', fontsize=12)
    
    # Style section separator rows
    for row_idx in [1, 5, 6]:
        for col_idx in range(4):
            cell = table[(row_idx, col_idx)]
            if row_idx == 6:  # "Timeout Conservation" header
                cell.set_facecolor('#e8e8e8')
                cell.set_text_props(weight='bold', fontsize=11)
            else:
                cell.set_facecolor('#f5f5f5')
    
    # Alternate row colors for data rows
    data_rows = [2, 3, 4, 7, 8]
    for idx, row in enumerate(data_rows):
        for col in range(4):
            cell = table[(row, col)]
            if idx % 2 == 0:
                cell.set_facecolor('#ffffff')
            else:
                cell.set_facecolor('#f9f9f9')
    
    # Add title and subtitle
    plt.suptitle('Clock Management Success Rates - Critical Scenarios', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.title('Baltimore Ravens (2019-2025)', fontsize=12, style='italic', pad=20)
    
    # Add footnote
    fig.text(0.5, 0.02, 
             'Success Rate: Two-minute drives ending in points (FG or TD) | Closing Games: Win% when winning/tied at 2-min mark',
             ha='center', fontsize=9, style='italic', color='#666666')
    
    # save the table
    output_dir = Path(__file__).parent.parent / "output" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "clockManagementTable.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Table saved to: {output_path}")
    
    plt.close()
    
    # Print summary to console
    print(f"\n{'='*70}")
    print("CLOCK MANAGEMENT SUCCESS RATES SUMMARY")
    print(f"{'='*70}\n")
    print(f"Two-Minute Drill (1st Half):  {q2_weighted_success:5.1f}%  ({total_q2_drives} drives)")
    print(f"Two-Minute Drill (2nd Half):  {q4_weighted_success:5.1f}%  ({total_q4_drives} drives)")
    print(f"Closing Games (Win/Tied):      {overall_endgame_pct:5.1f}%  ({total_endgame_wins}/{total_endgame})")
    print(f"\nTimeout Conservation:")
    print(f"  End of Q2: {avg_to_q2:.2f} timeouts remaining")
    print(f"  End of Q4: {avg_to_q4:.2f} timeouts remaining")
    print(f"\n{'='*70}")


if __name__ == "__main__":
    create_clock_management_table()
