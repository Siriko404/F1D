"""Build tab:driver_matrix consolidated table for §IV.1.

Reads high-precision coefficients from model_diagnostics.csv of:
  - H11 PRisk: outputs/econometric/h11_prisk_uncertainty/<ts>/model_diagnostics.csv
  - H24  US EPU: outputs/econometric/h24_us_epu/<ts>/model_diagnostics.csv
  - H24b GEPU:   outputs/econometric/h24b_global_epu/<ts>/model_diagnostics.csv

Table emitted at docs/Draft/per_suite/h24_table.tex (supersedes stale H24 raw
table). Label: tab:driver_matrix (cited in body §IV.1).

Rows: 3 drivers (PRisk, US EPU log, Global EPU log)
Cols: 4 = (UncAnsCEO Industry, UncAnsCEO Firm, UncPreCEO Industry, UncPreCEO Firm)
Inference: one-tailed positive on all drivers.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
H11_DIR = ROOT / "outputs" / "econometric" / "h11_prisk_uncertainty"
H24_DIR = ROOT / "outputs" / "econometric" / "h24_us_epu"
H24B_DIR = ROOT / "outputs" / "econometric" / "h24b_global_epu"
OUT_FILE = ROOT / "docs" / "Draft" / "per_suite" / "h24_table.tex"


def latest(dir_: Path) -> Path:
    subs = sorted([p for p in dir_.iterdir() if p.is_dir()], reverse=True)
    return subs[0]


def read_h11_cells(ts_dir: Path) -> dict[tuple[str, str], tuple[float, float, float, int]]:
    """{(dv, fe): (beta, se, p_two, n_obs)} from H11 diagnostics (Main sample only)."""
    csv_path = ts_dir / "model_diagnostics.csv"
    result: dict[tuple[str, str], tuple[float, float, float, int]] = {}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["sample"] != "Main":
                continue
            dv = row["dv"]
            fe = row["fe"]
            if dv in ("UncAnsCEO", "UncPreCEO") and fe in ("industry", "firm"):
                result[(dv, fe)] = (
                    float(row["beta_prisk"]),
                    float(row["beta_prisk_se"]),
                    float(row["beta_prisk_p_two"]),
                    int(row["n_obs"]),
                )
    return result


def read_macro_cells(ts_dir: Path) -> dict[tuple[str, str], tuple[float, float, float, int]]:
    """{(dv, fe): (beta, se, p_two, n_obs)} from H24/H24b diagnostics."""
    csv_path = ts_dir / "model_diagnostics.csv"
    result: dict[tuple[str, str], tuple[float, float, float, int]] = {}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dv = row["dv"]
            fe = row["fe"]
            if dv in ("UncAnsCEO", "UncPreCEO") and fe in ("industry", "firm"):
                result[(dv, fe)] = (
                    float(row["beta"]),
                    float(row["beta_se"]),
                    float(row["beta_p_two"]),
                    int(row["n_obs"]),
                )
    return result


def stars_one(beta: float, p_two: float) -> str:
    if beta <= 0:
        return ""
    p_one = p_two / 2
    if p_one < 0.01: return "***"
    if p_one < 0.05: return "**"
    if p_one < 0.10: return "*"
    return ""


def cell_rows(data: dict, beta_fmt: str, se_fmt: str) -> tuple[list[str], list[str]]:
    coef_cells: list[str] = []
    se_cells: list[str] = []
    for (iv, fe) in [("UncAnsCEO", "industry"), ("UncAnsCEO", "firm"),
                     ("UncPreCEO", "industry"), ("UncPreCEO", "firm")]:
        beta, se, p_two, _ = data[(iv, fe)]
        stars = stars_one(beta, p_two)
        beta_str = beta_fmt.format(beta)
        if stars:
            coef_cells.append(r"\textbf{" + beta_str + r"}$^{" + stars + "}$")
        else:
            coef_cells.append(beta_str)
        se_cells.append("(" + se_fmt.format(se) + ")")
    return coef_cells, se_cells


def main() -> None:
    h11_latest = latest(H11_DIR)
    h24_latest = latest(H24_DIR)
    h24b_latest = latest(H24B_DIR)
    print(f"H11:  {h11_latest.relative_to(ROOT)}")
    print(f"H24:  {h24_latest.relative_to(ROOT)}")
    print(f"H24b: {h24b_latest.relative_to(ROOT)}")

    prisk = read_h11_cells(h11_latest)
    us_epu = read_macro_cells(h24_latest)
    gepu = read_macro_cells(h24b_latest)

    if len(prisk) != 4 or len(us_epu) != 4 or len(gepu) != 4:
        raise RuntimeError(
            f"Missing cells: PRisk={len(prisk)} US_EPU={len(us_epu)} GEPU={len(gepu)}"
        )

    lines: list[str] = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Consolidated Driver Matrix: Exogenous Uncertainty Drivers of CEO Speech Uncertainty}")
    lines.append(r"\label{tab:driver_matrix}")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{lcccc}")
    lines.append(r"\toprule")
    lines.append(r" & \multicolumn{2}{c}{UncAnsCEO} & \multicolumn{2}{c}{UncPreCEO} \\")
    lines.append(r"\cmidrule(lr){2-3} \cmidrule(lr){4-5}")
    lines.append(r" & Industry FE & Firm FE & Industry FE & Firm FE \\")
    lines.append(r"\midrule")

    # PRisk (scientific-scale: beta ~1e-4, use 5 decimal + SE small)
    coef_p, se_p = cell_rows(prisk, "{:.5f}", "{:.5f}")
    lines.append(r"PRisk (firm-call, \citeA{hassan2020}) & " + " & ".join(coef_p) + r" \\")
    lines.append(r" & " + " & ".join(se_p) + r" \\")

    # US EPU log (beta ~0.01-0.02, 4 decimal)
    coef_u, se_u = cell_rows(us_epu, "{:.4f}", "{:.4f}")
    lines.append(r"US EPU (log, \citeA{baker2016}) & " + " & ".join(coef_u) + r" \\")
    lines.append(r" & " + " & ".join(se_u) + r" \\")

    # Global EPU log (beta ~0.02-0.03, 4 decimal)
    coef_g, se_g = cell_rows(gepu, "{:.4f}", "{:.4f}")
    lines.append(r"Global EPU (log, \citeA{davis2016}) & " + " & ".join(coef_g) + r" \\")
    lines.append(r" & " + " & ".join(se_g) + r" \\")

    lines.append(r"\midrule")

    n_cells = []
    for (iv, fe) in [("UncAnsCEO", "industry"), ("UncAnsCEO", "firm"),
                     ("UncPreCEO", "industry"), ("UncPreCEO", "firm")]:
        ns = [prisk[(iv, fe)][3], us_epu[(iv, fe)][3], gepu[(iv, fe)][3]]
        n_cells.append(f"{min(ns):,}--{max(ns):,}")
    lines.append(r"N range & " + " & ".join(n_cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{minipage}{\linewidth}")
    lines.append(r"\vspace{4pt}\scriptsize")
    lines.append(
        r"\textit{Notes:} Each cell reports the coefficient and cluster-robust "
        r"standard error (in parentheses) on the respective driver variable "
        r"from a PanelOLS regression of the CEO speech-uncertainty regressand "
        r"(UncAnsCEO or UncPreCEO) on the driver plus the standard control set. "
        r"PRisk is the firm-call-level political-risk count of "
        r"\citeA{hassan2020}; US EPU is the news-based US Economic Policy "
        r"Uncertainty index of \citeA{baker2016} (natural log, calendar-monthly "
        r"match); Global EPU is the GDP-weighted global extension of "
        r"\citeA{davis2016} (natural log, calendar-monthly match). "
        r"Industry FE uses Fama-French 12 dummies; firm FE uses \texttt{gvkey} "
        r"entity effects; calendar-year FE absorbed in all specifications. "
        r"Standard errors clustered at firm level (PRisk, suite H11); two-way "
        r"firm $\times$ calendar-year-quarter (US EPU and Global EPU, suites "
        r"H24 and H24b). $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ "
        r"(one-tailed positive on all drivers). Significant coefficients in "
        r"\textbf{bold}."
    )
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table}")

    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(ROOT)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
