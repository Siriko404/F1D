"""Trace N drops through DiD data assembly."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_010458"

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

PRE_Q=[20153,20154]; POST_Q=[20163,20164]
ctrl_cols = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]

# Start with variables panel: DiD window
n0 = len(panel[panel["cal_yr_qtr"].isin(PRE_Q+POST_Q)])
print(f"Variables panel in DiD window: {n0:,}")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

did = panel[panel["cal_yr_qtr"].isin(PRE_Q+POST_Q)]
n1 = len(did)
print(f"After stock+ceps+beta merge: {n1:,}")

# Lag controls
did = did.sort_values(["gvkey","cal_yr_qtr"])
for c in ctrl_cols:
    did[f"{c}_lag1"] = did.groupby("gvkey")[c].shift(1)

# Add CASH_T8
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]: comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")
did = did.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")

# Trace drops per variable
print(f"\nN in DiD window: {len(did):,}")
for v in ["CASH","beta_uk"] + ctrl_cols + ["cheq"]:
    n = did[v].notna().sum()
    pct = n/len(did)*100
    print(f"  {v:<20}: {n:>6,}  ({pct:.1f}%)")

# Lagged controls
print(f"\nLagged:")
for c in ctrl_cols:
    n = did[f"{c}_lag1"].notna().sum()
    print(f"  {c}_lag1: {n:,}")

# Final intersection
required = ["CASH"] + [f"{c}_lag1" for c in ctrl_cols]
sub = did.dropna(subset=required)
print(f"\nFull sample (no β NAN filter): {len(sub):,}")

required_beta = ["CASH","beta_uk"] + [f"{c}_lag1" for c in ctrl_cols]
sub_beta = did.dropna(subset=required_beta)
print(f"With β non-missing: {len(sub_beta):,}")
