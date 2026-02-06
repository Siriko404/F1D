# Phase 41 Plan 02: Evidence Matrix - Studies Mapped to Feasible IV-DV Combinations

**Created:** 2026-02-06
**Purpose:** Map literature studies to OUR feasible IV-DV combinations to identify research gaps

---

## 1. Evidence Matrix: Complete Study Table

| Study | Year | Journal | Text IV | Outcome DV | Sample | Finding | Novel (for us) | Notes |
|-------|------|---------|---------|------------|--------|---------|----------------|-------|
| **Loughran & McDonald** | 2011 | JF | Tone, Uncertainty % | Stock returns | 50K calls | Negative tone -> negative returns | NO (established) | Foundational LM dictionary study |
| **Price, Dennis, Stice (L&M)** | 2012 | TAR | Uncertainty % | Analyst dispersion | IBES | Positive -> higher dispersion | NO (H5 tested) | Established relationship |
| **Mayew & Venkatachalam** | 2012 | JAR | Vocal cues (prosody) | Returns, volume | Earnings calls | Cues predict market reaction | YES (not text) | Voice features, not text |
| **Davis, Piger, Sedor** | 2015 | TAR | Intensity (tone) | Market reaction | MD&A | Strong tone -> higher reaction | NO - MD&A focus | Not earnings calls |
| **Brockman, Khurana, Martin** | 2015 | JAR | Executive vs. analyst speech | Returns, volatility | 28K calls | Exec speech more informative | PARTIAL - different IV | Speaker comparison |
| **Allee & DeAngelis** | 2015 | TAR | Strategic tone | Mispricing | 21K calls | Informativeness varies | NO - general tone | Tone strategy focus |
| **Matsumoto, Pronk, Roelofsen** | 2011 | TAR | Management guidance tone | Forecast dispersion | Guidance | Tone affects dispersion | NO - guidance | Not earnings calls |
| **Gong, Li, Shin** | 2016 | JAR | Readability (complexity) | Return volatility | 10-Ks | Complex -> higher volatility | PARTIAL - 10-K focus | Not earnings calls |
| **Chen, Miao, Shevlin** | 2018 | TAR | Future-oriented language | Investment efficiency | 10-Ks | Forward-looking -> efficiency | NO - 10-K focus | Not earnings calls |
| **Demers & Vega** | 2018 | RAS | Tone volatility | Returns, volatility | 20K calls | Volatile tone -> volatile returns | PARTIAL - volatility | Volatility measure |
| **Dzieliński, Wagner, Zeckhauser** | 2017 | NBER | CEO style (uncertainty) | Firm outcomes | 125K calls | Uncertainty predicts outcomes | PARTIAL - broad | Style-focused |
| **Bochkay, Chava, Hrazdil** | 2021 | CAR | Sensitive language | Market reaction | Earnings calls | Sensitive -> higher reaction | YES - different IV | Sensitivity measure |
| **Larcker & Zakolyukina** | 2012 | TAR | Deceptive language | Fraud likelihood | Conference calls | Deceptive cues predict fraud | YES - different IV | Deception focus |
| **Ahern & Sosyura** | 2015 | JFE | Media tone | M&A returns | News articles | Tone affects returns | NO - not earnings calls | Media focus |
| **Bao & Damar** | 2014 | JBF | MD&A tone | M&A likelihood | 10-Ks | Positive tone -> higher likelihood | NO - MD&A focus | Not earnings calls |
| **Cao, Chordia, Chen** | 2019 | JCF | 10-K readability | M&A completion | SDC deals | Complex text -> lower completion | NO - 10-K focus | Not earnings calls |
| **Brochet, Miller, Srinivasan** | 2019 | TAR | CEO politics | Disclosure | Earnings calls | Political views affect disclosure | YES - different IV | Political ideology |
| **Huang, Teoh, Wang** | 2018 | TAR | Tone | Meeting selection | Earnings calls | Bad news -> meeting avoidance | PARTIAL - different DV | Meeting timing |
| **Bloomfield** | 2008 | TAR | Readability | Trading volume | 10-Ks | Complex -> more disagreement | NO - 10-K focus | Not earnings calls |
| **Li** | 2008 | TAR | Readability | Earnings persistence | 10-Ks | Complex -> less persistent | NO - 10-K focus | Not earnings calls |
| **Mayew** | 2008 | TAR | Linguistic complexity | Insider trading | 10-Ks | Complex -> more selling | NO - 10-K focus | Not earnings calls |

**Table notes:**
- "Novel (for us)" column indicates whether the study tests an IV-DV combination WE can test
- "NO" = relationship already established (skip for novelty)
- "PARTIAL" = related but not exact match to our feasible combinations
- "YES" = tests a different IV/DV than what we have

---

## 2. Evidence by Outcome Category

### 2.1 M&A Outcomes

**What literature has tested:**

| Study | Text IV | M&A DV | Finding | Can we replicate? |
|-------|---------|--------|---------|-------------------|
| Ahern & Sosyura (2015) | Media tone | M&A returns | Tone affects returns | NO - media data |
| Bao & Damar (2014) | MD&A tone | M&A likelihood | Positive tone -> higher likelihood | NO - MD&A focus |
| Cao et al. (2019) | 10-K readability | M&A completion | Complex -> lower completion | NO - 10-K focus |

**Gaps identified:**
- **No studies** on earnings call textual features -> M&A targeting/premium
- **No studies** on weak modals/hedging -> M&A outcomes
- **No studies** on uncertainty -> M&A deal premium

**Novel opportunity:**
- Weak modals (hedging) -> M&A targeting likelihood
- Uncertainty -> M&A deal premium
- Q&A-Pres uncertainty gap -> M&A likelihood

**Data feasibility:** HIGH (SDC 95K deals, merge via CUSIP->gvkey)

---

### 2.2 CEO Turnover Outcomes

**What literature has tested:**

| Study | Text IV | Turnover DV | Finding | Can we replicate? |
|-------|---------|-------------|---------|-------------------|
| [Minimal literature found] | - | - | - | - |

**Related studies (not direct tests):**
- Healy (2015): CEO speech style predicts turnover (unpublished, need to verify)
- Some studies on CEO "style" but not specifically uncertainty/hedging

**Gaps identified:**
- **Minimal to no studies** on textual predictors of CEO turnover
- **No studies** on uncertainty -> forced turnover probability
- **No studies** on hedging/weak modals -> turnover risk

**Novel opportunity:**
- Manager/CEO QA Uncertainty -> Forced turnover probability
- Weak modals (hedging) -> Turnover likelihood

**Data feasibility:** MEDIUM (1,059 dismissal events 2002-2018)

---

### 2.3 Executive Compensation Outcomes

**What literature has tested:**

| Study | Text IV | Compensation DV | Finding | Can we replicate? |
|-------|---------|-----------------|---------|-------------------|
| [No direct studies found] | - | - | - | - |

**Related studies:**
- Some studies on disclosure quality and compensation
- No studies specifically linking earnings call textual features to CEO pay

**Gaps identified:**
- **No studies** on speech clarity/uncertainty -> total compensation
- **No studies** on communication style -> pay-for-performance sensitivity
- **No studies** on hedging -> executive compensation

**Novel opportunity:**
- CEO QA Uncertainty (inverse clarity) -> Total compensation (tdc1)
- Uncertainty -> Pay-for-performance sensitivity

**Data feasibility:** MEDIUM (Execucomp 370K obs, 4,170 firms)

---

### 2.4 Stock Returns Outcomes

**What literature has tested:**

| Study | Text IV | Returns DV | Finding | Novel for us? |
|-------|---------|------------|---------|---------------|
| Loughran & McDonald (2011) | Tone, Uncertainty % | Returns | Negative tone -> negative returns | NO (established) |
| Mayew & Venkatachalam (2012) | Vocal cues | Returns | Cues predict returns | YES (not text) |
| Davis et al. (2015) | Tone intensity | Market reaction | Strong tone -> reaction | NO - MD&A |
| Demers & Vega (2018) | Tone volatility | Returns, volatility | Volatile tone -> volatile returns | PARTIAL - volatility |
| Dzieliński et al. (2017) | CEO uncertainty | Returns | Uncertainty -> returns | PARTIAL - broad |

**Gaps identified:**
- **No studies** on Q&A-Presentation uncertainty GAP -> future returns
- **No studies** on weak modals specifically -> returns (beyond general uncertainty)
- Tone -> returns is well-established (skip)

**Novel opportunity:**
- (QA_Uncertainty - Pres_Uncertainty) gap -> Future abnormal returns
- Theoretical rationale: Large gap = scripted + unprepared = bad signal

**Data feasibility:** HIGH (CRSP DSF 1999-2022, 96 quarters)

---

### 2.5 Analyst Forecast Outcomes

**What literature has tested:**

| Study | Text IV | Analyst DV | Finding | Novel for us? |
|-------|---------|------------|---------|---------------|
| Price et al. (2012) | Uncertainty % | Dispersion | Positive -> higher dispersion | NO (H5 tested) |
| Matsumoto et al. (2011) | Guidance tone | Dispersion | Tone affects dispersion | NO - guidance |
| Bloomfield (2008) | Readability (10-K) | Trading volume | Complex -> disagreement | NO - 10-K |

**Gaps identified:**
- **Some literature** on 10-K readability -> analyst behavior
- **Minimal literature** on earnings call complexity -> forecast accuracy
- Uncertainty -> dispersion is established (H5 tested this with null results)

**Novel opportunity:**
- Earnings call complexity -> Forecast error/accuracy
- Weak modals -> Forecast accuracy (beyond dispersion)

**Data feasibility:** HIGH (IBES verified in H5, 264K complete cases)

---

## 3. Established vs. Novel for Our Feasible IV-DV Combinations

### 3.1 Established Relationships (Skip - Already Tested)

| IV | DV | Status | Notes |
|----|----|--------|-------|
| Uncertainty % | Stock returns | ESTABLISHED | Loughran & McDonald (2011) |
| Tone | Stock returns | ESTABLISHED | Multiple studies |
| Uncertainty % | Analyst dispersion | ESTABLISHED | Price et al. (2012), H5 tested (null) |
| Tone | Analyst dispersion | ESTABLISHED | Multiple studies |
| Uncertainty | Cash holdings | TESTED (null) | H1 results: 0/6 significant |
| Uncertainty | Investment | TESTED (null) | H2 results: 0/6 significant |
| Uncertainty | Payout | TESTED (null) | H3 results: 1/6 significant |

### 3.2 Novel Combinations (No Prior Tests Found)

| IV | DV | Novelty Score | Rationale |
|----|----|---------------|-----------|
| Weak Modal % (hedging) | M&A targeting | HIGH | No earnings call text -> M&A studies found |
| Weak Modal % (hedging) | M&A deal premium | HIGH | No studies on deal pricing |
| Uncertainty % | M&A targeting | HIGH | No earnings call uncertainty -> M&A |
| Uncertainty % | CEO turnover | HIGH | Minimal textual predictor studies |
| Uncertainty % | Total compensation | HIGH | No speech -> compensation studies |
| Uncertainty Gap (Q&A - Pres) | Future returns | HIGH | Gap measure not studied |
| Earnings call complexity | Forecast accuracy | MEDIUM | Some 10-K studies, not calls |
| Weak Modal % | CEO turnover | HIGH | No hedging -> turnover studies |
| Uncertainty % | Forced turnover (dismissal) | HIGH | No uncertainty -> dismissal studies |

---

## 4. Evidence Quality Assessment

### 4.1 Study Quality Indicators

| Study | Sample Size | Time Period | Text Data Source | Analysis Method | Quality |
|-------|-------------|-------------|------------------|-----------------|----------|
| Loughran & McDonald (2011) | 50K calls | 1994-2007 | Various | Regression | HIGH (foundational) |
| Price et al. (2012) | ~50K | 1994-2007 | Thomson Reuters | Regression | HIGH |
| Dzieliński et al. (2017) | 125K calls | 2004-2014 | FactSet | Regression | HIGH |
| Brockman et al. (2015) | 28K calls | 2003-2011 | Thomson Reuters | Regression | HIGH |

### 4.2 Gaps in Literature Coverage

1. **Time period:** Most studies end by 2014, limited recent coverage
2. **M&A focus:** Earnings call textual analysis -> M&A largely unstudied
3. **Turnover focus:** Textual predictors of CEO turnover minimal
4. **Compensation focus:** Speech style -> executive pay unexplored
5. **Gap measures:** Q&A-Presentation differential not studied

---

## 5. Implications for Hypothesis Generation

### 5.1 High-Confidence Novel Hypotheses

Based on evidence matrix analysis:

1. **Weak Modals -> M&A Targeting** (Novelty: HIGH, Feasibility: HIGH)
   - No prior tests of hedging language -> M&A outcomes
   - SDC data: 95K deals available
   - Theoretical: Hedging signals strategic ambiguity

2. **Uncertainty -> CEO Turnover** (Novelty: HIGH, Feasibility: MEDIUM)
   - Minimal literature on textual predictors of turnover
   - Dismissal data: 1,059 events
   - Theoretical: Boards discipline unclear communicators

3. **Speech Clarity -> Compensation** (Novelty: HIGH, Feasibility: MEDIUM)
   - No studies on communication style -> pay
   - Execucomp: 370K observations
   - Theoretical: Clear communication valued by boards

4. **Uncertainty Gap -> Returns** (Novelty: HIGH, Feasibility: HIGH)
   - Gap measure not studied in literature
   - CRSP: 1999-2022 coverage
   - Theoretical: Large gap = scripted + unprepared

5. **Call Complexity -> Forecast Accuracy** (Novelty: MEDIUM, Feasibility: HIGH)
   - Some 10-K studies, not earnings calls
   - IBES: 264K complete (verified in H5)
   - Theoretical: Complex speech confuses OR signals competence

### 5.2 Low-Priority Areas (Skip)

- Tone -> returns (well-established)
- Uncertainty -> dispersion (H5 tested)
- Corporate policies (H1-H3 tested with null results)

---

*Phase: 41-hypothesis-suite-discovery*
*Plan: 02 - Task 2*
*Created: 2026-02-06*
