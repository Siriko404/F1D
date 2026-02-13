# Phase 64: Folder Structure Consolidation - Research

**Researched:** 2026-02-12
**Domain:** Python project restructuring, file migration, import path updates
**Confidence:** HIGH

## Summary

This phase involves consolidating erroneously created V3 folders into the canonical V2 structure. The V3 folders were created by mistake and contain hypothesis-specific scripts that belong in the existing V2 folder structure. The migration requires careful handling of:

1. **Script moves** with proper renaming to follow V2 numbering conventions
2. **Import path updates** within moved scripts (they reference shared utilities via relative paths)
3. **Output path updates** within scripts (hardcoded V3 paths need changing to V2)
4. **Output folder migration** to match new script locations
5. **Documentation updates** referencing V3 folders

The project uses a config-driven I/O pattern where scripts write to `4_Outputs/[family]/[script]/[timestamp]` and the shared utilities (`shared/` folder) provide path resolution helpers like `get_latest_output_dir()`.

**Primary recommendation:** Process migrations sequentially (one script at a time), verify execution after each move before proceeding to the next.

## Standard Stack

### Core
| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Python | 3.x | Runtime | Project language |
| pathlib | stdlib | Path handling | Cross-platform path operations |
| pandas | installed | Data I/O | All scripts use parquet format |
| pyarrow | installed | Parquet I/O | Parquet file reading/writing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyyaml | installed | Config loading | Scripts load `config/project.yaml` |
| git | installed | Version control | Track file moves with history |

### Project-Specific Utilities
| Module | Location | Purpose |
|--------|----------|---------|
| shared.path_utils | 2_Scripts/shared/ | Path validation, output dir creation, latest resolution |
| shared.observability_utils | 2_Scripts/shared/ | DualWriter logging, memory stats, checksums |
| shared.panel_ols | 2_Scripts/shared/ | Panel regression with fixed effects |
| shared.diagnostics | 2_Scripts/shared/ | VIF calculation |
| shared.industry_utils | 2_Scripts/shared/ | Fama-French industry parsing |

## Architecture Patterns

### Current Script Folder Structure
```
2_Scripts/
├── 1_Sample/              # Sample construction scripts
├── 2_Text/                # Textual analysis scripts
├── 3_Financial/           # Legacy (deprecated)
├── 3_Financial_V2/        # Current financial variable construction
│   ├── 3.1_H1Variables.py
│   ├── 3.2_H2Variables.py
│   ├── 3.2a_AnalystDispersionPatch.py
│   ├── 3.3_H3Variables.py
│   ├── 3.5_H5Variables.py
│   ├── 3.6_H6Variables.py
│   ├── 3.7_H7IlliquidityVariables.py
│   └── 3.8_H8TakeoverVariables.py
├── 3_Financial_V3/        # ERRONEOUS - merge into V2
│   ├── 4.1_H2_BiddleInvestmentResidual.py  -> 3.9_H2_BiddleInvestmentResidual.py
│   └── 4.2_H2_PRiskUncertaintyMerge.py     -> 3.10_H2_PRiskUncertaintyMerge.py
├── 4_Econometric/         # Legacy (deprecated)
├── 4_Econometric_V2/      # Current regression scripts
│   ├── 4.1_H1CashHoldingsRegression.py
│   ├── 4.2_H2InvestmentEfficiencyRegression.py
│   ├── ... (through 4.9_CEOFixedEffects.py)
├── 4_Econometric_V3/      # ERRONEOUS - merge into V2
│   └── 4.3_H2_PRiskUncertainty_Investment.py -> 4.10_H2_PRiskUncertainty_Investment.py
├── 5_Financial_V3/        # ERRONEOUS - split across V2 folders
│   ├── 5.8_H9_StyleFrozen.py          -> 3_Financial_V2/3.11_H9_StyleFrozen.py
│   ├── 5.8_H9_PRiskFY.py              -> 3_Financial_V2/3.12_H9_PRiskFY.py
│   ├── 5.8_H9_AbnormalInvestment.py   -> 3_Financial_V2/3.13_H9_AbnormalInvestment.py
│   └── 5.8_H9_FinalMerge.py           -> 4_Econometric_V2/4.11_H9_Regression.py
└── shared/                # Shared utilities (no changes needed)
```

### Output Folder Structure Pattern
```
4_Outputs/
├── 3_Financial_V2/
│   ├── 3.1_H1Variables/
│   │   └── {timestamp}/
│   ├── ... (3.2 through 3.8)
│   └── latest -> symlink to most recent
├── 3_Financial_V3/           # ERRONEOUS - outputs need moving
│   ├── 4.1_H2_BiddleInvestmentResidual/  -> 3_Financial_V2/3.9_H2_BiddleInvestmentResidual/
│   └── 4.2_H2_PRiskUncertaintyMerge/     -> 3_Financial_V2/3.10_H2_PRiskUncertaintyMerge/
├── 4_Econometric_V2/
│   └── (4.1 through 4.9)
├── 4_Econometric_V3/         # ERRONEOUS - outputs need moving
│   └── 4.3_H2_PRiskUncertainty_Investment/ -> 4_Econometric_V2/4.10_H2_PRiskUncertainty_Investment/
├── 5.8_H9_StyleFrozen/       -> 3_Financial_V2/3.11_H9_StyleFrozen/
├── 5.8_H9_PRiskFY/           -> 3_Financial_V2/3.12_H9_PRiskFY/
├── 5.8_H9_AbnormalInvestment/ -> 3_Financial_V2/3.13_H9_AbnormalInvestment/
└── 5.8_H9_FinalMerge/        -> 4_Econometric_V2/4.11_H9_Regression/
```

### Script Path Update Pattern

Each moved script requires internal path updates:

**Before (V3 path in script):**
```python
# In 4.1_H2_BiddleInvestmentResidual.py (in 3_Financial_V3/)
output_base = (
    root / "4_Outputs" / "3_Financial_V3" / "4.1_H2_BiddleInvestmentResidual"
)
log_base = root / "3_Logs" / "3_Financial_V3" / "4.1_H2_BiddleInvestmentResidual"
```

**After (V2 path in script):**
```python
# In 3.9_H2_BiddleInvestmentResidual.py (in 3_Financial_V2/)
output_base = (
    root / "4_Outputs" / "3_Financial_V2" / "3.9_H2_BiddleInvestmentResidual"
)
log_base = root / "3_Logs" / "3_Financial_V2" / "3.9_H2_BiddleInvestmentResidual"
```

### Shared Module Import Pattern

All scripts use this pattern for shared imports (no change needed after move):
```python
# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from shared.path_utils import ensure_output_dir, get_latest_output_dir
from shared.observability_utils import DualWriter, get_process_memory_mb
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File moves with history preservation | Manual copy + delete | `git mv` | Preserves git blame and history |
| Path resolution for latest outputs | Manual directory scanning | `get_latest_output_dir()` from shared.path_utils | Handles timestamp directories correctly |
| Output directory creation | Manual mkdir | `ensure_output_dir()` from shared.path_utils | Creates parents, handles errors |
| Input validation | Manual exists check | `validate_input_file()` from shared.path_utils | Consistent error messages |

**Key insight:** The shared utilities already handle path operations correctly. After renaming, scripts will continue to find their inputs via `get_latest_output_dir()` which resolves by timestamp.

## Common Pitfalls

### Pitfall 1: Breaking Cross-Script Dependencies
**What goes wrong:** Scripts reference each other's outputs via hardcoded paths. Moving a producer script changes its output location, breaking consumer scripts.
**Why it happens:** V3 scripts reference V3 output paths; V2 scripts reference V2 paths.
**How to avoid:** Update ALL path references in moved scripts BEFORE executing. Check `get_latest_output_dir()` calls for input paths.
**Warning signs:** FileNotFoundError when running moved script, path pointing to old V3 location.

### Pitfall 2: Incorrect Script Numbering
**What goes wrong:** Using wrong target number (e.g., 4.1 instead of 3.9 for Biddle script).
**Why it happens:** V3 scripts used 4.x numbering despite being in "3_Financial" family.
**How to avoid:** Follow the explicit mapping in requirements:
- 4.1_H2_Biddle -> 3.9_H2_Biddle (after 3.8 in 3_Financial_V2)
- 4.2_H2_PRiskMerge -> 3.10_H2_PRiskMerge
- 4.3_H2_PRiskInvestment -> 4.10_H2_PRiskInvestment (after 4.9 in 4_Econometric_V2)
- 5.8_H9_StyleFrozen -> 3.11_H9_StyleFrozen
- 5.8_H9_PRiskFY -> 3.12_H9_PRiskFY
- 5.8_H9_AbnormalInvestment -> 3.13_H9_AbnormalInvestment
- 5.8_H9_FinalMerge -> 4.11_H9_Regression (it's a regression, belongs in econometric)

### Pitfall 3: Output Folder Location Mismatch
**What goes wrong:** Script runs but outputs to old V3 location because internal paths weren't updated.
**Why it happens:** Output paths are hardcoded as strings, not derived from script name.
**How to avoid:** Search for all string occurrences of "V3" in moved scripts and update to "V2".
**Warning signs:** Script succeeds but output appears in V3 folder.

### Pitfall 4: Log File Path Inconsistency
**What goes wrong:** Logs go to wrong location (3_Logs/3_Financial_V3 instead of V2).
**Why it happens:** Log paths follow same pattern as output paths but are easy to miss.
**How to avoid:** Update log_base path alongside output_base path in every moved script.

### Pitfall 5: Windows Symlink Issues
**What goes wrong:** `latest/` symlink creation fails on Windows.
**Why it happens:** Windows requires admin privileges for symlinks, or junction points for directories.
**How to avoid:** Scripts already handle this with try/except fallback to junction. Don't modify symlink logic.

## Code Examples

### Git Move with Rename
```bash
# Move script with git tracking
git mv 2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py \
       2_Scripts/3_Financial_V2/3.9_H2_BiddleInvestmentResidual.py
```

### Path Update Search Pattern
```bash
# Find all V3 references in a script
grep -n "V3\|4\.1_H2\|4\.2_H2\|4\.3_H2\|5\.8_H9" 2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py
```

### Output Folder Migration
```bash
# Move output folder with git tracking
git mv 4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual \
       4_Outputs/3_Financial_V2/3.9_H2_BiddleInvestmentResidual
```

### Verification Command
```bash
# Verify script runs after move
cd 2_Scripts/3_Financial_V2
python 3.9_H2_BiddleInvestmentResidual.py --dry-run
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual path construction | `pathlib.Path` objects | Project inception | Cross-platform compatibility |
| Hardcoded output paths | Config + timestamp directories | Project inception | Reproducibility, versioning |
| Copy-paste file moves | `git mv` for reorganization | This phase | History preservation |

**Deprecated/outdated:**
- `3_Financial/` folder: Legacy structure, superseded by V2
- `4_Econometric/` folder: Legacy structure, superseded by V2
- `5_Financial_V3/` folder: Erroneous creation, should never have existed

## Open Questions

1. **Should we archive V3 output folders or delete them?**
   - What we know: Output folders contain timestamped runs that are reproducible
   - What's unclear: Whether historical V3 outputs should be preserved for audit trail
   - Recommendation: Move existing outputs to V2 locations, delete empty V3 folders afterward

2. **Should documentation files be updated in this phase?**
   - What we know: README.md files in V3 folders reference V3 structure
   - What's unclear: Scope of documentation updates vs. code-only changes
   - Recommendation: Delete V3 READMEs when folders are removed; update any cross-references in V2 READMEs

## Files Requiring Updates

### Scripts to Move and Rename (7 total)
| Current Location | New Location | New Name |
|------------------|--------------|----------|
| 2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py | 2_Scripts/3_Financial_V2/ | 3.9_H2_BiddleInvestmentResidual.py |
| 2_Scripts/3_Financial_V3/4.2_H2_PRiskUncertaintyMerge.py | 2_Scripts/3_Financial_V2/ | 3.10_H2_PRiskUncertaintyMerge.py |
| 2_Scripts/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment.py | 2_Scripts/4_Econometric_V2/ | 4.10_H2_PRiskUncertainty_Investment.py |
| 2_Scripts/5_Financial_V3/5.8_H9_StyleFrozen.py | 2_Scripts/3_Financial_V2/ | 3.11_H9_StyleFrozen.py |
| 2_Scripts/5_Financial_V3/5.8_H9_PRiskFY.py | 2_Scripts/3_Financial_V2/ | 3.12_H9_PRiskFY.py |
| 2_Scripts/5_Financial_V3/5.8_H9_AbnormalInvestment.py | 2_Scripts/3_Financial_V2/ | 3.13_H9_AbnormalInvestment.py |
| 2_Scripts/5_Financial_V3/5.8_H9_FinalMerge.py | 2_Scripts/4_Econometric_V2/ | 4.11_H9_Regression.py |

### Output Folders to Move
| Current Location | New Location |
|------------------|--------------|
| 4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/ | 4_Outputs/3_Financial_V2/3.9_H2_BiddleInvestmentResidual/ |
| 4_Outputs/3_Financial_V3/4.2_H2_PRiskUncertaintyMerge/ | 4_Outputs/3_Financial_V2/3.10_H2_PRiskUncertaintyMerge/ |
| 4_Outputs/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment/ | 4_Outputs/4_Econometric_V2/4.10_H2_PRiskUncertainty_Investment/ |
| 4_Outputs/5.8_H9_StyleFrozen/ | 4_Outputs/3_Financial_V2/3.11_H9_StyleFrozen/ |
| 4_Outputs/5.8_H9_PRiskFY/ | 4_Outputs/3_Financial_V2/3.12_H9_PRiskFY/ |
| 4_Outputs/5.8_H9_AbnormalInvestment/ | 4_Outputs/3_Financial_V2/3.13_H9_AbnormalInvestment/ |
| 4_Outputs/5.8_H9_FinalMerge/ | 4_Outputs/4_Econometric_V2/4.11_H9_Regression/ |

### Documentation Files with V3 References
- 2_Scripts/3_Financial_V3/README.md (delete)
- 2_Scripts/4_Econometric_V3/README.md (delete)
- 2_Scripts/5_Financial_V3/README.md (delete)
- 2_Scripts/3_Financial/README.md (update references)
- 2_Scripts/4_Econometric/README.md (update references)
- docs/VARIABLE_CATALOG_V2_V3.md (update or rename)

### Log Folders (will be created by scripts on next run)
- 3_Logs/3_Financial_V3/ -> 3_Logs/3_Financial_V2/ (after path updates)
- 3_Logs/4_Econometric_V3/ -> 3_Logs/4_Econometric_V2/ (after path updates)
- 3_Logs/5_Financial_V3/ -> 3_Logs/3_Financial_V2/ or 3_Logs/4_Econometric_V2/

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection - Read V3 scripts to understand imports, outputs, dependencies
- Git history analysis - Confirmed V3 folders were recent additions

### Secondary (MEDIUM confidence)
- Project structure conventions - Standard Python project organization patterns

### Tertiary (LOW confidence)
- None - All findings verified from source code

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Based on direct codebase inspection
- Architecture: HIGH - Mapped current structure and target structure from requirements
- Pitfalls: HIGH - Derived from analysis of script internals and common refactoring mistakes

**Research date:** 2026-02-12
**Valid until:** 30 days - Project structure is stable
