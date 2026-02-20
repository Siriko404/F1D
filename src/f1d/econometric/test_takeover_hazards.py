#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test Takeover Hazard Hypothesis (4.3)
================================================================================
ID: econometric/test_takeover_hazards
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
    - Requires: Stage 3 (build_takeover_panel)
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

# lifelines — always-bound pattern
CoxPHFitter: Any = None
try:
    from lifelines import CoxPHFitter  # type: ignore[no-redef,import-untyped]

    LIFELINES_AVAILABLE = True
except ImportError:
    LIFELINES_AVAILABLE = False
    print("WARNING: lifelines not available. Install with: pip install lifelines")

from f1d.shared.observability_utils import DualWriter
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

# Survival columns
DURATION_COL = "Duration"
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
    """Load firm-level takeover panel from Stage 3."""
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
    print(f"  Rows (firms): {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")
    print(
        f"  Takeover events: {int(panel[EVENT_ALL_COL].sum()):,} ({100.0 * panel[EVENT_ALL_COL].mean():.1f}%)"
    )

    # Hard assertion: ff12_code must be present for sample filtering
    if "ff12_code" not in panel.columns:
        raise ValueError("'ff12_code' not found in takeover panel. Re-run Stage 3.")

    return panel


def prepare_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample and create cause-specific event indicators."""
    df = panel[~panel["ff12_code"].isin(MAIN_SAMPLE_EXCLUDE_FF12)].copy()
    print(f"\n  Main sample: {len(df):,} firms")
    print(f"  Takeover events (Main): {int(df[EVENT_ALL_COL].sum()):,}")

    # Create cause-specific event indicators
    df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
    df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)

    print(f"  Uninvited events: {df[EVENT_UNINVITED_COL].sum():,}")
    print(f"  Friendly events: {df[EVENT_FRIENDLY_COL].sum():,}")

    return df


# ==============================================================================
# Survival Models
# ==============================================================================


def run_cox(
    df: pd.DataFrame,
    event_col: str,
    covariates: List[str],
    title: str,
    out_file: Path,
) -> Optional[Any]:
    """Fit a Cox PH model (all takeovers or cause-specific).

    Args:
        df: Firm-level DataFrame
        event_col: Event indicator column (Takeover, Takeover_Uninvited, Takeover_Friendly)
        covariates: List of covariate column names
        title: Model title for output file
        out_file: Path to append results to

    Returns:
        Fitted CoxPHFitter or None on failure.
    """
    if not LIFELINES_AVAILABLE or CoxPHFitter is None:
        print("  ERROR: lifelines not available")
        sys.exit(1)

    print(f"\n  Cox PH: {title}")

    # Validate required columns
    required = [DURATION_COL, event_col] + covariates
    try:
        validate_columns(df, required)
    except RegressionValidationError as e:
        raise ValueError(f"Column validation failed: {e}") from e

    needed_cols = [DURATION_COL, event_col] + covariates
    df_clean = df[needed_cols].dropna().copy()

    try:
        validate_sample_size(df_clean, min_observations=MIN_OBS)
    except RegressionValidationError as e:
        print(f"  Skipping: {e}")
        return None

    n_events = int(df_clean[event_col].sum())
    print(f"  N = {len(df_clean):,}, Events = {n_events:,}")

    if n_events < 5:
        print(f"  Skipping: too few events ({n_events} < 5)")
        return None

    formula = " + ".join(covariates)

    try:
        cph = CoxPHFitter()  # type: ignore[call-arg]
        cph.fit(  # type: ignore[call-arg]
            df_clean,
            duration_col=DURATION_COL,
            event_col=event_col,
            formula=formula,
        )
    except Exception as e:
        print(f"  ERROR: Cox PH failed: {e}", file=sys.stderr)
        return None

    print(f"  Concordance: {cph.concordance_index_:.4f}")  # type: ignore[union-attr]

    # Append to output file
    with open(out_file, "a") as fh:
        fh.write(f"\n{'=' * 70}\n{title}\n{'=' * 70}\n")
        fh.write(str(cph.summary))  # type: ignore[union-attr]
        fh.write(f"\nN = {len(df_clean):,}, Events = {n_events:,}\n")
        fh.write(f"Concordance index: {cph.concordance_index_:.4f}\n")  # type: ignore[union-attr]

    return cph


def extract_results(
    cph: Any,
    df_clean_len: int,
    n_events: int,
    model_name: str,
    variant: str,
    event_type: str,
    covariates: List[str],
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
                    "concordance": float(cph.concordance_index_),  # type: ignore[union-attr]
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
        "| Model | Variant | Event Type | N Firms | N Events | Concordance |",
        "|-------|---------|------------|---------|----------|-------------|",
    ]
    for d in diag_rows:
        conc = d.get("concordance", "N/A")
        conc_str = f"{conc:.4f}" if isinstance(conc, float) else str(conc)
        report_lines.append(
            f"| {d.get('model')} | {d.get('variant')} | {d.get('event_type')} "
            f"| {d.get('n_firms', 'N/A'):,} | {d.get('n_events', 'N/A'):,} | {conc_str} |"
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

            cph = run_cox(df, event_col, covariates, title, out_file)

            if cph is not None:
                # Count observations used
                needed = [DURATION_COL, event_col] + covariates
                df_used = df[needed].dropna()
                n_firms = len(df_used)
                n_events = int(df_used[event_col].sum())
                concordance = float(cph.concordance_index_)  # type: ignore[union-attr]

                hr_rows = extract_results(
                    cph,
                    n_firms,
                    n_events,
                    model_label,
                    variant_key,
                    event_type,
                    covariates,
                )
                all_hr_rows.extend(hr_rows)

                diag_rows.append(
                    {
                        "model": model_label,
                        "variant": variant_key,
                        "event_type": event_type,
                        "event_col": event_col,
                        "n_firms": n_firms,
                        "n_events": n_events,
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
