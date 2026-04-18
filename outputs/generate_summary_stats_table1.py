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
  outputs/summary_stats_table1.tex             — \\input fragment for main.tex
  outputs/summary_stats_table1_standalone.tex  — preview-compile document
  outputs/summary_stats_table1.pdf             — compiled preview
  outputs/summary_stats_table1.csv             — tidy stats table
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

REPO_ROOT = Path(__file__).resolve().parents[1]
RENDER_ORDER = REPO_ROOT / "config" / "suite_render_order.yaml"
SS_CONFIG = REPO_ROOT / "config" / "summary_stats_config.yaml"
ECONOMETRIC = REPO_ROOT / "outputs" / "econometric"
VARIABLES = REPO_ROOT / "outputs" / "variables"
OUT_DIR = REPO_ROOT / "outputs"

MAIN_SAMPLE_EXCLUDE_FF12 = [8, 11]  # Finance, Utility


def find_latest_spec(suite_id: str) -> Optional[Path]:
    matches = sorted(
        ECONOMETRIC.glob(f"**/suite_spec_{suite_id}.json"),
        key=lambda p: p.parent.name,
        reverse=True,
    )
    return matches[0] if matches else None


def load_spec_panel(suite_id: str, panel_dir_alias: Optional[dict] = None):
    """Load (spec, panel). If spec.dir_name doesn't have a physical panel
    (sub-suites that share a parent's panel), consult panel_dir_alias map."""
    spec_path = find_latest_spec(suite_id)
    if spec_path is None:
        return None, None
    spec = load_suite_spec(spec_path)
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
        return spec, pd.read_parquet(panel_ts / f"{dn}_panel.parquet")
    return spec, None


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
        "p25": float(data.quantile(0.25)),
        "p50": float(data.median()),
        "p75": float(data.quantile(0.75)),
    }


def fmt(x: float, nd: int = 4) -> str:
    if pd.isna(x):
        return "---"
    return f"{x:.{nd}f}"


def tex_escape(s: str) -> str:
    return s.replace("_", r"\_")


def build_panels(include_suites, specs, panels, anchor_overrides, exclude_vars):
    """Classify vars into IV / DV / Control with priority IV > DV > Control.

    Many sub-suites (H7b/c/d/e, H14b-e, H1.1/H1.2, H12b, H19b, H20b, H24/H24b/H25)
    share a parent suite's panel. The spec's dir_name names a logical runner, not
    necessarily a physical panel directory. So per-var routing falls through the
    ordered list of ALL suites mentioning the var, picking the first one that has
    both a loaded panel AND the column.
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
        """Return (suite_id, panel) for the anchor: config override first, then
        first candidate suite with a loaded panel containing the column."""
        ordered = []
        if var in anchor_overrides:
            ordered.append(anchor_overrides[var])
        ordered += var_candidates.get(var, [])
        for sid in ordered:
            if sid in panels and var in panels[sid].columns:
                return sid, panels[sid]
        return None, None

    rows = []
    for panel_label, vars_list in [
        ("A. Independent Variables", sorted(iv_set)),
        ("B. Dependent Variables", sorted(dv_set)),
        ("C. Firm Controls", sorted(control_set)),
    ]:
        for var in vars_list:
            sid, panel = resolve_anchor(var)
            if panel is None:
                print(f"  [skip] {var}: no loaded panel contains this column")
                continue
            sample = apply_main_filter(panel)
            stats = compute_stats(sample[var])
            if stats is None:
                print(f"  [skip] {var}: all NaN in {sid} Main sample")
                continue
            rows.append(
                {
                    "panel": panel_label,
                    "variable": var,
                    "unit": detect_unit(panel),
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
    """Emit \\input-able LaTeX fragment (no preamble, no \\begin{document})."""
    col_fmt = "llcrrrrrr"
    header = (
        "Variable & Unit & N & Mean & SD & P25 & Median & P75 \\\\"
    )
    lines = [
        "% Auto-generated by outputs/generate_summary_stats_table1.py",
        "% Fragment for \\input; wrap in table float in main.tex",
        f"\\begin{{tabular}}{{{col_fmt}}}",
        "\\toprule",
        header,
        "\\midrule",
    ]
    current_panel = None
    for _, row in stats.iterrows():
        if row["panel"] != current_panel:
            if current_panel is not None:
                lines.append("\\midrule")
            lines.append(
                f"\\multicolumn{{9}}{{l}}{{\\textit{{{row['panel']}}}}} \\\\"
            )
            lines.append("\\midrule")
            current_panel = row["panel"]
        lines.append(
            f"{tex_escape(row['variable'])} & {row['unit']} & "
            f"{int(row['n']):,} & {fmt(row['mean'])} & {fmt(row['sd'])} & "
            f"{fmt(row['p25'])} & {fmt(row['p50'])} & {fmt(row['p75'])} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}"]

    footnote_lines = [
        "",
        "% Caption + footnote (caller supplies \\caption + \\label)",
        "\\begin{minipage}{\\textwidth}",
        "\\footnotesize",
        f"\\textit{{Notes:}} Summary statistics for variables used in the hypothesis tests. "
        f"Sample period: {balance.get('year_min', '')}--{balance.get('year_max', '')}. "
        f"Anchor sample (H1, Main): {balance['total_calls']:,} earnings-call observations "
        f"across {balance['unique_firms']:,} firms. "
        f"Unit column: C = call-level, F = firm-year. "
        f"N varies by row because each variable is summarized on its anchor panel's Main "
        f"sample (complete cases per variable); per-suite samples differ due to lags, "
        f"control availability, and merges. ",
        "\\end{minipage}",
    ]
    out_path.write_text("\n".join(lines + footnote_lines), encoding="utf-8")
    print(f"  wrote: {out_path.relative_to(REPO_ROOT)}")


def emit_latex_standalone(fragment_path: Path, out_path: Path) -> None:
    """Emit standalone compile-able document that \\input's the fragment."""
    doc = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=2cm]{geometry}
\usepackage{newtxtext,newtxmath}
\usepackage{booktabs}
\usepackage{caption}
\begin{document}
\begin{table}[ht]
  \centering
  \caption{Summary Statistics}
  \label{tab:summary_stats_table1}
""" + f"  \\input{{{fragment_path.stem}}}\n" + r"""\end{table}
\end{document}
"""
    out_path.write_text(doc, encoding="utf-8")
    print(f"  wrote: {out_path.relative_to(REPO_ROOT)}")


def compile_pdf(standalone_tex: Path) -> bool:
    try:
        result = subprocess.run(
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

    specs, panels = {}, {}
    for sid in include_suites:
        s, p = load_spec_panel(sid, panel_dir_alias)
        if s is None:
            print(f"  [miss] {sid}: no spec file found")
            continue
        if p is None:
            print(f"  [miss] {sid}: spec OK, panel missing")
            specs[sid] = s
            continue
        specs[sid], panels[sid] = s, p
    print(
        f"\nLoaded {len(specs)}/{len(include_suites)} specs, "
        f"{len(panels)}/{len(include_suites)} panels"
    )

    stats = build_panels(include_suites, specs, panels, anchor_overrides, exclude_vars)
    stats = append_extra_vars(stats, extra_vars, panels)
    print(f"\nVariables summarized: {len(stats)}")
    print(stats.groupby("panel").size().to_string())

    balance = compute_panel_balance(panels["H1"]) if "H1" in panels else {
        "total_calls": 0, "unique_firms": 0, "year_min": "?", "year_max": "?"
    }

    stats.to_csv(OUT_DIR / "summary_stats_table1.csv", index=False)
    print(f"\n  wrote: outputs/summary_stats_table1.csv")

    fragment = OUT_DIR / "summary_stats_table1.tex"
    standalone = OUT_DIR / "summary_stats_table1_standalone.tex"
    emit_latex_fragment(stats, balance, fragment)
    emit_latex_standalone(fragment, standalone)
    compile_pdf(standalone)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
