# Issue 1 -- de-hedge plan (VERY SENSITIVE; honesty floor must survive intact)

Goal: thin the redundant honesty-floor repetition WITHOUT weakening the floor. Conservative -- under-cut
beats over-cut. Cuts go in the generator as assert-guarded transforms (phaseB_result.json stays pristine).

## Floor elements (locked) + thesis-wide counts (from `_audit/floor_inventory.py --counts`, FLAT @ 51e11bfa)
CORR 17 | NOCAUSE 20 | WITHIN 12 | MECH 13 | SUPP 10 | CONC 19 | POWER 6 | NULL 2 | BYPROD 1   (~100 total)

## Method
- KEEP-UNTOUCHED (load-bearing homes): Introduction, Conceptual Framework (2.1), Hypothesis Development
  (2.2), Methodology (2.4), Specification (2.5), Conclusion (5 -- the FORMAL limitations disclosure).
- THIN only the RESULTS (MA1/MA2/MA3, 4.1-4.5): drop/shorten the per-paragraph CLOSERS that repeat an
  element already stated in that section. Prefer SHORTEN (strip the redundant element, keep any element
  unique to that sentence) over DELETE.
- Filter false positives by hand: e.g. MA1 "concentrated in a single quarter" (CONC tag) and 4.4
  "within-firm transformation" (WITHIN tag) are SUBSTANCE, not floor hedges -- do NOT touch.
- Never weaken a retained hedge, never alter a number, never touch a table.

## ONE-TIER invariant (the deterministic safety gate)  [advisor: simpler + safer than two-tier]
Re-run `floor_inventory.py --counts` after thinning, diff vs the @51e11bfa baseline:
- NO section may drop to zero ANY element it carried. Hard stop. Achieved by SHORTEN/MERGE, never a
  to-zero delete -- so the two-tier carve-out is unnecessary.
Plus:
- Math-untouched guard: every cut/shorten touches ZERO `$...$` spans -- cheap proof no number moved
  (complements `destars_verify`, which must still PASS).
- Register agent (blind, fresh FLAT) is given the LOCKED ELEMENT LIST and confirms, PER thinned section,
  WHICH elements are present (element-specific checklist, NOT a "reads-hedged?" vibe-check).
- advisor; compile 70pp 0/0; orphan 0/21; coherence no new desync.

## CUT-LIST (everything not listed = KEEP verbatim)
MA1 (keep CORR/NOCAUSE/WITHIN/SUPP/NULL >=1):
- CUT  "Because each firm is compared with itself, the pattern is within-firm; it remains correlational and
        does not identify a cause."   (CORR/NOCAUSE/WITHIN all still in the two prior sentences)
- SHORTEN "These magnitudes are supportive but not definitive, and they do not establish a cause."
        -> "These magnitudes are supportive but not definitive."   (keep SUPP; NOCAUSE already 2x above)

MA2 (keep CORR/NOCAUSE/WITHIN/MECH/SUPP >=1):
- SHORTEN "Throughout, firms are compared with themselves, the design is correlational, and it does not
        identify a cause." -> "Throughout, firms are compared with themselves."   (keep the section's only
        WITHIN; CORR/NOCAUSE remain in the primary + the closer)
- CUT  "This remains a correlational reading, not a causal one."   (pure CORR/NOCAUSE dup)
- KEEP the 4-element closer (carries MA2's only MECH + SUPP).

MA3 (cash-specificity -- LOAD-BEARING; NO cuts):
- KEEP "We leave that mechanism open."  [advisor: "open" = undetermined STANCE != "not established by
        these tests" = epistemic; mechanism-OPEN is the locked element and 3.4 is its home. The count
        invariant is blind to this distinction, so DO NOT cut.] Everything in MA3 stays.

### Section 4 -- DEPTH CHOICE for Sina (he said sec 4 has "a lot ... exhaustively")
All §4 changes below are SHORTEN/MERGE (never-to-zero safe). Two depths:
- CONSERVATIVE = 4.3 + 4.5 only.
- DEEPER (recommended, matches "a lot") = 4.1 + 4.3 + 4.4 + 4.5 -- removes every cross-section boilerplate echo.

4.1 Scrutiny: SHORTEN the 4-element closer "The reading is correlational and supportive, not definitive; it
   identifies no cause, and the mechanism remains open." -> drop "correlational and" (CORR is in the
   within-firm sentence above); SUPP/NOCAUSE/MECH are unique here and STAY.   [DEEPER only]
4.2 Bid-ask: KEEP both (each is the section's sole caveat).
4.3 Withdrawal: SHORTEN "The reading is correlational and supportive rather than definitive." ->
   "The reading is supportive rather than definitive."   (CORR in "This is a correlational concern..." above).
4.4 Dynamic-term: MERGE the two near-duplicate closers -- "This is a robustness check and is supportive
   rather than definitive." + "The reading is correlational and supportive rather than definitive." -> ONE
   sentence, e.g. "This is a correlational robustness check, supportive rather than definitive." (removes the
   doubled "supportive rather than definitive"; CORR+SUPP both stay).   [DEEPER only]
4.5 First-deal: SHORTEN "The design stays correlational and identifies no causal effect, and we read it as
   concentration in cash deals, not strict specificity." -> "The design stays correlational."  (the echoed
   concentration/no-cause is already in the prior sentence; CORR stays).

Net (DEEPER): ~2 deletes (MA1, MA2) + ~6 shortens/merge. Removes the repeated "correlational and supportive,
not definitive; identifies no cause; mechanism open" cross-section echo wherever it only repeats; keeps it
wherever it is a section's only home for an element; never touches the conclusion's formal disclosure.

## Execution order (next session/turn)
1. Add `dehedge()` transform (per-section asserted .replace) to build_uottawa_rewrite.py; phaseB pristine.
2. Run generator; regenerate FLAT (`flatten.py`).
3. `floor_inventory.py --counts` diff vs baseline -> enforce the two-tier invariant (script-checked).
4. register agent (blind) on the fresh FLAT -> floor holds in every section.
5. compile 70pp 0/0; destars_verify PASS; orphan 0/21; coherence no new desync.
6. advisor; then commit.
