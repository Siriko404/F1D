# Phase 24: Complete Script Refactoring - Research

**Researched:** 2026-01-24
**Domain:** Python code refactoring, modularization, line count reduction
**Confidence:** HIGH

## Summary

Phase 24 focuses on reducing the 3 remaining large scripts below 800 lines through actual code extraction (not just imports), building on the foundation established in Phases 13 and 18. Research identified specific extraction opportunities in each script:

- **1.2_LinkEntities.py (847 lines):** Extract industry classification parsing (`parse_ff_industries`), variable description loading, and consolidate verbose inline code in the 507-line main() function
- **3.1_FirmControls.py (801 lines):** Already well-structured with shared module usage; needs minor inline code consolidation (1 line over target)
- **4.1.3_EstimateCeoClarity_Regime.py (799 lines):** Replace duplicate `load_all_data()` function (~110 lines) with import from existing shared module

Previous refactoring attempts (Phase 13, Phase 18) laid groundwork by creating shared utility modules but failed to achieve line count targets because they added imports without removing inline code. Phase 24 must focus on actual code removal through extraction.

**Primary recommendation:** Extract identified functions to new/expanded shared modules, replace inline implementations with imports, and write unit tests for all extracted functions to preserve functionality.

## Standard Stack

The established libraries/tools for Python code refactoring in this project:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | Latest | Unit testing | Industry standard, fixtures, parametrization |
| pathlib | Python 3.4+ | Path operations | Official stdlib, handles symlinks/junctions |
| pandas | Latest | Data manipulation | Primary data processing framework |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| black | Latest | Code formatting | Consistent style, enforces PEP 8 |
| ruff | Latest | Fast linting | Rust-based, replaces flake8+black combo |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest | unittest | pytest more Pythonic, better fixtures |
| pathlib | os.path | pathlib is more modern, OOP-style |

**Installation:**
```bash
pip install pytest black ruff
```

## Architecture Patterns

### Recommended Shared Module Structure
```
2_Scripts/shared/
├── industry_utils.py      # NEW: FF industry classification parsing
├── metadata_utils.py      # NEW: Variable description loading
├── data_loading.py        # EXISTING: load_all_data() (use this!)
├── financial_utils.py     # EXISTING: Financial control calculations
├── string_matching.py     # EXISTING: RapidFuzz wrappers
├── observability_utils.py  # EXISTING: DualWriter, stats helpers
├── symlink_utils.py       # EXISTING: update_latest_link
└── regression_utils.py     # EXISTING: Fixed effects OLS helpers
```

### Pattern 1: Extract Industry Classification Utilities
**What:** Extract `parse_ff_industries()` from 1.2 to shared module
**When to use:** Parsing Fama-French industry classifications from SIC code ranges
**Example:**
```python
# Source: 2_Scripts/1_Sample/1.2_LinkEntities.py (lines 199-234)
# Target: 2_Scripts/shared/industry_utils.py (NEW MODULE)

def parse_ff_industries(zip_path, num_industries):
    """Parse Fama-French industry classification from SIC code ranges.

    Args:
        zip_path: Path to zip file containing FF industry definitions
        num_industries: Number of industries (12 or 48)

    Returns:
        Dict mapping SIC code -> (industry_code, industry_name)
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        txt_file = z.namelist()[0]
        with z.open(txt_file) as f:
            content = f.read().decode("utf-8")

    industry_map = {}
    lines = content.strip().split("\n")

    current_industry_code = None
    current_industry_name = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split(maxsplit=2)
        if len(parts) >= 2 and parts[0].isdigit():
            current_industry_code = int(parts[0])
            current_industry_name = parts[1]
        elif stripped and current_industry_code is not None:
            sic_range = stripped.split()[0] if stripped.split() else ""
            if "-" in sic_range:
                try:
                    start, end = sic_range.split("-")
                    for sic in range(int(start), int(end) + 1):
                        industry_map[sic] = (
                            current_industry_code,
                            current_industry_name,
                        )
                except ValueError:
                    continue

    return industry_map
```

### Pattern 2: Use Existing Shared load_all_data()
**What:** Replace duplicate `load_all_data()` with import from shared module
**When to use:** Loading and merging multi-source data in Step 4 scripts
**Example:**
```python
# BEFORE (2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py, lines 122-233)
def load_all_data(root, year_start, year_end, stats=None):
    # ... 110 lines of duplicate code ...
    return combined

# AFTER (replace with import)
from shared.data_loading import load_all_data

# In main():
df = load_all_data(root, CONFIG["year_start"], CONFIG["year_end"])
```

### Pattern 3: Extract Metadata Utilities
**What:** Extract `load_variable_descriptions()` to shared module
**When to use:** Loading variable descriptions from reference files
**Example:**
```python
# Source: 2_Scripts/1_Sample/1.2_LinkEntities.py (lines 237-258)
# Target: 2_Scripts/shared/metadata_utils.py (NEW MODULE)

def load_variable_descriptions(ref_files):
    """Load variable descriptions from reference files.

    Args:
        ref_files: Dict mapping source name -> file path

    Returns:
        Dict mapping variable name -> {source, description}
    """
    descriptions = {}

    for source, path in ref_files.items():
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        var_name = parts[0].lower()
                        var_desc = parts[2]
                        descriptions[var_name] = {
                            "source": source,
                            "description": var_desc,
                        }
            except Exception:
                pass

    return descriptions
```

### Pattern 4: Unit Testing Extracted Functions
**What:** Write tests for all extracted functions
**When to use:** After any code extraction to shared modules
**Example:**
```python
# tests/unit/test_industry_utils.py (NEW FILE)

import pytest
from shared.industry_utils import parse_ff_industries
from pathlib import Path
import zipfile
import tempfile

def test_parse_ff_industries_basic():
    """Test basic FF industry parsing."""
    # Create test zip file
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".zip", delete=False) as f:
        zip_path = Path(f.name)
        with zipfile.ZipFile(zip_path, "w") as zf:
            # Add test FF industry file
            content = """# FF Industry Classification
1  Consumer Non-durables
1-999
2  Consumer Durables
1000-1999
"""
            zf.writestr("siccodes12.txt", content)

    result = parse_ff_industries(zip_path, 12)

    assert 500 in result
    assert result[500] == (1, "Consumer Non-durables")
    assert 1500 in result
    assert result[1500] == (2, "Consumer Durables")

    zip_path.unlink()
```

### Anti-Patterns to Avoid
- **Extracting without removing:** Adding imports but keeping inline code (Phase 13 mistake)
  - Why bad: Line counts increase instead of decrease
  - Do instead: Remove inline code after adding import

- **Generic utility modules:** Creating overly broad `_utils.py` modules
  - Why bad: Becomes dumping ground for unrelated functions
  - Do instead: Create focused modules by domain (industry_utils, metadata_utils)

- **Skipping unit tests:** Extracting code without tests
  - Why bad: Risk of breaking functionality
  - Do instead: Write tests for all extracted functions

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Industry classification parsing | Custom SIC mapping | shared/industry_utils.py | Already defined in 1.2, just needs extraction |
| Multi-source data loading | Custom merge logic | shared/data_loading.py | Duplicate `load_all_data()` exists in 4.1.3 |
| Variable description loading | Inline file parsing | shared/metadata_utils.py | Generic pattern used across metadata scripts |

**Key insight:** The code to extract already exists inline. The task is moving it to shared modules and replacing with imports, not writing new implementations.

## Common Pitfalls

### Pitfall 1: Extraction Without Removal
**What goes wrong:** Adding `from shared.module import function` but keeping the original function in the script
**Why it happens:** Forgetting to delete the inline implementation
**How to avoid:** After adding import, search for the original function definition and delete it
**Warning signs:** Line count increases after refactoring, duplicate function definitions

### Pitfall 2: Breaking Existing Contracts
**What goes wrong:** Extracted function changes signature or behavior subtly
**Why it happens:** Assuming function signature without checking all usages
**How to avoid:** Verify all calling sites before extraction, preserve exact signature
**Warning signs:** Scripts fail with TypeError after refactoring

### Pitfall 3: Missing Test Coverage
**What goes wrong:** Extracted code breaks edge cases that weren't tested
**Why it happens:** Focusing on happy path, missing edge cases
**How to avoid:** Write comprehensive unit tests with edge cases before extracting
**Warning signs:** Test suite passes but actual script execution fails

### Pitfall 4: Over-Extraction
**What goes wrong:** Extracting too many small functions, creating fragmentation
**Why it happens:** Enthusiasm for reduction without considering readability
**How to avoid:** Only extract functions that:
  - Are at least 20 lines
  - Have a single, clear purpose
  - Could be reused or improve organization
**Warning signs:** Multiple 5-10 line functions extracted that aren't reused

### Pitfall 5: Ignoring Import Cleanup
**What goes wrong:** Unused imports accumulate after extraction
**Why it happens:** Removing code but not removing corresponding imports
**How to avoid:** Run `ruff check --fix` or manually review imports after extraction
**Warning signs:** Linting warnings about unused imports

## Code Examples

Verified patterns from existing codebase:

### Removing Duplicate load_all_data()
```python
# Source: 2_Scripts/shared/data_loading.py (lines 26-153)
# This function already exists! Just import it.

from shared.data_loading import load_all_data

# In 4.1.3, replace lines 122-233 with:
def main(year_start=None, year_end=None):
    # ... setup code ...

    # Load data using shared utility
    df = load_all_data(root, year_start, year_end, stats)

    # ... rest of main() ...
```

### Extracting Industry Classification Parsing
```python
# Source: 2_Scripts/1_Sample/1.2_LinkEntities.py (lines 199-234)
# Move to: 2_Scripts/shared/industry_utils.py

from shared.industry_utils import parse_ff_industries

# In 1.2, replace inline implementation with import and usage:
ff12_map = parse_ff_industries(paths["ff12"], 12)
ff48_map = parse_ff_industries(paths["ff48"], 48)
```

### Extracting Variable Description Loading
```python
# Source: 2_Scripts/1_Sample/1.2_LinkEntities.py (lines 237-258)
# Move to: 2_Scripts/shared/metadata_utils.py

from shared.metadata_utils import load_variable_descriptions

# In 1.2, replace inline implementation with import and usage:
ref_files = {
    "CRSPCompustat_CCM": paths["ccm"] / "variable_reference.txt",
    "metadata": paths["metadata"] / "variable_reference.txt",
}
descriptions = load_variable_descriptions(ref_files)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|----------------|--------------|--------|
| Inline industry parsing | shared/industry_utils.py | Phase 24 (planned) | Reusable FF classification parsing |
| Duplicate load_all_data() | shared/data_loading.py | Phase 18 | Reusable multi-source loading (but not yet used) |
| Inline variable descriptions | shared/metadata_utils.py | Phase 24 (planned) | Centralized metadata loading |

**Deprecated/outdated:**
- Phase 13 generic helpers: Too broad, not specific enough for extraction

## Open Questions

1. **How much inline code consolidation is needed for 3.1?**
   - What we know: 3.1 is only 1 line over target (801 vs 800)
   - What's unclear: Whether inline code can be consolidated without extraction
   - Recommendation: Try minor consolidation first (remove verbose comments, consolidate similar blocks), extract only if still over target

2. **Should industry_utils.py include SIC range optimization?**
   - What we know: Current implementation loops over all SIC codes in ranges
   - What's unclear: Whether range-based lookup would be more efficient
   - Recommendation: Keep current implementation (it works), optimize only if performance issue

3. **How to handle CONFIG dict references in load_all_data() replacement?**
   - What we know: 4.1.3's load_all_data references CONFIG["firm_controls"]
   - What's unclear: Whether shared load_all_data supports flexible column selection
   - Recommendation: Check shared/data_loading.py implementation, may need parameterization

## Sources

### Primary (HIGH confidence)
- 2_Scripts/shared/data_loading.py - Existing load_all_data() implementation
- 2_Scripts/shared/financial_utils.py - Financial control calculations
- 2_Scripts/shared/observability_utils.py - DualWriter, stats helpers
- tests/conftest.py - Pytest fixtures and testing patterns
- tests/unit/test_fuzzy_matching.py - Unit testing examples

### Secondary (MEDIUM confidence)
- .planning/phases/13-script-refactoring/13-RESEARCH.md - Previous refactoring research
- .planning/phases/18-complete-phase-13-refactoring/18-05-SUMMARY.md - Phase 18 results
- v1.2.0-MILESTONE-AUDIT.md - Gap analysis and success criteria

### Tertiary (LOW confidence)
- None - all sources from codebase or documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries standard Python tools
- Architecture: HIGH - Based on existing codebase patterns
- Pitfalls: HIGH - Based on Phase 13/18 failures and common refactoring issues

**Research date:** 2026-01-24
**Valid until:** 2026-02-23 (30 days for stable refactoring patterns)
