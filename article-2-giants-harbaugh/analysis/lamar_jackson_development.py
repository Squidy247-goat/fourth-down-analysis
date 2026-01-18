# lamar jackson development under harbaugh
# tracking his passing stats over different periods

import pandas as pd
import glob
import os

# lamar jackson player id
LAMAR_ID = '00-0034796'
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

# filter to lamar jackson passing plays (ravens offense)
lamar_passes = df[
    (df['passer_player_id'] == LAMAR_ID) &
    (df['pass_attempt'] == 1) &
    (df['posteam'] == RAVENS)
].copy()

# year 2 (2019) - mvp season baseline
lamar_2019 = lamar_passes[lamar_passes['season'] == 2019].copy()
yards_2019 = lamar_2019['passing_yards'].sum()
attempts_2019 = len(lamar_2019)
completions_2019 = lamar_2019['complete_pass'].sum()
ypa_2019 = yards_2019 / attempts_2019 if attempts_2019 > 0 else 0
comp_pct_2019 = (completions_2019 / attempts_2019 * 100) if attempts_2019 > 0 else 0
epa_2019 = lamar_2019['qb_epa'].sum()

# years 3-4 (2020-2022) - decline period with roman
lamar_2020_2022 = lamar_passes[lamar_passes['season'].between(2020, 2022)].copy()
yards_2020_2022 = lamar_2020_2022['passing_yards'].sum()
attempts_2020_2022 = len(lamar_2020_2022)
completions_2020_2022 = lamar_2020_2022['complete_pass'].sum()
ypa_2020_2022 = yards_2020_2022 / attempts_2020_2022 if attempts_2020_2022 > 0 else 0
comp_pct_2020_2022 = (completions_2020_2022 / attempts_2020_2022 * 100) if attempts_2020_2022 > 0 else 0
epa_2020_2022 = lamar_2020_2022['qb_epa'].sum()

# years 5-6 (2023-2024) - recovery with monken
lamar_2023_2024 = lamar_passes[lamar_passes['season'].between(2023, 2024)].copy()
yards_2023_2024 = lamar_2023_2024['passing_yards'].sum()
attempts_2023_2024 = len(lamar_2023_2024)
completions_2023_2024 = lamar_2023_2024['complete_pass'].sum()
ypa_2023_2024 = yards_2023_2024 / attempts_2023_2024 if attempts_2023_2024 > 0 else 0
comp_pct_2023_2024 = (completions_2023_2024 / attempts_2023_2024 * 100) if attempts_2023_2024 > 0 else 0
epa_2023_2024 = lamar_2023_2024['qb_epa'].sum()

# calculate per-game and per-attempt averages for epa
games_2020_2022 = lamar_2020_2022['game_id'].nunique()
games_2023_2024 = lamar_2023_2024['game_id'].nunique()
epa_per_game_2020_2022 = epa_2020_2022 / games_2020_2022 if games_2020_2022 > 0 else 0
epa_per_game_2023_2024 = epa_2023_2024 / games_2023_2024 if games_2023_2024 > 0 else 0
epa_per_attempt_2020_2022 = epa_2020_2022 / attempts_2020_2022 if attempts_2020_2022 > 0 else 0
epa_per_attempt_2023_2024 = epa_2023_2024 / attempts_2023_2024 if attempts_2023_2024 > 0 else 0

print("\n" + "="*60)
print("LAMAR JACKSON DEVELOPMENT ANALYSIS")
print("="*60)
print("\nYEAR 2 (2019) - MVP SEASON:")
print(f"  Yards per attempt: {ypa_2019:.2f}")
print(f"  Completion %: {comp_pct_2019:.2f}%")
print(f"  Total passing EPA: {epa_2019:.2f}")
print(f"  Attempts: {attempts_2019}")

print("\nYEARS 3-4 (2020-2022) - DECLINE WITH ROMAN:")
print(f"  Yards per attempt: {ypa_2020_2022:.2f}")
print(f"  Completion %: {comp_pct_2020_2022:.2f}%")
print(f"  Passing EPA per game: {epa_per_game_2020_2022:.2f}")
print(f"  Total attempts: {attempts_2020_2022}")
print(f"  Games: {games_2020_2022}")

print("\nYEARS 5-6 (2023-2024) - RECOVERY WITH MONKEN:")
print(f"  Yards per attempt: {ypa_2023_2024:.2f}")
print(f"  Completion %: {comp_pct_2023_2024:.2f}%")
print(f"  Passing EPA per game: {epa_per_game_2023_2024:.2f}")
print(f"  Total attempts: {attempts_2023_2024}")
print(f"  Games: {games_2023_2024}")

print("\n" + "-"*60)
print("KEY STATISTICS FOR BLOG:")
print("-"*60)
print(f"\nYards per attempt drop (2019 to 2020-2022): {ypa_2019:.2f} -> {ypa_2020_2022:.2f}")
print(f"Completion % in decline period (2020-2022): {comp_pct_2020_2022:.2f}%")
print(f"\nPassing EPA per attempt:")
print(f"  2020-2022 (Roman): {epa_per_attempt_2020_2022:.3f}")
print(f"  2023-2024 (Monken): {epa_per_attempt_2023_2024:.3f}")
print(f"  EPA improvement: {epa_per_attempt_2023_2024 / epa_per_attempt_2020_2022:.2f}x" if epa_per_attempt_2020_2022 > 0 else "N/A")
print(f"\nPassing EPA per game:")
print(f"  2020-2022 (Roman): {epa_per_game_2020_2022:.2f}")
print(f"  2023-2024 (Monken): {epa_per_game_2023_2024:.2f}")
print(f"\nCompletion % recovery (2023-2024): {comp_pct_2023_2024:.2f}%")
print(f"Yards per attempt recovery (2023-2024): {ypa_2023_2024:.2f}")
print("\n" + "="*60)
