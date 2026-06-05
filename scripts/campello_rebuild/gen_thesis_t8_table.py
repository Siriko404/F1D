"""GEN — side-by-side Campello Table-8 rebuild LaTeX fragment (14-col).

Single source of truth = step summary.json files. NO numbers hardcoded.

Columns (Sina 2026-06-05; CASH eq.14 + CASH PSM + UncResCEO full grid + Campello):
  (1)  Rebuild CASH        βᵁᴷ-tercile   <- econometric/h1_5_brexit_did
  (2)  Rebuild CASH        textual §1+7  <- econometric/h1_5_brexit_did
  (3)  Rebuild CASH PSM    βᵁᴷ-tercile   <- econometric/h1_5_brexit_did_psm
  (4)  Rebuild CASH PSM    textual §1+7  <- econometric/h1_5_brexit_did_psm
  (5)  UncResCEO           βᵁᴷ-tercile   <- econometric/h1_5_brexit_did_uncres_ext (cont,normal)
  (6)  UncResCEO           textual §1+7  <- "" (cont,normal)
  (7)  UncResCEO PSM       βᵁᴷ-tercile   <- "" (cont,psm)
  (8)  UncResCEO PSM       textual §1+7  <- "" (cont,psm)
  (9)  1[UncRes≥med]       βᵁᴷ-tercile   <- "" (bin,normal)
  (10) 1[UncRes≥med]       textual §1+7  <- "" (bin,normal)
  (11) 1[UncRes≥med] PSM   βᵁᴷ-tercile   <- "" (bin,psm)
  (12) 1[UncRes≥med] PSM   textual §1+7  <- "" (bin,psm)
  (13) Campello T8 col.1   βᵁᴷ  CASH benchmark
  (14) Campello T8 col.2   textual CASH benchmark

CASH cols (1)-(4) and UncResCEO cols (5)-(12) share the SAME canonical eq-(14);
PSM cols re-estimate it weighted on the 3-NN-with-replacement matched sub-panel
(OUR extension — Campello's PSM/Table C.3 is on investment/employment/R&D/
divestitures, not cash or uncertainty). Binary cols (9)-(12) use an LPM on
1[UncResCEO ≥ pooled per-arm median]. Campello benchmarks CASH only (13-14).

Writes docs/Draft/_campello_rebuild_t8.tex (\\input by thesis_tables.tex).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "Draft" / "_campello_rebuild_t8.tex"
BREXIT_SUITE = "h1_5_brexit_did"               # CASH DV (both arms)
PSM_SUITE = "h1_5_brexit_did_psm"              # CASH DV, PSM-matched (both arms)
UNC_EXT_SUITE = "h1_5_brexit_did_uncres_ext"   # UncResCEO full grid (8 cells)

LABEL = {
    "POST_x_HIGH": r"POST\_x\_HIGH",
    "brexit_stock_return": r"brexit\_stock\_return",
    "brexit_tobins_q": r"brexit\_tobins\_q",
    "brexit_cash_flow": r"brexit\_cash\_flow",
    "brexit_sales_growth": r"brexit\_sales\_growth",
    "log_assets": r"log\_assets",
    "cons_fwd": r"cons\_fwd",
}
FIRM_ORDER = ["brexit_stock_return", "brexit_tobins_q",
              "brexit_cash_flow", "brexit_sales_growth"]
# the 12 rebuild data columns (everything except the 2 Campello benchmark cols)
KEYS = ["cb", "c7", "pb", "p7",
        "ucnb", "ucnt", "ucpb", "ucpt",
        "ubnb", "ubnt", "ubpb", "ubpt"]
ONE_TAIL = {"cb", "c7", "pb", "p7"}            # CASH one-tailed; UncResCEO two-tailed
PSM_KEYS = {"pb", "p7", "ucpb", "ucpt", "ubpb", "ubpt"}
BIN_KEYS = {"ubnb", "ubnt", "ubpb", "ubpt"}


def _latest_econ(sub: str) -> tuple[dict, str]:
    base = ROOT / "outputs" / "econometric" / sub
    d = sorted(p for p in base.iterdir() if p.is_dir())[-1]
    return json.loads((d / "summary.json").read_text(encoding="utf-8")), d.name


def _stars2(p: float) -> str:
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def _stars1_pos(coef: float, p_two: float) -> str:
    return _stars2(p_two / 2 if coef > 0 else 1 - p_two / 2)


def _cell(coef: float, star: str) -> str:
    body = f"{coef:.4f}{('$^{' + star + '}$') if star else ''}"
    return rf"\textbf{{{body}}}" if star else body


def _r2(x: float) -> str:
    return "0.0000" if abs(x) < 5e-5 else f"{x:.4f}"


def main() -> None:
    s_bx, d_bx = _latest_econ(BREXIT_SUITE)
    s_psm, d_psm = _latest_econ(PSM_SUITE)
    s_ext, d_ext = _latest_econ(UNC_EXT_SUITE)
    r_cb, r_c7 = s_bx["results"][0], s_bx["results"][1]    # CASH unmatched
    r_pb, r_p7 = s_psm["results"][0], s_psm["results"][1]  # CASH PSM
    # UncResCEO full grid: index by (dv_kind, method, arm)
    E = {(r["dv_kind"], r["method"], r["arm"]): r for r in s_ext["results"]}
    ref_b = s_bx["campello_reference_buk"]
    ref_t = s_bx["campello_reference_textual"]

    R = {
        "cb": r_cb, "c7": r_c7, "pb": r_pb, "p7": r_p7,
        "ucnb": E[("cont", "normal", "buk")], "ucnt": E[("cont", "normal", "textual")],
        "ucpb": E[("cont", "psm", "buk")],    "ucpt": E[("cont", "psm", "textual")],
        "ubnb": E[("bin", "normal", "buk")],  "ubnt": E[("bin", "normal", "textual")],
        "ubpb": E[("bin", "psm", "buk")],     "ubpt": E[("bin", "psm", "textual")],
    }
    M = {k: {c["name"]: c for c in R[k]["coefficients"]} for k in KEYS}
    cons = {k: R[k].get("consensus_variant", "cons_fwd") for k in KEYS}

    def delta_cell(k: str) -> str:
        c = M[k]["POST_x_HIGH"]
        st = (_stars1_pos(c["coef"], c["pvalue"]) if k in ONE_TAIL
              else _stars2(c["pvalue"]))
        return _cell(c["coef"], st)

    def yn_row(label: str, flag) -> str:
        cells = " & ".join("Yes" if flag(k) else "No" for k in KEYS)
        return rf"{label} & {cells} & No & No \\"

    L: list[str] = []
    ap = L.append
    ap(r"% AUTO-GENERATED by scripts/campello_rebuild/gen_thesis_t8_table.py")
    ap(rf"% sources: econometric/{BREXIT_SUITE}/{d_bx} + "
       rf"{PSM_SUITE}/{d_psm} + {UNC_EXT_SUITE}/{d_ext}")
    ap(rf"% generated: {datetime.now().isoformat(timespec='seconds')} "
       r"— DO NOT EDIT BY HAND")
    ap(r"\begin{table}[htbp]")
    ap(r"\centering")
    ap(r"\caption{Campello Brexit Replication Suite}")
    ap(r"\label{tab:h1_5_brexit_did}")
    ap(r"\scriptsize")
    ap(r"\setlength{\tabcolsep}{2pt}")
    ap(r"\begin{tabular}{l*{14}{c}}")
    ap(r"\toprule")
    ap(r" & \multicolumn{2}{c}{CASH (eq.~14)} "
       r"& \multicolumn{2}{c}{CASH (PSM)} "
       r"& \multicolumn{2}{c}{UncRes} "
       r"& \multicolumn{2}{c}{UncRes (PSM)} "
       r"& \multicolumn{2}{c}{UncRes$_{\geq m}$} "
       r"& \multicolumn{2}{c}{UncRes$_{\geq m}$ (PSM)} "
       r"& \multicolumn{2}{c}{Campello T.8} \\")
    ap(r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}"
       r"\cmidrule(lr){8-9}\cmidrule(lr){10-11}\cmidrule(lr){12-13}"
       r"\cmidrule(lr){14-15}")
    ap(r" & " + " & ".join(f"({i})" for i in range(1, 15)) + r" \\")
    # arm sub-headers: βᵁᴷ / textual repeated for the 6 rebuild groups, then Campello
    ap(r" & " + " & ".join([r"$\beta^{UK}$", "textual"] * 6
                           + ["col.~1", "col.~2"]) + r" \\")
    ap(r" & " + " & ".join(["tercile", r"Item~1$+$7"] * 6
                           + ["col.~1", "col.~2"]) + r" \\")
    ap(r"\midrule")

    # δ̂ (POST × HIGH) row + SE row
    ap(rf"{LABEL['POST_x_HIGH']} & "
       + " & ".join(delta_cell(k) for k in KEYS)
       + rf" & {_cell(ref_b['cash_delta'], ref_b.get('stars', ''))} "
       rf"& {_cell(ref_t['cash_delta'], ref_t.get('stars', ''))} \\")
    ap(r" & " + " & ".join(f"({M[k]['POST_x_HIGH']['se']:.4f})" for k in KEYS)
       + rf" & ({ref_b['se']:.4f}) & ({ref_t['se']:.4f}) \\")
    ap(r"\midrule")

    # control coefficient rows (Campello reports none → n.r.)
    for nm in FIRM_ORDER + ["__LOGA__", "__CONS__"]:
        if nm == "__LOGA__":
            lbl = LABEL["log_assets"]
            E_ = {k: (M[k].get("log_assets") or M[k].get("log_assets_l1")) for k in KEYS}
        elif nm == "__CONS__":
            lbl = LABEL["cons_fwd"]
            E_ = {k: M[k][cons[k]] for k in KEYS}
        else:
            lbl = LABEL[nm]
            E_ = {k: M[k][nm] for k in KEYS}
        ap(rf"{lbl} & "
           + " & ".join(_cell(E_[k]["coef"], _stars2(E_[k]["pvalue"])) for k in KEYS)
           + r" & n.r. & n.r. \\")
        ap(r" & " + " & ".join(f"({E_[k]['se']:.4f})" for k in KEYS) + r" & & \\")
    ap(r"\midrule")

    ap(r"Firm FE & " + " & ".join(["Yes"] * 14) + r" \\")
    ap(r"Ind.(FIC100)$\times$qtr FE & " + " & ".join(["Yes"] * 14) + r" \\")
    ap(yn_row(r"PSM (3-NN, w/ repl.)", lambda k: k in PSM_KEYS))
    ap(yn_row(r"Binary DV $\mathbf{1}$[UncRes$\geq$med]", lambda k: k in BIN_KEYS))
    ap(r"\midrule")
    ap(r"N & " + " & ".join(f"{R[k]['nobs']:,}" for k in KEYS)
       + rf" & {ref_b['n']:,} & {ref_t['n']:,} \\")
    ap(r"Firms & " + " & ".join(f"{R[k]['n_firms']:,}" for k in KEYS)
       + r" & n.r. & n.r. \\")
    ap(r"$R^2$ & "
       + " & ".join(_r2(R[k]["rsquared_within"]) + r"$^{\ddagger}$" for k in KEYS)
       + rf" & {ref_b['rsquared']:.2f}$^{{\dagger}}$ "
       rf"& {ref_t['rsquared']:.2f}$^{{\dagger}}$ \\")
    ap(r"\bottomrule")
    ap(r"\end{tabular}")
    ap(r"\begin{minipage}{\linewidth}")
    ap(r"\vspace{2pt}\scriptsize")
    ap(r"\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$; "
       r"CASH columns (1)--(4) one-tailed, UncResCEO columns (5)--(12) two-tailed; "
       r"significant coefficients in \textbf{bold}. Standard errors "
       r"(parentheses) double-clustered firm $\times$ calendar-quarter. "
       r"\textbf{UncRes} $=$ UncResCEO (DWZ Eq.4 CEO Q\&A residual, firm-quarter mean); "
       r"\textbf{UncRes$_{\geq m}$} $=$ $\mathbf{1}$[UncResCEO $\geq$ pooled per-arm "
       r"median] (LPM). \textbf{(PSM)} columns re-estimate eq-(14) weighted on the "
       r"3-NN-with-replacement propensity-matched sub-panel (our extension; Campello "
       r"match investment/R\&D/divestitures, not cash or uncertainty). "
       r"$^{\ddagger}$within-$R^2$; $^{\dagger}$Campello reported $R^2$.")
    ap(r"\end{minipage}")
    ap(r"\end{table}")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"sources: {d_bx} | {d_psm} | {d_ext}")
    print(f"written: {OUT}")
    tags = {"cb": "CASH βᵁᴷ", "c7": "CASH txt", "pb": "PSM βᵁᴷ", "p7": "PSM txt",
            "ucnb": "Unc βᵁᴷ", "ucnt": "Unc txt", "ucpb": "UncPSM βᵁᴷ",
            "ucpt": "UncPSM txt", "ubnb": "Bin βᵁᴷ", "ubnt": "Bin txt",
            "ubpb": "BinPSM βᵁᴷ", "ubpt": "BinPSM txt"}
    for k in KEYS:
        c = M[k]["POST_x_HIGH"]
        print(f"  {tags[k]:<12} δ̂ {c['coef']:+.4f} ({c['se']:.4f}) N {R[k]['nobs']:,}")
    print(f"  Campello βᵁᴷ {ref_b['cash_delta']:+.3f}{ref_b.get('stars','')} | "
          f"txt {ref_t['cash_delta']:+.3f}{ref_t.get('stars','')}")


if __name__ == "__main__":
    main()
