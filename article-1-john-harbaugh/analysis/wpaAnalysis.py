"""
checks how offense defense and special teams contribute to wins
"""

import pandas as pd
from pathlib import Path

def analyze_wpa_by_phase(year):
    """gets wpa numbers for different parts of the game"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\n{'='*80}")
    print(f"Analyzing {year} Win Probability Added by Phase")
    print(f"{'='*80}")
    
    # Read the CSV file
    print(f"Reading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    print(f"Total rows: {len(df):,}")
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    print(f"Regular season rows: {len(df):,}")
    
    # Remove rows where wpa is NaN
    df_wpa = df[df['wpa'].notna()].copy()
    print(f"Rows with WPA data: {len(df_wpa):,}")
    
    # Calculate Offensive WPA (when Ravens have possession)
    offense_wpa = df_wpa[df_wpa['posteam'] == 'BAL']['wpa'].sum()
    
    # Calculate Defensive WPA (when Ravens are on defense)
    # When opponent has ball and loses WP, that's positive for Ravens defense
    defense_wpa = -df_wpa[df_wpa['defteam'] == 'BAL']['wpa'].sum()
    
    # Calculate Special Teams WPA
    # Check if special_teams_play column exists
    if 'special_teams_play' in df_wpa.columns:
        special_teams = df_wpa[
            (df_wpa['special_teams_play'] == 1) & 
            ((df_wpa['posteam'] == 'BAL') | (df_wpa['defteam'] == 'BAL'))
        ].copy()
    else:
        # Alternative: use 'special' column or identify by play_type
        special_teams = df_wpa[
            (df_wpa['special'] == 1) & 
            ((df_wpa['posteam'] == 'BAL') | (df_wpa['defteam'] == 'BAL'))
        ].copy()
    
    # For special teams, positive WPA when Ravens have possession, negative when they don't
    st_offense = special_teams[special_teams['posteam'] == 'BAL']['wpa'].sum()
    st_defense = -special_teams[special_teams['defteam'] == 'BAL']['wpa'].sum()
    special_teams_wpa = st_offense + st_defense
    
    # Adjust offense and defense WPA to exclude special teams
    # (since special teams plays are also counted in offense/defense)
    offense_wpa_adjusted = offense_wpa - st_offense
    defense_wpa_adjusted = defense_wpa - st_defense
    
    print(f"\nRavens WPA by Phase ({year}):")
    print(f"  Offense WPA:       {offense_wpa_adjusted:+.3f}")
    print(f"  Defense WPA:       {defense_wpa_adjusted:+.3f}")
    print(f"  Special Teams WPA: {special_teams_wpa:+.3f}")
    print(f"  Total WPA:         {offense_wpa_adjusted + defense_wpa_adjusted + special_teams_wpa:+.3f}")
    
    return {
        'year': year,
        'offense_wpa': offense_wpa_adjusted,
        'defense_wpa': defense_wpa_adjusted,
        'special_teams_wpa': special_teams_wpa,
        'total_wpa': offense_wpa_adjusted + defense_wpa_adjusted + special_teams_wpa
    }


def main():
    """Analyze WPA by phase for 2008-2011."""
    
    years = [2008, 2009, 2010, 2011]
    results = []
    
    for year in years:
        result = analyze_wpa_by_phase(year)
        if result:
            results.append(result)
    
    # Calculate totals across all years
    total_offense_wpa = sum(r['offense_wpa'] for r in results)
    total_defense_wpa = sum(r['defense_wpa'] for r in results)
    total_st_wpa = sum(r['special_teams_wpa'] for r in results)
    total_wpa = sum(r['total_wpa'] for r in results)
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY: Ravens WPA by Phase (2008-2011)")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['year']}: Offense {result['offense_wpa']:+.3f} | "
              f"Defense {result['defense_wpa']:+.3f} | "
              f"Special Teams {result['special_teams_wpa']:+.3f} | "
              f"Total {result['total_wpa']:+.3f}")
    
    print(f"\n{'='*80}")
    print("TOTALS (2008-2011):")
    print(f"{'='*80}")
    print(f"Offense WPA:       {total_offense_wpa:+.3f}")
    print(f"Defense WPA:       {total_defense_wpa:+.3f}")
    print(f"Special Teams WPA: {total_st_wpa:+.3f}")
    print(f"Total WPA:         {total_wpa:+.3f}")
    
    print(f"\n{'='*80}")
    print("BLOG FORMAT:")
    print(f"{'='*80}")
    print(f"Offense WPA: {total_offense_wpa:+.2f}")
    print(f"Defense WPA: {total_defense_wpa:+.2f}")
    print(f"Special Teams WPA: {total_st_wpa:+.2f}")


if __name__ == "__main__":
    main()
