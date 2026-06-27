"""Generic: clone the given subsections' pristine paragraph ledgers into _phase3_clones/,
stripping locked final_prose for clean chain-work files. Originals untouched.

Usage:  python tmp/clone_strip_prose.py 3.1 3.2 3.3 3.4
Handles both schemas (paragraphs as dict{P1..} or list[]).
"""
import json, sys
from pathlib import Path

FORK = Path(__file__).resolve().parents[1]
RW = FORK / "docs" / "Thesis" / "rewrite"
CLONE_DIR = RW / "_phase3_clones"
CLONE_DIR.mkdir(parents=True, exist_ok=True)
PROSE_KEYS = ("final_prose", "final_prose_PRE_MASKING")

for s in sys.argv[1:]:
    orig = RW / f"section{s}_paragraph_ledger.json"
    data = json.loads(orig.read_text(encoding="utf-8"))
    para = data.get("paragraphs")
    items = list(para.values()) if isinstance(para, dict) else (para or [])
    stripped = 0
    for p in items:
        if not isinstance(p, dict):
            continue
        for k in PROSE_KEYS:
            if k in p and p[k]:
                p[k] = ""
                stripped += 1
        if "prose_status" in p:
            p["prose_status"] = "PROSE-STRIPPED (chain-work clone; prose regenerated after chain ratified)"
    data["_clone_provenance"] = {
        "is_clone": True, "of": f"section{s}_paragraph_ledger.json (pristine original)",
        "purpose": "Phase-3 chain redesign; locked final_prose stripped.",
        "built_by": "tmp/clone_strip_prose.py",
        "note": "Proposed chain fixes APPENDED under _proposed_fixes; original chain untouched.",
    }
    out = CLONE_DIR / f"section{s}_paragraph_ledger.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"section{s}: stripped {stripped} prose fields | {orig.stat().st_size:,}B -> {out.stat().st_size:,}B")
print("ORIGINALS untouched.")
