"""Investigate remaining unmatched records"""
import pandas as pd

# Load data with the fix
meta = pd.read_parquet(r'4_Outputs/1.2_LinkEntities/latest/metadata_linked.parquet')
tenure = pd.read_parquet(r'4_Outputs/1.3_BuildTenureMap/latest/tenure_monthly.parquet')

# Apply the same GVKEY fix
meta['gvkey_str'] = meta['gvkey'].apply(lambda x: str(int(x)).zfill(6) if pd.notna(x) else None)
tenure['gvkey_str'] = tenure['gvkey'].astype(str).str.zfill(6)

# Check overlap again
meta_gvkeys = set(meta['gvkey_str'].dropna().unique())
tenure_gvkeys = set(tenure['gvkey_str'].unique())

overlap = meta_gvkeys & tenure_gvkeys
only_meta = meta_gvkeys - tenure_gvkeys
only_tenure = tenure_gvkeys - meta_gvkeys

print(f"--- After GVKEY Fix ---")
print(f"Metadata GVKEYs: {len(meta_gvkeys):,}")
print(f"Tenure GVKEYs: {len(tenure_gvkeys):,}")
print(f"Overlap: {len(overlap):,} ({len(overlap)/len(meta_gvkeys)*100:.1f}% of metadata GVKEYs)")
print(f"Only in metadata: {len(only_meta):,}")
print(f"Only in tenure: {len(only_tenure):,}")

# How many CALLS have overlapping GVKEYs?
meta['has_tenure_gvkey'] = meta['gvkey_str'].isin(tenure_gvkeys)
calls_with_tenure = meta['has_tenure_gvkey'].sum()
print(f"\nCalls with GVKEY in tenure panel: {calls_with_tenure:,} ({calls_with_tenure/len(meta)*100:.1f}%)")

# For calls that have matching GVKEY, why don't some match on (year, month)?
meta['start_date'] = pd.to_datetime(meta['start_date'])
meta['year'] = meta['start_date'].dt.year
meta['month'] = meta['start_date'].dt.month

# Check year coverage in tenure
print(f"\n--- Year Coverage ---")
print(f"Tenure years: {tenure['year'].min()} - {tenure['year'].max()}")

# Sample some unmatched GVKEYs (those only in metadata)
print(f"\n--- Sample GVKEYs only in metadata (no CEO data) ---")
sample = list(only_meta)[:5]
print(sample)

# For a GVKEY that is in both, check if year/month alignment works
if len(overlap) > 0:
    test_gvkey = list(overlap)[0]
    print(f"\n--- Testing GVKEY: {test_gvkey} ---")
    meta_sample = meta[meta['gvkey_str'] == test_gvkey][['gvkey_str', 'year', 'month', 'start_date']].drop_duplicates()
    tenure_sample = tenure[tenure['gvkey_str'] == test_gvkey][['gvkey_str', 'year', 'month']].drop_duplicates()
    print(f"Metadata has {len(meta_sample)} unique (year, month) combos")
    print(f"Tenure has {len(tenure_sample)} unique (year, month) combos")
    
    # Check intersection
    meta_ym = set(zip(meta_sample['year'], meta_sample['month']))
    tenure_ym = set(zip(tenure_sample['year'], tenure_sample['month']))
    ym_overlap = meta_ym & tenure_ym
    print(f"Overlapping (year, month) combos: {len(ym_overlap)}")
