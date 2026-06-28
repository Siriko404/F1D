# FINAL AUDIT HARNESS -- design (REFEREE-PROOF, identify-only, never fix)

Goal: an extra-conservative, examiner-grade audit of the FINAL thesis so the author need not re-read it.
Every agent reads ONLY one self-contained flat file. Each issue is identified, evidenced (verbatim), and
given a best-fix WITH its own evidence -- but NO fix is ever applied. Output = a report complete enough to
stand alone.

## Input -- the ONE file every agent reads
`_thesis_AUDIT.tex` = `_thesis_FLAT.tex` (prose + all 21 tables + bib + appendices; compiles to the 70pp
PDF) + an AUDIT-AIDS header of LaTeX COMMENTS (don't compile) that pre-resolves everything so agents make
ZERO external calls:
- label -> "Table N" map (from the .aux), citekey -> Author(Year) map (from the bibitems),
- hand-verified COLUMN MAPS for every multi-panel table (so an agent never column-counts raw LaTeX).
Built by `_audit/build_audit_input.py` (already exists; refresh against the current FLAT).

## THE SCRUTINY MAP -- 33 aspects in 8 categories (the audit charter)
I. NUMERIC CORRECTNESS
  1 prose stat == cited table cell (value/sign/SE/p/N/R^2)   2 same quantity identical across ALL mentions
  (SDs, means, sample sizes, firm counts, reused coefs)   3 derived numbers correct (econ effects = coef/SD%,
  %-of-mean; bin drops = differences; Wald = beta_c-beta_s)   4 significance: p-level == star count == note;
  one/two-tailed applied right; "not significant" matches   5 table-internal: cols match headers, bold==sig,
  N/R^2 plausible, panel labels right
II. HONESTY / NON-OVERCLAIM (locked floor)
  6 correlational-not-causal everywhere; no slipped causal verb   7 within-firm scope; concentration-not-
  strict-specificity; mechanism-open; supportive-not-definitive   8 stock arm = noisy null (never
  "suppressed/dampened"); cash = by-product (not war-chest)   9 novelty hedged ("to our knowledge", not
  "first"); no unsupported superlatives   10 floor present in every section that needs it (post-dehedge NOT
  under-hedged); no section over-claims
III. COHERENCE / COHESION
  11 argument arc intact (motivation->hypotheses->method->results->interpretation->conclusion)
  12 abstract <-> body <-> conclusion: every abstract claim delivered; conclusion summarizes only what's shown
  13 hypothesis <-> test: every H stated is tested + verdict given; none dropped; verdicts consistent
  14 roadmap fidelity ("we do X in Section Y" -> Y does X; "three checks" -> three present)
  15 transitions/connectives sound; no non-sequitur; NO cross-section contradiction
IV. COMPLETENESS / STRUCTURE
  16 every table referenced (no orphan), every \ref resolves   17 every symbol/var/acronym defined before
  first use (UncResCEO, PRE1/2, GAP, POST, FF12...)   18 chapter/section/appendix numbering + TOC consistent;
  appendices referenced + present   19 no dangling "see Section/Table X"   20 no promised-but-missing content;
  no leftover placeholder/TODO/note-to-self
V. CITATIONS / ATTRIBUTION
  21 every \citet/\citep resolves; every bibitem cited (no orphan refs)   22 borrowed methods/claims are cited
  23 [RESIDUAL] each claim attributed to a paper matches that paper -> EXTRACT to a checklist (flat file can't
  resolve external sources)   24 reference list format + author/year internally consistent with in-text
VI. PRESENTATION / STYLE
  25 notation uniform (p-format, SE format, leading zeros, dashes, math) post Issues 2/3   26 plain-language
  register consistent; jargon explained at first use   27 terminology stable (no synonym drift per construct)
  28 tense/voice consistency; no LaTeX artifact leaking into rendered text
VII. TYPESETTING / MECHANICAL (mostly deterministic)
  29 no overfull hbox / broken math / undefined ref in compile   30 tables fit; notes standardized; no
  malformed environment
VIII. METHODOLOGICAL DEFENSIBILITY (examiner mindset)
  31 do the caveats actually cover the inferential threats? any claim stronger than the design supports?
  32 robustness coverage adequate for an examiner; any glaring omission?   33 limitations honest + complete

## ARCHITECTURE -- 4 layers: deterministic -> find -> adversarially verify -> completeness-critic -> synthesize
LAYER 0  DETERMINISTIC (scripts; 100% reliable for what they cover): orphan.py, check_coherence.py,
  destars_verify.py, floor_inventory.py + a STRENGTHENED number-provenance script (extract every prose
  number + every table cell; flag any prose number absent from every table = fabricated/mistyped). Certainty
  layer; frees agents for judgment.
LAYER 1  FINDERS (~10 parallel referees, one per dimension, each reads the audit file, agentType=Explore):
  numbers (I) | honesty-floor (II) | coherence (III) | completeness (IV) | citations+defs (V) | style/
  notation (VI) | typesetting (VII) | methodology/examiner (VIII) | abstract<->body<->conclusion alignment |
  attribution-extractor (V.23). Each emits FINDINGS {dimension, location, severity, problem, evidence[verbatim
  quotes], best_fix, fix_rationale, fix_evidence[]} AND a CLEAN-BILL list (what it checked and passed, with why).
LAYER 2  ADVERSARIAL VERIFY (>=2 independent skeptics per finding; pipeline so each finder streams into verify):
  re-derive the finding FROM THE FILE, vote real/not-real, assign confidence, and stress-test the proposed fix
  (is it correct? does it preserve the floor + every number?). CONSERVATIVE: downgrade confidence, never
  silently drop -- an audit keeps plausible flags.
LAYER 3  COMPLETENESS CRITIC (1-2 agents, LOOP-UNTIL-2-DRY): "what dimension/section/claim was NOT covered or
  NOT verified?" -> targeted re-find; repeat until two consecutive empty rounds. This is the guard for "all
  aspects I don't remember."
SYNTHESIS (me, deterministic): dedupe across layers, severity-rank, and write the report. NO fix applied.

## OUTPUT -- the AUDIT REPORT (what earns "I don't have to read it again")
1 COVERAGE MANIFEST: dimension x section grid -- who checked each cell, by what method. Proves exhaustiveness.
2 FINDINGS LEDGER: every issue + verbatim evidence + best fix + fix-evidence + confidence + severity. (Sorted;
  nothing applied.)
3 CLEAN BILLS: checked-and-passed, WITH the evidence of why -- negative results recorded, not just failures.
4 RESIDUALS: what the flat file CANNOT prove -- external-source attribution accuracy (the extracted checklist)
  + the author's own taste calls -- explicitly bounded, so the guarantee's edge is visible.

## ADVISOR-HARDENED (binding additions, 2026-06-28) -- the confidence comes from SHRINKING agent judgment
M1. NUMBERS GO DETERMINISTIC (highest-stakes; agents buckled on this twice this session). Layer 0 number
   script must: (a) for every prose number adjacent to `\ref{tab:X}`, confirm it is in THAT table, not any
   table (catches "0.0461 cited at 5.5 where 5.5 says 0.0459"); (b) RECOMPUTE every derived number
   (econ-effect coef/SD, %-of-mean, bin drops = differences, Wald = beta_c-beta_s) and compare to the prose;
   (c) RESOLVE the two check_coherence "known false positives" -- recompute, confirm, convert to clean. A
   referee-proof audit may NOT carry "trust us, ignore these." (Done preview: 0.0461/0.3010=15.3%, 0.0473/
   0.3010=15.7% -- both correct; they are cross-table econ-effect sentences, genuinely clean.)
M2. REDUNDANT FINDERS ON FATAL DIMENSIONS (false negatives are the real threat to "don't re-read"). For
   numbers, honesty-floor, and hypothesis<->test: run a SECOND independent finder (different agent, same
   file, BLIND to the first) and loop-until-2-dry. A miss never becomes a finding, so verify can't catch it
   -- only redundant independent coverage can.
F1. CLEAN BILLS MUST BE VERIFIED. "Section X clean" is itself a claim; unverified, it is worse than silence
   because the reader relaxes. Tie each clean bill to deterministic evidence; verifiers spot-check the rest.
F2. COVERAGE STRUCTURAL, NOT ASSERTED. Fan the high-stakes dimensions per-table / per-section so each
   (dimension x section) manifest cell is real work behind it, not one agent claiming the whole sweep.
F3. ABSTRACT/FRONTMATTER in the audited file -- CONFIRMED present (FLAT l.122). The section-splitter for the
   manifest MUST include the abstract (it is a \textbf{Abstract} block, not a \section) + the frontmatter.
F4. PDF-LEVEL RESIDUAL named: the audit reads .tex, so float placement (a table landing pages from its
   reference), page breaks, and visual table fit are INVISIBLE (overfull-hbox covers only part). -> one human
   glance at the rendered PDF, stated as an explicit residual beside external-attribution.
SEQ. The guarantee holds for the FROZEN audited file with NOTHING applied. Applying the surfaced fixes
   RE-OPENS the audit (every fix can introduce a new error -- shown repeatedly this session). After fixes
   land: re-run Layer 0 + re-audit the touched sections. "Never read again" = the version that exits the
   audit clean with nothing applied after it.

## THE GUARANTEE (honest, not hand-wavy)
100% of the thesis's INTERNAL properties (every aspect above except V.23) are checked AND double-verified AND
deterministically backstopped where possible. The ONE thing this harness cannot close from a flat file is
whether a claim matches its EXTERNAL source paper -- that is extracted into a checklist and verified
separately (small, bounded). Within that explicit boundary: airtight.
