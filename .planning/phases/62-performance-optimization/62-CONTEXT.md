---
phase: 62-performance-optimization
created: 2026-02-11

# Phase 62: Performance Optimization - Context

## Objective

Optimize pipeline performance across identified bottlenecks while maintaining bitwise-identical outputs.

## Background

Phase 10 (Performance Optimization) previously optimized the tokenization script (2.1_TokenizeAndCount.py) by replacing .iterrows() loops with vectorized .melt() operations, achieving ~10x speedup.

Phase 62 continues performance optimization work across the remaining pipeline scripts, targeting the high-ROI bottlenecks identified in CONCERNS.md.

## Decisions

### Locked Choices (Must Honor)

- **Reproducibility is non-negotiable**: All optimizations must produce bitwise-identical outputs (verified via df.equals())
- **No algorithm changes**: Optimizations must preserve exact logic, only improve performance
- **Incremental validation**: Each optimized script must be verified before proceeding

### Claude's Discretion (Your Freedom Areas)

- **Priority ranking**: Which scripts to optimize first based on impact vs effort
- **Optimization techniques**: Vectorization, efficient DataFrame patterns, chunking improvements
- **Scope**: May subset to highest-ROI optimizations if full pipeline is too large

### Deferred Ideas (Out of Scope)

- Parallel processing (multiprocessing) - may break single-threaded determinism
- Caching mechanisms - adds complexity, may violate reproducibility
- Algorithm changes - must preserve exact logic

## Known Bottlenecks (from CONCERNS.md)

1. **Inefficient DataFrame Operations** (High ROI)
   - Pattern: `df.loc[update_df.index, col] = update_df[col]` for bulk updates
   - Files: `1.2_LinkEntities.py`, `3.2_H2Variables.py`
   - Fix: Use `pd.merge()` with `how='left'` or `df.update()`

2. **Excessive pd.concat() Calls** (Medium ROI)
   - Problem: 60+ instances create memory pressure
   - Cause: Incremental DataFrame building pattern
   - Fix: Pre-allocate or use list-of-dicts then single concat

3. **Duplicate Computations in Rolling Windows** (High ROI)
   - Problem: `3.2_H2Variables.py` computes rolling windows per-firm without vectorization
   - Fix: Use pandas `.groupby().rolling()` with `transform()`

4. **Chunked Processing Without Proper Consolidation** (Low-Medium ROI)
   - Problem: Fixed chunk_size=1000 may not be optimal
   - Fix: Make configurable via project.yaml and benchmark

## Dependencies

- Phase 60 (Code Organization) - Complete
- Phase 61 (Documentation) - Complete

## Success Criteria

- [ ] Optimizations produce bitwise-identical outputs
- [ ] Performance improvement measured and documented
- [ ] No regression in functionality
- [ ] Documentation updated with optimization notes
