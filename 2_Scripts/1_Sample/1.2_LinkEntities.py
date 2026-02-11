#!/usr/bin/env python3
"""
==============================================================================
STEP 1.2: Entity Resolution (CCM Linking) - OPTIMIZED WITH DEDUP-INDEX
==============================================================================
ID: 1.2_LinkEntities
Description: Links cleaned metadata to CCM database using 4-tier strategy:
             Tier 1 (PERMNO+Date), Tier 2 (CUSIP8+Date), Tier 3 (Fuzzy Name).

             OPTIMIZATION: Deduplicates by company_id before matching,
             then broadcasts results to all related records.
             ~11k unique companies instead of 297k individual calls.

Inputs:
    - 4_Outputs/1.1_CleanMetadata/latest/metadata_cleaned.parquet
    - 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet
    - 1_Inputs/Siccodes12.zip
    - 1_Inputs/Siccodes48.zip
    - config/project.yaml

Outputs:
    - 4_Outputs/1.2_LinkEntities/{timestamp}/metadata_linked.parquet
    - 4_Outputs/1.2_LinkEntities/{timestamp}/variable_reference.csv
    - 4_Outputs/1.2_LinkEntities/{timestamp}/report_step_1_2.md
    - 3_Logs/1.2_LinkEntities/{timestamp}.log

Deterministic: true
==============================================================================
"""

import argparse
import importlib.util
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Add parent directory to sys.path for shared module imports (works when running directly)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Dynamic import for 1.5_Utils.py to comply with naming convention
try:
    utils_path = Path(__file__).parent / "1.5_Utils.py"
    spec = importlib.util.spec_from_file_location("utils", utils_path)
    utils = importlib.util.module_from_spec(spec)
    sys.modules["utils"] = utils
    spec.loader.exec_module(utils)
    from utils import generate_variable_reference
except ImportError as e:
    print(f"Criticial Error importing utils: {e}")
    sys.exit(1)
import re

# Import string matching utilities from shared module
# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from shared.chunked_reader import track_memory_usage
from shared.industry_utils import parse_ff_industries
from shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    calculate_throughput,
    collect_before_after_samples,
    collect_fuzzy_match_samples,
    collect_tier_match_samples,
    collect_unmatched_samples,
    compute_file_checksum,
    compute_linking_input_stats,
    compute_linking_output_stats,
    compute_linking_process_stats,
    detect_anomalies_zscore,
    get_process_memory_mb,
    print_stats_summary,
    save_stats,
)
from shared.string_matching import (
    RAPIDFUZZ_AVAILABLE,
    load_matching_config,
    match_company_names,
)

# Import shared path validation utilities
try:
    from shared.path_utils import (
        ensure_output_dir,
        get_latest_output_dir,
        validate_input_file,
        validate_output_path,
    )
except ImportError:
    import sys as _sys

    _script_dir = Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.path_utils import (
        ensure_output_dir,
        get_latest_output_dir,
        validate_input_file,
    )

# Using shared.string_matching.match_company_names() instead of direct RapidFuzz imports


# ==============================================================================
# Dual-write logging utility
# Helper function for dual writing
def print_dual(msg):
    """Print message both to stdout and via DualWriter if available."""
    print(msg, flush=True)


# ==============================================================================
# CLI argument parsing and prerequisite validation
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 1.2_LinkEntities.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 1.2: Link Entities

Links cleaned metadata to CRSP/Compustat CCM data using CUSIP,
ticker, and fuzzy name matching. Identifies firms and tracks
company names over time.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from shared.dependency_checker import validate_prerequisites

    required_files = {
        "CRSPCompustat_CCM/": root / "1_Inputs" / "CRSPCompustat_CCM",
    }

    required_steps = {
        "1.1_CleanMetadata": "metadata_cleaned.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================
# Configuration and setup
# ==============================================================================


def load_config():
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config):
    root = Path(__file__).parent.parent.parent

    # Resolve input from prior step using timestamp-based resolution
    metadata_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.1_CleanMetadata",
        required_file="metadata_cleaned.parquet",
    )

    paths = {
        "root": root,
        "metadata": metadata_dir / "metadata_cleaned.parquet",
        "ccm": root / "1_Inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
        "ccm_varref": root
        / "1_Inputs"
        / "CRSPCompustat_CCM"
        / "CRSP_CCM_Variable_Reference.txt",
        "ff12": root / "1_Inputs" / "Siccodes12.zip",
        "ff48": root / "1_Inputs" / "Siccodes48.zip",
    }

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.2_LinkEntities"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    log_base = root / config["paths"]["logs"] / "1.2_LinkEntities"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths, timestamp


# ==============================================================================
# Utility functions
# ==============================================================================


def normalize_company_name(name):
    """Normalize company name for fuzzy matching"""
    if pd.isna(name):
        return ""

    name = str(name).upper().strip()
    name = re.sub(r"[^\w\s]", " ", name)

    suffixes = [
        "INC",
        "CORP",
        "LTD",
        "LLC",
        "CO",
        "COMPANY",
        "CORPORATION",
        "INCORPORATED",
        "LIMITED",
        "PLC",
        "SA",
        "NV",
    ]
    for suffix in suffixes:
        name = re.sub(rf"\b{suffix}\b", "", name)

    name = " ".join(name.split())
    return name


# Generate_variable_reference and update_latest_symlink imported from step1_utils

# ==============================================================================
# Memory-tracked operations
# ==============================================================================


@track_memory_usage("load_entities")
def load_entities_with_tracking(metadata_path, ccm_path):
    """Load metadata and CCM entities with memory tracking"""
    # Load metadata with column pruning
    validate_input_file(metadata_path, must_exist=True)
    df = pd.read_parquet(
        metadata_path,
        columns=[
            "company_id",
            "permno",
            "cusip",
            "company_name",
            "company_ticker",
            "start_date",
            "file_name",
        ],
    )

    # Load CCM with column pruning
    validate_input_file(ccm_path, must_exist=True)
    ccm = pd.read_parquet(
        ccm_path,
        columns=[
            "LPERMNO",
            "gvkey",
            "conm",
            "sic",
            "LINKPRIM",
            "LINKTYPE",
            "LINKDT",
            "LINKENDDT",
            "cusip",
        ],
    )
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"])
    ccm["LINKENDDT_clean"] = ccm["LINKENDDT"].replace("E", "2099-12-31")
    ccm["LINKENDDT_dt"] = pd.to_datetime(ccm["LINKENDDT_clean"])
    ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]

    return {"df": df, "ccm": ccm}


@track_memory_usage("entity_linking")
def entity_linking_with_tracking(df, ccm, paths):
    """Perform entity linking (dedup + matching + merge) with memory tracking"""
    # This function wraps the main linking logic
    # Return the linked result

    # Import linking functions here to avoid circular imports
    # The actual linking logic remains in main for now
    # This wrapper is for tracking the entire linking operation

    # Dedup-index optimization would go here
    # Entity matching would go here
    # Merging would go here

    # Return placeholder - actual implementation in main
    return {"result": "placeholder"}


@track_memory_usage("save_output")
def save_output_with_tracking(df, output_path):
    """Save output with memory tracking"""
    df.to_parquet(output_path, index=False)
    return {"path": str(output_path)}


# ==============================================================================
# Main processing with DEDUP-INDEX optimization
# ==============================================================================


def main():
    config = load_config()
    paths, timestamp = setup_paths(config)

    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print_dual("=" * 80)
    print_dual("STEP 1.2: Entity Resolution (CCM Linking) - DEDUP-INDEX OPTIMIZED")
    print_dual("=" * 80)
    print_dual(f"Timestamp: {timestamp}\n")

    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()

    # Memory tracking at script start
    mem_start = get_process_memory_mb()

    # Initialize stats
    stats = {
        "step_id": "1.2_LinkEntities",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "linking": {},
        "memory_mb": {},  # Added for operation-level memory tracking
    }

    # Load entities with memory tracking
    print_dual("Loading cleaned metadata and CCM database...")
    load_result = load_entities_with_tracking(paths["metadata"], paths["ccm"])
    df = load_result["result"]["df"]
    ccm = load_result["result"]["ccm"]
    stats["memory_mb"]["load_entities"] = load_result["memory_mb"]

    total_calls = len(df)
    print_dual(f"  Loaded {total_calls:,} calls")
    print_dual(f"  Loaded {len(ccm):,} CCM link records\n")

    stats["input"]["files"].append("metadata_cleaned.parquet")
    stats["input"]["checksums"]["metadata_cleaned.parquet"] = compute_file_checksum(
        paths["metadata"]
    )
    stats["input"]["total_rows"] = len(df)
    stats["input"]["total_columns"] = len(df.columns)

    stats["input"]["files"].append("CRSPCompustat_CCM.parquet")
    stats["input"]["checksums"]["CRSPCompustat_CCM.parquet"] = compute_file_checksum(
        paths["ccm"]
    )
    stats["linking"]["ccm_records"] = len(ccm)

    # Compute entity linking input statistics
    stats["linking_input"] = compute_linking_input_stats(df, ccm)

    # ==========================================================================
    # DEDUP-INDEX OPTIMIZATION
    # ==========================================================================
    print_dual("Building dedup-index...")

    # Build index: company_id -> list of file_names
    dedup_index = df.groupby("company_id")["file_name"].apply(list).to_dict()
    unique_company_ids = list(dedup_index.keys())

    print_dual(
        f"  Unique companies: {len(unique_company_ids):,} (from {total_calls:,} calls)"
    )
    print_dual(f"  Compression ratio: {total_calls / len(unique_company_ids):.1f}x\n")

    stats["linking"]["unique_companies"] = len(unique_company_ids)
    stats["linking"]["compression_ratio"] = round(
        total_calls / len(unique_company_ids), 1
    )

    # Create unique records (one per company_id)
    unique_df = df.drop_duplicates("company_id")[
        [
            "company_id",
            "permno",
            "cusip",
            "company_name",
            "company_ticker",
            "start_date",
        ]
    ].copy()
    unique_df = unique_df.reset_index(drop=True)

    # Initialize linking columns on unique_df
    unique_df["gvkey"] = np.nan
    unique_df["conm"] = np.nan
    unique_df["sic"] = np.nan
    unique_df["link_method"] = np.nan
    unique_df["link_quality"] = np.nan
    unique_df["fuzzy_score"] = np.nan

    # Convert to object type
    for col in ["gvkey", "conm", "sic", "link_method"]:
        unique_df[col] = unique_df[col].astype("object")

    unique_df["start_date"] = pd.to_datetime(unique_df["start_date"])

    print_dual("Executing 4-tier linking strategy on UNIQUE companies:")

    # ==========================================================================
    # TIER 1: PERMNO + Date Range
    # ==========================================================================
    print_dual("\n  Tier 1: PERMNO + Date Range...")

    unmatched_mask = unique_df["gvkey"].isna()
    has_permno = unique_df["permno"].notna() & (unique_df["permno"] != "")
    tier1_candidates = unique_df[unmatched_mask & has_permno].copy()

    print_dual(
        f"    Candidates: {len(tier1_candidates):,} unmatched companies with PERMNO"
    )

    if len(tier1_candidates) > 0:
        tier1_candidates["permno_int"] = pd.to_numeric(
            tier1_candidates["permno"], errors="coerce"
        ).astype("Int64")
        tier1_candidates = tier1_candidates[tier1_candidates["permno_int"].notna()]

        merged = tier1_candidates[["company_id", "permno_int", "start_date"]].merge(
            ccm[
                [
                    "LPERMNO",
                    "gvkey",
                    "conm",
                    "sic",
                    "LINKPRIM",
                    "LINKTYPE",
                    "LINKDT",
                    "LINKENDDT_dt",
                ]
            ],
            left_on="permno_int",
            right_on="LPERMNO",
            how="inner",
        )

        merged = merged[
            (merged["start_date"] >= merged["LINKDT"])
            & (merged["start_date"] <= merged["LINKENDDT_dt"])
        ]

        linkprim_priority = {"P": 1, "C": 2, "J": 3, "N": 4}
        linktype_priority = {"LC": 1, "LU": 2}
        merged["linkprim_rank"] = merged["LINKPRIM"].map(linkprim_priority).fillna(99)
        merged["linktype_rank"] = merged["LINKTYPE"].map(linktype_priority).fillna(99)
        merged = merged.sort_values(["company_id", "linkprim_rank", "linktype_rank"])
        merged = merged.drop_duplicates(subset=["company_id"], keep="first")

        print_dual(f"    Matched: {len(merged):,} companies")

        if len(merged) > 0:
            update_df = merged[["company_id", "gvkey", "conm", "sic"]].copy()
            update_df["link_method"] = "permno_date"
            update_df["link_quality"] = 100

            unique_df = unique_df.set_index("company_id")
            update_df = update_df.set_index("company_id")

            unique_df.loc[update_df.index, "gvkey"] = update_df["gvkey"]
            unique_df.loc[update_df.index, "conm"] = update_df["conm"]
            unique_df.loc[update_df.index, "sic"] = update_df["sic"]
            unique_df.loc[update_df.index, "link_method"] = update_df["link_method"]
            unique_df.loc[update_df.index, "link_quality"] = update_df["link_quality"]

            unique_df = unique_df.reset_index()

    tier1_matched = unique_df["gvkey"].notna().sum()
    print_dual(f"    [CHECK] Total matched after Tier 1: {tier1_matched:,}")

    stats["linking"]["tier1_matched"] = int(tier1_matched)

    # ==========================================================================
    # TIER 2: CUSIP8 + Date Range
    # ==========================================================================
    print_dual("\n  Tier 2: CUSIP8 + Date Range...")

    unmatched_mask = unique_df["gvkey"].isna()
    has_cusip = unique_df["cusip"].notna() & (unique_df["cusip"] != "")
    tier2_candidates = unique_df[unmatched_mask & has_cusip].copy()

    print_dual(
        f"    Candidates: {len(tier2_candidates):,} unmatched companies with CUSIP"
    )

    if len(tier2_candidates) > 0:
        tier2_candidates["cusip8"] = tier2_candidates["cusip"].astype(str).str[:8]

        merged = tier2_candidates[["company_id", "cusip8", "start_date"]].merge(
            ccm[["cusip8", "gvkey", "conm", "sic", "LINKDT", "LINKENDDT_dt"]],
            on="cusip8",
            how="inner",
        )

        merged = merged[
            (merged["start_date"] >= merged["LINKDT"])
            & (merged["start_date"] <= merged["LINKENDDT_dt"])
        ]
        merged = merged.drop_duplicates(subset=["company_id"], keep="first")

        print_dual(f"    Matched: {len(merged):,} companies")

        if len(merged) > 0:
            update_df = merged[["company_id", "gvkey", "conm", "sic"]].copy()
            update_df["link_method"] = "cusip8_date"
            update_df["link_quality"] = 90

            unique_df = unique_df.set_index("company_id")
            update_df = update_df.set_index("company_id")

            unique_df.loc[update_df.index, "gvkey"] = update_df["gvkey"]
            unique_df.loc[update_df.index, "conm"] = update_df["conm"]
            unique_df.loc[update_df.index, "sic"] = update_df["sic"]
            unique_df.loc[update_df.index, "link_method"] = update_df["link_method"]
            unique_df.loc[update_df.index, "link_quality"] = update_df["link_quality"]

            unique_df = unique_df.reset_index()

    tier2_matched = unique_df["gvkey"].notna().sum()
    print_dual(f"    [CHECK] Total matched after Tier 2: {tier2_matched:,}")

    stats["linking"]["tier2_matched"] = int(tier2_matched)

    # ==========================================================================
    # TIER 3: Fuzzy Name Match
    # ==========================================================================
    # Load fuzzy matching threshold from config
    matching_config = load_matching_config()
    fuzzy_threshold = matching_config.get("company_name", {}).get(
        "default_threshold", 92.0
    )
    scorer_name = matching_config.get("company_name", {}).get(
        "scorer", "token_sort_ratio"
    )

    print_dual(
        f"\n  Tier 3: Fuzzy Name Match (threshold={fuzzy_threshold:.0f}, scorer={scorer_name})..."
    )

    if not RAPIDFUZZ_AVAILABLE:
        print_dual("    WARNING: rapidfuzz not available, skipping")
    else:
        unmatched_mask = unique_df["gvkey"].isna()
        has_name = unique_df["company_name"].notna()
        tier3_candidates = unique_df[unmatched_mask & has_name].copy()

        print_dual(
            f"    Candidates: {len(tier3_candidates):,} unmatched companies with name"
        )

        if len(tier3_candidates) > 0:
            tier3_candidates["company_name_norm"] = tier3_candidates[
                "company_name"
            ].apply(normalize_company_name)
            tier3_candidates = tier3_candidates[
                tier3_candidates["company_name_norm"] != ""
            ]

            ccm_names = ccm[["conm", "gvkey", "sic"]].copy()
            ccm_names["conm_norm"] = ccm_names["conm"].apply(normalize_company_name)
            ccm_names = ccm_names[ccm_names["conm_norm"] != ""].drop_duplicates(
                "conm_norm"
            )

            choices = {
                row["conm_norm"]: {
                    "gvkey": row["gvkey"],
                    "conm": row["conm"],
                    "sic": row["sic"],
                }
                for _, row in ccm_names.iterrows()
            }
            choice_list = list(choices.keys())

            print_dual(
                f"    Matching {len(tier3_candidates):,} names against {len(ccm_names):,} CCM names..."
            )

            matched_records = []
            total = len(tier3_candidates)
            progress_interval = max(500, total // 20)

            for i, (_idx, row) in enumerate(tier3_candidates.iterrows(), 1):
                query_name = row["company_name_norm"]

                # Use shared string matching function
                best_match, best_score = match_company_names(
                    query=query_name,
                    candidates=choice_list,
                    threshold=fuzzy_threshold,
                    scorer_name=scorer_name,
                    preprocess=True,
                )

                if (
                    best_score > 0
                ):  # Match found (returns 0.0 if no match above threshold)
                    ccm_data = choices[best_match]
                    matched_records.append(
                        {
                            "company_id": row["company_id"],
                            "gvkey": ccm_data["gvkey"],
                            "conm": ccm_data["conm"],
                            "sic": ccm_data["sic"],
                            "fuzzy_score": float(best_score),
                        }
                    )

                if i % progress_interval == 0 or i == total:
                    print_dual(
                        f"      Progress: {i:,}/{total:,} ({i / total * 100:.1f}%) - Matched: {len(matched_records):,}"
                    )

            print_dual(f"    Matched: {len(matched_records):,} companies")

            if len(matched_records) > 0:
                update_df = pd.DataFrame(matched_records)
                update_df["link_method"] = "name_fuzzy"
                update_df["link_quality"] = 80

                unique_df = unique_df.set_index("company_id")
                update_df = update_df.set_index("company_id")

                unique_df.loc[update_df.index, "gvkey"] = update_df["gvkey"]
                unique_df.loc[update_df.index, "conm"] = update_df["conm"]
                unique_df.loc[update_df.index, "sic"] = update_df["sic"]
                unique_df.loc[update_df.index, "link_method"] = update_df["link_method"]
                unique_df.loc[update_df.index, "link_quality"] = update_df[
                    "link_quality"
                ]

                # Store fuzzy scores for sample collection
                unique_df.loc[update_df.index, "fuzzy_score"] = update_df["fuzzy_score"]

                unique_df = unique_df.reset_index()

    tier3_matched = unique_df["gvkey"].notna().sum()
    print_dual(f"    [CHECK] Total matched after Tier 3: {tier3_matched:,}")

    stats["linking"]["tier3_matched"] = int(tier3_matched)

    # Compute entity linking process statistics
    stats["linking_process"] = compute_linking_process_stats(unique_df, stats)

    # Collect fuzzy match and tier match samples
    print_dual("\nCollecting matching samples for quality review...")
    fuzzy_samples = collect_fuzzy_match_samples(unique_df, n_samples=5)
    tier_samples = collect_tier_match_samples(unique_df, n_samples=3)

    # Store samples in linking_process stats
    stats["linking_process"]["samples"] = {
        "fuzzy_matches": fuzzy_samples,
        "tier_matches": tier_samples,
    }
    print_dual(
        f"  Collected {len(fuzzy_samples.get('high_score', []))} high-score fuzzy matches"
    )
    print_dual(
        f"  Collected {len(fuzzy_samples.get('borderline', []))} borderline fuzzy matches"
    )
    print_dual(f"  Collected {len(tier_samples.get('tier1', []))} Tier 1 examples")
    print_dual(f"  Collected {len(tier_samples.get('tier2', []))} Tier 2 examples")

    # ==========================================================================
    # BROADCAST RESULTS back to full dataset
    # ==========================================================================
    print_dual("\n" + "=" * 60)
    print_dual("Broadcasting results to all calls...")

    # Create lookup from company_id to CCM data
    matched_companies = unique_df[unique_df["gvkey"].notna()][
        ["company_id", "gvkey", "conm", "sic", "link_method", "link_quality"]
    ].copy()

    print_dual(f"  Matched companies: {len(matched_companies):,}")
    print_dual(
        f"  Total calls to update: {sum(len(dedup_index[cid]) for cid in matched_companies['company_id']):,}"
    )

    # Initialize columns in original df
    df["gvkey"] = np.nan
    df["conm"] = np.nan
    df["sic"] = np.nan
    df["link_method"] = np.nan
    df["link_quality"] = np.nan

    for col in ["gvkey", "conm", "sic", "link_method"]:
        df[col] = df[col].astype("object")

    # Broadcast via merge (most efficient)
    df = df.merge(matched_companies, on="company_id", how="left", suffixes=("_old", ""))

    # Clean up old columns if they exist
    for col in ["gvkey", "conm", "sic", "link_method", "link_quality"]:
        if f"{col}_old" in df.columns:
            df = df.drop(columns=[f"{col}_old"])

    total_matched_calls = df["gvkey"].notna().sum()
    print_dual(
        f"  Total calls with GVKEY: {total_matched_calls:,} ({total_matched_calls / total_calls * 100:.1f}%)"
    )

    stats["linking"]["total_matched_companies"] = len(matched_companies)
    stats["linking"]["total_matched_calls"] = int(total_matched_calls)

    # Collect unmatched samples
    print_dual("\nCollecting unmatched company samples...")
    unmatched_samples = collect_unmatched_samples(
        df_original=df, unique_df=unique_df, n_samples=5
    )
    stats["linking_process"]["samples"]["unmatched"] = unmatched_samples
    print_dual(f"  Collected {len(unmatched_samples)} unmatched company samples")

    # ==========================================================================
    # Filter unmatched and add FF industries
    # ==========================================================================
    print_dual("\nFiltering calls without GVKEY...")
    df_linked = df[df["gvkey"].notna()].copy()
    removed = len(df) - len(df_linked)
    print_dual(f"  Removed {removed:,} unmatched calls")
    print_dual(f"  Final count: {len(df_linked):,} calls")

    # Parse FF industries
    print_dual("\nMapping SIC codes to FF industries...")
    validate_input_file(paths["ff12"], must_exist=True)
    validate_input_file(paths["ff48"], must_exist=True)
    ff12_map = parse_ff_industries(paths["ff12"], 12)
    ff48_map = parse_ff_industries(paths["ff48"], 48)

    df_linked["sic_int"] = pd.to_numeric(df_linked["sic"], errors="coerce").astype(
        "Int64"
    )

    df_linked["ff12_code"] = df_linked["sic_int"].map(
        lambda x: ff12_map.get(x, (None, None))[0] if pd.notna(x) else None
    )
    df_linked["ff12_name"] = df_linked["sic_int"].map(
        lambda x: ff12_map.get(x, (None, None))[1] if pd.notna(x) else None
    )
    df_linked["ff48_code"] = df_linked["sic_int"].map(
        lambda x: ff48_map.get(x, (None, None))[0] if pd.notna(x) else None
    )
    df_linked["ff48_name"] = df_linked["sic_int"].map(
        lambda x: ff48_map.get(x, (None, None))[1] if pd.notna(x) else None
    )

    ff12_matched = df_linked["ff12_code"].notna().sum()
    ff48_matched = df_linked["ff48_code"].notna().sum()
    print_dual(
        f"  FF12 matched: {ff12_matched:,} ({ff12_matched / len(df_linked) * 100:.1f}%)"
    )
    print_dual(
        f"  FF48 matched: {ff48_matched:,} ({ff48_matched / len(df_linked) * 100:.1f}%)"
    )

    stats["processing"]["unmatched_calls_removed"] = int(removed)
    stats["linking"]["ff12_matched"] = int(ff12_matched)
    stats["linking"]["ff48_matched"] = int(ff48_matched)

    # Compute entity linking output statistics
    stats["linking_output"] = compute_linking_output_stats(df_linked)

    # Collect before/after samples
    print_dual("\nCollecting before/after linking samples...")
    before_after_samples = collect_before_after_samples(
        df_original=df, df_linked=df_linked, n_samples=3
    )
    stats["linking_output"]["samples"] = {"before_after": before_after_samples}
    print_dual(f"  Collected {len(before_after_samples)} before/after examples")

    # Save output with memory tracking
    output_file = paths["output_dir"] / "metadata_linked.parquet"
    print_dual("\nSaving linked metadata...")
    save_result = save_output_with_tracking(df_linked, output_file)
    stats["memory_mb"]["save_output"] = save_result["memory_mb"]
    print_dual(f"Saved linked metadata: {output_file}")

    stats["output"]["final_rows"] = len(df_linked)
    stats["output"]["final_columns"] = len(df_linked.columns)
    stats["output"]["files"].append("metadata_linked.parquet")

    # Analyze missing values in final output
    stats["missing_values"] = analyze_missing_values(df_linked)

    # Generate enhanced variable reference
    var_ref_file = paths["output_dir"] / "variable_reference.csv"
    generate_variable_reference(df_linked, var_ref_file, print_dual)

    # Finalize timing
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Memory tracking at script end
    mem_end = get_process_memory_mb()

    # Add memory stats to stats
    stats["memory"] = {
        "start_mb": round(mem_start["rss_mb"], 2),
        "end_mb": round(mem_end["rss_mb"], 2),
        "delta_mb": round(mem_end["rss_mb"] - mem_start["rss_mb"], 2),
    }

    # Add throughput to stats
    duration_seconds = end_time - start_time
    throughput = calculate_throughput(stats["output"]["final_rows"], duration_seconds)
    stats["throughput"] = {
        "rows_per_second": throughput,
        "total_rows": stats["output"]["final_rows"],
        "duration_seconds": round(duration_seconds, 3),
    }

    # Add output checksums
    stats["output"]["checksums"] = {}
    for filepath in [output_file, var_ref_file]:
        if filepath.exists():
            checksum = compute_file_checksum(filepath)
            stats["output"]["checksums"][filepath.name] = checksum

    # Add anomaly detection for numeric columns (link_quality, sic_int)
    # Check if there are any numeric columns suitable for anomaly detection
    numeric_cols = df_linked.select_dtypes(include=[np.number]).columns.tolist()
    # Filter to relevant numeric columns for entity linking
    anomaly_cols = [col for col in numeric_cols if col in ["link_quality", "sic_int"]]
    if anomaly_cols:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            df_linked, anomaly_cols, threshold=3.0
        )

    # Generate comprehensive entity linking report
    print_dual("\nGenerating entity linking report...")
    report_lines = [
        "# Step 1.2: Entity Resolution (CCM Linking) Report",
        "",
        f"**Generated:** {timestamp}",
        f"**Input:** metadata_cleaned.parquet ({stats['input']['total_rows']:,} rows)",
        f"**Output:** metadata_linked.parquet ({stats['output']['final_rows']:,} rows)",
        "",
        "## INPUT DATA",
        "",
        "### Source Metadata (from Step 1.1)",
        "",
        f"- **Total calls**: {stats['input']['total_rows']:,}",
    ]

    # Add input metadata stats
    if "linking_input" in stats and "input_metadata" in stats["linking_input"]:
        im = stats["linking_input"]["input_metadata"]
        report_lines.extend(
            [
                f"- **Unique companies**: {im.get('unique_companies', 0):,}",
                f"- **Columns**: {im.get('column_count', 0)}",
                f"- **Memory footprint**: {im.get('memory_mb', 0):.2f} MB",
                "",
            ]
        )

    # Add reference database stats
    if "linking_input" in stats and "reference_database" in stats["linking_input"]:
        rd = stats["linking_input"]["reference_database"]
        report_lines.extend(
            [
                "### Reference Database (CCM)",
                "",
                f"- **Total CCM records**: {rd.get('total_records', 0):,}",
                f"- **Unique GVKEYs**: {rd.get('unique_gvkey', 0):,}",
                f"- **Unique LPERMNOs**: {rd.get('unique_lpermno', 0):,}",
            ]
        )

        if "date_coverage" in rd:
            dc = rd["date_coverage"]
            report_lines.extend(
                [
                    f"- **Date coverage**: {dc.get('earliest', 'N/A')} to {dc.get('latest', 'N/A')} ({dc.get('span_days', 0):,} days)",
                ]
            )
        report_lines.append("")

    # Add identifier coverage
    if "linking_input" in stats and "coverage_metrics" in stats["linking_input"]:
        cm = stats["linking_input"]["coverage_metrics"]
        report_lines.extend(
            [
                "### Identifier Coverage",
                "",
                f"- **PERMNO**: {cm.get('permno_coverage_pct', 0):.1f}% of companies",
                f"- **CUSIP**: {cm.get('cusip_coverage_pct', 0):.1f}% of companies",
                f"- **Ticker**: {cm.get('ticker_coverage_pct', 0):.1f}% of companies",
                f"- **Company name**: {cm.get('name_coverage_pct', 0):.1f}% of companies",
                "",
            ]
        )

    # Add matching process section
    report_lines.extend(
        [
            "## MATCHING PROCESS",
            "",
            "### 4-Tier Matching Funnel",
            "",
            "| Tier | Method | Candidates | Matched | Cumulative | Match Rate |",
            "|------|--------|------------|---------|------------|------------|",
        ]
    )

    if "linking_process" in stats and "funnel_analysis" in stats["linking_process"]:
        fa = stats["linking_process"]["funnel_analysis"]
        mr = stats["linking_process"].get("match_rates", {})

        report_lines.extend(
            [
                f"| 1 | PERMNO+Date | {fa.get('tier1_candidates', 0):,} | {fa.get('tier1_matched', 0):,} | {fa.get('tier1_matched', 0):,} | {mr.get('tier1_match_pct', 0):.1f}% |",
                f"| 2 | CUSIP8+Date | {fa.get('tier2_candidates', 0):,} | {fa.get('tier2_matched', 0):,} | {fa.get('tier1_matched', 0) + fa.get('tier2_matched', 0):,} | {mr.get('tier2_match_pct', 0):.1f}% |",
                f"| 3 | Fuzzy Name | {fa.get('tier3_candidates', 0):,} | {fa.get('tier3_matched', 0):,} | {fa.get('total_matched', 0):,} | {mr.get('tier3_match_pct', 0):.1f}% |",
                "",
            ]
        )

    # Add link quality distribution
    if (
        "linking_process" in stats
        and "link_quality_distribution" in stats["linking_process"]
    ):
        lqd = stats["linking_process"]["link_quality_distribution"]
        if "error" not in lqd:
            report_lines.extend(
                [
                    "### Link Quality Distribution",
                    "",
                    f"- **Quality 100 (PERMNO)**: {lqd.get('quality_100_count', 0):,} companies ({lqd.get('quality_100_pct', 0):.1f}%)",
                    f"- **Quality 90 (CUSIP8)**: {lqd.get('quality_90_count', 0):,} companies ({lqd.get('quality_90_pct', 0):.1f}%)",
                    f"- **Quality 80 (Fuzzy)**: {lqd.get('quality_80_count', 0):,} companies ({lqd.get('quality_80_pct', 0):.1f}%)",
                    "",
                ]
            )

    # Add dedup-index optimization
    if "linking" in stats:
        report_lines.extend(
            [
                "### Dedup-Index Optimization",
                "",
                f"- **Compression ratio**: {stats['linking'].get('compression_ratio', 0):.1f}x",
                f"  ({stats['input']['total_rows']:,} calls -> {stats['linking'].get('unique_companies', 0):,} unique companies)",
                "",
            ]
        )

    # Add matching samples section
    if "linking_process" in stats and "samples" in stats["linking_process"]:
        samples = stats["linking_process"]["samples"]

        report_lines.extend(
            [
                "## MATCHING SAMPLES",
                "",
                "### Fuzzy Name Match Examples",
                "",
            ]
        )

        # High-score fuzzy matches
        if "fuzzy_matches" in samples and "high_score" in samples["fuzzy_matches"]:
            high_scores = samples["fuzzy_matches"]["high_score"]
            if len(high_scores) > 0:
                report_lines.extend(
                    [
                        "**High-Score Matches (>98)**",
                        "",
                        "| Query Name | Matched Name | Score | GVKEY | SIC |",
                        "|------------|--------------|-------|-------|-----|",
                    ]
                )
                for sample in high_scores:
                    report_lines.append(
                        f"| {sample.get('company_name', 'N/A')[:30]} | {sample.get('matched_name', 'N/A')[:30]} | {sample.get('score', 0):.1f} | {sample.get('gvkey', 'N/A')} | {sample.get('sic', 'N/A')} |"
                    )
                report_lines.append("")
            else:
                report_lines.extend(["No high-score fuzzy matches available.", ""])

        # Borderline fuzzy matches
        if "fuzzy_matches" in samples and "borderline" in samples["fuzzy_matches"]:
            borderline = samples["fuzzy_matches"]["borderline"]
            if len(borderline) > 0:
                report_lines.extend(
                    [
                        "**Borderline Matches (92-95)**",
                        "",
                        "| Query Name | Matched Name | Score | GVKEY | SIC |",
                        "|------------|--------------|-------|-------|-----|",
                    ]
                )
                for sample in borderline:
                    report_lines.append(
                        f"| {sample.get('company_name', 'N/A')[:30]} | {sample.get('matched_name', 'N/A')[:30]} | {sample.get('score', 0):.1f} | {sample.get('gvkey', 'N/A')} | {sample.get('sic', 'N/A')} |"
                    )
                report_lines.append("")
            else:
                report_lines.extend(["No borderline fuzzy matches available.", ""])

        # Tier 1 (PERMNO) examples
        if "tier_matches" in samples and "tier1" in samples["tier_matches"]:
            tier1 = samples["tier_matches"]["tier1"]
            if len(tier1) > 0:
                report_lines.extend(
                    [
                        "### Tier 1 (PERMNO) Match Examples",
                        "",
                        "| Company | PERMNO | GVKEY | Matched Name | SIC |",
                        "|---------|--------|-------|--------------|-----|",
                    ]
                )
                for sample in tier1:
                    report_lines.append(
                        f"| {sample.get('company_id', 'N/A')[:20]} | {sample.get('permno', 'N/A')} | {sample.get('gvkey', 'N/A')} | {sample.get('conm', 'N/A')[:30]} | {sample.get('sic', 'N/A')} |"
                    )
                report_lines.append("")
            else:
                report_lines.extend(["No Tier 1 examples available.", ""])

        # Tier 2 (CUSIP8) examples
        if "tier_matches" in samples and "tier2" in samples["tier_matches"]:
            tier2 = samples["tier_matches"]["tier2"]
            if len(tier2) > 0:
                report_lines.extend(
                    [
                        "### Tier 2 (CUSIP8) Match Examples",
                        "",
                        "| Company | CUSIP8 | GVKEY | Matched Name | SIC |",
                        "|---------|--------|-------|--------------|-----|",
                    ]
                )
                for sample in tier2:
                    report_lines.append(
                        f"| {sample.get('company_id', 'N/A')[:20]} | {sample.get('cusip8', 'N/A')} | {sample.get('gvkey', 'N/A')} | {sample.get('conm', 'N/A')[:30]} | {sample.get('sic', 'N/A')} |"
                    )
                report_lines.append("")
            else:
                report_lines.extend(["No Tier 2 examples available.", ""])

        # Unmatched samples
        if "unmatched" in samples and len(samples["unmatched"]) > 0:
            report_lines.extend(
                [
                    "### Unmatched Companies (Sample)",
                    "",
                    "| Company Name | Has PERMNO | Has CUSIP | Has Ticker | Likely Reason |",
                    "|--------------|------------|-----------|------------|---------------|",
                ]
            )
            for sample in samples["unmatched"][:10]:
                report_lines.append(
                    f"| {sample.get('company_name', 'N/A')[:30]} | {'Yes' if sample.get('has_permno', False) else 'No'} | {'Yes' if sample.get('has_cusip', False) else 'No'} | {'Yes' if sample.get('has_ticker', False) else 'No'} | {sample.get('likely_reason', 'unknown')} |"
                )
            report_lines.append("")
        else:
            report_lines.extend(["No unmatched companies.", ""])

        # Before/After examples
        if (
            "linking_output" in stats
            and "samples" in stats["linking_output"]
            and "before_after" in stats["linking_output"]["samples"]
        ):
            before_after = stats["linking_output"]["samples"]["before_after"]
            if len(before_after) > 0:
                report_lines.extend(
                    [
                        "### Before/After Examples",
                        "",
                        "Shows the transformation from original to linked fields:",
                        "",
                    ]
                )
                for i, example in enumerate(before_after, 1):
                    before = example.get("before", {})
                    after = example.get("after", {})
                    report_lines.extend(
                        [
                            f"**Example {i}:**",
                            "",
                            f"- **Company ID:** {before.get('company_id', 'N/A')}",
                            f"- **Before:** name='{before.get('company_name', 'N/A')[:40]}', ticker='{before.get('company_ticker', 'N/A')}', permno={before.get('permno', 'N/A')}, cusip={before.get('cusip', 'N/A')[:8]}",
                            f"- **After:** gvkey='{after.get('gvkey', 'N/A')}', conm='{after.get('conm', 'N/A')[:40]}', sic={after.get('sic', 'N/A')}, ff12='{after.get('ff12_name', 'N/A')[:30]}', method={after.get('link_method', 'N/A')}, quality={after.get('link_quality', 0)}",
                            "",
                        ]
                    )
            else:
                report_lines.extend(["No before/after examples available.", ""])

    # Add output summary section
    report_lines.extend(
        [
            "## OUTPUT SUMMARY",
            "",
            "### Linkage Success",
            "",
        ]
    )

    if "linking_output" in stats and "linkage_summary" in stats["linking_output"]:
        ls = stats["linking_output"]["linkage_summary"]
        report_lines.extend(
            [
                f"- **Total calls linked**: {ls.get('total_calls_linked', 0):,} ({stats['output']['final_rows']:,})",
                f"- **Unique companies linked**: {ls.get('unique_companies_linked', 0):,}",
                f"- **Unique GVKEYs assigned**: {ls.get('unique_gvkey_assigned', 0):,}",
                f"- **Company linkage rate**: {ls.get('company_linkage_rate', 0):.1f}%",
                f"- **Average calls per company**: {ls.get('calls_per_company_avg', 0):.2f}",
                "",
            ]
        )

    # Add industry coverage
    if "linking_output" in stats and "industry_coverage" in stats["linking_output"]:
        ic = stats["linking_output"]["industry_coverage"]
        if "error" not in ic:
            report_lines.extend(
                [
                    "### Industry Coverage",
                    "",
                    f"- **FF12**: {ic.get('ff12_assigned', 0):,} assigned ({ic.get('ff12_completion_pct', 0):.1f}%), {ic.get('ff12_unique_industries', 0):,} unique industries",
                    f"- **FF48**: {ic.get('ff48_assigned', 0):,} assigned ({ic.get('ff48_completion_pct', 0):.1f}%), {ic.get('ff48_unique_industries', 0):,} unique industries",
                    "",
                ]
            )

    # Add SIC distribution
    if "linking_output" in stats and "sic_distribution" in stats["linking_output"]:
        sd = stats["linking_output"]["sic_distribution"]
        if "error" not in sd:
            report_lines.extend(
                [
                    "### SIC Distribution",
                    "",
                    f"- **Unique SIC codes**: {sd.get('unique_sic_codes', 0):,}",
                    "",
                    "Top 10 SIC Industries:",
                    "",
                    "| SIC | Count | Percentage |",
                    "|-----|-------|------------|",
                ]
            )
            for industry in sd.get("top_industries", [])[:10]:
                report_lines.append(
                    f"| {industry.get('sic', 'N/A')} | {industry.get('count', 0):,} | {industry.get('percentage', 0):.2f}% |"
                )
            report_lines.append("")

    # Add quality metrics
    if "linking_output" in stats and "quality_metrics" in stats["linking_output"]:
        qm = stats["linking_output"]["quality_metrics"]
        if "error" not in qm:
            report_lines.extend(
                [
                    "### Linkage Quality Metrics",
                    "",
                    f"- **Average link quality**: {qm.get('avg_link_quality', 0):.2f}",
                ]
            )

            if "link_quality_by_method" in qm:
                report_lines.extend(
                    [
                        "",
                        "Link Quality by Method:",
                        "",
                        "| Method | Avg Quality |",
                        "|--------|-------------|",
                    ]
                )
                for method, avg_quality in qm["link_quality_by_method"].items():
                    report_lines.append(f"| {method} | {avg_quality:.2f} |")
                report_lines.append("")

    # Add temporal coverage
    if "linking_output" in stats and "temporal_coverage" in stats["linking_output"]:
        tc = stats["linking_output"]["temporal_coverage"]
        report_lines.extend(
            [
                "### Temporal Coverage",
                "",
                f"- **Date range**: {tc.get('earliest_date', 'N/A')} to {tc.get('latest_date', 'N/A')}",
                "",
            ]
        )

    # Add output files section
    report_lines.extend(
        [
            "## Output Files",
            "",
            f"- Linked metadata: `{output_file.name}`",
            f"- Variable reference: `{var_ref_file.name}`",
            "- Statistics: `stats.json`",
            "",
            "## Columns",
            "",
            f"Total columns: {stats['output']['final_columns']}",
            "",
            "```",
            ", ".join(df_linked.columns.tolist()),
            "```",
        ]
    )

    # Write report
    report_file = paths["output_dir"] / "report_step_1_2.md"
    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    print_dual(f"Report saved: {report_file}")

    # Print and save stats summary
    print_stats_summary(stats)
    save_stats(stats, paths["output_dir"])

    print_dual("\n" + "=" * 80)
    print_dual("Step 1.2 completed successfully.")
    print_dual("=" * 80)

    sys.stdout = dual_writer.terminal
    dual_writer.close()

    return 0


if __name__ == "__main__":
    # Parse arguments and check prerequisites
    args = parse_arguments()
    # Use resolve() to get absolute path before going up directories
    root = Path(__file__).resolve().parent.parent.parent

    # Handle dry-run mode
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    # Check prerequisites
    check_prerequisites(root)

    # Run main processing
    sys.exit(main())
