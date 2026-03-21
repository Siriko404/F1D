# H13 Capital Expenditure -- Second-Layer Red-Team Audit

**Audit Date:** 2026-03-18
**Auditor Context:** Fresh-context, adversarial, no prior involvement
**Target:** First-layer audit `docs/provenance/H13.md` + implementation code
**Suite ID:** H13
**Runner:** `src/f1d/econometric/run_h13_capex.py`
**Panel Builder:** `src/f1d/variables/build_h13_capex_panel.py`
**Engine:** `src/f1d/shared/variables/_compustat_engine.py`

---

## A. First-Layer Audit Completeness Scorecard

| Section | Present | Adequate | Notes |
|---------|---------|----------|-------|
| A1 Identity | Yes | Yes | Correctly identifies call-level unit, panel index |
| A2 Estimator | Yes | Yes | PanelOLS, FE types, clustering documented |
| A3 Outcome | Yes | Partial | CapexAt formula correct; does not verify denominator is lagged atq from `__init__.py` vs engine |
| A4 Key IVs | Yes | Yes | 4 simultaneous IVs correctly listed |
| A5 Controls | Yes | Yes | Base (7) and Extended (+4) correctly listed |
| A6 Hypothesis test | Yes | Yes | Two-tailed, firm-clustered, star thresholds correct |
| A7 Sample | Yes | Yes | Main only, FF12 exclusions correct |
| B Specifications | Yes | Yes | 8-column layout matches code exactly |
| C Results | Yes | Partial | Results labeled "pre-4IV run" -- unclear if current |
| D Reproducibility | Yes | Yes | File paths correct |
| E Design Decisions | Yes | Partial | Missing discussion of negative within-R-squared |

---

## B. Claim-by-Claim Verification

| ID | Audit Claim | Location | Verified? | Evidence | Verdict |
|----|-------------|----------|-----------|----------|---------|
| B01 | Model family: Panel FE OLS | A2 | YES | `run_h13_capex.py` line 73: `from linearmodels.panel import PanelOLS` | **VERIFIED FACT** |
| B02 | Industry FE absorbed via `other_effects` (FF12 dummies, not C() formula) | A2 | YES | `run_h13_capex.py` lines 316-328: constructor uses `other_effects=industry_data` | **VERIFIED FACT** |
| B03 | Firm FE via `EntityEffects + TimeEffects` from_formula | A2 | YES | `run_h13_capex.py` lines 332-334: formula string uses `EntityEffects + TimeEffects` | **VERIFIED FACT** |
| B04 | `drop_absorbed=True` | A2 | YES | Lines 326 and 334 both set `drop_absorbed=True` | **VERIFIED FACT** |
| B05 | Time FE = `fyearq_int` (fiscal year) | A2 | YES | MultiIndex is `["gvkey", "fyearq_int"]` at line 312; `TimeEffects` absorbs second index level | **VERIFIED FACT** |
| B06 | CapexAt = Q4 capxy / lagged total assets | A3 | YES | `_compustat_engine.py` lines 1079-1085: `capxy_annual` from Q4, divided by `atq_annual_lag1` | **VERIFIED FACT** |
| B07 | TobinsQ = (atq + cshoq*prccq - ceqq) / atq | A5 | NO | `_compustat_engine.py` lines 1067-1077: actual formula is `(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq`; ceqq is NOT used in TobinsQ | **VERIFIED ERROR** |
| B08 | ROA = Annual income / average assets | A5 | YES | `_compustat_engine.py` lines 1051-1060: `iby_annual / avg_assets` where avg = (atq_t + atq_{t-1})/2 | **VERIFIED FACT** |
| B09 | BookLev = (dlcq + dlttq) / atq | A5 | YES | `_compustat_engine.py` line 1039: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` | **VERIFIED FACT** |
| B10 | CashHoldings = cheq / atq | A5 | YES | `_compustat_engine.py` line 1066 | **VERIFIED FACT** |
| B11 | DividendPayer = dvy > 0 | A5 | YES | `_compustat_engine.py` lines 1089-1092: Q4 annual dvy > 0 | **VERIFIED FACT** |
| B12 | OCF_Volatility = rolling 5yr std of oancfy/lagged_atq | A5 | YES | `_compute_ocf_volatility()` lines 307-356: 1826D rolling, min 3, uses `atq_lag` | **VERIFIED FACT** |
| B13 | Two-tailed p-values, no one-tailed conversion | A6 | YES | Line 360: `p_two = float(model.pvalues.get(iv, np.nan))` -- raw model pvalues used directly | **VERIFIED FACT** |
| B14 | Firm-clustered SEs: `cov_type='clustered', cluster_entity=True` | A6 | YES | Lines 329 and 335 | **VERIFIED FACT** |
| B15 | Main sample: FF12 codes 1-7, 9-10, 12 (exclude 8, 11) | A7 | YES | Line 221: `~panel["ff12_code"].isin([8, 11])` | **VERIFIED FACT** |
| B16 | Min 5 calls per firm | A7 | YES | Line 121: `MIN_CALLS_PER_FIRM = 5` | **VERIFIED FACT** |
| B17 | 8 model specifications as described | B | YES | Lines 110-119: `MODEL_SPECS` list matches table exactly | **VERIFIED FACT** |
| B18 | CapexAt excluded from controls in all 8 specs | A5/E | YES | `BASE_CONTROLS` list (lines 93-101) does not include CapexAt | **VERIFIED FACT** |
| B19 | SalesGrowth winsorized once per-year | A5 | YES | `_compute_biddle_residual()` line 665: winsorized before first-stage; C-6 fix removed second winsorization | **VERIFIED FACT** |
| B20 | Panel file: 112,968 rows x 30 columns | D2 | UNVERIFIABLE | No parquet file inspected; accept as claimed | **UNVERIFIED** (no runtime artifact available) |
| B21 | `check_rank=False` used on Industry FE specs | Not documented | -- | Line 327: `check_rank=False` suppresses rank-deficiency warnings | **VERIFIED MISSED ISSUE** |
| B22 | Negative within-R-squared in Cols 3 and 7 | Not documented | -- | Table shows -0.012 and -0.037 | **VERIFIED MISSED ISSUE** |

---

## C. Verified Errors in First-Layer Audit

| ID | Error | Severity | Detail |
|----|-------|----------|--------|
| E01 | **TobinsQ formula is wrong** | Medium | Audit states `TobinsQ = (atq + cshoq*prccq - ceqq) / atq`. Code computes `(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq`. ceqq is NOT an input to TobinsQ. The formula in the `__init__.py` docstring is also wrong (same error). This exact issue was flagged in prior H1 and H13.1 red-team audits. The first-layer audit copy-pasted the incorrect `__init__.py` formula without verifying against actual engine code at `_compustat_engine.py:1073-1077`. |

---

## D. Verified Missed Issues

| ID | Issue | Severity | Category | Detail |
|----|-------|----------|----------|--------|
| M01 | **Negative within-R-squared not discussed** | Medium | Inference | Cols 3 and 7 (Industry FE + Extended controls) report negative within-R-squared (-0.012, -0.037). Negative within-R-squared in PanelOLS with `other_effects` (not entity effects) indicates the model fits worse than an intercept-only model after demeaning by the absorbed effects. This is a red flag for model specification issues with extended controls under Industry FE. The audit reports these values in the results table but does not acknowledge or explain them. A thesis referee would flag this immediately. |
| M02 | **`check_rank=False` not documented** | Low-Medium | Robustness | Industry FE specs use `check_rank=False` (line 327), which suppresses warnings about rank-deficient design matrices. If any FF12 dummies are collinear with controls or time effects, coefficients may be unreliable. The audit does not mention this parameter. |
| M03 | **Duplicate MultiIndex entries not discussed** | Medium | Identification | The panel is call-level (multiple calls per firm-year), but `set_index(["gvkey", "fyearq_int"])` at line 312 creates duplicate index entries. PanelOLS with `EntityEffects` treats gvkey as the entity dimension, but `TimeEffects` uses `fyearq_int` as the time dimension. With multiple calls per firm-year, the "time" dimension is non-unique within entity. PanelOLS handles this by treating each row as a separate observation, but this means the "within-R-squared" interpretation is non-standard -- it is not the traditional panel within-R-squared from a balanced firm-year panel. The audit mentions "Moulton concern" but does not address this index-structure implication. |
| M04 | **Moulton problem mitigation insufficiency** | Medium | Inference | The audit acknowledges the Moulton problem (CapexAt constant within firm-fiscal-year) and claims "Firm-clustered SEs partially mitigate." This is technically imprecise. Firm-clustered SEs correct for within-firm serial correlation, but the Moulton problem arises from regressing a group-level outcome on individual-level variation. With CapexAt constant within firm-year, the effective number of independent observations for the DV is the number of firm-years, not calls. Firm-clustered SEs help but do not fully address the inflated t-statistics from pseudoreplication. The correct mitigation would be to (a) collapse to firm-year level, or (b) use multi-way clustering (firm + fiscal year), or (c) use a Moulton correction factor. The audit does not discuss these alternatives. |
| M05 | **Lead variable construction: CapexAt_lead uses latest call within fiscal year** | Low | Variable dictionary | `create_capex_lead()` at line 280 uses `idxmax()` on `start_date_dt` to select the latest call's CapexAt within each (gvkey, fyearq_int). Since CapexAt is constant within firm-fiscal-year (Q4 annual value joined to all quarters), this choice is inconsequential -- all calls within the same firm-year have the same CapexAt. The audit does not explicitly note this invariance, which would strengthen the justification. |
| M06 | **Results labeled "pre-4IV run"** | Low | Audit craft | Section C header says "results from pre-4IV run" in parentheses, suggesting the reported results may not correspond to the current 4-IV implementation. If results were not updated after the redesign, the entire results section is stale. This undermines the audit's value as a reproducibility document. |
| M07 | **Attrition table in runner is approximate** | Low | Sample accounting | The attrition table construction (lines 756-762) uses `panel["CapexAt_lead"].notna().sum()` for the "After lead filter" stage, but this count is from the Main sample before complete-case filtering and min-calls filtering. It does not represent the actual sample size after all filters. The Col 1 N is used as the final stage, but Col 1 uses CapexAt (not CapexAt_lead), so comparing the lead count to the Col 1 N is comparing apples to oranges. |
| M08 | **No mention of H13.1 relationship** | Low | Completeness | The audit does not mention that H13.1 (competition-moderated capex) exists as a companion suite that uses the same panel and tests interaction effects. A thesis referee would want to know how these two suites relate. |

---

## E. Verified False Positives

None. The first-layer audit does not make any claims that are technically correct but misleading.

---

## F. Variable Dictionary Cross-Check

| Variable | Audit Formula | Code Formula | Match? | Note |
|----------|---------------|--------------|--------|------|
| CapexAt | Q4 capxy / lagged total assets | `_compute_annual_q4_variable("capxy") / _compute_annual_q4_variable_lag("atq")` | YES | |
| CapexAt_lead | Same ratio, next fiscal year | `create_capex_lead()` in panel builder: shift -1 within gvkey, consecutive-year validated | YES | |
| Size | ln(total assets) | `np.log(atq)` for `atq > 0` | YES | |
| TobinsQ | (atq + cshoq*prccq - ceqq) / atq | (cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq | **NO** | **E01** |
| ROA | Annual income / average assets | iby_annual / ((atq_t + atq_{t-1})/2) | YES | |
| BookLev | (dlcq + dlttq) / atq | (dlcq.fillna(0) + dlttq.fillna(0)) / atq | YES | fillna(0) not mentioned in audit |
| CashHoldings | cheq / atq | cheq / atq | YES | |
| DividendPayer | dvy > 0 | Q4 annual dvy > 0, binary | YES | |
| OCF_Volatility | Rolling 5yr std of oancfy/lagged_atq | 1826D rolling, min 3 periods, uses atq_lag | YES | |
| SalesGrowth | YoY sales growth | (sale_t - sale_{t-1}) / abs(sale_{t-1}) | YES | |
| RD_Intensity | xrdq / atq | xrdq.fillna(0) / atq | YES | fillna(0) not mentioned |
| CashFlow | Operating cash flow / assets | oancfy / avg_assets | YES | "Biddle pipeline" note is accurate |
| Volatility | Annualized stock return std (CRSP) | CRSP-sourced via VolatilityBuilder | YES | |

---

## G. Identification and Inference Assessment

| ID | Issue | Severity | Detail |
|----|-------|----------|--------|
| G01 | **Moulton problem is the dominant identification concern** | High | CapexAt is constant within firm-fiscal-year. With ~3 calls per firm-year on average (37,661 calls / ~3,000 firm-years = ~12.5 calls/firm, across ~10 years = ~1.25 calls/firm-year), the DV has no within-firm-year variation. The 4 IVs (uncertainty percentages) vary at the call level. This creates a classic Moulton (1990) problem: standard errors are too small because the regression treats each call as independent when the DV is measured at the group (firm-year) level. Firm-clustered SEs correct for within-firm correlation across years but not for within-firm-year pseudoreplication. The audit acknowledges this but understates the severity and does not suggest the standard remedy (aggregate to firm-year level). |
| G02 | **Industry FE significance vs. Firm FE insignificance** | Medium | All significance in Cols 1,3,5,7 (Industry FE) disappears in Cols 2,4,6,8 (Firm FE). The audit correctly interprets this as "between-firm rather than within-firm" effects. However, it does not note that this pattern is consistent with omitted variable bias at the firm level: industry composition correlates with both uncertainty language norms and capital intensity. The within-firm estimator (Firm FE) removes this confound, and the coefficients become insignificant. This is not just a matter of "variation source" -- it is a direct challenge to the causal interpretation. |
| G03 | **No discussion of economic magnitude** | Low-Medium | The audit reports significance but not coefficient magnitudes or economic significance. A thesis referee would want to know: a 1-percentage-point increase in CEO QA Uncertainty is associated with how much change in CapexAt? Is this economically meaningful relative to the mean/SD of CapexAt? |

---

## H. Robustness Assessment

| ID | Issue | Severity | Detail |
|----|-------|----------|--------|
| H01 | **No robustness checks reported** | Medium | The audit documents the 8-spec design (varying DV, FE, controls) as the robustness structure. However, no additional robustness checks are mentioned: no alternative clustering (double-clustering by firm+year), no alternative winsorization bounds, no subsample analysis (by industry, time period), no placebo tests. For a thesis, the 8-spec design is a reasonable starting point, but a referee would likely request at least double-clustered SEs. |
| H02 | **Firm-year collapse robustness not tested** | Medium | Given M04/G01 (Moulton problem), the most important robustness check would be to collapse the data to firm-year level and re-estimate. This is not mentioned anywhere. |

---

## I. Sample Accounting Verification

| Stage | Audit Claim | Code Evidence | Verified? |
|-------|-------------|---------------|-----------|
| Full panel | 112,968 rows | Panel builder output (claimed) | UNVERIFIABLE (no runtime) |
| Main sample | Not explicitly stated | `filter_main_sample()` excludes FF12 = {8, 11} | Logic verified |
| CapexAt complete cases | Col 1: 37,661 | Runtime output (claimed) | UNVERIFIABLE |
| CapexAt_lead complete cases | Col 5: 35,424 | Runtime output (claimed) | UNVERIFIABLE |
| N firms Col 1 | 1,276 | Runtime output (claimed) | UNVERIFIABLE |
| N firms Col 5 | 1,220 | Runtime output (claimed) | UNVERIFIABLE |

**Sample drop from Col 1 to Col 5:** 37,661 - 35,424 = 2,237 calls (~5.9% drop). This is the lead-variable attrition (last fiscal year per firm + gap years). The magnitude is plausible.

**Sample drop from base to extended controls:** 37,661 - 37,656 = 5 calls (Col 1 vs Col 3). Only 5 calls lost to extended control missingness. This is plausible if extended controls (SalesGrowth, RD_Intensity, CashFlow, Volatility) have very high coverage.

---

## J. Merge and Provenance Verification

| Stage | Merge Key | Verified? | Detail |
|-------|-----------|-----------|--------|
| Manifest -> variables | `file_name` (left join) | YES | `build_h13_capex_panel.py` lines 158-193: zero-row-delta enforced with ValueError on fan-out |
| Manifest -> Compustat | `merge_asof` on `(gvkey, start_date)` | YES | Via `CompustatEngine.match_to_manifest()` in each builder; backward asof merge |
| Panel -> fyearq | `attach_fyearq()` via `panel_utils.py` | YES | Called at line 251; uses merge_asof backward |
| Lead variable | `(gvkey, fyearq_int)` left join | YES | `create_capex_lead()` lines 317-327; zero-row-delta enforced |

**No fan-out risk identified.** All merges have explicit row-count guards.

---

## K. LaTeX Table Verification

| Check | Verified? | Detail |
|-------|-----------|--------|
| Column count matches specs | YES | 8 columns, `"c" * n_cols` at line 432 |
| DV grouping headers correct | YES | Cols 1-4 = CapexAt, Cols 5-8 = CapexAt_lead |
| Star notation matches code | YES | `_sig_stars()` at lines 379-389: */<0.10, **/<0.05, ***/<0.01 |
| SE in parentheses | YES | `fmt_se()` at lines 413-416 |
| Table notes accurate | Partial | Notes say "Variables winsorized at 1%/99% by year at engine level" -- correct for Compustat vars. But extended controls (SalesGrowth, CashFlow) are winsorized inside Biddle computation, then the Compustat engine explicitly skips re-winsorizing them. The note is technically correct but could be clearer. |
| Table notes mention Moulton | YES | "CapEx intensity is constant within firm-fiscal-year" disclosed |
| Fiscal year FE mentioned | YES | "Time FE uses fiscal year (fyearq_int)" |

---

## L. Code Quality and Reproducibility

| Check | Status | Detail |
|-------|--------|--------|
| Deterministic | YES | No random seeds, no stochastic elements |
| Timestamped outputs | YES | Output dir = `{timestamp}/` |
| Run manifest | YES | `generate_manifest()` called at line 766 |
| Logging | YES | `setup_run_logging()` at line 670 |
| Dry-run mode | YES | `--dry-run` flag at line 163 |
| Complete-case filtering | YES | Line 257: `notna().all(axis=1)` on all required columns |
| Inf handling | YES | Line 243: `replace([np.inf, -np.inf], np.nan)` |

---

## M. Relationship to H13.1

The audit does not mention H13.1 (competition-moderated capex). Key relationship facts:

- H13.1 uses the **same panel** (`h13_capex_panel.parquet`) as H13.
- H13.1 merges TNIC3HHI data at load time for interaction analysis.
- H13.1 tests each IV separately (1 IV per model) with interaction terms, while H13 tests all 4 IVs simultaneously.
- H13.1 uses Extended controls only, while H13 tests both Base and Extended.
- The two suites are complementary: H13 establishes the main effects, H13.1 tests moderation.

A thesis referee would expect the H13 provenance document to reference H13.1 as a companion analysis.

---

## N. Severity Summary

| Severity | Count | IDs |
|----------|-------|-----|
| VERIFIED ERROR | 1 | E01 (TobinsQ formula) |
| VERIFIED MISSED ISSUE (High) | 0 | |
| VERIFIED MISSED ISSUE (Medium) | 5 | M01, M02, M03, M04, M06 |
| VERIFIED MISSED ISSUE (Low-Medium) | 1 | M08 |
| VERIFIED MISSED ISSUE (Low) | 2 | M05, M07 |
| REFEREE JUDGMENT (High) | 1 | G01 (Moulton) |
| REFEREE JUDGMENT (Medium) | 2 | G02, G03 |
| UNVERIFIED CONCERN | 0 | |

---

## O. Actionable Recommendations

| Priority | ID | Action |
|----------|----|--------|
| **P0 (must fix)** | E01 | Correct TobinsQ formula in audit doc to: `TobinsQ = (cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq`. Also fix in `__init__.py` docstring. |
| **P1 (should fix)** | G01, M04 | Add a firm-year-collapsed robustness check or explicitly justify why call-level estimation with Moulton-affected DV is acceptable. At minimum, add a paragraph to Design Decisions discussing the Moulton problem more rigorously and explaining why firm-clustered SEs are considered sufficient. |
| **P1 (should fix)** | M01 | Add a Design Decisions entry explaining negative within-R-squared in Cols 3 and 7 (Industry FE + Extended). This likely reflects the extended controls absorbing variation differently under the `other_effects` specification vs. entity effects. |
| **P1 (should fix)** | M06 | Update results section to reflect current 4-IV run, or remove "pre-4IV run" label if results are in fact current. |
| **P2 (nice to have)** | M03 | Add a note in A2 or E explaining that the MultiIndex `(gvkey, fyearq_int)` is non-unique at call level, and how PanelOLS handles this. |
| **P2 (nice to have)** | G02 | Add a discussion of the industry-FE-significant / firm-FE-insignificant pattern in terms of potential omitted variable bias at the firm level, not just "variation source." |
| **P2 (nice to have)** | G03 | Add economic magnitude interpretation to the results section. |
| **P2 (nice to have)** | M08 | Add a reference to H13.1 as a companion suite. |

---

## P. Overall Verdict

**First-layer audit quality: ADEQUATE WITH GAPS**

The first-layer audit correctly documents the implementation mechanics in 17 of 18 verified claims. The suite ID, estimator, FE structure, clustering, sample filters, DV construction, lead variable timing, and 8-spec layout are all accurately described and verified against code.

**One factual error** (TobinsQ formula) is a recurring documentation bug across multiple suite audits and should be fixed project-wide.

**The most material gap** is the insufficient treatment of the Moulton problem. The audit acknowledges the issue but understates its severity and does not suggest the standard remedy (firm-year aggregation). For a thesis defense, this is the single most likely referee challenge: "Why not just collapse to firm-year level and avoid the pseudoreplication entirely?"

**The negative within-R-squared** in Industry FE + Extended control specs is unremarked, which a referee would notice immediately. The **"pre-4IV run" label** on results creates uncertainty about whether the reported numbers are current.

The audit is sufficient as a working provenance document but would benefit from the P0 and P1 fixes before thesis submission.
