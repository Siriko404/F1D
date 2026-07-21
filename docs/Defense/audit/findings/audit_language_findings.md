# Citation inventory

This inventory covers every external work visible in deck body text or source footers. The Dzielinski source-table shorthand on slide 7 is included separately even though it is not printed as a full author-year citation.

| Reference as printed on the deck | Slide | In thesis reference list | Matching thesis entry | Citation support and role |
|---|---:|---|---|---|
| Verrecchia (1983) | 2 | Yes | Verrecchia, R. 1983. *Discretionary disclosure*. *Journal of Accounting and Economics* 5: 179-194. | Consistent. The thesis uses it for costly discretionary withholding by an informed manager. |
| Dye (1985) | 2 | Yes | Dye, R. 1985. *Disclosure of nonproprietary information*. *Journal of Accounting Research* 23: 123-145. | Consistent. The thesis uses it for equilibrium non-disclosure when outsiders cannot distinguish an uninformed manager from an informed but silent one. |
| Basic (1988) | 2 | Yes | *Basic Inc. v. Levinson*, 485 U.S. 224 (1988). | Substantive use is consistent: preliminary merger discussions can be material, and a firm that speaks may not mislead. The shortened author form and mixed legal-literature role are reported as L-002. |
| Rule 10b-5 | 2 | Yes | U.S. Securities and Exchange Commission. *Employment of manipulative and deceptive devices*. Rule 10b-5, 17 C.F.R. Section 240.10b-5. | Consistent. The thesis uses it as legal authority for the prohibition on misleading statements. The omitted year is operator-settled and is not a mismatch. |
| Matsumoto et al. (2011) | 2 | Yes | Matsumoto, D., M. Pronk, and E. Roelofsen. 2011. *What makes conference calls useful? The information content of managers' presentations and analysts' discussion sessions*. *The Accounting Review* 86: 1383-1414. | Consistent. The thesis uses it for the information content of the analyst-discussion session beyond prepared remarks. |
| Hollander et al. (2010) | 2 | Yes | Hollander, S., M. Pronk, and E. Roelofsen. 2010. *Does silence speak? An empirical analysis of disclosure choices during conference calls*. *Journal of Accounting Research* 48: 531-563. | Consistent. The thesis uses it for deliberate non-disclosure and the informativeness of non-answers or silence. |
| Harford (1999) | 3 | Yes | Harford, J. 1999. *Corporate cash reserves and acquisitions*. *The Journal of Finance* 54: 1969-1997. | Consistent. The thesis uses it for accumulated cash reserves before acquisitions and the greater acquisitiveness of cash-rich firms. |
| Shleifer and Vishny (2003) | 3 | Yes | Shleifer, A., and R. Vishny. 2003. *Stock market driven acquisitions*. *Journal of Financial Economics* 70: 295-311. | Consistent. The thesis uses it for the equity-as-acquisition-currency motive of stock bidders. |
| Louis (2004) | 3 | Yes | Louis, H. 2004. *Earnings management and the market performance of acquiring firms*. *Journal of Financial Economics* 74: 121-148. | Consistent. The thesis uses it for pre-announcement earnings management by stock-for-stock bidders rather than cash acquirers. |
| Thewissen et al. (2024) | 3 and 5 | Yes | Thewissen, J., B. Yan, O. Arslan-Ayaydin, and S. Yan. 2024. *Manipulating disclosure tone: Understanding acquiring firms' strategies in stock-for-stock mergers and acquisitions*. SSRN Working Paper 4900453. | Consistent on both slides. The thesis uses it for managed press-release tone before stock-for-stock acquisitions. |
| Ragozzino & Reuer 2024 in the body; Ragozzino and Reuer (2024) in the footer | 5 | Yes | Ragozzino, R., and J. J. Reuer. 2024. *Implications of mergers and acquisitions for information disclosures in earnings calls*. *Long Range Planning* 57: 102393. | Consistent. The thesis uses it for corporate-strategy vocabulary on earnings calls around deal activity. The ampersand versus "and" display variation is a house-style variation, not a substantive author mismatch. |
| Keown & Pinkerton 1981 in the body; Keown and Pinkerton (1981) in the footer | 5 | Yes | Keown, A. J., and J. M. Pinkerton. 1981. *Merger announcements and insider trading activity: An empirical investigation*. *The Journal of Finance* 36: 855-869. | Consistent. The thesis uses it for abnormal stock-price run-up before public merger announcements. The ampersand versus "and" display variation is a house-style variation, not a substantive author mismatch. |
| Dzielinski et al. replication table | 7 | Yes | Dzielinski, M., A. F. Wagner, and R. J. Zeckhauser. 2021. *Straight talkers and vague talkers: The effects of managerial style in earnings conference calls*. M-RCBG Faculty Working Paper Series 2017-02, Harvard Kennedy School. | Consistent. The thesis uses the work for the manager-style and call-level residual decomposition replicated on the thesis sample. |

# Exceptions

## L-001 | major | slide 4 | BROKEN

**Exact text:** `Uncertainty and cash = PRE1 + GAP + POST`

**Problem:** PRE1, GAP, and POST are relied on in the empirical roadmap before the deck defines them. Their first plain-language definitions do not appear until slide 9.

**Evidence:** `deck_text_extracted(4).json`, pages 4 and 9; `thesis_defense_main_deck_slides_01-13_standardized_v2(5).pdf`, slides 4 and 9; `_thesis_FLAT(3).tex`, Methodology and Empirical Design, where PRE1 is one quarter before announcement, GAP is announced but not closed, and POST is after completion.

**Why it matters:** RQ2 is the audience's first map of the timing design. A first-time listener cannot decode the equation without waiting five slides or silently guessing the stages.

**Correction:** Replace the symbols with plain-language stages on slide 4, or define them at first use: `PRE1 (one quarter before) + GAP (announced, not closed) + POST (after completion)`.

## L-002 | minor | slide 2 | INCONSISTENT

**Exact text:** `Thesis framework: Verrecchia (1983); Dye (1985); Basic (1988); Rule 10b-5; Matsumoto et al. (2011); Hollander et al. (2010)`

**Problem:** The footer presents a court decision and an SEC rule in the same undifferentiated list as disclosure theory and empirical conference-call research. It also shortens the thesis author form `Basic Inc. v. Levinson (1988)` to `Basic (1988)`, which makes the case look like an academic author citation.

**Evidence:** `_thesis_FLAT(3).tex`, Conceptual Framework, identifies Basic as a Court holding and Rule 10b-5 as legal authority; the reference list gives `Basic Inc. v. Levinson (1988)` and the SEC Rule 10b-5 entry. The same section uses Verrecchia and Dye as theory and Matsumoto and Hollander as academic evidence.

**Why it matters:** The slide's statement that a firm may stay silent but cannot mislead depends on legal authority, not on the academic papers. The current source line obscures that evidentiary distinction.

**Correction:** Split the footer by role, for example: `Disclosure theory: Verrecchia (1983); Dye (1985). Legal authorities: Basic Inc. v. Levinson (1988); Rule 10b-5. Earnings-call evidence: Matsumoto et al. (2011); Hollander et al. (2010).`

## L-003 | minor | slide 6 | BROKEN

**Exact text:** `Calls with an estimated UncResCEO measure.`

**Problem:** `UncResCEO` is used as a named measure before the deck introduces or decodes the symbol. The definition appears on slide 7.

**Evidence:** `deck_text_extracted(4).json`, pages 6 and 7; `thesis_defense_main_deck_slides_01-13_standardized_v2(5).pdf`, slides 6 and 7; `_thesis_FLAT(3).tex`, Estimation of the Main Variable, defines UncResCEO as the residual part of CEO answer uncertainty left after the first-stage decomposition.

**Why it matters:** The sample funnel asks the audience to understand what qualifies the 44,900 calls, but the measure name is opaque at that point.

**Correction:** Write `Calls with an estimated residual CEO uncertainty measure (UncResCEO)` on slide 6, then retain the short label thereafter.

## L-004 | minor | slide 8 | BROKEN

**Exact text:** `one SD from zero`; `SE`; `Approx. 95% CI`

**Problem:** The statistical abbreviations SD, SE, and CI are used without being expanded before reliance. The deck later continues with the same shorthand.

**Evidence:** `deck_text_extracted(4).json`, pages 7 through 10; `thesis_defense_main_deck_slides_01-13_standardized_v2(5).pdf`, slides 7 through 10. No audience-facing legend expands these abbreviations before their first use.

**Why it matters:** The quantities are compact but load-bearing. A listener should not have to translate the labels while also following the substantive result.

**Correction:** Add one compact first-use legend, such as `SD = standard deviation; SE = standard error; CI = confidence interval`.

## L-005 | minor | slide 8 | INCONSISTENT

**Exact text:** `Leverage, size, Tobin's Q, ROA, capex, dividends, cash-flow volatility`

**Problem:** The same control set is named differently on later slides: slide 8 says `size` and `dividends`, while slides 9 and 10 say `ln(assets)` and `dividend indicator`. The latter wording identifies the actual variables; the former can imply a different size measure and a continuous dividend amount.

**Evidence:** `deck_text_extracted(4).json`, pages 8 through 10; `_thesis_FLAT(3).tex`, Methodology and Empirical Design and Appendix II. Appendix II defines `lnAssets` as the natural log of assets and `DivDummy` as an indicator equal to one for a dividend payer.

**Why it matters:** An examiner comparing specifications may reasonably wonder whether the controls changed across findings.

**Correction:** Use the same labels on all three slides, preferably `ln(assets)` and `dividend indicator`, or introduce them once as `firm size, measured by ln(assets)` and `dividend-payer indicator`.

## L-006 | minor | slide 9 | BROKEN

**Exact text:** `ns`

**Problem:** `ns` is used repeatedly as a result label but is never defined as `not statistically significant`.

**Evidence:** `deck_text_extracted(4).json`, pages 9 and 10; `thesis_defense_main_deck_slides_01-13_standardized_v2(5).pdf`, slides 9 and 10. The deck supplies no legend for `ns`.

**Why it matters:** Unlike the displayed p-value thresholds, `ns` has no spoken or written decoding on the deck.

**Correction:** Add `ns = not statistically significant` to the first statistical legend, or replace each `ns` with `not significant`.

## L-007 | minor | slide 9 | BROKEN

**Exact text:** `POST dip is marginal; not over-read`

**Problem:** The second clause is missing the verb and object needed for speech. It cannot be read aloud as written without changing it to an instruction or passive construction.

**Evidence:** `deck_text_extracted(4).json`, page 9; `thesis_defense_main_deck_slides_01-13_standardized_v2(5).pdf`, slide 9; `_thesis_FLAT(3).tex`, Main Analysis 2, says the POST uncertainty estimate should not be over-read.

**Why it matters:** This annotation carries an interpretive boundary. A grammatical stumble weakens the caution at the moment it is needed.

**Correction:** Use `The POST dip is marginal; do not over-read it.`

## L-008 | minor | slide 9 | BROKEN

**Exact text:** `Cash adds its own lag: 0.7547 (SE 0.0108), p < .01.`

**Problem:** Cash does not add a lag. The cash-ratio regression includes the outcome's own lag. The written subject makes the sentence semantically and orally awkward.

**Evidence:** `deck_text_extracted(4).json`, page 9; `thesis_defense_main_deck_slides_01-13_standardized_v2(5).pdf`, slide 9; `_thesis_FLAT(3).tex`, Methodology and Empirical Design, states that the CashRatio outcome adds its own one-quarter within-firm lag.

**Why it matters:** The current wording makes the model specification sound like an action performed by the cash variable.

**Correction:** Use `The cash-ratio regression includes its own one-quarter lag: 0.7547 (SE 0.0108), p < .01.`

## L-009 | minor | slide 11 | BROKEN

**Exact text:** `Documents that the language pattern concentrates in cash acquisitions rather than stock.`

**Problem:** The comparison is grammatically unbalanced: `cash acquisitions` is compared with `stock`, rather than with `stock acquisitions`.

**Evidence:** `deck_text_extracted(4).json`, page 11; `thesis_defense_main_deck_slides_01-13_standardized_v2(5).pdf`, slide 11; `_thesis_FLAT(3).tex`, Introduction contribution paragraph and Conclusion, consistently compare cash acquisitions with stock acquisitions.

**Why it matters:** The intended contrast is clear, but a presenter must silently repair the final phrase to say it naturally.

**Correction:** Use `Documents that the language pattern concentrates in cash acquisitions rather than in stock acquisitions.`

# Clean dimensions

Citation support is clean: no cited work is attached to a proposition outside the role for which the thesis uses it.

Citation existence and years remain operator-settled. No new existence or year exception was found.

Author identity is otherwise consistent. The ampersand versus `and` forms on slide 5 are treated as excluded house-style variation.

No additional dash-based sentence construction was found beyond the two operator-settled slide 12 constructions: `A within-firm regularity around disclosure - no more, and no less.` and `WHAT IT DOES NOT SHOW - AND WHERE IT MAY NOT CARRY.`

All other audience-facing sentences and concept labels could be spoken and decoded without a reportable repair in this pass.
