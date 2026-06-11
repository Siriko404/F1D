#!/usr/bin/env python3
"""Generate the thesis Summary Statistics table fragment (Table 1).

Descriptive moments (N, mean, SD, p25, median, p75) computed on the EXACT
estimation samples of the Empire-Building run-up test, cash arm
(tab:empire_building_did). Loaders and sample construction are IMPORTED from
scripts/gen_empire_did_table.py -- no logic duplicated, no regression re-run:

  Panel A: CashRatio-equation universe   (col 1; partial-adjustment sample)
  Panel B: UncResCEO-equation universe   (col 2); the CashScrutiny and
           HighCashScrutiny rows use their matched universe (cols 3-4)

Cross-artifact gate: each sample's N and firm count MUST equal the latest
empire_building_did summary.json values -- the script aborts on any mismatch,
so the published stats can only ever describe the published samples.

Writes:
  outputs/econometric/summary_stats/<ts>/summary.json   (numbers)
  docs/Draft/_summary_stats.tex                          (thesis fragment)

The .tex is rendered FROM the written summary.json (read back from disk),
never from in-memory results.

Regenerate: python scripts/gen_summary_stats_table.py
NOT hand-edited -- table cells come from this script's JSON output.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_empire_did_table as emp

ROOT = emp.ROOT
TEX_OUT = ROOT / "docs" / "Draft" / "_summary_stats.tex"


def est_sample(q: pd.DataFrame, dv: str, match: str | None = None,
               add_cash_lag: bool = False) -> pd.DataFrame:
    """The exact rows the corresponding regression used (mirrors emp.run)."""
    extra = ["CashRatio_lag"] if add_cash_lag else []
    need = [dv, "PreAnnounceQtr"] + emp.CTRL + extra + ([match] if match else [])
    return q.replace([np.inf, -np.inf], np.nan).dropna(subset=need)


def moments(d: pd.DataFrame, col: str) -> dict:
    x = d[col]
    return {"n": int(x.count()), "mean": float(x.mean()), "sd": float(x.std()),
            "p25": float(x.quantile(0.25)), "p50": float(x.quantile(0.50)),
            "p75": float(x.quantile(0.75))}


def main() -> None:
    p, s, m = emp.base_panel(), emp.sdc(), emp.manifest()
    q, _ = emp.build(p, s, m, s["pc"] >= 50)  # cash arm

    d_a = est_sample(q, "CashRatio", add_cash_lag=True)            # col 1
    d_b = est_sample(q, "UncResCEO")                               # col 2
    d_s = est_sample(q, "CashScrutiny", match="UncResCEO")         # cols 3-4

    # Gate: samples must reproduce the locked table's N / firm counts.
    ref_path = Path(emp._latest("outputs/econometric/empire_building_did/*/summary.json"))
    ref = json.loads(ref_path.read_text(encoding="utf-8"))["results"]
    gate = {}
    for key, d in [("cash:CashRatio", d_a), ("cash:UncResCEO", d_b),
                   ("cash:CashScrutiny", d_s)]:
        got = (len(d), int(d["gvkey"].nunique()))
        want = (ref[key]["n"], ref[key]["n_firms"])
        gate[key] = {"n": got[0], "n_firms": got[1]}
        if got != want:
            raise SystemExit(f"GATE FAIL {key}: sample {got} != summary.json {want}")

    ctrl_rows = [(c, c) for c in emp.CTRL]
    panel_a_rows = [("CashRatio", "CashRatio"),
                    ("CashRatio_lag", r"CashRatio$_{t-1}$"),
                    ("PreAnnounceQtr", "PreAnnounceQtr")] + ctrl_rows
    panel_b_rows = [("UncResCEO", "UncResCEO"),
                    ("CashScrutiny", "CashScrutiny"),
                    ("HighCashScrutiny", "HighCashScrutiny"),
                    ("PreAnnounceQtr", "PreAnnounceQtr")] + ctrl_rows

    def rows(spec, frame_for):
        out = []
        for var, label in spec:
            d = frame_for(var)
            out.append({"var": var, "label": label, **moments(d, var)})
        return out

    summary = {
        "source": "exact estimation samples of tab:empire_building_did, cash arm "
                  "(gen_empire_did_table.build + per-DV dropna)",
        "gate": {"ref_summary": str(ref_path.relative_to(ROOT)), "checked": gate},
        "panels": {
            "A": {"title": "Cash-acquirer universe, CashRatio equation "
                           "(run-up test, column 1)",
                  "n": len(d_a), "n_firms": int(d_a["gvkey"].nunique()),
                  "rows": rows(panel_a_rows, lambda v: d_a)},
            "B": {"title": "Cash-acquirer universe, UncResCEO equation "
                           "(run-up test, column 2)",
                  "n": len(d_b), "n_firms": int(d_b["gvkey"].nunique()),
                  "rows": rows(panel_b_rows,
                               lambda v: d_s if v in ("CashScrutiny", "HighCashScrutiny") else d_b)},
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d_%H%M%S"),
    }

    out = ROOT / "outputs" / "econometric" / "summary_stats" / summary["timestamp"]
    out.mkdir(parents=True, exist_ok=True)
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    write_tex(summary_path)
    print(f"wrote {summary_path}")
    print(f"wrote {TEX_OUT}")


def write_tex(summary_path: Path) -> None:
    s = json.loads(summary_path.read_text(encoding="utf-8"))
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Summary Statistics}",
        r"\label{tab:summary_stats}",
        r"\scriptsize",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r" & N & Mean & SD & P25 & Median & P75 \\",
        r"\midrule",
    ]
    for pid in ("A", "B"):
        panel = s["panels"][pid]
        lines.append(r"\multicolumn{7}{l}{\textit{Panel " + pid + ". "
                     + panel["title"] + r"}} \\")
        lines.append(r"\addlinespace")
        for r_ in panel["rows"]:
            lines.append(
                f"{r_['label']} & {r_['n']:,} & {r_['mean']:.4f} & {r_['sd']:.4f}"
                f" & {r_['p25']:.4f} & {r_['p50']:.4f} & {r_['p75']:.4f} \\\\")
        if pid == "A":
            lines.append(r"\midrule")
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} Moments are computed on the exact estimation samples of "
        r"the Empire-Building Run-Up Test (cash-acquirer arm): Panel A on the "
        r"CashRatio-equation universe (column 1), Panel B on the UncResCEO-equation "
        r"universe (column 2); the CashScrutiny and HighCashScrutiny rows use their "
        r"matched universe (columns 3--4), hence their smaller N. Never-acquirer "
        r"firm-quarters are included (the fixed-effects baseline); treated firms' "
        r"post-announcement quarters are excluded by design. All variables are "
        r"defined in the Appendix.",
        r"\end{minipage}",
        r"\end{table}",
    ]
    TEX_OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
