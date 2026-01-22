import pandas as pd

try:
    df = pd.read_parquet(r'c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/1_Inputs/Execucomp/comp_execucomp.parquet')
    
    # Filter for CEO records only (ceoann == 'CEO' or similar indicator)
    # Let's check what value 'ceoann' takes
    print("Unique CEO Ann values:", df['ceoann'].unique())
    
    # Pick one interesting GVKEY manually or the first one with distinct CEOs
    target_gv = '001004' # AAR Corp (from previous sample) or let's find one dynamically
    
    # improved filter: Find a gvkey with at least 3 distinct CEOs
    counts = df.groupby('gvkey')['execid'].nunique()
    multi_ceo_gvkeys = counts[counts >= 3].index.tolist()
    
    if multi_ceo_gvkeys:
        target_gv = multi_ceo_gvkeys[0]

    print(f"\nAnalyzing Transitions for GVKEY: {target_gv}")
    subset = df[df['gvkey'] == target_gv].sort_values(['year', 'execid'])
    
    # Only show rows that might imply CEO status
    # ceoann='CEO' OR becameceo is not null OR leftofc is not null
    mask = (subset['ceoann'] == 'CEO') | (subset['becameceo'].notna()) | (subset['leftofc'].notna())
    subset = subset[mask]
    
    cols = ['year', 'execid', 'becameceo', 'leftofc', 'ceoann', 'joined_co']
    
    # Write to file
    with open('transition_dump.txt', 'w', encoding='utf-8') as f:
        f.write(subset[cols].head(30).to_string())
    print("Written to transition_dump.txt")

except Exception as e:
    print(e)
