#!/usr/bin/env python3
"""
==============================================================================
STEP 4.3: Takeover Hazards (Cox PH and Fine-Gray Competing Risks)
==============================================================================
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
    - 4_Outputs/4.3_TakeoverHazards/TIMESTAMP/
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import argparse

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
from shared.regression_utils import run_fixed_effects_ols
from shared.reporting_utils import (
    generate_regression_report,
    save_model_diagnostics,
    save_variable_reference,
)
from shared.symlink_utils import update_latest_link


# Import shared path validation utilities
try:
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
    )
    from shared.observability_utils import DualWriter
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path

    _script_dir = Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
    )
    from shared.observability_utils import DualWriter

from shared.regression_validation import (
    validate_columns,
    validate_sample_size,
)

from lifelines import CoxPHFitter
import warnings
import hashlib
import json

warnings.filterwarnings("ignore")


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
    from shared.dependency_checker import validate_prerequisites

    required_files = {}

    required_steps = {
        "4.1_EstimateCeoClarity": "ceo_clarity_scores.parquet",
        "3.3_EventFlags": "event_flags.parquet",
    }

    validate_prerequisites(required_files, required_steps)


def main():
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Setup output directories
    out_dir = ROOT / "4_Outputs" / "4.3_TakeoverHazards" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    log_dir = ROOT / "3_Logs" / "4.3_TakeoverHazards" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Initialize stats
    stats = {
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
    cph_all_regime = run_cox_ph(
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
    cph_all_ceo = run_cox_ph(
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

    fg_uninv_regime = run_fine_gray(
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

    fg_uninv_ceo = run_fine_gray(
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

    fg_friend_regime = run_fine_gray(
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

    fg_friend_ceo = run_fine_gray(
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
        print(f"  Saved: hazard_ratios.csv")

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
    print(f"  Saved: takeover_event_summary.csv")

    # Update latest symlink
    try:
        update_latest_link(out_dir, out_dir.parent / "latest")
    except PermissionError as e:
        print(f"ERROR: Permission denied updating latest symlink: {e}", file=sys.stderr)
        print(f"  Directory: {out_dir}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: OS error updating latest symlink: {e}", file=sys.stderr)
        print(f"  Directory: {out_dir}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to update latest symlink: {e}", file=sys.stderr)
        print(f"  Directory: {out_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"  Created 'latest' copy")

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
        print("✓ All prerequisites validated")
        sys.exit(0)

    check_prerequisites(root)
    main()
