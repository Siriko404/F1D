# Editorial Decision Package (Round 2): Speech Uncertainty and Corporate Financial Decisions

**Date:** 2026-04-03
**Manuscript:** Thesis-scope empirical core (thesis_findings.txt + thesis_tables.tex, 6 regression suites)
**Review type:** Full 5-person re-review panel (EIC + 3 Peer Reviewers + Devil's Advocate)
**Previous verdict:** MAJOR REVISION (46/100, unanimous)

---

## Editorial Decision: MINOR REVISION

---

## Score Summary

| Reviewer | Role | Score | Previous | Change | Recommendation |
|----------|------|-------|----------|--------|----------------|
| EIC | Journal fit, originality, significance | 64/100 | 38/100 | +26 | Minor Revision |
| R1 | Methodology (Econometrics) | 64/100 | 38/100 | +26 | Minor Revision |
| R2 | Domain Expert (Corporate Finance Theory) | 71/100 | 52/100 | +19 | Minor Revision |
| R3 | Cross-Disciplinary (NLP/Disclosure) | 68/100 | 62/100 | +6 | Major Revision |
| Devil's Advocate | Core argument challenges | 54/100 | 46/100 | +8 | Major Revision |
| **Consensus** | | **64/100** | **46/100** | **+18** | **Minor Revision (3-2 split)** |

### Decision Rationale

The editorial decision is **Minor Revision** despite the 3-2 split. Three reviewers (EIC, R1, R2) independently
conclude the empirical core has reached Minor Revision quality. R3's Major Revision is driven primarily by
measurement validation concerns (FinBERT/hand-coding) and theoretical grounding for the Q&A vs Presentation
asymmetry -- important for a journal submission but addressable in the thesis text. The Devil's Advocate's
Major Revision reflects the adversarial role and centers on: (1) the NoCEO paradox (which all 5 reviewers
flag but only DA considers blocking), (2) H16 magnitude (flagged by 4/5), and (3) omitted operational
uncertainty controls (a fair concern but not standard in the corporate finance panel-FE literature).

The gap between the consensus score (64) and a publishable paper (~70 for JCF) is closable through
disciplined writing and 2-3 targeted empirical checks.

---

## Consensus Issues

### CONSENSUS-5: All 5 reviewers agree

1. **NoCEO decomposition undermines the original "management team" contribution claim.**
   The decomposition shows UncAnsCEO dominates (H1: 10/12, H16: 6/12) while UncAnsNoCEO is marginal
   (scattered * at Industry FE only). The contribution must be restated: UncAnsMgr is preferred for
   *coverage reliability*, not because non-CEO managers carry independent signal. All 5 reviewers
   commend the honest reporting but require the contribution statement to be rewritten.
   [EIC Critical #2, R1 NoCEO section, R2 Critical #3, R3 Critical #2, DA Critical #1]

2. **Writing tasks (W1-W12) remain undelivered.**
   The paradox resolution, methodology paragraphs, citation integration, and identification-limitations
   discussion exist only as plans. All reviewers note the empirical infrastructure is adequate but the
   intellectual argument connecting results has not been written.
   [EIC Critical #1, R2 Critical #1, R3 implicit, DA implicit]

3. **H1 cash holdings result is genuinely robust.**
   6/6 current-DV specs under two-way clustering, surviving all FE structures. All 5 reviewers
   acknowledge this as a real within-firm association. Single-IV specs show it strengthens (6/6 lead
   also significant at ***). This is the thesis's strongest empirical finding.
   [EIC Strength #2, R1 verification confirmed, R2 Pillar 1 component, R3 acknowledged, DA Grudging #3]

4. **Scope narrowing from 23 to 6 suites was well-executed.**
   The narrative arc (+Cash -> -Leverage -> +R&D -> Capex null -> Unrated amplifies) is coherent.
   All reviewers view this as the single most impactful improvement.
   [EIC Strength #1, R1 implicit, R2 Narrative Arc section, R3 implicit, DA Grudging #5]

5. **Pipeline infrastructure is exceptional.**
   Double-clustering, 12-column FE matrices, deterministic reproducible pipeline, timestamp-versioned
   outputs, coefficient cross-checks verified to 4 decimal places.
   [EIC Strength #5, R1 verification section, R2 implicit, R3 acknowledged, DA Grudging #1]

### CONSENSUS-4: 4+ reviewers agree

6. **H16 RDSales magnitude (11-17% of DV mean) requires scrutiny.**
   4-6x the effect found by Atanassov et al. (2024, RFS) using quasi-experiments. Heavy-tailed R&D
   distribution, possible outlier influence, no winsorization or pharma/biotech exclusion tested.
   [EIC Major #7, R1 Major #2 (Lagged_DV reversal), R2 Critical #2, DA Critical #2]

7. **CEO-Manager sign divergence in H4a remains unexplained.**
   UncAnsCEO predicts HIGHER future leverage (+, 6/6) while UncAnsMgr predicts LOWER future leverage
   (-, 6/6). Opposite signs in the same table. No mechanism test or theoretical explanation.
   [EIC Major #5, R1 New Issue #1, R2 Major #5, DA Major #3]

8. **H1.2 moderation lacks Firm FE.**
   Only 2 Industry FE columns. Credit ratings are largely time-invariant, so Firm FE would absorb the
   dummy, but the interaction could theoretically be estimated within-firm.
   [EIC Major #6, R1 Major #3, R2 Major #6, DA Major #2]

9. **Multiple testing correction absent.**
   72 UncAnsMgr coefficient tests across 6 suites with no formal correction. Pre-specification of
   UncAnsMgr as primary IV and scope reduction help but are not substitutes for statistical correction.
   Raw p-values not reported, making external correction impossible.
   [EIC partially addressed, R1 Critical #1, DA Critical #1 partial, DA Major #5]

### CONSENSUS-3: 3 reviewers agree

10. **H16 Lagged_DV sign reversal under Firm FE is a specification red flag.**
    Lagged_DV flips from +0.48 (Industry FE, ***) to -0.11 (Firm FE, NS). Within-firm Adj R-squared
    is 0.001-0.041 (near zero). H16 Firm FE results may be poorly identified.
    [EIC Major #7, R1 Major #2, DA Critical #2 component]

11. **Single-IV H16 Firm FE failure.**
    When UncAnsCEO is removed from the regression, UncAnsMgr Firm FE significance in H16 vanishes
    (p=0.48-0.70). The within-firm R&D result may partially depend on the multi-IV specification.
    [R1 Major #5, DA Cherry-picking section, EIC New Issue #2]

12. **H1 col1-2 significance discrepancy between table and findings.**
    Table shows single-star (*), findings.txt shows double-star (**). p_one = 0.046 for col1. Must be
    reconciled.
    [EIC Major #3, R1 Minor #8]

---

## Reviewer-Specific Issues

### R3-Specific (Measurement/NLP)

13. **CRITICAL: No LM uncertainty validation for oral discourse.**
    The dictionary was designed for 10-K filings, not spoken Q&A. Without FinBERT or 200-sentence
    hand-coded validation, the measure is "an article of faith." Captures: genuine uncertainty,
    legal hedging, speaking style, or question difficulty?
    [R3 Critical #1 -- sole driver of R3's Major Revision vote]

14. **MAJOR: No speaker-composition control.**
    UncAnsMgr conflates variation in who speaks with variation in what they say. A CEO-word-fraction
    control is computationally trivial and would address whether composition drives the result.
    [R3 Major #3]

15. **MAJOR: Q&A vs Presentation asymmetry needs theoretical grounding.**
    UncPreMgr null everywhere while UncAnsMgr significant -- maps to voluntary vs forced disclosure
    (Verrecchia 1983), tone management (Huang et al. 2014), cheap talk vs costly talk. Under-exploited.
    [R3 Major #6]

### DA-Specific (Adversarial)

16. **CRITICAL: Omitted operational uncertainty controls.**
    Earnings volatility, cash flow volatility, guidance accuracy absent. DailyVola is market-based,
    not operational. Linguistic measure may proxy for volatile fundamentals.
    [DA Critical #3]

17. **MAJOR: No pre/post-GFC subsample split.**
    2008-2009 may dominate within-firm variation. Temporal stability undemonstrated.
    [DA Major #4]

18. **MAJOR: CEO-absent subsample test not run.**
    The testable prediction of the coverage-artifact explanation: does UncAnsMgr still predict
    outcomes in the 29.6% of calls where the CEO is absent? If yes, non-CEO managers do contribute.
    If no, the coverage story is confirmed. This test was not run.
    [DA Critical #1 component]

---

## Strengths (Consensus across all reviewers)

1. **H1 is a strong flagship** -- 6/6 current specs, 6/6 single-IV lead, all FE structures (all 5)
2. **Pipeline infrastructure exceptional** -- deterministic, reproducible, timestamp-versioned (all 5)
3. **Honest null reporting** -- 17 suites dropped, NoCEO decomposition reported transparently (all 5)
4. **6-suite narrative arc is coherent** -- genuine equilibrium balance-sheet story (all 5)
5. **Double-clustering is now default** -- two-way (firm, time) verified in code and diagnostics (all 5)
6. **Standardized effects enable economic interpretation** -- DV means + one-SD effects reported (all 5)
7. **R&D vs Capex decomposition is theoretically sharp** -- Bloom (2014) growth options, Dixit-Pindyck (R2, EIC, DA)
8. **Paradox resolution framework well-sourced** -- Atanassov et al. 2024, He & Wintoki 2016, verified (R2, EIC, DA)
9. **DV formula documentation exceeds standard practice** -- raw Compustat items, source papers (EIC, R1, DA)
10. **Single-IV H1 dramatically strengthens the flagship** -- multicollinearity was suppressing lead (R1, EIC)

---

## Revision Roadmap (Round 2)

### Priority 1 -- Required (must address before thesis defense / JCF submission)

| # | Issue | Source | Action | Effort |
|---|-------|--------|--------|--------|
| R1 | Rewrite contribution statement | All 5 | UncAnsMgr is preferred for coverage reliability; CEO drives signal; non-CEO marginal. Frame as "measurement reliability" + "multi-outcome equilibrium." Not "team dominates CEO." | Writing |
| R2 | Execute paradox resolution (Decision 4) | EIC, R2, DA | Write the 5-paragraph resolution with disciplined causal language. Do NOT claim mediation without test. | Writing |
| R3 | Investigate H16 magnitude | EIC, R1, R2, DA | Report median RDSales, within-firm SD of RDSales, check pharma/biotech exclusion, winsorize at 1%/5%. Compare to AJL (2024) 2.6%. | Empirical |
| R4 | Reconcile H1 col1-2 star discrepancy | EIC, R1 | Check one-tailed p-value threshold: p=0.046 is ** (p<0.05) but table shows *. Fix whichever is wrong. | Bug fix |
| R5 | Discuss CEO-Manager sign divergence in H4a | EIC, R1, R2, DA | At minimum: acknowledge as limitation, propose mechanisms (multicollinearity artifact, CEO strategic communication). Check if sign divergence disappears in NoCEO decomposition. | Writing + check |
| R6 | Add NoCEO theoretical framework | R2, R3 | CEO authority (Adams et al. 2005), signal averaging, information leakage. Not just descriptive reporting. | Writing |
| R7 | Acknowledge H1.2 Firm FE limitation | EIC, R1, R2, DA | "The moderation analysis uses Industry FE because credit rating status has limited within-firm variation." One paragraph. | Writing |
| R8 | Report raw p-values for UncAnsMgr | R1, DA | At least for the 6 thesis suites, enabling external multiple-testing correction. | Table footnote |

### Priority 2 -- Strongly recommended

| # | Issue | Source | Action | Effort |
|---|-------|--------|--------|--------|
| S1 | CEO-absent subsample test | DA | Run UncAnsMgr on calls where CEO was absent (~29.6% of sample). If significant: non-CEO managers DO contribute. If null: coverage story confirmed. | Empirical |
| S2 | Earnings volatility control | DA | Add rolling 8-quarter earnings volatility as control. If UncAnsMgr survives, the "proxy for fundamentals" concern is neutralized. | Empirical |
| S3 | Pre/post-GFC subsample split | DA | Run H1 and H16 on 2002-2007 vs 2010-2018. Temporal stability test. | Empirical |
| S4 | Speaker-composition control | R3 | Add CEO-word-fraction as control to UncAnsMgr regressions. Computationally trivial. | Empirical |
| S5 | LM uncertainty validation | R3 | 200-sentence hand-coded sample stratified by high/low UncAnsMgr and CEO/non-CEO. Or FinBERT sentence-level scoring. | Research |
| S6 | Discuss H16 Lagged_DV sign reversal | R1, DA | Acknowledge Firm FE specification concerns, within-firm R-squared near zero. Present Firm FE as secondary to Industry FE for R&D. | Writing |
| S7 | Q&A vs Presentation theoretical grounding | R3 | Connect to Verrecchia (1983), Huang et al. (2014), costly vs cheap talk. Two paragraphs. | Writing |
| S8 | R&D-Cash complementarity test | R2 | Interaction: UncAnsMgr x R&D-intensity -> CashRatio. Tests whether +Cash is driven by +R&D. If infeasible, state as future work. | Empirical |

### Priority 3 -- Nice to have

| # | Issue | Source | Action |
|---|-------|--------|--------|
| N1 | Report within-R-squared alongside overall | EIC, R1 | More informative under Firm FE |
| N2 | Discuss H4a/H4b lead-concentration alternative | R2 | Trending vs timing -- test with lead+2, lead+3 if feasible |
| N3 | Apply within-suite Holm-Bonferroni or BH correction | R1 | For marginal results especially |
| N4 | Discuss long-run vs short-run effects | DA | beta / (1 - rho) for dynamic interpretation |
| N5 | Add word-level examples from transcripts | R3 | 3-5 example sentences showing what LM uncertainty looks like |
| N6 | Discuss PRisk AR(1) = 0.30 implications | R2 | Moderate, not high -- lead-placebo not fully explained by persistence |
| N7 | Discuss single-IV divergence from main table for H4/H16 | R2, R1 | H4 collapses, H16 weakens -- multicollinearity dynamics |

---

## Strategic Recommendations (from R2)

R2 offers a strategic repositioning that the EIC endorses:

1. **Elevate R&D-Capex decomposition as the central contribution** (not cash holdings as flagship).
   The contrast between R&D (survives Firm FE, growth options) and Capex (dies under Firm FE, Dixit-Pindyck)
   is the sharpest empirical result and the most publishable insight.

2. **Reframe UncAnsMgr advantage as measurement-reliability finding**, not "team matters."
   Coverage advantage (95.8% vs 70.4%) + signal averaging + CEO-authority framework.

3. **The three contribution pillars** (in order of strength):
   - Pillar 1: R&D vs Capex decomposition under uncertainty (strong)
   - Pillar 2: Measurement reliability of team-aggregate vs CEO-only measures (moderate)
   - Pillar 3: Precautionary balance-sheet restructuring as coherent equilibrium (moderate)

---

## Comparison: Round 1 vs Round 2

| Dimension | Round 1 (46/100) | Round 2 (64/100) |
|-----------|-----------------|-----------------|
| Scope | 23 suites, fishing deck | 6 suites, coherent narrative |
| Clustering | Firm-only | Two-way (firm, time) |
| Primary IV | Not pre-specified | UncAnsMgr declared primary |
| Effect sizes | Unreported | DV means + one-SD effects |
| Robustness | None | Single-IV, NoCEO decomp, no-lagged-DV, CEO probit, PRisk AR(1) |
| NoCEO finding | Unknown | CEO drives signal (transparently reported) |
| R-squared type | Ambiguous | Footnoted as "overall, not within" |
| Causal language | "Effects" throughout | "Predicts" for Tier 1 (partially) |
| Contribution claim | "Team dominates CEO" | Needs rewrite (all 5 agree) |
| Paradox resolution | Nonexistent | Framework designed, unwritten |
| Writing | Not evaluated | Not yet executed (W1-W12 pending) |

---

## Path to Acceptance

### For thesis defense (target: 70/100):
Complete Priority 1 items (R1-R8). These are primarily writing tasks plus one empirical check (H16 magnitude).
The empirical core is sufficient for a thesis defense if properly framed.

### For Journal of Corporate Finance submission (target: 75/100):
Complete Priority 1 + Priority 2 items S1-S4. The CEO-absent subsample test (S1) and earnings volatility
control (S2) are the most impactful additional analyses. If both confirm the results, the identification
concern is substantially mitigated (though not fully resolved without an instrument).

### For JFE/RFS (target: 85+/100):
Not achievable without a quasi-experiment or instrument. This is a permanent design limitation, not a
fixable issue. The thesis correctly acknowledges this.

---

*This Editorial Decision Package was generated by a 5-person re-review panel. Round 2 of 2.*
