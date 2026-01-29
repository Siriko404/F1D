# Phase 26: Repository Cleanup & Archive Organization - Research

**Researched:** 2026-01-29
**Domain:** Repository maintenance, file organization, archival strategies
**Confidence:** HIGH

## Summary

This phase focuses on cleaning up the F1D repository by removing unnecessary files from the root directory and organizing legacy/backup files into a structured archive. The repository currently has 187 files scattered in `.___archive/`, multiple archive directories within `2_Scripts/`, backup files in root, and documentation files that may not belong in root according to the project's strict naming conventions.

The research identified a clear categorization scheme for archive organization:
- **backups/** - Time-stamped backups and compressed archives
- **legacy/** - Old script versions and replaced implementations
- **debug/** - Debug scripts and investigation files
- **docs/** - Superseded documentation and reports
- **test_outputs/** - Test execution logs and temporary outputs

Safety mechanisms are critical: verify no active script imports archived files, check git tracking status before removal, maintain all git-tracked files in archive (don't delete tracked history), and create a manifest of all moved files for rollback capability.

**Primary recommendation:** Create a structured archive with categorized subdirectories, move all non-essential root files to archive, consolidate all scattered archive directories into `.___archive/`, and verify functionality by running Phase 25.1 E2E test as validation.

## Standard Stack

### Core Tools
| Tool/Approach | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| **bash/POSIX utilities** | System default | File operations, finding, moving | Cross-platform, reliable, scriptable |
| **git ls-files** | Git 2.x+ | Verify tracked status | Prevents accidental deletion of tracked files |
| **find + xargs** | POSIX | Batch file operations | Efficient for large file trees |
| **grep -r/-f** | POSIX | Search for file references | Safety check before moving |

### Python Helpers (Optional)
| Library | Purpose | When to Use |
|---------|---------|-------------|
| **pathlib** | Cross-platform path handling | If writing Python cleanup script |
| **shutil** | High-level file operations | For complex moves with metadata |
| **hashlib** | Checksum verification | For integrity checks before/after |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| bash/find | Python script with pathlib | More portable but slower for large trees; bash is simpler for one-time cleanup |
| Manual moves | Automated script | Script is repeatable and auditable; manual is error-prone |

**Installation:** No installation required - uses system utilities. Optional Python script would use standard library only (no external dependencies).

## Architecture Patterns

### Recommended Archive Structure
```
.___archive/
├── backups/              # Time-stamped backups and compressed archives
│   ├── config/
│   │   └── project.yaml.backup
│   ├── scripts/
│   │   ├── 2_Scripts_Backup_20251129_135139.zip
│   │   └── 2_Scripts_backup_20251205_1724.rar
│   └── root/
│       └── BACKUP_20260114_191340/
├── legacy/               # Old script versions and replaced implementations
│   ├── ARCHIVE/          # From 2_Scripts/ARCHIVE
│   ├── ARCHIVE_OLD/      # From 2_Scripts/ARCHIVE_OLD
│   └── ARCHIVE_BROKEN_STEP4/  # From 2_Scripts/4_Econometric/
├── debug/                # Debug scripts and investigation files
│   ├── investigations/   # From .___archive root (investigate_*.py, debug_*.py)
│   └── verification/     # verify_*.py scripts
├── docs/                 # Superseded documentation and reports
│   ├── reports/          # Analysis reports, audit reports
│   ├── readme_archive/   # Old README versions and copies
│   └── presentations/    # Presentation files (HTML, PDF)
├── test_outputs/         # Test execution logs and temporary outputs
│   ├── integration/      # E2E test logs
│   └── temp/             # nul, test_output.txt, etc.
└── manifest.json         # Inventory of all archived files with metadata
```

### Pattern 1: Safety-First File Movement
**What:** Never move files without first verifying they're not actively used and documenting the move
**When to use:** All file movements during cleanup
**Example:**
```bash
# Before moving any file:
# 1. Check if tracked by git
git ls-files | grep -q "$file"
if [ $? -eq 0 ]; then
    echo "WARNING: $file is tracked by git - use git mv instead"
fi

# 2. Check for imports/references
grep -r "import.*$(basename $file .py)" 2_Scripts/
grep -r "from.*$(basename $file .py)" 2_Scripts/

# 3. Move with logging
echo "$(date -Iseconds) MOVED $file -> $destination" >> archive_manifest.log
mv "$file" "$destination"
```

### Pattern 2: Archive Manifest Generation
**What:** Create a JSON manifest tracking all moved files with metadata for rollback
**When to use:** Before and after cleanup operations
**Example:**
```json
{
  "archive_date": "2026-01-29T15:30:00Z",
  "files_moved": 187,
  "categories": {
    "backups": 5,
    "legacy": 82,
    "debug": 45,
    "docs": 30,
    "test_outputs": 25
  },
  "movements": [
    {
      "original_path": "2_Scripts_20251212.rar",
      "archive_path": "___archive/backups/scripts/2_Scripts_20251212.rar",
      "size_bytes": 412371,
      "git_tracked": false,
      "reason": "Compressed backup archive - not needed for active development"
    }
  ]
}
```

### Pattern 3: Validation by E2E Test
**What:** Run full pipeline E2E test after cleanup to verify nothing broke
**When to use:** After completing all file movements
**Example:**
```bash
# From Phase 25.1 - run all scripts sequentially
for script in 2_Scripts/*/1.*.py 2_Scripts/*/2.*.py 2_Scripts/*/3.*.py 2_Scripts/*/4.*.py; do
    echo "Testing: $script"
    python "$script" --dry-run --help
done

# Full E2E test if all scripts respond correctly
python tests/integration/test_e2e_full_pipeline.py
```

### Anti-Patterns to Avoid
- **Delete without verifying:** Never delete files without checking git status and import references
- **Move tracked files with mv:** Use `git mv` for tracked files to preserve history
- **Archive without documentation:** Always update archive_manifest.json when moving files
- **Break the build:** Run E2E test immediately after cleanup to catch issues

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Finding all backup files | Custom glob patterns | `find -name "*.backup" -o -name "*.bak" -o -name "*~"` | Standard, portable, handles edge cases |
| Checking git tracking status | Parse git status output | `git ls-files --error-unmatch <file>` | Reliable exit code, handles submodules |
| Creating archive manifest | Manual JSON writing | `find . -printf ... | jq` or Python `json` module | Handles escaping, special characters |
| Batch file moves with logging | Bash loop with echo | `find ... -print0 | xargs -0 -I{} mv {} dest` | Handles spaces, newlines in filenames |

**Key insight:** Repository cleanup is about organization, not building new tooling. Standard Unix tools are battle-tested for this exact use case. The only custom piece needed is the categorization logic (what goes where), not the movement mechanics.

## Common Pitfalls

### Pitfall 1: Breaking Imports by Moving Modules
**What goes wrong:** Moving a Python module that's still imported by active scripts causes ImportError
**Why it happens:** Relative imports break when source files move without updating import statements
**How to avoid:**
```bash
# Before moving any .py file, grep for imports
for file in $(find 2_Scripts/ARCHIVE* -name "*.py"); do
    basename=$(basename "$file" .py)
    if grep -qr "import.*$basename\|from.*$basename" 2_Scripts/ --exclude-dir=ARCHIVE*; then
        echo "WARNING: $file is still imported - skip or fix imports first"
    fi
done
```
**Warning signs:** Scripts failing with ImportError after cleanup, E2E test showing module not found errors

### Pitfall 2: Deleting Git-Tracked Files
**What goes wrong:** Using `rm` instead of `git rm` on tracked files creates inconsistencies
**Why it happens:** Git still tracks the file but filesystem doesn't have it
**How to avoid:**
```bash
# Always check tracking status first
is_tracked() {
    git ls-files --error-unmatch "$1" >/dev/null 2>&1
}

# Use appropriate command
if is_tracked "$file"; then
    git mv "$file" "$archive_path"  # Preserves git history
else
    mv "$file" "$archive_path"       # Regular move for untracked files
fi
```
**Warning signs:** `git status` showing deleted files, `git diff` showing entire file as deletion

### Pitfall 3: Moving Configuration Files Without Validation
**What goes wrong:** Archiving config/project.yaml.backup breaks ability to restore previous config
**Why it happens:** Backup files look redundant but serve as rollback mechanism
**How to avoid:**
- Keep the most recent config backup in root or easily accessible location
- Only archive old/obsolete config backups (verify age and relevance)
- Document in archive manifest which config version was active when archived
**Warning signs:** Scripts failing with config errors, inability to restore previous working state

### Pitfall 4: Forgetting to Update .gitignore
**What goes wrong:** Archived files continue to appear in `git status` as untracked
**Why it happens:** New archive structure not covered by existing ignore patterns
**How to avoid:**
```bash
# Update .gitignore to include archive
echo ".___archive/" >> .gitignore
git add .gitignore
git commit -m "chore: add archive directory to gitignore"
```
**Warning signs:** `git status` showing many archive files as untracked, bloated git status output

### Pitfall 5: Losing Context with Poor Archive Organization
**What goes wrong:** Files dumped into flat archive with no categorization, impossible to find later
**Why it happens:** Treating archive as junk drawer rather than organized storage
**How to avoid:**
- Use categorized subdirectories (backups/, legacy/, debug/, docs/)
- Create descriptive README.md in each archive subdirectory explaining contents
- Maintain archive_manifest.json with search capability
**Warning signs:** Can't find needed file 6 months later, duplicate files in archive

## Code Examples

Verified patterns from official sources:

### Pre-Movement Safety Checks
```bash
#!/bin/bash
# Source: Git best practices - https://git-scm.com/docs/git-ls-files

# Function to check if file is safe to move
safe_to_move() {
    local file="$1"
    local basename=$(basename "$file" .py)

    # Check 1: Is it tracked by git?
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "TRACKED: $file - use git mv"
        return 1
    fi

    # Check 2: Is it imported by active scripts?
    # Exclude archive directories from search
    if grep -qr "import.*$basename\|from.*$basename" 2_Scripts/ \
        --exclude-dir={ARCHIVE,ARCHIVE_OLD,ARCHIVE_BROKEN*} 2>/dev/null; then
        echo "IMPORTED: $file - still in use"
        return 1
    fi

    return 0
}

# Usage
for file in 2_Scripts/ARCHIVE_OLD/*.py; do
    if safe_to_move "$file"; then
        echo "SAFE: $file"
    fi
done
```

### Archive Manifest Creation
```python
#!/usr/bin/env python3
"""Create archive inventory manifest."""

import json
from pathlib import Path
from datetime import datetime
import subprocess

def get_git_status(filepath):
    """Check if file is tracked by git."""
    try:
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(filepath)],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def create_archive_manifest():
    """Generate JSON manifest of archive contents."""
    manifest = {
        "archive_date": datetime.now().isoformat(),
        "categories": {},
        "movements": []
    }

    archive_root = Path(".___archive")

    for category_dir in archive_root.iterdir():
        if not category_dir.is_dir():
            continue

        category = category_dir.name
        manifest["categories"][category] = 0

        for file in category_dir.rglob("*"):
            if file.is_file():
                manifest["categories"][category] += 1
                manifest["movements"].append({
                    "path": str(file.relative_to(archive_root)),
                    "size_bytes": file.stat().st_size,
                    "git_tracked": get_git_status(file),
                    "modified": datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).isoformat()
                })

    # Write manifest
    manifest_path = archive_root / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest created: {manifest_path}")
    print(f"Total files archived: {len(manifest['movements'])}")

if __name__ == "__main__":
    create_archive_manifest()
```

### Validation After Cleanup
```bash
#!/bin/bash
# Source: Phase 25.1 E2E test validation

echo "=== Post-Cleanup Validation ==="

# Test 1: All scripts respond to --help
echo "Test 1: CLI availability check"
help_errors=0
for script in 2_Scripts/*/[0-9]*.py; do
    if ! python "$script" --help >/dev/null 2>&1; then
        echo "ERROR: $script does not respond to --help"
        ((help_errors++))
    fi
done
echo "Result: $help_errors scripts failed --help test"

# Test 2: No broken imports
echo "Test 2: Import check"
python -c "
import sys
sys.path.insert(0, '2_Scripts/shared')
try:
    import data_loading
    import data_validation
    import observability_utils
    print('OK: All shared modules importable')
except ImportError as e:
    print(f'ERROR: Import failed - {e}')
    sys.exit(1)
"

# Test 3: Config accessible
echo "Test 3: Config check"
if [ -f "config/project.yaml" ]; then
    echo "OK: config/project.yaml exists"
else
    echo "ERROR: config/project.yaml not found"
    exit 1
fi

# Test 4: Root directory compliance
echo "Test 4: Root directory compliance"
root_files=$(ls -1 *.md *.txt *.py 2>/dev/null | wc -l)
echo "Root files count: $root_files"
if [ $root_files -gt 5 ]; then
    echo "WARNING: Root has more than 5 files (expected: README.md, requirements.txt, pyproject.toml)"
fi

echo "=== Validation Complete ==="
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual file deletion | Automated cleanup with manifest | ~2020 | Auditable, reversible |
| Flat archive dump | Categorized archive structure | ~2021 | Searchable, maintainable |
| Ad-hoc backup naming | ISO timestamped backups | ~2019 | Sortable, unambiguous |
| Post-cleanup debugging | Pre-cleanup validation | 2024-2025 | Prevents breakage |

**Deprecated/outdated:**
- **Flat archive directories:** Modern practice uses categorized subdirectories with README.md in each
- **Using .gitignore to hide files:** Better to remove or archive properly than ignore in place
- **Manual file-by-file movement:** Use batch operations with logging for audit trail

## Open Questions

Things that couldn't be fully resolved:

1. **nul file purpose**
   - What we know: File exists in root, contains error message about missing path
   - What's unclear: Why this file exists, if it's referenced by any script
   - Recommendation: Investigate by grepping for "nul" in all scripts; if no references, safe to archive as test_outputs/temp/

2. **INTEGRATION_REPORT.md disposition**
   - What we know: Documents integration gaps from earlier phases, contains valuable historical info
   - What's unclear: Should this stay in root as documentation or be archived
   - Recommendation: Consider keeping in root if it describes current state, otherwise archive to docs/reports/

3. **presentation.pdf placement**
   - What we know: Large PDF (1.5MB) in root, appears to be research presentation
   - What's unclear: Is this actively used, should it be in archive
   - Recommendation: Move to docs/presentations/ in archive; if needed for thesis submission, can be retrieved

## Sources

### Primary (HIGH confidence)
- [Managing large Git Repositories](https://wellarchitected.github.com/library/architecture/recommendations/scaling-git-repositories/large-git-repositories/) - Repository cleanup strategies, archiving obsolete files
- [Git Best Practices: Effective Source Control Management](https://daily.dev/blog/git-best-practices-effective-source-control-management) - Branch management, cleanup practices
- [Backing up a repository](https://docs.github.com/en/repositories/archiving-a-github-repository/backing-up-a-repository) - Official GitHub backup and archival documentation
- [Git ls-files documentation](https://git-scm.com/docs/git-ls-files) - Checking file tracking status

### Secondary (MEDIUM confidence)
- [Cleaning up a messy, exploratory Python project](https://ehmatthes.com/blog/messy_python_project/) - Python project restructuring patterns
- [Python for DevOps: Simple File Cleanup Automation](https://medium.com/@ntando.mv15/python-for-devops-simple-file-cleanup-automation-e508f123ce12) - Automated cleanup with logging
- [Keep your Git repository clean](https://fixed.docs.upsun.com/learn/bestpractices/clean-repository.html) - Repository hygiene best practices
- [Git Backup Best Practices](https://thescimus.com/blog/git-backup-best-practices/) - Backup strategies and verification

### Tertiary (LOW confidence)
- [Good strategies for archiving Git repositories?](https://www.reddit.com/r/DataHoarder/comments/5rg16q/good_strategies-for-arching-git_repositories/) - Community discussion (verified against official docs)
- [How to clean up and create an Archiving strategy](https://stackoverflow.com/questions/74367208/how-to-clean-up-and-create-a-archiving-strategy-for-a-folder-on-github) - StackOverflow community patterns

## Repository-Specific Findings

### Current State Analysis

**Files in Root (non-standard per naming convention):**
- `DEPENDENCIES.md` (tracked) - Dependency documentation
- `INTEGRATION_REPORT.md` (untracked) - Integration gap analysis
- `prd.md` (tracked) - Project requirements document
- `UPGRADE_GUIDE.md` (untracked) - Upgrade procedures
- `presentation.pdf` (tracked) - Research presentation
- `nul` (untracked) - Unknown purpose, contains error message
- `2_Scripts_20251212.rar` (untracked) - Backup archive
- `2_Scripts_20261201.rar` (untracked) - Backup archive

**Archive Directories:**
- `.___archive/` - 187 files, 47MB, flat structure
- `2_Scripts/ARCHIVE/` - 156KB, debug/verification scripts
- `2_Scripts/ARCHIVE_OLD/` - 2.2MB, legacy script versions
- `2_Scripts/4_Econometric/ARCHIVE_BROKEN_STEP4/` - Broken econometric scripts
- `BACKUP_20260114_191340/` - Root backup directory (76KB)

**Python Cache:**
- 10 `__pycache__` directories found (already in .gitignore)

**Test Artifacts:**
- 468 .log files (458 in 3_Logs, 4 in tests/integration, 6 elsewhere)
- 4 test log files in tests/integration/ from Phase 25 E2E testing

**Backup Files:**
- `config/project.yaml.backup` (5KB)
- `2_Scripts/ARCHIVE_OLD/2.7_BuildFinancialControls.py.backup`

**Total Impact:**
- ~200+ files that could be moved to organized archive
- ~50MB of disk space in archives
- Root directory violates naming convention (should only have: README.md, 1_Inputs/, 2_Scripts/, 3_Logs/, 4_Outputs/)

### Recommended Categorization

**backups/** (11 files):
- `2_Scripts_20251212.rar`, `2_Scripts_20261201.rar`
- `BACKUP_20260114_191340/`
- `2_Scripts_Backup_20251129_135139.zip`, `2_Scripts_backup_20251205_1724.rar`
- `config/project.yaml.backup`
- `2.7_BuildFinancialControls.py.backup`

**legacy/** (82 files):
- All of `2_Scripts/ARCHIVE_OLD/` (58 files)
- All of `2_Scripts/ARCHIVE/` (14 files)
- `2_Scripts/4_Econometric/ARCHIVE_BROKEN_STEP4/` (~10 files)

**debug/** (45 files):
- `debug_*.py` files from `.___archive/`
- `investigate_*.py` files from `.___archive/`
- `verify_*.py` files from `2_Scripts/ARCHIVE/`
- `check_*.py` files from `.___archive/`

**docs/** (30 files):
- `*.md` files from `.___archive/` (audit reports, analyses, README copies)
- `presentations/` from `Docs/` directory
- Superseded documentation files

**test_outputs/** (25 files):
- Test logs from `tests/integration/`
- `nul` file (if safe)
- `test_output.txt` and similar temp files

### Files to Keep in Root

**Standard (per CLAUDE.md requirements):**
- `README.md` - Main documentation (keep)
- `1_Inputs/` - Input data directory (keep)
- `2_Scripts/` - Scripts directory (keep)
- `3_Logs/` - Logs directory (keep)
- `4_Outputs/` - Outputs directory (keep)

**Project-standard (Python projects):**
- `requirements.txt` - Dependencies (keep, tracked)
- `pyproject.toml` - Project config (keep, tracked)

**Decision needed (user should verify):**
- `DEPENDENCIES.md` - Detailed dependency docs (value: keeps dependency rationale in easy reach)
- `INTEGRATION_REPORT.md` - Integration gaps (value: may be superseded, check if issues still relevant)
- `prd.md` - Product requirements doc (value: planning doc, may belong in .planning/)
- `UPGRADE_GUIDE.md` - Upgrade procedures (value: operational doc, useful reference)
- `presentation.pdf` - Large file (value: retrieve from archive if needed for thesis)

**Config:**
- `config/project.yaml` - Active config (keep)
- `config/project.yaml.backup` - Archive to backups/

### Safety Verification Steps

1. **Pre-cleanup validation:**
   - Run Phase 25.1 E2E test to establish baseline
   - Create checksum manifest of all files before moving
   - Check all scripts for imports of files to be moved

2. **During cleanup:**
   - Move files in categorized batches
   - Update archive_manifest.json after each batch
   - Use `git mv` for tracked files, regular `mv` for untracked

3. **Post-cleanup validation:**
   - Re-run Phase 25.1 E2E test
   - Verify all scripts still respond to `--help`
   - Check `git status` for unexpected deletions
   - Confirm root directory only contains allowed files

4. **Rollback capability:**
   - Archive manifest enables selective restoration
   - Git history allows reverting if needed
   - Keep pre-cleanup state reference (commit SHA)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using system utilities (bash, git, find) which are stable and well-documented
- Architecture: HIGH - Archive categorization follows established patterns from community sources
- Pitfalls: HIGH - Based on common repository cleanup mistakes documented in multiple sources

**Research date:** 2026-01-29
**Valid until:** 2026-03-01 (60 days - repository cleanup patterns are stable, but tooling may evolve)

**Repository-specific data:**
- Total files analyzed: ~700+ (including archive contents)
- Archive directories identified: 5
- Files recommended for archival: ~200
- Estimated disk space to reclaim: ~50MB (already in archives, just reorganized)
- Risk level: LOW (no active script imports detected in preliminary scan)
