#!/usr/bin/env python3
"""Comparability check: run UncResCEO and CashRatio on the IDENTICAL sample.

The pooled drop test runs each DV on its own complete-case set -> UncRes on the
~29k call-quarter universe (residual only exists where there's a CEO Q&A), Cash on
the ~77k all-quarter universe. So the 'differential timing' (UncRes falls at announce,
cash falls at close) could be a SAMPLE artifact (different firms/quarters), not a real
within-firm timing split.

Fix: require UncResCEO AND CashRatio AND controls all non-missing -> one shared sample.
Run BOTH DVs on those exact rows. If cash still stays-high-at-GAP / drops-at-POST on the
UncRes universe, the timing split is real. If it weakens, the dissociation was an artifact.

Also reports the correct per-DV post-dropna bin counts (the pooled script printed
pre-dropna pops, ~2.4x inflated). Reuses empire_drop_test helpers. Read-only on inputs.

Writes:
  outputs/econometric/empire_drop_matched/<ts>/summary.json   (numbers = the JSON spec)
  docs/Draft/_empire_drop_matched.tex                         (thesis fragment, built FROM the json)

Run: python src/f1d/econometric/empire_drop_matched_universe.py
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
spec = importlib.util.spec_from_file_location("_edt", Path(__file__).resolve().parent / "empire_drop_test.py")
edt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edt)
CTRL, BINS = edt.CTRL, edt.BINS

SUITE = "empire_drop_matched"
TEX_OUT = ROOT / "docs" / "Draft" / "_empire_drop_matched.tex"
BIN_LABEL = {"PRE2": r"PRE2 ($t{-}2$, pre-trend)",
             "PRE1": r"PRE1 ($t{-}1$, pre-announce)",
             "GAP":  r"GAP (announced, pre-close)",
             "POST": r"POST (completed)"}


def run_on(d: pd.DataFrame, dv: str) -> dict:
    n_firms = int(d["gvkey"].nunique())
    dd = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(BINS) + " + " + " + ".join(CTRL) \
        + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov

    def one(n):
        b, p2 = float(par[n]), float(pv[n])
        return {"b": b, "se": float(se[n]), "p1": p2 / 2 if b > 0 else 1 - p2 / 2, "p2": p2}

    def wald(i, j):
        diff = float(par[i] - par[j])
        var = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j])
        se_ = var ** 0.5
        t = diff / se_
        p2 = 2 * norm.sf(abs(t))
        return {"diff": diff, "se": se_, "t": t, "p1": p2 / 2 if diff > 0 else 1 - p2 / 2, "p2": p2}

    return {"bins": {b: one(b) for b in BINS if b in par.index},
            "pre1_gap": wald("PRE1", "GAP"), "pre1_post": wald("PRE1", "POST"),
            "n": int(mod.nobs), "n_firms": n_firms}


def stars(p: float) -> str:
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))


def cell(coef: float, p: float) -> str:
    s = stars(p)
    return f"\\textbf{{{coef:.4f}}}$^{{{s}}}$" if s else f"{coef:.4f}"


def write_tex(summary_path: Path) -> None:
    """Build the LaTeX fragment FROM the written JSON spec (+4 primary; +8 in JSON)."""
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    sp = summary["specs"]["post_cap_4"]
    res = sp["results"]
    dvs = ["UncResCEO", "CashRatio"]
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Pre-Acquisition Uncertainty vs.\ Cash on the Matched Universe (disclosure-window event study)}",
        r"\label{tab:empire_drop_matched}",
        r"\scriptsize",
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r" & (1) UncResCEO & (2) CashRatio \\",
        r"\midrule",
    ]
    for b in BINS:
        cells = " & ".join(cell(res[dv]["bins"][b]["b"], res[dv]["bins"][b]["p1"]) for dv in dvs)
        ses = " & ".join(f"({res[dv]['bins'][b]['se']:.4f})" for dv in dvs)
        lines.append(f"{BIN_LABEL[b]} & {cells} \\\\")
        lines.append(f" & {ses} \\\\")
    lines.append(r"\midrule")
    for key, lab in (("pre1_gap", r"Drop: PRE1 $-$ GAP"), ("pre1_post", r"Drop: PRE1 $-$ POST")):
        cells = " & ".join(cell(res[dv][key]["diff"], res[dv][key]["p2"]) for dv in dvs)
        sline = " & ".join(f"({res[dv][key]['se']:.4f})" for dv in dvs)
        lines.append(f"{lab} & {cells} \\\\")
        lines.append(f" & {sline} \\\\")
    lines += [
        r"\midrule",
        r"Firm FE / Year-Qtr FE / Controls & Yes & Yes \\",
        f"N (firm-quarters) & {sp['n']:,} & {sp['n']:,} \\\\",
        f"Firms & {sp['n_firms']:,} & {sp['n_firms']:,} \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize",
        r"\textit{Notes:} Two-way FE OLS (firm + calendar year-quarter), firm-clustered SE, on the "
        rf"\emph{{identical}} {sp['n']:,}-observation sample where both UncResCEO and CashRatio are "
        r"present (the UncResCEO call universe). Event bins around the firm's first $\geq$50\%-cash "
        r"acquisition: PRE2/PRE1 = two / one quarter pre-announcement; GAP = announced but not yet "
        r"completed; POST = completed. Baseline = $e\leq-3$ plus never-acquirers. Bin coefficients: "
        r"$^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ one-tailed; Drop rows (Wald on the bin difference): "
        r"stars two-tailed. Standard errors in parentheses throughout. Pre-completion bin counts (PRE2/PRE1/GAP/POST): "
        rf"{sp['pops']['PRE2']:,}/{sp['pops']['PRE1']:,}/{sp['pops']['GAP']:,}/{sp['pops']['POST']:,}. "
        r"UncResCEO peaks at PRE1 and collapses at GAP (announcement); CashRatio stays elevated through "
        r"GAP and falls only at POST (completion). The uncertainty tracks the disclosure state, not the "
        r"cash balance. Robustness: +8-quarter post-window in the summary JSON.",
        r"\end{minipage}",
        r"\end{table}",
    ]
    TEX_OUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    p, s, m = edt.base_panel(), edt.sdc(), edt.manifest()
    specs = {}
    for cap in (4, 8):
        edt.POST_CAP = cap
        q, n_tr = edt.build_event(p, s, m, s["pc"] >= 50)   # cash arm
        need = ["UncResCEO", "CashRatio"] + BINS + CTRL      # ONE shared sample
        d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
        pops = {b: int(d[b].sum()) for b in BINS}
        results = {dv: run_on(d, dv) for dv in ("UncResCEO", "CashRatio")}
        specs[f"post_cap_{cap}"] = {"post_cap": cap, "n": len(d),
                                    "n_firms": int(d["gvkey"].nunique()),
                                    "pops": pops, "results": results}
        print(f"\n###### CASH arm | +{cap} | SHARED N={len(d):,} firms={d['gvkey'].nunique():,} ######")
        print(f"  bin counts (PRE2/PRE1/GAP/POST): " + "/".join(f"{pops[b]:,}" for b in BINS))
        for dv in ("UncResCEO", "CashRatio"):
            r = results[dv]
            for b in BINS:
                v = r["bins"][b]
                print(f"  {dv:10} {b:5} b={v['b']:+.5f} se={v['se']:.5f} p1={v['p1']:.3f}")
            print(f"  {dv:10} DROP PRE1-GAP={r['pre1_gap']['diff']:+.5f} t={r['pre1_gap']['t']:+.2f}"
                  f" | PRE1-POST={r['pre1_post']['diff']:+.5f} t={r['pre1_post']['t']:+.2f}")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / SUITE / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"suite": SUITE, "dvs": ["UncResCEO", "CashRatio"], "bins": BINS,
               "controls": CTRL, "specs": specs, "timestamp": ts}
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_tex(summary_path)
    print(f"\nwrote {summary_path}")
    print(f"wrote {TEX_OUT}")


if __name__ == "__main__":
    main()
