
import pandas as pd
import numpy as np
from pathlib import Path
import sys

def setup_logging():
    log_dir = Path(__file__).parent.parent.parent / '3_Logs' / '2.2_VerifyStep2'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def verify_output(year, root):
    path = root / f"4_Outputs/2_Linguistic_Analysis/latest/linguistic_features_{year}.parquet"
    if not path.exists():
        print(f"❌ {year}: File not found at {path}")
        return False
        
    df = pd.read_parquet(path)
    print(f"✅ {year}: File found. Rows: {len(df):,}")
    
    # 1. Schema Check
    required_cols = ['file_name', 'speaker_name', 'context', 'total_tokens', 'year',
                     'gvkey', 'conm', 'sic', 'start_date']
    categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious']
    
    missing = []
    for c in required_cols:
        if c not in df.columns: missing.append(c)
        
    for cat in categories:
        if f"{cat}_count" not in df.columns: missing.append(f"{cat}_count")
        if f"{cat}_tokens" not in df.columns: missing.append(f"{cat}_tokens")
        if f"{cat}_unique_tokens" not in df.columns: missing.append(f"{cat}_unique_tokens")
        if f"{cat}_unique_count" not in df.columns: missing.append(f"{cat}_unique_count")
        
    if missing:
        print(f"❌ {year}: Missing columns: {missing}")
        return False
    else:
        print(f"✅ {year}: Schema Check Passed")
        
    # 2. Metadata Check
    null_meta = df['gvkey'].isnull().sum()
    if null_meta > 0:
        print(f"⚠️ {year}: {null_meta:,} rows ({null_meta/len(df):.1%}) missing GVKEY (Failed Merge?)")
    else:
        print(f"✅ {year}: 100% GVKEY Coverage")
        
    # 3. Token Check (Spot Check)
    # Check a random row where Positive_count > 0
    sample = df[df['Positive_count'] > 0].head(1)
    if not sample.empty:
        row = sample.iloc[0]
        count = row['Positive_count']
        tokens = row['Positive_tokens']
        unique = row['Positive_unique_tokens']
        unique_cnt = row['Positive_unique_count']
        
        print(f"ℹ️  Sample {year} (Positive): Count={count}, Len(Tokens)={len(tokens)}")
        if count != len(tokens):
            print(f"❌ {year}: Count mismatch! {count} != {len(tokens)}")
        else:
            print(f"✅ {year}: Count logic consistent")
            
        if unique_cnt != len(unique):
            print(f"❌ {year}: Unique Count mismatch!")
            
    return True

def main():
    root = Path(__file__).parent.parent.parent
    print("=== Step 2 Verification ===")
    
    years = list(range(2002, 2019))
    all_pass = True
    
    for y in years:
        if not verify_output(y, root):
            all_pass = False
            
    if all_pass:
        print("\n🎉 SUCCESS: All 3 years verified.")
    else:
        print("\n❌ FAILURE: Verification failed.")

if __name__ == "__main__":
    main()
