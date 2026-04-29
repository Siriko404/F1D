#!/usr/bin/env python3
"""
================================================================================
H.lewbel.iv: Lewbel (2012) heteroskedasticity-based IV — Cash Holdings
================================================================================
ID: econometric/run_h_lewbel_iv_cash
Description: Lewbel (2012) JBES heteroskedasticity-based instrumental-variable
             identification for the H1 main result. Manufactures internal
             instruments from heteroskedasticity in the first-stage residual
             of UncResCEO on Bates 2009 control vector. 2SLS estimation on
             HC main panel.

             Lewbel construction (Lewbel 2012 §2):
               First stage: UncResCEO_{i,t} = α + γ' W_{i,t} + ε_X
               Manufactured instruments: Z_j = (W_j − E[W_j]) × ε̂_X
                 for each W_j with significant heteroskedasticity in ε̂_X
               2SLS:    Cash_{i,t} = α + β · UncResCEO_{i,t} + γ' W_{i,t}
                                       + δ' FE + ε_Y, instrumenting UncResCEO
                                       with the kept Z_j

             Identifying assumption (Lewbel 2012):
               Cov(Z_j, ε_Y) = 0  iff  Cov(W_j, ε_Y · ε_X) = 0
               Holds when ε_X has heteroskedastic relation to W_j AND no
               common time-varying confounder simultaneously drives the
               (W_j, ε_X) and ε_Y dependence after controls. Pesaran-Taylor
               test filters W_j to the heteroskedastic subset; surviving
               W_j are valid instrument-base.

             What threat does Lewbel address (vs Phase E + H.dwz.fd)?
               - Phase E (sudden death): exogenous shock; addresses reverse
                 causality + omitted vars; n=8 power-limited
               - H.dwz.fd (turnover FD): time-invariant heterogeneity (firm
                 + manager), correlational; n=659
               - H.lewbel.iv: omitted TIME-VARYING confounders within firm
                 spell (which neither firm-FE nor manager-FE absorbs); 2SLS
                 strips out endogenous component of UncResCEO via internal
                 instruments
             Three designs cover three different threats. NOT "convergence"
             framing — "coverage" framing.

             Caveat (advisor-required, §4.3 disclosure): Lewbel works best
             when endogeneity is OMITTED-VARIABLE type. If endogeneity is
             reverse-causality flowing through the cash policy → speech
             channel, and W_j contains controls correlated with cash policy
             (lnAssets, Leverage), manufactured Z_j may absorb both
             directions, weakening exclusion. Reverse-causality threat is
             addressed primarily by Phase E sudden-death design.

Specifications (3 cols + footnote diagnostics):
    Col 1: OLS HC main baseline (replicates main panel HC sample exactly)
    Col 2: 2SLS Lewbel on HC main (Pesaran-Taylor-filtered Z)
    Col 3: 2SLS Lewbel + extended controls (DailyVola, StockPrice partial
           out alternatives)

Diagnostics (footnote):
    - Pesaran-Taylor heteroskedasticity p-values per W_j (filtering criterion)
    - Cragg-Donald weak-IV F-statistic
    - Hansen-Sargan over-id test (multiple instruments)
    - Hausman-Wu endogeneity test (rejects → IV preferred over OLS)

Anchor: Lewbel (2012) JBES "Using Heteroscedasticity to Identify and Estimate
Mismeasured and Endogenous Regressor Models". Standard references for the
Pesaran-Taylor (1999) heteroskedasticity test and Baum-Schaffer-Stillman
(2007) Stata implementation.

Sample: HC main (Main industries; FF12 ∉ {Finance, Utility}); same as the
H1.ceo2 main panel.

Deterministic: true
Author: Thesis Author (Sina Soleimanipour)
Date: 2026-04-29
================================================================================
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.iv import IV2SLS

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

# ==============================================================================
# Suite metadata
# ==============================================================================
SUITE_ID = "H.lewbel.iv"
SUITE_LABEL = "tab:h_lewbel_iv"
SUITE_CAPTION = "Lewbel (2012) Heteroskedasticity-Based IV: Cash Holdings"
SAMPLE_LABEL = (
    "Sample: HC Main panel — F1D firm-quarters in Main industries "
    "(FF12 $\\notin$ \\{Finance, Utility\\}) 2002Q1--2018Q4. "
    "Identical to H1.ceo2 main-panel HC sample. "
)
HYPOTHESIS_DIRECTION = "positive"  # H1 prior: UncResCEO ↑ → Cash ↑

# Path inputs
H1_PANEL_DIR = REPO_ROOT / "outputs" / "variables" / "h1_cash_holdings"

# Variables
DV = "CashRatio"
ENDOG = "UncResCEO"

# Bates 2009 base controls (matches H1.ceo2 main panel)
BATES_CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA",
    "Capex", "DivDummy", "sCFO", "CashRatio_lag",
]

# Extended controls
EXTENDED_CONTROLS = ["SalesGrowth", "RDSales", "DailyVola"]

# Pesaran-Taylor significance threshold
PT_ALPHA = 0.05


# ==============================================================================
# Data loading
# ==============================================================================
def find_latest_panel() -> Path:
    cand = sorted(
        H1_PANEL_DIR.glob("*/h1_cash_holdings_panel.parquet"), reverse=True
    )
    if not cand:
        raise FileNotFoundError(f"No panel found in {H1_PANEL_DIR}")
    return cand[0]


def find_latest_residual() -> Path:
    cand = sorted(
        (REPO_ROOT / "outputs" / "econometric" / "ceo_clarity_extended").glob(
            "*/ceo_clarity_residual.parquet"
        ),
        reverse=True,
    )
    if not cand:
        raise FileNotFoundError("No ceo_clarity_residual.parquet found")
    return cand[0]


def load_hc_main_panel() -> pd.DataFrame:
    """Load HC main panel: Main industries only, drop NaN on DV+IV+Bates.
    Merges UncResCEO from H0.3 ceo_clarity_residual file (call-level, on file_name).
    """
    p = find_latest_panel()
    print(f"Panel: {p}")
    df = pd.read_parquet(p)
    print(f"  raw: {len(df):,} rows; {df['gvkey'].nunique():,} firms")

    res = pd.read_parquet(find_latest_residual())
    print(f"  UncResCEO file: {len(res):,} rows; "
          f"{res['ceo_id'].nunique()} CEOs")
    df = df.merge(res[["file_name", "UncResCEO"]], on="file_name", how="left")
    print(f"  After merge: UncResCEO non-null = {df['UncResCEO'].notna().sum():,}")

    df = df[df["sample"] == "Main"].copy()
    print(f"  Main only: {len(df):,} rows; {df['gvkey'].nunique():,} firms")
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["cal_yr"] = df["start_date"].dt.year
    df["cal_q"] = df["start_date"].dt.quarter
    df["cal_yq"] = df["cal_yr"] * 4 + df["cal_q"] - 1
    return df


# ==============================================================================
# Lewbel construction
# ==============================================================================
def first_stage_residuals(df: pd.DataFrame, controls: List[str]) -> pd.Series:
    """Run first stage: ENDOG = α + γ' W + ε. Return residuals ε̂_X."""
    X = sm.add_constant(df[controls].astype(float))
    y = df[ENDOG].astype(float)
    fs = sm.OLS(y, X).fit()
    print(f"  First stage R²: {fs.rsquared:.4f}; n={fs.nobs:.0f}")
    return fs.resid


def pesaran_taylor_test(W_j: pd.Series, eps_X: pd.Series) -> Dict[str, float]:
    """Pesaran-Taylor (1999) heteroskedasticity test.

    Auxiliary regression: ε̂_X² = a + b · W_j + ν.
    H_0: b = 0 (homoskedastic). Reject → W_j has heteroskedastic relation
    to ε_X → valid Lewbel instrument-base.
    """
    eps_sq = eps_X ** 2
    X = sm.add_constant(W_j.astype(float))
    aux = sm.OLS(eps_sq, X).fit()
    var_name = W_j.name
    return {
        "var": var_name,
        "coef": float(aux.params[var_name]),
        "t": float(aux.tvalues[var_name]),
        "p": float(aux.pvalues[var_name]),
    }


def filter_lewbel_instruments(
    df: pd.DataFrame, controls: List[str], eps_X: pd.Series
) -> Tuple[List[str], pd.DataFrame]:
    """Per Pesaran-Taylor: keep W_j with significant heteroskedasticity.

    Returns (kept_W_list, pt_diagnostic_df).
    """
    rows = [pesaran_taylor_test(df[w], eps_X) for w in controls]
    pt_df = pd.DataFrame(rows)
    kept = pt_df[pt_df["p"] < PT_ALPHA]["var"].tolist()
    print(f"\nPesaran-Taylor heteroskedasticity test (alpha={PT_ALPHA}):")
    for r in rows:
        keep_marker = "[KEEP]" if r["p"] < PT_ALPHA else "[drop]"
        print(f"  {r['var']:>15s}  t={r['t']:+7.3f}  p={r['p']:.4f}  {keep_marker}")
    print(f"  Kept: {len(kept)}/{len(controls)} as instrument-base")
    return kept, pt_df


def construct_lewbel_z(
    df: pd.DataFrame, kept_W: List[str], eps_X: pd.Series
) -> pd.DataFrame:
    """Build Z_j = (W_j − mean(W_j)) × ε̂_X for each kept W_j."""
    Z = pd.DataFrame(index=df.index)
    for w in kept_W:
        Z[f"Z_{w}"] = (df[w].astype(float) - df[w].astype(float).mean()) * eps_X
    return Z


# ==============================================================================
# Estimation
# ==============================================================================
def run_ols_baseline(df: pd.DataFrame, controls: List[str]) -> Dict[str, Any]:
    """Col 1: OLS baseline replicating main panel HC spec."""
    X = sm.add_constant(df[[ENDOG] + controls].astype(float))
    y = df[DV].astype(float)
    # Cluster SE by firm
    fit = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["gvkey"].astype(str).values},
    )
    p_two = fit.pvalues[ENDOG]
    beta = fit.params[ENDOG]
    p_one = p_two / 2 if beta > 0 else 1 - p_two / 2  # H1 positive prior
    return {
        "col": 1,
        "label": "OLS",
        "spec": "OLS baseline",
        "beta": float(beta),
        "se": float(fit.bse[ENDOG]),
        "t": float(fit.tvalues[ENDOG]),
        "p_two": float(p_two),
        "p_one": float(p_one),
        "n_obs": int(fit.nobs),
        "n_firms": int(df["gvkey"].nunique()),
        "r2": float(fit.rsquared),
        "diagnostics": {},
    }


def run_2sls_lewbel(
    df: pd.DataFrame, controls: List[str], Z: pd.DataFrame, label: str, col: int
) -> Dict[str, Any]:
    """2SLS with Lewbel-manufactured instruments."""
    # IV2SLS: dependent + exog + endog + instruments
    exog = sm.add_constant(df[controls].astype(float))
    endog = df[[ENDOG]].astype(float)
    instruments = Z.astype(float)
    y = df[[DV]].astype(float)

    mod = IV2SLS(dependent=y, exog=exog, endog=endog, instruments=instruments)
    fit = mod.fit(cov_type="clustered", clusters=df["gvkey"].astype(str).values)

    p_two = float(fit.pvalues[ENDOG])
    beta = float(fit.params[ENDOG])
    p_one = p_two / 2 if beta > 0 else 1 - p_two / 2

    # Diagnostics
    diagnostics: Dict[str, Any] = {}

    # First-stage F-stat (Cragg-Donald approximation via fit.first_stage)
    try:
        fs_stats = fit.first_stage
        if hasattr(fs_stats, "diagnostics"):
            fs_diag = fs_stats.diagnostics
            f_stat = float(fs_diag.iloc[0]["f.stat"])
            diagnostics["first_stage_F"] = f_stat
            diagnostics["weak_iv_pass"] = bool(f_stat >= 10.0)
    except Exception as e:
        diagnostics["first_stage_F_error"] = str(e)

    # Sargan / J-test for over-identification
    try:
        sargan = fit.sargan
        diagnostics["sargan_stat"] = float(sargan.stat)
        diagnostics["sargan_p"] = float(sargan.pval)
    except Exception:
        pass
    try:
        jstat = fit.j_stat
        diagnostics["j_stat"] = float(jstat.stat)
        diagnostics["j_p"] = float(jstat.pval)
    except Exception:
        pass

    # Wu-Hausman endogeneity test
    try:
        wu = fit.wu_hausman()
        diagnostics["wu_hausman_stat"] = float(wu.stat)
        diagnostics["wu_hausman_p"] = float(wu.pval)
    except Exception as e:
        diagnostics["wu_hausman_error"] = str(e)

    return {
        "col": col,
        "label": label,
        "spec": f"2SLS Lewbel ({len(Z.columns)} Z)",
        "beta": beta,
        "se": float(fit.std_errors[ENDOG]),
        "t": float(fit.tstats[ENDOG]),
        "p_two": p_two,
        "p_one": p_one,
        "n_obs": int(fit.nobs),
        "n_firms": int(df["gvkey"].nunique()),
        "r2": float(fit.rsquared),
        "n_instruments": len(Z.columns),
        "diagnostics": diagnostics,
    }


# ==============================================================================
# LaTeX emit
# ==============================================================================
def emit_latex(columns: List[Dict[str, Any]], pt_df: pd.DataFrame, out_dir: Path) -> Path:
    n = len(columns)
    L = []
    L.append(r"\begin{table}[!htbp]")
    L.append(r"\centering\footnotesize")
    L.append(rf"\caption{{{SUITE_CAPTION}}}")
    L.append(rf"\label{{{SUITE_LABEL}}}")
    L.append(r"\begin{tabular}{l" + "c" * n + "}")
    L.append(r"\toprule")
    L.append(r" & " + " & ".join([f"({c['col']})" for c in columns]) + r" \\")
    L.append(r" & " + " & ".join([c["label"] for c in columns]) + r" \\")
    L.append(r"\midrule")

    # UncResCEO row
    beta_row = ["UncResCEO"]
    se_row = [""]
    for c in columns:
        beta = c["beta"]
        se = c["se"]
        p_one = c["p_one"]
        stars = ""
        if p_one < 0.01:
            stars = "***"
        elif p_one < 0.05:
            stars = "**"
        elif p_one < 0.10:
            stars = "*"
        beta_row.append(f"{beta:+.4f}{stars}")
        se_row.append(f"({se:.4f})")
    L.append(" & ".join(beta_row) + r" \\")
    L.append(" & ".join(se_row) + r" \\")
    L.append(r"\midrule")

    L.append("N & " + " & ".join([f"{c['n_obs']:,}" for c in columns]) + r" \\")
    L.append("N firms & " + " & ".join([f"{c['n_firms']:,}" for c in columns]) + r" \\")
    L.append("$R^2$ & " + " & ".join([f"{c['r2']:.3f}" for c in columns]) + r" \\")
    L.append(r"\midrule")
    L.append(
        "First-stage F & "
        + " & ".join(
            [
                "n/a"
                if c["col"] == 1
                else f"{c['diagnostics'].get('first_stage_F', float('nan')):.1f}"
                for c in columns
            ]
        )
        + r" \\"
    )
    L.append(
        "Hansen J $p$ & "
        + " & ".join(
            [
                "n/a"
                if c["col"] == 1
                else f"{c['diagnostics'].get('j_p', float('nan')):.3f}"
                for c in columns
            ]
        )
        + r" \\"
    )
    L.append(
        "Wu-Hausman $p$ & "
        + " & ".join(
            [
                "n/a"
                if c["col"] == 1
                else f"{c['diagnostics'].get('wu_hausman_p', float('nan')):.3f}"
                for c in columns
            ]
        )
        + r" \\"
    )
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}")

    pt_summary = ", ".join([f"{r['var']}={r['p']:.3f}" for _, r in pt_df.iterrows()])
    note = (
        f"{SAMPLE_LABEL}"
        r"Lewbel (2012) heteroskedasticity-based IV identifies $\beta$ on UncResCEO via internal "
        r"instruments $Z_j = (W_j - \bar W_j) \cdot \hat{\varepsilon}_X^{1\text{st-stage}}$ for each "
        r"$W_j$ with significant Pesaran-Taylor heteroskedasticity in the first-stage residual. "
        r"Col (1) OLS baseline replicates the H1.ceo2 main panel HC specification on the same sample. "
        r"Cols (2)-(3) are 2SLS with Lewbel-manufactured instruments. "
        rf"Pesaran-Taylor $p$-values (W_j $\to$ heteroskedasticity in $\hat\varepsilon_X$): {pt_summary}. "
        r"Standard errors firm-clustered. "
        r"\textbf{Identification scope (\S 4.3 disclosure):} Lewbel addresses omitted TIME-VARYING "
        r"confounders within firm spells (which neither firm-FE nor manager-FE absorbs). For "
        r"reverse-causality concerns (firms hoard cash $\to$ CEO talks more uncertainly about that "
        r"position), the design is weaker than Phase E sudden-death (Table~\ref{tab:h_death_did}); the "
        r"three designs together cover three different identification threats rather than converge "
        r"on a single coefficient. "
        r"$p$-value on UncResCEO is one-tailed (H1 prior: UncResCEO $\uparrow \Rightarrow$ Cash "
        r"$\uparrow$). "
        r"$^{*}/^{**}/^{***}$ denote $p<0.10/0.05/0.01$."
    )
    L.append(rf"\begin{{tablenotes}}\footnotesize\item {note}\end{{tablenotes}}")
    L.append(r"\end{table}")

    slug = SUITE_ID.lower().replace(".", "_")
    out_path = out_dir / f"{slug}_table.tex"
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWrote {out_path}")
    return out_path


def emit_suite_spec(
    columns: List[Dict[str, Any]], pt_df: pd.DataFrame, out_dir: Path
):
    spec = {
        "suite_id": SUITE_ID,
        "suite_label": SUITE_LABEL,
        "suite_caption": SUITE_CAPTION,
        "sample_label": SAMPLE_LABEL,
        "hypothesis_direction": HYPOTHESIS_DIRECTION,
        "anchor": "Lewbel 2012 JBES heteroskedasticity-based IV",
        "tail_direction": "positive",
        "columns": columns,
        "pesaran_taylor_diagnostic": pt_df.to_dict(orient="records"),
    }
    spec_file = out_dir / f"suite_spec_{SUITE_ID}.json"
    spec_file.write_text(json.dumps(spec, indent=2, default=str))
    print(f"Wrote {spec_file}")


# ==============================================================================
# Main
# ==============================================================================
def main():
    df = load_hc_main_panel()

    # Drop missing on DV + endog + bates controls (complete-case)
    needed = [DV, ENDOG] + BATES_CONTROLS
    df_complete = df.dropna(subset=needed).copy()
    print(f"\nComplete-case (DV + ENDOG + Bates): {len(df_complete):,} rows; "
          f"{df_complete['gvkey'].nunique()} firms")

    # First-stage residuals on Bates controls
    print("\n=== First stage on Bates controls ===")
    eps_X = first_stage_residuals(df_complete, BATES_CONTROLS)

    # Pesaran-Taylor filter
    kept_W, pt_df = filter_lewbel_instruments(df_complete, BATES_CONTROLS, eps_X)
    if len(kept_W) < 2:
        print(f"\nWARNING: only {len(kept_W)} W_j survived Pesaran-Taylor; "
              "weak-IV / under-id risk. Continuing for diagnostic transparency.")

    # Construct Lewbel Z matrix
    Z = construct_lewbel_z(df_complete, kept_W, eps_X)

    # Run 3 specifications
    print("\n=== Specifications ===")
    columns: List[Dict[str, Any]] = []

    # Col 1: OLS baseline
    print("\n[Col 1] OLS baseline")
    col1 = run_ols_baseline(df_complete, BATES_CONTROLS)
    print(f"  beta(UncResCEO)={col1['beta']:+.4f} ({col1['se']:.4f}) "
          f"p_one={col1['p_one']:.4f} n={col1['n_obs']}")
    columns.append(col1)

    # Col 2: 2SLS Lewbel
    print("\n[Col 2] 2SLS Lewbel (Bates controls)")
    col2 = run_2sls_lewbel(df_complete, BATES_CONTROLS, Z, "2SLS-Lewbel", 2)
    print(f"  beta(UncResCEO)={col2['beta']:+.4f} ({col2['se']:.4f}) "
          f"p_one={col2['p_one']:.4f} n={col2['n_obs']}")
    print(f"  diagnostics: {col2['diagnostics']}")
    columns.append(col2)

    # Col 3: 2SLS Lewbel + extended controls
    print("\n[Col 3] 2SLS Lewbel + extended controls")
    df3 = df_complete.dropna(subset=BATES_CONTROLS + EXTENDED_CONTROLS).copy()
    eps_X3 = first_stage_residuals(df3, BATES_CONTROLS + EXTENDED_CONTROLS)
    kept_W3, _ = filter_lewbel_instruments(
        df3, BATES_CONTROLS + EXTENDED_CONTROLS, eps_X3
    )
    Z3 = construct_lewbel_z(df3, kept_W3, eps_X3)
    col3 = run_2sls_lewbel(
        df3, BATES_CONTROLS + EXTENDED_CONTROLS, Z3, "+ extended", 3
    )
    print(f"  beta(UncResCEO)={col3['beta']:+.4f} ({col3['se']:.4f}) "
          f"p_one={col3['p_one']:.4f} n={col3['n_obs']}")
    print(f"  diagnostics: {col3['diagnostics']}")
    columns.append(col3)

    # Output
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = REPO_ROOT / "outputs" / "econometric" / "h_lewbel_iv_cash" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    pt_df.to_csv(out_dir / "pesaran_taylor_diagnostic.csv", index=False)

    emit_latex(columns, pt_df, out_dir)
    emit_suite_spec(columns, pt_df, out_dir)

    # Mirror to per_suite for main.tex \input
    per_suite_dir = REPO_ROOT / "docs" / "Draft" / "per_suite"
    per_suite_dir.mkdir(parents=True, exist_ok=True)
    emit_latex(columns, pt_df, per_suite_dir)

    print(f"\nDone. Output dir: {out_dir}")


if __name__ == "__main__":
    main()
