import pandas as pd
import numpy as np

def load_season_data(year):
    """Load play-by-play data for a specific season"""
    file_path = f'../data/play_by_play_{year}.csv'
    try:
        df = pd.read_csv(file_path, low_memory=False)
        print(f"Loaded {year} season data: {len(df)} plays")
        return df
    except Exception as e:
        print(f"Error loading {year} data: {e}")
        return None

def get_qualifying_qbs(df, min_pass_attempts=100):
    """Get list of qualifying quarterbacks based on pass attempts"""
    # Count completions + incompletions (excluding spikes) for each QB
    qb_attempts = {}
    for qb in df['passer_player_name'].dropna().unique():
        qb_data = df[(df['passer_player_name'] == qb) & (df['qb_spike'] != 1)]
        completions = qb_data['complete_pass'].sum()
        incompletions = len(qb_data[qb_data['incomplete_pass'] == 1])
        attempts = completions + incompletions
        if attempts > 0:
            qb_attempts[qb] = attempts
    
    potential_qbs = [qb for qb, attempts in qb_attempts.items() if attempts >= min_pass_attempts]
    return potential_qbs

def calculate_basic_passing_stats(df, qb_name):
    """Calculate basic passing statistics for a QB"""
    
    # Filter for all plays by this QB as passer
    qb_passes = df[(df['passer_player_name'] == qb_name)].copy()
    
    if len(qb_passes) == 0:
        return None
    
    # Exclude spikes from attempts (standard practice)
    qb_passes_no_spike = qb_passes[qb_passes['qb_spike'] != 1]
    
    # Basic stats - attempts = completions + incompletions (NOT including sacks)
    completions = qb_passes_no_spike['complete_pass'].sum()
    incompletions = len(qb_passes_no_spike[qb_passes_no_spike['incomplete_pass'] == 1])
    total_attempts = completions + incompletions
    completion_pct = (completions / total_attempts * 100) if total_attempts > 0 else 0
    
    # Yards (from completed/incomplete passes only, not sacks)
    passing_yards = qb_passes_no_spike['passing_yards'].sum()
    yards_per_attempt = passing_yards / total_attempts if total_attempts > 0 else 0
    
    # TDs and INTs
    pass_tds = qb_passes_no_spike['pass_touchdown'].sum()
    interceptions = qb_passes_no_spike['interception'].sum()
    
    # Sacks (from all qb_passes including spikes)
    sacks = qb_passes['sack'].sum()
    
    # Calculate passer rating (NFL formula)
    if total_attempts > 0:
        a = ((completions / total_attempts) - 0.3) * 5
        b = ((passing_yards / total_attempts) - 3) * 0.25
        c = (pass_tds / total_attempts) * 20
        d = 2.375 - ((interceptions / total_attempts) * 25)
        
        a = max(0, min(a, 2.375))
        b = max(0, min(b, 2.375))
        c = max(0, min(c, 2.375))
        d = max(0, min(d, 2.375))
        
        passer_rating = ((a + b + c + d) / 6) * 100
    else:
        passer_rating = 0
    
    return {
        'qb_name': qb_name,
        'attempts': int(total_attempts),
        'completions': int(completions),
        'completion_pct': round(completion_pct, 2),
        'passing_yards': int(passing_yards),
        'yards_per_attempt': round(yards_per_attempt, 2),
        'pass_tds': int(pass_tds),
        'interceptions': int(interceptions),
        'td_int_ratio': round(pass_tds / interceptions, 2) if interceptions > 0 else pass_tds,
        'sacks': int(sacks),
        'passer_rating': round(passer_rating, 2)
    }

def calculate_advanced_passing_stats(df, qb_name):
    """Calculate advanced passing statistics (EPA, success rate, CPOE)"""
    
    # Filter for QB dropbacks (passes + sacks)
    qb_dropbacks = df[
        (df['passer_player_name'] == qb_name) & 
        (df['qb_dropback'] == 1)
    ].copy()
    
    if len(qb_dropbacks) == 0:
        return None
    
    # EPA per dropback
    epa_per_dropback = qb_dropbacks['qb_epa'].mean()
    
    # Success rate (plays with positive EPA)
    successful_plays = len(qb_dropbacks[qb_dropbacks['success'] == 1])
    total_plays = len(qb_dropbacks)
    success_rate = (successful_plays / total_plays * 100) if total_plays > 0 else 0
    
    # CPOE (Completion Percentage Over Expected)
    cpoe = qb_dropbacks['cpoe'].mean()
    
    return {
        'qb_name': qb_name,
        'dropbacks': int(total_plays),
        'epa_per_dropback': round(epa_per_dropback, 4),
        'success_rate': round(success_rate, 2),
        'cpoe': round(cpoe, 2)
    }

def calculate_league_averages(df, qb_list, stat_type='basic'):
    """Calculate league averages for all qualifying QBs"""
    
    all_stats = []
    
    for qb in qb_list:
        if stat_type == 'basic':
            stats = calculate_basic_passing_stats(df, qb)
        else:
            stats = calculate_advanced_passing_stats(df, qb)
        
        if stats:
            all_stats.append(stats)
    
    if not all_stats:
        return None
    
    stats_df = pd.DataFrame(all_stats)
    
    # Calculate averages
    averages = {}
    for col in stats_df.columns:
        if col != 'qb_name':
            averages[col] = round(stats_df[col].mean(), 2)
    
    return averages, stats_df

def rank_qb_stats(stats_df, qb_name, stat_column, ascending=False):
    """Rank a QB in a specific statistic"""
    sorted_df = stats_df.sort_values(by=stat_column, ascending=ascending).reset_index(drop=True)
    sorted_df['rank'] = range(1, len(sorted_df) + 1)
    
    qb_row = sorted_df[sorted_df['qb_name'] == qb_name]
    if len(qb_row) > 0:
        return int(qb_row.iloc[0]['rank']), len(sorted_df)
    return None, len(sorted_df)

def generate_full_report(df, season, qb_name='C.Williams', min_attempts=100):
    """Generate comprehensive passing statistics report"""
    
    print(f"\n{'='*70}")
    print(f"CALEB WILLIAMS PASSING STATISTICS - {season} SEASON")
    print(f"{'='*70}\n")
    
    # Get qualifying QBs
    qualifying_qbs = get_qualifying_qbs(df, min_attempts)
    print(f"Analyzing {len(qualifying_qbs)} qualifying quarterbacks ({min_attempts}+ attempts)\n")
    
    # Calculate Caleb's basic stats
    caleb_basic = calculate_basic_passing_stats(df, qb_name)
    if not caleb_basic:
        print(f"No data found for {qb_name}")
        return None
    
    # Calculate league averages for basic stats
    league_basic_avg, basic_stats_df = calculate_league_averages(df, qualifying_qbs, 'basic')
    
    # Calculate Caleb's advanced stats
    caleb_advanced = calculate_advanced_passing_stats(df, qb_name)
    
    # Calculate league averages for advanced stats
    league_advanced_avg, advanced_stats_df = calculate_league_averages(df, qualifying_qbs, 'advanced')
    
    print("="*70)
    print("BASIC PASSING STATISTICS")
    print("="*70)
    
    # Completion Percentage
    comp_pct_rank, total_qbs = rank_qb_stats(basic_stats_df, qb_name, 'completion_pct', ascending=False)
    print(f"\nCompletion Percentage:")
    print(f"  Caleb Williams: {caleb_basic['completion_pct']}%")
    print(f"  League Average: {league_basic_avg['completion_pct']}%")
    print(f"  Ranking: {comp_pct_rank} out of {total_qbs} QBs")
    print(f"  Difference: {'+' if caleb_basic['completion_pct'] - league_basic_avg['completion_pct'] > 0 else ''}{round(caleb_basic['completion_pct'] - league_basic_avg['completion_pct'], 2)}%")
    
    # Yards per Attempt
    ypa_rank, _ = rank_qb_stats(basic_stats_df, qb_name, 'yards_per_attempt', ascending=False)
    print(f"\nYards Per Attempt:")
    print(f"  Caleb Williams: {caleb_basic['yards_per_attempt']} yards")
    print(f"  League Average: {league_basic_avg['yards_per_attempt']} yards")
    print(f"  Ranking: {ypa_rank} out of {total_qbs} QBs")
    print(f"  Difference: {'+' if caleb_basic['yards_per_attempt'] - league_basic_avg['yards_per_attempt'] > 0 else ''}{round(caleb_basic['yards_per_attempt'] - league_basic_avg['yards_per_attempt'], 2)} yards")
    
    # TD to INT Ratio
    td_int_rank, _ = rank_qb_stats(basic_stats_df, qb_name, 'td_int_ratio', ascending=False)
    print(f"\nTD to INT Ratio:")
    print(f"  Caleb Williams: {caleb_basic['pass_tds']} TDs to {caleb_basic['interceptions']} INTs (Ratio: {caleb_basic['td_int_ratio']})")
    print(f"  League Average Ratio: {league_basic_avg['td_int_ratio']}")
    print(f"  Ranking: {td_int_rank} out of {total_qbs} QBs")
    
    # Passer Rating
    rating_rank, _ = rank_qb_stats(basic_stats_df, qb_name, 'passer_rating', ascending=False)
    print(f"\nPasser Rating:")
    print(f"  Caleb Williams: {caleb_basic['passer_rating']}")
    print(f"  League Average: {league_basic_avg['passer_rating']}")
    print(f"  Ranking: {rating_rank} out of {total_qbs} QBs")
    print(f"  Difference: {'+' if caleb_basic['passer_rating'] - league_basic_avg['passer_rating'] > 0 else ''}{round(caleb_basic['passer_rating'] - league_basic_avg['passer_rating'], 2)}")
    
    print(f"\n{'='*70}")
    print("ADVANCED PASSING STATISTICS")
    print("="*70)
    
    if caleb_advanced and league_advanced_avg:
        # EPA per Dropback
        epa_rank, _ = rank_qb_stats(advanced_stats_df, qb_name, 'epa_per_dropback', ascending=False)
        print(f"\nEPA per Dropback:")
        print(f"  Caleb Williams: {caleb_advanced['epa_per_dropback']}")
        print(f"  League Average: {league_advanced_avg['epa_per_dropback']}")
        print(f"  Ranking: {epa_rank} out of {total_qbs} QBs")
        print(f"  Difference: {'+' if caleb_advanced['epa_per_dropback'] - league_advanced_avg['epa_per_dropback'] > 0 else ''}{round(caleb_advanced['epa_per_dropback'] - league_advanced_avg['epa_per_dropback'], 4)}")
        
        # Success Rate
        success_rank, _ = rank_qb_stats(advanced_stats_df, qb_name, 'success_rate', ascending=False)
        print(f"\nSuccess Rate:")
        print(f"  Caleb Williams: {caleb_advanced['success_rate']}%")
        print(f"  League Average: {league_advanced_avg['success_rate']}%")
        print(f"  Ranking: {success_rank} out of {total_qbs} QBs")
        print(f"  Difference: {'+' if caleb_advanced['success_rate'] - league_advanced_avg['success_rate'] > 0 else ''}{round(caleb_advanced['success_rate'] - league_advanced_avg['success_rate'], 2)}%")
        
        # CPOE
        cpoe_rank, _ = rank_qb_stats(advanced_stats_df, qb_name, 'cpoe', ascending=False)
        print(f"\nCPOE (Completion % Over Expected):")
        print(f"  Caleb Williams: {caleb_advanced['cpoe']}%")
        print(f"  League Average: {league_advanced_avg['cpoe']}%")
        print(f"  Ranking: {cpoe_rank} out of {total_qbs} QBs")
        print(f"  Difference: {'+' if caleb_advanced['cpoe'] - league_advanced_avg['cpoe'] > 0 else ''}{round(caleb_advanced['cpoe'] - league_advanced_avg['cpoe'], 2)}%")
    
    # Compile results
    results = {
        'season': season,
        'basic_stats': caleb_basic,
        'advanced_stats': caleb_advanced,
        'league_basic_avg': league_basic_avg,
        'league_advanced_avg': league_advanced_avg,
        'rankings': {
            'completion_pct': comp_pct_rank,
            'yards_per_attempt': ypa_rank,
            'td_int_ratio': td_int_rank,
            'passer_rating': rating_rank,
            'epa_per_dropback': epa_rank if caleb_advanced else None,
            'success_rate': success_rank if caleb_advanced else None,
            'cpoe': cpoe_rank if caleb_advanced else None
        },
        'total_qbs': total_qbs
    }
    
    return results, basic_stats_df, advanced_stats_df

def print_article_format(results_2024, results_2025=None):
    """Print statistics in article format with blanks filled in"""
    
    print(f"\n{'='*70}")
    print("ARTICLE FORMAT - STATISTICS FILLED IN")
    print("="*70)
    
    if results_2024:
        r = results_2024
        basic = r['basic_stats']
        advanced = r['advanced_stats']
        league_basic = r['league_basic_avg']
        league_advanced = r['league_advanced_avg']
        ranks = r['rankings']
        total = r['total_qbs']
        
        print(f"\n2024 SEASON (Year 1):")
        print("-"*70)
        
        print(f"\nWilliams completed {basic['completion_pct']}% of his passes in Year 1, ")
        print(f"ranking {ranks['completion_pct']} out of {total} in the league compared to the ")
        print(f"{league_basic['completion_pct']}% league average.")
        
        print(f"\nHis {basic['yards_per_attempt']} yards per attempt sat well below the league's ")
        print(f"{league_basic['yards_per_attempt']} mark, placing him {ranks['yards_per_attempt']} ")
        print(f"among {total} qualifying quarterbacks.")
        
        print(f"\nThe TD to INT ratio of {basic['pass_tds']} to {basic['interceptions']} ")
        print(f"showed a quarterback who could not protect the football consistently, and his ")
        print(f"{basic['passer_rating']} passer rating trailed the league average of ")
        print(f"{league_basic['passer_rating']} by a significant margin.")
        
        if advanced:
            print(f"\nThe advanced metrics painted an even bleaker picture. Williams posted ")
            print(f"an EPA per dropback of {advanced['epa_per_dropback']}, ranking {ranks['epa_per_dropback']} ")
            print(f"in the league against a {league_advanced['epa_per_dropback']} average.")
            
            print(f"\nHis success rate of {advanced['success_rate']}% fell short of the league's ")
            print(f"{league_advanced['success_rate']}% benchmark, meaning more than half his ")
            print(f"dropbacks failed to generate positive yardage relative to down and distance.")
            
            print(f"\nHis CPOE (completion percentage over expected) of {advanced['cpoe']}% ")
            print(f"indicated he was missing throws that NFL quarterbacks are expected to complete ")
            print(f"based on coverage, separation, and target depth.")
    
    if results_2025:
        print(f"\n\n2025 SEASON (Year 2) - IMPROVEMENT:")
        print("-"*70)
        r = results_2025
        basic = r['basic_stats']
        advanced = r['advanced_stats']
        league_basic = r['league_basic_avg']
        league_advanced = r['league_advanced_avg']
        ranks = r['rankings']
        total = r['total_qbs']
        
        print(f"\nCompletion %: {basic['completion_pct']}% (Rank: {ranks['completion_pct']}/{total})")
        print(f"Yards/Attempt: {basic['yards_per_attempt']} (Rank: {ranks['yards_per_attempt']}/{total})")
        print(f"TD-INT Ratio: {basic['td_int_ratio']} (Rank: {ranks['td_int_ratio']}/{total})")
        print(f"Passer Rating: {basic['passer_rating']} (Rank: {ranks['passer_rating']}/{total})")
        if advanced:
            print(f"EPA/Dropback: {advanced['epa_per_dropback']} (Rank: {ranks['epa_per_dropback']}/{total})")
            print(f"Success Rate: {advanced['success_rate']}% (Rank: {ranks['success_rate']}/{total})")
            print(f"CPOE: {advanced['cpoe']}% (Rank: {ranks['cpoe']}/{total})")

def main():
    """Main analysis function"""
    
    # Load data
    df_2024 = load_season_data(2024)
    df_2025 = load_season_data(2025)
    
    results_2024 = None
    results_2025 = None
    
    # Analyze 2024 season
    if df_2024 is not None:
        results_2024, basic_2024, advanced_2024 = generate_full_report(df_2024, 2024)
    
    # Analyze 2025 season
    if df_2025 is not None:
        results_2025, basic_2025, advanced_2025 = generate_full_report(df_2025, 2025)
    
    # Print article format
    print_article_format(results_2024, results_2025)
    
    # Export to CSV
    if results_2024:
        # Combine basic and advanced stats
        output_2024 = {**results_2024['basic_stats'], **results_2024['advanced_stats']}
        output_2024['season'] = 2024
        
        # Add rankings
        for stat, rank in results_2024['rankings'].items():
            output_2024[f'{stat}_rank'] = rank
        
        # Add league averages
        for stat, val in results_2024['league_basic_avg'].items():
            output_2024[f'league_avg_{stat}'] = val
        for stat, val in results_2024['league_advanced_avg'].items():
            output_2024[f'league_avg_{stat}'] = val
        
        df_output = pd.DataFrame([output_2024])
        df_output.to_csv('../output/caleb_williams_passing_stats_2024.csv', index=False)
        print(f"\n\n2024 stats exported to: ../output/caleb_williams_passing_stats_2024.csv")
        
        # Export full rankings
        basic_2024.to_csv('../output/all_qb_basic_passing_stats_2024.csv', index=False)
        advanced_2024.to_csv('../output/all_qb_advanced_passing_stats_2024.csv', index=False)
        print(f"2024 QB rankings exported")
    
    if results_2025:
        output_2025 = {**results_2025['basic_stats'], **results_2025['advanced_stats']}
        output_2025['season'] = 2025
        
        for stat, rank in results_2025['rankings'].items():
            output_2025[f'{stat}_rank'] = rank
        
        for stat, val in results_2025['league_basic_avg'].items():
            output_2025[f'league_avg_{stat}'] = val
        for stat, val in results_2025['league_advanced_avg'].items():
            output_2025[f'league_avg_{stat}'] = val
        
        df_output = pd.DataFrame([output_2025])
        df_output.to_csv('../output/caleb_williams_passing_stats_2025.csv', index=False)
        print(f"2025 stats exported to: ../output/caleb_williams_passing_stats_2025.csv")
        
        # Export full rankings
        basic_2025.to_csv('../output/all_qb_basic_passing_stats_2025.csv', index=False)
        advanced_2025.to_csv('../output/all_qb_advanced_passing_stats_2025.csv', index=False)
        print(f"2025 QB rankings exported")

if __name__ == "__main__":
    main()
