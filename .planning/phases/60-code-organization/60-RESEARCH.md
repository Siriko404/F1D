# Phase 60: Code Organization - Research

**Researched:** 2026-02-11
**Domain:** Python code organization, refactoring, code quality tools
**Confidence:** HIGH

## Summary

Phase 60 focuses on code organization improvements across four sub-phases: archiving backup files, clarifying V1/V2/V3 structure through documentation, splitting the monolithic `observability_utils.py` (4,668 lines) into focused modules, and setting up code quality tools (Ruff, mypy, vulture).

**Key findings:**
1. Two files need archiving: `1.0_BuildSampleManifest-legacy.py` and `3.7_H7IlliquidityVariables.py.bak`
2. The `.___archive/` directory structure already exists with `legacy/`, `backups/`, `debug/`, and `docs/` subdirectories
3. The `observability_utils.py` module has 60+ functions used by 47+ files across the codebase
4. Ruff is the modern standard for Python linting/formatting (replaces Flake8+Black)
5. Backward compatibility via `__init__.py` re-exports is well-established Python pattern

**Primary recommendation:** Execute sub-phases sequentially, starting with 60-01 (archive backup files) as lowest risk, then 60-02 (documentation), 60-03 (module split with backward compatibility), and finally 60-04 (code quality tools).

## Standard Stack

### Code Quality Tools (ORG-04)

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| **Ruff** | 0.8+ (2025) | Python linter & formatter (Rust-based) | Replaces Flake8+Black, 100x faster, single binary |
| **mypy** | 1.19+ (2025) | Static type checker | Industry standard for gradual typing |
| **vulture** | 2+ (2025) | Dead code detection | Lightweight, finds unused Python code |

### Python Module Organization

| Practice | Purpose | Why Standard |
|----------|---------|--------------|
| **Package with __init__.py** | Module grouping | Standard Python import mechanism |
| **Re-exports in __init__.py** | Backward compatibility | Allows `from pkg import symbol` from submodules |
| **Logical module split** | Maintainability | Group related functions, reduce file size |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Ruff | Flake8 + Black + isort | Ruff is faster, unified config; alternatives require multiple tools |
| Manual module split | Automatic refactoring tools | Tools can break backward compatibility; manual is safer for reproducibility |
| vulture | coverage.py dead code | Coverage requires test execution; vulture is static analysis |

**Installation:**
```bash
# Code quality tools
pip install ruff mypy vulture

# For type annotations (optional, useful for mypy)
pip install types-psutil types-pandas
```

## Architecture Patterns

### Recommended Archive Structure

```
.___archive/
├── README.md           # Explains archive contents
├── legacy/             # *-legacy.py files (old implementations)
├── backups/            # *.bak files (editor backups)
├── old_versions/       # *_old.py files (previous versions)
└── debug/              # Existing debug scripts (keep)
```

### Pattern 1: Module Split with Backward Compatibility

**What:** Split large module into package while maintaining old import paths

**When to use:** Module > 1,000 lines with clear logical groupings

**Example:**

```python
# shared/observability/__init__.py
"""
Observability utilities package.
Provides backward compatibility with shared.observability_utils.
"""

# Re-export from submodules for backward compatibility
from .logging import DualWriter
from .stats import compute_file_checksum, print_stat, analyze_missing_values
from .files import compute_file_checksum
from .memory import get_process_memory_mb
from .throughput import calculate_throughput
from .anomalies import detect_anomalies_zscore, detect_anomalies_iqr

# Old import path still works:
# from shared.observability_utils import DualWriter  # ✓
from .logging import DualWriter  # New preferred import

__all__ = [
    "DualWriter",
    "compute_file_checksum",
    "print_stat",
    "analyze_missing_values",
    "get_process_memory_mb",
    "calculate_throughput",
    "detect_anomalies_zscore",
    "detect_anomalies_iqr",
]
```

**Source:** [StackOverflow - Re-export modules from __init__.py](https://stackoverflow.com/questions/60440945/correct-way-to-re-export-modules-from-init-py)

### Pattern 2: Ruff Configuration in pyproject.toml

**What:** Centralized configuration for linter and formatter

**Example:**

```toml
[tool.ruff]
# Same as Black
line-length = 88
indent-width = 4
target-version = "py39"

[tool.ruff.lint]
# Enable Pyflakes, pycodestyle, and additional rules
select = ["E4", "E7", "E9", "F", "B", "W"]
ignore = ["E501"]  # Line length (formatter handles)

# Allow auto-fix for all enabled rules
fixable = ["ALL"]
unfixable = []

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402"]  # Import violations
".___archive/**" = ["ALL"]  # Ignore archived code
"tests/**" = ["S101"]  # Allow assert in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Source:** [Ruff Official Documentation](https://docs.astral.sh/ruff/configuration/)

### Pattern 3: Mypy Configuration for Gradual Typing

**What:** Start type checking progressively, not all at once

**Example:**

```toml
[tool.mypy]
# Start with shared utilities only
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

# Progressive rollout: exclude most files initially
exclude = [
    "2_Scripts/[^s]*",  # Exclude all non-shared scripts initially
    "tests/",
    ".___archive/",
]

# Follow imports for type checking
follow_imports = "normal"

# Enable strict mode for new shared modules only
[[tool.mypy.overrides]]
module = "shared.observability.*"
strict = true
```

**Source:** [mypy Configuration Documentation](https://mypy.readthedocs.io/en/stable/config_file.html)

### Anti-Patterns to Avoid

- **Breaking imports without warning:** Always provide deprecation period or maintain backward compatibility
- **Splitting by arbitrary line counts:** Group by logical function, not file size
- **Aggressive auto-fixing:** Review Ruff's `--fix` output before committing
- **Type hints on pipeline scripts:** Focus on shared utilities first; data processing scripts gain less from typing

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Linting/formatting | Custom scripts | Ruff | Handles 700+ rules, battle-tested, fast |
| Dead code detection | Grep for unused | vulture | Handles module hierarchies, attributes |
| Type checking | Runtime isinstance | mypy | Catches errors before execution, better IDE support |
| Import re-exports | Manual from .x import y | __init__.py pattern | Standard Python, maintains backward compat |

**Key insight:** Code quality tools are mature; building custom versions adds maintenance burden without benefit.

## Common Pitfalls

### Pitfall 1: Breaking Backward Compatibility During Module Split

**What goes wrong:** Scripts that import from old path fail after refactoring

**Why it happens:** Direct file moves without re-exports break import statements

**How to avoid:** Use `__init__.py` to re-export all public symbols from new locations

**Warning signs:** Import errors after refactor, failing test suite

```python
# BAD: Just move file
# observability_utils.py -> observability/utils.py
# Scripts fail: from shared.observability_utils import DualWriter  # ERROR

# GOOD: Create package with re-exports
# shared/observability/__init__.py:
# from .utils import DualWriter
# Old import continues to work
```

### Pitfall 2: Overly Aggressive Ruff Auto-Fix

**What goes wrong:** Code behavior changes unexpectedly after `ruff check --fix`

**Why it happens:** Some "fixes" are semantic changes, not just formatting

**How to avoid:** Review diffs before committing; use `--diff` flag first

**Warning signs:** Test failures after formatting, changed logic

```bash
# SAFE: Check what will change first
ruff check --diff 2_Scripts/

# SAFE: Auto-fix with review
ruff check --fix 2_Scripts/
git diff  # Review before commit
```

### Pitfall 3: Vulture False Positives

**What goes wrong:** Vulture reports code as unused when it's called dynamically

**Why it happens:** Static analysis can't detect runtime attribute access, imports

**How to avoid:** Use `# noqa` or `__all__` to whitelist known-used symbols

**Warning signs:** Removing "unused" code causes runtime errors

```python
# Tell vulture these are used externally
__all__ = ["DualWriter", "compute_file_checksum"]

# Or use noqa for specific attributes
getattr(module, func_name)  # noqa: F401
```

### Pitfall 4: Mypy Excludes Too Broad

**What goes wrong:** Important code not type-checked, errors missed

**Why it happens:** Using broad exclude patterns to avoid initial type errors

**How to avoid:** Start narrow (only shared utilities), expand gradually

**Warning signs:** Type errors in "checked" code, inconsistent coverage

```toml
# TOO BROAD - misses real errors
exclude = ["2_Scripts/"]

# BETTER - gradual rollout
exclude = [
    "2_Scripts/1_Sample/",
    "2_Scripts/2_Text/",
    "2_Scripts/3_Financial/",
    "2_Scripts/4_Econometric/",
    # shared/ IS checked
]
```

## Code Examples

### Archive Files with Verification

```python
#!/usr/bin/env python3
"""Archive backup files to .___archive/"""

import shutil
from pathlib import Path
from typing import List

def find_files_to_archive(root: Path) -> dict[str, List[Path]]:
    """Find all *-legacy.py, *.bak, *_old.py files."""
    legacy = list(root.rglob("*-legacy.py"))
    backups = list(root.rglob("*.bak"))
    old = list(root.rglob("*_old.py"))
    return {"legacy": legacy, "backups": backups, "old": old}

def verify_no_active_imports(archived_files: List[Path], scripts_dir: Path) -> bool:
    """Check that archived files aren't imported by active scripts."""
    archived_names = {f.stem for f in archived_files}
    for script in scripts_dir.rglob("*.py"):
        content = script.read_text()
        for name in archived_names:
            if name in content and f"import {name}" in content:
                print(f"WARNING: {script} imports archived {name}")
                return False
    return True
```

### Split observability_utils.py Structure

```
shared/observability/
├── __init__.py           # Re-exports for backward compatibility
├── files.py              # File operations (compute_file_checksum)
├── stats.py              # Statistics (analyze_missing_values, print_stats_summary)
├── memory.py             # Memory tracking (get_process_memory_mb)
├── throughput.py         # Performance (calculate_throughput)
├── anomalies.py          # Anomaly detection (detect_anomalies_zscore, iqr)
└── logging.py            # DualWriter class
```

### Ruff Commands for Development

```bash
# Check what violations exist
ruff check 2_Scripts/

# Fix auto-fixable issues
ruff check --fix 2_Scripts/

# Format code
ruff format 2_Scripts/

# Check without modifying
ruff format --check 2_Scripts/

# Specific rule checks
ruff check --select F401,F403 2_Scripts/  # Unused imports
```

### Vulture Dead Code Detection

```bash
# Find unused code
vulture 2_Scripts/shared/ --min-confidence 80

# Generate whitelist
vulture 2_Scripts/shared/ --make-whitelist > .vulture-whitelist.py

# Exclude archived code
vulture 2_Scripts/ --exclude .___archive/
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flake8 + Black + isort | Ruff (unified) | 2023-2024 | Single tool, 100x faster |
| mypy.ini/setup.cfg | pyproject.toml | 2021+ | Centralized config with other tools |
| Type all at once | Gradual typing | 2019+ | Allows legacy codebase adoption |
| Manual module split | __init__ re-exports | Ongoing | Standard pattern since Python 2.x |

**Deprecated/outdated:**
- **Flake8**: Superseded by Ruff for most use cases
- **pylint**: Too slow, noisy for gradual rollout; Ruff preferred
- **autopep8**: Black/Ruff formatter more opinionated/consistent
- **nosetests**: pytest is de facto standard

## Open Questions

### Q1: observability_utils.py Function Groupings

**What we know:** The module has 60+ functions across 4,668 lines. Functions fall into clear categories (checksum/stats/memory/throughput/anomalies/logging).

**What's unclear:** Exact line counts per category; some functions may have dependencies across categories.

**Recommendation:** Create mapping of all functions by category before split; use `grep -n "^def "` to identify boundaries.

### Q2: Active References to Legacy Files

**What we know:** Two files identified: `1.0_BuildSampleManifest-legacy.py` and `3.7_H7IlliquidityVariables.py.bak`

**What's unclear:** Whether any active scripts reference these files

**Recommendation:** Run grep search across all `.py` files for these filenames before archiving.

### Q3: Mypy Type Annotation Effort

**What we know:** Shared utilities have ~10,000 total lines. Type annotations don't exist yet.

**What's unclear:** How many type errors mypy will find initially; effort required to add annotations.

**Recommendation:** Run mypy on `shared/` only first; document errors; prioritize high-impact modules (data_validation, observability).

## Sources

### Primary (HIGH confidence)
- [Ruff Official Documentation - Configuration](https://docs.astral.sh/ruff/configuration/) - Complete configuration reference
- [mypy Documentation - Configuration File](https://mypy.readthedocs.io/en/stable/config_file.html) - Official mypy config guide
- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/) - Python formatting standards
- [pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) - TOML config standard

### Secondary (MEDIUM confidence)
- [Real Python - Python Code Quality](https://realpython.com/python-code-quality/) - Code quality best practices (March 2025)
- [Medium - How to Structure Large-Scale Python Projects](https://medium.com/the-pythonworld/how-to-structure-large-scale-python-projects-like-a-senior-engineer-77b6cc741924) - Project structure patterns
- [StackOverflow - Re-export modules from __init__.py](https://stackoverflow.com/questions/60440945/correct-way-to-re-export-modules-from-init-py) - Backward compatibility pattern
- [Vulture GitHub Repository](https://github.com/jendrikseipp/vulture) - Dead code detection tool

### Tertiary (LOW confidence)
- [Medium - Progressive Type Checking with mypy](https://medium.com/alan/python-typing-with-mypy-progressive-type-checking-on-a-large-code-base-74e13356bd3a) - Gradual typing approach
- [Python Discuss - Large Project Structure](https://discuss.python.org/t/how-to-best-structure-a-large-project-into-multiple-installable-packages/5404) - Package splitting discussion

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Ruff/mypy/vulture are industry standards, well-documented
- Architecture: HIGH - Python packaging patterns are stable, mature
- Pitfalls: HIGH - Common issues well-documented in official sources

**Research date:** 2026-02-11
**Valid until:** 2026-05-11 (3 months - tool versions may update)

## Codebase-Specific Findings

### Files to Archive (ORG-01)

| File | Location | Destination | Rationale |
|------|----------|-------------|-----------|
| `1.0_BuildSampleManifest-legacy.py` | `2_Scripts/1_Sample/` | `.___archive/legacy/` | Legacy implementation |
| `3.7_H7IlliquidityVariables.py.bak` | `2_Scripts/3_Financial_V2/` | `.___archive/backups/` | Editor backup |
| `STATE.md.bak` | `.planning/` | `.___archive/backups/` | Planning backup |

### observability_utils.py Structure (ORG-03)

Analysis of 4,668-line module:

| Category | Estimated Lines | Functions | Destination |
|----------|----------------|-----------|-------------|
| Logging/DualWriter | ~500 | 1 class | `logging.py` |
| Stats/Summary | ~800 | 15+ functions | `stats.py` |
| File utilities | ~200 | 1 function | `files.py` |
| Memory utilities | ~150 | 1 function | `memory.py` |
| Throughput | ~300 | 1 function | `throughput.py` |
| Anomaly detection | ~400 | 2 functions | `anomalies.py` |
| Step-specific stats* | ~2,200 | 40+ functions | Leave in main or separate |

*Step-specific stats (compute_*_input/process/output_stats) are pipeline-specific and may not belong in shared utilities.

### Import Impact Analysis

- **47 active files** import from `shared.observability_utils`
- **71 total import statements** across the codebase
- Most common imports: `DualWriter`, `compute_file_checksum`, `print_stat`, `calculate_throughput`

### Existing pyproject.toml

- Already contains pytest and coverage configurations
- Missing: `[tool.ruff]`, `[tool.mypy]` sections
- Location: `F1D/pyproject.toml`

### Existing Archive Structure

- `.___archive/legacy/` - Already contains archived scripts
- `.___archive/backups/` - Contains RAR/ZIP backups and config
- `.___archive/debug/` - Contains verification/investigation scripts
- `.___archive/legacy/README.md` - Documents archive contents

---

*Research completed: 2026-02-11*
*Next step: Create PLAN.md files for 60-01 through 60-04*
