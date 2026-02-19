# Stage 3/4 Refactoring Progress Report

**Date:** 2026-02-19
**Status:** Phase 1 Complete (Manager Clarity Pilot)
**Author:** Claude Code Session

---

## Executive Summary

This document records the complete refactoring of Stage 3 (variables) and Stage 4 (econometric) architecture for the F1D project. The pilot implementation for the Manager Clarity hypothesis (4.1) has been successfully completed, verified, and serves as the template for extending to other hypotheses.

### Key Results
- **Main sample:** 56,060 observations, 2,539 managers, R² = 0.41
- **Finance sample:** 12,852 observations, 548 managers, R² = 0.31
- **Utility sample:** 2,950 observations, 134 managers, R² = 0.22

---

## Table of Contents

1. [Background and Motivation](#background-and-motivation)
2. [Architecture Overview](#architecture-overview)
3. [Implementation Details](#implementation-details)
4. [Files Created](#files-created)
5. [Files Modified](#files-modified)
6. [Files Deleted](#files-deleted)
7. [Key Learnings](#key-learnings)
8. [Bugs Fixed](#bugs-fixed)
9. [Next Steps](#next-steps)
10. [Verification Checklist](#verification-checklist)

---

## Background and Motivation

### Problems with Old Architecture

The previous Stage 3 (financial) and Stage 4 (econometric) architecture had several critical issues:

1. **Versioned subdirectories (v1, v2)**: Created confusion about which scripts to use
2. **Hardcoded timestamp paths**: Scripts referenced specific output directories that changed on each run
3. **Inconsistent variable loading**: Each script had its own logic for loading variables
4. **Numbered prefixes**: Scripts like `4.1_EstimateManagerClarity.py` were hard to maintain
5. **No centralized configuration**: Variable sources were scattered across files

### Goals of Refactoring

1. **Single source of truth**: One config file (`config/variables.yaml`) for all variable sources
2. **Shared variable modules**: Reusable builders in `src/f1d/shared/variables/`
3. **Modern naming**: Descriptive names without numbered prefixes
4. **Config-based path resolution**: Scripts find latest output directories automatically
5. **Accounting Review LaTeX output**: Professional table format for publications

---

## Architecture Overview

### New Folder Structure

```
src/f1d/
├── shared/
│   ├── variables/                    # NEW: Shared variable modules
│   │   ├── __init__.py              # Exports all builders
│   │   ├── base.py                  # VariableBuilder, VariableStats, VariableResult
│   │   ├── manager_qa_uncertainty.py
│   │   ├── manager_pres_uncertainty.py
│   │   ├── analyst_qa_uncertainty.py
│   │   ├── negative_sentiment.py
│   │   ├── stock_return.py
│   │   ├── market_return.py
│   │   ├── eps_growth.py
│   │   ├── earnings_surprise.py
│   │   └── manifest_fields.py       # ceo_id, gvkey, ff12_code, etc.
│   └── latex_tables_accounting.py   # Accounting Review LaTeX generator
│
├── variables/                        # NEW: Stage 3 scripts
│   ├── __init__.py
│   └── build_manager_clarity_panel.py
│
├── sample/                           # RENAMED (was 1.0_, 1.1_, etc.)
│   ├── build_sample_manifest.py
│   ├── clean_metadata.py
│   ├── link_entities.py
│   ├── build_tenure_map.py
│   ├── assemble_manifest.py
│   └── utils.py
│
├── text/                             # RENAMED (was 2.1_, 2.2_, etc.)
│   ├── tokenize_transcripts.py
│   └── build_linguistic_variables.py
│
├── financial/                        # MOVED from v1/ subdirectory
│   ├── build_financial_features.py
│   ├── build_firm_controls.py
│   ├── build_market_variables.py
│   ├── build_event_flags.py
│   └── utils.py
│
└── econometric/
    └── test_manager_clarity.py       # NEW: Modern hypothesis test

config/
└── variables.yaml                    # NEW: Central variable configuration
```

### Variable Builder Pattern

Each variable module follows this interface:

```python
class VariableBuilder:
    """Base class for variable builders."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build the variable for all years."""
        ...

    def resolve_source_dir(self, root_path: Path) -> Path:
        """Find directory with most matching files (auto-detects timestamp)."""
        ...
```

### Config-Based Path Resolution

The `resolve_source_dir()` method is critical for reproducibility:

```python
def resolve_source_dir(self, root_path: Path) -> Path:
    source = self.config.get("source", "")
    source_path = root_path / source

    # Find subdirectory with most matching files
    subdirs = sorted([d for d in source_path.iterdir() if d.is_dir()],
                    key=lambda x: x.name, reverse=True)

    best_dir = None
    best_count = 0
    for subdir in subdirs:
        count = self._count_matching_files(subdir)
        if count > best_count:
            best_count = count
            best_dir = subdir

    return best_dir if best_dir else source_path
```

This ensures scripts always use the most complete output directory, not hardcoded timestamps.

---

## Implementation Details

### Stage 3: Panel Building (`build_manager_clarity_panel.py`)

**Purpose:** Build complete panel for Manager Clarity hypothesis test.

**Inputs:**
- Manifest from Stage 1 (ceo_id, gvkey, ff12_code, start_date)
- Linguistic variables from Stage 2 (Manager_QA_Uncertainty_pct, etc.)
- Financial variables from Stage 3 (StockRet, MarketRet, EPS_Growth, SurpDec)

**Outputs:**
- `manager_clarity_panel.parquet` - Complete merged panel
- `summary_stats.csv` - Statistics for all variables
- `report_step3_manager_clarity.md` - Human-readable report

**Process:**
1. Load variable config from `config/variables.yaml`
2. Initialize all variable builders
3. Build each variable (finds latest output automatically)
4. Merge on `file_name` key
5. Assign industry samples (Main, Finance, Utility)
6. Save outputs with timestamp directory

### Stage 4: Hypothesis Test (`test_manager_clarity.py`)

**Purpose:** Run Manager Clarity fixed effects regression and output results.

**Model Specification:**
```
Manager_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
    Manager_Pres_Uncertainty_pct +
    Analyst_QA_Uncertainty_pct +
    Entire_All_Negative_pct +
    StockRet + MarketRet + EPS_Growth + SurpDec
```

**Outputs:**
- `manager_clarity_table.tex` - Accounting Review LaTeX table
- `clarity_scores.parquet` - Manager fixed effects (ClarityManager = -gamma_i)
- `regression_results_*.txt` - Full regression summaries
- `report_step4_manager_clarity.md` - Human-readable report

**Process:**
1. Load panel from Stage 3
2. Filter to complete cases
3. Run regressions by industry sample (Main, Finance, Utility)
4. Filter managers with >= 5 calls
5. Extract manager fixed effects
6. Standardize to ClarityManager scores
7. Generate LaTeX output

### Industry Sample Classification

```python
def assign_sample(ff12_code: int) -> str:
    if ff12_code == 11:
        return "Finance"
    elif ff12_code == 8:
        return "Utility"
    elif ff12_code in [1, 2, 3, 4, 5, 6, 7, 9, 10, 12]:
        return "Main"
    else:
        return "Other"
```

---

## Files Created

### Variable Modules (11 files)

| File | Purpose |
|------|---------|
| `src/f1d/shared/variables/__init__.py` | Package init, exports all builders |
| `src/f1d/shared/variables/base.py` | VariableBuilder, VariableStats, VariableResult classes |
| `src/f1d/shared/variables/manager_qa_uncertainty.py` | Manager Q&A uncertainty |
| `src/f1d/shared/variables/manager_pres_uncertainty.py` | Manager presentation uncertainty |
| `src/f1d/shared/variables/analyst_qa_uncertainty.py` | Analyst Q&A uncertainty |
| `src/f1d/shared/variables/negative_sentiment.py` | Entire_All_Negative_pct |
| `src/f1d/shared/variables/stock_return.py` | StockRet |
| `src/f1d/shared/variables/market_return.py` | MarketRet |
| `src/f1d/shared/variables/eps_growth.py` | EPS_Growth |
| `src/f1d/shared/variables/earnings_surprise.py` | SurpDec |
| `src/f1d/shared/variables/manifest_fields.py` | ceo_id, gvkey, ff12_code, start_date |

### Stage 3/4 Scripts (4 files)

| File | Purpose |
|------|---------|
| `src/f1d/variables/__init__.py` | Package init |
| `src/f1d/variables/build_manager_clarity_panel.py` | Stage 3: Build panel |
| `src/f1d/econometric/test_manager_clarity.py` | Stage 4: Run hypothesis test |
| `src/f1d/shared/latex_tables_accounting.py` | Accounting Review LaTeX generator |

### Configuration (1 file)

| File | Purpose |
|------|---------|
| `config/variables.yaml` | Central variable source configuration |

### Renamed Stage 1 Scripts (6 files)

| Old Name | New Name |
|----------|----------|
| `1.0_BuildSampleManifest.py` | `build_sample_manifest.py` |
| `1.1_CleanMetadata.py` | `clean_metadata.py` |
| `1.2_LinkEntities.py` | `link_entities.py` |
| `1.3_BuildTenureMap.py` | `build_tenure_map.py` |
| `1.4_AssembleManifest.py` | `assemble_manifest.py` |
| `1.5_Utils.py` | `utils.py` |

### Renamed Stage 2 Scripts (2 files)

| Old Name | New Name |
|----------|----------|
| `tokenize_and_count.py` | `tokenize_transcripts.py` |
| `construct_variables.py` | `build_linguistic_variables.py` |

### Moved Financial Scripts (from v1/)

| Old Location | New Location |
|--------------|--------------|
| `financial/v1/3.0_BuildFinancialFeatures.py` | `financial/build_financial_features.py` |
| `financial/v1/3.1_FirmControls.py` | `financial/build_firm_controls.py` |
| `financial/v1/3.2_MarketVariables.py` | `financial/build_market_variables.py` |
| `financial/v1/3.3_EventFlags.py` | `financial/build_event_flags.py` |
| `financial/v1/3.4_Utils.py` | `financial/utils.py` |

---

## Files Modified

### Financial Scripts (Path Fixes)

After moving from `v1/` to parent directory, parent count in path resolution needed adjustment:

**`src/f1d/financial/build_firm_controls.py`:**
- Changed `parent.parent.parent.parent.parent` to `parent.parent.parent.parent` (3 occurrences)
- Fixed CCCL path from `CCCL instrument` to `CCCL_instrument`

**`src/f1d/financial/build_market_variables.py`:**
- Changed parent count from 5 to 4 (3 occurrences)
- Fixed hardcoded path from `1.0_BuildSampleManifest` to `1.4_AssembleManifest`

**`src/f1d/text/build_linguistic_variables.py`:**
- Fixed hardcoded path from `1.0_BuildSampleManifest` to `1.4_AssembleManifest`

---

## Files Deleted

### Dead Stage 2 Scripts

| File | Reason |
|------|--------|
| `src/f1d/text/construct_variables.py` | Replaced by `build_linguistic_variables.py` |
| `src/f1d/text/report_step2.py` | Dead code, no longer used |
| `src/f1d/text/verify_step2.py` | Dead code, no longer used |
| `src/f1d/text/tokenize_and_count.py` | Renamed to `tokenize_transcripts.py` |

### Old Financial v1 Directory

The entire `src/f1d/financial/v1/` directory was deleted after scripts were moved to parent.

---

## Key Learnings

### 1. Never Hardcode Timestamp Directories

**Problem:** Referencing specific output folders like `outputs/2026-02-19_153954/` breaks reproducibility.

**Solution:** Use config-based path resolution that finds the directory with most matching files.

```python
# BAD
path = root_path / "outputs/2026-02-19_153954/panel.parquet"

# GOOD
config = {"source": "outputs/variables", "file_pattern": "panel_{year}.parquet"}
builder = VariableBuilder(config)
path = builder.resolve_source_dir(root_path)  # Finds latest automatically
```

### 2. Parent Directory Counts Are Fragile

**Problem:** Moving scripts changes relative paths to project root.

**Solution:** Use a consistent method to find project root:

```python
# Instead of counting parents:
root_path = Path(__file__).parent.parent.parent.parent

# Consider adding a marker file and searching upward:
def find_project_root() -> Path:
    path = Path(__file__).resolve()
    while path.parent != path:
        if (path / "config" / "project.yaml").exists():
            return path
        path = path.parent
    raise RuntimeError("Project root not found")
```

### 3. Variable Builder Pattern Is Extensible

The `VariableBuilder` base class makes it easy to add new variables:

1. Create new module in `src/f1d/shared/variables/`
2. Inherit from `VariableBuilder`
3. Implement `build()` method
4. Add config entry in `variables.yaml`
5. Register in `__init__.py`

### 4. Accounting Review LaTeX Format

Key requirements for publication-ready tables:
- No vertical lines
- Two subcolumns per model: Estimate and t-value (NOT coefficient with SE in parentheses)
- **NO significance stars**
- Multi-panel tables with `\multicolumn{7}{l}{\textit{Panel X: ...}}`
- Sparse horizontal rules (toprule, midrule, cmidrule, bottomrule)

---

## Bugs Fixed

### Bug 1: stats_list_to_dataframe Type Error

**Error:** `stats_list_to_dataframe()` expected VariableStats instances but received dicts.

**Fix:** Updated function to handle both types with isinstance check:

```python
def stats_list_to_dataframe(stats_list: list) -> pd.DataFrame:
    rows = []
    for s in stats_list:
        if isinstance(s, VariableStats):
            rows.append(asdict(s))
        else:
            rows.append(s)  # Already a dict
    return pd.DataFrame(rows)
```

### Bug 2: Financial Variables Loading 0 Rows

**Error:** `resolve_source_dir()` found wrong directory because it just checked existence.

**Fix:** Rewrote to find directory with MOST matching files:

```python
def resolve_source_dir(self, root_path: Path) -> Path:
    # ... find subdirectory with most files matching pattern
    best_dir = None
    best_count = 0
    for subdir in subdirs:
        count = len(list(subdir.glob(glob_pattern)))
        if count > best_count:
            best_count = count
            best_dir = subdir
```

### Bug 3: Wrong Parent Count After Move

**Error:** Scripts moved from `v1/` to parent directory but path resolution still used 5 parents.

**Fix:** Changed to 4 parents:

```python
# Before (in v1/ subdirectory)
root_path = Path(__file__).parent.parent.parent.parent.parent

# After (in parent directory)
root_path = Path(__file__).parent.parent.parent.parent
```

### Bug 4: CCCL Path with Space vs Underscore

**Error:** Script used "CCCL instrument" but folder is "CCCL_instrument".

**Fix:** Updated path string.

### Bug 5: Old Manifest Path Reference

**Error:** `build_market_variables.py` used `1.0_BuildSampleManifest` instead of `1.4_AssembleManifest`.

**Fix:** Updated to correct path.

---

## Next Steps

### Immediate (Before Extending to Other Hypotheses)

1. **Verify all Stage 1-3 scripts work** with renamed paths
2. **Run full pipeline** from scratch to verify reproducibility
3. **Update any remaining hardcoded paths** in v2 scripts

### Short Term (Extend Architecture)

Create variable modules and test scripts for remaining hypotheses:

| Hypothesis | Test Script | Variables Needed |
|------------|-------------|------------------|
| H1: Cash Holdings | `test_cash_holdings.py` | CashRatio, CashFlow, Size, Leverage, etc. |
| H2: Investment Efficiency | `test_investment_efficiency.py` | Investment, TobinQ, CashFlow, etc. |
| H3: Payout Policy | `test_payout_policy.py` | Dividends, Repurchases, Earnings, etc. |
| H4: Leverage Discipline | `test_leverage_discipline.py` | Leverage, Debt Issuance, etc. |
| H5: Analyst Dispersion | `test_analyst_dispersion.py` | Dispersion, Forecast Error, etc. |
| H6: CCCL | `test_cccl.py` | CCCL components, Crash Risk, etc. |
| H7: Illiquidity | `test_illiquidity.py` | Amihud Illiquidity, Volume, etc. |
| H8: Takeover | `test_takeover.py` | Takeover indicators, etc. |
| H9: CEO Style | `test_ceo_style.py` | Style factors, etc. |

### Long Term (Architecture Improvements)

1. **Create base hypothesis test class** in `src/f1d/econometric/base.py`
2. **Add schema validation** for variable config
3. **Create CLI interface** for running specific hypotheses
4. **Add automated testing** for each hypothesis
5. **Document all variables** in a central catalog

---

## Verification Checklist

### Stage 3 Verification

- [x] All 9 variables load successfully
- [x] Panel has 112,968 rows (matches manifest)
- [x] Panel has 17 columns (all expected variables)
- [x] Sample distribution is correct:
  - Main: 88,205 calls
  - Finance: 20,482 calls
  - Utility: 4,281 calls
- [x] Summary stats CSV generated
- [x] Report markdown generated

### Stage 4 Verification

- [x] Panel loads from Stage 3
- [x] Complete cases filter works (72,608 rows)
- [x] Regressions run for all 3 samples
- [x] Manager fixed effects extracted
- [x] ClarityManager scores standardized (mean=0, std=1)
- [x] LaTeX table generated
- [x] Report markdown generated

### Results Match Expected

| Sample | N Obs | N Managers | R² | Status |
|--------|-------|------------|-----|--------|
| Main | 56,060 | 2,539 | 0.4105 | ✅ |
| Finance | 12,852 | 548 | 0.3052 | ✅ |
| Utility | 2,950 | 134 | 0.2172 | ✅ |

---

## Appendix: Variable Configuration

Full `config/variables.yaml` structure:

```yaml
# Stage 1 outputs
manifest:
  stage: 1
  source: "outputs/1.4_AssembleManifest"
  file_name: "master_sample_manifest.parquet"

# Stage 2 outputs (linguistic variables)
manager_qa_uncertainty:
  stage: 2
  source: "outputs/2_Textual_Analysis/2.2_Variables"
  file_pattern: "linguistic_variables_{year}.parquet"
  column: "Manager_QA_Uncertainty_pct"

manager_pres_uncertainty:
  stage: 2
  source: "outputs/2_Textual_Analysis/2.2_Variables"
  file_pattern: "linguistic_variables_{year}.parquet"
  column: "Manager_Pres_Uncertainty_pct"

analyst_qa_uncertainty:
  stage: 2
  source: "outputs/2_Textual_Analysis/2.2_Variables"
  file_pattern: "linguistic_variables_{year}.parquet"
  column: "Analyst_QA_Uncertainty_pct"

negative_sentiment:
  stage: 2
  source: "outputs/2_Textual_Analysis/2.2_Variables"
  file_pattern: "linguistic_variables_{year}.parquet"
  column: "Entire_All_Negative_pct"

# Stage 3 outputs (financial variables)
stock_return:
  stage: 3
  source: "outputs/3_Financial_Features"
  file_pattern: "market_variables_{year}.parquet"
  column: "StockRet"

market_return:
  stage: 3
  source: "outputs/3_Financial_Features"
  file_pattern: "market_variables_{year}.parquet"
  column: "MarketRet"

eps_growth:
  stage: 3
  source: "outputs/3_Financial_Features"
  file_pattern: "firm_controls_{year}.parquet"
  column: "EPS_Growth"

earnings_surprise:
  stage: 3
  source: "outputs/3_Financial_Features"
  file_pattern: "firm_controls_{year}.parquet"
  column: "SurpDec"
```

---

## Appendix: Running the Pipeline

```bash
# Stage 1: Sample assembly
python -m f1d.sample.build_sample_manifest
python -m f1d.sample.clean_metadata
python -m f1d.sample.link_entities
python -m f1d.sample.build_tenure_map
python -m f1d.sample.assemble_manifest

# Stage 2: Text processing
python -m f1d.text.tokenize_transcripts
python -m f1d.text.build_linguistic_variables

# Stage 3: Financial features
python -m f1d.financial.build_firm_controls
python -m f1d.financial.build_market_variables

# NEW Stage 3: Panel building
python -m f1d.variables.build_manager_clarity_panel

# NEW Stage 4: Hypothesis test
python -m f1d.econometric.test_manager_clarity
```

---

*End of Report*
