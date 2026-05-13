"""
Tests for OVB-defense FE specs added to run_h1_cash_holdings.py (2026-05-13).

Covers:
  - ind_yr_id / ind_qtr_id / firm_yr_id column construction correctness
  - All 3 new specs produce non-NaN beta for UncPreCEO
  - Effective N >= 50% of baseline (col 2 firm-FE) for each new spec
  - Spec C pre-flight assertion: median within-FY SD / overall SD >= 5%

Run from project root:
    pytest tests/test_run_h1_cash_holdings_ovb_specs.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def panel() -> pd.DataFrame:
    """Load + filter H1 main-sample panel (same logic as runner)."""
    panel_dir = get_latest_output_dir(
        ROOT / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    )
    panel_file = panel_dir / "h1_cash_holdings_panel.parquet"
    cols = [
        "start_date", "gvkey", "ff12_code",
        "UncPreCEO", "UncAnsCEO", "UncPreMgr", "UncAnsMgr",
        "CashRatio", "CashRatio_lead",
    ]
    df = pd.read_parquet(panel_file, columns=cols)
    df = build_cal_yr_qtr_index(df)
    # Main sample filter
    df = df[~df["ff12_code"].isin([8, 11])].copy()
    df = df[df["CashRatio"].notna()].copy()
    return df


# ---------------------------------------------------------------------------
# Spec C pre-flight assertion
# ---------------------------------------------------------------------------

def test_spec_c_preflight_ratio(panel):
    """Median within-firm-year SD / overall SD >= 5% for all 4 key IVs."""
    for iv in ["UncPreCEO", "UncAnsCEO", "UncPreMgr", "UncAnsMgr"]:
        sub = panel[panel[iv].notna()].copy()
        overall_sd = sub[iv].std()
        fy_sd = sub.groupby(["gvkey", "cal_yr"])[iv].std().dropna()
        ratio = fy_sd.median() / overall_sd if overall_sd > 0 else 0.0
        assert ratio >= 0.05, (
            f"Spec C pre-flight FAILED for {iv}: ratio={ratio:.4f} < 0.05. "
            "Drop Spec C for H1 if this fails."
        )


# ---------------------------------------------------------------------------
# ID column construction tests
# ---------------------------------------------------------------------------

def test_ind_yr_id_construction(panel):
    """ind_yr_id must be string, no NaN, format 'N_YYYY'."""
    df = panel.copy()
    df["ind_yr_id"] = df["ff12_code"].astype(str) + "_" + df["cal_yr"].astype(str)
    assert df["ind_yr_id"].notna().all(), "ind_yr_id has NaN"
    assert df["ind_yr_id"].dtype == object, "ind_yr_id must be string dtype"
    # spot-check format: should be like "3_2010" not "3.0_2010"
    sample = df["ind_yr_id"].iloc[0]
    parts = sample.split("_")
    assert len(parts) == 2, f"Unexpected format: {sample}"
    assert "." not in parts[0], f"ff12_code converted to float string: {parts[0]}"
    n_cells = df["ind_yr_id"].nunique()
    assert n_cells >= 100, f"ind_yr_id cell count {n_cells} < 100 (too sparse)"


def test_ind_qtr_id_construction(panel):
    """ind_qtr_id must be string, no NaN, cell count >= 500."""
    df = panel[panel["cal_yr_qtr"].notna()].copy()
    df["ind_qtr_id"] = df["ff12_code"].astype(str) + "_" + df["cal_yr_qtr"].astype(str)
    assert df["ind_qtr_id"].notna().all(), "ind_qtr_id has NaN"
    n_cells = df["ind_qtr_id"].nunique()
    assert n_cells >= 500, f"ind_qtr_id cell count {n_cells} < 500"


def test_firm_yr_id_construction(panel):
    """firm_yr_id must be string, no NaN, format 'GVKEY_YYYY'."""
    df = panel.copy()
    df["firm_yr_id"] = df["gvkey"].astype(str) + "_" + df["cal_yr"].astype(str)
    assert df["firm_yr_id"].notna().all(), "firm_yr_id has NaN"
    assert df["firm_yr_id"].dtype == object, "firm_yr_id must be string dtype"
    n_cells = df["firm_yr_id"].nunique()
    # Should be ~ n_firms × n_years; at minimum larger than n_firms
    n_firms = df["gvkey"].nunique()
    assert n_cells > n_firms, f"firm_yr_id cell count {n_cells} not > n_firms {n_firms}"


# ---------------------------------------------------------------------------
# Regression smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_new_fe_specs_produce_results():
    """
    Smoke test: run all 3 new FE specs (Spec A/B/C) via the runner's
    run_regression() and assert non-NaN UncPreCEO beta + N >= 50% baseline.

    Marked slow — skipped in fast CI via: pytest -m 'not slow'
    """
    from f1d.econometric.run_h1_cash_holdings import (
        MODEL_SPECS,
        load_panel,
        filter_main_sample,
        prepare_regression_data,
        run_regression,
    )

    panel = load_panel(ROOT)
    panel = filter_main_sample(panel)

    # Baseline N from col 2 (firm FE, base controls, CashRatio)
    spec_baseline = next(s for s in MODEL_SPECS if s["col"] == 2)
    df_baseline = prepare_regression_data(panel, spec_baseline)
    baseline_n = len(df_baseline)
    assert baseline_n > 0, "Baseline col 2 has zero observations"

    new_fe_cols = [13, 14, 15]  # Spec A/B/C on CashRatio
    threshold = 0.50 * baseline_n

    for col_num in new_fe_cols:
        spec = next(s for s in MODEL_SPECS if s["col"] == col_num)
        df_prep = prepare_regression_data(panel, spec)
        model, meta = run_regression(df_prep, spec)

        assert model is not None, f"Col {col_num} regression returned None"
        assert meta, f"Col {col_num} meta is empty"

        beta = meta.get("UncPreCEO_beta", np.nan)
        assert not np.isnan(beta), f"Col {col_num} UncPreCEO beta is NaN"

        n_obs = meta.get("n_obs", 0)
        assert n_obs >= threshold, (
            f"Col {col_num} N={n_obs:,} < threshold={threshold:.0f} "
            f"(50% of baseline {baseline_n:,})"
        )
