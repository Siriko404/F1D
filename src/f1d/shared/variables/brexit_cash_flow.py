"""Brexit-verbatim cash-flow builder — H1.5.brexit_did design (Module #10, audit MAJOR-3).

Per Campello et al. 2022 JFQA Section II.E firm-control verbatim:
    CashFlow_t = oibdpq / atq_{t-1}     (operating income before D&A / lagged total assets)

This deviates from F1D's canonical CashFlowBuilder which uses oancfy / avg_assets
(operating cash flow YTD / average assets). Campello uses pre-D&A operating
income with lagged-AT denominator. 1% winsorization within cal_yr_qtr.

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

        df["atq_lag1"] = df.groupby("gvkey")["atq"].shift(1)
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
            "formula": "oibdpq / atq_{t-1} (operating income before D&A / lagged total assets)",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr",
            "n_rows": int(len(df)),
            "n_unique_gvkeys": int(df["gvkey"].nunique()),
            "column": COL_NAME,
        }
        return VariableResult(data=df, stats=stats, metadata=metadata)
