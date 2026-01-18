# harbaugh's record in 1-score games 2008-2017
# comparing different roster quality periods

import pandas as pd
import glob
import os

# ravens team code
RAVENS = 'BAL'

# get all csv files
data_dir = '../data'
csv_files = sorted(glob.glob(os.path.join(data_dir, 'play_by_play_*.csv')))

# load everything
all_data = []
for file in csv_files:
    print(f"Loading {file}...")
    df = pd.read_csv(file)
    all_data.append(df)

# combine all years
df = pd.concat(all_data, ignore_index=True)

# filter to available years (2016-2024)
# note: data only goes back to 2016
# using 2016-2017 as "mediocre talent" period
# using 2019-2020 as "elite roster" period (lamar mvp years)
df = df[df['season'].between(2016, 2024)]

# get final scores for each game
games = df.groupby('game_id').agg({
    'home_team': 'first',
    'away_team': 'first',
    'total_home_score': 'max',
    'total_away_score': 'max',
    'season': 'first'
}).reset_index()

# calculate score difference (absolute value)
games['score_diff'] = abs(games['total_home_score'] - games['total_away_score'])

# one score games are decided by 8 points or less
one_score_games = games[games['score_diff'] <= 8].copy()

# find ravens games
ravens_games = one_score_games[
    (one_score_games['home_team'] == RAVENS) | 
    (one_score_games['away_team'] == RAVENS)
].copy()

# figure out if ravens won or lost
def get_ravens_result(row):
    if row['home_team'] == RAVENS:
        return 'W' if row['total_home_score'] > row['total_away_score'] else 'L'
    else:  # ravens are away
        return 'W' if row['total_away_score'] > row['total_home_score'] else 'L'

ravens_games['result'] = ravens_games.apply(get_ravens_result, axis=1)

# overall 2016-2017 (closest to requested 2008-2017 period)
overall = ravens_games[ravens_games['season'].between(2016, 2017)].copy()
overall_wins = (overall['result'] == 'W').sum()
overall_losses = (overall['result'] == 'L').sum()
overall_total = len(overall)
overall_win_pct = (overall_wins / overall_total * 100) if overall_total > 0 else 0

# elite roster period - using 2019-2020 (lamar mvp years) as proxy for elite roster
elite = ravens_games[ravens_games['season'].between(2019, 2020)].copy()
elite_wins = (elite['result'] == 'W').sum()
elite_losses = (elite['result'] == 'L').sum()
elite_total = len(elite)
elite_win_pct = (elite_wins / elite_total * 100) if elite_total > 0 else 0

# mediocre talent period (2016-2017 - available data)
mediocre = ravens_games[ravens_games['season'].between(2016, 2017)].copy()
mediocre_wins = (mediocre['result'] == 'W').sum()
mediocre_losses = (mediocre['result'] == 'L').sum()
mediocre_total = len(mediocre)
mediocre_win_pct = (mediocre_wins / mediocre_total * 100) if mediocre_total > 0 else 0

# actually, let me check if we can get data from later years to compare
# maybe compare 2016-2017 to a better period like 2019-2020 or something
# but for now, let's see what we have for 2016-2017

print("\n" + "="*60)
print("HARBAUGH 1-SCORE GAME RECORD")
print("="*60)
print(f"\nNOTE: Data only available from 2016-2024")
print(f"Using 2016-2017 as 'overall' period (closest to requested 2008-2017)")
print(f"Using 2019-2020 as 'elite roster' period (Lamar MVP years)")

print(f"\nOVERALL (2016-2017):")
print(f"  Record: {int(overall_wins)}-{int(overall_losses)}")
print(f"  Win percentage: {overall_win_pct:.2f}%")
print(f"  Total games: {overall_total}")

print(f"\nELITE ROSTER PERIOD (2019-2020 - Lamar MVP years):")
print(f"  Record: {int(elite_wins)}-{int(elite_losses)}")
print(f"  Win percentage: {elite_win_pct:.2f}%")
print(f"  Total games: {elite_total}")

print(f"\nMEDIOCRE TALENT PERIOD (2016-2017):")
print(f"  Record: {int(mediocre_wins)}-{int(mediocre_losses)}")
print(f"  Win percentage: {mediocre_win_pct:.2f}%")
print(f"  Total games: {mediocre_total}")

print("\n" + "-"*60)
print("KEY STATISTICS FOR BLOG:")
print("-"*60)
print(f"\nOverall record (2016-2017): {int(overall_wins)}-{int(overall_losses)} ({overall_win_pct:.1f}%)")
print(f"Elite roster win rate (2019-2020): {elite_win_pct:.1f}%")
print(f"Mediocre talent win rate (2016-2017): {mediocre_win_pct:.1f}%")
print("\nNOTE: Original request was for 2008-2017, but data only available from 2016")
print("\n" + "="*60)
