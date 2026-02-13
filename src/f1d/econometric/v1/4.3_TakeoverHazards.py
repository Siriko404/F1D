#!/usr/bin/env python3
"""
==============================================================================
STEP 4.3: Takeover Hazards (Cox PH and Fine-Gray Competing Risks)
==============================================================================
ID: 4.3_TakeoverHazards
Description: Analyzes how CEO Clarity and Q&A Uncertainty predict takeover
             probability using survival analysis.

Models:
    - Model 1: Cox Proportional Hazards (All Takeovers)
    - Model 2: Fine-Gray Competing Risks (Uninvited: Hostile + Unsolicited)
    - Model 3: Fine-Gray Competing Risks (Friendly: Friendly + Neutral)

Variables:
    - ClarityRegime: CEO Fixed Effect (time-invariant)
    - ClarityCEO: CEO-specific Fixed Effect
    - Manager_QA_Uncertainty_pct: Call-level vagueness

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
    - 4_Outputs/4.1_CeoClarity/latest/ceo_clarity_scores.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_*.parquet
    - 1_Inputs/SDC/sdc-ma-merged.parquet

Outputs:
    - 4_Outputs/4.3_TakeoverHazards/{timestamp}/
    - stats.json
    - {timestamp}.log

Deterministic: true

Dependencies:
    - Requires: Step 3.3
    - Uses: shared.regression_utils, linearmodels

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# Add parent directory to path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

# Import shared regression and reporting utilities

# Import shared path validation utilities
try:
    from f1d.shared.observability_utils import (
        DualWriter,
        print_stat,
        print_stats_summary,
        save_stats,
    )
    from f1d.shared.path_utils import (
        OutputResolutionError,
        ensure_output_dir,
        get_latest_output_dir,
        validate_input_file,
        validate_output_path,
    )
except ImportError:
    import sys as _sys

    _script_dir = Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from f1d.shared.observability_utils import (
        DualWriter,
        print_stat,
        print_stats_summary,
        save_stats,
    )
    from f1d.shared.path_utils import (
        OutputResolutionError,
        get_latest_output_dir,
    )


import warnings

warnings.filterwarnings("ignore")

# Configuration
CONFIG: Dict[str, Any] = {
    "year_start": 2002,
    "year_end": 2018,
    "clarity_var_regime": "ClarityRegime",
    "clarity_var_ceo": "ClarityCEO",
    "uncertainty_var": "Manager_QA_Uncertainty_pct",
    "firm_controls": [
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
        "Size",
        "BM",
        "Lev",
        "ROA",
    ],
    "exclude_ff12": [8, 11],
}

# Global ROOT - initialized to project root
ROOT: Path = Path(__file__).resolve().parents[4]


# ==============================================================================
# Survival Analysis Functions (Stubs - V1 legacy code)
# ==============================================================================


def run_cox_ph(df, time_col, event_col, formula):
    """
    Run Cox Proportional Hazards model.

    NOTE: This is a stub function for V1 legacy code.
    The full implementation requires lifelines or statsmodels survival.
    """
    raise NotImplementedError(
        "run_cox_ph: Cox PH model not implemented. "
        "Install lifelines (pip install lifelines) and implement using lifelines.CoxPHFitter"
    )


def run_fine_gray(df, time_col, event_col, formula):
    """
    Run Fine-Gray competing risks model.

    NOTE: This is a stub function for V1 legacy code.
    The full implementation requires lifelines or statsmodels survival.
    """
    raise NotImplementedError(
        "run_fine_gray: Fine-Gray model not implemented. "
        "Install lifelines (pip install lifelines) and implement using lifelines.FineGrayAFTFitter"
    )


def load_data():
    """Load and merge all required data for takeover hazard models."""
    print("\n" + "=" * 60)
    print("Loading data")
    print("=" * 60)

    # Load manifest
    manifest_dir = get_latest_output_dir(
        ROOT / "4_Outputs" / "1.0_BuildSampleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    manifest = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "gvkey",
            "start_date",
            "ceo_id",
            "ff12_code",
            "ff48_code",
        ],
    )
    manifest["year"] = pd.to_datetime(manifest["start_date"]).dt.year
    print(f"  Manifest: {len(manifest):,} calls")

    # Load linguistic variables
    all_ling = []
    for year in range(int(CONFIG["year_start"]), int(CONFIG["year_end"]) + 1):
        try:
            lv_dir = get_latest_output_dir(
                ROOT / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
                required_file=f"linguistic_variables_{year}.parquet",
            )
            lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
            lv = pd.read_parquet(lv_path)
            all_ling.append(lv)
        except OutputResolutionError:
            continue
    ling = pd.concat(all_ling, ignore_index=True) if all_ling else pd.DataFrame()
    ling_cols = ["file_name", "Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct"]
    ling_cols = [c for c in ling_cols if c in ling.columns]
    if ling_cols:
        ling = ling[ling_cols].drop_duplicates("file_name")
    print(f"  Linguistic: {len(ling):,} calls")

    # Load clarity scores
    try:
        clarity_dir = get_latest_output_dir(
            ROOT / "4_Outputs" / "4.1_CeoClarity",
            required_file="ceo_clarity_scores.parquet",
        )
        clarity_path = clarity_dir / "ceo_clarity_scores.parquet"
        clarity = pd.read_parquet(
            clarity_path, columns=["ceo_id", "ClarityCEO", "sample"]
        )
        clarity["ceo_id"] = clarity["ceo_id"].astype(str)
        print(f"  Clarity scores: {len(clarity):,} CEOs")
    except OutputResolutionError:
        clarity = pd.DataFrame()
        print("  WARNING: Clarity scores not found")

    # Load firm controls
    all_fc = []
    for year in range(int(CONFIG["year_start"]), int(CONFIG["year_end"]) + 1):
        try:
            fc_dir = get_latest_output_dir(
                ROOT / "4_Outputs" / "3_Financial_Features",
                required_file=f"firm_controls_{year}.parquet",
            )
            fc_path = fc_dir / f"firm_controls_{year}.parquet"
            fc = pd.read_parquet(fc_path)
            all_fc.append(fc)
        except OutputResolutionError:
            continue
    firm = pd.concat(all_fc, ignore_index=True) if all_fc else pd.DataFrame()
    fc_cols = ["file_name"] + [c for c in CONFIG["firm_controls"] if c in firm.columns]
    if fc_cols and len(firm) > 0:
        firm = firm[fc_cols].drop_duplicates("file_name")
    print(f"  Firm controls: {len(firm):,} calls")

    # Load event flags
    try:
        events_dir = get_latest_output_dir(
            ROOT / "4_Outputs" / "3.3_EventFlags",
            required_file="event_flags.parquet",
        )
        events_path = events_dir / "event_flags.parquet"
        events = pd.read_parquet(events_path)
        print(f"  Event flags: {len(events):,} calls")
    except OutputResolutionError:
        events = pd.DataFrame()
        print("  WARNING: Event flags not found")

    # Merge all data
    df = manifest.copy()
    if len(ling) > 0:
        df = df.merge(ling, on="file_name", how="left")
    if len(clarity) > 0:
        df["sample_clarity"] = "Main"
        df.loc[df["ff12_code"] == 11, "sample_clarity"] = "Finance"
        df.loc[df["ff12_code"] == 8, "sample_clarity"] = "Utility"
        df["ceo_id"] = df["ceo_id"].astype(str)
        df = df.merge(
            clarity[["ceo_id", "ClarityCEO", "sample"]],
            left_on=["ceo_id", "sample_clarity"],
            right_on=["ceo_id", "sample"],
            how="left",
        )
        df = df.rename(columns={"ClarityCEO": "ClarityRegime"})
    if len(firm) > 0:
        df = df.merge(firm, on="file_name", how="left")
    if len(events) > 0:
        df = df.merge(events, on="file_name", how="left")

    print(f"\n  Combined: {len(df):,} calls")
    print(f"  With ClarityRegime: {df['ClarityRegime'].notna().sum():,}")
    print(f"  With Uncertainty: {df['Manager_QA_Uncertainty_pct'].notna().sum():,}")

    return df


def parse_arguments():
    """Parse command-line arguments for 4.3_TakeoverHazards.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.3: Takeover Hazard Models

Estimates Cox proportional hazards models for takeover risk.
Tests whether CEO clarity predicts takeover likelihood
using survival analysis.
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
    from f1d.shared.dependency_checker import validate_prerequisites

    required_files: Dict[str, Path] = {}

    required_steps = {
        "4.1_EstimateCeoClarity": "ceo_clarity_scores.parquet",
        "3.3_EventFlags": "event_flags.parquet",
    }

    validate_prerequisites(required_files, required_steps)


def main():
    global ROOT
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Set ROOT if not already set
    if ROOT is None:
        ROOT = Path(__file__).resolve().parents[2]

    # Setup output directories
    out_dir = ROOT / "4_Outputs" / "4.3_TakeoverHazards" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    log_dir = ROOT / "3_Logs" / "4.3_TakeoverHazards" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Initialize stats
    stats: Dict[str, Any] = {
        "step_id": "4.3_TakeoverHazards",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": []},
        "missing_values": {},
        "survival_models": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    log_file = log_dir / f"step4_3_{timestamp}.log"
    dual_writer = DualWriter(log_file)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.3: Takeover Hazards")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load data
    df = load_data()

    # Capture input stats
    stats["input"]["total_rows"] = len(df)
    stats["input"]["total_columns"] = len(df.columns)
    print_stat("Input rows", value=len(df))

    # Filter to Main sample
    print("\n" + "=" * 60)
    print("Filtering to Main Sample")
    print("=" * 60)
    df_main = df[~df["ff12_code"].isin(CONFIG["exclude_ff12"])].copy()
    print(f"  Main Sample: {len(df_main):,} calls")
    print(f"  Takeovers: {df_main['Takeover'].sum():,}")
    print(f"    Uninvited: {(df_main['Takeover_Type'] == 'Uninvited').sum():,}")
    print(f"    Friendly: {(df_main['Takeover_Type'] == 'Friendly').sum():,}")

    # Capture filter stats
    stats["processing"]["sample_filter"] = len(df) - len(df_main)
    print_stat("Sample filtered rows", before=len(df), after=len(df_main))

    # Define covariates for Regime model
    covariates_regime = [
        CONFIG["clarity_var_regime"],
        CONFIG["uncertainty_var"],
    ] + CONFIG["firm_controls"]
    covariates_regime = [c for c in covariates_regime if c in df_main.columns]

    # Define covariates for CEO model
    covariates_ceo = [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]] + CONFIG[
        "firm_controls"
    ]
    covariates_ceo = [c for c in covariates_ceo if c in df_main.columns]

    results = []

    # ===========================================================================
    # MODEL 1: Cox PH - All Takeovers
    # ===========================================================================
    print("\n" + "=" * 60)
    print("MODEL 1: Cox Proportional Hazards - All Takeovers")
    print("=" * 60)

    out_file = out_dir / "cox_ph_all.txt"
    out_file.write_text(f"Generated: {timestamp}\n")

    # Regime Model
    cph_all_regime = run_cox_ph(  # type: ignore[call-arg]
        df_main,
        "Takeover",
        covariates_regime,
        "All Takeovers (Regime Clarity)",
        out_file,
    )
    if cph_all_regime:
        for var in [CONFIG["clarity_var_regime"], CONFIG["uncertainty_var"]]:
            if var in cph_all_regime.summary.index:
                results.append(
                    {
                        "Model": "CPH_All",
                        "Type": "Regime",
                        "Variable": var,
                        "HR": cph_all_regime.summary.loc[var, "exp(coef)"],
                        "Coef": cph_all_regime.summary.loc[var, "coef"],
                        "Pval": cph_all_regime.summary.loc[var, "p"],
                        "N": int(cph_all_regime.event_observed.sum()),
                    }
                )

    # CEO Model
    cph_all_ceo = run_cox_ph(  # type: ignore[call-arg]
        df_main, "Takeover", covariates_ceo, "All Takeovers (CEO Clarity)", out_file
    )
    if cph_all_ceo:
        for var in [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]]:
            if var in cph_all_ceo.summary.index:
                results.append(
                    {
                        "Model": "CPH_All",
                        "Type": "CEO",
                        "Variable": var,
                        "HR": cph_all_ceo.summary.loc[var, "exp(coef)"],
                        "Coef": cph_all_ceo.summary.loc[var, "coef"],
                        "Pval": cph_all_ceo.summary.loc[var, "p"],
                        "N": int(cph_all_ceo.event_observed.sum()),
                    }
                )

    # ===========================================================================
    # MODEL 2: Fine-Gray - Uninvited (Hostile + Unsolicited)
    # ===========================================================================
    print("\n" + "=" * 60)
    print("MODEL 2: Fine-Gray - Uninvited Takeovers")
    print("=" * 60)

    out_file_uninv = out_dir / "fine_gray_uninvited.txt"
    out_file_uninv.write_text(f"Generated: {timestamp}\n")

    fg_uninv_regime = run_fine_gray(  # type: ignore[call-arg]
        df_main,
        "Uninvited",
        covariates_regime,
        "Uninvited (Regime Clarity)",
        out_file_uninv,
    )
    if fg_uninv_regime:
        for var in [CONFIG["clarity_var_regime"], CONFIG["uncertainty_var"]]:
            if var in fg_uninv_regime.summary.index:
                results.append(
                    {
                        "Model": "FG_Uninvited",
                        "Type": "Regime",
                        "Variable": var,
                        "SHR": fg_uninv_regime.summary.loc[var, "exp(coef)"],
                        "Coef": fg_uninv_regime.summary.loc[var, "coef"],
                        "Pval": fg_uninv_regime.summary.loc[var, "p"],
                        "N": int(fg_uninv_regime.event_observed.sum()),
                    }
                )

    fg_uninv_ceo = run_fine_gray(  # type: ignore[call-arg]
        df_main, "Uninvited", covariates_ceo, "Uninvited (CEO Clarity)", out_file_uninv
    )
    if fg_uninv_ceo:
        for var in [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]]:
            if var in fg_uninv_ceo.summary.index:
                results.append(
                    {
                        "Model": "FG_Uninvited",
                        "Type": "CEO",
                        "Variable": var,
                        "SHR": fg_uninv_ceo.summary.loc[var, "exp(coef)"],
                        "Coef": fg_uninv_ceo.summary.loc[var, "coef"],
                        "Pval": fg_uninv_ceo.summary.loc[var, "p"],
                        "N": int(fg_uninv_ceo.event_observed.sum()),
                    }
                )

    # ===========================================================================
    # MODEL 3: Fine-Gray - Friendly (Friendly + Neutral)
    # ===========================================================================
    print("\n" + "=" * 60)
    print("MODEL 3: Fine-Gray - Friendly Takeovers")
    print("=" * 60)

    out_file_friend = out_dir / "fine_gray_friendly.txt"
    out_file_friend.write_text(f"Generated: {timestamp}\n")

    fg_friend_regime = run_fine_gray(  # type: ignore[call-arg]
        df_main,
        "Friendly",
        covariates_regime,
        "Friendly (Regime Clarity)",
        out_file_friend,
    )
    if fg_friend_regime:
        for var in [CONFIG["clarity_var_regime"], CONFIG["uncertainty_var"]]:
            if var in fg_friend_regime.summary.index:
                results.append(
                    {
                        "Model": "FG_Friendly",
                        "Type": "Regime",
                        "Variable": var,
                        "SHR": fg_friend_regime.summary.loc[var, "exp(coef)"],
                        "Coef": fg_friend_regime.summary.loc[var, "coef"],
                        "Pval": fg_friend_regime.summary.loc[var, "p"],
                        "N": int(fg_friend_regime.event_observed.sum()),
                    }
                )

    fg_friend_ceo = run_fine_gray(  # type: ignore[call-arg]
        df_main, "Friendly", covariates_ceo, "Friendly (CEO Clarity)", out_file_friend
    )
    if fg_friend_ceo:
        for var in [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]]:
            if var in fg_friend_ceo.summary.index:
                results.append(
                    {
                        "Model": "FG_Friendly",
                        "Type": "CEO",
                        "Variable": var,
                        "SHR": fg_friend_ceo.summary.loc[var, "exp(coef)"],
                        "Coef": fg_friend_ceo.summary.loc[var, "coef"],
                        "Pval": fg_friend_ceo.summary.loc[var, "p"],
                        "N": int(fg_friend_ceo.event_observed.sum()),
                    }
                )

    # ===========================================================================
    # Save Results
    # ===========================================================================
    print("\n" + "=" * 60)
    print("Saving Results")
    print("=" * 60)

    # Hazard ratios summary
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv(out_dir / "hazard_ratios.csv", index=False)
        print("  Saved: hazard_ratios.csv")

        # Capture survival model stats
        stats["survival_models"]["cox_ph_all"] = len(
            [r for r in results if r["Model"] == "CPH_All"]
        )
        stats["survival_models"]["fine_gray_uninvited"] = len(
            [r for r in results if r["Model"] == "FG_Uninvited"]
        )
        stats["survival_models"]["fine_gray_friendly"] = len(
            [r for r in results if r["Model"] == "FG_Friendly"]
        )

    # Event summary
    summary = {
        "Sample": "Main",
        "N_Calls": len(df_main),
        "N_Takeover": int(df_main["Takeover"].sum()),
        "N_Uninvited": int((df_main["Takeover_Type"] == "Uninvited").sum()),
        "N_Friendly": int((df_main["Takeover_Type"] == "Friendly").sum()),
        "Pct_Takeover": df_main["Takeover"].mean() * 100,
    }
    pd.DataFrame([summary]).to_csv(out_dir / "takeover_event_summary.csv", index=False)
    print("  Saved: takeover_event_summary.csv")

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    # Final stats
    stats["output"]["final_rows"] = len(df_main)
    stats["output"]["final_columns"] = len(df_main.columns)
    stats["output"]["files"] = [
        "cox_ph_all.txt",
        "fine_gray_uninvited.txt",
        "fine_gray_friendly.txt",
        "hazard_ratios.csv",
        "takeover_event_summary.csv",
    ]
    stats["timing"]["end_iso"] = end_time.isoformat()
    stats["timing"]["duration_seconds"] = round(duration, 2)

    # Save and print stats summary
    print_stats_summary(stats)
    save_stats(stats, out_dir)

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        # validate_prerequisites already prints "[OK] All prerequisites validated"
        sys.exit(0)

    check_prerequisites(root)
    main()
