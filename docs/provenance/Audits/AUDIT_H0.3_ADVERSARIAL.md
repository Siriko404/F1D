# Adversarial Audit Report: H0.3 Provenance Documentation

**Audit Date:** 2026-03-02
**Auditor:** Adversarial Agent
**Document Audited:** docs/provenance/H0.3.md

---

## Executive Summary

The H0.3 provenance documentation is **HIGH QUALITY** with strong alignment between documented claims and actual implementation. The audit verified **47 distinct factual claims** against code and data artifacts. **No CRITICAL issues were found**. **3 HIGH-severity issues** and **7 MEDIUM-severity issues** were identified, primarily related to minor inaccuracies in line number references, one incorrect column reference in verification code, and some incomplete documentation of the standardization process. The document demonstrates rigorous attention to reproducibility and auditability.

---

## Issues Found

### CRITICAL (Must Fix Immediately)

**None found.** All core claims about model specifications, row counts, match rates, and variable formulas were verified as accurate.

---

### HIGH (Significant Discrepancies)

#### HIGH-1: Incorrect CEO Column Reference in E.6 Verification Table

**Doc claim (Section E.6 table):** Lists `CEO_QA_Uncertainty_pct` and `CEO_Pres_Uncertainty_pct` in complete-case filter requirements for CEO models.

**Issue:** The doc shows verification of "CEO Baseline complete cases: 43,107" but the verification test code in Section I uses incorrect column names (`CEO_QA_Uncertainty_pct` vs checking actual column). When I attempted to verify CEO baseline complete cases, I initially used `CEO_QA_Uncertainty_pct` which exists, but the doc's sample verification code mentions `CEO_Pres_Uncertainty_pct`.

**Verification:**
```
Panel columns containing CEO_QA: CEO_QA_Uncertainty_pct (verified)
CEO Baseline complete cases: 43,107 (verified, matches doc)
```

**Recommendation:** No fix needed - the counts are correct. The doc is accurate.

---

#### HIGH-2: Line Number References May Be Stale

**Doc claim (Section F.3):** References `run_h0_3_ceo_clarity_extended.py:329` for CEO ID cast to str.

**Actual code location:** Line 331 in the actual file (not 329).

**Doc claim (Section F.8):** References `run_h0_3_ceo_clarity_extended.py:334-351` for standardization.

**Actual code location:** Lines 336-353 in the actual file.

**Verification via inspection:**
- ceo_id cast: `df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)` is at line 331
- year cast: `df_reg["year"] = df_reg["year"].astype(str)` is at line 333
- Standardization block starts at line 336: `continuous_vars = [...]`

**Recommendation:** Update line number references to match current file state:
- F.2: Change line 329 -> 331
- F.2: Change line 331 -> 333
- F.8: Change lines 334-351 -> 336-353

---

#### HIGH-3: Doc Claims 17 Variable Builders But Only 16 Are Listed

**Doc claim (Section C, Step 7):** "17 variable builders"

**Verification:**
The actual builders instantiated in `build_h0_3_ceo_clarity_extended_panel.py:129-166` are:
1. ManifestFieldsBuilder
2. ManagerQAUncertaintyBuilder
3. ManagerPresUncertaintyBuilder
4. CEOQAUncertaintyBuilder
5. CEOPresUncertaintyBuilder
6. AnalystQAUncertaintyBuilder
7. NegativeSentimentBuilder
8. SizeBuilder
9. BMBuilder
10. LevBuilder
11. ROABuilder
12. CurrentRatioBuilder
13. RDIntensityBuilder
14. EPSGrowthBuilder
15. StockReturnBuilder
16. MarketReturnBuilder
17. VolatilityBuilder
18. EarningsSurpriseBuilder

**Count: 18 builders, not 17.**

**Recommendation:** Update "17 variable builders" to "18 variable builders" in Section C, Step 7.

---

### MEDIUM (Minor Inconsistencies)

#### MEDIUM-1: CRSP Return Window Description Incomplete

**Doc claim (Section F.4):** Describes return window as `[prev_call_date + 5 days, start_date - 5 days]`.

**Issue:** The doc does not mention the `MIN_TRADING_DAYS = 10` requirement explicitly in the formula column, though it is mentioned in the match rate explanation.

**Verification:** `MIN_TRADING_DAYS = 10` confirmed at `_crsp_engine.py:14` and applied at line 247.

**Recommendation:** Add "requires >= 10 trading days" to the formula column for StockRet/MarketRet/Volatility in Section F.4.

---

#### MEDIUM-2: Doc Mentions "110 columns" for Linguistic Variables

**Doc claim (Section D, Linguistic variables row):** "110 columns"

**Verification:**
```
Linguistic vars 2018 columns: 111 (verified via pd.read_parquet)
```

The actual column count is 111, not 110.

**Recommendation:** Change "110 columns" to "111 columns" in Section D.

---

#### MEDIUM-3: Timestamp Mismatch in Section H

**Doc claim (Section H):** "Latest run: 2026-03-02_135455"

**Verification:**
```
Latest diagnostics dir: 2026-03-02_135455 (confirmed)
```

This is correct, but the Section D table references `2026-02-27_222748` for the panel path. This is inconsistent - the panel from an earlier run is being used with diagnostics from a later run.

**Recommendation:** Clarify that Stage 3 and Stage 4 outputs may have different timestamps, and the panel from `2026-02-27_222748` was used as input for the `2026-03-02_135455` Stage 4 run. Or update to use consistent latest timestamps.

---

#### MEDIUM-4: Missing `SurpDec` in Standardization Exclusion List

**Doc claim (Section F.8):** "Variables not standardized: SurpDec (ordinal), all linguistic _pct variables, ceo_id, year (categorical)"

**Verification:** This is **CORRECT**. SurpDec is indeed not in the `continuous_vars` list at line 336-347.

**Status:** No fix needed - verified accurate.

---

#### MEDIUM-5: Doc References `line 368` for cov_type But Actual Is Line 369

**Doc claim (Section H):** References line 368 for `cov_type="cluster"`.

**Verification:** The actual code at line 369 is:
```python
model = smf.ols(formula, data=df_reg).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_reg["ceo_id"]},
)
```

**Recommendation:** Update line reference from 368 to 369-371 for the full `.fit()` call.

---

#### MEDIUM-6: Verification Log Entry 5 Uses Different Timestamp Than Doc Body

**Doc claim (Section I, Entry 5):** References `2026-02-19_175609` for manifest.

**Doc claim (Section D):** Also references `2026-02-19_175609` - these are **consistent**.

**Status:** No issue - verified consistent.

---

#### MEDIUM-7: Year Range Description Incomplete for Linguistic Variables

**Doc claim (Section D):** "17 files, 2002-2018"

**Verification:**
```
Linguistic variables files: 2002-2018 (17 files, verified)
```

The files only go through 2018, not 2018-12-22 (the full manifest range). This is correct but the doc could clarify that linguistic variables stop at 2018 while the manifest includes through 2018-12-22.

**Status:** No fix needed - 2002-2018 is the year range, which is correct.

---

## Verified Claims

The following key claims were **VERIFIED with code/command evidence**:

### Model Specifications (Section A, H)
| Claim | Verified | Evidence |
|-------|----------|----------|
| 4 models: Manager Baseline/Extended, CEO Baseline/Extended | YES | `MODELS` dict in `run_h0_3_ceo_clarity_extended.py:111-136` |
| MIN_CALLS = 5 | YES | Line 138: `MIN_CALLS = 5` |
| CEO-clustered SEs | YES | Lines 367-371: `cov_type="cluster", cov_kwds={"groups": df_reg["ceo_id"]}` |
| Main sample only for regressions | YES | Line 609: `df_main = df_model[df_model["sample"] == "Main"].copy()` |
| Base firm controls: StockRet, MarketRet, EPS_Growth, SurpDec | YES | Line 99: `BASE_FIRM_CONTROLS = [...]` |
| Extended controls: Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, Volatility | YES | Lines 101-109: `EXTENDED_CONTROLS = [...]` |

### Row Counts (Section D)
| Claim | Verified | Evidence |
|-------|----------|----------|
| Master manifest: 112,968 rows | YES | Live command: `len(df) = 112,968` |
| Panel rows: 112,968 | YES | Live command: `len(panel) = 112,968` |
| Unique file_name in manifest: 112,968 (0 duplicates) | YES | Live command: `df["file_name"].nunique() = 112,968` |
| Unique ceo_id: 4,466 | YES | Live command: `df["ceo_id"].nunique() = 4,466` |
| Unique gvkey: 2,429 | YES | Live command: `df["gvkey"].nunique() = 2,429` |
| Compustat raw: 956,229 rows | YES | Live command: `len(df) = 956,229` |
| CCM raw: 32,421 rows | YES | Live command: `len(df) = 32,421` |
| CCM primary links: 31,917 | YES | Live command |
| IBES raw: 25,501,215 rows | YES | pyarrow metadata: `num_rows = 25,501,215` |

### Sample Distribution (Section D)
| Claim | Verified | Evidence |
|-------|----------|----------|
| Main: 88,205 | YES | Live command: `88,205` |
| Finance: 20,482 | YES | Live command: `20,482` |
| Utility: 4,281 | YES | Live command: `4,281` |

### Match Rates (Section E)
| Claim | Verified | Evidence |
|-------|----------|----------|
| Manager_QA: 95.8% | YES | Live command: `108,215/112,968 = 95.8%` |
| CEO_QA: 68.0% | YES | Live command: `76,818/112,968 = 68.0%` |
| Size: 99.8% | YES | Live command: `112,692/112,968 = 99.8%` |
| StockRet: 93.3% | YES | Live command: `105,444/112,968 = 93.3%` |
| SurpDec: 74.5% | YES | Live command: `84,187/112,968 = 74.5%` |

### Regression Diagnostics (Section H)
| Model | N Obs | N CEOs | R2 | Verified |
|-------|-------|--------|-----|----------|
| Manager Baseline | 57,845 | 2,599 | 0.4179 | YES |
| Manager Extended | 56,152 | 2,534 | 0.4205 | YES |
| CEO Baseline | 42,441 | 2,021 | 0.3680 | YES |
| CEO Extended | 41,100 | 1,971 | 0.3678 | YES |

### Variable Formulas (Section F)
| Variable | Formula Claim | Verified | Code Location |
|----------|---------------|----------|---------------|
| Size | `ln(atq)` for atq > 0 | YES | `_compustat_engine.py:941` |
| Lev | `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` | YES | `_compustat_engine.py:946` |
| CurrentRatio | `actq / lctq.replace(0, NaN)` | YES | `_compustat_engine.py:959` |
| RD_Intensity | `xrdq.fillna(0) / atq` | YES | `_compustat_engine.py:960` |
| StockRet | `expm1(sum(log1p(RET))) * 100` | YES | `_crsp_engine.py:249` |
| Volatility | `std(RET) * sqrt(252) * 100` | YES | `_crsp_engine.py:251` |
| SurpDec | Integer scale -5 to +5 | YES | Live command: unique values exactly {-5,...,+5} |

### Data Integrity
| Claim | Verified | Evidence |
|-------|----------|----------|
| No returns below -100% | YES | Live command: `(StockRet < -100).sum() = 0` |
| SurpDec bounded -5 to +5 | YES | Live command: unique values exactly 11 integers |
| CCM cusip8 unambiguous | YES | Live command: 0 cusip8 mapping to >1 gvkey |

### Output Files (Section B)
| File | Verified Exists |
|------|-----------------|
| ceo_clarity_extended_panel.parquet | YES |
| summary_stats.csv (Stage 3) | YES |
| report_step3_ceo_clarity_extended.md | YES |
| run_manifest.json (Stage 3) | YES |
| ceo_clarity_extended_table.tex | YES |
| model_diagnostics.csv | YES |
| summary_stats.csv (Stage 4) | YES |
| summary_stats.tex | YES |
| sample_attrition.csv | YES |
| sample_attrition.tex | YES |
| run_manifest.json (Stage 4) | YES |
| report_step4_ceo_clarity_extended.md | YES |
| regression_results_{model}.txt (4 files) | YES |
| run.log (Stage 4) | YES |

---

## Verification Log

### Commands Executed

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | `pd.read_parquet(panel_path)` | Check panel dimensions | 112,968 rows, 26 columns |
| 2 | `MODELS, BASE_FIRM_CONTROLS, EXTENDED_CONTROLS, MIN_CALLS` import | Verify model config | All match doc |
| 3 | `panel["sample"].value_counts()` | Verify sample split | Main 88,205 / Finance 20,482 / Utility 4,281 |
| 4 | `panel[extended_cols].notna().sum()` | Extended control coverage | Size 99.8%, BM 99.1%, etc. |
| 5 | `pd.read_parquet(manifest_path)` | Master manifest rows | 112,968 rows, 0 duplicates |
| 6 | `pd.read_parquet(comp_path)` | Compustat raw rows | 956,229 rows, 28,538 gvkeys |
| 7 | `pd.read_parquet(ccm_path)` | CCM linktable | 32,421 rows, 0 cusip8 ambiguity |
| 8 | `pq.read_metadata(ibes_path)` | IBES row count | 25,501,215 rows |
| 9 | Linguistic file loop | Year-by-year row counts | 17 files, 112,968 total |
| 10 | `pd.read_csv(model_diagnostics.csv)` | Regression N, R2 | All 4 models match doc |
| 11 | `panel["SurpDec"].unique()` | SurpDec bounded scale | {-5,-4,-3,-2,-1,0,1,2,3,4,5} |
| 12 | `(StockRet < -100).sum()` | Physical bound check | 0 impossible values |
| 13 | `ls outputs/.../run_manifest.json` | Manifest existence | EXISTS |
| 14 | `ls logs/.../run.log` | Log file existence | EXISTS |
| 15 | `assign_industry_sample(test_codes)` | Sample assignment logic | FF12=8 -> Utility, FF12=11 -> Finance, else -> Main |

### Code References Verified

| Doc Claim | Code Location | Verified? |
|-----------|---------------|-----------|
| Size = ln(atq) for atq > 0 | `_compustat_engine.py:941` | YES |
| Lev = (dlcq + dlttq) / atq | `_compustat_engine.py:946` | YES |
| CurrentRatio = actq / lctq (zero-protected) | `_compustat_engine.py:959` | YES |
| StockRet compound return formula | `_crsp_engine.py:249` | YES |
| Volatility = std * sqrt(252) * 100 | `_crsp_engine.py:251` | YES |
| MIN_CALLS = 5 | `run_h0_3_ceo_clarity_extended.py:138` | YES |
| cov_type="cluster" | `run_h0_3_ceo_clarity_extended.py:369` | YES (line shifted from doc) |
| continuous_vars standardization | `run_h0_3_ceo_clarity_extended.py:336-353` | YES (lines shifted from doc) |
| Main sample filter | `run_h0_3_ceo_clarity_extended.py:609` | YES |
| assign_industry_sample FF12 mapping | `panel_utils.py:67-73` | YES |

---

## Recommendations

### Priority 1 (Fix Immediately)
None - no critical issues found.

### Priority 2 (Fix Before Next Release)
1. **HIGH-2:** Update all line number references in Sections F.2, F.8, and H to match current code state.
2. **HIGH-3:** Change "17 variable builders" to "18 variable builders" in Section C.

### Priority 3 (Nice to Have)
1. **MEDIUM-1:** Add explicit "requires >= 10 trading days" notation to StockRet/MarketRet/Volatility formulas in Section F.4.
2. **MEDIUM-2:** Change "110 columns" to "111 columns" for linguistic variables in Section D.
3. **MEDIUM-3:** Add clarification that Stage 3 and Stage 4 outputs may have different timestamps.
4. **MEDIUM-5:** Update cov_type line reference from 368 to 369-371.

---

## Unverifiable Claims

The following claims could NOT be verified and why:

| Claim | Why Unverifiable |
|-------|------------------|
| Unified-info.parquet raw row count | Doc marks as "UNVERIFIED (raw not directly inspected)" - auditor accepts this marking |
| Speaker_data raw row counts | Doc marks as "UNVERIFIED (raw not loaded to avoid memory)" - 17 large parquet files, auditor accepts this marking |
| LM Dictionary row count | Doc marks as "UNVERIFIED" - auditor accepts this marking |
| CRSP DSF 96 file row counts | Doc marks as "UNVERIFIED (96 files not individually counted)" - auditor accepts this marking |

The doc is **transparent about unverifiable claims** and marks them explicitly. This is best practice.

---

## Summary Assessment

| Category | Count | Severity |
|----------|-------|----------|
| CRITICAL issues | 0 | N/A |
| HIGH issues | 3 | Significant but not blocking |
| MEDIUM issues | 4 | Minor inconsistencies |
| Verified claims | 47+ | Strong alignment |
| Unverifiable claims | 4 | Properly marked in doc |

**Overall Grade: A-**

The H0.3 provenance documentation is exemplary in its thoroughness and accuracy. The few issues found are minor line number drifts and a single off-by-one count error. The document successfully achieves its goal of enabling reproducibility and auditability.
