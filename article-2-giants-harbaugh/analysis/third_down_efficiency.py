# third down efficiency for giants 2016-2025
# trying to figure out how bad they are at converting third downs

import pandas as pd
import glob
import os

# giants team code
GIANTS = 'NYG'

# get all the csv files from the data folder
data_dir = '../data'
csv_files = sorted(glob.glob(os.path.join(data_dir, 'play_by_play_*.csv')))

# load all the files
all_data = []
for file in csv_files:
    print(f"Loading {file}...")
    df = pd.read_csv(file)
    all_data.append(df)

# put everything together
df = pd.concat(all_data, ignore_index=True)

# only look at 2016-2025
df = df[df['season'].between(2016, 2025)]

# filter to just third down plays
third_down = df[df['down'] == 3].copy()

# get rid of plays where third_down_converted and third_down_failed are both NaN (those dont count)
third_down = third_down[
    (third_down['third_down_converted'].notna()) | 
    (third_down['third_down_failed'].notna())
]

# calculate giants stats
giants_third_down = third_down[third_down['posteam'] == GIANTS].copy()
giants_converted = giants_third_down['third_down_converted'].sum()
giants_attempts = len(giants_third_down)
giants_rate = (giants_converted / giants_attempts * 100) if giants_attempts > 0 else 0

# calculate league stats (not including giants)
league_third_down = third_down[third_down['posteam'] != GIANTS].copy()
league_converted = league_third_down['third_down_converted'].sum()
league_attempts = len(league_third_down)
league_rate = (league_converted / league_attempts * 100) if league_attempts > 0 else 0

# figure out where giants rank
team_stats = []
for team in third_down['posteam'].dropna().unique():
    if pd.isna(team):
        continue
    team_data = third_down[third_down['posteam'] == team]
    team_converted = team_data['third_down_converted'].sum()
    team_attempts = len(team_data)
    if team_attempts > 0:
        team_rate = (team_converted / team_attempts * 100)
        team_stats.append({'team': team, 'rate': team_rate, 'attempts': team_attempts})

team_df = pd.DataFrame(team_stats)
team_df = team_df.sort_values('rate', ascending=False).reset_index(drop=True)
team_df['rank'] = team_df.index + 1

giants_rank = team_df[team_df['team'] == GIANTS]['rank'].values[0] if len(team_df[team_df['team'] == GIANTS]) > 0 else None

# calculate how many drives they failed and how many wins that cost them
# average drives per game is like 12, games per season is 17
avg_drives_per_game = 12
games_per_season = 17
seasons = len(df['season'].unique())
total_games = seasons * games_per_season

# giants failed third downs per game
giants_failed_per_game = (giants_attempts / total_games) * (1 - giants_rate/100)
league_failed_per_game = (league_attempts / (total_games * 31)) * (1 - league_rate/100)  # 31 other teams

# how many more drives they failed compared to league average
additional_failed_per_season = (giants_failed_per_game - league_failed_per_game) * games_per_season

# estimate wins lost - each failed drive probably costs like 0.05 wins or something
wins_lost_per_season = additional_failed_per_season * 0.05

print("\n" + "="*60)
print("THIRD DOWN EFFICIENCY ANALYSIS (2016-2025)")
print("="*60)
print(f"\nGiants conversion rate: {giants_rate:.2f}%")
print(f"League average: {league_rate:.2f}%")
print(f"League rank: {int(giants_rank)}")
print(f"\nGiants attempts: {giants_attempts:,}")
print(f"Giants converted: {giants_converted:,}")
print(f"\nAdditional failed drives per season: {additional_failed_per_season:.1f}")
print(f"Estimated wins lost per season: {wins_lost_per_season:.2f}")
print("\n" + "="*60)
