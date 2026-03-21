# H5 Analyst Dispersion -- Second-Layer Red-Team Audit

**Generated:** 2026-03-21
**Auditor role:** Hostile-but-fair replication auditor (second layer)
**Suite ID:** H5
**First-layer doc:** `docs/provenance/H5.md` (dated 2026-03-18)
**Runner:** `src/f1d/econometric/run_h5_dispersion.py`
**Panel builder:** `src/f1d/variables/build_h5_dispersion_panel.py`

---

## A. First-Layer Audit Completeness

The first-layer audit (H5.md) is **unusually thorough** -- 714 lines covering 14 sections with a full variable dictionary, dependency chain, verification log, identification critique, and known-limitations register. It addresses its own prior red-team findings in Section 13. Coverage is comprehensive for a provenance document.

**Missing or thin areas:**

1. The audit does not document the `ACTUAL` column from IBES Detail -- it is mentioned in Section 4.1 raw columns but never traced into the dispersion computation. `ACTUAL` is not used in the dispersion formula itself (only `VALUE` enters std/mean), so this is cosmetic rather than functional.
2. No discussion of whether the `merge_asof` direction="forward" for FPEDATS matching (postcall_dispersion.py line 169) could systematically exclude calls near fiscal-year boundaries.
3. The audit does not note that the `_compute_dispersions` method invokes `_dispersion_bulk` twice (once for pre-call, once for post-call) but the exact dispatch is not traced in the dependency chain.

**Verdict:** ADEQUATE. The audit covers all material code paths and is well above the typical provenance document standard.

---

## B. Factual Accuracy of First-Layer Claims

Each claim below was independently verified against source code.

| # | Claim in H5.md | Verified? | Evidence | Notes |
|---|----------------|-----------|----------|-------|
| B1 | DV = SD/\|Mean\| x 100 | YES | `postcall_dispersion.py` lines 270-274 | Correct |
| B2 | Post-call timing = +3 trading days | YES | line 56: `self.days_after = 3` | Correct |
| B3 | Pre-call timing = -1 trading day | YES | line 55: `self.days_before = 1` | Correct |
| B4 | USFederalHolidayCalendar used | YES | line 61 | Correct |
| B5 | FPEDATS 120-day tolerance | YES | line 58, 169 | Correct |
| B6 | Stale estimate filter = 180 days | YES | line 57 config default, line 245 | Correct |
| B7 | NUMEST_MIN = 2 | YES | line 51, lines 259-260 | Correct |
| B8 | 4 simultaneous IVs | YES | runner lines 83-87 | Correct |
| B9 | 8 base controls | YES | runner lines 91-100 | Correct |
| B10 | 4 extended additions | YES | runner lines 102-107 | Correct |
| B11 | FF12 exclusions [8, 11] | YES | runner line 212 | Correct |
| B12 | MIN_CALLS_PER_FIRM = 5 | YES | runner line 116 | Correct |
| B13 | One-tailed formula | YES | runner line 340 | Correct |
| B14 | Firm-clustered SEs | YES | runner lines 307, 312 | Correct |
| B15 | Industry FE via other_effects | YES | runner lines 298-303 | Correct |
| B16 | Firm FE via EntityEffects formula | YES | runner lines 309-311 | Correct |
| B17 | drop_absorbed=True both specs | YES | runner lines 304, 311 | Correct |
| B18 | check_rank=False in industry spec | YES | runner line 305 | Correct |
| B19 | DV winsorization 1%/99% pooled | YES | postcall_dispersion.py lines 91-96 | Correct |
| B20 | Compustat per-year 1%/99% | YES | _compustat_engine.py lines 1212-1215 | Correct |
| B21 | Linguistic per-year 0%/99% upper-only | YES | _linguistic_engine.py lines 255-258 | Correct |
| B22 | FPI=['6','7'] loaded by engine | YES | _ibes_detail_engine.py line 64 | Correct |
| B23 | Zero-row-delta merge enforcement | YES | build_h5_dispersion_panel.py lines 154-159 | Correct |
| B24 | file_name uniqueness assertion | YES | build_h5_dispersion_panel.py lines 139-141 | Correct |
| B25 | fyearq_int = floor(to_numeric(fyearq)).astype(Int64) | YES | build_h5_dispersion_panel.py lines 171-173 | Correct |
| B26 | BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq | YES | _compustat_engine.py line 1041 | Correct |
| B27 | Size = ln(atq) for atq > 0 | YES | _compustat_engine.py line 1036 | Correct |
| B28 | DividendPayer not winsorized (in skip set) | YES | _compustat_engine.py line 1200 | Correct |
| B29 | std() uses ddof=1 (pandas default) | YES | postcall_dispersion.py line 266: `.agg(["std", "mean"])` | Correct |
| B30 | Panel index set_index(["gvkey", "fyearq_int"]) | YES | runner line 291 | Correct |

**Line number accuracy:** Several line numbers in the audit are approximate (off by a few lines), which is normal given code evolution. No line reference pointed to an entirely wrong location. The references to `_compustat_engine.py` line 1186 for skip_winsorize (Section 6.4.6) should be line 1199. The reference to "lines 1151-1172" for inf replacement (Section 6.4.4) should be lines 1164-1186. These are minor documentation imprecisions, not factual errors.

**Verdict:** All factual claims are **CORRECT**. No fabricated or misleading assertions found.

---

## C. Accuracy of Known Limitations (L-1 through L-7)

| ID | Limitation | Accurate? | Assessment |
|----|-----------|-----------|------------|
| L-1 | FPI documented as '6' but engine loads ['6','7'] | YES | Independently confirmed: docstring line 15, metadata line 109 both say FPI='6'. Engine line 64 loads ['6','7']. The audit correctly identifies this as a documentation error. |
| L-2 | Duplicate multi-index | YES | Correct analysis. Multiple calls per firm-year create non-unique (gvkey, fyearq_int) pairs. The audit's analysis of implications for entity vs. time demeaning is sound. |
| L-3 | check_rank=False | YES | Correctly identified and correctly assessed as mitigated by drop_absorbed=True. |
| L-4 | std() ddof=1 with min 2 analysts | YES | Correctly identified. Note: with exactly 2 analysts, std(ddof=1) = \|x1-x2\|/sqrt(2), which is a valid but potentially noisy measure. |
| L-5 | Linguistic IV winsorization unclear | PARTIALLY OUTDATED | The audit says "Winsorization status depends on Stage 2 upstream processing" but then in Section 6.7 correctly documents that linguistic variables are winsorized at 0%/99% per-year by the LinguisticEngine. The L-5 text and the Section 6.7 table contradict each other. Section 6.7 is correct. |
| L-6 | CCM linking first-duplicate | YES | Correctly identified as minor and standard practice. |
| L-7 | No execution evidence | YES | Correctly flagged. No run output is referenced. |

**Verdict:** Limitations are accurately identified and appropriately severity-rated. L-5 has an internal inconsistency (body text vs. summary table) but the table is correct.

---

## D. Issues the First-Layer Audit Missed

### D-1. Summary Statistics Computed on Pre-Filtering Sample (MINOR -- reporting)

**Finding:** `make_summary_stats_table` at runner lines 675-681 is called on `panel` AFTER `filter_main_sample` but BEFORE any regression-specific filtering (complete cases, min calls). The summary statistics therefore describe the main-sample universe, not the regression estimation sample. This is standard practice but could mislead if a reader assumes summary stats match the regression N.

**Impact:** Summary stats N will exceed regression N. Not a bug, but should be disclosed.

### D-2. Attrition Table Records PostCallDispersion Non-Null from Main Sample, Not Estimation Sample (MINOR -- reporting)

**Finding:** At runner line 715, `panel["PostCallDispersion"].notna().sum()` uses the main-sample-filtered `panel` variable, which has not yet been filtered for complete cases. The attrition table stage 3 ("PostCallDispersion non-null") thus reports the count of calls with a valid DV in the main sample before control-variable filtering. This is correct for an attrition table but could be confusing if the step 4 count drops substantially due to missing controls.

**Impact:** Cosmetic. The attrition table correctly shows progressive filtering.

### D-3. LaTeX Table Note Still Says "Variables winsorized at 1%/99%" (MINOR -- documentation)

**Finding:** Runner line 488 contains `r"Variables winsorized at 1\%/99\%. "`. The first-layer audit identifies this as L-5 and documents the correct per-variable-group winsorization chain in Section 6.7. However, the code itself has NOT been corrected -- the LaTeX table note remains a blanket (and inaccurate) statement. Linguistic variables are winsorized at 0%/99% (upper-only), not 1%/99%. Binary and ordinal variables are not winsorized at all. DV dispersion variables are winsorized pooled, not per-year.

**Status:** The audit acknowledges this in L-5 but marks it as a documentation issue without flagging that the LaTeX output going into the thesis will carry this inaccuracy to the reader.

### D-4. No Constant/Intercept in Industry FE Specification (MINOR -- econometric)

**Finding:** In the industry FE specification (runner lines 298-306), `PanelOLS` is called with constructor arguments (not `from_formula`). The `exog` DataFrame does not include a constant column, and there is no `add_constant`. PanelOLS with `entity_effects=False` and `time_effects=True` plus `other_effects` will absorb the overall mean through the fixed effects, so no separate intercept is needed. However, the firm FE formula (line 310) includes `~ 1 + ...` (explicit intercept), which PanelOLS will absorb into the entity effects. The asymmetry is benign but the first-layer audit does not discuss it.

**Impact:** None on coefficients. PanelOLS handles this correctly in both cases.

### D-5. `year` Column Loaded but Not Used in Runner (COSMETIC)

**Finding:** The runner loads `"year"` at line 188 but never uses it in any regression, filter, or output beyond being present in the DataFrame. This is dead weight in the column selection.

**Impact:** None.

---

## E. Identification Critique Assessment

The first-layer audit's Section 11 provides a substantive identification critique covering reverse causality, simultaneity, and omitted variable bias. The critique is honest about what the design cannot establish (causal identification). The mitigations listed (PreCallDispersion control, extended controls, firm FE) are accurately described.

**Missing from the identification discussion:**

1. **Selection on observables vs. unobservables:** The audit does not discuss whether the control set is sufficient to proxy for the information environment. Specifically, no measure of earnings quality, guidance issuance, or call complexity is included beyond loss_dummy and SurpDec.

2. **Mechanical correlation risk:** If analyst forecast dispersion and managerial speech uncertainty are both driven by the same firm-quarter earnings realization, the coefficient may be capturing a mechanical relationship rather than an information channel. The pre-call dispersion control partially addresses this, but the audit could be more explicit.

3. **Post-treatment bias:** The extended controls include `Analyst_QA_Uncertainty_pct` and `Entire_All_Negative_pct`, which are measured during the same earnings call. If uncertainty language causally influences analyst questions (and vice versa), these controls are post-treatment and could attenuate the IV coefficients. The audit does not flag this.

**Verdict:** The identification section is **good for a provenance document** but has room for deeper scrutiny on post-treatment controls.

---

## F. Econometric Specification Assessment

| Check | Status | Notes |
|-------|--------|-------|
| Correct use of PanelOLS | PASS | Both constructor and formula approaches are valid |
| Clustering level appropriate | PASS | Firm-level clustering for call-level data is standard |
| Fixed effects correctly specified | PASS | Industry FE via other_effects, Firm FE via EntityEffects |
| One-tailed test correctly implemented | PASS | `p_two / 2 if beta > 0 else 1 - p_two / 2` is the correct directional formula |
| No look-ahead bias in controls | PASS | All controls use backward merge_asof from call date |
| DV timing appropriate | PASS | +3 trading days post-call allows information absorption |

**Potential concern:** The 4 IVs (CEO/Manager x QA/Pres uncertainty) are likely highly correlated with each other, as noted in the audit. With all 4 entering simultaneously, multicollinearity could inflate standard errors substantially, making individual IV significance tests uninformative. The audit notes this but does not recommend VIF diagnostics or sequential inclusion tests. This is an important methodological gap.

---

## G. Variable Construction Verification

All 20 variables used in the regression (1 DV + 4 IVs + 8 base controls + 4 extended controls + 3 index/FE variables) were traced through the code. Construction formulas match the audit's documentation. No discrepancies found.

**One observation:** The `ROA` formula uses `iby` (Income Before Extraordinary Items), not `ibq`. The audit references `ibq` at line 1059 for the NaN condition but the actual variable used is `iby` (annual, from Q4 extraction). The audit's Section 6.4.3 correctly describes the Q4 extraction chain. This is consistent.

---

## H. Data Flow Integrity

The end-to-end dependency chain (Section 3) is accurate. I verified:

1. ManifestFieldsBuilder produces file_name, gvkey, start_date, ff12_code.
2. All builders merge on file_name with zero-row-delta enforcement.
3. fyearq attachment uses backward merge_asof via CompustatEngine.
4. Runner loads 20 columns (verified at lines 187-200 -- actually loads year too, so 21 columns total, though the audit says 20 "excludes file_name" which is technically inaccurate since `year` is also loaded but not counted).

**Column count discrepancy:** The audit Section 3 says "Loads panel columns (20 columns, excludes file_name)." The actual column list at runner lines 187-200 has 20 items including `year` but excluding `file_name`. Since `year` is not used in any regression, this is accurate but the parenthetical could be clearer.

---

## I. Output Inventory Verification

The output file list in Section 8 matches the code. All 8 files listed for the runner are produced by the save_outputs function, generate_report function, and generate_attrition_table/generate_manifest calls. The panel builder output list is also correct.

One addition: the runner also produces `sample_attrition.tex` (line 719 mentions both csv and tex), which is not listed in the Section 8 table. This is a cosmetic omission.

---

## J. Reproducibility Assessment

The reproduction commands in Section 2 are correct and sufficient. The required inputs table is accurate. One gap: the `config/project.yaml` and `config/variables.yaml` files are listed but their contents are not version-pinned or documented. Changes to these configs could change the year range, winsorization thresholds, or other parameters, breaking reproducibility.

---

## K. Internal Consistency Check

| Cross-reference | Consistent? | Notes |
|-----------------|-------------|-------|
| Section 1 "4 specs" vs. Section 7 table | YES | 4 specs, 2 FE x 2 controls |
| Section 1 "8 base controls" vs. Section 6.4 | YES | 8 controls listed |
| Section 6.7 winsorization table vs. code | YES | All entries verified |
| L-5 body text vs. Section 6.7 table | NO | L-5 says "depends on Stage 2 upstream processing" but Section 6.7 correctly documents 0%/99% per-year. The L-5 text should be updated to match the table. |
| Section 13 dispositions vs. L-1 through L-7 | YES | All prior red-team findings are addressed |

---

## L. Severity Assessment of All Issues

### Issues from First-Layer Audit (re-rated)

| ID | First-Layer Rating | Red-Team Rating | Rationale |
|----|-------------------|-----------------|-----------|
| L-1 | MAJOR (doc) | MAJOR (doc) | Agree. Builder docstring and metadata say FPI='6' but engine loads ['6','7']. A replicator following the code comments would be confused. Fix is trivial (update docstring + metadata). |
| L-2 | MAJOR (econometric) | MODERATE | Downgrade. The analysis in the audit is correct that duplicate indices do not introduce bias. Firm-clustered SEs handle within-firm-year correlation. The main consequence is interpretational (time FE pools all calls in a fiscal year), which is defensible for annual time effects. |
| L-3 | MINOR | MINOR | Agree. |
| L-4 | MINOR | MINOR | Agree. |
| L-5 | MINOR | MINOR | Agree, though the internal inconsistency in the audit text should be resolved. |
| L-6 | MINOR | MINOR | Agree. |
| L-7 | PROCEDURAL | PROCEDURAL | Agree. Must be resolved before thesis submission. |

### New Issues Found in This Audit

| ID | Finding | Severity | Recommendation |
|----|---------|----------|----------------|
| D-1 | Summary stats on pre-regression sample | MINOR | Add a note in the table indicating the sample universe, or compute stats on the estimation sample |
| D-3 | LaTeX table note inaccurately states "1%/99%" for all variables | MINOR | Update the LaTeX note to accurately reflect the heterogeneous winsorization scheme, or add a footnote |
| D-4 | No explicit intercept in industry FE spec (asymmetry with firm FE spec) | COSMETIC | No action needed; PanelOLS handles this correctly |
| D-5 | `year` column loaded but unused in runner | COSMETIC | No action needed |
| E-post | Extended controls (Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct) may be post-treatment | MODERATE (methodological) | Discuss in thesis text; consider showing results with and without these controls |

---

## M. Red-Team Verdict on First-Layer Audit

**Overall assessment: PASS -- the first-layer audit is factually correct, appropriately detailed, and adequately skeptical.**

The audit accurately documents the code, correctly identifies the major issues (FPI mismatch, duplicate index, missing execution evidence), and provides a substantive identification critique. All 30 factual claims independently verified were correct.

**Strengths:**
- Exhaustive variable dictionary with verified construction chains
- Honest identification critique that does not overclaim causal identification
- Internal cross-referencing between known limitations and design decisions
- Accurate winsorization summary table (Section 6.7) despite the inconsistent L-5 text

**Weaknesses:**
- Does not flag the post-treatment concern with extended linguistic controls
- Does not note the LaTeX table note inaccuracy as requiring a code fix (only documents it)
- Line number references are approximate in several places (functional, but a purist would want exact references)

---

## N. Recommendations for Thesis Submission

1. **Fix the builder docstring and metadata** (L-1): Change `postcall_dispersion.py` line 15 from `FPI='6'` to `FPI in ['6','7']` and line 109 metadata from `"6 (next quarter)"` to `"['6','7'] (current and next quarter)"`. This is a one-line documentation fix.

2. **Fix the LaTeX table note** (D-3): Replace the blanket "Variables winsorized at 1%/99%" with a more accurate statement, e.g., "Continuous financial controls winsorized at 1%/99% per fiscal year; linguistic variables at 0%/99% per calendar year; dispersion measures at 1%/99% pooled."

3. **Resolve L-5 internal inconsistency**: Update the L-5 body text to match the accurate Section 6.7 table, removing the "depends on Stage 2 upstream processing" characterization.

4. **Discuss post-treatment controls in thesis**: Note that Analyst_QA_Uncertainty_pct and Entire_All_Negative_pct are contemporaneous with the IVs and may attenuate coefficients if causally downstream of managerial speech.

5. **Run the suite and record output** (L-7): Produce execution evidence (sample sizes, R-squared, coefficient signs) before thesis submission.

6. **Consider VIF diagnostics**: The 4 correlated IVs entering simultaneously may produce uninformative individual t-tests. Report VIF or a joint F-test for the 4 IVs as a group.

---

## O. Disposition of Prior Red-Team Findings

The first-layer audit's Section 13 addresses 11 findings from a previous red-team audit (MI-1 through MI-8, E1-E3). All dispositions were verified as accurate:

- MI-1 (duplicate index): Correctly documented as L-2
- MI-2 (FPI mismatch): Correctly documented as L-1
- MI-4 (no identification discussion): Addressed in Section 11
- MI-5 (no robustness): Acknowledged in Section 11.3
- E1 (FPI claim): Corrected in the provenance document
- E3 (winsorization blanket statement): Corrected in Section 6.7, though L-5 text is inconsistent

All dispositions are appropriate.

---

## P. Sign-Off

| Item | Status |
|------|--------|
| All factual claims verified | YES (30/30) |
| Known limitations accurately rated | YES (7/7) |
| New issues found | 5 (1 MODERATE, 2 MINOR, 2 COSMETIC) |
| First-layer audit quality | PASS |
| Thesis-blocking issues | L-7 (no execution evidence) -- must be resolved before submission |
| Recommended code fixes | 2 (postcall_dispersion.py docstring/metadata, LaTeX table note) |

**Second-layer audit status: COMPLETE**
