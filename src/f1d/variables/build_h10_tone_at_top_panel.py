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

Author: Thesis Author
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import numpy as np

from f1d.shared.config import load_variable_config
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


def assign_industry_sample(ff12_code: pd.Series) -> pd.Series:
    conditions = [ff12_code == 11, ff12_code == 8]
    choices = ["Finance", "Utility"]
    return pd.Series(
        np.select(conditions, choices, default="Main"), index=ff12_code.index
    )


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

        panel = panel.merge(data, on="file_name", how="left")
        print(f"  After {name} merge: {len(panel):,} rows")

    if "ff12_code" in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"]).dt.year
    if "quarter" not in panel.columns and "start_date" in panel.columns:
        panel["quarter"] = pd.to_datetime(panel["start_date"]).dt.quarter

    stats["variable_stats"] = [asdict(r.stats) for r in all_results.values()]
    return panel


def build_turns_panel(
    root_path: Path, years: range, call_panel: pd.DataFrame
) -> pd.DataFrame:
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
        return pd.DataFrame()

    print("  [Turns Panel] Concatenating token data...")
    tokens = pd.concat(dfs, ignore_index=True)

    # Filter to QA only
    print("  [Turns Panel] Filtering to QA and identifying speakers...")
    qa_tokens = tokens[tokens["context"].str.lower() == "qa"].copy()

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

    # Compute Uncertainty % per turn
    qa_tokens["Turn_Uncertainty_pct"] = np.where(
        qa_tokens["total_tokens"] > 0,
        (qa_tokens["Uncertainty_count"] / qa_tokens["total_tokens"]) * 100.0,
        0.0,
    )

    # For each Non-CEO turn j, we need the mean uncertainty of CEO turns < j in the SAME call
    print("  [Turns Panel] Aggregating prior CEO turns...")
    # 1. Extract all CEO turns and sort
    ceo_turns = qa_tokens[qa_tokens["is_ceo"]][
        ["file_name", "speaker_number", "Turn_Uncertainty_pct"]
    ].copy()
    ceo_turns = ceo_turns.sort_values(["file_name", "speaker_number"])

    # Calculate expanding mean per call
    ceo_turns["CEO_Prior_QA_Unc"] = ceo_turns.groupby("file_name")[
        "Turn_Uncertainty_pct"
    ].transform(lambda x: x.expanding().mean())

    # 2. Extract Non-CEO manager turns
    mgr_turns = qa_tokens[qa_tokens["is_nonceo_mgr"]].copy()

    # For pd.merge_asof, both dataframes MUST be sorted primarily by the "on" key
    ceo_turns = ceo_turns.sort_values("speaker_number")
    mgr_turns = mgr_turns.sort_values("speaker_number")

    print("  [Turns Panel] Joining back and merging controls...")
    # 3. Merge_asof to get the LATEST CEO mean strictly prior to this turn
    turns_panel = pd.merge_asof(
        mgr_turns,
        ceo_turns[["file_name", "speaker_number", "CEO_Prior_QA_Unc"]],
        on="speaker_number",
        by="file_name",
        allow_exact_matches=False,  # Must be strictly before
        direction="backward",
    )

    # 4. Merge relevant call-level controls
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
    turns_panel = turns_panel.merge(controls, on="file_name", how="inner")

    print(f"  Turns panel built: {len(turns_panel):,} Non-CEO manager Q&A turns")
    return turns_panel


def main():
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    if args.dry_run:
        print("Dry run OK")
        return

    year_start = args.year_start or 2002
    year_end = args.year_end or 2018
    years = range(year_start, year_end + 1)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = root / "outputs" / "variables" / "tone_at_top" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    var_config = load_variable_config()
    stats = {}

    t0 = datetime.now()
    call_panel = build_call_panel(root, years, var_config, stats)
    turns_panel = build_turns_panel(root, years, call_panel)

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

    print(f"\nDone in {(datetime.now() - t0).total_seconds():.1f}s")


if __name__ == "__main__":
    main()
