"""
Materiality GRADING test (supervisor artifact -- NOT in the thesis).
Answers FLAG 1 (§2.1): is the disclosure bind GRADED with materiality, or binary?

Materiality = Basic (1988) "magnitude to the firm" = relative deal size.
  Rel    = DealValue / acquirer assets (assets in the pre-announcement quarter)
  lnMag  = ln(Rel), winsorized 1/99 (matches thesis control winsorization)

Round-trip event study (mirrors Table 5.3/5.4) with each event-window dummy
INTERACTED with lnMag:

  UncResCEO_it = Sum_b [ b_bin*Bin + d_bin*(Bin x lnMag) ] + g'X + firm FE + qtr FE

Read (advisor-locked):
  d_PRE1 > 0  : pre-announce run-up SCALES with deal materiality (grading)
  d_GAP  ~ 0  : the size-scaled excess RESOLVES at announcement (the bind, not scrutiny)
  HEADLINE Wald: d_PRE1 - d_GAP > 0   (within-firm; cancels small-firm noise + scrutiny,
                 which lands in GAP and biases the contrast AGAINST us -> conservative)
lnMag main effect is firm-constant -> absorbed by firm FE (only interactions enter).
Two samples: ALL payment types (primary) + CASH>=50 (secondary).

Convention: compute -> summary.json -> write_tex(json) -> .tex.
"""
import glob, importlib.util, json
import numpy as np, pandas as pd, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy.stats import norm

ROOT = Path(".").resolve()
def _imp(n, rel):
    sp = importlib.util.spec_from_file_location(n, ROOT/rel); md = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(md); return md
edt = _imp("edt", "src/f1d/econometric/empire_drop_test.py")
BINS, CTRL = edt.BINS, edt.CTRL
IBINS = ["i"+b for b in BINS]

p = edt.base_panel(); s = edt.sdc(); m = edt.manifest()
p["assets"] = np.exp(p["lnAssets"])                                  # $M, same units as DealValue
raw = pd.read_parquet(ROOT/"inputs"/"SDC"/"sdc-ma-merged.parquet",
        columns=["Acquiror 6-digit CUSIP", "Date Announced", "Deal Value (USD Millions)"]).rename(
        columns={"Acquiror 6-digit CUSIP": "c6", "Deal Value (USD Millions)": "dv"})
raw["da"] = pd.to_datetime(raw["Date Announced"], errors="coerce")
s = s.reset_index(drop=True); s["dv"] = raw["dv"].values; s["dq"] = edt._qtr(s["da"])


def lnmag_map(mask):
    """gvkey -> ln(DealValue/assets) for each firm's FIRST qualifying deal, winsorized 1/99."""
    cd = s[s["known"] & mask].copy().merge(m, on="c6", how="inner").sort_values("da")
    cd["rank"] = cd.groupby("c6").cumcount()
    first = cd[cd["rank"] == 0]
    pa = p[["gvkey", "cq", "assets"]].copy(); pa["cq"] = pa["cq"] + 1     # assets at dq-1
    j = first.merge(pa, left_on=["gvkey", "dq"], right_on=["gvkey", "cq"], how="inner")
    j = j[(j["dv"] > 0) & (j["assets"] > 0)].copy()
    j["lnmag"] = np.log(j["dv"] / j["assets"])
    lo, hi = j["lnmag"].quantile([.01, .99]); j["lnmag"] = j["lnmag"].clip(lo, hi)
    j["lnmag"] = j["lnmag"] - j["lnmag"].mean()         # MEAN-CENTER: bin main effect = run-up at AVERAGE deal size
    return dict(zip(j["gvkey"], j["lnmag"]))


def one(par, se, pv, name):
    return {"b": float(par[name]), "se": float(se[name]),
            "p2": float(pv[name]), "p1": float(pv[name]/2 if par[name] > 0 else 1-pv[name]/2)}


POST_CAP = edt.POST_CAP


def fit(q):
    """Estimate UncRes ~ bins + bins x lnMag + controls + firm/qtr FE; return coef dict + Wald."""
    need = ["UncResCEO"] + BINS + IBINS + CTRL
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    n_firms = int(d["gvkey"].nunique())
    dd = d.set_index(["gvkey", "cq"])
    f = ("UncResCEO ~ 1 + " + " + ".join(BINS + IBINS + CTRL) + " + EntityEffects + TimeEffects")
    mod = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov

    def wald(i, j):
        diff = float(par[i] - par[j]); var = float(V.loc[i, i] + V.loc[j, j] - 2*V.loc[i, j])
        sd = var**0.5 if var > 0 else float("nan"); t = diff/sd if sd == sd and sd > 0 else float("nan")
        p2 = 2*norm.sf(abs(t)) if t == t else float("nan")
        return {"diff": diff, "se": sd, "t": t, "p2": p2,
                "p1": (p2/2 if diff > 0 else 1-p2/2) if p2 == p2 else float("nan")}
    return {"beta": {b: one(par, se, pv, b) for b in BINS if b in par.index},
            "delta": {b: one(par, se, pv, "i"+b) for b in BINS if "i"+b in par.index},
            "wald_pre1_gap": wald("iPRE1", "iGAP"), "wald_pre1_post": wald("iPRE1", "iPOST"),
            "controls": {c: one(par, se, pv, c) for c in CTRL if c in par.index},
            "n": int(mod.nobs), "n_firms": n_firms}


def run_fd(mask):
    """FIRST-DEAL clock: each firm's first qualifying deal sets the event window."""
    q, _ = edt.build_event(p, s, m, mask)
    lm = lnmag_map(mask)
    q = q.copy(); q["lnMag"] = q["gvkey"].map(lm)
    for b in BINS:
        q["i"+b] = q[b] * q["lnMag"].fillna(0.0)
    treated_row = q[BINS].sum(axis=1) > 0
    q = q[~(treated_row & q["lnMag"].isna())].copy()
    return fit(q)


def deals_with_rel(mask):
    """Per-firm list of (dq, ceq, wq, status, lnMag) for EVERY qualifying deal (stacked design).
    lnMag is per-DEAL (DealValue/assets at that deal's pre-quarter), winsorized 1/99, mean-centered."""
    cd = s[s["known"] & mask].copy().merge(m, on="c6", how="inner")
    cd["dq"] = edt._qtr(cd["da"]); cd["ceq"] = edt._qtr(cd["de"]); cd["wq"] = edt._qtr(cd["dw"])
    cd.loc[cd["ceq"] < cd["dq"], "ceq"] = np.nan
    pa = p[["gvkey", "cq", "assets"]].copy(); pa["cq"] = pa["cq"] + 1        # assets at dq-1
    cd = cd.merge(pa, left_on=["gvkey", "dq"], right_on=["gvkey", "cq"], how="left")
    cd = cd[(cd["dv"] > 0) & (cd["assets"] > 0)].copy()
    cd["lnmag"] = np.log(cd["dv"] / cd["assets"])
    lo, hi = cd["lnmag"].quantile([.01, .99]); cd["lnmag"] = cd["lnmag"].clip(lo, hi)
    cd["lnmag"] = cd["lnmag"] - cd["lnmag"].mean()
    D = {}
    for g, dq, ceq, wq, stt, lr in zip(cd["gvkey"], cd["dq"], cd["ceq"], cd["wq"], cd["status"], cd["lnmag"]):
        D.setdefault(g, []).append((int(dq), (None if pd.isna(ceq) else int(ceq)),
                                    (None if pd.isna(wq) else int(wq)), stt, float(lr)))
    return D


def claim_rel(cq, deal):
    dq, ceq, wq, stt, lr = deal; e = cq - dq
    if e == -2: return ("PRE2", lr)
    if e == -1: return ("PRE1", lr)
    if 0 <= e <= POST_CAP:
        if stt == "Withdrawn" and wq is not None and cq >= wq: return None
        return ("POST", lr) if (ceq is not None and cq >= ceq) else ("GAP", lr)
    return None


def run_stacked(mask):
    """ALL-DEALS clock: every deal is its own event; firm-qtr claimed by 2+ windows dropped;
    baseline dropped on/after any deal's COMPLETION. Each event-qtr carries its own deal's lnMag."""
    D = deals_with_rel(mask)
    cls, lrs = [], []
    for g, cq in zip(p["gvkey"], p["cq"]):
        cl = [c for c in (claim_rel(cq, dl) for dl in D.get(g, [])) if c]
        if len(cl) == 1: cls.append(cl[0][0]); lrs.append(cl[0][1])
        elif len(cl) >= 2: cls.append("DROP"); lrs.append(0.0)
        elif any(dl[1] is not None and cq >= dl[1] for dl in D.get(g, [])): cls.append("DROP"); lrs.append(0.0)
        else: cls.append("BASE"); lrs.append(0.0)
    q = p.copy(); q["cls"] = cls; q["lnMag"] = lrs
    q = q[q["cls"] != "DROP"].copy()
    for b in BINS:
        q[b] = (q["cls"] == b).astype(float); q["i"+b] = q[b] * q["lnMag"]
    return fit(q)


ALLm = pd.Series(True, index=s.index); CASHm = s["pc"] >= 50
res = {"FD_ALL": run_fd(ALLm), "FD_CASH": run_fd(CASHm),
       "AD_ALL": run_stacked(ALLm), "AD_CASH": run_stacked(CASHm)}
_dirs = [d for d in glob.glob(str(ROOT/"outputs/econometric/firstdeal_robustness/*/")) if Path(d).is_dir()]
out = Path(sorted(_dirs)[-1])
(out/"materiality_grading_summary.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

print("=== Materiality GRADING (event study x lnMag) ===")
for k, r in res.items():
    print(f"\n[{k}] N={r['n']:,} firms={r['n_firms']}  "
          f"bPRE1={r['beta']['PRE1']['b']:+.4f}(p{r['beta']['PRE1']['p2']:.3f})")
    w = r["wald_pre1_gap"]
    print(f"  dPRE1={r['delta']['PRE1']['b']:+.4f}  dGAP={r['delta']['GAP']['b']:+.4f}  "
          f"HEADLINE dPRE1-dGAP={w['diff']:+.4f} (se {w['se']:.4f}, p2 {w['p2']:.3f})")
print("\nwrote", out/"materiality_grading_summary.json")

# ---------- write_tex(json): thesis-format table (supervisor artifact) ----------
J = json.loads((out/"materiality_grading_summary.json").read_text(encoding="utf-8"))
def st(p): return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))
def C(b, p):
    sg = st(p); return (r"\textbf{"+f"{b:.4f}"+r"}$^{"+sg+r"}$") if sg else f"{b:.4f}"
COLS = [("FD_ALL", "All"), ("FD_CASH", "Cash"), ("AD_ALL", "All"), ("AD_CASH", "Cash")]
LB = {"PRE2": r"PRE2 ($t{-}2$)", "PRE1": r"PRE1 ($t{-}1$)",
      "GAP": r"GAP (announced)", "POST": r"POST (completed)"}
def row(label, getter):
    return f"{label} & " + " & ".join(getter(J[k]) for k, _ in COLS) + r" \\"
L = [r"\documentclass[11pt]{article}",
     r"\usepackage[letterpaper,margin=0.8in]{geometry}\usepackage{newtxtext,newtxmath}\usepackage{booktabs,amsmath,float}",
     r"\begin{document}\pagestyle{empty}",
     r"\begin{table}[H]\centering",
     r"\caption{Materiality Grading: Pre-Announcement Run-Up by Relative Deal Size}",
     r"\small\begin{tabular}{lcccc}",
     r"\toprule",
     r" & \multicolumn{2}{c}{\textbf{First deal}} & \multicolumn{2}{c}{\textbf{All deals (stacked)}} \\",
     r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
     r" & " + " & ".join(c for _, c in COLS) + r" \\",
     r"\midrule",
     r"\multicolumn{5}{l}{\textit{Event-window main effects }$\beta_{\mathrm{bin}}$} \\"]
for b in BINS:
    L.append(row(LB[b], lambda r, b=b: C(r["beta"][b]["b"], r["beta"][b]["p2"])))
    L.append(row("", lambda r, b=b: f"({r['beta'][b]['se']:.4f})"))
L.append(r"\midrule")
L.append(r"\multicolumn{5}{l}{\textit{Materiality interactions }$\delta_{\mathrm{bin}}=\,$bin$\times\ln(\text{Mag})$} \\")
for b in BINS:
    L.append(row(LB[b] + r"$\,\times\ln$Mag", lambda r, b=b: C(r["delta"][b]["b"], r["delta"][b]["p2"])))
    L.append(row("", lambda r, b=b: f"({r['delta'][b]['se']:.4f})"))
L.append(r"\midrule")
L.append(row(r"Drop: PRE1 $-$ GAP",
             lambda r: C(r["wald_pre1_gap"]["diff"], r["wald_pre1_gap"]["p2"])))
L.append(row("", lambda r: f"({r['wald_pre1_gap']['se']:.4f})"))
L.append(r"\midrule")
L.append(row("Firm FE / Year-Qtr FE / Controls", lambda r: "Yes"))
L.append(row("N (firm-quarters)", lambda r: f"{r['n']:,}"))
L.append(row("Firms", lambda r: f"{r['n_firms']:,}"))
L += [r"\bottomrule\end{tabular}",
      r"\begin{minipage}{\linewidth}\vspace{3pt}\footnotesize\textit{Notes:} Standard errors clustered by firm "
      r"in parentheses. $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed).\end{minipage}",
      r"\end{table}", r"\end{document}"]
(out/"materiality_grading.tex").write_text("\n".join(L), encoding="utf-8")
print("wrote", out/"materiality_grading.tex")
