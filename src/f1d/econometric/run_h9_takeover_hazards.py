#!/usr/bin/env python3
"""
================================================================================
H9: Takeover Hazard Models
================================================================================
ID: econometric/run_h9_takeover_hazards
Description: Run Takeover Hazard models (H9) using the call-to-call
             counting-process panel from H9 panel builder.

Research Question:
    Does clarity in speech increase the likelihood of receiving a takeover bid,
    especially an UNINVITED bid?

Models:
    Model 1: Cox Proportional Hazards — All Takeovers
    Model 2: Cause-specific Cox PH    — Uninvited (Hostile + Unsolicited)
    Model 3: Cause-specific Cox PH    — Friendly (Friendly + Neutral)

Model Variants:
    PRIMARY STYLE MODELS:
        - CEO clarity score (ClarityCEO) — main clarity construct
        - Manager clarity score: does NOT exist in repo (noted as absent)
    SECONDARY RESIDUAL MODELS:
        - CEO residual (CEO_Clarity_Residual)
        - Manager residual (Manager_Clarity_Residual)

Hypothesis Tests (two-sided inference):
    H9-A: beta(Clarity) < 0 (clearer CEOs have lower takeover hazard)
    H9-B: beta(Clarity, uninvited) < beta(Clarity, friendly)
          (clarity reduces hostile takeover hazard more than friendly)

Financial controls (Compustat-only):
    Sparse block (all models): Size, BM, Lev, ROA, CashHoldings
    Expanded robustness (all families): + SalesGrowth, Intangibility, AssetGrowth

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    (Finance ff12=11 and Utility ff12=8 excluded from all models)

Survival construction (call-to-call intervals):
    Each interval opens at an earnings call and closes at the earliest of:
      (a) next earnings call date for the same firm
      (b) takeover announcement date
      (c) administrative censor date (end of sample)
    Time units: days since 2000-01-01
    Takeover = 1 only in the interval where a bid occurs, 0 otherwise
    Takeover_Uninvited = 1 if Takeover_Type == 'Uninvited', 0 otherwise
    Takeover_Friendly  = 1 if Takeover_Type == 'Friendly',  0 otherwise
    Unknown types are correctly censored in cause-specific models.

Inputs:
    - outputs/variables/takeover/latest/takeover_panel.parquet

Outputs:
    - outputs/econometric/takeover/{timestamp}/cox_ph_all.txt
    - outputs/econometric/takeover/{timestamp}/cox_cs_uninvited.txt
    - outputs/econometric/takeover/{timestamp}/cox_cs_friendly.txt
    - outputs/econometric/takeover/{timestamp}/hazard_ratios.csv
    - outputs/econometric/takeover/{timestamp}/model_diagnostics.csv
    - outputs/econometric/takeover/{timestamp}/report_h9_takeover.md
    - outputs/econometric/takeover/{timestamp}/run_log.txt
    - outputs/econometric/takeover/{timestamp}/summary_stats.csv
    - outputs/econometric/takeover/{timestamp}/summary_stats.tex
    - outputs/econometric/takeover/{timestamp}/takeover_hazard_table.tex

Deterministic: true
Dependencies:
    - Requires: H9 panel (build_h9_takeover_panel)
    - Uses: lifelines, f1d.shared

Author: Thesis Author
Date: 2026-02-26
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

warnings.filterwarnings("ignore")

# lifelines — CoxTimeVaryingFitter for call-to-call counting-process intervals
CoxTimeVaryingFitter: Any = None
concordance_index: Any = None
try:
    from lifelines import CoxTimeVaryingFitter  # type: ignore[no-redef,import-untyped]
    from lifelines.utils import concordance_index  # type: ignore[import-untyped]

    LIFELINES_AVAILABLE = True
except ImportError:
    LIFELINES_AVAILABLE = False
    print("WARNING: lifelines not available. Install with: pip install lifelines")

from f1d.shared.latex_tables_accounting import (
    make_summary_stats_table,
    make_cox_hazard_table,
)
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.observability import DualWriter
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.regression_validation import (
    RegressionValidationError,
    validate_columns,
    validate_sample_size,
)


# ==============================================================================
# Configuration
# ==============================================================================

# Financial controls (Compustat-only, no CRSP/IBES)
# Pass 05: Removed StockRet, MarketRet, SurpDec (CRSP/IBES)
# Sparse block: used in ALL models (primary + secondary)
SPARSE_CONTROLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CashHoldings",
]

# Expanded robustness block: used in all families as robustness check
EXPANDED_CONTROLS = SPARSE_CONTROLS + [
    "SalesGrowth",
    "Intangibility",
    "AssetGrowth",
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Clarity measures
    {"col": "ClarityCEO", "label": "ClarityCEO"},
    {"col": "CEO_Clarity_Residual", "label": "CEO_Clarity_Residual"},
    {"col": "Manager_Clarity_Residual", "label": "Manager_Clarity_Residual"},
    # Survival variables
    {"col": "duration", "label": "duration"},
    {"col": "Takeover", "label": "Takeover"},
    {"col": "Takeover_Uninvited", "label": "Takeover_Uninvited"},
    {"col": "Takeover_Friendly", "label": "Takeover_Friendly"},
    # Financial controls — Sparse block (all models)
    {"col": "Size", "label": "Size"},
    {"col": "BM", "label": "BM"},
    {"col": "Lev", "label": "Lev"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashHoldings", "label": "CashHoldings"},
    # Financial controls — Expanded robustness block (primary style only)
    {"col": "SalesGrowth", "label": "SalesGrowth"},
    {"col": "Intangibility", "label": "Intangibility"},
    {"col": "AssetGrowth", "label": "AssetGrowth"},
]

# Model variants: CEO clarity score (PRIMARY) + Residuals (SECONDARY)
# Pass 05: Reorganized to separate primary style models from secondary residual models
# Note: Manager clarity score (ClarityManager) does not exist in the repo.
# Only CEO clarity score (ClarityCEO) is available as a fixed-effect score.
# Manager variants are available only as residuals from the clarity extended regression.
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    # PRIMARY STYLE MODEL — CEO Clarity Score
    "CEO": {
        "clarity_var": "ClarityCEO",
        "description": "CEO Clarity Score (H1) — PRIMARY",
        "family": "primary_style",
    },
    # SECONDARY RESIDUAL MODELS — Residualized Uncertainty
    "CEO_Residual": {
        "clarity_var": "CEO_Clarity_Residual",
        "description": "CEO Residual — SECONDARY (residualized uncertainty)",
        "family": "secondary_residual",
    },
    "Manager_Residual": {
        "clarity_var": "Manager_Clarity_Residual",
        "description": "Manager Residual — SECONDARY (residualized uncertainty)",
        "family": "secondary_residual",
    },
}

# Counting-process columns (call-to-call: start/stop in days since 2000-01-01)
START_COL = "start"
STOP_COL = "stop"
EVENT_ALL_COL = "Takeover"
EVENT_UNINVITED_COL = "Takeover_Uninvited"
EVENT_FRIENDLY_COL = "Takeover_Friendly"

# Main sample: exclude Finance (ff12=11) and Utility (ff12=8)
MAIN_SAMPLE_EXCLUDE_FF12 = [8, 11]

MIN_OBS = 50  # Survival models need fewer obs than OLS


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="H9: Takeover Hazard Models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load call-to-call counting-process takeover panel."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "takeover",
            required_file="takeover_panel.parquet",
        )
        panel_file = panel_dir / "takeover_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows (call-to-call intervals): {len(panel):,}")
    print(f"  Unique firms: {panel['gvkey'].nunique():,}")
    print(f"  Columns: {len(panel.columns)}")

    # Hard assertions
    if "ff12_code" not in panel.columns:
        raise ValueError("'ff12_code' not found in takeover panel. Re-run build_h9_takeover_panel.")
    for col in [START_COL, STOP_COL]:
        if col not in panel.columns:
            raise ValueError(
                f"'{col}' not found in takeover panel. "
                "Panel must be in counting-process format. Re-run build_h9_takeover_panel."
            )

    n_event_firms = panel.groupby("gvkey")[EVENT_ALL_COL].max().sum()
    n_firms = panel["gvkey"].nunique()
    print(f"  Takeover event firms: {int(n_event_firms):,} / {n_firms:,}")

    if "duration" in panel.columns:
        print(f"  Interval duration (days): median={panel['duration'].median():.0f}, "
              f"mean={panel['duration'].mean():.0f}")

    return panel


def prepare_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample and create cause-specific event indicators."""
    df = panel[~panel["ff12_code"].isin(MAIN_SAMPLE_EXCLUDE_FF12)].copy()
    n_firms = df["gvkey"].nunique()
    n_event_firms = df.groupby("gvkey")[EVENT_ALL_COL].max().sum()
    print(f"\n  Main sample: {len(df):,} call-to-call intervals, {n_firms:,} firms")
    print(f"  Takeover event firms (Main): {int(n_event_firms):,}")

    # Create cause-specific event indicators
    # BUG FIX (Pass 03): Only mark as event when Takeover=1 AND type matches
    # Previous code marked ALL intervals of firms with that takeover type as events,
    # inflating cause-specific event counts by ~8-9x.
    df[EVENT_UNINVITED_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Uninvited")).astype(int)
    df[EVENT_FRIENDLY_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Friendly")).astype(int)

    n_uninvited = int(df[EVENT_UNINVITED_COL].sum())
    n_friendly = int(df[EVENT_FRIENDLY_COL].sum())
    n_all = int(df[EVENT_ALL_COL].sum())
    n_other = n_all - n_uninvited - n_friendly
    print(f"  Uninvited events: {n_uninvited:,}")
    print(f"  Friendly events:  {n_friendly:,}")
    # M-10 fix: firms with Takeover=1 but unknown/other Takeover_Type will have
    # EVENT_UNINVITED=0 AND EVENT_FRIENDLY=0, making them censored in both
    # cause-specific models. This is correct competing-risks practice (they are
    # competing events of unknown cause), but must be explicitly logged.
    if n_other > 0:
        other_types = df.loc[
            (df[EVENT_ALL_COL] == 1)
            & (df[EVENT_UNINVITED_COL] == 0)
            & (df[EVENT_FRIENDLY_COL] == 0),
            "Takeover_Type",
        ].value_counts(dropna=False)
        print(
            f"  WARNING: {n_other} takeover event(s) have neither Uninvited nor "
            f"Friendly type -- treated as censored in cause-specific models "
            f"(correct for competing risks). Type breakdown:\n{other_types.to_string()}"
        )

    return df


# ==============================================================================
# Survival Models
# ==============================================================================


def compute_concordance_time_varying(
    ctv: Any,
    df: pd.DataFrame,
    event_col: str,
    id_col: str = "gvkey",
) -> Optional[float]:
    """Compute concordance index for CoxTimeVaryingFitter.

    CoxTimeVaryingFitter does not expose concordance_index_ directly (unlike
    CoxPHFitter). We compute it by:
    1. Computing the mean partial hazard across all observations for each subject
    2. Using this as the predicted risk score
    3. Computing Harrell's C-index using lifelines.utils.concordance_index

    For time-varying covariates, using the mean hazard across the follow-up
    period provides a more stable estimate of overall risk than using just
    the last observation.

    Args:
        ctv: Fitted CoxTimeVaryingFitter model
        df: DataFrame used to fit the model (counting-process format)
        event_col: Name of the event indicator column
        id_col: Name of the subject identifier column

    Returns:
        Concordance index (float) or None if computation fails.
    """
    if concordance_index is None:
        return None

    try:
        # Predict partial hazard for all observations
        # Higher hazard = higher risk = shorter survival
        df_with_hazard = df.copy()
        df_with_hazard["_partial_hazard"] = ctv.predict_partial_hazard(df)  # type: ignore[union-attr]

        # Compute mean partial hazard for each subject
        # This gives a stable risk estimate across the follow-up period
        subject_hazards = df_with_hazard.groupby(id_col)["_partial_hazard"].mean()

        # Get the last observation for each subject (for event time and indicator)
        idx_last = df.groupby(id_col)[STOP_COL].idxmax()
        df_last = df.loc[idx_last].copy()

        # Align the hazards with the last observations
        subject_hazards = subject_hazards.loc[df_last[id_col].values]

        # Build clean dataframe for concordance computation (drop any NaNs)
        conc_df = pd.DataFrame(
            {
                "event_time": df_last[STOP_COL].values,
                "predicted_score": subject_hazards.values.flatten(),
                "event_observed": df_last[event_col].values,
            }
        )
        conc_df = conc_df.dropna()

        if len(conc_df) < 10:
            return None

        # For concordance_index:
        # - event_times: the stop time (time of event or censoring)
        # - predicted_scores: mean partial hazard (higher = worse prognosis)
        # - event_observed: whether the event occurred
        c_index = concordance_index(
            event_times=conc_df["event_time"].values,
            predicted_scores=conc_df["predicted_score"].values,
            event_observed=conc_df["event_observed"].values,
        )
        return float(c_index)
    except Exception:
        # Concordance computation may fail for edge cases
        return None


def run_cox_tv(
    df: pd.DataFrame,
    event_col: str,
    covariates: List[str],
    title: str,
    out_file: Path,
    strata: Optional[Any] = None,
) -> Optional[Any]:
    """Fit a Cox time-varying fitter (counting-process format).

    Uses CoxTimeVaryingFitter with start/stop columns in call-to-call
    intervals. Covariates are measured at the call that opens each interval.
    Time units: days since 2000-01-01.

    Args:
        df: Counting-process DataFrame (one row per call-to-call interval)
        event_col: Event indicator column (Takeover, Takeover_Uninvited, Takeover_Friendly)
        covariates: List of covariate column names
        title: Model title for output file
        out_file: Path to append results to
        strata: Column name(s) for stratified baseline hazard (None = unstratified)

    Returns:
        Fitted CoxTimeVaryingFitter or None on failure.
    """
    if not LIFELINES_AVAILABLE or CoxTimeVaryingFitter is None:
        print("  ERROR: lifelines not available")
        sys.exit(1)

    print(f"\n  Cox TV: {title}")

    # Validate required columns (B7 fix: start/stop instead of duration)
    required = [START_COL, STOP_COL, "id", event_col] + covariates
    # 'id' = gvkey for entity identification
    actual_required = [START_COL, STOP_COL, event_col] + covariates
    try:
        validate_columns(df, actual_required)
    except RegressionValidationError as e:
        raise ValueError(f"Column validation failed: {e}") from e

    needed_cols = [START_COL, STOP_COL, "gvkey", event_col] + covariates
    if strata is not None:
        strata_cols = [strata] if isinstance(strata, str) else list(strata)
        needed_cols = needed_cols + [c for c in strata_cols if c not in needed_cols]
    needed_cols = [c for c in needed_cols if c in df.columns]
    df_clean = (
        df[needed_cols]
        .dropna(subset=[START_COL, STOP_COL, event_col] + covariates)
        .copy()
    )

    try:
        validate_sample_size(df_clean, min_observations=MIN_OBS)
    except RegressionValidationError as e:
        print(f"  Skipping: {e}")
        return None

    # Count event firms (not rows)
    n_event_firms = (
        int(df_clean.groupby("gvkey")[event_col].max().sum())
        if "gvkey" in df_clean.columns
        else int(df_clean[event_col].sum())
    )
    print(f"  N intervals = {len(df_clean):,}, Event firms = {n_event_firms:,}")

    if n_event_firms < 5:
        print(f"  Skipping: too few event firms ({n_event_firms} < 5)")
        return None

    # Strata sparsity diagnostic
    if strata is not None:
        strata_col = strata if isinstance(strata, str) else strata[0]
        event_by_stratum = df_clean.groupby(strata_col)[event_col].sum()
        sparse_strata = event_by_stratum[event_by_stratum < 5]
        if len(sparse_strata) > 0:
            print(f"  WARNING: {len(sparse_strata)} strata have <5 events: "
                  f"{sparse_strata.to_dict()}")

    try:
        ctv = CoxTimeVaryingFitter()  # type: ignore[call-arg]
        ctv.fit(  # type: ignore[call-arg]
            df_clean,
            id_col="gvkey",
            start_col=START_COL,
            stop_col=STOP_COL,
            event_col=event_col,
            formula=" + ".join(covariates),
            strata=strata,
        )
    except Exception as e:
        print(f"  ERROR: Cox TV failed: {e}", file=sys.stderr)
        return None

    # Compute concordance index for time-varying model
    concordance = compute_concordance_time_varying(ctv, df_clean, event_col)
    if concordance is not None:
        print(f"  Concordance: {concordance:.4f}")

    # Append to output file
    with open(out_file, "a") as fh:
        fh.write(f"\n{'=' * 70}\n{title}\n{'=' * 70}\n")
        fh.write(str(ctv.summary))  # type: ignore[union-attr]
        fh.write(
            f"\nN intervals = {len(df_clean):,}, Event firms = {n_event_firms:,}\n"
        )
        if concordance is not None:
            fh.write(f"Concordance index: {concordance:.4f}\n")

    return ctv


def extract_results(
    cph: Any,
    df_clean_len: int,
    n_events: int,
    model_name: str,
    variant: str,
    event_type: str,
    covariates: List[str],
    concordance: Optional[float] = None,
    control_block: str = "sparse",
    strata: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Extract key coefficient rows from fitted CoxPHFitter."""
    rows = []
    if cph is None:
        return rows

    summary = cph.summary  # type: ignore[union-attr]
    for var in covariates:
        if var in summary.index:
            rows.append(
                {
                    "model": model_name,
                    "variant": variant,
                    "event_type": event_type,
                    "variable": var,
                    "coef": summary.loc[var, "coef"],
                    "exp_coef": summary.loc[var, "exp(coef)"],
                    "se_coef": summary.loc[var, "se(coef)"],
                    "z": summary.loc[var, "z"],
                    "p": summary.loc[var, "p"],
                    "n_firms": df_clean_len,
                    "n_events": n_events,
                    "concordance": concordance
                    if concordance is not None
                    else float("nan"),
                    "control_block": control_block,
                    "strata": strata if strata else "none",
                }
            )
    return rows


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    all_hr_rows: List[Dict[str, Any]],
    diag_rows: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Save hazard ratios and model diagnostics."""
    if all_hr_rows:
        hr_df = pd.DataFrame(all_hr_rows)
        hr_df.to_csv(out_dir / "hazard_ratios.csv", index=False)
        print(f"  Saved: hazard_ratios.csv ({len(hr_df)} rows)")

    if diag_rows:
        diag_df = pd.DataFrame(diag_rows)
        diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False)
        print(f"  Saved: model_diagnostics.csv ({len(diag_df)} rows)")


def generate_report(
    all_hr_rows: List[Dict[str, Any]],
    diag_rows: List[Dict[str, Any]],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report."""
    report_lines = [
        "# H9: Takeover Hazard Results",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Research Question",
        "",
        "Does clarity in speech increase the likelihood of receiving a takeover bid,",
        "especially an UNINVITED bid?",
        "",
        "## Model Structure",
        "",
        "- **PRIMARY STYLE MODELS**: CEO Clarity Score (ClarityCEO)",
        "- **SECONDARY RESIDUAL MODELS**: CEO Residual, Manager Residual",
        "- Model 1 (Cox PH All): All takeovers",
        "- Model 2 (Cox CS Uninvited): Cause-specific Cox — Uninvited (Hostile + Unsolicited)",
        "- Model 3 (Cox CS Friendly): Cause-specific Cox — Friendly (Friendly + Neutral)",
        "",
        "## Financial Controls (Compustat-only)",
        "",
        "- **Sparse block** (all models): Size, BM, Lev, ROA, CashHoldings",
        "- **Expanded robustness** (all families): + SalesGrowth, Intangibility, AssetGrowth",
        "",
        "## Model Diagnostics",
        "",
        "| Model | Variant | Event Type | N Intervals | N Event Firms | Concordance |",
        "|-------|---------|------------|-------------|---------------|-------------|",
    ]
    for d in diag_rows:
        conc = d.get("concordance", "N/A")
        conc_str = f"{conc:.4f}" if isinstance(conc, float) else str(conc)
        report_lines.append(
            f"| {d.get('model')} | {d.get('variant')} | {d.get('event_type')} "
            f"| {d.get('n_intervals', 'N/A'):,} | {d.get('n_event_firms', 'N/A'):,} | {conc_str} |"
        )
    report_lines.append("")

    report_lines += [
        "## Key Coefficients (Clarity Variables)",
        "",
        "| Model | Variant | Variable | HR (exp coef) | p-val |",
        "|-------|---------|----------|---------------|-------|",
    ]
    key_vars = {
        "ClarityCEO",
        "CEO_Clarity_Residual",
        "Manager_Clarity_Residual",
    }
    for row in all_hr_rows:
        if row.get("variable") in key_vars:
            hr = row.get("exp_coef", "N/A")
            pv = row.get("p", "N/A")
            hr_str = f"{hr:.4f}" if isinstance(hr, float) else str(hr)
            pv_str = f"{pv:.4f}" if isinstance(pv, float) else str(pv)
            report_lines.append(
                f"| {row.get('model')} | {row.get('variant')} "
                f"| {row.get('variable')} | {hr_str} | {pv_str} |"
            )
    report_lines.append("")

    report_path = out_dir / "report_h9_takeover.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("  Saved: report_h9_takeover.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "takeover" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H9_Takeover",
        timestamp=timestamp,
    )

    log_path = out_dir / "run_log.txt"
    dual = DualWriter(log_path)
    sys.stdout = dual

    print("=" * 80)
    print("H9: Takeover Hazard Models")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Log dir: {log_dir}")

    if not LIFELINES_AVAILABLE:
        print(
            "ERROR: lifelines package not available. Install with: pip install lifelines"
        )
        sys.exit(1)

    # Load panel
    panel = load_panel(root, panel_path)

    # Track panel file path for manifest
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root / "outputs" / "variables" / "takeover",
            required_file="takeover_panel.parquet",
        )
        panel_file = panel_dir / "takeover_panel.parquet"

    # Main sample + event indicators
    df = prepare_main_sample(panel)

    # ------------------------------------------------------------------
    # Summary Statistics (firm-level survival panel, Main only)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    summary_vars = [
        {"col": v["col"], "label": v["label"]}
        for v in SUMMARY_STATS_VARS
        if v["col"] in df.columns
    ]
    make_summary_stats_table(
        df=df,
        variables=summary_vars,
        sample_names=None,  # Aggregate only (survival panel, Main sample)
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H9 Takeover Hazards",
        label="tab:summary_stats_h9",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    all_hr_rows: List[Dict[str, Any]] = []
    diag_rows: List[Dict[str, Any]] = []

    # Model definitions: (output_file_stem, event_col, model_label, event_type_label)
    model_defs: List[Tuple[str, str, str, str]] = [
        ("cox_ph_all", EVENT_ALL_COL, "Cox PH All", "All"),
        ("cox_cs_uninvited", EVENT_UNINVITED_COL, "Cox CS Uninvited", "Uninvited"),
        ("cox_cs_friendly", EVENT_FRIENDLY_COL, "Cox CS Friendly", "Friendly"),
    ]

    def _run_variant(
        file_stem: str,
        event_col: str,
        model_label: str,
        event_type: str,
        variant_key: str,
        variant_spec: Dict[str, str],
        controls: List[str],
        control_label: str,
        strata: Optional[Any] = None,
    ) -> None:
        """Run a single model variant and collect results."""
        clarity_var = variant_spec["clarity_var"]
        covariates = [clarity_var] + [c for c in controls if c in df.columns]
        covariates = [c for c in covariates if c in df.columns]

        suffix = f" [{control_label}]" if control_label != "sparse" else ""
        title = f"{model_label} — {variant_spec['description']}{suffix}"

        out_file = out_dir / f"{file_stem}.txt"
        ctv = run_cox_tv(df, event_col, covariates, title, out_file, strata=strata)

        if ctv is not None:
            needed = [START_COL, STOP_COL, "gvkey", event_col] + covariates
            needed = [c for c in needed if c in df.columns]
            df_used = df[needed].dropna(
                subset=[START_COL, STOP_COL, event_col] + covariates
            )
            n_intervals = len(df_used)
            n_event_firms = (
                int(df_used.groupby("gvkey")[event_col].max().sum())
                if "gvkey" in df_used.columns
                else int(df_used[event_col].sum())
            )
            concordance = compute_concordance_time_varying(ctv, df_used, event_col)

            var_key_out = (
                f"{variant_key}_{control_label}" if control_label != "sparse" else variant_key
            )
            hr_rows = extract_results(
                ctv,
                n_intervals,
                n_event_firms,
                model_label,
                var_key_out,
                event_type,
                covariates,
                concordance=concordance,
                control_block=control_label,
                strata=strata if strata else None,
            )
            all_hr_rows.extend(hr_rows)

            diag_rows.append(
                {
                    "model": model_label,
                    "variant": var_key_out,
                    "event_type": event_type,
                    "event_col": event_col,
                    "n_intervals": n_intervals,
                    "n_event_firms": n_event_firms,
                    "n_clusters": df_used["gvkey"].nunique()
                    if "gvkey" in df_used.columns
                    else n_intervals,
                    "cluster_var": "gvkey",
                    "concordance": concordance,
                    "control_block": control_label,
                    "strata": strata if strata else "none",
                }
            )
            print(f"  Saved: {file_stem}.txt")
        else:
            print(f"  [{variant_key}] Model not fitted — insufficient data")

    # ---- A. PRIMARY STYLE + B. SECONDARY RESIDUAL (all with sparse controls) ----
    for file_stem, event_col, model_label, event_type in model_defs:
        out_file = out_dir / f"{file_stem}.txt"
        out_file.write_text(f"Generated: {timestamp}\n")

        print(f"\n{'=' * 80}")
        print(f"MODEL: {model_label} (event: {event_col})")
        print("=" * 80)

        for variant_key, variant_spec in MODEL_VARIANTS.items():
            _run_variant(
                file_stem, event_col, model_label, event_type,
                variant_key, variant_spec, SPARSE_CONTROLS, "sparse",
            )

    # ---- C. EXPANDED-CONTROL ROBUSTNESS (all families) ----
    print(f"\n{'=' * 80}")
    print("EXPANDED-CONTROL ROBUSTNESS (all families)")
    print("=" * 80)

    for file_stem, event_col, model_label, event_type in model_defs:
        out_file_expanded = out_dir / f"{file_stem}_expanded.txt"
        out_file_expanded.write_text(f"Generated: {timestamp}\n")

        for variant_key, variant_spec in MODEL_VARIANTS.items():
            _run_variant(
                f"{file_stem}_expanded", event_col, model_label, event_type,
                variant_key, variant_spec, EXPANDED_CONTROLS, "expanded",
            )

    # ---- D. YEAR-STRATIFIED ROBUSTNESS (all variants, sparse) ----
    print(f"\n{'=' * 80}")
    print("YEAR-STRATIFIED ROBUSTNESS (all variants)")
    print("=" * 80)

    for file_stem, event_col, model_label, event_type in model_defs:
        out_file = out_dir / f"{file_stem}_strata_year.txt"
        out_file.write_text(f"Generated: {timestamp}\n")
        for variant_key, variant_spec in MODEL_VARIANTS.items():
            _run_variant(
                f"{file_stem}_strata_year", event_col, model_label, event_type,
                variant_key, variant_spec, SPARSE_CONTROLS, "strata_year",
                strata="year",
            )

    # ---- E. INDUSTRY-STRATIFIED ROBUSTNESS (all variants, sparse) ----
    print(f"\n{'=' * 80}")
    print("INDUSTRY-STRATIFIED ROBUSTNESS (all variants)")
    print("=" * 80)

    for file_stem, event_col, model_label, event_type in model_defs:
        out_file = out_dir / f"{file_stem}_strata_industry.txt"
        out_file.write_text(f"Generated: {timestamp}\n")
        for variant_key, variant_spec in MODEL_VARIANTS.items():
            _run_variant(
                f"{file_stem}_strata_industry", event_col, model_label, event_type,
                variant_key, variant_spec, SPARSE_CONTROLS, "strata_industry",
                strata="ff12_code",
            )

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    save_outputs(all_hr_rows, diag_rows, out_dir)

    # Generate Accounting Review LaTeX table for Cox hazard models
    if all_hr_rows:
        # Variable labels for the table
        var_labels = {
            "ClarityCEO": "ClarityCEO",
            "CEO_Clarity_Residual": "CEO_Clarity_Residual",
            "Manager_Clarity_Residual": "Manager_Clarity_Residual",
            "Size": "Size",
            "BM": "BM",
            "Lev": "Lev",
            "ROA": "ROA",
            "CashHoldings": "CashHoldings",
            "SalesGrowth": "SalesGrowth",
            "Intangibility": "Intangibility",
            "AssetGrowth": "AssetGrowth",
        }
        make_cox_hazard_table(
            results=all_hr_rows,
            variable_labels=var_labels,
            caption="Hazard Ratios from Cox Proportional Hazards Models",
            label="tab:h9_takeover_hazard",
            note=(
                "This table reports hazard ratios from Cox proportional hazards models "
                r"estimating the effect of managerial clarity on takeover probability. "
                "Panel A reports model diagnostics; Panel B reports hazard ratios (HR) "
                "with standard errors in parentheses. "
                r"HR $<$ 1 indicates lower hazard (longer survival); "
                r"HR $>$ 1 indicates higher hazard. "
                "Models estimated on the Main sample (non-financial, non-utility firms). "
                "Sparse controls: Size, BM, Lev, ROA, CashHoldings. "
                "Expanded robustness adds SalesGrowth, Intangibility, AssetGrowth (all families). "
                "Intervals are call-to-call (days since 2000-01-01). "
                "All continuous controls are standardized within each model's estimation sample. "
                r"Variables are winsorized at 1\%/99\% by year at the engine level."
            ),
            output_path=out_dir / "takeover_table.tex",
        )
        print("  Saved: takeover_table.tex")

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_hr_rows, diag_rows, out_dir, duration)

    # Generate sample attrition table
    if diag_rows:
        first_diag = diag_rows[0]
        attrition_stages = [
            ("Full survival panel", len(panel)),
            ("Main sample (ex-Finance/Utility)", len(df)),
            ("After complete-case filter", first_diag.get("n_intervals", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H9 Takeover Hazards")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="h9_econometric",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "takeover_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    print(f"\n  Models completed: {len(diag_rows)}")
    print(f"  Hazard ratio rows: {len(all_hr_rows)}")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

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
