File: CLAUDE_H9_FINAL_PASS_06.md
Scope: Final H9 implementation + provenance completion
Edits made: H9 files only
Model/code changes made: Yes
Status: Complete

# H9 Final Completion — Pass 06

This pass converts H9 from firm-year intervals to call-to-call intervals and rewrites the provenance document into the clean 10-section canonical structure. It is the FINAL H9 pass.

# Task 1 — Final Gap Lock

## Current State Summary (before Pass 06)

H9 used **firm-year** counting-process intervals:
- `start`/`stop` were integer years (e.g., 2001/2002)
- One row per firm-year at risk
- 27,773 rows, 25 columns
- Covariates aggregated to firm-year (mean for linguistic, last for financial)

The Pass 05 edits were already applied:
- Compustat-only controls (no CRSP/IBES)
- Sparse (5) and expanded (8) control blocks
- 18 models total (3 families x 3 event types x 2 control blocks)
- Cause-specific event coding correct from Pass 03

## Final Target Summary

H9 must use **call-to-call** counting-process intervals:
- `start` = call date (days since 2000-01-01)
- `stop` = min(next call date, takeover date, censor date)
- One row per call-based risk interval
- Covariates measured at the call that opens the interval
- No aggregation to firm-year

## Precise Remaining Gap List

1. **Panel interval architecture**: firm-year → call-to-call (MAJOR)
2. **Aggregation function**: `aggregate_to_firm_year()` must be removed
3. **Counting-process builder**: `build_counting_process_panel()` must be replaced with call-to-call logic
4. **ClarityCEO merge point**: currently merged after firm-year aggregation → must merge at call level
5. **Runner wording**: "firm-year" labels → "call-to-call"
6. **Provenance document**: hybrid structure → clean 10-section format

## Evidence

- `build_h9_takeover_panel.py` line 251: `aggregate_to_firm_year()` function
- `build_h9_takeover_panel.py` line 314: `build_counting_process_panel()` uses integer years
- Current panel `start`/`stop` range: 2001-2018 (integer years)
- Manifest `start_date` column: datetime64[ns] with actual call timestamps
- SDC `Date Announced`: datetime64[ns] with actual takeover dates

## Explicit Answers

1. **Is H9 still firm-year in current code?** YES (before this pass)
2. **Can call-to-call intervals be built with existing repo inputs?** YES — manifest has `start_date` (call dates as datetime64), SDC has `Date Announced` (takeover dates as datetime64)
3. **Does Manager clarity score exist in repo-accessible artifacts?** NO — verified. Only ClarityCEO exists as a fixed-effect score. Manager variants are available only as residuals (Manager_Clarity_Residual).

# Task 2 — Call-to-Call Panel Implementation

## Files Edited

- `src/f1d/variables/build_h9_takeover_panel.py` — complete rewrite of interval construction

## Changes Made

### Removed
- `aggregate_to_firm_year()` function (lines 251-311) — no longer needed
- `build_counting_process_panel()` function (lines 314-491) — replaced by call-to-call logic

### Added
- `build_call_to_call_panel()` function — new call-to-call interval constructor
- `REFERENCE_DATE = pd.Timestamp("2000-01-01")` module-level constant

### New Interval Definition

```python
# For each call in the at-risk set:
start = (call_date - REFERENCE_DATE).dt.days      # days since 2000-01-01
stop  = (stop_date - REFERENCE_DATE).dt.days       # same units

# where stop_date = min(next_call_date, takeover_date, censor_date)
# and censor_date = 2018-12-31
```

### How Next-Call Dates Were Constructed

```python
df = df.sort_values(["gvkey", "call_date"]).reset_index(drop=True)
df["next_call_date"] = df.groupby("gvkey")["call_date"].shift(-1)
```

For the last call of each firm, `next_call_date` is NaN → replaced by `censor_date` (2018-12-31).

### How Takeover Dates Were Aligned

1. Merge firm-level takeover data (gvkey → Takeover, Takeover_Type, Takeover_Date) onto call panel
2. Remove calls on or after takeover date (not at risk): 4,890 calls removed
3. For remaining calls, check if takeover falls in interval `(call_date, stop_date]`
4. If yes: truncate `stop_date` to `Takeover_Date`, set `Takeover = 1`
5. Each firm has at most 1 event row (validated)

### How Compustat Values Were As-Of Matched

Compustat builders (SizeBuilder, BMBuilder, etc.) already match the most recent fiscal year to each call date at the call level. No change needed — values flow directly from `build_call_panel()`.

### Final Panel

- **Rows:** 107,644 call-to-call intervals
- **Columns:** 29
- **Firms:** 2,410
- **Event firms:** 671
- **Duration:** median 91 days, mean 97 days, min 1, max 5,550
- **Event breakdown:** Friendly 554, Uninvited 80, Unknown 37

### ClarityCEO Merge Change

Previously merged after firm-year aggregation. Now merged at call level before interval construction:

```python
call_panel = call_panel.merge(
    ceo_clarity[["ceo_id", "sample", "ClarityCEO"]],
    on=["ceo_id", "sample"],
    how="left",
)
```

Coverage: 64,217/107,644 intervals (59.7%) have ClarityCEO.

# Task 3 — Runner and Model Menu Update

## Files Edited

- `src/f1d/econometric/run_h9_takeover_hazards.py` — wording and docstring updates only

## Changes

1. Docstring: updated survival construction section to describe call-to-call intervals
2. `load_panel()`: "firm-year intervals" → "call-to-call intervals", added duration stats print
3. `prepare_main_sample()`: "firm-year rows" → "call-to-call intervals"
4. `run_cox_tv()` docstring: updated to describe call-to-call intervals
5. LaTeX table note: added "Intervals are call-to-call (days since 2000-01-01)"
6. Comment updates: "B7 fix" references → call-to-call descriptions
7. Docstring: explicitly notes Manager clarity score does NOT exist

No structural changes to the runner — `CoxTimeVaryingFitter` already uses `start`/`stop` columns in counting-process format. The change from years to days is transparent to the estimator.

## Final Model Menu Actually Run

### Primary Style (ClarityCEO) — Sparse
1. Cox PH All — ClarityCEO + sparse controls → 51,627 intervals, 308 events
2. Cox CS Uninvited — ClarityCEO + sparse → 51,627 intervals, 40 events
3. Cox CS Friendly — ClarityCEO + sparse → 51,627 intervals, 251 events

### Secondary Residual (CEO_Clarity_Residual) — Sparse
4. Cox PH All — CEO_Residual + sparse → 40,310 intervals, 276 events
5. Cox CS Uninvited — CEO_Residual + sparse → 40,310 intervals, 36 events
6. Cox CS Friendly — CEO_Residual + sparse → 40,310 intervals, 225 events

### Secondary Residual (Manager_Clarity_Residual) — Sparse
7. Cox PH All — Manager_Residual + sparse → 54,981 intervals, 355 events
8. Cox CS Uninvited — Manager_Residual + sparse → 54,981 intervals, 46 events
9. Cox CS Friendly — Manager_Residual + sparse → 54,981 intervals, 290 events

### Expanded Controls (all families)
10-18. Same 9 combinations with expanded controls (+ SalesGrowth, Intangibility, AssetGrowth)

**Manager clarity family included?** NO — ClarityManager does not exist in the repo. Verified by searching all Python files, parquet outputs, and config files. Only Manager_Clarity_Residual (secondary) is available.

# Task 4 — Final Rerun Log

## Stage 3 — Panel Build

```
python -m f1d.variables.build_h9_takeover_panel
```

- **Status:** SUCCESS
- **Duration:** 73.1 seconds
- **Output:** `outputs/variables/takeover/2026-03-11_204327/`
- **Panel:** 107,644 rows x 29 columns
- **Key files:**
  - `takeover_panel.parquet` (107,644 intervals)
  - `summary_stats.csv` (16 variables)
  - `report_step3_takeover.md`
  - `run_manifest.json`

## Stage 4 — Hazard Models

```
python -m f1d.econometric.run_h9_takeover_hazards
```

- **Status:** SUCCESS
- **Duration:** 12.5 seconds
- **Output:** `outputs/econometric/takeover/2026-03-11_204501/`
- **Models estimated:** 18 (9 sparse + 9 expanded)
- **Hazard ratio rows:** 135
- **Key files:**
  - `hazard_ratios.csv` (135 rows)
  - `model_diagnostics.csv` (18 rows)
  - `takeover_table.tex`
  - `summary_stats.csv`, `summary_stats.tex`
  - `report_step4_takeover.md`
  - `sample_attrition.csv`, `sample_attrition.tex`
  - `run_manifest.json`
  - `cox_ph_all.txt`, `cox_cs_uninvited.txt`, `cox_cs_friendly.txt`
  - `cox_ph_all_expanded.txt`, `cox_cs_uninvited_expanded.txt`, `cox_cs_friendly_expanded.txt`

# Task 5 — Provenance Rewrite Applied

## Confirmation

`docs/provenance/H9.md` was completely rewritten into the 10-section canonical structure:

I. Suite Identity and Status
II. Research Question and Current Hypotheses
III. Canonical Inputs and Upstream Dependencies
IV. Sample Construction and Filters
V. Variable Dictionary
VI. Model Specification Register
VII. Output Artifacts and Active Run Paths
VIII. Verification Summary
IX. Known Limitations / Open Issues
X. Change Log

## Final Status

Suite status: **FINAL (Pass 06)**

## Biggest Changes in Rewritten Provenance

1. **Interval description:** Changed from firm-year to call-to-call throughout. All sections now describe call-to-call intervals with days since 2000-01-01.
2. **Structure:** Replaced hybrid issue-log/diary structure with clean 10-section format. Removed all stale command snippets, broken assert blocks, and contradictory legacy wording.
3. **Manager clarity:** Explicitly documented that ClarityManager does NOT exist. Separated primary style (CEO only) from secondary residual (CEO + Manager).
4. **Active run paths:** Updated to Pass 06 output paths.
5. **Verification table:** Added 12-row pass/fail verification summary.

## Open Issues Remaining

1. ClarityManager does not exist in the repo (documented, not fixable without upstream changes)
2. LaTeX table formatting has known alignment issues (CSV is authoritative)
3. No year/industry stratification (potential robustness extension)

# Task 6 — Final Verification and Result

## A. 12-Row Verification Table

| # | Check | Result |
|---|-------|--------|
| 1 | H9 uses call-to-call intervals | PASS — start/stop are days since 2000-01-01, derived from `start_date` (actual call timestamps) |
| 2 | Interval start is call date | PASS — `start = (call_date - 2000-01-01).days` where `call_date = pd.to_datetime(start_date).dt.normalize()` |
| 3 | Interval stop is next call / event / censoring | PASS — `stop = min(next_call_date, Takeover_Date, 2018-12-31)` converted to days |
| 4 | No negative durations | PASS — all 107,644 intervals have `duration > 0`; 434 zero-duration intervals were removed |
| 5 | No duplicated event assignment across intervals | PASS — max events per firm = 1 (validated by assertion in `build_call_to_call_panel`) |
| 6 | All-bids definition correct | PASS — 671 event firms; Takeover=1 only in the interval containing the bid |
| 7 | Uninvited definition correct | PASS — 80 events; Takeover_Uninvited=1 only when Takeover=1 AND Takeover_Type='Uninvited' |
| 8 | Friendly definition correct | PASS — 554 events; Takeover_Friendly=1 only when Takeover=1 AND Takeover_Type='Friendly' |
| 9 | Unknown-type handling correct | PASS — 37 Unknown events; censored in both cause-specific models (Uninvited=0, Friendly=0) |
| 10 | No CRSP/IBES controls remain | PASS — no StockRet, MarketRet, SurpDec, EPS_Growth in panel or code |
| 11 | Provenance uses clean 10-section structure | PASS — H9.md rewritten with sections I-X |
| 12 | Final outputs and provenance describe the same implementation | PASS — both describe call-to-call intervals, Compustat-only controls, 18 models, same run paths |

## B. Final Verdict

**FINAL COMPLETE WITH ONE KNOWN LIMITATION**

The known limitation is: Manager clarity score (ClarityManager) does not exist in the repo. Only ClarityCEO is available as a primary style construct. This is not fixable without upstream changes to produce a Manager fixed-effect clarity score.

## C. Files Edited

| File | Change |
|------|--------|
| `src/f1d/variables/build_h9_takeover_panel.py` | Replaced firm-year aggregation with call-to-call interval construction |
| `src/f1d/econometric/run_h9_takeover_hazards.py` | Updated wording from firm-year to call-to-call |
| `docs/provenance/H9.md` | Rewritten to clean 10-section canonical structure |

## D. Final Output Run Paths

- **Panel:** `outputs/variables/takeover/2026-03-11_204327/`
- **Hazards:** `outputs/econometric/takeover/2026-03-11_204501/`

## E. What Remains

Nothing remains for the H9 implementation scope defined in this pass. The suite is architecturally complete:
- Call-to-call intervals: implemented and verified
- Compustat-only controls: intact from Pass 05
- Cause-specific event coding: intact from Pass 03
- Provenance: rewritten to clean canonical format
- Manager clarity score: documented as absent

The only potential extensions are robustness checks (year/industry stratification) which are outside the scope of this pass.
