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

def get_red_zone_stats(df, qb_name):
    """Calculate red zone statistics for a QB"""
    
    # Red zone is defined as inside the opponent's 20 yard line (yardline_100 <= 20)
    red_zone_plays = df[
        (df['yardline_100'] <= 20) &
        (df['yardline_100'] > 0) &
        (
            (df['passer_player_name'] == qb_name) |
            (df['rusher_player_name'] == qb_name)
        )
    ].copy()
    
    if len(red_zone_plays) == 0:
        return None
    
    # Count touchdowns
    total_tds = red_zone_plays['touchdown'].sum()
    total_plays = len(red_zone_plays)
    td_rate = (total_tds / total_plays * 100) if total_plays > 0 else 0
    
    # Interception rate in red zone
    interceptions = red_zone_plays['interception'].sum()
    pass_attempts = len(red_zone_plays[red_zone_plays['pass_attempt'] == 1])
    int_rate = (interceptions / pass_attempts * 100) if pass_attempts > 0 else 0
    
    # Average depth of target in red zone
    red_zone_passes = red_zone_plays[red_zone_plays['pass_attempt'] == 1]
    avg_dot = red_zone_passes['air_yards'].mean() if len(red_zone_passes) > 0 else 0
    
    # Additional metrics
    completions = red_zone_passes['complete_pass'].sum() if len(red_zone_passes) > 0 else 0
    completion_rate = (completions / pass_attempts * 100) if pass_attempts > 0 else 0
    
    # EPA in red zone
    avg_epa = red_zone_plays['epa'].mean()
    
    # Success rate
    successful = len(red_zone_plays[red_zone_plays['success'] == 1])
    success_rate = (successful / total_plays * 100) if total_plays > 0 else 0
    
    return {
        'qb_name': qb_name,
        'total_plays': int(total_plays),
        'touchdowns': int(total_tds),
        'td_rate': round(td_rate, 2),
        'pass_attempts': int(pass_attempts),
        'interceptions': int(interceptions),
        'int_rate': round(int_rate, 2),
        'avg_depth_of_target': round(avg_dot, 2),
        'completion_rate': round(completion_rate, 2),
        'avg_epa': round(avg_epa, 4),
        'success_rate': round(success_rate, 2)
    }

def calculate_league_red_zone_avg(df, season):
    """Calculate league averages for red zone stats"""
    # Get qualifying QBs (100+ pass attempts overall)
    pass_attempts = df[df['pass_attempt'] == 1].groupby('passer_player_name').size()
    potential_qbs = pass_attempts[pass_attempts >= 100].index.tolist()
    
    all_stats = []
    
    for qb in potential_qbs:
        stats = get_red_zone_stats(df, qb)
        if stats and stats['total_plays'] >= 10:  # At least 10 red zone plays
            all_stats.append(stats)
    
    if not all_stats:
        return None
    
    stats_df = pd.DataFrame(all_stats)
    
    return {
        'league_avg_td_rate': round(stats_df['td_rate'].mean(), 2),
        'league_avg_int_rate': round(stats_df['int_rate'].mean(), 2),
        'league_avg_dot': round(stats_df['avg_depth_of_target'].mean(), 2),
        'league_avg_epa': round(stats_df['avg_epa'].mean(), 4),
        'total_qbs': len(stats_df)
    }, stats_df

def rank_qb_red_zone(stats_df, qb_name, stat_column, ascending=False):
    """Rank a QB in red zone statistics"""
    sorted_df = stats_df.sort_values(by=stat_column, ascending=ascending).reset_index(drop=True)
    sorted_df['rank'] = range(1, len(sorted_df) + 1)
    
    qb_row = sorted_df[sorted_df['qb_name'] == qb_name]
    if len(qb_row) > 0:
        return int(qb_row.iloc[0]['rank']), len(sorted_df)
    return None, len(sorted_df)

def generate_red_zone_report(df, season, qb_name='C.Williams'):
    """Generate comprehensive red zone report"""
    
    print(f"\n{'='*70}")
    print(f"CALEB WILLIAMS RED ZONE ANALYSIS - {season} SEASON")
    print(f"{'='*70}\n")
    
    # Get Caleb's stats
    caleb_stats = get_red_zone_stats(df, qb_name)
    
    if not caleb_stats:
        print(f"No red zone data found for {qb_name}")
        return None
    
    # Get league averages
    league_avg, league_stats_df = calculate_league_red_zone_avg(df, season)
    
    if not league_avg:
        print("Could not calculate league averages")
        return None
    
    # Rank Caleb
    td_rate_rank, total_qbs = rank_qb_red_zone(league_stats_df, qb_name, 'td_rate', ascending=False)
    int_rate_rank, _ = rank_qb_red_zone(league_stats_df, qb_name, 'int_rate', ascending=True)
    
    print("RED ZONE PERFORMANCE (Inside 20 Yard Line)")
    print("="*70)
    
    print(f"\nTouchdown Rate:")
    print(f"  Caleb Williams: {caleb_stats['td_rate']}%")
    print(f"  League Average: {league_avg['league_avg_td_rate']}%")
    print(f"  Ranking: {td_rate_rank} out of {total_qbs} QBs")
    print(f"  Touchdowns: {caleb_stats['touchdowns']} in {caleb_stats['total_plays']} plays")
    
    print(f"\nInterception Rate:")
    print(f"  Caleb Williams: {caleb_stats['int_rate']}%")
    print(f"  League Average: {league_avg['league_avg_int_rate']}%")
    print(f"  Ranking: {int_rate_rank} out of {total_qbs} QBs (lower is better)")
    print(f"  Interceptions: {caleb_stats['interceptions']} in {caleb_stats['pass_attempts']} pass attempts")
    
    print(f"\nAverage Depth of Target:")
    print(f"  Caleb Williams: {caleb_stats['avg_depth_of_target']} yards")
    print(f"  League Average: {league_avg['league_avg_dot']} yards")
    
    print(f"\nAdditional Metrics:")
    print(f"  Completion Rate: {caleb_stats['completion_rate']}%")
    print(f"  EPA per Play: {caleb_stats['avg_epa']}")
    print(f"  Success Rate: {caleb_stats['success_rate']}%")
    
    return {
        'season': season,
        'caleb_stats': caleb_stats,
        'league_avg': league_avg,
        'rankings': {
            'td_rate': td_rate_rank,
            'int_rate': int_rate_rank
        },
        'total_qbs': total_qbs
    }, league_stats_df

def print_article_format(results):
    """Print in article format"""
    if not results:
        return
    
    print(f"\n{'='*70}")
    print("ARTICLE FORMAT - RED ZONE STATISTICS")
    print("="*70)
    
    stats = results['caleb_stats']
    league = results['league_avg']
    ranks = results['rankings']
    total = results['total_qbs']
    
    print(f"\nRed Zone Statistics (Inside 20 Yard Line):")
    print(f"  TD rate inside 20: {stats['td_rate']}%")
    print(f"  (League avg: {league['league_avg_td_rate']}%, Rank: {ranks['td_rate']} out of {total})")
    print(f"\n  Interception rate: {stats['int_rate']}%")
    print(f"  Average depth of target: {stats['avg_depth_of_target']} yards")

def main():
    """Main analysis function"""
    
    # Load data
    df_2024 = load_season_data(2024)
    df_2025 = load_season_data(2025)
    
    results_2024 = None
    results_2025 = None
    
    # Analyze 2024 season
    if df_2024 is not None:
        results_2024, league_2024 = generate_red_zone_report(df_2024, 2024)
    
    # Analyze 2025 season
    if df_2025 is not None:
        results_2025, league_2025 = generate_red_zone_report(df_2025, 2025)
    
    # Print article format
    if results_2024:
        print_article_format(results_2024)
    
    if results_2025:
        print(f"\n2025 SEASON:")
        print_article_format(results_2025)
    
    # Export to CSV
    if results_2024:
        output = {**results_2024['caleb_stats']}
        output['season'] = 2024
        for key, val in results_2024['league_avg'].items():
            output[f'league_{key}'] = val
        for key, val in results_2024['rankings'].items():
            output[f'{key}_rank'] = val
        
        df_output = pd.DataFrame([output])
        df_output.to_csv('../output/caleb_williams_red_zone_stats_2024.csv', index=False)
        print(f"\n\n2024 red zone stats exported to: ../output/caleb_williams_red_zone_stats_2024.csv")
        
        league_2024.to_csv('../output/all_qb_red_zone_stats_2024.csv', index=False)
        print(f"2024 league red zone stats exported")
    
    if results_2025:
        output = {**results_2025['caleb_stats']}
        output['season'] = 2025
        for key, val in results_2025['league_avg'].items():
            output[f'league_{key}'] = val
        for key, val in results_2025['rankings'].items():
            output[f'{key}_rank'] = val
        
        df_output = pd.DataFrame([output])
        df_output.to_csv('../output/caleb_williams_red_zone_stats_2025.csv', index=False)
        print(f"2025 red zone stats exported to: ../output/caleb_williams_red_zone_stats_2025.csv")
        
        league_2025.to_csv('../output/all_qb_red_zone_stats_2025.csv', index=False)
        print(f"2025 league red zone stats exported")

if __name__ == "__main__":
    main()
