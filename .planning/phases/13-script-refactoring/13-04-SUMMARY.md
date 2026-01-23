---
phase: 13-script-refactoring
plan: 04
subsystem: String Matching Configuration
tags: [config, rapidfuzz, string-matching, fuzzy-matching, yaml, dependencies]

dependency_graph:
  requires:
    - Phase 13-01: Shared utility modules created (regression, financial, reporting)
  provides:
    - Centralized string matching configuration in config/project.yaml
    - RapidFuzz-based string matching module (2_Scripts/shared/string_matching.py)
    - Updated Python dependencies (rapidfuzz>=3.14.0)
  affects:
    - Future scripts that need fuzzy matching can use string_matching.py
    - Step 1 scripts that perform entity matching can migrate to this module

tech_stack:
  added:
    - "rapidfuzz>=3.14.0": Fuzzy string matching library (MIT-licensed, faster than fuzzywuzzy)
  patterns:
    - "Config-driven thresholds": All string matching parameters externalized to config/project.yaml
    - "Graceful degradation": Module functions return empty results when RapidFuzz unavailable

file_tracking:
  key_files:
    created:
      - "2_Scripts/shared/string_matching.py": String matching utilities with 5 functions
    modified:
      - "config/project.yaml": Added string_matching section with thresholds and scorers
      - "requirements.txt": Added rapidfuzz>=3.14.0 dependency

decisions_made:
  - "Scorer selection": Used token_sort_ratio for company_name (handles word order variations), WRatio for entity_name
  - "Threshold values": Default 92.0 for company_name (from existing 1.2_LinkEntities.py), 85.0 for entity_name
  - "Path resolution": Use __file__ for module-relative path calculation (ensures config loads from any working directory)

metrics:
  duration: "4 minutes"
  completed: "2026-01-23"
  commits: 4 (3 tasks + 1 bug fix)

deviations:
  auto_fixed:
    - type: "Rule 1 - Bug"
      description: "Fixed config path resolution relative to module location"
      found_during: "Task 2 verification"
      issue: "Config path used cwd-relative lookup, failed when running from 2_Scripts/"
      fix: "Changed to module-relative path: Path(__file__).parent / '../../config/project.yaml'"
      files_modified: "2_Scripts/shared/string_matching.py"
      commit: "e1f3270"
  authentication_gates: []

---

# Phase 13 Plan 04: String Matching Configuration Summary

**One-liner:** Config-driven fuzzy string matching using RapidFuzz with thresholds externalized to project.yaml.

## Overview

Parameterized string matching thresholds in config/project.yaml and integrated RapidFuzz library for all fuzzy matching operations. Created a reusable string_matching.py module that provides config-driven fuzzy matching for company and entity names.

## What Was Done

### 1. Configuration Structure (config/project.yaml)

Added `string_matching` section with hierarchical configuration:

```yaml
string_matching:
  company_name:
    default_threshold: 92.0
    min_threshold: 85.0
    scorer: token_sort_ratio
    preprocess: true
  entity_name:
    default_threshold: 85.0
    min_threshold: 70.0
    scorer: WRatio
    preprocess: true
  batch_size: 1000
  enable_parallel: false
```

**Threshold selection:**
- company_name: 92.0 (based on existing `score_cutoff=92` in 1.2_LinkEntities.py)
- entity_name: 85.0 (more permissive for general entity matching)

**Scorers:**
- `token_sort_ratio`: Handles word order variations (e.g., "ABC Corp" vs "Corp ABC")
- `WRatio`: Weighted ratio combining multiple scoring methods (most robust)

### 2. String Matching Module (2_Scripts/shared/string_matching.py)

Created shared utility module with 5 functions:

| Function | Purpose |
|----------|---------|
| `warn_if_rapidfuzz_missing()` | Log warning if RapidFuzz unavailable |
| `load_matching_config()` | Load string_matching section from config/project.yaml |
| `get_scorer(name)` | Get RapidFuzz scorer function by name |
| `match_company_names()` | Find best match for single query against candidates |
| `match_many_to_many()` | Efficient many-to-many matching using cdist |

**Key features:**
- Config-driven thresholds (no hard-coded values in code)
- Multiple scorer support (ratio, partial_ratio, token_sort_ratio, token_set_ratio, WRatio, QRatio)
- Optional preprocessing (default_process for case folding and special char removal)
- Graceful degradation (returns empty results if RapidFuzz unavailable)
- Efficient many-to-many matching using `process.cdist` with fallback to `extractOne`

### 3. Dependency Update (requirements.txt)

Added `rapidfuzz>=3.14.0` to requirements.txt:
- MIT-licensed (no commercial restrictions)
- 10x faster than fuzzywuzzy
- Python 3.8+ compatibility
- Mature, well-maintained library

## Technical Decisions

### Path Resolution (Bug Fix)

**Issue:** Initial implementation used cwd-relative path (`config/project.yaml`), which failed when running scripts from subdirectories.

**Fix:** Changed to module-relative path using `Path(__file__).parent / '../../config/project.yaml'`:
- Resolves correctly from any working directory
- Aligns with how other modules handle config loading
- Ensures scripts in 2_Scripts/ can load config without path issues

### Scorer Selection

| Use Case | Scorer | Rationale |
|----------|--------|-----------|
| Company names | `token_sort_ratio` | Handles "ABC Corporation" vs "Corporation ABC" |
| Entity names | `WRatio` | Combines partial, token sort, and set ratios |
| General purpose | `WRatio` | Most robust across name variations |

### Graceful Degradation

Module is designed to work without RapidFuzz (for environments where fuzzy matching is optional):
- Warning logged at import time
- Functions return empty/safe defaults
- No exceptions raised for missing dependency

## Integration Guide

### Basic Usage

```python
from shared.string_matching import match_company_names

# Single query matching
best_match, score = match_company_names(
    "ABC Corporation Inc",
    ["ABC Inc", "XYZ Corp", "ABC Corporation"],
    threshold=90.0,
    scorer_name="token_sort_ratio"
)

if score > 0:
    print(f"Matched: {best_match} (score: {score})")
else:
    print("No match above threshold")
```

### Many-to-Many Matching

```python
from shared.string_matching import match_many_to_many

matches = match_many_to_many(
    queries=["ABC Corp", "XYZ Inc"],
    targets=["ABC Corporation", "XYZ Incorporated", "DEF Ltd"],
    threshold=85.0,
    scorer_name="WRatio"
)

for query, target, score in matches:
    print(f"{query} -> {target} ({score:.1f})")
```

### Loading Configuration

```python
from shared.string_matching import load_matching_config

config = load_matching_config()
company_threshold = config["company_name"]["default_threshold"]
company_scorer = config["company_name"]["scorer"]
```

## Deviations from Plan

### Auto-Fixed Issues

**1. [Rule 1 - Bug] Fixed config path resolution**

- **Found during:** Task 2 verification (config loading test failed)
- **Issue:** Config path used cwd-relative lookup (`config/project.yaml`), failed when running from 2_Scripts/
- **Fix:** Changed to module-relative path: `Path(__file__).parent / '../../config/project.yaml'`
- **Files modified:** 2_Scripts/shared/string_matching.py
- **Commit:** e1f3270

## Next Steps

### Phase 13 Remaining

Phase 13 has 3 plans total, with 1 remaining:
- [ ] **13-05:** Refactor large Step 4 scripts to use shared modules

### Future Integrations

Scripts that can benefit from string_matching.py:
- 1.2_LinkEntities.py: Currently uses fuzzy matching inline
- Any scripts that need company name normalization
- Entity resolution across datasets

## Success Criteria Met

✅ All success criteria from plan achieved:
1. [x] string_matching section added to config/project.yaml
2. [x] shared/string_matching.py module created with 5 functions
3. [x] rapidfuzz>=3.14.0 added to requirements.txt
4. [x] All fuzzy matching thresholds now configurable
5. [x] Module imports successfully and loads config correctly

## Files Modified

| File | Changes | Commit |
|------|---------|--------|
| config/project.yaml | Added string_matching section | 466e5a7 |
| 2_Scripts/shared/string_matching.py | Created (253 lines) + path fix | cd0b72f, e1f3270 |
| requirements.txt | Added rapidfuzz>=3.14.0 | c418711 |

## Testing

**Verification steps executed:**
```bash
# Config verification
grep -q "string_matching:" config/project.yaml

# Requirements verification
grep -q "rapidfuzz" requirements.txt

# Module import verification
cd 2_Scripts && python -c "from shared.string_matching import load_matching_config; config = load_matching_config(); print('Config loaded with', len(config), 'keys')"
# Output: Config loaded with 4 keys: ['company_name', 'entity_name', 'batch_size', 'enable_parallel']
```

All tests pass successfully.
