"""Deep investigation of linking options via CCM"""
import pandas as pd
from pathlib import Path

root = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

# Load data
manifest = pd.read_parquet(root / "4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet")
ccm = pd.read_parquet(root / "1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet")

print(f"Manifest: {len(manifest):,} calls")
print(f"CCM: {len(ccm):,} rows")

print(f"\n{'='*60}")
print("MANIFEST IDENTIFIER COVERAGE")
print("="*60)

# Clean identifiers
manifest['permno_clean'] = pd.to_numeric(manifest['permno'], errors='coerce')
manifest['gvkey_clean'] = manifest['gvkey'].astype(str).str.zfill(6) if 'gvkey' in manifest.columns else None
manifest['cusip_clean'] = manifest['cusip'].astype(str).str[:8] if 'cusip' in manifest.columns else None
manifest['cusip6'] = manifest['cusip'].astype(str).str[:6] if 'cusip' in manifest.columns else None

for col in ['permno_clean', 'gvkey_clean', 'cusip_clean', 'cusip6']:
    if col in manifest.columns and manifest[col] is not None:
        valid = manifest[col].notna() & (manifest[col] != '') & (manifest[col] != 'nan')
        n = valid.sum()
        print(f"{col:20}: {n:,} / {len(manifest):,} ({n/len(manifest)*100:.1f}%)")

print(f"\n{'='*60}")
print("CCM IDENTIFIER COVERAGE")
print("="*60)

# CCM identifiers
ccm['gvkey_clean'] = ccm['gvkey'].astype(str).str.zfill(6)
ccm['LPERMNO_clean'] = pd.to_numeric(ccm['LPERMNO'], errors='coerce')
ccm['cusip_clean'] = ccm['cusip'].astype(str).str[:8]
ccm['cusip6'] = ccm['cusip'].astype(str).str[:6]

for col in ['gvkey_clean', 'LPERMNO_clean', 'cusip_clean', 'cusip6']:
    if col in ccm.columns:
        valid = ccm[col].notna()
        n = valid.sum()
        print(f"{col:20}: {n:,} / {len(ccm):,} ({n/len(ccm)*100:.1f}%)")

print(f"\n{'='*60}")
print("LINKING VIA GVKEY")
print("="*60)

# Create gvkey -> LPERMNO mapping
gvkey_to_permno = ccm[['gvkey_clean', 'LPERMNO_clean']].dropna().drop_duplicates()
gvkey_to_permno = gvkey_to_permno.groupby('gvkey_clean')['LPERMNO_clean'].first().reset_index()
print(f"Unique gvkey -> LPERMNO mappings: {len(gvkey_to_permno):,}")

# How many manifest gvkeys can we link?
manifest_with_gvkey = manifest[manifest['gvkey_clean'].notna() & (manifest['gvkey_clean'] != 'nan')].copy()
linked = manifest_with_gvkey.merge(gvkey_to_permno, on='gvkey_clean', how='left')
n_linked = linked['LPERMNO_clean'].notna().sum()
print(f"Manifest calls with valid gvkey: {len(manifest_with_gvkey):,}")
print(f"Calls linked to LPERMNO via gvkey: {n_linked:,} ({n_linked/len(manifest)*100:.1f}%)")

print(f"\n{'='*60}")
print("LINKING VIA CUSIP6")
print("="*60)

# Create cusip6 -> LPERMNO mapping
cusip_to_permno = ccm[['cusip6', 'LPERMNO_clean']].dropna().drop_duplicates()
cusip_to_permno = cusip_to_permno.groupby('cusip6')['LPERMNO_clean'].first().reset_index()
print(f"Unique cusip6 -> LPERMNO mappings: {len(cusip_to_permno):,}")

# How many manifest cusips can we link?
manifest_with_cusip = manifest[manifest['cusip6'].notna() & (manifest['cusip6'] != 'nan') & (manifest['cusip6'] != '')].copy()
linked_cusip = manifest_with_cusip.merge(cusip_to_permno, on='cusip6', how='left')
n_linked_cusip = linked_cusip['LPERMNO_clean'].notna().sum()
print(f"Manifest calls with valid cusip6: {len(manifest_with_cusip):,}")
print(f"Calls linked to LPERMNO via cusip6: {n_linked_cusip:,} ({n_linked_cusip/len(manifest)*100:.1f}%)")

print(f"\n{'='*60}")
print("COMBINED LINKING STRATEGY")
print("="*60)

# Try combined: gvkey first, then cusip6 fallback
manifest['linked_permno'] = manifest['permno_clean']  # Start with direct permno

# Fallback 1: gvkey -> CCM
no_permno = manifest['linked_permno'].isna()
gvkey_map = dict(zip(gvkey_to_permno['gvkey_clean'], gvkey_to_permno['LPERMNO_clean']))
manifest.loc[no_permno, 'linked_permno'] = manifest.loc[no_permno, 'gvkey_clean'].map(gvkey_map)

# Fallback 2: cusip6 -> CCM
still_no_permno = manifest['linked_permno'].isna()
cusip_map = dict(zip(cusip_to_permno['cusip6'], cusip_to_permno['LPERMNO_clean']))
manifest.loc[still_no_permno, 'linked_permno'] = manifest.loc[still_no_permno, 'cusip6'].map(cusip_map)

final_coverage = manifest['linked_permno'].notna().sum()
print(f"Final PERMNO coverage with combined strategy: {final_coverage:,} / {len(manifest):,} ({final_coverage/len(manifest)*100:.1f}%)")

# Breakdown
direct = manifest['permno_clean'].notna().sum()
from_gvkey = (manifest['linked_permno'].notna() & manifest['permno_clean'].isna() & manifest['gvkey_clean'].isin(gvkey_map.keys())).sum()
from_cusip = final_coverage - direct - from_gvkey
print(f"\n  - Direct permno: {direct:,}")
print(f"  - Via gvkey->CCM: ~{from_gvkey:,}")
print(f"  - Via cusip6->CCM: ~{from_cusip:,}")
