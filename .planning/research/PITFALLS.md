# Domain Pitfalls: Academic Replication Packages

**Domain:** Empirical Finance Research Pipeline Documentation
**Researched:** 2026-01-22
**Confidence:** HIGH (based on AEA Data Editor guidance, DCAS v1.0, TIER Protocol 4.0)

## Overview

This document catalogs pitfalls specific to academic replication packages in empirical finance research. These are the actual reasons packages get rejected, require revisions, or fail verification by journal data editors. Sources include AEA Data and Code Availability Policy, Social Science Data Editors' guidance, and TIER Protocol standards.

---

## Critical Pitfalls

Mistakes that cause outright rejection or major revision requests from data editors.

### Pitfall 1: Missing or Inadequate Data Availability Statement

**What goes wrong:** Authors provide data files or code but fail to document how an independent researcher can obtain the original data. For CRSP/Compustat/earnings call data, this is especially common because authors assume "everyone knows" how to get WRDS data.

**Why it happens:** 
- Authors conflate "I have the data" with "the data is documented"
- Assumption that commercial database access is self-explanatory
- Focus on code rather than data provenance

**Consequences:**
- Immediate revision request from AEA Data Editor
- Verification cannot proceed until resolved
- Delays acceptance by weeks or months

**Prevention:**
1. For each data source, document in README:
   - Full name of data provider (e.g., "Center for Research in Security Prices (CRSP)")
   - Access mechanism (e.g., "via WRDS subscription")
   - Monetary and time cost to obtain access
   - Specific tables/datasets used with identifiers
   - Date range of data extract
   - Any filters applied during download
2. Include even for data you cannot redistribute

**Detection (warning signs):**
- README mentions data files without explaining their origin
- Code references input files with no corresponding provenance documentation
- "Data available upon request" without explaining the request process

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rules #1, #2, #3

---

### Pitfall 2: Undocumented Sample Selection Criteria

**What goes wrong:** The paper reports "our sample consists of 15,847 firm-quarters" but the replication package doesn't document exactly how that number was derived. Reviewers cannot trace from raw data to final sample.

**Why it happens:**
- Sample construction evolved over drafts; final criteria not consolidated
- Filters scattered across multiple scripts without summary
- "Obvious" exclusions (e.g., financials, utilities) not explicitly stated
- Missing firms due to merge failures not quantified

**Consequences:**
- Reviewers question whether results are cherry-picked
- Cannot verify sample is as described in paper
- Thesis committee may require sample reconstruction demonstration
- Journal editors flag as reproducibility concern

**Prevention:**
1. Create explicit sample construction documentation showing:
   - Starting universe (e.g., "all CRSP common stocks, share codes 10/11")
   - Each filter applied with observation counts before/after
   - Merge success rates between datasets
   - Final sample count matching paper exactly
2. Every script should output observation counts at each stage
3. README should include "Sample Construction" section with cascade table

**Detection (warning signs):**
- Scripts apply filters without logging how many observations dropped
- No single place documents all exclusion criteria
- Sample size in paper doesn't match what code produces
- Merge operations don't report match rates

**Phase to address:** Statistics instrumentation phase (add to every script)
**DCAS Reference:** Rule #7 (data transformation code)

---

### Pitfall 3: Non-Reproducible Outputs (Bitwise Non-Identical Results)

**What goes wrong:** Running the same code twice produces different results, or results differ from what's in the paper. Common in finance research due to floating-point operations, random seeds, and parallel processing.

**Why it happens:**
- Random number generators not seeded
- Parallel processing introduces non-determinism
- Floating-point operations accumulate differently across runs
- Sort order not guaranteed for ties
- Package versions changed between paper draft and submission

**Consequences:**
- Data editor cannot verify results match paper
- Raises suspicion about result validity
- May require complete re-analysis with documented environment

**Prevention:**
1. Set explicit random seeds at script start (project uses seed 42)
2. Pin thread count to 1 for deterministic parallel operations
3. Use stable sort algorithms; break ties explicitly
4. Document exact package versions in requirements.txt
5. Log computational environment at runtime (Python version, package versions)
6. Re-run entire pipeline before submission and verify outputs match paper

**Detection (warning signs):**
- Scripts use `np.random` or `random` without setting seed
- Parallel operations without fixed worker counts
- No requirements.txt or environment specification
- Results in 4_Outputs don't match paper tables exactly

**Phase to address:** Statistics phase (add environment logging) + pre-submission verification
**DCAS Reference:** Rule #8 (analysis code must reproduce results)

---

### Pitfall 4: Missing Code for Data Transformations

**What goes wrong:** Replication package includes analysis code and final datasets but omits the code that transformed raw data into analysis-ready format. AEA policy explicitly requires transformation code even when raw data cannot be shared.

**Why it happens:**
- Authors think "I can't share the data, so why include the code?"
- Data cleaning was done interactively and never scripted
- Transformations happened in Excel or GUI tools
- Legacy code from early project stages was lost

**Consequences:**
- Explicit policy violation (DCAS Rule #7)
- Cannot verify data manipulations are as described
- Revision request to provide all transformation code

**Prevention:**
1. Include ALL code from raw data to final analysis, even if data is confidential
2. Never do transformations manually or in GUI tools
3. Maintain complete script chain: raw -> cleaned -> merged -> analysis
4. This project's 4-stage structure (Sample -> Text -> Financial -> Econometric) naturally supports this

**Detection (warning signs):**
- Scripts read from "cleaned" or "processed" files with no corresponding cleaning code
- Gaps in the step numbering (e.g., scripts 2.1, 2.3, 2.5 exist but not 2.2, 2.4)
- README describes transformations that have no corresponding code

**Phase to address:** Code audit before documentation
**DCAS Reference:** Rule #7 (data transformation code required even without data)

---

### Pitfall 5: Hardcoded Paths Breaking Portability

**What goes wrong:** Code contains absolute paths like `C:\Users\researcher\thesis\data\` that only work on the author's machine. Replicator must manually edit dozens of files to run the code.

**Why it happens:**
- Development convenience (paths worked for author)
- Not tested on clean machine
- Path handling differs across operating systems

**Consequences:**
- Replicator frustration and errors
- AEA Data Editor notes as "not one-click reproducible"
- Revision request to fix all paths

**Prevention:**
1. Use configuration file for all paths (project.yaml)
2. All paths relative to project root
3. Use pathlib for cross-platform compatibility
4. Test on fresh clone before submission
5. README documents single config change needed

**Detection (warning signs):**
- Grep for `C:\`, `/Users/`, `/home/` in code
- Paths defined inside scripts rather than config
- Different scripts use different base directories

**Phase to address:** Code standardization (verify all scripts read from project.yaml)
**DCAS Reference:** TIER Protocol portability standard

---

### Pitfall 6: Missing Computational Requirements

**What goes wrong:** README doesn't specify software versions, required packages, hardware requirements, or expected runtime. Replicator installs wrong versions and gets different results or errors.

**Why it happens:**
- Assumed "everyone uses the same setup"
- Requirements evolved during project without tracking
- Runtime never measured (author's machine is fast)

**Consequences:**
- Replicator cannot recreate environment
- Version mismatches cause silent failures or different results
- AEA Data Editor cannot plan verification resources

**Prevention:**
1. Generate requirements.txt with pinned versions: `pip freeze > requirements.txt`
2. Document in README:
   - Python version (e.g., 3.11.x)
   - Operating system tested on
   - RAM requirements (especially for large merges)
   - Disk space needed
   - Expected runtime per script and total
3. Include setup instructions

**Detection (warning signs):**
- No requirements.txt in repository
- README mentions "Python" without version
- No runtime estimates anywhere
- Scripts import packages not in requirements

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rule #13 (README must list all dependencies and requirements)

---

## Moderate Pitfalls

Mistakes that cause revision requests but don't block verification.

### Pitfall 7: Incomplete Variable Documentation

**What goes wrong:** Dataset contains variables like `ret_adj`, `clarity_score`, `sue_rank` without documentation of their construction, allowed values, or meaning.

**Why it happens:**
- Variable names seem "self-explanatory" to author
- Documentation created early and not updated
- Variables added during revisions without updating codebook

**Consequences:**
- Replicator cannot verify variable construction is correct
- Reviewers question whether variables match paper description
- Data editor requests metadata improvement

**Prevention:**
1. Create codebook/data dictionary for each output dataset
2. Include for each variable:
   - Name, type, allowed values
   - Construction formula or source
   - Missing value treatment
   - Reference to paper section using it
3. Statistics output should include variable summaries automatically

**Detection (warning signs):**
- Output datasets have no accompanying documentation
- Variable names are cryptic abbreviations
- Statistics show unexpected missing values or ranges

**Phase to address:** Statistics instrumentation + data appendix creation
**DCAS Reference:** Rule #5 (metadata for variables)

---

### Pitfall 8: Missing Data Citations

**What goes wrong:** Paper uses CRSP, Compustat, I/B/E/S, earnings call transcripts but doesn't cite them as data sources in the references section.

**Why it happens:**
- Data citations are newer requirement (post-2019 emphasis)
- Authors cite academic papers but not data sources
- Confusion about how to cite commercial databases

**Consequences:**
- AEA Data Editor revision request
- Delays during copyediting
- Violates DCAS Rule #6

**Prevention:**
1. Cite every data source in paper's reference section
2. Use proper data citation format (see AEA Sample References)
3. Include data citations in README as well
4. Example: `Center for Research in Security Prices (CRSP). 2020. "CRSP US Stock Database." Wharton Research Data Services. https://wrds-www.wharton.upenn.edu/`

**Detection (warning signs):**
- Paper mentions data sources only in text, not references
- README lists data sources without formal citations
- In-text mentions like "we use CRSP data" without citation

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rule #6 (all data must be cited)

---

### Pitfall 9: No Master Script / Unclear Execution Order

**What goes wrong:** Replication package contains 15 scripts but no documentation of which order to run them, or which can be skipped if data is unavailable.

**Why it happens:**
- Author knows the order from memory
- Scripts have dependencies that aren't documented
- Some scripts are obsolete but still in package

**Consequences:**
- Replicator runs scripts in wrong order, gets errors
- Hours wasted figuring out dependencies
- AEA Data Editor notes as "not minimal intervention"

**Prevention:**
1. README includes explicit numbered execution order
2. Create master script that runs all steps (or document why not possible)
3. Document which outputs each script produces
4. Map scripts to paper tables/figures
5. This project's naming convention (1.0, 1.1, 2.1, etc.) helps but needs README explanation

**Detection (warning signs):**
- README says "run the scripts" without specifying order
- Scripts in package that don't appear in any documentation
- No mapping from scripts to paper exhibits

**Phase to address:** Documentation/README phase
**DCAS Reference:** Rule #13 (README must explain how to reproduce)

---

### Pitfall 10: Statistics Don't Match Paper Tables

**What goes wrong:** Replication package produces Table 1 with N=15,234 but paper says N=15,847. Or means/standard deviations differ in second decimal place.

**Why it happens:**
- Paper revised after tables generated but code not re-run
- Copy-paste errors when transferring to paper
- Sample changed but old numbers in paper
- Rounding differences

**Consequences:**
- Data editor flags discrepancy
- Must investigate whether code or paper is correct
- Delays while regenerating and matching

**Prevention:**
1. Re-run entire pipeline before final submission
2. Generate tables programmatically (LaTeX output from code)
3. Include output verification step that compares to expected values
4. Statistics phase should produce machine-readable outputs for comparison

**Detection (warning signs):**
- Tables in paper were manually formatted
- Last pipeline run was months before submission
- No automated comparison between outputs and paper

**Phase to address:** Statistics phase + pre-submission verification
**DCAS Reference:** Rule #8 (code must reproduce paper results)

---

## Minor Pitfalls

Mistakes that cause delays or annoyance but are quickly fixable.

### Pitfall 11: Platform-Specific Code Issues

**What goes wrong:** Code works on Windows but fails on Linux/Mac due to path separators, line endings, or platform-specific commands.

**Why it happens:**
- Only tested on author's platform
- Used backslashes for paths
- Shell commands only work on one OS

**Prevention:**
1. Use `pathlib.Path` for all path operations
2. Avoid shell commands in Python; use libraries instead
3. Document tested platform in README
4. Test on second platform if possible

**Phase to address:** Code review before documentation

---

### Pitfall 12: Confusing File Structure

**What goes wrong:** Replicator cannot find files mentioned in README, or folder structure is too deep/complex to navigate.

**Why it happens:**
- Structure evolved organically
- Archive/backup folders left in package
- Naming conventions inconsistent

**Prevention:**
1. Clean package before submission (remove __pycache__, .DS_Store, backups)
2. Use consistent naming convention (this project's Stage.Step_Name pattern)
3. Keep structure flat enough to be understandable
4. README describes structure explicitly

**Phase to address:** Package cleanup before submission

---

### Pitfall 13: Missing Runtime Estimates

**What goes wrong:** Replicator allocates 2 hours but job runs for 3 days. Or expects long run but it finishes in 5 minutes (makes them worry something failed).

**Why it happens:**
- Author never timed the runs
- Runtime varies dramatically by machine
- Individual scripts timed but not total

**Prevention:**
1. Time each script during final run
2. Document in README: individual script times and total
3. Note hardware used for timing
4. Flag long-running steps (>1 hour) prominently

**Phase to address:** Statistics phase (add timing output) + README

---

## Finance-Specific Pitfalls

Issues particular to empirical finance research with CRSP/Compustat data.

### Pitfall 14: WRDS Data Redistribution Violation

**What goes wrong:** Author includes CRSP or Compustat extracts in replication package, violating WRDS terms of service.

**Why it happens:**
- Author wants to be "complete"
- Doesn't realize redistribution is prohibited
- Confused about what can/cannot be shared

**Consequences:**
- Data editor requires removal
- Potential licensing issues
- Delays for package revision

**Prevention:**
1. NEVER include raw CRSP/Compustat/IBES data in deposit
2. Provide code that works with WRDS access
3. Document exact WRDS query to recreate data
4. May provide synthetic example data for code testing

**Phase to address:** Package preparation (audit for restricted data)

---

### Pitfall 15: Undocumented Link Table Methodology

**What goes wrong:** Paper merges CRSP with Compustat, earnings calls with ExecuComp, etc., but doesn't document the linking methodology or success rates.

**Why it happens:**
- Link tables are "standard" (CRSP-Compustat Merged)
- But link quality varies; authors don't report match rates
- Ambiguous matches resolved silently

**Consequences:**
- Reviewers cannot assess sample attrition due to linking
- Different link methods yield different samples
- Core reproducibility concern for finance papers

**Prevention:**
1. Document link table source and version
2. Report match rates at each merge
3. Document how ties/ambiguities are resolved
4. Statistics phase should output merge diagnostics automatically

**Phase to address:** Statistics instrumentation (add merge diagnostics)

---

### Pitfall 16: Text Data Processing Not Reproducible

**What goes wrong:** Paper analyzes earnings call transcripts but text preprocessing (tokenization, cleaning) is not fully documented or reproducible.

**Why it happens:**
- NLP preprocessing has many implicit choices
- Dictionaries updated without versioning
- Regular expressions not documented
- Encoding issues across platforms

**Consequences:**
- Different preprocessing yields different measures
- Cannot verify text variable construction
- Raises questions about robustness

**Prevention:**
1. Version and include all dictionaries used
2. Document every text preprocessing step
3. Log tokenization choices (lowercase, stemming, stopwords)
4. Include character encoding handling explicitly
5. This project's C++ tokenizer should have documented behavior

**Phase to address:** Text processing documentation + statistics

---

## Phase-Specific Warnings

| Phase/Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Sample Construction (1_Sample) | Undocumented selection criteria | Add cascade table to every script output |
| Text Processing (2_Text) | Non-reproducible tokenization | Version dictionaries, document all choices |
| Financial Features (3_Financial) | Missing link methodology | Document merge success rates |
| Econometric (4_Econometric) | Results don't match paper | Re-run before submission, automate table generation |
| README Creation | Incomplete Data Availability Statement | Use Social Science Data Editors' template |
| Statistics Addition | Missing variable documentation | Add codebook generation to each script |
| Package Preparation | Includes restricted data | Audit for CRSP/Compustat before deposit |

---

## Pre-Submission Checklist

Based on AEA Data Editor requirements and common rejection reasons:

### Data Documentation
- [ ] Data Availability Statement for every data source
- [ ] Access instructions including cost and time
- [ ] All data sources cited in references
- [ ] Sample selection fully documented with counts
- [ ] No restricted data (CRSP/Compustat) in deposit

### Code Documentation  
- [ ] All transformation code included (even without data)
- [ ] No hardcoded paths (all from config)
- [ ] Execution order documented
- [ ] Script-to-table/figure mapping provided
- [ ] Package versions in requirements.txt

### Reproducibility
- [ ] Random seeds set
- [ ] Deterministic outputs verified
- [ ] Re-run produces same results as paper
- [ ] Runtime estimates documented
- [ ] Platform requirements stated

### README Completeness (per DCAS #13)
- [ ] Data Availability Statement
- [ ] Computational requirements
- [ ] Software and hardware specifications
- [ ] Step-by-step instructions
- [ ] Expected outputs described
- [ ] All data cited

---

## Sources

| Source | Type | Confidence |
|--------|------|------------|
| [AEA Data and Code Availability Policy](https://www.aeaweb.org/journals/data/data-code-policy) | Official | HIGH |
| [Data and Code Availability Standard v1.0](https://datacodestandard.org/) | Official | HIGH |
| [TIER Protocol 4.0](https://www.projecttier.org/tier-protocol/protocol-4-0/) | Official | HIGH |
| [AEA Data Editor Preparation Guide](https://aeadataeditor.github.io/aea-de-guidance/preparing-for-data-deposit.html) | Official | HIGH |
| [Social Science Data Editors' Template README](https://social-science-data-editors.github.io/template_README/) | Official | HIGH |
| [AEA Data Editor FAQ](https://aeadataeditor.github.io/aea-de-guidance/FAQ.html) | Official | HIGH |

---

*This pitfalls catalog should be consulted when instrumenting statistics, creating README documentation, and preparing the final replication package.*

---

# Part 2: Hypothesis Testing Implementation Pitfalls

**Domain:** Adding econometric hypothesis testing (panel FE, interactions, manager FE, 2SLS) to existing F1D pipeline  
**Researched:** 2026-02-04  
**Confidence:** MEDIUM (based on existing codebase analysis + linearmodels documentation + econometric theory)

This section catalogs pitfalls specific to adding hypothesis testing capabilities with interaction terms, manager fixed effects, and 2SLS instrumentation to the existing F1D pipeline.

---

## Critical Pitfalls (Hypothesis Testing)

Mistakes that cause incorrect inference, paper rejection, or complete rewrites.

---

### Pitfall H1: Fixed Effects Collinearity — Absorbed Variable Trap

**What goes wrong:**  
When using firm + year + industry fixed effects simultaneously, time-invariant variables (like industry dummies) get absorbed. Including industry FE with firm FE is redundant since firms don't change industries in most panels. This creates silent collinearity — linearmodels may drop variables automatically or produce unstable estimates without clear warnings.

**Why it happens:**  
The existing `regression_utils.py` uses statsmodels formula API with `C(ceo_id) + C(year)` syntax. Adding `C(industry) + C(firm) + C(year)` with interaction terms can cause near-collinearity when industry and firm overlap substantially.

**Warning signs:**
- `drop_absorbed=True` in linearmodels silently removes variables
- `check_rank=False` skips detection of collinearity 
- Condition numbers > 30 in diagnostics
- Standard errors that are orders of magnitude larger than expected
- Coefficients change dramatically when adding/removing controls

**Prevention:**
```python
# 1. Use linearmodels PanelOLS with explicit checks
from linearmodels.panel import PanelOLS

model = PanelOLS(
    dependent=df['y'],
    exog=df[['x1', 'x2']],
    entity_effects=True,   # Firm FE
    time_effects=True,     # Year FE
    other_effects=df['industry'],  # Industry FE via other_effects
    singletons=False,      # Keep singletons for diagnostics
    drop_absorbed=False,   # FAIL on absorbed variables, don't hide them
    check_rank=True        # Mandatory rank check
)

# 2. Run VIF diagnostics BEFORE adding new FE dimensions
from shared.regression_validation import check_multicollinearity
vif_results = check_multicollinearity(df_reg, independent_vars, vif_threshold=10.0)

# 3. Test each FE dimension incrementally
# First: firm + year only
# Then: add industry and compare coefficients
# If main coefficients stable, adding is safe
```

**Detection code for existing pipeline:**
```python
# Add to regression_validation.py
def check_fe_compatibility(df, entity_col, time_col, other_effects_cols):
    """Check if FE dimensions are separable."""
    # Count unique entities per other_effect combination
    if other_effects_cols:
        for col in other_effects_cols:
            coverage = df.groupby(col)[entity_col].nunique()
            if coverage.min() < 3:
                warnings.warn(
                    f"FE {col} has thin coverage: {coverage.min()} entities. "
                    "May cause collinearity with entity FE."
                )
```

**Phase to address:** Validation Phase — before any hypothesis regression runs

---

### Pitfall H2: Interaction Term Multicollinearity Without Centering

**What goes wrong:**  
Creating `Uncertainty × Leverage` interaction without centering causes:
1. High correlation between `Uncertainty`, `Leverage`, and `Uncertainty × Leverage` (multicollinearity)
2. Unstable main effect coefficients
3. Misleading interpretation of the interaction coefficient

**Why it happens:**  
The current `regression_helpers.py` has `build_regression_sample()` but no automatic centering. Raw interaction terms create collinearity because `X × Z` is correlated with both `X` and `Z` when they have non-zero means.

**Warning signs:**
- VIF > 10 for interaction term
- Main effects (`Uncertainty`, `Leverage`) flip sign when interaction added
- Large standard errors on main effects
- Model fits well but individual coefficients are insignificant

**Prevention:**
```python
# ALWAYS center continuous variables before creating interactions
def prepare_interaction_terms(df, var1, var2, center=True):
    """Create interaction term with optional centering."""
    df = df.copy()
    
    if center:
        df[f'{var1}_c'] = df[var1] - df[var1].mean()
        df[f'{var2}_c'] = df[var2] - df[var2].mean()
        df[f'{var1}_x_{var2}'] = df[f'{var1}_c'] * df[f'{var2}_c']
    else:
        df[f'{var1}_x_{var2}'] = df[var1] * df[var2]
    
    return df

# For panel data: consider within-group centering
def within_group_center(df, var, group_col):
    """Center variable within groups (e.g., within-firm)."""
    df = df.copy()
    df[f'{var}_wc'] = df.groupby(group_col)[var].transform(
        lambda x: x - x.mean()
    )
    return df
```

**Interpretation note:**
- Centered: interaction coefficient = "effect of X on Y when Z is at its mean"
- Uncentered: interaction coefficient = "effect of X on Y when Z = 0" (often meaningless)

**Phase to address:** Variable Construction Phase — before regression specification

---

### Pitfall H3: 2SLS Weak Instruments — Silent Bias

**What goes wrong:**  
Using weak instruments produces 2SLS estimates that are more biased than OLS, but with inflated standard errors that make results look significant. The pipeline could produce "significant" endogeneity-corrected results that are actually garbage.

**Why it happens:**  
The linearmodels IV2SLS requires explicit instrument specification but doesn't automatically reject weak instruments. First-stage F-statistic < 10 indicates weakness, but the library only reports it — doesn't fail.

**Warning signs:**
- First-stage partial F-statistic < 10 (classic rule of thumb)
- First-stage partial R-squared very low (< 0.01)
- 2SLS standard errors >> OLS standard errors (10x+ inflation)
- 2SLS coefficient dramatically different from OLS (possible bias direction reversed)
- Confidence intervals include both positive and negative values (uninformative)

**Prevention:**
```python
from linearmodels.iv import IV2SLS

# Fit IV model
iv_model = IV2SLS(
    dependent=df['y'],
    exog=df[['controls']],
    endog=df['endogenous_var'],
    instruments=df['instruments']
)
iv_results = iv_model.fit(cov_type='robust')

# MANDATORY: Check first-stage diagnostics
first_stage = iv_results.first_stage
print(f"Partial F-stat: {first_stage.diagnostics['partial_f'].stat:.2f}")
print(f"Partial R-squared: {first_stage.diagnostics['partial_rsquared']:.4f}")

# Enforcement rule
if first_stage.diagnostics['partial_f'].stat < 10:
    raise ValueError(
        f"Weak instrument detected. F-stat = {first_stage.diagnostics['partial_f'].stat:.2f}. "
        "Use LIML estimator or find stronger instruments."
    )

# For weak instruments, use LIML instead of 2SLS
from linearmodels.iv import IVLIML
liml_results = IVLIML(dependent, exog, endog, instruments).fit(cov_type='robust')
```

**Testing procedure:**
1. Report first-stage F-statistic prominently
2. If F < 10: use LIML or Anderson-Rubin confidence intervals
3. Compare 2SLS and OLS — if dramatically different, investigate why
4. Run Durbin-Wu-Hausman test to confirm endogeneity exists

**Phase to address:** 2SLS Implementation Phase — with built-in weak instrument checks

---

### Pitfall H4: 2SLS Exclusion Restriction Violations — Invalid Instruments

**What goes wrong:**  
Instruments that correlate with the error term (violate exclusion restriction) produce biased and inconsistent 2SLS estimates. Unlike weak instruments, this cannot be tested directly — it's a conceptual/theoretical issue.

**Why it happens:**  
In corporate finance, common "instruments" often fail exclusion:
- Lagged values of endogenous variable (still correlated with unobserved firm characteristics)
- Industry averages (correlated with industry-level shocks affecting outcome)
- Geographic variables (correlated with regional economic conditions)

**Warning signs:**
- J-statistic rejects overidentifying restrictions (but only if overidentified)
- Sensitivity to adding/removing instruments changes main result dramatically
- Economic story for exclusion is weak ("we assume this doesn't affect Y directly")
- Referee comments questioning instrument validity

**Prevention:**
```python
# For overidentified models: run J-test
if len(instruments) > len(endogenous):
    print(f"J-statistic: {iv_results.j_stat.stat:.4f}")
    print(f"J-stat p-value: {iv_results.j_stat.pval:.4f}")
    if iv_results.j_stat.pval < 0.05:
        warnings.warn(
            "J-test rejects instrument validity. "
            "Some instruments may violate exclusion restriction."
        )

# Document exclusion restriction argument explicitly
INSTRUMENT_JUSTIFICATION = """
Instrument: CEO birth-order among siblings
Exclusion argument: Birth order affects CEO communication style (first-borns more 
assertive) but has no direct effect on cash holdings except through communication.
Potential violation: Birth order could correlate with risk preferences (first-borns 
more conservative), which directly affects cash holdings. ADDRESSED by controlling 
for CEO risk-taking measures.
"""
```

**Best practices:**
1. Use MULTIPLE instruments to enable J-test
2. Document theoretical exclusion argument in paper and code comments
3. Run robustness with subsets of instruments
4. Consider "plausibly exogenous" approaches (bounds estimation)

**Phase to address:** Instrument Selection Phase — before 2SLS coding begins

---

### Pitfall H5: Manager Fixed Effects — Connected Sample Problems

**What goes wrong:**  
Manager (CEO) fixed effects require "connected" sample — CEOs who move between firms to separately identify CEO effect vs. firm effect. Without movers, CEO FE and firm FE are perfectly collinear. The AKM (Abowd-Kramarz-Margolis) decomposition fails.

**Why it happens:**  
In your sample, you're extracting `gamma_i` (CEO fixed effects) from `4.1_EstimateCeoClarity.py`. If most CEOs are in a single firm throughout the sample, you're identifying a mix of CEO style + firm culture, not pure CEO effect.

**Warning signs:**
- Very few CEO-firm pairs where CEO appears in multiple firms
- High correlation between estimated CEO FE and average firm-level outcomes
- CEO FE estimates are similar for all CEOs at the same firm
- Standard errors on CEO FE are huge

**Prevention — check sample connectivity:**
```python
def check_manager_connectivity(df, manager_col='ceo_id', firm_col='gvkey'):
    """Check if manager FE are identified separately from firm FE."""
    
    # Count firms per manager
    managers_multi_firm = df.groupby(manager_col)[firm_col].nunique()
    movers = (managers_multi_firm > 1).sum()
    total_managers = len(managers_multi_firm)
    
    print(f"Total managers: {total_managers:,}")
    print(f"Movers (multiple firms): {movers:,} ({100*movers/total_managers:.1f}%)")
    
    # Check if connected
    if movers < 0.05 * total_managers:
        warnings.warn(
            f"Only {movers} managers appear at multiple firms. "
            "Manager FE may not be separately identified from firm FE. "
            "Consider: (1) longer sample period, (2) interpreting as manager-firm style, "
            "(3) Bonhomme-Lamadon-Manresa clustering approach."
        )
    
    # Build connected components
    import networkx as nx
    G = nx.Graph()
    for _, row in df[[manager_col, firm_col]].drop_duplicates().iterrows():
        G.add_edge(f"M_{row[manager_col]}", f"F_{row[firm_col]}")
    
    components = list(nx.connected_components(G))
    print(f"Connected components: {len(components)}")
    
    largest = max(components, key=len)
    print(f"Largest component size: {len(largest)} nodes")
    
    return movers, len(components)

# Run before CEO FE estimation
check_manager_connectivity(df)
```

**Alternative approaches if connectivity is low:**
1. **Within-manager variation only:** Use manager-by-firm FE, focus on time-series variation
2. **Correlated random effects:** Allow CEO effects to be correlated with firm effects
3. **Leave-one-out estimation:** Estimate manager effect excluding current firm's data

**Phase to address:** Sample Construction Phase — verify connectivity before running manager FE

---

## Moderate Pitfalls (Hypothesis Testing)

Mistakes that cause delays, reviewer concerns, or technical debt.

---

### Pitfall H6: Standard Error Clustering Inconsistency

**What goes wrong:**  
Using different clustering levels across specifications makes results incomparable. Or clustering at wrong level biases inference (too few clusters = inflated t-stats, too many clusters = conservative but inefficient).

**Why it happens:**
- Existing `regression_utils.py` defaults to `cov_type='HC1'` (robust, not clustered)
- Panel data with firm-year structure should cluster at firm level minimum
- If CEO moves between firms, might need two-way clustering (firm + CEO)

**Warning signs:**
- T-stats > 3 for small effects (possible under-clustering)
- Coefficients significant in some specs but not others with same data
- Fewer than 50 clusters in any dimension

**Prevention:**
```python
# Standard pattern for panel finance regressions
def run_panel_regression(df, formula, entity_col='gvkey', time_col='year'):
    """Run panel regression with appropriate clustering."""
    
    model = PanelOLS.from_formula(
        formula,
        data=df.set_index([entity_col, time_col])
    )
    
    # Cluster at entity level (firm) by default
    results = model.fit(
        cov_type='clustered',
        cluster_entity=True,
        cluster_time=False  # Set True for two-way clustering
    )
    
    # Report number of clusters
    n_clusters = df[entity_col].nunique()
    print(f"Clusters: {n_clusters} {entity_col}s")
    
    if n_clusters < 50:
        warnings.warn(
            f"Only {n_clusters} clusters. Consider wild bootstrap for inference."
        )
    
    return results

# For 2SLS: match clustering
iv_results = iv_model.fit(cov_type='clustered', clusters=df[entity_col])
```

**Phase to address:** All Regression Phases — consistent clustering throughout

---

### Pitfall H7: Subsample Analysis — Multiple Testing Inflation

**What goes wrong:**  
Running 10+ subsample analyses (high leverage, low leverage, crisis, non-crisis, high growth, low growth, etc.) without multiple testing correction guarantees false positives. If main effect is null, you'll find "significant" subsample effects by chance.

**Why it happens:**  
Thesis requirement mentions: "Subsample analyses (leverage, crisis, growth)". Each subsample test has 5% false positive rate. With 10 tests, ~40% chance of at least one false positive.

**Warning signs:**
- Main effect insignificant but 3+ subsamples are significant
- Subsample effects have opposite signs (suspicious)
- Subsample p-values cluster around 0.03-0.05 (p-hacking)

**Prevention:**
```python
def report_subsample_analysis(results_dict, alpha=0.05):
    """Report subsample analyses with multiple testing correction."""
    
    n_tests = len(results_dict)
    bonferroni_alpha = alpha / n_tests
    
    print(f"Subsample analyses: {n_tests}")
    print(f"Bonferroni-corrected alpha: {bonferroni_alpha:.4f}")
    print()
    
    for name, result in results_dict.items():
        pval = result.pvalues['main_effect']
        coef = result.params['main_effect']
        
        sig_uncorrected = '*' if pval < 0.05 else ''
        sig_corrected = '**' if pval < bonferroni_alpha else ''
        
        print(f"{name}: coef={coef:.4f}, p={pval:.4f} {sig_uncorrected}{sig_corrected}")
    
    # Summary
    n_sig_uncorrected = sum(
        1 for r in results_dict.values() 
        if r.pvalues['main_effect'] < 0.05
    )
    n_sig_corrected = sum(
        1 for r in results_dict.values() 
        if r.pvalues['main_effect'] < bonferroni_alpha
    )
    
    print(f"\nSignificant (uncorrected): {n_sig_uncorrected}/{n_tests}")
    print(f"Significant (Bonferroni): {n_sig_corrected}/{n_tests}")
```

**Better approach — interaction terms instead of subsamples:**
```python
# Instead of: run regression on high_leverage and low_leverage separately
# Do: run full sample with Uncertainty × HighLeverage interaction

df['high_leverage'] = (df['leverage'] > df['leverage'].median()).astype(int)
formula = 'y ~ uncertainty + high_leverage + uncertainty:high_leverage + controls'

# Interaction coefficient tests difference across groups in ONE regression
# No multiple testing problem
```

**Phase to address:** Analysis Planning Phase — design subsample strategy before running

---

### Pitfall H8: Survivorship Bias in Panel Construction

**What goes wrong:**  
Panel requires same firms/CEOs across time. Firms that go bankrupt, are acquired, or delist are dropped. CEOs who leave are excluded. This biases toward successful firms/CEOs, underestimating true effects if uncertainty leads to exit.

**Why it happens:**  
Current sample construction in `1_Sample/` links entities across databases. If matching is stricter, you lose distressed firms. The "5 calls per CEO" filter in `4.1_EstimateCeoClarity.py` excludes short-tenure CEOs (who may have been fired for poor communication).

**Warning signs:**
- Steady increase in average firm size/performance over sample period
- Few firm-exit events (bankruptcy, acquisition) in sample
- Short-tenure CEOs underrepresented

**Prevention:**
```python
# Track sample attrition
def diagnose_panel_attrition(df, entity_col, time_col):
    """Check for non-random panel attrition."""
    
    # Count entries and exits per year
    first_year = df.groupby(entity_col)[time_col].min()
    last_year = df.groupby(entity_col)[time_col].max()
    
    entries_per_year = first_year.value_counts().sort_index()
    exits_per_year = last_year.value_counts().sort_index()
    
    print("Entries by year:")
    print(entries_per_year)
    print("\nExits by year:")
    print(exits_per_year)
    
    # Compare characteristics of exits vs. continuing
    last_obs = df.groupby(entity_col).last()
    max_year = df[time_col].max()
    
    exits = last_obs[last_obs[time_col] < max_year]
    continues = last_obs[last_obs[time_col] == max_year]
    
    # Compare key characteristics
    for var in ['uncertainty', 'leverage', 'size']:
        if var in df.columns:
            exit_mean = exits[var].mean()
            continue_mean = continues[var].mean()
            print(f"{var}: exits={exit_mean:.4f}, continues={continue_mean:.4f}")

# Include sample attrition analysis in output
diagnose_panel_attrition(df, 'gvkey', 'year')
```

**Phase to address:** Sample Construction Phase — document attrition

---

### Pitfall H9: Time Period Selection Bias

**What goes wrong:**  
Choosing sample period to maximize significance (e.g., excluding 2008-2009 crisis if it weakens results) or picking endpoints that favor hypothesis is p-hacking.

**Why it happens:**  
Current config shows `year_start: 2002, year_end: 2018`. Why not 2001 or 2019? The choice should be based on data availability, not result strength.

**Warning signs:**
- Sample period differs from typical literature (why?)
- Results sensitive to adding/removing boundary years
- Exclusion of crisis years without clear justification

**Prevention:**
```python
# Document sample period choice upfront
SAMPLE_PERIOD_JUSTIFICATION = """
Period: 2002-2018
Start: 2002 — First full year of call transcripts in our sample 
       (SEC filing requirements + data vendor coverage)
End: 2018 — Last year of Execucomp data at time of analysis
       (not 2019 due to data vendor lag)
Crisis years: INCLUDED (2008-2009). Excluding would bias toward normal periods.
"""

# Test sensitivity to period choice
def test_period_sensitivity(run_regression_func, periods):
    """Test if results robust to sample period."""
    
    results = {}
    for start, end in periods:
        result = run_regression_func(year_start=start, year_end=end)
        results[(start, end)] = result.params['main_effect']
    
    # Report range of coefficients
    coefs = list(results.values())
    print(f"Coefficient range: [{min(coefs):.4f}, {max(coefs):.4f}]")
    
    # Flag if sign changes
    if min(coefs) < 0 < max(coefs):
        warnings.warn("Main effect CHANGES SIGN across sample periods!")
```

**Phase to address:** Sample Definition Phase — lock period before analysis

---

## Minor Pitfalls (Hypothesis Testing)

Mistakes that cause annoyance, reviewer questions, or minor rework.

---

### Pitfall H10: Inconsistent Variable Scaling

**What goes wrong:**  
Mixing percentage (0-100) with proportion (0-1) variables, or not winsorizing outliers consistently, makes coefficient comparison difficult.

**Prevention:**
```python
# Standardize variable construction
def standardize_variables(df, pct_vars, proportion_vars, winsorize_vars):
    """Ensure consistent scaling."""
    
    df = df.copy()
    
    # Convert percentages to proportions
    for var in pct_vars:
        if df[var].max() > 1:
            print(f"Converting {var} from % to proportion")
            df[var] = df[var] / 100
    
    # Winsorize at 1%/99%
    for var in winsorize_vars:
        lower = df[var].quantile(0.01)
        upper = df[var].quantile(0.99)
        df[var] = df[var].clip(lower, upper)
        print(f"Winsorized {var}: [{lower:.4f}, {upper:.4f}]")
    
    return df
```

---

### Pitfall H11: Formula String Errors in statsmodels

**What goes wrong:**  
Typos in R-style formulas (e.g., `C(year` without closing paren) cause cryptic errors. Special characters in column names break formulas.

**Prevention:**
```python
# Validate formula before regression
def validate_formula(formula, df):
    """Check formula variables exist in DataFrame."""
    import re
    
    # Extract variable names (simple parser)
    tokens = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', formula)
    
    # Exclude statsmodels keywords
    keywords = {'C', 'I', 'np', 'log', 'exp', 'sqrt'}
    vars_in_formula = set(tokens) - keywords
    
    missing = vars_in_formula - set(df.columns)
    if missing:
        raise ValueError(f"Variables in formula but not in DataFrame: {missing}")
    
    print(f"Formula validated: {len(vars_in_formula)} variables found")
```

---

### Pitfall H12: Output File Versioning Conflicts

**What goes wrong:**  
Running hypothesis regressions with different parameters overwrites previous outputs. No way to trace which parameters produced which results.

**Prevention (already partially implemented in codebase):**
```python
# Extend existing timestamp pattern with config hash
import hashlib
import json

def get_run_id(config_dict, timestamp):
    """Generate unique run ID including config hash."""
    config_str = json.dumps(config_dict, sort_keys=True)
    config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
    return f"{timestamp}_{config_hash}"

# Save config alongside outputs
def save_regression_outputs(results, out_dir, config):
    """Save outputs with config for reproducibility."""
    
    # Save config
    with open(out_dir / 'run_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Save results (existing pattern)
    ...
```

---

## Phase-Specific Warnings (Hypothesis Testing)

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Variable construction | Interaction multicollinearity | Center variables before interactions (Pitfall H2) |
| Sample construction | Manager FE connectivity | Check mover fraction before FE estimation (Pitfall H5) |
| Sample construction | Survivorship bias | Document attrition and compare exit characteristics (Pitfall H8) |
| Fixed effects setup | Absorbed variable trap | Use `drop_absorbed=False`, check rank (Pitfall H1) |
| 2SLS implementation | Weak instruments | Report and enforce F > 10 rule (Pitfall H3) |
| 2SLS implementation | Invalid instruments | Document exclusion restriction, run J-test (Pitfall H4) |
| Standard errors | Wrong clustering level | Cluster at firm level minimum, check cluster count (Pitfall H6) |
| Subsample analysis | Multiple testing | Use interaction terms instead, or Bonferroni correction (Pitfall H7) |
| All phases | Inconsistent reporting | Standardize variable scaling, validate formulas (Pitfalls H10-H11) |

---

## Integration with Existing Pipeline

The existing F1D codebase has partial safeguards but needs extensions:

| Existing Safeguard | Location | Gap |
|--------------------|----------|-----|
| VIF multicollinearity check | `regression_validation.py:219` | Not called by default in regression scripts |
| Sample size validation | `regression_validation.py:199` | Threshold may be too low for FE-heavy models |
| CEO FE extraction | `regression_utils.py:71` | No connectivity check for manager FE |
| Clustered SE support | `regression_utils.py:61` | Not defaulted, scripts use HC1 |
| Formula validation | None | Need to add |
| Instrument diagnostics | None | Need to add for 2SLS |

**Recommended additions to `shared/` modules:**
1. `interaction_utils.py` — centering, interaction creation, VIF for interactions
2. `panel_diagnostics.py` — FE collinearity check, connectivity check, attrition analysis
3. `iv_diagnostics.py` — weak instrument tests, J-test wrapper, first-stage reporting
4. `subsample_utils.py` — multiple testing correction, subsample comparison

---

## Sources (Hypothesis Testing Section)

**Authoritative (HIGH confidence):**
- linearmodels documentation: `bashtage.github.io/linearmodels/` — PanelOLS, IV2SLS, first-stage diagnostics
- Existing codebase: `regression_utils.py`, `regression_validation.py`, `regression_helpers.py`

**Econometric theory (MEDIUM confidence — from training, verify with textbooks):**
- Stock-Yogo weak instrument thresholds (F > 10 rule)
- AKM/connected sample for worker-firm FE decomposition
- Bonferroni correction for multiple testing

**Needs verification before implementation:**
- Specific linearmodels syntax for `other_effects` with multiple dimensions
- Wild bootstrap for small cluster inference (may require additional library)
- Bounds estimation for plausibly exogenous instruments

---

*Last updated: 2026-02-04*
