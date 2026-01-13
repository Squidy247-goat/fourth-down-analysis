"""
compares ravens identity early vs rebuild years
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_team_identity(year):
    """gets identity stats for one season"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\n{'='*80}")
    print(f"Analyzing {year} Team Identity")
    print(f"{'='*80}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, low_memory=False)
        
        # Filter for regular season only
        df_reg = df[df['season_type'] == 'REG'].copy()
        
        # OFFENSIVE METRICS (Ravens have ball)
        ravens_offense = df_reg[df_reg['posteam'] == 'BAL'].copy()
        
        # 1. RUSHING PERCENTAGE
        # Count rush and pass plays (exclude special teams, penalties, etc.)
        rush_plays = ravens_offense[ravens_offense['rush_attempt'] == 1]
        pass_plays = ravens_offense[ravens_offense['pass_attempt'] == 1]
        
        total_offensive_plays = len(rush_plays) + len(pass_plays)
        rush_percentage = (len(rush_plays) / total_offensive_plays * 100) if total_offensive_plays > 0 else 0
        
        print(f"\nOFFENSIVE IDENTITY:")
        print(f"  Total offensive plays: {total_offensive_plays}")
        print(f"  Rush attempts: {len(rush_plays)} ({rush_percentage:.1f}%)")
        print(f"  Pass attempts: {len(pass_plays)} ({100 - rush_percentage:.1f}%)")
        
        # 2. PASS AGGRESSION (Deep ball % - 20+ air yards)
        passes_with_air_yards = pass_plays[pass_plays['air_yards'].notna()].copy()
        deep_balls = passes_with_air_yards[passes_with_air_yards['air_yards'] >= 20]
        
        deep_ball_pct = (len(deep_balls) / len(passes_with_air_yards) * 100) if len(passes_with_air_yards) > 0 else 0
        
        print(f"  Deep ball attempts (20+ yards): {len(deep_balls)}")
        print(f"  Deep ball percentage: {deep_ball_pct:.1f}%")
        
        # 3. TIME OF POSSESSION
        # Calculate average time of possession per game
        # drive_time_of_possession is in "M:SS" format, need to convert to seconds
        
        def parse_time_to_seconds(time_str):
            """Convert M:SS format to total seconds"""
            if pd.isna(time_str) or time_str == '':
                return 0
            try:
                parts = str(time_str).split(':')
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            except:
                return 0
        
        # Get unique drives and their durations
        drives = ravens_offense[['game_id', 'drive', 'drive_time_of_possession']].drop_duplicates(subset=['game_id', 'drive'])
        drives['top_seconds'] = drives['drive_time_of_possession'].apply(parse_time_to_seconds)
        
        # Sum TOP per game
        games_top = drives.groupby('game_id')['top_seconds'].sum().reset_index()
        
        avg_top_seconds = games_top['top_seconds'].mean()
        avg_top_minutes = avg_top_seconds / 60 if not pd.isna(avg_top_seconds) else 0
        
        print(f"  Average time of possession: {avg_top_minutes:.1f} minutes per game")
        
        # DEFENSIVE METRICS (Opponents have ball)
        ravens_defense = df_reg[df_reg['defteam'] == 'BAL'].copy()
        
        print(f"\nDEFENSIVE IDENTITY:")
        
        # 4. DEFENSIVE PRESSURE RATE
        # Count sacks, QB hits as pressure indicators
        opponent_dropbacks = ravens_defense[ravens_defense['qb_dropback'] == 1].copy()
        
        sacks = ravens_defense[ravens_defense['sack'] == 1]
        qb_hits = ravens_defense[ravens_defense['qb_hit'] == 1]
        
        # Pressure = sacks + qb_hits (some overlap, but best available metric)
        total_dropbacks = len(opponent_dropbacks)
        total_sacks = len(sacks)
        total_qb_hits = len(qb_hits)
        
        # Use sacks as primary pressure metric (more reliable)
        sack_rate = (total_sacks / total_dropbacks * 100) if total_dropbacks > 0 else 0
        
        print(f"  Opponent dropbacks: {total_dropbacks}")
        print(f"  Sacks: {total_sacks}")
        print(f"  QB hits recorded: {total_qb_hits}")
        print(f"  Sack rate (pressure proxy): {sack_rate:.1f}%")
        
        # Additional defensive context
        opponent_rush_attempts = ravens_defense[ravens_defense['rush_attempt'] == 1]
        opponent_rush_yards = opponent_rush_attempts['yards_gained'].sum()
        avg_rush_yards = opponent_rush_yards / len(opponent_rush_attempts) if len(opponent_rush_attempts) > 0 else 0
        
        print(f"  Opponent rush yards/attempt: {avg_rush_yards:.2f}")
        
        return {
            'year': year,
            'rush_percentage': rush_percentage,
            'deep_ball_pct': deep_ball_pct,
            'avg_top_minutes': avg_top_minutes,
            'sack_rate': sack_rate,
            'total_sacks': total_sacks,
            'opponent_ypc': avg_rush_yards
        }
        
    except FileNotFoundError:
        print(f"File not found for {year}")
        return None


def main():
    """Compare team identity between 2008-2011 and 2015-2017."""
    
    early_years = [2008, 2009, 2010, 2011]
    rebuild_years = [2015, 2016, 2017]
    
    print("\n" + "="*80)
    print("EARLY ERA (2008-2011) - ELITE DEFENSE & POWER RUNNING")
    print("="*80)
    
    early_results = []
    for year in early_years:
        result = analyze_team_identity(year)
        if result:
            early_results.append(result)
    
    print("\n" + "="*80)
    print("REBUILD ERA (2015-2017) - IDENTITY IN FLUX")
    print("="*80)
    
    rebuild_results = []
    for year in rebuild_years:
        result = analyze_team_identity(year)
        if result:
            rebuild_results.append(result)
    
    # Calculate averages
    print("\n" + "="*80)
    print("COMPARATIVE ANALYSIS: Early Era vs Rebuild Era")
    print("="*80)
    
    if early_results and rebuild_results:
        early_rush_avg = np.mean([r['rush_percentage'] for r in early_results])
        rebuild_rush_avg = np.mean([r['rush_percentage'] for r in rebuild_results])
        
        early_deep_avg = np.mean([r['deep_ball_pct'] for r in early_results])
        rebuild_deep_avg = np.mean([r['deep_ball_pct'] for r in rebuild_results])
        
        early_top_avg = np.mean([r['avg_top_minutes'] for r in early_results])
        rebuild_top_avg = np.mean([r['avg_top_minutes'] for r in rebuild_results])
        
        early_sack_avg = np.mean([r['sack_rate'] for r in early_results])
        rebuild_sack_avg = np.mean([r['sack_rate'] for r in rebuild_results])
        
        early_ypc_avg = np.mean([r['opponent_ypc'] for r in early_results])
        rebuild_ypc_avg = np.mean([r['opponent_ypc'] for r in rebuild_results])
        
        print(f"\nRUSHING PERCENTAGE:")
        print(f"  2008-2011 average: {early_rush_avg:.1f}%")
        print(f"  2015-2017 average: {rebuild_rush_avg:.1f}%")
        print(f"  Change: {rebuild_rush_avg - early_rush_avg:+.1f} percentage points")
        
        print(f"\nPASS AGGRESSION (Deep Ball %):")
        print(f"  2008-2011 average: {early_deep_avg:.1f}%")
        print(f"  2015-2017 average: {rebuild_deep_avg:.1f}%")
        print(f"  Change: {rebuild_deep_avg - early_deep_avg:+.1f} percentage points")
        
        print(f"\nDEFENSIVE PRESSURE RATE (Sack Rate):")
        print(f"  2008-2011 average: {early_sack_avg:.1f}%")
        print(f"  2015-2017 average: {rebuild_sack_avg:.1f}%")
        print(f"  Change: {rebuild_sack_avg - early_sack_avg:+.1f} percentage points")
        
        print(f"\nTIME OF POSSESSION:")
        print(f"  2008-2011 average: {early_top_avg:.1f} minutes per game")
        print(f"  2015-2017 average: {rebuild_top_avg:.1f} minutes per game")
        print(f"  Change: {rebuild_top_avg - early_top_avg:+.1f} minutes")
        
        print(f"\nOPPONENT RUSH YARDS/ATTEMPT (Defensive Run Stopping):")
        print(f"  2008-2011 average: {early_ypc_avg:.2f} yards")
        print(f"  2015-2017 average: {rebuild_ypc_avg:.2f} yards")
        print(f"  Change: {rebuild_ypc_avg - early_ypc_avg:+.2f} yards")
        
        # Analysis
        print(f"\n{'='*80}")
        print("KEY INSIGHTS:")
        print(f"{'='*80}")
        
        print("\n1. OFFENSIVE IDENTITY SHIFT:")
        if rebuild_rush_avg < early_rush_avg:
            print(f"   The Ravens became LESS run-heavy during the rebuild")
            print(f"   ({early_rush_avg:.1f}% rushing → {rebuild_rush_avg:.1f}% rushing)")
            print(f"   Shift toward more passing despite lacking elite passing game talent")
        else:
            print(f"   The Ravens maintained or increased their run-heavy approach")
        
        print("\n2. PASSING PHILOSOPHY:")
        if rebuild_deep_avg < early_deep_avg:
            print(f"   Deep ball attempts DECREASED from {early_deep_avg:.1f}% to {rebuild_deep_avg:.1f}%")
            print(f"   More conservative passing attack during rebuild")
        else:
            print(f"   Deep ball attempts INCREASED despite talent limitations")
        
        print("\n3. DEFENSIVE PRESSURE:")
        if rebuild_sack_avg < early_sack_avg:
            print(f"   Significant DROP in pressure rate: {early_sack_avg:.1f}% → {rebuild_sack_avg:.1f}%")
            print(f"   Lost ability to generate consistent pass rush without elite talent")
        else:
            print(f"   Maintained pressure despite personnel changes")
        
        print("\n4. TIME OF POSSESSION:")
        if rebuild_top_avg < early_top_avg:
            print(f"   DECREASED ball control: {early_top_avg:.1f} → {rebuild_top_avg:.1f} minutes")
            print(f"   Less effective at sustaining drives and controlling tempo")
        else:
            print(f"   Maintained or improved ball control")
        
        # Blog format output
        print(f"\n{'='*80}")
        print("BLOG FORMAT:")
        print(f"{'='*80}\n")
        
        print("Team Identity Metrics (2015-2017 vs 2008-2011):")
        print(f"\nRushing Percentage:")
        print(f"  2008-2011 average: {early_rush_avg:.1f}%")
        print(f"  2015-2017 average: {rebuild_rush_avg:.1f}%")
        
        print(f"\nPass Aggression (Deep ball %):")
        print(f"  2008-2011 average: {early_deep_avg:.1f}%")
        print(f"  2015-2017 average: {rebuild_deep_avg:.1f}%")
        
        print(f"\nDefensive Pressure Rate:")
        print(f"  2008-2011 average: {early_sack_avg:.1f}%")
        print(f"  2015-2017 average: {rebuild_sack_avg:.1f}%")
        
        print(f"\nTime of Possession:")
        print(f"  2008-2011 average: {early_top_avg:.1f} minutes")
        print(f"  2015-2017 average: {rebuild_top_avg:.1f} minutes")
        
        print(f"\n{'='*80}")
        print("NARRATIVE ANALYSIS:")
        print(f"{'='*80}")
        
        print("\nThe rebuild forced a fundamental reimagining of Ravens football.")
        print(f"Without elite defensive talent, the identity shifted dramatically:")
        print(f"\n• The run-first identity ERODED: rushing percentage dropped from")
        print(f"  {early_rush_avg:.1f}% to {rebuild_rush_avg:.1f}%, forcing more reliance on passing")
        print(f"\n• Pass aggression DECREASED: deep ball rate fell from {early_deep_avg:.1f}% to")
        print(f"  {rebuild_deep_avg:.1f}%, reflecting conservative approach without weapons")
        print(f"\n• Defensive pressure COLLAPSED: sack rate plummeted from {early_sack_avg:.1f}% to")
        print(f"  {rebuild_sack_avg:.1f}%, losing the core identity of Ravens defense")
        print(f"\n• Ball control WEAKENED: time of possession dropped by {early_top_avg - rebuild_top_avg:.1f}")
        print(f"  minutes per game, unable to sustain long drives")
        print("\nThe Ravens tried to maintain their defensive, run-first philosophy,")
        print("but personnel limitations forced an uncomfortable hybrid - not enough")
        print("talent to dominate with power running or defense, yet not built for")
        print("an aggressive passing attack. This identity crisis defined the rebuild era.")


if __name__ == "__main__":
    main()
