import pandas as pd
import numpy as np

input_path = r"c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/1_Inputs/CEO Dismissal Data 2021.02.03.xlsx"

def verify_assumption():
    print("Loading data...")
    df = pd.read_excel(input_path)
    
    # 1. Clean Dates
    # 'leftofc' might have mixed types or be missing
    df['leftofc_clean'] = pd.to_datetime(df['leftofc'], errors='coerce')
    
    # Filter for valid gvkey and sort
    df = df.dropna(subset=['gvkey'])
    df = df.sort_values(by=['gvkey', 'leftofc_clean', 'year'])
    
    results = []
    
    print("Analyzing tenure gaps...")
    for gvkey, group in df.groupby('gvkey'):
        group = group.reset_index(drop=True)
        
        for i in range(1, len(group)):
            curr = group.iloc[i]
            prev = group.iloc[i-1]
            
            # Assumption: Current starts day after Prev ends
            if pd.notnull(prev['leftofc_clean']):
                implied_start = prev['leftofc_clean'] + pd.Timedelta(days=1)
                
                # Check alignment with current record's 'year'
                # 'year' is likely the fiscal year of the record
                record_year = curr['year']
                
                if pd.notnull(record_year):
                    gap_years = record_year - implied_start.year
                    
                    results.append({
                        'gvkey': gvkey,
                        'prev_ceo': prev['exec_fullname'],
                        'curr_ceo': curr['exec_fullname'],
                        'prev_end': prev['leftofc_clean'],
                        'implied_start': implied_start,
                        'record_year': record_year,
                        'gap_years': gap_years
                    })
    
    results_df = pd.DataFrame(results)
    
    if results_df.empty:
        print("No consecutive records found with valid dates to test.")
        return

    with open('verification_results.txt', 'w') as f:
        # Analyze Gaps
        f.write("\n--- Assumption Verification Results ---\n")
        f.write(f"Total transitions analyzed: {len(results_df)}\n")
        
        # Perfect match (Implied start year == Record year)
        perfect = results_df[results_df['gap_years'] == 0]
        f.write(f"Perfect Year Match (Gap=0): {len(perfect)} ({len(perfect)/len(results_df):.1%})\n")
        
        # Close match (within 1 year)
        close = results_df[results_df['gap_years'].abs() <= 1]
        f.write(f"Close Match (Gap <= 1 yr): {len(close)} ({len(close)/len(results_df):.1%})\n")
        
        # Large gaps
        large_gaps = results_df[results_df['gap_years'] > 1]
        f.write(f"Potential Missing Data (Gap > 1 yr): {len(large_gaps)} ({len(large_gaps)/len(results_df):.1%})\n")
        
        # Negative gaps (Overlaps?)
        overlaps = results_df[results_df['gap_years'] < -1]
        f.write(f"Significant Overlaps (Gap < -1 yr): {len(overlaps)} ({len(overlaps)/len(results_df):.1%})\n")
        
        if not large_gaps.empty:
            f.write("\nExample Large Gaps:\n")
            f.write(large_gaps[['gvkey', 'prev_end', 'implied_start', 'record_year', 'gap_years']].head().to_string())

if __name__ == "__main__":
    verify_assumption()
