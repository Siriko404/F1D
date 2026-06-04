"""Chen et al. (2017) — Greenfield rebuild: Restatement DiD on Cash.

Split-sample PSM DiD. HLM dataset -> Compustat merge -> PSM matching
-> event-window panel -> split-sample joint estimation -> Table 3 Panel A.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import re, zipfile
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

# =============================================================================
# Phase 1: Load & filter HLM restatement data
# =============================================================================
print("=" * 60)
print("Phase 1: Loading HLM restatement dataset")
print("=" * 60)

hlm = pd.read_csv(ROOT / "inputs" / "ERROR_IRREG_HLM.csv", encoding="latin1")
col_irreg = [c for c in hlm.columns if "Irreg" in c or "irreg" in c][0]
hlm["Restatement_Date"] = pd.to_datetime(hlm["Restatement_Date"], errors="coerce")
hlm = hlm[hlm["duplicate_restate"] != 1].copy()
hlm = hlm[hlm["gvkey"].notna()].copy()
hlm["gvkey"] = hlm["gvkey"].astype(int)
hlm = hlm.sort_values(["gvkey", "Restatement_Date"])
hlm = hlm.drop_duplicates(subset=["gvkey"], keep="first").copy()

print(f"Restatements after dedup: {len(hlm):,}")
print(f"  Irregularity: {(hlm[col_irreg]==1).sum()}  Error: {(hlm[col_irreg]==0).sum()}")

# =============================================================================
# Phase 2: Load Compustat + merge HLM
# =============================================================================
print("\n" + "=" * 60)
print("Phase 2: Loading Compustat Annual")
print("=" * 60)

FUNDA_COLS = [
    "gvkey", "fyear", "datadate", "sic",
    "che", "at", "prcc_f", "csho", "ceq",
    "oancf", "act", "lct", "dlc", "dltt",
    "capx", "aqc", "xrd", "sale", "dvc",
    "dltis", "dltr", "dlcch", "sstk", "ni",
    "dd1", "dd2", "dd3", "au",
]
comp = pd.read_csv(ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv", usecols=FUNDA_COLS)
comp = comp[comp["at"] > 0].copy()
comp["gvkey"] = comp["gvkey"].astype(int)

comp = comp.merge(hlm[["gvkey", "Restatement_Date", col_irreg]], on="gvkey", how="left", validate="many_to_one")
comp["IS_RESTATER"] = comp[col_irreg].notna().astype(int)
comp["IRREG"] = comp[col_irreg].fillna(0).astype(int)

# =============================================================================
# Phase 3: Variable construction (baseline Panel A)
# =============================================================================
print("\n" + "=" * 60)
print("Phase 3: Constructing variables")
print("=" * 60)

comp["CASH"] = comp["che"] / comp["at"]
comp["Q"] = (comp["at"] + comp["prcc_f"] * comp["csho"] - comp["ceq"]) / comp["at"]
comp["SIZE"] = np.log(comp["at"])
comp["CF"] = comp["oancf"] / comp["at"]
comp["NWC"] = ((comp["act"] - comp["che"].fillna(0)) - (comp["lct"] - comp["dlc"].fillna(0))) / comp["at"]
comp["LEV"] = (comp["dltt"] + comp["dlc"].fillna(0)) / comp["at"]
comp["MVE"] = comp["prcc_f"] * comp["csho"]

# SIGMA
cf_cols = comp[["gvkey", "fyear", "CF"]].dropna(subset=["CF"])
m = cf_cols.merge(cf_cols, on="gvkey", suffixes=("", "_hist"))
in_w = (m["fyear_hist"] < m["fyear"]) & (m["fyear_hist"] >= m["fyear"] - 10)
hist = m[in_w]
cf_sd = hist.groupby(["gvkey", "fyear"])["CF_hist"].agg(["std", "count"])
cf_sd = cf_sd[cf_sd["count"] >= 3].reset_index()
cf_sd = cf_sd.rename(columns={"std": "cf_sd"})
comp = comp.merge(cf_sd[["gvkey", "fyear", "cf_sd"]], on=["gvkey", "fyear"], how="left")
comp["sic2"] = pd.to_numeric(comp["sic"], errors="coerce").fillna(0).astype(int) // 100
comp["SIGMA"] = comp.groupby(["sic2", "fyear"])["cf_sd"].transform("median")

# NSEG
SEG_CSV = ROOT / "inputs" / "CompustatHistoricalSegments" / "eceabmcmldcdggbz.csv.zip"
seg = pd.read_csv(SEG_CSV, usecols=["gvkey", "datadate", "srcdate", "stype", "sid", "ias"])
seg = seg[seg["stype"].isin(["BUSSEG", "OPSEG"])]
seg = seg[seg["ias"] > 0]
seg["srcdate_dt"] = pd.to_datetime(seg["srcdate"], errors="coerce")
seg["datadate_dt"] = pd.to_datetime(seg["datadate"], errors="coerce")
seg = seg[seg["srcdate_dt"] == seg["datadate_dt"]]
seg["gvkey_int"] = pd.to_numeric(seg["gvkey"], errors="coerce")
seg = seg.drop_duplicates(subset=["gvkey_int", "datadate", "stype", "sid"])
seg["fyear"] = seg["datadate_dt"].dt.year
seg_nseg = seg.groupby(["gvkey_int", "fyear"])["sid"].nunique().reset_index()
seg_nseg.columns = ["gvkey", "fyear", "NSEG"]
comp = comp.merge(seg_nseg, on=["gvkey", "fyear"], how="left")
comp["NSEG"] = comp["NSEG"].fillna(1).astype(int)

# AGE
first_year = comp.groupby("gvkey")["fyear"].min().rename("first_fyear")
comp = comp.merge(first_year, on="gvkey", how="left")
comp["AGE"] = np.log(np.maximum(comp["fyear"] - comp["first_fyear"], 1))

# PSM covariates (expanded model vars)
comp["CAPX"] = comp["capx"] / comp["at"]
comp["ACQUISITION"] = comp["aqc"].fillna(0) / comp["at"]
comp["RD"] = comp["xrd"].fillna(0) / comp["sale"]
comp["DIV"] = comp["dvc"].fillna(0) / comp["at"]

print(f"Variables constructed. {len(comp):,} rows")

# =============================================================================
# Phase 4: Quality filters
# =============================================================================
print("\n" + "=" * 60)
print("Phase 4: Quality filters")
print("=" * 60)

# SIC exclusions
comp["sic_num"] = pd.to_numeric(comp["sic"], errors="coerce")
before = len(comp)
comp = comp[~comp["sic_num"].between(6000, 6999)]
comp = comp[~comp["sic_num"].between(4900, 4999)]
print(f"  After SIC filter: {len(comp):,} (dropped {before - len(comp):,})")

# CHE <= AT
before = len(comp)
comp = comp[comp["che"].fillna(0) <= comp["at"]]
print(f"  After CHE <= AT: {len(comp):,} (dropped {before - len(comp):,})")

# AT OR MVE >= $10M
before = len(comp)
comp = comp[(comp["at"] >= 10) | (comp["MVE"] >= 10)]
print(f"  After AT>=10 OR MVE>=10: {len(comp):,} (dropped {before - len(comp):,})")

# Growth screens
comp = comp.sort_values(["gvkey", "fyear"])
comp["asset_growth"] = comp.groupby("gvkey")["at"].pct_change()
comp["sales_growth"] = comp.groupby("gvkey")["sale"].pct_change()
before = len(comp)
comp = comp[comp["asset_growth"].fillna(0).abs() <= 1]
comp = comp[comp["sales_growth"].fillna(0).abs() <= 1]
print(f"  After growth <= 100%: {len(comp):,} (dropped {before - len(comp):,})")

print(f"\nPanel: {len(comp):,} rows, {comp['gvkey'].nunique():,} firms")
print(f"  Restatement: {comp[comp['IS_RESTATER']==1]['gvkey'].nunique():,}")
print(f"  Non-restatement: {comp[comp['IS_RESTATER']==0]['gvkey'].nunique():,}")

# =============================================================================
# Phase 5: FF48 classification + Event-window panel + naive DiD
# =============================================================================
print("\n" + "=" * 60)
print("Phase 5: FF48 classification")
print("=" * 60)

with zipfile.ZipFile(ROOT / "inputs" / "FF1248" / "Siccodes48.zip") as zf:
    txt = zf.read("Siccodes48.txt").decode("utf-8")
sic_to_ff48 = {}
current_ff48 = None
for line in txt.split("\n"):
    m = re.match(r"^\s*(\d+)\s+\w+", line)
    if m and not re.match(r"^\s*\d{4}-\d{4}", line):
        current_ff48 = int(m.group(1))
    elif current_ff48:
        mm = re.match(r"\s*(\d{4})-(\d{4})", line)
        if mm:
            for sic in range(int(mm.group(1)), int(mm.group(2)) + 1):
                sic_to_ff48[sic] = current_ff48

comp["ff48"] = comp["sic"].fillna(0).astype(int).map(sic_to_ff48).fillna(99).astype(int)
print(f"FF48 mapped. Unique industries: {comp['ff48'].nunique()}")

# =============================================================================
# Phase 6: Event-window panel (treated firms only, no PSM for now)
# =============================================================================
print("\n" + "=" * 60)
print("Phase 6: Event-window panel for treated firms")
print("=" * 60)

# Build per-firm event windows: years [-3,-1] ∪ [+1,+3] relative to year 0
treated = comp[comp["IS_RESTATER"] == 1].copy()
treated["y0"] = pd.to_datetime(treated["Restatement_Date"]).dt.year
event_rows = []
for gv in treated["gvkey"].unique():
    sub = comp[comp["gvkey"] == gv].copy()
    y0 = int(treated.loc[treated["gvkey"] == gv, "y0"].iloc[0])
    irreg = int(treated.loc[treated["gvkey"] == gv, "IRREG"].iloc[0])
    for t in [-3, -2, -1, 1, 2, 3]:
        cy = y0 + t
        fy = sub[sub["fyear"] == cy].copy()
        if len(fy) > 0:
            fy["event_year"] = t
            fy["y0"] = y0
            fy["POST"] = 1 if t > 0 else 0
            event_rows.append(fy)

ep = pd.concat(event_rows, ignore_index=True)
ep["POST"] = ep["POST"].astype(int)

print(f"Event panel: {len(ep):,} rows, {ep['gvkey'].nunique():,} firms")
print(f"  POST=1: {(ep['POST']==1).sum():,}  POST=0: {(ep['POST']==0).sum():,}")
print(f"  IRREG=1: {(ep['IRREG']==1).sum():,} rows, {ep[ep['IRREG']==1]['gvkey'].nunique():,} firms")
print(f"  IRREG=0: {(ep['IRREG']==0).sum():,} rows, {ep[ep['IRREG']==0]['gvkey'].nunique():,} firms")

# Pre-post CASH means by IRREG
for label, mask in [("ALL", slice(None)), ("IRREG", ep["IRREG"]==1), ("ERROR", ep["IRREG"]==0)]:
    sub = ep[mask]
    pre = sub[sub["POST"]==0]["CASH"].mean()
    post = sub[sub["POST"]==1]["CASH"].mean()
    diff = post - pre
    n = len(sub)
    print(f"  {label:6s}: pre={pre:.4f} post={post:.4f} diff={diff:+.4f} N={n:,}")

# =============================================================================
# Phase 7: Industry-matched control firms + event-window panel
# =============================================================================
print("\n" + "=" * 60)
print("Phase 7: Matching control firms (FF48 + year-0 SIZE)")
print("=" * 60)

# Get year-0 data for all treated firms
treated_y0 = ep[["gvkey", "y0", "ff48", "IRREG", "SIZE"]].drop_duplicates(["gvkey"])
# Control pool: non-restatement firms with data in each treated firm's year 0
controls = comp[comp["IS_RESTATER"] == 0].copy()

# For each treated firm, find best FF48+SIZE match in year 0
matches = []
for _, trow in treated_y0.iterrows():
    y0 = int(trow["y0"])
    ff48 = int(trow["ff48"])
    t_size = trow["SIZE"]
    t_gv = int(trow["gvkey"])
    # Control candidates: same FF48, same year, non-restater
    c_candidates = controls[(controls["fyear"] == y0) & (controls["ff48"] == ff48)]
    if len(c_candidates) == 0:
        continue
    # Closest SIZE
    c_candidates = c_candidates.copy()
    c_candidates["size_diff"] = (c_candidates["SIZE"] - t_size).abs()
    best = c_candidates.loc[c_candidates["size_diff"].idxmin()]
    matches.append({
        "treated_gvkey": t_gv,
        "control_gvkey": int(best["gvkey"]),
        "y0": y0,
        "ff48": ff48,
        "IRREG": int(trow["IRREG"]),
    })

match_df = pd.DataFrame(matches)
print(f"Matched pairs: {len(match_df)}")
print(f"  IRREG pairs: {(match_df['IRREG']==1).sum()}")
print(f"  ERROR pairs: {(match_df['IRREG']==0).sum()}")

# Build control-firm event panels (same event window as matched treated)
control_rows = []
for _, mr in match_df.iterrows():
    c_gv = int(mr["control_gvkey"])
    y0 = int(mr["y0"])
    irreg = int(mr["IRREG"])
    sub = comp[comp["gvkey"] == c_gv].copy()
    for t in [-3, -2, -1, 1, 2, 3]:
        cy = y0 + t
        fy = sub[sub["fyear"] == cy].copy()
        if len(fy) > 0:
            fy["event_year"] = t
            fy["y0"] = y0
            fy["POST"] = 1 if t > 0 else 0
            fy["IS_TREATED"] = 0
            fy["IRREG"] = irreg  # inherited from matched treated
            fy["treated_gvkey"] = mr["treated_gvkey"]
            fy["control_gvkey"] = c_gv
            control_rows.append(fy)

cp = pd.concat(control_rows, ignore_index=True)
cp["POST"] = cp["POST"].astype(int)
cp["IS_TREATED"] = 0

# Tag treated panel
ep["IS_TREATED"] = 1
ep["treated_gvkey"] = ep["gvkey"]
ep["control_gvkey"] = np.nan

print(f"Control event panel: {len(cp):,} rows, {cp['gvkey'].nunique():,} firms")

# Stack treated + control
full_panel = pd.concat([ep, cp], ignore_index=True)
full_panel["pair_id"] = full_panel["treated_gvkey"].astype(str) + "_" + full_panel["y0"].astype(str)
full_panel["firm_id"] = full_panel["gvkey"].astype(str)
print(f"Full DiD panel: {len(full_panel):,} rows")

# =============================================================================
# Phase 8: DiD estimation with full control coefficient comparison
# =============================================================================
print("\n" + "=" * 60)
print("Phase 8: DiD estimation — full coefficient comparison")
print("=" * 60)

from linearmodels.panel import PanelOLS

BASELINE_CTRLS = ["Q", "SIZE", "CF", "NWC", "LEV", "SIGMA", "NSEG", "AGE"]
ALL_VARS = ["CASH", "POST", "IS_TREATED"] + BASELINE_CTRLS

diag = full_panel.dropna(subset=ALL_VARS).copy()
diag["gvkey_str"] = diag["gvkey"].astype(str)

# Paper Table 3 Panel A anchors (IRREG: cols 5-6)
PAPER_IRREG = {
    "T":  {"POST": (0.046, 4.84), "Q": (0.003, 1.01), "SIZE": (0.013, 0.91),
           "CF": (-0.014, -0.18), "NWC": (-0.000, -0.03), "LEV": (-0.020, -0.30),
           "SIGMA": (0.015, 0.55), "NSEG": (0.004, 0.73), "AGE": (-0.023, -1.93)},
    "C":  {"POST": (0.012, 1.90), "Q": (0.003, 0.77), "SIZE": (0.002, 0.14),
           "CF": (0.089, 1.12), "NWC": (0.003, 0.37), "LEV": (0.029, 0.60),
           "SIGMA": (0.004, 0.21), "NSEG": (-0.001, -0.49), "AGE": (-0.005, -0.45)},
    "R2": (0.180, 0.198), "N": (1391, 1434),
}

PAPER_ERROR = {
    "T":  {"POST": (0.020, 2.23), "Q": (0.003, 1.36), "SIZE": (-0.010, -0.95),
           "CF": (0.144, 2.68), "NWC": (-0.003, -1.18), "LEV": (-0.001, -0.03),
           "SIGMA": (0.001, 0.05), "NSEG": (0.001, 0.49), "AGE": (-0.005, -0.54)},
    "C":  {"POST": (0.011, 1.73), "Q": (0.006, 1.96), "SIZE": (-0.002, -0.22),
           "CF": (0.185, 3.52), "NWC": (-0.001, -0.56), "LEV": (0.009, 0.18),
           "SIGMA": (0.008, 0.39), "NSEG": (-0.001, -0.47), "AGE": (-0.008, -0.88)},
    "R2": (0.156, 0.160), "N": (3550, 3570),
}

for sample_label, sample_mask, paper in [
    ("IRREG", diag["IRREG"] == 1, PAPER_IRREG),
    ("ERROR", diag["IRREG"] == 0, PAPER_ERROR),
]:
    sub = diag[sample_mask]
    print(f"\n{'='*70}")
    print(f"  {sample_label} SAMPLE — COEFFICIENT COMPARISON")
    print(f"{'='*70}")

    for group, treat_mask, pkey in [("TREATED", sub["IS_TREATED"] == 1, "T"), ("CONTROL", sub["IS_TREATED"] == 0, "C")]:
        sg = sub[treat_mask].set_index(["gvkey_str", "fyear"])
        exog = ["POST"] + BASELINE_CTRLS
        m = PanelOLS(sg["CASH"], sg[exog], entity_effects=True).fit()
        n = int(m.nobs)
        print(f"\n  --- {group} (N={n:,}) ---")
        print(f"  {'Variable':8s} {'Ours':>12s} {'t-stat':>8s}  {'Paper':>12s} {'t-stat':>8s}")
        print(f"  {'-'*52}")

        for var in ["POST"] + BASELINE_CTRLS:
            b = m.params.get(var, np.nan)
            t = m.tstats.get(var, np.nan)
            pb, pt = paper[pkey].get(var, (np.nan, np.nan))
            print(f"  {var:8s} {b:+.4f}   {t:+8.3f}  {pb:+.4f}   {pt:+8.3f}")

        r2 = m.rsquared
        pr2, pn = paper.get("R2", (np.nan, np.nan)), paper.get("N", (np.nan, np.nan))
        print(f"  {'R2':8s} {r2:.3f}            {pr2[0]:.3f} / {pr2[1]:.3f}")
        if group == "TREATED":
            print(f"  {'N':8s} {n:,}            {pn[0]:,}")
        else:
            print(f"  {'N':8s} {n:,}            {pn[1]:,}")

    # DiD: POST difference
    sub_t = sub[sub["IS_TREATED"] == 1].set_index(["gvkey_str", "fyear"])
    sub_c = sub[sub["IS_TREATED"] == 0].set_index(["gvkey_str", "fyear"])
    m_t = PanelOLS(sub_t["CASH"], sub_t[exog], entity_effects=True).fit()
    m_c = PanelOLS(sub_c["CASH"], sub_c[exog], entity_effects=True).fit()
    b_diff = m_t.params["POST"] - m_c.params["POST"]
    print(f"\n  POST Diff (T-C): {b_diff:+.4f}  (paper: {paper['T']['POST'][0] - paper['C']['POST'][0]:+.4f})")

print("\nPhase 8 complete.")
