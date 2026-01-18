
# looks at punt and kickoff returns


import pandas as pd
from pathlib import Path

def analyze_pkr_data():
    
    print(f"\n{'='*80}")
    print("PUNT AND KICKOFF RETURN ANALYSIS (2008-2011)")
    print(f"{'='*80}\n")
    
    years = [2008, 2009, 2010, 2011]
    all_results = []
    
    for year in years:
        file_path = Path(__file__).parent.parent / "csvFiles" / f"pkr{year}.csv"
        
        print(f"\n{'='*60}")
        print(f"{year} Season")
        print(f"{'='*60}")
        
        test_df = pd.read_csv(file_path, nrows=3)
        
        if any('Punt Returns' in str(col) for col in test_df.columns):
            # 2011 has weird format
            df = pd.read_csv(file_path, skiprows=[0])
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        else:
            # normal csv
            df = pd.read_csv(file_path)
        
        # clean up column names
        df.columns = df.columns.str.strip()
        
        # find ravens row
        ravens_row = df[df['Tm'].str.contains('Baltimore Ravens', na=False)]
        
        if ravens_row.empty:
            print(f"Ravens not found in {year}")
            continue
        
        ravens_data = ravens_row.iloc[0]
        rank_val = ravens_data['Rk'] if 'Rk' in ravens_data.index else ravens_data.iloc[0]
        rank = int(rank_val) if pd.notna(rank_val) else 0
        
        # get punt return numbers
        ret_val = ravens_data['Ret'] if 'Ret' in ravens_data.index else 0
        punt_returns = int(ret_val) if pd.notna(ret_val) and ret_val != '' else 0
        
        try:
            yds_val = ravens_data['Yds']
            if isinstance(yds_val, pd.Series):
                yds_val = yds_val.iloc[0]
            punt_yards = int(yds_val) if pd.notna(yds_val) and yds_val != '' else 0
        except:
            punt_yards = 0
            
        try:
            td_val = ravens_data['TD']
            if isinstance(td_val, pd.Series):
                td_val = td_val.iloc[0]
            punt_tds = int(td_val) if pd.notna(td_val) and td_val != '' else 0
        except:
            punt_tds = 0
        
        # get kickoff return numbers
        try:
            rt_val = ravens_data['Rt']
            if isinstance(rt_val, pd.Series):
                rt_val = rt_val.iloc[0]
            kick_returns = int(rt_val) if pd.notna(rt_val) and rt_val != '' else 0
        except:
            kick_returns = 0
        
        kick_yards = 0
        kick_tds = 0
        
        if 'Yds.1' in ravens_data.index:
            try:
                yds_val = ravens_data['Yds.1']
                if isinstance(yds_val, pd.Series):
                    yds_val = yds_val.iloc[0]
                kick_yards = int(yds_val) if pd.notna(yds_val) and yds_val != '' else 0
            except:
                pass
                
            try:
                td_val = ravens_data['TD.1']
                if isinstance(td_val, pd.Series):
                    td_val = td_val.iloc[0]
                kick_tds = int(td_val) if pd.notna(td_val) and td_val != '' else 0
            except:
                pass
        else:
            # find the right columns
            cols = list(df.columns)
            yds_idx = [i for i, col in enumerate(cols) if 'Yds' in str(col)]
            td_idx = [i for i, col in enumerate(cols) if 'TD' in str(col)]
            
            if len(yds_idx) >= 2:
                try:
                    kick_yards = int(ravens_data.iloc[yds_idx[1]]) if pd.notna(ravens_data.iloc[yds_idx[1]]) else 0
                except:
                    kick_yards = 0
                    
            if len(td_idx) >= 2:
                try:
                    kick_tds = int(ravens_data.iloc[td_idx[1]]) if pd.notna(ravens_data.iloc[td_idx[1]]) else 0
                except:
                    kick_tds = 0
        
        yr_per_punt = punt_yards / punt_returns if punt_returns > 0 else 0
        yr_per_kick = kick_yards / kick_returns if kick_returns > 0 else 0
        
        total_return_tds = punt_tds + kick_tds
        total_returns = punt_returns + kick_returns
        total_return_yards = punt_yards + kick_yards
        
        print(f"Rank: {rank} of 32")
        print(f"\nPunt Returns:")
        print(f"  Returns: {punt_returns}")
        print(f"  Yards: {punt_yards}")
        print(f"  TDs: {punt_tds}")
        print(f"  Avg: {yr_per_punt:.1f} yards/return")
        print(f"\nKickoff Returns:")
        print(f"  Returns: {kick_returns}")
        print(f"  Yards: {kick_yards}")
        print(f"  TDs: {kick_tds}")
        print(f"  Avg: {yr_per_kick:.1f} yards/return")
        print(f"\nTotal Return TDs: {total_return_tds}")
        
        all_results.append({
            'year': year,
            'rank': rank,
            'punt_returns': punt_returns,
            'punt_yards': punt_yards,
            'punt_tds': punt_tds,
            'kick_returns': kick_returns,
            'kick_yards': kick_yards,
            'kick_tds': kick_tds,
            'total_return_tds': total_return_tds,
            'total_returns': total_returns,
            'total_return_yards': total_return_yards
        })
    
    # calculate totals and averages
    total_punt_tds = sum(r['punt_tds'] for r in all_results)
    total_kick_tds = sum(r['kick_tds'] for r in all_results)
    total_return_tds = sum(r['total_return_tds'] for r in all_results)
    total_return_yards = sum(r['total_return_yards'] for r in all_results)
    total_returns = sum(r['total_returns'] for r in all_results)
    avg_rank = sum(r['rank'] for r in all_results) / len(all_results)
    
    print(f"\n{'='*80}")
    print("SUMMARY (2008-2011)")
    print(f"{'='*80}\n")
    
    for result in all_results:
        print(f"{result['year']}: Rank {int(result['rank']):2d} | "
              f"Punt TDs: {result['punt_tds']} | "
              f"Kick TDs: {result['kick_tds']} | "
              f"Total Return TDs: {result['total_return_tds']}")
    
    print(f"\n{'='*80}")
    print("TOTALS (2008-2011)")
    print(f"{'='*80}")
    print(f"Total Return TDs: {total_return_tds} ({total_punt_tds} punt + {total_kick_tds} kickoff)")
    print(f"Total Return Yards: {total_return_yards:,}")
    print(f"Total Returns: {total_returns}")
    print(f"Average Rank: {avg_rank:.1f} of 32")
    
    print(f"\n{'='*80}")
    print("BLOG FORMAT:")
    print(f"{'='*80}")
    print(f"\nReturn touchdowns: {total_return_tds} (Rank: {avg_rank:.0f} average over 4 years)")
    print(f"  - {total_punt_tds} punt return TDs")
    print(f"  - {total_kick_tds} kickoff return TDs")
    
    # year by year rankings
    print(f"\nYear-by-year rankings in all-purpose yards from returns:")
    for result in all_results:
        print(f"  {result['year']}: Rank {result['rank']} of 32")
    
    return all_results


if __name__ == "__main__":
    analyze_pkr_data()
