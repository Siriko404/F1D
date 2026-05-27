"""Check Hoberg FIC 100 overlap with sample gvkeys."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import zipfile
from io import BytesIO
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

# Load Hoberg from zip (per hoberg_phillips_fic100.py pattern)
zpath = ROOT / "inputs" / "Brexit_replication" / "HobergPhillips_FIC" / "FIC_Data.zip"
with zipfile.ZipFile(zpath) as zf:
    with zf.open("fic_data.txt") as f:
        buf = BytesIO(f.read())
hp = pd.read_csv(buf, sep="\t", usecols=["gvkey","year","icode100"],
                 dtype={"gvkey":"Int64","year":"Int64","icode100":"Int64"})
hp = hp.dropna()
hp["gvkey"] = hp["gvkey"].astype(int).astype(str).str.zfill(6)
hp["sic_3digit"] = hp["icode100"]  # FIC 100 industry code

# Which years available?
print(f"Hoberg FIC: {len(hp):,} rows, years {hp['year'].min()}-{hp['year'].max()}")
print(f"  Unique gvkeys: {hp['gvkey'].nunique():,}")
print(f"  Unique FIC100 codes: {hp['icode100'].nunique():,}")

# Overlap with our sample panel
OUT = ROOT / "outputs" / "campello_v2"
runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / "variables_panel.parquet").exists()], reverse=True)
panel = pd.read_parquet(runs[0] / "variables_panel.parquet")
panel_gv = set(panel["gvkey"].unique())
hp_gv = set(hp["gvkey"].unique())
overlap = panel_gv & hp_gv
print(f"\nPanel gvkeys: {len(panel_gv):,}")
print(f"Hoberg gvkeys: {len(hp_gv):,}")
print(f"Overlap: {len(overlap):,} ({len(overlap)/len(panel_gv)*100:.1f}% of panel)")

# Paper F8 benchmark: drop if missing Hoberg-Phillips → 49,107 obs
# Our F7 = 55,606 obs. Expected F8 = ~49,107 × (55,606/56,081) ≈ 48,700
# Let's compute expected: merge Hoberg year into panel by (gvkey, cal_yr)
panel_yr_gv = set((r.gvkey, r.cal_yr) for r in panel[["gvkey","cal_yr"]].drop_duplicates().itertuples())
hp_yr_gv = set((h.gvkey, int(h.year)) for h in hp[["gvkey","year"]].itertuples())
overlap_yr = panel_yr_gv & hp_yr_gv
print(f"\nPanel (gvkey, year) pairs: {len(panel_yr_gv):,}")
print(f"Hoberg (gvkey, year) pairs: {len(hp_yr_gv):,}")
print(f"Overlap: {len(overlap_yr):,}")

# Count N after Hoberg merge
panel_w_year = panel.copy()
panel_w_year["_merge_year"] = panel_w_year["cal_yr"].astype(int)
hp_years = hp[["gvkey","year","sic_3digit"]].drop_duplicates()
n_before = len(panel)
panel_w_hoberg = panel_w_year.merge(hp_years, left_on=["gvkey","_merge_year"], right_on=["gvkey","year"], how="inner")
n_after = len(panel_w_hoberg)
print(f"\nN before Hoberg filter: {n_before:,}")
print(f"N after Hoberg merge: {n_after:,}")
print(f"  Ratio: {n_after/n_before:.3f} (paper F7→F8: {49107/56081:.3f})")
print(f"  Unique gvkeys after: {panel_w_hoberg['gvkey'].nunique():,}")
