"""Phase-2 v2 embed: bake the PAPERS-ONLY exemplars of N writing-types into the harness -> a runnable .js.
Reads docs/papers/style_exemplars/bundles/<type>.json, STRIPS the `ours` half (we analyze ONLY the papers),
and injects TYPES=[{type,exemplars}] at the __TYPES_ANCHOR__ line. The harness never reads files at runtime.

Usage:  python docs/Thesis/rewrite/_phase2_v2/build_v2.py abstract        # smoke (plumbing)
        python docs/Thesis/rewrite/_phase2_v2/build_v2.py methods         # one hard type to READ
        python docs/Thesis/rewrite/_phase2_v2/build_v2.py ALL             # all 8 in batches
"""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]   # .../F1D  (build_v2.py is 4 dirs deep: _phase2_v2/rewrite/Thesis/docs)
ALL = ["abstract", "intro", "lit_review", "hypotheses", "data", "methods", "results", "conclusion"]

# PDF extraction leaves hidden chars (soft hyphen, zero-width, C0/C1 controls, exotic spaces) that
# (a) the Workflow approval dialog rejects and (b) break verbatim quote matching. Strip them at source
# so the agent never sees them and the gate stays consistent. ensure_ascii=True (below) does the rest.
_HIDDEN = dict.fromkeys([0x00ad, 0x200b, 0x200c, 0x200d, 0x2060, 0xfeff], None)  # soft hyphen, ZW*, WJ, BOM
_CTRL   = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_SPACES = re.compile("[  -   　]")  # exotic spaces -> normal space

def clean(s):
    if not isinstance(s, str):
        return s
    s = s.translate(_HIDDEN)
    s = _CTRL.sub("", s)
    s = _SPACES.sub(" ", s)
    return re.sub(r"[ \t]+", " ", s).strip()

def clean_exemplar(s):
    return {
        "paper": clean(s.get("paper", "")),
        "venue": clean(s.get("venue", "")),
        "head":  clean(s.get("head", "")),
        "paragraphs": [clean(p) for p in s.get("paragraphs", [])],
    }

types = sys.argv[1:] or ["abstract"]
if types == ["ALL"]:
    types = ALL
label = "-".join(types) if len(types) <= 3 else f"{len(types)}types"

tpl = (ROOT / "docs/Thesis/rewrite/style_phase2_v2_principles.js").read_text(encoding="utf-8")

TYPES = []
for t in types:
    b = json.loads((ROOT / f"docs/papers/style_exemplars/bundles/{t}.json").read_text(encoding="utf-8"))
    TYPES.append({"type": b["type"], "exemplars": [clean_exemplar(s) for s in b["exemplars"]]})  # papers ONLY

arr = json.dumps(TYPES, ensure_ascii=True)   # pure-ASCII data -> no hidden chars survive into the file
out, done = [], False
for line in tpl.splitlines():
    if "__TYPES_ANCHOR__" in line:
        out.append(f"const TYPES = {arr} // {label}")
        done = True
    else:
        out.append(line)
assert done, "anchor __TYPES_ANCHOR__ missing in harness"

dest = ROOT / f"docs/Thesis/rewrite/_phase2_v2/_run/phase2_v2_{label}.js"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text("\n".join(out), encoding="utf-8", newline="\n")   # LF only; CRLF \r trips the approval dialog

print(f"wrote {dest.relative_to(ROOT)}  ({len(chr(10).join(out)):,} chars)")
print("per-type counts (verify before running -- a dropped bundle shows here):")
for T in TYPES:
    papers = len(T["exemplars"])
    paras = sum(len(s.get("paragraphs", [])) for s in T["exemplars"])
    names = ", ".join(s["paper"] for s in T["exemplars"])
    print(f"  {T['type']:11s} {papers} papers / {paras:3d} paras   [{names}]")
