"""
compares 2012 regular season vs playoff offense
"""

import pandas as pd
from pathlib import Path

def analyze_2012_epa():
    """gets epa for 2012 regular season and playoffs"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / "pbpRavens2012.csv"
    
    print(f"\n{'='*80}")
    print(f"Analyzing 2012 Baltimore Ravens EPA: Regular Season vs Playoffs")
    print(f"{'='*80}")
    
    # Read the CSV file
    print(f"\nReading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    print(f"Total rows in dataset: {len(df):,}")
    
    # Filter for offensive plays where Ravens have possession and EPA is not null
    # We want plays where Ravens are on offense (posteam == 'BAL')
    # and where EPA exists (not NaN)
    offensive_plays = df[(df['posteam'] == 'BAL') & (df['epa'].notna())].copy()
    
    print(f"Total offensive plays with EPA data: {len(offensive_plays):,}")
    
    # Separate regular season and playoff data
    regular_season = offensive_plays[offensive_plays['season_type'] == 'REG'].copy()
    playoffs = offensive_plays[offensive_plays['season_type'] == 'POST'].copy()
    
    print(f"\nRegular season offensive plays: {len(regular_season):,}")
    print(f"Playoff offensive plays: {len(playoffs):,}")
    
    # Calculate EPA per play
    regular_season_epa_per_play = regular_season['epa'].mean()
    playoff_epa_per_play = playoffs['epa'].mean()
    difference = playoff_epa_per_play - regular_season_epa_per_play
    
    # Calculate total EPA as well (for context)
    regular_season_total_epa = regular_season['epa'].sum()
    playoff_total_epa = playoffs['epa'].sum()
    
    print(f"\n{'='*80}")
    print("RESULTS:")
    print(f"{'='*80}")
    print(f"\n2012 REGULAR SEASON:")
    print(f"  Offensive plays: {len(regular_season):,}")
    print(f"  Total offensive EPA: {regular_season_total_epa:+.2f}")
    print(f"  Offensive EPA per play: {regular_season_epa_per_play:+.4f}")
    
    print(f"\n2012 PLAYOFFS:")
    print(f"  Offensive plays: {len(playoffs):,}")
    print(f"  Total offensive EPA: {playoff_total_epa:+.2f}")
    print(f"  Offensive EPA per play: {playoff_epa_per_play:+.4f}")
    
    print(f"\nDIFFERENCE (Playoffs - Regular Season):")
    print(f"  EPA per play improvement: {difference:+.4f}")
    print(f"  Percentage improvement: {(difference / abs(regular_season_epa_per_play) * 100):+.1f}%")
    
    print(f"\n{'='*80}")
    print("BLOG FORMAT:")
    print(f"{'='*80}")
    print(f"2012 Regular Season Offensive EPA/play: {regular_season_epa_per_play:+.3f}")
    print(f"2012 Playoff Offensive EPA/play: {playoff_epa_per_play:+.3f}")
    print(f"Difference: {difference:+.3f}")
    print(f"{'='*80}\n")
    
    # Additional breakdown by play type for context
    print(f"\n{'='*80}")
    print("ADDITIONAL CONTEXT - EPA by Play Type:")
    print(f"{'='*80}")
    
    # Regular season breakdown
    print(f"\nREGULAR SEASON:")
    reg_pass = regular_season[regular_season['pass'] == 1]
    reg_rush = regular_season[regular_season['rush'] == 1]
    
    if len(reg_pass) > 0:
        print(f"  Passing EPA/play: {reg_pass['epa'].mean():+.4f} ({len(reg_pass):,} plays)")
    if len(reg_rush) > 0:
        print(f"  Rushing EPA/play: {reg_rush['epa'].mean():+.4f} ({len(reg_rush):,} plays)")
    
    # Playoff breakdown
    print(f"\nPLAYOFFS:")
    playoff_pass = playoffs[playoffs['pass'] == 1]
    playoff_rush = playoffs[playoffs['rush'] == 1]
    
    if len(playoff_pass) > 0:
        print(f"  Passing EPA/play: {playoff_pass['epa'].mean():+.4f} ({len(playoff_pass):,} plays)")
    if len(playoff_rush) > 0:
        print(f"  Rushing EPA/play: {playoff_rush['epa'].mean():+.4f} ({len(playoff_rush):,} plays)")
    
    return {
        'regular_season_epa_per_play': regular_season_epa_per_play,
        'playoff_epa_per_play': playoff_epa_per_play,
        'difference': difference
    }


if __name__ == "__main__":
    analyze_2012_epa()
