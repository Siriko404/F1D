# Flip §2.2 to RATIFIED (user approved from the PDF, 2026-06-13). Unlock all gates. Fail-closed.
import json
p = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
P = d["paragraphs"]
for k in ["P1", "P2", "P3", "P4", "P5"]:
    assert "NOT ratified" in P[k]["prose_status"], f"{k} unexpected state: {P[k]['prose_status']!r}"
    P[k]["prose_status"] = "RATIFIED 2026-06-13 (user, from PDF) -- v2: hypotheses set off (informal+formal math), dash-free"
    P[k]["prose_gate"]["all_supported"] = True
    P[k]["prose_gate"]["unlocked"] = True
d["status"] = "RATIFIED PROSE 2026-06-13 (user, from PDF); v2 hypotheses set off + dash-free; in thesis_draft.tex."
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))
print("2.2 RATIFIED: P1-P5 gates unlocked.")
