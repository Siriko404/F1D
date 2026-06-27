"""Clone the 5 pristine section-2 paragraph ledgers into _phase3_clones/, stripping the
old locked final_prose so the clones are clean chain-work files. Originals untouched.

Run:  python tmp/clone_s2_strip_prose.py
"""
import json
from pathlib import Path

FORK = Path(__file__).resolve().parents[1]
RW = FORK / "docs" / "Thesis" / "rewrite"
CLONE_DIR = RW / "_phase3_clones"
CLONE_DIR.mkdir(parents=True, exist_ok=True)

SUBS = ["2.1", "2.2", "2.3", "2.4", "2.5"]
PROSE_KEYS = ("final_prose", "final_prose_PRE_MASKING")

for s in SUBS:
    orig = RW / f"section{s}_paragraph_ledger.json"
    data = json.loads(orig.read_text(encoding="utf-8"))
    para = data.get("paragraphs")
    items = list(para.values()) if isinstance(para, dict) else para
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
        "purpose": "Phase-3 section-2 chain redesign; locked final_prose stripped for clean chain work.",
        "built_by": "tmp/clone_s2_strip_prose.py",
        "note": "Proposed chain fixes are APPENDED under _proposed_fixes; original propositions untouched.",
    }
    out = CLONE_DIR / f"section{s}_paragraph_ledger.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    sz0 = orig.stat().st_size; sz1 = out.stat().st_size
    print(f"section{s}: cloned -> _phase3_clones/  | prose fields stripped: {stripped}  "
          f"| {sz0:,}B -> {sz1:,}B")

print("\nORIGINALS untouched (clones written under _phase3_clones/).")
