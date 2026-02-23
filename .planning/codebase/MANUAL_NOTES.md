# Manual Codebase Notes

This file contains human-maintained notes that persist across codebase mapping refreshes.

## Red Team Audit Findings (2026-02-21)

### Concerns that were FALSE POSITIVES

1. **Subprocess validation** - ALREADY EXISTS in `src/f1d/shared/subprocess_validation.py`
   - Has `validate_script_path()` function
   - Used in `build_sample_manifest.py`

2. **Schema validation** - PARTIALLY IMPLEMENTED
   - `src/f1d/shared/data_validation.py` exists with INPUT_SCHEMAS
   - Only 2 schemas defined, but infrastructure is there

3. **Test coverage for link_entities** - COMPREHENSIVE TESTS EXIST
   - `tests/performance/test_performance_link_entities.py` (424 lines, 11 tests)

### Concerns that are REAL but LOW PRIORITY

1. **stats.py size (5,309 lines)** - Architectural debt, but:
   - Functions are cohesive (all observability/stats)
   - Clear naming convention (`compute_{step}_*_stats`)
   - Splitting would increase import complexity
   - **Recommendation:** Keep as-is, add table of contents

2. **Legacy path references** - `inputs/` is intentional for external data

### Fixed in This Audit Cycle

1. **financial_utils.py:157** - Vectorized with merge
2. **build_tenure_map.py:646** - Vectorized with explode()

---

*Last updated: 2026-02-21*
*This file is manually maintained and will NOT be overwritten by /gsd:map-codebase*
