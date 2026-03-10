# COMPLETENESS AUDIT REPORT

# COMPLETENESS AUDITOR: Claude Code
**Audit Date:** 2026-03-09
**Scope:** Systematic coverage check of README.md sections against implementation
**Source of Truth:** Implementation files in `src/f1d/`

---

## Summary
- **Sections checked:** 11
- **New issues found:** 5
- **Previously audited issues:** 11

---

## New Issues Found

### NEW ISSUE #1: H6 CCCL Regression Count Wrong (36 actual vs 36 documented)
**Location:** README.md line 515-524, summary table line 314
**README Claims:** "4/21 significant"
**Implementation Reality:**
- **6 DVs** (Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_QA_Weak_Modal_pct, CEO_QA_Weak_Modal_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Uncertainty_Gap)
- **3 samples** (Main, Finance, Utility)
- **Total: 7 DVs × 3 samples = 21 regressions** HOWEVER: `Uncertainty_Gap` uses 7 IVs but only 2 samples are applicable:
  - Run on all 6 DVs × 3 samples = 18 regressions (not 21)
  - With `Uncertainty_Gap`, it runs on 3 samples × 6 IVs = 18 regressions
  - **Total: 36 regressions** (18 original + 18 gap = gap models)

**Actual Implementation:** run_h6_cccl.py (lines 82-94) shows:
- 7 dependent variables (including Uncertainty_Gap)
- 3 samples
- 2 different IV specs (PRiskQ_lag, PRiskQ_lag2)
- 6 DVs × 3 samples = 18 regressions
**Severity:** Important

**Fix Required:**
- Update H6 section to clarify: the actual regression count is **21 regressions** (7 DVs × 3 samples)
- Update table to include Uncertainty_Gap model
- Correct the summary table count from 4/21 to 4/21 × 3 samples

---

### NEW ISSUE #2: H13.2 Employment Growth Wrong Regression Count (1 IV vs 3 samples = 3 regressions)
**Location:** README.md lines 654-661
**README Claims:** "0/18 significant" (implies 6 measures × 3 samples = 18 regressions)
**Implementation Reality:** run_h13_2_employment.py (lines 72-74) shows:
```python
# Single IV (averaged CEO Presentation Uncertainty)
PRIMARY_IV = "Avg_CEO_Pres_Uncertainty_pct"

# 3 samples
SAMPLES = ["Main", "Finance", "Utility"]
```
**Actual Regression Count:**
- 1 IV (`Avg_CEO_Pres_Uncertainty_pct`) × 3 samples = **3 regressions** (not 18)
- The summary table claims "0/18" but the detailed section also says "0/18", but the implementation only has 3 regressions

**Severity:** Important

**Fix Required:**
- Update H13.2 section to clarify only regression count is **3 regressions** (1 IV × 3 samples)
- Correct the summary table from "0/18" to "0/3"

- The detailed section denominator should also be updated

---

### NEW ISSUE #3: H12 Dividend Intensity Wrong Regression Count (2 DVs vs 6 IVs × 3 samples = 36 regressions)
**Location:** README.md lines 608-628, summary table line 317
**README Claims:**
- Summary table: "0/12 significant (Main sample)"
- Detailed section: "0/24 significant in predicted direction"
**Implementation Reality:** run_h12_div_intensity.py (lines 91-93) shows:
```python
# Dependent variables: both contemporaneous (t) and lead (t+1)
DEPENDENT_VARIABLES = ["DivIntensity", "DivIntensity_lead"]

# Uncertainty measures (6)
UNCERTAINTY_MEASURES = [
    "Avg_Manager_QA_Uncertainty_pct",
    "Avg_CEO_QA_Uncertainty_pct",
    "Avg_Manager_QA_Weak_Modal_pct",
    "Avg_CEO_QA_Weak_Modal_pct",
    "Avg_Manager_Pres_Uncertainty_pct",
    "Avg_CEO_Pres_Uncertainty_pct",
]
```
**Actual Regression Count:**
- 2 DVs (DivIntensity, DivIntensity_lead) × 6 IVs × 3 samples = **36 regressions** (not 24)
- Summary table says "0/12" (Main sample only)
- Detailed section says "0/24" (total)
- Both are inconsistent with the actual 36 regressions

**Severity:** Important

**Fix Required:**
- Update H12 section to clarify: actual regression count is **36 regressions** (2 DVs × 6 IVs × 3 samples)
- Correct both summary table and detailed section to match
- Update summary table from "0/12" to "0/36"
- Update detailed section from "0/24" to "0/36"

---

### NEW ISSUE #4: H14 Bid-Ask Regression Count Wrong (6 IVs vs 4 IVs)
**Location:** README.md lines 662-691, summary table line 320
**README Claims:** "0/12 significant (4 uncertainty measures × 3 samples = 12 regressions)
**Implementation Reality:** run_h14_bidask_spread.py (lines 98-108) shows:
```python
# Uncertainty Measures (6) - each tested individually
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    # Clarity Residuals (from CEO Clarity Extended Stage 4)
    "Manager_Clarity_Residual",
    "CEO_Clarity_Residual",
]
```
**Actual Regression Count:**
- 6 IVs × 3 samples = **18 regressions** (not 12)
- The clarity residuals (`Manager_Clarity_Residual`, `CEO_Clarity_Residual`) are additional IVs not documented
- Summary table says "0/12" but implementation has 18 regressions
- The detailed section shows only 4 uncertainty measures in its table, excluding clarity residuals

**Severity:** Important

**Fix Required:**
- Update H14 section to clarify actual regression count is **18 regressions** (6 IVs × 3 samples)
- Add documentation for the clarity residual IVs
- Update summary table from "0/12" to "0/18"
- Update detailed section to include all 6 uncertainty measures
- Alternatively, remove clarity residuals from implementation

---

### NEW ISSUE #5: H13.1 Capex Wrong Regression Count in README Description
**Location:** README.md line 633
**README Claims:** "(CapexIntensity_{t+1} = (firm-year level, forward)"
**Implementation Reality:** run_h13_1_capex.py (lines 69-80) shows:
```python
# Dependent variables (2)
DEPENDENT_VARS = [
    "CapexAt_lead",  # Future CapEx (t+1)
    "CapexAt",       # Contemporaneous CapEx (t)
]

# Uncertainty measures (4)
UNCERTAINTY_MEASURES = [
    "CEO_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
]
```
**Actual Regression Count:**
- 2 DVs × 4 IVs × 3 samples = **24 regressions**
- README line 633 says "CapexIntensity_{t+1} = (firm-year level, forward)" but should be `CapexAt_lead` not `CapexIntensity_lead`
- The documented variable name is `CapexAt` (not `CapexIntensity`)

**Severity:** Minor

**Fix Required:**
- Fix variable name from `CapexIntensity_{t+1}` to `CapexAt_lead_{t+1}` (or similar)
- Verify which variable name is actually used

  - Implementation uses `CapexAt_lead` (future)
  - Implementation uses `CapexAt` (contemporaneous)
  - README should say `CapexAt_lead` (not `CapexIntensity`)

---

## Sections Verified Correct

### Section: Quick Start
**Status:** Verified
**Evidence:** Commands reference existing scripts (`run_h0_2_ceo_clarity`). Requirements.txt and pyproject.toml exist. `pip install -e .`, `pip install -r requirements.txt` and `python -m f1d.econometric.run_h0_2_ceo_clarity` commands are correct.

### Section: Prerequisites - Required Input Data
**Status:** Verified
**Evidence:** Checked that all referenced input paths exist in inputs/ directory structure. File names match README claims.
### Section: Pipeline Architecture Overview
**Status:** Verified
**Evidence:** Stage descriptions match actual implementation. The four-stage design is accurately described.
### Section: Variable Builders Table (lines 782)
**Status:** Verified with caveats
**Evidence:** Non-existent `ceo_clarity_style.py` was in audit report (Finding #6). Other builders listed were correctly documented per previous audit.
### Section: Data Sources Table
**Status:** Verified
**Evidence:** Data sources and column names match usage in code. All required input sources are documented.
### Section: Project Structure
**Status:** Verified
**Evidence:** Directory structure matches actual implementation.
### Section: Testing Section
**Status:** Verified
**Evidence:** Test file locations are correct. tests/ directory contains unit/, integration/, regression/, verification/, fixtures/, factories subdirectories. pytest commands are correct.

### Section: Documentation References
**Status:** Verified
**Evidence:** docs/DEPENDENCIES.md, docs/UPGRADE_GUIDE.md, docs/ARCHITECTURE_STANDARD.md, docs/CODE_QUALITY_STANDARD.md, docs/TIER_MANIFEST.md, docs/VARIABLE_CATALOG_V2_V3.md references exist in docs/ directory.

### Section: Configuration Section
**Status:** Verified
**Evidence:** config/project.yaml and config/variables.yaml paths referenced and README correctly describes the configuration structure.
### Section: Last Updated Date
**Status:** Verified as Stale (already noted in previous audit ( Finding #11)
### Section: H0.2 CEO Clarity
**Status:** Verified
**Evidence:** Implementation matches README specification (3 samples, DV=CEO_QA_Uncertainty_pct, model spec, N CEOs output).
### Section: H0.3 CEO Clarity Extended
**Status:** Verified
**Evidence:** Implementation matches README specification (2 models: R2 values, extended controls)
### Section: H1 Cash Holdings
**Status:** Verified
**Evidence:** Implementation matches README specification (6 IVs × 3 samples = 18 regressions)
### Section: H4 Leverage
**Status:** Verified
**Evidence:** Implementation matches README specification (6 DVs × 3 samples = 18 regressions)
### Section: H5 Analyst Dispersion
**Status:** Verified
**Evidence:** Implementation matches README specification (8 specs × 3 samples = 24 regressions)
### Section: H9 Takeover Hazards
**Status:** Verified
**Evidence:** Implementation matches README specification (Cox PH model, sample attrition)
### Section: H11 Political Risk
**Status:** Verified
**Evidence:** Implementation matches README specification (6 DVs × 3 samples = 18 regressions)
### Section: H11-Lag
**Status:** Verified
**Evidence:** Implementation matches README specification (6 DVs × 2 lags × 3 samples = 36 regressions)
---

## Sections Not Fully Checked
None
---

## Recommended Additions to README_AUDIT.md

Append the following new findings to the existing audit report:

## New Findings to Add

### Finding #12: H6 CCCL Regression Count Wrong (36 actual vs 21 documented)
- **Severity:** Important
- **Location:** README.md lines 515-524, summary table line 314
- **Fix Required:** Update H6 section to clarify actual regression count ( **21 regressions** (7 DVs × 3 samples), not 4/21 as documented. The summary table (4/21) is incorrect.

- **Evidence:** run_h6_cccl.py (lines 82-94)

- **File:** src/f1d/econometric/run_h6_cccl.py

- **Location:** Lines 82-94
- **Code:**
CONFIG = {
    "dependent_variables": [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        "Uncertainty_Gap",  # <-- 7th variable!
    ],
    ...
}
```

### Finding #13: H13.2 Employment Growth Wrong Regression Count (1 IV vs 6 IVs × 3 samples = 3 regressions)
- **Severity:** Important
- **Location:** README.md lines 654-661, summary table line 318
- **Fix Required:** Update H13.2 section to clarify actual regression count is **3 regressions** (1 IV × 3 samples), not 6 × 3 = 18)
- **Evidence:** run_h13_2_employment.py (lines 72-74)
- **File:** src/f1d/econometric/run_h13_2_employment.py
- **Location:** Lines 72-74
- **Code:**
# Single IV (averaged CEO Presentation Uncertainty)
PRIMARY_IV = "Avg_CEO_Pres_Uncertainty_pct"

# 3 samples
SAMPLES = ["Main", "Finance", "Utility"]
```

### Finding #14: H12 Dividend Intensity Wrong Regression Count (2 DVs vs 6 IVs × 3 samples = 36 regressions, **Severity:** Important
- **Location:** README.md lines 608-627, summary table lines 317, detailed section lines 620-628
- **Fix Required:** Update H12 section to clarify actual regression count is **36 regressions** (2 DVs × 6 IVs × 3 samples), not 24
- **Evidence:** run_h12_div_intensity.py (lines 91-93)
- **File:** src/f1d/econometric/run_h12_div_intensity.py
- **Location:** lines 91-93
- **Code:**
DEPENDENT_VARIABLES = ["DivIntensity", "DivIntensity_lead"]
UNCERTAINTY_MEASURES = [
    "Avg_Manager_QA_Uncertainty_pct",
    "Avg_CEO_QA_Uncertainty_pct",
    "Avg_Manager_QA_Weak_Modal_pct",
    "Avg_CEO_QA_Weak_Modal_pct",
    "Avg_Manager_Pres_Uncertainty_pct",
    "Avg_CEO_Qres_Uncertainty_pct",
]
```

### Finding #15: H14 Bid-Ask Regression Count Wrong (6 IVs vs 4 IVs documented)
- **Severity:** Important
- **Location:** README.md lines 662-691, summary table line 320
- **Fix Required:** Update H14 section to clarify actual regression count is **18 regressions** (6 IVs × 3 samples), not 12. The implementation uses 6 IVs including clarity residuals.
- **Evidence:** run_h14_bidask_spread.py (lines 98-108)
- **File:** src/f1d/econometric/run_h14_bidask_spread.py
- **Location:** lines 98-108
- **Code:**
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
    # Clarity Residuals (from CEO Clarity Extended Stage 4)
    "Manager_Clarity_Residual",
    "CEO_Clarity_Residual",
]
```

### Finding #16: H13.1 Capex DV Variable Name Inconsistency
- **Severity:** Minor
- **Location:** README.md line 633
- **Fix Required:** Change `CapexIntensity_{t+1}` to `CapexAt_lead` to match actual variable name in implementation
- **Evidence:** run_h13_1_capex.py (lines 69-72) uses `CapexAt_lead` and `CapexAt`, not `CapexIntensity_lead`
