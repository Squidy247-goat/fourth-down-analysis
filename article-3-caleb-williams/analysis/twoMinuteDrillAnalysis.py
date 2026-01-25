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

def get_two_minute_drill_stats(df, qb_name, team):
    """Calculate two-minute drill statistics"""
    
    # Two-minute drill: final 2 minutes of either half
    # Half seconds remaining <= 120 (2 minutes = 120 seconds)
    two_min_plays = df[
        (df['half_seconds_remaining'] <= 120) &
        (df['half_seconds_remaining'] > 0) &
        (df['posteam'] == team) &
        (
            (df['passer_player_name'] == qb_name) |
            (df['rusher_player_name'] == qb_name)
        )
    ].copy()
    
    if len(two_min_plays) == 0:
        return None
    
    # Group by drive to calculate drive-level statistics
    drives = two_min_plays.groupby('drive')
    
    total_drives = len(drives)
    drives_with_points = 0
    total_points = 0
    
    # Analyze each drive
    for drive_id, drive_plays in drives:
        # Check if drive ended in points (TD or FG)
        drive_score = drive_plays['posteam_score_post'].iloc[-1] - drive_plays['posteam_score'].iloc[0]
        if drive_score > 0:
            drives_with_points += 1
            total_points += drive_score
    
    # Calculate drives ending in points percentage
    drives_ending_in_points_pct = (drives_with_points / total_drives * 100) if total_drives > 0 else 0
    
    # Count games to calculate points per game
    games = two_min_plays['game_id'].nunique()
    points_per_game = total_points / games if games > 0 else 0
    
    # Success rate in two-minute situations
    successful_plays = len(two_min_plays[two_min_plays['success'] == 1])
    total_plays = len(two_min_plays)
    success_rate = (successful_plays / total_plays * 100) if total_plays > 0 else 0
    
    # EPA
    avg_epa = two_min_plays['epa'].mean()
    
    # Additional metrics
    pass_attempts = len(two_min_plays[two_min_plays['pass_attempt'] == 1])
    completions = two_min_plays['complete_pass'].sum()
    completion_rate = (completions / pass_attempts * 100) if pass_attempts > 0 else 0
    
    touchdowns = two_min_plays['touchdown'].sum()
    interceptions = two_min_plays['interception'].sum()
    
    return {
        'qb_name': qb_name,
        'team': team,
        'total_drives': int(total_drives),
        'drives_with_points': int(drives_with_points),
        'drives_ending_in_points_pct': round(drives_ending_in_points_pct, 2),
        'total_points': int(total_points),
        'games': int(games),
        'points_per_game': round(points_per_game, 2),
        'total_plays': int(total_plays),
        'success_rate': round(success_rate, 2),
        'avg_epa': round(avg_epa, 4),
        'pass_attempts': int(pass_attempts),
        'completions': int(completions),
        'completion_rate': round(completion_rate, 2),
        'touchdowns': int(touchdowns),
        'interceptions': int(interceptions)
    }

def calculate_league_two_minute_avg(df, season):
    """Calculate league averages for two-minute drill stats"""
    # Get qualifying QBs (100+ pass attempts overall)
    pass_attempts = df[df['pass_attempt'] == 1].groupby('passer_player_name').size()
    potential_qbs = pass_attempts[pass_attempts >= 100].index.tolist()
    
    # Get team for each QB (most common team they played for)
    qb_teams = {}
    for qb in potential_qbs:
        qb_plays = df[df['passer_player_name'] == qb]
        if len(qb_plays) > 0:
            qb_teams[qb] = qb_plays['posteam'].mode()[0]
    
    all_stats = []
    
    for qb, team in qb_teams.items():
        stats = get_two_minute_drill_stats(df, qb, team)
        if stats and stats['total_plays'] >= 10:  # At least 10 plays in two-minute situations
            all_stats.append(stats)
    
    if not all_stats:
        return None
    
    stats_df = pd.DataFrame(all_stats)
    
    return {
        'league_avg_drives_ending_in_points': round(stats_df['drives_ending_in_points_pct'].mean(), 2),
        'league_avg_points_per_game': round(stats_df['points_per_game'].mean(), 2),
        'league_avg_success_rate': round(stats_df['success_rate'].mean(), 2),
        'league_avg_epa': round(stats_df['avg_epa'].mean(), 4),
        'total_qbs': len(stats_df)
    }, stats_df

def rank_qb_two_minute(stats_df, qb_name, stat_column, ascending=False):
    """Rank a QB in two-minute drill statistics"""
    sorted_df = stats_df.sort_values(by=stat_column, ascending=ascending).reset_index(drop=True)
    sorted_df['rank'] = range(1, len(sorted_df) + 1)
    
    qb_row = sorted_df[sorted_df['qb_name'] == qb_name]
    if len(qb_row) > 0:
        return int(qb_row.iloc[0]['rank']), len(sorted_df)
    return None, len(sorted_df)

def generate_two_minute_report(df, season, qb_name='C.Williams', team='CHI'):
    """Generate comprehensive two-minute drill report"""
    
    print(f"\n{'='*70}")
    print(f"CALEB WILLIAMS TWO-MINUTE DRILL ANALYSIS - {season} SEASON")
    print(f"{'='*70}\n")
    
    # Get Caleb's stats
    caleb_stats = get_two_minute_drill_stats(df, qb_name, team)
    
    if not caleb_stats:
        print(f"No two-minute drill data found for {qb_name}")
        return None
    
    # Get league averages
    league_avg, league_stats_df = calculate_league_two_minute_avg(df, season)
    
    if not league_avg:
        print("Could not calculate league averages")
        return None
    
    # Rank Caleb
    points_rank, total_qbs = rank_qb_two_minute(league_stats_df, qb_name, 'drives_ending_in_points_pct', ascending=False)
    ppg_rank, _ = rank_qb_two_minute(league_stats_df, qb_name, 'points_per_game', ascending=False)
    success_rank, _ = rank_qb_two_minute(league_stats_df, qb_name, 'success_rate', ascending=False)
    
    print("TWO-MINUTE DRILL PERFORMANCE (Final 2 Minutes of Halves)")
    print("="*70)
    
    print(f"\nDrives Ending in Points:")
    print(f"  Caleb Williams: {caleb_stats['drives_ending_in_points_pct']}%")
    print(f"  ({caleb_stats['drives_with_points']} of {caleb_stats['total_drives']} drives)")
    print(f"  League Average: {league_avg['league_avg_drives_ending_in_points']}%")
    print(f"  Ranking: {points_rank} out of {total_qbs} QBs")
    
    print(f"\nPoints Per Game (Final 2 Min):")
    print(f"  Caleb Williams: {caleb_stats['points_per_game']} points/game")
    print(f"  Total Points: {caleb_stats['total_points']} in {caleb_stats['games']} games")
    print(f"  League Average: {league_avg['league_avg_points_per_game']} points/game")
    print(f"  Ranking: {ppg_rank} out of {total_qbs} QBs")
    
    print(f"\nSuccess Rate:")
    print(f"  Caleb Williams: {caleb_stats['success_rate']}%")
    print(f"  League Average: {league_avg['league_avg_success_rate']}%")
    print(f"  Ranking: {success_rank} out of {total_qbs} QBs")
    
    print(f"\nAdditional Metrics:")
    print(f"  Total Plays: {caleb_stats['total_plays']}")
    print(f"  Completion Rate: {caleb_stats['completion_rate']}%")
    print(f"  EPA per Play: {caleb_stats['avg_epa']}")
    print(f"  Touchdowns: {caleb_stats['touchdowns']}")
    print(f"  Interceptions: {caleb_stats['interceptions']}")
    
    return {
        'season': season,
        'caleb_stats': caleb_stats,
        'league_avg': league_avg,
        'rankings': {
            'drives_ending_in_points': points_rank,
            'points_per_game': ppg_rank,
            'success_rate': success_rank
        },
        'total_qbs': total_qbs
    }, league_stats_df

def print_article_format(results):
    """Print in article format"""
    if not results:
        return
    
    print(f"\n{'='*70}")
    print("ARTICLE FORMAT - TWO-MINUTE DRILL STATISTICS")
    print("="*70)
    
    stats = results['caleb_stats']
    league = results['league_avg']
    ranks = results['rankings']
    total = results['total_qbs']
    
    print(f"\nTwo-Minute Drill (Final 2 minutes of halves):")
    print(f"  Drives ending in points: {stats['drives_ending_in_points_pct']}%")
    print(f"  (League avg: {league['league_avg_drives_ending_in_points']}%, Rank: {ranks['drives_ending_in_points']} out of {total})")
    print(f"\n  Points per game (final 2 min of halves): {stats['points_per_game']}")
    print(f"  (League avg: {league['league_avg_points_per_game']})")
    print(f"\n  Success rate: {stats['success_rate']}%")
    print(f"  (League avg: {league['league_avg_success_rate']}%)")

def main():
    """Main analysis function"""
    
    # Load data
    df_2024 = load_season_data(2024)
    df_2025 = load_season_data(2025)
    
    results_2024 = None
    results_2025 = None
    
    # Analyze 2024 season
    if df_2024 is not None:
        results_2024, league_2024 = generate_two_minute_report(df_2024, 2024)
    
    # Analyze 2025 season
    if df_2025 is not None:
        results_2025, league_2025 = generate_two_minute_report(df_2025, 2025)
    
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
        df_output.to_csv('../output/caleb_williams_two_minute_drill_2024.csv', index=False)
        print(f"\n\n2024 two-minute drill stats exported to: ../output/caleb_williams_two_minute_drill_2024.csv")
        
        league_2024.to_csv('../output/all_qb_two_minute_drill_2024.csv', index=False)
        print(f"2024 league two-minute drill stats exported")
    
    if results_2025:
        output = {**results_2025['caleb_stats']}
        output['season'] = 2025
        for key, val in results_2025['league_avg'].items():
            output[f'league_{key}'] = val
        for key, val in results_2025['rankings'].items():
            output[f'{key}_rank'] = val
        
        df_output = pd.DataFrame([output])
        df_output.to_csv('../output/caleb_williams_two_minute_drill_2025.csv', index=False)
        print(f"2025 two-minute drill stats exported to: ../output/caleb_williams_two_minute_drill_2025.csv")
        
        league_2025.to_csv('../output/all_qb_two_minute_drill_2025.csv', index=False)
        print(f"2025 league two-minute drill stats exported")

if __name__ == "__main__":
    main()
