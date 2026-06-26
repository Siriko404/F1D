"""Two separate cash-gate logit tables (columns = (1) LPM, (2) Logit; UncResCEO + all controls
as rows), each with a plain, readable DV header. Reads logit_fullcontrols_results.json."""
import json
from pathlib import Path

FORK = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3")
J = json.loads((FORK / "tmp" / "logit_fullcontrols_results.json").read_text(encoding="utf-8"))
CTRL = J["controls"]


def stars(p): return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))
def cell(d):
    s = stars(d["p2"]); body = f"{d['beta']:.4f}"
    return (r"\textbf{" + body + r"}$^{" + s + r"}$") if s else body
def se(d): return f"({d['se']:.4f})"


def table_tex(caption, label, dv_head, dv_sub, blk):
    lpm, log = blk["lpm"], blk["logit"]
    L = [r"\begin{table}[htbp]\centering",
         rf"\caption{{{caption}}}", rf"\label{{{label}}}",
         r"\small\begin{tabular}{lcc}", r"\toprule",
         rf" & \multicolumn{{2}}{{c}}{{\textbf{{{dv_head}}}}} \\",
         rf" & \multicolumn{{2}}{{c}}{{\scriptsize {dv_sub}}} \\",
         r"\cmidrule(lr){2-3}",
         r" & (1) LPM & (2) Logit \\", r"\midrule",
         r"UncResCEO & " + cell(lpm["key"]) + " & " + cell(log["key"]) + r" \\",
         r" & " + se(lpm["key"]) + " & " + se(log["key"]) + r" \\", r"\midrule"]
    for c in CTRL:
        L.append(f"{c} & " + cell(lpm["ctrls"][c]) + " & " + cell(log["ctrls"][c]) + r" \\")
        L.append(r" & " + se(lpm["ctrls"][c]) + " & " + se(log["ctrls"][c]) + r" \\")
    L += [r"\midrule",
          f"$N$ & {lpm['n']:,} & {log['n']:,}" + r" \\",
          f"Firms & {lpm['n_firms']:,} & {log['n_firms']:,}" + r" \\",
          rf"$R^2$ / Pseudo-$R^2$ & {lpm['r2']:.3f} & {log['pseudo_r2']:.3f}" + r" \\",
          r"\bottomrule\end{tabular}",
          r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} "
          r"Col.\ (1) is a linear probability model; col.\ (2) a logit (raw log-odds coefficients). "
          r"UncResCEO is the only CEO-speech regressor; all controls shown. No fixed effects; "
          r"standard errors (parentheses) clustered by firm; significant coefficients in \textbf{bold}. "
          r"$^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed).\end{minipage}",
          r"\end{table}"]
    return "\n".join(L)


tA = table_tex(r"Logit A --- CEO Q\&A Uncertainty Predicts a Deal Next Quarter",
               "tab:logit_dealnext", "Deal next quarter",
               r"$=1$ if a deal (any payment type) is announced in the next quarter",
               J["TEST_A"])
tB = table_tex(r"Logit B --- Among Deals, CEO Q\&A Uncertainty Predicts Cash vs.\ Stock",
               "tab:logit_cashstock", "Cash deal",
               r"$=1$ if cash-financed, $0$ if stock-financed (deals only)",
               J["TEST_B"])

doc = "\n".join([
    r"\documentclass[11pt]{article}",
    r"\usepackage[letterpaper,margin=0.9in]{geometry}",
    r"\usepackage{newtxtext,newtxmath}\usepackage{booktabs,amsmath,float}",
    r"\begin{document}\pagestyle{empty}",
    tA, r"\clearpage", tB,
    r"\end{document}",
])
texp = FORK / "tmp" / "logit_tables_final.tex"
texp.write_text(doc, encoding="utf-8")
print("wrote", texp)
