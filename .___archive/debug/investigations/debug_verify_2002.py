
import pandas as pd
from pathlib import Path

# Check 2002 Output
path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\4_Outputs\2.9_LiquidityAnalysis\2025-12-05_175334\calls_with_liquidity_2002.parquet")
if path.exists():
    df = pd.read_parquet(path)
    print(f"Columns: {sorted(df.columns.tolist())}")
    
    # Check for sic-like columns
    sics = [c for c in df.columns if 'sic' in c.lower()]
    print(f"SIC candidates: {sics}")
else:
    print("File not found")
