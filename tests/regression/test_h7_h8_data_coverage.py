#!/usr/bin/env python3
"""
Regression tests for H7-H8 data coverage.
Tests detect the data truncation bug where Volatility/StockRet missing for 2005-2018.
"""

import pytest
import pandas as pd
from pathlib import Path

from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
from f1d.shared.observability.files import compute_file_checksum

# Get repository root from test file location
REPO_ROOT = Path(__file__).parent.parent.parent
pytestmark = pytest.mark.regression


def resolve_output_dir(base_path: Path, required_file: str = None) -> Path:
    """Resolve output directory using timestamp or fallback to /latest/."""
    try:
        return get_latest_output_dir(base_path, required_file=required_file)
    except OutputResolutionError:
        return base_path / "latest"


def test_h7_volatility_coverage():
    """Verify H7 Volatility covers full 2002-2018 period."""
    h7_dir = resolve_output_dir(
        REPO_ROOT / "outputs/3_Financial_V2", required_file="H7_Illiquidity.parquet"
    )
    h7_file = h7_dir / "H7_Illiquidity.parquet"

    if not h7_file.exists():
        pytest.skip(f"H7 output not found: {h7_file}")

    df = pd.read_parquet(h7_file)

    # Check year coverage
    years = df["year"].unique()
    expected_years = list(range(2002, 2019))

    missing_years = set(expected_years) - set(years)
    assert len(missing_years) == 0, f"Missing years in H7: {missing_years}"

    # Check Volatility coverage per year
    for year in expected_years:
        year_data = df[df["year"] == year]
        volatility_valid = year_data["Volatility"].notna().sum()

        # Require at least 80% coverage per year (allows some missing for valid reasons)
        coverage_pct = volatility_valid / len(year_data) * 100
        assert coverage_pct >= 80, (
            f"Volatility coverage too low in {year}: {coverage_pct:.1f}% "
            f"({volatility_valid}/{len(year_data)} observations)"
        )


def test_h8_sample_size():
    """Verify H8 sample includes full 2002-2018 period (~39,408 obs)."""
    h8_dir = resolve_output_dir(
        REPO_ROOT / "outputs/3_Financial_V2", required_file="H8_Takeover.parquet"
    )
    h8_file = h8_dir / "H8_Takeover.parquet"

    if not h8_file.exists():
        pytest.skip(f"H8 output not found: {h8_file}")

    df = pd.read_parquet(h8_file)

    # Check total observations (should be ~39,408 for 2002-2018)
    # Current bug: only 12,408 observations (2002-2004 only)
    n_obs = len(df)
    assert n_obs >= 35000, (
        f"H8 sample size too small: {n_obs:,} observations. "
        f"Expected ~39,408 for 2002-2018. "
        f"Possible data truncation bug (only 2002-2004 data?)"
    )

    # Check year range
    year_range = (df["year"].min(), df["year"].max())
    assert year_range[1] >= 2018, (
        f"H8 year range ends at {year_range[1]}, expected 2018. "
        f"Possible data truncation."
    )


def test_h7_h8_volatility_stockret_not_null():
    """Verify Volatility and StockRet are NOT 100% missing for 2005-2018."""
    h7_dir = resolve_output_dir(
        REPO_ROOT / "outputs/3_Financial_V2", required_file="H7_Illiquidity.parquet"
    )
    h7_file = h7_dir / "H7_Illiquidity.parquet"

    if not h7_file.exists():
        pytest.skip(f"H7 output not found: {h7_file}")

    df = pd.read_parquet(h7_file)

    # Filter to 2005-2018 (the years affected by the bug)
    df_bug_years = df[df["year"].between(2005, 2018)]

    if len(df_bug_years) == 0:
        pytest.fail("No data for 2005-2018 in H7 output")

    # Check that Volatility and StockRet have SOME non-null values
    volatility_valid = df_bug_years["Volatility"].notna().sum()
    stockret_valid = df_bug_years["StockRet"].notna().sum()

    assert volatility_valid > 0, (
        f"Volatility is 100% missing for 2005-2018: {volatility_valid} valid values. "
        f"This is the data truncation bug."
    )
    assert stockret_valid > 0, (
        f"StockRet is 100% missing for 2005-2018: {stockret_valid} valid values. "
        f"This is the data truncation bug."
    )


def test_h7_output_checksum_stable():
    """Verify H7 output checksum is stable (detects unintended changes)."""
    h7_dir = resolve_output_dir(
        REPO_ROOT / "outputs/3_Financial_V2", required_file="H7_Illiquidity.parquet"
    )
    h7_file = h7_dir / "H7_Illiquidity.parquet"

    if not h7_file.exists():
        pytest.skip(f"H7 output not found: {h7_file}")

    # Compute current checksum
    current_checksum = compute_file_checksum(h7_file)

    # Load baseline checksums
    baseline_path = REPO_ROOT / "tests/fixtures/baseline_h7_h8.json"
    if not baseline_path.exists():
        pytest.skip(f"Baseline checksums not found: {baseline_path}")

    import json

    with open(baseline_path) as f:
        baseline = json.load(f)

    expected_checksum = baseline.get("h7_illiquidity")
    if expected_checksum is None:
        pytest.skip("No baseline checksum for h7_illiquidity")

    assert current_checksum == expected_checksum, (
        f"H7 output checksum changed!\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}\n"
        f"Re-run H7 script if this change is intentional."
    )


def test_h8_output_checksum_stable():
    """Verify H8 output checksum is stable (detects unintended changes)."""
    h8_dir = resolve_output_dir(
        REPO_ROOT / "outputs/3_Financial_V2", required_file="H8_Takeover.parquet"
    )
    h8_file = h8_dir / "H8_Takeover.parquet"

    if not h8_file.exists():
        pytest.skip(f"H8 output not found: {h8_file}")

    # Compute current checksum
    current_checksum = compute_file_checksum(h8_file)

    # Load baseline checksums
    baseline_path = REPO_ROOT / "tests/fixtures/baseline_h7_h8.json"
    if not baseline_path.exists():
        pytest.skip(f"Baseline checksums not found: {baseline_path}")

    import json

    with open(baseline_path) as f:
        baseline = json.load(f)

    expected_checksum = baseline.get("h8_takeover")
    if expected_checksum is None:
        pytest.skip("No baseline checksum for h8_takeover")

    assert current_checksum == expected_checksum, (
        f"H8 output checksum changed!\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}\n"
        f"Re-run H8 script if this change is intentional."
    )
