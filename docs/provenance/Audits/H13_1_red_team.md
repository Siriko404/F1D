# H13.1 Competition-Moderated Capex -- Second-Layer Red-Team Audit

**Audit Date:** 2026-03-18
**Auditor:** Independent Red-Team (Layer 2)
**Suite ID:** H13.1
**First-Layer Audit:** `docs/provenance/H13_1.md`
**Suite Entrypoint:** `src/f1d/econometric/run_h13_1_competition.py`
**Panel Builder:** Shares `src/f1d/variables/build_h13_capex_panel.py` (H13 panel); TNIC merged at runtime

---

## A. Executive Summary

The first-layer audit is a brief provenance document rather than a full red-team audit. It accurately describes the basic design and code structure of H13.1 but omits several material issues: (1) a potential year-key mismatch between TNIC data (calendar year of `datadate`) and the panel merge key (`fyearq_int`, the Compustat fiscal year), which could misalign ~30% of firm-years; (2) no centering or standardization of interaction term components, making the main-effect coefficients (b1, b2) uninterpretable at non-zero values of the moderator; (3) within-variation statistics are stated without any code or log evidence; (4) the TNIC3HHI measure is contemporaneous (same fiscal year as the call), raising endogeneity concerns for a moderator; (5) the LaTeX table declares 6 data columns (`"c" * 6`) but only 4 IVs per panel, producing a malformed table. The audit is factually correct on what it covers but materially incomplete as a thesis-standard review.

---

## B. Audit-the-Audit: First-Layer Claims Verification

| # | First-Layer Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | "Each IV gets its own regression with its own interaction term (one IV per model)" | **VERIFIED FACT** | `run_h13_1_competition.py` L99-108: 4 IVs x 2 DVs x 2 FE = 16 models, each with one IV + tnic3hhi + interaction |
| 2 | "16 models: 4 IVs x 2 DVs x 2 FE" | **VERIFIED FACT** | `_build_model_specs()` L99-108 generates exactly 16 specs |
| 3 | "TNIC3HHI merged on (gvkey, fyearq_int)" | **VERIFIED FACT (with caveat)** | L168-178 performs merge on `[_gvkey_int, fyearq_int]`. See issue C-1 below for year-key mismatch concern |
| 4 | "Coverage: 98.3% of calls (111,000 / 112,968)" | **UNVERIFIED** | No runtime output available; cannot validate without executing the pipeline. Plausible given 188K TNIC rows and typical panel sizes |
| 5 | "Within-industry variation: 85.7%" | **UNVERIFIED** | Not computed anywhere in the codebase. No log or output file supports this statistic |
| 6 | "Within-firm variation: 27.8%" | **UNVERIFIED** | Same as above -- no code computes within-firm R-squared of tnic3hhi on firm FE |
| 7 | "b3 well-identified via call-level IV variation" | **REFEREE JUDGMENT -- DISPUTED** | The interaction b3 = IV * HHI. Under Firm FE, both the IV (call-level) and HHI (firm-year) are demeaned by firm mean. If HHI has only 27.8% within-firm variation (per the unverified claim), the demeaned HHI is near zero for most firms, and b3 identification relies on thin cross-temporal HHI variation multiplied by IV variation. The claim is arguable but overstated |
| 8 | "Controls: Extended" | **VERIFIED FACT** | L80-84: exactly matches H13's EXTENDED_CONTROLS list |
| 9 | "SEs: Firm-clustered" | **VERIFIED FACT** | L283: `cov_type="clustered", cluster_entity=True` for industry FE; L288: same for firm FE |
| 10 | "MIN_CALLS_PER_FIRM: 5" | **VERIFIED FACT** | L89 |
| 11 | "Main only (FF12 not in {8, 11})" | **VERIFIED FACT** | L192 |
| 12 | "1/16 significant at p<0.05: Col 7, CEO_QA x HHI, Firm FE, DV=CapexAt, b3=-0.0063, p=0.027" | **UNVERIFIED** | Cannot verify without running the pipeline. The column numbering is from a "pre-4IV run" per the audit text itself |
| 13 | "Loads existing H13 panel + merges TNIC data at runtime. No panel builder changes needed." | **VERIFIED FACT** | L133-186: `load_panel_with_tnic()` loads H13 panel and merges TNIC at runtime |

---

## C. Verified Errors

### C-1. TNIC Year-Key Mismatch Risk (MAJOR)

**Issue:** The TNIC3HHI data readme explicitly states: "the year field in this database is based on Compustat calendar years obtained as the first four digits of the YYYYMMDD datadate variable." This means TNIC `year` = `calendar_year(datadate)`, which equals `int(datadate[:4])`. However, the panel merge uses `fyearq_int`, which is the Compustat *fiscal* year. For firms with non-December fiscal year-ends (~30% of the panel), `fyearq` can differ from `calendar_year(datadate)` by one year. For example, a firm with a September 30 fiscal year-end filing a 10-K for FY2019 will have `fyearq=2019` but `datadate=20190930`, so the TNIC record's `year=2019` happens to match in this case. But consider a firm with a January 31 fiscal year-end: `fyearq=2019` but `datadate=20200131`, so TNIC `year=2020` while the panel tries to merge on `fyearq_int=2019`, resulting in a miss or mismatch.

**Severity:** Potentially affects ~5-15% of firm-year merges (the subset of non-December FYE firms where calendar year != fiscal year). The actual impact depends on the distribution of fiscal year-ends in the sample. Could inflate the 1.7% unmatched rate reported by the audit.

**Evidence:** `inputs/TNIC3HHIdata/Readme_tnic3HHIData.txt` Technical Note 1; `run_h13_1_competition.py` L173 merges on `fyearq_int`.

**First-layer audit status:** Not mentioned.

### C-2. LaTeX Table Column Count Mismatch (MINOR)

**Issue:** `_save_latex_table()` at L425 declares `"\\begin{tabular}{l" + "c" * 6 + "}"`, creating a 7-column table (1 label + 6 data columns). However, each panel has only 4 IVs (4 data columns). The table will have 2 empty columns or LaTeX compilation errors.

**Evidence:** L425 vs L360 (`results_for_fe` has at most 4 entries per panel).

**First-layer audit status:** Not mentioned.

---

## D. Verified Missed Issues

### D-1. No Centering/Standardization of Interaction Components (MAJOR -- Econometric)

**Issue:** The interaction term `IV_k x tnic3hhi` is constructed as a raw product (L220: `df[interaction_col] = df[iv] * df["tnic3hhi"]`). Neither the IV nor HHI is centered (demeaned) or standardized before forming the interaction. This means:

1. The coefficient b1 on IV_k represents the effect of IV when `tnic3hhi = 0`. Since HHI ranges from 0.01 to 1.0 with mean 0.275, this is an extreme extrapolation to a market structure that essentially does not exist in the data.
2. The coefficient b2 on `tnic3hhi` represents the effect of HHI when `IV_k = 0`. Since the IVs are percentage measures that are typically > 0, this is also an extrapolation.
3. Multicollinearity between the interaction term and its components is maximized when components are not centered.

**Standard practice:** Aiken & West (1991), Brambor et al. (2006) -- center continuous variables before forming interactions so that main effects are interpretable at meaningful values.

**First-layer audit status:** Not mentioned.

### D-2. TNIC3HHI Is Contemporaneous, Not Pre-Determined (MODERATE -- Identification)

**Issue:** TNIC3HHI is merged on the same fiscal year as the earnings call and the DV (CapexAt). The competition measure is thus contemporaneous with both the uncertainty language (IV) and the investment outcome (DV). If a firm's investment decisions (capex) and its competitive positioning (HHI) are jointly determined -- which is plausible since firms that invest heavily may change their competitive position -- then the moderator is endogenous. Standard practice for moderation analysis uses a lagged moderator (HHI_{t-1}) to ensure the moderator is pre-determined relative to the outcome.

**First-layer audit status:** Not mentioned. The audit notes the merge is on `(gvkey, fyearq_int)` but does not flag the contemporaneity.

### D-3. No Robustness Checks (MODERATE -- Completeness)

**Issue:** The suite runs a single specification with no robustness variants:
- No lagged HHI specification
- No alternative competition measures (e.g., HHI from census data, number of TNIC peers)
- No split-sample analysis (high vs low HHI subsamples)
- No placebo/falsification tests
- No examination of whether results are driven by outliers in HHI distribution

For a thesis-standard moderation analysis, at least a lagged moderator and an alternative measure would be expected.

**First-layer audit status:** Not mentioned.

### D-4. Sample Accounting Gap: TNIC-Induced Attrition Not Fully Tracked (MINOR)

**Issue:** The attrition table (L602-611) reports three stages: Full panel, Main sample, and "After TNIC + complete-case + min-calls." This collapses multiple distinct attrition sources (TNIC merge failure, complete-case on controls, and min-calls filter) into a single step. Good practice would separate these, particularly because TNIC merge failure is a novel source of selection (firms without 10-K filings in the SEC Edgar database are excluded from TNIC, which may systematically exclude certain firm types).

**First-layer audit status:** Not mentioned.

### D-5. check_rank=False Suppresses Rank Deficiency Warnings (MINOR)

**Issue:** L281 sets `check_rank=False` in the PanelOLS constructor for industry FE models. This suppresses warnings about collinear regressors. Given that the interaction term is a product of two included regressors without centering, near-collinearity is plausible. The rank check should be enabled or the condition number reported.

**First-layer audit status:** Not mentioned.

### D-6. Interpretation of Negative Interaction May Be Reversed (MODERATE -- Econometric Interpretation)

**Issue:** The audit states: "in more concentrated markets (high HHI), CEO Q&A uncertainty has a weaker (more negative) effect on capex. This suggests competitive pressure amplifies the uncertainty-investment link."

Let us verify: If b1 < 0 (uncertainty reduces capex) and b3 < 0 (negative interaction), then at high HHI, the total marginal effect of uncertainty = b1 + b3 * HHI becomes *more* negative (larger in magnitude). The audit says "weaker (more negative)" which is contradictory -- "weaker" means closer to zero, "more negative" means further from zero. The correct interpretation depends on the sign of b1. Without centering, we cannot even know the sign of b1 at typical HHI values. The audit's economic interpretation may be incorrect.

**First-layer audit status:** Interpretation provided but potentially erroneous.

---

## E. Verified False Positives

None identified. The first-layer audit did not flag any issues, so there are no false positive flags to evaluate.

---

## F. Variable Dictionary Cross-Check

| Variable | Audit Description | Code Definition | Match? |
|---|---|---|---|
| CapexAt | (implied) capex/assets | `_compute_and_winsorize` L1080-1085: Q4 capxy / lagged atq | Yes |
| CapexAt_lead | (implied) t+1 capex/assets | `create_capex_lead` L215-337: fiscal year t+1 via shift-1 with consecutive-year validation | Yes |
| tnic3hhi | "Firm-specific text-based Herfindahl index" | TNIC data file: `tnic3hhi` column | Yes |
| Interaction | IV_k x tnic3hhi | L220: raw product, no centering | Not documented in audit |
| BookLev | (implied) leverage | `_compute_and_winsorize` L1039: (dlcq+dlttq)/atq | Yes |
| All 4 IVs | Uncertainty pct measures | Same as H13 parent suite | Yes |

---

## G. Merge/Provenance Audit

| Merge Step | Left | Right | Key | Type | Row-Delta Guard? | Verified? |
|---|---|---|---|---|---|---|
| H13 panel load | -- | parquet file | -- | direct load | N/A | Yes |
| TNIC merge | H13 panel | TNIC3HHIdata.txt | `[_gvkey_int, fyearq_int]` | left | Yes (L178 assert) | Yes, but see C-1 |
| gvkey conversion | panel `gvkey` (str) | `_gvkey_int` (numeric) | -- | in-place | -- | Yes |
| TNIC has no duplicates on (gvkey,year) | -- | -- | -- | -- | -- | Verified: 0 duplicates in 188,422 rows |

**Key concern:** The TNIC data uses `gvkey` as integer (max 999,996) and `year` as calendar year of datadate. The panel uses `gvkey` as zero-padded string (converted to int via `pd.to_numeric`) and `fyearq_int` as fiscal year. The gvkey conversion is safe, but the year-key mismatch (C-1) is a genuine merge risk.

---

## H. Identification & Inference Audit

| Aspect | Status | Notes |
|---|---|---|
| Endogeneity of moderator | **Concern** | TNIC3HHI is contemporaneous with DV. Product market competition may respond to investment decisions. Lagged HHI would be more defensible |
| Reverse causality (IV -> DV) | **Not addressed** | Linguistic uncertainty and capex may be jointly determined by the same firm-quarter shocks. Not unique to H13.1 (inherited from H13) |
| Interaction interpretation | **Problematic** | Without centering, b1 and b2 are extrapolations to zero-valued components. Only b3 has a clear interpretation as the moderation effect |
| Multiple testing | **Concern** | 16 regressions tested; 1/16 significant at 5%. With Bonferroni correction (0.05/16 = 0.003), the p=0.027 finding would not survive. No multiple testing correction discussed |
| Clustering | **Adequate** | Firm-clustered SEs account for within-firm serial correlation |
| Fixed effects | **Adequate** | Industry FE via `other_effects` (absorbed, not dummies); Firm FE via `EntityEffects` |
| Absorbed variation | **Risk** | If HHI has low within-firm variation (claimed 27.8%), the interaction is also low-variation under Firm FE. The significant finding (Col 7, Firm FE) is thus somewhat surprising and should be scrutinized |

---

## I. Sample Accounting Reconstruction

| Stage | Audit Claim | Code Evidence | Verified? |
|---|---|---|---|
| Full panel (H13) | ~112,968 calls | Not stated in audit; "112,968" appears in coverage denominator | Cannot verify without execution |
| Main sample filter | FF12 not in {8,11} | L192 | Yes (logic verified) |
| TNIC merge | 98.3% matched | L181-182 prints this | Cannot verify without execution |
| Complete cases + min-calls | Not broken out | L216-234 applies all-IVs-nonmissing + complete-case + min-calls in one block | Not separately tracked |
| Final N per regression | Not stated | Would be in model_diagnostics.csv | Cannot verify |

---

## J. Reproducibility Assessment

| Criterion | Status | Notes |
|---|---|---|
| Deterministic | Claimed "true" in docstring | Correct: no random seeds, no sampling. PanelOLS is deterministic |
| Single command | `python -m f1d.econometric.run_h13_1_competition` | Verified from L639 `__main__` block |
| Input data pinned | H13 panel via `get_latest_output_dir`; TNIC via fixed path | TNIC is fixed; H13 panel uses "latest" which is time-dependent |
| Output timestamped | Yes, L541 | Verified |
| Manifest generated | Yes, L614-620 | Verified |

---

## K. Econometric Methodology Assessment

### K-1. Interaction Term Construction

The interaction is `IV_k * tnic3hhi` (raw product). This is valid but non-standard for continuous-by-continuous interactions. Best practice (Aiken & West 1991; Brambor, Clark & Golder 2006) recommends:
1. Center both components at their sample means
2. Report marginal effects at meaningful moderator values (e.g., 25th, 50th, 75th percentiles of HHI)
3. Plot the interaction to show how the effect of IV varies across HHI values

None of these are implemented. The interaction coefficient is still interpretable as the change in the IV effect per unit change in HHI, but the main effects become extrapolations.

### K-2. One-IV-Per-Model Design

The audit correctly notes that each IV gets its own model. This is a defensible exploratory design but differs from H13's simultaneous-IV design. The audit does not discuss whether the one-IV-per-model design inflates the effective number of tests or whether results would change if all 4 IVs entered simultaneously with their interactions.

### K-3. No Three-Way Interaction

The model is: `DV = b1*IV + b2*HHI + b3*(IV*HHI) + controls + FE`. This is a two-way interaction, not a three-way. The user prompt mentions "interpretation of three-way interactions" -- this is not applicable here. The model is correctly specified as a two-way interaction.

---

## L. Code Quality Assessment

| Aspect | Rating | Notes |
|---|---|---|
| Documentation | Good | Comprehensive docstring, clear variable naming |
| Error handling | Good | FileNotFoundError checks, assertion on merge row-delta |
| Modularity | Good | Clean separation of load, prepare, regress, save |
| LaTeX output | **Bug** | Column count mismatch (6 declared, 4 data columns per panel). See C-2 |
| Logging | Adequate | Print-based (not logging module), but sufficient for reproducibility |
| Test coverage | None | No unit tests for H13.1 |

---

## M. Comparison with Parent Suite (H13)

| Aspect | H13 | H13.1 | Match? |
|---|---|---|---|
| Panel source | h13_capex_panel.parquet | Same + TNIC merge | Yes |
| IVs | 4 simultaneous | 4 one-at-a-time | Different design |
| Controls | Base + Extended (8 specs) | Extended only (all 16 specs) | H13.1 uses Extended only |
| FE types | Industry, Firm | Industry, Firm | Same |
| DVs | CapexAt, CapexAt_lead | CapexAt, CapexAt_lead | Same |
| Sample filter | Main (FF12 not in {8,11}) | Main (FF12 not in {8,11}) | Same |
| MIN_CALLS_PER_FIRM | 5 | 5 | Same |
| Clustering | Firm | Firm | Same |

**Key difference:** H13 uses base and extended controls (8 specifications); H13.1 uses extended controls only (16 specifications). This means H13.1's sample may be slightly smaller (more complete-case attrition from requiring all extended controls).

---

## N. Risk Register

| ID | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| C-1 | TNIC year-key mismatch (fyearq vs calendar year) | Major | Moderate (~5-15% of merges affected) | Re-merge using `int(datadate[:4])` or verify fyearq == year for all matched pairs |
| D-1 | Uncentered interaction inflates multicollinearity, makes main effects uninterpretable | Major | Certain | Center IV and HHI at sample means before interaction |
| D-2 | Contemporaneous HHI is endogenous | Moderate | Moderate | Add lagged HHI robustness check |
| D-3 | No robustness checks | Moderate | Certain | Add lagged HHI, alternative measures, split-sample |
| D-6 | Potentially incorrect economic interpretation | Moderate | Moderate | Re-derive after centering; plot marginal effects |
| C-2 | LaTeX table malformed | Minor | Certain | Change `"c" * 6` to `"c" * 4` |
| D-5 | check_rank=False hides collinearity | Minor | Moderate | Enable or report condition number |

---

## O. Recommended Actions (Priority-Ordered)

1. **CRITICAL:** Verify TNIC year-key alignment. Either (a) confirm that for the actual sample, `fyearq_int` always equals the calendar year of the matched Compustat `datadate` for firms in TNIC, or (b) switch the merge key to `calendar_year(datadate)` as recommended by the TNIC readme.

2. **HIGH:** Center both IV and tnic3hhi at their sample means before constructing the interaction term. Report marginal effects at the 25th, 50th, and 75th percentiles of HHI.

3. **HIGH:** Add a lagged-HHI specification (tnic3hhi_{t-1}) to address moderator endogeneity.

4. **MODERATE:** Discuss multiple testing. With 16 tests at 5%, the expected number of false positives under the null is 0.8. The observed 1/16 is indistinguishable from chance. Consider Bonferroni, Holm, or FDR correction.

5. **MODERATE:** Fix LaTeX table column count (C-2).

6. **MODERATE:** Break out attrition stages separately (TNIC merge, complete-case, min-calls).

7. **LOW:** Add within-variation diagnostics for tnic3hhi (under both Industry and Firm FE) to the output, so the 85.7%/27.8% claims can be verified from logs.

8. **LOW:** Enable `check_rank=True` or report condition numbers.

---

## P. Overall Assessment

| Dimension | Grade | Notes |
|---|---|---|
| First-layer audit factual accuracy | B | Accurate on what it covers, but covers very little |
| First-layer audit completeness | D | Missing all major econometric issues (centering, endogeneity, multiple testing, year-key mismatch) |
| Implementation correctness | B- | Core regression logic is sound, but year-key mismatch and LaTeX bug are real errors |
| Econometric rigor | C+ | Adequate basic specification but lacks standard interaction-term best practices |
| Identification strategy | C | Contemporaneous moderator, no robustness checks, borderline significance |
| Thesis readiness | C+ | Needs centering, lagged-HHI robustness, and multiple testing discussion before thesis defense |

**Bottom line:** The H13.1 implementation is functional and the first-layer audit is not wrong on any verified claim, but the audit is a thin provenance document that missed all substantive econometric concerns. The suite's single significant finding (1/16 at p=0.027) does not survive Bonferroni correction and may reflect chance. The year-key mismatch (C-1) could introduce systematic measurement error in the moderator. Before including H13.1 results in a thesis, the author should (1) verify the TNIC year alignment, (2) center the interaction components, (3) add lagged-HHI robustness, and (4) address multiple testing.
