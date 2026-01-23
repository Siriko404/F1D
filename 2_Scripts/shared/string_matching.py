#!/usr/bin/env python3
"""
Shared string matching utilities using RapidFuzz.
Provides config-driven fuzzy matching for company/entity names.

id: shared.string_matching
description: String matching utilities with config-driven thresholds using RapidFuzz
inputs: config/project.yaml (string_matching section)
outputs: Fuzzy match results with scores
deterministic: true
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import warnings

# Try rapidfuzz
try:
    from rapidfuzz import fuzz, process, utils

    RAPIDFUZZ_AVAILABLE = True
    RAPIDFUZZ_VERSION = "unknown"
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    RAPIDFUZZ_VERSION = None


def warn_if_rapidfuzz_missing():
    """Log warning if RapidFuzz is unavailable."""
    if not RAPIDFUZZ_AVAILABLE:
        warnings.warn(
            "RapidFuzz not installed. Fuzzy matching will be disabled. "
            "Install: pip install rapidfuzz",
            ImportWarning,
        )


def load_matching_config() -> Dict[str, Any]:
    """
    Load string matching configuration from config/project.yaml.

    Returns:
        Dict with string matching settings (or empty dict if config missing)

    Raises:
        FileNotFoundError: If config/project.yaml not found
        yaml.YAMLError: If config file is invalid YAML
    """
    # Resolve config path relative to this module's location
    # Module is at: 2_Scripts/shared/string_matching.py
    # Config is at: config/project.yaml
    # Need to go up two levels from shared/, then into config/
    module_dir = Path(__file__).parent  # 2_Scripts/shared/
    config_path = module_dir / "../../config/project.yaml"  # ../../config/project.yaml

    if not config_path.exists():
        warnings.warn(
            f"Config file not found: {config_path.resolve()}. Using defaults."
        )
        return {}

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        warnings.warn(f"Error parsing config file: {e}. Using defaults.")
        return {}

    return config.get("string_matching", {})


def get_scorer(name: str):
    """
    Get RapidFuzz scorer function by name.

    Args:
        name: Scorer name (ratio, partial_ratio, token_sort_ratio, WRatio, QRatio)

    Returns:
        Scorer function from rapidfuzz.fuzz

    Raises:
        ValueError: If scorer name unknown
    """
    if not RAPIDFUZZ_AVAILABLE:
        raise ImportError("RapidFuzz not available. Install: pip install rapidfuzz")

    scorers = {
        "ratio": fuzz.ratio,
        "partial_ratio": fuzz.partial_ratio,
        "token_sort_ratio": fuzz.token_sort_ratio,
        "token_set_ratio": fuzz.token_set_ratio,
        "WRatio": fuzz.WRatio,
        "QRatio": fuzz.QRatio,
    }

    if name not in scorers:
        raise ValueError(f"Unknown scorer: {name}. Options: {list(scorers.keys())}")

    return scorers[name]


def match_company_names(
    query: str,
    candidates: List[str],
    threshold: Optional[float] = None,
    scorer_name: str = "WRatio",
    preprocess: bool = True,
) -> Tuple[str, float]:
    """
    Find best matching company name using RapidFuzz.

    Args:
        query: Company name to search for
        candidates: List of candidate company names
        threshold: Minimum similarity score (0-100). If None, uses config default.
        scorer_name: Scorer to use (default: WRatio)
        preprocess: If True, apply default preprocessing

    Returns:
        (best_match, score) tuple. If no match above threshold, returns (query, 0.0)

    Note:
        WRatio provides weighted ratio combining multiple metrics.
        Works well for company names with word order variations.
    """
    if not RAPIDFUZZ_AVAILABLE:
        return (query, 0.0)

    if not candidates:
        return (query, 0.0)

    # Load config for default threshold
    config = load_matching_config()
    if threshold is None:
        threshold = config.get("company_name", {}).get("default_threshold", 92.0)

    # Get scorer
    scorer = get_scorer(scorer_name)

    # Apply preprocessing if requested
    if preprocess:
        query_processed = utils.default_process(query)
        candidates_processed = [utils.default_process(c) for c in candidates]
    else:
        query_processed = query
        candidates_processed = candidates

    # Find best match
    best_match, score, _ = process.extractOne(
        query_processed, candidates_processed, scorer=scorer
    )

    # Return original candidate (not processed version)
    if score < threshold:
        return (query, 0.0)

    # Find original name (before preprocessing)
    # This assumes preprocessing is reversible for the purpose of matching
    best_match_idx = candidates_processed.index(best_match)
    original_match = candidates[best_match_idx]

    return (original_match, score)


def match_many_to_many(
    queries: List[str],
    targets: List[str],
    threshold: Optional[float] = None,
    scorer_name: str = "WRatio",
    preprocess: bool = True,
) -> List[Tuple[str, str, float]]:
    """
    Match multiple queries against targets using RapidFuzz.

    This is significantly faster than nested loops for large datasets.

    Args:
        queries: List of query strings
        targets: List of target strings
        threshold: Minimum similarity score (0-100)
        scorer_name: Scorer to use
        preprocess: If True, apply default preprocessing

    Returns:
        List of (query, target, score) tuples for matches above threshold
    """
    if not RAPIDFUZZ_AVAILABLE:
        return []

    if not queries or not targets:
        return []

    # Load config for default threshold
    config = load_matching_config()
    if threshold is None:
        threshold = config.get("company_name", {}).get("default_threshold", 92.0)

    # Get scorer
    scorer = get_scorer(scorer_name)

    # Apply preprocessing if requested
    if preprocess:
        queries_processed = [utils.default_process(q) for q in queries]
        targets_processed = [utils.default_process(t) for t in targets]
    else:
        queries_processed = queries
        targets_processed = targets

    # Compute distance matrix efficiently using cdist
    try:
        scores = process.cdist(queries_processed, targets_processed, scorer=scorer)
    except Exception as e:
        warnings.warn(f"cdist failed: {e}. Falling back to extractOne for each query.")
        # Fallback: process each query individually
        return _match_many_to_many_fallback(
            queries_processed, targets, targets_processed, threshold, scorer, preprocess
        )

    # Collect results above threshold
    results = []
    for query_idx, query in enumerate(queries):
        for target_idx, target in enumerate(targets):
            score = scores[query_idx][target_idx]
            if score >= threshold:
                results.append((query, target, score))

    return results


def _match_many_to_many_fallback(
    queries: List[str],
    targets: List[str],
    targets_processed: List[str],
    threshold: float,
    scorer,
    preprocess: bool,
) -> List[Tuple[str, str, float]]:
    """Fallback method for many-to-many matching (slower but more robust)."""
    results = []

    for query_idx, query in enumerate(queries):
        query_processed = queries_processed[query_idx] if preprocess else query

        best_match, score, _ = process.extractOne(
            query_processed, targets_processed, scorer=scorer
        )

        if score >= threshold:
            # Find original target
            best_match_idx = targets_processed.index(best_match)
            original_target = targets[best_match_idx]
            results.append((query, original_target, score))

    return results


# Call warning at module import
warn_if_rapidfuzz_missing()
