import pandas as pd
from pathlib import Path

# Paths
root = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
unified_path = root / "1_Inputs/Unified-info.parquet"
tokenized_dir = root / "4_Outputs/2.3_TokenizeAndCount/latest"

def investigate_null_permno(year):
    print(f"\nInvestigating NULL PERMNO for Year {year}...")
    
    # Load Unified-info
    try:
        unified_df = pd.read_parquet(unified_path)
        # Apply the same cleaning as the script
        unified_df['file_name'] = unified_df['file_name'].astype(str).str.strip()
        
        # Deduplicate as per script logic (simplified)
        unified_df = unified_df.sort_values(
            by=['file_name', 'validation_timestamp', 'start_date'],
            ascending=[True, False, False]
        ).drop_duplicates(subset=['file_name'], keep='first')
        
        print(f"Unified-info loaded and deduplicated. Total rows: {len(unified_df):,}")
    except Exception as e:
        print(f"Error loading Unified-info: {e}")
        return

    # Load tokenized data
    tokenized_file = tokenized_dir / f"manager_qa_call_{year}.parquet"
    if not tokenized_file.exists():
        print(f"Tokenized file not found: {tokenized_file}")
        return

    tokenized_df = pd.read_parquet(tokenized_file)
    tokenized_df['file_name'] = tokenized_df['file_name'].astype(str).str.strip()
    print(f"Tokenized (manager_qa {year}) loaded. Total rows: {len(tokenized_df):,}")

    # Merge
    merged = tokenized_df.merge(unified_df, on='file_name', how='left')
    
    # Analyze missing PERMNO
    missing_permno = merged[merged['permno'].isna()]
    count_missing = len(missing_permno)
    
    print(f"\nTotal rows after merge: {len(merged):,}")
    print(f"Rows with missing PERMNO: {count_missing:,} ({count_missing/len(merged)*100:.2f}%)")
    
    if count_missing > 0:
        print("\nBreakdown of missing PERMNO:")
        # Check if they matched a row in Unified but PERMNO was null, or if they didn't match at all
        # We can check 'company_name' or another column that should exist if matched
        
        matched_but_null_permno = missing_permno[missing_permno['company_name'].notna()]
        no_match_in_unified = missing_permno[missing_permno['company_name'].isna()]
        
        print(f"  - Matched in Unified but PERMNO is NULL: {len(matched_but_null_permno):,}")
        print(f"  - Did NOT match any row in Unified: {len(no_match_in_unified):,}")
        
        if len(matched_but_null_permno) > 0:
            print("\n  Sample files matched but with NULL PERMNO:")
            print(matched_but_null_permno[['file_name', 'company_name', 'start_date_x']].head())
            
        if len(no_match_in_unified) > 0:
            print("\n  Sample files with NO MATCH in Unified:")
            print(no_match_in_unified['file_name'].head())

investigate_null_permno(2014)
