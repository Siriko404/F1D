"""Investigate firm-level aggregation potential"""
import pandas as pd

df = pd.read_parquet(r'4_Outputs/1.1_CleanMetadata/latest/metadata_cleaned.parquet')

print(f"Total calls: {len(df):,}")
print(f"\nUnique identifiers:")
print(f"  company_name: {df['company_name'].nunique():,}")
print(f"  company_id: {df['company_id'].nunique():,}")
print(f"  cusip: {df['cusip'].nunique():,}")
print(f"  company_ticker: {df['company_ticker'].nunique():,}")
print(f"  permno: {df['permno'].nunique():,}")

print(f"\nAvg calls per company_name: {len(df)/df['company_name'].nunique():.1f}")
print(f"Avg calls per company_id: {len(df)/df['company_id'].nunique():.1f}")

# Check if company_id is stable (same company_id -> same PERMNO/CUSIP)
print("\n--- Stability Check ---")
check = df.groupby('company_id').agg({
    'permno': 'nunique',
    'cusip': 'nunique',
    'company_name': 'nunique'
}).reset_index()

multi_permno = (check['permno'] > 1).sum()
multi_cusip = (check['cusip'] > 1).sum()
multi_name = (check['company_name'] > 1).sum()

print(f"company_ids with multiple PERMNOs: {multi_permno}")
print(f"company_ids with multiple CUSIPs: {multi_cusip}")
print(f"company_ids with multiple names: {multi_name}")
