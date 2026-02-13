# F1D Code Quality Standard

**Version:** 5.0
**Last Updated:** 2026-02-13
**Status:** DEFINITION - Implementation deferred to v6.0+
**Milestone:** v5.0 Architecture Standard Definition

---

## Purpose

This document defines the naming conventions and code quality standards for the F1D (Financial Text Analysis) data processing pipeline. It builds on the foundation established in ARCHITECTURE_STANDARD.md (folder structure, module organization) and ensures:

- **Readability:** Code is read more often than written
- **Consistency:** Same patterns applied across the codebase
- **Industry Alignment:** PEP 8, Google Style Guide compliance
- **Tool Support:** ruff, mypy enforcement capabilities

This is a **DEFINITION document**. The standards described here represent the target quality standards that will be implemented in v6.0+. Current code may not fully comply with all standards.

---

## Document Structure

This standard is organized into 6 main sections:

1. **Naming Conventions** (NAM-01 through NAM-05): Script, module, function, variable, and output file naming
2. **Docstring Standard** (CODE-01): Google-style docstrings for functions, methods, and modules
3. **Type Hint Coverage** (CODE-02): Type hint requirements per module tier
4. **Import Organization** (CODE-03): PEP 8 import order and conventions
5. **Error Handling** (CODE-04): Custom exceptions, no bare except policy
6. **Function Size and Module Organization** (CODE-05): Size limits and organization rules

Additionally:
- **Appendix A**: Quick Reference Card
- **Appendix B**: Related Standards

---

## How to Use This Standard

### For New Development (v6.0+)

1. Follow all naming conventions (Section 1)
2. Use Google-style docstrings (Section 2)
3. Add type hints per tier requirements (Section 3)
4. Organize imports per PEP 8 (Section 4)
5. Handle errors with custom exceptions (Section 5)
6. Keep functions focused and small (Section 6)

### For Current Development (v5.0)

1. Use this standard as reference for understanding target quality
2. New code should align with these patterns where feasible
3. Document deviations from the standard
4. Plan for migration to full compliance

### For Code Review

1. Check naming conventions compliance
2. Verify docstrings follow Google-style
3. Ensure type hints on Tier 1 and Tier 2 modules
4. Confirm import organization
5. Check error handling patterns
6. Review function size and complexity

---

## Design Principles

### 1. Readability

Code is read far more often than it is written. Every convention in this standard prioritizes clarity and comprehension:

- **Descriptive names:** Names should reveal intent
- **Consistent patterns:** Same concept, same name
- **Documented behavior:** Docstrings explain what and why
- **Visual structure:** Whitespace and organization aid scanning

**Implementation:**
- Use full words, not abbreviations (except standard ones)
- Follow established naming patterns
- Write self-documenting code with clear docstrings
- Organize code logically

### 2. Consistency

The same patterns should be applied uniformly across the entire codebase:

- **Naming:** Same naming convention for same entity types
- **Formatting:** Same indentation, spacing, line length
- **Documentation:** Same docstring structure everywhere
- **Error handling:** Same exception patterns throughout

**Implementation:**
- Follow this standard without deviation
- Use automated tools (ruff, mypy) for enforcement
- Review for consistency in code review
- Update existing code to match patterns

### 3. Industry Alignment

Follow recognized industry standards to ensure:

- **Familiarity:** Developers recognize patterns
- **Tooling:** IDEs and linters understand conventions
- **Portability:** Code style transfers to other projects
- **Best practices:** Benefit from community wisdom

**Implementation:**
- PEP 8 for style conventions
- Google Style Guide for docstrings
- PEP 484 for type hints
- PEP 760 for exception handling

### 4. Tool Support

Standards should be enforceable with automated tools:

- **ruff:** Linting and formatting
- **mypy:** Type checking
- **pytest:** Testing framework
- **pre-commit:** Git hook automation

**Implementation:**
- Configure tools in pyproject.toml
- Run checks in CI pipeline
- Use pre-commit hooks locally
- Fix violations immediately

---

## Standards Hierarchy

This code quality standard builds on the architecture foundation:

```
ARCHITECTURE_STANDARD.md (Phase 65)
    ├── Defines: Folder structure, module organization, data lifecycle
    │
    └── Referenced by:
        ├── CODE_QUALITY_STANDARD.md (this document)
        │   └── Builds on: Module tiers, import conventions, __init__.py patterns
        │
        ├── CONFIG_STANDARD.md (Phase 67 - Planned)
        │   └── Builds on: config/ directory structure
        │
        └── DOC_STANDARD.md (Phase 68 - Planned)
            └── Builds on: docs/ directory structure
```

Changes to ARCHITECTURE_STANDARD.md may require updates to this document.

---

## Scope and Exclusions

### In Scope

- Naming conventions for all code entities
- Docstring format and requirements
- Type hint coverage requirements
- Import organization patterns
- Error handling conventions
- Function and module organization

### Out of Scope

- Folder structure (see ARCHITECTURE_STANDARD.md)
- Configuration file patterns (Phase 67)
- Documentation templates (Phase 68)
- CI/CD pipeline configuration
- Deployment procedures

---

## Requirements Overview

This document defines the following requirements:

### Naming Conventions

| Requirement | Description |
|-------------|-------------|
| **NAM-01** | Script naming convention (Stage.Step_Description.py) |
| **NAM-02** | Module naming convention (snake_case) |
| **NAM-03** | Function/class naming (snake_case/PascalCase) |
| **NAM-04** | Variable naming patterns |
| **NAM-05** | Output file naming patterns |

### Code Quality Standards

| Requirement | Description |
|-------------|-------------|
| **CODE-01** | Docstring standard (Google-style) |
| **CODE-02** | Type hint coverage per tier |
| **CODE-03** | Import organization (stdlib -> third-party -> local) |
| **CODE-04** | Error handling (custom exceptions, no bare except) |
| **CODE-05** | Function size limits and module organization |

---
