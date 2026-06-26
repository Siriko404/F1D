"""Materialize a harness run's returned object to durable rulebooks (mechanical write, NOT grading).
Usage: python finalize_v2.py <path-to-task.output>
Writes docs/papers/style_exemplars/_rulebooks_v2/<type>.json (full per-type result: principles + dropped + side_notes)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DST = ROOT / "docs/papers/style_exemplars/_rulebooks_v2"
DST.mkdir(parents=True, exist_ok=True)

src = Path(sys.argv[1])
o = json.loads(src.read_text(encoding="utf-8"))
results = (o.get("result") or {}).get("results") or []
if not results:
    print("no results in", src); sys.exit(1)

for r in results:
    t = r["type"]
    principles = r.get("principles") or []
    (DST / f"{t}.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    gr = len(r.get("gate_rejected") or [])
    note = r.get("note") or ""
    flag = "  <-- 0 principles!" if not principles else ""
    print(f"  {t:12s} {len(principles):>2} principles  ({gr} gate-rejected)  {note}{flag}")
