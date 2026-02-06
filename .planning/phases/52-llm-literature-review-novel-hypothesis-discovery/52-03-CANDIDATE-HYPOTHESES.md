# Phase 52-03: Blue Team Candidate Hypothesis Generation

**Generated:** 2026-02-06
**Purpose:** Blue Team creative hypothesis generation grounded in verified literature gaps (52-01) and data feasibility (52-02)
**Status:** Complete
**Mode:** BLUE TEAM (Creative Brainstorming)

---

## Executive Summary

This document contains 27 candidate hypotheses generated through abductive reasoning from verified literature gaps. Each hypothesis has explicit IV-DV relationship, predicted sign, theoretical mechanism, and feasibility verification. Candidates are ranked by preliminary scoring for Red Team (52-04) adversarial review.

**Generation Process:**
- For each gap from 52-01: "What hypothesis, if true, would fill this gap?"
- For each mechanism: "What explains this relationship?"
- For each measure: "What data from 52-02 enables testing?"

**Tier Distribution:**
- Tier 1 (Data Integration): 8 candidates
- Tier 2 (LLM + Earnings Calls): 9 candidates
- Tier 3 (Political Risk Integration): 6 candidates
- Tier 4 (Dictionary Extensions): 4 candidates

---

## Candidate Hypotheses

### TIER 1: DATA INTEGRATION (HIGHEST NOVELTY)

These hypotheses leverage UNIQUE data linkages across SEC letters + earnings calls + FirmLevelRisk not found in prior literature.

---

### Candidate H1: SEC Letter Topics Predict Earnings Call Language Adaptation

**Hypothesis Statement:**
SEC Letter Topic Severity → Increased Specificity in Next Earnings Call (expected sign: +)

**Theoretical Mechanism:**
When the SEC raises specific concerns in comment letters (e.g., revenue recognition, risk factor clarity), management strategically adapts their subsequent earnings call disclosure to preemptively address these concerns. Higher severity SEC concerns trigger more specific, quantitative language in the next earnings call to demonstrate regulatory responsiveness and reduce future scrutiny risk.

**Operationalization:**
- IV: LLM-extracted SEC concern severity score (1-5 scale) for each topic category
  - Source: SEC Edgar Letters (190K letters)
  - Extraction: GPT-4 zero-shot classification of concern intensity
- DV: Change in earnings call specificity (Δ Quantitative FLS count / Total FLS)
  - Source: Earnings Call Transcripts (112K calls)
  - Extraction: LLM classification of forward-looking statements as quantitative vs. vague
- Controls: Firm size, prior specificity level, SEC letter volume, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 50K-70K letter-call pairs
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #1 (0.99 score) - "SEC Letter Topics → Earnings Call Language Shift"
- Why not tested before: Prior SEC letter studies examine letter counts or market reactions; no test of letter CONTENT → call TEXT response chain
- Anti-novelty check: ✓ Not on watchlist; specific combination is novel

**Tier:** 1

---

### Candidate H2: SEC Correspondence Resolution Quality Predicts Stock Returns

**Hypothesis Statement:**
Correspondence Thread Resolution Quality → Positive CAR around Resolution (expected sign: +)

**Theoretical Mechanism:**
When firms effectively resolve SEC concerns across multi-letter correspondence threads (demonstrated by declining concern intensity, shorter responses, and resolution language), this signals successful uncertainty resolution to the market. Higher-quality resolution (measured by LLM analysis of the full thread trajectory) reduces information uncertainty, generating positive abnormal returns around correspondence completion.

**Operationalization:**
- IV: LLM-measured resolution quality score (composite)
  - Source: SEC correspondence threads (linked letter sequences)
  - Components: (1) Concern intensity decline across letters, (2) Response thoroughness, (3) Resolution language presence
- DV: CAR [-3, +3] around correspondence completion date
  - Source: CRSP daily returns via CCM linkage
- Controls: Letter count in thread, initial concern severity, firm size, industry volatility
- FE: Industry + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 30K-50K correspondence threads
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #4 (0.94 score) - "Correspondence Thread Resolution Quality → CAR"
- Why not tested before: Thread-level analysis of correspondence quality never attempted; prior work uses letter counts not resolution dynamics
- Anti-novelty check: ✓ Not on watchlist; thread-level analysis is novel capability

**Tier:** 1

---

### Candidate H3: Political Risk × Uncertainty Interaction Predicts Investment Efficiency

**Hypothesis Statement:**
PRisk × LM_Uncertainty → Decreased Investment Efficiency (expected sign: -)

**Theoretical Mechanism:**
Political risk creates external uncertainty about future policy, while linguistic uncertainty reflects internal information asymmetry. When both are elevated simultaneously, managers face compounded uncertainty from both external (policy) and internal (information quality) sources, leading to suboptimal investment allocation. The interaction effect captures the amplification mechanism where political uncertainty magnifies the real effects of managerial uncertainty signaling.

**Operationalization:**
- IV: Interaction term: Hassan PRisk × Manager_Uncertainty_pct
  - Source: FirmLevelRisk (PRisk) + Speech measures (LM Uncertainty)
  - Both standardized before interaction to reduce multicollinearity
- DV: Investment efficiency (Biddle et al. 2009 residual)
  - Source: Compustat (CapEx, Sales Growth, Tobin's Q)
- Controls: PRisk (main effect), Uncertainty (main effect), Size, Leverage, Cash flow
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 30K+ firm-quarter observations
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #3 (0.95 score) - "PRisk × Uncertainty Interaction → Investment"
- Why not tested before: Integration of Hassan PRisk with dictionary uncertainty measures never tested; prior work examines each in isolation
- Anti-novelty check: ✓ Novel interaction; both measures established but combination untested

**Tier:** 1

---

### Candidate H4: SEC Letter Receipt Predicts PRisk Increase

**Hypothesis Statement:**
SEC Comment Letter Receipt → Increased Political Risk Discussion (expected sign: +)

**Theoretical Mechanism:**
SEC scrutiny signals regulatory attention that may generalize to broader regulatory/political concerns. After receiving SEC comment letters, managers become more attuned to regulatory risk broadly, leading to increased discussion of political and regulatory risks in subsequent earnings calls. This represents a spillover effect from SEC scrutiny to political risk awareness.

**Operationalization:**
- IV: SEC letter receipt indicator (0/1) in prior quarter
  - Source: SEC Edgar Letters (190K letters)
- DV: Change in Hassan PRisk (ΔPRisk from t-1 to t)
  - Source: FirmLevelRisk dataset
- Controls: Prior PRisk level, firm size, industry regulatory intensity, market volatility
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 70K-90K merged observations
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: TRUE GAP - Data integration combining SEC letters with PRisk measures
- Why not tested before: SEC letters and FirmLevelRisk data have not been linked in prior research
- Anti-novelty check: ✓ Novel data integration

**Tier:** 1

---

### Candidate H5: SEC + Earnings Call + PRisk Triple Integration

**Hypothesis Statement:**
SEC Letter Severity × High PRisk Exposure → Largest Call Language Adaptation (expected sign: +)

**Theoretical Mechanism:**
Firms facing both SEC scrutiny AND high political risk exposure experience compounded regulatory pressure from multiple sources. This triple interaction predicts that SEC letter effects on earnings call language are amplified when firms already face elevated political uncertainty. The combined regulatory attention creates multiplicative pressure for disclosure improvement.

**Operationalization:**
- IV: Triple interaction: SEC_Severity × High_PRisk_Indicator × Post_Letter
  - SEC Severity from LLM extraction (1-5)
  - High PRisk = top quartile of Hassan PRisk
  - Post_Letter = 1 if earnings call follows letter within 90 days
- DV: Earnings call specificity change (Δ quantitative language)
  - Source: LLM classification of call text
- Controls: All main effects and two-way interactions, firm size, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: ~20K triple-matched observations (SEC letter + PRisk + calls)
- Power: HIGH (>95% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: TRUE GAP - No prior test integrates all three data sources
- Why not tested before: Data integration across SEC letters, earnings calls, and FirmLevelRisk is unique to this project
- Anti-novelty check: ✓ Highest novelty - unprecedented data combination

**Tier:** 1

---

### Candidate H6: SEC Letter Topics Predict Call Q&A Focus

**Hypothesis Statement:**
SEC Letter Topic Focus → Matching Q&A Topic Focus (expected sign: +)

**Theoretical Mechanism:**
When SEC comment letters focus on specific topics (revenue recognition, related parties, risk factors), analysts incorporate this information into their subsequent earnings call questions. This creates predictable topic alignment between SEC concerns and Q&A content, as analysts use SEC letters as signals for areas requiring management clarification.

**Operationalization:**
- IV: Topic distribution vector from SEC letter (LLM-extracted)
  - Source: SEC Edgar Letters
  - Extraction: Topic classification (e.g., revenue, expense, risk, governance)
- DV: Topic distribution vector from Q&A segment (LLM-extracted)
  - Source: Earnings call Q&A transcripts
  - Same topic taxonomy as IV
- Controls: Prior Q&A topic distribution, analyst coverage, firm complexity
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 50K-70K letter-call pairs
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Extension of Gap #1 - Analyst-mediated channel from SEC to calls
- Why not tested before: Topic-level alignment between letters and Q&A never measured
- Anti-novelty check: ✓ Novel specific combination

**Tier:** 1

---

### Candidate H7: Regulatory Scrutiny Chain - Letters to Calls to Returns

**Hypothesis Statement:**
SEC Letter Receipt → Call Language Improvement → Positive CAR (expected sign: + mediated)

**Theoretical Mechanism:**
SEC comment letters trigger managerial disclosure improvement in subsequent earnings calls. This improved disclosure quality (more specific, less uncertain language) reduces information asymmetry, which the market values positively. The hypothesis tests a mediation chain: regulatory pressure → improved disclosure → market reward.

**Operationalization:**
- IV: SEC letter receipt (0/1) in prior 90 days
- Mediator: Call disclosure quality improvement (composite LLM score)
- DV: CAR [-1, +3] around earnings call
  - Source: CRSP daily returns
- Controls: Prior CAR, earnings surprise, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level
- Method: Mediation analysis (Baron-Kenny or structural)

**Sample Estimate:**
- From 52-02: 50K-70K letter-call pairs
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Novel mediation chain
- Why not tested before: Mediation pathway from SEC letters through call quality to returns untested
- Anti-novelty check: ✓ Specific causal chain is novel

**Tier:** 1

---

### Candidate H8: Cross-Document Semantic Alignment

**Hypothesis Statement:**
SEC Response Quality → Earnings Call Consistency (expected sign: +)

**Theoretical Mechanism:**
Firms that provide high-quality, thorough responses to SEC comment letters demonstrate consistent narrative management. This consistency should transfer to earnings calls, where similar topics are discussed with aligned messaging. High SEC response quality predicts high earnings call consistency, as firms with strong disclosure practices apply them across documents.

**Operationalization:**
- IV: SEC response quality score (LLM-measured comprehensiveness, directness)
  - Source: SEC correspondence responses
- DV: Earnings call narrative consistency (embedding similarity to prior calls)
  - Source: Earnings call transcripts
- Controls: Firm size, SEC letter topic, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 30K-50K matched observations
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Cross-document quality consistency never tested
- Why not tested before: Requires linking SEC responses to earnings calls across documents
- Anti-novelty check: ✓ Novel cross-document analysis

**Tier:** 1

---

### TIER 2: LLM + EARNINGS CALLS (HIGH NOVELTY)

These hypotheses leverage LLM capabilities for semantic analysis of earnings calls to measure constructs that dictionaries cannot capture.

---

### Candidate H9: Q&A Response Relevance Predicts Returns

**Hypothesis Statement:**
CEO Response Relevance to Analyst Questions → Positive CAR (expected sign: +)

**Theoretical Mechanism:**
When CEOs directly and relevantly answer analyst questions (rather than evading or pivoting to different topics), they provide higher-quality information that reduces analyst uncertainty. High response relevance signals management transparency and competence, which markets value positively. Low relevance (evasiveness) signals information hiding.

**Operationalization:**
- IV: Response relevance score (LLM-measured alignment between question and answer)
  - Source: Q&A segment of earnings calls
  - Method: Embedding similarity OR GPT-4 relevance rating
- DV: CAR [-1, +3] around earnings call
  - Source: CRSP daily returns
- Controls: Earnings surprise, prior CAR, analyst coverage, call length
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 100K+ Q&A pairs (aggregated to call level)
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #5 (0.91 score) - "Q&A Response Relevance (LLM) → Returns"
- Why not tested before: Prior evasiveness studies use word counts; LLM semantic relevance is novel
- Anti-novelty check: ⚠️ Some evasiveness studies exist but LLM-based relevance is novel

**Tier:** 2

---

### Candidate H10: Narrative Inconsistency Predicts Volatility

**Hypothesis Statement:**
Quarter-over-Quarter Narrative Drift → Increased Realized Volatility (expected sign: +)

**Theoretical Mechanism:**
When a firm's earnings call narrative changes substantially from the prior quarter (measured by embedding dissimilarity), this signals strategic change, uncertainty about direction, or information concealment. High narrative drift creates investor uncertainty about the firm's trajectory, leading to higher post-call realized volatility as investors reassess positions.

**Operationalization:**
- IV: Narrative drift score = 1 - Cosine_Similarity(current_call, prior_call)
  - Source: Earnings call embeddings (sentence-transformers)
  - Method: Full transcript or management discussion embeddings
- DV: Realized volatility in [+1, +20] trading days post-call
  - Source: CRSP daily returns
- Controls: Prior volatility, market volatility, earnings surprise, call length
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 50K+ call pairs (current vs. prior quarter)
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #4 (0.96 score) - "Narrative Inconsistency → Volatility"
- Why not tested before: Temporal embedding consistency is emerging method; not applied to earnings call volatility prediction
- Anti-novelty check: ✓ Novel temporal dimension; embedding similarity is novel application

**Tier:** 2

---

### Candidate H11: FLS Specificity Predicts Analyst Accuracy

**Hypothesis Statement:**
Forward-Looking Statement Quantitative Specificity → Lower Analyst Forecast Error (expected sign: -)

**Theoretical Mechanism:**
When managers provide specific, quantitative forward-looking statements ("We expect revenue of $X-$Y million") versus vague statements ("We expect growth"), analysts have concrete anchors for forecasting. Higher quantitative specificity in FLS reduces analyst uncertainty and improves forecast precision. This is a direct information provision → forecast quality mechanism.

**Operationalization:**
- IV: FLS specificity ratio = Count(Quantitative FLS) / Count(All FLS)
  - Source: LLM classification of earnings call FLS
  - Quantitative: Contains numbers, ranges, or specific metrics
  - Qualitative: Vague directional statements only
- DV: Absolute analyst forecast error = |ACTUAL - MEANEST| / |ACTUAL|
  - Source: IBES
- Controls: Prior forecast error, analyst coverage, earnings volatility, firm size
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 50K+ earnings calls with FLS + IBES match
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #6 (0.91 score) - "FLS Specificity (LLM) → Analyst Accuracy"
- Why not tested before: Prior FLS studies measure presence, not quality distinction between quantitative vs. vague
- Anti-novelty check: ⚠️ FLS studies exist but LLM quality classification is novel

**Tier:** 2

---

### Candidate H12: CEO-CFO Alignment Predicts M&A Target Premium

**Hypothesis Statement:**
Low CEO-CFO Tone Alignment → Lower M&A Premium When Target (expected sign: +)

**Theoretical Mechanism:**
When CEO and CFO exhibit misaligned tone in earnings calls (disagreement in sentiment about company prospects), this signals internal discord that acquirers can detect and exploit. Acquirers pay lower premiums for targets with visible CEO-CFO misalignment, as the discord suggests management problems or disagreement about firm value. Alignment = higher bargaining power; discord = lower premium.

**Operationalization:**
- IV: CEO-CFO tone gap = |CEO_Sentiment - CFO_Sentiment|
  - Source: Speaker-level sentiment from earnings calls
  - Method: FinBERT sentence-level sentiment aggregated by speaker
- DV: M&A deal premium = (Offer Price - Prior Stock Price) / Prior Stock Price
  - Source: SDC M&A, CRSP for prior price
- Controls: Target size, target profitability, deal size, competing bidders
- FE: Industry + Year fixed effects
- SE: Clustered at target firm level

**Sample Estimate:**
- From 52-02: 5K-10K target firms with pre-acquisition calls
- Power: MEDIUM (~95% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #7 (0.87 score) - "CEO-CFO Alignment → M&A Premium"
- Why not tested before: CEO-CFO alignment studied for returns but NOT in M&A context
- Anti-novelty check: ⚠️ CEO-CFO studies exist but M&A premium DV is novel

**Tier:** 2

---

### Candidate H13: Information Novelty Predicts Trading Volume

**Hypothesis Statement:**
Earnings Call Information Novelty → Increased Trading Volume (expected sign: +)

**Theoretical Mechanism:**
When earnings calls contain substantively new information (measured by low similarity to prior calls AND to boilerplate language), investors have more to trade on. High information novelty creates heterogeneous interpretation and position adjustments, generating abnormal trading volume. Low novelty (repetitive, boilerplate calls) provides minimal new trading signals.

**Operationalization:**
- IV: Information novelty score = 1 - max(Sim_to_prior, Sim_to_boilerplate)
  - Source: Embeddings of current call vs. prior call and vs. industry boilerplate
- DV: Abnormal trading volume in [0, +5] days post-call
  - Source: CRSP volume, normalized by prior period average
- Controls: Earnings surprise, prior volume, market volume, call length
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 100K+ earnings calls
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Related to Tier 4 candidate #12 in RESEARCH.md
- Why not tested before: Embedding-based content novelty vs. word count novelty is methodological advancement
- Anti-novelty check: ✓ Novel method for measuring novelty

**Tier:** 2

---

### Candidate H14: Question Difficulty Predicts Evasiveness

**Hypothesis Statement:**
Analyst Question Difficulty → Increased CEO Response Evasiveness (expected sign: +)

**Theoretical Mechanism:**
When analysts ask difficult questions (probing, multi-part, requiring specific metrics), CEOs are more likely to evade than when asked easy questions. This establishes a baseline relationship between question characteristics and response quality, enabling identification of "excess evasiveness" beyond what question difficulty predicts. Excess evasiveness signals information hiding.

**Operationalization:**
- IV: Question difficulty score (LLM-rated complexity, specificity, probe intensity)
  - Source: Analyst questions from Q&A segment
- DV: Response evasiveness score (LLM-rated relevance, directness)
  - Source: CEO responses from Q&A segment
- Controls: Firm size, earnings surprise, analyst experience, prior relationship
- FE: Firm + Year fixed effects
- SE: Clustered at firm level
- Extension: Use residual as "excess evasiveness" IV for returns prediction

**Sample Estimate:**
- From 52-02: 100K+ Q&A pairs
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Novel decomposition of evasiveness into expected vs. excess
- Why not tested before: Prior evasiveness studies don't control for question difficulty
- Anti-novelty check: ✓ Novel decomposition approach

**Tier:** 2

---

### Candidate H15: Prepared vs. Spontaneous Uncertainty Gap

**Hypothesis Statement:**
Higher Spontaneous Uncertainty (Q&A) vs. Prepared Uncertainty (Presentation) → Negative Returns (expected sign: -)

**Theoretical Mechanism:**
The gap between uncertainty language in prepared remarks versus spontaneous Q&A reveals management's true uncertainty level. Higher spontaneous uncertainty relative to prepared uncertainty signals that managers are hiding bad news in scripted sections but revealing it under questioning. Markets interpret this gap as a negative signal about management credibility.

**Operationalization:**
- IV: Uncertainty gap = QA_Uncertainty_pct - Pres_Uncertainty_pct
  - Source: Speaker-level text measures (already computed)
  - Pres = Presentation section; QA = Q&A section
- DV: CAR [-1, +3] around earnings call
  - Source: CRSP daily returns
- Controls: Overall uncertainty level, earnings surprise, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 100K+ earnings calls
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Related to H5-B from prior phases but with LLM measures
- Why not tested before: Gap measure tested with dictionary (H5-B) showed mixed results; LLM-based may improve
- Anti-novelty check: ⚠️ Similar to prior H5-B but with refined measurement

**Tier:** 2

---

### Candidate H16: Management Confidence Trajectory

**Hypothesis Statement:**
Declining Confidence Trajectory Across Quarters → Negative Returns (expected sign: -)

**Theoretical Mechanism:**
When management's expressed confidence declines across consecutive quarters (measured by LLM confidence ratings), this signals deteriorating outlook. The trajectory of confidence, not just level, contains predictive information. Declining confidence trajectory predicts future underperformance as firms approach problems management saw coming.

**Operationalization:**
- IV: Confidence trajectory = Confidence_t - Confidence_{t-1}
  - Source: LLM-rated confidence from management remarks (1-5 scale)
- DV: CAR over subsequent quarter
  - Source: CRSP returns
- Controls: Current confidence level, earnings surprise, prior returns
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 50K+ consecutive call pairs
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Novel trajectory-based predictor
- Why not tested before: Level studies dominate; trajectory is novel angle
- Anti-novelty check: ✓ Novel dynamic measure

**Tier:** 2

---

### Candidate H17: Cross-Speaker Information Consistency

**Hypothesis Statement:**
CEO-CFO Information Consistency → Lower Analyst Dispersion (expected sign: -)

**Theoretical Mechanism:**
When CEO and CFO provide consistent information (same facts, aligned numbers, no contradictions), analysts face less uncertainty about firm fundamentals. High information consistency across speakers reduces analyst disagreement, lowering forecast dispersion. Inconsistency (different numbers, contradictory statements) increases uncertainty and dispersion.

**Operationalization:**
- IV: Information consistency score = Cosine_Sim(CEO_facts, CFO_facts)
  - Source: LLM-extracted factual claims by speaker
  - Method: Compare numerical claims and directional statements
- DV: Analyst forecast dispersion = STDEV / |MEANEST|
  - Source: IBES
- Controls: Prior dispersion, earnings surprise, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 50K+ calls with CEO + CFO participation + IBES
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Related to CEO-CFO alignment but focused on factual consistency
- Why not tested before: Prior work focuses on sentiment alignment, not factual consistency
- Anti-novelty check: ✓ Novel focus on information (not tone) consistency

**Tier:** 2

---

### TIER 3: POLITICAL RISK INTEGRATION (MEDIUM NOVELTY)

These hypotheses leverage FirmLevelRisk (Hassan PRisk) data with earnings call measures.

---

### Candidate H18: Topic-Specific PRisk Predicts Sector Returns

**Hypothesis Statement:**
Industry-Level PRiskT_trade → Negative Industry Returns (expected sign: -)

**Theoretical Mechanism:**
Topic-specific political risk (trade policy, tax policy, regulatory policy) has differential effects across industries. When trade-related political risk (PRiskT_trade) is elevated, trade-sensitive industries underperform. The granular topic decomposition allows testing whether specific political risk topics predict industry-specific returns beyond aggregate PRisk.

**Operationalization:**
- IV: Industry average PRiskT_* (8 topic-specific risks)
  - Source: FirmLevelRisk aggregated by FF48 industry
- DV: Industry portfolio returns (industry-adjusted)
  - Source: CRSP daily returns aggregated to industry
- Controls: Market returns, aggregate PRisk, industry volatility
- FE: Industry + Year fixed effects
- SE: Clustered at industry level

**Sample Estimate:**
- From 52-02: 48 industries × 17 years × 4 quarters = ~3,200 industry-quarters
- Power: MEDIUM (~85% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #10 (0.84 score) - "Topic-Specific PRisk → Sector Rotation"
- Why not tested before: Aggregate PRisk tested; topic-level industry effects not tested
- Anti-novelty check: ✓ Granular topic analysis is novel

**Tier:** 3

---

### Candidate H19: Event Exposure Predicts Analyst Behavior

**Hypothesis Statement:**
Covid_Exposure → Increased Analyst Forecast Dispersion (expected sign: +)

**Theoretical Mechanism:**
Firms with high Covid exposure (as measured in earnings calls) faced unprecedented uncertainty, leading to wider analyst disagreement about future earnings. The event-specific exposure measure captures heterogeneous impact within industries, explaining variation in analyst uncertainty beyond industry effects.

**Operationalization:**
- IV: Covid_Exposure from FirmLevelRisk
  - Source: FirmLevelRisk dataset
- DV: Analyst forecast dispersion = STDEV / |MEANEST|
  - Source: IBES
- Controls: Prior dispersion, industry, firm size, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level
- Sample restriction: 2020-2021 period for Covid relevance

**Sample Estimate:**
- From 52-02: ~20K firm-quarters in 2020-2021 with Covid exposure data
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Event-driven uncertainty transmission
- Why not tested before: FirmLevelRisk Covid exposure + analyst dispersion not directly tested
- Anti-novelty check: ✓ Specific event × dispersion combination novel

**Tier:** 3

---

### Candidate H20: PRisk × Leverage → Speech Discipline

**Hypothesis Statement:**
High PRisk × High Leverage → Reduced Next Quarter Uncertainty (expected sign: -)

**Theoretical Mechanism:**
Firms facing both political risk AND high leverage are under increased creditor monitoring. This dual pressure disciplines management speech, leading to reduced uncertainty language in subsequent quarters. Leverage acts as a monitoring mechanism that constrains managerial discretion in disclosure, especially when political uncertainty is elevated.

**Operationalization:**
- IV: Interaction: High_PRisk × High_Leverage
  - High PRisk = top quartile of Hassan PRisk
  - High Leverage = top quartile of book leverage
- DV: Change in uncertainty language (ΔUncertainty_pct from t to t+1)
  - Source: LM dictionary uncertainty measures
- Controls: PRisk (main effect), Leverage (main effect), firm size, profitability
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 30K+ firm-quarters with PRisk + leverage data
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #9 (0.86 score) - "Uncertainty × Leverage → Speech Discipline"
- Why not tested before: Leverage as monitoring mechanism for speech discipline untested
- Anti-novelty check: ⚠️ H1b tested leverage attenuation but not discipline mechanism

**Tier:** 3

---

### Candidate H21: Political Sentiment → Investment Timing

**Hypothesis Statement:**
Positive Political Sentiment → Accelerated Investment (expected sign: +)

**Theoretical Mechanism:**
When firms express positive sentiment about political conditions (PSentiment from FirmLevelRisk), they perceive favorable policy environment for investment. This optimism translates to accelerated investment spending. The political sentiment component captures forward-looking policy expectations that influence investment timing decisions.

**Operationalization:**
- IV: PSentiment (political sentiment) from FirmLevelRisk
  - Source: FirmLevelRisk dataset
- DV: Investment intensity = CapEx / Lagged_Assets
  - Source: Compustat
- Controls: Tobin's Q, Cash flow, Prior investment, firm size
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 30K+ firm-quarters
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Sentiment component of political risk less studied than risk component
- Why not tested before: Hassan PRisk tested but PSentiment → investment not directly tested
- Anti-novelty check: ⚠️ Hassan 2019 may cover related ground; verify in Red Team

**Tier:** 3

---

### Candidate H22: PRisk Volatility → Return Volatility

**Hypothesis Statement:**
Quarter-over-Quarter PRisk Volatility → Increased Stock Return Volatility (expected sign: +)

**Theoretical Mechanism:**
Firms with high volatility in political risk mentions (oscillating PRisk across quarters) face unpredictable political exposure. This unpredictability creates investor uncertainty about future policy impacts, leading to higher stock return volatility. It's not the level of PRisk but its instability that drives volatility.

**Operationalization:**
- IV: PRisk volatility = StdDev(PRisk) over trailing 4 quarters
  - Source: FirmLevelRisk
- DV: Realized stock return volatility
  - Source: CRSP daily returns
- Controls: PRisk level, firm size, industry volatility, market volatility
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 30K+ firm-quarters with 4-quarter history
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Volatility-of-volatility approach novel
- Why not tested before: PRisk level tested; PRisk volatility not tested
- Anti-novelty check: ✓ Novel dynamic approach to PRisk

**Tier:** 3

---

### Candidate H23: Cross-Topic PRisk Concentration

**Hypothesis Statement:**
Concentrated PRisk (Few Topics) → Higher Abnormal Returns (expected sign: +)

**Theoretical Mechanism:**
Firms with concentrated political risk exposure (e.g., 80% of PRisk from tax policy only) face more predictable and hedgeable risk than firms with diffuse exposure across all 8 topics. Concentrated exposure allows specialized monitoring and hedging, reducing uncertainty discount. Diffuse exposure = unpredictable = higher discount.

**Operationalization:**
- IV: PRisk concentration = Herfindahl index across 8 PRiskT topics
  - Source: FirmLevelRisk topic-specific risks
  - HHI = Σ(PRiskT_i / Total_PRisk)²
- DV: Industry-adjusted stock returns
  - Source: CRSP
- Controls: Total PRisk level, firm size, industry
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 30K+ firm-quarters with topic-specific PRisk
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Novel concentration approach
- Why not tested before: Topic-level data rarely analyzed for concentration
- Anti-novelty check: ✓ Novel application of Herfindahl to PRisk topics

**Tier:** 3

---

### TIER 4: DICTIONARY EXTENSIONS (LOWER NOVELTY)

These hypotheses extend established dictionary-based measures with novel applications.

---

### Candidate H24: LM Complexity (2024) → Investment Efficiency

**Hypothesis Statement:**
Earnings Call Complexity → Lower Investment Efficiency (expected sign: -)

**Theoretical Mechanism:**
When managers use complex language (as measured by new LM 2024 Complexity category), they obscure information that investors and analysts need for efficient capital allocation. High complexity creates friction in information transmission, leading to suboptimal investment decisions. Complexity may signal either intentional obfuscation or genuine underlying complexity.

**Operationalization:**
- IV: Complexity word count ratio (LM 2024 category, 53 words)
  - Source: Earnings call transcripts × LM Dictionary 2024
- DV: Investment efficiency (Biddle et al. 2009 residual)
  - Source: Compustat
- Controls: Uncertainty, Tone, firm size, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 100K+ earnings calls
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Rank #8 (0.88 score) - "LM Complexity (2024) → Investment Efficiency"
- Why not tested before: LM 2024 Complexity category just released; not yet tested with investment efficiency
- Anti-novelty check: ⚠️ Dictionary measure may face H1-H6 variation issues; test carefully

**Tier:** 4

---

### Candidate H25: Weak Modal Specificity → M&A Premium

**Hypothesis Statement:**
Low Weak Modal Usage → Higher M&A Premium When Target (expected sign: -)

**Theoretical Mechanism:**
Targets that use less hedging language (fewer "may," "might," "could" weak modals) project confidence about their prospects. Acquirers interpret low hedging as management conviction, supporting higher valuations. High hedging signals uncertainty about future, weakening target's bargaining position.

**Operationalization:**
- IV: Weak Modal word ratio (LM category)
  - Source: Earnings call transcripts × LM Dictionary
- DV: M&A deal premium
  - Source: SDC M&A
- Controls: Target size, profitability, deal characteristics
- FE: Industry + Year fixed effects
- SE: Clustered at target level

**Sample Estimate:**
- From 52-02: 5K-10K targets with pre-acquisition calls
- Power: MEDIUM (~95% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Weak modal in M&A context
- Why not tested before: Weak modal tested for dispersion (H5) but not M&A premium
- Anti-novelty check: ⚠️ May face H5 variation issues in M&A context

**Tier:** 4

---

### Candidate H26: Sentiment Consistency → Analyst Revision

**Hypothesis Statement:**
Cross-Quarter Sentiment Consistency → Smaller Analyst Revisions (expected sign: -)

**Theoretical Mechanism:**
When firm sentiment is consistent across quarters (predictable tone), analysts make smaller forecast revisions because expectations are already priced in. Sentiment volatility (oscillating positive/negative) triggers larger revisions as analysts repeatedly update expectations. Consistency = stability = smaller revisions.

**Operationalization:**
- IV: Sentiment consistency = StdDev(Tone) over trailing 4 quarters
  - Source: LM dictionary sentiment
- DV: Analyst forecast revision magnitude = |Revision| / |Prior Forecast|
  - Source: IBES
- Controls: Prior revision, earnings surprise, analyst coverage
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: 50K+ firm-quarters with 4-quarter history + IBES
- Power: HIGH (>99% for f2=0.02)

**Novelty Claim:**
- Gap from 52-01: Consistency/volatility of tone measures less studied
- Why not tested before: Tone level tested extensively; tone volatility less explored
- Anti-novelty check: ⚠️ May be incremental to existing sentiment studies

**Tier:** 4

---

### Candidate H27: Positive-to-Negative Ratio → Credit Spread

**Hypothesis Statement:**
Lower Positive/Negative Word Ratio → Higher Credit Spread (expected sign: -)

**Theoretical Mechanism:**
The ratio of positive to negative language in earnings calls signals management's assessment of financial health. When ratio is low (more negative language), credit markets interpret this as increased default risk, demanding higher spreads. The ratio provides a simple but effective signal for credit assessment.

**Operationalization:**
- IV: Positive/Negative ratio = LM_Positive_count / LM_Negative_count
  - Source: Earnings calls × LM Dictionary
- DV: Credit default swap spread OR bond yield spread
  - Source: Markit CDS or TRACE (if available)
- Controls: Leverage, profitability, rating, firm size
- FE: Firm + Year fixed effects
- SE: Clustered at firm level

**Sample Estimate:**
- From 52-02: Depends on CDS/TRACE availability (verify in Red Team)
- Power: UNCERTAIN (data availability issue)

**Novelty Claim:**
- Gap from 52-01: Credit market outcomes less studied than equity
- Why not tested before: Credit spread data access may have limited prior research
- Anti-novelty check: ⚠️ Tone-credit relationship may exist in literature; verify

**Tier:** 4

---

## Summary Statistics

### Tier Distribution

| Tier | Count | Description |
|------|-------|-------------|
| 1 | 8 | Data Integration (HIGHEST NOVELTY) |
| 2 | 9 | LLM + Earnings Calls (HIGH NOVELTY) |
| 3 | 6 | Political Risk Integration (MEDIUM NOVELTY) |
| 4 | 4 | Dictionary Extensions (LOWER NOVELTY) |
| **Total** | **27** | |

### Gap Coverage from 52-01

| Gap Rank | Gap Description | Candidates Addressing |
|----------|-----------------|----------------------|
| #1 (0.99) | SEC Letter Topics → Call Language | H1, H5, H6, H7 |
| #2 (0.94) | Correspondence Resolution → CAR | H2 |
| #3 (0.95) | PRisk × Uncertainty → Investment | H3 |
| #4 (0.96) | Narrative Inconsistency → Volatility | H10 |
| #5 (0.91) | Q&A Relevance → Returns | H9 |
| #6 (0.91) | FLS Specificity → Analyst Accuracy | H11 |
| #7 (0.87) | CEO-CFO Alignment → M&A Premium | H12 |
| #8 (0.88) | LM Complexity → Investment | H24 |
| #9 (0.86) | Uncertainty × Leverage → Speech | H20 |
| #10 (0.84) | Topic PRisk → Sector Returns | H18 |

### Anti-Novelty Flags

| Flag | Candidates | Concern | Mitigation |
|------|------------|---------|------------|
| ⚠️ | H9, H11, H12, H15, H20, H21, H24, H25, H26, H27 | Related prior work exists | Verify specific combination is novel in Red Team |
| ✓ | All others | No novelty concerns | Proceed with scoring |

---

## 5E Rule Compliance Matrix (Task 2)

Each hypothesis is verified against the 5E Rule for hypothesis quality:
1. **Explicit:** Clearly stated IV → DV relationship with expected sign
2. **Evidence-based:** Rooted in prior literature or theory
3. **Ex-ante:** Formulated BEFORE testing (pre-registration quality)
4. **Explanatory:** Provides a "why" mechanism
5. **Empirically Testable:** Operationalizable with available data

### Tier 1 Candidates (Data Integration)

| Candidate | Explicit | Evidence-based | Ex-ante | Explanatory | Testable | 5E Pass |
|-----------|----------|----------------|---------|-------------|----------|---------|
| H1: SEC Topics → Call Specificity | ✓ Sign: + | ✓ Disclosure adaptation theory | ✓ Pre-specified | ✓ Regulatory pressure mechanism | ✓ 50K-70K obs | **PASS** |
| H2: Resolution Quality → CAR | ✓ Sign: + | ✓ Information uncertainty resolution | ✓ Pre-specified | ✓ Thread trajectory mechanism | ✓ 30K-50K obs | **PASS** |
| H3: PRisk × Uncertainty → Investment | ✓ Sign: - | ✓ Compound uncertainty theory | ✓ Pre-specified | ✓ Amplification mechanism | ✓ 30K+ obs | **PASS** |
| H4: SEC Receipt → ΔPRisk | ✓ Sign: + | ✓ Spillover effect theory | ✓ Pre-specified | ✓ Regulatory attention mechanism | ✓ 70K-90K obs | **PASS** |
| H5: Triple Integration | ✓ Sign: + | ✓ Compound regulatory pressure | ✓ Pre-specified | ✓ Multiplicative pressure mechanism | ✓ ~20K obs | **PASS** |
| H6: SEC Topics → Q&A Topics | ✓ Sign: + | ✓ Analyst information processing | ✓ Pre-specified | ✓ Analyst-mediated mechanism | ✓ 50K-70K obs | **PASS** |
| H7: Mediation Chain | ✓ Sign: + | ✓ Disclosure quality theory | ✓ Pre-specified | ✓ Information asymmetry reduction | ✓ 50K-70K obs | **PASS** |
| H8: Cross-Doc Alignment | ✓ Sign: + | ✓ Narrative management theory | ✓ Pre-specified | ✓ Disclosure consistency mechanism | ✓ 30K-50K obs | **PASS** |

### Tier 2 Candidates (LLM + Earnings Calls)

| Candidate | Explicit | Evidence-based | Ex-ante | Explanatory | Testable | 5E Pass |
|-----------|----------|----------------|---------|-------------|----------|---------|
| H9: Response Relevance → CAR | ✓ Sign: + | ✓ Transparency signaling | ✓ Pre-specified | ✓ Quality information mechanism | ✓ 100K+ obs | **PASS** |
| H10: Narrative Drift → Volatility | ✓ Sign: + | ✓ Information uncertainty | ✓ Pre-specified | ✓ Strategic change signal | ✓ 50K+ obs | **PASS** |
| H11: FLS Specificity → Error | ✓ Sign: - | ✓ Information provision | ✓ Pre-specified | ✓ Anchor for forecasting | ✓ 50K+ obs | **PASS** |
| H12: CEO-CFO Gap → M&A Premium | ✓ Sign: + | ✓ Internal discord theory | ✓ Pre-specified | ✓ Bargaining power mechanism | ✓ 5K-10K obs | **PASS** |
| H13: Info Novelty → Volume | ✓ Sign: + | ✓ Heterogeneous beliefs | ✓ Pre-specified | ✓ Trading signal mechanism | ✓ 100K+ obs | **PASS** |
| H14: Question Difficulty → Evasion | ✓ Sign: + | ✓ Selective disclosure | ✓ Pre-specified | ✓ Information hiding mechanism | ✓ 100K+ obs | **PASS** |
| H15: Uncertainty Gap → CAR | ✓ Sign: - | ✓ Prepared vs spontaneous | ✓ Pre-specified | ✓ Credibility signaling | ✓ 100K+ obs | **PASS** |
| H16: Confidence Trajectory → CAR | ✓ Sign: - | ✓ Leading indicator theory | ✓ Pre-specified | ✓ Deteriorating outlook mechanism | ✓ 50K+ obs | **PASS** |
| H17: Info Consistency → Dispersion | ✓ Sign: - | ✓ Analyst uncertainty | ✓ Pre-specified | ✓ Factual clarity mechanism | ✓ 50K+ obs | **PASS** |

### Tier 3 Candidates (Political Risk)

| Candidate | Explicit | Evidence-based | Ex-ante | Explanatory | Testable | 5E Pass |
|-----------|----------|----------------|---------|-------------|----------|---------|
| H18: Topic PRisk → Returns | ✓ Sign: - | ✓ Risk pricing theory | ✓ Pre-specified | ✓ Sector-specific exposure | ⚠️ ~3.2K obs | **PASS** |
| H19: Covid Exposure → Dispersion | ✓ Sign: + | ✓ Event uncertainty | ✓ Pre-specified | ✓ Heterogeneous impact | ✓ ~20K obs | **PASS** |
| H20: PRisk × Leverage → Speech | ✓ Sign: - | ✓ Monitoring theory | ✓ Pre-specified | ✓ Creditor discipline mechanism | ✓ 30K+ obs | **PASS** |
| H21: PSentiment → Investment | ✓ Sign: + | ✓ Policy expectations | ✓ Pre-specified | ✓ Investment timing mechanism | ✓ 30K+ obs | **PASS** |
| H22: PRisk Volatility → Vol | ✓ Sign: + | ✓ Uncertainty transmission | ✓ Pre-specified | ✓ Unpredictability mechanism | ✓ 30K+ obs | **PASS** |
| H23: PRisk Concentration → Returns | ✓ Sign: + | ✓ Hedgeability theory | ✓ Pre-specified | ✓ Predictable risk mechanism | ✓ 30K+ obs | **PASS** |

### Tier 4 Candidates (Dictionary Extensions)

| Candidate | Explicit | Evidence-based | Ex-ante | Explanatory | Testable | 5E Pass |
|-----------|----------|----------------|---------|-------------|----------|---------|
| H24: Complexity → Investment Eff | ✓ Sign: - | ✓ Information friction | ✓ Pre-specified | ✓ Obfuscation mechanism | ✓ 100K+ obs | **PASS** |
| H25: Weak Modal → M&A Premium | ✓ Sign: - | ✓ Confidence signaling | ✓ Pre-specified | ✓ Bargaining position mechanism | ✓ 5K-10K obs | **PASS** |
| H26: Tone Consistency → Revision | ✓ Sign: - | ✓ Predictability theory | ✓ Pre-specified | ✓ Expectations priced in | ✓ 50K+ obs | **PASS** |
| H27: Pos/Neg Ratio → Credit | ✓ Sign: - | ✓ Default risk signaling | ✓ Pre-specified | ✓ Financial health signal | ⚠️ Data TBD | **PARTIAL** |

**5E Summary:**
- **27 candidates evaluated**
- **26 PASS** full 5E compliance
- **1 PARTIAL** (H27 - data availability uncertain)

---

## Preliminary Scoring & Ranking (Task 3)

### Scoring Methodology

| Dimension | Weight | Scoring Criteria |
|-----------|--------|------------------|
| **Novelty** | 0.35 | No prior test (1.0), Related tests (0.7), Incremental (0.4) |
| **Feasibility** | 0.35 | All data available + high variation (1.0), Minor construction (0.8), Major gaps (0.5) |
| **Confidence** | 0.30 | >95% power + high variation (1.0), 80-95% power (0.8), <80% power (0.5) |

**Weighted Total = 0.35×N + 0.35×F + 0.30×C**

### Detailed Scoring by Candidate

#### Tier 1: Data Integration (Highest Novelty)

| Candidate | Novelty (0.35) | Feasibility (0.35) | Confidence (0.30) | **Weighted Score** |
|-----------|----------------|--------------------|--------------------|---------------------|
| **H1:** SEC Topics → Call Specificity | 1.00 (no prior test) | 1.00 (50K-70K, high var) | 1.00 (>99% power) | **1.00** |
| **H2:** Resolution Quality → CAR | 1.00 (thread analysis novel) | 0.90 (30K-50K, construction) | 1.00 (>99% power) | **0.97** |
| **H3:** PRisk × Uncertainty → Investment | 1.00 (integration novel) | 1.00 (30K+, high var) | 1.00 (>99% power) | **1.00** |
| **H4:** SEC Receipt → ΔPRisk | 1.00 (data integration novel) | 1.00 (70K-90K) | 1.00 (>99% power) | **1.00** |
| **H5:** Triple Integration | 1.00 (highest novelty) | 0.80 (~20K, complex match) | 0.90 (>95% power) | **0.90** |
| **H6:** SEC Topics → Q&A Topics | 0.90 (extends H1) | 1.00 (50K-70K) | 1.00 (>99% power) | **0.97** |
| **H7:** Mediation Chain | 0.85 (mediation novel) | 1.00 (50K-70K) | 1.00 (>99% power) | **0.95** |
| **H8:** Cross-Doc Alignment | 0.90 (cross-doc novel) | 0.85 (30K-50K, construction) | 1.00 (>99% power) | **0.92** |

#### Tier 2: LLM + Earnings Calls (High Novelty)

| Candidate | Novelty (0.35) | Feasibility (0.35) | Confidence (0.30) | **Weighted Score** |
|-----------|----------------|--------------------|--------------------|---------------------|
| **H9:** Response Relevance → CAR | 0.85 (some evasion studies) | 1.00 (100K+) | 1.00 (>99% power) | **0.95** |
| **H10:** Narrative Drift → Volatility | 0.95 (temporal novel) | 1.00 (50K+, high var) | 1.00 (>99% power) | **0.98** |
| **H11:** FLS Specificity → Error | 0.85 (FLS studied, quality novel) | 1.00 (50K+) | 1.00 (>99% power) | **0.95** |
| **H12:** CEO-CFO Gap → M&A Premium | 0.90 (M&A context novel) | 0.80 (5K-10K) | 0.80 (~95% power) | **0.84** |
| **H13:** Info Novelty → Volume | 0.80 (method novel) | 1.00 (100K+) | 1.00 (>99% power) | **0.93** |
| **H14:** Question Difficulty → Evasion | 0.85 (decomposition novel) | 1.00 (100K+) | 1.00 (>99% power) | **0.95** |
| **H15:** Uncertainty Gap → CAR | 0.70 (similar to H5-B) | 1.00 (100K+) | 1.00 (>99% power) | **0.90** |
| **H16:** Confidence Trajectory → CAR | 0.85 (trajectory novel) | 1.00 (50K+) | 1.00 (>99% power) | **0.95** |
| **H17:** Info Consistency → Dispersion | 0.85 (factual focus novel) | 1.00 (50K+) | 1.00 (>99% power) | **0.95** |

#### Tier 3: Political Risk Integration (Medium Novelty)

| Candidate | Novelty (0.35) | Feasibility (0.35) | Confidence (0.30) | **Weighted Score** |
|-----------|----------------|--------------------|--------------------|---------------------|
| **H18:** Topic PRisk → Returns | 0.80 (granular novel) | 0.60 (~3.2K industry-qtr) | 0.60 (~85% power) | **0.67** |
| **H19:** Covid Exposure → Dispersion | 0.85 (event-specific novel) | 0.80 (~20K, time-limited) | 1.00 (>99% power) | **0.88** |
| **H20:** PRisk × Leverage → Speech | 0.75 (similar to H1b) | 1.00 (30K+) | 1.00 (>99% power) | **0.91** |
| **H21:** PSentiment → Investment | 0.70 (Hassan may cover) | 1.00 (30K+) | 1.00 (>99% power) | **0.90** |
| **H22:** PRisk Volatility → Vol | 0.85 (dynamics novel) | 1.00 (30K+) | 1.00 (>99% power) | **0.95** |
| **H23:** PRisk Concentration → Returns | 0.85 (HHI novel) | 1.00 (30K+) | 1.00 (>99% power) | **0.95** |

#### Tier 4: Dictionary Extensions (Lower Novelty)

| Candidate | Novelty (0.35) | Feasibility (0.35) | Confidence (0.30) | **Weighted Score** |
|-----------|----------------|--------------------|--------------------|---------------------|
| **H24:** Complexity → Investment Eff | 0.70 (new dict, old DV) | 0.70 (may lack variation) | 1.00 (>99% power) | **0.79** |
| **H25:** Weak Modal → M&A Premium | 0.70 (new DV) | 0.70 (5K-10K, variation?) | 0.80 (~95% power) | **0.73** |
| **H26:** Tone Consistency → Revision | 0.60 (incremental) | 1.00 (50K+) | 1.00 (>99% power) | **0.86** |
| **H27:** Pos/Neg Ratio → Credit | 0.70 (credit DV novel) | 0.40 (data TBD) | 0.50 (uncertain) | **0.54** |

---

## Ranked Candidate List

### Sorted by Weighted Score (Descending)

| Rank | Candidate | Score | Tier | Advance to Red Team |
|------|-----------|-------|------|---------------------|
| 1 | **H1:** SEC Topics → Call Specificity | **1.00** | 1 | ✓ YES |
| 1 | **H3:** PRisk × Uncertainty → Investment | **1.00** | 1 | ✓ YES |
| 1 | **H4:** SEC Receipt → ΔPRisk | **1.00** | 1 | ✓ YES |
| 4 | **H10:** Narrative Drift → Volatility | **0.98** | 2 | ✓ YES |
| 5 | **H2:** Resolution Quality → CAR | **0.97** | 1 | ✓ YES |
| 5 | **H6:** SEC Topics → Q&A Topics | **0.97** | 1 | ✓ YES |
| 7 | **H7:** Mediation Chain | **0.95** | 1 | ✓ YES |
| 7 | **H9:** Response Relevance → CAR | **0.95** | 2 | ✓ YES |
| 7 | **H11:** FLS Specificity → Error | **0.95** | 2 | ✓ YES |
| 7 | **H14:** Question Difficulty → Evasion | **0.95** | 2 | ✓ YES |
| 7 | **H16:** Confidence Trajectory → CAR | **0.95** | 2 | ✓ YES |
| 7 | **H17:** Info Consistency → Dispersion | **0.95** | 2 | ✓ YES |
| 7 | **H22:** PRisk Volatility → Vol | **0.95** | 3 | ✓ YES |
| 7 | **H23:** PRisk Concentration → Returns | **0.95** | 3 | ✓ YES |
| 15 | **H13:** Info Novelty → Volume | **0.93** | 2 | ✓ YES |
| 16 | **H8:** Cross-Doc Alignment | **0.92** | 1 | ✓ YES |
| 17 | **H20:** PRisk × Leverage → Speech | **0.91** | 3 | ✓ YES |
| 18 | **H5:** Triple Integration | **0.90** | 1 | ✓ YES |
| 18 | **H15:** Uncertainty Gap → CAR | **0.90** | 2 | ✓ YES |
| 18 | **H21:** PSentiment → Investment | **0.90** | 3 | ✓ YES |
| 21 | **H19:** Covid Exposure → Dispersion | **0.88** | 3 | ✓ YES |
| 22 | **H26:** Tone Consistency → Revision | **0.86** | 4 | ✓ YES |
| 23 | **H12:** CEO-CFO Gap → M&A Premium | **0.84** | 2 | ✓ YES |
| 24 | **H24:** Complexity → Investment Eff | **0.79** | 4 | ✓ YES |
| 25 | **H25:** Weak Modal → M&A Premium | **0.73** | 4 | ✓ YES |
| 26 | **H18:** Topic PRisk → Returns | **0.67** | 3 | ⚠️ BORDERLINE |
| 27 | **H27:** Pos/Neg Ratio → Credit | **0.54** | 4 | ❌ NO |

---

## Selection Summary

### Advancement Threshold: Score ≥ 0.70

| Status | Count | Candidates |
|--------|-------|------------|
| **Advance to Red Team** | **25** | H1-H17, H19-H26 |
| **Borderline (0.67-0.69)** | **1** | H18 (Topic PRisk) |
| **Do Not Advance** | **1** | H27 (Credit data unavailable) |

### Score Distribution

| Score Range | Count | Tier Distribution |
|-------------|-------|-------------------|
| ≥ 0.95 | 14 | 6 Tier 1, 6 Tier 2, 2 Tier 3 |
| 0.85 - 0.94 | 8 | 2 Tier 1, 3 Tier 2, 2 Tier 3, 1 Tier 4 |
| 0.70 - 0.84 | 3 | 0 Tier 1, 1 Tier 2, 0 Tier 3, 2 Tier 4 |
| < 0.70 | 2 | 0 Tier 1, 0 Tier 2, 1 Tier 3, 1 Tier 4 |

### Priority Candidates for Red Team (Score ≥ 0.95)

These 14 candidates have the highest preliminary scores and should receive priority attention in adversarial verification:

1. **H1:** SEC Topics → Call Specificity (1.00) - TIER 1
2. **H3:** PRisk × Uncertainty → Investment (1.00) - TIER 1
3. **H4:** SEC Receipt → ΔPRisk (1.00) - TIER 1
4. **H10:** Narrative Drift → Volatility (0.98) - TIER 2
5. **H2:** Resolution Quality → CAR (0.97) - TIER 1
6. **H6:** SEC Topics → Q&A Topics (0.97) - TIER 1
7. **H7:** Mediation Chain (0.95) - TIER 1
8. **H9:** Response Relevance → CAR (0.95) - TIER 2
9. **H11:** FLS Specificity → Error (0.95) - TIER 2
10. **H14:** Question Difficulty → Evasion (0.95) - TIER 2
11. **H16:** Confidence Trajectory → CAR (0.95) - TIER 2
12. **H17:** Info Consistency → Dispersion (0.95) - TIER 2
13. **H22:** PRisk Volatility → Vol (0.95) - TIER 3
14. **H23:** PRisk Concentration → Returns (0.95) - TIER 3

### Candidates Requiring Special Red Team Attention

| Candidate | Concern | Red Team Focus |
|-----------|---------|----------------|
| H9, H11, H14 | Prior evasiveness/FLS studies exist | Verify specific LLM-based approach is novel |
| H15 | Similar to prior H5-B | Differentiate from failed hypothesis |
| H20, H21 | May overlap with Hassan 2019 | Verify interaction/sentiment angle is novel |
| H24, H25 | Dictionary measure variation risk | Verify within-firm variation adequate |
| H18 | Lower sample size (~3.2K) | Verify statistical power adequate |

---

## Verification Checklist (Plan 52-03)

- [x] **Task 1:** 25-30 candidate hypotheses generated ✓ (27 candidates)
- [x] **Task 1:** Each tier represented ✓ (Tier 1: 8, Tier 2: 9, Tier 3: 6, Tier 4: 4)
- [x] **Task 1:** Candidates derived from verified gaps ✓ (All Top 10 gaps from 52-01 addressed)
- [x] **Task 2:** Full 5E documentation for each candidate ✓ (26 PASS, 1 PARTIAL)
- [x] **Task 2:** Each hypothesis has explicit sign prediction ✓
- [x] **Task 2:** Mechanism documented for each ✓
- [x] **Task 2:** Sample size referenced from 52-02 ✓
- [x] **Task 3:** All candidates scored on 3 dimensions ✓
- [x] **Task 3:** Weighted scores calculated ✓
- [x] **Task 3:** Ranking complete ✓
- [x] **Task 3:** Advancement threshold applied (≥0.70) ✓ (25 advance, 1 borderline, 1 no)
- [x] Each candidate references literature gap from 52-01 ✓
- [x] Each candidate references feasibility from 52-02 ✓
- [x] Candidates ≥ 0.70 flagged for Red Team ✓

---

*Document generated for Phase 52: LLM Literature Review & Novel Hypothesis Discovery*
*Plan 52-03 Tasks 1-3 Complete*
*Date: 2026-02-06*
