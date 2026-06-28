# -*- coding: utf-8 -*-
"""Materialize the harness output: read the workflow's returned result (saved to
harness_result.json) and write ONE JSON file per section into output/ -- each section's full,
diligent record (3 drafts + 8 audit reports + coherence issues + judge's final). No two sections
share a file. With --place, also splice each OK section's final_prose into its _final ledger
(GATE: re-run the deterministic checks via the harness's own gate offline before placing)."""
import json, sys
from pathlib import Path
H = Path(__file__).resolve().parent
RES = H / "harness_result.json"          # I save the Workflow tool's returned object here after the run
OUT = H / "output"; OUT.mkdir(exist_ok=True)
FIN = H.parent / "_final"
PLACE = "--place" in sys.argv

if not RES.exists():
    print(f"[wait] {RES.name} not found -- save the Workflow result here first, then re-run."); sys.exit(0)
data = json.loads(RES.read_text(encoding="utf-8"))
results = data.get("results", data if isinstance(data, list) else [])

ok = blocked = 0
written = []
for r in results:
    if not isinstance(r, dict) or not r.get("section"):
        continue
    sec = r["section"]
    stem = "section_abstract" if sec in ("abstract", "_abstract") else ("section" + sec)
    fp = OUT / f"{stem}.json"
    fp.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")   # one file per section
    written.append(fp.name)
    if r.get("status") == "OK": ok += 1
    elif r.get("status") == "BLOCKED": blocked += 1

print(f"materialized {len(written)} per-section files -> output/  ({ok} OK, {blocked} BLOCKED)")
for n in written: print("  -", n)
if blocked:
    print("\nBLOCKED sections (re-run only these via args.only):")
    for r in results:
        if isinstance(r, dict) and r.get("status") == "BLOCKED":
            print(f"  - {r['section']} @ {r.get('stage')}: {str(r.get('detail'))[:120]}")

if PLACE:
    # splice each OK section's final_prose into its _final ledger (separate, gated step)
    placed = 0
    for r in results:
        if not isinstance(r, dict) or r.get("status") != "OK": continue
        sec = r["section"]; stem = "section_abstract" if sec in ("abstract",) else ("section" + sec)
        led = FIN / f"{stem}_paragraph_ledger.json"
        if not led.exists(): print(f"  [skip] no ledger {led.name}"); continue
        d = json.loads(led.read_text(encoding="utf-8"))
        pl = d["paragraphs"]; byid = (pl if isinstance(pl, dict) else {p.get("para_id"): p for p in pl})
        fin = {p["para_id"]: p["final_prose"] for p in r["final"]["paragraphs"]}
        for pid, prose in fin.items():
            tgt = byid.get(pid) if isinstance(byid, dict) else None
            if tgt is not None: tgt["final_prose"] = prose
        led.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        placed += 1
    print(f"\nPLACED final_prose into {placed} ledgers.")
else:
    print("\n(materialize only; pass --place to splice final_prose into the ledgers)")
