"""Diagnose CONSENSUS_EPS magnitude. Anchor mean=0.07 sd=3.51. Ours mean=0.75 sd=3.49.
Hypothesis: near-zero STDEV creates blow-ups."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

zpath = ROOT / "inputs" / "tr_ibes" / "ibes_statsum.zip"
with zipfile.ZipFile(zpath) as z:
    with z.open(z.namelist()[0]) as f:
        ibes = pd.read_csv(f, usecols=["TICKER", "STATPERS", "MEASURE", "FISCALP", "FPI",
                                         "MEANEST", "FPEDATS", "USFIRM", "CURCODE",
                                         "ACTUAL", "STDEV", "NUMEST"], low_memory=False)

ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")
ibes = ibes[(ibes["MEASURE"]=="EPS") & (ibes["FISCALP"]=="QTR") & (ibes["FPI_n"]==6)
            & (ibes["CURCODE"]=="USD") & (ibes["USFIRM"]==1)]
ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["FPEDATS"] >= "2010-01-01") & (ibes["FPEDATS"] <= "2017-03-31")]
ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
ibes = ibes.sort_values(["TICKER", "FPEDATS", "STATPERS"]).drop_duplicates(["TICKER","FPEDATS"], keep="last")

for c in ["ACTUAL", "MEANEST", "STDEV", "NUMEST"]:
    ibes[c] = pd.to_numeric(ibes[c], errors="coerce")

print(f"N after filters: {len(ibes):,}")
print(f"\nSTDEV distribution:")
print(ibes["STDEV"].describe())
print(f"\n% STDEV == 0: {(ibes['STDEV']==0).mean()*100:.1f}%")
print(f"% STDEV < 0.01: {(ibes['STDEV']<0.01).mean()*100:.1f}%")
print(f"% STDEV < 0.05: {(ibes['STDEV']<0.05).mean()*100:.1f}%")
print(f"\nNUMEST distribution:")
print(ibes["NUMEST"].describe())

# Compute SUE under multiple denom thresholds
def sue_stats(df, label):
    sue = (df["ACTUAL"] - df["MEANEST"]) / df["STDEV"].replace(0, np.nan)
    sue = sue.replace([np.inf, -np.inf], np.nan)
    lo, hi = sue.quantile(0.01), sue.quantile(0.99)
    sue_w = sue.clip(lo, hi)
    s = sue_w.dropna()
    print(f"  {label}: N={len(s):,}  mean={s.mean():.4f}  sd={s.std():.4f}  p50={s.median():.4f}")

print("\n=== SUE stats by STDEV threshold ===")
print("Anchor: N=42,031  mean=0.07  sd=3.51  p50=0.09")
sue_stats(ibes, "no STDEV filter")
sue_stats(ibes[ibes["STDEV"] >= 0.01], "STDEV >= $0.01")
sue_stats(ibes[ibes["STDEV"] >= 0.05], "STDEV >= $0.05")
sue_stats(ibes[ibes["NUMEST"] >= 3], "NUMEST >= 3")
sue_stats(ibes[ibes["NUMEST"] >= 5], "NUMEST >= 5")
sue_stats(ibes[(ibes["STDEV"] >= 0.01) & (ibes["NUMEST"] >= 3)], "STDEV>=0.01 + NUMEST>=3")

# Alt: scale by lagged price (use prccq from Compustat?). Quick proxy: scale by |MEANEST|
print("\n=== Alt scaling: (ACTUAL-MEANEST)/|MEANEST| ===")
alt = (ibes["ACTUAL"] - ibes["MEANEST"]) / ibes["MEANEST"].abs().replace(0, np.nan)
alt = alt.replace([np.inf, -np.inf], np.nan)
lo, hi = alt.quantile(0.01), alt.quantile(0.99)
alt_w = alt.clip(lo, hi).dropna()
print(f"  N={len(alt_w):,}  mean={alt_w.mean():.4f}  sd={alt_w.std():.4f}  p50={alt_w.median():.4f}")

# Try: raw earnings surprise (no scaling)
print("\n=== Alt scaling: raw (ACTUAL - MEANEST) — no denom ===")
raw_surp = (ibes["ACTUAL"] - ibes["MEANEST"]).dropna()
lo, hi = raw_surp.quantile(0.01), raw_surp.quantile(0.99)
raw_w = raw_surp.clip(lo, hi)
print(f"  N={len(raw_w):,}  mean={raw_w.mean():.4f}  sd={raw_w.std():.4f}  p50={raw_w.median():.4f}")

# Try: MEANEST alone (raw forecast)
print("\n=== Alt: MEANEST raw (just the forecast) ===")
m = ibes["MEANEST"].dropna()
lo, hi = m.quantile(0.01), m.quantile(0.99)
m_w = m.clip(lo, hi)
print(f"  N={len(m_w):,}  mean={m_w.mean():.4f}  sd={m_w.std():.4f}  p50={m_w.median():.4f}")
