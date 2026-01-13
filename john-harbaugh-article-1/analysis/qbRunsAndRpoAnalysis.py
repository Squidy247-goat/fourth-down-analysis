"""
looks at qb runs and rpo plays
"""

import pandas as pd
from pathlib import Path

def analyze_qb_runs(year, weeks=None):
    """gets qb run stats for one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nReading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for specific weeks if provided (e.g., 2018 weeks 11-17)
    if weeks:
        start_week, end_week = weeks
        df = df[(df['week'] >= start_week) & (df['week'] <= end_week)].copy()
        print(f"Filtering for weeks {start_week}-{end_week}")
    
    # Filter for Ravens offensive plays
    ravens_offense = df[df['posteam'] == 'BAL'].copy()
    
    # Get Lamar Jackson's player ID (he became starter in 2018)
    # We'll identify QB runs as rush attempts by the QB
    # qb_scramble = 1 means it's a scramble (not designed)
    # So designed QB runs are: rush_attempt=1 AND qb_scramble!=1 AND rusher is QB
    
    # First, let's identify who the QB is
    # In 2018, Lamar took over in week 11
    # We'll look for rush attempts where qb_scramble is not 1
    
    # Get all rush attempts by Ravens
    rush_plays = ravens_offense[ravens_offense['rush_attempt'] == 1].copy()
    
    # QB scrambles are marked with qb_scramble = 1
    # Designed QB runs are rush attempts that are NOT scrambles
    # We need to identify which rusher is a QB
    
    # Common QB names in Ravens history
    qb_names = ['L.Jackson', 'J.Flacco', 'R.Griffin', 'T.Huntley', 'T.Taylor', 'J.Johnson']
    
    # Get designed QB runs (rush attempts that aren't scrambles)
    designed_qb_runs = rush_plays[
        (rush_plays['qb_scramble'] != 1) & 
        (rush_plays['rusher_player_name'].isin(qb_names))
    ].copy()
    
    # Get all QB runs (including scrambles) for context
    all_qb_runs = rush_plays[rush_plays['rusher_player_name'].isin(qb_names)].copy()
    
    total_attempts = len(designed_qb_runs)
    total_yards = designed_qb_runs['rushing_yards'].sum() if total_attempts > 0 else 0
    ypc = total_yards / total_attempts if total_attempts > 0 else 0
    
    print(f"\nDesigned QB Runs ({year}):")
    print(f"  Total attempts: {total_attempts}")
    print(f"  Total yards: {total_yards}")
    print(f"  Yards per carry: {ypc:.2f}")
    
    # Also show QB breakdown
    if total_attempts > 0:
        print(f"\n  Breakdown by QB:")
        for qb in designed_qb_runs['rusher_player_name'].unique():
            qb_runs = designed_qb_runs[designed_qb_runs['rusher_player_name'] == qb]
            qb_attempts = len(qb_runs)
            qb_yards = qb_runs['rushing_yards'].sum()
            qb_ypc = qb_yards / qb_attempts if qb_attempts > 0 else 0
            print(f"    {qb}: {qb_attempts} att, {qb_yards} yds, {qb_ypc:.2f} ypc")
    
    return {
        'year': year,
        'weeks': weeks,
        'attempts': total_attempts,
        'yards': total_yards,
        'ypc': ypc
    }


def analyze_rpo_success(year):
    """
    Analyze RPO success rates
    Note: NFL play-by-play data doesn't explicitly tag RPO plays
    We'll use a proxy: short passes from shotgun on early downs with quick releases
    """
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nReading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for Ravens offensive plays
    ravens_offense = df[df['posteam'] == 'BAL'].copy()
    
    # RPO proxy: shotgun formations on 1st/2nd down with short passes or runs
    # This is an approximation since RPO isn't explicitly tagged
    # RPOs typically are:
    # - Shotgun formation
    # - 1st or 2nd down
    # - Pass attempts with air_yards < 5 OR rush attempts
    
    potential_rpo_plays = ravens_offense[
        (ravens_offense['shotgun'] == 1) &
        (ravens_offense['down'].isin([1, 2])) &
        (
            ((ravens_offense['pass_attempt'] == 1) & (ravens_offense['air_yards'] < 5)) |
            (ravens_offense['rush_attempt'] == 1)
        )
    ].copy()
    
    # Success = gained enough yards (40% on 1st, 60% on 2nd, 100% on 3rd/4th)
    # Or first down or touchdown
    total_plays = len(potential_rpo_plays)
    
    if total_plays == 0:
        print(f"\nNo potential RPO plays found for {year}")
        return None
    
    # Calculate success
    successful_plays = potential_rpo_plays[
        (potential_rpo_plays['first_down'] == 1) |
        (potential_rpo_plays['touchdown'] == 1) |
        ((potential_rpo_plays['down'] == 1) & (potential_rpo_plays['yards_gained'] >= potential_rpo_plays['ydstogo'] * 0.4)) |
        ((potential_rpo_plays['down'] == 2) & (potential_rpo_plays['yards_gained'] >= potential_rpo_plays['ydstogo'] * 0.6))
    ]
    
    success_count = len(successful_plays)
    success_rate = (success_count / total_plays * 100) if total_plays > 0 else 0
    
    print(f"\nRPO Success Rate ({year}) [Estimated]:")
    print(f"  Total RPO-style plays: {total_plays}")
    print(f"  Successful plays: {success_count}")
    print(f"  Success rate: {success_rate:.1f}%")
    
    return {
        'year': year,
        'total_plays': total_plays,
        'successful': success_count,
        'success_rate': success_rate
    }


def analyze_yards_before_contact(years):
    """
    Analyze yards before contact (team rushing)
    Note: NFL pbp data may not have explicit yards before contact
    We'll use EPA and success rate as proxies for rushing effectiveness
    """
    
    print(f"\n{'='*80}")
    print(f"Analyzing Team Rushing Effectiveness for {years}")
    print(f"{'='*80}")
    
    all_results = []
    
    for year in years:
        file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
        
        print(f"\nReading {file_path.name}...")
        df = pd.read_csv(file_path, low_memory=False)
        
        # Filter for regular season only
        df = df[df['season_type'] == 'REG'].copy()
        
        # Filter for Ravens offensive plays
        ravens_offense = df[df['posteam'] == 'BAL'].copy()
        
        # Get rushing plays
        rush_plays = ravens_offense[ravens_offense['rush_attempt'] == 1].copy()
        
        total_rushes = len(rush_plays)
        total_yards = rush_plays['rushing_yards'].sum() if total_rushes > 0 else 0
        ypc = total_yards / total_rushes if total_rushes > 0 else 0
        
        # EPA per rush
        avg_epa = rush_plays['epa'].mean() if total_rushes > 0 else 0
        
        # Success rate (EPA > 0 or first down)
        successful_rushes = rush_plays[
            (rush_plays['epa'] > 0) | 
            (rush_plays['first_down'] == 1)
        ]
        success_rate = (len(successful_rushes) / total_rushes * 100) if total_rushes > 0 else 0
        
        print(f"\n{year} Team Rushing:")
        print(f"  Total rushes: {total_rushes}")
        print(f"  Total yards: {total_yards}")
        print(f"  Yards per carry: {ypc:.2f}")
        print(f"  EPA per rush: {avg_epa:.3f}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        all_results.append({
            'year': year,
            'total_rushes': total_rushes,
            'total_yards': total_yards,
            'ypc': ypc,
            'epa_per_rush': avg_epa,
            'success_rate': success_rate
        })
    
    return all_results


def main():
    """Main analysis function"""
    
    print(f"{'='*80}")
    print("LAMAR JACKSON ERA QB RUNS & RPO ANALYSIS")
    print(f"{'='*80}")
    
    # 1. Designed QB Runs Analysis
    print(f"\n{'='*80}")
    print("PART 1: DESIGNED QB RUNS")
    print(f"{'='*80}")
    
    qb_run_results = []
    
    # 2018 (Weeks 11-17 - Lamar's first starts)
    result_2018 = analyze_qb_runs(2018, weeks=(11, 17))
    qb_run_results.append(result_2018)
    
    # 2019 (MVP season)
    result_2019 = analyze_qb_runs(2019)
    qb_run_results.append(result_2019)
    
    # 2020
    result_2020 = analyze_qb_runs(2020)
    qb_run_results.append(result_2020)
    
    # 2021-2025 (for average)
    results_2021_2025 = []
    for year in [2021, 2022, 2023, 2024, 2025]:
        result = analyze_qb_runs(year)
        results_2021_2025.append(result)
        qb_run_results.append(result)
    
    # Calculate 2021-2025 average
    avg_attempts = sum(r['attempts'] for r in results_2021_2025) / len(results_2021_2025)
    avg_yards = sum(r['yards'] for r in results_2021_2025) / len(results_2021_2025)
    avg_ypc = sum(r['ypc'] for r in results_2021_2025) / len(results_2021_2025)
    
    print(f"\n{'='*80}")
    print("2021-2025 AVERAGE:")
    print(f"{'='*80}")
    print(f"  Average attempts: {avg_attempts:.1f}")
    print(f"  Average yards: {avg_yards:.1f}")
    print(f"  Average YPC: {avg_ypc:.2f}")
    
    # 2. RPO Success Rate Analysis
    print(f"\n{'='*80}")
    print("PART 2: RPO SUCCESS RATES (ESTIMATED)")
    print(f"{'='*80}")
    
    rpo_results = []
    
    for year in [2019, 2020]:
        result = analyze_rpo_success(year)
        if result:
            rpo_results.append(result)
    
    # 2021-2025 average
    rpo_2021_2025 = []
    for year in [2021, 2022, 2023, 2024, 2025]:
        result = analyze_rpo_success(year)
        if result:
            rpo_2021_2025.append(result)
    
    if rpo_2021_2025:
        avg_rpo_success = sum(r['success_rate'] for r in rpo_2021_2025) / len(rpo_2021_2025)
        print(f"\n2021-2025 Average RPO Success Rate: {avg_rpo_success:.1f}%")
    
    # 3. Yards Before Contact / Team Rushing Effectiveness
    print(f"\n{'='*80}")
    print("PART 3: TEAM RUSHING EFFECTIVENESS")
    print(f"{'='*80}")
    
    print(f"\nPre-Lamar Era (2016-2017):")
    pre_lamar = analyze_yards_before_contact([2016, 2017])
    
    print(f"\nPeak Lamar Era (2019-2020):")
    peak_lamar = analyze_yards_before_contact([2019, 2020])
    
    # Calculate averages
    pre_lamar_ypc = sum(r['ypc'] for r in pre_lamar) / len(pre_lamar)
    peak_lamar_ypc = sum(r['ypc'] for r in peak_lamar) / len(peak_lamar)
    difference_ypc = peak_lamar_ypc - pre_lamar_ypc
    
    pre_lamar_epa = sum(r['epa_per_rush'] for r in pre_lamar) / len(pre_lamar)
    peak_lamar_epa = sum(r['epa_per_rush'] for r in peak_lamar) / len(peak_lamar)
    difference_epa = peak_lamar_epa - pre_lamar_epa
    
    print(f"\n{'='*80}")
    print("COMPARISON:")
    print(f"{'='*80}")
    print(f"Pre-Lamar (2016-2017) Average YPC: {pre_lamar_ypc:.2f}")
    print(f"Peak Lamar (2019-2020) Average YPC: {peak_lamar_ypc:.2f}")
    print(f"Difference: +{difference_ypc:.2f} YPC")
    print(f"\nPre-Lamar EPA/Rush: {pre_lamar_epa:.3f}")
    print(f"Peak Lamar EPA/Rush: {peak_lamar_epa:.3f}")
    print(f"Difference: +{difference_epa:.3f} EPA/Rush")
    
    # 4. Print Blog-Ready Output
    print(f"\n{'='*80}")
    print("BLOG-READY FORMAT:")
    print(f"{'='*80}\n")
    
    print("Designed QB Runs:")
    print(f"2018 (Weeks 11-17): {result_2018['attempts']} attempts, {result_2018['yards']} yards, {result_2018['ypc']:.1f} per carry")
    print(f"2019: {result_2019['attempts']} attempts, {result_2019['yards']} yards, {result_2019['ypc']:.1f} per carry")
    print(f"2020: {result_2020['attempts']} attempts, {result_2020['yards']} yards, {result_2020['ypc']:.1f} per carry")
    print(f"2021-2025 average: {avg_attempts:.0f} attempts, {avg_yards:.0f} yards, {avg_ypc:.1f} per carry")
    
    print("\nRPO Success Rates (Estimated):")
    if len(rpo_results) >= 2:
        print(f"2019: {rpo_results[0]['success_rate']:.1f}%")
        print(f"2020: {rpo_results[1]['success_rate']:.1f}%")
    if rpo_2021_2025:
        print(f"2021-2025 average: {avg_rpo_success:.1f}%")
    
    print("\nTeam Rushing Effectiveness (Yards per Carry):")
    print(f"2016-2017 (Pre-Lamar): {pre_lamar_ypc:.2f} YPC")
    print(f"2019-2020 (Peak Lamar): {peak_lamar_ypc:.2f} YPC")
    print(f"Difference: +{difference_ypc:.2f} YPC")


if __name__ == "__main__":
    main()
