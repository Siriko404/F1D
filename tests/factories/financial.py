"""Factory fixtures for generating financial test data.

This module provides pytest fixtures that generate Compustat-style
financial data for testing. Each factory is function-scoped to ensure
fresh data per test.

Available Factories:
    - sample_compustat_factory: Generate Compustat-style panel DataFrame
    - sample_panel_data_factory: Generate panel regression test data
    - sample_financial_row_factory: Generate single Compustat row (Series)
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data.

    Returns a callable that generates a DataFrame with standard Compustat
    columns for testing financial data processing functions.

    Args (via factory call):
        n_firms: Number of unique firms (default 10)
        n_years: Number of years per firm (default 5)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.DataFrame with columns: gvkey, fyear, at, dlc, dltt, oancf, sale, ib

    Example:
        def test_asset_calculation(sample_compustat_factory):
            df = sample_compustat_factory(n_firms=10, n_years=5)
            assert len(df) == 50
            assert "gvkey" in df.columns
            assert "at" in df.columns
    """

    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        seed: int = 42,
    ) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        data = []

        for firm_id in range(n_firms):
            gvkey = str(firm_id).zfill(6)
            base_assets = rng.uniform(100, 10000)

            for year_offset in range(n_years):
                fyear = 2000 + year_offset
                # Generate realistic financial values
                at = base_assets * rng.uniform(0.9, 1.1)  # Total assets
                sale = at * rng.uniform(0.5, 2.0)  # Sales
                dlc = at * rng.uniform(0.01, 0.1)  # Debt in current liabilities
                dltt = at * rng.uniform(0.05, 0.3)  # Long-term debt
                oancf = sale * rng.uniform(-0.1, 0.2)  # Operating cash flow
                ib = sale * rng.uniform(-0.1, 0.15)  # Income before extraordinary items

                data.append({
                    "gvkey": gvkey,
                    "fyear": fyear,
                    "at": round(at, 2),
                    "dlc": round(dlc, 2),
                    "dltt": round(dltt, 2),
                    "oancf": round(oancf, 2),
                    "sale": round(sale, 2),
                    "ib": round(ib, 2),
                })

        return pd.DataFrame(data)

    return _factory


@pytest.fixture
def sample_panel_data_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate panel regression test data.

    Returns a callable that generates a DataFrame suitable for testing
    panel regression functions with dependent and independent variables.

    Args (via factory call):
        n_firms: Number of unique firms (default 10)
        n_years: Number of years per firm (default 5)
        n_independent: Number of independent variables (default 2)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.DataFrame with columns: gvkey, year, dependent, independent1, ...

    Example:
        def test_panel_regression(sample_panel_data_factory):
            df = sample_panel_data_factory(n_firms=20, n_years=10, n_independent=3)
            assert len(df) == 200
            assert "dependent" in df.columns
            assert "independent1" in df.columns
    """

    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        n_independent: int = 2,
        seed: int = 42,
    ) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        data = []

        for firm_id in range(n_firms):
            gvkey = str(firm_id).zfill(6)
            firm_effect = rng.normal(0, 1)  # Random firm fixed effect

            for year_offset in range(n_years):
                year = 2000 + year_offset

                # Generate independent variables
                independents = {}
                for i in range(n_independent):
                    independents[f"independent{i + 1}"] = rng.normal(0, 1)

                # Generate dependent variable with firm effect
                dependent = firm_effect + sum(independents.values()) + rng.normal(0, 0.5)

                row = {
                    "gvkey": gvkey,
                    "year": year,
                    "dependent": round(dependent, 4),
                    **{k: round(v, 4) for k, v in independents.items()},
                }
                data.append(row)

        return pd.DataFrame(data)

    return _factory


@pytest.fixture
def sample_financial_row_factory() -> Callable[..., pd.Series]:
    """Factory fixture to generate a single Compustat row (Series).

    Returns a callable that generates a pd.Series representing a single
    Compustat observation. Useful for testing functions that operate on
    individual rows like calculate_firm_controls.

    Args (via factory call):
        gvkey: Firm identifier (default "000001")
        fyear: Fiscal year (default 2010)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.Series with Compustat columns: gvkey, fyear, at, dlc, dltt, oancf, sale, ib

    Example:
        def test_firm_controls(sample_financial_row_factory):
            row = sample_financial_row_factory(gvkey="000123", fyear=2015)
            assert row["gvkey"] == "000123"
            assert row["fyear"] == 2015
    """

    def _factory(
        gvkey: str = "000001",
        fyear: int = 2010,
        seed: int = 42,
    ) -> pd.Series:
        rng = np.random.default_rng(seed)

        at = rng.uniform(100, 10000)
        sale = at * rng.uniform(0.5, 2.0)
        dlc = at * rng.uniform(0.01, 0.1)
        dltt = at * rng.uniform(0.05, 0.3)
        oancf = sale * rng.uniform(-0.1, 0.2)
        ib = sale * rng.uniform(-0.1, 0.15)

        return pd.Series({
            "gvkey": gvkey,
            "fyear": fyear,
            "at": round(at, 2),
            "dlc": round(dlc, 2),
            "dltt": round(dltt, 2),
            "oancf": round(oancf, 2),
            "sale": round(sale, 2),
            "ib": round(ib, 2),
        })

    return _factory
