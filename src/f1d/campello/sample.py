"""Phase 1: Sample construction — Table C.1 filters 1–7.

Filters verbatim from Campello et al. (2022) Supplementary Table C.1:

  Filter                                     Firm-Quarters  (paper)
  ─────────────────────────────────────────────────────────────────
  1. Raw COMPUSTAT 2010:Q1–2016:Q4           262,412
  2. Drop non-US (USD, US HQ, no dups)        160,254
  3. Drop negative fundamentals (ASSETS, SALES) 158,312
  4. Drop financials & utilities              112,939
  5. Drop ASSETS or MARKET_CAP < $10M          93,011
  6. Drop missing key vars (INV, AT, CF, Q, SG) 75,013
  7. Drop non-consecutive / <12 quarters       56,081
  ─────────────────────────────────────────────────────────────────
  8. Drop missing FIC 100                      49,107  (deferred)
  9. Drop missing β^UK                         43,025  (deferred)
  10. Drop missing CRSP & IBES controls        41,630  (deferred)

Filters 8–10 require external data (FIC 100, CRSP, IBES).
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

SAMPLE_START = pd.Timestamp("2010-01-01")
SAMPLE_END = pd.Timestamp("2016-12-31")
MIN_ASSETS_M = 10
MIN_MKTCAP_M = 10

COMPUSTAT_COLS = [
    "gvkey", "datadate", "fyearq", "fqtr", "sic",
    "curcdq", "loc", "consol", "indfmt", "datafmt",
    "atq", "cshoq", "prccq", "cheq",
    # filter 3: saleq for SALES
    "saleq",
    # filter 6 key vars: capxy (INV), oibdpq (CF), ceqq+txditcq (TOBIN_Q)
    "capxy", "oibdpq", "ceqq", "txditcq",
]


def _de_cumulate_ytd(df: pd.DataFrame, col: str) -> pd.Series:
    """De-cumulate a YTD-compounded Compustat field to quarterly.

    Within each (gvkey, fyearq): Q1 = raw, Qn = raw - raw_{n-1}.
    Rows where fqtr changes across fiscal years are handled correctly
    by grouping on fyearq.
    """
    df = df.sort_values(["gvkey", "datadate"])
    result = pd.Series(np.nan, index=df.index, name=f"{col}_q")
    for (_gvkey, fy), grp in df.groupby(["gvkey", "fyearq"], dropna=False):
        if grp["fyearq"].isna().all():
            continue
        grp = grp.sort_values("fqtr")
        prev = grp[col].shift(1)
        is_q1 = grp["fqtr"] == 1
        result.loc[grp.index] = np.where(is_q1, grp[col], grp[col] - prev)
    return result


def _compute_lagged_assets(df: pd.DataFrame) -> pd.Series:
    """Compute atq lagged 1 quarter, validated as consecutive."""
    df = df.sort_values(["gvkey", "datadate"])
    lag = df.groupby("gvkey")["atq"].shift(1)
    lag_date = df.groupby("gvkey")["datadate"].shift(1)
    gap = (df["datadate"] - lag_date).dt.days
    # invalidate if gap not in [45, 135] days (~1 quarter ± buffer)
    lag = lag.where((gap >= 45) & (gap <= 135), np.nan)
    return pd.Series(lag.values, index=df.index, name="atq_lag1")


def _find_longest_consecutive_run(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the longest consecutive cal_yr_qtr run per firm.

    Drops firms with longest run < 12 quarters.
    """
    df = df.sort_values(["gvkey", "cal_yr_qtr"])
    df["_next_qtr"] = df.groupby("gvkey")["cal_yr_qtr"].shift(-1)
    # cal_yr_qtr = year*10 + quarter; next consecutive is +1
    # handle year boundary: 20104 + 1 = 20105 which is wrong (should be 20111)
    def _next_qtr(q):
        yr = q // 10
        qtr = q % 10
        new_qtr = qtr + 1
        new_yr = yr + (new_qtr > 4)
        return new_yr * 10 + (new_qtr if new_qtr <= 4 else 1)
    _next_qtr_vec = np.vectorize(_next_qtr)
    df["_expected_next"] = _next_qtr_vec(df["cal_yr_qtr"].astype(int).values)
    df["_is_break"] = df["_next_qtr"] != df["_expected_next"]

    # assign run IDs per firm
    df["_run_id"] = df.groupby("gvkey")["_is_break"].transform(
        lambda x: x.shift(1).fillna(False).cumsum()
    )

    # find best run per firm: longest, then latest (highest run_id) as tiebreaker
    run_sizes = df.groupby(["gvkey", "_run_id"]).size().reset_index(name="_size")
    # per gvkey, pick largest _size; tiebreak on largest _run_id
    best = run_sizes.sort_values(["_size", "_run_id"], ascending=[False, False])
    best = best.drop_duplicates(subset=["gvkey"], keep="first")
    best = best.set_index("gvkey")

    # filter to best runs
    result_rows = []
    for gvkey, grp in df.groupby("gvkey"):
        if gvkey in best.index:
            best_run = best.loc[gvkey, "_run_id"]
            best_size = best.loc[gvkey, "_size"]
            if best_size >= 12:
                result_rows.append(grp[grp["_run_id"] == best_run])

    if not result_rows:
        return pd.DataFrame(columns=df.columns)

    result = pd.concat(result_rows, ignore_index=True)
    result = result.drop(columns=["_next_qtr", "_expected_next", "_is_break", "_run_id"])
    return result


def build_sample(root_path: Path) -> pd.DataFrame:
    """Apply Table C.1 filters 1–7 and return cleaned sample panel.

    Logs N at each step against paper benchmark.
    """
    parquet_path = (
        root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    )
    logger.info("Loading COMPUSTAT Quarterly from %s", parquet_path.name)
    comp = pd.read_parquet(parquet_path, columns=COMPUSTAT_COLS)

    # ---- type coercion ----
    comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
    comp["datadate"] = pd.to_datetime(comp["datadate"])
    numeric_cols = ["atq", "cshoq", "prccq", "cheq", "sic",
                    "saleq", "capxy", "oibdpq", "ceqq", "txditcq"]
    for col in numeric_cols:
        comp[col] = pd.to_numeric(comp[col], errors="coerce").astype("float64")

    BENCH = {1: 262412, 2: 160254, 3: 158312, 4: 112939,
             5: 93011, 6: 75013, 7: 56081}

    # ---- Filter 1: Raw 2010Q1–2016Q4 ----
    comp = comp[
        (comp["datadate"] >= SAMPLE_START) & (comp["datadate"] <= SAMPLE_END)
    ].copy()
    logger.info("  F1 Raw 2010Q1–2016Q4: %s  (paper: %s)", f"{len(comp):,}", f"{BENCH[1]:,}")

    # ---- Filter 2: Drop non-US (USD, US HQ, duplicates excluded) ----
    comp = comp[
        comp["curcdq"].eq("USD") & comp["loc"].eq("USA")
        & comp["consol"].eq("C") & comp["indfmt"].eq("INDL")
        & comp["datafmt"].eq("STD")
    ].copy()
    # "duplicates excluded" — drop duplicate (gvkey, datadate)
    comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")
    logger.info("  F2 Drop non-US: %s  (paper: %s)", f"{len(comp):,}", f"{BENCH[2]:,}")

    # ---- calendar year-quarter ----
    comp["cal_yr"] = comp["datadate"].dt.year.astype("Int64")
    comp["cal_qtr"] = comp["datadate"].dt.quarter.astype("Int64")
    comp["cal_yr_qtr"] = (
        comp["cal_yr"].astype(int) * 10 + comp["cal_qtr"].astype(int)
    ).astype("Int64")

    # ---- Filter 3: Drop negative fundamentals (ASSETS, SALES) ----
    # "negative" means explicitly ≤ 0, NOT missing. NaN is kept here
    # (drops later at F6 if still missing when key vars are needed).
    neg_atq = comp["atq"].notna() & (comp["atq"] <= 0)
    neg_saleq = comp["saleq"].notna() & (comp["saleq"] <= 0)
    comp = comp[~(neg_atq | neg_saleq)].copy()
    logger.info("  F3 Drop negative fundamentals: %s  (paper: %s)", f"{len(comp):,}", f"{BENCH[3]:,}")

    # ---- Filter 4: Drop financials & utilities ----
    sic = comp["sic"]
    is_utility = (sic >= 4900) & (sic <= 4999)
    is_financial = (sic >= 6000) & (sic <= 6799)
    comp = comp[~(is_utility | is_financial)].copy()
    logger.info("  F4 Drop fin/utility: %s  (paper: %s)", f"{len(comp):,}", f"{BENCH[4]:,}")

    # ---- Filter 5: Drop ASSETS or MARKET_CAP < $10M ----
    # NaN passes (paper drops only confirmed < $10M, not missing)
    comp["mktcap"] = comp["cshoq"] * comp["prccq"]
    drop_mc = comp["mktcap"].notna() & (comp["mktcap"] < MIN_MKTCAP_M)
    drop_at = comp["atq"].notna() & (comp["atq"] < MIN_ASSETS_M)
    comp = comp[~(drop_mc | drop_at)].copy()
    logger.info("  F5 Drop <$10M: %s  (paper: %s)", f"{len(comp):,}", f"{BENCH[5]:,}")

    # ---- deduplicate (gvkey, cal_yr_qtr) — keep last datadate ----
    comp = comp.sort_values(["gvkey", "cal_yr_qtr", "datadate"])
    comp = comp.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="last")

    # ---- Filter 6: Drop missing key variables ----
    # Compute lagged assets first (needed for INVESTMENT and CASH_FLOW)
    comp["atq_lag1"] = _compute_lagged_assets(comp)

    # INVESTMENT = quarterly capxy / atq_lag1
    comp["_capxy_q"] = _de_cumulate_ytd(comp, "capxy")
    comp["INVESTMENT"] = np.where(
        comp["atq_lag1"].notna() & (comp["atq_lag1"] > 0),
        comp["_capxy_q"] / comp["atq_lag1"],
        np.nan,
    )

    # CASH_FLOW = oibdpq / atq_lag1  (oibdpq is QUARTERLY, not YTD)
    comp["CASH_FLOW"] = np.where(
        comp["atq_lag1"].notna() & (comp["atq_lag1"] > 0),
        comp["oibdpq"] / comp["atq_lag1"],
        np.nan,
    )

    # TOBIN_Q = (cshoq*prccq + atq - ceqq + txditcq) / atq
    comp["txditcq"] = comp["txditcq"].fillna(0)
    comp["TOBIN_Q"] = np.where(
        comp["atq"].notna() & (comp["atq"] > 0),
        (comp["cshoq"] * comp["prccq"] + comp["atq"]
         - comp["ceqq"] + comp["txditcq"]) / comp["atq"],
        np.nan,
    )

    # SALES_GROWTH = YoY % change in quarterly sales (saleq / saleq_{t-4} - 1)
    comp = comp.sort_values(["gvkey", "cal_yr_qtr"])
    comp["_saleq_lag4"] = comp.groupby("gvkey")["saleq"].shift(4)
    comp["SALES_GROWTH"] = np.where(
        comp["_saleq_lag4"].notna() & (comp["_saleq_lag4"].abs() > 0),
        (comp["saleq"] - comp["_saleq_lag4"]) / comp["_saleq_lag4"].abs(),
        np.nan,
    )

    key_vars = ["INVESTMENT", "atq", "CASH_FLOW", "TOBIN_Q"]
    comp = comp.dropna(subset=key_vars).copy()
    logger.info("  F6 Drop missing key vars: %s  (paper: %s)", f"{len(comp):,}", f"{BENCH[6]:,}")

    # ---- Filter 7: Drop non-consecutive / < 12 quarters ----
    comp = _find_longest_consecutive_run(comp)
    logger.info("  F7 Consecutive ≥12q: %s  (paper: %s)", f"{len(comp):,}", f"{BENCH[7]:,}")

    # ---- clean up temp columns ----
    comp = comp.drop(columns=["_capxy_q", "_oibdpq_q", "_saleq_lag4"], errors="ignore")
    comp = comp.sort_values(["gvkey", "cal_yr_qtr"]).reset_index(drop=True)

    logger.info("  Final: %s obs, %s firms", f"{len(comp):,}", f"{comp['gvkey'].nunique():,}")

    return comp


def build_and_save(root_path: Path | None = None) -> pd.DataFrame:
    """Build sample, save to outputs/, print summary stats."""
    if root_path is None:
        root_path = Path(__file__).resolve().parent.parent.parent.parent

    panel = build_sample(root_path)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = root_path / "outputs" / "campello_v2" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "sample_panel.parquet"
    panel.to_parquet(out_path, index=False)
    logger.info("Saved to %s", out_path)

    # ---- summary stats for key variables ----
    _print_summary_stats(panel)

    return panel


def _print_summary_stats(df: pd.DataFrame) -> None:
    """Print summary stats for Table 1 variables (post-filter 7, pre-winsorization)."""
    stats_vars = {
        "INVESTMENT": "INVESTMENT",
        "atq": "ASSETS",
        "CASH_FLOW": "CASH_FLOW",
        "TOBIN_Q": "TOBIN_Q",
        "SALES_GROWTH": "SALES_GROWTH",
        "mktcap": "MARKET_CAP",
        "cheq": "CASH (raw)",
        "saleq": "SALES (raw)",
    }
    print("\n--- Summary Statistics (post-filter 7, pre-winsorization) ---")
    for col, label in stats_vars.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if len(s) == 0:
            continue
        print(
            f"  {label:20s}: N={len(s):,}  mean={s.mean():.4f}  "
            f"sd={s.std():.4f}  p50={s.median():.4f}"
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    build_and_save()
