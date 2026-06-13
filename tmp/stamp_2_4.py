# Stamp 2.4 RATIFIED (at approval, not batched -- advisor) + record the 2 advisor write-time flags. Programmatic.
import json

def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    json.load(open(p, encoding="utf-8"))

# 2.4
p = "docs/Thesis/rewrite/section2.4_paragraph_ledger.json"
d = load(p)
d["status"] = "RATIFIED 2026-06-13 (user ratification ceremony)"
d["_schema"]["status"] = ("RATIFIED 2026-06-13 (user ceremony). Prose BLOCKED; NEW cites (opler1999/bates2009/"
    "petersen2009/cameron2011) verify at write-time.")
save(p, d)

# resume: 2.4 done, 2.5 next + the 2 advisor write-time flags for 2.4 P2 prose
p = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = load(p)
d["updated"] = "2026-06-13 (ratification: 2.2 + 2.3 + 2.4 RATIFIED; 2.5 pending -- the last)"
d["ratification_progress_2026_06_13"]["2.4"] = "RATIFIED."
d["ratification_progress_2026_06_13"]["2.5"] = "PENDING (re-present next -- the LAST subsection)."
flags = d["PENDING_EDITS_unapplied"]["WRITE_TIME_FLAGS"]
flags.append("2.4 P2 (MNPI): 'MNPI' = MY expansion to 'Material Non-Public Information' (the ledger uses the bare "
    "token) -> confirm the term against the source at write-time; do NOT assert the expansion from memory (advisor).")
flags.append("2.4 P2 (GAP discriminator): the 'cash persists through the GAP' leg is LARGELY MECHANICAL (cash is paid "
    "only at completion, so it sits on the books during the GAP) -- 2.2 P4.3 'partly mechanical' -- NOT a separate "
    "estimated event-study result. The discriminator's empirical bite is the UNCERTAINTY drop at the GAP; do not "
    "present cash-persistence as an estimated contrast (advisor).")
d["NEXT_ACTION"] = ("===RATIFICATION (2026-06-13): 2.2 + 2.3 + 2.4 RATIFIED; 2.5 NEXT (the LAST).=== Re-present 2.5 "
    "(Specification & Measurement / validity) for approve/amend, stamp at approval + commit. AFTER 2.5 -> ALL FOUR "
    "ratified -> prose ONE PARAGRAPH AT A TIME (order 2.2->2.5, per paragraph_workflow.json): verify props -> draft -> "
    "accuracy-pass -> advisor -> show user -> record final_prose + unlock prose_gate. WRITE-TIME FLAGS in "
    "PENDING_EDITS_unapplied.WRITE_TIME_FLAGS (incl. the 2 new 2.4-P2 ones: MNPI expansion, cash-persists mechanical). "
    "DISCIPLINE: no prose before full ratification; transfer PROGRAMMATICALLY.")
save(p, d)
print("2.4 stamped RATIFIED; resume updated; 2 advisor write-time flags recorded; re-parse OK")
