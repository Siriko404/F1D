"""Filter docs/Draft/variable_definitions.tex to vars actually used in v7
thesis-body suite_specs.

Source-of-truth = the 12 thesis suite_spec_*.json files (DV, IVs, controls,
interactions extracted from spec). Drops rows for vars not in any spec.
Preserves longtable scaffolding (headers, footers, end-of-table markers).

Usage:
    python scripts/adhoc/filter_vardefs_thesis.py [--dry-run]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ECONOMETRIC_DIR = ROOT / "outputs" / "econometric"
VARDEFS_TEX = ROOT / "docs" / "Draft" / "variable_definitions.tex"

# 12 v7 thesis-body suites — directory names under outputs/econometric/.
# Matches config/suite_render_order.yaml `thesis_suites:` list.
THESIS_DIRS = [
    "h1_cash_holdings_ceo2iv_decomp",
    "h1_cash_holdings_ceo2iv_decomp_qtrexp",
    "h1_2_cash_constraint_ceo2iv_decomp",
    "h1_2_cash_constraint_ceo2iv_decomp_qtrexp",
    "h1_3_cfvol_moderation",
    "h11_prisk_uncertainty",
    "h11_prisk_uncertainty_lag",
    "h23_competition_uncertainty",
    "h24_us_epu",
    "h24b_global_epu",
    "h14c_spread_bgt_level_ceo2iv_decomp",
    "h18_cccl_received_ceo2iv_decomp",
]

# Vars that aren't IVs/DVs/controls in any spec but are referenced by name
# inside another vardefs entry's formula — dropping them creates dangling refs.
ALWAYS_KEEP = {
    "UncAnsCEO",  # referenced in ClarityCEO + UncResCEO formulas (DWZ Eq.4/5 input)
    "SurpDec",    # referenced in AbsSurpDec formula (= abs(SurpDec))
}


def latest_spec(dir_name: str) -> Path | None:
    cands = sorted((ECONOMETRIC_DIR / dir_name).rglob("suite_spec_*.json"))
    return cands[-1] if cands else None


def normalize(name: str) -> str:
    """LaTeX-escape variant -> raw name. e.g. 'BGTAvg\\_Amihud' -> 'BGTAvg_Amihud'."""
    return name.replace("\\_", "_").replace("\\", "")


def vars_from_spec(spec_path: Path) -> set[str]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for iv in spec.get("ivs", []):
        out.add(iv["name"])
    ctrls = spec.get("controls", {})
    if isinstance(ctrls, dict):
        out.update(ctrls.get("base", []))
        out.update(ctrls.get("extended_only", []))
    for col in spec.get("columns", []):
        if col.get("dv"):
            out.add(col["dv"])
        out.update(col.get("control_vars", []))
        out.update(col.get("coefs", {}).keys())
    # Skip header_rows — labels are display strings (FE indicator labels, math-mode
    # DV captions like "Spread$_{25D,t}$"), not vars. DV names come from columns[].dv.
    return out


def collect_used_vars() -> set[str]:
    used: set[str] = set()
    for d in THESIS_DIRS:
        spec = latest_spec(d)
        if spec is None:
            print(f"WARN: no spec for {d}")
            continue
        vs = vars_from_spec(spec)
        used |= vs
        print(f"  {d}: +{len(vs)} vars")
    return used


# A row is a single line that begins with a var-name token followed by ` &`.
# Examples that MUST match:  "BGTAvg\_Amihud & ...", "ClarityCEO & ..."
# Examples that MUST NOT match: header `\textbf{Name} & ...`, manifest comma-list.
ROW_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_\\]*)\s*&")


def filter_tex(used: set[str], dry_run: bool) -> tuple[list[str], list[str]]:
    """Return (kept_var_names, dropped_var_names)."""
    text = VARDEFS_TEX.read_text(encoding="utf-8")
    lines = text.split("\n")
    out: list[str] = []
    kept: list[str] = []
    dropped: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = ROW_RE.match(line)
        if m:
            raw = normalize(m.group(1))
            # Edge: comma-list rows (manifest) — first token is "file_name", which
            # then has ", ceo_id, ..." after it. Detect via comma in original line.
            head = line.split("&", 1)[0]
            if "," in head:
                # comma-list row (manifest) — keep unconditionally
                out.append(line)
                i += 1
                # also keep \addlinespace if present
                if i < len(lines) and "addlinespace" in lines[i]:
                    out.append(lines[i])
                    i += 1
                continue
            if raw in used:
                kept.append(raw)
                out.append(line)
                i += 1
                if i < len(lines) and "addlinespace" in lines[i]:
                    out.append(lines[i])
                    i += 1
                continue
            else:
                dropped.append(raw)
                # skip row + following \addlinespace
                i += 1
                if i < len(lines) and "addlinespace" in lines[i]:
                    i += 1
                continue
        out.append(line)
        i += 1
    if not dry_run:
        VARDEFS_TEX.write_text("\n".join(out), encoding="utf-8")
    return kept, dropped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report changes without writing the .tex")
    args = ap.parse_args()

    print(f"Reading {len(THESIS_DIRS)} thesis suite specs:")
    used = collect_used_vars()
    used |= ALWAYS_KEEP
    print(f"\nUnion: {len(used)} unique var names "
          f"(incl. {len(ALWAYS_KEEP)} ALWAYS_KEEP formula-references).")

    kept, dropped = filter_tex(used, args.dry_run)
    action = "WOULD KEEP" if args.dry_run else "KEPT"
    print(f"\n{action} {len(set(kept))} vars in vardefs:")
    for v in sorted(set(kept)):
        print(f"  + {v}")
    action = "WOULD DROP" if args.dry_run else "DROPPED"
    print(f"\n{action} {len(set(dropped))} orphan vars from vardefs:")
    for v in sorted(set(dropped)):
        print(f"  - {v}")

    # Sanity: any used var not in vardefs is a coverage gap.
    in_vardefs = set(kept)  # only those we found in vardefs
    not_in_vardefs = used - in_vardefs - set(dropped)
    if not_in_vardefs:
        print(f"\nINFO: {len(not_in_vardefs)} used vars have no vardefs entry "
              f"(may be column-derived or not yet documented):")
        for v in sorted(not_in_vardefs):
            print(f"  ? {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
