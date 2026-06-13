# Reconcile the resume so it reads as ONE coherent story (advisor): the scrutiny reframe is the ACTIVE
# unapplied work, NOT "only write-time flags"; matsumoto is nice-to-have, not a blocker; clear stale spots.
import json
p = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(p, encoding="utf-8"))

# C1 -- mission stale "currently in 2.1"
d["mission"] = ("Rewrite thesis Section 2 (Conceptual Framework and Empirical Strategy) paragraph-by-paragraph to a thin, "
    "referee-proof, COMPLETE claim, from scratch. 2.1 (the lit-review framework, 7 paragraphs) is LOCKED in thesis_draft.tex. "
    "Currently applying the SCRUTINY-DRIVER reframe to the 2.2/2.5 PLANS (then re-ratify) before any 2.2-2.5 prose.")

# A (advisor #1) -- PENDING_EDITS._note now CONTRADICTS scrutiny_reframe ("only write-time flags remain" is false)
d["PENDING_EDITS_unapplied"]["_note"] = ("The yardstick-AUDIT edits (F1-F5) were applied to the 2.2/2.3/2.5 PLANS (see "
    "EDITS_APPLIED_2026_06_13). BUT a NEW major edit is now DECIDED + UNAPPLIED: the SCRUTINY-DRIVER REFRAME "
    "(scrutiny_reframe_DECIDED_2026_06_13), which re-opens 2.2 P5 + 2.5 P4 + a 2.1-P7 prose touch. So 'only write-time flags "
    "remain' is NO LONGER true -- the scrutiny reframe is the ACTIVE unapplied work. The WRITE_TIME_FLAGS below are the "
    "SEPARATE at-prose-time items.")

# C2 -- EDITS_APPLIED superseded-in-part pointer
d["EDITS_APPLIED_2026_06_13"]["_superseded_in_part"] = ("The SCRUTINY-DRIVER reframe (scrutiny_reframe_DECIDED_2026_06_13) "
    "lands ON TOP of these -- it re-opens 2.2 P5 + 2.5 P4 framing. These F1-F5 edits STAND; the reframe is the next layer, "
    "after which 2.2 + 2.5 re-ratify.")

# C3 -- section_2_1_paragraphs: clarify ALL P1-P7 are locked prose in the .tex
d["section_2_1_paragraphs"]["_status"] = ("ALL of P1-P7 are DONE + LOCKED as PROSE in thesis_draft.tex (the 2.1-only file). "
    "The per-paragraph notes below are HISTORICAL plan rationale (P1/P2 say DONE; the P3-P7 notes predate drafting, but their "
    "PROSE is locked in the .tex). The ONLY pending 2.1 change is the P7 'and we do not try'->'cannot' softening (scrutiny_reframe; "
    "P7 carries a TODO comment in the .tex).")

# C4 -- the_draft pointer (post-trim reality)
d["files_of_record"]["the_draft"] = ("docs/Thesis/thesis_draft.tex -- now 2.1-ONLY (117 lines, post-trim 2026-06-13). 2.1 = "
    "\\section{Conceptual Framework and Empirical Strategy} + \\subsection{Conceptual Framework}, P1-P7 (currently ~L26-43); the "
    "bibliography follows. Locate 2.1 by HEADING, not line number. Full prior draft (abstract/intro/stale-2.2-2.5/3/4/5/appendices) "
    "recoverable at commit 81efc78. P7 (~L43) carries a TODO comment marking the scrutiny-reframe softening.")

# B (advisor #3) -- NEXT_ACTION: matsumoto is NICE-TO-HAVE, not a blocker; reframe rests on our own co-movements
d["NEXT_ACTION"] = (
"===CURRENT (2026-06-13, post draft-trim): apply the DECIDED-but-UNAPPLIED SCRUTINY-DRIVER REFRAME "
"(scrutiny_reframe_DECIDED_2026_06_13). It rests on OUR OWN co-movements -> NOT blocked on any NLM/lit.=== "
"STEP 1: apply the reframe per scrutiny_reframe.change_list -> RULE-COH-5, 2.2 P5, 2.5 P4, claim-C4 + roadmap (light), + the "
"2.1-P7 'and we do not try'->'cannot' softening (LOCKED thesis_draft.tex ~L43, marked with a TODO comment -> SHOW-FIRST, "
"byte-safe). PROGRAMMATIC transfer. STEP 1b (NICE-TO-HAVE, NOT a blocker; run after/parallel): NLM re-verify matsumoto2011 "
"scope (scrutiny_reframe.NLM_GATE) -- ONLY refines the LIT framing + answers the 2.1-P2 question; if matsumoto is "
"'informative only', the reframe STILL stands on the co-movements. STEP 2: advisor cross-check the applied reframe. STEP 3: "
"RE-RATIFY 2.2 (P5) + ratify 2.5 (the last). STEP 4 (after all four ratified): write PROSE one paragraph at a time (order "
"2.2->2.5) from the ratified plans INTO thesis_draft.tex (only 2.1 is there now). DISCIPLINE: NLM sole paper authority; "
"numbers bible-verbatim; transfer programmatically; SHOW-FIRST before any .tex prose; one paragraph at a time; ignore "
"mempalace auto-recall. WRITE-TIME FLAGS live in PENDING_EDITS_unapplied.WRITE_TIME_FLAGS.")

json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(p, encoding="utf-8"))
print("resume reconciled: PENDING._note (A), NEXT_ACTION matsumoto-not-blocker (B), mission/EDITS/2.1-status/the_draft (C); re-parse OK")
