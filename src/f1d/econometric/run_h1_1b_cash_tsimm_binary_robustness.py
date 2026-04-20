#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1.1b Binary TNIC-Moderated Cash Holdings Hypothesis
================================================================================
ID: econometric/run_h1_1b_cash_tsimm_binary
Description: Test whether product-market similarity (Hoberg-Phillips TNIC3TSIMM),
             binarized at per-fiscal-year median, moderates the
             UncAnsMgr -> CashRatio relationship.

Model Specification:
    CashRatio = b1*Mgr_QA_Unc_c + b2*HighTSIMM
              + b3*(Mgr_QA_Unc_c x HighTSIMM)
              + controls + IndustryFE + CalendarYearFE + e

    HighTSIMM = 1 if TotalSimilarity > per-fiscal-year median (Main sample), 0 otherwise.
    b1 = effect of uncertainty for low-TSIMM firms (reference group).
    b1 + b3 = effect for high-TSIMM firms.
    b3 = moderation increment (parameter of interest).

Parent suite: H1.1 (Continuous TNIC moderation)
    This suite complements H1.1 with a binary moderator presentation,
    standard in empirical corporate finance (Hoberg & Phillips 2016).

8 Models:
    Cols 1-4: DV = CashRatio_t, full FE ladder (Industry+CalYr, Firm+CalYr, Industry+YQ, Firm+YQ)
    Cols 5-8: DV = CashRatio_{t+1} (lead), full FE ladder

Moderator: HighTSIMM (binary, above/below per-fiscal-year median of TNIC3TSIMM)
    Median computed on Main sample before complete-case deletion.

Sample: Main only (FF12 not in {8, 11}).
Hypothesis: Two-tailed on interaction (b3 != 0); one-tailed on main IV (b1 > 0).
Unit: Call-level (loads H1 panel, merges TNIC at load time).
Panel index: ["gvkey", "cal_yr"] or ["gvkey", "cal_yr_qtr"].
SEs: Firm-clustered.

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
    - inputs/TNIC3HHIdata/TNIC3HHIdata.txt

Outputs:
    - outputs/econometric/h1_1b_cash_tsimm_binary/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-03-28
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import (
    extract_coefs_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

IV = "UncAnsCEO"

CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    "Lagged_DV",  # Unified lagged DV
]

MODERATOR_RAW = "TotalSimilarity"
MODERATOR = "HighTSIMM"
IV_CENTERED = "UncAnsCEO_c"  # mean-centered on Main sample
INTERACTION = "UncAnsCEO_c_x_HighTSIMM"

MIN_CALLS_PER_FIRM = 5

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission (moderation, 4 cols, single DV).
# ------------------------------------------------------------------
SUITE_ID = "H1.1b.r"
SUITE_DIR_NAME = "h1_1b_cash_tsimm_binary_robustness"
SUITE_TITLE = "Binary Product Similarity-Moderated Speech Uncertainty and Cash Holdings (Orthogonal Speaker Partition: CEO Q&A)"
SUITE_CAPTION = (
    "H1.1b.r: Binary Product Similarity--Moderated Speech Uncertainty and Cash Holdings "
    "(Robustness: CEO Q\\&A Speaker Partition)"
)
SUITE_LABEL = "tab:h1_1b_robust"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms)."
HYP_DIR = "positive"  # main IV expected beta > 0; moderator + interaction two-tailed
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []

MODEL_SPECS = [
    # CashRatio_t: cols 1-4 (full FE ladder)
    {"col": 1, "dv": "CashRatio",      "fe": "industry",    "extra_controls": []},
    {"col": 2, "dv": "CashRatio",      "fe": "firm",        "extra_controls": []},
    {"col": 3, "dv": "CashRatio",      "fe": "industry_yq", "extra_controls": []},
    {"col": 4, "dv": "CashRatio",      "fe": "firm_yq",     "extra_controls": []},
    # CashRatio_lead: cols 5-8 (full FE ladder)
    {"col": 5, "dv": "CashRatio_lead", "fe": "industry",    "extra_controls": []},
    {"col": 6, "dv": "CashRatio_lead", "fe": "firm",        "extra_controls": []},
    {"col": 7, "dv": "CashRatio_lead", "fe": "industry_yq", "extra_controls": []},
    {"col": 8, "dv": "CashRatio_lead", "fe": "firm_yq",     "extra_controls": []},
]

DV_TEX = {
    "CashRatio": r"Cash$_t$",
    "CashRatio_lead": r"Cash$_{t+1}$",
}

IV_LABEL = "Mgr QA Uncertainty"
MODERATOR_LABEL = "HighTSIMM"
INTERACTION_LABEL = r"Mgr QA Unc $\times$ HighTSIMM"

SUMMARY_STATS_VARS = [
    {"col": "CashRatio", "label": "Cash Holdings$_t$"},
    {"col": "CashRatio_lead", "label": "Cash Holdings$_{t+1}$"},
    {"col": IV, "label": "CEO QA Uncertainty (raw)"},
    {"col": IV_CENTERED, "label": "CEO QA Uncertainty (centered)"},
    {"col": MODERATOR_RAW, "label": "TNIC3TSIMM (raw)"},
    {"col": MODERATOR, "label": "HighTSIMM (binary)"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": "R\\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.1b Binary TNIC-Moderated Cash Holdings (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load call-level H1 panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading H1 panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        panel_file = panel_dir / "h1_cash_holdings_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "start_date",  # needed for cal_yr_qtr
        "gvkey", "year", "fyearq_int", "ff12_code",
        "CashRatio", "CashRatio_lag", "CashRatio_lead",
        IV,
        *[c for c in CONTROLS if c != "Lagged_DV"],  # lagged created dynamically
    ]

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")

    # Build calendar year-quarter index for FE specs
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

    return panel, panel_file


def load_and_merge_tnic(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Load TNIC3 data and merge TotalSimilarity into panel."""
    print("\n" + "=" * 60)
    print("Merging TNIC3TSIMM")
    print("=" * 60)

    tnic_path = root_path / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt"
    if not tnic_path.exists():
        raise FileNotFoundError(f"TNIC data not found: {tnic_path}")

    tnic = pd.read_csv(tnic_path, sep="\t")
    print(f"  Loaded TNIC: {len(tnic):,} rows, years {tnic['year'].min()}-{tnic['year'].max()}")

    # Merge on (gvkey_int, fyearq_int)
    panel["_gvkey_int"] = pd.to_numeric(panel["gvkey"], errors="coerce")

    before = len(panel)
    panel = panel.merge(
        tnic[["gvkey", "year", "tnic3tsimm"]].rename(
            columns={"gvkey": "_gvkey_int", "year": "fyearq_int", "tnic3tsimm": "TotalSimilarity"}
        ),
        on=["_gvkey_int", "fyearq_int"],
        how="left",
    )
    assert len(panel) == before, f"TNIC merge changed row count: {before} -> {len(panel)}"
    panel = panel.drop(columns=["_gvkey_int"])

    n_matched = panel[MODERATOR_RAW].notna().sum()
    print(f"  TNIC match: {n_matched:,} / {len(panel):,} ({100 * n_matched / len(panel):.1f}%)")
    print(f"  TotalSimilarity range: [{panel[MODERATOR_RAW].min():.2f}, {panel[MODERATOR_RAW].max():.2f}]")

    return panel


def transform_moderator_and_center_iv(
    panel: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Create binary HighTSIMM indicator and mean-center IV on Main sample.

    HighTSIMM = 1 if TotalSimilarity > per-fiscal-year median (Main sample).
    Per-year median prevents the dummy from capturing secular trends in
    product similarity over the 2002-2018 sample period.

    Mean-centering the IV before forming the interaction reduces
    multicollinearity between the moderator and interaction term.
    """
    print("\n" + "=" * 60)
    print("Creating binary moderator + centering IV")
    print("=" * 60)

    main_mask = ~panel["ff12_code"].isin([8, 11])

    # --- Moderator: per-fiscal-year median split on Main sample ---
    tsimm_main = panel.loc[main_mask].dropna(subset=[MODERATOR_RAW])
    yearly_median = tsimm_main.groupby("fyearq_int")[MODERATOR_RAW].median()

    panel["_tsimm_yr_median"] = panel["fyearq_int"].map(yearly_median)
    panel[MODERATOR] = (panel[MODERATOR_RAW] > panel["_tsimm_yr_median"]).astype(float)
    # NaN TSIMM stays NaN (will be dropped in complete-case filter)
    panel.loc[panel[MODERATOR_RAW].isna(), MODERATOR] = np.nan
    panel.drop(columns=["_tsimm_yr_median"], inplace=True)

    high_n = int((panel.loc[main_mask, MODERATOR] == 1).sum())
    low_n = int((panel.loc[main_mask, MODERATOR] == 0).sum())
    total = high_n + low_n

    print(f"  Main sample TSIMM obs: {total:,}")
    print(f"  HighTSIMM=1: {high_n:,} ({100*high_n/total:.1f}%)")
    print(f"  HighTSIMM=0: {low_n:,} ({100*low_n/total:.1f}%)")
    print(f"  Per-year median range: [{yearly_median.min():.4f}, {yearly_median.max():.4f}]")

    # --- IV: mean-center on Main sample ---
    iv_main = panel.loc[main_mask, IV].dropna()
    iv_mu = iv_main.mean()

    panel[IV_CENTERED] = panel[IV] - iv_mu

    print(f"  IV mean (Main): {iv_mu:.4f}")
    print(f"  IV centered mean (Main): {panel.loc[main_mask, IV_CENTERED].mean():.4f}")

    params: Dict[str, Any] = {
        "iv_mu": iv_mu,
        "yearly_medians": yearly_median.to_dict(),
        "n_high": high_n,
        "n_low": low_n,
    }

    return panel, params


# ==============================================================================
# Regression
# ==============================================================================


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only (exclude Finance ff12=8, Utility ff12=11)."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any]
) -> pd.DataFrame:
    """Prepare data for one regression spec with interaction term."""
    dv = spec["dv"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    # Determine time column based on FE type
    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"

    # Create Lagged_DV: always lag of the base DV (t-1), regardless of t/t+1
    base_dv = dv.replace("_lead", "")
    lag_col = f"{base_dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    required = [dv, IV, IV_CENTERED, MODERATOR] + all_controls + ["gvkey", time_col, "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Create interaction term using CENTERED IV
    df[INTERACTION] = df[IV_CENTERED] * df[MODERATOR]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases (DV + IV + moderator + interaction + controls + identifiers)
    all_required = required + [INTERACTION]
    complete_mask = df[all_required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()

    n_firms = df["gvkey"].nunique()
    n_time_periods = df.groupby(["gvkey", time_col]).ngroups
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {n_firms:,} firms, {n_time_periods:,} firm-time-periods")

    return df


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any]
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with Industry FE + Calendar Year or Year-Quarter FE."""
    dv = spec["dv"]
    col_num = spec["col"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    # Determine time column and FE label
    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"
    base_fe = fe.replace("_yq", "")
    fe_label = f"{'Firm' if base_fe == 'firm' else 'Industry(FF12)'} + {'CalYrQtr' if fe.endswith('_yq') else 'CalYear'}"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    # Use centered IV in regression so main-effect coefficient represents
    # the effect for the reference group (low-TSIMM firms)
    exog = [IV_CENTERED, MODERATOR, INTERACTION] + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_time_periods = df_prepared.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-time-periods={n_time_periods:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        if base_fe == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv],
                exog=df_panel[exog],
                entity_effects=False,
                time_effects=True,
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True,
                check_rank=False,
            )
        else:  # firm
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()

    # Extract coefficients (IV is centered; coefficient = effect for low-TSIMM reference group)
    beta_iv = float(model.params.get(IV_CENTERED, np.nan))
    se_iv = float(model.std_errors.get(IV_CENTERED, np.nan))
    p_two_iv = float(model.pvalues.get(IV_CENTERED, np.nan))

    # One-tailed p for main IV (expected positive)
    if not np.isnan(p_two_iv) and not np.isnan(beta_iv):
        p_one_iv = p_two_iv / 2 if beta_iv > 0 else 1 - p_two_iv / 2
    else:
        p_one_iv = np.nan

    beta_mod = float(model.params.get(MODERATOR, np.nan))
    se_mod = float(model.std_errors.get(MODERATOR, np.nan))
    p_two_mod = float(model.pvalues.get(MODERATOR, np.nan))

    beta_int = float(model.params.get(INTERACTION, np.nan))
    se_int = float(model.std_errors.get(INTERACTION, np.nan))
    p_two_int = float(model.pvalues.get(INTERACTION, np.nan))

    stars_iv = _sig_stars_one(p_one_iv)
    stars_int = _sig_stars_two(p_two_int)

    print(f"  [OK] {elapsed:.1f}s | R2={model.rsquared:.4f}  Adj R2={1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")
    print(f"  {IV}: b={beta_iv:.4f} p1={p_one_iv:.4f} {stars_iv}")
    print(f"  {MODERATOR}: b={beta_mod:.4f} p2={p_two_mod:.4f}")
    print(f"  INTERACTION: b={beta_int:.4f} p2={p_two_int:.4f} {stars_int}")

    meta = {
        "col": col_num,
        "dv": dv,
        "fe": fe,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "n_time_periods": n_time_periods,
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "beta_iv": beta_iv, "se_iv": se_iv,
        "p_one_iv": p_one_iv, "p_two_iv": p_two_iv,
        "beta_moderator": beta_mod, "se_moderator": se_mod, "p_two_moderator": p_two_mod,
        "beta_interaction": beta_int, "se_interaction": se_int, "p_two_interaction": p_two_int,
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
    }

    return model, meta


def _sig_stars_one(p: float) -> str:
    """Significance stars for one-tailed p-value."""
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def _sig_stars_two(p: float) -> str:
    """Significance stars for two-tailed p-value."""
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


# ==============================================================================
# Output
# ==============================================================================


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write clean 2-column LaTeX table."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    def fmt_coef(val: float, stars: str) -> str:
        if np.isnan(val):
            return ""
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        if np.isnan(val):
            return ""
        return f"({val:.4f})"

    def fmt_r2(val: float) -> str:
        if np.isnan(val):
            return ""
        if abs(val) < 0.001:
            return f"{val:.2e}"
        return f"{val:.3f}"

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Binary Product Similarity--Moderated Speech Uncertainty and Cash Holdings}",
        r"\label{tab:h1_1b_cash_tsimm_binary}",
        r"\small",
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r" & (1) & (2) \\",
        r" & \multicolumn{2}{c}{Cash Holdings$_t$} \\",
        r"\cmidrule(lr){2-3}",
        r" & Cal Year FE & Cal Yr-Qtr FE \\",
        r"\midrule",
    ]

    m1 = results_by_col.get(1, {})
    m2 = results_by_col.get(2, {})

    # IV coefficient
    lines.append(
        f"Mgr QA Uncertainty & "
        f"{fmt_coef(m1.get('beta_iv', np.nan), _sig_stars_one(m1.get('p_one_iv', np.nan)))} & "
        f"{fmt_coef(m2.get('beta_iv', np.nan), _sig_stars_one(m2.get('p_one_iv', np.nan)))} \\\\"
    )
    lines.append(
        f" & {fmt_se(m1.get('se_iv', np.nan))} & {fmt_se(m2.get('se_iv', np.nan))} \\\\"
    )

    # Moderator coefficient
    lines.append(
        f"HighTSIMM & "
        f"{fmt_coef(m1.get('beta_moderator', np.nan), _sig_stars_two(m1.get('p_two_moderator', np.nan)))} & "
        f"{fmt_coef(m2.get('beta_moderator', np.nan), _sig_stars_two(m2.get('p_two_moderator', np.nan)))} \\\\"
    )
    lines.append(
        f" & {fmt_se(m1.get('se_moderator', np.nan))} & {fmt_se(m2.get('se_moderator', np.nan))} \\\\"
    )

    # Interaction coefficient (key)
    lines.append(
        f"Mgr QA Unc $\\times$ HighTSIMM & "
        f"{fmt_coef(m1.get('beta_interaction', np.nan), _sig_stars_two(m1.get('p_two_interaction', np.nan)))} & "
        f"{fmt_coef(m2.get('beta_interaction', np.nan), _sig_stars_two(m2.get('p_two_interaction', np.nan)))} \\\\"
    )
    lines.append(
        f" & {fmt_se(m1.get('se_interaction', np.nan))} & {fmt_se(m2.get('se_interaction', np.nan))} \\\\"
    )

    lines.append(r"\midrule")

    # Footer
    lines.append(r"Controls & Extended & Extended \\")
    lines.append(r"Industry FE & Yes & Yes \\")
    lines.append(r"Calendar Year FE & Yes &  \\")
    lines.append(r"Calendar Year-Quarter FE &  & Yes \\")
    lines.append(r"\midrule")

    # N calls
    lines.append(
        f"N (calls) & {m1.get('n_obs', 0):,} & {m2.get('n_obs', 0):,} \\\\"
    )
    # N firm-time-periods
    lines.append(
        f"N (firm-time-periods) & {m1.get('n_time_periods', 0):,} & {m2.get('n_time_periods', 0):,} \\\\"
    )
    # R² and Adj R²
    lines.append(
        f"$R^2$ & {fmt_r2(m1.get('r2', np.nan))} & "
        f"{fmt_r2(m2.get('r2', np.nan))} \\\\"
    )
    lines.append(
        f"Adj.~$R^2$ & {fmt_r2(m1.get('adj_r2', np.nan))} & "
        f"{fmt_r2(m2.get('adj_r2', np.nan))} \\\\"
    )

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$. ",
        r"Main IV (Mgr QA Uncertainty) mean-centered; one-tailed ($\beta > 0$). ",
        r"Interaction and moderator: two-tailed. ",
        r"IV coefficient represents effect at sample-mean uncertainty. ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"Main sample (excludes financial and utility firms). ",
        r"HighTSIMM is 1 if Hoberg--Phillips (2016) TNIC3TSIMM exceeds the per-fiscal-year median ",
        r"on the main sample, 0 otherwise. ",
        r"Col~(1): Calendar Year FE. Col~(2): Calendar Year-Quarter FE. ",
        r"HighTSIMM is a binary firm-year variable repeated across calls within the same firm-year. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_1b_cash_tsimm_binary_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
    """Save all outputs."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Individual regression .txt files
    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        col_num = meta["col"]
        fname = f"regression_results_col{col_num}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            f.write(f"H1.1b Binary TNIC-Moderated Cash Holdings Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IV: {IV}\n")
            f.write(f"Moderator: HighTSIMM (binary, per-fiscal-year median)\n")
            f.write(f"Interaction: {INTERACTION}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    # Diagnostics CSV
    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    # LaTeX table
    _save_latex_table(all_results, out_dir)

    return diag_df


def generate_report(
    all_results: List[Dict[str, Any]], out_dir: Path,
    duration: float, transform_params: Dict[str, Any],
) -> None:
    """Generate markdown report."""
    n_high = transform_params["n_high"]
    n_low = transform_params["n_low"]
    lines = [
        "# H1.1b Binary TNIC-Moderated Cash Holdings Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** UncAnsMgr x HighTSIMM (binary) interaction",
        f"**Moderator:** HighTSIMM = 1 if TNIC3TSIMM > per-fiscal-year median (Main sample)",
        f"**Split:** HighTSIMM=1: {n_high:,}, HighTSIMM=0: {n_low:,} ({100*n_high/(n_high+n_low):.1f}% high)",
        f"**FE:** Col 1: Industry + CalYear; Col 2: Industry + CalYrQtr",
        f"**Parent suite:** H1.1 (Continuous TNIC moderation)",
        "",
        "## Model Specifications",
        "",
        "| Col | DV | FE |",
        "|-----|-----|-----|",
        "| (1) | CashRatio_t | Industry + Calendar Year |",
        "| (2) | CashRatio_t | Industry + Calendar Year-Quarter |",
        "",
        "## Results",
        "",
        "| Col | DV | FE | b_iv | p1_iv | b_interaction | p2_interaction | N calls | R2 |",
        "|-----|----|-----|------|-------|---------------|----------------|---------|-----|",
    ]

    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        stars_iv = _sig_stars_one(m["p_one_iv"])
        stars_int = _sig_stars_two(m["p_two_interaction"])
        lines.append(
            f"| ({m['col']}) | {m['dv']} | {m['fe']} | {m['beta_iv']:.4f}{stars_iv} | "
            f"{m['p_one_iv']:.4f} | {m['beta_interaction']:.4f}{stars_int} | "
            f"{m['p_two_interaction']:.4f} | {m['n_obs']:,} | "
            f"{m['r2']:.4f} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Main IV (Mgr QA Unc): one-tailed test (H1: beta > 0)")
    lines.append("- Interaction: two-tailed test")
    lines.append("- HighTSIMM is a binary firm-year variable, repeated across calls within firm-year")
    lines.append("- Col (1): Calendar Year FE; Col (2): Calendar Year-Quarter FE")
    lines.append("- SEs firm-clustered throughout")

    with open(out_dir / "report_step4_H1_1b.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_1b.md")


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H1.1b.json from moderation runner state.

    H1.1b structure: 8 cols = 2 DVs (CashRatio, CashRatio_lead) x 2 FE
    entities x 2 time-FE granularities. Binary moderator HighTSIMM;
    interaction UncAnsCEO_c_x_HighTSIMM.
    """
    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    results_by_col = {
        r["meta"]["col"]: r for r in all_results if r.get("meta")
    }

    for spec in MODEL_SPECS:
        col_num = spec["col"]
        if col_num not in results_by_col:
            raise RuntimeError(
                f"H1.1b spec build: missing result for col {col_num}"
            )
        result = results_by_col[col_num]
        model = result["model"]
        meta = result["meta"]

        fe = spec["fe"]
        base_fe = fe.replace("_yq", "")
        fe_entity = "industry" if base_fe == "industry" else "firm"
        fe_time = (
            "calendar_year_quarter" if fe.endswith("_yq") else "calendar_year"
        )

        extra_controls = spec.get("extra_controls", [])
        control_vars = list(CONTROLS) + list(extra_controls)

        try:
            dv_mean: Optional[float] = float(
                model.model.dependent.dataframe.mean().iloc[0]
            )
        except Exception:
            dv_mean = None

        col_metadata.append(
            {
                "col": col_num,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": fe_time,
                "control_vars": control_vars,
                "n_obs": int(meta["n_obs"]),
                "n_firms": int(meta.get("n_firms", 0)) or None,
                "r2": float(meta["r2"]),
                "adj_r2": float(meta.get("adj_r2", float("nan"))),
                "dv_mean": dv_mean,
                "cluster_fallback": False,
            }
        )

        iv_key_names = [IV_CENTERED, MODERATOR, INTERACTION]
        coefs_per_col.append(
            extract_coefs_panelols(
                model=model,
                key_ivs=iv_key_names,
                all_vars=iv_key_names + control_vars,
                hyp_dir=HYP_DIR,
            )
        )

    header_rows = [
        [
            {"label": "CashRatio", "span": 4},
            {"label": r"CashRatio\_lead", "span": 4},
        ]
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR_NAME,
        sub_tables=[
            {
                "suite_id": SUITE_ID,
                "dir_name": SUITE_DIR_NAME,
                "title": SUITE_TITLE,
                "caption": SUITE_CAPTION,
                "label": SUITE_LABEL,
                "col_range": [s["col"] for s in MODEL_SPECS],
                "header_rows": header_rows,
                "suite_type": "moderation",
            }
        ],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=SAMPLE_LABEL,
        clustering=CLUSTERING,
        tail=TAIL,
        # All three H1.1b key vars are one-tailed positive per
        # feedback_moderation_tails.md (user explicitly corrected twice —
        # IV, moderator, AND interaction must all be one-tailed positive).
        ivs=[
            {"name": IV_CENTERED, "label": r"UncAnsCEO\_c", "tail": "one_pos"},
            {"name": MODERATOR, "label": "HighTSIMM", "tail": "one_pos"},
            {"name": INTERACTION, "label": r"UncAnsCEO\_c\_x\_HighTSIMM", "tail": "one_pos"},
        ],
        controls={
            "base": list(CONTROLS),
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h1_1b_cash_tsimm_binary_robustness" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_1b_CashTSIMMBinary_Robust",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.1b Binary TNIC-Moderated Cash Holdings")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    1 IV x 2 DVs x 4 FE types = 8 models")
    print(f"Moderator: HighTSIMM (binary, per-fiscal-year median)")
    print(f"IV:        {IV}")

    # Load panel
    panel, panel_file = load_panel(root, panel_path)

    # Merge TNIC
    panel = load_and_merge_tnic(panel, root)

    # Transform moderator + center IV (on Main sample)
    panel, transform_params = transform_moderator_and_center_iv(panel)

    # Filter to Main sample
    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    for dv in ["CashRatio", "CashRatio_lead"]:
        print(f"  {dv} non-null: {panel[dv].notna().sum():,}")
    print(f"  {IV}: {panel[IV].notna().sum():,} "
          f"({100 * panel[IV].notna().mean():.1f}%)")
    print(f"  {MODERATOR}: {panel[MODERATOR].notna().sum():,} "
          f"({100 * panel[MODERATOR].notna().mean():.1f}%)")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H1.1b.r Binary TNIC-Moderated Cash Holdings (Robustness, Main Sample)",
        label="tab:summary_stats_h1_1b_robust",
    )
    print("  Saved: summary_stats.csv/.tex")

    # Run 2 regressions
    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} ---")

        try:
            df_prep = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        if len(df_prep) < 100:
            print(f"  Skipping: too few obs")
            continue

        model, meta = run_regression(df_prep, spec)
        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    # Save outputs
    diag_df = save_outputs(all_results, out_dir)
    _write_suite_spec_json(all_results, out_dir)

    # Attrition
    tnic_matched = panel[MODERATOR_RAW].notna().sum()
    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel (H1)", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("TNIC3TSIMM matched", tnic_matched),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir, "H1.1b Binary TNIC-Moderated Cash Holdings",
        )
        print("  Saved: sample_attrition.csv/.tex")

    # Manifest
    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={
            "panel": panel_file,
            "tnic": root / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt",
        },
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, out_dir, duration, transform_params)

    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    for r in all_results:
        m = r["meta"]
        stars_iv = _sig_stars_one(m["p_one_iv"])
        stars_int = _sig_stars_two(m["p_two_interaction"])
        print(f"  Col ({m['col']}) {m['dv']}: "
              f"IV b={m['beta_iv']:.4f}{stars_iv} | "
              f"Interaction b={m['beta_interaction']:.4f}{stars_int}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IV: {IV}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(CONTROLS)}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
