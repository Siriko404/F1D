# -*- coding: utf-8 -*-
"""Logit tables with a 3rd column: (1) LPM (2) Logit (3) LPM+FE. Reads
logit_fullcontrols_results.json (LPM+Logit) + fe_results.json (FE). Overwrites logit_tables_final.tex.
Logit-FE is infeasible (perfect separation) -> the FE column is LPM only, with an explicit FE row."""
import json
from pathlib import Path
FORK = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3")
J  = json.loads((FORK/"tmp"/"logit_fullcontrols_results.json").read_text(encoding="utf-8"))
FE = json.loads((FORK/"tmp"/"fe_results.json").read_text(encoding="utf-8"))
CTRL = J["controls"]
def stars(p): return "***" if p<.01 else ("**" if p<.05 else ("*" if p<.10 else ""))
def cell(d):
    s=stars(d["p2"]); body=f"{d['beta']:.4f}"
    return (r"\textbf{"+body+r"}$^{"+s+r"}$") if s else body
def se(d): return f"({d['se']:.4f})"

def table_tex(caption, label, dv_head, dv_sub, jblk, feblk):
    lpm, log, fe = jblk["lpm"], jblk["logit"], feblk
    L = [r"\begin{table}[htbp]\centering",
         rf"\caption{{{caption}}}", rf"\label{{{label}}}",
         r"\small\begin{tabular}{lccc}", r"\toprule",
         rf" & \multicolumn{{3}}{{c}}{{\textbf{{{dv_head}}}}} \\",
         rf" & \multicolumn{{3}}{{c}}{{\scriptsize {dv_sub}}} \\",
         r"\cmidrule(lr){2-4}",
         r" & (1) LPM & (2) Logit & (3) LPM + FE \\", r"\midrule",
         r"UncResCEO & " + cell(lpm["key"]) + " & " + cell(log["key"]) + " & " + cell(fe["key"]) + r" \\",
         r" & " + se(lpm["key"]) + " & " + se(log["key"]) + " & " + se(fe["key"]) + r" \\", r"\midrule"]
    for c in CTRL:
        L.append(f"{c} & " + cell(lpm["ctrls"][c]) + " & " + cell(log["ctrls"][c]) + " & " +
                 (cell(fe["ctrls"][c]) if c in fe.get("ctrls",{}) else "---") + r" \\")
        L.append(r" & " + se(lpm["ctrls"][c]) + " & " + se(log["ctrls"][c]) + " & " +
                 (se(fe["ctrls"][c]) if c in fe.get("ctrls",{}) else "") + r" \\")
    L += [r"\midrule",
          r"Firm + Year-Qtr FE & No & No & Yes \\",
          f"$N$ & {lpm['n']:,} & {log['n']:,} & {fe['n']:,}" + r" \\",
          f"Firms & {lpm['n_firms']:,} & {log['n_firms']:,} & {fe['n_firms']:,}" + r" \\",
          rf"$R^2$ / Pseudo-$R^2$ & {lpm['r2']:.3f} & {log['pseudo_r2']:.3f} & {fe['r2_within']:.3f}" + r" \\",
          r"\bottomrule\end{tabular}",
          r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} "
          r"Col.\ (1) linear probability model; (2) logit (raw log-odds); (3) LPM adding firm and "
          r"year-quarter fixed effects. A firm-fixed-effects logit is infeasible here (perfect separation: "
          r"the deal/cash base rate leaves most firms with no within-firm outcome variation). "
          r"UncResCEO is the residual CEO Q\&A uncertainty; all controls shown; SEs clustered by firm; "
          r"$^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed).\end{minipage}",
          r"\end{table}"]
    return "\n".join(L)

tA = table_tex(r"Logit A --- CEO Q\&A Uncertainty Predicts a Deal Next Quarter",
               "tab:logit_dealnext", "Deal next quarter",
               r"$=1$ if a deal (any payment type) is announced in the next quarter", J["TEST_A"], FE["TEST_A"])
tB = table_tex(r"Logit B --- Among Deals, CEO Q\&A Uncertainty Predicts Cash vs.\ Stock",
               "tab:logit_cashstock", "Cash deal",
               r"$=1$ if cash-financed, $0$ if stock-financed (deals only)", J["TEST_B"], FE["TEST_B"])
doc = "\n".join([r"\documentclass[11pt]{article}",
                 r"\usepackage[letterpaper,margin=0.9in]{geometry}",
                 r"\usepackage{newtxtext,newtxmath}\usepackage{booktabs,amsmath,float}",
                 r"\begin{document}\pagestyle{empty}", tA, r"\clearpage", tB, r"\end{document}"])
texp = FORK/"tmp"/"logit_tables_final.tex"
texp.write_text(doc, encoding="utf-8")
print("wrote", texp)
print("Logit A FE col: UncResCEO", round(FE["TEST_A"]["key"]["beta"],4), stars(FE["TEST_A"]["key"]["p2"]), "| Logit B FE col:", round(FE["TEST_B"]["key"]["beta"],4), stars(FE["TEST_B"]["key"]["p2"]) or "n.s.")
