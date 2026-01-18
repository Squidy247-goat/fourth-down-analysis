# one score game record for giants 2016-2025
# games decided by 8 points or less

import pandas as pd
import glob
import os

# giants team code
GIANTS = 'NYG'

# get all csv files
data_dir = '../data'
csv_files = sorted(glob.glob(os.path.join(data_dir, 'play_by_play_*.csv')))

# load all the data
all_data = []
for file in csv_files:
    print(f"Loading {file}...")
    df = pd.read_csv(file)
    all_data.append(df)

# combine everything
df = pd.concat(all_data, ignore_index=True)

# only 2016-2025
df = df[df['season'].between(2016, 2025)]

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

# find giants games
giants_games = one_score_games[
    (one_score_games['home_team'] == GIANTS) | 
    (one_score_games['away_team'] == GIANTS)
].copy()

# figure out if giants won or lost
def get_giants_result(row):
    if row['home_team'] == GIANTS:
        return 'W' if row['total_home_score'] > row['total_away_score'] else 'L'
    else:  # giants are away team
        return 'W' if row['total_away_score'] > row['total_home_score'] else 'L'

giants_games['result'] = giants_games.apply(get_giants_result, axis=1)
giants_wins = (giants_games['result'] == 'W').sum()
giants_losses = (giants_games['result'] == 'L').sum()
giants_total = len(giants_games)
giants_win_pct = (giants_wins / giants_total * 100) if giants_total > 0 else 0

# league average (not including giants games)
league_one_score = one_score_games[
    (one_score_games['home_team'] != GIANTS) & 
    (one_score_games['away_team'] != GIANTS)
].copy()

# count wins for each team (each game has one winner)
team_wins = {}
team_games = {}

for _, game in league_one_score.iterrows():
    home_team = game['home_team']
    away_team = game['away_team']
    
    if home_team not in team_games:
        team_games[home_team] = 0
        team_wins[home_team] = 0
    if away_team not in team_games:
        team_games[away_team] = 0
        team_wins[away_team] = 0
    
    team_games[home_team] += 1
    team_games[away_team] += 1
    
    if game['total_home_score'] > game['total_away_score']:
        team_wins[home_team] += 1
    else:
        team_wins[away_team] += 1

# calculate average win percentage
total_win_rate = sum(team_wins.values()) / sum(team_games.values()) if sum(team_games.values()) > 0 else 0.5
league_win_pct = total_win_rate * 100

# calculate expected wins based on league average
expected_win_pct = league_win_pct / 100
expected_wins = giants_total * expected_win_pct
actual_wins = giants_wins
wins_lost = expected_wins - actual_wins

# calculate point differential in giants losses from 2020-2025
giants_all_games = games[
    (games['home_team'] == GIANTS) | 
    (games['away_team'] == GIANTS)
].copy()

# only 2020-2025
giants_recent_games = giants_all_games[giants_all_games['season'].between(2020, 2025)].copy()

# calculate point differential from giants perspective
def get_giants_point_diff(row):
    if row['home_team'] == GIANTS:
        return row['total_home_score'] - row['total_away_score']
    else:  # giants are away
        return row['total_away_score'] - row['total_home_score']

giants_recent_games['point_diff'] = giants_recent_games.apply(get_giants_point_diff, axis=1)
giants_recent_games['result'] = giants_recent_games.apply(get_giants_result, axis=1)

# average point differential in losses
giants_losses_recent = giants_recent_games[giants_recent_games['result'] == 'L']
avg_point_diff_losses = abs(giants_losses_recent['point_diff']).mean() if len(giants_losses_recent) > 0 else 0

# calculate what percent of all giants games were one score (2016-2025)
all_giants_games = games[
    (games['home_team'] == GIANTS) | 
    (games['away_team'] == GIANTS)
].copy()
all_giants_games['is_one_score'] = all_giants_games['score_diff'] <= 8
one_score_pct = (all_giants_games['is_one_score'].sum() / len(all_giants_games) * 100) if len(all_giants_games) > 0 else 0

print("\n" + "="*60)
print("ONE-SCORE GAME RECORD ANALYSIS (2016-2025)")
print("="*60)
print(f"\nGiants' record in one-score games: {int(giants_wins)}-{int(giants_losses)}")
print(f"Win percentage: {giants_win_pct:.2f}%")
print(f"League average: ~{league_win_pct:.1f}%")
print(f"\nTotal one-score games: {giants_total}")
print(f"\nExpected wins (based on league avg): {expected_wins:.1f}")
print(f"Actual wins: {actual_wins}")
print(f"Wins lost: {wins_lost:.1f}")
print("\n" + "-"*60)
print("ADDITIONAL STATISTICS:")
print("-"*60)
print(f"\nAverage point differential in Giants losses (2020-2025): {avg_point_diff_losses:.2f} points")
print(f"Percentage of all Giants games decided by 1 score (2016-2025): {one_score_pct:.1f}%")
print("\n" + "="*60)
