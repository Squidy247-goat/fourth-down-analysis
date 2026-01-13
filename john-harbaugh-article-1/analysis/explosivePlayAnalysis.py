"""
counts big plays and yards after catch
"""

import pandas as pd
from pathlib import Path

def analyze_explosive_plays(year):
    """gets big play numbers for one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nReading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for Ravens offensive plays
    ravens_offense = df[df['posteam'] == 'BAL'].copy()
    
    # Get plays with yards gained (pass or rush)
    # Explosive plays are 20+ yards
    plays_with_yards = ravens_offense[
        (ravens_offense['pass_attempt'] == 1) | 
        (ravens_offense['rush_attempt'] == 1)
    ].copy()
    
    # Count 20+ yard plays
    explosive_plays = plays_with_yards[plays_with_yards['yards_gained'] >= 20].copy()
    
    total_explosive = len(explosive_plays)
    
    # Break down by play type
    explosive_pass = explosive_plays[explosive_plays['pass_attempt'] == 1]
    explosive_rush = explosive_plays[explosive_plays['rush_attempt'] == 1]
    
    total_explosive_pass = len(explosive_pass)
    total_explosive_rush = len(explosive_rush)
    
    # Calculate average yards on explosive plays
    avg_explosive_yards = explosive_plays['yards_gained'].mean() if total_explosive > 0 else 0
    
    # Total yards from explosive plays
    total_explosive_yards = explosive_plays['yards_gained'].sum() if total_explosive > 0 else 0
    
    # Total offensive yards
    total_yards = plays_with_yards['yards_gained'].sum()
    
    # Percentage of total yards from explosive plays
    explosive_yards_pct = (total_explosive_yards / total_yards * 100) if total_yards > 0 else 0
    
    print(f"\n{year} Explosive Play Analysis:")
    print(f"  Total 20+ yard plays: {total_explosive}")
    print(f"    Passing: {total_explosive_pass}")
    print(f"    Rushing: {total_explosive_rush}")
    print(f"  Average yards on explosive plays: {avg_explosive_yards:.1f}")
    print(f"  Total yards from explosive plays: {total_explosive_yards}")
    print(f"  % of total offense from explosive plays: {explosive_yards_pct:.1f}%")
    
    return {
        'year': year,
        'total_explosive': total_explosive,
        'explosive_pass': total_explosive_pass,
        'explosive_rush': total_explosive_rush,
        'avg_explosive_yards': avg_explosive_yards,
        'total_explosive_yards': total_explosive_yards,
        'explosive_yards_pct': explosive_yards_pct
    }


def analyze_yards_after_catch(year):
    """
    Analyze yards after catch (YAC) for a specific year
    """
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nReading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for Ravens offensive plays
    ravens_offense = df[df['posteam'] == 'BAL'].copy()
    
    # Get completed passes with YAC data
    completed_passes = ravens_offense[
        (ravens_offense['complete_pass'] == 1) & 
        (ravens_offense['yards_after_catch'].notna())
    ].copy()
    
    total_completions = len(completed_passes)
    
    if total_completions == 0:
        print(f"No YAC data available for {year}")
        return None
    
    # Calculate YAC metrics
    total_yac = completed_passes['yards_after_catch'].sum()
    avg_yac = completed_passes['yards_after_catch'].mean()
    total_receiving_yards = completed_passes['receiving_yards'].sum()
    total_air_yards = completed_passes['air_yards'].sum()
    
    # YAC percentage of total receiving yards
    yac_pct = (total_yac / total_receiving_yards * 100) if total_receiving_yards > 0 else 0
    
    print(f"\n{year} Yards After Catch Analysis:")
    print(f"  Total completions: {total_completions}")
    print(f"  Total YAC: {total_yac:.0f}")
    print(f"  Average YAC per completion: {avg_yac:.2f}")
    print(f"  Total receiving yards: {total_receiving_yards:.0f}")
    print(f"  YAC as % of receiving yards: {yac_pct:.1f}%")
    
    return {
        'year': year,
        'total_completions': total_completions,
        'total_yac': total_yac,
        'avg_yac': avg_yac,
        'total_receiving_yards': total_receiving_yards,
        'yac_pct': yac_pct
    }


def main():
    """Main analysis function"""
    
    print(f"{'='*80}")
    print("EXPLOSIVE PLAY GENERATION ANALYSIS")
    print(f"{'='*80}")
    
    # 1. Analyze explosive plays for all years
    print(f"\n{'='*80}")
    print("PART 1: EXPLOSIVE PLAYS (20+ YARDS)")
    print(f"{'='*80}")
    
    all_explosive_results = []
    
    for year in range(2016, 2026):
        result = analyze_explosive_plays(year)
        all_explosive_results.append(result)
    
    # Calculate averages for different periods
    pre_lamar = [r for r in all_explosive_results if r['year'] in [2016, 2017]]
    peak_lamar = [r for r in all_explosive_results if r['year'] in [2019, 2020]]
    lamar_era = [r for r in all_explosive_results if r['year'] >= 2018]
    
    pre_lamar_avg = sum(r['total_explosive'] for r in pre_lamar) / len(pre_lamar)
    peak_lamar_avg = sum(r['total_explosive'] for r in peak_lamar) / len(peak_lamar)
    
    increase = peak_lamar_avg - pre_lamar_avg
    increase_pct = (increase / pre_lamar_avg * 100) if pre_lamar_avg > 0 else 0
    
    print(f"\n{'='*80}")
    print("EXPLOSIVE PLAY COMPARISON:")
    print(f"{'='*80}")
    print(f"2016-2017 average: {pre_lamar_avg:.1f} explosive plays per season")
    print(f"2019-2020 average: {peak_lamar_avg:.1f} explosive plays per season")
    print(f"Increase: {increase:.1f} plays ({increase_pct:.1f}%)")
    
    # 2. Analyze YAC for all years
    print(f"\n{'='*80}")
    print("PART 2: YARDS AFTER CATCH (YAC)")
    print(f"{'='*80}")
    
    all_yac_results = []
    
    for year in range(2016, 2026):
        result = analyze_yards_after_catch(year)
        if result:
            all_yac_results.append(result)
    
    # Calculate YAC averages
    pre_lamar_yac = [r for r in all_yac_results if r['year'] in [2016, 2017]]
    peak_lamar_yac = [r for r in all_yac_results if r['year'] in [2019, 2020]]
    
    if pre_lamar_yac and peak_lamar_yac:
        pre_lamar_yac_avg = sum(r['avg_yac'] for r in pre_lamar_yac) / len(pre_lamar_yac)
        peak_lamar_yac_avg = sum(r['avg_yac'] for r in peak_lamar_yac) / len(peak_lamar_yac)
        
        yac_increase = peak_lamar_yac_avg - pre_lamar_yac_avg
        yac_increase_pct = (yac_increase / pre_lamar_yac_avg * 100) if pre_lamar_yac_avg > 0 else 0
        
        print(f"\n{'='*80}")
        print("YAC COMPARISON:")
        print(f"{'='*80}")
        print(f"2016-2017 average: {pre_lamar_yac_avg:.2f} yards after catch per completion")
        print(f"2019-2020 average: {peak_lamar_yac_avg:.2f} yards after catch per completion")
        print(f"Increase: {yac_increase:+.2f} YAC per completion ({yac_increase_pct:+.1f}%)")
    
    # 3. Print Blog-Ready Output
    print(f"\n{'='*80}")
    print("BLOG-READY FORMAT:")
    print(f"{'='*80}\n")
    
    print("Plays of 20+ Yards:")
    print(f"2016-2017 average: {pre_lamar_avg:.0f} plays")
    print(f"2019-2020 average: {peak_lamar_avg:.0f} plays")
    print(f"Increase: {increase_pct:.0f}%")
    
    if pre_lamar_yac and peak_lamar_yac:
        print("\nYards After Catch:")
        print(f"2016-2017 average: {pre_lamar_yac_avg:.2f} YAC per completion")
        print(f"2019-2020 average: {peak_lamar_yac_avg:.2f} YAC per completion")
    
    print("\nBig Play Sustainability (2018-2025):")
    for result in lamar_era:
        print(f"{result['year']}: {result['total_explosive']} plays (Pass: {result['explosive_pass']}, Rush: {result['explosive_rush']})")
    
    # Additional insights
    print(f"\n{'='*80}")
    print("ADDITIONAL INSIGHTS:")
    print(f"{'='*80}")
    
    # Track rushing explosive plays trend
    print("\nRushing Explosive Plays (20+ yards) Trend:")
    for result in lamar_era:
        print(f"  {result['year']}: {result['explosive_rush']} explosive rush plays")
    
    # Calculate explosive play rate per game (assuming 16-17 games)
    print("\nExplosive Plays Per Game:")
    for result in lamar_era:
        games = 17 if result['year'] >= 2021 else 16
        if result['year'] == 2025:
            games = 17  # Adjust if partial season
        per_game = result['total_explosive'] / games
        print(f"  {result['year']}: {per_game:.1f} explosive plays per game")


if __name__ == "__main__":
    main()
