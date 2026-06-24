"""
First-deal-only robustness, rendered in the EXACT thesis table format
(SUPERVISOR ARTIFACT -- NOT a thesis fragment).

It reuses the thesis writers verbatim:
  * gen_empire_did_table.write_tex      -> the Run-Up table (same as Table 5.2)
  * empire_cashspec_interaction.write_tex -> the Cash-Specificity table (same as Table 5.5)
fed with an ALL-DEALS (stacked) panel instead of first-deal-only. Convention preserved:
compute -> summary.json -> write_tex(json) -> .tex; nothing hardcoded.

Output (timestamped): outputs/econometric/firstdeal_robustness/<ts>/
  summary_runup.json, summary_cashspec.json   (numbers)
  _rb_runup.tex, _rb_cashspec.tex             (all-deals, thesis format)
  robustness_standalone.tex                    (wraps thesis 5.2/5.5 + all-deals, side by side)

Run: python scripts/gen_firstdeal_robustness.py
"""
import importlib.util, json, sys
import numpy as np, pandas as pd
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gen_empire_did_table as G

_spec = importlib.util.spec_from_file_location(
    "cx", ROOT / "src" / "f1d" / "econometric" / "empire_cashspec_interaction.py")
cx = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(cx)

AFT, CONTAM = 3, 3


def _deal_q(s, m, mask):
    cd = s[s["known"] & mask].copy()
    cd["dq"] = cd["da"].dt.year * 4 + (cd["da"].dt.quarter - 1)
    cd = cd.merge(m, on="c6", how="inner")
    return cd.groupby("gvkey")["dq"].apply(lambda x: sorted(set(x))).to_dict()


def _clean_pre(D, g, cq):
    Dg = D.get(g)
    return bool(Dg) and ((cq + 1) in Dg) and not any((cq - (CONTAM - 1)) <= d <= cq for d in Dg)


def _arm_panel(p, D, after_q):
    """Stacked single-arm panel: PreAnnounceQtr = clean e=-1; drop contaminated run-up + aftermath."""
    out = p.copy()
    cls = []
    for g, cq in zip(out["gvkey"], out["cq"]):
        if _clean_pre(D, g, cq):
            cls.append("treat")
        elif after_q(g, cq):
            cls.append("drop")
        else:
            cls.append("base")
    out["cls"] = cls
    out = out[out["cls"] != "drop"].copy()
    out["PreAnnounceQtr"] = (out["cls"] == "treat").astype(float)
    return out


def main():
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / "firstdeal_robustness" / ts
    out.mkdir(parents=True, exist_ok=True)

    p, s, m = G.base_panel(), G.sdc(), G.manifest()
    cashD, stockD = _deal_q(s, m, s["pc"] >= 50), _deal_q(s, m, s["ps"] >= 50)
    after_cash = lambda g, cq: any(0 <= cq - d <= AFT for d in cashD.get(g, []))
    after_stock = lambda g, cq: any(0 <= cq - d <= AFT for d in stockD.get(g, []))

    # ---------- RUN-UP (Table 5.2 format), all-deals ----------
    qc = _arm_panel(p, cashD, after_cash)
    qs = _arm_panel(p, stockD, after_stock)
    res, counts = {}, {}
    for arm, q in (("cash", qc), ("stock", qs)):
        counts[arm] = int(q.loc[q["PreAnnounceQtr"] == 1, "gvkey"].nunique())
        for dv in G.DVS:
            mu = "UncResCEO" if dv in ("CashScrutiny", "HighCashScrutiny") else None
            res[(arm, dv)] = G.run(q, dv, match=mu, add_cash_lag=(dv == "CashRatio"))
    (out / "summary_runup.json").write_text(json.dumps(
        {f"{a}:{d}": res[(a, d)] for (a, d) in res}, indent=2), encoding="utf-8")
    # reuse the THESIS writer (same format), redirect output, retitle/relabel
    G.TEX_OUT = out / "_rb_runup.tex"
    G.write_tex(res, counts)
    t = (out / "_rb_runup.tex").read_text(encoding="utf-8")
    t = t.replace(r"\caption{Empire-Building Run-Up Test}",
                  r"\caption{Pre-Announcement Run-Up --- ALL cash/stock deals (stacked, contaminated run-ups dropped)}")
    t = t.replace(r"\label{tab:empire_building_did}", r"\label{tab:rb_runup}")
    (out / "_rb_runup.tex").write_text(t, encoding="utf-8")

    # ---------- CASH-SPECIFICITY (Table 5.5 format), all-deals pooled ----------
    pc = _clean_pre  # alias
    def pooled():
        d = p.copy()
        af = lambda g, cq: after_cash(g, cq) or after_stock(g, cq)
        rows = []
        for g, cq in zip(d["gvkey"], d["cq"]):
            cpre, spre = pc(cashD, g, cq), pc(stockD, g, cq)
            if cpre and spre: rows.append("drop")
            elif cpre and not af(g, cq): rows.append("cash")
            elif spre and not af(g, cq): rows.append("stock")
            elif af(g, cq): rows.append("drop")
            else: rows.append("base")
        d["cls"] = rows
        d = d[d["cls"] != "drop"].copy()
        d["PreAnn_cash"] = (d["cls"] == "cash").astype(float)
        d["PreAnn_stock"] = (d["cls"] == "stock").astype(float)
        return d
    q = pooled()
    results = {
        "UncResCEO": cx.run(q, "UncResCEO", restrict_uncres=True),
        "CashRatio_matched": cx.run(q, "CashRatio", restrict_uncres=True, add_cash_lag=True),
        "CashRatio_full": cx.run(q, "CashRatio", restrict_uncres=False, add_cash_lag=True),
    }
    summ = {"suite": "firstdeal_robustness_cashspec",
            "dvs": ["UncResCEO", "CashRatio_matched", "CashRatio_full"],
            "pre_counts": {"cash": int((q["PreAnn_cash"] == 1).sum()),
                           "stock": int((q["PreAnn_stock"] == 1).sum())},
            "controls": cx.CTRL, "results": results, "timestamp": ts}
    sp = out / "summary_cashspec.json"
    sp.write_text(json.dumps(summ, indent=2), encoding="utf-8")
    cx.TEX_OUT = out / "_rb_cashspec.tex"
    cx.write_tex(sp)
    t = (out / "_rb_cashspec.tex").read_text(encoding="utf-8")
    t = t.replace(r"\caption{Formal Cash-Specificity: Pre-Announcement Uncertainty (effect) vs.\ Cash Build-Up (proposed cause), cash vs.\ stock acquirers}",
                  r"\caption{Formal Cash-Specificity --- ALL deals (stacked, contaminated run-ups dropped)}")
    t = t.replace(r"\label{tab:empire_cashspec}", r"\label{tab:rb_cashspec}")
    (out / "_rb_cashspec.tex").write_text(t, encoding="utf-8")

    # ---------- standalone doc: thesis tables + all-deals tables, same format ----------
    draft = ROOT / "docs" / "Draft"
    doc = [
        r"\documentclass[10pt]{article}",
        r"\usepackage[margin=0.7in,landscape]{geometry}",
        r"\usepackage{booktabs,amsmath,graphicx,float}",
        r"\renewcommand{\arraystretch}{1.0}",
        r"\begin{document}",
        r"\begin{center}{\large\textbf{First-Deal vs.\ All-Deals --- same thesis table format}}\\",
        r"\small supervisor artifact, not in the thesis. Top = published thesis table; bottom = all-deals re-estimation.\end{center}",
        r"\section*{Run-Up}",
        r"\textbf{Thesis (Table 5.2, first deal):}\par", rf"\input{{{(draft / '_empire_building_did.tex').as_posix()}}}",
        r"\par\vspace{6pt}\textbf{All cash/stock deals (stacked):}\par", rf"\input{{{(out / '_rb_runup.tex').as_posix()}}}",
        r"\clearpage",
        r"\section*{Cash-Specificity}",
        r"\textbf{Thesis (Table 5.5, matched):}\par", rf"\input{{{(draft / '_empire_cashspec.tex').as_posix()}}}",
        r"\par\vspace{6pt}\textbf{All deals (stacked):}\par", rf"\input{{{(out / '_rb_cashspec.tex').as_posix()}}}",
        r"\end{document}",
    ]
    (out / "robustness_standalone.tex").write_text("\n".join(doc), encoding="utf-8")
    print("OUT_DIR:", out)
    for f in ["summary_runup.json", "summary_cashspec.json", "_rb_runup.tex", "_rb_cashspec.tex", "robustness_standalone.tex"]:
        print("  wrote", f)


if __name__ == "__main__":
    main()
