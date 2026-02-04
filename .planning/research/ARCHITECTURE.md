# Architecture Patterns: Hypothesis Testing Integration

**Domain:** F1D Data Pipeline - Econometric Analysis
**Researched:** 2026-02-04
**Focus:** Integrating hypothesis testing (H1-H3) with existing 4-stage pipeline

## Executive Summary

The F1D pipeline follows a clean 4-stage architecture (Sample -> Text -> Financial -> Econometric) with shared modules providing reusable patterns. Hypothesis testing scripts integrate naturally into Stage 4 (Econometric), following established patterns for FE regression, 2SLS, and subsample analysis. **No fundamental architecture changes required** - new scripts follow existing conventions and leverage existing shared modules.

## Current Architecture

### Pipeline Structure

```
2_Scripts/
  1_Sample/         # Stage 1: Sample construction
    1.0_BuildSampleManifest.py
    1.1_CleanMetadata.py
    1.2_LinkEntities.py
    1.3_BuildTenureMap.py
    1.4_AssembleManifest.py
    
  2_Text/           # Stage 2: Text processing
    2.1_TokenizeAndCount.py
    2.2_ConstructVariables.py
    2.3_Report.py
    
  3_Financial/      # Stage 3: Financial features
    3.0_BuildFinancialFeatures.py
    3.1_FirmControls.py
    3.2_MarketVariables.py
    3.3_EventFlags.py
    
  4_Econometric/    # Stage 4: Regression analysis
    4.1_EstimateCeoClarity.py          # Base FE regression
    4.1.1_EstimateCeoClarity_CeoSpecific.py
    4.1.2_EstimateCeoClarity_Extended.py
    4.1.3_EstimateCeoClarity_Regime.py
    4.1.4_EstimateCeoTone.py
    4.2_LiquidityRegressions.py        # OLS + 2SLS with IV
    4.3_TakeoverHazards.py             # Cox PH survival
    4.4_GenerateSummaryStats.py
    
  shared/           # Reusable modules
    path_utils.py
    dependency_checker.py
    regression_utils.py
    regression_helpers.py
    regression_validation.py
    data_loading.py
    observability_utils.py
    reporting_utils.py
```

### Data Flow Pattern

```
1_Inputs/
    |
    v
4_Outputs/1.x_Sample/      <- manifest, ceo_id, gvkey, ff12_code
    |
    v
4_Outputs/2.x_Text/        <- linguistic_variables_{year}.parquet
    |                         (uncertainty_pct, negative_pct, etc.)
    v
4_Outputs/3.x_Financial/   <- firm_controls_{year}.parquet
    |                         market_variables_{year}.parquet
    v
4_Outputs/4.x_Econometric/ <- ceo_clarity_scores.parquet
                              regression_results_{sample}.txt
                              model_diagnostics.csv
```

### Key Conventions

| Pattern | Convention | Example |
|---------|------------|---------|
| Script naming | `{step}_{substep}_{Name}.py` | `4.1.3_EstimateCeoClarity_Regime.py` |
| Output dirs | `4_Outputs/{step}_{Name}/{timestamp}/` | `4_Outputs/4.1_CeoClarity/2026-02-04_123456/` |
| Log dirs | `3_Logs/{step}_{Name}/{timestamp}/` | `3_Logs/4.1_CeoClarity/2026-02-04_123456/` |
| Latest resolution | Timestamp-sorted directories (no symlinks) | `get_latest_output_dir()` |
| Prerequisite check | `dependency_checker.validate_prerequisites()` | Check 4.1 before 4.2 |
| Merge key | `file_name` for call-level, `ceo_id` for CEO-level | All merges use these keys |

## Shared Modules Analysis

### Existing Modules (Reuse Directly)

| Module | Purpose | Integration Notes |
|--------|---------|-------------------|
| `path_utils.py` | `get_latest_output_dir()`, path validation | Use for all file I/O |
| `dependency_checker.py` | `validate_prerequisites()` | Add prereqs for new scripts |
| `regression_utils.py` | `run_fixed_effects_ols()`, `extract_ceo_fixed_effects()` | Core FE pattern |
| `regression_validation.py` | `validate_columns()`, `validate_sample_size()` | Pre-regression validation |
| `regression_helpers.py` | `build_regression_sample()`, filters | Sample construction |
| `data_loading.py` | `load_all_data()` | Multi-source data merge |
| `observability_utils.py` | `DualWriter`, stats, checksums | Logging pattern |
| `reporting_utils.py` | Reports, diagnostics | Output generation |

### New Module Needed

```python
# shared/hypothesis_utils.py (NEW)
"""
Hypothesis testing utilities for H1-H3 regressions.

Purpose:
  - Subsample splitting by manager tenure
  - Additional outcome variable construction
  - 2SLS instrumentation helpers
  - FE decomposition analysis
"""

def split_by_manager_tenure(df: pd.DataFrame, 
                           tenure_thresholds: list = [3, 5, 10]) -> dict:
    """Split sample by manager tenure for subsample analysis."""
    pass

def construct_cash_holdings_vars(df: pd.DataFrame) -> pd.DataFrame:
    """Construct cash holdings outcome variables (H1)."""
    pass

def construct_investment_efficiency_vars(df: pd.DataFrame) -> pd.DataFrame:
    """Construct investment efficiency outcome variables (H2)."""
    pass

def construct_payout_stability_vars(df: pd.DataFrame) -> pd.DataFrame:
    """Construct payout stability outcome variables (H3)."""
    pass

def run_iv_regression(df: pd.DataFrame, 
                      dep_var: str,
                      endog_var: str,
                      instrument: str,
                      exog_vars: list) -> dict:
    """Run 2SLS IV regression with diagnostics."""
    pass

def decompose_manager_fe(model, ceo_col: str = "ceo_id") -> pd.DataFrame:
    """Decompose manager fixed effects into clarity scores."""
    pass
```

**Rationale:** While `regression_utils.py` handles basic FE OLS, hypothesis testing requires additional utilities for subsample analysis, IV regression, and outcome construction that don't fit the existing module scope.

## Integration Points

### 1. Manager Fixed Effects (Extension of 4.1 Pattern)

**Existing pattern in 4.1_EstimateCeoClarity.py:**
```python
# Extract CEO fixed effects
ceo_params = {p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")}
ceo_fe["ClarityCEO"] = -ceo_fe["gamma_i"]  # Standardized
```

**New scripts follow identical pattern:**
- `4.5_EstimateManagerUncertainty.py` - Same FE extraction, different dependent variable
- Store output in same format: `ceo_clarity_scores.parquet` compatible schema

### 2. 2SLS Instrumentation (Extension of 4.2 Pattern)

**Existing pattern in 4.2_LiquidityRegressions.py:**
```python
from linearmodels.iv import IV2SLS

# First stage: Endogenous ~ Instrument + Controls
first_stage = smf.ols(formula, data=df).fit()
kp_f = first_stage.fvalue  # Kleibergen-Paap F-stat

# Second stage: IV2SLS
model = IV2SLS(y, exog, endog, instruments).fit(cov_type="robust")
```

**H1-H3 scripts use identical pattern:**
- Same instrument: `shift_intensity_sale_ff48` (CCCL)
- Same validation: F-stat > 10 for strong instrument
- First stage + 2SLS in separate phases

### 3. Subsample Analysis (Extension of 4.1.3 Pattern)

**Existing pattern in 4.1.3_EstimateCeoClarity_Regime.py:**
```python
CONFIG = {
    "samples": {
        "Main": {"exclude_ff12": [8, 11], "include_ff12": None},
        "Finance": {"exclude_ff12": None, "include_ff12": [11]},
        "Utility": {"exclude_ff12": None, "include_ff12": [8]},
    }
}

for sample_name in ["Main", "Finance", "Utility"]:
    df_sample = df[df["sample"] == sample_name].copy()
    # Run regression on subsample
```

**H1-H3 add tenure-based subsamples:**
```python
CONFIG = {
    "samples": {
        "Main": {"exclude_ff12": [8, 11]},
        "EarlyTenure": {"tenure_max": 3},      # New
        "MidTenure": {"tenure_min": 3, "tenure_max": 7},  # New
        "LateTenure": {"tenure_min": 7},       # New
    }
}
```

### 4. Outcome Variables (Extension of 3.x Pattern)

**Existing pattern in 3.1_FirmControls.py:**
- Construct firm-level financial variables
- Output per-year parquet files
- Merge on `file_name`

**New H1-H3 outcomes constructed in 3.x (or new 3.5 step):**

| Hypothesis | Outcome Variable | Source | Construction |
|------------|------------------|--------|--------------|
| H1 | `CashHoldings` | Compustat | che / at |
| H1 | `ExcessCash` | Compustat | che/at - industry median |
| H2 | `InvestmentQ` | Compustat | capx / ppent regressed on q |
| H2 | `InvestmentEfficiency` | Compustat | Residual from investment-q regression |
| H3 | `PayoutStability` | Compustat | std(div + repurchase) / mean |

## New Scripts Specification

### Stage 3 Extensions (Financial Features)

```
3_Financial/
  3.5_HypothesisOutcomes.py  (NEW)
    - Inputs: Compustat annual, 1.4 manifest
    - Outputs: hypothesis_outcomes_{year}.parquet
      - file_name, gvkey, year
      - CashHoldings, ExcessCash
      - InvestmentQ, InvestmentEfficiency  
      - PayoutStability, PayoutVolatility
```

### Stage 4 Extensions (Econometric)

```
4_Econometric/
  4.5_CashHoldingsRegression.py  (NEW - H1)
    - Prerequisites: 4.1, 3.5
    - Model: CashHoldings ~ Uncertainty + ClarityFE + Controls + FE
    - Variants: OLS, 2SLS, subsample by tenure
    - Outputs: 4.5_CashHoldings/{timestamp}/
    
  4.6_InvestmentEfficiencyRegression.py  (NEW - H2)
    - Prerequisites: 4.1, 3.5
    - Model: InvestmentEfficiency ~ Uncertainty + ClarityFE + Controls + FE
    - Variants: OLS, 2SLS, subsample by tenure
    - Outputs: 4.6_InvestmentEfficiency/{timestamp}/
    
  4.7_PayoutStabilityRegression.py  (NEW - H3)
    - Prerequisites: 4.1, 3.5
    - Model: PayoutStability ~ Uncertainty + ClarityFE + Controls + FE
    - Variants: OLS, 2SLS, subsample by tenure
    - Outputs: 4.7_PayoutStability/{timestamp}/
    
  4.8_SubsampleAnalysis.py  (NEW - Cross-cutting)
    - Prerequisites: 4.5, 4.6, 4.7
    - Runs all H1-H3 regressions across tenure subsamples
    - Consolidates results for comparison
    - Outputs: 4.8_SubsampleAnalysis/{timestamp}/
    
  4.9_RobustnessTests.py  (NEW - Optional)
    - Alternative specifications
    - Placebo tests
    - Sensitivity analysis
```

## Dependency Graph

```
                    ┌──────────────────┐
                    │ 1.4_Manifest     │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         v                   v                   v
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 2.2_LingVars    │ │ 3.1_FirmCtrls   │ │ 3.5_HypOutcomes │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │  (NEW)
         └───────────────────┼───────────────────┘
                             │
                             v
                    ┌────────────────────┐
                    │ 4.1_CeoClarity     │
                    │  (Manager FE)      │
                    └────────┬───────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         v                   v                   v
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 4.5_CashHolding │ │ 4.6_InvestEff   │ │ 4.7_PayoutStab  │
│      (H1)       │ │      (H2)       │ │      (H3)       │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │  (NEW)
         └───────────────────┼───────────────────┘
                             │
                             v
                    ┌─────────────────┐
                    │ 4.8_Subsample   │
                    │    Analysis     │
                    └─────────────────┘
                             (NEW)
```

## Script Template for H1-H3

Based on existing 4.1 and 4.2 patterns, each hypothesis script follows:

```python
#!/usr/bin/env python3
"""
STEP 4.X: Hypothesis [N] - [Outcome] Regression
==============================================================================

Purpose:
    Test H[N]: [Statement]
    
Structure:
    Phase 1: OLS (baseline)
    Phase 2: 2SLS (instrumented)
    Phase 3: Subsample analysis

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - 4_Outputs/4.1_CeoClarity/latest/ceo_clarity_scores.parquet
    - 4_Outputs/3.5_HypothesisOutcomes/latest/hypothesis_outcomes_{year}.parquet

Outputs:
    - 4_Outputs/4.X_[Outcome]/{timestamp}/ols_results.txt
    - 4_Outputs/4.X_[Outcome]/{timestamp}/iv_results.txt
    - 4_Outputs/4.X_[Outcome]/{timestamp}/subsample_results.csv
    - 4_Outputs/4.X_[Outcome]/{timestamp}/model_diagnostics.csv
    - 4_Outputs/4.X_[Outcome]/{timestamp}/report_step4_X.md

Deterministic: true
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import argparse

# Standard imports (identical to 4.1, 4.2)
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from shared.regression_utils import run_fixed_effects_ols
from shared.regression_validation import validate_columns, validate_sample_size
from shared.path_utils import get_latest_output_dir, OutputResolutionError
from shared.observability_utils import DualWriter, print_stats_summary, save_stats
from shared.dependency_checker import validate_prerequisites
from shared.hypothesis_utils import run_iv_regression  # NEW module

# CONFIG follows 4.1 pattern
CONFIG = {
    "year_start": 2002,
    "year_end": 2018,
    "dependent_var": "[OUTCOME_VAR]",
    "uncertainty_var": "Manager_QA_Uncertainty_pct",
    "clarity_var": "ClarityCEO",
    "instrument": "shift_intensity_sale_ff48",
    "firm_controls": ["Size", "BM", "Lev", "ROA", ...],
    "samples": {
        "Main": {"exclude_ff12": [8, 11]},
        "EarlyTenure": {"tenure_max": 3},
        "LateTenure": {"tenure_min": 7},
    }
}

def check_prerequisites(root):
    required_steps = {
        "4.1_EstimateCeoClarity": "ceo_clarity_scores.parquet",
        "3.5_HypothesisOutcomes": "hypothesis_outcomes.parquet",  # NEW
    }
    validate_prerequisites({}, required_steps)

def load_data(root):
    # Pattern from 4.2_LiquidityRegressions.py
    pass

def run_ols_regression(df, sample_name, out_file):
    # Pattern from 4.2_LiquidityRegressions.py
    pass

def run_iv_regression(df, sample_name, out_file):
    # Pattern from 4.2_LiquidityRegressions.py
    pass

def main():
    # Standard initialization (identical to 4.1, 4.2)
    pass
```

## Build Order Recommendation

Based on dependency analysis, the recommended implementation order:

### Phase 1: Foundation (Week 1)
1. **3.5_HypothesisOutcomes.py** - Construct outcome variables for H1-H3
   - Cash holdings from Compustat
   - Investment efficiency calculation
   - Payout stability metrics
   - *Rationale: Data foundation needed before regressions*

2. **shared/hypothesis_utils.py** - Shared utilities
   - Subsample splitting logic
   - Additional regression helpers
   - *Rationale: Avoid code duplication across H1-H3 scripts*

### Phase 2: Core Hypotheses (Week 2)
3. **4.5_CashHoldingsRegression.py** (H1)
   - Start with simplest outcome
   - OLS + 2SLS structure
   - *Rationale: Establish pattern for H2, H3*

4. **4.6_InvestmentEfficiencyRegression.py** (H2)
   - Follow 4.5 pattern
   - Investment-specific controls
   - *Rationale: Similar structure to H1*

5. **4.7_PayoutStabilityRegression.py** (H3)
   - Follow 4.5/4.6 pattern
   - Payout-specific controls
   - *Rationale: Completes hypothesis set*

### Phase 3: Analysis (Week 3)
6. **4.8_SubsampleAnalysis.py**
   - Consolidate across H1-H3
   - Tenure-based splits
   - *Rationale: Cross-cutting analysis after individual hypotheses*

7. **4.9_RobustnessTests.py** (Optional)
   - Alternative specifications
   - Sensitivity analysis
   - *Rationale: Polish after core implementation*

## Component Boundaries

### Modified Components

| Component | Modification | Risk |
|-----------|--------------|------|
| `config/project.yaml` | Add step_45, step_46, step_47, step_48 sections | LOW - additive |
| `shared/__init__.py` | Export new hypothesis_utils | LOW - additive |

### New Components

| Component | Type | Dependencies |
|-----------|------|--------------|
| `shared/hypothesis_utils.py` | Shared module | regression_utils, regression_validation |
| `3_Financial/3.5_HypothesisOutcomes.py` | Script | 1.4 manifest, Compustat |
| `4_Econometric/4.5_CashHoldingsRegression.py` | Script | 4.1, 3.5, shared/* |
| `4_Econometric/4.6_InvestmentEfficiencyRegression.py` | Script | 4.1, 3.5, shared/* |
| `4_Econometric/4.7_PayoutStabilityRegression.py` | Script | 4.1, 3.5, shared/* |
| `4_Econometric/4.8_SubsampleAnalysis.py` | Script | 4.5, 4.6, 4.7 |

### Unchanged Components

All Stage 1, Stage 2, existing Stage 3 (3.0-3.4), and existing Stage 4 (4.1-4.4) scripts remain unchanged.

## Anti-Patterns to Avoid

Based on existing codebase patterns:

1. **Don't duplicate data loading logic** - Use `shared/data_loading.py` or extend it
2. **Don't skip prerequisite validation** - Always call `validate_prerequisites()`
3. **Don't hardcode paths** - Use `get_latest_output_dir()` for timestamp resolution
4. **Don't skip dual logging** - Use `DualWriter` for all scripts
5. **Don't create new merge keys** - Use `file_name` (call-level) or `ceo_id` (CEO-level)
6. **Don't skip regression validation** - Use `validate_columns()` and `validate_sample_size()`

## Scalability Considerations

| Concern | Current Scale | At 10x Scale | Mitigation |
|---------|---------------|--------------|------------|
| Memory | ~6MB/year parquet | 60MB/year | Column pruning already implemented |
| I/O | 17 years × 3 files | Same | LRU cache in place (4.1) |
| Regression time | ~60s per model | Same | Not I/O bound |
| Output size | ~1MB per step | ~10MB | Timestamped dirs handle this |

## Sources

- Direct code analysis of existing scripts (HIGH confidence)
- `config/project.yaml` configuration structure (HIGH confidence)
- Existing shared module implementations (HIGH confidence)
- No external sources needed - architecture derived from codebase

## Quality Gate Checklist

- [x] Integration points clearly identified (4.1 FE pattern, 4.2 2SLS pattern, 4.1.3 subsample pattern)
- [x] New vs modified components explicit (table above)
- [x] Build order considers existing dependencies (3-phase rollout)
- [x] Data flow documented (dependency graph)
- [x] Shared module reuse maximized (6 existing modules)
- [x] New shared module justified (hypothesis_utils.py)
