# Phase 56: CEO/Management Uncertainty as Persistent Style - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

---

## Phase Boundary

Replicate Dzieliński, Wagner, Zeckhauser (2020) "Straight talkers and vague talkers: The effects of managerial style in earnings conference calls" CEO fixed effects extraction methodology. This phase estimates CEO communication style as a time-invariant personal trait via CEO fixed effects regression (Equation 4), then validates the measure through robustness specifications. Outcome regressions (Tables 5-7 from paper) are NOT in scope - this phase focuses on CEO style extraction only.

---

## Paper Reference

**Title:** "Straight talkers and vague talkers: The effects of managerial style in earnings conference calls"

**Authors:**
- Michal Dzieliński (Stockholm University)
- Alexander F. Wagner (University of Zurich)
- Richard J. Zeckhauser (Harvard Kennedy School)

**Working Paper:** M-RCBG Faculty Working Paper Series | 2017-02 | Revised 2021

**Previous Title:** "In No (Un-)Certain Terms: Managerial Style in Communicating Earnings News"

**PDF Location:** `papers/FWP_2017_02_v2.pdf` and `papers/FWP_2017_02_v2.txt`

---

## Implementation Decisions

### Equation 4: CEO Fixed Effects Regression (Primary Specification)

```
UncAns_i,t = α + γ_i·CEO_i + Σ_s β_s·Speech_s + Σ_k β_k·FirmChars_k + Year_t + ε_i,t
```

**Components:**

| Element | Variable | Description |
|---------|----------|-------------|
| **Dependent Variable** | UncAns | Frequency of uncertainty words in CEO **answers** (Q&A only) - LM dictionary |
| **Key Parameter** | γ_i | CEO fixed effect coefficient for each CEO i |
| **Speech Controls (Speech_s)** | UncPreCEO | Uncertainty words in CEO's **presentation** (controls for firm culture) |
| | UncQue | Uncertainty words in **analyst questions** (controls for question framing) |
| | NegCall | Negative words / total words (Loughran-McDonald dictionary) |
| **FirmChars Controls** | SurpDec | Earnings surprise decile (-5 to +5) |
| | EPS growth | Year-over-year EPS growth (fraction) |
| | StockRet | Stock return (%) for quarter |
| | MarketRet | Market return (%) for quarter |
| **Fixed Effects** | CEO FE | CEO indicator variables (N_CEO coefficients γ_1,...,γ_N) |
| | Year FE | Year indicator variables |
| **Standard Errors** | Clustered by CEO | Per paper methodology |

### CEO Clarity Measure
- **Definition:** ClarityCEO_i = -γ_i (negative of CEO fixed effect)
- **Raw Distribution:** Mean = -0.62, SD = 0.23 (pre-standardization, paper page 19)
- **Standardization:** AFTER extraction, standardize to mean=0, SD=1
- **Interpretation:** Higher ClarityCEO = clearer communication (fewer uncertainty words used)
- **Economic Meaning:** "A clear-talking CEO (one SD above mean) would typically use less than half as many uncertainty words than a typical fuzzy-talker (one SD below mean)"

### Sample Periods
- **Paper replication:** 2003-2015 (exact paper period: 122,611 calls, 5,095 firms)
- **Extended analysis:** 2002-2018 (full V2 sample)
- **Run BOTH in parallel** for comparison/validation
- **Minimum calls per CEO:** 5 calls during combined tenure (paper page 45, "To qualify for the CEO sample, the manager must have participated in at least 5 calls")

### Table 3 Specifications (Primary)

| Column | Specification | Variables |
|--------|---------------|------------|
| (1) | Baseline | UncAns ~ CEO FE + UncPreCEO + UncQue + Year FE |
| (2) | Full Equation 4 | UncAns ~ CEO FE + UncPreCEO + UncQue + NegCall + SurpDec + EPS growth + StockRet + MarketRet + Year FE |

**Notes:**
- Benchmark R² = 0.31 (CEO FE only, no other controls)
- ∆R² reports incremental explanatory power vs benchmark
- Column (1) ∆R² = 0.0507 (UncPreCEO + UncQue add 5.07% explanatory power)
- Column (2) ∆R² = 0.0537 (FirmChars add 0.30% more)
- All variables defined in paper Table A.1
- F-statistics for CEO FE joint significance: 6.320 (Col 1) and 6.139 (Col 2), both p < 0.001

### Table IA.1 Robustness Specifications (8 Total)

| Spec | Variables | Correlation with Baseline |
|------|-----------|---------------------------|
| (0) | CEO FE only | 0.99 (equivalent to averaging UncAns per CEO) |
| (1) | + UncPreCEO | 0.99 |
| (2) | + UncPreCEO + Firm chars | 0.99 |
| (3) | Baseline (Eq. 4 = Table 3 Col 1) | 1.00 (reference) |
| (4) | + UncPreCFO + UncAnsCFO | 0.96 |
| (5) | + UncEPR (earnings press releases) | 0.95 |
| (6) | + AnDispPre (analyst dispersion in presentations) | 0.91 |
| (7) | + ∆UncPreCEO (change in presentation uncertainty) | 0.90 |

**Output:** Correlation matrix of CEO FE across specifications vs baseline (spec 3)

### Variable Mapping: V2 to Paper

| Paper Variable | V2 Equivalent | Notes |
|----------------|---------------|-------|
| UncAns (CEO Q&A uncertainty) | CEO_QA_Uncertainty_pct | LM uncertainty words in CEO Q&A |
| UncPreCEO (CEO presentation) | CEO_Pres_Uncertainty_pct | LM uncertainty in CEO presentation |
| UncQue (analyst Q&A) | Analyst_QA_Uncertainty_pct | LM uncertainty in analyst questions |
| NegCall | CEO_All_Negative_pct | LM negative words (CEO_All_Negative_pct) |
| SurpDec | SurpDec | Earnings surprise decile (from V2, already computed) |
| EPS growth | EPS_Growth | Year-over-year EPS growth (from V2) |
| StockRet | StockRet | Stock return for quarter (from V2) |
| MarketRet | MarketRet | Market return for quarter (from V2) |

### Additional Variables for Robustness (Table IA.1)

| Variable | Description | V2 Mapping |
|----------|-------------|------------|
| UncPreCFO | Uncertainty in CFO presentation | CFO_Pres_Uncertainty_pct |
| UncAnsCFO | Uncertainty in CFO answers | CFO_QA_Uncertainty_pct |
| UncEPR | Uncertainty in earnings press releases | NOT in V2 - skip or note limitation |
| AnDispPre | Analyst dispersion in presentations | NOT in V2 - skip or note limitation |
| ∆UncPreCEO | Change in CEO presentation uncertainty | Compute as difference |

### Data Requirements
- **CEO identification:** Must have CEO speaker role tagged in V2 data (from ExecuComp matching)
- **Q&A vs Presentation separation:** Required for UncAns vs UncPreCEO
- **Analyst questions:** Must be separable from CEO answers (speaker_role field)
- **Minimum calls:** 5 calls per CEO minimum (paper requirement)
- **Time periods:** 2002-2018 available, filter to 2003-2015 for paper replication

---

## Claude's Discretion

None - this is a strict replication. All specifications must match paper exactly.

---

## Specific Ideas

### Key Findings from Paper (for reference):
- **CEO heterogeneity:** "The heterogeneity is substantial. The mean and standard deviation are -0.62 and 0.23 respectively" (page 19)
- **Economic meaning:** Clear CEOs use <50% uncertainty words compared to fuzzy CEOs
- **Benchmark R² = 0.31:** CEO fixed effects alone explain 31% of variation in UncAns
- **UncPreCEO + UncQue:** Add >5% explanatory power (∆R² = 0.0507)
- **FirmChars:** Add minimal explanatory power (<0.3%) - CEO FE dominates
- **F-statistics:** CEO FE joint significance at p < 0.001 in all specifications
- **Robustness:** All 8 Table IA.1 specifications correlate ≥0.90 with baseline

### Distribution Characteristics (Figure 3 replication):
- "Continuous with a fatter left tail" - more extremely unclear CEOs than extremely clear
- No clear outliers
- Post-standardization: mean=0, SD=1 for subsequent analysis

---

## Deferred Ideas

**Outcome regressions (Tables 5-7):** Testing whether ClarityCEO predicts firm outcomes (abnormal returns, analyst forecast dispersion, Tobin's Q, analyst recommendations) - deferred to potential future phase

**CFO/Other manager styles:** Paper estimates separate models for CFOs - CEO-only focus for Phase 56

**Cross-sectional analyses (Table 4):** Correlating ClarityCEO with CEO characteristics (ability, age, gender, firm size, intangibles) - not in Phase 56 scope

**CEO turnover analysis:** Paper uses turnover sample to include firm fixed effects - not in Phase 56 scope

---

## Outputs

### 1. CEO Scores Dataset
- **File:** `ceo_clarity_scores.parquet`
- **Columns:**
  - ceo_id (CEO identifier)
  - ceo_name (from ExecuComp matching)
  - gamma_i (raw CEO fixed effect coefficient)
  - ClarityCEO_raw = -gamma_i (negative of FE)
  - ClarityCEO (standardized to mean=0, SD=1)
  - n_calls (number of calls used for estimation)
  - sample_period (2003-2015 or 2002-2018)
  - specification (which model specification)

### 2. Results Tables
- **Table 3 replication:**
  - Coefficients for UncPreCEO, UncQue, NegCall, SurpDec, EPS growth, StockRet, MarketRet
  - t-statistics (clustered by CEO)
  - R² and ∆R² values
  - F-statistics for CEO FE joint significance
  - For both sample periods
- **Table IA.1 replication:**
  - Correlation matrix of CEO FE across 8 specifications vs baseline
  - For both sample periods

### 3. Distribution Plots
- **Figure 3 replication:** Histogram of ClarityCEO (pre-standardization)
  - Mean = -0.62, SD = 0.23 annotations
  - Visual representation of "fatter left tail"
  - For both sample periods

### 4. Summary Report
- **Sample statistics:**
  - N_CEOs (total and with ≥5 calls)
  - N_obs (total observations)
  - N_firms
  - For both sample periods
- **ClarityCEO distribution:**
  - Mean, SD, min, max, quintiles (pre-standardization)
  - Post-standardization verification (mean≈0, SD≈1)
- **Specification comparison:**
  - ∆R² values across specifications
  - Correlation with baseline
  - F-statistics for CEO FE joint significance

---

## Technical Notes

### Regression Implementation
- **Package:** statsmodels OLS with Formula API or linearmodels PanelOLS
- **Fixed effects:** C(ceo_id) for CEO indicator variables, C(year) for Year indicator variables
- **Clustering:** cov_type='cluster', cov_kwds={'groups': ceo_id}
- **Reference CEO:** CEO with most observations (or first alphabetically) becomes reference (γ=0), adjust all others accordingly

### Variable Construction Details
- **Uncertainty measures:**
  ```
  UncAns = UncertaintyCount_QA_CEO / TotalWords_QA_CEO × 100
  UncPreCEO = UncertaintyCount_Pres_CEO / TotalWords_Pres_CEO × 100
  UncQue = UncertaintyCount_QA_Analyst / TotalWords_QA_Analyst × 100
  ```
- **SurpDec construction:**
  ```
  EarningsSurprise = (ActualEPS - ForecastEPS) / SharePrice
  SurpDec = pd.qcut(EarningsSurprise, 10, labels=False, duplicates='drop')
  # Map to -5 to +5 scale (deciles -5, -4, ..., 0, ..., +4, +5)
  ```
- **Standardization (Post-Extraction):**
  ```python
  # After extracting gamma_i from regression
  ClarityCEO_raw = -gamma_i
  ClarityCEO = (ClarityCEO_raw - ClarityCEO_raw.mean()) / ClarityCEO_raw.std()
  ```

### Minimum Calls Filter
```python
# Filter to CEOs with at least 5 calls (paper requirement)
ceo_call_counts = df['ceo_id'].value_counts()
valid_ceos = set(ceo_call_counts[ceo_call_counts >= 5].index)
df = df[df['ceo_id'].isin(valid_ceos)]
```

### Sample Period Filtering
```python
# Paper replication: 2003-2015
df_paper = df[(df['year'] >= 2003) & (df['year'] <= 2015)]

# Extended: 2002-2018
df_extended = df[(df['year'] >= 2002) & (df['year'] <= 2018)]
```

---

## Validation Checklist

Before marking Phase 56 complete, verify:

- [ ] CEO FE extraction matches Equation 4 specification exactly
- [ ] UncAns = CEO Q&A uncertainty only (not All, not Presentation)
- [ ] All controls (UncPreCEO, UncQue, NegCall, FirmChars) included in Column (2)
- [ ] Year fixed effects included
- [ ] Standard errors clustered by CEO
- [ ] ClarityCEO = -gamma_i (negative of FE)
- [ ] Post-extraction standardization to mean=0, SD=1
- [ ] Minimum 5 calls per CEO filter applied
- [ ] Both sample periods run (2003-2015 and 2002-2018)
- [ ] All 8 Table IA.1 specifications estimated
- [ ] Correlation matrix matches format (baseline correlation = 1.00)
- [ ] Distribution histogram shows mean=-0.62, SD=0.23 for 2003-2015 sample

---

*Phase: 56-ceo-management-uncertainty-as-persistent-style*
*Context gathered: 2026-02-06*
*Paper: Dzieliński, Wagner, Zeckhauser (2020) "Straight talkers and vague talkers"*
