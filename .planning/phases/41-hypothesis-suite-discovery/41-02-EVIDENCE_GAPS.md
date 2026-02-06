# Phase 41 Plan 02: Evidence Gaps - Novel Hypotheses We Can Test

**Created:** 2026-02-06
**Purpose:** Synthesize evidence matrix and document novel hypotheses that are BOTH untested AND data-feasible

---

## 1. Established Relationships (Skip - Already Tested)

These relationships are well-established in literature OR have been tested in our project with null results:

| Relationship | Evidence | Status |
|--------------|----------|--------|
| Uncertainty % -> Stock returns | Loughran & McDonald (2011) | ESTABLISHED (negative) |
| Tone -> Stock returns | Multiple studies | ESTABLISHED |
| Uncertainty % -> Analyst dispersion | Price et al. (2012) | ESTABLISHED (positive) |
| Weak Modal -> Analyst dispersion (beyond uncertainty) | H5 tested (Phase 40) | NOT SUPPORTED |
| Uncertainty -> Cash holdings | H1 tested | NULL (0/6 significant) |
| Uncertainty -> Investment efficiency | H2 tested | NULL (0/6 significant) |
| Uncertainty -> Payout stability | H3 tested | WEAK (1/6 significant) |

**Implication:** Focus on NEW outcome categories (M&A, turnover, compensation) and NEW text measures (weak modals, gap measures).

---

## 2. Novel Gaps (No Prior Tests + Data Available)

### Gap 1: Weak Modals (Hedging) -> M&A Targeting Likelihood

**Hypothesis H6: Managerial hedging language (weak modals) in earnings calls predicts higher likelihood of becoming an M&A target.**

| Component | Specification |
|-----------|---------------|
| **IV** | Manager_QA_Weak_Modal_pct, CEO_QA_Weak_Modal_pct (hedging: may/might/could) |
| **DV** | M&A target dummy (1 = firm becomes target in next 12 months) |
| **Data sources** | Text measures (112,968 calls), SDC M&A (95,452 deals 2002-2018) |
| **Controls** | Firm size, Tobin's Q, leverage, ROA, industry/Year FE |
| **Theoretical mechanism** | Hedging signals strategic ambiguity or undervaluation, attracting acquirers seeking opportunities |
| **Novelty** | HIGH - No studies on earnings call weak modals -> M&A outcomes |
| **Data feasibility** | HIGH - 95K deals, merge via CUSIP->gvkey verified in Plan 01 |

**Why no prior tests:**
- M&A textual analysis focuses on media tone (Ahern & Sosyura 2015) or MD&A tone (Bao & Damar 2014)
- Earnings call analysis focuses on stock returns, not M&A
- Weak modals as distinct from general uncertainty not widely used

**Expected effect direction:** POSITIVE (hedging -> higher targeting likelihood)

---

### Gap 2: Speech Uncertainty -> CEO Forced Turnover

**Hypothesis H7: Managerial speech uncertainty (vagueness) in earnings calls predicts higher probability of forced CEO turnover.**

| Component | Specification |
|-----------|---------------|
| **IV** | CEO_QA_Uncertainty_pct, Manager_QA_Uncertainty_pct |
| **DV** | Forced CEO turnover dummy (ceo_dismissal = 1) |
| **Data sources** | Text measures (112,968 calls), CEO dismissal data (1,059 events 2002-2018) |
| **Controls** | Prior performance (ROA, stock returns), firm size, tenure, industry/Year FE |
| **Theoretical mechanism** | Boards discipline unclear communicators; vagueness signals problems or incompetence |
| **Novelty** | HIGH - Minimal literature on textual predictors of CEO turnover |
| **Data feasibility** | MEDIUM - 1,059 dismissal events sufficient for logistic regression |

**Why no prior tests:**
- CEO turnover literature focuses on firm performance, board characteristics
- Textual analysis of CEOs focuses on deception (Larcker & Zakolyukina 2012), not turnover
- Limited overlap between textual analysis and labor market outcomes

**Expected effect direction:** POSITIVE (uncertainty -> higher turnover probability)

**Power consideration:** 1,059 events is borderline; logistic regression with firm FE may have limited power. Survival analysis alternative recommended.

---

### Gap 3: Speech Clarity (Inverse Uncertainty) -> Executive Compensation

**Hypothesis H8: CEO speech clarity (lower uncertainty) in earnings calls predicts higher total compensation and higher pay-for-performance sensitivity.**

| Component | Specification |
|-----------|---------------|
| **IV** | CEO_QA_Uncertainty_pct (lower = clearer speech), CEO_Pres_Uncertainty_pct |
| **DV** | (a) Total compensation (tdc1), (b) PPS sensitivity (delta(tdc1)/delta(returns)) |
| **Data sources** | Text measures, Execucomp (370,545 obs, 4,170 firms 1992-2025) |
| **Controls** | Firm size, ROA, stock returns, tenure, industry/Year FE |
| **Theoretical mechanism** | Clear communication valued by boards; unclear speech reduces perceived competence |
| **Novelty** | HIGH - No studies linking communication style to executive pay |
| **Data feasibility** | MEDIUM - Execucomp merge via gvkey+year, ~15K expected overlap |

**Why no prior tests:**
- Compensation literature focuses on firm performance, governance, ownership
- Speech analysis focuses on market reactions, not internal labor markets
- Perception of CEO "quality" typically measured by performance, not communication

**Expected effect direction:** NEGATIVE (higher uncertainty -> lower compensation)

---

### Gap 4: Q&A-Presentation Uncertainty Gap -> Future Stock Returns

**Hypothesis H9: The gap between Q&A uncertainty and Presentation uncertainty predicts future abnormal stock returns.**

| Component | Specification |
|-----------|---------------|
| **IV** | uncertainty_gap = Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct |
| **DV** | Future abnormal returns (3-day, 1-month, 1-quarter after call) |
| **Data sources** | Text measures (both QA and Pres available), CRSP DSF (1999-2022) |
| **Controls** | Prior returns, volatility, firm size, earnings surprise, analyst coverage |
| **Theoretical mechanism** | Large gap = scripted presentation + unprepared for Q&A = bad signal to market |
| **Novelty** | HIGH - Gap measure not studied for return prediction |
| **Data feasibility** | HIGH - CRSP DSF 96 quarters, CCM linking verified |

**Why no prior tests:**
- Most studies analyze QA or Presentation separately, not the differential
- Focus on absolute uncertainty levels, not relative measures
- Gap measure only recently computable with combined datasets

**Expected effect direction:** POSITIVE (higher gap = QA much more uncertain than Pres -> negative returns)

**Variation:**
- Positive gap (QA > Pres): Manager unprepared -> negative abnormal returns
- Negative gap (Pres > QA): Atypical (shouldn't happen) - possible signal of reverse script

---

### Gap 5: Earnings Call Complexity -> Analyst Forecast Accuracy

**Hypothesis H10: Earnings call complexity predicts higher analyst forecast error (lower accuracy).**

| Component | Specification |
|-----------|---------------|
| **IV** | Complexity measure (can derive from LM dictionary: Fog index, avg syllables, etc.) |
| **DV** | Forecast error = |MEANEST - ACTUAL| / |ACTUAL| |
| **Data sources** | Text measures, IBES (25.5M rows, 264K complete verified in H5) |
| **Controls** | Firm size, earnings volatility, analyst coverage, prior dispersion |
| **Theoretical mechanism** | Complex speech confuses analysts OR signals sophisticated operations (ambiguous) |
| **Novelty** | MEDIUM - Some 10-K readability studies (Li 2008, Bloomfield 2008), not earnings calls |
| **Data feasibility** | HIGH - IBES integration verified in H5 (264K complete cases) |

**Why limited prior tests:**
- 10-K readability studied extensively (Li 2008, Bloomfield 2008)
- Earnings call complexity less studied (Gong et al. 2016 focuses on 10-Ks)
- Distinction: Earnings call complexity is spoken (interactive) vs. 10-K written

**Expected effect direction:** AMBIGUOUS (complex -> confusing = worse accuracy OR complex = competent = better accuracy)

**Measurement note:** Need to compute complexity from text measures. Options:
- Average word length (syllables per word)
- Fog index (if sentence length available)
- Proportion of complex words (LM dictionary has complexity category)

---

### Gap 6: Uncertainty -> M&A Deal Premium

**Hypothesis H11: Managerial uncertainty in earnings calls predicts lower M&A deal premium for targets.**

| Component | Specification |
|-----------|---------------|
| **IV** | CEO_QA_Uncertainty_pct, Manager_QA_Uncertainty_pct |
| **DV** | Deal premium = (Offer price - Pre-announcement price) / Pre-announcement price |
| **Data sources** | Text measures, SDC M&A (deal value, offer terms) |
| **Controls** | Target firm size, ROA, industry FE, deal characteristics (cash vs stock) |
| **Theoretical mechanism** | Uncertainty signals problems or lower quality, reducing bidder valuation |
| **Novelty** | HIGH - No studies on earnings call uncertainty -> deal pricing |
| **Data feasibility** | HIGH - SDC has premium data for 95K deals |

**Why no prior tests:**
- M&A pricing literature focuses on deal structure, synergies, market conditions
- Earnings call textual analysis focuses on market reaction, not deal pricing
- Uncertainty -> returns established, but not -> M&A-specific pricing

**Expected effect direction:** NEGATIVE (higher uncertainty -> lower premium)

---

### Gap 7: Weak Modals (Hedging) -> CEO Turnover

**Hypothesis H12: Managerial hedging language (weak modals) in earnings calls predicts lower CEO turnover probability.**

| Component | Specification |
|-----------|---------------|
| **IV** | CEO_QA_Weak_Modal_pct, Manager_QA_Weak_Modal_pct |
| **DV** | CEO turnover dummy (all departures, or forced specifically) |
| **Data sources** | Text measures, CEO dismissal data (1,059 forced + 3,852 non-forced) |
| **Controls** | Performance, tenure, firm size, industry/Year FE |
| **Theoretical mechanism** | Hedging is strategic ambiguity that protects manager from commitment; may reduce accountability |
| **Novelty** | HIGH - No studies on hedging specifically -> turnover |
| **Data feasibility** | MEDIUM - Same as Gap 2 |

**Why distinct from Gap 2:**
- Gap 2: Uncertainty (vagueness) -> turnover (expected positive)
- Gap 7: Weak modals (hedging) -> turnover (expected negative, hedging as protection)
- Tests nuance: Does hedging serve as "career insurance"?

**Expected effect direction:** NEGATIVE (hedging -> lower turnover, protective effect)

---

### Gap 8: Uncertainty Volatility -> Stock Return Volatility

**Hypothesis H13: Volatility in managerial speech uncertainty (over-time variation) predicts higher stock return volatility.**

| Component | Specification |
|-----------|---------------|
| **IV** | SD(Uncertainty) over prior 4 quarters, or absolute change vs. prior quarter |
| **DV** | Stock return volatility = SD(daily returns) in post-call period |
| **Data sources** | Text measures (time series available), CRSP DSF (daily returns) |
| **Controls** | Prior volatility, earnings volatility, firm size, industry FE |
| **Theoretical mechanism** | Inconsistent communication signals instability to markets |
| **Novelty** | MEDIUM - Demers & Vega (2018) study tone volatility, not uncertainty volatility |
| **Data feasibility** | HIGH - Both text and returns data time-series available |

**Why no prior tests:**
- Demers & Vega (2018) study tone volatility (variations in positive/negative)
- Uncertainty volatility not specifically studied
- Distinction: Tone volatility = sentiment swings; Uncertainty volatility = clarity swings

**Expected effect direction:** POSITIVE (uncertainty volatility -> return volatility)

---

### Gap 9: Q&A Uncertainty -> Analyst Forecast Revisions

**Hypothesis H14: Higher Q&A uncertainty predicts larger magnitude analyst forecast revisions.**

| Component | Specification |
|-----------|---------------|
| **IV** | Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct |
| **DV** | Forecast revision magnitude = |Forecast_rev_date1 - Forecast_pre_call| / |Forecast_pre_call| |
| **Data sources** | Text measures, IBES detailed forecasts (time-stamped) |
| **Controls** | Earnings surprise, prior dispersion, analyst coverage, firm size |
| **Theoretical mechanism** | Uncertain communication causes analysts to update beliefs more |
| **Novelty** | MEDIUM - Some studies on dispersion, fewer on revisions |
| **Data feasibility** | HIGH - IBES has forecast timestamps for revision analysis |

**Why no prior tests:**
- Focus on dispersion (cross-sectional disagreement) rather than revisions (temporal updating)
- Revisions require time-stamped forecast data (available but underutilized)

**Expected effect direction:** POSITIVE (uncertainty -> larger revisions)

---

### Gap 10: Cross-Speaker Uncertainty Dispersion -> Firm Value

**Hypothesis H15: Dispersion in uncertainty between CEO and CFO (or CEO vs. Manager) predicts lower firm value (Tobin's Q).**

| Component | Specification |
|-----------|---------------|
| **IV** | |CEO_QA_Uncertainty_pct - Manager_QA_Uncertainty_pct| (absolute difference) |
| **DV** | Tobin's Q (market value / book value of assets) |
| **Data sources** | Text measures (both CEO and Manager available), Compustat (Q) |
| **Controls** | ROA, firm size, growth opportunities, leverage, industry/Year FE |
| **Theoretical mechanism** | Inconsistent messaging across executives signals coordination problems |
| **Novelty** | HIGH - No studies on cross-speaker uncertainty differences |
| **Data feasibility** | HIGH - Both CEO and Manager measures in text data |

**Why no prior tests:**
- Brockman et al. (2015) compare executive vs. analyst speech, not CEO vs. CFO
- Focus on absolute uncertainty levels, not interpersonal differences
- Team cohesion literature doesn't include linguistic measures

**Expected effect direction:** NEGATIVE (higher dispersion -> lower Tobin's Q)

---

## 3. Hypothesis Summary Table

| Hypothesis | IV | DV | Novelty | Feasibility | Theoretical Score | Overall |
|------------|----|----|---------|-------------|-------------------|---------|
| H6 | Weak Modal % | M&A Target | HIGH (1.0) | HIGH (1.0) | Strong (1.0) | **1.00** |
| H11 | Uncertainty % | M&A Premium | HIGH (1.0) | HIGH (1.0) | Strong (1.0) | **1.00** |
| H9 | Uncertainty Gap | Abnormal Returns | HIGH (1.0) | HIGH (1.0) | Strong (1.0) | **1.00** |
| H4 | Uncertainty Gap | Volatility | HIGH (1.0) | HIGH (1.0) | Strong (1.0) | **1.00** |
| H10 | Complexity | Forecast Error | MEDIUM (0.5) | HIGH (1.0) | Moderate (0.5) | **0.65** |
| H7 | Uncertainty % | Forced Turnover | HIGH (1.0) | MEDIUM (0.5) | Strong (1.0) | **0.85** |
| H8 | Uncertainty % (inverse) | Compensation | HIGH (1.0) | MEDIUM (0.5) | Moderate (0.5) | **0.70** |
| H12 | Weak Modal % | Turnover | HIGH (1.0) | MEDIUM (0.5) | Moderate (0.5) | **0.70** |
| H13 | Uncertainty Volatility | Return Volatility | MEDIUM (0.5) | HIGH (1.0) | Moderate (0.5) | **0.65** |
| H14 | Q&A Uncertainty | Forecast Revisions | MEDIUM (0.5) | HIGH (1.0) | Moderate (0.5) | **0.65** |
| H15 | Cross-Speaker Gap | Tobin's Q | HIGH (1.0) | HIGH (1.0) | Moderate (0.5) | **0.85** |

**Scoring:**
- Novelty: HIGH=1.0 (no tests), MEDIUM=0.5 (indirect/related), LOW=0.0 (established)
- Feasibility: HIGH=1.0 (data verified), MEDIUM=0.5 (data available TBD), LOW=0.0 (missing)
- Theoretical: Strong=1.0 (clear causal story), Moderate=0.5 (ambiguous), Weak=0.0
- Overall = 0.4*Theoretical + 0.3*Novelty + 0.3*Feasibility

---

## 4. Prioritization for Power Analysis (Plan 03)

**Tier 1: Highest Priority (Overall >= 0.85)**
1. H6: Weak Modals -> M&A Target (1.00) - Novel, feasible, strong theory
2. H9: Uncertainty Gap -> Returns (1.00) - Novel measure, feasible, strong theory
3. H11: Uncertainty -> M&A Premium (1.00) - Novel, feasible, strong theory
4. H7: Uncertainty -> Turnover (0.85) - Novel, medium feasibility
5. H15: Cross-Speaker Gap -> Tobin's Q (0.85) - Novel, feasible

**Tier 2: Medium Priority (Overall 0.65-0.85)**
6. H8: Uncertainty -> Compensation (0.70)
7. H12: Weak Modals -> Turnover (0.70)
8. H10: Complexity -> Forecast Error (0.65)
9. H13: Uncertainty Volatility -> Return Volatility (0.65)
10. H14: Uncertainty -> Forecast Revisions (0.65)

---

*Phase: 41-hypothesis-suite-discovery*
*Plan: 02 - Task 3*
*Created: 2026-02-06*
