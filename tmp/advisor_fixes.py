# Advisor cross-coherence fixes (programmatic):
#  #3 (2.5 P3): separate time-variation (FE-absorption, P3.3) from content-location (known/disclosable, P3.2) -- no fusion, drop 'standing'.
#  #2 (2.3 P4): honest-threats 'trio' -> 'pair' (FirmChars cut).
#  #4 (resume BLOCKER): mark all decided edits APPLIED; keep only write-time flags. (#1 keown cut verified clean via 2.1 P6 prose.)
import json

def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    json.load(open(p, encoding="utf-8"))

def prop(par, pid):
    for x in par["propositions"]:
        if x["prop_id"] == pid: return x
    raise KeyError(pid)

# ---------- #3: 2.5 P3 -- de-fuse time-variation from content-location ----------
p5 = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
d5 = load(p5); P5 = d5["paragraphs"]
P5["P3"]["intent"] = ("Lead with the decisive validity result: product-market competition -- a KNOWN, disclosable business "
    "condition -- surfaces in the scripted presentation (UncPre), not in the call-varying residual the design uses.")
p3_2 = prop(P5["P3"], "P3.2")
p3_2["statement"] = ("This is the cleanest validity evidence and leads the validity story: product-market competition is a "
    "KNOWN, disclosable business condition a firm addresses in its prepared, scripted remarks, so it loads on presentation "
    "uncertainty (UncPre); the call-varying residual is reserved for the unscripted, deal-specific signal. The locus turns on "
    "competition being DISCLOSABLE-IN-ADVANCE (scriptable) -- NOT on persistence (it is in fact time-varying firm-year, which "
    "does a separate job in P3.3).")
p3_2["verification_plan"] = ("Framing; C3 = cleanest. F1 REFRAME (advisor #3): the presentation-locus rests ONLY on competition "
    "being KNOWN/DISCLOSABLE-IN-ADVANCE (scriptable). Do NOT justify the locus by time-variation -- non-sequitur (time-variation "
    "would push TOWARD the call-varying residual); time-variation's only job is the FE-absorption rebuttal (P3.3). Avoid "
    "'standing'/'persistent'. The 'why' = ONE hedged clause; the claim rides the regression result. Write-time pass.")
# rebuild the F1-REFRAME guardrail (index 2) to forbid the fusion + drop 'standing'
P5["P3"]["guardrails"][2] = ("F1 REFRAME (advisor #3): NEVER call competition 'persistent' (contradicts verified time-varying "
    "TNIC). CONTENT-LOCATION rests ONLY on competition being KNOWN/DISCLOSABLE-IN-ADVANCE (scriptable -> prepared remarks); do "
    "NOT use 'standing'. Time-variation does a SEPARATE job (P3.3: firm FE cannot absorb it) -- do NOT fuse them: 'in the "
    "presentation because time-varying' is a non-sequitur (time-variation would push toward the call-varying residual). The "
    "discriminant CLAIM rides the regression result; the 'why' = ONE hedged clause.")
save(p5, d5)

# ---------- #2: 2.3 P4.serves trio -> pair ----------
p3 = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
d3 = load(p3)
d3["paragraphs"]["P4"]["serves"] = "Closes the honest-threats pair (UncPre over-control + generated-regressand); hands validity to 2.5."
save(p3, d3)

# ---------- #4: resume -- mark APPLIED; keep only write-time flags ----------
pr = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = load(pr)
d["updated"] = "2026-06-13 (ALL decided edits APPLIED across 2.2/2.3/2.5; advisor cross-coherence clean; plans FINAL, ratification-ready)"
d["where_we_are"] = ("[2026-06-13] 2.1 COMPLETE (in thesis_draft.tex). 2.2/2.3/2.4/2.5 PLAN LEDGERS NOW FINAL + "
    "ADVISOR-CROSS-CHECKED -- every decided edit APPLIED this session (not merely planned). Yardstick defs NLM-verified "
    "(hassan2020/baker2016/hoberg2016 LOCKED, davis2016 provisional). The 2.5 'persistent industry trait' error was reframed to "
    "CONTENT-LOCATION (rests on disclosable-in-advance, NOT on time-variation -- those do separate jobs); 2.2/2.3 wording fixes "
    "applied (involuntary/thewissen/keown; FirmChars cut + suggestive retone). Ratification-ready. NOTHING in prose yet (prose "
    "BLOCKED, gated behind ratification).")
d["EDITS_APPLIED_2026_06_13"] = {
  "_what": "The decided PENDING edits, APPLIED to the ledgers this session (programmatically: tmp/revise_2_2.py, revise_2_3.py, revise_2_5.py, advisor_fixes.py). Recorded so a future compaction does NOT re-apply them.",
  "2.2": "P2.2 thewissen -> one-clause callback (15% dropped); P2.3 'involuntary' dropped (aligns 2.1 P7); P4.2 keown CUT + P4.3->P4.2 renumber (price-vs-language distinction confirmed carried in 2.1 P6 prose).",
  "2.3": "P3.2 FirmChars 'bad-control' CUT (we adopt DWZ's spec) + P3.3->P3.2 renumber; P3.1 UncPre + P4.1 generated-regressand RETONED suggestive; honest-threats trio->pair. keown1981 dropped from 2.3.",
  "2.5": "F1 content-location reframe (killed 'persistent'); folded the 4 NLM-verified yardstick defs (papers + P2/P3 plans); F3 time-varying strengthening (P3.3); F4 convergent identification basis (P2); foregrounded CashScrutiny (P4). Advisor #3: time-variation SEPARATED from content-location (P3.2/intent/guardrail) -- no fusion.",
  "2.4": "No edits -- already advisor-clean (P5.5 selection disclosure; P1.3 within-firm).",
  "advisor_cross_coherence": "CLEAN: keown cut safe (2.1 P6 prose carries language-vs-price, L1731/L1798); time-variation/content-location de-fused; trio->pair; C3->2.3 P3.1 and R3->2.3 P4.1 still homed (FirmChars/keown are not C/R items)."
}
d["PENDING_EDITS_unapplied"] = {
  "_note": "The 2.2/2.3/2.5 ledger edits were ALL APPLIED 2026-06-13 (see EDITS_APPLIED_2026_06_13). Only WRITE-TIME flags remain -- resolve during prose, post-ratification, NOT now.",
  "WRITE_TIME_FLAGS": [
    "F2: hoberg2010 + the word 'fluidity' -> NLM-verify at write-time; our competition var is z_log_TotalSimilarity = total similarity = hoberg2016, NOT fluidity. Do not assert-drop from memory.",
    "F5: Hassan cite year -- variable_ledger says 'Hassan et al. 2019' (WP) vs QJE 2020; reconcile vs the .bib.",
    "F1-leak: the 'persistent industry condition' defect also sits in variable_ledger.json L188 (role_in_thesis) -> fix when prose draws from it.",
    "Owed NLM cites (verify at write-time, post-ratification upload): pagan1984 (2.3); opler1999/bates2009/petersen2009/cameron2011 (2.4).",
    "Bible cross-check C3/C4/C5 numbers vs _tables_from_bible.tex at write-time. R-class: two-way clustering (R2). drop-FirmChars is now a robustness column, not a 2.3 threat."
  ]
}
d["NEXT_ACTION"] = ("===CURRENT (2026-06-13): ALL FOUR §2 PLAN LEDGERS FINAL + ADVISOR-CROSS-CHECKED.=== 2.1 COMPLETE. "
    "2.2/2.3/2.4/2.5 plans now FINAL -- every decided edit APPLIED (see EDITS_APPLIED_2026_06_13). STEP NEXT = USER RATIFICATION "
    "of all four ledgers (2.2-2.5) per the ratification ceremony (atomic per-section AskUserQuestion: 'Approve as written' / "
    "'Amend'). THEN (post-ratification, ONE PARAGRAPH AT A TIME, order 2.2->2.5, per paragraph_workflow.json): verify props -> "
    "draft prose -> accuracy-pass uncited claims -> advisor -> show user -> record final_prose + unlock prose_gate. WRITE-TIME "
    "FLAGS in PENDING_EDITS_unapplied.WRITE_TIME_FLAGS (F2/F5/F1-leak/owed-NLM/bible-cross-check/R2). DISCIPLINE: no prose before "
    "ratification; transfer to ledgers PROGRAMMATICALLY.")
save(pr, d)

print("advisor fixes applied: 2.5 P3 de-fused (#3), 2.3 P4 trio->pair (#2), resume marked APPLIED + write-time flags (#4); all re-parsed OK")
