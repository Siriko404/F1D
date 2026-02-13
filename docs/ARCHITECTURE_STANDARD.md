# F1D Architecture Standard

**Version:** 5.0
**Last Updated:** 2026-02-13
**Status:** DEFINITION - Implementation deferred to v6.0+
**Milestone:** v5.0 Architecture Standard Definition

---

## Purpose

This document defines the canonical architecture standard for the F1D (Financial Text Analysis) data processing pipeline. It establishes the folder structure, module organization, data management, versioning, and archival conventions that ensure:

- **Reproducibility:** All analyses can be recreated from raw data
- **Auditability:** Complete traceability from results to source data
- **Maintainability:** Clear structure that supports long-term maintenance
- **Quality:** Industry-standard practices for portfolio-ready code

This is a **DEFINITION document**. The standards described here represent the target architecture that will be implemented in v6.0+. Current code follows legacy patterns documented in Appendix A.

---

## Document Structure

This standard is organized into 5 main sections:

1. **Folder Structure** (ARCH-01): Canonical directory layout with src-layout pattern
2. **Module Organization** (ARCH-02): __init__.py hierarchy and package conventions
3. **Data Directory Structure** (ARCH-03): Data lifecycle stages and mutability rules
4. **Version Management** (ARCH-04): Single active version policy and deprecation strategy
5. **Archive and Legacy Code** (ARCH-05): Archive structure and legacy code handling

Additionally:
- **Appendix A**: Migration Guide from current to target state
- **Appendix B**: Relationship to other standards (naming, configuration, documentation)

---

## How to Use This Standard

### For New Development (v6.0+)

1. Follow the canonical folder structure (Section 1)
2. Use the module organization patterns (Section 2)
3. Store data according to lifecycle stage (Section 3)
4. Use semantic versioning on the package (Section 4)
5. Archive deprecated code properly (Section 5)

### For Current Development (v5.0)

1. Use this standard as reference for understanding the target architecture
2. New code should align with these patterns where feasible
3. Document deviations from the standard
4. Plan for migration to the standard structure

### For Code Review

1. Check alignment with folder structure conventions
2. Verify __init__.py follows the pattern
3. Ensure data storage follows mutability rules
4. Confirm deprecated code is properly archived

---

## Design Principles

### 1. Reproducibility (FAIR Principles)

The architecture supports FAIR principles (Findable, Accessible, Interoperable, Reusable):

- **Findable:** Clear structure makes data and code easy to locate
- **Accessible:** Standard paths and import patterns ensure code is usable
- **Interoperable:** Industry-standard patterns align with Python ecosystem
- **Reusable:** Proper packaging enables code reuse across projects

**Implementation:**
- Raw data is never modified (immutability)
- All transformations are version-controlled
- Dependencies are pinned and documented
- Processing scripts are deterministic

### 2. Auditability (Complete Traceability)

Every result can be traced back to source data and transformations:

- **Input provenance:** Clear separation of raw vs. processed data
- **Processing history:** Git tracks all code changes
- **Output lineage:** Results directory preserves analysis outputs
- **Configuration tracking:** Config files document parameters used

**Implementation:**
- data/raw/ is read-only
- data/processed/ documents transformation pipeline
- results/ captures all analysis outputs
- logs/ preserves execution history

### 3. Maintainability (Clear Structure)

The structure supports long-term maintenance and evolution:

- **Separation of concerns:** Code, data, config, docs, tests are separate
- **Explicit dependencies:** pyproject.toml manages all dependencies
- **Consistent patterns:** Same structure applies across all modules
- **Documentation:** Every package and module is documented

**Implementation:**
- src-layout prevents import issues
- __init__.py defines public APIs
- Tests mirror source structure
- Documentation is versioned with code

### 4. Industry Alignment (Standards Compliance)

The architecture follows recognized industry standards:

- **Python Packaging Authority (PyPA):** src-layout, pyproject.toml
- **Cookiecutter Data Science:** Data directory conventions
- **Semantic Versioning:** Package version management
- **Scientific Python:** Research project best practices

**Implementation:**
- PyPA-recommended src-layout pattern
- Cookiecutter data science directory structure
- PEP 621 compliant pyproject.toml
- Standard Python packaging conventions

---

## Standards Hierarchy

This architecture standard is the foundation for a suite of standards:

```
ARCHITECTURE_STANDARD.md (this document)
    ├── Defines: Folder structure, module organization
    │
    ├── Referenced by:
    │   ├── NAMING_STANDARD.md (Phase 66) - File and variable naming conventions
    │   ├── CONFIG_STANDARD.md (Phase 67) - Configuration file patterns
    │   └── DOC_STANDARD.md (Phase 68) - Documentation templates
    │
    └── All standards build upon this foundation
```

Changes to this document may require updates to dependent standards.

---

## Scope and Exclusions

### In Scope

- Directory structure and organization
- Package and module conventions
- Data lifecycle management
- Version control approach
- Archive and legacy handling

### Out of Scope

- Naming conventions (Phase 66: NAMING_STANDARD.md)
- Configuration patterns (Phase 67: CONFIG_STANDARD.md)
- Documentation templates (Phase 68: DOC_STANDARD.md)
- CI/CD pipeline configuration
- Deployment procedures

---

## References

- [Python Packaging Authority - src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Cookiecutter Data Science V2](https://drivendata.co/blog/ccds-v2)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [Semantic Versioning](https://semver.org/)
- [FAIR Principles](https://www.go-fair.org/fair-principles/)
