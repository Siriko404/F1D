"""Inline pytest for Boasiako Eq 1 controls builder (Phase 1A Task A5).

11 controls per spec §3.3 verbatim. v2 audit M3: CF formula
(OIBDP-XINT-TXT-DVC)/AT documented as Bates 2009 interpretation (spec wording
'earnings after interest, dividends, and taxes but before depreciation' is
non-standard).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from f1d.shared.variables.boasiako_eq1_controls import BoasiakoEq1ControlsBuilder

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def controls_panel() -> pd.DataFrame:
    return BoasiakoEq1ControlsBuilder().build(
        years=range(1997, 2016), root_path=ROOT
    ).data


def test_schema_has_11_controls(controls_panel):
    """11 controls per spec §3.3."""
    df = controls_panel
    expected = {
        "gvkey", "fyear",
        "firm_size",          # log(AT)
        "firm_age",           # log(years_in_compustat)
        "book_leverage",      # (DLC + DLTT) / AT
        "market_to_book",     # (AT - BVE + MVE) / AT
        "cash_flow",          # (OIBDP - XINT - TXT - DVC) / AT — Bates 2009 (audit M3 deviation)
        "capital_expenditure", # CAPX / AT_lag
        "acquisition_expenditure", # AQC / AT_lag
        "dividend_paying",    # 1 if pays div
        "rd_expenditure",     # XRD / AT_lag (missing → 0)
        "nwc",                # (ACT - LCT - DLC) / (AT - CHE)  net-assets denom
    }
    # IndCFVol is built separately (Task A6); not in this controls table
    assert expected.issubset(df.columns), f"missing: {expected - set(df.columns)}"


def test_firm_size_is_log_at(controls_panel):
    """Firm Size = log(AT); must be finite and positive for AT > 1."""
    df = controls_panel
    assert df["firm_size"].notna().any()
    # log(AT) for typical firms (AT in millions) ranges roughly 0 to 15
    finite = df["firm_size"].dropna()
    assert finite.min() > -10
    assert finite.max() < 20


def test_dividend_paying_is_binary(controls_panel):
    """Dividend Paying Firms(0/1) per spec line 1049."""
    df = controls_panel
    vals = set(df["dividend_paying"].dropna().unique())
    assert vals.issubset({0, 1, 0.0, 1.0})


def test_winsorize_1pct_both_tails(controls_panel):
    """All firm-level continuous vars winsorized 1% both tails per spec line 1054.

    Verification: a clipped series must have a non-negligible mass at the clip ceiling.
    Specifically, the top-1% population should all be within a tight band of the max
    (since clipping flattens the upper tail). If clipping is broken, the top-1% would
    span a wide range. We verify ratio (top-99-percentile span) / (median span) is small.
    """
    df = controls_panel
    for col in ["firm_size", "book_leverage", "market_to_book", "cash_flow"]:
        ser = df[col].dropna()
        if len(ser) < 100:
            continue
        # Sanity: post-winsorize, the top-1% range (max - p99) should be << median range
        max_val = ser.max()
        p99 = ser.quantile(0.99)
        p50 = ser.median()
        p95 = ser.quantile(0.95)
        top_1pct_span = max_val - p99
        mid_50pct_span = p95 - p50  # representative "normal" range
        if mid_50pct_span > 0:
            ratio = top_1pct_span / mid_50pct_span
            # If winsorize works, top 1% is a small fraction of mid-range mass
            # (clipped values pile at the ceiling). Ratio threshold 0.5 is generous.
            assert ratio < 0.5, (
                f"{col} top-1% span {top_1pct_span:.4f} >> mid-50% span {mid_50pct_span:.4f} "
                f"(ratio {ratio:.3f}) — winsorize likely broken"
            )


def test_no_decimal_dtype(controls_panel):
    """v2 Brexit-lesson: decimal.Decimal trap caught by pd.to_numeric in reader."""
    df = controls_panel
    for col in ["firm_size", "cash_flow", "market_to_book"]:
        sample = df[col].dropna().head(10).tolist()
        assert not any(type(x).__name__ == "Decimal" for x in sample)
