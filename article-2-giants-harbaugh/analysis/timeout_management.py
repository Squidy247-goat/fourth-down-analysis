# timeout management for harbaugh's ravens
# average timeouts remaining at end of 1st and 3rd quarters

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

# find plays at end of 1st quarter (qtr == 1 and quarter_end == 1)
# and end of 3rd quarter (qtr == 3 and quarter_end == 1)
end_q1 = ravens_games[
    (ravens_games['qtr'] == 1) & 
    (ravens_games['quarter_end'] == 1)
].copy()

end_q3 = ravens_games[
    (ravens_games['qtr'] == 3) & 
    (ravens_games['quarter_end'] == 1)
].copy()

# figure out how many timeouts ravens had left
def get_ravens_timeouts(row):
    if row['home_team'] == RAVENS:
        return row['home_timeouts_remaining']
    else:  # ravens are away
        return row['away_timeouts_remaining']

end_q1['ravens_timeouts'] = end_q1.apply(get_ravens_timeouts, axis=1)
end_q3['ravens_timeouts'] = end_q3.apply(get_ravens_timeouts, axis=1)

# average timeouts remaining
avg_q1_timeouts = end_q1['ravens_timeouts'].mean() if len(end_q1) > 0 else 0
avg_q3_timeouts = end_q3['ravens_timeouts'].mean() if len(end_q3) > 0 else 0
avg_timeouts = (avg_q1_timeouts + avg_q3_timeouts) / 2

print("\n" + "="*60)
print("TIMEOUT MANAGEMENT ANALYSIS")
print("="*60)
print(f"\nAverage timeouts remaining at end of 1st quarter: {avg_q1_timeouts:.2f}")
print(f"Average timeouts remaining at end of 3rd quarter: {avg_q3_timeouts:.2f}")
print(f"\nAverage timeouts remaining (1st + 3rd quarters): {avg_timeouts:.2f}")
print(f"\nTotal games analyzed: {len(end_q1)}")
print("\n" + "="*60)
