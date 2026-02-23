#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build Tone-at-the-Top Panel
================================================================================
ID: variables/build_h10_tone_at_top_panel
Description: Build panels for H_TT tests by loading variables and merging.
             Also builds a speaker-turn level panel for Model 2.

Inputs (all raw):
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_{year}.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet
    - inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet
    - inputs/tr_ibes/tr_ibes.parquet

Outputs:
    - outputs/variables/tone_at_top/{timestamp}/tone_at_top_panel.parquet
    - outputs/variables/tone_at_top/{timestamp}/tone_at_top_turns_panel.parquet
    - outputs/variables/tone_at_top/{timestamp}/summary_stats.csv
    - outputs/variables/tone_at_top/{timestamp}/reconciliation_table.csv

Author: Thesis Author
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import numpy as np

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.variables.panel_utils import assign_industry_sample
from f1d.shared.variables import (
    ManifestFieldsBuilder,
    NonCEOManagerQAUncertaintyBuilder,
    NonCEOManagerPresUncertaintyBuilder,
    CFOQAUncertaintyBuilder,
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    CEOStyleRealtimeBuilder,
    SizeBuilder,
    BMBuilder,
    LevBuilder,
    ROABuilder,
    StockReturnBuilder,
    MarketReturnBuilder,
    EPSGrowthBuilder,
    EarningsSurpriseBuilder,
    stats_list_to_dataframe,
)
from f1d.shared.path_utils import get_latest_output_dir


def parse_arguments():
    parser = argparse.ArgumentParser(description="Stage 3: Build Tone-at-the-Top Panel")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without executing"
    )
    parser.add_argument("--year-start", type=int, default=None)
    parser.add_argument("--year-end", type=int, default=None)
    return parser.parse_args()


def build_call_panel(
    root_path: Path, years: range, var_config: Dict[str, Any], stats: Dict[str, Any]
) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Loading Call-Level Variables")
    print("=" * 60)

    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "nonceo_manager_qa_uncertainty": NonCEOManagerQAUncertaintyBuilder(
            var_config.get("nonceo_manager_qa_uncertainty", {})
        ),
        "nonceo_manager_pres_uncertainty": NonCEOManagerPresUncertaintyBuilder(
            var_config.get("nonceo_manager_pres_uncertainty", {})
        ),
        "cfo_qa_uncertainty": CFOQAUncertaintyBuilder(
            var_config.get("cfo_qa_uncertainty", {})
        ),
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "ceo_style_realtime": CEOStyleRealtimeBuilder(
            var_config.get("ceo_style_realtime", {})
        ),
        "size": SizeBuilder({}),
        "bm": BMBuilder({}),
        "lev": LevBuilder({}),
        "roa": ROABuilder({}),
        "stock_return": StockReturnBuilder({}),
        "market_return": MarketReturnBuilder({}),
        "eps_growth": EPSGrowthBuilder({}),
        "earnings_surprise": EarningsSurpriseBuilder(
            var_config.get("earnings_surprise", {})
        ),
    }

    all_results = {}
    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    panel = all_results["manifest"].data.copy()

    for name, result in all_results.items():
        if name == "manifest":
            continue
        data = result.data.copy()
        if "file_name" not in data.columns or len(data.columns) <= 1:
            continue

        conflicting = [
            c for c in data.columns if c in panel.columns and c != "file_name"
        ]
        if conflicting:
            data = data.drop(columns=conflicting)

        before_len = len(panel)
        panel = panel.merge(data, on="file_name", how="left")
        after_len = len(panel)
        if after_len != before_len:
            raise ValueError(
                f"Merge '{name}' changed row count: {before_len} → {after_len}. "
                "Builder returned duplicate file_name rows."
            )
        print(f"  After {name} merge: {after_len:,} rows")

    if "ff12_code" in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year
    if "quarter" not in panel.columns and "start_date" in panel.columns:
        panel["quarter"] = pd.to_datetime(
            panel["start_date"], errors="coerce"
        ).dt.quarter

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]
    return panel


def build_turns_panel(
    root_path: Path, years: range, call_panel: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Build speaker-turn level panel for Model 2.

    Args:
        root_path: Project root path
        years: Range of years to process
        call_panel: Call-level panel with controls

    Returns:
        Tuple of (turns_panel, stage_counts) where:
        - turns_panel: DataFrame with manager turns and prior CEO uncertainty
        - stage_counts: Dict mapping stage names to row counts for reconciliation
    """
    print("\n" + "=" * 60)
    print("Building Speaker-Turn Panel (Model 2)")
    print("=" * 60)

    token_dir = get_latest_output_dir(
        root_path / "outputs" / "2_Textual_Analysis" / "2.1_Tokenized",
        required_file="linguistic_counts_2010.parquet",
    )

    # We only care about calls that made it to the call_panel
    valid_files = set(call_panel["file_name"])

    dfs = []
    print(f"  [Turns Panel] Loading token data for {len(years)} years...")
    for year in years:
        p = token_dir / f"linguistic_counts_{year}.parquet"
        if p.exists():
            df_y = pd.read_parquet(p)
            df_y = df_y[df_y["file_name"].isin(valid_files)].copy()
            dfs.append(df_y)

    if not dfs:
        return pd.DataFrame(), {}

    print("  [Turns Panel] Concatenating token data...")
    tokens = pd.concat(dfs, ignore_index=True)

    # =========================================================================
    # Track row counts for reconciliation table
    # =========================================================================
    stage_counts = {}

    # Filter to QA only
    print("  [Turns Panel] Filtering to QA and identifying speakers...")
    qa_tokens = tokens[tokens["context"].str.lower() == "qa"].copy()
    stage_counts["1_raw_qa_tokens"] = len(qa_tokens)

    # =========================================================================
    # Compute Turn_Uncertainty_pct EARLY (needed for deterministic dedup sort)
    # =========================================================================
    qa_tokens["Turn_Uncertainty_pct"] = np.where(
        qa_tokens["total_tokens"] > 0,
        (qa_tokens["Uncertainty_count"] / qa_tokens["total_tokens"]) * 100.0,
        0.0,
    )

    # =========================================================================
    # CRITICAL: Deterministic Deduplication (P0 BLOCKER)
    # =========================================================================
    # Raw token data may contain duplicate (file_name, speaker_number) pairs.
    # Must sort deterministically before dedup to ensure reproducibility.
    qa_tokens = qa_tokens.sort_values(
        ["file_name", "speaker_number", "Turn_Uncertainty_pct"],
        kind="stable"
    ).reset_index(drop=True)

    # DIAGNOSTIC: Check for divergent values in duplicates BEFORE dropping
    dup_mask = qa_tokens.duplicated(subset=["file_name", "speaker_number"], keep=False)
    if dup_mask.any():
        dup_groups = qa_tokens[dup_mask].groupby(["file_name", "speaker_number"])
        unc_variance = dup_groups["Turn_Uncertainty_pct"].var()
        divergent = unc_variance[unc_variance > 1e-6]
        if len(divergent) > 0:
            print(f"  [WARNING] {len(divergent)} duplicate groups have divergent uncertainty values")
            print(f"  Sample (file_name, speaker_number -> variance):")
            for (fn, sn), var in divergent.head(5).items():
                print(f"    {fn}, {sn}: {var:.4f}")

    # DEDUPLICATE: Keep first occurrence after deterministic sort
    before_dedup = len(qa_tokens)
    qa_tokens = qa_tokens.drop_duplicates(
        subset=["file_name", "speaker_number"],
        keep="first"
    ).copy()
    after_dedup = len(qa_tokens)
    stage_counts["2_post_dedup"] = after_dedup
    print(f"  [QA Tokens] Deduplicated: {before_dedup:,} -> {after_dedup:,} rows")
    if before_dedup != after_dedup:
        print(f"  [QA Tokens] Removed {before_dedup - after_dedup:,} duplicate turn pairs")

    # Identify CEO turns
    # In 2.2_Variables, CEO is flagged by role matching "CEO" etc., but we know the speaker_name matching the manifest ceo_name is the most reliable way.
    # However, for simplicity let's use the role column which has "CEO"
    qa_tokens["is_ceo"] = qa_tokens["role"].str.contains(
        r"\bCEO\b|Chief Executive", case=False, na=False
    )

    # Identify Non-CEO manager turns (manager but not CEO)
    # Using the 45 keywords for manager
    mgr_pattern = r"PRESIDENT|VP|DIRECTOR|CEO|EVP|SVP|CFO|OFFICER|CHIEF|EXECUTIVE|HEAD|CHAIRMAN|SENIOR|MANAGER|COO|TREASURER|SECRETARY|MD|DEPUTY|CONTROLLER|GM|PRINCIPAL|CAO|CIO|CTO|CMO|LEADER|LEAD|CCO|COORDINATOR|AVP|ADMINISTRATOR|CHAIRWOMAN|CHAIRPERSON|SUPERINTENDENT|DEAN|COMMISSIONER|CA|GOVERNOR|SUPERVISOR|COACH|PROVOST|CAPTAIN|CHO|RECTOR"
    qa_tokens["is_manager"] = qa_tokens["role"].str.contains(
        mgr_pattern, case=False, na=False
    )
    qa_tokens["is_nonceo_mgr"] = qa_tokens["is_manager"] & ~qa_tokens["is_ceo"]

    # =========================================================================
    # NEW: Identify analyst turns (for preceding analyst uncertainty control)
    # =========================================================================
    analyst_pattern = r"\bAnalyst\b"
    qa_tokens["is_analyst"] = qa_tokens["role"].str.contains(
        analyst_pattern, case=False, na=False
    )

    # =========================================================================
    # NEW: Analyst turn uncertainty - compute on full qa_tokens BEFORE filtering
    # =========================================================================
    # For each turn, get the PRECEDING turn's analyst uncertainty
    qa_tokens["Analyst_Turn_Unc_pct"] = qa_tokens["Turn_Uncertainty_pct"]  # Already computed
    # shift(1) gives the immediately preceding turn's analyst uncertainty
    qa_tokens["Preceding_Analyst_Unc"] = qa_tokens.groupby("file_name")["Analyst_Turn_Unc_pct"].shift(1)
    # Also flag if preceding turn was actually an analyst
    qa_tokens["Preceding_Is_Analyst"] = qa_tokens.groupby("file_name")["is_analyst"].shift(1)

    # =========================================================================
    # NEW: Manager type classification (CFO, Top Exec, Other)
    # =========================================================================
    cfo_pattern = r"\bCFO\b|Chief\s+Financial|Financial\s+Officer|Principal\s+Financial"
    top_exec_pattern = r"\bCOO\b|President|Chief Operating"

    qa_tokens["is_cfo"] = qa_tokens["role"].str.contains(cfo_pattern, case=False, na=False)
    qa_tokens["is_top_exec"] = qa_tokens["role"].str.contains(top_exec_pattern, case=False, na=False)
    qa_tokens["is_other_mgr"] = qa_tokens["is_nonceo_mgr"] & ~qa_tokens["is_cfo"] & ~qa_tokens["is_top_exec"]

    # =========================================================================
    # For each Non-CEO turn j, we need the mean uncertainty of CEO turns < j in the SAME call
    # =========================================================================
    print("  [Turns Panel] Aggregating prior CEO turns...")
    # 1. Extract all CEO turns and sort
    ceo_turns = qa_tokens[qa_tokens["is_ceo"]][
        ["file_name", "speaker_number", "Turn_Uncertainty_pct"]
    ].copy()
    ceo_turns = ceo_turns.sort_values(["file_name", "speaker_number"])

    # =========================================================================
    # Calculate expanding mean per call (baseline)
    # =========================================================================
    ceo_turns["CEO_Prior_QA_Unc"] = ceo_turns.groupby("file_name")[
        "Turn_Uncertainty_pct"
    ].transform(lambda x: x.expanding().mean())

    # =========================================================================
    # NEW: Local lag specifications (compute BEFORE merge, add to single merge)
    # =========================================================================
    ceo_turns["CEO_Unc_Lag1"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].shift(1)
    ceo_turns["CEO_Unc_Roll2"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].transform(
        lambda x: x.shift(1).rolling(2, min_periods=1).mean()
    )
    ceo_turns["CEO_Unc_Roll3"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].transform(
        lambda x: x.shift(1).rolling(3, min_periods=1).mean()
    )
    ceo_turns["CEO_Unc_ExpDecay"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].transform(
        lambda x: x.shift(1).ewm(alpha=0.5, min_periods=1).mean()
    )
    ceo_turns["CEO_Unc_Lead1"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].shift(-1)

    # =========================================================================
    # 2. Extract Non-CEO manager turns
    # =========================================================================
    mgr_turns = qa_tokens[qa_tokens["is_nonceo_mgr"]].copy()

    # =========================================================================
    # 3. Merge CEO variables to Manager turns (VECTORIZED - no loop)
    # =========================================================================
    # Instead of slow file-by-file loop, use forward-fill propagation:
    # 1. Merge CEO values to qa_tokens (only CEO rows get values, others get NaN)
    # 2. Sort by file_name, speaker_number
    # 3. Use groupby().ffill() to propagate CEO values forward
    # 4. Filter to manager turns
    # Since CEO and manager turns are DISJOINT sets, ffill gives STRICTLY PRIOR values
    print("  [Turns Panel] Merging CEO variables to manager turns (vectorized)...")

    # CEO columns to propagate
    ceo_value_cols = [
        "CEO_Prior_QA_Unc",
        "CEO_Unc_Lag1",
        "CEO_Unc_Roll2",
        "CEO_Unc_Roll3",
        "CEO_Unc_ExpDecay",
        "CEO_Unc_Lead1",
    ]

    # =========================================================================
    # Step 1: Merge CEO values to qa_tokens with VALIDATION (P0 BLOCKER)
    # =========================================================================
    # Only CEO rows will have non-NaN values after this merge
    ceo_for_merge = ceo_turns[["file_name", "speaker_number"] + ceo_value_cols].copy()

    # CRITICAL: Verify ceo_for_merge is unique on merge keys
    ceo_dup_count = ceo_for_merge.duplicated(subset=["file_name", "speaker_number"]).sum()
    if ceo_dup_count > 0:
        raise ValueError(f"ceo_for_merge has {ceo_dup_count} duplicate merge keys! Dedup failed.")

    # Merge with validation
    pre_merge = len(qa_tokens)
    try:
        qa_tokens = qa_tokens.merge(
            ceo_for_merge,
            on=["file_name", "speaker_number"],
            how="left",
            validate="m:1"  # FATAL if fails
        )
    except pd.errors.MergeError as e:
        print(f"  [FATAL] CEO merge validation failed: {e}")
        raise
    post_merge = len(qa_tokens)
    stage_counts["3_post_ceo_merge"] = post_merge
    assert post_merge == pre_merge, f"CEO merge changed row count: {pre_merge} -> {post_merge}"
    print(f"  [CEO Merge] {pre_merge:,} -> {post_merge:,} rows (unchanged, as expected)")

    # Step 2: Sort by file and speaker_number (required for ffill)
    qa_tokens = qa_tokens.sort_values(["file_name", "speaker_number"])

    # Step 3: Forward fill CEO values within each file (single groupby for efficiency)
    # This propagates the last CEO turn's values to all subsequent turns
    qa_tokens[ceo_value_cols] = qa_tokens.groupby("file_name")[ceo_value_cols].transform(
        lambda g: g.ffill()
    )

    # Step 4: Filter to manager turns - they now have the PRIOR CEO values
    turns_panel = qa_tokens[qa_tokens["is_nonceo_mgr"]].copy()
    stage_counts["4_post_manager_filter"] = len(turns_panel)

    print(f"  [Turns Panel] Merged {len(turns_panel):,} manager turns")

    # =========================================================================
    # NEW: Create turn_index from speaker_number (for time controls) - AFTER merge
    # =========================================================================
    turns_panel = turns_panel.rename(columns={"speaker_number": "turn_index"})

    # Add polynomial terms for flexible time controls
    turns_panel["turn_index_sq"] = turns_panel["turn_index"] ** 2
    turns_panel["turn_index_cu"] = turns_panel["turn_index"] ** 3

    # Alternative: normalized turn index (0 to 1 within call)
    call_max_turns = turns_panel.groupby("file_name")["turn_index"].transform("max")
    turns_panel["turn_index_norm"] = turns_panel["turn_index"] / call_max_turns.clip(lower=1)

    # =========================================================================
    # 4. Merge relevant call-level controls with VALIDATION (P0 BLOCKER)
    # =========================================================================
    controls = call_panel[
        [
            "file_name",
            "gvkey",
            "ceo_id",
            "sample",
            "CEO_Pres_Uncertainty_pct",
            "year",
            "quarter",
        ]
    ].copy()

    # Log file_names that will be dropped by inner join
    files_in_turns = set(turns_panel["file_name"].unique())
    files_in_controls = set(controls["file_name"].unique())
    files_dropped = files_in_turns - files_in_controls
    if files_dropped:
        print(f"  [WARNING] {len(files_dropped)} file_names in turns_panel have no controls (will be dropped)")

    pre_merge = len(turns_panel)
    turns_panel = turns_panel.merge(
        controls,
        on="file_name",
        how="inner",
        validate="m:1"  # FATAL if fails
    )
    post_merge = len(turns_panel)
    stage_counts["5_post_controls_merge"] = post_merge
    assert post_merge <= pre_merge, f"Controls merge increased rows: {pre_merge} -> {post_merge}"
    if post_merge < pre_merge:
        print(f"  [Controls Merge] {pre_merge:,} -> {post_merge:,} rows ({pre_merge - post_merge:,} dropped)")

    # =========================================================================
    # NEW: Create speaker_id composite key (Addendum A)
    # Ensures each firm-specific speaker gets unique fixed effect
    # =========================================================================
    turns_panel["speaker_id"] = turns_panel["gvkey"].astype(str) + "_" + turns_panel["speaker_name"]

    # =========================================================================
    # NEW: Report M2 observation filtering (Addendum B)
    # =========================================================================
    total_mgr_turns = len(turns_panel)
    no_prior_ceo = turns_panel["CEO_Prior_QA_Unc"].isna().sum()
    print(f"  Manager turns with no prior CEO turn: {no_prior_ceo:,} ({100*no_prior_ceo/total_mgr_turns:.1f}%)")

    # Filter to valid M2 observations (must have at least one prior CEO turn)
    turns_panel = turns_panel[turns_panel["CEO_Prior_QA_Unc"].notna()].copy()
    print(f"  Valid M2 observations: {len(turns_panel):,}")

    # =========================================================================
    # FINAL VERIFICATION: Ensure each turn is uniquely identified (P0 BLOCKER)
    # =========================================================================
    key_cols = ["file_name", "turn_index", "speaker_id"]
    duplicates = turns_panel.duplicated(subset=key_cols, keep=False)
    if duplicates.any():
        n_dup = duplicates.sum()
        n_dup_groups = turns_panel[duplicates].groupby(key_cols).ngroups
        print(f"  [FATAL] {n_dup} duplicate rows in {n_dup_groups} turn key groups!")
        print(f"  Sample duplicates:")
        print(turns_panel[duplicates].head(10)[key_cols + ["role", "speaker_name"]])
        raise ValueError(f"Final turns_panel has {n_dup_groups} duplicate turn keys")

    print(f"  [Final Check] {len(turns_panel):,} rows, all unique by {key_cols}")
    print(f"  [Final Check] Unique file_names: {turns_panel['file_name'].nunique():,}")
    print(f"  [Final Check] Unique speaker_ids: {turns_panel['speaker_id'].nunique():,}")

    stage_counts["6_final"] = len(turns_panel)
    print(f"  Turns panel built: {len(turns_panel):,} Non-CEO manager Q&A turns")
    return turns_panel, stage_counts


def generate_reconciliation_table(
    stages: List[tuple],
    out_dir: Path
) -> pd.DataFrame:
    """Generate table showing row counts at each stage.

    Args:
        stages: List of (stage_name, row_count) tuples
        out_dir: Directory to save reconciliation table

    Returns:
        DataFrame with stages, row counts, and deltas
    """
    recon_df = pd.DataFrame(stages, columns=["stage", "n_rows"])
    recon_df["delta"] = recon_df["n_rows"].diff()
    recon_df.to_csv(out_dir / "reconciliation_table.csv", index=False)
    print("\n" + "=" * 60)
    print("RECONCILIATION TABLE")
    print("=" * 60)
    print(recon_df.to_string(index=False))
    return recon_df


def main():
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    year_start = args.year_start
    year_end = args.year_end
    if year_start is None or year_end is None:
        # Load year range from project.yaml — same pattern as all other panel builders
        config = get_config(root / "config" / "project.yaml")
        if year_start is None:
            year_start = config.data.year_start
        if year_end is None:
            year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    # Dry run: test with just 1 year to validate logic
    if args.dry_run:
        print("=" * 60)
        print("DRY RUN: Testing with 1 year of data")
        print("=" * 60)
        years = range(year_end, year_end + 1)  # Just the last year
        var_config = load_variable_config(root / "config" / "variables.yaml")
        stats = {}

        try:
            call_panel = build_call_panel(root, years, var_config, stats)
            print(f"  Call panel: {len(call_panel):,} rows")

            turns_panel, stage_counts = build_turns_panel(root, years, call_panel)
            print(f"  Turns panel: {len(turns_panel):,} rows")

            # Verify new columns exist
            expected_cols = [
                "turn_index", "turn_index_sq", "turn_index_norm",
                "CEO_Prior_QA_Unc", "CEO_Unc_Lag1", "CEO_Unc_Roll2",
                "CEO_Unc_Roll3", "CEO_Unc_ExpDecay", "CEO_Unc_Lead1",
                "speaker_id", "Preceding_Analyst_Unc"
            ]
            missing = [c for c in expected_cols if c not in turns_panel.columns]
            if missing:
                print(f"  WARNING: Missing columns: {missing}")
            else:
                print(f"  All expected columns present!")

            print("\n" + "=" * 60)
            print("DRY RUN SUCCESSFUL")
            print("=" * 60)
        except Exception as e:
            print(f"\nDRY RUN FAILED: {e}")
            raise
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = root / "outputs" / "variables" / "tone_at_top" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Pass explicit path so CWD doesn't matter — same pattern as all other panel builders
    var_config = load_variable_config(root / "config" / "variables.yaml")
    stats = {}

    t0 = datetime.now()
    call_panel = build_call_panel(root, years, var_config, stats)
    turns_panel, stage_counts = build_turns_panel(root, years, call_panel)

    # Save call panel
    p1 = out_dir / "tone_at_top_panel.parquet"
    call_panel.to_parquet(p1, index=False)
    print(f"  Saved {p1.name} ({len(call_panel):,} rows)")

    # Save turns panel
    p2 = out_dir / "tone_at_top_turns_panel.parquet"
    if not turns_panel.empty:
        turns_panel.to_parquet(p2, index=False)
        print(f"  Saved {p2.name} ({len(turns_panel):,} rows)")

    # Save stats
    stats_df = stats_list_to_dataframe(stats.get("variable_stats", []))
    stats_df.to_csv(out_dir / "summary_stats.csv", index=False)

    # Generate reconciliation table
    if stage_counts:
        stages = [(k, v) for k, v in stage_counts.items()]
        generate_reconciliation_table(stages, out_dir)

    print(f"\nDone in {(datetime.now() - t0).total_seconds():.1f}s")


if __name__ == "__main__":
    main()
