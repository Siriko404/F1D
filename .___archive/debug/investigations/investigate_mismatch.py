import pandas as pd
from pathlib import Path

# Paths
root = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
unified_path = root / "1_Inputs/Unified-info.parquet"
tokenized_dir = root / "4_Outputs/2.3_TokenizeAndCount/latest"

def investigate_mismatch(year):
    print(f"\nInvestigating mismatch for Year {year}...")
    
    # Load Unified-info
    try:
        unified_df = pd.read_parquet(unified_path)
        unified_files = set(unified_df['file_name'].astype(str).str.strip().unique())
        print(f"Unified-info total unique file_names: {len(unified_files):,}")
    except Exception as e:
        print(f"Error loading Unified-info: {e}")
        return

    # Load tokenized data for the year
    tokenized_file = tokenized_dir / f"manager_qa_call_{year}.parquet"
    if not tokenized_file.exists():
        print(f"Tokenized file not found: {tokenized_file}")
        return

    try:
        tokenized_df = pd.read_parquet(tokenized_file)
        tokenized_files = set(tokenized_df['file_name'].astype(str).str.strip().unique())
        print(f"Tokenized (manager_qa {year}) unique file_names: {len(tokenized_files):,}")
    except Exception as e:
        print(f"Error loading tokenized file: {e}")
        return

    # Calculate missing
    missing = tokenized_files - unified_files
    print(f"Missing from Unified-info: {len(missing):,}")
    
    if len(missing) > 0:
        print("\nSample missing file_names (Tokenized but not in Unified):")
        for fn in list(missing)[:5]:
            print(f"  - '{fn}'")
            
        print("\nSample present file_names (In both):")
        present = list(tokenized_files.intersection(unified_files))[:5]
        for fn in present:
            print(f"  - '{fn}'")
            
        # Check for potential partial matches or formatting issues
        print("\nChecking for potential formatting issues...")
        sample_missing = list(missing)[0]
        
        # Check if it exists in unified with different extension
        base_name = sample_missing.rsplit('.', 1)[0]
        potential_matches = [f for f in unified_files if base_name in f]
        if potential_matches:
            print(f"Found potential partial matches for '{sample_missing}':")
            for match in potential_matches:
                print(f"  - '{match}'")
        else:
            print(f"No partial matches found for base name '{base_name}'")

investigate_mismatch(2014)
