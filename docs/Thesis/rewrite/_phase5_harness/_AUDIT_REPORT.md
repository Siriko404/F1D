# THESIS FINAL AUDIT REPORT (1 panel x 7 referees, merged from JSONL)

## Coverage
- referees reported: citations_A, coherence_A, completeness_A, honesty_A, methodology_A, numbers_A, style_A
- malformed/partial lines skipped: 0

## Counts
- HIGH 2 | MEDIUM 25 | LOW 79 | total 106 | clean-bills 90

## HIGH severity (2)

### 1. [methodology] high -- generated-regressand SE correction asserted-but-not-run
- location: Sec 2.3 (l.319) + Sec 2.4 threats (l.331)
- problem: UncResCEO is a first-stage residual used as DV; Pagan(1984) two-step SE understatement is flagged, but the bootstrap is never run and they ASSERT it 'does not change the descriptive readings' without evidence. The load-bearing run-up significance (p=.0074 two-tailed) and the marginal Wald (p=.039) ride on SEs that ignore first-stage estimation noise.
- evidence: 'together with the bootstrap that would address it, and note that it does not change'
- best fix: Actually run the two-step/wild bootstrap on at least the headline run-up and the cash-specificity Wald; report corrected SEs, or downgrade the significance claims to point estimates.
- refutation: They frame every claim as 'descriptive/correlational', so arguably no inferential weight is placed on the SEs; but stars and p-values are reported and leaned on throughout.  (confidence: high)

### 2. [methodology] high -- stock arm is a confounded comparison yet labelled 'placebo' and used as the cash-specificity baseline
- location: Tables 5.2/5.4/5.5/5.17 captions vs Sec 2.1-2.2 framework
- problem: The framework argues stock bidders actively manage pre-deal tone (Thewissen/Louis), so the stock arm is NOT a clean placebo; yet tables call it 'placebo'. Worse, the cash-specificity Wald (beta_c-beta_s) treats stock as the comparison: if stock bidders manage uncertainty DOWNWARD pre-deal, beta_s is biased negative and the cash-minus-stock gap is inflated. They concede the gap 'rides on the imprecise negative stock estimate' but never confront that this negativity may be the management artifact, i.e. the test is contaminated by the very story invoked to motivate it.
- evidence: 'Stock acquirers (placebo)' | 'rides in part on the imprecise negative stock estimate'
- best fix: Drop the word 'placebo' everywhere (use 'managed comparison'); add a one-sided caveat that stock-arm tone management biases beta_s negative and can inflate the Wald gap, so the gap is an upper bound.
- refutation: They do flag the gap rides on the stock estimate and frame as 'concentration not specificity', partially covering it.  (confidence: high)

## MEDIUM severity (25)

### 1. [citations] medium -- author-name-consistency
- location: Table 5.21 (tab:dwz_replication) caption + notes vs bibitem dwz
- problem: Lead author DWZ spelled inconsistently: bibliography and every \citet/\citeauthor render plain 'Dzielinski', but Table 5.21 caption and notes use an accented form (LaTeX Dzielin\'ski). The accent is also mis-placed (lands on s, giving Dzielinski-with-s-accent) rather than the intended Polish n.
- evidence: bib: 'Dzielinski, M.' no accent | caption: 'Replication of Dzielin\'ski et al.' | notes: 'Equation 4 of Dzielin\'ski, Wagner...'
- best fix: Make all instances identical: use plain 'Dzielinski' in Table 5.21 caption+notes to match the bibitem and the in-text cites (or apply the correct accent everywhere).
- refutation: Both forms point to the same person; a reader still maps them. Cosmetic, not a resolution failure.  (confidence: high)

### 2. [citations] medium -- reference-list-ordering
- location: References (thebibliography, ch. after Conclusion)
- problem: Author-year reference list is not in a single alphabetical sequence. Entries 1-11 are alphabetical (Baker..Thewissen), then the list restarts the alphabet at Bertrand and runs two further un-merged blocks (three alphabetical runs in all) (Bertrand, Dye, Harford, Hollander, Keown, Verrecchia, Bates, Louis, Opler, Pagan, Shleifer) -- and even within it Verrecchia precedes Bates.
- evidence: Thewissen(2024) then Bertrand(2003) | Verrecchia(1983) then Bates(2009)
- best fix: Re-sort all 22 ibitem entries into one alphabetical-by-first-author sequence (standard for author-year/natbib).
- refutation: Citations still resolve by key regardless of print order; some templates tolerate citation-order lists, though authoryear convention is alphabetical.  (confidence: high)

### 3. [coherence] medium -- scrutiny rule-out tests the wrong scrutiny measure
- location: Sec 4.1; Tables 5.10, 5.11
- problem: 4.1 names the 'genuine confound' as scrutiny INCIDENCE (HighCashScrutiny, rises 0.0408** pre-announce) yet the channel/gating rule-out (Tables 5.10/5.11) is run on the VOLUME measure CashScrutiny, which itself does NOT rise pre-announce (0.0854 ns). The direct test HighCashScrutiny x PreAnnounceQtr is never shown.
- evidence: 'genuine confound is...incidence' | gating uses CashScrutiny x PreAnnounceQtr | HiSc 0.0408** vs CshSc 0.0854 ns
- best fix: Run channel/gating with HighCashScrutiny + its interaction, or justify why continuous CashScrutiny subsumes incidence.
- refutation: Continuous CashScrutiny encodes 0 vs >0; its null on the residual plausibly implies incidence null; text mentions 'coarser scrutiny proxies' were checked.  (confidence: medium)

### 4. [coherence] medium -- undefined variables vs table-note claim
- location: Table 5.1; Tables 5.6-5.8
- problem: FirmMat and EarnVol appear in summary stats and the convergent-validity tables but are never defined in the text or Appendices I/II, contradicting Table 5.1's note 'All variables are defined in the main text and in Appendices I and II'. FirmMat shows an anomalous min of -317.57 with no definition to consult.
- evidence: FirmMat, EarnVol in Table 5.1 | note: 'All variables are defined' | absent from App I/II + text
- best fix: Define FirmMat, EarnVol (and Table 5.12 extended controls) in Appendix II, or drop the blanket 'all defined' claim.
- refutation: They are validity-only controls a reader might infer; but the formulas are genuinely absent and the note over-promises.  (confidence: high)

### 5. [completeness] medium -- chapter-vs-section naming mismatch
- location: intro roadmap + all cross-refs
- problem: Body uses book class with \chapter (renders 'Chapter 1..5') but prose consistently calls them 'Section 2/3/4/5'; e.g. roadmap 'Section 5 concludes' points to Chapter 5 Conclusion
- evidence: \chapter{Conclusion} | 'Section~5 concludes' | 'develops...empirical strategy' is Chapter 2
- best fix: Replace bare 'Section N' chapter references with 'Chapter N' (the X.Y subsection refs already render correctly)
- refutation: Finance papers conventionally say 'Section'; X.Y refs all resolve, so a charitable reader maps Section N->Chapter N  (confidence: high)

### 6. [completeness] medium -- undefined variables vs 'all variables defined' claim
- location: Table 5.1 notes; Tables 5.6-5.8
- problem: FirmMat and EarnVol appear in summary stats and convergent-validity tables as controls but are never defined in text or Appendices; yet Table 5.1 note asserts 'All variables are defined in the main text and in Appendices I and II'
- evidence: FirmMat / EarnVol only in tables | note: 'All variables are defined...'
- best fix: Add FirmMat (firm maturity) and EarnVol (earnings volatility) definitions to Appendix II, or drop them
- refutation: Names are self-suggestive (firm maturity, earnings volatility) and they are non-focal controls  (confidence: high)

### 7. [completeness] medium -- broken roadmap promise: decomposition controls not in Appendix
- location: Sec 2.5 final para (line ~343)
- problem: Text says 'the controls from the Section 2.3 decomposition that builds the residual are catalogued in the Appendix', but Appendix II catalogs only CashRatio + firm-financial controls; SurpDec, EPSgrowth, StockRet, MarketRet, NegCall, UncQue are not catalogued anywhere
- evidence: 'catalogued in the Appendix' | Appendix II has no SurpDec/EPSgrowth/StockRet/MarketRet
- best fix: Add the Section-2.3 decomposition controls to an appendix table, or soften the claim
- refutation: Table 5.21 glosses SurpDec/StockRet/EPSgrowth/MarketRet in row labels; UncQue/NegCall named in 2.3  (confidence: high)

### 8. [honesty] medium -- causal verb in plain-language gloss
- location: Sec 4.1 reason-gating paragraph
- problem: De-hedged gloss uses a transitive causal verb in a strictly-correlational thesis (floor #1 forbids any causal verb): 'the reason for the deal raises uncertainty' attributes causation; 'amplify' frames the interaction causally. Milder second instance 'the uncertainty raised in the run-up' (Sec 3.3).
- evidence: the reason for the deal raises uncertainty | does not amplify the reason | uncertainty raised in the run-up
- best fix: Use associational verb: 'the pre-announcement quarter is associated with higher uncertainty; cash scrutiny is not, and does not interact with it.'
- refutation: Same sentence ends '...and correlational'; 'raises' may be loose shorthand and the surrounding frame is associational.  (confidence: medium)

### 9. [honesty] medium -- 'rule out' overclaims a null
- location: Intro; Sec 4.1 title and first sentence
- problem: 'We also rule out the most immediate alternative', section title 'Ruling Out Analyst Scrutiny', and 'We rule it out in three steps' assert elimination of the scrutiny confound, contradicted by the section's own landing: 'a failure to find ... not a powered equivalence test that could formally rule an effect out.'
- evidence: We also rule out the most immediate alternative | We rule it out in three steps | not a powered equivalence test
- best fix: Retitle 'Assessing the Analyst-Scrutiny Alternative'; replace 'rule out' with 'fail to find support for'.
- refutation: Each 'rule out' is narrowed locally ('does not account for this run-up, not that scrutiny never matters'); net claim lands honest.  (confidence: medium)

### 10. [honesty] medium -- core 'unmanaged' assumption de-hedged to flat fact
- location: Sec 2.1 (line 295) vs Sec 2.1 (line 297) and Sec 2.2 H1 (line 305)
- problem: The load-bearing identifying assumption is hedged correctly as 'the RELATIVELY unmanaged window' / 'hardest to stage-manage' / 'cannot fully prepare', but stated flat as fact elsewhere: 'ours is UNMANAGED uncertainty in the unscripted Q&A' and 'unmanaged uncertainty before cash deals'. The flat form asserts immunity to management that the design (and the thesis's own 'residual understates it if anticipation leaks into scripted remarks') does not support.
- evidence: the relatively unmanaged window | ours is unmanaged uncertainty | but unmanaged uncertainty before cash deals
- best fix: Make every instance 'relatively unmanaged' / 'less managed', matching line 295.
- refutation: Context makes the comparative sense clear; 'unmanaged' may read as shorthand for 'unmanaged relative to the scripted channel'.  (confidence: medium)

### 11. [methodology] medium -- prose contradicts table footnote on tailedness
- location: Sec 3.2 prose (l.368) vs Table 5.2 notes (l.671)
- problem: Prose says 'the table's one-tailed reporting convention' for Table 5.2, but Table 5.2's own footnote states '(two-tailed)'. The headline coefficient 0.0461/0.0172=2.68 gives two-tailed p=.0074, so the *** is two-tailed-correct and the footnote is right; the prose's characterization of the table as one-tailed is simply wrong/internally inconsistent.
- evidence: prose: 'the table's one-tailed reporting convention' | table note: '(two-tailed)'
- best fix: Reword prose to: 'a worry that the result depends on one-tailed reporting; it does not -- the table is two-tailed and p=.0074.'
- refutation: None substantive; it is a self-contradiction within the same file.  (confidence: high)

### 12. [methodology] medium -- bid-ask DV magnitudes irreconcilable with summary stats (undisclosed scaling)
- location: Table 5.12 (l.1147-1186) vs Table 5.1 BGTLevel_Spread (l.597)
- problem: Summary stats give BGTLevel_Spread mean 0.0017, max 0.0164. But Table 5.12 coefficients are orders of magnitude larger (lnAssets -0.80 to -1.91, ROA -9.4, Turnover -24.1, UncPreCEO 0.166-0.350). On the raw 0.0017-scale DV these coefficients are impossible (a single regressor would drive the spread far past its max). The regression DV is evidently rescaled (~x1000 / bps), but the table never states the units, so a reader cannot reconcile magnitudes with Table 5.1 or judge economic size.
- evidence: mean 0.0017 vs lnAssets coef -0.8039 | Turnover -24.1012
- best fix: State the DV units in the Table 5.12 header/notes (e.g. 'spread in basis points, x1000') and ensure consistency with Table 5.1.
- refutation: Speech-coefficient ranges quoted in prose match the table rows, so the within-table reading is internally consistent; only the cross-table unit reconciliation is missing.  (confidence: medium)

### 13. [methodology] medium -- no robustness to the 50%-cash classification threshold
- location: Sec 2.2/3.1 deal definition (l.303, l.360)
- problem: Cash arm = deals >=50% cash; stock arm = >=50% stock. The entire design hinges on this dichotomy yet no sensitivity to the threshold is shown (e.g. pure 100%-cash deals, or 80% cut). An examiner would demand evidence the run-up is not an artifact of mixed-consideration deals near the 50% boundary.
- evidence: 'at least 50% cash'
- best fix: Add a robustness cut restricting to >=80% or 100% cash (and symmetric stock) and report the run-up and Wald survive.
- refutation: The all-deals-stacked and matched checks vary sample composition broadly, indirectly probing robustness; but none varies the cash/stock cut itself.  (confidence: medium)

### 14. [methodology] medium -- variables used in tables are defined nowhere
- location: Tables 5.6-5.8 (FirmMat,EarnVol), Table 5.12 extended controls, Sec 4.1 HighCash, Appendix II
- problem: FirmMat and EarnVol appear in summary stats and in the headline convergent-validity regressions (5.6/5.7/5.8) but are defined nowhere (Appendix II lists only CashRatio + 7 financial controls; Sec 2.3 lists only SurpDec/EPSgrowth/StockRet/MarketRet/NegCall/UncPreCEO/UncQue). HighCash carries a validity claim (0.1754***) with no cutoff stated (mean 0.3333, not a median split). Table 5.12's extended controls (StockPrice, Turnover, DailyVola, AbsSurpDec) are likewise undefined. An examiner flags every undefined regressor.
- evidence: FirmMat/EarnVol in Table 5.6 rows; absent from Appendix II | HighCash mean 0.3333
- best fix: Add FirmMat, EarnVol, HighCash, and the four bid-ask extended controls to Appendix II with formulas/cutoffs.
- refutation: Some (e.g. AbsSurpDec, DailyVola) are semi-self-evident from name; none is a focal treatment variable.  (confidence: high)

### 15. [methodology] medium -- number of cash vs stock deals never reported for the load-bearing first-deal tests
- location: Ch.3 main analyses (Tables 5.2-5.5)
- problem: The first-deal run-up, event study, and Wald tables report firm and firm-quarter counts but never the count of cash vs stock acquisitions actually identifying the effect. The count clearly exists (Logit B discloses 982 cash / 123 stock for the all-deals deal-level sample). Its omission for the headline first-deal results is a transparency and power gap a referee will demand.
- evidence: Tables 5.2-5.5 report only firm/firm-qtr N | Logit B: '982 cash, 123 stock'
- best fix: Report the number of treated cash and stock deals (and treated firms) underlying each first-deal table.
- refutation: PreAnnounceQtr mean (0.0094) and firm counts let a determined reader bound the deal count indirectly.  (confidence: high)

### 16. [methodology] medium -- REFINES finding 'prose contradicts table footnote on tailedness' — likely the footnote, not the prose, is the error
- location: Table 5.2 notes (l.671) vs Sec 3.2 prose (l.368)
- problem: Correcting my earlier direction: the Table 5.2 stars cannot themselves discriminate one- vs two-tailed, and the prose offers 'survives a two-tailed test (p=.0074)' as an EXTRA check, implying the table stars were computed one-tailed and the '(two-tailed)' footnote is the mislabel -- consistent with Tables 5.6-5.12 all using one-tailed focal tests. Either way it is a genuine contradiction; the safer reading is that the footnote is wrong.
- evidence: prose: 'survives a two-tailed test (p=.0074)' framed as additional reassurance
- best fix: Reconcile: confirm whether Table 5.2 stars are one- or two-tailed and correct the mislabelled element; do not assume the prose is the error.
- refutation: For the headline coefficient *** holds two-tailed anyway, so the substantive significance claim is unaffected by which element is wrong.  (confidence: medium)

### 17. [methodology] medium -- REFINES bid-ask scaling confidence
- location: Table 5.12 vs Table 5.1
- problem: Confidence on the undisclosed-scaling finding should be high, not medium: lnAssets -0.80, ROA -9.4, Turnover -24.1 are arithmetically impossible on a DV whose summary max is 0.0164, so the regression DV is certainly rescaled (~x1000) and the units are certainly undisclosed.
- evidence: DV max 0.0164 vs Turnover coef -24.1012
- best fix: State the rescaled DV units in Table 5.12.
- refutation: None on existence of the mismatch; only its severity is a judgement call.  (confidence: high)

### 18. [numbers] medium -- tail-convention prose-vs-table mismatch
- location: Sec 3.2 line 368 vs Table 5.2 note
- problem: prose calls it 'the table's one-tailed reporting convention' but Table 5.2 note says '(two-tailed)' and stars are two-tailed
- evidence: 'table's one-tailed reporting convention' | Table 5.2 note '(two-tailed)' | ROA stock 0.0075* t=1.83 is * two-tailed not ** one-tailed
- best fix: reword to 'two-tailed' or drop the one-tailed framing for this table
- refutation: may be loose wording referring to the thesis-wide focal-test convention rather than this table; *** holds either way  (confidence: medium)

### 19. [style] medium -- variable-name typography uniformity
- location: throughout; esp. line 317, Ch2 vs Ch3-4
- problem: Same constructs (UncResCEO, CashRatio, CashScrutiny, PreAnnounceQtr) typeset 4 ways: \mathrm{} (upright), \mathit{} (math-italic), \textit{} (text-italic), and bare unformatted in Ch3-4; renders as visibly different fonts for one variable
- evidence: line317 \mathit{UncResCEO} and \textit{UncResCEO} same sentence | 268 \mathrm{UncResCEO} | 356/368 bare UncResCEO
- best fix: Pick ONE convention (e.g. \textit{} text-italic) and apply to every variable mention incl. bare Ch3-4 names
- refutation: If a macro \Var were defined the source could differ yet render uniformly, but raw \mathrm vs \textit render upright vs italic differently  (confidence: high)

### 20. [style] medium -- p-value format / no-leading-zero
- location: Sec 2.4 methodology, line 331
- problem: Same statistic written two incompatible ways: $p = 0.0074$ (leading zero + spaces) at line 331 vs $p=.0074$ (no leading zero, no spaces) at line 368; line 331 is the ONLY leading-zero p-value in the whole doc
- evidence: 331 $p = 0.0074$ | 368 $p=.0074$ same number | all other p: $p<.0 / $p=.0
- best fix: Change line 331 to $p=.0074$ to match the document-wide no-leading-zero convention
- refutation: Leading zero is defensible APA-side, but doc's own dominant style is no-leading-zero so 331 is the outlier  (confidence: high)

### 21. [style] medium -- dash style uniformity
- location: Ch2 (lines ~287-343) vs Abstract/Intro/Ch3-4
- problem: Two parenthetical-dash styles coexist: spaced en-dash ' -- ' (33x, concentrated in Ch2) vs unspaced em-dash '---' (in abstract L217, intro L278, Ch3-4 L354-388). One device, two renderings
- evidence: 287 'be -- a probability' | 217 'uncertainty---the part' | 354 'paid for---keeping'
- best fix: Normalize all interruptive dashes to one form (em-dash '---' is the majority register in body sections); convert Ch2 ' -- ' accordingly
- refutation: Both are valid typographically; only a problem because the same doc mixes them  (confidence: high)

### 22. [style] medium -- event-time index notation
- location: Tables 5.3/5.4 row labels (L687,746) vs prose Sec2.4 & same-table notes (L728)
- problem: Event-time bins labelled '($t{-}2$)'/'($t{-}1$)' in table rows, but defined as '$e{=}{-}2$'/'$e=-1$' in prose and in the SAME table's notes; worse, $t$ is already the calendar-quarter index in $Y_{it}$, $\tau_t$, so $t-1$ overloads the symbol the $e$ notation exists to disambiguate
- evidence: 687 'PRE2 ($t{-}2$, pre-trend)' | 728 notes '$\mathrm{PRE2}$ ($e{=}{-}2$)' | 323 $Y_{it}$ uses t for calendar
- best fix: Relabel table rows to $e{=}{-}2$/$e{=}{-}1$ to match prose and notes
- refutation: $t-1$ is a common generic 'one period before' shorthand a reader may parse loosely, but here it collides with the model's own t index  (confidence: high)

### 23. [style] medium -- construct-name synonym drift across tables
- location: Tables 5.15-5.18 (L1330,1366,1420,1472) vs Tables 5.2-5.14
- problem: Same constructs abbreviated inconsistently in all-deals robustness tables: UncResCEO->'UncRes'(5.16,5.18)/'UncR'(5.15); CashRatio->'CashR'(5.16,5.18)/'CshR'(5.15); CashScrutiny->'CshSc'; HighCashScrutiny->'HiSc' -- while main tables spell them out. Two abbreviation schemes even within the robustness block; Table 5.15 needs an ad-hoc notes glossary
- evidence: 1330 'CshR & UncR & CshSc & HiSc' | 1366 'UncRes & CashR' | 1355 glossary 'CshR=CashRatio(+lag)'
- best fix: Use the full construct names (UncResCEO, CashRatio, CashScrutiny, HighCashScrutiny) as column heads in 5.15-5.18, matching 5.2-5.14
- refutation: Abbreviations save width in landscape 8-col tables; a glossary is provided -- but the two schemes (CshR vs CashR) are indefensible  (confidence: high)

### 24. [style] medium -- standard-error decimal precision (prose)
- location: Sec 4.5 prose L448, L452 vs doc-wide 4dp and Tables 5.19/5.20
- problem: Two SEs printed to 5 decimals in prose -- $0.00275$ (L448) and $0.05076$ (L452) -- while every other SE in prose and all tables uses 4 decimals; the SAME two coefficients show 4dp SEs in their tables (5.19 L1520 (0.0027); 5.20 L1556 (0.0508)), so it is both a precision drift and a prose-table mismatch
- evidence: 448 'standard error $0.00275$' | 452 'standard error $0.05076$' | 1520 (0.0027) | 1556 (0.0508)
- best fix: Round both prose SEs to 4dp ($0.0027$/$0.0028$ and $0.0508$) to match the tables and the document standard
- refutation: 5dp is more precise, not wrong; but it is inconsistent with the doc's own 4dp standard and its own tables  (confidence: high)

### 25. [style] medium -- unit naming: 'Section N' vs rendered 'Chapter N'
- location: prose L278 (and L268,311,335,etc.) vs chapter at L259/283/350/402/457; fossil label sec:framework L283
- problem: book class with \chapter{} for all five top units renders headings 'Chapter 1..5', but prose refers to whole units as 'Section~2..Section~5' (roadmap L278: 'Section 2 develops... Section 5 concludes'). Subsection refs 'Section 2.3/4.1' are fine; only the whole-unit refs mismatch. The \chapter carries \label{sec:framework}, a leftover from a section->chapter conversion
- evidence: 278 'Section~2 ... Section~5 concludes' | 283 \chapter{...}\label{sec:framework}
- best fix: Change whole-unit cross-references from 'Section N' to 'Chapter N' (leave 'Section N.M' subsection refs)
- refutation: Overlaps the cross-reference referee's lane; if the author intends 'Section' as the top-level term the fix is heading-side instead -- but as rendered they contradict  (confidence: high)

## LOW severity (79)

### 1. [citations] low -- cite-year-vs-entry
- location: References: rule10b5 bibitem + in-text \citep{rule10b5}
- problem: In-text the rule renders 'Rule 10b-5 (2014)' (label year 2014), but the reference entry text contains no 2014 -- it reads only 'Rule 10b-5, 17 C.F.R. 240.10b-5'. A reader checking the year finds no matching date in the entry.
- evidence: label [Rule 10b-5(2014)] | entry has no '2014'
- best fix: Add the C.F.R. edition/revision year (e.g. '(2014 ed.)') to the rule10b5 entry text so the cited year is sourced.
- refutation: Legal-citation convention puts the code-edition year only in the parenthetical; some readers accept the label year alone.  (confidence: high)

### 2. [citations] low -- borrowed-method-uncited
- location: Table notes 5.6/5.7/5.8 + cash_scrutiny tables ('industry (FF12)')
- problem: The Fama-French 12-industry (FF12) classification is used as a fixed-effect grouping in multiple tables but Fama and French (1997) is never cited; no bibitem exists for it.
- evidence: notes: 'industry (FF12)' | no Fama-French bibitem
- best fix: Add a Fama-French (1997) reference and cite it at first use of FF12, or define FF12 in the Appendix with the source.
- refutation: FF12 is a near-universal, off-the-shelf scheme often left uncited; not a claim of novelty.  (confidence: medium)

### 3. [citations] low -- borrowed-method-uncited
- location: Sec 4.4 (Robustness: dynamic term), 'subject to the Nickell bias'
- problem: 'Nickell bias' is invoked by name to justify the static-FE robustness check, but Nickell (1981) is not cited and has no bibitem.
- evidence: 'subject to the Nickell bias' | no Nickell bibitem
- best fix: Cite Nickell (1981) at the phrase, or attribute the dynamic-panel-bias point to a cited source.
- refutation: 'Nickell bias' is a textbook eponym econometricians read without a cite; pagan1984 already covers the generated-regressor caveat (different issue).  (confidence: medium)

### 4. [citations] low -- prose-vs-table-claim (cross-referee flag)
- location: Sec 2.4 disclosure para vs validity table notes 5.6-5.10
- problem: Prose states 'some validity tables use two-way clustering, by firm and by calendar quarter', but every validity table note actually reads 'Standard errors clustered by firm' only -- no table reports two-way clustering.
- evidence: prose: 'two-way clustering, by firm and by calendar quarter' | all notes: 'clustered by firm'
- best fix: Reconcile: either correct the prose to 'clustered by firm throughout' or update the relevant table notes if two-way clustering was in fact used.
- refutation: This is a methods/consistency issue, not citation/attribution -- likely belongs to the numbers/consistency referee, not this dimension.  (confidence: medium)

### 5. [citations] low -- external-attribution
- location: Intro + Sec 2.1 (matsumoto2011)
- problem: Verify against source: claim that the analyst-discussion/Q&A session carries information beyond the prepared presentation.
- evidence: 'analyst-discussion session carries information beyond the managers prepared presentation'
- best fix: Confirm Matsumoto et al.(2011) supports this.
- refutation: Standard reading of the paper; likely accurate.  (confidence: low)

### 6. [citations] low -- external-attribution
- location: Sec 2.1 (verrecchia1983)
- problem: Verify: informed manager rationally withholds when disclosure is costly; a threshold below which he withholds.
- evidence: 'rationally choose not to reveal... threshold below which the informed manager simply withholds'
- best fix: Confirm Verrecchia(1983) discretionary-disclosure threshold.
- refutation: Canonical summary of Verrecchia(1983).  (confidence: low)

### 7. [citations] low -- external-attribution
- location: Intro + Sec 2.1 (dye1985)
- problem: Verify: non-disclosure persists in equilibrium because investors cannot tell an uninformed manager from an informed-but-silent one.
- evidence: 'cannot... tell a manager who knows nothing from one who knows something and is keeping quiet'
- best fix: Confirm Dye(1985).
- refutation: Standard Dye(1985) pooling result.  (confidence: low)

### 8. [citations] low -- external-attribution
- location: Sec 2.1 (basic1988, materiality)
- problem: Verify: Court held preliminary/pending merger talks can be material; materiality = probability x magnitude.
- evidence: 'preliminary, still-pending merger negotiations can be material... how likely... against how large'
- best fix: Confirm Basic v. Levinson(1988) holding.
- refutation: Accurately states the Basic probability/magnitude test.  (confidence: low)

### 9. [citations] low -- external-attribution
- location: Intro + Sec 2.1 (basic1988 + rule10b5, duty/mislead)
- problem: Verify: no general duty to disclose confidential merger talks, but once it speaks a firm may not mislead (untrue/half-true statement unlawful).
- evidence: 'no general duty to disclose... once it speaks, it may not mislead'
- best fix: Confirm jointly against Basic(1988) and Rule 10b-5.
- refutation: Consistent with 10b-5 half-truth doctrine.  (confidence: low)

### 10. [citations] low -- external-attribution
- location: Intro + Sec 2.1 (hollander2010)
- problem: Verify: managers make deliberate disclosure/silence choices on calls and a non-answer is itself informative ('silence speaks').
- evidence: 'silence speaks' | 'non-answer or a silence is itself informative'
- best fix: Confirm Hollander et al.(2010).
- refutation: Matches the paper's title/thesis.  (confidence: low)

### 11. [citations] low -- external-attribution
- location: Intro + Sec 2.5 (keown1981)
- problem: Verify: abnormal stock-price run-up precedes public merger announcements (pre-announcement leakage into prices).
- evidence: 'abnormal stock-price run-up before public merger announcements'
- best fix: Confirm Keown and Pinkerton(1981).
- refutation: Standard citation for pre-bid run-up.  (confidence: low)

### 12. [citations] low -- external-attribution
- location: Intro + Sec 2.1 (lm2011)
- problem: Verify: finance-specific word lists, including the uncertainty list used here, classify tone/uncertainty in financial text.
- evidence: 'finance-specific word lists -- among them the uncertainty list our measure uses'
- best fix: Confirm Loughran and McDonald(2011) uncertainty list.
- refutation: LM(2011) is the canonical source.  (confidence: low)

### 13. [citations] low -- external-attribution
- location: Sec 2.1 (bertrand_schoar2003)
- problem: Verify: managers carry durable individual styles showing up as manager fixed effects in firm policies/outcomes.
- evidence: 'durable, individual styles that show up as manager fixed effects'
- best fix: Confirm Bertrand and Schoar(2003).
- refutation: Matches 'Managing with Style'.  (confidence: low)

### 14. [citations] low -- external-attribution
- location: Sec 2.1/2.3 (dwz, decomposition)
- problem: Verify: DWZ separate call uncertainty/clarity into a persistent CEO-specific component and a time-varying call-level residual (the decomposition this paper re-estimates).
- evidence: 'separate... into two pieces: a persistent, manager-specific component... and a time-varying, call-level residual'
- best fix: Confirm Dzielinski et al.(2021) decomposition.
- refutation: Method described matches a working paper this study replicates in Table 5.21.  (confidence: low)

### 15. [citations] low -- external-attribution
- location: Sec 2.1 + 4.2 (dwz, residual null on prices); recurs 293/418/420/422
- problem: Verify (single recurring claim): DWZ find the residual component largely unrelated to stock-price/trading-volume reactions, with the market reaction loading instead on persistent CEO clarity.
- evidence: 'residual component... largely unrelated to market and stock-price reactions' | 'loads instead on... persistent clarity'
- best fix: Confirm DWZ(2021) price/volume vs clarity result.
- refutation: Load-bearing for Sec 4.2 framing; restated 4x but one claim.  (confidence: low)

### 16. [citations] low -- external-attribution
- location: Table 5.21 + Sec 2.3 (dwz Table 3 col 2 numbers)
- problem: Verify (high-value): published DWZ Table 3(2) values reproduced here -- UncPreCEO 0.093, UncQue 0.049, NegCall 0.046; N=95,296; 5,985 CEOs; R2 incremental ~0.05 over 0.31 base; sample 2003-2015.
- evidence: '0.093... in theirs' | '95,296... 5,985' | '0.05 on top of a 0.31 base'
- best fix: Cross-check every DWZ column figure against DWZ(2021) Table 3 col (2).
- refutation: Header notes claim these were user-verified against the PDF + NotebookLM.  (confidence: low)

### 17. [citations] low -- external-attribution
- location: Sec 4.2 (bgt2018, opposite-sign segments)
- problem: Verify: BGT find call language relates to information asymmetry with opposite signs -- scripted-presentation complexity positive (obfuscation), spontaneous-response complexity negative (information).
- evidence: 'opposite signs across the call two segments' | 'presentation... positively... response... negatively'
- best fix: Confirm Bushee et al.(2018) segment signs.
- refutation: Matches the obfuscation-vs-information framing in the title.  (confidence: low)

### 18. [citations] low -- external-attribution
- location: Sec 4.2 (bgt2018, window adopted)
- problem: Verify: the 25-trading-day post-call bid-ask window is adopted from BGT.
- evidence: '25 trading days that begin on the call date... following \citet{bgt2018}, whose post-call window we adopt'
- best fix: Confirm BGT(2018) use this post-call window.
- refutation: Plausible; window choice attributed explicitly.  (confidence: low)

### 19. [citations] low -- external-attribution
- location: Sec 2.1 (harford1999)
- problem: Verify: firms build cash reserves ahead of acquisitions and cash-rich firms are more acquisitive.
- evidence: 'build up cash reserves ahead of acquisitions and... cash-rich firms are more acquisitive'
- best fix: Confirm Harford(1999).
- refutation: Standard Harford(1999) result.  (confidence: low)

### 20. [citations] low -- external-attribution
- location: Sec 2.1 (shleifer_vishny2003)
- problem: Verify: an overvalued bidder has incentive to keep equity overvalued so it can buy with stock.
- evidence: 'overvalued bidder... incentive to keep its equity overvalued so that it can buy with stock'
- best fix: Confirm Shleifer and Vishny(2003).
- refutation: Matches 'Stock market driven acquisitions'.  (confidence: low)

### 21. [citations] low -- external-attribution
- location: Sec 2.1 (louis2004)
- problem: Verify: stock-for-stock bidders show positive abnormal accruals (overstate earnings) the quarter before announcement, while cash acquirers do not.
- evidence: 'stock-for-stock bidders overstate reported earnings... whereas cash acquirers do not'
- best fix: Confirm Louis(2004) accruals result.
- refutation: Consistent with Louis(2004).  (confidence: low)

### 22. [citations] low -- external-attribution
- location: Sec 2.3 (pagan1984)
- problem: Verify: generated-regressor two-step setting -> conventional standard errors understated absent correction.
- evidence: 'sets out the issue for such two-step settings' | 'standard errors may be understated'
- best fix: Confirm Pagan(1984) generated-regressor result.
- refutation: Canonical Pagan(1984) point.  (confidence: low)

### 23. [citations] low -- external-attribution
- location: Sec 2.4 (opler1999 + bates2009)
- problem: Verify: the firm-financial controls follow the standard cash-determinants regression of these two papers.
- evidence: 'standard cash-determinants regression \citep{opler1999, bates2009}'
- best fix: Confirm control set matches Opler et al.(1999) / Bates et al.(2009).
- refutation: Both are canonical cash-holdings determinants papers.  (confidence: low)

### 24. [citations] low -- external-attribution
- location: Sec 2.5 (hassan2020)
- problem: Verify: PRisk is the call-based firm-level political-risk measure of Hassan et al.(2020).
- evidence: 'firm-level political risk (PRisk), the call-based measure of \citet{hassan2020}'
- best fix: Confirm Hassan et al.(2020) PRisk.
- refutation: Correct source for PRisk.  (confidence: low)

### 25. [citations] low -- external-attribution
- location: Sec 2.5 (baker2016)
- problem: Verify: US-EPU is the newspaper-based economic-policy-uncertainty index of Baker et al.(2016).
- evidence: 'US economic policy uncertainty (US-EPU), the newspaper-based index of \citet{baker2016}'
- best fix: Confirm Baker, Bloom, Davis(2016).
- refutation: Correct source for US-EPU.  (confidence: low)

### 26. [citations] low -- external-attribution
- location: Sec 2.5 (davis2016)
- problem: Verify: GEPU is the global economic-policy-uncertainty index of Davis(2016).
- evidence: 'global economic policy uncertainty (GEPU), the index of \citet{davis2016}'
- best fix: Confirm Davis(2016) NBER WP 22740.
- refutation: Correct source for GEPU.  (confidence: low)

### 27. [citations] low -- external-attribution
- location: Intro + Sec 2.1/2.2 (thewissen2024)
- problem: Verify: stock-for-stock acquirers deliberately manage/inflate the tone of their pre-deal disclosure (earnings press releases) before the announcement.
- evidence: 'stock bidders inflate the tone of their earnings press releases before a stock-for-stock acquisition'
- best fix: Confirm Thewissen et al.(2024) tone-management finding.
- refutation: Matches the SSRN working-paper title; load-bearing for the cash-vs-stock motivation.  (confidence: low)

### 28. [citations] low -- external-attribution
- location: Intro + Sec 2.1 (ragozzino2024)
- problem: Verify: the volume of corporate-strategy vocabulary rises on the earnings calls of acquisitive firms around deal activity.
- evidence: 'volume of corporate-strategy vocabulary rises on the calls of acquisitive firms'
- best fix: Confirm Ragozzino and Reuer(2024).
- refutation: Plausible; cited as adjacent (volume, not uncertainty) work.  (confidence: low)

### 29. [citations] low -- borrowed-claim-uncited
- location: Sec 4.2 (bid-ask spread as information asymmetry)
- problem: The interpretation of the bid-ask spread as a measure of adverse selection / trading against better-informed insiders rests on the Glosten-Milgrom/Kyle microstructure literature, which is uncited; bgt2018 is cited only for the post-call window, not for the spread-as-information-asymmetry premise.
- evidence: 'how much outside traders fear trading against better-informed insiders' | only bgt2018 cited nearby
- best fix: Cite a microstructure source (e.g. Glosten-Milgrom) for the adverse-selection reading of the spread, or attribute it to bgt2018 explicitly if they supply it.
- refutation: The spread-as-info-asymmetry reading is textbook and bgt2018 itself uses the spread that way, so the premise is implicitly sourced.  (confidence: low)

### 30. [coherence] low -- narrative-arc inversion: validity results before data section
- location: Sec 2.5 vs Sec 3.1
- problem: Empirical validity RESULTS with coefficients/p-values/N (Tables 5.21, 5.6, 5.7, 5.8, 5.9) are reported in 2.5 inside the 'Conceptual Framework and Empirical Strategy' chapter, BEFORE the five data sources, sampling layers, and summary stats appear in 3.1. Reader meets estimates before the sample.
- evidence: 2.5 reports '0.0001 p<.01 (Table 5.6)' | data/sample only in 3.1 | Table 5.1 after
- best fix: Move the sample description ahead of measure-validation, or relocate validity tables into the empirical chapter.
- refutation: Measurement-validation conventionally sits with construction; partial sample info (2002-2018, non-fin non-util) is given in 2.5.  (confidence: medium)

### 31. [coherence] low -- fragility caveat present in body, absent from summaries
- location: Abstract/Intro/Conclusion vs Sec 3.4
- problem: 3.4 calls the cash-concentration result 'supported but fragile... its significance rides on the imprecise negative stock estimate'. Abstract, intro and conclusion present it as cleanly 'survives a formal pooled test'; they hedge interpretation (concentration not specificity, mechanism open) but omit the statistical-fragility caveat.
- evidence: 3.4 'supported but fragile' | abstract 'survives a formal pooled test' | no fragility in summaries
- best fix: Signal in the conclusion (and maybe abstract) that the difference rests on an imprecise stock null.
- refutation: 'Survives a formal pooled test' is literally true (p=.039); abstracts routinely drop second-order caveats and the interpretive hedge is present.  (confidence: medium)

### 32. [coherence] low -- paper-to-thesis conversion artifacts
- location: throughout (roadmap, all cross-refs)
- problem: Document is a thesis (book class chapters render 'Chapter 1..5'), but prose consistently calls its chapters 'Section 2/3/4/5' and calls itself 'the paper' ('the remainder of the paper proceeds'). Whole-chapter cross-refs mislabel Chapters as Sections; sub-refs (2.3 etc.) are fine.
- evidence: 'Section 2 develops' = Chapter 2 | 'the remainder of the paper' | chapters used throughout
- best fix: Global replace whole-unit 'Section N'->'Chapter N' and 'the paper'->'this thesis'; keep 'Section X.Y'.
- refutation: Usage is consistent so a reader can follow; subsection numbers still resolve correctly.  (confidence: high)

### 33. [coherence] low -- residual under-described in summaries
- location: Abstract, Intro (4th contribution), Conclusion vs Sec 2.3
- problem: Summaries describe UncResCEO as 'the part that remains once each executive's persistent speaking style is removed', but per 2.3 it also nets out UncPreCEO, UncQue, NegCall, performance and year FE. 2.3 reconciles ('removes more...a refinement, not a different object'), so disclosed, but the abstract/conclusion understate what is removed.
- evidence: abstract 'persistent speaking style is removed' | 2.3 'removes more...narrower' | also nets UncPre/UncQue/NegCall
- best fix: Add 'and observable call-level factors' to summary descriptions or cite 2.3.
- refutation: Explicitly reconciled in 2.3; 'net of persistent style' is true if incomplete; standard abstract simplification.  (confidence: medium)

### 34. [coherence] low -- redundant double-reporting of validity coefficients
- location: Sec 2.5 and Sec 4.1 step 1
- problem: CashScrutiny construct-validity coefficients (0.7530**, 0.8519**) are stated in full in 2.5 and again in 4.1 step 1 (both Table 5.9), duplicating the same numbers across two chapters.
- evidence: 2.5 '0.7530...and 0.8519' | 4.1 '0.7530...and 0.8519'
- best fix: In 4.1 reference the 2.5 validity result instead of restating coefficients.
- refutation: 2.5 uses it to motivate the measure, 4.1 as step 1 of a 3-step rule-out; mild and arguably intentional recap.  (confidence: high)

### 35. [coherence] low -- hypothesis verdicts not closed out by label
- location: Sec 3.2 (H1), 3.3 (H1b) vs 3.4 (H1a)
- problem: H1/H1a/H1b are stated (2.2) and mapped to MA1/MA2/MA3 (2.4), but only H1a is named in its results section (3.4). 3.2 and 3.3 never say 'this supports H1 / H1b', leaving those verdicts implicit.
- evidence: 3.4 names 'H1a' | 3.2/3.3 omit H1/H1b | verdicts implicit
- best fix: Add a 'consistent with H1' / 'consistent with H1b' line to 3.2 and 3.3.
- refutation: 2.4's explicit mapping lets the reader connect each result without repeated labels.  (confidence: medium)

### 36. [coherence] low -- loose 'residual-feasible' sample label
- location: Sec 3.2 para 3
- problem: 3.2 calls 1,884 the 'residual-feasible call sample' vs the 2,232-firm cash panel, but the UncResCEO regression runs on 1,248 firms; 1,884 is the full language sample from which residuals are estimated, not the set with usable residuals (N=44,900 of 88,205).
- evidence: '1,884-firm residual-feasible' | UncResCEO reg 1,248 firms | residual N=44,900
- best fix: Call 1,884 the 'language sample'; if contrasting feasibility use 1,248.
- refutation: Directional claim (cash panel broader) holds; 1,884 is the universe residuals derive from, so loosely defensible.  (confidence: low)

### 37. [coherence] low -- AUDIT-AIDS column maps stale (aid, not thesis)
- location: AUDIT-AIDS header for Tables 5.15-5.18 vs rendered tables
- problem: The audit-aid maps describe Tables 5.15-5.18 as combined 'Thesis vs All-Deals' panels (16/4/4/6 data cols), but the rendered tables are all-deals-only (8/2/2/3 cols). E.g. aid says all-deals Wald 0.1056 'is col 4' of 5.18, but 5.18 has 3 cols and 0.1056 is the UncRes col. Thesis PROSE resolves correctly against the actual tables; only the aid is stale.
- evidence: aid '16 data cols' for 5.15 | rendered 5.15 has 8 cols | prose matches actual
- best fix: Disregard/repair the aid maps for 5.15-5.18; rely on rendered tables.
- refutation: Not a thesis-body defect; the comment header does not compile and the prose is internally correct.  (confidence: high)

### 38. [coherence] low -- roadmap omits data section and validity analyses
- location: Intro roadmap vs Sec 3.1 and 2.5
- problem: Roadmap says 'Section 3 presents the three main analyses', but Sec 3 opens with 3.1 Data/Sample (not an analysis); and 'Section 2 develops the conceptual framework and empirical strategy' does not flag that 2.5 houses empirical validity analyses (Tables 5.6-5.9, 5.21).
- evidence: roadmap 'three main analyses' | 3.1 is Data/Sample | validity sits in 2.5
- best fix: Mention the data section and measurement-validation in the roadmap.
- refutation: Roadmaps summarize at chapter granularity; data + validation are subsumed under 'empirical strategy'/'main analyses'.  (confidence: low)

### 39. [coherence] low -- summary-stats role taxonomy loose
- location: Table 5.1 panels A/B/C
- problem: Panels labelled 'A. Independent / B. Dependent / C. Firm Controls', but roles vary: CashScrutiny (Panel A 'Independent') is the DV in Table 5.9; UncResCEO (Panel B 'Dependent') is a regressor in Logit A/B and the bid-ask table; PRisk/EPU (Panel A) are only validity regressors.
- evidence: CashScrutiny 'Independent' but DV in 5.9 | UncResCEO regressor in 5.19/5.20
- best fix: Relabel panels by data type (call-level/firm-level) or note roles vary by analysis.
- refutation: Presentational grouping for a multi-analysis paper; clean role-mapping impossible when a variable serves several models.  (confidence: low)

### 40. [coherence] low -- 'strongest result' superlative vs moderate significance
- location: Intro vs Tables 5.3/5.4
- problem: Intro calls the round-trip 'the study's strongest result', but its discriminating announcement-resolution leg (PRE1-GAP uncertainty drop) is only p<.05 matched (0.0455**) and p<.10 placebo (0.0428*); the run-up itself is p<.01. The superlative leans on the full PRE1-POST swing (0.0723***), not the crux GAP-drop.
- evidence: 'strongest result' | PRE1-GAP 0.0455**/0.0428* | run-up p=.0074
- best fix: Qualify 'strongest' as 'most identifying' or anchor on the 0.0723*** swing.
- refutation: 'Strongest' plausibly means most identifying (two-clocks design rules out cash-persistence stories); full swing is p<.01.  (confidence: low)

### 41. [coherence] low -- conclusion drops the 'one-tailed' qualifier on the bid-ask claim
- location: Conclusion para 3 vs Abstract and Sec 4.2
- problem: Conclusion states 'the scripted presentation is contemporaneously positively associated with it' with no 'one-tailed' qualifier, whereas the abstract ('on one-tailed within-firm tests') and body 4.2 (table note: one-tailed for speech components) both carry it. The conclusion's version is slightly less guarded than the rest.
- evidence: conclusion: 'contemporaneously positively associated' | abstract: 'one-tailed within-firm' | 4.2 one-tailed
- best fix: Add 'on one-tailed tests' (or 'within-firm') to the conclusion sentence to match abstract/body.
- refutation: Conclusions routinely compress qualifiers; 'contemporaneously' is retained, and the claim is not false, only less hedged.  (confidence: medium)

### 42. [coherence] low -- all tables numbered 5.x and placed after the Conclusion
- location: Tables block (after the Conclusion chapter) vs discussion in Ch 2-4
- problem: All 21 tables physically sit after the Conclusion chapter and the references, so they render as Table 5.x (chapter-5/Conclusion numbering) even though discussed throughout Chapters 2-4. Every body table reference is thus a forward reference to material past the conclusion (e.g. Table 5.21 cited in Sec 2.3, Table 5.2 in Sec 3.2), and the 5. prefix mismatches the discussing chapter.
- evidence: tables begin after Conclusion | render Table 5.1 to 5.21 | cited in Ch 2-4
- best fix: Embed each table within its discussing chapter so numbering tracks the chapter, or accept end-placement as a flagged layout choice.
- refutation: Tables-at-end is an accepted manuscript style; numbering is mechanically correct given placement; may be the layout referee remit.  (confidence: high)

### 43. [completeness] low -- leftover placeholder in front matter
- location: Examining Committee page
- problem: Three reader-visible placeholders '[Examiner --- name, affiliation]' remain in the Examining Committee block
- evidence: [Examiner --- name, affiliation] x3
- best fix: Fill examiner names/affiliations before deposit, or note conventionally that they are assigned at defense
- refutation: Examiner names are routinely filled only at/after the defense; expected to be blank in a pre-defense draft  (confidence: high)

### 44. [completeness] low -- asserted-but-unshown bootstrap
- location: Sec 2.3 generated-regressor caveat
- problem: Pagan generated-regressor concern is flagged and the text 'notes that it does not change the descriptive readings', implying a two-step/bootstrap result that is never reported in any table
- evidence: 'together with the bootstrap that would address it' | 'does not change the descriptive readings'
- best fix: Either report the bootstrap SEs or reword to a purely conceptual claim (signs/directions are robust to SE corrections)
- refutation: Load-bearing results are framed descriptively (direction), which an SE correction cannot flip, so the claim is defensible without a table  (confidence: medium)

### 45. [completeness] low -- stale AUDIT-AIDS column maps (meta, non-thesis)
- location: comment header lines 75-87
- problem: The provided column maps describe robustness Tables 5.15-5.18 as Thesis|All-deals blocks (16/4/4/6 cols), but the actual tables contain only the all-deals block (8/2/2/3 cols); prose attributions still resolve correctly to actual cells
- evidence: AID: '16 data cols THESIS vs ALL-DEALS' | actual rob_runup tabular lcccccccc = 8 data cols, 'All deals (stacked)'
- best fix: Audit aid only (does not compile); note for auditors that 5.15-5.18 are all-deals-only and verify prose against actual tables, which checks out
- refutation: AUDIT-AIDS is an explicitly non-compiling comment, not part of the thesis; thesis prose+tables are mutually consistent  (confidence: high)

### 46. [completeness] low -- undefined acronym 'DWZ'
- location: Table 5.10 column header '(DWZ residual)'
- problem: Reader-visible 'DWZ' (in table header) is never expanded; citation key is Dzielinski et al. (2021), and 'DWZ' initials are not introduced in prose
- evidence: '(DWZ residual)' header | prose uses \citet{dwz}=Dzielinski et al.
- best fix: Spell out 'Dzielinski et al. (DWZ)' once, or relabel header
- refutation: Context (citation to Dzielinski et al.) makes the initials inferable  (confidence: medium)

### 47. [completeness] low -- internal label scheme hints at collapsed hypotheses
- location: table labels h11_/h24_/h24b_/h14c_
- problem: Table labels encode an older hypothesis numbering (H11, H24, H24b, H14c) but the reader-visible thesis states only H1/H1a/H1b; the convergent-validity and bid-ask analyses are reframed as 'checks/analyses', so no reader-visible hypothesis is dropped without a verdict
- evidence: label tab:h11_prisk_uncertainty etc. | prose: only H1,H1a,H1b stated
- best fix: None needed for reader (labels invisible); optionally rename labels to avoid confusion
- refutation: Labels are invisible; the reframed analyses each receive an explicit verdict, so completeness of hypothesis<->test is intact  (confidence: high)

### 48. [completeness] low -- more undefined symbols/acronyms
- location: Table 5.12 controls; Tables 5.6-5.8 notes
- problem: StockPrice, Turnover, DailyVola, AbsSurpDec (bid-ask 'Extended Controls', Tab5.12) are never defined in prose or appendices; AbsSurpDec is also distinct from the decomposition's SurpDec; the acronym 'FF12' (industry FE in Tab5.6-5.8 notes) is unexpanded
- evidence: Tab5.12 rows StockPrice/Turnover/DailyVola/AbsSurpDec | note 'industry (FF12)'
- best fix: Define the four microstructure controls in an appendix and expand 'FF12' = Fama-French 12 industries once
- refutation: These are standard market-microstructure controls and FF12 is a near-universal abbreviation; arguably common knowledge  (confidence: high)

### 49. [completeness] low -- hypothesis stated-order vs tested-order
- location: Sec 2.2 vs Ch.3
- problem: Hypotheses are stated H1->H1a->H1b but presented/tested H1->H1b->H1a (MA1/MA2/MA3); the mapping is made explicit so it is not a defect, only a mild ordering wrinkle
- evidence: 2.2 order H1,H1a,H1b | 'MA1 tests H1; MA2 tests H1b; MA3 tests H1a'
- best fix: Optionally reorder the H statements or add a one-line signpost; not required
- refutation: Explicit mapping fully removes ambiguity; many papers present in a different order than stated  (confidence: high)

### 50. [honesty] low -- stock arm labeled 'placebo' against framework
- location: Table captions/notes 5.2, 5.4, 5.17
- problem: Framework states 'we treat the stock deal as a managed comparison rather than an inert placebo', yet several table captions/notes call the stock arm 'placebo', overstating the comparison's cleanness and contradicting the in-text disclaimer.
- evidence: managed comparison rather than an inert placebo | Stock acquirers (placebo) | as a placebo, stock acquirers
- best fix: Relabel the stock column 'stock comparison' to match the prose.
- refutation: 'Placebo arm' is standard DiD terminology for a not-expected-to-respond group.  (confidence: medium)

### 51. [honesty] low -- 'cash-specificity' label vs 'concentration' floor
- location: Sec 3.4 title and result sentences
- problem: Floor #3 mandates 'concentration, not strict specificity', yet the operative noun is repeatedly 'the formal cash-specificity result/test/claim', and one sentence says the table 'delivers the formal cash-specificity result' -- nominally asserting the disclaimed specificity.
- evidence: delivers the formal cash-specificity result | the cash-specificity claim | Main Analysis 3: Cash-Specificity
- best fix: Name it the 'cash-concentration test'; reserve 'specificity' for the null being tested.
- refutation: Body repeatedly hedges ('we keep our wording at concentrated rather than specific'); a 'specificity test' may yield a 'concentration' reading.  (confidence: low)

### 52. [honesty] low -- prose mislabels table's tail convention
- location: Sec 3.2 vs Table 5.2 note
- problem: Prose defends the headline against 'the table's one-tailed reporting convention', but Table 5.2's note marks the stars '(two-tailed)'; the premise contradicts the table. Conservative direction (result holds two-tailed) but an internal inconsistency on the exact tail-reporting axis the floor polices.
- evidence: the table's one-tailed reporting convention | (two-tailed)
- best fix: Drop the false premise: 'the coefficient is significant two-tailed (p=.0074), as the table reports.'
- refutation: May loosely invoke the thesis-wide one-tailed convention (Sec 2.4) rather than Table 5.2 specifically; either way it understates, not overstates.  (confidence: medium)

### 53. [honesty] low -- one-tailed significance reported without local flag
- location: Sec 4.1 scrutiny-gating numbers
- problem: The robustness coefficient 0.0413 (se .0177, t=2.33) is p<.01 only one-tailed (Table 5.11 note: one-tailed for directional terms); two-tailed it is p~.02 (**). Prose reports 'p<.01' with no local one-tailed flag, overstating this rule-out check while the headline run-up is carefully defended two-tailed.
- evidence: 0.0413 ... p<.01 | one-tailed for the directional terms
- best fix: Report 'p<.05 two-tailed' or flag '(one-tailed)' locally, as done for the main run-up.
- refutation: Thesis-wide one-tailed convention disclosed in Sec 2.4; the second column (0.0439**) holds two-tailed so the dissociation survives.  (confidence: medium)

### 54. [honesty] low -- implied robustness to uncorrected generated-regressor SEs
- location: Sec 2.3 generated-regressand caveat
- problem: Says the generated-regressand SE issue 'does not change the descriptive readings we report', citing 'the bootstrap that would address it' in the conditional -- implying robustness to a correction not shown to be run, when corrected SEs could weaken the significance the load-bearing results rely on.
- evidence: bootstrap that would address it | does not change the descriptive readings
- best fix: State only what is shown: 'point estimates are unaffected; corrected SEs may widen, which we have not implemented.'
- refutation: 'Descriptive readings' plausibly means point-estimate patterns, which a generated-regressor correction leaves unchanged; Sec 2.4 reiterates the caveat applies to every design.  (confidence: low)

### 55. [honesty] low -- abstract omits cash-specificity result's fragility
- location: Abstract
- problem: Abstract presents the cash-vs-stock difference as 'a difference that survives a formal pooled test' without the body's caveat that it is 'supported but fragile' and 'rides on the imprecise negative stock estimate'; the abstract reads firmer than the body supports.
- evidence: survives a formal pooled test | supported but fragile
- best fix: Add one hedge: 'survives a formal pooled test, though the difference is fragile.'
- refutation: Abstracts compress; the claim is literally true (p=.039<.05) and fragility is disclosed in Sec 3.4.  (confidence: low)

### 56. [honesty] low -- causal-flavored framing and null read as zero
- location: Sec 4.2 bid-ask
- problem: Research question phrased causally ('whether the speech-uncertainty signal moves the post-call information environment'); the null is then read as 'outsiders do not react to the residual' / 'the residual is inert', stating absence of evidence as evidence of absence.
- evidence: whether the ... signal moves | outsiders do not react to the residual | the residual is inert
- best fix: 'whether the signal is associated with ...'; 'we find no association between the residual and the spread.'
- refutation: Sec 4.2 explicitly disclaims 'not evidence of a precisely estimated zero' and frames the payoff as 'interpretation rather than identification'.  (confidence: low)

### 57. [honesty] low -- 'construct validity carries over' from a re-estimation
- location: Sec 2.5 replication paragraph
- problem: Infers DWZ's 'construct validity ... carries over to our setting' from coefficient similarity; coefficient replication shows the spec reproduces, not that the construct is valid here -- a stronger inference than the evidence, since the thesis's own convergent checks are called 'weak'.
- evidence: construct validity they establish ... carries over | the convergent leg is supportive but weak
- best fix: Soften: 'the specification reproduces; whether the construct is valid here is what the checks below assess.'
- refutation: Same paragraph defers validity to the checks below and never claims the construct is established here.  (confidence: low)

### 58. [honesty] low -- absolute 'not an artifact' from a partialling-out argument
- location: Sec 2.1 (line 295)
- problem: 'our signal is therefore not an artifact of the very tone-management the citations describe' states an absolute negative from a residualization argument (residual is net of UncPreCEO/NegCall). Defensible but the absolute form overclaims what partialling-out can guarantee.
- evidence: not an artifact of the very tone-management
- best fix: Soften to 'is unlikely to be a mechanical artifact of the scripted-channel tone-management'.
- refutation: The residual is genuinely net of scripted presentation and call negativity, so the scripted-tone artifact channel is largely closed by construction.  (confidence: low)

### 59. [methodology] low -- no outlier/winsorization treatment despite extreme control tails
- location: Table 5.1 (l.604-617)
- problem: Several controls show extreme untrimmed tails: sCFO max 32.40, EarnVol max 19.51, FirmMat min -317.57, TobinsQ max 35.61, ROA min -3.98. No winsorization or trimming is mentioned anywhere. Influential outliers in controls (and in the residual first stage) could move coefficients; the thesis is silent on outlier handling.
- evidence: FirmMat min -317.5714 | sCFO max 32.4035
- best fix: State winsorization (e.g. 1/99%) policy, or add a winsorized robustness column.
- refutation: Main MA1 controls (Leverage, lnAssets, TobinsQ, ROA, Capex) are more bounded; FE absorb level outliers; effect sizes are stable across many cuts.  (confidence: medium)

### 60. [methodology] low -- main run-up uses firm-only clustering despite calendar-clustered treatment
- location: Sec 2.4 (l.331) + Table 5.2 notes
- problem: PreAnnounceQtr is concentrated in calendar-time M&A waves, so residuals are likely correlated across firms within a quarter. Main MA1/MA2/MA3 cluster by firm only; only 'some validity tables' use two-way (firm x quarter) clustering. Year-quarter FE absorb common means but not within-quarter cross-firm residual correlation. The headline SE may be understated.
- evidence: 'some validity tables use two-way clustering'
- best fix: Report the headline run-up and Wald with two-way (firm and calendar-quarter) clustering, or note it survives.
- refutation: Year-quarter FE materially mitigate calendar dependence; with ~1,200+ firm clusters firm-clustering is defensible.  (confidence: medium)

### 61. [methodology] low -- generated-regressand caveat absent from the Conclusion limitations list
- location: Conclusion limitations (l.468-470)
- problem: The two-step/generated-regressand SE concern is disclosed in Sec 2 but omitted from the consolidated limitations in the Conclusion, which an examiner often reads as the definitive honesty inventory. The list covers selection, mechanism, word-list, counterfactual, external validity, but not the SE caveat.
- evidence: limitations para omits Pagan/two-step
- best fix: Add one clause to the Conclusion limitations noting the generated-regressand SE caveat and that a bootstrap correction is left to future work.
- refutation: It is disclosed in the methodology, so the thesis as a whole is not silent.  (confidence: medium)

### 62. [methodology] low -- no multiple-testing acknowledgement across 21 tables / many focal tests
- location: throughout Ch.3-4
- problem: Numerous focal tests, several near thresholds (Wald p=.039; PRE1-GAP drop p<.05 / p<.10 across samples; Logit B FE p=.205). No discussion of multiple comparisons or family-wise error. An examiner may push on selective emphasis of the significant cuts.
- evidence: Wald p=.039 | PRE1-GAP p<.10 in placebo cash col
- best fix: Add a sentence noting the inferential burden of multiple tests and that the round-trip (the strongest, p<.01) anchors the claims.
- refutation: The strongest result (peak-to-post 0.0723, p<.01) is robust across every sample, reducing multiple-testing fragility; heavy hedging limits overclaiming.  (confidence: low)

### 63. [methodology] low -- Table 5.12 set in portrait at 13 columns (legibility/oversize risk)
- location: Table 5.12 tab:h14c_ceo2_decomp (l.1135-1190)
- problem: A 13-column (12 data) table is placed in PORTRAIT, scriptsize, inside adjustbox max width=linewidth, while the other wide tables (5.2 run-up = 9 col, 5.15 = 9 col) are in landscape. adjustbox will shrink 12 numeric columns into 6.375in, risking illegibly small type in the final PDF.
- evidence: {lcccccccccccc} not in landscape; 5.2/5.15 use landscape
- best fix: Wrap Table 5.12 in the landscape environment as done for the 9-column tables.
- refutation: adjustbox guarantees no margin overflow, so it compiles; this is a legibility judgement, not a broken table.  (confidence: medium)

### 64. [methodology] low -- convergent validity is near-vacuous yet used to support the construct
- location: Sec 2.5 (l.339) + Tables 5.6/5.7/5.8
- problem: All three convergent checks are one-tailed, economically trivial (PRisk R^2~0.003; coef 0.0001), and the macro EPU/GEPU indices are identified only by within-year aggregate co-movement under year FE (one US-EPU estimate only marginal, p<.10). This is barely evidence the residual measures uncertainty rather than noise; the construct rests mainly on the DWZ replication.
- evidence: 'R^2 approx 0.003' | 'the convergent leg is supportive but weak'
- best fix: Frame convergent validity as corroborative only and lean the construct case on the replication; or add a firm-quarter-level convergent measure.
- refutation: They explicitly concede it is 'supportive but weak' and do not overclaim; the replication carries the main construct-validity weight.  (confidence: medium)

### 65. [methodology] low -- 'scripted presentation is the segment outsiders react to' rests on one-tailed, contemporaneous, 4/6 cols
- location: Sec 4.2 (l.422-424)
- problem: The bid-ask conclusion that UncPreCEO drives the spread is built on one-tailed tests, contemporaneous only, significant in 4 of 6 columns and null in both extended-control industry-FE columns; the between-segment difference is never formally tested. The section-level phrasing is firmer than the evidence.
- evidence: 'one-tailed' | 'insignificant in the two industry-fixed-effect specifications' | 'we do not test the between-segment difference directly'
- best fix: Soften to 'contemporaneously and on one-tailed tests, the scripted presentation is associated...' (the abstract already does this; align the section prose).
- refutation: The abstract and the closing of Sec 4.2 do hedge ('contemporaneous only', 'supportive reading, not proof').  (confidence: low)

### 66. [methodology] low -- no alternative-dictionary / placebo word-list robustness for the core DV
- location: Sec 2.3 measure + Conclusion limitation (l.470)
- problem: The entire dependent variable rests on the single Loughran-McDonald uncertainty list. The conclusion concedes the word-count abstracts from context, but nothing probes sensitivity to an alternative uncertainty dictionary or a placebo (non-uncertainty) word list, which would show the run-up is keyed to uncertainty specifically and not generic word-share dynamics.
- evidence: 'Uncertainty is captured by applying a finance-specific word list'
- best fix: Add a robustness using an alternative uncertainty lexicon and a placebo word list; show the run-up appears for uncertainty and not the placebo.
- refutation: LM is the field-standard list; the residualization nets out persistent style, limiting generic-vocabulary artifacts.  (confidence: medium)

### 67. [numbers] low -- AUDIT-AIDS column map stale for Tables 5.15-5.18
- location: header lines 75-88 vs rendered tables 5.15-5.17
- problem: header describes 16/4/4/6-col 'Thesis vs All-Deals' layout; actual rendered tables are all-deals-only (8/2/2 cols). e.g. claims 0.0391 is col10 but actual table has 8 cols, 0.0391 is Cash/UncR
- evidence: header '16 data cols','0.0391*** is col 10' | table: multicolumn{8}{All deals (stacked)}
- best fix: update audit-aid column maps to all-deals-only layout (non-compiling comment; no PDF impact)
- refutation: AUDIT-AIDS is a non-compiling comment, not thesis body; prose-vs-actual-cell all match, so PDF is correct  (confidence: medium)

### 68. [numbers] low -- deal-rate 2.84% not verifiable from a table cell
- location: Sec 4.5 line 448 / Table 5.19
- problem: 'deal rate of 2.84%' is the DV mean for Logit A but not shown in the table; cannot cross-check against a cell
- evidence: 'deal rate of 2.84%' | Table 5.19 has no DV-mean row
- best fix: none needed if correct; could add DV-mean to table note
- refutation: likely correct internal stat; just not independently checkable from shown cells  (confidence: low)

### 69. [numbers] low -- mixed one/two-tailed convention for SAME PreAnnounceQtr indicator across tables
- location: Table 5.2 vs Table 5.11
- problem: identical pre-announce indicator gets *** two-tailed in 5.2 (0.0461,t=2.68) but *** one-tailed in 5.11 (0.0413,t=2.33 -> two-tailed only **); reader cannot tell standard differs
- evidence: 5.2 note two-tailed | 5.11 note one-tailed for directional | 0.0413/0.0177=2.33 two-tailed p=.0196
- best fix: harmonize focal-test tail convention or label each focal coef's tail inline
- refutation: explicitly disclosed at line 331; both stars are individually correct under their stated tail; structural not an arithmetic error  (confidence: high)

### 70. [style] low -- country-name register (terminology)
- location: Ch3 data section L354/360 vs rest
- problem: Sample country called 'United States' in abstract/intro/framework/conclusion but 'U.S.' in the Ch3 data-section prose (L354 'U.S. public firms', L360 'U.S. public-acquirer')
- evidence: 217/268/337/470 United States | 354/360 U.S.
- best fix: Use 'United States' (the body-prose majority) consistently in Ch3 data section, or standardize to U.S. throughout body
- refutation: 'U.S.' as adjective + 'United States' as noun is a common house style; may be intentional  (confidence: medium)

### 71. [style] low -- raw code variable names in rendered tables
- location: Table 5.1 (L589,593,597,606) and reg tables (L912,935,969,992)
- problem: Reader-facing table labels carry machine column names with underscores and code suffixes (US\_EPU\_log, GEPU\_log, CashRatio\_lag, BGTLevel\_Spread, Lagged\_DV, sCFO, EarnVol, FirmMat) rather than the polished prose notation (US-EPU, GEPU, lagged DV)
- evidence: 593 US\_EPU\_log | 969 GEPU\_log | 935 Lagged\_DV | 597 BGTLevel\_Spread
- best fix: Map raw column names to display labels matching prose (e.g. US-EPU, GEPU, Cash ratio (t-1))
- refutation: Some readers accept verbatim variable codes in tables; underscores are escaped so they render legibly  (confidence: medium)

### 72. [style] low -- table layout/spacing consistency across pipelines
- location: Tables 5.15-5.18 vs 5.2-5.14
- problem: Two table generators produce different micro-layout: bible tables order rows [FE; then Firms/N] with notes \vspace{8pt}; robustness tables order [Firms/N; then FE] with notes \vspace{2pt}
- evidence: 660-664 FE-then-N, vspace8pt | 1350-1353 N-then-FE, vspace2pt
- best fix: Unify row order (FE block then counts) and notes vspace across all tables
- refutation: Reader tolerance for minor layout drift is high; both orders are legible  (confidence: medium)

### 73. [style] low -- cited-author surname diacritic stability
- location: Table 5.21 caption L1599 & notes L1643 vs References L497-498 and all in-text cites
- problem: Surname rendered both 'Dzielin\'ski' (accented, Table 5.21 caption + notes) and 'Dzielinski' (no accent, References entry + every \citet{dwz} in-text render). Same author, two spellings in the rendered PDF
- evidence: 1599 Dzielin\'ski et al. | 498 bib 'Dzielinski, M.' | 35 cite label Dzielinski
- best fix: Pick the correct diacritic and apply to bib \bibitem label + entry so in-text and table agree
- refutation: If the accented form is correct the bib is the error, not the table; either way they must match  (confidence: high)

### 74. [style] low -- parenthetical statistic format (SE vs t)
- location: Table 5.21 (L1611 etc.) vs all other reg tables
- problem: In every other regression table the value in parentheses is a clustered standard error; in Table 5.21 it is a t-statistic (e.g. (24.47),(14.94)). The parenthetical convention flips in one table
- evidence: 1643 notes 't-statistics (in parentheses)' | 671 elsewhere 'Standard errors ... in parentheses'
- best fix: State plainly in 5.21 it reports t-stats (already in notes) or add SE; ideally harmonize to SE for cross-table comparability
- refutation: Disclosed in the table's own notes and matches the replicated DWZ source's reporting; numerically unmistakable as t-stats  (confidence: high)

### 75. [style] low -- math subscript index style
- location: Appendix I/II (L1664,1665,1686,1697) vs Sec 2.4 equations (L317-327)
- problem: Firm-quarter subscript written without comma in the model equations ($Y_{it}$,$X_{it}$,$\varepsilon_{it}$) but with a comma in the appendices ($X_{i,t}$, CashScrutiny$_{i,t}$, HighCashScrutiny$_{i,t}$)
- evidence: 323 X_{it} | 1686 X_{i,t} | 1664 _{i,t}
- best fix: Standardize to one subscript style (the equation block's $_{it}$ is the majority)
- refutation: $i,t$ vs $it$ is universally understood; purely cosmetic  (confidence: high)

### 76. [style] low -- unexpanded acronyms in reader-facing tables
- location: Table 5.21 header 'DWZ (2021)' L1604; Table 5.12 'BGTLevel_Spread' L1144; notes 'FF12' L893
- problem: Acronyms DWZ, BGT, FF12 appear in column heads/labels/notes but are never expanded in rendered prose (in-text cites render full author names, never the initials). Reader must infer DWZ=Dzielinski-Wagner-Zeckhauser, BGT=Bushee-Gow-Taylor, FF12=Fama-French 12
- evidence: 1604 'DWZ (2021)' | 1144 BGTLevel_Spread | 893 'industry (FF12)'
- best fix: Expand at first table use, e.g. 'Dzielinski et al. (2021)' as the 5.21 header, 'Fama-French 12 industries' in notes
- refutation: DWZ surnames appear in 5.21 notes; BGT/FF12 are finance-standard shorthands many readers know  (confidence: medium)

### 77. [style] low -- signed-zero artifact
- location: prose L362,L410; Table 5.21 L1621; tables 5.7/5.8 adj R2 L944/L1001
- problem: Negative zero printed: '$-0.0000$' (residual mean L362; scrutiny effect L410), '$-0.000$' (StockRet L1621), '-0.000' (Adj. R^2 L944/1001) -- a rounding/formatting artifact of a near-zero or slightly-negative value
- evidence: 362 mean $-0.0000$ | 944 Adj R2 -0.000
- best fix: Render exact/near zeros as '0.0000' (or report adj-R2 as 0.00) to avoid a minus sign on zero
- refutation: $-0.0000$ faithfully signals a tiny negative that rounds to zero; negative adj-R2 is a real computed value, not an error  (confidence: low)

### 78. [style] low -- Tobin's Q typography
- location: L358 vs L1700 vs table rows (e.g. L649)
- problem: Same construct rendered three ways: 'Tobin's~Q' (upright Q, prose L358), 'Tobin's $Q$' (math-italic Q, appendix L1700), and 'TobinsQ' (bare, table rows). A concrete instance of the variable-typography non-uniformity
- evidence: 358 Tobin's~Q | 1700 Tobin's $Q$ | 649 TobinsQ
- best fix: Pick one (e.g. 'Tobin's $Q$' in prose+appendix, label 'Tobin's Q' in tables) and apply uniformly
- refutation: Upright vs italic Q is subtle; many readers won't notice  (confidence: high)

### 79. [style] low -- round-trip compound hyphenation
- location: L270,L428 vs L384,L386,L432,L450
- problem: 'round-trip' hyphenated as a modifier (L270 'round-trip contrast', L428 'round-trip contrasts') but 'round trip' two words as a noun (L384,386,432,450)
- evidence: 270 round-trip | 384 round trip
- best fix: If desired fix one form; otherwise leave -- current usage already follows the modifier-hyphenation rule
- refutation: This is standard correct English: hyphenate the compound modifier, not the standalone noun -- likely not an error at all  (confidence: low)

## Completeness sweeps
- [citations] Verified all \citet/\citep/\citeauthor resolve (22 keys<->22 bibitems, 1:1, no orphans/danglers), header-map vs bibitem author-year/et-al consistency, table \ref resolution, and EPU/GEPU split. NOT audited (out of citation dimension; flag to other referees): external ACCURACY of every attributed claim (impossible from this self-contained file -- see ~24 external-attribution checklist items); hardcoded section cross-refs (Section 2.3/4.1/2.5 etc.) and Appendix I/II name-refs are typed text not \ref, so their numbering correctness is a consistency-referee matter; the prose 'two-way clustering' claim vs firm-only clustering in table notes (Finding F) is a methods-referee matter; DWZ R2 wording 0.36 vs 0.364 and other in-text numbers belong to the numbers referee. Residual risk: a \cite buried inside an adjustbox/longtable cell I read as data, and whether natbib would actually compile the non-alphabetical manual bibitem labels without warning (cannot run LaTeX here).
- [coherence] Verified the full arc (abstract<->body<->conclusion), the H1/H1a/H1b -> MA1/MA2/MA3 -> results mapping, the two-clocks thread, register consistency, headline-number consistency, and roadmap-vs-structure; no high-severity contradiction exists. Residual risk: (1) paragraph-level transitions inside the dense theory paragraphs (2.1, 2.3, 2.5) were spot-checked, not exhaustively traced sentence-by-sentence, so a subtle non-sequitur there could remain; (2) numeric prose-vs-table agreement was checked only for narrative-bearing headline cells, leaving exhaustive cell-by-cell verification to the numbers referee; (3) table-placement/numbering and Section-vs-Chapter labeling straddle the layout referee remit and are recorded here as cohesion items; (4) bibliography completeness (each citet has a bibitem) was assumed from the AUDIT-AIDS cite map, not re-derived.
- [completeness] Source-only audit (no compile): could NOT verify rendered TOC / List-of-Tables ordering, page numbering, or that table float placement matches the 5.1-5.21 numbering a reader sees -- assumed from labels+AUDIT-AIDS. Numeric DATA integrity (e.g. near-identical 5.7/5.8 control coeffs, whether reported SEs/p-values are arithmetically correct) is out-of-dimension and left to the stats/numbers referee. I verified hypothesis->test->verdict (H1/H1a/H1b all stated, tested, judged; no reader-visible H dropped), roadmap delivery (Ch3 three analyses, Ch4 five subsections, 'three checks'/'three steps'), all 21 table refs resolve and are cited, 22=22 bibliography, and spot-checked prose<->cell numbers across 3.2-4.5. Residual risk: undefined non-focal controls (FirmMat/EarnVol/StockPrice/Turnover/DailyVola/AbsSurpDec/FF12) and the false 'all variables defined'/'catalogued in the Appendix' promises are the main completeness gaps; a subtle cross-ref I may have under-weighted is whether every 'Section N' truly maps to the intended chapter in every instance.
- [honesty] Covered all 8 locked floor items across every section + tables/captions/notes. Possible residual gaps: (1) I judged tail-convention honesty mostly via the AUDIT-AIDS notes and spot t-stat recomputation, not a full recompute of every starred coefficient's one- vs two-tailed status, so other one-tailed-dependent stars in the validity tables (5.6-5.9, 5.12) may carry the same under-flag as Finding 6; (2) I did not independently re-derive any reported magnitude/SD-share beyond a few headline checks, so an arithmetic overclaim hidden inside prose could remain (out of my honesty charter but adjacent); (3) 'tracks'/'anticipatory trace of an acquisition' is the central interpretive verb -- I judged it correlational and within bounds, but a maximally hostile referee could read directional attribution into it; (4) front-matter (title 'Cash Got Your Tongue?', keywords, JEL) judged non-overclaiming. No high-severity honesty breach found; the floor holds, with two medium de-hedges (causal 'raises'; flat 'unmanaged') and the 'rule out' framing as the main exposures.
- [methodology] Read all 1714 lines (prose + 21 tables + bib + appendices). Verified focal t/p/SD arithmetic (reconciles), causal-hedging discipline (sound, even over-hedged), DWZ replication and dynamic-panel handling (clean). Top threats: (1) generated-regressand SEs asserted-not-corrected under load-bearing significance; (2) 'placebo' stock arm is a tone-managed comparison whose negative beta_s inflates the cash-specificity Wald. Plus undefined variables (FirmMat/EarnVol/HighCash/bid-ask extended controls), unreported cash-vs-stock deal counts, undisclosed bid-ask DV scaling, a tailedness footnote/prose contradiction, and Table 5.12 oversize-in-portrait. NOT independently checkable from this file alone: actual first-stage regression code, whether the bootstrap was ever run, true DV units, winsorization in the data pipeline, and every cell of the 12-col bid-ask table (verified only the rows quoted in prose). Did not exhaustively re-derive every control coefficient in all 21 tables; focused on focal estimands and cross-references.
- [numbers] Cross-checked every prose number vs its exact cell in all 21 tables; recomputed all economic effects (coef/SD, %-of-mean), all bin drops, all Wald=beta_c-beta_s and their SEs, derived p-values from t-stats, and Table 5.1 monotonicity/mean-in-range for all 26 rows. Could NOT independently verify auxiliary stats absent from any cell: deal rate 2.84%, exact deal counts, the 25-trading-day BGT window, and the convergent-validity within-year co-movement claims. DWZ Table 5.21 reports t-stats not SEs, so I verified stars<->t but not coefficient magnitudes against the external source (external lookups barred). First-stage residualization coefficients beyond Table 5.21 are not shown. p-values use normal approx; exact clustered-t df could nudge borderline cases (none flipped). Sub-0.0001 prose/table gaps treated as rounding from unrounded inputs; raw data not available to confirm rounding direction. Front-matter TOC/List-of-Tables page numbers out of numeric charter and not resolvable. Worst issue found: line 368 mislabels two-tailed Table 5.2 as one-tailed (medium); no high-severity numeric error.
- [style] Audited from LaTeX source, not a compiled PDF, so rendered typography (upright vs italic; \mathrm/\mathit/\textit/bare) was inferred from macros -- subtle visual artifacts (margin overflow, widows/orphans, italic-correction, caption line-breaks) are UNVERIFIED. Spot-checked but not exhaustively audited: number style (spelled-out 'fifteen percent' L372 vs numeric '15.3%' coexist by design), quotation-mark style (backtick-apostrophe singles, e.g. L289 'uncertainty' list), Oxford-comma usage, title-case of table captions and the H1/H1a/H1b hypothesis-label formatting, and hyphenation of non-/stock-for-stock/cash-to-assets compounds (looked uniform). Numeric-value correctness and ref/citet target accuracy belong to other referees. Strongest confirmed style issues: variable-name typography split (mathrm/mathit/textit/bare), construct-abbreviation drift in Tables 5.15-5.18 (UncR/UncRes, CshR/CashR), dash-style split (en vs em), p-value L331 leading-zero, SE 5dp prose vs 4dp tables, and 'Section N' refs to chapters.