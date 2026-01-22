#!/usr/bin/env python3
"""
==============================================================================
STEP 2.7: Build Financial Controls
==============================================================================
ID: 2.7_BuildFinancialControls
Description: Constructs 4 financial control variables for CEO clarity regression:
             1. SurpDec - Earnings surprise decile (-5 to +5)
             2. EPS_Growth - Year-over-year EPS growth (%)
             3. StockRet - Stock return from previous call to current call (%)
             4. MarketRet - Value-weighted market return over same period (%)
Inputs:
    - config/project.yaml
    - 4_Outputs/2.5c_FilterCallsAndCeos/latest/f1d_enriched_ceo_filtered_YYYY.parquet (17 files)
    - 1_Inputs/CRSP_DSF/CRSP_DSF_YYYY_QQ.parquet (quarterly stock data)
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet (Compustat)
    - 1_Inputs/tr_ibes/tr_ibes.parquet (IBES forecasts)
Outputs:
    - 4_Outputs/2.7_BuildFinancialControls/TIMESTAMP/calls_with_controls_YYYY.parquet
    - 4_Outputs/2.7_BuildFinancialControls/TIMESTAMP/report_step_07.md
    - 4_Outputs/2.7_BuildFinancialControls/latest/ (symlink)
    - 3_Logs/2.7_BuildFinancialControls/TIMESTAMP.log
Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yaml
import shutil
import hashlib
from collections import defaultdict

import importlib.util

# Import vectorized return computation (dynamic import for file starting with number)
module_name = "2.7_ComputeReturnsVectorized"
file_path = Path(__file__).resolve().parent / f"{module_name}.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
vectorized_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = vectorized_module
spec.loader.exec_module(vectorized_module)

compute_stock_returns_vectorized = vectorized_module.compute_stock_returns_vectorized

# ==============================================================================
# Dual-write logging utility
# ==============================================================================

class DualWriter:
    """Writes to both stdout and log file verbatim"""
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def print_dual(msg):
    """Print to both terminal and log"""
    print(msg, flush=True)

# ==============================================================================
# Configuration and setup
# ==============================================================================

def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent

    paths = {
        'root': root,
        'ceo_data_dir': root / '4_Outputs' / '2.5c_FilterCallsAndCeos' / 'latest',
        'crsp_dir': root / '1_Inputs' / 'CRSP_DSF',
        'compustat_file': root / '1_Inputs' / 'comp_na_daily_all' / 'comp_na_daily_all.parquet',
        'ibes_file': root / '1_Inputs' / 'tr_ibes' / 'tr_ibes.parquet',
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2.7_BuildFinancialControls"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "2.7_BuildFinancialControls"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# ==============================================================================
# Data loading
# ==============================================================================

def load_ceo_call_data(ceo_data_dir, year_start, year_end):
    """Load and concatenate all years of CEO-linked call data"""
    print_dual("\n" + "="*60)
    print_dual("Loading CEO-linked call data")
    print_dual("="*60)

    all_data = []
    for year in range(year_start, year_end + 1):
        file_path = ceo_data_dir / f"f1d_enriched_ceo_filtered_{year}.parquet"
        if not file_path.exists():
            print_dual(f"  WARNING: Missing {file_path.name}, skipping year {year}")
            continue

        df = pd.read_parquet(file_path)
        print_dual(f"  Loaded {year}: {len(df):,} calls")
        all_data.append(df)

    if not all_data:
        raise FileNotFoundError("No CEO-linked call data found")

    combined = pd.concat(all_data, ignore_index=True)

    # FIX: Normalize gvkey to match Compustat format (6-digit zero-padded string)
    combined['gvkey'] = combined['gvkey'].astype(str).str.zfill(6)

    print_dual(f"\nTotal calls loaded: {len(combined):,}")
    print_dual(f"Date range: {combined['start_date'].min()} to {combined['start_date'].max()}")
    print_dual(f"Unique firms (gvkey): {combined['gvkey'].nunique():,}")
    print_dual(f"Unique CEOs: {combined['ceo_id'].nunique():,}")

    return combined

def compute_previous_call_date(df):
    """Compute prev_call_date for each call (lag within gvkey)"""
    print_dual("\nComputing previous call dates...")

    # Ensure start_date is datetime
    df['start_date'] = pd.to_datetime(df['start_date'])

    # Sort by gvkey and start_date
    df = df.sort_values(['gvkey', 'start_date']).reset_index(drop=True)

    # Compute lag within gvkey
    df['prev_call_date'] = df.groupby('gvkey')['start_date'].shift(1)

    # Compute days since previous call
    df['days_since_prev_call'] = (df['start_date'] - df['prev_call_date']).dt.days

    n_with_prev = df['prev_call_date'].notna().sum()
    print_dual(f"  Calls with previous call date: {n_with_prev:,} / {len(df):,} ({n_with_prev/len(df)*100:.1f}%)")

    return df

# ==============================================================================
# Stock returns (StockRet, MarketRet)
# ==============================================================================

def load_crsp_data(crsp_dir, year_start, year_end):
    """Load CRSP daily stock file (DSF) for return calculations"""
    print_dual("\n" + "="*60)
    print_dual("Loading CRSP daily stock data")
    print_dual("="*60)

    all_crsp = []
    for year in range(year_start, year_end + 1):
        for quarter in range(1, 5):
            file_path = crsp_dir / f"CRSP_DSF_{year}_Q{quarter}.parquet"
            if not file_path.exists():
                print_dual(f"  WARNING: Missing {file_path.name}")
                continue

            df = pd.read_parquet(file_path)
            all_crsp.append(df)

    if not all_crsp:
        raise FileNotFoundError("No CRSP data found")

    crsp = pd.concat(all_crsp, ignore_index=True)
    print_dual(f"  Loaded {len(crsp):,} daily observations")

    # Ensure date is datetime
    if 'date' in crsp.columns:
        crsp['date'] = pd.to_datetime(crsp['date'])
    elif 'DATE' in crsp.columns:
        crsp.rename(columns={'DATE': 'date'}, inplace=True)
        crsp['date'] = pd.to_datetime(crsp['date'])

    # Ensure PERMNO column exists
    if 'PERMNO' in crsp.columns:
        crsp.rename(columns={'PERMNO': 'permno'}, inplace=True)

    # Ensure return column exists (RET or ret)
    if 'RET' in crsp.columns:
        crsp.rename(columns={'RET': 'ret'}, inplace=True)

    # Keep only necessary columns
    required_cols = ['permno', 'date', 'ret', 'vwretd']
    available_cols = [c for c in required_cols if c in crsp.columns]
    crsp = crsp[available_cols]

    # Convert returns to numeric (handle 'C' codes, etc.)
    if 'ret' in crsp.columns:
        crsp['ret'] = pd.to_numeric(crsp['ret'], errors='coerce')
    if 'vwretd' in crsp.columns:
        crsp['vwretd'] = pd.to_numeric(crsp['vwretd'], errors='coerce')

    print_dual(f"  Date range: {crsp['date'].min()} to {crsp['date'].max()}")
    print_dual(f"  Unique stocks (PERMNO): {crsp['permno'].nunique():,}")

    return crsp

def get_trading_days(crsp, start_date, end_date):
    """Get list of trading days between start and end date from CRSP"""
    mask = (crsp['date'] >= start_date) & (crsp['date'] <= end_date)
    trading_days = sorted(crsp[mask]['date'].unique())
    return trading_days

def compute_stock_returns_OLD_SLOW(df, crsp, config):
    """Compute StockRet and MarketRet for each call (OLD SLOW VERSION - NOT USED)"""
    print_dual("\n" + "="*60)
    print_dual("Computing stock returns")
    print_dual("="*60)

    days_after_prev = config['step_07']['return_windows']['days_after_prev_call']
    days_before_curr = config['step_07']['return_windows']['days_before_current_call']
    min_trading_days = config['step_07']['return_windows']['min_trading_days']

    print_dual(f"  Return window: {days_after_prev} days after previous call -> {days_before_curr} days before current call")
    print_dual(f"  Minimum trading days required: {min_trading_days}")

    # Initialize columns
    df['StockRet'] = np.nan
    df['MarketRet'] = np.nan
    df['return_window_days'] = np.nan

    # Filter to calls with both LPERMNO and prev_call_date
    # Also filter out empty string LPERMNOs (though LPERMNO should be float/int from CCM)
    valid_mask = (
        df['LPERMNO'].notna() &
        df['prev_call_date'].notna()
    )
    valid_calls = df[valid_mask].copy()

    print_dual(f"\n  Processing {len(valid_calls):,} calls with PERMNO and previous call date...")

    # Group CRSP by PERMNO for faster lookups
    crsp_grouped = crsp.groupby('permno')

    results = []
    for idx, row in valid_calls.iterrows():
        try:
            permno = int(float(row['LPERMNO']))
        except (ValueError, TypeError):
            results.append({'idx': idx, 'StockRet': np.nan, 'MarketRet': np.nan, 'return_window_days': 0})
            continue
        prev_date = row['prev_call_date']
        curr_date = row['start_date']

        # Define window
        window_start = prev_date + timedelta(days=days_after_prev)
        window_end = curr_date - timedelta(days=days_before_curr)

        if window_end <= window_start:
            # Invalid window
            results.append({'idx': idx, 'StockRet': np.nan, 'MarketRet': np.nan, 'return_window_days': 0})
            continue

        # Get firm's CRSP data
        if permno not in crsp_grouped.groups:
            results.append({'idx': idx, 'StockRet': np.nan, 'MarketRet': np.nan, 'return_window_days': 0})
            continue

        firm_crsp = crsp_grouped.get_group(permno)
        firm_crsp = firm_crsp[(firm_crsp['date'] >= window_start) & (firm_crsp['date'] <= window_end)].copy()

        if len(firm_crsp) < min_trading_days:
            results.append({'idx': idx, 'StockRet': np.nan, 'MarketRet': np.nan, 'return_window_days': len(firm_crsp)})
            continue

        # Compute cumulative return (compound)
        # Cumulative return = Π(1 + r_t) - 1
        firm_crsp = firm_crsp[firm_crsp['ret'].notna()]
        if len(firm_crsp) < min_trading_days:
            results.append({'idx': idx, 'StockRet': np.nan, 'MarketRet': np.nan, 'return_window_days': len(firm_crsp)})
            continue

        stock_ret = ((1 + firm_crsp['ret']).product() - 1) * 100  # Convert to %

        # Compute market return over same dates
        market_data = crsp[(crsp['date'] >= window_start) & (crsp['date'] <= window_end)][['date', 'vwretd']].drop_duplicates('date')
        market_data = market_data[market_data['vwretd'].notna()]

        if len(market_data) >= min_trading_days:
            market_ret = ((1 + market_data['vwretd']).product() - 1) * 100  # Convert to %
        else:
            market_ret = np.nan

        results.append({
            'idx': idx,
            'StockRet': stock_ret,
            'MarketRet': market_ret,
            'return_window_days': len(firm_crsp)
        })

        if len(results) % 1000 == 0:
            print_dual(f"    Processed {len(results):,} / {len(valid_calls):,} calls...")

    # Merge results back
    results_df = pd.DataFrame(results)
    df.loc[results_df['idx'], 'StockRet'] = results_df['StockRet'].values
    df.loc[results_df['idx'], 'MarketRet'] = results_df['MarketRet'].values
    df.loc[results_df['idx'], 'return_window_days'] = results_df['return_window_days'].values

    n_stock_ret = df['StockRet'].notna().sum()
    n_market_ret = df['MarketRet'].notna().sum()
    print_dual(f"\n  StockRet computed: {n_stock_ret:,} / {len(df):,} ({n_stock_ret/len(df)*100:.1f}%)")
    print_dual(f"  MarketRet computed: {n_market_ret:,} / {len(df):,} ({n_market_ret/len(df)*100:.1f}%)")

    # Winsorize extreme values
    if n_stock_ret > 0:
        p1, p99 = df['StockRet'].quantile([0.01, 0.99])
        n_winsorized = ((df['StockRet'] < p1) | (df['StockRet'] > p99)).sum()
        df['StockRet'] = df['StockRet'].clip(lower=p1, upper=p99)
        print_dual(f"  Winsorized StockRet: {n_winsorized} observations at 1%/99% percentiles")

    return df

# ==============================================================================
# EPS Growth
# ==============================================================================

def compute_eps_growth(df, compustat_file, config):
    """Compute year-over-year EPS growth"""
    print_dual("\n" + "="*60)
    print_dual("Computing EPS growth")
    print_dual("="*60)

    lag_quarters = config['step_07']['eps_growth']['lag_quarters']
    winsorize_pct = config['step_07']['eps_growth']['winsorize_percentiles']

    # Check file exists and size
    if not compustat_file.exists():
        print_dual(f"  WARNING: Compustat file not found: {compustat_file}")
        print_dual("  Skipping EPS growth.")
        df['EPS'] = np.nan
        df['EPS_Growth'] = np.nan
        return df

    file_size_mb = compustat_file.stat().st_size / (1024 * 1024)
    print_dual(f"  Loading Compustat data from {compustat_file.name} ({file_size_mb:.1f} MB)...")
    print_dual(f"  This may take 1-3 minutes for large files...")

    comp = pd.read_parquet(compustat_file)
    print_dual(f"  Loaded! {len(comp):,} rows, {len(comp.columns)} columns")
    print_dual(f"  Columns: {list(comp.columns[:10])}{'...' if len(comp.columns) > 10 else ''}")

    # Identify EPS column (epspxq or similar)
    eps_col = None
    for col in ['epspxq', 'EPSPXQ', 'eps', 'EPS', 'epspiq', 'EPSPIQ']:
        if col in comp.columns:
            eps_col = col
            break

    if eps_col is None:
        print_dual(f"  WARNING: EPS column not found in Compustat.")
        print_dual(f"  Available columns: {list(comp.columns)}")
        print_dual("  Skipping EPS growth.")
        df['EPS'] = np.nan
        df['EPS_Growth'] = np.nan
        return df

    print_dual(f"  Using EPS column: {eps_col}")

    # Ensure gvkey and datadate exist
    print_dual(f"  Checking required columns (gvkey, datadate)...")
    if 'datadate' not in comp.columns and 'DATADATE' in comp.columns:
        comp.rename(columns={'DATADATE': 'datadate'}, inplace=True)
        print_dual(f"    Renamed DATADATE -> datadate")
    if 'gvkey' not in comp.columns and 'GVKEY' in comp.columns:
        comp.rename(columns={'GVKEY': 'gvkey'}, inplace=True)
        print_dual(f"    Renamed GVKEY -> gvkey")

    # Verify required columns exist
    if 'gvkey' not in comp.columns or 'datadate' not in comp.columns:
        print_dual(f"  ERROR: Missing required columns!")
        print_dual(f"    gvkey present: {'gvkey' in comp.columns}")
        print_dual(f"    datadate present: {'datadate' in comp.columns}")
        print_dual(f"  Skipping EPS growth.")
        df['EPS'] = np.nan
        df['EPS_Growth'] = np.nan
        return df

    print_dual(f"  Converting data types...")
    comp['datadate'] = pd.to_datetime(comp['datadate'])
    # FIX: Compustat gvkeys are 6-digit zero-padded strings (e.g., '020747')
    comp['gvkey'] = comp['gvkey'].astype(str).str.zfill(6)
    print_dual(f"    Date range: {comp['datadate'].min()} to {comp['datadate'].max()}")

    # Keep only necessary columns
    print_dual(f"  Filtering to necessary columns...")
    comp = comp[['gvkey', 'datadate', eps_col]].copy()
    comp.rename(columns={eps_col: 'eps'}, inplace=True)
    comp['eps'] = pd.to_numeric(comp['eps'], errors='coerce')

    print_dual(f"  Final Compustat data: {len(comp):,} quarterly observations")
    print_dual(f"    Unique firms (gvkey): {comp['gvkey'].nunique():,}")
    print_dual(f"    Non-null EPS: {comp['eps'].notna().sum():,} ({comp['eps'].notna().sum()/len(comp)*100:.1f}%)")

    # Sort by gvkey and datadate
    print_dual(f"  Sorting by gvkey and datadate...")
    comp = comp.sort_values(['gvkey', 'datadate']).reset_index(drop=True)

    # Compute lagged EPS (4 quarters back for YoY)
    print_dual(f"  Computing lagged EPS ({lag_quarters} quarters back)...")
    comp['eps_lag4'] = comp.groupby('gvkey')['eps'].shift(lag_quarters)
    print_dual(f"    Non-null lagged EPS: {comp['eps_lag4'].notna().sum():,}")

    # Merge with call data
    df['gvkey'] = df['gvkey'].astype(str)
    df['start_date'] = pd.to_datetime(df['start_date'])

    # For each call, find closest Compustat quarter end date (before or on call date)
    print_dual(f"\n  Matching calls to Compustat quarters...")
    print_dual(f"  Processing {len(df):,} calls (this may take 2-5 minutes)...")

    df['EPS'] = np.nan
    df['EPS_lag4'] = np.nan

    comp_grouped = comp.groupby('gvkey')
    print_dual(f"    Compustat has data for {len(comp_grouped):,} unique firms")

    matched = 0
    no_gvkey = 0
    no_quarter = 0

    for i, (idx, row) in enumerate(df.iterrows()):
        gvkey = row['gvkey']
        call_date = row['start_date']

        if gvkey not in comp_grouped.groups:
            no_gvkey += 1
            continue

        firm_comp = comp_grouped.get_group(gvkey)
        # Find most recent quarter end on or before call date
        mask = firm_comp['datadate'] <= call_date
        if mask.sum() == 0:
            no_quarter += 1
            continue

        most_recent = firm_comp[mask].iloc[-1]
        df.at[idx, 'EPS'] = most_recent['eps']
        df.at[idx, 'EPS_lag4'] = most_recent['eps_lag4']
        matched += 1

        if (i + 1) % 10000 == 0:
            pct = (i + 1) / len(df) * 100
            print_dual(f"    Progress: {i+1:,} / {len(df):,} ({pct:.1f}%) - Matched: {matched:,}")

    print_dual(f"  Matching complete:")
    print_dual(f"    Matched: {matched:,} / {len(df):,} ({matched/len(df)*100:.1f}%)")
    print_dual(f"    No gvkey in Compustat: {no_gvkey:,}")
    print_dual(f"    No quarter before call: {no_quarter:,}")

    # Compute EPS growth: (EPS_t - EPS_t-4) / |EPS_t-4| as FRACTION (not percentage)
    # Paper definition: "The fraction by which earnings in a quarter exceed earnings in the same quarter in the prior year"
    df['EPS_Growth'] = np.nan
    mask = df['EPS_lag4'].notna() & (df['EPS_lag4'] != 0)
    df.loc[mask, 'EPS_Growth'] = (df.loc[mask, 'EPS'] - df.loc[mask, 'EPS_lag4']) / df.loc[mask, 'EPS_lag4'].abs()

    n_growth = df['EPS_Growth'].notna().sum()
    print_dual(f"  EPS_Growth computed: {n_growth:,} / {len(df):,} ({n_growth/len(df)*100:.1f}%)")

    # Winsorize
    if n_growth > 0:
        p_low, p_high = winsorize_pct
        p_low_val, p_high_val = df['EPS_Growth'].quantile([p_low/100, p_high/100])
        n_winsorized = ((df['EPS_Growth'] < p_low_val) | (df['EPS_Growth'] > p_high_val)).sum()
        df['EPS_Growth'] = df['EPS_Growth'].clip(lower=p_low_val, upper=p_high_val)
        print_dual(f"  Winsorized EPS_Growth: {n_winsorized} observations at {p_low}%/{p_high}% percentiles")

    return df

# ==============================================================================
# Earnings Surprise (SurpDec)
# ==============================================================================

def compute_earnings_surprise(df, ibes_file, config):
    """Compute earnings surprise decile (SurpDec)"""
    print_dual("\n" + "="*60)
    print_dual("Computing earnings surprise")
    print_dual("="*60)

    # Check file exists
    if not ibes_file.exists():
        print_dual(f"  WARNING: IBES file not found: {ibes_file}")
        print_dual("  Skipping earnings surprise.")
        df['ActualEPS'] = np.nan
        df['ForecastEPS'] = np.nan
        df['SurpDec'] = 0
        df['SurpDecAbs'] = 0
        return df

    # Load CCM for IBES linking
    print_dual(f"  Loading CCM for LPERMNO linking...")
    ccm_file = Path(__file__).parent.parent / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSPCompustat_CCM.parquet'
    ccm = pd.read_parquet(ccm_file)

    # Create CUSIP8 -> LPERMNO mapping
    ccm['cusip8'] = ccm['cusip'].astype(str).str[:8]
    ccm['LPERMNO'] = pd.to_numeric(ccm['LPERMNO'], errors='coerce')
    ccm_cusip = ccm[['cusip8', 'LPERMNO']].drop_duplicates().dropna()

    # Create TICKER -> LPERMNO mapping
    ccm_ticker = ccm[['tic', 'LPERMNO']].drop_duplicates().dropna()
    ccm_ticker.columns = ['TICKER', 'LPERMNO']

    print_dual(f"    CCM CUSIP8->LPERMNO: {len(ccm_cusip):,} mappings")
    print_dual(f"    CCM TICKER->LPERMNO: {len(ccm_ticker):,} mappings")

    file_size_mb = ibes_file.stat().st_size / (1024 * 1024)
    print_dual(f"  Loading IBES data from {ibes_file.name} ({file_size_mb:.1f} MB)...")
    print_dual(f"  This may take 1-2 minutes...")

    ibes = pd.read_parquet(ibes_file)
    print_dual(f"  Loaded! {len(ibes):,} rows, {len(ibes.columns)} columns")

    # Filter to EPS, quarterly
    print_dual(f"  Filtering to EPS quarterly forecasts...")
    ibes = ibes[(ibes['MEASURE'] == 'EPS') & (ibes['FISCALP'] == 'QTR')].copy()
    print_dual(f"  After filter: {len(ibes):,} IBES quarterly EPS forecasts")

    # Ensure necessary columns exist
    required_cols = ['TICKER', 'CUSIP', 'FPEDATS', 'STATPERS', 'MEANEST', 'ACTUAL']
    missing_cols = [c for c in required_cols if c not in ibes.columns]
    if missing_cols:
        print_dual(f"  ERROR: Missing IBES columns: {missing_cols}")
        print_dual(f"  Available columns: {list(ibes.columns)}")
        df['ActualEPS'] = np.nan
        df['ForecastEPS'] = np.nan
        df['SurpDec'] = 0
        df['SurpDecAbs'] = 0
        return df

    # Link IBES to LPERMNO via CUSIP8 and TICKER (combined for max coverage)
    print_dual(f"  Linking IBES to LPERMNO via CCM...")
    ibes['cusip8'] = ibes['CUSIP'].astype(str).str[:8]
    ibes_linked_cusip = ibes.merge(ccm_cusip, on='cusip8', how='inner')
    ibes_linked_ticker = ibes.merge(ccm_ticker, on='TICKER', how='inner')
    ibes_linked = pd.concat([ibes_linked_cusip, ibes_linked_ticker]).drop_duplicates()

    print_dual(f"    Via CUSIP8: {len(ibes_linked_cusip):,} / {len(ibes):,} ({len(ibes_linked_cusip)/len(ibes)*100:.1f}%)")
    print_dual(f"    Via TICKER: {len(ibes_linked_ticker):,} / {len(ibes):,} ({len(ibes_linked_ticker)/len(ibes)*100:.1f}%)")
    print_dual(f"    Combined:   {len(ibes_linked):,} / {len(ibes):,} ({len(ibes_linked)/len(ibes)*100:.1f}%)")

    # Normalize data types
    ibes_linked['fpedats'] = pd.to_datetime(ibes_linked['FPEDATS'])
    ibes_linked['statpers'] = pd.to_datetime(ibes_linked['STATPERS'])
    ibes_linked['forecast'] = pd.to_numeric(ibes_linked['MEANEST'], errors='coerce')
    ibes_linked['actual'] = pd.to_numeric(ibes_linked['ACTUAL'], errors='coerce')

    ibes_linked = ibes_linked[['LPERMNO', 'fpedats', 'statpers', 'forecast', 'actual']].copy()
    print_dual(f"    Non-null forecasts: {ibes_linked['forecast'].notna().sum():,}")
    print_dual(f"    Non-null actuals: {ibes_linked['actual'].notna().sum():,}")

    # Sort by LPERMNO, fpedats, statpers
    print_dual(f"  Sorting by LPERMNO, fpedats, statpers...")
    ibes_linked = ibes_linked.sort_values(['LPERMNO', 'fpedats', 'statpers']).reset_index(drop=True)

    print_dual(f"\n  Matching calls to IBES forecasts via LPERMNO...")
    print_dual(f"  Processing {len(df):,} calls (may take 1-3 minutes)...")

    df['ActualEPS'] = np.nan
    df['ForecastEPS'] = np.nan

    ibes_grouped = ibes_linked.groupby('LPERMNO')
    print_dual(f"    IBES has data for {len(ibes_grouped):,} unique LPERMNOs")

    matched = 0
    no_lpermno = 0
    no_forecast = 0

    for i, (idx, row) in enumerate(df.iterrows()):
        lpermno = row['LPERMNO']
        call_date = row['start_date']

        # Skip if no LPERMNO
        if pd.isna(lpermno):
            no_lpermno += 1
            continue

        # Get IBES records for this LPERMNO
        if lpermno not in ibes_grouped.groups:
            no_lpermno += 1
            continue

        ibes_firm = ibes_grouped.get_group(lpermno)

        # Find fiscal quarter end within +/- 45 days of call date
        ibes_firm_near = ibes_firm[
            (ibes_firm['fpedats'] >= call_date - pd.Timedelta(days=45)) &
            (ibes_firm['fpedats'] <= call_date + pd.Timedelta(days=45))
        ]

        if len(ibes_firm_near) == 0:
            no_forecast += 1
            continue

        # Select forecast closest to (but before) call date
        mask = ibes_firm_near['statpers'] <= call_date
        if mask.sum() == 0:
            no_forecast += 1
            continue

        closest_forecast = ibes_firm_near[mask].iloc[-1]
        df.at[idx, 'ForecastEPS'] = closest_forecast['forecast']
        df.at[idx, 'ActualEPS'] = closest_forecast['actual']
        matched += 1

        if (i + 1) % 10000 == 0:
            pct = (i + 1) / len(df) * 100
            print_dual(f"    Progress: {i+1:,} / {len(df):,} ({pct:.1f}%) - Matched: {matched:,}")

    print_dual(f"  Matching complete:")
    print_dual(f"    Matched: {matched:,} / {len(df):,} ({matched/len(df)*100:.1f}%)")
    print_dual(f"    No LPERMNO in IBES: {no_lpermno:,}")
    print_dual(f"    No forecast within +/-45 days: {no_forecast:,}")

    # Compute surprise (need price to normalize)
    # For simplicity, compute surprise as (Actual - Forecast) without price normalization
    # Then rank into deciles
    df['surprise_raw'] = df['ActualEPS'] - df['ForecastEPS']

    # Create quarter-year for grouping
    df['call_quarter'] = pd.to_datetime(df['start_date']).dt.to_period('Q')

    # Rank into deciles using PAPER'S METHODOLOGY:
    # "SurpDec is obtained by grouping firms into five equally sized bins of positive surprise
    #  (numbered from 5 to 1, from largest positive to smallest positive surprise), then 0 for
    #  zero surprises, and then five equally sized bins of negative surprise from -1 (for the
    #  smallest negative surprises) through -5 (for the largest negative surprises)."
    print_dual("\n  Ranking surprises using paper's 11-point scale...")

    df['SurpDec'] = np.nan  # Default to NaN (unmatched)
    df['SurpDecAbs'] = np.nan

    for quarter, group in df.groupby('call_quarter'):
        valid_mask = group['surprise_raw'].notna()
        if valid_mask.sum() == 0:
            continue
        
        surprises = group.loc[valid_mask, 'surprise_raw']
        
        # Separate positive, zero, and negative surprises
        pos_mask = surprises > 0
        zero_mask = surprises == 0
        neg_mask = surprises < 0
        
        # Handle positives: 5 bins (5=largest positive, 1=smallest positive)
        if pos_mask.sum() >= 5:
            pos_surprises = surprises[pos_mask]
            # Rank descending (largest=1), then map to bins
            ranks = pos_surprises.rank(ascending=False, method='first')
            n_pos = len(pos_surprises)
            # Divide into 5 equal bins
            bins = pd.cut(ranks, bins=5, labels=[5, 4, 3, 2, 1])
            df.loc[pos_surprises.index, 'SurpDec'] = bins.astype(float)
        elif pos_mask.sum() > 0:
            # Not enough for 5 bins, assign proportionally
            pos_surprises = surprises[pos_mask]
            ranks = pos_surprises.rank(ascending=False, method='first', pct=True)
            df.loc[pos_surprises.index, 'SurpDec'] = (5 - (ranks * 4)).round().clip(1, 5)
        
        # Handle zeros: assign 0
        if zero_mask.sum() > 0:
            df.loc[surprises[zero_mask].index, 'SurpDec'] = 0
        
        # Handle negatives: 5 bins (-1=smallest negative/closest to 0, -5=largest negative/most negative)
        if neg_mask.sum() >= 5:
            neg_surprises = surprises[neg_mask]
            # Rank ascending (most negative=1, least negative=highest)
            ranks = neg_surprises.rank(ascending=True, method='first')
            n_neg = len(neg_surprises)
            # Divide into 5 equal bins: rank 1-20% -> -5, 81-100% -> -1
            bins = pd.cut(ranks, bins=5, labels=[-5, -4, -3, -2, -1])
            df.loc[neg_surprises.index, 'SurpDec'] = bins.astype(float)
        elif neg_mask.sum() > 0:
            # Not enough for 5 bins, assign proportionally
            neg_surprises = surprises[neg_mask]
            ranks = neg_surprises.rank(ascending=True, method='first', pct=True)
            df.loc[neg_surprises.index, 'SurpDec'] = (-5 + (ranks * 4)).round().clip(-5, -1)
    
    # Compute absolute value
    df['SurpDecAbs'] = df['SurpDec'].abs()
    
    n_surp = df['SurpDec'].notna().sum()
    print_dual(f"  SurpDec assigned: {n_surp:,} / {len(df):,} ({n_surp/len(df)*100:.1f}%)")
    print_dual(f"  SurpDec mean: {df['SurpDec'].mean():.2f}, median: {df['SurpDec'].median():.0f}")

    return df

# ==============================================================================
# Data validation
# ==============================================================================

def validate_data(df):
    """Validate constructed control variables"""
    print_dual("\n" + "="*60)
    print_dual("Data validation")
    print_dual("="*60)

    # Check for duplicates
    n_dup = df.duplicated(subset=['file_name']).sum()
    if n_dup > 0:
        print_dual(f"  WARNING: {n_dup} duplicate file_name entries found!")
    else:
        print_dual(f"  [OK] No duplicate file_name entries")

    # Missingness report
    print_dual("\n  Missingness rates:")
    control_vars = ['prev_call_date', 'StockRet', 'MarketRet', 'EPS', 'EPS_Growth', 'ActualEPS', 'ForecastEPS', 'SurpDec']
    for var in control_vars:
        if var in df.columns:
            n_missing = df[var].isna().sum()
            pct_missing = n_missing / len(df) * 100
            print_dual(f"    {var:20s}: {n_missing:8,} missing ({pct_missing:5.1f}%)")

    # Summary statistics
    print_dual("\n  Summary statistics:")
    numeric_vars = ['StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec']
    for var in numeric_vars:
        if var in df.columns and df[var].notna().sum() > 0:
            print_dual(f"    {var}:")
            print_dual(f"      Mean: {df[var].mean():10.2f}")
            print_dual(f"      Median: {df[var].median():10.2f}")
            print_dual(f"      Std: {df[var].std():10.2f}")
            print_dual(f"      Min: {df[var].min():10.2f}")
            print_dual(f"      Max: {df[var].max():10.2f}")

    return True

# ==============================================================================
# Save outputs
# ==============================================================================

def save_outputs(df, paths, year_start, year_end, config):
    """Save processed data by year"""
    print_dual("\n" + "="*60)
    print_dual("Saving outputs")
    print_dual("="*60)

    df['year'] = pd.to_datetime(df['start_date']).dt.year

    for year in range(year_start, year_end + 1):
        year_data = df[df['year'] == year].copy()
        if len(year_data) == 0:
            continue

        output_file = paths['output_dir'] / f"calls_with_controls_{year}.parquet"
        year_data.to_parquet(output_file, index=False, compression='snappy')

        file_size = output_file.stat().st_size / (1024**2)
        print_dual(f"  Saved {year}: {len(year_data):,} calls ({file_size:.1f} MB)")

    # Update latest symlink
    print_dual("\nUpdating latest symlink...")
    if paths['latest_dir'].exists():
        if paths['latest_dir'].is_symlink():
            paths['latest_dir'].unlink()
        else:
            shutil.rmtree(paths['latest_dir'])

    try:
        paths['latest_dir'].symlink_to(paths['output_dir'].name, target_is_directory=True)
        print_dual(f"  Created symlink: latest -> {paths['output_dir'].name}")
    except OSError:
        # Fallback to copy on Windows
        shutil.copytree(paths['output_dir'], paths['latest_dir'])
        print_dual(f"  Created copy: latest")

# ==============================================================================
# Generate report
# ==============================================================================

def generate_report(df, paths, config, duration):
    """Generate markdown report"""
    report_path = paths['output_dir'] / "report_step_07.md"

    report = []
    report.append("# STEP 2.7: Build Financial Controls - Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Process Version:** {config['project']['version']}\n")
    report.append(f"**Script:** 2.7_BuildFinancialControls.py\n")
    report.append("\n---\n")

    report.append("## Summary\n")
    report.append(f"Constructed 4 financial control variables for CEO clarity regression:\n")
    report.append(f"- **StockRet**: Stock return from previous call to current call\n")
    report.append(f"- **MarketRet**: Value-weighted market return over same period\n")
    report.append(f"- **EPS_Growth**: Year-over-year EPS growth (%)\n")
    report.append(f"- **SurpDec**: Earnings surprise decile (-5 to +5)\n")
    report.append("\n---\n")

    report.append("## Data Coverage\n")
    report.append(f"- **Total calls**: {len(df):,}\n")
    report.append(f"- **Date range**: {df['start_date'].min()} to {df['start_date'].max()}\n")
    report.append(f"- **Unique firms**: {df['gvkey'].nunique():,}\n")
    report.append(f"- **Unique CEOs**: {df['ceo_id'].nunique():,}\n")
    report.append("\n---\n")

    report.append("## Variable Missingness\n")
    control_vars = ['prev_call_date', 'StockRet', 'MarketRet', 'EPS', 'EPS_Growth', 'ActualEPS', 'ForecastEPS', 'SurpDec']
    report.append("| Variable | Missing | % Missing |\n")
    report.append("|----------|---------|----------|\n")
    for var in control_vars:
        if var in df.columns:
            n_missing = df[var].isna().sum()
            pct_missing = n_missing / len(df) * 100
            report.append(f"| {var} | {n_missing:,} | {pct_missing:.1f}% |\n")

    report.append("\n---\n")

    report.append("## Summary Statistics\n")
    numeric_vars = ['StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec']
    report.append("| Variable | Mean | Median | Std | Min | Max |\n")
    report.append("|----------|------|--------|-----|-----|-----|\n")
    for var in numeric_vars:
        if var in df.columns and df[var].notna().sum() > 0:
            report.append(f"| {var} | {df[var].mean():.2f} | {df[var].median():.2f} | {df[var].std():.2f} | {df[var].min():.2f} | {df[var].max():.2f} |\n")

    report.append("\n---\n")
    report.append(f"**Execution time:** {duration:.1f} seconds\n")
    report.append("\n**End of Report**\n")

    with open(report_path, 'w') as f:
        f.writelines(report)

    print_dual(f"\nReport saved: {report_path}")

# ==============================================================================
# Main execution
# ==============================================================================

def main():
    """Main execution"""
    start_time = datetime.now()

    # Load configuration
    config = load_config()
    paths, timestamp = setup_paths(config)

    year_start = config['data']['year_start']
    year_end = config['data']['year_end']

    # Set up dual-write logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer

    print_dual("="*80)
    print_dual("STEP 2.7: Build Financial Controls")
    print_dual("="*80)
    print_dual(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Config: {config['project']['name']} v{config['project']['version']}")
    print_dual(f"Year range: {year_start}-{year_end}")
    print_dual(f"Log file: {paths['log_file']}")
    print_dual("")

    # Step 1: Load CEO call data
    df = load_ceo_call_data(paths['ceo_data_dir'], year_start, year_end)

    # Step 2: Compute previous call date
    df = compute_previous_call_date(df)

    # Step 3: Load CRSP and compute stock returns
    crsp = load_crsp_data(paths['crsp_dir'], year_start, year_end)
    df = compute_stock_returns_vectorized(df, crsp, config, print_dual)

    # Step 4: Compute EPS growth
    df = compute_eps_growth(df, paths['compustat_file'], config)

    # Step 5: Compute earnings surprise
    df = compute_earnings_surprise(df, paths['ibes_file'], config)

    # Step 6: Validate data
    validate_data(df)

    # Step 7: Save outputs
    save_outputs(df, paths, year_start, year_end, config)

    # Step 8: Generate report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    generate_report(df, paths, config, duration)

    print_dual("\n" + "="*80)
    print_dual("STEP 2.7 COMPLETE")
    print_dual("="*80)
    print_dual(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Duration: {duration:.1f} seconds")
    print_dual(f"Output directory: {paths['output_dir']}")
    print_dual("="*80)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
