# THESIS FINAL AUDIT REPORT (1 panel x 7 referees, merged from JSONL)

## Coverage
- referees reported: citations_A, completeness_A, honesty_A, methodology_A, numbers_A, style_A
- malformed/partial lines skipped: 10

## Counts
- HIGH 0 | MEDIUM 17 | LOW 17 | total 34 | clean-bills 39

## HIGH severity (0)

## MEDIUM severity (17)

### 1. [citations] medium -- reference-list-ordering
- location: References (thebibliography, ch. after Conclusion)
- problem: Author-year reference list is not in a single alphabetical sequence. Entries 1-11 are alphabetical (Baker..Thewissen), then the list restarts the alphabet at Bertrand and runs a second un-merged block (Bertrand, Dye, Harford, Hollander, Keown, Verrecchia, Bates, Louis, Opler, Pagan, Shleifer) -- and even within it Verrecchia precedes Bates.
- evidence: Thewissen(2024) then Bertrand(2003) | Verrecchia(1983) then Bates(2009)
- best fix: Re-sort all 22 ibitem entries into one alphabetical-by-first-author sequence (standard for author-year/natbib).
- refutation: Citations still resolve by key regardless of print order; some templates tolerate citation-order lists, though authoryear convention is alphabetical.  (confidence: high)

### 2. [completeness] medium -- roadmap pointer unfulfilled (control catalog)
- location: Section 2.5 final paragraph + Appendices I/II
- problem: prose says the Section-2.3 decomposition controls are 'catalogued in the Appendix', but no appendix lists them (App I=cash scrutiny, App II=firm-financial controls + CashRatio only)
- evidence: 'controls from the Section~2.3 decomposition...catalogued in the Appendix' | App II lists only Leverage..sCFO,CashRatio
- best fix: add SurpDec/EPSgrowth/StockRet/MarketRet/NegCall defs to an appendix or repoint to Sec 2.3
- refutation: they are named in Sec 2.3 and appear in Table 5.21, just not formally catalogued  (confidence: high)

### 3. [honesty] medium -- causal verb in plain-language gloss
- location: Sec 4.1 reason-gating paragraph
- problem: De-hedged gloss uses a transitive causal verb in a strictly-correlational thesis (floor #1 forbids any causal verb): 'the reason for the deal raises uncertainty' attributes causation; 'amplify' frames the interaction causally. Milder second instance 'the uncertainty raised in the run-up' (Sec 3.3).
- evidence: the reason for the deal raises uncertainty | does not amplify the reason | uncertainty raised in the run-up
- best fix: Use associational verb: 'the pre-announcement quarter is associated with higher uncertainty; cash scrutiny is not, and does not interact with it.'
- refutation: Same sentence ends '...and correlational'; 'raises' may be loose shorthand and the surrounding frame is associational.  (confidence: medium)

### 4. [honesty] medium -- 'rule out' overclaims a null
- location: Intro; Sec 4.1 title and first sentence
- problem: 'We also rule out the most immediate alternative', section title 'Ruling Out Analyst Scrutiny', and 'We rule it out in three steps' assert elimination of the scrutiny confound, contradicted by the section's own landing: 'a failure to find ... not a powered equivalence test that could formally rule an effect out.'
- evidence: We also rule out the most immediate alternative | We rule it out in three steps | not a powered equivalence test
- best fix: Retitle 'Assessing the Analyst-Scrutiny Alternative'; replace 'rule out' with 'fail to find support for'.
- refutation: Each 'rule out' is narrowed locally ('does not account for this run-up, not that scrutiny never matters'); net claim lands honest.  (confidence: medium)

### 5. [methodology] medium -- outlier handling / winsorization
- location: Table 5.1 summary_stats; Sec 3.1; App II
- problem: No winsorization documented anywhere; summary stats show wild un-trimmed outliers in controls used by OLS
- evidence: FirmMat min -317.57 | sCFO max 32.40 | EarnVol max 19.51 | ROA min -3.98 | Leverage max 3.95
- best fix: State winsorization policy (e.g. 1/99%) and add a winsorized-robustness column; bid-ask ROA coef -9 to -12 is outlier-exposed
- refutation: Focal DVs UncResCEO and CashRatio are naturally bounded, so headline coefficients may be insensitive; outliers mainly threaten controls/validity tables  (confidence: high)

### 6. [methodology] medium -- typesetting / oversized table
- location: Table 5.12 (tab:h14c_ceo2_decomp)
- problem: 13-column (l+12) bid-ask table set in PORTRAIT at scriptsize under adjustbox max-width; will be scaled to ~3-4pt, effectively unreadable
- evidence: 12 data cols portrait | scriptsize + adjustbox | comparable 8/16-col tables ARE landscaped
- best fix: Put in landscape like Tables 5.2/5.15, or split into contemporaneous vs lead panels
- refutation: adjustbox keeps it on-page and technically compiles; not malformed, only cramped  (confidence: high)

### 7. [methodology] medium -- undefined variables / broken appendix promise
- location: Tables 5.6-5.8; Sec 2.5 line 343; Sec 3.1 line 358; App I/II
- problem: FirmMat and EarnVol appear as regressors in validity tables but are defined nowhere; prose promises DWZ first-stage controls 'catalogued in the Appendix' but App II lists only the 7 firm-financial controls
- evidence: FirmMat/EarnVol in 5.6-5.8 | App II omits NegCall,UncQue,SurpDec,EPSgrowth,StockRet,MarketRet | 'catalogued in the Appendix'
- best fix: Add definitions for FirmMat, EarnVol and the DWZ first-stage controls to an appendix
- refutation: FirmMat/EarnVol are only in convergent-validity tables, not the headline designs; reader can infer 'firm maturity'/'earnings volatility'  (confidence: high)

### 8. [methodology] medium -- generated-regressand SE correction flagged but not executed
- location: Sec 2.3 line 319; Sec 2.4 line 331; Tables 5.19-5.20
- problem: Two-step (Pagan) SE correction/bootstrap is named but never run; reassurance 'does not change the descriptive readings' is asserted, not demonstrated; in Logit A/B UncResCEO is a genuine generated REGRESSOR (the case Pagan addresses) yet the caveat is not repeated there
- evidence: 'flag the concern, together with the bootstrap' | p=.0074 headline on generated DV | Logit A/B RHS UncResCEO, no caveat at Sec 4.5
- best fix: Run the block-bootstrap two-step SEs (or report them for the headline and the logits) rather than only naming them
- refutation: Headline survives across many specs (all-deals 0.0391 p<.01); for a generated regressand added noise often inflates SEs (conservative), so correction may not weaken it  (confidence: medium)

### 9. [methodology] medium -- pre-trend assessed with a single lead
- location: Sec 3.3; Table 5.3 (empire_drop_matched)
- problem: Only PRE2 (e=-2) is shown as a pre-trend check; all e<=-3 are folded into the baseline, so a slow multi-quarter ramp toward the deal would be absorbed into baseline and make PRE1 look like a discrete jump
- evidence: bins PRE2,PRE1,GAP,POST only | baseline = e<=-3 + never-acquirers | 'clean pre-trend'
- best fix: Show e=-4,-3,-2 leads (not just PRE2) to demonstrate flat pre-period
- refutation: They disclaim parallel trends and make no causal claim; PRE2~0 plus the announcement-timed reversal is suggestive of a discrete event  (confidence: medium)

### 10. [methodology] medium -- claim stronger than design: 'readable/observable' signal
- location: Abstract; Conclusion line 466; Table 5.19
- problem: Calls the signal 'readable' / 'a signature researchers can observe before the announcement', but its own forward predictive model has near-zero fit (LPM R2 0.006, pseudo-R2 0.026), i.e. not practically detectable
- evidence: 'readable, anticipatory trace' | Logit A pseudo-R2 0.026 | LPM R2 0.006
- best fix: Soften 'readable/observable' to a within-firm statistical elevation; note predictive content is trivial
- refutation: 'in principle' hedges line 466; claim is a within-firm mean shift, not a cross-sectional classifier  (confidence: medium)

### 11. [methodology] medium -- cash-specificity label overclaims vs design
- location: Sec 3.4 title; Table 5.5 caption ('Cash-Specificity Test')
- problem: Section and table are titled 'Cash-Specificity' while the prose retreats to 'concentration, not strict specificity'; worse, by their own 'unmanaged window' logic the cash>stock gap is equally consistent with pure stock-side suppression (no cash-specificity at all)
- evidence: title 'Cash-Specificity Test' | prose 'concentration rather than strict specificity' | 'cash deal as the relatively unmanaged window'
- best fix: Retitle to 'Cash-vs-Stock Concentration'; state the gap cannot separate cash-trigger from stock-suppression
- refutation: Prose repeatedly hedges to concentration and discloses reliance on the imprecise negative stock estimate  (confidence: medium)

### 12. [methodology] medium -- asymmetric one-tailed reporting
- location: Tables 5.6-5.9, 5.11, 5.12 notes; Sec 2.4 line 331
- problem: Headline run-up is reported two-tailed (conservative) but the supporting validity/secondary results are one-tailed (liberal); several flip to insignificant two-tailed, so the weakest evidence gets the most permissive test
- evidence: US-EPU col3 0.0123* one-tailed | bid-ask UncPreCEO col6 0.1644* one-tailed | 'one-tailed for the independent variable'
- best fix: Report validity/secondary tests two-tailed too, or justify the directional prior per table; flag which survive
- refutation: Directional priors exist (convergent measures, BGT obfuscation); one-tailedness is disclosed in notes and even the abstract  (confidence: medium)

### 13. [methodology] medium -- construct-validity vs central interpretation
- location: Sec 2.6; Sec 4.2; Table 5.6; abstract
- problem: The residual is inert on every external dimension (DWZ: no price/volume link; here: no bid-ask link; convergent R2~0.003) yet the whole thesis interprets its one active result as 'uncertainty'; the tension is disclosed piecewise but never assembled into a single 'the construct is weak, the spike could be a call-language artifact' statement
- evidence: PRisk R2~0.003 'economically trivial' | residual 'inert' on spread | 'supportive but weak'
- best fix: Add a consolidated construct-risk caveat acknowledging the spike may not reflect 'uncertainty' specifically
- refutation: Each weakness is individually disclosed; round-trip reversal and survival under controls argue the spike is not pure noise  (confidence: medium)

### 14. [numbers] medium -- tail-convention prose-vs-table mismatch
- location: Sec 3.2 line 368 vs Table 5.2 note
- problem: prose calls it 'the table's one-tailed reporting convention' but Table 5.2 note says '(two-tailed)' and stars are two-tailed
- evidence: 'table's one-tailed reporting convention' | Table 5.2 note '(two-tailed)' | ROA stock 0.0075* t=1.83 is * two-tailed not ** one-tailed
- best fix: reword to 'two-tailed' or drop the one-tailed framing for this table
- refutation: may be loose wording referring to the thesis-wide focal-test convention rather than this table; *** holds either way  (confidence: medium)

### 15. [style] medium -- p-value format / no-leading-zero
- location: Sec 2.4 methodology, line 331
- problem: Same statistic written two incompatible ways: $p = 0.0074$ (leading zero + spaces) at line 331 vs $p=.0074$ (no leading zero, no spaces) at line 368; line 331 is the ONLY leading-zero p-value in the whole doc
- evidence: 331 $p = 0.0074$ | 368 $p=.0074$ same number | all other p: $p<.0 / $p=.0
- best fix: Change line 331 to $p=.0074$ to match the document-wide no-leading-zero convention
- refutation: Leading zero is defensible APA-side, but doc's own dominant style is no-leading-zero so 331 is the outlier  (confidence: high)

### 16. [style] medium -- dash style uniformity
- location: Ch2 (lines ~287-343) vs Abstract/Intro/Ch3-4
- problem: Two parenthetical-dash styles coexist: spaced en-dash ' -- ' (33x, concentrated in Ch2) vs unspaced em-dash '---' (in abstract L217, intro L278, Ch3-4 L354-388). One device, two renderings
- evidence: 287 'be -- a probability' | 217 'uncertainty---the part' | 354 'paid for---keeping'
- best fix: Normalize all interruptive dashes to one form (em-dash '---' is the majority register in body sections); convert Ch2 ' -- ' accordingly
- refutation: Both are valid typographically; only a problem because the same doc mixes them  (confidence: high)

### 17. [style] medium -- construct-name synonym drift across tables
- location: Tables 5.15-5.18 (L1330,1366,1420,1472) vs Tables 5.2-5.14
- problem: Same constructs abbreviated inconsistently in all-deals robustness tables: UncResCEO->'UncRes'(5.16,5.18)/'UncR'(5.15); CashRatio->'CashR'(5.16,5.18)/'CshR'(5.15); CashScrutiny->'CshSc'; HighCashScrutiny->'HiSc' -- while main tables spell them out. Two abbreviation schemes even within the robustness block; Table 5.15 needs an ad-hoc notes glossary
- evidence: 1330 'CshR & UncR & CshSc & HiSc' | 1366 'UncRes & CashR' | 1355 glossary 'CshR=CashRatio(+lag)'
- best fix: Use the full construct names (UncResCEO, CashRatio, CashScrutiny, HighCashScrutiny) as column heads in 5.15-5.18, matching 5.2-5.14
- refutation: Abbreviations save width in landscape 8-col tables; glossary is provided -- but the two schemes (CshR vs CashR) are indefensible  (confidence: high)

## LOW severity (17)

### 1. [citations] low -- borrowed-method-uncited
- location: Table notes 5.6/5.7/5.8 + cash_scrutiny tables ('industry (FF12)')
- problem: The Fama-French 12-industry (FF12) classification is used as a fixed-effect grouping in multiple tables but Fama and French (1997) is never cited; no bibitem exists for it.
- evidence: notes: 'industry (FF12)' | no Fama-French bibitem
- best fix: Add a Fama-French (1997) reference and cite it at first use of FF12, or define FF12 in the Appendix with the source.
- refutation: FF12 is a near-universal, off-the-shelf scheme often left uncited; not a claim of novelty.  (confidence: medium)

### 2. [citations] low -- borrowed-method-uncited
- location: Sec 4.4 (Robustness: dynamic term), 'subject to the Nickell bias'
- problem: 'Nickell bias' is invoked by name to justify the static-FE robustness check, but Nickell (1981) is not cited and has no bibitem.
- evidence: 'subject to the Nickell bias' | no Nickell bibitem
- best fix: Cite Nickell (1981) at the phrase, or attribute the dynamic-panel-bias point to a cited source.
- refutation: 'Nickell bias' is a textbook eponym econometricians read without a cite; pagan1984 already covers the generated-regressor caveat (different issue).  (confidence: medium)

### 3. [citations] low -- prose-vs-table-claim (cross-referee flag)
- location: Sec 2.4 disclosure para vs validity table notes 5.6-5.10
- problem: Prose states 'some validity tables use two-way clustering, by firm and by calendar quarter', but every validity table note actually reads 'Standard errors clustered by firm' only -- no table reports two-way clustering.
- evidence: prose: 'two-way clustering, by firm and by calendar quarter' | all notes: 'clustered by firm'
- best fix: Reconcile: either correct the prose to 'clustered by firm throughout' or update the relevant table notes if two-way clustering was in fact used.
- refutation: This is a methods/consistency issue, not citation/attribution -- likely belongs to the numbers/consistency referee, not this dimension.  (confidence: medium)

### 4. [honesty] low -- stock arm labeled 'placebo' against framework
- location: Table captions/notes 5.2, 5.4, 5.17
- problem: Framework states 'we treat the stock deal as a managed comparison rather than an inert placebo', yet several table captions/notes call the stock arm 'placebo', overstating the comparison's cleanness and contradicting the in-text disclaimer.
- evidence: managed comparison rather than an inert placebo | Stock acquirers (placebo) | as a placebo, stock acquirers
- best fix: Relabel the stock column 'stock comparison' to match the prose.
- refutation: 'Placebo arm' is standard DiD terminology for a not-expected-to-respond group.  (confidence: medium)

### 5. [honesty] low -- 'cash-specificity' label vs 'concentration' floor
- location: Sec 3.4 title and result sentences
- problem: Floor #3 mandates 'concentration, not strict specificity', yet the operative noun is repeatedly 'the formal cash-specificity result/test/claim', and one sentence says the table 'delivers the formal cash-specificity result' -- nominally asserting the disclaimed specificity.
- evidence: delivers the formal cash-specificity result | the cash-specificity claim | Main Analysis 3: Cash-Specificity
- best fix: Name it the 'cash-concentration test'; reserve 'specificity' for the null being tested.
- refutation: Body repeatedly hedges ('we keep our wording at concentrated rather than specific'); a 'specificity test' may yield a 'concentration' reading.  (confidence: low)

### 6. [honesty] low -- prose mislabels table's tail convention
- location: Sec 3.2 vs Table 5.2 note
- problem: Prose defends the headline against 'the table's one-tailed reporting convention', but Table 5.2's note marks the stars '(two-tailed)'; the premise contradicts the table. Conservative direction (result holds two-tailed) but an internal inconsistency on the exact tail-reporting axis the floor polices.
- evidence: the table's one-tailed reporting convention | (two-tailed)
- best fix: Drop the false premise: 'the coefficient is significant two-tailed (p=.0074), as the table reports.'
- refutation: May loosely invoke the thesis-wide one-tailed convention (Sec 2.4) rather than Table 5.2 specifically; either way it understates, not overstates.  (confidence: medium)

### 7. [honesty] low -- one-tailed significance reported without local flag
- location: Sec 4.1 scrutiny-gating numbers
- problem: The robustness coefficient 0.0413 (se .0177, t=2.33) is p<.01 only one-tailed (Table 5.11 note: one-tailed for directional terms); two-tailed it is p~.02 (**). Prose reports 'p<.01' with no local one-tailed flag, overstating this rule-out check while the headline run-up is carefully defended two-tailed.
- evidence: 0.0413 ... p<.01 | one-tailed for the directional terms
- best fix: Report 'p<.05 two-tailed' or flag '(one-tailed)' locally, as done for the main run-up.
- refutation: Thesis-wide one-tailed convention disclosed in Sec 2.4; the second column (0.0439**) holds two-tailed so the dissociation survives.  (confidence: medium)

### 8. [honesty] low -- implied robustness to uncorrected generated-regressor SEs
- location: Sec 2.3 generated-regressand caveat
- problem: Says the generated-regressand SE issue 'does not change the descriptive readings we report', citing 'the bootstrap that would address it' in the conditional -- implying robustness to a correction not shown to be run, when corrected SEs could weaken the significance the load-bearing results rely on.
- evidence: bootstrap that would address it | does not change the descriptive readings
- best fix: State only what is shown: 'point estimates are unaffected; corrected SEs may widen, which we have not implemented.'
- refutation: 'Descriptive readings' plausibly means point-estimate patterns, which a generated-regressor correction leaves unchanged; Sec 2.4 reiterates the caveat applies to every design.  (confidence: low)

### 9. [honesty] low -- abstract omits cash-specificity result's fragility
- location: Abstract
- problem: Abstract presents the cash-vs-stock difference as 'a difference that survives a formal pooled test' without the body's caveat that it is 'supported but fragile' and 'rides on the imprecise negative stock estimate'; the abstract reads firmer than the body supports.
- evidence: survives a formal pooled test | supported but fragile
- best fix: Add one hedge: 'survives a formal pooled test, though the difference is fragile.'
- refutation: Abstracts compress; the claim is literally true (p=.039<.05) and fragility is disclosed in Sec 3.4.  (confidence: low)

### 10. [honesty] low -- causal-flavored framing and null read as zero
- location: Sec 4.2 bid-ask
- problem: Research question phrased causally ('whether the speech-uncertainty signal moves the post-call information environment'); the null is then read as 'outsiders do not react to the residual' / 'the residual is inert', stating absence of evidence as evidence of absence.
- evidence: whether the ... signal moves | outsiders do not react to the residual | the residual is inert
- best fix: 'whether the signal is associated with ...'; 'we find no association between the residual and the spread.'
- refutation: Sec 4.2 explicitly disclaims 'not evidence of a precisely estimated zero' and frames the payoff as 'interpretation rather than identification'.  (confidence: low)

### 11. [honesty] low -- 'construct validity carries over' from a re-estimation
- location: Sec 2.5 replication paragraph
- problem: Infers DWZ's 'construct validity ... carries over to our setting' from coefficient similarity; coefficient replication shows the spec reproduces, not that the construct is valid here -- a stronger inference than the evidence, since the thesis's own convergent checks are called 'weak'.
- evidence: construct validity they establish ... carries over | the convergent leg is supportive but weak
- best fix: Soften: 'the specification reproduces; whether the construct is valid here is what the checks below assess.'
- refutation: Same paragraph defers validity to the checks below and never claims the construct is established here.  (confidence: low)

### 12. [methodology] low -- differential-timing contrast partly informal/mechanical
- location: Sec 3.3; Table 5.3
- problem: The 'two different clocks' centerpiece compares a significant within-uncertainty drop against a non-significant within-cash drop across two different-scaled outcomes (no cross-equation test), and the cash leg is admitted 'partly mechanical' (cash held until paid)
- evidence: 'two paths running on different clocks' | cash leg 'partly mechanical' | no cross-outcome restriction
- best fix: State explicitly that the contrast is each-outcome-within-itself, not a tested cross-outcome difference; foreground that the substantive leg is uncertainty only
- refutation: Each outcome's drop is a within-outcome Wald test at a different bin, so 'different clocks' is supported per-outcome; mechanical nature is disclosed  (confidence: medium)

### 13. [numbers] low -- AUDIT-AIDS column map stale for Tables 5.15-5.18
- location: header lines 75-88 vs rendered tables 5.15-5.17
- problem: header describes 16/4/4/6-col 'Thesis vs All-Deals' layout; actual rendered tables are all-deals-only (8/2/2 cols). e.g. claims 0.0391 is col10 but actual table has 8 cols, 0.0391 is Cash/UncR
- evidence: header '16 data cols','0.0391*** is col 10' | table: multicolumn{8}{All deals (stacked)}
- best fix: update audit-aid column maps to all-deals-only layout (non-compiling comment; no PDF impact)
- refutation: AUDIT-AIDS is a non-compiling comment, not thesis body; prose-vs-actual-cell all match, so PDF is correct  (confidence: medium)

### 14. [style] low -- country-name register (terminology)
- location: Ch3 data section L354/360 vs rest
- problem: Sample country called 'United States' in abstract/intro/framework/conclusion but 'U.S.' in the Ch3 data-section prose (L354 'U.S. public firms', L360 'U.S. public-acquirer')
- evidence: 217/268/337/470 United States | 354/360 U.S.
- best fix: Use 'United States' (the body-prose majority) consistently in Ch3 data section, or standardize to U.S. throughout body
- refutation: 'U.S.' as adjective + 'United States' as noun is a common house style; may be intentional  (confidence: medium)

### 15. [style] low -- parenthetical statistic format (SE vs t)
- location: Table 5.21 (L1611 etc.) vs all other reg tables
- problem: In every other regression table the value in parentheses is a clustered standard error; in Table 5.21 it is a t-statistic (e.g. (24.47),(14.94)). The parenthetical convention flips in one table
- evidence: 1643 notes 't-statistics (in parentheses)' | 671 elsewhere 'Standard errors ... in parentheses'
- best fix: State plainly in 5.21 it reports t-stats (already in notes) or add SE; ideally harmonize to SE for cross-table comparability
- refutation: Disclosed in the table's own notes and matches the replicated DWZ source's reporting; numerically unmistakable as t-stats  (confidence: high)

### 16. [style] low -- unexpanded acronyms in reader-facing tables
- location: Table 5.21 header 'DWZ (2021)' L1604; Table 5.12 'BGTLevel_Spread' L1144; notes 'FF12' L893
- problem: Acronyms DWZ, BGT, FF12 appear in column heads/labels/notes but are never expanded in rendered prose (in-text cites render full author names, never the initials). Reader must infer DWZ=Dzielinski-Wagner-Zeckhauser, BGT=Bushee-Gow-Taylor, FF12=Fama-French 12
- evidence: 1604 'DWZ (2021)' | 1144 BGTLevel_Spread | 893 'industry (FF12)'
- best fix: Expand at first table use, e.g. 'Dzielinski et al. (2021)' as the 5.21 header, 'Fama-French 12 industries' in notes
- refutation: DWZ surnames appear in 5.21 notes; BGT/FF12 are finance-standard shorthands many readers know  (confidence: medium)

### 17. [style] low -- signed-zero artifact
- location: prose L362,L410; Table 5.21 L1621; tables 5.7/5.8 adj R2 L944/L1001
- problem: Negative zero printed: '$-0.0000$' (residual mean L362; scrutiny effect L410), '$-0.000$' (StockRet L1621), '-0.000' (Adj.~R^2 L944/1001) -- a rounding/formatting artifact of a near-zero or slightly-negative value
- evidence: 362 mean $-0.0000$ | 944 Adj R2 -0.000
- best fix: Render exact/near zeros as '0.0000' (or report adj-R2 as 0.00) to avoid a minus sign on zero
- refutation: $-0.0000$ faithfully signals a tiny negative that rounds to zero; negative adj-R2 is a real computed value, not an error  (confidence: low)

## Completeness sweeps