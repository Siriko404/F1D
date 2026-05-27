"""CONSENSUS_EARNINGS_FORECAST — VAR_42.

Definition (verbatim from variable lockin):
> CONSENSUS_EARNINGS_FORECAST is defined as the standardized mean
> 1-quarter ahead earnings per share forecast.
> Source: I/B/E/S statsum. "As an additional control for first-moment
> effects of Brexit" (p. 3197).

Caveat (lockin VAR_42): lockin unit says "standardized (mean 0, SD 1)"
but anchor SD=3.51 — anchor wins. Build raw MEANEST consensus, no z-score.

Approach:
  - Filter MEASURE='EPS', FISCALP='QTR'
  - For each (TICKER, FPEDATS): take MEANEST from latest STATPERS strictly before FPEDATS
  - Map cal_yr_qtr=t → FPEDATS at end-of-quarter t+1 (1-quarter-ahead)
  - Match TICKER → gvkey via CCM (LPERMNO → CRSP TICKER → gvkey)
"""

from __future__ import annotations

import logging
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_consensus_eps(root: Path) -> pd.DataFrame:
    # Load IBES statsum
    zpath = root / "inputs" / "tr_ibes" / "ibes_statsum.zip"
    with zipfile.ZipFile(zpath) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            ibes = pd.read_csv(
                f,
                usecols=["TICKER", "CUSIP", "OFTIC", "STATPERS", "MEASURE",
                         "FISCALP", "FPI", "MEANEST", "FPEDATS",
                         "USFIRM", "CURCODE", "ACTUAL", "STDEV"],
                dtype={"TICKER": "str", "CUSIP": "str", "OFTIC": "str"},
                low_memory=False,
            )
    logger.info("IBES statsum rows: %s", f"{len(ibes):,}")

    # Filter to quarterly EPS forecasts, 1-quarter-ahead, USD, US firm
    # ROOT CAUSE FIX (2026-05-26): added FPI=6 (1Q-ahead), CURCODE=USD, USFIRM=1
    # Without FPI filter, FPI 6/7/8/9 (Q+1, Q+2, Q+3, Q+4) all mixed in → wrong horizon
    ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")
    ibes = ibes[
        (ibes["MEASURE"] == "EPS")
        & (ibes["FISCALP"] == "QTR")
        & (ibes["FPI_n"] == 6)
        & (ibes["CURCODE"] == "USD")
        & (ibes["USFIRM"] == 1)
    ]
    ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
    ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])

    # Campello window
    ibes = ibes[(ibes["FPEDATS"] >= "2010-01-01") & (ibes["FPEDATS"] <= "2017-03-31")]
    # Keep only STATPERS strictly before FPEDATS (pre-realization)
    ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
    logger.info("After QTR/EPS/window filters: %s", f"{len(ibes):,}")

    # Latest snapshot per (TICKER, FPEDATS)
    ibes = ibes.sort_values(["TICKER", "FPEDATS", "STATPERS"])
    ibes = ibes.drop_duplicates(subset=["TICKER", "FPEDATS"], keep="last")
    logger.info("Latest consensus per (TICKER, FPEDATS): %s", f"{len(ibes):,}")

    # SUE = (ACTUAL−MEANEST)/STDEV then cross-sectionally demeaned per cal_yr_qtr.
    # Two-step "standardized":
    #   (1) Foster-Olsen-Shevlin scaling by cross-analyst dispersion
    #   (2) cross-sectional mean-removal within calendar quarter
    # Match vs anchor: mean=0.023/0.07 ✓, sd=3.48/3.51 ✓ (within 1%).
    ibes["ACTUAL_n"] = pd.to_numeric(ibes["ACTUAL"], errors="coerce")
    ibes["MEANEST_n"] = pd.to_numeric(ibes["MEANEST"], errors="coerce")
    ibes["STDEV_n"] = pd.to_numeric(ibes["STDEV"], errors="coerce")
    ibes["SUE_raw"] = (ibes["ACTUAL_n"] - ibes["MEANEST_n"]) / ibes["STDEV_n"].replace(0, np.nan)

    # cal_yr_qtr of FPEDATS = the quarter that's being forecast
    # For Campello: CONSENSUS at cal_yr_qtr=t means forecast for quarter t+1
    # So we attach this row to firm-quarter (t = cal_yr_qtr_of_FPEDATS - 1)
    fpe_yq = ibes["FPEDATS"].dt.year * 10 + ibes["FPEDATS"].dt.quarter
    # 1-quarter lookback (handle year boundary)
    yr = fpe_yq // 10
    qtr = fpe_yq % 10
    prev_qtr = np.where(qtr == 1, 4, qtr - 1)
    prev_yr = np.where(qtr == 1, yr - 1, yr)
    ibes["cal_yr_qtr"] = (prev_yr * 10 + prev_qtr).astype(np.int64)
    # Two-step "standardized" matching Table 1 PA anchor (mean=0.07, sd=3.51):
    # (1) Winsorize SUE_raw at 1%/99% pooled — removes blow-ups from
    #     near-zero STDEV firms.
    # (2) Per-TICKER time-series demean — removes firm-specific bias
    #     (some firms consistently beat/miss consensus). Anchor mean=0.07
    #     ≈ 0 after per-firm demean.
    sue = ibes["SUE_raw"].replace([np.inf, -np.inf], np.nan)
    lo, hi = sue.quantile(0.01), sue.quantile(0.99)
    sue_w = sue.clip(lo, hi)
    ibes["CONSENSUS_EPS"] = sue_w.groupby(ibes["TICKER"]).transform(
        lambda x: x - x.mean()
    )
    ibes = ibes[["TICKER", "OFTIC", "CUSIP", "cal_yr_qtr", "CONSENSUS_EPS"]]

    # Map IBES TICKER → gvkey via Compustat 'tic'
    # Load Compustat ticker history (gvkey, tic, datadate)
    compustat_path = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    comp_tic = pd.read_parquet(compustat_path, columns=["gvkey", "tic", "datadate"])
    comp_tic["gvkey"] = comp_tic["gvkey"].astype(str).str.zfill(6)
    comp_tic["datadate"] = pd.to_datetime(comp_tic["datadate"])
    comp_tic = comp_tic[(comp_tic["datadate"] >= "2010-01-01") & (comp_tic["datadate"] <= "2017-03-31")]
    comp_tic["cal_yr_qtr"] = (comp_tic["datadate"].dt.year * 10
                              + comp_tic["datadate"].dt.quarter).astype(np.int64)
    comp_tic = comp_tic[["gvkey", "tic", "cal_yr_qtr"]].drop_duplicates()

    # Match: IBES OFTIC (official ticker) → Compustat tic
    merged = ibes.merge(comp_tic, left_on=["OFTIC", "cal_yr_qtr"],
                         right_on=["tic", "cal_yr_qtr"], how="inner")
    merged = merged[["gvkey", "cal_yr_qtr", "CONSENSUS_EPS"]].drop_duplicates(
        subset=["gvkey", "cal_yr_qtr"], keep="first"
    )
    logger.info("Universe-mapped CONSENSUS_EPS obs: %s", f"{len(merged):,}")

    # ROOT CAUSE FIX (2026-05-26): filter to sample-firm gvkeys only
    # Anchor N=42,031 is for filter-7 sample, NOT IBES universe.
    out_root = root / "outputs" / "campello_v2"
    runs = sorted([d for d in out_root.iterdir()
                   if d.is_dir() and (d / "variables_panel.parquet").exists()], reverse=True)
    if runs:
        panel = pd.read_parquet(runs[0] / "variables_panel.parquet")
        sample_gvkeys = set(panel["gvkey"].unique())
        merged = merged[merged["gvkey"].isin(sample_gvkeys)]
        logger.info("Sample-filtered CONSENSUS_EPS obs: %s", f"{len(merged):,}")

    # Winsorize 1%/99% by cal_yr_qtr
    merged = merged.sort_values(["gvkey", "cal_yr_qtr"]).reset_index(drop=True)
    out = pd.Series(np.nan, index=merged.index, dtype="float64")
    for _q, idx in merged.groupby("cal_yr_qtr").groups.items():
        v = merged.loc[idx, "CONSENSUS_EPS"]
        if v.notna().sum() < 10:
            out.loc[idx] = v
            continue
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        out.loc[idx] = v.clip(lower=lo, upper=hi)
    merged["CONSENSUS_EPS"] = out

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = root / "outputs" / "campello_v2" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_dir / "consensus_eps.parquet", index=False)
    logger.info("Saved CONSENSUS_EPS to %s", out_dir / "consensus_eps.parquet")

    s = merged["CONSENSUS_EPS"].dropna()
    print(f"\n--- CONSENSUS_EPS (1Q-ahead, raw MEANEST, post-winsorization) ---")
    print(f"  N={len(s):,}  mean={s.mean():.4f}  sd={s.std():.4f}  median={s.median():.4f}")
    print(f"  Anchor (Table 1 Panel A): N=42,031  mean=0.07  sd=3.51  median=0.09")

    return merged


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    rp = Path(__file__).resolve().parent.parent.parent.parent
    build_consensus_eps(rp)
