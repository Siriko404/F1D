# README.md Audit Report

**Date:** 2025-01-08
**Auditor:** Claude Code
**Project:** F1D: CEO Communication Clarity and Market Outcomes
**Severity:** CRITICAL - Multiple documentation mismatches found

---

## Executive Summary

The README.md file contains **significant discrepancies** when compared against:
1. The actual implemented scripts in `2_Scripts/`
2. The project configuration in `config/project.yaml`
3. The project memory in `.claude/CLAUDE.md`
4. The actual input data files in `1_Inputs/`
5. The actual output directories in `4_Outputs/`

**Key Finding:** The README documents a **different pipeline** than what is actually implemented, creating confusion about which scripts represent the "source of truth" for this project.

---

## Critical Issues

### Issue 1: Pipeline Documentation vs. Actual Implementation

**Severity: CRITICAL**

The README describes Steps 1-4 with a specific pipeline structure, but this does not align with the actual implemented workflow:

| README Claims | Reality (CLAUDE.md + OLD/ scripts) |
|--------------|-------------------------------------|
| Step 1: Sample (1.0-1.4) | STEP 00: Unified Info Check |
| Step 2: Text Processing (2.1-2.3) | STEPS 00b, 00c, 01, 02, 03, 04 |
| Step 3: Financial Features (3.0-3.3) | STEPS 05, 05b, 05c, 07 |
| Step 4: Econometric Analysis (4.1-4.3.1) | STEP 08 |

**Evidence:**
- `2_Scripts/OLD/` contains scripts numbered `2.0`, `2.1`, `2.2`, etc. matching CLAUDE.md
- `2_Scripts/1_Sample/`, `2_Text/`, `3_Financial/`, `4_Econometric/` exist but represent a NEWER/REDONE pipeline
- The README documents the NEW scripts as if they are the current implementation

**Impact:** Users following the README will be confused about which scripts to run. The OLD/ scripts represent the proven pipeline (286,652 calls), while the new scripts (1-4) appear to be incomplete or experimental.

---

### Issue 2: Variable Naming Inconsistency

**Severity: HIGH**

The README uses one naming convention, but the config/project.yaml uses another:

| README Variable | Config/CLAUDE.md Variable |
|----------------|---------------------------|
| `Manager_QA_Uncertainty_pct` | `MaQaUnc_pct` |
| `Manager_Pres_Uncertainty_pct` | `MaPresUnc_pct` |
| `Analyst_QA_Uncertainty_pct` | `AnaQaUnc_pct` |
| `Entire_All_Negative_pct` | `EntireCallNeg_pct` |

**Note:** The actual script `4.1_EstimateCeoClarity.py` uses the README naming convention (`Manager_QA_Uncertainty_pct`), suggesting the new scripts were designed independently of the original pipeline.

---

### Issue 3: Data Source Inconsistencies

**Severity: HIGH**

| Data Source | README Claim | Actual File | Notes |
|------------|-------------|-------------|-------|
| CEO Tenure Data | `1_Inputs/Execucomp/comp_execucomp.parquet` | `CEO Dismissal Data 2021.02.03.xlsx` | Different source entirely |
| SDC M&A | `1_Inputs/SDC/sdc-ma-merged.parquet` | `1_Inputs/SDC/` (directory exists) | File path unverified |

**Impact:** The README documentation for Step 1.3 (BuildTenureMap) describes Execucomp processing, but the actual OLD scripts use the CEO Dismissal Excel file.

---

### Issue 4: Sample Count Discrepancy

**Severity: MEDIUM**

| Source | Call Count |
|--------|-----------|
| README Key Findings (line 13) | ~75,000 calls |
| CLAUDE.md Final Outputs | 286,652 calls |

**Explanation:** The 286,652 figure likely represents the full universe before CEO filtering, while 75,000 may represent the filtered sample. However, this distinction is not clearly documented.

---

### Issue 5: Output Directory Structure Mismatch

**Severity: MEDIUM**

The README's repository structure (lines 19-37) shows:
```
4_Outputs/
├── 1.0_BuildSampleManifest/
├── 2_Textual_Analysis/
├── 3_Financial_Features/
├── 4.1_CeoClarity/
...
```

But the actual OLD pipeline outputs would be:
```
4_Outputs/
├── 2.0_UnifiedInfoCheck/
├── 2.1_BuildLmClarityDictionary/
├── 2.2_ExtractFilteredDocs/
├── 2.3_TokenizeAndCount/
├── 2.4_BuildF1dPanel/
...
```

---

### Issue 6: Missing "latest" Symlinks

**Severity: MEDIUM**

The README describes a `latest/` symlink convention (line 39), but verification shows:
```
No files found
```
when searching for `4_Outputs/*/latest/*.parquet`. This suggests either:
1. The symlinks were never created
2. They don't work on Windows (MSYS environment)
3. The pipeline hasn't been run successfully with the new scripts

---

### Issue 7: Step Numbering Inconsistency

**Severity: MEDIUM**

Three different step numbering schemes exist:

| Context | Scheme |
|---------|--------|
| README | 1.0, 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.0, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3 |
| CLAUDE.md | 00, 00b, 00c, 01, 02, 03, 04, 05, 05b, 05c, 07, 08 |
| OLD/ scripts | 2.0, 2.0b, 2.0c, 2.1, 2.2, 2.3, 2.4, 2.5, 2.5b, 2.5c, 2.7, 2.8 |
| Config YAML | step_00, step_00b, step_00c, step_01, step_02, step_03, step_04 |

**Recommendation:** Choose one convention and document it clearly.

---

## Specific Line-by-Line Issues

### Line 13: "Key Findings"
```
**Key Findings**: The dataset covers ~75,000 earnings calls from 2002-2018...
```
**Issue:** This conflicts with CLAUDE.md which states 286,652 calls. Clarify whether this is pre-filter or post-filter count.

### Lines 145-146 (Step 1.3 BuildTenureMap)
```
**File**: `1_Inputs/Execucomp/comp_execucomp.parquet`
**Description**: Raw Execucomp data containing executive compensation and tenure details.
```
**Issue:** The actual OLD scripts use `CEO Dismissal Data 2021.02.03.xlsx`. The Execucomp directory exists but its role is unclear.

### Line 246 (Step 2.2 Output path)
```
*   **File**: `4_Outputs/2.4_Linguistic_Variables/{timestamp}/linguistic_variables_{year}.parquet`
```
**Issue:** The Step number in the path (2.4) doesn't match the script number (2.2). This suggests inconsistent planning.

### Line 258 (Step 2.3 title)
```
### 2.3_VerifyStep2.py
```
**Issue:** This is a verification script, not a processing step. It should be documented as a utility, not a main pipeline step.

### Lines 292-296 (Step 3.0 outputs)
```
*   `firm_controls_{year}.parquet` (from 3.1)
*   `market_variables_{year}.parquet` (from 3.2)
*   `event_flags_{year}.parquet` (from 3.3)
```
**Issue:** These files don't appear to exist in 4_Outputs. The old pipeline uses `calls_with_controls_YYYY.parquet` naming instead.

---

## Missing Documentation

### 1. The OLD/ Directory
The README does not explain:
- Why `2_Scripts/OLD/` exists
- What the old scripts do
- Whether the old scripts are deprecated or still valid
- The relationship between old and new scripts

### 2. Archive Directories
No mention of:
- `2_Scripts/2_Text/ARCHIVE_BROKEN_STEP2/`
- What was broken and why it was archived

### 3. Variable Reference File
The file `1_Inputs/master_variable_definitions.csv` exists but is not documented in the README.

### 4. Execucomp vs CEO Dismissal Data
The README mentions Execucomp but the actual implementation uses CEO Dismissal data. The relationship between these sources is unclear.

---

## Recommendations

### Immediate Actions Required:

1. **Clarify Pipeline Status**
   - Document which pipeline is "current": OLD scripts or new 1-4 scripts
   - If new: explain what was wrong with old pipeline
   - If old: remove or mark new scripts as experimental

2. **Standardize Variable Names**
   - Choose one naming convention (descriptive vs. abbreviated)
   - Apply consistently across README, config, and scripts
   - Provide a mapping table if both are used

3. **Fix Sample Count Documentation**
   - Document both pre-filter and post-filter call counts
   - Explain the filtering process and how ~286K becomes ~75K

4. **Resolve Data Source Ambiguity**
   - Clarify which CEO data source is used
   - Document both Execucomp and CEO Dismissal Data roles

5. **Fix Step Numbering**
   - Choose one scheme (recommend: 1.0, 1.1, etc. for clarity)
   - Apply to README, config, and directory naming
   - Update all documentation

6. **Verify Output Paths**
   - Either create `latest/` symlinks or document Windows limitations
   - Ensure all documented output paths actually exist
   - Provide example outputs

7. **Add Architecture Diagram**
   - Visual showing data flow from inputs to outputs
   - Clear labeling of which scripts are used in production

### Documentation Structure Recommendations:

```
README.md (should contain):
├── Project Overview (current)
├── Pipeline Status (NEW: explain old vs new)
├── Quick Start (NEW: minimal commands to run)
├── Repository Structure (current - needs update)
├── Data Sources (NEW: consolidated source documentation)
├── Pipeline Steps (reorganize by current vs. old)
├── Variable Definitions (current)
└── Troubleshooting (NEW)
```

---

## Positive Findings

1. **Detailed Script Documentation:** Each script has thorough input/output documentation
2. **Conceptual Explanations:** The regression model explanations are clear
3. **Variable Definition Table:** Comprehensive variable reference at end
4. **Contract Headers:** Scripts follow the project's documentation conventions

---

## Conclusion

The README.md requires significant revision to accurately reflect the current state of the project. The primary issue is that it documents a newer/experimental pipeline (Steps 1-4) without explaining the proven pipeline in OLD/ that actually produces the documented outputs.

**Priority: HIGH** - This documentation mismatch could lead to:
- Wasted time running wrong scripts
- Confusion for new contributors
- Reproducibility issues
- Incorrect analysis based on wrong data

---

**Audit Completed:** 2025-01-08
**Next Review:** After pipeline status is resolved
