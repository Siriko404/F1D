#!/usr/bin/env python3
"""FORMAL cash-specificity test for the empire run-up (Gate B).

The locked empire table (gen_empire_did_table.py) shows the t-1 UncResCEO rise for
CASH acquirers (significant) and STOCK acquirers (placebo, null) as TWO SEPARATE
regressions. 'Cash significant, stock not' is NOT a formal test that cash != stock
(Gelman-Stern). This pools both treatments in ONE model and runs the difference test.

Spec mirrors the locked empire build EXACTLY: CTRL (7, Lagged_DV dropped), single
pre-announce quarter (e==-1), post-announce quarters dropped, never-(either)-acquirers
as the FE baseline, two-way FE (firm + cal. year-qtr), firm-clustered SE.

  UncResCEO ~ PreAnn_cash + PreAnn_stock + CTRL + EntityEffects + TimeEffects

Formal cash-specificity = Wald on (PreAnn_cash - PreAnn_stock) > 0. Reuses the locked
module's base_panel/sdc/manifest so the inputs are identical. Read-only on inputs.

CAVEAT (honest): the cash run-up (PreAnn_cash) is robust; the difference's significance
rides on the imprecise, theory-unpredicted NEGATIVE stock estimate (small N) -- so the
formal cash-specificity is supported-but-fragile, not settled.

Writes:
  outputs/econometric/empire_cashspec/<ts>/summary.json   (numbers = the JSON spec)
  docs/Draft/_empire_cashspec.tex                         (thesis fragment, built FROM the json)

Run: python src/f1d/econometric/empire_cashspec_interaction.py
NOT hand-edited -- table cells come from this script's regression output.
"""
from __future__ import annotations
import importlib.util
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("_emp", ROOT / "scripts" / "gen_empire_did_table.py")
emp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(emp)
CTRL = emp.CTRL

SUITE = "empire_cashspec"
TEX_OUT = ROOT / "docs" / "Draft" / "_empire_cashspec.tex"


def first_dq(s: pd.DataFrame, m: pd.DataFrame, mask: pd.Series, col: str) -> pd.DataFrame:
    cd = s[s["known"] & mask].copy()
    cd["dq"] = cd["da"].dt.year * 4 + (cd["da"].dt.quarter - 1)
    first = cd.sort_values("da").groupby("c6", as_index=False)["dq"].first()
    t = m.merge(first, on="c6", how="inner")[["gvkey", "dq"]].drop_duplicates("gvkey")
    return t.rename(columns={"dq": col})


def build_pooled(p, s, m):
    tc = first_dq(s, m, s["pc"] >= 50, "dq_cash")
    tsk = first_dq(s, m, s["ps"] >= 50, "dq_stock")
    q = p.merge(tc, on="gvkey", how="left").merge(tsk, on="gvkey", how="left")
    # firm's first deal of EITHER type -> only keep the clean run-up + never-either firms
    q["dq_first"] = q[["dq_cash", "dq_stock"]].min(axis=1)
    keep = q["dq_first"].isna() | (q["cq"] < q["dq_first"])
    q = q[keep].copy()
    q["PreAnn_cash"] = (q["cq"] == q["dq_cash"] - 1).astype(float)
    q["PreAnn_stock"] = (q["cq"] == q["dq_stock"] - 1).astype(float)
    n_cash = int((q["PreAnn_cash"] == 1).sum())
    n_stock = int((q["PreAnn_stock"] == 1).sum())
    return q, n_cash, n_stock


def run(q, dv):
    need = ["UncResCEO", "CashRatio", "PreAnn_cash", "PreAnn_stock"] + CTRL  # shared sample: both DVs present
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + PreAnn_cash + PreAnn_stock + " + " + ".join(CTRL) \
        + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov

    def one(n):
        b, p2 = float(par[n]), float(pv[n])
        return {"b": b, "se": float(se[n]), "p1": p2 / 2 if b > 0 else 1 - p2 / 2, "p2": p2}

    i, j = "PreAnn_cash", "PreAnn_stock"
    diff = float(par[i] - par[j])
    var = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j])
    se_ = var ** 0.5
    t = diff / se_
    p2 = 2 * norm.sf(abs(t))
    wald = {"diff": diff, "se": se_, "t": t, "p1": p2 / 2 if diff > 0 else 1 - p2 / 2, "p2": p2}
    return {"cash": one(i), "stock": one(j), "wald": wald,
            "n": int(mod.nobs), "n_firms": int(d.reset_index()["gvkey"].nunique())}


def stars(p: float) -> str:
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))


def cell(coef: float, p: float) -> str:
    s = stars(p)
    return f"\\textbf{{{coef:.4f}}}$^{{{s}}}$" if s else f"{coef:.4f}"


def write_tex(summary_path: Path) -> None:
    """Build the LaTeX fragment FROM the written JSON spec."""
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    res = summary["results"]
    dvs = ["UncResCEO", "CashRatio"]
    # (json key, p-key, row label)
    rows = [("cash", "p1", r"Pre-announce qtr, Cash acquirer"),
            ("stock", "p1", r"Pre-announce qtr, Stock acquirer")]
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Formal Cash-Specificity of the Pre-Announcement Uncertainty Run-Up (cash vs.\ stock acquirers, pooled)}",
        r"\label{tab:empire_cashspec}",
        r"\scriptsize",
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r" & (1) UncResCEO & (2) CashRatio \\",
        r"\midrule",
    ]
    for jkey, pkey, lab in rows:
        coefs = " & ".join(cell(res[dv][jkey]["b"], res[dv][jkey][pkey]) for dv in dvs)
        ses = " & ".join(f"({res[dv][jkey]['se']:.4f})" for dv in dvs)
        lines.append(f"{lab} & {coefs} \\\\")
        lines.append(f" & {ses} \\\\")
    lines.append(r"\midrule")
    # the formal test row: cash - stock difference (two-tailed stars)
    dcoefs = " & ".join(cell(res[dv]["wald"]["diff"], res[dv]["wald"]["p2"]) for dv in dvs)
    dses = " & ".join(f"({res[dv]['wald']['se']:.4f})" for dv in dvs)
    lines.append(r"Cash $-$ Stock (formal test) & " + dcoefs + r" \\")
    lines.append(r" & " + dses + r" \\")
    lines += [
        r"\midrule",
        r"Firm FE / Year-Qtr FE / Controls & Yes & Yes \\",
        "N (firm-quarters) & " + " & ".join(f"{res[dv]['n']:,}" for dv in dvs) + r" \\",
        "Firms & " + " & ".join(f"{res[dv]['n_firms']:,}" for dv in dvs) + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize",
        r"\textit{Notes:} Two-way FE OLS (firm + calendar year-quarter), firm-clustered SE, with both "
        r"columns estimated on the \emph{identical} UncResCEO$\,\cap\,$CashRatio sample. Both "
        r"pre-announce dummies enter the SAME model; the omitted baseline is the firm's pre-deal and "
        r"never-acquirer quarters. \textbf{Pre-announce qtr} = the single quarter before the firm's "
        r"first $\geq$50\%-cash (resp.\ stock) acquisition. The \textbf{Cash $-$ Stock} row is the formal "
        r"cash-specificity test (Wald on the coefficient difference) the side-by-side placebo never ran. "
        r"$^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$; the two pre-announce rows one-tailed ($\beta>0$), the "
        r"Cash $-$ Stock row two-tailed. Standard errors in parentheses. For UncResCEO the cash run-up is "
        r"robust and the cash$-$stock difference is significant, but that significance rides on the "
        r"imprecise, theory-unpredicted negative stock estimate (small N$_{\text{stock}}$): read it as "
        r"supported-but-fragile, not settled. CashRatio (col 2) is not cash-specific, as expected --- the "
        r"claim concerns the uncertainty response, not cash levels.",
        r"\end{minipage}",
        r"\end{table}",
    ]
    TEX_OUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    p, s, m = emp.base_panel(), emp.sdc(), emp.manifest()
    q, n_cash, n_stock = build_pooled(p, s, m)
    print(f"pooled panel: PreAnn_cash obs={n_cash:,}  PreAnn_stock obs={n_stock:,}\n")
    results = {}
    for dv in ("UncResCEO", "CashRatio"):
        r = run(q, dv)
        results[dv] = r
        print(f"=== DV={dv}  N={r['n']:,}  firms={r['n_firms']:,} ===")
        print(f"  PreAnn_cash  b={r['cash']['b']:+.5f} se={r['cash']['se']:.5f} p2={r['cash']['p2']:.3f}")
        print(f"  PreAnn_stock b={r['stock']['b']:+.5f} se={r['stock']['se']:.5f} p2={r['stock']['p2']:.3f}")
        w = r["wald"]
        print(f"  CASH-SPECIFICITY (cash - stock) = {w['diff']:+.5f} se={w['se']:.5f} "
              f"t={w['t']:+.2f} p2={w['p2']:.3f}")
        print(f"  --> {'cash > stock at p<.05 (one-tailed)' if w['p1'] < 0.05 else 'NOT separable at .05'}\n")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / SUITE / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"suite": SUITE, "dvs": ["UncResCEO", "CashRatio"],
               "pre_counts": {"cash": n_cash, "stock": n_stock},
               "controls": CTRL, "results": results, "timestamp": ts}
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_tex(summary_path)
    print(f"wrote {summary_path}")
    print(f"wrote {TEX_OUT}")


if __name__ == "__main__":
    main()
