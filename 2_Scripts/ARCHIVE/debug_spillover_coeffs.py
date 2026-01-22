import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path

def analyze_spillover(root):
    # Paths
    clarity_personal_path = root / '4_Outputs' / '4.1.1_CeoClarity_CEO_Only' / 'latest' / 'ceo_clarity_scores.parquet'
    clarity_regime_path = root / '4_Outputs' / '4.1.3_CeoClarity_Regime' / 'latest' / 'ceo_clarity_scores.parquet'
    
    tone_personal_path = root / '4_Outputs' / '4.1.4_CeoTone' / 'latest' / 'ceo_tone_scores.parquet'
    # Note: Tone scores are all in one file, we need to separate models
    
    print("Loading Clarity Scores...")
    c_pers = pd.read_parquet(clarity_personal_path)
    c_reg = pd.read_parquet(clarity_regime_path)
    
    # Merge Clarity
    # Personal model is 'ClarityCEO', Regime is 'ClarityRegime' (or similar, checking columns)
    # The output of 4.1.1 has 'ClarityCEO'. 4.1.3 has 'ClarityCEO' (variable name in parquet might be same, need to check)
    
    # Actually 4.1.3 variable is likely named 'ClarityCEO' too inside the file unless I changed it.
    # Let's rename for merge
    c_pers = c_pers[['ceo_id', 'ClarityCEO']].rename(columns={'ClarityCEO': 'Personal_Clarity'})
    c_reg = c_reg[['ceo_id', 'ClarityCEO']].rename(columns={'ClarityCEO': 'Regime_Clarity'})
    
    clarity_merged = c_pers.merge(c_reg, on='ceo_id')
    
    print(f"\nMatched {len(clarity_merged)} CEOs for Clarity.")
    
    # Regress Regime ~ Personal
    model_c = smf.ols("Regime_Clarity ~ Personal_Clarity", data=clarity_merged).fit()
    beta_c = model_c.params['Personal_Clarity']
    r2_c = model_c.rsquared
    corr_c = clarity_merged['Regime_Clarity'].corr(clarity_merged['Personal_Clarity'])
    
    print(f"CLARITY Spillover:")
    print(f"  Correlation: {corr_c:.4f}")
    print(f"  Beta (Slope): {beta_c:.4f}")
    print(f"  R2 (of the link): {r2_c:.4f}")

    # ---------------------------------------------------------
    
    print("\nLoading Tone Scores...")
    t_scores = pd.read_parquet(tone_personal_path)
    # This file has 'ToneCEO', 'ToneRegime', etc. columns if merged?
    # Or is it long format? The script 4.1.4 outputs one file.
    # Let's inspect columns of tone scores first.
    # Based on 4.1.4 script: "ceo_scores = ceo_fe.merge..." and "all_ceo_scores.append". 
    # It stacks them row-wise? Or merges?
    # 4.1.4 script: "ceo_scores_df = pd.concat(all_ceo_scores, ignore_index=True)"
    # So it's long format with a 'model' column ('ToneAll', 'ToneCEO', 'ToneRegime').
    
    t_pers = t_scores[t_scores['model'] == 'ToneCEO'][['ceo_id', 'ToneCEO']].rename(columns={'ToneCEO': 'Personal_Tone'})
    t_reg = t_scores[t_scores['model'] == 'ToneRegime'][['ceo_id', 'ToneRegime']].rename(columns={'ToneRegime': 'Regime_Tone'})
    
    tone_merged = t_pers.merge(t_reg, on='ceo_id')
    
    print(f"\nMatched {len(tone_merged)} CEOs for Tone.")
    
    # Regress Regime ~ Personal
    model_t = smf.ols("Regime_Tone ~ Personal_Tone", data=tone_merged).fit()
    beta_t = model_t.params['Personal_Tone']
    r2_t = model_t.rsquared
    corr_t = tone_merged['Regime_Tone'].corr(tone_merged['Personal_Tone'])
    
    print(f"TONE Spillover:")
    print(f"  Correlation: {corr_t:.4f}")
    print(f"  Beta (Slope): {beta_t:.4f}")
    print(f"  R2 (of the link): {r2_t:.4f}")

if __name__ == "__main__":
    root = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
    analyze_spillover(root)
