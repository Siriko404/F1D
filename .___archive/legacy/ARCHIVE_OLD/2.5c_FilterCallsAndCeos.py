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

def filter_calls_and_ceos():
    config = load_config()
    root_dir = Path(__file__).parent.parent

    # Configuration
    step_config = config['step_02_5c']
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']
    min_calls = step_config['min_calls_threshold']

    # Input/Output Paths
    input_base_dir = root_dir / config['paths']['outputs'] / '2.5b_LinkCallsToCeo' / 'latest'
    output_subdir = step_config['output_subdir']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = root_dir / config['paths']['outputs'] / output_subdir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    log_file = setup_logging(output_dir, output_subdir)
    log_message(f"Starting Step 2.5c: Filter Calls and CEOs", log_file)
    log_message(f"Filter 1 (Calls): event_type='1' (earnings calls only)", log_file)
    log_message(f"Filter 2 (CEOs): CEOs with >= {min_calls} calls (after call filter)", log_file)
    log_message(f"Input Directory: {input_base_dir}", log_file)
    log_message(f"Output Directory: {output_dir}", log_file)

    # Load Unified-info for event_type
    log_message("Loading Unified-info for event_type filter...", log_file)
    unified_path = root_dir / config['paths']['inputs'] / 'Unified-info.parquet'
    unified = pd.read_parquet(unified_path)
    unified_event = unified[['file_name', 'event_type']].drop_duplicates()
    log_message(f"Loaded {len(unified_event):,} unique file_name -> event_type mappings", log_file)

    # --- Pass 1: Count Calls per CEO (event_type='1' only) ---
    log_message("--- Pass 1: Counting Calls per CEO (event_type='1' only) ---", log_file)
    ceo_counts = {}
    total_calls_before_event_filter = 0
    total_calls_after_event_filter = 0

    for year in range(year_start, year_end + 1):
        input_file = input_base_dir / f"f1d_enriched_ceo_{year}.parquet"
        if not input_file.exists():
            log_message(f"Skipping {year}: Input file not found ({input_file})", log_file)
            continue

        try:
            df = pd.read_parquet(input_file)
            total_calls_before_event_filter += len(df)

            # FILTER 1: event_type='1' (earnings calls only)
            df = df.merge(unified_event, on='file_name', how='left')
            df_earnings = df[df['event_type'] == '1'].copy()
            total_calls_after_event_filter += len(df_earnings)

            # Count non-null CEO IDs (in earnings calls only)
            counts = df_earnings['ceo_id'].value_counts().to_dict()
            for ceo_id, count in counts.items():
                ceo_counts[ceo_id] = ceo_counts.get(ceo_id, 0) + count
        except Exception as e:
            log_message(f"Error reading {input_file}: {e}", log_file)

    log_message(f"Event Type Filter Results:", log_file)
    log_message(f"  Before filter (all events): {total_calls_before_event_filter:,} calls", log_file)
    log_message(f"  After filter (event_type='1'): {total_calls_after_event_filter:,} calls", log_file)
    log_message(f"  Removed: {total_calls_before_event_filter - total_calls_after_event_filter:,} non-earnings calls", log_file)

    log_message(f"Total Unique CEOs found: {len(ceo_counts)}", log_file)
    
    # Identify Valid CEOs
    valid_ceos = {ceo_id for ceo_id, count in ceo_counts.items() if count >= min_calls}
    dropped_ceos_count = len(ceo_counts) - len(valid_ceos)
    log_message(f"Valid CEOs (>= {min_calls} calls): {len(valid_ceos)}", log_file)
    log_message(f"Dropped CEOs (< {min_calls} calls): {dropped_ceos_count}", log_file)

    # --- Pass 2: Filter and Save ---
    log_message("--- Pass 2: Applying Filters and Saving ---", log_file)
    total_calls_kept = 0
    total_calls_dropped_event = 0
    total_calls_dropped_ceo = 0

    for year in range(year_start, year_end + 1):
        input_file = input_base_dir / f"f1d_enriched_ceo_{year}.parquet"
        if not input_file.exists():
            continue

        try:
            df = pd.read_parquet(input_file)
            original_count = len(df)

            # FILTER 1: event_type='1' (earnings calls only)
            df = df.merge(unified_event, on='file_name', how='left')
            df_earnings = df[df['event_type'] == '1'].copy()
            dropped_event = original_count - len(df_earnings)
            total_calls_dropped_event += dropped_event

            # FILTER 2: CEOs with >= min_calls
            mask = df_earnings['ceo_id'].isin(valid_ceos)
            kept_df = df_earnings[mask].copy()
            dropped_df = df_earnings[~mask].copy()

            dropped_ceo = len(dropped_df)
            total_calls_dropped_ceo += dropped_ceo
            
            # Save Kept
            output_file = output_dir / f"f1d_enriched_ceo_filtered_{year}.parquet"
            kept_df.to_parquet(output_file, index=False)
            
            # Save Dropped
            dropped_file = output_dir / f"f1d_dropped_ceo_calls_{year}.parquet"
            dropped_df.to_parquet(dropped_file, index=False)
            
            kept_count = len(kept_df)
            total_calls_kept += kept_count

            log_message(f"Processed {year}: Kept {kept_count}, Dropped {dropped_event} (event_type), {dropped_ceo} (CEO filter)", log_file)

        except Exception as e:
            log_message(f"Error processing {year}: {e}", log_file)

    # Summary
    log_message("-" * 60, log_file)
    log_message(f"FINAL SUMMARY:", log_file)
    log_message(f"  Total Calls Kept: {total_calls_kept:,}", log_file)
    log_message(f"  Dropped by event_type filter: {total_calls_dropped_event:,}", log_file)
    log_message(f"  Dropped by CEO filter: {total_calls_dropped_ceo:,}", log_file)
    log_message(f"  Total Dropped: {total_calls_dropped_event + total_calls_dropped_ceo:,}", log_file)
    total_processed = total_calls_kept + total_calls_dropped_event + total_calls_dropped_ceo
    if total_processed > 0:
        log_message(f"  Retention Rate: {total_calls_kept / total_processed:.1%}", log_file)

    # Update 'latest' symlink
    latest_output_dir = root_dir / config['paths']['outputs'] / output_subdir / 'latest'
    latest_output_dir.mkdir(parents=True, exist_ok=True)
    import shutil
    for item in output_dir.glob('*'):
        if item.is_file():
            shutil.copy2(item, latest_output_dir / item.name)
    log_message(f"Updated 'latest' output directory.", log_file)

if __name__ == "__main__":
    filter_calls_and_ceos()
