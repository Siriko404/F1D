#!/usr/bin/env python3
"""Generate the Cash-Scrutiny Reason-Gating test table fragment.

Tests the hypothesis: do CEOs sound more uncertain IN RESPONSE to analyst
cash-scrutiny only when there is a real reason -- a pending >=50%-cash
acquisition? The test is the interaction CashScrutiny x PreAnnounceQtr on
UncResCEO, estimated on the cash-acquirer pre-announcement universe (the SAME
universe that produces the empire run-up effect), restricted to calls that have
both CashScrutiny and UncResCEO (the matched universe).

Reads the universe via gen_empire_did_table.py's exact wiring (base_panel/sdc/
manifest/build, cash mask pc>=50), so the sample is identical to the empire
table's cash arm. Two columns:
  (1) UncRes ~ CashScrutiny + PreAnnounceQtr + controls            (main effects)
  (2) (1) + CashScrutiny x PreAnnounceQtr                          (reason-gating)
Both firm + cal-year-quarter FE, firm-clustered SE.

Finding: PreAnnounceQtr (the reason) raises UncRes; CashScrutiny does not; the
interaction is null -> CEO residual uncertainty is event-driven, not gated by
analyst scrutiny.

script -> outputs/econometric/reason_gating/<ts>/summary.json -> docs/Draft/_reason_gating.tex
Regenerate: python scripts/gen_reason_gating_table.py
NOT hand-edited -- table cells come from this script's regression output.
"""
from __future__ import annotations
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gen_empire_did_table import base_panel, sdc, manifest, build, CTRL  # exact empire universe

SUITE = "reason_gating"
TEX_OUT = ROOT / "docs" / "Draft" / f"_{SUITE}.tex"
DV = "UncResCEO"


def fit(q: pd.DataFrame, rhs: list[str]) -> dict:
    """Firm + cal-qtr FE OLS of UncResCEO on rhs (+ controls), firm-clustered.

    Sample = cash-acquirer pre-window rows with BOTH CashScrutiny and UncResCEO
    present (the matched universe); identical across columns for comparability.
    """
    d = q.replace([np.inf, -np.inf], np.nan).dropna(
        subset=[DV, "CashScrutiny", "PreAnnounceQtr"] + CTRL).copy()
    n_firms = int(d["gvkey"].nunique())
    d = d.set_index(["gvkey", "cq"])
    f = f"{DV} ~ 1 + " + " + ".join(rhs + CTRL) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    terms = {}
    for v in rhs:
        if v in m.params.index:
            b, se, p2 = float(m.params[v]), float(m.std_errors[v]), float(m.pvalues[v])
            terms[v] = {"beta": b, "se": se, "p2": p2, "p1": p2 / 2 if b > 0 else 1 - p2 / 2}
    return {"terms": terms, "n": int(m.nobs), "n_firms": n_firms, "r2": float(m.rsquared)}


def stars(p: float) -> str:
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))


def cell(t: dict | None) -> str:
    if t is None:
        return ""
    s = stars(t["p1"])
    body = f"{t['beta']:.4f}"
    return f"\\textbf{{{body}}}$^{{{s}}}$" if s else body


def se_cell(t: dict | None) -> str:
    return "" if t is None else f"({t['se']:.4f})"


def write_tex(C1: dict, C2: dict) -> None:
    def row(name, key):
        t1 = C1["terms"].get(key)
        t2 = C2["terms"].get(key)
        return [f"{name} & " + cell(t1) + " & " + cell(t2) + r" \\",
                " & " + se_cell(t1) + " & " + se_cell(t2) + r" \\"]

    L = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Cash-Scrutiny Reason-Gating Test}",
        r"\label{tab:reason_gating}",
        r"\small",
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r" & \multicolumn{2}{c}{UncResCEO} \\",
        r"\cmidrule(lr){2-3}",
        r" & (1) & (2) \\",
        r"\midrule",
    ]
    L += row("CashScrutiny", "CashScrutiny")
    L += row("PreAnnounceQtr", "PreAnnounceQtr")
    L += row(r"CashScrutiny $\times$ PreAnnounceQtr", "ScrXPre")
    L += [
        r"\midrule",
        r"Controls & Yes & Yes \\",
        r"Firm FE & Yes & Yes \\",
        r"Cal. Year-Quarter FE & Yes & Yes \\",
        r"\midrule",
        f"N (firm-quarters) & {C1['n']:,} & {C2['n']:,} " + r"\\",
        f"Firms & {C1['n_firms']:,} & {C2['n_firms']:,} " + r"\\",
        f"$R^2$ & {C1['r2']:.3f} & {C2['r2']:.3f} " + r"\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed, $\beta>0$, "
        r"for the directional terms); significant coefficients in \textbf{bold}. Standard errors "
        r"(in parentheses) clustered at firm level. Estimated on cash-acquirer firms "
        r"($\geq$50\%-cash acquisitions; SDC, US public, 2002--2018) over their pre-announcement "
        r"and earlier quarters (post-announcement quarters dropped); \texttt{PreAnnounceQtr} $=$ "
        r"$\mathbf{1}$[the single quarter before announcement]. Sample restricted to calls with "
        r"both \texttt{CashScrutiny} and \texttt{UncResCEO} (the matched universe). "
        r"\texttt{CashScrutiny} $=$ \% of a call's analyst Q\&A turns on cash/liquidity. The reason "
        r"(\texttt{PreAnnounceQtr}) raises CEO residual uncertainty; analyst cash-scrutiny does not, "
        r"and the interaction is insignificant.",
        r"\end{minipage}",
        r"\end{table}",
    ]
    TEX_OUT.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    p, s, m = base_panel(), sdc(), manifest()
    q, ntreat = build(p, s, m, s["pc"] >= 50)         # cash-acquirer universe (exact empire wiring)
    q["ScrXPre"] = q["CashScrutiny"] * q["PreAnnounceQtr"]

    C1 = fit(q, ["CashScrutiny", "PreAnnounceQtr"])                 # main effects
    C2 = fit(q, ["CashScrutiny", "PreAnnounceQtr", "ScrXPre"])      # + reason-gating interaction

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / SUITE / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"suite": SUITE, "dv": DV, "universe": "cash-acquirer pre-window, UncRes-matched",
               "treated_firms": ntreat, "controls": CTRL,
               "col1_main": C1, "col2_interaction": C2, "timestamp": ts}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_tex(C1, C2)

    for tag, C in [("main", C1), ("interaction", C2)]:
        bits = " | ".join(f"{k} b={v['beta']:+.5f} p1={v['p1']:.3f}" for k, v in C["terms"].items())
        print(f"  {tag:11s} N={C['n']:,} firms={C['n_firms']:,} :: {bits}")
    print(f"wrote {out/'summary.json'}")
    print(f"wrote {TEX_OUT}")


if __name__ == "__main__":
    main()
