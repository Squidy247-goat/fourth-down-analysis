"""
looks at 4th down conversion rates over the years
"""

import pandas as pd
from pathlib import Path

def analyze_fourth_down_conversions(year):
    """gets 4th down numbers for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nAnalyzing {year}...")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"  WARNING: File not found for {year}")
        return None
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for fourth down plays where teams go for it (run or pass)
    fourth_down_attempts = df[
        (df['down'] == 4) & 
        (df['play_type'].isin(['run', 'pass']))
    ].copy()
    
    if len(fourth_down_attempts) == 0:
        print(f"  WARNING: No 4th down attempt data found for {year}")
        return None
    
    # Ravens attempts
    ravens_attempts = fourth_down_attempts[fourth_down_attempts['posteam'] == 'BAL'].copy()
    
    if len(ravens_attempts) == 0:
        print(f"  WARNING: No Ravens 4th down attempts for {year}")
        return None
    
    # Calculate Ravens conversions
    # A conversion is when they get a first down or score a touchdown
    ravens_conversions = ravens_attempts[
        (ravens_attempts['first_down'] == 1) | 
        (ravens_attempts['touchdown'] == 1)
    ]
    
    ravens_total = len(ravens_attempts)
    ravens_converted = len(ravens_conversions)
    ravens_rate = (ravens_converted / ravens_total * 100) if ravens_total > 0 else 0
    
    # Calculate league average
    league_conversions = fourth_down_attempts[
        (fourth_down_attempts['first_down'] == 1) | 
        (fourth_down_attempts['touchdown'] == 1)
    ]
    
    league_total = len(fourth_down_attempts)
    league_converted = len(league_conversions)
    league_rate = (league_converted / league_total * 100) if league_total > 0 else 0
    
    print(f"  Ravens: {ravens_converted}/{ravens_total} ({ravens_rate:.1f}%)")
    print(f"  League: {league_converted}/{league_total} ({league_rate:.1f}%)")
    
    # Field position analysis (for all years)
    field_position_data = None
    
    # Own territory: yardline_100 >= 51 (own 1 to own 49)
    own_territory = ravens_attempts[ravens_attempts['yardline_100'] >= 51].copy()
    own_conversions = own_territory[
        (own_territory['first_down'] == 1) | 
        (own_territory['touchdown'] == 1)
    ]
    
    # Opponent territory (not red zone): 21 < yardline_100 < 51 (opp 49 to opp 21)
    opp_territory = ravens_attempts[
        (ravens_attempts['yardline_100'] > 20) & 
        (ravens_attempts['yardline_100'] < 51)
    ].copy()
    opp_conversions = opp_territory[
        (opp_territory['first_down'] == 1) | 
        (opp_territory['touchdown'] == 1)
    ]
    
    # Red zone: yardline_100 <= 20 (opp 20 to opp 1)
    red_zone = ravens_attempts[ravens_attempts['yardline_100'] <= 20].copy()
    red_zone_conversions = red_zone[
        (red_zone['first_down'] == 1) | 
        (red_zone['touchdown'] == 1)
    ]
    
    field_position_data = {
        'own_territory': {
            'attempts': len(own_territory),
            'conversions': len(own_conversions),
            'rate': (len(own_conversions) / len(own_territory) * 100) if len(own_territory) > 0 else 0
        },
        'opp_territory': {
            'attempts': len(opp_territory),
            'conversions': len(opp_conversions),
            'rate': (len(opp_conversions) / len(opp_territory) * 100) if len(opp_territory) > 0 else 0
        },
        'red_zone': {
            'attempts': len(red_zone),
            'conversions': len(red_zone_conversions),
            'rate': (len(red_zone_conversions) / len(red_zone) * 100) if len(red_zone) > 0 else 0
        }
    }
    
    return {
        'year': year,
        'ravens_attempts': ravens_total,
        'ravens_conversions': ravens_converted,
        'ravens_rate': ravens_rate,
        'league_attempts': league_total,
        'league_conversions': league_converted,
        'league_rate': league_rate,
        'field_position': field_position_data
    }


def analyze_era_conversions(years, era_name):
    """Analyze 4th down conversion rates for a given era."""
    
    print(f"\n{'='*80}")
    print(f"{era_name}")
    print(f"{'='*80}")
    
    results = []
    
    for year in years:
        result = analyze_fourth_down_conversions(year)
        if result:
            results.append(result)
    
    if not results:
        print(f"  No data available for {era_name}")
        return None
    
    # Calculate era totals
    ravens_total_attempts = sum(r['ravens_attempts'] for r in results)
    ravens_total_conversions = sum(r['ravens_conversions'] for r in results)
    league_total_attempts = sum(r['league_attempts'] for r in results)
    league_total_conversions = sum(r['league_conversions'] for r in results)
    
    ravens_era_rate = (ravens_total_conversions / ravens_total_attempts * 100) if ravens_total_attempts > 0 else 0
    league_era_rate = (league_total_conversions / league_total_attempts * 100) if league_total_attempts > 0 else 0
    
    print(f"\n{era_name} SUMMARY:")
    print(f"  Ravens: {ravens_total_conversions}/{ravens_total_attempts} ({ravens_era_rate:.1f}%)")
    print(f"  League: {league_total_conversions}/{league_total_attempts} ({league_era_rate:.1f}%)")
    print(f"  Difference: {ravens_era_rate - league_era_rate:+.1f}%")
    
    # Field position summary (for all years)
    field_position_summary = None
    fp_results = [r for r in results if r['field_position'] is not None]
    
    if fp_results:
        own_territory_attempts = sum(r['field_position']['own_territory']['attempts'] for r in fp_results)
        own_territory_conversions = sum(r['field_position']['own_territory']['conversions'] for r in fp_results)
        
        opp_territory_attempts = sum(r['field_position']['opp_territory']['attempts'] for r in fp_results)
        opp_territory_conversions = sum(r['field_position']['opp_territory']['conversions'] for r in fp_results)
        
        red_zone_attempts = sum(r['field_position']['red_zone']['attempts'] for r in fp_results)
        red_zone_conversions = sum(r['field_position']['red_zone']['conversions'] for r in fp_results)
        
        field_position_summary = {
            'own_territory': {
                'attempts': own_territory_attempts,
                'conversions': own_territory_conversions,
                'rate': (own_territory_conversions / own_territory_attempts * 100) if own_territory_attempts > 0 else 0
            },
            'opp_territory': {
                'attempts': opp_territory_attempts,
                'conversions': opp_territory_conversions,
                'rate': (opp_territory_conversions / opp_territory_attempts * 100) if opp_territory_attempts > 0 else 0
            },
            'red_zone': {
                'attempts': red_zone_attempts,
                'conversions': red_zone_conversions,
                'rate': (red_zone_conversions / red_zone_attempts * 100) if red_zone_attempts > 0 else 0
            }
        }
    
    return {
        'era_name': era_name,
        'years': years,
        'ravens_attempts': ravens_total_attempts,
        'ravens_conversions': ravens_total_conversions,
        'ravens_rate': ravens_era_rate,
        'league_attempts': league_total_attempts,
        'league_conversions': league_total_conversions,
        'league_rate': league_era_rate,
        'field_position': field_position_summary,
        'year_results': results
    }


def main():
    """Analyze fourth-down conversion rates by era."""
    
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
        result = analyze_era_conversions(era['years'], era['name'])
        if result:
            era_results.append(result)
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT - CONVERSION RATES BY ERA")
    print(f"{'='*80}\n")
    
    print("Conversion Rates by Era:\n")
    
    for result in era_results:
        years_label = f"{result['years'][0]}-{result['years'][-1]}"
        print(f"{years_label}: {result['ravens_rate']:.1f}% ({result['ravens_conversions']}/{result['ravens_attempts']} conversions)")
    
    # Field position analysis for ALL YEARS (2008-2024)
    print(f"\n{'='*80}")
    print("FIELD POSITION ANALYSIS (2008-2024)")
    print(f"{'='*80}\n")
    
    # Aggregate field position data across ALL eras
    total_own_attempts = 0
    total_own_conversions = 0
    total_opp_attempts = 0
    total_opp_conversions = 0
    total_rz_attempts = 0
    total_rz_conversions = 0
    
    for era_result in era_results:
        if era_result['field_position']:
            fp = era_result['field_position']
            total_own_attempts += fp['own_territory']['attempts']
            total_own_conversions += fp['own_territory']['conversions']
            total_opp_attempts += fp['opp_territory']['attempts']
            total_opp_conversions += fp['opp_territory']['conversions']
            total_rz_attempts += fp['red_zone']['attempts']
            total_rz_conversions += fp['red_zone']['conversions']
    
    own_rate = (total_own_conversions / total_own_attempts * 100) if total_own_attempts > 0 else 0
    opp_rate = (total_opp_conversions / total_opp_attempts * 100) if total_opp_attempts > 0 else 0
    rz_rate = (total_rz_conversions / total_rz_attempts * 100) if total_rz_attempts > 0 else 0
    
    print(f"Fourth Down Success by Field Position (2008-2024):\n")
    
    print(f"Own territory (own 1-49): {total_own_attempts} attempts, {own_rate:.1f}% conversion")
    print(f"Opponent territory (opp 49-21): {total_opp_attempts} attempts, {opp_rate:.1f}% conversion")
    print(f"Red zone (opp 20-1): {total_rz_attempts} attempts, {rz_rate:.1f}% conversion")
    
    # Field position breakdown by era
    print(f"\n{'='*80}")
    print("FIELD POSITION BREAKDOWN BY ERA")
    print(f"{'='*80}\n")
    
    for era_result in era_results:
        if era_result['field_position']:
            print(f"\n{era_result['era_name']}:")
            fp = era_result['field_position']
            print(f"  Own territory: {fp['own_territory']['attempts']} attempts, {fp['own_territory']['rate']:.1f}% conversion")
            print(f"  Opp territory: {fp['opp_territory']['attempts']} attempts, {fp['opp_territory']['rate']:.1f}% conversion")
            print(f"  Red zone: {fp['red_zone']['attempts']} attempts, {fp['red_zone']['rate']:.1f}% conversion")
    
    # Additional insights
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR BREAKDOWN")
    print(f"{'='*80}\n")
    
    for result in era_results:
        print(f"\n{result['era_name']}:")
        for year_result in result['year_results']:
            diff = year_result['ravens_rate'] - year_result['league_rate']
            print(f"  {year_result['year']}: {year_result['ravens_rate']:.1f}% "
                  f"(League: {year_result['league_rate']:.1f}%, Diff: {diff:+.1f}%)")


if __name__ == "__main__":
    main()
