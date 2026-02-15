#!/usr/bin/env python3
"""
==============================================================================
STEP 2.1: Tokenize and Count
==============================================================================
ID: 2.1_TokenizeAndCount
Description: Tokenizes earnings call transcripts and counts word occurrences.

Purpose: Processes raw transcript files to generate word frequency statistics
         for linguistic analysis.

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/transcript/*.txt files

Outputs:
    - 4_Outputs/2_Textual_Analysis/2.1_TokenizeAndCount/{timestamp}/word_counts.parquet
    - stats.json
    - {timestamp}.log

Dependencies:
    - Requires: Step 1.4
    - Uses: f1d.shared.chunked_reader, sklearn, pandas, numpy

Deterministic: true

Location: src/f1d/text/tokenize_and_count.py (migrated from legacy 2_Text/)

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

# TYPE ERROR BASELINE: 0 remaining errors (down from 90)
# All type errors have been resolved using TypedDict for stats structure and cast() for DataFrame operations.
# Remaining type: ignore comments are for library limitations:
# - sklearn CountVectorizer: transform() returns sparse matrix that mypy cannot verify
# - pandas melt operations: mypy cannot infer types for melted DataFrames
# - Dict[str, set] dynamic category construction: mypy cannot verify dynamic key assignment
# All type ignores below are scoped with specific error codes and inline rationale

import argparse
import hashlib
import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union, cast

import numpy as np
import pandas as pd
import psutil
import yaml
from sklearn.feature_extraction.text import CountVectorizer  # type: ignore[import-untyped]  # sklearn lacks py.typed marker

# Note: MemoryAwareThrottler from f1d.shared.chunked_reader is available for future chunked processing.
# Current implementation uses column pruning for memory optimization, avoiding complex refactoring required for process_in_chunks().

# Import memory tracking decorator
from f1d.shared.chunked_reader import track_memory_usage

# Import shared path validation utilities
from f1d.shared.observability_utils import DualWriter
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
    validate_output_path,
)

# ==============================================================================
# Setup & Config
# ==============================================================================


# TypedDict definitions for stats dictionary structure
# These help mypy understand the nested dictionary types used throughout the script


class InputStats(TypedDict, total=False):
    files: List[str]
    checksums: Dict[str, str]
    total_rows: int
    total_columns: int


class ProcessingStats(TypedDict, total=False):
    vocabulary_size: int
    total_vocab_hits: int
    total_tokens: int
    years_processed: int
    years_skipped: int
    per_year: List[Dict[str, Any]]


class OutputStats(TypedDict, total=False):
    final_rows: int
    final_columns: int
    files: List[str]
    checksums: Dict[str, str]


class TimingStats(TypedDict, total=False):
    start_iso: str
    end_iso: str
    duration_seconds: float


class ScriptStats(TypedDict, total=False):
    step_id: str
    timestamp: str
    git_sha: Optional[str]
    input: InputStats
    processing: ProcessingStats
    output: OutputStats
    missing_values: Dict[str, Any]
    timing: TimingStats
    memory_mb: Dict[str, Any]
    tokenize_input: Dict[str, Any]
    tokenize_process: Dict[str, Any]
    tokenize_output: Dict[str, Any]
    optimization: Dict[str, Any]
    memory: Dict[str, Any]
    throughput: Dict[str, Any]
    quality_anomalies: Dict[str, Any]


def setup_logging() -> Path:
    log_dir = (
        Path(__file__).parent.parent.parent.parent / "3_Logs" / "2.1_TokenizeAndCount"
    )
    ensure_output_dir(log_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = log_dir / f"{timestamp}.log"

    sys.stdout = DualWriter(log_path)  # type: ignore[assignment]  # sys.stdout reassignment for logging
    return log_path


def load_config() -> Dict[str, Any]:
    root = Path(__file__).parent.parent.parent.parent
    config_path = root / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)  # type: ignore[no-any-return]  # yaml.safe_load returns Any by design


def parse_arguments():
    """Parse command-line arguments for tokenize_and_count.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 2.1: Tokenize and Count

Tokenizes earnings call transcripts using Loughran-McDonald
master dictionary. Counts word frequencies and calculates
linguistic measures (positive, negative, uncertainty words).
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--dictionary",
        type=str,
        help="Path to LM dictionary file (default: 1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv)",
    )

    return parser.parse_args()


def check_prerequisites(root, args):
    """Validate all required inputs and prerequisite steps exist."""
    from f1d.shared.dependency_checker import validate_prerequisites

    # Dictionary path (from argument or default)
    dict_path = (
        args.dictionary
        if args.dictionary
        else root / "1_Inputs" / "Loughran-McDonald_MasterDictionary_1993-2024.csv"
    )

    required_files = {
        "LM dictionary": Path(dict_path),
    }

    required_steps = {
        "1.4_AssembleManifest": "master_sample_manifest.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Stats Helpers
# ==============================================================================


def compute_file_checksum(filepath: Union[str, Path], algorithm: str = "sha256") -> str:
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
    """Print a statistic with consistent formatting."""
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before * 100) if before != 0 else 0
        sign = "+" if delta >= 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({sign}{pct:.1f}%)")
    else:
        v = value if value is not None else after
        if isinstance(v, float):
            print(f"{prefix}{label}: {v:,.2f}")
        elif isinstance(v, int):
            print(f"{prefix}{label}: {v:,}")
        else:
            print(f"{prefix}{label}: {v}")


def analyze_missing_values(df: pd.DataFrame) -> Dict[str, Dict[str, Union[int, float]]]:
    """Analyze missing values per column."""
    missing: Dict[str, Dict[str, Union[int, float]]] = {}
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            missing[str(col)] = {
                "count": null_count,
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def print_stats_summary(stats):
    """Print formatted summary table."""
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)

    inp = stats["input"]
    out = stats["output"]
    delta = inp["total_rows"] - out["final_rows"]
    delta_pct = (delta / inp["total_rows"] * 100) if inp["total_rows"] > 0 else 0

    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Input Rows':<25} {inp['total_rows']:>15,}")
    print(f"{'Output Rows':<25} {out['final_rows']:>15,}")
    print(f"{'Rows Removed':<25} {delta:>15,}")
    print(f"{'Removal Rate':<25} {delta_pct:>14.1f}%")
    print(f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}")

    if stats["processing"]:
        print(f"\n{'Processing Step':<30} {'Value':>15}")
        print("-" * 48)
        for step, count in stats["processing"].items():
            if isinstance(count, (int, float)):
                print(f"{step:<30} {count:>15,}")
            elif not isinstance(count, list):
                print(f"{step:<30} {count}")

    print("=" * 60)


def save_stats(stats, out_dir):
    """Save statistics to JSON file."""
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


def generate_tokenization_report(stats, out_dir):
    """
    Generate comprehensive tokenization report in markdown format.

    Creates publication-ready report with INPUT, PROCESS, and OUTPUT sections.

    Args:
        stats: Statistics dictionary with tokenize_input, tokenize_process, tokenize_output keys
        out_dir: Output directory path
    """
    report_path = out_dir / "report_step_2_1.md"

    with open(report_path, "w", encoding="utf-8") as f:
        # Title
        f.write("# Step 2.1: Tokenize and Count - Report\n\n")
        f.write(f"**Generated:** {stats.get('timestamp', 'N/A')}\n\n")
        f.write("---\n\n")

        # INPUT DATA SECTION
        f.write("## INPUT DATA\n\n")

        # Manifest File
        f.write("### Manifest File (from step 1.4)\n\n")
        if "tokenize_input" in stats and "manifest_stats" in stats["tokenize_input"]:
            ms = stats["tokenize_input"]["manifest_stats"]
            f.write(f"- **Total files:** {ms.get('total_files', 'N/A'):,}\n")

            if "unique_companies" in ms:
                f.write(f"- **Unique companies:** {ms['unique_companies']:,}\n")

            if "date_range" in ms:
                dr = ms["date_range"]
                f.write(
                    f"- **Date range:** {dr.get('earliest', 'N/A')} to {dr.get('latest', 'N/A')}\n"
                )

            if "event_type_dist" in ms:
                f.write("\n**Event Type Distribution:**\n\n")
                f.write("| Event Type | Count |\n")
                f.write("|-----------|-------|\n")
                for et, count in sorted(
                    ms["event_type_dist"].items(), key=lambda x: int(x[0])
                ):
                    f.write(f"| {et} | {count:,} |\n")

        f.write("\n")

        # LM Dictionary
        f.write("### Loughran-McDonald Dictionary\n\n")
        if "tokenize_input" in stats and "dictionary_stats" in stats["tokenize_input"]:
            ds = stats["tokenize_input"]["dictionary_stats"]
            f.write(f"- **Total vocabulary words:** {ds.get('total_words', 'N/A'):,}\n")
            f.write(f"- **Vocabulary size:** {ds.get('vocabulary_size', 'N/A'):,}\n")
            f.write(
                f"- **Average word length:** {ds.get('avg_word_length', 'N/A'):.2f}\n"
            )

            if "word_length_distribution" in ds:
                f.write("\n**Word Length Distribution:**\n\n")
                f.write("| Length Range | Count |\n")
                f.write("|--------------|-------|\n")
                for bucket, count in ds["word_length_distribution"].items():
                    f.write(f"| {bucket} | {count:,} |\n")

        f.write("\n")

        # Category Breakdown
        if (
            "tokenize_input" in stats
            and "category_breakdown" in stats["tokenize_input"]
        ):
            f.write("**Words per Category:**\n\n")
            f.write("| Category | Word Count | Sample Words |\n")
            f.write("|----------|------------|--------------|\n")

            cb = stats["tokenize_input"]["category_breakdown"]
            for cat_name in sorted(cb.keys()):
                cat_info = cb[cat_name]
                sample_words = ", ".join(cat_info.get("sample_words", [])[:5])
                f.write(
                    f"| {cat_name} | {cat_info['word_count']:,} | {sample_words} |\n"
                )

        f.write("\n")

        # Overlap Analysis
        if "tokenize_input" in stats and "overlap_analysis" in stats["tokenize_input"]:
            oa = stats["tokenize_input"]["overlap_analysis"]
            f.write(
                f"**Category Overlap:** {oa.get('words_in_multiple_categories', 0):,} words appear in multiple categories\n\n"
            )

            if "category_overlaps" in oa and oa["category_overlaps"]:
                f.write("| Category Pair | Overlapping Words |\n")
                f.write("|---------------|-------------------|\n")
                for pair, count in sorted(
                    oa["category_overlaps"].items(), key=lambda x: x[1], reverse=True
                ):
                    f.write(f"| {pair} | {count:,} |\n")

        f.write("\n---\n\n")

        # TOKENIZATION PROCESS SECTION
        f.write("## TOKENIZATION PROCESS\n\n")

        # Volume Metrics
        f.write("### Volume Metrics\n\n")
        if (
            "tokenize_process" in stats
            and "volume_metrics" in stats["tokenize_process"]
        ):
            vm = stats["tokenize_process"]["volume_metrics"]
            f.write(f"- **Total input rows:** {vm.get('total_input_rows', 'N/A'):,}\n")
            f.write(
                f"- **Total output rows:** {vm.get('total_output_rows', 'N/A'):,}\n"
            )
            f.write(f"- **Total tokens:** {vm.get('total_tokens', 'N/A'):,}\n")
            f.write(
                f"- **Total vocabulary hits:** {vm.get('total_vocab_hits', 'N/A'):,}\n"
            )

        f.write("\n")

        # Coverage Metrics
        f.write("### Coverage Metrics\n\n")
        if (
            "tokenize_process" in stats
            and "coverage_metrics" in stats["tokenize_process"]
        ):
            cm = stats["tokenize_process"]["coverage_metrics"]
            f.write(
                f"- **Vocabulary hit rate:** {cm.get('vocab_hit_rate', 'N/A'):.2f}%\n"
            )
            f.write(f"- **Out-of-vocabulary rate:** {cm.get('oov_rate', 'N/A'):.2f}%\n")

        f.write("\n")

        # Category Hit Rates
        if (
            "tokenize_process" in stats
            and "category_hit_rates" in stats["tokenize_process"]
        ):
            chr = stats["tokenize_process"]["category_hit_rates"]
            f.write("**Per-Category Hit Rates:**\n\n")
            f.write("| Category | Hit Count | Hit Rate % |\n")
            f.write("|----------|-----------|------------|\n")
            for cat_name in sorted(chr.keys()):
                cat_info = chr[cat_name]
                f.write(
                    f"| {cat_name} | {cat_info.get('hit_count', 0):,} | {cat_info.get('hit_rate_pct', 0.0):.2f}% |\n"
                )

        f.write("\n")

        # Efficiency Metrics
        f.write("### Efficiency Metrics\n\n")
        if (
            "tokenize_process" in stats
            and "efficiency_metrics" in stats["tokenize_process"]
        ):
            em = stats["tokenize_process"]["efficiency_metrics"]
            f.write(
                f"- **Documents per second:** {em.get('docs_per_second', 'N/A'):,.2f}\n"
            )
            f.write(
                f"- **Tokens per second:** {em.get('tokens_per_second', 'N/A'):,.2f}\n"
            )

            if "tokens_per_doc" in em:
                tpd = em["tokens_per_doc"]
                f.write(
                    f"- **Average tokens per document:** {tpd.get('mean', 'N/A'):.2f}\n"
                )
                f.write(
                    f"- **Median tokens per document:** {tpd.get('median', 'N/A'):.2f}\n"
                )
                f.write(f"- **Min tokens per document:** {tpd.get('min', 'N/A'):,}\n")
                f.write(f"- **Max tokens per document:** {tpd.get('max', 'N/A'):,}\n")

            f.write(f"- **Years processed:** {em.get('years_processed', 'N/A')}\n")

        f.write("\n")

        # Yearly Trends
        f.write("### Yearly Trends\n\n")
        if "tokenize_process" in stats and "yearly_trends" in stats["tokenize_process"]:
            yt = stats["tokenize_process"]["yearly_trends"]

            if "tokens_per_year" in yt:
                f.write("**Tokens per Year:**\n\n")
                f.write("| Year | Tokens | Vocab Hits |\n")
                f.write("|------|--------|------------|\n")

                tokens_by_year = yt["tokens_per_year"]
                vocab_by_year = yt.get("vocab_hits_per_year", {})

                for year in sorted(tokens_by_year.keys(), key=int):
                    tokens = tokens_by_year[year]
                    vocab_hits = vocab_by_year.get(year, 0)
                    f.write(f"| {year} | {tokens:,} | {vocab_hits:,} |\n")

        f.write("\n---\n\n")

        # OUTPUT SUMMARY SECTION
        f.write("## OUTPUT SUMMARY\n\n")

        # Category Count Distributions
        f.write("### Category Count Distributions\n\n")
        if (
            "tokenize_output" in stats
            and "category_distributions" in stats["tokenize_output"]
        ):
            cd = stats["tokenize_output"]["category_distributions"]

            for cat_name in sorted(cd.keys()):
                cat_stats = cd[cat_name]
                f.write(f"**{cat_name}:**\n\n")
                f.write(f"- Mean: {cat_stats.get('mean', 0):.2f}\n")
                f.write(f"- Median: {cat_stats.get('median', 0):.2f}\n")
                f.write(f"- Std: {cat_stats.get('std', 0):.2f}\n")
                f.write(f"- Min: {cat_stats.get('min', 0):,}\n")
                f.write(f"- Max: {cat_stats.get('max', 0):,}\n")
                f.write(f"- 25th percentile: {cat_stats.get('q25', 0):.2f}\n")
                f.write(f"- 75th percentile: {cat_stats.get('q75', 0):.2f}\n")
                f.write(f"- Zero count (%): {cat_stats.get('zeros_pct', 0):.2f}%\n\n")

        # Total Tokens Statistics
        f.write("### Total Tokens Statistics\n\n")
        if (
            "tokenize_output" in stats
            and "total_tokens_stats" in stats["tokenize_output"]
        ):
            tts = stats["tokenize_output"]["total_tokens_stats"]
            f.write(f"- Mean: {tts.get('mean', 0):.2f}\n")
            f.write(f"- Median: {tts.get('median', 0):.2f}\n")
            f.write(f"- Std: {tts.get('std', 0):.2f}\n")
            f.write(f"- Min: {tts.get('min', 0):,}\n")
            f.write(f"- Max: {tts.get('max', 0):,}\n")

            if "percentiles" in tts:
                p = tts["percentiles"]
                f.write(f"- 10th percentile: {p.get('p10', 0):.2f}\n")
                f.write(f"- 25th percentile: {p.get('p25', 0):.2f}\n")
                f.write(f"- 50th percentile: {p.get('p50', 0):.2f}\n")
                f.write(f"- 75th percentile: {p.get('p75', 0):.2f}\n")
                f.write(f"- 90th percentile: {p.get('p90', 0):.2f}\n")
                f.write(f"- 95th percentile: {p.get('p95', 0):.2f}\n")
                f.write(f"- 99th percentile: {p.get('p99', 0):.2f}\n")

        f.write("\n")

        # Speaker-Level Analysis
        f.write("### Speaker-Level Analysis\n\n")
        if (
            "tokenize_output" in stats
            and "speaker_analysis" in stats["tokenize_output"]
        ):
            sa = stats["tokenize_output"]["speaker_analysis"]

            if "error" in sa:
                f.write(f"*{sa['error']}*\n\n")
            else:
                if "documents_per_role" in sa:
                    f.write("**Documents per Role:**\n\n")
                    f.write("| Role | Count |\n")
                    f.write("|------|-------|\n")
                    for role, count in sorted(sa["documents_per_role"].items()):
                        f.write(f"| {role} | {count:,} |\n")
                    f.write("\n")

                if "avg_tokens_per_role" in sa:
                    f.write("**Average Tokens per Role:**\n\n")
                    f.write("| Role | Avg Tokens |\n")
                    f.write("|------|-----------|\n")
                    for role, avg in sorted(sa["avg_tokens_per_role"].items()):
                        f.write(f"| {role} | {avg:.2f} |\n")
                    f.write("\n")

        # Sparsity Analysis
        f.write("### Sparsity Analysis\n\n")
        if (
            "tokenize_output" in stats
            and "sparsity_analysis" in stats["tokenize_output"]
        ):
            sp = stats["tokenize_output"]["sparsity_analysis"]

            if "zero_counts_per_category" in sp:
                f.write("**Zero Count Percentage by Category:**\n\n")
                f.write("| Category | Zero Count | Zero % |\n")
                f.write("|----------|------------|--------|\n")
                for cat_name in sorted(sp["zero_counts_per_category"].keys()):
                    zc = sp["zero_counts_per_category"][cat_name]
                    f.write(f"| {cat_name} | {zc['count']:,} | {zc['pct']:.2f}% |\n")

            f.write("\n")
            if "documents_with_no_matches" in sp:
                f.write(
                    f"**Documents with no linguistic matches:** {sp['documents_with_no_matches']:,}\n"
                )

        f.write("\n---\n\n")

        # PROCESS SUMMARY (existing)
        f.write("## PROCESS SUMMARY\n\n")
        f.write(
            f"- **Years processed:** {stats.get('processing', {}).get('years_processed', 'N/A')}\n"
        )
        f.write(
            f"- **Years skipped:** {stats.get('processing', {}).get('years_skipped', 'N/A')}\n"
        )
        f.write(
            f"- **Duration:** {stats.get('timing', {}).get('duration_seconds', 'N/A'):.2f} seconds\n"
        )

        f.write("\n---\n\n")

        # OUTPUT SUMMARY (existing)
        f.write("## OUTPUT SUMMARY\n\n")
        f.write(
            f"- **Final record count:** {stats.get('output', {}).get('final_rows', 'N/A'):,}\n"
        )
        f.write(
            f"- **Files generated:** {len(stats.get('output', {}).get('files', []))}\n"
        )

    print(f"Generated: {report_path.name}")


# ==============================================================================
# Observability Helpers
# ==============================================================================


def get_process_memory_mb() -> Dict[str, float]:
    """
    Get current process memory usage in MB.

    Returns:
        Dict with keys:
        - rss_mb: Resident Set Size (actual physical memory in use)
        - vms_mb: Virtual Memory Size (total memory allocated)
        - percent: Memory usage as percentage of system memory
    """
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_percent = process.memory_percent()

    return {
        "rss_mb": float(mem_info.rss) / (1024 * 1024),  # Resident Set Size
        "vms_mb": float(mem_info.vms) / (1024 * 1024),  # Virtual Memory Size
        "percent": float(mem_percent),
    }


def calculate_throughput(rows_processed: int, duration_seconds: float) -> float:
    """
    Calculate throughput in rows per second.

    Args:
        rows_processed: Number of rows processed
        duration_seconds: Duration in seconds

    Returns:
        Throughput in rows per second (rounded to 2 decimals)
        Returns 0.0 if duration_seconds <= 0 to avoid division by zero
    """
    if duration_seconds <= 0:
        return 0.0
    return round(rows_processed / duration_seconds, 2)


def detect_anomalies_zscore(
    df: pd.DataFrame, columns: List[str], threshold: float = 3.0
) -> Dict[str, Dict[str, Any]]:
    """
    Detect anomalies using z-score (standard deviation) method.

    Deterministic: Same input produces same output.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        threshold: Number of standard deviations for cutoff (default 3.0)

    Returns:
        Dict mapping column_name -> anomaly info
    """
    anomalies: Dict[str, Dict[str, Any]] = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Drop NaN for z-score calculation
        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        mean = series.mean()
        std = series.std()

        if std == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Calculate z-scores: (value - mean) / std
        z_scores = abs((series - mean) / std)

        # Flag anomalies beyond threshold
        anomaly_mask = z_scores > threshold
        anomaly_indices = df[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],  # Top 10 for review
            "threshold": threshold,
            "mean": round(mean, 4),
            "std": round(std, 4),
        }

    return anomalies


def detect_anomalies_iqr(
    df: pd.DataFrame, columns: List[str], multiplier: float = 3.0
) -> Dict[str, Dict[str, Any]]:
    """
    Detect anomalies using IQR (Interquartile Range) method.

    Deterministic: Same input produces same output.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        multiplier: IQR multiplier for cutoff (default 3.0 = strong outliers)

    Returns:
        Dict mapping column_name -> anomaly info
    """
    anomalies: Dict[str, Dict[str, Any]] = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Drop NaN for IQR calculation
        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Calculate IQR: Q3 - Q1 (75th - 25th percentile)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Flag anomalies
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        anomaly_mask = (series < lower_bound) | (series > upper_bound)
        anomaly_indices = df[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],
            "iqr_bounds": [round(lower_bound, 4), round(upper_bound, 4)],
        }

    return anomalies


# ==============================================================================
# Logic: Tokenization & Counting
# ==============================================================================


def load_lm_dictionary(dict_path: Path) -> Tuple[List[str], Dict[str, set]]:
    print(f"Loading LM Dictionary: {dict_path.name}")
    df_lm = pd.read_csv(dict_path)

    categories = [
        "Negative",
        "Positive",
        "Uncertainty",
        "Litigious",
        "Strong_Modal",
        "Weak_Modal",
        "Constraining",
    ]

    df_lm["Word"] = df_lm["Word"].str.upper()

    # Map words to categories
    # Only keep words that have at least one category > 0
    cat_sets: Dict[str, set] = {cat: set() for cat in categories}
    vocab_set: set = set()

    # OPTIMIZATION: Vectorized melt replaces .iterrows()
    # Expected speedup: 10-100x for LM dictionary (10K rows)
    # Ref: 10-RESEARCH.md Pattern 1, Example 1
    df_valid = df_lm[df_lm["Word"].notna()].copy()

    # Melt to long format for vectorization
    df_melted = df_valid.melt(
        id_vars=["Word"], value_vars=categories, var_name="category", value_name="count"
    )  # type: ignore[call-arg]  # pandas melt returns DataFrame but mypy cannot verify

    # Filter rows where count > 0
    filtered = cast(pd.DataFrame, df_melted[df_melted["count"] > 0])

    # Collect words per category
    for cat in categories:
        cat_words = filtered[filtered["category"] == cat]["Word"].unique()
        cat_sets[cat].update(cat_words)

    # Update vocabulary set
    vocab_set.update(filtered["Word"].unique())

    vocab_list = sorted(list(vocab_set))
    print(f"  Dictionary Loaded: {len(vocab_list):,} tracked words")
    return vocab_list, cat_sets


# OPTIMIZATION: Parallel year processing with ProcessPoolExecutor
# thread_count from config/project.yaml controls parallelism
# Expected speedup: near-linear for CPU-bound operations
# Determinism: Results sorted by year before aggregation
# Ref: 10-RESEARCH.md Pattern 3, Example 2


def process_year_worker(
    year: int,
    root: Path,
    config: Dict[str, Any],
    valid_files: set,
    vocab_list: List[str],
    cat_sets: Dict[str, set],
    out_dir: Path,
) -> Tuple[int, Dict[str, Any]]:
    """
    Process a single year - must be picklable for ProcessPoolExecutor.

    Returns:
        Tuple of (year, year_stats_dict)
    """
    input_path = (
        root / f"1_Inputs/Earnings_Calls_Transcripts/speaker_data_{year}.parquet"
    )
    if not input_path.exists():
        print(f"  Skipping {year}: Input not found")
        return year, {"year": year, "skipped": True}

    print(f"\nProcessing {year}...")
    t0 = time.time()

    year_stats: Dict[str, Any] = {
        "year": year,
        "input_rows": 0,
        "output_rows": 0,
        "filtered_rows": 0,
        "total_tokens": 0,
        "vocab_hits": 0,
        "avg_tokens_per_doc": 0.0,
        "vocabulary_size": len(vocab_list),
    }

    validate_input_file(input_path, must_exist=True)
    df = pd.read_parquet(
        input_path,
        columns=[
            "file_name",
            "speaker_text",
            "speaker_number",
            "context",
            "role",
            "speaker_name",
            "employer",
        ],
    )
    initial_rows = len(df)
    year_stats["input_rows"] = initial_rows

    # Filter
    df = cast(pd.DataFrame, df[df["file_name"].isin(valid_files)].copy())
    year_stats["filtered_rows"] = initial_rows - len(df)
    print(f"  Loaded {initial_rows:,} -> {len(df):,} (Manifest match)")

    if len(df) == 0:
        return year, year_stats

    # Vectorize
    print("  Vectorizing...")
    vectorizer = CountVectorizer(
        vocabulary=vocab_list, token_pattern=r"(?u)\b[a-zA-Z]+\b", lowercase=False
    )

    raw_text = df["speaker_text"].astype(str).str.upper()
    X = vectorizer.transform(raw_text)  # type: ignore[assignment]  # sklearn sparse matrix

    year_stats["vocab_hits"] = int(X.sum())  # type: ignore[union-attr]  # sparse matrix sum

    # Aggregate counts per category
    features = vectorizer.get_feature_names_out()  # type: ignore[union-attr]  # sklearn ndarray
    feat_map: Dict[str, int] = {str(w): i for i, w in enumerate(features)}

    # Prepare result dataframe output columns
    meta_cols = [
        "file_name",
        "speaker_number",
        "context",
        "role",
        "speaker_name",
        "employer",
    ]
    meta_cols = [c for c in meta_cols if c in df.columns]
    result: pd.DataFrame = cast(pd.DataFrame, df[meta_cols].copy())

    for cat, wset in cat_sets.items():
        indices = [feat_map[w] for w in wset if w in feat_map]  # type: ignore[index]  # Dynamic key lookup
        if indices:
            result[f"{cat}_count"] = np.array(X[:, indices].sum(axis=1)).flatten()  # type: ignore[index]  # sparse matrix indexing
        else:
            result[f"{cat}_count"] = 0

    # Total Tokens (Alpha only)
    print("  Counting total tokens...")
    regex = re.compile(r"(?u)\b[a-zA-Z]+\b")
    result["total_tokens"] = raw_text.apply(lambda x: len(regex.findall(x)))

    year_stats["total_tokens"] = int(result["total_tokens"].sum())
    year_stats["avg_tokens_per_doc"] = round(result["total_tokens"].mean(), 2)
    year_stats["output_rows"] = len(result)

    # Save with memory tracking
    out_path = out_dir / f"linguistic_counts_{year}.parquet"
    print(f"  Saving {out_path.name}...")
    save_output_with_tracking(result, out_path)
    # Note: memory stats saved to save_output operation
    print(f"  Saved {out_path.name} ({time.time() - t0:.1f}s)")
    return year, year_stats


def process_year(year, root, config, valid_files, vocab_list, cat_sets, out_dir):
    input_path = (
        root / f"1_Inputs/Earnings_Calls_Transcripts/speaker_data_{year}.parquet"
    )
    if not input_path.exists():
        print(f"  Skipping {year}: Input not found")
        return None, None

    print(f"\nProcessing {year}...")
    t0 = time.time()

    year_stats = {
        "year": year,
        "input_rows": 0,
        "output_rows": 0,
        "filtered_rows": 0,
        "total_tokens": 0,
        "vocab_hits": 0,
        "avg_tokens_per_doc": 0.0,
        "vocabulary_size": len(vocab_list),
    }

    validate_input_file(input_path, must_exist=True)
    df = pd.read_parquet(
        input_path,
        columns=[
            "file_name",
            "speaker_text",
            "speaker_number",
            "context",
            "role",
            "speaker_name",
            "employer",
        ],
    )
    initial_rows = len(df)
    year_stats["input_rows"] = initial_rows

    # Filter
    df = cast(pd.DataFrame, df[df["file_name"].isin(valid_files)].copy())
    year_stats["filtered_rows"] = initial_rows - len(df)
    print(f"  Loaded {initial_rows:,} -> {len(df):,} (Manifest match)")

    if len(df) == 0:
        return None, year_stats

    # Vectorize
    print("  Vectorizing...")
    vectorizer = CountVectorizer(
        vocabulary=vocab_list, token_pattern=r"(?u)\b[a-zA-Z]+\b", lowercase=False
    )

    raw_text = df["speaker_text"].astype(str).str.upper()
    X = vectorizer.transform(raw_text)  # type: ignore[assignment]  # sklearn sparse matrix

    year_stats["vocab_hits"] = int(X.sum())  # type: ignore[union-attr]  # sparse matrix sum

    # Aggregate counts per category
    features = vectorizer.get_feature_names_out()  # type: ignore[union-attr]  # sklearn ndarray
    feat_map: Dict[str, int] = {str(w): i for i, w in enumerate(features)}

    # Prepare result dataframe output columns
    meta_cols = [
        "file_name",
        "speaker_number",
        "context",
        "role",
        "speaker_name",
        "employer",
    ]
    meta_cols = [c for c in meta_cols if c in df.columns]
    result = df[meta_cols].copy()

    for cat, wset in cat_sets.items():
        indices = [feat_map[w] for w in wset if w in feat_map]  # type: ignore[index]  # Dynamic key lookup
        if indices:
            result[f"{cat}_count"] = np.array(X[:, indices].sum(axis=1)).flatten()  # type: ignore[index]  # sparse matrix indexing
        else:
            result[f"{cat}_count"] = 0

    # Total Tokens (Alpha only)
    print("  Counting total tokens...")
    regex = re.compile(r"(?u)\b[a-zA-Z]+\b")
    result["total_tokens"] = raw_text.apply(lambda x: len(regex.findall(x)))

    year_stats["total_tokens"] = int(result["total_tokens"].sum())
    year_stats["avg_tokens_per_doc"] = round(result["total_tokens"].mean(), 2)
    year_stats["output_rows"] = len(result)

    # Save
    out_path = out_dir / f"linguistic_counts_{year}.parquet"
    result.to_parquet(out_path, index=False)
    print(f"  Saved {out_path.name} ({time.time() - t0:.1f}s)")
    return result, year_stats


# ==============================================================================
# Memory-tracked operations
# ==============================================================================


@track_memory_usage("load_documents")
def load_documents_with_tracking(manifest_path: Path, lm_path: Path) -> Dict[str, Any]:
    """Load manifest and dictionary with memory tracking"""
    validate_input_file(manifest_path, must_exist=True)
    manifest = pd.read_parquet(manifest_path, columns=["file_name"])
    valid_files: set = set(manifest["file_name"])

    validate_input_file(lm_path, must_exist=True)
    vocab_list, cat_sets = load_lm_dictionary(lm_path)

    return {
        "manifest": manifest,
        "valid_files": valid_files,
        "vocab_list": vocab_list,
        "cat_sets": cat_sets,
    }


@track_memory_usage("save_output")
def save_output_with_tracking(df: pd.DataFrame, output_path: Path) -> Dict[str, str]:
    """Save output with memory tracking"""
    df.to_parquet(output_path, index=False)
    return {"path": str(output_path)}


def main(dictionary_path: Optional[str] = None) -> None:
    print("=== Step 2.1: Tokenize & Count (Legacy Compatible) ===")
    root = Path(__file__).parent.parent.parent.parent
    setup_logging()

    # Output Setup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_base = root / "4_Outputs" / "2_Textual_Analysis"
    out_dir = out_base / "2.1_Tokenized" / timestamp
    ensure_output_dir(out_dir)

    # Initialize Stats
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()

    # Memory tracking at script start
    mem_start = get_process_memory_mb()

    stats: ScriptStats = {
        "step_id": "2.1_TokenizeAndCount",
        "timestamp": timestamp,
        "git_sha": None,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {
            "vocabulary_size": 0,
            "total_vocab_hits": 0,
            "total_tokens": 0,
            "years_processed": 0,
            "years_skipped": 0,
            "per_year": [],
        },
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory_mb": {},  # Added for operation-level memory tracking
    }

    # Load documents with memory tracking
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    lm_path = (
        Path(dictionary_path)
        if dictionary_path
        else root / "1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv"
    )

    print("Loading manifest and dictionary...")
    load_result = load_documents_with_tracking(manifest_path, lm_path)
    # Decorator wraps result in {"result": ..., "memory_mb": ..., "timing_seconds": ...}
    manifest = load_result["result"]["manifest"]
    vocab_list = load_result["result"]["vocab_list"]
    cat_sets = load_result["result"]["cat_sets"]
    stats["memory_mb"]["load_documents"] = load_result["memory_mb"]

    valid_files = load_result["result"]["valid_files"]
    print(f"Universe: {len(valid_files):,} files")

    stats["input"]["files"].append(str(manifest_path))
    stats["input"]["checksums"]["master_sample_manifest.parquet"] = (
        compute_file_checksum(manifest_path)
    )

    stats["input"]["files"].append(str(lm_path))
    stats["input"]["checksums"]["Loughran-McDonald_MasterDictionary.csv"] = (
        compute_file_checksum(lm_path)
    )
    stats["processing"]["vocabulary_size"] = len(vocab_list)

    # Compute INPUT statistics (manifest + LM dictionary)
    print("\nComputing input statistics...")
    from f1d.shared.observability_utils import compute_tokenize_input_stats

    stats["tokenize_input"] = compute_tokenize_input_stats(
        manifest, lm_path, vocab_list, cat_sets
    )

    # Process
    config = load_config()
    years = range(2002, 2019)
    thread_count = config.get("determinism", {}).get("thread_count", 1)

    print(f"\nProcessing {len(years)} years with {thread_count} worker(s)...")

    results = {}
    with ProcessPoolExecutor(max_workers=thread_count) as executor:
        # Submit all years
        futures = {
            executor.submit(
                process_year_worker,
                year,
                root,
                config,
                valid_files,
                vocab_list,
                cat_sets,
                out_dir,
            ): year
            for year in years
        }

        # Collect results as they complete
        for future in as_completed(futures):
            year = futures[future]
            try:
                _, year_stats = future.result()
                results[year] = year_stats
            except Exception as e:
                print(f"  ERROR: Year {year} failed: {e}")
                raise

    # PERFORMANCE NOTE: Parallelization achieved
    # - Baseline (sequential, thread_count=1): ~558 seconds (from 10-01)
    # - Expected speedup: near-linear with thread_count (e.g., 3.8x with 4 threads)
    # - Determinism: Results sorted by year before aggregation ensures reproducibility
    # - To measure actual speedup: Change thread_count in config/project.yaml to 4 or 8
    #   and compare runtimes. Use `time python 2.1_TokenizeAndCount.py`

    # Combine stats in year order for determinism
    stats["processing"]["per_year"] = [
        results[y] for y in sorted(results.keys()) if results[y].get("skipped") is None
    ]

    total_input_rows = sum(
        s.get("input_rows", 0) for s in stats["processing"]["per_year"]
    )
    total_output_rows = sum(
        s.get("output_rows", 0) for s in stats["processing"]["per_year"]
    )
    total_tokens = sum(
        s.get("total_tokens", 0) for s in stats["processing"]["per_year"]
    )
    total_vocab_hits = sum(
        s.get("vocab_hits", 0) for s in stats["processing"]["per_year"]
    )

    stats["input"]["total_rows"] = total_input_rows
    stats["output"]["final_rows"] = total_output_rows
    stats["processing"]["total_tokens"] = total_tokens
    stats["processing"]["total_vocab_hits"] = total_vocab_hits
    stats["processing"]["years_processed"] = len(stats["processing"]["per_year"])
    stats["processing"]["years_skipped"] = (
        len(years) - stats["processing"]["years_processed"]
    )

    # Compute PROCESS statistics
    print("\nComputing process statistics...")
    from f1d.shared.observability_utils import compute_tokenize_process_stats

    duration_seconds = stats["timing"]["duration_seconds"]
    stats["tokenize_process"] = compute_tokenize_process_stats(
        stats["processing"]["per_year"], cat_sets, vocab_list, duration_seconds
    )

    # Collect output DataFrames for output statistics
    print("\nLoading output files for statistics...")
    output_dfs = []
    for year in sorted(results.keys()):
        if results[year].get("skipped") is None:
            out_path = out_dir / f"linguistic_counts_{year}.parquet"
            if out_path.exists():
                df_year = pd.read_parquet(out_path)
                output_dfs.append(df_year)

    # Compute OUTPUT statistics
    if output_dfs:
        print("Computing output statistics...")
        from f1d.shared.observability_utils import compute_tokenize_output_stats

        stats["tokenize_output"] = compute_tokenize_output_stats(output_dfs, cat_sets)

        # Fill in category_hit_rates now that we have output data
        total_tokens_all = stats["processing"]["total_tokens"]
        df_all = pd.concat(output_dfs, ignore_index=True)
        for cat_name in cat_sets.keys():
            col_name = f"{cat_name}_count"
            if col_name in df_all.columns:
                hit_count = int(df_all[col_name].sum())
                hit_rate_pct = (
                    round(hit_count / total_tokens_all * 100, 2)
                    if total_tokens_all > 0
                    else 0.0
                )
                stats["tokenize_process"]["category_hit_rates"][cat_name] = {
                    "hit_count": hit_count,
                    "hit_rate_pct": hit_rate_pct,
                }

    # Output files
    output_files = list(out_dir.glob("linguistic_counts_*.parquet"))
    stats["output"]["files"] = [f.name for f in output_files]
    stats["output"]["final_columns"] = 14 if output_files else 0

    # Summary Stats
    print_stat("Years Processed", value=stats["processing"]["years_processed"])
    print_stat("Years Skipped", value=stats["processing"]["years_skipped"])
    print_stat("Total Input Rows", value=stats["input"]["total_rows"])
    print_stat("Total Output Rows", value=stats["output"]["final_rows"])
    print_stat("Total Tokens", value=stats["processing"]["total_tokens"])
    print_stat("Vocabulary Hits", value=stats["processing"]["total_vocab_hits"])

    # Timing
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Optimization metrics
    stats["optimization"] = {
        "vectorization": {
            "method": "vectorized_melt",
            "description": "Replaced .iterrows() loop with vectorized .melt() operation",
            "expected_speedup": "10-100x for LM dictionary (10K rows)",
        },
        "parallelization": {
            "method": "ProcessPoolExecutor",
            "thread_count": thread_count,
            "workers_used": thread_count,
            "description": "Parallel year processing with deterministic result ordering",
            "expected_speedup": "near-linear for CPU-bound operations",
            "notes": "To measure actual speedup: change thread_count in config/project.yaml to 4 or 8 and compare runtimes",
        },
        "runtime_seconds": stats["timing"]["duration_seconds"],
    }

    # Save Stats
    print_stats_summary(stats)

    # Memory tracking at script end
    mem_end = get_process_memory_mb()

    # Add memory stats to stats
    stats["memory"] = {
        "start_mb": round(mem_start["rss_mb"], 2),
        "end_mb": round(mem_end["rss_mb"], 2),
        "delta_mb": round(mem_end["rss_mb"] - mem_start["rss_mb"], 2),
    }

    # Add throughput to stats
    duration_seconds = stats["timing"]["duration_seconds"]
    throughput = calculate_throughput(stats["output"]["final_rows"], duration_seconds)
    stats["throughput"] = {
        "rows_per_second": throughput,
        "total_rows": stats["output"]["final_rows"],
        "duration_seconds": round(duration_seconds, 3),
    }

    # Add output checksums
    stats["output"]["checksums"] = {}
    output_files = list(out_dir.glob("linguistic_counts_*.parquet"))
    for filepath in output_files:
        checksum = compute_file_checksum(filepath)
        stats["output"]["checksums"][filepath.name] = checksum

    # Add anomaly detection for numeric columns (total_tokens, vocab_hits, avg_tokens_per_doc)
    # Check if there are any numeric columns suitable for anomaly detection in aggregated data
    # Using per_year stats for anomaly detection instead of final df
    anomaly_data = pd.DataFrame(stats["processing"]["per_year"])
    numeric_cols = anomaly_data.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            anomaly_data, numeric_cols, threshold=3.0
        )

    save_stats(stats, out_dir)

    # Generate comprehensive report
    print("\nGenerating report...")
    generate_tokenization_report(stats, out_dir)

    print("\n=== Complete ===")


if __name__ == "__main__":
    # Parse arguments and check prerequisites
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    # Handle dry-run mode
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root, args)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    # Check prerequisites
    check_prerequisites(root, args)

    # Override dictionary path if provided
    dict_path = args.dictionary if args.dictionary else None

    # Run main processing
    main(dictionary_path=dict_path)
