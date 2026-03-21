# H15 Share Repurchase -- Second-Layer Red-Team Audit

**Generated:** 2026-03-21
**Auditor role:** Hostile-but-fair replication auditor (second layer)
**Suite ID:** H15
**First-layer doc:** `docs/provenance/H15.md`
**Runner:** `src/f1d/econometric/run_h15_repurchase.py`
**Panel builder:** `src/f1d/variables/build_h15_repurchase_panel.py`

---

## A. Scope & Mandate

This audit independently verifies every factual claim in the first-layer provenance document (`H15.md`) against the actual source code. The goal is to catch errors in the audit itself: wrong line numbers, misquoted formulas, omitted risks, or findings that were accepted but never actually fixed.

---

## B. First-Layer Accuracy: Line-Number Spot Checks

| Claim in H15.md | Cited location | Actual code | Verdict |
|---|---|---|---|
| `REPO_callqtr` = 1 if cshopq > 0 | Builder lines 251--254 | Builder lines 251--254: `np.where(comp["cshopq"].notna() & (comp["cshopq"] > 0), 1.0, ...)` | CONFIRMED |
| `next_fqtr = fqtr_int % 4 + 1` | Builder lines 271--272 | Builder line 271: `panel["next_fqtr"] = panel["fqtr_int"] % 4 + 1` | CONFIRMED |
| `next_fyearq` rollover at Q4 | Builder line 272 | Builder line 272: `panel["next_fyearq"] = panel["fyearq_int"] + (panel["fqtr_int"] == 4).astype(float)` | CONFIRMED |
| Year restriction: `max(config.data.year_start, 2004)` | Builder line 335 | Builder line 335: `year_start = max(config.data.year_start, 2004)` | CONFIRMED |
| Main sample filter: `~ff12_code.isin([8, 11])` | Runner line 206 | Runner line 206: `main = panel[~panel["ff12_code"].isin([8, 11])].copy()` | CONFIRMED |
| `MIN_CALLS_PER_FIRM = 5` | Runner line 114 | Runner line 114: `MIN_CALLS_PER_FIRM = 5` | CONFIRMED |
| Panel index: `gvkey x fyearq_int` | Runner line 283 | Runner line 283: `df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])` | CONFIRMED |
| 4 KEY_IVS | Runner lines 82--86 | Runner lines 82--86: 4 uncertainty variables listed | CONFIRMED |
| 8 BASE_CONTROLS | Runner lines 89--98 | Runner lines 89--98: 8 controls listed | CONFIRMED |
| EXTENDED = Base + 4 | Runner lines 100--105 | Runner lines 100--105: `BASE_CONTROLS + [SalesGrowth, RD_Intensity, CashFlow, Volatility]` | CONFIRMED |
| `drop_absorbed=True` | Runner lines 296, 303 | Runner line 296 (industry PanelOLS ctor), line 303 (firm `from_formula`) | CONFIRMED |
| `check_rank=False` for industry FE only | Runner line 297 | Runner line 297: `check_rank=False` in industry model; absent from firm formula (line 303) | CONFIRMED |
| P-values: `model.pvalues` two-tailed | Runner line 328 | Runner line 328: `p_two = float(model.pvalues.get(iv, np.nan))` | CONFIRMED |
| REPO in COMPUSTAT_COLS | Engine line 140 | Engine line 140: `"REPO"` in COMPUSTAT_COLS list | CONFIRMED |
| fqtr in COMPUSTAT_COLS | Engine line 141 | Engine line 141: `"fqtr"` in COMPUSTAT_COLS list | CONFIRMED |
| REPO in skip_winsorize | Engine line 1205 | Engine line 1205: `"REPO"` in skip_winsorize set | CONFIRMED |
| fqtr in skip_winsorize | Engine line 1206 | Engine line 1206: `"fqtr"` in skip_winsorize set | CONFIRMED |
| Engine REPO formula | Engine lines 1158--1162 | Engine lines 1158--1162: identical three-way np.where logic | CONFIRMED |
| merge_asof direction='backward' | Engine line 1307 | Engine line 1307: `direction="backward"` | CONFIRMED |
| BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq | Engine line 1041 | Engine line 1041: confirmed | CONFIRMED |
| TobinsQ = (mktcap + debt_book) / atq | Engine lines 1075--1078 | Engine lines 1075--1078: confirmed with guards | CONFIRMED |
| ROA = iby_annual / avg_assets | Engine lines 1060--1062 | Engine lines 1060--1062: confirmed | CONFIRMED |
| Size = ln(atq) where atq > 0 | Engine line 1036 | Engine line 1036: `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` | CONFIRMED (note: audit says line 1034, actual is 1036) |
| CashHoldings = cheq / atq | Engine line 1068 | Engine line 1068: `comp["CashHoldings"] = comp["cheq"] / comp["atq"]` | CONFIRMED (note: audit says line 1066, actual is 1068) |
| CapexAt = capxy_annual / atq_annual_lag1 | Engine lines 1082--1087 | Engine lines 1082--1087: confirmed | CONFIRMED (note: audit says lines 1079--1084, off by ~3) |
| DividendPayer = dvy_annual > 0 | Engine lines 1092--1094 | Engine lines 1092--1094: `(dvy_annual.fillna(0) > 0).astype(float)` | CONFIRMED (note: audit says lines 1089--1092, off by ~3) |
| OCF_Volatility: rolling 1826D, min_periods=3 | Engine line 341 | Engine line 341: `x.rolling("1826D", min_periods=3).std()` | CONFIRMED (note: audit says lines 307--356, function spans 309--358) |
| Compustat lookup dedup keep='last' | Builder lines 258--263 | Builder lines 258--263: `drop_duplicates(..., keep="last")` | CONFIRMED |
| REPO_callqtr merge row-count validation | Builder lines 288--292 | Builder lines 287--292: `if after_len != before_len: raise ValueError(...)` | CONFIRMED |
| RepurchaseIndicatorBuilder returns REPO + fqtr | repurchase_indicator.py line 48 | Line 48: `data = merged[["file_name", "REPO", "fqtr"]].copy()` | CONFIRMED |

**Line-number drift summary:** Several line numbers are off by 2--4 lines (Size cited as 1034 vs actual 1036; CashHoldings cited as 1066 vs 1068; CapexAt cited as 1079--1084 vs 1082--1087; DividendPayer cited as 1089--1092 vs 1092--1094). These are minor and do not affect correctness of the claim. The drift is consistent with code changes that inserted lines above the cited locations after the first-layer audit was written.

---

## C. First-Layer Accuracy: Formula Verification

All variable formulas stated in the first-layer audit match the actual code. No formula misquotation was found for any of the 16 variables (DV, 4 IVs, 8 base controls, 4 extended controls minus Volatility which is CRSP-based).

---

## D. Error Found: CashHoldings Inf Replacement Misstatement

**Severity: MINOR (factual error in documentation, no impact on estimates)**

The first-layer audit states in Section 6 (CashHoldings):

> "Not in explicit `ratio_cols` list but inf values are handled at the runner level via `df.replace([np.inf, -np.inf], np.nan)` (runner line 226)."

This is **factually incorrect**. `CashHoldings` IS explicitly listed in `ratio_cols` at engine line 1172:

```python
ratio_cols = [
    ...
    "CashHoldings",
    ...
]
```

Therefore, inf replacement occurs at the engine level (line 1186), not merely at the runner level. The runner's inf replacement at line 226 is a redundant safety net, not the primary mechanism. The audit got the mechanism wrong but the end result (inf values are handled) is correct -- this is a documentation error, not a code bug.

---

## E. Error Found: RepurchaseIndicatorBuilder Docstring Inconsistency (Not Flagged)

**Severity: MINOR**

`repurchase_indicator.py` line 8 says "Returns one column: file_name, REPO" but line 48 actually returns three columns: `file_name`, `REPO`, and `fqtr`. The first-layer audit correctly identifies the actual behavior (V26: "returns REPO + fqtr") but does not flag the misleading docstring as a code quality issue.

---

## F. Verification of Red-Team Findings Disposition (Section 13)

The first-layer audit lists 12 red-team findings (E1--E3, G1--G10, M1--M12). I verify the disposition of each:

| RT Finding | Disposition claimed | Verified? |
|---|---|---|
| E1/M1: TobinsQ formula corrected | Fixed in Section 6 | CONFIRMED -- Section 6 now shows correct formula `(cshoq*prccq + dlcq + dlttq) / atq` |
| E2: LPM heteroskedasticity | Addressed in Section 11 | CONFIRMED -- Section 11 discusses guaranteed heteroskedasticity |
| E3/M5: Stale results | Flagged throughout | CONFIRMED -- "STALE" warnings in Sections 1, 2, 9, results section |
| G1/M2: Non-unique panel index | Addressed in Section 11 | CONFIRMED -- Section 11 has detailed discussion |
| G2/M3: No Horrace-Oaxaca diagnostics | Listed as L2 (HIGH) | CONFIRMED -- L2 in Section 12 |
| G3/M4: No logit robustness | Listed as L3 (MODERATE) | CONFIRMED -- L3 in Section 12 |
| G4/M12: LPM marginal effects | Addressed in Section 11 | CONFIRMED -- discussed under "Marginal effects interpretation" |
| G5/M10: check_rank inconsistency | Listed as L7 (MINOR) | CONFIRMED -- L7 in Section 12 |
| G6/M11: Engine REPO redundancy | Listed as L8 (MINOR) | CONFIRMED -- L8 in Section 12, explained in Section 3 |
| G7/M6: Duong et al. method | Fixed in Section 1 | CONFIRMED -- Method 1 explicitly identified with rationale |
| G8/M7: Endogeneity discussion | Added to Section 11 | CONFIRMED -- dedicated subsection |
| G9/M9: Base rate implications | Added to Section 11 | CONFIRMED -- dedicated subsection |
| G10/M8: Collinearity diagnostics | Listed as L4 (MODERATE) | CONFIRMED -- L4 in Section 12 |

**All 12 dispositions verified as claimed.**

---

## G. Omissions: Risks Not Identified by First-Layer Audit

### G1. Summary statistics computed on pre-filter sample (MODERATE)

**Runner lines 662--676:** The summary statistics table (`summary_stats.csv`, `summary_stats.tex`) is computed on the `panel` dataframe AFTER the main sample filter (line 647) but BEFORE the DV non-null filter, complete-case filter, and min-calls filter (applied inside `prepare_regression_data` starting at line 234). This means the summary statistics describe a different (larger) sample than the regression sample. For a repurchase study with 2004 year restriction and a 70.5% base rate, the summary stats sample could be substantially larger than the regression N.

This is a standard but misleading practice. The thesis should either (a) compute summary statistics on the regression sample, or (b) clearly note the difference in the table caption. The first-layer audit does not flag this discrepancy.

### G2. No discussion of LPM goodness-of-fit alternatives (MINOR)

The audit discusses within-R-squared (~2%) in the context of the high base rate but does not mention that R-squared is a poor measure of fit for binary outcomes. Count-R-squared (fraction correctly classified) or the Brier score would provide more informative diagnostics for an LPM. This is a committee-ready question.

### G3. Attrition table omits intermediate steps (MINOR)

The attrition table (runner lines 705--711) has only 4 stages: full panel, main sample, DV non-null, and final regression sample (col 1). It does not separately report the number of observations dropped by the complete-case filter versus the min-calls filter. These are conflated into a single "After complete-case + min-calls" stage. A replication auditor would want to see these separated to understand whether most attrition comes from missing controls or from the 5-call threshold.

### G4. `file_name` column not loaded by runner (MINOR)

The runner's `load_panel()` at lines 183--194 specifies an explicit column list and does NOT include `file_name`. This means the observation-level identifier is lost at the runner stage. While not needed for regression, it prevents any post-hoc inspection of which specific calls entered the regression. This is a minor traceability gap.

### G5. LaTeX table note on winsorization is inaccurate (MINOR)

The LaTeX table note (runner line 477) states "Variables winsorized at 1%/99% by year at engine level." This is incomplete: textual IVs are winsorized at 0%/99% (upper-only) by the LinguisticEngine, not 1%/99%. The first-layer audit correctly documents this asymmetry in Section 6 (Winsorization Summary) but does not flag the inaccurate LaTeX note.

---

## H. Code-Level Verification: Quarter-Lead Logic

The quarter-lead logic (builder lines 271--272) is the most critical construction for this suite. Independent verification:

- `fqtr_int = 1` -> `next_fqtr = 1 % 4 + 1 = 2`, `next_fyearq = fyearq_int + 0 = fyearq_int`. Correct: Q1 reporting -> Q2 call quarter.
- `fqtr_int = 2` -> `next_fqtr = 2 % 4 + 1 = 3`, `next_fyearq = fyearq_int + 0`. Correct.
- `fqtr_int = 3` -> `next_fqtr = 3 % 4 + 1 = 4`, `next_fyearq = fyearq_int + 0`. Correct.
- `fqtr_int = 4` -> `next_fqtr = 4 % 4 + 1 = 0 + 1 = 1`, `next_fyearq = fyearq_int + 1`. Correct: Q4 reporting -> Q1 of next fiscal year.

The logic is mathematically correct and handles the fiscal year rollover properly.

---

## I. Code-Level Verification: Merge Guards

| Guard | Location | Verified |
|---|---|---|
| Manifest duplicate check | Builder lines 141--146 | CONFIRMED: raises ValueError |
| Per-builder duplicate check | Builder lines 159--164 | CONFIRMED: raises ValueError |
| Post-merge row count | Builder lines 175--182 | CONFIRMED: raises ValueError if count changes |
| REPO_callqtr merge guard | Builder lines 287--292 | CONFIRMED: same pattern |
| Compustat lookup dedup | Builder lines 258--263 | CONFIRMED: drop_duplicates(keep="last") |
| Runner inf replacement | Runner line 226 | CONFIRMED: `df.replace([np.inf, -np.inf], np.nan)` |
| Runner DV non-null | Runner line 234 | CONFIRMED: `df[df[dv].notna()]` |
| Runner complete-case | Runner line 237 | CONFIRMED: `df[required].notna().all(axis=1)` |
| Runner min-calls | Runner lines 241--243 | CONFIRMED: filters to firms with >= 5 calls |

All merge guards verified. The pipeline has adequate protections against row multiplication and data corruption.

---

## J. Code-Level Verification: Estimation Implementation

| Parameter | Audit claim | Code verification | Verdict |
|---|---|---|---|
| Industry FE: `other_effects=industry_data` | Section 7 | Runner line 295: `other_effects=industry_data` where `industry_data = df_panel["ff12_code"]` (line 289) | CONFIRMED |
| Industry FE: `entity_effects=False, time_effects=True` | Section 7 | Runner lines 293--294 | CONFIRMED |
| Firm FE: `EntityEffects + TimeEffects` via formula | Section 7 | Runner line 302: formula includes `EntityEffects + TimeEffects` | CONFIRMED |
| Clustered SEs: `cov_type="clustered", cluster_entity=True` | Section 7 | Runner lines 299 (industry), 304 (firm) | CONFIRMED |
| Two-tailed p-values from model.pvalues | Section 7 | Runner line 328 | CONFIRMED |
| Stars: `* p<0.10, ** p<0.05, *** p<0.01` | Section 7 | Runner lines 351--357: `_sig_stars()` function | CONFIRMED |

---

## K. Structural Assessment of First-Layer Audit

### Strengths

1. **Thorough variable dictionary.** All 16 variables have complete construction chains with code-level citations. The three-way REPO logic (1/0/NaN) is correctly explained.
2. **Correct identification of LPM limitations.** The Horrace-Oaxaca bounds issue, incidental parameters justification for firm FE, and guaranteed heteroskedasticity are all correctly discussed.
3. **Honest handling of stale results.** The audit does not try to hide the fact that results are from a prior specification.
4. **Correct quarter-lead logic documentation.** The one-quarter-forward matching is explained clearly with the Duong et al. (2025) Method 1 rationale.
5. **Design decisions well-documented.** Section 14 provides 8 design decisions with clear rationale.

### Weaknesses

1. **CashHoldings inf replacement misstatement** (Section D above). Minor factual error.
2. **Summary statistics sample mismatch not flagged** (G1 above). The reader is led to believe summary stats describe the regression sample.
3. **LaTeX note inaccuracy not flagged** (G5 above). The 1%/99% claim omits the textual IVs' 0%/99% asymmetry.
4. **Line-number drift.** Several line numbers are off by 2--4 lines (Section B above), suggesting the audit was written against a slightly earlier version of the engine code.

---

## L. Severity-Ranked Issue Register

| # | Severity | Issue | Source |
|---|---|---|---|
| R1 | **HIGH** | Results are stale (6-IV spec, N~27K). Fresh run required with current 4-IV code. | First-layer L1 (verified) |
| R2 | **HIGH** | No Horrace-Oaxaca predicted probability diagnostics for LPM. | First-layer L2 (verified) |
| R3 | **MODERATE** | No logit/probit robustness for industry FE specs (Cols 1, 3). | First-layer L3 (verified) |
| R4 | **MODERATE** | No VIF/condition number diagnostics for 4 correlated IVs. | First-layer L4 (verified) |
| R5 | **MODERATE** | Summary statistics computed on pre-regression-filter sample. | NEW (G1) |
| R6 | **MODERATE** | Non-unique (gvkey, fyearq_int) panel index undiscussed in thesis text. | First-layer L5 (verified) |
| R7 | **MODERATE** | No endogeneity discussion in thesis text. | First-layer L6 (verified) |
| R8 | **MINOR** | CashHoldings inf replacement misattributed to runner instead of engine. | NEW (D) |
| R9 | **MINOR** | LaTeX table note says 1%/99% winsorization but textual IVs use 0%/99%. | NEW (G5) |
| R10 | **MINOR** | RepurchaseIndicatorBuilder docstring says "one column" but returns three. | NEW (E) |
| R11 | **MINOR** | Attrition table conflates complete-case and min-calls stages. | NEW (G3) |
| R12 | **MINOR** | `file_name` not loaded by runner, preventing post-hoc observation tracing. | NEW (G4) |
| R13 | **MINOR** | `check_rank=False` inconsistency between industry/firm FE models. | First-layer L7 (verified) |
| R14 | **MINOR** | Engine REPO column loaded but only used as pass-through for fqtr delivery. | First-layer L8 (verified) |
| R15 | **MINOR** | Several line numbers in first-layer audit off by 2--4 lines due to code drift. | NEW (B) |

---

## M. First-Layer Audit Quality Grade

| Dimension | Grade | Comment |
|---|---|---|
| Factual accuracy | A- | One minor factual error (CashHoldings inf replacement source). All other claims verified. |
| Completeness | B+ | Covers all critical paths. Misses summary-stats sample mismatch (MODERATE) and LaTeX note inaccuracy. |
| Risk identification | A- | Correctly identifies the two HIGH risks (stale results, Horrace-Oaxaca). Misses the summary-stats sample discrepancy. |
| Code traceability | A- | Line numbers mostly correct, with small drift (2--4 lines) in ~5 citations. |
| Disposition follow-through | A | All 12 red-team findings verified as correctly dispositioned. |

**Overall: A-**

The first-layer audit is thorough and substantially accurate. The most important issues (stale results, LPM diagnostics, quarter-lead logic, merge guards) are correctly documented. The new findings from this second-layer audit are all MINOR or MODERATE severity.

---

## N. Recommendations

### Must-fix before thesis submission

1. **Run fresh regressions** with current 4-IV specification (R1).
2. **Add Horrace-Oaxaca diagnostics** to runner: compute fraction of fitted values outside [0, 1] (R2).
3. **Add logit robustness check** for industry FE specifications (R3).

### Should-fix

4. **Add VIF computation** for the 4 IVs to rule out multicollinearity as explanation for null results (R4).
5. **Compute summary statistics on the regression sample**, or add a clear note to the table caption (R5).
6. **Correct the LaTeX table note** to mention 0%/99% for textual variables (R9).

### Nice-to-fix

7. Fix CashHoldings inf replacement description in first-layer audit (R8).
8. Fix RepurchaseIndicatorBuilder docstring (R10).
9. Separate attrition table stages for complete-case vs. min-calls (R11).
10. Include `file_name` in runner column list for traceability (R12).
11. Update drifted line numbers in first-layer audit (R15).

---

## O. Replication Confidence

**Confidence level: HIGH (conditional on fresh run)**

The code implementation is correct. The quarter-lead logic, merge guards, variable constructions, and estimation specifications all verify against the audit documentation. The primary barrier to replication is that the existing results are stale (from a prior 6-IV specification). Once a fresh run is executed with the current 4-IV code, results should be fully reproducible.

---

## P. Sign-Off

This second-layer red-team audit was conducted by independently reading all source files and verifying every factual claim in the first-layer audit. The first-layer audit is substantially accurate (A- overall) with one minor factual error and a handful of omissions, none of which affect the correctness of the implementation. The two HIGH-severity issues (stale results, missing LPM diagnostics) were correctly identified by the first-layer audit and remain open action items.
