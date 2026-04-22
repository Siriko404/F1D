"""Build Appendix B — Detailed Validity Tables.

Writes docs/Draft/sections/appendix_b_validity_tables.tex with two subsections:

B.1 Driver Regressions — NoCEO Speech Channels (label app:additional:drivers)
    Mirror of tab:driver_matrix but regressor DVs are UncAnsNoCEO / UncPreNoCEO.
    Reads H11 PRisk + H24 US EPU + H24b GEPU diagnostics CSVs.

B.2 Outside-World Reaction — Manager-Pool Coefficients (label app:additional:reaction)
    H14c Mgr-pool coefficients (UncAnsMgr, UncPreMgr) across the 12 specs.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
H11_DIR = ROOT / "outputs" / "econometric" / "h11_prisk_uncertainty"
H24_DIR = ROOT / "outputs" / "econometric" / "h24_us_epu"
H24B_DIR = ROOT / "outputs" / "econometric" / "h24b_global_epu"
H14C_DIR = ROOT / "outputs" / "econometric" / "h14c_spread_bgt_level"
OUT_FILE = ROOT / "docs" / "Draft" / "sections" / "appendix_b_validity_tables.tex"


def latest(dir_: Path) -> Path:
    return sorted([p for p in dir_.iterdir() if p.is_dir()], reverse=True)[0]


def read_h11_noceo_cells(ts_dir: Path) -> dict[tuple[str, str], tuple[float, float, float, int]]:
    csv_path = ts_dir / "model_diagnostics.csv"
    result: dict[tuple[str, str], tuple[float, float, float, int]] = {}
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["sample"] != "Main":
                continue
            dv = row["dv"]
            fe = row["fe"]
            if dv in ("UncAnsNoCEO", "UncPreNoCEO") and fe in ("industry", "firm"):
                result[(dv, fe)] = (
                    float(row["beta_prisk"]),
                    float(row["beta_prisk_se"]),
                    float(row["beta_prisk_p_two"]),
                    int(row["n_obs"]),
                )
    return result


def read_macro_noceo_cells(ts_dir: Path) -> dict[tuple[str, str], tuple[float, float, float, int]]:
    csv_path = ts_dir / "model_diagnostics.csv"
    result: dict[tuple[str, str], tuple[float, float, float, int]] = {}
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dv = row["dv"]
            fe = row["fe"]
            if dv in ("UncAnsNoCEO", "UncPreNoCEO") and fe in ("industry", "firm"):
                result[(dv, fe)] = (
                    float(row["beta"]),
                    float(row["beta_se"]),
                    float(row["beta_p_two"]),
                    int(row["n_obs"]),
                )
    return result


def read_h14c_all(ts_dir: Path) -> list[dict]:
    csv_path = ts_dir / "model_diagnostics.csv"
    rows: list[dict] = []
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    rows.sort(key=lambda r: int(r["col"]))
    return rows


def stars_one(beta: float, p_two: float) -> str:
    if beta <= 0:
        return ""
    p_one = p_two / 2
    if p_one < 0.01: return "***"
    if p_one < 0.05: return "**"
    if p_one < 0.10: return "*"
    return ""


def fmt_coef(beta: float, stars: str, fmt: str) -> str:
    s = fmt.format(beta)
    if stars:
        return r"\textbf{" + s + r"}$^{" + stars + "}$"
    return s


def cell_rows(data: dict, fmt_b: str, fmt_s: str) -> tuple[list[str], list[str]]:
    coef_cells: list[str] = []
    se_cells: list[str] = []
    for (iv, fe) in [("UncAnsNoCEO", "industry"), ("UncAnsNoCEO", "firm"),
                     ("UncPreNoCEO", "industry"), ("UncPreNoCEO", "firm")]:
        beta, se, p_two, _ = data[(iv, fe)]
        coef_cells.append(fmt_coef(beta, stars_one(beta, p_two), fmt_b))
        se_cells.append("(" + fmt_s.format(se) + ")")
    return coef_cells, se_cells


def main() -> None:
    h11_latest = latest(H11_DIR)
    h24_latest = latest(H24_DIR)
    h24b_latest = latest(H24B_DIR)
    h14c_latest = latest(H14C_DIR)
    print(f"H11:  {h11_latest.relative_to(ROOT)}")
    print(f"H24:  {h24_latest.relative_to(ROOT)}")
    print(f"H24b: {h24b_latest.relative_to(ROOT)}")
    print(f"H14c: {h14c_latest.relative_to(ROOT)}")

    prisk_noceo = read_h11_noceo_cells(h11_latest)
    us_epu_noceo = read_macro_noceo_cells(h24_latest)
    gepu_noceo = read_macro_noceo_cells(h24b_latest)
    h14c_rows = read_h14c_all(h14c_latest)

    lines: list[str] = []
    lines.append(r"% Appendix B — Detailed Validity Tables (auto-generated via scripts/adhoc/build_appendix_b.py)")
    lines.append(r"")
    lines.append(r"\section{Detailed Validity Tables}")
    lines.append(r"\label{app:additional}")
    lines.append(r"")
    lines.append(r"This appendix reports two sets of companion tables for the construct-validation and outside-world reaction analyses of \S\ref{sec:additional}.")
    lines.append(r"")

    # B.1 — NoCEO driver matrix
    lines.append(r"\subsection{Driver Regressions --- Non-CEO Speech Channels}")
    lines.append(r"\label{app:additional:drivers}")
    lines.append(r"")
    lines.append(r"Table~\ref{tab:driver_matrix_noceo} replicates the consolidated driver matrix of \S\ref{sec:additional:drivers} using the non-CEO manager speech channels (UncAnsNoCEO, UncPreNoCEO) in place of the CEO-partitioned regressors. A driver that moves both the CEO and non-CEO speech channels in the predicted direction is consistent with aggregate firm-call-level uncertainty content propagating to both speaker pools; a driver that loads one channel and not the other suggests channel-specific responsiveness.")
    lines.append(r"")
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Driver Matrix --- Non-CEO Speech Channels}")
    lines.append(r"\label{tab:driver_matrix_noceo}")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{lcccc}")
    lines.append(r"\toprule")
    lines.append(r" & \multicolumn{2}{c}{UncAnsNoCEO} & \multicolumn{2}{c}{UncPreNoCEO} \\")
    lines.append(r"\cmidrule(lr){2-3} \cmidrule(lr){4-5}")
    lines.append(r" & Industry FE & Firm FE & Industry FE & Firm FE \\")
    lines.append(r"\midrule")

    coef, se = cell_rows(prisk_noceo, "{:.5f}", "{:.5f}")
    lines.append(r"PRisk (firm-call, \citeA{hassan2020}) & " + " & ".join(coef) + r" \\")
    lines.append(r" & " + " & ".join(se) + r" \\")

    coef, se = cell_rows(us_epu_noceo, "{:.4f}", "{:.4f}")
    lines.append(r"US EPU (log, \citeA{baker2016}) & " + " & ".join(coef) + r" \\")
    lines.append(r" & " + " & ".join(se) + r" \\")

    coef, se = cell_rows(gepu_noceo, "{:.4f}", "{:.4f}")
    lines.append(r"Global EPU (log, \citeA{davis2016}) & " + " & ".join(coef) + r" \\")
    lines.append(r" & " + " & ".join(se) + r" \\")

    lines.append(r"\midrule")
    n_cells = []
    for (iv, fe) in [("UncAnsNoCEO", "industry"), ("UncAnsNoCEO", "firm"),
                     ("UncPreNoCEO", "industry"), ("UncPreNoCEO", "firm")]:
        ns = [prisk_noceo[(iv, fe)][3], us_epu_noceo[(iv, fe)][3], gepu_noceo[(iv, fe)][3]]
        n_cells.append(f"{min(ns):,}--{max(ns):,}")
    lines.append(r"N range & " + " & ".join(n_cells) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{minipage}{\linewidth}")
    lines.append(r"\vspace{4pt}\scriptsize")
    lines.append(r"\textit{Notes:} Companion to Table~\ref{tab:driver_matrix}. Each cell reports the coefficient and cluster-robust standard error (in parentheses) on the respective driver variable from a PanelOLS regression of the non-CEO manager speech-uncertainty regressand (UncAnsNoCEO or UncPreNoCEO) on the driver plus the standard control set. PRisk is firm-clustered; US EPU and Global EPU are two-way firm $\times$ calendar-year-quarter clustered. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed positive on all drivers). Significant coefficients in \textbf{bold}.")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")
    lines.append(r"")

    # B.2 — H14c Mgr-pool
    lines.append(r"\subsection{Outside-World Reaction --- Manager-Pool Coefficients}")
    lines.append(r"\label{app:additional:reaction}")
    lines.append(r"")
    lines.append(r"Table~\ref{tab:h14c_mgr} reports the manager-pool speech-uncertainty coefficients from the same joint four-regressor specification used in \S\ref{sec:additional:reaction}. The H14c suite includes both CEO and non-CEO manager (pooled) speech-uncertainty regressors in every column; the body table reports the CEO coefficients, and this table reports the corresponding manager-pool coefficients. Dependent variable is the 26-day post-call relative bid-ask spread Spread\textsubscript{25D}.")
    lines.append(r"")
    lines.append(r"\begin{landscape}")
    lines.append(r"\begin{table}[H]")
    lines.append(r"\setlength{\tabcolsep}{3pt}")
    lines.append(r"\renewcommand{\arraystretch}{0.85}")
    lines.append(r"\centering")
    lines.append(r"\caption{H14c Manager-Pool Coefficients --- Companion to \S\ref{sec:additional:reaction}}")
    lines.append(r"\label{tab:h14c_mgr}")
    lines.append(r"\scriptsize")
    lines.append(r"\begin{tabular}{l" + "c" * 12 + "}")
    lines.append(r"\toprule")
    lines.append(r" & " + " & ".join(f"({i})" for i in range(1, 13)) + r" \\")
    # DV header (contemp [1-6] vs lead [7-12])
    lines.append(r" & \multicolumn{6}{c}{Spread\textsubscript{25D}$_t$} & \multicolumn{6}{c}{Spread\textsubscript{25D}$_{t+1}$} \\")
    lines.append(r"\cmidrule(lr){2-7} \cmidrule(lr){8-13}")
    lines.append(r"\midrule")

    def mgr_row(label: str, beta_key: str, se_key: str, p_key: str) -> None:
        coef = []
        sec = []
        for r in h14c_rows:
            beta = float(r[beta_key])
            se = float(r[se_key])
            p_one = float(r[p_key])
            # Convert p_one to a pseudo p_two for stars_one (stars_one uses p_one = p_two/2)
            # Equivalent: if beta>0 and p_one<threshold, star it.
            if beta > 0 and p_one < 0.01: stars = "***"
            elif beta > 0 and p_one < 0.05: stars = "**"
            elif beta > 0 and p_one < 0.10: stars = "*"
            else: stars = ""
            coef.append(fmt_coef(beta, stars, "{:.4f}"))
            sec.append(f"({se:.4f})")
        lines.append(f"{label} & " + " & ".join(coef) + r" \\")
        lines.append(f" & " + " & ".join(sec) + r" \\")

    mgr_row(r"UncAnsMgr", "UncAnsMgr_beta", "UncAnsMgr_se", "UncAnsMgr_p_one")
    mgr_row(r"UncPreMgr", "UncPreMgr_beta", "UncPreMgr_se", "UncPreMgr_p_one")
    lines.append(r"\midrule")
    # FE + Controls indicators
    ctrl_cells = []
    ind_cells = []
    firm_cells = []
    n_cells = []
    r2_cells = []
    for r in h14c_rows:
        ctrl_cells.append("Ext" if r["controls"] == "extended" else "Base")
        fe = r["fe"]
        ind_cells.append("Yes" if fe.startswith("industry") else "")
        firm_cells.append("Yes" if fe.startswith("firm") else "")
        n_cells.append(f"{int(r['n_obs']):,}")
        r2_cells.append(f"{float(r['r2']):.3f}")
    lines.append(r"Controls & " + " & ".join(ctrl_cells) + r" \\")
    lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
    lines.append(r"\midrule")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")
    lines.append(r"$R^2$ & " + " & ".join(r2_cells) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{minipage}{\linewidth}")
    lines.append(r"\vspace{2pt}\scriptsize")
    lines.append(r"\textit{Notes:} Companion to body \S\ref{sec:additional:reaction}. Reports the manager-pool (UncAnsMgr, UncPreMgr) coefficients from the same 4-regressor joint specification whose CEO coefficients appear in the body. Dependent variable: 26-day post-call closing-quote relative bid-ask spread Spread\textsubscript{25D}, scaled to basis points. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed positive). Significant coefficients in \textbf{bold}. Firm-clustered standard errors. Main sample 2002--2018.")
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")
    lines.append(r"\end{landscape}")
    lines.append(r"")

    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(ROOT)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
