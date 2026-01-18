"""
looks at 2 minute drill offense
"""

import pandas as pd
from pathlib import Path

def analyze_two_minute_drill(year):
    """gets 2 minute drill stats"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\n{'='*80}")
    print(f"Analyzing {year} Two-Minute Drill Performance")
    print(f"{'='*80}")
    
    # Read the CSV file
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season Ravens offensive plays
    ravens_plays = df[(df['season_type'] == 'REG') & (df['posteam'] == 'BAL')].copy()
    
    print(f"\nTotal Ravens offensive plays: {len(ravens_plays):,}")
    
    # Identify two-minute drill situations
    # A drive qualifies if it starts with 120 seconds (2:00) or less in a half
    # We need to look at the drive start time
    
    # Group by drive to analyze drive-level data
    # Get the first play of each drive to determine drive start conditions
    drives = ravens_plays.groupby(['game_id', 'drive']).agg({
        'half_seconds_remaining': ['first', 'last'],  # Time remaining at start and end of drive
        'qtr': 'first',  # Quarter
        'posteam_score': 'first',  # Score at start
        'defteam_score': 'first',  # Opponent score at start
        'posteam_score_post': 'last',  # Score at end
        'fixed_drive_result': 'first',  # Drive result
        'drive_play_count': 'first',  # Number of plays
        'drive_time_of_possession': 'first',  # Drive duration
        'drive_ended_with_score': 'first',  # Whether drive ended with score
    }).reset_index()
    
    # Flatten column names
    drives.columns = ['game_id', 'drive', 'half_seconds_start', 'half_seconds_end', 
                      'qtr', 'score_start', 'opp_score_start', 'score_end', 
                      'drive_result', 'play_count', 'drive_duration', 'ended_with_score']
    
    # Filter for drives starting with 2:00 or less (120 seconds or less)
    # Only consider drives in Q2 or Q4 (end of halves) or late in Q1/Q3 transitioning to next quarter
    two_min_drives = drives[drives['half_seconds_start'] <= 120].copy()
    
    print(f"Total drives with data: {len(drives):,}")
    print(f"Two-minute drill drives (≤2:00 in half): {len(two_min_drives):,}")
    
    # Calculate points scored on these drives
    two_min_drives['points_scored'] = two_min_drives['score_end'] - two_min_drives['score_start']
    
    # Success = drive ended with points (FG or TD)
    successful_drives = two_min_drives[two_min_drives['points_scored'] > 0]
    
    success_rate = (len(successful_drives) / len(two_min_drives) * 100) if len(two_min_drives) > 0 else 0
    total_points = two_min_drives['points_scored'].sum()
    
    print(f"\nRESULTS:")
    print(f"  Two-minute drill drives: {len(two_min_drives)}")
    print(f"  Successful drives (scored points): {len(successful_drives)}")
    print(f"  Success rate: {success_rate:.1f}%")
    print(f"  Total points scored: {total_points}")
    
    # Breakdown by result type
    print(f"\nDrive results breakdown:")
    if len(two_min_drives) > 0:
        td_drives = two_min_drives[two_min_drives['points_scored'] >= 6]
        fg_drives = two_min_drives[two_min_drives['points_scored'] == 3]
        
        print(f"  Touchdowns: {len(td_drives)} ({len(td_drives)/len(two_min_drives)*100:.1f}%)")
        print(f"  Field goals: {len(fg_drives)} ({len(fg_drives)/len(two_min_drives)*100:.1f}%)")
        print(f"  No score: {len(two_min_drives) - len(successful_drives)} ({(len(two_min_drives) - len(successful_drives))/len(two_min_drives)*100:.1f}%)")
    
    return {
        'year': year,
        'two_min_drives': len(two_min_drives),
        'successful_drives': len(successful_drives),
        'success_rate': success_rate,
        'total_points': total_points,
        'td_count': len(td_drives) if len(two_min_drives) > 0 else 0,
        'fg_count': len(fg_drives) if len(two_min_drives) > 0 else 0
    }


def main():
    """Analyze two-minute drill performance for 2012-2014."""
    
    years = [2012, 2013, 2014]
    results = []
    
    for year in years:
        result = analyze_two_minute_drill(year)
        if result:
            results.append(result)
    
    # Calculate combined totals
    total_two_min_drives = sum(r['two_min_drives'] for r in results)
    total_successful_drives = sum(r['successful_drives'] for r in results)
    combined_success_rate = (total_successful_drives / total_two_min_drives * 100) if total_two_min_drives > 0 else 0
    total_points_all_years = sum(r['total_points'] for r in results)
    total_tds = sum(r['td_count'] for r in results)
    total_fgs = sum(r['fg_count'] for r in results)
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY: Ravens Two-Minute Drill Performance (2012-2014)")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['year']}: {result['successful_drives']}/{result['two_min_drives']} drives successful "
              f"({result['success_rate']:.1f}%) - {result['total_points']} points")
    
    print(f"\n{'='*80}")
    print("COMBINED TOTALS (2012-2014):")
    print(f"{'='*80}")
    print(f"Two-minute drill drives: {total_two_min_drives}")
    print(f"Successful drives: {total_successful_drives}")
    print(f"Combined success rate: {combined_success_rate:.1f}%")
    print(f"Total points scored: {total_points_all_years}")
    print(f"  Touchdowns: {total_tds}")
    print(f"  Field goals: {total_fgs}")
    
    print(f"\n{'='*80}")
    print("BLOG FORMAT:")
    print(f"{'='*80}")
    print(f"Combined success rate (2012-2014): {combined_success_rate:.1f}%")
    print(f"Points scored in final two minutes: {total_points_all_years}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
