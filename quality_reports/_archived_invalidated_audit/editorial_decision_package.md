# Editorial Decision Package: Speech Uncertainty and Corporate Financial Decisions

**Date:** 2026-04-03
**Manuscript:** Empirical core (findings.txt + all_tables.tex, 23 regression suites)
**Review type:** Full 5-person panel (EIC + 3 Peer Reviewers + Devil's Advocate)
**Status:** 4 of 5 reviews complete (R1 Methodology still in progress)

---

## Editorial Decision: MAJOR REVISION

---

## Score Summary

| Reviewer | Role | Score | Recommendation |
|----------|------|-------|---------------|
| EIC | Journal fit, originality, significance | 38/100 | Major Revision |
| R2 | Domain Expert (Corporate Finance Theory) | 52/100 | Major Revision |
| R3 | Cross-Disciplinary (NLP/Disclosure) | 62/100 | Major Revision |
| Devil's Advocate | Core argument challenges | N/A | Major Revision |
| R1 | Methodology (Econometrics) | 38/100 | Major Revision |
| **Consensus** | | **46/100** | **Major Revision (unanimous)** |

---

## Consensus Issues (All 4 reviewers agree)

### CONSENSUS-4: Issues flagged by ALL reviewers

1. **No exogenous variation / instrument.** Every reviewer flagged this as a fundamental limitation. The thesis cannot claim causality with panel FE alone. [EIC MC1, R2 #10, R3 #2, DA #4]

2. **Multiple testing problem (~1,000 regressions, no correction).** 4 IVs x 23 suites x 6-12 cols with no Bonferroni, Holm, or BH correction. [EIC #2, R2 implicit, R3 implicit, DA CRITICAL #1]

3. **Economic magnitudes unreported.** No standardized effect sizes (beta x SD). Many coefficients appear trivially small (DISP 0.0001, spreads 0.0001). [EIC additional, R2 #7, R3 #8, DA "So What?"]

4. **H11-Lead placebo failure under-discussed.** Future political risk predicts current uncertainty at p<0.01. Undermines causal interpretation. [EIC additional, R2 #3, R3 #2, DA MAJOR #7]

5. **CEO-Manager sign divergence lacks mechanism test.** Three suites show opposite signs with no empirical test to distinguish strategic vs operational vs aggregation explanations. [EIC additional, R2 #6, R3 #7, DA MAJOR #8]

### CONSENSUS-3: Issues flagged by 3+ reviewers

6. **Firm FE kills 7+ suites.** Many results are cross-sectional only. Must partition Tier 1 (within-firm) from Tier 2 (cross-sectional). [EIC MC2, R2 #4, DA MAJOR #6]

7. **Cash-investment paradox unresolved.** +Cash AND +Investment contradicts standard precautionary/real-options predictions. [EIC MC3, R2 core section, DA CRITICAL #2]

8. **Scope too broad (23 suites).** Thesis scope, not journal scope. Need radical narrowing to 6-8 tables. [EIC scope assessment, R2 implicit, DA overgeneralization]

9. **Specification search across 4 IVs.** Different IVs highlighted per suite without pre-specified primary. [EIC #2, DA CRITICAL #1, R3 implicit]

### DA-CRITICAL: Devil's Advocate issues that block Accept

10. **Omitted variable: actual operational uncertainty.** No control for realized earnings volatility, cash flow volatility, or guidance accuracy. The linguistic measure may be a noisy proxy for the true confound. [DA CRITICAL #3]

11. **Honest hit rate is ~15-20% (3-4 Tier 1 out of 23).** Framing as "23 suites of evidence" overstates what the data support. [DA MAJOR #11]

---

## Unique Issues by Reviewer

### R2 (Domain Expert) — Unique contributions:
- **Missing critical citations:** Bloom (2009), Gulen & Ion (2016, RFS), Bloom-Bond-Van Reenen (2007), Bodnaruk-LM (2015, JF), LM (2016, JFE), Larcker & Zakolyukina (2012), OPSW (1999), Adams-Almeida-Ferreira (2005)
- **Gulen & Ion (2016) find uncertainty REDUCES investment** — directly contradicts H13/H16. Must be confronted.
- **Theoretical framework is ad hoc:** precautionary for cash, real options for investment, information asymmetry for financing — no unified model
- **H1.2 Unrated interaction** is about information opacity, not financial constraint per se

### R3 (NLP/Disclosure) — Unique contributions:
- **No validation of LM uncertainty against human judgment.** Need 200-sentence hand-coded sample or FinBERT validation
- **CEO absence rate ~30%.** Systematic selection issue for UncAnsCEO — CEOs may skip Q&A precisely when uncertainty is high
- **No speaker-composition control.** UncAnsMgr aggregates CEO + CFO + VP IR + others — composition varies by call
- **Voluntary disclosure theory (Verrecchia 1983)** maps cleanly onto Presentation (voluntary) vs Q&A (forced)
- **Tone management literature** — managers may strategically manage uncertainty language in presentations
- **Transcript quality variation** across the 2002-2018 sample period
- **"Forward-looking narrative" vs "responsive dialogue"** is better framing than "scripted vs spontaneous"

### Devil's Advocate — Unique contributions:
- **The "honest paper" is much smaller:** 3-4 Tier 1 associations, not 23 causal effects
- **No subsample stability tests** (pre/post GFC). The GFC may drive all within-firm variation.
- **"So What?" test fails.** No actionable implications for CFOs, portfolio managers, or regulators.

---

## Strengths (Consensus across all reviewers)

1. **The manager-team dominance finding is genuinely novel** (all 4 reviewers)
2. **Comprehensive identification battery** — 6-12 specs per suite with Industry/Firm FE x Year/YrQtr FE (all 4)
3. **Honest null reporting** — H7, H7b, H21 complete nulls; H11-Lead placebo failure documented (all 4)
4. **Large, well-constructed sample** — 112,968 calls, 2,429 firms (all 4)
5. **DV formula documentation** with raw Compustat/CRSP/IBES items (EIC, R3)
6. **Exceptional infrastructure** — deterministic pipeline, reproducible (R3)
7. **H1.2 Unrated interaction** is a sharp, well-identified moderation result (R2, EIC)
8. **QA-vs-Presentation asymmetry** for corporate vs intermediary outcomes is novel (R3, DA)

---

## Revision Roadmap

### Priority 1 — Required (must address before resubmission)

| # | Issue | Source | Action |
|---|-------|--------|--------|
| R1 | Pre-specify UncAnsMgr as primary IV | EIC, DA | Designate in introduction; relegate other 3 IVs to robustness/supplementary |
| R2 | Apply within-suite multiple-testing correction | EIC, DA | Holm-Bonferroni (alpha = 0.0125) or Benjamini-Hochberg FDR; report adjusted p-values |
| R3 | Compute standardized effect sizes | All 4 | Report beta x SD(IV) for all Tier 1 results; translate to economic magnitudes ($ or basis points) |
| R4 | Partition results into Tier 1 (within-firm) vs Tier 2 (cross-sectional) | EIC, R2, DA | Formal tier system; no causal language for Tier 2 |
| R5 | Reframe ALL claims as "associations," not "effects" | DA, EIC | Throughout manuscript |
| R6 | Resolve the cash-investment paradox | EIC, R2 | Balance-sheet identity exercise; cite Bloom (2009), Gulen & Ion (2016); test heterogeneity by constraint status |
| R7 | Add missing critical citations | R2 | Bloom (2009), Gulen & Ion (2016), BBV (2007), BLM (2015), LM (2016), L&Z (2012), OPSW (1999), AAF (2005) |
| R8 | Reframe H11 as association/validation, not causal | EIC, R2, DA | Report PRisk autocorrelation; frame as construct validation |
| R9 | Narrow scope to 6-8 core tables for journal submission | EIC, R2 | H1, H4a, H16, H1.2, H13.1, H11 in main body; rest in appendix |

### Priority 2 — Strongly recommended

| # | Issue | Source | Action |
|---|-------|--------|--------|
| S1 | Construct "non-CEO Manager" uncertainty measure | EIC, DA, R3 | Demonstrate whether UncAnsMgr dominance is team-driven or aggregation artifact |
| S2 | Report 4-IV correlation matrix and VIF statistics | EIC, DA | Address multicollinearity concern |
| S3 | Run pre/post-GFC subsample split for Tier 1 results | DA | Demonstrate temporal stability |
| S4 | Discuss CEO absence (~30%) as selection issue | R3 | Report CEO participation rates; discuss implications for UncAnsCEO nulls |
| S5 | Add speaker-composition control to UncAnsMgr regressions | R3 | Control for fraction of Q&A words spoken by CEO |
| S6 | Validate LM uncertainty measure (200-sentence hand-coded sample or FinBERT) | R3 | Demonstrate that word counts correspond to human-perceived uncertainty |
| S7 | Address H20 col-3 coefficient tripling | EIC, DA | Sequential control-addition table to identify suppressor |
| S8 | Control for realized operational uncertainty (earnings volatility) | DA | Rule out confound |
| S9 | Develop theoretical framework for CEO-Manager divergence | R2, R3 | Cite Adams et al. (2005); test predictions |
| S10 | Report DV means in all tables | EIC | Enables quick economic significance assessment |

### Priority 3 — Nice to have

| # | Issue | Source | Action |
|---|-------|--------|--------|
| N1 | Run Firm FE specifications for moderation suites (H1.1, H1.2, H13.1) | EIC | If computationally feasible |
| N2 | Acknowledge dictionary vs modern NLP limitation | R3 | Explicit design-choice framing |
| N3 | Frame Presentation as "forward-looking narrative" not just "scripted" | R3 | Better theoretical grounding |
| N4 | Discuss transcript quality variation over 2002-2018 | R3 | Robustness to early-sample noise |
| N5 | Report which R-squared is used (overall vs within) | EIC | Table footnotes |
| N6 | Rare-events logit for H18 (King & Zeng 2001) | R2, R3 | Replace LPM in main text |

---

## The Paper Inside the Thesis

All 4 reviewers converge on the same recommendation for a journal article:

**Title:** "Management Team Uncertainty and Corporate Balance Sheet Decisions: Evidence from Earnings Call Q&A"

**Core content (6-8 tables):**
1. Summary statistics + IV correlation matrix
2. H1: Cash holdings (UncAnsMgr, 12 cols)
3. H4a: Leverage (UncAnsMgr + UncAnsCEO, 12 cols)
4. H16: R&D intensity (UncAnsMgr, 12 cols)
5. H1.2: Financial constraint moderation (Unrated interaction)
6. H13.1: Competitive pressure moderation (TSIMM interaction for capex)
7. H11: Political risk validation (construct validation, with placebo caveat)
8. Robustness: Other IVs, other outcomes, subsample splits

**Theoretical framework:** Precautionary balance-sheet restructuring under uncertainty, with competitive preemption for investment. Acknowledge the tension with standard real-options "wait and see" predictions, cite Bloom (2009) and Gulen & Ion (2016), and test whether the investment increase is driven by firms facing competitive pressure (H13.1 supports this).

**Contribution statement:** "We extend DWZ (2021) from CEO-only to all-manager measures and find that the management team's spontaneous Q&A language is a robust within-firm predictor of cash, leverage, and R&D decisions, while CEO-specific measures are mostly uninformative. This challenges the CEO-centric focus of the corporate communication literature."

---

## Target Journals (ranked by fit)

1. **Journal of Corporate Finance** — best fit for scope and identification level
2. **Journal of Financial and Quantitative Analysis** — if standardized effects are large enough
3. **Review of Finance** — if theoretical framework is well-developed
4. **Journal of Financial Economics** — requires instrument or quasi-experiment
5. **Review of Financial Studies** — requires instrument or quasi-experiment

---

---

## R1 (Methodology) Review — Key Findings

**Score: 38/100 | Recommendation: Major Revision**

### R1's CRITICAL issues (4):
1. **No exogenous variation** — all results are conditional correlations, not causal effects
2. **H11-Lead placebo failure** — undermines the sole causal identification attempt
3. **No multiple testing correction** — ~800-1,000 IV coefficient tests uncorrected
4. **Simultaneous inclusion of mechanically overlapping IVs** — UncAnsMgr includes UncAnsCEO; entering both creates interpretation hazards, especially when signs oppose

### R1's MAJOR issues (7):
5. **No double-clustered standard errors** — firm-only clustering may under-reject given time-clustered earnings calls
6. **No Arellano-Bond / system-GMM robustness** — Lagged_DV coefficients of 0.63-0.94 under Firm FE with T~23 create non-trivial Nickell bias
7. **H18 LPM with 0.27% base rate** — negative adjusted R-squared under Firm FE; methodologically inappropriate
8. **H9 Cox concordance at/below 0.50** — model has zero predictive power; some variants BELOW random
9. **Moderation suites lack Firm FE** — H1.1, H1.1b, H1.2, H13.1 key findings never tested under within-firm identification
10. **H20 complete Firm FE failure** + anomalous col-3 coefficient tripling
11. **H16 Lagged_DV sign reversal under Firm FE** — flips from +0.48 to -0.08 (insignificant), suggesting specification problems

### R1's unique methodological contributions:
- **Nickell bias quantification**: At T=23, bias is approximately -0.04, non-trivial for IV coefficients of 0.003-0.007
- **Double-clustering recommendation**: Cameron, Gelbach & Miller (2011) — firm x calendar quarter
- **Arellano-Bond needed** for H1, H4a, H16 (highest autoregressive parameters)
- **Functional form concerns**: CashRatio bounded [0,1] → fractional response model; PayoutRatio censored → Tobit; binary DVs → proper logit
- **Single-IV specifications needed**: Run UncAnsMgr alone (without UncAnsCEO) to isolate the team effect without multicollinearity

### R1's additional required revisions (beyond Priority 1):
| # | Issue | Action |
|---|-------|--------|
| R1-A | Double-clustered SEs | Report firm x quarter clustering as robustness |
| R1-B | Arellano-Bond estimates | For H1, H4a, H16 (high AR coefficients) |
| R1-C | Single-IV specifications | Run UncAnsMgr alone to address mechanical overlap |
| R1-D | Firm FE for moderation suites | H1.1, H1.1b, H1.2, H13.1 |
| R1-E | Replace H18 LPM with rare-events logit | King & Zeng (2001) or Firth logit |
| R1-F | Remove or heavily caveat H9 | Concordance at/below chance |

---

## FINAL CONSENSUS: All 5 Reviews Complete

### Unanimous verdict: MAJOR REVISION (46/100)

All 5 reviewers independently recommend Major Revision. The core finding (UncAnsMgr predicts cash, leverage, R&D within-firm) is acknowledged as genuine by all reviewers. The required work centers on:

1. **Reframing** (associations, not effects)
2. **Statistical corrections** (multiple testing, double clustering, Arellano-Bond)
3. **Scope narrowing** (6-8 tables, not 23)
4. **Missing analyses** (standardized effects, subsample splits, non-CEO measure, FinBERT validation)
5. **Theoretical development** (unified framework, cash-investment paradox resolution)
6. **Missing citations** (8+ critical papers)

*This Editorial Decision Package was generated by the acad-paper-reviewer skill (v1.4) with 5 dynamically configured reviewers.*
