# F1D Module Tier Manifest

**Version:** 6.0.0
**Last Updated:** 2026-02-13
**Status:** Active

---

## Purpose

This document catalogs all modules in the F1D package and their tier classifications based on the Module Tier System defined in ARCHITECTURE_STANDARD.md (ARCH-02).

The tier system establishes quality requirements and maintenance expectations for different categories of code.

---

## Tier System Overview

| Tier | Description | Location | Test Coverage | Documentation |
|------|-------------|----------|---------------|---------------|
| **Tier 1** | Core Shared Utilities | `src/f1d/shared/` | 100% required | Comprehensive with examples |
| **Tier 2** | Stage-Specific Modules | `src/f1d/{stage}/` | 80%+ required | Standard docstrings |
| **Tier 3** | Scripts and One-offs | `scripts/` | Optional | Basic header comment |

### Quality Requirements by Tier

#### Tier 1: Core Shared Utilities

**Characteristics:**
- Used across all stages of the pipeline
- Breaking changes require deprecation period
- Highest stability requirements

**Code Quality:**
- 100% test coverage required
- Complete type hints required
- Strict mypy compliance
- Comprehensive docstrings with examples
- Code review required for all changes
- 30+ day deprecation period for breaking changes

#### Tier 2: Stage-Specific Modules

**Characteristics:**
- Specific to one pipeline stage
- May have version variants (V1, V2)
- Standard quality expectations

**Code Quality:**
- 80%+ test coverage required
- Type hints recommended
- Standard docstrings
- Code review recommended for significant changes

#### Tier 3: Scripts and One-offs

**Characteristics:**
- Ad-hoc analysis or data exploration
- Not imported by other modules
- Lower quality bar acceptable

**Code Quality:**
- Test coverage optional
- Basic header comment
- No stability guarantees

---

## Tier 1: Core Shared Utilities

**Location:** `src/f1d/shared/`

### Path and I/O Utilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `path_utils.py` | Path resolution and output directory utilities | `get_latest_output_dir()`, `ensure_output_dir()`, `validate_input_file()` |
| `data_loading.py` | Data loading utilities | Parquet and CSV loaders |
| `chunked_reader.py` | Memory-efficient chunked file reading | Large file processing |
| `metadata_utils.py` | Metadata handling utilities | Metadata extraction and storage |

### Regression and Econometric Utilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `panel_ols.py` | Panel OLS regression utilities | `run_panel_ols()`, fixed effects handling |
| `iv_regression.py` | Instrumental variable regression | IV estimation utilities |
| `centering.py` | Variable centering utilities | `center_continuous()`, group mean centering |
| `diagnostics.py` | Model diagnostics | `check_multicollinearity()`, `compute_vif()` |
| `regression_helpers.py` | Regression helper functions | Formula construction, result formatting |
| `regression_utils.py` | General regression utilities | Coefficient extraction, standard errors |
| `regression_validation.py` | Regression validation | Input validation for regression models |

### Data Processing Utilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `data_validation.py` | Data validation utilities | Schema validation, data quality checks |
| `financial_utils.py` | Financial data processing | `compute_financial_controls_quarterly()` |
| `industry_utils.py` | Industry classification utilities | FF12 mapping, SIC conversion |
| `string_matching.py` | String matching utilities | Fuzzy matching, entity resolution |

### Output and Reporting

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `latex_tables.py` | LaTeX table generation | Regression tables, summary statistics |
| `reporting_utils.py` | Report generation utilities | Output formatting |

### Validation and Environment

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `dependency_checker.py` | Dependency validation | `validate_prerequisites()` |
| `env_validation.py` | Environment validation | Python version, package checks |
| `cli_validation.py` | CLI argument validation | Argument parsing helpers |
| `subprocess_validation.py` | Subprocess utilities | Safe subprocess execution |

### Observability Subpackage

**Location:** `src/f1d/shared/observability/`

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `__init__.py` | Subpackage initialization | Public API exports |
| `logging.py` | Logging configuration | Structured logging setup |
| `stats.py` | Execution statistics | Performance metrics |
| `memory.py` | Memory monitoring | Memory usage tracking |
| `files.py` | File operation logging | Checksum computation |
| `throughput.py` | Throughput measurement | Processing rate tracking |
| `anomalies.py` | Anomaly detection | Statistical anomaly flags |

### Observability Utilities (Legacy)

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `observability_utils.py` | Combined observability utilities | `DualWriter`, `save_stats()`, `analyze_missing_values()` |
| `dual_writer.py` | Dual output writer | Console + file logging |

---

## Tier 2: Stage-Specific Modules

### Stage 1: Sample Construction

**Location:** `src/f1d/sample/`

| Module | Purpose | Classification |
|--------|---------|----------------|
| `1.0_BuildSampleManifest.py` | Sample manifest orchestrator | Tier 2: Stage 1 |
| `1.1_CleanMetadata.py` | Metadata cleaning | Tier 2: Stage 1 |
| `1.2_LinkEntities.py` | Entity linking | Tier 2: Stage 1 |
| `1.3_BuildTenureMap.py` | Tenure mapping | Tier 2: Stage 1 |
| `1.4_AssembleManifest.py` | Manifest assembly | Tier 2: Stage 1 |
| `1.5_Utils.py` | Stage 1 utilities | Tier 2: Stage 1 |

### Stage 2: Text Processing

**Location:** `src/f1d/text/`

| Module | Purpose | Classification |
|--------|---------|----------------|
| (To be migrated) | Text processing modules | Tier 2: Stage 2 |

### Stage 3: Financial Features

**Location:** `src/f1d/financial/`

#### V1 Methodology (Active Variant)

**Location:** `src/f1d/financial/v1/`

| Module | Purpose | Classification |
|--------|---------|----------------|
| `3.0_BuildFinancialFeatures.py` | V1 financial orchestrator | Tier 2: Stage 3 V1 |
| `3.1_FirmControls.py` | Firm control variables | Tier 2: Stage 3 V1 |
| `3.2_MarketVariables.py` | Market-based variables | Tier 2: Stage 3 V1 |
| `3.3_EventFlags.py` | Event flag construction | Tier 2: Stage 3 V1 |
| `3.4_Utils.py` | V1 utility functions | Tier 2: Stage 3 V1 |

#### V2 Methodology (Active Variant)

**Location:** `src/f1d/financial/v2/`

| Module | Purpose | Classification |
|--------|---------|----------------|
| `3.1_H1Variables.py` | H1 (Cash Holdings) variables | Tier 2: Stage 3 V2 |
| `3.2_H2Variables.py` | H2 (Investment Efficiency) variables | Tier 2: Stage 3 V2 |
| `3.2a_AnalystDispersionPatch.py` | Analyst dispersion patch | Tier 2: Stage 3 V2 |
| `3.3_H3Variables.py` | H3 (Payout Policy) variables | Tier 2: Stage 3 V2 |
| `3.5_H5Variables.py` | H5 (Analyst Dispersion) variables | Tier 2: Stage 3 V2 |
| `3.6_H6Variables.py` | H6 (CCC) variables | Tier 2: Stage 3 V2 |
| `3.7_H7IlliquidityVariables.py` | H7 (Illiquidity) variables | Tier 2: Stage 3 V2 |
| `3.8_H8TakeoverVariables.py` | H8 (Takeover) variables | Tier 2: Stage 3 V2 |
| `3.9_H2_BiddleInvestmentResidual.py` | Investment residual calculation | Tier 2: Stage 3 V2 |
| `3.10_H2_PRiskUncertaintyMerge.py` | PRisk uncertainty merge | Tier 2: Stage 3 V2 |
| `3.11_H9_StyleFrozen.py` | CEO style frozen variables | Tier 2: Stage 3 V2 |
| `3.12_H9_PRiskFY.py` | PRisk fiscal year variables | Tier 2: Stage 3 V2 |
| `3.13_H9_AbnormalInvestment.py` | Abnormal investment calculation | Tier 2: Stage 3 V2 |

### Stage 4: Econometric Analysis

**Location:** `src/f1d/econometric/`

#### V1 Methodology (Active Variant)

**Location:** `src/f1d/econometric/v1/`

| Module | Purpose | Classification |
|--------|---------|----------------|
| `4.1_EstimateCeoClarity.py` | CEO clarity estimation | Tier 2: Stage 4 V1 |
| `4.1.1_EstimateCeoClarity_CeoSpecific.py` | CEO-specific clarity | Tier 2: Stage 4 V1 |
| `4.1.2_EstimateCeoClarity_Extended.py` | Extended clarity model | Tier 2: Stage 4 V1 |
| `4.1.3_EstimateCeoClarity_Regime.py` | Regime-based clarity | Tier 2: Stage 4 V1 |
| `4.1.4_EstimateCeoTone.py` | CEO tone estimation | Tier 2: Stage 4 V1 |
| `4.2_LiquidityRegressions.py` | Liquidity regressions | Tier 2: Stage 4 V1 |
| `4.3_TakeoverHazards.py` | Takeover hazard models | Tier 2: Stage 4 V1 |
| `4.4_GenerateSummaryStats.py` | Summary statistics | Tier 2: Stage 4 V1 |

#### V2 Methodology (Active Variant)

**Location:** `src/f1d/econometric/v2/`

| Module | Purpose | Classification |
|--------|---------|----------------|
| `4.1_H1CashHoldingsRegression.py` | H1 cash holdings regressions | Tier 2: Stage 4 V2 |
| `4.2_H2InvestmentEfficiencyRegression.py` | H2 investment efficiency regressions | Tier 2: Stage 4 V2 |
| `4.3_H3PayoutPolicyRegression.py` | H3 payout policy regressions | Tier 2: Stage 4 V2 |
| `4.4_H4_LeverageDiscipline.py` | H4 leverage discipline regressions | Tier 2: Stage 4 V2 |
| `4.5_H5DispersionRegression.py` | H5 analyst dispersion regressions | Tier 2: Stage 4 V2 |
| `4.6_H6CCCLRegression.py` | H6 CCC regressions | Tier 2: Stage 4 V2 |
| `4.7_H7IlliquidityRegression.py` | H7 illiquidity regressions | Tier 2: Stage 4 V2 |
| `4.8_H8TakeoverRegression.py` | H8 takeover regressions | Tier 2: Stage 4 V2 |
| `4.9_CEOFixedEffects.py` | CEO fixed effects estimation | Tier 2: Stage 4 V2 |
| `4.10_H2_PRiskUncertainty_Investment.py` | PRisk investment regressions | Tier 2: Stage 4 V2 |
| `4.11_H9_Regression.py` | H9 abnormal investment regressions | Tier 2: Stage 4 V2 |

---

## Tier 3: Scripts and One-offs

**Location:** `scripts/` (to be created for ad-hoc analysis scripts)

Scripts in this category are not imported by other modules and serve specific one-time purposes such as:
- Data validation scripts
- One-time data migrations
- Exploratory analysis
- Debug utilities

---

## Import Conventions

### Recommended Import Patterns

```python
# Tier 1 imports (shared utilities)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols
from f1d.shared.diagnostics import check_multicollinearity

# Tier 2 imports (stage-specific)
from f1d.financial.v1 import build_financial_features
from f1d.financial.v2 import construct_h1_variables
from f1d.econometric.v2 import run_h1_regression
```

### Import Order (PEP 8)

```python
# 1. Standard library
import os
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party packages
import numpy as np
import pandas as pd
from linearmodels import PanelOLS

# 3. Local imports (f1d package)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols
```

---

## Version Variant Policy

Per ARCH-04 (Version Management), both V1 and V2 variants are **active** processing approaches:

- **Neither is deprecated** - both variants serve different research purposes
- **Both are maintained** to the same quality standards
- **Import paths explicitly specify the variant**

```python
# Use V1 for standard methodology
from f1d.financial.v1 import build_financial_features

# Use V2 for hypothesis-specific variables
from f1d.financial.v2 import construct_h1_variables
```

---

## Quality Gates by Tier

### Tier 1 Quality Checklist

- [ ] 100% test coverage
- [ ] All functions have type hints
- [ ] Strict mypy passes
- [ ] Comprehensive docstrings with examples
- [ ] Code review completed
- [ ] Breaking changes have deprecation warnings

### Tier 2 Quality Checklist

- [ ] 80%+ test coverage
- [ ] Type hints on public functions
- [ ] Standard docstrings
- [ ] Significant changes reviewed
- [ ] Version variants documented

### Tier 3 Quality Checklist

- [ ] Basic header comment
- [ ] Script is self-contained
- [ ] Does not import from other Tier 3 scripts

---

## Module Statistics

| Tier | Module Count | Description |
|------|--------------|-------------|
| Tier 1 | 24 + 6 (observability) | Core shared utilities |
| Tier 2 (Sample) | 6 | Sample construction |
| Tier 2 (Financial V1) | 5 | V1 financial features |
| Tier 2 (Financial V2) | 13 | V2 hypothesis variables |
| Tier 2 (Econometric V1) | 8 | V1 econometric analysis |
| Tier 2 (Econometric V2) | 11 | V2 hypothesis regressions |
| **Total Tier 2** | **43** | Stage-specific modules |

---

## References

- ARCHITECTURE_STANDARD.md (ARCH-02): Module Tier System definition
- CODE_QUALITY_STANDARD.md (CODE-02): Quality requirements per tier
- ARCH-04: Version Management policy
