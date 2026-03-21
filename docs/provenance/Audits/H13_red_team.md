# H13 Capital Expenditure -- Second-Layer Red-Team Audit

**Audit Date:** 2026-03-21
**Auditor Role:** Hostile-but-fair replication auditor (second layer)
**First-Layer Doc:** `docs/provenance/H13.md` (dated 2026-03-18)
**Suite:** H13 Capital Expenditure
**Runner:** `src/f1d/econometric/run_h13_capex.py`
**Panel Builder:** `src/f1d/variables/build_h13_capex_panel.py`
**Shared Engine:** `src/f1d/shared/variables/_compustat_engine.py`

---

## A. Scope and Method

This is a second-layer audit. The objective is to verify the accuracy and completeness of the first-layer provenance document (`H13.md`) by independently reading every code path referenced and checking whether the first-layer claims are correct, whether any material code paths were omitted, and whether the identified limitations are genuinely exhaustive.

Files independently inspected:
- `run_h13_capex.py` (full file, 817 lines)
- `build_h13_capex_panel.py` (full file, 497 lines)
- `_compustat_engine.py` (lines 230-360, 640-720, 1030-1330)
- `__init__.py` (TobinsQ docstring, line 21)
- `panel_utils.py` (`attach_fyearq`, lines 76-106)
- `book_lev.py` (full file)
- `lev.py` (full file)

---

## B. First-Layer Accuracy -- Verified Claims

The following first-layer claims were independently verified against the codebase:

| Audit Claim | Code Location | Verdict |
|-------------|---------------|---------|
| 8 model specs: 2 DVs x 2 FE x 2 control sets | Runner `MODEL_SPECS` lines 110-119 | **CONFIRMED** |
| 4 simultaneous IVs | Runner `KEY_IVS` lines 85-89 | **CONFIRMED** |
| 7 base controls (Size, TobinsQ, ROA, BookLev, CashHoldings, DividendPayer, OCF_Volatility) | Runner `BASE_CONTROLS` lines 93-101 | **CONFIRMED** |
| 4 extended controls (SalesGrowth, RD_Intensity, CashFlow, Volatility) | Runner `EXTENDED_CONTROLS` lines 103-108 | **CONFIRMED** |
| CapexAt excluded from controls | `BASE_CONTROLS` does not include CapexAt | **CONFIRMED** |
| Industry FE via `other_effects`, not C() dummies | Runner lines 319-328 | **CONFIRMED** |
| Firm FE via `EntityEffects + TimeEffects` from_formula | Runner lines 332-334 | **CONFIRMED** |
| `drop_absorbed=True` for all specs | Runner lines 326, 334 | **CONFIRMED** |
| `check_rank=False` for industry FE only | Runner line 327 | **CONFIRMED** |
| Firm-clustered SEs: `cov_type='clustered', cluster_entity=True` | Runner lines 329, 335 | **CONFIRMED** |
| Main sample excludes FF12 = {8, 11} | Runner line 221 | **CONFIRMED** |
| MIN_CALLS_PER_FIRM = 5 | Runner line 121 | **CONFIRMED** |
| Two-tailed p-values, no one-tailed conversion | Runner line 360: raw `model.pvalues` | **CONFIRMED** |
| Star thresholds: */0.10, **/0.05, ***/0.01 | `_sig_stars()` lines 379-389 | **CONFIRMED** |
| Inf replacement before complete-case filter | Runner line 243 | **CONFIRMED** |
| MultiIndex = `["gvkey", "fyearq_int"]` | Runner line 312 | **CONFIRMED** |
| CapexAt = capxy_annual_Q4 / atq_annual_lag1 | Engine lines 1081-1087 | **CONFIRMED** |
| TobinsQ = (cshoq*prccq + clipped_debt) / atq, NOT textbook | Engine lines 1069-1079 | **CONFIRMED** |
| BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq | Engine line 1041 | **CONFIRMED** |
| ROA = iby_annual_Q4 / avg_assets | Engine lines 1052-1062 | **CONFIRMED** |
| CashHoldings = cheq / atq | Engine line 1068 | **CONFIRMED** |
| DividendPayer = (dvy_annual_Q4.fillna(0) > 0) binary | Engine lines 1089-1094 | **CONFIRMED** |
| OCF_Volatility = rolling 5yr std, min_periods=3 | Engine lines 309-358 | **CONFIRMED** |
| Zero-row-delta guards on all merges | Builder lines 185-192, 321-328 | **CONFIRMED** |
| Manifest file_name uniqueness asserted | Builder lines 148-153 | **CONFIRMED** |
| Builder output file_name uniqueness asserted | Builder lines 168-173 | **CONFIRMED** |
| Lead variable consecutive-year validation | Builder lines 302-304 | **CONFIRMED** |
| Winsorization at 1%/99% per fiscal year, min 10 obs | Engine `_winsorize_by_year` lines 445-469 | **CONFIRMED** |
| `skip_winsorize` includes DividendPayer, InvestmentResidual, CashFlow, SalesGrowth, is_div_payer_5yr, REPO, fqtr | Engine lines 1199-1207 | **CONFIRMED** |
| SalesGrowth single-pass winsorization (not double) | Engine line 667 + `skip_winsorize` | **CONFIRMED** |
| CashFlow single-pass winsorization (not double) | Engine line 694 + `skip_winsorize` | **CONFIRMED** |
| `__init__.py` line 21 documents textbook TobinsQ formula, not actual | `__init__.py` line 21 | **CONFIRMED** |

**Summary:** All 32 factual claims verified against the codebase are accurate.

---

## C. First-Layer Accuracy -- Line Number Drift

The first-layer audit cites specific line numbers from `_compustat_engine.py`. Several are offset by 2-3 lines from the current codebase:

| Audit Citation | Actual Line | Delta |
|---------------|-------------|-------|
| "CapexAt at lines 1079-1085" | Lines 1081-1087 | +2 |
| "CashHoldings at line 1066" | Line 1068 | +2 |
| "TobinsQ at lines 1067-1077" | Lines 1069-1079 | +2 |
| "ROA at lines 1051-1060" | Lines 1052-1062 | +1 to +2 |
| "BookLev at line 1039" | Line 1041 | +2 |
| "Size at line 1034" | Line 1036 | +2 |

**Severity:** Cosmetic. The drift is consistent (~2 lines), suggesting code was edited (likely lines inserted near the top of the function) after the first-layer audit was written. All line-number citations still point to the correct code constructs; a reader following them would find the right code within 2-3 lines.

---

## D. First-Layer Accuracy -- Errors Found

| ID | Error | Severity |
|----|-------|----------|
| E01 | **CapexAt denominator documentation.** The first-layer audit Section 6.1.1 states the denominator is `atq_annual_lag1` and references `_compute_annual_q4_variable_lag` at "line 1052, reused at line 1081." In the actual code, `atq_annual_lag1` is computed at line 1054 and used at line 1083. The variable is correctly described but the "reused" phrasing is slightly misleading -- line 1054 computes the lag for ROA's denominator, and the same variable is indeed reused for CapexAt at line 1083. This is a minor wording issue, not a factual error. | Cosmetic |
| E02 | **`_compute_annual_q4_variable_lag` line reference.** The audit says "line 291" for the `fyearq += 1` shift. The actual code has this at line 293. | Cosmetic |

**No material factual errors were found in the first-layer audit.**

---

## E. First-Layer Completeness -- Omissions Found

| ID | Omission | Severity | Detail |
|----|----------|----------|--------|
| O01 | **`BookLev` inconsistency with `TobinsQ` on both-null guard** | Low-Medium | The first-layer audit correctly notes (Section 6.3.4) that BookLev fills each debt component with zero individually, so `both-null` produces BookLev=0 (not NaN). It correctly contrasts this with TobinsQ's `both-null` guard. However, the audit does not discuss whether this inconsistency could introduce systematic bias -- firms with missing debt data in BookLev are treated as zero-leverage firms, while the same firms in TobinsQ would have NaN debt. A referee could question why the same conceptual quantity (total debt) is handled differently in two controls in the same regression. |
| O02 | **`CapexAt` numerator uses `capxy` not `capx`** | Low | The audit correctly documents that `capxy` is YTD cumulative and Q4 is used. However, it does not explicitly note that `capxy` (YTD capital expenditure) and `capx` (annual capital expenditure from the annual Compustat file) are different Compustat items. The use of quarterly files with Q4-extraction is a deliberate design choice documented in the code comments, but the audit could have noted this is methodologically equivalent to using annual `capx` only if Compustat's accumulation is consistent. |
| O03 | **No discussion of `merge_asof` tolerance/max gap** | Low | The `match_to_manifest` function (line 1301) uses `merge_asof` with `direction="backward"` but no `tolerance` parameter. This means a call could match to arbitrarily old Compustat data if no recent quarter exists. The first-layer audit documents the merge strategy but does not flag the absence of a staleness guard. In practice, most calls should match within 1-2 quarters, but edge cases (newly listed firms, firms with reporting gaps) could match to data many quarters old. |
| O04 | **No discussion of `year` column usage in runner** | Low | The runner loads the `year` column (line 199) but never uses it in any filter, regression, or output. The panel builder creates `year` from `start_date` at line 204, and the runner loads it, but `fyearq_int` is the actual time dimension. The `year` column is dead code in the runner. This is harmless but undocumented. |
| O05 | **Summary stats computed on pre-filtered panel** | Low | The runner computes summary statistics (lines 718-726) on `panel` after `filter_main_sample()` but BEFORE complete-case filtering and min-calls filtering. This means summary stats include observations that are dropped from the regression. The first-layer audit does not note this. The summary stats reflect the Main sample population, not the estimation sample. |

---

## F. Moulton Problem Assessment

The first-layer audit correctly identifies and thoroughly discusses the Moulton (1990) pseudoreplication problem (Sections 1, 11.1, 12 L01). The treatment is accurate and appropriately severe. The audit correctly notes:

1. DVs are constant within firm-fiscal-year
2. Firm-clustered SEs partially but not fully address this
3. No firm-year-collapsed robustness check exists
4. A referee would likely demand a collapsed specification

**Red-team assessment:** The Moulton discussion is the strongest part of the first-layer audit. No additional concerns to add.

---

## G. Identification and Inference -- Additional Concerns

| ID | Concern | Severity |
|----|---------|----------|
| G01 | **No IV exogeneity discussion.** The 4 IVs (uncertainty percentages) are measured from earnings calls that occur during or after the fiscal year whose CapEx is measured. For `CapexAt` (contemporaneous), the call may occur AFTER Q4 CapEx decisions are already made, creating a simultaneity/reverse-causality concern. A firm that has already committed to high CapEx may discuss it with less (or more) uncertain language. The first-layer audit does not discuss timing/exogeneity of the IVs relative to CapEx decisions. | Medium |
| G02 | **Lead DV timing is cleaner but still imperfect.** For `CapexAt_lead` (t+1), the speech occurs before or during the CapEx measurement period, which is a cleaner identification. However, the audit does not explicitly note that the lead-DV specifications (Cols 5-8) are the more credible tests and should be emphasized over contemporaneous specs (Cols 1-4). | Low |
| G03 | **No mention of survivorship bias in lead construction.** Firms that exit the sample (delisting, merger, bankruptcy) before year t+1 receive NaN for `CapexAt_lead`. These exits are non-random -- distressed firms likely have higher uncertainty language AND are more likely to exit. This creates a sample selection bias in the lead-DV specifications that the first-layer audit does not discuss. | Medium |

---

## H. Variable Construction -- Verified Chains

All variable construction chains documented in the first-layer audit Sections 6.1-6.4 were independently verified. The descriptions are accurate, detailed, and trace the full path from raw Compustat fields through transformations, guards, winsorization, and manifest matching.

The level of detail is unusually high for a provenance document -- the first-layer audit traces individual function calls, line numbers, and edge-case handling. This is commendable.

---

## I. Merge and Sample Construction -- Verified

All merge steps documented in the first-layer audit Section 5 were verified:

1. Manifest file_name uniqueness assertion: **Verified** (builder lines 148-153)
2. Builder output uniqueness assertion: **Verified** (builder lines 168-173)
3. Left-join with zero-row-delta: **Verified** (builder lines 185-192)
4. Lead merge with zero-row-delta: **Verified** (builder lines 321-328)
5. `attach_fyearq` match rate guard: **Verified** (panel_utils.py line 95 docstring mentions 80% threshold)

No unguarded merges were found. The first-layer audit's claim that "all merges have explicit row-count guards" is correct.

---

## J. Output Inventory -- Verified

All 8 output files documented in Section 8 correspond to actual code paths in `save_outputs()`, `_save_latex_table()`, `generate_report()`, `generate_manifest()`, and `generate_attrition_table()`. No undocumented outputs were found. No missing outputs were found.

---

## K. LaTeX Table Audit

The LaTeX table generation (`_save_latex_table`, runner lines 392-529) was inspected:

1. **Coefficient formatting:** 4 decimal places with significance stars. Correct.
2. **SE in parentheses:** 4 decimal places. Correct.
3. **FE indicator rows:** Industry FE, Firm FE, Fiscal Year FE rows with "Yes"/blank. Correct.
4. **Table notes:** Correctly describe two-tailed test, firm clustering, main sample, fiscal year time FE, and unit of observation (earnings call).
5. **Moulton caveat in notes:** The table note at runner line 518-519 states "CapEx intensity is constant within firm-fiscal-year... results should be interpreted alongside lead DV (cols 5--8)." This is a partial Moulton disclosure in the table itself. Good practice.

**No issues found with LaTeX table generation.**

---

## L. Attrition Table Audit

The attrition table (runner lines 756-764) has 4 stages:

1. Master manifest (full panel from Stage 3): `full_panel_n`
2. Main sample filter: `main_panel_n`
3. After lead filter: `panel["CapexAt_lead"].notna().sum()` -- this is from the Main sample before complete-case/min-calls filtering
4. After complete-case + min-calls: `first_meta.get("n_obs", 0)` -- Col 1 final N

The first-layer audit correctly identifies (Section 9, L07) that stage 3 is an upper bound, not the final lead-DV sample. This is accurate.

**Minor concern:** Stage 4 uses Col 1's N, which is the `CapexAt` (contemporaneous) sample. The lead-DV samples (Cols 5-8) have different N due to lead-variable attrition. The attrition table does not show the final N for lead-DV specifications. This is not mentioned in the first-layer audit's attrition analysis. Severity: Low.

---

## M. Red-Team Findings Disposition -- Verified

The first-layer audit Section 13 documents disposition of a previous red-team audit. All dispositions were verified:

- E01 (TobinsQ formula): Fixed in Section 6.3 and L03. **Confirmed.**
- M01-M08: All marked as fixed with specific section references. **Confirmed** -- the corresponding sections exist and contain the claimed content.
- G01-G03: All addressed. **Confirmed.**

---

## N. Design Decisions -- Assessed

The 8 design decisions (D01-D08) in Section 14 are all defensible and accurately documented. No design decisions that exist in code but are undocumented in the first-layer audit were found.

---

## O. Overall Assessment

| Dimension | Rating | Comment |
|-----------|--------|---------|
| **Factual Accuracy** | Excellent | All 32 verified claims are correct. Line numbers have minor drift (~2 lines) but all point to the correct constructs. |
| **Completeness** | Very Good | The audit is thorough and covers all major code paths. Five minor omissions identified (O01-O05), none rising above Low-Medium severity. |
| **Identification Discussion** | Good | Moulton problem is thoroughly treated. Missing: IV exogeneity/timing discussion (G01), survivorship bias in lead construction (G03). |
| **Limitations Catalogue** | Very Good | 9 limitations (L01-L09) are comprehensive and accurately described. Two additional concerns (G01, G03) could be added. |
| **Variable Documentation** | Excellent | Full construction chains from raw fields through all transformations. Unusually detailed and accurate. |
| **Merge Safety** | Excellent | All merges have explicit guards. No fan-out risk. Accurately documented. |

---

## P. Summary of Findings

### Errors in First-Layer Audit
- E01-E02: Cosmetic line number inaccuracies (2-3 line drift). No material factual errors found.

### Omissions in First-Layer Audit
- O01: BookLev vs TobinsQ both-null handling inconsistency (Low-Medium)
- O02: `capxy` vs `capx` distinction undocumented (Low)
- O03: No `merge_asof` staleness guard discussion (Low)
- O04: Dead `year` column in runner (Low)
- O05: Summary stats computed on pre-filtered sample (Low)

### Additional Identification Concerns
- G01: No IV exogeneity/timing discussion for contemporaneous DV (Medium)
- G02: Lead DV specifications should be emphasized as cleaner identification (Low)
- G03: Survivorship bias in lead construction undiscussed (Medium)

### Additional Attrition Concern
- The attrition table does not show final N for lead-DV specifications separately from contemporaneous-DV specifications (Low)

### Verdict
The first-layer audit is of high quality. It is factually accurate, thorough, and appropriately identifies the dominant methodological concern (Moulton problem). The omissions are minor and the additional concerns raised here (IV timing, survivorship bias) are supplementary rather than contradictory. The document is suitable for use as a provenance record with the caveats noted above.
