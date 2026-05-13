"""Tests for OVB-defense FE specs added to run_h1_5_trump_did.py (cols 9-14)."""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from f1d.econometric.run_h1_5_trump_did import (
    MODEL_SPECS, build_cal_yr_qtr_index,
    CAL_YR_QTR_MIN, CAL_YR_QTR_MAX,
)
from f1d.shared.path_utils import get_latest_output_dir


@pytest.fixture(scope="module")
def df_panel():
    """Load minimal panel (H1 parquet) for structural tests."""
    panel_dir = get_latest_output_dir(
        ROOT / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    )
    df = pd.read_parquet(
        panel_dir / "h1_cash_holdings_panel.parquet",
        columns=["gvkey", "ff12_code", "start_date"],
    )
    df = build_cal_yr_qtr_index(df)
    df = df[(df["cal_yr_qtr"] >= CAL_YR_QTR_MIN) & (df["cal_yr_qtr"] <= CAL_YR_QTR_MAX)].copy()
    # cal_yr_qtr is Int64 encoded as YYYYQ (e.g. 20164 = 2016 Q4)
    df["cal_yr"] = (df["cal_yr_qtr"] // 10).astype(int)
    # Post_trump: 2016Q4 and later = encoded as 20164
    df["Post_trump"] = (df["cal_yr_qtr"] >= 20164).astype(int)
    return df


def test_new_ovb_specs_exist():
    """Cols 9-14 must be present in MODEL_SPECS."""
    cols = {s["col"] for s in MODEL_SPECS}
    for c in range(9, 15):
        assert c in cols, f"Col {c} missing from MODEL_SPECS"


def test_spec_c_trump_post_variation(df_panel):
    """
    Spec C (firm_yr_robust) is kept for Trump because DiD_Trump varies
    within firm-year in 2016: Q3 (Pre) vs Q4 (Post). Assert Post_trump
    has non-trivial within-firm-year variation so model is identified.
    """
    df = df_panel.copy()
    df["firm_yr_id"] = df["gvkey"].astype(str) + "_" + df["cal_yr"].astype(str)
    # Count firm-year cells that contain both Pre and Post calls
    within = df.groupby("firm_yr_id")["Post_trump"].nunique()
    mixed_cells = (within > 1).sum()
    # At least 5% of firm-year cells must have mixed Pre/Post
    ratio = mixed_cells / len(within)
    assert ratio >= 0.05, (
        f"Spec C identification weak: only {ratio:.1%} of firm-year cells "
        f"have mixed Post_trump values (need >= 5%)"
    )


def test_spec_c_not_dropped_for_trump():
    """Trump runner must include firm_yr_robust spec (unlike redistricting)."""
    firm_yr_specs = [s for s in MODEL_SPECS if s["fe"] == "firm_yr_robust"]
    assert len(firm_yr_specs) >= 1, "firm_yr_robust spec missing from Trump runner"


def test_ind_yr_id_construction(df_panel):
    """ind_yr_id must produce >= 30 unique cells (FF12 x ~4 years)."""
    df = df_panel.copy()
    df["ind_yr_id"] = df["ff12_code"].astype(str) + "_" + df["cal_yr"].astype(str)
    n_cells = df["ind_yr_id"].nunique()
    assert n_cells >= 30, f"Too few ind_yr_id cells: {n_cells}"
    # Verify format: integer codes should not produce '.0' float artifacts
    sample = df["ind_yr_id"].iloc[0]
    assert ".0" not in sample, f"Float artifact in ind_yr_id: {sample!r}"
    # Should look like "N_YYYY"
    parts = sample.split("_")
    assert len(parts) == 2 and parts[1].isdigit(), f"Bad ind_yr_id format: {sample!r}"


def test_ind_qtr_id_construction(df_panel):
    """ind_qtr_id must produce >= 100 unique cells (FF12 x ~20 quarters)."""
    df = df_panel.copy()
    # cal_yr_qtr is Int64 YYYYQ; astype(str) gives "20164" etc.
    df["ind_qtr_id"] = df["ff12_code"].astype(str) + "_" + df["cal_yr_qtr"].astype(str)
    n_cells = df["ind_qtr_id"].nunique()
    assert n_cells >= 100, f"Too few ind_qtr_id cells: {n_cells}"
    # Verify no float artifacts
    sample = df["ind_qtr_id"].iloc[0]
    assert ".0" not in sample, f"Float artifact in ind_qtr_id: {sample!r}"


def test_firm_yr_id_construction(df_panel):
    """firm_yr_id cell count must exceed number of unique firms."""
    df = df_panel.copy()
    df["firm_yr_id"] = df["gvkey"].astype(str) + "_" + df["cal_yr"].astype(str)
    n_cells = df["firm_yr_id"].nunique()
    n_firms = df["gvkey"].nunique()
    assert n_cells > n_firms, (
        f"firm_yr_id cells ({n_cells}) not > firms ({n_firms})"
    )


@pytest.mark.slow
def test_new_fe_specs_produce_results():
    """Full runner smoke test: cols 9-14 must all succeed."""
    import subprocess, json
    result = subprocess.run(
        [sys.executable, "-m", "src.f1d.econometric.run_h1_5_trump_did"],
        capture_output=True, text=True,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Runner failed:\n{result.stderr[-2000:]}"
    assert "14/14" in result.stdout, "Expected 14/14 regressions complete"
