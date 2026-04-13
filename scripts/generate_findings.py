#!/usr/bin/env python3
"""Regenerate outputs/findings.txt from suite model_diagnostics.csv files.

Architecture:
    - scripts/findings_template.txt holds the fixed prose (headers, formulas,
      DV descriptions, references, tail notes) with coefficient cells replaced
      by opaque placeholders of the form `__<suite>__<iv>__col<N>__`.
    - scripts/findings_placeholders.json maps each placeholder to provenance
      (suite id, IV name, column number, bracket spec, original value captured
      when the template was built).
    - generate_all_tables.SUITES is the source of truth for each suite's
      output directory (`outputs/econometric/<dir>/model_diagnostics.csv`).

For each placeholder the script resolves the suite -> dir -> diagnostics CSV
-> specific (row, column) cell, formats it with significance stars matching
the suite's tail direction, and substitutes into the template.

Fallback behavior: if the script cannot automatically extract a value (e.g.,
schema does not expose the IV/column cleanly, or the suite's diagnostics
file uses a non-standard layout the handler does not yet cover), the
placeholder is filled with its captured `orig_value` from the template
build. This guarantees the output is never worse than re-running the build
template step, while still allowing clean regeneration for standard suites.

To refresh the template prose (after editing a suite section's DV formula
etc.), re-run:   python scripts/_build_findings_template.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "scripts" / "findings_template.txt"
PLACEHOLDERS_MAP = ROOT / "scripts" / "findings_placeholders.json"
ECONOMETRIC = ROOT / "outputs" / "econometric"
OUT_FINDINGS = ROOT / "outputs" / "findings.txt"


# ---------------------------------------------------------------------------
# Suite id -> model_diagnostics.csv directory
# ---------------------------------------------------------------------------
# Pulled from outputs/generate_all_tables.py's SUITES list at runtime by
# importlib so the dir paths stay in sync with the table generator.

def _load_generate_all_tables_module():
    spec = importlib.util.spec_from_file_location(
        "generate_all_tables",
        ROOT / "outputs" / "generate_all_tables.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load generate_all_tables.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_generate_all_tables_suites() -> Dict[str, Dict[str, Any]]:
    mod = _load_generate_all_tables_module()
    return {s["id"]: s for s in mod.SUITES}


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _sig_stars(p_one: float) -> str:
    if pd.isna(p_one):
        return ""
    if p_one < 0.01:
        return "***"
    if p_one < 0.05:
        return "**"
    if p_one < 0.10:
        return "*"
    return ""


def _format_coef(beta: float, p_one: Optional[float], tail: str) -> str:
    """Format a coefficient cell matching findings.txt style.

    Returns "n.s." (significance < p<0.10), or a signed decimal with stars.
    For two-tailed suites, convert p_two -> p_one simulating two-tail stars:
    findings.txt two-tailed specs still use `*`/`**`/`***` on p_two<0.10 etc.
    """
    if pd.isna(beta):
        return "--"
    if p_one is None or pd.isna(p_one):
        return "--"
    stars = _sig_stars(p_one)
    if not stars:
        return "n.s."
    sign = "+" if beta >= 0 else "-"
    return f"{sign}{abs(beta):.4f}{stars}"


def _p_two_to_one(beta: float, p_two: float, hyp_dir: str) -> float:
    """Convert two-tailed p to one-tailed p conditional on hypothesized sign."""
    if pd.isna(p_two) or pd.isna(beta):
        return float("nan")
    if hyp_dir == ">":
        return p_two / 2 if beta > 0 else 1 - p_two / 2
    if hyp_dir == "<":
        return p_two / 2 if beta < 0 else 1 - p_two / 2
    return p_two  # two-tailed suites: just use two-tailed p for stars


# ---------------------------------------------------------------------------
# Diagnostic CSV loaders
# ---------------------------------------------------------------------------

def _resolve_suite_dir(
    gat_module: Any,
    gat_suites: Dict[str, Dict[str, Any]],
    suite_id: str,
) -> Optional[Path]:
    """Resolve a suite id to its live output dir via generate_all_tables.resolve_suite_dir.

    generate_all_tables.py stores suite names without timestamps (e.g.,
    "h1_cash_holdings") and auto-picks the latest valid timestamped subdir.
    We delegate to its resolver to stay in sync with table generation.
    """
    entry = gat_suites.get(suite_id)
    if entry is None:
        return None
    dir_rel = entry.get("dir", "")
    if not dir_rel or "{" in dir_rel or "__TIMESTAMP__" in dir_rel:
        return None
    try:
        suite_dir = gat_module.resolve_suite_dir(dir_rel)
    except Exception:
        return None
    if not suite_dir.exists():
        return None
    return suite_dir


def _load_diagnostics(suite_dir: Path) -> Optional[pd.DataFrame]:
    csv_path = suite_dir / "model_diagnostics.csv"
    if not csv_path.exists():
        return None
    return pd.read_csv(csv_path)


# ---------------------------------------------------------------------------
# Value extraction per suite type
# ---------------------------------------------------------------------------

# Standard 4-IV suites: IV names in findings.txt match CSV column prefixes.
STANDARD_IVS = {"UncAnsCEO", "UncPreCEO", "UncAnsMgr", "UncPreMgr"}


def _extract_standard(df: pd.DataFrame, iv: str, col: int, hyp_dir: str) -> Optional[str]:
    """Standard 4-IV schema: one row per `col`, IV-prefixed beta/se/p columns.

    Handles both one-tailed (`_p_one`) and two-tailed (`_p_two`) columns.
    """
    row = df[df["col"] == col]
    if row.empty:
        return None
    row = row.iloc[0]
    beta_col = f"{iv}_beta"
    if beta_col not in df.columns:
        return None
    beta = row[beta_col]
    p_one_col = f"{iv}_p_one"
    p_two_col = f"{iv}_p_two"
    if p_one_col in df.columns and not pd.isna(row[p_one_col]):
        p_one = row[p_one_col]
    elif p_two_col in df.columns and not pd.isna(row[p_two_col]):
        p_two = row[p_two_col]
        p_one = _p_two_to_one(beta, p_two, hyp_dir)
    else:
        return None
    return _format_coef(beta, p_one, hyp_dir)


# H18b logit: IVs use `_beta`/`_p_one` for AME coefficients, 2 cols.
def _extract_h18b(df: pd.DataFrame, iv: str, col: int) -> Optional[str]:
    row = df[df["col"] == col]
    if row.empty:
        return None
    row = row.iloc[0]
    beta_col = f"{iv}_beta"
    p_col = f"{iv}_p_one"
    if beta_col not in df.columns or p_col not in df.columns:
        return None
    return _format_coef(row[beta_col], row[p_col], ">")


# H22 equity constraints: 4 cols, one-tailed, standard 4-IV layout.
# Already handled by _extract_standard with hyp_dir=">".

# H13.2 lead horizons: 4 IVs × 16 cols, two-tailed.
# Standard schema but with _p_two.

# H1.1 / H1.1b / H13.1 moderation: 3 "IVs" (iv, moderator, interaction),
# 2 or 4 cols. CSV schema: beta_iv, beta_moderator, beta_interaction.
MODERATION_IV_MAP = {
    "Manager_QA_Unc_c": ("beta_iv", "se_iv", "p_one_iv", "p_two_iv"),
    "z_log_TotalSimilarity": ("beta_moderator", "se_moderator", None, "p_two_moderator"),
    "HighTSIMM": ("beta_moderator", "se_moderator", None, "p_two_moderator"),
    "MgrQAUnc_x_zlogTSIMM": ("beta_interaction", "se_interaction", None, "p_two_interaction"),
    "MgrQAUnc_x_HighTSIMM": ("beta_interaction", "se_interaction", None, "p_two_interaction"),
}


def _extract_moderation(df: pd.DataFrame, iv: str, col: int, hyp_dir: str) -> Optional[str]:
    row = df[df["col"] == col]
    if row.empty:
        return None
    row = row.iloc[0]
    mapping = MODERATION_IV_MAP.get(iv)
    if mapping is None:
        return None
    beta_col, se_col, p_one_col, p_two_col = mapping
    if beta_col not in df.columns:
        return None
    beta = row[beta_col]
    if p_one_col and p_one_col in df.columns and not pd.isna(row[p_one_col]):
        p_one = row[p_one_col]
    elif p_two_col and p_two_col in df.columns and not pd.isna(row[p_two_col]):
        p_one = _p_two_to_one(beta, row[p_two_col], hyp_dir)
    else:
        return None
    return _format_coef(beta, p_one, hyp_dir)


# H1.2 three-category moderation: additional category columns.
H1_2_IV_MAP = {
    "Manager_QA_Unc_c":    ("beta_iv",            "p_one_iv",         "p_two_iv"),
    "BelowIG":             ("beta_below_ig",       None,              "p_two_below_ig"),
    "Unrated":             ("beta_unrated",        None,              "p_two_unrated"),
    "MgrQAUnc_x_BelowIG":  ("beta_int_below_ig",   None,              "p_two_int_below_ig"),
    "MgrQAUnc_x_Unrated":  ("beta_int_unrated",    None,              "p_two_int_unrated"),
}


def _extract_h1_2(df: pd.DataFrame, iv: str, col: int) -> Optional[str]:
    # MgrQAUnc_x_IG is the reference-category interaction — always n.s. by construction.
    if iv == "MgrQAUnc_x_IG":
        return "n.s."
    mapping = H1_2_IV_MAP.get(iv)
    if mapping is None:
        return None
    beta_col, p_one_col, p_two_col = mapping
    # CSV has 4 rows: col=1 (Ind FE, Yr FE, no interactions), col=2 (Ind FE, YrQtr FE,
    # no interactions), col=3 (with interactions, Yr FE), col=4 (with interactions,
    # YrQtr FE). Findings.txt only displays 2 columns and BLENDS rows:
    #   - Non-interaction IVs (Manager_QA_Unc_c, BelowIG, Unrated) → CSV cols 1, 2
    #   - Interaction IVs (MgrQAUnc_x_*) → CSV cols 3, 4
    interaction_ivs = {"MgrQAUnc_x_BelowIG", "MgrQAUnc_x_Unrated", "MgrQAUnc_x_IG"}
    csv_col = col + (2 if iv in interaction_ivs else 0)
    row = df[df["col"] == csv_col]
    if row.empty or beta_col not in df.columns:
        return None
    row = row.iloc[0]
    beta = row[beta_col]
    if p_one_col and p_one_col in df.columns and not pd.isna(row[p_one_col]):
        p_one = row[p_one_col]
    elif p_two_col and p_two_col in df.columns and not pd.isna(row[p_two_col]):
        p_one = row[p_two_col]  # two-tailed suite — use p_two directly for stars
    else:
        return None
    return _format_coef(beta, p_one, "two")


# H11: 1 IV (PRisk) × 4 DV cols. No `col` field -- indexed by dv.
H11_COL_TO_DV = {1: "UncAnsMgr", 2: "UncAnsCEO", 3: "UncPreMgr", 4: "UncPreCEO"}


def _extract_h11(df: pd.DataFrame, iv: str, col: int) -> Optional[str]:
    target_dv = H11_COL_TO_DV.get(col)
    if not target_dv:
        return None
    row = df[df["dv"] == target_dv]
    if row.empty:
        return None
    row = row.iloc[0]
    beta = row.get("beta_prisk")
    p_one = row.get("beta_prisk_p_one")
    if pd.isna(beta) or pd.isna(p_one):
        return None
    return _format_coef(beta, p_one, ">")


# H11-Lag: 2 IVs (PRisk_lag, PRisk_lag2) × 8 cols (col1-4 lag, col5-8 lag2).
# Schema has `iv` column identifying which lag, and `dv` identifying the
# uncertainty measure. Rows within (iv, dv) pairs show that IV's estimate.
# Cols 1-4 display PRisk_lag estimates; cols 5-8 display PRisk_lag2 estimates.
# A `--` cell appears where the IV does not match the column's regression.
H11_LAG_COL_TO_DV = {
    1: "UncAnsMgr", 2: "UncAnsCEO", 3: "UncPreMgr", 4: "UncPreCEO",
    5: "UncAnsMgr", 6: "UncAnsCEO", 7: "UncPreMgr", 8: "UncPreCEO",
}


def _extract_h11_lag(df: pd.DataFrame, iv: str, col: int) -> Optional[str]:
    col_range_iv = "PRisk_lag" if col <= 4 else "PRisk_lag2"
    if iv != col_range_iv:
        return "--"
    target_dv = H11_LAG_COL_TO_DV[col]
    mask = (df["iv"] == col_range_iv) & (df["dv"] == target_dv)
    row = df[mask]
    if row.empty:
        return None
    row = row.iloc[0]
    beta = row.get("beta_prisk")
    p_one = row.get("beta_prisk_p_one")
    if pd.isna(beta) or pd.isna(p_one):
        return None
    return _format_coef(beta, p_one, ">")


# H23 competition: 1 IV (z(log(TSIMM))) × 8 cols. CSV schema stores beta in
# `beta_iv`/`p_two_iv`, indexed by `col`. All two-tailed.
def _extract_h23(df: pd.DataFrame, iv: str, col: int) -> Optional[str]:
    row = df[df["col"] == col]
    if row.empty:
        return None
    row = row.iloc[0]
    beta = row.get("beta_iv")
    p_two = row.get("p_two_iv")
    if pd.isna(beta) or pd.isna(p_two):
        return None
    return _format_coef(beta, p_two, "two")


# H24/H24b/H25 macro: 1 IV × 8 cols. Schema has `beta`, `beta_p_one`,
# indexed by `dv` and `sample`. Col ordering matches findings.txt specs.
H24_COL_TO_SPEC = {
    # col -> (sample, dv) — findings.txt shows only the Main sample.
    1: ("Main", "UncAnsMgr"),
    2: ("Main", "UncPreMgr"),
    3: ("Main", "UncAnsCEO"),
    4: ("Main", "UncPreCEO"),
    5: ("Main", "UncAnsMgr_lead1"),
    6: ("Main", "UncPreMgr_lead1"),
    7: ("Main", "UncAnsCEO_lead1"),
    8: ("Main", "UncPreCEO_lead1"),
}


def _extract_h24_family(df: pd.DataFrame, iv: str, col: int) -> Optional[str]:
    spec = H24_COL_TO_SPEC.get(col)
    if spec is None:
        return None
    sample, dv = spec
    mask = (df["sample"] == sample) & (df["dv"] == dv)
    row = df[mask]
    if row.empty:
        return None
    row = row.iloc[0]
    beta = row.get("beta")
    p_one = row.get("beta_p_one")
    if pd.isna(beta) or pd.isna(p_one):
        return None
    return _format_coef(beta, p_one, ">")


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

IRREGULAR_EXTRACTORS = {
    "H1.1":    _extract_moderation,
    "H1.1b":   _extract_moderation,
    "H13.1":   _extract_moderation,
    "H1.2":    "h1_2",
    "H11":     "h11",
    "H11-Lag": "h11_lag",
    "H18b":    "h18b",
    "H23":     "h23",
    "H24":     "h24",
    "H24b":    "h24",
    "H25":     "h24",
}

# Hypothesis direction per suite (for two-tailed stars vs one-tailed).
# Derived from findings.txt Tail: lines. Used for standard-suite formatting.
HYP_DIR: Dict[str, str] = {
    "H1": ">", "H1.1": ">", "H1.1b": ">", "H1.2": "two",
    "H4a": "two", "H4b": "two", "H5": ">",
    "H7": ">", "H7b": ">", "H7c": ">", "H7d": ">", "H7e": ">",
    "H11": ">", "H11-Lag": ">",
    "H12": "<", "H12b": "<",
    "H13": "two", "H13.1": "two", "H13.2": "two",
    "H14": ">", "H14b": ">", "H14c": ">", "H14d": ">", "H14e": ">",
    "H16": "two", "H17": "two",
    "H18": ">", "H18b": ">",
    "H19": "<", "H19b": "<",
    "H20": "two", "H20b": "two",
    "H21": ">", "H22": ">", "H23": "two",
    "H24": ">", "H24b": ">", "H25": ">",
}


def _extract_cell(
    suite_id: str,
    iv: str,
    col: int,
    df: pd.DataFrame,
) -> Optional[str]:
    handler = IRREGULAR_EXTRACTORS.get(suite_id)
    hyp_dir = HYP_DIR.get(suite_id, ">")
    if handler is None:
        if iv in STANDARD_IVS:
            return _extract_standard(df, iv, col, hyp_dir)
        return None
    # Dispatch to irregular handler
    if callable(handler):
        return handler(df, iv, col, hyp_dir)
    dispatch = {
        "h1_2":     lambda: _extract_h1_2(df, iv, col),
        "h11":      lambda: _extract_h11(df, iv, col),
        "h11_lag":  lambda: _extract_h11_lag(df, iv, col),
        "h18b":     lambda: _extract_h18b(df, iv, col),
        "h23":      lambda: _extract_h23(df, iv, col),
        "h24":      lambda: _extract_h24_family(df, iv, col),
    }
    fn = dispatch.get(handler)
    return fn() if fn else None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _pad_value(value: str, target_width: int = 16) -> str:
    """Right-pad the value to occupy the same visual width the template
    placeholder did, so bracket columns stay aligned.

    The template was built with placeholders of variable width; the original
    findings.txt used 16 characters of space between the value and the bracket.
    We emit exactly that: left-justify the value in a 16-char field.
    """
    return value.ljust(target_width)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate outputs/findings.txt from model_diagnostics.csv files."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing findings.txt.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every placeholder substitution.",
    )
    args = parser.parse_args()

    if not TEMPLATE.exists():
        print(f"[error] Template not found: {TEMPLATE}", file=sys.stderr)
        print(f"        Run scripts/_build_findings_template.py first.", file=sys.stderr)
        return 1
    if not PLACEHOLDERS_MAP.exists():
        print(f"[error] Placeholders map not found: {PLACEHOLDERS_MAP}", file=sys.stderr)
        return 1

    template_text = TEMPLATE.read_text(encoding="utf-8")
    placeholders: Dict[str, Dict[str, Any]] = json.loads(
        PLACEHOLDERS_MAP.read_text(encoding="utf-8")
    )

    # Load suite dir map and resolver from generate_all_tables
    gat_module = _load_generate_all_tables_module()
    gat_suites = {s["id"]: s for s in gat_module.SUITES}

    # Per-suite DataFrame cache
    diag_cache: Dict[str, Optional[pd.DataFrame]] = {}

    def _get_df(suite_id: str) -> Optional[pd.DataFrame]:
        if suite_id in diag_cache:
            return diag_cache[suite_id]
        suite_dir = _resolve_suite_dir(gat_module, gat_suites, suite_id)
        if suite_dir is None:
            diag_cache[suite_id] = None
            return None
        df = _load_diagnostics(suite_dir)
        diag_cache[suite_id] = df
        return df

    # Substitute each placeholder
    n_regen = 0
    n_fallback = 0
    n_missing_suite = 0
    per_suite_regen: Dict[str, int] = {}
    per_suite_fallback: Dict[str, int] = {}

    for key, meta in placeholders.items():
        suite_id = meta["suite"]
        iv = meta["iv"]
        col = meta["col"]
        orig_value = meta["orig_value"]

        df = _get_df(suite_id)
        new_value: Optional[str] = None
        if df is not None:
            try:
                new_value = _extract_cell(suite_id, iv, col, df)
            except Exception as exc:
                if args.verbose:
                    print(f"[warn] {suite_id}/{iv}/col{col}: extractor raised {exc}")
                new_value = None
        elif gat_suites.get(suite_id) is None:
            n_missing_suite += 1

        if new_value is None:
            new_value = orig_value
            n_fallback += 1
            per_suite_fallback[suite_id] = per_suite_fallback.get(suite_id, 0) + 1
            if args.verbose:
                print(f"[fallback] {suite_id}/{iv}/col{col}: using orig={orig_value!r}")
        else:
            n_regen += 1
            per_suite_regen[suite_id] = per_suite_regen.get(suite_id, 0) + 1
            if args.verbose and new_value != orig_value:
                print(f"[regen] {suite_id}/{iv}/col{col}: {orig_value!r} -> {new_value!r}")

        template_text = template_text.replace(key, _pad_value(new_value))

    # Summary
    print(f"Placeholders processed: {len(placeholders):,}")
    print(f"  Regenerated from diagnostics: {n_regen:,}")
    print(f"  Fallback to original value:   {n_fallback:,}")
    if n_missing_suite > 0:
        print(f"  (of which {n_missing_suite} had no entry in generate_all_tables.SUITES)")
    print()
    print("Per-suite breakdown:")
    all_suites = sorted(set(per_suite_regen) | set(per_suite_fallback))
    for s in all_suites:
        r = per_suite_regen.get(s, 0)
        f = per_suite_fallback.get(s, 0)
        tag = "OK" if f == 0 else ("PARTIAL" if r > 0 else "FALLBACK")
        print(f"  {s:10s}  regen={r:4d}  fallback={f:4d}  [{tag}]")

    if args.dry_run:
        print("\n[dry-run] Not writing output.")
        return 0

    OUT_FINDINGS.write_text(template_text, encoding="utf-8")
    print(f"\nWrote {OUT_FINDINGS} ({len(template_text.split(chr(10))):,} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
