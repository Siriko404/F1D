import pandas as pd
from pathlib import Path

# Paths
root = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
unified_path = root / "1_Inputs/Unified-info.parquet"
tokenized_dir = root / "4_Outputs/2.3_TokenizeAndCount/latest"

def check_coverage(year):
    print(f"\nChecking coverage for Year {year}...")
    
    # Load Unified-info
    try:
        unified_df = pd.read_parquet(unified_path)
        unified_files = set(unified_df['file_name'].unique())
        print(f"Unified-info total unique file_names: {len(unified_files):,}")
    except Exception as e:
        print(f"Error loading Unified-info: {e}")
        return

    # Load tokenized data for the year (using manager_qa as a sample)
    tokenized_file = tokenized_dir / f"manager_qa_call_{year}.parquet"
    if not tokenized_file.exists():
        print(f"Tokenized file not found: {tokenized_file}")
        return

    try:
        tokenized_df = pd.read_parquet(tokenized_file)
        tokenized_files = set(tokenized_df['file_name'].unique())
        print(f"Tokenized (manager_qa {year}) unique file_names: {len(tokenized_files):,}")
    except Exception as e:
        print(f"Error loading tokenized file: {e}")
        return

    # Calculate intersection and missing
    intersection = tokenized_files.intersection(unified_files)
    missing = tokenized_files - unified_files
    
    print(f"Matches found: {len(intersection):,}")
    print(f"Missing from Unified-info: {len(missing):,}")
    print(f"Match Rate: {len(intersection) / len(tokenized_files) * 100:.2f}%")

    if len(missing) > 0:
        print("\nSample missing file_names:")
        for fn in list(missing)[:5]:
            print(f"  - {fn}")

# Check for a good year and a bad year
check_coverage(2014)
check_coverage(2017)
