#!/usr/bin/env python3
"""LINK-2 (raw, PRIMARY): direct effect of analyst cash-scrutiny on CEO evasiveness.

  UncResCEO ~ CashScrutiny + firm FE + time FE     (firm-clustered SE)

The direct test of the channel: when analysts spend more of the Q&A pressing on the
firm's cash, does the CEO get more evasive (residual uncertainty rises)? Story => beta > 0.
No interaction (that is a secondary concentration check, run separately).

Tests the RAW measure plus variants, each as the sole IV, FE-only and +controls.
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


def fe1(d, dv, iv, ctrl=False):
    rhs = [iv] + (CTRL if ctrl else [])
    dd = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[dv] + rhs).copy()
    nf = dd["gvkey"].nunique()
    dd = dd.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    b, se, p2 = float(m.params[iv]), float(m.std_errors[iv]), float(m.pvalues[iv])
    p1 = p2/2 if b > 0 else 1 - p2/2
    return b, se, p1, p2, int(m.nobs), nf


def main():
    score = pd.read_parquet(SCORE)
    panel = pd.read_parquet(_latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
                            columns=["file_name", "gvkey", "CashRatio", "start_date", "ff12_code"] + CTRL)
    resid = pd.read_parquet(_latest("outputs/econometric/ceo_clarity_extended/*/ceo_clarity_residual.parquet"),
                            columns=["file_name", "UncResCEO"])
    df = panel.merge(score, on="file_name", how="inner").merge(resid, on="file_name", how="inner")
    df = df[~df["ff12_code"].isin([8, 11])]
    df = df.dropna(subset=["stock_score", "UncResCEO", "gvkey"])
    df = df[df["n_qa_turns"] >= MIN_QA].copy()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df.dropna(subset=["start_date"])
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cq"] = df["start_date"].dt.year * 4 + (df["start_date"].dt.quarter - 1)

    # ---- variants of the cash-scrutiny measure ----
    s = df["stock_score"]
    df["sc_share_pct"] = s * 100.0                                   # raw measure (% of analyst Q&A turns)
    df["sc_any"]       = (df["n_qa_stock_turns"] >= 1).astype(float) # extensive margin: any cash turn
    df["sc_count"]     = df["n_qa_stock_turns"].astype(float)        # raw count of cash turns
    df["sc_logcount"]  = np.log1p(df["n_qa_stock_turns"])            # log(1+count)
    df["sc_z"]         = (s - s.mean()) / s.std()                    # standardized share

    print(f"LINK-2 raw sample: N={len(df):,} calls | firms={df['gvkey'].nunique():,} | quarters={df['cq'].nunique()}")
    print(f"  UncResCEO mean {df['UncResCEO'].mean():+.4f} sd {df['UncResCEO'].std():.4f}")
    print(f"  any-cash share {df['sc_any'].mean():.3f} | mean count {df['sc_count'].mean():.3f} | "
          f"share_pct mean {df['sc_share_pct'].mean():.3f}")

    variants = [("sc_share_pct", "share % (raw)"), ("sc_z", "share z-score"),
                ("sc_any", "1[>=1 cash turn]"), ("sc_count", "count cash turns"),
                ("sc_logcount", "log(1+count)")]

    print("\n  DV = UncResCEO   (one-tailed p1, H: beta > 0 = more scrutiny -> more evasion)")
    print(f"  {'variant':18s} {'model':9s} {'beta':>10s} {'se':>9s} {'p1':>7s} {'p2':>7s}  sig")
    for col, lbl in variants:
        for ctrl, mlbl in [(False, "FE"), (True, "FE+ctrl")]:
            b, se, p1, p2, n, nf = fe1(df, "UncResCEO", col, ctrl)
            star = "***" if p2 < .01 else "**" if p2 < .05 else "*" if p2 < .10 else ""
            print(f"  {lbl:18s} {mlbl:9s} {b:+10.5f} {se:9.5f} {p1:7.4f} {p2:7.4f}  {star}")


if __name__ == "__main__":
    main()
