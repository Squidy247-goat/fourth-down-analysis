"""
checks deep balls and play action usage
"""

import pandas as pd
from pathlib import Path

def analyze_passing_style(year):
    """gets passing style stats for one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\n{'='*80}")
    print(f"Analyzing {year} Passing Style")
    print(f"{'='*80}")
    
    # Read the CSV file
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season Ravens offensive pass attempts
    # Include complete and incomplete passes, exclude spikes/kneels
    passes = df[
        (df['season_type'] == 'REG') &
        (df['posteam'] == 'BAL') &
        (df['pass_attempt'] == 1) &
        (df['qb_spike'].isna() | (df['qb_spike'] == 0)) &
        (df['qb_kneel'].isna() | (df['qb_kneel'] == 0))
    ].copy()
    
    total_pass_attempts = len(passes)
    
    print(f"\nTotal pass attempts: {total_pass_attempts}")
    
    # DEEP BALL ANALYSIS
    # Filter for passes with air_yards data
    passes_with_air_yards = passes[passes['air_yards'].notna()].copy()
    
    # Deep balls = air_yards >= 20
    deep_balls = passes_with_air_yards[passes_with_air_yards['air_yards'] >= 20].copy()
    
    deep_ball_attempts = len(deep_balls)
    deep_ball_percentage = (deep_ball_attempts / len(passes_with_air_yards) * 100) if len(passes_with_air_yards) > 0 else 0
    
    print(f"\nDEEP BALL ANALYSIS (air yards >= 20):")
    print(f"  Passes with air yards data: {len(passes_with_air_yards)}")
    print(f"  Deep ball attempts: {deep_ball_attempts}")
    print(f"  Deep ball percentage: {deep_ball_percentage:.1f}%")
    
    # Additional deep ball context
    if len(deep_balls) > 0:
        deep_ball_completions = len(deep_balls[deep_balls['complete_pass'] == 1])
        deep_ball_comp_pct = (deep_ball_completions / deep_ball_attempts * 100)
        deep_ball_epa = deep_balls['epa'].mean()
        
        print(f"  Deep ball completion %: {deep_ball_comp_pct:.1f}%")
        print(f"  Deep ball EPA/attempt: {deep_ball_epa:+.3f}")
    
    # PLAY-ACTION ANALYSIS
    # Check if pass_location column exists (some datasets have this)
    if 'pass_location' in passes.columns:
        # Filter for passes with play-action data
        # Note: nflfastR doesn't have a direct play_action column
        # We'll need to check what columns are available
        pass
    
    # Look for alternative play-action indicators
    # Check column names
    available_cols = passes.columns.tolist()
    
    # Many nflfastR datasets don't include play-action flags
    # We can try to infer from play description or check if column exists
    play_action_passes = None
    
    # Check if there's any play-action related column
    pa_related_cols = [col for col in available_cols if 'action' in col.lower() or 'fake' in col.lower()]
    
    print(f"\nPLAY-ACTION ANALYSIS:")
    
    # Try to identify play-action from description
    # Common play-action keywords: "play action", "fake", "PA"
    passes_with_desc = passes[passes['desc'].notna()].copy()
    
    # Look for play-action indicators in play description
    play_action_keywords = ['play action', 'Play action', 'PLAY ACTION', 'play-action']
    
    play_action_passes = passes_with_desc[
        passes_with_desc['desc'].str.contains('|'.join(play_action_keywords), case=False, na=False)
    ].copy()
    
    # Standard dropback = all other passes (not play-action)
    standard_dropback_passes = passes_with_desc[
        ~passes_with_desc['desc'].str.contains('|'.join(play_action_keywords), case=False, na=False)
    ].copy()
    
    play_action_attempts = len(play_action_passes)
    play_action_percentage = (play_action_attempts / len(passes_with_desc) * 100) if len(passes_with_desc) > 0 else 0
    
    print(f"  Total passes with description: {len(passes_with_desc)}")
    print(f"  Play-action attempts: {play_action_attempts}")
    print(f"  Play-action percentage: {play_action_percentage:.1f}%")
    
    # EPA comparison
    if len(play_action_passes) > 0:
        pa_epa = play_action_passes['epa'].mean()
        print(f"  Play-action EPA/attempt: {pa_epa:+.3f}")
    else:
        pa_epa = None
    
    if len(standard_dropback_passes) > 0:
        standard_epa = standard_dropback_passes['epa'].mean()
        print(f"  Standard dropback EPA/attempt: {standard_epa:+.3f}")
    else:
        standard_epa = None
    
    if pa_epa is not None and standard_epa is not None:
        print(f"  Difference: {pa_epa - standard_epa:+.3f}")
    
    return {
        'year': year,
        'total_pass_attempts': total_pass_attempts,
        'deep_ball_attempts': deep_ball_attempts,
        'deep_ball_percentage': deep_ball_percentage,
        'play_action_attempts': play_action_attempts,
        'play_action_percentage': play_action_percentage,
        'play_action_epa': pa_epa,
        'standard_dropback_epa': standard_epa
    }


def calculate_league_average_deep_balls(years):
    """
    Calculate league average deep ball percentage.
    Note: This would require all NFL team data, not just Ravens.
    For now, we'll note that typical NFL average is around 10-12% based on historical data.
    """
    print(f"\n{'='*80}")
    print("LEAGUE AVERAGE CONTEXT:")
    print(f"{'='*80}")
    print("\nNote: Full league data not available in current dataset.")
    print("Historical NFL average for deep ball rate (20+ air yards): ~10-12%")
    print("This varies by era and offensive philosophy.")
    print(f"{'='*80}\n")


def main():
    """Analyze passing style for 2012-2014."""
    
    years = [2012, 2013, 2014]
    results = []
    
    for year in years:
        result = analyze_passing_style(year)
        if result:
            results.append(result)
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY: Ravens Passing Style (2012-2014)")
    print(f"{'='*80}\n")
    
    print("DEEP BALL FREQUENCY:")
    for result in results:
        print(f"{result['year']}: {result['deep_ball_attempts']} attempts "
              f"({result['deep_ball_percentage']:.1f}% of passes)")
    
    print("\nPLAY-ACTION USAGE:")
    for result in results:
        print(f"{result['year']}: {result['play_action_percentage']:.1f}% of passes "
              f"({result['play_action_attempts']} attempts)")
    
    # Average EPA across all years
    print("\nEPA COMPARISON (Average across 2012-2014):")
    pa_epas = [r['play_action_epa'] for r in results if r['play_action_epa'] is not None]
    std_epas = [r['standard_dropback_epa'] for r in results if r['standard_dropback_epa'] is not None]
    
    if pa_epas and std_epas:
        avg_pa_epa = sum(pa_epas) / len(pa_epas)
        avg_std_epa = sum(std_epas) / len(std_epas)
        print(f"Play-action EPA/attempt: {avg_pa_epa:+.3f}")
        print(f"Standard dropback EPA/attempt: {avg_std_epa:+.3f}")
        print(f"Difference: {avg_pa_epa - avg_std_epa:+.3f}")
    
    calculate_league_average_deep_balls(years)
    
    print(f"\n{'='*80}")
    print("BLOG FORMAT:")
    print(f"{'='*80}")
    print("\nDeep Ball Frequency:")
    for result in results:
        print(f"{result['year']}: {result['deep_ball_attempts']} attempts "
              f"({result['deep_ball_percentage']:.1f}% of passes)")
    print("League average: ~10-12% (historical NFL average)")
    
    print("\nPlay-Action Usage:")
    for result in results:
        print(f"{result['year']}: {result['play_action_percentage']:.1f}% of passes")
    
    if pa_epas and std_epas:
        print(f"EPA per play-action: {avg_pa_epa:+.3f} vs standard dropback: {avg_std_epa:+.3f}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
