"""Phase 3: Variable construction — Compustat-based variables.

Each variable built verbatim from campello_variable_lockin.md.
Winsorized 1%/99% by cal_yr_qtr (per paper).
Summary stats compared against Table 1 Panel A anchor.

Compustat-sourced variables (built here):
  - INVESTMENT      (VAR_01): capxy_q / atq_lag1
  - R&D             (VAR_03): xrdy_q  / atq_lag1   (only firms with non-missing R&D)
  - DIVESTITURES    (VAR_04): sppey_q / atq_lag1   (printed ×100; stored as ratio)
  - CASH            (VAR_05): cheq / atq_lag1      (Table 1 def; user override)
  - NWC             (VAR_06): (actq − lctq − cheq) / atq_lag1
  - TOBIN_Q         (VAR_70-73): (cshoq*prccq + atq − ceqq + txditcq) / atq
  - CASH_FLOW       (VAR_39): oibdpq_q / atq_lag1
  - SIZE            (VAR_40): log(atq)
  - SALES_GROWTH    (VAR_41): (saleq − saleq_{t-4}) / |saleq_{t-4}|

Deferred (external data sources):
  - EMPLOYMENT_GROWTH (VAR_02 — Compustat Annual + YTS)
  - STOCK_RETURNS     (VAR_43 — CRSP)
  - CONSENSUS_EPS     (VAR_42 — I/B/E/S)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _load_anchor(root_path: Path) -> dict:
    anchor_path = root_path / "tmp" / "campello_table1_anchor_2026_05_26.json"
    with open(anchor_path) as f:
        return json.load(f)["A"]


def _de_cumulate_ytd(df: pd.DataFrame, col: str) -> pd.Series:
    """De-cumulate YTD field to quarterly: Q1=raw, Qn=raw−raw_{n−1} within (gvkey,fyearq)."""
    df = df.sort_values(["gvkey", "datadate"])
    out = pd.Series(np.nan, index=df.index, dtype="float64")
    for (_gvkey, _fy), grp in df.groupby(["gvkey", "fyearq"], dropna=False):
        if grp["fyearq"].isna().all():
            continue
        grp = grp.sort_values("fqtr")
        prev = grp[col].shift(1)
        is_q1 = grp["fqtr"] == 1
        out.loc[grp.index] = np.where(is_q1, grp[col], grp[col] - prev)
    return out


def _winsorize(df: pd.DataFrame, col: str) -> pd.Series:
    """Winsorize at 1%/99% within each cal_yr_qtr group."""
    out = pd.Series(np.nan, index=df.index, dtype="float64")
    for _qtr, idx in df.groupby("cal_yr_qtr").groups.items():
        vals = df.loc[idx, col]
        valid = vals.notna()
        if valid.sum() < 10:
            out.loc[idx] = vals
            continue
        lo, hi = vals[valid].quantile(0.01), vals[valid].quantile(0.99)
        out.loc[idx] = vals.clip(lower=lo, upper=hi)
    return out


def _load_compustat_raw(root_path: Path, gvkeys, mindate, maxdate) -> pd.DataFrame:
    extra_cols = ["gvkey", "datadate", "fyearq", "fqtr",
                  "ceqq", "txditcq", "oibdpq", "capxy", "saleq",
                  "cshoq", "prccq", "cheq", "atq",
                  "xrdy", "sppey", "actq", "lctq"]
    parquet_path = root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    comp = pd.read_parquet(parquet_path, columns=extra_cols)
    comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
    comp["datadate"] = pd.to_datetime(comp["datadate"])
    for c in extra_cols:
        if c not in ("gvkey", "datadate"):
            comp[c] = pd.to_numeric(comp[c], errors="coerce").astype("float64")
    comp = comp[comp["gvkey"].isin(gvkeys)]
    comp = comp[(comp["datadate"] >= mindate) & (comp["datadate"] <= maxdate)]
    comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")
    return comp


def build_variables(root_path: Path, sample_panel: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    if sample_panel is None:
        out_root = root_path / "outputs" / "campello_v2"
        runs = sorted([d for d in out_root.iterdir() if d.is_dir() and (d / "sample_panel.parquet").exists()], reverse=True)
        if not runs:
            raise FileNotFoundError("No sample panel found. Run sample.py first.")
        sample_path = runs[0] / "sample_panel.parquet"
        logger.info("Loading sample from %s", sample_path)
        panel = pd.read_parquet(sample_path)
    else:
        panel = sample_panel.copy()

    anchor = _load_anchor(root_path)

    # ---- merge extra Compustat columns ----
    comp_raw = _load_compustat_raw(
        root_path, panel["gvkey"].unique(),
        panel["datadate"].min(), panel["datadate"].max()
    )
    extra_cols = ["gvkey", "datadate", "fyearq", "fqtr",
                  "ceqq", "txditcq", "oibdpq", "capxy", "saleq",
                  "cshoq", "prccq", "cheq", "atq",
                  "xrdy", "sppey", "actq", "lctq"]
    merge_cols = ["gvkey", "datadate"] + [c for c in extra_cols
                  if c not in panel.columns and c not in ("gvkey", "datadate")]
    panel = panel.merge(
        comp_raw[merge_cols],
        on=["gvkey", "datadate"], how="left", validate="1:1"
    )
    panel = panel.sort_values(["gvkey", "cal_yr_qtr"]).reset_index(drop=True)

    # ---- 1. CASH = cheq / atq_lag1 (Table 1 def) ----
    panel["CASH"] = np.where(
        panel["atq_lag1"].notna() & (panel["atq_lag1"] > 0),
        panel["cheq"] / panel["atq_lag1"],
        np.nan,
    )
    panel["CASH"] = panel["CASH"].replace([np.inf, -np.inf], np.nan)
    panel["CASH"] = _winsorize(panel, "CASH")

    # ---- 2. INVESTMENT = capxy_q / atq_lag1 ----
    panel["_capxy_q"] = _de_cumulate_ytd(panel, "capxy")
    panel["INVESTMENT"] = np.where(
        panel["atq_lag1"].notna() & (panel["atq_lag1"] > 0),
        panel["_capxy_q"] / panel["atq_lag1"],
        np.nan,
    )
    panel["INVESTMENT"] = panel["INVESTMENT"].replace([np.inf, -np.inf], np.nan)
    panel["INVESTMENT"] = _winsorize(panel, "INVESTMENT")

    # ---- 3. R&D = xrdy_q / atq_lag1  (only firms with non-missing R&D) ----
    panel["_xrdy_q"] = _de_cumulate_ytd(panel, "xrdy")
    panel["RD"] = np.where(
        panel["atq_lag1"].notna() & (panel["atq_lag1"] > 0) & panel["_xrdy_q"].notna(),
        panel["_xrdy_q"] / panel["atq_lag1"],
        np.nan,
    )
    panel["RD"] = panel["RD"].replace([np.inf, -np.inf], np.nan)
    panel["RD"] = _winsorize(panel, "RD")

    # ---- 4. DIVESTITURES = sppey_q / atq_lag1  (ratio; ×100 only for display) ----
    panel["_sppey_q"] = _de_cumulate_ytd(panel, "sppey")
    # SPPE missing typically means zero sales of PPE → impute 0
    panel["_sppey_q"] = panel["_sppey_q"].fillna(0)
    panel["DIVESTITURES"] = np.where(
        panel["atq_lag1"].notna() & (panel["atq_lag1"] > 0),
        panel["_sppey_q"] / panel["atq_lag1"],
        np.nan,
    )
    panel["DIVESTITURES"] = panel["DIVESTITURES"].replace([np.inf, -np.inf], np.nan)
    panel["DIVESTITURES"] = _winsorize(panel, "DIVESTITURES")

    # ---- 5. NWC = (actq − lctq − cheq) / atq_lag1 ----
    panel["NWC"] = np.where(
        panel["atq_lag1"].notna() & (panel["atq_lag1"] > 0)
        & panel["actq"].notna() & panel["lctq"].notna() & panel["cheq"].notna(),
        (panel["actq"] - panel["lctq"] - panel["cheq"]) / panel["atq_lag1"],
        np.nan,
    )
    panel["NWC"] = panel["NWC"].replace([np.inf, -np.inf], np.nan)
    panel["NWC"] = _winsorize(panel, "NWC")

    # ---- 6. TOBIN_Q = (cshoq*prccq + atq − ceqq + txditcq) / atq ----
    panel["txditcq"] = panel["txditcq"].fillna(0)
    panel["TOBIN_Q"] = np.where(
        panel["atq"].notna() & (panel["atq"] > 0),
        (panel["cshoq"] * panel["prccq"] + panel["atq"] - panel["ceqq"] + panel["txditcq"]) / panel["atq"],
        np.nan,
    )
    panel["TOBIN_Q"] = panel["TOBIN_Q"].replace([np.inf, -np.inf], np.nan)
    panel["TOBIN_Q"] = _winsorize(panel, "TOBIN_Q")

    # ---- 7. CASH_FLOW = oibdpq / atq_lag1 ----
    # FIX 2026-05-26: oibdpq is QUARTERLY in Compustat (not YTD). Do NOT de-cumulate.
    panel["CASH_FLOW"] = np.where(
        panel["atq_lag1"].notna() & (panel["atq_lag1"] > 0),
        panel["oibdpq"] / panel["atq_lag1"],
        np.nan,
    )
    panel["CASH_FLOW"] = panel["CASH_FLOW"].replace([np.inf, -np.inf], np.nan)
    panel["CASH_FLOW"] = _winsorize(panel, "CASH_FLOW")

    # ---- 8. SIZE = log(atq) ----
    panel["SIZE"] = np.where(panel["atq"] > 0, np.log(panel["atq"]), np.nan)
    panel["SIZE"] = _winsorize(panel, "SIZE")

    # ---- 9. SALES_GROWTH = (saleq − saleq_{t−4}) / |saleq_{t−4}| ----
    panel["_saleq_lag4"] = panel.groupby("gvkey")["saleq"].shift(4)
    panel["SALES_GROWTH"] = np.where(
        panel["_saleq_lag4"].notna() & (panel["_saleq_lag4"].abs() > 0),
        (panel["saleq"] - panel["_saleq_lag4"]) / panel["_saleq_lag4"].abs(),
        np.nan,
    )
    panel["SALES_GROWTH"] = panel["SALES_GROWTH"].replace([np.inf, -np.inf], np.nan)
    panel["SALES_GROWTH"] = _winsorize(panel, "SALES_GROWTH")

    # ---- compare against anchor ----
    print("\n--- Variable comparison vs Table 1 Panel A (PyMuPDF anchor) ---")
    print(f"{'Variable':<28} {'N (mine/anchor)':<22} {'mean (mine/anchor)':<26} {'sd':<22} {'p50':<22}")
    print("-" * 130)
    _check("INVESTMENT",                  panel["INVESTMENT"], anchor)
    _check("R&D",                         panel["RD"], anchor)
    _check("DIVESTITURES (100)",          panel["DIVESTITURES"], anchor, display_mult=100)
    _check("CASH",                        panel["CASH"], anchor)
    _check("NON_CASH_WORKING_CAPITAL",    panel["NWC"], anchor)
    _check("TOBIN_Q",                     panel["TOBIN_Q"], anchor)
    _check("CASH_FLOW",                   panel["CASH_FLOW"], anchor)
    _check("SIZE (Log Assets)",           panel["SIZE"], anchor)
    _check("SALES_GROWTH",                panel["SALES_GROWTH"], anchor)

    # ---- save ----
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = root_path / "outputs" / "campello_v2" / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    out_cols = ["gvkey", "datadate", "cal_yr", "cal_qtr", "cal_yr_qtr",
                "sic", "atq", "mktcap", "atq_lag1",
                "CASH", "INVESTMENT", "RD", "DIVESTITURES", "NWC",
                "TOBIN_Q", "CASH_FLOW", "SIZE", "SALES_GROWTH"]
    out = panel[out_cols].copy()
    out_path = out_dir / "variables_panel.parquet"
    out.to_parquet(out_path, index=False)
    logger.info("Saved variables panel to %s", out_path)

    return out


def _check(label: str, series: pd.Series, anchor: Dict, display_mult: float = 1.0) -> None:
    """Compare variable stats against Table 1 anchor.

    Threshold logic: paper reports 2-decimal precision (e.g., 0.01) → implicit
    rounding tolerance ±0.005. For small anchors (<0.5), compare absolute diff;
    for large anchors, compare percent diff.
    """
    s = series.dropna() * display_mult
    bench = anchor.get(label, {})
    bench_n = int(bench.get("N", "0").replace(",", ""))
    bench_mean = float(bench.get("mean", "0"))
    bench_sd = float(bench.get("SD", "0"))
    bench_p50 = float(bench.get("median", "0"))

    def _flag(mine, anchor_val):
        diff = abs(mine - anchor_val)
        if abs(anchor_val) < 0.5:
            # Small anchor: absolute-diff comparison
            return "OK" if diff <= 0.01 else ("WARN" if diff <= 0.03 else "FAIL")
        else:
            pct = diff / abs(anchor_val) * 100
            return "OK" if pct < 10 else ("WARN" if pct < 25 else "FAIL")

    print(
        f"{label:<28} "
        f"{f'{len(s):,}/{bench_n:,}':<22} "
        f"{f'{s.mean():.3f}/{bench_mean:.2f} {_flag(s.mean(), bench_mean)}':<26} "
        f"{f'{s.std():.3f}/{bench_sd:.2f} {_flag(s.std(), bench_sd)}':<22} "
        f"{f'{s.median():.3f}/{bench_p50:.2f} {_flag(s.median(), bench_p50)}':<22}"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    rp = Path(__file__).resolve().parent.parent.parent.parent
    build_variables(rp)
