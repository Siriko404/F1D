# Large File Analysis and Splitting Strategy Discovery

**Plan:** 77-12
**Type:** Research
**Created:** 2026-02-14
**Purpose:** Analyze large files with mixed responsibilities and document splitting strategy for Phase 78+

---

## Executive Summary

This document analyzes three large files identified in CONCERNS.md as exceeding 1000+ lines with mixed responsibilities:

| File | Lines | Functions | Primary Issue |
|------|-------|-----------|---------------|
| `src/f1d/shared/observability/stats.py` | 5,304 | 57 | Monolithic statistics module serving 5+ pipeline stages |
| `2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py` | 1,767 | 22 | Data prep + regression + output generation combined |
| `2_Scripts/3_Financial_V2/3.2_H2Variables.py` | 1,700 | 29 | Multiple variable construction functions in single file |

**Recommendation:** Defer all splitting work to Phase 78+ due to:
1. High complexity and risk (especially stats.py with 7 import sites)
2. Need for comprehensive test coverage before refactoring
3. Current codebase stability for thesis work

---

## 1. stats.py Analysis

### 1.1 Current State

**Location:** `src/f1d/shared/observability/stats.py`
**Line Count:** 5,304 lines
**Functions:** 57 functions (including wrappers)
**TypedDicts:** 6 type definitions

### 1.2 Function Groupings by Responsibility

The module contains functions serving multiple distinct pipeline stages:

#### Group A: Core Statistics Utilities (Lines 1-500)
```
- print_stat()          - Format and print statistics
- analyze_missing_values() - Missing value analysis
- print_stats_summary() - Print summary tables
- save_stats()          - Save to JSON
- calculate_throughput() - Rows/second calculation
- detect_anomalies_zscore() - Z-score anomaly detection
- detect_anomalies_iqr() - IQR anomaly detection
```
**Lines:** ~500
**Dependencies:** None (pure utility)
**Split Target:** `stats_core.py`

#### Group B: Generic Data Analysis (Lines 500-900)
```
- compute_input_stats()    - Input data characteristics
- compute_temporal_stats() - Temporal coverage analysis
- compute_entity_stats()   - Entity/quality characteristics
```
**Lines:** ~400
**Dependencies:** Group A
**Split Target:** `stats_analysis.py`

#### Group C: Sample Construction Stats (Lines 900-1500)
```
- compute_linking_input_stats()    - Entity linking input
- compute_linking_process_stats()  - 4-tier matching analysis
- compute_linking_output_stats()   - Linked entity characteristics
- collect_fuzzy_match_samples()    - Fuzzy match examples
- collect_tier_match_samples()     - Tier 1/2 examples
- collect_unmatched_samples()      - Unmatched company examples
- collect_before_after_samples()   - Before/after linking examples
```
**Lines:** ~600
**Dependencies:** Group A, B
**Split Target:** `stats_sample.py`

#### Group D: CEO Tenure Stats (Lines 1500-2100)
```
- compute_tenure_input_stats()   - Execucomp input analysis
- compute_tenure_process_stats() - Episode construction analysis
- compute_tenure_output_stats()  - Monthly panel characteristics
- collect_tenure_samples()       - Tenure episode examples
```
**Lines:** ~600
**Dependencies:** Group A, B
**Split Target:** `stats_tenure.py`

#### Group E: Manifest Assembly Stats (Lines 2100-2500)
```
- compute_manifest_input_stats()   - Input data characteristics
- compute_manifest_process_stats() - Merge/filter analysis
- compute_manifest_output_stats()  - Final manifest characteristics
- collect_ceo_distribution_samples() - CEO distribution examples
```
**Lines:** ~400
**Dependencies:** Group A, B
**Split Target:** `stats_manifest.py`

#### Group F: Text Processing Stats (Lines 2550-3000)
```
- compute_tokenize_input_stats()   - LM dictionary analysis
- compute_tokenize_process_stats() - Tokenization performance
- compute_tokenize_output_stats()  - Category distributions
```
**Lines:** ~450
**Dependencies:** Group A
**Split Target:** `stats_text.py`

#### Group G: Variable Construction Stats (Lines 3000-3400)
```
- compute_constructvariables_input_stats()   - Input for variable construction
- compute_constructvariables_process_stats() - Process metrics
- compute_constructvariables_output_stats()  - Output distributions
```
**Lines:** ~400
**Dependencies:** Group A
**Split Target:** `stats_variables.py`

#### Group H: Financial Variables Stats (Lines 3400-4200)
```
- compute_financial_input_stats()   - Compustat/IBES/CCCL analysis
- compute_financial_process_stats() - Merge success rates
- compute_financial_output_stats()  - Variable distributions
- compute_market_input_stats()      - CRSP data analysis
- compute_market_process_stats()    - Return computation coverage
- compute_market_output_stats()     - Market variable stats
- compute_event_flags_input_stats() - SDC M&A analysis
- compute_event_flags_process_stats() - Takeover detection
- compute_event_flags_output_stats() - Event flag stats
```
**Lines:** ~800
**Dependencies:** Group A, B
**Split Target:** `stats_financial.py`

#### Group I: Step 3 Wrapper Functions (Lines 4400-5300)
```
- compute_step31_input_stats()   - Step 3.1 input analysis
- compute_step31_process_stats() - Step 3.1 process analysis
- compute_step31_output_stats()  - Step 3.1 output analysis
- compute_step32_input_stats()   - Step 3.2 input analysis
- compute_step32_process_stats() - Step 3.2 process analysis
- compute_step32_output_stats()  - Step 3.2 output analysis
- compute_step33_input_stats()   - Step 3.3 input analysis
- compute_step33_process_stats() - Step 3.3 process analysis
- compute_step33_output_stats()  - Step 3.3 output analysis
```
**Lines:** ~900
**Dependencies:** Groups A-H
**Split Target:** Keep in `stats.py` as orchestrator

### 1.3 Proposed Module Structure

```
src/f1d/shared/observability/
    __init__.py              # Re-exports all public functions
    stats.py                  # Core utilities + wrapper orchestration (~800 lines)
    stats_core.py             # Basic utilities (~300 lines)
    stats_analysis.py         # Generic analysis functions (~400 lines)
    stats_sample.py           # Sample construction stats (~600 lines)
    stats_tenure.py           # CEO tenure stats (~600 lines)
    stats_manifest.py         # Manifest assembly stats (~400 lines)
    stats_text.py             # Text processing stats (~450 lines)
    stats_variables.py        # Variable construction stats (~400 lines)
    stats_financial.py        # Financial/market/event stats (~800 lines)
    types_stats.py            # TypedDict definitions (~200 lines)
```

### 1.4 Import Call Sites

The following files import from `f1d.shared.observability.stats`:

1. **`src/f1d/shared/observability/__init__.py`** (Line 50)
   - Imports and re-exports functions
   - Impact: LOW - update re-exports after split

2. **`2_Scripts/shared/observability/__init__.py`** (Line 52)
   - Duplicate copy for legacy 2_Scripts path
   - Impact: MEDIUM - needs sync after split

3. **`tests/unit/test_stats_module.py`** (Line 27)
   - Test file imports specific functions
   - Impact: LOW - update imports

4. **`.planning/research/STACK.md`** (Line 218)
   - Documentation example
   - Impact: NONE - documentation only

5. **`.planning/research/PITFALLS.md`** (Line 73)
   - Documentation example
   - Impact: NONE - documentation only

### 1.5 Dependencies Between Sections

```
                    types_stats.py
                          |
                          v
    +------------------- stats_core.py -------------------+
    |                        |                            |
    v                        v                            v
stats_analysis.py     stats_text.py              stats_variables.py
    |                        |                            |
    +----------+-------------+--------------+-------------+
               |                            |
               v                            v
    +----- stats_sample.py            stats_financial.py -----+
    |           |                            |                 |
    |           v                            v                 |
    |    stats_tenure.py              stats_financial.py       |
    |           |                            |                 |
    |           +-------------+--------------+                 |
    |                         |                                |
    +-------------------------+--------------------------------+
                              |
                              v
                       stats.py (orchestrator)
                              |
                              v
                       __init__.py (re-exports)
```

### 1.6 Risks Identified

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking existing imports | HIGH | Keep `__init__.py` re-exports, deprecate gradually |
| Circular imports | MEDIUM | Use lazy imports, TYPE_CHECKING patterns |
| Type checking regressions | MEDIUM | Comprehensive mypy testing before/after |
| Test coverage gaps | HIGH | Require 90%+ coverage on each new module before split |
| Documentation drift | LOW | Update docstrings during split |

---

## 2. H4_LeverageDiscipline.py Analysis

### 2.1 Current State

**Location:** `2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py`
**Line Count:** 1,767 lines
**Functions:** 22 functions
**Purpose:** H4 hypothesis - Does leverage discipline managers to reduce speech uncertainty?

### 2.2 Function Groupings by Responsibility

#### Group A: Configuration and Setup (Lines 1-160)
```python
- load_config()     - Load project.yaml
- get_git_sha()     - Get current commit for reproducibility
- UNCERTAINTY_MEASURES, ANALYST_UNCERTAINTY_VAR, FINANCIAL_CONTROLS, VIF_COLUMNS (constants)
```
**Lines:** ~160
**Split Target:** `h4_config.py`

#### Group B: Statistical Helpers (Lines 160-350)
```python
- one_tailed_pvalue()        - Calculate one-tailed p-value
- run_all_h4_regressions()   - Run 6 regressions (one per DV)
- save_regression_results()  - Save to parquet/JSON
- generate_h4_summary()      - Generate H4_RESULTS.md
- generate_latex_table()     - Generate LaTeX coefficient table
```
**Lines:** ~190
**Split Target:** `h4_regression.py`

#### Group C: Path Setup (Lines 700-750)
```python
- setup_paths()    - Resolve directories, create output paths
```
**Lines:** ~50
**Split Target:** Keep in main script

#### Group D: Data Loading (Lines 750-850)
```python
- load_h1_variables()         - Load leverage and controls
- load_h3_variables()         - Load firm_maturity, earnings_volatility
- load_speech_uncertainty()   - Load linguistic variables
```
**Lines:** ~100
**Split Target:** `h4_data.py`

#### Group E: Variable Preparation (Lines 850-940)
```python
- create_lagged_leverage()     - Create Leverage(t-1)
- aggregate_speech_to_firmyear() - Aggregate call-level to firm-year
```
**Lines:** ~90
**Split Target:** `h4_data.py`

#### Group F: Data Preparation (Lines 940-1200)
```python
- prepare_analysis_dataset() - Merge all sources, VIF diagnostics
```
**Lines:** ~260
**Split Target:** `h4_data.py`

#### Group G: Main Execution (Lines 1200-1767)
```python
- parse_arguments()        - CLI argument parsing
- check_prerequisites()    - Validate input files
- main()                   - Orchestrate execution
```
**Lines:** ~567
**Split Target:** Keep in main script

### 2.3 Proposed Module Structure

```
2_Scripts/4_Econometric_V2/
    4.4_H4_LeverageDiscipline.py    # Main script (~600 lines)
    h4_config.py                     # Constants and config (~160 lines)
    h4_data.py                       # Data loading and prep (~450 lines)
    h4_regression.py                 # Regression functions (~190 lines)
```

### 2.4 Import Call Sites

Files referencing H4:

1. **`src/f1d/econometric/v2/4.2_H2InvestmentEfficiencyRegression.py`** - Related hypothesis script
2. **`tests/verification/test_stage4_dryrun.py`** - Dry-run test
3. **`tests/unit/test_h4_regression.py`** - Unit tests
4. **`.planning/phases/39-leverage-speech-discipline/*`** - Phase 39 docs

### 2.5 Natural Split Points

The file has clear natural boundaries:

1. **After line 160** - Configuration section ends
2. **After line 350** - Regression functions section ends
3. **After line 700** - Path setup (small, keep with main)
4. **After line 850** - Data loading section ends
5. **After line 1200** - Data prep ends, main() begins

### 2.6 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking hypothesis reproducibility | HIGH | Full regression test before merge |
| VIF check failures | MEDIUM | Preserve exact computation order |
| Import cycle with shared modules | LOW | No shared dependencies within hypothesis |

---

## 3. H2Variables.py Analysis

### 3.1 Current State

**Location:** `2_Scripts/3_Financial_V2/3.2_H2Variables.py`
**Line Count:** 1,700 lines
**Functions:** 29 functions
**Purpose:** Construct H2 investment efficiency variables

### 3.2 Function Groupings by Responsibility

#### Group A: Configuration (Lines 1-150)
```python
- load_config()    - Load project.yaml
- setup_paths()    - Set up all required paths
```
**Lines:** ~150
**Split Target:** Keep in main script

#### Group B: Data Loading (Lines 150-300)
```python
- load_manifest()      - Load sample manifest
- load_compustat_h2()  - Load Compustat with required columns
- load_ibes()          - Load IBES analyst forecasts
- build_ff_mappings()  - Build Fama-French mappings
```
**Lines:** ~150
**Split Target:** `h2_data.py`

#### Group C: Industry Classification (Lines 300-330)
```python
- assign_ff_industries() - Assign FF12/FF48 to observations
```
**Lines:** ~30
**Split Target:** `h2_data.py`

#### Group D: Over/Underinvestment (Lines 330-500)
```python
- compute_capex_dp()              - Capex/Depreciation ratio
- compute_sales_growth()          - Sales growth rate
- compute_industry_year_median()  - Industry-year median
- compute_overinvest_dummy()      - Overinvestment classification
- compute_underinvest_dummy()     - Underinvestment classification
- enforce_mutual_exclusivity()    - Ensure dummies exclusive
```
**Lines:** ~170
**Split Target:** `h2_efficiency.py`

#### Group E: Efficiency Score (Lines 500-560)
```python
- compute_efficiency_score() - 5-year rolling efficiency
```
**Lines:** ~60
**Split Target:** `h2_efficiency.py`

#### Group F: Biddle ROA Residual (Lines 560-670)
```python
- compute_delta_roa()      - Delta ROA (t+2 - t)
- compute_roa_residuals()   - Biddle regression residuals
```
**Lines:** ~110
**Split Target:** `h2_efficiency.py`

#### Group G: Analyst Dispersion (Lines 670-740)
```python
- link_ibes_to_compustat()     - CUSIP matching
- compute_analyst_dispersion() - STDEV/|MEANEST|
```
**Lines:** ~70
**Split Target:** `h2_analyst.py`

#### Group H: Control Variables (Lines 740-930)
```python
- compute_tobins_q()             - (AT + ME - CEQ) / AT
- compute_cf_volatility()        - 5-year rolling OCF/AT std
- compute_industry_capex_intensity() - Industry mean capex/AT
- compute_firm_size()            - ln(AT)
- compute_roa()                  - IB/AT
- compute_fcf()                  - (OANCF - CAPX)/AT
- compute_earnings_volatility()  - 5-year rolling ROA std
```
**Lines:** ~190
**Split Target:** `h2_controls.py`

#### Group I: Utilities (Lines 930-1010)
```python
- winsorize_series()      - Winsorize at 1%/99%
- parse_arguments()       - CLI parsing
- check_prerequisites()   - Validate inputs
```
**Lines:** ~80
**Split Target:** Keep in main script

#### Group J: Main Execution (Lines 1010-1700)
```python
- main() - Full execution pipeline
```
**Lines:** ~690
**Split Target:** Keep in main script

### 3.3 Proposed Module Structure

```
2_Scripts/3_Financial_V2/
    3.2_H2Variables.py      # Main script (~700 lines)
    h2_data.py               # Data loading (~180 lines)
    h2_efficiency.py         # Over/under investment, efficiency, ROA residual (~340 lines)
    h2_analyst.py            # Analyst dispersion (~70 lines)
    h2_controls.py           # Control variables (~190 lines)
```

### 3.4 Import Call Sites

Files referencing H2Variables:

1. **`src/f1d/financial/v2/3.2_H2Variables.py`** - Duplicate in src/f1d/
2. **`src/f1d/econometric/v2/4.2_H2InvestmentEfficiencyRegression.py`** - Consumer of H2 variables
3. **`2_Scripts/3_Financial_V2/3.9_H2_BiddleInvestmentResidual.py`** - Related script
4. **`tests/verification/test_stage3_dryrun.py`** - Dry-run test

### 3.5 Natural Split Points

1. **After line 150** - Configuration ends
2. **After line 330** - Data loading ends
3. **After line 670** - Investment efficiency variables end
4. **After line 740** - Analyst dispersion ends
5. **After line 930** - Control variables end
6. **After line 1010** - Utilities end, main() begins

### 3.6 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking 4.2 regression dependency | HIGH | Verify downstream consumer |
| Rolling window computation changes | MEDIUM | Unit tests for each rolling function |
| IBES linking changes | LOW | Isolated in small function |
| Duplicate file sync (src/f1d) | HIGH | Split both simultaneously |

---

## 4. Phase 78 Roadmap: Large File Refactoring

### 4.1 Priority Order (Least Risk First)

| Priority | File | Lines | Risk Level | Estimated Effort |
|----------|------|-------|------------|------------------|
| 1 | `3.2_H2Variables.py` | 1,700 | LOW-MEDIUM | 2-3 plans, 1-2 days |
| 2 | `4.4_H4_LeverageDiscipline.py` | 1,767 | MEDIUM | 2-3 plans, 2-3 days |
| 3 | `stats.py` | 5,304 | HIGH | 5-7 plans, 5-7 days |

### 4.2 Phase 78 Plan Structure

#### Plan 78-01: H2Variables Split
- **Duration:** 1-2 days
- **Tasks:**
  1. Create `h2_data.py` with data loading functions
  2. Create `h2_efficiency.py` with investment efficiency functions
  3. Create `h2_analyst.py` with analyst dispersion
  4. Create `h2_controls.py` with control variables
  5. Update imports in main script
  6. Add unit tests for each new module
  7. Update `src/f1d/financial/v2/3.2_H2Variables.py` duplicate
- **Verification:** All existing tests pass, dry-run succeeds

#### Plan 78-02: H4_LeverageDiscipline Split
- **Duration:** 2-3 days
- **Tasks:**
  1. Create `h4_config.py` with constants and config loading
  2. Create `h4_data.py` with data loading and preparation
  3. Create `h4_regression.py` with regression functions
  4. Update imports in main script
  5. Add unit tests for each new module
  6. Update `src/f1d/econometric/v2/4.4_H4_LeverageDiscipline.py` duplicate
- **Verification:** All existing tests pass, regression results unchanged

#### Plans 78-03 to 78-07: stats.py Split (5 plans)
- **Duration:** 5-7 days
- **Tasks by Plan:**

  **78-03: Foundation**
  1. Extract `types_stats.py` with TypedDict definitions
  2. Extract `stats_core.py` with basic utilities
  3. Update `__init__.py` re-exports
  4. Add comprehensive tests

  **78-04: Analysis Functions**
  1. Extract `stats_analysis.py` with generic analysis
  2. Extract `stats_text.py` with tokenization stats
  3. Update imports in stats.py
  4. Add tests

  **78-05: Pipeline Stage Stats (Part 1)**
  1. Extract `stats_sample.py` with sample construction stats
  2. Extract `stats_tenure.py` with CEO tenure stats
  3. Update imports
  4. Add tests

  **78-06: Pipeline Stage Stats (Part 2)**
  1. Extract `stats_manifest.py` with manifest stats
  2. Extract `stats_variables.py` with variable construction stats
  3. Update imports
  4. Add tests

  **78-07: Financial Stats**
  1. Extract `stats_financial.py` with financial/market/event stats
  2. Update stats.py to use all extracted modules
  3. Comprehensive integration tests
  4. Update 2_Scripts duplicate
  5. Final verification

### 4.3 Risk Mitigation Requirements

Before any split:

1. **Test Coverage Gate:** 90%+ coverage on target module
2. **Type Check Gate:** mypy 0 errors on target module
3. **Import Map:** Complete map of all import sites
4. **Rollback Plan:** Git tag before each split for easy rollback
5. **Verification Script:** Script to compare outputs before/after

### 4.4 Success Criteria for Phase 78

- [ ] All three large files split into focused modules
- [ ] Each new module < 600 lines
- [ ] Test coverage maintained or improved
- [ ] mypy passes with 0 errors
- [ ] All dry-run tests pass
- [ ] All regression outputs identical to pre-split

---

## 5. Deferral Rationale

### 5.1 Why Defer to Phase 78+

1. **Codebase Stability Priority**
   - Current thesis work requires stable codebase
   - Splitting introduces risk of subtle bugs
   - Large refactoring better suited for post-thesis maintenance

2. **Test Coverage Gaps**
   - stats.py has only basic test coverage (see 77-10-SUMMARY)
   - H2 and H4 scripts have limited unit tests
   - Full coverage needed before safe refactoring

3. **Dependency Complexity**
   - stats.py imports from 7+ files across codebase
   - Changes ripple through entire pipeline
   - Requires coordinated testing across stages

4. **Risk/Benefit Analysis**
   - Current code is functional and documented
   - Splitting provides maintainability benefit but no new functionality
   - Risk of breaking existing research results

### 5.2 Conditions for Starting Phase 78

Phase 78 should only start when:

1. **Test Coverage:** All target files have 90%+ coverage
2. **Time Available:** At least 2 weeks of non-thesis time
3. **No Active Research:** No pending hypothesis tests or analysis
4. **Backup:** Complete backup/archive of working codebase

---

## 6. Conclusion

This discovery document provides a comprehensive analysis of the three large files identified for splitting in CONCERNS.md. The analysis shows:

- **stats.py** is the most complex (5,304 lines, 57 functions) with the most import sites
- **H4_LeverageDiscipline.py** has clear natural split points along data/regression boundaries
- **H2Variables.py** is self-contained with well-defined variable groupings

The recommended approach is to **defer all splitting to Phase 78+** to maintain codebase stability for thesis work. When Phase 78 begins, start with H2Variables (lowest risk), then H4 (medium risk), and finally stats.py (highest risk).

The detailed splitting strategies in this document provide a roadmap that can be executed incrementally with comprehensive testing at each step.

---

*Document created: 2026-02-14*
*Author: GSD Executor (77-12)*
