#!/usr/bin/env python3
"""G4 compile & cross-ref integrity gate (audit P1, mechanical, no-LLM).

Protocol (AUDIT_PROTOCOL.md SS5/P1): "parse the .log; label<->ref matrix; cite<->bibitem
matrix (incl. fragments)." Baseline compile is already 0 undefined (baseline.json);
G4 makes that EXHAUSTIVE and matrix-complete rather than a bare count==0.

Compiled document = docs/Thesis/thesis_draft.tex + its only \\input,
docs/Thesis/_tables_from_bible.tex (the byte-exact embedded tables). natbib with
embedded \\bibitem (no bibtex), so cite<->bibitem is fully internal.

Checks (static extraction over the compiled sources + a log parse):
  ref  -> label : every \\ref/\\eqref/\\autoref/\\pageref resolves      (unresolved = CRITICAL)
  label-> ref   : labels never referenced                              (unused = MINOR)
  cite -> bibitem: every \\cite*/\\citep/\\citet key has a \\bibitem      (undefined = CRITICAL)
  bibitem->cite : \\bibitem never cited                                 (uncited = MINOR)
  duplicate \\label                                                      (multiply-defined = CRITICAL)
  log parse: undefined refs/cites, multiply-defined, rerun-needed

Run: python tmp/audit_g4.py     (exit 1 on any CRITICAL)
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THESIS = ROOT / "docs" / "Thesis"
SRC = {
    "thesis_draft.tex": (THESIS / "thesis_draft.tex").read_text(encoding="utf-8"),
    "_tables_from_bible.tex": (THESIS / "_tables_from_bible.tex").read_text(encoding="utf-8"),
}
LOG = THESIS / "thesis_draft.log"


def strip_comments(t: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", t)


# --- extract with source-file + multiplicity -----------------------------------
def find_all(pattern: str, *, split_keys: bool = False):
    """Return list of (key, file). split_keys handles \\citep{a,b,c}."""
    out = []
    rx = re.compile(pattern)
    for fname, text in SRC.items():
        for m in rx.finditer(strip_comments(text)):
            grp = m.group(1)
            keys = [k.strip() for k in grp.split(",")] if split_keys else [grp.strip()]
            for k in keys:
                if k:
                    out.append((k, fname))
    return out


labels = find_all(r"\\label\{([^}]*)\}")
refs = find_all(r"\\(?:ref|eqref|autoref|pageref|Cref|cref)\{([^}]*)\}", split_keys=True)
cites = find_all(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", split_keys=True)
bibitems = find_all(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}")

label_set = [k for k, _ in labels]
ref_set = [k for k, _ in refs]
cite_set = [k for k, _ in cites]
bib_set = [k for k, _ in bibitems]

# --- matrices ------------------------------------------------------------------
dup_labels = sorted({k for k in label_set if label_set.count(k) > 1})
dup_bibitems = sorted({k for k in bib_set if bib_set.count(k) > 1})
unresolved_refs = sorted({k for k in ref_set if k not in label_set})
unused_labels = sorted({k for k in label_set if k not in ref_set})
undefined_cites = sorted({k for k in cite_set if k not in bib_set})
uncited_bibitems = sorted({k for k in bib_set if k not in cite_set})

# --- log parse -----------------------------------------------------------------
log_flags = {}
if LOG.exists():
    log = LOG.read_text(encoding="utf-8", errors="replace")
    log_flags = {
        "undefined_references_warning": "There were undefined references" in log,
        "undefined_citations_warning": bool(re.search(r"Citation .* undefined", log)),
        "multiply_defined": "multiply defined" in log.lower(),
        "rerun_needed": "Rerun to get cross-references right" in log,
        "undefined_control_seq": log.count("Undefined control sequence"),
        "n_warnings": len(re.findall(r"LaTeX Warning:", log)),
    }

criticals = []
if unresolved_refs:
    criticals.append(f"unresolved \\ref -> {unresolved_refs}")
if undefined_cites:
    criticals.append(f"undefined \\cite -> {undefined_cites}")
if dup_labels:
    criticals.append(f"duplicate \\label -> {dup_labels}")
if log_flags.get("undefined_references_warning") or log_flags.get("undefined_citations_warning"):
    criticals.append("log: undefined refs/citations warning present")

minors = []
if unused_labels:
    minors.append(f"unused \\label (never \\ref'd) -> {unused_labels}")
if uncited_bibitems:
    minors.append(f"uncited \\bibitem -> {uncited_bibitems}")

out = {
    "gate": "G4_compile_crossref",
    "baseline_sha": "7f97a16",
    "compiled_sources": list(SRC.keys()),
    "tallies": {
        "labels": len(set(label_set)), "refs": len(set(ref_set)),
        "cites": len(set(cite_set)), "bibitems": len(set(bib_set)),
    },
    "label_ref_matrix": {
        "unresolved_refs": unresolved_refs,
        "unused_labels": unused_labels,
        "duplicate_labels": dup_labels,
    },
    "cite_bibitem_matrix": {
        "undefined_cites": undefined_cites,
        "uncited_bibitems": uncited_bibitems,
        "duplicate_bibitems": dup_bibitems,
    },
    "log_flags": log_flags,
    "findings": {"CRITICAL": criticals, "MINOR": minors},
    "all_labels": sorted(set(label_set)),
    "all_cites": sorted(set(cite_set)),
    "all_bibitems": sorted(set(bib_set)),
}
(THESIS / "audit" / "g4_compile_crossref.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

print("\nG4 compile & cross-ref integrity  (baseline 7f97a16)")
print("=" * 72)
print(f"  labels={len(set(label_set))}  refs={len(set(ref_set))}  "
      f"cites={len(set(cite_set))}  bibitems={len(set(bib_set))}")
print(f"  ref->label : unresolved={unresolved_refs or 'none'}  dup_labels={dup_labels or 'none'}")
print(f"  cite->bib  : undefined={undefined_cites or 'none'}  dup_bibitems={dup_bibitems or 'none'}")
print(f"  unused labels (MINOR): {unused_labels or 'none'}")
print(f"  uncited bibitems (MINOR): {uncited_bibitems or 'none'}")
print(f"  log: {log_flags}")
print("=" * 72)
print(f"  CRITICAL={len(criticals)}  MINOR={len(minors)}")
for c in criticals:
    print(f"    [CRIT] {c}")
for m in minors:
    print(f"    [min ] {m}")
print(f"  written: docs/Thesis/audit/g4_compile_crossref.json")
sys.exit(1 if criticals else 0)
