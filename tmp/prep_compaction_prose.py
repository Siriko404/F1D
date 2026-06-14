# Compaction-safety: persist the PROSE-PHASE state so post-compaction resumes cleanly.
# Critical: (1) LEDGER-FIRST workflow (do NOT push .tex yet); (2) the §2.2 P3 draft lives only in chat
# -> preserve it; (3) the recurring overclaim watch (advisor caught 3x).
import json
r = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(r, encoding="utf-8"))

d["updated"] = "2026-06-13 (PROSE PHASE, ledger-first: 2.2 P1+P2 recorded; P3 drafted/advisor-pending; .tex push deferred)"

d["where_we_are"] = ("[2026-06-13] §2 rewrite, PROSE PHASE (LEDGER-FIRST). All four plans (2.2-2.5) RATIFIED; scrutiny reframe "
    "applied+swept+cleaned. Now drafting prose into each subsection ledger's `final_prose` field -- NOT the .tex yet (user: ledger-first; "
    "the .tex push is a later phase after ALL 2.2-2.5 prose is drafted). DONE: 2.2 P1 (funnel) + P2 (H1) recorded + committed. IN FLIGHT: "
    "2.2 P3 (H1a) drafted + shown, advisor-PENDING, NOT yet recorded (draft preserved in prose_progress_2026_06_13). thesis_draft.tex is "
    "still 2.1-only.")

d["prose_progress_2026_06_13"] = {
  "_workflow_LEDGER_FIRST": ("Draft each paragraph's prose into its section2.X_paragraph_ledger.json `final_prose` (+ set prose_status + "
    "prose_gate.unlocked=true, all_supported=true). DO NOT push to thesis_draft.tex yet -- the .tex push is a SEPARATE later phase, after "
    "ALL of 2.2-2.5 is drafted into ledgers. Per-paragraph rhythm: DRAFT -> SHOW user -> (user says 'call advisor') -> advisor -> apply fixes "
    "-> RECORD into ledger via a tmp/record_2_X_pN.py script -> commit."),
  "recurring_overclaim_watch_CRITICAL": ("Advisor pattern-catch 3x this session: the prose keeps adding a causal/teleological/intensity notch "
    "the evidence does NOT carry -- (1) 'harder' [scrutiny is cash-question VOLUME, not difficulty]; (2) the §4.1 REJECTION verdict leaking "
    "into §2.5; (3) 'aimed at the share price' [bald motive vs 2.1's hedged rationale]. BEFORE recording ANY paragraph: scan for motive/intent/"
    "'why'/intensity words not backed by the ledger props; hold the descriptive register; let neutral verbs ('surfaces', 'is elevated') carry it."),
  "status": {
    "2.2 P1 (funnel)": "RECORDED in ledger (commit 6edd795).",
    "2.2 P2 (H1 run-up)": "RECORDED in ledger (commit 5381818).",
    "2.2 P3 (H1a concentration)": "DRAFTED + shown, advisor-PENDING, NOT recorded. Text in P3_draft_pending_advisor below.",
    "2.2 P4 (H1b two-clocks) + P5 (scrutiny FLAG)": "not drafted.",
    "2.3 P1-P3 / 2.4 P1-P5 / 2.5 P1-P5": "not drafted."
  },
  "P3_draft_pending_advisor": (
    "The second hypothesis sharpens the first by asking where the run-up should concentrate. H1a holds that the pre-announcement elevation "
    "is stronger for cash acquirers than for stock acquirers. The two deal types share the disclosure setting---both are material and "
    "withheld---but differ in one respect the design exploits: a cash purchase draws on an accumulated cash position, whereas a stock "
    "exchange need not. As developed in the framework, this makes the stock deal a natural placebo---the same withholding bind, minus the "
    "cash commitment---against which a cash acquirer's run-up can be read. The claim is one of concentration, not strict specificity: H1a "
    "predicts that the run-up is more pronounced in cash deals, not that it is unique to them. It concerns the run-up in language alone, not "
    "the cash accumulation that underlies the deal---H1a makes no claim that such accumulation is itself peculiar to cash acquirers. As "
    "before, no cause is asserted; the prediction locates an effect."),
  "tex_push_deferred": ("When ALL 2.2-2.5 prose is recorded in ledgers: push to thesis_draft.tex (currently 2.1-only) -- insert each "
    "\\subsection{<ledger title>} + its paragraphs' final_prose after 2.1, before the bibliography. The 2.1-P7 SOFTENING RIDES ALONG at that "
    "push: delete the L43 TODO comment + cut 'and we do not try' (keep 'Our design cannot distinguish them.'). Logic drafted in "
    "tmp/write_2_2_p1.py (P1+P7; NOT run). Compile = pdflatex x2 (manual \\thebibliography, no bibtex)."),
  "write_time_flags": ("(carried) 2.5 P4.2 prose 'tracks cash / behaves as intended' NOT bald 'valid' + 'rises AHEAD OF / quarter before' NOT "
    "'around' (0.0408**); NLM-verify NEW cites pagan1984[2.3], opler1999/bates2009/petersen2009/cameron2011[2.4], hoberg2010/'fluidity'+Hassan "
    "cite-year[2.5]; BIBLE cross-check ALL numbers (C1-C7) like Catch-3; provisional DWZ-isolation cite[2.3 P2.5]; variable_ledger L188 'persistent'.")
}

d["NEXT_ACTION"] = ("===PROSE PHASE, LEDGER-FIRST -- do NOT push .tex yet (see prose_progress_2026_06_13).=== "
    "IMMEDIATE: advisor-check the §2.2 P3 (H1a) draft (prose_progress_2026_06_13.P3_draft_pending_advisor) -> apply fixes -> RECORD into "
    "section2.2 ledger P3.final_prose (unlock gate) -> commit. THEN continue one paragraph at a time (DRAFT->SHOW->advisor->fix->RECORD->commit): "
    "2.2 P4 (H1b), P5 (scrutiny flag); then 2.3 (P1-P3), 2.4 (P1-P5), 2.5 (P1-P5). Every paragraph: verify-first (props PLANNED; numbers "
    "bible-verbatim; cites NLM-verified/callbacks), SHOW-first, and run the recurring_overclaim_watch. AFTER all 2.2-2.5 recorded -> the .tex "
    "PUSH phase (prose_progress.tex_push_deferred; includes the 2.1-P7 softening) -> compile -> advisor -> done. DISCIPLINE: NLM sole paper "
    "authority; numbers bible-verbatim; programmatic transfer; SHOW-first; ignore mempalace auto-recall.")

open(r, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(r, encoding="utf-8"))
print("resume updated: prose-phase ledger-first workflow + P3 draft preserved + overclaim watch + NEXT_ACTION.")
