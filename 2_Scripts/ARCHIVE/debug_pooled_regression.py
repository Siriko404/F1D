
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path

def run_pooled_regression():
    print("Loading datasets...")
    # Fix path relative to script location (2_Scripts/4_Econometric)
    root_in = Path(__file__).resolve().parents[2] / '4_Outputs'
    manifest = pd.read_parquet(root_in / '1.0_BuildSampleManifest/latest/master_sample_manifest.parquet')
    
    all_data = []
    years = range(2002, 2019)
    for year in years:
        try:
            lv = pd.read_parquet(root_in / f'2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet')
            fc = pd.read_parquet(root_in / f'3_Financial_Features/latest/firm_controls_{year}.parquet')
            mv = pd.read_parquet(root_in / f'3_Financial_Features/latest/market_variables_{year}.parquet')
            
            # Drop conflicts
            lv_drop = [c for c in ['gvkey', 'year', 'start_date'] if c in lv.columns]
            lv = lv.drop(columns=lv_drop)
            
            year_files = set(lv['file_name'])
            mf_year = manifest[manifest['file_name'].isin(year_files)].copy()
            
            merged = mf_year.merge(lv, on='file_name', how='left')
            
            if len(fc) > 0:
                fc_cols = ['file_name'] + [c for c in ['StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec'] if c in fc.columns]
                merged = merged.merge(fc[fc_cols], on='file_name', how='left')
                
            if len(mv) > 0:
                mv_cols = ['file_name'] + [c for c in ['StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec'] if c in mv.columns]
                # Avoid duplicates if column in both
                mv_cols = [c for c in mv_cols if c not in merged.columns or c == 'file_name']
                if len(mv_cols) > 1:
                    merged = merged.merge(mv[mv_cols], on='file_name', how='left')
            
            merged['year'] = year
            all_data.append(merged)
        except Exception as e:
            print(f"Skipping {year}: {e}")

    df = pd.concat(all_data, ignore_index=True)
    print(f"Total rows: {len(df)}")
    
    # Prepare Regression Data
    # 1. Filter CEO ID
    df = df[df['ceo_id'].notna()].copy()
    
    # 2. Select Vars
    dep_var = 'Manager_QA_Uncertainty_pct'
    controls = [
        'Manager_Pres_Uncertainty_pct',
        'Analyst_QA_Uncertainty_pct',
        'Entire_All_Negative_pct',
        'StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec'
    ]
    
    required = [dep_var] + controls + ['ceo_id', 'year']
    complete_mask = df[required].notna().all(axis=1)
    df_reg = df[complete_mask].copy()
    print(f"Complete cases: {len(df_reg)}")
    
    # 3. Filter min calls >= 5
    ceo_counts = df_reg['ceo_id'].value_counts()
    valid_ceos = ceo_counts[ceo_counts >= 5].index
    df_reg = df_reg[df_reg['ceo_id'].isin(valid_ceos)].copy()
    print(f"Final Regression N: {len(df_reg)} (CEOs: {df_reg['ceo_id'].nunique()})")
    
    # 4. Run Pooled Regression
    df_reg['ceo_id'] = df_reg['ceo_id'].astype(str)
    df_reg['year'] = df_reg['year'].astype(str)
    
    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"Running POOLED regression...")
    
    model = smf.ols(formula, data=df_reg).fit()
    
    print("\n=== POOLED REGRESSION RESULTS ===")
    print(f"R-squared: {model.rsquared:.4f}")
    print(f"Adj. R-squared: {model.rsquared_adj:.4f}")
    print(f"N: {int(model.nobs)}")
    
if __name__ == "__main__":
    run_pooled_regression()
