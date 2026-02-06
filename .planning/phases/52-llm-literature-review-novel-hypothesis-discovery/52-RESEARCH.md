# Phase 52: LLM Literature Review & Novel Hypothesis Discovery - Research

**Researched:** 2026-02-06
**Domain:** LLM-based Earnings Call Analysis & Novel Hypothesis Generation
**Confidence:** MEDIUM-HIGH

---

## Summary

Phase 52 represents a strategic pivot from dictionary-based textual analysis (which produced null results across H1-H6) to LLM-based approaches for earnings call analysis. This research synthesizes the latest (2023-2026) developments in LLM textual analysis of financial disclosures and establishes a rigorous red-team/blue-team methodology for identifying 5 novel hypotheses with extremely high confidence for statistical significance.

**CRITICAL UPDATE (2026-02-06):** Initial research MISSED two major data sources that dramatically expand hypothesis possibilities:

1. **SEC Edgar Comment Letters (150K+ letters, 2005-2022):** Full TEXT of SEC-firm regulatory correspondence. This is a GOLDMINE for LLM analysis — no prior academic work has applied LLMs to extract SEC concerns, severity, or topic content from these letters.

2. **FirmLevelRisk (354K firm-quarters, 2002-2022):** Hassan et al. (2019) political risk measures computed from the SAME earnings calls. Provides validated benchmark measures (PRisk, 8 topic-specific risks, event exposures) for comparison and interaction effects.

The key insight from recent literature: **LLMs have fundamentally changed what's measurable in earnings calls**. Beyond sentiment, modern approaches extract:
1. **Reasoning quality** - How well does management explain cause-effect relationships?
2. **Response evasiveness** - Does the CEO answer what was actually asked?
3. **Information novelty** - What's new vs. repeated boilerplate?
4. **Regulatory concern extraction** - What specific issues does the SEC raise? (NEW!)
5. **Strategic narrative shifts** - How does story change quarter-over-quarter?

**Primary recommendation:** Prioritize hypotheses using SEC Edgar Letters (Tier 1) because:
- Full letter TEXT available for LLM analysis (not just receipt counts)
- No prior LLM-based academic analysis of this corpus
- Creates natural regulatory shock → firm response → market outcome chain
- Large sample with rich textual content

---

## LLM Literature Summary (2023-2026)

### Major Paradigm Shifts

| Era | Approach | Limitation | State-of-Art Papers |
|-----|----------|------------|---------------------|
| 2011-2020 | Dictionary-based (LM) | Word counts, no context | Loughran & McDonald (2011) |
| 2019-2022 | BERT/FinBERT | 512 token limit, sentence-level | Araci (2019), Huang et al. (2023) |
| 2023-2026 | GPT-4/LLMs | Full transcript, reasoning | Kelly et al. (2024), Kim et al. (2024) |

### Key 2023-2026 Research Papers

#### 1. Expected Returns and Large Language Models (Kelly, Xiu, Chen 2024)
- **Core Finding:** LLMs create text-based factors predicting cross-sectional stock returns
- **Method:** GPT-4 digests corporate text to measure "expected returns" more accurately than linear models
- **Implication:** Text is the new "fundamental data" - not just sentiment, but narrative structure
- **Confidence:** HIGH (Bryan Kelly/AQR, top-tier journal quality)

#### 2. Financial Statement Analysis with LLMs (Kim, Muhn, Nikolaev 2024)
- **Core Finding:** GPT-4 predicts future earnings direction more accurately than human analysts
- **Method:** Standardized financial statements + transcript summaries fed to LLM
- **Alpha Generation:** Long-short strategy from LLM "analyst" generates significant abnormal returns
- **Implication:** LLM-based measures have predictive power for real outcomes
- **Confidence:** HIGH (Chicago Booth, forthcoming in Journal of Accounting Research)

#### 3. Can ChatGPT Forecast Stock Price Movements? (Lopez-Lira & Tang 2023/2024)
- **Core Finding:** ChatGPT sentiment scores correlate with subsequent stock returns
- **Method:** Zero-shot sentiment classification of news/disclosures
- **Outperformance:** Beats traditional sentiment vendors (RavenPack)
- **Confidence:** HIGH (most cited recent paper in this space)

#### 4. FinGPT-Forecaster (2024)
- **Core Finding:** LLM fine-tuned to predict stock movements directly from earnings call transcripts
- **Method:** Low-Rank Adaptation (LoRA) on Llama 2-13B with Dow 30 data
- **Implication:** End-to-end prediction possible without intermediate measures
- **Confidence:** MEDIUM (open-source, active development)

#### 5. FinDPO: Direct Preference Optimization (2024/2025)
- **Core Finding:** Preference-optimized LLMs reduce "hallucinated" sentiment in earnings calls
- **Method:** Training on human/expert preference pairs
- **Implication:** Quality of LLM-extracted measures improving rapidly
- **Confidence:** MEDIUM (ArXiv, recent)

### Q&A Dynamics Research (2023-2024)

| Research Theme | Key Finding | Novel Measure | Reference |
|----------------|-------------|---------------|-----------|
| **Evasiveness Detection** | CEO evasive language predicts bad news | Question-Answer relevance score | Multiple 2024 papers |
| **Language Style Matching** | CEO mimicry of analyst style signals cooperation | LSM break detection | 2023 Contemporary Accounting Research |
| **Prognostic Questioning** | Analyst questions forcing FLS have more price discovery | Question argumentative structure | INFORMS 2024 |
| **Non-Answer Detection** | AI detects "non-answers" in real-time | Informativeness Score | 2024 industry research |
| **Tone Dispersion** | Analyst-CEO sentiment gap predicts volatility | Dispersion between participants | American Finance Association 2024 |

### Multimodal Analysis (Text + Audio)

**Emerging 2024-2025 frontier:** Combining text and audio analysis:
- **Hajek & Munk (2024):** Speech Emotion Recognition (SER) + text sentiment detects "managerial obfuscation" text models miss
- **FinBERT-Acoustic:** Text (FinBERT) + audio (Wav2Vec 2.0) unified sentiment score
- **Key Finding:** When text is positive but vocal tone is anxious, market makers increase price impact

### LM Dictionary 2024 Update

The Loughran-McDonald dictionary received a 2024 update:
- **New Category:** Complexity (374 words) - measures complex economic activities
- **Publication:** "Measuring Firm Complexity" (JFQA 2024)
- **Maintained Categories:** Negative, Positive, Uncertainty, Litigious, Strong Modal, Weak Modal, Constraining
- **Implication:** Complexity category NOW AVAILABLE for hypothesis testing

---

## Novel Hypothesis Generation Methodology

### Red-Team/Blue-Team Verification Framework

Based on research on hypothesis generation frameworks, the following systematic approach is recommended:

#### Phase 1: Blue Team - Hypothesis Generation
**Objective:** Generate candidate hypotheses using abductive reasoning

1. **Observation Mining:**
   - Review H1-H6 null results for patterns
   - Identify anomalies in prior literature that weren't tested
   - Map LLM capabilities to untested relationships

2. **Abductive Generation:**
   - For each observation, ask: "What hypothesis, if true, would explain this?"
   - Use AI-augmented brainstorming (RAG over literature)
   - Cross-disciplinary exploration (apply concepts from other fields)

3. **Candidate Pool:**
   - Generate 20-30 candidate hypotheses
   - Document theoretical mechanism for each
   - Preliminary data feasibility check

#### Phase 2: Red Team - Adversarial Verification
**Objective:** Attempt to debunk each hypothesis

1. **Literature Gap Challenge:**
   - "Has this EXACT hypothesis been tested before?"
   - "What's the closest prior test and how is this different?"
   - **Novelty Kill Criterion:** Direct prior test with >500 observations

2. **Data Feasibility Challenge:**
   - "Can we measure BOTH IV and DV with available data?"
   - "What's the merge rate between required datasets?"
   - **Feasibility Kill Criterion:** <5,000 observations after merges

3. **Power/Effect Size Challenge:**
   - "What effect size is economically meaningful?"
   - "Given available N and variance, can we detect this effect?"
   - **Power Kill Criterion:** <80% power for small effect (f2=0.02)

4. **Mechanism Challenge:**
   - "What's the theoretical channel connecting IV to DV?"
   - "Could the effect be explained by obvious confounders?"
   - **Mechanism Kill Criterion:** No clear causal story

#### Phase 3: Survival Assessment
**Objective:** Rate surviving hypotheses on three dimensions

| Dimension | Weight | Scoring Criteria |
|-----------|--------|------------------|
| **Novelty** | 0.35 | No prior direct test (1.0), Related tests exist (0.7), Incremental extension (0.4) |
| **Feasibility** | 0.35 | All data available (1.0), Minor construction needed (0.8), Major gaps (0.5) |
| **Confidence** | 0.30 | >95% power for small effect (1.0), 80-95% power (0.8), <80% power (0.5) |

**Selection Criterion:** Overall Score >= 0.85 for "extremely high confidence"

### The 5E Rule for Hypothesis Quality

Each selected hypothesis MUST satisfy:
1. **Explicit:** Clearly stated IV → DV relationship with expected sign
2. **Evidence-based:** Rooted in prior literature or theory
3. **Ex-ante:** Formulated BEFORE testing (no HARKing)
4. **Explanatory:** Provides a "why" mechanism
5. **Empirically Testable:** Operationalizable with available data

---

## LLM Implementation Approaches

### Approach 1: Fine-Tuned Domain Models

| Model | Use Case | Pros | Cons |
|-------|----------|------|------|
| **FinBERT** | Sentence-level sentiment | Fast, consistent, validated | 512 token limit, no reasoning |
| **FinGPT v3.3** | Full transcript analysis | Instruction-following, financial tuning | Requires compute |
| **FinLlama** | Algorithmic trading signals | 30-year training data, Q&A focus | New, less validated |

**Best for:** High-volume processing, reproducible measures, benchmark comparisons

### Approach 2: Zero-Shot Classification with GPT-4

**Prompt Engineering Templates:**

```markdown
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

## Narrative Consistency Check
"Compare this quarter's earnings call to last quarter's.
- Identify any claims that contradict prior statements
- Flag any metrics that were highlighted last quarter but omitted now
- Detect any major strategic narrative shifts"
```

**Best for:** Rich semantic extraction, reasoning-intensive measures, exploratory analysis

### Approach 3: Embedding-Based Similarity

**Applications:**
1. **Information Novelty:** Cosine similarity between current and prior call embeddings
2. **Response Quality:** Similarity between analyst question and CEO answer embeddings
3. **Peer Comparison:** Distance from industry-peer average narrative embedding

**Implementation:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')  # or financial-specific

# Information novelty
current_embedding = model.encode(current_call_text)
prior_embedding = model.encode(prior_call_text)
novelty_score = 1 - cosine_similarity(current_embedding, prior_embedding)

# Question-answer alignment
question_embedding = model.encode(analyst_question)
answer_embedding = model.encode(ceo_response)
alignment_score = cosine_similarity(question_embedding, answer_embedding)
```

**Best for:** Scalable similarity measures, semantic clustering, dimension reduction

### Approach 4: Hybrid Dictionary + LLM

**Rationale:** Combine validated dictionary measures with LLM enhancement

**Implementation:**
1. Use LM dictionary for baseline sentiment/uncertainty
2. Use LLM to classify ambiguous cases or context-dependent words
3. Use LLM to extract information NOT in dictionary (evasiveness, forward-looking quality)

**Best for:** Building on established literature while adding novelty

### Recommended Technical Stack

| Component | Recommended Tool | Purpose |
|-----------|------------------|---------|
| Text Preprocessing | spaCy/NLTK | Tokenization, sentence segmentation |
| Dictionary Measures | LM Dictionary 2024 | Baseline uncertainty, weak modals |
| Sentence Embeddings | sentence-transformers | Similarity, clustering |
| LLM API | GPT-4o via API | Rich semantic extraction |
| Local LLM (optional) | Ollama + Llama 3 | Privacy-preserving, reproducible |
| Panel Regression | linearmodels | Fixed effects, clustering |

---

## High-Confidence Patterns from Prior Research

### Established Relationships (AVOID - already tested)

| IV | DV | Finding | Key Papers | Why Avoid |
|----|----|---------|-----------:|-----------|
| Tone (positive/negative) | Returns | Positive → positive returns | LM (2011), Huang (2014) | THOROUGHLY TESTED |
| Uncertainty words | Analyst dispersion | Uncertainty → higher dispersion | Price et al. (2012) | ESTABLISHED (H5 also null) |
| Readability | Returns | Obfuscation → negative returns | Li (2008), Loughran & McDonald (2014) | WELL DOCUMENTED |
| Sentiment | Volatility | Negative → higher volatility | Multiple | ESTABLISHED |

### Patterns with Mixed Results (POTENTIAL - needs novel angle)

| Pattern | Prior Finding | Gap/Opportunity |
|---------|---------------|-----------------|
| CEO speech → Investment | Mixed (H2 null) | Use Q&A DYNAMICS not levels |
| Uncertainty → Cash | Mixed (H1 null) | Try CHANGE in uncertainty over time |
| Speech → Turnover | Limited literature | Few direct tests of speech → CEO firing |
| Speech → M&A | Emerging literature | Target-side speech understudied |

### Untested/Novel Frontiers (HIGH PRIORITY)

Based on literature review, these areas have minimal prior testing:

1. **Q&A Response Evasiveness → Market Outcomes**
   - LLM can detect non-answers that word counts miss
   - Analyst "re-asking" behavior as proxy for hidden bad news
   - Novel: Response QUALITY not just word COUNTS

2. **Narrative Consistency Over Time → Returns**
   - Do managers contradict prior statements?
   - Semantic shift detection via embeddings
   - Novel: Temporal dimension of text measures

3. **Cross-Speaker Disagreement → Volatility**
   - CEO-CFO alignment/misalignment
   - Manager-Analyst tone gap
   - Novel: Multi-party dynamics in single call

4. **Forward-Looking Statement Quality → Forecast Accuracy**
   - Quantitative FLS vs. vague guidance
   - Specificity of guidance predicts analyst accuracy
   - Novel: FLS QUALITY not just presence

5. **Information Novelty Content → Price Discovery**
   - Embedding-based novelty vs. prior call
   - New information ratio
   - Novel: Semantic novelty, not word counts

---

## Data Feasibility Assessment Framework

### Complete Data Inventory (Updated 2026-02-06)

**IMPORTANT:** This inventory reflects ALL available data sources in `1_Inputs/`. Previous research missed several critical datasets.

#### Core Text Data

| Data Source | File(s) | Observations | Key Variables | Coverage |
|-------------|---------|--------------|---------------|----------|
| **Earnings Call Transcripts** | speaker_data_YYYY.parquet (17 files) | 112,968 calls | Full transcript, speaker roles, speaker_text | 2002-2018 |
| **Unified Call Metadata** | Unified-info.parquet | 465,434 records | company_name, cusip, isin, permno, data_quality_score | 2002-2018 |
| **LM Dictionary 2024** | Loughran-McDonald_MasterDictionary_1993-2024.csv | 86,553 words | 8 categories + NEW Complexity (53 words) | 1993-2024 |

#### SEC Regulatory Data (NEW - PREVIOUSLY MISSED)

| Data Source | File(s) | Observations | Key Variables | Coverage |
|-------------|---------|--------------|---------------|----------|
| **SEC Edgar Comment Letters** | SEC Edgar Letters/*.parquet (72 files) | ~150,000+ letters | letter_id, cik, form_type, filing_date, **full_text** (raw letter content) | **2005-2022** |
| **CCCL Instrument** | CCCL instrument/*.parquet | 145,000+ firm-years | gvkey, cik, sic, ff12, ff48, cccl_count, **6 shift_intensity variants** | 2005-2022 |

**SEC Edgar Letters - KEY INSIGHT:** These are the ACTUAL TEXT of SEC comment letters sent to firms. This enables:
- LLM extraction of SEC concerns/topics
- Firm-specific regulatory scrutiny measures (beyond industry-level CCCL)
- Question-response analysis of SEC-firm correspondence
- Linguistic analysis of SEC examiner language

#### Financial Outcome Data

| Data Source | File(s) | Observations | Key Variables | Coverage |
|-------------|---------|--------------|---------------|----------|
| **IBES Analyst Estimates** | tr_ibes/tr_ibes.parquet | 25.5M estimates | MEANEST, STDEV, NUMEST, ACTUAL, forecast error | 1999-2024 |
| **Execucomp** | Execucomp/comp_execucomp.parquet | 370,545 exec-years | salary, bonus, TDC1, option_awards, pceo, pcfo, **titleann** | 4,170 firms |
| **CEO Dismissal** | CEO Dismissal Data 2021.02.03.xlsx | 1,059 events | Forced turnover indicator | 1996-2021 |
| **SDC M&A** | SDC/sdc-ma-merged.parquet | 142,457 deals | Target/Acquiror CUSIP, Deal Value, **Deal Premium**, Deal Attitude | 1999-2025 |
| **CRSP Daily Returns** | CRSP_DSF/*.parquet (96 files) | ~1.3B daily obs | ret, prc, vol, shrout (daily) | 1999-2022 |
| **Compustat Fundamentals** | comp_na_daily_all/comp_na_daily_all.parquet | Large | All Compustat annual/quarterly variables | Full |
| **CCM Linking Table** | CRSPCompustat_CCM/CRSPCompustat_CCM.parquet | 2.4M links | gvkey ↔ permno linking | Full |

#### Risk and Sentiment Data (NEW - PREVIOUSLY MISSED)

| Data Source | File(s) | Observations | Key Variables | Coverage |
|-------------|---------|--------------|---------------|----------|
| **FirmLevelRisk** | FirmLevelRisk/firmquarter_2022q1.csv | 354,518 firm-quarters | **PRisk, NPRisk, Sentiment, PRiskT_economic/environment/trade/institutions/health/security/tax/technology**, Covid_Exposure, Brexit_Exposure | 2002-2022 |

**FirmLevelRisk - KEY INSIGHT:** This is Hassan et al. (2019) "Firm-Level Political Risk" data with:
- **PRisk/NPRisk:** Political risk from earnings call text (their original measure)
- **8 Topic-specific political risks:** Economic, environment, trade, institutions, health, security, tax, technology
- **Event exposures:** Covid, Brexit, SARS, H1N1, Zika, Ebola
- **Sentiment:** Call-level sentiment measures

This provides VALIDATED alternative text measures from the SAME earnings calls we have, enabling:
- Benchmarking our LLM measures against established PRisk
- Using their topic-specific risks as IVs or controls
- Studying interactions between political risk topics and uncertainty

### Text Measure Variables Available (1,785 total)

**Structure:** 15 speaker roles x 8 categories x 3 contexts
- **Roles:** Manager, CEO, CFO, Analyst, Operator, etc.
- **Categories:** Uncertainty, Weak Modal, Strong Modal, Positive, Negative, Litigious, Constraining, Complexity
- **Contexts:** Presentation (Pres), Q&A, Overall

### Merge Feasibility Matrix (Updated)

| Dataset A | Dataset B | Key | Expected N | Feasibility |
|-----------|-----------|-----|------------|-------------|
| Text measures | CRSP returns | GVKEY + date | ~60,000 | HIGH |
| Text measures | IBES | GVKEY + quarter | ~50,000 | HIGH |
| Text measures | Execucomp | GVKEY + year | ~20,000 | HIGH |
| Text measures | FirmLevelRisk | GVKEY + quarter | ~100,000+ | **HIGH** (same calls!) |
| Text measures | SEC Edgar Letters | CIK + year | ~30,000+ | **HIGH** |
| Text measures | SDC M&A (target) | CUSIP/GVKEY + year | ~3,000 | MEDIUM |
| Text measures | CEO dismissal | GVKEY + year | ~800 | MEDIUM |
| SEC Letters | CRSP returns | CIK → GVKEY → date | ~50,000 | HIGH |
| FirmLevelRisk | Outcomes | GVKEY + quarter | ~100,000+ | HIGH |

### NEW Hypothesis Opportunities from Additional Data

#### SEC Edgar Letters (Full Text Available!)

The SEC Edgar Letters contain the **actual regulatory correspondence** between the SEC and firms:
- 72 quarterly files covering 2005-2022
- Contains `full_text` field with complete letter content
- Can extract: SEC concerns, topics, severity, firm responses

**Novel Hypothesis Candidates from SEC Letters:**

| # | Hypothesis | IV (from SEC Letters) | DV | Novelty |
|---|------------|----------------------|----|----|
| 8 | SEC Concern Topic → Firm Behavior Change | LLM-extracted SEC concern topics | Future earnings call language change | SEC forces transparency |
| 9 | SEC Letter Severity → Stock Reaction | LLM-rated severity of SEC comments | CAR around letter receipt | Regulatory pressure signal |
| 10 | SEC Question Specificity → Disclosure Quality | LLM-measured question precision | Subsequent 10-K readability | SEC shapes disclosure |
| 11 | Repeat SEC Scrutiny → Management Turnover | Count of SEC letters to firm | CEO/CFO departure | Regulatory pressure on executives |

#### FirmLevelRisk (Validated Political Risk Measures)

The Hassan et al. (2019) data provides established text measures from the SAME earnings calls:

**Novel Hypothesis Candidates using FirmLevelRisk:**

| # | Hypothesis | IV | DV | Novelty |
|---|------------|----|----|---------|
| 12 | Political Risk Topic × Uncertainty → Investment | PRiskT_* interacted with our uncertainty | CapEx efficiency | Topic-specific risk channels |
| 13 | Political Risk Sentiment Mismatch → Returns | PRisk sentiment vs. our uncertainty gap | CAR | Inconsistent risk communication |
| 14 | Covid/Brexit Exposure → Analyst Dispersion | Covid_Exposure, Brexit_Exposure | Forecast dispersion | Event-driven uncertainty transmission |
| 15 | Topic-Specific Risk → Sector Returns | PRiskT_* (8 topics) | Industry-adjusted returns | Granular political risk pricing |

### Power Analysis Summary

For panel data with Firm + Year FE, using existing sample sizes:

| Effect Size | Required N | Available N | Power | Verdict |
|-------------|-----------|-------------|-------|---------|
| Small (f2=0.02) | ~5,000 | 20,000+ | >99% | EXCELLENT |
| Medium (f2=0.15) | ~1,000 | 20,000+ | >99% | EXCELLENT |
| Large (f2=0.35) | ~500 | 20,000+ | >99% | EXCELLENT |

**Implication:** H1-H6 null results NOT due to power. Must find REAL effects or accept no relationship exists.

---

## Recommended Planning Approach

### Phase 52 Execution Strategy

**Given the non-negotiable constraints:**
1. Ideas MUST be untested, unprecedented, and high in novelty
2. Ideas MUST be data-feasible (achievable with available data)
3. Ideas MUST have extremely high confidence of statistical significance

**Recommended 5-plan structure:**

#### Plan 52-01: LLM Capability Mapping & Literature Deep Dive
- Exhaustive search of 2023-2026 LLM + earnings call papers
- Create evidence matrix: What IVs have been tested with which DVs?
- Identify TRUE literature gaps (not just extensions)
- Map which LLM capabilities apply to available data
- **Output:** Literature gap matrix, capability inventory

#### Plan 52-02: Data Feasibility Verification
- Verify exact merge rates for all dataset combinations
- Calculate within-firm variation for text measures
- Identify sample size for each potential DV
- Check temporal overlap between datasets
- **Output:** Updated feasibility matrix with verified numbers

#### Plan 52-03: Blue Team - Candidate Hypothesis Generation
- Generate 20-30 candidate hypotheses using:
  - LLM capabilities not previously applied
  - Untested IV-DV combinations
  - Novel mechanisms suggested by Q&A dynamics literature
- Document theoretical mechanism for each
- Preliminary scoring on novelty/feasibility/power
- **Output:** Ranked candidate list

#### Plan 52-04: Red Team - Adversarial Verification
- For each candidate, execute kill criteria tests:
  - Direct prior test search
  - Data feasibility check (actual merge)
  - Power calculation with within-firm variance
  - Mechanism plausibility review
- Document specific reasons for survival/rejection
- **Output:** Verified survivors with full documentation

#### Plan 52-05: Final Selection & Hypothesis Specification
- Select top 5 hypotheses with scores >= 0.85
- Write full hypothesis specifications:
  - Exact IV definition and measurement
  - Exact DV definition and measurement
  - Controls and fixed effects
  - Expected sign and magnitude
  - Pre-specified sample filters
- **Output:** 5 hypothesis specification documents ready for implementation

### High-Priority Hypothesis Candidates (Updated with New Data)

Based on this research AND the newly discovered data sources, these candidates have highest novelty potential:

#### Tier 1: Highest Novelty (SEC Edgar Letters + LLM)

| # | Hypothesis | IV | DV | Novelty Rationale |
|---|------------|----|----|-------------------|
| 1 | **SEC Letter Topics → Earnings Call Language Change** | LLM-extracted concern topics from SEC letters | Change in next earnings call uncertainty/specificity | Novel use of SEC letter TEXT (not just receipt) |
| 2 | **SEC Question Specificity → Disclosure Quality** | LLM-measured precision of SEC questions | 10-K readability, earnings call FLS quality | SEC as disclosure quality enforcer |
| 3 | **Regulatory Correspondence Sentiment → Stock Reaction** | LLM tone analysis of SEC-firm back-and-forth | CAR around letter sequence | Full correspondence dynamics |

#### Tier 2: High Novelty (LLM + Earnings Calls)

| # | Hypothesis | IV | DV | Novelty Rationale |
|---|------------|----|----|-------------------|
| 4 | CEO Q&A Evasiveness → Negative Returns | LLM-measured response relevance | CAR around call | Evasiveness QUALITY not word counts |
| 5 | Narrative Inconsistency → Volatility | Embedding similarity across quarters | Realized volatility | Temporal dimension novel |
| 6 | FLS Specificity → Analyst Accuracy | Quantitative vs. vague guidance | Forecast error | FLS QUALITY not presence |
| 7 | CEO-CFO Tone Alignment → M&A Premium | Cross-speaker sentiment gap | Deal premium | Multi-speaker dynamics |

#### Tier 3: Medium Novelty (Political Risk Integration)

| # | Hypothesis | IV | DV | Novelty Rationale |
|---|------------|----|----|-------------------|
| 8 | Political Risk × Uncertainty Interaction → Investment | PRiskT_* × our uncertainty | CapEx efficiency | Topic-specific risk channels |
| 9 | PRisk-Uncertainty Mismatch → Returns | PRisk sentiment vs. uncertainty gap | CAR | Inconsistent risk signals |
| 10 | Topic-Specific Political Risk → Sector Rotation | PRiskT_economic/trade/tax | Industry returns | Granular political risk pricing |

#### Tier 4: Dictionary Extension

| # | Hypothesis | IV | DV | Novelty Rationale |
|---|------------|----|----|-------------------|
| 11 | LM Complexity → Investment Efficiency | New 2024 Complexity category | Biddle residual | New dictionary category |
| 12 | Information Novelty → Price Discovery | Embedding-based content novelty | Trading volume | Semantic novelty measure |
| 13 | Question Re-asking → Bad News Revelation | Analyst persistence pattern | SUE | Analyst behavior as signal |

**RECOMMENDATION:** Tier 1 hypotheses using SEC Edgar Letters represent the highest novelty because:
1. The SEC letter TEXT has never been analyzed with LLMs in academic literature
2. Direct regulatory-firm text exchange creates causal identification opportunities
3. Large sample size (150K+ letters) with rich text content
4. Can establish regulatory language → firm behavior → market outcomes chain

**Note:** Final selection requires red-team verification in Plans 52-03 and 52-04.

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

### Pitfall 5: Overfitting LLM Prompts to Sample
**Problem:** Iterating prompt until desired results emerge
**Solution:**
- Hold out validation sample during prompt development
- Lock prompts before running on full sample
- Document all prompt iterations

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

**Emerging frontiers (2025-2026):**
- Multi-agent LLM frameworks (hypothesis generator + adversarial debunker)
- Knowledge distillation (GPT-4 labels → smaller reproducible models)
- Causal LLM reasoning (counterfactual analysis)
- Real-time earnings call AI assistants

---

## Open Questions

1. **LLM Reproducibility:**
   - What we know: GPT-4 outputs can vary
   - What's unclear: Best practices for academic reproducibility
   - Recommendation: Use local models (Llama 3) or cache all API responses

2. **Effect Size Benchmarks:**
   - What we know: H1-H6 showed null effects
   - What's unclear: Are effects truly zero, or measures too noisy?
   - Recommendation: Power analysis for specific effect size thresholds

3. **Within-Firm Variation of LLM Measures:**
   - What we know: Dictionary measures have low within-firm variance
   - What's unclear: Do LLM measures vary more within firms?
   - Recommendation: Compute ICC for candidate measures before committing

4. **Computational Cost:**
   - What we know: 112,968 calls x GPT-4 API = expensive
   - What's unclear: Budget constraints
   - Recommendation: Prioritize measures that can be computed locally

---

## Sources

### Primary (HIGH confidence)
- Kelly, Xiu, Chen (2024) - "Expected Returns and Large Language Models"
- Kim, Muhn, Nikolaev (2024) - "Financial Statement Analysis with Large Language Models"
- Lopez-Lira & Tang (2023/2024) - "Can ChatGPT Forecast Stock Price Movements?"
- Loughran & McDonald (2024) - "Measuring Firm Complexity" (JFQA)
- PRISMA 2020 Statement - Systematic review methodology

### Secondary (MEDIUM confidence)
- FinGPT documentation and 2024 papers
- FinLlama (ICAIF 2024) - Financial sentiment classification
- FinDPO (ArXiv 2024/2025) - Preference optimization for financial LLMs
- Hajek & Munk (2024) - Multimodal speech emotion + text analysis
- Contemporary Accounting Research (2023) - Q&A subjectivity dimensions

### Tertiary (LOW confidence - needs verification)
- Web search results on Q&A dynamics, evasiveness detection
- Industry reports on LLM adoption in finance
- Various ArXiv preprints on financial NLP

---

## Metadata

**Confidence breakdown:**
- LLM Literature Summary: HIGH - Based on recent high-profile papers
- Novel Hypothesis Methodology: MEDIUM - Framework synthesized from multiple sources
- Implementation Approaches: HIGH - Technical stack well-established
- High-Confidence Patterns: MEDIUM - Requires verification through literature deep dive
- Data Feasibility: HIGH - Based on Phase 41 verified inventory

**Research date:** 2026-02-06
**Valid until:** 2026-05-06 (LLM field evolving rapidly; re-research before major decisions)

**Critical success factors for Phase 52:**
1. True literature gaps, not incremental extensions
2. LLM measures must have HIGH within-firm variance
3. Red-team must KILL weak hypotheses ruthlessly
4. Final 5 must survive ALL adversarial challenges
5. Pre-specification before any data analysis
6. **Prioritize SEC Edgar Letters — highest novelty potential (NEW)**
7. **Leverage FirmLevelRisk for validation and interaction effects (NEW)**

---

## Appendix: Complete File Inventory

### 1_Inputs/ Directory Structure (as of 2026-02-06)

```
1_Inputs/
├── CCCL instrument/
│   ├── instrument_shift_intensity_2005_2022.parquet (15 MB, CCCL shift-share instrument)
│   └── instrument_variable_reference.csv (variable definitions)
│
├── CEO Dismissal Data 2021.02.03.xlsx (2.5 MB, 1,059 forced turnover events)
│
├── CRSPCompustat_CCM/
│   ├── CRSPCompustat_CCM.parquet (2.4 MB, GVKEY-PERMNO linking)
│   └── CRSP_CCM_Variable_Reference.csv
│
├── CRSP_DSF/ (1.3 GB total, 96 quarterly files)
│   ├── CRSP_DSF_1999_Q1.parquet through CRSP_DSF_2022_Q4.parquet
│   └── CRSP_DSF_Variable_Reference.csv
│
├── Execucomp/
│   ├── comp_execucomp.parquet (44 MB, 370,545 executive-years)
│   └── vr.csv (variable reference)
│
├── FirmLevelRisk/ [NEW - PREVIOUSLY MISSED]
│   └── firmquarter_2022q1.csv (80 MB, 354,518 firm-quarters)
│       - PRisk, NPRisk, Sentiment (aggregate measures)
│       - PRiskT_* (8 topic-specific political risks)
│       - Covid/Brexit/SARS/H1N1/Zika/Ebola exposure
│
├── Loughran-McDonald_MasterDictionary_1993-2024.csv (9 MB, 86,553 words)
├── Loughran-McDonald_MasterDictionary_1993-2024-profile.md
│
├── SDC/
│   ├── sdc-ma-merged.parquet (26 MB, 142,457 M&A deals)
│   └── sdc-ma-merged-profile.md
│
├── SEC Edgar Letters/ [NEW - PREVIOUSLY MISSED] (15 GB total, 72 files)
│   ├── letters_2005_Q1.parquet through letters_2022_Q4.parquet
│   │   - letter_id, cik, form_type, filing_date
│   │   - full_text (ACTUAL LETTER CONTENT - key for LLM analysis)
│   │   - calendar_year
│   └── ~150,000+ total letters
│
├── Siccodes12.zip, Siccodes48.zip (FF industry classifications)
│
├── Unified-info.parquet (55 MB, 465,434 call metadata records)
├── Unified-info-profile.md
│
├── comp_na_daily_all/
│   └── comp_na_daily_all.parquet (467 MB, Compustat fundamentals)
│
├── speaker_data_2002.parquet through speaker_data_2018.parquet (5.2 GB total)
├── speaker_data_2002-profile.md, speaker_data_2014-profile.md
│
├── tr_ibes/
│   ├── tr_ibes.parquet (356 MB, 25.5M analyst estimates)
│   └── tr_ibes_dataset_profile.md
│
└── master_variable_definitions.csv, managerial_roles_extracted.txt
```

### Key Linking Variables Across Datasets

| From | To | Link Key | Notes |
|------|-----|----------|-------|
| Earnings Calls | Compustat | gvkey | Direct match |
| Earnings Calls | CRSP | gvkey → permno (via CCM) | Use LINKPRIM='P' |
| Earnings Calls | IBES | cusip (8-digit) | Standardize format |
| Earnings Calls | FirmLevelRisk | gvkey + quarter | Same source calls! |
| SEC Letters | Compustat | cik | Direct match |
| SEC Letters | CRSP | cik → gvkey → permno | Two-step link |
| Execucomp | Compustat | gvkey + year | Direct match |
| SDC M&A | Compustat | cusip (6-digit) → gvkey | Standardize CUSIP |

---

*Research conducted for Phase 52: LLM Literature Review & Novel Hypothesis Discovery*
*Project: F1D Earnings Call Analysis*
*Last Updated: 2026-02-06 (Added SEC Edgar Letters and FirmLevelRisk data sources)*
