#!/usr/bin/env python3
"""Regenerate outputs/findings.txt from suite_spec_*.json files + curated template.

Architecture (post-Phase-6 rewrite):
    - scripts/findings_template.txt holds the curated prose (DV formulas,
      references, tail notes, one-SD effect sizes) with cell positions marked
      by placeholders `__<suite>__<iv>__col<N>__`. Prose is hand-maintained;
      only cell values are regenerated.
    - outputs/econometric/<dir>/<timestamp>/suite_spec_<id>.json is the single
      source of truth for every numeric cell. These files are written by the
      runners via `write_suite_spec()` and validated against the pydantic
      SuiteSpec schema.
    - This script scans the template for placeholders, loads the latest spec
      file per suite, and substitutes each placeholder with a formatted cell.
    - Fails loudly on missing cells for suites in `config/suite_render_order.yaml`.
      Suites outside the render order (H19, H20 legacy) emit "--" with a warning.

Col remaps:
    - H11-Lag: template cols 1-4 (PRisk_lag Firm FE) → H11-Lag1 spec cols 5-8.
      Template cols 5-8 (PRisk_lag2 Firm FE) → H11-Lag2 spec cols 5-8.
      Cross-IV cells ("__H11-Lag__PRisk_lag__col5__" etc.) emit "--".
    - H24 / H24b / H25: template cols 1-4 (Firm FE contemporaneous) → spec
      cols 5-8 (Firm FE). Template cols 5-8 (Firm FE Next Quarter t+1) emit
      "--" because current runners don't produce lead1 specs.

Run:
    python scripts/generate_findings.py            # regenerate findings.txt
    python scripts/generate_findings.py --dry-run  # print summary, don't write
    python scripts/generate_findings.py --verbose  # log every substitution
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "scripts" / "findings_template.txt"
RENDER_ORDER = ROOT / "config" / "suite_render_order.yaml"
ECONOMETRIC = ROOT / "outputs" / "econometric"
OUT_FINDINGS = ROOT / "outputs" / "findings.txt"

# Regex: `__<suite>__<iv>__col<N>__` where IV is non-greedy to handle names
# with parentheses and spaces (e.g. `log(US EPU)_t`).
PLACEHOLDER_RE = re.compile(r"__([A-Za-z][A-Za-z0-9.\-]*)__(.+?)__col(\d+)__")

# Standard pad width for cell values (matches legacy findings.txt alignment).
PAD_WIDTH = 16

# Suites that are not in the render order — emit "--" with a warning.
LEGACY_SUITES = {"H19", "H20"}

# Known template-vs-runner structural mismatches (warn, don't error).
# Template expects these (placeholder suite_id, col) pairs but the current
# runner doesn't produce them. Placing here downgrades them from error to
# warning so findings.txt still regenerates cleanly.
KNOWN_MISMATCHES: set[tuple[str, int]] = {
    # H24/H24b/H25: template cols 5-8 are "Next Quarter (t+1)" lead1 specs.
    # Current macro runners (h24_us_epu, h24b_global_epu, h25_gpr) produce
    # 8 contemporaneous cols (4 Industry FE + 4 Firm FE). Dropping the lead1
    # specs was part of the Phase 4 batch 7 macro suite simplification.
    ("H24", 5), ("H24", 6), ("H24", 7), ("H24", 8),
    ("H24b", 5), ("H24b", 6), ("H24b", 7), ("H24b", 8),
    ("H25", 5), ("H25", 6), ("H25", 7), ("H25", 8),
}

# Per-suite template-col → spec-col remaps for suites whose template layout
# is a subset of the current spec's col count (i.e., template was built when
# the runner had fewer cols; the runner was later expanded).
#
# Each entry: suite_id -> {template_col: spec_col}
# If template_col not in the remap, 1-to-1 mapping is used.
COL_REMAPS: dict[str, dict[int, int]] = {
    # H1.1 / H1.1b / H1.2: template shows Industry FE only (col1=Ind+Yr,
    # col2=Ind+YrQtr). Spec has 4 cols including Firm FE variants: spec
    # [1=Ind+Yr, 2=Firm+Yr, 3=Ind+YrQtr, 4=Firm+YrQtr]. Remap picks the
    # Industry-FE cols only.
    "H1.1":  {1: 1, 2: 3},
    "H1.1b": {1: 1, 2: 3},
    "H1.2":  {1: 1, 2: 3},
    # H11: template shows Firm FE only (4 cols with Mgr-QA/CEO-QA/Mgr-Pres/
    # CEO-Pres DVs). Spec has 8 cols [1-4=Ind, 5-8=Firm], so remap picks the
    # Firm-FE half.
    "H11": {1: 5, 2: 6, 3: 7, 4: 8},
    # H13.1: template shows Industry FE only (col1=Capex+Yr, col2=Capex+YrQtr,
    # col3=Capex_lead+Yr, col4=Capex_lead+YrQtr). Spec has 8 cols:
    # [1=Capex+Ind+Yr, 2=Capex+Firm+Yr, 3=Capex+Ind+YrQtr, 4=Capex+Firm+YrQtr,
    #  5=Capex_lead+Ind+Yr, 6=Capex_lead+Firm+Yr,
    #  7=Capex_lead+Ind+YrQtr, 8=Capex_lead+Firm+YrQtr].
    "H13.1": {1: 1, 2: 3, 3: 5, 4: 7},
}


# ---------------------------------------------------------------------------
# Spec file loading
# ---------------------------------------------------------------------------


def find_latest_spec_path(suite_id: str) -> Optional[Path]:
    """Locate the newest suite_spec_<id>.json across all timestamped dirs."""
    pattern = f"**/suite_spec_{suite_id}.json"
    matches = sorted(ECONOMETRIC.glob(pattern), reverse=True)
    return matches[0] if matches else None


def load_spec(suite_id: str) -> Optional[dict[str, Any]]:
    path = find_latest_spec_path(suite_id)
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Coef extraction + formatting
# ---------------------------------------------------------------------------


def lookup_coef(
    spec: dict[str, Any], iv_name: str, col: int
) -> Optional[dict[str, Any]]:
    """Return the {beta, se, p_two, p_one} dict for (iv, col), or None if absent.

    Direct match preferred. For single-IV suites where the template uses a
    pretty-name placeholder (e.g. `log(US EPU)_t` vs spec IV `US_EPU_log`),
    fall back to the spec's sole declared IV.
    """
    if col < 1 or col > len(spec["columns"]):
        return None
    col_data = spec["columns"][col - 1]
    coefs = col_data["coefs"]
    if iv_name in coefs:
        return coefs[iv_name]
    if len(spec["ivs"]) == 1:
        fallback = spec["ivs"][0]["name"]
        return coefs.get(fallback)
    return None


def get_iv_tail(spec: dict[str, Any], iv_name: str) -> str:
    """Return `one_pos` / `one_neg` / `two` for the declared IV.

    Same fallback logic as lookup_coef: single-IV suites map any placeholder
    IV to spec.ivs[0].tail.
    """
    for iv in spec["ivs"]:
        if iv["name"] == iv_name:
            return iv["tail"]
    if len(spec["ivs"]) == 1:
        return spec["ivs"][0]["tail"]
    return "two"


def format_coef(coef: dict[str, Any], tail: str) -> str:
    """Format as `+0.0053***` / `-0.0147**` / `n.s.` / `--`.

    Stars gated on one-tailed p when tail is directional; two-tailed p
    otherwise. Negative beta under a one-tailed positive declaration (or
    vice versa) yields `n.s.` because p_one > 0.5 in the spec's direction-
    aware computation.
    """
    beta = coef.get("beta")
    if beta is None:
        return "--"
    if tail in ("one_pos", "one_neg"):
        p = coef.get("p_one")
    else:
        p = coef.get("p_two")
    if p is None:
        return "--"
    if p < 0.01:
        stars = "***"
    elif p < 0.05:
        stars = "**"
    elif p < 0.10:
        stars = "*"
    else:
        return "n.s."
    sign = "+" if beta >= 0 else "-"
    return f"{sign}{abs(beta):.4f}{stars}"


def pad(value: str) -> str:
    return value.ljust(PAD_WIDTH)


# ---------------------------------------------------------------------------
# Per-suite col remaps
# ---------------------------------------------------------------------------


def resolve_h11_lag(
    iv_name: str, col: int
) -> tuple[Optional[str], Optional[int], Optional[str]]:
    """Map template (iv, col) to (spec_suite_id, spec_col, reason).

    Returns (None, None, reason) for cross-IV cells that should render "--".
    """
    # H11-Lag template: 2 IVs × 8 cols where cross-IV cells are "--".
    # - PRisk_lag: cols 1-4 valid (Firm FE Lag1), cols 5-8 cross-IV "--"
    # - PRisk_lag2: cols 1-4 cross-IV "--", cols 5-8 valid (Firm FE Lag2)
    # Spec: H11-Lag1 has cols 1-4 Industry FE, cols 5-8 Firm FE (same for Lag2).
    if iv_name == "PRisk_lag":
        if 1 <= col <= 4:
            # template col 1-4 → H11-Lag1 spec col 5-8 (Firm FE)
            return "H11-Lag1", col + 4, None
        return None, None, "cross-IV cell (PRisk_lag in Lag2 col range)"
    if iv_name == "PRisk_lag2":
        if 5 <= col <= 8:
            # template col 5-8 → H11-Lag2 spec col 5-8 (Firm FE, col offset = -4 + 4 = 0)
            return "H11-Lag2", col, None
        return None, None, "cross-IV cell (PRisk_lag2 in Lag1 col range)"
    return None, None, f"unknown H11-Lag iv {iv_name!r}"


def resolve_macro(
    suite_id: str, col: int
) -> tuple[Optional[str], Optional[int], Optional[str]]:
    """H24 / H24b / H25: template cols 1-4 → spec cols 5-8, cols 5-8 → '--'."""
    if 1 <= col <= 4:
        return suite_id, col + 4, None
    if 5 <= col <= 8:
        return None, None, "lead1 (next quarter) cols not produced by current runner"
    return None, None, f"unexpected col {col} for macro suite"


# ---------------------------------------------------------------------------
# Main substitution
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate outputs/findings.txt from suite_spec JSON."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report counts without writing the output file.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every substitution + error + warning.",
    )
    args = parser.parse_args()

    if not TEMPLATE.exists():
        print(f"[error] template missing: {TEMPLATE}", file=sys.stderr)
        return 1
    if not RENDER_ORDER.exists():
        print(f"[error] render order config missing: {RENDER_ORDER}", file=sys.stderr)
        return 1

    template_text = TEMPLATE.read_text(encoding="utf-8")
    render_cfg = yaml.safe_load(RENDER_ORDER.read_text(encoding="utf-8"))
    valid_suites = set(render_cfg["suites"])

    spec_cache: dict[str, Optional[dict[str, Any]]] = {}

    def get_spec(sid: str) -> Optional[dict[str, Any]]:
        if sid not in spec_cache:
            spec_cache[sid] = load_spec(sid)
        return spec_cache[sid]

    # Accumulators
    errors: list[str] = []
    warnings: list[str] = []
    n_subst = 0
    n_missing = 0
    per_suite_counts: dict[str, int] = {}
    per_suite_missing: dict[str, int] = {}
    per_suite_has_real_error: dict[str, bool] = {}

    def record_success(placeholder: str, suite_id: str) -> None:
        nonlocal n_subst
        n_subst += 1
        per_suite_counts[suite_id] = per_suite_counts.get(suite_id, 0) + 1
        if args.verbose:
            print(f"[ok] {placeholder}")

    def record_missing(
        placeholder: str, suite_id: str, col: int, reason: str
    ) -> None:
        nonlocal n_missing
        n_missing += 1
        per_suite_missing[suite_id] = per_suite_missing.get(suite_id, 0) + 1
        msg = f"{placeholder}: {reason}"
        is_known = suite_id in LEGACY_SUITES or (suite_id, col) in KNOWN_MISMATCHES
        if is_known:
            warnings.append(msg)
        else:
            errors.append(msg)
            per_suite_has_real_error[suite_id] = True
        if args.verbose:
            tag = "[warn]" if is_known else "[error]"
            print(f"{tag} {msg}")

    def substitute(match: re.Match[str]) -> str:
        placeholder = match.group(0)
        suite_id = match.group(1)
        iv_name = match.group(2)
        col = int(match.group(3))

        if suite_id in LEGACY_SUITES:
            record_missing(placeholder, suite_id, col, "legacy suite not in render order")
            return pad("--")

        # Per-suite remap resolution
        if suite_id == "H11-Lag":
            target_suite, target_col, reason = resolve_h11_lag(iv_name, col)
            if target_suite is None:
                # Cross-IV cell — expected "--", NOT an error.
                n_cross = "--"
                nonlocal n_subst
                n_subst += 1
                per_suite_counts[suite_id] = per_suite_counts.get(suite_id, 0) + 1
                if args.verbose:
                    print(f"[cross] {placeholder}: {reason}")
                return pad(n_cross)
        elif suite_id in ("H24", "H24b", "H25"):
            target_suite, target_col, reason = resolve_macro(suite_id, col)
            if target_suite is None:
                record_missing(placeholder, suite_id, col, reason or "macro remap failed")
                return pad("--")
        elif suite_id in COL_REMAPS:
            target_suite = suite_id
            target_col = COL_REMAPS[suite_id].get(col, col)
        else:
            target_suite, target_col = suite_id, col

        if target_suite not in valid_suites:
            record_missing(
                placeholder,
                suite_id,
                col,
                f"target suite {target_suite!r} not in render order",
            )
            return pad("--")

        spec = get_spec(target_suite)
        if spec is None:
            record_missing(placeholder, suite_id, col, f"no spec file for {target_suite}")
            return pad("--")

        coef = lookup_coef(spec, iv_name, target_col)
        if coef is None:
            record_missing(
                placeholder,
                suite_id,
                col,
                f"iv {iv_name!r} not found in {target_suite} col {target_col}",
            )
            return pad("--")

        tail = get_iv_tail(spec, iv_name)
        cell = format_coef(coef, tail)
        record_success(placeholder, suite_id)
        return pad(cell)

    new_text = PLACEHOLDER_RE.sub(substitute, template_text)

    # Report
    print(f"Placeholders processed: {n_subst + n_missing:,}")
    print(f"  Substituted from spec: {n_subst:,}")
    print(f"  Missing / legacy:      {n_missing:,}")
    print()
    print("Per-suite counts (ok / missing):")
    all_suites = sorted(set(per_suite_counts) | set(per_suite_missing))
    for s in all_suites:
        ok = per_suite_counts.get(s, 0)
        miss = per_suite_missing.get(s, 0)
        if miss == 0:
            tag = "[OK]"
        elif per_suite_has_real_error.get(s, False):
            tag = "[ERROR]"
        else:
            tag = "[WARN]"
        print(f"  {s:10s}  ok={ok:4d}  missing={miss:4d}  {tag}")

    if warnings:
        print()
        print(f"Warnings ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"  {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")

    if errors:
        print()
        print(f"ERRORS ({len(errors)}):")
        for e in errors[:20]:
            print(f"  {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
        print()
        print("Fail-loud mode: refusing to write findings.txt while errors exist.")
        print("Fix the upstream issue (runner, spec file, template placeholder) and rerun.")
        return 1

    if args.dry_run:
        print("\n[dry-run] Not writing output.")
        return 0

    OUT_FINDINGS.write_text(new_text, encoding="utf-8")
    n_lines = new_text.count("\n")
    print(f"\nWrote {OUT_FINDINGS} ({n_lines:,} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
