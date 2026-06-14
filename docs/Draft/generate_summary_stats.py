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


_EXCLUDE_PATTERNS = (
    # Mean-centered derivatives (runtime constructs; raw form is what readers want)
    lambda v: v.endswith("_c"),
    # Interaction terms (product of centered IV * moderator; not a primitive)
    lambda v: "_x_" in v,
)
# NOTE: _lead / _lag forms are NOT auto-excluded -- body suites report them
# directly as DVs (CashRatio_lead, BGTLevel_Spread_lead1) or as IVs
# (PRisk_lag2), so they belong in Table 1.  Add explicit exclude_vars
# entries if a specific lead/lag form should be suppressed.


def is_excluded_by_pattern(var: str) -> bool:
    """Per advisor 5-fix #4: replace hand-curated exclude_vars enumeration
    with naming-pattern test for centered/interaction derivatives.  Adding
    a new interaction (e.g., UncResCEO_c_x_NewModerator) auto-excludes
    without needing to extend exclude_vars in YAML.
    """
    return any(pat(var) for pat in _EXCLUDE_PATTERNS)


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

    # Per advisor 5-fix #4: combine pattern-test (auto-excludes centered /
    # interaction / lead / lag forms) with explicit exclude_vars (legacy +
    # historical entries that don't fit the pattern).
    pattern_excluded = {v for v in iv_set | dv_set | control_set if is_excluded_by_pattern(v)}
    full_exclude = exclude_vars | pattern_excluded
    iv_set -= full_exclude
    dv_set -= full_exclude | iv_set
    control_set -= full_exclude | iv_set | dv_set

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
    coverage_failures: list[str] = []
    for panel_label, vars_list in [
        ("A. Independent Variables", sorted(iv_set)),
        ("B. Dependent Variables", sorted(dv_set)),
        ("C. Firm Controls", sorted(control_set)),
    ]:
        for var in vars_list:
            sid, panel, csv_stats = resolve_anchor(var)
            if panel is None and csv_stats is None:
                # Per advisor 5-fix #3: COVERAGE FAILURE.  Used vars must have
                # an anchor panel or runner CSV; silently skipping them leaves
                # readers with a regression cell whose construct has no row in
                # Table 1.  Collect all failures, then raise once at end.
                coverage_failures.append(var)
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
    if coverage_failures:
        raise RuntimeError(
            "summary_stats coverage failure -- the following thesis-suite "
            "variables have no anchor panel column AND no runner CSV row "
            "(silent-skip would leave Table 1 incomplete):\n  - "
            + "\n  - ".join(sorted(coverage_failures))
            + "\nFix steps: (a) add to summary_stats_config.exclude_vars if "
            "intentionally suppressed (e.g., interaction terms); or (b) add "
            "an anchor_panel: mapping for the var; or (c) ensure the runner "
            "emits the var in summary_stats.csv."
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
        f"control availability, and merges. "
        f"\\texttt{{PRisk}} is \\citet{{hassan2020}}'s scaled political-risk score (a weighted, "
        f"capped bigram index), not a percentage."
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


def _cash_acquirer_treat(repo_root: Path):
    """First >=50%-cash acquisition quarter per firm (gvkey -> dq), for PreAnnounceQtr.
    Ported from scripts/gen_empire_did_table.py (sdc + manifest, cash arm pc>=50).
    Returns a DataFrame[gvkey, dq] or None if the SDC/manifest inputs are absent."""
    sdc_path = repo_root / "inputs" / "SDC" / "sdc-ma-merged.parquet"
    man_glob = sorted(repo_root.glob("outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"))
    if not sdc_path.exists() or not man_glob:
        print("  [warn] PreAnnounceQtr: SDC or manifest input missing -> skipped")
        return None
    s = pd.read_parquet(
        sdc_path,
        columns=["Acquiror 6-digit CUSIP", "Acquiror Nation", "Acquiror Public Status",
                 "Date Announced", "Deal Status", "Percentage of Cash"],
    ).rename(columns={"Acquiror 6-digit CUSIP": "c6", "Percentage of Cash": "pc"})
    s["da"] = pd.to_datetime(s["Date Announced"], errors="coerce")
    yr = s["da"].dt.year
    known = ((yr >= 2002) & (yr <= 2018)
             & (s["Acquiror Nation"] == "United States")
             & (s["Acquiror Public Status"] == "Public")
             & (s["Deal Status"].isin(["Completed", "Pending", "Withdrawn"]))
             & s["pc"].notna())
    cd = s[known & (s["pc"] >= 50)].copy()                       # cash arm: >=50% cash
    cd["dq"] = cd["da"].dt.year * 4 + (cd["da"].dt.quarter - 1)
    first = cd.sort_values("dq").groupby("c6", as_index=False)["dq"].first()
    m = pd.read_parquet(man_glob[-1], columns=["gvkey", "cusip"])
    m["gvkey"] = m["gvkey"].astype(str).str.zfill(6)
    m["c6"] = m["cusip"].astype(str).str[:6]
    treat = m[["gvkey", "c6"]].drop_duplicates("gvkey").merge(first, on="c6", how="inner")
    return treat[["gvkey", "dq"]].drop_duplicates("gvkey")


def main() -> int:
    render = yaml.safe_load(RENDER_ORDER.read_text(encoding="utf-8"))
    ss_cfg = yaml.safe_load(SS_CONFIG.read_text(encoding="utf-8")) if SS_CONFIG.exists() else {}

    all_suites = list(render.get("suites", []))
    # Scope source of truth (2026-06-14 empire-thesis lock): summary_stats_suites: in
    # summary_stats_config.yaml names exactly the suite-framework tables in the thesis
    # (H11/H24/H24b convergent validity). Falls back to render.thesis_suites (the legacy
    # all_tables list) only if that key is absent. The empire/scrutiny tables are NOT
    # suites; their variables are added via extra_panels + extra_vars below.
    include_suites = list(
        ss_cfg.get("summary_stats_suites")
        or render.get("thesis_suites")
        or ss_cfg.get("include_suites")
        or all_suites
    )
    anchor_overrides = ss_cfg.get("anchor_panel") or {}
    exclude_vars = set(ss_cfg.get("exclude_vars") or [])
    panel_dir_alias = ss_cfg.get("panel_dir_alias") or {}
    extra_vars = ss_cfg.get("extra_vars") or []

    print("=" * 70)
    print("Summary Stats Table 1 — adaptive scope")
    print("=" * 70)
    print(f"Suites in render order: {len(all_suites)}")
    print(f"Thesis suites (source: suite_render_order.yaml): {len(include_suites)}")
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

    # --- Extra anchor panels (empire/scrutiny coverage) -------------------------------
    # These are NOT in include_suites, so their columns do NOT enter the IV/DV/control
    # var sets; they are loaded only as ANCHOR TARGETS for vars routed here via
    # anchor_panel (config) or appended via extra_vars. This is how the empire-building
    # event-study + analyst-scrutiny tables (standalone scripts, not the suite framework)
    # get all-universe rows in Table 1.
    #   EMPIRE = the h1_cash_holdings CALL panel: canonical cash universe for CashRatio,
    #            the firm-financial control set, and the derived analyst-scrutiny vars
    #            (CashScrutiny/HighCashScrutiny constructed here, ported from
    #            scripts/gen_empire_did_table.py:base_panel; HighCash = top-tercile cash).
    #   RESID  = the all-call DWZ residual file: UncResCEO on its FULL universe (the suite
    #            runner CSV would give the convergent estimation sample, not the universe).
    extra_panels = ss_cfg.get("extra_panels") or {}
    score_parquet = REPO_ROOT / "tmp" / "_cash_stock_score_call.parquet"

    def _latest_glob(pattern: str):
        hits = sorted(REPO_ROOT.glob(pattern))
        return hits[-1] if hits else None

    if "EMPIRE" in extra_panels:
        emp_path = _latest_glob(
            f"outputs/variables/{extra_panels['EMPIRE']}/*/{extra_panels['EMPIRE']}_panel.parquet"
        )
        if emp_path is not None:
            emp = pd.read_parquet(emp_path)
            emp_main = emp[emp["sample"] == "Main"] if "sample" in emp.columns else emp
            # Derived analyst-scrutiny vars (computed on the Main call universe).
            if score_parquet.exists() and "file_name" in emp.columns:
                score = pd.read_parquet(score_parquet, columns=["file_name", "stock_score"])
                emp = emp.merge(score, on="file_name", how="left")
                emp["CashScrutiny"] = emp["stock_score"] * 100.0  # % analyst Q&A turns on cash
                med = emp.loc[emp.get("sample", "Main") == "Main", "CashScrutiny"].median() \
                    if "sample" in emp.columns else emp["CashScrutiny"].median()
                emp["HighCashScrutiny"] = np.where(emp["CashScrutiny"] > med, 1.0, 0.0)
                emp.loc[emp["CashScrutiny"].isna(), "HighCashScrutiny"] = np.nan
            if "CashRatio" in emp.columns:
                terc = emp_main["CashRatio"].quantile(2.0 / 3.0)  # top-tercile threshold (Main)
                emp["HighCash"] = np.where(emp["CashRatio"] >= terc, 1.0, 0.0)
                emp.loc[emp["CashRatio"].isna(), "HighCash"] = np.nan
                if {"gvkey", "start_date"}.issubset(emp.columns):
                    sd = pd.to_datetime(emp["start_date"])
                    emp["_g"] = emp["gvkey"].astype(str).str.zfill(6)
                    emp["_cq"] = sd.dt.year * 4 + (sd.dt.quarter - 1)  # calendar year-quarter index
                    emp = emp.sort_values(["_g", "_cq"])
                    # CashRatio one-quarter within-firm lag (partial-adjustment control;
                    # consecutive quarters only) -- ported from gen_empire_did_table.base_panel.
                    emp["CashRatio_lag"] = emp.groupby("_g")["CashRatio"].shift(1)
                    _pcq = emp.groupby("_g")["_cq"].shift(1)
                    emp.loc[_pcq != emp["_cq"] - 1, "CashRatio_lag"] = np.nan
                    # PreAnnounceQtr = 1[the single quarter before the firm's first >=50%-cash
                    # deal]. Defined on the FULL Main panel (post-announcement quarters NOT
                    # dropped -> consistent with every other row; never-acquirers = 0). The
                    # regression sample drops post-quarters, so its prevalence differs slightly.
                    treat = _cash_acquirer_treat(REPO_ROOT)
                    if treat is not None:
                        emp = emp.merge(treat.rename(columns={"gvkey": "_g"}), on="_g", how="left")
                        emp["PreAnnounceQtr"] = (emp["_cq"] - emp["dq"] == -1).astype(float)
                        emp = emp.drop(columns=["dq"])
                        print(f"  [extra] PreAnnounceQtr: {int(emp['PreAnnounceQtr'].sum()):,} pre-announce quarters flagged")
                    emp = emp.drop(columns=["_g", "_cq"])
            panels["EMPIRE"] = emp
            print(f"  [extra] EMPIRE ({extra_panels['EMPIRE']}): {len(emp):,} rows + derived scrutiny vars")
        else:
            print(f"  [warn] EMPIRE panel {extra_panels['EMPIRE']} not found")

    if "RESID" in extra_panels:
        resid_path = _latest_glob(extra_panels["RESID"])
        if resid_path is not None:
            panels["RESID"] = pd.read_parquet(resid_path)
            print(f"  [extra] RESID ({resid_path.name}): {len(panels['RESID']):,} rows (all-call UncResCEO)")
        else:
            print(f"  [warn] RESID panel {extra_panels['RESID']} not found")

    stats = build_panels(include_suites, specs, panels, runner_stats_map, anchor_overrides, exclude_vars)
    stats = append_extra_vars(stats, extra_vars, panels)
    print(f"\nVariables summarized: {len(stats)}")
    print(stats.groupby("panel").size().to_string())

    # Anchor balance on whichever HC suite has its panel loaded (v6 thesis-suite first;
    # legacy H1 fallback for older configs).
    balance_anchor_candidates = ["EMPIRE", "H1.ceo2.decomp", "H1.ceo2.decomp.qtrexp", "H1"]
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
