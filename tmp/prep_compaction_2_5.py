# Compaction-prep: mark 2.5 flags FA/FD/FC DONE (FB placeholder), sweep resume to current reality. Fail-closed.
import json

# 1) 2.5 ledger flags status
LED = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
d = json.load(open(LED, encoding="utf-8"))
assert "PENDING_REWRITE_FLAGS_2026_06_14" in d
d["PENDING_REWRITE_FLAGS_2026_06_14"]["_STATUS_2026_06_14"] = ("FA (drop competition/P3) DONE -- P3 deleted, hoberg cites + bibitems removed, "
    "P1/P2/_plan/papers scrubbed, .tex+roadmap+claim_findings competition-free (post-gate passed). FD (lead with significant association) DONE in P2. "
    "FC (CashScrutiny word list -> Appendix pointer) DONE in P4. FB (economic effect) = OPEN PLACEHOLDER '[PLACEHOLDER-FB]' in P2: the 1-SD magnitudes "
    "are NOT computed -- the summary stats were disregarded as wrong by the user; FILL after corrected summary stats are built. Do NOT fabricate.")
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))

# 2) resume sweep
RS = "docs/Thesis/rewrite/_RESUME_STATE.json"
r = json.load(open(RS, encoding="utf-8"))
r["updated"] = "2026-06-14 (PROSE PHASE: full §2 in .tex/PDF; competition test DROPPED; 2.5 redrafted; 2.3/2.4/2.5 awaiting ratification; FB placeholder open)"
r["where_we_are"] = ("[2026-06-14] §2 PROSE. FULL §2 (2.1 locked+ratified, 2.2 ratified, 2.3/2.4/2.5 DRAFTED) in thesis_draft.tex + PDF (9pp, compiles clean, "
    "no undefined cites). COMPETITION / DISCRIMINANT TEST DROPPED ENTIRELY (user): old 2.5 P3 gone, hoberg cites+bibitems removed, all docs scrubbed "
    "(post-gate = zero competition in .tex/roadmap/bib; ledger/claim_findings carry [DROPPED] tombstones). 2.5 now P1/P2/P4/P5: P1 convergent+scrutiny "
    "frame; P2 LEADS with the significant convergent association (one-tailed) + a [PLACEHOLDER-FB] economic-magnitude stub; P4 scrutiny+Appendix pointer; "
    "P5 constructs. UNCOMMITTED work committed this turn as a DRAFTED checkpoint. 2.3/2.4/2.5 NOT ratified -- awaiting user PDF review.")
r["NEXT_ACTION"] = ("=== AWAIT user ratification of 2.3 / 2.4 / 2.5 from the PDF (all DRAFTED, committed as checkpoints). ON ratify (each): flip its ledger "
    "gate -> commit. OPEN ITEMS: (1) FB: fill the '[PLACEHOLDER-FB]' 1-SD economic magnitudes in 2.5 P2 AFTER corrected summary statistics are built (the "
    "prior summary stats were disregarded as wrong; do NOT fabricate); (2) FC: populate the Appendix with the CashScrutiny cash/liquidity word list (P4 "
    "forward-references it; transcribe from code); (3) the 2.1-P7 softening (cut 'and we do not try', keep 'Our design cannot distinguish them.', remove the "
    "P7 TODO). AFTER all five ratified -> whole-§2 coherence pass. If EDITS to any pushed section: edit draft -> re-record -> re-push(replace) -> recompile. "
    "DISCIPLINE: programmatic transfer w/ drift+dash+no-competition asserts + COLUMN-aligned number checks; numbers from regression tables (summary stats "
    "DISREGARDED); NLM sole paper authority; SHOW/ratify in PDF; hypotheses set off; no '---'/'--'.")
s = r["prose_progress_2026_06_13"]["status"]
s["2.5 (whole)"] = ("REDRAFTED 2026-06-14 + pushed + compiled (in PDF, 9pp): competition/discriminant DROPPED completely (P3 gone, hoberg removed); FA/FD/FC "
    "DONE; FB = open [PLACEHOLDER-FB] (pending corrected summary stats). Committed as DRAFTED checkpoint; NOT ratified.")
open(RS, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
json.load(open(RS, encoding="utf-8"))
print("prep done: 2.5 flags status (FA/FD/FC DONE, FB placeholder) + resume swept to current reality.")
