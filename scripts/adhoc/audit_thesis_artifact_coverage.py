"""Audit thesis artifact coverage — proves invariant by construction.

Reads `thesis_suites:` from `config/suite_render_order.yaml` (single source
of truth), walks the latest `suite_spec_*.json` for each, unions used_vars,
then diffs that union against:

  1. The rendered docs/Draft/variable_definitions.tex (every used var must
     have an appendix entry).
  2. The rendered docs/Draft/summary_stats.csv (every used var that is not
     in summary_stats_config.exclude_vars must have a row).

Exits non-zero on any mismatch.

This is the answer to "how do we know the variable-definitions and summary-
stats artifacts depend ONLY on the thesis-included suites and display them
COMPLETELY".  Every other determinism guarantee in the v7 toolchain reduces
to this script returning 0.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SUITE_RENDER_ORDER = ROOT / "config" / "suite_render_order.yaml"
SUMMARY_CONFIG = ROOT / "config" / "summary_stats_config.yaml"
ECONOMETRIC = ROOT / "outputs" / "econometric"
VARDEFS_TEX = ROOT / "docs" / "Draft" / "variable_definitions.tex"
SUMMARY_CSV = ROOT / "docs" / "Draft" / "summary_stats.csv"

# Vars referenced inside another vardef's formula — kept in vardefs even if
# not directly used in any spec. Same set as generate_var_defs_appendix.py.
ALWAYS_KEEP = {"UncAnsCEO", "SurpDec"}


def load_thesis_suites() -> list[str]:
    cfg = yaml.safe_load(SUITE_RENDER_ORDER.read_text(encoding="utf-8"))
    suites = cfg.get("thesis_suites") or []
    if not suites:
        raise RuntimeError(f"No thesis_suites: in {SUITE_RENDER_ORDER}")
    return list(suites)


def find_suite_spec(suite_id: str) -> Path | None:
    matches = sorted(ECONOMETRIC.glob(f"*/*/suite_spec_{suite_id}.json"))
    return matches[-1] if matches else None


def vars_from_spec(spec_path: Path) -> set:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out: set = set()
    for iv in spec.get("ivs", []):
        out.add(iv["name"] if isinstance(iv, dict) else iv)
    ctrls = spec.get("controls", {})
    if isinstance(ctrls, dict):
        out.update(ctrls.get("base", []))
        out.update(ctrls.get("extended_only", []))
    for col in spec.get("columns", []):
        if col.get("dv"):
            out.add(col["dv"])
        out.update(col.get("control_vars", []))
        out.update(col.get("coefs", {}).keys())
    return out


def collect_used_vars(thesis_suites: list[str]) -> set:
    used: set = set()
    missing_specs = []
    for suite_id in thesis_suites:
        sp = find_suite_spec(suite_id)
        if sp is None:
            missing_specs.append(suite_id)
            continue
        used |= vars_from_spec(sp)
    if missing_specs:
        raise RuntimeError(
            f"Missing suite_spec_*.json for thesis suites: {missing_specs}\n"
            f"Either run the suite or remove from thesis_suites: in {SUITE_RENDER_ORDER}."
        )
    used |= ALWAYS_KEEP
    return used


def vars_in_vardefs() -> set:
    """Extract var names from rendered variable_definitions.tex.

    Each entry row in a longtable starts with `<ColName> & ` (after LaTeX
    escaping of underscores).  Skips header / page-control rows.
    """
    if not VARDEFS_TEX.exists():
        raise FileNotFoundError(f"Missing {VARDEFS_TEX}; run generate_var_defs_appendix.py first.")
    text = VARDEFS_TEX.read_text(encoding="utf-8")
    cols = set()
    # Match the leading var name in a longtable row. Names may be wrapped in
    # \seqsplit{...} or have escaped underscores.
    for m in re.finditer(r"^([A-Za-z][A-Za-z0-9_\\]+)\s*&", text, re.MULTILINE):
        raw = m.group(1).replace(r"\_", "_").replace("\\", "")
        cols.add(raw)
    # Strip header tokens
    cols -= {"Name", "textbf", "multicolumn"}
    # Manifest row has compound 'file_name, ceo_id, ...'; first token is file_name
    return cols


def vars_in_summary_stats() -> set:
    if not SUMMARY_CSV.exists():
        return set()
    cols = set()
    with SUMMARY_CSV.open(encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            for key in ("Variable", "variable", "Col", "Name", "name"):
                if key in row and row[key]:
                    cols.add(row[key])
                    break
    return cols


def main() -> int:
    print("=" * 72)
    print("THESIS ARTIFACT COVERAGE AUDIT")
    print("=" * 72)

    suites = load_thesis_suites()
    print(f"thesis_suites: {len(suites)} suites (source: {SUITE_RENDER_ORDER.name})")

    used = collect_used_vars(suites)
    print(f"used_vars (incl. ALWAYS_KEEP): {len(used)}")

    vd_cols = vars_in_vardefs()
    print(f"variable_definitions.tex entries: {len(vd_cols)}")

    ss_vars = vars_in_summary_stats()
    print(f"summary_stats.csv entries: {len(ss_vars)}")

    ss_cfg = yaml.safe_load(SUMMARY_CONFIG.read_text(encoding="utf-8")) if SUMMARY_CONFIG.exists() else {}
    exclude = set(ss_cfg.get("exclude_vars") or [])

    fails = []

    # 1. Vardefs MUST contain every used var.
    missing_vd = used - vd_cols
    if missing_vd:
        fails.append(("variable_definitions.tex", "MISSING used vars", sorted(missing_vd)))

    # 2. Vardefs MUST NOT contain orphan vars (not in any used spec, not ALWAYS_KEEP).
    # Filter out manifest-only entries (file_name etc) and header tokens.
    KNOWN_NON_VARS = {"file_name", "ceo_id", "Name"}
    extras_vd = vd_cols - used - KNOWN_NON_VARS
    if extras_vd:
        fails.append(("variable_definitions.tex", "ORPHAN entries (not in any thesis spec)", sorted(extras_vd)))

    # 3. Summary_stats MUST contain every used var that is not excluded.
    expected_ss = used - exclude - ALWAYS_KEEP
    missing_ss = expected_ss - ss_vars
    if missing_ss:
        fails.append(("summary_stats.csv", "MISSING used vars (not in exclude_vars)", sorted(missing_ss)))

    if not fails:
        print("\n[PASS] All thesis-suite vars are present in both artifacts; no orphans.")
        return 0

    print("\n[FAIL] coverage mismatches:")
    for source, kind, items in fails:
        print(f"\n  {source} -- {kind} ({len(items)}):")
        for v in items:
            print(f"    - {v}")
    print(
        "\nFix steps:\n"
        "  - MISSING used vars in variable_definitions.tex: add HAND_STUB or YAML entry.\n"
        "  - ORPHAN entries in variable_definitions.tex: bug in generator filter.\n"
        "  - MISSING used vars in summary_stats.csv: rerun generate_summary_stats.py "
        "or add to exclude_vars: if intentionally suppressed."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
