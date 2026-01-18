"""
compares offense with flacco vs with lamar
"""

import pandas as pd
from pathlib import Path

def analyze_offensive_metrics(year):
    #gets offense stats for one year
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\nReading {file_path.name}...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for regular season only
    df = df[df['season_type'] == 'REG'].copy()
    
    # Filter for Ravens offensive plays
    ravens_offense = df[df['posteam'] == 'BAL'].copy()
    
    # Get passing and rushing plays
    pass_plays = ravens_offense[ravens_offense['pass_attempt'] == 1].copy()
    rush_plays = ravens_offense[ravens_offense['rush_attempt'] == 1].copy()
    
    # Calculate passing yards
    total_pass_yards = pass_plays['passing_yards'].sum()
    
    # Calculate rushing yards
    total_rush_yards = rush_plays['rushing_yards'].sum()
    
    # Calculate total offensive yards
    total_yards = total_pass_yards + total_rush_yards
    
    # Get points scored
    games = df.groupby('game_id').last().reset_index()
    
    total_points = 0
    game_count = 0
    
    for _, game in games.iterrows():
        home_team = game['home_team']
        away_team = game['away_team']
        
        if home_team == 'BAL':
            total_points += game['home_score']
            game_count += 1
        elif away_team == 'BAL':
            total_points += game['away_score']
            game_count += 1
    
    # Calculate per-game averages
    rush_ypg = total_rush_yards / game_count if game_count > 0 else 0
    pass_ypg = total_pass_yards / game_count if game_count > 0 else 0
    total_ypg = total_yards / game_count if game_count > 0 else 0
    ppg = total_points / game_count if game_count > 0 else 0
    
    print(f"\n{year} Offensive Metrics:")
    print(f"  Games: {game_count}")
    print(f"  Total Points: {total_points}")
    print(f"  Points per game: {ppg:.1f}")
    print(f"  Total rushing yards: {total_rush_yards}")
    print(f"  Rushing yards per game: {rush_ypg:.1f}")
    print(f"  Total passing yards: {total_pass_yards}")
    print(f"  Passing yards per game: {pass_ypg:.1f}")
    print(f"  Total yards per game: {total_ypg:.1f}")
    
    return {
        'year': year,
        'games': game_count,
        'total_points': total_points,
        'ppg': ppg,
        'total_rush_yards': total_rush_yards,
        'rush_ypg': rush_ypg,
        'total_pass_yards': total_pass_yards,
        'pass_ypg': pass_ypg,
        'total_ypg': total_ypg
    }


def main():
    """Main analysis function"""
    
    print(f"{'='*80}")
    print("BEFORE/AFTER OFFENSIVE METRICS ANALYSIS")
    print("Flacco Era (2008-2017) vs Peak Lamar Era (2019-2024)")
    print(f"{'='*80}")
    
    # 1. Analyze Flacco Era (2008-2017)
    print(f"\n{'='*80}")
    print("FLACCO ERA (2008-2017)")
    print(f"{'='*80}")
    
    flacco_era_results = []
    flacco_years = list(range(2008, 2018))  # 2008-2017
    
    for year in flacco_years:
        result = analyze_offensive_metrics(year)
        flacco_era_results.append(result)
    
    # Calculate Flacco Era averages
    total_games_flacco = sum(r['games'] for r in flacco_era_results)
    total_points_flacco = sum(r['total_points'] for r in flacco_era_results)
    total_rush_yards_flacco = sum(r['total_rush_yards'] for r in flacco_era_results)
    total_pass_yards_flacco = sum(r['total_pass_yards'] for r in flacco_era_results)
    
    flacco_ppg = total_points_flacco / total_games_flacco if total_games_flacco > 0 else 0
    flacco_rush_ypg = total_rush_yards_flacco / total_games_flacco if total_games_flacco > 0 else 0
    flacco_pass_ypg = total_pass_yards_flacco / total_games_flacco if total_games_flacco > 0 else 0
    flacco_total_ypg = (total_rush_yards_flacco + total_pass_yards_flacco) / total_games_flacco if total_games_flacco > 0 else 0
    
    print(f"\n{'='*80}")
    print("FLACCO ERA AVERAGES (2008-2017):")
    print(f"{'='*80}")
    print(f"Total games: {total_games_flacco}")
    print(f"Rushing yards per game: {flacco_rush_ypg:.1f}")
    print(f"Passing yards per game: {flacco_pass_ypg:.1f}")
    print(f"Points per game: {flacco_ppg:.1f}")
    print(f"Total yards per game: {flacco_total_ypg:.1f}")
    
    # 2. Analyze Peak Lamar Era (2019-2024)
    print(f"\n{'='*80}")
    print("PEAK LAMAR ERA (2019-2024)")
    print(f"{'='*80}")
    
    lamar_era_results = []
    lamar_years = [2019, 2020, 2021, 2022, 2023, 2024]
    
    for year in lamar_years:
        result = analyze_offensive_metrics(year)
        lamar_era_results.append(result)
    
    # Calculate Lamar Era averages
    total_games_lamar = sum(r['games'] for r in lamar_era_results)
    total_points_lamar = sum(r['total_points'] for r in lamar_era_results)
    total_rush_yards_lamar = sum(r['total_rush_yards'] for r in lamar_era_results)
    total_pass_yards_lamar = sum(r['total_pass_yards'] for r in lamar_era_results)
    
    lamar_ppg = total_points_lamar / total_games_lamar if total_games_lamar > 0 else 0
    lamar_rush_ypg = total_rush_yards_lamar / total_games_lamar if total_games_lamar > 0 else 0
    lamar_pass_ypg = total_pass_yards_lamar / total_games_lamar if total_games_lamar > 0 else 0
    lamar_total_ypg = (total_rush_yards_lamar + total_pass_yards_lamar) / total_games_lamar if total_games_lamar > 0 else 0
    
    print(f"\n{'='*80}")
    print("PEAK LAMAR ERA AVERAGES (2019-2024):")
    print(f"{'='*80}")
    print(f"Total games: {total_games_lamar}")
    print(f"Rushing yards per game: {lamar_rush_ypg:.1f}")
    print(f"Passing yards per game: {lamar_pass_ypg:.1f}")
    print(f"Points per game: {lamar_ppg:.1f}")
    print(f"Total yards per game: {lamar_total_ypg:.1f}")
    
    # 3. Calculate differences
    print(f"\n{'='*80}")
    print("COMPARISON & CHANGES:")
    print(f"{'='*80}")
    
    rush_ypg_diff = lamar_rush_ypg - flacco_rush_ypg
    rush_ypg_pct = (rush_ypg_diff / flacco_rush_ypg * 100) if flacco_rush_ypg > 0 else 0
    
    pass_ypg_diff = lamar_pass_ypg - flacco_pass_ypg
    pass_ypg_pct = (pass_ypg_diff / flacco_pass_ypg * 100) if flacco_pass_ypg > 0 else 0
    
    ppg_diff = lamar_ppg - flacco_ppg
    ppg_pct = (ppg_diff / flacco_ppg * 100) if flacco_ppg > 0 else 0
    
    total_ypg_diff = lamar_total_ypg - flacco_total_ypg
    total_ypg_pct = (total_ypg_diff / flacco_total_ypg * 100) if flacco_total_ypg > 0 else 0
    
    print(f"\nRushing yards per game:")
    print(f"  Flacco Era: {flacco_rush_ypg:.1f}")
    print(f"  Lamar Era: {lamar_rush_ypg:.1f}")
    print(f"  Change: {rush_ypg_diff:+.1f} ({rush_ypg_pct:+.1f}%)")
    
    print(f"\nPassing yards per game:")
    print(f"  Flacco Era: {flacco_pass_ypg:.1f}")
    print(f"  Lamar Era: {lamar_pass_ypg:.1f}")
    print(f"  Change: {pass_ypg_diff:+.1f} ({pass_ypg_pct:+.1f}%)")
    
    print(f"\nPoints per game:")
    print(f"  Flacco Era: {flacco_ppg:.1f}")
    print(f"  Lamar Era: {lamar_ppg:.1f}")
    print(f"  Change: {ppg_diff:+.1f} ({ppg_pct:+.1f}%)")
    
    print(f"\nTotal yards per game:")
    print(f"  Flacco Era: {flacco_total_ypg:.1f}")
    print(f"  Lamar Era: {lamar_total_ypg:.1f}")
    print(f"  Change: {total_ypg_diff:+.1f} ({total_ypg_pct:+.1f}%)")
    
    # 4. Print Blog-Ready Output
    print(f"\n{'='*80}")
    print("BLOG-READY FORMAT:")
    print(f"{'='*80}\n")
    
    print("Before/After Offensive Metrics:")
    print("\n2008-2017 (Flacco Era):")
    print(f"Rushing yards/game: {flacco_rush_ypg:.1f}")
    print(f"Passing yards/game: {flacco_pass_ypg:.1f}")
    print(f"Points/game: {flacco_ppg:.1f}")
    print(f"Total yards/game: {flacco_total_ypg:.1f}")
    
    print("\n2019-2024 (Peak Lamar):")
    print(f"Rushing yards/game: {lamar_rush_ypg:.1f}")
    print(f"Passing yards/game: {lamar_pass_ypg:.1f}")
    print(f"Points/game: {lamar_ppg:.1f}")
    print(f"Total yards/game: {lamar_total_ypg:.1f}")
    
    # 5. Year-by-year breakdown for context
    print(f"\n{'='*80}")
    print("YEAR-BY-YEAR BREAKDOWN:")
    print(f"{'='*80}")
    
    print("\nFlacco Era (2008-2017):")
    print(f"{'Year':<8} {'PPG':<8} {'Rush YPG':<12} {'Pass YPG':<12} {'Total YPG':<12}")
    print("-" * 60)
    for result in flacco_era_results:
        print(f"{result['year']:<8} {result['ppg']:<8.1f} {result['rush_ypg']:<12.1f} {result['pass_ypg']:<12.1f} {result['total_ypg']:<12.1f}")
    
    print("\nLamar Era (2019-2024):")
    print(f"{'Year':<8} {'PPG':<8} {'Rush YPG':<12} {'Pass YPG':<12} {'Total YPG':<12}")
    print("-" * 60)
    for result in lamar_era_results:
        print(f"{result['year']:<8} {result['ppg']:<8.1f} {result['rush_ypg']:<12.1f} {result['pass_ypg']:<12.1f} {result['total_ypg']:<12.1f}")


if __name__ == "__main__":
    main()
