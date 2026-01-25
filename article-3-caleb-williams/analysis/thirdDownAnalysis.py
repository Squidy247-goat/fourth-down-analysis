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

def filter_caleb_williams_third_downs(df, season):
    """Filter for 3rd down plays where Caleb Williams was involved"""
    
    # Filter for:
    # 1. Third down plays (down == 3)
    # 2. Chicago Bears on offense (posteam == 'CHI')
    # 3. Caleb Williams either passed or rushed
    third_down_plays = df[
        (df['down'] == 3) &
        (df['posteam'] == 'CHI') &
        (
            (df['passer_player_name'] == 'C.Williams') |
            (df['rusher_player_name'] == 'C.Williams')
        )
    ].copy()
    
    print(f"\n{season} Season - Caleb Williams 3rd Down Plays:")
    print(f"Total 3rd down attempts: {len(third_down_plays)}")
    
    return third_down_plays

def calculate_third_down_metrics(plays_df, season):
    """Calculate 3rd down conversion statistics"""
    
    if len(plays_df) == 0:
        print(f"No plays found for {season}")
        return None
    
    # Count conversions and failures
    conversions = plays_df['third_down_converted'].sum()
    failures = plays_df['third_down_failed'].sum()
    total_attempts = conversions + failures
    
    # Calculate conversion rate
    if total_attempts > 0:
        conversion_rate = (conversions / total_attempts) * 100
    else:
        conversion_rate = 0
    
    # EPA on third down
    avg_epa = plays_df['epa'].mean()
    
    # Tendency analysis - check down vs attack
    # Check downs are typically short passes (<5 yards)
    # Attacks are deeper passes (>=5 yards)
    pass_plays = plays_df[(plays_df['pass_attempt'] == 1) | (plays_df['sack'] == 1)]
    if len(pass_plays) > 0:
        # Use air_yards to determine if it's a check down or attack
        check_downs = pass_plays[pass_plays['air_yards'] < 5]
        attacks = pass_plays[pass_plays['air_yards'] >= 5]
        check_down_rate = (len(check_downs) / len(pass_plays) * 100) if len(pass_plays) > 0 else 0
        attack_rate = (len(attacks) / len(pass_plays) * 100) if len(pass_plays) > 0 else 0
    else:
        check_down_rate = 0
        attack_rate = 0
    
    # Break down by play type
    pass_plays_only = plays_df[plays_df['pass_attempt'] == 1]
    rush_plays = plays_df[plays_df['rush_attempt'] == 1]
    
    pass_conversions = pass_plays_only['third_down_converted'].sum() if len(pass_plays_only) > 0 else 0
    pass_attempts = pass_conversions + pass_plays_only['third_down_failed'].sum() if len(pass_plays_only) > 0 else 0
    pass_conversion_rate = (pass_conversions / pass_attempts * 100) if pass_attempts > 0 else 0
    
    rush_conversions = rush_plays['third_down_converted'].sum() if len(rush_plays) > 0 else 0
    rush_attempts = rush_conversions + rush_plays['third_down_failed'].sum() if len(rush_plays) > 0 else 0
    rush_conversion_rate = (rush_conversions / rush_attempts * 100) if rush_attempts > 0 else 0
    
    # Calculate average yards to go and yards gained
    avg_ydstogo = plays_df['ydstogo'].mean()
    avg_yards_gained = plays_df['yards_gained'].mean()
    
    # Distance breakdown
    short_distance = plays_df[plays_df['ydstogo'] <= 3]
    medium_distance = plays_df[(plays_df['ydstogo'] > 3) & (plays_df['ydstogo'] <= 7)]
    long_distance = plays_df[plays_df['ydstogo'] > 7]
    
    short_conv_rate = (short_distance['third_down_converted'].sum() / 
                       (short_distance['third_down_converted'].sum() + short_distance['third_down_failed'].sum()) * 100) \
                       if len(short_distance) > 0 and (short_distance['third_down_converted'].sum() + short_distance['third_down_failed'].sum()) > 0 else 0
    medium_conv_rate = (medium_distance['third_down_converted'].sum() / 
                        (medium_distance['third_down_converted'].sum() + medium_distance['third_down_failed'].sum()) * 100) \
                        if len(medium_distance) > 0 and (medium_distance['third_down_converted'].sum() + medium_distance['third_down_failed'].sum()) > 0 else 0
    long_conv_rate = (long_distance['third_down_converted'].sum() / 
                      (long_distance['third_down_converted'].sum() + long_distance['third_down_failed'].sum()) * 100) \
                      if len(long_distance) > 0 and (long_distance['third_down_converted'].sum() + long_distance['third_down_failed'].sum()) > 0 else 0
    
    metrics = {
        'season': season,
        'total_attempts': int(total_attempts),
        'conversions': int(conversions),
        'failures': int(failures),
        'conversion_rate': round(conversion_rate, 2),
        'avg_epa': round(avg_epa, 4),
        'check_down_rate': round(check_down_rate, 2),
        'attack_rate': round(attack_rate, 2),
        'pass_attempts': int(pass_attempts),
        'pass_conversions': int(pass_conversions),
        'pass_conversion_rate': round(pass_conversion_rate, 2),
        'rush_attempts': int(rush_attempts),
        'rush_conversions': int(rush_conversions),
        'rush_conversion_rate': round(rush_conversion_rate, 2),
        'avg_ydstogo': round(avg_ydstogo, 2),
        'avg_yards_gained': round(avg_yards_gained, 2),
        'short_attempts': len(short_distance),
        'short_conv_rate': round(short_conv_rate, 2),
        'medium_attempts': len(medium_distance),
        'medium_conv_rate': round(medium_conv_rate, 2),
        'long_attempts': len(long_distance),
        'long_conv_rate': round(long_conv_rate, 2)
    }
    
    return metrics

def calculate_league_third_down_avg(df, season):
    """Calculate league average for third down metrics"""
    # Get all QBs with significant playing time
    pass_attempts = df[df['pass_attempt'] == 1].groupby('passer_player_name').size()
    potential_qbs = pass_attempts[pass_attempts >= 100].index.tolist()
    
    all_conversion_rates = []
    all_epa = []
    
    for qb in potential_qbs:
        third_down = df[
            (df['down'] == 3) &
            (
                (df['passer_player_name'] == qb) |
                (df['rusher_player_name'] == qb)
            )
        ]
        
        if len(third_down) > 0:
            conversions = third_down['third_down_converted'].sum()
            failures = third_down['third_down_failed'].sum()
            total = conversions + failures
            if total > 0:
                all_conversion_rates.append((conversions / total) * 100)
            all_epa.append(third_down['epa'].mean())
    
    return {
        'league_avg_conversion': round(np.mean(all_conversion_rates), 2) if all_conversion_rates else 0,
        'league_avg_epa': round(np.mean(all_epa), 4) if all_epa else 0
    }

def print_metrics(metrics, league_avg=None):
    """Print formatted metrics"""
    if metrics is None:
        return
    
    print(f"\n{'='*60}")
    print(f"{metrics['season']} SEASON - CALEB WILLIAMS 3RD DOWN ANALYSIS")
    print(f"{'='*60}")
    print(f"\nOVERALL PERFORMANCE:")
    print(f"  Total 3rd Down Attempts: {metrics['total_attempts']}")
    print(f"  Conversions: {metrics['conversions']}")
    print(f"  Failures: {metrics['failures']}")
    print(f"  Conversion Rate: {metrics['conversion_rate']}%", end="")
    if league_avg:
        print(f" (League Avg: {league_avg['league_avg_conversion']}%)")
    else:
        print()
    print(f"  EPA on Third Down: {metrics['avg_epa']}", end="")
    if league_avg:
        print(f" (League Avg: {league_avg['league_avg_epa']})")
    else:
        print()
    print(f"  Average Yards to Go: {metrics['avg_ydstogo']}")
    print(f"  Average Yards Gained: {metrics['avg_yards_gained']}")
    
    print(f"\nTENDENCY (Pass Attempts):")
    print(f"  Check Down Rate (<5 air yards): {metrics['check_down_rate']}%")
    print(f"  Attack Rate (>=5 air yards): {metrics['attack_rate']}%")
    
    print(f"\nBY PLAY TYPE:")
    print(f"  Passing:")
    print(f"    Attempts: {metrics['pass_attempts']}")
    print(f"    Conversions: {metrics['pass_conversions']}")
    print(f"    Conversion Rate: {metrics['pass_conversion_rate']}%")
    print(f"  Rushing:")
    print(f"    Attempts: {metrics['rush_attempts']}")
    print(f"    Conversions: {metrics['rush_conversions']}")
    print(f"    Conversion Rate: {metrics['rush_conversion_rate']}%")
    
    print(f"\nBY DISTANCE:")
    print(f"  Short (1-3 yards):")
    print(f"    Attempts: {metrics['short_attempts']}")
    print(f"    Conversion Rate: {metrics['short_conv_rate']}%")
    print(f"  Medium (4-7 yards):")
    print(f"    Attempts: {metrics['medium_attempts']}")
    print(f"    Conversion Rate: {metrics['medium_conv_rate']}%")
    print(f"  Long (8+ yards):")
    print(f"    Attempts: {metrics['long_attempts']}")
    print(f"    Conversion Rate: {metrics['long_conv_rate']}%")

def calculate_all_qb_third_down_rates(df, season, min_plays=500):
    """Calculate 3rd down conversion rates for all QBs with minimum play count"""
    
    print(f"\n{'='*60}")
    print(f"ANALYZING ALL QUARTERBACKS - {season} SEASON")
    print(f"{'='*60}")
    
    # Count pass attempts per player (to identify actual QBs)
    pass_attempts = df[df['pass_attempt'] == 1].groupby('passer_player_name').size()
    
    # Only consider players with at least 100 pass attempts as potential QBs
    # This filters out RBs, WRs who throw trick plays
    potential_qbs = pass_attempts[pass_attempts >= 100].index.tolist()
    
    print(f"Found {len(potential_qbs)} potential quarterbacks with 100+ pass attempts")
    
    # Now count total plays (pass + rush) for these QBs only
    qb_total_plays = {}
    for qb in potential_qbs:
        pass_count = len(df[
            ((df['passer_player_name'] == qb) & (df['pass_attempt'] == 1)) |
            ((df['passer_player_name'] == qb) & (df['sack'] == 1))
        ])
        rush_count = len(df[
            (df['rusher_player_name'] == qb) & (df['rush_attempt'] == 1)
        ])
        qb_total_plays[qb] = pass_count + rush_count
    
    # Filter QBs with 500+ total plays
    qualifying_qbs = {qb: count for qb, count in qb_total_plays.items() if count >= min_plays}
    print(f"Found {len(qualifying_qbs)} quarterbacks with {min_plays}+ plays")
    
    # Calculate 3rd down stats for each qualifying QB
    qb_third_down_stats = []
    
    for qb_name in qualifying_qbs.keys():
        third_down_plays = df[
            (df['down'] == 3) &
            (
                (df['passer_player_name'] == qb_name) |
                (df['rusher_player_name'] == qb_name)
            )
        ].copy()
        
        if len(third_down_plays) > 0:
            conversions = third_down_plays['third_down_converted'].sum()
            failures = third_down_plays['third_down_failed'].sum()
            total_attempts = conversions + failures
            
            if total_attempts > 0:
                conversion_rate = (conversions / total_attempts) * 100
                
                qb_third_down_stats.append({
                    'qb_name': qb_name,
                    'total_plays': qualifying_qbs[qb_name],
                    'third_down_attempts': int(total_attempts),
                    'third_down_conversions': int(conversions),
                    'third_down_conversion_rate': round(conversion_rate, 2)
                })
    
    # Sort by conversion rate
    qb_third_down_stats.sort(key=lambda x: x['third_down_conversion_rate'], reverse=True)
    
    # Create DataFrame for easier handling
    rankings_df = pd.DataFrame(qb_third_down_stats)
    rankings_df['rank'] = range(1, len(rankings_df) + 1)
    
    return rankings_df

def print_qb_rankings(rankings_df, season, caleb_williams_name='C.Williams'):
    """Print QB rankings and highlight Caleb Williams' position"""
    
    print(f"\n{'='*60}")
    print(f"QB 3RD DOWN CONVERSION RANKINGS - {season} SEASON")
    print(f"(Minimum 500 total plays)")
    print(f"{'='*60}\n")
    
    # Find Caleb Williams' rank
    caleb_row = rankings_df[rankings_df['qb_name'] == caleb_williams_name]
    
    if len(caleb_row) > 0:
        caleb_rank = int(caleb_row.iloc[0]['rank'])
        caleb_rate = caleb_row.iloc[0]['third_down_conversion_rate']
        caleb_attempts = int(caleb_row.iloc[0]['third_down_attempts'])
        total_qbs = len(rankings_df)
        
        print(f"{'CALEB WILLIAMS RANKING':^60}")
        print(f"{'-'*60}")
        print(f"Rank: {caleb_rank} out of {total_qbs} qualifying QBs")
        print(f"Conversion Rate: {caleb_rate}%")
        print(f"3rd Down Attempts: {caleb_attempts}")
        print(f"Percentile: {round((total_qbs - caleb_rank) / total_qbs * 100, 1)}th percentile")
        print(f"{'-'*60}\n")
        
        # Show top 10
        print("TOP 10 QUARTERBACKS:")
        print(f"{'Rank':<6} {'QB Name':<25} {'Conv %':<10} {'Attempts':<12} {'Total Plays':<12}")
        print(f"{'-'*65}")
        
        for idx, row in rankings_df.head(10).iterrows():
            marker = " ← CALEB WILLIAMS" if row['qb_name'] == caleb_williams_name else ""
            print(f"{int(row['rank']):<6} {row['qb_name']:<25} {row['third_down_conversion_rate']:<10.2f} "
                  f"{int(row['third_down_attempts']):<12} {int(row['total_plays']):<12}{marker}")
        
        # If Caleb is not in top 10, show context around his ranking
        if caleb_rank > 10:
            print(f"\n{'...':<6} {'...':<25} {'...':<10} {'...':<12} {'...':<12}")
            
            start_idx = max(0, caleb_rank - 3)
            end_idx = min(len(rankings_df), caleb_rank + 2)
            
            for idx, row in rankings_df.iloc[start_idx:end_idx].iterrows():
                marker = " ← CALEB WILLIAMS" if row['qb_name'] == caleb_williams_name else ""
                print(f"{int(row['rank']):<6} {row['qb_name']:<25} {row['third_down_conversion_rate']:<10.2f} "
                      f"{int(row['third_down_attempts']):<12} {int(row['total_plays']):<12}{marker}")
        
        # Show bottom 5
        print(f"\nBOTTOM 5 QUARTERBACKS:")
        print(f"{'Rank':<6} {'QB Name':<25} {'Conv %':<10} {'Attempts':<12} {'Total Plays':<12}")
        print(f"{'-'*65}")
        for idx, row in rankings_df.tail(5).iterrows():
            marker = " ← CALEB WILLIAMS" if row['qb_name'] == caleb_williams_name else ""
            print(f"{int(row['rank']):<6} {row['qb_name']:<25} {row['third_down_conversion_rate']:<10.2f} "
                  f"{int(row['third_down_attempts']):<12} {int(row['total_plays']):<12}{marker}")
    else:
        print(f"Caleb Williams not found in rankings (may not meet minimum play requirement)")
    
    return caleb_row

def compare_seasons(metrics_2024, metrics_2025):
    """Compare metrics between seasons"""
    if metrics_2024 is None or metrics_2025 is None:
        return
    
    print(f"\n{'='*60}")
    print(f"SEASON COMPARISON (2024 vs 2025)")
    print(f"{'='*60}")
    
    conv_rate_change = metrics_2025['conversion_rate'] - metrics_2024['conversion_rate']
    pass_rate_change = metrics_2025['pass_conversion_rate'] - metrics_2024['pass_conversion_rate']
    rush_rate_change = metrics_2025['rush_conversion_rate'] - metrics_2024['rush_conversion_rate']
    
    print(f"\nOverall Conversion Rate:")
    print(f"  2024: {metrics_2024['conversion_rate']}%")
    print(f"  2025: {metrics_2025['conversion_rate']}%")
    print(f"  Change: {'+' if conv_rate_change > 0 else ''}{round(conv_rate_change, 2)}%")
    
    print(f"\nPass Conversion Rate:")
    print(f"  2024: {metrics_2024['pass_conversion_rate']}%")
    print(f"  2025: {metrics_2025['pass_conversion_rate']}%")
    print(f"  Change: {'+' if pass_rate_change > 0 else ''}{round(pass_rate_change, 2)}%")
    
    print(f"\nRush Conversion Rate:")
    print(f"  2024: {metrics_2024['rush_conversion_rate']}%")
    print(f"  2025: {metrics_2025['rush_conversion_rate']}%")
    print(f"  Change: {'+' if rush_rate_change > 0 else ''}{round(rush_rate_change, 2)}%")
    
    print(f"\nTotal Attempts:")
    print(f"  2024: {metrics_2024['total_attempts']}")
    print(f"  2025: {metrics_2025['total_attempts']}")
    print(f"  Change: {'+' if (metrics_2025['total_attempts'] - metrics_2024['total_attempts']) > 0 else ''}{metrics_2025['total_attempts'] - metrics_2024['total_attempts']}")

def main():
    """Main analysis function"""
    print("CALEB WILLIAMS 3RD DOWN CONVERSION ANALYSIS")
    print("="*60)
    
    # Load data for both seasons
    df_2024 = load_season_data(2024)
    df_2025 = load_season_data(2025)
    
    # Analyze 2024 season
    if df_2024 is not None:
        plays_2024 = filter_caleb_williams_third_downs(df_2024, 2024)
        metrics_2024 = calculate_third_down_metrics(plays_2024, 2024)
        league_avg_2024 = calculate_league_third_down_avg(df_2024, 2024)
        print_metrics(metrics_2024, league_avg_2024)
    else:
        metrics_2024 = None
        league_avg_2024 = None
    
    # Analyze 2025 season
    if df_2025 is not None:
        plays_2025 = filter_caleb_williams_third_downs(df_2025, 2025)
        metrics_2025 = calculate_third_down_metrics(plays_2025, 2025)
        league_avg_2025 = calculate_league_third_down_avg(df_2025, 2025)
        print_metrics(metrics_2025, league_avg_2025)
    else:
        metrics_2025 = None
        league_avg_2025 = None
    
    # Compare seasons
    if metrics_2024 and metrics_2025:
        compare_seasons(metrics_2024, metrics_2025)
    
    # Calculate and display QB rankings for 2024
    rankings_2024 = None
    if df_2024 is not None:
        rankings_2024 = calculate_all_qb_third_down_rates(df_2024, 2024, min_plays=500)
        print_qb_rankings(rankings_2024, 2024)
    
    # Calculate and display QB rankings for 2025
    rankings_2025 = None
    if df_2025 is not None:
        rankings_2025 = calculate_all_qb_third_down_rates(df_2025, 2025, min_plays=500)
        print_qb_rankings(rankings_2025, 2025)
    
    # Export to CSV
    if metrics_2024 or metrics_2025:
        results = []
        if metrics_2024:
            results.append(metrics_2024)
        if metrics_2025:
            results.append(metrics_2025)
        
        results_df = pd.DataFrame(results)
        output_path = '../output/caleb_williams_third_down_analysis.csv'
        results_df.to_csv(output_path, index=False)
        print(f"\n\nCaleb Williams results exported to: {output_path}")
    
    # Export rankings
    if rankings_2024 is not None:
        rankings_2024.to_csv('../output/qb_third_down_rankings_2024.csv', index=False)
        print(f"2024 QB rankings exported to: ../output/qb_third_down_rankings_2024.csv")
    
    if rankings_2025 is not None:
        rankings_2025.to_csv('../output/qb_third_down_rankings_2025.csv', index=False)
        print(f"2025 QB rankings exported to: ../output/qb_third_down_rankings_2025.csv")

if __name__ == "__main__":
    main()
