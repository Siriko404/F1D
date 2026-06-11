#!/usr/bin/env python3
"""Coefficient-difference (Wald) tests on the H1 3-IV decomposition (Table 1).

Advisor flag: "a difference in significance is not a significant difference."
Clarity/UncRes/UncPre all sit in the SAME regression, so whether they DIFFER is
directly testable. For each contemporaneous base-control spec (col 1 industry FE,
col 2 firm FE) compute, from the fitted parameter covariance:

    diff = b_i - b_j
    Var(diff) = V_ii + V_jj - 2 V_ij
    t = diff / sqrt(Var(diff)),  p_two = 2*Phi(-|t|)

for the three pairs (UncRes vs UncPre, UncRes vs Clarity, Clarity vs UncPre).

Reuses run_h1_cash_holdings_ceo2iv_decomp's load/prepare/fit verbatim so the
single coefficients reproduce Table 1 exactly. No production file touched.
Run: python tmp/_h1_decomp_coefdiff_wald.py
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location(
    "h1d", ROOT / "src" / "f1d" / "econometric" / "run_h1_cash_holdings_ceo2iv_decomp.py")
h1d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h1d)

PAIRS = [("UncResCEO", "UncPreCEO"), ("UncResCEO", "ClarityCEO"),
         ("ClarityCEO", "UncPreCEO")]


def stars(p): return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else "ns"


def run_spec(panel, spec):
    df = h1d.prepare_regression_data(panel, spec)
    time_col = "cal_yr_qtr" if spec["fe"].endswith("_yq") else "cal_yr"
    base_fe = spec["fe"].replace("_yq", "")
    controls = h1d.BASE_CONTROLS if spec["controls"] == "base" else h1d.EXTENDED_CONTROLS
    exog = h1d.KEY_IVS + controls
    dfp = df.set_index(["gvkey", time_col])
    m = h1d._fit_one(dfp, spec["dv"], exog, base_fe)
    b, V = m.params, m.cov
    print(f"\n=== col {spec['col']}  DV={spec['dv']}  FE={spec['fe']}  N={int(m.nobs):,} ===")
    print("  single coefs (reproduce Table 1):")
    for iv in h1d.KEY_IVS:
        print(f"    {iv:11s} b={float(b[iv]):+.5f}  se={float(m.std_errors[iv]):.5f}")
    print("  PAIRWISE coefficient-difference (Wald), two-tailed:")
    for i, j in PAIRS:
        diff = float(b[i] - b[j])
        var = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j])
        se = var ** 0.5
        t = diff / se if se > 0 else float("nan")
        p = 2 * norm.sf(abs(t))
        print(f"    {i:11s} - {j:11s} = {diff:+.5f}  se={se:.5f}  t={t:+.2f}  "
              f"p={p:.4f} [{stars(p)}]")


def main():
    panel = h1d.load_panel(ROOT)
    panel = h1d.filter_main_sample(panel)
    specs = {s["col"]: s for s in h1d.MODEL_SPECS}
    for col in (1, 2, 3, 4):          # contemporaneous CashRatio specs
        run_spec(panel, specs[col])


if __name__ == "__main__":
    main()
