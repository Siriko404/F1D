# README.md Hardnosed Audit Report

**Audit Date:** 2026-03-09
**Auditor:** Claude Code
**Scope:** Full comparison of README.md claims against actual implementation
**Source of Truth:** Implementation files in `src/f1d/`

**Audit Methodology:**
1. Initial hardnosed audit comparing README claims vs implementation
2. Red team adversarial verification of each finding (found 2 errors, corrected)
3. Completeness audit to ensure nothing was missed (added 5 findings)
4. Final red team verification (found 4 errors in audit, corrected)

**Red Team Corrections Applied:**
- Finding #2: Corrected script count from 14 to 15
- Finding #7: Removed `dispersion.py` from missing list (documented in H5)
- Finding #13: Corrected H12 count from 24 to 36 (3 samples, not 2)
- Finding #15: Completely rewrote - H13.2 has only 1 IV, actual count is 3

---

## Executive Summary

The README.md contains **16 significant discrepancies** with the current implementation. The document is outdated in several critical areas:

### Critical Issues (Break User Expectations)
- **Stage 3 Panel Builders section** is missing 4 builders (H11-Lead, H13.1, H13.2, H14)
- **Stage 4 Hypothesis Tests section** is missing 4 scripts (H11-Lead, H13.1, H13.2, H14)
- **H2 Investment model specification** is fundamentally wrong (claims 18 regressions, implementation has 36)
- **H7 Illiquidity model specification** is outdated (claims 9 regressions, implementation has 14)
- **Variable Builder table** lists a non-existent builder (`ceo_clarity_style.py`)

### Important Issues (Documentation Gaps)
- **H11-Lead hypothesis** is completely undocumented
- **Variable Builder table** is missing 5 active builders
- **Archived hypotheses (H8, H0.1)** are not clearly documented
- **Summary table regression counts** are wrong for multiple hypotheses (H6, H12, H13.1, H13.2, H14)
- **H6 CCCL** results table incomplete (missing 17 of 21 regressions)
- **H14 Bid-Ask** missing 2 clarity residual measures in documentation

### Summary Table Cross-Reference
| Hypothesis | README Count | Actual Count | Issue |
|------------|-------------|--------------|-------|
| H2 Investment | 18 | 36 | WRONG |
| H6 CCCL | 4 shown | 21 | INCOMPLETE |
| H7 Illiquidity | 9 | 14 | WRONG |
| H12 Dividend | 12/24 (inconsistent) | 36 | WRONG |
| H13.1 Capex | 18/24 (inconsistent) | 24 | INCONSISTENT |
| H13.2 Employment | 18/24 (inconsistent) | 3 | WRONG (single IV model) |
| H14 Bid-Ask | 12 | 18 | WRONG |

---

## Detailed Findings

### Finding #1: Stage 3 Panel Builders List Incomplete

**Location:** README.md lines 240-255

**README Claims:**
```bash
python -m f1d.variables.build_h0_2_ceo_clarity_panel
python -m f1d.variables.build_h0_3_ceo_clarity_extended_panel
python -m f1d.variables.build_h1_cash_holdings_panel
python -m f1d.variables.build_h2_investment_panel
python -m f1d.variables.build_h3_payout_policy_panel
python -m f1d.variables.build_h4_leverage_panel
python -m f1d.variables.build_h5_dispersion_panel
python -m f1d.variables.build_h6_cccl_panel
python -m f1d.variables.build_h7_illiquidity_panel
python -m f1d.variables.build_h9_takeover_panel
python -m f1d.variables.build_h11_prisk_uncertainty_panel
python -m f1d.variables.build_h11_prisk_uncertainty_lag_panel
python -m f1d.variables.build_h12_div_intensity_panel
```
(13 builders listed)

**Implementation Has:**
```
src/f1d/variables/build_h0_2_ceo_clarity_panel.py
src/f1d/variables/build_h0_3_ceo_clarity_extended_panel.py
src/f1d/variables/build_h1_cash_holdings_panel.py
src/f1d/variables/build_h2_investment_panel.py
src/f1d/variables/build_h3_payout_policy_panel.py
src/f1d/variables/build_h4_leverage_panel.py
src/f1d/variables/build_h5_dispersion_panel.py
src/f1d/variables/build_h6_cccl_panel.py
src/f1d/variables/build_h7_illiquidity_panel.py
src/f1d/variables/build_h9_takeover_panel.py
src/f1d/variables/build_h11_prisk_uncertainty_panel.py
src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py
src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py  # MISSING FROM README
src/f1d/variables/build_h12_div_intensity_panel.py
src/f1d/variables/build_h13_1_capex_panel.py                # MISSING FROM README
src/f1d/variables/build_h13_2_employment_panel.py           # MISSING FROM README
src/f1d/variables/build_h14_bidask_spread_panel.py          # MISSING FROM README
```
(17 builders actual)

**Fix Required:** Add the following to Stage 3 Panel Builders section:
```bash
python -m f1d.variables.build_h11_prisk_uncertainty_lead_panel
python -m f1d.variables.build_h13_1_capex_panel
python -m f1d.variables.build_h13_2_employment_panel
python -m f1d.variables.build_h14_bidask_spread_panel
```

---

### Finding #2: Stage 4 Hypothesis Tests List Incomplete

**Location:** README.md lines 259-275

**README Claims:** 15 scripts listed (ending with `run_h12_div_intensity`)

**Implementation Has:**
```
run_h0_2_ceo_clarity.py
run_h0_3_ceo_clarity_extended.py
run_h1_cash_holdings.py
run_h2_investment.py
run_h3_payout_policy.py
run_h4_leverage.py
run_h5_dispersion.py
run_h6_cccl.py
run_h7_illiquidity.py
run_h9_takeover_hazards.py
run_h11_prisk_uncertainty.py
run_h11_prisk_uncertainty_lag.py
run_h11_prisk_uncertainty_lead.py  # MISSING FROM README
run_h12_div_intensity.py
run_h13_1_capex.py                 # MISSING FROM README
run_h13_2_employment.py            # MISSING FROM README
run_h14_bidask_spread.py           # MISSING FROM README
```

**Fix Required:** Add the following to Stage 4 Hypothesis Tests section:
```bash
python -m f1d.econometric.run_h11_prisk_uncertainty_lead  # ~2 min (placebo test)
python -m f1d.econometric.run_h13_1_capex                 # ~2 min
python -m f1d.econometric.run_h13_2_employment            # ~2 min
python -m f1d.econometric.run_h14_bidask_spread           # ~1 min
```

---

### Finding #3: H2 Investment Model Specification is WRONG

**Location:** README.md lines 395-422

**README Claims:**
- "6 uncertainty measures × 3 samples = 18 regressions"
- "1/18 significant"
- Model: `InvestmentResidual_lead ~ Uncertainty + Lev + Size + TobinsQ + ROA + CashFlow + SalesGrowth + DivIntensity + CashHoldings + firm_maturity + StockRet + EntityEffects + TimeEffects`

**Implementation Reality (src/f1d/econometric/run_h2_investment.py lines 94-111):**
```python
# Dependent variables: 2 (contemporaneous AND lead)
DEPENDENT_VARIABLES = ["InvestmentResidual", "InvestmentResidual_lead"]

# Uncertainty measures: 4 (weak modals removed)
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]

# Clarity residual variables: 2
CLARITY_RESIDUAL_VARS = [
    "CEO_Clarity_Residual",
    "Manager_Clarity_Residual",
]

# Combined: 6 IVs × 2 DVs × 3 samples = 36 regressions
```

**Fix Required:**
- Update regression count: **36 regressions** (2 DVs × 6 IVs × 3 samples)
- Update model specification to include clarity residuals
- Update significant result count based on actual 36 regressions
- Document that weak modal measures were removed
- Document the inclusion of clarity residual IVs

---

### Finding #4: H7 Illiquidity Model Specification is OUTDATED

**Location:** README.md lines 526-548

**README Claims:**
- "3 specs × 3 samples = 9 regressions"
- Only 3 uncertainty measures (QA_Uncertainty, QA_Weak_Modal, Pres_Uncertainty)

**Implementation Reality (src/f1d/econometric/run_h7_illiquidity.py lines 102-114):**
```python
SPECS = [
    # A specs: raw uncertainty measures (all samples)
    ("A1", "CEO_QA_Uncertainty_pct", "CEO QA Uncertainty"),
    ("A2", "CEO_Pres_Uncertainty_pct", "CEO Pres Uncertainty"),
    ("A3", "Manager_QA_Uncertainty_pct", "Manager QA Uncertainty"),
    ("A4", "Manager_Pres_Uncertainty_pct", "Manager Pres Uncertainty"),
    # B specs: clarity residuals (Main sample ONLY)
    ("B1", "CEO_Clarity_Residual", "CEO Clarity Residual"),
    ("B2", "Manager_Clarity_Residual", "Mgr Clarity Residual"),
]

# B specs only run for Main sample
MAIN_ONLY_SPECS = {"B1", "B2"}
```

**Actual Regression Count:**
- A specs: 4 IVs × 3 samples = 12 regressions
- B specs: 2 IVs × 1 sample (Main only) = 2 regressions
- **Total: 14 regressions** (not 9)

**Fix Required:**
- Update regression count to **14**
- Add B specs (clarity residuals) documentation
- Update model specification table to include all 6 specs
- Update significance results table

---

### Finding #5: H11-Lead Hypothesis Completely Undocumented

**Location:** README.md Verified Results section (lines 592-606)

**Issue:** The README mentions H11-Lag but completely omits H11-Lead (placebo test with forward political risk).

**Implementation Reality (src/f1d/econometric/run_h11_prisk_uncertainty_lead.py):**
- Tests `PRiskQ_lead` (1-quarter forward) and `PRiskQ_lead2` (2-quarters forward)
- Purpose: Placebo test for reverse causality (future PRisk should NOT cause current speech)
- Expected result: Lead coefficients should be insignificant
- 6 DVs × 2 lead specs × 3 samples = 36 regressions

**Fix Required:** Add new section:
```markdown
### H11-Lead Political Risk (Placebo Test) — `run_h11_prisk_uncertainty_lead`

Tests whether FUTURE political risk affects CURRENT speech uncertainty (placebo test).
IV: PRiskQ_lead (1-quarter forward) and PRiskQ_lead2 (2-quarters forward).

**Purpose:** Test for reverse causality. Future political risk cannot cause current speech.
Expected result: Lead coefficients should be insignificant.

| Sample | N Obs Range | PRiskQ_lead β | PRiskQ_lead2 β |
|--------|------------:|--------------:|---------------:|
| Main   | [...]       | [results]     | [results]      |
| Finance| [...]       | [results]     | [results]      |
| Utility| [...]       | [results]     | [results]      |

**Result:** [Fill with actual results from latest run]
```

---

### Finding #6: Variable Builder Table Lists Non-Existent Builder

**Location:** README.md lines 751-782 (Linguistic Variable Builders table)

**README Claims:**
```markdown
| `ceo_clarity_style.py` | `ClarityStyle_Realtime` | Stage 2 + frozen CEO assignment |
```

**Implementation Reality:**
- File `src/f1d/shared/variables/ceo_clarity_style.py` **DOES NOT EXIST**
- Variable `ClarityStyle_Realtime` is not exported in `__init__.py`
- This builder was either never implemented or has been removed

**Fix Required:**
- Remove this row from the Linguistic Variable Builders table
- OR implement the builder if still needed

---

### Finding #7: Variable Builder Table Missing Active Builders

**Location:** README.md lines 784-828 (Financial Variable Builders table)

**Missing from README but present in implementation:**

| Builder | Column | Source |
|---------|--------|--------|
| `ceo_clarity_residual.py` | `CEO_Clarity_Residual` | From H0.3 CEO Clarity Extended Stage 4 |
| `manager_clarity_residual.py` | `Manager_Clarity_Residual` | From H0.3 CEO Clarity Extended Stage 4 |
| `prisk_q_lead.py` | `PRiskQ_lead` | Hassan (1-quarter forward) |
| `prisk_q_lead2.py` | `PRiskQ_lead2` | Hassan (2-quarters forward) |

**Note:** `dispersion.py` is documented in the H5 Analyst Dispersion section (lines 471-504), not in the variable builders table.

**Fix Required:** Add these 4 builders to the appropriate table sections.

---

### Finding #8: H13.1 Capex Results Mismatch

**Location:** README.md lines 630-644

**README Claims:**
- "0/24 significant in predicted direction"
- "2/18 significant (Manager measures only)" in summary table (line 318)

**Implementation Reality (src/f1d/econometric/run_h13_1_capex.py):**
- 2 DVs (CapexAt_lead, CapexAt) × 4 uncertainty measures × 3 samples = **24 regressions**
- The "2/18" in the summary table is inconsistent with "0/24" in the H13.1 section

**Fix Required:**
- Reconcile the discrepancy between summary table (2/18) and detailed section (0/24)
- Update summary table to use correct denominator

---

### Finding #9: Archived Hypotheses Not Clearly Documented

**Location:** README.md (no specific section)

**Issue:** The README does not clearly document which hypotheses have been archived and why.

**Implementation Reality:**
- H8 (Political Risk with PRiskFY) is archived in `.archive/h8_removal/`
- H0.1 (Manager Clarity) is archived in `src/f1d/variables/_archived/`
- H0.4, H0.5 are archived in `src/f1d/econometric/_archived/`

**Fix Required:** Add an "Archived Hypotheses" section documenting the archived hypotheses and their locations.

---

### Finding #10: Summary Table Regression Counts Inconsistent

**Location:** README.md lines 304-321 (Summary of hypothesis test results table)

**Issues:**

| Hypothesis | README Claim | Actual Implementation |
|------------|-------------|----------------------|
| H1 Cash | 6/18 | Correct (6 measures × 3 samples = 18) |
| H2 Investment | 1/18 | **WRONG** - Should be X/36 (2 DVs × 6 IVs × 3 samples) |
| H3 Payout | 1/36 | Correct (2 DVs × 6 measures × 3 samples = 36) |
| H4 Leverage | 2/18 | Correct (6 measures × 3 samples = 18) |
| H5 Dispersion | 0/24 | Correct (8 specs × 3 samples = 24) |
| H6 CCCL | 4/21 | **INCOMPLETE** - Shows 4, actual 21 (7 DVs × 3 samples) |
| H7 Illiquidity | 0/9 | **WRONG** - Should be X/14 (6 specs, B only Main) |
| H11 | 16/18 | Correct (6 measures × 3 samples = 18) |
| H11-Lag | 12/18 | Correct (6 measures × 3 samples = 18) |
| H12 Div Intensity | 0/12 | **WRONG** - Should be X/36 (2 DVs × 6 IVs × 3 samples) |
| H13.1 Capex | 2/18 | **WRONG** - Should be X/24 (2 DVs × 4 IVs × 3 samples) |
| H13.2 Employment | 0/18 | **WRONG** - Should be X/3 (1 DV × 1 IV × 3 samples) |
| H14 Bid-Ask | 0/12 | **WRONG** - Should be X/18 (6 IVs × 3 samples) |

**Fix Required:** Update all regression counts to match actual implementation.

---

### Finding #11: Last Updated Date is Stale

**Location:** README.md line 1087

**README Claims:** `*Last updated: 2026-03-05*`

**Audit Date:** 2026-03-09

**Implementation Reality:** Recent commits show updates through 2026-03-08:
- `57ac9d0 refactor: archive H8 political risk and H10 tone at top hypotheses`
- `179f78c refactor(h3,h5,h7): remove interaction terms, add H11 political risk uncertainty lead`
- `37d34e8 feat(h14): add bid-ask spread change hypothesis`

**Fix Required:** Update last updated date to `2026-03-09` (or current date after fixes).

---

### Finding #12: H6 CCCL Results Table Incomplete

**Location:** README.md lines 515-524 (H6 section), line 314 (summary table)

**README Claims:**
- Summary table: "4/21 significant (Finance only; pre-trends concerns)"
- H6 results table only shows 4 rows (2 Main + 1 Finance + 1 Utility)

**Implementation Reality (src/f1d/econometric/run_h6_cccl.py lines 82-94):**
```python
CONFIG = {
    "dependent_variables": [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        "Uncertainty_Gap",  # 7th DV not shown in README table
    ],
    "samples": ["Main", "Finance", "Utility"],
}
```

**Actual Regression Count:** 7 DVs × 3 samples = **21 regressions**
- README table shows only 4 results, missing 17 regressions
- Weak Modal measures and Uncertainty_Gap results not shown

**Fix Required:**
- Expand H6 results table to show all 7 DVs × 3 samples = 21 regressions
- Add rows for Weak Modal measures and Uncertainty_Gap
- Verify "4/21 significant" count is accurate

---

### Finding #13: H12 Dividend Intensity Inconsistent Denominator

**Location:** README.md line 317 (summary table), lines 620-628 (H12 section)

**README Claims:**
- Summary table: "0/12 significant (Main sample)"
- Detailed section total row: "0/24"

**Implementation Reality (src/f1d/econometric/run_h12_div_intensity.py lines 91-102, 433):**
```python
DEPENDENT_VARIABLES = ["DivIntensity", "DivIntensity_lead"]  # 2 DVs

UNCERTAINTY_MEASURES = [
    "Avg_Manager_QA_Uncertainty_pct",
    "Avg_CEO_QA_Uncertainty_pct",
    "Avg_Manager_QA_Weak_Modal_pct",
    "Avg_CEO_QA_Weak_Modal_pct",
    "Avg_Manager_Pres_Uncertainty_pct",
    "Avg_CEO_Pres_Uncertainty_pct",
]  # 6 IVs

samples = ["Main", "Finance", "Utility"]  # 3 samples

# 2 DVs × 6 IVs × 3 samples = 36 regressions
```

**Actual Regression Count:** 2 DVs × 6 IVs × 3 samples = **36 regressions**
- Summary table says "0/12" and detailed section says "0/24" - both are wrong
- The detailed section count of 24 is also incorrect (missing Utility sample)

**Fix Required:**
- Update summary table from "0/12" to "0/36"
- Update detailed section total from "0/24" to "0/36"
- Ensure consistency between summary and detailed sections

---

### Finding #14: H13.1 Capex Summary vs Detail Mismatch

**Location:** README.md line 318 (summary table), lines 638-642 (H13.1 section)

**README Claims:**
- Summary table: "2/18 significant (Manager measures only)"
- Detailed section: "0/24"

**Implementation Reality (src/f1d/econometric/run_h13_1_capex.py lines 69-80):**
```python
DEPENDENT_VARS = ["CapexAt_lead", "CapexAt"]  # 2 DVs

UNCERTAINTY_MEASURES = [
    "CEO_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
]  # 4 IVs

# 2 DVs × 4 IVs × 3 samples = 24 regressions
```

**Actual Regression Count:** 2 DVs × 4 IVs × 3 samples = **24 regressions**
- Summary says "2/18" but detail says "0/24" - **major inconsistency**
- Either 2 results are significant (not documented in detail) OR summary is wrong

**Fix Required:**
- Reconcile summary table ("2/18") with detailed section ("0/24")
- If 2 significant, document which ones in detailed section
- If 0 significant, update summary to "0/24"

---

### Finding #15: H13.2 Employment Wrong Model Structure

**Location:** README.md line 319 (summary table), lines 654-661 (H13.2 section)

**README Claims:**
- Summary table: "0/18 significant"
- Detailed section: "0/24"

**Implementation Reality (src/f1d/econometric/run_h13_2_employment.py lines 74, 102):**
```python
PRIMARY_IV = "Avg_CEO_Pres_Uncertainty_pct"  # ONLY 1 IV

SAMPLES = ["Main", "Finance", "Utility"]  # 3 samples

# 1 DV (EmploymentGrowth_lead) × 1 IV × 3 samples = 3 regressions
```

**Actual Regression Count:** 1 DV × 1 IV × 3 samples = **3 regressions**
- H13.2 has a completely different structure from H13.1
- Uses only a single primary IV (CEO Presentation Uncertainty)
- Summary says "0/18" and detail says "0/24" - both are wrong

**Fix Required:**
- Update summary table from "0/18" to "0/3"
- Update detailed section to reflect actual model structure
- Document that H13.2 uses only a single IV (not 4 like H13.1)

---

### Finding #16: H14 Bid-Ask Spread Missing Measures

**Location:** README.md line 320 (summary table), lines 662-691 (H14 section)

**README Claims:**
- Summary table: "0/12 significant"
- H14 table shows only 3 specs

**Implementation Reality (src/f1d/econometric/run_h14_bidask_spread.py lines 98-108):**
```python
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    "Manager_Clarity_Residual",  # NOT documented in README
    "CEO_Clarity_Residual",      # NOT documented in README
]
```

**Actual Regression Count:** 6 IVs × 3 samples = **18 regressions**
- Summary says "0/12" but there are 18 regressions
- 2 clarity residual measures are not documented in README

**Fix Required:**
- Update summary table from "0/12" to "0/18"
- Document clarity residual measures in H14 section
- Expand results table to include all 6 measures

---

## Summary Table Inconsistencies (Cross-Reference)

| Hypothesis | Summary Table | Detailed Section | Actual (Impl) | Status |
|------------|---------------|------------------|---------------|--------|
| H2 Investment | 1/18 | - | 36 | WRONG |
| H6 CCCL | 4/21 | Shows 4 results | 21 | INCOMPLETE |
| H7 Illiquidity | 0/9 | - | 14 | WRONG |
| H12 Dividend | 0/12 | 0/24 | 36 | BOTH WRONG |
| H13.1 Capex | 2/18 | 0/24 | 24 | INCONSISTENT |
| H13.2 Employment | 0/18 | 0/24 | 3 | BOTH WRONG (single IV) |
| H14 Bid-Ask | 0/12 | Shows 3 specs | 18 | WRONG |

---

## Prioritized Fix List

### Priority 1: Critical (Breaks User Expectations)

| # | Finding | Fix Required | Lines Affected |
|---|---------|--------------|----------------|
| 1 | Stage 3 builders list incomplete | Add 4 missing builders | 240-255 |
| 2 | Stage 4 tests list incomplete | Add 4 missing scripts | 259-275 |
| 3 | H2 model specification wrong | Complete rewrite of H2 section | 395-422 |
| 4 | H7 regression count wrong | Update from 9 to 14 | 526-548 |
| 6 | Non-existent variable builder listed | Remove `ceo_clarity_style.py` | 751-782 |

### Priority 2: Important (Documentation Gaps)

| # | Finding | Fix Required | Lines Affected |
|---|---------|--------------|----------------|
| 5 | H11-Lead undocumented | Add new section | ~590-610 |
| 7 | Variable builders missing | Add 5 missing builders | 784-828 |
| 9 | Archived hypotheses not documented | Add new section | New |
| 10 | Summary table inconsistent | Update all counts | 304-321 |
| 12 | H6 CCCL results table incomplete | Add missing DVs (7 total) | 515-524 |
| 13 | H12 Dividend inconsistent denominator | Fix 0/12 to 0/24 | 317, 620-628 |
| 14 | H13.1 Capex summary vs detail mismatch | Reconcile 2/18 vs 0/24 | 318, 638-642 |
| 15 | H13.2 Employment wrong denominator | Verify and fix count | 319, 654-661 |
| 16 | H14 Bid-Ask missing measures | Add 2 clarity residuals | 320, 662-691 |

### Priority 3: Minor (Inconsistencies)

| # | Finding | Fix Required | Lines Affected |
|---|---------|--------------|----------------|
| 8 | H13.1 results mismatch | Reconcile counts | 630-644 |
| 11 | Last updated date stale | Update date | 1087 |

---

## Recommended Fix Order

1. **Remove non-existent `ceo_clarity_style.py` from variable table** (Finding #6)
2. **Add missing Stage 3 and Stage 4 scripts** (Findings #1, #2)
3. **Rewrite H2 Investment section** with correct model spec (Finding #3)
4. **Rewrite H7 Illiquidity section** with correct spec (Finding #4)
5. **Add H11-Lead section** (Finding #5)
6. **Add missing variable builders to table** (Finding #7)
7. **Update summary table regression counts** (Finding #10)
8. **Add Archived Hypotheses section** (Finding #9)
9. **Fix H6 CCCL results table** - add missing DVs (Finding #12)
10. **Fix H12 Dividend denominator** (Finding #13)
11. **Reconcile H13.1 Capex summary vs detail** (Finding #14)
12. **Fix H13.2 Employment denominator** (Finding #15)
13. **Add H14 clarity residual measures** (Finding #16)
14. **Update last modified date** (Finding #11)

---

## Verification Commands

After fixes, verify with:

```bash
# Count Stage 3 panel builders
ls src/f1d/variables/build_*.py | grep -v _archived | wc -l
# Expected: 17

# Count Stage 4 hypothesis tests
ls src/f1d/econometric/run_*.py | grep -v _archived | wc -l
# Expected: 17

# Verify variable builders exist
for f in ceo_clarity_style ceo_clarity_residual manager_clarity_residual prisk_q_lead; do
  if [ -f "src/f1d/shared/variables/${f}.py" ]; then
    echo "EXISTS: ${f}.py"
  else
    echo "MISSING: ${f}.py"
  fi
done
```

---

## End of Audit Report

**Total Findings:** 16
**Critical:** 5
**Important:** 9
**Minor:** 2

**Audit Methodology:**
1. Initial hardnosed audit of README vs implementation (11 findings)
2. Red team adversarial verification (found 2 errors in original audit, corrected)
3. Completeness audit to find missed issues (5 additional findings)

**Estimated Fix Time:** 3-4 hours
