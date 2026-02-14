# Phase 77 Context

**Created:** 2026-02-14
**Source:** /gsd:discuss-phase 77

---

## User Decisions (LOCKED)

### Scope: ALL CONCERNS + ALL SCRIPTS

**User directive:** "ALL CONCERNS!" - Phase 77 will address every item in CONCERNS.md and verify ALL scripts execute on dry-run.

- **ALL concerns in CONCERNS.md** - not just high priority
- **Survival Analysis** - Implement full lifelines integration (run_cox_ph and run_fine_gray)
- **Test Coverage** - Add tests for hypothesis scripts
- **Script Verification** - ALL scripts must run and verify on dry-run (not only hypothesis tests, but sample step (1), text step (2), financials step (3), and hypothesis test stage (4))

---

## Critical Gap Discovered

### Stage 2 Text Scripts NOT Migrated

**Finding during /gsd:discuss-phase 77:**

`src/f1d/text/` directory is EMPTY - Stage 2 text processing scripts were NOT migrated in v6.1.

**Stage 2 scripts in `2_Scripts/2_Text/` (still use legacy imports):**
1. `2.1_TokenizeAndCount.py` - Uses `sys.path.insert()` and `from shared.*`
2. `2.2_ConstructVariables.py` - Likely same pattern
3. `2.3_Report.py` - Likely same pattern
4. `2.3_VerifyStep2.py` - Likely same pattern

**User directive:** "this is a gap that you just found! ALL scripts must have been migrated!"

**Phase 77 must include:**
1. Migrate Stage 2 text scripts to `src/f1d/text/`
2. Update imports to `f1d.shared.*`
3. Remove `sys.path.insert()` calls
4. Verify mypy passes

---

## Script Dependency Confirmation

**Scripts must run sequentially** due to data flow dependencies:

### Stage 1 (Sample):
- 1.1 → 1.2 → 1.3 (can parallel with 1.1-1.2) → 1.4

### Stage 2 (Text):
- 2.1, 2.2 (can parallel)

### Stage 3 (Financials V2):
- All require Stage 1.4 and Stage 2.2 outputs
- H2-H9 scripts can run in parallel after H1

### Stage 4 (Econometric/Regressions):
- All require Stage 3.x and Stage 2.2 outputs
- Most can run in parallel once inputs are ready

---

## Investigation Findings

### 1. Dynamic Module Imports (importlib.util)

**Recommendation:** Rename 1.5_Utils.py to `sample_utils.py`, move to `src/f1d/shared/`

**Rationale:**
- `1.5_Utils.py` is only 96 lines with 2 simple functions
- Used by 9 files in `src/f1d/sample/`
- Enables proper IDE autocomplete
- Removes 10+ `# type: ignore` comments
- Eliminates mypy errors

### 2. NotImplemented Survival Analysis

**Location:** `src/f1d/econometric/v1/4.3_TakeoverHazards.py:115-131`

**Functions:** `run_cox_ph()` and `run_fine_gray()` raise `NotImplementedError`

**User directive:** "ALL CONCERNS!" - Implement full lifelines integration

---

## Claude's Discretion

The following areas are open for implementation decisions:

1. **Parallel execution strategy:** How to parallelize independent scripts within waves
2. **Test coverage approach:** Specific test patterns for hypothesis scripts
3. **Large file splitting:** Exact boundaries for splitting 1000+ line files
4. **Type ignore resolution:** Priority order for fixing 40+ type ignores
5. **Exception handling:** Specific logging patterns for bare `pass` blocks

---

## Deferred Ideas

None - all concerns in CONCERNS.md are in scope.
