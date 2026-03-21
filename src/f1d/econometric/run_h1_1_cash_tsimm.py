#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1.1 TNIC-Moderated Cash Holdings Hypothesis
================================================================================
ID: econometric/run_h1_1_cash_tsimm
Description: Test whether product-market similarity (Hoberg-Phillips TNIC3TSIMM)
             moderates the Manager_Pres_Uncertainty → CashHoldings relationship.

Model Specification:
    CashHoldings = b1*Mgr_Pres_Unc + b2*z(log(TSIMM))
                 + b3*(Mgr_Pres_Unc x z(log(TSIMM)))
                 + controls + IndustryFE + FiscalYearFE + e

    b3 is the coefficient of interest: does product similarity moderate
    the effect of managerial presentation uncertainty on cash holdings?

Parent suite: H1 (Cash Holdings)
    Manager_Pres_Uncertainty_pct significant in Industry+FY specs only.
    Moderation memo recommends TSIMM (not HHI) as secondary moderator.

2 Models:
    Col 1: DV = CashHoldings_t,    Industry+FY FE, Extended controls
    Col 2: DV = CashHoldings_lead, Industry+FY FE, Extended controls + CashHoldings_t

Moderator: TNIC3TSIMM (Hoberg & Phillips JPE 2016)
    Log-transformed then z-scored on Main sample.

Sample: Main only (FF12 not in {8, 11}).
Hypothesis: Two-tailed on interaction (b3 != 0); one-tailed on main IV (b1 > 0).
Unit: Call-level (loads H1 panel, merges TNIC at load time).
Panel index: ["gvkey", "fyearq_int"].
SEs: Firm-clustered.

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
    - inputs/TNIC3HHIdata/TNIC3HHIdata.txt

Outputs:
    - outputs/econometric/h1_1_cash_tsimm/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-03-18
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
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir


# ==============================================================================
# Configuration
# ==============================================================================

IV = "Manager_Pres_Uncertainty_pct"

CONTROLS = [
    "BookLev", "Size", "TobinsQ", "ROA", "CapexAt",
    "DividendPayer", "OCF_Volatility",
    "SalesGrowth", "RD_Intensity", "CashFlow", "Volatility",
]

MODERATOR_RAW = "tnic3tsimm"
MODERATOR = "z_log_tnic3tsimm"
IV_CENTERED = "Manager_Pres_Unc_c"  # mean-centered on Main sample
INTERACTION = "MgrPresUnc_x_zlogTSIMM"

MIN_CALLS_PER_FIRM = 5

MODEL_SPECS = [
    {"col": 1, "dv": "CashHoldings",      "extra_controls": []},
    {"col": 2, "dv": "CashHoldings_lead",  "extra_controls": ["CashHoldings"]},
]

IV_LABEL = "Mgr Pres Uncertainty"
MODERATOR_LABEL = r"$z(\log(\mathrm{TSIMM}))$"
INTERACTION_LABEL = r"Mgr Pres Unc $\times$ $z(\log(\mathrm{TSIMM}))$"

SUMMARY_STATS_VARS = [
    {"col": "CashHoldings", "label": "Cash Holdings$_t$"},
    {"col": "CashHoldings_lead", "label": "Cash Holdings$_{t+1}$"},
    {"col": IV, "label": "Mgr Pres Uncertainty (raw)"},
    {"col": IV_CENTERED, "label": "Mgr Pres Uncertainty (centered)"},
    {"col": MODERATOR_RAW, "label": "TNIC3TSIMM (raw)"},
    {"col": MODERATOR, "label": "$z(\\log(\\mathrm{TSIMM}))$"},
    {"col": "BookLev", "label": "Leverage"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CapexAt", "label": "CapEx / Assets"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RD_Intensity", "label": "R\\&D Intensity"},
    {"col": "CashFlow", "label": "Cash Flow"},
    {"col": "Volatility", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.1 TNIC-Moderated Cash Holdings (call-level)",
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
        "gvkey", "year", "fyearq_int", "ff12_code",
        "CashHoldings", "CashHoldings_lead",
        IV,
        *CONTROLS,
    ]

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    return panel, panel_file


def load_and_merge_tnic(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Load TNIC3 data and merge tnic3tsimm into panel."""
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
            columns={"gvkey": "_gvkey_int", "year": "fyearq_int"}
        ),
        on=["_gvkey_int", "fyearq_int"],
        how="left",
    )
    assert len(panel) == before, f"TNIC merge changed row count: {before} -> {len(panel)}"
    panel = panel.drop(columns=["_gvkey_int"])

    n_matched = panel[MODERATOR_RAW].notna().sum()
    print(f"  TNIC match: {n_matched:,} / {len(panel):,} ({100 * n_matched / len(panel):.1f}%)")
    print(f"  tnic3tsimm range: [{panel[MODERATOR_RAW].min():.2f}, {panel[MODERATOR_RAW].max():.2f}]")

    return panel


def transform_moderator_and_center_iv(
    panel: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Log-transform + z-score TSIMM, and mean-center IV on Main sample.

    Both transformations use Main sample moments (after FF12 filter,
    before complete-case deletion) so both models use identical values.

    Mean-centering the IV before forming the interaction is critical:
    without it, Corr(moderator, interaction) ≈ 0.93 (severe multicollinearity).
    With centering, Corr drops to ≈ 0.12.
    """
    print("\n" + "=" * 60)
    print("Transforming moderator + centering IV")
    print("=" * 60)

    main_mask = ~panel["ff12_code"].isin([8, 11])

    # --- Moderator: log-transform then z-score ---
    tsimm_main = panel.loc[main_mask, MODERATOR_RAW].dropna()
    log_tsimm_main = np.log(tsimm_main)
    tsimm_mu = log_tsimm_main.mean()
    tsimm_sd = log_tsimm_main.std()

    panel["log_tnic3tsimm"] = np.log(panel[MODERATOR_RAW])
    panel[MODERATOR] = (panel["log_tnic3tsimm"] - tsimm_mu) / tsimm_sd

    print(f"  Main sample TSIMM obs: {len(tsimm_main):,}")
    print(f"  log(TSIMM) mean: {tsimm_mu:.4f}, std: {tsimm_sd:.4f}")

    z_main = panel.loc[main_mask, MODERATOR].dropna()
    print(f"  z(log(TSIMM)) on Main: mean={z_main.mean():.4f}, std={z_main.std():.4f}")

    # --- IV: mean-center on Main sample ---
    iv_main = panel.loc[main_mask, IV].dropna()
    iv_mu = iv_main.mean()

    panel[IV_CENTERED] = panel[IV] - iv_mu

    print(f"  IV mean (Main): {iv_mu:.4f}")
    print(f"  IV centered mean (Main): {panel.loc[main_mask, IV_CENTERED].mean():.4f}")

    params = {
        "tsimm_mu": tsimm_mu,
        "tsimm_sd": tsimm_sd,
        "iv_mu": iv_mu,
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
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    required = [dv, IV, IV_CENTERED, MODERATOR] + all_controls + ["gvkey", "fyearq_int", "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Create interaction term using CENTERED IV to avoid multicollinearity
    # Without centering: Corr(moderator, interaction) ≈ 0.93
    # With centering:    Corr(moderator, interaction) ≈ 0.12
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
    n_firm_years = df.groupby(["gvkey", "fyearq_int"]).ngroups
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {n_firms:,} firms, {n_firm_years:,} firm-years")

    return df


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any]
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with Industry+FY FE and firm-clustered SEs."""
    dv = spec["dv"]
    col_num = spec["col"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE=Industry+FY")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    # Use centered IV in regression so main-effect coefficient represents
    # the effect at mean TSIMM, and interaction is cleanly identified
    exog = [IV_CENTERED, MODERATOR, INTERACTION] + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_firm_years = df_prepared.groupby(["gvkey", "fyearq_int"]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-years={n_firm_years:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])

    try:
        model_obj = PanelOLS(
            dependent=df_panel[dv],
            exog=df_panel[exog],
            entity_effects=False,
            time_effects=True,
            other_effects=df_panel["ff12_code"],
            drop_absorbed=True,
            check_rank=False,
        )
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()

    # Extract coefficients (IV is centered; coefficient = effect at mean TSIMM)
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

    # Extract lagged DV control if present
    beta_lag_dv = np.nan
    se_lag_dv = np.nan
    p_two_lag_dv = np.nan
    if "CashHoldings" in extra_controls:
        beta_lag_dv = float(model.params.get("CashHoldings", np.nan))
        se_lag_dv = float(model.std_errors.get("CashHoldings", np.nan))
        p_two_lag_dv = float(model.pvalues.get("CashHoldings", np.nan))

    stars_iv = _sig_stars_one(p_one_iv)
    stars_int = _sig_stars_two(p_two_int)

    print(f"  [OK] {elapsed:.1f}s | R2w={model.rsquared_within:.4f}")
    print(f"  {IV}: b={beta_iv:.4f} p1={p_one_iv:.4f} {stars_iv}")
    print(f"  {MODERATOR}: b={beta_mod:.4f} p2={p_two_mod:.4f}")
    print(f"  INTERACTION: b={beta_int:.4f} p2={p_two_int:.4f} {stars_int}")
    if not np.isnan(beta_lag_dv):
        print(f"  CashHoldings_t (control): b={beta_lag_dv:.4f}")

    meta = {
        "col": col_num,
        "dv": dv,
        "fe": "industry",
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "n_firm_years": n_firm_years,
        "within_r2": float(model.rsquared_within),
        "beta_iv": beta_iv, "se_iv": se_iv,
        "p_one_iv": p_one_iv, "p_two_iv": p_two_iv,
        "beta_moderator": beta_mod, "se_moderator": se_mod, "p_two_moderator": p_two_mod,
        "beta_interaction": beta_int, "se_interaction": se_int, "p_two_interaction": p_two_int,
        "beta_lag_dv": beta_lag_dv, "se_lag_dv": se_lag_dv, "p_two_lag_dv": p_two_lag_dv,
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
        r"\caption{Product Similarity--Moderated Speech Uncertainty and Cash Holdings}",
        r"\label{tab:h1_1_cash_tsimm}",
        r"\small",
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r" & (1) & (2) \\",
        r" & Cash Holdings$_t$ & Cash Holdings$_{t+1}$ \\",
        r"\midrule",
    ]

    # Main IV row
    for col in [1, 2]:
        pass  # handled below

    m1 = results_by_col.get(1, {})
    m2 = results_by_col.get(2, {})

    # IV coefficient
    lines.append(
        f"Mgr Pres Uncertainty & "
        f"{fmt_coef(m1.get('beta_iv', np.nan), _sig_stars_one(m1.get('p_one_iv', np.nan)))} & "
        f"{fmt_coef(m2.get('beta_iv', np.nan), _sig_stars_one(m2.get('p_one_iv', np.nan)))} \\\\"
    )
    lines.append(
        f" & {fmt_se(m1.get('se_iv', np.nan))} & {fmt_se(m2.get('se_iv', np.nan))} \\\\"
    )

    # Moderator coefficient
    lines.append(
        f"$z(\\log(\\mathrm{{TSIMM}}))$ & "
        f"{fmt_coef(m1.get('beta_moderator', np.nan), _sig_stars_two(m1.get('p_two_moderator', np.nan)))} & "
        f"{fmt_coef(m2.get('beta_moderator', np.nan), _sig_stars_two(m2.get('p_two_moderator', np.nan)))} \\\\"
    )
    lines.append(
        f" & {fmt_se(m1.get('se_moderator', np.nan))} & {fmt_se(m2.get('se_moderator', np.nan))} \\\\"
    )

    # Interaction coefficient (key)
    lines.append(
        f"Mgr Pres Unc $\\times$ $z(\\log(\\mathrm{{TSIMM}}))$ & "
        f"{fmt_coef(m1.get('beta_interaction', np.nan), _sig_stars_two(m1.get('p_two_interaction', np.nan)))} & "
        f"{fmt_coef(m2.get('beta_interaction', np.nan), _sig_stars_two(m2.get('p_two_interaction', np.nan)))} \\\\"
    )
    lines.append(
        f" & {fmt_se(m1.get('se_interaction', np.nan))} & {fmt_se(m2.get('se_interaction', np.nan))} \\\\"
    )

    # Lagged DV control (col 2 only)
    if not np.isnan(m2.get("beta_lag_dv", np.nan)):
        lines.append(
            f"Cash Holdings$_t$ & & "
            f"{fmt_coef(m2['beta_lag_dv'], _sig_stars_two(m2.get('p_two_lag_dv', np.nan)))} \\\\"
        )
        lines.append(
            f" & & {fmt_se(m2.get('se_lag_dv', np.nan))} \\\\"
        )

    lines.append(r"\midrule")

    # Footer
    lines.append(r"Controls & Extended & Extended \\")
    lines.append(r"Industry FE & Yes & Yes \\")
    lines.append(r"Fiscal Year FE & Yes & Yes \\")
    lines.append(r"\midrule")

    # N calls
    lines.append(
        f"N (calls) & {m1.get('n_obs', 0):,} & {m2.get('n_obs', 0):,} \\\\"
    )
    # N firm-years
    lines.append(
        f"N (firm-years) & {m1.get('n_firm_years', 0):,} & {m2.get('n_firm_years', 0):,} \\\\"
    )
    # Within R²
    lines.append(
        f"Within-R$^2$ & {fmt_r2(m1.get('within_r2', np.nan))} & "
        f"{fmt_r2(m2.get('within_r2', np.nan))} \\\\"
    )

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$. ",
        r"Main IV (Mgr Pres Uncertainty) mean-centered; one-tailed ($\beta > 0$). ",
        r"Interaction and moderator: two-tailed. ",
        r"IV coefficient represents effect at sample-mean uncertainty. ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"Main sample (excludes financial and utility firms). ",
        r"TNIC3TSIMM is the Hoberg--Phillips (2016) total product similarity measure, ",
        r"log-transformed and standardized on the main sample. ",
        r"Col~(2) includes Cash Holdings$_t$ as additional control. ",
        r"TNIC3TSIMM is a firm-year variable repeated across calls within the same firm-year. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_1_cash_tsimm_table.tex"
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
            f.write(f"H1.1 TNIC-Moderated Cash Holdings Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IV: {IV}\n")
            f.write(f"Moderator: z(log(TNIC3TSIMM))\n")
            f.write(f"Interaction: {INTERACTION}\n")
            f.write(f"FE: Industry(FF12) + FiscalYear\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
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
    duration: float, tsimm_mu: float, tsimm_sd: float,
) -> None:
    """Generate markdown report."""
    lines = [
        "# H1.1 TNIC-Moderated Cash Holdings Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** Manager_Pres_Uncertainty x z(log(TNIC3TSIMM)) interaction",
        f"**Moderator:** TNIC3TSIMM (Hoberg & Phillips JPE 2016), log-transformed, z-scored",
        f"**z-score parameters:** mu(log(TSIMM))={tsimm_mu:.4f}, sd(log(TSIMM))={tsimm_sd:.4f}",
        f"**FE:** Industry(FF12) + FiscalYear (all models)",
        f"**Parent suite:** H1 (Cash Holdings)",
        "",
        "## Model Specifications",
        "",
        "| Col | DV | Extra Controls |",
        "|-----|-----|----------------|",
        "| (1) | CashHoldings_t | — |",
        "| (2) | CashHoldings_lead | CashHoldings_t |",
        "",
        "## Results",
        "",
        "| Col | DV | b_iv | p1_iv | b_interaction | p2_interaction | N calls | N firm-years | R2w |",
        "|-----|----|------|-------|---------------|----------------|---------|-------------|-----|",
    ]

    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        stars_iv = _sig_stars_one(m["p_one_iv"])
        stars_int = _sig_stars_two(m["p_two_interaction"])
        lines.append(
            f"| ({m['col']}) | {m['dv']} | {m['beta_iv']:.4f}{stars_iv} | "
            f"{m['p_one_iv']:.4f} | {m['beta_interaction']:.4f}{stars_int} | "
            f"{m['p_two_interaction']:.4f} | {m['n_obs']:,} | {m['n_firm_years']:,} | "
            f"{m['within_r2']:.4f} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Main IV (Mgr Pres Unc): one-tailed test (H1: beta > 0)")
    lines.append("- Interaction: two-tailed test")
    lines.append("- TNIC3TSIMM is a firm-year variable, repeated across calls within firm-year")
    lines.append("- Col (2) adds CashHoldings_t as control to address persistence (AR(1) > 0.9)")
    lines.append("- SEs firm-clustered throughout")

    with open(out_dir / "report_step4_H1_1.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_1.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h1_1_cash_tsimm" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_1_CashTSIMM",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.1 TNIC-Moderated Cash Holdings")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    1 IV x 2 DVs x Industry+FY FE = 2 models")
    print(f"Moderator: z(log(TNIC3TSIMM))")
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
    print(f"  CashHoldings non-null: {panel['CashHoldings'].notna().sum():,}")
    print(f"  CashHoldings_lead non-null: {panel['CashHoldings_lead'].notna().sum():,}")
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
        caption="Summary Statistics --- H1.1 TNIC-Moderated Cash Holdings (Main Sample)",
        label="tab:summary_stats_h1_1",
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
            attrition_stages, out_dir, "H1.1 TNIC-Moderated Cash Holdings",
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
    generate_report(all_results, out_dir, duration,
                    transform_params["tsimm_mu"], transform_params["tsimm_sd"])

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
