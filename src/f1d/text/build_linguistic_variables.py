#!/usr/bin/env python3
"""
==============================================================================
STEP 2.2: Construct Linguistic Variables
==============================================================================
ID: 2.2_ConstructVariables
Description: Constructs linguistic variables from word frequency data.

Purpose: Aggregates word-level statistics into call-level linguistic
         measures for regression analysis.

Inputs:
    - outputs/2.1_TokenizeAndCount/latest/word_counts.parquet
    - Linguistic dictionary files

Outputs:
    - outputs/2_Textual_Analysis/2.2_Variables/{timestamp}/linguistic_variables.parquet
    - stats.json
    - {timestamp}.log

Dependencies:
    - Requires: Step 2.1
    - Uses: f1d.shared.*, pandas, numpy

Deterministic: true

Location: src/f1d/text/construct_variables.py (migrated from legacy 2_Text/)

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

# TYPE ERROR BASELINE: 2 remaining errors (down from 20)
# Remaining type errors are library limitations:
# - pandas DataFrame operations: mypy cannot infer types after groupby/merge
# - Lines 481, 491: groupby().sum() returns DataFrame but mypy cannot verify column indexing
# All type ignores below are scoped with specific error codes
#
# Fixed in 77-15: Added explicit Dict[str, Any] type annotation to stats variable
# to resolve index assignment errors throughout main() function.

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Union, cast

import numpy as np
import pandas as pd
import psutil

# Note: MemoryAwareThrottler from f1d.shared.chunked_reader is available for future chunked processing.
# Current implementation uses column pruning for memory optimization, avoiding complex refactoring required for process_in_chunks().

# Import shared path validation utilities
from f1d.shared.output_schemas import validate_linguistic_variables
from f1d.shared.observability import (
    DualWriter,
    compute_constructvariables_input_stats,
    compute_constructvariables_output_stats,
    compute_constructvariables_process_stats,
)
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
    validate_output_path,
)

# ==============================================================================
# Setup
# ==============================================================================


def setup_logging():
    log_dir = (
        Path(__file__).parent.parent.parent.parent / "logs" / "2.2_ConstructVariables"
    )
    ensure_output_dir(log_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = log_dir / f"{timestamp}.log"

    sys.stdout = DualWriter(log_path)
    return log_path


def parse_arguments():
    """Parse command-line arguments for construct_variables.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 2.2: Construct Text Variables

Constructs text-based variables from word counts (clarity, tone,
complexity). Calculates linguistic measures for regression
analysis (fog index, word length, etc.).
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )
    parser.add_argument(
        "--year-start",
        type=int,
        default=2002,
        help="First year to process (default: 2002)",
    )
    parser.add_argument(
        "--year-end",
        type=int,
        default=2018,
        help="Last year to process inclusive (default: 2018)",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from f1d.shared.dependency_checker import validate_prerequisites
    from f1d.shared.path_utils import get_latest_output_dir

    required_files = {}

    # Check tokenized files from step 2.1
    get_latest_output_dir(
        root / "outputs" / "2_Textual_Analysis" / "2.1_Tokenized",
        required_file="linguistic_counts_2002.parquet",
    )

    # Check manifest from step 1.4
    get_latest_output_dir(
        root / "outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )

    # No file-based prerequisites: manager classification now uses BGT (2018)
    # verbatim presentation rule + F1+F2+F3 filters + per-call pres roster,
    # no external keyword list required.
    validate_prerequisites({}, {})


def compute_file_checksum(filepath, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
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
        print(f"\n{'Processing Step':<30} {'Removed':>10}")
        print("-" * 42)
        for step, count in stats["processing"].items():
            print(f"{step:<30} {count:>10,}")
    print("=" * 60)


def save_stats(stats, out_dir):
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


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


def detect_anomalies_zscore(df, columns, threshold=3.0):
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
    anomalies = {}

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
        # Get indices from the series (which has NaNs dropped)
        anomaly_indices = series[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],  # Top 10 for review
            "threshold": threshold,
            "mean": round(mean, 4),
            "std": round(std, 4),
        }

    return anomalies


def detect_anomalies_iqr(df, columns, multiplier=3.0):
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
    anomalies = {}

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
        upper_bound = q3 - multiplier * iqr

        anomaly_mask = (series < lower_bound) | (series > upper_bound)
        # Get indices from the series (which has NaNs dropped)
        anomaly_indices = series[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],
            "iqr_bounds": [round(lower_bound, 4), round(upper_bound, 4)],
        }

    return anomalies


# ==============================================================================
# Helper Loading Functions
# ==============================================================================


# Strip professional credential suffixes (", CPA", ", Jr.", ", III", ", CFA", ...)
# from executive names before last-name extraction.
# Affects 30.0% of CFOs (11,715 / 39,067) and 14.2% of CEOs (8,766 / 61,790)
# in Execucomp; without stripping, naive str.split()[-1] returns "cpa" instead
# of the real last name and breaks last-name matching.
CREDENTIAL_SUFFIX_PAT = re.compile(
    r"(?:,\s*(?:CPA|MBA|Ph\.?D\.?|Jr\.?|Sr\.?|III|IV|II|CFA|CA|Esq\.?|DDS|JD|MD|CMA|CIA)\.?)+\s*$",
    re.IGNORECASE,
)


def _strip_credentials(name_series: pd.Series) -> pd.Series:
    """Strip trailing professional credential suffixes from a name Series."""
    return (
        name_series.fillna("")
        .str.replace(CREDENTIAL_SUFFIX_PAT, "", regex=True)
        .str.strip()
    )


def load_executive_map(root):
    """Load manifest with CEO/prev-CEO data and merge in Execucomp CFO records.

    Returns a DataFrame keyed by file_name with cleaned (credential-stripped)
    name fields for CEO, prev-CEO, and CFO matching downstream.
    """
    manifest_dir = get_latest_output_dir(
        root / "outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    validate_input_file(manifest_path, must_exist=True)
    df = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "ceo_name",
            "prev_ceo_name",
            "gvkey",
            "conm",
            "sic",
            "start_date",
        ],
    )

    # Strip credential suffixes BEFORE extracting last names (bugfix:
    # ~14% of CEO records have trailing ", CPA" / ", Jr." etc. that the
    # naive str.split()[-1] would otherwise return as the "last name").
    df["ceo_name_clean"] = _strip_credentials(df["ceo_name"])
    df["prev_ceo_name_clean"] = _strip_credentials(df["prev_ceo_name"])
    df["ceo_last"] = df["ceo_name_clean"].str.split().str[-1].str.lower()
    df["prev_ceo_last"] = df["prev_ceo_name_clean"].str.split().str[-1].str.lower()
    df["ceo_name_lower"] = df["ceo_name_clean"].str.lower()
    df["prev_ceo_name_lower"] = df["prev_ceo_name_clean"].str.lower()

    # Extract Year from start_date
    df["year"] = pd.to_datetime(df["start_date"]).dt.year

    # Load Execucomp CFO records (cfoann == "CFO" flag)
    exec_path = root / "inputs" / "Execucomp" / "comp_execucomp.parquet"
    validate_input_file(exec_path, must_exist=True)
    exec_df = pd.read_parquet(
        exec_path, columns=["gvkey", "year", "exec_fullname", "cfoann"]
    )
    cfo_df = (
        exec_df[exec_df["cfoann"] == "CFO"][["gvkey", "year", "exec_fullname"]]
        .rename(columns={"exec_fullname": "cfo_name"})
        .sort_values(["gvkey", "year", "cfo_name"])
        # 127 firm-years (0.3%) have >1 CFO; pick first alphabetically.
        # Documented sub-issue; not blocking.
        .drop_duplicates(["gvkey", "year"])
    )
    # gvkey is object/str in both Execucomp and manifest
    df = df.merge(cfo_df, on=["gvkey", "year"], how="left")
    df["cfo_name_clean"] = _strip_credentials(df["cfo_name"])
    df["cfo_name_lower"] = df["cfo_name_clean"].str.lower()
    df["cfo_last"] = df["cfo_name_clean"].str.split().str[-1].str.lower()

    return df


# ==============================================================================
# Flagging Logic
# ==============================================================================


def flag_speakers(df, manifest_df):
    # Merge manifest info for context (company name, ceo/cfo names)
    cols_to_merge = [
        "file_name",
        "conm",
        "ceo_name_lower",
        "prev_ceo_name_lower",
        "ceo_last",
        "prev_ceo_last",
        "cfo_name_lower",
        "cfo_last",
    ]
    # Merge only columns that are NOT in df already (except key)
    cols_to_merge = [
        c for c in cols_to_merge if c not in df.columns or c == "file_name"
    ]

    df = df.merge(manifest_df[cols_to_merge], on="file_name", how="left")

    # Fill NA
    role = df["role"].fillna("")
    employer = df["employer"].fillna("")
    speaker_name = df["speaker_name"].fillna("")

    # Analyst (legacy role-based, kept unchanged for the Analyst sample)
    df["is_analyst"] = role.str.contains("analyst", case=False)
    df["is_operator"] = role.str.contains("operator", case=False)

    # CEO (Tiered: exact full-name OR last-name)
    speaker_lower = speaker_name.str.lower()
    speaker_last = speaker_name.str.split().str[-1].str.lower()
    is_ceo_exact = (speaker_lower == df["ceo_name_lower"]) | (
        speaker_lower == df["prev_ceo_name_lower"]
    )
    is_ceo_last = (speaker_last == df["ceo_last"]) | (
        speaker_last == df["prev_ceo_last"]
    )
    df["is_ceo"] = is_ceo_exact | is_ceo_last

    # ============================================================
    # CFO classification (Execucomp cfoann + tiered match)
    # ============================================================
    # Dual CEO+CFO persons (424 person-years in Execucomp) are counted in
    # BOTH samples per DWZ (2021) convention — no exclusion filter.
    is_cfo_exact = speaker_lower == df["cfo_name_lower"].fillna("")
    is_cfo_last = (speaker_last == df["cfo_last"].fillna("")) & (
        df["cfo_last"].notna() & (df["cfo_last"] != "")
    )
    df["is_cfo"] = is_cfo_exact | is_cfo_last

    # ============================================================
    # Manager classification (BGT 2018 + F1+F2+F3 + pres roster)
    # ============================================================
    # Replaces the legacy 45-keyword role-string regex on 2026-04-09 after
    # validation showed Pearson 0.94+ correlation with the legacy measure
    # across all 8 LM categories and a procedural-precedent grounding in
    # Bushee-Gow-Taylor (2018, JAR).
    placeholders = {
        "Operator",
        "Unidentified",
        "Unidentified Participant",
        "Unidentified Audience Member",
        "Unidentified Speaker",
        "Unidentified Company Representative",
        "??",
        "Editor",
        "Moderator",
        "Caller",
        "Unknown Speaker",
        "Company Executive",
        "Company Representative",
        "Corporate Participant",
        "Analyst",
        "Conference Facilitator",
        "Unidentified Analyst",
    }

    sn_clean = speaker_name.str.strip().str.rstrip(",").str.strip()
    sn_lower = sn_clean.str.lower()

    # F1: placeholder + operator filter
    is_ph = (
        sn_clean.isna()
        | (sn_clean == "")
        | sn_clean.isin(placeholders)
        | sn_clean.str.contains("nidentified", na=False)
        | sn_lower.isin({"operator", "unknown"})
    )

    # F2: role-based analyst exclusion
    # Tightened: \bresearch\b would wrongly exclude "EVP of Research & Development"
    # at pharma firms. Restrict to analyst-compound contexts only.
    role_analyst_pat = (
        r"\banalyst\b|"
        r"\bresearch\s+(?:analyst|associate|division|head|director)\b|"
        r"\bhead\s+of\s+research\b|"
        r"\b(?:equity|quantitative|sell.?side|buy.?side)\s+research\b|"
        r"\bsell.?side\b|\bbuy.?side\b|\bstrategist\b"
    )
    role_is_analyst = role.str.contains(
        role_analyst_pat, regex=True, case=False, na=False
    )

    # F3: employer-based analyst exclusion
    # The literal "securities," (with comma) is intentional — Capital IQ
    # employer strings nearly always include the comma between firm name
    # and corporate suffix ("Wells Fargo Securities, LLC" etc.). Empirical
    # test on 2014 Q&A: original 23,527 turns vs "fixed" 19,349 — original
    # is correct (red team finding #6 falsified).
    emp_analyst_pat = (
        r"research division|equity research|capital markets|"
        r"securities,|securities llc|securities inc|securities ltd|"
        r", llc, research|brokerage|sell.?side"
    )
    emp_is_analyst = employer.str.contains(
        emp_analyst_pat, regex=True, case=False, na=False
    )

    passes_f123 = (
        (~is_ph)
        & (sn_clean != "Operator")
        & (~role_is_analyst)
        & (~emp_is_analyst)
    )
    df["passes_f123"] = passes_f123
    df["speaker_name_lower_clean"] = sn_lower

    # Per-call pres roster: set of cleaned-lowercased speaker names that
    # appear in the call's presentation section AND pass F123. Q&A turns
    # qualify as Manager only if their speaker name is in this roster.
    pres_qualifying = df[(df["context"] == "pres") & passes_f123]
    roster = (
        pres_qualifying.groupby("file_name")["speaker_name_lower_clean"]
        .apply(set)
        .to_dict()
    )

    # Vectorized per-row roster lookup
    df["in_pres_roster"] = [
        sn in roster.get(fn, set())
        for sn, fn in zip(sn_lower.values, df["file_name"].values)
    ]

    # Manager is context-aware: all pres turns that pass F123, plus Q&A
    # turns whose speaker is in the call's pres roster.
    df["is_manager"] = passes_f123 & (
        (df["context"] == "pres")
        | ((df["context"] == "qa") & df["in_pres_roster"])
    )

    return df


# ==============================================================================
# Aggregation (Weighted - Ratio of Sums)
# ==============================================================================


def aggregate_weighted(
    df: pd.DataFrame,
    sample_mask: pd.Series,
    context_mask: pd.Series,
    count_cols: List[str],
) -> Optional[pd.DataFrame]:
    subset = df[sample_mask & context_mask].copy()
    if len(subset) == 0:
        return None

    # Group by file
    gb = subset.groupby("file_name")

    # Sum Counts and Totals
    sums = gb[count_cols + ["total_tokens"]].sum()  # type: ignore[index]  # mypy cannot verify groupby result indexing

    # Calculate Pct (x100)
    results: Dict[str, Any] = {}
    total_tokens = sums["total_tokens"].replace(0, np.nan)

    for col in count_cols:
        cat = col.replace("_count", "")
        # Variable naming: Sample_Context_Cat_pct
        # We handle sample/context prefix outside
        pct = (sums[col] / total_tokens) * 100.0  # type: ignore[index]  # mypy cannot verify groupby result indexing
        results[f"{cat}_pct"] = pct

    result_df = pd.DataFrame(results)
    result_df.index.name = "file_name"
    result_df = result_df.reset_index()
    return result_df


def process_year(year, root, manifest_df, out_dir, tokenized_dir):
    in_path = tokenized_dir / f"linguistic_counts_{year}.parquet"
    if not in_path.exists():
        print(f"  Skipping {year}: Input not found")
        return None

    print(f"\nProcessing {year}...")
    validate_input_file(in_path, must_exist=True)
    # Column pruning: Load metadata columns and all count columns (dynamic from LM dictionary)
    # First pass: get schema to identify count columns (load empty DataFrame to get column names)
    all_cols = pd.read_parquet(in_path).columns.tolist()
    count_cols = [c for c in all_cols if c.endswith("_count")]
    # Second pass: load only needed columns
    df = pd.read_parquet(
        in_path,
        columns=[
            "file_name",
            "context",
            "role",
            "employer",
            "speaker_name",
            "total_tokens",
        ]
        + count_cols,
    )
    len(df)

    # Flag
    df = flag_speakers(df, manifest_df)

    analyst_count = df["is_analyst"].sum()
    manager_count = df["is_manager"].sum()
    ceo_count = df["is_ceo"].sum()
    operator_count = df["is_operator"].sum()

    print(f"  Analyst: {analyst_count:,}")
    print(f"  Manager: {manager_count:,}")
    print(f"  CEO: {ceo_count:,}")

    # Identify count columns
    count_cols = [c for c in df.columns if c.endswith("_count")]

    # Define Aggregations
    # Legacy mainly cared about: Manager QA, Analyst QA (?), Manager Pres (?)
    # We will generate comprehensive set

    samples = {
        "Manager": df["is_manager"],  # BGT 2018 + F1+F2+F3 + pres roster (2026-04-09)
        "Analyst": df["is_analyst"],
        "CEO": df["is_ceo"],
        "NonCEO_Manager": df["is_manager"] & ~df["is_ceo"],  # Managers excluding CEO
        "Entire": pd.Series(True, index=df.index),
        "CFO": df["is_cfo"],
    }

    contexts = {
        "QA": df["context"] == "qa",
        "Pres": df["context"] == "pres",
        "All": df["context"].isin(["qa", "pres"]),
    }

    # Initialize result with metadata
    # Use manifest metadata
    meta = manifest_df[manifest_df["year"] == year][
        ["file_name", "start_date", "gvkey", "conm", "sic"]
    ].copy()

    variables_created = 0
    for s_name, s_mask in samples.items():
        for c_name, c_mask in contexts.items():
            agg_df = aggregate_weighted(df, s_mask, c_mask, count_cols)
            if agg_df is not None:
                # Rename columns (exclude file_name)
                rename_map = {
                    c: f"{s_name}_{c_name}_{c}"
                    for c in agg_df.columns
                    if c != "file_name"
                }
                agg_df = agg_df.rename(columns=rename_map)
                variables_created += len(rename_map)
                # Merge
                meta = meta.merge(agg_df, on="file_name", how="left")

    # Fill NaN with 0? Or keep NaN for missing sections?
    # Legacy behavior: likely keep NaN or impute.
    # We will keep NaN to distinctions between "No Uncertainty" (0) and "No Text" (NaN).

    # Validate output schema before writing
    meta = validate_linguistic_variables(meta, warn_only=False)

    out_path = out_dir / f"linguistic_variables_{year}.parquet"
    meta.to_parquet(out_path, index=False)
    print(f"  Saved {out_path.name}: {len(meta):,} rows, {variables_created} variables")

    return {
        "rows": len(meta),
        "cols": len(meta.columns),
        "variables_created": variables_created,
        "speaker_flags": {
            "analyst": int(analyst_count),
            "manager": int(manager_count),
            "ceo": int(ceo_count),
            "operator": int(operator_count),
        },
    }


def generate_variable_construction_report(stats, output_path):
    """
    Generate publication-ready markdown report for variable construction.

    Args:
        stats: Statistics dictionary with constructvariables_input,
               constructvariables_process, constructvariables_output keys
        output_path: Path to save the markdown report
    """
    lines = []
    lines.append("# Step 2.2: Construct Variables Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # INPUT DATA section
    lines.append("## INPUT DATA\n")

    if "constructvariables_input" in stats:
        inp = stats["constructvariables_input"]

        # Tokenized Files
        lines.append("### Tokenized Files (from step 2.1)\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        token_stats = inp.get("tokenized_files_stats", {})
        lines.append(f"| Files present | {len(token_stats.get('files_present', []))} |")
        lines.append(f"| Files missing | {len(token_stats.get('files_missing', []))} |")
        lines.append(f"| Total rows | {token_stats.get('total_rows', 0):,} |")
        lines.append(f"| Total tokens | {inp.get('total_tokens_available', 0):,} |\n")

        # Rows per year table
        if token_stats.get("rows_per_year"):
            lines.append("**Rows per year:**\n")
            lines.append("| Year | Rows |")
            lines.append("|------|------|")
            for year, rows in sorted(token_stats["rows_per_year"].items()):
                lines.append(f"| {year} | {rows:,} |")
            lines.append("")

        # Manifest Stats
        lines.append("### Master Manifest (from step 1.0)\n")
        manifest_stats = inp.get("manifest_stats", {})
        if manifest_stats:
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            if "unique_gvkey" in manifest_stats:
                lines.append(
                    f"| Unique companies (gvkey) | {manifest_stats['unique_gvkey']:,} |"
                )
            if "unique_ceos" in manifest_stats:
                lines.append(f"| Unique CEOs | {manifest_stats['unique_ceos']:,} |")
            if "temporal_coverage" in manifest_stats:
                tc = manifest_stats["temporal_coverage"]
                lines.append(
                    f"| Earliest start_date | {tc.get('earliest_start', 'N/A')} |"
                )
                lines.append(f"| Latest start_date | {tc.get('latest_start', 'N/A')} |")
            lines.append("")

        # Linguistic Categories
        lines.append("### Linguistic Categories\n")
        cat_info = inp.get("linguistic_categories", {})
        lines.append(f"- **Total categories:** {cat_info.get('count', 0)}")
        sample_cats = cat_info.get("sample_categories", [])
        if sample_cats:
            lines.append(f"- **Sample categories:** {', '.join(sample_cats)}")
        all_cats = cat_info.get("category_names", [])
        if all_cats:
            lines.append(f"- **All categories:** {', '.join(all_cats)}")
        lines.append("")

    # VARIABLE CONSTRUCTION PROCESS section
    lines.append("## VARIABLE CONSTRUCTION PROCESS\n")

    if "constructvariables_process" in stats:
        proc = stats["constructvariables_process"]

        # Speaker Flagging Metrics
        lines.append("### Speaker Flagging Metrics\n")
        flag_metrics = proc.get("speaker_flagging_metrics", {})
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(
            f"| Total speakers flagged | {flag_metrics.get('total_speakers_flagged', 0):,} |"
        )
        lines.append(
            f"| Total speakers unflagged | {flag_metrics.get('total_speakers_unflagged', 0):,} |"
        )
        lines.append(
            f"| Flagging rate | {flag_metrics.get('flagging_rate_pct', 0):.2f}% |\n"
        )

        # Role distribution
        role_dist = flag_metrics.get("role_distribution", {})
        if role_dist:
            lines.append("**Role distribution:**\n")
            lines.append("| Role | Count | Percentage |")
            lines.append("|------|-------|------------|")
            for role, info in sorted(role_dist.items()):
                lines.append(
                    f"| {role.capitalize()} | {info['count']:,} | {info['pct']:.2f}% |"
                )
            lines.append("")

        # Variable Creation Breakdown
        lines.append("### Variable Creation Breakdown\n")
        var_breakdown = proc.get("variable_creation_breakdown", {})
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(
            f"| Total variables created | {var_breakdown.get('total_variables', 0)} |"
        )
        lines.append(f"| Number of samples | {var_breakdown.get('num_samples', 0)} |")
        lines.append(f"| Number of contexts | {var_breakdown.get('num_contexts', 0)} |")
        lines.append(
            f"| Total combinations | {var_breakdown.get('total_combinations', 0)} |"
        )
        lines.append(
            f"| Categories per combo | {var_breakdown.get('categories_per_combo', 0)} |\n"
        )

        # Efficiency Metrics
        lines.append("### Efficiency Metrics\n")
        eff = proc.get("efficiency_metrics", {})
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Calls processed | {eff.get('calls_processed', 0):,} |")
        lines.append(f"| Calls per second | {eff.get('calls_per_second', 0):.2f} |")
        lines.append(f"| Variables created | {eff.get('variables_created', 0)} |")
        lines.append(
            f"| Variables per second | {eff.get('variables_per_second', 0):.2f} |"
        )
        lines.append(f"| Years processed | {eff.get('years_processed', 0)} |\n")

    # OUTPUT SUMMARY section
    lines.append("## OUTPUT SUMMARY\n")

    if "constructvariables_output" in stats:
        outp = stats["constructvariables_output"]

        # Variable Distributions (sample of key variables)
        lines.append("### Variable Distributions (Key Variables)\n")
        lines.append(
            "*Sample of key linguistic variables with descriptive statistics*\n"
        )

        var_dist = outp.get("variable_distributions", {})
        # Select a subset of key variables to display
        key_vars = [
            k
            for k in sorted(var_dist.keys())
            if "Manager_QA" in k or "Analyst_Pres" in k
        ][:10]

        if key_vars:
            lines.append(
                "| Variable | Mean | Median | Std | Min | Max | Zeros % | NaN % |"
            )
            lines.append(
                "|----------|------|--------|-----|-----|-----|---------|--------|"
            )
            for var in key_vars:
                v = var_dist[var]
                lines.append(
                    f"| {var} | {v['mean']:.4f} | {v['median']:.4f} | {v['std']:.4f} | {v['min']:.4f} | {v['max']:.4f} | {v['zeros']['pct']:.2f}% | {v['nans']['pct']:.2f}% |"
                )
            lines.append("")

        # Sample Aggregates
        lines.append("### Sample Aggregates\n")
        sample_agg = outp.get("sample_aggregates", {})
        if sample_agg:
            lines.append("| Sample | Mean | Median | Std | Min | Max | Num Variables |")
            lines.append(
                "|--------|------|--------|-----|-----|-----|----------------|"
            )
            for sample, info in sorted(sample_agg.items()):
                if "error" not in info:
                    lines.append(
                        f"| {sample} | {info['mean']:.4f} | {info['median']:.4f} | {info['std']:.4f} | {info['min']:.4f} | {info['max']:.4f} | {info['num_variables']} |"
                    )
            lines.append("")

        # Context Aggregates
        lines.append("### Context Aggregates\n")
        ctx_agg = outp.get("context_aggregates", {})
        if ctx_agg:
            lines.append(
                "| Context | Mean | Median | Std | Min | Max | Num Variables |"
            )
            lines.append(
                "|---------|------|--------|-----|-----|-----|----------------|"
            )
            for ctx, info in sorted(ctx_agg.items()):
                if "error" not in info:
                    lines.append(
                        f"| {ctx} | {info['mean']:.4f} | {info['median']:.4f} | {info['std']:.4f} | {info['min']:.4f} | {info['max']:.4f} | {info['num_variables']} |"
                    )
            lines.append("")

        # Temporal Trends (sample)
        lines.append("### Temporal Trends (Sample)\n")
        lines.append("*Average values per year for key variables*\n")

        trends = outp.get("temporal_trends", {})
        if trends:
            # Select 3 key variables for trend display
            trend_vars = [k for k in sorted(trends.keys()) if "Manager_QA" in k][:3]

            for var in trend_vars:
                var_trends = trends[var]
                if var_trends:
                    lines.append(f"**{var}:**\n")
                    lines.append("| Year | Average |")
                    lines.append("|------|---------|")
                    for year, avg in sorted(var_trends.items()):
                        lines.append(f"| {year} | {avg:.4f} |")
                    lines.append("")

        # NaN vs Zero Analysis
        lines.append("### NaN vs Zero Analysis\n")
        nan_zero = outp.get("nan_vs_zero_analysis", {})
        if "explanation" in nan_zero:
            lines.append(f"**Methodological Note:** {nan_zero['explanation']}\n")

        lines.append("| Metric | Count | Percentage |")
        lines.append("|--------|-------|------------|")
        lines.append(f"| Total values | {nan_zero.get('total_values', 0):,} | - |")
        lines.append(
            f"| NaN (no text in section) | {nan_zero.get('nan_count', 0):,} | {nan_zero.get('nan_pct', 0):.2f}% |"
        )
        lines.append(
            f"| Zero (text, no matches) | {nan_zero.get('zero_count', 0):,} | {nan_zero.get('zero_pct', 0):.2f}% |\n"
        )

    # PROCESS SUMMARY (existing)
    lines.append("## PROCESS SUMMARY\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    if "timing" in stats:
        lines.append(
            f"| Duration (seconds) | {stats['timing'].get('duration_seconds', 0):.2f} |"
        )
    if "output" in stats:
        lines.append(f"| Final rows | {stats['output'].get('final_rows', 0):,} |")
        lines.append(f"| Final columns | {stats['output'].get('final_columns', 0)} |")
    lines.append("")

    # OUTPUT SUMMARY (existing)
    lines.append("## OUTPUT SUMMARY (Files Generated)\n")
    if "output" in stats:
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Files generated | {len(stats['output'].get('files', []))} |")
        lines.append("")

    # Write report
    report_content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Report generated: {output_path.name}")


def main(year_start: int = 2002, year_end: int = 2018):
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    print("=== Step 2.2: Construct Variables (Weighted) ===")
    root = Path(__file__).parent.parent.parent.parent
    setup_logging()

    out_base = root / "outputs" / "2_Textual_Analysis"
    out_dir = out_base / "2.2_Variables" / timestamp
    ensure_output_dir(out_dir)

    # Memory tracking at script start
    mem_start = get_process_memory_mb()
    all_memory_values = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "2.2_ConstructVariables",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "speaker_flags": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    # Resolve manifest path using timestamp-based directory resolution
    manifest_dir = get_latest_output_dir(
        root / "outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"

    # Resolve tokenized input directory using timestamp-based resolution
    tokenized_dir = get_latest_output_dir(
        root / "outputs" / "2_Textual_Analysis" / "2.1_Tokenized",
        required_file="linguistic_counts_2002.parquet",
    )

    stats["input"]["files"].append(str(manifest_path))
    stats["input"]["checksums"]["master_sample_manifest.parquet"] = (
        compute_file_checksum(manifest_path)
    )

    manifest_df = load_executive_map(root)
    stats["input"]["total_rows"] = len(manifest_df)
    stats["input"]["total_columns"] = len(manifest_df.columns)
    print_stat("Manifest rows", value=len(manifest_df))

    # Collect input statistics for variable construction
    from f1d.shared.observability import compute_constructvariables_input_stats

    stats["constructvariables_input"] = compute_constructvariables_input_stats(
        tokenized_dir, manifest_df, years_range=(year_start, year_end + 1)
    )
    print(
        f"  Input stats collected: {stats['constructvariables_input']['tokenized_files_stats']['total_rows']:,} tokenized rows"
    )

    # Process
    output_rows = 0
    output_cols = 0
    total_speaker_flags = {"analyst": 0, "manager": 0, "ceo": 0, "operator": 0}
    per_year_stats = []
    total_variables_created = 0

    for year in range(year_start, year_end + 1):
        year_output = process_year(
            year, root, manifest_df, out_dir, tokenized_dir
        )
        if year_output:
            output_rows += year_output["rows"]
            output_cols = max(output_cols, year_output["cols"])
            stats["output"]["files"].append(f"linguistic_variables_{year}.parquet")
            if "speaker_flags" in year_output:
                for k, v in year_output["speaker_flags"].items():
                    total_speaker_flags[k] += v
            if "variables_created" in year_output:
                total_variables_created += year_output["variables_created"]
            # Collect per-year stats
            per_year_stats.append(year_output)

    stats["output"]["final_rows"] = output_rows
    stats["output"]["final_columns"] = output_cols
    stats["speaker_flags"] = total_speaker_flags

    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Collect process statistics for variable construction
    from f1d.shared.observability import compute_constructvariables_process_stats

    stats["constructvariables_process"] = compute_constructvariables_process_stats(
        per_year_stats,
        total_speaker_flags,
        total_variables_created,
        stats["timing"]["duration_seconds"],
    )
    print(
        f"  Process stats: {total_variables_created} variables created, {sum(total_speaker_flags.values()):,} speakers flagged"
    )

    # Memory tracking at script end
    mem_end = get_process_memory_mb()
    all_memory_values.append(mem_end["rss_mb"])

    # Add memory stats to stats
    stats["memory"] = {
        "start_mb": round(mem_start["rss_mb"], 2),
        "end_mb": round(mem_end["rss_mb"], 2),
        "peak_mb": round(max(all_memory_values), 2),
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
    output_files = list(out_dir.glob("linguistic_variables_*.parquet"))
    for filepath in output_files:
        checksum = compute_file_checksum(filepath)
        stats["output"]["checksums"][filepath.name] = checksum

    # Add anomaly detection for numeric columns (linguistic variables)
    # Check if there are any numeric columns suitable for anomaly detection in aggregated data
    # Using first year of output for anomaly detection
    first_year_file = next(
        (f for f in output_files if f.name.endswith("_2002.parquet")), None
    )
    if first_year_file:
        validate_input_file(first_year_file, must_exist=True)
        # Load all columns (need all numeric types for anomaly detection)
        first_year_df = pd.read_parquet(first_year_file)
        numeric_cols = first_year_df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            stats["quality_anomalies"] = detect_anomalies_zscore(
                first_year_df, numeric_cols, threshold=3.0
            )

    # Collect output statistics for variable construction
    # Load all output files for analysis
    output_dfs = []
    for year in range(year_start, year_end + 1):
        year_file = out_dir / f"linguistic_variables_{year}.parquet"
        if year_file.exists():
            try:
                df_year = pd.read_parquet(year_file)
                output_dfs.append(df_year)
            except (OSError, ValueError) as e:
                # OSError: file access issues, corruption
                # ValueError: invalid parquet format, schema issues
                print(f"  Warning: Could not load {year_file}: {e}")
            except Exception as e:
                # Catch-all for unexpected errors with full context
                print(
                    f"  Warning: Unexpected error loading {year_file}: {type(e).__name__}: {e}"
                )

    if output_dfs:
        # Define samples, contexts, and categories for analysis
        samples = [
            "Manager",
            "Analyst",
            "CEO",
            "NonCEO_Manager",
            "Entire",
            "CFO",
        ]
        contexts = ["QA", "Pres", "All"]
        # Extract categories from input stats
        categories = (
            stats.get("constructvariables_input", {})
            .get("linguistic_categories", {})
            .get("category_names", [])
        )

        from f1d.shared.observability import (
            compute_constructvariables_output_stats,
        )

        stats["constructvariables_output"] = compute_constructvariables_output_stats(
            output_dfs, samples, contexts, categories
        )
        print(
            f"  Output stats: analyzed {len(output_dfs)} years, {len(samples)} samples, {len(contexts)} contexts"
        )

    # Generate report
    report_path = out_dir / "report_step_2_2.md"
    generate_variable_construction_report(stats, report_path)

    print_stats_summary(stats)
    save_stats(stats, out_dir)

    print("\n=== Complete ===")


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    check_prerequisites(root)
    main(year_start=args.year_start, year_end=args.year_end)
