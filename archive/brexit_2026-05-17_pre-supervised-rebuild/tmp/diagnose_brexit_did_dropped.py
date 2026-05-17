"""Diagnose why DiD_BetaUK is silently dropped in Brexit cash industry-FE specs
(cols 1 + 3) but survives in speech industry-FE specs (cols 9 + 11).

Approach:
1. Rebuild the panel via the same builder pipeline the runner uses.
2. Re-run col 1 regression (cash, beta_uk, industry FE, year FE) and inspect
   what linearmodels' drop_absorbed dropped.
3. Compare with col 9 (speech, beta_uk, industry FE, year FE) — same FE, but
   sample differs (UncResCEO_c coverage).
4. Compute design-matrix rank manually to confirm what's collinear with what.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

# Replicate the runner's panel-assembly path. Instead of re-running from raw
# data (~minutes), read the latest h1_5_brexit_did panel — but the runner
# doesn't persist the assembled panel. So we'll re-invoke the runner's
# assembly fn directly.
sys.path.insert(0, "src")
from pathlib import Path
from f1d.econometric.run_h1_5_brexit_did import (
    load_h1_panel, merge_uncresceo, load_compustat_raw,
    load_brexit_builders, assemble_panel,
    KEY_IV_BETA_UK, KEY_IV_10K, WINDOW_START_YQ, WINDOW_END_YQ,
    MACRO_CONTROLS, FIRM_CONTROLS_LAG1, EPS_CONTROL_LAG1,
)

print("=" * 80)
print("REBUILDING PANEL (this calls all builders — may take 1-2 min)")
print("=" * 80)
root = Path.cwd()
panel, _ = load_h1_panel(root)
panel = merge_uncresceo(panel, root)
panel_brx = panel[(panel["cal_yr_qtr"] >= WINDOW_START_YQ - 1) & (panel["cal_yr_qtr"] <= WINDOW_END_YQ)]
gvkeys_keep = set(panel_brx["gvkey"].unique())
raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
builders = load_brexit_builders(root)
panel = assemble_panel(panel, raw_comp, builders)
print(f"Panel shape: {panel.shape}")

# Filter to beta_uk treated/control + cash sample.
exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]

print()
print("=" * 80)
print("COL 1: cash_brexit_dv ~ DiD_BetaUK + controls, industry FE + year FE")
print("=" * 80)

dv = "cash_brexit_dv"
treatment = KEY_IV_BETA_UK
df = panel.dropna(subset=[dv, treatment] + exog_cols).copy()
df = df[df["HIGH_BETA_UK"].isin([0.0, 1.0])]
df = df.dropna(subset=["ff12_code"])
print(f"Sample n = {len(df):,}")
print(f"DiD_BetaUK distribution: min={df[treatment].min()}, max={df[treatment].max()}, mean={df[treatment].mean():.4f}, std={df[treatment].std():.4f}")
print(f"HIGH_BETA_UK distribution: {df['HIGH_BETA_UK'].value_counts().to_dict()}")
print(f"Post_brexit distribution: {df['Post_brexit'].value_counts().to_dict()}")
print(f"Pre x treated: {((df['Post_brexit']==0) & (df['HIGH_BETA_UK']==1)).sum():,}")
print(f"Pre x control: {((df['Post_brexit']==0) & (df['HIGH_BETA_UK']==0)).sum():,}")
print(f"Post x treated: {((df['Post_brexit']==1) & (df['HIGH_BETA_UK']==1)).sum():,}")
print(f"Post x control: {((df['Post_brexit']==1) & (df['HIGH_BETA_UK']==0)).sum():,}")

exog_full = [treatment, "HIGH_BETA_UK"] + exog_cols
df_idx = df.set_index(["gvkey", "cal_yr_qtr"])

model = PanelOLS(
    dependent=df_idx[dv],
    exog=df_idx[exog_full],
    entity_effects=False,
    time_effects=False,  # col 1 = industry FE only via other_effects, NO time FE in PanelOLS — Year FE handled separately? Let's check the runner
    other_effects=df_idx["ff12_code"],
    drop_absorbed=True,
    check_rank=False,
)
result = model.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
print()
print(f"Exog requested: {exog_full}")
print(f"Params returned: {list(result.params.index)}")
dropped = set(exog_full) - set(result.params.index)
print(f"DROPPED by linearmodels: {dropped}")
print()
print("--- Now re-run WITHOUT drop_absorbed to see what linearmodels would have done ---")
try:
    model_nodrop = PanelOLS(
        dependent=df_idx[dv],
        exog=df_idx[exog_full],
        entity_effects=False,
        time_effects=False,
        other_effects=df_idx["ff12_code"],
        drop_absorbed=False,
        check_rank=True,
    )
    result_nodrop = model_nodrop.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    print(f"WITHOUT drop_absorbed: params = {list(result_nodrop.params.index)}")
    for k in exog_full:
        if k in result_nodrop.params.index:
            print(f"  {k:<25}: beta={result_nodrop.params[k]:+.6f} se={result_nodrop.std_errors[k]:.6f}")
except Exception as e:
    print(f"Without drop_absorbed failed: {type(e).__name__}: {e}")

print()
print("=" * 80)
print("MANUAL RANK CHECK — does DiD_BetaUK linearly depend on HIGH_BETA_UK + Post + FF12 + Year?")
print("=" * 80)
# Build a small design matrix: [DiD_BetaUK, HIGH_BETA_UK, Post_brexit, FF12 dummies]
# and check if DiD_BetaUK is in the span of the others.
ff12_dummies = pd.get_dummies(df["ff12_code"].astype(str), prefix="ff12", drop_first=True, dtype=float)
print(f"FF12 unique: {df['ff12_code'].nunique()}")

# Regress DiD_BetaUK on [HIGH_BETA_UK, Post_brexit, FF12_dummies] — if R^2 = 1, it's perfectly collinear.
import statsmodels.api as sm
X = pd.concat([
    df["HIGH_BETA_UK"].rename("HIGH_BETA_UK").reset_index(drop=True),
    df["Post_brexit"].rename("Post_brexit").reset_index(drop=True),
    ff12_dummies.reset_index(drop=True),
], axis=1)
X = sm.add_constant(X)
y = df[treatment].reset_index(drop=True)
ols = sm.OLS(y.astype(float), X.astype(float)).fit()
print(f"R^2 of DiD_BetaUK ~ HIGH_BETA_UK + Post + FF12_dummies: {ols.rsquared:.6f}")
print(f"If R^2 ≈ 1, DiD_BetaUK is collinear with HIGH_BETA_UK + Post + FF12 — drop_absorbed will drop it.")

# Same with [HIGH_BETA_UK, Post_brexit, FF12 x Year cross-product] — but col 1 doesn't have year FE in PanelOLS,
# year is one of the exog controls if any. Let's check what runner does for fe='industry'.
# Per _fit_one: fe='industry' → time_effects=False, other_effects=ff12_code only. NO year FE in regressor.

print()
print("=" * 80)
print("COL 9: UncResCEO_c ~ DiD_BetaUK + controls, industry FE (SAME spec, smaller sample)")
print("=" * 80)
dv2 = "UncResCEO_c"
df2 = panel.dropna(subset=[dv2, treatment] + exog_cols).copy()
df2 = df2[df2["HIGH_BETA_UK"].isin([0.0, 1.0])]
df2 = df2.dropna(subset=["ff12_code"])
print(f"Sample n = {len(df2):,}")
df2_idx = df2.set_index(["gvkey", "cal_yr_qtr"])
model2 = PanelOLS(
    dependent=df2_idx[dv2],
    exog=df2_idx[exog_full],
    entity_effects=False,
    time_effects=False,
    other_effects=df2_idx["ff12_code"],
    drop_absorbed=True,
    check_rank=False,
)
result2 = model2.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
print(f"Params returned: {list(result2.params.index)}")
dropped2 = set(exog_full) - set(result2.params.index)
print(f"DROPPED: {dropped2}")
