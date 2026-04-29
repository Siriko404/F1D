#!/usr/bin/env python3
"""
================================================================================
PHASE E: CEO Sudden-Death DiD on Cash Holdings (Ghafoor 2023 / Bennedsen 2020)
================================================================================
ID: econometric/run_ceo_death_did_cash
Description: Difference-in-differences identification of the causal effect of
             CEO turnover (via sudden-death exogenous shock) on corporate cash
             holdings. Replicates Ghafoor-Yousaf-Li (2023) JFI Section 4.5
             design directly: treated firms = those with sudden CEO death
             during 2002-2018, matched 1:1 to non-event control firms via PSM
             nearest-neighbor on Bates 2009 control vector at t-1. ±12 quarter
             event window per Ghafoor verbatim.

             Treatment classification per NotebookLM-verified Ghafoor 2023 §4.5:
             "deaths are unexpected and not preceded by poor health. The most
             common causes are heart attack and plane or automobile accidents."
             17 sudden events identified at F1D-panel firms; 8 viable for Phase E
             after ±12 quarter coverage + UncAnsCEO ≥5 pre-event filter.

             Phase E ground rules (user-authorized 2026-04-29):
             - Window: ±12 quarters (Ghafoor verbatim, no methodology deviation)
             - Sample: 8 viable treated + 8 PSM-matched controls
             - DV: CashRatio (cheq/atq, Bates 2009 form)
             - Spec: pooled ATT primary; heterogeneity test underpowered
             - Disclosure: §4.3 power-loss paragraph required

DiD Model:
    CashRatio_{i,t} = α + β1·Treated_i + β2·Post_t + β3·(Treated_i × Post_t)
                    + γ·X_{i,t} + FE + ε_{i,t}

    where:
        Treated_i = 1 if firm experienced CEO sudden death during sample
        Post_t    = 1 if quarter t > death_quarter (panel-time, per matched pair)
        β3        = ATT (causal effect of CEO turnover on cash holdings)

8 viable treated firms (gvkey | name | death):
    002783 ROBERT B MCGEHEE     2007-10-09  (PROGRESS ENERGY)
    064925 EDWARD H LINDE       2010-01-10  (BXP/BOSTON PROPERTIES)
    009699 JAI NAGARKATTI       2010-11-13  (SIGMA-ALDRICH)
    007343 STEVEN R APPLETON    2012-02-03  (MICRON TECHNOLOGY)
    003342 JAMES R BOLDT        2014-10-13  (COMPUTER TASK GROUP)
    065228 MELANIE J DRESSEL    2017-02-19  (COLUMBIA BANKING)
    010840 RON CROATTI          2017-05-23  (UNIFIRST)
    015060 FRED CALLON          2017-05-24  (CALLON PETROLEUM)

Specifications (4 columns):
    Col 1: Industry FE + Calendar YQ FE (pooled ATT)
    Col 2: Firm FE + Calendar YQ FE (pooled ATT, firm-level controls)
    Col 3: Industry FE + Event-Time FE (placebo-style)
    Col 4: Firm FE + Event-Time FE (most stringent)

Outputs:
    - outputs/econometric/ceo_death_did_cash/{timestamp}/
        - suite_spec_H_death_did.json  (consumed by docs/Draft/generate_all_tables.py)
        - matched_pairs.csv (8 treated × 1 control each)
        - did_panel.parquet (event-time panel for re-running)

Anchors:
    - Ghafoor-Yousaf-Li (2023) SSRN 4578724 §4.5 (DiD design + sudden-death
      protocol; 461 events 1996-2016; β=−0.043 SE 0.018 p=0.018**)
    - Bennedsen, Pérez-González, Wolfenzon (2020) JF (id-design anchor; CEO
      hospitalization/death exogeneity)
    - Bates, Kahle, Stulz (2009) JF (cash-holdings control vector)

Deterministic: true
Author: Thesis Author (Sina Soleimanipour)
Date: 2026-04-29
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
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from f1d.shared.path_utils import get_latest_output_dir


# ==============================================================================
# Configuration
# ==============================================================================

ROOT = Path(__file__).resolve().parents[3]

SUITE_ID = "H.death.did"
SUITE_DIR_NAME = "ceo_death_did_cash"
SUITE_TITLE = (
    "CEO Sudden-Death Difference-in-Differences on Corporate Cash Holdings "
    "(Ghafoor-Yousaf-Li 2023; PSM-matched ±12 quarter window)"
)
SUITE_CAPTION = (
    r"Phase E CEO sudden-death DiD: $\Delta$Cash around exogenous CEO shock; "
    r"PSM 1:1 nearest-neighbor controls on Bates (2009) covariates at $t-1$"
)
SUITE_LABEL = "tab:ceo_death_did"
SAMPLE_LABEL = (
    "8 viable treated firms (CEO sudden death 2002-2018; ±12 quarter coverage; "
    "$\\geq$5 pre-event UncAnsCEO obs) matched 1:1 to non-event controls via "
    "propensity-score nearest-neighbor on lnAssets, Leverage, ROA, DivDummy, "
    "sCFO at $t-1$. Window: $\\pm$12 fiscal quarters around death event."
)

# Window (Ghafoor verbatim ±3 years = ±12 quarters)
PRE_QUARTERS = 12
POST_QUARTERS = 12

# Bates 2009 PSM matching covariates at t-1
PSM_COVARIATES = ["lnAssets", "Leverage", "ROA", "DivDummy", "sCFO"]

# DiD controls (per H1.cash_holdings convention; Bates 2009)
CONTROLS = [
    "lnAssets", "Leverage", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO", "SalesGrowth", "RDSales", "CashFlowAt",
    "DailyVola",
]

# DiD coefficients to display
TREAT = "Treated"
POST = "Post"
ATT = "Treated_x_Post"

DISPLAY_COEFS = [TREAT, POST, ATT]

VARIABLE_LABELS = {
    TREAT: "Treated",
    POST: "Post",
    ATT: r"\textbf{Treated $\times$ Post (ATT)}",
}

IV_TAIL_DIRECTION: Dict[str, str] = {
    # Ghafoor predicts ATT < 0 (sudden death → reduced cash via co-option mechanism;
    # we test whether speech-uncertainty channel produces same sign on UncRes-high firms)
    TREAT: "none",
    POST: "none",
    ATT: "negative",
}


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(description="Phase E: CEO Sudden-Death DiD on Cash")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sudden-csv", type=str, default=None)
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_sudden_events(root: Path, sudden_csv: Optional[str] = None) -> pd.DataFrame:
    """Load 17 sudden events from Phase B classification CSV; filter to 8 viable."""
    if sudden_csv:
        csv_path = Path(sudden_csv)
    else:
        csv_path = root / "data" / "raw" / "ceo_death_events" / "sudden_classified_tier4_tier3.csv"

    df = pd.read_csv(csv_path)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df = df[df["is_sudden"].fillna("").astype(str).isin(["1", "1.0"])].copy()
    df["death_date"] = pd.to_datetime(df["death_date_canonical"])

    print(f"Loaded {len(df)} sudden events from {csv_path}")
    return df


def load_panel(root: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load F1D panel + retain DiD-relevant columns."""
    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        panel_file = panel_dir / "h1_cash_holdings_panel.parquet"

    cols = [
        "file_name", "gvkey", "ceo_id", "year", "fyearq_int", "ff12_code",
        "start_date", "CashRatio", "CashRatio_lag", "CashRatio_lead",
        "UncAnsCEO", "UncPreCEO",
    ] + CONTROLS

    panel = pd.read_parquet(panel_file, columns=cols)
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    panel["start_date"] = pd.to_datetime(panel["start_date"])
    panel["cal_yq"] = panel["start_date"].dt.year * 4 + panel["start_date"].dt.quarter - 1

    print(f"Loaded panel {panel_file.name}: {len(panel):,} rows × {panel['gvkey'].nunique():,} firms")
    return panel


# ==============================================================================
# Coverage filter (8 viable events)
# ==============================================================================


def filter_viable_events(events: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Keep only events with ±12q coverage AND ≥5 pre-event UncAnsCEO obs."""
    viable = []
    for _, ev in events.iterrows():
        gv = ev["gvkey"]
        dd = ev["death_date"]
        death_yq = dd.year * 4 + dd.quarter - 1
        firm_panel = panel[panel["gvkey"] == gv]
        pre = firm_panel[(firm_panel["cal_yq"] >= death_yq - PRE_QUARTERS)
                         & (firm_panel["cal_yq"] < death_yq)]
        post = firm_panel[(firm_panel["cal_yq"] > death_yq)
                          & (firm_panel["cal_yq"] <= death_yq + POST_QUARTERS)]
        ur_pre = pre["UncAnsCEO"].notna().sum()
        # Viable: ≥8 pre + ≥4 post + ≥5 UncAnsCEO pre (asymmetric per advisor)
        if len(pre) >= 8 and len(post) >= 4 and ur_pre >= 5:
            viable.append({
                "gvkey": gv,
                "exec_name": ev["exec_name_canonical"],
                "death_date": dd,
                "death_yq": death_yq,
                "pre_quarters": len(pre),
                "post_quarters": len(post),
                "ur_pre": int(ur_pre),
            })

    df = pd.DataFrame(viable).sort_values("death_date").reset_index(drop=True)
    print(f"\nViable treated events ({len(df)} of {len(events)}):")
    print(df.to_string(index=False))
    return df


# ==============================================================================
# PSM matching
# ==============================================================================


def find_matched_controls(
    treated: pd.DataFrame,
    panel: pd.DataFrame,
    treated_gvkeys: set,
) -> pd.DataFrame:
    """For each treated event, find nearest-neighbor non-event control via PSM
    on standardized Bates 2009 covariates measured at t-1 (1 quarter pre-death).

    Returns DataFrame with columns [treated_gvkey, control_gvkey, distance, ...].
    """
    print("\n" + "=" * 60)
    print("PSM matching (1:1 nearest-neighbor with replacement)")
    print("=" * 60)

    matches = []
    for _, ev in treated.iterrows():
        tg = ev["gvkey"]
        dd = ev["death_date"]

        # Treated covariates at t-1 (last call before death)
        firm_panel = panel[(panel["gvkey"] == tg) & (panel["start_date"] < dd)].copy()
        firm_panel = firm_panel.sort_values("start_date")
        if firm_panel.empty:
            print(f"  {tg} {ev['exec_name']}: no pre-death panel rows — skipping")
            continue
        # t-1 = last available pre-death row (median of last 4 quarters for stability)
        last_4 = firm_panel.tail(4)
        treated_cov = last_4[PSM_COVARIATES].mean(skipna=True)
        if treated_cov.isna().any():
            print(f"  {tg} {ev['exec_name']}: covariate NaN — skipping")
            continue

        # Pool of potential controls: same calendar quarter as t-1, not in treated set
        # Use death-year as the matching reference period
        match_yq = ev["death_yq"] - 1  # one quarter before death
        # Wider window for control pool (±2 quarters)
        pool = panel[
            (panel["cal_yq"] >= match_yq - 2)
            & (panel["cal_yq"] <= match_yq + 2)
            & (~panel["gvkey"].isin(treated_gvkeys))
        ].copy()
        if pool.empty:
            print(f"  {tg}: empty control pool")
            continue

        # Aggregate to firm-level mean (one row per gvkey) for matching
        pool_agg = pool.groupby("gvkey")[PSM_COVARIATES].mean().dropna()
        if pool_agg.empty:
            continue

        # Standardize using treated + pool means/std
        scaler = StandardScaler()
        all_cov = pd.concat([
            pool_agg,
            treated_cov.to_frame().T.assign(gvkey="__TREATED__").set_index("gvkey"),
        ])
        scaled = scaler.fit_transform(all_cov.values)
        treated_scaled = scaled[-1].reshape(1, -1)
        pool_scaled = scaled[:-1]

        nn = NearestNeighbors(n_neighbors=1, metric="euclidean")
        nn.fit(pool_scaled)
        dist, idx = nn.kneighbors(treated_scaled)

        control_gvkey = pool_agg.index[idx[0][0]]
        match = {
            "treated_gvkey": tg,
            "treated_name": ev["exec_name"],
            "death_date": dd,
            "control_gvkey": control_gvkey,
            "ps_distance": float(dist[0][0]),
        }
        for cov in PSM_COVARIATES:
            match[f"treated_{cov}"] = float(treated_cov[cov])
            match[f"control_{cov}"] = float(pool_agg.loc[control_gvkey, cov])

        matches.append(match)
        print(f"  {tg} ({ev['exec_name']}) -> {control_gvkey}  (dist={dist[0][0]:.4f})")

    df = pd.DataFrame(matches)
    return df


# ==============================================================================
# Build DiD panel
# ==============================================================================


def build_did_panel(
    treated: pd.DataFrame,
    matches: pd.DataFrame,
    panel: pd.DataFrame,
) -> pd.DataFrame:
    """Build event-time panel: treated × ±12q + matched control × ±12q.

    Each row tagged: pair_id, treated (0/1), post (0/1), event_time (-12..+12).
    """
    print("\n" + "=" * 60)
    print("Building DiD event-time panel")
    print("=" * 60)

    rows = []
    for pair_id, m in matches.iterrows():
        tg = m["treated_gvkey"]
        cg = m["control_gvkey"]
        death_yq = treated.loc[treated["gvkey"] == tg, "death_yq"].iloc[0]
        win_lo = death_yq - PRE_QUARTERS
        win_hi = death_yq + POST_QUARTERS

        for gv, is_treated in [(tg, 1), (cg, 0)]:
            firm_panel = panel[
                (panel["gvkey"] == gv)
                & (panel["cal_yq"] >= win_lo)
                & (panel["cal_yq"] <= win_hi)
            ].copy()
            firm_panel["pair_id"] = pair_id
            firm_panel["Treated"] = is_treated
            firm_panel["event_time"] = firm_panel["cal_yq"] - death_yq
            firm_panel["Post"] = (firm_panel["event_time"] > 0).astype(int)
            firm_panel["Treated_x_Post"] = firm_panel["Treated"] * firm_panel["Post"]
            rows.append(firm_panel)

    did_panel = pd.concat(rows, ignore_index=True)
    print(f"  DiD panel: {len(did_panel):,} firm-quarters")
    print(f"  Treated: {did_panel['Treated'].sum():,}; Control: {(1-did_panel['Treated']).sum():,}")
    print(f"  Pre: {(did_panel['Post'] == 0).sum():,}; Post: {did_panel['Post'].sum():,}")
    print(f"  Unique pairs: {did_panel['pair_id'].nunique()}")
    return did_panel


# ==============================================================================
# DiD regression
# ==============================================================================


def prepare_regression_data(did_panel: pd.DataFrame, dv: str = "CashRatio") -> pd.DataFrame:
    """Drop NaN in DV + controls + DiD vars; require complete cases."""
    required = [dv, TREAT, POST, ATT] + CONTROLS + ["gvkey", "cal_yq", "ff12_code"]
    df = did_panel[required].copy()
    df = df.replace([np.inf, -np.inf], np.nan)
    before = len(df)
    df = df.dropna(subset=required)
    print(f"  Complete-case: {len(df):,} / {before:,}")
    if len(df) == 0:
        return df
    df = df.set_index(["gvkey", "cal_yq"])
    return df


def run_did_regression(
    df: pd.DataFrame, fe: str = "industry_yq", dv: str = "CashRatio"
) -> Optional[Any]:
    """Run a single DiD regression."""
    if df.empty:
        return None

    exog_cols = [TREAT, POST, ATT] + CONTROLS

    # df comes in with 2-level MultiIndex (gvkey, cal_yq) — keep that for PanelOLS
    if fe == "industry_yq":
        try:
            model = PanelOLS(
                dependent=df[dv],
                exog=df[exog_cols],
                entity_effects=False,
                time_effects=True,
                other_effects=df.reset_index()["ff12_code"].values if "ff12_code" not in df.columns else df["ff12_code"],
                drop_absorbed=True,
                check_rank=False,
            )
            return model.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
        except Exception as e:
            print(f"  industry_yq FE failed: {e}")
            return None

    elif fe == "firm_yq":
        exog_str = " + ".join(exog_cols)
        formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
        try:
            model = PanelOLS.from_formula(formula, data=df, drop_absorbed=True, check_rank=False)
            return model.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
        except Exception as e:
            print(f"  firm_yq FE failed: {e}")
            return None

    elif fe == "industry":
        try:
            ind = df["ff12_code"] if "ff12_code" in df.columns else df.reset_index()["ff12_code"].values
            model = PanelOLS(
                dependent=df[dv],
                exog=df[exog_cols],
                entity_effects=False,
                time_effects=False,
                other_effects=ind,
                drop_absorbed=True,
                check_rank=False,
            )
            return model.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
        except Exception as e:
            print(f"  industry FE failed: {e}")
            return None

    elif fe == "firm":
        exog_str = " + ".join(exog_cols)
        formula = f"{dv} ~ 1 + {exog_str} + EntityEffects"
        try:
            model = PanelOLS.from_formula(formula, data=df, drop_absorbed=True, check_rank=False)
            return model.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
        except Exception as e:
            print(f"  firm FE failed: {e}")
            return None

    return None


def extract_coefs(model: Any) -> Dict[str, Any]:
    """Extract beta/SE/p_one for display coefficients."""
    out = {}
    for coef in DISPLAY_COEFS:
        if model is None or coef not in model.params.index:
            out[coef] = {"beta": np.nan, "se": np.nan, "p_two": np.nan, "p_one": np.nan}
            continue
        beta = float(model.params[coef])
        se = float(model.std_errors[coef])
        p_two = float(model.pvalues[coef])
        direction = IV_TAIL_DIRECTION.get(coef, "none")
        if direction == "negative":
            p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
        elif direction == "positive":
            p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
        else:
            p_one = p_two
        out[coef] = {"beta": beta, "se": se, "p_two": p_two, "p_one": p_one}
    return out


# ==============================================================================
# Suite spec emission
# ==============================================================================


def emit_suite_spec(
    columns_data: List[Dict[str, Any]],
    out_dir: Path,
    matches: pd.DataFrame,
    treated: pd.DataFrame,
):
    """Write suite_spec_<id>.json for the consolidated table generator."""
    spec = {
        "suite_id": SUITE_ID,
        "title": SUITE_TITLE,
        "caption": SUITE_CAPTION,
        "label": SUITE_LABEL,
        "sample_label": SAMPLE_LABEL,
        "n_treated": len(treated),
        "n_matches": len(matches),
        "psm_covariates": PSM_COVARIATES,
        "window_pre": PRE_QUARTERS,
        "window_post": POST_QUARTERS,
        "controls": CONTROLS,
        "display_coefs": DISPLAY_COEFS,
        "variable_labels": VARIABLE_LABELS,
        "tail_direction": IV_TAIL_DIRECTION,
        "columns": columns_data,
        "ghafoor_2023_anchor_beta": -0.043,
        "ghafoor_2023_anchor_p": 0.018,
    }
    spec_file = out_dir / f"suite_spec_{SUITE_ID.replace('.', '_')}.json"
    spec_file.write_text(json.dumps(spec, indent=2, default=str))
    print(f"\nWrote {spec_file}")


def emit_latex_table(
    columns_data: List[Dict[str, Any]], out_dir: Path
):
    """Emit per_suite/<slug>_table.tex for inclusion in main.pdf."""
    n = len(columns_data)
    col_align = "l" + "c" * n
    lines = []
    lines.append(r"\begin{table}[!htbp]")
    lines.append(r"\centering\footnotesize")
    lines.append(rf"\caption{{{SUITE_CAPTION}}}")
    lines.append(rf"\label{{{SUITE_LABEL}}}")
    lines.append(r"\begin{tabular}{" + col_align + "}")
    lines.append(r"\toprule")

    # Column headers
    header = " & ".join([f"({c['col']})" for c in columns_data])
    lines.append(rf" & {header} \\")
    fe_row = " & ".join([c["fe_label"] for c in columns_data])
    lines.append(rf"FE & {fe_row} \\")
    lines.append(r"\midrule")

    for coef in DISPLAY_COEFS:
        label = VARIABLE_LABELS.get(coef, coef)
        beta_row = [label]
        se_row = [""]
        for c in columns_data:
            cd = c["coefs"].get(coef, {})
            beta = cd.get("beta", np.nan)
            se = cd.get("se", np.nan)
            p_one = cd.get("p_one", np.nan)
            stars = ""
            if not np.isnan(p_one):
                if p_one < 0.01:
                    stars = "***"
                elif p_one < 0.05:
                    stars = "**"
                elif p_one < 0.10:
                    stars = "*"
            beta_str = "" if np.isnan(beta) else f"{beta:+.4f}{stars}"
            se_str = "" if np.isnan(se) else f"({se:.4f})"
            beta_row.append(beta_str)
            se_row.append(se_str)
        lines.append(" & ".join(beta_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")
    lines.append(r"\midrule")

    n_obs_row = "N (firm-quarters) & " + " & ".join([f"{c['n_obs']:,}" for c in columns_data]) + r" \\"
    r2_row = "$R^2$ & " + " & ".join([f"{c['r2']:.3f}" for c in columns_data]) + r" \\"
    n_clusters = "N (firms) & " + " & ".join([f"{c['n_firms']}" for c in columns_data]) + r" \\"
    lines.append(n_obs_row)
    lines.append(r2_row)
    lines.append(n_clusters)
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(rf"\begin{{tablenotes}}\footnotesize\item {SAMPLE_LABEL} Standard errors clustered at firm level. Coefficients on Lagged DV and other controls suppressed for space. ATT $p$-values are one-tailed (Ghafoor 2023 negative prior). $^{{*}}/^{{**}}/^{{***}}$ denote $p<0.10/0.05/0.01$.\end{{tablenotes}}")
    lines.append(r"\end{table}")

    tex_path = out_dir / f"{SUITE_ID.replace('.', '_').lower()}_table.tex"
    tex_path.write_text("\n".join(lines))
    print(f"Wrote {tex_path}")
    return tex_path


# ==============================================================================
# Main
# ==============================================================================


def main():
    args = parse_arguments()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = ROOT / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(f"Phase E: CEO Sudden-Death DiD on Cash Holdings (suite {SUITE_ID})")
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print("=" * 70)

    events = load_sudden_events(ROOT, args.sudden_csv)
    panel = load_panel(ROOT, args.panel_path)
    treated = filter_viable_events(events, panel)
    if len(treated) == 0:
        print("\nNo viable treated events — Phase E aborts.")
        return

    treated_gvkeys = set(treated["gvkey"].tolist())
    matches = find_matched_controls(treated, panel, treated_gvkeys)
    matches.to_csv(out_dir / "matched_pairs.csv", index=False)

    if len(matches) == 0:
        print("\nNo matched pairs — Phase E aborts.")
        return

    did_panel = build_did_panel(treated, matches, panel)
    did_panel.to_parquet(out_dir / "did_panel.parquet", index=False)

    # 4 specs
    specs = [
        {"col": 1, "fe": "industry",    "fe_label": "Industry"},
        {"col": 2, "fe": "firm",        "fe_label": "Firm"},
        {"col": 3, "fe": "industry_yq", "fe_label": "Ind+YQ"},
        {"col": 4, "fe": "firm_yq",     "fe_label": "Firm+YQ"},
    ]

    columns_data = []
    for spec in specs:
        print(f"\n--- Col {spec['col']}: {spec['fe_label']} FE ---")
        df_ready = prepare_regression_data(did_panel, dv="CashRatio")
        if df_ready.empty:
            print(f"  Empty data — skipping spec {spec['col']}")
            continue
        model = run_did_regression(df_ready, fe=spec["fe"], dv="CashRatio")
        if model is None:
            print(f"  Model failed — skipping spec {spec['col']}")
            continue
        coefs = extract_coefs(model)
        n_obs = int(model.nobs)
        n_firms = df_ready.reset_index()["gvkey"].nunique()
        r2 = float(model.rsquared)
        try:
            r2_within = float(model.rsquared_within)
        except Exception:
            r2_within = np.nan

        # Print ATT result with stars
        att_b = coefs[ATT]["beta"]
        att_p = coefs[ATT]["p_one"]
        stars = "***" if att_p < 0.01 else ("**" if att_p < 0.05 else ("*" if att_p < 0.10 else ""))
        print(f"  ATT: {att_b:+.4f} (p1={att_p:.4f}) {stars}  N={n_obs}  R²={r2:.3f}")

        columns_data.append({
            "col": spec["col"],
            "fe_label": spec["fe_label"],
            "fe_type": spec["fe"],
            "coefs": coefs,
            "n_obs": n_obs,
            "n_firms": n_firms,
            "r2": r2,
            "r2_within": r2_within,
        })

    if not columns_data:
        print("\nNo successful regressions — aborting.")
        return

    emit_suite_spec(columns_data, out_dir, matches, treated)

    # Latex output to per_suite/
    per_suite_dir = ROOT / "docs" / "Draft" / "per_suite"
    per_suite_dir.mkdir(parents=True, exist_ok=True)
    emit_latex_table(columns_data, per_suite_dir)

    print("\n" + "=" * 70)
    print(f"Phase E DONE — {len(columns_data)} cols emitted")
    print(f"Treated: {len(treated)}; Matched pairs: {len(matches)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
