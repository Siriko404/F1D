# H10: Tone-at-the-Top Transmission - Audit Documentation

**Document Version:** 2.1 (Post-Dedup Fix)
**Analysis Date:** 2026-02-22
**Author:** Thesis Author

---

## 0. Data Quality Audit (Round 2 Fix)

### 0.1 Issue Identified

The Round 2 audit identified a **critical data integrity issue**: M2 observation counts were inconsistent due to duplicate `(file_name, speaker_number)` pairs in raw token data.

**Root Cause:**
1. Tokenization produced duplicate rows for the same turn (6,820 duplicates across 2002-2018)
2. 2,149 duplicate groups had divergent uncertainty values (variance > 1e-6)
3. Without dedup, CEO merge could create row explosion

### 0.2 Fix Applied

Added deterministic deduplication to `build_h10_tone_at_top_panel.py`:

```python
# Sort deterministically before dedup
qa_tokens = qa_tokens.sort_values(
    ["file_name", "speaker_number", "Turn_Uncertainty_pct"],
    kind="stable"
).reset_index(drop=True)

# Check for divergent values in duplicates
dup_mask = qa_tokens.duplicated(subset=["file_name", "speaker_number"], keep=False)
if dup_mask.any():
    dup_groups = qa_tokens[dup_mask].groupby(["file_name", "speaker_number"])
    unc_variance = dup_groups["Turn_Uncertainty_pct"].var()
    divergent = unc_variance[unc_variance > 1e-6]
    if len(divergent) > 0:
        print(f"[WARNING] {len(divergent)} duplicate groups have divergent uncertainty values")

# Deduplicate keeping first occurrence after deterministic sort
qa_tokens = qa_tokens.drop_duplicates(
    subset=["file_name", "speaker_number"],
    keep="first"
).copy()
```

### 0.3 Validation Added

- **CEO merge validation:** `validate="m:1"` with explicit duplicate check
- **Controls merge validation:** `validate="m:1"` with row count assertion
- **Final uniqueness verification:** Fatal error if duplicate turn keys exist
- **Reconciliation table:** Generated at each pipeline stage

### 0.4 Impact on Results

| Metric | Before Fix | After Fix | Change |
|--------|------------|-----------|--------|
| Main M2 N | 1,699,402 | **1,697,632** | -1,770 |
| Duplicate rows removed | 0 | **6,820** | +6,820 |
| Divergent uncertainty groups | N/A | 2,149 | Logged |
| Main M2 coef | 0.0424*** | **0.0426*** | +0.0002 |
| Placebo coef (Main) | 0.0372*** | **0.0373*** | +0.0001 |
| Utility bootstrap p | 0.4951 | **0.4918** | -0.0033 |

**Conclusion:** The duplicate removal had minimal impact on coefficients (< 0.5% change). The placebo test remains significant, confirming the original correlation was NOT caused by duplicates but by substantive confounding.

### 0.5 Reconciliation Table (2026-02-22 Run)

| Stage | N Rows | Delta |
|-------|--------|-------|
| 1. Raw QA tokens | 9,160,874 | - |
| 2. Post dedup | 9,154,054 | -6,820 |
| 3. Post CEO merge | 9,154,054 | 0 |
| 4. Post manager filter | 2,065,473 | -7,088,581 |
| 5. Post controls merge | 2,065,473 | 0 |
| 6. Final M2 | 1,697,632 | -367,841 |

---

## Executive Summary

This document provides complete documentation for the H10 Tone-at-the-Top hypothesis, addressing all concerns raised in the referee report.

### ⚠️ CRITICAL FINDING: Placebo Test Failure

**The placebo test FAILED.** Future CEO uncertainty (Lead1) significantly predicts current manager uncertainty:
- Main: β = 0.0372*** (SE = 0.0012)
- Finance: β = 0.0407*** (SE = 0.0029)
- Utility: β = 0.0349*** (SE = 0.0054)

This suggests **confounding or reverse causality** rather than a causal transmission effect. The results should be interpreted as **within-call temporal association**, NOT evidence of CEO-to-manager influence.

### Summary of Results

| Sample | Model | Key IV | Coefficient | SE | t-stat | p-value | N |
|--------|-------|--------|-------------|-----|--------|---------|---|
| Main | M1 | ClarityStyle_Realtime | 0.0173 | 0.0037 | 4.66 | <0.001 | 43,571 |
| Main | M2 | IHS_CEO_Prior_QA_Unc | **0.0426** | 0.0022 | 19.37 | <0.001 | **1,697,632** |
| Finance | M1 | ClarityStyle_Realtime | 0.0047 | 0.0080 | 0.59 | 0.558 | 6,837 |
| Finance | M2 | IHS_CEO_Prior_QA_Unc | 0.0312 | 0.0050 | 6.27 | <0.001 | 325,224 |
| Utility | M1 | ClarityStyle_Realtime | -0.0124 | 0.0126 | -0.99 | 0.323 | 1,430 |
| Utility | M2 | IHS_CEO_Prior_QA_Unc | **0.0247** | 0.0071 | 3.50 | <0.001 | **62,453** |

### Wild Cluster Bootstrap Results

| Sample | N Firms | Clustered SE p-value | Bootstrap p-value | Interpretation |
|--------|---------|---------------------|-------------------|----------------|
| Utility | 62 | <0.001 | **0.4918** | NOT significant with bootstrap |
| Finance | 291 | <0.001 | — | Bootstrap not run (≥100 firms) |

---

## 1. Research Question

**Primary Question:** Does a CEO's persistent communication style transmit to subordinate managers within the same earnings call?

**Key Distinction:** We document *within-call temporal association* consistent with transmission. We do NOT claim causal effects due to:
1. **Failed placebo test** - future CEO uncertainty predicts current manager uncertainty
2. **Strategic analyst questioning** - turn ordering is not random
3. **Call-level confounds** - unobserved factors may affect both CEO and manager speech

---

## 2. Hypotheses

### H_TT1: Call-Level Transmission (Real-Time Style)
> A CEO's real-time uncertainty communication style, measured by a rolling 4-call EB-shrunk estimator, positively predicts CFO uncertainty in the same earnings call.

**Result:** SUPPORTED for Main sample (β = 0.0173, p < 0.001), NOT for Finance (p = 0.558) or Utility (p = 0.323).

### H_TT2: Turn-Level Transmission (Within-Call)
> Within an earnings call, CEO Q&A uncertainty in earlier turns positively predicts Non-CEO manager uncertainty in subsequent turns.

**Result:** STATISTICALLY SIGNIFICANT for all samples, BUT:
- **Placebo test FAILS** - future CEO uncertainty also predicts manager uncertainty
- **Bootstrap p-value = 0.4951** for Utility sample (NOT significant)
- Results should be interpreted as association, NOT causation

---

## 3. Model Specifications

### 3.1 Model 1: Call-Level (H_TT1)

$$
\text{IHS}(CFO\_QA\_Unc_{ict}) = \beta_0 + \beta_1 \cdot ClarityStyle\_Realtime_{ict} + \mathbf{X}'_{ict}\boldsymbol{\gamma} + \alpha_i + \delta_{qt} + \varepsilon_{ict}
$$

**Fixed Effects:** Firm FE + Year-Quarter FE
**Clustering:** Two-way by (Firm, CEO)
**Primary Controls (no CEO same-call):** Size, BM, Lev, ROA, StockRet, MarketRet, EPS_Growth, SurpDec

### 3.2 Model 2: Turn-Level (H_TT2)

$$
\text{IHS}(NonCEO\_Turn\_Unc_{jict}) = \beta_0 + \beta_1 \cdot \text{IHS}(CEO\_Prior\_QA\_Unc_{jict}) + \eta_j + \kappa_c + \varepsilon_{jict}
$$

**Fixed Effects:** Speaker FE + Call FE (absorbed via AbsorbingLS)
**Clustering:** Two-way by (Firm, Call) — **CORRECTED per Addendum C**

---

## 4. Robustness Tests

### 4.1 M2 Local Lag Specifications

| Specification | Main | Finance | Utility |
|---------------|------|---------|---------|
| Baseline (Expanding Mean) | 0.0424*** | 0.0312*** | 0.0239*** |
| Lag1 (Last CEO turn) | 0.0167*** | 0.0131*** | 0.0133** |
| Roll2 (Last 2 turns) | 0.0221*** | 0.0186*** | 0.0166*** |
| Roll3 (Last 3 turns) | 0.0243*** | 0.0208*** | 0.0155** |
| Exp. Decay (α=0.5) | 0.0250*** | 0.0201*** | 0.0106* |

**Finding:** Effects persist across all lag specifications, but coefficients are smaller for local lags (Lag1: 0.0167 vs Baseline: 0.0424).

### 4.2 M2 With Additional Controls

| Specification | Main | Finance | Utility |
|---------------|------|---------|---------|
| Baseline (no controls) | 0.0424*** | 0.0312*** | 0.0239*** |
| + Turn index | 0.0500*** | 0.0362*** | 0.0269*** |
| + Quadratic time | 0.0487*** | 0.0348*** | 0.0257*** |
| + Analyst uncertainty | 0.0319*** | 0.0227*** | 0.0195*** |
| Full controls | 0.0391*** | 0.0249*** | 0.0204*** |

**Finding:** Effects persist with controls. Analyst uncertainty control attenuates coefficient (0.0424 → 0.0319), suggesting analyst questions explain ~25% of the association.

### 4.3 Placebo Test: Future CEO Uncertainty (CRITICAL)

| Sample | CEO Unc. Lead1 Coef | SE | p-value | Expected | Result |
|--------|---------------------|-----|---------|----------|--------|
| Main | **0.0373** | 0.0012 | <0.001 | ≈ 0 | **FAILED** |
| Finance | 0.0407 | 0.0029 | <0.001 | ≈ 0 | **FAILED** |
| Utility | **0.0350** | 0.0054 | <0.001 | ≈ 0 | **FAILED** |

**Interpretation:** Future CEO uncertainty (CEO Unc. Lead1) should NOT predict current manager uncertainty if the effect is truly causal. The highly significant coefficients suggest:

1. **Call-level confounding:** Unobserved call characteristics (complexity, news, market conditions) affect BOTH CEO and manager speech
2. **Reverse causality:** Manager speech may influence subsequent CEO speech
3. **Strategic ordering:** Analysts may direct complex questions to both CEOs and managers based on unobserved factors

**Implication:** The M2 results should be interpreted as **within-call association**, NOT evidence of CEO-to-manager transmission.

---

## 5. Wild Cluster Bootstrap

For small samples (N firms < 100), we use wild cluster bootstrap with Rademacher weights.

### Utility Sample (N = 62 firms)

| Method | p-value |
|--------|---------|
| Clustered SE (Firm × Call) | <0.001 |
| Wild Cluster Bootstrap (n=9999) | **0.4951** |

**Interpretation:** The bootstrap p-value indicates the Utility M2 effect is **NOT statistically significant** when using more reliable small-sample inference. The clustered SE is unreliable with only 62 clusters.

---

## 6. Economic Significance

### M2 Baseline (Main Sample)

| Metric | Value |
|--------|-------|
| β (CEO Prior Unc.) | 0.0424 |
| SD(CEO Prior Unc., IHS) | ~1.92 |
| SD(Manager Unc., IHS) | ~2.15 |
| Δ from 1 SD CEO Unc. | ~0.08 IHS units |
| As % of Manager Unc. SD | ~3.8% |
| Approx. Basis Points | ~8 bps |

**Interpretation:** A one-standard-deviation increase in CEO prior uncertainty increases manager uncertainty by approximately 3-4% of its standard deviation, or about 8 basis points.

---

## 7. Sample Construction

### 7.1 Sample Sizes

| Sample | FF12 Codes | N Calls (M1) | N Turns (M2) | N Firms |
|--------|------------|--------------|--------------|---------|
| Main | Excl. 8, 11 | 43,571 | **1,697,632** | 1,776 |
| Finance | 11 | 6,837 | **325,224** | 291 |
| Utility | 8 | 1,430 | **62,453** | 62 |

**Note:** M2 counts updated after Round 2 deduplication fix (6,820 duplicate turns removed).

### 7.2 M2 Filtering

| Metric | Main | Finance | Utility |
|--------|------|---------|---------|
| Total Manager Turns | 1,485,219 | 287,412 | 52,916 |
| Excluded (no prior CEO turn) | 261,930 | 35,293 | 5,648 |
| Exclusion Rate | 17.6% | 12.3% | 10.7% |
| Valid M2 Observations | 1,223,289 | 252,119 | 47,268 |

### 7.3 Speaker Identification

- **CFO Pattern:** `\bCFO\b|Chief\s+Financial|Financial\s+Officer|Principal\s+Financial`
- **CEO Pattern:** `\bCEO\b|Chief Executive`
- **Non-CEO Manager Pattern:** 45 keywords (PRESIDENT, VP, DIRECTOR, etc.)
- **Speaker ID:** Composite key `gvkey_speaker_name` ensures unique Speaker FE

---

## 8. Estimation Details

### 8.1 M1 Estimation

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

### 8.2 M2 Estimation

```python
from linearmodels.iv.absorbing import AbsorbingLS

# Use composite speaker_id to avoid name collision
absorb_df = reg_df[["speaker_id", "file_name"]].copy()
absorb_df = absorb_df.astype("category").apply(lambda x: x.cat.codes)

mod = AbsorbingLS(
    dependent=reg_df["IHS_NonCEO_Turn_Unc"],
    exog=reg_df[["const", "IHS_CEO_Prior_QA_Unc"]],
    absorb=absorb_df,
    drop_absorbed=True,
)

# CORRECTED: Two-way clustering by Firm × Call (not Firm × CEO)
clusters = reg_df[["gvkey", "file_name"]].copy()
clusters = clusters.astype("category").apply(lambda x: x.cat.codes)
res = mod.fit(cov_type="clustered", clusters=clusters)
```

### 8.3 Wild Cluster Bootstrap

```python
def wild_cluster_bootstrap(df, dv, iv, cluster_col, n_bootstrap=9999, seed=42):
    # Draw Rademacher weights (±1) for each cluster
    weights = np.random.choice([-1, 1], size=n_clusters)

    # Create wild residuals
    wild_resid = np.array([weight_map[c] * r for c, r in zip(df[cluster_col], resid)])

    # Bootstrap outcome and re-estimate
    y_boot = X @ beta + wild_resid
    beta_boot = np.linalg.lstsq(X, y_boot, rcond=None)[0]

    # Two-sided p-value
    p_value = np.mean(np.abs(boot_coefs) >= np.abs(baseline_coef))
```

---

## 9. Limitations

### 9.1 Internal Validity

1. **Placebo test failure:** Future CEO uncertainty predicts manager uncertainty, suggesting confounding or reverse causality.

2. **Turn ordering not random:** Analyst question order may be strategic. Analysts may direct complex questions to certain managers based on factors correlated with prior CEO communication.

3. **Speaker identification errors:** Role-based pattern matching may misclassify some speakers. No manual validation performed.

4. **CEO same-call controls as "bad controls":** Including CEO same-call uncertainty may block the causal channel. Primary specification excludes these.

### 9.2 Statistical Inference

1. **Small sample inference:** Utility sample (62 firms) shows significant clustered SE but NOT significant bootstrap p-value. Results for Utility should be interpreted with extreme caution.

2. **Clustering choice:** M2 clusters by (Firm, Call). Results may differ with (Firm, CEO) clustering.

### 9.3 External Validity

1. **Sample period:** 2002-2018 only; may not generalize to post-COVID era.
2. **Industry coverage:** Finance and Utility samples are small and underpowered.
3. **Earnings calls only:** May not apply to other disclosure contexts.

---

## 10. Data Sources

| Source | Data | Period |
|--------|------|--------|
| Earnings Call Provider | Transcripts, speaker metadata | 2002-2018 |
| Loughran-McDonald | Uncertainty word list | 1993-2024 |
| WRDS Compustat | Financial variables | 2002-2018 |
| WRDS CRSP | Stock returns | 2002-2018 |
| WRDS IBES | Analyst forecasts | 2002-2018 |

---

## 11. Files Generated

| File | Description |
|------|-------------|
| `H10_TONE_AT_TOP_AUDIT.md` | This documentation file |
| `H10_TONE_AT_TOP_TABLES.tex` | Complete LaTeX tables for all specifications |
| `tone_at_top_panel.parquet` | Call-level panel (112,968 calls) |
| `tone_at_top_turns_panel.parquet` | Turn-level panel (**1,697,632** turns) |
| `reconciliation_table.csv` | Row count reconciliation by pipeline stage |
| `report.md` | Detailed coefficient output |
| `coefficients_*.csv` | Individual coefficient tables for each specification |

---

## 12. Revision Changes

| Issue | v1.0 | v2.0 | v2.1 (Current) |
|-------|------|------|----------------|
| M1 CEO controls | Included | Excluded (primary spec) | Same |
| M2 clustering | Firm × CEO | Firm × Call | Same |
| Speaker FE key | speaker_name | gvkey_speaker_name | Same |
| Bootstrap | Not run | Wild cluster bootstrap | Same |
| Robustness specs | Not available | Local lags, time controls, placebo | Same |
| Economic significance | Not computed | Calculated | Same |
| Causal language | "Granger-style causality" | "Within-call temporal association" | Same |
| Placebo test | Not run | RUN - FAILED | Same |
| **Duplicate deduplication** | **Not applied** | **Not applied** | **Deterministic dedup (6,820 removed)** |
| **Merge validation** | **None** | **None** | **validate="m:1" with assertions** |
| **Reconciliation table** | **None** | **None** | **Generated** |
| **M2 N (Main)** | 1,699,402 | 1,699,402 | **1,697,632** |

---

## 13. Recommendations for Revision

Given the failed placebo test, we recommend:

1. **Soften causal claims:** Do not claim "transmission" or "influence" - use "association" or "correlation"

2. **Acknowledge the placebo failure:** Explicitly discuss in the paper

3. **Alternative interpretation:** The association may reflect:
   - Call-level confounds (complexity, news)
   - Strategic analyst behavior
   - Common shocks to all speakers

4. **Utility sample:** Either exclude or heavily caveat due to bootstrap nonsignificance

5. **Future research:** Suggest instrumental variable approaches or natural experiments to address endogeneity

---

## 14. References

1. Bandura, A. (1977). *Social Learning Theory*. Prentice Hall.
2. Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics*, 90(3), 414-427.
3. Hambrick, D. C., & Mason, P. A. (1984). Upper echelons: The organization as a reflection of its top managers. *Academy of Management Review*, 9(2), 193-206.
4. Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance*, 66(1), 35-65.
