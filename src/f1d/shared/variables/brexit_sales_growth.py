"""Brexit-verbatim sales-growth builder — H1.5.brexit_did design.

Campello et al. (2022 JFQA) Table 1 note (verbatim): "SALES_GROWTH is
defined as the year-on-year percentage change in quarterly sales."

    SALES_GROWTH_t = (saleq_t − saleq_{t−4}) / saleq_{t−4}

Signed denominator (verbatim "percentage change" = (new−old)/old, no
absolute value). The t−4 lag is the same calendar quarter one year prior,
resolved via calendar-aware merge (NOT row-order shift(4), which mis-lags
gappy panels). 1% winsorization within cal_yr_qtr (verbatim: "All
variables are winsorized at the 1% level.").

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

        # Quarterly YoY: saleq_t / saleq_{calendar t-4Q}. Calendar-aware merge (NOT
        # row-order shift) is correct for unbalanced panels. Per Campello j.3198
        # verbatim: "year-on-year percentage change in quarterly sales" → denom
        # is signed saleq_{t-4Q} (no |.|).
        df["cal_yr_qtr"] = df["cal_yr_qtr"].astype("int64")
        df["prev_yr_qtr_id"] = ((df["cal_yr_qtr"] // 10 - 1) * 10 + (df["cal_yr_qtr"] % 10)).astype("int64")
        lag_src = df[["gvkey", "cal_yr_qtr", "saleq"]].rename(
            columns={"cal_yr_qtr": "prev_yr_qtr_id", "saleq": "saleq_lag4"}
        )
        df = df.merge(lag_src, on=["gvkey", "prev_yr_qtr_id"], how="left")
        df[COL_NAME] = (df["saleq"] - df["saleq_lag4"]) / df["saleq_lag4"]
        df = df[(np.isfinite(df[COL_NAME]))].dropna(subset=[COL_NAME])

        # Restrict output to Brexit window proper (2010Q1-2016Q4) AFTER lag computation.
        df = df[df["cal_yr_qtr"] >= 20094]  # 2009Q4 to leave buffer for runner's 1Q-lag
        df = _winsorize_within(df, COL_NAME, "cal_yr_qtr")

        df = df[["gvkey", "cal_yr_qtr", COL_NAME]].reset_index(drop=True)
        logger.info(f"  rows: {len(df):,}; gvkeys: {df['gvkey'].nunique():,}")

        stats = self.get_stats(df[COL_NAME], COL_NAME)
        metadata = {
            "source": "Campello et al. 2022 JFQA Section II.E (Sales Growth)",
            "formula": "(saleq_t - saleq_{calendar t-4Q}) / saleq_{calendar t-4Q} (signed denom; calendar-merged lag)",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr",
            "n_rows": int(len(df)),
            "n_unique_gvkeys": int(df["gvkey"].nunique()),
            "column": COL_NAME,
        }
        return VariableResult(data=df, stats=stats, metadata=metadata)
