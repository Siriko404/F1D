"""H1.5 fallback diagnostic — single-topic HighTrade-only and HighTax-only DiD.

Tests the plan v3 risks-register mitigation: if BothHigh × Post is null, try
each topic alone to see if the intersection is the noisy cut.

Treatment defs (mirroring spec v3 logic, single-dim):
   HighTrade_i = 1 if firm i's mean PRiskT_trade over 2011q4-2016q3 >=
                  FF12-industry-own median; else 0
   HighTax_i   = 1 if firm i's mean PRiskT_tax   over 2011q4-2016q3 >=
                  FF12-industry-own median; else 0

   DiD_trade_{i,t} = HighTrade_i * Post_t
   DiD_tax_{i,t}   = HighTax_i   * Post_t
   Post_t          = (cal_yr_qtr >= 2016q4)

Sample window: Q3 2014 - Q4 2018 (Hu cutoff)
Sample: Main (FF12 not in {8,11})
Controls: F1D canonical 12-var
DVs: CashRatio, UncResCEO_c

Output: prints 16 regressions (8 trade-only + 8 tax-only). One-tail POS expected.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

# Make F1D importable from this script.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index
from f1d.shared.variables.political_risk_subtopics import (
    PRiskSubtopicsBuilder,
    _parse_cal_q,
)
from f1d.shared.variables.winsorization import winsorize_by_year


PRE_START = "2011q4"
PRE_END = "2016q3"
POST_THRESH = 20164

CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO", "SalesGrowth", "RDSales",
    "CashFlowAt", "DailyVola", "Lagged_DV",
]


def in_window(q: str) -> bool:
    return PRE_START <= q <= PRE_END


def load_h1_panel() -> pd.DataFrame:
    panel_dir = get_latest_output_dir(
        ROOT / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    )
    panel_file = panel_dir / "h1_cash_holdings_panel.parquet"
    cols = [
        "file_name", "gvkey", "ceo_id", "year", "ff12_code", "start_date",
        "CashRatio", "CashRatio_lag",
        *[c for c in CONTROLS if c != "Lagged_DV"],
    ]
    panel = pd.read_parquet(panel_file, columns=cols)
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    panel["start_date"] = pd.to_datetime(panel["start_date"])
    return build_cal_yr_qtr_index(panel)


def load_uncres() -> pd.DataFrame:
    full_dir = get_latest_output_dir(
        ROOT / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    return pd.read_parquet(
        full_dir / "ceo_clarity_residual.parquet",
        columns=["file_name", "UncResCEO"],
    )


def build_single_topic_labels(panel: pd.DataFrame) -> pd.DataFrame:
    """Compute per-gvkey: trade_pre, tax_pre, HighTrade, HighTax."""
    # Load PRisk pre-window data directly (full universe, not just F1D).
    prisk_path = ROOT / "inputs" / "FirmLevelRisk" / "firmquarter_2022q1.csv"
    cols = ["gvkey", "date", "PRiskT_trade", "PRiskT_tax"]
    df = pd.read_csv(prisk_path, sep="\t", usecols=cols, on_bad_lines="skip")
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cal_q"] = df["date"].apply(_parse_cal_q)
    df = df.dropna(subset=["cal_q"])
    df["year"] = df["cal_q"].str[:4].astype(int)
    df = df[df["year"].between(int(PRE_START[:4]), int(PRE_END[:4]))].copy()
    df["_sum"] = df[["PRiskT_trade", "PRiskT_tax"]].sum(axis=1, skipna=True)
    df = (
        df.sort_values("_sum", ascending=False)
        .drop_duplicates(subset=["gvkey", "cal_q"], keep="first")
        .drop(columns=["_sum"])
    )
    df = winsorize_by_year(df, ["PRiskT_trade", "PRiskT_tax"], year_col="year")

    in_pre = df["cal_q"].apply(in_window)
    df = df[in_pre].copy()
    firm_means = (
        df.groupby("gvkey")[["PRiskT_trade", "PRiskT_tax"]]
        .mean().reset_index()
        .rename(columns={
            "PRiskT_trade": "trade_pre_mean",
            "PRiskT_tax": "tax_pre_mean",
        })
    )
    n_obs = df.groupby("gvkey")["cal_q"].nunique().rename("n_pre_obs")
    firm_means = firm_means.merge(n_obs, on="gvkey", how="left")
    firm_means = firm_means[firm_means["n_pre_obs"] >= 8].copy()

    # ff12 from H1 panel
    gv_ff12 = (
        panel.dropna(subset=["ff12_code"])
        .groupby("gvkey")["ff12_code"].first().reset_index()
    )
    firm_means = firm_means.merge(gv_ff12, on="gvkey", how="left")
    firm_means = firm_means.dropna(subset=["ff12_code"])

    firm_means["trade_med_ff12"] = firm_means.groupby("ff12_code")[
        "trade_pre_mean"
    ].transform("median")
    firm_means["tax_med_ff12"] = firm_means.groupby("ff12_code")[
        "tax_pre_mean"
    ].transform("median")

    firm_means["HighTrade"] = (
        firm_means["trade_pre_mean"] >= firm_means["trade_med_ff12"]
    ).astype(float)
    firm_means["HighTax"] = (
        firm_means["tax_pre_mean"] >= firm_means["tax_med_ff12"]
    ).astype(float)

    return firm_means[
        ["gvkey", "trade_pre_mean", "tax_pre_mean", "HighTrade", "HighTax"]
    ]


def attach_speech_lag(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["gvkey", "cal_yr_qtr", "start_date"], kind="stable").copy()
    panel["UncResCEO_c_lag"] = panel.groupby("gvkey", sort=False)[
        "UncResCEO_c"
    ].shift(1)
    return panel


def run_did(
    panel: pd.DataFrame, dv: str, key_iv: str, level_dummy: str,
    fe: str, controls: List[str],
) -> Dict[str, Any]:
    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"
    base_fe = fe.replace("_yq", "")

    # Lagged_DV mapping
    if dv == "CashRatio":
        lag_col = "CashRatio_lag"
    elif dv == "UncResCEO_c":
        lag_col = "UncResCEO_c_lag"
    else:
        raise ValueError(f"Unknown DV: {dv}")
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    needed = [dv, key_iv, level_dummy, "Post_trump"] + controls + ["gvkey", time_col, "ff12_code"]
    miss = [c for c in needed if c not in panel.columns]
    if miss:
        raise ValueError(f"missing cols: {miss}")

    df = panel.dropna(subset=needed).copy()
    df = df[df[dv].notna()].copy()

    # Min 3 calls per firm
    fc = df["gvkey"].value_counts()
    df = df[df["gvkey"].isin(fc[fc >= 3].index)].copy()

    if len(df) < 100:
        return {
            "fe": fe, "dv": dv, "n": len(df),
            "beta": np.nan, "p_two": np.nan, "se": np.nan,
        }

    df_panel = df.set_index(["gvkey", time_col])
    exog_list = [key_iv, level_dummy, "Post_trump"] + controls

    if base_fe == "industry":
        m = PanelOLS(
            dependent=df_panel[dv],
            exog=df_panel[exog_list],
            entity_effects=False,
            time_effects=True,
            other_effects=df_panel["ff12_code"],
            drop_absorbed=True,
            check_rank=False,
        ).fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    else:
        formula = f"{dv} ~ 1 + " + " + ".join(exog_list) + " + EntityEffects + TimeEffects"
        m = PanelOLS.from_formula(
            formula, data=df_panel, drop_absorbed=True
        ).fit(cov_type="clustered", cluster_entity=True, cluster_time=False)

    if key_iv not in m.params.index:
        return {
            "fe": fe, "dv": dv, "n": int(m.nobs),
            "beta": np.nan, "p_two": np.nan, "se": np.nan,
        }
    return {
        "fe": fe, "dv": dv, "n": int(m.nobs),
        "beta": float(m.params[key_iv]),
        "se": float(m.std_errors[key_iv]),
        "p_two": float(m.pvalues[key_iv]),
    }


def main() -> int:
    print("=" * 80)
    print("H1.5 SINGLE-TOPIC FALLBACK DIAGNOSTIC")
    print("Plan v3 risks register: if BothHigh × Post is null, try each topic alone")
    print("=" * 80)

    panel = load_h1_panel()
    uncres = load_uncres()
    panel = panel.merge(uncres, on="file_name", how="left")
    print(f"  H1 panel + UncResCEO: {len(panel):,} rows")

    # Single-topic firm labels
    labels = build_single_topic_labels(panel)
    n_high_trade = int((labels["HighTrade"] == 1).sum())
    n_high_tax = int((labels["HighTax"] == 1).sum())
    print(
        f"  Firm labels: HighTrade={n_high_trade}/{len(labels)}, "
        f"HighTax={n_high_tax}/{len(labels)}"
    )

    # Merge labels per gvkey
    panel = panel.merge(labels[["gvkey", "HighTrade", "HighTax"]], on="gvkey", how="left")

    # Post + interactions
    panel["Post_trump"] = (panel["cal_yr_qtr"] >= POST_THRESH).astype(float)
    panel["DiD_trade"] = panel["HighTrade"] * panel["Post_trump"]
    panel["DiD_tax"] = panel["HighTax"] * panel["Post_trump"]

    # Sample window + Main filter
    panel = panel[panel["cal_yr_qtr"].between(20143, 20184)].copy()
    panel = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  After sample window + Main: {len(panel):,}")

    # Center UncResCEO on Main
    mu = float(panel["UncResCEO"].dropna().mean())
    panel["UncResCEO_c"] = panel["UncResCEO"] - mu

    # Speech lag
    panel = attach_speech_lag(panel)

    # Drop firms missing single-topic labels
    panel_t = panel[panel["HighTrade"].notna()].copy()
    panel_x = panel[panel["HighTax"].notna()].copy()
    print(f"  Trade-eligible: {len(panel_t):,}; Tax-eligible: {len(panel_x):,}")

    fe_set = ["industry", "firm", "industry_yq", "firm_yq"]
    dv_set = ["CashRatio", "UncResCEO_c"]

    print("\n" + "=" * 80)
    print("HIGHTRADE × POST(2016q4) — single-topic, drop tax dimension")
    print("=" * 80)
    print("| col | dv          | fe          | beta     | se     | p_one  | n      | dir |")
    print("|-----|-------------|-------------|----------|--------|--------|--------|-----|")
    col = 0
    for dv in dv_set:
        for fe in fe_set:
            col += 1
            r = run_did(
                panel_t, dv=dv, key_iv="DiD_trade", level_dummy="HighTrade",
                fe=fe, controls=CONTROLS,
            )
            beta = r["beta"]; se = r["se"]; p_two = r["p_two"]
            if np.isnan(p_two) or np.isnan(beta):
                p_one = np.nan
            else:
                p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
            sign = "POS" if beta > 0 else ("NEG" if beta < 0 else "0")
            sig = "***" if p_one < 0.01 else ("**" if p_one < 0.05 else ("*" if p_one < 0.10 else "ns"))
            print(
                f"| {col}   | {dv:11s} | {fe:11s} | {beta:+.4f} | {se:.4f} | {p_one:.4f} "
                f"| {r['n']:>6,d} | {sign:<3s} {sig} |"
            )

    print("\n" + "=" * 80)
    print("HIGHTAX × POST(2016q4) — single-topic, drop trade dimension")
    print("=" * 80)
    print("| col | dv          | fe          | beta     | se     | p_one  | n      | dir |")
    print("|-----|-------------|-------------|----------|--------|--------|--------|-----|")
    col = 0
    for dv in dv_set:
        for fe in fe_set:
            col += 1
            r = run_did(
                panel_x, dv=dv, key_iv="DiD_tax", level_dummy="HighTax",
                fe=fe, controls=CONTROLS,
            )
            beta = r["beta"]; se = r["se"]; p_two = r["p_two"]
            if np.isnan(p_two) or np.isnan(beta):
                p_one = np.nan
            else:
                p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
            sign = "POS" if beta > 0 else ("NEG" if beta < 0 else "0")
            sig = "***" if p_one < 0.01 else ("**" if p_one < 0.05 else ("*" if p_one < 0.10 else "ns"))
            print(
                f"| {col}   | {dv:11s} | {fe:11s} | {beta:+.4f} | {se:.4f} | {p_one:.4f} "
                f"| {r['n']:>6,d} | {sign:<3s} {sig} |"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
