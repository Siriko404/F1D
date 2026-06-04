#!/usr/bin/env python3
"""Link-1 + Link-2 restricted to the EMPIRE-BUILDING universe (cash-acquirer firms).

Empire universe = gvkeys that announce a >=50%-cash acquisition (SDC, US public, 2002-2018,
payment known) -- the firms that actually hoard cash for deals. Construction mirrors
scripts/gen_empire_did_table.py exactly. Question: does the analyst cash-scrutiny channel
(Link-1 validity, Link-2 dodge) hold inside this universe, and does it SHARPEN in the
pre-announcement run-up (e<0), where the deal-secrecy story bites?
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
MIN_QA = 3


def _latest(p):
    h = sorted(glob.glob(str(ROOT / p)))
    if not h: raise FileNotFoundError(p)
    return h[-1]


def empire_acquirers():
    """Cash-acquirer gvkeys + first deal quarter dq. Mirrors gen_empire_did_table.py."""
    s = pd.read_parquet(ROOT / "inputs" / "SDC" / "sdc-ma-merged.parquet",
                        columns=["Acquiror 6-digit CUSIP", "Acquiror Nation", "Acquiror Public Status",
                                 "Date Announced", "Deal Status", "Percentage of Cash", "Percentage of Stock"]
                        ).rename(columns={"Acquiror 6-digit CUSIP": "c6", "Percentage of Cash": "pc",
                                          "Percentage of Stock": "ps"})
    s["da"] = pd.to_datetime(s["Date Announced"], errors="coerce")
    yr = s["da"].dt.year
    known = ((yr >= 2002) & (yr <= 2018) & (s["Acquiror Nation"] == "United States")
             & (s["Acquiror Public Status"] == "Public")
             & (s["Deal Status"].isin(["Completed", "Pending", "Withdrawn"]))
             & (s["pc"].notna() | s["ps"].notna()))
    cd = s[known & (s["pc"] >= 50)].copy()
    cd["dq"] = cd["da"].dt.year * 4 + (cd["da"].dt.quarter - 1)
    first = cd.sort_values("da").groupby("c6", as_index=False)["dq"].first()
    m = pd.read_parquet(_latest("outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"),
                        columns=["gvkey", "cusip"])
    m["gvkey"] = m["gvkey"].astype(str).str.zfill(6)
    m["c6"] = m["cusip"].astype(str).str[:6]
    treat = m.merge(first, on="c6", how="inner")[["gvkey", "dq"]].drop_duplicates("gvkey")
    return treat


def fe1(d, dv, iv, extra=None):
    rhs = [iv] + (extra or [])
    dd = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[dv] + rhs).copy()
    if dd["gvkey"].nunique() < 5 or len(dd) < 50:
        return None
    nf = dd["gvkey"].nunique()
    dd = dd.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(rhs) + " + EntityEffects + TimeEffects"
    try:
        m = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        return {"err": str(e)[:50]}
    b, se, p2 = float(m.params[iv]), float(m.std_errors[iv]), float(m.pvalues[iv])
    return {"b": b, "se": se, "p2": p2, "p1": p2/2 if b > 0 else 1-p2/2, "n": int(m.nobs), "nf": nf}


def row(tag, r):
    if r is None: print(f"  {tag:34s} (too few obs)"); return
    if "err" in r: print(f"  {tag:34s} ERR {r['err']}"); return
    star = "***" if r["p2"] < .01 else "**" if r["p2"] < .05 else "*" if r["p2"] < .10 else ""
    print(f"  {tag:34s} b={r['b']:+.5f} se={r['se']:.5f} p2={r['p2']:.4f} p1={r['p1']:.4f} N={r['n']:,} firms={r['nf']:,} {star}")


def run_block(df, name):
    print(f"\n===== {name}  (N={len(df):,}, firms={df['gvkey'].nunique():,}) =====")
    print(" LINK-1 validity:")
    row("CashAttn ~ CashRatio", fe1(df, "CashAttn", "CashRatio"))
    print(" LINK-2 direct (DV=UncResCEO):")
    for iv, lbl in [("sc_share_pct", "share%"), ("sc_any", "any-turn"),
                    ("sc_count", "count"), ("sc_logcount", "log(1+cnt)")]:
        row(f"UncResCEO ~ {lbl}", fe1(df, "UncResCEO", iv))
    print(" LINK-2 interaction:")
    row("UncResCEO ~ CashScrutiny x HighCash", fe1(df, "UncResCEO", "CashxHigh", extra=["CashScrutiny", "HighCash"]))


def main():
    score = pd.read_parquet(SCORE)
    panel = pd.read_parquet(_latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
                            columns=["file_name", "gvkey", "CashRatio", "start_date", "ff12_code"])
    resid = pd.read_parquet(_latest("outputs/econometric/ceo_clarity_extended/*/ceo_clarity_residual.parquet"),
                            columns=["file_name", "UncResCEO"])
    df = panel.merge(score, on="file_name", how="inner").merge(resid, on="file_name", how="left")
    df = df[~df["ff12_code"].isin([8, 11])]
    df = df.dropna(subset=["CashRatio", "stock_score", "gvkey"])
    df = df[df["n_qa_turns"] >= MIN_QA].copy()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df.dropna(subset=["start_date"])
    lo, hi = df["CashRatio"].quantile([.01, .99]); df["CashRatio"] = df["CashRatio"].clip(lo, hi)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cq"] = df["start_date"].dt.year * 4 + (df["start_date"].dt.quarter - 1)
    s = df["stock_score"]
    df["CashAttn"] = s * 100.0
    df["CashScrutiny"] = s * 100.0
    df["sc_share_pct"] = s * 100.0
    df["sc_any"] = (df["n_qa_stock_turns"] >= 1).astype(float)
    df["sc_count"] = df["n_qa_stock_turns"].astype(float)
    df["sc_logcount"] = np.log1p(df["n_qa_stock_turns"])

    treat = empire_acquirers()
    emp_gv = set(treat["gvkey"])
    dq = treat.set_index("gvkey")["dq"]
    print(f"empire cash-acquirer gvkeys: {len(emp_gv):,}")
    print(f"full channel sample firms: {df['gvkey'].nunique():,} | overlap with empire: "
          f"{df['gvkey'].isin(emp_gv).groupby(df['gvkey']).first().sum():,}")

    emp = df[df["gvkey"].isin(emp_gv)].copy()
    # HighCash tercile + interaction computed WITHIN the empire universe
    emp["HighCash"] = (emp["CashRatio"] >= emp["CashRatio"].quantile(2/3)).astype(float)
    emp["CashxHigh"] = emp["CashScrutiny"] * emp["HighCash"]
    emp["e"] = emp["cq"] - emp["gvkey"].map(dq)

    run_block(emp, "EMPIRE UNIVERSE (all calls of cash-acquirer firms)")
    runup = emp[emp["e"] < 0].copy()
    run_block(runup, "EMPIRE RUN-UP (pre-announcement quarters, e<0)")
    near = emp[(emp["e"] >= -8) & (emp["e"] < 0)].copy()
    run_block(near, "EMPIRE RUN-UP 8Q (e in [-8,-1])")


if __name__ == "__main__":
    main()
