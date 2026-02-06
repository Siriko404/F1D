# Phase 52: LLM Literature Review & Novel Hypothesis Discovery - Research

**Researched:** 2026-02-06 (UPDATED)
**Domain:** LLM-based Earnings Call Analysis & Novel Hypothesis Generation
**Confidence:** MEDIUM-HIGH

---

## Summary

Phase 52 represents a strategic pivot from dictionary-based textual analysis (which produced null results across H1-H6) to LLM-based approaches for earnings call analysis. This research synthesizes the latest (2023-2026) developments in LLM textual analysis of financial disclosures and establishes a rigorous red-team/blue-team methodology for identifying 5 novel hypotheses with extremely high confidence for statistical significance.

**CRITICAL CONTEXT:** Prior hypotheses (H1-H6) using Loughran-McDonald dictionary measures ALL produced null results. This demonstrates that simple word-count approaches lack predictive power for corporate outcomes. Phase 52 must identify fundamentally different measurement approaches.

**IMPORTANT UPDATE (2026-02-06):** Research verification reveals that:
1. **SEC Comment Letter textual analysis is NOT unexplored** - 111+ papers on SSRN, with recent ML/NLP work (2022-2024) including LLM applications
2. **True novelty must be more specific** than simply "apply LLM to SEC letters"
3. **Novel angles exist** in unexplored IV-DV combinations and integration with earnings call dynamics

**Primary recommendation:** Prioritize hypotheses that leverage UNIQUE data linkages (SEC letters + earnings calls + FirmLevelRisk) to create novel causal chains not previously tested.

---

## Key Data Sources Verified

### Complete Data Inventory (Verified 2026-02-06)

| Data Source | Files | Observations | Key Variables | Coverage |
|-------------|-------|--------------|---------------|----------|
| **Earnings Call Transcripts** | 17 parquet files | 112,968 calls | Full transcript, speaker roles, speaker_text | 2002-2018 |
| **SEC Edgar Comment Letters** | 72 parquet files | **190,559 letters** | letter_id, cik, form_type, filing_date, **full_text** | 2005-2022 |
| **FirmLevelRisk** | 1 CSV file | **354,518 firm-quarters** | PRisk, NPRisk, 8 topic-specific risks, Covid/Brexit exposure | 2002-2022 |
| **IBES Analyst Estimates** | 1 parquet file | 25.5M estimates | MEANEST, STDEV, NUMEST, ACTUAL, forecast error | 1999-2024 |
| **Execucomp** | 1 parquet file | 370,545 exec-years | salary, bonus, TDC1, option_awards | 4,170 firms |
| **CEO Dismissal** | 1 Excel file | 1,059 events | Forced turnover indicator | 1996-2021 |
| **SDC M&A** | 1 parquet file | 142,457 deals | Target/Acquiror CUSIP, Deal Value, Deal Premium | 1999-2025 |
| **CRSP Daily Returns** | 96 parquet files | ~1.3B daily obs | ret, prc, vol, shrout | 1999-2022 |
| **LM Dictionary 2024** | 1 CSV file | 86,553 words | 8 categories + NEW Complexity (53 words) | 1993-2024 |
| **CCCL Instrument** | 2 files | 145,000+ firm-years | shift_intensity variants | 2005-2022 |

### SEC Edgar Letters - Sample Content Analysis

```
Sample letter (2020 Q1):
"march 6, 2020 fabian souza senior vice president and corporate controller 
exelon corp... re:exelon corp form 10-k for the fiscal year ended december 31, 
2019... we have reviewed your filing and have the following comments...
1.you disclose that if generation's state-supported nuclear plants in pjm or 
nyiso are subjected to the minimum offer price rule (mopr) without compensation 
under an fixed resource requirement (frr) or similar program, it could have a 
material adverse impact..."

Average text length: 2,786 characters
Median text length: 1,876 characters
Range: 505 - 23,693 characters
```

### FirmLevelRisk - Variable Structure

| Variable Category | Variables | Description |
|-------------------|-----------|-------------|
| **Aggregate Risk** | PRisk, NPRisk, Risk | Political risk, non-political risk, total risk |
| **Sentiment** | PSentiment, NPSentiment, Sentiment | Political/non-political sentiment |
| **Topic-Specific Risks (8)** | PRiskT_economic, PRiskT_environment, PRiskT_trade, PRiskT_institutions, PRiskT_health, PRiskT_security, PRiskT_tax, PRiskT_technology | Granular political risk topics |
| **Event Exposures** | Covid_Exposure, Brexit_Exposure, SARS/H1N1/Zika/Ebola | Crisis-specific exposure measures |
| **Identifiers** | gvkey, cusip, ticker, isin | Standard linking variables |

---

## LLM Literature Summary (2023-2026)

### Major Paradigm Shifts

| Era | Approach | Limitation | State-of-Art Papers |
|-----|----------|------------|---------------------|
| 2011-2020 | Dictionary-based (LM) | Word counts, no context | Loughran & McDonald (2011) |
| 2019-2022 | BERT/FinBERT | 512 token limit, sentence-level | Araci (2019), Huang et al. (2023) |
| 2023-2026 | GPT-4/LLMs | Full transcript, reasoning | Kelly et al. (2024), Kim et al. (2024) |

### Key 2023-2026 Research Papers

#### 1. Financial Statement Analysis with LLMs (Kim, Muhn, Nikolaev 2024)
- **Core Finding:** GPT-4 predicts future earnings direction more accurately than human analysts (60% vs 53-57%)
- **Method:** Standardized financial statements + transcript summaries fed to LLM with Chain-of-Thought prompting
- **Alpha Generation:** Long-short strategy from LLM "analyst" generates significant abnormal returns
- **Confidence:** HIGH (Chicago Booth, Journal of Accounting Research forthcoming)

#### 2. Expected Returns and Large Language Models (Kelly, Xiu, Chen 2024)
- **Core Finding:** LLMs create text-based factors predicting cross-sectional stock returns
- **Method:** GPT-4 digests corporate text to measure "expected returns" more accurately than linear models
- **Implication:** Text is the new "fundamental data" - not just sentiment, but narrative structure
- **Confidence:** HIGH (Bryan Kelly/AQR, top-tier journal quality)

#### 3. Can ChatGPT Forecast Stock Price Movements? (Lopez-Lira & Tang 2023/2024)
- **Core Finding:** ChatGPT sentiment scores correlate with subsequent stock returns
- **Method:** Zero-shot sentiment classification of news/disclosures
- **Outperformance:** Beats traditional sentiment vendors (RavenPack)
- **Confidence:** HIGH (most cited recent paper in this space)

#### 4. Market Reactions to Earnings Calls with GPT-4o (Van Mook 2024)
- **Core Finding:** GPT-4o better at detecting "financial nuance" including management's tone on guidance
- **Method:** Multimodal analysis of earnings call transcripts
- **Market Correlation:** Higher correlation with t+1 volatility than BERT-based models
- **Confidence:** MEDIUM (Tilburg University working paper)

### SEC Comment Letter Literature (CRITICAL UPDATE)

**FINDING:** SEC comment letter textual analysis is NOT unexplored terrain. SSRN shows 111+ papers on this topic.

#### Recent SEC Comment Letter Research (2022-2024)

| Study | Method | Finding |
|-------|--------|---------|
| **Wang et al. (2024/2025)** | LLM | "Machine-Readable Disclosures Facilitate Regulatory Scrutiny" - Uses LLM with inline XBRL |
| **Ryans (2019)** | Topic Modeling | "Textual Classification of SEC Comment Letters" - Review of Accounting Studies |
| **Hu & Zhang (2024)** | Naive Bayes | "Spillover Effect" - SEC letters improve clarity of subsequent qualitative disclosures |
| **Olsen & Hassan (2023/2024)** | ML (CLARITY) | Framework for optimizing SEC letter analysis from EDGAR |
| **Arakelyan et al. (2023)** | LLM | "Stance Detection" - Identifies defensive/compliant/aggressive response styles |
| **Cunningham & Leidner (2022)** | Textual Analysis | Earnings call linguistic cues predict SEC scrutiny topics |

**Implication:** Simple "apply LLM to SEC letters" is NOT novel. Novelty must come from:
1. **Unexplored IV-DV combinations** (e.g., SEC letter topics → earnings call language change)
2. **Data integration** (SEC letters + earnings calls + PRisk measures)
3. **Specific LLM capabilities** not yet applied (e.g., correspondence thread analysis)

---

## Novel Hypothesis Generation Methodology

### Red-Team/Blue-Team Verification Framework

Based on research on hypothesis generation frameworks, systematic approach ensures only truly novel, feasible, high-confidence hypotheses survive.

#### Phase 1: Blue Team - Hypothesis Generation
**Objective:** Generate candidate hypotheses using abductive reasoning

1. **Observation Mining:**
   - Review H1-H6 null results for patterns (dictionary measures failed)
   - Identify anomalies in prior literature that weren't tested
   - Map LLM capabilities to untested relationships

2. **Abductive Generation:**
   - For each observation, ask: "What hypothesis, if true, would explain this?"
   - Cross-disciplinary exploration
   - Generate 20-30 candidates

#### Phase 2: Red Team - Adversarial Verification
**Objective:** Attempt to debunk each hypothesis with kill criteria

| Challenge | Kill Threshold | Evidence Required |
|-----------|----------------|-------------------|
| **Literature Gap** | Direct prior test with >500 observations | Paper citation, sample size |
| **Data Feasibility** | <5,000 observations after merges | Actual merge verification |
| **Power** | <80% power for small effect (f2=0.02) | Power calculation |
| **Mechanism** | No clear causal story | Theoretical justification |

#### Phase 3: Survival Assessment

| Dimension | Weight | Scoring Criteria |
|-----------|--------|------------------|
| **Novelty** | 0.35 | No prior direct test (1.0), Related tests exist (0.7), Incremental (0.4) |
| **Feasibility** | 0.35 | All data available (1.0), Minor construction (0.8), Major gaps (0.5) |
| **Confidence** | 0.30 | >95% power for small effect (1.0), 80-95% (0.8), <80% (0.5) |

**Selection Criterion:** Overall Score >= 0.85 for "extremely high confidence"

### The 5E Rule for Hypothesis Quality

Each selected hypothesis MUST satisfy:
1. **Explicit:** Clearly stated IV → DV relationship with expected sign
2. **Evidence-based:** Rooted in prior literature or theory
3. **Ex-ante:** Formulated BEFORE testing (no HARKing)
4. **Explanatory:** Provides a "why" mechanism
5. **Empirically Testable:** Operationalizable with available data

---

## High-Priority Hypothesis Candidates (Updated with Novelty Verification)

### Tier 1: HIGHEST NOVELTY (Data Integration + LLM)

These hypotheses leverage UNIQUE data linkages not found in prior literature:

| # | Hypothesis | IV | DV | Novelty Rationale | Prior Tests |
|---|------------|----|----|-------------------|-------------|
| **1** | **SEC Letter Topics → Earnings Call Language Shift** | LLM-extracted SEC concern topics | Change in next earnings call uncertainty/specificity | Causal chain: SEC scrutiny → management disclosure adaptation | No direct test of SEC letter CONTENT → earnings call TEXT response |
| **2** | **Regulatory Correspondence Resolution → Stock Reaction** | LLM-measured correspondence thread resolution quality | CAR around letter sequence completion | Full correspondence dynamics, not just letter receipt | Prior work uses letter counts, not resolution quality |
| **3** | **PRisk-Uncertainty Interaction → Investment Efficiency** | Hassan PRisk × our text uncertainty interaction | Biddle investment residual | Integration of two established text measures | Topic-specific risk × uncertainty interaction untested |

### Tier 2: HIGH NOVELTY (LLM + Earnings Calls)

| # | Hypothesis | IV | DV | Novelty Rationale |
|---|------------|----|----|-------------------|
| **4** | **CEO Q&A Evasiveness → Negative Returns** | LLM-measured response relevance (not word counts) | CAR around call | Evasiveness QUALITY not dictionary-based counts |
| **5** | **Narrative Inconsistency Across Quarters → Volatility** | Embedding similarity between current and prior call | Realized volatility | Temporal dimension of text measures novel |
| **6** | **FLS Specificity → Analyst Accuracy** | LLM-classified quantitative vs. vague guidance | Forecast error | Forward-looking statement QUALITY not presence |
| **7** | **CEO-CFO Tone Alignment → M&A Premium** | Cross-speaker sentiment gap | Deal premium when target | Multi-speaker dynamics in M&A context |

### Tier 3: MEDIUM NOVELTY (Political Risk Integration)

| # | Hypothesis | IV | DV | Novelty Rationale |
|---|------------|----|----|-------------------|
| **8** | **Topic-Specific Political Risk → Sector Rotation** | PRiskT_* (8 topics) | Industry-adjusted returns | Granular topic-specific risk pricing |
| **9** | **Covid/Brexit Exposure → Analyst Dispersion** | Event exposure measures | Forecast dispersion | Event-driven uncertainty transmission |
| **10** | **PRisk × Leverage → Speech Discipline** | PRisk × leverage interaction | Next quarter uncertainty change | Risk-leverage discipline channel |

### Tier 4: DICTIONARY EXTENSION (Lower Novelty)

| # | Hypothesis | IV | DV | Novelty Rationale |
|---|------------|----|----|-------------------|
| **11** | **LM Complexity (2024) → Investment Efficiency** | New 2024 Complexity category | Biddle residual | New dictionary category just released |
| **12** | **Information Novelty → Price Discovery** | Embedding-based content novelty | Trading volume | Semantic novelty vs. word count novelty |

### Critical Novelty Assessment

| Hypothesis | Literature Gap Status | Risk Level |
|------------|----------------------|------------|
| SEC Letter → Earnings Call | TRUE GAP: No prior test of letter CONTENT → call TEXT | LOW RISK |
| Correspondence Resolution | TRUE GAP: Thread-level analysis novel | LOW RISK |
| PRisk × Uncertainty | TRUE GAP: Interaction effect untested | LOW RISK |
| CEO Evasiveness | PARTIAL GAP: Some evasiveness studies exist, but LLM-based novel | MEDIUM RISK |
| Narrative Consistency | TRUE GAP: Temporal embedding similarity novel | LOW RISK |
| FLS Specificity | PARTIAL GAP: FLS studies exist, but LLM quality measure novel | MEDIUM RISK |
| CEO-CFO Alignment | TRUE GAP in M&A context | LOW RISK |

---

## LLM Implementation Approaches

### Approach 1: Zero-Shot Classification with GPT-4

**Prompt Engineering Templates:**

```markdown
## SEC Letter Concern Extraction
"Analyze this SEC comment letter. For each comment:
- Extract the specific disclosure concern (revenue recognition, risk factors, etc.)
- Rate severity (1-5 scale) based on language intensity
- Identify if this is a request for clarification vs. demand for change
- Classify the accounting/disclosure topic area"

## Evasiveness Detection
"Analyze the Q&A section. For each question:
- Extract the specific metric the analyst asked about
- Evaluate the executive's response for evasiveness (1-5 scale)
- Note if response addressed a DIFFERENT topic than asked
- List any metrics requested but not provided"

## Forward-Looking Statement Quality
"Extract all forward-looking statements from management remarks.
For each FLS:
- Classify as Quantitative (specific numbers) or Qualitative (vague)
- Identify time horizon (Q1, FY, multi-year)
- Rate confidence level expressed by management (1-5)"
```

**Best for:** Rich semantic extraction, reasoning-intensive measures

### Approach 2: Embedding-Based Similarity

**Applications:**
1. **Information Novelty:** Cosine similarity between current and prior call embeddings
2. **Response Quality:** Similarity between analyst question and CEO answer embeddings
3. **Narrative Consistency:** Quarter-over-quarter semantic drift

**Implementation:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Narrative consistency
current_embedding = model.encode(current_call_text)
prior_embedding = model.encode(prior_call_text)
consistency_score = cosine_similarity(current_embedding, prior_embedding)

# Q&A alignment
question_embedding = model.encode(analyst_question)
answer_embedding = model.encode(ceo_response)
alignment_score = cosine_similarity(question_embedding, answer_embedding)
```

**Best for:** Scalable similarity measures, reproducible

### Approach 3: Hybrid Dictionary + LLM

**Rationale:** Combine validated dictionary measures with LLM enhancement

1. Use LM dictionary for baseline uncertainty (established)
2. Use LLM to classify ambiguous cases or context-dependent words
3. Use LLM to extract information NOT in dictionary

**Best for:** Building on established literature while adding novelty

### Recommended Technical Stack

| Component | Recommended Tool | Purpose |
|-----------|------------------|---------|
| Text Preprocessing | spaCy/NLTK | Tokenization, sentence segmentation |
| Dictionary Measures | LM Dictionary 2024 | Baseline uncertainty, weak modals |
| Sentence Embeddings | sentence-transformers | Similarity, clustering |
| LLM API | GPT-4o via API | Rich semantic extraction |
| Local LLM | Ollama + Llama 3 | Privacy-preserving, reproducible |
| Panel Regression | linearmodels | Fixed effects, clustering |

---

## Power Analysis Summary

For panel data with Firm + Year FE, using existing sample sizes:

| Sample Size | Small Effect (f2=0.02) | Medium Effect (f2=0.15) | Large Effect (f2=0.35) |
|-------------|------------------------|-------------------------|------------------------|
| 50,000+ | >99% power | >99% power | >99% power |
| 20,000 | >99% power | >99% power | >99% power |
| 5,000 | ~95% power | >99% power | >99% power |
| 1,000 | ~65% power | >95% power | >99% power |

**Critical Insight from H1-H6:** All had >99% power for small effects. Null results = TRUE NULL, not power issue. New hypotheses must find REAL effects.

---

## Common Pitfalls to Avoid

### Pitfall 1: LLM Measure Instability
**Problem:** GPT-4 outputs vary with temperature and prompt wording
**Solution:** 
- Temperature = 0 for all extractions
- Standardized prompts with validation sets
- Report inter-rater reliability for LLM measures

### Pitfall 2: Confusing LLM Capability with Hypothesis Novelty
**Problem:** "We used GPT-4" is not a contribution; the hypothesis must be novel
**Solution:** 
- Novelty comes from WHAT you measure, not HOW you measure
- LLM is a tool; the theoretical insight is the contribution

### Pitfall 3: Insufficient Within-Firm Variation
**Problem:** Fixed effects absorb most text measure variation (H5 lesson)
**Solution:**
- Pre-calculate within-firm variance of candidate IVs
- Prefer measures with high temporal variation
- Consider first-differenced specifications

### Pitfall 4: P-hacking Through Measure Selection
**Problem:** Trying 1,785 text measures until one works
**Solution:**
- Pre-specify primary measure before running regressions
- Use FDR correction if testing multiple measures
- Report ALL specifications, not just significant ones

### Pitfall 5: Claiming SEC Letter Analysis is Novel
**Problem:** 111+ papers exist on SEC comment letter textual analysis
**Solution:**
- Be specific about WHAT aspect is novel
- Focus on unexplored IV-DV combinations
- Emphasize data integration (SEC + earnings calls + PRisk)

---

## State of the Art (2026)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Dictionary word counts | LLM semantic extraction | 2023-2024 | Context-aware, nuanced measures |
| Sentence-level (BERT) | Full transcript (GPT-4) | 2024 | Long-range dependencies captured |
| Text-only analysis | Multimodal (text + audio) | 2024-2025 | Detect tone-text mismatch |
| Static measures | Dynamic (across time) | 2024 | Narrative consistency measures |
| Single-speaker | Multi-speaker dynamics | 2023-2024 | CEO-CFO, CEO-Analyst interactions |
| Positive/Negative | Multi-dimensional tone | 2024 | Confidence, transparency, urgency |
| SEC letter counts | SEC letter text content | 2022-2024 | Topic, severity, resolution analysis |

**Emerging frontiers (2025-2026):**
- Multi-agent LLM frameworks (hypothesis generator + adversarial debunker)
- Knowledge distillation (GPT-4 labels → smaller reproducible models)
- Causal LLM reasoning (counterfactual analysis)
- SEC-firm correspondence thread analysis

---

## Recommended Planning Approach

### Phase 52 Execution Strategy

**Given the non-negotiable constraints:**
1. Ideas MUST be untested, unprecedented, and high in novelty
2. Ideas MUST be data-feasible (achievable with available data)
3. Ideas MUST have extremely high confidence of statistical significance

**5-Plan Structure:**

#### Plan 52-01: Literature Deep Dive & Evidence Matrix
- Exhaustive search of 2023-2026 LLM + earnings call papers
- Create evidence matrix: What IVs have been tested with which DVs?
- Identify TRUE literature gaps (not just extensions)
- **Output:** Literature gap matrix, capability inventory

#### Plan 52-02: Data Feasibility Verification
- Verify exact merge rates for all dataset combinations
- Calculate within-firm variation for text measures
- Check temporal overlap between datasets
- **Output:** Updated feasibility matrix with verified numbers

#### Plan 52-03: Blue Team - Candidate Generation
- Generate 20-30 candidate hypotheses from gaps
- Document theoretical mechanism for each
- Preliminary scoring
- **Output:** Ranked candidate list

#### Plan 52-04: Red Team - Adversarial Verification
- Apply kill criteria to each candidate
- Document specific reasons for survival/rejection
- **Output:** Verified survivors with full documentation

#### Plan 52-05: Final Selection & Specification
- Select top 5 hypotheses with scores >= 0.85
- Write complete implementation specifications
- **Output:** 5 hypothesis specification documents

---

## Open Questions

1. **LLM Reproducibility:**
   - What we know: GPT-4 outputs can vary
   - What's unclear: Best practices for academic reproducibility
   - Recommendation: Use local models (Llama 3) or cache all API responses

2. **Within-Firm Variation of LLM Measures:**
   - What we know: Dictionary measures have low within-firm variance
   - What's unclear: Do LLM measures vary more within firms?
   - Recommendation: Compute ICC for candidate measures before committing

3. **SEC Letter → Earnings Call Linkage:**
   - What we know: Both have CIK/GVKEY identifiers
   - What's unclear: Exact temporal alignment (which call follows which letter?)
   - Recommendation: Map letter dates to subsequent earnings call dates

4. **Computational Cost:**
   - What we know: 112,968 calls + 190,559 letters × GPT-4 API = expensive
   - What's unclear: Budget constraints
   - Recommendation: Prioritize measures that can be computed locally

---

## Sources

### Primary (HIGH confidence)
- Kim, Muhn, Nikolaev (2024) - "Financial Statement Analysis with Large Language Models"
- Kelly, Xiu, Chen (2024) - "Expected Returns and Large Language Models"
- Lopez-Lira & Tang (2023/2024) - "Can ChatGPT Forecast Stock Price Movements?"
- Hassan et al. (2019) - "Firm-Level Political Risk: Measurement and Effects" (QJE)
- Loughran & McDonald (2024) - "Measuring Firm Complexity" (JFQA)
- PRISMA 2020 Statement - Systematic review methodology

### Secondary (MEDIUM confidence)
- Wang et al. (2024/2025) - "Machine-Readable Disclosures Facilitate Regulatory Scrutiny"
- Ryans (2019) - "Textual Classification of SEC Comment Letters" (RAST)
- FinGPT documentation and 2024 papers
- Van Mook (2024) - "Market Reactions to Earnings Calls with GPT-4o"
- Cunningham & Leidner (2022) - Earnings call cues predict SEC scrutiny

### Tertiary (LOW confidence - needs verification)
- Web search results on Q&A dynamics, evasiveness detection
- Various ArXiv preprints on financial NLP
- SSRN working papers on SEC comment letters

---

## Metadata

**Confidence breakdown:**
- LLM Literature Summary: HIGH - Based on recent high-profile papers
- SEC Letter Literature: MEDIUM - Discovered 111+ papers exist (novelty claims refined)
- Data Inventory: HIGH - Verified actual file counts and structures
- Novel Hypothesis Methodology: MEDIUM - Framework synthesized from multiple sources
- Implementation Approaches: HIGH - Technical stack well-established

**Research date:** 2026-02-06 (Updated)
**Valid until:** 2026-05-06 (LLM field evolving rapidly)

**Critical success factors for Phase 52:**
1. TRUE literature gaps, not incremental extensions
2. LLM measures must have HIGH within-firm variance
3. Red-team must KILL weak hypotheses ruthlessly
4. Final 5 must survive ALL adversarial challenges
5. Pre-specification before any data analysis
6. **SEC letter analysis must be SPECIFIC** - general "LLM on SEC letters" is not novel
7. **Leverage data integration** - SEC + earnings calls + PRisk together is novel
8. **Focus on unexplored IV-DV combinations** within existing literature

---

## Appendix: Complete File Inventory (Verified)

### 1_Inputs/ Directory Structure

```
1_Inputs/
├── CCCL instrument/
│   ├── instrument_shift_intensity_2005_2022.parquet (CCCL shift-share instrument)
│   └── instrument_variable_reference.csv
│
├── CEO Dismissal Data 2021.02.03.xlsx (1,059 forced turnover events)
│
├── CRSPCompustat_CCM/
│   ├── CRSPCompustat_CCM.parquet (2.4 MB, GVKEY-PERMNO linking)
│   └── CRSP_CCM_Variable_Reference.csv
│
├── CRSP_DSF/ (96 quarterly files, 1999-2022)
│
├── Execucomp/
│   └── comp_execucomp.parquet (370,545 executive-years)
│
├── FirmLevelRisk/
│   └── firmquarter_2022q1.csv (354,518 firm-quarters, 13,149 unique gvkeys)
│       - PRisk, NPRisk, Sentiment (aggregate)
│       - PRiskT_* (8 topic-specific risks)
│       - Covid/Brexit/SARS/H1N1/Zika/Ebola exposure
│
├── Loughran-McDonald_MasterDictionary_1993-2024.csv (86,553 words)
│
├── SDC/
│   └── sdc-ma-merged.parquet (142,457 M&A deals)
│
├── SEC Edgar Letters/ (72 files, 2005-2022)
│   └── letters_YYYY_QQ.parquet (190,559 total letters)
│       - letter_id, cik, form_type, filing_date
│       - full_text (ACTUAL LETTER CONTENT)
│       - Average text length: 2,786 chars
│
├── Unified-info.parquet (465,434 call metadata records)
│
├── comp_na_daily_all/
│   └── comp_na_daily_all.parquet (Compustat fundamentals)
│
├── speaker_data_YYYY.parquet (17 files, 2002-2018, 112,968 calls)
│
└── tr_ibes/
    └── tr_ibes.parquet (25.5M analyst estimates)
```

### Key Linking Variables

| From | To | Link Key | Notes |
|------|-----|----------|-------|
| Earnings Calls | Compustat | gvkey | Direct |
| Earnings Calls | FirmLevelRisk | gvkey + quarter | Same source! |
| SEC Letters | Compustat | cik | Direct |
| SEC Letters | CRSP | cik → gvkey → permno | Two-step |
| Execucomp | Compustat | gvkey + year | Direct |
| SDC M&A | Compustat | cusip (6-digit) → gvkey | Standardize CUSIP |

---

*Research conducted for Phase 52: LLM Literature Review & Novel Hypothesis Discovery*
*Project: F1D Earnings Call Analysis*
*Last Updated: 2026-02-06*
