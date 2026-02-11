"""
Shared fixtures for performance tests.

This module provides test data fixtures for benchmarking Phase 62 optimizations:
- Rolling window vectorization (H2 variables)
- df.update() optimization (entity linking)

Ref: .planning/phases/63-testing-validation/63-03-PLAN.md
"""
import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_compustat_for_rolling():
    """
    Create sample Compustat data for rolling window benchmarking.

    Returns DataFrame with 100 firms x 20 years = 2000 observations.
    Sufficient size to demonstrate vectorization benefit.

    Seed fixed at 42 for reproducible benchmark comparisons.
    """
    np.random.seed(42)
    n_firms = 100
    n_years = 20

    data = []
    for gvkey in range(n_firms):
        for year in range(2000, 2000 + n_years):
            data.append({
                "gvkey": str(gvkey).zfill(6),
                "fiscal_year": year,
                "ocf_at": np.random.rand() * 0.2 + 0.05,  # OCF/assets ratio
                "roa": np.random.rand() * 0.3 - 0.05,     # ROA
                "ebitda_at": np.random.rand() * 0.25 + 0.08,  # EBITDA/assets
            })

    return pd.DataFrame(data)


@pytest.fixture
def sample_entity_link_data():
    """
    Create sample data for entity linking benchmark.

    Returns tuple of (unique_df, update_df) for testing df.update() pattern.

    Simulates the entity linking workflow where:
    - unique_df: Master company list with empty gvkey/conm/sic columns
    - update_df: Matched entities from Compustat to be merged in

    Seed fixed at 42 for reproducible benchmark comparisons.
    """
    np.random.seed(42)
    n_unique = 10000
    n_updates = 5000

    unique_df = pd.DataFrame({
        "company_id": range(n_unique),
        "company_name": [f"Company {i}" for i in range(n_unique)],
        "gvkey": [np.nan] * n_unique,
        "conm": [np.nan] * n_unique,
        "sic": [np.nan] * n_unique,
    })

    update_df = pd.DataFrame({
        "company_id": range(n_updates),
        "gvkey": [str(i).zfill(6) for i in range(n_updates)],
        "conm": [f"Updated {i}" for i in range(n_updates)],
        "sic": [np.random.randint(1000, 9999) for _ in range(n_updates)],
        "link_method": ["fuzzy"] * n_updates,
        "link_quality": [np.random.rand() for _ in range(n_updates)],
    })

    return unique_df, update_df


@pytest.fixture
def sample_compustat_large():
    """
    Large dataset for stress testing rolling window performance.

    Returns DataFrame with 500 firms x 20 years = 10000 observations.
    Used to demonstrate scaling benefits of vectorized operations.

    Seed fixed at 42 for reproducible benchmark comparisons.
    """
    np.random.seed(42)
    n_firms = 500
    n_years = 20

    data = []
    for gvkey in range(n_firms):
        for year in range(2000, 2000 + n_years):
            data.append({
                "gvkey": str(gvkey).zfill(6),
                "fiscal_year": year,
                "ocf_at": np.random.rand() * 0.2 + 0.05,
                "roa": np.random.rand() * 0.3 - 0.05,
            })

    return pd.DataFrame(data)


@pytest.fixture
def sample_entity_link_large():
    """
    Large dataset for stress testing df.update() performance.

    Returns tuple of (unique_df, update_df) with 50000 unique records
    and 20000 updates. Used to demonstrate scaling benefits.

    Seed fixed at 42 for reproducible benchmark comparisons.
    """
    np.random.seed(42)
    n_unique = 50000
    n_updates = 20000

    unique_df = pd.DataFrame({
        "company_id": range(n_unique),
        "company_name": [f"Company {i}" for i in range(n_unique)],
    })

    # Add multiple columns for update
    for i in range(5):
        unique_df[f"col_{i}"] = np.nan

    # Create update data
    update_df = pd.DataFrame({
        "company_id": range(n_updates),
    })
    for i in range(5):
        update_df[f"col_{i}"] = np.random.rand(n_updates)

    return unique_df, update_df
