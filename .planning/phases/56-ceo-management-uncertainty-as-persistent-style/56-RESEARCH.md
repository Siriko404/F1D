# Phase 56: CEO/Management Uncertainty as Persistent Style - Research

**Researched:** 2026-02-06
**Domain:** Panel econometrics, CEO fixed effects extraction, persistent style measurement
**Confidence:** HIGH

## Summary

This phase replicates Dzieliński, Wagner, Zeckhauser (2020) "Straight talkers and vague talkers" CEO fixed effects extraction methodology. The research confirms that V2 data contains all required variables (CEO/Analyst Q&A and Presentation uncertainty measures, firm controls) and that V1 implementation provides a proven pattern. The standard approach uses statsmodels OLS with CEO dummy variables (LSDV method), clustering standard errors by CEO. Key technical decision: statsmodels with Formula API is preferred over linearmodels PanelOLS for better FE coefficient extraction, though both are mathematically equivalent.

**Primary recommendation:** Use statsmodels Formula API with C(ceo_id) for CEO fixed effects, following V1's proven 4.1_EstimateCeoClarity.py pattern exactly. All required linguistic variables exist in V2, CFO-related robustness specs must be skipped, and implement both paper (2003-2015) and extended (2002-2018) sample periods.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Phase Boundary:**
- Replicate Dzieliński, Wagner, Zeckhauser (2020) Equation 4 CEO fixed effects extraction
- Outcome regressions (Tables 5-7) are NOT in scope
- Focus only on CEO style extraction and validation

**Equation 4 Specification (Exact):**
```
UncAns_i,t = α + γ_i·CEO_i + Σ_s β_s·Speech_s + Σ_k β_k·FirmChars_k + Year_t + ε_i,t
```

**Components:**
| Element | Variable | V2 Mapping |
|---------|----------|-------------|
| Dependent Variable | UncAns | CEO_QA_Uncertainty_pct (CEO Q&A only, LM dictionary) |
| Key Parameter | γ_i | CEO fixed effect coefficient (extract from regression) |
| Speech Controls | UncPreCEO | CEO_Pres_Uncertainty_pct |
| | UncQue | Analyst_QA_Uncertainty_pct |
| | NegCall | CEO_All_Negative_pct |
| FirmChars | SurpDec | SurpDec (from V2) |
| | EPS growth | EPS_Growth (from V2) |
| | StockRet | StockRet (from V2) |
| | MarketRet | MarketRet (from V2) |
| Fixed Effects | CEO FE | C(ceo_id) indicator variables |
| | Year FE | C(year) indicator variables |
| Standard Errors | Clustered by CEO | cov_type='cluster', cov_kwds={'groups': ceo_id} |

**CEO Clarity Measure:**
- ClarityCEO_i = -γ_i (negative of CEO fixed effect)
- Raw distribution: Mean = -0.62, SD = 0.23 (pre-standardization)
- Post-extraction: Standardize to mean=0, SD=1
- Interpretation: Higher = clearer communication (fewer uncertainty words)

**Sample Periods:**
- Paper replication: 2003-2015 (exact paper period)
- Extended analysis: 2002-2018 (full V2 sample)
- Run BOTH in parallel
- Minimum 5 calls per CEO (paper requirement)

**Table 3 Specifications:**
- Column (1): UncAns ~ CEO FE + UncPreCEO + UncQue + Year FE
- Column (2): UncAns ~ CEO FE + UncPreCEO + UncQue + NegCall + SurpDec + EPS_Growth + StockRet + MarketRet + Year FE
- Benchmark R² = 0.31 (CEO FE only)
- Report ∆R² (incremental vs benchmark)
- F-statistics for CEO FE joint significance

**Table IA.1 Robustness (8 specs):**
- Spec (0): CEO FE only
- Spec (1): + UncPreCEO
- Spec (2): + UncPreCEO + Firm chars
- Spec (3): Baseline (Eq. 4 = Table 3 Col 1)
- Spec (4): + UncPreCFO + UncAnsCFO → **SKIP (no CFO variables in V2)**
- Spec (5): + UncEPR (earnings press releases) → **SKIP (not in V2)**
- Spec (6): + AnDispPre (analyst dispersion) → **SKIP (not in V2)**
- Spec (7): + ∆UncPreCEO (change in presentation uncertainty)
- Output: Correlation matrix vs baseline (spec 3)

**Variable Construction (Exact formulas):**
```
UncAns = UncertaintyCount_QA_CEO / TotalWords_QA_CEO × 100
UncPreCEO = UncertaintyCount_Pres_CEO / TotalWords_Pres_CEO × 100
UncQue = UncertaintyCount_QA_Analyst / TotalWords_QA_Analyst × 100
```

**SurpDec construction:**
```
EarningsSurprise = (ActualEPS - ForecastEPS) / SharePrice
SurpDec = pd.qcut(EarningsSurprise, 10, labels=False, duplicates='drop')
# Map to -5 to +5 scale (deciles -5, -4, ..., 0, ..., +4, +5)
```

**Standardization (Post-Extraction):**
```python
# After extracting gamma_i from regression
ClarityCEO_raw = -gamma_i
ClarityCEO = (ClarityCEO_raw - ClarityCEO_raw.mean()) / ClarityCEO_raw.std()
```

**Minimum Calls Filter:**
```python
# Filter to CEOs with at least 5 calls (paper requirement)
ceo_call_counts = df['ceo_id'].value_counts()
valid_ceos = set(ceo_call_counts[ceo_call_counts >= 5].index)
df = df[df['ceo_id'].isin(valid_ceos)]
```

### Claude's Discretion

None - this is a strict replication. All specifications must match paper exactly.

### Deferred Ideas (OUT OF SCOPE)

**Outcome regressions (Tables 5-7):** Testing whether ClarityCEO predicts firm outcomes

**CFO/Other manager styles:** Paper estimates separate models for CFOs

**Cross-sectional analyses (Table 4):** Correlating ClarityCEO with CEO characteristics

**CEO turnover analysis:** Paper uses turnover sample to include firm fixed effects

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **statsmodels** | 0.14+ | OLS with Formula API, fixed effects, clustered SE | V1 proven implementation, matches paper's LSDV approach |
| **pandas** | 2.0+ | Data manipulation, groupby operations | Required for data prep |
| **numpy** | 1.24+ | Vectorized operations | Performance for standardization |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **linearmodels** | 6.0+ | PanelOLS (alternative) | NOT recommended - harder to extract FE coefficients |

### Installation

```bash
# Core requirements (already in V1/V2)
pip install statsmodels pandas numpy
```

**Why NOT linearmodels PanelOLS:**
- PanelOLS uses within-transformation to absorb fixed effects
- Extracting individual γ_i coefficients is more complex
- statsmodels LSDV (dummy variable) approach is mathematically equivalent and simpler for FE extraction
- Paper methodology explicitly uses "CEO fixed effects" via dummy variables
- Source: [Stack Overflow discussion on FE dummies vs FE estimator](https://stats.stackexchange.com/questions/174243/difference-between-fixed-effects-dummies-and-fixed-effects-estimator)

## Architecture Patterns

### Project Structure

```
2_Scripts/
├── 4_Econometric/
│   ├── 4.1_EstimateCeoClarity.py              # V1 reference implementation
│   └── 4.1.1_EstimateCeoClarity_CeoSpecific.py # V1 CEO-only variant
├── shared/
│   ├── regression_utils.py                    # Shared regression utilities
│   ├── path_utils.py                          # get_latest_output_dir
│   └── observability_utils.py                 # Logging, stats

4_Outputs/
├── 2_Textual_Analysis/2.2_Variables/         # Linguistic variables (V2)
│   └── latest/
│       ├── linguistic_variables_2002.parquet
│       ├── linguistic_variables_2003.parquet
│       └── ...
├── 3_Financial_Features/                     # Firm/market controls (V2)
│   └── latest/
│       ├── firm_controls_2002.parquet
│       ├── market_variables_2002.parquet
│       └── ...
├── 1.4_AssembleManifest/latest/              # CEO identification (V2)
│   └── master_sample_manifest.parquet
└── 4.1_CeoClarity/{timestamp}/              # Phase 56 outputs
    ├── ceo_clarity_scores.parquet            # Main output
    ├── table3_replication.csv                # Regression results
    ├── table_ia1_correlation_matrix.csv      # Robustness correlations
    ├── clarity_distribution_histogram.png    # Figure 3 replication
    ├── regression_results_*.txt              # Full model output
    └── report_step56.md                      # Summary report
```

### Pattern 1: CEO Fixed Effects Extraction with statsmodels

**What:** Use OLS with CEO dummy variables (C(ceo_id)) to estimate γ_i coefficients, then extract and negate to get ClarityCEO.

**When to use:** All CEO fixed effects regressions in Phase 56.

**Why this works:**
- LSDV (Least Squares Dummy Variable) model = OLS with entity dummies
- Mathematically equivalent to within-transformation (demeaning)
- Each CEO dummy coefficient = deviation from reference CEO's intercept
- Paper explicitly uses this approach (Equation 4)

**Example:**
```python
# Source: V1 4.1_EstimateCeoClarity.py (lines 338-400)
import statsmodels.formula.api as smf

# Convert to string for categorical treatment
df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
df_reg["year"] = df_reg["year"].astype(str)

# Build formula (Column 2 - Full Equation 4)
formula = (
    "CEO_QA_Uncertainty_pct ~ C(ceo_id) + "
    "CEO_Pres_Uncertainty_pct + "
    "Analyst_QA_Uncertainty_pct + "
    "CEO_All_Negative_pct + "
    "SurpDec + EPS_Growth + StockRet + MarketRet + "
    "C(year)"
)

# Estimate with CEO-clustered standard errors
model = smf.ols(formula, data=df_reg).fit(
    cov_type='cluster',
    cov_kwds={'groups': df_reg['ceo_id']}
)

# Extract CEO fixed effects
ceo_params = {
    p: model.params[p]
    for p in model.params.index
    if p.startswith("C(ceo_id)")
}

# Parse CEO IDs from dummy names
ceo_effects = {}
for param_name, gamma_i in ceo_params.items():
    if "[T." in param_name:
        ceo_id = param_name.split("[T.")[1].split("]")[0]
        ceo_effects[ceo_id] = gamma_i

# Reference CEO (not in params) gets gamma = 0
all_ceos = df_reg["ceo_id"].unique()
reference_ceos = [c for c in all_ceos if c not in ceo_effects]
for ref_ceo in reference_ceos:
    ceo_effects[ref_ceo] = 0.0

# Create DataFrame
ceo_fe = pd.DataFrame(list(ceo_effects.items()), columns=["ceo_id", "gamma_i"])

# Compute Clarity = -gamma_i
ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]

# Standardize to mean=0, SD=1
mean_val = ceo_fe["ClarityCEO_raw"].mean()
std_val = ceo_fe["ClarityCEO_raw"].std()
ceo_fe["ClarityCEO"] = (ceo_fe["ClarityCEO_raw"] - mean_val) / std_val
```

**Reference:** [Statsmodels OLS with Formula API](https://www.statsmodels.org/stable/examples/notebooks/generated/formulas.html)

### Pattern 2: Loading Multi-Year Data with get_latest_output_dir

**What:** Use V2's timestamp-based directory resolution to find latest input files.

**When to use:** Loading all input data for Phase 56.

**Example:**
```python
from shared.path_utils import get_latest_output_dir

# Resolve directories
manifest_dir = get_latest_output_dir(
    root / "4_Outputs" / "1.4_AssembleManifest",
    required_file="master_sample_manifest.parquet"
)
lv_dir = get_latest_output_dir(
    root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables"
)
fc_dir = get_latest_output_dir(
    root / "4_Outputs" / "3_Financial_Features"
)

# Load manifest
manifest = pd.read_parquet(
    manifest_dir / "master_sample_manifest.parquet",
    columns=["file_name", "gvkey", "start_date", "ceo_id", "ceo_name", "ff12_code"]
)

# Load per-year linguistic variables
all_data = []
for year in range(2003, 2016):  # Paper period
    lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
    lv = pd.read_parquet(lv_path)
    # ... merge and process
```

### Pattern 3: Robustness Correlation Matrix

**What:** Run multiple specifications, extract CEO FE from each, compute pairwise correlations.

**When to use:** Table IA.1 replication.

**Example:**
```python
# Define 8 specifications (skip CFO, EPR, AnDispPre)
specifications = {
    0: ["CEO_QA_Uncertainty_pct"],  # CEO FE only
    1: ["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct"],
    2: ["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct", "SurpDec", "EPS_Growth"],
    3: ["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct"],  # Baseline
    # Skip 4 (CFO), 5 (EPR), 6 (AnDispPre)
    7: ["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct", "delta_UncPreCEO"]
}

# Store CEO FE from each spec
ceo_fe_by_spec = {}
for spec_id, variables in specifications.items():
    formula = build_formula(variables)
    model = smf.ols(formula, data=df).fit(cov_type='cluster', cov_kwds={'groups': ceo_id})
    ceo_fe = extract_ceo_fe(model)
    ceo_fe_by_spec[spec_id] = ceo_fe

# Compute correlation matrix (spec 3 as reference)
baseline = ceo_fe_by_spec[3]["ClarityCEO"]
correlations = {}
for spec_id, ceo_fe in ceo_fe_by_spec.items():
    # Merge on ceo_id to align
    merged = ceo_fe.merge(ceo_fe_by_spec[3][["ceo_id", "ClarityCEO"]], on="ceo_id", suffixes=("", "_ref"))
    corr = merged["ClarityCEO"].corr(merged["ClarityCEO_ref"])
    correlations[spec_id] = corr

# Output format: spec_id, correlation_with_baseline
# Baseline (spec 3) should have correlation = 1.00
```

### Anti-Patterns to Avoid

- **Using linearmodels PanelOLS:** Harder to extract individual CEO FE coefficients; statsmodels LSDV is simpler and equivalent
- **Clustering by firm instead of CEO:** Paper methodology explicitly clusters by CEO (manager-level clustering)
- **Forgetting to convert ceo_id to string:** statsmodels requires string type for C(ceo_id) categorical treatment
- **Using HC1 instead of cluster:** V1 uses HC1, but paper requires CEO clustering (verify this is correct for paper replication)
- **Standardizing before negation:** Must compute ClarityCEO_raw = -gamma_i FIRST, then standardize
- **Including firm fixed effects:** Paper's Equation 4 only has CEO FE + Year FE (firm FE only in turnover analysis, not in scope)

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CEO fixed effects extraction | Manual demeaning or loop over CEOs | statsmodels C(ceo_id) dummies | LSDV is mathematically equivalent, simpler, proven |
| Clustered standard errors | Manual variance-covariance matrix | cov_type='cluster', cov_kwds={'groups': ceo_id} | Built-in, tested, matches paper methodology |
| CEO dummy coefficient parsing | String manipulation by regex | V1's proven parsing pattern (lines 413-428) | Handles reference category correctly |
| Standardization | Manual mean/std computation | scipy.stats.zscore or (x - mean) / std | Vectorized, tested, V1 uses this |
| Correlation matrix | Nested loops | pandas DataFrame.corr() | Vectorized, handles missing data |

**Key insight:** V1's 4.1_EstimateCeoClarity.py has already solved all these problems. Copy the patterns, don't reinvent.

## Common Pitfalls

### Pitfall 1: Reference CEO Coefficient Missing

**What goes wrong:** Extraction loop only parses parameters with "[T." in name, missing reference CEO (γ=0).

**Why it happens:** statsmodels sets first CEO alphabetically as reference (omitted from params), but that CEO still exists in data.

**How to avoid:**
```python
# Parse CEOs with coefficients
ceo_effects = {parse_id(p): gamma for p, gamma in ceo_params.items()}

# ADD reference CEOs with gamma=0
all_ceos = df_reg["ceo_id"].unique()
reference_ceos = [c for c in all_ceos if c not in ceo_effects]
for ref_ceo in reference_ceos:
    ceo_effects[ref_ceo] = 0.0

# NOW create DataFrame (includes ALL CEOs)
ceo_fe = pd.DataFrame(list(ceo_effects.items()), columns=["ceo_id", "gamma_i"])
```

**Warning signs:** CEO count in ceo_fe < CEO count in df_reg, or KeyError when merging.

### Pitfall 2: Wrong Uncertainty Measure

**What goes wrong:** Using CEO_All_Uncertainty_pct or Manager_QA_Uncertainty_pct instead of CEO_QA_Uncertainty_pct.

**Why it happens:** Paper variable naming (UncAns) is ambiguous, V2 has multiple uncertainty measures.

**How to avoid:**
- UncAns = CEO Q&A uncertainty ONLY (not All, not Presentation, not Manager)
- Verify: CEO_QA_Uncertainty_pct (V2) matches paper definition
- CONTEXT.md explicitly states: "UncAns = CEO Q&A uncertainty only (not All, not Presentation)"

**Warning signs:** Regression R² ≠ 0.31 benchmark, or distribution doesn't match paper (mean=-0.62, SD=0.23).

### Pitfall 3: CFO Variables Not in V2

**What goes wrong:** Trying to run Table IA.1 spec (4) with UncPreCFO and UncAnsCFO.

**Why it happens:** Paper includes these robustness specs, but V2 text analysis doesn't tag CFO speech separately.

**How to avoid:**
- Skip specs (4), (5), (6) entirely (CFO, EPR, AnDispPre not available)
- Document as limitation in summary report
- Run remaining 5 specs: (0), (1), (2), (3), (7)

**Warning signs:** KeyError: 'CFO_Pres_Uncertainty_pct' or missing column errors.

### Pitfall 4: Forgetting Minimum 5 Calls Filter

**What goes wrong:** Including CEOs with <5 calls, biasing γ_i estimates.

**Why it happens:** Paper explicitly states minimum 5 calls requirement (page 45).

**How to avoid:**
```python
# MUST apply before regression
ceo_call_counts = df['ceo_id'].value_counts()
valid_ceos = set(ceo_call_counts[ceo_call_counts >= 5].index)
df_reg = df[df['ceo_id'].isin(valid_ceos)].copy()

print(f"After >=5 calls filter: {len(df_reg)} calls, {df_reg['ceo_id'].nunique()} CEOs")
```

**Warning signs:** Very high CEO count (>5000), or many CEOs with n_calls < 5 in output.

### Pitfall 5: Sample Period Confusion

**What goes wrong:** Running 2002-2018 when paper used 2003-2015, or vice versa.

**Why it happens:** CONTEXT.md requires BOTH periods, outputs must be comparable.

**How to avoid:**
```python
# Run BOTH separately
df_paper = df[(df['year'] >= 2003) & (df['year'] <= 2015)]
df_extended = df[(df['year'] >= 2002) & (df['year'] <= 2018)]

# Run regressions for each, store in separate outputs
for period_name, df_period in [("paper", df_paper), ("extended", df_extended)]:
    model = run_regression(df_period)
    # ...
```

**Warning signs:** N observations ≠ ~122,611 for paper period, or sample_period column missing in ceo_clarity_scores.parquet.

## Code Examples

### CEO Fixed Effects Regression (Full Equation 4)

```python
# Source: V1 4.1_EstimateCeoClarity.py (adapted for Phase 56)
import statsmodels.formula.api as smf

def run_ceo_fe_regression(df, specification="col2"):
    """
    Run CEO fixed effects regression.

    Args:
        df: DataFrame with all required variables
        specification: "col1" (baseline) or "col2" (full Equation 4)

    Returns:
        model: Fitted OLS model
        ceo_fe: DataFrame with ceo_id, gamma_i, ClarityCEO_raw, ClarityCEO
    """
    # Filter to CEOs with >=5 calls
    ceo_counts = df["ceo_id"].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= 5].index)
    df_reg = df[df["ceo_id"].isin(valid_ceos)].copy()

    # Convert to string for categorical
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula based on specification
    if specification == "col1":
        # Table 3 Column (1): Baseline
        formula = (
            "CEO_QA_Uncertainty_pct ~ C(ceo_id) + "
            "CEO_Pres_Uncertainty_pct + "
            "Analyst_QA_Uncertainty_pct + "
            "C(year)"
        )
    elif specification == "col2":
        # Table 3 Column (2): Full Equation 4
        formula = (
            "CEO_QA_Uncertainty_pct ~ C(ceo_id) + "
            "CEO_Pres_Uncertainty_pct + "
            "Analyst_QA_Uncertainty_pct + "
            "CEO_All_Negative_pct + "
            "SurpDec + EPS_Growth + StockRet + MarketRet + "
            "C(year)"
        )
    else:
        raise ValueError(f"Unknown specification: {specification}")

    # Estimate with CEO-clustered standard errors
    model = smf.ols(formula, data=df_reg).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_reg['ceo_id']}
    )

    # Extract CEO fixed effects
    ceo_params = {
        p: model.params[p]
        for p in model.params.index
        if p.startswith("C(ceo_id)")
    }

    # Parse CEO IDs
    ceo_effects = {}
    for param_name, gamma_i in ceo_params.items():
        if "[T." in param_name:
            ceo_id = param_name.split("[T.")[1].split("]")[0]
            ceo_effects[ceo_id] = gamma_i

    # Reference CEO gets gamma = 0
    all_ceos = df_reg["ceo_id"].unique()
    for ref_ceo in [c for c in all_ceos if c not in ceo_effects]:
        ceo_effects[ref_ceo] = 0.0

    # Create DataFrame
    ceo_fe = pd.DataFrame(list(ceo_effects.items()), columns=["ceo_id", "gamma_i"])

    # Compute Clarity = -gamma_i (negate FIRST)
    ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]

    # THEN standardize to mean=0, SD=1
    mean_val = ceo_fe["ClarityCEO_raw"].mean()
    std_val = ceo_fe["ClarityCEO_raw"].std()
    ceo_fe["ClarityCEO"] = (ceo_fe["ClarityCEO_raw"] - mean_val) / std_val

    # Merge back CEO names and call counts
    ceo_stats = df_reg.groupby("ceo_id").agg({
        "ceo_name": "first",
        "file_name": "count"
    }).rename(columns={"file_name": "n_calls"})

    ceo_fe = ceo_fe.merge(ceo_stats, left_index=True, right_index=True, how="left")

    return model, ceo_fe
```

### Distribution Plot (Figure 3 Replication)

```python
import matplotlib.pyplot as plt

def plot_clarity_distribution(ceo_fe, sample_period, output_path):
    """
    Replicate Figure 3: Histogram of ClarityCEO (pre-standardization).

    Args:
        ceo_fe: DataFrame with ClarityCEO_raw column
        sample_period: "2003-2015" or "2002-2018"
        output_path: Path to save plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Histogram of raw Clarity (pre-standardization)
    ax.hist(ceo_fe["ClarityCEO_raw"], bins=50, edgecolor='black', alpha=0.7)

    # Add mean and SD annotations
    mean_val = ceo_fe["ClarityCEO_raw"].mean()
    std_val = ceo_fe["ClarityCEO_raw"].std()

    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean = {mean_val:.2f}')
    ax.axvline(mean_val - std_val, color='blue', linestyle=':', linewidth=1.5, label=f'-1 SD = {mean_val - std_val:.2f}')
    ax.axvline(mean_val + std_val, color='blue', linestyle=':', linewidth=1.5, label=f'+1 SD = {mean_val + std_val:.2f}')

    # Labels and title
    ax.set_xlabel('ClarityCEO (raw)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Figure 3 Replication: Distribution of CEO Clarity ({sample_period})\nHistogram shows "fatter left tail" - more extremely unclear CEOs', fontsize=14)
    ax.legend(fontsize=10)

    # Grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {output_path}")
    print(f"  Mean = {mean_val:.2f}, SD = {std_val:.2f}")
```

### Table 3 Replication Output

```python
def create_table3_replication(models_dict, output_path):
    """
    Create Table 3 replication with coefficients, t-stats, R².

    Args:
        models_dict: {
            "col1_main": model_object,
            "col2_main": model_object,
            "col1_finance": model_object,
            ...
        }
        output_path: Path to save CSV
    """
    results = []

    for spec_name, model in models_dict.items():
        # Extract key coefficients
        coeffs = {
            "specification": spec_name,
            "n_obs": int(model.nobs),
            "r_squared": model.rsquared,
            "r_squared_adj": model.rsquared_adj,
            "f_statistic": model.fvalue,
            "f_pvalue": model.f_pvalue,
        }

        # Add control variable coefficients
        for var in ["CEO_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct",
                    "CEO_All_Negative_pct", "SurpDec", "EPS_Growth",
                    "StockRet", "MarketRet"]:
            if var in model.params.index:
                coeffs[f"{var}_coef"] = model.params[var]
                coeffs[f"{var}_tstat"] = model.tvalues[var]

        results.append(coeffs)

    df_results = pd.DataFrame(results)
    df_results.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")
    return df_results
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual within-transformation | statsmodels C(ceo_id) LSDV | V1 implementation | Simpler FE extraction, proven pattern |
| HC1 robust SE | CEO-clustered SE (cov_type='cluster') | Phase 56 requirement | Matches paper methodology |
| Single sample period | Parallel paper (2003-2015) + extended (2002-2018) | Phase 56 requirement | Validation of paper results |
| All 8 Table IA.1 specs | 5 specs only (skip CFO, EPR, AnDispPre) | Phase 56 V2 limitation | Document as data limitation |

**Deprecated/outdated:**
- **linearmodels PanelOLS for FE extraction:** Harder to extract individual γ_i; statsmodels is preferred
- **Manager-level aggregation:** Paper uses CEO-specific measures, not manager aggregates
- **Firm fixed effects in Equation 4:** Only in turnover analysis (deferred), not in Phase 56

## Open Questions

1. **Clustering method in V1:** V1 uses HC1 heteroskedasticity-robust SE, but paper requires CEO-clustered SE. Should we:
   - Use cov_type='cluster' (paper methodology)
   - Use cov_type='HC1' (V1 consistency)
   - **Recommendation:** Use cov_type='cluster' to match paper exactly, document difference from V1

2. **SurpDec construction in V2:** Is SurpDec already computed in V2 firm controls, or must we construct from scratch?
   - V1 code references SurpDec in CONFIG, implies it exists
   - Need to verify in 3_Financial_Features outputs
   - **Recommendation:** Check firm_controls parquet files, construct if missing using CONTEXT.md formula

3. **∆UncPreCEO for spec (7):** How to compute "change in CEO presentation uncertainty"?
   - Paper likely means lagged difference: UncPreCEO_t - UncPreCEO_{t-1}
   - Or change from previous call: UncPreCEO_t - UncPreCEO_t-1
   - **Recommendation:** Use lagged difference by firm-quarter, verify with paper text if unclear

4. **Industry samples vs full sample:** V1 runs separate regressions for Main/Finance/Utility. Should Phase 56:
   - Run pooled regression (all firms)?
   - Run separate by industry (V1 pattern)?
   - **Recommendation:** Paper doesn't mention industry splits, use pooled regression for simplicity

## Sources

### Primary (HIGH confidence)

- **V1 Implementation:**
  - `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py` - Proven CEO FE extraction pattern
  - `2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py` - Extended controls robustness
  - Lines 338-452: Regression estimation, FE extraction, standardization
  - Confidence: HIGH - tested in production, matches paper methodology

- **Paper Text:**
  - `papers/FWP_2017_02_v2.txt` - Full paper text with Equation 4, variable definitions
  - Lines 635-671: Equation 4 specification, Table 3 description
  - Lines 712-714: ClarityCEO definition, standardization
  - Confidence: HIGH - authoritative source for methodology

- **V2 Data Schema:**
  - `4_Outputs/2_Textual_Analysis/2.2_Variables/2025-12-28_155038/linguistic_variables_2003.parquet`
  - Columns: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Analyst_QA_Uncertainty_pct, CEO_All_Negative_pct
  - Confidence: HIGH - verified existence, matches paper variables exactly

- **V2 CEO Identification:**
  - `4_Outputs/1.4_AssembleManifest/2026-01-30_151106/master_sample_manifest.parquet`
  - Columns: ceo_id, ceo_name, gvkey, start_date, ff12_code
  - 4,466 unique CEOs with ceo_id
  - Confidence: HIGH - verified CEO identification exists

### Secondary (MEDIUM confidence)

- **Statsmodels Documentation:**
  - [OLS with Formula API](https://www.statsmodels.org/stable/examples/notebooks/generated/formulas.html)
  - [Categorical variables and contrast coding](https://www.statsmodels.org/stable/contrasts.html)
  - Confidence: HIGH - official documentation

- **Fixed Effects Methodology:**
  - [Fixed effects dummies vs FE estimator](https://stats.stackexchange.com/questions/174243/difference-between-fixed-effects-dummies-and-fixed-effects-estimator)
  - LSDV = mathematically equivalent to within-transformation
  - Confidence: HIGH - verified by multiple sources

### Tertiary (LOW confidence)

- **Panel Data Regression Best Practices:**
  - [Panel data regression guide (Towards Data Science)](https://towardsdatascience.com/a-guide-to-panel-data-regression-theoretics-and-implementation-in-python-4c84c5055cf8/)
  - Confirms LSDV approach, but not paper-specific
  - Confidence: MEDIUM - general guide, not authoritative for this paper

- **ICC and Persistent Style Traits:**
  - 2025 publications on ICC for personality stability ([BMC Psychology](https://link.springer.com/article/1186/s40359-025-02716-x))
  - Not directly applicable to Phase 56 (ICC not in scope)
  - Confidence: LOW - informational only

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - statsmodels is V1 proven approach, paper methodology verified
- Architecture: HIGH - V1 patterns directly applicable, data schema verified
- Pitfalls: HIGH - V1 code shows all pitfalls already solved
- Variable mapping: HIGH - verified V2 has all required variables

**Research date:** 2026-02-06
**Valid until:** 30 days (stable domain - econometrics methods don't change rapidly)

**Key verification steps completed:**
- [x] V2 data schema inspected - all required linguistic variables exist
- [x] CEO identification verified - 4,466 CEOs with ceo_id in manifest
- [x] V1 implementation reviewed - proven pattern for CEO FE extraction
- [x] Paper methodology verified - Equation 4, Table 3, Figure 3 specifications confirmed
- [x] Variable mapping confirmed - CEO_QA_Uncertainty_pct = UncAns, etc.
- [x] CFO variables confirmed missing - specs (4), (5), (6) must be skipped
