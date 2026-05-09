"""Inline pytest for 4 Brexit-verbatim control builders (modules #7-#10, audit MAJOR-3)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from f1d.shared.variables.brexit_tobins_q import BrexitTobinsQBuilder
from f1d.shared.variables.brexit_sales_growth import BrexitSalesGrowthBuilder
from f1d.shared.variables.brexit_stock_return import BrexitStockReturnBuilder
from f1d.shared.variables.brexit_cash_flow import BrexitCashFlowBuilder

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def tobins():
    return BrexitTobinsQBuilder().build(years=range(2010, 2017), root_path=ROOT)


@pytest.fixture(scope="module")
def sales_growth():
    return BrexitSalesGrowthBuilder().build(years=range(2010, 2017), root_path=ROOT)


@pytest.fixture(scope="module")
def stock_return():
    return BrexitStockReturnBuilder().build(years=range(2010, 2017), root_path=ROOT)


@pytest.fixture(scope="module")
def cash_flow():
    return BrexitCashFlowBuilder().build(years=range(2010, 2017), root_path=ROOT)


# ---- Schema tests ----

def test_tobins_schema(tobins):
    df = tobins.data
    assert set(df.columns) == {"gvkey", "cal_yr_qtr", "brexit_tobins_q"}
    assert df["brexit_tobins_q"].notna().all()
    assert (df["brexit_tobins_q"] >= 1.0).mean() > 0.5  # most firms have Q>=1


def test_sales_growth_schema(sales_growth):
    df = sales_growth.data
    assert set(df.columns) == {"gvkey", "cal_yr_qtr", "brexit_sales_growth"}
    assert df["brexit_sales_growth"].notna().all()
    assert df["brexit_sales_growth"].abs().max() < 100  # winsorized — no extreme outliers


def test_stock_return_schema(stock_return):
    df = stock_return.data
    assert set(df.columns) == {"gvkey", "cal_yr_qtr", "brexit_stock_return"}
    assert df["brexit_stock_return"].notna().all()
    assert df["brexit_stock_return"].abs().max() < 5  # winsorized — no >500% returns


def test_cash_flow_schema(cash_flow):
    df = cash_flow.data
    assert set(df.columns) == {"gvkey", "cal_yr_qtr", "brexit_cash_flow"}
    assert df["brexit_cash_flow"].notna().all()


# ---- Window tests ----

@pytest.mark.parametrize("fixture", ["tobins", "sales_growth", "stock_return", "cash_flow"])
def test_window_subset(request, fixture):
    """Each builder's output must lie within Brexit window (with 1Q-buffer for runner-stage lag)."""
    df = request.getfixturevalue(fixture).data
    yqs = df["cal_yr_qtr"]
    assert yqs.min() >= 20094, f"{fixture} cal_yr_qtr too early: {yqs.min()}"
    assert yqs.max() <= 20164, f"{fixture} cal_yr_qtr too late: {yqs.max()}"


@pytest.mark.parametrize("fixture", ["tobins", "sales_growth", "stock_return", "cash_flow"])
def test_no_dup_gvkey_yq(request, fixture):
    """One row per (gvkey, cal_yr_qtr)."""
    df = request.getfixturevalue(fixture).data
    n = len(df)
    n_unique = df.drop_duplicates(subset=["gvkey", "cal_yr_qtr"]).shape[0]
    assert n == n_unique, f"{fixture} has {n - n_unique} duplicate (gvkey, cal_yr_qtr) rows"


@pytest.mark.parametrize("fixture", ["tobins", "sales_growth", "stock_return", "cash_flow"])
def test_gvkey_zfill(request, fixture):
    df = request.getfixturevalue(fixture).data
    sample = df["gvkey"].head(20)
    assert all(len(g) == 6 for g in sample), f"{fixture} gvkey not zfilled to 6"
