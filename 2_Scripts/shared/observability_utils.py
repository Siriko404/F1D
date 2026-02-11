#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Observability and Statistics Helpers
================================================================================
ID: shared/observability_utils
Description: [DEPRECATED] Provides backward compatibility for existing imports.

This file now re-exports all symbols from the shared.observability package.
Please update your imports to use the new package structure:

    OLD: from shared.observability_utils import DualWriter
    NEW: from shared.observability import DualWriter

All existing imports will continue to work without changes.
The actual implementation has been moved to:
    - shared.observability.logging: DualWriter
    - shared.observability.stats: Statistics functions
    - shared.observability.files: File utilities
    - shared.observability.memory: Memory tracking
    - shared.observability.throughput: Performance measurement
    - shared.observability.anomalies: Anomaly detection

Deterministic: true
Main Functions:
    - DualWriter: Class for dual stdout/file logging
    - print_stat(): Print statistics with formatting
    - get_process_memory_mb(): Get current process memory usage

Dependencies:
    - Utility module for observability (deprecated - use observability/ subpackage)
    - Uses: pandas, numpy, time

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

# Re-export all symbols from observability package for backward compatibility
from shared.observability import (
    # Logging
    DualWriter,
    analyze_missing_values,
    # Throughput
    calculate_throughput,
    collect_before_after_samples,
    collect_ceo_distribution_samples,
    collect_fuzzy_match_samples,
    collect_tenure_samples,
    collect_tier_match_samples,
    collect_unmatched_samples,
    compute_constructvariables_input_stats,
    compute_constructvariables_output_stats,
    compute_constructvariables_process_stats,
    compute_entity_stats,
    compute_event_flags_input_stats,
    compute_event_flags_output_stats,
    compute_event_flags_process_stats,
    # Files
    compute_file_checksum,
    compute_financial_input_stats,
    compute_financial_output_stats,
    compute_financial_process_stats,
    # Statistics (step-specific)
    compute_input_stats,
    compute_linking_input_stats,
    compute_linking_output_stats,
    compute_linking_process_stats,
    compute_manifest_input_stats,
    compute_manifest_output_stats,
    compute_manifest_process_stats,
    compute_market_input_stats,
    compute_market_output_stats,
    compute_market_process_stats,
    compute_step31_input_stats,
    compute_step31_output_stats,
    compute_step31_process_stats,
    compute_step32_input_stats,
    compute_step32_output_stats,
    compute_step32_process_stats,
    compute_step33_input_stats,
    compute_step33_output_stats,
    compute_step33_process_stats,
    compute_temporal_stats,
    compute_tenure_input_stats,
    compute_tenure_output_stats,
    compute_tenure_process_stats,
    compute_tokenize_input_stats,
    compute_tokenize_output_stats,
    compute_tokenize_process_stats,
    detect_anomalies_iqr,
    # Anomalies
    detect_anomalies_zscore,
    generate_financial_report_markdown,
    # Memory
    get_process_memory_mb,
    # Statistics (general)
    print_stat,
    print_stats_summary,
    save_stats,
)

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
