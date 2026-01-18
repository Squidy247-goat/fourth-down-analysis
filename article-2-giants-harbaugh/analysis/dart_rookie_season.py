# jayden dart's 2025 rookie season stats
# comparing to other rookie qbs and all nfl qbs

import pandas as pd
import glob
import os

# dart player id
DART_ID = '00-0040691'
GIANTS = 'NYG'

# get 2025 data
data_dir = '../data'
df = pd.read_csv(os.path.join(data_dir, 'play_by_play_2025.csv'))

# filter to dart's plays (giants offense)
dart_passes = df[
    (df['passer_player_id'] == DART_ID) &
    (df['pass_attempt'] == 1) &
    (df['posteam'] == GIANTS)
].copy()

dart_rushes = df[
    (df['rusher_player_id'] == DART_ID) &
    (df['rush_attempt'] == 1) &
    (df['posteam'] == GIANTS)
].copy()

# passing stats
pass_attempts = len(dart_passes)
completions = dart_passes['complete_pass'].sum()
pass_yards = dart_passes['passing_yards'].sum()
pass_tds = dart_passes['pass_touchdown'].sum()
interceptions = dart_passes['interception'].sum()

# calculate completion percentage
comp_pct = (completions / pass_attempts * 100) if pass_attempts > 0 else 0

# calculate passer rating (nfl formula)
# passer rating = ((completion% - 30) / 20 + (ypa - 3) / 4 + (td% * 20) + 2.375 - (int% * 25)) / 6 * 100
# but capped at 0-158.3
if pass_attempts > 0:
    ypa = pass_yards / pass_attempts
    td_pct = pass_tds / pass_attempts
    int_pct = interceptions / pass_attempts
    
    # components (capped between 0 and 2.375)
    comp_component = max(0, min(2.375, (comp_pct / 100 - 0.3) / 0.2))
    ypa_component = max(0, min(2.375, (ypa - 3) / 4))
    td_component = max(0, min(2.375, td_pct * 20))
    int_component = max(0, min(2.375, 2.375 - int_pct * 25))
    
    passer_rating = ((comp_component + ypa_component + td_component + int_component) / 6) * 100
else:
    passer_rating = 0

# rushing stats
rush_yards = dart_rushes['rushing_yards'].sum()
rush_tds = dart_rushes['rush_touchdown'].sum()

# total touchdowns
total_tds = pass_tds + rush_tds

# get games dart started (12 starts)
dart_games = dart_passes['game_id'].unique()
num_games = len(dart_games)

# calculate qbr by week (using qb_epa as proxy for qbr)
# group by game/week to get weekly qbr
dart_weekly = []
for game_id in dart_games:
    game_passes = dart_passes[dart_passes['game_id'] == game_id]
    game_epa = game_passes['qb_epa'].sum()
    game_attempts = len(game_passes)
    
    # get week number
    week = game_passes['week'].iloc[0] if len(game_passes) > 0 else None
    
    dart_weekly.append({
        'game_id': game_id,
        'week': week,
        'epa': game_epa,
        'attempts': game_attempts
    })

dart_weekly_df = pd.DataFrame(dart_weekly)

# compare to all qbs weekly (for top 10 qbr)
all_qb_weekly = []
for game_id in df['game_id'].unique():
    game_data = df[df['game_id'] == game_id]
    
    # get all qbs who played in this game
    qbs_in_game = game_data[game_data['pass_attempt'] == 1]['passer_player_id'].dropna().unique()
    
    for qb_id in qbs_in_game:
        qb_passes = game_data[
            (game_data['passer_player_id'] == qb_id) &
            (game_data['pass_attempt'] == 1)
        ]
        
        if len(qb_passes) >= 10:  # minimum attempts
            qb_epa = qb_passes['qb_epa'].sum()
            qb_attempts = len(qb_passes)
            week = qb_passes['week'].iloc[0] if len(qb_passes) > 0 else None
            
            all_qb_weekly.append({
                'game_id': game_id,
                'week': week,
                'qb_id': qb_id,
                'epa': qb_epa,
                'attempts': qb_attempts
            })

all_qb_weekly_df = pd.DataFrame(all_qb_weekly)

# rank qbs by epa each week (aggregate all games in that week)
top_10_weeks = 0
for week in dart_weekly_df['week'].dropna().unique():
    # get all qbs for this week (sum epa across all their games that week)
    week_qb_totals = all_qb_weekly_df[all_qb_weekly_df['week'] == week].groupby('qb_id').agg({
        'epa': 'sum',
        'attempts': 'sum'
    }).reset_index()
    
    # only qbs with at least 10 attempts
    week_qb_totals = week_qb_totals[week_qb_totals['attempts'] >= 10]
    week_qb_totals = week_qb_totals.sort_values('epa', ascending=False).reset_index(drop=True)
    week_qb_totals['rank'] = week_qb_totals.index + 1
    
    # check if dart was in top 10
    dart_week_epa = dart_weekly_df[dart_weekly_df['week'] == week]['epa'].sum()
    dart_rank_row = week_qb_totals[week_qb_totals['qb_id'] == DART_ID]
    if len(dart_rank_row) > 0 and dart_rank_row['rank'].iloc[0] <= 10:
        top_10_weeks += 1

# compare to rookie qbs
# identify rookie qbs - qbs who played in 2025 but not in previous years
# load previous year to check
prev_year = pd.read_csv(os.path.join(data_dir, 'play_by_play_2024.csv'))
prev_year_qbs = prev_year['passer_player_id'].dropna().unique()

rookie_qbs = df[
    (df['pass_attempt'] == 1) &
    (df['season'] == 2025)
].copy()

# identify rookie qbs (didn't play in 2024)
rookie_stats = []
for qb_id in rookie_qbs['passer_player_id'].dropna().unique():
    # skip if they played in 2024 (not a rookie)
    if qb_id in prev_year_qbs:
        continue
    qb_passes = rookie_qbs[rookie_qbs['passer_player_id'] == qb_id]
    qb_rushes = df[
        (df['rusher_player_id'] == qb_id) &
        (df['rush_attempt'] == 1) &
        (df['season'] == 2025)
    ]
    
    qb_pass_tds = qb_passes['pass_touchdown'].sum()
    qb_rush_tds = qb_rushes['rush_touchdown'].sum()
    qb_total_tds = qb_pass_tds + qb_rush_tds
    
    qb_pass_attempts = len(qb_passes)
    qb_completions = qb_passes['complete_pass'].sum()
    # only count qbs with meaningful attempts (at least 100)
    if qb_pass_attempts >= 100:
        qb_ypa = qb_passes['passing_yards'].sum() / qb_pass_attempts
        qb_comp_pct = (qb_completions / qb_pass_attempts * 100)
        qb_td_pct = qb_pass_tds / qb_pass_attempts
        qb_int_pct = qb_passes['interception'].sum() / qb_pass_attempts
        
        comp_comp = max(0, min(2.375, (qb_comp_pct / 100 - 0.3) / 0.2))
        ypa_comp = max(0, min(2.375, (qb_ypa - 3) / 4))
        td_comp = max(0, min(2.375, qb_td_pct * 20))
        int_comp = max(0, min(2.375, 2.375 - qb_int_pct * 25))
        qb_rating = ((comp_comp + ypa_comp + td_comp + int_comp) / 6) * 100
    else:
        qb_rating = 0
    
    qb_rush_yards = qb_rushes['rushing_yards'].sum()
    
    rookie_stats.append({
        'qb_id': qb_id,
        'total_tds': qb_total_tds,
        'passer_rating': qb_rating,
        'rush_yards': qb_rush_yards
    })

rookie_df = pd.DataFrame(rookie_stats)
# filter to meaningful sample sizes
rookie_df = rookie_df[
    (rookie_df['total_tds'] > 0) &
    (rookie_df['passer_rating'] > 0)  # must have passer rating
]

# rank dart among rookies
dart_total_tds_rank = (rookie_df['total_tds'] > total_tds).sum() + 1
dart_rating_rank = (rookie_df['passer_rating'] > passer_rating).sum() + 1
dart_rush_rank = (rookie_df['rush_yards'] > rush_yards).sum() + 1

print("\n" + "="*60)
print("JAYDEN DART 2025 ROOKIE SEASON ANALYSIS")
print("="*60)
print(f"\nPASSING STATS:")
print(f"  Completion %: {comp_pct:.2f}%")
print(f"  Passing yards: {int(pass_yards):,}")
print(f"  Passing touchdowns: {int(pass_tds)}")
print(f"  Interceptions: {int(interceptions)}")
print(f"  Passer rating: {passer_rating:.2f}")

print(f"\nRUSHING STATS:")
print(f"  Rushing yards: {int(rush_yards):,}")
print(f"  Rushing touchdowns: {int(rush_tds)}")

print(f"\nTOTAL STATS:")
print(f"  Total touchdowns: {int(total_tds)}")
print(f"  Games started: {num_games}")

print(f"\nROOKIE QB RANKINGS:")
print(f"  Total TDs rank: {dart_total_tds_rank}")
print(f"  Passer rating rank: {dart_rating_rank}")
print(f"  Rushing yards rank: {dart_rush_rank}")

print(f"\nTOP 10 QBR WEEKS:")
print(f"  Weeks in top 10: {top_10_weeks}")

print("\n" + "="*60)
