"""Inline pytest for Chen PS_DEMAND (Phase 1C Task C6).

Per spec C7 (Duchin 2010 framework):
    PS_DEMAND = mean of percentile ranks of:
      IND_STDCF (σ over 10y of industry-MEDIAN CF)
      IND_STDQ (σ over 10y of industry-MEDIAN Q)
      NEG_IND_CORR (-1 × corr over 10y of (industry-MEDIAN CF, industry-MEDIAN Q))
    Audit V2: percentile rank AFTER -1× flip.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from f1d.shared.variables.chen_ps_demand import (
    ChenPSDemandBuilder,
    WINDOW_LEN,
    MIN_OBS,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ps_demand() -> pd.DataFrame:
    return ChenPSDemandBuilder().build(
        years=range(1997, 2007), root_path=ROOT
    ).data


def test_three_components_and_pct_ranks_present(ps_demand):
    expected = {
        "ff48_code", "fyear",
        "ind_stdcf", "ind_stdq", "neg_ind_corr",
        "pct_ind_stdcf", "pct_ind_stdq", "pct_neg_ind_corr",
        "ps_demand",
    }
    assert expected.issubset(ps_demand.columns)


def test_ff48_range(ps_demand):
    assert ps_demand["ff48_code"].between(1, 48).all()


def test_year_range(ps_demand):
    assert ps_demand["fyear"].between(1997, 2006).all()


def test_no_duplicate_ff48_fyear(ps_demand):
    assert ps_demand.duplicated(subset=["ff48_code", "fyear"]).sum() == 0


def test_pct_rank_in_unit_interval(ps_demand):
    """Per fyear, percentile rank of each component ∈ (0, 1]."""
    for col in ["pct_ind_stdcf", "pct_ind_stdq", "pct_neg_ind_corr"]:
        valid = ps_demand[col].dropna()
        if len(valid) > 0:
            assert (valid > 0).all() and (valid <= 1).all()


def test_ps_demand_in_unit_interval(ps_demand):
    """PS_DEMAND = mean of three percentile ranks ∈ (0, 1]."""
    valid = ps_demand["ps_demand"].dropna()
    if len(valid) > 0:
        assert (valid > 0).all() and (valid <= 1).all()


def test_ps_demand_is_mean_of_three_pct_ranks(ps_demand):
    """PS_DEMAND must equal the row-wise mean of pct_* columns."""
    df = ps_demand.dropna(subset=["pct_ind_stdcf", "pct_ind_stdq", "pct_neg_ind_corr"]).copy()
    expected = df[["pct_ind_stdcf", "pct_ind_stdq", "pct_neg_ind_corr"]].mean(axis=1)
    np.testing.assert_allclose(df["ps_demand"].values, expected.values, rtol=1e-9)


def test_neg_ind_corr_is_negative_of_corr(ps_demand):
    """NEG_IND_CORR ∈ [-1, 1] (since it's -1 × corr ∈ [-1, 1])."""
    valid = ps_demand["neg_ind_corr"].dropna()
    if len(valid) > 0:
        assert valid.between(-1.0, 1.0).all()


def test_audit_v2_pct_rank_after_flip(ps_demand):
    """High NEG_IND_CORR (from very-negative original corr) → high pct rank → high PS_DEMAND."""
    df = ps_demand.dropna(subset=["neg_ind_corr", "pct_neg_ind_corr"]).copy()
    # Within each fyear, sort by neg_ind_corr ASC and verify pct_neg_ind_corr is monotone non-decreasing
    for yr, grp in df.groupby("fyear"):
        if len(grp) < 3:
            continue
        srt = grp.sort_values("neg_ind_corr")
        diffs = srt["pct_neg_ind_corr"].diff().dropna()
        assert (diffs >= -1e-9).all(), f"pct rank not monotone in fyear {yr}"


def test_window_constants():
    assert WINDOW_LEN == 10
    assert MIN_OBS == 3


def test_components_non_negative_where_applicable(ps_demand):
    """IND_STDCF and IND_STDQ are stds → non-negative."""
    for col in ["ind_stdcf", "ind_stdq"]:
        valid = ps_demand[col].dropna()
        if len(valid) > 0:
            assert (valid >= 0).all()
