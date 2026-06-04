#!/usr/bin/env python3
"""LINK-2 (logit): binarized CEO evasiveness ~ analyst cash-scrutiny.

Binarize UncResCEO at several thresholds (high-uncertainty = a 'dodge' flag) and run a
LOGIT of each binary on each cash-scrutiny variant. Grid: DV cutoff x IV form, no-ctrl and
+ctrl. Reports the IV coefficient (log-odds), clustered p, and significance.

FE: industry (ff12) + calendar year-quarter dummies (firm-FE logit is biased by the
incidental-parameters problem). SE clustered by firm via GLM-Binomial cluster cov.
=> cross-firm identification (weaker than the within-firm LPM); the right tool for a binary DV.
"""
from __future__ import annotations
import glob
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
SCORE = ROOT / "tmp" / "_cash_stock_score_call.parquet"
CTRL = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO"]
MIN_QA = 3


def _latest(p):
    h = sorted(glob.glob(str(ROOT / p)))
    if not h: raise FileNotFoundError(p)
    return h[-1]


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
    df = df.dropna(subset=["start_date"]).reset_index(drop=True)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cyq"] = df["start_date"].dt.year.astype(str) + "Q" + df["start_date"].dt.quarter.astype(str)

    # winsorize + standardize continuous controls so the +ctrl logit IRLS converges
    for c in CTRL:
        lo, hi = df[c].quantile([.01, .99])
        df[c] = df[c].clip(lo, hi)
        sd = df[c].std()
        if sd and sd > 0:
            df[c] = (df[c] - df[c].mean()) / sd

    # IV variants
    s = df["stock_score"]
    df["sc_share_pct"] = s * 100.0
    df["sc_any"] = (df["n_qa_stock_turns"] >= 1).astype(float)
    df["sc_count"] = df["n_qa_stock_turns"].astype(float)
    df["sc_logcount"] = np.log1p(df["n_qa_stock_turns"])

    # DV binaries from UncResCEO
    u = df["UncResCEO"]
    dvs = {
        "1[UncRes>0]":   (u > 0).astype(int),
        "1[>=median]":   (u >= u.median()).astype(int),
        "1[top tercile]":(u >= u.quantile(2/3)).astype(int),
        "1[top quart.]": (u >= u.quantile(0.75)).astype(int),
        "1[top decile]": (u >= u.quantile(0.90)).astype(int),
    }
    ivs = [("sc_share_pct", "share %"), ("sc_any", "any cash turn"),
           ("sc_count", "count"), ("sc_logcount", "log(1+cnt)")]

    # FE dummy block (industry + calendar quarter), built once
    FE = pd.concat([pd.get_dummies(df["ff12_code"].astype("Int64").astype(str), prefix="ind", drop_first=True),
                    pd.get_dummies(df["cyq"], prefix="q", drop_first=True)], axis=1).astype(float)

    print(f"LINK-2 logit sample: N={len(df):,} | firms={df['gvkey'].nunique():,} | "
          f"quarters={df['cyq'].nunique()} | industries={df['ff12_code'].nunique()}")
    print("base rates:", {k: round(float(v.mean()), 3) for k, v in dvs.items()})
    g = df["gvkey"].values

    def fit(y, ivcol, with_ctrl):
        cols = [df[[ivcol]].rename(columns={ivcol: "IV"})]
        if with_ctrl:
            cols.append(df[CTRL])
        cols.append(FE)
        X = pd.concat(cols, axis=1)
        X = sm.add_constant(X, has_constant="add")
        keep = X.notna().all(axis=1)
        Xk, yk, gk = X[keep], y[keep], g[keep]
        Xk = Xk.loc[:, (Xk != 0).any(axis=0)]                  # drop all-zero dummy cols
        try:
            res = sm.GLM(yk, Xk, family=sm.families.Binomial()).fit(
                cov_type="cluster", cov_kwds={"groups": gk})
            b = res.params["IV"]; p = res.pvalues["IV"]
            return b, p
        except Exception as e:
            return float("nan"), float("nan")

    for with_ctrl in (False, True):
        tag = "+ctrl" if with_ctrl else "FE only"
        print(f"\n===== LOGIT log-odds of IV  ({tag}; ind+quarter FE; firm-clustered) =====")
        print(f"  {'DV \\ IV':16s}" + "".join(f"{lbl:>16s}" for _, lbl in ivs))
        for dvname, y in dvs.items():
            row = f"  {dvname:16s}"
            for ivcol, _ in ivs:
                b, p = fit(y, ivcol, with_ctrl)
                star = "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
                row += (f"{b:+.4f} p{p:.2f}{star}").rjust(16)
            print(row)
    print("\n(one-sided story: IV>0 = more cash-scrutiny -> higher chance of a high-uncertainty 'dodge'.)")


if __name__ == "__main__":
    main()
