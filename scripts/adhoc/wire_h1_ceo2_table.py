"""Assemble per_suite/h1_table.tex from h1_cash_holdings_ceo2iv regression output.

Parses regression_results_col*.txt (12 files) at the ceo2iv output dir and emits
a 12-col landscape LaTeX table with IVs + full controls + FE ladder + N + R2.

Replaces stale Mgr-based per_suite/h1_table.tex (which labels `tab:h1` and
includes UncAnsMgr + UncPreMgr rows body does NOT cite). Body §2.4 + §3.2
cite `tab:h1_ceo2` which is what this output emits.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CEO2IV_DIR = ROOT / "outputs" / "econometric" / "h1_cash_holdings_ceo2iv"
OUT_FILE = ROOT / "docs" / "Draft" / "per_suite" / "h1_table.tex"

# 12-col spec per runner MODEL_SPECS
SPEC = [
    (1, "CashRatio", "industry", "base"),
    (2, "CashRatio", "firm", "base"),
    (3, "CashRatio", "industry", "extended"),
    (4, "CashRatio", "firm", "extended"),
    (5, "CashRatio", "industry_yq", "extended"),
    (6, "CashRatio", "firm_yq", "extended"),
    (7, "CashRatio_lead", "industry", "base"),
    (8, "CashRatio_lead", "firm", "base"),
    (9, "CashRatio_lead", "industry", "extended"),
    (10, "CashRatio_lead", "firm", "extended"),
    (11, "CashRatio_lead", "industry_yq", "extended"),
    (12, "CashRatio_lead", "firm_yq", "extended"),
]

KEY_IVS = ["UncAnsCEO", "UncPreCEO"]
BASE_CONTROLS = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO", "Lagged_DV"]
EXT_ONLY = ["SalesGrowth", "RDSales", "CashFlowAt", "DailyVola"]

IV_LABEL = {"UncAnsCEO": r"UncAnsCEO", "UncPreCEO": r"UncPreCEO"}


def latest_ts_dir() -> Path:
    """Return newest timestamped subdir in ceo2iv output."""
    dirs = sorted([p for p in CEO2IV_DIR.iterdir() if p.is_dir()], reverse=True)
    return dirs[0]


def parse_result(txt: str) -> tuple[dict[str, tuple[float, float, float]], int, float]:
    """Return (coefs dict {var: (beta, se, p_two)}, n_obs, rsq)."""
    coefs: dict[str, tuple[float, float, float]] = {}
    n_obs = 0
    rsq = 0.0

    m = re.search(r"No\. Observations:\s+(\d+)", txt)
    if m:
        n_obs = int(m.group(1))

    m = re.search(r"R-squared:\s+([\d.]+)", txt)
    if m:
        rsq = float(m.group(1))

    # Parameter estimate block delimited by header "Parameter  Std. Err." and closing "========".
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
            in_params = False
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


def stars_onetailed(beta: float, p_two: float) -> str:
    if beta <= 0:
        return ""
    p_one = p_two / 2
    if p_one < 0.01:
        return "***"
    if p_one < 0.05:
        return "**"
    if p_one < 0.10:
        return "*"
    return ""


def stars_twotailed(p_two: float) -> str:
    if p_two < 0.01:
        return "***"
    if p_two < 0.05:
        return "**"
    if p_two < 0.10:
        return "*"
    return ""


def fmt_coef(beta: float, stars: str) -> str:
    b = f"{beta:.4f}{stars}"
    if stars:
        return r"\textbf{" + f"{beta:.4f}" + r"}$^{" + stars + "}$"
    return f"{beta:.4f}"


def fmt_se(se: float) -> str:
    return f"({se:.4f})"


def main() -> None:
    ts_dir = latest_ts_dir()
    print(f"Using: {ts_dir.relative_to(ROOT)}")

    per_col: dict[int, tuple[dict, int, float]] = {}
    for col, dv, fe, ctrls in SPEC:
        path = ts_dir / f"regression_results_col{col}.txt"
        if not path.exists():
            raise FileNotFoundError(path)
        coefs, n_obs, rsq = parse_result(path.read_text(encoding="utf-8"))
        per_col[col] = (coefs, n_obs, rsq)

    # Build LaTeX body
    lines: list[str] = []
    lines.append(r"\begin{landscape}")
    lines.append(r"\begin{table}[H]")
    lines.append(r"\setlength{\tabcolsep}{3pt}")
    lines.append(r"\renewcommand{\arraystretch}{0.85}")
    lines.append(r"\centering")
    lines.append(r"\caption{Speech Uncertainty and Cash Holdings (CEO 2-IV: Q\&A + Presentation)}")
    lines.append(r"\label{tab:h1_ceo2}")
    lines.append(r"\scriptsize")
    lines.append(r"\begin{tabular}{lcccccccccccc}")
    lines.append(r"\toprule")
    col_nums = " & ".join(f"({i})" for i in range(1, 13))
    lines.append(f" & {col_nums} \\\\")
    lines.append(r" & \multicolumn{6}{c}{CashRatio$_t$} & \multicolumn{6}{c}{CashRatio$_{t+1}$} \\")
    lines.append(r"\cmidrule(lr){2-7} \cmidrule(lr){8-13}")
    lines.append(r"\midrule")

    # IV rows (one-tailed, bold)
    for iv in KEY_IVS:
        coef_cells = []
        se_cells = []
        for col, dv, fe, ctrls in SPEC:
            coefs, _, _ = per_col[col]
            beta, se, p_two = coefs.get(iv, (0.0, 0.0, 1.0))
            coef_cells.append(fmt_coef(beta, stars_onetailed(beta, p_two)))
            se_cells.append(fmt_se(se))
        lines.append(f"{IV_LABEL[iv]} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # Base controls (present in all 12 cols)
    for ctrl in BASE_CONTROLS:
        coef_cells = []
        se_cells = []
        for col, dv, fe, ctrls in SPEC:
            coefs, _, _ = per_col[col]
            if ctrl in coefs:
                beta, se, p_two = coefs[ctrl]
                coef_cells.append(fmt_coef(beta, stars_twotailed(p_two)))
                se_cells.append(fmt_se(se))
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{ctrl.replace('_', r'\_')} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    # Extended-only controls
    for ctrl in EXT_ONLY:
        coef_cells = []
        se_cells = []
        for col, dv, fe, ctrls in SPEC:
            coefs, _, _ = per_col[col]
            if ctrl in coefs:
                beta, se, p_two = coefs[ctrl]
                coef_cells.append(fmt_coef(beta, stars_twotailed(p_two)))
                se_cells.append(fmt_se(se))
            else:
                coef_cells.append("")
                se_cells.append("")
        lines.append(f"{ctrl.replace('_', r'\_')} & " + " & ".join(coef_cells) + r" \\")
        lines.append(f" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # FE + Controls indicators
    ext_cells = []
    ind_cells = []
    firm_cells = []
    yr_cells = []
    yq_cells = []
    n_cells = []
    r2_cells = []
    for col, dv, fe, ctrls in SPEC:
        _, n_obs, rsq = per_col[col]
        ext_cells.append("Yes" if ctrls == "extended" else "")
        base_fe = fe.replace("_yq", "")
        is_yq = fe.endswith("_yq")
        ind_cells.append("Yes" if base_fe == "industry" else "")
        firm_cells.append("Yes" if base_fe == "firm" else "")
        yr_cells.append("Yes" if not is_yq else "")
        yq_cells.append("Yes" if is_yq else "")
        n_cells.append(f"{n_obs:,}")
        r2_cells.append(f"{rsq:.3f}")

    lines.append(r"Extended Controls & " + " & ".join(ext_cells) + r" \\")
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
    lines.append(r"\textit{Notes:} CEO 2-IV variant of H1: joint-IV stack restricted to UncAnsCEO (Q\&A) + UncPreCEO (Presentation); manager-pool and non-CEO measures dropped.")
    lines.append(r" $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for IVs, $\beta > 0$; two-tailed for controls).")
    lines.append(r" Significant coefficients in \textbf{bold}.")
    lines.append(r" Standard errors (in parentheses) clustered at firm level.")
    lines.append(r" Main sample (excludes financial and utility firms).")
    lines.append(r" $R^2$ includes absorbed fixed effects (not within-$R^2$).")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")
    lines.append(r"\end{landscape}")

    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(ROOT)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
