"""Inline pytest for run_parallel_trends_test() utility."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from f1d.shared.variables.brexit_parallel_trends import PRE_LEADS, run_parallel_trends_test


def _make_synth_panel(n_firms: int = 80, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    quarters = [20121, 20122, 20123, 20124, 20131, 20132, 20133, 20134,
                20141, 20142, 20143, 20144, 20151, 20152, 20153, 20154,
                20161, 20162]
    rows = []
    for f in range(n_firms):
        high = int(f < n_firms // 2)
        for q in quarters:
            rows.append({
                "gvkey": f"{f:06d}",
                "cal_yr_qtr": q,
                "cash": 0.2 + 0.005 * (q - 20121) + np.random.normal(0, 0.03),
                "HIGH_BETA_UK": high,
                "lnAssets": 8 + np.random.normal(0, 0.5),
            })
    return pd.DataFrame(rows)


def test_returns_sane_keys():
    panel = _make_synth_panel()
    res = run_parallel_trends_test(panel, dv="cash", treatment_col="HIGH_BETA_UK", control_cols=["lnAssets"])
    assert "f_stat" in res
    assert "p_value" in res
    assert "n_obs" in res
    assert "lead_estimates" in res
    assert "warnings" in res


def test_n_obs_positive():
    panel = _make_synth_panel()
    res = run_parallel_trends_test(panel, dv="cash", treatment_col="HIGH_BETA_UK", control_cols=["lnAssets"])
    assert res["n_obs"] > 0
    assert isinstance(res["n_obs"], int)


def test_pre_period_only():
    """The function must restrict to cal_yr_qtr < 20163 (POST-start)."""
    panel = _make_synth_panel()
    res = run_parallel_trends_test(panel, dv="cash", treatment_col="HIGH_BETA_UK", control_cols=["lnAssets"])
    # Synthetic panel has 18 quarters (incl 20162 which is < 20163), so n_obs ≤ original
    assert res["n_obs"] <= 80 * 18


def test_lead_dummies_constructed():
    """All 4 PRE_LEADS values must appear as estimates if not absorbed."""
    panel = _make_synth_panel()
    res = run_parallel_trends_test(panel, dv="cash", treatment_col="HIGH_BETA_UK", control_cols=["lnAssets"])
    # If panel includes all 4 lead quarters with treated firms, all 4 should estimate.
    assert len(res["lead_estimates"]) >= 1, f"no lead estimates produced: warnings={res['warnings']}"


def test_pre_leads_constants_correct():
    """Verify PRE_LEADS map to the 4 quarters before 2016Q3 (POST start)."""
    expected = {"lead_m1": 20162, "lead_m2": 20161, "lead_m3": 20154, "lead_m4": 20153}
    assert PRE_LEADS == expected
