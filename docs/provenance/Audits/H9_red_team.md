# H9: Takeover Hazard Models — Second-Layer Red-Team Audit

**Audit date:** 2026-03-15
**Auditor posture:** Hostile-but-fair replication auditor, adversarial toward both the implementation and the first-layer audit.
**First-layer audit:** `docs/provenance/H9.md`

---

## A. Red-Team Bottom Line

The first-layer audit is a thorough, well-structured document that correctly identifies the suite boundary, traces dependencies end-to-end, and flags several genuine issues. However, it contains one **material factual error** that propagates through its entire inference assessment: it claims the standard errors are "Robust sandwich estimator (lifelines default for CoxTimeVaryingFitter)" when in fact the SEs are **model-based (inverse Hessian), not robust**. The `robust` parameter defaults to `False` in lifelines 0.30.0's `CoxTimeVaryingFitter.fit()`, and the H9 code does not pass `robust=True`. Furthermore, `robust=True` raises `NotImplementedError` for this estimator class. This error causes the first audit to *understate* the inference problem: not only are the SEs unclustered (as the audit correctly notes), they are not even heteroskedasticity-robust. The first audit's other factual claims are largely correct, and its issue register is reasonably complete, though it misses or underweights several items identified below.

**Overall grade for the first audit: PARTIALLY RELIABLE**

The factual error on SE type is material. Most other claims are verified. The audit is useful as a starting point but cannot be trusted as standalone referee documentation without correction.

**Suite as implemented: SALVAGEABLE WITH MAJOR REVISIONS**

The first audit's verdict of "SALVAGEABLE WITH MAJOR REVISIONS" is correct, but the severity of the inference gap is worse than stated.

**Risk characterization of the first audit: Understated risk** on the SE/inference dimension (claimed robust when actually model-based); adequately stated risk on most other dimensions.

---

## B. Scope and Objects Audited

| Role | Path |
|------|------|
| Suite ID | H9 |
| Suite entrypoint | `src/f1d/econometric/run_h9_takeover_hazards.py` |
| Panel builder | `src/f1d/variables/build_h9_takeover_panel.py` |
| First-layer audit | `docs/provenance/H9.md` |
| Takeover indicator builder | `src/f1d/shared/variables/takeover_indicator.py` |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` |
| Path utils | `src/f1d/shared/path_utils.py` |
| Latest panel artifact | `outputs/variables/takeover/2026-03-12_024947/takeover_panel.parquet` |
| Latest econometric outputs | `outputs/econometric/takeover/2026-03-13_053120/` |
| Run log inspected | `outputs/econometric/takeover/2026-03-13_053120/run_log.txt` |
| Hazard ratios CSV | `outputs/econometric/takeover/2026-03-13_053120/hazard_ratios.csv` |
| Model diagnostics CSV | `outputs/econometric/takeover/2026-03-13_053120/model_diagnostics.csv` |
| lifelines version | 0.30.0 (verified via `lifelines.__version__`) |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | Pass | Code inspection confirms 3 events x 3 variants x 4 configs = 36 models. Verified against `model_diagnostics.csv` (36 rows). | Correct and complete. |
| Reproducibility commands | Pass | Commands `python -m f1d.variables.build_h9_takeover_panel` and `python -m f1d.econometric.run_h9_takeover_hazards` are documented and runnable. | Correct. |
| Dependency tracing | Pass | All 14 builders, ClarityCEO merge, SDC merge, counting-process construction documented with line references. | Thorough. |
| Raw data provenance | Pass | Manifest, Compustat, SDC, ClarityCEO, residuals all traced with row counts and uniqueness checks. | Verified against artifacts. |
| Merge/sample audit | Pass | All merges documented with pre/post row counts, join types, key uniqueness. Row count validation in code confirmed. | Verified. |
| Variable dictionary completeness | Pass | All 20 variables documented with formulas, timing, transforms, winsorization, source fields, code locations. | Comprehensive. |
| Outlier/missing-data rules | Pass | Winsorization rules, listwise deletion, denominator protections, inf replacement all documented. | Verified against `_compustat_engine.py`. |
| Estimation spec register | Pass | All 36 specs enumerated with model type, outcome, controls, strata, EPV. | Matches output. |
| Verification log quality | Partial | 19 verification steps documented. But the audit references run date 2026-03-12 while latest output is 2026-03-13; it is unclear which run the audit actually verified. | Minor provenance gap. |
| Known issues section | Partial | 6 issues documented (J1-J6). Misses the SE type error (claims robust when model-based). | Material omission on SE type. |
| Identification critique | Pass | 12 identification threats enumerated in K2. Covers reverse causality, OVB, endogenous selection, survivorship, etc. | Thorough. |
| Econometric implementation critique | **Fail** | Claims "Robust sandwich estimator" for SE. Actual: model-based (inverse Hessian). `robust=False` is the default; `robust=True` raises `NotImplementedError`. | **Material factual error.** |
| Robustness critique | Pass | Robustness table in K5 correctly identifies gaps (no placebo, no alternative clustering, no sub-period, no nonlinearity). | Adequate. |
| Academic-integrity critique | Pass | K7 table covers 11 risk dimensions with evidence. | Reasonable. |
| Severity calibration | Partial | L-01 (clustering) rated Critical, L-02 (PH test) rated High. But L-01 should be even more severe given SEs are not even robust. | Understated due to SE error. |
| Final thesis verdict support | Partial | "SALVAGEABLE WITH MAJOR REVISIONS" is correct. But the reasoning understates the SE problem. | Verdict is right; reasoning is partially wrong. |

---

## D. Claim Verification Matrix (First Audit Claims Tested)

| ID | First-layer claim | Section | Verified? | Evidence checked | Red-team verdict | Notes |
|----|-------------------|---------|-----------|-----------------|-----------------|-------|
| C1 | Estimator is `lifelines.CoxTimeVaryingFitter` | A2 | Y | `run_h9_takeover_hazards.py:100,475` | Correct | |
| C2 | Tie method is Efron | A2 | Y | lifelines source: `_newton_raphson_for_efron_model` | Correct | |
| C3 | SE = "Robust sandwich estimator (lifelines default)" | A5 | **N** | `CoxTimeVaryingFitter.fit` signature: `robust=False`; code does not pass `robust=True`; `robust=True` raises `NotImplementedError` | **FACTUALLY INCORRECT** | Model-based (inverse Hessian) SEs used. |
| C4 | SE is NOT clustered by firm | A5 | Y | No `cluster_col` in `CoxTimeVaryingFitter.fit`; confirmed via `inspect.signature` | Correct | |
| C5 | Panel has 107,644 rows x 31 cols | B | Y | `pd.read_parquet()` confirms shape (107644, 31) | Correct | |
| C6 | 2,410 unique firms, 663 event firms | B | Y | `df['gvkey'].nunique()` = 2410; event firm count = 663 | Correct | |
| C7 | Main sample: 84,104 intervals, 1,870 firms, 560 events | E5 | Y | Reproduced via filter and count | Correct | |
| C8 | Complete-case CEO: 51,627 intervals, 1,349 firms, 307 events | E5 | Y | Reproduced via `dropna` on CEO + sparse controls | Correct | |
| C9 | 243 HR rows, 36 diagnostic rows | B | Y | `hazard_ratios.csv` = 243 rows, `model_diagnostics.csv` = 36 rows | Correct | |
| C10 | All clarity p-values > 0.49 | I-14, K6 | **N** | Min p = 0.480 (Manager_Residual_strata_year, Friendly model) | **Minor factual error** | Should say "p > 0.48". |
| C11 | Concordance range 0.43-0.59 | I-13 | Y | `diag['concordance'].min()` = 0.432, `.max()` = 0.588 | Correct | |
| C12 | ClarityCEO 40.3% missing in full panel | E2, I | Partial | In Main sample: 38.1% missing. In full panel: need to check. | First audit says 40.3% in multiple places referencing "panel" broadly; in Main it is 38.1%. | The 40.3% figure appears to be for the full panel (pre-Main filter). Confirmed: full panel ClarityCEO coverage = 64,217/107,644 = 59.7% non-missing = 40.3% missing. Correct for full panel, but some references in E2 may confuse full vs Main. |
| C13 | No PH assumption test implemented | J6, K3, L-02 | Y | Grep for `schoenfeld`, `check_assumptions` yields no H9 hits | Correct | |
| C14 | 26 Unknown-type events in Main sample | E4 step 7 | Y | Reproduced: 26 Unknown events in Main | Correct | |
| C15 | Compustat merge_asof has no tolerance | L-09 | Y | `_compustat_engine.py:1246-1253` confirms no `tolerance` parameter | Correct | |
| C16 | Deterministic: yes | B | Y | No random seeds, Cox PH is deterministic given data | Correct | |
| C17 | 23 output files | B | Y | `ls` on latest output dir shows 23 files | Correct | |
| C18 | Docstring says `takeover_hazard_table.tex` but code writes `takeover_table.tex` | Not flagged | Y | `run_h9_takeover_hazards.py:64` vs line 940 | **Missed by first audit** | Minor documentation inconsistency in source. |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|-------------------|------------------------|----------|-----------------|----------------------|
| E1 | "Standard errors: Robust sandwich estimator (lifelines default for CoxTimeVaryingFitter)" (A5, repeated in H spec register, K3, K7) | **Factually false.** `CoxTimeVaryingFitter.fit()` has `robust=False` as default. The code does not pass `robust=True`. In lifelines 0.30.0, `robust=True` raises `NotImplementedError`. | **Critical** | Should have inspected lifelines source or tested `robust` parameter. | "Standard errors: Model-based (inverse Hessian). Robust sandwich SE is NOT available for `CoxTimeVaryingFitter` in lifelines 0.30.0 (`robust=True` raises NotImplementedError). SEs are neither robust nor clustered." |
| E2 | "all p > 0.49" (I-14, K6) | Minimum clarity p-value is 0.480 (Manager_Residual_strata_year, Friendly model). | Low | Should have computed `min(p)` from CSV. | "all p > 0.48" |
| E3 | "The latest verified run completed in 19.4 seconds on 2026-03-12" (B) | The latest actual output directory is 2026-03-13_053120, which took 66.1 seconds. The audit references a prior run. | Low | Should cite the actual latest run or note which specific run was verified. | Cite the specific run timestamp verified. |
| E4 | "Given all p > 0.49, this does not change the null conclusion" (K3 discussion of clustering) | With model-based SEs (not even robust), the understated SE problem is more severe than described. While the null conclusion is likely robust, the degree of SE understatement is larger than the audit implies. | Medium | Should have verified SE type before assessing clustering impact. | "Given all p > 0.48 with model-based (non-robust, non-clustered) SEs, the null conclusion is likely robust, but the true SEs could be substantially larger." |
| E5 | L-01 states "CoxTimeVaryingFitter uses robust sandwich SE but does not cluster by gvkey" | The premise is wrong: it does NOT use robust sandwich SE. | **Critical** | Same as E1. | "CoxTimeVaryingFitter uses model-based (inverse Hessian) SE. It does not support robust SE (NotImplementedError) and does not cluster." |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why it appears false/overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|--------------------------------|----------|------------------------|----------------|
| F1 | None identified | The first audit's criticisms of the implementation are generally warranted or understated. The main error is in the *characterization* of the SE problem (wrong premise, correct conclusion direction). | N/A | N/A | N/A |

No false positives found. The first audit's issues are real; the problem is that one issue (SE type) is more severe than stated.

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed/underplayed it | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|--------------------------------------|-------------|----------------|
| G1 | Inference/SEs | **SEs are model-based, not robust.** `CoxTimeVaryingFitter.fit()` defaults to `robust=False` and `robust=True` raises `NotImplementedError` in lifelines 0.30.0. The H9 code does not pass `robust=True`. | `inspect.signature(CoxTimeVaryingFitter.fit)` shows `robust=False`; testing `robust=True` raises `NotImplementedError: Not available yet.` | **Critical** | First audit trusted the lifelines docstring (which misleadingly says "default: True" in the description but the actual parameter default is `False`) without testing. | SEs are likely understated for heteroskedasticity in addition to the clustering problem. All p-values, z-statistics, and confidence intervals in the output are based on model-based SEs with no heteroskedasticity correction. | Must either (a) switch to `CoxPHFitter` with `cluster_col` and `robust=True` using last-observation-per-subject or entry_col format, or (b) implement block bootstrap at the firm level. |
| G2 | Documentation bug | **Docstring output filename mismatch.** `run_h9_takeover_hazards.py:64` says `takeover_hazard_table.tex` but code at line 940 writes `takeover_table.tex`. | Code inspection. | Low | Likely not in scope of first audit's focus, but it constitutes a documentation inaccuracy in the source that could confuse reproduction. | Minor confusion when checking output enumeration. | Fix docstring to match actual filename. |
| G3 | Redundant code | **Cause-specific indicators created twice.** `build_h9_takeover_panel.py:362-367` creates `Takeover_Uninvited`/`Takeover_Friendly` in the panel. `prepare_main_sample()` at `run_h9_takeover_hazards.py:287-288` re-creates them identically. | Code inspection; verified outputs are identical via pandas comparison. | Low | Not a defect (results are identical) but creates maintenance risk: if one is changed without the other, silent discrepancy could occur. | No immediate impact; maintenance hazard. | Remove redundant creation in the runner; rely on panel-level indicators. |
| G4 | Stale artifact risk | **Multiple stale panel directories exist.** 12 timestamped panel directories exist under `outputs/variables/takeover/`. The econometric runner uses `get_latest_output_dir()` which picks the chronologically latest. If a bad panel build occurs after the good one, it will be silently used. | `ls` on `outputs/variables/takeover/` shows 12 directories from 2026-02-19 through 2026-03-12. | Low-Medium | First audit mentions stale artifact risk as "Low" in K7 but does not enumerate the actual number of stale directories or assess the risk of accidental bad-panel usage. | Could use wrong panel if latest build is corrupt. | Document which panel timestamp the econometric results correspond to; consider cleaning old directories. |
| G5 | Inference | **No power analysis or minimum detectable effect reported.** With 307 events for the primary All-Takeover/CEO model (and only 40 for Uninvited), the null result may simply reflect insufficient power. | Run log confirms event counts. Audit references null results but does not compute or request a power calculation. | Medium | First audit notes low EPV for uninvited models but does not request or flag the absence of a formal power analysis for the primary models. | A referee cannot distinguish "no effect" from "underpowered study" without knowing the minimum detectable hazard ratio. | Compute minimum detectable HR at 80% power for each model configuration. |
| G6 | Model specification | **Calendar-time scale may be inappropriate.** The Cox model uses days-since-2000-01-01 as the time scale. For takeover hazard, a more natural time scale might be firm-age, listing-age, or CEO-tenure. Calendar time conflates firm-specific risk dynamics with economy-wide M&A wave patterns. | `build_h9_takeover_panel.py:339-340` confirms calendar-day time scale. Year-stratified models partially address this but do not change the underlying time scale. | Medium | First audit documents the time scale correctly but does not critique the choice. | If M&A activity clusters in time (e.g., 2005-2007 wave), calendar time scale may violate the PH assumption more severely than a firm-age scale. | Consider alternative time scales (firm-age, CEO tenure); at minimum discuss the choice. |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|------------------|---------------|
| L-01 / G1 | First audit L-01 + Red-team G1 (merged) | Critical (clustering only) | **Critical+** | First audit's premise was wrong: SEs are not even robust, let alone clustered. The problem is strictly worse than described. | Blocks thesis-standard reliance. All reported SEs, z-stats, p-values, and CIs are computed from model-based (inverse-information) variance, with no heteroskedasticity or clustering correction. |
| L-02 | First audit | High | High | No change. PH assumption test remains mandatory. | Blocks thesis-standard. |
| L-03 | First audit | High | High | No change. Structural missingness concern is valid. | Blocks thesis-standard. |
| L-04 | First audit | High | High | No change. OVB from missing governance controls is standard reviewer concern. | Blocks thesis-standard. |
| L-05 | First audit | High | Medium | Downgraded. For a null-result suite, placebo tests are less urgent than for a suite claiming effects. The null is the conservative finding. | Does not block, but referee will request. |
| L-06 | First audit | Medium | Subsumed into L-01/G1 | Merged. "No alternative clustering" is part of the broader SE problem. | Subsumed. |
| L-07 | First audit | Medium | Medium | No change. | Does not block. |
| L-08 | First audit | Medium | Medium | No change. | Does not block. |
| L-09 | First audit | Medium | Medium | No change. Stale Compustat match risk is real. | Does not block, but should be fixed. |
| L-10 / L-18 | First audit | Medium / Medium | Medium (merge) | L-10 and L-18 describe the same issue (Unknown-type events). Should be one entry. | Does not block. |
| L-11 | First audit | Medium | Medium | No change. Year-stratified uninvited models are unreliable. | Does not block (correctly flagged as unreliable). |
| L-12 | First audit | Low | Low | No change. | Minor. |
| L-13 | First audit | Low | Low | No change. | Minor. |
| L-14 | First audit | Low | Low | No change. | Minor. |
| L-15 | First audit | Low | Low | No change. | Minor. |
| L-16 | First audit | Low | Low | No change. | Minor. |
| L-17 | First audit | Low | Low | No change. | Minor. |
| G5 | Red-team | N/A | Medium | New. Absence of power analysis for null-result suite. | Does not block, but a referee will want this. |
| G6 | Red-team | N/A | Medium | New. Calendar-time scale choice uncritiqued. | Does not block, but should be discussed. |

---

## I. Completeness Gaps in the First Audit

| Missing/incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|------------------------|----------------|----------|----------|-------------------------------|
| SE type verification | Trusted lifelines docstring instead of testing actual `robust` default or attempting `robust=True`. | `CoxTimeVaryingFitter.fit` has `robust=False` as actual default; `robust=True` raises `NotImplementedError`. | **Critical** | Should have run a test fit or inspected `inspect.signature()` to confirm SE type. |
| Power analysis | Not mentioned anywhere in the audit. | N/A | Medium | For a null-result suite, should have flagged absence of minimum detectable effect / power calculation. |
| Time scale critique | Time scale documented but not critiqued. | Calendar-time scale used; no discussion of alternatives. | Low-Medium | Should have assessed whether calendar time is the appropriate risk time scale for takeover hazard. |
| Stale directory enumeration | First audit says stale artifact risk is "Low" but does not count actual stale directories. | 12 stale panel directories exist. | Low | Should have enumerated stale directories and assessed risk. |
| Source code documentation bug | Docstring/code filename mismatch not flagged. | `run_h9_takeover_hazards.py:64` vs line 940. | Low | Should have cross-checked docstring output list against actual code. |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented it? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|---------------------------|-----------|-------------------|------|---------------|
| Build panel: `python -m f1d.variables.build_h9_takeover_panel` | Yes | Yes (output exists) | No | Low | Command is correct and runnable. |
| Run estimation: `python -m f1d.econometric.run_h9_takeover_hazards` | Yes | Yes (output exists) | No | Low | Command is correct and runnable. |
| Upstream H1 clarity scores must exist | Yes (C3) | Yes | Yes — requires prior `run_h1_*` completion | Medium | If clarity scores are stale or missing, panel build will produce NaN ClarityCEO. Not a hidden step per se but an ordering dependency. |
| Upstream H0.3 residuals must exist | Yes (C3) | Yes | Yes — requires prior clarity extended run | Medium | Same ordering dependency. |
| SDC raw data at `inputs/SDC/sdc-ma-merged.parquet` | Yes (D) | Yes (file exists) | No | Low | Raw data is present. |
| Compustat raw data at `inputs/comp_na_daily_all/comp_na_daily_all.parquet` | Yes (D) | Yes (file exists) | No | Low | Raw data is present. |
| lifelines version sensitivity | Partially (mentions lifelines but no version pin) | Yes — lifelines 0.30.0 installed | Yes — `robust` behavior is version-dependent | Medium | The `robust=False` default and `NotImplementedError` for `robust=True` are lifelines-version-specific. A different lifelines version might behave differently. First audit should pin the lifelines version. |
| `get_latest_output_dir()` picks the chronologically latest panel | Not explicitly documented | Verified via code | Yes — silent dependency on directory naming | Medium | If directories are not chronologically ordered by name, wrong panel could be used. Currently 12 panel directories exist. |
| Output enumeration completeness | Yes (B) | Yes — 23 files confirmed | No | Low | Complete. |
| Environment (Python version) | Yes (Python 3.13) | Verified | No | Low | |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Identification threats | Y | 12 threats enumerated with evidence and severity. | None missed. | N/A |
| Inference / clustering | **N** | **Incorrectly states SEs are robust sandwich.** Actual: model-based. The clustering concern is correct but understated because the baseline is worse than assumed. | SE type is wrong. Should say "model-based, non-robust, non-clustered." | Critical |
| FE and within-variation | Y | Correctly notes no entity/time FE in base models; stratification as robustness. | None. | N/A |
| Timing alignment | Y | Verified covariate timing (call date) precedes event. | None. | N/A |
| Post-treatment controls | Y | Correctly verifies all controls are pre-treatment via merge_asof(backward). | None. | N/A |
| Reverse causality | Y | Discussed for both time-invariant (ClarityCEO) and time-varying (residuals). | None. | N/A |
| Endogenous sample selection | Y | 40% missingness flagged as structural. | Could be stronger: should explicitly request Heckman model or inverse-probability weighting, not just "report comparison." | Low |
| Model-family-specific threats | Partial | PH assumption (correct), competing risks (correct), EPV (correct). | Missing: discussion of time-scale appropriateness (calendar vs firm-age); missing: power analysis for null result. | Medium |
| Robustness adequacy | Y | Comprehensive table of implemented/missing robustness checks. | None. | N/A |
| Interpretation discipline | Y | Correctly constrains interpretation to descriptive association. | None. | N/A |
| Academic-integrity / auditability | Y | 11-item risk table in K7. | None. | N/A |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk in first audit | Evidence | Severity | Why it matters | Fix |
|----------------------------------|----------|----------|----------------|-----|
| **Material factual error on SE type propagates through 6+ sections.** | A5, H (all 36 spec entries), K3 (first row), K7, L-01 all say "Robust sandwich." | Critical | A thesis committee reading the audit would believe SEs are robust when they are not. This mischaracterizes the inference apparatus. | Correct all references to state "model-based (inverse Hessian), non-robust, non-clustered." |
| Minor factual error on p-value bound. | First audit says "all p > 0.49"; actual min = 0.480. | Low | Slightly overstates the distance from significance. Does not change conclusion. | Correct to "all p > 0.48." |
| Audit references a specific run but latest output is from a different run. | Audit says "2026-03-12"; latest output is 2026-03-13_053120. | Low | Creates provenance ambiguity about which outputs were actually verified. | Cite the exact run timestamp verified. |
| Fact/judgment separation is generally good. | Tags like [VERIFIED FACT], [REFEREE CONCERN], [VERIFIED IMPLEMENTATION ISSUE] used consistently. | None | Good practice. | None. |
| Traceable evidentiary trail. | File paths and line numbers cited throughout. | None | Good practice. | None. |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis-standard reliance on first audit? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|------------------------------------------------|
| RT-01 | First-audit factual error | Inference/SEs | Y | **Critical** | A5, H, K3, K7, L-01 | First audit claims SEs are "Robust sandwich estimator (lifelines default)." Actual: model-based (inverse Hessian). `robust=False` is the default; `robust=True` raises `NotImplementedError`. | `inspect.signature(CoxTimeVaryingFitter.fit)` shows `robust=False`; testing `robust=True` raises `NotImplementedError`. | All SE characterizations in the first audit are wrong. The inference problem is worse than stated. | Correct all SE references. Switch estimator to `CoxPHFitter` with `cluster_col` and `robust=True`, or implement firm-level bootstrap. | **Y** |
| RT-02 | First-audit factual error | Verification | Y | Low | I-14, K6 | Claims "all p > 0.49." Actual minimum p = 0.480. | `hazard_ratios.csv` min p for clarity vars = 0.480. | Minor — does not change null conclusion. | Correct to "all p > 0.48." | N |
| RT-03 | Underlying implementation issue missed by first audit | Inference | Y | **Critical** | `run_h9_takeover_hazards.py:475-484` | SEs are model-based, not robust. The code does not pass `robust=True` to `CoxTimeVaryingFitter.fit()`. Even if it did, `robust=True` is not implemented. | See RT-01 evidence. | All z-statistics, p-values, and CIs are from model-based variance. No heteroskedasticity correction. | Switch to estimator supporting robust/clustered SE. | **Y** |
| RT-04 | First-audit omission | Power/interpretation | Y | Medium | Not in first audit | No power analysis or minimum detectable effect for null-result suite. With 307 events (primary) and 40 uninvited events, the study may lack power to detect economically meaningful hazard ratios. | Event counts from `model_diagnostics.csv`. | Cannot distinguish "no effect" from "underpowered." | Compute minimum detectable HR at 80% power. | N |
| RT-05 | First-audit omission | Model specification | Y | Medium | Not in first audit | Calendar-time scale used without critique. Alternative scales (firm-age, CEO tenure) may be more appropriate for takeover hazard. | `build_h9_takeover_panel.py:339-340`. | PH assumption more likely violated under calendar time if M&A waves exist. | Discuss time-scale choice; consider alternatives. | N |
| RT-06 | Underlying implementation issue underplayed by first audit | Stale artifacts | Y | Low-Medium | K7 (rated "Low") | 12 stale panel directories exist. `get_latest_output_dir()` silently picks the latest by directory name. No mechanism to verify panel-econometric correspondence. | `ls` on panel output directory. | Could silently use wrong panel. | Document panel timestamp used; clean stale directories. | N |
| RT-07 | First-audit omission | Documentation | Y | Low | `run_h9_takeover_hazards.py:64` vs 940 | Docstring says `takeover_hazard_table.tex`; code writes `takeover_table.tex`. | Code inspection. | Minor confusion for reproducers. | Fix docstring. | N |
| RT-08 | Underlying implementation issue missed by first audit | Maintenance | Y | Low | `run_h9_takeover_hazards.py:287-288` and `build_h9_takeover_panel.py:362-367` | Cause-specific indicators created twice (panel builder + runner). Currently identical; future divergence risk. | Code inspection and pandas comparison. | Maintenance hazard. | Remove redundant creation in runner. | N |
| RT-09 | First-audit severity error | Robustness | Y | Low | L-05 | Placebo/falsification tests rated High. For a null-result suite, this should be Medium — the null is already the conservative finding. | N/A | Overstated urgency relative to SE problem. | Downgrade to Medium. | N |
| RT-10 | First-audit omission | Reproducibility | Y | Medium | B | lifelines version not pinned. `robust` behavior is version-dependent. | `lifelines.__version__` = 0.30.0. | Different lifelines version could change SE computation behavior. | Pin lifelines version in requirements. | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The SEs are model-based, not robust.** The first audit says "Robust sandwich estimator" in 6+ locations. A committee member would believe the SEs have at least heteroskedasticity robustness. They do not. The inference apparatus is strictly weaker than described.

2. **`robust=True` is not available for `CoxTimeVaryingFitter` in lifelines 0.30.0.** The recommended fix of "just add clustering" cannot be done within the current estimator class. A more fundamental estimator change is required (switch to `CoxPHFitter` with `entry_col`, or bootstrap).

3. **The study may lack statistical power.** No minimum detectable effect is computed. With 40 uninvited events, the study cannot detect anything short of a very large hazard ratio for the Uninvited hypothesis.

4. **The calendar-time scale choice is uncritiqued.** If M&A activity varies over time (it does), the PH assumption is more likely violated under calendar time than under a firm-specific time scale.

5. **The lifelines version is not pinned.** SE computation behavior could differ across versions.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|----------|-------------------|----------------|--------|------------------|
| 1 | **Correct all "Robust sandwich SE" claims to "Model-based (inverse Hessian) SE."** Update A5, all H spec register entries, K3, K7, L-01. | Material factual error that misleads readers about inference quality. | Low (text edits) | Critical — eliminates false claim. |
| 2 | **Update L-01 to state that SEs are neither robust nor clustered; note that `robust=True` raises `NotImplementedError`.** | The recommended fix path is more complex than the first audit suggests. | Low | High — corrects the fix recommendation. |
| 3 | **Correct "all p > 0.49" to "all p > 0.48."** | Minor factual accuracy. | Trivial | Low. |
| 4 | **Add power analysis gap as a known issue.** | Null-result suites require power assessment for credible interpretation. | Low | Medium. |
| 5 | **Add lifelines version pin to environment section.** | SE behavior is version-dependent. | Trivial | Low-Medium. |
| 6 | **Add time-scale critique to identification section.** | Standard survival analysis consideration missing. | Low | Low-Medium. |
| 7 | **Fix run timestamp reference (2026-03-12 vs actual latest).** | Provenance accuracy. | Trivial | Low. |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
No. The material factual error on SE type (claiming robust sandwich when actual SEs are model-based) disqualifies it as a standalone document. A referee reading this audit would form an incorrect belief about the inference apparatus. After correcting this single error and its downstream propagation, the audit would be close to referee-quality.

**What is its biggest factual weakness?**
The claim that `CoxTimeVaryingFitter` uses robust sandwich SE by default. It does not. The actual default is `robust=False`, and `robust=True` is not implemented.

**What is its biggest completeness weakness?**
Absence of a power analysis discussion for a null-result suite. A referee cannot assess whether the null reflects a true zero effect or insufficient power without knowing the minimum detectable hazard ratio.

**What is its biggest severity/judgment weakness?**
L-01 (clustering issue) is rated Critical, which is correct directionally, but the reasoning is built on a false premise (that the baseline is robust SE). The actual severity is worse: SEs are model-based with no heteroskedasticity correction at all.

**What is the single most important missed issue?**
RT-01/RT-03: SEs are model-based, not robust. This was missed because the first audit trusted the lifelines docstring (which misleadingly says "default: True" in the description text) without verifying the actual function signature or testing the parameter.

**What is the single most misleading claim?**
"Standard errors: Robust sandwich estimator (lifelines default for CoxTimeVaryingFitter)" -- repeated in 6+ locations throughout the audit.

**What should a thesis committee believe after reading this red-team review?**
The first-layer audit is a thorough, well-structured document that correctly identifies the suite boundary, data provenance, variable construction, and most implementation issues. Its verdict of "SALVAGEABLE WITH MAJOR REVISIONS" is correct. However, the inference problem is more severe than the first audit describes: the SEs are model-based (not robust, not clustered), and `CoxTimeVaryingFitter` does not support robust or clustered SE in the installed lifelines version. The practical fix requires switching to a different estimator class (`CoxPHFitter` with `entry_col` for late entry, `cluster_col='gvkey'`, `robust=True`) or implementing a firm-level block bootstrap. The uniformly null results (all clarity p > 0.48) are likely robust to this SE correction (model-based SEs are usually *smaller* than cluster-robust SEs, so corrected p-values would be even larger), but the methodological credibility of the suite requires proper inference before publication. After correcting the SE characterization error and adding power analysis, the first audit would be a reliable referee document.
