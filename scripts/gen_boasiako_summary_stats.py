"""Generate summary stats table: paper Panel A vs F1D complete-case panel.
Reads from outputs/econometric/h1_5_disclosure_law_did/summary_stats/latest_summary_stats.json
(produced by tmp/_dld_rebuild.py).
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
STATS_FILE = ROOT / "outputs" / "econometric" / "h1_5_disclosure_law_did" / "summary_stats" / "latest_summary_stats.json"
OUT = ROOT / "docs" / "Draft" / "_boasiako_summary_stats.tex"

# ── Paper Panel A anchors: transcribed verbatim in inputs/benchmarks/boasiako_2020.json
#    (NOT F1D estimates; cited there). Read here, never hardcoded. ──
BENCH = ROOT / "config" / "benchmarks" / "boasiako_2020.json"
_t1 = json.loads(BENCH.read_text(encoding="utf-8"))["table1_panelA"]
PAPER = {k: tuple(v) for k, v in _t1["vars"].items()}
PAPER_N = _t1["n_obs"]

LABELS = {
    "cash_w": r"cash\_w", "firm_size_w": r"firm\_size\_w", "firm_age_w": r"firm\_age\_w",
    "book_leverage_w": r"book\_leverage\_w", "market_to_book_w": r"market\_to\_book\_w",
    "cash_flow_w": r"cash\_flow\_w", "capital_expenditure_w": r"capital\_expenditure\_w",
    "acquisition_expenditure_w": r"acquisition\_expenditure\_w",
    "rd_expenditure_w": r"rd\_expenditure\_w", "nwc_w": r"nwc\_w",
    "dividend_paying_w": r"dividend\_paying\_w", "industry_cf_vol_w": r"industry\_cf\_vol\_w",
}

def main():
    if not STATS_FILE.exists():
        raise FileNotFoundError(
            f"{STATS_FILE} missing. Run tmp/_dld_rebuild.py first to generate it."
        )
    ours = json.loads(STATS_FILE.read_text(encoding="utf-8"))
    our_N = ours["cash_w"]["N"]

    L = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Disclosure-Law Sample: Summary Statistics}",
        r"\label{tab:boasiako_summary_stats}",
        r"\small\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{lrrrrr rrrrr}",
        r"\toprule",
        r" & \multicolumn{5}{c}{Boasiako-Keefe (2020)} & \multicolumn{5}{c}{This paper} \\",
        r"\cmidrule(lr){2-6} \cmidrule(lr){7-11}",
        r" & Mean & SD & p25 & p50 & p75 & Mean & SD & p25 & p50 & p75 \\",
        r"\midrule",
    ]
    for var, label in LABELS.items():
        p = PAPER[var]
        o = ours[var]
        L.append(f"  {label} & {_f(p[0])} & {_f(p[1])} & {_f(p[2])} & {_f(p[3])} & {_f(p[4])} & {_f(o['mean'])} & {_f(o['sd'])} & {_f(o['p25'])} & {_f(o['p50'])} & {_f(o['p75'])} \\\\")

    L += [
        r"\midrule",
        f"  Observations & \\multicolumn{{5}}{{c}}{{{PAPER_N}}} & \\multicolumn{{5}}{{c}}{{{our_N:,}}} \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}  N={our_N:,}")

def _f(val):
    if val is None:
        return "---"
    return f"{val:.4f}"

if __name__ == "__main__":
    main()
