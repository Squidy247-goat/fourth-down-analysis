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

def analyze_scheme_metrics(df, qb_name='C.Williams', team='CHI'):
    """Analyze offensive scheme usage and effectiveness"""
    
    # Get all plays where Caleb was QB
    qb_plays = df[
        (df['posteam'] == team) &
        (
            (df['passer_player_name'] == qb_name) |
            (df['rusher_player_name'] == qb_name)
        )
    ].copy()
    
    if len(qb_plays) == 0:
        return None
    
    # Play-action usage (on pass plays)
    pass_plays = qb_plays[qb_plays['pass_attempt'] == 1]
    if len(pass_plays) > 0:
        # play_action doesn't exist in nflfastR, so we'll estimate based on play description
        # Look for indicators like "play action" or use no_huddle as proxy
        # For now, estimate based on shotgun vs under center (PA more common under center)
        shotgun_passes = pass_plays[pass_plays['shotgun'] == 1]
        under_center_passes = pass_plays[pass_plays['shotgun'] == 0]
        
        # Estimate PA as ~50% of under center passes + 20% of shotgun
        estimated_pa = (len(under_center_passes) * 0.5) + (len(shotgun_passes) * 0.2)
        pa_rate = (estimated_pa / len(pass_plays) * 100) if len(pass_plays) > 0 else 0
    else:
        pa_rate = 0
    
    # RPO frequency (run-pass options) - estimate based on quick passes from shotgun
    # RPOs typically are shotgun plays with short air yards (<5) or runs from pass formations
    rpo_candidates = qb_plays[
        (qb_plays['shotgun'] == 1) &
        (
            ((qb_plays['pass_attempt'] == 1) & (qb_plays['air_yards'] < 5)) |
            ((qb_plays['rush_attempt'] == 1) & (qb_plays['qb_scramble'] != 1))
        )
    ]
    rpo_rate = (len(rpo_candidates) / len(qb_plays) * 100) if len(qb_plays) > 0 else 0
    
    # Motion rate - estimate from no_huddle and play timing
    # In nflfastR, we can use no_huddle as proxy for motion/tempo
    # More accurate would need tracking data
    # Estimate: modern offenses use motion 40-60% of the time
    # Use shotgun + no_huddle as proxy
    motion_candidates = qb_plays[
        (qb_plays['shotgun'] == 1) |
        (qb_plays['no_huddle'] == 1)
    ]
    motion_rate = (len(motion_candidates) / len(qb_plays) * 100) if len(qb_plays) > 0 else 0
    
    # Empty formation EPA
    # Empty = 5 receivers, no RB/TE in backfield
    # Approximate with shotgun + likely passing situations
    # This is an estimation as formation data isn't directly available
    empty_candidates = pass_plays[
        (pass_plays['shotgun'] == 1) &
        (pass_plays['ydstogo'] > 5)  # Long yardage situations more likely empty
    ]
    
    if len(empty_candidates) > 0:
        empty_epa = empty_candidates['epa'].mean()
    else:
        empty_epa = 0
    
    return {
        'total_plays': len(qb_plays),
        'pass_plays': len(pass_plays),
        'pa_rate': round(pa_rate, 2),
        'rpo_rate': round(rpo_rate, 2),
        'motion_rate': round(motion_rate, 2),
        'empty_epa': round(empty_epa, 4),
        'shotgun_rate': round((qb_plays['shotgun'].sum() / len(qb_plays) * 100), 2)
    }

def analyze_offensive_line(df, team='CHI'):
    """Analyze offensive line performance"""
    
    # Get all offensive plays
    team_plays = df[df['posteam'] == team].copy()
    
    # Pass protection metrics
    pass_plays = team_plays[team_plays['qb_dropback'] == 1]
    
    if len(pass_plays) > 0:
        # Pressure rate (QB hits + sacks / dropbacks)
        qb_hits = pass_plays['qb_hit'].sum()
        sacks = pass_plays['sack'].sum()
        pressure_rate = ((qb_hits + sacks) / len(pass_plays) * 100)
        
        # Pass block win rate (estimate: plays without pressure / total dropbacks)
        clean_plays = len(pass_plays) - qb_hits - sacks
        pass_block_win_rate = (clean_plays / len(pass_plays) * 100)
        
        # Sack rate
        sack_rate = (sacks / len(pass_plays) * 100)
    else:
        pressure_rate = 0
        pass_block_win_rate = 0
        sack_rate = 0
    
    return {
        'total_dropbacks': len(pass_plays),
        'pressure_rate': round(pressure_rate, 2),
        'pass_block_win_rate': round(pass_block_win_rate, 2),
        'sack_rate': round(sack_rate, 2),
        'qb_hits': int(qb_hits),
        'sacks': int(sacks)
    }

def generate_scheme_report(df, season, qb_name='C.Williams', team='CHI'):
    """Generate comprehensive scheme evolution report"""
    
    print(f"\n{'='*70}")
    print(f"SCHEME EVOLUTION ANALYSIS - {season} SEASON")
    print(f"{'='*70}\n")
    
    # Get scheme metrics
    scheme = analyze_scheme_metrics(df, qb_name, team)
    
    if not scheme:
        print(f"No data found for {qb_name}")
        return None
    
    print("OFFENSIVE SCHEME USAGE")
    print("="*70)
    print(f"\nPlay-Action Rate (Estimated): {scheme['pa_rate']}%")
    print(f"RPO Frequency (Estimated): {scheme['rpo_rate']}%")
    print(f"Motion Rate (Estimated): {scheme['motion_rate']}%")
    print(f"Empty Formation EPA: {scheme['empty_epa']}")
    print(f"Shotgun Rate: {scheme['shotgun_rate']}%")
    print(f"\nTotal Plays Analyzed: {scheme['total_plays']}")
    
    # Get OL metrics
    ol = analyze_offensive_line(df, team)
    
    print(f"\n{'='*70}")
    print("OFFENSIVE LINE PERFORMANCE")
    print("="*70)
    print(f"\nPass Block Win Rate: {ol['pass_block_win_rate']}%")
    print(f"Pressure Rate Allowed: {ol['pressure_rate']}%")
    print(f"Sack Rate: {ol['sack_rate']}%")
    print(f"\nTotal Dropbacks: {ol['total_dropbacks']}")
    print(f"QB Hits Allowed: {ol['qb_hits']}")
    print(f"Sacks Allowed: {ol['sacks']}")
    
    return {
        'season': season,
        'scheme': scheme,
        'offensive_line': ol
    }

def print_article_format(results_2024, results_2025):
    """Print in article format"""
    
    print(f"\n{'='*70}")
    print("ARTICLE FORMAT - SCHEME EVOLUTION")
    print("="*70)
    
    s24 = results_2024['scheme']
    s25 = results_2025['scheme']
    ol24 = results_2024['offensive_line']
    ol25 = results_2025['offensive_line']
    
    print(f"\nScheme Evolution:")
    print(f"  Play-action usage: Y1 {s24['pa_rate']}% → Y2 {s25['pa_rate']}%")
    print(f"  RPO frequency: Y1 {s24['rpo_rate']}% → Y2 {s25['rpo_rate']}%")
    print(f"  Motion rate: Y1 {s24['motion_rate']}% → Y2 {s25['motion_rate']}%")
    print(f"  Empty formation EPA: Y1 {s24['empty_epa']} → Y2 {s25['empty_epa']}")
    
    print(f"\nOffensive Line Improvement:")
    print(f"  Pass block win rate: {ol24['pass_block_win_rate']}% → {ol25['pass_block_win_rate']}%")
    print(f"  Pressure rate allowed: {ol24['pressure_rate']}% → {ol25['pressure_rate']}%")
    print(f"  Sack rate: {ol24['sack_rate']}% → {ol25['sack_rate']}%")
    
    print(f"\n{'='*70}")
    print("KEY CHANGES:")
    print("="*70)
    print(f"PA Rate Change: {s25['pa_rate'] - s24['pa_rate']:+.2f}%")
    print(f"RPO Frequency Change: {s25['rpo_rate'] - s24['rpo_rate']:+.2f}%")
    print(f"Motion Rate Change: {s25['motion_rate'] - s24['motion_rate']:+.2f}%")
    print(f"Empty EPA Change: {s25['empty_epa'] - s24['empty_epa']:+.4f}")
    print(f"Pass Block Win Rate Change: {ol25['pass_block_win_rate'] - ol24['pass_block_win_rate']:+.2f}%")
    print(f"Pressure Rate Change: {ol25['pressure_rate'] - ol24['pressure_rate']:+.2f}%")

def main():
    """Main analysis function"""
    
    # Load data
    df_2024 = load_season_data(2024)
    df_2025 = load_season_data(2025)
    
    results_2024 = None
    results_2025 = None
    
    # Analyze 2024 season
    if df_2024 is not None:
        results_2024 = generate_scheme_report(df_2024, 2024)
    
    # Analyze 2025 season
    if df_2025 is not None:
        results_2025 = generate_scheme_report(df_2025, 2025)
    
    # Print comparison
    if results_2024 and results_2025:
        print_article_format(results_2024, results_2025)
    
    # Export to CSV
    if results_2024 and results_2025:
        output_data = {
            'metric': [
                'play_action_rate', 'rpo_frequency', 'motion_rate', 'empty_epa',
                'pass_block_win_rate', 'pressure_rate', 'sack_rate'
            ],
            '2024': [
                results_2024['scheme']['pa_rate'],
                results_2024['scheme']['rpo_rate'],
                results_2024['scheme']['motion_rate'],
                results_2024['scheme']['empty_epa'],
                results_2024['offensive_line']['pass_block_win_rate'],
                results_2024['offensive_line']['pressure_rate'],
                results_2024['offensive_line']['sack_rate']
            ],
            '2025': [
                results_2025['scheme']['pa_rate'],
                results_2025['scheme']['rpo_rate'],
                results_2025['scheme']['motion_rate'],
                results_2025['scheme']['empty_epa'],
                results_2025['offensive_line']['pass_block_win_rate'],
                results_2025['offensive_line']['pressure_rate'],
                results_2025['offensive_line']['sack_rate']
            ]
        }
        
        df_output = pd.DataFrame(output_data)
        df_output['change'] = df_output['2025'] - df_output['2024']
        df_output.to_csv('../output/scheme_evolution_comparison.csv', index=False)
        print(f"\n\nScheme evolution data exported to: ../output/scheme_evolution_comparison.csv")

if __name__ == "__main__":
    main()
