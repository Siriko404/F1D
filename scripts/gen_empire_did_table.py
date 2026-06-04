#!/usr/bin/env python3
"""Generate the Empire-Building pre-acquisition run-up table fragment.

Reverse-causality probe for the UncResCEO -> Cash finding. Treatment = call-firms
in the SINGLE quarter BEFORE they announce a >=50%-cash acquisition (SDC, US public
acquirers, 2002-2018, payment method known). Two outcomes, same pre-announce quarter:
  (1) CashRatio   -> do they hold more cash the quarter before the deal? (first stage)
  (2) UncResCEO   -> does CEO Q&A uncertainty rise that same quarter? (the probe)

STOCK-ACQUIRER PLACEBO (cols 3-4): the t-1 uncertainty rise could be a confound --
before any secret deal the CEO is under a legal gag (MNPI/Reg FD) and sounds evasive
regardless of cash. Stock-financed acquirers (>=50% STOCK) have the SAME pending-deal
gag but NO cash war-chest. So if uncertainty rises for stock acquirers too, the rise
is deal-secrecy not cash; if it is flat for stock but present for cash, the dodging is
cash-specific. The placebo runs the identical spec with ps>=50 instead of pc>=50.

NOTE ON METHOD: a two-way fixed-effects OLS (firm FE + calendar-year-quarter FE,
firm-clustered SE) of a continuous outcome on a single binary "quarter before
announcement" indicator (e == -1). Post-announcement quarters (e >= 0) are DROPPED
from the sample by design -- we observe only the run-up, never the aftermath. So the
PreAnnounceQtr coefficient is a pre-event (anticipation) effect, identified off the treated
firm's pre-announcement quarter vs its earlier normal quarters and vs non-acquiring
firms. Controls/FE mirror the H1 cash suite (Lagged_DV dropped).

Writes:
  outputs/econometric/empire_building_did/<ts>/summary.json   (numbers)
  docs/Draft/_empire_building_did.tex                          (thesis fragment)

Regenerate: python scripts/gen_empire_did_table.py
NOT hand-edited -- table cells come from this script's regression output.
"""
from __future__ import annotations
import glob
import json
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
CTRL = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO"]  # base minus Lagged_DV
PRE_LAGS = (-1, -1)  # treatment = the single quarter before announcement (e == -1)
DVS = ["CashRatio", "UncResCEO"]
TEX_OUT = ROOT / "docs" / "Draft" / "_empire_building_did.tex"


def _latest(pattern: str) -> str:
    hits = sorted(glob.glob(str(ROOT / pattern)))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[-1]


def base_panel() -> pd.DataFrame:
    p = pd.read_parquet(
        _latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
        columns=["file_name", "start_date", "gvkey", "CashRatio"] + CTRL,
    )
    res = pd.read_parquet(
        _latest("outputs/econometric/ceo_clarity_extended/*/ceo_clarity_residual.parquet"),
        columns=["file_name", "UncResCEO"],
    )
    p = p.merge(res, on="file_name", how="left")
    p["gvkey"] = p["gvkey"].astype(str).str.zfill(6)
    p["start_date"] = pd.to_datetime(p["start_date"])
    p["cq"] = p["start_date"].dt.year * 4 + (p["start_date"].dt.quarter - 1)
    return p


def sdc() -> pd.DataFrame:
    s = pd.read_parquet(
        ROOT / "inputs" / "SDC" / "sdc-ma-merged.parquet",
        columns=["Acquiror 6-digit CUSIP", "Acquiror Nation", "Acquiror Public Status",
                 "Date Announced", "Deal Status", "Percentage of Cash", "Percentage of Stock"],
    ).rename(columns={"Acquiror 6-digit CUSIP": "c6", "Percentage of Cash": "pc", "Percentage of Stock": "ps"})
    s["da"] = pd.to_datetime(s["Date Announced"], errors="coerce")
    yr = s["da"].dt.year
    s["known"] = ((yr >= 2002) & (yr <= 2018)
                  & (s["Acquiror Nation"] == "United States")
                  & (s["Acquiror Public Status"] == "Public")
                  & (s["Deal Status"].isin(["Completed", "Pending", "Withdrawn"]))
                  & (s["pc"].notna() | s["ps"].notna()))
    return s


def manifest() -> pd.DataFrame:
    m = pd.read_parquet(
        _latest("outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"),
        columns=["gvkey", "cusip"],
    )
    m["gvkey"] = m["gvkey"].astype(str).str.zfill(6)
    m["c6"] = m["cusip"].astype(str).str[:6]
    return m[["gvkey", "c6"]].drop_duplicates("gvkey")


def build(p: pd.DataFrame, s: pd.DataFrame, m: pd.DataFrame, mask: pd.Series) -> tuple[pd.DataFrame, int]:
    """Build the t-1 panel for the acquirer set selected by `mask` (payment filter)."""
    cd = s[s["known"] & mask].copy()
    cd["dq"] = cd["da"].dt.year * 4 + (cd["da"].dt.quarter - 1)
    first = cd.sort_values("da").groupby("c6", as_index=False)["dq"].first()
    treat = m.merge(first, on="c6", how="inner")[["gvkey", "dq"]].drop_duplicates("gvkey")

    q = p.merge(treat, on="gvkey", how="left")
    q["e"] = q["cq"] - q["dq"]
    # Drop post-announcement quarters for treated firms (e >= 0): we observe ONLY
    # the run-up, never the aftermath. NaN e = never-acquirers (controls) -> kept.
    q = q[q["e"].isna() | (q["e"] < 0)].copy()
    q["PreAnnounceQtr"] = ((q["e"] >= PRE_LAGS[0]) & (q["e"] <= PRE_LAGS[1])).astype(float)
    return q, treat["gvkey"].nunique()


def run(q: pd.DataFrame, dv: str) -> dict:
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=[dv, "PreAnnounceQtr"] + CTRL).copy()
    n_firms = int(d["gvkey"].nunique())
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + PreAnnounceQtr + " + " + ".join(CTRL) + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    par, se, pv = mod.params, mod.std_errors, mod.pvalues
    b, s_, p2 = float(par["PreAnnounceQtr"]), float(se["PreAnnounceQtr"]), float(pv["PreAnnounceQtr"])
    p1 = p2 / 2 if b > 0 else 1 - p2 / 2  # one-tailed, H: PreAnnounceQtr > 0
    ctrls = {c: {"beta": float(par[c]), "se": float(se[c]), "p2": float(pv[c])}
             for c in CTRL if c in par.index}
    return {"dv": dv, "beta": b, "se": s_, "p1": p1, "p2": p2,
            "ctrls": ctrls, "n": int(mod.nobs), "n_firms": n_firms, "r2": float(mod.rsquared)}


def stars(p: float) -> str:
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))


def cell(coef: float, p: float) -> str:
    s = stars(p)
    body = f"{coef:.4f}"
    return (f"\\textbf{{{body}}}$^{{{s}}}$" if s else body)


def write_tex(res: dict, counts: dict) -> None:
    # column order: (arm, dv)
    cols = [("cash", "CashRatio"), ("cash", "UncResCEO"),
            ("stock", "CashRatio"), ("stock", "UncResCEO")]
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Empire-Building Run-Up Test}",
        r"\label{tab:empire_building_did}",
        r"\scriptsize",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r" & \multicolumn{2}{c}{Cash acquirers} & \multicolumn{2}{c}{Stock acquirers (placebo)} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
        r" & (1) & (2) & (3) & (4) \\",
        r" & CashRatio & UncResCEO & CashRatio & UncResCEO \\",
        r"\midrule",
        "PreAnnounceQtr & "
        + " & ".join(cell(res[k]["beta"], res[k]["p1"]) for k in cols) + r" \\",
        " & " + " & ".join(f"({res[k]['se']:.4f})" for k in cols) + r" \\",
        r"\midrule",
    ]
    for c in CTRL:
        lines.append(f"{c} & "
                     + " & ".join(cell(res[k]["ctrls"][c]["beta"], res[k]["ctrls"][c]["p2"]) for k in cols)
                     + r" \\")
        lines.append(" & " + " & ".join(f"({res[k]['ctrls'][c]['se']:.4f})" for k in cols) + r" \\")
    lines += [
        r"\midrule",
        r"Firm FE & Yes & Yes & Yes & Yes \\",
        r"Cal. Year-Quarter FE & Yes & Yes & Yes & Yes \\",
        r"\midrule",
        "Firms & " + " & ".join(f"{res[k]['n_firms']:,}" for k in cols) + r" \\",
        "N (firm-quarters) & " + " & ".join(f"{res[k]['n']:,}" for k in cols) + r" \\",
        "$R^2$ & " + " & ".join(f"{res[k]['r2']:.3f}" for k in cols) + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for the treatment coefficient, $\beta > 0$; two-tailed for controls). ",
        r"Significant coefficients in \textbf{bold}. Standard errors (in parentheses) clustered at firm level.",
        r"\end{minipage}",
        r"\end{table}",
    ]
    TEX_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p, s, m = base_panel(), sdc(), manifest()
    arms = {"cash": s["pc"] >= 50, "stock": s["ps"] >= 50}
    res, counts = {}, {}
    for arm, mask in arms.items():
        q, n = build(p, s, m, mask)
        counts[arm] = n
        for dv in DVS:
            res[(arm, dv)] = run(q, dv)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / "empire_building_did" / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"pre_window_lags": PRE_LAGS, "controls": CTRL, "counts": counts,
               "results": {f"{a}:{d}": res[(a, d)] for (a, d) in res}, "timestamp": ts}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_tex(res, counts)

    print(f"cash acquirers: {counts['cash']:,} | stock acquirers: {counts['stock']:,}")
    for (a, d), r in res.items():
        print(f"  {a:5} {d:10} beta={r['beta']:+.5f} se={r['se']:.5f} p1={r['p1']:.3f} p2={r['p2']:.3f} N={r['n']:,}")
    print(f"wrote {out/'summary.json'}")
    print(f"wrote {TEX_OUT}")


if __name__ == "__main__":
    main()
