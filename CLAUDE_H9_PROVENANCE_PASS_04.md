File: CLAUDE_H9_PROVENANCE_PASS_04.md
Scope: H9 provenance sync after Pass 03
Edits made: H9.md only
Model/code changes made: None
Status: Complete

# H9 Provenance Sync — Pass 04

# Task 1 — Verified Pass 03 Artifacts

## Actual Verified Run Path

```
outputs/econometric/takeover/2026-03-11_173952/
```

## Files Found in Directory

- `cox_ph_all.txt`
- `cox_cs_uninvited.txt`
- `cox_cs_friendly.txt`
- `hazard_ratios.csv` (90 rows)
- `model_diagnostics.csv` (9 rows)
- `takeover_table.tex`
- `report_step4_takeover.md`
- `run_log.txt`
- `run_manifest.json`
- `summary_stats.csv`
- `summary_stats.tex`
- `sample_attrition.csv`
- `sample_attrition.tex`

## Exact Evidence Snippets for Corrected Counts

From `run_log.txt` (lines 19-24):
```
  Uninvited events: 76
  Friendly events:  469
  WARNING: 26 takeover event(s) have neither Uninvited nor Friendly type -- treated as censored in cause-specific models (correct for competing risks). Type breakdown:
Takeover_Type
Unknown    26
```

From `model_diagnostics.csv`:
- All-bids event firms (unchanged): 349 (CEO), 351 (CEO_Residual), 439 (Manager_Residual)
- Uninvited event firms: 39 (CEO), 41 (CEO_Residual), 50 (Manager_Residual)
- Friendly event firms: 291 (CEO), 291 (CEO_Residual), 367 (Manager_Residual)

## Path Ambiguity Resolution

Prior markdown summaries contained inconsistent references:
- `CLAUDE_H9_CODEFIX_PASS_03.md` referenced `2026-03-11_173952` (correct)
- Line 148 of `CLAUDE_H9_PROVENANCE_PASS_02.md` referenced `2026-03-11_173954` (incorrect)

**Resolution**: Only `2026-03-11_173952` exists in the filesystem. The `173954` reference was a typo in the prior pass documentation. H9.md now references only the correct path.

---

# Task 2 — Issue 8 Update Applied

## Section Edited

`docs/provenance/H9.md` → Section J. Known Issues / Ambiguities → Issue 8 (lines 749-786)

## Before Snippet

```markdown
### Issue 8: Cause-Specific Event Coding Bug (OPEN, CRITICAL)

**Severity**: CRITICAL — invalidates cause-specific model results

**Verification Status**: OPEN. Bug identified but NOT YET FIXED. Do not cite cause-specific model results until this is resolved.
```

## After Snippet

```markdown
### Issue 8: Cause-Specific Event Coding Bug (RESOLVED, was CRITICAL)

**Severity**: Was CRITICAL — cause-specific model results were invalidated

**Fix Applied**:
- **Date**: 2026-03-11 (Code Fix Pass 03)
- **Fix**: Added `df[EVENT_ALL_COL] == 1` condition to both cause-specific event indicators
- **Rerun Path**: `outputs/econometric/takeover/2026-03-11_173952/`
- **Post-Fix Counts**: Uninvited=76, Friendly=469, Unknown=26 (correctly censored in cause-specific models)
- **All-bids model**: Unaffected — event counts unchanged (349/351/439 event firms)

**Verification Status**: RESOLVED. Bug fixed in Pass 03, rerun completed, event counts verified.
```

## Final Status Label

RESOLVED

## Final Date and Rerun Path

- Date: 2026-03-11
- Rerun Path: `outputs/econometric/takeover/2026-03-11_173952/`

---

# Task 3 — Result Language Sync

## Warning Box Updated (Line 356)

**Before**:
```markdown
> **⚠️ WARNING (Issue 8 — OPEN, CRITICAL)**: The cause-specific event variables ... **Cause-specific model outputs should NOT be treated as reliable until this is fixed.** See Issue 8 for details.
```

**After**:
```markdown
> **✓ RESOLVED (Issue 8 — Pass 03)**: The cause-specific event variables ... were previously implemented incorrectly ... This bug was fixed on 2026-03-11 (Pass 03). Post-fix rerun path: `outputs/econometric/takeover/2026-03-11_173952/`. Cause-specific event counts are now correct: Uninvited=76, Friendly=469, Unknown=26 (correctly censored). See Issue 8 for historical details.
```

## Regression Run Reference Updated (Line 794)

**Before**: `**Regression Run**: 2026-03-10_175654`

**After**: `**Regression Run**: 2026-03-11_173952`

## Change Log Updated (Line 797)

Added new entry documenting this provenance sync pass.

---

# Task 4 — Open Issues Preserved

## Issue 7 Status

Issue 7 (LaTeX Table Generation Broken for Residual Variants) remains **OPEN, HIGH**.

Location: Lines 725-747 of H9.md

The header explicitly states:
```markdown
### Issue 7: LaTeX Table Generation Broken for Residual Variants (OPEN, HIGH)
```

The verification status explicitly states:
```markdown
**Verification Status**: OPEN. Requires fix to LaTeX table generation function.
```

## No Overclaiming

H9.md does NOT imply:
- The whole H9 suite is fully clean
- All reporting artifacts are correct
- All documentation is synchronized outside H9.md
- No further work is needed

The Change Log explicitly states: "Issue 7 remains OPEN."

---

# Task 5 — Self-Check Results

| # | Check | Result |
|---|-------|--------|
| 1 | Does Issue 8 now show RESOLVED? | **PASS** — Line 749: `Issue 8: Cause-Specific Event Coding Bug (RESOLVED, was CRITICAL)` |
| 2 | Does it still accurately describe the historical bug? | **PASS** — "Historical Description" section preserved, buggy code shown |
| 3 | Does it include the verified rerun path? | **PASS** — `2026-03-11_173952` referenced in Issue 8 and metadata |
| 4 | Does it avoid the 173952/173954 ambiguity? | **PASS** — Only `173952` appears in H9.md; no `173954` references |
| 5 | Does it keep Issue 7 OPEN? | **PASS** — Line 725: `Issue 7: LaTeX Table Generation Broken for Residual Variants (OPEN, HIGH)` |
| 6 | Does it avoid claiming any new code fixes beyond cause-specific event bug? | **PASS** — Only Issue 8 changed from OPEN to RESOLVED |
| 7 | Does it avoid touching report_step4 or LaTeX outputs? | **PASS** — Only H9.md edited |
| 8 | Did you edit any file other than docs/provenance/H9.md? | **PASS** — Only H9.md edited |

---

# Task 6 — Final Result

## Edited File Path

`docs/provenance/H9.md`

## Actual Verified Rerun Path

`outputs/econometric/takeover/2026-03-11_173952/`

## Total Number of Provenance Edits Made

4 edits:
1. Warning box in Variable Dictionary (line 356) — updated from OPEN warning to RESOLVED note
2. Issue 8 section (lines 749-786) — changed status from OPEN to RESOLVED, added fix details
3. Regression Run metadata (line 794) — updated path from `2026-03-10_175654` to `2026-03-11_173952`
4. Change Log (line 797) — added entry for this provenance sync pass

## Confirmation: No Code Files Changed

Confirmed. Only `docs/provenance/H9.md` was edited. No `.py` files, `.tex` generators, `report_step*.md`, CSVs, or output files were modified.

## What Should Happen Next

1. **LaTeX table repair** — Issue 7 remains OPEN; `make_cox_hazard_table` needs refactoring for 9-model structure
2. **Output/report sync** — `report_step4_takeover.md` in `2026-03-11_173952/` should be reviewed for consistency with post-fix results
3. **Thesis-facing interpretation** — Updated cause-specific hazard ratios should be documented for thesis use

---

**Pass Completed**: 2026-03-11
