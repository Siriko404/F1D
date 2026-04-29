#!/usr/bin/env python3
"""Generate thesis Table 1: Summary Statistics (adaptive-scope).

Reads ALL suites from config/suite_render_order.yaml. Pulls IVs + DVs +
controls from each suite_spec_<id>.json (Phase-8 canonical). Computes
mean/sd/p25/median/p75/N per variable from its anchor panel (Main sample,
per-variable complete cases).

Scope curation: edit config/summary_stats_config.yaml — NOT this script.
Per feedback_adaptive_scope_via_config.md: build wide, filter via config.
Per feedback_table_completeness.md: report all variables completely.

Outputs:
  docs/Draft/summary_stats.tex             — \\input fragment for main.tex
  docs/Draft/summary_stats_standalone.tex  — preview-compile document
  docs/Draft/summary_stats.pdf             — compiled preview
  docs/Draft/summary_stats.csv             — tidy stats table
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml

from f1d.shared.outputs import load_suite_spec
from f1d.shared.path_utils import get_latest_output_dir

REPO_ROOT = Path(__file__).resolve().parents[2]  # docs/Draft/<script> → repo root
RENDER_ORDER = REPO_ROOT / "config" / "suite_render_order.yaml"
SS_CONFIG = REPO_ROOT / "config" / "summary_stats_config.yaml"
ECONOMETRIC = REPO_ROOT / "outputs" / "econometric"
VARIABLES = REPO_ROOT / "outputs" / "variables"
OUT_DIR = Path(__file__).resolve().parent  # outputs land alongside the script (docs/Draft/)

MAIN_SAMPLE_EXCLUDE_FF12 = [8, 11]  # Finance, Utility


def find_latest_spec(suite_id: str) -> Optional[Path]:
    matches = sorted(
        ECONOMETRIC.glob(f"**/suite_spec_{suite_id}.json"),
        key=lambda p: p.parent.name,
        reverse=True,
    )
    return matches[0] if matches else None


def load_spec_panel(suite_id: str, panel_dir_alias: Optional[dict] = None):
    """Load (spec, panel, runner_stats). If spec.dir_name doesn't have a physical
    panel (sub-suites that share a parent's panel), consult panel_dir_alias map.

    Also loads runner-output summary_stats.csv (sibling of suite_spec_*.json) so
    runtime-computed IVs (e.g., ClarityCEO, UncResCEO from CEO-FE residualization)
    can be reported even though they're absent from the panel parquet.
    """
    spec_path = find_latest_spec(suite_id)
    if spec_path is None:
        return None, None, None
    spec = load_suite_spec(spec_path)

    runner_stats = None
    runner_csv = spec_path.parent / "summary_stats.csv"
    if runner_csv.exists():
        try:
            df = pd.read_csv(runner_csv)
            if {"Sample", "Col", "N", "Mean", "SD", "Min", "P25", "Median", "P75", "Max"}.issubset(df.columns):
                df = df[df["Sample"] == "All"] if "Sample" in df.columns else df
                runner_stats = {
                    row["Col"]: {
                        "n": int(str(row["N"]).replace(",", "")),
                        "mean": float(row["Mean"]),
                        "sd": float(row["SD"]),
                        "min": float(row["Min"]),
                        "p25": float(row["P25"]),
                        "p50": float(row["Median"]),
                        "p75": float(row["P75"]),
                        "max": float(row["Max"]),
                    }
                    for _, row in df.iterrows()
                }
        except Exception as exc:
            print(f"  [warn] {suite_id}: runner csv unparseable ({exc})")

    alias = (panel_dir_alias or {}).get(suite_id)
    candidates = [alias, spec.dir_name] if alias else [spec.dir_name]
    for dn in candidates:
        if dn is None:
            continue
        var_dir = VARIABLES / dn
        if not var_dir.exists():
            continue
        try:
            panel_ts = get_latest_output_dir(
                var_dir, required_file=f"{dn}_panel.parquet"
            )
        except Exception:
            continue
        return spec, pd.read_parquet(panel_ts / f"{dn}_panel.parquet"), runner_stats
    return spec, None, runner_stats


def detect_unit(panel: pd.DataFrame) -> str:
    if "file_name" in panel.columns:
        return "C"
    if "fyearq_int" in panel.columns:
        return "F"
    return "?"


def apply_main_filter(panel: pd.DataFrame) -> pd.DataFrame:
    if "sample" in panel.columns:
        return panel[panel["sample"] == "Main"]
    if "ff12_code" in panel.columns:
        return panel[~panel["ff12_code"].isin(MAIN_SAMPLE_EXCLUDE_FF12)]
    return panel


def compute_stats(series: pd.Series) -> Optional[dict]:
    data = series.dropna()
    if len(data) == 0:
        return None
    return {
        "n": len(data),
        "mean": float(data.mean()),
        "sd": float(data.std()),
        "min": float(data.min()),
        "p25": float(data.quantile(0.25)),
        "p50": float(data.median()),
        "p75": float(data.quantile(0.75)),
        "max": float(data.max()),
    }


def fmt(x: float, nd: int = 4) -> str:
    if pd.isna(x):
        return "---"
    return f"{x:.{nd}f}"


def tex_escape(s: str) -> str:
    return s.replace("_", r"\_")


def build_panels(include_suites, specs, panels, runner_stats_map, anchor_overrides, exclude_vars):
    """Classify vars into IV / DV / Control with priority IV > DV > Control.

    Resolves each var via TWO paths:
      (a) panel parquet column (panel-based stats on Main filter)
      (b) runner summary_stats.csv from the suite output dir (runtime-computed
          IVs like ClarityCEO/UncResCEO that aren't stored in the panel parquet)

    Path (a) wins when both are available; path (b) is the fallback.
    """
    iv_set, dv_set, control_set = set(), set(), set()
    var_candidates: dict = {}  # var → ordered list of suites that mention it

    def add(var, sid):
        var_candidates.setdefault(var, []).append(sid)

    for sid in include_suites:
        if sid not in specs:
            continue
        spec = specs[sid]
        for iv in spec.ivs:
            iv_set.add(iv.name); add(iv.name, sid)
        base = list(spec.controls.base)
        ext = list(spec.controls.extended_only)
        for c in base + ext:
            control_set.add(c); add(c, sid)
        for col in spec.columns:
            dv_set.add(col.dv); add(col.dv, sid)

    iv_set -= exclude_vars
    dv_set -= exclude_vars | iv_set
    control_set -= exclude_vars | iv_set | dv_set

    def resolve_anchor(var: str):
        """Return (suite_id, panel, runner_stats) for the anchor.

        Tries panel match first; falls back to runner_stats_map (var → stats dict)
        for runtime-computed IVs not stored in the panel parquet.
        """
        ordered = []
        if var in anchor_overrides:
            ordered.append(anchor_overrides[var])
        ordered += var_candidates.get(var, [])
        # Path (a): panel match
        for sid in ordered:
            if sid in panels and var in panels[sid].columns:
                return sid, panels[sid], None
        # Path (b): runner csv fallback
        for sid in ordered:
            csv_stats = runner_stats_map.get(sid) or {}
            if var in csv_stats:
                return sid, None, csv_stats[var]
        return None, None, None

    rows = []
    for panel_label, vars_list in [
        ("A. Independent Variables", sorted(iv_set)),
        ("B. Dependent Variables", sorted(dv_set)),
        ("C. Firm Controls", sorted(control_set)),
    ]:
        for var in vars_list:
            sid, panel, csv_stats = resolve_anchor(var)
            if panel is None and csv_stats is None:
                print(f"  [skip] {var}: not in any panel column or runner csv")
                continue
            if panel is not None:
                sample = apply_main_filter(panel)
                stats = compute_stats(sample[var])
                unit = detect_unit(panel)
            else:
                stats = csv_stats
                unit = "C"  # runner CSV stats are call-level by construction
            if stats is None:
                print(f"  [skip] {var}: all NaN in {sid} Main sample")
                continue
            rows.append(
                {
                    "panel": panel_label,
                    "variable": var,
                    "unit": unit,
                    "anchor": sid,
                    **stats,
                }
            )
    return pd.DataFrame(rows)


def append_extra_vars(rows_df, extra_vars, panels):
    """Append supplementary vars (raw economic forms whose transformed version
    is what enters the regression). Each entry: name, anchor (suite_id), panel."""
    extra_rows = []
    for ev in extra_vars or []:
        name = ev["name"]
        sid = ev["anchor"]
        target_panel = ev["panel"]
        if sid not in panels:
            print(f"  [skip extra] {name}: anchor suite {sid} has no panel loaded")
            continue
        panel = panels[sid]
        if name not in panel.columns:
            print(f"  [skip extra] {name}: not in {sid} panel")
            continue
        sample = apply_main_filter(panel)
        stats = compute_stats(sample[name])
        if stats is None:
            print(f"  [skip extra] {name}: all NaN in {sid} Main sample")
            continue
        extra_rows.append(
            {
                "panel": target_panel,
                "variable": name,
                "unit": detect_unit(panel),
                "anchor": sid,
                **stats,
            }
        )
    if not extra_rows:
        return rows_df
    extras = pd.DataFrame(extra_rows)
    out = pd.concat([rows_df, extras], ignore_index=True)
    return out.sort_values(["panel", "variable"]).reset_index(drop=True)


def compute_panel_balance(panel: pd.DataFrame) -> dict:
    df = apply_main_filter(panel)
    return {
        "total_calls": int(len(df)),
        "unique_firms": int(df["gvkey"].nunique()),
        "year_min": int(df["year"].min()) if "year" in df.columns else None,
        "year_max": int(df["year"].max()) if "year" in df.columns else None,
    }


def emit_latex_fragment(stats: pd.DataFrame, balance: dict, out_path: Path) -> None:
    """Emit \\input-able longtable fragment.

    NEW CONTRACT (2026-04-18 fix): emits longtable, not tabular. Caller must NOT
    wrap in \\begin{table}...\\end{table} — longtable manages its own floats and
    splits across pages. Caller is responsible for \\caption and \\label inside
    the longtable header (or omit; standalone preview handles both).
    """
    # 10 columns: l(var) l(unit) c(N) r(mean) r(sd) r(min) r(p25) r(p50) r(p75) r(max)
    col_fmt = "llcrrrrrrr"
    n_cols = 10
    notes = (
        f"\\textit{{Notes:}} Summary statistics for variables used in the hypothesis tests. "
        f"Sample period: {balance.get('year_min', '')}--{balance.get('year_max', '')}. "
        f"Anchor sample (H1, Main): {balance['total_calls']:,} earnings-call observations "
        f"across {balance['unique_firms']:,} firms. "
        f"Unit column: C = call-level, F = firm-year. "
        f"N varies by row because each variable is summarized on its anchor panel's Main "
        f"sample (complete cases per variable); per-suite samples differ due to lags, "
        f"control availability, and merges."
    )
    header_row = "Variable & Unit & N & Mean & SD & Min & P25 & Median & P75 & Max \\\\"

    lines = [
        "% Auto-generated by outputs/generate_summary_stats.py",
        "% Longtable fragment — caller must NOT wrap in \\begin{table}.",
        "% Caption + label embedded inside longtable; notes follow as a separate",
        "% paragraph after \\end{longtable} so they don't trigger 'Infinite glue",
        "% shrinkage' on the splitting page.",
        "\\begingroup",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{4pt}",
        f"\\begin{{longtable}}{{{col_fmt}}}",
        "\\caption{Summary Statistics} \\label{tab:summary_stats} \\\\",
        "\\toprule",
        header_row,
        "\\midrule",
        "\\endfirsthead",
        f"\\multicolumn{{{n_cols}}}{{l}}{{\\textit{{(continued from previous page)}}}} \\\\",
        "\\toprule",
        header_row,
        "\\midrule",
        "\\endhead",
        "\\midrule",
        f"\\multicolumn{{{n_cols}}}{{r}}{{\\textit{{(continued on next page)}}}} \\\\",
        "\\endfoot",
        "\\bottomrule",
        "\\endlastfoot",
    ]

    current_panel = None
    for _, row in stats.iterrows():
        if row["panel"] != current_panel:
            if current_panel is not None:
                lines.append("\\midrule")
            lines.append(
                f"\\multicolumn{{{n_cols}}}{{l}}{{\\textit{{{row['panel']}}}}} \\\\"
            )
            lines.append("\\midrule")
            current_panel = row["panel"]
        lines.append(
            f"{tex_escape(row['variable'])} & {row['unit']} & "
            f"{int(row['n']):,} & {fmt(row['mean'])} & {fmt(row['sd'])} & "
            f"{fmt(row['min'])} & {fmt(row['p25'])} & {fmt(row['p50'])} & "
            f"{fmt(row['p75'])} & {fmt(row['max'])} \\\\"
        )
    lines += [
        "\\end{longtable}",
        "",
        "\\noindent",
        f"\\begin{{minipage}}{{\\linewidth}}\\footnotesize\\parindent=0pt {notes}\\end{{minipage}}",
        "\\endgroup",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote: {out_path.relative_to(REPO_ROOT)}")


def emit_latex_standalone(fragment_path: Path, out_path: Path) -> None:
    """Emit standalone compile-able document that \\input's the longtable fragment.

    NOTE: longtable manages own page breaks; do NOT wrap in \\begin{table}...
    UTF-8 inputenc + T1 fontenc handle non-ASCII chars (×, em-dash) from
    upstream variable formulas.
    """
    doc = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=2cm]{geometry}
\usepackage{newtxtext,newtxmath}
\usepackage{textcomp}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{caption}
\begin{document}
""" + f"\\input{{{fragment_path.stem}}}\n" + r"""\end{document}
"""
    out_path.write_text(doc, encoding="utf-8")
    print(f"  wrote: {out_path.relative_to(REPO_ROOT)}")


def compile_pdf(standalone_tex: Path) -> bool:
    """Two pdflatex passes — longtable needs second pass for cross-refs/page numbers."""
    try:
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", standalone_tex.name],
                cwd=standalone_tex.parent,
                capture_output=True,
                timeout=60,
            )
        ok = (standalone_tex.parent / (standalone_tex.stem + ".pdf")).exists()
        if ok:
            print(f"  wrote: outputs/{standalone_tex.stem}.pdf")
        else:
            print(f"  [warn] pdflatex failed, stderr: {result.stderr[:500]!r}")
        return ok
    except FileNotFoundError:
        print("  [warn] pdflatex not on PATH; skipping PDF compile")
        return False


def main() -> int:
    render = yaml.safe_load(RENDER_ORDER.read_text(encoding="utf-8"))
    ss_cfg = yaml.safe_load(SS_CONFIG.read_text(encoding="utf-8")) if SS_CONFIG.exists() else {}

    all_suites = list(render.get("suites", []))
    include_suites = ss_cfg.get("include_suites") or all_suites
    anchor_overrides = ss_cfg.get("anchor_panel") or {}
    exclude_vars = set(ss_cfg.get("exclude_vars") or [])
    panel_dir_alias = ss_cfg.get("panel_dir_alias") or {}
    extra_vars = ss_cfg.get("extra_vars") or []

    print("=" * 70)
    print("Summary Stats Table 1 — adaptive scope")
    print("=" * 70)
    print(f"Suites in render order: {len(all_suites)}")
    print(f"Suites included: {len(include_suites)}")
    print(f"Excluded vars: {sorted(exclude_vars)}")

    specs, panels, runner_stats_map = {}, {}, {}
    for sid in include_suites:
        s, p, rs = load_spec_panel(sid, panel_dir_alias)
        if s is None:
            print(f"  [miss] {sid}: no spec file found")
            continue
        specs[sid] = s
        if p is not None:
            panels[sid] = p
        if rs is not None:
            runner_stats_map[sid] = rs
        if p is None and rs is None:
            print(f"  [miss] {sid}: spec OK, panel + runner csv both missing")
    print(
        f"\nLoaded {len(specs)}/{len(include_suites)} specs, "
        f"{len(panels)}/{len(include_suites)} panels, "
        f"{len(runner_stats_map)}/{len(include_suites)} runner CSVs"
    )

    stats = build_panels(include_suites, specs, panels, runner_stats_map, anchor_overrides, exclude_vars)
    stats = append_extra_vars(stats, extra_vars, panels)
    print(f"\nVariables summarized: {len(stats)}")
    print(stats.groupby("panel").size().to_string())

    # Anchor balance on whichever HC suite has its panel loaded (v6 thesis-suite first;
    # legacy H1 fallback for older configs).
    balance_anchor_candidates = ["H1.ceo2.decomp", "H1.ceo2.decomp.qtrexp", "H1"]
    balance = None
    for anchor_sid in balance_anchor_candidates:
        if anchor_sid in panels:
            balance = compute_panel_balance(panels[anchor_sid])
            break
    if balance is None:
        balance = {"total_calls": 0, "unique_firms": 0, "year_min": "?", "year_max": "?"}

    stats.to_csv(OUT_DIR / "summary_stats.csv", index=False)
    print(f"\n  wrote: docs/Draft/summary_stats.csv")

    fragment = OUT_DIR / "summary_stats.tex"
    standalone = OUT_DIR / "summary_stats_standalone.tex"
    emit_latex_fragment(stats, balance, fragment)
    emit_latex_standalone(fragment, standalone)
    compile_pdf(standalone)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
