# H4 Suite: Second-Layer Red-Team Audit

**Suite ID:** H4
**Red-team date:** 2026-03-15
**Object under audit:** First-layer audit at `docs/provenance/H4.md`
**Auditor posture:** Hostile-but-fair, independent verification

---

## A. Red-Team Bottom Line

The first-layer audit is a competent, thorough document that correctly identifies most of the mechanical implementation details and several key econometric concerns. However, it contains factual errors in its significance counts, misses a critical falsification failure (Lev_lead is significant for Manager_Clarity_Residual in Main, and MORE significant than Lev_lag in Finance and Utility subsamples), understates the severity of the multiple-testing problem, and fails to flag a significant disclosure issue in the LaTeX tables (stars based on one-tailed p-values without disclosure). It also misses the negative within-R-squared values present in several models, which indicate model misspecification. The first audit's final verdict of "THESIS-STANDARD AS IMPLEMENTED (for descriptive association)" is arguably too generous given the falsification failures and the full pattern of results across all 60 models.

**Overall grade for first audit: PARTIALLY RELIABLE**

**Suite as implemented: SALVAGEABLE WITH MAJOR REVISIONS**

**Risk characterization:** The first audit **understated risk** on balance. While it correctly flagged multiple-testing and reverse-causality concerns as high-severity, it failed to notice that the falsification check (Lev_lead) actually produces significant results that undermine the theoretical story, and it understated the total count of significant tests.

---

## B. Scope and Objects Audited

| Item | Path / identifier |
|------|-------------------|
| Suite ID | H4 |
| Suite entrypoint | `src/f1d/econometric/run_h4_leverage.py` |
| Panel builder | `src/f1d/variables/build_h4_leverage_panel.py` |
| First-layer audit | `docs/provenance/H4.md` |
| Panel utils | `src/f1d/shared/variables/panel_utils.py` |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` |
| CEO clarity builder | `src/f1d/shared/variables/ceo_clarity_residual.py` |
| Latest panel parquet | `outputs/variables/h4_leverage/2026-03-09_221758/h4_leverage_panel.parquet` |
| Latest diagnostics CSV | `outputs/econometric/h4_leverage/2026-03-09_221928/model_diagnostics.csv` |
| Latest LaTeX tables | `outputs/econometric/h4_leverage/2026-03-09_221928/h4_leverage_table_*.tex` |
| Run manifest | `outputs/econometric/h4_leverage/2026-03-09_221928/run_manifest.json` |
| Sample attrition | `outputs/econometric/h4_leverage/2026-03-09_221928/sample_attrition.csv` |
| 12 prior run directories | `outputs/econometric/h4_leverage/` (12 timestamped dirs) |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | Pass | Correct: PanelOLS, entity+time FE, clustered SEs, 8 DVs x 3 lev_vars x 3 samples | Accurately described |
| Reproducibility commands | Pass | Commands verified runnable; correct module paths | H0.3 dependency correctly flagged |
| Dependency tracing | Pass | All 17 builders listed with correct class names | Thorough |
| Raw data provenance | Partial | Raw counts marked UNVERIFIED; match rates stated but not independently confirmed | Honest about gaps |
| Merge/sample audit | Pass | Zero-row-delta enforcement verified; merge table complete | Correct |
| Variable dictionary completeness | Pass | All 22 variables documented with formulas and sources | firm_maturity docstring error correctly caught |
| Outlier/missing-data rules | Pass | Winsorization layers documented; firm_maturity extremes flagged | Adequate |
| Estimation spec register | **Partial** | 8 Main/Lev_lag specs listed with correct betas/p-values; Lev_t and Lev_lead results only described as "in diagnostics" | Did not surface the falsification failure in Lev_lead |
| Verification log quality | Pass | 16 verification checks listed with specific outputs | Adequate |
| Known issues section | **Partial** | 8 issues correctly identified; severity calibration mostly reasonable | Missed Lev_lead falsification failure; missed one-tailed star disclosure |
| Identification critique | Pass | Reverse causality, OVB, simultaneity, endogenous selection all flagged | Thorough |
| Econometric implementation critique | **Partial** | Calendar-year/fiscal-year mismatch correctly flagged; one-tailed test verified | Missed negative within-R2; missed star-disclosure issue |
| Robustness critique | Pass | Comprehensive table of missing robustness checks | Correctly identified multiplicity as primary concern |
| Academic-integrity critique | Partial | Warning suppression, stale artifacts, manifest mismatch flagged | Missed Finance/Utility txt file absence |
| Severity calibration | **Partial** | Multiple-testing and reverse causality correctly ranked High | Understated by not examining full 60-model result pattern |
| Final thesis verdict support | **Fail** | "THESIS-STANDARD AS IMPLEMENTED" too generous given falsification failures | See Section G |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|-------------------|---------|-----------|----------|------------------|-------|
| C1 | Panel has 112,968 rows, 30 columns | A1, I | Y | `pd.read_parquet` confirms 112,968 x 30 | Correct | |
| C2 | file_name is unique | E1, I | Y | `p["file_name"].is_unique` = True | Correct | |
| C3 | 2,429 unique firms | I | Y | `p["gvkey"].nunique()` = 2,429 | Correct | |
| C4 | Sample: Main=88,205; Finance=20,482; Utility=4,281 | I | Y | `p["sample"].value_counts()` matches | Correct | |
| C5 | Primary keys are gvkey + year | A1 | **N** | 83,993 duplicate (gvkey,year) pairs; panel is call-level with ~3.9 calls per (gvkey,year) | **Misleading** | The first audit states estimation unit is "individual earnings call" (correct) but then says primary keys are "gvkey + year" which is NOT unique. The actual observation unit is file_name. PanelOLS receives a non-unique MultiIndex. |
| C6 | Main/Lev_lag: Mgr QA beta=0.0008, CEO QA beta=-0.029, Mgr Pres beta=-0.055, CEO Pres beta=-0.042 | H, I | Y | model_diagnostics.csv matches exactly | Correct | |
| C7 | "2 out of 24 primary tests are significant at 5%" | K6, N | **Partial** | 2/8 Main/Lev_lag models significant; but 3/24 Main models significant (includes Manager_Clarity_Residual with Lev_lead at p=0.050) | **Understated** | The first audit counted only Main/Lev_lag as "primary" which is defensible but inconsistent with its own "24 primary tests" framing |
| C8 | Lev_lag coverage 93.3% | C | **N** | Actual: 105,380/112,968 = 93.3% matches the first audit's claim for full panel, but Main-sample Lev_lag coverage is 82,252/88,205 = 93.3%. This is consistent. | Correct on percentage but verified differently | |
| C9 | Cluster counts 1,303-1,805 for Main/Lev_lag | I | Y | Matches model_diagnostics.csv | Correct | |
| C10 | Within-R2 "0.0002 to 0.0224" | I | **Partial** | Main/Lev_lag range matches, but across all 60 models within-R2 goes to -0.000437 (negative) | **Missed negative R2** | Negative within-R2 indicates model fits worse than within-group mean |
| C11 | One-tailed test correctly implemented | K3 | Y | Code line 240: `p1_one = p_two/2 if beta < 0 else 1 - p_two/2` | Correct | |
| C12 | Lev fillna(0) codes missing debt as zero | J4, K4 | Y | Code line 1032: `comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)` | Correct; no both-NaN guard unlike TobinsQ at line 623-624 | |
| C13 | firm_maturity docstring says RE/TE but code computes RE/AT | J3, K4 | Y | Docstring line 775: "RE / TE"; code line 840: `req / atq` | Correct | |
| C14 | Lev_lead "included but not formally compared" as falsification | K5 | **Partial** | Lev_lead IS included and results ARE in diagnostics. But first audit did not examine those results. Lev_lead produces MORE significant results than Lev_lag in Finance/Utility. | **Critical omission** | |
| C15 | Utility has 69-82 clusters | I, L15 | Y | Matches model_diagnostics.csv | Correct | |
| C16 | "THESIS-STANDARD AS IMPLEMENTED (for descriptive association)" | K1, N | **N** | Given that Lev_lead (future leverage) is significant in several specs and more significant than Lev_lag in Finance/Utility, even the descriptive-association claim is weakened | **Overstated** | |
| C17 | 60 models actually run (of 72 potential) | C | Y | model_diagnostics.csv has 60 rows; Main=24, Finance=18, Utility=18 | Correct; 12 skipped (low N in Finance/Utility) | |
| C18 | CEO_Clarity_Residual coverage 42,441 | D | Y | Panel parquet confirms 42,441 non-null | Correct | |
| C19 | 12 stale output directories exist | B | Y | 12 timestamped dirs in `outputs/econometric/h4_leverage/`; 7 in `outputs/variables/h4_leverage/` | Correct; stale artifact concern valid | |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim/statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|-----------------|------------------------|----------|-----------------|----------------------|
| E1 | "2 out of 24 primary tests are significant at 5%, which is close to the expected false positive rate (24 x 0.05 = 1.2)" (K6) | Actually 3/24 Main models are significant (Mgr Pres/Lev_lag, CEO Pres/Lev_lag, Mgr Clarity Residual/Lev_lead). The framing of "24 primary tests" includes all leverage timings, but the count of 2 only covers Lev_lag. | Medium | Examination of all 24 Main results | "3 of 24 Main-sample models are significant at 5% one-tailed; 12 of 60 total models are significant across all samples" |
| E2 | "Expected false positives ~1.2" (K6) | Under the null, expected false positives at 5% one-tailed from 24 tests is 1.2; from 60 tests it is 3.0. The 12 actually significant is far above chance across all 60 models. | Medium | Full counting of 60 tests | "Expected false positives: 1.2 (of 24 Main) or 3.0 (of 60 total); observed: 3 (Main) or 12 (total)" |
| E3 | "H4 is supported at p < 0.05 only for Presentation measures" (H) | This is only true for Main/Lev_lag. Across the full result set, QA measures ARE significant for Finance (Lev_t, Lev_lead) and Utility (Lev_t, Lev_lead). | Medium | Examination of Finance/Utility results | "In the Main sample with Lev_lag, only Presentation measures are significant. Finance and Utility show significant QA effects with contemporaneous and forward leverage." |
| E4 | "Lev_lead included but not formally tested against Lev_lag" (K5) | While technically true that no formal Hausman-type comparison exists, the first audit did not even REPORT the Lev_lead coefficients, missing that they are MORE significant than Lev_lag in several specs. | High | Lev_lead result examination | "Lev_lead produces 5 significant results in Utility, 4 in Finance, and 1 in Main — equal or greater than Lev_lag. This constitutes a falsification failure." |
| E5 | "THESIS-STANDARD AS IMPLEMENTED (for what it estimates — descriptive panel association)" (K1) | This verdict does not account for the falsification failure or the one-tailed star disclosure issue. | High | Full result-pattern analysis | "SALVAGEABLE WITH MAJOR REVISIONS — the Lev_lead falsification failure and undisclosed one-tailed stars must be addressed before thesis submission." |
| E6 | Stars in LaTeX tables described as standard significance markers (K3) | The first audit verified the one-tailed p-value computation but did not flag that the LaTeX tables use one-tailed p-values for stars without disclosing this in the table notes. | Medium | Inspection of table code and output | "Stars in all three LaTeX tables are based on one-tailed p-values but table notes do not disclose this. This inflates apparent significance." |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why it appears false/overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|-------------------------------|----------|------------------------|----------------|
| F1 | J5: "Clarity residuals reduce sample by 50-63%" rated as High | While the sample reduction is real, calling it "High" severity for a variable that shows null results anyway is arguably overstated. The clarity residual models are supplementary and non-significant. | model_diagnostics.csv: CEO_Clarity_Residual p=0.155, Mgr_Clarity_Residual p=0.385 (Main/Lev_lag) | Low | Medium severity is more appropriate since the results are null regardless of sample selection concerns |
| F2 | "within-R2 0.0002 to 0.0224 (very low, typical for linguistic DVs with firm FE)" | Described as "typical" without further concern, but some models have NEGATIVE within-R2 (-0.000437). The first audit did not actually notice the negative values. While low R2 is common, negative within-R2 indicates the model is worse than the within-group mean. | model_diagnostics.csv full range | Low | This is not so much a false positive as a missed concern; the "typical" framing normalizes a genuine problem |

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|--------------------------|-------------|-----------------|
| G1 | Falsification failure | Lev_lead (future leverage) produces MORE significant results than Lev_lag in Finance (4 significant) and Utility (5 significant) subsamples. In Main, Lev_lead produces 1 significant result (Manager_Clarity_Residual, p=0.050). | model_diagnostics.csv: Utility/Lev_lead has 5 significant models vs Lev_lag with 0; Finance/Lev_lead has 4 vs Lev_lag with 0 | **Critical** | First audit noted Lev_lead was "included but not formally compared" (K5, L13) but never actually examined the Lev_lead results. | If future leverage predicts current speech better than lagged leverage, the "discipline" mechanism is falsified. Firms that WILL become more leveraged speak less vaguely, suggesting reverse causality or confounding. | Must report Lev_lead results explicitly in thesis; formal coefficient comparison required; may need to abandon or heavily caveat the discipline interpretation. |
| G2 | Star disclosure | LaTeX tables (all three) apply significance stars using one-tailed p-values (`beta1_p_one`) but table notes do not disclose this. Standard practice uses two-tailed p-values unless explicitly noted. | `run_h4_leverage.py` line 350: `fmt_coef(r["beta1"], r["beta1_p_one"])`. Table note says "Standard errors are clustered at the firm level" with no mention of one-tailed tests. | **High** | First audit verified the one-tailed computation was correct (K3) but did not check whether the LaTeX tables disclosed this. | A reader/referee would assume two-tailed stars and conclude more significance than actually present. For CEO_QA_Uncertainty_pct, the two-tailed p-value is 0.168, not significant at any conventional level, but it receives a star (*) in the table. | Add explicit note: "Significance levels based on one-tailed tests given directional hypothesis" or switch to two-tailed stars with one-tailed p-values reported separately. |
| G3 | Negative within-R2 | Some models have negative within-R-squared (-0.000437), meaning the model fits worse than a within-group-mean constant. | model_diagnostics.csv: minimum within_r2 across all 60 models is -0.000437 | Medium | First audit reported within-R2 as "0.0002 to 0.0224" using only the Main/Lev_lag range. | Negative within-R2 indicates the covariates (including leverage) are pure noise for some DV/sample combinations. This is not just low explanatory power; it is model misspecification evidence. | Report negative within-R2 values; discuss implications for the leverage-speech relationship. |
| G4 | Primary key misstatement | First audit says primary keys are "gvkey + year" but there are 83,993 duplicate (gvkey,year) pairs out of 112,968 rows. The data has ~3.9 calls per (gvkey,year). | `p.duplicated(subset=['gvkey','year']).sum()` = 83,993 | Medium | First audit correctly stated the estimation unit is "individual earnings call" but contradicted itself by listing primary keys as gvkey+year. | PanelOLS receives a non-unique MultiIndex. While this is technically valid (linearmodels handles it), the entity FE is at the gvkey level, meaning the year FE has multiple call-level obs per cell. This is a repeated-obs design within entity-time cells. | Correct primary key description to "file_name (unique call identifier)" with panel index "(gvkey, year) with multiple obs per cell". |
| G5 | Finance/Utility regression txt files missing | The latest output directory has 24 regression_results_*.txt files, all for the Main sample. Finance and Utility models are in model_diagnostics.csv (36 models) but their individual regression summaries are not saved as txt files. | `ls outputs/econometric/h4_leverage/2026-03-09_221928/regression_results_*` shows 24 files, all with "Main" in filename; `grep -c "Finance\|Utility"` = 0 | Low-Medium | First audit listed "33 files" in verification log item 14 but did not check that Finance/Utility summaries were missing. | Full regression summaries (with all coefficients, not just leverage) are lost for 36 models. Only the diagnostics CSV row is preserved. | Debug why Finance/Utility txt files are not being written, or document this as intentional. |
| G6 | Within (gvkey,year) variation in controls | Multiple calls per (gvkey,year) can map to different Compustat quarters via merge_asof, creating within-cell variation in financial controls (Size, Lev, etc.). Std(Lev_lag) within (gvkey,year) has mean=0.020, max=1.08. | `main_valid.groupby(['gvkey','year'])['Lev_lag'].std().describe()` | Low | Not flagged because the first audit did not investigate within-cell variation. | Minor: the variation is small on average, but for some cells it is substantial. This means financial controls are not truly annual even though year FE is annual. | Document; not necessarily a problem but should be acknowledged. |
| G7 | Full result pattern undermines selective reporting concern | First audit (K6) warned about selective reporting of Presentation results. But the FULL pattern is worse: Utility and Finance show strong Lev_lead effects on QA measures (exactly where Lev_lag fails), suggesting the relationship runs from future leverage to current speech, not past leverage to current speech. | model_diagnostics.csv: Utility Lev_lead significant for Mgr QA (p=0.001), CEO QA (p=0.033), Mgr Weak Modal (p=0.005) | **Critical** | First audit focused only on Main/Lev_lag results and did not examine the cross-sample, cross-timing pattern. | The full result pattern is more consistent with reverse causality or confounding than with a leverage discipline channel. | Thesis must present the full 60-model result pattern and address why Lev_lead dominates. |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|------------------|---------------|
| L1 | First audit | High | **Critical** | Lev_lead results show reverse-causality is not merely theoretical; it is empirically dominant in subsamples | Discipline interpretation is falsified in Finance/Utility |
| L3 | First audit | High | **Critical** | Multiple-testing problem is worse than stated: 12/60 significant but pattern favors Lev_lead over Lev_lag | Core finding is not robust to proper multiplicity control |
| G1 | Red-team | N/A | **Critical** | New: Lev_lead falsification failure across subsamples | Thesis-killing if not addressed |
| G2 | Red-team | N/A | **High** | New: Undisclosed one-tailed stars in tables | Academic integrity risk |
| L2 | First audit | High | High | OVB concern stands | Unchanged |
| L5 | First audit | Medium | Medium | Calendar/fiscal year mismatch stands | Unchanged |
| L6 | First audit | Medium | Medium | Lev fillna(0) concern stands | Unchanged |
| L4 | First audit | Medium | Medium | Single-dimension clustering stands | Unchanged |
| G3 | Red-team | N/A | Medium | New: Negative within-R2 | Model misspecification evidence |
| G4 | Red-team | N/A | Medium | New: Primary key misstatement | Internal inconsistency in first audit |
| L7 | First audit | Medium | Low-Medium | Clarity residual sample reduction; downgraded because results are null | Less concerning given null results |
| L8 | First audit | Medium | Medium | No alternative FE stands | Unchanged |
| L9 | First audit | Medium | Medium | No subperiod robustness stands | Unchanged |
| L10 | First audit | Medium | Low | firm_maturity docstring error | Documentation, not substantive |
| L11 | First audit | Low-Medium | Low | firm_maturity extremes | Minor |
| L12 | First audit | Low-Medium | Low-Medium | Warning suppression stands | Unchanged |
| L13 | First audit | Low-Medium | **Critical** (merged with G1) | No placebo test — now known to FAIL | Merged with G1 |
| L14 | First audit | Low | Low | Manifest file reference mismatch | Minor |
| L15 | First audit | Low | Low | Small Utility clusters | Subsumed under G1 |
| G5 | Red-team | N/A | Low-Medium | Finance/Utility txt files missing | Reproducibility gap |

---

## I. Completeness Gaps in the First Audit

| Missing/incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|------------------------|----------------|----------|----------|-------------------------------|
| Lev_lead and Lev_t results not reported | First audit listed results only for Main/Lev_lag (8 models) and described Lev_t/Lev_lead as "in diagnostics" | Section H: only Lev_lag betas shown; Lev_t/Lev_lead marked as "(in diagnostics)" | **Critical** | Full table of all 24 Main results (8 DVs x 3 lev_vars) plus key Finance/Utility results |
| Finance/Utility result patterns not analyzed | First audit noted "larger negative effects on CEO measures but not significant" for Finance and "very small samples, results unreliable" for Utility | Section I item 13 | High | The Finance/Utility subsample pattern (strong Lev_lead > Lev_lag) is material to the hypothesis interpretation |
| One-tailed star disclosure not checked | First audit verified one-tailed p-value computation but did not inspect the LaTeX table output for star basis | Section K3 | High | Explicit check of what p-value feeds into the star function in the LaTeX tables |
| Negative within-R2 not reported | First audit stated within-R2 range only for Main/Lev_lag models | Section I item 12 | Medium | Full within-R2 range across all 60 models including negative values |
| Finance/Utility regression txt files not verified | First audit counted 33 output files but did not verify completeness against the 60 model runs | Section I item 14 | Low-Medium | Check that all models producing diagnostics rows also produce regression_results txt files |
| Winsorization note in LaTeX table | Table note says "Variables are winsorized at 1%/99% by year" but this applies only to Compustat vars; linguistic vars are 0%/99% per calendar year; clarity residuals are not winsorized | Table output inspection | Low | Correct the note to accurately describe the heterogeneous winsorization scheme |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Run H0.3 (clarity residuals prerequisite) | Y (B) | Partial — command provided but not tested | Y — no orchestrator enforces ordering | Medium | If H0.3 fails or uses stale data, clarity residual specs silently have zero obs |
| Build panel (`python -m f1d.variables.build_h4_leverage_panel`) | Y (B) | Y — latest panel exists and is valid | N | Low | |
| Run regressions (`python -m f1d.econometric.run_h4_leverage`) | Y (B) | Y — latest diagnostics exist | N | Low | |
| `get_latest_output_dir()` resolution | Y (B) | Y — 12 stale dirs exist | Y — stale panel could silently feed wrong data | Medium | First audit correctly flagged |
| Raw data placement (`inputs/`) | Y (B) | N — cannot verify without raw data | Y — manual step | Medium | First audit correctly flagged |
| Environment packages | Y (B) | Partial — versions listed but Python version is vague (">=3.8, tested on 3.x") | N | Low | Should specify exact Python version |
| Output completeness verification | Partial (B) | Partial — 33 files listed but Finance/Utility txt files missing | Y — 36 regression summaries are missing from output | Low-Medium | Finance/Utility models produce diagnostics rows but not txt files |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|-----------------------|----------|
| Identification threats | Partial | Reverse causality, OVB, simultaneity flagged correctly | Did not examine Lev_lead results which empirically demonstrate reverse causality concern | Critical |
| Inference / clustering | Y | Entity clustering documented; small-cluster Utility concern flagged | Could have also flagged that ~3.9 obs per entity-year cell means clustering at entity is computing SEs over correlated within-cell residuals | Low |
| FE and within-variation | Partial | Calendar-year vs fiscal-year mismatch flagged | Did not note that with multiple obs per (gvkey,year), year FE absorbs less variation than it would in a firm-year panel; also did not flag negative within-R2 | Medium |
| Timing alignment | Y | Lev_lag fiscal-year timing documented; approximate alignment noted | Adequate | |
| Post-treatment controls | Y | Presentation-as-control-for-QA concern flagged (K2) | Appropriately low severity | |
| Reverse causality | **Fail** | Flagged as theoretical concern but did not examine the empirical evidence (Lev_lead results) | Lev_lead falsification failure is the most important finding for this suite | Critical |
| Endogenous sample selection | Y | CEO missingness and clarity residual subsample flagged | Adequate | |
| Model-family-specific threats | Partial | Calendar/fiscal year mismatch flagged | Did not discuss implications of call-level panel with entity-year indexing for FE interpretation | Low |
| Robustness adequacy | Y | Comprehensive table of missing robustness checks | Correctly harsh | |
| Interpretation discipline | Partial | Causal language warning appropriate | Should have more forcefully flagged that the Presentation-only significance is theoretically backward (discipline should affect Q&A responses, not scripted presentations) | Medium |
| Academic-integrity / auditability | Partial | Warning suppression, stale artifacts flagged | Missed one-tailed star disclosure issue | High |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|----------------|-----|
| First audit does not present full result pattern | Only Main/Lev_lag results shown; 52 of 60 models described only as "in diagnostics" or single-sentence summaries | High | A committee reading only the first audit would not know that Lev_lead outperforms Lev_lag in subsamples | Show at minimum a summary table of all 60 models, flagging where Lev_lead is significant |
| First audit does not flag one-tailed star disclosure | One-tailed p-values feed into star computation; not flagged | High | A committee would not know that stars in the thesis tables are inflated relative to standard two-tailed convention | Add explicit flag |
| First audit separates facts from judgments | Generally good — uses "VERIFIED" and "REFEREE CONCERN" labels | Low | Adequate | |
| First audit creates traceable evidence trail | 16 verification log entries with specific commands/values | Low | Adequate but could be more systematic | |
| First audit's final verdict is too generous | "THESIS-STANDARD AS IMPLEMENTED" given the unexamined falsification failure | High | A committee relying on this verdict would be misled about the credibility of the leverage-discipline claim | Revise to "SALVAGEABLE WITH MAJOR REVISIONS" |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance on first audit? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|---------------------------------------|
| RT-1 | Underlying implementation issue missed by first audit | Falsification | Y | **Critical** | model_diagnostics.csv, all samples | Lev_lead (future leverage) produces 10 significant models across all samples vs 2 for Lev_lag (Main). In Utility, Lev_lead has 5 significant results, Lev_lag has 0. In Finance, Lev_lead has 4, Lev_lag has 0. | Verified from model_diagnostics.csv | The leverage-discipline mechanism is empirically contradicted: future leverage predicts current speech better than past leverage | Must report full temporal comparison; formal falsification test; likely must abandon or heavily caveat discipline interpretation | **Y** |
| RT-2 | First-audit omission | Star disclosure | Y | **High** | `run_h4_leverage.py` line 350; all three LaTeX tables | Stars use one-tailed p-values without disclosure in table notes | Code line 350: `fmt_coef(r["beta1"], r["beta1_p_one"])`; table note mentions only clustering | Reader assumes two-tailed stars; CEO_QA_Unc appears starred at 10% one-tail but would not be starred at any conventional two-tailed level | Add one-tailed test disclosure to table notes; or use two-tailed stars | **Y** |
| RT-3 | First-audit factual error | Significance count | Y | Medium | K6, N | First audit says "2 out of 24 primary tests significant" but 3/24 Main models are significant (including Mgr_Clarity_Residual with Lev_lead) | model_diagnostics.csv | Understates the scope of significant results and misses that the third is a falsification failure | Correct count; note that one of the three is a Lev_lead (falsification) result | N |
| RT-4 | First-audit omission | Result reporting | Y | High | Section H | Lev_t and Lev_lead results not reported; only described as "(in diagnostics)" | Section H table shows only "in diagnostics" for non-Lev_lag results | Committee cannot evaluate the temporal pattern of results | Add full result table for all leverage timings | **Y** |
| RT-5 | Underlying implementation issue missed by first audit | Negative within-R2 | Y | Medium | model_diagnostics.csv | Some models have negative within-R-squared (-0.000437) | Verified: `main["within_r2"].min()` = -0.000437 | Model fits worse than within-group mean for some DV/sample combinations | Report and discuss; indicates controls are noise for these specs | N |
| RT-6 | First-audit factual error | Primary key | Y | Medium | Section A1 | States primary keys are "gvkey + year" but 83,993 rows have duplicate (gvkey,year) | `p.duplicated(subset=['gvkey','year']).sum()` = 83,993 | Internal inconsistency: estimation unit is correctly stated as "call" but primary key is wrong | Correct to "file_name" as primary key; note (gvkey,year) as panel index with multiple obs per cell | N |
| RT-7 | First-audit severity error | Reverse causality | Y | Critical | L1, L13, K2 | Reverse causality flagged as "High" theoretical concern but not tested empirically; the Lev_lead results constitute empirical evidence of the problem | Lev_lead significant in 10/60 models vs Lev_lag in 2/60 (Main only) | Should have been escalated to Critical with empirical evidence | Upgrade to Critical with empirical falsification evidence | **Y** |
| RT-8 | First-audit unsupported claim | Thesis verdict | Y | High | K1, N | "THESIS-STANDARD AS IMPLEMENTED" not supported given unexamined falsification failures | Full 60-model result pattern | Committee would be misled about suite credibility | Revise to "SALVAGEABLE WITH MAJOR REVISIONS" | **Y** |
| RT-9 | Underlying implementation issue underplayed by first audit | Multiple testing | Y | Critical | K6, L3 | First audit identified multiple testing as "High" but framed it as 2/24; actual pattern is 12/60 with Lev_lead dominating | Full diagnostics CSV | The multiple-testing problem is worse AND directionally problematic (wrong timing dominates) | Upgrade to Critical; note that significance pattern favors wrong direction | **Y** |
| RT-10 | First-audit omission | Finance/Utility files | Y | Low-Medium | Output directory | 36 Finance/Utility regression_results txt files missing from output despite models running | `ls` shows 24 Main-only files; diagnostics CSV has 60 rows | Full regression summaries lost for subsamples | Debug file writing or document as intentional | N |
| RT-11 | First-audit omission | LaTeX note accuracy | Y | Low | Table output | Table note says "winsorized at 1%/99% by year" but this applies only to Compustat vars; linguistic vars are 0%/99%; clarity residuals not winsorized | Code: different engines use different schemes | Minor inaccuracy | Correct table note | N |
| RT-12 | First-audit omission | Interpretation | Y | Medium | K6 | First audit warns Q&A null results are "theoretically more interesting" but does not note the irony that PRESENTATION results are significant: discipline should affect unscripted speech (Q&A), not scripted presentations | Theory implies discipline constrains spontaneous speech; presentation is pre-prepared | Significant Presentation-only results are theoretically backward | Note this explicitly as an interpretation concern | N |

---

## N. What a Committee/Referee Would Still Not Know if They Read Only the First Audit

1. **Lev_lead (future leverage) is a stronger predictor of current speech than Lev_lag (past leverage) in Finance and Utility subsamples.** This is the single most important fact the first audit fails to communicate. It constitutes empirical evidence of reverse causality or confounding that directly contradicts the leverage-discipline mechanism.

2. **Stars in all LaTeX tables are based on one-tailed p-values without disclosure.** A referee reading the tables would overestimate significance levels. The CEO_QA_Uncertainty column appears starred but has a two-tailed p-value of 0.168.

3. **Some models have negative within-R-squared.** The controls including leverage explain less variation than a simple within-group mean for certain DV/sample combinations.

4. **The full 60-model result pattern.** Only 8 of 60 model results are actually reported in the first audit. The other 52 are described only as "in diagnostics" or with one-sentence summaries.

5. **The panel has ~3.9 calls per (gvkey,year) cell.** The stated "primary keys" are not actually unique. This does not invalidate the regressions but changes the interpretation of within-R2 and FE absorption.

6. **The significance pattern is theoretically backward.** Leverage discipline should affect spontaneous Q&A responses, not scripted presentations. The fact that only Presentation measures are significant in Main is inconsistent with the theoretical mechanism.

---

## O. Priority Fixes to the First Audit

| Priority | Fix | Why it matters | Effort | Credibility gain |
|----------|-----|----------------|--------|------------------|
| 1 | **Report full Lev_lead and Lev_t results; flag the falsification failure** | Without this, the first audit conceals the strongest evidence against the hypothesis | Low (data already exists) | Critical — transforms the audit from misleading to informative |
| 2 | **Flag one-tailed star disclosure issue in LaTeX tables** | Academic integrity concern; standard practice requires disclosure | Low | High |
| 3 | **Revise final verdict from "THESIS-STANDARD" to "SALVAGEABLE WITH MAJOR REVISIONS"** | Current verdict does not reflect the full evidence pattern | Low | High |
| 4 | **Correct the "2 out of 24" count to 3/24 Main and 12/60 total** | Factual error in significance counting | Low | Medium |
| 5 | **Add full 60-model summary table or at minimum all 24 Main results** | Committee needs the complete picture | Low-Medium | High |
| 6 | **Correct primary key from "gvkey + year" to "file_name"** | Internal inconsistency | Low | Low |
| 7 | **Report negative within-R2 values** | Model misspecification evidence | Low | Medium |
| 8 | **Add note about theoretically backward Presentation-only significance** | Interpretation discipline | Low | Medium |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
No. The first audit is mechanically competent and catches many real issues, but its failure to examine the Lev_lead results means it misses the single most damaging finding for this hypothesis: that future leverage is a better predictor of current speech than past leverage. A referee relying solely on the first audit would not know that the falsification check fails.

**Biggest factual weakness:**
The count of "2 out of 24 primary tests significant" is wrong (3/24 in Main, 12/60 total), and the first audit does not report the Lev_lead results that constitute a falsification failure.

**Biggest completeness weakness:**
Only 8 of 60 model results are actually reported. The other 52 results, which contain the most damaging evidence against the hypothesis, are described only as "in diagnostics."

**Biggest severity/judgment weakness:**
The final verdict of "THESIS-STANDARD AS IMPLEMENTED (for descriptive association)" is not justified given the unexamined falsification failure. Even the descriptive-association claim is weakened when future leverage predicts current speech better than past leverage.

**Single most important missed issue:**
The Lev_lead falsification failure. In Utility, 5 of 6 Lev_lead models are significant while 0 of 6 Lev_lag models are significant. In Finance, 4 of 6 Lev_lead models are significant while 0 of 6 Lev_lag models are significant. This pattern is devastating for the leverage-discipline interpretation.

**Single most misleading claim:**
"THESIS-STANDARD AS IMPLEMENTED" in the final verdict. This is the claim most likely to mislead a committee into believing the suite's results are credible for thesis purposes without revision.

**What should a thesis committee believe after reading this red-team review?**
The H4 suite is technically competent in its implementation (correct estimator, proper clustering, validated panel construction) but its results do not support the leverage-discipline hypothesis. The falsification check (Lev_lead) produces stronger results than the primary specification (Lev_lag), particularly in Finance and Utility subsamples. The LaTeX tables use undisclosed one-tailed p-values for star notation. The within-R-squared values are near zero or negative for most specifications. The thesis should either (a) present the full result pattern honestly and reframe the finding as a null result with an interesting reverse-timing pattern that warrants future investigation, or (b) fundamentally redesign the identification strategy with an instrument or quasi-experimental setting. The first-layer audit, while competent on mechanical details, must be revised to surface the falsification failure before it can serve as a reliable referee document.
