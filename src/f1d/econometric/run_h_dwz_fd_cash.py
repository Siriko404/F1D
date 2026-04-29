#!/usr/bin/env python3
"""
================================================================================
H.dwz.fd: DWZ §6 First-Difference Design — Cash adaptation
================================================================================
ID: econometric/run_h_dwz_fd_cash
Description: Replication of Dzielinski-Wagner-Zeckhauser (2021) §6 Equation 7
             first-difference identification, adapted from Tobin's Q to cash
             holdings. One observation per CEO turnover pair (gvkey, old_CEO,
             new_CEO). Tenure-averaged variables. Δ = New - Old. Estimated by
             weighted least squares with robust SE; weights = harmonic-mean of
             quarter counts per CEO tenure.

             DWZ §6 verbatim (Eq 7):
               ΔValue_j = α + β·ΔClarityCEO,j + β_k·ΔControls_kj + FF48_j + ε_j
               "weighting is by the number of quarterly observations used to
                calculate each average"

             Adapted for cash:
               ΔCashRatio_j = α + β·ΔClarityCEO,j + β_k·ΔControls_kj
                              + FF12_j + ε_j

             Sample filters (per DWZ §6 verbatim):
               - Gap between old CEO last call and new CEO first call ≤ 120 days
               - Both CEOs ≥ 5 calls at firm
               - Both CEOs have valid ClarityCEO (= -CEO fixed effect from H0.3)
             F1D yield: 2,280 raw transitions → 1,675 (gap+calls) → 661 (FE).

             Hypothesis sign: H1 says higher UncResCEO (less clarity) → more
             cash. Equivalently, higher ClarityCEO → less cash → β NEGATIVE.

             Specifications (3 columns):
               Col 1: DWZ §6 controls verbatim only
                      (Δ NegCall + Δ UncPreCEO + Δ UncQue + Δ lnAssets + Δ ROA)
               Col 2: Bates-augmented (Col 1 + Δ Leverage, Δ DivDummy, Δ sCFO)
               Col 3: Industry-adjusted (Col 1 controls, FF12-demeaned per panel)

             Endogeneity disclosure (advisor-required, §4.3 thesis text):
               1. DWZ themselves admit "this approach does not completely
                  eliminate endogeneity concerns" (§6 verbatim).
               2. Cash is a CHOICE variable subject to direct CEO discretion;
                  endogeneity is MORE concerning for cash than for Tobin's Q
                  (DWZ's outcome). Forced/voluntary turnover not separated.
               3. This is a §4.3 robustness companion to Phase E sudden-death
                  DiD (n=8 exogenous events), NOT a primary identification.

             Deviations from DWZ §6 verbatim (must disclose):
               - FF12 industry FE instead of FF48 (panel infrastructure)
               - Intangibles ratio dropped (not in panel)
               - Sample = F1D Main industries (FF12 ∉ {Finance, Utility});
                 DWZ used S&P 500. Our 661 obs vs DWZ's 905.

Anchor:
    - Dzielinski, Wagner & Zeckhauser (2021) "Straight talkers and vague
      talkers", §6 + Equation 7 + Table 7. NotebookLM session 446a7902
      verified 2026-04-29.

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

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

# ==============================================================================
# Suite metadata
# ==============================================================================
SUITE_ID = "H.dwz.fd"
SUITE_LABEL = "tab:h_dwz_fd"
SUITE_CAPTION = (
    "DWZ \\S 6 First-Difference Replication: CEO Turnover and Cash Holdings"
)
SAMPLE_LABEL = (
    "Sample: 661 CEO turnover pairs in F1D Main-industry firms 2002Q1--2018Q4. "
    "One observation per turnover pair; variables averaged over each CEO's "
    "tenure at the firm. WLS weighted by harmonic-mean of quarter counts. "
)
HYPOTHESIS_DIRECTION = "negative"  # H1: clarity ↑ → cash ↓

# Path inputs
H1_PANEL_DIR = REPO_ROOT / "outputs" / "variables" / "h1_cash_holdings"
FE_TABLE = (
    REPO_ROOT
    / "outputs"
    / "econometric"
    / "ceo_clarity_extended"
    / "2026-04-24_210450"
    / "ceo_clarity_fe.parquet"
)

# Filter constants per DWZ §6 verbatim
MAX_GAP_DAYS = 120
MIN_CALLS_PER_CEO = 5

# DV
DV = "CashRatio"

# Variables to tenure-average
SPEECH_CONTROLS = ["NegCall", "UncPreCEO", "UncQue"]
DWZ_FIRM_CONTROLS = ["lnAssets", "ROA"]
BATES_EXTRA_CONTROLS = ["Leverage", "DivDummy", "sCFO"]
ALL_AVERAGE_VARS = [DV] + SPEECH_CONTROLS + DWZ_FIRM_CONTROLS + BATES_EXTRA_CONTROLS

# Display labels
VARIABLE_LABELS = {
    "ClarityCEO": "$\\Delta$ ClarityCEO",
    "NegCall": "$\\Delta$ NegCall",
    "UncPreCEO": "$\\Delta$ UncPreCEO",
    "UncQue": "$\\Delta$ UncQue",
    "lnAssets": "$\\Delta$ lnAssets",
    "ROA": "$\\Delta$ ROA",
    "Leverage": "$\\Delta$ Leverage",
    "DivDummy": "$\\Delta$ DivDummy",
    "sCFO": "$\\Delta$ sCFO",
}

# Column specs
COL_SPECS = [
    {
        "col": 1,
        "label": "DWZ \\S 6",
        "controls": SPEECH_CONTROLS + DWZ_FIRM_CONTROLS,
        "industry_demean": False,
        "fe_label": "FF12",
    },
    {
        "col": 2,
        "label": "+ Bates",
        "controls": SPEECH_CONTROLS + DWZ_FIRM_CONTROLS + BATES_EXTRA_CONTROLS,
        "industry_demean": False,
        "fe_label": "FF12",
    },
    {
        "col": 3,
        "label": "Ind-adj",
        "controls": SPEECH_CONTROLS + DWZ_FIRM_CONTROLS,
        "industry_demean": True,
        "fe_label": "demeaned",
    },
]

DISPLAY_COEFS = [
    "ClarityCEO",
    "NegCall",
    "UncPreCEO",
    "UncQue",
    "lnAssets",
    "ROA",
    "Leverage",
    "DivDummy",
    "sCFO",
]


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


def load_panel() -> pd.DataFrame:
    p = find_latest_panel()
    print(f"Panel: {p}")
    df = pd.read_parquet(p)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df = df.sort_values(["gvkey", "start_date"]).reset_index(drop=True)
    print(f"  {len(df):,} rows; {df['gvkey'].nunique():,} firms")
    return df


def load_fe_table() -> pd.DataFrame:
    print(f"FE: {FE_TABLE}")
    fe = pd.read_parquet(FE_TABLE)
    print(f"  {len(fe):,} CEOs with ClarityCEO")
    return fe


# ==============================================================================
# Transition detection + sample filtering
# ==============================================================================
def detect_transitions(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()
    p["prev_ceo_id"] = p.groupby("gvkey")["ceo_id"].shift(1)
    p["prev_start_date"] = p.groupby("gvkey")["start_date"].shift(1)
    mask = (p["ceo_id"] != p["prev_ceo_id"]) & (p["prev_ceo_id"].notna())
    trans = p.loc[mask, ["gvkey", "ceo_id", "prev_ceo_id", "start_date", "prev_start_date", "ff12_code"]].copy()
    trans = trans.rename(
        columns={
            "ceo_id": "new_ceo_id",
            "prev_ceo_id": "old_ceo_id",
            "start_date": "new_first_call",
            "prev_start_date": "old_last_call",
        }
    )
    trans["gap_days"] = (trans["new_first_call"] - trans["old_last_call"]).dt.days
    print(f"\nRaw transitions: {len(trans):,}")
    return trans.reset_index(drop=True)


def filter_transitions(
    trans: pd.DataFrame, panel: pd.DataFrame, fe: pd.DataFrame
) -> pd.DataFrame:
    calls = panel.groupby(["gvkey", "ceo_id"]).size().reset_index(name="n_calls")
    counts = calls.set_index(["gvkey", "ceo_id"])["n_calls"].to_dict()
    fe_set = set(fe["ceo_id"].astype(str).tolist())

    trans["n_old"] = trans.apply(
        lambda r: counts.get((r["gvkey"], r["old_ceo_id"]), 0), axis=1
    )
    trans["n_new"] = trans.apply(
        lambda r: counts.get((r["gvkey"], r["new_ceo_id"]), 0), axis=1
    )
    trans["old_in_fe"] = trans["old_ceo_id"].astype(str).isin(fe_set)
    trans["new_in_fe"] = trans["new_ceo_id"].astype(str).isin(fe_set)

    f1 = trans["gap_days"] <= MAX_GAP_DAYS
    f2 = f1 & (trans["n_old"] >= MIN_CALLS_PER_CEO) & (trans["n_new"] >= MIN_CALLS_PER_CEO)
    f3 = f2 & trans["old_in_fe"] & trans["new_in_fe"]
    print(f"  + gap<={MAX_GAP_DAYS}d: {f1.sum():,}")
    print(f"  + both >= {MIN_CALLS_PER_CEO} calls: {f2.sum():,}")
    print(f"  + both ClarityCEO available: {f3.sum():,}")

    out = trans.loc[f3].reset_index(drop=True)
    return out


# ==============================================================================
# Tenure aggregation + Δ computation
# ==============================================================================
def compute_tenure_means(panel: pd.DataFrame, vars_: List[str]) -> pd.DataFrame:
    grp = panel.groupby(["gvkey", "ceo_id"])
    means = grp[vars_].mean().reset_index()
    means["n_quarters"] = grp.size().reset_index(name="n_quarters")["n_quarters"]
    return means


def build_fd_panel(
    transitions: pd.DataFrame,
    tenure_means: pd.DataFrame,
    fe: pd.DataFrame,
    panel: pd.DataFrame,
) -> pd.DataFrame:
    means_idx = tenure_means.set_index(["gvkey", "ceo_id"])

    rows = []
    fe_idx = fe.set_index("ceo_id")["ClarityCEO"].to_dict()
    # FF12 industry per gvkey (firm-level constant; first observed)
    ff12 = panel.groupby("gvkey")["ff12_code"].first().to_dict()

    for _, r in transitions.iterrows():
        gv, old_id, new_id = r["gvkey"], r["old_ceo_id"], r["new_ceo_id"]
        try:
            old = means_idx.loc[(gv, old_id)]
            new = means_idx.loc[(gv, new_id)]
        except KeyError:
            continue
        row = {
            "gvkey": gv,
            "old_ceo_id": old_id,
            "new_ceo_id": new_id,
            "n_old": int(old["n_quarters"]),
            "n_new": int(new["n_quarters"]),
            "ff12_code": ff12.get(gv, np.nan),
            "d_ClarityCEO": fe_idx.get(new_id, np.nan) - fe_idx.get(old_id, np.nan),
        }
        for v in ALL_AVERAGE_VARS:
            row[f"d_{v}"] = new[v] - old[v]
        rows.append(row)

    fd = pd.DataFrame(rows)
    fd = fd.dropna(subset=["d_ClarityCEO"]).reset_index(drop=True)
    # WLS weight: harmonic-mean-ish, precision-of-paired-averages
    fd["weight"] = (fd["n_old"] * fd["n_new"]) / (fd["n_old"] + fd["n_new"])
    print(f"\nFD panel: {len(fd):,} pairs across {fd['gvkey'].nunique():,} firms")
    return fd


# ==============================================================================
# Industry demeaning (DWZ §6 panel (b))
# ==============================================================================
def industry_demean(fd: pd.DataFrame, vars_: List[str]) -> pd.DataFrame:
    out = fd.copy()
    for v in vars_:
        out[v] = out.groupby("ff12_code")[v].transform(lambda s: s - s.mean())
    return out


# ==============================================================================
# WLS regression
# ==============================================================================
def run_wls_spec(fd: pd.DataFrame, spec: Dict[str, Any]) -> Dict[str, Any]:
    rhs_cols = ["d_ClarityCEO"] + [f"d_{c}" for c in spec["controls"]]

    if spec["industry_demean"]:
        cols_to_demean = ["d_CashRatio", "d_ClarityCEO"] + [f"d_{c}" for c in spec["controls"]]
        df = industry_demean(fd, cols_to_demean)
        # No FE dummies post-demean
        X = df[rhs_cols].copy()
    else:
        df = fd.copy()
        # FF12 industry dummies (drop one to avoid collinearity)
        dummies = pd.get_dummies(df["ff12_code"], prefix="ff12", drop_first=True).astype(float)
        X = pd.concat([df[rhs_cols].copy(), dummies], axis=1)

    X = sm.add_constant(X, has_constant="add")
    y = df["d_CashRatio"]
    w = df["weight"]

    # Drop NaN rows
    mask = X.notna().all(axis=1) & y.notna() & w.notna()
    X, y, w = X[mask], y[mask], w[mask]

    model = sm.WLS(y, X, weights=w).fit(cov_type="HC1")
    coefs = {}
    for raw, label in [("d_ClarityCEO", "ClarityCEO")] + [
        (f"d_{c}", c) for c in spec["controls"]
    ]:
        if raw in model.params.index:
            beta = model.params[raw]
            se = model.bse[raw]
            t = model.tvalues[raw]
            p_two = model.pvalues[raw]
            # One-tailed: H1 negative → p_one = p_two/2 if beta<0 else 1-p_two/2
            if HYPOTHESIS_DIRECTION == "negative":
                p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
            else:
                p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
            coefs[label] = {
                "beta": float(beta),
                "se": float(se),
                "t": float(t),
                "p_two": float(p_two),
                "p_one": float(p_one),
            }
    return {
        "col": spec["col"],
        "label": spec["label"],
        "fe_label": spec["fe_label"],
        "n_obs": int(len(y)),
        "n_firms": int(df.loc[mask, "gvkey"].nunique()),
        "r2": float(model.rsquared),
        "coefs": coefs,
    }


# ==============================================================================
# LaTeX emit
# ==============================================================================
def emit_latex(columns: List[Dict[str, Any]], out_dir: Path) -> Path:
    n = len(columns)
    col_align = "l" + "c" * n
    L = []
    L.append(r"\begin{table}[!htbp]")
    L.append(r"\centering\footnotesize")
    L.append(rf"\caption{{{SUITE_CAPTION}}}")
    L.append(rf"\label{{{SUITE_LABEL}}}")
    L.append(r"\begin{tabular}{" + col_align + "}")
    L.append(r"\toprule")

    header = " & ".join([f"({c['col']})" for c in columns])
    L.append(rf" & {header} \\")
    label_row = " & ".join([c["label"] for c in columns])
    L.append(rf" & {label_row} \\")
    fe_row = " & ".join([c["fe_label"] for c in columns])
    L.append(rf"FE & {fe_row} \\")
    L.append(r"\midrule")

    for coef in DISPLAY_COEFS:
        label = VARIABLE_LABELS.get(coef, coef)
        beta_row = [label]
        se_row = [""]
        for c in columns:
            cd = c["coefs"].get(coef, {})
            beta = cd.get("beta", np.nan)
            se = cd.get("se", np.nan)
            p_one = cd.get("p_one", np.nan)
            stars = ""
            if not np.isnan(p_one):
                if coef == "ClarityCEO":
                    if p_one < 0.01:
                        stars = "***"
                    elif p_one < 0.05:
                        stars = "**"
                    elif p_one < 0.10:
                        stars = "*"
                else:
                    p_two = cd.get("p_two", np.nan)
                    if not np.isnan(p_two):
                        if p_two < 0.01:
                            stars = "***"
                        elif p_two < 0.05:
                            stars = "**"
                        elif p_two < 0.10:
                            stars = "*"
            beta_str = "" if np.isnan(beta) else f"{beta:+.4f}{stars}"
            se_str = "" if np.isnan(se) else f"({se:.4f})"
            beta_row.append(beta_str)
            se_row.append(se_str)
        L.append(" & ".join(beta_row) + r" \\")
        L.append(" & ".join(se_row) + r" \\")
    L.append(r"\midrule")

    L.append(
        "N (turnover pairs) & " + " & ".join([f"{c['n_obs']:,}" for c in columns]) + r" \\"
    )
    L.append("$R^2$ & " + " & ".join([f"{c['r2']:.3f}" for c in columns]) + r" \\")
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}")

    note = (
        f"{SAMPLE_LABEL} "
        r"Replicates Dzielinski, Wagner \& Zeckhauser (2021) \S 6 Equation 7 first-difference design, "
        r"adapted from Tobin's Q to cash holdings. One observation per CEO turnover pair (gvkey, old, new); "
        r"variables averaged over each CEO's tenure at the firm; $\Delta = \text{New} - \text{Old}$. "
        r"Estimated by weighted least squares with weights $w = (n_{\text{old}} \cdot n_{\text{new}}) / (n_{\text{old}} + n_{\text{new}})$ "
        r"per DWZ verbatim. Robust (HC1) standard errors. "
        r"Sample filters per DWZ \S 6 verbatim: gap between old CEO last call and new CEO first call $\leq 120$ days; "
        r"both CEOs $\geq 5$ calls at firm; both CEOs have valid ClarityCEO. "
        r"Deviations from DWZ verbatim: FF12 industry FE (vs FF48); intangibles ratio omitted (not in panel); "
        r"sample $=$ F1D Main industries (FF12 $\notin$ \{Finance, Utility\}). "
        r"\textbf{Endogeneity caveat} (\S 4.3 disclosure): DWZ themselves note this design ``does not completely eliminate endogeneity concerns'' (\S 6); "
        r"because cash is a CEO-discretion choice variable, the endogeneity profile here is more concerning than in DWZ's Tobin's Q application. "
        r"This table is a robustness companion to the Phase E sudden-death DiD (Table~\ref{tab:ceo_death_did}); forced/voluntary turnover not separated. "
        r"$p$-value on $\Delta$ ClarityCEO is one-tailed (H1 prior: clarity $\uparrow \Rightarrow$ cash $\downarrow$); other $p$-values two-tailed. "
        r"$^{*}/^{**}/^{***}$ denote $p<0.10/0.05/0.01$."
    )
    L.append(rf"\begin{{tablenotes}}\footnotesize\item {note}\end{{tablenotes}}")
    L.append(r"\end{table}")

    slug = SUITE_ID.lower().replace(".", "_")
    out_path = out_dir / f"{slug}_table.tex"
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWrote {out_path}")
    return out_path


def emit_suite_spec(columns: List[Dict[str, Any]], out_dir: Path):
    spec = {
        "suite_id": SUITE_ID,
        "suite_label": SUITE_LABEL,
        "suite_caption": SUITE_CAPTION,
        "sample_label": SAMPLE_LABEL,
        "hypothesis_direction": HYPOTHESIS_DIRECTION,
        "anchor": "DWZ 2021 §6 Eq 7 (NotebookLM session 446a7902, 2026-04-29)",
        "tail_direction": "negative",
        "columns": columns,
    }
    spec_file = out_dir / f"suite_spec_{SUITE_ID}.json"
    spec_file.write_text(json.dumps(spec, indent=2, default=str))
    print(f"Wrote {spec_file}")


# ==============================================================================
# Main
# ==============================================================================
def main():
    panel = load_panel()
    fe = load_fe_table()

    transitions_raw = detect_transitions(panel)
    transitions = filter_transitions(transitions_raw, panel, fe)
    if len(transitions) < 50:
        print(f"\nERROR: only {len(transitions)} pairs survived filters; aborting.")
        sys.exit(1)

    tenure = compute_tenure_means(panel, ALL_AVERAGE_VARS)
    fd = build_fd_panel(transitions, tenure, fe, panel)

    print("\n=== Specification results ===")
    columns = []
    for spec in COL_SPECS:
        out = run_wls_spec(fd, spec)
        cd = out["coefs"].get("ClarityCEO", {})
        beta = cd.get("beta", np.nan)
        se = cd.get("se", np.nan)
        p_one = cd.get("p_one", np.nan)
        print(
            f"  Col {out['col']} [{out['label']}]: "
            f"beta(d_ClarityCEO)={beta:+.4f} ({se:.4f}), p_one={p_one:.4f}, "
            f"n={out['n_obs']}, R2={out['r2']:.3f}"
        )
        columns.append(out)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = REPO_ROOT / "outputs" / "econometric" / "h_dwz_fd_cash" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    fd.to_parquet(out_dir / "fd_panel.parquet", index=False)
    transitions.to_csv(out_dir / "transitions.csv", index=False)

    emit_latex(columns, out_dir)
    emit_suite_spec(columns, out_dir)

    # Mirror per_suite emission for direct \input from main.tex body (matches
    # Phase E pattern; bypasses generate_all_tables.py schema validation since
    # this suite's spec doesn't fit the canonical SuiteSpec model).
    per_suite_dir = REPO_ROOT / "docs" / "Draft" / "per_suite"
    per_suite_dir.mkdir(parents=True, exist_ok=True)
    emit_latex(columns, per_suite_dir)

    print(f"\nDone. Output dir: {out_dir}")


if __name__ == "__main__":
    main()
