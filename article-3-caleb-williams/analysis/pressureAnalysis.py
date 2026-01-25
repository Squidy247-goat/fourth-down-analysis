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

def get_pressure_stats(df, qb_name):
    """Calculate statistics when QB is under pressure"""
    
    # Get all dropbacks for this QB
    qb_dropbacks = df[
        (df['passer_player_name'] == qb_name) &
        (df['qb_dropback'] == 1)
    ].copy()
    
    if len(qb_dropbacks) == 0:
        return None
    
    # Filter for plays where QB was hit
    # qb_hit indicates pressure/contact
    pressure_plays = qb_dropbacks[qb_dropbacks['qb_hit'] == 1]
    
    # Calculate completion percentage under pressure
    if len(pressure_plays) > 0:
        pass_attempts_under_pressure = len(pressure_plays[pressure_plays['pass_attempt'] == 1])
        completions_under_pressure = pressure_plays['complete_pass'].sum()
        completion_pct_pressure = (completions_under_pressure / pass_attempts_under_pressure * 100) if pass_attempts_under_pressure > 0 else 0
    else:
        completion_pct_pressure = 0
        pass_attempts_under_pressure = 0
        completions_under_pressure = 0
    
    # Sack rate (sacks / total dropbacks)
    total_dropbacks = len(qb_dropbacks)
    sacks = qb_dropbacks['sack'].sum()
    sack_rate = (sacks / total_dropbacks * 100) if total_dropbacks > 0 else 0
    
    # Turnover-worthy plays under pressure
    # Turnovers = interceptions + fumbles lost
    turnovers = pressure_plays['interception'].sum() + pressure_plays['fumble_lost'].sum()
    turnover_worthy_rate = (turnovers / len(pressure_plays) * 100) if len(pressure_plays) > 0 else 0
    
    # Additional metrics
    # EPA under pressure
    epa_under_pressure = pressure_plays['epa'].mean() if len(pressure_plays) > 0 else 0
    
    # Success rate under pressure
    success_under_pressure = len(pressure_plays[pressure_plays['success'] == 1])
    success_rate_pressure = (success_under_pressure / len(pressure_plays) * 100) if len(pressure_plays) > 0 else 0
    
    # Overall completion percentage (for comparison)
    all_pass_attempts = len(qb_dropbacks[qb_dropbacks['pass_attempt'] == 1])
    all_completions = qb_dropbacks['complete_pass'].sum()
    overall_completion_pct = (all_completions / all_pass_attempts * 100) if all_pass_attempts > 0 else 0
    
    # Scrambles (QB runs when under pressure)
    scrambles = qb_dropbacks['qb_scramble'].sum()
    
    return {
        'qb_name': qb_name,
        'total_dropbacks': int(total_dropbacks),
        'pressure_plays': int(len(pressure_plays)),
        'pressure_rate': round((len(pressure_plays) / total_dropbacks * 100) if total_dropbacks > 0 else 0, 2),
        'completion_pct_under_pressure': round(completion_pct_pressure, 2),
        'pass_attempts_under_pressure': int(pass_attempts_under_pressure),
        'completions_under_pressure': int(completions_under_pressure),
        'overall_completion_pct': round(overall_completion_pct, 2),
        'sacks': int(sacks),
        'sack_rate': round(sack_rate, 2),
        'turnovers_under_pressure': int(turnovers),
        'turnover_worthy_rate': round(turnover_worthy_rate, 2),
        'epa_under_pressure': round(epa_under_pressure, 4),
        'success_rate_pressure': round(success_rate_pressure, 2),
        'scrambles': int(scrambles)
    }

def calculate_time_to_throw(df, qb_name):
    """
    Calculate average time to throw
    This is a proxy calculation based on play duration
    """
    qb_passes = df[
        (df['passer_player_name'] == qb_name) &
        (df['pass_attempt'] == 1)
    ].copy()
    
    if len(qb_passes) == 0:
        return None
    
    # Use CPOE and other metrics as proxy for quick/slow release
    # Quick passes typically have lower air yards
    avg_air_yards = qb_passes['air_yards'].mean()
    
    # Estimate time to throw based on air yards
    # Typically: short passes (<5 yards) = ~2.3s, medium (5-15) = ~2.6s, deep (15+) = ~3.0s+
    if avg_air_yards < 5:
        estimated_time = 2.3
    elif avg_air_yards < 15:
        estimated_time = 2.3 + (avg_air_yards - 5) * 0.03
    else:
        estimated_time = 2.6 + (avg_air_yards - 15) * 0.02
    
    return {
        'avg_air_yards': round(avg_air_yards, 2),
        'estimated_time_to_throw': round(estimated_time, 2)
    }

def calculate_league_pressure_avg(df, season):
    """Calculate league averages for pressure statistics"""
    # Get qualifying QBs (100+ pass attempts overall)
    pass_attempts = df[df['pass_attempt'] == 1].groupby('passer_player_name').size()
    potential_qbs = pass_attempts[pass_attempts >= 100].index.tolist()
    
    all_stats = []
    
    for qb in potential_qbs:
        stats = get_pressure_stats(df, qb)
        time_stats = calculate_time_to_throw(df, qb)
        
        if stats and stats['total_dropbacks'] >= 100:
            if time_stats:
                stats['estimated_time_to_throw'] = time_stats['estimated_time_to_throw']
                stats['avg_air_yards'] = time_stats['avg_air_yards']
            all_stats.append(stats)
    
    if not all_stats:
        return None
    
    stats_df = pd.DataFrame(all_stats)
    
    return {
        'league_avg_completion_pct_pressure': round(stats_df['completion_pct_under_pressure'].mean(), 2),
        'league_avg_sack_rate': round(stats_df['sack_rate'].mean(), 2),
        'league_avg_time_to_throw': round(stats_df['estimated_time_to_throw'].mean(), 2),
        'league_avg_turnover_rate': round(stats_df['turnover_worthy_rate'].mean(), 2),
        'league_avg_epa_pressure': round(stats_df['epa_under_pressure'].mean(), 4),
        'total_qbs': len(stats_df)
    }, stats_df

def rank_qb_pressure(stats_df, qb_name, stat_column, ascending=False):
    """Rank a QB in pressure statistics"""
    sorted_df = stats_df.sort_values(by=stat_column, ascending=ascending).reset_index(drop=True)
    sorted_df['rank'] = range(1, len(sorted_df) + 1)
    
    qb_row = sorted_df[sorted_df['qb_name'] == qb_name]
    if len(qb_row) > 0:
        return int(qb_row.iloc[0]['rank']), len(sorted_df)
    return None, len(sorted_df)

def find_signature_moments(df, qb_name, team='CHI'):
    """Find notable bad games/plays for the QB"""
    
    # Group by game
    qb_games = df[
        (df['posteam'] == team) &
        (
            (df['passer_player_name'] == qb_name) |
            (df['rusher_player_name'] == qb_name)
        )
    ].copy()
    
    game_stats = []
    
    for game_id in qb_games['game_id'].unique():
        game = qb_games[qb_games['game_id'] == game_id]
        
        # Calculate game stats
        sacks = game['sack'].sum()
        turnovers = game['interception'].sum() + game['fumble_lost'].sum()
        total_epa = game['epa'].sum()
        
        # Get opponent
        opponent = game['defteam'].mode()[0] if len(game) > 0 else 'Unknown'
        
        # Get week
        week = game['week'].iloc[0] if len(game) > 0 else 0
        
        game_stats.append({
            'game_id': game_id,
            'week': week,
            'opponent': opponent,
            'sacks': int(sacks),
            'turnovers': int(turnovers),
            'total_epa': round(total_epa, 2),
            'plays': len(game)
        })
    
    # Sort by worst EPA
    game_stats_df = pd.DataFrame(game_stats)
    worst_games = game_stats_df.nsmallest(3, 'total_epa')
    
    return worst_games

def generate_pressure_report(df, season, qb_name='C.Williams', team='CHI'):
    """Generate comprehensive pressure statistics report"""
    
    print(f"\n{'='*70}")
    print(f"CALEB WILLIAMS UNDER PRESSURE ANALYSIS - {season} SEASON")
    print(f"{'='*70}\n")
    
    # Get Caleb's stats
    caleb_stats = get_pressure_stats(df, qb_name)
    caleb_time = calculate_time_to_throw(df, qb_name)
    
    if not caleb_stats:
        print(f"No pressure data found for {qb_name}")
        return None
    
    # Add time to throw
    if caleb_time:
        caleb_stats['estimated_time_to_throw'] = caleb_time['estimated_time_to_throw']
        caleb_stats['avg_air_yards'] = caleb_time['avg_air_yards']
    
    # Get league averages
    league_avg, league_stats_df = calculate_league_pressure_avg(df, season)
    
    if not league_avg:
        print("Could not calculate league averages")
        return None
    
    # Rank Caleb
    comp_rank, total_qbs = rank_qb_pressure(league_stats_df, qb_name, 'completion_pct_under_pressure', ascending=False)
    sack_rank, _ = rank_qb_pressure(league_stats_df, qb_name, 'sack_rate', ascending=True)
    time_rank, _ = rank_qb_pressure(league_stats_df, qb_name, 'estimated_time_to_throw', ascending=True)
    turnover_rank, _ = rank_qb_pressure(league_stats_df, qb_name, 'turnover_worthy_rate', ascending=True)
    
    print("PERFORMANCE UNDER PRESSURE")
    print("="*70)
    
    print(f"\nCompletion Percentage Under Pressure:")
    print(f"  Caleb Williams: {caleb_stats['completion_pct_under_pressure']}%")
    print(f"  Overall Completion %: {caleb_stats['overall_completion_pct']}%")
    print(f"  League Average (Under Pressure): {league_avg['league_avg_completion_pct_pressure']}%")
    print(f"  Ranking: {comp_rank} out of {total_qbs} QBs")
    print(f"  Pressure Plays: {caleb_stats['pressure_plays']} ({caleb_stats['pressure_rate']}% of dropbacks)")
    
    print(f"\nSack Rate:")
    print(f"  Caleb Williams: {caleb_stats['sack_rate']}%")
    print(f"  Sacks: {caleb_stats['sacks']} in {caleb_stats['total_dropbacks']} dropbacks")
    print(f"  League Average: {league_avg['league_avg_sack_rate']}%")
    print(f"  Ranking: {sack_rank} out of {total_qbs} QBs (lower is better)")
    
    print(f"\nTime to Throw (Estimated):")
    print(f"  Caleb Williams: {caleb_stats['estimated_time_to_throw']} seconds")
    print(f"  Average Air Yards: {caleb_stats['avg_air_yards']} yards")
    print(f"  League Average: {league_avg['league_avg_time_to_throw']} seconds")
    print(f"  Ranking: {time_rank} out of {total_qbs} QBs")
    
    print(f"\nTurnover-Worthy Play Rate (Under Pressure):")
    print(f"  Caleb Williams: {caleb_stats['turnover_worthy_rate']}%")
    print(f"  Turnovers Under Pressure: {caleb_stats['turnovers_under_pressure']}")
    print(f"  League Average: {league_avg['league_avg_turnover_rate']}%")
    print(f"  Ranking: {turnover_rank} out of {total_qbs} QBs (lower is better)")
    
    print(f"\nAdditional Metrics:")
    print(f"  EPA Under Pressure: {caleb_stats['epa_under_pressure']}")
    print(f"  Success Rate Under Pressure: {caleb_stats['success_rate_pressure']}%")
    print(f"  Scrambles: {caleb_stats['scrambles']}")
    
    # Find signature bad moments
    print(f"\n{'='*70}")
    print("SIGNATURE ROOKIE STRUGGLES (3 Worst Games by EPA)")
    print("="*70)
    worst_games = find_signature_moments(df, qb_name, team)
    
    for idx, game in worst_games.iterrows():
        print(f"\nWeek {game['week']} vs {game['opponent']}:")
        print(f"  Total EPA: {game['total_epa']}")
        print(f"  Sacks: {game['sacks']}")
        print(f"  Turnovers: {game['turnovers']}")
        print(f"  Total Plays: {game['plays']}")
    
    return {
        'season': season,
        'caleb_stats': caleb_stats,
        'league_avg': league_avg,
        'rankings': {
            'completion_pct_pressure': comp_rank,
            'sack_rate': sack_rank,
            'time_to_throw': time_rank,
            'turnover_rate': turnover_rank
        },
        'total_qbs': total_qbs,
        'worst_games': worst_games
    }, league_stats_df

def print_article_format(results):
    """Print in article format"""
    if not results:
        return
    
    print(f"\n{'='*70}")
    print("ARTICLE FORMAT - UNDER PRESSURE STATISTICS")
    print("="*70)
    
    stats = results['caleb_stats']
    league = results['league_avg']
    ranks = results['rankings']
    total = results['total_qbs']
    
    print(f"\nUnder Pressure:")
    print(f"  Completion percentage: {stats['completion_pct_under_pressure']}%")
    print(f"  (League avg: {league['league_avg_completion_pct_pressure']}%)")
    print(f"\n  Sack rate: {stats['sack_rate']}%")
    print(f"  (League avg: {league['league_avg_sack_rate']}%)")
    print(f"\n  Time to throw: {stats['estimated_time_to_throw']} seconds")
    print(f"  (League avg: {league['league_avg_time_to_throw']} seconds)")
    print(f"\n  Turnover-worthy play rate: {stats['turnover_worthy_rate']}%")
    print(f"  (League avg: {league['league_avg_turnover_rate']}%)")
    
    print(f"\n\nSignature Rookie Moments (3 worst games by EPA):")
    for idx, game in results['worst_games'].iterrows():
        print(f"  - Week {game['week']} vs {game['opponent']}: {game['total_epa']} EPA, {game['sacks']} sacks, {game['turnovers']} turnovers")

def main():
    """Main analysis function"""
    
    # Load data
    df_2024 = load_season_data(2024)
    df_2025 = load_season_data(2025)
    
    results_2024 = None
    results_2025 = None
    
    # Analyze 2024 season
    if df_2024 is not None:
        results_2024, league_2024 = generate_pressure_report(df_2024, 2024)
    
    # Analyze 2025 season
    if df_2025 is not None:
        results_2025, league_2025 = generate_pressure_report(df_2025, 2025)
    
    # Print article format
    if results_2024:
        print_article_format(results_2024)
    
    if results_2025:
        print(f"\n\n2025 SEASON:")
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
        df_output.to_csv('../output/caleb_williams_pressure_stats_2024.csv', index=False)
        print(f"\n\n2024 pressure stats exported to: ../output/caleb_williams_pressure_stats_2024.csv")
        
        league_2024.to_csv('../output/all_qb_pressure_stats_2024.csv', index=False)
        print(f"2024 league pressure stats exported")
        
        results_2024['worst_games'].to_csv('../output/caleb_williams_worst_games_2024.csv', index=False)
        print(f"2024 worst games exported")
    
    if results_2025:
        output = {**results_2025['caleb_stats']}
        output['season'] = 2025
        for key, val in results_2025['league_avg'].items():
            output[f'league_{key}'] = val
        for key, val in results_2025['rankings'].items():
            output[f'{key}_rank'] = val
        
        df_output = pd.DataFrame([output])
        df_output.to_csv('../output/caleb_williams_pressure_stats_2025.csv', index=False)
        print(f"2025 pressure stats exported to: ../output/caleb_williams_pressure_stats_2025.csv")
        
        league_2025.to_csv('../output/all_qb_pressure_stats_2025.csv', index=False)
        print(f"2025 league pressure stats exported")
        
        results_2025['worst_games'].to_csv('../output/caleb_williams_worst_games_2025.csv', index=False)
        print(f"2025 worst games exported")

if __name__ == "__main__":
    main()
