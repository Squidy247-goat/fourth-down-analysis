"""
looks at 3rd down defense
"""

import pandas as pd
from pathlib import Path

def analyze_third_down_defense(year):
    """gets 3rd down defense numbers"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\n{'='*80}")
    print(f"Analyzing {year} Third-Down Defense")
    print(f"{'='*80}")
    
    print(f"Reading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    print(f"Total rows: {len(df):,}")
    
    # filtering for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    print(f"Regular season rows: {len(df):,}")
    
    # only third down plays
    third_downs = df[df['down'] == 3].copy()
    print(f"Total third-down plays (regular season): {len(third_downs):,}")
    
    team_stats = {}
    
    for team in df['defteam'].dropna().unique():
        # all third-down plays where Ravens were on defense
        team_def = third_downs[third_downs['defteam'] == team].copy()
        
        if len(team_def) == 0:
            continue
        
        # Count conversions (first down or touchdown)
        # A conversion happens when the offense gets a first down or scores
        conversions = team_def[
            (team_def['first_down'] == 1) | 
            (team_def['touchdown'] == 1)
        ]
        
        total_attempts = len(team_def)
        total_conversions = len(conversions)
        conversion_pct = (total_conversions / total_attempts * 100) if total_attempts > 0 else 0
        
        team_stats[team] = {
            'team': team,
            'attempts': total_attempts,
            'conversions': total_conversions,
            'conversion_pct': conversion_pct
        }
    
    # Get Ravens stats
    ravens_stats = team_stats.get('BAL', {})
    
    if not ravens_stats:
        print(f"WARNING: No Ravens defensive data found for {year}")
        return None
    
    print(f"\nRavens Third-Down Defense ({year}):")
    print(f"  Attempts: {ravens_stats['attempts']}")
    print(f"  Conversions Allowed: {ravens_stats['conversions']}")
    print(f"  Conversion % Allowed: {ravens_stats['conversion_pct']:.1f}%")
    
    # Sort teams by conversion percentage (ascending = better defense)
    sorted_teams = sorted(team_stats.values(), key=lambda x: x['conversion_pct'])
    
    # Find Ravens rank (1 = best defense = lowest conversion rate allowed)
    ravens_rank = None
    for idx, team in enumerate(sorted_teams, 1):
        if team['team'] == 'BAL':
            ravens_rank = idx
            break
    
    print(f"  NFL Rank: {ravens_rank} out of {len(sorted_teams)} teams")
    
    # Show top 5 defenses for context
    print(f"\nTop 5 Third-Down Defenses in {year}:")
    for idx, team in enumerate(sorted_teams[:5], 1):
        marker = " ← RAVENS" if team['team'] == 'BAL' else ""
        print(f"  {idx}. {team['team']}: {team['conversion_pct']:.1f}%{marker}")
    
    return {
        'year': year,
        'conversion_pct': ravens_stats['conversion_pct'],
        'rank': ravens_rank,
        'total_teams': len(sorted_teams),
        'attempts': ravens_stats['attempts'],
        'conversions': ravens_stats['conversions']
    }


def main():
    """Analyze third-down defense for 2008-2011."""
    
    years = [2008, 2009, 2010, 2011]
    results = []
    
    for year in years:
        result = analyze_third_down_defense(year)
        if result:
            results.append(result)
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY: Ravens Third-Down Defense (2008-2011)")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['year']}: {result['conversion_pct']:.1f}% (Rank: {result['rank']} of {result['total_teams']})")
    
    print(f"\n{'='*80}")
    print("BLOG FORMAT:")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"{result['year']}: {result['conversion_pct']:.1f}% (Rank: {result['rank']})")


if __name__ == "__main__":
    main()
