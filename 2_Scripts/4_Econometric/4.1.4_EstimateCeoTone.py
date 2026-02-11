#!/usr/bin/env python3
"""
==============================================================================
STEP 4.1.4: Estimate CEO Tone (Net Sentiment as Personal Style)
==============================================================================
ID: 4.1.4_EstimateCeoTone
Description: Estimate CEO "Tone" (Net Sentiment = Positive - Negative)
             as a persistent communication trait using fixed effects.

Purpose:
    Estimate CEO "Tone" (Net Sentiment = Positive - Negative) as a persistent
    communication trait using fixed effects OLS regression.

    Runs 3 models for each industry sample:
    - ToneAll: CEO FE on all manager speech
    - ToneCEO: CEO FE on CEO's own speech only
    - ToneRegime: CEO FE on non-CEO manager speech only

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet

Outputs:
    - 4_Outputs/4.1.4_CeoTone/{timestamp}/ceo_tone_scores.parquet
    - 4_Outputs/4.1.4_CeoTone/{timestamp}/regression_results_{model}_{sample}.txt
    - 4_Outputs/4.1.4_CeoTone/{timestamp}/model_diagnostics.csv
    - 4_Outputs/4.1.4_CeoTone/{timestamp}/report_step4_1_4.md

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
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add 2_Scripts to Python path for shared module imports (MUST be before shared imports)
scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scripts_dir))

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

warnings.filterwarnings("ignore", category=FutureWarning)

# Import shared utilities


# Import shared path validation utilities
from shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    compute_file_checksum,
    print_stats_summary,
    save_stats,
)
from shared.path_utils import (
    OutputResolutionError,
    get_latest_output_dir,
)
from shared.regression_validation import (
    validate_columns,
    validate_sample_size,
)

# ==============================================================================
# CLI Arguments & Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 4.1.4_EstimateCeoTone.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.1.4: Estimate CEO Tone

Estimates CEO tone measures (positive/negative/uncertainty)
from linguistic variables. Extracts CEO-specific tone
coefficients using fixed effects regression.
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
        "2.2_ConstructVariables": "linguistic_variables.parquet",
        "3.1_FirmControls": "firm_controls.parquet",
        "3.2_MarketVariables": "market_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Configuration
# ==============================================================================

# Three model specifications
MODEL_SPECS = {
    "ToneAll": {
        "dependent_var": "Manager_QA_NetTone",
        "linguistic_controls": [
            "Manager_Pres_NetTone",
            "Analyst_QA_NetTone",
            "Entire_All_Uncertainty_pct",
        ],
        "description": "All Manager Tone",
    },
    "ToneCEO": {
        "dependent_var": "CEO_QA_NetTone",
        "linguistic_controls": [
            "CEO_Pres_NetTone",
            "Analyst_QA_NetTone",
            "Entire_All_Uncertainty_pct",
        ],
        "description": "CEO Personal Tone",
    },
    "ToneRegime": {
        "dependent_var": "NonCEO_Manager_QA_NetTone",
        "linguistic_controls": [
            "Manager_Pres_NetTone",
            "Analyst_QA_NetTone",
            "Entire_All_Uncertainty_pct",
        ],
        "description": "CEO Regime Tone (Influence on Team)",
    },
}

CONFIG = {
    "firm_controls": ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"],
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

    # Load manifest
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.0_BuildSampleManifest",
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
            "ceo_name",
            "ff12_code",
            "ff12_name",
        ],
    )
    print(f"  Manifest: {len(manifest):,} calls")
    if stats:
        stats["input"]["files"].append(str(manifest_path))
        stats["input"]["checksums"]["manifest"] = compute_file_checksum(manifest_path)

    # Load linguistic variables, firm controls per year
    all_data = []

    for year in range(year_start, year_end + 1):
        # Linguistic variables
        try:
            lv_dir = get_latest_output_dir(
                root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
                required_file=f"linguistic_variables_{year}.parquet",
            )
            lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
        except OutputResolutionError:
            print(f"  WARNING: Missing linguistic_variables_{year}.parquet")
            continue

        lv = pd.read_parquet(lv_path)

        # Drop columns that would conflict with manifest
        lv_drop_cols = [c for c in ["gvkey", "year", "start_date"] if c in lv.columns]
        if lv_drop_cols:
            lv = lv.drop(columns=lv_drop_cols)

        # Firm controls
        try:
            fc_dir = get_latest_output_dir(
                root / "4_Outputs" / "3_Financial_Features",
                required_file=f"firm_controls_{year}.parquet",
            )
            fc_path = fc_dir / f"firm_controls_{year}.parquet"
            fc = pd.read_parquet(fc_path)
        except OutputResolutionError:
            fc = pd.DataFrame()

        # Market variables
        try:
            mv_dir = get_latest_output_dir(
                root / "4_Outputs" / "3_Financial_Features",
                required_file=f"market_variables_{year}.parquet",
            )
            mv_path = mv_dir / f"market_variables_{year}.parquet"
            mv = pd.read_parquet(mv_path)
        except OutputResolutionError:
            mv = pd.DataFrame()

        # Filter manifest to this year
        year_files = set(lv["file_name"])
        mf_year = manifest[manifest["file_name"].isin(year_files)].copy()

        # Merge linguistic variables
        merged = mf_year.merge(lv, on="file_name", how="left")

        # Merge firm controls
        if len(fc) > 0:
            fc_cols = ["file_name"] + [
                c for c in fc.columns if c in CONFIG["firm_controls"]
            ]
            merged = merged.merge(fc[fc_cols], on="file_name", how="left")

        # Merge market variables
        if len(mv) > 0:
            mv_cols = ["file_name"] + [
                c for c in mv.columns if c in CONFIG["firm_controls"]
            ]
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
# Compute NetTone Variables
# ==============================================================================


def compute_net_tone(df):
    """Compute NetTone = Positive - Negative for each sample/context."""
    print("\n" + "=" * 60)
    print("Computing NetTone Variables")
    print("=" * 60)

    # Define sample/context combinations
    samples = ["Manager", "CEO", "NonCEO_Manager", "Analyst", "Entire"]
    contexts = ["QA", "Pres", "All"]

    created = 0
    for s in samples:
        for c in contexts:
            pos_col = f"{s}_{c}_Positive_pct"
            neg_col = f"{s}_{c}_Negative_pct"
            tone_col = f"{s}_{c}_NetTone"

            if pos_col in df.columns and neg_col in df.columns:
                df[tone_col] = df[pos_col] - df[neg_col]
                created += 1

    print(f"  Created {created} NetTone variables")

    # Print sample stats
    for col in ["Manager_QA_NetTone", "CEO_QA_NetTone", "NonCEO_Manager_QA_NetTone"]:
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            print(f"  {col}: mean={mean:.4f}, std={std:.4f}")

    return df


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_regression_data(df, model_spec):
    """Filter to complete cases for a specific model."""

    # Filter to non-null ceo_id
    df = df[df["ceo_id"].notna()].copy()

    # Define required variables for this model
    required = (
        [model_spec["dependent_var"]]
        + model_spec["linguistic_controls"]
        + CONFIG["firm_controls"]
        + ["ceo_id", "year"]
    )

    # Check which variables exist
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        print(f"    WARNING: Missing variables: {missing_vars}")
        required = [v for v in required if v in df.columns]

    # Filter to complete cases
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()

    # Assign industry samples
    df["sample"] = "Main"
    df.loc[df["ff12_code"] == 11, "sample"] = "Finance"
    df.loc[df["ff12_code"] == 8, "sample"] = "Utility"

    return df


# ==============================================================================
# Regression Estimation
# ==============================================================================


def run_regression(df_sample, model_name, model_spec, sample_name):
    """Run OLS regression with CEO fixed effects for a single model/sample."""
    print(f"\n  [{model_name} - {sample_name}]")

    if not STATSMODELS_AVAILABLE:
        print("    ERROR: statsmodels not available")
        return None, None, None

    # Filter to CEOs with minimum calls
    min_calls = CONFIG["min_calls_per_ceo"]
    ceo_counts = df_sample["ceo_id"].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"    After >=5 calls filter: {len(df_reg):,} calls, {df_reg['ceo_id'].nunique():,} CEOs"
    )

    if len(df_reg) < 100:
        print(f"    WARNING: Too few observations ({len(df_reg)}), skipping")
        return None, None, None

    # Convert to string for categorical treatment
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula
    dep_var = model_spec["dependent_var"]
    controls = model_spec["linguistic_controls"] + CONFIG["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"

    # Validate regression data before estimation
    print("    Validating regression data...")
    try:
        required_columns = [dep_var] + controls + ["ceo_id", "year"]
        validate_columns(df_reg, required_columns)
        validate_sample_size(df_reg, min_observations=100)
        print("    Validation passed")
    except ValueError as e:
        print(f"ERROR: Validation failed: {e}", file=sys.stderr)
        print(f"  Variable: {dep_var}", file=sys.stderr)
        print(f"  Controls: {controls}", file=sys.stderr)
        sys.exit(1)

    # Estimate model
    start_time = datetime.now()

    try:
        model = smf.ols(formula, data=df_reg).fit(cov_type="HC1")
    except ValueError as e:
        print(f"ERROR: Regression failed: {e}", file=sys.stderr)
        print(f"  Formula: {formula}", file=sys.stderr)
        print(f"  Observations: {len(df_reg)}", file=sys.stderr)
        sys.exit(1)

    duration = (datetime.now() - start_time).total_seconds()

    print(f"    [OK] R²={model.rsquared:.4f}, N={int(model.nobs):,}, {duration:.1f}s")

    return model, df_reg, valid_ceos


# ==============================================================================
# Extract CEO Fixed Effects
# ==============================================================================


def extract_ceo_fixed_effects(model, df_reg, model_name, sample_name):
    """Extract gamma_i coefficients and compute Tone scores."""

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
    reference_ceos = [c for c in all_ceos if c not in ceo_effects]
    for ref_ceo in reference_ceos:
        ceo_effects[ref_ceo] = 0.0

    # Create DataFrame
    ceo_fe = pd.DataFrame(list(ceo_effects.items()), columns=["ceo_id", "gamma_i"])

    # For Tone, high gamma_i = more positive = high Tone (no negation needed)
    ceo_fe["Tone_raw"] = ceo_fe["gamma_i"]

    # Standardize
    mean_val = ceo_fe["Tone_raw"].mean()
    std_val = ceo_fe["Tone_raw"].std()
    ceo_fe[model_name] = (ceo_fe["Tone_raw"] - mean_val) / std_val

    ceo_fe["model"] = model_name
    ceo_fe["sample"] = sample_name

    return ceo_fe


# ==============================================================================
# Compute CEO-Level Statistics
# ==============================================================================


def compute_ceo_stats(df_sample_filtered, ceo_fe, model_spec, sample_name):
    """Compute descriptive statistics per CEO."""
    dep_var = model_spec["dependent_var"]

    # Vectorized GroupBy aggregation
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

    # Flatten column names
    ceo_stats.columns = [
        "ceo_id",
        "n_calls",
        "avg_tone",
        "std_tone",
        "ceo_name",
        "first_call_date",
        "last_call_date",
        "n_firms",
    ]

    # Convert ceo_id to string
    ceo_stats["ceo_id"] = ceo_stats["ceo_id"].astype(str)

    # Merge with fixed effects
    ceo_scores = ceo_fe.merge(ceo_stats, on="ceo_id", how="left")

    # Sort by Tone (descending = most positive first)
    tone_col = [c for c in ceo_fe.columns if c.startswith("Tone") and c != "Tone_raw"][
        0
    ]
    ceo_scores = ceo_scores.sort_values(tone_col, ascending=False).reset_index(
        drop=True
    )

    return ceo_scores


# ==============================================================================
# Model Diagnostics
# ==============================================================================


def compute_diagnostics(model, model_name, sample_name, n_ceos, n_firms):
    """Compute model diagnostics."""
    return {
        "model": model_name,
        "sample": sample_name,
        "n_observations": int(model.nobs),
        "n_ceos": n_ceos,
        "n_firms": n_firms,
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

    # CEO Tone Scores
    ceo_scores_df = pd.concat(all_ceo_scores, ignore_index=True)
    ceo_scores_path = out_dir / "ceo_tone_scores.parquet"
    ceo_scores_df.to_parquet(ceo_scores_path, index=False)
    print(f"  Saved: ceo_tone_scores.parquet ({len(ceo_scores_df):,} rows)")

    # Regression results (per model/sample)
    for (model_name, sample_name), model in all_models.items():
        if model is not None:
            results_path = (
                out_dir
                / f"regression_results_{model_name.lower()}_{sample_name.lower()}.txt"
            )
            with open(results_path, "w") as f:
                f.write(model.summary().as_text())
            print(
                f"  Saved: regression_results_{model_name.lower()}_{sample_name.lower()}.txt"
            )

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
    """Generate markdown report."""
    print("\n  Generating report...")

    report_lines = [
        "# Step 4.1.4: CEO Tone Regression Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Model Summary",
        "",
        "| Model | Sample | CEOs | Calls | R² |",
        "|-------|--------|------|-------|-----|",
    ]

    for diag in all_diagnostics:
        report_lines.append(
            f"| {diag['model']} | {diag['sample']} | {diag['n_ceos']:,} | {diag['n_observations']:,} | {diag['r_squared']:.4f} |"
        )

    report_lines.append("")
    report_lines.append("## Interpretation")
    report_lines.append("")
    report_lines.append("- **ToneAll:** CEO fixed effect on all manager tone")
    report_lines.append("- **ToneCEO:** CEO fixed effect on CEO's own tone")
    report_lines.append(
        "- **ToneRegime:** CEO fixed effect on non-CEO manager tone (spillover)"
    )
    report_lines.append("")
    report_lines.append("High Tone = More positive/optimistic communication style")

    # Write report
    report_path = out_dir / "report_step4_1_4.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: report_step4_1_4.md")


# ==============================================================================
# Main
# ==============================================================================


def main(year_start=None, year_end=None):
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Override config if provided
    if year_start:
        CONFIG["year_start"] = year_start
    if year_end:
        CONFIG["year_end"] = year_end

    # Setup paths
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "4_Outputs" / "4.1.4_CeoTone" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "3_Logs" / "4.1.4_CeoTone" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Setup dual logging
    log_path = log_dir / f"step4_1_4_{timestamp}.log"
    dual_writer = DualWriter(log_path)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.1.4: CEO Tone (Net Sentiment) Regression")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {CONFIG['year_start']}-{CONFIG['year_end']}")

    # Initialize stats dict for observability
    stats = {
        "step_id": "4.1.4_EstimateCeoTone",
        "timestamp": timestamp,
        "timing": {"start_iso": start_time.isoformat(), "end_iso": "", "duration_seconds": 0},
        "missing_values": {},
        "regressions": {},
    }

    # Load data
    df = load_all_data(root, CONFIG["year_start"], CONFIG["year_end"])

    # Compute NetTone variables
    df = compute_net_tone(df)

    # Run all three models for each sample
    all_ceo_scores = []
    all_diagnostics = []
    all_models = {}

    for model_name, model_spec in MODEL_SPECS.items():
        print("\n" + "=" * 60)
        print(f"MODEL: {model_name} - {model_spec['description']}")
        print("=" * 60)

        # Prepare data for this model
        df_model = prepare_regression_data(df.copy(), model_spec)
        print(f"  Complete cases: {len(df_model):,}")

        for sample_name in ["Main", "Finance", "Utility"]:
            df_sample = df_model[df_model["sample"] == sample_name].copy()

            if len(df_sample) < 100:
                print(
                    f"\n  [{model_name} - {sample_name}] Skipping: too few observations"
                )
                continue

            # Run regression
            model, df_reg, valid_ceos = run_regression(
                df_sample, model_name, model_spec, sample_name
            )

            if model is None:
                continue

            all_models[(model_name, sample_name)] = model

            # Extract CEO fixed effects
            ceo_fe = extract_ceo_fixed_effects(model, df_reg, model_name, sample_name)

            # Filter original sample to valid CEOs for stats
            df_sample_filtered = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

            # Compute CEO stats
            ceo_scores = compute_ceo_stats(
                df_sample_filtered, ceo_fe, model_spec, sample_name
            )
            all_ceo_scores.append(ceo_scores)

            # Compute diagnostics
            diag = compute_diagnostics(
                model,
                model_name,
                sample_name,
                len(valid_ceos),
                df_sample_filtered["gvkey"].nunique(),
            )
            all_diagnostics.append(diag)

    # Save outputs
    if all_ceo_scores:
        save_outputs(all_ceo_scores, all_diagnostics, all_models, out_dir)

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

    # Print R² comparison
    if all_diagnostics:
        print("\nR² Comparison (Main Sample):")
        for diag in all_diagnostics:
            if diag["sample"] == "Main":
                print(
                    f"  {diag['model']}: {diag['r_squared']:.4f} ({diag['n_ceos']:,} CEOs)"
                )

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
    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        # validate_prerequisites already prints "[OK] All prerequisites validated"
        sys.exit(0)

    check_prerequisites(root)
    sys.exit(main())
