"""Brexit macro-controls builder — H1.5.brexit_did design (Module #4).

Replicates Campello et al. 2022 JFQA Section II.D 5 quarterly macro controls
verbatim per spec lines 824-832 of ``tmp/3did_replication_v2_2026_05_08.md``,
all entered into the DiD as 1Q-lagged contemporaneous controls:

    1. usd_gbp_lag1      BoE USD/GBP daily (XUDLUSS)        quarterly mean
    2. vix_lag1          CBOE VIX daily close               quarterly mean
    3. gdp_fcst_1y_lag1  Philly Fed Livingston (RGDPX_1Y)   biannual → quarterly ffill
    4. umcsent_lag1      UMich UMCSENT monthly              quarterly mean
    5. state_lei_lag1    Philly Fed US Leading Index        quarterly mean
                         (Sina decision 2026-05-14 Problem 5: switched from
                          ADS Business Conditions Index to the Philly Fed
                          national VAR-based Leading Index — the actual LEI
                          Campello cites. ADS is a coincident index, not
                          leading; ADS substitution was a prior misstep.
                          Source: State_Leading_Revised.xls, "US" column.)

Window: 2010Q1 through 2016Q4 (28 quarters). 1Q-lag means we need
contemporaneous values for 2009Q4 through 2016Q3 (28 quarters) and shift
forward to label 2010Q1 through 2016Q4.

Output:
    outputs/variables/brexit_macro/<ts>/brexit_macro_quarterly.parquet
    schema: cal_yr_qtr (int YYYY*10+Q), 5 lag1 columns; 28 rows.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


# Output window per spec §1G + Brexit DiD frame.
WINDOW_START_YQ = 20101  # 2010Q1
WINDOW_END_YQ = 20164    # 2016Q4
# Contemporaneous window for the underlying series (needed before lag).
CONTEMP_START = pd.Timestamp("2009-10-01")  # for 2009Q4 lag-1 input to 2010Q1
CONTEMP_END = pd.Timestamp("2016-09-30")    # for 2016Q3 lag-1 input to 2016Q4

INPUT_VAR_COLUMNS = ["usd_gbp_lag1", "vix_lag1", "gdp_fcst_1y_lag1", "umcsent_lag1", "state_lei_lag1"]


def _yq_int(date: pd.Timestamp) -> int:
    return int(date.year) * 10 + int((date.month - 1) // 3 + 1)


def _add_yq(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Add cal_yr_qtr column (int YYYY*10+Q) from a date column."""
    df = df.copy()
    df["cal_yr_qtr"] = df[date_col].dt.year * 10 + ((df[date_col].dt.month - 1) // 3 + 1)
    return df


def _quarterly_mean(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    df = _add_yq(df, date_col)
    out = df.groupby("cal_yr_qtr", as_index=False)[value_col].mean()
    return out


def _lag1_yq(df: pd.DataFrame, value_col: str, new_name: str) -> pd.DataFrame:
    """Shift cal_yr_qtr forward by 1 quarter to make value the previous-quarter lag.

    cal_yr_qtr=20094 (2009Q4) value labeled as the lag1 for cal_yr_qtr=20101.
    """
    df = df.copy().sort_values("cal_yr_qtr")
    # Compute next-quarter cal_yr_qtr from current.
    yr = df["cal_yr_qtr"] // 10
    q = df["cal_yr_qtr"] % 10
    next_q = q + 1
    next_yr = yr + (next_q == 5).astype(int)
    next_q = next_q.where(next_q != 5, 1)
    df["cal_yr_qtr_lag_target"] = next_yr * 10 + next_q
    return df.rename(columns={value_col: new_name})[["cal_yr_qtr_lag_target", new_name]].rename(
        columns={"cal_yr_qtr_lag_target": "cal_yr_qtr"}
    )


def _load_gbp(root_path: Path) -> pd.DataFrame:
    p = root_path / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv"
    df = pd.read_csv(p)
    df.columns = [c.strip().upper() for c in df.columns]
    df = df.rename(columns={"DATE": "date", "XUDLUSS": "usd_gbp"})
    df["date"] = pd.to_datetime(df["date"], format="%d %b %Y")
    df = df.dropna(subset=["usd_gbp"])
    df = df[(df["date"] >= CONTEMP_START) & (df["date"] <= CONTEMP_END)]
    q = _quarterly_mean(df, "date", "usd_gbp")
    return _lag1_yq(q, "usd_gbp", "usd_gbp_lag1")


def _load_vix(root_path: Path) -> pd.DataFrame:
    p = root_path / "inputs" / "Brexit_replication" / "CBOE" / "VIX_daily_1990-present.csv"
    df = pd.read_csv(p)
    df.columns = [c.strip().upper() for c in df.columns]
    df = df.rename(columns={"DATE": "date", "CLOSE": "vix"})
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y", errors="coerce")
    df = df.dropna(subset=["date", "vix"])
    df = df[(df["date"] >= CONTEMP_START) & (df["date"] <= CONTEMP_END)]
    q = _quarterly_mean(df, "date", "vix")
    return _lag1_yq(q, "vix", "vix_lag1")


def _load_livingston_gdp(root_path: Path) -> pd.DataFrame:
    """Biannual Livingston RGDPX_1Y (12-month-ahead real GDP forecast) → quarterly fwd-fill."""
    p = root_path / "inputs" / "Brexit_replication" / "PhillyFed" / "Livingston_means.xlsx"
    df = pd.read_excel(p)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Date": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["RGDPX_1Y"])
    df = df[(df["date"] >= pd.Timestamp("2009-01-01")) & (df["date"] <= CONTEMP_END)]
    df = df.sort_values("date").reset_index(drop=True)

    # Biannual obs (June + December). Build quarterly index spanning contemp window.
    quarters = pd.date_range(CONTEMP_START, CONTEMP_END, freq="QS")
    qdf = pd.DataFrame({"date": quarters})
    qdf["cal_yr_qtr"] = qdf["date"].dt.year * 10 + ((qdf["date"].dt.month - 1) // 3 + 1)
    # merge_asof — pad-backward (use most-recent prior survey).
    df_sorted = df.sort_values("date")
    qdf_sorted = qdf.sort_values("date")
    out = pd.merge_asof(qdf_sorted, df_sorted[["date", "RGDPX_1Y"]], on="date", direction="backward")
    out = out.rename(columns={"RGDPX_1Y": "gdp_fcst_1y"})[["cal_yr_qtr", "gdp_fcst_1y"]]
    return _lag1_yq(out, "gdp_fcst_1y", "gdp_fcst_1y_lag1")


def _load_umcsent(root_path: Path) -> pd.DataFrame:
    p = root_path / "inputs" / "Brexit_replication" / "UMich" / "UMCSENT.csv"
    df = pd.read_csv(p)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"observation_date": "date", "UMCSENT": "umcsent"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["umcsent"])
    df = df[(df["date"] >= CONTEMP_START) & (df["date"] <= CONTEMP_END)]
    q = _quarterly_mean(df, "date", "umcsent")
    return _lag1_yq(q, "umcsent", "umcsent_lag1")


def _load_state_lei(root_path: Path) -> pd.DataFrame:
    """Philly Fed US Leading Index — the actual LEI Campello cites.

    Source: ``State_Leading_Revised.xls`` (Philly Fed, last release 2020-02-01,
    discontinued post-COVID). Column ``US`` is the VAR-based national leading
    index from Philly Fed's vector-autoregression model. Monthly frequency,
    coverage 1982 onwards. Aggregated to quarterly mean then 1Q-lagged.

    Sina decision 2026-05-14 (Problem 5): replace ADS Business Conditions Index
    (a coincident index) with the proper Philly Fed Leading Index. Closes one
    audit DESIGN deviation.
    """
    p = root_path / "inputs" / "Brexit_replication" / "PhillyFed" / "State_Leading_Revised.xls"
    df = pd.read_excel(p, sheet_name="Indexes")
    df = df[["Date", "US"]].rename(columns={"Date": "date", "US": "state_lei"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["date", "state_lei"])
    df = df[(df["date"] >= CONTEMP_START) & (df["date"] <= CONTEMP_END)]
    q = _quarterly_mean(df, "date", "state_lei")
    return _lag1_yq(q, "state_lei", "state_lei_lag1")


class BrexitMacroControlsBuilder(VariableBuilder):
    """Build 28-row quarterly panel of 5 1Q-lagged macro controls for Brexit DiD."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "vix_lag1"  # representative for stats/winsorization

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years  # window fixed at 2010Q1-2016Q4.

        logger.info("BrexitMacroControlsBuilder: loading 5 macro series ...")
        gbp = _load_gbp(root_path)
        vix = _load_vix(root_path)
        gdp = _load_livingston_gdp(root_path)
        umc = _load_umcsent(root_path)
        lei = _load_state_lei(root_path)

        out = gbp.merge(vix, on="cal_yr_qtr", how="outer")
        out = out.merge(gdp, on="cal_yr_qtr", how="outer")
        out = out.merge(umc, on="cal_yr_qtr", how="outer")
        out = out.merge(lei, on="cal_yr_qtr", how="outer")
        out = out[(out["cal_yr_qtr"] >= WINDOW_START_YQ) & (out["cal_yr_qtr"] <= WINDOW_END_YQ)]
        out = out.sort_values("cal_yr_qtr").reset_index(drop=True)

        # Reorder columns.
        out = out[["cal_yr_qtr"] + INPUT_VAR_COLUMNS]
        logger.info(f"  output rows: {len(out)} (expect 28)")

        # NaN diagnostics — should be 0 for all 5 series.
        n_nan = {c: int(out[c].isna().sum()) for c in INPUT_VAR_COLUMNS}
        logger.info(f"  NaN count per column: {n_nan}")

        # Stats on representative column for VariableResult contract.
        stats = self.get_stats(out[self.column], self.column)
        metadata = {
            "source": "Campello et al. 2022 JFQA Section II.D 5 macro controls",
            "window": f"{WINDOW_START_YQ}-{WINDOW_END_YQ}",
            "n_quarters": int(len(out)),
            "n_nan_per_column": n_nan,
            "lei_source": (
                "Philly Fed US Leading Index ('US' column of State_Leading_Revised.xls; "
                "VAR-based national leading index; discontinued 2020 post-COVID). "
                "Replaces prior ADS Business Conditions Index (coincident, not leading) "
                "per Sina decision 2026-05-14 Problem 5."
            ),
            "lag_convention": "1Q-lagged (each value labeled by the cal_yr_qtr where it serves as the lag1 control)",
            "column": self.column,
            "all_columns": INPUT_VAR_COLUMNS,
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
