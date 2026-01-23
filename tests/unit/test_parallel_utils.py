"""
Unit tests for parallel_utils.py

Tests deterministic random number generation for parallel processing.

Contract:
  ID: test_parallel_utils.py
  Description: Unit tests for deterministic RNG spawning in parallel workers
  Dependencies: pytest, numpy
  Deterministic: true
"""

import numpy as np
import pytest

import sys
from pathlib import Path

# Add 2_Scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.parallel_utils import spawn_worker_rng, get_deterministic_random


def test_spawn_worker_rng_reproducibility():
    """Same worker_id + same root_seed produces same random sequence."""
    # Create two identical RNGs
    rng1 = spawn_worker_rng(0, 42)
    rng2 = spawn_worker_rng(0, 42)

    # Generate random sequences
    seq1 = rng1.integers(0, 100, size=100)
    seq2 = rng2.integers(0, 100, size=100)

    # Verify sequences are identical
    assert np.array_equal(seq1, seq2), (
        "Same worker_id + root_seed should produce same sequence"
    )


def test_spawn_worker_rng_independence():
    """Different worker_ids produce different random sequences."""
    # Create two different RNGs
    rng1 = spawn_worker_rng(0, 42)
    rng2 = spawn_worker_rng(1, 42)

    # Generate random sequences
    seq1 = rng1.integers(0, 100, size=100)
    seq2 = rng2.integers(0, 100, size=100)

    # Verify sequences are different
    assert not np.array_equal(seq1, seq2), (
        "Different worker_ids should produce different sequences"
    )


def test_get_deterministic_random_reproducibility():
    """Same seed produces same sequence."""
    # Create two identical RNGs
    rng1 = get_deterministic_random(42)
    rng2 = get_deterministic_random(42)

    # Generate random sequences
    seq1 = rng1.integers(0, 100, size=100)
    seq2 = rng2.integers(0, 100, size=100)

    # Verify sequences are identical
    assert np.array_equal(seq1, seq2), "Same seed should produce same sequence"


def test_seed_sequence_no_collision():
    """Spawn multiple workers, ensure no duplicate sequences."""
    n_workers = 100
    root_seed = 42

    # Generate a single value from each worker's RNG
    values = []
    for worker_id in range(n_workers):
        rng = spawn_worker_rng(worker_id, root_seed)
        # Generate just one integer per worker to test for collision
        value = rng.integers(0, 2**32)
        values.append(value)

    # Verify all values are unique (no collision)
    unique_values = set(values)
    assert len(unique_values) == n_workers, (
        f"SeedSequence collision detected: {len(unique_values)} unique values from {n_workers} workers"
    )


@pytest.mark.parametrize("worker_id", [0, 1, 10, 100])
@pytest.mark.parametrize("root_seed", [1, 42, 12345])
def test_spawn_worker_rng_parameterized(worker_id, root_seed):
    """Test spawn_worker_rng with various parameters."""
    rng1 = spawn_worker_rng(worker_id, root_seed)
    rng2 = spawn_worker_rng(worker_id, root_seed)

    seq1 = rng1.integers(0, 1000, size=50)
    seq2 = rng2.integers(0, 1000, size=50)

    assert np.array_equal(seq1, seq2), (
        f"Reproducibility failed for worker_id={worker_id}, root_seed={root_seed}"
    )


@pytest.mark.parametrize("seed", [0, 1, 42, 12345])
def test_get_deterministic_random_parameterized(seed):
    """Test get_deterministic_random with various seeds."""
    rng1 = get_deterministic_random(seed)
    rng2 = get_deterministic_random(seed)

    seq1 = rng1.integers(0, 1000, size=50)
    seq2 = rng2.integers(0, 1000, size=50)

    assert np.array_equal(seq1, seq2), f"Reproducibility failed for seed={seed}"


def test_rng_provides_full_random_stream():
    """Verify RNG provides independent samples (no repeating patterns)."""
    rng = get_deterministic_random(42)

    # Generate large sample
    sample = rng.integers(0, 100, size=1000)

    # Check for reasonable variance (not all same value)
    unique_count = len(np.unique(sample))
    assert unique_count > 90, f"RNG produces too few unique values: {unique_count}/1000"

    # Check mean is roughly 50 (uniform distribution over 0-100)
    # With 1000 samples, should be within ~5 units of expected mean
    assert 45 < sample.mean() < 55, f"Sample mean {sample.mean()} not near expected 50"
