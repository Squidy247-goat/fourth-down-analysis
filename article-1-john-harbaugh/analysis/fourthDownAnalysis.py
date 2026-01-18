"""
checks how often ravens go for it on 4th down
"""

import pandas as pd
from pathlib import Path

def analyze_fourth_down_attempts(year):
    """gets 4th down attempt numbers"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for fourth down plays where Ravens are on offense
    fourth_downs = df[(df['down'] == 4) & (df['posteam'] == 'BAL')].copy()
    
    if len(fourth_downs) == 0:
        print(f"  WARNING: No 4th down data found for {year}")
        return None
    
    # Count total 4th downs
    total_fourth_downs = len(fourth_downs)
    
    # Count attempts (go for it - excluding punts, field goals, and special teams plays)
    # An attempt is when they go for it (run or pass play)
    attempts = fourth_downs[
        (fourth_downs['play_type'].isin(['run', 'pass'])) &
        (fourth_downs['play_type'] != 'no_play')
    ]
    
    total_attempts = len(attempts)
    attempt_rate = (total_attempts / total_fourth_downs * 100) if total_fourth_downs > 0 else 0
    
    print(f"  Total 4th downs: {total_fourth_downs}")
    print(f"  4th down attempts (go for it): {total_attempts}")
    print(f"  Attempt rate: {attempt_rate:.1f}%")
    
    return {
        'year': year,
        'total_fourth_downs': total_fourth_downs,
        'attempts': total_attempts,
        'attempt_rate': attempt_rate
    }


def analyze_era(years, era_name):
    """Analyze 4th down attempts for a given era."""
    
    print(f"\n{'='*80}")
    print(f"{era_name}")
    print(f"{'='*80}")
    
    results = []
    
    for year in years:
        result = analyze_fourth_down_attempts(year)
        if result:
            results.append(result)
    
    if not results:
        print(f"  No data available for {era_name}")
        return None
    
    # Calculate era totals and averages
    total_attempts = sum(r['attempts'] for r in results)
    total_fourth_downs = sum(r['total_fourth_downs'] for r in results)
    num_seasons = len(results)
    
    attempts_per_season = total_attempts / num_seasons if num_seasons > 0 else 0
    era_attempt_rate = (total_attempts / total_fourth_downs * 100) if total_fourth_downs > 0 else 0
    
    print(f"\n{era_name} SUMMARY:")
    print(f"  Total 4th down attempts: {total_attempts}")
    print(f"  Attempts per season: {attempts_per_season:.1f}")
    print(f"  Attempt rate (% of 4th downs): {era_attempt_rate:.1f}%")
    print(f"  Number of seasons: {num_seasons}")
    
    return {
        'era_name': era_name,
        'years': years,
        'total_attempts': total_attempts,
        'attempts_per_season': attempts_per_season,
        'attempt_rate': era_attempt_rate,
        'num_seasons': num_seasons,
        'year_results': results
    }


def main():
    """Analyze fourth-down attempts by era."""
    
    # Define eras
    eras = [
        {
            'name': 'Early Years (2008-2011)',
            'years': [2008, 2009, 2010, 2011]
        },
        {
            'name': 'Championship Window (2012-2014)',
            'years': [2012, 2013, 2014]
        },
        {
            'name': 'Rebuild Era (2015-2017)',
            'years': [2015, 2016, 2017]
        },
        {
            'name': 'Lamar Era (2018-2024)',
            'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        }
    ]
    
    era_results = []
    
    for era in eras:
        result = analyze_era(era['years'], era['name'])
        if result:
            era_results.append(result)
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("Fourth Down Attempt Rate by Era\n")
    
    for result in era_results:
        print(f"{result['era_name']}:")
        print(f"Total 4th down attempts: {result['total_attempts']}")
        print(f"Attempts per season: {result['attempts_per_season']:.1f}")
        print(f"Attempt rate (% of 4th downs): {result['attempt_rate']:.1f}%\n")
    
    # Additional analysis - year by year breakdown
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR BREAKDOWN")
    print(f"{'='*80}\n")
    
    for result in era_results:
        print(f"\n{result['era_name']}:")
        for year_result in result['year_results']:
            print(f"  {year_result['year']}: {year_result['attempts']} attempts, "
                  f"{year_result['attempt_rate']:.1f}% rate")


if __name__ == "__main__":
    main()
