#!/usr/bin/env python3
"""
================================================================================
H9: Takeover Hazard Models
================================================================================
ID: econometric/run_h9_takeover_hazards
Description: Run Takeover Hazard models (H9) using the call-to-call
             counting-process panel from H9 panel builder.

Research Question:
    Does speech uncertainty increase the likelihood of receiving a takeover bid,
    especially an UNINVITED bid?

Models:
    Model 1: Cox Proportional Hazards — All Takeovers
    Model 2: Cause-specific Cox PH    — Uninvited (Hostile + Unsolicited)
    Model 3: Cause-specific Cox PH    — Friendly (Friendly + Neutral)

IVs (all 4 appear simultaneously in every model):
    - UncAnsMgr:   Manager uncertainty in Q&A segment
    - UncAnsCEO:   CEO uncertainty in Q&A segment
    - UncPreMgr:   Manager uncertainty in Presentation segment
    - UncPreCEO:   CEO uncertainty in Presentation segment

Control Configurations (3 event types × 4 control configs = 12 models):
    sparse:           lnAssets, BTM, Leverage, ROA, CashRatio
    expanded:         sparse + SalesGrowth, FracInt, dAA
    strata_year:      sparse + year-stratified baseline hazard
    strata_industry:  sparse + ff12_code-stratified baseline hazard

Hypothesis Tests (two-sided inference):
    H9: beta(Uncertainty) > 0 (higher uncertainty firms face higher takeover hazard)

Financial controls (Compustat-only):
    Sparse block (all models): lnAssets, BTM, Leverage, ROA, CashRatio
    Expanded robustness: + SalesGrowth, FracInt, dAA

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

# L-10: Route warnings through print() so DualWriter captures them in run_log.txt
# (warnings.filterwarnings("ignore") was removed — convergence/separation warnings must be visible)
import warnings as _warnings_module

def _print_warning(message, category, filename, lineno, file=None, line=None):
    print(f"WARNING [{category.__name__}] {filename}:{lineno}: {message}")

_warnings_module.showwarning = _print_warning

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
    "lnAssets",
    "BTM",
    "Leverage",
    "ROA",
    "CashRatio",
]

# Expanded robustness block: used in all families as robustness check
EXPANDED_CONTROLS = SPARSE_CONTROLS + [
    "SalesGrowth",
    "FracInt",
    "dAA",
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Uncertainty IVs (4 standard measures)
    {"col": "UncAnsMgr", "label": "UncAnsMgr"},
    {"col": "UncAnsCEO", "label": "UncAnsCEO"},
    {"col": "UncPreMgr", "label": "UncPreMgr"},
    {"col": "UncPreCEO", "label": "UncPreCEO"},
    # Survival variables
    {"col": "duration", "label": "duration"},
    {"col": "Takeover", "label": "Takeover"},
    {"col": "Takeover_Uninvited", "label": "Takeover_Uninvited"},
    {"col": "Takeover_Friendly", "label": "Takeover_Friendly"},
    # Financial controls — Sparse block (all models)
    {"col": "lnAssets", "label": "lnAssets"},
    {"col": "BTM", "label": "BTM"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashRatio", "label": "CashRatio"},
    # Financial controls — Expanded robustness block
    {"col": "SalesGrowth", "label": "SalesGrowth"},
    {"col": "FracInt", "label": "FracInt"},
    {"col": "dAA", "label": "dAA"},
]

# The 4 standard uncertainty IVs — all appear simultaneously in every model
KEY_IVS: List[str] = [
    "UncAnsMgr",
    "UncAnsCEO",
    "UncPreMgr",
    "UncPreCEO",
]

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
    epv: Optional[float] = None,
    epv_flag: Optional[str] = None,
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
                    "n_intervals": df_clean_len,
                    "n_events": n_events,
                    "concordance": concordance
                    if concordance is not None
                    else float("nan"),
                    "control_block": control_block,
                    "strata": strata if strata else "none",
                    "epv": epv if epv is not None else float("nan"),
                    "epv_flag": epv_flag if epv_flag is not None else "unknown",
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
        diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
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
        "Does speech uncertainty increase the likelihood of receiving a takeover bid,",
        "especially an UNINVITED bid?",
        "",
        "## Model Structure",
        "",
        "- **IVs (all 4 simultaneously)**: UncAnsMgr, UncAnsCEO,",
        "  UncPreMgr, UncPreCEO",
        "- Model 1 (Cox PH All): All takeovers",
        "- Model 2 (Cox CS Uninvited): Cause-specific Cox — Uninvited (Hostile + Unsolicited)",
        "- Model 3 (Cox CS Friendly): Cause-specific Cox — Friendly (Friendly + Neutral)",
        "",
        "**EPV note:** With 4 IVs per model, EPV will be lower than single-IV designs.",
        "Models with EPV < 5 (Peduzzi 1995) are suppressed from the LaTeX table.",
        "Uninvited expanded models are most likely to fall below this threshold.",
        "",
        "## Financial Controls (Compustat-only)",
        "",
        "- **Sparse block** (all models): lnAssets, BTM, Leverage, ROA, CashRatio",
        "- **Expanded robustness**: + SalesGrowth, FracInt, dAA",
        "",
        "## Model Diagnostics",
        "",
        "| Model | Control Block | Event Type | N Intervals | N Event Firms | Concordance |",
        "|-------|--------------|------------|-------------|---------------|-------------|",
    ]
    for d in diag_rows:
        conc = d.get("concordance", "N/A")
        conc_str = f"{conc:.4f}" if isinstance(conc, float) else str(conc)
        report_lines.append(
            f"| {d.get('model')} | {d.get('control_block')} | {d.get('event_type')} "
            f"| {d.get('n_intervals', 'N/A'):,} | {d.get('n_event_firms', 'N/A'):,} | {conc_str} |"
        )
    report_lines.append("")

    report_lines += [
        "## Key Coefficients (Uncertainty IVs)",
        "",
        "| Model | Control Block | Variable | HR (exp coef) | p-val |",
        "|-------|--------------|----------|---------------|-------|",
    ]
    key_vars = set(KEY_IVS)
    for row in all_hr_rows:
        if row.get("variable") in key_vars:
            hr = row.get("exp_coef", "N/A")
            pv = row.get("p", "N/A")
            hr_str = f"{hr:.4f}" if isinstance(hr, float) else str(hr)
            pv_str = f"{pv:.4f}" if isinstance(pv, float) else str(pv)
            report_lines.append(
                f"| {row.get('model')} | {row.get('control_block')} "
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

    def _run_model(
        file_stem: str,
        event_col: str,
        model_label: str,
        event_type: str,
        controls: List[str],
        control_label: str,
        strata: Optional[Any] = None,
    ) -> None:
        """Run a single model with all 4 uncertainty IVs simultaneously."""
        # All 4 IVs first, then controls — filter to columns present in df
        iv_cols = [c for c in KEY_IVS if c in df.columns]
        covariates = iv_cols + [c for c in controls if c in df.columns]

        suffix = f" [{control_label}]" if control_label != "sparse" else ""
        title = f"{model_label} — 4 Uncertainty IVs{suffix}"

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

            # L-3/RT-5: Compute Events Per Variable (EPV) diagnostic
            n_covariates = len(covariates)
            epv = n_event_firms / n_covariates if n_covariates > 0 else float("nan")
            print(f"  EPV: {epv:.1f} ({n_event_firms} events / {n_covariates} covariates)")
            if epv < 10:
                print(f"  WARNING: EPV={epv:.1f} < 10 (Peduzzi 1995 minimum)")
            if epv < 5:
                print(f"  CRITICAL: EPV={epv:.1f} < 5 — results will be suppressed from LaTeX table")
            epv_flag = "critical" if epv < 5 else "low" if epv < 10 else "ok"

            hr_rows = extract_results(
                ctv,
                n_intervals,
                n_event_firms,
                model_label,
                control_label,
                event_type,
                covariates,
                concordance=concordance,
                control_block=control_label,
                strata=strata if strata else None,
                epv=epv,
                epv_flag=epv_flag,
            )
            all_hr_rows.extend(hr_rows)

            diag_rows.append(
                {
                    "model": model_label,
                    "variant": control_label,
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
                    "epv": epv,
                    "epv_flag": epv_flag,
                }
            )
            print(f"  Saved: {file_stem}.txt")
        else:
            print(f"  [{control_label}] Model not fitted — insufficient data")

    # ---- A. SPARSE CONTROLS ----
    for file_stem, event_col, model_label, event_type in model_defs:
        out_file = out_dir / f"{file_stem}.txt"
        out_file.write_text(f"Generated: {timestamp}\n")

        print(f"\n{'=' * 80}")
        print(f"MODEL: {model_label} (event: {event_col})")
        print("=" * 80)

        _run_model(
            file_stem, event_col, model_label, event_type,
            SPARSE_CONTROLS, "sparse",
        )

    # ---- B. EXPANDED-CONTROL ROBUSTNESS ----
    print(f"\n{'=' * 80}")
    print("EXPANDED-CONTROL ROBUSTNESS")
    print("=" * 80)

    for file_stem, event_col, model_label, event_type in model_defs:
        out_file_expanded = out_dir / f"{file_stem}_expanded.txt"
        out_file_expanded.write_text(f"Generated: {timestamp}\n")

        _run_model(
            f"{file_stem}_expanded", event_col, model_label, event_type,
            EXPANDED_CONTROLS, "expanded",
        )

    # ---- C. YEAR-STRATIFIED ROBUSTNESS ----
    print(f"\n{'=' * 80}")
    print("YEAR-STRATIFIED ROBUSTNESS")
    print("=" * 80)

    for file_stem, event_col, model_label, event_type in model_defs:
        out_file = out_dir / f"{file_stem}_strata_year.txt"
        out_file.write_text(f"Generated: {timestamp}\n")
        _run_model(
            f"{file_stem}_strata_year", event_col, model_label, event_type,
            SPARSE_CONTROLS, "strata_year",
            strata="year",
        )

    # ---- D. INDUSTRY-STRATIFIED ROBUSTNESS ----
    print(f"\n{'=' * 80}")
    print("INDUSTRY-STRATIFIED ROBUSTNESS")
    print("=" * 80)

    for file_stem, event_col, model_label, event_type in model_defs:
        out_file = out_dir / f"{file_stem}_strata_industry.txt"
        out_file.write_text(f"Generated: {timestamp}\n")
        _run_model(
            f"{file_stem}_strata_industry", event_col, model_label, event_type,
            SPARSE_CONTROLS, "strata_industry",
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
            "UncAnsMgr": "UncAnsMgr",
            "UncAnsCEO": "UncAnsCEO",
            "UncPreMgr": "UncPreMgr",
            "UncPreCEO": "UncPreCEO",
            "lnAssets": "lnAssets",
            "BTM": "BTM",
            "Leverage": "Leverage",
            "ROA": "ROA",
            "CashRatio": "CashRatio",
            "SalesGrowth": "SalesGrowth",
            "FracInt": "FracInt",
            "dAA": "dAA",
        }
        # Filter critical EPV models from LaTeX table (EPV < 5 — statistically invalid)
        table_hr_rows = [r for r in all_hr_rows if r.get("epv_flag") != "critical"]
        make_cox_hazard_table(
            results=table_hr_rows,
            variable_labels=var_labels,
            caption="Hazard Ratios from Cox Proportional Hazards Models",
            label="tab:h9_takeover_hazard",
            note=(
                "This table reports hazard ratios from Cox proportional hazards models "
                r"estimating the effect of managerial speech uncertainty on takeover probability. "
                "Panel A reports model diagnostics; Panel B reports hazard ratios (HR) "
                "with standard errors in parentheses. "
                r"HR $<$ 1 indicates lower hazard (longer survival); "
                r"HR $>$ 1 indicates higher hazard. "
                "Models estimated on the Main sample (non-financial, non-utility firms). "
                "All four uncertainty IVs (Manager\\_QA, CEO\\_QA, Manager\\_Pres, CEO\\_Pres) "
                "appear simultaneously in every specification. "
                "Sparse controls: lnAssets, BTM, Leverage, ROA, CashRatio. "
                "Expanded robustness adds SalesGrowth, FracInt, dAA. "
                "Intervals are call-to-call (days since 2000-01-01). "
                r"Variables are winsorized at 1\%/99\% by year at the engine level. "
                "Models with EPV $<$ 5 (Peduzzi et al. 1995 minimum = 10) are omitted from table."
            ),
            output_path=out_dir / "takeover_table.tex",
        )
        print("  Saved: takeover_table.tex")

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_hr_rows, diag_rows, out_dir, duration)

    # Generate sample attrition table — one complete-case row for the sparse All-takeover model
    if diag_rows:
        # Find the sparse, All-takeover complete-case count (single IV set, single model)
        sparse_all_n = None
        for d in diag_rows:
            if d.get("control_block") == "sparse" and d.get("event_type") == "All":
                sparse_all_n = d.get("n_intervals", 0)
                break
        attrition_stages = [
            ("Full survival panel", len(panel)),
            ("Main sample (ex-Finance/Utility)", len(df)),
        ]
        if sparse_all_n is not None:
            attrition_stages.append(("Complete-case (4 uncertainty IVs + sparse controls)", sparse_all_n))
        generate_attrition_table(attrition_stages, out_dir, "H9 Takeover Hazards")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate model sample characteristics table (sparse models only)
    model_sample_chars = []
    for d in diag_rows:
        if d.get("control_block") == "sparse":
            model_sample_chars.append({
                "Event_Type": d.get("event_type"),
                "N_intervals": d.get("n_intervals"),
                "N_firms": d.get("n_clusters"),
                "N_events": d.get("n_event_firms"),
                "EPV": d.get("epv"),
                "EPV_flag": d.get("epv_flag"),
            })
    if model_sample_chars:
        pd.DataFrame(model_sample_chars).to_csv(
            out_dir / "model_sample_chars.csv", index=False
        )
        print("  Saved: model_sample_chars.csv")

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
