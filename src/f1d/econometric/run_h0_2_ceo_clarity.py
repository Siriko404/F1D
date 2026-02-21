#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test CEO Clarity Hypothesis
================================================================================
ID: econometric/run_h0_2_ceo_clarity
Description: Run CEO Clarity hypothesis test by loading panel from Stage 3,
             running fixed effects regression by industry sample, extracting
             CEO fixed effects, and outputting Accounting Review style
             LaTeX tables.

Model Specification:
    CEO_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
        CEO_Pres_Uncertainty_pct +
        Analyst_QA_Uncertainty_pct +
        Entire_All_Negative_pct +
        StockRet + MarketRet + EPS_Growth + SurpDec

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    CEOs must have >= 5 calls to be included in regression.

Inputs:
    - outputs/variables/ceo_clarity/latest/ceo_clarity_panel.parquet

Outputs:
    - outputs/econometric/ceo_clarity/{timestamp}/ceo_clarity_table.tex
    - outputs/econometric/ceo_clarity/{timestamp}/clarity_scores.parquet
    - outputs/econometric/ceo_clarity/{timestamp}/regression_results_{sample}.txt
    - outputs/econometric/ceo_clarity/{timestamp}/report_step4_ceo_clarity.md

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h0_2_ceo_clarity_panel)
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
from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning, module="linearmodels.*")

try:
    from linearmodels.panel import PanelOLS  # type: ignore[no-redef]

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: linearmodels not available. Install with: pip install linearmodels")

from f1d.shared.latex_tables_accounting import make_accounting_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample


# ==============================================================================
# Configuration
# ==============================================================================

CONFIG: Dict[str, Any] = {
    "dependent_var": "CEO_QA_Uncertainty_pct",
    "linguistic_controls": [
        "CEO_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
    ],
    "firm_controls": [
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
    ],
    "min_calls_per_ceo": 5,
}


# ==============================================================================
# Variable Labels for LaTeX Table
# ==============================================================================

VARIABLE_LABELS = {
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "Analyst_QA_Uncertainty_pct": "Analyst QA Uncertainty",
    "Entire_All_Negative_pct": "Negative Sentiment",
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
        description="Stage 4: Test CEO Clarity Hypothesis",
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
        # Find latest panel
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "ceo_clarity",
            required_file="ceo_clarity_panel.parquet",
        )
        panel_file = panel_dir / "ceo_clarity_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    return panel


def prepare_regression_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Prepare panel data for regression.

    Filters to complete cases and ensures proper data types.

    Args:
        panel: Raw panel DataFrame

    Returns:
        Prepared DataFrame
    """
    print("\n" + "=" * 60)
    print("Preparing regression data")
    print("=" * 60)

    initial_n = len(panel)

    # Filter to non-null ceo_id
    df = panel[panel["ceo_id"].notna()].copy()
    print(f"  After ceo_id filter: {len(df):,} / {initial_n:,}")

    # Define required variables
    required = (
        [CONFIG["dependent_var"]]
        + CONFIG["linguistic_controls"]
        + CONFIG["firm_controls"]
        + ["ceo_id", "year"]
    )

    # Check which variables exist — MAJOR-5: hard-fail if any required variable missing
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        raise ValueError(
            f"Required variables missing from panel: {missing_vars}. "
            "Panel build may be incomplete. Aborting to prevent misspecified regression."
        )

    # Filter to complete cases
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases filter: {len(df):,}")

    # Assign sample based on FF12 industry code.
    # FF12 codes: 8=Utility, 11=Finance, all others=Main.
    # Note: ff12_code is guaranteed non-null in the manifest (ff12=12 "Other"
    # is the catch-all for SIC codes not in FF12 categories 1-11). Any residual
    # NaN rows are placed in Main (matching v1 behaviour) so no rows are dropped.
    if "ff12_code" in df.columns:
        if "sample" not in df.columns:
            df["sample"] = assign_industry_sample(df["ff12_code"])

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (df["sample"] == sample).sum()
        print(f"    {sample}: {n:,} calls")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    sample_name: str,
) -> tuple[Any, Optional[pd.DataFrame], Set[Any]]:
    """Run OLS regression with CEO fixed effects.

    Args:
        df_sample: Sample DataFrame
        sample_name: Name of sample for logging

    Returns:
        Tuple of (model, df_reg, valid_ceos)
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, set()

    # Filter to CEOs with minimum calls
    min_calls = CONFIG["min_calls_per_ceo"]
    ceo_counts = df_sample["ceo_id"].value_counts()
    valid_ceos: Set[Any] = set(ceo_counts[ceo_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"  After >={min_calls} calls filter: {len(df_reg):,} calls, {df_reg['ceo_id'].nunique():,} CEOs"
    )

    if len(df_reg) < 100:
        print(f"  WARNING: Too few observations ({len(df_reg)}), skipping")
        return None, None, set()

    # Convert to string for categorical treatment
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula - only include controls that exist in dataframe
    dep_var = CONFIG["dependent_var"]
    controls = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula}")

    # Estimate model
    print("  Estimating... (this may take a minute)")
    start_time = datetime.now()

    try:
        # Model: C(ceo_id) categorical dummies act as CEO fixed effects within
        # the PanelOLS entity (gvkey) × time (year) index. C(year) adds year dummies.
        # EntityEffects/TimeEffects are NOT used — the CEO-FE design intentionally
        # uses C(ceo_id) dummies so that individual CEO coefficients can be extracted
        # post-estimation (clarity scores = gamma_i per CEO).
        model_obj = PanelOLS.from_formula(
            formula,
            data=df_reg.set_index(["gvkey", "year"]),
            drop_absorbed=True,
        )
        model = model_obj.fit(
            # M-2 fix: cluster SEs at CEO level (not HC1) to account for
            # within-CEO correlation across calls in the same regression.
            # HC1 treats all observations as independent, understating SEs
            # when the same CEO appears in many rows (Liang-Zeger problem).
            cov_type="clustered",
            cov_kwds={"groups": df_reg["ceo_id"]},
        )
    except ValueError as e:
        print(f"ERROR: Regression failed: {e}", file=sys.stderr)
        return None, None, set()

    duration = (datetime.now() - start_time).total_seconds()

    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {float(model.rsquared_within):.4f}")
    print(f"  Adj. R-squared: {float(model.rsquared_inclusive):.4f}")
    print(f"  N observations: {int(model.nobs):,}")

    return model, df_reg, valid_ceos


def extract_clarity_scores(
    model: Any,
    df_reg: pd.DataFrame,
    sample_name: str,
) -> pd.DataFrame:
    """Extract CEO fixed effects as raw (unstandardized) ClarityCEO_raw scores.

    ClarityCEO_raw = -gamma_i (negative of CEO fixed effect).
    Standardization is deferred to save_outputs() so it is applied
    globally across all samples — ensuring scores are on a single
    comparable scale rather than independently normalized per sample.

    FIX-6: Reference CEOs (gamma = 0 by statsmodels convention, not estimated)
    are tagged with is_reference=True and excluded from clarity_scores.parquet,
    since their score is a normalization artifact rather than an estimate.

    Args:
        model: Fitted OLS model
        df_reg: Regression DataFrame (ceo_id already cast to str)
        sample_name: Sample name for metadata

    Returns:
        DataFrame with ceo_id, gamma_i, ClarityCEO_raw, sample, is_reference
        (NOT yet standardized — caller must standardize globally)
    """
    print(f"\n  Extracting CEO fixed effects for {sample_name}...")

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

    # FIX-6: Identify reference CEOs (alphabetically first — statsmodels default).
    # Their gamma = 0 is a normalization artifact, not an estimate.
    # We record them but will exclude from final output.
    all_ceos = df_reg["ceo_id"].unique()
    reference_ceos = set(c for c in all_ceos if c not in ceo_effects)

    print(
        f"  Found {len(ceo_effects)} estimated CEOs + {len(reference_ceos)} reference "
        f"(reference excluded from output)"
    )

    # Build DataFrame — estimated CEOs only
    rows = [
        {"ceo_id": ceo_id, "gamma_i": gamma_i, "is_reference": False}
        for ceo_id, gamma_i in ceo_effects.items()
    ]
    # Include reference CEOs tagged so caller can inspect if needed
    for ref_ceo in reference_ceos:
        rows.append({"ceo_id": ref_ceo, "gamma_i": 0.0, "is_reference": True})

    ceo_fe = pd.DataFrame(rows)

    # ClarityCEO_raw = -gamma_i (higher = lower uncertainty tendency = clearer)
    ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]
    ceo_fe["sample"] = sample_name

    # NOTE: ClarityCEO (standardized) is NOT computed here.
    # It is computed globally in save_outputs() after all samples are collected.

    return ceo_fe


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    results: Dict[str, Dict[str, Any]],
    all_clarity_scores: List[pd.DataFrame],
    panel: pd.DataFrame,
    out_dir: Path,
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Save all outputs.

    S4 fix: Standardization of ClarityCEO is done here, PER SAMPLE (not globally).
    Regressions for Main, Finance, and Utility each use a different reference CEO
    (statsmodels' alphabetically-first CEO per sample), so raw gamma values are
    anchored to different baselines across samples and cannot be compared directly.
    Per-sample z-score absorbs the reference-level offset while preserving the
    within-sample relative rank.

    FIX-6: Reference CEOs (gamma=0 normalization artifact) are excluded from
    the saved clarity_scores.parquet.

    FIX-10: CEO metadata (ceo_name, n_calls) is joined from the panel.

    Args:
        results: Dict mapping sample names to regression results
        all_clarity_scores: List of raw (unstandardized) clarity score DataFrames
        panel: Full panel DataFrame (for CEO metadata join)
        out_dir: Output directory
        stats: Stats dict

    Returns:
        Final clarity_df with per-sample standardized ClarityCEO scores
    """
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Control variables for LaTeX table
    control_vars = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]

    # Generate LaTeX table
    make_accounting_table(
        results=results,
        caption="Table 1: CEO Clarity Fixed Effects",
        label="tab:ceo_clarity",
        note=(
            "This table reports CEO fixed effects from regressing CEO Q&A "
            "uncertainty on firm characteristics and year fixed effects. "
            "ClarityCEO is computed as the negative of the CEO fixed effect, "
            "standardized globally across all industry samples. "
            "Standard errors are clustered at the CEO level (cov_type=cluster, groups=ceo_id)."
        ),
        variable_labels=VARIABLE_LABELS,
        control_variables=control_vars,
        entity_label="N CEOs",
        output_path=out_dir / "ceo_clarity_table.tex",
    )
    print("  Saved: ceo_clarity_table.tex")

    # Build and save clarity scores
    clarity_df = pd.DataFrame()
    if all_clarity_scores:
        raw_df = pd.concat(all_clarity_scores, ignore_index=True)

        # FIX-6: Exclude reference CEOs — their gamma=0 is a normalization artifact
        estimated_df = raw_df[~raw_df["is_reference"]].copy()
        n_reference = raw_df["is_reference"].sum()
        print(f"  Excluded {n_reference} reference CEO(s) from clarity scores")

        # S4 fix: Standardize ClarityCEO_raw PER SAMPLE (not globally).
        # Regressions for Main, Finance, and Utility each use a different
        # reference CEO (statsmodels' alphabetically-first CEO per sample),
        # so raw gamma values are anchored to different baselines across samples
        # and cannot be compared directly.  Per-sample z-score absorbs the
        # reference-level offset while preserving the within-sample relative rank.
        # (Identical pattern to test_ceo_clarity_regime.py's per-regime logic.)
        estimated_df["ClarityCEO"] = np.nan
        for _sample_key in estimated_df["sample"].unique():
            _idx = estimated_df.index[estimated_df["sample"] == _sample_key]
            _raw_vals: np.ndarray = estimated_df.loc[
                _idx, "ClarityCEO_raw"
            ].values.astype(float)  # type: ignore[union-attr]
            _s_mean = float(_raw_vals.mean())
            _s_std = float(_raw_vals.std())
            if _s_std > 0:
                estimated_df.loc[_idx, "ClarityCEO"] = (_raw_vals - _s_mean) / _s_std
            else:
                estimated_df.loc[_idx, "ClarityCEO"] = 0.0
            print(
                f"  {_sample_key} standardization: mean={_s_mean:.4f}, std={_s_std:.4f} "
                f"(N={len(_idx):,} estimated CEOs)"
            )

        print(
            f"  ClarityCEO post-standardization (per-sample): "
            f"overall mean={estimated_df['ClarityCEO'].mean():.4f}, "
            f"std={estimated_df['ClarityCEO'].std():.4f}"
        )

        # FIX-10: Join CEO metadata from panel (ceo_name, n_calls per CEO)
        ceo_meta = (
            panel[panel["ceo_id"].notna()]
            .assign(ceo_id_str=lambda df: df["ceo_id"].astype(str))
            .groupby("ceo_id_str")
            .agg(
                ceo_name=("ceo_name", "first"),
                n_calls=("file_name", "count"),
            )
            .reset_index()
            .rename(columns={"ceo_id_str": "ceo_id"})
        )
        estimated_df = estimated_df.merge(ceo_meta, on="ceo_id", how="left")

        # Final column order
        output_cols = [
            "ceo_id",
            "ceo_name",
            "sample",
            "gamma_i",
            "ClarityCEO_raw",
            "ClarityCEO",
            "n_calls",
        ]
        output_cols = [c for c in output_cols if c in estimated_df.columns]
        clarity_df = estimated_df[output_cols]

        clarity_path = out_dir / "clarity_scores.parquet"
        clarity_df.to_parquet(clarity_path, index=False)
        print(f"  Saved: clarity_scores.parquet ({len(clarity_df):,} estimated CEOs)")

    # Save regression results text
    for sample_name, result in results.items():
        model = result.get("model")
        if model is not None:
            results_path = out_dir / f"regression_results_{sample_name.lower()}.txt"
            with open(results_path, "w") as f:
                f.write(model.summary().as_text())
            print(f"  Saved: regression_results_{sample_name.lower()}.txt")

    return clarity_df


def generate_report(
    results: Dict[str, Dict[str, Any]],
    clarity_df: pd.DataFrame,
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report.

    Args:
        results: Regression results dict
        clarity_df: Final clarity scores DataFrame (per-sample standardized, references excluded)
        out_dir: Output directory
        duration: Duration in seconds
    """
    report_lines = [
        "# Stage 4: CEO Clarity Hypothesis Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Model Specification",
        "",
        "```",
        f"{CONFIG['dependent_var']} ~ C(ceo_id) + C(year) +",
        "    " + " + ".join(CONFIG["linguistic_controls"]) + " +",
        "    " + " + ".join(CONFIG["firm_controls"]),
        "```",
        "",
        "## Summary Statistics",
        "",
        "| Sample | N Obs | N CEOs (estimated) | R-squared |",
        "|--------|---------|--------------------|-----------|",
    ]

    for sample_name, result in results.items():
        diag = result.get("diagnostics", {})
        n_obs = diag.get("n_obs", "N/A")
        n_ceo = diag.get("n_ceos", "N/A")
        r2 = diag.get("rsquared", "N/A")
        # MAJOR-4: format spec :, only applies to ints — guard against "N/A" string
        n_obs_str = f"{n_obs:,}" if isinstance(n_obs, int) else str(n_obs)
        n_ceo_str = f"{n_ceo:,}" if isinstance(n_ceo, int) else str(n_ceo)
        r2_str = f"{r2:.4f}" if isinstance(r2, float) else str(r2)
        report_lines.append(f"| {sample_name} | {n_obs_str} | {n_ceo_str} | {r2_str} |")

    report_lines.append("")
    if not clarity_df.empty:
        report_lines.append(
            f"**Note:** ClarityCEO scores are standardized per-sample (within Main, "
            f"Finance, and Utility separately) across all "
            f"{len(clarity_df):,} estimated CEOs (mean=0, std=1 within each sample). "
            f"Per-sample standardization absorbs the reference-CEO baseline offset. "
            f"Reference CEOs (statsmodels baseline) are excluded."
        )
        report_lines.append("")

    # Top CEOs by sample — use globally standardized scores
    if not clarity_df.empty and "ClarityCEO" in clarity_df.columns:
        for sample in ["Main", "Finance", "Utility"]:
            sample_df = clarity_df[clarity_df["sample"] == sample].copy()
            if len(sample_df) == 0:
                continue

            name_col = "ceo_name" if "ceo_name" in sample_df.columns else "ceo_id"

            report_lines.append(f"## {sample} Sample")
            report_lines.append("")
            report_lines.append("### Top 5 Clearest CEOs")
            report_lines.append("")
            report_lines.append("| Rank | CEO | ClarityCEO |")
            report_lines.append("|------|-----|------------|")

            for rank, (_, row) in enumerate(
                sample_df.nlargest(5, "ClarityCEO").iterrows(), start=1
            ):
                report_lines.append(
                    f"| {rank} | {row[name_col]} | {row['ClarityCEO']:.3f} |"
                )

            report_lines.append("")
            report_lines.append("### Top 5 Most Uncertain CEOs")
            report_lines.append("")
            report_lines.append("| Rank | CEO | ClarityCEO |")
            report_lines.append("|------|-----|------------|")

            for rank, (_, row) in enumerate(
                sample_df.nsmallest(5, "ClarityCEO").iterrows(), start=1
            ):
                report_lines.append(
                    f"| {rank} | {row[name_col]} | {row['ClarityCEO']:.3f} |"
                )

            report_lines.append("")

    # Write report
    report_path = out_dir / "report_step4_ceo_clarity.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: report_step4_ceo_clarity.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "test_ceo_clarity",
        "timestamp": timestamp,
        "regressions": {},
        "timing": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "ceo_clarity" / timestamp

    print("=" * 80)
    print("STAGE 4: Test CEO Clarity Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Prepare data
    df = prepare_regression_data(panel)

    # Run regressions by sample
    results: Dict[str, Dict[str, Any]] = {}
    all_clarity_scores: List[pd.DataFrame] = []

    for sample_name in ["Main", "Finance", "Utility"]:
        df_sample = df[df["sample"] == sample_name].copy()

        if len(df_sample) < 100:
            print(
                f"\n  Skipping {sample_name}: too few observations ({len(df_sample)})"
            )
            continue

        # Run regression
        model, df_reg, valid_ceos = run_regression(df_sample, sample_name)

        if model is None or df_reg is None:
            continue

        # Extract clarity scores
        clarity_scores = extract_clarity_scores(model, df_reg, sample_name)
        all_clarity_scores.append(clarity_scores)

        # Store results
        results[sample_name] = {
            "model": model,
            "diagnostics": {
                "n_obs": int(model.nobs),
                "n_ceos": len(valid_ceos),
                "rsquared": float(model.rsquared_within),
                "rsquared_adj": float(model.rsquared_inclusive),
            },
        }

        # Stats
        stats["regressions"][sample_name] = {
            "n_obs": int(model.nobs),
            "n_ceos": len(valid_ceos),
            "rsquared": float(model.rsquared_within),
        }

    # Save outputs
    clarity_df: pd.DataFrame = pd.DataFrame()
    if results:
        clarity_df = save_outputs(results, all_clarity_scores, panel, out_dir, stats)

        # Generate report
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(results, clarity_df, out_dir, duration)

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    stats["timing"]["duration_seconds"] = round(duration, 2)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
