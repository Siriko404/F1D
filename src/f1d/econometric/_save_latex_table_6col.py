"""Save LaTeX table function for H7 Illiquidity with 6 columns (A1-A4 + B1-B2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Emit a LaTeX table of the primary (Main sample) results."""
    tex_path = out_dir / "h7_illiquidity_table.tex"

    def get_res(spec_id: str, sample: str = "Main") -> Optional[Dict[str, Any]]:
        for r in all_results:
            if r["sample"] == sample and r["spec_id"] == spec_id:
                return r
        return None

    def fmt_coef(val: float, pval: float) -> str:
        if val is None or pd.isna(val):
            return ""
        stars = (
            "^{***}"
            if pval < 0.01
            else "^{**}"
            if pval < 0.05
            else "^{*}"
            if pval < 0.10
            else ""
        )
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        return "" if (val is None or pd.isna(val)) else f"({val:.4f})"

    # 6 columns: a1-a4 (raw uncertainty) + b1-b2 (clarity residuals)
    specs_order = ["A1", "A2", "A3", "A4", "B1", "B2"]
    results_main = [get_res(s) for s in specs_order]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H7: Speech Vagueness and Stock Illiquidity (Amihud 2002)}",
        r"\label{tab:h7_illiquidity}",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r" & (A1) & (A2) & (A3) & (A4) & (B1) & (B2) \\",
        r" & CEO QA & CEO Pres & Mgr QA & Mgr Pres & CEO Resid & Mgr Resid \\",
        r"\midrule",
    ]

    # Uncertainty coefficient row
    row_b = "Uncertainty Measure & "
    row_se = " & "
    for r in results_main:
        if r:
            row_b += f"{fmt_coef(r['beta1'], r['beta1_p_one'])} & "
            row_se += f"{fmt_se(r['beta1_se'])} & "
        else:
            row_b += " & "
            row_se += " & "
    lines.append(row_b.rstrip(" &") + r" \\")
    lines.append(row_se.rstrip(" &") + r" \\")

    lines += [
        r"\midrule",
        r"Negative Sentiment & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Analyst Uncertainty & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Controls & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Firm FE  & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"Year FE  & Yes & Yes & Yes & Yes & Yes & Yes \\",
        r"\midrule",
    ]

    row_n = "Observations & "
    row_r2 = "Within-$R^2$ & "
    for r in results_main:
        if r:
            row_n += f"{r['n_obs']:,} & "
            row_r2 += f"{r['within_r2']:.4f} & "
        else:
            row_n += " & "
            row_r2 += " & "
    lines.append(row_n.rstrip(" &") + r" \\")
    lines.append(row_r2.rstrip(" &") + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\\[-0.5em]",
        r"\parbox{\textwidth}{\scriptsize ",
        r"\textit{Notes:} "
        r"Dependent variable is Amihud illiquidity$_{t}$ (Amihud 2002). "
        r"All models use the Main industry sample (non-financial, non-utility firms). "
        r"Columns (A1)--(A4) use raw uncertainty measures; "
        r"columns (B1)--(B2) use clarity residuals (idiosyncratic uncertainty after firm/linguistic controls). "
        r"Firms with fewer than 5 calls are excluded. "
        r"Standard errors (in parentheses) are clustered at the firm level. "
        r"All continuous controls are standardized within each model's estimation sample. "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for H7).",
        r"}",
        r"\end{table}",
    ]

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  LaTeX table saved: {tex_path.name}")
