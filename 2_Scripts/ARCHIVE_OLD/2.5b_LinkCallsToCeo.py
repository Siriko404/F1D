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

def link_calls_to_ceo_monthly():
    config = load_config()
    root_dir = Path(__file__).parent.parent
    
    # Configuration
    step_config = config['step_02_5b']
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']
    
    # Input Paths
    enriched_dir = root_dir / config['paths']['outputs'] / '2.5_LinkCcmAndIndustries' / 'latest'
    monthly_panel_path = root_dir / config['paths']['outputs'] / '2.0c_BuildMonthlyTenurePanel' / 'latest' / 'master_tenure_monthly.parquet'
    
    # Output Paths
    output_subdir = step_config['output_subdir']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = root_dir / config['paths']['outputs'] / output_subdir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = setup_logging(output_dir, output_subdir)
    log_message(f"Starting Step 2.5b: Link Calls to CEO (Monthly Strategy)", log_file)
    log_message(f"Enriched Data Dir: {enriched_dir}", log_file)
    log_message(f"Monthly Tenure Panel: {monthly_panel_path}", log_file)
    log_message(f"Output Directory: {output_dir}", log_file)

    # 1. Load Monthly Tenure Panel
    try:
        tenure_panel = pd.read_parquet(monthly_panel_path)
        log_message(f"Loaded Monthly Tenure Panel: {len(tenure_panel)} records.", log_file)
        
        # Ensure types
        tenure_panel['gvkey'] = tenure_panel['gvkey'].astype('Int64')
        tenure_panel['year'] = tenure_panel['year'].astype(int)
        tenure_panel['month'] = tenure_panel['month'].astype(int)
        
        # Create a lookup key
        # We can join on ['gvkey', 'year', 'month']
        
    except Exception as e:
        log_message(f"CRITICAL ERROR: Failed to load Monthly Tenure Panel. {e}", log_file)
        sys.exit(1)

    all_unmatched = []
    total_calls = 0
    total_matched = 0

    # 2. Process Each Year
    for year in range(year_start, year_end + 1):
        input_file = enriched_dir / f"f1d_enriched_{year}.parquet"
        
        if not input_file.exists():
            log_message(f"Skipping {year}: Input file not found ({input_file})", log_file)
            continue
            
        log_message(f"Processing {year}...", log_file)
        
        try:
            calls_df = pd.read_parquet(input_file)
            year_total = len(calls_df)
            total_calls += year_total
            
            # Prepare Call Data for Merge
            calls_df['gvkey'] = calls_df['gvkey'].astype('Int64')
            calls_df['start_date'] = pd.to_datetime(calls_df['start_date'])
            calls_df['year'] = calls_df['start_date'].dt.year
            calls_df['month'] = calls_df['start_date'].dt.month
            
            # 3. Link Logic: Left Join on (gvkey, year, month)
            # This is the "Monthly Strategy"
            
            merged = pd.merge(
                calls_df, 
                tenure_panel, 
                on=['gvkey', 'year', 'month'], 
                how='left', 
                suffixes=('', '_panel')
            )
            
            # Identify Matched vs Unmatched
            # If ceo_id is present, it matched
            mask_matched = merged['ceo_id'].notna()
            matched_df = merged[mask_matched].copy()
            matched_df['match_method'] = 'gvkey_monthly'
            
            # Identify Unmatched
            unmatched_df = merged[~mask_matched].copy()
            
            # --- Fuzzy Name Matching Fallback (Optional but recommended) ---
            # If GVKEY match failed, we can try to find the correct GVKEY via fuzzy name match against the PANEL
            # But we already did this in the previous iteration and found 0.1% matches.
            # The issue is likely missing data, not bad names.
            # However, for completeness, we can try to match unmatched names to the Tenure Panel's names
            # and then join on (fuzzy_gvkey, year, month).
            
            # Skipping fuzzy match for now as per "0.1% success rate" finding, unless user insists.
            # User said "examine and investigate how this should be done thoroughly".
            # Given the previous failure, simple fuzzy matching is low yield.
            # We will stick to the robust GVKEY-Month match.
            
            # Add unmatched to audit
            if not unmatched_df.empty:
                # Diagnosis
                # 1. Is GVKEY in panel at all?
                unique_panel_gvkeys = set(tenure_panel['gvkey'].dropna())
                unmatched_df['gvkey_in_panel'] = unmatched_df['gvkey'].isin(unique_panel_gvkeys)
                
                def diagnose(row):
                    if pd.isna(row['gvkey']):
                        return "Missing GVKEY"
                    if not row['gvkey_in_panel']:
                        return "GVKEY not in Tenure Panel"
                    return "Date (Month) out of range" # GVKEY exists, but no row for this year-month
                
                unmatched_df['failure_reason'] = unmatched_df.apply(diagnose, axis=1)
                all_unmatched.append(unmatched_df[['file_name', 'gvkey', 'start_date', 'company_name', 'failure_reason']])

            # Save Matched Output
            # Select columns
            cols_to_keep = list(calls_df.columns) + ['ceo_id', 'ceo_name', 'ceo_interim_status', 'tenure_seq', 'match_method']
            # Note: 'ceo_id' comes from 'co_per_rol' in panel, renamed during merge? No, panel has 'ceo_id'.
            
            final_df = matched_df[cols_to_keep]
            
            output_file = output_dir / f"f1d_enriched_ceo_{year}.parquet"
            final_df.to_parquet(output_file, index=False)
            
            matched_count = len(final_df)
            total_matched += matched_count
            log_message(f"  Matched: {matched_count} / {year_total} ({matched_count/year_total:.1%})", log_file)

        except Exception as e:
            log_message(f"ERROR processing {year}: {e}", log_file)
            continue

    # 4. Save Unmatched Audit
    if all_unmatched:
        audit_df = pd.concat(all_unmatched, ignore_index=True)
        audit_file = output_dir / 'unmatched_calls_audit.csv'
        audit_df.to_csv(audit_file, index=False)
        log_message(f"Saved {len(audit_df)} unmatched calls to audit file.", log_file)
    else:
        log_message("No unmatched calls found.", log_file)

    # Summary
    log_message("-" * 30, log_file)
    log_message(f"Total Calls Processed: {total_calls}", log_file)
    log_message(f"Total Matched: {total_matched}", log_file)
    log_message(f"Total Unmatched: {total_calls - total_matched}", log_file)
    if total_calls > 0:
        log_message(f"Overall Match Rate: {total_matched/total_calls:.1%}", log_file)

    # Update 'latest' symlink
    latest_output_dir = root_dir / config['paths']['outputs'] / output_subdir / 'latest'
    latest_output_dir.mkdir(parents=True, exist_ok=True)
    import shutil
    for item in output_dir.glob('*'):
        if item.is_file():
            shutil.copy2(item, latest_output_dir / item.name)
    log_message(f"Updated 'latest' output directory.", log_file)

if __name__ == "__main__":
    link_calls_to_ceo_monthly()
