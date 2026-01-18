# challenge success rate for harbaugh's ravens
# comparing to league average

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

# filter to plays where there was a challenge (replay_or_challenge == 1)
challenges = df[df['replay_or_challenge'] == 1].copy()

# get ravens challenges
ravens_challenges = challenges[
    ((challenges['home_team'] == RAVENS) | (challenges['away_team'] == RAVENS))
].copy()

# figure out if challenge was successful
# "reversed" means challenge was successful (call was overturned)
# "upheld" means challenge failed (call stood)
ravens_total_challenges = len(ravens_challenges)
ravens_reversed = ravens_challenges[
    ravens_challenges['replay_or_challenge_result'].str.contains('reversed', case=False, na=False)
].shape[0]

ravens_upheld = ravens_challenges[
    ravens_challenges['replay_or_challenge_result'].str.contains('upheld', case=False, na=False)
].shape[0]

# success rate - reversed means challenge worked
ravens_success_rate = (ravens_reversed / ravens_total_challenges * 100) if ravens_total_challenges > 0 else 0

# league average
league_challenges = challenges[
    (challenges['home_team'] != RAVENS) & 
    (challenges['away_team'] != RAVENS)
].copy()

league_total = len(league_challenges)
league_reversed = league_challenges[
    league_challenges['replay_or_challenge_result'].str.contains('reversed', case=False, na=False)
].shape[0]

league_success_rate = (league_reversed / league_total * 100) if league_total > 0 else 0

print("\n" + "="*60)
print("CHALLENGE SUCCESS RATE ANALYSIS")
print("="*60)
print(f"\nRavens (Harbaugh) challenges: {ravens_total_challenges}")
print(f"Ravens successful (reversed): {ravens_reversed}")
print(f"Ravens failed (upheld): {ravens_upheld}")
print(f"Ravens success rate: {ravens_success_rate:.2f}%")
print(f"\nLeague average success rate: {league_success_rate:.2f}%")
print(f"\nLeague total challenges: {league_total}")
print(f"League successful (reversed): {league_reversed}")
print("\n" + "="*60)
