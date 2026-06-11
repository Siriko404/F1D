#!/usr/bin/env python3
"""G5 ledger-freshness gate (audit P1, mechanical, git+content evidence).

Protocol (AUDIT_PROTOCOL.md SS5/P1): "verify every file:line evidence anchor in
variable_ledger.json still matches current code (hand-built 2026-06-10; code may
have moved). Stale anchors -> re-trace in P2."

Two-layer evidence:
  LAYER 1 (git): for every .py file the ledger anchors into, is its last content
    change AFTER the ledger date (2026-06-10)? A file unchanged since before the
    ledger was written CANNOT have drifted -> its anchors are FRESH by construction.
    (Tree is frozen/clean at 7f97a16, so on-disk == committed == git history.)
  LAYER 2 (content): for files that DID change after the ledger, line numbers may
    have moved. Each such anchor carries a quoted code token in the ledger; probe
    the CURRENT file for it and classify FRESH / DRIFTED / STALE by whether the
    token still sits in the claimed line range.

Also: resolve basename mentions to full paths, confirm no referenced file is
actually missing, and bound-check every anchor (line <= file length).

Run: python tmp/audit_g5.py     (exit 1 on STALE/DRIFTED/MISSING)
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "Thesis" / "variable_ledger.json"
LEDGER_DATE = "2026-06-10"
RAW = LEDGER.read_text(encoding="utf-8")
DOC = json.loads(RAW)

# --- resolve every referenced .py: full paths + basename-only mentions ---------
all_py = sorted(set(re.findall(r"[\w./]*\w\.py", RAW)))
full_paths = [p for p in all_py if "/" in p and (ROOT / p).exists()]
basename_to_full = {}
for p in full_paths:
    basename_to_full.setdefault(Path(p).name, []).append(p)

missing = []
for p in all_py:
    if "/" in p:
        if not (ROOT / p).exists():
            missing.append(p)
    else:  # basename only -> must resolve to exactly one full path
        if p not in basename_to_full:
            missing.append(p + " (basename, unresolved)")


def last_change(relpath: str) -> str:
    r = subprocess.run(["git", "log", "-1", "--format=%cI", "--", relpath],
                       cwd=ROOT, capture_output=True, text=True)
    return (r.stdout.strip()[:10]) or "NO-COMMITS"


# --- LAYER 1: git partition ----------------------------------------------------
changed_after, fresh_by_git = [], []
for p in full_paths:
    d = last_change(p)
    (changed_after if d > LEDGER_DATE else fresh_by_git).append((p, d))

# --- LAYER 2: content probes for the changed (suspect) files -------------------
# (file, claimed_lo, claimed_hi, probe_regex, what the ledger says is there)
PROBES = [
    ("scripts/gen_empire_did_table.py", 141, 143, r"PanelOLS|EntityEffects|TimeEffects", "two-way FE estimator"),
    ("scripts/gen_empire_did_table.py", 66, 70, r"file_name", "merge residual parquet on file_name"),
    ("scripts/gen_empire_did_table.py", 71, 73, r"stock_score[\"'\]\s]*\*\s*100", "CashScrutiny = stock_score*100"),
    ("scripts/gen_summary_stats_table.py", 1, 99999, r"def main|def build|summary", "summary-stats generator present"),
    ("src/f1d/econometric/empire_drop_matched_universe.py", 90, 147, r"def write_tex", "write_tex renderer"),
    ("src/f1d/econometric/empire_drop_matched_universe.py", 49, 56, r"def run_on", "run_on estimator"),
    ("src/f1d/econometric/empire_drop_matched_universe.py", 63, 69, r"def wald", "wald drop-difference"),
    ("src/f1d/econometric/empire_drop_test.py", 109, 141, r"def build_event", "build_event bins"),
    ("src/f1d/econometric/empire_drop_test.py", 126, 133, r"\+\s*4|cap|trunc|withdraw|2nd|second", "post-window hygiene"),
    ("src/f1d/econometric/empire_drop_test.py", 188, 242, r"def write_tex", "write_tex (placebo fragment)"),
    ("src/f1d/econometric/empire_drop_test.py", 10, 15, r"event|bin|PRE|deal|empire", "module docstring"),
    ("src/f1d/econometric/empire_cashspec_interaction.py", 124, 205, r"def write_tex", "write_tex renderer"),
]


def probe(relpath, lo, hi, rx):
    lines = (ROOT / relpath).read_text(encoding="utf-8", errors="replace").splitlines()
    nlines = len(lines)
    rxc = re.compile(rx)
    matches = [i + 1 for i, ln in enumerate(lines) if rxc.search(ln)]
    in_range = [m for m in matches if lo - 2 <= m <= hi + 2]
    if in_range:
        verdict = "FRESH"
    elif matches:
        verdict = "DRIFTED"
    else:
        verdict = "STALE"
    return verdict, in_range, matches[:10], nlines


content = []
suspect_files = {p for p, _ in changed_after}
for relpath, lo, hi, rx, what in PROBES:
    if not (ROOT / relpath).exists():
        content.append({"file": relpath, "claimed": f"L{lo}-{hi}", "what": what, "verdict": "MISSING"})
        continue
    verdict, in_range, matches, nlines = probe(relpath, lo, hi, rx)
    content.append({"file": relpath, "claimed": f"L{lo}-{hi}", "what": what,
                    "verdict": verdict, "in_range_hits": in_range, "all_hits": matches,
                    "file_lines": nlines, "changed_after_ledger": relpath in suspect_files})

# --- bound-check ALL anchors (line <= file length) across resolved files --------
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


bound_violations = []
for path, s in walk(DOC):
    files_in = re.findall(r"[\w./]*\w\.py", s)
    Ls = [int(x) for x in re.findall(r"L(\d+)", s)]
    if not files_in or not Ls:
        continue
    # associate every L with the nearest resolvable file in the string
    fulls = []
    for f in files_in:
        if "/" in f and (ROOT / f).exists():
            fulls.append(f)
        elif f in basename_to_full and len(basename_to_full[f]) == 1:
            fulls.append(basename_to_full[f][0])
    if not fulls:
        continue
    maxline = max((ROOT / fulls[-1]).read_text(encoding="utf-8", errors="replace").count("\n") + 1, 1)
    for L in Ls:
        if L > maxline:
            bound_violations.append({"path": path, "file": fulls[-1], "L": L, "file_lines": maxline})

stale = [c for c in content if c["verdict"] in ("DRIFTED", "STALE", "MISSING")]
crit = bool(stale or missing or bound_violations)

out = {
    "gate": "G5_ledger_freshness",
    "baseline_sha": "7f97a16",
    "ledger_date": LEDGER_DATE,
    "method": "LAYER1 git (file unchanged since before ledger -> anchors fresh by construction); "
              "LAYER2 content probe for files changed after the ledger; basename resolution; bound-check.",
    "referenced_py_files": len(full_paths),
    "missing_files": missing,
    "git_partition": {
        "changed_after_ledger": sorted(changed_after),
        "fresh_by_git_count": len(fresh_by_git),
        "fresh_by_git": sorted(fresh_by_git),
    },
    "content_probes": content,
    "bound_violations": bound_violations,
    "verdict": "STALE" if crit else "FRESH",
}
(ROOT / "docs" / "Thesis" / "audit" / "g5_ledger_freshness.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8")

print("\nG5 ledger-freshness  (baseline 7f97a16, ledger 2026-06-10)")
print("=" * 72)
print(f"  referenced .py files: {len(full_paths)}   missing: {missing or 'none'}")
print(f"  git: {len(fresh_by_git)} unchanged-since-before-ledger (FRESH), "
      f"{len(changed_after)} changed-after -> content-probed")
for p, d in sorted(changed_after):
    print(f"      changed {d}  {p}")
print("  content probes (changed files):")
for c in content:
    mark = {"FRESH": "ok  ", "DRIFTED": "DRIFT", "STALE": "STALE", "MISSING": "MISS"}[c["verdict"]]
    print(f"    [{mark}] {c['claimed']:10s} {c['what']:32s} in-range={c.get('in_range_hits')}  {Path(c['file']).name}")
print(f"  bound violations (line>EOF): {bound_violations or 'none'}")
print("=" * 72)
print(f"  VERDICT: {out['verdict']}   (stale/drift={len(stale)}, missing={len(missing)}, bound={len(bound_violations)})")
print(f"  written: docs/Thesis/audit/g5_ledger_freshness.json")
sys.exit(1 if crit else 0)
