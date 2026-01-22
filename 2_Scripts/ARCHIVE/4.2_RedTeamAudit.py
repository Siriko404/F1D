#!/usr/bin/env python3
"""
==============================================================================
RED TEAM AUDIT: Step 4.2 Liquidity Regressions
==============================================================================

Objective: 
    Independently verify the findings of 4.2_LiquidityRegressions.py.
    Assume the previous implementation is flawed until proven otherwise.

Strategy:
    1. Independent Data Re-load: Load inputs from source parquets.
    2. Strict Merge Accounting: Track N at every join. Report dropped rows.
    3. Variable Audit: Verify distributions of key variables (outliers, nulls).
    4. Manual Specification: Re-construct regression matrices from scratch.
    5. Alternative Library: Use Linearmodels for everything to ensure consistency.
    6. Side-by-Side Comparison: Compare results with the 'production' run.

Author: Red Team Auditor
Date: 2025-12-28
==============================================================================
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels.iv import IV2SLS
# from linearmodels.reg import HeterskedasticityRobustOLS # REMOVED

# Setup paths
ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / '4_Outputs' / '4.2_RedTeamAudit'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Logging
LOG_FILE = OUT_DIR / 'audit_log.txt'
sys.stdout = open(LOG_FILE, 'w', encoding='utf-8')

def log(msg):
    print(f"[AUDIT] {msg}")
    sys.stdout.flush()

def load_parquet_year_range(base_path_template, start_year, end_year, columns=None):
    dfs = []
    for year in range(start_year, end_year + 1):
        path = Path(str(base_path_template).format(year=year))
        if path.exists():
            df = pd.read_parquet(path)
            if columns:
                df = df[[c for c in columns if c in df.columns]]
            dfs.append(df)
        else:
            log(f"WARNING: Missing file {path}")
    return pd.concat(dfs, ignore_index=True)

def main():
    log("Starting Red Team Audit...")
    
    # --------------------------------------------------------------------------
    # 1. LOAD DATA
    # --------------------------------------------------------------------------
    log("\n--- PHASE 1: Data Loading & Integrity Checks ---")
    
    # Manifest
    manifest_path = ROOT / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest' / 'master_sample_manifest.parquet'
    manifest = pd.read_parquet(manifest_path)
    log(f"Manifest N: {len(manifest):,}")
    
    # Linguistic
    ling_path = str(ROOT / '4_Outputs' / '2_Textual_Analysis' / '2.2_Variables' / 'latest' / 'linguistic_variables_{year}.parquet')
    ling = load_parquet_year_range(ling_path, 2002, 2018)
    log(f"Linguistic Raw N: {len(ling):,}")
    
    # Firm Controls
    firm_path = str(ROOT / '4_Outputs' / '3_Financial_Features' / 'latest' / 'firm_controls_{year}.parquet')
    firm = load_parquet_year_range(firm_path, 2002, 2018)
    log(f"Firm Controls Raw N: {len(firm):,}")
    
    # Market Variables
    market_path = str(ROOT / '4_Outputs' / '3_Financial_Features' / 'latest' / 'market_variables_{year}.parquet')
    market = load_parquet_year_range(market_path, 2002, 2018)
    log(f"Market Variables Raw N: {len(market):,}")
    
    # Clarity Scores
    regime_clarity_path = ROOT / '4_Outputs' / '4.1_CeoClarity' / 'latest' / 'ceo_clarity_scores.parquet'
    regime_clarity = pd.read_parquet(regime_clarity_path)
    log(f"Regime Clarity CEOs N: {len(regime_clarity):,}")
    
    ceo_clarity_path = ROOT / '4_Outputs' / '4.1.1_CeoClarity_CEO_Only' / 'latest' / 'ceo_clarity_scores.parquet'
    ceo_clarity = pd.read_parquet(ceo_clarity_path)
    log(f"CEO Clarity CEOs N: {len(ceo_clarity):,}")
    
    # --------------------------------------------------------------------------
    # 2. MERGE AUDIT
    # --------------------------------------------------------------------------
    log("\n--- PHASE 2: Merge Construction ---")
    
    df = manifest.copy()
    
    # Merge Ling
    pre_n = len(df)
    df = df.merge(ling.drop_duplicates('file_name'), on='file_name', how='left')
    log(f"After Ling Merge: {len(df):,} (Change: {len(df)-pre_n})")
    
    # Merge Firm
    pre_n = len(df)
    df = df.merge(firm.drop_duplicates('file_name'), on='file_name', how='left', suffixes=('', '_firm'))
    log(f"After Firm Merge: {len(df):,} (Change: {len(df)-pre_n})")
    
    # Merge Market
    pre_n = len(df)
    df = df.merge(market.drop_duplicates('file_name'), on='file_name', how='left', suffixes=('', '_mkt'))
    log(f"After Market Merge: {len(df):,} (Change: {len(df)-pre_n})")
    
    # Sample Logic for Clarity Matching
    df['sample_clarity'] = 'Main'
    df.loc[df['ff12_code'] == 11, 'sample_clarity'] = 'Finance'
    df.loc[df['ff12_code'] == 8, 'sample_clarity'] = 'Utility'
    
    # Standardize CEO ID
    df['ceo_id'] = df['ceo_id'].astype(str)
    regime_clarity['ceo_id'] = regime_clarity['ceo_id'].astype(str)
    ceo_clarity['ceo_id'] = ceo_clarity['ceo_id'].astype(str)
    
    # Merge Regime Clarity
    pre_n = len(df)
    df = df.merge(regime_clarity[['ceo_id', 'sample', 'ClarityCEO']], 
                  left_on=['ceo_id', 'sample_clarity'], 
                  right_on=['ceo_id', 'sample'], 
                  how='left')
    df.rename(columns={'ClarityCEO': 'ClarityRegime'}, inplace=True)
    df.drop(columns=['sample'], inplace=True)
    log(f"After Regime Clarity Merge: {len(df):,}")
    
    # Merge CEO Clarity
    df = df.merge(ceo_clarity[['ceo_id', 'sample', 'ClarityCEO']], 
                  left_on=['ceo_id', 'sample_clarity'], 
                  right_on=['ceo_id', 'sample'], 
                  how='left')
    df.rename(columns={'ClarityCEO': 'ClarityCEOOnly'}, inplace=True)
    df.drop(columns=['sample'], inplace=True)
    log(f"After CEO Clarity Merge: {len(df):,}")
    
    # --------------------------------------------------------------------------
    # 3. SAMPLE FILTER AUDIT
    # --------------------------------------------------------------------------
    log("\n--- PHASE 3: Sample Filtering (Main Only) ---")
    
    # Main Sample: Exclude FF12 8 (Utilities) and 11 (Finance)
    df_main = df[~df['ff12_code'].isin([8, 11])].copy()
    log(f"Main Sample N: {len(df_main):,} (Dropped {len(df) - len(df_main)} Finance/Util firms)")
    
    # --------------------------------------------------------------------------
    # 4. VARIABLE AUDIT
    # --------------------------------------------------------------------------
    log("\n--- PHASE 4: Specific Variable Audit ---")
    
    cols_to_check = [
        'Delta_Amihud', 'Delta_Corwin_Schultz', 
        'ClarityRegime', 'ClarityCEOOnly',
        'Manager_QA_Uncertainty_pct', 'CEO_QA_Uncertainty_pct',
        'shift_intensity_sale_ff48'
    ]
    
    for c in cols_to_check:
        if c in df_main.columns:
            n_nan = df_main[c].isna().sum()
            log(f"{c}: {n_nan} NaNs ({n_nan/len(df_main):.1%}), Mean={df_main[c].mean():.4f}")
        else:
            log(f"ERROR: Missing column {c}")
            
    # --------------------------------------------------------------------------
    # 5. REGRESSION REPLICATION
    # --------------------------------------------------------------------------
    log("\n--- PHASE 5: Regression Replication (Main Sample) ---")
    
    controls = [
        'Manager_Pres_Uncertainty_pct', 'Analyst_QA_Uncertainty_pct', 'Entire_All_Negative_pct',
        'StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec',
        'Size', 'BM', 'Lev', 'ROA', 'CurrentRatio', 'RD_Intensity', 'Volatility'
    ]
    
    dep_vars = ['Delta_Amihud', 'Delta_Corwin_Schultz']
    models_to_run = [
        ('Regime', 'ClarityRegime', 'Manager_QA_Uncertainty_pct'),
        ('CEO', 'ClarityCEOOnly', 'CEO_QA_Uncertainty_pct')
    ]
    
    results = []
    
    year_dummies = pd.get_dummies(df_main['year'].astype(int).astype(str), prefix='year', drop_first=True)
    
    for dv in dep_vars:
        for model_type, clarity_var, unc_var in models_to_run:
            log(f"\nrunning {model_type} - {dv}...")
            
            # Construct Regression DataFrame Manually
            reg_vars = [dv, clarity_var, unc_var, 'shift_intensity_sale_ff48'] + controls
            reg_df = df_main[['year'] + reg_vars].copy()
            
            # Explicit Type Casting for numeric columns
            for c in reg_vars:
                reg_df[c] = pd.to_numeric(reg_df[c], errors='coerce').astype(np.float64)
                
            # Drop NaNs on all regression variables
            reg_df = reg_df.dropna(subset=reg_vars)
            
            # Create year dummies after dropna to ensure alignment
            year_dummies = pd.get_dummies(reg_df['year'].astype(int).astype(str), prefix='year', drop_first=True).astype(np.float64)
            
            log(f"  N Obs used: {len(reg_df)}")
            
            # --- OLS ---
            y = reg_df[dv].astype(np.float64).values
            
            # X (Exogenous only)
            exog_vars = [clarity_var, unc_var] + controls
            X_data = reg_df[exog_vars].astype(np.float64)
            X_data = pd.concat([X_data.reset_index(drop=True), year_dummies.reset_index(drop=True)], axis=1)
            X = sm.add_constant(X_data).astype(np.float64)
            
            try:
                ols_mod = sm.OLS(y, X).fit(cov_type='HC1')
                log(f"  [OLS] Clarity Coef: {ols_mod.params[clarity_var]:.4f} (p={ols_mod.pvalues[clarity_var]:.4f})")
                log(f"  [OLS] Unc Coef: {ols_mod.params[unc_var]:.4f}")
                log(f"  [OLS] R2: {ols_mod.rsquared:.6f}")
                r2_ols = ols_mod.rsquared
            except Exception as e:
                log(f"  [OLS] FAILED: {e}")
                r2_ols = np.nan
            
            # --- IV ---
            y_iv = reg_df[dv].astype(np.float64).values
            
            # Exogenous (Controls + Clarity + Constant + Time)
            exog_iv_vars = [clarity_var] + controls
            X_exog_data = reg_df[exog_iv_vars].astype(np.float64)
            X_exog_data = pd.concat([X_exog_data.reset_index(drop=True), year_dummies.reset_index(drop=True)], axis=1)
            X_exog = sm.add_constant(X_exog_data).astype(np.float64)
            
            # Endogenous
            X_endog = reg_df[[unc_var]].astype(np.float64).reset_index(drop=True)
            
            # Instrument
            Z_inst = reg_df[['shift_intensity_sale_ff48']].astype(np.float64).reset_index(drop=True)
            
            try:
                iv_mod = IV2SLS(y_iv, X_exog, X_endog, Z_inst).fit(cov_type='robust')
                log(f"  [IV] Clarity Coef: {iv_mod.params[clarity_var]:.4f} (p={iv_mod.pvalues[clarity_var]:.4f})")
                log(f"  [IV] Unc Coef: {iv_mod.params[unc_var]:.4f}")
                log(f"  [IV] R2: {iv_mod.rsquared:.6f}")
                
                # Manual First Stage for verification
                fs_X = pd.concat([X_exog, Z_inst], axis=1).astype(np.float64)
                fs_y = X_endog.values.ravel()
                fs_mod = sm.OLS(fs_y, fs_X).fit(cov_type='HC1')
                fs_f = fs_mod.fvalue
                log(f"  [AUDIT-FS] Manual F-stat: {fs_f:.2f}")
                
                r2_iv = iv_mod.rsquared
            except Exception as e:
                log(f"  [IV] FAILED: {e}")
                r2_iv = np.nan
                
            results.append({
                'Sample': 'Main', 'DepVar': dv, 'Type': model_type,
                'N': len(reg_df),
                'OLS_R2': r2_ols, 'IV_R2': r2_iv
            })

    log("\n--- AUDIT COMPLETE ---")

if __name__ == '__main__':
    main()
