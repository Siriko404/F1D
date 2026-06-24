"""Inject N type bundles into the master WAVE template -> a self-contained runnable.
Usage: python tmp/embed_master.py abstract intro   ->  tmp/run_wave_abstract-intro.js"""
import json, sys
from pathlib import Path
ROOT = Path(".").resolve()
types = sys.argv[1:] or ["abstract", "intro"]
label = "-".join(types)
tpl = (ROOT/"docs/Thesis/rewrite/style_phase1_master.js").read_text(encoding="utf-8")
bundles = [json.loads((ROOT/f"docs/papers/style_exemplars/bundles/{t}.json").read_text(encoding="utf-8")) for t in types]
arr = json.dumps(bundles, ensure_ascii=False)
out, done = [], False
for line in tpl.splitlines():
    if "__BUNDLES_ANCHOR__" in line:
        out.append(f"const BUNDLES = {arr} // wave: {label}")
        done = True
    else:
        out.append(line)
assert done, "anchor __BUNDLES_ANCHOR__ missing"
dest = ROOT/f"tmp/run_wave_{label}.js"
dest.write_text("\n".join(out), encoding="utf-8")
ex = sum(len(b["exemplars"]) for b in bundles); ou = sum(len(b["ours"]) for b in bundles)
print(f"wrote {dest}  | types={types}  exemplars={ex}  ours={ou}  chars={len(chr(10).join(out)):,}")
