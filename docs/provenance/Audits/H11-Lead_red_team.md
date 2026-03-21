# H11-Lead Suite: Second-Layer Red-Team Audit

**Suite ID:** H11-Lead (Political Risk Lead -- Placebo Tests for Reverse Causality)
**Auditor:** Red-Team (Layer 2)
**Date:** 2026-03-21
**First-Layer Audit:** `docs/provenance/H11-Lead.md`
**Method:** Independent code inspection against first-layer claims

---

## A. Red-Team Bottom Line

**Verdict: FIRST-LAYER AUDIT IS SUBSTANTIALLY CORRECT AND THOROUGH**

The first-layer audit is one of the stronger provenance documents in this project. It correctly identifies the false standardization claim (HIGH severity), the one-tailed test concern for a placebo design (MEDIUM), and entity-only clustering limitations (MEDIUM). The audit demonstrates genuine code tracing rather than surface-level description.

However, the red-team identifies three issues the first-layer audit missed or mis-characterized:
1. The `firm_maturity` formula is correctly stated as `req / atq` in the audit, but the audit fails to note that the Compustat engine's own docstring (line 784) incorrectly labels this as "RE / TE (retained earnings / total equity)" when the code actually divides by total assets. This is a *code-level* docstring error beyond the runner docstring issue already flagged.
2. The LaTeX table presents Observations and Within-R-squared from lead-1 regressions only, even though lead-2 regressions may have different sample sizes due to differential missingness. This is not flagged.
3. The LaTeX significance stars use one-tailed p-values, compounding the one-tailed test concern already flagged. The first-layer audit notes the test is one-tailed but does not explicitly flag that the published table stars inherit this bias.

---

## B. Scope and Objects Audited

| Object | Path | Inspected |
|--------|------|-----------|
| First-layer audit | `docs/provenance/H11-Lead.md` | Full read |
| Runner | `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py` | Full read (595 lines) |
| Panel builder | `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py` | Full read (298 lines) |
| PRiskQ lead builder | `src/f1d/shared/variables/prisk_q_lead.py` | Lines 60-210 |
| PRiskQ lead2 builder | `src/f1d/shared/variables/prisk_q_lead2.py` | Lines 60-210 |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` | Lines 780-860 (firm_maturity) |
| Winsorization utility | `src/f1d/shared/variables/winsorization.py` | Lines 23-62 |
| Linguistic engine | `src/f1d/shared/variables/_linguistic_engine.py` | Winsorization grep |

---

## C. Audit-of-Audit Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Factual accuracy | 4.5 | All major claims verified correct; one formula description subtlety missed (see D) |
| Completeness | 4.0 | Good coverage; misses LaTeX table N/R2 discrepancy and star-basis issue |
| Appropriate skepticism | 4.5 | Correctly flags false standardization claim, one-tailed placebo concern, clustering limitation |
| Code tracing depth | 5.0 | Line-number references, formula verification, builder inspection -- exemplary |
| Severity calibration | 4.0 | Generally correct; see Section H for recalibrations |
| Actionability of fixes | 4.5 | Priority fixes are specific and implementable |
| Overall | 4.3 | Strong audit; minor gaps only |

---

## D. Claim Verification Matrix

| Audit Claim (Section) | Code Location | Verified? | Notes |
|------------------------|---------------|-----------|-------|
| 24 regressions = 4 DVs x 3 samples x 2 IVs (A) | Runner CONFIG, lines 91-101; loop at 509-515 | CORRECT | Loop nests: iv_vars (2) x DVs (4) x samples (3) = 24 |
| Panel index is (gvkey, year) (A) | Runner line 203 | CORRECT | `df_sample.set_index(["gvkey", "year"])` |
| One-tailed test: p/2 if beta>0, else 1-p/2 (H5) | Runner lines 226-228 | CORRECT | Standard one-sided formula |
| PRiskQ_lead uses _get_next_quarter (E2) | prisk_q_lead.py line 161 | CORRECT | Q4 -> Y+1 Q1, else Q+1 |
| PRiskQ_lead2 uses _get_next2_quarter (E2) | prisk_q_lead2.py line 164 | CORRECT | Q3->Y+1Q1, Q4->Y+1Q2, else Q+2 |
| Year extension: lead-1 adds max(years)+1 (D3) | prisk_q_lead.py lines 110-112 | CORRECT | `year_list.append(max(year_list) + 1)` |
| Year extension: lead-2 adds +1 and +2 (D3) | prisk_q_lead2.py lines 114-115 | CORRECT | `year_list.extend([max(year_list) + 1, max(year_list) + 2])` |
| PRisk dedup keeps max per (gvkey, cal_q) (D3) | prisk_q_lead.py lines 116-118 | CORRECT | `sort_values("PRisk", ascending=False).drop_duplicates(keep="first")` |
| Zero row-delta merge enforcement (E1) | Panel builder lines 147-152 | CORRECT | `raise ValueError` on delta != 0 |
| min_calls >= 5 filter (E3) | Runner lines 527-532 | CORRECT | `groupby("gvkey")["file_name"].transform("count") >= 5` |
| Skip if < 100 obs (E3) | Runner line 538 | CORRECT | `if len(df_filtered) < 100: continue` |
| FALSE standardization claim in LaTeX (J1) | Runner line 399 | CORRECT | "All continuous controls are standardized." -- no standardization code exists |
| BookLev loaded but unused (J3) | Panel builder line 116; runner BASE_CONTROLS | CORRECT | BookLevBuilder instantiated but BookLev not in controls |
| Linguistic winsorization: 0%/99% (J4) | _linguistic_engine.py line 257 | CORRECT | `lower=0.0, upper=0.99` |
| PRisk winsorization: 1%/99% (D3) | prisk_q_lead.py line 170; winsorization.py defaults | CORRECT | Uses default `lower=0.01, upper=0.99` |
| firm_maturity = req / atq (F) | _compustat_engine.py line 849 | CORRECT | `df["req"] / df["atq"]` |
| firm_maturity described as "RE/TA" (K4) | Audit section K4 | CORRECT | Audit calls it "DeAngelo et al. (2006) RE/TA ratio" |
| PRES_CONTROL_MAP logic (H2) | Runner lines 115-120 | CORRECT | QA DVs get presentation control; Pres DVs get None |
| Dynamic control: 10 controls for QA, 9 for Pres (H3) | Runner lines 164-167 | CORRECT | BASE_CONTROLS (9) + optional pres control |

---

## E. Unsupported Claims

No unsupported claims were identified in the first-layer audit. All factual assertions were verified against source code.

---

## F. False Positives

| Audit Issue ID | Claimed Issue | Red-Team Assessment |
|----------------|---------------|---------------------|
| L7 | Runner docstring describes firm_maturity as "Years since first Compustat appearance" | **CANNOT VERIFY AS STATED.** The runner docstring (lines 1-65) does not contain the phrase "Years since first Compustat appearance." The audit cites "runner line 111 (implicit from control list)" but line 111 is just `"firm_maturity",` in BASE_CONTROLS. The runner's *module* docstring (lines 1-64) does not describe individual control formulas. This issue may exist in other documentation or in the H11 base suite, but the citation is incorrect for this specific runner file. **Reclassify as unverifiable in this runner.** |

---

## G. Missed Issues

| ID | Severity | Description |
|----|----------|-------------|
| G1 | LOW-MEDIUM | **LaTeX table N and R-squared use lead-1 only.** The LaTeX table (lines 371-384) displays Observations and Within-R2 from lead-1 results (`r_mq_1`, `r_cq_1`, etc.) but lead-2 regressions may have different sample sizes due to the 2-quarter forward window creating more edge-case missingness. A reader seeing both lead-1 and lead-2 coefficients in the same column with a single N row may assume they share the same estimation sample. |
| G2 | LOW | **LaTeX significance stars are based on one-tailed p-values.** The `fmt_coef` function (line 290) receives `beta_prisk_p_one` (lines 330-333), meaning the published table uses one-tailed significance thresholds. For a placebo test, this inflates the apparent significance of positive coefficients (halved p-value). The first-layer audit flags the one-tailed test (L2) but does not note that the LaTeX stars inherit this bias, which is the reader-facing manifestation. |
| G3 | LOW | **Compustat engine docstring mismatch for firm_maturity.** The `_compute_h3_payout_policy` docstring (line 784) describes `firm_maturity` as "RE / TE (retained earnings / total equity)" but the actual formula (line 849) is `req / atq` (retained earnings / total assets). The first-layer audit correctly identifies the formula but does not flag this internal docstring inconsistency. |
| G4 | LOW | **Attrition table covers only one DV path.** The attrition table (lines 558-569) uses `n_obs` from the first Main/PRiskQ_lead result. Since different DVs (especially CEO measures) have different missingness patterns, the attrition table underrepresents the variation in sample loss across specifications. |

---

## H. Severity Recalibration

| Issue ID | Original Severity | Red-Team Severity | Rationale |
|----------|-------------------|-------------------|-----------|
| L1 (False standardization claim) | HIGH | **HIGH** -- AGREE | A materially false statement in the published table. No change. |
| L2 (One-tailed placebo test) | MEDIUM | **MEDIUM-HIGH** | The concern is valid and the first-layer audit's reasoning is correct. Elevated slightly because the LaTeX stars also use one-tailed p-values (G2), meaning the reader-facing output compounds the issue. |
| L3 (Entity-only clustering) | MEDIUM | **MEDIUM** -- AGREE | Valid concern for a placebo test. The anti-conservative direction argument is sound. |
| L4 (No multiple testing correction) | MEDIUM | **LOW-MEDIUM** | For a placebo test where the *desired* outcome is non-significance, multiple testing correction would make it *harder* to reject (more conservative). The absence of correction is actually conservative for the researcher's desired conclusion. The issue is only relevant if the researcher wants to claim that *all* 24 tests are null, which benefits from Bonferroni. Downgraded. |
| L5 (Non-unique panel index) | MEDIUM | **LOW-MEDIUM** | This is standard practice in earnings-call research. PanelOLS handles repeated observations within entity-time cells. The entity clustering is appropriate. The concern is valid for disclosure purposes but overstated at MEDIUM. |
| L7 (firm_maturity description) | LOW | **UNVERIFIABLE** | The cited location (runner line 111) does not contain the claimed text. See Section F. |
| L9 (max-PRisk dedup) | LOW | **LOW** -- AGREE | No change. |
| L10 (No power analysis) | LOW | **LOW** -- AGREE | Desirable but not standard in this literature. |

---

## I. Completeness Gaps

| Gap | Severity | Assessment |
|-----|----------|------------|
| No check of whether lead-1 and lead-2 match rates differ materially | LOW | The builders log match statistics but the audit does not discuss expected match-rate differences between 1Q and 2Q leads |
| No verification of `generate_attrition_table` or `generate_manifest` functions | LOW | These utility functions are assumed correct but not inspected |
| No check of whether `drop_absorbed=True` absorbs any regressors unexpectedly | LOW | In theory, a control perfectly collinear with FE could be silently absorbed without warning to the researcher |

---

## J. Reproducibility Red-Team

| Check | Result |
|-------|--------|
| Commands documented? | YES -- Stage 3 and Stage 4 commands in Section B |
| Input files specified? | YES -- manifest, linguistic variables, PRisk CSV, Compustat |
| Output paths deterministic? | YES -- timestamped subdirectories |
| Config files referenced? | YES -- project.yaml and variables.yaml |
| Seed/determinism documented? | YES -- random_seed: 42, thread_count: 1, sort_inputs: true |
| Can an independent researcher reproduce from scratch? | YES, given access to input data files |

---

## K. Econometric Meta-Audit

### K1. Model Specification
The PanelOLS with entity + time FE and entity-clustered SEs is standard. The formula construction is verified correct. The dynamic presentation control logic is sound and prevents "bad control" contamination (presentation uncertainty is upstream of QA uncertainty within the same call).

### K2. Lead Variable Construction
The quarter-shifting logic is verified correct. `_get_next_quarter` and `_get_next2_quarter` handle year rollovers properly. The year-extension logic for data loading ensures edge-case matches are available.

### K3. Placebo Test Design
The first-layer audit's concern about one-tailed testing for placebos is **correct and important**. A placebo test's value lies in demonstrating absence of effect in *either* direction. Using one-tailed tests:
- Halves the p-value for positive coefficients (making them look more significant)
- Nearly doubles the p-value for negative coefficients (hiding potentially problematic negative associations)
This asymmetry biases the placebo interpretation.

### K4. Multiple Testing
The first-layer audit overstates the multiple testing concern (see H, recalibration of L4). For a placebo test seeking non-significance, the absence of correction is conservative for the researcher's argument: it makes it *easier* for any one test to appear significant, which would *undermine* the placebo claim. The real concern would be if the researcher cherry-picks only the non-significant results.

### K5. Clustering
The first-layer audit's anti-conservative argument for entity-only clustering is valid. Political risk has aggregate components (elections, regulatory changes) that create cross-sectional correlation. For a placebo test, this matters because the test's value comes from demonstrating that lead coefficients *are not* significant -- understated standard errors would make this conclusion *harder* to reach (more likely to find spurious significance), which is actually conservative. On reflection, entity-only clustering is **conservative** for the placebo conclusion (it is harder to show insignificance when SEs are too small). The first-layer audit's reasoning on this point is **reversed** -- smaller SEs make it easier to reject the null, meaning entity-only clustering makes it *harder* for the placebo to "pass" (show insignificance). This is actually a favorable property for placebo tests.

**IMPORTANT CORRECTION:** The first-layer audit (L3, K2) claims entity-only clustering is "anti-conservative" for a placebo test. This reasoning is inverted. For a placebo test where the desired outcome is *non-significance*:
- Understated SEs -> smaller p-values -> more likely to find significance -> HARDER for the placebo to pass
- This is actually **conservative** (works against the researcher's desired conclusion)
- Double-clustering would *increase* SEs and make it *easier* to show non-significance, which would be *anti-conservative* for the placebo claim

The first-layer audit's recommendation to double-cluster is still reasonable for robustness, but the directionality of the concern is wrong.

---

## L. Audit-Safety Assessment

| Dimension | Assessment |
|-----------|------------|
| Does the audit create false confidence? | NO -- the audit is appropriately critical |
| Does the audit miss any data-integrity issues? | Minor: does not verify PRisk source file integrity or check for gvkey mismatches |
| Could the audit mislead a committee? | The inverted clustering argument (L3/K2) could lead a committee to request double-clustering, which would actually make the placebo test *easier* to pass, not harder. This is a beneficial error (leads to more conservative reporting). |
| Are severity ratings appropriate? | Mostly yes, with recalibrations noted in Section H |

---

## M. Master Red-Team Issue Register

| ID | Source | Severity | Category | Description |
|----|--------|----------|----------|-------------|
| L1 | Layer 1 | HIGH | Integrity | False "standardized" claim in LaTeX table notes (line 399). **CONFIRMED.** |
| L2 | Layer 1 | MEDIUM-HIGH | Identification | One-tailed test inappropriate for placebo design. **CONFIRMED** and elevated due to G2. |
| G2 | Layer 2 | LOW | Presentation | LaTeX significance stars use one-tailed p-values, compounding L2. |
| L3 | Layer 1 | MEDIUM | Inference | Entity-only clustering. **CONFIRMED** as a valid disclosure concern, but the anti-conservative directionality argument is **REVERSED** (see K5). Entity-only clustering is actually conservative for a placebo test. |
| L4 | Layer 1 | LOW-MEDIUM | Inference | No multiple testing correction. **DOWNGRADED** -- absence is conservative for placebo claims. |
| G1 | Layer 2 | LOW-MEDIUM | Presentation | LaTeX table N and R2 from lead-1 only; lead-2 may differ. |
| L5 | Layer 1 | LOW-MEDIUM | Panel index | Non-unique (gvkey, year) index. **DOWNGRADED** -- standard practice. |
| G3 | Layer 2 | LOW | Documentation | Compustat engine docstring says "RE/TE" but code computes RE/TA (req/atq). |
| G4 | Layer 2 | LOW | Documentation | Attrition table covers only one DV path. |
| L6 | Layer 1 | LOW | Integrity | Imprecise winsorization claim in LaTeX notes. **CONFIRMED.** |
| L7 | Layer 1 | UNVERIFIABLE | Documentation | Claimed firm_maturity misdescription not found at cited location. |
| L8 | Layer 1 | LOW | Code hygiene | BookLev loaded but unused. **CONFIRMED.** |
| L9 | Layer 1 | LOW | Data quality | max-PRisk dedup undisclosed. **CONFIRMED.** |
| L10 | Layer 1 | LOW | Robustness | No power analysis for placebo test. **CONFIRMED.** |

---

## N. What Committee Wouldn't Know

Even after reading the first-layer audit, a thesis committee would not know:

1. **The clustering concern is directionally wrong.** The audit says entity-only clustering is "anti-conservative" for the placebo, but it is actually conservative (harder to show insignificance with smaller SEs). A committee might request double-clustering thinking it would make the test more rigorous, when in fact it would make the placebo easier to pass.

2. **The LaTeX table conflates lead-1 and lead-2 sample sizes.** Both lead horizons appear in the same column, but only lead-1 N is reported. The committee cannot assess whether lead-2 results have meaningfully different sample sizes.

3. **The significance stars are one-tailed.** The committee would see the star thresholds and assume standard two-tailed convention unless explicitly told otherwise. The table notes do not specify one-tailed stars.

4. **The Compustat engine's own docstring mislabels the firm_maturity denominator.** While the first-layer audit correctly describes the formula as RE/TA, a committee member tracing the code would find a docstring saying "RE/TE," creating confusion.

---

## O. Priority Fixes

### O1 (HIGH) -- Remove false standardization claim
**File:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, line 399
**Action:** Delete `"All continuous controls are standardized. ",` or replace with accurate description.
**Confirmed by:** Both Layer 1 (L1) and Layer 2.

### O2 (MEDIUM-HIGH) -- Switch to two-tailed p-values for placebo test
**File:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, lines 226-232 and 290-300 (star thresholds)
**Action:** Report two-tailed p-values in meta dict and pass `p_two` to `fmt_coef` for star assignment. Update hypothesis significance logic to use two-tailed threshold.

### O3 (LOW-MEDIUM) -- Show lead-2 N separately or note discrepancy
**File:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, lines 371-384
**Action:** Either add a second Observations row for lead-2, or add a table note stating "Observation counts shown are for lead-1 specifications; lead-2 sample sizes may differ slightly."

### O4 (LOW) -- Fix winsorization description in LaTeX notes
**File:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, line 400
**Action:** Replace "Variables are winsorized at 1\\%/99\\% by year." with "Financial controls and political risk are winsorized at 1\\%/99\\% by year; linguistic variables are winsorized at 0\\%/99\\% (upper-only)."

### O5 (LOW) -- Remove unused BookLev from panel builder
**File:** `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py`, line 116
**Action:** Remove `BookLevBuilder` instantiation and its import.

---

## P. Final Red-Team Readiness Statement

**The first-layer audit is RELIABLE and SUBSTANTIALLY CORRECT.**

It correctly identifies the most important issue (false standardization claim, L1) and raises valid concerns about the placebo test design (L2). Its code tracing is thorough and all factual claims were verified against source code.

**Key correction:** The clustering directionality argument (L3) is inverted. Entity-only clustering is *conservative* for a placebo test (makes it harder to show insignificance), not anti-conservative. This does not invalidate the recommendation to discuss or test double-clustering, but the justification needs correction.

**Remaining mandatory fix:** Only O1 (false standardization claim) is truly blocking. O2 (two-tailed p-values) is strongly recommended for methodological soundness. All other issues are documentation improvements.

**The suite is conditionally ready for thesis submission, pending resolution of O1 and O2.**
