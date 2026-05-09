"""Inline pytest for Chen restatement treatment with 3 classifier variants (Task C2)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from f1d.shared.variables.chen_restatement_treatment import (
    ChenRestatementTreatmentBuilder,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def variant_a() -> pd.DataFrame:
    return ChenRestatementTreatmentBuilder({"classifier_variant": "A"}).build(
        years=range(1997, 2007), root_path=ROOT
    ).data


@pytest.fixture(scope="module")
def variant_b() -> pd.DataFrame:
    return ChenRestatementTreatmentBuilder({"classifier_variant": "B"}).build(
        years=range(1997, 2007), root_path=ROOT
    ).data


@pytest.fixture(scope="module")
def variant_c() -> pd.DataFrame:
    return ChenRestatementTreatmentBuilder({"classifier_variant": "C"}).build(
        years=range(1997, 2007), root_path=ROOT
    ).data


def test_variant_a_irreg_count_in_audit_range(variant_a):
    """v2 audit M0b expected: A ≈ 89; we accept [50, 200]."""
    n_irreg = int((variant_a["IRREG"] == 1).sum())
    assert 50 <= n_irreg <= 200, f"Variant A IRREG count {n_irreg} outside [50, 200]"


def test_variant_b_irreg_count_in_audit_range(variant_b):
    """v2 audit M0b expected: B ≈ 311 (closest to Chen 270); we accept [200, 450]."""
    n_irreg = int((variant_b["IRREG"] == 1).sum())
    assert 200 <= n_irreg <= 450, f"Variant B IRREG count {n_irreg} outside [200, 450]"


def test_variant_c_irreg_count_at_least_b(variant_b, variant_c):
    """Variant C ⊇ Variant B (only adds rows; never subtracts)."""
    nb = int((variant_b["IRREG"] == 1).sum())
    nc = int((variant_c["IRREG"] == 1).sum())
    assert nc >= nb


def test_first_restatement_only_per_gvkey(variant_b):
    """Per spec Table 1 Panel A '-396 Subsequent restatements (keep first only)'."""
    n_dup = variant_b.duplicated(subset=["gvkey"]).sum()
    assert n_dup == 0


def test_year_0_excluded_in_window(variant_b):
    """Spec C2 verbatim: '[-3,-1] vs [+1,+3]' — year 0 NOT in pre or post window."""
    df = variant_b
    for _, row in df.head(10).iterrows():
        assert row["pre_window_end_fyear"] == row["event_year"] - 1
        assert row["post_window_start_fyear"] == row["event_year"] + 1


def test_chen_window_filter(variant_b):
    """Sample restricted to 1997 - June 2006."""
    df = variant_b
    assert df["event_year"].between(1997, 2006).all()
    # June 2006 cutoff: events in 2006 must be in months 1-6
    y2006 = df[df["event_year"] == 2006]
    if len(y2006) > 0:
        months = pd.to_datetime(y2006["event_date"]).dt.month
        assert (months <= 6).all()


def test_industry_excl_sic_6000_6999(variant_b):
    """Financial firms (SIC 6000-6999) excluded per spec C1."""
    df = variant_b
    assert not df["sic_code_at_event"].between(6000, 6999).any()


def test_industry_excl_sic_4900_4999(variant_b):
    """Utility firms (SIC 4900-4999) excluded per spec C1."""
    df = variant_b
    assert not df["sic_code_at_event"].between(4900, 4999).any()


def test_classifier_variant_metadata(variant_b):
    """Variant label propagates into output."""
    assert (variant_b["classifier_variant"] == "B").all()
