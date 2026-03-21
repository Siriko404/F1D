# H6 Suite — Second-Layer Red-Team Audit

**Suite ID:** H6 (CCCL / SEC Scrutiny)
**Audit date:** 2026-03-18
**Auditor mode:** Fresh-context adversarial, second-layer (audit of audit)
**First-layer audit:** `docs/provenance/H6.md`
**Code version audited:** HEAD (working tree, post-commit `8f5e929`)
**Canonical run inspected:** `outputs/econometric/h6_cccl/2026-03-18_155736/`

---

## A. Red-Team Bottom Line

The first-layer audit is **substantially correct and unusually thorough** for a self-audit. It correctly identifies the three most critical issues in the suite (contemporaneous treatment, IV-vs-OLS mislabeling, pre-trends violation) and assigns appropriate severity levels. However, it contains **several factual errors** in its output-counting claims, an **internal contradiction** regarding Finance sample outputs, and **20 stale directories** (not 17). It also misses a material issue: the pre-trends test is run on a substantially smaller sample (N=57,136 vs N=67,393 in the base regression), making the lead coefficient comparison non-trivially confounded by sample composition. The audit is strong on econometric substance but occasionally sloppy on artifact verification.

**Overall first-layer audit quality:** 7.5/10. Rigorous on identification threats and econometric logic; weak on precise artifact accounting.

---

## B. Scope and Objects Audited

| Object | Path | Audited by L1? | Re-verified by L2? |
|--------|------|----------------|---------------------|
| Estimation runner | `src/f1d/econometric/run_h6_cccl.py` | Yes | Yes, line-by-line |
| Panel builder | `src/f1d/variables/build_h6_cccl_panel.py` | Yes | Yes, line-by-line |
| CCCL builder | `src/f1d/shared/variables/cccl_instrument.py` | Yes | Yes, full file |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` | Yes (partial) | Yes (winsorization block) |
| Linguistic engine | `src/f1d/shared/variables/_linguistic_engine.py` | Yes (partial) | Yes (winsorization block) |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` | Yes | Yes, full file |
| Leverage builder | `src/f1d/shared/variables/lev.py` | Mentioned | Yes, full file |
| Config: variables.yaml | `config/variables.yaml` | Yes | Yes (CCCL entries) |
| Model diagnostics CSV | `outputs/econometric/h6_cccl/2026-03-18_155736/model_diagnostics.csv` | Yes | Yes, full contents |
| Pre-trends output | `outputs/.../regression_results_Main_Manager_QA_Uncertainty_pct_PRETRENDS.txt` | Yes | Yes, full header |
| Sample attrition CSV | `outputs/.../sample_attrition.csv` | Yes | Yes |
| Output directory listing | `outputs/econometric/h6_cccl/` | Yes | Yes |
| LaTeX table | `outputs/.../h6_cccl_table.tex` | Yes (table notes) | Yes (via source code lines 287-357) |

---

## C. Audit-of-Audit Scorecard

| Dimension | Score (1-10) | Notes |
|-----------|-------------|-------|
| Factual accuracy of claims | 7 | Multiple counting errors (output files, stale directories); one internal contradiction |
| Completeness of code tracing | 9 | Traced all builders, merge logic, FE, clustering, winsorization |
| Identification threat coverage | 9 | Correctly identifies contemporaneous treatment, pre-trends failure, IV mislabeling, look-ahead bias, bad controls |
| Variable dictionary quality | 8 | Complete and accurate; minor: does not note that `BookLev` in audit text is called `Lev` in some builder references |
| Merge/provenance verification | 8 | Zero-row-delta enforcement verified; CCCL merge logic correct; some "UNVERIFIED" items left open |
| Estimation output verification | 6 | Internal contradiction on Finance file production; wrong count of stale dirs; pre-trends sample size difference missed |
| Robustness gap analysis | 9 | Comprehensive K5 table; correctly flags 12+ missing robustness checks |
| Reproducibility assessment | 8 | Correctly identifies config dependency, stale outputs, Utility failures |
| Academic integrity assessment | 9 | Correctly flags IV mislabeling, table note mismatches, suppressed warnings |
| Internal consistency of audit | 6 | Contradicts itself on Finance outputs; verification items 19 reference old run dir (053758) while canonical is 155736 |

---

## D. Claim Verification Matrix

| Claim ID | Claim (from H6.md) | Verified? | Evidence | Status |
|----------|---------------------|-----------|----------|--------|
| C1 | "No IV2SLS import or call" in run_h6_cccl.py | Yes | `grep IV2SLS` returns 0 matches; only `PanelOLS` imported (line 66) | **VERIFIED FACT** |
| C2 | "iv_cols is a misnomer" — used for regular OLS regressors | Yes | Line 148-154: `iv_cols` holds column names fed to PanelOLS formula, not an IV estimator | **VERIFIED FACT** |
| C3 | "prepare_regression_data() is a no-op" | Yes | Lines 136-138: returns `panel.copy()` with no transformation | **VERIFIED FACT** |
| C4 | "Table notes claim standardized controls" | Yes | Line 352: `"All continuous controls are standardized. "` | **VERIFIED FACT** |
| C5 | "Table notes claim 1%/99% winsorization" | Yes | Line 353: `"Variables are winsorized at 1\\%/99\\% by year. "` | **VERIFIED FACT** |
| C6 | "Linguistic vars winsorized at 0%/99% upper-only" | Yes | `_linguistic_engine.py` line 256-257: `lower=0.0, upper=0.99` | **VERIFIED FACT** |
| C7 | "Compustat controls winsorized per-year 1%/99%" | Yes | `_compustat_engine.py` lines 1177-1201: `_winsorize_by_year` applied to all control cols | **VERIFIED FACT** |
| C8 | "shift_intensity_mkvalt_ff48_lag never used in any regression" | Yes | `grep shift_intensity_mkvalt_ff48_lag run_h6_cccl.py` returns 0 matches | **VERIFIED FACT** |
| C9 | "8 Utility regressions fail with rank-deficiency" | Partially | Cannot verify from current artifacts (no log file inspected for 155736 run); code path shows Utility is attempted | **UNVERIFIED (plausible)** |
| C10 | "8 rows in model_diagnostics.csv" | Yes | CSV has exactly 8 data rows (4 Main + 4 Finance) | **VERIFIED FACT** |
| C11 | "lead1 beta=-0.0727, p=0.038" | Yes | Pre-trends .txt file: `shift_intensity_mkvalt_ff48_lead1  -0.0727  0.0350  -2.0767  0.0378` | **VERIFIED FACT** |
| C12 | "4 Main-sample base + 4 Main-sample pre-trends = 8 files (Finance and Utility produce no txt files)" (Section B) | **NO** | Latest run (155736) contains 16 regression .txt files: 8 Main + 8 Finance (4 base + 4 pre-trends each) | **VERIFIED ERROR** |
| C13 | "17 stale output directories" (Section J13, L22) | **NO** | `ls outputs/econometric/h6_cccl/` shows 20 directories (including 3 post-audit runs) | **VERIFIED ERROR** |
| C14 | "beta=-0.1125 for Main-MgrQA" | Yes | CSV: `beta1 = -0.11245970429237859` | **VERIFIED FACT** |
| C15 | "Within-R2 = 0.0038 for Main-MgrQA" | Yes | CSV: `within_r2 = 0.003794241064986048` | **VERIFIED FACT** |
| C16 | "112,968 rows in panel" | Plausible | Consistent with attrition CSV starting point; not independently re-verified on parquet | **UNVERIFIED (consistent)** |
| C17 | "One-tailed test correctly implemented" (K3) | Yes | Line 219: `p1_two / 2 if beta1 < 0 else 1 - p1_two / 2` | **VERIFIED FACT** |
| C18 | "Verification item 19: 12 regression .txt files (6 Main base + 6 Main pre-trends)" | **NO** | Item 19 references run 053758, which is not the canonical run; the canonical run (155736) has 16 files. Also "6" would imply 6 DVs, which is outdated (only 4 DVs in current code). | **VERIFIED ERROR** |
| C19 | "Fin-MgrQA beta=-1.046, p_one=0.033" | Yes | CSV: `beta1 = -1.0455787437104678`, `beta1_p_one = 0.03317357387794917` | **VERIFIED FACT** |
| C20 | "Fin-MgrPres beta=0.043, p_one=0.525 (wrong sign)" | Yes | CSV: `beta1 = 0.042816766921856445`, `beta1_p_one = 0.5248165999631622` | **VERIFIED FACT** |

---

## E. Unsupported/Overstated Claims

| ID | Claim | Issue | Severity |
|----|-------|-------|----------|
| E1 | "Finance and Utility produce no txt files in latest run" (Section B, line 130) | **Factually wrong.** The latest run (2026-03-18_155736) contains 8 Finance regression .txt files. The audit's own Section E5 and H tables correctly report 4 Finance models succeeding. This is an internal contradiction within the audit. | Medium |
| E2 | "17 stale output directories" (J13, L22) | **Incorrect count.** There are 20 directories, not 17. The audit was likely written when only 17 existed, and was not updated after additional runs were executed. | Low |
| E3 | Verification item 19: "12 regression .txt files (6 Main base + 6 Main pre-trends)" | References the old run directory (053758), not the canonical run (155736). The count of "6" implies a prior code version with 6 DVs, not the current 4. The canonical run has 16 files, not 12. | Low (affects verification log only) |
| E4 | "CCCL includes firm's own industry standing" (K4, first bullet) | The claim that "the instrument value is firm-specific, not purely industry-level" because the firm's own `share_lag_mkvalt_ff48` determines its weight needs qualification. The shift-intensity instrument construction typically excludes the firm itself (leave-one-out). Without inspecting the external instrument construction code, this claim is **unverified by the audit itself** yet stated as fact. | Medium |

---

## F. False Positives

| ID | Claim in L1 audit | Why it is a false positive or overstated | Recalibrated severity |
|----|--------------------|-----------------------------------------|----------------------|
| F1 | "J6: Time FE uses calendar year, CCCL uses fiscal year — minor misalignment" rated Low | This is correctly identified but arguably not a defect at all. The entity FE absorb firm-level effects and the year FE absorb common annual shocks. Using calendar year for time FE when the instrument is matched on fiscal year is standard practice in panel studies with varying fiscal years. The "misalignment" does not introduce bias. | Non-issue (informational only) |
| F2 | "L7: PanelOLS multi-index (gvkey, year) is not unique — High severity" | The severity is overstated. PanelOLS with a non-unique multi-index is a well-known use case in `linearmodels`. Entity effects demean within gvkey (across all observations for that firm), and time effects demean within year. The clustering at firm level properly accounts for within-firm correlation. The non-unique index does not invalidate the estimation; it simply means the panel is unbalanced at the call level within firm-years. | Low-Medium (document, do not block) |

---

## G. Missed Issues

| ID | Issue | Evidence | Severity | Why first-layer audit missed it |
|----|-------|----------|----------|---------------------------------|
| G1 | **Pre-trends test uses a substantially smaller sample (N=57,136) than the base regression (N=67,393).** The ~10,257 observation difference arises because the pre-trends model requires non-null `lead1` and `lead2` values, which drops observations at the end of the panel. The lead coefficient significance (p=0.038) may be partly an artifact of the changed sample composition, not a true pre-trends violation. | Pre-trends output header: `No. Observations: 57136` vs base: `N=67,393` | Medium-High | Audit focused on the coefficient result without noting the sample difference |
| G2 | **LaTeX table star symbols use one-tailed p-values against standard two-tailed thresholds.** The `fmt_coef` function (line 265-275) applies conventional thresholds (0.01, 0.05, 0.10) to one-tailed p-values. A coefficient with a two-tailed p=0.066 (e.g., Finance MgrQA) receives `**` stars because the one-tailed p=0.033 crosses the 0.05 threshold. The table note says "(one-tailed)" but a reader accustomed to standard conventions may overinterpret the stars. | Code lines 265-275 and 303: `fmt_coef(r_1['beta1'], r_1['beta1_p_one'])` | Medium | Audit noted the one-tailed test is "correctly implemented" but did not flag the star-threshold interaction in the LaTeX table |
| G3 | **A post-canonical run exists (2026-03-18_185641) with identical results.** The audit declares 155736 as canonical but a later run was executed. If results are identical, this is harmless; if not, it would undermine the canonical designation. | Directory listing shows `2026-03-18_185641/` after `2026-03-18_155736/` | Low | Audit was likely completed before the later run |
| G4 | **No discussion of the `drop_absorbed=True` parameter's implications.** PanelOLS with `drop_absorbed=True` (line 196) silently drops any absorbed regressors. If any controls are collinear with the FE structure, they are dropped without explicit logging. This could mask specification issues. | `run_h6_cccl.py` line 196: `model_obj = PanelOLS.from_formula(form_clean, data=df_panel, drop_absorbed=True)` | Low-Medium | Not flagged in any section of the L1 audit |
| G5 | **Attrition table only reports the Main-MgrQA path.** The attrition table (lines 507-512) uses `main_result` which is the first Main-sample result. It does not report attrition for Finance or Utility samples, or for CEO-specific DVs (which have ~30% higher missingness). | Code lines 506-512; `sample_attrition.csv` shows only one path | Medium | Audit notes "40.3% loss" but does not note the attrition table covers only one of 12 estimation paths |
| G6 | **`rsquared` and `within_r2` are identical in the diagnostics CSV.** Lines 237-239: `"rsquared": float(model.rsquared_within)` and `"within_r2": within_r2` (which equals `float(model.rsquared_within)`). The `rsquared` column is mislabeled — it is not the overall R-squared but a duplicate of within-R-squared. | CSV data: `rsquared` column equals `within_r2` column for all rows | Low | Not flagged |

---

## H. Severity Recalibration

| Issue ID (from L1) | L1 Severity | L2 Recalibrated Severity | Rationale |
|---------------------|-------------|--------------------------|-----------|
| L1 (Contemporaneous treatment) | Critical | **Critical** (agree) | No temporal separation is the most fundamental identification flaw. Correctly rated. |
| L2 (IV label on OLS) | Critical | **High** | Downgrade from Critical: the mislabeling is a documentation/framing issue, not an estimation error. The reduced-form OLS is itself a valid (if limited) estimator. A rename solves the problem entirely. |
| L3 (Pre-trends violation) | High | **Medium-High** | Slight downgrade: the pre-trends test operates on a 15% smaller sample (57,136 vs 67,393). The significance (p=0.038) is marginal and could reflect sample composition differences, not a genuine pre-trends violation. Still concerning but not definitive. |
| L7 (Non-unique panel index) | High | **Low-Medium** | Significant downgrade: PanelOLS handles non-unique (entity, time) indices as a standard use case. Clustering at firm level is correct. This is not an error but a feature of call-level analysis with firm-year FE. |
| L8 (Table note mismatches) | High | **High** (agree) | Table notes claiming "standardized" and "1%/99%" are factually wrong and would mislead a replicator. Correctly rated. |
| L9 (No MHC) | Medium-High | **Medium** | Slight downgrade: multiple hypothesis correction is a legitimate concern but the 8 tests are not independent (same underlying data, overlapping samples). Bonferroni would be overly conservative. Romano-Wolf or FDR would be more appropriate. |
| L10 (Own-firm contamination) | Medium-High | **Medium-High** (agree) | Valid concern. Without seeing the instrument construction code, cannot confirm whether leave-one-out is already applied. |
| L16 (Low within-R2) | Medium | **Low-Medium** | Within-R2 of 0.3-0.4% is not unusual for call-level panel regressions with firm FE. The firm FE absorb most of the cross-sectional variation; the within-R2 reflects only time-series variation within firms. Low within-R2 is expected, not alarming. |

---

## I. Completeness Gaps

| Gap | What is missing | Impact on thesis review | Effort to close |
|-----|-----------------|------------------------|-----------------|
| I1 | **No verification of CRSP Volatility winsorization.** The audit marks this "UNVERIFIED" (Section G, Volatility row) and never resolves it. | Low: winsorization of a control variable is unlikely to materially affect results | Low: inspect `_crsp_engine.py` |
| I2 | **No verification of raw Compustat or CRSP row counts.** The audit marks these "UNVERIFIED" in Section D. | Low: these are upstream inputs; the panel builder's zero-row-delta enforcement provides indirect validation | Medium: requires running the full pipeline |
| I3 | **No inspection of the actual Utility failure logs for the canonical run (155736).** The audit references log files from run 053758, not the canonical run. | Low: the Utility failure mode is likely identical across runs, but this is unverified | Low: inspect `logs/H6_CCCL/2026-03-18_155736/run.log` |
| I4 | **No verification of the CCCL instrument construction itself.** The audit takes the pre-computed CCCL instrument at face value. The leave-one-out question (L10), the normalization, and the "market-value weighted" construction are all unverified. | Medium: the instrument is the core of the suite; its construction quality determines the validity of all results | High: requires access to the CCCL construction code (external) |
| I5 | **No comparison of results across the 20 output directories** to verify that the canonical run is indeed the correct one and that earlier runs used "superseded code." | Low: the latest run is likely correct, but the audit's claim about superseded code is unverified | Medium |

---

## J. Reproducibility Assessment

| Criterion | Met? | Evidence | Notes |
|-----------|------|----------|-------|
| All source code present and readable | Yes | `run_h6_cccl.py`, `build_h6_cccl_panel.py`, all builders in `src/f1d/shared/variables/` | |
| Config dependencies documented | Partially | Audit notes `variables.yaml` dependency (J3); `project.yaml` also needed but not discussed in detail | |
| Input data paths documented | Yes | Section D lists all input paths | |
| Output artifacts match audit claims | **No** | Audit claims 8 regression files; actual count is 16 (8 base + 8 pre-trends, Main + Finance) | Internal contradiction |
| Canonical run identified | Partially | Audit says 155736 but a later run (185641) exists; both appear to have identical results | |
| Stale artifact accounting accurate | **No** | 20 directories, not 17 | |
| End-to-end reproduction instructions present | Yes | Section B provides commands | |
| Environment pinned | Partially | Python 3.13.5, linearmodels 7.0, etc. listed but no lockfile reference | |

---

## K. Econometric Meta-Audit

| Dimension | L1 Audit Assessment | L2 Agreement? | L2 Notes |
|-----------|---------------------|---------------|----------|
| Estimator choice (PanelOLS vs IV2SLS) | Correctly flags OLS-not-IV | **Agree** | The most important finding. The suite name is misleading. |
| Fixed effects specification | Correctly documents firm + year FE | **Agree** | Appropriate for the research design |
| Clustering | Correctly documents firm-level clustering | **Agree** | Could add industry-level clustering as robustness |
| Treatment timing | Correctly flags contemporaneous treatment as Critical | **Agree** | The lag variable exists but is unused — a baffling omission |
| Pre-trends interpretation | Correctly flags lead1 significance as violation | **Partially agree** | The 15% sample size reduction (57K vs 67K) in the pre-trends spec should qualify the conclusion; marginal significance (p=0.038) on a smaller sample is less definitive than presented |
| Control variable concerns | Correctly flags potential bad controls | **Agree** | Post-treatment controls (Volatility, RD_Intensity) are a valid concern |
| Multiple testing | Correctly flags absence of MHC | **Agree** | Though Bonferroni is too conservative for dependent tests |
| Economic significance | Correctly flags negligible magnitudes | **Agree** | One-SD effect of ~0.004 pp is economically meaningless |
| CCCL distribution concerns | Correctly flags extreme right skew | **Agree** | Critical robustness gap |
| Identification strategy coherence | Correctly identifies fundamental incoherence (IV name, OLS estimation, no lag) | **Agree** | The suite's identification strategy is not internally consistent |

**L2 Econometric Assessment:** The first-layer audit is strong on econometric substance. Its identification of the contemporaneous-treatment problem as the primary threat is exactly right. The one area where the L1 audit could be more nuanced is on the pre-trends test: the sample size difference between the base and pre-trends regressions (67,393 vs 57,136) means the marginal significance (p=0.038) should be interpreted cautiously. The audit presents it as a definitive violation, when it is more accurately a warning flag that warrants further investigation (e.g., re-running the pre-trends test on the same sample as the base regression).

---

## L. Audit-Safety Assessment

| Risk | Evidence | Severity |
|------|----------|----------|
| **Internal contradiction could mislead.** Section B says "Finance produces no txt files" while Sections E5 and H show Finance succeeding. A reader trusting Section B would undercount available results. | Section B line 130 vs Section E5 and H | Medium |
| **Stale directory count (17 vs 20) could lead to incomplete cleanup.** | Section J13/L22 | Low |
| **Verification items reference old run (053758) not canonical (155736).** Items 11, 17, 19 reference the old directory. | Section I, items 11, 17, 19 | Low-Medium |
| **Audit does not note that `rsquared` column in diagnostics is a duplicate of `within_r2`.** A reader might interpret `rsquared` as overall R-squared. | model_diagnostics.csv column naming | Low |

---

## M. Master Issue Register

| ID | Source | Category | Severity | Verified? | Description | Blocks thesis? |
|----|--------|----------|----------|-----------|-------------|----------------|
| RT2-1 | L1 audit, Section B | Audit factual error | Medium | Yes | L1 audit claims "Finance and Utility produce no txt files in latest run" — Finance produces 8 .txt files | N/A (audit error) |
| RT2-2 | L1 audit, Section J13/L22 | Audit factual error | Low | Yes | L1 claims 17 stale directories; actual count is 20 | N/A (audit error) |
| RT2-3 | L1 audit, Section I item 19 | Audit factual error | Low | Yes | Verification item 19 references old run dir (053758) with outdated file counts (12 files, 6 DVs) — does not match canonical run (155736, 16 files, 4 DVs) | N/A (audit error) |
| RT2-4 | New finding | Estimation | Medium-High | Yes | Pre-trends regression runs on N=57,136 (15.2% fewer obs than base N=67,393). Lead coefficient significance (p=0.038) may partly reflect sample composition change. | N (but should re-run on matched sample) |
| RT2-5 | New finding | Reporting | Medium | Yes | LaTeX table applies standard star thresholds (0.01/0.05/0.10) to one-tailed p-values, inflating apparent significance. Finance MgrQA gets ** stars despite two-tailed p=0.066. | Y (fix table or note convention explicitly) |
| RT2-6 | New finding | Reporting | Low | Yes | `rsquared` and `within_r2` columns in diagnostics CSV are identical (both are within-R2). Mislabeled. | N |
| RT2-7 | New finding | Estimation | Low-Medium | Yes | `drop_absorbed=True` silently drops collinear regressors without logging which (if any) were dropped. | N |
| RT2-8 | New finding | Reporting | Medium | Yes | Attrition table reports only Main-MgrQA path; does not show Finance, Utility, or CEO-specific DV attrition paths. | N (but recommended) |
| RT2-9 | L1 recalibration | Identification | Downgrade | -- | L7 (non-unique index) downgraded from High to Low-Medium. PanelOLS handles non-unique (entity, time) indices correctly with firm-level clustering. | No longer blocks |
| RT2-10 | L1 recalibration | Identification | Downgrade | -- | L2 (IV label on OLS) downgraded from Critical to High. A naming/framing issue, not an estimation error. | Still blocks (but lower bar to fix) |
| L1-confirmed | L1 audit L1 | Identification | Critical | Yes | L1 (contemporaneous treatment) confirmed as the primary threat. Lag variable exists but is unused. | **Y** |
| L1-confirmed | L1 audit L3 | Identification | Medium-High | Yes | L3 (pre-trends lead1 p=0.038) confirmed but qualified by sample size difference (G1/RT2-4). | **Y** (with caveat) |
| L1-confirmed | L1 audit L8 | Academic integrity | High | Yes | Table note mismatches ("standardized", "1%/99%") confirmed. | **Y** |

---

## N. What Committee Would Not Know

Based solely on reading the first-layer audit, a committee member would NOT know:

1. **The pre-trends test uses a 15% smaller sample** (57,136 vs 67,393). The audit presents the lead1 coefficient as a definitive pre-trends violation, but the sample composition difference introduces ambiguity. A committee member should ask: "Does the lead significance survive when the base and pre-trends regressions use the same sample?"

2. **The LaTeX table stars are mechanically inflated** by applying standard thresholds to one-tailed p-values. The Finance MgrQA result appears with ** stars despite a two-tailed p=0.066.

3. **The first-layer audit contradicts itself on Finance outputs.** Section B says no Finance .txt files; Sections E5/H report 4 successful Finance models. A committee member reading only Section B would think only Main-sample results exist.

4. **There are 20 stale output directories**, not 17, and a run exists after the designated canonical run.

5. **The `drop_absorbed=True` parameter** could be silently dropping controls without any diagnostic output.

6. **The attrition table covers only one estimation path** (Main, MgrQA) and does not show the differential attrition for CEO DVs (~32% missingness) or Finance/Utility samples.

---

## O. Priority Fixes

| Priority | Fix | Source | Effort | Impact |
|----------|-----|--------|--------|--------|
| 1 | **Switch primary spec to lagged CCCL (t-1).** | L1-L1, confirmed | Low (one-line change) | Resolves the most critical identification threat |
| 2 | **Rename suite from "IV/Instrument" to "Reduced-Form."** | L1-L2, confirmed (downgraded to High) | Low | Eliminates the single most misleading framing issue |
| 3 | **Fix table notes** — remove "standardized" claim; correct winsorization description. | L1-L8, confirmed | Low | Prevents replication failure and committee embarrassment |
| 4 | **Fix LaTeX star convention** — either use two-tailed p-values for stars or clearly document the one-tailed star thresholds in the table note. | RT2-5, new | Low | Prevents inflated appearance of significance |
| 5 | **Re-run pre-trends on matched sample** (restrict base and pre-trends regressions to the same N). | RT2-4, new | Low | Resolves ambiguity about whether lead significance is genuine |
| 6 | **Report pre-trends in structured output** (add to diagnostics CSV and/or LaTeX table). | L1-L20, confirmed | Low | Makes the pre-trends finding auditable |
| 7 | **Document estimation failures** in model_diagnostics.csv. | L1-L4, confirmed | Low | Prevents silent data loss |
| 8 | **Correct audit internal contradiction** — update Section B to reflect Finance outputs. | RT2-1 | Low | Internal consistency of provenance documentation |
| 9 | **Add industry-year FE specification** as robustness. | L1-L13, confirmed | Low-Medium | Addresses key omitted variable concern |
| 10 | **Apply MHC** (FDR or Romano-Wolf, not Bonferroni). | L1-L9, recalibrated | Low | Addresses multiple testing concern |

---

## P. Final Readiness Statement

**Is the first-layer audit trustworthy as a basis for thesis committee review?**

Substantially yes, with caveats. The first-layer audit correctly identifies the three most important issues in the H6 suite: (1) contemporaneous treatment with no lag, (2) IV mislabeling on an OLS implementation, and (3) a pre-trends violation in the primary specification. These findings are verified and the severity assessments are largely appropriate (with minor recalibrations noted in Section H). The econometric analysis is rigorous and the priority fixes are well-ordered.

However, the audit contains factual errors in its artifact accounting (Finance file production, stale directory count, verification item references to old runs) that, while not material to the econometric conclusions, undermine confidence in the audit's attention to detail. The audit also misses the pre-trends sample size issue (RT2-4), which qualifies its strongest finding.

**Recommended actions before submitting to committee:**
1. Fix the three factual errors in the audit (RT2-1, RT2-2, RT2-3).
2. Implement Priority 1 (lagged CCCL) — this is a one-line code change that resolves the most critical threat.
3. Fix table notes (Priority 3) and star convention (Priority 4).
4. Re-run pre-trends on the matched sample (Priority 5) to determine if the violation is genuine.

**Suite readiness:** NOT READY for thesis submission in current form. The contemporaneous treatment specification and IV mislabeling are blocking issues. With lagged CCCL and honest "reduced-form" framing, the suite becomes defensible as a descriptive finding (association, not causation) if the pre-trends concern is addressed.
