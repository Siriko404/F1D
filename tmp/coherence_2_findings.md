# §2 Brutal Coherence Pass — FINAL (2026-06-14, advisor-hardened + verified)

Scope: §2.1–2.5 prose vs 11 tables + spec page + Appendix I. Verified against committed NLM
spans (tmp/verify_2_numbers.py) and the variable registry. CONFIRMED = cross-checked.

## HIGH — confirmed; committee-dangerous

### A. sCFO mislabeled (CONFIRMED — primary source)
- §2.4 calls the control "scaled cash flow from operations." Variable registry
  (tools/rebuild_variables_yaml.py:56): `sCFO = biddle2009, 5-year rolling std of CFO/avg assets`
  = cash-flow VOLATILITY. Table 1 (mean 0.062, min 0.0014, max 32, right-skew) fits a dispersion
  measure, not a level. Mislabel also propagates to the Appendix I gloss "Cash Flow (sCFO)."
- FIX: §2.4 + Appendix I → "cash-flow volatility (5-yr rolling SD of scaled operating cash flow)."

### B. PRisk "share" gloss clashes with its scale (CONFIRMED — advisor + spans)
- §2.5 P2: PRisk = "the share of a firm's earnings call devoted to political risk." Hassan's own
  words agree (span n2/n5: "the share of the conversation devoted to risks associated with political
  topics") — BUT it is a WEIGHTED sum of bigrams, capped at the 99th pct, STANDARDIZED by its SD
  (spans n2/n3). Table 1 shows mean 99.6 / SD 146 / max 1192 — not a 0–100 share.
- FIX: qualify as "Hassan's scaled measure of the share of the call devoted to political risk
  (a standardized political-risk bigram-frequency index)", or add a scaling note to Table 1.

### C. Table 1 omits the eq(4) first-stage controls (CONFIRMED)
- §2.3 eq(4) FirmChars = {SurpDec, EPSgrowth, StockRet, MarketRet}. NONE appear in Table 1
  ("variables used in the hypothesis tests"). Three different control sets coexist (eq(4) first
  stage / validity tables / main design) with the first-stage four never summarized.
- FIX: add the four to Table 1 (regenerate summary stats), OR state they are internal first-stage
  controls and put them in the (pending) controls catalogue.

### D. Hollander "six of ten" figure is unverified (CONFIRMED — span check)
- §2.1 P3: "in roughly six of ten calls managers withhold." P3.1 spans: the decisive span is
  TRUNCATED right before the figure; the other two are OCR/URL garbage. No admissible span carries
  60% / six-of-ten. Verdict was SUPPORTED on the qualitative claim, not the figure.
- FIX: NLM requery for a clean span with the figure, OR soften to the supported qualitative claim
  ("managers frequently withhold requested information... silence speaks").

## MEDIUM

### E. Validity coefs are industry-FE columns; US-EPU marginal under firm-FE (CONFIRMED; narrowed)
- §2.5 P2 cites col (1) Industry+CalYr FE. Under the design's firm-FE spec: PRisk same (0.0001***
  both), GEPU STRONGER (0.0187** col3 vs 0.0181** col1), US-EPU WEAKER (0.0124**→0.0123*, p<0.10).
- FIX (narrow): note US-EPU validity is marginal under firm FE, or report the firm-FE column.

### F. Lagged-DV asymmetry across validity tables (CONFIRMED — advisor)
- h24/h24b carry `Lagged_DV 0.0202***`; h11 (PRisk) does not. Unexplained.
- FIX: justify (EPU is a persistent macro series; PRisk less so) or harmonize.

### G. §2.5 P5 dangling controls catalogue (CONFIRMED)
- P5: controls "catalogued in the Appendix." Appendix I holds ONLY the cash-scrutiny word list.
- FIX: build the controls catalogue (Appendix II / extend I) or soften P5. (Do NOT just rename
  "the Appendix"→"Appendix I" here — the catalogue genuinely does not exist.)

## LOW — polish
- H. §2.5 P1 "measures of uncertainty" vs P2 "uncertainty and risk" — align P1.
- I. §2.5 P4 "the Appendix" → "Appendix~I" (P4 only — its word list IS Appendix I; NOT P5).
- J. §2.1 P7 ledger prose_status reads "DRAFTED" while §2.1 is ratified — hygiene.
- K. H1b formal states θ_gap=0 (a null) but §2.4 tests β_PRE1−β_GAP>0 — restate θ_gap=0 as a
  descriptive expectation, not a tested restriction.
- L. Thewissen 15%: span says "in the year preceding the M&A announcement"; thesis says
  "stock-for-stock." Confirm the 15% is the stock-for-stock figure (not all-M&A).
- M. (results-section, NOT a §2 error) H1b κ_gap>0 but CashRatio at GAP is insignificant
  (0.0055) in empire_drop_matched — flag for §3/§4.
- N. Verify DWZ "Equation (2)/(4)/(5)" numbering vs tmp/nlm_dwz_equations.json (likely OK).

## VERIFIED-OK (no action)
- LM "285 words" ✓ span; Harvard "nearly three-quarters" ✓ ("three-fourths (73.8%)").
- Thewissen 15% ✓; Ragozzino 9% / 7.2% ✓ (spans).
- Thin-claim discipline consistent; "managers nonetheless hold" (voluntary-call scar fixed);
  net-of-{UncPre,UncQue,NegCall} consistent; PreAnnounceQtr consistent 2.2/2.4/spec;
  main-design 7 controls match empire_building_did exactly; cash-scrutiny def consistent.
