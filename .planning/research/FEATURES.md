# Features: v3.0 Codebase Cleanup & Optimization

**Project:** F1D Data Processing Pipeline
**Research Date:** 2026-02-10
**Milestone:** v3.0 - Codebase Cleanup & Optimization

## Executive Summary

This milestone focuses on codebase health, not new features. The pipeline works (all hypotheses tested, null results validated), but accumulated technical debt makes maintenance difficult. The cleanup will improve maintainability, performance, and documentation while preserving all existing functionality and reproducibility.

---

## Table Stakes (Must-Have)

### 1. Bug Fixes

| Bug | Impact | Fix Approach |
|-----|--------|--------------|
| **H7-H8 Data Truncation** | H8 silently uses 2002-2004 only (12K obs vs 39K) | Calculate Volatility from CRSP daily within H7 script |
| **Empty DataFrame Returns** | Error messages lost, bugs hidden | Raise exceptions instead of returning empty containers |
| **Division by Zero Guards** | Masks underlying data quality issues | Log warnings and raise informative exceptions |

### 2. Code Organization

| Feature | Description | Priority |
|---------|-------------|----------|
| **Archive backup files** | Move `*-legacy.py`, `*.bak`, `*_old.py` to `.___archive/` | HIGH |
| **Clarify V1/V2/V3 structure** | Document purpose of each financial directory | HIGH |
| **Monolithic utility split** | Break `observability_utils.py` (4,652 lines) into focused modules | MEDIUM |
| **Import path updates** | Update imports after module splitting | MEDIUM |

### 3. Documentation

| Feature | Description | Priority |
|---------|-------------|----------|
| **Repo-level README** | Comprehensive project overview for academic reviewers | HIGH |
| **Script-level docstrings** | Each script has header with purpose, inputs, outputs | HIGH |
| **Directory READMEs** | Each major directory has explanation of its contents | MEDIUM |
| **Variable reference** | Complete catalog of all constructed variables | MEDIUM |

### 4. Performance Optimization

| Feature | Description | Priority |
|---------|-------------|----------|
| **Vectorize `.apply(lambda)`** | Replace with vectorized operations (10-100x speedup) | MEDIUM |
| **Eliminate `.iterrows()`** | Use vectorized alternatives (50-1000x speedup) | MEDIUM |
| **Optimize `.groupby().apply()`** | Use `.groupby().agg()` with built-ins (5-50x speedup) | MEDIUM |
| **Reduce `pd.concat()` calls** | Pre-allocate or use list-of-dicts pattern | LOW |

### 5. Testing & Validation

| Feature | Description | Priority |
|---------|-------------|----------|
| **Regression test for H7-H8 bug** | Prevent recurrence of data truncation | HIGH |
| **Integration tests** | Multi-step pipeline validation | MEDIUM |
| **Coverage increase** | Target 70% on shared utilities | MEDIUM |
| **Pandera schemas** | Validate parquet schemas at key points | LOW |

---

## Differentiators (Exemplary Practices)

### 1. Reproducibility Guarantees

| Feature | Description | Value |
|---------|-------------|-------|
| **Bitwise-identical outputs** | Verify cleanup doesn't change results | Academic confidence |
| **Automated regression tests** | Catch result changes before commits | Continuous validation |
| **Determinism assertions** | Verify seed/threading configuration | Reproducibility proof |

### 2. Developer Experience

| Feature | Description | Value |
|---------|-------------|-------|
| **Ruff integration** | One-command formatting and linting | Consistent code style |
| **Type hints on utilities** | Mypy validation on shared modules | Catch errors early |
| **Profiler integration** | py-spy for on-demand profiling | Performance insights |

### 3. Documentation Excellence

| Feature | Description | Value |
|---------|-------------|-------|
| **Thesis-ready README** | Publication-quality project documentation | Academic acceptance |
| **Per-script headers** | Standardized docstring format | Easy navigation |
| **Variable catalog** | Complete reference for all constructs | Reviewer clarity |

---

## Anti-Features (Deliberately Excluded)

| Feature | Reason to Exclude |
|---------|-------------------|
| **Polars migration** | Pandas 3.0 + vectorization sufficient; over-engineering for cleanup |
| **Docker containerization** | Unnecessary for single-researcher project; dependency pinning works |
| **Great Expectations** | Pandera is lighter; GE is production overkill |
| **Sphinx/MkDocs documentation** | Markdown READMEs sufficient for academic review |
| **Pre-commit hooks** | Adds git complexity for single-user project |
| **Dask/Modin parallelization** | Datasets fit in memory; unnecessary complexity |
| **Feature flag system** | V1/V2/V3 have legitimate differences; don't over-abstract |

---

## Feature Categories by Work Type

### Critical Fixes (Blockers)
- H7-H8 data truncation bug
- Empty DataFrame returns pattern
- Backup file cleanup

### Code Quality (Maintainability)
- Monolithic utility splitting
- V1/V2/V3 structure documentation
- Import path cleanup

### Performance (Speed)
- Vectorization of `.apply(lambda)`
- Elimination of `.iterrows()`
- Optimization of `.groupby().apply()`

### Documentation (Clarity)
- Repo-level README
- Script-level docstrings
- Directory READMEs
- Variable reference catalog

### Testing (Reliability)
- Regression tests for critical bugs
- Integration tests for workflows
- Coverage targets

---

## Complexity Assessment

| Work Type | Complexity | Reason |
|-----------|------------|--------|
| Bug fixes | LOW | Well-understood issues, clear fixes |
| Backup cleanup | LOW | Simple file moves |
| V1/V2/V3 documentation | LOW | Writing only, no code changes |
| Utility splitting | MEDIUM | Requires care for backward compatibility |
| Performance optimization | MEDIUM | Requires profiling and testing |
| Script docstrings | MEDIUM | 61 scripts to document |
| Testing expansion | MEDIUM | Need to design good tests |
| Variable catalog | HIGH | Many variables to catalog across scripts |

---

## Success Criteria

A feature is "complete" when:

1. **Bug fixes**: Regression test passes, all existing tests pass
2. **Code organization**: Files moved, imports updated, all scripts run
3. **Documentation**: READMEs written and reviewed for clarity
4. **Performance**: Before/after benchmarks show improvement
5. **Testing**: Tests pass, coverage meets target

---

*Features research: 2026-02-10*
