"""Scout for config/variables.yaml repair (Step 8.4).

Diff-only scan. NO yaml generation. Outputs scout_report.md so we can decide
whether the planned AST metadata walker is needed or if line-1 docstrings cover
90%+ of cases.

Inputs scanned:
  1. outputs/econometric/*/<latest_ts>/suite_spec_*.json (canonical var lists)
  2. src/f1d/shared/variables/*.py (78 modules, line-1 docstring only)
  3. config/variables.yaml (existing entries, indexed by `column` field)
  4. config/summary_stats_config.yaml (extra_vars to include in scope)

Outputs:
  tmp/yaml_repair/scout_report.md — gap report by category + docstring quality
"""

from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent
ECON_DIR = ROOT / "outputs" / "econometric"
VAR_MODULES = ROOT / "src" / "f1d" / "shared" / "variables"
YAML_PATH = ROOT / "config" / "variables.yaml"
SS_CONFIG = ROOT / "config" / "summary_stats_config.yaml"
OUT = ROOT / "tmp" / "yaml_repair" / "scout_report.md"


def latest_spec_dirs(econ_dir: Path) -> List[Path]:
    out = []
    for suite_dir in sorted(econ_dir.iterdir()):
        if not suite_dir.is_dir() or suite_dir.name.startswith("_"):
            continue
        ts_dirs = sorted(
            [d for d in suite_dir.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True,
        )
        for ts in ts_dirs:
            specs = list(ts.glob("suite_spec_*.json"))
            if specs:
                out.extend(specs)
                break
    return out


def scan_specs(spec_paths: List[Path]) -> Dict[str, Dict]:
    """Return {var_name: {role, suites:set, in_extended:bool}}."""
    canonical: Dict[str, Dict] = {}
    for sp in spec_paths:
        try:
            spec = json.loads(sp.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARN parse {sp.name}: {e}")
            continue
        sid = spec.get("suite_id", sp.stem.replace("suite_spec_", ""))

        def add(name: str, role: str, extended: bool = False):
            entry = canonical.setdefault(
                name, {"role": role, "suites": set(), "in_extended": False}
            )
            entry["suites"].add(sid)
            if role == "iv" and entry["role"] != "iv":
                entry["role"] = "iv"
            elif role == "dv" and entry["role"] not in ("iv",):
                entry["role"] = "dv"
            elif extended:
                entry["in_extended"] = True

        for iv in spec.get("ivs", []):
            add(iv["name"], "iv")
        for ctrl in spec.get("controls", {}).get("base", []):
            add(ctrl, "control")
        for ctrl in spec.get("controls", {}).get("extended_only", []):
            add(ctrl, "control", extended=True)
        for col in spec.get("columns", []):
            dv = col.get("dv")
            if dv:
                add(dv, "dv")
    return canonical


def scan_modules(var_dir: Path) -> Dict[str, Dict]:
    """Return {module_path: {docstring_line1, parsed_ok, source_field}}.

    Indexed by file stem (NOT column). We then look up column via metadata
    in a follow-up pass if needed.
    """
    out: Dict[str, Dict] = {}
    for py in sorted(var_dir.glob("*.py")):
        if py.name in ("__init__.py", "base.py"):
            continue
        out[py.stem] = parse_module(py)
    return out


def parse_module(py: Path) -> Dict:
    info = {
        "file": str(py.relative_to(ROOT)),
        "module_doc": None,
        "module_doc_line1": None,
        "class_doc": None,
        "metadata_source": None,
        "metadata_column": None,
        "metadata_reference": None,
        "parsed_ok": False,
    }
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
        info["parsed_ok"] = True
        info["module_doc"] = ast.get_docstring(tree)
        if info["module_doc"]:
            info["module_doc_line1"] = info["module_doc"].split("\n", 1)[0].strip()
        # Walk for ClassDef (first one) + metadata={...} dict literals
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and info["class_doc"] is None:
                info["class_doc"] = ast.get_docstring(node)
            if isinstance(node, ast.Call):
                # Look for VariableResult(... metadata={...})
                for kw in node.keywords:
                    if kw.arg == "metadata" and isinstance(kw.value, ast.Dict):
                        for k, v in zip(kw.value.keys, kw.value.values):
                            if not isinstance(k, ast.Constant):
                                continue
                            key = k.value
                            val = v.value if isinstance(v, ast.Constant) else None
                            if key == "source" and val and not info["metadata_source"]:
                                info["metadata_source"] = val
                            if key == "column" and val and not info["metadata_column"]:
                                info["metadata_column"] = val
                            if key == "reference" and val and not info["metadata_reference"]:
                                info["metadata_reference"] = val
    except Exception as e:
        info["parse_error"] = str(e)
    return info


def load_existing_yaml(path: Path) -> Dict[str, Dict]:
    """Index existing entries by `column` field (some have no column = manifest etc)."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    by_col: Dict[str, Dict] = {}
    for entry_name, entry in raw.get("variables", {}).items():
        if not isinstance(entry, dict):
            continue
        col = entry.get("column")
        if col:
            by_col[col] = {"_entry_name": entry_name, **entry}
        # multi-column entries (manifest, engines)
        for c in entry.get("columns", []) or []:
            by_col[c] = {"_entry_name": entry_name, **entry}
    return by_col


def derivative_kind(var: str) -> Optional[str]:
    if re.search(r"_lead\d*$|_lead_qtr$", var):
        return "lead"
    if re.search(r"_lag\d*$", var):
        return "lag"
    if var.endswith("_c"):
        return "mean_centered"
    if "_x_" in var:
        return "interaction"
    return None


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    spec_paths = latest_spec_dirs(ECON_DIR)
    canonical = scan_specs(spec_paths)
    modules = scan_modules(VAR_MODULES)
    existing = load_existing_yaml(YAML_PATH)
    extra = yaml.safe_load(SS_CONFIG.read_text(encoding="utf-8")).get("extra_vars", []) or []
    extra_names = {e["name"] for e in extra}

    # Build column → module_meta map (via metadata_column)
    col_to_module: Dict[str, Dict] = {}
    for stem, meta in modules.items():
        if meta.get("metadata_column"):
            col_to_module[meta["metadata_column"]] = meta
        # also index by stem-uppercase guess (for modules like cash_holdings → CashRatio)

    all_canonical_vars = set(canonical.keys()) | extra_names
    in_yaml = set(existing.keys())

    missing = sorted(all_canonical_vars - in_yaml)
    dead = sorted(in_yaml - all_canonical_vars)
    in_both = sorted(all_canonical_vars & in_yaml)

    # Categorize missing
    by_kind: Dict[str, List[str]] = defaultdict(list)
    for v in missing:
        kind = derivative_kind(v)
        if kind:
            by_kind[f"derivative_{kind}"].append(v)
            continue
        # Speech IVs heuristic
        if v in {"UncAnsMgr", "UncPreMgr", "UncAnsCEO", "UncPreCEO", "UncQue",
                 "NegCall", "SurpDec", "UncAnsCFO", "UncPreCFO", "UncCall",
                 "UncAnsNoCEO", "UncPreNoCEO"}:
            by_kind["speech_iv"].append(v)
            continue
        # Has matching module?
        if v in col_to_module:
            by_kind["module_present"].append(v)
            continue
        by_kind["other"].append(v)

    # Categorize incomplete (in YAML but missing fields)
    incomplete: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for col in in_both:
        e = existing[col]
        for f in ("formula", "reference", "role", "suites", "description"):
            if f not in e or not e[f]:
                incomplete[f].append((col, e.get("_entry_name", "?")))

    # Module docstring quality
    docstring_stats = {"with_line1": 0, "no_doc": 0, "parse_fail": 0, "total": len(modules)}
    docstring_samples = []
    for stem, m in modules.items():
        if not m["parsed_ok"]:
            docstring_stats["parse_fail"] += 1
        elif m["module_doc_line1"]:
            docstring_stats["with_line1"] += 1
            if len(docstring_samples) < 10:
                docstring_samples.append((stem, m["module_doc_line1"]))
        else:
            docstring_stats["no_doc"] += 1

    # Metadata dict coverage
    md_stats = {
        "with_source": sum(1 for m in modules.values() if m.get("metadata_source")),
        "with_column": sum(1 for m in modules.values() if m.get("metadata_column")),
        "with_reference": sum(1 for m in modules.values() if m.get("metadata_reference")),
    }

    # Emit report
    lines = []
    lines.append("# Variables YAML repair scout report")
    lines.append(f"\n**Generated:** scout_variables_yaml.py | "
                 f"specs={len(spec_paths)} modules={len(modules)} "
                 f"yaml_cols={len(existing)} extra_vars={len(extra)}")
    lines.append(f"\n## Top-line gap")
    lines.append(f"- **Canonical var set:** {len(all_canonical_vars)} (specs+extra_vars)")
    lines.append(f"- **In current YAML (by column):** {len(in_yaml)}")
    lines.append(f"- **MISSING (in spec/extra, not in YAML):** {len(missing)}")
    lines.append(f"- **DEAD (in YAML, not in any spec/extra):** {len(dead)}")
    lines.append(f"- **In both (need metadata fill check):** {len(in_both)}")

    lines.append("\n## Missing — by category")
    for kind, vars_ in sorted(by_kind.items()):
        lines.append(f"\n### {kind} ({len(vars_)})")
        for v in vars_:
            extras = ""
            if v in col_to_module:
                m = col_to_module[v]
                extras = f"  → module={m['file']}  doc=`{(m.get('module_doc_line1') or '')[:80]}`"
            lines.append(f"- `{v}`{extras}")

    lines.append("\n## DEAD entries (in YAML, no spec/extra reference)")
    lines.append("Manual review needed — may be archived suites or planned future work.")
    for v in dead:
        e = existing[v]
        lines.append(f"- `{v}` (entry_name=`{e['_entry_name']}`, ref=`{e.get('reference', '?')}`)")

    lines.append("\n## Incomplete metadata (in YAML, fields missing)")
    for field, items in sorted(incomplete.items()):
        lines.append(f"\n### Missing `{field}` ({len(items)})")
        for col, name in items[:30]:
            lines.append(f"- `{col}` (entry: `{name}`)")
        if len(items) > 30:
            lines.append(f"- ... and {len(items)-30} more")

    lines.append("\n## Module docstring quality (78 modules)")
    lines.append(f"- **with line-1 docstring:** {docstring_stats['with_line1']} "
                 f"({100*docstring_stats['with_line1']/docstring_stats['total']:.0f}%)")
    lines.append(f"- no docstring: {docstring_stats['no_doc']}")
    lines.append(f"- parse fail: {docstring_stats['parse_fail']}")
    lines.append(f"\n### Sample line-1 docstrings (first 10)")
    for stem, doc in docstring_samples:
        lines.append(f"- `{stem}.py`: {doc}")

    lines.append("\n## Metadata dict extraction coverage")
    lines.append(f"- modules with `source` in VariableResult metadata: {md_stats['with_source']}")
    lines.append(f"- modules with `column` in metadata: {md_stats['with_column']}")
    lines.append(f"- modules with `reference` in metadata: {md_stats['with_reference']}")
    lines.append(f"\n→ If `with_column` close to 78, the metadata walker is reliable for var↔module")
    lines.append(f"  mapping. If sparse, need fallback (e.g., engine COLS scan).")

    lines.append("\n## Decision points (post-scout)")
    lines.append("1. AST metadata walker needed? → check `with_source` / `with_column` above.")
    lines.append("2. Splice strategy → depends on diff size (missing+dead+incomplete).")
    lines.append("3. Speech IV count → confirms hand-stub list size.")
    lines.append("4. Lead/lag derivative count → confirms naming-rule scope.")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {OUT.relative_to(ROOT)}")
    print(f"  missing={len(missing)} dead={len(dead)} in_both={len(in_both)}")
    print(f"  module docstrings: {docstring_stats['with_line1']}/{docstring_stats['total']}")
    print(f"  metadata column coverage: {md_stats['with_column']}/{len(modules)}")


if __name__ == "__main__":
    main()
