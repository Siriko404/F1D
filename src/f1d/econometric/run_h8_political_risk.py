#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H8 Political Risk × CEO Speech Vagueness -> Abnormal Investment
================================================================================
ID: econometric/test_h8_political_risk
Description: Run H8 moderation hypothesis test by loading the firm-year panel
             from Stage 3, running fixed effects OLS regressions, and outputting
             results.

Model Specification:
    AbsAbInv_{i,t+1} = β0 + β1·PRiskFY_t + β2·StyleFrozen_t
                      + β3·(PRiskFY_t × StyleFrozen_t)
                      + γ'·Controls_t
                      + FirmFE_i + YearFE_t + ε

    Unit of obs: firm-fiscal-year (gvkey, fyearq)
    DV: AbsAbInv_lead = |Biddle InvestmentResidual|_{t+1}

Key Coefficients:
    β3 (interact = PRiskFY × style_frozen):
        β3 > 0 (sig): Vague CEOs AMPLIFY the PRisk → abnormal investment channel
        β3 < 0 (sig): Vague CEOs DAMPEN the PRisk → abnormal investment channel
        β3 ≈ 0:       CEO clarity does NOT moderate (meaningful null)

Controls: Size, Lev, ROA, TobinsQ (firm-year level from Compustat)

Sanity checks run before regression:
    - PRiskFY distribution (mean, SD, p1, p99)
    - StyleFrozen distribution (mean≈0, SD≈1)
    - DV coverage (AbsAbInv_lead non-missing fraction)
    - Within-CEO variance of style_frozen (should be 0 — time-invariant)
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.path_utils import get_latest_output_dir

warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)
warnings.filterwarnings("ignore", category=FutureWarning, module="linearmodels.*")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_CONTROLS = ["Size", "Lev", "ROA", "TobinsQ"]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable
    {"col": "AbsAbInv_lead", "label": "|Abnormal Investment|$_{t+1}$"},
    # Main independent variables
    {"col": "PRiskFY", "label": "Political Risk"},
    {"col": "style_frozen", "label": "Style Frozen (Clarity)"},
    {"col": "interact", "label": "PRiskFY $\\times$ Style Frozen"},
    # Controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "ROA"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
]


CONFIG = {
    "min_firms": 50,  # Minimum unique firms for a valid regression
    "min_obs": 200,  # Minimum observations for a valid regression
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H8 Political Risk × CEO Clarity → Abnormal Investment (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H8 firm-year panel parquet"
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------


def run_sanity_checks(df: pd.DataFrame, out_dir: Path) -> None:
    """Print and save mandatory sanity checks."""
    lines = [
        "=" * 70,
        "H8 POLITICAL RISK PANEL — SANITY CHECKS",
        "=" * 70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"N firm-years (raw):  {len(df):,}",
        f"N firms (unique):    {df['gvkey'].nunique():,}",
        "",
    ]

    # PRiskFY
    if "PRiskFY" in df.columns:
        q = df["PRiskFY"].quantile([0.01, 0.99])
        lines += [
            "PRiskFY:",
            f"  mean={df['PRiskFY'].mean():.4f}  SD={df['PRiskFY'].std():.4f}",
            f"  p1={q.iloc[0]:.4f}  p99={q.iloc[1]:.4f}",
            f"  missing={df['PRiskFY'].isna().sum():,}",
            "",
        ]

    # StyleFrozen
    if "style_frozen" in df.columns:
        lines += [
            "StyleFrozen:",
            f"  mean={df['style_frozen'].mean():.4f}  SD={df['style_frozen'].std():.4f}",
            "  (expected: mean~=0, SD~=1)",
            f"  missing={df['style_frozen'].isna().sum():,}",
        ]
        # Within-CEO variance check
        if "ceo_id" in df.columns:
            ceo_var = df.groupby("ceo_id")["style_frozen"].var()
            n_ceos_with_var = (ceo_var > 1e-10).sum()
            lines.append(
                f"  Within-CEO variance > 0: {n_ceos_with_var} CEOs "
                f"(should be 0 — style_frozen is time-invariant per CEO)"
            )
        lines.append("")

    # DV
    if "AbsAbInv_lead" in df.columns:
        lines += [
            "AbsAbInv_lead (DV):",
            f"  valid={df['AbsAbInv_lead'].notna().sum():,} / {len(df):,}",
            f"  mean={df['AbsAbInv_lead'].mean():.4f}  SD={df['AbsAbInv_lead'].std():.4f}",
            "",
        ]

    # Interaction
    if "interact" in df.columns:
        lines += [
            "Interact (PRiskFY × StyleFrozen):",
            f"  valid={df['interact'].notna().sum():,}",
            f"  mean={df['interact'].mean():.4f}  SD={df['interact'].std():.4f}",
            "",
        ]

    lines.append("=" * 70)

    for line in lines:
        print(f"  {line}")

    sanity_path = out_dir / "sanity_checks.txt"
    with open(sanity_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Sanity checks saved: {sanity_path.name}")


# ---------------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------------


def run_regression(
    df: pd.DataFrame,
    spec_name: str,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run PanelOLS for H8.

    Returns (model_result, meta_dict).
    """
    required = (
        ["AbsAbInv_lead", "PRiskFY", "style_frozen", "interact"]
        + BASE_CONTROLS
        + ["gvkey", "fyearq"]
    )
    existing_controls = [c for c in BASE_CONTROLS if c in df.columns]
    required_avail = (
        ["AbsAbInv_lead", "PRiskFY", "style_frozen", "interact"]
        + existing_controls
        + ["gvkey", "fyearq"]
    )

    df_reg = df.replace([np.inf, -np.inf], np.nan).dropna(subset=required_avail).copy()

    if (
        len(df_reg) < CONFIG["min_obs"]
        or df_reg["gvkey"].nunique() < CONFIG["min_firms"]
    ):
        print(
            f"  Skipping {spec_name}: insufficient data "
            f"(N={len(df_reg):,}, firms={df_reg['gvkey'].nunique():,})"
        )
        return None, {}

    formula = (
        "AbsAbInv_lead ~ PRiskFY + style_frozen + interact + "
        + " + ".join(existing_controls)
        + " + EntityEffects + TimeEffects"
    )

    print(f"\n--- {spec_name} ---")
    print(
        f"  N firm-years: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}"
        f"  |  N years: {df_reg['fyearq'].nunique():,}"
    )
    print(
        f"  Formula: AbsAbInv_lead ~ PRiskFY + style_frozen + interact + {' + '.join(existing_controls)}"
    )
    print("  Estimating with firm-clustered SEs...")

    t0 = datetime.now()

    df_panel = df_reg.set_index(["gvkey", "fyearq"])

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: PanelOLS failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(
        f"  [OK] Complete in {duration:.1f}s  |  Within-R²: {model.rsquared_within:.4f}"
    )

    # Key coefficients
    beta1 = float(model.params.get("PRiskFY", np.nan))
    beta2 = float(model.params.get("style_frozen", np.nan))
    beta3 = float(model.params.get("interact", np.nan))

    se1 = float(model.std_errors.get("PRiskFY", np.nan))
    se2 = float(model.std_errors.get("style_frozen", np.nan))
    se3 = float(model.std_errors.get("interact", np.nan))

    t1 = float(model.tstats.get("PRiskFY", np.nan))
    t2 = float(model.tstats.get("style_frozen", np.nan))
    t3 = float(model.tstats.get("interact", np.nan))

    p1 = float(model.pvalues.get("PRiskFY", np.nan))
    p2 = float(model.pvalues.get("style_frozen", np.nan))
    p3 = float(model.pvalues.get("interact", np.nan))

    h8_sig = not np.isnan(p3) and p3 < 0.05

    print(f"  beta1(PRiskFY):      {beta1:.4f}  SE={se1:.4f}  t={t1:.2f}  p={p1:.4f}")
    print(f"  beta2(StyleFrozen):  {beta2:.4f}  SE={se2:.4f}  t={t2:.2f}  p={p2:.4f}")
    print(
        f"  beta3(Interact):     {beta3:.4f}  SE={se3:.4f}  t={t3:.2f}  p={p3:.4f}  H8={'SUPPORTED' if h8_sig else 'not supported'}"
    )

    if h8_sig and beta3 > 0:
        print("  -> Vague CEOs AMPLIFY the PRisk -> abnormal investment channel")
    elif h8_sig and beta3 < 0:
        print("  -> Vague CEOs DAMPEN the PRisk -> abnormal investment channel")
    else:
        print("  -> CEO vagueness does NOT significantly moderate PRisk effect (null)")

    meta: Dict[str, Any] = {
        "spec_name": spec_name,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "within_r2": float(model.rsquared_within),
        "beta1_PRiskFY": beta1,
        "se1": se1,
        "t1": t1,
        "p1": p1,
        "beta2_StyleFrozen": beta2,
        "se2": se2,
        "t2": t2,
        "p2": p2,
        "beta3_Interact": beta3,
        "se3": se3,
        "t3": t3,
        "p3": p3,
        "h8_sig": h8_sig,
    }

    return model, meta


# ---------------------------------------------------------------------------
# LaTeX table
# ---------------------------------------------------------------------------


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    tex_path = out_dir / "h8_political_risk_table.tex"

    def fmt_coef(val: float, pval: float) -> str:
        if pd.isna(val):
            return ""
        stars = (
            "^{***}"
            if pval < 0.01
            else "^{**}"
            if pval < 0.05
            else "^{*}"
            if pval < 0.10
            else ""
        )
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        return "" if pd.isna(val) else f"({val:.4f})"

    n_cols = len(all_results)
    col_spec = "l" + "c" * n_cols
    col_heads = " & " + " & ".join(f"({i + 1})" for i in range(n_cols)) + r" \\"

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H8: CEO Speech Vagueness Moderates Political Risk and Abnormal Investment}",
        r"\label{tab:h8_political_risk}",
        r"\small",
        r"\begin{tabular}{" + col_spec + "}",
        r"\toprule",
        col_heads,
        r"\midrule",
    ]

    for var_key, label in [
        ("beta1_PRiskFY", "Political Risk"),
        ("beta2_StyleFrozen", "Style Frozen"),
        ("beta3_Interact", "PRisk $\\times$ Style Frozen"),
    ]:
        pkey = (
            var_key.replace("beta1_", "p").replace("beta2_", "p").replace("beta3_", "p")
        )
        pmap = {
            "beta1_PRiskFY": "p1",
            "beta2_StyleFrozen": "p2",
            "beta3_Interact": "p3",
        }
        pk = pmap[var_key]

        coef_row = (
            f"{label} & "
            + " & ".join(
                fmt_coef(r.get(var_key, np.nan), r.get(pk, np.nan)) for r in all_results
            )
            + r" \\"
        )
        se_row = (
            " & "
            + " & ".join(
                fmt_se(
                    r.get(
                        var_key.replace("beta", "se")
                        .replace("1_PRiskFY", "1")
                        .replace("2_StyleFrozen", "2")
                        .replace("3_Interact", "3"),
                        np.nan,
                    )
                )
                for r in all_results
            )
            + r" \\"
        )
        lines += [coef_row, se_row]

    lines += [
        r"\midrule",
        r"Controls & " + " & ".join("Yes" for _ in all_results) + r" \\",
        r"Firm FE  & " + " & ".join("Yes" for _ in all_results) + r" \\",
        r"Year FE  & " + " & ".join("Yes" for _ in all_results) + r" \\",
        r"\midrule",
        "Observations & "
        + " & ".join(f"{r.get('n_obs', 0):,}" for r in all_results)
        + r" \\",
        "Within-$R^2$ & "
        + " & ".join(f"{r.get('within_r2', np.nan):.4f}" for r in all_results)
        + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  LaTeX table saved: {tex_path.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(panel_path: Optional[str] = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h8_political_risk" / timestamp

    print("=" * 80)
    print("STAGE 4: Test H8 Political Risk x CEO Clarity -> Abnormal Investment")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")

    # ------------------------------------------------------------------
    # Load Stage 3 panel
    # ------------------------------------------------------------------
    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h8_political_risk",
                required_file="h8_political_risk_panel.parquet",
            )
            panel_file = panel_dir / "h8_political_risk_panel.parquet"
        except Exception as e:
            print(f"ERROR: Could not find Stage 3 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    print(f"  File:    {panel_file}")
    df = pd.read_parquet(
        panel_file,
    )
    print(f"  Rows:    {len(df):,}")
    print(f"  Columns: {len(df.columns)}")

    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Summary Statistics (firm-year level, aggregate only)
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
        sample_names=None,  # Aggregate only (firm-year level, Main sample)
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H8 Political Risk",
        label="tab:summary_stats_h8",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # ------------------------------------------------------------------
    # Sanity checks
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Sanity checks")
    print("=" * 60)
    run_sanity_checks(df, out_dir)

    # Ensure interaction exists
    if "interact" not in df.columns:
        if "PRiskFY" in df.columns and "style_frozen" in df.columns:
            df["interact"] = df["PRiskFY"] * df["style_frozen"]
        else:
            print("ERROR: Cannot create interaction — PRiskFY or style_frozen missing.")
            return 1

    # ------------------------------------------------------------------
    # Run regressions
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Regressions")
    print("=" * 60)

    all_results: List[Dict[str, Any]] = []

    # Primary specification: all industries
    model_primary, meta_primary = run_regression(df, "Primary (All Industries)")
    if model_primary is not None:
        all_results.append(meta_primary)
        with open(out_dir / "regression_primary.txt", "w", encoding="utf-8") as f:
            f.write(str(model_primary.summary))

    # Robustness: non-finance / non-utility firms only
    # ff12_code: 8 = Utilities, 11 = Finance
    if "ff12_code" in df.columns:
        df_main = df[~df["ff12_code"].isin([8, 11])].copy()
        model_main, meta_main = run_regression(
            df_main, "Main Sample (ex-Finance/Utility)"
        )
        if model_main is not None:
            all_results.append(meta_main)
            with open(out_dir / "regression_main.txt", "w", encoding="utf-8") as f:
                f.write(str(model_main.summary))
    elif "sample" in df.columns:
        df_main = df[df["sample"] == "Main"].copy()
        model_main, meta_main = run_regression(df_main, "Main Sample")
        if model_main is not None:
            all_results.append(meta_main)
            with open(out_dir / "regression_main.txt", "w", encoding="utf-8") as f:
                f.write(str(model_main.summary))

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    if all_results:
        _save_latex_table(all_results, out_dir)
        pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False)
        print(f"\n  Diagnostics saved: {out_dir / 'model_diagnostics.csv'}")

    duration = (datetime.now() - t0).total_seconds()
    print("\n" + "=" * 80)
    print(f"COMPLETE in {duration:.1f}s")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(panel_path=args.panel_path))
