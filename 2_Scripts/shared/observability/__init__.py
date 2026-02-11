#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE
================================================================================
ID: shared/observability
Description: Provides reusable functions for statistics, monitoring,
             anomaly detection, and performance tracking.

This package splits the monolithic observability_utils.py into focused modules
while maintaining 100% backward compatibility.

Modules:
    - logging: DualWriter class for dual stdout/file logging
    - stats: Statistics and analysis functions (print_stat, analyze_missing_values, etc.)
    - files: File utility functions (compute_file_checksum)
    - memory: Memory tracking utilities (get_process_memory_mb)
    - throughput: Performance measurement functions (calculate_throughput)
    - anomalies: Anomaly detection functions (detect_anomalies_zscore, detect_anomalies_iqr)

Backward Compatibility:
    All symbols are re-exported from this package, so existing imports continue to work:
    - from shared.observability_utils import DualWriter  # Still works
    - from shared.observability import DualWriter  # New preferred way

Deterministic: true
================================================================================
"""

# Re-export all public symbols for backward compatibility
from .logging import DualWriter
from .stats import (
    print_stat,
    analyze_missing_values,
    print_stats_summary,
    save_stats,
    compute_input_stats,
    compute_temporal_stats,
    compute_entity_stats,
    compute_linking_input_stats,
    compute_linking_process_stats,
    compute_linking_output_stats,
    collect_fuzzy_match_samples,
    collect_tier_match_samples,
    collect_unmatched_samples,
    collect_before_after_samples,
    compute_tenure_input_stats,
    compute_tenure_process_stats,
    compute_tenure_output_stats,
    collect_tenure_samples,
    compute_manifest_input_stats,
    compute_manifest_process_stats,
    compute_manifest_output_stats,
    collect_ceo_distribution_samples,
    compute_tokenize_input_stats,
    compute_tokenize_process_stats,
    compute_tokenize_output_stats,
    compute_constructvariables_input_stats,
    compute_constructvariables_process_stats,
    compute_constructvariables_output_stats,
    compute_financial_input_stats,
    compute_financial_process_stats,
    compute_financial_output_stats,
    compute_market_input_stats,
    compute_market_process_stats,
    compute_market_output_stats,
    compute_event_flags_input_stats,
    compute_event_flags_process_stats,
    compute_event_flags_output_stats,
    compute_step31_input_stats,
    compute_step31_process_stats,
    compute_step31_output_stats,
    compute_step32_input_stats,
    compute_step32_process_stats,
    compute_step32_output_stats,
    compute_step33_input_stats,
    compute_step33_process_stats,
    compute_step33_output_stats,
    generate_financial_report_markdown,
)
from .files import compute_file_checksum
from .memory import get_process_memory_mb
from .throughput import calculate_throughput
from .anomalies import (
    detect_anomalies_zscore,
    detect_anomalies_iqr,
)

# Configure logger for this module
import logging
logger = logging.getLogger(__name__)

__all__ = [
    # Logging
    "DualWriter",
    # Statistics (general)
    "print_stat",
    "analyze_missing_values",
    "print_stats_summary",
    "save_stats",
    # Statistics (step-specific)
    "compute_input_stats",
    "compute_temporal_stats",
    "compute_entity_stats",
    "compute_linking_input_stats",
    "compute_linking_process_stats",
    "compute_linking_output_stats",
    "collect_fuzzy_match_samples",
    "collect_tier_match_samples",
    "collect_unmatched_samples",
    "collect_before_after_samples",
    "compute_tenure_input_stats",
    "compute_tenure_process_stats",
    "compute_tenure_output_stats",
    "collect_tenure_samples",
    "compute_manifest_input_stats",
    "compute_manifest_process_stats",
    "compute_manifest_output_stats",
    "collect_ceo_distribution_samples",
    "compute_tokenize_input_stats",
    "compute_tokenize_process_stats",
    "compute_tokenize_output_stats",
    "compute_constructvariables_input_stats",
    "compute_constructvariables_process_stats",
    "compute_constructvariables_output_stats",
    "compute_financial_input_stats",
    "compute_financial_process_stats",
    "compute_financial_output_stats",
    "compute_market_input_stats",
    "compute_market_process_stats",
    "compute_market_output_stats",
    "compute_event_flags_input_stats",
    "compute_event_flags_process_stats",
    "compute_event_flags_output_stats",
    "compute_step31_input_stats",
    "compute_step31_process_stats",
    "compute_step31_output_stats",
    "compute_step32_input_stats",
    "compute_step32_process_stats",
    "compute_step32_output_stats",
    "compute_step33_input_stats",
    "compute_step33_process_stats",
    "compute_step33_output_stats",
    "generate_financial_report_markdown",
    # Files
    "compute_file_checksum",
    # Memory
    "get_process_memory_mb",
    # Throughput
    "calculate_throughput",
    # Anomalies
    "detect_anomalies_zscore",
    "detect_anomalies_iqr",
]
