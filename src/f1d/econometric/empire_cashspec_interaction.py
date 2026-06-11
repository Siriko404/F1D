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

The CashRatio (proposed-cause) columns use CashRatio as the DV and ADD its own one-quarter
within-firm lag (CashRatio_lag) as a partial-adjustment control (cash is sticky, rho~0.78),
so the pre-announce coefficient tracks the CHANGE in cash, not its level. The UncResCEO
column is a residual and takes NO lagged DV.

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


def run(q, dv, restrict_uncres=True, add_cash_lag=False):
    # restrict_uncres=True  -> matched UncResCEO-CashRatio sample (both present)
    # restrict_uncres=False -> full cash panel (UncResCEO not required); dv always required
    # add_cash_lag=True     -> partial-adjustment: add CashRatio's own one-quarter within-firm
    #                          lag so the pre-announce coef tracks the CHANGE, not the level
    #                          (cash is sticky, lag coef ~0.78). Residual DVs must NOT use this.
    extra = ["CashRatio_lag"] if add_cash_lag else []
    need = [dv, "PreAnn_cash", "PreAnn_stock"] + CTRL + extra
    if restrict_uncres and "UncResCEO" not in need:
        need = ["UncResCEO"] + need
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + PreAnn_cash + PreAnn_stock + " + " + ".join(CTRL + extra) \
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
    out = {"cash": one(i), "stock": one(j), "wald": wald,
           "controls": {c: one(c) for c in CTRL if c in par.index},
           "n": int(mod.nobs), "n_firms": int(d.reset_index()["gvkey"].nunique())}
    if add_cash_lag and "CashRatio_lag" in par.index:
        out["lag"] = one("CashRatio_lag")   # partial-adjustment coefficient (two-tailed)
    return out


def stars(p: float) -> str:
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))


def cell(coef: float, p: float) -> str:
    s = stars(p)
    return f"\\textbf{{{coef:.4f}}}$^{{{s}}}$" if s else f"{coef:.4f}"


def write_tex(summary_path: Path) -> None:
    """Build the LaTeX fragment FROM the written JSON spec.

    All significance is uniform two-tailed (cash row, stock row, and the Cash-Stock
    formal difference alike).

    Three columns: (1) the EFFECT (UncResCEO, matched sample, no lag), (2) the
    proposed CAUSE (CashRatio + its own lag) on the SAME matched sample, (3) the
    same cause on the FULL cash panel (UncResCEO restriction dropped). The point:
    with the partial-adjustment lag, the cash-build Cash-Stock difference stays ns
    in the matched sample and is only marginal (p~.10) in the full panel, while the
    uncertainty difference is clearly significant."""
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    res = summary["results"]
    pdir = "p2"                                # uniform two-tailed
    cols = ["UncResCEO", "CashRatio_matched", "CashRatio_full"]
    head = {"UncResCEO": r"(1) UncResCEO", "CashRatio_matched": r"(2) CashRatio",
            "CashRatio_full": r"(3) CashRatio"}
    sub = {"UncResCEO": r"(matched)", "CashRatio_matched": r"(matched, +lag)",
           "CashRatio_full": r"(full panel, +lag)"}
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Formal Cash-Specificity: Pre-Announcement Uncertainty (effect) vs.\ Cash Build-Up (proposed cause), cash vs.\ stock acquirers}",
        r"\label{tab:empire_cashspec}",
        r"\scriptsize",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r" & \multicolumn{1}{c}{EFFECT} & \multicolumn{2}{c}{PROPOSED CAUSE} \\",
        r"\cmidrule(lr){2-2}\cmidrule(lr){3-4}",
        " & " + " & ".join(head[c] for c in cols) + r" \\",
        " & " + " & ".join(sub[c] for c in cols) + r" \\",
        r"\midrule",
    ]
    # cash row: two-tailed (uniform convention)
    lines.append(r"Pre-announce qtr, Cash acquirer & "
                 + " & ".join(cell(res[c]["cash"]["b"], res[c]["cash"][pdir]) for c in cols) + r" \\")
    lines.append(" & " + " & ".join(f"({res[c]['cash']['se']:.4f})" for c in cols) + r" \\")
    # stock row: TWO-tailed (placebo arm, no directional prior)
    lines.append(r"Pre-announce qtr, Stock acquirer & "
                 + " & ".join(cell(res[c]["stock"]["b"], res[c]["stock"]["p2"]) for c in cols) + r" \\")
    lines.append(" & " + " & ".join(f"({res[c]['stock']['se']:.4f})" for c in cols) + r" \\")

    lines.append(r"\midrule")
    # formal difference: two-tailed
    lines.append(r"Cash $-$ Stock (formal test) & "
                 + " & ".join(cell(res[c]["wald"]["diff"], res[c]["wald"]["p2"]) for c in cols) + r" \\")
    lines.append(" & " + " & ".join(f"({res[c]['wald']['se']:.4f})" for c in cols) + r" \\")

    def _lag_cell(c):
        r = res[c].get("lag")
        return cell(r["b"], r["p2"]) if r else r"---"

    def _lag_se(c):
        r = res[c].get("lag")
        return f"({r['se']:.4f})" if r else ""
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{4}{l}{\textit{Controls}} \\")
    for ct in CTRL:
        cv = " & ".join((cell(res[c]["controls"][ct]["b"], res[c]["controls"][ct]["p2"])
                         if ct in res[c].get("controls", {}) else "---") for c in cols)
        cs = " & ".join((f"({res[c]['controls'][ct]['se']:.4f})"
                        if ct in res[c].get("controls", {}) else "") for c in cols)
        lines.append(f"{ct} & {cv} \\\\")
        lines.append(f" & {cs} \\\\")
    lines.append(r"\quad CashRatio$_{t-1}$ (partial adj.) & "
                 + " & ".join(_lag_cell(c) for c in cols) + r" \\")
    lines.append(" & " + " & ".join(_lag_se(c) for c in cols) + r" \\")
    lines += [
        r"\midrule",
        r"Firm FE / Year-Qtr FE / Controls & Yes & Yes & Yes \\",
        r"UncResCEO-present restriction & Yes & Yes & \textbf{No} \\",
        "N (firm-quarters) & " + " & ".join(f"{res[c]['n']:,}" for c in cols) + r" \\",
        "Firms & " + " & ".join(f"{res[c]['n_firms']:,}" for c in cols) + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize",
        r"\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed).",
        r"\end{minipage}",
        r"\end{table}",
    ]
    TEX_OUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    p, s, m = emp.base_panel(), emp.sdc(), emp.manifest()
    # CashRatio is sticky -> build its true one-quarter within-firm lag (consecutive quarters
    # only) so the CashRatio regressions can control for the firm's own prior cash level
    # (partial-adjustment). Built on the full base panel BEFORE build_pooled so it survives
    # the merge; the residual UncResCEO column does NOT use it.
    p = p.sort_values(["gvkey", "cq"]).copy()
    p["CashRatio_lag"] = p.groupby("gvkey")["CashRatio"].shift(1)
    prev_cq = p.groupby("gvkey")["cq"].shift(1)
    p.loc[prev_cq != p["cq"] - 1, "CashRatio_lag"] = np.nan   # only consecutive-quarter lags
    q, n_cash, n_stock = build_pooled(p, s, m)
    print(f"pooled panel: PreAnn_cash obs={n_cash:,}  PreAnn_stock obs={n_stock:,}\n")
    results = {
        "UncResCEO": run(q, "UncResCEO", restrict_uncres=True),                              # effect, matched (residual, no lag)
        "CashRatio_matched": run(q, "CashRatio", restrict_uncres=True, add_cash_lag=True),   # cause, matched, partial-adjustment
        "CashRatio_full": run(q, "CashRatio", restrict_uncres=False, add_cash_lag=True),     # cause, full panel, partial-adjustment
    }
    for key, r in results.items():
        print(f"=== {key}  N={r['n']:,}  firms={r['n_firms']:,} ===")
        print(f"  PreAnn_cash  b={r['cash']['b']:+.5f} se={r['cash']['se']:.5f} p2={r['cash']['p2']:.3f}")
        print(f"  PreAnn_stock b={r['stock']['b']:+.5f} se={r['stock']['se']:.5f} p2={r['stock']['p2']:.3f} (two-tailed)")
        w = r["wald"]
        print(f"  CASH-STOCK diff = {w['diff']:+.5f} se={w['se']:.5f} t={w['t']:+.2f} p2={w['p2']:.3f}\n")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / SUITE / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"suite": SUITE, "dvs": ["UncResCEO", "CashRatio_matched", "CashRatio_full"],
               "pre_counts": {"cash": n_cash, "stock": n_stock},
               "controls": CTRL, "results": results, "timestamp": ts}
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_tex(summary_path)
    print(f"wrote {summary_path}")
    print(f"wrote {TEX_OUT}")


if __name__ == "__main__":
    main()
