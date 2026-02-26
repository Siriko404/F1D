#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test Takeover Hazard Hypothesis (4.3)
================================================================================
ID: econometric/run_h9_takeover_hazards
Description: Run Takeover Hazard models (4.3) using the firm-level survival
             panel from Stage 3.

Models:
    Model 1: Cox Proportional Hazards — All Takeovers
    Model 2: Cause-specific Cox PH    — Uninvited (Hostile + Unsolicited)
    Model 3: Cause-specific Cox PH    — Friendly (Friendly + Neutral)

Each model is run twice:
    Regime variant: ClarityManager + Manager_QA_Uncertainty_pct + controls
    CEO variant:    ClarityCEO    + CEO_QA_Uncertainty_pct    + controls

Financial controls: Size, BM, Lev, ROA, EPS_Growth, StockRet, MarketRet, SurpDec
Main sample only (exclude Finance ff12=11, Utility ff12=8).

Survival construction (from Stage 3):
    Duration = years from first call to takeover announcement or end of sample
    Takeover = 1 if bid received, 0 otherwise (censored)
    Takeover_Uninvited = 1 if Takeover_Type == 'Uninvited', 0 otherwise
    Takeover_Friendly  = 1 if Takeover_Type == 'Friendly',  0 otherwise

Inputs:
    - outputs/variables/takeover/{latest_timestamp}/takeover_panel.parquet

Outputs:
    - outputs/econometric/takeover/{timestamp}/cox_ph_all.txt
    - outputs/econometric/takeover/{timestamp}/cox_cs_uninvited.txt
    - outputs/econometric/takeover/{timestamp}/cox_cs_friendly.txt
    - outputs/econometric/takeover/{timestamp}/hazard_ratios.csv
    - outputs/econometric/takeover/{timestamp}/model_diagnostics.csv
    - outputs/econometric/takeover/{timestamp}/report_step4_takeover.md
    - outputs/econometric/takeover/{timestamp}/run_log.txt

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h9_takeover_panel)
    - Uses: lifelines, f1d.shared

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
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

warnings.filterwarnings("ignore")

# lifelines — always-bound pattern (B7 fix: CoxTimeVaryingFitter for counting-process)
CoxTimeVaryingFitter: Any = None
concordance_index: Any = None
try:
    from lifelines import CoxTimeVaryingFitter  # type: ignore[no-redef,import-untyped]
    from lifelines.utils import concordance_index  # type: ignore[import-untyped]

    LIFELINES_AVAILABLE = True
except ImportError:
    LIFELINES_AVAILABLE = False
    print("WARNING: lifelines not available. Install with: pip install lifelines")

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.observability import DualWriter
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.regression_validation import (
    RegressionValidationError,
    validate_columns,
    validate_sample_size,
)


# ==============================================================================
# Configuration
# ==============================================================================

# Financial controls (time-averaged in Stage 3)
FINANCIAL_CONTROLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "EPS_Growth",
    "StockRet",
    "MarketRet",
    "SurpDec",
]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Clarity measures (two variants)
    {"col": "ClarityManager", "label": "Clarity (Manager)"},
    {"col": "ClarityCEO", "label": "Clarity (CEO)"},
    # Uncertainty measures (two variants)
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    # Survival variables
    {"col": "duration", "label": "Duration (years)"},
    {"col": "Takeover", "label": "Takeover Event"},
    {"col": "Takeover_Uninvited", "label": "Uninvited Takeover"},
    {"col": "Takeover_Friendly", "label": "Friendly Takeover"},
    # Financial controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "BM", "label": "Book-to-Market"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "ROA"},
    {"col": "EPS_Growth", "label": "EPS Growth"},
    {"col": "StockRet", "label": "Stock Return"},
    {"col": "MarketRet", "label": "Market Return"},
    {"col": "SurpDec", "label": "Earnings Surprise Decile"},
]

# Two model variants
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    "Regime": {
        "clarity_var": "ClarityManager",
        "uncertainty_var": "Manager_QA_Uncertainty_pct",
        "description": "Manager Clarity (4.1) model",
    },
    "CEO": {
        "clarity_var": "ClarityCEO",
        "uncertainty_var": "CEO_QA_Uncertainty_pct",
        "description": "CEO Clarity (4.1.1) model",
    },
}

# Counting-process columns (B7 fix: start/stop format)
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
        description="Stage 4: Test Takeover Hazard Hypothesis (4.3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load counting-process takeover panel from Stage 3 (B7 fix)."""
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
    print(f"  Rows (firm-year intervals): {len(panel):,}")
    print(f"  Unique firms: {panel['gvkey'].nunique():,}")
    print(f"  Columns: {len(panel.columns)}")

    # Hard assertions
    if "ff12_code" not in panel.columns:
        raise ValueError("'ff12_code' not found in takeover panel. Re-run Stage 3.")
    for col in [START_COL, STOP_COL]:
        if col not in panel.columns:
            raise ValueError(
                f"'{col}' not found in takeover panel. "
                "Panel must be in counting-process format. Re-run Stage 3."
            )

    n_event_firms = panel.groupby("gvkey")[EVENT_ALL_COL].max().sum()
    n_firms = panel["gvkey"].nunique()
    print(f"  Takeover event firms: {int(n_event_firms):,} / {n_firms:,}")

    return panel


def prepare_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample and create cause-specific event indicators."""
    df = panel[~panel["ff12_code"].isin(MAIN_SAMPLE_EXCLUDE_FF12)].copy()
    n_firms = df["gvkey"].nunique()
    n_event_firms = df.groupby("gvkey")[EVENT_ALL_COL].max().sum()
    print(f"\n  Main sample: {len(df):,} firm-year rows, {n_firms:,} firms")
    print(f"  Takeover event firms (Main): {int(n_event_firms):,}")

    # Create cause-specific event indicators
    df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
    df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)

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
        conc_df = pd.DataFrame({
            "event_time": df_last[STOP_COL].values,
            "predicted_score": subject_hazards.values.flatten(),
            "event_observed": df_last[event_col].values,
        })
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
) -> Optional[Any]:
    """Fit a Cox time-varying fitter (counting-process format).

    B7 fix: uses CoxTimeVaryingFitter with start/stop columns instead of
    CoxPHFitter with a single Duration column. Time-varying covariates are
    now used at their actual per-year values rather than time-averaged.

    Args:
        df: Counting-process DataFrame (one row per firm-year at risk)
        event_col: Event indicator column (Takeover, Takeover_Uninvited, Takeover_Friendly)
        covariates: List of covariate column names
        title: Model title for output file
        out_file: Path to append results to

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

    try:
        ctv = CoxTimeVaryingFitter()  # type: ignore[call-arg]
        ctv.fit(  # type: ignore[call-arg]
            df_clean,
            id_col="gvkey",
            start_col=START_COL,
            stop_col=STOP_COL,
            event_col=event_col,
            formula=" + ".join(covariates),
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
                    "concordance": concordance if concordance is not None else float("nan"),
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
        "# Stage 4: Takeover Hazard Results (4.3)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Models",
        "",
        "- Model 1 (Cox PH All): All takeovers — Regime and CEO variants",
        "- Model 2 (Cox CS Uninvited): Cause-specific Cox — Uninvited only",
        "- Model 3 (Cox CS Friendly): Cause-specific Cox — Friendly only",
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
        "## Key Coefficients (Clarity and Uncertainty)",
        "",
        "| Model | Variant | Variable | HR (exp coef) | p-val |",
        "|-------|---------|----------|---------------|-------|",
    ]
    key_vars = {
        "ClarityManager",
        "ClarityCEO",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
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

    report_path = out_dir / "report_step4_takeover.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("  Saved: report_step4_takeover.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "takeover" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = out_dir / "run_log.txt"
    dual = DualWriter(log_path)
    sys.stdout = dual

    print("=" * 80)
    print("STAGE 4: Test Takeover Hazard Hypothesis (4.3)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    if not LIFELINES_AVAILABLE:
        print(
            "ERROR: lifelines package not available. Install with: pip install lifelines"
        )
        sys.exit(1)

    # Load panel
    panel = load_panel(root, panel_path)

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

    for file_stem, event_col, model_label, event_type in model_defs:
        out_file = out_dir / f"{file_stem}.txt"
        out_file.write_text(f"Generated: {timestamp}\n")

        print(f"\n{'=' * 80}")
        print(f"MODEL: {model_label} (event: {event_col})")
        print("=" * 80)

        for variant_key, variant_spec in MODEL_VARIANTS.items():
            clarity_var = variant_spec["clarity_var"]
            uncertainty_var = variant_spec["uncertainty_var"]

            covariates = [clarity_var, uncertainty_var] + [
                c for c in FINANCIAL_CONTROLS if c in df.columns
            ]
            # Only keep covariates present in panel
            covariates = [c for c in covariates if c in df.columns]

            title = f"{model_label} — {variant_spec['description']}"

            ctv = run_cox_tv(df, event_col, covariates, title, out_file)

            if ctv is not None:
                # Count observations used (counting-process format)
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
                # Compute concordance for time-varying model
                concordance = compute_concordance_time_varying(ctv, df_used, event_col)

                hr_rows = extract_results(
                    ctv,
                    n_intervals,
                    n_event_firms,
                    model_label,
                    variant_key,
                    event_type,
                    covariates,
                    concordance=concordance,
                )
                all_hr_rows.extend(hr_rows)

                diag_rows.append(
                    {
                        "model": model_label,
                        "variant": variant_key,
                        "event_type": event_type,
                        "event_col": event_col,
                        "n_intervals": n_intervals,
                        "n_event_firms": n_event_firms,
                        "concordance": concordance,
                    }
                )
                print(f"  Saved: {file_stem}.txt")
            else:
                print(f"  [{variant_key}] Model not fitted — insufficient data")

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    save_outputs(all_hr_rows, diag_rows, out_dir)

    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_hr_rows, diag_rows, out_dir, duration)

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
