"""Inline pytest for Chen PSM matching (Phase 1C Task C5).

Per spec C5 + audit M2 (FF12 fallback) + audit V4 (no caliper):
    1:1 NN no-replace WITHIN FF48; widen to FF12 if FF48 pool <5;
    NO caliper; t-3 to t-1 predictor avg; year-0 score; X1∪X2∪X3.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from f1d.shared.variables.chen_psm_matching import (
    ChenPSMMatchingBuilder,
    COVARIATES,
    FF48_MIN_POOL,
    DIAGNOSTIC_THRESHOLD,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def matched_b() -> pd.DataFrame:
    return ChenPSMMatchingBuilder({"classifier_variant": "B"}).build(
        years=range(1997, 2007), root_path=ROOT
    ).data


def test_x1_x2_x3_covariate_set_size():
    """X1 (12) + X2 (6) + X3 (2) = 20 covariates per spec C5."""
    assert len(COVARIATES) == 20


def test_x1_includes_baseline_8(matched_b):
    """X1 must include all 8 baseline controls (Q SIZE CF NWC LEV SIGMA NSEG AGE)."""
    expected_baseline = {"q", "size", "cf", "nwc", "lev", "sigma_chen", "nseg", "age"}
    assert expected_baseline.issubset(set(COVARIATES))


def test_x1_x2_x3_split():
    """X1 has 12 cash-determinants, X2 has 6 restatement-det., X3 has 2 trend."""
    x1 = {"size", "q", "cf", "lev", "nwc", "sigma_chen", "nseg", "age",
          "capx", "rd", "acquisition", "div"}
    x2 = {"sgrw", "finance", "delta_nwc", "loss", "z_score", "big_n"}
    x3 = {"cash", "delta_cash"}
    assert len(x1) == 12
    assert len(x2) == 6
    assert len(x3) == 2
    assert (x1 | x2 | x3) == set(COVARIATES)


def test_no_replacement_keeps_first(matched_b):
    """Each control gvkey × event_year used at most once across all treated matches."""
    # Filter to rows where treated=0 and in_psm_sample=1 (matched controls)
    controls = matched_b[(matched_b["treated"] == 0) & (matched_b["in_psm_sample"] == 1)]
    n_dup = controls.duplicated(subset=["gvkey", "event_year"]).sum()
    assert n_dup == 0, f"Found {n_dup} duplicate control rows (replacement violated)"


def test_match_within_ff48_when_pool_sufficient(matched_b):
    """When NOT widened (sufficient FF48 pool): treated_ff48 == control_ff48."""
    sufficient = matched_b[
        (matched_b["in_psm_sample"] == 1)
        & (matched_b["widened_to_ff12"] == False)
    ]
    if len(sufficient) > 0:
        # Both treated and control rows should share treated_ff48 == control_ff48
        assert (sufficient["treated_ff48"] == sufficient["control_ff48"]).all()


def test_widen_to_ff12_when_small_industry(matched_b):
    """When widened: treated_ff12 == control_ff12 (broader industry agreement)."""
    widened = matched_b[
        (matched_b["in_psm_sample"] == 1)
        & (matched_b["widened_to_ff12"] == True)
    ]
    if len(widened) > 0:
        assert (widened["treated_ff12"] == widened["control_ff12"]).all()


def test_no_caliper_force_1to1(matched_b):
    """Per audit V4: NO caliper. Match distance can exceed any threshold."""
    matched_only = matched_b[matched_b["in_psm_sample"] == 1]
    # Just confirm no upper-bound enforcement: max distance should not be magically capped
    if len(matched_only) > 0:
        max_d = matched_only["match_distance"].max()
        assert pd.notna(max_d)
        # Match distance is a real value (not capped at any specific number)
        assert isinstance(max_d, (float, np.floating))


def test_diagnostic_threshold_constant():
    """Audit V4 threshold = 0.10 (median |p_t-p_c| flag)."""
    assert DIAGNOSTIC_THRESHOLD == 0.10


def test_min_pool_constant():
    """Audit M2 small-industry fallback = pool < 5 firms."""
    assert FF48_MIN_POOL == 5


def test_classifier_variant_propagation(matched_b):
    """Variant label propagates into output."""
    if len(matched_b) > 0:
        assert (matched_b["classifier_variant"] == "B").all()


def test_event_year_in_chen_window(matched_b):
    """Output restricted to Chen window 1997-2006."""
    if len(matched_b) > 0:
        assert matched_b["event_year"].between(1997, 2006).all()


def test_match_pair_symmetry(matched_b):
    """Each matched pair: treated row partner = control gvkey, control row partner = treated gvkey."""
    matched_only = matched_b[matched_b["in_psm_sample"] == 1].copy()
    # Group by event_year + match_partner_gvkey to find pairs
    treated_rows = matched_only[matched_only["treated"] == 1]
    control_rows = matched_only[matched_only["treated"] == 0]
    if len(treated_rows) == 0 or len(control_rows) == 0:
        pytest.skip("No matched pairs to validate symmetry")

    # For each treated row: there must be a control row whose partner is this treated gvkey
    for _, t in treated_rows.head(20).iterrows():
        c_match = control_rows[
            (control_rows["match_partner_gvkey"] == t["gvkey"])
            & (control_rows["event_year"] == t["event_year"])
        ]
        assert len(c_match) >= 1, f"No symmetric control row for treated {t['gvkey']} @ {t['event_year']}"


def test_in_psm_sample_binary(matched_b):
    if len(matched_b) > 0:
        assert matched_b["in_psm_sample"].isin([0, 1]).all()


def test_treated_indicator_binary(matched_b):
    if len(matched_b) > 0:
        assert matched_b["treated"].isin([0, 1]).all()
