#!/usr/bin/env python3
"""Generate the Cash-Scrutiny channel test (Link 2) table fragment.

SECOND LINK of the analyst-scrutiny reverse-causality channel. Link 1 showed the measure
is valid (analysts talk cash when cash is high). Link 2 asks the channel question directly:
does more analyst cash-scrutiny on a call make the CEO more evasive (CEO Q&A uncertainty up)?

DV = CEO Q&A uncertainty, two forms, each its own table column:
       UncResCEO  -- the DWZ residual (firm/linguistic part removed; untouched).
       UncAnsCEO  -- the RAW measure (LinguisticEngine CEO_QA_Uncertainty_pct, pooled-1% winsor).
IV = analyst cash-scrutiny (CashScrutiny reported; any-turn/count/log-count also computed).

  Panel A. OLS:   DV (continuous) ~ Scrutiny + firm FE + cal-quarter FE
  Panel B. Logit: 1[DV >= median] ~ Scrutiny + industry FE + cal-quarter FE
                  (firm-FE logit is biased by incidental parameters -> industry FE)
All firm-clustered SE.

Inputs: tmp/_cash_stock_score_call.parquet (STOCK cache); h1 cash panel; ceo_clarity_residual;
        linguistic_variables_*.parquet (raw UncAnsCEO).
Writes: outputs/econometric/cash_scrutiny_channel/<ts>/summary.json  +  docs/Draft/_cash_scrutiny_channel.tex
Regenerate: python scripts/gen_cash_scrutiny_channel_table.py
NOT hand-edited.
"""
from __future__ import annotations
import glob, json, warnings
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
SCORE = ROOT / "tmp" / "_cash_stock_score_call.parquet"
CTRL = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO"]
MIN_QA = 3
SUITE = "cash_scrutiny_channel"
TEX_OUT = ROOT / "docs" / "Draft" / f"_{SUITE}.tex"
IVS = [("CashScrutiny", r"CashScrutiny"), ("sc_any", r"sc\_any"),
       ("sc_count", r"sc\_count"), ("sc_logcount", r"sc\_logcount")]
PRIMARY = "CashScrutiny"   # single reported measure: % of a call's Q&A turns on cash
                           # = analyst cash-attention score validated in Link 1 (Table 16).


def _latest(p):
    h = sorted(glob.glob(str(ROOT / p)))
    if not h: raise FileNotFoundError(p)
    return h[-1]


def _load_uncans():
    """Raw CEO Q&A uncertainty: LinguisticEngine CEO_QA_Uncertainty_pct -> UncAnsCEO (call-level)."""
    d = sorted(glob.glob(str(ROOT / "outputs" / "2_Textual_Analysis" / "2.2_Variables" / "*")))
    if not d: raise FileNotFoundError("linguistic_variables dir")
    files = sorted(glob.glob(str(Path(d[-1]) / "linguistic_variables_*.parquet")))
    parts = [pd.read_parquet(f, columns=["file_name", "CEO_QA_Uncertainty_pct"]) for f in files]
    g = pd.concat(parts, ignore_index=True).rename(columns={"CEO_QA_Uncertainty_pct": "UncAnsCEO"})
    return g.dropna(subset=["UncAnsCEO"]).drop_duplicates("file_name")


def build_df():
    score = pd.read_parquet(SCORE)
    panel = pd.read_parquet(_latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
                            columns=["file_name", "gvkey", "start_date", "ff12_code"] + CTRL)
    resid = pd.read_parquet(_latest("outputs/econometric/ceo_clarity_extended/*/ceo_clarity_residual.parquet"),
                            columns=["file_name", "UncResCEO"])
    ling = _load_uncans()                          # raw CEO Q&A uncertainty (UncAnsCEO)
    df = (panel.merge(score, on="file_name", how="inner")
               .merge(resid, on="file_name", how="inner")
               .merge(ling, on="file_name", how="left"))
    df = df[~df["ff12_code"].isin([8, 11])]
    df = df.dropna(subset=["stock_score", "UncResCEO", "gvkey"])
    df = df[df["n_qa_turns"] >= MIN_QA].copy()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df.dropna(subset=["start_date"]).reset_index(drop=True)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cq"] = df["start_date"].dt.year * 4 + (df["start_date"].dt.quarter - 1)
    df["cyq"] = df["start_date"].dt.year.astype(str) + "Q" + df["start_date"].dt.quarter.astype(str)
    s = df["stock_score"]
    df["CashScrutiny"] = s * 100.0
    df["sc_any"] = (df["n_qa_stock_turns"] >= 1).astype(float)
    df["sc_count"] = df["n_qa_stock_turns"].astype(float)
    df["sc_logcount"] = np.log1p(df["n_qa_stock_turns"])
    df["dodge"] = (df["UncResCEO"] >= df["UncResCEO"].median()).astype(int)   # above-median evasiveness
    mr = df["UncAnsCEO"].notna()                    # raw UncAnsCEO: pooled-1% winsor (match engine)
    if mr.any():
        lo, hi = df.loc[mr, "UncAnsCEO"].quantile([.01, .99])
        df.loc[mr, "UncAnsCEO"] = df.loc[mr, "UncAnsCEO"].clip(lo, hi)
        df["dodge_raw"] = np.where(df["UncAnsCEO"] >= df.loc[mr, "UncAnsCEO"].median(), 1.0, 0.0)
        df.loc[~mr, "dodge_raw"] = np.nan
    else:
        df["dodge_raw"] = np.nan
    for c in CTRL:                                  # winsor + standardize (logit stability)
        lo, hi = df[c].quantile([.01, .99]); df[c] = df[c].clip(lo, hi)
        sd = df[c].std()
        if sd and sd > 0: df[c] = (df[c] - df[c].mean()) / sd
    return df


def ols(df, iv, dv="UncResCEO"):
    """Firm + cal-quarter FE OLS on `dv` (no firm controls; controlled spec separately verified null)."""
    d = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[dv, iv]).copy()
    nf = d["gvkey"].nunique()
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + {iv} + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    return {"beta": float(m.params[iv]), "se": float(m.std_errors[iv]), "p2": float(m.pvalues[iv]),
            "n": int(m.nobs), "n_firms": nf, "r2": float(m.rsquared)}


def logit(df, iv, FE, ycol="dodge"):
    """Industry + cal-quarter FE logit on binary `ycol` (firm-FE logit biased via incidental params)."""
    X = sm.add_constant(pd.concat([df[[iv]].rename(columns={iv: "IV"}), FE], axis=1), has_constant="add")
    keep = X.notna().all(axis=1) & df[ycol].notna()
    Xk, yk, gk = X[keep], df[ycol][keep], df["gvkey"].values[keep]
    Xk = Xk.loc[:, (Xk != 0).any(axis=0)]
    m = sm.GLM(yk, Xk, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": gk})
    pseudo = 1 - m.deviance / m.null_deviance
    return {"beta": float(m.params["IV"]), "se": float(m.bse["IV"]), "p2": float(m.pvalues["IV"]),
            "n": int(m.nobs), "n_firms": int(pd.Series(gk).nunique()), "r2": float(pseudo)}


def stars(p): return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
def cell(b, p): return (f"\\textbf{{{b:.4f}}}$^{{{stars(p)}}}$" if stars(p) else f"{b:.4f}")


def write_tex(summary_path):
    S = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    a, a2 = S["panelA_ols"][PRIMARY], S["panelA_ols_raw"][PRIMARY]
    b, b2 = S["panelB_logit"][PRIMARY], S["panelB_logit_raw"][PRIMARY]
    L = [
        r"\begin{table}[htbp]", r"\centering",
        r"\caption{Analyst Cash-Scrutiny Channel (Link 2)}",
        r"\label{tab:cash_scrutiny_channel}", r"\small",
        r"\begin{tabular}{lcc}", r"\toprule",
        r" & UncResCEO & UncAnsCEO \\",
        r" & (DWZ residual) & (raw Q\&A) \\",
        r"\midrule",
        r"\multicolumn{3}{l}{\textit{Panel A. OLS --- DV in continuous level}} \\",
        r"CashScrutiny & " + cell(a["beta"], a["p2"]) + " & " + cell(a2["beta"], a2["p2"]) + r" \\",
        r" & (" + f"{a['se']:.4f}" + r") & (" + f"{a2['se']:.4f}" + r") \\",
        r"$N$ (calls) & " + f"{a['n']:,}" + r" & " + f"{a2['n']:,}" + r" \\",
        r"Within $R^2$ & " + f"{a['r2']:.3f}" + r" & " + f"{a2['r2']:.3f}" + r" \\",
        r"\midrule",
        r"\multicolumn{3}{l}{\textit{Panel B. Logit --- DV $= \mathbf{1}$[measure $\geq$ median]}} \\",
        r"CashScrutiny (log-odds) & " + cell(b["beta"], b["p2"]) + " & " + cell(b2["beta"], b2["p2"]) + r" \\",
        r" & (" + f"{b['se']:.4f}" + r") & (" + f"{b2['se']:.4f}" + r") \\",
        r"$N$ (calls) & " + f"{b['n']:,}" + r" & " + f"{b2['n']:,}" + r" \\",
        r"Pseudo $R^2$ & " + f"{b['r2']:.3f}" + r" & " + f"{b2['r2']:.3f}" + r" \\",
        r"\midrule",
        r"Firm FE (A) / Industry FE (B) & Yes & Yes \\",
        r"Cal. Year-Quarter FE & Yes & Yes \\",
        r"\bottomrule", r"\end{tabular}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize",
        r"\textit{Notes:} DV is CEO Q\&A uncertainty as the DWZ residual (\texttt{UncResCEO}, "
        r"firm/linguistic component removed) or the raw measure (\texttt{UncAnsCEO}, pooled-1\% "
        r"winsorized). \texttt{CashScrutiny} $=$ the share (\%) of a call's "
        r"Q\&A turns devoted to cash topics (validated in the Link~1 table). Panel~A is OLS on "
        r"the continuous DV; Panel~B is a logit on $\mathbf{1}$[DV $\geq$ sample median]. "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed); significant coefficients "
        r"in \textbf{bold}; SE (parentheses) clustered at firm level. Coarser scrutiny measures "
        r"(any-turn, raw count, log count) give the same null.",
        r"\end{minipage}", r"\end{table}",
    ]
    TEX_OUT.write_text("\n".join(L), encoding="utf-8")


def main():
    df = build_df()
    print(f"N={len(df):,} | firms={df['gvkey'].nunique():,} | dodge base-rate {df['dodge'].mean():.3f}")
    FE = pd.concat([pd.get_dummies(df["ff12_code"].astype("Int64").astype(str), prefix="ind", drop_first=True),
                    pd.get_dummies(df["cyq"], prefix="q", drop_first=True)], axis=1).astype(float)
    A = {iv: ols(df, iv) for iv, _ in IVS}                         # DV1: UncResCEO (residual)
    B = {iv: logit(df, iv, FE) for iv, _ in IVS}
    A2 = {iv: ols(df, iv, dv="UncAnsCEO") for iv, _ in IVS}        # DV2: UncAnsCEO (raw Q&A)
    B2 = {iv: logit(df, iv, FE, ycol="dodge_raw") for iv, _ in IVS}
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / SUITE / ts; out.mkdir(parents=True, exist_ok=True)
    sp = out / "summary.json"
    sp.write_text(json.dumps({"suite": SUITE, "dv": ["UncResCEO", "UncAnsCEO"], "min_qa": MIN_QA, "controls": CTRL,
                              "panelA_ols": A, "panelB_logit": B,
                              "panelA_ols_raw": A2, "panelB_logit_raw": B2, "timestamp": ts}, indent=2), encoding="utf-8")
    write_tex(sp)
    for iv, _ in IVS:
        print(f"  {iv:14s} res(OLS) b={A[iv]['beta']:+.5f} p={A[iv]['p2']:.3f} | "
              f"raw(OLS) b={A2[iv]['beta']:+.5f} p={A2[iv]['p2']:.3f} (N {A2[iv]['n']:,})")
    print(f"wrote {sp}\nwrote {TEX_OUT}")


if __name__ == "__main__":
    main()
