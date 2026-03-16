# H12 Second-Layer Red-Team Audit

**Suite ID:** H12
**Red-team auditor:** Independent (fresh context, adversarial posture)
**Date:** 2026-03-15
**First-layer audit under review:** `docs/provenance/H12.md`

---

## A. Red-Team Bottom Line

The first-layer audit is detailed, well-structured, and correctly identifies the most important econometric concern (zero-inflated DV modeled with OLS). However, it contains a **material factual error** regarding the Finance sample results: it claims "All beta1 > 0, none significant" when in fact 8 of 12 Finance specifications are statistically significant at p < 0.05 (two-tailed) with positive coefficients. This is a significant finding -- uncertainty is associated with *higher* dividend intensity in financial firms, the opposite of H12 -- and the first audit entirely fails to flag it. Additionally, the first audit incorrectly claims Utility was skipped for insufficient data, but the latest panel yields sufficient observations for all 12 Utility specs. The audit also makes a false claim about `get_latest_output_dir` using a "file count heuristic" when it actually uses timestamp sorting.

**Overall grade for the first audit:** PARTIALLY RELIABLE

**Suite as implemented:** SALVAGEABLE WITH MAJOR REVISIONS

**Risk assessment:** The first audit **understated risk** by missing the significant opposite-sign Finance results and their implications, while correctly identifying the zero-inflation and robustness gaps.

---

## B. Scope and Objects Audited

| Item | Path / Reference |
|------|-----------------|
| Suite ID | H12 |
| Suite entrypoint | `src/f1d/econometric/run_h12_div_intensity.py` |
| Panel builder | `src/f1d/variables/build_h12_div_intensity_panel.py` |
| First-layer audit | `docs/provenance/H12.md` |
| DivIntensity builder | `src/f1d/shared/variables/div_intensity.py` |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` (lines 227-297, 1065-1162) |
| LinguisticEngine | `src/f1d/shared/variables/_linguistic_engine.py` (lines 235-259) |
| Winsorization module | `src/f1d/shared/variables/winsorization.py` |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` (lines 46-192) |
| Path utilities | `src/f1d/shared/path_utils.py` (lines 254-312) |
| Latest panel artifact | `outputs/variables/h12_div_intensity/2026-03-05_210240/h12_div_intensity_panel.parquet` |
| Latest diagnostics CSV | `outputs/econometric/h12_div_intensity/2026-03-05_210406/model_diagnostics.csv` |
| Latest run manifest | `outputs/econometric/h12_div_intensity/2026-03-05_210406/run_manifest.json` |
| Latest sanity checks | `outputs/econometric/h12_div_intensity/2026-03-05_210406/sanity_checks.txt` |
| Latest report | `outputs/econometric/h12_div_intensity/2026-03-05_210406/report_step4_H12.md` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | Pass | Code lines cited; formula verified | Correctly identifies PanelOLS with entity+time FE, firm-clustered SE |
| Reproducibility commands | Partial | Stage 3 + Stage 4 commands given | Misses that Finance .txt files not saved; Utility skip claim incorrect |
| Dependency tracing | Pass | Full chain from raw to output enumerated | All 16 builders and 8 chain steps correctly traced |
| Raw data provenance | Partial | 3 datasets listed; Compustat/linguistic row counts UNVERIFIED | Correctly labels UNVERIFIED items |
| Merge/sample audit | Pass | Zero-delta enforcement verified; aggregation methods correct | merge_asof, groupby aggregation logic verified independently |
| Variable dictionary completeness | Pass | 22 variables documented with formulas, timing, winsorization | Thorough; all panel columns covered |
| Outlier/missing-data rules | Pass | Engine-level winsorization, listwise deletion documented | Winsorization bounds verified in code |
| Estimation spec register | **Fail** | Finance specs described as "none significant" | 8/12 Finance specs are significant (two-tailed p < 0.05, positive direction); factual error |
| Verification log quality | Partial | 20 verification steps logged | Missing: verification of Finance coefficient significance; Utility skip reason |
| Known issues section | Pass | 8 issues documented with clear impact/fix | Correctly identifies MIN_CALLS naming, docstring mismatch, zero-inflation |
| Identification critique | Pass | Reverse causality, OVB, sample selection covered | Adequate for panel OLS |
| Econometric implementation critique | Pass | Zero-inflation, low R2, absorbed firms flagged | Core concern correctly identified |
| Robustness critique | Pass | Comprehensive gap analysis (11 dimensions) | Correctly notes absence of alt-FE, alt-cluster, placebo, subperiod |
| Academic-integrity critique | Partial | Docstring mismatch, unpinned version noted | Misses DivIntensityBuilder docstring error; misses Finance .txt file gap |
| Severity calibration | Partial | L1 (zero-inflation) correctly Critical | Misses Finance positive-significant result as a severity-worthy finding |
| Final thesis verdict support | Partial | "SALVAGEABLE WITH MAJOR REVISIONS" is correct | But verdict incomplete without the Finance opposite-sign finding |

---

## D. Claim Verification Matrix (First Audit Claims Tested)

| ID | First-layer claim | Section | Verified? | Evidence checked | Red-team verdict | Notes |
|----|-------------------|---------|-----------|-----------------|------------------|-------|
| C1 | PanelOLS with EntityEffects + TimeEffects, drop_absorbed=True | A2 | Y | `run_h12_div_intensity.py:333` | Correct | Formula includes `EntityEffects + TimeEffects` |
| C2 | Firm-clustered SEs via `cluster_entity=True` | A5 | Y | `run_h12_div_intensity.py:334` | Correct | `cov_type="clustered", cluster_entity=True` |
| C3 | DivIntensity_lead = dvy_Q4_{t+1} / atq_t | A3 | Y | `_compustat_engine.py:1077-1084`, `build_h12_div_intensity_panel.py:164-185` | Correct | Forward shift of DivIntensity = dvy_Q4_t / atq_{t-1} |
| C4 | 29,343 firm-years, 2,429 firms, 20 fiscal years | C | Y | `pd.read_parquet` inspection | Correct | Shape (29343, 22), gvkey nunique=2429, fyearq 2000-2019 |
| C5 | 0 duplicate (gvkey, fyearq) pairs | E3 | Y | `df.duplicated(subset=['gvkey','fyearq']).sum()=0` | Correct | |
| C6 | 45.4% of DivIntensity = 0 | K2, L1 | Y | `(df['DivIntensity']==0).sum()/df['DivIntensity'].notna().sum()=45.4%` | Correct | 13,292/29,289 |
| C7 | 773/2,429 firms have constant DivIntensity | I (line 352) | Y | Independent groupby std computation | Correct | 773 firms with std=0 and >1 obs |
| C8 | Main: 732/1,884 constant-zero DivIntensity (38.9%) | K3 | Y | Independent computation | Correct | 732/1884 = 38.9% |
| C9 | CEO measures ~25% missing | A4 | Y | CEO_QA: 7,147/29,343 (24.4%); CEO_Pres: 7,342/29,343 (25.0%) | Correct | |
| C10 | 24 regressions completed, Utility skipped | H, C | **Partial** | `model_diagnostics.csv` has 24 rows (12 Main + 12 Finance) | Correct that 24 ran; **incorrect that Utility was skipped for insufficient data** -- latest panel gives 80+ firms and 1000+ obs for Utility | See G1 |
| C11 | "M7a-M12a: All beta1 > 0, none significant" (Finance DivIntensity) | H | **N** | Diagnostics CSV: 5/6 Finance DivIntensity specs have p_two < 0.05 | **FACTUAL ERROR** -- coefficients are positive AND statistically significant (two-tailed) | See E1 |
| C12 | "M7b-M12b: All beta1 > 0, none significant" (Finance DivIntensity_lead) | H | **N** | 3/6 Finance DivIntensity_lead specs have p_two < 0.05 | **FACTUAL ERROR** -- same issue | See E1 |
| C13 | 0/24 support H12 | H | Y | All beta1_signif=False in diagnostics | Correct for H12 direction (one-tailed, beta < 0) | But omits opposite-direction significance |
| C14 | `get_latest_output_dir()` resolves by file count heuristic | B | **N** | `path_utils.py:300-301`: `sorted(timestamped_dirs, key=lambda d: d.name, reverse=True)` | **FALSE CLAIM** -- uses timestamp-sorted directory names, not file count | See F1 |
| C15 | Winsorization: Compustat by-year 1%/99%; Linguistic by-year 0%/99% | G1 | Y | `_compustat_engine.py:1158`, `_linguistic_engine.py:255-258` | Correct | |
| C16 | BASE_CONTROLS has 7 entries vs docstring 4 | J2 | Y | Lines 104-112 vs lines 13-18 | Correct | |
| C17 | MIN_CALLS_PER_FIRM=5 filters on firm-year count, not calls | E5, J1 | Y | `run_h12_div_intensity.py:298-300` | Correct | `df_reg["gvkey"].value_counts()` counts firm-years |
| C18 | One-tailed p-value formula correct | K6 | Y | `run_h12_div_intensity.py:351-354` | Correct | `p_two/2 if beta < 0 else 1-p_two/2` |
| C19 | Zero-row-delta enforcement in panel builder | E1 | Y | `build_h12_div_intensity_panel.py:258-263` | Correct | `raise ValueError` if delta != 0 |
| C20 | Lead DV gap detection: non-consecutive fyearq set to NaN | E4 | Y | `build_h12_div_intensity_panel.py:176-181` | Correct | Int64 casting, gap > 1 check |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim / statement | Why unsupported or weak | Severity | What evidence was missing | Corrected formulation |
|----|-------------------|------------------------|----------|--------------------------|----------------------|
| E1 | "M7a-M12a: All beta1 > 0, none significant" and "M7b-M12b: All beta1 > 0, none significant" (Section H) | Finance coefficients ARE statistically significant at conventional two-tailed thresholds (8/12 have p_two < 0.05). The audit only checked one-tailed significance (H12 direction) and failed to report two-tailed significance in the opposite direction. | **Critical** | Two-tailed p-values for Finance specs: 5/6 DivIntensity specs have p_two < 0.05; 3/6 DivIntensity_lead specs have p_two < 0.05 | "All 12 Finance coefficients are positive. 8 of 12 are statistically significant (p_two < 0.05), indicating that higher uncertainty is associated with HIGHER dividend intensity in financial firms -- opposite to H12." |
| E2 | "Utility skipped: Insufficient data (<200 obs or <50 firms after filters)" (Section H, L12) | With the latest panel (2026-03-05_210240), Utility specs have 640-1,099 obs and 60-80 firms after filters, well above both thresholds. | **Medium** | The first audit did not independently verify whether the thresholds were actually breached for the specific panel used. The Utility skip may have occurred due to a runtime error or earlier panel, but the stated reason is not supported by the current panel. | "Utility results are absent from the diagnostics CSV. The stated reason (<200 obs or <50 firms) is not supported by the latest panel, which yields 640-1,099 obs and 60-80 firms per spec. The actual cause of the skip is unverified." |
| E3 | "`get_latest_output_dir()` resolves by file count heuristic" (Section B) | The code at `path_utils.py:300-301` sorts directories by name (chronological timestamp), not by file count. | **Low** | Reading `path_utils.py` would have shown the actual resolution mechanism. | "`get_latest_output_dir()` sorts timestamped directories lexicographically by name (newest first) and, if `required_file` is specified, selects the first containing that file." |
| E4 | "3 stale panel directories exist alongside latest" (L14) | While 3 directories exist, this is described as a problem with "latest resolution" failing. The timestamp-sorted resolution is robust to multiple directories. | **Low** | The actual risk is not wrong-directory selection but disk clutter and confusion. | "3 timestamped panel directories exist. The timestamp-based resolution correctly selects the latest. Stale directories are a housekeeping issue, not a resolution risk." |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|----------------------------------|----------|------------------------|----------------|
| F1 | `get_latest_output_dir()` resolves by "file count heuristic"; "multiple partial runs could select wrong directory" (Section B) | The function uses timestamp-sorted directory names and, when `required_file` is specified, validates the file exists. This is robust, not heuristic-based. | `path_utils.py:254-312`: sorts by `d.name`, checks `(d / required_file).exists()` | Low | The directory resolution is deterministic and file-validated. The "file count heuristic" criticism is a factual error in the first audit. |

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed/underplayed | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|-----------------------------------|-------------|----------------|
| G1 | Estimation results interpretation | **Finance sample shows significant POSITIVE coefficients** (opposite to H12). 8/12 Finance specs have two-tailed p < 0.05 with positive beta1. This is a substantive finding: uncertainty is associated with HIGHER dividends in financial firms. | `model_diagnostics.csv`: Finance/DivIntensity Manager_QA p_two=0.022, Weak_Modal p_two=0.033, CEO_Weak_Modal p_two=0.011, Pres p_two=0.041; Finance/DivIntensity_lead Manager_QA p_two=0.013, Weak_Modal p_two=0.034, CEO_Weak_Modal p_two=0.016, Pres p_two=0.003 | **Critical** | First audit only checked one-tailed significance (H12 direction: beta < 0) and concluded "none significant," ignoring that positive coefficients can be significant in the two-tailed sense | A thesis presenting "null results across all specifications" would be factually misleading. The Finance sample shows a significant opposite-direction effect that requires discussion. | Report two-tailed significance; discuss the positive Finance-sample finding; compare Main (null) vs Finance (positive significant) patterns |
| G2 | Output integrity | **Finance regression .txt files missing from output directory.** Diagnostics CSV records 12 Finance regressions, but no `regression_results_Finance_*.txt` files exist in `outputs/econometric/h12_div_intensity/2026-03-05_210406/`. | `ls` of output directory: only 12 Main .txt files present; 0 Finance files | **Medium** | First audit did not verify that per-regression output files match the diagnostics CSV | Incomplete audit trail; Finance regression summaries (with full PanelOLS output) are not preserved | Investigate why Finance .txt files were not saved; rerun to ensure all outputs are complete |
| G3 | Utility sample | **Utility sample should be runnable** with the latest panel. All 12 specs pass CONFIG thresholds (min_obs=200, min_firms=50). | Independent simulation: Manager_QA DivIntensity gives 1,099 obs, 80 firms; CEO_Pres DivIntensity_lead gives 640 obs, 60 firms | **Medium** | First audit accepted the "insufficient data" explanation without verifying against the actual panel | 12 Utility regressions are missing from the output despite being feasible; Utility results could inform the analysis | Rerun with the latest panel; if Utility regressions still fail, investigate the runtime cause |
| G4 | Documentation gap | **DivIntensityBuilder docstring says `dvy_Q4 / atq`** (contemporaneous) but the CompustatEngine uses `atq_annual_lag1` (lagged). This is a secondary docstring error distinct from the runner docstring error the first audit flagged (J2). | `div_intensity.py:4`: "dvy_Q4 / atq" vs `_compustat_engine.py:1077-1084`: uses `atq_annual_lag1` | **Low** | First audit traced the CompustatEngine correctly but did not check the builder docstring | Reader of the builder module gets wrong denominator impression | Update `div_intensity.py` docstring to "dvy_Q4 / atq_{t-1}" |
| G5 | LaTeX table | **Mixed significance star basis**: LaTeX table uses one-tailed p-values for beta1 (line 491: `beta1_p_one`) but two-tailed p-values for control coefficients (line 503: `p_{ctrl}` from `model.pvalues`). The table note partially discloses this but a reader would likely apply the same interpretation to all stars. | `run_h12_div_intensity.py:491` vs `run_h12_div_intensity.py:503` | **Medium** | First audit noted the one-tailed test but did not verify that the LaTeX star logic is internally consistent across rows | Stars on controls use two-tailed thresholds while the beta1 star uses one-tailed, creating an inconsistent table | Use two-tailed p-values for all rows, or clearly label the difference; add a separate column for one-tailed H12 test result |
| G6 | Inference concern | **Finance cluster counts are low for some CEO specs** (258-291 firms). While above the conventional 50-cluster threshold, these are in the range where cluster-robust SEs may be unreliable. Combined with the significant positive coefficients, this warrants a small-sample caveat. | `model_diagnostics.csv`: Finance CEO specs have 258-291 clusters | **Low** | First audit did not examine Finance cluster counts specifically because it assumed Finance results were insignificant | The significant Finance results rely on 258-291 clusters, which is adequate but not large | Disclose cluster counts for Finance; consider wild bootstrap for robustness |
| G7 | Robustness / interpretation | **No discussion of Main vs Finance divergence.** Main sample: all null; Finance sample: 8/12 significantly positive. This divergence is econometrically interesting and requires explanation (different payout norms, regulatory environment, sample composition). | Diagnostics CSV comparison | **High** | First audit missed the Finance significance entirely | A referee would immediately ask why the effect reverses between Main and Finance; the thesis must address this | Add explicit discussion of Main vs Finance divergence; consider interaction model (uncertainty x financial_sector) |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|-----------------|---------------|
| L1 | First audit | Critical | Critical | Agree: zero-inflated DV with OLS is the fundamental concern | Blocks credible coefficient interpretation |
| L2 | First audit | High | High | Agree: missing payout-specific controls | Standard OVB concern |
| L3 | First audit | High | High | Agree: no extensive/intensive margin separation | Cannot interpret economic mechanism |
| L4 | First audit | High | High | Agree: robustness battery absent | Null result unchallenged |
| L5 | First audit | Medium | Low | Downgrade: docstring mismatch is cosmetic; LaTeX table and code are correct | Documentation only |
| L6 | First audit | Medium | Medium | Agree: `dvy.fillna(0)` is a defensible but underdocumented choice | Measurement assumption |
| L7 | First audit | Medium | Low | Downgrade: `.last()` picks the last call's matched Compustat quarter, but DivIntensity uses Q4 dvy specifically (joined to all quarters by `_compute_annual_q4_variable`), so the value IS the Q4 annual figure regardless of which call triggers the selection | The Q4-join in the engine means all quarterly rows for the same (gvkey, fyearq) already have the same DivIntensity value; `.last()` just picks any of them |
| L8 | First audit | Medium | Low | Downgrade: naming is confusing but functionally correct; no downstream impact | Documentation only |
| L9 | First audit | Medium | Medium | Agree: unpinned version is a real reproducibility risk | Exact replication blocked |
| L10 | First audit | Medium | Low | Downgrade: OCF_Volatility/CurrentRatio only appear in summary_stats CSV, not in the LaTeX table or regression output. Impact is limited. | Summary stat table only |
| L11 | First audit | Medium | Low | Downgrade: low within-R2 is expected for a hypothesis that turns out null | Not a defect |
| L12 | First audit | Low | Medium | **Upgrade**: Utility should be runnable; its absence is unexplained, not "insufficient data" | 12 missing specs |
| L13 | First audit | Low | Low | Agree | Selection concern for CEO measures |
| L14 | First audit | Low | Low | Agree, but the "file count heuristic" framing is wrong | Housekeeping issue |
| G1 | Red-team | -- | **Critical** | NEW: Finance significant positive coefficients completely unreported | Major omission -- changes the narrative from "universal null" to "null in Main, opposite-sign in Finance" |
| G2 | Red-team | -- | Medium | NEW: Finance .txt files missing from output | Incomplete audit trail |
| G5 | Red-team | -- | Medium | NEW: Mixed star basis in LaTeX table | Reader confusion |
| G7 | Red-team | -- | High | NEW: Main/Finance divergence requires explanation | Thesis interpretation gap |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|--------------------------|----------------|----------|----------|-------------------------------|
| Two-tailed significance for Finance specs | First audit only checked one-tailed significance and concluded "none significant" without examining two-tailed p-values | `model_diagnostics.csv` Finance rows | Critical | Report both one-tailed and two-tailed significance for all specs; flag opposite-direction significance |
| Utility sample feasibility verification | Accepted "insufficient data" without independently testing the threshold against the current panel | `pd.read_parquet` + simulation shows all 12 Utility specs pass thresholds | Medium | Independently verify sample sizes after all filters; report actual N/firms for Utility |
| Output file completeness check | Did not verify that all expected output files (regression .txt per spec) exist | `ls` of output directory shows 12 Main .txt files but 0 Finance | Medium | Count and verify all expected outputs; flag any missing files |
| Finance coefficient interpretation | No discussion of Finance positive significant coefficients or Main vs Finance divergence | Diagnostics CSV | Critical | Analyze and interpret the pattern of results across industry samples |
| LaTeX table star consistency | Did not verify that star notation uses the same p-value basis for all rows | `run_h12_div_intensity.py:491` vs `:503` | Medium | Verify star computation logic; flag inconsistencies |
| `get_latest_output_dir` mechanism | Stated "file count heuristic" without reading the implementation | `path_utils.py:254-312` | Low | Read and correctly describe the resolution mechanism |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Stage 3: `python -m f1d.variables.build_h12_div_intensity_panel` | Y | Not re-run (existing artifact inspected) | Y: requires master manifest + linguistic variables + raw Compustat | Medium | First audit correctly flags upstream dependencies |
| Stage 4: `python -m f1d.econometric.run_h12_div_intensity` | Y | Not re-run (existing outputs inspected) | Y: requires Stage 3 panel at correct path | Medium | First audit correctly flags this |
| Panel path resolution | Y | Y | N: timestamp-sorted, not file-count | Low | First audit's "file count heuristic" claim is wrong |
| Output completeness after run | N | Y | Y: Finance .txt files missing despite CSV results | Medium | First audit did not verify output file inventory |
| Utility sample availability | Partial (claims skipped) | Y | N: data is sufficient for Utility | Medium | First audit did not verify the threshold computation |
| Environment: `linearmodels` version | Y (flags unpinned) | N | Y: version affects exact coefficients | Medium | Correctly identified as reproducibility risk |
| End-to-end determinism | Y (claims deterministic given inputs) | Not tested | Possible: PanelOLS is deterministic, but OS/version effects on floating point | Low | Reasonable claim |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Identification threats | Y | Reverse causality, OVB, zero-inflation covered | No major gap | -- |
| Inference / clustering | Y | Firm-clustered SEs identified; no two-way clustering noted | Finance low-cluster-count caveat missed | Low |
| FE and within-variation | Y | Absorbed constant-zero firms documented | Good coverage | -- |
| Timing alignment | Y | Lead DV correct; look-ahead bias ruled out | -- | -- |
| Post-treatment controls | Y | No post-treatment issue identified (correct) | -- | -- |
| Reverse causality | Y | Flagged as Medium severity | -- | -- |
| Endogenous sample selection | Y | CEO 25% missing rate flagged | -- | -- |
| Model-family-specific threats | Partial | Zero-inflation and Tobit alternative discussed | Missing: PPML/Poisson for count-like DV; fractional logit for bounded DV | Low |
| Robustness adequacy | Y | 11-dimension robustness gap table | Thorough | -- |
| Interpretation discipline | **Partial** | Correctly flags causal verb misuse and null result | **Fails to flag the Finance opposite-sign significant result as an interpretation issue** | High |
| Academic-integrity / auditability | Partial | Docstring mismatch, unpinned version flagged | Misses Finance .txt output gap; misses mixed-star LaTeX issue | Medium |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|----------------|-----|
| Finance "none significant" claim is factually wrong | 8/12 Finance specs have p_two < 0.05 (positive beta1) | Critical | A committee relying on this audit would believe all results are null, missing a significant opposite-direction effect | Correct the spec register; add two-tailed significance reporting |
| Utility skip explanation is unverified | First audit states "insufficient data" but does not compute the post-filter sample sizes | Medium | Creates a false impression that the data limitation is known and understood | Verify and correctly document the skip reason |
| `get_latest_output_dir` mechanism misdescribed | Code uses timestamp sorting, not file count | Low | Minor factual error that does not affect conclusions | Correct the description |
| First audit does not clearly separate one-tailed from two-tailed significance in the spec register | Section H labels coefficients as "none significant" without specifying which test | Medium | "None significant" is ambiguous -- true one-tailed but false two-tailed for Finance | Always specify "not significant in H12 direction (one-tailed)" and separately report two-tailed significance |
| Evidentiary trail is generally strong | 20 verification steps logged with specific commands | -- | Positive: first audit is largely traceable | -- |
| Fact/judgment separation is adequate | Uses explicit labels: "VERIFIED IMPLEMENTATION ISSUE", "REFEREE CONCERN" | -- | Positive: clear labeling | -- |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance on first audit? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|----------------|---------------------------------------|
| RT-1 | First-audit factual error | Estimation results | Y | Critical | H12.md Section H, spec register M7a-M12b | Finance sample described as "none significant" when 8/12 specs have two-tailed p < 0.05 (positive beta1) | `model_diagnostics.csv`: Finance Manager_QA DivIntensity p_two=0.022, CEO_Weak_Modal p_two=0.011, Manager_Pres DivIntensity_lead p_two=0.003, etc. | Committee would not know about significant opposite-direction Finance results | Correct spec register; report two-tailed significance; discuss Main vs Finance divergence | **Y** |
| RT-2 | First-audit omission | Interpretation | Y | High | H12.md Sections K6, N | No discussion of Main (null) vs Finance (positive significant) divergence | Diagnostics CSV shows clear pattern difference | Referee would immediately question this pattern | Add explicit analysis comparing Main and Finance results; test interaction effects | **Y** |
| RT-3 | First-audit unsupported claim | Utility sample | Y | Medium | H12.md Section H, L12 | Claims Utility skipped for "insufficient data (<200 obs or <50 firms)" but latest panel yields 640-1099 obs and 60-80 firms per spec | Independent simulation on latest panel artifact | Utility skip reason is unexplained; 12 regressions potentially missing | Verify why Utility was actually skipped; rerun if possible | N |
| RT-4 | First-audit factual error | Reproducibility | Y | Low | H12.md Section B | Claims `get_latest_output_dir()` uses "file count heuristic" | `path_utils.py:300-301`: timestamp-sorted | Minor factual error | Correct description | N |
| RT-5 | Underlying implementation issue missed by first audit | Output integrity | Y | Medium | Output directory | Finance regression .txt files not saved despite diagnostics CSV recording Finance results | `ls` of `outputs/econometric/h12_div_intensity/2026-03-05_210406/`: 0 Finance files | Incomplete audit trail; Finance regression summaries not preserved | Investigate and fix output saving; rerun | N |
| RT-6 | First-audit omission | LaTeX table | Y | Medium | `run_h12_div_intensity.py:491,503` | Mixed star basis: one-tailed p for beta1, two-tailed p for controls | Code inspection | Reader confusion about significance interpretation | Standardize star basis across all table rows | N |
| RT-7 | First-audit omission | Documentation | Y | Low | `div_intensity.py:4` | Builder docstring says "dvy_Q4 / atq" but engine uses atq_{t-1} (lagged) | `_compustat_engine.py:1077-1084` vs `div_intensity.py:4` | Secondary docstring error | Update builder docstring | N |
| RT-8 | First-audit severity error | Issue register | Y | Medium | H12.md L7, L12 | L7 (.last() aggregation) overrated at Medium; L12 (Utility skip) underrated at Low | L7: Q4-join in engine makes `.last()` moot for DivIntensity; L12: Utility is actually runnable | Misallocated reviewer attention | Downgrade L7 to Low; upgrade L12 to Medium | N |
| RT-9 | Underlying implementation issue underplayed by first audit | Inference | Y | Medium | Finance specifications | Finance cluster counts for CEO specs: 258-291 firms | `model_diagnostics.csv` n_firms column | Significant results rest on moderate cluster counts | Report cluster counts; consider wild bootstrap | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The Finance sample shows significant positive effects of uncertainty on dividend intensity** (8/12 specs, p_two < 0.05). This is the opposite direction from H12 and is an important finding that changes the overall narrative from "universal null" to "null in non-financial firms, significantly positive in financial firms."

2. **The Utility sample is runnable with the current panel.** A committee would believe Utility data is insufficient, when in fact 12 additional regressions are feasible and their absence is unexplained.

3. **The LaTeX table uses different p-value bases for different coefficient rows** (one-tailed for beta1, two-tailed for controls), which could mislead readers about relative significance.

4. **The Finance regression .txt files are missing from the output directory**, meaning the full PanelOLS summaries (with R-squared, F-stats, residual diagnostics) for the significant Finance results are not preserved.

5. **The `get_latest_output_dir` function is robust, not heuristic-based.** A committee might worry about wrong-panel loading based on the first audit, but this concern is unfounded.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|----------|-------------------|----------------|--------|-----------------|
| 1 | **Correct Finance "none significant" claim**; report two-tailed significance; discuss 8/12 significant positive coefficients | Factually wrong characterization of results; changes narrative from universal null to heterogeneous | Low | Critical |
| 2 | **Add Main vs Finance divergence analysis** to K6 interpretation section | Referee would immediately ask about pattern differences across samples | Medium | High |
| 3 | **Verify and correct Utility skip explanation**; rerun Utility regressions if possible | 12 missing regressions; false claim about data insufficiency | Medium | Medium |
| 4 | **Correct `get_latest_output_dir` description** from "file count heuristic" to timestamp sorting | Factual error in reproducibility section | Trivial | Low |
| 5 | **Flag Finance .txt output gap** and mixed LaTeX star basis | Output completeness and table interpretation integrity | Low | Medium |
| 6 | **Recalibrate L7 and L12 severity** per Section H above | Issue priority alignment | Trivial | Low |

---

## P. Final Red-Team Readiness Statement

- **Can the first audit be trusted as a standalone referee-quality document?** NO -- not until the Finance significance claim is corrected. The factual error about Finance results being "none significant" is a material mischaracterization that would mislead a committee or referee about the pattern of results.

- **Biggest factual weakness:** The claim that all 24 specifications show null results with no significant coefficients. In fact, 8 of 12 Finance specifications have significant positive coefficients (two-tailed p < 0.05), representing the opposite direction of H12. This transforms the result narrative.

- **Biggest completeness weakness:** Absence of any discussion of the Main vs Finance divergence. A hostile referee would immediately note that null results in non-financial firms but significant positive results in financial firms requires explanation -- potentially reflecting different payout norms, regulatory constraints, or agency dynamics in financial institutions.

- **Biggest severity/judgment weakness:** The first audit correctly identifies zero-inflation (L1) as Critical but fails to recognize the Finance opposite-sign finding as equally important for thesis interpretation. A null everywhere is simpler to present than a heterogeneous pattern.

- **Single most important missed issue:** The significant positive Finance coefficients (G1/RT-1). This is not a statistical nuance -- it is a substantive finding that the first audit entirely missed by only checking one-tailed significance.

- **Single most misleading claim:** "0 of 24 completed regressions support H12" and the Finance spec register entries stating "none significant." While technically correct for the one-tailed H12 test, these statements actively conceal that uncertainty significantly predicts HIGHER dividend intensity in financial firms, which is a finding that demands interpretation.

- **What should a thesis committee believe after reading this red-team review?** The H12 suite's implementation is technically sound (correct estimator, FE, clustering, timing). The first-layer audit is well-structured and catches most issues but contains a critical factual omission: the Finance sample shows robust positive effects of uncertainty on dividend intensity, opposite to the H12 hypothesis. The thesis cannot simply present H12 as a uniform null result. The zero-inflation concern remains the primary econometric threat. After correcting the Finance significance reporting and addressing the zero-inflation modeling, the suite is salvageable.
