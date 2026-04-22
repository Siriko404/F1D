"""Assemble per_suite/h1_2_table.tex from h1_2_cash_constraint_ceo2iv 16-col output.

Body §3.3 describes 16-col structure (4 FE x 2 DV x {unconditional, interaction}).
The runner emits 16 cols of regression_results but its _save_latex_table function
displays only 8 (interaction-only). This script parses all 16
regression_results_col*.txt files and assembles a full 16-col landscape table
emitting tab:h1_2_ceo2 with full base + extended controls.

Layout:
  Cols  1-4: CashRatio_t,    unconditional (FE ladder x 4)
  Cols  5-8: CashRatio_t,    interaction   (FE ladder x 4)
  Cols  9-12: CashRatio_lead, unconditional (FE ladder x 4)
  Cols 13-16: CashRatio_lead, interaction   (FE ladder x 4)

For unconditional cols, Below-IG/Unrated/Interaction rows are blank.
For interaction cols, IG vs rated-pooled main effects appear in IV rows;
Below-IG and Unrated level dummies appear; Interaction rows populated.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE_DIR = ROOT / "outputs" / "econometric" / "h1_2_cash_constraint_ceo2iv"
OUT_FILE = ROOT / "docs" / "Draft" / "per_suite" / "h1_2_table.tex"

SPEC = [
    # CashRatio_t unconditional
    (1, "CashRatio", "industry", False),
    (2, "CashRatio", "firm", False),
    (3, "CashRatio", "industry_yq", False),
    (4, "CashRatio", "firm_yq", False),
    # CashRatio_t interaction
    (5, "CashRatio", "industry", True),
    (6, "CashRatio", "firm", True),
    (7, "CashRatio", "industry_yq", True),
    (8, "CashRatio", "firm_yq", True),
    # CashRatio_lead unconditional
    (9, "CashRatio_lead", "industry", False),
    (10, "CashRatio_lead", "firm", False),
    (11, "CashRatio_lead", "industry_yq", False),
    (12, "CashRatio_lead", "firm_yq", False),
    # CashRatio_lead interaction
    (13, "CashRatio_lead", "industry", True),
    (14, "CashRatio_lead", "firm", True),
    (15, "CashRatio_lead", "industry_yq", True),
    (16, "CashRatio_lead", "firm_yq", True),
]

# Ordered IV rows (label, var-key in coefs dict, one_or_two)
# In unconditional fits, only main IVs present.
# In interaction fits, var names are appended _c (mean-centered) and interactions present.
IV_ROWS = [
    (r"UncAnsCEO\_c", "UncAnsCEO_c", "one"),
    (r"UncPreCEO\_c", "UncPreCEO_c", "one"),
    (r"BelowIG", "BelowIG", "two"),
    (r"Unrated", "Unrated", "two"),
    (r"UncAnsCEO\_c $\times$ Unrated", "UncAnsCEO_c_x_Unrated", "one"),
    (r"UncPreCEO\_c $\times$ Unrated", "UncPreCEO_c_x_Unrated", "one"),
]

CONTROL_ROWS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO", "Lagged_DV",
]


def latest_ts_dir() -> Path:
    dirs = sorted([p for p in SUITE_DIR.iterdir() if p.is_dir()], reverse=True)
    return dirs[0]


def parse_result(txt: str) -> tuple[dict[str, tuple[float, float, float]], int, float]:
    coefs: dict[str, tuple[float, float, float]] = {}
    n_obs = 0
    rsq = 0.0

    m = re.search(r"No\. Observations:\s+(\d+)", txt)
    if m:
        n_obs = int(m.group(1))

    m = re.search(r"R-squared:\s+([\d.]+)", txt)
    if m:
        rsq = float(m.group(1))

    in_params = False
    seen_header = False
    for line in txt.splitlines():
        stripped = line.strip()
        if "Parameter Estimates" in stripped:
            seen_header = True
            continue
        if not seen_header:
            continue
        if "Parameter" in stripped and "Std. Err" in stripped:
            in_params = True
            continue
        if in_params and stripped.startswith("====="):
            break
        if not in_params:
            continue
        if stripped.startswith("-----") or not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 5:
            continue
        try:
            var = parts[0]
            beta = float(parts[1])
            se = float(parts[2])
            p_two = float(parts[4])
            coefs[var] = (beta, se, p_two)
        except (ValueError, IndexError):
            continue

    return coefs, n_obs, rsq


def stars_one(beta: float, p_two: float) -> str:
    if beta <= 0:
        return ""
    p_one = p_two / 2
    if p_one < 0.01: return "***"
    if p_one < 0.05: return "**"
    if p_one < 0.10: return "*"
    return ""


def stars_two(p_two: float) -> str:
    if p_two < 0.01: return "***"
    if p_two < 0.05: return "**"
    if p_two < 0.10: return "*"
    return ""


def fmt_coef(beta: float, stars: str) -> str:
    if stars:
        return r"\textbf{" + f"{beta:.4f}" + r"}$^{" + stars + "}$"
    return f"{beta:.4f}"


def fmt_se(se: float) -> str:
    return f"({se:.4f})"


def main() -> None:
    ts_dir = latest_ts_dir()
    print(f"Using: {ts_dir.relative_to(ROOT)}")

    per_col: dict[int, tuple[dict, int, float]] = {}
    for col, dv, fe, is_int in SPEC:
        path = ts_dir / f"regression_results_col{col}.txt"
        if not path.exists():
            raise FileNotFoundError(path)
        coefs, n_obs, rsq = parse_result(path.read_text(encoding="utf-8"))
        per_col[col] = (coefs, n_obs, rsq)

    lines: list[str] = []
    lines.append(r"\begin{landscape}")
    lines.append(r"\begin{table}[H]")
    lines.append(r"\setlength{\tabcolsep}{2pt}")
    lines.append(r"\renewcommand{\arraystretch}{0.85}")
    lines.append(r"\centering")
    lines.append(r"\caption{Financial Constraint--Moderated CEO Speech Uncertainty and Cash Holdings (CEO 2-IV: Q\&A + Presentation)}")
    lines.append(r"\label{tab:h1_2_ceo2}")
    lines.append(r"\tiny")
    lines.append(r"\begin{tabular}{l" + "c" * 16 + "}")
    lines.append(r"\toprule")
    col_nums = " & ".join(f"({i})" for i in range(1, 17))
    lines.append(f" & {col_nums} \\\\")
    lines.append(r" & \multicolumn{8}{c}{CashRatio$_t$} & \multicolumn{8}{c}{CashRatio$_{t+1}$} \\")
    lines.append(r"\cmidrule(lr){2-9} \cmidrule(lr){10-17}")
    lines.append(r" & \multicolumn{4}{c}{Unc.} & \multicolumn{4}{c}{Int.} & \multicolumn{4}{c}{Unc.} & \multicolumn{4}{c}{Int.} \\")
    lines.append(r"\cmidrule(lr){2-5} \cmidrule(lr){6-9} \cmidrule(lr){10-13} \cmidrule(lr){14-17}")
    lines.append(r"\midrule")

    # IV rows
    for label, var, tail in IV_ROWS:
        coef_cells = []
        se_cells = []
        for col, dv, fe, is_int in SPEC:
            coefs, _, _ = per_col[col]
            if var in coefs:
                beta, se, p_two = coefs[var]
                stars = stars_one(beta, p_two) if tail == "one" else stars_two(p_two)
                coef_cells.append(fmt_coef(beta, stars))
                se_cells.append(fmt_se(se))
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # Control rows (extended only, applies to all 16 cols)
    for ctrl in CONTROL_ROWS:
        coef_cells = []
        se_cells = []
        for col, dv, fe, is_int in SPEC:
            coefs, _, _ = per_col[col]
            if ctrl in coefs:
                beta, se, p_two = coefs[ctrl]
                coef_cells.append(fmt_coef(beta, stars_two(p_two)))
                se_cells.append(fmt_se(se))
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{ctrl.replace('_', r'\_')} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # FE indicators
    ind_cells = []
    firm_cells = []
    yr_cells = []
    yq_cells = []
    int_cells = []
    n_cells = []
    r2_cells = []
    for col, dv, fe, is_int in SPEC:
        _, n_obs, rsq = per_col[col]
        base_fe = fe.replace("_yq", "")
        is_yq = fe.endswith("_yq")
        ind_cells.append("Yes" if base_fe == "industry" else "")
        firm_cells.append("Yes" if base_fe == "firm" else "")
        yr_cells.append("Yes" if not is_yq else "")
        yq_cells.append("Yes" if is_yq else "")
        int_cells.append("Yes" if is_int else "")
        n_cells.append(f"{n_obs:,}")
        r2_cells.append(f"{rsq:.3f}")

    lines.append(r"Interaction terms & " + " & ".join(int_cells) + r" \\")
    lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
    lines.append(r"Year FE & " + " & ".join(yr_cells) + r" \\")
    lines.append(r"Year-Quarter FE & " + " & ".join(yq_cells) + r" \\")
    lines.append(r"\midrule")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")
    lines.append(r"$R^2$ & " + " & ".join(r2_cells) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{minipage}{\linewidth}")
    lines.append(r"\vspace{2pt}\scriptsize")
    lines.append(r"\textit{Notes:} CEO 2-IV variant of H1.2: speech-uncertainty IV stack restricted to UncAnsCEO\_c (Q\&A) + UncPreCEO\_c (Presentation), both mean-centered on the Main sample.")
    lines.append(r" Cols 1--4 / 9--12: unconditional specifications (no interactions). Cols 5--8 / 13--16: interaction specifications including Below-IG and Unrated level dummies + UncAnsCEO\_c $\times$ Unrated and UncPreCEO\_c $\times$ Unrated interaction terms. Below-IG interaction terms suppressed; main-IV slope in interaction cols applies to rated firms (IG $\cup$ Below-IG pooled).")
    lines.append(r" Reference category: investment-grade firms (S\&P long-term issuer rating BBB$-$ or above).")
    lines.append(r" $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for IVs and Unrated interactions; two-tailed for level dummies and controls).")
    lines.append(r" Significant coefficients in \textbf{bold}.")
    lines.append(r" Standard errors (in parentheses) clustered at firm level.")
    lines.append(r" Sample restricted to fiscal years 2002--2016 (Compustat ratings coverage).")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")
    lines.append(r"\end{landscape}")

    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(ROOT)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
