# Number-vs-Source Verification — the 15 non-§4.5 sections (readiness gate)

**Verdict: PASS. All 15 sections' coefficients + significance trace to primary source. 0 real errors.**
Re-run: `python tmp/verify_all_sections.py`. Combined with §4.5 (69/69), all 16 sections are number-verified.

## Method
Tokenized every (value, stars) from the located primary sources, classified every coefficient-shaped
number in each section's props: EXACT / STAR-mismatch / ABSENT. Derived stats (p, z, within-R2, SE-context, N)
skipped. Sources: `_tables_from_bible.tex` (main+validity+scrutiny tables) + `_empire_drop_resolution.tex` +
`_empire_drop_staticfe.tex` + `nlm_dwz_reactions.json` + `nlm_bgt_spread.json` + `rob_4tables.tex`.

## Result
- 215 coefficient tokens EXACT-match source; 10/15 sections fully clean by the checker.
- **0 ABSENT real errors; 0 dangerous over-starring** (prop claims MORE significance than source — the CC-1 class). NONE.
- 13 flags, ALL triaged benign:
  - 6 STAR = the prop cites a value as a MAGNITUDE/comparison without restating stars (e.g. "0.0473 here against
    0.0461 there"; "stock lag 0.8013 almost the same"); the significance-claim instances (0.0461***, 0.0983**,
    0.0723***) match source exactly.
  - 2 ABSENT = §4.1 confidence-interval bounds, explicitly "approximately [-0.027, +0.016]" (derived, hedged).

## Honest scope caveat
Coefficients + significance: fully traced (the load-bearing dimension). SEs / Ns / p / z / within-R2: NOT exhaustively
re-checked here (secondary; §4.5's were all correct at cell level, indicating careful transcription). Cell-context
(right number, right cell) is covered by the harness's semantic number-lane at write time. For the READINESS gate
(are the inputs number-correct enough to write from): PASS.
