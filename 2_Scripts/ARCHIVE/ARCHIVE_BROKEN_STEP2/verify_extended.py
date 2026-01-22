
import pandas as pd
from pathlib import Path

def main():
    root = Path(__file__).parent.parent.parent
    # Get latest dir
    latest = root / '4_Outputs' / '2_Linguistic_Measures' / '2025-12-25_222300' # Hardcoded for safety during run
    
    f = latest / 'linguistic_features_extended_2002.parquet'
    if not f.exists():
        print("File not found")
        return
        
    df = pd.read_parquet(f)
    print(f"Rows: {len(df)}")
    print("Columns:", df.columns.tolist())
    
    # Check sample with data
    df_nonzero = df[df['Uncertainty_entropy'] > 0.5]
    if len(df_nonzero) > 0:
        sample = df_nonzero.sample(1).iloc[0]
        print(f"\nSample Row (High Entropy, N={len(df_nonzero)}):")
        for c in df.columns:
            if 'entropy' in c or 'pct' in c:
                print(f"{c}: {sample[c]}")
    else:
        print("No non-zero uncertainty rows found!")

if __name__ == "__main__":
    main()
