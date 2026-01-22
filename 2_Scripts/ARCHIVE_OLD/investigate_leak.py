"""Investigate data leak in Step 1.4 join"""
import pandas as pd

# Load the linked metadata
meta = pd.read_parquet(r'4_Outputs/1.2_LinkEntities/latest/metadata_linked.parquet')
print(f"Linked metadata: {len(meta):,} calls")
print(f"Unique GVKEYs in metadata: {meta['gvkey'].nunique():,}")

# Load the CEO tenure panel
tenure = pd.read_parquet(r'4_Outputs/1.3_BuildTenureMap/latest/tenure_monthly.parquet')
print(f"\nTenure panel: {len(tenure):,} records")
print(f"Unique GVKEYs in tenure: {tenure['gvkey'].nunique():,}")

# Check GVKEY overlap
meta_gvkeys = set(meta['gvkey'].unique())
tenure_gvkeys = set(tenure['gvkey'].unique())

overlap = meta_gvkeys & tenure_gvkeys
only_meta = meta_gvkeys - tenure_gvkeys
only_tenure = tenure_gvkeys - meta_gvkeys

print(f"\n--- GVKEY Overlap Analysis ---")
print(f"Metadata GVKEYs: {len(meta_gvkeys):,}")
print(f"Tenure GVKEYs: {len(tenure_gvkeys):,}")
print(f"Overlap: {len(overlap):,}")
print(f"Only in metadata: {len(only_meta):,}")
print(f"Only in tenure: {len(only_tenure):,}")

# How many calls have GVKEYs that exist in tenure panel?
meta['has_tenure_gvkey'] = meta['gvkey'].isin(tenure_gvkeys)
calls_with_tenure = meta['has_tenure_gvkey'].sum()
print(f"\nCalls with GVKEY in tenure panel: {calls_with_tenure:,} ({calls_with_tenure/len(meta)*100:.1f}%)")

# Check date ranges
print(f"\n--- Date Range Check ---")
meta['year'] = pd.to_datetime(meta['start_date']).dt.year
meta['month'] = pd.to_datetime(meta['start_date']).dt.month
print(f"Metadata years: {meta['year'].min()} - {meta['year'].max()}")
print(f"Tenure years: {tenure['year'].min()} - {tenure['year'].max()}")

# Sample some GVKEYs from metadata that are NOT in tenure
print(f"\n--- Sample GVKEYs only in metadata ---")
sample_only_meta = list(only_meta)[:10]
print(sample_only_meta)

# Check one specific overlapping GVKEY
if len(overlap) > 0:
    sample_gvkey = list(overlap)[0]
    print(f"\n--- Sample overlapping GVKEY: {sample_gvkey} ---")
    meta_sample = meta[meta['gvkey'] == sample_gvkey][['gvkey', 'year', 'month', 'start_date']].head(5)
    tenure_sample = tenure[tenure['gvkey'] == sample_gvkey][['gvkey', 'year', 'month']].head(10)
    print("Metadata sample:")
    print(meta_sample)
    print("\nTenure sample:")
    print(tenure_sample)
