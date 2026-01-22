import pandas as pd
import yaml
from pathlib import Path
import sys
import datetime

# Add script directory to path to import utils if needed
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

def build_monthly_tenure_panel():
    config = load_config()
    root_dir = Path(__file__).parent.parent
    
    # Configuration
    step_config = config['step_00c']
    input_path = root_dir / config['paths']['outputs'] / '2.0b_BuildMasterTenureMap' / 'latest' / 'master_tenure_map.parquet'
    output_subdir = step_config['output_subdir']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = root_dir / config['paths']['outputs'] / output_subdir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = setup_logging(output_dir, output_subdir)
    log_message(f"Starting Step 00c: Build Monthly Tenure Panel", log_file)
    log_message(f"Input: {input_path}", log_file)
    log_message(f"Output Directory: {output_dir}", log_file)

    # 1. Load Master Tenure Map
    try:
        df = pd.read_parquet(input_path)
        log_message(f"Loaded {len(df)} tenure records.", log_file)
    except Exception as e:
        log_message(f"CRITICAL ERROR: Failed to load input file. {e}", log_file)
        sys.exit(1)

    # 2. Expand to Monthly Panel
    monthly_records = []
    
    for _, row in df.iterrows():
        start_date = row['tenure_start_date']
        end_date = row['tenure_end_date']
        
        if pd.isna(start_date):
            continue # Skip invalid start dates

        # Handle active CEOs (sentinel date 2100) or missing end dates
        if pd.isna(end_date) or end_date.year > 2025:
            display_end = pd.Timestamp("2025-12-31")
        else:
            display_end = end_date
            
        # Generate monthly range (Month Start)
        # We use 'MS' (Month Start) so 2017-01-15 becomes 2017-01-01
        # If a tenure starts mid-month, say Jan 15, and we use MS, 
        # pd.date_range('2017-01-15', '2017-02-15', freq='MS') -> ['2017-02-01']
        # This misses January!
        # Fix: Normalize start to 1st of month
        norm_start = start_date.replace(day=1)
        
        months = pd.date_range(start=norm_start, end=display_end, freq='MS')
        
        for month_date in months:
            monthly_records.append({
                'gvkey': row['gvkey'],
                'year': month_date.year,
                'month': month_date.month,
                'date': month_date,
                'ceo_id': row['co_per_rol'],
                'ceo_name': row['exec_fullname'],
                'ceo_interim_status': row['Interim & Co-CEO'],
                'tenure_seq': row['tenure_seq'],
                'coname': row['coname']
            })

    panel_df = pd.DataFrame(monthly_records)
    
    # 3. Conflict Resolution (Duplicate Month-Keys)
    # If multiple CEOs are active in the same month (e.g., transition on Jan 15),
    # we have two rows for Jan 2017.
    # Strategy: Keep the one that started LATER? Or EARLIER?
    # Usually, for matching calls, we want the CEO who was active for the MAJORITY of the month?
    # Or just flag it?
    # Simple heuristic: Keep the last one (assuming chronological order in processing implies later start)
    # Better: Sort by tenure_seq and keep last (incumbent takes precedence over outgoing?)
    # Actually, if transition is Jan 15, outgoing is Jan 1-15, incoming is Jan 15-31.
    # A call on Jan 20 should match incoming. A call on Jan 5 should match outgoing.
    # BUT we are doing MONTHLY matching. We lose day precision.
    # User accepted this limitation.
    # We will keep the LAST one (incoming CEO) for the transition month.
    
    initial_len = len(panel_df)
    panel_df = panel_df.sort_values(['gvkey', 'year', 'month', 'tenure_seq'])
    panel_df = panel_df.drop_duplicates(subset=['gvkey', 'year', 'month'], keep='last')
    
    log_message(f"Expanded to {initial_len} monthly rows.", log_file)
    log_message(f"After resolving monthly conflicts: {len(panel_df)} rows.", log_file)

    # 4. Save Output
    output_file = output_dir / 'master_tenure_monthly.parquet'
    panel_df.to_parquet(output_file, index=False)
    log_message(f"Saved Monthly Tenure Panel to: {output_file}", log_file)
    
    # Update 'latest'
    latest_output_dir = root_dir / config['paths']['outputs'] / output_subdir / 'latest'
    latest_output_dir.mkdir(parents=True, exist_ok=True)
    panel_df.to_parquet(latest_output_dir / 'master_tenure_monthly.parquet', index=False)
    log_message(f"Updated 'latest' output directory.", log_file)

if __name__ == "__main__":
    build_monthly_tenure_panel()
