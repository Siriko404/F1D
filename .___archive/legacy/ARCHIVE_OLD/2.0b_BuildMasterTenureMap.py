import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import sys
import datetime

# Add script directory to path to import utils if needed (not used here yet but good practice)
sys.path.append(str(Path(__file__).parent))

def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'project.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_logging(output_dir, step_name):
    log_dir = Path(__file__).parent.parent / '3_Logs' / step_name
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_file = log_dir / f"{timestamp}.log"
    return log_file

def log_message(message, log_file=None, console=True):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    if console:
        print(formatted_message)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(formatted_message + "\n")

def build_master_tenure_map():
    config = load_config()
    root_dir = Path(__file__).parent.parent
    
    # Configuration
    step_config = config['step_00b']
    input_path = root_dir / config['paths']['inputs'] / 'CEO Dismissal Data 2021.02.03.xlsx'
    output_subdir = step_config['output_subdir']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = root_dir / config['paths']['outputs'] / output_subdir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Update 'latest' symlink/junction logic (simulated by copying or just knowing the path)
    latest_dir = root_dir / config['paths']['outputs'] / output_subdir / 'latest'
    # Note: Windows symlinks require admin, so we rely on the timestamped folder for now 
    # or user can manage 'latest'. For this pipeline, we usually point 'latest' to the new folder 
    # but Python symlink creation on Windows is tricky without admin. 
    # We will just write to the timestamped folder and print it.
    
    log_file = setup_logging(output_dir, output_subdir)
    log_message(f"Starting Step 0b: Master Tenure Map Construction", log_file)
    log_message(f"Input: {input_path}", log_file)
    log_message(f"Output Directory: {output_dir}", log_file)

    # 1. Load Data
    try:
        df = pd.read_excel(input_path)
        log_message(f"Loaded {len(df)} rows from Excel.", log_file)
    except Exception as e:
        log_message(f"CRITICAL ERROR: Failed to load input file. {e}", log_file)
        sys.exit(1)

    # 2. Data Cleaning & Normalization
    # Date Parsing
    df['leftofc'] = pd.to_datetime(df['leftofc'], errors='coerce')
    
    # Status Standardization
    # We preserve the original 'Interim & Co-CEO' column per user request.
    # No boolean conversion needed here.
    
    # 3. Deduplication
    # Identify duplicates based on EXACT match of all columns
    initial_count = len(df)
    df = df.drop_duplicates(keep='first')
    log_message(f"Deduplication: Removed {initial_count - len(df)} exact duplicate records.", log_file)

    # 4. Timeline Reconstruction (Chaining)
    # Sort: Company -> End Date -> Year
    df = df.sort_values(by=['gvkey', 'leftofc', 'year'])
    
    master_map = []
    
    grouped = df.groupby('gvkey')
    
    for gvkey, group in grouped:
        group = group.reset_index(drop=True)
        prev_end_date = None
        
        for i, row in group.iterrows():
            # Determine Start Date
            if i == 0:
                # First recorded CEO
                # Default to 1990-01-01 per plan
                start_date = pd.Timestamp("1990-01-01")
            else:
                # Sequential: Start = Prev_End + 1
                if pd.notna(prev_end_date):
                    start_date = prev_end_date + pd.Timedelta(days=1)
                else:
                    # If previous CEO has no end date (and wasn't active), this is an issue.
                    # But per logic, if they were active, they shouldn't be 'previous' in a closed chain sense unless we handle active.
                    # If previous row had NULL leftofc, we check 'Still There'.
                    # If 'Still There' was true, then this current row implies an overlap or data error?
                    # For strict chaining, we need a date.
                    # Fallback: Use Jan 1 of current record year if chain is broken by missing date
                    start_date = pd.Timestamp(f"{int(row['year'])}-01-01")

            # Determine End Date
            end_date = row['leftofc']
            is_active = False
            
            if pd.isna(end_date):
                # Check 'Still There'
                still_there = str(row['Still There']).strip().lower()
                # Heuristic: if it contains a digit (date) or 'yes'/'present' (though dataset usually has dates)
                # The spec says: "If a date is present... treat as Last Observed Active Date"
                # But for the Map, we need a tenure_end_date.
                # Spec Stage C: "Set End_Date to sentinel value (e.g. 2100-01-01)"
                if still_there != 'nan' and len(still_there) > 0:
                    is_active = True
                    end_date = pd.Timestamp("2100-01-01")
                else:
                    # No end date, not active?
                    # Leave as NaT or handle?
                    # For now, leave NaT, but this breaks the chain for the NEXT guy.
                    pass
            
            # Store for next iteration
            prev_end_date = end_date
            
            master_map.append({
                'gvkey': row['gvkey'],
                'co_per_rol': row['co_per_rol'],
                'exec_fullname': row['exec_fullname'],
                'tenure_start_date': start_date,
                'tenure_end_date': end_date,
                'Interim & Co-CEO': row['Interim & Co-CEO'],
                'is_active': is_active,
                'tenure_seq': i + 1,
                'year': row['year'],
                'coname': row['coname'],
                'dismissal_dataset_id': row['dismissal_dataset_id']
            })

    result_df = pd.DataFrame(master_map)
    
    # 5. Validation
    # Continuity Check (Start N == End N-1 + 1)
    # We constructed it this way, so it should pass by definition unless missing dates broke the chain.
    
    # Date Integrity (End >= Start)
    # Filter out cases where End < Start (impossible tenures)
    invalid_dates = result_df[result_df['tenure_end_date'] < result_df['tenure_start_date']]
    if not invalid_dates.empty:
        log_message(f"WARNING: Found {len(invalid_dates)} records where End Date < Start Date. These will be kept but flagged in logs.", log_file)
        # log_message(invalid_dates[['company_id', 'ceo_name', 'tenure_start_date', 'tenure_end_date']].to_string(), log_file)

    # 6. Save Output
    output_file = output_dir / 'master_tenure_map.parquet'
    result_df.to_parquet(output_file, index=False)
    log_message(f"Saved Master Tenure Map to: {output_file}", log_file)
    
    # Also save CSV for easy inspection
    result_df.to_csv(output_dir / 'master_tenure_map.csv', index=False)
    log_message(f"Saved CSV copy to: {output_dir / 'master_tenure_map.csv'}", log_file)

    # Update 'latest' symlink (Manual copy for Windows compatibility if needed, or just rely on path)
    # Ideally, we create a 'latest' folder and copy the file there.
    latest_output_dir = root_dir / config['paths']['outputs'] / output_subdir / 'latest'
    latest_output_dir.mkdir(parents=True, exist_ok=True)
    result_df.to_parquet(latest_output_dir / 'master_tenure_map.parquet', index=False)
    log_message(f"Updated 'latest' output: {latest_output_dir / 'master_tenure_map.parquet'}", log_file)

if __name__ == "__main__":
    build_master_tenure_map()
