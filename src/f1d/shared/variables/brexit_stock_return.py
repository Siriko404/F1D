"""Brexit-verbatim stock-return builder — H1.5.brexit_did design (Module #9, audit MAJOR-3).

Per Campello et al. 2022 JFQA Section II.E firm-control verbatim: quarterly
buy-and-hold stock return measured over the calendar quarter. Implemented as
the split-adjusted price ratio:

    StockRet_t = (prccq_t / prccq_{t-1}) - 1   (split-adjusted via ajexq)

i.e., prccq divided by ajexq for split-consistency on both ends:
    adj_p_t = prccq_t / ajexq_t
    StockRet_t = adj_p_t / adj_p_{t-1} - 1

This deviates from F1D's canonical StockReturnBuilder which compounds CRSP
daily ret over a CALL-window (start_date to next-call-start). Campello uses
calendar quarter, not call window. 1% winsorization within cal_yr_qtr.

Output:
    outputs/variables/brexit_stock_return/<ts>/brexit_stock_return.parquet
    schema: gvkey (zfill-6), cal_yr_qtr, brexit_stock_return (float64)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


WINDOW_START_YQ = 20094  # 2009Q4 buffer
WINDOW_END_YQ = 20164
COL_NAME = "brexit_stock_return"
WINSOR_PCT = 0.01


def _winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    def _w(s: pd.Series) -> pd.Series:
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby(group, observed=True)[col].transform(_w)
    return df


class BrexitStockReturnBuilder(VariableBuilder):
    """Campello-verbatim quarterly buy-and-hold stock return (split-adjusted)."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = COL_NAME

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years
        comp_path = root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
        logger.info(f"BrexitStockReturnBuilder: reading {comp_path} ...")
        df = pd.read_parquet(comp_path, columns=["gvkey", "datadate", "prccq", "ajexq"])
        for c in ["prccq", "ajexq"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["datadate"] = pd.to_datetime(df["datadate"])
        df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
        df = df[(df["cal_yr_qtr"] >= WINDOW_START_YQ - 1) & (df["cal_yr_qtr"] <= WINDOW_END_YQ)]
        # Note: subtract 1 from cal_yr_qtr is wrong for window-start (20094-1=20093 still 2009Q3 buffer; OK)
        df = df.dropna(subset=["prccq"]).copy()
        df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)
        # ajexq missing → assume 1.0 (no split adjustment).
        df["ajexq"] = df["ajexq"].fillna(1.0)
        df["adj_prccq"] = df["prccq"] / df["ajexq"]

        df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
            subset=["gvkey", "cal_yr_qtr"], keep="last"
        ).reset_index(drop=True)

        # Calendar-prev-Q merge (NOT row-order shift) — bug-fix 2026-05-14 for
        # gappy panels (firms missing a quarter would pull wrong reference price
        # under row-order shift). Per Campello j.3198 verbatim "quarterly
        # buy-and-hold return".
        def _prev_yq(yq: int) -> int:
            yr, q = yq // 10, yq % 10
            if q == 1: return (yr - 1) * 10 + 4
            return yr * 10 + (q - 1)
        df["cal_yr_qtr"] = df["cal_yr_qtr"].astype("int64")
        df["prev_qtr_id"] = df["cal_yr_qtr"].map(_prev_yq).astype("int64")
        lag_src = df[["gvkey", "cal_yr_qtr", "adj_prccq"]].rename(
            columns={"cal_yr_qtr": "prev_qtr_id", "adj_prccq": "adj_prccq_lag1"}
        )
        df = df.merge(lag_src, on=["gvkey", "prev_qtr_id"], how="left")
        df[COL_NAME] = df["adj_prccq"] / df["adj_prccq_lag1"] - 1
        df = df[np.isfinite(df[COL_NAME])].dropna(subset=[COL_NAME])

        df = _winsorize_within(df, COL_NAME, "cal_yr_qtr")
        df = df[["gvkey", "cal_yr_qtr", COL_NAME]].reset_index(drop=True)
        logger.info(f"  rows: {len(df):,}; gvkeys: {df['gvkey'].nunique():,}")

        stats = self.get_stats(df[COL_NAME], COL_NAME)
        metadata = {
            "source": "Campello et al. 2022 JFQA Section II.E (Stock Return)",
            "formula": "(prccq_t/ajexq_t) / (prccq_{t-1}/ajexq_{t-1}) - 1 quarterly buy-and-hold",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr",
            "n_rows": int(len(df)),
            "n_unique_gvkeys": int(df["gvkey"].nunique()),
            "column": COL_NAME,
        }
        return VariableResult(data=df, stats=stats, metadata=metadata)
