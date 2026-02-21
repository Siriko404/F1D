#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Tone-at-the-Top Econometrics (H_TT)
================================================================================
ID: econometric/run_h10_tone_at_top
Description: Executes regressions for the Tone-at-the-Top transmission hypothesis.
             H_TT1: Call-level, real-time CEO style predicts CFO uncertainty.
             H_TT2: Speaker-turn level, prior CEO QA turns predict NonCEO manager uncertainty.
             Model 3: Robustness using full-sample ClarityCEO instead of real-time style.

Outputs:
    - outputs/econometric/tone_at_top/{timestamp}/results_*.csv
    - report.md

Author: Thesis Author
================================================================================
"""

import argparse
from datetime import datetime
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from linearmodels.iv.absorbing import AbsorbingLS

from f1d.shared.path_utils import get_latest_output_dir, ensure_output_dir


def generate_latex_table(df: pd.DataFrame, out_path: Path):
    """Generate publication-ready LaTeX table from results."""
    latex = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Tone-at-the-Top Transmission (H\\_TT)}",
        "\\label{tab:tone_at_top}",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Sample & Model & Coef & t-stat & p-value & N & Adj R$^2$ \\\\",
        "\\midrule",
    ]

    for _, row in df.iterrows():
        # Format numbers
        coef = f"{row['Coef']:.4f}" if pd.notna(row["Coef"]) else ""
        tstat = f"{row['t-stat']:.2f}" if pd.notna(row["t-stat"]) else ""
        pval = f"{row['p-value']:.4f}" if pd.notna(row["p-value"]) else ""
        nobs = f"{int(row['N']):,}" if pd.notna(row["N"]) else ""
        adj_r2 = f"{row['Adj_R2']:.4f}" if pd.notna(row["Adj_R2"]) else ""

        # Add significance stars
        stars = ""
        if pd.notna(row["p-value"]):
            p = float(row["p-value"])
            if p < 0.01:
                stars = "$^{***}$"
            elif p < 0.05:
                stars = "$^{**}$"
            elif p < 0.10:
                stars = "$^{*}$"

        coef_str = f"{coef}{stars}"

        latex.append(
            f"{row['Sample']} & {row['Model']} & {coef_str} & {tstat} & {pval} & {nobs} & {adj_r2} \\\\"
        )

    latex.extend(
        [
            "\\bottomrule",
            "\\multicolumn{7}{l}{\\footnotesize \\textit{Notes:} $^{***}$ p$<$0.01, $^{**}$ p$<$0.05, $^{*}$ p$<$0.10.} \\\\",
            "\\end{tabular}",
            "\\end{table}",
        ]
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(latex) + "\n")


def parse_arguments():
    parser = argparse.ArgumentParser(description="H_TT Econometrics")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without executing"
    )
    return parser.parse_args()


def asinh(series: pd.Series) -> pd.Series:
    """Inverse hyperbolic sine transformation for percentage variables."""
    return pd.Series(np.arcsinh(series.to_numpy()), index=series.index)


def run_call_level_model(
    df: pd.DataFrame, dv: str, iv: str, controls: list
) -> pd.Series:
    """Run Model 1 or 3 (Call-level) with two-way clustering and FEs."""
    reg_df = df.copy()
    reg_df["year_qtr"] = (
        reg_df["year"].astype(str) + "Q" + reg_df["quarter"].astype(str)
    )
    reg_df["yq_id"] = reg_df["year_qtr"].astype("category").cat.codes

    # Drop NAs
    keep_cols = ["file_name", "gvkey", "ceo_id", "yq_id", dv, iv] + controls
    reg_df = reg_df.dropna(subset=keep_cols)

    if len(reg_df) < 50:
        return pd.Series({"N": len(reg_df), "Error": "Too few obs"})

    reg_df["const"] = 1

    # Set multi-index for panel
    reg_df = reg_df.set_index(["gvkey", "yq_id"])

    exog = ["const", iv] + controls

    try:
        mod = PanelOLS(
            dependent=reg_df[dv],
            exog=reg_df[exog],
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
        )
        # Cluster by firm (gvkey) and CEO
        # Linearmodels cluster expects explicit passing of all cluster columns
        # if you want multi-way clustering that is different from the entity effect.
        clusters = pd.DataFrame(
            {
                "gvkey": pd.Categorical(reg_df.index.get_level_values("gvkey")).codes,
                "ceo_id": reg_df["ceo_id"].astype("category").cat.codes,
            },
            index=reg_df.index,
        )
        res = mod.fit(cov_type="clustered", clusters=clusters)

        coef = res.params[iv]
        tstat = res.tstats[iv]
        pval = res.pvalues[iv]

        return pd.Series(
            {
                "N": int(res.nobs),
                "Coef": round(coef, 4),
                "t-stat": round(tstat, 2),
                "p-value": round(pval, 4),
                "Adj_R2": round(res.rsquared_within, 4),
            }
        )
    except Exception as e:
        return pd.Series({"N": len(reg_df), "Error": str(e)})


def run_turn_level_model(
    df: pd.DataFrame, dv: str, iv: str, call_controls: list
) -> pd.Series:
    """Run Model 2 (Speaker-turn level)."""
    reg_df = df.copy()

    keep_cols = [
        "file_name",
        "speaker_name",
        "gvkey",
        "ceo_id",
        dv,
        iv,
    ] + call_controls
    reg_df = reg_df.dropna(subset=keep_cols)

    if len(reg_df) < 50:
        return pd.Series({"N": len(reg_df), "Error": "Too few obs"})

    reg_df["const"] = 1.0
    for col in [dv, iv] + call_controls:
        reg_df[col] = reg_df[col].astype(float)

    exog = ["const", iv] + call_controls

    try:
        absorb_df = reg_df[["speaker_name", "file_name"]].copy()
        absorb_df["speaker_name"] = (
            absorb_df["speaker_name"].astype("category").cat.codes
        )
        absorb_df["file_name"] = absorb_df["file_name"].astype("category").cat.codes

        mod = AbsorbingLS(
            dependent=reg_df[dv],
            exog=reg_df[exog],
            absorb=absorb_df,
            drop_absorbed=True,
        )

        # Two-way cluster by firm and ceo
        clusters = reg_df[["gvkey", "ceo_id"]].copy()
        clusters["gvkey"] = clusters["gvkey"].astype("category").cat.codes
        clusters["ceo_id"] = clusters["ceo_id"].astype("category").cat.codes
        res = mod.fit(cov_type="clustered", clusters=clusters)

        coef = res.params[iv]
        tstat = res.tstats[iv]
        pval = res.pvalues[iv]

        return pd.Series(
            {
                "N": int(res.nobs),
                "Coef": round(coef, 4),
                "t-stat": round(tstat, 2),
                "p-value": round(pval, 4),
                "Adj_R2": round(res.rsquared, 4),
            }
        )
    except Exception as e:
        return pd.Series({"N": len(reg_df), "Error": str(e)})


def main():
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    if args.dry_run:
        print("Dry run OK")
        return

    # Load panels
    panel_dir = get_latest_output_dir(
        root / "outputs" / "variables" / "tone_at_top",
        required_file="tone_at_top_panel.parquet",
    )
    call_panel = pd.read_parquet(panel_dir / "tone_at_top_panel.parquet")
    turns_panel = pd.read_parquet(panel_dir / "tone_at_top_turns_panel.parquet")

    # Add start_date to turns_panel if missing
    if "start_date" not in turns_panel.columns:
        turns_panel = turns_panel.merge(
            call_panel[["file_name", "start_date"]].drop_duplicates(),
            on="file_name",
            how="left",
        )

    # Prep variables - Call panel
    call_panel["IHS_CFO_QA_Unc"] = asinh(call_panel["CFO_QA_Uncertainty_pct"])
    call_panel["IHS_CEO_QA_Unc"] = asinh(call_panel["CEO_QA_Uncertainty_pct"])
    call_panel["IHS_CEO_Pres_Unc"] = asinh(call_panel["CEO_Pres_Uncertainty_pct"])

    # Prep variables - Turns panel
    turns_panel["IHS_NonCEO_Turn_Unc"] = asinh(turns_panel["Turn_Uncertainty_pct"])
    turns_panel["IHS_CEO_Prior_QA_Unc"] = asinh(turns_panel["CEO_Prior_QA_Unc"])
    turns_panel["IHS_CEO_Pres_Unc"] = asinh(turns_panel["CEO_Pres_Uncertainty_pct"])

    call_controls = [
        "Size",
        "BM",
        "Lev",
        "ROA",
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
        "IHS_CEO_QA_Unc",
        "IHS_CEO_Pres_Unc",
    ]
    # Do not include call-level controls like IHS_CEO_Pres_Unc here because
    # they are perfectly collinear with the CallFE (file_name)
    turn_controls = []

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = root / "outputs" / "econometric" / "tone_at_top" / timestamp
    ensure_output_dir(out_dir)

    results = []

    for sample in ["Main", "Finance", "Utility"]:
        print(f"\nProcessing {sample} Sample...")

        call_sub = (
            call_panel
            if sample == "Main"
            else call_panel[call_panel["sample"] == sample]
        )
        turns_sub = (
            turns_panel
            if sample == "Main"
            else turns_panel[turns_panel["sample"] == sample]
        )

        # M1: H_TT1 (Real-time style, 4-call rolling window, min=4)
        m1 = run_call_level_model(
            call_sub, "IHS_CFO_QA_Unc", "ClarityStyle_Realtime", call_controls
        )
        m1["Model"] = "M1 (H_TT1 Realtime)"
        m1["Sample"] = sample
        results.append(m1)

        # M2: H_TT2 (Speaker turns)
        m2 = run_turn_level_model(
            turns_sub, "IHS_NonCEO_Turn_Unc", "IHS_CEO_Prior_QA_Unc", turn_controls
        )
        m2["Model"] = "M2 (H_TT2 Turns)"
        m2["Sample"] = sample
        results.append(m2)

    res_df = pd.DataFrame(results)
    cols = ["Sample", "Model", "Coef", "t-stat", "p-value", "N", "Adj_R2", "Error"]
    for c in cols:
        if c not in res_df.columns:
            res_df[c] = np.nan
    res_df = res_df[cols]

    for sample in ["Main", "Finance", "Utility"]:
        s_df = res_df[res_df["Sample"] == sample].copy()
        s_df.to_csv(out_dir / f"results_{sample.lower()}.csv", index=False)
        print(f"\n{sample} Results:")
        print(s_df.to_string(index=False))

    # Generate LaTeX table
    generate_latex_table(res_df, out_dir / "tone_at_top_table.tex")

    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
