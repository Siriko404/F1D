"""Brexit-verbatim Tobin's Q builder — H1.5.brexit_did design.

Campello et al. (2022 JFQA) Table 1 note (verbatim, PDF-verified
2026-05-28): "TOBIN_Q is defined as the market value of assets divided by
the book value of assets, and is calculated as the market value of equity
plus the book value of assets minus book value of equity, divided by total
assets." Three terms; no deferred taxes.

    TOBIN_Q = (cshoq*prccq + atq − ceqq) / atq

where market value of equity = cshoq*prccq, book value of assets = atq,
book value of equity = ceqq. 1% winsorization within cal_yr_qtr (verbatim:
"All variables are winsorized at the 1% level.").

Output:
    outputs/variables/brexit_tobins_q/<ts>/brexit_tobins_q.parquet
    schema: gvkey (zfill-6), cal_yr_qtr (int YYYY*10+Q), brexit_tobins_q (float64)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


WINDOW_START_YQ = 20094  # 2009Q4 (1-quarter buffer for 1Q-lag at runner stage)
WINDOW_END_YQ = 20164    # 2016Q4
COL_NAME = "brexit_tobins_q"
WINSOR_PCT = 0.01


def _winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    """1% winsorization within each group (e.g., cal_yr_qtr) on a single column."""
    def _w(s: pd.Series) -> pd.Series:
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby(group, observed=True)[col].transform(_w)
    return df


class BrexitTobinsQBuilder(VariableBuilder):
    """Campello-verbatim Tobin's Q: (cshoq*prccq + atq − ceqq) / atq."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = COL_NAME

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years
        comp_path = root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
        logger.info(f"BrexitTobinsQBuilder: reading {comp_path} ...")
        df = pd.read_parquet(comp_path, columns=["gvkey", "datadate", "atq", "cshoq", "prccq", "ceqq"])
        # Compustat stores numerics as decimal.Decimal in object cols — coerce.
        for c in ["atq", "cshoq", "prccq", "ceqq"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["datadate"] = pd.to_datetime(df["datadate"])
        df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
        df = df[(df["cal_yr_qtr"] >= WINDOW_START_YQ) & (df["cal_yr_qtr"] <= WINDOW_END_YQ)]
        # Campello et al. 2022 JFQA Table 1 note (verbatim, PDF-verified
        # 2026-05-28): "market value of equity plus the book value of
        # assets minus book value of equity, divided by total assets."
        # Three terms. No deferred taxes.
        df = df.dropna(subset=["atq", "cshoq", "prccq", "ceqq"]).copy()
        df = df[df["atq"] > 0]  # avoid div-by-0

        df[COL_NAME] = (df["cshoq"] * df["prccq"] + df["atq"] - df["ceqq"]) / df["atq"]
        df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)

        df = df[["gvkey", "cal_yr_qtr", COL_NAME]].dropna(subset=[COL_NAME])
        df = _winsorize_within(df, COL_NAME, "cal_yr_qtr")

        # Dedup any (gvkey, cal_yr_qtr) duplicates (some firms have 5+ quarters/year due to FY-change).
        df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
            subset=["gvkey", "cal_yr_qtr"], keep="last"
        ).reset_index(drop=True)

        logger.info(f"  rows: {len(df):,}; gvkeys: {df['gvkey'].nunique():,}")
        stats = self.get_stats(df[COL_NAME], COL_NAME)
        metadata = {
            "source": "Campello et al. 2022 JFQA Section II.E (Tobin's Q)",
            "formula": "(cshoq*prccq + atq - ceqq) / atq",
            "notes": "Three terms per paper Table 1 note (PDF-verified 2026-05-28). ceqq required; no deferred taxes.",
            "winsorization": f"{WINSOR_PCT*100}% within cal_yr_qtr",
            "n_rows": int(len(df)),
            "n_unique_gvkeys": int(df["gvkey"].nunique()),
            "column": COL_NAME,
        }
        return VariableResult(data=df, stats=stats, metadata=metadata)
