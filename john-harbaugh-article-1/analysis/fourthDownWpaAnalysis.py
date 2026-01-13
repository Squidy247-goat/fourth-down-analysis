"""
checks if going for it on 4th down helped or hurt the ravens
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analyze_fourth_down_wpa(year):
    """gets wpa from 4th down plays for one year"""
    
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
    
    # Ravens attempts only
    ravens_attempts = fourth_down_attempts[fourth_down_attempts['posteam'] == 'BAL'].copy()
    
    if len(ravens_attempts) == 0:
        print(f"  WARNING: No Ravens 4th down attempts for {year}")
        return None
    
    # Calculate conversions
    ravens_attempts['converted'] = (
        (ravens_attempts['first_down'] == 1) | 
        (ravens_attempts['touchdown'] == 1)
    )
    
    # Get WPA for each play
    # WPA column shows the change in win probability for that play
    successful_attempts = ravens_attempts[ravens_attempts['converted'] == True].copy()
    failed_attempts = ravens_attempts[ravens_attempts['converted'] == False].copy()
    
    # Calculate WPA totals (handling NaN values)
    total_wpa_success = successful_attempts['wpa'].fillna(0).sum()
    total_wpa_fail = failed_attempts['wpa'].fillna(0).sum()
    net_wpa = ravens_attempts['wpa'].fillna(0).sum()
    
    num_success = len(successful_attempts)
    num_fail = len(failed_attempts)
    
    print(f"  Successful conversions: {num_success}")
    print(f"  WPA from conversions: {total_wpa_success:+.3f}")
    print(f"  Failed attempts: {num_fail}")
    print(f"  WPA from failures: {total_wpa_fail:+.3f}")
    print(f"  Net WPA: {net_wpa:+.3f}")
    
    # Calculate average WPA per attempt
    avg_wpa_per_attempt = net_wpa / len(ravens_attempts) if len(ravens_attempts) > 0 else 0
    print(f"  Avg WPA per attempt: {avg_wpa_per_attempt:+.4f}")
    
    return {
        'year': year,
        'total_attempts': len(ravens_attempts),
        'successful_conversions': num_success,
        'failed_attempts': num_fail,
        'wpa_from_conversions': total_wpa_success,
        'wpa_from_failures': total_wpa_fail,
        'net_wpa': net_wpa,
        'avg_wpa_per_attempt': avg_wpa_per_attempt
    }


def main():
    """Analyze fourth-down WPA for 2020-2024."""
    
    years = [2020, 2021, 2022, 2023, 2024]
    
    print(f"{'='*80}")
    print("FOURTH DOWN WPA ANALYSIS (2020-2024)")
    print(f"{'='*80}")
    
    results = []
    
    for year in years:
        result = analyze_fourth_down_wpa(year)
        if result:
            results.append(result)
    
    if not results:
        print("No data available")
        return
    
    # Calculate totals
    total_attempts = sum(r['total_attempts'] for r in results)
    total_conversions = sum(r['successful_conversions'] for r in results)
    total_failures = sum(r['failed_attempts'] for r in results)
    total_wpa_conversions = sum(r['wpa_from_conversions'] for r in results)
    total_wpa_failures = sum(r['wpa_from_failures'] for r in results)
    total_net_wpa = sum(r['net_wpa'] for r in results)
    avg_wpa_per_attempt = total_net_wpa / total_attempts if total_attempts > 0 else 0
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY (2020-2024)")
    print(f"{'='*80}\n")
    
    print(f"Total 4th down attempts: {total_attempts}")
    print(f"Successful conversions: {total_conversions} ({total_conversions/total_attempts*100:.1f}%)")
    print(f"Failed attempts: {total_failures} ({total_failures/total_attempts*100:.1f}%)")
    print(f"\nTotal WPA from conversions: {total_wpa_conversions:+.3f}")
    print(f"Total WPA from failures: {total_wpa_failures:+.3f}")
    print(f"Net WPA: {total_net_wpa:+.3f}")
    print(f"Average WPA per attempt: {avg_wpa_per_attempt:+.4f}")
    
    # Print final summary in blog format
    print(f"\n\n{'='*80}")
    print("BLOG FORMAT OUTPUT")
    print(f"{'='*80}\n")
    
    print("Win Probability Added (WPA) from 4th Down Decisions (2020-2024):\n")
    print(f"Total WPA from 4th down conversions: {total_wpa_conversions:+.3f}")
    print(f"Total WPA from failed 4th down attempts: {total_wpa_failures:+.3f}")
    print(f"Net WPA: {total_net_wpa:+.3f}")
    print(f"Average WPA per attempt: {avg_wpa_per_attempt:+.4f}")
    
    print(f"\nYear-by-Year WPA from 4th Downs:\n")
    for result in results:
        print(f"{result['year']}: Net WPA {result['net_wpa']:+.3f} "
              f"({result['successful_conversions']}/{result['total_attempts']} conversions, "
              f"avg {result['avg_wpa_per_attempt']:+.4f} per attempt)")
    
    # Interpretation
    print(f"\n{'='*80}")
    print("INTERPRETATION")
    print(f"{'='*80}\n")
    
    if total_net_wpa > 0:
        print(f"✓ POSITIVE NET WPA: Harbaugh's fourth-down aggressiveness added {total_net_wpa:+.3f} to")
        print(f"  the Ravens' win probability over 5 seasons. The strategy PAID OFF.")
    else:
        print(f"✗ NEGATIVE NET WPA: Harbaugh's fourth-down decisions cost the Ravens {total_net_wpa:.3f}")
        print(f"  in win probability over 5 seasons. The strategy did NOT pay off.")
    
    print(f"\nOn average, each fourth-down attempt changed win probability by {avg_wpa_per_attempt:+.4f}.")
    
    # Find best and worst years
    best_year = max(results, key=lambda x: x['net_wpa'])
    worst_year = min(results, key=lambda x: x['net_wpa'])
    
    print(f"\nBest year: {best_year['year']} (Net WPA: {best_year['net_wpa']:+.3f})")
    print(f"Worst year: {worst_year['year']} (Net WPA: {worst_year['net_wpa']:+.3f})")
    
    # Additional context
    print(f"\n{'='*80}")
    print("DETAILED BREAKDOWN BY YEAR")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"\n{result['year']}:")
        print(f"  Attempts: {result['total_attempts']}")
        print(f"  Conversions: {result['successful_conversions']} ({result['successful_conversions']/result['total_attempts']*100:.1f}%)")
        print(f"  Failures: {result['failed_attempts']} ({result['failed_attempts']/result['total_attempts']*100:.1f}%)")
        print(f"  WPA from conversions: {result['wpa_from_conversions']:+.3f}")
        print(f"  WPA from failures: {result['wpa_from_failures']:+.3f}")
        print(f"  Net WPA: {result['net_wpa']:+.3f}")
        print(f"  Avg WPA per attempt: {result['avg_wpa_per_attempt']:+.4f}")


if __name__ == "__main__":
    main()
