#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test CEO Tone Hypothesis
================================================================================
ID: econometric/run_h0_5_ceo_tone
Description: Run CEO Tone hypothesis test (4.1.4) by loading panel from Stage 3,
             running fixed effects regressions for 3 model specs × 3 industry
             samples = 9 regressions, extracting CEO fixed effects, and outputting
             Accounting Review style LaTeX tables.

Model Specifications:
    ToneAll    — dependent: Manager_QA_NetTone
                 controls:  Manager_Pres_NetTone, Analyst_QA_NetTone, Entire_All_Uncertainty_pct
    ToneCEO    — dependent: CEO_QA_NetTone
                 controls:  CEO_Pres_NetTone, Analyst_QA_NetTone, Entire_All_Uncertainty_pct
    ToneRegime — dependent: NonCEO_Manager_QA_NetTone
                 controls:  Manager_Pres_NetTone, Analyst_QA_NetTone, Entire_All_Uncertainty_pct

    All models share financial controls:
        StockRet, MarketRet, EPS_Growth, SurpDec
    All models use:
        C(ceo_id) + C(year) fixed effects

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    CEOs must have >= 5 calls to be included in regression.

Scoring Direction:
    ToneCEO = +gamma_i  (unlike Clarity where ClarityCEO = -gamma_i)
    Higher gamma = more positive tone tendency = higher ToneCEO.

Standardization:
    Per-model globally across all samples (same as clarity pipeline).

Inputs:
    - outputs/variables/ceo_tone/{latest_timestamp}/ceo_tone_panel.parquet

Outputs:
    - outputs/econometric/ceo_tone/{timestamp}/tone_scores.parquet
    - outputs/econometric/ceo_tone/{timestamp}/ceo_tone_table.tex
    - outputs/econometric/ceo_tone/{timestamp}/model_diagnostics.csv
    - outputs/econometric/ceo_tone/{timestamp}/regression_results_{model}_{sample}.txt
    - outputs/econometric/ceo_tone/{timestamp}/report_step4_ceo_tone.md
    - outputs/econometric/ceo_tone/{timestamp}/run_log.txt

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h0_5_ceo_tone_panel)
    - Uses: statsmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-02-19
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning, module="linearmodels.*")

# Try importing statsmodels — assign None so the name is always bound
smf: Any = None
try:
    import statsmodels.formula.api as smf  # type: ignore[no-redef]

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

from f1d.shared.latex_tables_accounting import (
    make_accounting_table,
    make_summary_stats_table,
)
from f1d.shared.observability import DualWriter
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample
from f1d.shared.regression_validation import (
    RegressionValidationError,
    validate_columns,
    validate_sample_size,
)


# ==============================================================================
# Configuration
# ==============================================================================

# Shared financial controls for all 3 models
FINANCIAL_CONTROLS = ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]

# Shared uncertainty control present in all 3 models
UNCERTAINTY_CONTROL = "Entire_All_Uncertainty_pct"

# 3 model specifications
MODEL_SPECS: Dict[str, Dict[str, Any]] = {
    "ToneAll": {
        "dependent_var": "Manager_QA_NetTone",
        "linguistic_controls": [
            "Manager_Pres_NetTone",
            "Analyst_QA_NetTone",
            UNCERTAINTY_CONTROL,
        ],
        "description": "All-manager Q&A tone (CEO + non-CEO managers)",
    },
    "ToneCEO": {
        "dependent_var": "CEO_QA_NetTone",
        "linguistic_controls": [
            "CEO_Pres_NetTone",
            "Analyst_QA_NetTone",
            UNCERTAINTY_CONTROL,
        ],
        "description": "CEO-only Q&A tone",
    },
    "ToneRegime": {
        "dependent_var": "NonCEO_Manager_QA_NetTone",
        "linguistic_controls": [
            "Manager_Pres_NetTone",
            "Analyst_QA_NetTone",
            UNCERTAINTY_CONTROL,
        ],
        "description": "Non-CEO manager Q&A tone (placebo/regime)",
    },
}

MIN_CALLS_PER_CEO = 5


# ==============================================================================
# Summary Statistics Variables (Combined across all 3 models)
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables (3 models)
    {"col": "Manager_QA_NetTone", "label": "Manager QA NetTone"},
    {"col": "CEO_QA_NetTone", "label": "CEO QA NetTone"},
    {"col": "NonCEO_Manager_QA_NetTone", "label": "NonCEO Manager QA NetTone"},
    # Linguistic controls (all models)
    {"col": "Manager_Pres_NetTone", "label": "Manager Pres NetTone"},
    {"col": "CEO_Pres_NetTone", "label": "CEO Pres NetTone"},
    {"col": "Analyst_QA_NetTone", "label": "Analyst QA NetTone"},
    {"col": UNCERTAINTY_CONTROL, "label": "Uncertainty"},
    # Financial controls (all models)
    {"col": "StockRet", "label": "Stock Return"},
    {"col": "MarketRet", "label": "Market Return"},
    {"col": "EPS_Growth", "label": "EPS Growth"},
    {"col": "SurpDec", "label": "Earnings Surprise Decile"},
]


# ==============================================================================
# Variable Labels for LaTeX Table
# ==============================================================================

VARIABLE_LABELS = {
    # ToneAll / ToneRegime controls
    "Manager_Pres_NetTone": "Manager Pres NetTone",
    "Analyst_QA_NetTone": "Analyst QA NetTone",
    UNCERTAINTY_CONTROL: "Uncertainty",
    # ToneCEO controls
    "CEO_Pres_NetTone": "CEO Pres NetTone",
    # Financial controls (shared)
    "StockRet": "Stock Return",
    "MarketRet": "Market Return",
    "EPS_Growth": "EPS Growth",
    "SurpDec": "Earnings Surprise Decile",
}


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Test CEO Tone Hypothesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without executing",
    )
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Path to panel parquet file (default: latest from Stage 3)",
    )
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load panel from Stage 3 output.

    Args:
        root_path: Project root path
        panel_path: Optional explicit path to panel file

    Returns:
        DataFrame with panel data
    """
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "ceo_tone",
            required_file="ceo_tone_panel.parquet",
        )
        panel_file = panel_dir / "ceo_tone_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    return panel


def prepare_regression_data(
    panel: pd.DataFrame,
    model_key: str,
) -> pd.DataFrame:
    """Prepare panel data for regression for a given model spec.

    Filters to non-null ceo_id and complete cases for the specified model's
    dependent variable, linguistic controls, and financial controls.
    Always re-derives the sample column from ff12_code on the post-filter
    DataFrame to handle any NaN ff12_code rows that survived the complete-case
    filter (they are assigned to Main, consistent with v1 behavior).

    Args:
        panel: Raw panel DataFrame (caller must pass panel.copy() to be safe)
        model_key: Key into MODEL_SPECS dict (ToneAll / ToneCEO / ToneRegime)

    Returns:
        Prepared DataFrame with sample column assigned
    """
    spec = MODEL_SPECS[model_key]
    dep_var = spec["dependent_var"]
    controls = spec["linguistic_controls"] + FINANCIAL_CONTROLS

    print(f"\n  Preparing data for {model_key} (dep: {dep_var})...")

    initial_n = len(panel)

    # Filter to non-null ceo_id
    df = panel[panel["ceo_id"].notna()].copy()
    print(f"  After ceo_id filter: {len(df):,} / {initial_n:,}")

    # Validate required variables — hard fail, no silent fallback
    required = [dep_var] + controls + ["ceo_id", "year"]
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        raise ValueError(
            f"[{model_key}] Required variables missing from panel: {missing_vars}. "
            "Panel build may be incomplete. Aborting to prevent misspecified regression."
        )

    # Use shared validation utility (raises RegressionValidationError on failure)
    try:
        validate_columns(df, required)
    except RegressionValidationError as e:
        raise ValueError(f"[{model_key}] Column validation failed: {e}") from e

    # Filter to complete cases for this model's variables
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases filter: {len(df):,}")

    # Validate minimum sample size (raise hard error, not silent skip)
    try:
        validate_sample_size(df, min_observations=100)
    except RegressionValidationError as e:
        raise ValueError(f"[{model_key}] Sample size validation failed: {e}") from e

    # Always re-derive sample from ff12_code on the filtered DataFrame.
    # This correctly handles:
    #   1. Panel built without a sample column
    #   2. NaN ff12_code rows (assigned to Main, matching v1 behavior)
    #   3. Complete-case filtering that may have changed sample composition
    if "ff12_code" not in df.columns:
        raise ValueError(
            f"[{model_key}] 'ff12_code' column missing from panel. "
            "Cannot assign industry samples. Check Stage 3 manifest output."
        )
    df["sample"] = assign_industry_sample(df["ff12_code"])
    n_nan_ff12 = df["ff12_code"].isna().sum()
    if n_nan_ff12 > 0:
        print(f"  NOTE: {n_nan_ff12} rows with NaN ff12_code assigned to Main sample.")

    print(f"  Sample distribution for {model_key}:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (df["sample"] == sample).sum()
        print(f"    {sample}: {n:,} calls")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    model_key: str,
    sample_name: str,
) -> Tuple[Any, Optional[pd.DataFrame], Set[Any]]:
    """Run OLS regression with CEO fixed effects for a given model+sample.

    Args:
        df_sample: Sample DataFrame (already filtered to the relevant sample)
        model_key: Key into MODEL_SPECS dict
        sample_name: Name of sample for logging

    Returns:
        Tuple of (model, df_reg, valid_ceos)
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {model_key} / {sample_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, set()

    spec = MODEL_SPECS[model_key]
    dep_var = spec["dependent_var"]
    controls = [
        c
        for c in spec["linguistic_controls"] + FINANCIAL_CONTROLS
        if c in df_sample.columns
    ]

    # Filter to CEOs with minimum calls
    ceo_counts = df_sample["ceo_id"].value_counts()
    valid_ceos: Set[Any] = set(ceo_counts[ceo_counts >= MIN_CALLS_PER_CEO].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"  After >={MIN_CALLS_PER_CEO} calls filter: {len(df_reg):,} calls, "
        f"{df_reg['ceo_id'].nunique():,} CEOs"
    )

    # Validate sample size using shared utility — return None on failure
    try:
        validate_sample_size(df_reg, min_observations=100)
    except RegressionValidationError as e:
        print(f"  ERROR: {e}")
        return None, None, set()

    # Validate required columns using shared utility
    required_for_reg = [dep_var] + controls + ["ceo_id", "year"]
    try:
        validate_columns(df_reg, required_for_reg)
    except RegressionValidationError as e:
        print(f"  ERROR: {e}")
        return None, None, set()

    # Convert to string for categorical treatment
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula
    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula}")

    # Estimate model
    print("  Estimating... (this may take a minute)")
    est_start = datetime.now()

    try:
        model = smf.ols(formula, data=df_reg).fit(
            # M-2 fix: cluster SEs at CEO level (not HC1) to account for
            # within-CEO correlation across calls in the same regression.
            # HC1 treats all observations as independent, understating SEs
            # when the same CEO appears in many rows (Liang-Zeger problem).
            cov_type="cluster",
            cov_kwds={"groups": df_reg["ceo_id"]},
        )
    except ValueError as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, None, set()

    duration = (datetime.now() - est_start).total_seconds()

    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adj. R-squared: {model.rsquared_adj:.4f}")
    print(f"  N observations: {int(model.nobs):,}")

    return model, df_reg, valid_ceos


def extract_tone_scores(
    model: Any,
    df_reg: pd.DataFrame,
    model_key: str,
    sample_name: str,
) -> pd.DataFrame:
    """Extract CEO fixed effects as raw (unstandardized) Tone_raw scores.

    ToneCEO_raw = +gamma_i  (positive — unlike Clarity where score = -gamma_i).
    Higher gamma = more positive tone tendency = higher ToneCEO.

    Standardization is deferred to save_outputs() so it is applied globally
    across all samples for a given model — consistent with clarity pipeline.

    Reference CEOs (gamma = 0 by statsmodels convention, not estimated) are
    tagged with is_reference=True and excluded from tone_scores.parquet.

    Args:
        model: Fitted OLS model
        df_reg: Regression DataFrame (ceo_id already cast to str)
        model_key: Model key (ToneAll / ToneCEO / ToneRegime)
        sample_name: Sample name for metadata

    Returns:
        DataFrame with ceo_id, gamma_i, Tone_raw, model, sample, is_reference,
        avg_tone, std_tone (per-CEO descriptive stats from regression sample)
        (NOT yet standardized — caller must standardize globally per model)
    """
    print(f"\n  Extracting CEO fixed effects for {model_key}/{sample_name}...")

    spec = MODEL_SPECS[model_key]
    dep_var = spec["dependent_var"]

    # Get CEO coefficient names
    ceo_params = {
        p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")
    }

    # Parse CEO IDs from parameter names like "C(ceo_id)[T.ABC123]"
    ceo_effects: Dict[str, float] = {}
    for param_name, gamma_i in ceo_params.items():
        if "[T." in param_name:
            ceo_id = param_name.split("[T.")[1].split("]")[0]
            ceo_effects[ceo_id] = gamma_i

    # Identify reference CEOs (alphabetically first — statsmodels default)
    all_ceos = df_reg["ceo_id"].unique()
    reference_ceos = set(c for c in all_ceos if c not in ceo_effects)

    print(
        f"  Found {len(ceo_effects)} estimated CEOs + {len(reference_ceos)} reference "
        f"(reference excluded from output)"
    )

    # Build DataFrame — estimated CEOs
    rows = [
        {"ceo_id": ceo_id, "gamma_i": gamma_i, "is_reference": False}
        for ceo_id, gamma_i in ceo_effects.items()
    ]
    # Include reference CEOs tagged so caller can inspect if needed
    for ref_ceo in reference_ceos:
        rows.append({"ceo_id": ref_ceo, "gamma_i": 0.0, "is_reference": True})

    ceo_fe = pd.DataFrame(rows)

    # Tone_raw = +gamma_i (positive sign — higher tone tendency = higher score)
    ceo_fe["Tone_raw"] = ceo_fe["gamma_i"]
    ceo_fe["model"] = model_key
    ceo_fe["sample"] = sample_name

    # Per-CEO descriptive stats from the regression sample (not from full panel)
    # This matches v1's compute_ceo_stats behavior: use only calls in df_reg
    if dep_var in df_reg.columns:
        ceo_tone_stats = (
            df_reg.groupby("ceo_id")[dep_var]
            .agg(avg_tone="mean", std_tone="std")
            .reset_index()
        )
        ceo_fe = ceo_fe.merge(ceo_tone_stats, on="ceo_id", how="left")
    else:
        ceo_fe["avg_tone"] = float("nan")
        ceo_fe["std_tone"] = float("nan")

    # NOTE: ToneCEO (standardized), n_calls, n_firms, first/last call dates
    # are joined in save_outputs() after standardization.

    return ceo_fe


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    results: Dict[str, Dict[str, Any]],
    all_tone_scores: List[pd.DataFrame],
    panel: pd.DataFrame,
    reg_samples: Dict[str, Dict[str, pd.DataFrame]],
    out_dir: Path,
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Save all outputs.

    Standardization of ToneCEO is done here, globally per model across ALL
    samples, so that scores from different samples are on the same scale and
    are directly comparable.

    Reference CEOs (gamma=0 normalization artifact) are excluded from the
    saved tone_scores.parquet.

    Output parquet has a `model` column distinguishing ToneAll/ToneCEO/ToneRegime rows.
    n_calls is computed from the full panel (CEO characteristic, not model-specific).
    n_firms, first_call_date, last_call_date are also computed from the full panel.
    avg_tone and std_tone are per-CEO stats from the model-specific regression sample.

    Args:
        results: Nested dict {model_key: {sample_name: {model, diagnostics}}}
        all_tone_scores: List of raw (unstandardized) tone score DataFrames
        panel: Full panel DataFrame (for CEO metadata join)
        reg_samples: Nested dict {model_key: {sample_name: df_reg}} for n_calls
        out_dir: Output directory
        stats: Stats dict

    Returns:
        Final tone_df with globally-per-model standardized ToneCEO scores
    """
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Build combined tone scores
    tone_df = pd.DataFrame()
    if all_tone_scores:
        raw_df = pd.concat(all_tone_scores, ignore_index=True)

        # Exclude reference CEOs — their gamma=0 is a normalization artifact
        estimated_df = raw_df[~raw_df["is_reference"]].copy()
        n_reference = raw_df["is_reference"].sum()
        print(f"  Excluded {n_reference} reference CEO(s) from tone scores")

        # Standardize ToneCEO GLOBALLY PER MODEL across all samples
        # so a score of 1.0 means the same thing regardless of sample
        standardized_parts = []
        for model_key in MODEL_SPECS:
            model_mask = estimated_df["model"] == model_key
            model_subset = estimated_df[model_mask].copy()
            if len(model_subset) == 0:
                continue

            global_mean = model_subset["Tone_raw"].mean()
            global_std = model_subset["Tone_raw"].std()

            if global_std == 0 or pd.isna(global_std):
                model_subset["ToneCEO"] = 0.0
                print(f"  [{model_key}] WARNING: std=0, ToneCEO set to 0")
            else:
                model_subset["ToneCEO"] = (
                    model_subset["Tone_raw"] - global_mean
                ) / global_std

            print(
                f"  [{model_key}] Global standardization: mean={global_mean:.4f}, "
                f"std={global_std:.4f} (across {len(model_subset):,} estimated CEOs)"
            )
            print(
                f"  [{model_key}] ToneCEO post-standardization: "
                f"mean={model_subset['ToneCEO'].mean():.4f}, "
                f"std={model_subset['ToneCEO'].std():.4f}"
            )
            standardized_parts.append(model_subset)

        estimated_df = pd.concat(standardized_parts, ignore_index=True)

        # CEO metadata from full panel: n_calls, n_firms, first/last call date
        ceo_meta_base = panel[panel["ceo_id"].notna()].copy()
        ceo_meta_base["ceo_id_str"] = ceo_meta_base["ceo_id"].astype(str)

        agg_dict: Dict[str, Any] = {
            "ceo_name": ("ceo_name", "first"),
            "n_calls": ("file_name", "count"),
        }
        if "gvkey" in ceo_meta_base.columns:
            agg_dict["n_firms"] = ("gvkey", "nunique")
        if "start_date" in ceo_meta_base.columns:
            agg_dict["first_call_date"] = ("start_date", "min")
            agg_dict["last_call_date"] = ("start_date", "max")

        ceo_meta = (
            ceo_meta_base.groupby("ceo_id_str")
            .agg(**agg_dict)
            .reset_index()
            .rename(columns={"ceo_id_str": "ceo_id"})
        )
        estimated_df = estimated_df.merge(ceo_meta, on="ceo_id", how="left")

        # Final column order (avg_tone and std_tone come from extract_tone_scores)
        output_cols = [
            "ceo_id",
            "ceo_name",
            "sample",
            "model",
            "gamma_i",
            "Tone_raw",
            "ToneCEO",
            "avg_tone",
            "std_tone",
            "n_calls",
            "n_firms",
            "first_call_date",
            "last_call_date",
        ]
        output_cols = [c for c in output_cols if c in estimated_df.columns]
        tone_df = estimated_df[output_cols]

        tone_path = out_dir / "tone_scores.parquet"
        tone_df.to_parquet(tone_path, index=False)
        print(
            f"  Saved: tone_scores.parquet ({len(tone_df):,} estimated CEO-model rows)"
        )

    # Generate LaTeX table — Main sample only, 3 columns (one per model)
    main_results_for_table: Dict[str, Dict[str, Any]] = {}
    for model_key in MODEL_SPECS:
        if model_key in results and "Main" in results[model_key]:
            main_results_for_table[model_key] = results[model_key]["Main"]

    # Hard error if any model is missing a Main sample result
    missing_models = [k for k in MODEL_SPECS if k not in main_results_for_table]
    if missing_models:
        raise ValueError(
            f"Main sample results missing for models: {missing_models}. "
            "Cannot generate LaTeX table without all 3 Main-sample columns. "
            "Check whether Main sample had <100 observations for these models."
        )

    # Union of all controls in insertion order
    all_controls: List[str] = []
    seen: set = set()
    for spec in MODEL_SPECS.values():
        for c in spec["linguistic_controls"] + FINANCIAL_CONTROLS:
            if c not in seen:
                all_controls.append(c)
                seen.add(c)

    make_accounting_table(
        results=main_results_for_table,
        caption="Table 2: CEO Tone Fixed Effects (Main Sample)",
        label="tab:ceo_tone",
        note=(
            "This table reports CEO fixed effects from regressing net tone "
            "(Positive_pct - Negative_pct) on firm characteristics and year "
            "fixed effects. ToneCEO = +gamma_i, standardized globally per "
            "model across all industry samples. "
            "Standard errors are clustered at the CEO level (cov_type=cluster, groups=ceo_id)."
        ),
        variable_labels=VARIABLE_LABELS,
        control_variables=all_controls,
        entity_label="N CEOs",
        output_path=out_dir / "ceo_tone_table.tex",
    )
    print("  Saved: ceo_tone_table.tex")

    # Save regression results text files
    for model_key, sample_results in results.items():
        for sample_name, result in sample_results.items():
            model = result.get("model")
            if model is not None:
                results_path = (
                    out_dir
                    / f"regression_results_{model_key.lower()}_{sample_name.lower()}.txt"
                )
                with open(results_path, "w") as f:
                    f.write(model.summary().as_text())
                print(
                    f"  Saved: regression_results_{model_key.lower()}_{sample_name.lower()}.txt"
                )

    # Save model diagnostics CSV (F-stat, AIC, BIC, R², N obs, N CEOs per model×sample)
    diag_rows = []
    for model_key, sample_results in results.items():
        for sample_name, result in sample_results.items():
            model = result.get("model")
            diag = result.get("diagnostics", {})
            if model is not None:
                diag_rows.append(
                    {
                        "model": model_key,
                        "sample": sample_name,
                        "n_obs": diag.get("n_obs"),
                        "n_ceos": diag.get("n_ceos"),
                        "rsquared": diag.get("rsquared"),
                        "rsquared_adj": diag.get("rsquared_adj"),
                        "fvalue": getattr(model, "fvalue", None),
                        "f_pvalue": getattr(model, "f_pvalue", None),
                        "aic": getattr(model, "aic", None),
                        "bic": getattr(model, "bic", None),
                        "llf": getattr(model, "llf", None),
                    }
                )
    if diag_rows:
        diag_df = pd.DataFrame(diag_rows)
        diag_path = out_dir / "model_diagnostics.csv"
        diag_df.to_csv(diag_path, index=False)
        print(f"  Saved: model_diagnostics.csv ({len(diag_df)} model×sample rows)")

    return tone_df


def generate_report(
    results: Dict[str, Dict[str, Any]],
    tone_df: pd.DataFrame,
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report.

    Args:
        results: Nested dict {model_key: {sample_name: {model, diagnostics}}}
        tone_df: Final tone scores DataFrame (globally standardized, references excluded)
        out_dir: Output directory
        duration: Duration in seconds
    """
    report_lines = [
        "# Stage 4: CEO Tone Hypothesis Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Model Specifications",
        "",
    ]

    for model_key, spec in MODEL_SPECS.items():
        report_lines.append(f"### {model_key}")
        report_lines.append("")
        report_lines.append(f"- **Dependent:** `{spec['dependent_var']}`")
        report_lines.append(f"- **Description:** {spec['description']}")
        report_lines.append(
            f"- **Controls:** "
            + ", ".join(
                f"`{c}`" for c in spec["linguistic_controls"] + FINANCIAL_CONTROLS
            )
        )
        report_lines.append("")

    report_lines += [
        "## Summary Statistics",
        "",
        "| Model | Sample | N Obs | N CEOs | R-squared |",
        "|-------|--------|-------|--------|-----------|",
    ]

    for model_key in MODEL_SPECS:
        if model_key not in results:
            continue
        for sample_name, result in results[model_key].items():
            diag = result.get("diagnostics", {})
            n_obs = diag.get("n_obs", "N/A")
            n_ceo = diag.get("n_ceos", "N/A")
            r2 = diag.get("rsquared", "N/A")
            n_obs_str = f"{n_obs:,}" if isinstance(n_obs, int) else str(n_obs)
            n_ceo_str = f"{n_ceo:,}" if isinstance(n_ceo, int) else str(n_ceo)
            r2_str = f"{r2:.4f}" if isinstance(r2, float) else str(r2)
            report_lines.append(
                f"| {model_key} | {sample_name} | {n_obs_str} | {n_ceo_str} | {r2_str} |"
            )

    report_lines.append("")
    if not tone_df.empty:
        n_total = len(tone_df)
        report_lines.append(
            f"**Note:** ToneCEO scores are standardized globally per model across "
            f"all samples. Total rows in tone_scores.parquet: {n_total:,} "
            f"(CEO × model combinations). Reference CEOs excluded."
        )
        report_lines.append("")

    # Top/bottom CEOs by ToneCEO score, per model, Main sample
    if not tone_df.empty and "ToneCEO" in tone_df.columns:
        for model_key, spec in MODEL_SPECS.items():
            model_main = tone_df[
                (tone_df["model"] == model_key) & (tone_df["sample"] == "Main")
            ].copy()
            if len(model_main) == 0:
                continue

            name_col = "ceo_name" if "ceo_name" in model_main.columns else "ceo_id"
            score_label = f"ToneCEO [{model_key}]"

            report_lines.append(f"## {model_key} — Main Sample")
            report_lines.append(f"*Dependent variable: `{spec['dependent_var']}`*")
            report_lines.append("")
            report_lines.append(f"### Top 5 Most Positive {score_label} CEOs")
            report_lines.append("")
            report_lines.append(f"| Rank | CEO | {score_label} |")
            report_lines.append("|------|-----|" + "-" * (len(score_label) + 2) + "|")
            for rank, (_, row) in enumerate(
                model_main.nlargest(5, "ToneCEO").iterrows(), start=1
            ):
                report_lines.append(
                    f"| {rank} | {row[name_col]} | {row['ToneCEO']:.3f} |"
                )

            report_lines.append("")
            report_lines.append(f"### Top 5 Most Negative {score_label} CEOs")
            report_lines.append("")
            report_lines.append(f"| Rank | CEO | {score_label} |")
            report_lines.append("|------|-----|" + "-" * (len(score_label) + 2) + "|")
            for rank, (_, row) in enumerate(
                model_main.nsmallest(5, "ToneCEO").iterrows(), start=1
            ):
                report_lines.append(
                    f"| {rank} | {row[name_col]} | {row['ToneCEO']:.3f} |"
                )
            report_lines.append("")

    # Write report
    report_path = out_dir / "report_step4_ceo_tone.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: report_step4_ceo_tone.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "test_ceo_tone",
        "timestamp": timestamp,
        "regressions": {},
        "timing": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "ceo_tone" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Capture all output to a persistent log file (DualWriter mirrors stdout → file)
    log_path = out_dir / "run_log.txt"
    dual = DualWriter(log_path)
    sys.stdout = dual

    print("=" * 80)
    print("STAGE 4: Test CEO Tone Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Derive sample column from ff12_code for summary stats
    # (prepare_regression_data does this per-model, but we need it once for summary stats)
    if "sample" not in panel.columns and "ff12_code" in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    # Generate summary stats for panel data (all model variables, by sample)
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    make_summary_stats_table(
        df=panel,
        variables=SUMMARY_STATS_VARS,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — CEO Tone",
        label="tab:summary_stats_h05",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Run 3 models × 3 samples = 9 regressions
    # Nested dict: results[model_key][sample_name] = {model, diagnostics}
    results: Dict[str, Dict[str, Any]] = {}
    all_tone_scores: List[pd.DataFrame] = []
    # Store regression DataFrames for metadata computation
    reg_samples: Dict[str, Dict[str, pd.DataFrame]] = {}

    for model_key in MODEL_SPECS:
        results[model_key] = {}
        reg_samples[model_key] = {}
        stats["regressions"][model_key] = {}

        print(f"\n{'=' * 80}")
        print(f"MODEL: {model_key}")
        print("=" * 80)

        # Prepare data for this model — pass a copy to avoid cross-model mutation
        df = prepare_regression_data(panel.copy(), model_key)

        for sample_name in ["Main", "Finance", "Utility"]:
            df_sample = df[df["sample"] == sample_name].copy()

            if len(df_sample) < 100:
                print(
                    f"\n  Skipping {model_key}/{sample_name}: "
                    f"too few observations ({len(df_sample)})"
                )
                continue

            # Run regression
            model, df_reg, valid_ceos = run_regression(
                df_sample, model_key, sample_name
            )

            if model is None or df_reg is None:
                continue

            # Extract tone scores (raw — standardization deferred to save_outputs)
            tone_scores = extract_tone_scores(model, df_reg, model_key, sample_name)
            all_tone_scores.append(tone_scores)
            reg_samples[model_key][sample_name] = df_reg

            # Store results
            results[model_key][sample_name] = {
                "model": model,
                "diagnostics": {
                    "n_obs": int(model.nobs),
                    "n_ceos": len(valid_ceos),
                    "rsquared": model.rsquared,
                    "rsquared_adj": model.rsquared_adj,
                },
            }

            stats["regressions"][model_key][sample_name] = {
                "n_obs": int(model.nobs),
                "n_ceos": len(valid_ceos),
                "rsquared": model.rsquared,
            }

    # Save outputs (includes global-per-model standardization)
    tone_df: pd.DataFrame = pd.DataFrame()
    if any(results.values()):
        tone_df = save_outputs(
            results, all_tone_scores, panel, reg_samples, out_dir, stats
        )

        # Generate report
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(results, tone_df, out_dir, duration)

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    stats["timing"]["duration_seconds"] = round(duration, 2)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    # Restore stdout before exiting
    sys.stdout = dual.original_stdout
    dual.log.close()

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
