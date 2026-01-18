"""
cleans the csv files to only keep ravens games
"""

import pandas as pd
from pathlib import Path
from collections import Counter

def clean_ravens_games(input_file, output_file=None):
    """filters data to just ravens games"""
    
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file, low_memory=False)
    
    print(f"Original dataset shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
    
    # only keep ravens games
    ravens_mask = (df['home_team'] == 'BAL') | (df['away_team'] == 'BAL')
    ravens_df = df[ravens_mask].copy()
    
    print(f"Filtered dataset shape: {ravens_df.shape[0]:,} rows, {ravens_df.shape[1]} columns")
    print(f"Rows removed: {df.shape[0] - ravens_df.shape[0]:,}")
    
    # get some stats
    stats = {
        'original_rows': df.shape[0],
        'filtered_rows': ravens_df.shape[0],
        'rows_removed': df.shape[0] - ravens_df.shape[0],
        'total_games': len(ravens_df['game_id'].unique()) if 'game_id' in ravens_df.columns else 'N/A',
        'home_games': (ravens_df['home_team'] == 'BAL').sum() if 'home_team' in ravens_df.columns else 'N/A',
        'away_games': (ravens_df['away_team'] == 'BAL').sum() if 'away_team' in ravens_df.columns else 'N/A'
    }
    
    # count unique games
    if 'game_id' in ravens_df.columns:
        unique_games = ravens_df['game_id'].unique()
        stats['unique_games'] = len(unique_games)
        print(f"\nTotal unique Ravens games: {stats['unique_games']}")
        
        # see who they played
        opponents = []
        for game_id in unique_games:
            game_data = ravens_df[ravens_df['game_id'] == game_id].iloc[0]
            if game_data['home_team'] == 'BAL':
                opponents.append(game_data['away_team'])
            else:
                opponents.append(game_data['home_team'])
        
        opponent_counts = Counter(opponents)
        print("\nOpponents in this dataset:")
        for opp, count in sorted(opponent_counts.items()):
            print(f"  {opp}: {count} game(s)")
    
    # save over the original file
    if output_file is None:
        output_file = input_file
    
    # save it
    print(f"\nSaving cleaned data to {output_file}...")
    ravens_df.to_csv(output_file, index=False)
    print("Done!")
    
    return ravens_df, stats


def main():
    """cleans 2021-2025 csv files"""
    
    # find the csv folder
    current_dir = Path(__file__).parent
    
    # years we want to clean
    target_years = range(2021, 2026)
    
    all_stats = []
    
    for year in target_years:
        # look for file
        target_file = current_dir / f"pbpRavens{year}.csv"
        alt_file = current_dir / f"play_by_play_{year}.csv"
        
        # rename if needed
        if alt_file.exists():
            target_file_new = current_dir / f"pbpRavens{year}.csv"
            print(f"Renaming {alt_file.name} to {target_file_new.name}...")
            alt_file.rename(target_file_new)
            target_file = target_file_new
        
        if not target_file.exists():
            print(f"Warning: {target_file.name} not found, skipping...")
            print()
            continue
        
        print("=" * 80)
        print(f"Processing: {target_file.name}")
        print("=" * 80)
        
        # clean it
        cleaned_df, stats = clean_ravens_games(str(target_file))
        stats['filename'] = target_file.name
        all_stats.append(stats)
        
        print("\n")
    
    # show summary
    if all_stats:
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        for stat in all_stats:
            print(f"\n{stat['filename']}:")
            print(f"  Original rows: {stat['original_rows']:,}")
            print(f"  Filtered rows: {stat['filtered_rows']:,}")
            print(f"  Rows removed: {stat['rows_removed']:,}")
            print(f"  Unique games: {stat.get('unique_games', 'N/A')}")


if __name__ == "__main__":
    main()
