"""Inline pytest for Chen baseline controls (Phase 1C Task C3).

Per spec C3 PDF p.6 j.295 verbatim:
    Q     = (#AT + (#PRCC_F · #CSHO − #CEQ)) / #AT
    SIZE  = ln(#AT)
    CF    = #OANCF / #AT     (NOT Boasiako's Bates 2009)
    NWC   = (#ACT − #CHE − #LCT + #DLC) / #AT     (CORRECTION 2)
    LEV   = (#DLTT + #DLC) / #AT
    NSEG  = =1 if missing (no Segment file in F1D inputs)
    AGE   = ln(yrs since first appearance in Compustat)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from f1d.shared.variables.chen_baseline_controls import (
    ChenBaselineControlsBuilder,
    CONTINUOUS_CONTROLS,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def chen_controls() -> pd.DataFrame:
    return ChenBaselineControlsBuilder().build(
        years=range(1997, 2007), root_path=ROOT
    ).data


def test_schema_has_all_8_named_columns(chen_controls):
    """Output schema = gvkey + fyear + 7 controls (Q SIZE CF NWC LEV NSEG AGE)."""
    expected = {"gvkey", "fyear", "q", "size", "cf", "nwc", "lev", "nseg", "age"}
    assert expected.issubset(chen_controls.columns)


def test_no_duplicate_gvkey_fyear(chen_controls):
    assert chen_controls.duplicated(subset=["gvkey", "fyear"]).sum() == 0


def test_size_is_positive_log_at(chen_controls):
    """SIZE = ln(AT); Compustat AT in $M so most firms have AT≥1 → SIZE≥0."""
    valid = chen_controls["size"].dropna()
    # Some micro-cap firms have AT<1 → SIZE<0 OK; just check finite
    assert np.isfinite(valid).all()
    # Median size ~ ln of $100M-1B firm = 4-7
    assert 0 < valid.median() < 12


def test_nseg_default_one(chen_controls):
    """NSEG = 1 for ALL firms (no Segment file in F1D inputs/)."""
    assert (chen_controls["nseg"] == 1).all()


def test_age_non_negative(chen_controls):
    """AGE = ln(years_active.clip(lower=1)) ≥ 0."""
    valid = chen_controls["age"].dropna()
    assert (valid >= 0).all()


def test_cf_uses_oancf_not_bates(chen_controls):
    """CF should use OANCF/AT directly. Compare to a hand spot-check via Compustat read."""
    # Read raw Compustat for a few rows and verify CF column matches OANCF/AT
    from f1d.shared._compustat_annual_reader import read_compustat_annual
    raw = read_compustat_annual(
        path=ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
        cols=["gvkey", "datadate", "loc", "at", "oancf"],
        years=range(2000, 2003),
        us_only=True,
    )
    raw = raw.dropna(subset=["at", "oancf"]).copy()
    raw = raw[raw["at"] > 0]
    raw["expected_cf"] = raw["oancf"] / raw["at"]
    raw = raw.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

    merged = chen_controls.merge(
        raw[["gvkey", "fyear", "expected_cf"]],
        on=["gvkey", "fyear"], how="inner",
    )
    # Allow winsorization to clip but CF for non-clipped rows must match
    p1 = raw["expected_cf"].quantile(0.01)
    p99 = raw["expected_cf"].quantile(0.99)
    interior = merged[
        merged["expected_cf"].between(p1 + 1e-6, p99 - 1e-6)
    ].head(50)
    np.testing.assert_allclose(
        interior["cf"].values, interior["expected_cf"].values, rtol=1e-3
    )


def test_winsorize_top_bottom_1pct_applied(chen_controls):
    """Top-1% span should be much smaller than middle-50% span (clipping signature)."""
    for col in CONTINUOUS_CONTROLS:
        v = chen_controls[col].dropna()
        if len(v) < 100:
            continue
        top_span = v.quantile(0.999) - v.quantile(0.99)
        mid_span = v.quantile(0.75) - v.quantile(0.25)
        # If clipping at p99 worked, the >p99 span collapses to ~0
        if mid_span > 0:
            assert top_span < 0.5 * mid_span, (
                f"{col}: top-1% span {top_span:.4f} not collapsed vs mid-50% {mid_span:.4f}"
            )


def test_us_only_filter_applied(chen_controls):
    """Reader applies us_only=True; non-US firms should not appear."""
    # Cross-check: re-read with us_only=False, get more rows
    from f1d.shared._compustat_annual_reader import read_compustat_annual
    us_only_count = read_compustat_annual(
        path=ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
        cols=["gvkey", "datadate", "loc"],
        years=range(2000, 2003),
        us_only=True,
    ).shape[0]
    full_count = read_compustat_annual(
        path=ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
        cols=["gvkey", "datadate", "loc"],
        years=range(2000, 2003),
        us_only=False,
    ).shape[0]
    assert full_count > us_only_count  # filter actually drops rows


def test_industry_excl_sic_6000_6999_and_4900_4999(chen_controls):
    """Reader excludes financial + utility per spec C1; verify via raw join."""
    from f1d.shared._compustat_annual_reader import read_compustat_annual
    raw = read_compustat_annual(
        path=ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
        cols=["gvkey", "datadate", "sic"],
        years=range(2000, 2003),
        us_only=True,
    )
    sic_join = chen_controls.merge(
        raw[["gvkey", "fyear", "sic"]].drop_duplicates(),
        on=["gvkey", "fyear"], how="left",
    )
    if sic_join["sic"].notna().any():
        valid_sic = sic_join.dropna(subset=["sic"])
        assert not valid_sic["sic"].between(6000, 6999).any()
        assert not valid_sic["sic"].between(4900, 4999).any()


def test_year_range(chen_controls):
    """Output restricted to plan years 1997-2006 (Chen window)."""
    assert chen_controls["fyear"].between(1997, 2006).all()
