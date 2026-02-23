# H10: Tone-at-the-Top Transmission Hypothesis

**Hypothesis Code:** H_TT (Tone at the Top)
**Analysis Date:** 2026-02-21
**Author:** Thesis Author

---

## Table of Contents

1. [Research Question](#1-research-question)
2. [Theoretical Motivation](#2-theoretical-motivation)
3. [Hypotheses](#3-hypotheses)
4. [Empirical Strategy](#4-empirical-strategy)
5. [Model Specifications](#5-model-specifications)
6. [Variable Definitions](#6-variable-definitions)
7. [Sample Construction](#7-sample-construction)
8. [Identification Strategy](#8-identification-strategy)
9. [Estimation Details](#9-estimation-details)
10. [Results Summary](#10-results-summary)
11. [Robustness Tests](#11-robustness-tests)
12. [Limitations](#12-limitations)
13. [Data Sources](#13-data-sources)
14. [References](#14-references)

---

## 1. Research Question

**Primary Question:** Does a CEO's persistent communication style transmit to subordinate managers within the same earnings call?

**Secondary Questions:**
- Is CEO communication style contagious within the corporate hierarchy?
- Does the transmission effect differ across industry contexts (Main vs. Finance vs. Utility)?
- Is the transmission driven by real-time CEO behavior or persistent CEO traits?

---

## 2. Theoretical Motivation

### 2.1 Upper Echelons Theory
Hambrick and Mason (1984) posit that organizational outcomes reflect the values and cognitive bases of powerful actors. The CEO's communication style may establish a "tone at the top" that influences subordinate behavior.

### 2.2 Social Learning Theory
Bandura (1977) suggests that individuals learn by observing others. Non-CEO managers may unconsciously mimic the CEO's uncertainty language patterns during Q&A sessions.

### 2.3 Information Environment
The collective uncertainty expressed by management affects the firm's information environment. If CEO style "trickles down," it amplifies or dampens the overall signal to investors.

---

## 3. Hypotheses

### H_TT1: Call-Level Transmission (Real-Time Style)
> **H_TT1:** A CEO's real-time uncertainty communication style, measured by a rolling 4-call EB-shrunk estimator, positively predicts CFO uncertainty in the same earnings call.

**Prediction:** β₁ > 0 in Model 1

### H_TT2: Turn-Level Transmission (Within-Call Granger)
> **H_TT2:** Within an earnings call, CEO Q&A uncertainty in earlier turns positively predicts Non-CEO manager uncertainty in subsequent turns.

**Prediction:** β₁ > 0 in Model 2

---

## 4. Empirical Strategy

### 4.1 Two-Level Identification

| Level | Design | Identification Source |
|-------|--------|----------------------|
| **Call-Level (H_TT1)** | Cross-call variation in CEO style | Firm × Quarter FE, two-way clustering |
| **Turn-Level (H_TT2)** | Within-call time ordering | Call FE + Speaker FE, Granger-style |

### 4.2 Why Two Models?

**Model 1 (Call-Level):** Tests whether a CEO's *persistent* style (measured across prior calls) affects CFO behavior in the current call. This captures trait-level transmission.

**Model 2 (Turn-Level):** Tests whether CEO behavior in the *current call* affects non-CEO managers in the same call. This captures real-time mimicry.

The combination provides both cross-sectional and within-call identification.

---

## 5. Model Specifications

### 5.1 Model 1: Call-Level Transmission (H_TT1)

$$
\text{IHS}(CFO\_QA\_Unc_{ict}) = \beta_0 + \beta_1 \cdot ClarityStyle\_Realtime_{ict} + \mathbf{X}'_{ict}\boldsymbol{\gamma} + \alpha_i + \delta_{qt} + \varepsilon_{ict}
$$

**Where:**
- $i$ = firm, $c$ = call, $t$ = year, $q$ = quarter
- $\alpha_i$ = Firm fixed effects
- $\delta_{qt}$ = Year-Quarter fixed effects
- $\mathbf{X}_{ict}$ = Control variables (see Section 6)
- Standard errors: Two-way clustered by Firm × CEO

**Key Independent Variable:** `ClarityStyle_Realtime`
- 4-call rolling window of CEO Q&A uncertainty
- Minimum 4 prior calls required
- Empirical Bayes (James-Stein) shrinkage applied
- Standardized within each calendar quarter

### 5.2 Model 2: Turn-Level Transmission (H_TT2)

$$
\text{IHS}(NonCEO\_Turn\_Unc_{jict}) = \beta_0 + \beta_1 \cdot \text{IHS}(CEO\_Prior\_QA\_Unc_{jict}) + \eta_j + \kappa_c + \varepsilon_{jict}
$$

**Where:**
- $j$ = speaker turn, $i$ = firm, $c$ = call, $t$ = year
- $\eta_j$ = Speaker fixed effects (absorbed)
- $\kappa_c$ = Call fixed effects (absorbed)
- $\varepsilon_{jict}$ = Error term

**Key Independent Variable:** `CEO_Prior_QA_Unc`
- Mean uncertainty of CEO Q&A turns *strictly prior* to turn $j$ in the same call
- Computed via expanding mean of CEO's QA turns
- Merged to Non-CEO manager turns via `pd.merge_asof` with `allow_exact_matches=False`

---

## 6. Variable Definitions

### 6.1 Dependent Variables

| Variable | Definition | Transformation | Source |
|----------|------------|----------------|--------|
| `CFO_QA_Uncertainty_pct` | Uncertainty words / Total words × 100 in CFO Q&A remarks | IHS: $\text{arcsinh}(x)$ | Stage 2.1 tokenizer |
| `NonCEO_Turn_Unc_pct` | Uncertainty words / Total words × 100 in Non-CEO manager Q&A turn | IHS: $\text{arcsinh}(x)$ | Stage 2.1 tokenizer |

### 6.2 Key Independent Variables

| Variable | Definition | Construction |
|----------|------------|--------------|
| `ClarityStyle_Realtime` | Rolling EB-shrunk CEO style | 4-call rolling window, min=4, EB shrinkage, quarter-standardized |
| `CEO_Prior_QA_Unc` | Mean CEO uncertainty in prior turns | Expanding mean of CEO QA turns, merged backward |

**ClarityStyle_Realtime Construction:**

1. **Demean by Year-Quarter:**
   $$u^*_{ct} = u_{ct} - \bar{u}_{qt}$$

2. **Rolling Prior Mean (4-call window):**
   $$\bar{u}^{prior}_{ct} = \frac{1}{4}\sum_{k=1}^{4} u^*_{c-k,t}$$

3. **Empirical Bayes Shrinkage:**
   $$\hat{\gamma}_{ct} = (1 - \hat{B}) \cdot \bar{u}^{prior}_{ct}$$
   where $\hat{B} = \min\left(1, \frac{\sigma^2_e}{n \cdot \sigma^2_u}\right)$

4. **Quarter Standardization:**
   $$ClarityStyle\_Realtime_{ct} = \frac{\hat{\gamma}_{ct} - \bar{\gamma}_q}{\text{SD}(\gamma_q)}$$

### 6.3 Control Variables (Model 1 Only)

| Variable | Definition | Expected Sign | Source |
|----------|------------|---------------|--------|
| `Size` | Log(Total Assets), inflation-adjusted | ± | Compustat |
| `BM` | Book-to-Market ratio | ± | Compustat |
| `Lev` | Total Debt / Total Assets | + | Compustat |
| `ROA` | Net Income / Total Assets | - | Compustat |
| `StockRet` | Stock return ([-3, +3] day window around call) | - | CRSP |
| `MarketRet` | Market return over same window | - | CRSP |
| `EPS_Growth` | Quarter-over-quarter EPS growth | - | Compustat |
| `SurpDec` | Earnings surprise decile (IBES) | - | IBES |
| `IHS_CEO_QA_Unc` | CEO Q&A uncertainty (same call) | + | Stage 2.1 |
| `IHS_CEO_Pres_Unc` | CEO Presentation uncertainty | + | Stage 2.1 |

---

## 7. Sample Construction

### 7.1 Industry Samples

| Sample | FF12 Codes | Description |
|--------|------------|-------------|
| **Main** | Excl. 8, 11 | Non-finance, non-utility |
| **Finance** | 11 | Banks, insurance, real estate |
| **Utility** | 8 | Electric, gas, telecommunications |

### 7.2 Filtering Criteria

**Model 1 (Call-Level):**
1. Call has valid `CFO_QA_Uncertainty_pct`
2. Call has valid `ClarityStyle_Realtime` (≥4 prior calls)
3. Call has non-missing control variables
4. Firm has valid GVKEY linkage

**Model 2 (Turn-Level):**
1. Turn is by a Non-CEO manager (role pattern match)
2. Turn is in Q&A segment (`context == "qa"`)
3. At least one prior CEO turn exists in the same call
4. Speaker name is non-missing

### 7.3 Speaker Identification

**CFO Pattern (Narrow):**
```python
CFO_ROLE_PATTERN = r"\bCFO\b|Chief\s+Financial|Financial\s+Officer|Principal\s+Financial"
```

**Non-CEO Manager Pattern (45 keywords):**
```python
MGR_PATTERN = r"PRESIDENT|VP|DIRECTOR|CEO|EVP|SVP|CFO|OFFICER|CHIEF|EXECUTIVE|
HEAD|CHAIRMAN|SENIOR|MANAGER|COO|TREASURER|SECRETARY|MD|DEPUTY|CONTROLLER|
GM|PRINCIPAL|CAO|CIO|CTO|CMO|LEADER|LEAD|CCO|COORDINATOR|AVP|ADMINISTRATOR|
CHAIRWOMAN|CHAIRPERSON|SUPERINTENDENT|DEAN|COMMISSIONER|CA|GOVERNOR|SUPERVISOR|
COACH|PROVOST|CAPTAIN|CHO|RECTOR"
```

**CEO Identification:**
- CEO turns flagged by `is_ceo = role.contains(r"\bCEO\b|Chief Executive")`
- Non-CEO managers: `is_nonceo_mgr = is_manager & ~is_ceo`

---

## 8. Identification Strategy

### 8.1 Threats to Identification

| Threat | Mitigation |
|--------|------------|
| **Omitted firm characteristics** | Firm fixed effects (Model 1) |
| **Time-varying shocks** | Year-Quarter fixed effects (Model 1) |
| **Speaker-specific communication style** | Speaker fixed effects (Model 2) |
| **Call-specific factors** | Call fixed effects (Model 2) |
| **Reverse causality (Model 2)** | Temporal ordering: only *prior* CEO turns used |
| **Serial correlation** | Two-way clustering (Firm × Call for M2) |

### 8.2 Key Assumptions

**Model 1:**
- CEO style is *predetermined* relative to CFO behavior in the same call
- `ClarityStyle_Realtime` captures persistent trait, not current mood

**Model 2:**
- Turn ordering within Q&A is quasi-random (depends on analyst question order)
- CEO's influence on Non-CEO managers operates through observed prior speech, not unobserved cues

**Important Caveat:** Turn ordering is determined by analyst question sequence, which may be strategic. We cannot rule out that analysts target complex questions to certain managers based on factors correlated with CEO behavior. Our identification thus relies on *temporal precedence* rather than true randomization.

### 8.3 Why Model 2 is the Primary Identification

Model 2 exploits the *within-call time ordering* of Q&A turns:
- CEO speaks first in many Q&A exchanges
- Non-CEO managers respond to analyst questions *after* hearing the CEO
- By restricting the IV to *strictly prior* CEO turns, we achieve within-call temporal association consistent with transmission

This design provides temporal identification but should not be interpreted as establishing causal effects. The results are consistent with CEO-to-manager transmission but cannot definitively rule out alternative explanations.

---

## 9. Estimation Details

### 9.1 Software

| Package | Version | Purpose |
|---------|---------|---------|
| `linearmodels` | 0.6.0+ | PanelOLS, AbsorbingLS |
| `statsmodels` | 0.14.6 | Post-estimation diagnostics |
| `numpy` | 2.3.2 | IHS transformation |
| `pandas` | 2.2.3 | Data manipulation |

### 9.2 Model 1 Estimation

```python
from linearmodels.panel import PanelOLS

mod = PanelOLS(
    dependent=reg_df["IHS_CFO_QA_Unc"],
    exog=reg_df[["const", "ClarityStyle_Realtime"] + controls],
    entity_effects=True,      # Firm FE
    time_effects=True,        # Year-Quarter FE
    drop_absorbed=True,
)

# Two-way clustering: Firm × CEO
clusters = pd.DataFrame({
    "gvkey": pd.Categorical(reg_df.index.get_level_values("gvkey")).codes,
    "ceo_id": reg_df["ceo_id"].astype("category").cat.codes,
})
res = mod.fit(cov_type="clustered", clusters=clusters)
```

### 9.3 Model 2 Estimation

```python
from linearmodels.iv.absorbing import AbsorbingLS

# Absorb Speaker FE + Call FE
absorb_df = reg_df[["speaker_name", "file_name"]].copy()
absorb_df["speaker_name"] = absorb_df["speaker_name"].astype("category").cat.codes
absorb_df["file_name"] = absorb_df["file_name"].astype("category").cat.codes

mod = AbsorbingLS(
    dependent=reg_df["IHS_NonCEO_Turn_Unc"],
    exog=reg_df[["const", "IHS_CEO_Prior_QA_Unc"]],
    absorb=absorb_df,
    drop_absorbed=True,
)

# Two-way clustering: Firm × CEO
res = mod.fit(cov_type="clustered", clusters=reg_df[["gvkey", "ceo_id"]])
```

### 9.4 Standard Error Clustering

**Rationale:** CEO style is persistent within CEO-firm spells. Observations from the same CEO are not independent.

**Implementation:** Two-way clustering by Firm and CEO accounts for:
- Correlation within firm (same corporate culture)
- Correlation within CEO (same communication style)

---

## 10. Results Summary

*See `tone_at_top_full_doc.pdf` for complete regression results.*

### 10.1 Interpretation

**H_TT1 (Call-Level):**
- **Main sample:** Confirmed at p<0.001. A one-standard-deviation increase in CEO style increases CFO uncertainty by 0.017 IHS units.
- **Finance/Utility:** No significant effect. Regulated industries may suppress style transmission at the call level.

**H_TT2 (Turn-Level):**
- **Main sample:** Strongly confirmed (t=19.25, p<0.001). Coefficient = 0.042.
- **Finance sample:** Confirmed (t=6.25, p<0.001). Coefficient = 0.031.
- **Utility sample:** Significant with clustered SE (t=3.45, p<0.001), but wild cluster bootstrap p=0.50 (not significant). Small sample (62 firms) limits inference.

### 10.2 Economic Significance

For the Main sample in Model 2:
- A one-standard-deviation increase in CEO prior uncertainty increases manager uncertainty by approximately 0.04 IHS units
- This represents about 2-3% of the within-call standard deviation of manager uncertainty
- In approximate basis points: ~4 bps increase per SD of CEO uncertainty

### 10.3 Key Finding

Tone-at-the-top transmission is primarily a *within-call phenomenon*. CEO behavior in earlier Q&A turns is associated with increased uncertainty in subsequent non-CEO manager turns. However, this association should not be interpreted causally due to potential confounds from strategic analyst questioning.

---

## 11. Robustness Tests

### 11.1 M1 Without CEO Same-Call Controls (Primary Specification)

Per the referee's concern about "bad controls," we run M1 WITHOUT CEO same-call uncertainty controls (`IHS_CEO_QA_Unc`, `IHS_CEO_Pres_Unc`). These variables may block the causal channel if CEO style affects CFO behavior through CEO's own communication in the call.

**Primary Specification Controls:**
- Size, BM, Lev, ROA, StockRet, MarketRet, EPS_Growth, SurpDec

**Robustness:** M1 with CEO same-call controls is available in the appendix.

### 11.2 M2 Local Lag Specifications

To address the referee's concern about time trends, we test alternative CEO uncertainty measures:

| Specification | Description | Main Coef | Main SE |
|---------------|-------------|-----------|---------|
| Baseline | Expanding mean of prior CEO turns | 0.042 | 0.002 |
| Lag1 | Last CEO turn only | — | — |
| Roll2 | Rolling mean of last 2 CEO turns | — | — |
| Roll3 | Rolling mean of last 3 CEO turns | — | — |
| ExpDecay | Exponentially weighted (α=0.5) | — | — |

### 11.3 M2 With Additional Controls

| Specification | Controls Added | Main Coef |
|---------------|----------------|-----------|
| + Turn index | Linear turn position | — |
| + Quadratic time | turn_index + turn_index² | — |
| + Analyst uncertainty | IHS_Analyst_Unc | — |
| Full controls | All above | — |

### 11.4 M2 Clustering Strategy (Per Addendum C)

Model 2 exploits within-call variation. Per the referee's concern, we cluster by (Firm, Call) instead of (Firm, CEO):
- **Rationale:** Clustering by (Firm, CEO) ignores within-call correlation, which is the primary level of variation in M2.
- **Implementation:** `clusters = reg_df[["gvkey", "file_name"]]`

### 11.5 Wild Cluster Bootstrap (Small Samples)

For Utility (62 firms) and Finance samples, we run wild cluster bootstrap with Rademacher weights (n=9999):

| Sample | Clustered SE p-value | Bootstrap p-value | Interpretation |
|--------|---------------------|-------------------|----------------|
| Utility | <0.001 | 0.495 | Inference unreliable due to small sample |
| Finance | <0.001 | — | Not run (sufficient firms) |

**Decision Rule:** When bootstrap p-value differs from clustered p-value by >0.10, we rely on bootstrap as primary inference.

### 11.6 Placebo Test: Future CEO Uncertainty

We test whether FUTURE CEO uncertainty (lead variable) predicts current manager uncertainty. If transmission is real, future CEO uncertainty should NOT predict:

**Specification:** `IHS_NonCEO_Turn_Unc ~ IHS_CEO_Unc_Lead1 + Call FE + Speaker FE`

**Expected Result:** Coefficient ≈ 0 (null effect)

### 11.7 Sample Sensitivity

| Exclusion | Impact |
|-----------|--------|
| Financial crisis (2008-2009) | Not tested |
| High-tech firms | Not tested |
| Small firms (Assets < $100M) | Not tested |

### 11.8 Manager Type Sensitivity

We run M2 separately for:
- CFO turns only
- Top executives (COO, President) only
- Other managers only

This tests whether transmission varies by manager seniority.

---

## 12. Limitations

### 12.1 Internal Validity

1. **Turn ordering not random:** Analyst question order may be strategic. Analysts may direct complex questions to certain managers based on factors correlated with prior CEO communication. Our temporal identification cannot rule out this confound.

2. **Speaker identification errors:** Role-based pattern matching may misclassify some speakers. We have not validated classification accuracy with manual review. Misclassification would attenuate estimates toward zero.

3. **Unobserved shocks:** Call-level shocks may affect both CEO and Non-CEO speech simultaneously.

4. **CEO same-call controls as "bad controls":** In M1, including CEO same-call uncertainty (`IHS_CEO_QA_Unc`, `IHS_CEO_Pres_Unc`) may block the causal channel. Our primary specification excludes these controls.

### 12.2 External Validity

1. **Sample period:** 2002-2018 only; may not generalize to post-COVID era with increased video calls.

2. **Industry coverage:** Finance and Utility samples are small (291 and 62 firms respectively). Inference in these samples is unreliable:
   - Utility: Clustered SE shows significance but wild cluster bootstrap p=0.50
   - Results should be interpreted with caution

3. **Earnings calls only:** May not apply to other disclosure contexts (investor days, conferences).

### 12.3 Measurement

1. **Uncertainty dictionary:** Loughran-McDonald may not capture all uncertainty dimensions (tone, hedging, forward-looking statements).

2. **IHS transformation:** While preserving zeros, may have different interpretation than log for larger values.

3. **EB shrinkage:** Assumes normal distribution of CEO effects.

4. **Speaker ID uniqueness:** Speaker names are NOT unique across firms. We use composite key `gvkey_speaker_name` for Speaker FE to avoid misattributing fixed effects across firms with same-named speakers.

### 12.4 Statistical Inference

1. **Clustering choice:** M2 clusters by (Firm, Call) rather than (Firm, CEO) because the variation of interest is within-call. Results may differ with alternative clustering.

2. **Small sample inference:** For Utility sample (62 firms), we report wild cluster bootstrap p-values in addition to clustered SE. The bootstrap suggests the effect is not statistically significant in this sample.

---

## 13. Data Sources

| Source | Data | Period | Location |
|--------|------|--------|----------|
| Earnings Call Provider | Transcripts, speaker metadata | 2002-2018 | `inputs/Earnings_Calls_Transcripts/` |
| Loughran-McDonald | Uncertainty word list | 1993-2024 | `inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv` |
| WRDS Compustat | Financial variables | 2002-2018 | `inputs/comp_na_daily_all/` |
| WRDS CRSP | Stock returns | 2002-2018 | `inputs/CRSP_DSF/` |
| WRDS IBES | Analyst forecasts | 2002-2018 | `inputs/tr_ibes/` |
| WRDS CCM | GVKEY-PERMNO linkage | - | `inputs/CRSPCompustat_CCM/` |

---

## 14. References

1. Bandura, A. (1977). *Social Learning Theory*. Prentice Hall.
2. Hambrick, D. C., & Mason, P. A. (1984). Upper echelons: The organization as a reflection of its top managers. *Academy of Management Review*, 9(2), 193-206.
3. Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance*, 66(1), 35-65.
4. James, W., & Stein, C. (1961). Estimation with quadratic loss. *Proceedings of the Fourth Berkeley Symposium on Mathematical Statistics and Probability*, 1, 361-379.

---

## Appendix A: Summary Statistics

*See `tone_at_top_full_doc.pdf` for summary statistics.*

---

## Appendix B: Replication Instructions

### Step 1: Build Panel (Stage 3)

```bash
python -m f1d.variables.build_h10_tone_at_top_panel
```

**Outputs:**
- `outputs/variables/tone_at_top/{timestamp}/tone_at_top_panel.parquet`
- `outputs/variables/tone_at_top/{timestamp}/tone_at_top_turns_panel.parquet`

### Step 2: Run Regressions (Stage 4)

```bash
python -m f1d.econometric.run_h10_tone_at_top
```

**Outputs:**
- `outputs/econometric/tone_at_top/{timestamp}/results_main.csv`
- `outputs/econometric/tone_at_top/{timestamp}/results_finance.csv`
- `outputs/econometric/tone_at_top/{timestamp}/results_utility.csv`
- `outputs/econometric/tone_at_top/{timestamp}/tone_at_top_table.tex`

---

*Documentation last updated: 2026-02-22*
