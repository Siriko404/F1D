# H2 Investment Efficiency -- Second-Layer Red-Team Audit

**Generated:** 2026-03-18
**Suite ID:** H2
**Auditor posture:** Hostile-but-fair, fresh-context, adversarial toward both implementation and first-layer audit
**First-layer audit:** `docs/provenance/H2.md`
**Suite entrypoint:** `src/f1d/econometric/run_h2_investment.py`
**Panel builder:** `src/f1d/variables/build_h2_investment_panel.py`
**Key upstream dependency:** `src/f1d/shared/variables/_compustat_engine.py` (function `_compute_biddle_residual`)

---

## A. Red-Team Bottom Line

The first-layer audit of H2 is **critically incomplete** -- it is a specification summary sheet, not an audit. It documents what the code *claims* to do (DVs, IVs, FE, controls, results) but performs zero verification of those claims against the actual implementation. It contains at least one factually incorrect claim (that CapexAt has no mechanical relation to InvestmentResidual). It omits all identification critique, all robustness assessment, all sample accounting, all dependency tracing, and all variable-dictionary verification. A thesis committee reading only the first-layer audit would learn the regression table layout and nothing about whether the results are trustworthy. Meanwhile, the implementation itself has a material specification issue: the Biddle (2009) first-stage OLS uses only SalesGrowth_lag as a predictor, omitting TobinQ_lag which is computed but unused -- a departure from the standard Biddle et al. (2009) specification. The panel builder docstring also documents H2b (leverage moderation) which is never tested in the runner. The suite is mechanically functional but underaudited.

---

## B. Scope and Objects Audited

| Object | Path | Lines Inspected |
|--------|------|----------------|
| First-layer audit | `docs/provenance/H2.md` | All (46 lines) |
| Runner | `src/f1d/econometric/run_h2_investment.py` | All (611 lines) |
| Panel builder | `src/f1d/variables/build_h2_investment_panel.py` | All (594 lines) |
| Compustat engine (Biddle residual) | `src/f1d/shared/variables/_compustat_engine.py` | Lines 470-768 (`_compute_biddle_residual`), 443-467 (`_winsorize_by_year`), 234-304 (Q4 helpers), 1027-1203 (`_compute_and_winsorize`) |
| InvestmentResidualBuilder | `src/f1d/shared/variables/investment_residual.py` | All (67 lines) |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` | All (193 lines) |
| BookLevBuilder | `src/f1d/shared/variables/book_lev.py` | All (57 lines) |
| Variable registry init | `src/f1d/shared/variables/__init__.py` | All (330 lines) |
| Financial utils (legacy) | `src/f1d/shared/financial_utils.py` | All (431 lines) -- confirmed not used by H2 pipeline |

---

## C. Audit-of-Audit Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Model/spec identification | 2/5 | Correct DV/IV/FE listing, but omits first-stage Biddle specification, omits H2b sub-hypothesis |
| Reproducibility commands | 0/5 | No reproduction commands provided at all |
| Dependency tracing | 1/5 | Lists only two files (panel, runner); omits `_compustat_engine.py`, `panel_utils.py`, FF48 zip, Compustat raw |
| Raw data provenance | 0/5 | No mention of Compustat parquet path, FF48 SIC codes, linguistic variable sources |
| Merge/sample audit | 0/5 | No merge verification, no sample accounting, no attrition documentation |
| Variable dictionary completeness | 2/5 | Lists variable names but no definitions, formulas, or data sources |
| Outlier/missing-data rules | 0/5 | No mention of winsorization (1%/99% by year), inf replacement, or missing-data handling |
| Estimation spec register | 3/5 | 8-column layout documented; missing formula-level detail |
| Verification log quality | 0/5 | No verification log exists |
| Known issues section | 0/5 | No known issues documented |
| Identification critique | 0/5 | No discussion of endogeneity, reverse causality, or omitted variable bias |
| Econometric implementation critique | 0/5 | No analysis of PanelOLS settings, clustering, or FE specification |
| Robustness critique | 0/5 | No robustness discussion whatsoever |
| Academic-integrity critique | 0/5 | No one-tailed test justification analysis, no p-hacking discussion |
| Severity calibration | N/A | No issues identified to calibrate |
| Final thesis verdict support | 0/5 | No verdict provided |

**Overall:** 8/80 (10%). The first-layer audit is a specification summary, not an audit.

---

## D. Claim Verification Matrix

| Claim ID | First-layer claim | Section | Verified? | Evidence checked | Red-team verdict | Notes |
|----------|-------------------|---------|-----------|-----------------|-----------------|-------|
| C1 | DVs = InvestmentResidual (t), InvestmentResidual_lead (t+1) | Spec table | Yes | `MODEL_SPECS` lines 107-115 of runner | VERIFIED FACT | Correct |
| C2 | 4 simultaneous IVs: CEO/Manager x QA/Pres Uncertainty | Spec table | Yes | `KEY_IVS` lines 81-85 of runner | VERIFIED FACT | Correct |
| C3 | 8 Base Controls: Size, TobinsQ, ROA, BookLev, CapexAt, CashHoldings, DividendPayer, OCF_Volatility | Spec table | Yes | `BASE_CONTROLS` lines 88-97 of runner | VERIFIED FACT | Correct |
| C4 | Extended Controls (+4): Volatility, RD_Intensity, Entire_All_Negative_pct, Analyst_QA_Uncertainty_pct | Spec table | Yes | `EXTENDED_CONTROLS` lines 99-104 of runner | VERIFIED FACT | Correct |
| C5 | CashFlow, SalesGrowth excluded (Biddle first-stage inputs) | Spec/Design | Partially | CashFlow/SalesGrowth absent from `BASE_CONTROLS` and `EXTENDED_CONTROLS` | VERIFIED FACT (exclusion); VERIFIED ERROR (rationale) | See C8 |
| C6 | FE: Industry(FF12) + FiscalYear / Firm + FiscalYear | Spec table | Yes | Lines 256-274 of runner | VERIFIED FACT | Industry via `other_effects`, Firm via `EntityEffects` |
| C7 | Firm-clustered SEs | Spec table | Yes | `cov_type="clustered", cluster_entity=True` lines 269, 274 | VERIFIED FACT | |
| C8 | "InvestmentResidual is not mechanically related to BookLev, CashHoldings, or CapexAt" | Design #3 | No | CapexAt = capxy/at_lag; InvestmentResidual = (capxy+xrdy+aqcy-sppey)/at_lag | **VERIFIED ERROR** | capxy appears in BOTH numerators and at_lag in BOTH denominators -- they share two components. The claim is factually incorrect. |
| C9 | 8 model specifications (2 DVs x 2 FE x 2 controls) | Spec table | Yes | `MODEL_SPECS` has 8 entries | VERIFIED FACT | |
| C10 | One-tailed: beta < 0 | Spec table | Yes | `p_one = p_two / 2 if beta < 0 else 1 - p_two / 2` line 300 | VERIFIED FACT | Correctly implemented |
| C11 | Main sample only (FF12 not in {8, 11}) | Spec table | Yes | `filter_main_sample` lines 188-192 | VERIFIED FACT | |
| C12 | Manager QA Uncertainty 2/8 significant | Results | Unverifiable | No output artifacts checked; no reproduction run | UNVERIFIED | Cannot verify without running code or inspecting saved outputs |
| C13 | Time index: fyearq_int (fiscal year) | Spec table | Yes | `df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])` line 253 | VERIFIED FACT | |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims

| Issue ID | Claim/statement | Why unsupported or weak | Severity | What evidence was missing | Corrected formulation |
|----------|-----------------|------------------------|----------|--------------------------|----------------------|
| E1 | "InvestmentResidual is not mechanically related to... CapexAt" (Design Decision #3) | CapexAt = capxy_Q4 / atq; InvestmentResidual numerator = capxy + xrdy + aqcy - sppey, denominator = at_lag. capxy is a component of both. at_lag and atq are nearly identical for the same firm-year. The correlation is not "mechanical" in the sense of algebraic identity, but there is substantial shared component overlap. | High | Code inspection of `_compute_biddle_residual` (line 599-604) and `_compute_and_winsorize` (lines 1079-1085) | "CapexAt shares the capxy numerator component and similar atq denominator with the InvestmentResidual construction; partial mechanical overlap exists but is attenuated by the residual-from-OLS step" |
| E2 | Implicit claim that Biddle (2009) specification is correctly implemented | The first audit cites "Biddle (2009)" repeatedly but never verifies the first-stage specification | High | The actual Biddle et al. (2009) paper uses SalesGrowth as the sole first-stage predictor in the baseline specification (Equation 1), which matches the code. However, TobinQ_lag is computed (line 669) but unused in the first-stage OLS (line 718), creating dead code that suggests an incomplete implementation or abandoned extension. | "First-stage uses SalesGrowth_lag only (matching Biddle 2009 Equation 1 baseline); TobinQ_lag is computed but not used (dead code)" |
| E3 | Results claims (2/8 significant for Manager QA) | No output artifact was inspected to verify; the first audit does not reference any specific output file | Medium | Actual model_diagnostics.csv or regression_results files | "Results as reported by runner console output; not independently verified against saved artifacts" |

---

## F. False Positives in the First Audit

| Issue ID | First-audit criticism | Why false/overstated | Evidence | Severity of audit error | Corrected view |
|----------|----------------------|---------------------|----------|------------------------|---------------|

The first-layer audit raises zero criticisms, so there are no false positives to evaluate. This is itself a finding: the audit is pure description with no critical analysis.

---

## G. Missed Issues

| Issue ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|----------|----------|-------------|----------|----------|--------------------------|-------------|----------------|
| G1 | Specification | **CapexAt shares capxy component with InvestmentResidual DV** | `_compute_biddle_residual` line 599: Investment numerator includes capxy. `_compute_and_winsorize` line 1079: CapexAt = capxy_annual / atq_annual_lag1. Both use capxy from Q4 rows. | High | First audit did not trace variable definitions upstream to `_compustat_engine.py` | Including CapexAt as a control in a regression where the DV is a residual that mechanically contains capxy introduces partial mechanical correlation. The OLS residualization in the first stage mitigates but does not eliminate this. Could bias the coefficient on CapexAt and, through collinearity, affect uncertainty IV estimates. | Document the shared-component overlap. Consider dropping CapexAt from controls or testing sensitivity to its inclusion/exclusion. |
| G2 | Specification | **H2b (leverage moderation) documented but never tested** | Panel builder docstring lines 32-33: "H2b: leverage attenuates the uncertainty-investment link (beta3 > 0)". Runner contains no interaction term (grep for "interaction", "BookLev.*Uncertainty", "H2b" returns no matches). | Medium | First audit did not compare docstring claims to actual implementation | A documented sub-hypothesis is never tested. Either the docstring is stale or the test was abandoned without documentation. Either way, provenance is incomplete. | Remove H2b from docstring if abandoned, or implement the interaction test if it is part of the thesis. |
| G3 | DV construction | **TobinQ_lag computed as dead code in Biddle first-stage** | `_compute_biddle_residual` line 669: `annual["TobinQ_lag"] = ...`. Line 705-718: OLS uses only `["Investment", "SalesGrowth_lag"]`. TobinQ_lag is never referenced in the regression. | Medium | First audit did not read `_compustat_engine.py` at all | Dead code suggests an incomplete implementation. If TobinQ was intended as a Biddle first-stage predictor, its absence changes the residual. If it was correctly omitted (matching Biddle 2009 Equation 1), the dead code is misleading. | Remove TobinQ_lag computation or add a comment explaining why it is computed but not used. |
| G4 | Sample accounting | **No attrition documentation in first audit** | The runner generates `sample_attrition.csv` (lines 567-573) but the first audit documents none of the sample filtering steps: full panel -> main sample -> DV non-missing -> complete cases -> min 5 calls/firm. | High | First audit does not document any sample flow | A committee cannot evaluate whether the sample is representative without knowing how many observations are lost at each step. | Add full sample attrition table to provenance doc. |
| G5 | Identification | **No discussion of endogeneity or reverse causality** | Investment decisions are made by the same managers who speak in earnings calls. Managerial uncertainty in speech could reflect knowledge of poor investment prospects (reverse causality) rather than causing investment inefficiency. No IV, no diff-in-diff, no exogenous shock identification strategy. | High | First audit performs no identification analysis | Without identification strategy, the causal claim in H2 ("higher uncertainty -> lower investment efficiency") is unsupported. The regression establishes association only. | Document that H2 estimates a reduced-form association, not a causal effect. Discuss potential endogeneity and what additional identification would be needed for causal claims. |
| G6 | Robustness | **No robustness analysis documented or discussed** | No alternative Biddle specifications (e.g., absolute residual, signed residual decomposition), no alternative IV definitions, no subsample analysis, no placebo tests. | Medium | First audit has no robustness section | Committee cannot assess sensitivity of findings to specification choices. | Add robustness discussion: alternative DV definitions, subsample stability, sensitivity to control set. |
| G7 | Econometric | **check_rank=False in PanelOLS for industry FE specs** | Runner line 267: `check_rank=False`. This disables the rank check that would detect near-collinearity or absorbed variables. | Low-Medium | First audit does not examine PanelOLS configuration | Could mask collinearity problems in the exog matrix without warning. | Document why check_rank is disabled (performance? known false positives?) or enable it. |
| G8 | Winsorization | **Triple-layer winsorization for some variables** | InvestmentResidual is winsorized inside `_compute_biddle_residual` (line 741), then all Compustat variables (except those in `skip_winsorize`) are winsorized again in `_compute_and_winsorize` (lines 1194-1201) -- but InvestmentResidual IS in `skip_winsorize` (line 1190). So InvestmentResidual is correctly single-winsorized. However, SalesGrowth is in `skip_winsorize` but is also NOT a final control in H2 (excluded). CashFlow is also in skip list. No issue for H2 specifically, but the first audit documents none of this winsorization logic. | Low | First audit mentions nothing about winsorization | Committee cannot verify data cleaning choices. | Document winsorization strategy in provenance. |
| G9 | Dependency tracing | **Multiple upstream dependencies untraced** | The suite depends on: (1) `inputs/comp_na_daily_all/comp_na_daily_all.parquet`, (2) `inputs/FF1248/Siccodes48.zip`, (3) `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`, (4) `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`, (5) `config/project.yaml`, (6) `config/variables.yaml`. The first audit lists none of these. | Medium | First audit lists only two code files | Reproduction is impossible without knowing all inputs. | Add complete dependency tree to provenance. |
| G10 | Unit of observation | **Call-level analysis with firm-year DV may inflate significance** | InvestmentResidual is an annual firm-level variable matched to all calls in that firm-year (via the merge-back step in `_compute_biddle_residual` lines 751-768 and the lead construction in `create_lead_variable`). Multiple calls per firm-year share the identical DV value. Firm-clustered SEs partially address this, but within-year call-level variation in IVs is exploited against a constant DV within firm-year. | Medium | First audit does not discuss the unit-of-observation mismatch | Effective N may be much lower than reported N. Within-firm-year variation in uncertainty (across Q1-Q4 calls) is mapped to an identical investment residual, potentially inflating t-statistics despite clustering. | Document the call-level vs. firm-year DV mismatch. Consider firm-year level analysis as a robustness check (collapse to one obs per firm-year). |
| G11 | Reproducibility | **No reproduction commands or verification steps** | The first audit contains zero runnable commands. | High | The first audit is a specification summary, not a reproducibility document. | A third party cannot reproduce any result. | Add: `python -m f1d.variables.build_h2_investment_panel` and `python -m f1d.econometric.run_h2_investment` with expected output checksums. |
| G12 | One-tailed test | **One-tailed test applied to all 4 IVs simultaneously without correction** | 4 IVs tested simultaneously across 8 specs = 32 tests. One-tailed test doubles the effective alpha for the predicted direction. No multiple-testing correction is applied. | Medium | First audit does not examine the testing framework | With 32 one-tailed tests at alpha=0.05, expected false positives under the null are 1.6. Finding 2/32 significant is barely above chance. | Document multiple-testing exposure. Consider Bonferroni or BH correction, or at minimum report it. |

---

## H. Severity Recalibration

| Issue ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----------|--------|-------------------|-------------------|------------------|---------------|
| N/A | N/A | N/A | N/A | First audit raises no issues to recalibrate | N/A |

The first-layer audit identifies zero issues, so there is nothing to recalibrate. All issues in Section G are newly identified by this red-team audit.

---

## I. Completeness Gaps

| Missing/incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|------------------------|---------------|----------|----------|-------------------------------|
| Variable definitions | Audit lists variable names without formulas | E.g., "InvestmentResidual" is listed but the Biddle first-stage formula is never stated | High | Full formula: Investment = (capxy + xrdy + aqcy - sppey) / at_lag; OLS by FF48-year cell: Investment ~ SalesGrowth_lag; Residual = actual - predicted |
| Winsorization rules | Not mentioned at all | `_winsorize_by_year` at 1%/99% with min 10 obs per year group applies to all Compustat controls | Medium | Document: 1%/99% by-year winsorization for all continuous controls; InvestmentResidual winsorized once post-OLS; DividendPayer binary (not winsorized) |
| Missing-data handling | Not mentioned | fillna(0) for xrdy/aqcy/sppey in investment numerator; inf->NaN replacement; complete-case analysis at regression stage | Medium | Document all fillna decisions, especially the Biddle convention of treating missing R&D/acquisitions/asset-sales as zero |
| Sample period | Not explicitly documented | "2002-2018" appears in runner report template (line 472) but not in the first audit | Low | State sample period explicitly |
| MIN_CALLS_PER_FIRM | Not documented | Runner line 117: `MIN_CALLS_PER_FIRM = 5` -- firms with fewer than 5 earnings calls are dropped | Medium | Document the minimum-calls threshold and its impact on sample composition |
| Biddle first-stage diagnostics | Not documented | Number of FF48-year cells run, skipped (too few obs), skipped (missing SIC) | Medium | Include first-stage OLS diagnostics: how many cells, how many firm-years get valid residuals |
| Lead variable construction | Not documented | Complex fiscal-year-based lead with gap validation (lines 254-396 of panel builder) | High | Document: InvestmentResidual_lead = end-of-fiscal-year residual from fiscal year t+1; gap validation ensures consecutive fyearq; NaN for last fiscal year per firm |
| Industry FE implementation | Not documented | Industry FE via PanelOLS `other_effects` (absorbed, not dummies) vs. Firm FE via `EntityEffects` formula | Low | Clarify that industry FE uses absorbed FF12 dummies, not explicit C() dummies |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented it? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|---------------------------|-----------|-------------------|------|---------------|
| Load raw Compustat parquet | No | Yes (code path verified) | `inputs/comp_na_daily_all/comp_na_daily_all.parquet` | Medium | File must exist; no checksum or version documented |
| Load FF48 SIC codes | No | Yes (code path verified) | `inputs/FF1248/Siccodes48.zip` | Medium | Required for Biddle first-stage industry classification |
| Load master manifest | No | Yes (code path verified) | `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet` | Medium | Depends on prior pipeline stage; "latest" symlink is non-deterministic |
| Load linguistic variables | No | Yes (code path verified) | `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet` | Medium | Per-year files; depends on NLP pipeline |
| Load config files | No | Yes (code path verified) | `config/project.yaml`, `config/variables.yaml` | Low | Year range and variable config |
| Build panel | No | Partially (code reviewed) | CompustatEngine singleton cache | Low | First call populates cache; subsequent calls reuse |
| Run regressions | No | Partially (code reviewed) | linearmodels PanelOLS version | Medium | Results may vary with library version |
| End-to-end reproduction | No | No | All above | High | No reproduction was attempted; no expected output hashes documented |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Causal identification | No | No discussion at all | Reverse causality (managers who know about bad investments speak more uncertainly); omitted variable bias (firm distress drives both uncertainty and investment); no instrumental variable strategy | High |
| DV construction validity | No | Biddle (2009) cited but first-stage specification not verified or documented | First-stage uses only SalesGrowth_lag (matches Biddle baseline but not extended specs); TobinQ_lag is dead code | Medium |
| Unit of observation | No | Not discussed | Call-level analysis with firm-year DV; multiple calls per firm-year share identical DV | Medium |
| Standard error adequacy | Partially | Firm-clustered SEs mentioned | Adequate for within-firm correlation but does not address the call-level/firm-year DV mismatch; consider two-way clustering (firm + year) | Medium |
| Multiple testing | No | Not discussed | 32 one-tailed tests (4 IVs x 8 specs) with no correction | Medium |
| Economic magnitude | No | Not discussed | Coefficients reported but economic significance (effect size in terms of investment efficiency units) not interpreted | Medium |
| One-tailed justification | No | Not discussed | One-tailed test requires strong prior justification; the audit does not evaluate whether the prior is adequately supported | Low-Medium |
| Contemporaneous vs. lead DV | No | Both DVs listed but not discussed | Why test both InvestmentResidual(t) and InvestmentResidual_lead(t+1)? The timing justification is absent | Low |

---

## L. Audit-Safety / Academic-Integrity Assessment

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|---------------|-----|
| First audit is pure specification summary | 46 lines of doc, zero criticisms, zero verification steps | High | Creates false confidence that the suite has been audited; a committee might rely on it as evidence of due diligence | Replace with a genuine audit containing verification log, identification critique, and known issues |
| No falsification / placebo test discussion | No mention in first audit or runner | Medium | Without falsification tests, the significant results (2/8 for Manager QA) could be spurious | Add discussion of what would constitute a falsification failure |
| No discussion of null results | 30/32 IV-spec combinations are insignificant; first audit reports this but does not discuss implications | Medium | The overwhelmingly null results may be the most important finding; silence on this understates the evidence | Discuss whether the null results suggest the hypothesis is unsupported |

---

## M. Master Red-Team Issue Register

| Issue ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis-standard reliance? |
|----------|------|----------|-----------|----------|----------|-------------|----------|-------------|----------------|--------------------------------|
| G1 | VERIFIED ERROR | Variable overlap | Yes | High | `_compustat_engine.py` lines 599, 1079 | CapexAt shares capxy component with InvestmentResidual DV; first audit falsely claims no mechanical relation | Both use capxy/at variants | Partial mechanical correlation in regression | Test sensitivity to CapexAt exclusion; correct provenance claim | Yes -- factual error in audit |
| G2 | VERIFIED MISSED ISSUE | Stale docstring | Yes | Medium | `build_h2_investment_panel.py` lines 32-33 | H2b (leverage moderation) documented but never tested | grep returns no interaction terms in runner | Incomplete provenance | Remove stale docstring or implement test | No |
| G3 | VERIFIED MISSED ISSUE | Dead code | Yes | Medium | `_compustat_engine.py` lines 669-670 | TobinQ_lag computed but unused in Biddle first-stage OLS | First-stage `reg_cols` at line 705 excludes TobinQ_lag | Misleading code; potential incomplete implementation | Remove dead code or document rationale | No |
| G4 | VERIFIED MISSED ISSUE | Sample accounting | Yes | High | Runner lines 567-573 | No attrition documentation in first audit despite runner generating it | `generate_attrition_table` called but results not documented | Committee cannot evaluate sample representativeness | Add attrition table to provenance | Yes |
| G5 | VERIFIED MISSED ISSUE | Identification | Yes | High | Runner; entire suite | No endogeneity / reverse causality discussion | Reduced-form OLS with no identification strategy | Causal interpretation unsupported | Add identification limitations section | Yes |
| G6 | VERIFIED MISSED ISSUE | Robustness | Yes | Medium | First audit | No robustness analysis of any kind | No alternative specs, no placebo, no subsample analysis | Findings appear fragile (only 2/32 significant) | Add robustness discussion | No (but strongly recommended) |
| G7 | VERIFIED MISSED ISSUE | Econometric config | Yes | Low-Medium | Runner line 267 | check_rank=False disables collinearity detection | PanelOLS constructor parameter | Could mask rank deficiency | Enable or document rationale | No |
| G8 | VERIFIED FACT | Winsorization | Yes | Low | `_compustat_engine.py` lines 1185-1201 | Winsorization correctly applied; InvestmentResidual in skip_winsorize list | Code inspection | No double-winsorization for H2 DV | Document in provenance | No |
| G9 | VERIFIED MISSED ISSUE | Dependencies | Yes | Medium | Panel builder; shared modules | 6+ upstream data dependencies untraced | Code path analysis | Reproduction impossible without dependency map | Add dependency tree | No (but recommended) |
| G10 | VERIFIED MISSED ISSUE | Unit of observation | Yes | Medium | `_compute_biddle_residual` lines 751-768; runner | Call-level IVs regressed on firm-year DV | InvestmentResidual identical for all calls in same firm-year | Inflated effective N; potentially misleading standard errors | Discuss; add firm-year-level robustness check | No (but recommended) |
| G11 | VERIFIED MISSED ISSUE | Reproducibility | Yes | High | First audit | Zero reproduction commands | No commands in doc | Third party cannot reproduce | Add commands with expected outputs | Yes |
| G12 | VERIFIED MISSED ISSUE | Multiple testing | Yes | Medium | Runner lines 293-311 | 32 one-tailed tests with no correction | 4 IVs x 8 specs | Expected 1.6 false positives; 2 found barely exceeds chance | Document exposure; consider correction | No (but recommended) |
| E1 | VERIFIED ERROR | Factual claim | Yes | High | `docs/provenance/H2.md` Design Decision #3 | "InvestmentResidual is not mechanically related to... CapexAt" is factually incorrect | Both use capxy in numerator and atq variants in denominator | Misleading provenance | Correct the claim | Yes |

---

## N. What a Committee Would Still Not Know

After reading the first-layer audit, a thesis committee would still not know:

1. **What the Biddle (2009) first-stage specification actually is** -- the formula for Investment and the OLS specification are never stated
2. **How InvestmentResidual_lead is constructed** -- the fiscal-year-based lead with gap validation is a critical and complex construction step that is entirely undocumented
3. **How many observations are lost at each filtering step** -- no attrition table
4. **Whether CapexAt creates a mechanical correlation problem** -- the first audit incorrectly claims there is none
5. **Why the results are overwhelmingly null (30/32 non-significant)** and what that implies for H2
6. **Whether the causal interpretation is valid** -- no identification discussion
7. **What data files are needed to reproduce the results** -- no dependency list
8. **How winsorization is handled** -- not mentioned
9. **Whether H2b (leverage moderation) was tested or abandoned** -- the docstring mentions it but no test exists
10. **Whether the 2/32 significant results survive multiple testing correction** -- no correction applied or discussed
11. **Whether the call-level unit of observation inflates significance** relative to firm-year analysis
12. **What the economic magnitude of the estimated effects is** -- only statistical significance is reported

---

## O. Priority Fixes

| Priority | Fix | Why it matters | Effort | Credibility gain |
|----------|-----|----------------|--------|-----------------|
| P0 | Correct the false claim that CapexAt has no mechanical relation to InvestmentResidual | Factual error in provenance documentation; directly misleading | Low (edit one sentence) | High |
| P0 | Add identification limitations section discussing endogeneity and reverse causality | Committee will immediately ask about causality; the current doc is silent | Medium (write 1-2 paragraphs) | High |
| P1 | Add complete sample attrition table | Standard for any regression-based thesis chapter | Low (runner already generates it; copy to provenance) | High |
| P1 | Add full variable definitions with formulas | Biddle first-stage, lead construction, all controls | Medium | High |
| P1 | Add reproduction commands | Currently zero commands documented | Low | High |
| P2 | Remove or document H2b stale docstring | Provenance inconsistency | Low | Medium |
| P2 | Remove TobinQ_lag dead code or add comment | Code cleanliness; prevents confusion about first-stage spec | Low | Medium |
| P2 | Add dependency tree (all input files) | Reproduction requires knowing all inputs | Low-Medium | Medium |
| P2 | Discuss null result implications (30/32 non-significant) | The null is arguably the most important finding | Medium | High |
| P3 | Add multiple testing discussion | 32 one-tailed tests at alpha=0.05 | Low | Medium |
| P3 | Add firm-year-level robustness check | Address call-level vs. firm-year DV mismatch | Medium-High (requires new analysis) | Medium |
| P3 | Document winsorization strategy | Standard for transparency | Low | Low-Medium |

---

## P. Final Red-Team Readiness Statement

**Is the first-layer audit sufficient for thesis-standard reliance?** No.

The first-layer audit for H2 is a specification summary sheet that documents the regression table layout (DVs, IVs, controls, FE, results counts). It is not an audit. It contains one verified factual error (the claim that CapexAt has no mechanical relation to InvestmentResidual), performs zero verification of any claim against actual code, omits all identification critique, omits all sample accounting, omits all dependency tracing, omits all robustness discussion, and provides no reproduction commands. A thesis committee reading this document would learn the 8-column regression layout and nothing about whether the results are trustworthy or reproducible.

The **implementation itself** is mechanically competent: the Biddle residual construction follows the standard approach (with the minor note that TobinQ_lag is dead code), the panel builder has proper zero-row-delta merge guards, the lead variable construction correctly handles fiscal-year gaps, and the runner correctly implements one-tailed p-values. The overwhelmingly null results (2/32 significant, barely above chance expectation of 1.6 under the null) are honestly reported.

**To reach thesis-standard:**
- Fix the factual error about CapexAt (P0)
- Add identification limitations (P0)
- Add sample attrition, variable definitions, and reproduction commands (P1)
- Discuss the implications of predominantly null findings (P2)
- The first-layer audit needs to be expanded from a 46-line summary to a substantive audit document

**Estimated effort to remedy:** 4-6 hours of documentation work; no code changes required for core functionality.
