#!/usr/bin/env python3
"""G1b embed-parity gate (audit P1; closes the bible->embed provenance link).

G1 proved code->fragments->bible; verify_draft_numbers proved prose<->bible. But
the thesis COMPILES \\input{_tables_from_bible} -> docs/Thesis/_tables_from_bible.tex,
a byte-exact embed generated FROM the bible by tmp/extract_draft_tables.py. Nothing
upstream value-diffed that embed against the validated bible, so the table cells the
REFEREE actually reads were never checked against the source we validated.

This closes it with G1's pattern: regenerate the embed from the (validated) bible +
fragments and byte-diff vs the committed embed. MATCH => the rendered tables are the
validated numbers. Restores the committed embed in a finally block (extractor writes it).

Run: python tmp/audit_g1b_embed_parity.py     (exit 1 on MISMATCH)
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMBED = ROOT / "docs" / "Thesis" / "_tables_from_bible.tex"
EXTRACTOR = ROOT / "tmp" / "extract_draft_tables.py"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


before = sha(EMBED)
err = None
try:
    r = subprocess.run([sys.executable, str(EXTRACTOR)], cwd=ROOT,
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        err = f"extractor exit {r.returncode}: {r.stderr.strip()[-400:]}"
    after = sha(EMBED)
finally:
    # restore the committed embed whatever happened
    subprocess.run(["git", "checkout", "--", "docs/Thesis/_tables_from_bible.tex"],
                   cwd=ROOT, capture_output=True, text=True)

status = "MATCH" if (not err and before == after) else ("BLOCKED" if err else "MISMATCH")
out = {
    "gate": "G1b_embed_parity",
    "baseline_sha": "7f97a16",
    "purpose": "prove the compiled embed docs/Thesis/_tables_from_bible.tex == regenerate-from-validated-bible",
    "extractor": "tmp/extract_draft_tables.py",
    "committed_embed_sha256": before,
    "regenerated_embed_sha256": after if not err else None,
    "status": status,
    "error": err,
}
(ROOT / "docs" / "Thesis" / "audit" / "g1b_embed_parity.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8")

# verify restore
st = subprocess.run(["git", "status", "--porcelain", "--", "docs/Thesis/_tables_from_bible.tex"],
                    cwd=ROOT, capture_output=True, text=True).stdout.strip()
print("G1b embed-parity  (baseline 7f97a16)")
print("=" * 72)
print(f"  committed   : {before[:16]}")
print(f"  regenerated : {(after[:16]) if not err else 'n/a'}")
print(f"  STATUS      : {status}" + (f"   {err}" if err else ""))
print(f"  embed restored: {'CLEAN' if not st else 'DIRTY -> ' + st}")
print(f"  written: docs/Thesis/audit/g1b_embed_parity.json")
sys.exit(0 if status == "MATCH" else 1)
