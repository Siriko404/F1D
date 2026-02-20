#!/usr/bin/env python3
"""
==============================================================================
STEP 4.1.2: Estimate CEO Clarity (Extended Controls Robustness)
==============================================================================
ID: 4.1.2_EstimateCeoClarity_Extended
Description: Run robustness tests with extended financial controls.

Purpose:
    Run 4 regressions to test robustness with extended financial controls:
    1. Manager (Baseline) - Manager_QA_Uncertainty_pct with base controls
    2. Manager (Extended) - + CurrentRatio, RD_Intensity, Volatility
    3. CEO-Only (Baseline) - CEO_QA_Uncertainty_pct with base controls
    4. CEO-Only (Extended) - + CurrentRatio, RD_Intensity, Volatility

    This tests whether adding financial/market controls changes the CEO fixed
    effects estimates, providing evidence for the robustness of the Clarity
    measure.

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - outputs/3_Financial_Features/latest/market_variables_{year}.parquet

Outputs:
    - outputs/4.1.2_CeoClarity_Extended/{timestamp}/ceo_clarity_scores_{model}.parquet
    - outputs/4.1.2_CeoClarity_Extended/{timestamp}/regression_results_{model}_{sample}.txt
    - outputs/4.1.2_CeoClarity_Extended/{timestamp}/model_diagnostics.csv
    - outputs/4.1.2_CeoClarity_Extended/{timestamp}/report_step4_1_2.md

Deterministic: true
Dependencies:
    - Requires: Step 3.1
    - Uses: shared.regression_utils, shared.panel_ols, linearmodels

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

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

# Import shared regression and reporting utilities
from f1d.shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    compute_file_checksum,
    print_stats_summary,
    save_stats,
)

# Import shared path validation utilities
from f1d.shared.path_utils import (
    get_latest_output_dir,
)
from f1d.shared.regression_utils import run_fixed_effects_ols
from f1d.shared.regression_validation import (
    validate_columns,
    validate_sample_size,
)

# ==============================================================================
# CLI Arguments & Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 4.1.2_EstimateCeoClarity_Extended.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.1.2: Estimate CEO Fixed Effects - Extended Controls Robustness

Run 4 regressions to test robustness with extended financial controls:
    1. Manager (Baseline) - Manager_QA_Uncertainty_pct with base controls
    2. Manager (Extended) - + CurrentRatio, RD_Intensity, Volatility
    3. CEO-Only (Baseline) - CEO_QA_Uncertainty_pct with base controls
    4. CEO-Only (Extended) - + CurrentRatio, RD_Intensity, Volatility

This tests whether adding financial/market controls changes CEO fixed
effects estimates, providing evidence for robustness of the Clarity measure.
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

    required_files: Dict[str, Any] = {}

    required_steps = {
        "2.2_ConstructVariables": "linguistic_variables.parquet",
        "3.1_FirmControls": "firm_controls.parquet",
        "3.2_MarketVariables": "market_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Configuration - 4 Models
# ==============================================================================

# Base controls (same as 4.1 and 4.1.1)
BASE_FIRM_CONTROLS = ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]

# Extended controls (new financial variables)
EXTENDED_CONTROLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CurrentRatio",
    "RD_Intensity",
    "Volatility",
]

# Model configurations
# Note: Manager models use Manager_QA_Uncertainty (management team incl. CEO)
#       CEO models use CEO_QA_Uncertainty (CEO only)
# Note: Only Analyst_QA_* variables are allowed for analyst controls
MODELS: Dict[str, Dict[str, Any]] = {
    "Manager_Baseline": {
        "dependent_var": "Manager_QA_Uncertainty_pct",
        "linguistic_controls": [
            "Manager_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct",  # Only Analyst_QA_* variables allowed
            "Entire_All_Negative_pct",
        ],
        "firm_controls": BASE_FIRM_CONTROLS,
        "description": "Manager Q&A Uncertainty with baseline controls",
    },
    "Manager_Extended": {
        "dependent_var": "Manager_QA_Uncertainty_pct",
        "linguistic_controls": [
            "Manager_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct",  # Only Analyst_QA_* variables allowed
            "Entire_All_Negative_pct",
        ],
        "firm_controls": BASE_FIRM_CONTROLS + EXTENDED_CONTROLS,
        "description": "Manager Q&A Uncertainty with extended controls",
    },
    "CEO_Baseline": {
        "dependent_var": "CEO_QA_Uncertainty_pct",
        "linguistic_controls": [
            "CEO_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct",
            "Entire_All_Negative_pct",
        ],
        "firm_controls": BASE_FIRM_CONTROLS,
        "description": "CEO Q&A Uncertainty with baseline controls",
    },
    "CEO_Extended": {
        "dependent_var": "CEO_QA_Uncertainty_pct",
        "linguistic_controls": [
            "CEO_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct",
            "Entire_All_Negative_pct",
        ],
        "firm_controls": BASE_FIRM_CONTROLS + EXTENDED_CONTROLS,
        "description": "CEO Q&A Uncertainty with extended controls",
    },
}

GLOBAL_CONFIG: Dict[str, Any] = {
    "min_calls_per_ceo": 5,
    "year_start": 2002,
    "year_end": 2018,
    "samples": {
        "Main": {"exclude_ff12": [8, 11], "include_ff12": None},
        "Finance": {"exclude_ff12": None, "include_ff12": [11]},
        "Utility": {"exclude_ff12": None, "include_ff12": [8]},
    },
}

# ==============================================================================
# Data Loading
# ==============================================================================


def load_all_data(root, year_start, year_end, stats=None):
    """Load and merge all input data sources."""
    print("\n" + "=" * 60)
    print("Loading and merging data")
    print("=" * 60)

    # Resolve directories using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    lv_dir = get_latest_output_dir(
        root / "outputs" / "2_Textual_Analysis" / "2.2_Variables"
    )
    # Require market_variables to ensure complete Stage 3 outputs
    # (directories with market_variables also have firm_controls)
    fc_dir = get_latest_output_dir(
        root / "outputs" / "3_Financial_Features",
        required_file="market_variables_2010.parquet",
    )

    # Load manifest
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    manifest = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "gvkey",
            "start_date",
            "ceo_id",
            "ceo_name",
            "ff12_code",
            "ff12_name",
        ],
    )
    print(f"  Manifest: {len(manifest):,} calls")
    if stats:
        stats["input"]["files"].append(str(manifest_path))
        stats["input"]["checksums"]["manifest"] = compute_file_checksum(manifest_path)

    # Load per-year data
    all_data = []

    for year in range(year_start, year_end + 1):
        # Linguistic variables (from 2.2_Variables - same as 4.1 and 4.1.1)
        lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
        if not lv_path.exists():
            print(f"  WARNING: Missing linguistic_variables_{year}.parquet")
            continue

        lv = pd.read_parquet(lv_path)

        # Drop columns that would conflict with manifest
        lv_drop_cols = [c for c in ["gvkey", "year", "start_date"] if c in lv.columns]
        if lv_drop_cols:
            lv = lv.drop(columns=lv_drop_cols)

        # Firm controls
        fc_path = fc_dir / f"firm_controls_{year}.parquet"
        fc = pd.read_parquet(fc_path) if fc_path.exists() else pd.DataFrame()

        # Market variables
        mv_path = fc_dir / f"market_variables_{year}.parquet"
        mv = pd.read_parquet(mv_path) if mv_path.exists() else pd.DataFrame()

        # Filter manifest to this year's files
        year_files = set(lv["file_name"])
        mf_year = manifest[manifest["file_name"].isin(year_files)].copy()

        # Merge linguistic variables
        merged = mf_year.merge(lv, on="file_name", how="left")

        # Merge firm controls
        if len(fc) > 0:
            # Get all needed firm control columns
            all_firm_cols = list(set(BASE_FIRM_CONTROLS + EXTENDED_CONTROLS))
            fc_cols = ["file_name"] + [c for c in fc.columns if c in all_firm_cols]
            merged = merged.merge(fc[fc_cols], on="file_name", how="left")

        # Merge market variables (MarketRet, Volatility may be here)
        if len(mv) > 0:
            all_mkt_cols = list(set(BASE_FIRM_CONTROLS + EXTENDED_CONTROLS))
            # Only add columns not already in merged
            existing = set(merged.columns)
            mv_cols = ["file_name"] + [
                c for c in mv.columns if c in all_mkt_cols and c not in existing
            ]
            if len(mv_cols) > 1:  # more than just file_name
                merged = merged.merge(mv[mv_cols], on="file_name", how="left")

        merged["year"] = year
        all_data.append(merged)
        print(f"  {year}: {len(merged):,} calls")

    combined = pd.concat(all_data, ignore_index=True)
    print(f"\n  Total: {len(combined):,} calls")
    print(f"  Unique CEOs: {combined['ceo_id'].nunique():,}")
    print(f"  Unique firms: {combined['gvkey'].nunique():,}")

    return combined


# ==============================================================================
# Data Preparation (per model)
# ==============================================================================


def prepare_regression_data(df, model_config, model_name):
    """Filter to complete cases for a specific model."""
    print(f"\n  Preparing data for {model_name}...")

    initial_n = len(df)

    # Filter to non-null ceo_id
    df_model = df[df["ceo_id"].notna()].copy()

    # Define required variables for this model
    required = (
        [model_config["dependent_var"]]
        + model_config["linguistic_controls"]
        + model_config["firm_controls"]
        + ["ceo_id", "year"]
    )

    # Check which variables exist
    missing_vars = [v for v in required if v not in df_model.columns]
    if missing_vars:
        print(f"    WARNING: Missing variables: {missing_vars}")
        required = [v for v in required if v in df_model.columns]

    # Filter to complete cases
    complete_mask = df_model[required].notna().all(axis=1)
    df_model = df_model[complete_mask].copy()
    print(f"    Complete cases: {len(df_model):,} / {initial_n:,}")

    # Assign industry samples
    df_model["sample"] = "Main"
    df_model.loc[df_model["ff12_code"] == 11, "sample"] = "Finance"
    df_model.loc[df_model["ff12_code"] == 8, "sample"] = "Utility"

    return df_model


# ==============================================================================
# Regression Estimation
# ==============================================================================


def run_regression(df_sample, model_config, model_name, sample_name):
    """Run OLS regression with CEO fixed effects."""
    print("\n" + "=" * 60)
    print(f"Regression: {model_name} / {sample_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, None

    # Filter to CEOs with minimum calls
    min_calls = GLOBAL_CONFIG["min_calls_per_ceo"]
    ceo_counts = df_sample["ceo_id"].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"  After >=5 calls filter: {len(df_reg):,} calls, {df_reg['ceo_id'].nunique():,} CEOs"
    )

    if len(df_reg) < 100:
        print("  WARNING: Too few observations, skipping")
        return None, None, None

    # Convert to string for categorical treatment
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula
    dep_var = model_config["dependent_var"]
    controls = model_config["linguistic_controls"] + model_config["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula[:80]}...")
    print(f"  N controls: {len(controls)}")

    # Validate regression data before estimation
    print("  Validating regression data...")
    try:
        required_columns = [dep_var] + controls + ["ceo_id", "year"]
        validate_columns(df_reg, required_columns)
        validate_sample_size(df_reg, min_observations=100)
        print("  Validation passed")
    except Exception as e:
        print(f"  Validation failed: {e}")
        return None, None, None

    # Estimate model using shared function
    print("  Estimating...")
    start_time = datetime.now()

    try:
        model = run_fixed_effects_ols(
            df_reg, formula, f"{model_name}_{sample_name}", cov_type="HC1"
        )
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}")
        return None, None, None

    duration = (datetime.now() - start_time).total_seconds()

    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adj R-squared: {model.rsquared_adj:.4f}")

    return model, df_reg, valid_ceos


# ==============================================================================
# Extract CEO Fixed Effects
# ==============================================================================


def extract_ceo_fixed_effects(model, df_reg, model_name, sample_name):
    """Extract gamma_i coefficients and compute Clarity scores."""
    # Get CEO coefficient names
    ceo_params = {
        p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")
    }

    # Parse CEO IDs
    ceo_effects = {}
    for param_name, gamma_i in ceo_params.items():
        if "[T." in param_name:
            ceo_id = param_name.split("[T.")[1].split("]")[0]
            ceo_effects[ceo_id] = gamma_i

    # Reference CEO gets gamma = 0
    all_ceos = df_reg["ceo_id"].unique()
    for ref_ceo in [c for c in all_ceos if c not in ceo_effects]:
        ceo_effects[ref_ceo] = 0.0

    # Create DataFrame
    ceo_fe = pd.DataFrame(list(ceo_effects.items()), columns=["ceo_id", "gamma_i"])
    ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]

    # Standardize
    mean_val = ceo_fe["ClarityCEO_raw"].mean()
    std_val = ceo_fe["ClarityCEO_raw"].std()
    ceo_fe["ClarityCEO"] = (ceo_fe["ClarityCEO_raw"] - mean_val) / std_val

    ceo_fe["model"] = model_name
    ceo_fe["sample"] = sample_name

    return ceo_fe


# ==============================================================================
# Compute CEO-Level Statistics
# ==============================================================================


def compute_ceo_stats(df_sample_filtered, ceo_fe, model_config):
    """Compute descriptive statistics per CEO."""
    dep_var = model_config["dependent_var"]

    ceo_stats = (
        df_sample_filtered.groupby("ceo_id")
        .agg(
            {
                dep_var: ["count", "mean", "std"],
                "ceo_name": "first",
                "start_date": ["min", "max"],
                "gvkey": "nunique",
            }
        )
        .reset_index()
    )

    ceo_stats.columns = [
        "ceo_id",
        "n_calls",
        "avg_uncertainty",
        "std_uncertainty",
        "ceo_name",
        "first_call_date",
        "last_call_date",
        "n_firms",
    ]

    ceo_stats["ceo_id"] = ceo_stats["ceo_id"].astype(str)
    ceo_scores = ceo_fe.merge(ceo_stats, on="ceo_id", how="left")
    ceo_scores = ceo_scores.sort_values("ClarityCEO", ascending=False).reset_index(
        drop=True
    )

    return ceo_scores


# ==============================================================================
# Model Diagnostics
# ==============================================================================


def compute_diagnostics(model, model_name, sample_name, n_ceos, n_firms, n_controls):
    """Compute model diagnostics."""
    return {
        "model": model_name,
        "sample": sample_name,
        "n_observations": int(model.nobs),
        "n_ceos": n_ceos,
        "n_firms": n_firms,
        "n_controls": n_controls,
        "r_squared": model.rsquared,
        "r_squared_adj": model.rsquared_adj,
        "f_statistic": model.fvalue,
        "f_pvalue": model.f_pvalue,
        "aic": model.aic,
        "bic": model.bic,
    }


# ==============================================================================
# Save Outputs
# ==============================================================================


def save_outputs(all_ceo_scores, all_diagnostics, all_models, out_dir, stats=None):
    """Save all output files."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    # CEO Clarity Scores (all models combined)
    ceo_scores_df = pd.concat(all_ceo_scores, ignore_index=True)
    ceo_scores_path = out_dir / "ceo_clarity_scores_all.parquet"
    ceo_scores_df.to_parquet(ceo_scores_path, index=False)
    print(f"  Saved: ceo_clarity_scores_all.parquet ({len(ceo_scores_df):,} rows)")

    # Regression results (per model/sample)
    for (model_name, sample_name), model in all_models.items():
        if model is not None:
            results_path = (
                out_dir
                / f"regression_results_{model_name.lower()}_{sample_name.lower()}.txt"
            )
            with open(results_path, "w") as f:
                f.write(model.summary().as_text())
            print(f"  Saved: {results_path.name}")

    # Model diagnostics
    if all_diagnostics:
        diag_df = pd.DataFrame(all_diagnostics)
        diag_path = out_dir / "model_diagnostics.csv"
        diag_df.to_csv(diag_path, index=False)
        print("  Saved: model_diagnostics.csv")

    return ceo_scores_df


# ==============================================================================
# Generate Report
# ==============================================================================


def generate_report(all_diagnostics, out_dir, duration):
    """Generate markdown report comparing models."""
    print("\n  Generating report...")

    report_lines = [
        "# Step 4.1.2: Extended Controls Robustness Check",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Purpose",
        "Test robustness of CEO Clarity estimates by adding extended financial controls.",
        "",
        "## Extended Controls Added",
        "- Size (log total assets)",
        "- BM (Book-to-Market ratio)",
        "- Lev (Leverage)",
        "- ROA (Return on Assets)",
        "- CurrentRatio (Current Assets / Current Liabilities)",
        "- RD_Intensity (R&D / Total Assets)",
        "- Volatility (Stock return volatility)",
        "",
        "## Results Summary",
        "",
        "| Model | Sample | N | CEOs | R-squared | Adj R-sq | Controls |",
        "|-------|--------|---|------|-----------|----------|----------|",
    ]

    for diag in all_diagnostics:
        report_lines.append(
            f"| {diag['model']} | {diag['sample']} | {diag['n_observations']:,} | "
            f"{diag['n_ceos']:,} | {diag['r_squared']:.4f} | {diag['r_squared_adj']:.4f} | "
            f"{diag['n_controls']} |"
        )

    report_lines.append("")
    report_lines.append("## Interpretation")
    report_lines.append("")
    report_lines.append(
        "If R-squared increases only marginally when adding extended controls,"
    )
    report_lines.append(
        "this suggests the CEO fixed effects are robust and not confounded by"
    )
    report_lines.append("omitted firm characteristics.")
    report_lines.append("")

    # Write report
    report_path = out_dir / "report_step4_1_2.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: report_step4_1_2.md")


# ==============================================================================
# Main
# ==============================================================================


def main(year_start=None, year_end=None):
    """Main execution."""
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "4.1.2_EstimateCeoClarity_Extended",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "regressions": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": []},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    # Override config if provided
    if year_start:
        GLOBAL_CONFIG["year_start"] = year_start
    if year_end:
        GLOBAL_CONFIG["year_end"] = year_end

    # Setup paths
    # From src/f1d/econometric/v1/ -> need parents[4] to reach project root
    root = Path(__file__).resolve().parents[4]
    out_dir = root / "outputs" / "4.1.2_CeoClarity_Extended" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "logs" / "4.1.2_CeoClarity_Extended" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Setup dual logging
    log_path = log_dir / f"step4_1_2_{timestamp}.log"
    dual_writer = DualWriter(log_path)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.1.2: Extended Controls Robustness Check")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {GLOBAL_CONFIG['year_start']}-{GLOBAL_CONFIG['year_end']}")
    print(f"Models: {list(MODELS.keys())}")

    # Load data once
    df = load_all_data(root, GLOBAL_CONFIG["year_start"], GLOBAL_CONFIG["year_end"])

    # Run all 4 models
    all_ceo_scores = []
    all_diagnostics = []
    all_models = {}

    for model_name, model_config in MODELS.items():
        print(f"\n{'#' * 80}")
        print(f"# MODEL: {model_name}")
        print(f"# {model_config['description']}")
        print(f"{'#' * 80}")

        # Prepare data for this model
        df_model = prepare_regression_data(df, model_config, model_name)

        # Run for each industry sample
        for sample_name in ["Main", "Finance", "Utility"]:
            df_sample = df_model[df_model["sample"] == sample_name].copy()

            if len(df_sample) < 100:
                print(
                    f"\n  Skipping {sample_name}: too few observations ({len(df_sample)})"
                )
                continue

            # Run regression
            model, df_reg, valid_ceos = run_regression(
                df_sample, model_config, model_name, sample_name
            )

            if model is None:
                continue

            all_models[(model_name, sample_name)] = model

            # Extract CEO fixed effects
            ceo_fe = extract_ceo_fixed_effects(model, df_reg, model_name, sample_name)

            # Filter original to valid CEOs for stats
            df_sample_filtered = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

            # Compute CEO stats
            ceo_scores = compute_ceo_stats(df_sample_filtered, ceo_fe, model_config)
            all_ceo_scores.append(ceo_scores)

            # Compute diagnostics
            n_controls = len(
                [
                    c
                    for c in model_config["linguistic_controls"]
                    + model_config["firm_controls"]
                    if c in df_reg.columns
                ]
            )
            diag = compute_diagnostics(
                model,
                model_name,
                sample_name,
                len(valid_ceos),
                df_sample_filtered["gvkey"].nunique(),
                n_controls,
            )
            all_diagnostics.append(diag)

    # Save outputs
    if all_ceo_scores:
        save_outputs(all_ceo_scores, all_diagnostics, all_models, out_dir, stats)

        # Generate report
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(all_diagnostics, out_dir, duration)

    # Update symlink

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")
    print(f"Models run: {len(all_models)}")

    # Final stats
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(
        (datetime.now() - start_time).total_seconds(), 2
    )

    if all_ceo_scores:
        ceo_scores_df = pd.concat(all_ceo_scores, ignore_index=True)
        stats["missing_values"] = analyze_missing_values(ceo_scores_df)

        if all_diagnostics:
            for diag in all_diagnostics:
                key = diag.get("sample", "unknown")
                stats["regressions"][key] = {
                    "n_observations": diag.get("n_observations", 0),
                    "n_ceos": diag.get("n_ceos", 0),
                    "n_firms": diag.get("n_firms", 0),
                    "r_squared": diag.get("r_squared", 0),
                    "r_squared_adj": diag.get("r_squared_adj", 0),
                    "f_statistic": diag.get("f_statistic", 0),
                    "f_pvalue": diag.get("f_pvalue", 0),
                    "aic": diag.get("aic", 0),
                    "bic": diag.get("bic", 0),
                }

    print_stats_summary(stats)
    save_stats(stats, out_dir)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    # From src/f1d/econometric/v1/ -> need parents[4] to reach project root
    root = Path(__file__).resolve().parents[4]

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        # validate_prerequisites already prints "[OK] All prerequisites validated"
        sys.exit(0)

    # check_prerequisites(root)  # Skip validation - data exists
    sys.exit(main())
