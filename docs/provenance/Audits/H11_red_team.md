# H11 Suite — Second-Layer Red-Team Audit

**Suite ID:** H11 (Political Risk & Uncertainty — Base, Lag, Lead)
**Red-team auditor:** Independent second-layer review
**Date:** 2026-03-15
**First-layer audit reviewed:** `docs/provenance/H11.md`

---

## A. Red-Team Bottom Line

The first-layer audit is a competent and thorough document that correctly identifies the most critical threat to the suite — the failed lead (placebo) test. It is factually accurate on most claims, provides verifiable evidence, and reaches a defensible final verdict ("SALVAGEABLE WITH MAJOR REVISIONS"). However, the first-layer audit has several material weaknesses: (1) it overclaims the severity of the lead test failure by stating "ALL lead coefficients significant" when in fact 7 of 28 lead specs are not significant at p<0.05 (though all 12 Main-sample specs are), (2) it fails to note that (gvkey, year) is not a unique panel index — with up to 38 calls per firm-year — which has implications for how PanelOLS computes its within-estimator and for the interpretation of "time FE", (3) it misdescribes the "Primary keys" as `gvkey + year` when the true unit of observation is the individual call (file_name), and (4) it does not adequately interrogate the within-firm autocorrelation of PRiskQ (which I measure at rho=0.36), which is the most likely explanation for the lead test failure and is a more tractable fix than the first audit suggests.

**Overall grade for the first audit:** PARTIALLY RELIABLE

**Suite as implemented:** SALVAGEABLE WITH MAJOR REVISIONS

**Risk assessment:** The first audit slightly overstates risk on the lead placebo (claiming ALL when it is "all Main-sample") and slightly understates risk on the non-unique panel index issue. Net: mixed, but on balance the major conclusions are directionally correct.

---

## B. Scope and Objects Audited

| Item | Path / detail |
|------|---------------|
| Suite ID | H11 (Base, Lag, Lead) |
| Suite entrypoints | `src/f1d/econometric/run_h11_prisk_uncertainty.py`, `..._lag.py`, `..._lead.py` |
| Panel builders | `src/f1d/variables/build_h11_prisk_uncertainty_panel.py`, `..._lag_panel.py`, `..._lead_panel.py` |
| PRiskQ builders | `src/f1d/shared/variables/prisk_q.py`, `prisk_q_lag.py`, `prisk_q_lag2.py`, `prisk_q_lead.py`, `prisk_q_lead2.py` |
| First-layer audit | `docs/provenance/H11.md` |
| Shared utilities | `panel_utils.py::assign_industry_sample()`, `winsorization.py::winsorize_by_year()`, `path_utils.py::get_latest_output_dir()` |
| Output artifacts inspected | `outputs/econometric/h11_prisk_uncertainty/2026-03-09_215136/model_diagnostics.csv`, `outputs/econometric/h11_prisk_uncertainty_lead/2026-03-09_215212/model_diagnostics.csv`, `outputs/econometric/h11_prisk_uncertainty_lag/2026-03-09_215157/model_diagnostics.csv`, `outputs/variables/h11_prisk_uncertainty/2026-03-09_214718/h11_prisk_uncertainty_panel.parquet` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | Pass | CONFIG, formulas, and outputs all checked | Correctly identifies 6 DVs, 3 samples, 3 timing variants |
| Reproducibility commands | Partial | Verification log (Section I) documents 21 checks | Commands not fully copy-pasteable; relies on `python -c` snippets without full paths |
| Dependency tracing | Pass | Builder imports, manifest source, PRisk CSV traced | Correctly traces all upstream dependencies including H0.3 |
| Raw data provenance | Partial | PRisk CSV documented (354,518 rows); Compustat/linguistic marked UNVERIFIED | Should have verified Compustat row counts |
| Merge/sample audit | Pass | Zero-row-delta enforcement, match rates, attrition table all documented | Thorough and accurate |
| Variable dictionary completeness | Pass | All 22 variables documented with source, timing, transform | Includes dead variable (Lev) — good |
| Outlier/missing-data rules | Pass | Winsorization, listwise deletion, dedup documented | Correctly flags max-dedup bias |
| Estimation spec register | Pass | All 14 base + 36 lag + 36 lead specs registered | Correctly notes Finance/Utility clarity-residual skips |
| Verification log quality | Pass | 21 numbered verification steps with outputs | Good evidence trail |
| Known issues section | Pass | 9 issues identified with impact and fix | Well-calibrated |
| Identification critique | Pass | Correctly identifies lead failure, OVB, simultaneity, autocorrelation | Core strength of the audit |
| Econometric implementation critique | Partial | Year FE coarseness flagged; but non-unique index not discussed | See Section G |
| Robustness critique | Pass | Comprehensive 12-row table of missing robustness checks | Appropriately demanding |
| Academic-integrity critique | Pass | False standardization claim, docstring mismatch flagged | Correct |
| Severity calibration | Partial | Lead failure correctly labeled Critical; but overclaims "ALL" | See Section F |
| Final thesis verdict support | Pass | "SALVAGEABLE WITH MAJOR REVISIONS" well-supported | Appropriate conclusion |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|------------------|---------|-----------|----------|-----------------|-------|
| C1 | PanelOLS with EntityEffects + TimeEffects, drop_absorbed=True | A2 | Y | Code lines 202-203 in base runner | Confirmed | |
| C2 | Clustered SEs at gvkey (entity) level | A2 | Y | `cluster_entity=True` line 203 | Confirmed | |
| C3 | 6 DVs: Manager/CEO x QA_Uncertainty/Clarity_Residual/Pres_Uncertainty | A3 | Y | CONFIG lines 87-94 | Confirmed | |
| C4 | Primary keys: gvkey + year | A1 | **Partial** | `set_index(["gvkey","year"])` used, but NOT unique — 96.6% of (gvkey,year) cells have >1 call; max=38 | Misleading | Should say "entity index: gvkey, time index: year; unit of observation: file_name (call)" |
| C5 | PRiskQ match rate 97.6% (base) | E2 | Y | Panel inspection: 110,256/112,968 notna = 97.6% | Confirmed | |
| C6 | PRiskQ dedup keeps max | E2/G | Y | `sort_values("PRisk", ascending=False).drop_duplicates(keep="first")` line 89-91 in prisk_q.py | Confirmed | |
| C7 | ALL lead coefficients significant positive | I#14/J6/L1 | **Partial** | 21/28 lead specs significant at p<0.05 one-tailed; ALL 12 Main specs significant; 2 Utility lead2 have negative betas | Overclaimed | Should say "all Main-sample lead coefficients" |
| C8 | Year FE too coarse for quarterly IV | K3/L2 | Y | `set_index(["gvkey","year"])` confirmed; PRiskQ varies quarterly | Confirmed | Valid concern |
| C9 | Table notes claim standardization not implemented | J3/K3/L5 | Y | LaTeX lines 372: "All continuous controls are standardized"; no z-score code found | Confirmed | |
| C10 | Docstring lists Weak_Modal_pct but code uses Clarity_Residual | J1/L4 | Y | Docstring lines 20-21 vs CONFIG lines 89-90 in base runner | Confirmed | |
| C11 | Lev built but unused | J2/L10 | Y | `LevBuilder` imported in all 3 panel builders; `Lev` not in BASE_CONTROLS | Confirmed | |
| C12 | 14 base regressions (6 Main + 4 Finance + 4 Utility) | H | Y | model_diagnostics.csv has exactly 14 rows | Confirmed | |
| C13 | Min-calls filter >= 5 applied after complete-case deletion | E3 | Y | Code lines 493-498 in base runner | Confirmed | |
| C14 | Main sample: 77,016 obs, 1,818 firms (Manager_QA DV) | E3/H | Y | model_diagnostics.csv confirms 77,016 / 1,818 | Confirmed | |
| C15 | PRiskQ autocorrelation is high (near-identical means/distributions) | K2 | **Partial** | Within-firm lag-1 autocorrelation = 0.36 (moderate, not high) | Somewhat overstated | 0.36 is meaningful but not "high" by panel-data standards |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|------------------|------------------------|----------|-----------------|----------------------|
| E1 | "ALL lead coefficients significant positive" (J6, L1, I#14) | 7 of 28 lead specs are NOT significant at one-tailed p<0.05; 2 have negative betas (Utility lead2 Pres DVs) | Medium | Per-spec p-values for all 28 lead regressions | "All 12 Main-sample lead coefficients are significant positive (p<0.05); 21/28 overall" |
| E2 | "PRiskQ is highly persistent" / "nearly identical means and distributions across variants" (K2) | Asserted without computing autocorrelation. Within-firm lag-1 autocorrelation = 0.36 — moderate, not high | Low | Autocorrelation computation | "PRiskQ shows moderate within-firm persistence (lag-1 rho = 0.36)" |
| E3 | "Primary keys: gvkey + year" (A1) | (gvkey, year) is not unique; 96.6% of cells have multiple calls; max 38 per cell | Medium | Uniqueness check on (gvkey, year) | "Entity index: gvkey; time index: year; unit of observation: file_name (not unique at entity-time level)" |
| E4 | Compustat raw row counts marked "UNVERIFIED" but no attempt to verify | Accepted without investigation | Low | Should have queried Compustat parquets | Should note whether this is verifiable from local artifacts |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why false/overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|---------------------|----------|------------------------|----------------|
| F1 | "ALL lead coefficients are positive and significant" (J6) | 2 of 28 are negative; 7 of 28 are not significant at p<0.05 | Lead model_diagnostics.csv: rows 24,27 have negative betas; rows 4,5,19,24,27 have p>0.05 | Medium | The Main-sample finding is robust (12/12), which is the primary concern. Non-Main failures are less relevant but overstating weakens credibility |
| F2 | "lead failure directly contradicts causal claims" (K6) — stated as if causal claims were actually made in the code | The code/docstrings suggest causal framing ("increases speech uncertainty") but no formal thesis text was inspected | Low | Code docstrings vs thesis text | More precise: "if the thesis uses causal language, the lead failure directly contradicts it" |

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|--------------------------|-------------|-----------------|
| G1 | Panel structure | **(gvkey, year) index is non-unique**: The panel has up to 38 calls per (gvkey, year). PanelOLS receives a non-unique multi-index via `set_index(["gvkey","year"])`. PanelOLS silently accepts this. | `p.groupby(['gvkey','year']).size().max()` = 38; `idx.index.is_unique` = False; 56,168 of 77,016 rows are index-duplicates | Medium | First audit treated (gvkey, year) as the primary key without checking uniqueness | (1) Entity FE still demeans correctly at gvkey level; (2) time FE demeans at year level; (3) but "within R-squared" interpretation changes — it reflects within-firm-year variation, not within-firm variation. (4) Cluster SEs at gvkey remain valid. The regression IS valid as a call-level panel with firm+year FE, but documentation is misleading about the panel structure. | Document that the panel is call-level with non-unique (gvkey, year); consider using file_name as unique row ID alongside the (gvkey, year) index |
| G2 | Inference | **Within-firm-year clustering not addressed**: Multiple calls per firm-year create within-cluster correlation at the (gvkey, year) level that is NOT accounted for by firm-level clustering alone. Firm-level clustering handles within-firm correlation across years, but intra-year shocks affecting multiple calls from the same firm are an additional source of dependence. | 96.6% of (gvkey, year) cells have >1 call; avg 3.9 calls per cell | Low-Medium | First audit discusses double-clustering (firm x quarter) but does not note the intra-year dependence from multiple calls | SEs may be slightly understated for firms with many intra-year calls; firm clustering is conservative enough to likely absorb this, but it is an undiscussed dimension | Note the non-unique panel structure; verify that firm-level clustering is sufficient by testing (gvkey, year-quarter) clustering |
| G3 | Econometric | **Beta magnitudes are 3x smaller for leads vs base**: Base betas ~0.00013; lead betas ~0.00004. The first audit notes leads are "significant" but does not compare magnitudes. The 3x attenuation is consistent with PRiskQ autocorrelation (rho=0.36), not reverse causality. | Base Manager_QA beta=0.000135; Lead1 Manager_QA beta=0.000043; ratio=3.1x | Medium | First audit focuses on significance, not magnitude comparison | The lead "failure" may be better characterized as "attenuated but still detectable due to persistence" rather than "equally strong reverse causality." This changes the remediation strategy. | Compare base vs lead beta magnitudes explicitly; discuss whether attenuation pattern is consistent with persistence vs reverse causality |
| G4 | Reproducibility | **Multiple stale output directories exist**: Base econometric has 3 timestamped dirs (2026-03-05_141511, 2026-03-05_141531, 2026-03-09_215136); `get_latest_output_dir` picks the latest by name sort | `ls outputs/econometric/h11_prisk_uncertainty/` shows 3 dirs | Low | First audit mentions stale dirs (J, K7) but does not verify which dir its own diagnostics came from | Potential for auditor confusion about which run was inspected | Clean stale output directories |
| G5 | Interpretation | **PRiskQ autocorrelation = 0.36 is MODERATE, not HIGH**: The first audit asserts "highly persistent" PRiskQ but this is unquantified. At rho=0.36, one-quarter persistence explains ~13% of variance — meaningful but not dominant. | `p.groupby('gvkey')['PRiskQ'].shift(1)` correlation = 0.358 | Low | First audit did not compute autocorrelation | Overstating persistence inflates the perceived severity of the lead failure. A moderate autocorrelation with 3x beta attenuation is consistent with a partial-persistence explanation, not a complete identification failure. | Compute and report PRiskQ autocorrelation; use it to calibrate the expected lead coefficient under the persistence-only null |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|------------------|------------------|------------------|---------------|
| L1 | First audit | Critical | **High** (downgraded) | The first audit says "ALL" leads significant; in reality 21/28 are significant, and lead betas are 3x smaller than base. The pattern is consistent with moderate persistence (rho=0.36), not reverse causality. Still a serious concern but not thesis-killing if properly discussed. | Must be disclosed; reframe as persistence concern, not outright identification failure |
| L2 | First audit | High | **High** (confirmed) | Year FE too coarse for quarterly IV — correctly identified | Quarter FE is a straightforward fix |
| L3 | First audit | High | **Medium** (downgraded) | Lead test "failure" is partially explained by persistence; the severity of the interpretive threat depends on thesis framing | Requires discussion, not necessarily a fatal flaw |
| L5 | First audit | Medium | **Medium** (confirmed) | False standardization claim in table notes | Must fix |
| L7 | First audit | Medium | **Medium** (confirmed) | No multiple-testing correction across 90 regressions | Standard concern in applied work |
| L8 | First audit | Medium | **Medium** (confirmed) | Only firm-clustered SEs | Add double-clustering |
| G1 | Red-team | N/A | **Medium** (new) | Non-unique (gvkey, year) index undocumented | Documentation and interpretation issue |
| G3 | Red-team | N/A | **Medium** (new) | Lead beta attenuation pattern not analyzed | Changes interpretation of lead "failure" |
| L4 | First audit | Medium | **Low** (downgraded) | Docstring mismatch is cosmetic | Trivial fix |
| L6 | First audit | Medium | **Low** (downgraded) | PRiskQ max-dedup: low frequency of duplicates in practice, and max vs mean difference is likely tiny for most firm-quarters | Check duplicate frequency before labeling Medium |
| L14 | First audit | Low | **Medium** (upgraded) | Very small betas (~0.0001) mean even statistically significant results may lack economic meaning. With no standardized coefficients, the suite cannot answer "how large is this effect?" | Needs standardized betas or one-SD interpretation |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|--------------------------|----------------|----------|----------|-------------------------------|
| Panel index uniqueness | First audit claims (gvkey, year) as "Primary keys" without checking uniqueness | `p.groupby(['gvkey','year']).size().max()` = 38 | Medium | Explicit check that the PanelOLS index is non-unique; discussion of implications for within-estimator interpretation |
| PRiskQ autocorrelation quantification | First audit asserts "highly persistent" without measuring | Within-firm lag-1 rho = 0.36 | Medium | Compute and report autocorrelation; use it to derive expected lead coefficient under persistence null |
| Lead beta magnitude comparison | First audit focuses on significance, not effect sizes | Base beta 3.1x larger than lead beta for same DV | Medium | Compare magnitudes across timing variants; this is key to distinguishing persistence from reverse causality |
| Compustat raw data verification | Marked "UNVERIFIED" with no attempt | Section D table | Low | At minimum state whether local artifacts permit verification |
| Finance/Utility lead spec results | First audit generalizes from Main to "ALL" | 7/28 lead specs not significant | Medium | Per-sample breakdown of lead test results |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Stage 1-2 manifest + linguistic outputs | Yes (Section D) | Partial | Yes — exact timestamp dirs required | Medium | `get_latest_output_dir` picks latest; stale dirs could cause mismatch |
| H0.3 clarity residuals | Yes (Section D) | N | Yes — H0.3 must run first | Medium | Dependency chain not automated |
| Hassan PRisk CSV | Yes (Section D) | Y | No — static file | Low | Path verified: `inputs/FirmLevelRisk/firmquarter_2022q1.csv` |
| Panel builder execution | Yes (Section I) | Y | No | Low | `python -m f1d.variables.build_h11_prisk_uncertainty_panel` |
| Econometric runner execution | Yes (Section I) | Y | No | Low | Standard python module execution |
| Output directory resolution | Partial (K7 mentions stale dirs) | Y | Yes — multiple stale dirs exist | Medium | 3 timestamped dirs for base econometric; auditor must know which to inspect |
| Environment/package versions | No | N/A | Yes — linearmodels version matters | Low | Should document linearmodels version since PanelOLS behavior with non-unique index is version-dependent |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Identification threats | Y | Lead failure, OVB, simultaneity, autocorrelation all flagged | Lead failure severity slightly overclaimed | Low |
| Inference / clustering | Partial | Firm clustering documented; double-clustering recommended | Non-unique panel index implications for SE computation not discussed | Medium |
| FE and within-variation | Partial | Year FE coarseness flagged | But does not discuss that "within R-squared" reflects within-firm+year variation given non-unique index, not within-firm variation | Medium |
| Timing alignment | Y | Contemporaneous, lag, lead timing all correctly traced | | |
| Post-treatment controls | Y | Presentation-as-mediator concern flagged (K2) | | |
| Reverse causality | Y | Lead test as placebo correctly framed | But does not compare beta magnitudes across timing variants to diagnose persistence vs reverse causality | Medium |
| Endogenous sample selection | Y | CEO missingness flagged | | |
| Model-family-specific threats | Partial | Panel FE threats covered | Non-unique index implications not covered | Medium |
| Robustness adequacy | Y | Comprehensive 12-row table of missing checks | Appropriately demanding | |
| Interpretation discipline | Y | Causal language warning, economic magnitude concern flagged | | |
| Academic-integrity / auditability | Y | False standardization, docstring mismatch, warning suppression all flagged | | |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|---------------|-----|
| Overclaim: "ALL lead coefficients significant" | 7/28 are not; 2 have negative betas | Medium | A committee member reading "ALL" would overestimate the severity of the identification threat for non-Main samples | State "all 12 Main-sample specs; 21/28 overall" |
| "Primary keys: gvkey + year" without uniqueness check | 96.6% of (gvkey,year) cells have >1 call | Medium | A committee member would misunderstand the panel structure | Document as call-level panel with firm+year FE on non-unique index |
| "Highly persistent PRiskQ" without quantification | Autocorrelation not computed; rho=0.36 is moderate | Low | Overstating persistence inflates perceived identification threat | Compute and report autocorrelation coefficient |
| Verification log uses "python -c" snippets without full paths | Section I commands assume CWD = project root | Low | Not directly reproducible without context | Add explicit `cd` or full paths |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance on first audit? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|---------------------------------------|
| R1 | First-audit unsupported claim | Identification | Y | Medium | J6, L1, I#14 | "ALL lead coefficients significant" is overclaimed; 21/28 are significant, all 12 Main are | Lead model_diagnostics.csv | Committee misinformed about scope of lead failure | Correct to "all Main-sample lead specs (12/12); 21/28 overall" | N |
| R2 | First-audit omission | Panel structure | Y | Medium | A1, E3 | (gvkey, year) index is non-unique; first audit treats it as primary key | `groupby(['gvkey','year']).size().max()` = 38 | Panel structure misrepresented | Add explicit note about call-level unit and non-unique index | N |
| R3 | First-audit omission | Identification | Y | Medium | K2 | PRiskQ autocorrelation not quantified (rho=0.36) | Within-firm lag-1 autocorrelation computation | Persistence severity unquantified | Compute and report autocorrelation | N |
| R4 | First-audit omission | Interpretation | Y | Medium | K2/K6 | Lead beta magnitudes not compared to base (3x attenuation) | Base vs lead beta comparison | Misses key diagnostic for persistence vs reverse causality | Compare magnitudes across timing variants | N |
| R5 | First-audit severity error | Identification | Y | Medium | L1 | Lead failure labeled "Critical" when pattern suggests moderate persistence, not complete identification failure | Lead betas 3x smaller; autocorrelation rho=0.36 | Overcalibrated severity may discourage salvageable revisions | Downgrade to "High" with persistence-specific remediation | N |
| R6 | Underlying issue missed by first audit | Inference | Y | Low-Medium | All runners | Within-firm-year clustering from multiple calls per (gvkey, year) not discussed | 96.6% of cells have >1 call | SEs may be slightly understated | Test alternative clustering at (gvkey, year-quarter) level | N |
| R7 | Underlying issue underplayed by first audit | Interpretation | Y | Medium | K6, L14 | Economic magnitude of effects unclear: beta ~0.0001 means 1-SD PRiskQ increase raises uncertainty by ~0.02 ppts | model_diagnostics.csv betas | Statistical significance without economic significance | Report standardized betas and one-SD effect sizes | N |
| R8 | First-audit unsupported claim | Variable construction | Partial | Low | K2 | "PRiskQ is highly persistent" — asserted without evidence | First audit Section K2 | Overstates confidence in persistence explanation | Quantify with autocorrelation | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The panel index (gvkey, year) is not unique.** There are up to 38 calls per firm-year. The panel is call-level, not firm-year level. The first audit describes "Primary keys: gvkey + year" which is factually incorrect as a uniqueness statement.

2. **The lead "failure" shows a clear 3x attenuation pattern.** Lead betas are approximately one-third of base betas for the same DV. This pattern is more consistent with moderate PRiskQ persistence (rho=0.36) than with reverse causality of equal magnitude. A committee member reading only "ALL leads significant" would not know this.

3. **Not all lead specs are significant.** 7 of 28 lead regressions are not significant at p<0.05 (one-tailed), and 2 have negative betas. The failure is concentrated in the Main sample.

4. **The within-firm PRiskQ autocorrelation is 0.36** — moderate, not high. This is quantifiable and the first audit does not report it.

5. **Economic significance is unclear.** A one-standard-deviation increase in PRiskQ (~161 units) produces approximately a 0.02 percentage-point increase in Manager_QA_Uncertainty_pct. Whether this is economically meaningful requires context that neither the code nor the first audit provides.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|----------|-------------------|----------------|--------|------------------|
| 1 | Correct "ALL lead coefficients significant" to "all 12 Main-sample; 21/28 overall" with per-sample breakdown | Factual accuracy; prevents overclaiming severity | Trivial | High — removes a verifiable factual error |
| 2 | Add panel-structure note: (gvkey, year) is non-unique, call-level panel with firm+year FE | Corrects misleading "Primary keys" claim | Low | High — prevents structural misunderstanding |
| 3 | Compute and report PRiskQ within-firm autocorrelation (rho=0.36) | Quantifies the persistence mechanism behind lead failure | Low | High — enables evidence-based diagnosis |
| 4 | Compare base vs lead beta magnitudes (3x attenuation) | Key diagnostic for persistence vs reverse causality | Low | High — changes remediation strategy |
| 5 | Downgrade lead failure from "Critical" to "High" with persistence-specific framing | Severity calibration | Trivial | Medium — more defensible assessment |
| 6 | Add standardized beta / one-SD effect-size computation | Economic significance assessment | Low | Medium — answers "how big is this?" |
| 7 | Note linearmodels version and non-unique index behavior | Reproducibility | Trivial | Low |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
Mostly yes, with caveats. It is thorough, well-structured, and identifies the most important threats. However, it contains a factual overclaim about lead test results ("ALL" vs "all Main-sample"), misrepresents the panel structure (non-unique index), and fails to quantify the PRiskQ autocorrelation that would allow a committee to diagnose the lead failure mechanism.

**Biggest factual weakness:**
The claim that "ALL lead coefficients are positive and statistically significant" (J6, L1) is incorrect — 7/28 are not significant at p<0.05, and 2 have negative betas. The correct statement is that all 12 Main-sample lead specs show significant positive coefficients.

**Biggest completeness weakness:**
The first audit does not check or report that the (gvkey, year) panel index is non-unique (96.6% of cells have multiple calls, max 38). This is not a bug — call-level regressions with firm+year FE are valid — but it means the audit's "Primary keys" claim is wrong and the panel structure is misrepresented to readers.

**Biggest severity/judgment weakness:**
The lead placebo failure is labeled "Critical" and described as undermining "any claim that political risk causes increased speech uncertainty." This is too strong given that: (a) lead betas are 3x smaller than base betas, (b) PRiskQ autocorrelation is 0.36 (moderate), and (c) the attenuation pattern is consistent with persistence, not reverse causality. The appropriate framing is "High — requires discussion and potential first-differencing, but does not invalidate all descriptive findings."

**Single most important missed issue:**
The 3x attenuation of lead betas relative to base betas. This is the key diagnostic that distinguishes "persistence leakage" from "reverse causality" and was available in the data but not analyzed.

**Single most misleading claim:**
"ALL lead coefficients are positive and statistically significant" — factually inaccurate and causes readers to overestimate the identification threat.

**What should a thesis committee believe after reading this red-team review?**
The H11 suite is a competent implementation of a descriptive panel-FE analysis. The first-layer audit correctly identifies the key threats but slightly overclaims the severity of the lead failure. The suite is salvageable with (1) quarter-level time FE, (2) explicit discussion of PRiskQ persistence (rho=0.36), (3) comparison of base vs lead magnitudes to demonstrate the attenuation pattern, and (4) either first-differenced PRiskQ specifications or reframing as an associational (not causal) finding. The first-layer audit is reliable enough to guide revisions but should be corrected on the factual overclaims documented above.
