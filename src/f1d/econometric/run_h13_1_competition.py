#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H13.1 Competition-Moderated Capex Hypothesis
================================================================================
ID: econometric/run_h13_1_competition
Description: Test whether product market competition (Hoberg-Phillips TNIC3HHI)
             moderates the uncertainty-capex relationship. Each of 6 IVs gets
             its own regression with its own interaction term.

Model Specification (one IV per model):
    CapexAt = b1*IV_k + b2*tnic3hhi + b3*(IV_k x tnic3hhi) + controls + FE + e

    b3 is the coefficient of interest: does competitive intensity moderate
    the effect of uncertainty language on capital expenditure?

6 IVs (tested separately, one per model):
    CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct,
    Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct,
    CEO_Clarity_Residual, Manager_Clarity_Residual

2 DVs: CapexAt (t) and CapexAt_lead (t+1)
2 FE: Industry(FF12)+FiscalYear, Firm+FiscalYear
= 24 total regressions

Controls (Extended): Size, TobinsQ, ROA, Lev, CashHoldings, DividendPayer,
    OCF_Volatility, SalesGrowth, RD_Intensity, CashFlow, Volatility

Competition measure: TNIC3HHI (Hoberg & Phillips JPE 2016)
    Firm-specific text-based HHI from 10-K business descriptions.
    High HHI = concentrated market. Low HHI = competitive market.

Sample: Main only (FF12 not in {8, 11}).
Hypothesis: Two-tailed on interaction (b3 != 0).
Unit: Call-level (loads H13 panel, merges TNIC at load time).
Panel index: ["gvkey", "fyearq_int"].
SEs: Firm-clustered.

Inputs:
    - outputs/variables/h13_capex/latest/h13_capex_panel.parquet
    - inputs/TNIC3HHIdata/TNIC3HHIdata.txt

Outputs:
    - outputs/econometric/h13_1_competition/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-03-17
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

INDIVIDUAL_IVS = [
    "CEO_QA_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Clarity_Residual",
    "Manager_Clarity_Residual",
]

CONTROLS = [
    "Size", "TobinsQ", "ROA", "Lev", "CashHoldings",
    "DividendPayer", "OCF_Volatility",
    "SalesGrowth", "RD_Intensity", "CashFlow", "Volatility",
]

DVS = ["CapexAt", "CapexAt_lead"]
FE_TYPES = ["industry", "firm"]

MIN_CALLS_PER_FIRM = 5

IV_LABELS = {
    "CEO_QA_Uncertainty_pct": "CEO QA Unc",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Unc",
    "Manager_QA_Uncertainty_pct": "Mgr QA Unc",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Unc",
    "CEO_Clarity_Residual": "CEO Clarity",
    "Manager_Clarity_Residual": "Mgr Clarity",
}


def _build_model_specs() -> List[Dict[str, str]]:
    """Generate 24 model specs: 6 IVs x 2 DVs x 2 FE."""
    specs = []
    col = 0
    for dv in DVS:
        for fe in FE_TYPES:
            for iv in INDIVIDUAL_IVS:
                col += 1
                specs.append({"col": col, "iv": iv, "dv": dv, "fe": fe})
    return specs


MODEL_SPECS = _build_model_specs()


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H13.1 Competition-Moderated Capex (call-level)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel_with_tnic(
    root_path: Path, panel_path: Optional[str] = None
) -> pd.DataFrame:
    """Load H13 call-level panel and merge TNIC3HHI at load time."""
    print("\n" + "=" * 60)
    print("Loading H13 panel + TNIC3HHI")
    print("=" * 60)

    # Load H13 panel
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h13_capex",
            required_file="h13_capex_panel.parquet",
        )
        panel_file = panel_dir / "h13_capex_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded panel: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")

    # Load TNIC3HHI
    tnic_path = root_path / "inputs" / "TNIC3HHIdata" / "TNIC3HHIdata.txt"
    if not tnic_path.exists():
        raise FileNotFoundError(f"TNIC data not found: {tnic_path}")

    tnic = pd.read_csv(tnic_path, sep="\t")
    print(f"  Loaded TNIC: {len(tnic):,} rows, years {tnic['year'].min()}-{tnic['year'].max()}")

    # Merge: panel gvkey (str zero-padded) -> int, fyearq_int (float) kept as-is
    # NaN-safe: pandas handles float-to-int merge correctly (2005.0 == 2005)
    panel["_gvkey_int"] = pd.to_numeric(panel["gvkey"], errors="coerce")

    before = len(panel)
    panel = panel.merge(
        tnic[["gvkey", "year", "tnic3hhi"]].rename(
            columns={"gvkey": "_gvkey_int", "year": "fyearq_int"}
        ),
        on=["_gvkey_int", "fyearq_int"],
        how="left",
    )
    assert len(panel) == before, f"TNIC merge changed row count: {before} -> {len(panel)}"
    panel = panel.drop(columns=["_gvkey_int"])

    n_matched = panel["tnic3hhi"].notna().sum()
    print(f"  TNIC match: {n_matched:,} / {len(panel):,} ({100*n_matched/len(panel):.1f}%)")
    print(f"  tnic3hhi: mean={panel['tnic3hhi'].mean():.3f}, "
          f"median={panel['tnic3hhi'].median():.3f}")

    return panel, panel_file


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any]
) -> pd.DataFrame:
    """Prepare data for one regression spec with interaction term."""
    iv = spec["iv"]
    dv = spec["dv"]
    interaction_col = f"{iv}_x_hhi"

    required = [dv, iv, "tnic3hhi"] + CONTROLS + ["gvkey", "fyearq_int", "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Require ALL 6 IVs non-missing (match H13's sample for apples-to-apples comparison)
    all_ivs_mask = df[INDIVIDUAL_IVS].notna().all(axis=1)
    df = df[all_ivs_mask].copy()

    # Create interaction term
    df[interaction_col] = df[iv] * df["tnic3hhi"]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()

    # Complete cases (including tnic3hhi and interaction)
    all_required = required + [interaction_col]
    complete_mask = df[all_required].notna().all(axis=1)
    df = df[complete_mask].copy()

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()

    print(f"  Prepared: {len(df):,} calls, {df['gvkey'].nunique():,} firms "
          f"(from {before:,})")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any]
) -> Tuple[Any, Dict[str, Any]]:
    """Run one PanelOLS regression with IV + HHI + interaction."""
    iv = spec["iv"]
    dv = spec["dv"]
    fe_type = spec["fe"]
    col_num = spec["col"]
    interaction_col = f"{iv}_x_hhi"

    print(f"\n{'='*60}")
    print(f"Col ({col_num}) | IV={IV_LABELS.get(iv,iv)} | DV={dv} | FE={fe_type}")
    print(f"{'='*60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    exog = [iv, "tnic3hhi", interaction_col] + CONTROLS

    print(f"  N={len(df_prepared):,}, firms={df_prepared['gvkey'].nunique():,}")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])

    try:
        if fe_type == "industry":
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
        else:
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()

    # Extract key coefficients
    beta_iv = float(model.params.get(iv, np.nan))
    se_iv = float(model.std_errors.get(iv, np.nan))
    p_iv = float(model.pvalues.get(iv, np.nan))

    beta_hhi = float(model.params.get("tnic3hhi", np.nan))
    se_hhi = float(model.std_errors.get("tnic3hhi", np.nan))
    p_hhi = float(model.pvalues.get("tnic3hhi", np.nan))

    beta_int = float(model.params.get(interaction_col, np.nan))
    se_int = float(model.std_errors.get(interaction_col, np.nan))
    p_int = float(model.pvalues.get(interaction_col, np.nan))

    stars_int = _sig_stars(p_int)

    print(f"  [OK] {elapsed:.1f}s | R2w={model.rsquared_within:.4f}")
    print(f"  {iv}: b={beta_iv:.4f} p={p_iv:.4f}")
    print(f"  tnic3hhi: b={beta_hhi:.4f} p={p_hhi:.4f}")
    print(f"  INTERACTION: b={beta_int:.4f} p={p_int:.4f} {stars_int}")

    meta = {
        "col": col_num,
        "iv": iv,
        "dv": dv,
        "fe": fe_type,
        "n_obs": int(model.nobs),
        "n_firms": df_prepared["gvkey"].nunique(),
        "within_r2": float(model.rsquared_within),
        "beta_iv": beta_iv, "se_iv": se_iv, "p_two_iv": p_iv,
        "beta_hhi": beta_hhi, "se_hhi": se_hhi, "p_two_hhi": p_hhi,
        "beta_interaction": beta_int, "se_interaction": se_int, "p_two_interaction": p_int,
    }

    return model, meta


def _sig_stars(p: float) -> str:
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


def _save_latex_table(
    all_results: List[Dict[str, Any]], dv: str, out_dir: Path
) -> None:
    """Write LaTeX table for one DV with Panel A (Industry FE) + Panel B (Firm FE)."""

    def _panel(fe_type: str, panel_label: str) -> List[str]:
        results_for_fe = [
            r for r in all_results
            if r["meta"].get("dv") == dv and r["meta"].get("fe") == fe_type
        ]
        # Sort by IV order
        iv_order = {iv: i for i, iv in enumerate(INDIVIDUAL_IVS)}
        results_for_fe.sort(key=lambda r: iv_order.get(r["meta"]["iv"], 99))

        lines = [
            f"\\multicolumn{{7}}{{l}}{{\\textit{{{panel_label}}}}} \\\\",
            "\\midrule",
        ]

        # Column headers
        col_headers = " & ".join(IV_LABELS.get(r["meta"]["iv"], "?") for r in results_for_fe)
        col_nums = " & ".join(f"({r['meta']['col']})" for r in results_for_fe)
        lines.append(f" & {col_nums} \\\\")
        lines.append(f" & {col_headers} \\\\")
        lines.append("\\midrule")

        # IV row
        coefs = " & ".join(
            f"{r['meta']['beta_iv']:.4f}{_sig_stars(r['meta']['p_two_iv'])}"
            for r in results_for_fe
        )
        ses = " & ".join(f"({r['meta']['se_iv']:.4f})" for r in results_for_fe)
        lines.append(f"$IV_k$ & {coefs} \\\\")
        lines.append(f" & {ses} \\\\")

        # HHI row
        coefs = " & ".join(
            f"{r['meta']['beta_hhi']:.4f}{_sig_stars(r['meta']['p_two_hhi'])}"
            for r in results_for_fe
        )
        ses = " & ".join(f"({r['meta']['se_hhi']:.4f})" for r in results_for_fe)
        lines.append(f"TNIC3HHI & {coefs} \\\\")
        lines.append(f" & {ses} \\\\")

        # Interaction row (key coefficient)
        coefs = " & ".join(
            f"{r['meta']['beta_interaction']:.4f}{_sig_stars(r['meta']['p_two_interaction'])}"
            for r in results_for_fe
        )
        ses = " & ".join(f"({r['meta']['se_interaction']:.4f})" for r in results_for_fe)
        lines.append(f"$IV_k \\times$ HHI & {coefs} \\\\")
        lines.append(f" & {ses} \\\\")

        lines.append("\\midrule")

        # Footer rows
        n_row = " & ".join(f"{r['meta']['n_obs']:,}" for r in results_for_fe)
        r2_row = " & ".join(f"{r['meta']['within_r2']:.3f}" for r in results_for_fe)
        fe_label = "Industry" if fe_type == "industry" else "Firm"
        lines.append(f"Controls & " + " & ".join(["Ext"] * len(results_for_fe)) + " \\\\")
        lines.append(f"{fe_label} FE & " + " & ".join(["Yes"] * len(results_for_fe)) + " \\\\")
        lines.append(f"Fiscal Year FE & " + " & ".join(["Yes"] * len(results_for_fe)) + " \\\\")
        lines.append("\\midrule")
        lines.append(f"N & {n_row} \\\\")
        lines.append(f"Within-R$^2$ & {r2_row} \\\\")

        return lines

    dv_label = "CapEx$_t$ / Assets" if dv == "CapexAt" else "CapEx$_{t+1}$ / Assets"

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{Competition-Moderated Speech Uncertainty and {dv_label}}}",
        f"\\label{{tab:h13_1_{dv.lower()}}}",
        "\\scriptsize",
        "\\begin{tabular}{l" + "c" * 6 + "}",
        "\\toprule",
    ]

    lines += _panel("industry", "Panel A: Industry FE")
    lines.append("\\midrule")
    lines += _panel("firm", "Panel B: Firm FE")

    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\begin{minipage}{\\linewidth}",
        "\\vspace{2pt}\\scriptsize",
        "\\textit{Notes:} ",
        "$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed). ",
        "Standard errors (in parentheses) clustered at firm level. ",
        "Each column runs a separate regression with one IV, TNIC3HHI, and their interaction. ",
        "TNIC3HHI is the Hoberg-Phillips (2016) text-based Herfindahl index. ",
        "Main sample (excludes financial and utility firms). ",
        "Extended controls in all specifications. ",
        "Unit of observation: individual earnings call.",
        "\\end{minipage}",
        "\\end{table}",
    ]

    suffix = "capex" if dv == "CapexAt" else "capex_lead"
    tex_path = out_dir / f"h13_1_competition_table_{suffix}.tex"
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
        iv_short = meta["iv"].replace("_Uncertainty_pct", "").replace("_Residual", "")
        fname = f"regression_results_{iv_short}_{meta['dv']}_{meta['fe']}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            f.write(f"H13.1 Competition-Moderated Regression\n")
            f.write(f"IV: {meta['iv']}\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Interaction: {meta['iv']}_x_hhi\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    # Diagnostics CSV
    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    # LaTeX tables (one per DV)
    for dv in DVS:
        _save_latex_table(all_results, dv, out_dir)

    return diag_df


def generate_report(
    all_results: List[Dict[str, Any]], out_dir: Path, duration: float
) -> None:
    """Generate markdown report."""
    lines = [
        "# H13.1 Competition-Moderated Capex Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** Each IV tested separately with TNIC3HHI interaction",
        f"**Competition measure:** TNIC3HHI (Hoberg & Phillips JPE 2016)",
        "",
        "## Interaction Results (beta_interaction, two-tailed p-values)",
        "",
        "| IV | DV | FE | b_interaction | SE | p | Sig |",
        "|----|----|----|---------------|-----|---|-----|",
    ]
    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        stars = _sig_stars(m["p_two_interaction"])
        lines.append(
            f"| {IV_LABELS.get(m['iv'],m['iv'])} | {m['dv']} | {m['fe']} | "
            f"{m['beta_interaction']:.4f} | {m['se_interaction']:.4f} | "
            f"{m['p_two_interaction']:.4f} | {stars} |"
        )
    lines.append("")

    with open(out_dir / "report_step4_H13_1.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H13_1.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h13_1_competition" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_1_Competition",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H13.1 Competition-Moderated Capex")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    6 IVs x 2 DVs x 2 FE = 24 regressions")
    print(f"Competition: TNIC3HHI (Hoberg & Phillips JPE 2016)")

    # Load panel + TNIC
    panel, panel_file = load_panel_with_tnic(root, panel_path)

    # Filter to Main
    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    stats_vars = [
        {"col": "CapexAt", "label": "CapEx / Assets"},
        {"col": "CapexAt_lead", "label": "CapEx$_{t+1}$ / Assets"},
        {"col": "tnic3hhi", "label": "TNIC3 HHI"},
    ] + [{"col": iv, "label": IV_LABELS.get(iv, iv)} for iv in INDIVIDUAL_IVS]
    make_summary_stats_table(
        df=panel, variables=stats_vars, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics -- H13.1 Competition-Moderated Capex",
        label="tab:summary_stats_h13_1",
    )
    print("  Saved: summary_stats.csv/.tex")

    # Run 24 regressions
    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
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

    # Save
    diag_df = save_outputs(all_results, out_dir)

    # Attrition
    if all_results:
        first = all_results[0]["meta"]
        generate_attrition_table(
            [
                ("Full panel", full_n),
                ("Main sample", main_n),
                ("After TNIC + complete-case + min-calls", first["n_obs"]),
            ],
            out_dir, "H13.1 Competition-Moderated Capex",
        )
        print("  Saved: sample_attrition.csv/.tex")

    # Manifest
    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, out_dir, duration)

    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")
    n_sig = sum(1 for r in all_results if r["meta"]["p_two_interaction"] < 0.05)
    print(f"Significant interactions (p<0.05): {n_sig}/{len(all_results)}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IVs: {len(INDIVIDUAL_IVS)}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(CONTROLS)}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
