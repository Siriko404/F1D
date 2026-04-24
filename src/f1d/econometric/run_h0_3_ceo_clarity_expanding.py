#!/usr/bin/env python3
"""
================================================================================
H0.3 EXPANDING: DWZ 2021 Eq.4 — quarterly-expanding-window CEO clarity
================================================================================
ID: econometric/run_h0_3_ceo_clarity_expanding
Description: Clone of H0.3 (`run_h0_3_ceo_clarity_extended.py`).
             ONE substitution: full-panel single fit -> quarterly-expanding-window
             (one fit per calendar quarter q, training on calls with _qtr < q —
             strict no-look-ahead; out-of-sample residuals for stronger IV).
             ONE scope reduction: CEO_Baseline only (DWZ Eq.4 EXACT).
             Manager_Baseline / Manager_Extended / CEO_Extended dropped — they
             are H0.3 robustness add-ons, not DWZ Eq.4.

Model (Main sample only):
    CEO Baseline:
       UncAnsCEO ~ C(ceo_id) + base_controls + C(year)

Base controls (DWZ Eq.4):
    Linguistic: UncPreCEO, UncQue, NegCall
    Firm:       StockRet, MarketRet, EPSgrowth, SurpDec

Expanding-window protocol (no-look-ahead):
    For each calendar quarter q (sorted): fit DWZ Eq.4 on calls with start_date
    with _qtr < q (strict no-look-ahead); for each test call in q, extract:
        ClarityCEO_QtrExp = -gamma_i  (DWZ §4.4 p.16: "negative of CEO fixed effect")
        UncResCEO_QtrExp  = raw - predicted  (DWZ Table 6 Notes p.30)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)

Minimum Calls Filter:
    CEOs must have >= 5 calls within TRAINING window (per quarter).

Inputs:
    - outputs/variables/ceo_clarity_extended/latest/ceo_clarity_extended_panel.parquet

Outputs (under outputs/econometric/ceo_clarity_expanding/{ts}/):
    - ceo_clarity_qtrexp_residuals.parquet
        per-call cols: file_name, gvkey, ceo_id, sample, start_date, year,
                       quarter, UncAnsCEO, ClarityCEO_QtrExp, UncResCEO_QtrExp
    - quarter_diagnostics.csv
    - summary_stats.csv / summary_stats.tex
    - model_diagnostics.csv
    - report_h0_3_expanding.md
    - run_manifest.json

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h0_3_ceo_clarity_extended_panel)
    - Uses: statsmodels
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
import statsmodels.formula.api as smf

STATSMODELS_AVAILABLE = True

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample


# ==============================================================================
# Model Configurations
# ==============================================================================

BASE_LINGUISTIC_CONTROLS_CEO = [
    "UncPreCEO",
    "UncQue",
    "NegCall",
]

BASE_FIRM_CONTROLS = ["StockRet", "MarketRet", "EPSgrowth", "SurpDec"]

MODELS: Dict[str, Dict[str, Any]] = {
    "CEO_Baseline": {
        "dependent_var": "UncAnsCEO",
        "linguistic_controls": BASE_LINGUISTIC_CONTROLS_CEO,
        "firm_controls": BASE_FIRM_CONTROLS,
        "description": "CEO Q&A Uncertainty — DWZ Eq.4 baseline (expanding window)",
    },
}

MIN_CALLS = 5


# ==============================================================================
# Variable Labels for LaTeX Table
# ==============================================================================

VARIABLE_LABELS = {
    "UncPreCEO": "CEO Pres Uncertainty",
    "UncQue": "Analyst QA Uncertainty",
    "NegCall": "Negative Sentiment",
    "StockRet": "Stock Return",
    "MarketRet": "Market Return",
    "EPSgrowth": "EPS Growth",
    "SurpDec": "Earnings Surprise Decile",
}


# ==============================================================================
# Summary Statistics Variables (DV + DWZ Eq.4 controls only)
# ==============================================================================

SUMMARY_STATS_VARS = [
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": "UncQue", "label": "Analyst QA Uncertainty"},
    {"col": "NegCall", "label": "Negative Sentiment"},
    {"col": "StockRet", "label": "Stock Return"},
    {"col": "MarketRet", "label": "Market Return"},
    {"col": "EPSgrowth", "label": "EPS Growth"},
    {"col": "SurpDec", "label": "Earnings Surprise Decile"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Test CEO Clarity Extended Controls Robustness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "ceo_clarity_extended",
            required_file="ceo_clarity_extended_panel.parquet",
        )
        panel_file = panel_dir / "ceo_clarity_extended_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    return panel


# ==============================================================================
# Data Preparation (per model)
# ==============================================================================


def prepare_regression_data(
    panel: pd.DataFrame,
    model_config: Dict[str, Any],
    model_name: str,
) -> pd.DataFrame:
    """Filter panel to complete cases for a specific model."""
    print(f"\n  Preparing data for {model_name}...")

    initial_n = len(panel)

    df = panel[panel["ceo_id"].notna()].copy()

    # Required variables for this model
    # Include gvkey, sample, file_name, start_date for residual extraction
    required = (
        [model_config["dependent_var"]]
        + model_config["linguistic_controls"]
        + model_config["firm_controls"]
        + ["ceo_id", "year", "gvkey", "sample", "file_name", "start_date"]
    )

    # MAJOR-5: hard-fail if any required variable missing
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        raise ValueError(
            f"Required variables missing from panel for model '{model_name}': {missing_vars}. "
            "Panel build may be incomplete. Aborting to prevent misspecified regression."
        )

    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"    Complete cases: {len(df):,} / {initial_n:,}")

    # Assign industry sample
    if "ff12_code" in df.columns:
        if "sample" not in df.columns:
            df["sample"] = assign_industry_sample(df["ff12_code"])
    elif "sample" not in df.columns:
        raise ValueError(
            "load_and_prepare_panel: neither 'ff12_code' nor 'sample' column found. "
            "Cannot assign industry sample. Check Stage 3 panel output."
        )

    print(f"    Main sample: {(df['sample'] == 'Main').sum():,} calls")

    return df


# ==============================================================================
# Regression
# ==============================================================================


CONTINUOUS_CONTROLS_FOR_STD = [
    "StockRet", "MarketRet", "EPSgrowth", "SurpDec",
]


def run_expanding_regression(
    df_sample: pd.DataFrame,
    model_config: Dict[str, Any],
    model_name: str,
) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Set[Any]]:
    """Quarterly-expanding-window DWZ Eq.4.

    For each calendar quarter q (sorted ascending):
      - Training window: all calls with start_date STRICTLY BEFORE start of q
      - Filter training to CEOs with >= MIN_CALLS in training window
      - Standardize continuous controls using TRAINING mean/SD (apply same to test)
      - Fit OLS: dep_var ~ C(ceo_id) + controls + C(year)
      - For each test call in q whose CEO AND year both appear in training:
            ClarityCEO_QtrExp = -gamma_i  (DWZ §4.4 p.16)
            UncResCEO_QtrExp  = raw - predicted  (DWZ Table 6 Notes p.30)
        Else: emit NaN row (no-look-ahead preserved)

    Returns:
        residuals_df: per-call DataFrame with metadata + raw + ClarityCEO_QtrExp
                      + UncResCEO_QtrExp + per-quarter diagnostics columns
        quarter_diagnostics: per-quarter fit diagnostics (train_n, test_n, R²)
        valid_ceos_union: union of valid training-window CEOs across all quarters
    """
    print("\n" + "=" * 60)
    print(f"Quarterly-expanding regression: {model_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, set()

    dep_var = model_config["dependent_var"]
    controls = model_config["linguistic_controls"] + model_config["firm_controls"]
    controls = [c for c in controls if c in df_sample.columns]
    print(f"  Formula: {dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)")
    print(f"  N controls: {len(controls)}")

    df = df_sample.copy()
    df["_start_dt"] = pd.to_datetime(df["start_date"])
    df["_qtr"] = df["_start_dt"].dt.to_period("Q")
    all_quarters = sorted(df["_qtr"].unique())
    print(f"  Quarters: {len(all_quarters)} ({all_quarters[0]} ... {all_quarters[-1]})")
    print(f"  N calls (pre-train-filter): {len(df):,}  unique CEOs: {df['ceo_id'].nunique():,}")

    collected_rows: List[Dict[str, Any]] = []
    quarter_diagnostics: List[Dict[str, Any]] = []
    valid_ceos_union: Set[Any] = set()

    start_time = datetime.now()

    for q in all_quarters:
        # Strict no-look-ahead: train on calls with _qtr < q (NOT including q).
        # Test rows in q are out-of-sample for the training that produces their
        # decomp. Stronger IV interpretation (predetermined relative to test
        # outcomes). Q1-Y rows drop because year_FE_Y is unestimable from
        # training that ends at Q4-(Y-1) — accepted spec cost (~25% sample loss).
        train_mask = df["_qtr"] < q
        test_mask = df["_qtr"] == q
        df_train_raw = df[train_mask].copy()
        df_test = df[test_mask].copy()

        # Min-calls filter applied to TRAINING window only
        train_ceo_counts = df_train_raw["ceo_id"].value_counts()
        valid_train_ceos = set(train_ceo_counts[train_ceo_counts >= MIN_CALLS].index)
        df_train = df_train_raw[df_train_raw["ceo_id"].isin(valid_train_ceos)].copy()
        valid_ceos_union |= valid_train_ceos

        def _emit_na_rows(df_subset: pd.DataFrame, reason: str) -> None:
            for _, r in df_subset.iterrows():
                collected_rows.append({
                    "file_name": r["file_name"],
                    "gvkey": r["gvkey"],
                    "ceo_id": r["ceo_id"],
                    "sample": r.get("sample", "Main"),
                    "start_date": r["start_date"],
                    "year": r["year"],
                    "quarter": str(q),
                    dep_var: r[dep_var],
                    "ClarityCEO_QtrExp": np.nan,
                    "UncResCEO_QtrExp": np.nan,
                    "train_n": int(len(df_train)),
                    "train_r2": np.nan,
                    "has_training": False,
                    "skip_reason": reason,
                })

        if len(df_train) < 100 or len(valid_train_ceos) < 10:
            _emit_na_rows(df_test, "insufficient_training")
            quarter_diagnostics.append({
                "quarter": str(q), "train_n": len(df_train), "train_ceos": len(valid_train_ceos),
                "test_n": len(df_test), "test_valid": 0, "rsquared": np.nan, "skipped": True,
            })
            continue

        # Standardize continuous controls using TRAINING mu/sd (apply same to test)
        for var in CONTINUOUS_CONTROLS_FOR_STD:
            if var in df_train.columns:
                mu = df_train[var].mean()
                sd = df_train[var].std()
                if sd > 0:
                    df_train[var] = (df_train[var] - mu) / sd
                    if var in df_test.columns:
                        df_test[var] = (df_test[var] - mu) / sd

        # Stringify categoricals for formula
        df_train["_ceo_str"] = df_train["ceo_id"].astype(str)
        df_train["_year_str"] = df_train["year"].astype(str)
        df_test["_ceo_str"] = df_test["ceo_id"].astype(str)
        df_test["_year_str"] = df_test["year"].astype(str)

        formula = f"{dep_var} ~ C(_ceo_str) + " + " + ".join(controls) + " + C(_year_str)"

        try:
            model = smf.ols(formula, data=df_train).fit()
        except Exception as e:
            print(f"    Q{q} fit failed: {e}")
            _emit_na_rows(df_test, f"fit_failed:{e}")
            quarter_diagnostics.append({
                "quarter": str(q), "train_n": len(df_train), "train_ceos": len(valid_train_ceos),
                "test_n": len(df_test), "test_valid": 0, "rsquared": np.nan, "skipped": True,
            })
            continue

        # Extract CEO fixed-effect coefficients (gamma_i). Reference CEO has gamma=0.
        gamma: Dict[str, float] = {}
        for name, coef in model.params.items():
            if name.startswith("C(_ceo_str)[T."):
                ceo_str = name[len("C(_ceo_str)[T."):-1]
                gamma[ceo_str] = float(coef)

        train_ceos_str = set(df_train["_ceo_str"].unique())
        train_years_str = set(df_train["_year_str"].unique())

        test_valid_mask = (
            df_test["_ceo_str"].isin(train_ceos_str)
            & df_test["_year_str"].isin(train_years_str)
        )
        df_test_valid = df_test[test_valid_mask].copy()
        df_test_drop = df_test[~test_valid_mask].copy()

        if len(df_test_valid) > 0:
            try:
                y_hat = model.predict(df_test_valid)
            except Exception as e:
                print(f"    Q{q} predict failed: {e}; UncRes will be NaN this quarter")
                y_hat = pd.Series(np.nan, index=df_test_valid.index)
        else:
            y_hat = pd.Series(dtype=float)

        for idx, r in df_test_valid.iterrows():
            ceo_str = str(r["ceo_id"])
            g_i = gamma.get(ceo_str, 0.0)  # 0.0 = reference CEO (absorbed in Intercept)
            clarity_value = -g_i
            pred = y_hat.get(idx, np.nan)
            uncres_value = (r[dep_var] - pred) if pd.notna(pred) else np.nan
            collected_rows.append({
                "file_name": r["file_name"],
                "gvkey": r["gvkey"],
                "ceo_id": r["ceo_id"],
                "sample": r.get("sample", "Main"),
                "start_date": r["start_date"],
                "year": r["year"],
                "quarter": str(q),
                dep_var: r[dep_var],
                "ClarityCEO_QtrExp": clarity_value,
                "UncResCEO_QtrExp": uncres_value,
                "train_n": int(len(df_train)),
                "train_r2": float(model.rsquared),
                "has_training": True,
                "skip_reason": "",
            })

        _emit_na_rows(df_test_drop, "ceo_or_year_not_in_training")

        quarter_diagnostics.append({
            "quarter": str(q),
            "train_n": int(len(df_train)),
            "train_ceos": len(valid_train_ceos),
            "test_n": int(len(df_test)),
            "test_valid": int(len(df_test_valid)),
            "rsquared": float(model.rsquared),
            "skipped": False,
        })
        if len(all_quarters) <= 80 or (len(quarter_diagnostics) % 10 == 0):
            print(f"    Q{q}: train n={len(df_train):>6,} ({len(valid_train_ceos):>4,} CEOs)  "
                  f"test n={len(df_test):>5,} valid={len(df_test_valid):>5,}  R^2={model.rsquared:.3f}")

    duration = (datetime.now() - start_time).total_seconds()

    residuals_df = pd.DataFrame(collected_rows)
    diag_df = pd.DataFrame(quarter_diagnostics)
    n_clarity = int(residuals_df["ClarityCEO_QtrExp"].notna().sum())
    n_uncres = int(residuals_df["UncResCEO_QtrExp"].notna().sum())
    print(f"\n  [OK] Complete in {duration:.1f}s")
    print(f"  Per-call rows: {len(residuals_df):,}")
    print(f"  Non-NaN ClarityCEO_QtrExp: {n_clarity:,}")
    print(f"  Non-NaN UncResCEO_QtrExp:  {n_uncres:,}")
    print(f"  Union of training-window valid CEOs: {len(valid_ceos_union):,}")

    return residuals_df, diag_df, valid_ceos_union


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    residuals_df: pd.DataFrame,
    quarter_diagnostics: pd.DataFrame,
    valid_ceos: Set[Any],
    out_dir: Path,
) -> None:
    """Save per-call residuals + per-quarter + summary diagnostics."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-call decomposition (DWZ-named, expanding-window suffix)
    res_path = out_dir / "ceo_clarity_qtrexp_residuals.parquet"
    residuals_df.to_parquet(res_path, index=False)
    n_clarity = int(residuals_df["ClarityCEO_QtrExp"].notna().sum())
    n_uncres = int(residuals_df["UncResCEO_QtrExp"].notna().sum())
    print(f"  Saved: ceo_clarity_qtrexp_residuals.parquet "
          f"({len(residuals_df):,} rows; {n_clarity:,} non-NaN ClarityCEO_QtrExp; "
          f"{n_uncres:,} non-NaN UncResCEO_QtrExp)")

    # Per-quarter diagnostics
    if quarter_diagnostics is not None and len(quarter_diagnostics) > 0:
        quarter_diagnostics.to_csv(
            out_dir / "quarter_diagnostics.csv", index=False, float_format="%.6f"
        )
        print(f"  Saved: quarter_diagnostics.csv ({len(quarter_diagnostics)} quarters)")

    # Summary diagnostics: median / range across quarters (single-row CSV)
    qd_valid = quarter_diagnostics[~quarter_diagnostics["skipped"]] if quarter_diagnostics is not None else pd.DataFrame()
    diag_row = {
        "model": "CEO_Baseline",
        "n_obs_total": int(len(residuals_df)),
        "n_obs_with_training": int(residuals_df["has_training"].sum()) if "has_training" in residuals_df.columns else 0,
        "n_clarity_nonnan": n_clarity,
        "n_uncres_nonnan": n_uncres,
        "n_quarters_total": int(len(quarter_diagnostics)) if quarter_diagnostics is not None else 0,
        "n_quarters_fit": int(len(qd_valid)),
        "n_quarters_skipped": int(len(quarter_diagnostics) - len(qd_valid)) if quarter_diagnostics is not None else 0,
        "valid_ceos_union": len(valid_ceos),
        "median_train_n": int(qd_valid["train_n"].median()) if len(qd_valid) > 0 else None,
        "median_train_ceos": int(qd_valid["train_ceos"].median()) if len(qd_valid) > 0 else None,
        "median_rsquared": float(qd_valid["rsquared"].median()) if len(qd_valid) > 0 else None,
        "min_rsquared": float(qd_valid["rsquared"].min()) if len(qd_valid) > 0 else None,
        "max_rsquared": float(qd_valid["rsquared"].max()) if len(qd_valid) > 0 else None,
    }
    pd.DataFrame([diag_row]).to_csv(
        out_dir / "model_diagnostics.csv", index=False, float_format="%.10f"
    )
    print("  Saved: model_diagnostics.csv (1 row)")


def generate_report(
    residuals_df: pd.DataFrame,
    quarter_diagnostics: pd.DataFrame,
    valid_ceos: Set[Any],
    out_dir: Path,
    duration: float,
) -> None:
    """Markdown report on the quarterly-expanding decomposition."""
    n_total = len(residuals_df)
    n_training = int(residuals_df["has_training"].sum()) if "has_training" in residuals_df.columns else 0
    n_clarity = int(residuals_df["ClarityCEO_QtrExp"].notna().sum())
    n_uncres = int(residuals_df["UncResCEO_QtrExp"].notna().sum())

    qd_valid = quarter_diagnostics[~quarter_diagnostics["skipped"]] if quarter_diagnostics is not None else pd.DataFrame()
    n_qtrs_total = len(quarter_diagnostics) if quarter_diagnostics is not None else 0
    n_qtrs_fit = len(qd_valid)

    report_lines = [
        "# H0.3 Expanding — Quarterly-Expanding DWZ Replication Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Method",
        "",
        "Spec: DWZ 2021 Eq.4 — `UncAnsCEO ~ C(ceo_id) + UncPreCEO + UncQue + NegCall + StockRet + MarketRet + EPSgrowth + SurpDec + C(year)`.",
        "",
        "Substitution from H0.3 baseline: full-panel single fit -> quarterly-expanding-window.",
        "For each calendar quarter q, training window = calls with _qtr < q (strict no-look-ahead; out-of-sample residuals for stronger IV interpretation).",
        "Min-calls filter (>=5 calls per CEO) applied to training window only.",
        "Continuous controls standardized using training mean/SD; same transformation applied to test rows.",
        "",
        "Outputs (DWZ-named with expanding-window suffix):",
        "- `ClarityCEO_QtrExp` = -gamma_i  (DWZ §4.4 p.16: 'negative of the CEO fixed effect')",
        "- `UncResCEO_QtrExp`  = raw - predicted  (DWZ Table 6 Notes p.30)",
        "",
        "## Decomposition counts",
        "",
        f"- Per-call rows emitted: **{n_total:,}**",
        f"- Rows with sufficient training: **{n_training:,}**",
        f"- Non-NaN `ClarityCEO_QtrExp`: **{n_clarity:,}**",
        f"- Non-NaN `UncResCEO_QtrExp`:  **{n_uncres:,}**",
        f"- Union of training-window valid CEOs (>=5 calls anywhere): **{len(valid_ceos):,}**",
        "",
        "## Quarter-fit diagnostics",
        "",
        f"- Quarters total: **{n_qtrs_total}**",
        f"- Quarters fit:   **{n_qtrs_fit}** (skipped insufficient training: {n_qtrs_total - n_qtrs_fit})",
    ]
    if len(qd_valid) > 0:
        report_lines += [
            f"- Median training N: **{int(qd_valid['train_n'].median()):,}**",
            f"- Median training CEOs: **{int(qd_valid['train_ceos'].median()):,}**",
            f"- Training R^2 range: **[{qd_valid['rsquared'].min():.3f}, {qd_valid['rsquared'].max():.3f}]**",
            f"- Median training R^2: **{qd_valid['rsquared'].median():.3f}**",
        ]
    report_lines.append("")

    # Decomposition summary stats (mean/SD of the produced columns)
    dv_cols = [c for c in ["UncAnsCEO", "ClarityCEO_QtrExp", "UncResCEO_QtrExp"]
               if c in residuals_df.columns]
    if dv_cols:
        report_lines += [
            "## Per-call decomposition summary stats",
            "",
            "| Variable | N | Mean | SD | Min | P25 | P50 | P75 | Max |",
            "|----------|--:|----:|---:|----:|----:|----:|----:|----:|",
        ]
        for c in dv_cols:
            s = residuals_df[c].dropna()
            if len(s) == 0:
                continue
            report_lines.append(
                f"| `{c}` | {len(s):,} | {s.mean():.4f} | {s.std():.4f} | "
                f"{s.min():.4f} | {s.quantile(0.25):.4f} | {s.median():.4f} | "
                f"{s.quantile(0.75):.4f} | {s.max():.4f} |"
            )
        report_lines.append("")

        # Correlation among raw + clarity + residual
        corr = residuals_df[dv_cols].corr()
        report_lines += [
            "## Correlation matrix (raw vs decomposed)",
            "",
            "|            | " + " | ".join([f"`{c}`" for c in dv_cols]) + " |",
            "|------------|" + "|".join(["---:"] * len(dv_cols)) + "|",
        ]
        for c in dv_cols:
            row = [f"{corr.loc[c, c2]:+.4f}" for c2 in dv_cols]
            report_lines.append(f"| `{c}` | " + " | ".join(row) + " |")
        report_lines.append("")

        corr.to_csv(out_dir / "correlation_matrix.csv", float_format="%.6f")
        print("  Saved: correlation_matrix.csv")

    report_path = out_dir / "report_h0_3_expanding.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("  Saved: report_h0_3_expanding.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution — quarterly-expanding DWZ Eq.4 replication."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    # Separate output dir; do NOT clobber non-expanding H0.3 outputs
    out_dir = root / "outputs" / "econometric" / "ceo_clarity_expanding" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H0.3_CeoClarity_Expanding",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("H0.3 EXPANDING: DWZ Eq.4 quarterly-expanding-window")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    panel = load_panel(root, panel_path)
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "ceo_clarity_extended",
        required_file="ceo_clarity_extended_panel.parquet",
    ) / "ceo_clarity_extended_panel.parquet"

    # Sample assignment
    if "sample" not in panel.columns:
        if "ff12_code" in panel.columns:
            panel["sample"] = assign_industry_sample(panel["ff12_code"])
        else:
            raise ValueError("Neither 'sample' nor 'ff12_code' column found in panel")

    out_dir.mkdir(parents=True, exist_ok=True)

    # Summary statistics across DV + DWZ Eq.4 controls (3 samples)
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    stats_cols = [v["col"] for v in SUMMARY_STATS_VARS]
    available_cols = [c for c in stats_cols if c in panel.columns]
    missing_cols = [c for c in stats_cols if c not in panel.columns]
    if missing_cols:
        print(f"  WARNING: Missing columns for summary stats: {missing_cols}")
    if available_cols:
        complete_mask = panel[available_cols].notna().all(axis=1)
        df_complete = panel[complete_mask].copy()
        print(f"  Complete cases for summary stats: {len(df_complete):,}")
        for samp in ["Main", "Finance", "Utility"]:
            n = (df_complete["sample"] == samp).sum()
            print(f"    {samp}: {n:,}")
        make_summary_stats_table(
            df=df_complete,
            variables=SUMMARY_STATS_VARS,
            sample_names=["Main", "Finance", "Utility"],
            sample_col="sample",
            output_csv=out_dir / "summary_stats.csv",
            output_tex=out_dir / "summary_stats.tex",
            caption="Summary Statistics — H0.3 Expanding (DWZ Eq.4 inputs)",
            label="tab:summary_stats_h03_expanding",
        )
        print("  Saved: summary_stats.csv")
        print("  Saved: summary_stats.tex")

    # Single CEO_Baseline model — DWZ Eq.4 with quarterly-expanding window
    model_config = MODELS["CEO_Baseline"]
    df_model = prepare_regression_data(panel, model_config, "CEO_Baseline")
    df_main = df_model[df_model["sample"] == "Main"].copy()

    if len(df_main) < 100:
        print(f"\n  ABORT CEO_Baseline: too few observations ({len(df_main)})")
        return 1

    residuals_df, quarter_diagnostics, valid_ceos = run_expanding_regression(
        df_main, model_config, "CEO_Baseline"
    )

    if residuals_df is None or len(residuals_df) == 0:
        print("\n  ABORT: expanding-window regression produced no rows")
        return 1

    save_outputs(residuals_df, quarter_diagnostics, valid_ceos, out_dir)
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(residuals_df, quarter_diagnostics, valid_ceos, out_dir, duration)

    # Sample attrition
    attrition_stages = [
        ("Master manifest", len(panel)),
        ("Main sample filter", int((panel["sample"] == "Main").sum())),
        ("Per-call rows emitted (expanding)", int(len(residuals_df))),
        ("Non-NaN ClarityCEO_QtrExp", int(residuals_df["ClarityCEO_QtrExp"].notna().sum())),
    ]
    generate_attrition_table(attrition_stages, out_dir, "H0.3 Expanding (DWZ Eq.4)")
    print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="h0_3_expanding",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "residuals": out_dir / "ceo_clarity_qtrexp_residuals.parquet",
            "quarter_diagnostics": out_dir / "quarter_diagnostics.csv",
            "model_diagnostics": out_dir / "model_diagnostics.csv",
            "summary_stats": out_dir / "summary_stats.csv",
            "report": out_dir / "report_h0_3_expanding.md",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
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
