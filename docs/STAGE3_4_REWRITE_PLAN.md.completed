# Stage 3/4 Rewrite Plan: New Architecture for Variables and Econometric Pipeline

**Date Updated:** 2026-02-19
**Status:** Phase 1 COMPLETE (Manager Clarity Pilot) - Ready for Phase 2 (H1-H9)

---

## Executive Summary

The current Stage 3 (financial) and Stage 4 (econometric) architecture has significant issues:
- Messy organization with v1/v2 separation
- Inconsistent variable definitions across scripts
- Bugs and code quality issues
- No standardized output format

We are rewriting the pipeline with a new clean architecture:
- **Stage 3 → "variables"**: One script per hypothesis, uses shared variable modules
- **Stage 4 → "econometric"**: One script per hypothesis, outputs Accounting Review style LaTeX
- **Shared variable modules**: One file per variable, ensuring consistent definitions

This document captures the full design decisions, **completed implementation details**, and **detailed next steps** for extending to all other hypotheses.

---

## PILOT IMPLEMENTATION STATUS: ✅ COMPLETE

### Manager Clarity Test (4.1) - VERIFIED WORKING

**Commit:** `91ec198` - `refactor: implement new Stage 3/4 architecture for Manager Clarity pilot`

**Results:**
| Sample | N Obs | N Managers | R-squared | Status |
|--------|-------|------------|-----------|--------|
| Main | 56,060 | 2,539 | 0.4105 | ✅ |
| Finance | 12,852 | 548 | 0.3052 | ✅ |
| Utility | 2,950 | 134 | 0.2172 | ✅ |

**Run Commands:**
```bash
python -m f1d.variables.build_manager_clarity_panel
python -m f1d.econometric.test_manager_clarity
```

---

## Hypothesis Coverage

### V2 Hypotheses (H1-H9) - TO BE IMPLEMENTED

| Hypothesis | Test | V2 Script | V2 Variables Script | Status |
|------------|------|-----------|---------------------|--------|
| H1 | Cash Holdings | `4.1_H1CashHoldingsRegression.py` | `3.1_H1Variables.py` | 🔴 Pending |
| H2 | Investment Efficiency | `4.2_H2InvestmentEfficiencyRegression.py` | `3.2_H2Variables.py` | 🔴 Pending |
| H3 | Payout Policy | `4.3_H3PayoutPolicyRegression.py` | `3.3_H3Variables.py` | 🔴 Pending |
| H4 | Leverage Discipline | `4.4_H4_LeverageDiscipline.py` | (uses H1 variables) | 🔴 Pending |
| H5 | Analyst Dispersion | `4.5_H5DispersionRegression.py` | `3.5_H5Variables.py` | 🔴 Pending |
| H6 | CCCL (SEC Scrutiny) | `4.6_H6CCCLRegression.py` | `3.6_H6Variables.py` | 🔴 Pending |
| H7 | Stock Illiquidity | `4.7_H7IlliquidityRegression.py` | `3.7_H7IlliquidityVariables.py` | 🔴 Pending |
| H8 | Takeover | `4.8_H8TakeoverRegression.py` | `3.8_H8TakeoverVariables.py` | 🔴 Pending |
| H9 | CEO Style x PRisk | `4.11_H9_Regression.py` | `3.11_H9_StyleFrozen.py`, `3.12_H9_PRiskFY.py` | 🔴 Pending |

### V1 Tests - NOT YET REWRITTEN

| Test | Method | Description | Status |
|------|--------|-------------|--------|
| 4.1.x Clarity Estimation | Panel OLS with FE | Extract CEO/Manager fixed effects | ✅ Replaced by new `test_manager_clarity.py` |
| 4.2 Liquidity IV | 2SLS IV Regression | Communication effects on market liquidity | 🔴 Pending |
| 4.3 Takeover Hazards | Cox PH, Fine-Gray | Survival analysis for takeover timing | 🔴 Pending |
| 4.4 Summary Stats | Descriptive | Summary statistics generation | 🔴 Pending |

---

## Architecture Design (IMPLEMENTED)

### Folder Structure

```
src/f1d/
├── shared/
│   ├── variables/                    # ✅ IMPLEMENTED
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
│   │   └── manifest_fields.py
│   ├── latex_tables_accounting.py   # ✅ IMPLEMENTED
│   └── ... (existing shared modules)
│
├── variables/                        # ✅ IMPLEMENTED (pilot only)
│   ├── __init__.py
│   └── build_manager_clarity_panel.py
│
├── econometric/
│   ├── test_manager_clarity.py       # ✅ IMPLEMENTED (pilot only)
│   ├── v1/                           # OLD - kept for reference
│   └── v2/                           # OLD - to be replaced
│
├── sample/                           # ✅ RENAMED
│   ├── build_sample_manifest.py      # (was 1.0_BuildSampleManifest.py)
│   ├── clean_metadata.py             # (was 1.1_CleanMetadata.py)
│   ├── link_entities.py              # (was 1.2_LinkEntities.py)
│   ├── build_tenure_map.py           # (was 1.3_BuildTenureMap.py)
│   ├── assemble_manifest.py          # (was 1.4_AssembleManifest.py)
│   └── utils.py                      # (was 1.5_Utils.py)
│
├── text/                             # ✅ RENAMED
│   ├── tokenize_transcripts.py       # (was tokenize_and_count.py)
│   └── build_linguistic_variables.py # (was construct_variables.py)
│
└── financial/
    ├── build_firm_controls.py        # ✅ MOVED from v1/
    ├── build_market_variables.py     # ✅ MOVED from v1/
    ├── build_event_flags.py          # ✅ MOVED from v1/
    ├── build_financial_features.py   # ✅ MOVED from v1/
    ├── utils.py                      # ✅ MOVED from v1/
    └── v2/                           # OLD - to be replaced
```

### Configuration File

**`config/variables.yaml`** - Central configuration for all variable sources:

```yaml
variables:
  # Stage 1: Sample Manifest
  manifest:
    stage: 1
    source: "outputs/1.4_AssembleManifest"
    file_name: "master_sample_manifest.parquet"
    columns: [file_name, ceo_id, ceo_name, gvkey, ff12_code, ff12_name, start_date]

  # Stage 2: Text/Linguistic Variables
  manager_qa_uncertainty:
    stage: 2
    source: "outputs/2_Textual_Analysis/2.2_Variables"
    file_pattern: "linguistic_variables_{year}.parquet"
    column: "Manager_QA_Uncertainty_pct"

  # Stage 3: Financial Variables
  stock_return:
    stage: 3
    source: "outputs/3_Financial_Features"
    file_pattern: "market_variables_{year}.parquet"
    column: "StockRet"

hypothesis_tests:
  manager_clarity:
    dependent: "manager_qa_uncertainty"
    linguistic_controls: [manager_pres_uncertainty, analyst_qa_uncertainty, negative_sentiment]
    firm_controls: [stock_return, market_return, eps_growth, earnings_surprise]
    regression:
      min_calls_per_manager: 5
      fixed_effects: [ceo_id, year]
```

---

## IMPLEMENTATION DETAILS (Pilot: Manager Clarity)

### 1. Base Classes (`src/f1d/shared/variables/base.py`)

```python
@dataclass
class VariableStats:
    """Summary statistics for a variable."""
    name: str
    n: int
    mean: float
    std: float
    min: float
    p25: float
    median: float
    p75: float
    max: float
    n_missing: int
    pct_missing: float

@dataclass
class VariableResult:
    """Result from building a variable."""
    data: pd.DataFrame          # DataFrame with file_name and variable column(s)
    stats: VariableStats        # Summary statistics
    metadata: Dict[str, Any]    # Source, column name, etc.

class VariableBuilder:
    """Base class for variable builders."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build the variable for all years."""
        raise NotImplementedError

    def get_stats(self, series: pd.Series, name: str) -> VariableStats:
        """Compute summary statistics."""
        ...

    def resolve_source_dir(self, root_path: Path) -> Path:
        """Find directory with most matching files (auto-detects timestamp)."""
        # CRITICAL: This method finds the subdirectory with the MOST matching files
        # based on file_pattern or file_name, NOT hardcoded timestamps
        ...
```

### 2. Example Variable Builder (`manager_qa_uncertainty.py`)

```python
class ManagerQAUncertaintyBuilder(VariableBuilder):
    """Build Manager Q&A Uncertainty variable from Stage 2 outputs."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "Manager_QA_Uncertainty_pct")

    def build(self, years: range, root_path: Path) -> VariableResult:
        source_dir = self.resolve_source_dir(root_path)
        all_data: List[pd.DataFrame] = []

        for year in years:
            df = self.load_year_file(source_dir, year)
            if df is not None:
                cols = ["file_name"]
                if self.column in df.columns:
                    cols.append(self.column)
                all_data.append(df[cols])

        if not all_data:
            # Return empty result with proper schema
            return VariableResult(
                data=pd.DataFrame(columns=["file_name", self.column]),
                stats=VariableStats(name=self.column, n=0, ...),
                metadata={"source": str(source_dir), "column": self.column}
            )

        combined = pd.concat(all_data, ignore_index=True)
        stats = self.get_stats(combined[self.column], self.column)

        return VariableResult(
            data=combined[["file_name", self.column]],
            stats=stats,
            metadata={"source": str(source_dir), "column": self.column}
        )
```

### 3. Stage 3 Panel Builder (`build_manager_clarity_panel.py`)

Key sections:

```python
def build_panel(root_path, years, var_config, stats) -> pd.DataFrame:
    # Initialize builders
    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "manager_qa_uncertainty": ManagerQAUncertaintyBuilder(
            var_config.get("manager_qa_uncertainty", {})
        ),
        # ... all other builders
    }

    # Build all variables
    all_results = {}
    for name, builder in builders.items():
        result = builder.build(years, root_path)
        all_results[name] = result

    # Start with manifest as base
    panel = all_results["manifest"].data.copy()

    # Merge all other variables on file_name
    for name, result in all_results.items():
        if name == "manifest":
            continue
        panel = panel.merge(result.data, on="file_name", how="left")

    # Add derived fields
    panel["sample"] = assign_industry_sample(panel["ff12_code"])

    return panel
```

### 4. Stage 4 Test Script (`test_manager_clarity.py`)

Key configuration:

```python
CONFIG = {
    "dependent_var": "Manager_QA_Uncertainty_pct",
    "linguistic_controls": [
        "Manager_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
    ],
    "firm_controls": ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"],
    "min_calls_per_manager": 5,
}
```

Key regression function:

```python
def run_regression(df_sample, sample_name):
    # Filter to managers with minimum calls
    min_calls = CONFIG["min_calls_per_manager"]
    manager_counts = df_sample["ceo_id"].value_counts()
    valid_managers = set(manager_counts[manager_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_managers)].copy()

    # Build formula
    dep_var = CONFIG["dependent_var"]
    controls = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]
    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"

    # Estimate with robust SE
    model = smf.ols(formula, data=df_reg).fit(cov_type="HC1")

    return model, df_reg, valid_managers
```

### 5. LaTeX Table Generator (`latex_tables_accounting.py`)

Accounting Review format requirements:
- No vertical lines (booktabs style)
- Two subcolumns per model: **Estimate** and **t-value** (NOT coefficient with SE in parentheses)
- **NO significance stars**
- Multi-panel tables with `\multicolumn{N}{l}{\textit{Panel X: ...}}`
- Sparse horizontal rules (toprule, midrule, cmidrule, bottomrule)

---

## BUGS FIXED DURING IMPLEMENTATION

### Bug 1: `stats_list_to_dataframe` Type Error

**Problem:** Function expected `VariableStats` instances but received dicts.

**Fix in `base.py`:**
```python
def stats_list_to_dataframe(stats_list: List[Any]) -> pd.DataFrame:
    records = []
    for s in stats_list:
        if isinstance(s, dict):
            records.append(s)
        else:
            records.append(asdict(s))  # VariableStats instance
    return pd.DataFrame(records)
```

### Bug 2: Financial Variables Loading 0 Rows

**Problem:** `resolve_source_dir()` found wrong directory because it just checked existence.

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
    return best_dir if best_dir else source_path
```

### Bug 3: Wrong Parent Count After Script Move

**Problem:** Scripts moved from `v1/` to parent directory but path resolution still used 5 parents.

**Fix:** Changed from 5 to 4 parents in:
- `build_firm_controls.py`
- `build_market_variables.py`

### Bug 4: CCCL Path with Space vs Underscore

**Problem:** Script used "CCCL instrument" but folder is "CCCL_instrument".

**Fix:** Updated path string in `build_firm_controls.py`.

### Bug 5: Old Manifest Path Reference

**Problem:** `build_market_variables.py` used `1.0_BuildSampleManifest` instead of `1.4_AssembleManifest`.

**Fix:** Updated to correct path.

---

## Design Decisions (Confirmed)

### 1. Variable Config Location
- **Decision:** `config/variables.yaml` at project root (next to `project.yaml`)
- **Rationale:** Easy to find and modify; follows existing pattern

### 2. Shared Variable Modules
- **Decision:** One file per variable in `src/f1d/shared/variables/`
- **Rationale:** Ensures consistent definitions; reusable across hypotheses

### 3. Config-Based Path Resolution
- **Decision:** Scripts NEVER hardcode timestamp directories
- **Critical:** Use `resolve_source_dir()` which finds the directory with most matching files

### 4. Summary Stats Format
- **Decision:** CSV with columns: `name, n, mean, std, min, p25, median, p75, max, n_missing, pct_missing`

### 5. LaTeX Table Format
- **Decision:** Accounting Review style
- Two columns per model: Estimate AND t-value
- **NO significance stars**
- Multi-panel structure

### 6. Output Locations
- Stage 3: `outputs/variables/{hypothesis}/`
- Stage 4: `outputs/econometric/{hypothesis}/`

---

## NEXT STEPS: Extending to Other Hypotheses

### Overview

For each hypothesis H1-H9, follow this pattern:

1. **Read the existing V2 scripts** to understand model specification
2. **Identify required variables** from the V2 variables script
3. **Create new variable builders** in `src/f1d/shared/variables/` (or reuse existing)
4. **Update `config/variables.yaml`** with new variable definitions
5. **Create Stage 3 panel builder** in `src/f1d/variables/build_{hypothesis}_panel.py`
6. **Create Stage 4 test script** in `src/f1d/econometric/test_{hypothesis}.py`
7. **Verify** by comparing results with original V2 script

### Detailed Instructions for Each Hypothesis

---

## H1: Cash Holdings

**Source Scripts:**
- `src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py`
- `src/f1d/financial/v2/3.1_H1Variables.py`

**Model Specification:**
```
CashHoldings_{t+1} = beta0 + beta1*Uncertainty_t + beta2*Leverage_t
                     + beta3*(Uncertainty_t * Leverage_t)
                     + gamma*Controls + Firm FE + Year FE + epsilon
```

**Hypothesis Tests:**
- H1a: beta1 > 0 (Higher uncertainty leads to more cash holdings)
- H1b: beta3 < 0 (Leverage attenuates the uncertainty-cash relationship)

**Variables Required:**

| Variable | Type | Source | New Builder Needed? |
|----------|------|--------|---------------------|
| `CashHoldings` | Dependent | Compustat (CHE/AT) | ✅ Yes |
| `Leverage` | Moderator | Compustat ((DLTT+DLC)/AT) | ✅ Yes |
| `Uncertainty` | Key IV | Stage 2 (Manager_QA_Uncertainty_pct) | ❌ Reuse |
| `OCF_Volatility` | Control | Compustat (5yr rolling std) | ✅ Yes |
| `CurrentRatio` | Control | Compustat (ACT/LCT) | ✅ Yes |
| `TobinQ` | Control | Compustat calculation | ✅ Yes |
| `ROA` | Control | Compustat (IB/AT) | ✅ Yes |
| `Capex_AT` | Control | Compustat (CAPX/AT) | ✅ Yes |
| `DividendPayer` | Control | Compustat indicator | ✅ Yes |
| `FirmSize` | Control | Compustat ln(AT) | ✅ Yes |
| `gvkey`, `year` | ID | Manifest | ❌ Reuse |

**Files to Create:**
1. `src/f1d/shared/variables/cash_holdings.py`
2. `src/f1d/shared/variables/leverage.py`
3. `src/f1d/shared/variables/ocf_volatility.py`
4. `src/f1d/shared/variables/current_ratio.py`
5. `src/f1d/shared/variables/tobin_q.py`
6. `src/f1d/shared/variables/roa.py`
7. `src/f1d/shared/variables/capex_ratio.py`
8. `src/f1d/shared/variables/dividend_payer.py`
9. `src/f1d/shared/variables/firm_size.py`
10. `src/f1d/variables/build_h1_panel.py`
11. `src/f1d/econometric/test_h1_cash_holdings.py`

**Config Updates (`variables.yaml`):**
```yaml
variables:
  # H1 variables
  cash_holdings:
    stage: 3
    source: "outputs/3_Financial_V2"
    file_pattern: "H1_CashHoldings.parquet"
    column: "CashHoldings"

  leverage:
    stage: 3
    source: "outputs/3_Financial_V2"
    file_pattern: "H1_CashHoldings.parquet"
    column: "Leverage"

  # ... etc

hypothesis_tests:
  h1_cash_holdings:
    test_id: "H1_CashHoldings"
    dependent: "cash_holdings"
    key_iv: "manager_qa_uncertainty"
    moderator: "leverage"
    controls: [ocf_volatility, current_ratio, tobin_q, roa, capex_ratio, dividend_payer, firm_size]
    interaction: "manager_qa_uncertainty * leverage"
    fixed_effects: [gvkey, year]
```

---

## H2: Investment Efficiency

**Source Scripts:**
- `src/f1d/econometric/v2/4.2_H2InvestmentEfficiencyRegression.py`
- `src/f1d/financial/v2/3.2_H2Variables.py`

**Model Specification:**
Tests whether policy risk moderates the uncertainty-investment relationship.

**Variables Required:**
- Investment (CAPX/AT or similar)
- Policy Risk Uncertainty (PRisk)
- Manager Uncertainty
- Tobin's Q
- Cash Flow
- Firm Size
- Firm FE, Year FE

**Special Considerations:**
- Read `3.9_H2_BiddleInvestmentResidual.py` for investment efficiency measure
- Read `3.10_H2_PRiskUncertaintyMerge.py` for policy risk data

---

## H3: Payout Policy

**Source Scripts:**
- `src/f1d/econometric/v2/4.3_H3PayoutPolicyRegression.py`
- `src/f1d/financial/v2/3.3_H3Variables.py`

**Model Specification:**
Tests whether CEO clarity affects dividend policy.

**Variables Required:**
- Dividends (DVC)
- Repurchases (PRSTKC)
- Earnings (IB)
- Cash Holdings
- Leverage
- Firm Size
- Tobin's Q

---

## H5: Analyst Dispersion

**Source Scripts:**
- `src/f1d/econometric/v2/4.5_H5DispersionRegression.py`
- `src/f1d/financial/v2/3.5_H5Variables.py`

**Model Specification:**
Tests whether weak modal language predicts forecast dispersion.

**Variables Required:**
- Analyst Forecast Dispersion
- Forecast Error
- Manager Uncertainty
- Firm Size
- Analyst Coverage
- Earnings Volatility

---

## H6: CCCL (SEC Scrutiny)

**Source Scripts:**
- `src/f1d/econometric/v2/4.6_H6CCCLRegression.py`
- `src/f1d/financial/v2/3.6_H6Variables.py`

**Model Specification:**
2SLS IV regression testing whether SEC scrutiny reduces CEO uncertainty.

**Variables Required:**
- CCCL components (Crash risk measures)
- SEC Scrutiny indicators
- Manager Uncertainty
- Control variables

**Special Considerations:**
- This is a 2SLS IV regression, not OLS
- Need to implement IV regression support in shared modules

---

## H7: Stock Illiquidity

**Source Scripts:**
- `src/f1d/econometric/v2/4.7_H7IlliquidityRegression.py`
- `src/f1d/financial/v2/3.7_H7IlliquidityVariables.py`

**Model Specification:**
Tests whether uncertainty increases stock illiquidity.

**Variables Required:**
- Amihud Illiquidity measure
- Trading Volume
- Manager Uncertainty
- Control variables

---

## H8: Takeover

**Source Scripts:**
- `src/f1d/econometric/v2/4.8_H8TakeoverRegression.py`
- `src/f1d/financial/v2/3.8_H8TakeoverVariables.py`

**Model Specification:**
Logistic regression testing whether uncertainty predicts takeover probability.

**Variables Required:**
- Takeover indicator
- Manager Uncertainty
- Firm characteristics
- Industry controls

**Special Considerations:**
- This is a logit model, not OLS
- May also include survival analysis (Cox PH)

---

## H9: CEO Style x Policy Risk

**Source Scripts:**
- `src/f1d/econometric/v2/4.11_H9_Regression.py`
- `src/f1d/financial/v2/3.11_H9_StyleFrozen.py`
- `src/f1d/financial/v2/3.12_H9_PRiskFY.py`
- `src/f1d/financial/v2/3.13_H9_AbnormalInvestment.py`

**Model Specification:**
Tests whether CEO style moderates policy risk effect.

**Variables Required:**
- CEO Style factors (frozen from manager fixed effects)
- Policy Risk measures
- Investment outcomes
- Control variables

---

## Implementation Checklist Template

For each hypothesis, complete this checklist:

```markdown
## {HYPOTHESIS} Implementation Checklist

### Step 1: Analysis
- [ ] Read existing V2 econometric script for model specification
- [ ] Read existing V2 variables script for required variables
- [ ] Document all required variables with sources

### Step 2: Variable Builders
- [ ] Create new variable builders in `src/f1d/shared/variables/`
- [ ] Update `src/f1d/shared/variables/__init__.py` to export new builders
- [ ] Update `config/variables.yaml` with new variable definitions

### Step 3: Stage 3 Panel Builder
- [ ] Create `src/f1d/variables/build_{hypothesis}_panel.py`
- [ ] Implement variable loading using builders
- [ ] Implement panel merging logic
- [ ] Add derived fields if needed
- [ ] Generate summary stats output

### Step 4: Stage 4 Test Script
- [ ] Create `src/f1d/econometric/test_{hypothesis}.py`
- [ ] Implement regression function
- [ ] Implement results extraction
- [ ] Generate LaTeX table output
- [ ] Generate markdown report

### Step 5: Verification
- [ ] Run Stage 3 script
- [ ] Run Stage 4 script
- [ ] Compare results with original V2 script
- [ ] Verify LaTeX table compiles

### Step 6: Cleanup (Optional)
- [ ] Mark old V2 scripts as deprecated
- [ ] Update documentation
```

---

## Verification Process

### For Each Hypothesis

1. **Stage 3 Verification:**
   - Panel has all required columns
   - Row count matches expected
   - Summary stats generated
   - Report markdown generated

2. **Stage 4 Verification:**
   - Regressions run for all samples
   - Coefficient values match original script within tolerance (1e-6)
   - LaTeX table compiles without errors
   - Report markdown generated

3. **Regression Test:**
   ```bash
   # Run original V2 script
   python -m f1d.econometric.v2.4.X_HXRegression

   # Run new script
   python -m f1d.econometric.test_hx

   # Compare results programmatically
   ```

---

## Files Reference

### Created Files (Pilot)
| File | Purpose |
|------|---------|
| `src/f1d/shared/variables/__init__.py` | Package init, exports |
| `src/f1d/shared/variables/base.py` | Base classes |
| `src/f1d/shared/variables/manager_qa_uncertainty.py` | Variable builder |
| `src/f1d/shared/variables/manager_pres_uncertainty.py` | Variable builder |
| `src/f1d/shared/variables/analyst_qa_uncertainty.py` | Variable builder |
| `src/f1d/shared/variables/negative_sentiment.py` | Variable builder |
| `src/f1d/shared/variables/stock_return.py` | Variable builder |
| `src/f1d/shared/variables/market_return.py` | Variable builder |
| `src/f1d/shared/variables/eps_growth.py` | Variable builder |
| `src/f1d/shared/variables/earnings_surprise.py` | Variable builder |
| `src/f1d/shared/variables/manifest_fields.py` | Variable builder |
| `src/f1d/variables/__init__.py` | Package init |
| `src/f1d/variables/build_manager_clarity_panel.py` | Stage 3 script |
| `src/f1d/econometric/test_manager_clarity.py` | Stage 4 script |
| `src/f1d/shared/latex_tables_accounting.py` | LaTeX generator |
| `config/variables.yaml` | Variable configuration |

### Documentation
| File | Purpose |
|------|---------|
| `docs/STAGE3_4_REWRITE_PLAN.md` | This document |
| `docs/STAGE3_4_REFACTOR_PROGRESS.md` | Progress report |

### Existing V2 Scripts (Reference)
| Script | Purpose |
|--------|---------|
| `src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py` | H1 regression |
| `src/f1d/econometric/v2/4.2_H2InvestmentEfficiencyRegression.py` | H2 regression |
| `src/f1d/econometric/v2/4.3_H3PayoutPolicyRegression.py` | H3 regression |
| `src/f1d/econometric/v2/4.5_H5DispersionRegression.py` | H5 regression |
| `src/f1d/econometric/v2/4.6_H6CCCLRegression.py` | H6 regression |
| `src/f1d/econometric/v2/4.7_H7IlliquidityRegression.py` | H7 regression |
| `src/f1d/econometric/v2/4.8_H8TakeoverRegression.py` | H8 regression |
| `src/f1d/econometric/v2/4.11_H9_Regression.py` | H9 regression |
| `src/f1d/financial/v2/3.1_H1Variables.py` | H1 variables |
| `src/f1d/financial/v2/3.2_H2Variables.py` | H2 variables |
| `src/f1d/financial/v2/3.3_H3Variables.py` | H3 variables |
| `src/f1d/financial/v2/3.5_H5Variables.py` | H5 variables |
| `src/f1d/financial/v2/3.6_H6Variables.py` | H6 variables |
| `src/f1d/financial/v2/3.7_H7IlliquidityVariables.py` | H7 variables |
| `src/f1d/financial/v2/3.8_H8TakeoverVariables.py` | H8 variables |

---

## Critical Reminders for AI Implementer

1. **NEVER hardcode timestamp directories** - Use `resolve_source_dir()` which finds directories automatically

2. **Follow the established patterns** - Look at `test_manager_clarity.py` as the template

3. **Read V2 scripts carefully** - They contain the exact model specifications needed

4. **Test incrementally** - Run Stage 3 before Stage 4, verify panel structure

5. **Update config first** - Add new variables to `config/variables.yaml` before creating builders

6. **Reuse existing builders** - Many hypotheses will use `manager_qa_uncertainty`, `manifest_fields`, etc.

7. **LaTeX format is strict** - Use `latex_tables_accounting.py`, two columns per model (Est., t-value), no stars

---

*End of Document*
