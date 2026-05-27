"""Improve IBES→Compustat match. Try multi-key: tic + CUSIP + historical tic."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/"variables_panel.parquet").exists()], reverse=True)
panel = pd.read_parquet(runs[0] / "variables_panel.parquet")
sample_gv = set(panel["gvkey"].unique())

# Load IBES — get TICKER, OFTIC, CUSIP for unique firms
zpath = ROOT / "inputs" / "tr_ibes" / "ibes_statsum.zip"
with zipfile.ZipFile(zpath) as z:
    with z.open(z.namelist()[0]) as f:
        ibes = pd.read_csv(f, usecols=["TICKER","OFTIC","CUSIP","FPEDATS","MEASURE","FISCALP","FPI","USFIRM","CURCODE"], low_memory=False)

ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")
ibes = ibes[(ibes["MEASURE"]=="EPS")&(ibes["FISCALP"]=="QTR")&(ibes["FPI_n"]==6)&(ibes["CURCODE"]=="USD")&(ibes["USFIRM"]==1)]
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["FPEDATS"]>="2010-01-01")&(ibes["FPEDATS"]<="2017-03-31")]
print(f"IBES rows: {len(ibes):,}, unique TICKER: {ibes['TICKER'].nunique():,}, unique OFTIC: {ibes['OFTIC'].nunique():,}, unique CUSIP: {ibes['CUSIP'].nunique():,}")

# Compustat: gvkey + tic + cusip + datadate
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
    columns=["gvkey","tic","cusip","datadate"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp = comp[comp["gvkey"].isin(sample_gv)]
print(f"Compustat unique tics: {comp['tic'].nunique():,}, cusips: {comp['cusip'].nunique():,}")

# CUSIP format: IBES = 8-digit (issue), Compustat = 9-digit (CUSIP9). Try 8-char prefix match.
ibes_cusip8 = ibes["CUSIP"].dropna().astype(str).str[:8].unique()
comp_cusip8 = comp["cusip"].dropna().astype(str).str[:8].unique()
print(f"\nCUSIP-8 overlap: IBES={len(set(ibes_cusip8)):,} Comp={len(set(comp_cusip8)):,} overlap={len(set(ibes_cusip8) & set(comp_cusip8)):,}")

# Test ticker match (OFTIC vs Compustat tic)
ibes_ofticer = set(ibes["OFTIC"].dropna().unique())
comp_tic_set = set(comp["tic"].dropna().unique())
print(f"OFTIC overlap with Compustat tic: {len(ibes_ofticer & comp_tic_set):,} of {len(ibes_ofticer):,} IBES OFTICs")

# Build full IBES→gvkey map via CUSIP-8
ibes["CUSIP8"] = ibes["CUSIP"].astype(str).str[:8]
comp["cusip8"] = comp["cusip"].astype(str).str[:8]
unique_ibes = ibes[["TICKER","OFTIC","CUSIP8"]].drop_duplicates()
unique_comp = comp[["gvkey","tic","cusip8"]].drop_duplicates(subset=["gvkey","cusip8"])

map_via_cusip = unique_ibes.merge(unique_comp[["gvkey","cusip8"]], left_on="CUSIP8", right_on="cusip8", how="inner")
print(f"\nIBES→gvkey via CUSIP8: {map_via_cusip['TICKER'].nunique():,} unique TICKERs mapped")
print(f"  Unique gvkeys reached: {map_via_cusip['gvkey'].nunique():,}")
