"""Supervisor Task 16: Proximity-scoped keyword recount + T8 DiD.

Sentence-level proximity rule for "Uncertainty"/"Uncertain":
- UK-specific terms (count freely): Brexit, Great Britain, United Kingdom,
  UK, U.K., G.B., Referendum
- Generic terms (need proximity): Uncertainty, Uncertain
- Count generic terms ONLY if they appear in a sentence containing >=1 UK term.
- All 9 keywords counted; the proximity filter applies only to the 2 generic terms.

Re-runs §1+7 extraction from the 10-K zip (same as step3b3), then runs
T8-DV DiD with the new treatment. Reports treated/control counts + δ/SE/t/N/R².
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
CCM = ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")

# Consensus
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
FNAME = re.compile(
    r"\d{4}/QTR\d/(\d{8})_([A-Z0-9-]+)_edgar_data_(\d+)_([A-Za-z0-9-]+)\.txt")
MIN_SEC = 200
HIGH_T, ZERO_T = 5, 0

# UK-specific terms: count freely
UK_TERMS_RE = re.compile(
    r"\b(brexit|great britain|united kingdom|referendum|uk)\b"
    r"|(?<![A-Za-z])(u\.k\.|g\.b\.)(?![A-Za-z])",
    re.IGNORECASE)

# Generic terms: only count if in UK-proximate sentence
GEN_TERMS_RE = re.compile(r"\b(uncertainty|uncertain)\b", re.IGNORECASE)

# Split text into sentences (handles common 10-K formatting)
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\'\(])')


def _norm_item(g: str) -> str:
    return g.lower().strip()


def _best_span(text: str, target: str, terms: set[str]) -> str | None:
    marks = [(_norm_item(m.group(1)), m.start(), m.end())
             for m in ITEM_RE.finditer(text)]
    if not marks:
        return None
    best, best_len = None, 0
    for i, (num, s, e) in enumerate(marks):
        if num != target:
            continue
        end = len(text)
        for num2, s2, _e2 in marks[i + 1:]:
            if num2 in terms:
                end = s2
                break
        seg = text[e:end]
        if len(seg) > best_len:
            best, best_len = seg, len(seg)
    return best if (best is not None and best_len >= MIN_SEC) else None


def _sec17(text: str) -> str | None:
    s1 = _best_span(text, "1", {"1a", "1b", "2", "3", "4"})
    s7 = _best_span(text, "7", {"7a", "8", "9"})
    if s1 is None or s7 is None:
        return None
    return s1 + "\n" + s7


def _count_proximity(text: str) -> int:
    """Count keywords with sentence-level proximity for generic terms."""
    sentences = SENT_SPLIT.split(text)
    # If text has no sentence breaks, treat as one sentence
    if len(sentences) <= 1:
        sentences = [text]

    total = 0
    for sent in sentences:
        # UK-specific terms in this sentence — count freely
        uk_hits = len(UK_TERMS_RE.findall(sent))
        total += uk_hits
        # Generic terms only count if sentence has UK content
        if uk_hits > 0:
            total += len(GEN_TERMS_RE.findall(sent))
    return total


def _count_verbatim(text: str) -> int:
    """Original 9-keyword count (no proximity filter) — for comparison."""
    pat_wb = re.compile(
        r"\b(brexit|great britain|uncertainty|referendum|uncertain|"
        r"united kingdom|uk)\b", re.IGNORECASE)
    pat_abbr = re.compile(r"(?<![A-Za-z])(u\.k\.|g\.b\.)(?![A-Za-z])",
                          re.IGNORECASE)
    return len(pat_wb.findall(text)) + len(pat_abbr.findall(text))


def _load_ccm() -> pd.DataFrame:
    c = pd.read_parquet(CCM, columns=["gvkey", "cik", "LINKPRIM",
                                      "LINKTYPE", "LINKDT", "LINKENDDT"])
    c = c[c["LINKPRIM"].isin(["P", "C"])
          & c["LINKTYPE"].isin(["LU", "LC"])].copy()
    c["LINKDT"] = pd.to_datetime(c["LINKDT"], errors="coerce")
    c["LINKENDDT"] = pd.to_datetime(
        c["LINKENDDT"].astype(str).replace({"E": "2099-12-31"}), errors="coerce")
    c["cik"] = pd.to_numeric(c["cik"], errors="coerce")
    c = c.dropna(subset=["gvkey", "cik", "LINKDT", "LINKENDDT"])
    c["cik"] = c["cik"].astype("int64")
    c["gvkey"] = c["gvkey"].astype("int64").astype(str).str.zfill(6)
    return c[["gvkey", "cik", "LINKDT", "LINKENDDT"]]


def build_treatment():
    """Re-run §1+7 extraction with proximity counting."""
    print("── Re-extracting §1+7 with proximity counting ──")
    t0 = time.time()
    rows, n_dir, n_badname, n_decerr, n_secfail = [], 0, 0, 0, 0
    with zipfile.ZipFile(ZIP, "r") as zf:
        infos = zf.infolist()
        for i, info in enumerate(infos, 1):
            if info.is_dir() or info.file_size == 0:
                n_dir += 1
                continue
            m = FNAME.match(info.filename)
            if not m:
                n_badname += 1
                continue
            date_str, ftype, cik, _acc = m.groups()
            try:
                with zf.open(info, "r") as f:
                    text = f.read().decode("utf-8", errors="replace")
            except Exception:
                n_decerr += 1
                continue
            scoped = _sec17(text)
            del text
            if scoped is None:
                n_secfail += 1
                continue
            prox_count = _count_proximity(scoped)
            verb_count = _count_verbatim(scoped)
            del scoped
            rows.append({"filing_date": pd.to_datetime(date_str, format="%Y%m%d"),
                         "filing_type": ftype, "cik": int(cik),
                         "prox_count": prox_count, "verb_count": verb_count})
            if i % 1500 == 0:
                print(f"  …{i:,}/{len(infos):,} (secfail {n_secfail:,}, "
                      f"{time.time()-t0:.0f}s)")

    f = pd.DataFrame(rows)
    print(f"\nparsed {len(f):,} filings WITH §1+7 (dirs {n_dir}, "
          f"badname {n_badname}, decerr {n_decerr}, §1+7-fail {n_secfail:,}) "
          f"{time.time()-t0:.0f}s")

    # Comparison: how many shift classification?
    f = f.sort_values(["cik", "filing_date"], kind="stable").drop_duplicates("cik", keep="last")
    print(f"after CIK dedupe: {len(f):,} CIKs")

    # Per-CIK classification comparison
    f["verb_group"] = "_excl"
    f.loc[f["verb_count"] == 0, "verb_group"] = "control"
    f.loc[f["verb_count"] > HIGH_T, "verb_group"] = "treated"
    f["prox_group"] = "_excl"
    f.loc[f["prox_count"] == 0, "prox_group"] = "control"
    f.loc[f["prox_count"] > HIGH_T, "prox_group"] = "treated"

    vT = int((f["verb_group"] == "treated").sum())
    vC = int((f["verb_group"] == "control").sum())
    pT = int((f["prox_group"] == "treated").sum())
    pC = int((f["prox_group"] == "control").sum())

    print(f"\n  Per-CIK (before GVKEY merge):")
    print(f"    Verbatim 9-kw:  T={vT:,}  C={vC:,}")
    print(f"    Proximity rule:  T={pT:,}  C={pC:,}")
    print(f"    Shift T→excl: {vT - pT:,}  C→excl: {vC - pC:,}")

    # CIK→GVKEY merge
    ccm = _load_ccm()
    mg = f.merge(ccm, on="cik", how="left")
    ok = ((mg["filing_date"] >= mg["LINKDT"])
          & (mg["filing_date"] <= mg["LINKENDDT"]))
    mp = (mg[ok].sort_values(["cik", "LINKDT"], kind="stable")
              .drop_duplicates("cik", keep="first"))
    n_unmapped = f["cik"].nunique() - mp["cik"].nunique()
    print(f"\n  CIK→gvkey: mapped {mp['cik'].nunique():,}, unmapped {n_unmapped:,}")

    # Aggregate by GVKEY
    for cnt_col, grp_col in [("prox_count", "prox_group"),
                              ("verb_count", "verb_group")]:
        g = mp.groupby("gvkey", as_index=False)[cnt_col].sum()
        g["group"] = "_excl"
        g.loc[g[cnt_col] == 0, "group"] = "control"
        g.loc[g[cnt_col] > HIGH_T, "group"] = "treated"
        g["HIGH_UK_EXPOSURE"] = g["group"].map(
            {"treated": 1.0, "control": 0.0}).astype("float64")
        nT = int((g["group"] == "treated").sum())
        nC = int((g["group"] == "control").sum())
        print(f"  {grp_col} (by GVKEY): T={nT:,}  C={nC:,}  excl={int((g['group']=='_excl').sum()):,}")

    # Build both treatment DataFrames for DiD
    g_prox = mp.groupby("gvkey", as_index=False)["prox_count"].sum()
    g_prox["group"] = "_excl"
    g_prox.loc[g_prox["prox_count"] == 0, "group"] = "control"
    g_prox.loc[g_prox["prox_count"] > HIGH_T, "group"] = "treated"
    g_prox["HIGH_UK_EXPOSURE"] = g_prox["group"].map(
        {"treated": 1.0, "control": 0.0}).astype("float64")
    g_prox = g_prox[g_prox["group"].isin(["treated", "control"])]

    g_verb = mp.groupby("gvkey", as_index=False)["verb_count"].sum()
    g_verb["group"] = "_excl"
    g_verb.loc[g_verb["verb_count"] == 0, "group"] = "control"
    g_verb.loc[g_verb["verb_count"] > HIGH_T, "group"] = "treated"
    g_verb["HIGH_UK_EXPOSURE"] = g_verb["group"].map(
        {"treated": 1.0, "control": 0.0}).astype("float64")
    g_verb = g_verb[g_verb["group"].isin(["treated", "control"])]

    return g_prox, g_verb, n_unmapped


# ── T8 DV BUILDER ──────────────────────────────────────────────────────

def _cash_dv_t8() -> pd.DataFrame:
    """T8 DV: CASH = cheq_t / (atq_{t-1} - cheq_{t-1})"""
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc",
                       "consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD") & (df["loc"]=="USA") & (df["consol"]=="C")
            & (df["indfmt"]=="INDL") & (df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year*10+df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(
        columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & (df["denom"]>0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH"]]


# ── DiD RUNNER ─────────────────────────────────────────────────────────

def run_did(treatment_df, label: str):
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    tt = treatment_df.copy()
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    nT = int((tt["HIGH_UK_EXPOSURE"]==1).sum())
    nC = int((tt["HIGH_UK_EXPOSURE"]==0).sum())

    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_cash_dv_t8(), on=["gvkey","cal_yr_qtr"], how="inner")
    df = df[df["atq"]>0].copy()
    df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls)
        col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(
        df[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(
        columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    df = df.merge(_statsum_meanest_z(), on=["gvkey","cal_yr_qtr"], how="left")

    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(WINSOR), s.quantile(1-WINSOR)))
    df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          +"_"+df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH","indqtr_code"]+cols).copy()
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()

    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)
    b = float(res.params["POST_x_HIGH"])
    se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"])
    p = float(res.pvalues["POST_x_HIGH"])
    cash_mean = float(sub["CASH"].mean())
    cash_sd = float(sub["CASH"].std())
    nT_est = int(sub[sub["HIGH_UK_EXPOSURE"]==1]["gvkey"].nunique())
    nC_est = int(sub[sub["HIGH_UK_EXPOSURE"]==0]["gvkey"].nunique())

    return {"label": label, "nT_treat": nT, "nC_treat": nC,
            "nT_est": nT_est, "nC_est": nC_est,
            "delta": b, "se": se, "t": t, "p": p,
            "nobs": int(res.nobs), "nfirms": int(nf),
            "r2w": float(res.rsquared_within),
            "cash_mean": cash_mean, "cash_sd": cash_sd}


# ── MAIN ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("="*72)
    print("TASK 16: Proximity-scoped keyword recount + T8 DiD")
    print("="*72)

    g_prox, g_verb, n_unmapped = build_treatment()

    print(f"\n{'='*72}")
    print("T8 DiD COMPARISON")
    print(f"{'='*72}")

    results = []

    print("\n── Proximity-scoped treatment ──")
    r = run_did(g_prox, "§1+7 proximity")
    results.append(r)
    print(f"  treatment: T={r['nT_treat']:,} C={r['nC_treat']:,}")
    print(f"  estimation: T={r['nT_est']:,} C={r['nC_est']:,}")
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}  CASH_μ={r['cash_mean']:.4f}  "
          f"σ={r['cash_sd']:.4f}")

    print("\n── Verbatim 9-kw treatment (same-CIK-set comparison) ──")
    r = run_did(g_verb, "§1+7 verbatim (this run)")
    results.append(r)
    print(f"  treatment: T={r['nT_treat']:,} C={r['nC_treat']:,}")
    print(f"  estimation: T={r['nT_est']:,} C={r['nC_est']:,}")
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}  CASH_μ={r['cash_mean']:.4f}  "
          f"σ={r['cash_sd']:.4f}")

    print(f"\n{'='*72}")
    print("SIDE-BY-SIDE")
    print(f"{'='*72}")
    print(f"{'Variant':<30} {'T(treat)':>8} {'C(treat)':>8} {'δ':>10} {'SE':>8} {'t':>7} {'p':>7} {'N':>8} {'firms':>6} {'R²w':>6}")
    print("-"*105)
    for r in results:
        print(f"{r['label']:<30} {r['nT_treat']:>8,} {r['nC_treat']:>8,} "
              f"{r['delta']:>+10.5f} {r['se']:>8.5f} {r['t']:>+7.3f} "
              f"{r['p']:>7.4f} {r['nobs']:>8,} {r['nfirms']:>6,} {r['r2w']:>6.4f}")
    print(f"{'Paper (T8 col.2)':<30} {807:>8} {433:>8} {+0.357:>+10.3f} {0.062:>8.3f} {'?':>7} {'***':>7} {24195:>8,} {'?':>6} {0.24:>6.2f}")

    # Save
    od = ROOT / "outputs" / "campello_rebuild" / "_diag_t16"
    od.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (od / f"results_{ts}.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\nwritten → {od / f'results_{ts}.json'}")
