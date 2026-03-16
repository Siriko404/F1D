# H6 Suite: Second-Layer Red-Team Audit

**Suite ID:** H6
**Red-team audit date:** 2026-03-15
**Auditor posture:** Adversarial, fresh-context, independent verification
**First-layer audit under review:** `docs/provenance/H6.md` (git commit `43f12b0`)

---

## A. Red-Team Bottom Line

The first-layer audit is **MATERIALLY FLAWED**. It documents a version of the code that no longer exists. The suite underwent a major refactoring after the audit was written (commit `cf25167`), which changed the key independent variable from lagged CCCL (`shift_intensity_mkvalt_ff48_lag`, t-1) to contemporaneous CCCL (`shift_intensity_mkvalt_ff48`, t), replaced three dependent variables (Weak Modal variants and Uncertainty_Gap) with two Clarity Residual variables, and added three additional controls (earnings_volatility, RD_Intensity, Volatility). The first-layer audit's spec register, variable dictionary, regression results table, hypothesis test definitions, and output file counts are all factually incorrect relative to the current codebase. Additionally, the first audit failed to identify that 8 out of ~26 regressions in the latest run fail with rank-deficiency errors, and that Clarity Residual DVs have 0% coverage outside the Main sample.

**Overall grade for first audit:** MATERIALLY FLAWED

**Suite as implemented:** SALVAGEABLE WITH MAJOR REVISIONS

**Risk assessment:** The first audit **understates risk** on multiple fronts: it does not flag the contemporaneous-treatment timing problem (which worsens reverse causality), does not document the rank-deficiency failures, and overstates the number of successfully estimated models. It also **mixed risk** by correctly identifying the reduced-form vs. IV issue but then documenting results from a superseded run.

---

## B. Scope and Objects Audited

| Object | Path |
|--------|------|
| Suite ID | H6 |
| Suite entrypoint | `src/f1d/econometric/run_h6_cccl.py` |
| Panel builder | `src/f1d/variables/build_h6_cccl_panel.py` |
| First-layer audit | `docs/provenance/H6.md` (git: `43f12b0`) |
| CCCL instrument builder | `src/f1d/shared/variables/cccl_instrument.py` |
| Clarity residual builder | `src/f1d/shared/variables/ceo_clarity_residual.py` |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` |
| Panel utils | `src/f1d/shared/variables/panel_utils.py` |
| Variable config | `config/variables.yaml` |
| Latest panel artifact | `outputs/variables/h6_cccl/2026-03-13_053427/h6_cccl_panel.parquet` |
| Latest econometric output | `outputs/econometric/h6_cccl/2026-03-13_053758/` |
| Audit-era econometric output | `outputs/econometric/h6_cccl/2026-02-27_224404/` |
| Latest run log | `logs/H6_CCCL/2026-03-13_053758/run.log` |
| Git diff (audit to HEAD) | `git diff 43f12b0 HEAD -- src/f1d/econometric/run_h6_cccl.py` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | **Fail** | Code diff shows 7 DVs replaced by 6; key RHS changed from lag to contemporaneous | Audit documents superseded code version |
| Reproducibility commands | Partial | Commands exist but outputs differ from documented counts | Running current code produces 10 models, not 21 |
| Dependency tracing | Partial | Correctly traces manifest, CCCL instrument, Compustat | Misses Clarity Residual dependency on H0.3; misses 3 additional controls |
| Raw data provenance | Pass | CCCL instrument verified at 145,693 rows, 0 duplicates | Consistent with independent check |
| Merge/sample audit | Partial | Zero-delta enforcement correctly documented | But merge table lists merges (#3-6) for Weak_Modal builders no longer in panel builder |
| Variable dictionary completeness | **Fail** | Lists `Uncertainty_Gap`, `Weak_Modal` vars not in current code; omits `Clarity_Residual`, `earnings_volatility`, `RD_Intensity`, `Volatility` | 6 variables wrong/missing |
| Outlier/missing-data rules | Partial | Winsorization rules correct for Compustat/linguistic engines | Does not note 0% Clarity Residual coverage in Finance/Utility |
| Estimation spec register | **Fail** | Documents 7 specs per sample (21 total); actual is 6 per sample with different DVs | Register is entirely stale |
| Verification log quality | **Fail** | Logs reference old run (2026-02-27_224404) with different DVs and lag variable | Results table cannot be reproduced from current code |
| Known issues section | Partial | Pre-trends and coverage issues noted | Misses rank-deficiency errors, contemporaneous-treatment timing, Clarity Residual coverage gap |
| Identification critique | Partial | Correctly flags reduced-form vs. IV mismatch | Underweights contemporaneous-treatment reverse causality after code change |
| Econometric implementation critique | Partial | FE/clustering correctly described | Does not discuss non-unique (gvkey,year) index with PanelOLS |
| Robustness critique | Partial | Pre-trends documented | Does not note that lead1 is significant in current run (p=0.038) |
| Academic-integrity critique | **Fail** | Audit itself is stale — relying on it would mislead a committee | Documenting old results as current is an integrity risk |
| Severity calibration | Partial | Some issues correctly flagged | But stale-documentation issue is the single most severe problem and is not flagged at all |
| Final thesis verdict support | **Fail** | Verdict based on 21-model run with different DVs/RHS variable | Verdict is not supportable from current code |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|-------------------|---------|-----------|----------|------------------|-------|
| C1 | Key RHS is `shift_intensity_mkvalt_ff48_lag` (t-1) | A4, H | **N** | Code line 160: `iv_cols = ["shift_intensity_mkvalt_ff48"]` (contemporaneous) | FACTUAL ERROR | Changed in commit `cf25167` |
| C2 | 7 DVs: 4 Uncertainty_pct + 2 Weak_Modal + Uncertainty_Gap | A3, H | **N** | Code CONFIG lines 83-90: 6 DVs, Clarity Residuals replace Weak_Modal/Gap | FACTUAL ERROR | Code refactored |
| C3 | 5 controls: Size, Lev, ROA, TobinsQ, CashHoldings | A4 | **N** | Code lines 94-103: 8 controls (adds earnings_volatility, RD_Intensity, Volatility) | FACTUAL ERROR | 3 controls missing |
| C4 | 21 regressions (7 DVs x 3 samples) | H | **N** | Latest diagnostics: 10 models; 8 Utility regressions fail with rank-deficiency | FACTUAL ERROR | Count and composition wrong |
| C5 | Panel: 112,968 rows, 25 columns | D | **Partial** | Latest panel: 112,968 rows, 28 columns | Rows correct, columns wrong | 3 additional variables |
| C6 | PanelOLS with EntityEffects + TimeEffects | A2 | **Y** | Code line 201-202 | Correct | Formula approach equivalent |
| C7 | Clustered at firm level | A5 | **Y** | Code line 203: `cov_type="clustered", cluster_entity=True` | Correct | |
| C8 | drop_absorbed=True | A2 | **Y** | Code line 202 | Correct | |
| C9 | Sample split: Main/Finance/Utility by FF12 | A4 | **Y** | Code lines 484-489; `assign_industry_sample` in panel_utils.py | Correct | |
| C10 | min_calls >= 5 filter | A4 | **Y** | Code line 493-498 | Correct, but counts non-null `shift_intensity_mkvalt_ff48` (not lag) | |
| C11 | CCCL merge via gvkey + fyearq (B5 fix) | E | **Y** | `cccl_instrument.py` lines 77-84, 131-137 | Correct | |
| C12 | Zero row-delta enforcement on merges | E | **Y** | `build_h6_cccl_panel.py` lines 230-236 | Correct | |
| C13 | Regression results: Main MgrQA beta=-0.0865, p_one=0.089 | I | **N** | Latest run: beta=-0.1125, p_one=0.015 | OLD results, not reproducible from current code | |
| C14 | Main sample: 88,205 calls | D | **Y** | `panel['sample'].value_counts()`: Main=88,205 | Correct | |
| C15 | CCCL_lag coverage: 76.3% (86,189/112,968) | D, I | **Y** | Independent verification confirms | Correct — but lag variable no longer used in regressions |
| C16 | Pre-trends falsification run for each spec | H | **Partial** | Pre-trends run exists but uses contemporaneous CCCL, not lag | Falsification target changed |
| C17 | H6 partially supported in Finance sample | I | **N** | Latest run shows Main significant (p=0.015), not just Finance | Results completely different with new RHS |
| C18 | One-tailed p-value: `p_two/2` if beta<0, else `1-p_two/2` | Code | **Y** | Code lines 224-226 | Correct lower-tail formula | |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims

| ID | Claim/statement | Why unsupported | Severity | Missing evidence | Corrected formulation |
|----|-----------------|-----------------|----------|------------------|-----------------------|
| U1 | "21 regression outputs (7 DVs x 3 samples)" | Current code has 6 DVs; latest run produced 10 successful models out of ~36 attempts (6 DVs x 3 samples x 2 variants) | Critical | Correct model count from current code | "10 successful regressions (6 DVs x 2-3 samples); 8 Utility regressions failed due to rank deficiency" |
| U2 | "4/21 specifications show significant negative beta" | Based on superseded run with different DVs and RHS | Critical | Current run diagnostics | "In latest run: 2/10 successful specifications show significant negative beta (Main MgrQA p=0.015, Finance MgrQA p=0.033)" |
| U3 | "CCCL_lag (t-1) is key independent variable" | Code uses contemporaneous CCCL (t), not lag | Critical | Code inspection | "CCCL exposure at time t is the key independent variable" |
| U4 | "Panel has 25 columns" | Latest panel has 28 columns | Minor | Panel schema check | "28 columns" |
| U5 | "H6-C: beta(CCCL_lag) < 0 for Uncertainty_Gap" | Uncertainty_Gap no longer exists as a DV | Moderate | Code inspection | Hypothesis H6-C is not tested in current code |
| U6 | Coverage stats for Weak_Modal variables | Variables no longer in panel | Moderate | Code inspection | Replace with Clarity Residual coverage (47.0% and 34.2% overall; 0% in Finance/Utility) |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why false/overstated | Evidence | Severity | Corrected view |
|----|----------------------|---------------------|----------|----------|----------------|
| FP1 | "Finance sample significance may be small-sample noise" | While cluster count is low (436 firms in Finance), this is a reasonable concern, not a false positive | Latest run still shows Finance significance | Low | Concern is valid but framing is now incomplete since Main also shows significance |

The first-layer audit was relatively conservative and did not generate many false positives. Its main problem is omission and staleness, not overclaiming.

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|--------------------------|-------------|-----------------|
| M1 | Code-audit mismatch | Entire audit documents superseded code version; key RHS changed from lag to contemporaneous, DVs changed, controls added | `git diff 43f12b0 HEAD -- src/f1d/econometric/run_h6_cccl.py` (295 lines changed) | **Critical** | Audit written before code refactoring; never updated | Committee would be misled about what the suite actually does | Rewrite audit from scratch against current code |
| M2 | Identification | Contemporaneous CCCL (time t) as treatment creates severe reverse-causality risk: firms experiencing uncertainty may drive SEC scrutiny patterns | Code line 160: `iv_cols = ["shift_intensity_mkvalt_ff48"]` | **High** | Audit written when lag was used; lag partially mitigated this | Causal interpretation is weaker than with lag | Either revert to lag or add extensive discussion of timing assumption |
| M3 | Estimation failure | 8 Utility-sample regressions fail with "exog does not have full column rank" | `logs/H6_CCCL/2026-03-13_053758/run.log`: 8 ERROR entries | **High** | Not present in audit-era run (which used different DVs/controls) | Utility sample results are entirely missing from latest output | Investigate rank deficiency; likely too few firms (72-85) for firm FE + 8 controls |
| M4 | Variable coverage | Clarity Residual DVs have 0% coverage in Finance and Utility samples | `panel['Manager_Clarity_Residual'].notna()` for Finance: 0/20,482 | **High** | Variables did not exist in audit-era code | 4 out of 6 DVs cannot be estimated for Finance/Utility | Document limitation; these DVs are Main-only by construction (H0.3 dependency) |
| M5 | Warning suppression | Code silences statsmodels covariance warnings (line 77-79) | `warnings.filterwarnings("ignore", message="covariance of constraints does not have full rank")` | **Moderate** | Not mentioned in first audit | Potential covariance issues hidden from user | Log warnings instead of suppressing; or document suppression rationale |
| M6 | Non-unique panel index | PanelOLS index (gvkey, year) is non-unique: 48,817/67,393 duplicate index entries in Main MgrQA sample. Mean 3.9 calls per (gvkey, year). | `df_panel.index.duplicated().sum()` = 48,817 | **Moderate** | Not checked in first audit | PanelOLS entity effects demean within gvkey (correct) and time effects demean within year (correct), so functionally OK for call-level analysis. But standard errors assume observations within a cluster are correlated — with ~4 calls per firm-year, within-firm-year correlation is likely high. | Discuss call-level vs firm-year-level identification; consider firm-year aggregation or multi-way clustering |
| M7 | Missing controls in audit | Audit lists 5 controls; code has 8 (adds earnings_volatility, RD_Intensity, Volatility) | Code lines 94-103 vs audit section A4 | **Moderate** | Audit documents pre-refactoring control set | Audit understates control set; post-treatment control risk for RD_Intensity and Volatility not assessed | Update variable dictionary; assess whether new controls are post-treatment |
| M8 | Pre-trends concern | Lead1 coefficient is significant (p=0.038) in latest Main MgrQA pre-trends run | `regression_results_Main_Manager_QA_Uncertainty_pct_PRETRENDS.txt`: lead1 p=0.038 | **High** | Audit notes pre-trends concern from old run but with different RHS variable | Causal interpretation undermined; suggests pre-existing trends in uncertainty correlated with future CCCL exposure | Flag prominently; consider whether contemporaneous CCCL specification is viable |
| M9 | Stale output artifacts | Multiple output directories (17 runs) exist; latest run differs substantially from audit-era run | `ls outputs/econometric/h6_cccl/` shows 17 directories | **Moderate** | Audit references 2026-02-27 run only | Stale artifacts could masquerade as valid outputs | Clean old outputs or document which run is canonical |
| M10 | Post-treatment controls | `Volatility` (stock return volatility) and `RD_Intensity` may be affected by SEC scrutiny — they could be post-treatment mediators | Added in commit `cf25167` | **Moderate** | Controls not in audit-era code | If CCCL affects Volatility or RD, controlling for them biases the CCCL coefficient toward zero | Assess and document; consider running without potentially post-treatment controls |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|------------------|---------------|
| M1 | Red-team | N/A | **Critical** | New discovery; renders entire audit document unreliable | Audit cannot be relied upon; must be rewritten |
| M2 | Red-team | N/A | **High** | Contemporaneous treatment worsens identification relative to audited lag specification | Causal claims substantially weakened |
| M3 | Red-team | N/A | **High** | 8 silent failures not documented anywhere | Utility results entirely absent from latest output |
| M4 | Red-team | N/A | **High** | 0% DV coverage for 2 of 6 DVs in 2 of 3 samples | Most Clarity Residual models cannot be estimated |
| M8 | Red-team | N/A | **High** | Pre-trends concern with new specification | Causal interpretation compromised |
| M5 | Red-team | N/A | Moderate | Warning suppression hides potential issues | Audit transparency |
| M6 | Red-team | N/A | Moderate | Non-unique index may affect SE computation | Inference validity |
| M7 | Red-team | N/A | Moderate | Missing controls from audit | Documentation completeness |
| M10 | Red-team | N/A | Moderate | Potential post-treatment bias from new controls | Coefficient interpretation |
| M9 | Red-team | N/A | Moderate | Stale artifacts | Reproducibility risk |
| Known-1 | First audit | "Expected" | Low | CCCL starts 2005 — correctly handled in code | Documented limitation |
| Known-2 | First audit | Moderate | Moderate | CEO coverage at 68% — still valid | Sample size concern |
| Known-3 | First audit | Moderate | Now moot | "Finance-only significance" — no longer true with current code | Results changed |
| Known-4 | First audit | Low | Low | Utility small sample — still valid; now also fails | Rank deficiency |
| Known-5 | First audit | "Resolved" | Moderate | "Within-R2 reporting fixed" — but within-R2 values are very low (0.001-0.004) | Weak explanatory power not flagged |
| Known-6 | First audit | Moderate | High | "Pre-trends violations" — worse with contemporaneous treatment | Identification threat upgraded |

---

## I. Completeness Gaps in the First Audit

| Missing/incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|------------------------|----------------|----------|----------|-------------------------------|
| Current code specification | Audit documents superseded version | Git diff: 295 lines changed | Critical | Must audit the code at HEAD, not a prior commit |
| Control variable dictionary | Missing 3 controls (earnings_volatility, RD_Intensity, Volatility) | Code lines 94-103 | Moderate | Full control set with definitions, sources, timing, post-treatment assessment |
| Clarity Residual provenance | Not documented (did not exist in audited code) | `ceo_clarity_residual.py` depends on H0.3 output | High | Upstream dependency on H0.3 regression; coverage by sample; construction method |
| Estimation failure documentation | 8 rank-deficiency failures not logged in audit | Run log: 8 ERROR entries | High | Complete success/failure accounting for all attempted regressions |
| Within-R-squared assessment | Reported but not critiqued | All models: within-R2 between 0.0003 and 0.017 | Moderate | Should flag that treatment explains <0.4% of within-variation in most specs |
| Multiple-testing correction | Not discussed | 10+ significance tests on same data | Moderate | Bonferroni, BH, or other correction needed for 10+ one-tailed tests |
| Observation-level vs. firm-year identification | Not discussed | Mean 3.9 calls per firm-year | Moderate | Discuss whether treatment varies within firm-year and implications for identification |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Stage 1: Manifest construction | Yes (commands given) | Not re-run | Depends on raw input files | Low | Commands appear correct |
| Stage 2: Linguistic processing | Yes | Not re-run | Depends on LM dictionary | Low | Commands appear correct |
| Stage 3: Panel build | Yes | Verified: 112,968 rows, 28 cols | H0.3 Clarity Residual dependency undocumented | **High** | Must run H0.3 before Stage 3 for Clarity Residuals; not in command sequence |
| Stage 4: Regressions | Yes | Verified: produces 10 models, not 21 | 8 Utility regressions fail silently | **High** | Output count mismatch; errors only visible in log |
| Output file count | "21 regression outputs" | **No**: latest run has 6 Main + 2 Finance = 8 base + 8 pre-trends = 16 regression files | N/A | **High** | Documented count is wrong |
| Model diagnostics | "model_diagnostics.csv" | Verified: 10 rows (not 21) | N/A | High | Count mismatch |
| Environment | Python 3.9-3.13, key packages listed | Not tested | linearmodels version may affect rank-check behavior | Low | |
| Stale artifacts | Not discussed | 17 output directories exist | Previous runs could be confused with current | Moderate | Should document canonical run or clean old outputs |

**Missing from reproducibility guidance:**
- H0.3 regression must be run before Stage 3 (for Clarity Residual variables)
- `config/variables.yaml` must set `cccl_instrument_mkvalt.column: "shift_intensity_mkvalt_ff48"` (overrides default `shift_intensity_sale_ff48`)
- Utility regressions will fail — this is expected but not documented

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed/weak points | Severity |
|-------------------|----------------------|----------------|-------------------|----------|
| Identification threats | **N** | Correctly flags reduced-form vs IV issue, but audit was written when lag was used; contemporaneous treatment severely worsens reverse-causality exposure | Contemporaneous CCCL allows simultaneous determination; firm speech and SEC scrutiny patterns could be jointly driven by industry shocks | High |
| Inference/clustering | Partial | Firm-clustered SEs correctly documented | Does not discuss whether ~4 calls per firm-year create within-cluster dependence structure issues; does not assess whether year-level clustering is also needed | Moderate |
| FE and within-variation | **N** | FE structure correct, but within-R2 ranges from 0.03% to 1.7% — not flagged | Treatment explains almost none of the within-firm variation; this is a power concern that should be discussed | Moderate |
| Timing alignment | **N** | Audit describes lag (t-1) alignment; code uses contemporaneous (t) | CCCL at time t with DV at time t = no temporal separation | High |
| Post-treatment controls | **N** | Not discussed in first audit | Stock Volatility and RD_Intensity (newly added controls) may be affected by SEC scrutiny | Moderate |
| Reverse causality | **N** | First audit mentions it in passing for reduced-form; far more severe with contemporaneous treatment | Firms anticipating scrutiny may preemptively change language; industry-level confounders affect both | High |
| Endogenous sample selection | Partial | min_calls >= 5 filter documented | Does not discuss survivorship bias from requiring 5+ calls with valid CCCL | Low |
| Model-family-specific threats | Partial | Standard panel OLS concerns noted | Does not discuss Nickell bias (short T, large N panel with firm FE) or incidental parameters | Low |
| Robustness adequacy | **N** | Pre-trends only robustness test | No alternative clustering (double-cluster by firm and year); no winsorization sensitivity; no placebo tests; no alternative specifications without potentially post-treatment controls | High |
| Interpretation discipline | **N** | Audit allows "H6 PARTIALLY SUPPORTED" conclusion | With contemporaneous treatment, significant pre-trends (lead1 p=0.038), and within-R2 < 0.4%, causal interpretation is not defensible | High |
| Academic integrity / auditability | **N** | Audit documents wrong version of code | A committee relying on this audit would be materially misled about what was actually estimated | Critical |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|----------------|-----|
| Stale documentation: audit describes superseded code | Git diff: 295 lines changed in entrypoint since audit commit | **Critical** | A referee reading the audit would believe the treatment is lagged (t-1), controls are 5 variables, and 21 models were estimated. None of this is true. | Rewrite audit against current code |
| Results table from old run presented as current | Audit section I shows diagnostics from 2026-02-27 run | **High** | Coefficient estimates, sample sizes, and significance conclusions are all different in latest run | Replace with current results |
| Separation of fact and judgment | Moderate — audit uses "VERIFIED" labels appropriately in some places | Low | Generally acceptable practice | |
| Traceable evidentiary trail | Partial — commands given but output timestamps are from old run | Moderate | Cannot reproduce documented results from current code | Include commit hash in audit; tie results to specific code version |
| Rhetorical overreach | "H6 PARTIALLY SUPPORTED" based on Finance-only significance in old run | Moderate | With current code, Main is also significant but pre-trends undermine causal interpretation | Replace with measured statement about correlation vs. causation |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|------------------------|
| RT-1 | First-audit factual error | Code-audit mismatch | Y | Critical | Entire audit | Audit documents superseded code: wrong RHS variable (lag vs contemporaneous), wrong DVs (7 vs 6), wrong controls (5 vs 8) | `git diff 43f12b0 HEAD` | Committee would be misled about every aspect of the estimation | Rewrite audit from current code | **Y** |
| RT-2 | Underlying issue missed | Identification | Y | High | `run_h6_cccl.py:160` | Contemporaneous CCCL (t) used as treatment — no temporal separation from outcome | Code inspection | Reverse causality not mitigable without lag or IV | Revert to lag or implement formal IV | **Y** |
| RT-3 | First-audit factual error | Results | Y | High | Audit section I | Results table shows old-run coefficients (beta=-0.0865) not reproducible from current code (beta=-0.1125) | Compare diagnostics CSV files | Documented results are fictional for current code | Update with current results | **Y** |
| RT-4 | Underlying issue missed | Estimation | Y | High | Run log | 8 Utility regressions fail with rank-deficiency errors; failures not documented anywhere | `logs/H6_CCCL/2026-03-13_053758/run.log` | Utility sample has zero valid results in latest run | Document failures; investigate cause | Y |
| RT-5 | Underlying issue missed | Coverage | Y | High | Panel builder | Clarity Residual DVs have 0% coverage in Finance/Utility (depend on H0.3, Main-only) | `panel[col].notna().sum()` for Finance/Utility = 0 | 4/6 DVs cannot be estimated for Finance/Utility | Document as Main-only DVs; adjust spec register | Y |
| RT-6 | Underlying issue missed | Identification | Y | High | Pre-trends output | Lead1 CCCL coefficient significant (p=0.038) in Main MgrQA pre-trends test | Pre-trends regression output | Causal interpretation undermined by parallel-trends failure | Flag prominently in thesis | Y |
| RT-7 | First-audit factual error | Spec register | Y | High | Audit section H | Lists 7 specs including Weak_Modal and Uncertainty_Gap; actual code has 6 different specs | Code CONFIG lines 83-90 | Spec register is entirely wrong | Rewrite spec register | Y |
| RT-8 | First-audit omission | Controls | Y | Moderate | Audit section A4 | Missing 3 controls: earnings_volatility, RD_Intensity, Volatility | Code lines 94-103 | Incomplete variable dictionary; post-treatment risk not assessed for new controls | Add to variable dictionary; assess post-treatment bias | N |
| RT-9 | Underlying issue underplayed | Robustness | Y | Moderate | Audit section J | Only robustness test is pre-trends; no alternative clustering, winsorization sensitivity, placebo, or control sensitivity | Code inspection | Robustness battery is minimal | Add double-clustering, control sensitivity, subsample tests | N |
| RT-10 | First-audit omission | Warning suppression | Y | Moderate | `run_h6_cccl.py:77-79` | Statsmodels covariance warnings silenced via `warnings.filterwarnings` | Code line 77-79 | Potential covariance issues hidden | Log rather than suppress | N |
| RT-11 | First-audit omission | Panel structure | Y | Moderate | `run_h6_cccl.py:194` | Non-unique (gvkey, year) index passed to PanelOLS; mean 3.9 calls per firm-year | `df_panel.index.duplicated().sum()` = 48,817 | Entity/time effects applied at call level with multi-obs per cell; may affect SE computation | Discuss or aggregate to firm-year | N |
| RT-12 | First-audit omission | Explanatory power | Y | Moderate | Model diagnostics | Within-R2 ranges 0.03%-1.7% across all specs | `model_diagnostics.csv` | Treatment explains almost no within-variation | Flag in thesis; discuss power | N |
| RT-13 | Unverified concern | Multiple testing | N/A | Moderate | Audit section I | 10+ one-tailed tests without correction | Standard practice concern | Inflated false-positive rate | Apply BH or similar correction | N |

---

## N. What a Committee / Referee Would Still Not Know

1. **The treatment variable changed from lagged (t-1) to contemporaneous (t)** after the audit was written, creating a fundamentally different identification strategy with worse reverse-causality properties.

2. **The dependent variables changed**: Weak Modal and Uncertainty_Gap were replaced by Clarity Residuals, which have 0% coverage outside the Main sample and depend on a separate regression (H0.3) not documented in the audit.

3. **Eight regressions silently fail** in the latest run due to rank deficiency in the Utility sample. The audit reports Utility results that cannot be reproduced.

4. **Three additional controls were added** (earnings_volatility, RD_Intensity, Volatility) without post-treatment assessment. Stock volatility and R&D intensity may be affected by SEC scrutiny.

5. **Pre-trends are present**: the lead1 CCCL coefficient is significant at 5% in the primary specification, undermining causal interpretation.

6. **Within-R-squared is extremely low** (0.03%-1.7%), meaning the treatment explains almost none of the outcome variation even within firms.

7. **The documented results table is from a different run** with different variables, sample sizes, and coefficients. None of the audit's reported estimates can be reproduced from the current code.

---

## O. Priority Fixes to the First Audit

| Priority | Fix | Why it matters | Effort | Credibility gain |
|----------|-----|----------------|--------|------------------|
| 1 | Rewrite entire audit against current code at HEAD | Every material section is factually incorrect | High | Critical — audit is currently unusable |
| 2 | Document contemporaneous-treatment identification concern | Core identification strategy changed; reverse causality now unmitigated | Medium | High — referee would immediately flag this |
| 3 | Document all estimation failures and coverage gaps | 8 failed regressions + 0% Clarity Residual coverage in Finance/Utility not mentioned | Medium | High — completeness |
| 4 | Add pre-trends assessment for current specification | Lead1 significant at 5% undermines causal claims | Low | High — identification |
| 5 | Update variable dictionary with all 8 controls and 6 DVs | Missing variables from audit | Medium | Moderate — completeness |
| 6 | Add multiple-testing correction discussion | 10+ tests on same data | Low | Moderate — inference rigor |
| 7 | Discuss within-R2 and statistical power | Treatment explains <0.4% of within-variation | Low | Moderate — honest reporting |
| 8 | Add post-treatment control assessment for new controls | Volatility and RD_Intensity may be affected by treatment | Low | Moderate — identification |
| 9 | Document H0.3 dependency for Clarity Residuals | Upstream dependency not in reproducibility commands | Low | Moderate — reproducibility |
| 10 | Clean stale output directories or document canonical run | 17 output directories with different specifications | Low | Low — housekeeping |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
No. The first audit documents a version of the code that no longer exists. Every material section — the spec register, variable dictionary, results table, hypothesis definitions, and output counts — is factually incorrect relative to the current codebase.

**Biggest factual weakness:**
The key independent variable is documented as lagged CCCL (t-1) but the code uses contemporaneous CCCL (t). This is not a minor labeling error; it changes the identification strategy fundamentally.

**Biggest completeness weakness:**
The audit omits 3 control variables, 2 new dependent variables (Clarity Residuals), the H0.3 upstream dependency, all estimation failures in the Utility sample, and the 0% DV coverage for Clarity Residuals outside Main.

**Biggest severity/judgment weakness:**
The audit concludes "H6 PARTIALLY SUPPORTED" based on a superseded run. The current run shows different patterns of significance and faces worse identification challenges due to the contemporaneous treatment.

**Single most important missed issue:**
The switch from lagged to contemporaneous CCCL exposure (RT-2). This eliminates the temporal separation between treatment and outcome that partially mitigated reverse causality, and the audit does not flag it because it was written before the change.

**Single most misleading claim:**
The results table in Section I, which presents coefficient estimates, sample sizes, and significance conclusions from a run that used different variables, different controls, and a different treatment timing. A reader would believe these are the actual results of the current code. They are not.

**What should a thesis committee believe after this red-team review?**
The H6 suite is a call-level panel regression estimating the association between CCCL-based SEC scrutiny exposure and managerial uncertainty language. The implementation is mechanically sound (correct FE, clustering, and merge logic), but the suite faces three material challenges: (1) contemporaneous treatment timing with no lag creates unresolved reverse-causality risk, (2) significant pre-trends (lead1 p=0.038) undermine causal interpretation, and (3) within-R-squared is extremely low (<0.4% in primary specs). The existing first-layer audit is not reliable as a referee document because it describes a superseded version of the code. A complete rewrite of the audit against the current codebase is required before any thesis-level reliance.
