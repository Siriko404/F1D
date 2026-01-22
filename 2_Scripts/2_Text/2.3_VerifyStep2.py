
import pandas as pd
from pathlib import Path
import sys

def main():
    print("=== Step 2.3: Verify Step 2 Outputs ===")
    root = Path(__file__).parent.parent.parent
    
    out_base = root / '4_Outputs' / '2_Textual_Analysis'
    
    years = range(2002, 2019)
    all_ok = True
    
    print(f"{'Year':<6} {'Counts File':<20} {'Variables File':<20} {'Rows (Vars)':<12} {'Missing DepVar':<15}")
    print("-" * 80)
    
    for year in years:
        counts_path = out_base / f'2.1_Tokenized/latest/linguistic_counts_{year}.parquet'
        vars_path = out_base / f'2.2_Variables/latest/linguistic_variables_{year}.parquet'
        
        counts_ok = "OK" if counts_path.exists() else "MISSING"
        vars_ok = "OK" if vars_path.exists() else "MISSING"
        
        rows = 0
        missing_dep = 0
        
        if vars_path.exists():
            df = pd.read_parquet(vars_path)
            rows = len(df)
            col = 'Manager_QA_Uncertainty_pct'
            if col not in df.columns:
                vars_ok = "BAD COL"
            else:
                missing_dep = df[col].isna().sum()
                
        print(f"{year:<6} {counts_ok:<20} {vars_ok:<20} {rows:<12,} {missing_dep:<15,}")
        
        if counts_ok != "OK" or vars_ok != "OK":
            all_ok = False
            
    if all_ok:
        print("\n[SUCCESS] All files present and valid.")
    else:
        print("\n[FAILURE] Some files missing or invalid.")
        
if __name__ == "__main__":
    main()
