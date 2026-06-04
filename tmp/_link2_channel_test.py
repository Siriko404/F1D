#!/usr/bin/env python3
"""LINK-2: the analyst-scrutiny channel test (diagnostic, audit-before-table).

  UncResCEO ~ CashScrutiny x HighCash + CashScrutiny + HighCash + firm FE + time FE

Story (Jensen + Hollander): when a firm holds idle cash AND analysts press it on cash,
the CEO turns evasive -> CEO Q&A residual uncertainty rises. So the INTERACTION
(CashScrutiny x HighCash) is the PRIMARY prediction (> 0). The CashScrutiny main effect
is NOT robust (UncResCEO is already residualized on UncQue analyst tone -> see pre-cell a).

DV is the EXISTING UncResCEO (DWZ recipe untouched). New regressor = CashScrutiny =
analyst cash-topic attention (STOCK score, % of analyst Q&A turns). HighCash = top-tercile
CashRatio dummy.

Pre-cells (advisor-locked, run FIRST):
  (a) corr(CashScrutiny, UncQue) on the Link-2 sample -> how readable is a null.
  (b) re-print Gate-1 (CashScrutiny ~ CashRatio) on this CEO>=5 sample -> validity transfers?
"""
from __future__ import annotations
import glob
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
SCORE = ROOT / "tmp" / "_cash_stock_score_call.parquet"
CTRL = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO"]
MIN_QA = 3


def _latest(p):
    h = sorted(glob.glob(str(ROOT / p)))
    if not h: raise FileNotFoundError(p)
    return h[-1]


def fe_ols(d, dv, rhs, label):
    dd = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[dv] + rhs).copy()
    nf = dd["gvkey"].nunique()
    dd = dd.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    print(f"\n[{label}]  N={int(m.nobs):,}  firms={nf:,}")
    for v in rhs:
        if v not in m.params.index:
            print(f"    {v:22s} (absorbed)"); continue
        b, se, p2 = float(m.params[v]), float(m.std_errors[v]), float(m.pvalues[v])
        p1 = p2/2 if b > 0 else 1 - p2/2
        star = "***" if p2 < .01 else "**" if p2 < .05 else "*" if p2 < .10 else ""
        print(f"    {v:22s} beta={b:+.5f}  se={se:.5f}  p2={p2:.4f}  p1={p1:.4f} {star}")
    return m


def main():
    score = pd.read_parquet(SCORE)  # file_name, stock_score, n_qa_turns
    panel = pd.read_parquet(_latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
                            columns=["file_name", "gvkey", "CashRatio", "start_date", "ff12_code", "UncQue"] + CTRL)
    resid = pd.read_parquet(_latest("outputs/econometric/ceo_clarity_extended/*/ceo_clarity_residual.parquet"),
                            columns=["file_name", "UncResCEO"])

    df = panel.merge(score, on="file_name", how="inner").merge(resid, on="file_name", how="inner")
    df = df[~df["ff12_code"].isin([8, 11])]                      # main sample
    df = df.dropna(subset=["CashRatio", "stock_score", "UncResCEO", "gvkey"])
    df = df[df["n_qa_turns"] >= MIN_QA].copy()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df.dropna(subset=["start_date"])
    lo, hi = df["CashRatio"].quantile([.01, .99]); df["CashRatio"] = df["CashRatio"].clip(lo, hi)
    df["HighCash"] = (df["CashRatio"] >= df["CashRatio"].quantile(2/3)).astype(float)
    df["CashScrutiny"] = df["stock_score"] * 100.0               # percent of analyst Q&A turns
    df["CashxHigh"] = df["CashScrutiny"] * df["HighCash"]
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cq"] = df["start_date"].dt.year * 4 + (df["start_date"].dt.quarter - 1)

    print(f"LINK-2 sample: N={len(df):,} calls | firms={df['gvkey'].nunique():,} | "
          f"quarters={df['cq'].nunique()} | MIN_QA={MIN_QA}")
    print(f"  UncResCEO mean {df['UncResCEO'].mean():+.4f} sd {df['UncResCEO'].std():.4f}")
    print(f"  CashScrutiny mean {df['CashScrutiny'].mean():.4f} | HighCash share {df['HighCash'].mean():.3f}")

    # ---- pre-cell (a): corr(CashScrutiny, UncQue) ----
    r = df[["CashScrutiny", "UncQue"]].corr().iloc[0, 1]
    print(f"\n[PRE-a] corr(CashScrutiny, UncQue) = {r:+.3f}  "
          + ("(|r|<0.1: main-effect partialling minor -> a null IS meaningful)" if abs(r) < 0.1
             else "(|r| sizable: UncQue partialling MECHANICALLY suppresses the CashScrutiny MAIN effect; "
                  "interaction unaffected -> read the interaction, not the main effect)"))

    # ---- pre-cell (b): Gate-1 validity on THIS sample ----
    fe_ols(df, "CashScrutiny", ["CashRatio"], "PRE-b  validity transfer (CashScrutiny ~ CashRatio)")

    # ---- LINK-2 primary: interaction, no controls ----
    fe_ols(df, "UncResCEO", ["CashScrutiny", "HighCash", "CashxHigh"], "LINK-2 M1  interaction (no controls)")

    # ---- LINK-2 robustness: + controls ----
    fe_ols(df, "UncResCEO", ["CashScrutiny", "HighCash", "CashxHigh"] + CTRL, "LINK-2 M2  interaction (+controls)")

    print("\nNOTE: PRIMARY test = CashxHigh (interaction), one-tailed p1, H: > 0 (Jensen evasion "
          "concentrated where idle cash high). Main CashScrutiny effect is secondary (UncQue-partialled).")


if __name__ == "__main__":
    main()
