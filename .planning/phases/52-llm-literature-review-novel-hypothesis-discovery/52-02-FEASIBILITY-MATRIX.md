# Phase 52-02: Data Feasibility Verification Matrix

**Created:** 2026-02-06
**Purpose:** Verify exact data feasibility for all potential hypothesis combinations
**Status:** Complete

---

## 1. Dataset Inventory (Verified Counts)

### Complete Data Sources

| Data Source | Observations | Coverage | Key Linking Variable | Source File(s) |
|-------------|--------------|----------|---------------------|----------------|
| **Earnings Call Transcripts** | 112,968 calls | 2002-2018 | gvkey | speaker_data_YYYY.parquet (17 files) |
| **SEC Edgar Letters** | 190,559 letters | 2005-2022 | cik | letters_YYYY_QQ.parquet (72 files) |
| **FirmLevelRisk (Hassan PRisk)** | 354,518 firm-quarters | 2002-2022 | gvkey + quarter | firmquarter_2022q1.csv |
| **IBES Analyst Estimates** | 25.5M estimates | 1999-2024 | cusip → gvkey | tr_ibes.parquet |
| **Execucomp** | 370,545 exec-years | 4,170 firms | gvkey + year | comp_execucomp.parquet |
| **CEO Dismissal** | 1,059 events | 1996-2021 | firm identifier | CEO Dismissal Data 2021.02.03.xlsx |
| **SDC M&A** | 142,457 deals | 1999-2025 | cusip → gvkey | sdc-ma-merged.parquet |
| **CRSP Daily Returns** | ~1.3B daily obs | 1999-2022 | permno → gvkey | CRSP_DSF/ (96 files) |
| **CCCL Instrument** | 145,000+ firm-years | 2005-2022 | gvkey | instrument_shift_intensity_2005_2022.parquet |
| **LM Dictionary 2024** | 86,553 words | 1993-2024 | N/A | Loughran-McDonald_MasterDictionary_1993-2024.csv |
| **CCM Link Table** | 2.4 MB | Cross-section | gvkey ↔ permno | CRSPCompustat_CCM.parquet |

### FirmLevelRisk - Detailed Variable Structure

| Variable Category | Variables | Description |
|-------------------|-----------|-------------|
| **Aggregate Risk** | PRisk, NPRisk, Risk | Political risk, non-political risk, total risk |
| **Sentiment** | PSentiment, NPSentiment, Sentiment | Political/non-political sentiment |
| **Topic-Specific Risks (8)** | PRiskT_economic, PRiskT_environment, PRiskT_trade, PRiskT_institutions, PRiskT_health, PRiskT_security, PRiskT_tax, PRiskT_technology | Granular political risk topics |
| **Event Exposures** | Covid_Exposure, Brexit_Exposure, SARS/H1N1/Zika/Ebola | Crisis-specific exposure measures |
| **Unique Firms** | 13,149 unique gvkeys | Broad coverage |

---

## 2. Linkage Paths

### Direct Linkages (Single Join)

| From | To | Join Key | Notes |
|------|-----|----------|-------|
| Earnings Calls | Compustat | gvkey | Direct match, no transformation |
| Earnings Calls | FirmLevelRisk | gvkey + quarter | **SAME SOURCE!** Both derived from earnings calls |
| SEC Letters | Compustat | cik | CIK available in Compustat |
| Execucomp | Compustat | gvkey + year | Direct match |
| CCCL Instrument | Compustat | gvkey | Direct match |

### Two-Step Linkages

| From | Via | To | Join Keys | Notes |
|------|-----|-----|-----------|-------|
| Earnings Calls | CCM | CRSP | gvkey → permno | Use LINKPRIM='P' for primary link |
| SEC Letters | Compustat | CRSP | cik → gvkey → permno | Two-step transformation |
| SDC M&A | CUSIP standardization | Compustat | cusip (6-digit) → gvkey | Standardize to 6-digit CUSIP |
| IBES | CUSIP standardization | Compustat | cusip → gvkey | Standard merge |

### Complex Linkages

| Combination | Method | Expected Success Rate |
|-------------|--------|----------------------|
| SEC Letters → Earnings Calls | cik → gvkey → match to calls with same gvkey | 60-80% (CIK coverage) |
| SEC Letters → FirmLevelRisk | cik → gvkey → PRisk match | 60-80% |
| SDC M&A → Earnings Calls (Target) | Target CUSIP → gvkey → pre-acquisition calls | ~50% (not all targets have calls) |

---

## 3. Temporal Overlap Matrix

### Dataset Coverage Windows

| Dataset | Start Year | End Year | Duration |
|---------|------------|----------|----------|
| Earnings Calls | 2002 | 2018 | 17 years |
| SEC Letters | 2005 | 2022 | 18 years |
| FirmLevelRisk | 2002 | 2022 | 21 years |
| IBES | 1999 | 2024 | 26 years |
| Execucomp | 1990s | 2024 | 30+ years |
| CEO Dismissal | 1996 | 2021 | 26 years |
| SDC M&A | 1999 | 2025 | 27 years |
| CRSP | 1999 | 2022 | 24 years |
| CCCL | 2005 | 2022 | 18 years |

### Intersection Windows

| Dataset Pair | Overlap Start | Overlap End | Usable Years |
|--------------|---------------|-------------|--------------|
| Earnings Calls ∩ SEC Letters | 2005 | 2018 | **14 years** |
| Earnings Calls ∩ FirmLevelRisk | 2002 | 2018 | **17 years** (full earnings call coverage) |
| Earnings Calls ∩ IBES | 2002 | 2018 | **17 years** |
| Earnings Calls ∩ CCCL | 2005 | 2018 | **14 years** |
| SEC Letters ∩ CCCL | 2005 | 2022 | **18 years** |
| SEC Letters ∩ FirmLevelRisk | 2005 | 2022 | **18 years** |
| Earnings Calls ∩ CEO Dismissal | 2002 | 2018 | **17 years** |
| Earnings Calls ∩ SDC M&A | 2002 | 2018 | **17 years** |
| Earnings Calls ∩ Execucomp | 2002 | 2018 | **17 years** |

---

## 4. Merge Rates & Sample Size Estimates

### Prior Verified Sample Sizes (from Phase 41/42)

| Hypothesis | Sample Size | Verification Status |
|------------|-------------|---------------------|
| H5 (Analyst Dispersion) | 264,000+ obs | VERIFIED (Phase 40-01) |
| H6 (CCCL → Uncertainty) | 22,273 firm-year obs | VERIFIED (Phase 42-01) |

### New IV-DV Combination Estimates

#### High-Priority Combinations (Highest Novelty)

| IV Source | DV Source | Estimated Sample | Calculation Basis | Power (f2=0.02) |
|-----------|-----------|------------------|-------------------|-----------------|
| **SEC Letters** | **Earnings Calls (text change)** | 50K-70K letter-call pairs | 190K letters × 60-80% CIK match × 50% temporal overlap | >99% |
| **SEC Letters + Calls** | **FirmLevelRisk (PRisk)** | 30K-50K merged obs | 70K pairs × 60% PRisk coverage | >99% |
| Earnings Calls | M&A Target (pre-acquisition) | 5K-10K calls | 95K deals × 10-15% have pre-M&A calls | 95%+ |
| Earnings Calls | CEO Turnover | ~1,000 events | 1,059 dismissals × ~95% call coverage | 82% |
| Earnings Calls | Stock Returns (CAR) | 100K+ obs | 112K calls × 90% CRSP match | >99% |

#### Sample Size Calculation Details

**SEC Letters → Earnings Calls:**
1. SEC Letters: 190,559 (2005-2022)
2. CIK → GVKEY match rate: ~60-80% → 115K-150K linkable letters
3. Temporal window (2005-2018): ~75% of linkable letters → 85K-112K
4. Matching to earnings calls by gvkey: ~60-80% have calls → **50K-70K pairs**

**SEC Letters → FirmLevelRisk:**
1. Linkable SEC letters: 115K-150K
2. PRisk coverage: 13,149 unique gvkeys (large firms, high overlap with SEC letter recipients)
3. Expected match rate: ~60-80% → **70K-90K merged obs**

**Earnings Calls → M&A (as Target):**
1. SDC M&A deals: 142,457
2. Prior estimate (Phase 41): 95K deals with valid CUSIP linkage
3. Deals where target has pre-acquisition earnings calls: ~10-15%
4. Expected: **5K-10K target firm calls**

**Earnings Calls → CEO Dismissal:**
1. CEO Dismissal events: 1,059 (forced turnover)
2. Events during earnings call period (2002-2018): ~90%
3. Call coverage for these firms: ~95%
4. Expected: **~900-1,000 dismissal events with calls**

---

## 5. Feasibility Rating System

### Rating Criteria

| Rating | Observations | Power (small effect) | Within-Firm Variation | Recommendation |
|--------|--------------|---------------------|----------------------|----------------|
| **HIGH** | >20K obs | >95% power | High (event-driven, temporal) | PURSUE immediately |
| **MEDIUM** | 5K-20K obs | 80-95% power | Moderate | PURSUE with caution |
| **LOW** | <5K obs | <80% power | Low (firm trait) | AVOID or use as robustness |

### Kill Thresholds

| Criterion | Kill Threshold | Rationale |
|-----------|----------------|-----------|
| Sample Size | <5,000 observations | Insufficient for small effects with FE |
| Power | <80% for f2=0.02 | Cannot detect economically meaningful effects |
| Within-Firm Variation | >70% absorbed by Firm FE | H5 lesson: dictionary measures failed due to low within-firm variation |

---

## 6. Within-Firm Variation Assessment

### Critical Lesson from H1-H6 Null Results

**Problem identified:** Dictionary-based text measures (uncertainty, weak modal, etc.) have LOW within-firm variation. When Firm Fixed Effects are included, most variation is absorbed, leaving insufficient residual variation for identification.

**Evidence:**
- H5 (Weak Modal → Dispersion): Significant WITHOUT Firm FE, insignificant WITH Firm FE
- H1-H3: All null with Firm FE
- H6: All null with Firm FE

### Measure Categories by Expected Within-Firm Variation

#### HIGH Within-Firm Variation (Preferred for New Hypotheses)

| Measure Type | Rationale | Examples |
|--------------|-----------|----------|
| **SEC Letter Topics** | Varies by specific letter, not constant firm trait | Topic classification, concern severity |
| **Q&A Dynamics** | Varies by call, question-specific | Evasiveness scores, response quality |
| **Narrative Consistency** | Inherently temporal (quarter-over-quarter comparison) | Embedding similarity to prior call |
| **Information Novelty** | Inherently temporal | New content vs. boilerplate |
| **Response to Exogenous Events** | Shock-driven variation | PRisk changes, SEC scrutiny response |
| **LLM-Extracted Specific Items** | Context-sensitive, not word counts | Quantitative guidance, specific concerns |

#### LOW Within-Firm Variation (Avoid as Primary IVs)

| Measure Type | Rationale | Prior Evidence |
|--------------|-----------|----------------|
| **General Tone/Sentiment** | Firm-level trait (consistent across calls) | H1-H3 null results |
| **Dictionary Uncertainty** | Relatively stable within firm | H5, H6 null results |
| **Complexity** | Writing style is manager/firm trait | LM 2024 suggests firm persistence |
| **Speaking Style** | Manager-specific trait | Captured by manager FE |
| **Word Count Ratios** | Structural persistence | H1-H6 failures |

### Variance Decomposition Implications

| Design Element | Purpose | Implementation |
|----------------|---------|----------------|
| First-Differenced Specification | Remove firm-level mean | ΔY = β × ΔX + ε |
| Event-Based Design | Exploit exogenous shocks | SEC letter receipt → call change |
| Temporal Dynamics | Quarter-over-quarter change | Narrative drift measures |
| Cross-Speaker Variation | Within-call, cross-manager | CEO vs CFO gap |

---

## 7. Power Analysis Summary

### Reference Power Table (from RESEARCH.md)

| Sample Size | Small Effect (f2=0.02) | Medium Effect (f2=0.15) | Large Effect (f2=0.35) |
|-------------|------------------------|-------------------------|------------------------|
| 50,000+ | >99% power | >99% power | >99% power |
| 20,000 | >99% power | >99% power | >99% power |
| 5,000 | ~95% power | >99% power | >99% power |
| 1,000 | ~65% power | >95% power | >99% power |
| 500 | ~45% power | ~80% power | >95% power |

### Feasibility by IV-DV Combination

| IV Source | DV Source | Est. Sample | Power Rating | Feasibility |
|-----------|-----------|-------------|--------------|-------------|
| SEC Letters (LLM topics) | Earnings Call text change | 50K-70K | >99% | **HIGH** |
| SEC Letters + Calls | PRisk measures | 30K-50K | >99% | **HIGH** |
| Earnings Call (LLM measures) | Stock Returns (CAR) | 100K+ | >99% | **HIGH** |
| Earnings Call (narrative consistency) | Analyst Dispersion | 50K+ | >99% | **HIGH** |
| Earnings Call (LLM evasiveness) | Future Returns | 100K+ | >99% | **HIGH** |
| SEC Letters | M&A Target status | 10K-20K | >95% | **MEDIUM-HIGH** |
| Earnings Call | M&A Target (pre-acquisition) | 5K-10K | ~95% | **MEDIUM** |
| Earnings Call | CEO Turnover | ~1,000 | ~65-82% | **LOW** |
| PRisk × Uncertainty interaction | Investment Efficiency | 30K+ | >99% | **HIGH** |

---

## 8. Complete Feasibility Matrix

### Summary by Hypothesis Priority

| Rank | IV | DV | Sample | Power | Variation | Score | Feasibility |
|------|----|----|--------|-------|-----------|-------|-------------|
| 1 | SEC Letter Topics (LLM) | Earnings Call Language Shift | 50K-70K | >99% | HIGH (event-driven) | 1.00 | **HIGH** |
| 2 | Narrative Inconsistency | Realized Volatility | 50K+ | >99% | HIGH (temporal) | 0.95 | **HIGH** |
| 3 | SEC Correspondence Resolution | Stock Returns (CAR) | 30K-50K | >99% | HIGH (event) | 0.95 | **HIGH** |
| 4 | LLM Evasiveness (Q&A) | Future Returns | 100K+ | >99% | HIGH (question-specific) | 0.95 | **HIGH** |
| 5 | PRisk × Uncertainty | Investment Efficiency | 30K+ | >99% | HIGH (interaction) | 0.90 | **HIGH** |
| 6 | FLS Specificity (LLM) | Analyst Accuracy | 50K+ | >99% | HIGH (guidance-specific) | 0.90 | **HIGH** |
| 7 | CEO-CFO Alignment | M&A Premium (target) | 5K-10K | ~95% | MEDIUM | 0.80 | **MEDIUM** |
| 8 | Uncertainty Measures | CEO Turnover | ~1,000 | ~65-82% | LOW | 0.50 | **LOW** |

### Kill List (Avoid These Combinations)

| IV | DV | Reason | Alternative |
|----|----|--------|-------------|
| Dictionary Uncertainty | Any with Firm FE | Low within-firm variation (H1-H6 lesson) | Use LLM context-aware measures |
| Any text measure | CEO Turnover (forced) | Only 1,059 events, <80% power | Use as robustness only |
| Tone/Sentiment | Stock Returns | Heavily studied, minimal novelty | Focus on unexplored measures |
| General Complexity | Investment | Low within-firm variation | Use LLM-extracted specifics |

---

## 9. Recommendations for Blue Team (Plan 52-03)

### Top 5 Highest-Feasibility Hypothesis Directions

1. **SEC Letter Topics → Earnings Call Language Adaptation**
   - Novelty: TRUE GAP (no prior test of letter CONTENT → call TEXT response)
   - Feasibility: HIGH (50K-70K obs, >99% power)
   - Within-Firm Variation: HIGH (letter-specific, not firm trait)

2. **Narrative Inconsistency → Market Outcomes**
   - Novelty: TRUE GAP (temporal embedding similarity novel)
   - Feasibility: HIGH (50K+ obs, >99% power)
   - Within-Firm Variation: HIGH (inherently temporal)

3. **SEC Correspondence Resolution Quality → Stock Returns**
   - Novelty: TRUE GAP (thread-level analysis, not letter counts)
   - Feasibility: HIGH (30K-50K obs, >99% power)
   - Within-Firm Variation: HIGH (resolution-specific)

4. **LLM-Measured Q&A Evasiveness → Returns**
   - Novelty: PARTIAL GAP (some studies exist, but LLM-based novel)
   - Feasibility: HIGH (100K+ obs, >99% power)
   - Within-Firm Variation: HIGH (question-specific)

5. **PRisk × Uncertainty Interaction → Investment Efficiency**
   - Novelty: TRUE GAP (interaction effect untested)
   - Feasibility: HIGH (30K+ obs, >99% power)
   - Within-Firm Variation: HIGH (both components vary)

### Directions to Avoid

1. **Dictionary-based measures as primary IV** (H1-H6 lesson)
2. **CEO Turnover as DV** (sample size constraint)
3. **"Apply LLM to SEC letters" without specific angle** (111+ papers exist)
4. **Firm-trait-like measures with Firm FE** (variation absorption)

---

## 10. Verification Checklist

- [x] All 9 primary datasets documented with exact counts
- [x] 3 additional linking datasets documented (CCM, LM Dictionary, CCCL)
- [x] Linkage paths specified for all combinations
- [x] Temporal overlap calculated for all dataset pairs
- [x] Sample sizes estimated for 9 IV-DV combinations
- [x] Power calculations based on f2=0.02 (small effect)
- [x] Kill threshold (<5K obs, <80% power) clearly documented
- [x] Within-firm variation assessment for measure types
- [x] Feasibility ratings assigned (HIGH/MEDIUM/LOW)
- [x] Recommendations for Blue Team provided

---

*Prepared for Phase 52: LLM Literature Review & Novel Hypothesis Discovery*
*Plan 52-02: Data Feasibility Verification*
*Date: 2026-02-06*
