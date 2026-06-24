import json, glob
from pathlib import Path
ROOT = Path(".").resolve()

def latest(p): return sorted(glob.glob(str(ROOT/p)))[-1]
def J(p): return json.load(open(p, encoding="utf-8"))

# sources (all from json specs)
th_run  = J(latest("outputs/econometric/empire_building_did/*/summary.json"))["results"]
th_cash = J(latest("outputs/econometric/empire_cashspec/*/summary.json"))
ad_dir  = Path(latest("outputs/econometric/firstdeal_robustness/*/summary_runup.json")).parent
ad_run  = J(ad_dir/"summary_runup.json")
ad_cash = J(ad_dir/"summary_cashspec.json")

CTRL = ["Leverage","lnAssets","TobinsQ","ROA","Capex","DivDummy","sCFO"]
DVS  = ["CashRatio","UncResCEO","CashScrutiny","HighCashScrutiny"]
def st(p): return "***" if p<.01 else ("**" if p<.05 else ("*" if p<.10 else ""))
def C(b,p):
    s=st(p)
    return (r"\textbf{" + f"{b:.4f}" + r"}$^{" + s + r"}$") if s else f"{b:.4f}"

# ---------- RUN-UP merged (thesis 8 cols + all-deals 8 cols) ----------
def run_cells(src, arm, dv, field):
    r = src[f"{arm}:{dv}"]
    return r if field=="row" else r
def runrow(label, getter):
    cells=[]
    for src in (th_run, ad_run):
        for arm in ("cash","stock"):
            for dv in DVS:
                cells.append(getter(src[f"{arm}:{dv}"]))
    return label + " & " + " & ".join(cells) + r" \\"

ncol=16
run=[r"\begin{table}[H]\centering",
     r"\caption{Pre-Announcement Run-Up: Thesis (first deal) vs.\ All Deals (stacked)}\label{tab:rb_runup_merged}",
     r"\scriptsize\begin{adjustbox}{max width=\linewidth}",
     r"\begin{tabular}{l"+"c"*ncol+"}",
     r"\toprule",
     r" & \multicolumn{8}{c}{\textbf{Thesis (first deal)}} & \multicolumn{8}{c}{\textbf{All deals (stacked)}} \\",
     r"\cmidrule(lr){2-9}\cmidrule(lr){10-17}",
     r" & \multicolumn{4}{c}{Cash} & \multicolumn{4}{c}{Stock} & \multicolumn{4}{c}{Cash} & \multicolumn{4}{c}{Stock} \\",
     r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}\cmidrule(lr){14-17}",
     r" & " + " & ".join([r"CshR",r"UncR",r"CshScr",r"HiScr"]*4) + r" \\",
     r"\midrule",
     runrow("PreAnnounceQtr", lambda r: C(r["beta"], r["p2"])),
     runrow("", lambda r: f"({r['se']:.4f})"),
     r"\midrule"]
for ct in CTRL:
    run.append(runrow(ct, lambda r,ct=ct: C(r["ctrls"][ct]["beta"], r["ctrls"][ct]["p2"]) if ct in r.get("ctrls",{}) else "---"))
    run.append(runrow("", lambda r,ct=ct: f"({r['ctrls'][ct]['se']:.4f})" if ct in r.get("ctrls",{}) else ""))
run += [r"\midrule",
        runrow("Firms", lambda r: f"{r['n_firms']:,}"),
        runrow("N", lambda r: f"{r['n']:,}"),
        r"\bottomrule\end{tabular}\end{adjustbox}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE clustered by firm in parentheses; significant coefficients in \textbf{bold}. Columns: CshR=CashRatio (with one-quarter lag), UncR=UncResCEO, CshScr=CashScrutiny, HiScr=HighCashScrutiny. Left block = thesis first-deal design (Table 5.2); right block = every cash/stock deal stacked, dropping run-ups contaminated by a same-arm deal in the prior 3 quarters and a 3-quarter aftermath.\end{minipage}",
        r"\end{table}"]

# ---------- CASH-SPEC merged (thesis 3 cols + all-deals 3 cols) ----------
def cs_cell(src, dvkey, rowkey, sub):
    r = src["results"][dvkey]
    if rowkey=="wald": return (C(r["wald"]["diff"], r["wald"]["p2"]) if sub=="b" else f"({r['wald']['se']:.4f})")
    return (C(r[rowkey]["b"], r[rowkey]["p2"]) if sub=="b" else f"({r[rowkey]['se']:.4f})")
cols=["UncResCEO","CashRatio_matched","CashRatio_full"]
def csrow(label, rowkey):
    cells=[]
    for src in (th_cash, ad_cash):
        for c in cols: cells.append(cs_cell(src,c,rowkey,"b"))
    return label+" & "+" & ".join(cells)+r" \\"
def csse(rowkey):
    cells=[]
    for src in (th_cash, ad_cash):
        for c in cols: cells.append(cs_cell(src,c,rowkey,"se"))
    return " & "+" & ".join(cells)+r" \\"
cs=[r"\begin{table}[H]\centering",
    r"\caption{Formal Cash-Specificity: Thesis (matched) vs.\ All Deals (stacked)}\label{tab:rb_cashspec_merged}",
    r"\scriptsize\begin{adjustbox}{max width=\linewidth}",
    r"\begin{tabular}{lcccccc}",
    r"\toprule",
    r" & \multicolumn{3}{c}{\textbf{Thesis (matched)}} & \multicolumn{3}{c}{\textbf{All deals (stacked)}} \\",
    r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
    r" & UncRes & CashR(m) & CashR(f) & UncRes & CashR(m) & CashR(f) \\",
    r"\midrule",
    csrow("Pre-announce qtr, Cash","cash"), csse("cash"),
    csrow("Pre-announce qtr, Stock","stock"), csse("stock"),
    r"\midrule",
    csrow("Cash $-$ Stock (Wald)","wald"), csse("wald"),
    r"\bottomrule\end{tabular}\end{adjustbox}",
    r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed). UncRes=UncResCEO (effect); CashR(m)=CashRatio matched +lag; CashR(f)=CashRatio full panel +lag (proposed cause). Left = thesis Table 5.5; right = all stacked deals.\end{minipage}",
    r"\end{table}"]

# ---------- TABLE 3: POOLED run-up (UncResCEO), the coefs that feed the Wald ----------
def p_uncr(src, rk, sub):
    r = src["results"]["UncResCEO"]
    if rk=="wald": return (C(r["wald"]["diff"], r["wald"]["p2"]) if sub=="b" else f"({r['wald']['se']:.4f})")
    return (C(r[rk]["b"], r[rk]["p2"]) if sub=="b" else f"({r[rk]['se']:.4f})")
def p3row(label, rk):
    return label+" & "+" & ".join([p_uncr(th_cash,rk,"b"), p_uncr(ad_cash,rk,"b")])+r" \\"
def p3se(rk):
    return " & "+" & ".join([p_uncr(th_cash,rk,"se"), p_uncr(ad_cash,rk,"se")])+r" \\"
p3=[r"\begin{table}[H]\centering",
    r"\caption{Pooled Run-Up (UncResCEO): cash \& stock in ONE regression --- these are the coefficients the Wald uses. Thesis (matched) vs.\ All Deals (stacked)}\label{tab:rb_pooled_runup}",
    r"\scriptsize\begin{tabular}{lcc}",
    r"\toprule",
    r" & Thesis (matched) & All deals (stacked) \\",
    r"\midrule",
    p3row(r"Pre-announce qtr, Cash ($\beta_c$)","cash"), p3se("cash"),
    p3row(r"Pre-announce qtr, Stock ($\beta_s$)","stock"), p3se("stock"),
    r"\midrule",
    p3row(r"Cash $-$ Stock (Wald, $\beta_c-\beta_s$)","wald"), p3se("wald"),
    r"\bottomrule\end{tabular}",
    r"\begin{minipage}{0.8\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE in parentheses. Cash and stock estimated jointly (pooled), so the Wald is exactly $\beta_c-\beta_s$ from this same regression ($0.0459-(-0.0524)=0.0983$ thesis; $0.0394-(-0.0237)=0.0631$ all-deals). NOTE: the pooled cash coefficient ($0.0459$) differs slightly from the single-arm run-up ($0.0461$, Table 1) because it is a different, joint, matched-sample regression --- the joint estimation is required to get a valid standard error for the difference.\end{minipage}",
    r"\end{table}"]

doc=[r"\documentclass[12pt]{article}",
     r"\usepackage[letterpaper,margin=0.6in,landscape]{geometry}",
     r"\usepackage{newtxtext,newtxmath}\usepackage{booktabs,amsmath,adjustbox,float}",
     r"\begin{document}",
     r"\begin{center}{\large\textbf{First-Deal vs.\ All-Deals robustness}}\ \small supervisor artifact --- not in the thesis\end{center}\vspace{6pt}",
     "\n".join(run), r"\vspace{10pt}", "\n".join(cs), r"\vspace{10pt}", "\n".join(p3),
     r"\end{document}"]
outp = ad_dir/"robustness_merged.tex"
outp.write_text("\n".join(doc), encoding="utf-8")
print("wrote", outp)
