import json, re
from pathlib import Path
OUT = Path(r"C:/Users/sinas/AppData/Local/Temp/claude/C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D/1dc537be-cd0b-4f69-bc84-f30eed2a6192/tasks/wsdplxv1c.output")
o = json.loads(OUT.read_text(encoding="utf-8"))
r = o["result"]["results"][0]
r["_provenance"] = {"runId": "wf_1ada80a2-6b9", "wave": "results", "tool_calls_total": 4, "note": "clean under TOOL_LOCK; number-heavy type"}
prof = r["profile"]

# number-touch: our_quote with a real decimal, a p-value, or LaTeX-math containing a digit
NUM = re.compile(r"\d+\.\d+|p\s*(?:<|&lt;)\s*0|percent")
numhits = []
for f in prof:
    if any(NUM.search(q.get("quote", "")) for q in f.get("our_quotes", [])):
        numhits.append((f["id"], f["guardrail_collision"], f["aspect"][:48]))

Path("docs/Thesis/rewrite/style_profiles/results_profile.json").write_text(
    json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"results_profile.json: {len(prof)} findings, "
      f"{len(r.get('guardrail_collisions', []))} guardrail-flagged, "
      f"{len(r.get('gate_rejected', []))} gate-rejected")
print(f"\nNUMBER-TOUCHING findings (Phase-2 must preserve these exact numbers): {len(numhits)}")
for i, gc, asp in numhits:
    print(f"  {i}  guardrail_flag={gc!s:<5}  {asp}")
missed = [i for i, gc, _ in numhits if not gc]
print(f"\n{len(missed)} number-touching findings have guardrail_flag=FALSE -> the collision flag MISSES numbers")
print("(expected: guardrails are concept-notes, not number lists). Phase-2 number-survival gate must scan ALL findings, not just flagged ones.")
