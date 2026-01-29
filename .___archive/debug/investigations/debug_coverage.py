import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from datetime import datetime, timedelta

def load_config():
    config_path = Path("config/project.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    root = Path(".")
    year = 2010
    ceo_data_dir = root / '4_Outputs' / '2.5b_LinkCallsToCeo' / 'latest'
    call_file = ceo_data_dir / f"f1d_enriched_ceo_{year}.parquet"
    
    if not call_file.exists(): return

    df = pd.read_parquet(call_file)
    target_file = "666892_T"
    target_row = df[df['file_name'].str.contains(target_file, na=False)]
    
    if len(target_row) == 0:
        print("Target not found, picking random")
        target_row = df[df['LPERMNO'].notna()].iloc[[0]]
    
    lpermno = target_row['LPERMNO'].iloc[0]
    start_date = pd.to_datetime(target_row['start_date'].iloc[0])
    call_year = start_date.year
    
    print(f"Call: {target_row['file_name'].iloc[0]}, Date: {start_date}, Year: {call_year}, LPERMNO: {lpermno}")
    
    crsp_dir = root / '1_Inputs' / 'CRSP_DSF'
    crsp_dfs = []
    for q in range(1, 5):
        f = crsp_dir / f"CRSP_DSF_{call_year}_Q{q}.parquet"
        if f.exists(): crsp_dfs.append(pd.read_parquet(f))
            
    if not crsp_dfs: return
    crsp = pd.concat(crsp_dfs)
    
    if 'PERMNO' in crsp.columns: crsp.rename(columns={'PERMNO': 'permno'}, inplace=True)
    if 'DATE' in crsp.columns: crsp.rename(columns={'DATE': 'date'}, inplace=True)
    crsp['date'] = pd.to_datetime(crsp['date'])
        
    try:
        lpermno_int = int(float(lpermno))
        firm_crsp = crsp[crsp['permno'] == lpermno_int].copy()
        print(f"CRSP records for {lpermno_int}: {len(firm_crsp)}")
        
        if len(firm_crsp) > 0:
            window_start = start_date - timedelta(days=100)
            window_end = start_date + timedelta(days=10)
            mask = (firm_crsp['date'] >= window_start) & (firm_crsp['date'] <= window_end)
            print(f"Records in window: {mask.sum()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
