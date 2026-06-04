"""Campello Table 1 summary stats — broad COMPUSTAT universe (filters 1-5).
Variable-by-variable available data, NOT restricted to estimation sample.
Writes tmp/campello_summary_stats_v2.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

from step7_fullpanel_hypothesis import _prev_q

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
WINSOR = 0.01
PRE_Q_LO, PRE_Q_HI = 20101, 20154  # Campello Table 1 window

# statsum consensus (same as locked econometric runner)
_p = ROOT / "scripts" / "campello_rebuild" / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p)
_fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin)
_statsum_meanest_z = _fin._statsum_meanest_z

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _load_compustat_universe() -> pd.DataFrame:
    """Compustat with Campello filters 1-5 applied. 2008+ buffer for lags."""
    cols = ["gvkey", "datadate", "curcdq", "loc", "consol", "indfmt",
            "datafmt", "sic", "atq", "saleq", "cheq", "oibdpq", "ceqq",
            "prccq", "cshoq"]
    df = pq.read_table(COMP, columns=cols).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= pd.Timestamp("2008-01-01"))
            & (df["datadate"] <= pd.Timestamp("2015-12-31"))]
    for c in ["atq", "saleq", "cheq", "oibdpq", "ceqq", "prccq", "cshoq"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["sic"] = pd.to_numeric(df["sic"], errors="coerce")

    # Filter 2: USD + US HQ + canonical screen + dedup
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA")
            & (df["consol"] == "C") & (df["indfmt"] == "INDL")
            & (df["datafmt"] == "STD")]
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10
                        + df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last").reset_index(drop=True)
    print(f"  Filter 2 (USD/USA/canon/dedup): {len(df):,} rows (buffer incl)")

    # Pre-window: keep only 2010Q1-2015Q4 for counting
    pre = df[(df["cal_yr_qtr"] >= PRE_Q_LO) & (df["cal_yr_qtr"] <= PRE_Q_HI)].copy()
    print(f"  Pre-treatment window (2010Q1-2015Q4): {len(pre):,} fq / "
          f"{pre['gvkey'].nunique():,} firms")

    # Filter 3: Drop negative ASSETS and SALES
    pre = pre[~((pre["atq"] < 0) | (pre["saleq"] < 0))]
    print(f"  Filter 3 (no negative fundamentals): {len(pre):,} fq / "
          f"{pre['gvkey'].nunique():,} firms")

    # Filter 4: Drop financials (6000-6999) and utilities (4900-4999)
    pre = pre[~(pre["sic"].between(6000, 6999) | pre["sic"].between(4900, 4999))]
    print(f"  Filter 4 (no fin/util): {len(pre):,} fq / "
          f"{pre['gvkey'].nunique():,} firms")

    # Filter 5: Drop ASSETS or MARKET_CAP < $10M
    pre["mktcap"] = pre["prccq"] * pre["cshoq"]
    pre = pre[~((pre["atq"] < 10) | (pre["mktcap"] < 10))]
    print(f"  Filter 5 (size >= $10M): {len(pre):,} fq / "
          f"{pre['gvkey'].nunique():,} firms")

    # Build lags on the FULL buffer frame (needed for CASH/CF/SG)
    base = df[["gvkey", "cal_yr_qtr", "atq", "saleq"]].copy()
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df["_pyq"] = df["cal_yr_qtr"].map(
        lambda yq: (yq // 10 - 1) * 10 + (yq % 10)).astype("int64")
    atq_src = base[["gvkey", "cal_yr_qtr", "atq"]].rename(
        columns={"cal_yr_qtr": "_pq", "atq": "atq_l1"})
    sal_src = base[["gvkey", "cal_yr_qtr", "saleq"]].rename(
        columns={"cal_yr_qtr": "_pyq", "saleq": "saleq_l4"})
    df = df.merge(atq_src, on=["gvkey", "_pq"], how="left")
    df = df.merge(sal_src, on=["gvkey", "_pyq"], how="left")
    df = df.drop(columns=["_pq", "_pyq"])

    # Keep only pre-treatment window for stats
    out = df[(df["cal_yr_qtr"] >= PRE_Q_LO)
             & (df["cal_yr_qtr"] <= PRE_Q_HI)].copy()
    # Re-apply filter 3-5 on the merged frame (lags may have introduced filtered rows)
    out = out[~((out["atq"] < 0) | (out["saleq"] < 0))]
    out = out[~(out["sic"].between(6000, 6999) | out["sic"].between(4900, 4999))]
    out["mktcap"] = out["prccq"] * out["cshoq"]
    out = out[~((out["atq"] < 10) | (out["mktcap"] < 10))]
    print(f"  Final universe (filters 1-5, pre-treatment): {len(out):,} fq / "
          f"{out['gvkey'].nunique():,} firms")
    return out


def _winsorize_within_qtr(s: pd.Series, cal_yr_qtr: pd.Series) -> pd.Series:
    """1% winsor within cal_yr_qtr. Returns winsorized series."""
    df = pd.DataFrame({"v": s, "q": cal_yr_qtr})
    return df.groupby("q", observed=True)["v"].transform(
        lambda x: x.clip(x.quantile(WINSOR), x.quantile(1 - WINSOR)))


def _stats(s: pd.Series, label: str) -> dict:
    """Compute mean/SD/med/IQR/N on non-missing winsorized values."""
    v = s.dropna()
    return {
        "mean": round(float(v.mean()), 4),
        "SD": round(float(v.std(ddof=1)), 4),
        "med": round(float(v.median()), 4),
        "IQR": round(float(v.quantile(0.75) - v.quantile(0.25)), 4),
        "N": int(len(v)),
    }


def main() -> None:
    print("=== Campello Table 1 summary stats — broad universe "
          "(filters 1-5, variable-by-variable) ===\n")

    uni = _load_compustat_universe()
    results = {}

    # --- CASH_T1 = cheq / atq_{t-1} (Campello Table 1 verbatim) ---
    mask_cash = (uni["cheq"].notna() & uni["atq_l1"].notna()
                 & (uni["atq_l1"] > 0))
    cash_sub = uni[mask_cash].copy()
    cash_sub["CASH_T1"] = cash_sub["cheq"] / cash_sub["atq_l1"]
    cash_sub["CASH_T1_w"] = _winsorize_within_qtr(
        cash_sub["CASH_T1"], cash_sub["cal_yr_qtr"])
    results["CASH_T1"] = _stats(cash_sub["CASH_T1_w"], "CASH_T1")
    print(f"  CASH_T1           mean={results['CASH_T1']['mean']:+.4f}  "
          f"SD={results['CASH_T1']['SD']:.4f}  N={results['CASH_T1']['N']:,}")

    # --- SIZE = ln(atq) ---
    mask_size = uni["atq"].notna() & (uni["atq"] > 0)
    size_sub = uni[mask_size].copy()
    size_sub["SIZE"] = np.log(size_sub["atq"])
    size_sub["SIZE_w"] = _winsorize_within_qtr(size_sub["SIZE"], size_sub["cal_yr_qtr"])
    results["SIZE"] = _stats(size_sub["SIZE_w"], "SIZE")
    print(f"  SIZE              mean={results['SIZE']['mean']:+.4f}  "
          f"SD={results['SIZE']['SD']:.4f}  N={results['SIZE']['N']:,}")

    # --- TOBIN_Q = (cshoq*prccq + atq - ceqq)/atq (audited: NO txditcq) ---
    mask_tq = (uni["cshoq"].notna() & uni["prccq"].notna() & uni["atq"].notna()
               & uni["ceqq"].notna() & (uni["atq"] > 0))
    tq_sub = uni[mask_tq].copy()
    tq_sub["TOBIN_Q"] = (tq_sub["cshoq"] * tq_sub["prccq"]
                         + tq_sub["atq"] - tq_sub["ceqq"]) / tq_sub["atq"]
    tq_sub["TOBIN_Q_w"] = _winsorize_within_qtr(
        tq_sub["TOBIN_Q"], tq_sub["cal_yr_qtr"])
    results["TOBIN_Q"] = _stats(tq_sub["TOBIN_Q_w"], "TOBIN_Q")
    print(f"  TOBIN_Q           mean={results['TOBIN_Q']['mean']:+.4f}  "
          f"SD={results['TOBIN_Q']['SD']:.4f}  N={results['TOBIN_Q']['N']:,}")

    # --- CASH_FLOW = oibdpq / atq_{t-1} ---
    mask_cf = (uni["oibdpq"].notna() & uni["atq_l1"].notna()
               & (uni["atq_l1"] > 0))
    cf_sub = uni[mask_cf].copy()
    cf_sub["CASH_FLOW"] = cf_sub["oibdpq"] / cf_sub["atq_l1"]
    cf_sub["CASH_FLOW_w"] = _winsorize_within_qtr(
        cf_sub["CASH_FLOW"], cf_sub["cal_yr_qtr"])
    results["CASH_FLOW"] = _stats(cf_sub["CASH_FLOW_w"], "CASH_FLOW")
    print(f"  CASH_FLOW         mean={results['CASH_FLOW']['mean']:+.4f}  "
          f"SD={results['CASH_FLOW']['SD']:.4f}  N={results['CASH_FLOW']['N']:,}")

    # --- SALES_GROWTH = (saleq - saleq_{t-4}) / saleq_{t-4} ---
    mask_sg = (uni["saleq"].notna() & uni["saleq_l4"].notna()
               & (uni["saleq_l4"] != 0))
    sg_sub = uni[mask_sg].copy()
    sg_sub["SALES_GROWTH"] = ((sg_sub["saleq"] - sg_sub["saleq_l4"])
                               / sg_sub["saleq_l4"])
    sg_sub["SALES_GROWTH_w"] = _winsorize_within_qtr(
        sg_sub["SALES_GROWTH"], sg_sub["cal_yr_qtr"])
    results["SALES_GROWTH"] = _stats(sg_sub["SALES_GROWTH_w"], "SALES_GROWTH")
    print(f"  SALES_GROWTH      mean={results['SALES_GROWTH']['mean']:+.4f}  "
          f"SD={results['SALES_GROWTH']['SD']:.4f}  N={results['SALES_GROWTH']['N']:,}")

    # --- STOCK_RETURNS via BrexitStockReturnBuilder ---
    from f1d.shared.variables.brexit_stock_return import BrexitStockReturnBuilder
    sret = BrexitStockReturnBuilder().build(range(2009, 2017), root_path=ROOT).data
    sret["gvkey"] = sret["gvkey"].astype(str).str.zfill(6)
    sret["cal_yr_qtr"] = sret["cal_yr_qtr"].astype("int64")
    # Merge with universe to restrict to same firm-quarter scope
    uni_gvkeys = set(uni["gvkey"].unique())
    sret = sret[sret["gvkey"].isin(uni_gvkeys)]
    sret = sret[(sret["cal_yr_qtr"] >= PRE_Q_LO)
                & (sret["cal_yr_qtr"] <= PRE_Q_HI)]
    col = [c for c in sret.columns if c not in ("gvkey", "cal_yr_qtr")][0]
    sret["STOCK_RETURNS_w"] = _winsorize_within_qtr(
        sret[col], sret["cal_yr_qtr"])
    results["STOCK_RETURNS"] = _stats(sret["STOCK_RETURNS_w"], "STOCK_RETURNS")
    print(f"  STOCK_RETURNS     mean={results['STOCK_RETURNS']['mean']:+.4f}  "
          f"SD={results['STOCK_RETURNS']['SD']:.4f}  N={results['STOCK_RETURNS']['N']:,}")

    # --- CONSENSUS_EPS via statsum MEANEST z-score ---
    cons = _statsum_meanest_z()
    cons = cons[(cons["cal_yr_qtr"] >= PRE_Q_LO)
                & (cons["cal_yr_qtr"] <= PRE_Q_HI)]
    cons_gvkeys = set(cons["gvkey"].unique())
    cons_uni = cons[cons["gvkey"].isin(uni_gvkeys)]
    # cons_fwd is already z-scored within-quarter — no additional winsor needed
    # (MEANEST is winsorized before z-scoring inside _statsum_meanest_z)
    v = cons_uni["cons_fwd"].dropna()
    results["CONSENSUS_EPS"] = {
        "mean": round(float(v.mean()), 4),
        "SD": round(float(v.std(ddof=1)), 4),
        "med": round(float(v.median()), 4),
        "IQR": round(float(v.quantile(0.75) - v.quantile(0.25)), 4),
        "N": int(len(v)),
    }
    print(f"  CONSENSUS_EPS     mean={results['CONSENSUS_EPS']['mean']:+.4f}  "
          f"SD={results['CONSENSUS_EPS']['SD']:.4f}  N={results['CONSENSUS_EPS']['N']:,}")

    # Write
    out_path = ROOT / "tmp" / "campello_summary_stats_v2.json"
    out_path.write_text(json.dumps({
        "source": "Compustat broad universe (filters 1-5, Campello Table 1 level)",
        "window": "2010Q1-2015Q4",
        "winsor": "1% within cal_yr_qtr (Campello convention)",
        "universe": (f"USD/USA/INDL/STD, no negative fundamentals, "
                     f"no fin/util, size>=$10M; variable-by-variable "
                     f"available data"),
        "cash_definition": "CASH_T1 = cheq_t / atq_{t-1} (Campello Table 1 verbatim)",
        "tobinq_definition": "TOBIN_Q = (cshoq*prccq + atq - ceqq)/atq (NO txditcq, "
                            "per audit commit 4253d97)",
        "consensus_definition": "statsum MEANEST z-score, within-quarter pooled",
        "variables": results,
    }, indent=2), encoding="utf-8")
    print(f"\n-> {out_path}")


if __name__ == "__main__":
    main()
