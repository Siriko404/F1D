# PRD: F1D Pipeline Refactoring - Descriptive Statistics & Documentation

**Project:** F1D Clarity Measure Pipeline
**Date:** 2025-01-17
**Status:** Planning Complete (Revised)

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Spec](#spec-requirements)
3. [Blueprint](#blueprint-implementation-plan)
4. [ToDo Checklist](#todo-checklist)

---

## CHANGELOG (Revisions)
- **Rev 1**: No extra scripts allowed - descriptive stats code must be inlined into each script
- **Rev 1**: Orchestrator and verify scripts to be archived (moved to ARCHIVE_OLD/)

---

## Executive Summary

This PRD documents a comprehensive refactoring of the F1D pipeline to achieve two goals:

1. **Add comprehensive descriptive statistics** to every script (input, process, output stats)
2. **Write a comprehensive README** documenting the entire pipeline in detail

### Scope
- **Active scripts only** (16 scripts across 4 phases, after archiving)
- **Orchestrator and verify scripts will be archived** (moved to ARCHIVE_OLD/)
- **No new scripts** - descriptive stats code inlined into each script
- No legacy scripts in ARCHIVE_OLD/ need to be modified
- Any dependencies on legacy scripts will be reported

### Scripts to Archive (Move to ARCHIVE_OLD/)
| Script | Reason |
|--------|--------|
| `1_Sample/1.0_BuildSampleManifest.py` | Orchestrator - runs subscripts sequentially |
| `2_Text/2.3_VerifyStep2.py` | Verification script - not core processing |
| `3_Financial/3.0_BuildFinancialFeatures.py` | Orchestrator - runs subscripts sequentially |

### Active Scripts to Refactor (16 total)
| Phase | Scripts | Count |
|-------|---------|-------|
| Phase 1 | 1.1, 1.2, 1.3, 1.4 | 4 |
| Phase 2 | 2.1, 2.2 | 2 |
| Phase 3 | 3.1, 3.2, 3.3 | 3 |
| Phase 4 | 4.1, 4.1.1, 4.1.2, 4.1.3, 4.1.4, 4.2, 4.3 | 7 |

### Output Format
- Descriptive stats: **Both log files AND separate CSV/MD files**
- README: **Detailed documentation** (not brief) covering input, process, and output logic for each script

### Implementation Constraint
- **NO NEW SCRIPTS** - All descriptive statistics code must be inlined directly into each existing script

---

## Spec: Requirements

### 1. Inline Descriptive Statistics Functions

#### 1.1 Function Specifications

**Implementation:** Inline functions in each script (no shared module)

**Functions to Add to Each Script:**

```python
def generate_descriptive_stats(df, stage_name, output_dir, timestamp):
    """
    Generate comprehensive descriptive statistics for a DataFrame.

    Args:
        df: pandas DataFrame to analyze
        stage_name: str, e.g., "input", "output", "intermediate"
        output_dir: Path to output directory
        timestamp: Execution timestamp

    Generates statistics for:
    - Numerical columns: count, mean, std, min, Q1, median, Q3, max, range, IQR, skew, kurtosis
    - Categorical columns: count, unique, mode, mode_freq, mode_pct
    - Temporal (datetime) columns: count, unique, min, max, range_days
    - Text/String columns: count, unique, avg_length, min_length, max_length, empty_count

    Outputs to:
    1. Log file (via DualWriter) - brief summary printed
    2. CSV (long format) - {stage}_stats_{timestamp}.csv
    3. Markdown (tables) - descriptive_stats_{timestamp}.md
    """

def print_stats_summary(stats_dict, dual_writer):
    """Print brief statistics summary to DualWriter (stdout + log)."""

def save_stats_csv(stats_dict, output_path):
    """Save statistics to CSV in long format."""

def save_stats_markdown(stats_dict, output_path):
    """Save statistics to Markdown with formatted tables."""
```

#### 1.2 Statistics by Data Type

**Numerical Columns:**
```
count, missing, missing_pct, mean, std, min, q25, median, q75, max,
range, iqr, skewness, kurtosis, sum, cv (coefficient of variation)
```

**Categorical Columns:**
```
count, missing, missing_pct, unique, mode, mode_freq, mode_pct,
n_below_5pct (categories with <5% frequency)
```

**Temporal (datetime) Columns:**
```
count, missing, unique, min, max, range_days
```

**Text/String Columns:**
```
count, missing, unique, avg_length, min_length, max_length,
empty_count, whitespace_count
```

**Boolean Columns:**
```
count, missing, true_count, true_pct, false_count, false_pct
```

#### 1.3 Output File Formats

**CSV Format** (`{stage}_stats_{timestamp}.csv`):
```csv
variable,dtype,stat_name,stat_value,stage
file_name,string,unique,286652,output
start_date,date,min,2002-01-15,output
Manager_QA_Uncertainty_pct,float,mean,2.34,output
Manager_QA_Uncertainty_pct,float,std,1.45,output
```

**Markdown Format** (`descriptive_stats_{step}_{timestamp}.md`):
```markdown
# Descriptive Statistics: Step 4.1

**Generated:** 2025-01-17 10:30:00
**Records:** 286,652

## Numerical Variables

| Variable | Mean | Std | Min | Max | Missing % |
|----------|------|-----|-----|-----|-----------|
| Manager_QA_Uncertainty_pct | 2.34 | 1.45 | 0.00 | 12.45 | 0.0% |
...
```

#### 1.4 Output Directory Convention

```
{output_dir}/descriptive_stats/
├── input_stats_{step}_{timestamp}.csv
├── output_stats_{step}_{timestamp}.csv
└── descriptive_stats_{step}_{timestamp}.md
```

---

### 2. Per-Script Statistics Requirements

#### Phase 1: Sample Building (1_Sample/)

**1.1_CleanMetadata.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Total records, missing per field, duplicate file_name count |
| Process | Invalid dates, cleaned strings, validation failures |
| Output | Records after cleaning, date coverage, field completeness |

**1.2_LinkEntities.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Total calls to link, available identifiers |
| Process | Tier 1 (PERMNO+date), Tier 2 (CUSIP8+date), Tier 3 (fuzzy >=92), Tier 4 (ticker), unmatched |
| Output | Final gvkey match rate, unique gvkeys, linkage quality distribution |

**1.3_BuildTenureMap.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Total CEO records, companies represented |
| Process | Overlapping tenures resolved, gaps detected, first CEOs |
| Output | Total tenure records, unique CEOs, date range, avg tenure length |

**1.4_AssembleManifest.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Input row counts, join key coverage |
| Process | Rows after each join, CEO match rate, industry assignment |
| Output | Final call count, CEO coverage %, complete case count, sample distribution |

#### Phase 2: Text Processing (2_Text/)

**Note:** Script `2.3_VerifyStep2.py` will be archived (not core processing).

**2.1_TokenizeAndCount.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Files per year, total documents, file sizes (MB) |
| Process | Tokens processed, dictionary hits per type, processing time |
| Output | Calls after aggregation, avg word_tokens per call, unc_pct/neg_pct distributions |

**2.2_ConstructVariables.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Calls with raw counts |
| Process | Calls with sufficient tokens, percentage ranges, consistency checks |
| Output | Variable list/completeness, distribution of key variables, correlation matrix |

#### Phase 3: Financial Features (3_Financial/)

**Note:** Script `3.0_BuildFinancialFeatures.py` (orchestrator) will be archived.

**3.1_FirmControls.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Calls with gvkey, available Compustat fields |
| Process | Ratio calculations, winsorization bounds, extremes capped |
| Output | Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, Volatility stats |

**3.2_MarketVariables.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Trading days, calls with return data |
| Process | Windows meeting min days, avg window length |
| Output | StockRet, MarketRet, Volatility, Delta stats |

**3.3_EventFlags.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | SDC deals, calls in sample period |
| Process | Matches by tier, events identified |
| Output | Takeover flag count/pct, type distribution |

#### Phase 4: Econometric Analysis (4_Econometric/)

**4.1_EstimateCeoClarity.py** (Baseline Model)
| Stage | Key Metrics |
|-------|-------------|
| Input | Total calls, variable completeness |
| Process | Rows after merges, complete cases, CEOs filtered, regression N |
| Output | Model diagnostics (N, CEOs, firms, R2, F, AIC, BIC), ClarityCEO distribution |

**4.1.1_EstimateCeoClarity_CeoSpecific.py** - Same structure, CEO-specific variables

**4.1.2_EstimateCeoClarity_Extended.py** - Extended controls, model comparison

**4.1.3_EstimateCeoClarity_Regime.py** - Dependent: NonCEO_Manager_QA_Uncertainty_pct

**4.1.4_EstimateCeoTone.py** - Dependent: NetTone (Positive - Negative)

**4.2_LiquidityRegressions.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Calls with Clarity, instrument coverage |
| Process | First-stage F-stat, OLS/IV coefficients |
| Output | Delta_Amihud, Delta_Corwin_Schultz regression results |

**4.3_TakeoverHazards.py**
| Stage | Key Metrics |
|-------|-------------|
| Input | Takeover events |
| Process | Event counts, censoring rate |
| Output | Hazard ratios, concordance, event summary |

---

### 3. README Specifications

#### 3.1 README Structure

**File:** `README.md` (NEW at project root)

```markdown
# F1D: CEO Clarity Measure from Earnings Calls

## Table of Contents
1. Overview
2. Pipeline Architecture
3. Data Sources
4. Installation and Setup
5. Pipeline Execution
6. Phase 1: Sample Building
7. Phase 2: Text Processing
8. Phase 3: Financial Features
9. Phase 4: Econometric Analysis
10. Outputs and Results
11. Troubleshooting
12. References
13. Appendix A: Variable Dictionary
```

#### 3.2 Section Requirements

**1. Overview**
- Purpose of F1D measure
- Key measures (ClarityCEO, ClarityRegime, Tone)
- Sample period and size

**2. Pipeline Architecture**
- Directory structure
- Design principles (deterministic, no-flags, timestamped outputs, dual-write logging)

**3. Data Sources**
- Table format: Source, Description, Size/Variables
- Earnings call data, LM dictionary, firm data, CEO data, event data

**4. Installation and Setup**
- Requirements (Python 3.8+, g++)
- Dependencies with pip install command
- Configuration (config/project.yaml)

**5. Pipeline Execution**
- Sequential execution commands for all phases
- Expected runtime per phase

**6. Phase 1: Sample Building**
- Overview paragraph
- Per-script subsections:
  - Purpose (1-2 sentences)
  - Input Data (table: Field, Description, Source)
  - Process (numbered steps)
  - Output (files and key fields)
  - Quality Checks

**7. Phase 2: Text Processing**
- Same structure as Phase 1
- Include key variable definitions table

**8. Phase 3: Financial Features**
- Same structure
- Include variable formulas where applicable

**9. Phase 4: Econometric Analysis**
- Same structure
- Include model specifications in LaTeX-like format
- Explain fixed effects and standard errors

**10. Outputs and Results**
- Directory structure diagram
- Key output files with descriptions

**11. Troubleshooting**
- Common issues with solutions
- Log file locations

**12. References**
- Academic papers
- Data documentation links

**13. Appendix A: Variable Dictionary**
- Comprehensive table: Variable, Type, Description, Source

---

## Blueprint: Implementation Plan

### Implementation Sequence

#### Step 1: Archive Orchestrator and Verify Scripts
**Priority:** 1

**Scripts to Move to ARCHIVE_OLD/:**
| From | To |
|------|-----|
| `1_Sample/1.0_BuildSampleManifest.py` | `ARCHIVE_OLD/1.0_BuildSampleManifest.py` |
| `2_Text/2.3_VerifyStep2.py` | `ARCHIVE_OLD/2.3_VerifyStep2.py` |
| `3_Financial/3.0_BuildFinancialFeatures.py` | `ARCHIVE_OLD/3.0_BuildFinancialFeatures.py` |

**Note:** After archiving, scripts must be run individually in sequence.

#### Step 2: Refactor Phase 4 Scripts
**Priority:** 2 (most complex, highest value)

**Scripts to Modify:**
1. `4_Econometric/4.1_EstimateCeoClarity.py`
2. `4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py`
3. `4_Econometric/4.1.2_EstimateCeoClarity_Extended.py`
4. `4_Econometric/4.1.3_EstimateCeoClarity_Regime.py`
5. `4_Econometric/4.1.4_EstimateCeoTone.py`
6. `4_Econometric/4.2_LiquidityRegressions.py`
7. `4_Econometric/4.3_TakeoverHazards.py`

**Changes per Script:**
1. Add inline `generate_descriptive_stats()` function (no imports)
2. Add helper functions: `print_stats_summary()`, `save_stats_csv()`, `save_stats_markdown()`
3. Call `generate_descriptive_stats()` after loading each data source (input stats)
4. Call after key transformations (process stats)
5. Call before saving outputs (output stats)
6. Create `descriptive_stats/` subdirectory in outputs
7. Generate CSV and markdown report files

#### Step 3: Refactor Phase 1 Scripts
**Priority:** 3 (foundation for downstream)

**Scripts to Modify:**
1. `1_Sample/1.1_CleanMetadata.py`
2. `1_Sample/1.2_LinkEntities.py`
3. `1_Sample/1.3_BuildTenureMap.py`
4. `1_Sample/1.4_AssembleManifest.py`

**Changes:** Same pattern as Phase 4 (inline functions, input/process/output stats)

#### Step 4: Refactor Phase 2 Scripts
**Priority:** 4

**Scripts to Modify:**
1. `2_Text/2.1_TokenizeAndCount.py`
2. `2_Text/2.2_ConstructVariables.py`

**Changes:** Same pattern as Phase 4

#### Step 5: Refactor Phase 3 Scripts
**Priority:** 5

**Scripts to Modify:**
1. `3_Financial/3.1_FirmControls.py`
2. `3_Financial/3.2_MarketVariables.py`
3. `3_Financial/3.3_EventFlags.py`

**Changes:** Same pattern as Phase 4

#### Step 6: Write README
**Priority:** 6

**Approach:**
1. Create `README.md` following the spec structure
2. Fill sections based on actual script analysis
3. Include real variable names, formulas, and output paths
4. Add code examples for sequential execution (no orchestrators)
5. Review for completeness

### Critical Files Reference

**Files to Archive (Move):**
| From | To |
|------|-----|
| `1_Sample/1.0_BuildSampleManifest.py` | `ARCHIVE_OLD/` |
| `2_Text/2.3_VerifyStep2.py` | `ARCHIVE_OLD/` |
| `3_Financial/3.0_BuildFinancialFeatures.py` | `ARCHIVE_OLD/` |

**Files to Create:**
| File | Purpose |
|------|---------|
| `README.md` | Comprehensive documentation |

**Files to Modify (Add inline stats functions):**
| Phase | Scripts | Count |
|-------|---------|-------|
| Phase 1 | 1.1, 1.2, 1.3, 1.4 | 4 |
| Phase 2 | 2.1, 2.2 | 2 |
| Phase 3 | 3.1, 3.2, 3.3 | 3 |
| Phase 4 | 4.1, 4.1.1, 4.1.2, 4.1.3, 4.1.4, 4.2, 4.3 | 7 |
| **Total** | | **16 scripts** |

### Inline Statistics Function Template

Each script will include this template (adapted for script-specific needs):

```python
# ==============================================================================
# Descriptive Statistics Functions (Inline - No External Module)
# ==============================================================================

def generate_descriptive_stats(df, stage_name, output_dir, timestamp, dual_writer=None):
    """
    Generate comprehensive descriptive statistics for a DataFrame.

    Args:
        df: pandas DataFrame to analyze
        stage_name: str, e.g., "input", "output", "intermediate"
        output_dir: Path to output directory
        timestamp: Execution timestamp
        dual_writer: Optional DualWriter instance for log output

    Returns:
        DataFrame with statistics (long format)
    """
    from pathlib import Path
    import pandas as pd
    from scipy import stats

    stats_list = []
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    datetime_cols = df.select_dtypes(include=['datetime64']).columns

    # Numerical stats
    for col in numeric_cols:
        col_data = df[col].dropna()
        stats_list.extend([
            {'variable': col, 'dtype': 'numeric', 'stat': 'count', 'value': len(col_data), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'missing', 'value': df[col].isna().sum(), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'missing_pct', 'value': df[col].isna().mean()*100, 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'mean', 'value': col_data.mean(), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'std', 'value': col_data.std(), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'min', 'value': col_data.min(), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'q25', 'value': col_data.quantile(0.25), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'median', 'value': col_data.median(), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'q75', 'value': col_data.quantile(0.75), 'stage': stage_name},
            {'variable': col, 'dtype': 'numeric', 'stat': 'max', 'value': col_data.max(), 'stage': stage_name},
        ])

    # Categorical stats
    for col in categorical_cols:
        stats_list.extend([
            {'variable': col, 'dtype': 'categorical', 'stat': 'count', 'value': len(df), 'stage': stage_name},
            {'variable': col, 'dtype': 'categorical', 'stat': 'unique', 'value': df[col].nunique(), 'stage': stage_name},
            {'variable': col, 'dtype': 'categorical', 'stat': 'missing', 'value': df[col].isna().sum(), 'stage': stage_name},
        ])
        # Mode if exists
        if df[col].notna().any():
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                stats_list.append({'variable': col, 'dtype': 'categorical', 'stat': 'mode', 'value': mode_val[0], 'stage': stage_name})

    # Datetime stats
    for col in datetime_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            stats_list.extend([
                {'variable': col, 'dtype': 'datetime', 'stat': 'count', 'value': len(col_data), 'stage': stage_name},
                {'variable': col, 'dtype': 'datetime', 'stat': 'min', 'value': col_data.min(), 'stage': stage_name},
                {'variable': col, 'dtype': 'datetime', 'stat': 'max', 'value': col_data.max(), 'stage': stage_name},
            ])

    stats_df = pd.DataFrame(stats_list)

    # Save CSV
    stats_dir = Path(output_dir) / 'descriptive_stats'
    stats_dir.mkdir(parents=True, exist_ok=True)
    csv_path = stats_dir / f'{stage_name}_stats_{timestamp}.csv'
    stats_df.to_csv(csv_path, index=False)

    # Save Markdown
    md_path = stats_dir / f'descriptive_stats_{timestamp}.md'
    _save_markdown_report(stats_df, md_path, stage_name, len(df))

    # Print summary
    if dual_writer:
        dual_writer.write(f"\n{'='*60}\n")
        dual_writer.write(f"Descriptive Statistics: {stage_name}\n")
        dual_writer.write(f"{'='*60}\n")
        dual_writer.write(f"  Records: {len(df):,}\n")
        dual_writer.write(f"  Columns: {len(df.columns)}\n")
        dual_writer.write(f"  Numeric: {len(numeric_cols)}, Categorical: {len(categorical_cols)}\n")
        dual_writer.write(f"  Saved to: {csv_path}\n")
        dual_writer.flush()

    return stats_df


def _save_markdown_report(stats_df, output_path, stage_name, n_records):
    """Append stats to markdown report."""
    from pathlib import Path

    # Read existing if exists
    if Path(output_path).exists():
        with open(output_path, 'r') as f:
            content = f.read()
    else:
        content = f"# Descriptive Statistics Report\n\nGenerated: {pd.Timestamp.now()}\n\n"

    # Add section for this stage
    content += f"\n## {stage_name.upper()} ({n_records:,} records)\n\n"

    # Numeric table
    numeric_stats = stats_df[stats_df['dtype'] == 'numeric'].pivot(index='variable', columns='stat', values='value')
    if not numeric_stats.empty:
        content += "### Numerical Variables\n\n"
        content += "| Variable | Count | Mean | Std | Min | Median | Max | Missing % |\n"
        content += "|----------|-------|------|-----|-----|--------|-----|----------|\n"
        for var in numeric_stats.index:
            row = numeric_stats.loc[var]
            content += f"| {var} | {row.get('count', 0):.0f} | {row.get('mean', 0):.2f} | {row.get('std', 0):.2f} | {row.get('min', 0):.2f} | {row.get('median', 0):.2f} | {row.get('max', 0):.2f} | {row.get('missing_pct', 0):.1f}% |\n"

    # Write
    with open(output_path, 'w') as f:
        f.write(content)
```

---

## ToDo Checklist

### Step 1: Archive Scripts
- [ ] Move `1_Sample/1.0_BuildSampleManifest.py` to `ARCHIVE_OLD/`
- [ ] Move `2_Text/2.3_VerifyStep2.py` to `ARCHIVE_OLD/`
- [ ] Move `3_Financial/3.0_BuildFinancialFeatures.py` to `ARCHIVE_OLD/`

### Phase 1 Refactoring (4 scripts)
- [ ] `1.1_CleanMetadata.py` - full stats implementation
- [ ] `1.2_LinkEntities.py` - include tier-specific stats
- [ ] `1.3_BuildTenureMap.py` - include tenure timeline stats
- [ ] `1.4_AssembleManifest.py` - include final manifest stats

### Phase 2 Refactoring (2 scripts)
- [ ] `2.1_TokenizeAndCount.py` - include tokenization metrics
- [ ] `2.2_ConstructVariables.py` - include variable construction stats

### Phase 3 Refactoring (3 scripts)
- [ ] `3.1_FirmControls.py` - include financial ratio stats
- [ ] `3.2_MarketVariables.py` - include return window stats
- [ ] `3.3_EventFlags.py` - include takeover event stats

### Phase 4 Refactoring (7 scripts)
- [ ] `4.1_EstimateCeoClarity.py`
  - [ ] Add inline `generate_descriptive_stats()` function
  - [ ] Add input stats for manifest, linguistic vars, controls
  - [ ] Add process stats for merging, filtering
  - [ ] Add output stats for CEO scores, model results
  - [ ] Create descriptive_stats/ subdir
  - [ ] Generate CSV and MD reports
- [ ] `4.1.1_EstimateCeoClarity_CeoSpecific.py` - same pattern
- [ ] `4.1.2_EstimateCeoClarity_Extended.py` - same pattern
- [ ] `4.1.3_EstimateCeoClarity_Regime.py` - same pattern
- [ ] `4.1.4_EstimateCeoTone.py` - same pattern
- [ ] `4.2_LiquidityRegressions.py`
  - [ ] Add stats for first stage, OLS, IV results
- [ ] `4.3_TakeoverHazards.py`
  - [ ] Add stats for Cox PH, Fine-Gray models

### README Documentation
- [ ] Create README.md structure
- [ ] Section 1: Overview
- [ ] Section 2: Pipeline Architecture
- [ ] Section 3: Data Sources
- [ ] Section 4: Installation and Setup
- [ ] Section 5: Pipeline Execution (sequential, no orchestrators)
- [ ] Section 6: Phase 1 (4 scripts: 1.1, 1.2, 1.3, 1.4)
- [ ] Section 7: Phase 2 (2 scripts: 2.1, 2.2)
- [ ] Section 8: Phase 3 (3 scripts: 3.1, 3.2, 3.3)
- [ ] Section 9: Phase 4 (7 scripts: 4.1, 4.1.1, 4.1.2, 4.1.3, 4.1.4, 4.2, 4.3)
- [ ] Section 10: Outputs and Results
- [ ] Section 11: Troubleshooting
- [ ] Section 12: References
- [ ] Appendix A: Variable Dictionary
- [ ] Review and refine

### Testing & Validation
- [ ] Run pipeline sequentially (no orchestrators)
- [ ] Verify all stats files are generated
- [ ] Verify log output includes stats summaries
- [ ] Compare outputs before/after (data should be identical)
- [ ] Review README for accuracy and completeness

---

## Dependency Report

**No legacy script dependencies found.** The active pipeline is fully self-contained:
- Phase 1 (1_Sample/) generates its own outputs
- Phase 2 (2_Text/) reads from Phase 1 outputs only
- Phase 3 (3_Financial/) reads from Phase 1 outputs only
- Phase 4 (4_Econometric/) reads from Phases 1, 2, 3 outputs

Scripts in `ARCHIVE_OLD/` and `ARCHIVE/` are not referenced by any active scripts.

**Scripts Being Archived:**
After moving orchestrators and verify scripts to ARCHIVE_OLD/, the pipeline will be run sequentially:
```bash
# Phase 1 (run in order)
python 2_Scripts/1_Sample/1.1_CleanMetadata.py
python 2_Scripts/1_Sample/1.2_LinkEntities.py
python 2_Scripts/1_Sample/1.3_BuildTenureMap.py
python 2_Scripts/1_Sample/1.4_AssembleManifest.py

# Phase 2
python 2_Scripts/2_Text/2.1_TokenizeAndCount.py
python 2_Scripts/2_Text/2.2_ConstructVariables.py

# Phase 3
python 2_Scripts/3_Financial/3.1_FirmControls.py
python 2_Scripts/3_Financial/3.2_MarketVariables.py
python 2_Scripts/3_Financial/3.3_EventFlags.py

# Phase 4
python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py
# ... etc
```

---

## Notes

- All existing functionality must be preserved (data outputs must be bitwise identical)
- The `DualWriter` pattern is already used in scripts; we're adding stats to it
- Descriptive stats files are additive; they don't change core outputs
- README should be a living document; include version/date
- **No new scripts will be created** - all stats code is inline in existing scripts
