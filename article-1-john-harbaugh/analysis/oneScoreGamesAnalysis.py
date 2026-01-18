"""
checks how ravens do in close games
"""

import pandas as pd
from pathlib import Path

def analyze_one_score_games(year):
    """gets close game stats for one year"""
    
    file_path = Path(__file__).parent.parent / "csvFiles" / f"pbpRavens{year}.csv"
    
    print(f"\n{'='*80}")
    print(f"Analyzing {year} One-Score Games")
    print(f"{'='*80}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, low_memory=False)
        
        # Filter for regular season only
        df_reg = df[df['season_type'] == 'REG'].copy()
        
        # Get unique games and their results
        # We'll use the last play of each game to determine the outcome
        games = df_reg.groupby('game_id').agg({
            'away_team': 'first',
            'home_team': 'first',
            'away_score': 'last',
            'home_score': 'last',
            'posteam': 'first',  # To determine if Ravens are home or away
        }).reset_index()
        
        # Determine if Ravens were home or away, and the final scores
        games['ravens_home'] = games['home_team'] == 'BAL'
        games['ravens_score'] = games.apply(
            lambda x: x['home_score'] if x['ravens_home'] else x['away_score'], axis=1
        )
        games['opponent_score'] = games.apply(
            lambda x: x['away_score'] if x['ravens_home'] else x['home_score'], axis=1
        )
        
        # Calculate margin and outcome
        games['margin'] = games['ravens_score'] - games['opponent_score']
        games['ravens_win'] = games['margin'] > 0
        games['one_score_game'] = games['margin'].abs() <= 8
        
        # Calculate statistics
        total_games = len(games)
        one_score_games = games[games['one_score_game']]
        num_one_score = len(one_score_games)
        
        if num_one_score > 0:
            one_score_wins = len(one_score_games[one_score_games['ravens_win']])
            one_score_win_pct = (one_score_wins / num_one_score) * 100
        else:
            one_score_wins = 0
            one_score_win_pct = 0.0
        
        total_wins = len(games[games['ravens_win']])
        
        print(f"\nTotal games: {total_games}")
        print(f"Total wins: {total_wins} ({total_wins}/{total_games})")
        print(f"One-score games: {num_one_score}")
        print(f"One-score wins: {one_score_wins}")
        print(f"One-score win percentage: {one_score_win_pct:.1f}%")
        
        # Show breakdown of one-score games
        if num_one_score > 0:
            print(f"\nOne-score game results:")
            for _, game in one_score_games.iterrows():
                result = "W" if game['ravens_win'] else "L"
                margin = int(game['margin'])
                opponent = game['away_team'] if game['ravens_home'] else game['home_team']
                print(f"  {result} by {abs(margin)} vs {opponent} "
                      f"({int(game['ravens_score'])}-{int(game['opponent_score'])})")
        
        return {
            'year': year,
            'total_games': total_games,
            'total_wins': total_wins,
            'one_score_games': num_one_score,
            'one_score_wins': one_score_wins,
            'one_score_win_pct': one_score_win_pct
        }
        
    except FileNotFoundError:
        print(f"File not found for {year}")
        return None


def main():
    """Analyze one-score game performance for 2008-2017."""
    
    years = list(range(2008, 2018))  # 2008-2017
    results = []
    
    for year in years:
        result = analyze_one_score_games(year)
        if result:
            results.append(result)
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY: Ravens One-Score Game Performance (2008-2017)")
    print(f"{'='*80}\n")
    
    print(f"{'Year':<6} {'Record':<12} {'Win %':<10} {'Overall Record':<15}")
    print("-" * 80)
    
    for result in results:
        one_score_record = f"{result['one_score_wins']}-{result['one_score_games'] - result['one_score_wins']}"
        overall_record = f"{result['total_wins']}-{result['total_games'] - result['total_wins']}"
        print(f"{result['year']:<6} {one_score_record:<12} {result['one_score_win_pct']:<10.1f} {overall_record:<15}")
    
    # Calculate era-specific statistics
    print(f"\n{'='*80}")
    print("ERA ANALYSIS:")
    print(f"{'='*80}")
    
    # Early years (2008-2012)
    early_years = [r for r in results if 2008 <= r['year'] <= 2012]
    early_one_score_wins = sum(r['one_score_wins'] for r in early_years)
    early_one_score_games = sum(r['one_score_games'] for r in early_years)
    early_win_pct = (early_one_score_wins / early_one_score_games * 100) if early_one_score_games > 0 else 0
    
    print(f"\nEarly Era (2008-2012 - Strong Rosters):")
    print(f"  One-score record: {early_one_score_wins}-{early_one_score_games - early_one_score_wins}")
    print(f"  Win percentage: {early_win_pct:.1f}%")
    
    # Post-Super Bowl decline (2013-2015)
    decline_years = [r for r in results if 2013 <= r['year'] <= 2015]
    decline_one_score_wins = sum(r['one_score_wins'] for r in decline_years)
    decline_one_score_games = sum(r['one_score_games'] for r in decline_years)
    decline_win_pct = (decline_one_score_wins / decline_one_score_games * 100) if decline_one_score_games > 0 else 0
    
    print(f"\nDecline Era (2013-2015 - Aging Roster):")
    print(f"  One-score record: {decline_one_score_wins}-{decline_one_score_games - decline_one_score_wins}")
    print(f"  Win percentage: {decline_win_pct:.1f}%")
    
    # Rebuild years (2016-2017)
    rebuild_years = [r for r in results if 2016 <= r['year'] <= 2017]
    rebuild_one_score_wins = sum(r['one_score_wins'] for r in rebuild_years)
    rebuild_one_score_games = sum(r['one_score_games'] for r in rebuild_years)
    rebuild_win_pct = (rebuild_one_score_wins / rebuild_one_score_games * 100) if rebuild_one_score_games > 0 else 0
    
    print(f"\nRebuild Era (2016-2017 - Inferior Talent):")
    print(f"  One-score record: {rebuild_one_score_wins}-{rebuild_one_score_games - rebuild_one_score_wins}")
    print(f"  Win percentage: {rebuild_win_pct:.1f}%")
    
    # Overall Harbaugh era
    total_one_score_wins = sum(r['one_score_wins'] for r in results)
    total_one_score_games = sum(r['one_score_games'] for r in results)
    overall_win_pct = (total_one_score_wins / total_one_score_games * 100) if total_one_score_games > 0 else 0
    
    print(f"\nOverall (2008-2017):")
    print(f"  One-score record: {total_one_score_wins}-{total_one_score_games - total_one_score_wins}")
    print(f"  Win percentage: {overall_win_pct:.1f}%")
    
    # Analysis
    print(f"\n{'='*80}")
    print("KEY INSIGHTS:")
    print(f"{'='*80}")
    
    print(f"\n1. Harbaugh's overall one-score win rate: {overall_win_pct:.1f}%")
    print(f"   {'Above' if overall_win_pct > 50 else 'Below'} the .500 expectation for 'coin flip' games")
    
    print(f"\n2. Rebuild years (2016-2017) performance: {rebuild_win_pct:.1f}%")
    if rebuild_win_pct > 50:
        print(f"   MAINTAINED his edge in close games despite talent deficit")
    else:
        print(f"   Talent deficit caught up - fell below .500 in one-score games")
    
    comparison_early = rebuild_win_pct - early_win_pct
    print(f"\n3. Rebuild vs Early Era: {comparison_early:+.1f} percentage points")
    if abs(comparison_early) < 10:
        print(f"   Remarkably consistent coaching impact across talent levels")
    elif comparison_early < -10:
        print(f"   Significant decline shows limits of coaching without talent")
    
    # Blog format output
    print(f"\n{'='*80}")
    print("BLOG FORMAT:")
    print(f"{'='*80}\n")
    
    print("Win Percentage in One-Score Games:")
    for result in results:
        print(f"{result['year']}: {result['one_score_win_pct']:.1f}%")
    
    print(f"\n{'='*80}")
    print("NARRATIVE ANALYSIS:")
    print(f"{'='*80}")
    
    if rebuild_win_pct > 50:
        print(f"\nDuring the rebuild years (2016-2017), Harbaugh posted a {rebuild_win_pct:.1f}% ")
        print(f"win rate in one-score games, maintaining his ability to win close games even ")
        print(f"with inferior talent. This {rebuild_one_score_wins}-{rebuild_one_score_games - rebuild_one_score_wins} record in nail-biters validates his ")
        print(f"coaching acumen - he continued to tilt the odds in Baltimore's favor when ")
        print(f"games came down to execution and game management.")
    else:
        print(f"\nDuring the rebuild years (2016-2017), Harbaugh's one-score win rate dropped ")
        print(f"to {rebuild_win_pct:.1f}%, falling below .500 for the first time in his tenure. ")
        print(f"This {rebuild_one_score_wins}-{rebuild_one_score_games - rebuild_one_score_wins} record shows that while coaching matters, there are ")
        print(f"limits to what scheme and preparation can overcome when the talent deficit is ")
        print(f"too significant.")
    
    print(f"\nFor context, Harbaugh's career one-score win rate of {overall_win_pct:.1f}% ")
    print(f"({total_one_score_wins}-{total_one_score_games - total_one_score_wins}) significantly exceeds the .500 expectation, ")
    print(f"demonstrating his consistent ability to maximize every possession and make ")
    print(f"crucial adjustments in tight games.")


if __name__ == "__main__":
    main()
