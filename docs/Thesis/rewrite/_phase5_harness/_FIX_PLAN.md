# FIX PLAN — all audit findings (cheapest safe path). Status 2026-06-28.

Mechanism = generator transforms (like Issues 1-3 / H1), NEVER hand-edit the clone or phaseB.
Verify after EVERY batch: generator prints "PDF OK pages=70 0/0"; floor_inventory unchanged; number_audit clean.
HIGH H1 = DONE (6b378581/2cf3fb40). Everything below is open.

## GROUP A — CHEAP, MECHANICAL, NO DECISION (auto via transforms)

| ID | what | exact fix | where |
|----|------|-----------|-------|
| H2-cap | "placebo" mislabels the managed stock arm | rendered "placebo" -> "managed comparison"/"comparison" in table notes/captions/headers (5.2 note+header, 5.4, 5.17). Labels tab:*_placebo stay (internal). | _tables_from_bible patch + generator ROB_NOTE/ADHEAD/caption for rob_timing_placebo |
| H2-prose | Wald gap not flagged as upper bound | add ONE sentence to 3.4: stock-tone management biases beta_s negative, so the cash-minus-stock gap is an upper bound | phaseB 3.4 transform |
| 4/11/16/18n | 3.2 calls Table 5.2 "one-tailed"; table is two-tailed (verified t=2.68 -> p=.0074 two-tailed, note says two-tailed) | reword 3.2: drop the false "one-tailed convention" worry; state plainly the coef is significant two-tailed (p=.0074) as Table 5.2 reports | phaseB 3.2 transform |
| 7 | causal verb in 4.1 gloss ("the reason for the deal raises uncertainty"); "amplify" | -> "in the pre-announcement quarter uncertainty is higher, the questioning is not, and does not interact with it"; intro "amplify"->"interact" | phaseB 4.1 + 1 transform |
| 9 | "unmanaged" stated flat (2.1 l.179, 2.2 H1 l.187) vs hedged "relatively unmanaged" elsewhere | both -> "relatively unmanaged" / "less-managed" | phaseB 2.1 + 2.2 transform |
| 12/25 | whole-unit "Section~N" but \chapter renders "Chapter N" | regex Section~([1-5]) NOT followed by .digit -> Chapter~\1 (keeps Section~N.M). Sweep all prose. | normalize-level transform |
| 14 | "$p = 0.0074$" (only leading-zero p) | -> "$p=.0074$" | phaseB 2.4 transform |
| 15 | spaced " -- " in Ch2 vs em-dash "---" in body | " -- " -> "---" (spaced only; ranges "--" untouched) | phaseB 2.x transform (idempotent doc-wide) |
| 18s | prose SEs 5dp ($0.00275$, $0.05076$) vs tables (0.0027, 0.0508) | match table cells: 0.00275->0.0027, 0.05076->0.0508 | phaseB 4.5 transform |
| 10 | "Dzielin\'ski" (mis-placed accent) vs plain "Dzielinski" in bib+intext | -> plain "Dzielinski" in Table 5.21 caption (l.11) + notes (l.55) | _dwz_replication patch |
| 16t/22 | event rows "$t{-}1$"/"$t{-}2$" overload t (calendar idx) | -> "$e{=}{-}1$"/"$e{=}{-}2$" (8 rows) | _tables_from_bible patch |
| 2 | Table 5.12 bid-ask coefs irreconcilable w/ summary stats | add to 5.12 note: "DV (spread) rescaled by $10^4$ (basis points)" — factor CONFIRMED 1e4 | h14c table-note patch |
| 11 | references not alphabetical (3 runs) | rebuild \thebibliography: parse 22 bibitems, sort by first-author, re-emit | wrapper transform (read bib at exec) |

## GROUP B — NEEDS A DECISION (open questions for Sina)

| ID | issue | option A (cheap) | option B (stronger/more work) |
|----|-------|------------------|-------------------------------|
| 1 | FirmMat/EarnVol/HighCash-cutoff/5.12-controls undefined; Table 5.1 says "all defined" | add brief defs to Appendix II (defs in hand: EarnVol=rolling SD of qtrly earnings/assets; FirmMat=lifecycle from age+sales-growth+capital-structure) | drop the vars from the secondary tables |
| 8 | "rule out"/"Ruling Out" title overclaims a null (section itself says "cannot formally rule an effect out") | soften: retitle "Assessing the Analyst-Scrutiny Alternative"; "rule it out"->"assess it" (floor-aligned) | keep "Ruling Out" as-is |
| 3 | scrutiny rule-out tests VOLUME (CashScrutiny) but the confound is INCIDENCE (HighCashScrutiny, the one that rises 0.0408**) | prose caveat: note the gating test uses the continuous measure; incidence rises but volume is null | re-run gating with HighCashScrutiny x PreAnn (DATA) |
| 5 | no robustness to the 50%-cash classification threshold | add a one-line limitation (Conclusion) | re-run >=80%/100%-cash cut (DATA) |
| 6 | first-deal cash/stock deal counts never reported | report counts if found in outputs (cheap) | skip |
| 13 | one variable typeset 4 ways (\mathrm/\mathit/\textit/bare) | DEFER (regex risk in math mode near submission) | careful context-aware unify to \textit (text) keeping \mathit in displayed eqns |

## SINA DECISIONS (2026-06-28)
- #4 -> TWO-TAILED: fix the 3.2 prose (note is right). #5 -> limitation note (cheap). #1 -> ADD defs to Appendix II.
- #3 -> "keep silent COMPLETELY": REMOVE the 4.1 "genuine confound is incidence, not volume" sentence (numbers
  reworded out); add NO caveat anywhere. #8 -> SOFTEN ("Assessing the Analyst-Scrutiny Alternative"; "assess").
- #13 -> DEFER (typography). #6 -> add deal counts only if found cheaply, else skip.

## ADVISOR REFINEMENTS (2026-06-28)
- #4 tail: VERIFIED via runners -- empire_drop_test.py:191 + empire_cashspec_interaction.py:127 both
  "uniform two-tailed" (pdir=p2); 5.2 note plain "(two-tailed)"; test_h1 one-tailed = hypothesis-support,
  not the star rule. Direction = 5.2 two-tailed, 3.2 prose is the error. STILL confirm with Sina (load-bearing).
- #11 bib: assert len==22 BEFORE and AFTER sort; diff the KEY SET (not just order) so no entry is dropped/mangled.
- #12/#15 global sweeps: run LAST in prose_of (after fix_XX/destars/dehedge) so a global replace can't break a
  later anchor; also grep "Sections~" (plural) for #12.

## FINAL STATUS (2026-06-28, after waves 1-3; gates all green: PDF 70pp 0/0, floor 12/15/11/13/9/18/6/2/1, number A=0 B=0, orphan 0)
- DONE + committed (f7670537 wave1, 23dad6e6 wave2, 341e210a wave3):
  H2-caption, #1, #2, #4, #5, #7, #8, #9, #10, #11, #12, #14, #15, #16/#22, #18  (15 items)
- #3 RESOLVED (Sina: ACCEPT RESIDUAL): the explicit "incidence not volume" sentence is removed (wave1); the two
  load-bearing lines stay -- "HighCashScrutiny rises 0.0408" [l.58, motivation] and "CashScrutiny = volume"
  [l.62, non-circularity defense] -- because cutting them would break the section. Mismatch no longer spelled
  out. No further edit; current committed state is final.
- DECLINED: H2-prose upper-bound caveat (referee's "beta_s biased negative" conflicts with locked floor
  "stock arm = noisy flat null, never suppressed"; + overclaims). Existing hedge kept.
- DEFERRED (Sina): #13 variable typography (math-mode regex risk near submission).
- SKIPPED (Sina "else skip"; OUTSTANDING transparency gap): #6 first-deal cash/stock deal counts (not cheap;
  all-deals 982/123 already in via Logit B).
- HEADS-UP: FirmMat appendix def is approximate (data source says "lifecycle ... such as age/sales-growth/
  capital-structure"; the -317.57 min isn't explained by "lifecycle stage"). Ships fine; flag if examiner probes.

## VERIFY (each batch)
generator "PDF OK pages=70 undefined-ref/cite=0 overfull-hbox=0"; floor_inventory grid unchanged;
destars_verify PASS; number_audit A=0/B=0; orphan 0/21; advisor check after the batch.
