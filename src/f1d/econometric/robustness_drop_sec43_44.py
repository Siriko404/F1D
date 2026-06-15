#!/usr/bin/env python3
"""Two robustness checks on the differential-timing / drop result (tab:empire_drop_matched).

Read-only on all inputs. Reuses empire_drop_test (event clock, bins) and
empire_drop_matched_universe (run_on, shared-sample regression). Writes ONLY a
new robustness JSON + prints; it does NOT touch the thesis tables or any
existing output.

Section 4.3 -- RESOLUTION robustness (withdrawal-inclusive POST):
  Baseline POST = completed deals only (cq >= Date Effective). Withdrawn-first
  deals' post-withdrawal call-quarters are dropped, so POST is, by construction,
  a completed-deal bin. A referee asks whether the post-resolution drop is a
  winner-selection artifact. Fix: treat WITHDRAWAL as a resolution event too --
  POST = (closed AND cq>=ceq) OR (withdrawn AND cq>=wq). If the PRE1->POST drop
  survives, the drop is about RESOLUTION (completion or withdrawal), not
  selection of completed deals. (Adds ~89 complete-case POST rows / 28 firms.)

Section 4.4 -- STATIC-FE robustness (Nickell):
  The CashRatio runs carry a within-firm lagged DV (CashRatio_lag) alongside
  firm fixed effects -> a dynamic-panel (Nickell) bias of order 1/T. With T up
  to ~68 quarters the bias is negligible, but to show the run-up/drop does not
  ride on the dynamic term, re-estimate the CashRatio column on the IDENTICAL
  sample WITHOUT CashRatio_lag. The residual DV (UncResCEO) carries no lag, so
  it is mechanically unchanged and is reported only as the unaffected anchor.

Run: python src/f1d/econometric/robustness_drop_sec43_44.py
"""
from __future__ import annotations
import importlib.util
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


edt = _load("edt", "src/f1d/econometric/empire_drop_test.py")
edm = _load("edm", "src/f1d/econometric/empire_drop_matched_universe.py")
CTRL, BINS, DVS = edt.CTRL, edt.BINS, ["UncResCEO", "CashRatio"]
POST_CAP = 4
NEED = ["UncResCEO", "CashRatio", "CashRatio_lag"] + BINS + CTRL


def build_event_resolution(p, s, m, mask, post_cap):
    """edt.build_event, but POST counts ANY resolution (completion OR withdrawal):
    the post-withdrawal drop is removed and withdrawn quarters at/after wq join POST."""
    cd = s[s["known"] & mask].copy()
    cd["dq"] = edt._qtr(cd["da"]); cd["ceq"] = edt._qtr(cd["de"]); cd["wq"] = edt._qtr(cd["dw"])
    cd.loc[cd["ceq"] < cd["dq"], "ceq"] = np.nan
    cd = cd.sort_values("da"); cd["rank"] = cd.groupby("c6").cumcount()
    first = cd[cd["rank"] == 0][["c6", "dq", "ceq", "wq", "status"]].copy()
    second = cd[cd["rank"] == 1][["c6", "dq"]].rename(columns={"dq": "dq2"})
    first = first.merge(second, on="c6", how="left")
    treat = m.merge(first, on="c6", how="inner").drop_duplicates("gvkey")
    q = p.merge(treat[["gvkey", "dq", "ceq", "wq", "status", "dq2"]], on="gvkey", how="left")
    q["e"] = q["cq"] - q["dq"]; tr = q["dq"].notna()
    q = q[~(tr & q["dq2"].notna() & (q["cq"] >= q["dq2"]))].copy(); tr = q["dq"].notna()
    # (the baseline post-withdrawal drop is INTENTIONALLY omitted here)
    q = q[~(tr & (q["e"] > post_cap))].copy(); tr = q["dq"].notna()
    closed = q["ceq"].notna() & (q["cq"] >= q["ceq"])
    withdrawn_res = (q["status"] == "Withdrawn") & q["wq"].notna() & (q["cq"] >= q["wq"])
    resolved = closed | withdrawn_res
    q["PRE2"] = (tr & (q["e"] == -2)).astype(float)
    q["PRE1"] = (tr & (q["e"] == -1)).astype(float)
    q["POST"] = (tr & (q["e"] >= 0) & resolved).astype(float)
    q["GAP"] = (tr & (q["e"] >= 0) & ~resolved).astype(float)
    return q, int(q.loc[tr, "gvkey"].nunique())


def sample(q):
    return q.replace([np.inf, -np.inf], np.nan).dropna(subset=NEED).copy()


def slim(r):
    """Keep bins + drops + controls (+lag) -- everything the comparison AND the
    mirror tables need (controls were previously dropped; advisor #1 2026-06-15)."""
    pick = lambda d: {"b": d["b"], "se": d["se"], "p2": d["p2"]}
    out = {"bins": {b: pick(r["bins"][b]) for b in BINS if b in r["bins"]},
           "pre1_post": r["pre1_post"], "gap_post": r["gap_post"], "pre1_gap": r["pre1_gap"],
           "controls": {c: pick(v) for c, v in r.get("controls", {}).items()},
           "n": r["n"], "n_firms": r["n_firms"]}
    if "lag" in r:
        out["lag"] = pick(r["lag"])
    return out


# ---- LaTeX fragment writer: byte-format-identical to empire_drop_matched_universe.write_tex ----
def _stars(p):
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))


def _cell(coef, p):
    s = _stars(p)
    return f"\\textbf{{{coef:.4f}}}$^{{{s}}}$" if s else f"{coef:.4f}"


_BIN_LABEL = {"PRE2": r"PRE2 ($t{-}2$, pre-trend)",
              "PRE1": r"PRE1 ($t{-}1$, pre-announce)",
              "GAP":  r"GAP (announced, pre-close)",
              "POST": r"POST (completed)"}


def write_tex_robust(res, caption, label, out_path):
    """Build a thesis table fragment from a {dv: slim(run_on)} dict, mirroring the
    matched-universe table exactly (4 bins, 3 drops, controls, lag, N/firms; two-tailed)."""
    dvs = DVS
    L = [r"\begin{table}[htbp]", r"\centering",
         f"\\caption{{{caption}}}", f"\\label{{{label}}}", r"\scriptsize",
         r"\begin{tabular}{lcc}", r"\toprule",
         r" & (1) UncResCEO & (2) CashRatio \\", r"\midrule"]
    for b in BINS:
        cells = " & ".join(_cell(res[dv]["bins"][b]["b"], res[dv]["bins"][b]["p2"]) for dv in dvs)
        ses = " & ".join(f"({res[dv]['bins'][b]['se']:.4f})" for dv in dvs)
        L += [f"{_BIN_LABEL[b]} & {cells} \\\\", f" & {ses} \\\\"]
    L.append(r"\midrule")
    for key, lab in (("pre1_gap", r"Drop: PRE1 $-$ GAP"), ("gap_post", r"Drop: GAP $-$ POST"),
                     ("pre1_post", r"Drop: PRE1 $-$ POST")):
        cells = " & ".join(_cell(res[dv][key]["diff"], res[dv][key]["p2"]) for dv in dvs)
        ses = " & ".join(f"({res[dv][key]['se']:.4f})" for dv in dvs)
        L += [f"{lab} & {cells} \\\\", f" & {ses} \\\\"]
    L += [r"\midrule", r"\multicolumn{3}{l}{\textit{Controls}} \\"]
    for c in CTRL:
        cv = " & ".join((_cell(res[dv]["controls"][c]["b"], res[dv]["controls"][c]["p2"])
                         if c in res[dv].get("controls", {}) else "---") for dv in dvs)
        cs = " & ".join((f"({res[dv]['controls'][c]['se']:.4f})"
                        if c in res[dv].get("controls", {}) else "") for dv in dvs)
        L += [f"{c} & {cv} \\\\", f" & {cs} \\\\"]
    lag_cells = " & ".join((_cell(res[dv]["lag"]["b"], res[dv]["lag"]["p2"]) if "lag" in res[dv] else "---") for dv in dvs)
    lag_ses = " & ".join((f"({res[dv]['lag']['se']:.4f})" if "lag" in res[dv] else "") for dv in dvs)
    L += [r"CashRatio$_{t-1}$ (partial adj.) & " + lag_cells + r" \\", f" & {lag_ses} \\\\"]
    n, nf = res["CashRatio"]["n"], res["CashRatio"]["n_firms"]
    L += [r"\midrule", r"Firm FE / Year-Qtr FE / Controls & Yes & Yes \\",
          f"N (firm-quarters) & {n:,} & {n:,} \\\\",
          f"Firms & {nf:,} & {nf:,} \\\\",
          r"\bottomrule", r"\end{tabular}",
          r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize",
          r"\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed).",
          r"\end{minipage}", r"\end{table}"]
    out_path.write_text("\n".join(L), encoding="utf-8")


def main():
    p = edt.base_panel()
    p = p.sort_values(["gvkey", "cq"])
    p["CashRatio_lag"] = p.groupby("gvkey")["CashRatio"].shift(1)
    _pcq = p.groupby("gvkey")["cq"].shift(1)
    p.loc[_pcq != p["cq"] - 1, "CashRatio_lag"] = np.nan
    s, m = edt.sdc(), edt.manifest()
    mask = s["pc"] >= 50

    edt.POST_CAP = POST_CAP
    q_base, _ = edt.build_event(p, s, m, mask)
    d_base = sample(q_base)
    base = {dv: slim(edm.run_on(d_base, dv, add_cash_lag=(dv == "CashRatio"))) for dv in DVS}

    q_res, _ = build_event_resolution(p, s, m, mask, POST_CAP)
    d_res = sample(q_res)
    res43 = {dv: slim(edm.run_on(d_res, dv, add_cash_lag=(dv == "CashRatio"))) for dv in DVS}

    # §4.4: same baseline sample, CashRatio WITHOUT the lag (UncResCEO unchanged anchor)
    res44 = {dv: slim(edm.run_on(d_base, dv, add_cash_lag=False)) for dv in DVS}

    def line(tag, r):
        for dv in DVS:
            b = r[dv]["bins"]; pp = r[dv]["pre1_post"]
            print(f"  {tag:12} {dv:10} PRE1={b['PRE1']['b']:+.4f}(p{b['PRE1']['p2']:.3f}) "
                  f"GAP={b['GAP']['b']:+.4f}(p{b['GAP']['p2']:.3f}) POST={b['POST']['b']:+.4f}(p{b['POST']['p2']:.3f}) "
                  f"| PRE1-POST={pp['diff']:+.4f}(p{pp['p2']:.3f}) | N={r[dv]['n']:,}")

    print(f"\nBASELINE  N={base['CashRatio']['n']:,}")
    line("baseline", base)
    print(f"\n§4.3 RESOLUTION (withdrawal in POST)  N={res43['CashRatio']['n']:,}  (+{res43['CashRatio']['n']-base['CashRatio']['n']} rows)")
    line("resolution", res43)
    print(f"\n§4.4 STATIC-FE (no CashRatio_lag)  N={res44['CashRatio']['n']:,}")
    line("static-fe", res44)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / "robustness_drop_sec43_44" / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"suite": "robustness_drop_sec43_44", "post_cap": POST_CAP,
               "baseline": base, "sec43_resolution": res43, "sec44_static_fe": res44,
               "timestamp": ts}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nwrote {out / 'summary.json'}")

    drv = ROOT / "docs" / "Draft"
    write_tex_robust(res43, "Resolution-Inclusive POST: Withdrawal Treated as a Resolution Event (robustness)",
                     "tab:empire_drop_resolution", drv / "_empire_drop_resolution.tex")
    write_tex_robust(res44, "Static Fixed Effects: the Cash Result Without the Lagged Dependent Variable (robustness)",
                     "tab:empire_drop_staticfe", drv / "_empire_drop_staticfe.tex")
    print(f"wrote {drv / '_empire_drop_resolution.tex'}")
    print(f"wrote {drv / '_empire_drop_staticfe.tex'}")


if __name__ == "__main__":
    main()
