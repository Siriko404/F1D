# Stage 3/4 Refactoring Progress Report

**Date:** 2026-02-19
**Status:** Phase 3 Complete (Post-Audit Fixes Applied)
**Author:** Claude Code Session

---

## Executive Summary

This document records the complete refactoring of Stage 3 (variables) and Stage 4 (econometric) architecture for the F1D project. The pilot implementation for the Manager Clarity hypothesis (4.1) has been successfully completed and extended to CEO Clarity (4.1.1), both verified end-to-end.

### Manager Clarity (4.1) Results (post-audit)
- **Main sample:** 47,890 observations, 2,197 managers, R² = 0.42
- **Finance sample:** 12,852 observations, 547 managers, R² = 0.31
- **Utility sample:** 2,950 observations, 133 managers, R² = 0.22
- **Total estimated managers:** 2,877 (reference entities excluded)
- **Global standardization:** mean=0.221, std=0.238 before z-scoring

### CEO Clarity (4.1.1) Results (post-audit)
- **Main sample:** 35,472 observations, 1,727 CEOs, R² = 0.35
- **Finance sample:** 7,978 observations, 366 CEOs, R² = 0.29
- **Utility sample:** 1,711 observations, 87 CEOs, R² = 0.16
- **Total estimated CEOs:** 2,180 (reference entities excluded)
- **Global standardization:** mean=0.019, std=0.238 before z-scoring

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
9. [Red Team Audit Findings and Fixes](#red-team-audit-findings-and-fixes)
10. [Next Steps](#next-steps)
11. [Verification Checklist](#verification-checklist)
12. [CEO Clarity (4.1.1) Extension](#ceo-clarity-411-extension)

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
│   │   ├── ceo_qa_uncertainty.py    # NEW (4.1.1)
│   │   ├── ceo_pres_uncertainty.py  # NEW (4.1.1)
│   │   ├── stock_return.py
│   │   ├── market_return.py
│   │   ├── eps_growth.py
│   │   ├── earnings_surprise.py
│   │   └── manifest_fields.py       # ceo_id, gvkey, ff12_code, etc.
│   └── latex_tables_accounting.py   # Accounting Review LaTeX generator
│
├── variables/                        # NEW: Stage 3 scripts
│   ├── __init__.py
│   ├── build_manager_clarity_panel.py
│   └── build_ceo_clarity_panel.py    # NEW (4.1.1)
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
    ├── test_manager_clarity.py       # NEW: Manager Clarity (4.1)
    └── test_ceo_clarity.py           # NEW: CEO Clarity (4.1.1)

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

### Variable Modules (13 files)

| File | Purpose |
|------|---------|
| `src/f1d/shared/variables/__init__.py` | Package init, exports all builders |
| `src/f1d/shared/variables/base.py` | VariableBuilder, VariableStats, VariableResult classes |
| `src/f1d/shared/variables/manager_qa_uncertainty.py` | Manager Q&A uncertainty |
| `src/f1d/shared/variables/manager_pres_uncertainty.py` | Manager presentation uncertainty |
| `src/f1d/shared/variables/analyst_qa_uncertainty.py` | Analyst Q&A uncertainty |
| `src/f1d/shared/variables/negative_sentiment.py` | Entire_All_Negative_pct |
| `src/f1d/shared/variables/ceo_qa_uncertainty.py` | CEO-only Q&A uncertainty **(NEW 4.1.1)** |
| `src/f1d/shared/variables/ceo_pres_uncertainty.py` | CEO-only presentation uncertainty **(NEW 4.1.1)** |
| `src/f1d/shared/variables/stock_return.py` | StockRet |
| `src/f1d/shared/variables/market_return.py` | MarketRet |
| `src/f1d/shared/variables/eps_growth.py` | EPS_Growth |
| `src/f1d/shared/variables/earnings_surprise.py` | SurpDec |
| `src/f1d/shared/variables/manifest_fields.py` | ceo_id, gvkey, ff12_code, start_date |

### Stage 3/4 Scripts (6 files)

| File | Purpose |
|------|---------|
| `src/f1d/variables/__init__.py` | Package init |
| `src/f1d/variables/build_manager_clarity_panel.py` | Stage 3: Build Manager Clarity panel |
| `src/f1d/variables/build_ceo_clarity_panel.py` | Stage 3: Build CEO Clarity panel **(NEW 4.1.1)** |
| `src/f1d/econometric/test_manager_clarity.py` | Stage 4: Manager Clarity hypothesis test |
| `src/f1d/econometric/test_ceo_clarity.py` | Stage 4: CEO Clarity hypothesis test **(NEW 4.1.1)** |
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

## Red Team Audit Findings and Fixes

After the initial implementation was verified end-to-end, a systematic red team audit was conducted. Ten bugs were identified and fixed across both Manager and CEO Clarity scripts.

### FIX-1: Column Conflict on Merge

**Severity:** High — silent data corruption  
**Files:** `build_manager_clarity_panel.py`, `build_ceo_clarity_panel.py`

**Problem:** Linguistic variable files contain columns (`gvkey`, `year`, `start_date`) that also appear in the manifest. Merging on `file_name` without dropping these produced silent `_x`/`_y` pandas suffix columns, creating duplicate data with no warning.

**Fix:** Explicitly drop all manifest-column overlaps from each variable DataFrame before merging:

```python
manifest_cols = set(df.columns)
cols_to_drop = [c for c in var_df.columns if c in manifest_cols and c != "file_name"]
var_df = var_df.drop(columns=cols_to_drop)
```

### FIX-2: Config Path CWD-Relative Fragility

**Severity:** Medium — runtime error if not run from project root  
**Files:** `build_manager_clarity_panel.py`, `build_ceo_clarity_panel.py`

**Problem:** `get_config()` and `load_variable_config()` defaulted to `Path("config/project.yaml")` — a CWD-relative path. Both scripts correctly computed `root` from `__file__`, but passed it to variable builders while calling config loaders with no path argument.

**Fix:** Pass the explicit path derived from script location:

```python
config = get_config(root / "config" / "project.yaml")
variable_configs = load_variable_config(root / "config" / "variables.yaml")
```

### FIX-3: Per-Sample Standardization (Catastrophic)

**Severity:** Critical — econometric invalidity  
**Files:** `test_manager_clarity.py`, `test_ceo_clarity.py`

**Problem:** `ClarityManager`/`ClarityCEO` scores were standardized independently per sample (Main, Finance, Utility) before concatenation. A manager with γ=0.3 in the Main sample and another with γ=0.3 in the Finance sample would get identical z-scores even if the Finance sample had a completely different distribution. This makes cross-sample comparisons meaningless.

**Fix:** Collect all raw gamma values first, then standardize globally across all 2,877/2,180 estimated entities in a single pass:

```python
# Collect raw scores from all samples
all_rows = []
for sample, fe_dict in all_fixed_effects.items():
    for entity_id, gamma in fe_dict.items():
        all_rows.append({"ceo_id": entity_id, "sample": sample, "gamma": gamma})

# Standardize globally
df = pd.DataFrame(all_rows)
mean_gamma = df["gamma"].mean()
std_gamma = df["gamma"].std()
df["ClarityScore"] = -(df["gamma"] - mean_gamma) / std_gamma  # Note: negated
```

### FIX-4: LaTeX Entity Label Hardcoded

**Severity:** Low — incorrect table output  
**Files:** `src/f1d/shared/latex_tables_accounting.py`, both test scripts

**Problem:** `make_accounting_table()` always wrote "N Managers" in the diagnostics panel row — wrong for CEO Clarity tables.

**Fix:** Added `entity_label: str = "N Entities"` parameter to `make_accounting_table()` and `make_diagnostics_table()`. Test scripts pass `entity_label="N CEOs"` / `entity_label="N Managers"` accordingly.

### FIX-5: No Duplicate Detection on Merge

**Severity:** High — silent row fan-out  
**Files:** `build_manager_clarity_panel.py`, `build_ceo_clarity_panel.py`

**Problem:** If any variable builder returned duplicate `file_name` rows, the left merge would silently multiply rows, inflating the panel with no warning.

**Fix:** Assert uniqueness before every merge, raising `ValueError` immediately on fan-out:

```python
dupes = var_df["file_name"].duplicated().sum()
if dupes > 0:
    raise ValueError(f"{name}: {dupes} duplicate file_name rows — merge would fan-out")
```

### FIX-6: Reference Entity Artifact in Output

**Severity:** Medium — spurious data point in clarity_scores.parquet  
**Files:** `test_manager_clarity.py`, `test_ceo_clarity.py`

**Problem:** The statsmodels reference category (alphabetically first CEO/manager) gets `gamma_i = 0` by normalization convention, not estimation. Including this artificial zero in `clarity_scores.parquet` creates a ghost data point with false precision.

**Fix:** After extracting fixed effects, identify the reference entity (absent from model params), exclude it from the output parquet, and log the count:

```python
estimated_ids = set(fe_dict.keys())  # from model params
all_ids = set(df_sample["ceo_id"].unique())
reference_ids = all_ids - estimated_ids  # convention zeros
# Only write estimated entities to clarity_scores.parquet
```

### FIX-7: Dead YAML Configuration Section

**Severity:** Low — misleading false documentation  
**Files:** `config/variables.yaml`

**Problem:** The `hypothesis_tests:` section in `variables.yaml` was never read by any script — `load_variable_config()` only returns the `variables:` section. Developers reading the YAML might incorrectly believe these settings were active.

**Fix:** Removed the dead `hypothesis_tests:` section entirely.

### FIX-8: Formula Log Truncation

**Severity:** Low — debugging/reproducibility  
**Files:** `test_manager_clarity.py`, `test_ceo_clarity.py`

**Problem:** `formula[:80]` in the log statement silently truncated the formula, hiding the `C(year)` year fixed effect from printed output.

**Fix:** Removed the `[:80]` slice — full formula is now printed.

### FIX-9: NaN ff12_code Assigned to Main Sample

**Severity:** High — sample contamination  
**Files:** `test_manager_clarity.py`, `test_ceo_clarity.py`

**Problem:** Rows with unknown industry (`NaN` in `ff12_code`) fell through the sample assignment logic and were silently included in regressions via the Main sample. Unknown-industry firms should be excluded.

**Fix:** Explicitly filter out `NaN ff12_code` rows after complete-cases filtering:

```python
df_reg = df_reg[df_reg["ff12_code"].notna()]
```
This dropped 8,276 Manager rows and 5,887 CEO rows — a material difference.

### FIX-10: Missing CEO/Manager Metadata in clarity_scores.parquet

**Severity:** Low — downstream usability  
**Files:** `test_manager_clarity.py`, `test_ceo_clarity.py`

**Problem:** `clarity_scores.parquet` only contained `ceo_id` and `ClarityScore`. Downstream analysis would need to re-join just to get the entity name or call count.

**Fix:** Join `ceo_name` (or `manager_name`) and `n_calls` from the panel before saving:

```python
meta = panel.groupby("ceo_id").agg(
    ceo_name=("ceo_name", "first"),
    n_calls=("file_name", "count")
).reset_index()
clarity_df = clarity_df.merge(meta, on="ceo_id", how="left")
```

### Post-Audit Verification

Pipeline re-run after all 10 fixes confirmed clean execution:

| Script | Rows | Entities | Outcome |
|--------|------|----------|---------|
| `build_manager_clarity_panel.py` | 112,968 | — | 0 row delta on every merge |
| `build_ceo_clarity_panel.py` | 112,968 | — | 0 row delta on every merge |
| `test_manager_clarity.py` | 47,890 / 12,852 / 2,950 | 2,877 managers | R²=0.42/0.31/0.22 |
| `test_ceo_clarity.py` | 35,472 / 7,978 / 1,711 | 2,180 CEOs | R²=0.35/0.29/0.16 |

---

## Next Steps

### Completed Scripts (v1 Architecture → New Architecture)

| Script | Status |
|--------|--------|
| 4.1 Manager Clarity | ✅ Complete |
| 4.1.1 CEO Clarity | ✅ Complete |

### Short Term (Next v1 Scripts to Refactor)

Extend the architecture to remaining v1 econometric scripts:

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

### Manager Clarity (4.1) — Stage 3

- [x] All 9 variables load successfully
- [x] Panel has 112,968 rows (matches manifest)
- [x] Panel has 17 columns (all expected variables)
- [x] Sample distribution is correct:
  - Main: 88,205 calls
  - Finance: 20,482 calls
  - Utility: 4,281 calls
- [x] Summary stats CSV generated
- [x] Report markdown generated

### Manager Clarity (4.1) — Stage 4

- [x] Panel loads from Stage 3
- [x] Complete cases filter works (72,608 rows)
- [x] NaN ff12_code rows excluded (8,276 dropped) — FIX-9
- [x] Regressions run for all 3 samples
- [x] Reference entity excluded from clarity_scores.parquet — FIX-6
- [x] Manager fixed effects extracted
- [x] ClarityManager scores standardized globally (mean=0, std=1) — FIX-3
- [x] ceo_name and n_calls joined into clarity_scores.parquet — FIX-10
- [x] LaTeX table generated with "N Managers" label — FIX-4
- [x] Full formula logged (no truncation) — FIX-8
- [x] Report markdown generated

| Sample | N Obs | N Managers | R² | Status |
|--------|-------|------------|-----|--------|
| Main | 47,890 | 2,197 | 0.4166 | ✅ |
| Finance | 12,852 | 547 | 0.3052 | ✅ |
| Utility | 2,950 | 133 | 0.2172 | ✅ |

### CEO Clarity (4.1.1) — Stage 3

- [x] All 9 variables load successfully (uses CEO_QA/CEO_Pres instead of Manager_QA/Manager_Pres)
- [x] Panel has 112,968 rows (matches manifest)
- [x] Panel has 17 columns (all expected variables)
- [x] Sample distribution is correct:
  - Main: 88,205 calls
  - Finance: 20,482 calls
  - Utility: 4,281 calls
- [x] Summary stats CSV generated
- [x] Report markdown generated

### CEO Clarity (4.1.1) — Stage 4

- [x] Panel loads from Stage 3
- [x] Complete cases filter works (51,730 rows)
- [x] NaN ff12_code rows excluded (5,887 dropped) — FIX-9
- [x] Regressions run for all 3 samples
- [x] Reference entity excluded from clarity_scores.parquet — FIX-6
- [x] CEO fixed effects extracted
- [x] ClarityCEO scores standardized globally (mean=0, std=1) — FIX-3
- [x] ceo_name and n_calls joined into clarity_scores.parquet — FIX-10
- [x] LaTeX table generated with "N CEOs" label — FIX-4
- [x] Full formula logged (no truncation) — FIX-8
- [x] Clarity scores saved (`clarity_scores.parquet`, 2,180 CEOs)
- [x] Regression summaries saved for all 3 samples
- [x] Report markdown generated

| Sample | N Obs | N CEOs | R² | Status |
|--------|-------|--------|-----|--------|
| Main | 35,472 | 1,727 | 0.3539 | ✅ |
| Finance | 7,978 | 366 | 0.2948 | ✅ |
| Utility | 1,711 | 87 | 0.1596 | ✅ |

---

## CEO Clarity (4.1.1) Extension

### Overview

CEO Clarity (4.1.1) follows the identical architecture as Manager Clarity (4.1) with two key differences:

| Aspect | Manager Clarity (4.1) | CEO Clarity (4.1.1) |
|--------|----------------------|---------------------|
| Dependent variable | `Manager_QA_Uncertainty_pct` | `CEO_QA_Uncertainty_pct` |
| Speech control | `Manager_Pres_Uncertainty_pct` | `CEO_Pres_Uncertainty_pct` |
| Score column | `ClarityManager` | `ClarityCEO` |
| Output directory | `outputs/variables/manager_clarity/` | `outputs/variables/ceo_clarity/` |
| Results directory | `outputs/econometric/manager_clarity/` | `outputs/econometric/ceo_clarity/` |

### Files Added

| File | Purpose |
|------|---------|
| `src/f1d/shared/variables/ceo_qa_uncertainty.py` | CEO-only Q&A uncertainty variable builder |
| `src/f1d/shared/variables/ceo_pres_uncertainty.py` | CEO-only presentation uncertainty builder |
| `src/f1d/variables/build_ceo_clarity_panel.py` | Stage 3: Build CEO Clarity panel |
| `src/f1d/econometric/test_ceo_clarity.py` | Stage 4: CEO Clarity fixed effects regression |

### Files Modified

| File | Change |
|------|--------|
| `src/f1d/shared/variables/__init__.py` | Registered `CEOQAUncertaintyBuilder`, `CEOPresUncertaintyBuilder` |
| `config/variables.yaml` | Added `ceo_qa_uncertainty`, `ceo_pres_uncertainty` variable configs and `ceo_clarity` hypothesis test config |

### Type Errors Fixed

During implementation, pre-existing type errors across the Manager Clarity files were discovered and fixed in both Manager and CEO scripts:

| Error | Files | Fix |
|-------|-------|-----|
| `main(year_start: int = None)` — `None` not assignable to `int` | `build_manager_clarity_panel.py`, `build_ceo_clarity_panel.py` | Changed to `Optional[int]` |
| `run_regression` return type excluded `None` from `df_reg` | `test_manager_clarity.py`, `test_ceo_clarity.py` | Changed to `tuple[Any, Optional[pd.DataFrame], Set[Any]]` |
| `smf` possibly unbound (conditional import) | `test_manager_clarity.py`, `test_ceo_clarity.py` | Pre-assigned `smf: Any = None` before try block |
| `index.get_loc(i) + 1` — get_loc returns `int \| slice \| ndarray` | `test_manager_clarity.py` | Replaced with `enumerate(..., start=1)` |
| `if model is None: continue` — doesn't narrow `df_reg` from `Optional` | `test_manager_clarity.py`, `test_ceo_clarity.py` | Changed to `if model is None or df_reg is None: continue` |

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

# Stage 3: Panel building
python -m f1d.variables.build_manager_clarity_panel   # 4.1 Manager Clarity
python -m f1d.variables.build_ceo_clarity_panel       # 4.1.1 CEO Clarity

# Stage 4: Hypothesis tests
python -m f1d.econometric.test_manager_clarity        # 4.1 Manager Clarity
python -m f1d.econometric.test_ceo_clarity            # 4.1.1 CEO Clarity
```

---

*End of Report*

---

## Phase 4 Complete (Full-Scale Pipeline Validation)
**Date:** 2026-02-21

The final phase involved extending the canonical architecture to all 15 hypothesis suites across Stage 3 and Stage 4. 

### Key Accomplishments:
1. **Canonical `panel_utils` Extraction**: Removed 13 duplicated copies of `assign_industry_sample` and 7 duplicated copies of `attach_fyearq`. Both functions now reside in `src/f1d/shared/variables/panel_utils.py` and are imported uniformly by all 14 Stage 3 panel builders and 15 Stage 4 econometric scripts.
2. **Adversarial Audit Resolutions**: 
    - Fixed H8 `start_date` unconditional coercion.
    - Added idempotency `.copy()` return to `attach_fyearq`.
    - Removed `sys.exit(1)` from H0.5, returning `None` instead.
    - Updated H0.2 documentation to correctly state standardizations are "per-sample" instead of "globally".
    - Fixed `load_variable_config()` empty argument calls in H10.
3. **Econometric Pipeline Unbricking (H3-H7)**:
    - Addressed `KeyError: 'sample'` crashes in `run_h3` through `run_h7` by appending `"ff12_code"` to the column inclusions inside `read_parquet()` and implementing dynamic `assign_industry_sample()` checks immediately after data loading.
    - Fixed H8 PyArrow read schema errors by loosening strict `columns=[]` restrictions when loading datasets without `ceo_id` and `ff12_code`.
4. **Full-Scale Execution**: All 15 Stage 4 scripts (`run_h0_1` to `run_h10`) successfully processed at full scale and generated complete outputs with zero silent failures or NaN propagations.

