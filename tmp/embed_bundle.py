"""Inject a type bundle into the workflow template -> a self-contained runnable .js (no args needed).
Deterministic: the bundle JSON never passes through hand-transcription."""
import json, sys
from pathlib import Path
ROOT = Path(".").resolve()
btype = sys.argv[1] if len(sys.argv) > 1 else "lit_review"

tpl    = (ROOT/"docs/Thesis/rewrite/style_phase1_pilot.js").read_text(encoding="utf-8")
bundle = json.loads((ROOT/f"docs/papers/style_exemplars/bundles/{btype}.json").read_text(encoding="utf-8"))
lit    = json.dumps(bundle, ensure_ascii=False)   # valid JSON == valid JS object literal

out, done = [], False
for line in tpl.splitlines():
    if "__BUNDLE_ANCHOR__" in line:
        out.append(f"const A = {lit} // bundle embedded: {btype}")
        done = True
    else:
        out.append(line)
assert done, "anchor __BUNDLE_ANCHOR__ not found in template"

dest = ROOT/f"tmp/run_{btype}.js"
dest.write_text("\n".join(out), encoding="utf-8")
print(f"wrote {dest}  | chars={len('\\n'.join(out)):,}  exemplars={len(bundle['exemplars'])}  ours={len(bundle['ours'])}")
