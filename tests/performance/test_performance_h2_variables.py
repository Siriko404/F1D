"""
Performance regression tests for H2 variables rolling window optimization.

Tests verify that vectorized rolling windows (Phase 62-02, 62-03)
are significantly faster than naive loop-based implementation
while producing bitwise-identical results.

Ref: .planning/phases/62-performance-optimization/62-02-PLAN.md
     .planning/phases/62-performance-optimization/62-03-PLAN.md
     .planning/phases/63-testing-validation/63-03-PLAN.md
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add 2_Scripts to path for potential imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

pytestmark = pytest.mark.performance


def _rolling_std_naive(df: pd.DataFrame, group_col: str, value_col: str,
                      window: int = 5, min_periods: int = 3) -> pd.Series:
    """
    Naive rolling std implementation using for loop (pre-optimization).

    This mimics the slow pattern from Phase 62-02 before optimization.
    Used for benchmarking comparison against vectorized approach.

    The naive approach:
    1. Iterates over each group (firm) separately
    2. Sorts each group independently
    3. Computes rolling statistics per group
    4. Concatenates results

    Complexity: O(n * groups) due to Python-level iteration
    """
    results = []

    for _gvkey, group in df.groupby(group_col):
        group = group.sort_values("fiscal_year").reset_index(drop=True)
        rolling_std = group[value_col].rolling(window=window, min_periods=min_periods).std()

        mask = rolling_std.notna()
        if mask.any():
            group_subset = group.loc[mask].copy()
            group_subset["rolling_value"] = rolling_std.loc[mask].values
            results.append(group_subset[["rolling_value"]])

    if results:
        result = pd.concat(results, ignore_index=True)
        return result["rolling_value"]
    else:
        return pd.Series(dtype=float)


def _rolling_std_vectorized(df: pd.DataFrame, group_col: str, value_col: str,
                            window: int = 5, min_periods: int = 3) -> pd.Series:
    """
    Vectorized rolling std implementation (post-optimization).

    This uses the efficient pattern from Phase 62-02/62-03.
    Uses pandas groupby().transform() to apply rolling computation
    to all groups in a single C-level operation.

    The vectorized approach:
    1. Sorts once globally
    2. Applies groupby().transform() with rolling
    3. Filters to valid observations

    Complexity: O(n) - single pass with C-level operations
    """
    df_sorted = df.sort_values([group_col, "fiscal_year"]).copy()

    df_sorted["rolling_value"] = (
        df_sorted.groupby(group_col)[value_col]
        .transform(lambda x: x.rolling(window=window, min_periods=min_periods).std())
    )

    # Filter to valid observations (where rolling was computed)
    result = df_sorted[df_sorted["rolling_value"].notna()]["rolling_value"]
    return result.reset_index(drop=True)


def test_rolling_window_naive_baseline(benchmark, sample_compustat_for_rolling):
    """Establish baseline performance for naive rolling window loop.

    This test benchmarks the pre-optimization approach.
    Expected to be slow due to Python-level iteration over groups.
    """
    result_naive = benchmark(
        _rolling_std_naive,
        sample_compustat_for_rolling,
        "gvkey",
        "ocf_at",
        5,
        3,
    )

    # Verify computation produces valid results
    assert result_naive.notna().sum() > 0, "No valid rolling std values computed"


def test_rolling_window_vectorized(benchmark, sample_compustat_for_rolling):
    """Benchmark vectorized rolling window transform.

    This test benchmarks the post-optimization approach.
    Expected to be significantly faster due to C-level operations.
    """
    result_vectorized = benchmark(
        _rolling_std_vectorized,
        sample_compustat_for_rolling,
        "gvkey",
        "ocf_at",
        5,
        3,
    )

    # Verify computation produces valid results
    assert result_vectorized.notna().sum() > 0, "No valid rolling std values computed"


def test_rolling_window_vectorized_bitwise_identical(sample_compustat_for_rolling):
    """Verify vectorized implementation produces bitwise-identical results to naive.

    This is critical for Phase 62 optimization - speedup must not change results.
    Uses pytest.approx() for floating-point comparison with strict tolerance.

    Ref: .planning/phases/62-performance-optimization/62-RESEARCH.md
          "Every cleanup change must preserve bitwise-identical outputs"
    """
    result_naive = _rolling_std_naive(
        sample_compustat_for_rolling, "gvkey", "ocf_at", 5, 3
    )
    result_vectorized = _rolling_std_vectorized(
        sample_compustat_for_rolling, "gvkey", "ocf_at", 5, 3
    )

    # Verify same number of results
    assert len(result_naive) == len(result_vectorized), \
        f"Different result counts: {len(result_naive)} vs {len(result_vectorized)}"

    # Align results for comparison
    df_compare = pd.DataFrame({
        "naive": result_naive.values,
        "vectorized": result_vectorized.values,
    })

    # Use pytest.approx for floating point comparison
    # rtol=1e-10 ensures bitwise-identical within floating point precision
    for idx, row in df_compare.iterrows():
        assert row["naive"] == pytest.approx(row["vectorized"], rel=1e-10, abs=1e-10), \
            f"Mismatch at index {idx}: naive={row['naive']}, vectorized={row['vectorized']}"

    # All non-NaN values should match
    assert len(df_compare) > 0, "No valid overlapping results"


def test_rolling_window_bitwise_identical_different_window(sample_compustat_for_rolling):
    """Verify bitwise-identical results for different window configurations.

    Tests edge cases: larger windows, different min_periods.
    """
    # Test with larger window
    result_naive = _rolling_std_naive(
        sample_compustat_for_rolling, "gvkey", "ocf_at", 8, 5
    )
    result_vectorized = _rolling_std_vectorized(
        sample_compustat_for_rolling, "gvkey", "ocf_at", 8, 5
    )

    assert len(result_naive) == len(result_vectorized)
    if len(result_naive) > 0:
        np.testing.assert_allclose(
            result_naive.values, result_vectorized.values,
            rtol=1e-10, atol=1e-10,
            err_msg="Results differ for larger window"
        )


@pytest.mark.parametrize("n_firms,n_years,expected_speedup", [
    (50, 10, 2.0),     # Small dataset - expect at least 2x speedup
    (100, 20, 5.0),    # Medium dataset - expect at least 5x speedup
    (500, 20, 10.0),   # Large dataset - expect at least 10x speedup
])
def test_rolling_window_scaling(benchmark, n_firms, n_years, expected_speedup):
    """Test that vectorized implementation scales better than naive.

    Parametrized test verifies speedup increases with dataset size.
    For larger datasets, vectorized operations at C-level should
    significantly outperform Python-level iteration.

    Args:
        n_firms: Number of firms (groups)
        n_years: Number of years per firm
        expected_speedup: Minimum expected speedup factor
    """
    np.random.seed(42)
    data = []
    for gvkey in range(n_firms):
        for year in range(2000, 2000 + n_years):
            data.append({
                "gvkey": str(gvkey).zfill(6),
                "fiscal_year": year,
                "ocf_at": np.random.rand() * 0.2 + 0.05,
            })

    df = pd.DataFrame(data)

    # Benchmark naive implementation
    naive_time = benchmark.pedantic(
        _rolling_std_naive, args=(df, "gvkey", "ocf_at", 5, 3),
        iterations=3, rounds=2
    )

    # Benchmark vectorized implementation
    vectorized_time = benchmark.pedantic(
        _rolling_std_vectorized, args=(df, "gvkey", "ocf_at", 5, 3),
        iterations=3, rounds=2
    )

    # Calculate speedup
    speedup = naive_time.stats["mean"] / vectorized_time.stats["mean"]

    print(f"\nScaling test ({n_firms} firms x {n_years} years):")
    print(f"  Naive: {naive_time.stats['mean']:.6f}s")
    print(f"  Vectorized: {vectorized_time.stats['mean']:.6f}s")
    print(f"  Speedup: {speedup:.1f}x")

    # Verify minimum speedup requirement
    assert speedup >= expected_speedup, \
        f"Speedup {speedup:.1f}x below expected {expected_speedup}x for {n_firms} firms"


def test_rolling_window_multiple_metrics(sample_compustat_for_rolling):
    """Test that vectorization works for multiple financial metrics.

    Verifies the pattern works correctly for different columns:
    - ocf_at: Operating cash flow to assets
    - roa: Return on assets
    - ebitda_at: EBITDA to assets
    """
    for col in ["ocf_at", "roa", "ebitda_at"]:
        result_naive = _rolling_std_naive(
            sample_compustat_for_rolling, "gvkey", col, 5, 3
        )
        result_vectorized = _rolling_std_vectorized(
            sample_compustat_for_rolling, "gvkey", col, 5, 3
        )

        # Verify bitwise-identical for each metric
        assert len(result_naive) == len(result_vectorized), \
            f"Different result counts for {col}"

        if len(result_naive) > 0:
            np.testing.assert_allclose(
                result_naive.values, result_vectorized.values,
                rtol=1e-10, atol=1e-10,
                err_msg=f"Results differ for metric {col}"
            )


def test_rolling_mean_vectorization(benchmark, sample_compustat_for_rolling):
    """Test that vectorization pattern works for rolling mean, not just std.

    Phase 62-03 mentions earnings_volatility which may use mean.
    """
    def _rolling_mean_naive(df, group_col, value_col, window=5, min_periods=3):
        """Naive rolling mean for comparison."""
        results = []
        for _gvkey, group in df.groupby(group_col):
            group = group.sort_values("fiscal_year").reset_index(drop=True)
            rolling_mean = group[value_col].rolling(window=window, min_periods=min_periods).mean()
            mask = rolling_mean.notna()
            if mask.any():
                group_subset = group.loc[mask].copy()
                group_subset["rolling_value"] = rolling_mean.loc[mask].values
                results.append(group_subset[["rolling_value"]])
        if results:
            result = pd.concat(results, ignore_index=True)
            return result["rolling_value"]
        return pd.Series(dtype=float)

    def _rolling_mean_vectorized(df, group_col, value_col, window=5, min_periods=3):
        """Vectorized rolling mean."""
        df_sorted = df.sort_values([group_col, "fiscal_year"]).copy()
        df_sorted["rolling_value"] = (
            df_sorted.groupby(group_col)[value_col]
            .transform(lambda x: x.rolling(window=window, min_periods=min_periods).mean())
        )
        result = df_sorted[df_sorted["rolling_value"].notna()]["rolling_value"]
        return result.reset_index(drop=True)

    # Verify bitwise-identical
    result_naive = _rolling_mean_naive(
        sample_compustat_for_rolling, "gvkey", "ocf_at", 5, 3
    )
    result_vectorized = _rolling_mean_vectorized(
        sample_compustat_for_rolling, "gvkey", "ocf_at", 5, 3
    )

    assert len(result_naive) == len(result_vectorized)
    if len(result_naive) > 0:
        np.testing.assert_allclose(
            result_naive.values, result_vectorized.values,
            rtol=1e-10, atol=1e-10
        )

    # Benchmark vectorized version
    result = benchmark(
        _rolling_mean_vectorized,
        sample_compustat_for_rolling,
        "gvkey",
        "ocf_at",
        5,
        3,
    )
    assert result.notna().sum() > 0
