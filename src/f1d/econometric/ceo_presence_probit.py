#!/usr/bin/env python3
"""
================================================================================
CEO Presence Probit — H7 Selection Characterisation
================================================================================
ID: econometric/ceo_presence_probit
Description: Characterise determinants of CEO presence in earnings call Q&A
             to support discussion of selection concerns in H7 (L5).

Derives binary indicator:
    CEO_present_QA = CEO_QA_Uncertainty_pct.notna()  (1 if CEO participated in Q&A)

Runs probit: CEO_present_QA ~ Size + BookLev + ROA + TobinsQ + Volatility + C(year)

Outputs:
    - ceo_presence_probit_summary.txt  (full statsmodels summary)
    - ceo_presence_marginal_effects.csv  (average marginal effects + SE + p-value)

Note: CEO absence in Q&A (~29.6% of Main calls) is likely non-random.
This script characterises its determinants for thesis disclosure (Section X).

Dependencies:
    - Stage 3 H7 panel (build_h7_illiquidity_panel)

Author: Thesis Author
Date: 2026-03-12
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from f1d.shared.logging.config import setup_run_logging
from f1d.shared.path_utils import get_latest_output_dir


PROBIT_CONTROLS = ["Size", "BookLev", "ROA", "TobinsQ", "Volatility"]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CEO Presence Probit — H7 Selection Characterisation"
    )
    parser.add_argument("--panel-path", type=str, help="Explicit path to H7 panel parquet")
    return parser.parse_args()


def main(panel_path: Optional[str] = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "ceo_presence_probit" / timestamp

    setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="CEO_Presence_Probit",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("CEO Presence Probit — H7 Selection Characterisation")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")

    # ------------------------------------------------------------------
    # Load H7 panel
    # ------------------------------------------------------------------
    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h7_illiquidity",
                required_file="h7_illiquidity_panel.parquet",
            )
            panel_file = panel_dir / "h7_illiquidity_panel.parquet"
        except Exception as e:
            print(f"ERROR: Could not find H7 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    cols = ["file_name", "gvkey", "year", "sample", "CEO_QA_Uncertainty_pct"] + PROBIT_CONTROLS
    panel = pd.read_parquet(panel_file, columns=cols)
    print(f"  Loaded: {len(panel):,} rows")

    # Restrict to Main sample
    if "sample" in panel.columns:
        panel = panel[panel["sample"] == "Main"].copy()
    print(f"  Main sample: {len(panel):,} rows")

    # ------------------------------------------------------------------
    # Derive CEO_present_QA from NaN pattern
    # ------------------------------------------------------------------
    panel["CEO_present_QA"] = panel["CEO_QA_Uncertainty_pct"].notna().astype(int)
    n_present = panel["CEO_present_QA"].sum()
    n_absent = (~panel["CEO_QA_Uncertainty_pct"].notna()).sum()
    pct_absent = 100.0 * n_absent / len(panel)
    print(f"\n  CEO present in Q&A: {n_present:,} ({100 - pct_absent:.1f}%)")
    print(f"  CEO absent  in Q&A: {n_absent:,} ({pct_absent:.1f}%)")

    # ------------------------------------------------------------------
    # Probit regression
    # ------------------------------------------------------------------
    required = ["CEO_present_QA"] + PROBIT_CONTROLS + ["year"]
    df_reg = panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()
    print(f"\n  Regression sample: {len(df_reg):,} rows")

    formula = "CEO_present_QA ~ " + " + ".join(PROBIT_CONTROLS) + " + C(year)"
    print(f"  Formula: {formula}")

    try:
        model = smf.probit(formula, data=df_reg).fit(
            maxiter=200, disp=False, method="newton"
        )
    except Exception as e:
        print(f"  ERROR: Probit failed: {e}")
        return 1

    print(f"  Pseudo-R²: {model.prsquared:.4f}")
    print(f"  Log-likelihood: {model.llf:.2f}")

    # Average marginal effects
    try:
        mfx = model.get_margeff()
        mfx_df = pd.DataFrame({
            "variable": mfx.margeff_names,
            "marginal_effect": mfx.margeff,
            "std_error": mfx.margeff_se,
            "z_stat": mfx.tvalues,
            "p_value": mfx.pvalues,
        })
    except Exception as e:
        print(f"  WARNING: Marginal effects failed: {e}")
        mfx_df = pd.DataFrame()

    # ------------------------------------------------------------------
    # Save outputs
    # ------------------------------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = out_dir / "ceo_presence_probit_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(str(model.summary()))
        f.write("\n\n")
        if not mfx_df.empty:
            f.write("Average Marginal Effects:\n")
            f.write(mfx_df.to_string(index=False))

    print(f"\n  Saved: {summary_path.name}")

    if not mfx_df.empty:
        mfx_path = out_dir / "ceo_presence_marginal_effects.csv"
        mfx_df.to_csv(mfx_path, index=False)
        print(f"  Saved: {mfx_path.name}")

        # Print key marginal effects
        print("\n  Average Marginal Effects (non-year controls):")
        for _, row in mfx_df[~mfx_df["variable"].str.startswith("C(year)")].iterrows():
            sig = "***" if row["p_value"] < 0.01 else "**" if row["p_value"] < 0.05 else "*" if row["p_value"] < 0.10 else ""
            print(f"    {row['variable']:20s}  dF/dx={row['marginal_effect']:+.4f}  SE={row['std_error']:.4f}  p={row['p_value']:.4f} {sig}")

    duration = (datetime.now() - t0).total_seconds()
    print(f"\nCOMPLETE in {duration:.1f}s")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(panel_path=args.panel_path))
