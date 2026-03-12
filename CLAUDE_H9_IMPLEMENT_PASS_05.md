File: CLAUDE_H9_IMPLEMENT_PASS_05.md
Scope: H9 implementation alignment within current architecture
Edits made: H9 implementation files only
Model/code changes made: Yes
Status: Complete

# H9 Implementation Alignment — Pass 05

# Task 1 — Target Spec Lock

## Current H9 Implementation Summary (Pre-Pass 05)

### Model Variants
- CEO clarity score (ClarityCEO) with uncertainty companion (`uncertainty_var: CEO_QA_Uncertainty_pct`)
- CEO residual (CEO_Clarity_Residual) with uncertainty companion
- Manager residual (Manager_Clarity_Residual) with uncertainty companion
- All variants mixed in a single `MODEL_VARIANTS` dict with no family separation

### Financial Controls
- Size, BM, Lev, ROA (Compustat)
- EPS_Growth (IBES)
- StockRet, MarketRet (CRSP)
- SurpDec (IBES)
- Single flat `FINANCIAL_CONTROLS` list used by all models

### Presentation
- Single mixed table for all variants
- No separation between primary style and secondary residual models
- Report text described "CEO Clarity + Uncertainty interaction" framing

## Desired H9 Implementation Summary (Target)

### Primary Research Question
Does clarity in speech increase the likelihood of receiving a takeover bid, especially an UNINVITED bid?

### Model Organization
- **PRIMARY STYLE MODELS**: CEO clarity score (ClarityCEO), Manager clarity score (ClarityManager)
- **SECONDARY RESIDUAL MODELS**: CEO residual, Manager residual
- Sparse controls for all models; expanded controls as robustness for all families

### Financial Controls (Compustat-only)
- **SPARSE BLOCK**: Size, BM, Lev, ROA, CashHoldings
- **EXPANDED ROBUSTNESS BLOCK**: + SalesGrowth, Intangibility, AssetGrowth
- NO CRSP/IBES controls (StockRet, MarketRet, SurpDec, EPS_Growth removed)

### Presentation
- Separate PRIMARY STYLE and SECONDARY RESIDUAL sections
- Separate EXPANDED ROBUSTNESS section
- Primary focus on CEO clarity score as main construct

## Gap List

| # | Mismatch | File | Evidence |
|---|----------|------|----------|
| 1 | Controls include EPS_Growth (IBES) | `build_h9_takeover_panel.py` | `EPSGrowthBuilder` imported |
| 2 | Controls include StockRet, MarketRet (CRSP) | `build_h9_takeover_panel.py` | `StockReturnBuilder`, `MarketReturnBuilder` imported |
| 3 | Controls include SurpDec (IBES) | `build_h9_takeover_panel.py` | `EarningsSurpriseBuilder` imported |
| 4 | Econometric controls list includes CRSP/IBES | `run_h9_takeover_hazards.py` | `FINANCIAL_CONTROLS` included EPS_Growth, StockRet, MarketRet, SurpDec |
| 5 | MODEL_VARIANTS includes uncertainty_var | `run_h9_takeover_hazards.py` | Each variant dict had `uncertainty_var` key |
| 6 | No family separation (primary vs secondary) | `run_h9_takeover_hazards.py` | MODEL_VARIANTS had no `family` key |
| 7 | No sparse/expanded control separation | `run_h9_takeover_hazards.py` | Single `FINANCIAL_CONTROLS` list for all models |
| 8 | Report text did not separate PRIMARY/SECONDARY | `run_h9_takeover_hazards.py` | Report generation used mixed wording |
| 9 | Manager clarity score not available | N/A | ClarityManager does not exist in repo |
| 10 | CashHoldings not in panel | `build_h9_takeover_panel.py` | `CashHoldingsBuilder` not imported |
| 11 | Intangibility, AssetGrowth not in panel or repo | `_compustat_engine.py` | No builder existed for either variable |

---

# Task 2 — Panel / Variable Flow Fixes

## Files Edited

1. `src/f1d/variables/build_h9_takeover_panel.py` — Updated imports and builders
2. `src/f1d/shared/variables/__init__.py` — Exported new builders
3. `src/f1d/shared/variables/_compustat_engine.py` — Added Intangibility and AssetGrowth computation
4. `src/f1d/shared/variables/intangibility.py` — New file: IntangibilityBuilder
5. `src/f1d/shared/variables/asset_growth.py` — New file: AssetGrowthBuilder

## Before Snippet (build_h9_takeover_panel.py imports)

```python
from f1d.shared.variables import (
    ...
    EPSGrowthBuilder,
    StockReturnBuilder,
    MarketReturnBuilder,
    EarningsSurpriseBuilder,
    ...
)
```

## After Snippet (build_h9_takeover_panel.py imports)

```python
from f1d.shared.variables import (
    ...
    CashHoldingsBuilder,
    SalesGrowthBuilder,
    IntangibilityBuilder,
    AssetGrowthBuilder,
    ...
)
```

## Before Snippet (builders dict)

```python
builders = {
    ...
    "eps_growth": EPSGrowthBuilder(...),
    "stock_return": StockReturnBuilder(...),
    "market_return": MarketReturnBuilder(...),
    "earnings_surprise": EarningsSurpriseBuilder(...),
}
```

## After Snippet (builders dict)

```python
builders = {
    ...
    "cash_holdings": CashHoldingsBuilder({}),
    "sales_growth": SalesGrowthBuilder({}),
    "intangibility": IntangibilityBuilder({}),
    "asset_growth": AssetGrowthBuilder({}),
}
```

## Final Variable List Flowing into H9

| Variable | Source | Status |
|----------|--------|--------|
| ClarityCEO | CEO fixed-effect score (4.1.1) | Available (59.5% coverage) |
| CEO_Clarity_Residual | Clarity extended regression residual | Available (42.5% coverage) |
| Manager_Clarity_Residual | Clarity extended regression residual | Available (55.8% coverage) |
| Size | Compustat: log(AT) | Available (99.8% coverage) |
| BM | Compustat: Book-to-Market | Available (99.2% coverage) |
| Lev | Compustat: Debt/Assets | Available (99.8% coverage) |
| ROA | Compustat: Return on Assets | Available (99.6% coverage) |
| CashHoldings | Compustat: CHE/AT | Available (99.8% coverage) |
| SalesGrowth | Compustat: YoY revenue growth | Available (99.6% coverage) |
| Intangibility | Compustat: INTAN/AT | Available (99.4% coverage) |
| AssetGrowth | Compustat: YoY total asset growth | Available (98.8% coverage) |

## Variables Not Added

| Variable | Reason |
|----------|--------|
| ClarityManager | Does not exist in repo. The repo has CEO fixed-effect clarity scores (ClarityCEO) but no equivalent Manager clarity score. Manager variants are available only as residuals (Manager_Clarity_Residual). |

---

# Task 3 — Econometric Spec Fixes

## Files Edited

- `src/f1d/econometric/run_h9_takeover_hazards.py`

## Before Snippet (FINANCIAL_CONTROLS)

```python
FINANCIAL_CONTROLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "EPS_Growth",
    "StockRet",
    "MarketRet",
    "SurpDec",
]
```

## After Snippet (SPARSE_CONTROLS + EXPANDED_CONTROLS)

```python
SPARSE_CONTROLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CashHoldings",
]

EXPANDED_CONTROLS = SPARSE_CONTROLS + [
    "SalesGrowth",
    "Intangibility",
    "AssetGrowth",
]
```

## Before Snippet (MODEL_VARIANTS)

```python
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    "CEO": {
        "clarity_var": "ClarityCEO",
        "uncertainty_var": "CEO_QA_Uncertainty_pct",
        "description": "CEO Clarity Score (4.1.1)",
    },
    "CEO_Residual": {
        "clarity_var": "CEO_Clarity_Residual",
        "uncertainty_var": "CEO_QA_Uncertainty_pct",
        "description": "CEO Residual",
    },
    "Manager_Residual": {
        "clarity_var": "Manager_Clarity_Residual",
        "uncertainty_var": "Manager_QA_Uncertainty_pct",
        "description": "Manager Residual",
    },
}
```

## After Snippet (MODEL_VARIANTS)

```python
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    # PRIMARY STYLE MODEL
    "CEO": {
        "clarity_var": "ClarityCEO",
        "description": "CEO Clarity Score (4.1.1) — PRIMARY",
        "family": "primary_style",
    },
    # SECONDARY RESIDUAL MODELS
    "CEO_Residual": {
        "clarity_var": "CEO_Clarity_Residual",
        "description": "CEO Residual — SECONDARY (residualized uncertainty)",
        "family": "secondary_residual",
    },
    "Manager_Residual": {
        "clarity_var": "Manager_Clarity_Residual",
        "description": "Manager Residual — SECONDARY (residualized uncertainty)",
        "family": "secondary_residual",
    },
}
```

## Before Snippet (Covariate Construction)

```python
clarity_var = variant["clarity_var"]
uncertainty_var = variant["uncertainty_var"]
covariates = [clarity_var, uncertainty_var] + [
    c for c in FINANCIAL_CONTROLS if c in df.columns
]
```

## After Snippet (Covariate Construction)

```python
clarity_var = variant_spec["clarity_var"]
covariates = [clarity_var] + [c for c in controls if c in df.columns]
covariates = [c for c in covariates if c in df.columns]
```

Where `controls` is `SPARSE_CONTROLS` for the main run and `EXPANDED_CONTROLS` for the robustness run.

## Model Execution Structure

The main loop now runs in two phases:

1. **Phase A+B (Sparse)**: All 3 variants (CEO, CEO_Residual, Manager_Residual) x 3 event types = 9 models with `SPARSE_CONTROLS`
2. **Phase C (Expanded)**: All 3 variants x 3 event types = 9 models with `EXPANDED_CONTROLS`

Expanded variants are tagged with `_expanded` suffix (e.g., `CEO_expanded`, `CEO_Residual_expanded`).

## Final Primary Model Menu (Sparse)

| Model | Event | Clarity Variable | Controls |
|-------|-------|------------------|----------|
| Cox PH All | All takeovers | ClarityCEO | Size, BM, Lev, ROA, CashHoldings |
| Cox CS Uninvited | Uninvited (Hostile+Unsolicited) | ClarityCEO | Size, BM, Lev, ROA, CashHoldings |
| Cox CS Friendly | Friendly (Friendly+Neutral) | ClarityCEO | Size, BM, Lev, ROA, CashHoldings |

## Final Secondary Model Menu (Sparse)

| Model | Event | Clarity Variable | Controls |
|-------|-------|------------------|----------|
| Cox PH All | All takeovers | CEO_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings |
| Cox CS Uninvited | Uninvited | CEO_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings |
| Cox CS Friendly | Friendly | CEO_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings |
| Cox PH All | All takeovers | Manager_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings |
| Cox CS Uninvited | Uninvited | Manager_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings |
| Cox CS Friendly | Friendly | Manager_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings |

## Expanded-Control Robustness Menu (All Families)

| Model | Event | Clarity Variable | Controls |
|-------|-------|------------------|----------|
| Cox PH All | All | ClarityCEO | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox CS Uninvited | Uninvited | ClarityCEO | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox CS Friendly | Friendly | ClarityCEO | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox PH All | All | CEO_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox CS Uninvited | Uninvited | CEO_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox CS Friendly | Friendly | CEO_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox PH All | All | Manager_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox CS Uninvited | Uninvited | Manager_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |
| Cox CS Friendly | Friendly | Manager_Clarity_Residual | Size, BM, Lev, ROA, CashHoldings, SalesGrowth, Intangibility, AssetGrowth |

## Confirmation: CRSP/IBES Controls Removed

**CONFIRMED.** No StockRet, MarketRet, SurpDec, or EPS_Growth in:
- `SPARSE_CONTROLS`
- `EXPANDED_CONTROLS`
- `hazard_ratios.csv` output
- `model_diagnostics.csv` output

Only Compustat-sourced variables remain.

---

# Task 4 — Rerun Log

## Exact Commands Run

### Stage 3 Panel Build

```bash
python -m f1d.variables.build_h9_takeover_panel
```

**Start time**: 2026-03-11 20:10:42
**End time**: 2026-03-11 20:12:01
**Duration**: 79.2 seconds
**Result**: SUCCESS

### Stage 4 Hazard Models

```bash
python -m f1d.econometric.run_h9_takeover_hazards
```

**Start time**: 2026-03-11 20:16:29
**End time**: 2026-03-11 20:16:32
**Duration**: 2.6 seconds
**Result**: SUCCESS

## Output Directories Generated

- `outputs/variables/takeover/2026-03-11_201042/`
- `outputs/econometric/takeover/2026-03-11_201629/`

## Key Regenerated Files

### Stage 3 Panel
- `takeover_panel.parquet` (27,773 rows, 25 columns)
- `summary_stats.csv`
- `report_step3_takeover.md`
- `run_manifest.json`

### Stage 4 Hazards
- `hazard_ratios.csv` (135 rows, 18 model variants)
- `model_diagnostics.csv` (18 rows)
- `cox_ph_all.txt`, `cox_cs_uninvited.txt`, `cox_cs_friendly.txt` (sparse models)
- `cox_ph_all_expanded.txt`, `cox_cs_uninvited_expanded.txt`, `cox_cs_friendly_expanded.txt` (expanded models)
- `takeover_table.tex`
- `summary_stats.csv`, `summary_stats.tex`
- `report_step4_takeover.md`
- `sample_attrition.csv`, `sample_attrition.tex`
- `run_manifest.json`, `run_log.txt`

---

# Task 5 — Post-Run Verification

## 12-Row Pass/Fail Table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | CEO clarity models exist and ran | **PASS** | `hazard_ratios.csv`: variant=CEO and CEO_expanded, 3 event types each |
| 2 | Manager clarity models exist and ran | **FAIL (KNOWN)** | ClarityManager does not exist in repo. Only Manager_Clarity_Residual available. |
| 3 | CEO residual models exist and ran | **PASS** | `hazard_ratios.csv`: variant=CEO_Residual and CEO_Residual_expanded, 3 event types each |
| 4 | Manager residual models exist and ran | **PASS** | `hazard_ratios.csv`: variant=Manager_Residual and Manager_Residual_expanded, 3 event types each |
| 5 | No final H9 model uses StockRet | **PASS** | Not in SPARSE_CONTROLS or EXPANDED_CONTROLS; not in hazard_ratios.csv variable column |
| 6 | No final H9 model uses MarketRet | **PASS** | Not in SPARSE_CONTROLS or EXPANDED_CONTROLS; not in hazard_ratios.csv variable column |
| 7 | No final H9 model uses SurpDec | **PASS** | Not in SPARSE_CONTROLS or EXPANDED_CONTROLS; not in hazard_ratios.csv variable column |
| 8 | Uninvited = Hostile + Unsolicited | **PASS** | `prepare_main_sample()`: `(Takeover_Type == "Uninvited")` where Uninvited is mapped from Hostile+Unsolicited in SDC |
| 9 | Friendly = Friendly + Neutral | **PASS** | `prepare_main_sample()`: `(Takeover_Type == "Friendly")` where Friendly is mapped from Friendly+Neutral in SDC |
| 10 | Unknown censored in cause-specific | **PASS** | `run_log.txt`: "26 takeover event(s) have neither Uninvited nor Friendly type -- treated as censored in cause-specific models" |
| 11 | Style/residual separated in output | **PASS** | `model_diagnostics.csv`: CEO variants (primary_style) and CEO_Residual/Manager_Residual variants (secondary_residual) in separate rows with control_block label; report separates PRIMARY/SECONDARY |
| 12 | Primary focus on clarity score | **PASS** | MODEL_VARIANTS: CEO has `family: "primary_style"`, runs first in model loop |

## Summary

- **11/12 checks PASS**
- **1 check FAIL (KNOWN LIMITATION)**: ClarityManager does not exist in the repository. The repo produces CEO fixed-effect clarity scores (ClarityCEO) but has no equivalent Manager clarity score. Manager variants are available only as residuals (Manager_Clarity_Residual) from the clarity extended regression.

---

# Task 6 — Final Result and Next Provenance Template

## Final Verdict

**IMPLEMENTATION PARTIALLY ALIGNED**

H9 is aligned to the research question with Compustat-only controls, sparse/expanded control separation, and proper model family organization. The sole gap is Manager clarity score (ClarityManager), which does not exist in the repository.

## Files Edited

1. `src/f1d/variables/build_h9_takeover_panel.py` — Removed CRSP/IBES builders, added CashHoldings, SalesGrowth, Intangibility, AssetGrowth builders
2. `src/f1d/econometric/run_h9_takeover_hazards.py` — Replaced FINANCIAL_CONTROLS with SPARSE_CONTROLS + EXPANDED_CONTROLS, removed uncertainty_var, added family tags, restructured model loop into sparse + expanded phases, updated report/table generation
3. `src/f1d/shared/variables/_compustat_engine.py` — Added Intangibility (INTAN/AT) and AssetGrowth (YoY AT growth) computation
4. `src/f1d/shared/variables/__init__.py` — Exported IntangibilityBuilder and AssetGrowthBuilder
5. `src/f1d/shared/variables/intangibility.py` — New file: IntangibilityBuilder class
6. `src/f1d/shared/variables/asset_growth.py` — New file: AssetGrowthBuilder class

## Final Output Run Paths

- **Panel**: `outputs/variables/takeover/2026-03-11_201042/`
- **Hazards**: `outputs/econometric/takeover/2026-03-11_201629/`

## What Is Now True About H9

1. **Sparse Compustat controls**: Size, BM, Lev, ROA, CashHoldings — used in all 9 sparse models
2. **Expanded Compustat controls**: + SalesGrowth, Intangibility, AssetGrowth — used in all 9 expanded robustness models
3. **No CRSP/IBES controls**: StockRet, MarketRet, SurpDec, EPS_Growth fully removed from code and outputs
4. **CEO clarity as PRIMARY**: ClarityCEO is the main construct (family: primary_style)
5. **Residuals as SECONDARY**: CEO_Clarity_Residual and Manager_Clarity_Residual are companion models (family: secondary_residual)
6. **Proper event definitions**: Uninvited = Hostile + Unsolicited; Friendly = Friendly + Neutral
7. **Cause-specific censoring**: 26 Unknown-type takeover events correctly censored in cause-specific models
8. **18 total models**: 9 sparse (3 variants x 3 events) + 9 expanded (3 variants x 3 events)
9. **Two-sided inference**: lifelines default, no one-tailed p-values
10. **Report structure**: PRIMARY STYLE and SECONDARY RESIDUAL sections separated; expanded robustness in separate section

## What Still Remains

1. **Manager clarity score unavailable**: ClarityManager does not exist in repo — cannot implement primary Manager clarity models (Family 2 from plan)
2. **LaTeX table structural issues**: `make_cox_hazard_table` produces a single mixed table with misaligned standard errors for the 18-model output. CSV and markdown report outputs are correct. This is a pre-existing issue in the shared LaTeX table generator, not an H9-specific bug.
3. **Provenance update**: `docs/provenance/H9.md` needs update to reflect Pass 05 changes (per plan: not done in this pass)

## Recommended Standard Provenance Outline for Next Pass

```
I. Suite Identity and Status
   - Suite ID (H9), hypothesis number (4.3), current status, last run date and output path

II. Research Question and Current Hypotheses
   - Primary question: Does clarity increase takeover likelihood, especially uninvited bids?
   - H9-A: beta(Clarity) < 0; H9-B: beta(Clarity, uninvited) < beta(Clarity, friendly)

III. Canonical Inputs and Upstream Dependencies
   - Data sources: Compustat (financial controls), SDC M&A (takeover events), clarity scores (4.1.1), clarity residuals (4.1.3)
   - Required upstream stages: Stage 3 panel build, clarity score estimation, clarity extended regression

IV. Sample Construction and Filters
   - Entry: first observed earnings call for firm; Exit: takeover announcement or end of sample
   - Main sample only (FF12 codes 1-7, 9-10, 12; excludes Finance=11 and Utility=8)
   - Counting-process format: one row per firm-year at risk

V. Variable Dictionary
   - Primary: ClarityCEO (CEO fixed-effect clarity score)
   - Secondary: CEO_Clarity_Residual, Manager_Clarity_Residual
   - Outcomes: Takeover (all), Takeover_Uninvited (Hostile+Unsolicited), Takeover_Friendly (Friendly+Neutral)
   - Sparse controls: Size, BM, Lev, ROA, CashHoldings
   - Expanded controls: + SalesGrowth, Intangibility, AssetGrowth

VI. Model Specification Register
   - 18 models: 3 families (CEO, CEO_Residual, Manager_Residual) x 3 events (All, Uninvited, Friendly) x 2 control blocks (sparse, expanded)
   - Estimator: CoxTimeVaryingFitter (counting-process format with start/stop columns)

VII. Output Artifacts and Active Run Paths
   - Panel: outputs/variables/takeover/{timestamp}/takeover_panel.parquet
   - Hazards: outputs/econometric/takeover/{timestamp}/ (hazard_ratios.csv, model_diagnostics.csv, .tex tables, report)

VIII. Verification Summary
   - 11/12 checks pass; 1 known limitation (ClarityManager unavailable)
   - All CRSP/IBES controls confirmed removed

IX. Known Limitations / Open Issues
   - ClarityManager does not exist in repo (Family 2 from plan cannot be implemented)
   - LaTeX table generator produces structural issues for 18-model output
   - Residual variable coverage lower than financial controls (~42-56% vs ~99%)

X. Change Log
   - Pass 03 (2026-03-08): Fixed cause-specific event indicator bug (was inflating events 8-9x)
   - Pass 05 (2026-03-11): Removed CRSP/IBES controls, added Compustat-only sparse/expanded blocks, separated primary/secondary model families, added Intangibility and AssetGrowth builders, restructured model loop, 18 models total
```

---

**Pass Completed**: 2026-03-11
