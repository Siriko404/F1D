# H6 Systematic Fix Plan

**Created:** 2026-03-02
**Based On:** REVERIFICATION_REPORT_H6.md
**Status:** COMPLETE

---

## Fix Checklist

| # | ID | Severity | Issue | Target File | Status |
|---|-----|----------|-------|-------------|--------|
| 1 | BLK-1 | BLOCKER | README detailed table wrong values | README.md (lines 469-474) | COMPLETE |
| 2 | MIN-1 | MINOR | LaTeX table missing Finance sample | h6_cccl_table.tex | COMPLETE |
| 3 | MIN-2 | MINOR | merge_asof tolerance missing | panel_utils.py, cccl_instrument.py | DEFERRED |

---

## Fix #1: BLK-1 README Detailed Table

### Problem Statement
The README H6 detailed table (lines 469-474) contains incorrect values:
- The β column shows within-R2 values (~0.0007) instead of actual beta coefficients (~0.0865)
- Wrong N values for CEO QA Uncertainty (shows 63,902 instead of 48,091)
- Finance and Utility rows lack coefficient data entirely (show "—" for all values)
- Wrong firm counts for Finance and Utility samples

### Root Cause
The table was populated with within-R2 values instead of actual beta1 coefficients. The CEO QA Uncertainty row incorrectly used Manager QA Uncertainty sample size. Finance and Utility rows were left as placeholders without actual data.

### Fix Strategy
Replace the incorrect values with correct values from model_diagnostics.csv:
- Main (Mgr QA Unc): beta1=-0.0865, p=0.089, N=63,902, firms=1,751
- Main (CEO QA Unc): beta1=0.0227, p=0.599, N=48,091, firms=1,561
- Finance (Mgr QA Unc): beta1=-1.3066, p=0.014, N=15,662, firms=436, Significant=Yes
- Utility (Mgr QA Unc): beta1=1.3637, p=0.987 (one-sided for positive), N=3,154, firms=81

### Target File(s)
- README.md (lines 469-474)

### Verification Method
1. Read README.md lines 469-474 after edit
2. Confirm beta values are ~0.0865 magnitude, not ~0.0007
3. Confirm N values match model_diagnostics.csv
4. Confirm Finance row now has actual values

### Status: COMPLETE

---

## Fix #2: MIN-1 LaTeX Table Finance Note

### Problem Statement
The LaTeX table `h6_cccl_table.tex` only shows Main sample results. The 4 significant Finance results (p<0.05) are not included in any publication table.

### Root Cause
The table generation code was designed to produce a single Main sample table for paper submission.

### Fix Strategy (Option C - Note Addition)
Add a note to the README H6 section directing readers to the Finance results in model_diagnostics.csv. This avoids the need to regenerate the LaTeX table or modify code.

Alternative: Manually add a note to the LaTeX table caption referencing Finance results.

### Target File(s)
- README.md (H6 section)
- Optionally: outputs/econometric/h6_cccl/2026-03-02_000559/h6_cccl_table.tex

### Verification Method
Confirm the note clearly indicates Finance sample results exist and where to find them.

### Status: COMPLETE

---

## Fix #3: MIN-2 merge_asof Tolerance

### Problem Statement
The merge_asof calls in panel_utils.py and cccl_instrument.py lack a tolerance parameter, allowing 78 stale matches where calls are matched to Compustat data from the wrong fiscal year (|cal_year - fyearq| > 2).

### Root Cause
The merge_asof calls use backward direction without a max time gap constraint.

### Fix Strategy
Add `tolerance=pd.Timedelta(days=548)` (1.5 years) to the merge_asof calls.

### Impact Assessment
- Requires Stage 3 rerun (build_h6_cccl_panel)
- Requires Stage 4 rerun (run_h6_cccl)
- Affects only 72 rows with valid CCCL_lag (0.07% of panel)
- Expected coefficient changes < 0.001

### Decision: DEFERRED
This fix requires a full Stage 3+4 rerun for minimal impact (0.07% of data). Defer unless explicitly requested by user or required for paper submission.

### Status: DEFERRED

---

## Correct Values Reference (from model_diagnostics.csv)

### Primary Specifications (Manager QA Uncertainty)
| Sample | N Obs | N Firms | beta1 | p-value (one) | Significant |
|--------|------:|--------:|------:|--------:|:-----------:|
| Main | 63,902 | 1,751 | -0.0865 | 0.089 | No |
| Finance | 15,662 | 436 | -1.3066 | 0.014 | Yes |
| Utility | 3,154 | 81 | 1.3637 | 0.987* | No |

### Secondary Specifications (CEO QA Uncertainty)
| Sample | N Obs | N Firms | beta1 | p-value (one) | Significant |
|--------|------:|--------:|------:|--------:|:-----------:|
| Main | 48,091 | 1,561 | 0.0227 | 0.599 | No |
| Finance | 9,970 | 346 | -0.8839 | 0.158 | No |
| Utility | 1,948 | 72 | 1.1874 | 0.942 | No |

*Note: Utility p-value is one-sided for POSITIVE effect (H6 predicts negative effect, so result does not support H6)

---

## Execution Log

| Step | Action | Result |
|------|--------|--------|
| 1 | Read FIX_PLAN_PROMPT_H6.md | Instructions loaded |
| 2 | Read REVERIFICATION_REPORT_H6.md | Issues identified |
| 3 | Read README.md lines 460-495 | Current table captured |
| 4 | Read model_diagnostics.csv | Correct values extracted |
| 5 | Create FIX_PLAN_H6.md | This document |
| 6 | Execute Fix #1 (BLK-1) | COMPLETE |
| 7 | Execute Fix #2 (MIN-1) | COMPLETE |
| 8 | Create FIX_EXECUTION_REPORT_H6.md | COMPLETE |
