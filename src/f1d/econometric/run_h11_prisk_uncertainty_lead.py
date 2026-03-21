#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H11-Lead Political Risk (Lead) - Language Uncertainty Hypothesis
================================================================================
ID: econometric/test_h11_prisk_uncertainty_lead
Description: Run H11-Lead Political Risk hypothesis tests by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample and uncertainty measure, and outputting results.

             Tests BOTH 1-quarter lead (PRiskQ_lead) AND 2-quarter lead (PRiskQ_lead2).

Model Specification:
    Uncertainty_t ~ PRiskQ_lead_t + Controls_it + EntityEffects + TimeEffects
    Uncertainty_t ~ PRiskQ_lead2_t + Controls_it + EntityEffects + TimeEffects

Dependent Variables:
    1. Manager_QA_Uncertainty_pct
    2. CEO_QA_Uncertainty_pct
    3. Manager_Pres_Uncertainty_pct
    4. CEO_Pres_Uncertainty_pct

Independent Variables:
    - PRiskQ_lead: Political risk from quarter t+1 (1-quarter lead)
    - PRiskQ_lead2: Political risk from quarter t+2 (2-quarter lead)

Dynamic Covariates:
    - If DV is a QA measure, the corresponding Presentation measure is added as a control.
      (e.g., Manager_QA regressions control for Manager_Pres_Uncertainty_pct)
    - Analyst_QA_Uncertainty_pct is always included as a control.

Hypothesis Tests (one-tailed):
    H11-Lead:  beta(PRiskQ_lead) > 0  -- higher next-quarter political risk increases speech uncertainty
    H11-Lead2: beta(PRiskQ_lead2) > 0 -- higher 2-quarter ahead political risk increases speech uncertainty

    NOTE: Lead tests are placebo tests for reverse causality.
    Expected result: Lead coefficients should be insignificant (future PRisk cannot cause current speech).

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls to be included in regression.

Inputs:
    - outputs/variables/h11_prisk_uncertainty_lead/latest/h11_prisk_uncertainty_lead_panel.parquet

Outputs:
    - outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/regression_results_{sample}_{dv}_{lead}.txt
    - outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/h11_prisk_uncertainty_lead_table.tex
    - outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/summary_stats.csv
    - outputs/econometric/h11_prisk_uncertainty_lead/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h11_prisk_uncertainty_lead_panel)
    - Uses: statsmodels, linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-07
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample

# Silence statsmodels covariance warnings
warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)

CONFIG = {
    "min_calls": 5,
    "dependent_variables": [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ],
    "samples": ["Main", "Finance", "Utility"],
    "iv_vars": ["PRiskQ_lead", "PRiskQ_lead2"],  # Test both lead-1 and lead-2
}

BASE_CONTROLS = [
    "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
    "Size",
    "TobinsQ",
    "ROA",
    "CashHoldings",
    "DividendPayer",
    "firm_maturity",
    "earnings_volatility",
]

PRES_CONTROL_MAP = {
    "Manager_QA_Uncertainty_pct": "Manager_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct": "CEO_Pres_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct": None,
    "CEO_Pres_Uncertainty_pct": None,
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables (uncertainty measures)
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # Main independent variables (lead)
    {"col": "PRiskQ_lead", "label": "Political Risk$_{t+1}$"},
    {"col": "PRiskQ_lead2", "label": "Political Risk$_{t+2}$"},
    # Controls
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    {"col": "Entire_All_Negative_pct", "label": "Negative Sentiment"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "firm_maturity", "label": "Firm Maturity"},
    {"col": "earnings_volatility", "label": "Earnings Volatility"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H11-Lead Political Risk Uncertainty Hypothesis (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H11-Lead panel parquet"
    )
    return parser.parse_args()


def prepare_regression_data(
    panel: pd.DataFrame,
    dv_var: str,
    iv_var: str,
) -> Tuple[pd.DataFrame, List[str]]:
    pres_control = PRES_CONTROL_MAP.get(dv_var)
    controls = list(BASE_CONTROLS)
    if pres_control:
        controls.append(pres_control)

    required = [dv_var, iv_var] + controls + ["gvkey", "year"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing required columns in panel: {missing}")

    df = panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    return df, controls


def run_regression(
    df_sample: pd.DataFrame,
    dv_var: str,
    sample_name: str,
    iv_var: str,
    controls: List[str],
) -> Tuple[Any, Dict[str, Any]]:
    formula = (
        f"{dv_var} ~ 1 + {iv_var} + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )

    print(
        f"  Formula: {dv_var} ~ {iv_var} + {' + '.join(controls)} + EntityEffects + TimeEffects"
    )
    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating with firm-clustered SEs via PanelOLS...")

    t0 = datetime.now()

    df_panel = df_sample.set_index(["gvkey", "year"])

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared (within): {model.rsquared_within:.4f}")
    print(f"  Adj R-squared:      {model.rsquared_inclusive:.4f}")
    print(f"  N obs:              {int(model.nobs):,}")

    within_r2 = float(model.rsquared_within)
    print(f"  Within-R2: {within_r2:.4f}")

    beta_prisk = model.params.get(iv_var, np.nan)
    p_two = model.pvalues.get(iv_var, np.nan)
    beta_se = model.std_errors.get(iv_var, np.nan)
    beta_t = model.tstats.get(iv_var, np.nan)

    # Hypothesis test: beta > 0 (one-tailed)
    if not np.isnan(p_two) and not np.isnan(beta_prisk):
        p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2
    else:
        p_one = np.nan

    h_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0
    h_text = "YES" if h_sig else "no"

    print(
        f"  beta1 ({iv_var}):   {beta_prisk:.4f}  SE={beta_se:.4f}  p(one-tail)={p_one:.4f}  H={h_text}"
    )

    # Determine hypothesis name based on IV
    hyp_name = "h11_lead_sig" if iv_var == "PRiskQ_lead" else "h11_lead2_sig"

    meta = {
        "dv": dv_var,
        "sample": sample_name,
        "iv": iv_var,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters": df_sample["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "within_r2": within_r2,
        "rsquared_inclusive": float(model.rsquared_inclusive),
        "beta_prisk": float(beta_prisk),
        "beta_prisk_se": float(beta_se),
        "beta_prisk_t": float(beta_t),
        "beta_prisk_p_two": float(p_two),
        "beta_prisk_p_one": float(p_one),
        hyp_name: h_sig,
    }

    return model, meta


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    tex_path = out_dir / "h11_prisk_uncertainty_lead_table.tex"

    # Get results for Main sample, lead-1
    def get_res_lead1(dv):
        for r in all_results:
            if r.get("sample") == "Main" and r.get("dv") == dv and r.get("iv") == "PRiskQ_lead":
                return r
        return None

    # Get results for Main sample, lead-2
    def get_res_lead2(dv):
        for r in all_results:
            if r.get("sample") == "Main" and r.get("dv") == dv and r.get("iv") == "PRiskQ_lead2":
                return r
        return None

    r_mq_1 = get_res_lead1("Manager_QA_Uncertainty_pct")
    r_cq_1 = get_res_lead1("CEO_QA_Uncertainty_pct")
    r_mp_1 = get_res_lead1("Manager_Pres_Uncertainty_pct")
    r_cp_1 = get_res_lead1("CEO_Pres_Uncertainty_pct")

    r_mq_2 = get_res_lead2("Manager_QA_Uncertainty_pct")
    r_cq_2 = get_res_lead2("CEO_QA_Uncertainty_pct")
    r_mp_2 = get_res_lead2("Manager_Pres_Uncertainty_pct")
    r_cp_2 = get_res_lead2("CEO_Pres_Uncertainty_pct")

    def fmt_coef(val, pval):
        if val is None or pd.isna(val):
            return ""
        stars = ""
        if pval < 0.01:
            stars = "^{***}"
        elif pval < 0.05:
            stars = "^{**}"
        elif pval < 0.10:
            stars = "^{*}"
        return f"{val:.4f}{stars}"

    def fmt_se(val):
        if val is None or pd.isna(val):
            return ""
        return f"({val:.4f})"

    def fmt_r2(val):
        if val is None or pd.isna(val):
            return ""
        if abs(val) < 0.001:
            return f"{val:.2e}"
        return f"{val:.4f}"

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{H11-Lead: Political Risk (Lead) and Language Uncertainty}",
        "\\label{tab:h11_prisk_uncertainty_lead}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        " & \\multicolumn{2}{c}{Q\\&A Session} & \\multicolumn{2}{c}{Presentation} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}",
        " & Mgr Unc & CEO Unc & Mgr Unc & CEO Unc \\\\",
        " & (1) & (2) & (3) & (4) \\\\",
        "\\midrule",
    ]

    # Row 1: PRiskQ_lead (t+1)
    r1 = "Political Risk$_{t+1}$ & "
    r1 += f"{fmt_coef(r_mq_1['beta_prisk'], r_mq_1['beta_prisk_p_one'])} & " if r_mq_1 else " & "
    r1 += f"{fmt_coef(r_cq_1['beta_prisk'], r_cq_1['beta_prisk_p_one'])} & " if r_cq_1 else " & "
    r1 += f"{fmt_coef(r_mp_1['beta_prisk'], r_mp_1['beta_prisk_p_one'])} & " if r_mp_1 else " & "
    r1 += f"{fmt_coef(r_cp_1['beta_prisk'], r_cp_1['beta_prisk_p_one'])} \\\\" if r_cp_1 else " \\\\"
    lines.append(r1)

    # Row 2: SE for lead-1
    r2 = " & "
    r2 += f"{fmt_se(r_mq_1['beta_prisk_se'])} & " if r_mq_1 else " & "
    r2 += f"{fmt_se(r_cq_1['beta_prisk_se'])} & " if r_cq_1 else " & "
    r2 += f"{fmt_se(r_mp_1['beta_prisk_se'])} & " if r_mp_1 else " & "
    r2 += f"{fmt_se(r_cp_1['beta_prisk_se'])} \\\\" if r_cp_1 else " \\\\"
    lines.append(r2)

    # Row 3: PRiskQ_lead2 (t+2)
    r3 = "Political Risk$_{t+2}$ & "
    r3 += f"{fmt_coef(r_mq_2['beta_prisk'], r_mq_2['beta_prisk_p_one'])} & " if r_mq_2 else " & "
    r3 += f"{fmt_coef(r_cq_2['beta_prisk'], r_cq_2['beta_prisk_p_one'])} & " if r_cq_2 else " & "
    r3 += f"{fmt_coef(r_mp_2['beta_prisk'], r_mp_2['beta_prisk_p_one'])} & " if r_mp_2 else " & "
    r3 += f"{fmt_coef(r_cp_2['beta_prisk'], r_cp_2['beta_prisk_p_one'])} \\\\" if r_cp_2 else " \\\\"
    lines.append(r3)

    # Row 4: SE for lead-2
    r4 = " & "
    r4 += f"{fmt_se(r_mq_2['beta_prisk_se'])} & " if r_mq_2 else " & "
    r4 += f"{fmt_se(r_cq_2['beta_prisk_se'])} & " if r_cq_2 else " & "
    r4 += f"{fmt_se(r_mp_2['beta_prisk_se'])} & " if r_mp_2 else " & "
    r4 += f"{fmt_se(r_cp_2['beta_prisk_se'])} \\\\" if r_cp_2 else " \\\\"
    lines.append(r4)

    lines.extend(
        [
            "\\midrule",
            "Negative Sentiment & Yes & Yes & Yes & Yes \\\\",
            "Controls & Yes & Yes & Yes & Yes \\\\",
            "Firm FE & Yes & Yes & Yes & Yes \\\\",
            "Year FE & Yes & Yes & Yes & Yes \\\\",
            "\\midrule",
        ]
    )

    # Observations row (use lead-1 results for consistency)
    rn = "Observations & "
    rn += f"{r_mq_1['n_obs']:,} & " if r_mq_1 else " & "
    rn += f"{r_cq_1['n_obs']:,} & " if r_cq_1 else " & "
    rn += f"{r_mp_1['n_obs']:,} & " if r_mp_1 else " & "
    rn += f"{r_cp_1['n_obs']:,} \\\\" if r_cp_1 else " \\\\"
    lines.append(rn)

    rr = "Within-$R^2$ & "
    rr += f"{fmt_r2(r_mq_1['within_r2'])} & " if r_mq_1 else " & "
    rr += f"{fmt_r2(r_cq_1['within_r2'])} & " if r_cq_1 else " & "
    rr += f"{fmt_r2(r_mp_1['within_r2'])} & " if r_mp_1 else " & "
    rr += f"{fmt_r2(r_cp_1['within_r2'])} \\\\" if r_cp_1 else " \\\\"
    lines.append(rr)

    lines.extend(["\\bottomrule", "\\end{tabular}"])
    # Add table notes
    lines.extend([
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} ",
        "This table reports the effect of lead political risk on language uncertainty. ",
        "Political Risk$_{t+1}$ is measured one quarter after the earnings call; ",
        "Political Risk$_{t+2}$ is measured two quarters after. ",
        "Columns (1)--(2) use Q\\&A session measures; columns (3)--(4) use presentation measures. ",
        "All models use the Main industry sample (non-financial, non-utility firms). ",
        "Firms with fewer than 5 calls are excluded. ",
        "Standard errors are clustered at the firm level. ",
        "All continuous controls are standardized. ",
        "Variables are winsorized at 1\\%/99\\% by year. ",
        "Lead tests are placebo tests for reverse causality; coefficients are expected to be insignificant.",
        "}",
        "\\end{table}",
    ])

    with open(tex_path, "w") as f:
        f.write("\n".join(lines))


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h11_prisk_uncertainty_lead" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H11_PRisk_Uncertainty_Lead",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H11-Lead Political Risk - Language Uncertainty Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h11_prisk_uncertainty_lead",
                required_file="h11_prisk_uncertainty_lead_panel.parquet",
            )
            panel_file = panel_dir / "h11_prisk_uncertainty_lead_panel.parquet"
        except Exception as e:
            print(f"ERROR: Could not find Stage 3 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    print(f"  Loaded: {panel_file}")
    panel = pd.read_parquet(
        panel_file,
        columns=[
            "file_name",
            "gvkey",
            "year",
            "ff12_code",
            # Dependent variables (uncertainty measures)
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            # Primary predictors (lead)
            "PRiskQ_lead",
            "PRiskQ_lead2",
            # Base controls
            "Analyst_QA_Uncertainty_pct",
            "Entire_All_Negative_pct",
            "Size",
            "TobinsQ",
            "ROA",
            "CashHoldings",
            "DividendPayer",
            "firm_maturity",
            "earnings_volatility",
        ],
    )
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Summary Statistics (call-level, by sample)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    summary_vars = [
        {"col": v["col"], "label": v["label"]}
        for v in SUMMARY_STATS_VARS
        if v["col"] in panel.columns
    ]
    make_summary_stats_table(
        df=panel,
        variables=summary_vars,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics - H11-Lead Political Risk Uncertainty",
        label="tab:summary_stats_h11_lead",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    all_results = []

    # Run regressions for each DV, sample, and IV combination
    for iv_var in CONFIG["iv_vars"]:
        print(f"\n{'=' * 60}")
        print(f"Testing IV: {iv_var}")
        print("=" * 60)

        for dv in CONFIG["dependent_variables"]:
            for sample in CONFIG["samples"]:
                print(f"\n--- {sample} / {dv} / {iv_var} ---")

                df_prep, controls = prepare_regression_data(panel, dv, iv_var)

                if sample == "Main":
                    df_sample = df_prep[df_prep["sample"] == "Main"].copy()
                elif sample == "Finance":
                    df_sample = df_prep[df_prep["sample"] == "Finance"].copy()
                else:
                    df_sample = df_prep[df_prep["sample"] == "Utility"].copy()

                df_sample["gvkey_count"] = df_sample.groupby("gvkey")[
                    "file_name"
                ].transform("count")
                df_filtered = df_sample[
                    df_sample["gvkey_count"] >= CONFIG["min_calls"]
                ].copy()

                print(
                    f"  After filters: {len(df_filtered):,} calls, {df_filtered['gvkey'].nunique():,} firms"
                )

                if len(df_filtered) < 100:
                    print("  Skipping: insufficient data")
                    continue

                print(f"\n============================================================")
                print(f"Running regression: {sample} / {dv} / {iv_var}")
                print(f"============================================================")

                model, meta = run_regression(df_filtered, dv, sample, iv_var, controls)

                if model is not None:
                    all_results.append(meta)
                    # Save individual regression results with lead version in filename
                    lead_suffix = "lead1" if iv_var == "PRiskQ_lead" else "lead2"
                    with open(out_dir / f"regression_results_{sample}_{dv}_{lead_suffix}.txt", "w") as f:
                        f.write(str(model.summary))

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")

    # Generate sample attrition table
    if all_results:
        main_result = next(
            (r for r in all_results if r.get("sample") == "Main" and r.get("iv") == "PRiskQ_lead"),
            all_results[0]
        )
        attrition_stages = [
            ("Master manifest", len(panel)),
            ("Main sample filter", (panel["sample"] == "Main").sum()),
            ("After complete-case + min-calls filter", main_result.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H11-Lead Political Risk Uncertainty")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h11_prisk_uncertainty_lead_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = parse_arguments()
    sys.exit(main(panel_path=parser.panel_path))
