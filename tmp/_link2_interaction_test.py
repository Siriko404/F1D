#!/usr/bin/env python3
"""EXPLORATION (not production): Link-2 reason-gating interaction test.

Question (Sina's framing): analyst cash-scrutiny alone is inert on CEO residual
uncertainty (the channel null, Table 17). But does scrutiny predict uncertainty
WHEN there is a real cash situation to be uncertain about? i.e. is the residual
uncertainty REASON-gated?

Operationalization 1 (Jensen interaction, matches the original Link-2 design):
    UncResCEO ~ CashScrutiny + HighCash + CashScrutiny x HighCash + firm FE + cal-qtr FE
    HighCash = 1[CashRatio >= top tercile]  (same def as the Link-1 validity table).
    Interaction > 0 while main ~ 0  =>  scrutiny bites only when cash is high.

Reuses the EXACT build_df() wiring from the production channel generator (same
sample, filters, FE, winsor/standardize) and only appends CashRatio -> HighCash
and the interaction. No production file touched.

Run:  python tmp/_link2_interaction_test.py
"""
from __future__ import annotations
import sys, glob, warnings
from pathlib import Path
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gen_cash_scrutiny_channel_table import build_df, _latest   # exact same wiring


def panel_fit(d, dv, rhs):
    nf = d["gvkey"].nunique()
    dd = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[dv] + rhs).copy()
    nf2 = dd["gvkey"].nunique()
    dd = dd.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    out = {}
    for v in rhs:
        if v in m.params.index:
            out[v] = (float(m.params[v]), float(m.std_errors[v]), float(m.pvalues[v]))
    return out, int(m.nobs), nf2


def stars(p): return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else "ns"


def show(title, res, n, nf):
    print(f"\n=== {title}  (N={n:,}, firms={nf:,}) ===")
    for v, (b, se, p) in res.items():
        # one-tailed p for the directional Jensen prediction (beta>0)
        p1 = p / 2 if b > 0 else 1 - p / 2
        print(f"  {v:28s} b={b:+.5f}  se={se:.5f}  p2={p:.4f} [{stars(p)}]  p1={p1:.4f} [{stars(p1)}]")


def main():
    df = build_df()
    # append raw CashRatio from the same h1 panel build_df() used, by file_name
    panel = pd.read_parquet(
        _latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
        columns=["file_name", "CashRatio"])
    df = df.merge(panel, on="file_name", how="left")
    n0 = len(df); df = df.dropna(subset=["CashRatio"]).copy()
    print(f"build_df N={n0:,} | with CashRatio N={len(df):,} | firms={df['gvkey'].nunique():,}")

    # HighCash = top tercile of CashRatio (pooled), matching the Link-1 validity table def
    q67 = df["CashRatio"].quantile(2.0 / 3.0)
    df["HighCash"] = (df["CashRatio"] >= q67).astype(float)
    df["Scr_x_High"] = df["CashScrutiny"] * df["HighCash"]
    print(f"HighCash base-rate={df['HighCash'].mean():.3f} (cut@CashRatio>={q67:.4f}); "
          f"CashScrutiny mean={df['CashScrutiny'].mean():.3f} median={df['CashScrutiny'].median():.3f}")

    rhs = ["CashScrutiny", "HighCash", "Scr_x_High"]
    for dv in ["UncResCEO", "UncAnsCEO"]:
        res, n, nf = panel_fit(df, dv, rhs)
        show(f"{dv} ~ CashScrutiny x HighCash (firm + cal-qtr FE, firm-clustered)", res, n, nf)

    # also report scrutiny effect within the HighCash subsample only (interpretability)
    hi = df[df["HighCash"] == 1].copy()
    res, n, nf = panel_fit(hi, "UncResCEO", ["CashScrutiny"])
    show("UncResCEO ~ CashScrutiny  | HighCash==1 subsample only", res, n, nf)
    lo = df[df["HighCash"] == 0].copy()
    res, n, nf = panel_fit(lo, "UncResCEO", ["CashScrutiny"])
    show("UncResCEO ~ CashScrutiny  | HighCash==0 subsample only", res, n, nf)


if __name__ == "__main__":
    main()
