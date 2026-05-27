"""Check DIVESTITURES for top tercile β firms — no PSM."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/"beta_uk.parquet").exists()], reverse=True)
beta_dir = runs[0]

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="inner")

# Full pre-window
pre = panel[panel["cal_yr_qtr"] <= 20154]

# Paper Panel B: Top tercile of β^UK (nonneg)
nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)

top = pre[pre["beta_uk"] > t2].copy()
mid = pre[(pre["beta_uk"] >= t1) & (pre["beta_uk"] <= t2)].copy()
bot = pre[(pre["beta_uk"] >= 0) & (pre["beta_uk"] < t1)].copy()

# Table 1 Panel B (paper, top tercile β^UK)
# DIVESTITURES (×100): 0.10, N=8,604
# Table 1 Panel C (paper, bot tercile β^UK)
# DIVESTITURES (×100): 0.08, N=9,422

print(f"=== RAW DIVESTITURES (×100) by β^UK tercile (no PSM) ===")
print(f"Paper Panel B (top tercile): mean=0.10, sd=0.38, N=8,604")
print(f"Paper Panel C (bot tercile): mean=0.08, sd=0.32, N=9,422")
print()
for label, grp in [("Top β (>t2)", top), ("Mid β (t1-t2)", mid), ("Bot β (0-t1)", bot)]:
    s = grp["DIVESTITURES"].dropna()
    n_firms = grp["gvkey"].nunique()
    print(f"  {label}: mean={(s.mean()*100):.3f}  sd={s.std()*100:.3f}  N={len(s):,}  firms={n_firms}")

# Now check: DIVESTITURES for firms WITH available SPPE (non-zero denominator)
# Our DIVESTITURES imputes 0 where SPPE is missing. Paper may keep them as missing.
# This would pull mean DOWN.
print(f"\n=== DIVESTITURES for firms with sppey_q>0 only ===")
for label, grp in [("Top β", top), ("Bot β", bot)]:
    # sppey_q is the de-cumulated variable - check raw DIVESTITURES distribution
    s = grp["DIVESTITURES"].dropna()
    s_pos = s[s > 0]  # actual divestitures
    print(f"  {label}: all mean={(s.mean()*100):.3f}  non-zero mean={(s_pos.mean()*100):.3f}  %zero={(s<=0).mean()*100:.1f}%  N={len(s):,}")
