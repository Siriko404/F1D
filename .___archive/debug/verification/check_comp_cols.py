import pandas as pd
from pathlib import Path

def main():
    root = Path(".")
    comp_file = root / '1_Inputs' / 'comp_na_daily_all' / 'ht3poqveggoha6qj.parquet'
    
    if not comp_file.exists():
        print(f"File not found: {comp_file}")
        return

    print(f"Reading {comp_file}...")
    df = pd.read_parquet(comp_file)
    print("Columns found:")
    print(df.columns.tolist())
    
    # Check for EPS-like columns
    eps_candidates = [c for c in df.columns if 'eps' in c.lower()]
    print(f"\nPotential EPS columns: {eps_candidates}")
    return

if __name__ == "__main__":
    main()
