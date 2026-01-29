#!/usr/bin/env python3
"""
==============================================================================
STEP 2.11: Replication Reports & Comparison
==============================================================================
ID: 2.11_Replication_Reports
Description: Generates summary statistics, time-series data, and word frequency
             analysis to replicate findings from the reference paper.
             Comparisons include:
             - Sample selection & CEO filtering (Quotes 1 & 2)
             - Word counts & Uncertainty % (Quotes 3 & 4)
             - Zipf's Law / Top Words (Figure 1 / Quote 4)
             - Time Series & Dispersion (Figure 2 / Quote 5)
             - Correlations & Table 1 Stats (Quote 6)

Inputs:
    - 4_Outputs/2.3_TokenizeAndCount/latest/*.parquet (Token metrics, Top 5 words)
    - 4_Outputs/2.5b_LinkCallsToCeo/latest/*.parquet (Pre-filter CEO links)
    - 4_Outputs/2.8_EstimateCeoClarity/latest/calls_with_clarity_*.parquet (Final Panel)
Outputs:
    - 4_Outputs/2.11_Replication_Reports/TIMESTAMP/replication_results.json
    - 4_Outputs/2.11_Replication_Reports/TIMESTAMP/time_series_data.csv
    - 4_Outputs/2.11_Replication_Reports/TIMESTAMP/zipf_law_data.csv
    - 4_Outputs/2.11_Replication_Reports/TIMESTAMP/table_1_replication.csv
    - 4_Outputs/2.11_Replication_Reports/latest/ (symlink)
==============================================================================
"""

import sys
import os
import json
import pandas as pd
import numpy as np
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter
import warnings

# ==============================================================================
# Setup & Logging
# ==============================================================================

class DualWriter:
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')
        self._closed = False
    def write(self, message):
        self.terminal.write(message)
        if not self._closed:
            self.log.write(message)
            self.log.flush()
    def flush(self):
        self.terminal.flush()
        if not self._closed:
            self.log.flush()
    def close(self):
        if not self._closed:
            self.log.close()
            self._closed = True

def print_dual(msg):
    print(msg, flush=True)

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    root = Path(__file__).parent.parent
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # Base output path
    output_base = root / config['paths']['outputs'] / "2.11_Replication_Reports"
    output_dir = output_base / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Logs
    log_base = root / config['paths']['logs'] / "2.11_Replication_Reports"
    log_base.mkdir(parents=True, exist_ok=True)
    log_file = log_base / f"{timestamp}.log"
    
    # Input paths (using 'latest' symlinks)
    inputs = {
        'step_2_3': root / '4_Outputs' / '2.3_TokenizeAndCount' / 'latest',
        'step_2_5b': root / '4_Outputs' / '2.5b_LinkCallsToCeo' / 'latest',
        'step_2_8': root / '4_Outputs' / '2.8_EstimateCeoClarity' / 'latest'
    }
    
    return {
        'root': root,
        'output_dir': output_dir,
        'latest_dir': output_base / "latest",
        'log_file': log_file,
        'inputs': inputs
    }, timestamp

# ==============================================================================
# 1. Zipf's Law & Word Counts (Quotes 3 & 4)
# ==============================================================================

def analyze_tokens_and_zipf(paths, start_year, end_year):
    print_dual("\n" + "="*60)
    print_dual("Part 1: Analyzing Word Counts & Zipf's Law")
    print_dual("="*60)
    
    # Initialize aggregators
    stats = {
        'entire_call': {'tokens': [], 'unc_pct': []},
        'manager_pres': {'tokens': [], 'unc_pct': []},
        'manager_qa': {'tokens': [], 'unc_pct': []},
        'analyst_qa': {'tokens': [], 'unc_pct': []}
    }
    
    # Global word counter for Zipf's Law (Uncertainty words)
    # We will aggregate the 'top5_uncertainty' counts from each file
    global_unc_counts = Counter()
    
    # We need to process both 'manager_pres' and 'manager_qa' for Zipf's law as per paper
    zipf_datasets = ['manager_pres', 'manager_qa']
    
    for dataset in stats.keys():
        print_dual(f"  Processing {dataset}...")
        for year in range(start_year, end_year + 1):
            file_path = paths['inputs']['step_2_3'] / f"{dataset}_call_{year}.parquet"
            if not file_path.exists():
                continue
                
            df = pd.read_parquet(file_path)
            
            # Aggregate stats
            stats[dataset]['tokens'].extend(df['total_word_tokens'].tolist())
            stats[dataset]['unc_pct'].extend(df['unc_pct'].tolist())
            
            # Zipf's Law Aggregation (only for target datasets)
            if dataset in zipf_datasets and 'top5_uncertainty' in df.columns:
                # We need to parse the JSON if it's stored as string, or handle struct
                # The C++ pipeline saves it as a JSON string
                
                # Sample check first row
                first_val = df['top5_uncertainty'].iloc[0]
                is_string = isinstance(first_val, str)
                
                for _, row in df.iterrows():
                    val = row['top5_uncertainty']
                    try:
                        top5 = json.loads(val) if is_string else val
                        if not top5: continue
                        
                        for item in top5:
                            # Item is dict {'token': '...', 'count': ...}
                            word = item['token'].lower()
                            count = item['count']
                            global_unc_counts[word] += count
                    except:
                        continue
                        
    # Compute Summary Stats
    results = {}
    for dataset, data in stats.items():
        results[dataset] = {
            'avg_tokens': np.mean(data['tokens']) if data['tokens'] else 0,
            'avg_unc_pct': np.mean(data['unc_pct']) if data['unc_pct'] else 0,
            'n_obs': len(data['tokens'])
        }
        print_dual(f"    {dataset}: Avg Tokens={results[dataset]['avg_tokens']:.0f}, Avg Unc%={results[dataset]['avg_unc_pct']:.2f}%")

    # Zipf's Law Output
    print_dual("\n  Top 25 Uncertainty Words (Global):")
    top_25 = global_unc_counts.most_common(25)
    zipf_data = []
    total_hits = sum(global_unc_counts.values())
    
    current_cumulative = 0
    for rank, (word, count) in enumerate(top_25, 1):
        share = count / total_hits if total_hits > 0 else 0
        current_cumulative += share
        zipf_data.append({
            'rank': rank,
            'word': word,
            'count': count,
            'share': share,
            'cumulative_share': current_cumulative
        })
        print_dual(f"    {rank}. {word}: {count:,} ({share:.1%}) - Cum: {current_cumulative:.1%}")
        
    return results, zipf_data

# ==============================================================================
# 2. Sample Selection & Filtering (Quotes 1 & 2)
# ==============================================================================

def analyze_sample_filtering(paths, start_year, end_year):
    print_dual("\n" + "="*60)
    print_dual("Part 2: Sample Selection & CEO Filtering")
    print_dual("="*60)
    
    # 1. Total Calls (Proxy: Step 2.5b outputs)
    pre_filter_data = []
    for year in range(start_year, end_year + 1):
        f = paths['inputs']['step_2_5b'] / f"f1d_enriched_ceo_{year}.parquet"
        if f.exists():
            pre_filter_data.append(pd.read_parquet(f))
            
    if not pre_filter_data:
        print_dual("  ERROR: No Step 2.5b data found")
        return {}
        
    df_pre = pd.concat(pre_filter_data, ignore_index=True)
    
    # Metrics
    total_calls_linked = len(df_pre)
    total_ceos_linked = df_pre['ceo_id'].nunique()
    calls_with_ceo = df_pre[df_pre['ceo_id'].notna()]
    ceo_presence_rate = len(calls_with_ceo) / total_calls_linked if total_calls_linked else 0
    
    # Apply 5-call filter logic manually to verify
    ceo_counts = calls_with_ceo['ceo_id'].value_counts()
    valid_ceos = ceo_counts[ceo_counts >= 5].index
    
    dropped_ceos = total_ceos_linked - len(valid_ceos)
    post_filter_calls = calls_with_ceo[calls_with_ceo['ceo_id'].isin(valid_ceos)]
    
    results = {
        'total_calls_linked': total_calls_linked,
        'ceo_presence_rate': ceo_presence_rate,
        'total_individual_ceos': total_ceos_linked,
        'ceos_with_5_plus_calls': len(valid_ceos),
        'dropped_ceos': dropped_ceos,
        'calls_post_filter': len(post_filter_calls)
    }
    
    print_dual(f"  Total Calls Linked: {total_calls_linked:,}")
    print_dual(f"  CEO Presence Rate: {ceo_presence_rate:.2%}")
    print_dual(f"  Total Unique CEOs: {total_ceos_linked:,}")
    print_dual(f"  CEOs Left (>5 calls): {len(valid_ceos):,} (Dropped {dropped_ceos:,})")
    print_dual(f"  Calls Left: {len(post_filter_calls):,}")
    
    return results

# ==============================================================================
# 3. Time Series & Correlation (Quote 5 & 6)
# ==============================================================================

def analyze_time_series_and_correlation(paths, start_year, end_year):
    print_dual("\n" + "="*60)
    print_dual("Part 3: Time Series, Dispersion & Correlation")
    print_dual("="*60)
    
    # Load Final Panel (Step 2.8)
    final_data = []
    for year in range(start_year, end_year + 1):
        f = paths['inputs']['step_2_8'] / f"calls_with_clarity_{year}.parquet"
        if f.exists():
            final_data.append(pd.read_parquet(f))
            
    if not final_data:
        print_dual("  ERROR: No Step 2.8 data found")
        return {}, [], pd.DataFrame()
        
    df = pd.concat(final_data, ignore_index=True)
    
    # Keep our pipeline variable names (no rename)
    # Reference mapping to paper notation:
    #   MaPresUnc_pct -> UncPreCEO (Manager Presentation Uncertainty)
    #   MaQaUnc_pct -> UncAnsCEO (Manager Q&A Uncertainty)
    #   AnaQaUnc_pct -> UncQue (Analyst Q&A Uncertainty)
    #   EntireCallNeg_pct -> NegCall (Entire Call Negativity)
    
    # Ensure variables exist
    if 'MaPresUnc_pct' not in df.columns or 'MaQaUnc_pct' not in df.columns:
        print_dual("  ERROR: Missing MaPresUnc_pct or MaQaUnc_pct in final panel")
        vars_found = [c for c in df.columns if 'Unc' in c or 'Ma' in c]
        print_dual(f"  Found potential vars: {vars_found}")
        return {}, [], pd.DataFrame()
        
    # --- Correlation ---
    # Paper reports: correlation(UncPreCEO, UncAnsCEO) = 0.22
    # Our equivalent: correlation(MaPresUnc_pct, MaQaUnc_pct)
    corr = df[['MaPresUnc_pct', 'MaQaUnc_pct']].corr().iloc[0, 1]
    print_dual(f"  Correlation (MaPresUnc_pct, MaQaUnc_pct): {corr:.4f}")
    print_dual(f"    [Paper equivalent: UncPreCEO, UncAnsCEO = 0.22]")
    
    # --- Time Series (Quarterly) ---
    # Create Quarter identifier
    df['date'] = pd.to_datetime(df['start_date'])
    df['q_date'] = df['date'].dt.to_period('Q')
    
    ts_stats = []
    
    # Group by Quarter
    grouped = df.groupby('q_date')
    
    for q, group in grouped:
        stats = {
            'quarter': str(q),
            'n_obs': len(group),
            
            # MaPresUnc_pct (Paper: UncPreCEO)
            'MaPresUnc_mean': group['MaPresUnc_pct'].mean(),
            'MaPresUnc_p25': group['MaPresUnc_pct'].quantile(0.25),
            'MaPresUnc_p75': group['MaPresUnc_pct'].quantile(0.75),
            
            # MaQaUnc_pct (Paper: UncAnsCEO)
            'MaQaUnc_mean': group['MaQaUnc_pct'].mean(),
            'MaQaUnc_p25': group['MaQaUnc_pct'].quantile(0.25),
            'MaQaUnc_p75': group['MaQaUnc_pct'].quantile(0.75),
        }
        ts_stats.append(stats)
        
    ts_df = pd.DataFrame(ts_stats)
    print_dual(f"  Generated Time Series for {len(ts_df)} quarters")
    
    # --- Table 1 Stats ---
    # Using our pipeline names
    target_vars = [
        # Speech (our names -> paper names)
        'MaPresUnc_pct',  # -> UncPreCEO
        'MaQaUnc_pct',    # -> UncAnsCEO 
        'AnaQaUnc_pct',   # -> UncQue
        'EntireCallNeg_pct',  # -> NegCall
        # Financial
        'StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec', 'log_assets', 'tobins_q', 'roa',
        # CEO
        'ClarityCEO' 
    ]
    
    # Check what's actually in columns
    available_vars = [v for v in target_vars if v in df.columns]
    
    table_1 = df[available_vars].describe().T[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    print_dual("\n  Table 1 Replication (Partial):")
    print_dual(table_1.to_string())
    
    return {'correlation': corr}, ts_stats, table_1

# ==============================================================================
# Main
# ==============================================================================

def main():
    config = load_config()
    paths, timestamp = setup_paths(config)
    
    # Setup Logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    start_year = config['data']['year_start']
    end_year = config['data']['year_end']
    
    try:
        # Part 1: Zipf
        zipf_stats, zipf_data = analyze_tokens_and_zipf(paths, start_year, end_year)
        
        # Part 2: Sample
        sample_stats = analyze_sample_filtering(paths, start_year, end_year)
        
        # Part 3: Time Series & Table 1
        ts_metrics, ts_data, table_1_df = analyze_time_series_and_correlation(paths, start_year, end_year)
        
        # Combine JSON Results
        final_results = {
            'meta': {
                'timestamp': timestamp,
                'year_range': f"{start_year}-{end_year}"
            },
            'word_counts': zipf_stats,
            'sample_filtering': sample_stats,
            'correlations': ts_metrics
        }
        
        # Save Outputs
        
        # 1. JSON
        json_path = paths['output_dir'] / "replication_results.json"
        with open(json_path, 'w') as f:
            json.dump(final_results, f, indent=2)
            
        # 2. Time Series CSV
        pd.DataFrame(ts_data).to_csv(paths['output_dir'] / "time_series_data.csv", index=False)
        
        # 3. Zipf CSV
        pd.DataFrame(zipf_data).to_csv(paths['output_dir'] / "zipf_law_data.csv", index=False)
        
        # 4. Table 1 CSV
        table_1_df.to_csv(paths['output_dir'] / "table_1_replication.csv")
        
        print_dual("\n" + "="*60)
        print_dual("Outputs Saved:")
        print_dual(f"- {json_path.name}")
        print_dual(f"- time_series_data.csv")
        print_dual(f"- zipf_law_data.csv")
        print_dual(f"- table_1_replication.csv")
        
        # Update latest
        if paths['latest_dir'].exists():
            if paths['latest_dir'].is_symlink():
                paths['latest_dir'].unlink()
            else:
                shutil.rmtree(paths['latest_dir'])
        try:
            paths['latest_dir'].symlink_to(paths['output_dir'], target_is_directory=True)
            print_dual(f"  Updated latest symlink -> {paths['output_dir'].name}")
        except:
            shutil.copytree(paths['output_dir'], paths['latest_dir'])
            print_dual(f"  Created latest copy")
            
    except Exception as e:
        print_dual(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        dual_writer.close()

if __name__ == "__main__":
    main()
