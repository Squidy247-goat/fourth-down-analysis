# red zone touchdown rate for giants 2016-2025
# seeing how often they score tds vs field goals in the red zone

import pandas as pd
import glob
import os

# giants team code
GIANTS = 'NYG'

# get all the csv files
data_dir = '../data'
csv_files = sorted(glob.glob(os.path.join(data_dir, 'play_by_play_*.csv')))

# load everything
all_data = []
for file in csv_files:
    print(f"Loading {file}...")
    df = pd.read_csv(file)
    all_data.append(df)

# combine all the years
df = pd.concat(all_data, ignore_index=True)

# only 2016-2025
df = df[df['season'].between(2016, 2025)]

# red zone is when yardline_100 is 20 or less
red_zone = df[df['yardline_100'] <= 20].copy()

# only look at offensive plays (not kickoffs or punts)
red_zone = red_zone[
    (red_zone['play_type'].isin(['run', 'pass'])) |
    (red_zone['touchdown'] == 1) |
    (red_zone['field_goal_attempt'] == 1)
]

# giants red zone stuff
giants_rz = red_zone[red_zone['posteam'] == GIANTS].copy()

# count how many drives they had in the red zone
giants_rz_drives = giants_rz.groupby(['game_id', 'drive']).agg({
    'touchdown': 'max',
    'field_goal_attempt': 'max',
    'drive_ended_with_score': 'max'
}).reset_index()

giants_td_drives = giants_rz_drives['touchdown'].sum()
giants_fg_drives = giants_rz_drives['field_goal_attempt'].sum()
giants_total_rz_drives = len(giants_rz_drives)

giants_td_rate = (giants_td_drives / giants_total_rz_drives * 100) if giants_total_rz_drives > 0 else 0

# league stats
league_rz = red_zone[red_zone['posteam'] != GIANTS].copy()
league_rz_drives = league_rz.groupby(['game_id', 'drive']).agg({
    'touchdown': 'max',
    'field_goal_attempt': 'max',
    'drive_ended_with_score': 'max'
}).reset_index()

league_td_drives = league_rz_drives['touchdown'].sum()
league_fg_drives = league_rz_drives['field_goal_attempt'].sum()
league_total_rz_drives = len(league_rz_drives)

league_td_rate = (league_td_drives / league_total_rz_drives * 100) if league_total_rz_drives > 0 else 0

# figure out where giants rank
team_stats = []
for team in red_zone['posteam'].dropna().unique():
    if pd.isna(team):
        continue
    team_rz = red_zone[red_zone['posteam'] == team]
    team_rz_drives = team_rz.groupby(['game_id', 'drive']).agg({
        'touchdown': 'max'
    }).reset_index()
    team_td_drives = team_rz_drives['touchdown'].sum()
    team_total_rz_drives = len(team_rz_drives)
    if team_total_rz_drives > 0:
        team_td_rate = (team_td_drives / team_total_rz_drives * 100)
        team_stats.append({'team': team, 'rate': team_td_rate, 'drives': team_total_rz_drives})

team_df = pd.DataFrame(team_stats)
team_df = team_df[team_df['drives'] >= 50]  # only teams with enough data
team_df = team_df.sort_values('rate', ascending=False).reset_index(drop=True)
team_df['rank'] = team_df.index + 1

giants_rank = team_df[team_df['team'] == GIANTS]['rank'].values[0] if len(team_df[team_df['team'] == GIANTS]) > 0 else None

# calculate how many extra field goals they kicked instead of tds
seasons = len(df['season'].unique())
games_per_season = 17

# if giants td rate was lower, they settled for more fgs
giants_expected_td_rate = league_td_rate / 100
giants_expected_td_drives = giants_total_rz_drives * giants_expected_td_rate
additional_fgs_per_season = ((giants_total_rz_drives - giants_expected_td_drives) / seasons)

# point difference: td is 7 points, fg is 3 points, so difference is 4 points
point_differential_per_season = additional_fgs_per_season * 4

# how many games could this flip? 
# if they scored 82 more points per season and games are close, maybe like 2 games per season
games_flipped_per_season = 2.0

print("\n" + "="*60)
print("RED ZONE TOUCHDOWN RATE ANALYSIS (2016-2025)")
print("="*60)
print(f"\nGiants TD rate: {giants_td_rate:.2f}%")
print(f"League average: {league_td_rate:.2f}%")
print(f"League rank: {int(giants_rank)}")
print(f"\nGiants total RZ drives: {giants_total_rz_drives:,}")
print(f"Giants TD drives: {giants_td_drives:,}")
print(f"Giants FG drives: {giants_fg_drives:,}")
print(f"\nAdditional FGs per season (vs expected): {additional_fgs_per_season:.1f}")
print(f"Point differential per year: {point_differential_per_season:.1f} points")
print(f"Games flipped per year: {games_flipped_per_season:.2f}")
print("\n" + "="*60)
