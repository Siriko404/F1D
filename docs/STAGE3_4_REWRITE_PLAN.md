# Stage 3/4 Rewrite Plan: V1 Econometric Tests

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite remaining V1 econometric scripts using the modern Stage 3 (variables) → Stage 4 (econometric) architecture.

**Architecture:**
- **Stage 3:** Panel builders in `src/f1d/variables/` load variables via shared builders, merge into complete panels
- **Stage 4:** Test scripts in `src/f1d/econometric/` run regressions, output Accounting Review LaTeX
- **Config:** `config/variables.yaml` defines ALL variable sources - scripts NEVER hardcode paths

**Tech Stack:** Python, pandas, statsmodels, YAML config, parquet files

---

## V1 Tests Status

### Completed

| Test | New Stage 3 | New Stage 4 | Status |
|------|-------------|-------------|--------|
| 4.1 Manager Clarity | `build_manager_clarity_panel.py` | `test_manager_clarity.py` | ✅ COMPLETE |

### Remaining (Priority Order)

| Test | V1 Script | Description | New Builders Needed |
|------|-----------|-------------|---------------------|
| 4.1.1 | `4.1.1_EstimateCeoClarity.py` | CEO clarity (CEO speech only) | `ceo_qa_uncertainty`, `ceo_pres_uncertainty` |
| 4.1.4 | `4.1.4_EstimateCeoTone.py` | CEO tone (Net Sentiment) | 6 NetTone builders |
| 4.1.3 | `4.1.3_EstimateCeoClarity_Regime.py` | Non-CEO manager clarity | `nonceo_manager_qa_uncertainty` |
| 4.2 | `4.2_LiquidityRegressions.py` | IV regression (liquidity) | CCCL instrument, clarity scores |
| 4.3 | `4.3_TakeoverHazards.py` | Survival analysis | Clarity scores, SDC data |
| 4.1.2 | `4.1.2_EstimateCeoClarity_Extended.py` | Extended controls | Extended financial vars |
| 4.4 | `4.4_GenerateSummaryStats.py` | **UTILITY** (not a test) | None - reads existing outputs |

---

## Pilot Reference: Manager Clarity (4.1)

**Run Commands:**
```bash
python -m f1d.variables.build_manager_clarity_panel
python -m f1d.econometric.test_manager_clarity
```

**Model (from V1 CONFIG):**
```python
CONFIG = {
    "dependent_var": "Manager_QA_Uncertainty_pct",
    "linguistic_controls": ["Manager_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct", "Entire_All_Negative_pct"],
    "firm_controls": ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"],
}
```

**Results:** Main: 56,060 obs / 2,539 managers / R²=0.41 | Finance: 12,852 / 548 / 0.31 | Utility: 2,950 / 134 / 0.22

---

## Task 1: 4.1.1 CEO Clarity

**Source:** `src/f1d/econometric/v1/4.1.1_EstimateCeoClarity.py`

**Model (from V1 CONFIG):**
```python
CONFIG = {
    "dependent_var": "CEO_QA_Uncertainty_pct",
    "linguistic_controls": ["CEO_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct", "Entire_All_Negative_pct"],
    "firm_controls": ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"],
}
```

**Formula:**
```
CEO_QA_Uncertainty_pct ~ C(ceo_id) + C(year) + CEO_Pres_Uncertainty_pct + Analyst_QA_Uncertainty_pct + Entire_All_Negative_pct + StockRet + MarketRet + EPS_Growth + SurpDec
```

**Variables:**

| Column | Type | Builder |
|--------|------|---------|
| `CEO_QA_Uncertainty_pct` | Dependent | **CREATE** `ceo_qa_uncertainty.py` |
| `CEO_Pres_Uncertainty_pct` | Control | **CREATE** `ceo_pres_uncertainty.py` |
| `Analyst_QA_Uncertainty_pct` | Control | REUSE `analyst_qa_uncertainty` |
| `Entire_All_Negative_pct` | Control | REUSE `negative_sentiment` |
| `StockRet`, `MarketRet`, `EPS_Growth`, `SurpDec` | Controls | REUSE existing |
| `ceo_id`, `gvkey`, `ff12_code`, `start_date` | ID | REUSE `manifest_fields` |

**Files to Create:**
- `src/f1d/shared/variables/ceo_qa_uncertainty.py`
- `src/f1d/shared/variables/ceo_pres_uncertainty.py`
- `src/f1d/variables/build_ceo_clarity_panel.py`
- `src/f1d/econometric/test_ceo_clarity.py`

**Config (`variables.yaml`):**
```yaml
variables:
  ceo_qa_uncertainty:
    stage: 2
    source: "outputs/2_Textual_Analysis/2.2_Variables"
    file_pattern: "linguistic_variables_{year}.parquet"
    column: "CEO_QA_Uncertainty_pct"

  ceo_pres_uncertainty:
    stage: 2
    source: "outputs/2_Textual_Analysis/2.2_Variables"
    file_pattern: "linguistic_variables_{year}.parquet"
    column: "CEO_Pres_Uncertainty_pct"

hypothesis_tests:
  ceo_clarity:
    test_id: "4.1.1_CeoClarity"
    dependent: "ceo_qa_uncertainty"
    linguistic_controls: [ceo_pres_uncertainty, analyst_qa_uncertainty, negative_sentiment]
    firm_controls: [stock_return, market_return, eps_growth, earnings_surprise]
    outputs:
      panel: "outputs/variables/ceo_clarity"
      results: "outputs/econometric/ceo_clarity"
```

---

## Task 2: 4.1.4 CEO Tone

**Source:** `src/f1d/econometric/v1/4.1.4_EstimateCeoTone.py`

**Description:** Uses NetTone (Positive - Negative), NOT raw sentiment percentages.

**Three Models (from V1 CONFIG):**

| Model | Dependent Variable |
|-------|-------------------|
| ToneAll | `Manager_QA_NetTone` |
| ToneCEO | `CEO_QA_NetTone` |
| ToneRegime | `NonCEO_Manager_QA_NetTone` |

**Formula (ToneAll):**
```
Manager_QA_NetTone ~ C(ceo_id) + C(year) + Manager_Pres_NetTone + Analyst_QA_NetTone + Entire_All_Uncertainty_pct + StockRet + MarketRet + EPS_Growth + SurpDec
```

**Variables:**

| Column | Type | Builder |
|--------|------|---------|
| `Manager_QA_NetTone` | Dependent (ToneAll) | **CREATE** `manager_qa_nettone.py` |
| `CEO_QA_NetTone` | Dependent (ToneCEO) | **CREATE** `ceo_qa_nettone.py` |
| `NonCEO_Manager_QA_NetTone` | Dependent (ToneRegime) | **CREATE** `nonceo_manager_qa_nettone.py` |
| `Manager_Pres_NetTone` | Control | **CREATE** `manager_pres_nettone.py` |
| `CEO_Pres_NetTone` | Control | **CREATE** `ceo_pres_nettone.py` |
| `Analyst_QA_NetTone` | Control | **CREATE** `analyst_qa_nettone.py` |
| `Entire_All_Uncertainty_pct` | Control | May need builder |
| Financial controls | Controls | REUSE existing |

**Files to Create:**
- 6 NetTone variable builders
- `src/f1d/variables/build_ceo_tone_panel.py`
- `src/f1d/econometric/test_ceo_tone.py`

---

## Task 3: 4.1.3 CEO Clarity Regime

**Source:** `src/f1d/econometric/v1/4.1.3_EstimateCeoClarity_Regime.py`

**Description:** Non-CEO manager clarity (CFO, other executives).

**Model (from V1 CONFIG):**
```python
CONFIG = {
    "dependent_var": "NonCEO_Manager_QA_Uncertainty_pct",
    "linguistic_controls": ["Manager_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct", "Entire_All_Negative_pct"],
    "firm_controls": ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"],
}
```

**Formula:**
```
NonCEO_Manager_QA_Uncertainty_pct ~ C(ceo_id) + C(year) + Manager_Pres_Uncertainty_pct + Analyst_QA_Uncertainty_pct + Entire_All_Negative_pct + StockRet + MarketRet + EPS_Growth + SurpDec
```

**Variables:**

| Column | Type | Builder |
|--------|------|---------|
| `NonCEO_Manager_QA_Uncertainty_pct` | Dependent | **CREATE** `nonceo_manager_qa_uncertainty.py` |
| Others | Controls | REUSE existing |

**Files to Create:**
- `src/f1d/shared/variables/nonceo_manager_qa_uncertainty.py`
- `src/f1d/variables/build_clarity_regime_panel.py`
- `src/f1d/econometric/test_clarity_regime.py`

---

## Task 4: 4.2 Liquidity Regressions

**Source:** `src/f1d/econometric/v1/4.2_LiquidityRegressions.py`

**Description:** IV/2SLS regression. Tests communication effects on market liquidity.

**Models:**
1. First Stage: Q&A Uncertainty ~ CCCL Instrument
2. OLS Regressions
3. 2SLS Regressions (Q&A Uncertainty instrumented)

**Key Variables:**
- `ClarityRegime`: From 4.1 output (EXOGENOUS)
- `ClarityCEO`: From 4.1.1 output (EXOGENOUS)
- `Manager_QA_Uncertainty_pct`: ENDOGENOUS (instrumented)
- `shift_intensity_sale_ff48`: CCCL instrument

**Dependencies:** Requires 4.1 and 4.1.1 scores

**Special:** Requires IV/2SLS support (linearmodels)

---

## Task 5: 4.3 Takeover Hazards

**Source:** `src/f1d/econometric/v1/4.3_TakeoverHazards.py`

**Description:** Survival analysis. Tests if clarity predicts takeover.

**Models:**
1. Cox Proportional Hazards (All Takeovers)
2. Fine-Gray Competing Risks (Uninvited)
3. Fine-Gray Competing Risks (Friendly)

**Key Variables:**
- `ClarityRegime`: From 4.1
- `ClarityCEO`: From 4.1.1
- `Manager_QA_Uncertainty_pct`

**Special:** Requires `lifelines` library, SDC M&A data

**Dependencies:** Requires 4.1 scores

---

## Task 6: 4.1.2 CEO Clarity Extended

**Source:** `src/f1d/econometric/v1/4.1.2_EstimateCeoClarity_Extended.py`

**Description:** Extended controls robustness. 4 models.

**Extended Controls:**
```python
extended_controls = ["Size", "BM", "Lev", "ROA", "CurrentRatio", "RD_Intensity", "Volatility"]
```

**Priority:** Lower - implement after core tests

---

## Task 7: 4.4 Summary Stats (UTILITY)

**Source:** `src/f1d/econometric/v1/4.4_GenerateSummaryStats.py`

**⚠️ THIS IS A UTILITY, NOT A HYPOTHESIS TEST**

Does NOT follow Stage 3 → Stage 4 pattern:
- No panel builder needed
- No variable builders needed
- Reads existing outputs directly
- Produces descriptive statistics

**File to Create:** `src/f1d/econometric/generate_summary_stats.py`

---

## Implementation Pattern

### For Each Hypothesis Test:

**Step 1:** Read V1 script, extract CONFIG with exact variable names

**Step 2:** Update `config/variables.yaml`:
- Add new variable definitions
- Add hypothesis test configuration

**Step 3:** Create variable builders in `src/f1d/shared/variables/`:
```python
class NewVariableBuilder(VariableBuilder):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "Column_Name")

    def build(self, years: range, root_path: Path) -> VariableResult:
        source_dir = self.resolve_source_dir(root_path)  # NEVER hardcode paths
        # ... load and return
```

**Step 4:** Update `src/f1d/shared/variables/__init__.py` exports

**Step 5:** Create Stage 3 panel builder in `src/f1d/variables/`:
```python
var_config = load_variable_config()  # From config
builders = {
    "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
    # ... other builders
}
# Merge on file_name, output panel.parquet
```

**Step 6:** Create Stage 4 test script in `src/f1d/econometric/`:
```python
CONFIG = {
    "dependent_var": "ExactColumnName",
    "linguistic_controls": ["ExactColumn1", "ExactColumn2"],
    "firm_controls": ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"],
}
# Load panel via get_latest_output_dir()
# Run regression, output LaTeX
```

**Step 7:** Verify results match V1 script within tolerance (1e-6)

**Step 8:** Commit

---

## Critical Rules

1. **ALL paths from config** - NEVER hardcode timestamp directories
2. **Use `resolve_source_dir()`** - Finds latest output automatically
3. **Exact variable names from V1 CONFIG** - Don't guess
4. **Test Stage 3 before Stage 4** - Verify panel first
5. **4.4 is a UTILITY** - No panel builder, no test pattern
6. **LaTeX format: Est. + t-value, NO stars**

---

## Files Reference

### Existing (Pilot)
- `src/f1d/shared/variables/base.py` - VariableBuilder, VariableStats, VariableResult
- `src/f1d/shared/variables/__init__.py` - Exports
- `src/f1d/shared/variables/manager_qa_uncertainty.py` - Template
- `src/f1d/variables/build_manager_clarity_panel.py` - Stage 3 template
- `src/f1d/econometric/test_manager_clarity.py` - Stage 4 template
- `config/variables.yaml` - Variable configuration

### V1 Scripts (Source of Truth)
- `src/f1d/econometric/v1/4.1.1_EstimateCeoClarity.py`
- `src/f1d/econometric/v1/4.1.2_EstimateCeoClarity_Extended.py`
- `src/f1d/econometric/v1/4.1.3_EstimateCeoClarity_Regime.py`
- `src/f1d/econometric/v1/4.1.4_EstimateCeoTone.py`
- `src/f1d/econometric/v1/4.2_LiquidityRegressions.py`
- `src/f1d/econometric/v1/4.3_TakeoverHazards.py`
- `src/f1d/econometric/v1/4.4_GenerateSummaryStats.py`

---

*End of Document*
