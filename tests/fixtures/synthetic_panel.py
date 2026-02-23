"""Synthetic panel data fixtures for F1D hypothesis tests."""

import pandas as pd
import numpy as np


def synthetic_manager_clarity_panel(n_rows: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic panel for H0.1 manager clarity tests.

    Creates a panel with file_name as unique identifier, matching the
    structure of the real manager clarity panel data.

    Args:
        n_rows: Number of rows to generate (default 100).
        seed: Random seed for reproducibility (default 42).

    Returns:
        DataFrame with manager clarity panel columns.
    """
    np.random.seed(seed)
    n_ceos = 10

    # Build sample column to match expected filter sequence
    sample_pattern = (["Main"] * 70 + ["Finance"] * 20 + ["Utility"] * 10)
    n_patterns = (n_rows + 99) // 100
    sample_col = (sample_pattern * n_patterns)[:n_rows]

    return pd.DataFrame({
        "file_name": [f"call_{i:04d}" for i in range(n_rows)],
        "ceo_id": [f"CEO{i % n_ceos + 1:03d}" for i in range(n_rows)],
        "sample": sample_col,
        "year": [2002 + (i // 10) % 17 for i in range(n_rows)],
        "Manager_QA_Uncertainty_pct": np.random.uniform(0.5, 2.5, n_rows),
        "Manager_Pres_Uncertainty_pct": np.random.uniform(0.5, 2.0, n_rows),
        "Analyst_QA_Uncertainty_pct": np.random.uniform(1.0, 3.0, n_rows),
        "Entire_All_Negative_pct": np.random.uniform(0.5, 1.5, n_rows),
        "StockRet": np.random.uniform(-0.1, 0.2, n_rows) * 100,
        "MarketRet": np.random.uniform(-0.05, 0.1, n_rows) * 100,
        "EPS_Growth": np.random.uniform(-0.3, 0.5, n_rows),
        "SurpDec": np.random.randint(-5, 6, n_rows),
    })


def synthetic_clarity_scores() -> pd.DataFrame:
    """Generate synthetic clarity scores for formula tests.

    Creates a small DataFrame with known gamma_i values to test the
    clarity formula: clarity_raw = -gamma_i. Includes one reference
    CEO per sample (gamma=0 by construction).

    Returns:
        DataFrame with gamma_i, is_reference, and sample columns.
    """
    return pd.DataFrame({
        "ceo_id": [
            "CEO001", "CEO002", "CEO003", "CEO004", "CEO005",
            "CEO006", "CEO007", "CEO008", "CEO009",
        ],
        "gamma_i": [-0.5, -0.25, 0.0, 0.25, 0.5, 0.0, -0.3, 0.0, 0.4],
        "is_reference": [
            False, False, True, False, False,
            True, False, True, False,
        ],
        "sample": [
            "Main", "Main", "Main", "Main", "Main",
            "Finance", "Finance", "Utility", "Utility",
        ],
    })


def synthetic_ceo_clarity_panel(n_rows: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic panel for H0.2/H0.3 CEO clarity tests.

    Similar structure to manager clarity but with CEO-specific variables.

    Args:
        n_rows: Number of rows to generate (default 100).
        seed: Random seed for reproducibility (default 42).

    Returns:
        DataFrame with CEO clarity panel columns.
    """
    np.random.seed(seed)
    n_ceos = 10

    sample_pattern = (["Main"] * 70 + ["Finance"] * 20 + ["Utility"] * 10)
    n_patterns = (n_rows + 99) // 100
    sample_col = (sample_pattern * n_patterns)[:n_rows]

    return pd.DataFrame({
        "file_name": [f"call_{i:04d}" for i in range(n_rows)],
        "ceo_id": [f"CEO{i % n_ceos + 1:03d}" for i in range(n_rows)],
        "sample": sample_col,
        "year": [2002 + (i // 10) % 17 for i in range(n_rows)],
        "CEO_QA_Uncertainty_pct": np.random.uniform(0.5, 2.5, n_rows),
        "CEO_Pres_Uncertainty_pct": np.random.uniform(0.5, 2.0, n_rows),
        "Analyst_QA_Uncertainty_pct": np.random.uniform(1.0, 3.0, n_rows),
        "Entire_All_Negative_pct": np.random.uniform(0.5, 1.5, n_rows),
        "StockRet": np.random.uniform(-0.1, 0.2, n_rows) * 100,
        "MarketRet": np.random.uniform(-0.05, 0.1, n_rows) * 100,
        "EPS_Growth": np.random.uniform(-0.3, 0.5, n_rows),
        "SurpDec": np.random.randint(-5, 6, n_rows),
    })
