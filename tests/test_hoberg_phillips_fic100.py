"""Inline pytest for HobergPhillipsFIC100Builder (per advisor 2026-05-08 inline-tests-as-you-go)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from f1d.shared.variables.hoberg_phillips_fic100 import HobergPhillipsFIC100Builder


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def fic_result():
    builder = HobergPhillipsFIC100Builder()
    return builder.build(years=range(2010, 2017), root_path=ROOT)


def test_year_range_in_window(fic_result):
    yrs = fic_result.data["year"].unique()
    assert set(yrs).issubset(set(range(2010, 2017))), f"year range outside window: {sorted(yrs)}"


def test_gvkey_zfill_format(fic_result):
    sample = fic_result.data["gvkey"].head(20)
    assert all(len(g) == 6 for g in sample), "gvkey not zfilled to 6"
    assert all(g.isdigit() for g in sample), "gvkey not numeric"


def test_no_null_industry_id(fic_result):
    n_null = fic_result.data["fic100_industry_id"].isna().sum()
    assert n_null == 0, f"{n_null} null fic100_industry_id rows"


def test_metadata_self_consistent(fic_result):
    md = fic_result.metadata
    assert md["n_rows_brexit_window"] == len(fic_result.data)
    assert md["n_unique_gvkeys"] == fic_result.data["gvkey"].nunique()
    assert md["n_fic100_industries"] == fic_result.data["fic100_industry_id"].nunique()
