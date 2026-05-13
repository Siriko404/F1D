"""Tests for OVB-defense FE specs added to run_h1_6_redistricting_did.py (cols 9-12)."""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from f1d.econometric.run_h1_6_redistricting_did import (
    MODEL_SPECS, build_cal_yr_qtr_index,
    YEAR_MIN, YEAR_MAX,
)
from f1d.shared.path_utils import get_latest_output_dir


@pytest.fixture(scope="module")
def df_panel():
    """Load minimal panel for structural tests."""
    panel_dir = get_latest_output_dir(
        ROOT / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    )
    df = pd.read_parquet(
        panel_dir / "h1_cash_holdings_panel.parquet",
        columns=["gvkey", "ff12_code", "start_date", "year"],
    )
    df = build_cal_yr_qtr_index(df)
    df = df[df["year"].between(YEAR_MIN, YEAR_MAX)].copy()
    # cal_yr_qtr is Int64 YYYYQ; derive cal_yr from it
    df["cal_yr"] = (df["cal_yr_qtr"] // 10).astype(int)
    # Post_redist: year > 2011 (Hasan verbatim)
    df["Post_redist"] = (df["year"] > 2011).astype(int)
    return df


def test_new_ovb_specs_exist():
    """Cols 9-12 must be present in MODEL_SPECS."""
    cols = {s["col"] for s in MODEL_SPECS}
    for c in range(9, 13):
        assert c in cols, f"Col {c} missing from MODEL_SPECS"


def test_spec_c_excluded():
    """firm_yr_robust must NOT appear in redistricting MODEL_SPECS (Post_redist is year-level)."""
    firm_yr_specs = [s for s in MODEL_SPECS if s["fe"] == "firm_yr_robust"]
    assert len(firm_yr_specs) == 0, (
        "firm_yr_robust found in redistricting MODEL_SPECS — must be excluded: "
        "Post_redist is year-level, making all firm-year cells homogeneous on Post"
    )


def test_post_redist_year_level_homogeneous(df_panel):
    """
    Hard test: Post_redist must be constant within firm-year cells.
    This is the mechanical reason Spec C is dropped for redistricting.
    """
    df = df_panel.copy()
    df["firm_yr_id"] = df["gvkey"].astype(str) + "_" + df["cal_yr"].astype(str)
    within_variation = df.groupby("firm_yr_id")["Post_redist"].nunique()
    cells_with_variation = (within_variation > 1).sum()
    assert cells_with_variation == 0, (
        f"Post_redist has within-firm-year variation in {cells_with_variation} cells — "
        f"expected 0 (Post_redist is year-level indicator)"
    )


def test_only_spec_a_and_b_added():
    """OVB additions must be exactly ind_yr_robust and ind_qtr_robust (not firm_yr_robust)."""
    new_fes = {s["fe"] for s in MODEL_SPECS if s["col"] >= 9}
    assert new_fes == {"ind_yr_robust", "ind_qtr_robust"}, (
        f"Expected only ind_yr_robust + ind_qtr_robust for cols 9+, got: {new_fes}"
    )


def test_ind_yr_id_construction(df_panel):
    """ind_yr_id must produce >= 30 unique cells (FF12 x ~10 years)."""
    df = df_panel.copy()
    df["ind_yr_id"] = df["ff12_code"].astype(str) + "_" + df["cal_yr"].astype(str)
    n_cells = df["ind_yr_id"].nunique()
    assert n_cells >= 30, f"Too few ind_yr_id cells: {n_cells}"
    sample = df["ind_yr_id"].iloc[0]
    assert ".0" not in sample, f"Float artifact in ind_yr_id: {sample!r}"


def test_ind_qtr_id_construction(df_panel):
    """ind_qtr_id must produce >= 200 unique cells (FF12 x ~40 quarters)."""
    df = df_panel.copy()
    df["ind_qtr_id"] = df["ff12_code"].astype(str) + "_" + df["cal_yr_qtr"].astype(str)
    n_cells = df["ind_qtr_id"].nunique()
    assert n_cells >= 200, f"Too few ind_qtr_id cells: {n_cells}"
    sample = df["ind_qtr_id"].iloc[0]
    assert ".0" not in sample, f"Float artifact in ind_qtr_id: {sample!r}"


@pytest.mark.slow
def test_new_fe_specs_produce_results():
    """Full runner smoke test: all 12 regressions must succeed."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "src.f1d.econometric.run_h1_6_redistricting_did"],
        capture_output=True, text=True,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Runner failed:\n{result.stderr[-2000:]}"
    assert "12/12" in result.stdout, "Expected 12/12 regressions complete"
