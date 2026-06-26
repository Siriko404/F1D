"""Prepare one runnable .js per remaining writing-type (separate files, for one-by-one firing).
Builds each via build_v2.py, scans the output for CR / non-ASCII / control chars (spawn-safety),
and reports paper/paragraph counts so a dropped bundle is visible."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TYPES = ["intro", "lit_review", "hypotheses", "data", "methods", "results", "conclusion"]  # abstract already done
BUILD = ROOT / "docs/Thesis/rewrite/_phase2_v2/build_v2.py"
RUN = ROOT / "docs/Thesis/rewrite/_phase2_v2/_run"

print(f"  {'type':12s} {'papers':>6} {'paras':>5} {'size':>9}  status")
allok = True
for t in TYPES:
    subprocess.run([sys.executable, str(BUILD), t], capture_output=True)
    f = RUN / f"phase2_v2_{t}.js"
    if not f.exists():
        print(f"  {t:12s} {'--':>6} {'--':>5} {'--':>9}  MISSING"); allok = False; continue
    b = f.read_bytes()
    dirty = b.count(13) > 0 or any(x > 0x7f or (x < 0x20 and x not in (9, 10)) for x in b)
    bundle = json.loads((ROOT / f"docs/papers/style_exemplars/bundles/{t}.json").read_text(encoding="utf-8"))
    ex = bundle["exemplars"]
    papers = len(ex)
    paras = sum(len(s.get("paragraphs", [])) for s in ex)
    if dirty:
        allok = False
    print(f"  {t:12s} {papers:>6} {paras:>5} {len(b):>8,}b  {'DIRTY' if dirty else 'clean'}")
print("\nALL 7 CLEAN - ready to fire" if allok else "\n!! some DIRTY - do not fire")
