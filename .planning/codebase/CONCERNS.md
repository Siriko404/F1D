# Codebase Concerns

**Analysis Date:** 2026-01-22

## Tech Debt

**Manual Version Control:**
- Issue: Repository contains large binary archives and backup directories instead of using git history.
- Files: 
  - `2_Scripts_20251212.rar`
  - `2_Scripts_20261201.rar`
  - `BACKUP_20260114_191340/`
  - `2_Scripts/ARCHIVE_OLD/`
- Impact: Bloats repo size, confuses current state, makes diffing impossible.
- Fix approach: Remove binary archives, trust git for history, delete `BACKUP_` folders.

**Dynamic Import Hacks:**
- Issue: Scripts use `importlib` to load sibling utilities because the directory is not a proper Python package.
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py`
- Impact: Fragile; breaks static analysis and IDE autocompletion; fails if file structure changes slightly.
- Fix approach: Structure `2_Scripts` as a proper python package with `__init__.py` or add root to `PYTHONPATH`.

**Abandoned Code Retention:**
- Issue: `2_Scripts/ARCHIVE_OLD` contains many scripts and binaries that are likely obsolete but still present.
- Files: `2_Scripts/ARCHIVE_OLD/*`
- Impact: Confuses developers about which scripts are active.
- Fix approach: Delete the directory. Git history preserves it if needed.

## Known Bugs

**Type Mismatch in Tokenization:**
- Symptoms: Static analysis reports accessing `.str` and `.to_parquet` on `ndarray` objects.
- Files: `2_Scripts/2_Text/2.1_TokenizeAndCount.py`
- Trigger: Execution of text processing step.
- Workaround: Ensure variable is cast to pandas Series/DataFrame before access.

**Configuration/Data Mismatch Risk:**
- Symptoms: Config defines `speaker_data_pattern` as yearly files, but inputs seem to include quarterly splits (`CRSP_DSF`).
- Files: `config/project.yaml` vs `1_Inputs/CRSP_DSF/*`
- Trigger: Running scripts expecting yearly aggregation on quarterly data.
- Workaround: Scripts currently might manually aggregate, but this logic should be centralized.

## Security Considerations

**Binary Executables in Source:**
- Risk: Executable files committed to repository.
- Files: `2_Scripts/ARCHIVE_OLD/2.2v2b_ProcessManagerDocs_debug.exe`
- Current mitigation: None.
- Recommendations: Delete immediately. Source code should be compiled, not committed as binary.

## Performance Bottlenecks

**Input File Cardinality:**
- Problem: `1_Inputs/CRSP_DSF` contains thousands of small Parquet files (quarterly).
- Files: `1_Inputs/CRSP_DSF/*`
- Cause: High I/O overhead when reading years of data across hundreds of files.
- Improvement path: Aggregate into yearly or multi-year Parquet files.

## Fragile Areas

**Script-Local Utilities:**
- Files: `2_Scripts/1_Sample/1.5_Utils.py` (referenced by import, assuming existence)
- Why fragile: Utility functions are co-located with scripts rather than in a shared `lib/` or `src/` directory.
- Safe modification: Move to a `shared/` directory and update imports.
- Test coverage: Unknown/Likely Zero.

## Test Coverage Gaps

**No Automated Testing:**
- What's not tested: Entire pipeline.
- Files: All.
- Risk: Regressions are undetectable without running full pipeline on large data.
- Priority: High.

## Missing Critical Features

**Dependency Management:**
- Problem: No `requirements.txt` or `pyproject.toml` detected in root (only `project.yaml` for config).
- Blocks: Reproducible environments.

---

*Concerns audit: 2026-01-22*
