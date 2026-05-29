"""Supervisor Tasks 19+20: Compustat-routed treatment + CASH vs Table 1.

Task 19: Route 10-K CIKs through step1 Compustat survivor sample.
  - Get step1 survivor GVKEYs → CCM P-only GVKEY→CIK (valid in 2015)
  - Intersect 10-K CIKs with survivor CIKs
  - Classify treated/control, run T8 DiD
  - Hypothesis: cleaner Compustat population → δ rises toward 0.357

Task 20: CASH distribution check.
  - Compute T1 and T8 CASH moments in estimation sample
  - Compare to paper Table 1 CASH (mean=0.22, SD=0.25, median=0.12)
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, WINSOR, _build, _calendar_lag1, _latest, _prev_q,
)

ZIP = ROOT / "inputs" / "10-X_C_2015_10Konly.zip"
CCM_PATH = ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")

_p = ROOT / "scripts" / "campello_rebuild" / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p)
_fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin)
_statsum_meanest_z = _fin._statsum_meanest_z

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── §1+7 EXTRACTION (same as step3b3) ──────────────────────────────────

ITEM_RE = re.compile(r"item[\s ]{0,4}(\d{1,2}[ab]?)\s*[\.\:\)\-—]", re.IGNORECASE)
FNAME = re.compile(r"\d{4}/QTR\d/(\d{8})_([A-Z0-9-]+)_edgar_data_(\d+)_([A-Za-z0-9-]+)\.txt")
PAT_WB = re.compile(r"\b(brexit|great britain|uncertainty|referendum|uncertain|united kingdom|uk)\b", re.IGNORECASE)
PAT_ABBR = re.compile(r"(?<![A-Za-z])(u\.k\.|g\.b\.)(?![A-Za-z])", re.IGNORECASE)
MIN_SEC, HIGH_T = 200, 5


def _norm_item(g): return g.lower().strip()

def _best_span(text, target, terms):
    marks = [(_norm_item(m.group(1)), m.start(), m.end()) for m in ITEM_RE.finditer(text)]
    if not marks: return None
    best, best_len = None, 0
    for i, (num, s, e) in enumerate(marks):
        if num != target: continue
        end = len(text)
        for num2, s2, _ in marks[i+1:]:
            if num2 in terms: end = s2; break
        seg = text[e:end]
        if len(seg) > best_len: best, best_len = seg, len(seg)
    return best if (best and best_len >= MIN_SEC) else None

def _sec17(text):
    s1 = _best_span(text, "1", {"1a","1b","2","3","4"})
    s7 = _best_span(text, "7", {"7a","8","9"})
    return (s1 + "\n" + s7) if (s1 and s7) else None

def _count(text):
    return len(PAT_WB.findall(text)) + len(PAT_ABBR.findall(text))


# ── T8 DV BUILDER ──────────────────────────────────────────────────────

def _cash_dv_t8():
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"]>=BUFFER_LO)&(df["datadate"]<=WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD")&(df["loc"]=="USA")&(df["consol"]=="C")&(df["indfmt"]=="INDL")&(df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year*10+df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable").drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & (df["denom"]>0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH"]]


# ── DiD RUNNER ─────────────────────────────────────────────────────────

def run_did(treatment_df, label):
    from linearmodels.panel import PanelOLS
    s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet", columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    nT = int((tt["HIGH_UK_EXPOSURE"]==1).sum()); nC = int((tt["HIGH_UK_EXPOSURE"]==0).sum())
    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_cash_dv_t8(), on=["gvkey","cal_yr_qtr"], how="inner")
    df = df[df["atq"]>0].copy(); df["log_assets"] = np.log(df["atq"])
    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls); col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left"); firm_cols.append(col)
    df = df.merge(_calendar_lag1(df[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")
    df = df.merge(_statsum_meanest_z(), on=["gvkey","cal_yr_qtr"], how="left")
    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(lambda s: s.clip(s.quantile(WINSOR), s.quantile(1-WINSOR)))
    df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)+"_"+df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)
    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH","indqtr_code"]+cols).copy()
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index(); nf = sub["gvkey"].nunique()
    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True, other_effects=pdat["indqtr_code"], drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    b = float(res.params["POST_x_HIGH"]); se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"]); p = float(res.pvalues["POST_x_HIGH"])
    nT_est = int(sub[sub["HIGH_UK_EXPOSURE"]==1]["gvkey"].nunique()); nC_est = int(sub[sub["HIGH_UK_EXPOSURE"]==0]["gvkey"].nunique())
    cash_pcts = {q: float(sub["CASH"].quantile(q)) for q in [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]}
    return {"label": label, "nT_treat": nT, "nC_treat": nC, "nT_est": nT_est, "nC_est": nC_est,
            "delta": b, "se": se, "t": t, "p": p, "nobs": int(res.nobs), "nfirms": int(nf),
            "r2w": float(res.rsquared_within), "cash_mean": float(sub["CASH"].mean()),
            "cash_sd": float(sub["CASH"].std()), "cash_pcts": cash_pcts}


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*72)
    print("TASKS 19+20: Compustat-routed treatment + CASH vs Table 1")
    print("="*72)

    # ── TASK 19: Build survivor CIK set ────────────────────────────────
    print("\n── Building step1 survivor CIK set (CCM P-only, valid in 2015) ──")
    s1_path = _latest("step1_sample") / "sample.parquet"
    s1 = pd.read_parquet(s1_path, columns=["gvkey"])
    survivor_gvkeys = set(s1["gvkey"].astype(str).str.zfill(6).unique())
    print(f"step1 survivor GVKEYs: {len(survivor_gvkeys):,}")

    # CCM P-only: GVKEY→CIK valid during 2015
    ccm = pd.read_parquet(CCM_PATH, columns=["gvkey","cik","LINKPRIM","LINKTYPE","LINKDT","LINKENDDT"])
    ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
    ccm = ccm[ccm["gvkey"].isin(survivor_gvkeys)]
    ccm = ccm[(ccm["LINKPRIM"]=="P") & (ccm["LINKTYPE"].isin(["LU","LC"]))]
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"].astype(str).replace({"E":"2099-12-31"}), errors="coerce")
    ccm = ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2015-01-01")) & (ccm["LINKDT"]<=pd.Timestamp("2015-12-31"))]
    ccm["cik"] = pd.to_numeric(ccm["cik"], errors="coerce"); ccm = ccm.dropna(subset=["cik"])
    ccm["cik"] = ccm["cik"].astype("int64")

    # Per GVKEY: pick CIK with best date overlap in 2015
    resolved = []
    for gk, grp in ccm.groupby("gvkey"):
        if len(grp)==1: resolved.append(grp.iloc[0])
        else:
            best, best_row = -1, None
            for _, row in grp.iterrows():
                s_d = max(row["LINKDT"], pd.Timestamp("2015-01-01"))
                e_d = min(row["LINKENDDT"], pd.Timestamp("2015-12-31"))
                ov = (e_d - s_d).days
                if ov > best: best, best_row = ov, row
            resolved.append(best_row)
    gvkey_to_cik = pd.DataFrame(resolved)[["gvkey","cik"]].drop_duplicates("gvkey")
    survivor_ciks = set(gvkey_to_cik["cik"].unique())
    cik_to_gvkey = dict(zip(gvkey_to_cik["cik"], gvkey_to_cik["gvkey"]))
    print(f"  GVKEYs with CIK: {len(gvkey_to_cik):,}")
    print(f"  Survivor CIKs: {len(survivor_ciks):,}")
    n_lost = len(survivor_gvkeys) - len(gvkey_to_cik)
    print(f"  GVKEYs without CIK in CCM P-only: {n_lost:,} ({n_lost/len(survivor_gvkeys)*100:.1f}%)")

    # ── Process 10-Ks with survivor-CIK filter ──────────────────────────
    print("\n── Processing 10-K zip (§1+7, survivor-CIK filter) ──")
    t0 = time.time()
    rows, n_dir, n_badname, n_decerr, n_secfail, n_no_cik = [], 0, 0, 0, 0, 0
    with zipfile.ZipFile(ZIP, "r") as zf:
        infos = zf.infolist()
        for i, info in enumerate(infos, 1):
            if info.is_dir() or info.file_size == 0: n_dir += 1; continue
            m = FNAME.match(info.filename)
            if not m: n_badname += 1; continue
            date_str, ftype, cik_str, _acc = m.groups()
            cik_int = int(cik_str)
            if cik_int not in survivor_ciks: n_no_cik += 1; continue  # KEY FILTER
            try:
                with zf.open(info, "r") as f: text = f.read().decode("utf-8", errors="replace")
            except Exception: n_decerr += 1; continue
            scoped = _sec17(text); del text
            if scoped is None: n_secfail += 1; continue
            tot = _count(scoped); del scoped
            rows.append({"filing_date": pd.to_datetime(date_str, format="%Y%m%d"),
                         "filing_type": ftype, "cik": cik_int, "total_count": tot,
                         "gvkey": cik_to_gvkey.get(cik_int)})
            if i % 1500 == 0:
                print(f"  …{i:,}/{len(infos):,} (surv {len(rows):,}, secfail {n_secfail:,}, {time.time()-t0:.0f}s)")

    f = pd.DataFrame(rows)
    print(f"\n  Parsed (survivor CIK): {len(f):,}  dirs={n_dir}  badname={n_badname}  "
          f"decerr={n_decerr}  secfail={n_secfail}  no-CIK={n_no_cik:,}  {time.time()-t0:.0f}s")

    # Dedupe: latest filing per CIK
    f = f.sort_values(["cik","filing_date"], kind="stable").drop_duplicates("cik", keep="last")
    print(f"  After CIK dedupe: {len(f):,}")

    # Aggregate by GVKEY (sum counts for multi-CIK GVKEYs)
    g = f.groupby("gvkey", as_index=False)["total_count"].sum()
    g["group"] = "_excl"
    g.loc[g["total_count"]==0, "group"] = "control"
    g.loc[g["total_count"]>HIGH_T, "group"] = "treated"
    g["HIGH_UK_EXPOSURE"] = g["group"].map({"treated":1.0,"control":0.0}).astype("float64")
    nT = int((g["group"]=="treated").sum())
    nC = int((g["group"]=="control").sum())
    nX = int((g["group"]=="_excl").sum())
    print(f"\n  Compustat-routed treatment:")
    print(f"    Treated: {nT:,}  (paper 807)")
    print(f"    Control: {nC:,}  (paper 433)")
    print(f"    Excluded: {nX:,}")

    # ── Run DiDs ───────────────────────────────────────────────────────
    print(f"\n{'='*72}")
    print("T8 DiD RESULTS")
    print(f"{'='*72}")

    results = []

    # (A) Compustat-routed treatment
    tt_comp = g[g["group"].isin(["treated","control"])][["gvkey","total_count","group","HIGH_UK_EXPOSURE"]]
    r = run_did(tt_comp, "Compustat-routed §1+7")
    results.append(r)
    print(f"\n── Compustat-routed §1+7 ──")
    print(f"  T(treat)={r['nT_treat']:,} C(treat)={r['nC_treat']:,}  "
          f"T(est)={r['nT_est']:,} C(est)={r['nC_est']:,}")
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}")

    # (B) Existing §1+7 treatment (from step3b3, for reference)
    s3b = _latest("step3b3_textual_treatment_sec17")
    tt_existing = pd.read_parquet(s3b / "treatment_textual.parquet")
    tt_existing["gvkey"] = tt_existing["gvkey"].astype(str).str.zfill(6)
    r2 = run_did(tt_existing, "Existing §1+7 (raw CCM {P,C})")
    results.append(r2)
    print("\n── Existing §1+7 (raw CCM {P,C}) ──")
    print(f"  T(treat)={r2['nT_treat']:,} C(treat)={r2['nC_treat']:,}  "
          f"T(est)={r2['nT_est']:,} C(est)={r2['nC_est']:,}")
    print(f"  δ={r2['delta']:+.5f}  SE={r2['se']:.5f}  t={r2['t']:+.3f}  "
          f"p={r2['p']:.4f}  N={r2['nobs']:,}  firms={r2['nfirms']:,}  "
          f"R²w={r2['r2w']:.4f}")

    # ── TASK 20: CASH distribution ─────────────────────────────────────
    print(f"\n{'='*72}")
    print("TASK 20: CASH DISTRIBUTION CHECK")
    print(f"{'='*72}")
    paper = {"mean":0.22, "sd":0.25, "median":0.12, "iqr":0.27, "n":78044}

    for r in results:
        print(f"\n── {r['label']} ──")
        print(f"  CASH (T8, winsor 1%):  μ={r['cash_mean']:.4f}  σ={r['cash_sd']:.4f}")
        pcts = r["cash_pcts"]
        print(f"  Percentiles: 1%={pcts[0.01]:.4f}  5%={pcts[0.05]:.4f}  "
              f"25%={pcts[0.25]:.4f}  50%={pcts[0.50]:.4f}  "
              f"75%={pcts[0.75]:.4f}  95%={pcts[0.95]:.4f}  99%={pcts[0.99]:.4f}")
    print(f"\n  Paper Table 1 Panel A CASH: μ={paper['mean']:.2f}  "
          f"σ={paper['sd']:.2f}  med={paper['median']:.2f}  "
          f"IQR={paper['iqr']:.2f}  N={paper['n']:,}")
    print(f"  NOTE: Paper Table 1 uses T1 DV (cheq/atq_l1). Our T8 DV ")
    print(f"  (cheq/(atq_l1-cheq_l1)) expected to have higher mean/SD.")

    # Side-by-side
    print(f"\n{'='*72}")
    print(f"{'Variant':<35} {'δ':>10} {'SE':>8} {'t':>7} {'p':>7} {'N':>8} {'firms':>6} {'R²w':>6}")
    print("-"*90)
    for r in results:
        print(f"{r['label']:<35} {r['delta']:>+10.5f} {r['se']:>8.5f} {r['t']:>+7.3f} "
              f"{r['p']:>7.4f} {r['nobs']:>8,} {r['nfirms']:>6,} {r['r2w']:>6.4f}")
    print(f"{'Paper (T8 col.2)':<35} {+0.357:>+10.3f} {0.062:>8.3f} {'?':>7} {'***':>7} {24195:>8,} {'?':>6} {0.24:>6.2f}")

    od = ROOT / "outputs" / "campello_rebuild" / "_diag_t19_t20"
    od.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (od / f"results_{ts}.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\nwritten → {od / f'results_{ts}.json'}")
