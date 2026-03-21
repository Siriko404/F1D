# H11 Suite -- Second-Layer Red-Team Audit

**Suite ID:** H11 (Political Risk & Uncertainty -- Base, Lag, Lead)
**Red-team audit date:** 2026-03-18
**Auditor posture:** Hostile-but-fair, fresh-context, adversarial toward BOTH implementation and first-layer audit
**First-layer audit under review:** `docs/provenance/H11.md` (dated 2026-03-15, revised same date incorporating prior red-team feedback)

---

## A. Meta-Audit: Is the First-Layer Audit Factually Correct?

### A1) Verified Correct Claims

| # | First-layer claim | Evidence | Status |
|---|-------------------|----------|--------|
| 1 | 4 DVs x 3 samples = 12 base regressions | `run_h11_prisk_uncertainty.py` CONFIG has 4 DVs and 3 samples; single loop with no IV sub-loop | VERIFIED FACT |
| 2 | Lag/Lead runners produce 4 DVs x 3 samples x 2 IVs = 24 regressions each | Lag/Lead runners loop over `iv_vars` (2 entries) x DVs (4) x samples (3) | VERIFIED FACT |
| 3 | Total regression count: 12 + 24 + 24 = 60 | Arithmetic verified | VERIFIED FACT |
| 4 | PRiskQ deduplication keeps max | `sort_values("PRisk", ascending=False).drop_duplicates(..., keep="first")` in all 5 builder files | VERIFIED FACT |
| 5 | BookLev built but unused in regressions | `BookLevBuilder` imported in all 3 panel builders; `BookLev` absent from `BASE_CONTROLS` in all 3 runners | VERIFIED FACT |
| 6 | Table notes claim "All continuous controls are standardized" but no standardization in code | LaTeX lines 352 (base), 396 (lag), 398 (lead) all contain this claim; no z-score or standardization code anywhere in the pipeline | VERIFIED FACT |
| 7 | `set_index(["gvkey", "year"])` used for PanelOLS in all 3 runners | Lines 191 (base), 200 (lag), 203 (lead) | VERIFIED FACT |
| 8 | One-tailed test formula: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` | Identical formula in all 3 runners | VERIFIED FACT |
| 9 | Entity + Time FE with `drop_absorbed=True` | `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)` and `fit(cov_type="clustered", cluster_entity=True)` in all 3 runners | VERIFIED FACT |
| 10 | Year extracted from `start_date` via `pd.to_datetime(...).dt.year` | Panel builder line 149 (base), 151 (lag), 156 (lead) | VERIFIED FACT |
| 11 | Zero-row-delta enforcement on all merges | `if delta != 0: raise ValueError(...)` in all 3 panel builders | VERIFIED FACT |
| 12 | Warning suppression for covariance rank | `warnings.filterwarnings("ignore", message="covariance of constraints does not have full rank")` in all 3 runners | VERIFIED FACT |
| 13 | Broad exception catch: `except Exception as e: return None, {}` | Present in all 3 runners' `run_regression` functions | VERIFIED FACT |
| 14 | Minimum calls filter >= 5 applied after complete-case deletion | Code sequence: `prepare_regression_data` (dropna) then `groupby("gvkey").transform("count")` then `>= CONFIG["min_calls"]` | VERIFIED FACT |
| 15 | `_get_prev_quarter` / `_get_next_quarter` arithmetic | "2010q1" -> "2009q4", "2010q4" -> "2011q1", etc. Hand-verified all 4 boundary conditions for all 4 functions | VERIFIED FACT |
| 16 | `_get_prev2_quarter` / `_get_next2_quarter` arithmetic | "2010q1" -> "2009q3", "2010q2" -> "2009q4", "2010q3" -> "2010q1", etc. Hand-verified | VERIFIED FACT |
| 17 | Lag builders load year_start-1 data; Lead builders load year_end+1 data | `prisk_q_lag.py` line 107: `year_list.append(min(year_list) - 1)`; `prisk_q_lead.py` line 112: `year_list.append(max(year_list) + 1)` | VERIFIED FACT |
| 18 | Lag2 builder loads year_start-1 AND year_start-2 | `prisk_q_lag2.py` line 110: `year_list.extend([min(year_list) - 1, min(year_list) - 2])` | VERIFIED FACT |
| 19 | Lead2 builder loads year_end+1 AND year_end+2 | `prisk_q_lead2.py` line 115: `year_list.extend([max(year_list) + 1, max(year_list) + 2])` | VERIFIED FACT |
| 20 | PRiskQ winsorized BEFORE merge to manifest | `winsorize_by_year` call precedes `manifest.merge(prisk_df, ...)` in all 5 builders | VERIFIED FACT |
| 21 | Presentation control dynamically added for QA DVs | `PRES_CONTROL_MAP` maps QA DVs to their Pres counterpart; `None` for Pres DVs. Verified identical in all 3 runners | VERIFIED FACT |
| 22 | Industry sample assignment: FF12=11 Finance, FF12=8 Utility, others Main | `panel_utils.py::assign_industry_sample` uses `np.select([ff12_code == 11, ff12_code == 8], ["Finance", "Utility"], default="Main")` | VERIFIED FACT |

### A2) Verified Errors in the First-Layer Audit

| # | First-layer claim | Actual code | Impact | Status |
|---|-------------------|-------------|--------|--------|
| E1 | **"21/28 lead specs significant" and "28-row analysis"** (Sections I-23, J6, K2, K5, L1, and throughout) | The lead runner produces 4 DVs x 3 samples x 2 IVs = **24** regressions maximum, not 28. The code at `CONFIG["iv_vars"] = ["PRiskQ_lead", "PRiskQ_lead2"]`, `CONFIG["dependent_variables"]` has 4 entries, `CONFIG["samples"]` has 3 entries. 4 x 3 x 2 = 24. Some Utility specs might be skipped (< 100 obs), making the actual count <= 24, never 28. | The denominator "28" is arithmetically impossible from the code. All ratios using "/28" are wrong. The actual max is 24; the realized count could be lower if Utility specs were skipped. The numerator "21" is also suspect since it was computed against a wrong denominator. | **VERIFIED ERROR** |
| E2 | **Winsorization table (Section G) claims financial controls and linguistic variables use "1%/99% by year (default)" via `_finalize_data()`** | `base.py::_finalize_data()` (line 173-174) calls `winsorize_pooled`, NOT `winsorize_by_year`. `winsorize_pooled` computes percentiles across ALL observations pooled together, not within each year. Only the PRiskQ builders explicitly call `winsorize_by_year`. | Financial controls and linguistic variables are winsorized **pooled** (all years together), not per-year as the audit claims. This is a factual mismatch between the audit's winsorization table and the actual code. The difference matters: pooled winsorization lets extreme values in low-variance years survive if they fall within the global 1%/99%. | **VERIFIED ERROR** |
| E3 | **Audit says lag runner produces "up to 24 files" of regression_results** (Section B, line 137) | Lag runner produces files named `regression_results_{sample}_{dv}_{lag1|lag2}.txt`. With 3 samples x 4 DVs x 2 lags = 24. The count is right, but the audit also later says "28-row" for the lead runner which is the same structure. Internally inconsistent. | Minor; the "up to 24" claim for lag is correct, but the "28" for lead is wrong. | **VERIFIED ERROR** (inconsistency) |

### A3) Verified Missed Issues (First-Layer Audit Gaps)

| # | Issue | Evidence | Severity | Why it matters | Status |
|---|-------|----------|----------|---------------|--------|
| M1 | **Differential sample composition across lag1/lag2 (and lead1/lead2) regressions** | The lag runner calls `prepare_regression_data(panel, dv, iv_var)` which does `dropna(subset=[dv, iv_var, ...controls...])`. Since `PRiskQ_lag` and `PRiskQ_lag2` have different missingness patterns (93.1% vs 91.7% match rates), the lag1 and lag2 regressions within the same suite operate on DIFFERENT subsamples. Same for lead1 vs lead2 (95.1% vs 94.8%). The first audit mentions match rates but never flags that the effective estimation samples differ across IV variants within the same runner. | Medium | Comparing lag1 vs lag2 (or lead1 vs lead2) coefficients is not apples-to-apples because they use different firm-quarter compositions. The lag table reports N from lag1 only (line 367-372 of lag runner), obscuring this. | **VERIFIED MISSED ISSUE** |
| M2 | **LaTeX table N mismatch in lag/lead tables** | The lag runner's LaTeX table (line 367-372) reports observations using lag-1 results only: `r_mq_1['n_obs']`. But the table also shows lag-2 coefficients. Since lag-1 and lag-2 regressions have different N (due to M1 above), the reported N does not correspond to the lag-2 row. Same issue in lead table (line 370-375). | Medium | Reader would assume the same sample underlies both coefficient rows in the table. This is misleading. | **VERIFIED MISSED ISSUE** |
| M3 | **Controls are contemporaneous (time t) while IV varies in timing** | The lag runner regresses `Uncertainty_t` on `PRiskQ_{t-1}` (or t-2) but ALL controls (Size, ROA, TobinsQ, etc.) are measured at time t (matched to the call date). This creates a temporal mismatch: the controls absorb contemporaneous variation but the IV is lagged. For the lag specification to properly test "does prior political risk predict current uncertainty," the controls should arguably also be lagged, or the analysis should acknowledge that contemporaneous controls may absorb part of the channel through which lagged PRiskQ operates. | Medium | Contemporaneous controls may be "bad controls" that absorb part of the mechanism in the lag specification. If PRiskQ_{t-1} affects Size_t, TobinsQ_t, etc., which in turn affect Uncertainty_t, then controlling for contemporaneous financials absorbs indirect effects. | **VERIFIED MISSED ISSUE** |
| M4 | **Lead runner uses one-tailed hypothesis test (H > 0) for placebo specifications** | The first audit flags this as L11 (Low severity), but understates its importance. The lead runner docstring (lines 33-37) explicitly states "H11-Lead: beta(PRiskQ_lead) > 0" and the code applies `p_one = p_two / 2 if beta_prisk > 0`. For a placebo/falsification test, the relevant null is beta = 0 (any direction). Using one-tailed H > 0 for a placebo test means: (a) p-values for positive betas are halved (making them appear more significant than they are under two-tailed), (b) negative betas get p-values near 1.0, making them automatically "pass" the placebo even if they are significantly negative. The lead LaTeX table uses one-tailed p-values for stars, which overstates significance of the positive lead coefficients. | Medium-High | This affects the interpretation of the lead "failure" documented throughout the first audit. If two-tailed p-values were used, some of the "21/N significant" lead specs might no longer be significant. Conversely, significantly negative lead betas (which the audit mentions 2 of) would become significant under two-tailed testing but are currently "hidden" by the one-tailed test. | **VERIFIED MISSED ISSUE** (first audit mentions this as Low; should be Medium-High given its interaction with the central lead-failure finding) |
| M5 | **PRiskQ and controls computed on different Compustat-matching vintages** | PRiskQ builders load the manifest and match to the Hassan CSV by (gvkey, cal_q). Financial control builders (Size, ROA, etc.) load the manifest and match to Compustat via `CompustatEngine.match_to_manifest()` using `merge_asof` on `start_date`. These are independent merge pipelines with potentially different matching logic. The PRiskQ match uses exact (gvkey, quarter) matching; Compustat controls use backward `merge_asof` on dates. A call could have PRiskQ from Q2 but Compustat data from Q1 (the most recent reporting date before the call). | Low | Minor timing inconsistency between PRiskQ (exact quarter) and financial controls (most recent Compustat report). Standard practice but worth documenting. | **VERIFIED MISSED ISSUE** |
| M6 | **No interaction terms between PRiskQ and controls** | The model specification is purely additive: `DV ~ PRiskQ + Controls + FE`. There is no PRiskQ x Size, PRiskQ x industry, or other interaction tested. This is particularly relevant given that the audit notes different behavior across Main/Finance/Utility samples, suggesting effect heterogeneity. | Low | Standard critique; the first audit does not mention this despite discussing heterogeneity across samples. | **VERIFIED MISSED ISSUE** |

### A4) Verified False Positives (Issues in First Audit That Are Less Serious Than Claimed)

| # | First-layer claim | Re-assessment | Status |
|---|-------------------|---------------|--------|
| F1 | None identified | The first audit's severity assessments are generally reasonable. The downgrade from Critical to High for the lead failure is well-justified given the attenuation evidence. | -- |

---

## B. Completeness Assessment: Is the First-Layer Audit Sufficient for Thesis-Standard Review?

### B1) Coverage Checklist

| Audit dimension | Covered? | Quality | Gaps |
|-----------------|----------|---------|------|
| Model specification accuracy | Yes | High | Correctly identifies all DVs, IVs, controls, FE structure |
| Variable construction tracing | Yes | High | Traces PRiskQ from raw CSV through all 5 builders; traces controls |
| Merge logic verification | Yes | High | Zero-row-delta, left-join, dedup all verified |
| Fixed effects structure | Yes | High | Correctly identifies year-level FE coarseness |
| Standard error clustering | Yes | Medium | Identifies firm-only clustering; misses that the effective cluster count varies across specs |
| Winsorization | Partial | **Low** | **Factual error**: claims per-year for controls/linguistic vars when code uses pooled (see E2) |
| Sample construction | Yes | High | Attrition table, min-calls filter, per-DV missingness all documented |
| Lead/lag timing arithmetic | Yes | High | All 4 quarter-shift functions verified |
| Robustness assessment | Yes | Medium | Comprehensive list of missing robustness checks |
| LaTeX table accuracy | Partial | Medium | Catches standardization claim; misses N mismatch in lag/lead tables (M2) |
| Regression count arithmetic | **No** | **Low** | Uses "28" instead of "24" for lead regressions throughout (E1) |
| Differential sample composition | **No** | N/A | Does not flag that lag1/lag2 and lead1/lead2 regressions use different subsamples (M1) |
| One-tailed test for placebo | Partial | Low | Mentions as Low severity; should be Medium-High given centrality of lead-failure finding (M4) |

### B2) Overall Completeness Verdict

The first-layer audit is **substantially complete** for a thesis-standard review. It covers model specification, variable construction, merge logic, identification threats, and robustness gaps with high quality. The two material gaps are: (1) the factual error on winsorization method for non-PRiskQ variables (E2), and (2) the wrong regression count denominator of 28 instead of 24 (E1). The missed issues (M1-M6) are real but mostly medium-severity additions rather than fundamental oversights.

---

## C. Audit-the-Audit: Craft Quality Assessment

### C1) Methodology

| Criterion | Assessment |
|-----------|------------|
| Fresh-context discipline | Good. The audit reads like it was conducted by examining the code directly, not relying on prior knowledge. |
| Evidence-based claims | High. Most claims cite specific line numbers, function names, or data outputs. |
| Separation of fact vs judgment | Good. Uses VERIFIED ISSUE, REFEREE CONCERN, etc. |
| Adversarial posture | Medium-High. Identifies the lead failure as the central issue and does not rubber-stamp it. But several missed issues suggest the adversarial stance was not exhaustive. |
| Internal consistency | **Low**. The "28" vs "24" error appears in at least 8 different locations, suggesting the number was asserted once and propagated without re-verification. |
| Arithmetic verification | **Low for this specific claim**. The "4 x 3 x 2 = 24" calculation is trivial and should have been caught. The audit even correctly states "24 regressions" in verification log #14 but then uses "28" in #23 and throughout J6/K5/L1. |
| Proportionality of severity ratings | Good overall. The High rating for the lead failure is well-calibrated. But L11 (one-tailed test for placebo) at "Low" is too lenient. |

### C2) Unsupported or Exaggerated Claims in the First-Layer Audit

| # | Claim | Assessment | Status |
|---|-------|------------|--------|
| U1 | "96.6% of (gvkey, year) cells have >1 call" (line 18, 22, 90, 373, etc.) | This specific number appears throughout and is cited as coming from verification command #22. Since I cannot re-run the command, I classify this as plausible but not independently verified. The claim that most firm-years have multiple calls is consistent with quarterly earnings calls (4 per year expected). | UNVERIFIED (plausible) |
| U2 | "PRiskQ within-firm lag-1 autocorrelation rho=0.36" (lines 389, 412-414, 461, 508-511, 538) | Cited as from verification command #25 "from red-team." This was apparently computed by a prior red-team, not by the first-layer auditor's own code. The autocorrelation of a quarterly variable within firm is plausible at 0.36 (moderate). | UNVERIFIED (plausible; sourced from prior red-team) |
| U3 | "Lead betas are approximately 1/3 of base betas (e.g., Manager_QA: 0.000135 vs 0.000043)" (lines 375, 412, 462, 508) | Cited as from "pre-4IV run" results in verification #24. These are specific beta values that depend on the exact model output. If the code has been re-run since, these values may have changed. | UNVERIFIED (dependent on specific run output) |
| U4 | "All 12 Main-sample lead coefficients are positive and significant" | This depends on the "28" denominator being wrong. If the actual count of lead regressions is 24 (or fewer if Utility specs were skipped), then "all 12 Main" is 12 out of at most 24, not 12 out of 28. The Main-sample claim itself (12 specs = 4 DVs x 1 sample x 2 IVs = 8, not 12) also needs checking. Wait: for Main sample with 2 leads x 4 DVs = 8 specs, not 12. Unless "12" includes all 3 samples... The audit says "all 12 Main-sample lead specs" but Main x 4 DVs x 2 leads = 8, not 12. | **VERIFIED ERROR**: "12 Main-sample lead specs" should be "8 Main-sample lead specs" (4 DVs x 2 lead IVs = 8). |

### C3) Correction to Lead Regression Counts

The correct arithmetic for lead regressions:
- Per-sample: 4 DVs x 2 lead IVs = 8 specs
- Main sample: 8 specs
- Finance sample: 8 specs (or fewer if skipped)
- Utility sample: 8 specs (or fewer if skipped)
- **Maximum total: 24 specs** (not 28)

The first audit's "12 Main-sample" and "28 total" counts are both wrong. The correct Main-sample count is 8. The total is at most 24.

---

## D. Variable Construction Verification

### D1) PRiskQ Builder Chain (All 5 Variants)

| Check | prisk_q.py | prisk_q_lag.py | prisk_q_lag2.py | prisk_q_lead.py | prisk_q_lead2.py |
|-------|-----------|----------------|-----------------|-----------------|------------------|
| Source file | firmquarter_2022q1.csv | Same | Same | Same | Same |
| Separator | TAB (`sep="\t"`) | Same | Same | Same | Same |
| gvkey zero-padding | `.str.zfill(6)` | Same | Same | Same | Same |
| Quarter parsing | `_parse_cal_q` (validated 1-4) | Same | Same | Same | Same |
| Year filter | `years` | `years` + min-1 | `years` + min-1, min-2 | `years` + max+1 | `years` + max+1, max+2 |
| Dedup rule | max PRisk | max PRisk | max PRisk | max PRisk | max PRisk |
| Winsorization | `winsorize_by_year` 1/99 | Same | Same | Same | Same |
| Merge key | (gvkey, cal_q) | (gvkey, cal_q_lag) | (gvkey, cal_q_lag2) | (gvkey, cal_q_lead) | (gvkey, cal_q_lead2) |
| Quarter shift fn | N/A | `_get_prev_quarter` | `_get_prev2_quarter` | `_get_next_quarter` | `_get_next2_quarter` |
| Quarter shift correct? | N/A | Yes (verified) | Yes (verified) | Yes (verified) | Yes (verified) |
| Post-merge dedup | `drop_duplicates(["file_name"])` | Same | Same | Same | Same |

All 5 builders follow an identical pattern with correct quarter arithmetic.

### D2) Winsorization Regime (Corrected)

| Variable category | Winsorization method | Thresholds | Scope | Where |
|-------------------|---------------------|-----------|-------|-------|
| PRiskQ (all 5 variants) | `winsorize_by_year` | 1%/99% | Per-year | Each PRiskQ builder, before merge |
| Financial controls (Size, ROA, TobinsQ, etc.) | `winsorize_pooled` (via `_finalize_data`) | 1%/99% | **Pooled across all years** | `base.py::_finalize_data()` -> `winsorize_pooled` |
| Linguistic variables (Uncertainty, Sentiment) | `winsorize_pooled` (via `_finalize_data`) | 1%/99% | **Pooled across all years** | `base.py::_finalize_data()` -> `winsorize_pooled` |

**CORRECTION**: The first audit claims "1%/99% by year (default)" for financial controls and linguistic variables. The actual code uses `winsorize_pooled` (global percentiles, not per-year). This is a factual error in the first audit's Section G.

---

## E. Estimation Logic Verification

### E1) Formula Construction

All 3 runners construct the formula as:
```
{dv} ~ 1 + {iv} + {controls} + EntityEffects + TimeEffects
```

The `1 +` (intercept) is included but will be absorbed by FE. The `drop_absorbed=True` parameter handles this silently. No issue.

### E2) One-Tailed P-Value Calculation

```python
p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2
```

This is the standard one-tailed conversion for H: beta > 0. Mathematically correct for the base and lag runners where the hypothesis is directional (PRiskQ increases uncertainty). **Inappropriate for the lead runner** where the test should be two-tailed (the placebo null is beta = 0 in either direction).

### E3) Hypothesis Significance Flag

```python
h_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0
```

For the lead runner, this means: a negative lead beta (which would be informative for a placebo -- reverse effect) is automatically classified as "not significant" regardless of its p-value. This asymmetric treatment biases the lead analysis toward detecting only positive failures and missing negative ones.

### E4) LaTeX Star Assignment

Stars in all tables use one-tailed p-values:
```python
fmt_coef(r['beta_prisk'], r['beta_prisk_p_one'])
```

For the lead table, stars reflect one-tailed significance, which inflates the apparent significance of positive lead coefficients by a factor of approximately 2x in p-value terms.

---

## F. Sample Construction Verification

### F1) Differential Missingness Across Sub-Suites

| Panel | Rows | PRiskQ variant | Match rate | Effective N after complete-case |
|-------|------|---------------|------------|-------------------------------|
| Base | 112,968 | PRiskQ | 97.6% | Varies by DV |
| Lag | 112,968 | PRiskQ_lag / PRiskQ_lag2 | 93.1% / 91.7% | Different for lag1 vs lag2 |
| Lead | 112,968 | PRiskQ_lead / PRiskQ_lead2 | 95.1% / 94.8% | Different for lead1 vs lead2 |

Within the lag (and lead) runner, the two IV variants produce **different estimation samples** because `dropna` requires the specific IV to be non-missing. The lag table reports N from lag1 only; the lead table reports N from lead1 only. This means the lag2 and lead2 coefficient rows in the combined tables correspond to a different (smaller) sample than the N reported.

### F2) Min-Calls Filter Sequencing

The min-calls filter is applied **per (sample, DV, IV)** combination. This means:
1. A firm with 5 calls in the lag1 sample might have only 4 in the lag2 sample (due to additional PRiskQ_lag2 missingness), causing it to be dropped from lag2 but not lag1.
2. Effective firm counts differ across specs within the same table.

The first audit correctly notes this for the base variant but does not extend the observation to the lag/lead differential.

---

## G. Identification and Inference Assessment

### G1) The Lead (Placebo) Test -- Reassessment

The first audit's central finding is that the lead tests "fail" (significant positive coefficients). Let me critically evaluate this claim and the audit's interpretation.

**What the first audit gets right:**
- The lead test is the primary identification diagnostic
- Significant positive lead coefficients undermine causal interpretation
- PRiskQ persistence (autocorrelation) is a plausible explanation
- The attenuation pattern (lead betas < base betas) is informative

**What the first audit gets wrong or overstates:**
1. **Regression count**: "21/28" should be at most "N/24" (see E1). The true significant count needs verification.
2. **"12 Main-sample" lead specs**: Should be 8 (4 DVs x 2 leads). If the first audit meant all leads across all samples, that is 24, not 12 or 28.
3. **One-tailed test inflates lead significance**: The lead runner applies one-tailed H > 0, which halves p-values for positive betas. Under two-tailed testing, some currently "significant" leads might cross the 0.05 threshold. The first audit mentions this (L11) but rates it Low and does not re-compute significance under two-tailed.
4. **Lead "failure" interpretation**: The first audit argues the ~3x attenuation suggests "persistence leakage rather than reverse causality." This is a reasonable inference but the logic is: if autocorrelation is rho=0.36, then the expected attenuation from base to lead1 is approximately rho=0.36 (not 1/3 ~ 0.33). And from base to lead2 the expected attenuation would be rho^2 = 0.13. The audit does not check whether the actual lead2 attenuation matches rho^2, which would strengthen or weaken the persistence explanation.

### G2) Year FE Coarseness

The first audit correctly identifies that year FE is too coarse for a quarterly IV. PRiskQ varies within year across quarters, but time FE only absorbs annual shocks. This is a genuine concern. Quarter-level FE or year-quarter FE would be a significant improvement and is trivially implementable (change the time index from `year` to `cal_q`).

### G3) Non-Unique Panel Index

The first audit extensively documents the non-unique (gvkey, year) index. This is a legitimate finding. PanelOLS with a non-unique MultiIndex will demean within entity (gvkey) and within time (year), treating each row (call) as a separate observation. This is functionally equivalent to a call-level regression with firm and year dummies. The within-R-squared reflects variation within (gvkey, year) cells, not within-firm variation across years. The first audit's interpretation is correct.

---

## H. Robustness and Specification Search

### H1) Multiple Testing

60 regressions with no correction is flagged by the first audit (L7). This is a standard concern. With 60 tests at alpha=0.05, the expected number of false positives under the global null is 3. The suite reports many more significant results than 3, so the finding is likely not entirely driven by multiple testing. However, the marginal significance of specific specs (e.g., Finance/Utility subsamples) could be entirely spurious.

### H2) Specification Degrees of Freedom Not Documented

The first audit does not discuss how many specifications were tried before arriving at the current setup. The 9 base controls, the 4 DVs, the 3 industry samples, and the lead/lag variants represent a large researcher degrees-of-freedom surface. No pre-registration or specification curve analysis is mentioned.

---

## I. Verified Issues Register (Second Layer)

| ID | Category | Severity | Source | Description | Evidence | Consequence | Recommended fix |
|----|----------|----------|--------|-------------|----------|-------------|-----------------|
| R1 | **Audit factual error** | High | First audit Sections I-23, J6, K2, K5, L1 | Lead regression count stated as "28" throughout; should be at most 24 (4 DVs x 3 samples x 2 IVs). "12 Main-sample" should be 8. | `CONFIG` has 4 DVs, 3 samples, 2 IVs; 4*3*2=24 | All ratios using "/28" are wrong; "21/28" significance rate is inflated numerically | Correct to actual count from model_diagnostics.csv; recompute all ratios |
| R2 | **Audit factual error** | Medium | First audit Section G, variable dictionary | Winsorization table claims controls and linguistic variables use "1%/99% by year (default)" | `base.py::_finalize_data()` line 174 calls `winsorize_pooled`, not `winsorize_by_year` | Audit misrepresents the winsorization regime; a replicator following the audit would expect per-year behavior | Correct the audit; note that PRiskQ uses per-year but others use pooled |
| R3 | **Implementation issue** | Medium | Lead runner | One-tailed test (H: beta > 0) applied to placebo specifications | `p_one = p_two / 2 if beta_prisk > 0` in lead runner; LaTeX stars use p_one | Positive lead betas appear more significant than under appropriate two-tailed test; negative lead betas (potentially informative) are automatically classified as "passing" the placebo | Use two-tailed p-values for lead specifications |
| R4 | **Missed issue** | Medium | Lag/Lead runners | Lag1 vs lag2 (and lead1 vs lead2) regressions use different estimation samples due to differential IV missingness | `prepare_regression_data` dropna requires specific IV; match rates differ (93.1% vs 91.7% for lags) | Coefficient comparisons across timing variants within the same table are not sample-comparable; reported N corresponds to variant-1 only | Report N for each IV variant separately; or use common estimation sample (intersect of both IV non-missing) |
| R5 | **Missed issue** | Medium | Lag/Lead LaTeX tables | Table N row uses variant-1 observations only, but table shows both variant-1 and variant-2 coefficients | Lag table lines 367-372 use `r_mq_1['n_obs']`; lead table lines 370-375 use `r_mq_1['n_obs']` | Reader assumes single N underlies all rows; actually variant-2 has different (smaller) N | Add separate N rows or footnote |
| R6 | **Missed issue** | Medium | Lag runner | Controls are contemporaneous (time t) while lagged PRiskQ is from time t-1 or t-2 | Controls (Size_t, ROA_t, etc.) matched via `merge_asof` to most recent Compustat report before call; PRiskQ_lag from Q-1 | Contemporaneous controls may absorb indirect effects of lagged PRiskQ, attenuating the estimated coefficient toward zero. This is a "bad controls" concern specific to the lag specification. | Discuss in thesis; consider running specs without financial controls, or with lagged controls |
| R7 | **Audit arithmetic error** | Medium | First audit throughout | "All 12 Main-sample lead coefficients are positive and significant" | Main sample has 4 DVs x 2 lead IVs = **8** lead specs, not 12 | Overstates the extent of Main-sample lead failure by 50% | Correct to 8 |
| R8 | **Implementation concern** | Low | All 5 PRiskQ builders | `_parse_cal_q` duplicated identically in all 5 files; `_load_prisk_quarterly` duplicated with minor variations (year boundary logic) | ~200 lines of near-identical code across 5 files | Bug fixes or format changes require quintuple application; risk of divergence | Refactor to shared module |

---

## J. Referee Judgment: Overall Assessment

### J1) Is the First-Layer Audit Factually Correct?

**Mostly yes, with two material errors and one pervasive arithmetic mistake.**

The factual errors are:
1. The lead regression count "28" (should be 24 max, and "12 Main" should be 8) -- this error propagates to at least 8 locations in the document.
2. The winsorization regime for controls/linguistic variables (claimed per-year, actually pooled).

Neither error changes the fundamental conclusions of the first audit (the lead failure remains a serious concern regardless of whether it is 21/24 or some other ratio), but they undermine confidence in the audit's quantitative precision.

### J2) Is the First-Layer Audit Complete Enough for Thesis-Standard Review?

**Yes, with the corrections noted above.** The audit covers model specification, variable construction, merge logic, identification threats, robustness gaps, and interpretation discipline at a level sufficient for a thesis committee. The missed issues (M1-M6) are additive improvements, not fundamental gaps.

### J3) Did the First-Layer Audit Miss Material Issues?

**Two medium-severity issues were missed:**
1. Differential sample composition across lag1/lag2 and lead1/lead2 regressions (M1/R4), with the LaTeX table reporting only variant-1 N (M2/R5).
2. The severity of the one-tailed placebo test was underrated (M4/R3). Given that the lead failure is the central finding, the fact that it is measured using an inappropriate one-tailed test directly affects the key conclusion.

### J4) Are There Unsupported or Exaggerated Claims?

**Yes:**
1. The specific counts "21/28" and "12 Main-sample" are arithmetically wrong (the code can only produce 24 lead regressions total, with 8 in the Main sample).
2. The rho=0.36 autocorrelation and specific beta values (e.g., 0.000135) are attributed to prior red-team runs and cannot be independently verified from code alone. The audit should label these as "reported from prior run output" rather than "VERIFIED."
3. The beta attenuation ratio of "~3x" is asserted without checking whether it is consistent with the reported rho=0.36 (expected attenuation for lead1 under pure persistence: rho itself, i.e., ~2.8x, which is close to 3x; for lead2: rho^2 ~ 7.7x). The consistency check would have strengthened the argument.

---

## K. Corrected Issue Severity Rankings

| Issue | First audit severity | Red-team severity | Reason for change |
|-------|---------------------|-------------------|-------------------|
| Lead placebo failure | High | High | Agree; remains the central concern |
| Year FE too coarse | High | High | Agree |
| One-tailed test for placebo | Low | **Medium-High** | Directly affects the central lead-failure finding; halves p-values for positive betas |
| Differential sample in lag/lead tables | Not identified | **Medium** | New finding; affects comparability within tables |
| LaTeX N mismatch in lag/lead tables | Not identified | **Medium** | New finding; misleading to readers |
| Winsorization audit error | Not applicable | **Medium** | Affects audit credibility, not implementation |
| "28" count error | Not applicable | **Medium** | Pervasive arithmetic error in the audit document |
| Controls contemporaneous in lag spec | Not identified | **Medium** | Bad-controls concern specific to lag specification |

---

## L. Priority Corrections for the First-Layer Audit Document

| Priority | Correction | Where in H11.md |
|----------|-----------|-----------------|
| 1 | Replace all instances of "28" (lead total) with the actual count from model_diagnostics.csv (max 24) | Sections I-23, J6, K2, K5, L1, and throughout |
| 2 | Replace "12 Main-sample" with "8 Main-sample" (4 DVs x 2 leads) | Same locations |
| 3 | Correct winsorization table: controls and linguistic variables use `winsorize_pooled` (global), not `winsorize_by_year` (per-year) | Section G |
| 4 | Upgrade L11 (one-tailed placebo test) from Low to Medium-High; add discussion of how this inflates significance of positive lead betas and hides informative negative ones | Sections K3, L |
| 5 | Add M1/M2 (differential sample composition and LaTeX N mismatch) as new issues | Sections J, L |
| 6 | Add M3 (contemporaneous controls in lag specification) as a new concern | Sections K2, J |
| 7 | Re-label rho=0.36 and specific beta values as "from prior run output" rather than VERIFIED | Sections I, K |

---

## M. Priority Fixes for the Implementation (Incremental to First Audit)

| Priority | Fix | Rationale | Effort |
|----------|-----|-----------|--------|
| 1 | **Use two-tailed p-values for lead runner** | The central diagnostic finding (lead "failure") is measured with the wrong test. Two-tailed testing is the only appropriate choice for a placebo/falsification test. | Trivial: change `p_one = p_two` in lead runner |
| 2 | **Report N for each IV variant in lag/lead tables** | Currently lag-2 and lead-2 coefficients are reported against lag-1 and lead-1 N, which is misleading | Low: add second N row or footnote |
| 3 | **Add quarter-level time FE** | Change time index from `year` to `cal_q`. Addresses both the OVB concern and partially addresses persistence. | Low: single line change in panel builder + runner |
| 4 | **Report two-tailed lead p-values alongside one-tailed base/lag p-values** | Ensures appropriate testing for each specification type | Trivial |
| 5 | **Consider common estimation sample for lag1/lag2 within same runner** | Ensures coefficient comparisons within the lag table are sample-comparable | Low: take intersection of lag1 and lag2 non-missing |

---

## N. Final Readiness Statement (Second Layer)

**Is the first-layer audit reliable enough to guide thesis revisions?**

YES, with corrections. The audit's core findings are sound: the lead placebo failure is real and serious, the year FE is too coarse, the standardization claim is false, and the non-unique panel index needs documentation. The arithmetic errors ("28" instead of 24, "12 Main" instead of 8) and the winsorization mislabeling are embarrassing but do not change the substantive conclusions. The missed issues (differential samples within lag/lead tables, severity of one-tailed placebo test) are additive improvements.

**What should the thesis author prioritize?**

1. Fix the lead runner to use two-tailed tests (this may change the "failure" rate and thus the severity of the finding).
2. Implement quarter-level time FE (single highest-value technical fix).
3. Report standardized effect sizes (the beta magnitudes are uninterpretable as-is).
4. Prominently discuss the lead results with appropriate nuance (persistence vs reverse causality).

**Is the suite salvageable?**

YES, for descriptive inference. The association between PRiskQ and speech uncertainty is robust across specifications. Causal claims require quarter FE, persistence controls (first-differenced PRiskQ or lagged DV), and a properly-tested (two-tailed) lead placebo.

---

## O. Audit Metadata

| Field | Value |
|-------|-------|
| Files read | 16 source files (3 runners, 3 panel builders, 5 PRiskQ builders, panel_utils.py, winsorization.py, lev.py, base.py, first-layer audit) |
| Lines of code reviewed | ~3,500 |
| Verified facts | 22 |
| Verified errors in first audit | 3 (E1: count "28"->24, E2: winsorization method, E3: count inconsistency) |
| Verified missed issues | 6 (M1-M6) |
| Verified false positives | 0 |
| Unverified concerns | 3 (U1: 96.6% non-unique, U2: rho=0.36, U3: specific beta values) |
| New implementation issues | 5 (R3-R7 beyond what first audit found) |

---

## P. Revision History

| Date | Description |
|------|-------------|
| 2026-03-18 | Second-layer red-team audit. Key findings: (1) Lead regression count "28" is wrong -- max is 24; "12 Main" should be 8. (2) Winsorization for controls/linguistic vars is pooled, not per-year as first audit claims. (3) One-tailed test for placebo should be upgraded from Low to Medium-High severity. (4) Differential sample composition within lag/lead tables is a new medium-severity issue. (5) First audit is substantially correct in its core findings despite these errors. |
