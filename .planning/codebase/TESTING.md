# Testing Patterns

**Analysis Date:** 2026-01-22

## Test Framework

**Runner:**
- None detected (no `pytest`, `unittest`, `jest` configs).
- Testing relies on **Verification Scripts** and **Direct Execution**.

**Philosophy:**
- "Direct-run commands" (from `CLAUDE.md`).
- Deterministic execution allows re-running to verify outputs match.

## Test File Organization

**Location:**
- Verification scripts are co-located with implementation scripts or in `ARCHIVE`.
- Examples: `2_Scripts/2_Text/2.3_VerifyStep2.py`, `2_Scripts/ARCHIVE/verify_step1.py`.

**Naming:**
- Pattern: `X.Y_Verify*.py` or `RedTeamAudit.py`.

## Test Structure

**Verification Scripts:**
- These scripts appear to load the outputs of previous steps and perform sanity checks (e.g., checking for nulls, unmatched records, or statistical outliers).
- They act as "Integration Tests" on the data pipeline.

**Manual Validation:**
- Presence of `VALIDATION.rar` suggests manual checks or ad-hoc validation artifacts.

## Mocking

**Framework:** None.

**Policy:**
- **"Real data only"**: `CLAUDE.md` explicitly forbids mocking without approval.
- Tests (Verification) run against actual pipeline outputs, not synthetic data.

## Fixtures and Factories

**Test Data:**
- Uses the actual input data (`1_Inputs`).
- No separate "test fixtures" directory.

## Coverage

**Requirements:** None enforced.
**View Coverage:** Not applicable.

## Test Types

**Data Validation (Pipeline Testing):**
- Checks input integrity and output consistency.
- Example: `1.1_CleanMetadata.py` likely contains internal checks for duplicates.

**Regression Testing:**
- `Determinism` settings (seed, threads) in `config/project.yaml` ensure that re-running code produces bitwise-identical outputs, enabling regression testing by file comparison.

**Orchestration Testing:**
- Top-level scripts (e.g., `1.0_BuildSampleManifest.py`) verify the successful execution of substeps (return codes).

## Common Patterns

**Audit Trails:**
- Scripts generate `audit.csv` files (e.g., `unmatched_calls_audit.csv`) which serve as test artifacts to verify logic correctness.

**Report Generation:**
- Steps generate markdown reports (`report_step_XX.md`) which summarize the run, acting as a human-readable test result.
