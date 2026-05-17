"""Confirm: NaN SE on DiD_BetaUK col 1 cash is caused by two-way clustering.
Re-run with one-way firm-cluster only and check if SE becomes finite.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "src")

from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.econometric.run_h1_5_brexit_did import (
    load_h1_panel, merge_uncresceo, load_compustat_raw,
    load_brexit_builders, assemble_panel,
    KEY_IV_BETA_UK, WINDOW_START_YQ, WINDOW_END_YQ,
    MACRO_CONTROLS, FIRM_CONTROLS_LAG1, EPS_CONTROL_LAG1,
)

root = Path.cwd()
panel, _ = load_h1_panel(root)
panel = merge_uncresceo(panel, root)
panel_brx = panel[(panel["cal_yr_qtr"] >= WINDOW_START_YQ - 1) & (panel["cal_yr_qtr"] <= WINDOW_END_YQ)]
gvkeys_keep = set(panel_brx["gvkey"].unique())
raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
builders = load_brexit_builders(root)
panel = assemble_panel(panel, raw_comp, builders)

dv = "cash_brexit_dv"
treatment = KEY_IV_BETA_UK
exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
df = panel.dropna(subset=[dv, treatment] + exog_cols).copy()
df = df[df["HIGH_BETA_UK"].isin([0.0, 1.0])]
df = df.dropna(subset=["ff12_code"])
df_idx = df.set_index(["gvkey", "cal_yr_qtr"])
exog_full = [treatment, "HIGH_BETA_UK"] + exog_cols

def fit_with(cov_kwargs, label):
    model = PanelOLS(
        dependent=df_idx[dv],
        exog=df_idx[exog_full],
        entity_effects=False, time_effects=False,
        other_effects=df_idx["ff12_code"],
        drop_absorbed=True, check_rank=False,
    )
    result = model.fit(cov_type="clustered", **cov_kwargs)
    print(f"\n--- {label} ---")
    for k in [treatment, "HIGH_BETA_UK", "Post_brexit", "usd_gbp_lag1", "vix_lag1", "ads_lag1", "ln_atq_lag1"]:
        if k in result.params.index:
            b = result.params[k]; se = result.std_errors[k]
            print(f"  {k:<25}: beta={b:+.6f} se={se if np.isnan(se) else f'{se:.6f}':>10}")

fit_with({"cluster_entity": True, "cluster_time": True}, "Two-way (firm + quarter) — current Brexit spec")
fit_with({"cluster_entity": True, "cluster_time": False}, "One-way (firm only)")
fit_with({"cluster_entity": False, "cluster_time": True}, "One-way (quarter only)")
fit_with({}, "Robust HC0 (no cluster)")
