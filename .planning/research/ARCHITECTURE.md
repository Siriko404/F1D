# Architecture: v3.0 Codebase Cleanup & Optimization

**Project:** F1D Data Processing Pipeline
**Research Date:** 2026-02-10
**Focus:** Reorganization and refactoring while preserving all functionality

## Executive Summary

The existing 4-stage pipeline architecture is sound. The cleanup focuses on (1) removing clutter (backup files), (2) clarifying the V1/V2/V3 structure through documentation (not renaming), and (3) splitting monolithic utilities. **No structural changes to active code** - all versions remain functional.

---

## Current Architecture (Preserved)

### 4-Stage Pipeline

```
1_Sample/    -> 2_Text/    -> 3_Financial/    -> 4_Econometric/
(Build manifest)  (Tokenize)    (Variables)      (Regressions)

Parallel versions (all active):
3_Financial/     -> 4_Econometric/      (V1 - Original)
3_Financial_V2/  -> 4_Econometric_V2/   (V2 - H1-H8)
5_Financial_V3/  -> 4_Econometric_V3/   (V3 - H9, PRisk)
```

**Key principle:** All three versions remain active. Do NOT archive or rename active directories.

---

## Cleanup Architecture

### 1. File Organization (Archive Only)

**Files to archive:**
```
2_Scripts/1_Sample/1.0_BuildSampleManifest-legacy.py    -> .___archive/legacy/
2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py.bak  -> .___archive/backups/
Any other *_backup.py, *_old.py, *~ files
```

**Files to KEEP active:**
- All `3_Financial/`, `3_Financial_V2/`, `5_Financial_V3/` directories
- All `4_Econometric/`, `4_Econometric_V2/`, `4_Econometric_V3/` directories
- All numbered pipeline scripts (1.*, 2.*, 3.*, 4.*)

### 2. Directory Documentation Strategy

**Clarify V1/V2/V3 through README files, not renaming:**

```
2_Scripts/
├── 3_Financial/
│   └── README.md  # "V1: Original financial variables (firm controls, market variables, event flags)"
├── 3_Financial_V2/
│   └── README.md  # "V2: Hypothesis-driven variables (H1-H8 dependent variables, moderators, controls)"
└── 5_Financial_V3/
    └── README.md  # "V3: Advanced interaction variables (H9: PRisk x CEO Style -> Abnormal Investment)"
```

### 3. Utility Module Refactoring

**Before:**
```
shared/
└── observability_utils.py  (4,652 lines - monolithic)
```

**After:**
```
shared/
├── observability/
│   ├── __init__.py          # Re-exports for backward compatibility
│   ├── logging.py           # DualWriter class (~500 lines)
│   ├── stats.py             # print_stat, analyze_missing_values (~800 lines)
│   ├── files.py             # compute_file_checksum (~200 lines)
│   ├── memory.py            # get_process_memory_mb (~150 lines)
│   ├── throughput.py        # calculate_throughput (~300 lines)
│   └── anomalies.py         # detect_anomalies_zscore/iqr (~400 lines)
```

**Backward compatibility preserved:**
```python
# Old imports still work:
from shared.observability_utils import DualWriter  # Re-exported from __init__.py

# New imports preferred:
from shared.observability import DualWriter  # Direct import
```

---

## Documentation Architecture

### File-Level Documentation

**Script header template:**
```python
#!/usr/bin/env python3
"""
STEP X.Y: {Script Name}
===============================================================================

Purpose:
    {One-sentence description of what this script does}

Inputs:
    - 4_Outputs/{PreviousStep}/latest/{file1.parquet}
    - 4_Outputs/{PreviousStep}/latest/{file2.parquet}

Outputs:
    - 4_Outputs/{CurrentStep}/{timestamp}/{output.parquet}
    - stats.json (distributions, diagnostics)
    - {timestamp}.log (execution log)

Dependencies:
    - Requires Step {X}.{Y-1} to be run first
    - Uses: shared.module1, shared.module2

Deterministic: true
==============================================================================
"""
```

### Variable Catalog Structure

```
docs/VARIABLE_CATALOG.md
├── Sample Variables        # From Step 1
│   ├── file_name
│   ├── gvkey
│   ├── ceo_id
│   └── ...
├── Text Variables          # From Step 2
│   ├── Manager_QA_Uncertainty_pct
│   ├── CEO_Pres_Uncertainty_pct
│   └── ...
├── Financial Variables     # From Step 3
│   ├── V1 Variables
│   ├── V2 Variables (H1-H8)
│   └── V3 Variables (H9)
└── Econometric Outputs     # From Step 4
    ├── ClarityCEO
    ├── Regression results
    └── ...
```

---

## Build Order

### Phase 1: Bug Fixes First
1. Fix H7-H8 data truncation bug
2. Fix empty DataFrame returns pattern
3. Add regression tests for bugs

### Phase 2: Cleanup
4. Archive backup files
5. Split observability_utils.py
6. Update imports across all scripts

### Phase 3: Documentation
7. Write directory READMEs (V1/V2/V3 clarification)
8. Write script docstrings (all 61 scripts)
9. Write repo-level README
10. Create variable catalog

### Phase 4: Performance (Optional, lower priority)
11. Profile and optimize hotspots
12. Verify identical outputs

---

## Component Boundaries

### Modified Components

| Component | Modification | Risk |
|-----------|--------------|------|
| `shared/` | Split observability_utils.py into submodules | MEDIUM - requires import updates |
| `.___archive/` | Add legacy/, backups/ subdirectories | LOW - archival only |

### New Components

| Component | Type | Purpose |
|-----------|------|---------|
| `shared/observability/` | Module package | Split utilities |
| `README.md` (repo root) | Documentation | Project overview |
| `*/README.md` (directories) | Documentation | Directory purpose |
| `docs/VARIABLE_CATALOG.md` | Documentation | Variable reference |

### Unchanged Components

All pipeline scripts remain functionally unchanged. Only documentation and imports are modified.

---

## Anti-Patterns to Avoid

1. **Don't rename active directories** - V1/V2/V3 confusion solved through documentation, not renaming
2. **Don't consolidate V1/V2/V3** - They serve different legitimate purposes
3. **Don't break backward compatibility** - Old imports should still work via re-exports
4. **Don't change functionality** - This is cleanup only, preserve exact behavior
5. **Don't optimize prematurely** - Profile first, target hotspots only

---

## Quality Gate Checklist

- [ ] All V1/V2/V3 scripts remain functional after cleanup
- [ ] Backward compatibility preserved (old imports work)
- [ ] All tests pass after refactoring
- [ ] Regression outputs are bitwise identical
- [ ] READMEs accurately describe each directory's purpose
- [ ] Variable catalog is comprehensive

---

*Architecture research: 2026-02-10*
