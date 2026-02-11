# Script Header Documentation Standard

## Purpose

This document defines the standard header format for all Python scripts in the 2_Scripts directory. Standardized headers ensure:

- **Consistency**: All scripts follow the same documentation structure
- **Maintainability**: Easy to understand script purpose, inputs, outputs, and dependencies
- **Traceability**: Author and date fields provide change history context
- **Quality**: Deterministic flags and dependency tracking support reproducible research

## Header Template: Pipeline Scripts (Steps 1-4)

For all pipeline scripts in 1_Sample, 2_Text, 3_Financial, 4_Econometric directories:

```python
#!/usr/bin/env python3
"""
==============================================================================
STEP X.Y: {Script Name}
==============================================================================
ID: X.Y_ScriptName
Description: {One-line description of what the script does}

Purpose: {Detailed purpose (what the script does and why it matters)}

Inputs:
    - 4_Outputs/{PreviousStep}/latest/{file.parquet}
    - 1_Inputs/{data_file}
    - (List all input files with paths)

Outputs:
    - 4_Outputs/{CurrentStep}/{timestamp}/{output.parquet}
    - stats.json
    - {timestamp}.log
    - (List all output files with paths)

Dependencies:
    - Requires: Step X.{Y-1}
    - Uses: shared.module1, shared.module2
    - (List all required modules and dependencies)

Deterministic: true

Author: Thesis Author
Date: YYYY-MM-DD
==============================================================================
"""
```

## Header Template: Shared Utility Modules

For all utility modules in 2_Scripts/shared directory:

```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: {Module Name}
================================================================================
ID: shared/{module_name}
Description: {One-line description of what the module provides}

Purpose: {Detailed purpose (what problem it solves and how it's used)}

Inputs:
    - {Input data types or "None (utility module)"}

Outputs:
    - {Output data types or "None (utility module)"}

Main Functions:
    - function1(): {Brief description}
    - function2(): {Brief description}
    - (List key exported functions/classes)

Dependencies:
    - Uses: pandas, numpy, {external libraries}
    - (List required external packages)

Author: Thesis Author
Date: YYYY-MM-DD
================================================================================
"""
```

## Header Template: Observability Subpackage

For modules in 2_Scripts/shared/observability directory:

```python
#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE - {MODULE NAME}
================================================================================
ID: shared.observability.{module_name}
Description: {One-line description of the module's purpose}

Purpose: {Detailed purpose and what functionality it provides}

Inputs:
    - {Input data types or "None (utility module)"}

Outputs:
    - {Output data types or "None (utility module)"}

Main Functions:
    - function1(): {Brief description}
    - function2(): {Brief description}
    - (List key exported functions/classes)

Dependencies:
    - Uses: pandas, numpy, {external libraries}

Author: Thesis Author
Date: YYYY-MM-DD
================================================================================
"""
```

## Field Definitions

### Shebang

```python
#!/usr/bin/env python3
```

- **Required**: Must be the first line of all executable Python scripts
- **Purpose**: Specifies the Python interpreter for execution
- **Note**: Package __init__.py files may omit shebang

### ID Field

```
ID: X.Y_ScriptName
```

- **Required**: Yes
- **Format**: `StepNumber_ScriptName` for pipeline scripts, `shared/module_name` for shared modules
- **Purpose**: Unique identifier for the script

### Description Field

```
Description: {One-line description}
```

- **Required**: Yes
- **Format**: Single concise sentence describing what the script does
- **Purpose**: Quick reference for script functionality
- **Example**: "Constructs firm-level control variables for regression analysis"

### Purpose Field

```
Purpose: {Detailed purpose}
```

- **Required**: Yes
- **Format**: 1-3 sentences explaining what the script does and why
- **Purpose**: Provides context for understanding the script's role in the pipeline
- **Example**: "Calculate size, book-to-market, leverage, ROA, and other control variables from Compustat quarterly data."

### Inputs Field

```
Inputs:
    - 4_Outputs/{path}/{file.parquet}
    - 1_Inputs/{data_file}
```

- **Required**: Yes for pipeline scripts, optional for utility modules
- **Format**: Bulleted list of input file paths
- **Purpose**: Documents all data inputs required for the script
- **Note**: Use "None (utility module)" for pure utility scripts

### Outputs Field

```
Outputs:
    - 4_Outputs/{path}/{file.parquet}
    - stats.json
    - {timestamp}.log
```

- **Required**: Yes for pipeline scripts, optional for utility modules
- **Format**: Bulleted list of output file paths
- **Purpose**: Documents all artifacts produced by the script
- **Note**: Standard pipeline scripts always output stats.json and {timestamp}.log

### Dependencies Field

```
Dependencies:
    - Requires: Step X.{Y-1}
    - Uses: shared.module1, shared.module2
```

- **Required**: Yes
- **Format**: Bulleted list with "Requires:" for pipeline steps and "Uses:" for imported modules
- **Purpose**: Documents pipeline dependencies and required Python modules
- **Example**: "Requires: Step 2.2" means the script needs Step 2.2 to complete first

### Deterministic Field

```
Deterministic: true
```

- **Required**: Yes for all pipeline scripts
- **Format**: Boolean value (true/false)
- **Purpose**: Indicates whether script produces identical outputs given identical inputs
- **Value**: Should be `true` for all reproducible pipeline scripts
- **Note**: Utility modules may omit this field

### Author Field

```
Author: Thesis Author
```

- **Required**: Yes
- **Format**: "Thesis Author" or actual author name
- **Purpose**: Provides attribution for code authorship
- **Note**: Use "Thesis Author" as placeholder during development

### Date Field

```
Date: YYYY-MM-DD
```

- **Required**: Yes
- **Format**: ISO 8601 date format (YYYY-MM-DD)
- **Purpose**: Records when the script was created or last modified
- **Note**: Update this date when making significant changes

## Examples from Actual Scripts

### Example 1: Pipeline Script (Step 1.1)

```python
#!/usr/bin/env python3
"""
==============================================================================
STEP 1.1: Clean Metadata & Event Filtering
==============================================================================
ID: 1.1_CleanMetadata
Description: Loads Unified-info, deduplicates exact rows, resolves file_name
             collisions, and filters for earnings calls (event_type='1') in
             the target date range (2002-2018).

Inputs:
    - 1_Inputs/Unified-info.parquet
    - config/project.yaml

Outputs:
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/variable_reference.csv
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/report_step_1_1.md
    - 3_Logs/1.1_CleanMetadata/{timestamp}.log

Deterministic: true
Dependencies:
    - Requires: Step 1.0
    - Uses: 1.5_Utils, pandas, yaml

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""
```

### Example 2: Shared Utility Module

```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Panel OLS with Fixed Effects
================================================================================
ID: shared/panel_ols
Description: Panel OLS regression with firm + year + industry fixed effects using
             linearmodels.PanelOLS. Supports clustered standard errors, HAC
             adjustment, and comprehensive diagnostics.

Purpose: Phases 33-35 (H1/H2/H3 Regressions) need standardized panel regression
         infrastructure with proper fixed effects, interaction terms, and
         multicollinearity diagnostics.

Inputs:
    - pandas DataFrame with panel data (gvkey, year, ff48_code, dependent, exog)

Outputs:
    - Fitted PanelOLS model with coefficients and standard errors
    - Summary statistics (R2, N, F-stat, fixed effects used)
    - VIF diagnostics with threshold warnings

Main Functions:
    - run_panel_ols(): Execute panel regression with fixed effects
    - compute_vif(): Calculate variance inflation factors
    - check_collinearity(): Detect perfect multicollinearity

Dependencies:
    - Utility module for panel OLS regression
    - Uses: linearmodels, pandas, numpy, statsmodels

Deterministic: true

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

### Example 3: Econometric Script (Step 4.1)

```python
#!/usr/bin/env python3
"""
==============================================================================
STEP 4.1: H1 Cash Holdings Regression
==============================================================================
ID: 4.1_H1CashHoldingsRegression
Description: Panel OLS regressions for H1 (Speech Uncertainty & Cash Holdings).
             Tests whether vague managers hoard more cash (precautionary motive)
             and whether leverage moderates this effect (debt discipline).

Model Specification:
    CashHoldings_{t+1} = beta0 + beta1*Uncertainty_t + beta2*Leverage_t
                         + beta3*(Uncertainty_t * Leverage_t)
                         + gamma*Controls + Firm FE + Year FE + epsilon

Hypothesis Tests:
    H1a: beta1 > 0 (Higher uncertainty leads to more cash holdings)
    H1b: beta3 < 0 (Leverage attenuates the uncertainty-cash relationship)

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H1_CashHoldings.parquet
      (cash_holdings, leverage, controls at firm-year level)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
      (speech uncertainty measures at call level)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.1_H1CashHoldingsRegression/{timestamp}/H1_Regression_Results.parquet
      (all regression coefficients, SEs, p-values, diagnostics)
    - 4_Outputs/4_Econometric_V2/4.1_H1CashHoldingsRegression/{timestamp}/stats.json
      (regression summaries, hypothesis tests, execution metadata)
    - 4_Outputs/4_Econometric_V2/4.1_H1CashHoldingsRegression/{timestamp}/H1_RESULTS.md
      (human-readable summary of key findings)
    - 3_Logs/4_Econometric_V2/4.1_H1CashHoldingsRegression/{timestamp}_H1.log
      (execution log with dual-writer output)

Deterministic: true
Dependencies:
    - Requires: Step 3.1_H1Variables
    - Uses: shared.regression_utils, shared.panel_ols, shared.diagnostics, linearmodels

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""
```

## Compliance Checklist

When creating or modifying a Python script, ensure:

- [ ] Shebang line `#!/usr/bin/env python3` is present
- [ ] Module docstring exists with triple quotes
- [ ] ID field is present and correctly formatted
- [ ] Description field is present
- [ ] Purpose field is present
- [ ] Inputs field lists all input files (or notes "None" for utilities)
- [ ] Outputs field lists all output files (or notes "None" for utilities)
- [ ] Dependencies field lists required steps and modules
- [ ] Deterministic field is set to `true` for pipeline scripts
- [ ] Author field is present
- [ ] Date field is present in YYYY-MM-DD format
- [ ] Header formatting matches the template (dashes, alignment)

## Verification

To verify compliance with this standard:

```bash
# Count shebang lines (should be 79)
find 2_Scripts -name "*.py" -type f -exec head -1 {} \; | grep -c "^#!/usr/bin/env python3"

# Count Author fields (should be 79)
grep -r "Author:" 2_Scripts --include="*.py" -l | wc -l

# Count Date fields (should be 79)
grep -r "Date:" 2_Scripts --include="*.py" -l | wc -l

# Count Dependencies sections (should be 79)
grep -r "Dependencies:" 2_Scripts --include="*.py" -l | wc -l
```

## Related Documents

- `docs/DOCSTRING_COMPLIANCE.md`: Compliance report and statistics
- `.planning/requirements.md`: DOC-02 requirements for header standardization
- Phase 61-02 Plan: Documentation header standardization execution

## Version History

- **2026-02-11**: Initial standard documented. All 79 scripts brought to compliance.
