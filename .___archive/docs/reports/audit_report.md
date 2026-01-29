# Audit Report: README.md vs. Project State

**Date:** 2025-12-05
**Auditor:** Antigravity

## Summary
The `README.md` is largely accurate and up-to-date with the current project structure and scripts. However, one specific discrepancy regarding the output directory for Step 2.5c was identified.

## Findings

### 1. Step 2.5c Output Directory Mismatch (High Priority)
-   **Documentation**: The README states the output directory is `4_Outputs/2.5c_FilterCeos`.
-   **Actual State**: The configuration (`config/project.yaml`) and script (`2.5c_FilterCallsAndCeos.py`) use `4_Outputs/2.5c_FilterCallsAndCeos`.
-   **Impact**: Users following the README path literally will not find the files.
-   **Recommendation**: Update README to reflect the correct directory `2.5c_FilterCallsAndCeos`.

### 2. Unaccounted Helper Script (Low Priority)
-   **Observation**: `2_Scripts/2.7_ComputeReturnsVectorized.py` exists but is not mentioned in the README.
-   **Context**: This is a helper module imported by `2.7_BuildFinancialControls.py` to optimize performance. It is not a standalone step.
-   **Recommendation**: Optional. Add a note in the Step 2.7 section about the vectorized implementation for performance transparency.

### 3. Legacy Directories (Informational)
-   **Observation**: The `4_Outputs` directory contains `2.2_ExtractQaManagerDocs` and `2.2v2_ExtractQaManagerDocs`, which are not in the README.
-   **Context**: The README correctly points to `2.2_ExtractFilteredDocs`, implying the others are legacy/superseded.
-   **Recommendation**: No action needed for README. Consider cleaning up legacy directories if they are no longer needed.

## Proposed Updates

### Update Step 2.5c Section
```markdown
**Outputs**:
- `4_Outputs/2.5c_FilterCallsAndCeos/{timestamp}/f1d_enriched_ceo_filtered_YYYY.parquet`
  - Calls where CEO has ≥5 total calls across the sample
- `4_Outputs/2.5c_FilterCallsAndCeos/{timestamp}/f1d_dropped_ceo_calls_YYYY.parquet`
  - Calls where CEO has <5 total calls (excluded from analysis)
- `3_Logs/2.5c_FilterCallsAndCeos/{timestamp}.log`
```
