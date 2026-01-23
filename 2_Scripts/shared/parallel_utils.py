"""
Deterministic Random Number Generation for Parallel Processing

Provides deterministic random number generation utilities for parallel processing
using NumPy's SeedSequence spawning pattern. Ensures each worker gets an
independent random stream while maintaining overall reproducibility.

Reference: https://numpy.org/doc/stable/reference/random/parallel.html

Contract:
  ID: parallel_utils.py
  Description: Deterministic RNG spawning for parallel workers using SeedSequence
  Inputs:
    - worker_id: int - Worker identifier for seed propagation
    - root_seed: int - Root seed for reproducibility
  Outputs:
    - numpy.random.Generator instance
  Deterministic: true

Usage Pattern:
    from shared.parallel_utils import spawn_worker_rng

    # In parallel worker function
    rng = spawn_worker_rng(worker_id, root_seed=42)
    result = rng.uniform(size=1000)
"""

import numpy as np


def spawn_worker_rng(worker_id: int, root_seed: int) -> np.random.Generator:
    """
    Create deterministic random number generator stream for a specific worker.

    Uses NumPy's SeedSequence spawning pattern to ensure each worker gets an
    independent random stream while maintaining overall reproducibility.

    Args:
        worker_id: Worker identifier (used in seed propagation)
        root_seed: Root seed for reproducibility (e.g., from config/project.yaml)

    Returns:
        numpy.random.Generator: Deterministic RNG instance for this worker

    Example:
        >>> rng = spawn_worker_rng(0, 42)
        >>> sample = rng.integers(0, 100, size=10)
        >>> # Same worker_id + root_seed produces same sequence
        >>> rng2 = spawn_worker_rng(0, 42)
        >>> assert np.array_equal(rng2.integers(0, 100, size=10), sample)

    Determinism Guarantees:
        - Same worker_id + root_seed always produces same random sequence
        - Different worker_ids produce independent random sequences
        - No adjacent seed collision (worker streams don't overlap)
    """
    # Use SeedSequence spawning pattern: [worker_id, root_seed]
    # This is the recommended pattern per NumPy parallel RNG documentation
    # Avoid manual seed addition (root_seed + worker_id) as adjacent seeds
    # produce similar streams
    seed_seq = np.random.SeedSequence([worker_id, root_seed])
    return np.random.default_rng(seed_seq)


def get_deterministic_random(seed: int) -> np.random.Generator:
    """
    Convenience function for single-threaded deterministic RNG.

    Creates a deterministic random number generator with a provided seed.
    Use this when you don't need parallel processing but want reproducibility.

    Args:
        seed: Seed for deterministic random number generation

    Returns:
        numpy.random.Generator: Deterministic RNG instance

    Example:
        >>> rng = get_deterministic_random(42)
        >>> sample = rng.integers(0, 100, size=10)
        >>> # Same seed always produces same sequence
        >>> rng2 = get_deterministic_random(42)
        >>> assert np.array_equal(rng2.integers(0, 100, size=10), sample)
    """
    return np.random.default_rng(seed)
