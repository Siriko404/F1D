---
phase: 73-cicd-pipeline
plan: 03
subsystem: tooling
tags: [pre-commit, hooks, quality-gates, local-ci]
requires:
  - 73-01-pyproject-toml
  - 73-02-github-actions
provides:
  - local-quality-gates
  - pre-commit-configuration
affects:
  - developer-workflow
  - code-quality
tech-stack:
  added:
    - pre-commit>=3.8
  patterns:
    - pre-commit hooks matching CI configuration
    - Tier-based mypy execution
key-files:
  created:
    - .pre-commit-config.yaml
  modified: []
decisions:
  - pre-commit hooks match CI workflow versions exactly
  - mypy runs only on Tier 1 modules (src/f1d/shared)
  - Large file threshold set to 1MB
metrics:
  duration: 2 min
  completed-date: 2026-02-14
  tasks: 3
  files: 1
---

# Phase 73 Plan 03: Pre-commit Hooks Summary

Pre-commit configuration that mirrors CI tool configuration exactly, ensuring developers catch issues locally before pushing.

## One-Liner

Pre-commit hooks with ruff, mypy, and file quality checks matching CI workflow versions for consistent local and remote quality gates.

## Tasks Completed

| Task | Name | Status | Commit |
|------|------|--------|--------|
| 1 | Create pre-commit configuration per TOOL-02 | COMPLETE | 973644a |
| 2 | Add pre-commit to dev dependencies | N/A (already in 73-01) | - |
| 3 | Verify hook-CI alignment | COMPLETE | 973644a |

## Files Created

### .pre-commit-config.yaml

Pre-commit hooks configuration with:

- **General file quality hooks** (pre-commit-hooks v5.0.0):
  - `trailing-whitespace` - Remove trailing spaces
  - `end-of-file-fixer` - Ensure newline at EOF
  - `check-yaml` - Validate YAML syntax
  - `check-toml` - Validate TOML syntax
  - `check-json` - Validate JSON syntax
  - `check-added-large-files` - Max 1MB threshold
  - `check-merge-conflict` - Catch conflict markers
  - `check-case-conflict` - Case-sensitivity issues
  - `detect-private-key` - Prevent secret commits
  - `debug-statements` - Catch debug code

- **Ruff hooks** (v0.9.0 matching CI):
  - `ruff` - Linter with auto-fix
  - `ruff-format` - Formatter

- **Type checking hooks** (mypy v1.14.1 matching CI):
  - `mypy` with pydantic and types-PyYAML dependencies
  - Runs only on Tier 1 modules (src/f1d/shared)
  - Uses pyproject.toml configuration

## Key Decisions

1. **Hook versions match CI exactly**
   - ruff v0.9.0 matches .github/workflows/ci.yml
   - mypy v1.14.1 matches .github/workflows/ci.yml
   - Both use pyproject.toml as single source of configuration

2. **Tier-based mypy execution**
   - mypy hook runs only on src/f1d/shared (Tier 1)
   - Matches CI behavior from 73-02
   - Prevents blocking commits on Tier 2/3 type issues

3. **Large file threshold**
   - Set to 1MB (1000KB)
   - Prevents accidental data file commits

4. **CI configuration included**
   - pre-commit.ci auto-fixes enabled
   - Weekly autoupdate schedule
   - Auto-fix PRs enabled

## Alignment Verification

| Check | Result |
|-------|--------|
| ruff version matches CI | v0.9.0 |
| mypy version matches CI | v1.14.1 |
| Config file | pyproject.toml (same as CI) |
| mypy scope | src/f1d/shared (same as CI) |
| pre-commit in dev deps | >=3.8 (from 73-01) |

## Deviations from Plan

None - plan executed exactly as written.

## Installation

Developers can install pre-commit hooks with:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # First-time run
```

## Next Steps

- Phase 74: Testing Infrastructure (TEST-01 to TEST-04)

---

*Completed: 2026-02-14*
