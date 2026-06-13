# Compaction-prep: rewrite the resume's live-state fields to the CORRECTED truth + the DECIDED-but-
# UNAPPLIED scrutiny-driver reframe. Additive/overwrite of named keys only (preserves the rest).
import json
p = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(p, encoding="utf-8"))

d["updated"] = ("2026-06-13 (CONTEXT-RESET prep: draft-state clarified -- only 2.1 locked, thesis_draft.tex TRIMMED to "
    "2.1-only; SCRUTINY-DRIVER reframe DECIDED but UNAPPLIED; matsumoto NLM gate pending)")

d["where_we_are"] = (
"[2026-06-13] We are REWRITING THE DRAFT FROM SCRATCH. ONLY 2.1 (Conceptual Framework) is LOCKED -- it lives in "
"docs/Thesis/thesis_draft.tex, now TRIMMED to 2.1-only (117 lines): abstract, intro, the STALE 2.2-2.5, sections 3/4/5, "
"and the appendices were REMOVED this session (pure deletion, 2.1+bib byte-identical; fully reversible via commit 81efc78 "
"which holds the complete prior draft). 2.2-2.5 are a FROM-SCRATCH rewrite, PLANNED in the per-subsection ledgers "
"(docs/Thesis/rewrite/section2.{2,3,4,5}_paragraph_ledger.json), NOT yet prose. Earlier this session (all COMMITTED): "
"applied every decided edit to the 2.2-2.5 PLANS (yardstick audit F1-F5; 2.3 P3 UncPre 'over-control' threat CUT -> folded "
"POSITIVE into 2.3 P2.5; etc.) and RATIFIED the 2.2/2.3/2.4 plans. THEN a MAJOR reframe emerged (scrutiny_reframe_DECIDED_2026_06_13) "
"that is DECIDED + advisor-validated on the change-list but NOT YET APPLIED; it re-opens 2.2 + 2.5 plans + needs a tiny 2.1-P7 "
"prose touch. 2.5 ratification is PAUSED pending that reframe.")

d["scrutiny_reframe_DECIDED_2026_06_13"] = {
  "_what": "MAJOR framing correction (user, emphatic, evidence-grounded). DECIDED + advisor-validated on the change-list; NOT yet applied to any doc. Apply BEFORE finishing 2.5 ratification. Transfer PROGRAMMATICALLY.",
  "the_reframe": ("Cash scrutiny is a PLAUSIBLE ALTERNATIVE DRIVER of the residual run-up -- an identification threat we CONSIDERED, "
    "TESTED, and REJECTED -- NOT a 'confound we pre-empt'. Plausibility is grounded in TWO of our OWN verified results: it rises WITH "
    "cash (CashRatio->CashScrutiny 0.7530***/0.8519***) AND rises PRE-ANNOUNCEMENT (HighCashScrutiny 0.0408**), so it could mechanically "
    "generate the run-up = textbook identification test -> tested -> rejected (CashScrutiny->UncRes ~ -0.0000 n.s.; PreAnnounceQtr x "
    "scrutiny -0.0056 n.s.). Still RULE-COH-5-clean (rule-out != mechanism; no WHY-it's-inert claimed)."),
  "identification_3_levels_the_dont_try_fix": ("Level 1 MAIN effect (deal->uncertainty causal ID): NO -- descriptive, DECIDED "
    "(thin_claim_ceiling), do NOT soften. Level 2 SCRUTINY alternative: we DO test + reject (lit-grounded) = the reframe (2.2/2.5). "
    "Level 3 TWO READINGS (compliance vs strategic silence): genuinely observationally-equivalent/UNIDENTIFIABLE -> 'cannot separate', "
    "NOT 'we do not try'. The blanket 'no identification' wrongly collapsed L2 (real test) + L3 (unidentifiable) into L1."),
  "change_list": {
    "RULE-COH-5 (tmp/section2_subsection_plan.json + the COH-5 strings in 2.2 ledger L306 + 2.5 ledger L30)": "'scrutiny = CONFOUND' -> 'scrutiny = PLAUSIBLE ALTERNATIVE DRIVER (identification threat, motivated by rise-with-cash + rise-pre-announce), tested & rejected in 4.1; not a P7 reading; rule-out != mechanism'.",
    "2.2 P5.1": "ADD the motivation (plausible BECAUSE rises with cash AND pre-announce -> could mechanically generate the run-up).",
    "2.2 P5.2 / P5 intent / thin_claim / serves": "'confound...rules out' -> 'plausible alternative driver -> identification test: considered -> tested -> rejected'.",
    "2.5 P4 (intent, P4.2, P4.3) + _governing.section_job": "LEAD with the plausibility (rises with cash 0.7530*** + pre-announce 0.0408**) as WHY it's a credible driver, THEN test -> reject. (foreground-CashScrutiny already in P4.1/intent.)",
    "claim_findings_ledger C4 (id C4_scrutiny_ruleout) + roadmap section2.5 Must-do 4": "LIGHT: 'alternative rule-out' -> 'plausible alternative driver, tested & rejected' (numbers + hedge UNCHANGED).",
    "section2.1 P7 (thesis_draft.tex ~L67, LOCKED prose)": "'Our design cannot distinguish them, and we do not try.' -> keep 'cannot distinguish', soften/cut 'and we do not try' (the two readings are genuinely unidentifiable). Main-effect 'We identify no causal channel...descriptive throughout' STAYS. EDITS LOCKED .tex -> SHOW-FIRST + careful + byte-safe."
  },
  "KEEP_VERBATIM_do_not_touch": "C4 hedge ('does not account for THIS run-up; not that scrutiny never matters') + the underpowered caveat (CI [-0.027,+0.016]; 89% of calls draw no scrutiny); RULE-COH-8 (CashScrutiny VOLUME != UncQue wording); 'rule-out != mechanism'; Level-1 main-effect no-causal-ID (DECIDED); all numbers (bible-verbatim).",
  "NLM_GATE": ("RE-VERIFY matsumoto2011 scope via a scoped nlm_common query (pattern = tmp/nlm_dwz_uncpre.py; matsumoto nlm_source_id "
    "a1dacc9f-2bee-46ba-9261-496fd687c8e6): does it support 'analyst questioning -> managerial HEDGING/uncertainty', or ONLY 'Q&A is "
    "informative'? Gates (a) whether matsumoto can anchor the scrutiny-driver plausibility in LIT (vs only our own co-movements), and "
    "(b) the 2.1-P2 question -- should P2's matsumoto ALSO seed the scrutiny rival? If matsumoto is only 'informative' -> keep the "
    "plausibility grounded in our co-movements and consider a NEW analyst-scrutiny->disclosure cite (NLM upload + verify). NLM auth "
    "expires -- user runs `! notebooklm login` if needed."),
  "advisor_status": "Change-list advisor-validated this session. RE-ADVISOR the APPLIED reframe before re-ratifying 2.2/2.5."
}

d["ratification_progress_2026_06_13"] = {
  "_note": "These ratify the LEDGER PLANS for the FROM-SCRATCH 2.2-2.5 rewrite (the stale .tex versions are GONE). Still valid -- BUT 2.2 + 2.5 plans must get the scrutiny-driver reframe applied, then RE-RATIFY those two. Stamp each at approval (not batched).",
  "2.2": "RATIFIED -- but RE-RATIFY after the scrutiny-driver reframe lands on P5.",
  "2.3": "RATIFIED (incl. the UncPre over-control P3 CUT -> folded positive into P2.5; P4 generated-regressand -> P3).",
  "2.4": "RATIFIED.",
  "2.5": "PENDING (paused) -- the scrutiny-driver reframe must land on P4 FIRST, then ratify. THE LAST subsection."
}

d["NEXT_ACTION"] = (
"===CURRENT (2026-06-13, post draft-trim): apply the DECIDED-but-UNAPPLIED SCRUTINY-DRIVER REFRAME (see "
"scrutiny_reframe_DECIDED_2026_06_13).=== STEP 1: NLM re-verify matsumoto2011 scope (the lit anchor; scrutiny_reframe.NLM_GATE) "
"-- scoped nlm_common query a la tmp/nlm_dwz_uncpre.py. STEP 2: apply the reframe per scrutiny_reframe.change_list -> RULE-COH-5, "
"2.2 P5, 2.5 P4, claim-C4 + roadmap (light), + the 2.1-P7 'and we do not try'->'cannot' softening (LOCKED thesis_draft.tex -> "
"SHOW-FIRST, byte-safe). PROGRAMMATIC transfer. STEP 3: advisor cross-check the applied reframe. STEP 4: RE-RATIFY 2.2 (P5) + "
"ratify 2.5 (the last). STEP 5 (after all four ratified): write PROSE one paragraph at a time (order 2.2->2.5) from the ratified "
"plans INTO thesis_draft.tex (only 2.1 is there now). DISCIPLINE: NLM sole paper authority; numbers bible-verbatim; transfer "
"programmatically; SHOW-FIRST before any .tex prose; one paragraph at a time; ignore mempalace auto-recall. WRITE-TIME FLAGS live "
"in PENDING_EDITS_unapplied.WRITE_TIME_FLAGS (F2 hoberg2010/fluidity, F5 Hassan year, MNPI-expansion, cash-persists-mechanical, "
"owed NLM cites pagan/opler/bates/petersen/cameron, bible cross-check C3/C4/C5, R2).")

json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(p, encoding="utf-8"))  # validate
print("resume updated for compaction: draft_state + scrutiny_reframe_DECIDED + ratification_progress + NEXT_ACTION; re-parse OK")
