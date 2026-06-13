# Durably stamp the ratification approvals (advisor): 2.2 + 2.3 RATIFIED 2026-06-13.
# Catch-up for the two already approved this ceremony; 2.4/2.5 will be stamped at THEIR approval.
import json

def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    json.load(open(p, encoding="utf-8"))

stamp = "RATIFIED 2026-06-13 (user ratification ceremony)"

# 2.2
p = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
d = load(p)
d["status"] = stamp
d["_schema"]["status"] = ("RATIFIED 2026-06-13 (user ceremony). Prose still BLOCKED -- drafted at write-time after ALL "
    "four subsections are ratified.")
save(p, d)

# 2.3 (incl. the UncPre P3 cut -> P2.5 positive fold)
p = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
d = load(p)
d["status"] = stamp + " -- incl. the UncPre over-control P3 cut -> P2.5 positive fold"
d["_schema"]["status"] = ("RATIFIED 2026-06-13 (user ceremony, incl. the P3 cut). Prose BLOCKED; pagan1984 + the "
    "provisional DWZ-isolation cite verified at write-time.")
save(p, d)

# resume: durable ratification progress
p = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = load(p)
d["updated"] = "2026-06-13 (ratification ceremony IN PROGRESS: 2.2 + 2.3 RATIFIED; 2.4/2.5 pending)"
d["ratification_progress_2026_06_13"] = {
  "_note": "Stamp each subsection at its approval, NOT batched (advisor) -- a compaction can land mid-ceremony.",
  "2.2": "RATIFIED",
  "2.3": "RATIFIED -- incl. the UncPre over-control P3 CUT -> folded positive into P2.5 (DWZ isolation, 'would' not 'must', conservative floor, gated provisional cite); P4 generated-regressand -> P3.",
  "2.4": "PENDING (ceremony interrupted at its ratify question; re-present next).",
  "2.5": "PENDING."
}
d["NEXT_ACTION"] = ("===RATIFICATION IN PROGRESS (2026-06-13): 2.2 + 2.3 RATIFIED; 2.4 NEXT, then 2.5.=== "
    "Re-present 2.4 (Methodology) for approve/amend, then 2.5 (Specification/validity). Stamp EACH at approval "
    "(programmatic + commit), not batched. AFTER all four ratified -> prose ONE PARAGRAPH AT A TIME (order 2.2->2.5, "
    "per paragraph_workflow.json): verify props -> draft -> accuracy-pass -> advisor -> show user -> record final_prose "
    "+ unlock prose_gate. WRITE-TIME FLAGS (PENDING_EDITS_unapplied.WRITE_TIME_FLAGS): F2 hoberg2010/fluidity, F5 "
    "Hassan year, F1-leak varledger L188, the PROVISIONAL DWZ-isolation cite in 2.3 P2.5 (answer-only -> verbatim or "
    "fall back to hedge), owed NLM cites (pagan/opler/bates/petersen/cameron), bible cross-check C3/C4/C5, R2. "
    "DISCIPLINE: no prose before full ratification; transfer to ledgers PROGRAMMATICALLY.")
save(p, d)

print("stamped RATIFIED: 2.2, 2.3; resume ratification_progress + NEXT_ACTION updated; all re-parsed OK")
