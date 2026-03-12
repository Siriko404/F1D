File: CLAUDE_H9_PROVENANCE_PASS_02.md
Scope: H9 provenance cleanup only
Edits made: H9.md only
Model/code changes made: None
Status: Complete

# H9 Provenance Cleanup — Pass 02

# Task 1 — Scope Lock

**Target file confirmed**: `docs/provenance/H9.md` (only file edited)

**Prohibited files not touched**:
- No `.py` files edited
- No output files edited
- No `.tex` files edited
- No CSVs edited
- No audit docs edited
- No report_step*.md outputs edited

**No code/model/output regeneration performed**: This was a document truthfulness pass only.

---

# Task 2 — Exact Edits Applied

## Edit A — Fixed False Issue-1 Wording

**Section**: J. Known Issues / Ambiguities → Issue 1

**What changed**: Replaced false claim "Only CEO variant remains" with truthful documentation of 3 variants.

**Before**:
```
**Verification Status**: RESOLVED. Dead code removed. Only CEO variant remains.
```

**After**:
```
**Current State**: RESOLVED. Three variants now exist:
1. **CEO**: Uses `ClarityCEO` + `CEO_QA_Uncertainty_pct`
2. **CEO_Residual**: Uses `CEO_Clarity_Residual` + `CEO_QA_Uncertainty_pct`
3. **Manager_Residual**: Uses `Manager_Clarity_Residual` + `Manager_QA_Uncertainty_pct`

**Note**: The original Regime variant (using raw ClarityManager FE) was replaced by Manager_Residual, which uses residualized Manager clarity. These are semantically different measures.
```

---

## Edit B — Updated Stale Verification Command Blocks

**Section**: D. Data Provenance → Raw Input File Verification

**What changed**:
- Removed specific timestamped run paths (replaced with `latest/`)
- Updated stale assert from 27,787 to 27,773
- Updated unique firm count from 2,429 to 2,415
- Updated comment to reflect 3-variant structure

**Before**:
```python
# Verified: H9 panel has 27,773 firm-year intervals (CEO variant only)
h9_panel = pd.read_parquet('outputs/variables/takeover/2026-02-28_152253/takeover_panel.parquet')
assert len(h9_panel) == 27_787
assert h9_panel['gvkey'].nunique() == 2_429
```

**After**:
```python
# Verified: H9 panel has 27,773 firm-year intervals (3 variants: CEO, CEO_Residual, Manager_Residual)
h9_panel = pd.read_parquet('outputs/variables/takeover/latest/takeover_panel.parquet')
assert len(h9_panel) == 27_773
assert h9_panel['gvkey'].nunique() == 2_415
```

---

## Edit C — Clarified SDC Count Presentation

**Section**: D. Data Provenance → Primary Datasets Used by H9

**What changed**: Distinguished raw SDC count, unfiltered US Public count, and filtered count used by pipeline.

**Before**:
```
| **SDC M&A** | `inputs/SDC/sdc-ma-merged.parquet` | `takeover_indicator.py` | `Target 6-digit CUSIP` | 142,457 | 8,784 US Public | M&A transactions |
```

**After**:
```
| **SDC M&A** | `inputs/SDC/sdc-ma-merged.parquet` | `takeover_indicator.py` | `Target 6-digit CUSIP` | 142,457 raw | 5,820 filtered (8,784 US Public unfiltered) | M&A transactions — counts: raw SDC, US Public unfiltered, filtered (2002-2018, Completed/Withdrawn/Pending) |
```

---

## Edit D — Duration Column Statement

**Status**: No change required. The provenance correctly describes duration as computed (`stop - start`) rather than a materialized column. Variable dictionary does not list a `duration` variable. The "Duration Construction" field at line 68 correctly describes computation, not storage.

---

# Task 3 — New Open Issue Added

**Issue Title**: Issue 8: Cause-Specific Event Coding Bug (OPEN, CRITICAL)

**Where Inserted**: Section J. Known Issues / Ambiguities, after Issue 7

**Final Status Label**: OPEN

**Final Severity Label**: CRITICAL

**Content Summary**:
- Documents the bug at `run_h9_takeover_hazards.py:250-251`
- Shows incorrect vs correct implementation
- Provides evidence of 8-9x inflation in event counts
- States cause-specific model outputs are unreliable until fixed
- Clarifies all-bids model is NOT affected

**Warning Note Added**: In Section F (Variable Dictionary), immediately after the cause-specific event variable definitions, a warning box directs readers to Issue 8 and states cause-specific outputs should not be treated as reliable.

---

# Task 4 — Status Language Cleanup

## Issue 7 — Escalated Severity

**Before**:
```
### Issue 7: LaTeX Table Generation Broken for Residual Variants (OPEN)
```

**After**:
```
### Issue 7: LaTeX Table Generation Broken for Residual Variants (OPEN, HIGH)

**Severity**: HIGH — blocks publication-ready output for residual variants
```

**Impact section expanded** to explicitly state:
- "6 of 9 models (all residual variants) have results that cannot be presented correctly"

## Other Issue Status Language

All other issues were reviewed:
- Issue 1: Status corrected from false claim to truthful documentation
- Issue 2: INVESTIGATED — status language is consistent with findings
- Issue 3: VERIFIED — status language is consistent
- Issue 4: VERIFIED — status language is consistent
- Issue 5: VERIFIED — status language is consistent
- Issue 6: RESOLVED — status language is consistent with fix applied

---

# Task 5 — Self-Check Results

| # | Check | Result |
|---|-------|--------|
| 1 | Does H9.md still say or imply "only CEO variant remains"? | **PASS** — No matches found |
| 2 | Does it still contain stale 27,787 language? | **PASS** — Only in Change Log (historical record) |
| 3 | Does it now clearly distinguish raw/unfiltered/filtered SDC counts? | **PASS** — Line 196 shows clear distinction |
| 4 | Does it now document cause-specific event-coding bug as OPEN? | **PASS** — Issue 8 is OPEN, CRITICAL |
| 5 | Does it clearly warn that cause-specific outputs are unreliable? | **PASS** — Warning in Variable Dictionary + Issue 8 |
| 6 | Does it keep Issue 7 open and clearly described? | **PASS** — Issue 7 is OPEN, HIGH |
| 7 | Does it accidentally claim code was fixed? | **PASS** — Line 783 states "NOT YET FIXED" |
| 8 | Did you edit any file other than H9.md? | **PASS** — Only H9.md edited |

---

# Task 6 — Final Result

**Edited File Path**: `docs/provenance/H9.md`

**Total Number of Edits Made**: 8
1. Updated Stage 5 description (3 models × 3 variants)
2. Updated SDC count presentation in data provenance table
3. Updated raw input file verification section
4. Updated verification commands section
5. Updated panel verification section
6. Updated survival diagnostics section
7. Fixed Issue 1 false claim and added truthful variant documentation
8. Added Issue 8 (cause-specific event coding bug) with warning

**Confirmation**: No other files were changed.

## What Should Happen Next

1. **Fix cause-specific event coding bug** — Implement the correct code at `run_h9_takeover_hazards.py:250-251` as documented in Issue 8

2. **Rerun Stage 4** — After fixing the bug, execute `python -m f1d.econometric.run_h9_takeover_hazards` to generate valid cause-specific model results

3. **Fix LaTeX table generation** — Implement the table structure fix documented in Issue 7 to properly present all 9 models

---

**Pass Completed**: 2026-03-11
