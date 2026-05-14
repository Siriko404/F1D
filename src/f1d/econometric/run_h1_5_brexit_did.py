#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1.5 Brexit Referendum DiD on Cash + Speech (Campello 2022 verbatim)
================================================================================
ID: econometric/run_h1_5_brexit_did
Description: Difference-in-differences design exploiting the June 23, 2016 UK
             Brexit referendum as a plausibly-exogenous foreign-uncertainty
             shock to U.S. firms with UK exposure. Two parallel treatment
             definitions per Campello et al. 2022 JFQA Section IV.A:

             1. HIGH_BETA_UK   — top tercile of nonneg β^UK from equation (13)
                                 (firm exposure to UK equity-market vol over
                                  60 monthly obs 2010M1-2014M12)
             2. HIGH_10K       — >5 entries of 9-keyword Brexit/UK terms in
                                 firm's 2015 10-K filing

             Two parallel DVs per treatment x FE configuration:
               Run 1: cash_brexit_dv = cheq / lag(atq - cheq)   (BKS net-assets)
               Run 2: UncResCEO_c    (F1D speech extension)

             POST = cal_yr_qtr in {20163, 20164} (2016Q3-Q4 — the referendum
             vote and the immediate aftermath through year-end).

             16 baseline cells = 2 DVs x 2 treatments x 4 FE configurations.

Tail directions:
    HIGH_X x Post on cash_brexit_dv:  one-tail POS  (precautionary cash response)
    HIGH_X x Post on UncResCEO_c:     one-tail POS  (uncertainty-induced speech)
    HIGH_X level dummy:               two-tailed (absorbed by firm FE)
    Post level dummy:                 two-tailed (absorbed by time FE)

Channel:
    CH-Brexit2016 — foreign-uncertainty macro shock orthogonal to US-domestic
    political-risk shocks (Trump). Strengthens the "shock-scale hierarchy"
    framing of Section III.E.4 (macro UK / state / firm-event triangulation).

Anchor: Campello et al. (2022) JFQA Section IV verbatim. Spec-locked at
    tmp/3did_replication_v2_2026_05_08.md Section A (lines 74-960).

Model Specification (per Campello et al. 2022 Section II.D):

    DV ~ b1 * (HIGH_X x POST) + b2 * HIGH_X + b3 * POST
       + 5 macro controls (1Q-lagged)
       + 5 firm controls (1Q-lagged): brexit_tobins_q, brexit_sales_growth,
         brexit_stock_return, brexit_cash_flow, ln(atq)
       + 1 add'l: consensus EPS z-score (1Q-lagged)
       + FIRM FE + Hoberg-Phillips FIC100 x cal_yr_qtr FE (manual interaction)
       + double-cluster SE (firm + cal_yr_qtr)

CRITICAL DESIGN DEVIATIONS FROM TRUMP/REDISTRICTING SISTER RUNNERS.
1. Controls: 5 macros + Brexit-verbatim firm controls (NOT F1D canonical 12)
   per audit MAJOR-3 + Sina-locked decision; macro-shock identification
   requires macro controls.
2. SE: double-cluster firm + cal_yr_qtr per Campello Section II.D verbatim
   ("Standard errors are double-clustered by firm and calendar quarters").
3. FE: firm + FIC100 x cal_yr_qtr (manually constructed interaction dummy
   passed as other_effects with drop_absorbed=True) per audit MAJOR-4.
4. DV: cash_brexit_dv = cheq / lag(atq - cheq) per Table 8 footer
   (BKS net-assets). Distinct from F1D-canonical CashRatio = cheq/atq.

Inputs:
    - outputs/variables/h1_cash_holdings/<latest>/h1_cash_holdings_panel.parquet
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet (raw cheq + atq + mkvaltq)
    - 10 Brexit builder outputs via get_latest_output_dir():
        brexit_treatment_beta_uk + brexit_treatment_10k + brexit_macro +
        brexit_consensus_eps + hoberg_phillips_fic100 +
        brexit_tobins_q + brexit_sales_growth + brexit_stock_return +
        brexit_cash_flow + brexit_psm_matching

Outputs:
    - outputs/econometric/h1_5_brexit_did/<timestamp>/
================================================================================
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.outputs import extract_coefs_panelols, write_suite_spec


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IV_BETA_UK = "DiD_BetaUK"
KEY_IV_10K = "DiD_10K"

# 5 macro controls (1Q-lagged, all already _lag1 in builder output).
MACRO_CONTROLS = ["usd_gbp_lag1", "vix_lag1", "gdp_fcst_1y_lag1", "umcsent_lag1", "ads_lag1"]

# 5 Brexit-verbatim firm controls (1Q-lagged at panel-assembly).
FIRM_CONTROLS_NAMES = [
    "brexit_tobins_q", "brexit_sales_growth", "brexit_stock_return",
    "brexit_cash_flow", "ln_atq",
]
FIRM_CONTROLS_LAG1 = [c + "_lag1" for c in FIRM_CONTROLS_NAMES]

# Consensus EPS (1Q-lagged at panel-assembly).
EPS_CONTROL_LAG1 = "consensus_eps_z_lag1"

ALL_CONTROLS_LAG1 = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1]

# DiD treatment columns (constructed in panel assembly).
DID_COLS = [KEY_IV_BETA_UK, KEY_IV_10K]
LEVEL_DUMMIES_BETA = ["HIGH_BETA_UK", "Post_brexit"]
LEVEL_DUMMIES_10K = ["HIGH_10K", "Post_brexit"]

# Sample window per spec §1G.
WINDOW_START_YQ = 20101  # 2010Q1
WINDOW_END_YQ = 20164    # 2016Q4
POST_START_YQ = 20163    # 2016Q3 — Brexit vote June 23 2016

# $10M MV/BA filter per spec §1G + audit MAJOR-2.
MIN_MV_OR_BA_MILLIONS = 10.0

# Winsorization 1% within cal_yr_qtr (per spec §2E + audit VAGUE-2).
WINSOR_PCT = 0.01

# FE configurations.
FE_LADDER = ["industry", "firm", "industry_yq", "firm_yq"]

SUITE_ID = "H1.5.brexit_did"
SUITE_DIR_NAME = "h1_5_brexit_did"
SUITE_TITLE = (
    "Brexit Referendum Difference-in-Differences: Cash Holdings + CEO Speech "
    "Uncertainty (Campello et al. 2022 JFQA verbatim)"
)
SUITE_LABEL = "tab:h1_5_brexit_did"

CLUSTERING = {"entity": True, "time": True}  # double-cluster firm + cal_yr_qtr


# ==============================================================================
# Data Loading
# ==============================================================================

def load_h1_panel(root: Path) -> Tuple[pd.DataFrame, Path]:
    """Load h1_cash_holdings panel for file_name + ff12_code + UncResCEO context."""
    pdir = get_latest_output_dir(
        root / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    )
    panel_file = pdir / "h1_cash_holdings_panel.parquet"
    columns = ["file_name", "gvkey", "ceo_id", "ff12_code", "start_date"]
    panel = pd.read_parquet(panel_file, columns=columns)
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    panel["start_date"] = pd.to_datetime(panel["start_date"])
    panel["cal_yr_qtr"] = (
        panel["start_date"].dt.year * 10 + panel["start_date"].dt.quarter
    )
    return panel, panel_file


def merge_uncresceo(panel: pd.DataFrame, root: Path) -> pd.DataFrame:
    """Merge UncResCEO from DWZ Eq.5 residual parquet (call-level by file_name)."""
    rdir = get_latest_output_dir(
        root / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    rfile = rdir / "ceo_clarity_residual.parquet"
    res = pd.read_parquet(rfile, columns=["file_name", "UncResCEO"])
    panel = panel.merge(res, on="file_name", how="left")
    return panel


def load_compustat_raw(root: Path, gvkeys_keep: set, qtr_min: int, qtr_max: int) -> pd.DataFrame:
    """Re-load raw Compustat for cheq, atq, mkvaltq per audit CRITICAL-3."""
    cpath = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    print(f"  Re-loading Compustat raw: {cpath}")
    df = pd.read_parquet(cpath, columns=["gvkey", "datadate", "atq", "cheq", "mkvaltq"])
    for c in ["atq", "cheq", "mkvaltq"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
    df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)
    df = df[df["gvkey"].isin(gvkeys_keep)]
    df = df[(df["cal_yr_qtr"] >= qtr_min) & (df["cal_yr_qtr"] <= qtr_max)]
    df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
        subset=["gvkey", "cal_yr_qtr"], keep="last"
    ).reset_index(drop=True)
    print(f"  Compustat raw rows in window: {len(df):,} ({df['gvkey'].nunique():,} gvkeys)")
    return df


def load_brexit_builders(root: Path) -> Dict[str, pd.DataFrame]:
    """Load all 10 Brexit builder outputs via get_latest_output_dir()."""
    base = root / "outputs" / "variables"
    sources = {
        "beta_uk": ("brexit_treatment_beta_uk", "beta_uk_per_firm.parquet"),
        "treat_10k": ("brexit_treatment_10k", "treatment_10k_per_firm.parquet"),
        "macro": ("brexit_macro", "brexit_macro_quarterly.parquet"),
        "eps": ("brexit_consensus_eps", "consensus_eps_per_firm_quarter.parquet"),
        "fic100": ("hoberg_phillips_fic100", "fic100_per_firm_year.parquet"),
        "tobins_q": ("brexit_tobins_q", "brexit_tobins_q.parquet"),
        "sales_growth": ("brexit_sales_growth", "brexit_sales_growth.parquet"),
        "stock_return": ("brexit_stock_return", "brexit_stock_return.parquet"),
        "cash_flow": ("brexit_cash_flow", "brexit_cash_flow.parquet"),
        "psm": ("brexit_psm_matching", "psm_matched_per_firm.parquet"),
    }
    out: Dict[str, pd.DataFrame] = {}
    for k, (dirname, fname) in sources.items():
        d = get_latest_output_dir(base / dirname, required_file=fname)
        out[k] = pd.read_parquet(d / fname)
        print(f"  {k:15s} {len(out[k]):>10,} rows  ({d.name})")
    return out


# ==============================================================================
# Panel assembly
# ==============================================================================

def winsorize_within(df: pd.DataFrame, col: str, group: str, pct: float = WINSOR_PCT) -> pd.DataFrame:
    def _w(s: pd.Series) -> pd.Series:
        if s.isna().all():
            return s
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby(group, observed=True)[col].transform(_w)
    return df


def assemble_panel(panel: pd.DataFrame, raw_comp: pd.DataFrame, builders: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build the (gvkey, cal_yr_qtr) panel with DV, treatment, controls, FE."""
    print("\n  --- Panel assembly ---")
    # 1. Restrict to Brexit window + drop FF12 8 (Util) + 11 (Fin) + drop missing UncResCEO.
    panel = panel[(panel["cal_yr_qtr"] >= WINDOW_START_YQ) & (panel["cal_yr_qtr"] <= WINDOW_END_YQ)]
    panel = panel[~panel["ff12_code"].isin([8, 11])]
    print(f"  Brexit window + Main FF12: {len(panel):,} call-rows ({panel['gvkey'].nunique():,} gvkeys)")

    # 2. UncResCEO_c centering (within Brexit-window Main sample).
    mu_uncres = panel["UncResCEO"].mean(skipna=True)
    panel["UncResCEO_c"] = panel["UncResCEO"] - mu_uncres
    print(f"  UncResCEO mean (centering offset): {mu_uncres:.6f}")

    # 3. Aggregate UncResCEO_c per (gvkey, cal_yr_qtr) — mean within multi-call cells.
    cell_speech = (
        panel.groupby(["gvkey", "cal_yr_qtr"], observed=True)["UncResCEO_c"]
        .mean().reset_index()
    )

    # 4. Merge raw Compustat onto cell-level frame (cheq, atq, mkvaltq).
    cell = cell_speech.merge(raw_comp, on=["gvkey", "cal_yr_qtr"], how="inner")

    # 5. Compute cash_brexit_dv = cheq_t / (atq_{t-1} - cheq_{t-1}) per Table 8 footer.
    cell = cell.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").reset_index(drop=True)
    cell["atq_lag1"] = cell.groupby("gvkey")["atq"].shift(1)
    cell["cheq_lag1"] = cell.groupby("gvkey")["cheq"].shift(1)
    cell["denom"] = cell["atq_lag1"] - cell["cheq_lag1"]
    cell = cell[cell["denom"] > 0]
    cell["cash_brexit_dv"] = cell["cheq"] / cell["denom"]

    # 6. $10M filter (per audit MAJOR-2).
    pre_filter = len(cell)
    cell = cell[(cell["mkvaltq"].fillna(0) >= MIN_MV_OR_BA_MILLIONS) | (cell["atq"] >= MIN_MV_OR_BA_MILLIONS)]
    print(f"  $10M MV/BA filter: {len(cell):,} (dropped {pre_filter - len(cell):,})")

    # 7. Merge treatment dummies HIGH_BETA_UK + HIGH_10K.
    bu = builders["beta_uk"][["gvkey", "HIGH_BETA_UK"]]
    tk = builders["treat_10k"][["gvkey", "HIGH_10K"]]
    cell = cell.merge(bu, on="gvkey", how="left")
    cell = cell.merge(tk, on="gvkey", how="left")

    # 8. Construct POST + DiD treatment indicators.
    cell["Post_brexit"] = (cell["cal_yr_qtr"] >= POST_START_YQ).astype(int)
    cell[KEY_IV_BETA_UK] = cell["HIGH_BETA_UK"].fillna(np.nan) * cell["Post_brexit"]
    cell[KEY_IV_10K] = cell["HIGH_10K"].fillna(np.nan) * cell["Post_brexit"]

    # 9. Merge 5 macros (already 1Q-lagged in builder).
    cell = cell.merge(builders["macro"], on="cal_yr_qtr", how="left")

    # 10. Merge 4 Brexit firm controls + ln_atq.
    for col, key in [("brexit_tobins_q", "tobins_q"),
                     ("brexit_sales_growth", "sales_growth"),
                     ("brexit_stock_return", "stock_return"),
                     ("brexit_cash_flow", "cash_flow")]:
        sub = builders[key][["gvkey", "cal_yr_qtr", col]]
        cell = cell.merge(sub, on=["gvkey", "cal_yr_qtr"], how="left")
    cell["ln_atq"] = np.log(cell["atq"].clip(lower=1.0))

    # 11. 1Q-lag firm controls within firm.
    cell = cell.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").reset_index(drop=True)
    for c in FIRM_CONTROLS_NAMES:
        cell[c + "_lag1"] = cell.groupby("gvkey")[c].shift(1)

    # 12. Merge consensus EPS (already labeled by current quarter; lag 1Q here).
    eps = builders["eps"][["gvkey", "cal_yr_qtr", "consensus_eps_z"]]
    cell = cell.merge(eps, on=["gvkey", "cal_yr_qtr"], how="left")
    cell[EPS_CONTROL_LAG1] = cell.groupby("gvkey")["consensus_eps_z"].shift(1)

    # 13. Merge FIC100 industry per (gvkey, year).
    cell["year"] = cell["cal_yr_qtr"] // 10
    fic = builders["fic100"][["gvkey", "year", "fic100_industry_id"]]
    cell = cell.merge(fic, on=["gvkey", "year"], how="left")
    fic_cov = cell["fic100_industry_id"].notna().mean()
    print(f"  FIC100 coverage on Brexit panel: {fic_cov:.1%}")

    # 14. FIC100 x cal_yr_qtr interaction id (per audit MAJOR-4 — manual dummy).
    cell["fic100_qtr_id"] = (
        cell["fic100_industry_id"].astype("Int64").astype(str) + "_" + cell["cal_yr_qtr"].astype(str)
    )

    # 15. Winsorize 1% within cal_yr_qtr on continuous firm-level variables.
    winsor_cols = [
        "cash_brexit_dv", "UncResCEO_c", "ln_atq",
        "brexit_tobins_q_lag1", "brexit_sales_growth_lag1",
        "brexit_stock_return_lag1", "brexit_cash_flow_lag1",
        EPS_CONTROL_LAG1,
    ]
    for c in winsor_cols:
        if c in cell.columns:
            cell = winsorize_within(cell, c, "cal_yr_qtr")

    # FF12 — re-derive from the panel side via gvkey first occurrence (FF12 is firm-fixed).
    ff12_lookup = panel.drop_duplicates("gvkey", keep="first")[["gvkey", "ff12_code"]]
    cell = cell.merge(ff12_lookup, on="gvkey", how="left")

    print(f"  Final panel: {len(cell):,} (gvkey, cal_yr_qtr) cells")
    return cell


# ==============================================================================
# Regression
# ==============================================================================

def _fit_one(df: pd.DataFrame, dv: str, treatment: str, exog_cols: List[str], fe: str) -> Tuple[Any, Dict[str, Any]]:
    """Fit one regression spec. Returns (model_or_None, meta_dict)."""
    df = df.dropna(subset=[dv, treatment] + exog_cols).copy()
    if treatment == KEY_IV_BETA_UK:
        # Restrict to firms with HIGH_BETA_UK in {0, 1}
        df = df[df["HIGH_BETA_UK"].isin([0.0, 1.0])]
        level_dummy = "HIGH_BETA_UK"
    elif treatment == KEY_IV_10K:
        df = df[df["HIGH_10K"].isin([0.0, 1.0])]
        level_dummy = "HIGH_10K"
    else:
        raise ValueError(f"Unknown treatment {treatment}")

    if len(df) < 100:
        return None, {"n_obs": int(len(df)), "skipped": "too few obs"}

    df = df.set_index(["gvkey", "cal_yr_qtr"])
    fit_kwargs: Dict[str, Any] = {"cov_type": "clustered"}
    if CLUSTERING.get("entity"):
        fit_kwargs["cluster_entity"] = True
    if CLUSTERING.get("time"):
        fit_kwargs["cluster_time"] = True

    exog_full = [treatment, level_dummy] + exog_cols
    # Note: Post_brexit absorbed by time FE in time-FE specs; let drop_absorbed handle it.
    if fe in ("industry", "industry_yq"):
        # Industry FE via other_effects (FF12) — simpler than FIC100xQ for industry-level.
        # For industry_yq we add time_effects=True in addition to FF12.
        time_effects = (fe == "industry_yq")
        df_fe = df.dropna(subset=["ff12_code"])
        model = PanelOLS(
            dependent=df_fe[dv],
            exog=df_fe[exog_full],
            entity_effects=False,
            time_effects=time_effects,
            other_effects=df_fe["ff12_code"],
            drop_absorbed=True,
            check_rank=False,
        )
    elif fe == "firm":
        model = PanelOLS(
            dependent=df[dv],
            exog=df[exog_full],
            entity_effects=True,
            time_effects=False,
            drop_absorbed=True,
            check_rank=False,
        )
    elif fe == "firm_yq":
        # Canonical TWFE-DiD: firm + cal_yr_qtr time effects.
        model = PanelOLS(
            dependent=df[dv],
            exog=df[exog_full],
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
            check_rank=False,
        )
    else:
        raise ValueError(f"Unknown FE config {fe}")

    try:
        result = model.fit(**fit_kwargs)
    except Exception as e:
        return None, {"n_obs": int(len(df)), "skipped": f"fit failed: {e}"}

    # Extract coefficients.
    meta = {
        "treatment": treatment,
        "dv": dv,
        "fe": fe,
        "n_obs": int(result.nobs),
        "r2": float(result.rsquared),
    }
    if treatment in result.params.index:
        meta["beta"] = float(result.params[treatment])
        meta["se"] = float(result.std_errors[treatment])
        meta["t"] = float(result.tstats[treatment])
        p_two = float(result.pvalues[treatment])
        # Convert to one-tailed positive (t > 0 → p_one = p_two/2 if t>0 else 1 - p_two/2).
        meta["p_two"] = p_two
        meta["p_one"] = (p_two / 2) if meta["beta"] >= 0 else 1 - (p_two / 2)
    else:
        meta.update({"beta": np.nan, "se": np.nan, "t": np.nan, "p_two": np.nan, "p_one": np.nan})
    return result, meta


def run_baseline_specs(panel: pd.DataFrame) -> List[Dict[str, Any]]:
    """16 baseline cells = 2 DVs x 2 treatments x 4 FE."""
    DVS = ["cash_brexit_dv", "UncResCEO_c"]
    TREATMENTS = [KEY_IV_BETA_UK, KEY_IV_10K]
    results: List[Dict[str, Any]] = []
    col = 0
    for dv in DVS:
        for treatment in TREATMENTS:
            for fe in FE_LADDER:
                col += 1
                exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
                model, meta = _fit_one(panel, dv, treatment, exog_cols, fe)
                meta["col"] = col
                results.append({"model": model, "meta": meta})
                msg = (f"  Col ({col:>2d}) DV={dv:14s} treat={treatment:12s} FE={fe:12s} "
                       f"n={meta.get('n_obs', 0):>5d} beta={meta.get('beta', np.nan):+.4f} "
                       f"p_one={meta.get('p_one', np.nan):.3f}")
                if meta.get("skipped"):
                    msg += f"  SKIPPED({meta['skipped']})"
                print(msg)
    return results


# ==============================================================================
# Output
# ==============================================================================

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


def write_outputs(results: List[Dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # CSV diagnostics.
    rows = []
    for r in results:
        m = r["meta"]
        rows.append(m)
    diag = pd.DataFrame(rows)
    diag.to_csv(out_dir / "model_diagnostics.csv", index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag)} rows)")

    # Markdown summary.
    lines = ["# H1.5 Brexit DiD — 16 Baseline Cells", ""]
    lines.append(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("| col | dv | treatment | fe | n | beta | p_one | sig |")
    lines.append("|-----|----|-----------|----|---|------|-------|-----|")
    for r in results:
        m = r["meta"]
        sig = _sig_stars(m.get("p_one", np.nan)) if m.get("beta", 0) >= 0 else ""
        lines.append(
            f"| {m.get('col', '?')} | {m.get('dv', '?')} | {m.get('treatment', '?')} | {m.get('fe', '?')} | "
            f"{m.get('n_obs', 0):,} | {m.get('beta', np.nan):+.4f} | {m.get('p_one', np.nan):.3f} | {sig} |"
        )
    (out_dir / "report_step4_H1_5_brexit_did.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved: report_step4_H1_5_brexit_did.md")

    # Canonical SuiteSpec emission (replaces prior stub dict 2026-05-13).
    # Produces standard suite_spec_<id>.json with per-cell columns array, so
    # docs/Draft/generate_all_tables.py renders this through render_suite()
    # uniformly with all other thesis suites (no stub fallback needed).
    _emit_canonical_suite_spec(results, out_dir)


# ------------------------------------------------------------------------------

# DV / treatment / FE display labels (paper-readable, not internal slugs).
_DV_LABEL = {
    "cash_brexit_dv": "Cash Holdings",
    "UncResCEO_c":    "UncResCEO",
}
_TREAT_LABEL = {
    "DiD_BetaUK": r"$\beta^{UK}$ tercile $\times$ Post",
    "DiD_10K":    r"10-K UK-mention $\times$ Post",
}
_FE_ENTITY_TIME = {
    "industry":    ("industry", "calendar_year"),
    "firm":        ("firm",     "calendar_year"),
    "industry_yq": ("industry", "calendar_year_quarter"),
    "firm_yq":     ("firm",     "calendar_year_quarter"),
}


def _emit_canonical_suite_spec(
    results: List[Dict[str, Any]], out_dir: Path,
) -> None:
    """Build standard SuiteSpec from per-cell results + call write_suite_spec().

    Per-column coefs include the treatment IV (DiD_BetaUK or DiD_10K) and all
    controls; the OTHER treatment is null-extracted because the model wasn't
    fit with it. The renderer skips null-valued cells.
    """
    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    for r in results:
        meta = r["meta"]
        model = r.get("model")
        treatment = meta["treatment"]
        dv = meta["dv"]
        fe = meta["fe"]
        fe_entity, fe_time = _FE_ENTITY_TIME[fe]
        level_dummy = "HIGH_BETA_UK" if treatment == KEY_IV_BETA_UK else "HIGH_10K"
        control_vars = ALL_CONTROLS_LAG1 + ["Post_brexit", level_dummy]

        adj_r2 = None
        n_firms = None
        dv_mean = None
        if model is not None:
            try:
                adj_r2 = float(model.rsquared)
            except Exception:
                pass
            try:
                dv_mean = float(model.model.dependent.dataframe.mean().iloc[0])
            except Exception:
                pass

        col_metadata.append({
            "col":          meta["col"],
            "dv":           dv,
            "fe_entity":    fe_entity,
            "fe_time":      fe_time,
            "control_vars": control_vars,
            "n_obs":        int(meta.get("n_obs", 0)),
            "n_firms":      n_firms,
            "r2":           float(meta.get("r2", float("nan"))),
            "adj_r2":       adj_r2,
            "dv_mean":      dv_mean,
            "cluster_fallback": False,
        })

        merged_coefs: Dict[str, Dict[str, Any]] = {}
        if model is not None:
            tcoefs = extract_coefs_panelols(
                model=model,
                key_ivs=[treatment],
                all_vars=[treatment],
                hyp_dir="positive",
            )
            merged_coefs.update(tcoefs)
            ctrl_coefs = extract_coefs_panelols(
                model=model,
                key_ivs=[],
                all_vars=control_vars,
                hyp_dir="none",
            )
            merged_coefs.update(ctrl_coefs)
        # Drop coefs whose SE / p_two is NaN (variable absorbed by FE or
        # singular). Pydantic schema requires float; renderer can't display
        # NaN coefficients anyway.
        merged_coefs = {
            k: v for k, v in merged_coefs.items()
            if v.get("se") is not None
            and not (isinstance(v["se"], float) and np.isnan(v["se"]))
            and v.get("p_two") is not None
            and not (isinstance(v["p_two"], float) and np.isnan(v["p_two"]))
        }
        coefs_per_col.append(merged_coefs)

    ivs = [
        {"name": KEY_IV_BETA_UK,
         "label": _TREAT_LABEL[KEY_IV_BETA_UK],
         "tail":  "one_pos"},
        {"name": KEY_IV_10K,
         "label": _TREAT_LABEL[KEY_IV_10K],
         "tail":  "one_pos"},
    ]

    # 4 block headers: cols 1-4 Cash×β^UK, 5-8 Cash×10K, 9-12 Speech×β^UK, 13-16 Speech×10K.
    header_rows = [
        [
            {"label": r"Cash Holdings: $\beta^{UK}$ treatment", "span": 4},
            {"label": r"Cash Holdings: 10-K treatment",          "span": 4},
            {"label": r"UncResCEO: $\beta^{UK}$ treatment",      "span": 4},
            {"label": r"UncResCEO: 10-K treatment",              "span": 4},
        ],
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR_NAME,
        sub_tables=[{
            "suite_id":    SUITE_ID,
            "dir_name":    SUITE_DIR_NAME,
            "title":       SUITE_TITLE,
            "caption":     SUITE_TITLE,
            "label":       SUITE_LABEL,
            "col_range":   list(range(1, len(col_metadata) + 1)),
            "header_rows": header_rows,
            "suite_type":  "standard",
        }],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=(
            "Brexit window 2010Q1-2016Q4. Treated firms: top tercile of "
            r"$\beta^{UK}$ (cols 1-4, 9-12) or >5 UK-mentions in 2015 10-K "
            "(cols 5-8, 13-16). Excludes financial + utility firms."
        ),
        clustering=CLUSTERING,
        tail={"direction": "positive", "applies_to": "ivs_only"},
        ivs=ivs,
        controls={
            "base": list(ALL_CONTROLS_LAG1) + ["Post_brexit", "HIGH_BETA_UK", "HIGH_10K"],
            "extended_only": [],
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(description="Stage 4: H1.5 Brexit DiD (Cash + Speech)")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp

    print("=" * 80)
    print("STAGE 4: H1.5 BREXIT DiD ON CASH + SPEECH (Campello 2022 verbatim)")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Window:     2010Q1 - 2016Q4 ({WINDOW_START_YQ}-{WINDOW_END_YQ})")
    print(f"POST:       cal_yr_qtr >= {POST_START_YQ} (2016Q3 - Brexit vote)")
    print(f"Clustering: double {CLUSTERING}")

    panel, panel_file = load_h1_panel(root)
    print(f"H1 panel: {len(panel):,} call-rows ({panel_file.parent.name})")
    panel = merge_uncresceo(panel, root)

    # Brexit-window-restricted gvkey set for raw Compustat re-load efficiency.
    panel_brx = panel[(panel["cal_yr_qtr"] >= WINDOW_START_YQ - 1) & (panel["cal_yr_qtr"] <= WINDOW_END_YQ)]
    gvkeys_keep = set(panel_brx["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)

    builders = load_brexit_builders(root)

    cell_panel = assemble_panel(panel, raw_comp, builders)

    print("\n  --- Running 16 baseline regressions ---")
    results = run_baseline_specs(cell_panel)

    write_outputs(results, out_dir)
    duration = (datetime.now() - t0).total_seconds()
    print(f"\nDuration: {duration:.1f}s")
    print(f"Cells produced: {sum(1 for r in results if r['meta'].get('beta') is not None and not np.isnan(r['meta'].get('beta', np.nan)))} / {len(results)}")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main())
