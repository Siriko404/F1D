# Research Summary: v3.0 Codebase Cleanup & Optimization

**Project:** F1D Data Processing Pipeline
**Research Date:** 2026-02-10
**Milestone:** v3.0 - Codebase Cleanup & Optimization
**Confidence:** HIGH

## Executive Summary

This milestone addresses accumulated technical debt in the F1D research data pipeline. The pipeline is functional (all 9 hypotheses tested, null results validated) but suffers from organizational issues, performance bottlenecks, and documentation gaps. The cleanup improves maintainability, performance, and documentation while preserving **all existing functionality and bitwise-identical reproducibility**.

**Key principle:** NO active code is archived. All V1/V2/V3 versions remain functional. Cleanup focuses on removing backup file clutter, clarifying structure through documentation, and fixing known bugs.

---

## Key Findings

### Stack Additions (Minimal)

**New tools needed:**
- **Ruff** (0.9+) - Unified linter/formatter replacing Black+isort+flake8
- **mypy** (1.15+) - Static type checking for refactoring safety
- **py-spy** (0.3+) - Profiler for performance optimization
- **pandera** (0.21+) - DataFrame schema validation
- **pytest-cov** - Coverage reporting

**What NOT to add:**
- Polars (pandas 3.0 sufficient)
- Great Expectations (pandera lighter)
- Sphinx/MkDocs (markdown sufficient)
- Docker (unnecessary for single-user research)

### Architecture: Preserve, Simplify, Document

**Current structure (preserved):**
```
1_Sample -> 2_Text -> 3_Financial -> 4_Econometric

Three parallel versions (all ACTIVE):
3_Financial/ + 4_Econometric/       (V1 - Original)
3_Financial_V2/ + 4_Econometric_V2/ (V2 - H1-H8)
5_Financial_V3/ + 4_Econometric_V3/ (V3 - H9)
```

**Cleanup actions:**
1. Archive backup files only (`*-legacy.py`, `*.bak`, `*_old.py`)
2. Clarify V1/V2/V3 through README files (not renaming)
3. Split monolithic `observability_utils.py` (4,652 lines) into focused modules
4. Add comprehensive README documentation

### Critical Bugs to Fix

| Bug | Impact | Fix |
|-----|--------|-----|
| H7-H8 data truncation | H8 uses 2002-2004 only (12K vs 39K obs) | Calculate Volatility inline in H7 |
| Empty DataFrame returns | Error messages lost | Raise exceptions |
| Division by zero guards | Masks data quality issues | Log warnings, raise exceptions |

### Performance Opportunities

**Identified bottlenecks:**
- `.apply(lambda)` in tokenization → vectorize (10-100x speedup)
- `.iterrows()` in tenure mapping → vectorize (50-1000x speedup)
- `.groupby().apply()` in financials → `.groupby().agg()` (5-50x speedup)
- Excessive `pd.concat()` calls → pre-allocate or list-of-dicts

**Optimization strategy:** Profile first, target top 3 bottlenecks per script, verify identical outputs.

### Documentation Needs

**Required deliverables:**
1. **Repo-level README** - Project overview for academic reviewers
2. **Directory READMEs** - Purpose of each major folder (clarify V1/V2/V3)
3. **Script docstrings** - Header on all 61 scripts (purpose, inputs, outputs)
4. **Variable catalog** - Complete reference for all constructed variables

---

## Implications for Roadmap

### Recommended Phase Structure

**Phase 59: Bug Fixes**
- Fix H7-H8 data truncation (calculate Volatility inline)
- Fix empty DataFrame returns pattern
- Add regression tests

**Phase 60: Archive & Cleanup**
- Move `*-legacy.py`, `*.bak` to `.___archive/`
- Set up Ruff configuration
- Run code quality tools

**Phase 61: Utility Refactoring**
- Split `observability_utils.py` into submodules
- Update imports across all scripts
- Verify backward compatibility

**Phase 62: Documentation**
- Write repo-level README
- Write directory READMEs
- Write script docstrings
- Create variable catalog

**Phase 63: Performance Optimization** (Optional, lower priority)
- Profile top 5 scripts
- Vectorize targeted operations
- Verify identical outputs

**Phase 64: Validation**
- Run full pipeline end-to-end
- Verify bitwise identical outputs
- Final documentation review

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Minimal additions, all well-established tools |
| Features | HIGH | Based on direct codebase audit |
| Architecture | HIGH | Existing structure preserved, only documentation added |
| Pitfalls | HIGH | Reproducibility preservation well-understood |

**Overall confidence:** HIGH

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking reproducibility | MEDIUM | CRITICAL | Bitwise comparison tests before/after |
| Import path errors | MEDIUM | HIGH | Re-exports in __init__.py |
| Documentation becomes stale | LOW | MEDIUM | Verify docs match code |
| Performance changes results | LOW | CRITICAL | Bitwise comparison tests |
| Archive breaks references | LOW | HIGH | Check references before moving |

---

## Quality Gates

Before concluding v3.0:

1. **Reproducibility verified** - All regression outputs bitwise identical
2. **All scripts run** - No import errors or runtime failures
3. **Tests pass** - All existing tests + new regression tests
4. **Documentation complete** - READMEs, docstrings, variable catalog
5. **Code quality improved** - Ruff passes, dead code identified

---

## Sources

| Source | Type | Confidence |
|--------|------|------------|
| Codebase audit | Direct | HIGH |
| `.planning/codebase/CONCERNS.md` | Internal | HIGH |
| Stack research | Compiled | HIGH |
| Python best practices | Industry | MEDIUM |

---

*Research summary: 2026-02-10*
