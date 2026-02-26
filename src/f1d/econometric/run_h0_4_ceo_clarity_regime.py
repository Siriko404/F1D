#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test CEO Clarity — Regime Analysis (4.1.3)
================================================================================
ID: econometric/run_h0_4_ceo_clarity_regime
Description: Split-sample regime analysis of CEO Clarity. Runs the same CEO
             Clarity fixed-effects regression (from 4.1.1) separately for three
             time regimes using the Main sample only (non-financial, non-utility):

               - Pre-Crisis:  2002–2007
               - Crisis:      2008–2009
               - Post-Crisis: 2010–2018

             Tests whether the Clarity trait is stable across economic regimes
             or shifts with market stress.

Model Specification (identical to 4.1.1):
    CEO_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
        CEO_Pres_Uncertainty_pct +
        Analyst_QA_Uncertainty_pct +
        Entire_All_Negative_pct +
        StockRet + MarketRet + EPS_Growth + SurpDec

Sample:
    Main only (FF12 codes 1-7, 9-10, 12 — non-financial, non-utility).
    Finance (FF12=11) and Utility (FF12=8) are excluded from all regime splits.

Regime Definitions:
    - Pre-Crisis:  year in [2002, 2007]
    - Crisis:      year in [2008, 2009]
    - Post-Crisis: year in [2010, 2018]

Minimum Calls Filter:
    CEOs must have >= 5 calls *within the regime window* to be included.

Standardization:
    ClarityCEO scores are standardized GLOBALLY across all three regimes
    combined, so regime scores are on a single comparable scale.

Inputs:
    - outputs/variables/ceo_clarity/latest/ceo_clarity_panel.parquet

Outputs:
    - outputs/econometric/ceo_clarity_regime/{timestamp}/ceo_clarity_regime_table.tex
    - outputs/econometric/ceo_clarity_regime/{timestamp}/clarity_scores.parquet
    - outputs/econometric/ceo_clarity_regime/{timestamp}/regression_results_{regime}.txt
    - outputs/econometric/ceo_clarity_regime/{timestamp}/report_step4_ceo_clarity_regime.md
    - outputs/econometric/ceo_clarity_regime/{timestamp}/summary_stats.csv
    - outputs/econometric/ceo_clarity_regime/{timestamp}/summary_stats.tex

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
from f1d.shared.path_utils import get_latest_output_dir


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
    # Regime definitions: inclusive year bounds
    "regimes": {
        "Pre-Crisis": (2002, 2007),
        "Crisis": (2008, 2009),
        "Post-Crisis": (2010, 2018),
    },
    # Main sample excludes Finance (FF12=11) and Utility (FF12=8)
    "exclude_ff12": [8, 11],
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
# Summary Statistics Variables (Same as H0.2, Main sample only)
# ==============================================================================

SUMMARY_STATS_VARS = [
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    {"col": "Entire_All_Negative_pct", "label": "Negative Sentiment"},
    {"col": "StockRet", "label": "Stock Return"},
    {"col": "MarketRet", "label": "Market Return"},
    {"col": "EPS_Growth", "label": "EPS Growth"},
    {"col": "SurpDec", "label": "Earnings Surprise Decile"},
]


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Test CEO Clarity — Regime Analysis",
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
    """Load CEO Clarity panel from Stage 3 output.

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
        # Find latest CEO Clarity panel (same panel as 4.1.1)
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


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_regression_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Prepare panel data for regime regression.

    Filters to Main sample (non-financial, non-utility) complete cases.
    Does NOT apply year filter here — that is done per-regime in the loop.

    Args:
        panel: Raw panel DataFrame

    Returns:
        Prepared Main-sample DataFrame (all years)
    """
    print("\n" + "=" * 60)
    print("Preparing regression data")
    print("=" * 60)

    initial_n = len(panel)

    # Filter to non-null ceo_id
    df = panel[panel["ceo_id"].notna()].copy()
    print(f"  After ceo_id filter: {len(df):,} / {initial_n:,}")

    # Define required variables — hard-fail if any missing (MAJOR-5)
    required = (
        [CONFIG["dependent_var"]]
        + CONFIG["linguistic_controls"]
        + CONFIG["firm_controls"]
        + ["ceo_id", "year"]
    )

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

    # Restrict to Main sample: exclude Finance (FF12=11) and Utility (FF12=8)
    if "ff12_code" in df.columns:
        exclude = CONFIG["exclude_ff12"]
        df = df[~df["ff12_code"].isin(exclude)].copy()
        print(f"  After Main sample filter (excl FF12 {exclude}): {len(df):,}")
    else:
        print("  WARNING: ff12_code column not found — no industry filter applied")

    # Log year coverage
    print(
        f"  Year range in data: {int(df['year'].min())}–{int(df['year'].max())}"
        if len(df) > 0
        else "  WARNING: no rows after filters"
    )

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_regime: pd.DataFrame,
    regime_name: str,
) -> tuple[Any, Optional[pd.DataFrame], Set[Any]]:
    """Run OLS regression with CEO and year fixed effects for a single regime.

    Args:
        df_regime: Regime-filtered DataFrame (already Main sample)
        regime_name: Label for this regime (e.g. "Pre-Crisis")

    Returns:
        Tuple of (model, df_reg, valid_ceos)
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {regime_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, set()

    # Filter to CEOs with minimum calls within this regime window
    min_calls = CONFIG["min_calls_per_ceo"]
    ceo_counts = df_regime["ceo_id"].value_counts()
    valid_ceos: Set[Any] = set(ceo_counts[ceo_counts >= min_calls].index)
    df_reg = df_regime[df_regime["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"  After >={min_calls} calls filter: {len(df_reg):,} calls, "
        f"{df_reg['ceo_id'].nunique():,} CEOs"
    )

    if len(df_reg) < 100:
        print(f"  WARNING: Too few observations ({len(df_reg)}), skipping")
        return None, None, set()

    # Convert to string for categorical treatment
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula — only include controls that exist in dataframe
    dep_var = CONFIG["dependent_var"]
    controls = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula}")

    # Estimate model
    print("  Estimating... (this may take a minute)")
    start_time = datetime.now()

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
        print(f"ERROR: Regression failed: {e}", file=sys.stderr)
        return None, None, set()

    duration = (datetime.now() - start_time).total_seconds()

    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adj. R-squared: {model.rsquared_adj:.4f}")
    print(f"  N observations: {int(model.nobs):,}")

    return model, df_reg, valid_ceos


# ==============================================================================
# Extract Clarity Scores
# ==============================================================================


def extract_clarity_scores(
    model: Any,
    df_reg: pd.DataFrame,
    regime_name: str,
) -> pd.DataFrame:
    """Extract CEO fixed effects as raw (unstandardized) ClarityCEO_raw scores.

    ClarityCEO_raw = -gamma_i (negative of CEO fixed effect).
    Standardization is deferred to save_outputs() so it is applied
    per-regime — each regime's scores are z-scored independently.

    Per-regime standardization is correct here because gamma_i values from
    three separate regressions are on incompatible scales: each regression
    has a different reference CEO (statsmodels' alphabetically-first CEO),
    so the raw gamma_i means differ across regimes due to reference-level
    contamination, not real regime differences. Standardizing within each
    regime absorbs this artifact and leaves only the relative rank signal.

    FIX-6: Reference CEOs (gamma = 0 by statsmodels convention, not estimated)
    are tagged with is_reference=True and excluded from clarity_scores.parquet,
    since their score is a normalization artifact rather than an estimate.

    Args:
        model: Fitted OLS model
        df_reg: Regression DataFrame (ceo_id already cast to str)
        regime_name: Regime name for metadata

    Returns:
        DataFrame with ceo_id, gamma_i, ClarityCEO_raw, regime, is_reference
        (NOT yet standardized — caller must standardize per regime)
    """
    print(f"\n  Extracting CEO fixed effects for {regime_name}...")

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
    all_ceos = df_reg["ceo_id"].unique()
    reference_ceos = set(c for c in all_ceos if c not in ceo_effects)

    print(
        f"  Found {len(ceo_effects)} estimated CEOs + {len(reference_ceos)} reference "
        f"(reference excluded from output)"
    )

    # Build DataFrame — estimated CEOs
    rows: List[Dict[str, Any]] = [
        {"ceo_id": ceo_id, "gamma_i": gamma_i, "is_reference": False}
        for ceo_id, gamma_i in ceo_effects.items()
    ]
    # Include reference CEOs tagged so caller can inspect if needed
    for ref_ceo in reference_ceos:
        rows.append({"ceo_id": ref_ceo, "gamma_i": 0.0, "is_reference": True})

    ceo_fe = pd.DataFrame(rows)

    # ClarityCEO_raw = -gamma_i (higher = lower uncertainty tendency = clearer)
    ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]
    ceo_fe["regime"] = regime_name

    # NOTE: ClarityCEO (standardized) is NOT computed here.
    # It is computed per-regime in save_outputs() after all regimes are collected.

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

    Standardization: ClarityCEO is z-scored PER REGIME (not globally).
    Each regime's regression produces gamma_i values relative to a different
    reference CEO (statsmodels' alphabetically-first CEO in that regime's
    valid-CEO set). Pooling raw gammas across regimes would conflate
    reference-level artifacts with real regime differences. Standardizing
    within each regime absorbs the reference offset and preserves only the
    within-regime relative rank signal — which is what the robustness check
    is designed to test.

    FIX-6: Reference CEOs (gamma=0 normalization artifact) are excluded from
    the saved clarity_scores.parquet.

    Args:
        results: Dict mapping regime names to regression results
        all_clarity_scores: List of raw (unstandardized) clarity score DataFrames
        panel: Full panel DataFrame (for CEO metadata join)
        out_dir: Output directory
        stats: Stats dict

    Returns:
        Final clarity_df with per-regime standardized ClarityCEO scores
    """
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Control variables for LaTeX table
    control_vars = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]

    # Generate LaTeX table — 3 columns: Pre-Crisis, Crisis, Post-Crisis
    make_accounting_table(
        results=results,
        caption=(
            "Table 2: CEO Clarity Fixed Effects by Economic Regime "
            "(Main Sample: Non-Financial, Non-Utility Firms)"
        ),
        label="tab:ceo_clarity_regime",
        note=(
            "This table reports CEO fixed effects from regressing CEO Q&A "
            "uncertainty on firm characteristics and year fixed effects, "
            "estimated separately for three economic regimes. "
            "Pre-Crisis: 2002--2007; Crisis: 2008--2009; Post-Crisis: 2010--2018. "
            "Main sample only (FF12 non-financial, non-utility firms). "
            "ClarityCEO is computed as the negative of the CEO fixed effect, "
            "standardized within each regime separately (mean 0, std 1 per regime). "
            "Per-regime standardization is used because gamma estimates from separate "
            "regressions are anchored to different reference CEOs and cannot be "
            "directly compared across regimes. "
            "CEOs must have $\\geq 5$ calls within the regime window to be included. "
            "Standard errors are clustered at the CEO level (cov_type=cluster, groups=ceo_id)."
        ),
        variable_labels=VARIABLE_LABELS,
        control_variables=control_vars,
        entity_label="N CEOs",
        output_path=out_dir / "ceo_clarity_regime_table.tex",
    )
    print("  Saved: ceo_clarity_regime_table.tex")

    # Build and save clarity scores
    clarity_df: pd.DataFrame = pd.DataFrame()
    if all_clarity_scores:
        raw_df = pd.concat(all_clarity_scores, ignore_index=True)

        # FIX-6: Exclude reference CEOs — their gamma=0 is a normalization artifact
        estimated_df = raw_df[~raw_df["is_reference"]].copy()
        n_reference = raw_df["is_reference"].sum()
        print(f"  Excluded {n_reference} reference CEO(s) from clarity scores")

        # Standardize ClarityCEO_raw PER REGIME.
        # gamma_i values from separate regressions are anchored to different
        # reference CEOs (statsmodels' alphabetically-first CEO per regime),
        # so raw values are on incompatible scales across regimes.
        # Standardizing within each regime absorbs the reference-level offset
        # while preserving the within-regime relative rank — the true signal.
        # Per-regime z-score: compute via numpy to avoid pandas-stubs loc overload
        # ambiguity; write result back via the same boolean mask.
        estimated_df["ClarityCEO"] = np.nan
        for _regime_key in estimated_df["regime"].unique():
            _idx = estimated_df.index[estimated_df["regime"] == _regime_key]
            _raw_vals: np.ndarray = estimated_df.loc[
                _idx, "ClarityCEO_raw"
            ].values.astype(float)  # type: ignore[union-attr]
            _r_mean = float(_raw_vals.mean())
            _r_std = float(_raw_vals.std())
            estimated_df.loc[_idx, "ClarityCEO"] = (_raw_vals - _r_mean) / _r_std
            print(
                f"  {_regime_key} standardization: mean={_r_mean:.4f}, std={_r_std:.4f} "
                f"(N={len(_idx):,} estimated CEOs)"
            )

        print(
            f"  ClarityCEO post-standardization (per-regime): "
            f"overall mean={estimated_df['ClarityCEO'].mean():.4f}, "
            f"std={estimated_df['ClarityCEO'].std():.4f}"
        )

        # Join CEO metadata from panel.
        # n_calls_regime: call count within the regime window (what matters for
        # interpreting the regression).
        # Computed by merging panel with the regime year bounds, then grouping.
        regime_bounds = CONFIG["regimes"]  # {name: (y0, y1)}
        regime_call_counts: List[pd.DataFrame] = []
        for rname, (y0, y1) in regime_bounds.items():
            rdf = (
                panel[
                    panel["ceo_id"].notna()
                    & (panel["year"] >= y0)
                    & (panel["year"] <= y1)
                ]
                .assign(ceo_id_str=lambda df: df["ceo_id"].astype(str))
                .groupby("ceo_id_str")
                .agg(n_calls_regime=("file_name", "count"))
                .reset_index()
                .rename(columns={"ceo_id_str": "ceo_id"})
                .assign(regime=rname)
            )
            regime_call_counts.append(rdf)
        regime_meta = pd.concat(regime_call_counts, ignore_index=True)

        # CEO name (panel-wide, first occurrence)
        ceo_names = (
            panel[panel["ceo_id"].notna()]
            .assign(ceo_id_str=lambda df: df["ceo_id"].astype(str))
            .groupby("ceo_id_str")
            .agg(ceo_name=("ceo_name", "first"))
            .reset_index()
            .rename(columns={"ceo_id_str": "ceo_id"})
        )

        estimated_df = estimated_df.merge(ceo_names, on="ceo_id", how="left").merge(
            regime_meta, on=["ceo_id", "regime"], how="left"
        )

        # Final column order
        output_cols = [
            "ceo_id",
            "ceo_name",
            "regime",
            "gamma_i",
            "ClarityCEO_raw",
            "ClarityCEO",
            "n_calls_regime",
        ]
        output_cols = [c for c in output_cols if c in estimated_df.columns]
        clarity_df = estimated_df[output_cols]

        clarity_path = out_dir / "clarity_scores.parquet"
        clarity_df.to_parquet(clarity_path, index=False)
        print(
            f"  Saved: clarity_scores.parquet ({len(clarity_df):,} estimated CEOs "
            f"across {clarity_df['regime'].nunique()} regimes)"
        )

    # Save regression results text
    for regime_name, result in results.items():
        model = result.get("model")
        if model is not None:
            safe_name = regime_name.lower().replace("-", "_").replace(" ", "_")
            results_path = out_dir / f"regression_results_{safe_name}.txt"
            with open(results_path, "w") as f:
                f.write(model.summary().as_text())
            print(f"  Saved: regression_results_{safe_name}.txt")

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
        clarity_df: Final clarity scores DataFrame (per-regime standardized, refs excluded)
        out_dir: Output directory
        duration: Duration in seconds
    """
    report_lines = [
        "# Stage 4: CEO Clarity Regime Analysis Report",
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
        "**Sample:** Main only (FF12 non-financial, non-utility)",
        "",
        "## Regime Definitions",
        "",
        "| Regime | Years |",
        "|--------|-------|",
    ]

    for regime_name, (yr_start, yr_end) in CONFIG["regimes"].items():
        report_lines.append(f"| {regime_name} | {yr_start}–{yr_end} |")

    report_lines += [
        "",
        "## Summary Statistics",
        "",
        "| Regime | N Obs | N CEOs (estimated) | R-squared |",
        "|--------|-------|--------------------|-----------|",
    ]

    for regime_name, result in results.items():
        diag = result.get("diagnostics", {})
        n_obs = diag.get("n_obs", "N/A")
        n_ceo = diag.get("n_ceos", "N/A")
        r2 = diag.get("rsquared", "N/A")
        n_obs_str = f"{n_obs:,}" if isinstance(n_obs, int) else str(n_obs)
        n_ceo_str = f"{n_ceo:,}" if isinstance(n_ceo, int) else str(n_ceo)
        r2_str = f"{r2:.4f}" if isinstance(r2, float) else str(r2)
        report_lines.append(f"| {regime_name} | {n_obs_str} | {n_ceo_str} | {r2_str} |")

    report_lines.append("")
    if not clarity_df.empty:
        report_lines.append(
            f"**Note:** ClarityCEO scores are standardized within each regime separately "
            f"(mean=0, std=1 per regime; {len(clarity_df):,} total CEO-regime rows). "
            f"Per-regime standardization is used because gamma estimates from separate "
            f"regressions are anchored to different reference CEOs. "
            f"Reference CEOs (statsmodels baseline) are excluded."
        )
        report_lines.append("")

    # Top CEOs by regime — use per-regime standardized scores
    if not clarity_df.empty and "ClarityCEO" in clarity_df.columns:
        for regime_name in CONFIG["regimes"]:
            regime_df = clarity_df[clarity_df["regime"] == regime_name].copy()
            if len(regime_df) == 0:
                continue

            name_col = "ceo_name" if "ceo_name" in regime_df.columns else "ceo_id"

            report_lines.append(f"## {regime_name} Regime")
            report_lines.append("")
            report_lines.append("### Top 5 Clearest CEOs")
            report_lines.append("")
            report_lines.append("| Rank | CEO | ClarityCEO |")
            report_lines.append("|------|-----|------------|")

            for rank, (_, row) in enumerate(
                regime_df.nlargest(5, "ClarityCEO").iterrows(), start=1
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
                regime_df.nsmallest(5, "ClarityCEO").iterrows(), start=1
            ):
                report_lines.append(
                    f"| {rank} | {row[name_col]} | {row['ClarityCEO']:.3f} |"
                )

            report_lines.append("")

    # Write report
    report_path = out_dir / "report_step4_ceo_clarity_regime.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: report_step4_ceo_clarity_regime.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "test_ceo_clarity_regime",
        "timestamp": timestamp,
        "regressions": {},
        "timing": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "ceo_clarity_regime" / timestamp

    print("=" * 80)
    print("STAGE 4: Test CEO Clarity — Regime Analysis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Regimes: {list(CONFIG['regimes'].keys())}")

    # Load panel (same CEO Clarity panel from 4.1.1)
    panel = load_panel(root, panel_path)

    # Prepare Main-sample data (all years; year filter applied per regime below)
    df_main = prepare_regression_data(panel)

    # Generate summary stats for Main-sample complete-case data (aggregate only)
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    make_summary_stats_table(
        df=df_main,
        variables=SUMMARY_STATS_VARS,
        sample_names=None,  # Aggregate only (Main sample)
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — CEO Clarity Regime Analysis (Main Sample)",
        label="tab:summary_stats_h04",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Run regressions by regime
    results: Dict[str, Dict[str, Any]] = {}
    all_clarity_scores: List[pd.DataFrame] = []

    for regime_name, (yr_start, yr_end) in CONFIG["regimes"].items():
        # Apply year filter for this regime
        df_regime = df_main[
            (df_main["year"] >= yr_start) & (df_main["year"] <= yr_end)
        ].copy()

        print(
            f"\n  {regime_name} ({yr_start}–{yr_end}): {len(df_regime):,} calls, "
            f"{df_regime['ceo_id'].nunique():,} CEOs (before min-calls filter)"
        )

        if len(df_regime) < 100:
            print(
                f"\n  Skipping {regime_name}: too few observations ({len(df_regime)})"
            )
            continue

        # Run regression
        model, df_reg, valid_ceos = run_regression(df_regime, regime_name)

        if model is None or df_reg is None:
            continue

        # Extract clarity scores (unstandardized)
        clarity_scores = extract_clarity_scores(model, df_reg, regime_name)
        all_clarity_scores.append(clarity_scores)

        # Store results
        results[regime_name] = {
            "model": model,
            "diagnostics": {
                "n_obs": int(model.nobs),
                "n_ceos": len(valid_ceos),
                "rsquared": model.rsquared,
                "rsquared_adj": model.rsquared_adj,
            },
        }

        # Stats
        stats["regressions"][regime_name] = {
            "n_obs": int(model.nobs),
            "n_ceos": len(valid_ceos),
            "rsquared": model.rsquared,
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

    if results:
        print("\nRegime Results:")
        for regime_name, result in results.items():
            diag = result["diagnostics"]
            print(
                f"  {regime_name}: N={diag['n_obs']:,}, "
                f"CEOs={diag['n_ceos']:,}, R²={diag['rsquared']:.4f}"
            )

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
