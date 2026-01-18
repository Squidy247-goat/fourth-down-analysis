# penalty discipline for harbaugh's ravens
# comparing penalties per game vs league average

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

# get ravens games
ravens_games = df[
    (df['home_team'] == RAVENS) | 
    (df['away_team'] == RAVENS)
].copy()

# count penalties for ravens
# penalty column is 1 if there was a penalty
ravens_penalties = ravens_games[ravens_games['penalty'] == 1].copy()

# figure out if penalty was on ravens or opponent
ravens_penalties_on_ravens = ravens_penalties[
    ravens_penalties['penalty_team'] == RAVENS
].copy()

# count total games
ravens_game_ids = ravens_games['game_id'].unique()
ravens_total_games = len(ravens_game_ids)

# penalties per game
ravens_penalties_per_game = len(ravens_penalties_on_ravens) / ravens_total_games if ravens_total_games > 0 else 0

# league average (excluding ravens)
league_games = df[
    (df['home_team'] != RAVENS) & 
    (df['away_team'] != RAVENS)
].copy()

league_penalties = league_games[league_games['penalty'] == 1].copy()

# count penalties per team per game
team_penalties = {}
team_games = {}

for _, play in league_penalties.iterrows():
    penalty_team = play['penalty_team']
    game_id = play['game_id']
    
    if pd.isna(penalty_team):
        continue
    
    if penalty_team not in team_penalties:
        team_penalties[penalty_team] = 0
        team_games[penalty_team] = set()
    
    team_penalties[penalty_team] += 1
    team_games[penalty_team].add(game_id)

# calculate penalties per game for each team
team_penalties_per_game = {}
for team in team_penalties:
    games_count = len(team_games[team])
    if games_count > 0:
        team_penalties_per_game[team] = team_penalties[team] / games_count

# league average
if team_penalties_per_game:
    league_avg_penalties = sum(team_penalties_per_game.values()) / len(team_penalties_per_game)
else:
    league_avg_penalties = 0

print("\n" + "="*60)
print("PENALTY DISCIPLINE ANALYSIS")
print("="*60)
print(f"\nRavens (Harbaugh) penalties per game: {ravens_penalties_per_game:.2f}")
print(f"League average penalties per game: {league_avg_penalties:.2f}")
print(f"\nRavens total penalties: {len(ravens_penalties_on_ravens)}")
print(f"Ravens total games: {ravens_total_games}")
print(f"\nLeague teams analyzed: {len(team_penalties_per_game)}")
print("\n" + "="*60)
