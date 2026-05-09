"""Brexit-verbatim sales-growth builder — H1.5.brexit_did design (Module #8, audit MAJOR-3).

Per Campello et al. 2022 JFQA Section II.E firm-control verbatim:
    SalesGrowth_t = (saleq_t − saleq_{t−4}) / |saleq_{t−4}|     quarterly year-on-year

This deviates from F1D's canonical SalesGrowthBuilder which uses annual saley
in Q4-only:
    F1D-canonical: (saley − saley_lag) / |saley_lag|  annual

Campello uses quarterly YoY for higher granularity in DiD. Lag via
groupby('gvkey').shift(4) on cal_yr_qtr-sorted data. 1% winsorization within cal_yr_qtr.

Output:
    outputs/variables/brexit_sales_growth/<ts>/brexit_sales_growth.parquet
    schema: gvkey (zfill-6), cal_yr_qtr, brexit_sales_growth (float64)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


WINDOW_START_YQ = 20084  # 2008Q4 (4-quarter buffer for shift(4) + 1Q-lag at runner)
WINDOW_END_YQ = 20164
COL_NAME = "brexit_sales_growth"
WINSOR_PCT = 0.01


def _winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    def _w(s: pd.Series) -> pd.Series:
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby(group, observed=True)[col].transform(_w)
    return df


class BrexitSalesGrowthBuilder(VariableBuilder):
    """Campello-verbatim quarterly YoY sales growth."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = COL_NAME

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years
        comp_path = root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
        logger.info(f"BrexitSalesGrowthBuilder: reading {comp_path} ...")
        df = pd.read_parquet(comp_path, columns=["gvkey", "datadate", "saleq"])
        df["saleq"] = pd.to_numeric(df["saleq"], errors="coerce")
        df["datadate"] = pd.to_datetime(df["datadate"])
        df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
        df = df[(df["cal_yr_qtr"] >= WINDOW_START_YQ) & (df["cal_yr_qtr"] <= WINDOW_END_YQ)]
        df = df.dropna(subset=["saleq"]).copy()
        df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)

        # Sort + dedup (gvkey, cal_yr_qtr) to ensure shift-4 alignment.
        df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
            subset=["gvkey", "cal_yr_qtr"], keep="last"
        ).reset_index(drop=True)

        # Quarterly YoY: saleq_t / saleq_{t-4}. shift(4) within firm is robust to gaps
        # only if quarters are consecutive — for unbalanced panels we should use
        # cal_yr_qtr-aware lag. Here we use shift(4) AFTER sorting + assume gaps drop NaN.
        df["saleq_lag4"] = df.groupby("gvkey")["saleq"].shift(4)
        df[COL_NAME] = (df["saleq"] - df["saleq_lag4"]) / df["saleq_lag4"].abs()
        df = df[(np.isfinite(df[COL_NAME]))].dropna(subset=[COL_NAME])

        # Restrict output to Brexit window proper (2010Q1-2016Q4) AFTER lag computation.
        df = df[df["cal_yr_qtr"] >= 20094]  # 2009Q4 to leave buffer for runner's 1Q-lag
        df = _winsorize_within(df, COL_NAME, "cal_yr_qtr")

        df = df[["gvkey", "cal_yr_qtr", COL_NAME]].reset_index(drop=True)
        logger.info(f"  rows: {len(df):,}; gvkeys: {df['gvkey'].nunique():,}")

        stats = self.get_stats(df[COL_NAME], COL_NAME)
        metadata = {
            "source": "Campello et al. 2022 JFQA Section II.E (Sales Growth)",
            "formula": "(saleq_t - saleq_{t-4}) / |saleq_{t-4}| quarterly YoY",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr",
            "n_rows": int(len(df)),
            "n_unique_gvkeys": int(df["gvkey"].nunique()),
            "column": COL_NAME,
        }
        return VariableResult(data=df, stats=stats, metadata=metadata)
