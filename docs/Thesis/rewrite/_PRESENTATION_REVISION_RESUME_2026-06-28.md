# Thesis presentation revision — RESUME (2026-06-28)

Three Sina-flagged presentation issues to fix in a FRESH session (this session's context was
near-full; large prose rewrites under context pressure introduced errors twice — do not repeat).

## CURRENT STATE (what's done, where things live)
- Live thesis = `docs/Thesis/_uottawa_rewrite/` (a CLONE; the docs/Thesis originals are untouched).
- ONE source of truth that regenerates the whole clone + compiles:
  `docs/Thesis/rewrite/_phase5_harness/build_uottawa_rewrite.py`
  - Reads `phaseB_result.json` (the audited plain-language prose, the LOCKED prose source).
  - Splices §2, regenerates `_abstract_body/_intro_body/_conclusion_body/sec34_body_from_ledgers`,
    builds `_robustness_tables.tex`, patches the bib + the dwz note, compiles `thesis_uottawa_rev2.pdf`.
  - Per-section prose tweaks are done as small assert-guarded TRANSFORMS in this file
    (`normalize`, `repoint_45`, `augment_25`, `fix_21`, `fix_34`, `drop_thesis_panel`). Add new
    transforms the same way — keep `phaseB_result.json` pristine.
- CURRENT PDF = ONLY `thesis_uottawa_rev2.pdf` (70pp). `thesis_draft_uottawa.pdf` and
  `thesis_uottawa_rev.pdf` in the clone are STALE (frozen pre-fixes by viewer locks) -- do NOT open
  them. The `_rev` name bumps because each opened PDF stays viewer-locked; once Sina closes all
  viewers, set `JOB="thesis_draft_uottawa"` in the generator and rebuild to mint the canonical name.
- Recent commits: 11acaf85 (panel fixes), then the advisor-correction commit, then the
  Thesis-panel-drop commit. Coherence panel (numbers/story/register) already PASSED; honesty floor holds.
- Tables: 21 total. 5.2-5.14 from `_tables_from_bible.tex`; 5.15-5.20 = §4.5 robustness
  (`_robustness_tables.tex`, all-deals-only after the panel drop) + logits; 5.21 = `_dwz_replication.tex`.

## VERIFICATION GATES (run after EVERY change; non-negotiable)
1. `python build_uottawa_rewrite.py` -> "PDF OK: pages=70 undefined-ref/cite=0 overfull-hbox=0".
2. orphan check (`docs/Thesis/rewrite/_phase5_harness/_audit/orphan.py`) -> 0/21 orphaned, no broken refs.
3. number check (`docs/Thesis/rewrite/_phase5_harness/_audit/check_coherence.py`) -> no new desync (2 known false positives ok).
   (also in `_audit/`: `flatten.py` = one-file flattener; `build_audit_input.py` = panel-input builder.)
4. For prose edits: re-derive every number/claim from the TABLE CELL (mechanical checks CANNOT catch
   claim-vs-table errors — that is how the §2.5 errors slipped). Re-run the register agent on the
   flat file to confirm the honesty floor still holds. Advisor before commit.

## ISSUE 1 — over-hedging (thin the register-lock repetition)
- Evidence: results prose (sec34) alone repeats the floor ~15x (correlational x4, mechanism x3,
  identification x3, strict-specificity x2, no-cause/no-causal...); more in §2/§5.
- REQUIREMENT: keep the honesty floor (the panel verified it holds) but state each element a SENSIBLE
  number of times, not in nearly every paragraph. Load-bearing homes to KEEP: the §2 framing
  statement, each hypothesis's one caveat, the §3.4 cash-specificity caveat, the §4.1 scrutiny
  rule-out caveat, the §5 limitations paragraph. CUT the per-paragraph "the design is correlational
  and identifies no cause" tails that close MA1/MA2/MA3/robustness paragraphs redundantly.
- APPROACH: section by section; for each, list every floor-mention, keep the first/load-bearing,
  delete the redundant closers (they add nothing once stated). Do NOT weaken or remove the floor
  where it is the only statement in that section.
- CAUTION: the register agent must re-confirm the floor still holds after thinning (don't over-cut).

## ISSUE 2 — [DONE 2026-06-28, commit c084ed52] coefficients: stars -> compact p (PROSE ONLY)
> RESOLVED: Sina chose COMPACT (`$0.0461$ (standard error $0.0172$, $p<.01$)`), NOT worded "significant at
> the N percent level" (he viewed a worded MA1 sample and judged compact neater) and NOT bare `$p<.01$`.
> Done via `destars()` in build_uottawa_rewrite.py: a regex copies value+SE verbatim, computes only
> star->threshold (*** $p<.01$, ** $p<.05$, * $p<.10$); two no-SE forms get asserted bespoke handling;
> exact-p coefs (logits, Wald) just lose the star. Verified: `_audit/destars_verify.py` PASS + full
> end-to-end read of sec34 + 2.5 splice. PROSE ONLY -- tables keep stars. The notes below are superseded.

## ISSUE 2 (original spec, superseded) — stars -> p-values + economic effect
- Evidence: phaseB prose states coefs as `$0.0461^{***}$ (standard error $0.0172$)` (stars).
  Inline stars in PROSE are non-standard; the ORIGINAL prose used p-values + an economic-magnitude
  reading. TEMPLATE LOCATION UNVERIFIED -- the grep for the old p-value style returned empty this
  session, and the SRC sec34 may already be the stars version. CONFIRM the template in git history
  (a pre-phaseB commit) or the original pre-rewrite files before trusting it; the old §2.5 used
  "coefficient 0.0001, $p<0.01$ ... about 5% of a SD" (p-value + economic effect), which is the goal.
- REQUIREMENT (per headline coefficient, in PROSE):
  (a) drop the inline stars; state the p-level: `***`->`$p<.01$`, `**`->`$p<.05$`, `*`->`$p<.10$`;
      use the EXACT p where the prose/tables already give it (run-up two-tailed $p=0.0074$;
      Wald first-deal $p=.039$ / all-deals $p\approx.013$; Logit A $p=.0011$/$.0008$; Logit B
      $p=.030$/$.028$/FE $p=.205$; convergent US-EPU/GEPU marginal).
  (b) state the ECONOMIC EFFECT for each load-bearing coef (SD-fraction or %-of-mean). Many are
      already present (run-up "~15.3% of a residual SD"; cash "~3% of mean"); add where missing.
- OPEN DECISION (ask Sina): does this apply to the PROSE only, or also the TABLE bodies? Tables
  conventionally keep stars + a significance note (standard); recommend PROSE -> p-values, TABLES
  keep stars (note explains them). Default to prose-only unless Sina says otherwise.
- APPROACH: section by section; for each coef, verify the value+significance against its table cell,
  then rewrite "X^{stars} (SE Y)" -> "X ($p<...$; SE Y), about Z% of a SD". Biggest change — go slow,
  one section per verify/commit. This is exactly where claim-vs-table errors hide.

## ISSUE 3 — standardize the table notes
- Evidence: notes vary ("Summary statistics for the main estimation sample..." / "Pre-announcement
  run-up test." / "Disclosure-window event study on the matched universe..."), with inconsistent
  FE / SE / significance disclosure.
- REQUIREMENT: ONE template for every table's `\textit{Notes:}`, e.g.:
  "Notes: [one-line what the table shows]. [sample + 2002--2018]. [FE: firm + calendar year-quarter].
   Standard errors clustered by firm, in parentheses. $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$
   (two-tailed)." Keep table-specific facts (e.g., one-tailed convergent tests, matched-universe N)
   but in a consistent order/wording. If Issue 2 converts table stars too, drop the star legend.
- FILES: `_tables_from_bible.tex`, `_robustness_tables.tex`, `_dwz_replication.tex` (clone copies;
  or patch in the generator after the clone step, like the existing dwz-note patch).
- CAUTION: edit ONLY the notes; never a number/cell.

## RECOMMENDED EXECUTION ORDER
1. [x] Issue 2 -- DONE (commit c084ed52). Compact p, prose only, verified end-to-end.
2. [x] Issue 3 -- DONE (commit 3d3bc11e). All 21 table notes standardized to one template + DWZ (5.21)
       bolded to match the other 20; bold-consistency verified both directions; data rows untouched
       (bible/robustness), DWZ values byte-identical (only \textbf added). Notes only, originals untouched.
3. [ ] Issue 1 last (thin hedges) -> register-agent re-check the floor still holds.
4. [ ] Final: re-run the 3-agent coherence panel on the flat file; advisor; set canonical JOB name.

## GATE before Issue 1 / the final panel (advisor-flagged 2026-06-28)
`_thesis_FLAT.tex` is a DERIVED flatten, NOT regenerated by build_uottawa_rewrite.py. The panel input
builder (`_audit/build_audit_input.py`) + manual reads consume it. ALWAYS re-run `python _audit/flatten.py`
after any build before trusting FLAT or running the panel, or it audits a stale (pre-edit) thesis.
(coherence.py + orphan.py read the fresh clone files, so they are safe; only FLAT-consumers need this.)
FLAT was refreshed at the Issue-3 commit, so it is current as of 3d3bc11e.
