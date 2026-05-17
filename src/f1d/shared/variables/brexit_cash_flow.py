"""Brexit-verbatim cash-flow builder — H1.5.brexit_did design.

Campello et al. (2022 JFQA) Table 1 note (verbatim): "CASH_FLOW is defined
as operating income before depreciation divided by lagged total assets."

    CASH_FLOW_t = oibdpq_t / atq_{t-1}

"lagged total assets" = atq at the prior CALENDAR quarter (t-1), resolved
via calendar-prev-Q merge (NOT row-order shift, which mis-lags gappy
panels). 1% winsorization within cal_yr_qtr (verbatim: "All variables are
winsorized at the 1% level.").

Output:
    outputs/variables/brexit_cash_flow/<ts>/brexit_cash_flow.parquet
    schema: gvkey (zfill-6), cal_yr_qtr, brexit_cash_flow (float64)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


WINDOW_START_YQ = 20094
WINDOW_END_YQ = 20164
COL_NAME = "brexit_cash_flow"
WINSOR_PCT = 0.01


def _winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    def _w(s: pd.Series) -> pd.Series:
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby(group, observed=True)[col].transform(_w)
    return df


class BrexitCashFlowBuilder(VariableBuilder):
    """Campello-verbatim cash flow: oibdpq / lag(atq)."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = COL_NAME

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years
        comp_path = root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
        logger.info(f"BrexitCashFlowBuilder: reading {comp_path} ...")
        df = pd.read_parquet(comp_path, columns=["gvkey", "datadate", "oibdpq", "atq"])
        for c in ["oibdpq", "atq"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["datadate"] = pd.to_datetime(df["datadate"])
        df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
        df = df[(df["cal_yr_qtr"] >= WINDOW_START_YQ - 1) & (df["cal_yr_qtr"] <= WINDOW_END_YQ)]
        df = df.dropna(subset=["oibdpq", "atq"]).copy()
        df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)

        df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
            subset=["gvkey", "cal_yr_qtr"], keep="last"
        ).reset_index(drop=True)

        # Verbatim "lagged total assets" = atq at the prior CALENDAR quarter
        # (t-1). Calendar-prev-Q merge, NOT groupby.shift(1): row-order shift
        # pulls the previous PRESENT quarter for gappy panels (mislabels
        # atq_{t-2} as atq_{t-1}). Matches sales_growth/stock_return
        # calendar-aware lag (bug-fix lineage 2026-05-14; cash_flow was
        # missed in that pass — corrected 2026-05-17 per verbatim).
        def _prev_yq(yq: int) -> int:
            yr, q = yq // 10, yq % 10
            if q == 1:
                return (yr - 1) * 10 + 4
            return yr * 10 + (q - 1)
        df["cal_yr_qtr"] = df["cal_yr_qtr"].astype("int64")
        df["prev_qtr_id"] = df["cal_yr_qtr"].map(_prev_yq).astype("int64")
        lag_src = df[["gvkey", "cal_yr_qtr", "atq"]].rename(
            columns={"cal_yr_qtr": "prev_qtr_id", "atq": "atq_lag1"}
        )
        df = df.merge(lag_src, on=["gvkey", "prev_qtr_id"], how="left")
        df = df[df["atq_lag1"] > 0]
        df[COL_NAME] = df["oibdpq"] / df["atq_lag1"]
        df = df[np.isfinite(df[COL_NAME])].dropna(subset=[COL_NAME])

        df = df[df["cal_yr_qtr"] >= WINDOW_START_YQ]
        df = _winsorize_within(df, COL_NAME, "cal_yr_qtr")
        df = df[["gvkey", "cal_yr_qtr", COL_NAME]].reset_index(drop=True)
        logger.info(f"  rows: {len(df):,}; gvkeys: {df['gvkey'].nunique():,}")

        stats = self.get_stats(df[COL_NAME], COL_NAME)
        metadata = {
            "source": "Campello et al. 2022 JFQA Section II.E (Cash Flow)",
            "formula": "oibdpq_t / atq_{calendar t-1} (op income before D&A / lagged total assets; calendar-prev-Q lag)",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr",
            "n_rows": int(len(df)),
            "n_unique_gvkeys": int(df["gvkey"].nunique()),
            "column": COL_NAME,
        }
        return VariableResult(data=df, stats=stats, metadata=metadata)
