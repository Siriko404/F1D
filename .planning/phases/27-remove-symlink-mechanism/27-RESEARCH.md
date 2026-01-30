# Phase 27: Remove Symlink Mechanism - Research

**Researched:** 2026-01-30
**Domain:** Pipeline Infrastructure / Path Resolution
**Confidence:** HIGH

## Summary

This phase involves removing the symlink mechanism from the pipeline and replacing it with timestamp-based directory resolution. The codebase currently uses symlinks (or junctions/copies on Windows) to create a `latest/` directory that points to the most recent timestamped output folder. Downstream scripts consume this symlink to find their inputs.

The good news is that **an existing solution already exists** in the codebase: `get_latest_output_dir()` functions in `1.5_Utils.py` and `3.4_Utils.py` already implement timestamp-based resolution with fallback. This function can be consolidated and moved to the shared module.

**Primary recommendation:** Consolidate `get_latest_output_dir()` into `shared/path_utils.py`, update all reader scripts to use it, remove all `update_latest_link()` calls, then deprecate/delete `symlink_utils.py`.

## Current State Analysis

### Symlink Writers (20 Scripts)

All pipeline scripts that produce outputs call `update_latest_link()` at the end:

| Script | Location | Call Pattern |
|--------|----------|--------------|
| 1.0_BuildSampleManifest.py | Line 319 | `update_latest_link(output_dir, output_base / "latest")` |
| 1.1_CleanMetadata.py | Line 678 | `update_latest_link(target_dir=paths["output_dir"], link_path=paths["latest_dir"])` |
| 1.2_LinkEntities.py | Line 830 | Same pattern |
| 1.3_BuildTenureMap.py | Line 666 | Same pattern |
| 1.4_AssembleManifest.py | Line 725 | Same pattern |
| 2.1_TokenizeAndCount.py | Line 1187 | `update_latest_link(out_dir, out_base / "2.1_Tokenized" / "latest")` |
| 2.2_ConstructVariables.py | Line 658 | Same pattern |
| 2.3_Report.py | Line 335 | Same pattern |
| 3.0_BuildFinancialFeatures.py | Line 686 | `update_latest_link(paths["latest_dir"], paths["output_dir"])` |
| 3.1_FirmControls.py | Line 773 | Same pattern |
| 3.2_MarketVariables.py | Line 1557 | Same pattern |
| 3.3_EventFlags.py | Line 548 | Same pattern |
| 4.1_EstimateCeoClarity.py | Line 862 | `update_latest_link(out_dir, out_dir.parent / "latest")` |
| 4.1.1_EstimateCeoClarity_CeoSpecific.py | Line 805 | Same pattern |
| 4.1.2_EstimateCeoClarity_Extended.py | Line 774 | Same pattern |
| 4.1.3_EstimateCeoClarity_Regime.py | Line 715 | Same pattern |
| 4.1.4_EstimateCeoTone.py | Line 736 | Same pattern |
| 4.2_LiquidityRegressions.py | Line 800 | Same pattern |
| 4.3_TakeoverHazards.py | Line 392 | Same pattern |
| 4.4_GenerateSummaryStats.py | Line 863 | Same pattern |

**Total: 20 scripts with symlink creation calls to remove**

### Symlink Readers (Hardcoded Paths)

**62 hardcoded `/latest/` path references** across script files:

```python
# Common pattern (found in setup_paths and data loading functions)
root / "4_Outputs" / "1.1_CleanMetadata" / "latest" / "metadata_cleaned.parquet"
root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables" / "latest" / f"linguistic_variables_{year}.parquet"
root / "4_Outputs" / "3_Financial_Features" / "latest" / f"firm_controls_{year}.parquet"
```

These are spread across:
- Script `setup_paths()` functions
- Data loading code in script bodies
- Docstrings describing inputs (cosmetic, low priority)
- `shared/data_loading.py` (lines 51-57, 79-86, 99-104, 109-115)
- `shared/dependency_checker.py` (line 95: `latest_dir = root / "4_Outputs" / step_name / "latest"`)

**4 additional references in test files** (need updating for tests to pass)

### Existing Solution Pattern

Both `1.5_Utils.py` and `3.4_Utils.py` have **identical** implementations of `get_latest_output_dir()`:

```python
def get_latest_output_dir(output_base, required_file=None):
    """
    Get the latest output directory. Uses 'latest' symlink if valid,
    otherwise finds the most recent timestamped folder.

    Args:
        output_base: Path to the output base directory
        required_file: Optional filename that must exist in the directory
    """
    latest = output_base / "latest"

    # Check if latest exists and has the required file
    if latest.exists():
        if required_file is None or (latest / required_file).exists():
            return latest

    # Fall back to finding latest timestamped folder with required file
    timestamped_dirs = [
        d
        for d in output_base.iterdir()
        if d.is_dir() and d.name != "latest" and d.name[0].isdigit()
    ]

    if timestamped_dirs:
        # Sort by name (timestamp format ensures chronological order)
        sorted_dirs = sorted(timestamped_dirs, key=lambda d: d.name, reverse=True)

        # If required_file specified, find first dir that has it
        if required_file:
            for d in sorted_dirs:
                if (d / required_file).exists():
                    return d
        else:
            return sorted_dirs[0]

    return latest  # Return latest path even if it doesn't exist
```

**Key insight:** This function already provides the exact behavior needed for symlink-free operation. When the symlink doesn't exist, it finds the most recent timestamped folder by sorting directory names.

## Standard Stack

### Core Implementation

| Component | Current Location | Target Location | Purpose |
|-----------|------------------|-----------------|---------|
| `get_latest_output_dir()` | 1.5_Utils.py, 3.4_Utils.py | shared/path_utils.py | Resolve latest timestamped folder |
| `update_latest_link()` | shared/symlink_utils.py | DELETE | No longer needed |
| `validate_prerequisite_step()` | shared/dependency_checker.py | UPDATE | Use new resolver |

### No New Dependencies Required

This is a refactoring phase - no new libraries needed.

## Architecture Patterns

### Recommended Implementation

#### 1. Consolidated Path Resolution (shared/path_utils.py)

```python
def get_latest_output_dir(output_base: Path, required_file: str = None) -> Path:
    """
    Find the most recent timestamped output directory.
    
    Scans for directories matching YYYY-MM-DD_HHMMSS pattern and returns
    the most recent one (by directory name sort, not mtime).
    
    Args:
        output_base: Base output directory (e.g., 4_Outputs/1.1_CleanMetadata)
        required_file: Optional file that must exist in the returned directory
        
    Returns:
        Path to latest timestamped directory, or None if none found
        
    Raises:
        FileNotFoundError: If no valid timestamped directory found
    """
    if not output_base.exists():
        raise FileNotFoundError(f"Output base does not exist: {output_base}")
    
    # Find timestamped directories (start with digit, exclude 'latest')
    timestamped_dirs = [
        d for d in output_base.iterdir()
        if d.is_dir() and d.name[0].isdigit() and d.name != "latest"
    ]
    
    if not timestamped_dirs:
        raise FileNotFoundError(f"No timestamped output directories in: {output_base}")
    
    # Sort by name (timestamp format YYYY-MM-DD_HHMMSS ensures chronological)
    sorted_dirs = sorted(timestamped_dirs, key=lambda d: d.name, reverse=True)
    
    # If required_file specified, find first dir containing it
    if required_file:
        for d in sorted_dirs:
            if (d / required_file).exists():
                return d
        raise FileNotFoundError(
            f"No directory with required file '{required_file}' in: {output_base}"
        )
    
    return sorted_dirs[0]


def resolve_step_output(step_name: str, required_file: str = None, root: Path = None) -> Path:
    """
    Convenience function to resolve a step's latest output directory.
    
    Args:
        step_name: Step name (e.g., "1.1_CleanMetadata")
        required_file: Optional file that must exist
        root: Project root (defaults to auto-detected)
        
    Returns:
        Path to latest output directory for the step
    """
    if root is None:
        root = Path(__file__).parent.parent.parent
    
    output_base = root / "4_Outputs" / step_name
    return get_latest_output_dir(output_base, required_file)
```

#### 2. Updated dependency_checker.py

```python
def validate_prerequisite_step(
    step_name: str, expected_output_file: str, root: Path
) -> bool:
    """
    Validates a single prerequisite step has completed.
    
    Uses timestamp-based resolution instead of symlinks.
    """
    from shared.path_utils import get_latest_output_dir
    
    output_base = root / "4_Outputs" / step_name
    
    try:
        latest_dir = get_latest_output_dir(output_base, required_file=expected_output_file)
        return (latest_dir / expected_output_file).exists()
    except FileNotFoundError:
        return False
```

### Pattern for Reader Scripts

**Before (hardcoded symlink path):**
```python
def setup_paths(config):
    paths = {
        "metadata": root / "4_Outputs" / "1.1_CleanMetadata" / "latest" / "metadata_cleaned.parquet",
    }
```

**After (dynamic resolution):**
```python
from shared.path_utils import get_latest_output_dir

def setup_paths(config):
    metadata_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.1_CleanMetadata",
        required_file="metadata_cleaned.parquet"
    )
    paths = {
        "metadata": metadata_dir / "metadata_cleaned.parquet",
    }
```

### Pattern for Writer Scripts

**Before:**
```python
from shared.symlink_utils import update_latest_link

# At end of main():
update_latest_link(
    target_dir=paths["output_dir"], 
    link_path=paths["latest_dir"], 
    verbose=True
)
```

**After:**
```python
# Simply remove the import and the call
# No replacement needed - writers just create timestamped directories
```

### Anti-Patterns to Avoid

- **Don't use filesystem mtime:** Use directory name sorting. Names are in YYYY-MM-DD_HHMMSS format which sorts chronologically.
- **Don't silently return None:** Raise `FileNotFoundError` when no valid directory found - fail fast.
- **Don't mix symlink and non-symlink approaches:** Complete the migration fully.
- **Don't break backward compatibility during migration:** Keep symlink fallback in reader during transition.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Timestamp parsing | Custom regex | Directory name string sort | Names already sort chronologically |
| Symlink detection | Custom is_symlink checks | Just iterate timestamped dirs | Simpler, cross-platform |

## Common Pitfalls

### Pitfall 1: Breaking Incremental Migration
**What goes wrong:** Updating writers to stop creating symlinks before updating readers to not require them
**Why it happens:** Temptation to remove symlink code first
**How to avoid:** Update ALL readers first, verify pipeline works, THEN remove symlink creation
**Warning signs:** Scripts failing with "latest not found" during partial migration

### Pitfall 2: Docstring/Comment References
**What goes wrong:** Docstrings still reference `/latest/` paths after code is updated
**Why it happens:** Search/replace misses docstrings
**How to avoid:** Grep for all `/latest/` references including in comments
**Warning signs:** Confusing documentation that doesn't match behavior

### Pitfall 3: Test File Hardcoding
**What goes wrong:** Tests fail because they still expect `/latest/` paths
**Why it happens:** Tests access outputs directly without using resolver
**How to avoid:** Update test fixtures to use `get_latest_output_dir()` or mock appropriately
**Warning signs:** Test failures after symlink removal

### Pitfall 4: shared/data_loading.py Forgotten
**What goes wrong:** `load_all_data()` in data_loading.py still uses hardcoded `/latest/` paths
**Why it happens:** Not all data access goes through setup_paths
**How to avoid:** Update data_loading.py to accept resolved paths or use resolver internally
**Warning signs:** 4.x scripts fail after symlink removal

### Pitfall 5: Inconsistent latest_dir References
**What goes wrong:** Scripts still define `paths["latest_dir"]` in setup_paths
**Why it happens:** Incomplete cleanup
**How to avoid:** Remove all `latest_dir` definitions from paths dictionaries
**Warning signs:** Unused variables, lint warnings

## Code Examples

### get_latest_output_dir() - Consolidated Version

```python
# Source: 2_Scripts/shared/path_utils.py (to be added)
from pathlib import Path
from typing import Optional

class OutputResolutionError(Exception):
    """Raised when output directory resolution fails."""
    pass

def get_latest_output_dir(
    output_base: Path, 
    required_file: Optional[str] = None
) -> Path:
    """
    Find the most recent timestamped output directory.
    
    Directories are expected to follow YYYY-MM-DD_HHMMSS naming convention.
    Sorting by name ensures chronological order without parsing timestamps.
    
    Args:
        output_base: Base directory containing timestamped subdirectories
        required_file: If provided, only consider directories containing this file
        
    Returns:
        Path to the most recent valid timestamped directory
        
    Raises:
        OutputResolutionError: If no valid directory found
    """
    if not output_base.exists():
        raise OutputResolutionError(f"Output base directory not found: {output_base}")
    
    # Find directories starting with a digit (timestamp pattern)
    timestamped_dirs = [
        d for d in output_base.iterdir()
        if d.is_dir() and d.name[0].isdigit()
    ]
    
    if not timestamped_dirs:
        raise OutputResolutionError(
            f"No timestamped directories found in: {output_base}"
        )
    
    # Sort by name descending (newest first)
    sorted_dirs = sorted(timestamped_dirs, key=lambda d: d.name, reverse=True)
    
    # Filter by required file if specified
    if required_file:
        for d in sorted_dirs:
            if (d / required_file).exists():
                return d
        raise OutputResolutionError(
            f"No directory contains required file '{required_file}' in: {output_base}"
        )
    
    return sorted_dirs[0]
```

### Updated setup_paths Pattern

```python
# Source: Example for any reader script
from shared.path_utils import get_latest_output_dir

def setup_paths(config):
    root = Path(__file__).parent.parent.parent
    
    # Resolve prerequisite outputs
    clean_metadata_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.1_CleanMetadata",
        required_file="metadata_cleaned.parquet"
    )
    
    paths = {
        "root": root,
        "metadata": clean_metadata_dir / "metadata_cleaned.parquet",
        # ... other paths
    }
    
    # Create this script's output directory (timestamped)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config["paths"]["outputs"] / "1.2_LinkEntities"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])
    
    # NO MORE: paths["latest_dir"] = output_base / "latest"
    
    return paths, timestamp
```

## Migration Strategy

### Phase 27 Sub-Tasks (Recommended Order)

1. **Add get_latest_output_dir() to shared/path_utils.py**
   - Consolidate from 1.5_Utils.py and 3.4_Utils.py
   - Add OutputResolutionError exception
   - Add resolve_step_output() convenience function

2. **Update shared/dependency_checker.py**
   - Use new resolver in validate_prerequisite_step()
   - Remove hardcoded `/latest/` reference

3. **Update shared/data_loading.py**
   - Replace hardcoded `/latest/` paths with resolver calls
   - Or accept pre-resolved paths as parameters

4. **Update all reader scripts (20+ scripts)**
   - Update setup_paths() to use get_latest_output_dir()
   - Update any inline path constructions
   - Remove `latest_dir` from paths dictionaries

5. **Update tests**
   - Update integration tests to use resolver
   - Update regression tests to use resolver

6. **Remove symlink creation (20 scripts)**
   - Remove `from shared.symlink_utils import update_latest_link` imports
   - Remove `update_latest_link()` calls
   - Remove `paths["latest_dir"]` definitions

7. **Clean up 1.5_Utils.py and 3.4_Utils.py**
   - Remove get_latest_output_dir() (now in shared)
   - Update imports in scripts that use these utils

8. **Deprecate/Delete symlink_utils.py**
   - Remove from shared/__init__.py exports
   - Delete the file
   - Remove update_latest_symlink from 1.5_Utils.py

9. **Final cleanup**
   - Update docstrings mentioning `/latest/`
   - Clean up any remaining references
   - Delete existing `latest/` symlinks from 4_Outputs/

### Rollback Strategy

If issues arise during migration:
1. The symlinks will still exist in 4_Outputs/ during migration
2. The new resolver checks symlink first (backward compatible)
3. Can revert individual script changes without breaking others

## Risk Areas

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missing a hardcoded path | MEDIUM | LOW | Comprehensive grep + test coverage |
| Tests break | HIGH | MEDIUM | Update tests early in process |
| Partial migration confusion | MEDIUM | MEDIUM | Clear task ordering, complete one script fully before moving on |
| Existing symlinks left behind | LOW | LOW | Final cleanup task to delete them |

## Open Questions

1. **Should existing `latest/` symlinks be deleted?**
   - Recommendation: Yes, as final cleanup step
   - Risk: Very low - they become unused after migration

2. **Should we keep backward compatibility in get_latest_output_dir()?**
   - Current impl checks symlink first, then falls back
   - Recommendation: Remove symlink check after full migration to simplify
   - Could add config flag if phased rollout needed

## Sources

### Primary (HIGH confidence)
- `2_Scripts/shared/symlink_utils.py` - Current symlink implementation (216 lines)
- `2_Scripts/1_Sample/1.5_Utils.py` - Existing get_latest_output_dir() implementation
- `2_Scripts/3_Financial/3.4_Utils.py` - Duplicate get_latest_output_dir() implementation
- `2_Scripts/shared/dependency_checker.py` - Uses `/latest/` pattern
- `2_Scripts/shared/data_loading.py` - Uses `/latest/` pattern
- Grep analysis of codebase (62 hardcoded references in scripts, 4 in tests)

### Secondary (MEDIUM confidence)
- Directory structure analysis of 4_Outputs/ (confirmed timestamp pattern)
- Git history from Phase 23-03 context (prior symlink consolidation)

## Metadata

**Confidence breakdown:**
- Current state analysis: HIGH - Direct codebase examination
- Migration strategy: HIGH - Based on existing solution pattern
- Risk assessment: MEDIUM - Standard refactoring risks

**Research date:** 2026-01-30
**Valid until:** Indefinite (internal infrastructure change)

## Script Reference Quick-Look

### Writers to Update (remove symlink creation)
```
2_Scripts/1_Sample/1.0_BuildSampleManifest.py
2_Scripts/1_Sample/1.1_CleanMetadata.py
2_Scripts/1_Sample/1.2_LinkEntities.py
2_Scripts/1_Sample/1.3_BuildTenureMap.py
2_Scripts/1_Sample/1.4_AssembleManifest.py
2_Scripts/2_Text/2.1_TokenizeAndCount.py
2_Scripts/2_Text/2.2_ConstructVariables.py
2_Scripts/2_Text/2.3_Report.py
2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
2_Scripts/3_Financial/3.1_FirmControls.py
2_Scripts/3_Financial/3.2_MarketVariables.py
2_Scripts/3_Financial/3.3_EventFlags.py
2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py
2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py
2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py
2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py
2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py
2_Scripts/4_Econometric/4.2_LiquidityRegressions.py
2_Scripts/4_Econometric/4.3_TakeoverHazards.py
2_Scripts/4_Econometric/4.4_GenerateSummaryStats.py
```

### Shared Modules to Update
```
2_Scripts/shared/path_utils.py (add get_latest_output_dir)
2_Scripts/shared/dependency_checker.py (update validate_prerequisite_step)
2_Scripts/shared/data_loading.py (replace hardcoded paths)
2_Scripts/shared/__init__.py (update exports)
2_Scripts/shared/symlink_utils.py (DELETE)
2_Scripts/1_Sample/1.5_Utils.py (remove duplicate, update exports)
2_Scripts/3_Financial/3.4_Utils.py (remove duplicate, update exports)
```

### Tests to Update
```
tests/integration/test_full_pipeline.py
tests/integration/test_pipeline_step1.py
tests/integration/test_pipeline_step2.py
tests/integration/test_pipeline_step3.py
tests/unit/test_chunked_reader.py
tests/regression/generate_baseline_checksums.py
tests/regression/test_output_stability.py
```
