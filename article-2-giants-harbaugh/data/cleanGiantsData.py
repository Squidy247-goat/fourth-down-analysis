# Clean Giants play-by-play data
# Filters all play-by-play CSV files to only include Giants offensive plays
# Outputs files named pbpGiants{year}.csv

import pandas as pd
import glob
import os
import re

# Giants team code
GIANTS = 'NYG'

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = script_dir

# Find all play_by_play CSV files
csv_files = sorted(glob.glob(os.path.join(data_dir, 'play_by_play_*.csv')))
print(f"Found {len(csv_files)} play-by-play CSV files")

# Process each file
for file_path in csv_files:
    # Extract year from filename (e.g., play_by_play_2016.csv -> 2016)
    filename = os.path.basename(file_path)
    year_match = re.search(r'play_by_play_(\d{4})\.csv', filename)
    
    if not year_match:
        print(f"Warning: Could not extract year from {filename}, skipping...")
        continue
    
    year = year_match.group(1)
    print(f"\nProcessing {filename} (year: {year})...")
    
    # Read the CSV file
    try:
        df = pd.read_csv(file_path)
        print(f"  Loaded {len(df):,} total plays")
        
        # Filter for Giants offensive plays (where Giants have possession)
        giants_plays = df[df['posteam'] == GIANTS].copy()
        print(f"  Found {len(giants_plays):,} Giants offensive plays")
        
        # Create output filename
        output_filename = f'pbpGiants{year}.csv'
        output_path = os.path.join(data_dir, output_filename)
        
        # Save the filtered data
        giants_plays.to_csv(output_path, index=False)
        print(f"  Saved to {output_filename}")
        
    except Exception as e:
        print(f"  Error processing {filename}: {e}")
        continue

print("\n" + "="*60)
print("Giants data cleaning complete!")
print("="*60)
