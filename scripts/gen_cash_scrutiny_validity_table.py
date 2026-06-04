#!/usr/bin/env python3
"""Generate the Cash-Scrutiny external-validity (Link-1) table fragment.

FIRST LINK of the analyst-scrutiny reverse-causality channel: validate that the
CashScrutiny measure (analyst attention to firm CASH HOLDINGS) actually tracks the
firm's cash. If analysts do NOT talk more about cash when the firm holds more cash,
the measure is noise and the channel is untestable.

  DV  = CashScrutiny = share of a call's analyst Q&A turns hitting the STOCK
        lexicon (cash level + liquidity; DISPOSITION/payout excluded -> its
        "dividend" loads on size/maturity, a spurious CashRatio correlate).
        Scaled to PERCENT of analyst Q&A turns for readability.
  IV  = CashRatio (= cheq/atq), the firm's actual cash holdings, contemporaneous.

Two-way fixed-effects OLS (firm FE + calendar-year-quarter FE, firm-clustered SE),
identical machinery to the H1 cash suite / empire run-up table. Four columns:
  (1) CashRatio, FE only        (3) High-Cash dummy 1[CashRatio>=p67], FE only
  (2) CashRatio, + controls     (4) High-Cash dummy, + controls
The High-Cash dummy is the Jensen-faithful PRIMARY spec (idle-cash region draws
scrutiny); the continuous slope is the weaker omnibus. A linear ~0 would NOT be a
null (distress firms draw liquidity questions too) -- only a flat high-cash region.

Inputs (pre-built artifacts):
  tmp/_cash_stock_score_call.parquet                          (STOCK-score cache; build via
                                                               scripts/.. tmp/_build_stock_score_cache.py)
  outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet  (gvkey, CashRatio, controls)

Writes:
  outputs/econometric/cash_scrutiny_validity/<ts>/summary.json   (numbers = the JSON spec)
  docs/Draft/_cash_scrutiny_validity.tex                         (thesis fragment, built FROM the json)

Regenerate: python scripts/gen_cash_scrutiny_validity_table.py
NOT hand-edited -- table cells come from this script's regression output.
"""
from __future__ import annotations
import glob
import json
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
SCORE = ROOT / "tmp" / "_cash_stock_score_call.parquet"
CTRL = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO"]
MIN_QA = 3            # require >=3 analyst Q&A turns so the share is meaningful
SUITE = "cash_scrutiny_validity"
TEX_OUT = ROOT / "docs" / "Draft" / f"_{SUITE}.tex"
# column key -> (iv, use_controls)
COLS = [("lin_noc", "CashRatio", False), ("lin_ctl", "CashRatio", True),
        ("hi_noc", "HighCash", False), ("hi_ctl", "HighCash", True)]


def _latest(pattern: str) -> str:
    hits = sorted(glob.glob(str(ROOT / pattern)))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[-1]


def load_df() -> pd.DataFrame:
    if not SCORE.exists():
        raise FileNotFoundError(f"{SCORE} -- run tmp/_build_stock_score_cache.py first")
    score = pd.read_parquet(SCORE)
    panel = pd.read_parquet(
        _latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
        columns=["file_name", "gvkey", "CashRatio", "start_date", "ff12_code"] + CTRL,
    )
    df = panel.merge(score, on="file_name", how="inner")
    df = df[~df["ff12_code"].isin([8, 11])]                       # main sample (drop fin/util)
    df = df.dropna(subset=["CashRatio", "stock_score", "gvkey"])
    df = df[df["n_qa_turns"] >= MIN_QA].copy()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df.dropna(subset=["start_date"])
    lo, hi = df["CashRatio"].quantile([.01, .99])                 # winsor fat-tailed ratio
    df["CashRatio"] = df["CashRatio"].clip(lo, hi)
    p67 = df["CashRatio"].quantile(2 / 3)
    df["HighCash"] = (df["CashRatio"] >= p67).astype(float)
    df["CashScrutiny"] = df["stock_score"] * 100.0                    # percent of analyst Q&A turns
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cq"] = df["start_date"].dt.year * 4 + (df["start_date"].dt.quarter - 1)
    return df


def run(df: pd.DataFrame, iv: str, use_ctrl: bool) -> dict:
    cols = ["CashScrutiny", iv] + (CTRL if use_ctrl else [])
    d = df.replace([np.inf, -np.inf], np.nan).dropna(subset=cols).copy()
    n_firms = int(d["gvkey"].nunique())
    d = d.set_index(["gvkey", "cq"])
    rhs = " + ".join([iv] + (CTRL if use_ctrl else []))
    f = f"CashScrutiny ~ 1 + {rhs} + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    par, se, pv = mod.params, mod.std_errors, mod.pvalues
    b, s_, p2 = float(par[iv]), float(se[iv]), float(pv[iv])
    p1 = p2 / 2 if b > 0 else 1 - p2 / 2                          # one-tailed, H: beta > 0
    ctrls = {c: {"beta": float(par[c]), "se": float(se[c]), "p2": float(pv[c])}
             for c in CTRL if c in par.index}
    return {"iv": iv, "use_ctrl": use_ctrl, "beta": b, "se": s_, "p1": p1, "p2": p2,
            "ctrls": ctrls, "n": int(mod.nobs), "n_firms": n_firms, "r2": float(mod.rsquared)}


def stars(p: float) -> str:
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))


def cell(coef: float, p: float) -> str:
    s = stars(p)
    body = f"{coef:.4f}"
    return (f"\\textbf{{{body}}}$^{{{s}}}$" if s else body)


CTRL_LABEL = {"Leverage": "Leverage", "lnAssets": "lnAssets", "TobinsQ": "TobinsQ",
              "ROA": "ROA", "Capex": "Capex", "DivDummy": "DivDummy", "sCFO": "sCFO"}

# LITERAL regex patterns actually searched -- copied VERBATIM from
# tmp/_build_stock_score_cache.py (LEVEL / LIQ / EXCL). Shown to the reader as-is.
LEX_LEVEL = [r"cash holdings?", r"cash balances?", r"cash position", r"cash on hand",
             r"cash on the balance sheet", r"cash reserves?", r"cash and cash equivalents",
             r"cash and equivalents", r"cash and short-?term investments", r"net cash",
             r"cash pile", r"cash hoard", r"cash stockpile", r"war chest", r"dry powder",
             r"excess cash", r"idle cash", r"surplus cash"]
LEX_LIQ = [r"liquidity", r"liquid assets", r"short-?term investments", r"marketable securities"]
LEX_EXCL = [r"free cash flow", r"operating cash flow", r"cash flow statement", r"cash flows?",
            r"cash conversion cycle", r"cash conversion", r"cash basis", r"cash cow",
            r"cash compensation", r"non-?cash", r"cash register", r"cash crop", r"cash taxes",
            r"cash earnings", r"cash in on"]


def _expand(pat: str) -> list[str]:
    """Expand a simple pattern (optional single chars marked by '?') into literal strings.
    e.g. 'non-?cash' -> ['noncash', 'non-cash']; 'cash balances?' -> ['cash balance', 'cash balances']."""
    forms = [""]
    i = 0
    while i < len(pat):
        ch = pat[i]
        if i + 1 < len(pat) and pat[i + 1] == "?":
            forms = [f + ch for f in forms] + list(forms)   # char present OR absent
            i += 2
        else:
            forms = [f + ch for f in forms]
            i += 1
    seen, out = set(), []
    for f in sorted(forms, key=lambda s: (len(s), s)):      # shorter/base form first
        if f not in seen:
            seen.add(f); out.append(f)
    return out


def _expand_all(ws: list[str]) -> list[str]:
    out = []
    for w in ws:
        out.extend(_expand(w))
    return out


def methodology_lines() -> list[str]:
    """Own-page block: variable definitions, regression spec, and the exact search terms + why."""
    j = lambda ws: ", ".join(r"\texttt{'" + w + r"'}" for w in _expand_all(ws))
    return [
        r"\begin{center}\large\textbf{Cash-Scrutiny Measure: Variable Construction (Link 1)}\end{center}",
        r"\vspace{4pt}\noindent\textbf{Variable definitions.}",
        r"\begin{itemize}\setlength\itemsep{2pt}",
        r"\item \textbf{CashScrutiny}$_{i,t}$ --- share (\%) of call $i$'s analyst Q\&A turns whose text "
        r"contains at least one \emph{cash level} or \emph{liquidity} term (listed below); a turn-level "
        r"binary averaged over the call's analyst Q\&A turns.",
        r"\item \textbf{CashRatio}$_{i,t}$ = cheq/atq (cash \& equivalents $\div$ total assets).",
        r"\item \textbf{High Cash}$_{i,t}$ = $\mathbf{1}[\text{CashRatio}_{i,t}\geq$ top tercile$]$.",
        r"\item \textbf{Controls} $X_{i,t}$: Leverage, ln(Assets), Tobin's Q, ROA, Capex, "
        r"Dividend Payer, Cash Flow (sCFO).",
        r"\end{itemize}",
        r"\vspace{2pt}\noindent\textbf{Specification.} Two-way fixed-effects OLS estimated at the call level:",
        r"\[ \text{CashScrutiny}_{i,t} = \beta\,\text{Cash}_{i,t} + \gamma' X_{i,t} + \alpha_i + \delta_{q(t)} + \varepsilon_{i,t}, \]",
        r"\noindent where $\text{Cash}_{i,t}$ = CashRatio (cols 1--2) or High Cash (cols 3--4); "
        r"$\alpha_i$ = firm fixed effects, $\delta_{q(t)}$ = calendar year-quarter fixed effects; "
        r"standard errors clustered by firm. The cash coefficient $\beta$ is the external-validity test.",
        r"\vspace{6pt}\noindent\textbf{Search terms.} An analyst Q\&A turn is flagged if, after the "
        r"\emph{excluded} phrases are blanked out, its lower-cased text contains any phrase below, matched "
        r"on a word boundary (case-insensitive). Every literal spelling actually searched is listed: where "
        r"a phrase has a singular/plural or hyphenated/closed variant (e.g.\ \texttt{'noncash'} and "
        r"\texttt{'non-cash'}), both forms appear. Disposition/payout terms (dividends, buybacks) are "
        r"deliberately \emph{not} used here: they load on firm size and maturity and would correlate with "
        r"CashRatio spuriously rather than through cash attention.",
        r"\begin{itemize}\setlength\itemsep{3pt}",
        r"\item \textbf{Cash level} (" + str(len(_expand_all(LEX_LEVEL))) + r" forms) --- \emph{why:} they "
        r"name the firm's cash stockpile or balance itself, the direct object of attention to how much "
        r"cash the firm holds. \\ " + j(LEX_LEVEL),
        r"\item \textbf{Liquidity} (" + str(len(_expand_all(LEX_LIQ))) + r" forms) --- \emph{why:} standard "
        r"analyst synonyms for the same liquid-asset buffer. \\ " + j(LEX_LIQ),
        r"\item \textbf{Excluded} (" + str(len(_expand_all(LEX_EXCL))) + r" forms) --- \emph{why:} they "
        r"contain ``cash'' but denote cash \emph{flow}, earnings, an accounting basis, or an idiom rather "
        r"than the cash holdings, so they are blanked out before matching to prevent false positives. \\ "
        + j(LEX_EXCL),
        r"\end{itemize}",
    ]


def write_tex(summary_path: Path) -> None:
    """Build the LaTeX table fragment FROM the written JSON spec (not in-memory)."""
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    res = summary["results"]
    keys = [c[0] for c in COLS]

    def iv_row(label: str, ivname: str) -> list[str]:
        cells = []
        for k in keys:
            r = res[k]
            cells.append(cell(r["beta"], r["p1"]) if r["iv"] == ivname else "")
        ses = []
        for k in keys:
            r = res[k]
            ses.append(f"({r['se']:.4f})" if r["iv"] == ivname else "")
        return [f"{label} & " + " & ".join(cells) + r" \\",
                " & " + " & ".join(ses) + r" \\"]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Analyst Cash-Scrutiny Validity (Link 1)}",
        r"\label{tab:cash_scrutiny_validity}",
        r"\scriptsize",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"& \multicolumn{4}{c}{DV: CashScrutiny (\% of analyst Q\&A turns on cash/liquidity)} \\",
        r"\cmidrule(lr){2-5}",
        r" & (1) & (2) & (3) & (4) \\",
        r"\midrule",
    ]
    lines += iv_row("CashRatio", "CashRatio")
    lines += iv_row("HighCash", "HighCash")
    lines.append(r"\midrule")
    for c in CTRL:
        cells = []
        for k in keys:
            r = res[k]
            cells.append(cell(r["ctrls"][c]["beta"], r["ctrls"][c]["p2"]) if r["use_ctrl"] else r"---")
        ses = []
        for k in keys:
            r = res[k]
            ses.append(f"({r['ctrls'][c]['se']:.4f})" if r["use_ctrl"] else "")
        lines.append(f"{CTRL_LABEL[c]} & " + " & ".join(cells) + r" \\")
        lines.append(" & " + " & ".join(ses) + r" \\")
    lines += [
        r"\midrule",
        r"Firm FE & Yes & Yes & Yes & Yes \\",
        r"Cal. Year-Quarter FE & Yes & Yes & Yes & Yes \\",
        r"Controls & No & Yes & No & Yes \\",
        r"\midrule",
        "Firms & " + " & ".join(f"{res[k]['n_firms']:,}" for k in keys) + r" \\",
        "N (calls) & " + " & ".join(f"{res[k]['n']:,}" for k in keys) + r" \\",
        "$R^2$ & " + " & ".join(f"{res[k]['r2']:.3f}" for k in keys) + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for the cash "
        r"coefficient, $\beta>0$; two-tailed for controls).",
        r"Significant coefficients in \textbf{bold}.",
        r"Standard errors (in parentheses) clustered at firm level.",
        r"\end{minipage}",
        r"\end{table}",
        r"\clearpage",
    ] + methodology_lines()
    TEX_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = load_df()
    print(f"analysis N={len(df):,} | firms={df['gvkey'].nunique():,} | "
          f"quarters={df['cq'].nunique()} | MIN_QA={MIN_QA}")
    res = {key: run(df, iv, uc) for (key, iv, uc) in COLS}

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / SUITE / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"suite": SUITE, "dv": "CashScrutiny (% analyst Q&A turns, STOCK lexicon)",
               "min_qa_turns": MIN_QA, "controls": CTRL,
               "columns": [{"key": k, "iv": iv, "controls": uc} for (k, iv, uc) in COLS],
               "results": res, "timestamp": ts}
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_tex(summary_path)

    for k, r in res.items():
        print(f"  {k:8} {r['iv']:9} ctrl={int(r['use_ctrl'])} "
              f"beta={r['beta']:+.5f} se={r['se']:.5f} p1={r['p1']:.4f} N={r['n']:,}")
    print(f"wrote {summary_path}")
    print(f"wrote {TEX_OUT}")


if __name__ == "__main__":
    main()
