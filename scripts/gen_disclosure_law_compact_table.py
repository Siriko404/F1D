"""Compact disclosure-law DiD table — Boasiako benchmark | our clone | our DV.

Sina 2026-05-18: collapse the 8-column FE-variant table to the canonical
spec only (drop the FE-sensitivity COLUMNS, NOT the controls). 3 columns:
  (1) Boasiako-O'Connor Keefe (2020) EFM Table 2 col 1 — PUBLISHED benchmark,
      headline + all 11 controls verbatim from paper p538 (cited; same
      convention as the Campello rebuild benchmark columns — NOT our estimate).
  (2) Our clone — CASH, canonical industry+state+year FE (suite col 1).
  (3) Our DV    — UncResCEO, canonical industry+state+year FE (suite col 5).

Our numbers (headline + 11 controls) are READ from the latest suite_spec
JSON (no hardcoding of our results). Rows: Disclosure Law x Post, the 11
Boasiako Eq-1 controls, FE indicators incl. STATE FE, N, R^2.

Writes docs/Draft/_disclosure_law_compact.tex (dedicated file, mirrors
_campello_rebuild_t8 convention); thesis_tables.tex \\input's it.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "outputs" / "econometric" / "h1_5_disclosure_law_did"
RUNS_UNCRES = ROOT / "outputs" / "econometric" / "h1_5_disclosure_law_did_uncres"
OUT = ROOT / "docs" / "Draft" / "_disclosure_law_compact.tex"

# Boasiako-O'Connor Keefe (2020) EFM 27(3):528-551, Table 2 col (1): published
# constants transcribed verbatim in inputs/benchmarks/boasiako_2020.json (cited
# there; baseline year+industry+state FE, state-clustered SE; NOT F1D estimates).
# Read here, never hardcoded.
_BENCH = ROOT / "config" / "benchmarks" / "boasiako_2020.json"
_b2 = json.loads(_BENCH.read_text(encoding="utf-8"))["table2_col1"]
BOASIAKO_PUB = dict(_b2["headline"])
# (json_key, display label) — beta/se/stars pulled from the benchmark JSON.
_CTRL_LABELS = [
    ("firm_size",                r"firm\_size"),
    ("firm_age",                 r"firm\_age"),
    ("book_leverage",            r"book\_leverage"),
    ("market_to_book",           r"market\_to\_book"),
    ("cash_flow",                r"cash\_flow"),
    ("capital_expenditure",      r"capital\_expenditure"),
    ("acquisition_expenditure",  r"acquisition\_expenditure"),
    ("rd_expenditure",           r"rd\_expenditure"),
    ("nwc",                      r"nwc"),
    ("dividend_paying",          r"dividend\_paying"),
    ("industry_cf_vol",          r"industry\_cf\_vol"),
]
CONTROLS = [(k, lbl, _b2["controls"][k]["beta"], _b2["controls"][k]["se"], _b2["controls"][k]["stars"])
            for k, lbl in _CTRL_LABELS]


def _latest_spec() -> Path:
    cands = sorted(glob.glob(str(RUNS / "*" / "suite_spec_H1.5.disclosure_law_did.json")))
    if not cands:
        raise FileNotFoundError(f"no suite_spec under {RUNS}")
    return Path(cands[-1])


def _latest_uncres_spec() -> Path:
    cands = sorted(glob.glob(str(RUNS_UNCRES / "*" / "suite_spec_H1.5.disclosure_law_did_uncres.json")))
    if not cands:
        raise FileNotFoundError(f"no suite_spec under {RUNS_UNCRES}")
    return Path(cands[-1])


def _stars_one(p):
    if p is None:
        return ""
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def _stars_two(p):
    if p is None:
        return ""
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def _col(spec, col_num, want_dv):
    c = next(c for c in spec["columns"] if c["col"] == col_num)
    assert c["dv"] == want_dv, f"col {col_num} dv={c['dv']} != {want_dv}"
    dl = c["coefs"]["Disclosure_Law"]
    return {
        "head_beta": f"{dl['beta']:.4f}", "head_se": f"{dl['se']:.4f}",
        "head_stars": _stars_one(dl.get("p_one")),
        "n": f"{c['n_obs']:,}", "r2": f"{c['r2']:.3f}",
        "coefs": c["coefs"],
    }


def _fmt(beta_str, stars):
    # Project convention: significant coefficients (any star) in \textbf bold.
    if not stars:
        return beta_str
    return f"\\textbf{{{beta_str}}}$^{{{stars}}}$"


def main() -> None:
    spec = json.loads(_latest_spec().read_text(encoding="utf-8"))
    cash = _col(spec, 1, "cash")

    spec_unc = json.loads(_latest_uncres_spec().read_text(encoding="utf-8"))
    uncres = _col(spec_unc, 1, "UncResCEO_c")

    # 3 columns: paper (1) | CASH (2) | UncResCEO (3)
    L = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Boasiako-Keefe Disclosure-Law Replication}",
        r"\label{tab:h1_5_disclosure_law_did}",
        r"\small",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r" & Boasiako-Keefe (2020) & \multicolumn{2}{c}{This paper (F1D rebuild)} \\",
        r" & Table~2 Col~(1) & CASH & UncResCEO \\",
        r" & (1) & (2) & (3) \\",
        r"\midrule",
        r"Disclosure\_Law "
        f"& {_fmt(BOASIAKO_PUB['beta'], BOASIAKO_PUB['stars'])} "
        f"& {_fmt(cash['head_beta'], cash['head_stars'])} "
        f"& {_fmt(uncres['head_beta'], uncres['head_stars'])} \\\\",
        f" & ({BOASIAKO_PUB['se']}) & ({cash['head_se']}) & "
        f"({uncres['head_se']}) \\\\",
        r"\midrule",
    ]
    for key, label, b_pub, se_pub, st_pub in CONTROLS:
        cc = cash["coefs"].get(key)
        cu = uncres["coefs"].get(key)
        if cc and cc.get("beta") is not None:
            cb = _fmt(f"{cc['beta']:.4f}", _stars_two(cc.get("p_two")))
            cb_se = f"{cc['se']:.4f}"
        else:
            cb, cb_se = "--", "--"
        if cu and cu.get("beta") is not None:
            ub = _fmt(f"{cu['beta']:.4f}", _stars_two(cu.get("p_two")))
            ub_se = f"{cu['se']:.4f}"
        else:
            ub, ub_se = "--", "--"
        L.append(f"{label} & {_fmt(b_pub, st_pub)} & {cb} & {ub} \\\\")
        L.append(f" & ({se_pub}) & ({cb_se}) & ({ub_se}) \\\\")
    L += [
        r"\midrule",
        r"Industry FE & Yes & Yes & Yes \\",
        r"State FE & Yes & Yes & Yes \\",
        r"Year FE & Yes & Yes & Yes \\",
        r"\midrule",
        f"N & {BOASIAKO_PUB['n']} & {cash['n']} & {uncres['n']} \\\\",
        f"$R^2$ & {BOASIAKO_PUB['r2']} & {cash['r2']} & {uncres['r2']} \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\footnotesize",
        r"\textit{Notes:} $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ "
        r"(headline one-tailed $\beta>0$; controls two-tailed). "
        r"Significant coefficients in \textbf{bold}. Standard errors "
        r"(in parentheses) clustered at the state level.",
        r"\end{minipage}",
        r"\end{table}",
    ]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  Boasiako pub : {BOASIAKO_PUB['beta']}{BOASIAKO_PUB['stars']} "
          f"({BOASIAKO_PUB['se']}) N {BOASIAKO_PUB['n']}")
    print(f"  F1D CASH     : {cash['head_beta']}{cash['head_stars']} "
          f"({cash['head_se']}) N {cash['n']}")
    print(f"  F1D UncResCEO: {uncres['head_beta']}{uncres['head_stars']} "
          f"({uncres['head_se']}) N {uncres['n']}")


if __name__ == "__main__":
    main()
