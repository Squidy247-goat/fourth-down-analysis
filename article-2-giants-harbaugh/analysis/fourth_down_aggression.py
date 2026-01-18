# fourth down conversion rates 2018-2024
# comparing harbaugh's ravens vs giants

import pandas as pd
import glob
import os

# team codes
RAVENS = 'BAL'
GIANTS = 'NYG'

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

# only 2018-2024
df = df[df['season'].between(2018, 2024)]

# filter to fourth down plays
fourth_down = df[df['down'] == 4].copy()

# only count actual attempts (where they went for it, not punts or field goals)
# fourth_down_converted or fourth_down_failed being not null means it was an actual attempt
fourth_down = fourth_down[
    ((fourth_down['fourth_down_converted'].notna()) | 
     (fourth_down['fourth_down_failed'].notna())) &
    (~fourth_down['play_type'].isin(['punt', 'field_goal']))
]

# ravens fourth down stats
ravens_fourth = fourth_down[fourth_down['posteam'] == RAVENS].copy()
ravens_converted = ravens_fourth['fourth_down_converted'].sum()
ravens_attempts = len(ravens_fourth)
ravens_rate = (ravens_converted / ravens_attempts * 100) if ravens_attempts > 0 else 0

# giants fourth down stats
giants_fourth = fourth_down[fourth_down['posteam'] == GIANTS].copy()
giants_converted = giants_fourth['fourth_down_converted'].sum()
giants_attempts = len(giants_fourth)
giants_rate = (giants_converted / giants_attempts * 100) if giants_attempts > 0 else 0

print("\n" + "="*60)
print("FOURTH DOWN CONVERSION RATE (2018-2024)")
print("="*60)
print(f"\nRavens (Harbaugh) conversion rate: {ravens_rate:.2f}%")
print(f"Giants conversion rate: {giants_rate:.2f}%")
print(f"\nRavens attempts: {ravens_attempts:,}")
print(f"Ravens converted: {int(ravens_converted):,}")
print(f"\nGiants attempts: {giants_attempts:,}")
print(f"Giants converted: {int(giants_converted):,}")
print("\n" + "="*60)
