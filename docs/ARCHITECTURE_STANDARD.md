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

---

## 1. Folder Structure (ARCH-01)

This section defines the canonical directory layout for the F1D project using the src-layout pattern recommended by the Python Packaging Authority.

### Target Structure

```
F1D/                              # Project root
├── .github/                      # GitHub-specific configuration
│   ├── workflows/                # CI/CD workflows
│   │   └── test.yml              # Test automation
│   └── ISSUE_TEMPLATE/           # Issue templates
│
├── .planning/                    # GSD planning artifacts
│   ├── phases/                   # Phase-specific plans
│   ├── STATE.md                  # Current project state
│   ├── PROJECT.md                # Project overview
│   └── ROADMAP.md                # Milestone roadmap
│
├── config/                       # Configuration files
│   ├── project.yaml              # Main project configuration
│   ├── logging.yaml              # Logging configuration
│   └── hypotheses.yaml           # Hypothesis definitions
│
├── data/                         # Data directory (mostly gitignored)
│   ├── raw/                      # Original immutable data (READ-ONLY)
│   ├── interim/                  # Intermediate processing stages
│   ├── processed/                # Final cleaned datasets
│   └── external/                 # Third-party reference data
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE_STANDARD.md  # This document
│   ├── VARIABLE_CATALOG.md       # Variable definitions
│   ├── SCRIPT_DOCSTANDARD.md     # Script documentation standard
│   ├── index.md                  # Documentation index
│   └── figures/                  # Documentation figures
│
├── results/                      # Analysis outputs (gitignored)
│   ├── figures/                  # Generated plots and visualizations
│   ├── tables/                   # Generated tables (CSV, LaTeX)
│   └── reports/                  # Generated reports and summaries
│
├── src/                          # Source code (src-layout pattern)
│   └── f1d/                      # Main package
│       ├── __init__.py           # Package metadata and public API
│       │
│       ├── sample/               # Stage 1: Sample construction
│       │   ├── __init__.py
│       │   ├── build_manifest.py # Manifest construction
│       │   └── filters.py        # Sample filters
│       │
│       ├── text/                 # Stage 2: Text processing
│       │   ├── __init__.py
│       │   ├── tokenize.py       # Tokenization utilities
│       │   └── uncertainty.py    # Uncertainty measures
│       │
│       ├── financial/            # Stage 3: Financial features
│       │   ├── __init__.py
│       │   ├── variables.py      # Variable construction
│       │   └── investment.py     # Investment metrics
│       │
│       ├── econometric/          # Stage 4: Econometric analysis
│       │   ├── __init__.py
│       │   ├── regressions.py    # Regression models
│       │   └── diagnostics.py    # Model diagnostics
│       │
│       └── shared/               # Shared utilities
│           ├── __init__.py
│           ├── path_utils.py     # Path resolution
│           ├── panel_ols.py      # Panel OLS utilities
│           ├── io_utils.py       # I/O utilities
│           └── observability/    # Logging and monitoring
│               ├── __init__.py
│               ├── logging.py    # Logging configuration
│               └── stats.py      # Execution statistics
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration and fixtures
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── test_path_utils.py
│   │   └── test_panel_ols.py
│   ├── integration/              # Integration tests
│   │   ├── __init__.py
│   │   └── test_pipeline.py
│   ├── regression/               # Regression tests
│   │   ├── __init__.py
│   │   └── test_outputs.py
│   └── performance/              # Performance tests
│       ├── __init__.py
│       └── test_memory.py
│
├── logs/                         # Execution logs (gitignored)
│   └── *.log
│
├── .___archive/                  # Archived/deprecated code
│   ├── legacy/                   # V1 scripts and deprecated code
│   ├── backups/                  # Backup files (*.bak, *_backup.py)
│   ├── experiments/              # Abandoned experiments
│   ├── docs/                     # Old documentation versions
│   ├── README.md                 # Archive documentation
│   └── manifest.json             # Archive tracking
│
├── .gitignore                    # Git ignore patterns
├── .pre-commit-config.yaml       # Pre-commit hooks (optional)
├── LICENSE                       # License file
├── README.md                     # Project readme
├── pyproject.toml                # Build system and tool configs
├── requirements.txt              # Pinned dependencies
└── setup.py                      # Optional backward compatibility
```

### Directory Descriptions

#### Top-Level Directories

| Directory | Purpose | Git Status | Write Access |
|-----------|---------|------------|--------------|
| `.github/` | GitHub CI/CD and templates | Tracked | Developers |
| `.planning/` | GSD workflow planning artifacts | Tracked | GSD workflow |
| `config/` | Configuration files | Tracked | Developers |
| `data/` | All data files | Partially ignored | Pipeline only |
| `docs/` | Documentation | Tracked | Developers |
| `results/` | Analysis outputs | Ignored | Analysis scripts |
| `src/` | Source code package | Tracked | Developers |
| `tests/` | Test suite | Tracked | Developers |
| `logs/` | Execution logs | Ignored | Pipeline only |
| `.___archive/` | Archived code | Tracked | Archive process |

#### Data Subdirectories

| Directory | Purpose | Mutability | Notes |
|-----------|---------|------------|-------|
| `data/raw/` | Original immutable data | READ-ONLY | Never modify |
| `data/interim/` | Intermediate processing | Deletable | Can regenerate |
| `data/processed/` | Final cleaned data | Controlled | Source for analysis |
| `data/external/` | Third-party data | Reference | Document sources |

#### Results Subdirectories

| Directory | Purpose | Content Types |
|-----------|---------|---------------|
| `results/figures/` | Visualizations | PNG, PDF, SVG |
| `results/tables/` | Data tables | CSV, LaTeX, Excel |
| `results/reports/` | Generated reports | Markdown, PDF, HTML |

### File Placement Rules

#### Root Files (Required)

| File | Purpose | Required |
|------|---------|----------|
| `pyproject.toml` | Build system, dependencies, tool configs | Yes |
| `README.md` | Project overview and quick start | Yes |
| `LICENSE` | License information | Yes |
| `.gitignore` | Git ignore patterns | Yes |
| `requirements.txt` | Pinned dependencies | Recommended |
| `setup.py` | Backward compatibility | Optional |

#### Configuration Files

All configuration files MUST be placed in `config/`:

- `project.yaml` - Main project configuration
- `logging.yaml` - Logging configuration
- `hypotheses.yaml` - Hypothesis definitions
- Additional config files as needed

#### Documentation Files

All documentation files MUST be placed in `docs/`:

- Standards documents (ARCHITECTURE_STANDARD.md, etc.)
- Variable catalogs and references
- User guides and tutorials
- API documentation

#### Test Files

All test files MUST be placed in `tests/` with structure mirroring `src/`:

```
tests/
├── unit/test_path_utils.py    → src/f1d/shared/path_utils.py
├── integration/test_pipeline.py → End-to-end tests
└── regression/test_outputs.py  → Output validation
```

### Rationale

#### Why src-layout?

The src-layout pattern (placing code in `src/package/`) is recommended by PyPA over flat layout for several reasons:

1. **Prevents import confusion**: Separates importable code from project files
2. **Better editable installs**: Ensures `pip install -e .` works correctly
3. **Early error detection**: Packaging issues surface before distribution
4. **Industry standard**: Modern Python projects use src-layout

**Source:** [PyPA src-layout vs flat layout discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

#### Why Separate data/ and results/?

1. **Different lifecycles**: Data is input, results are output
2. **Different git handling**: Data often gitignored, results always gitignored
3. **Clear semantics**: Separates source material from generated output
4. **Cookiecutter standard**: Aligns with data science conventions

#### Why .___archive/ Not Just Delete?

1. **Reproducibility**: Old code may be needed to reproduce old results
2. **Reference value**: Shows evolution of the codebase
3. **Git tracks history**: But archived files are explicitly marked as deprecated
4. **Clear boundaries**: Developers know archived code is not for active use

---

## References

- [Python Packaging Authority - src-layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Cookiecutter Data Science V2](https://drivendata.co/blog/ccds-v2)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [Semantic Versioning](https://semver.org/)
- [FAIR Principles](https://www.go-fair.org/fair-principles/)
