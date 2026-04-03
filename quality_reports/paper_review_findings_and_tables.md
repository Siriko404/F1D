# Manuscript Review: Speech Uncertainty and Corporate Outcomes (Empirical Core)

**Date:** 2026-04-03
**Reviewer:** review-paper skill
**Files:** `outputs/findings.txt` (1181 lines), `outputs/all_tables.tex` (23 regression tables)

---

## Summary Assessment

**Overall recommendation:** Revise & Resubmit

This thesis examines whether linguistic uncertainty in earnings conference calls --- measured via Loughran-McDonald uncertainty word counts following and extending Dzielinski, Wagner & Zeckhauser (2021) --- predicts corporate financial decisions. The study covers 112,968 calls from 2,429 firms over 2002--2018 across 23 hypothesis suites spanning cash holdings, leverage, investment, payout, market microstructure, takeover risk, SEC attention, and financing choice.

**The core contribution is genuine and well-supported.** The thesis extends DWZ's CEO-only measures to all-manager measures (UncAnsMgr, UncPreMgr) and shows that this novel composite management-team signal is the dominant predictor --- not the CEO-specific measures from the original paper. The flagship results (cash holdings, leverage, R&D intensity) survive demanding identification tests including firm fixed effects, year-quarter fixed effects, and lagged dependent variables.

**However, the empirical architecture has several vulnerabilities** that a top-journal referee would flag: (a) no exogenous variation or instrumental variable, (b) many results die under firm FE, (c) the H11-Lead placebo test fails, (d) CEO-Manager sign divergence across three suites lacks a mechanism test, (e) economic magnitudes are questionable for several DVs, and (f) ~1,000 regressions with no multiple-testing correction. The thesis needs to narrow its claims, acknowledge limitations more prominently, and provide standardized effect sizes.

---

## Strengths

1. **Novel measurement contribution.** Extending DWZ's CEO-only uncertainty measures to all managers is not a trivial exercise. The finding that UncAnsMgr dominates UncAnsCEO challenges the CEO-centric view of corporate communication research. This is a publishable insight on its own.

2. **Comprehensive identification battery.** Each suite runs 6-12 specifications: Industry FE + Year FE (basic), Firm FE + Year FE (basic), Industry FE + Year FE (extended), Firm FE + Year FE (extended), Industry FE + Year-Quarter FE (extended), Firm FE + Year-Quarter FE (extended). This is best practice. The lagged DV as a control in all specifications is a further strength.

3. **Tier 1 results are genuinely robust.** H1 (Cash: UncAnsMgr significant in all 6 specs, survives Firm FE + YrQtr FE), H4a/H4b (Leverage: UncAnsMgr significant in all 6 lead specs, survives Firm FE), H16 (R&D: UncAnsMgr significant in all 6 current specs, survives Firm FE). These pass the strictest within-firm identification tests in the battery.

4. **Honest null reporting.** H7, H7b, and H21 are reported as complete nulls. H12 (payout) is reported as near-null. The failed placebo test (H11-Lead) is documented candidly. This transparency strengthens credibility.

5. **Clean DV documentation.** Every DV formula is spelled out with raw Compustat/CRSP/IBES item codes and source paper references. This aids replicability.

6. **Cross-suite pattern analysis.** The 9 thematic patterns identified across suites demonstrate systematic thinking beyond individual hypothesis tests.

7. **Well-designed tables.** LaTeX tables include all controls (not just IVs), standard errors in parentheses, FE indicators, N, R-squared, Adj R-squared, and appropriate footnotes about clustering and tail direction.

---

## Major Concerns

### MC1: No Exogenous Variation or Instrumental Variable
- **Dimension:** Identification
- **Issue:** All 23 suites use panel regressions with fixed effects. There is no instrument, no natural experiment, no regression discontinuity, and no difference-in-differences around an exogenous shock. The thesis can claim "robust association" but cannot credibly claim "causal effect."
- **Suggestion:** (a) Acknowledge this limitation prominently in the introduction and conclusion. (b) The lead DV results (speech at t predicts outcomes at t+1) provide suggestive evidence against contemporaneous reverse causality --- emphasize this. (c) Consider whether any exogenous shock to uncertainty (e.g., unexpected CEO departures, natural disasters, regulatory shocks) could serve as a quasi-experiment for at least one suite. Even one causal result would dramatically strengthen the thesis.
- **Location:** All 23 suites; introduction and conclusion sections of the thesis.

### MC2: Firm FE Kills Many Results (7+ Suites)
- **Dimension:** Identification
- **Issue:** H13 (Capex, UncAnsMgr), H12 (Payout), H17 (Repurchases, UncAnsMgr), H19 (External Funding), H20 (Debt Choice --- all three significant IVs), H14 (Spreads delta) all lose significance under Firm FE. This means these results are driven by cross-sectional differences between firms, not within-firm temporal variation. A referee will argue these are confounded by time-invariant firm characteristics (industry, governance culture, permanent management style).
- **Suggestion:** (a) Formally partition the results into "within-firm effects" (Tier 1: H1, H4, H16) and "cross-sectional associations" (Tier 2: H13, H17, H20). (b) Do not claim causal language for Tier 2 results. (c) Discuss the statistical power argument: some DVs (capex, repurchases) may have insufficient within-firm variation over 16 years for Firm FE to detect effects. Report within-firm standard deviations of DVs to support this claim. (d) For H20, the restricted sample (~930 firms, ~13.6 obs/firm) may lack power for Firm FE. Report this explicitly.
- **Location:** H13, H12, H17, H19, H20 tables and discussion sections.

### MC3: H11-Lead Placebo Test Fails
- **Dimension:** Identification
- **Issue:** The H11-Lead placebo test was designed to show that future political risk should NOT predict current speech uncertainty (establishing temporal precedence for H11). It fails decisively: lead PRisk (t+1, t+2) is significant at p<0.01 in 7 of 8 columns. This undermines the causal interpretation of the entire H11 family.
- **Suggestion:** (a) Frame H11 as a "descriptive association" or "construct validation" exercise, NOT a causal claim. (b) The monotonic decay in coefficients (contemporaneous > lag1 > lag2 > lead1 > lead2) is consistent with autocorrelation in PRisk, not confounding. Report the autocorrelation coefficient of PRisk to support this defense. (c) If PRisk has AR(1) > 0.80, acknowledge that lag/lead tests are uninformative about temporal precedence because any adjacent quarter's PRisk proxies for the current quarter. (d) Consider testing with orthogonalized PRisk residuals (regress PRisk(t) on PRisk(t-1), use residuals as the IV) to isolate the innovation component.
- **Location:** H11-Lead section and H11 discussion.

### MC4: CEO-Manager Sign Divergence Has No Mechanism Test
- **Dimension:** Argument Structure
- **Issue:** Three suites show opposite signs between CEO and Manager measures: H4a (CEO +leverage vs Manager -leverage), H16 (CEO -R&D vs Manager +R&D), H20 (CEO -equity vs Manager +debt). The findings document offers interpretations ("strategic vs operational") but there is no empirical test distinguishing these channels. Since UncAnsMgr mechanically includes the CEO, the divergence implies the non-CEO portion of UncAnsMgr drives the Manager result in the opposite direction from the CEO-only signal. This is confusing and potentially undermines the unified "uncertainty" construct.
- **Suggestion:** (a) Construct a "non-CEO Manager" measure (UncAnsMgr minus CEO contribution) and test whether it resolves the sign divergence. (b) Report the correlation matrix of the 4 IVs. If UncAnsMgr and UncAnsCEO have correlation > 0.7, the separate identification of CEO effects is econometrically questionable (near-collinearity). (c) Either develop a full theoretical section on the CEO-Manager divergence or present it as an open puzzle. Do not claim you have explained it without a mechanism test.
- **Location:** H4a, H16, H20 sections; Cross-Suite Pattern 9.

### MC5: Multiple Testing Problem (~1,000 Regressions)
- **Dimension:** Econometric Specification
- **Issue:** With 23 suites x 4 IVs x 6-12 columns = ~900-1,000 individual coefficient tests, the probability of spurious significance is non-trivial. At alpha = 0.05, pure chance would yield ~45-50 significant results. The thesis reports ~80-100 significant coefficients, which is above the random expectation but not overwhelmingly so. No multiple-testing correction is applied.
- **Suggestion:** (a) At minimum, acknowledge the issue explicitly. (b) Apply a within-suite correction (e.g., Holm-Bonferroni across the 4 IVs, adjusting effective alpha from 0.05 to ~0.0125). (c) Alternatively, adopt a Benjamini-Hochberg false discovery rate (FDR) approach, which is more appropriate for correlated tests. (d) Emphasize that the Tier 1 results (H1, H4, H16) would survive even a conservative Bonferroni correction within their suites (UncAnsMgr is significant at p<0.01 in multiple specs). (e) Consider reporting q-values alongside p-values.
- **Location:** Methodology section; all tables.

### MC6: Economic Magnitudes Not Standardized
- **Dimension:** Econometric Specification
- **Issue:** Raw coefficients are reported without standardized effect sizes. A coefficient of 0.0036 on CashRatio is uninterpretable without knowing the standard deviation of UncAnsMgr. For DISP (0.0001-0.0003) and DSPREAD (0.0001), the magnitudes appear economically trivial. For R&D (0.02-0.04), they appear suspiciously large. Without standardized effects, the reader cannot evaluate economic significance.
- **Suggestion:** (a) Report beta * SD(IV) for all Tier 1 results to show the effect of a one-SD shock in uncertainty. (b) Report the percentage change relative to the DV mean. (c) For H16 (R&D), if a one-unit increase in UncAnsMgr (which is a percentage measure, 0-100) raises RDSales by 0.04, verify this is plausible. If the SD of UncAnsMgr is, say, 0.5 percentage points, then a one-SD shock raises RDSales by 0.02 --- which is still 20-40% relative to a typical RDSales of 0.05-0.10. This would be very large and needs scrutiny. (d) For H5 and H14, if standardized effects are < 1% of the DV's SD, acknowledge economic triviality.
- **Location:** All suites; a new "Economic Magnitude" subsection is needed.

---

## Minor Concerns

### mc1: H20 Anomalous Coefficient Jump in Column 3
- **Issue:** UncAnsMgr coefficient triples from +0.0454 (col 1, basic) to +0.1273 (col 3, extended controls). This is unusual and suggests a suppressor variable among the extended controls.
- **Suggestion:** Report a sequential control-addition table (add one extended control at a time) to identify which control causes the jump. If one control is the suppressor, discuss it explicitly.

### mc2: Lagged DV Coefficients Near Unity
- **Issue:** CashRatio lagged DV loads at 0.85 (Industry FE) and 0.63 (Firm FE). PostCallILLIQ loads at ~0.85. Near-unit-root behavior means the DV is highly persistent and the residual variance available for IVs to explain is small.
- **Suggestion:** Acknowledge that high persistence reduces the detectable effect size. For H7/H7b, the ~0.85 coefficient on PreCallILLIQ may explain the null: there is simply no room for speech uncertainty in the residual.

### mc3: H18/H18b LPM for Rare Event (0.27% Base Rate)
- **Issue:** Using a Linear Probability Model for a 0.27% base-rate event will produce fitted probabilities that are negative for many observations. The logit (H18b) is the correct model for this DV, and it shows the result weakening to insignificance with extended controls.
- **Suggestion:** Lead with the logit in the main text and relegate the LPM to a robustness appendix. Acknowledge that the CCCL result is fragile.

### mc4: H9 Cox Concordance Near 0.50
- **Issue:** A concordance of 0.50 means the model discriminates at chance level. Reporting individual hazard ratios from a model with no overall predictive power is misleading.
- **Suggestion:** Report concordance prominently alongside any H9 results. Frame the Friendly UncPreMgr finding as "suggestive" rather than "significant." Note that the model as a whole is uninformative.

### mc5: Moderation Suites Lack Firm FE
- **Issue:** H1.1, H1.1b, H1.2, and H13.1 all use Industry FE only (no Firm FE specifications). The thesis's strongest unmoderated results come from Firm FE. By omitting Firm FE in moderation tests, the thesis avoids the strictest identification.
- **Suggestion:** If computationally feasible, run Firm FE versions of the moderation suites. If not feasible (Firm FE with interactions may lack power in 2-column designs), discuss this limitation explicitly.

### mc6: Presentation Uncertainty as "Scripted" vs "Spontaneous" Not Tested
- **Issue:** The thesis argues UncPreMgr captures "scripted" uncertainty while UncAnsMgr captures "spontaneous" uncertainty. But this is assumed from the earnings call structure, not tested. Some CEOs may deviate from scripts in the presentation; some Q&A answers may be rehearsed.
- **Suggestion:** This is a framing issue. Acknowledge that "presentation" and "Q&A" are proxies for "prepared" and "spontaneous" and that the mapping is imperfect.

### mc7: Sample Period Ends in 2018
- **Issue:** The sample period is 2002-2018. A referee may question generalizability to the post-COVID era (2020+) when earnings calls, corporate uncertainty, and capital markets changed dramatically.
- **Suggestion:** Acknowledge the sample endpoint and note that extending to 2020+ would require re-collecting transcripts and constructing new call-level measures. This is a data availability limitation, not a design flaw.

### mc8: No Subsample Stability Tests
- **Issue:** The results are reported for the full 2002-2018 sample. No split-sample or rolling-window analysis is presented to test whether effects are stable over time (e.g., pre-GFC vs post-GFC, pre-2010 vs post-2010).
- **Suggestion:** Run at least one subsample split (e.g., 2002-2009 vs 2010-2018) for the Tier 1 results to show temporal robustness.

---

## Referee Objections

### RO1: "Your dominant IV (UncAnsMgr) mechanically includes the CEO. How do you disentangle team-level uncertainty from CEO uncertainty?"

**Why it matters:** If UncAnsMgr and UncAnsCEO are highly correlated (r > 0.7), the regressions with all 4 IVs simultaneously may suffer from near-multicollinearity. The "CEO is null" finding could be an artifact of the Manager measure absorbing the CEO signal. Conversely, the "Manager dominates" finding could be driven by the non-CEO managers, but you haven't isolated them.

**How to address it:** (a) Report the correlation matrix of the 4 IVs. (b) Run regressions with only UncAnsMgr as the IV (dropping the other 3) to show it remains significant. (c) Construct a "non-CEO Manager" uncertainty measure and test whether it drives the results. (d) Show VIF statistics for the 4-IV regressions.

### RO2: "You run ~1,000 regressions with 4 IVs and highlight whichever one is significant in each suite. Isn't this specification search?"

**Why it matters:** This is potentially fatal. The thesis runs UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr for each suite and then tells a story about which one "works." H1 = UncAnsMgr. H5 = UncPreMgr. H9 = UncPreMgr. H13 Firm FE = UncAnsCEO. This looks like post-hoc rationalization. A Bonferroni correction within each suite would raise the effective alpha to 0.0125, and several marginal results would disappear.

**How to address it:** (a) Pre-specify a primary IV (UncAnsMgr, since it is the novel contribution) and treat others as exploratory. (b) Report adjusted p-values (Holm or BH). (c) In the abstract and introduction, lead with UncAnsMgr results only. Present the other IVs in appendix/supplementary analyses. (d) Alternatively, argue that the 4 IVs are theoretically distinct (2 speaker groups x 2 call sections) and that testing all four is motivated by the research question, not fishing.

### RO3: "The cash-investment paradox: uncertainty increases cash (H1) AND investment (H13, H16). Where does the money come from?"

**Why it matters:** A precautionary motive predicts cash hoarding and investment deferral. Your results show cash hoarding and investment INCREASE. This contradicts the standard real-options "wait and see" prediction (Dixit & Pindyck 1994) and needs a reconciliation. Without a formal flow-of-funds argument, the simultaneous +cash and +investment is internally inconsistent.

**How to address it:** (a) The leverage results (H4a/b: negative) suggest the cash comes from reduced debt, not from reduced investment. Firms delever, freeing balance sheet space. (b) The payout results (H12, H17: negative) suggest firms also retain cash by cutting dividends and buybacks. (c) Present a simple balance sheet identity showing how +cash, -leverage, -payout, +investment can co-exist. (d) Frame investment as "uncertainty resolution" rather than "precautionary": firms invest specifically to resolve the uncertainty (R&D to explore, capex to commit to a direction). Cite Bloom, Bond & Van Reenen (2007) on the "cautious" vs "creative destruction" effects of uncertainty. (e) Note that capex (H13) loses significance under Firm FE, so only R&D (H16) is a robust within-firm investment effect.

### RO4: "All your Industry-FE-only results (H13, H17, H20) could be spurious cross-sectional correlations. What is your firm-level identification strategy?"

**Why it matters:** A top-5 journal requires within-firm identification for causal claims. Seven suites fail this test. The thesis would be much smaller if restricted to Firm FE survivors only (H1, H4, H16, and H14b).

**How to address it:** (a) Accept the critique gracefully. Partition results clearly. (b) Argue that Firm FE is a severe test that absorbs all time-invariant heterogeneity, and that for some DVs (capex, repurchases), within-firm variation over 16 years may be insufficient. Report within-firm standard deviations. (c) For H20, the restricted sample (~930 firms) compresses Firm FE power. Report effective degrees of freedom. (d) Consider the Hausman test to formally compare Industry FE vs Firm FE specifications.

### RO5: "Your measures are word counts from the Loughran-McDonald dictionary. How do you know this captures genuine uncertainty rather than stylistic verbosity?"

**Why it matters:** Loughran-McDonald word lists are generic. A manager who uses more words overall will mechanically have more uncertainty words. The percentage normalization helps but doesn't eliminate stylistic confounds. A manager who habitually uses hedging language ("might," "could," "uncertain") may not be more uncertain --- just more cautious in speech.

**How to address it:** (a) The H11 family (political risk predicts all uncertainty measures) validates the construct: when external political uncertainty rises, managers use more uncertainty language. This is face validity. (b) The firm FE specification absorbs time-invariant speaking style --- it identifies off within-firm changes in uncertainty language over time. (c) Consider controlling for total word count or speech length. (d) Cite DWZ's validation exercises from the original paper. (e) Acknowledge that dictionary-based measures are inherently noisy and that more sophisticated NLP (topic models, transformers) could improve measurement.

---

## Specific Comments

### Section: Column-to-FE Key (Lines 11-51)
The FE key is clear and well-documented. The different layouts for 12-col, 6-col, 2-col, and Cox suites are helpful for the reader.

### H1 Table (all_tables.tex, lines 11-74)
Table is well-formatted. All controls are visible. One note: the R-squared drops dramatically from Industry FE (0.818) to Firm FE (0.452). This is unusual --- typically Firm FE explains more variance. The reason is likely that the reported R-squared is "overall" (not within), and Firm FE demeaning removes the between-group variation that inflates the Industry FE R-squared. Clarify which R-squared is reported (overall vs within) in the table notes.

### H4a/H4b (Findings Lines 170-256)
The opposite-sign CEO-Manager finding is the most intellectually stimulating result in the thesis. The lead-DV concentration is well-documented. Consider adding a footnote comparing the relative magnitudes of UncAnsCEO (+0.0068) vs UncAnsMgr (-0.0071) --- they are nearly equal and opposite, which is suggestive of a mechanical offset.

### H11-Lead (Findings Lines 505-543)
The "PLACEBO FAILS" label is appropriately candid. The open questions (Q28-Q30) are excellent. Q30 ("frame as association rather than effect") should be answered affirmatively in the thesis text, not left as an open question.

### H17 (Findings Lines 768-819)
The opposite signs between UncAnsMgr (negative) and UncPreMgr (positive) for repurchases are the most puzzling finding. This deserves a dedicated discussion paragraph, not just an open question. If you cannot explain it, acknowledge it as a genuine anomaly that constrains the unified uncertainty interpretation.

### H20 (Findings Lines 928-981)
The coefficient jump in col 3 (UncAnsMgr from 0.0454 to 0.1273) is a red flag. A referee will ask whether this is a suppressor effect. The Q64 open question identifies this correctly. Convert this open question into an actual robustness check.

### Cross-Suite Patterns (Lines 1012-1181)
Patterns 1-3 (UncAnsMgr dominance, CEO null, UncPreMgr secondary) are well-supported by the data. Pattern 9 (CEO-Manager sign split) is the most speculative and least supported. Consider rewriting Pattern 9 to be more cautious in its interpretation.

### Table Formatting (all_tables.tex)
Tables are clean and professional. Bold + stars for significant coefficients is standard. One improvement: add a row showing the mean of the DV in each table. This allows the reader to gauge economic significance at a glance (coefficient / DV mean = approximate % effect).

---

## Summary Statistics

| Dimension | Rating (1-5) |
|-----------|-------------|
| Argument Structure | 3.5 |
| Identification | 2.5 |
| Econometrics | 3.5 |
| Literature | 3.0 |
| Writing | 4.0 |
| Presentation | 4.5 |
| **Overall** | **3.5** |

**Rating scale:** 1 = reject, 2 = major revision, 3 = R&R, 4 = minor revision, 5 = accept.

The 3.5 overall reflects a thesis with genuine empirical strengths (Tier 1 results, honest reporting, comprehensive battery) that needs targeted improvements in identification framing, multiple-testing acknowledgment, and economic magnitude reporting to meet the standard of a top finance journal. The core contribution --- management team uncertainty dominates CEO-specific measures --- is novel and defensible.
