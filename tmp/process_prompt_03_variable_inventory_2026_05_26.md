# Variable Extraction — Prompt 03: Complete variable inventory + reported summary stats
**Stage**: Variables Round 1 — solution-free enumeration of every variable in the paper, with definitions + reported summary statistics
**Design principle**: Solution-free (discovery, not leading). Verbatim only. Captures raw inputs AND derived/downstream variables. Captures reported summary stats so we can moment-fingerprint our rebuild against the paper.
**Run on**: NLM (Campello notebook), Claude-web (Sina attaches PDFs), Claude Code (PyMuPDF anchor on main + supplement)
**Created**: 2026-05-26
**Why**: Methodology lock-in is complete. Per Sina's three-category debugging plan (method / variables / code), this is Variables phase. The 2026-05-17 audit already used the moment-fingerprint technique (CASH rebuild 0.212/0.235/0.126 vs Campello reported 0.220/0.250/0.120) to discover the DV specification defect. Need ALL variables' paper-reported stats to extend that test to every variable.

---

## PROMPT (copy-paste below this line, identical to all 3 AIs)

The paper is:
> **Campello, Cortes, d'Almeida, Kankanhalli** — "Exporting Uncertainty: The Impact of Brexit on Corporate America" — *Journal of Financial and Quantitative Analysis*, Vol. 57, No. 8, Dec. 2022, pp. 3178–3222 — DOI 10.1017/S0022109022000308
>
> Includes the published Internet Appendix (supplementary materials).

### TASK
Enumerate **every variable** used in the paper's empirical analysis. For each variable, return:
1. **Definition** (verbatim, from the body text or table notes where it is first defined)
2. **Construction details** (raw data source if raw; formula if derived)
3. **Reported summary statistics** (verbatim from Table 1 or whichever table reports stats for that variable)
4. **Role** in the analysis (DV / Treatment / Control / Moderator / Instrument / Robustness / Other)

Include BOTH:
- **Raw variables** — items pulled directly from data sources (e.g., COMPUSTAT items `capx`, `atq`, `cheq`; FTSE100 index from Bloomberg; YTS establishment counts; I/B/E/S EPS forecasts; etc.)
- **Derived/downstream variables** — quantities constructed from raw inputs (e.g., `INVESTMENT_i,t = capx / lagged total assets`; `β_i^UK` from the equation-(13) regression; `HIGH_UK_EXPOSURE`; `Tobin's Q`; `AUTOMATION_i`; etc.)

Do NOT assume which variables matter. Do NOT skip "obvious" ones. Do NOT filter to "main analysis" only — include robustness variables, moderator-interaction variables, and any variable that appears in ANY regression, summary stats table, figure, or descriptive comparison.

### OUTPUT FORMAT (strict — one block per variable)

```
VAR_NN:
  name_as_printed: "<variable name EXACTLY as it appears in the paper, e.g. 'β_i^UK', 'HIGH_UK_EXPOSURE', 'AUTOMATION_i', 'capx', 'lagged total assets'>"
  role: <"DV" | "Treatment" | "Control" | "Moderator" | "Instrument" | "Robustness" | "Sample-filter" | "Other: <describe>">
  raw_or_derived: <"raw" | "derived">
  primary_definition:
    page: <printed page>
    section_or_table: <e.g. "§IV.A.1, ¶2", "Table 1 notes", "Table 2 notes", "IA Appendix E.1 ¶2">
    paragraph_position: <integer or "N/A for table-only">
    definition_verbatim: "<one or more sentences from the paper, EXACT. Preserve capitalization, punctuation, math notation. Include the entire defining clause; if a formula is given, include the formula in Unicode (e.g., 'Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + ...').>"
  data_source_or_formula: "<for raw vars: source DB + item code (e.g. 'COMPUSTAT Quarterly Fundamentals, item capx'); for derived vars: explicit formula (e.g. 'AUTOMATION_i = log(1 + AUTOMATION_KEYWORDS_i)') OR verbatim text describing construction>"
  unit_or_transformation: "<e.g. 'USD millions', 'logged', 'ratio (no unit)', 'percentage points', 'firm-year', 'firm-quarter', 'standardized (mean 0, SD 1)'>"
  reported_summary_stats:
    found_in: "<table name and page, e.g. 'Table 1, p. 3198' | 'Table 5, p. 3203' | 'NOT REPORTED in the paper'>"
    N: "<integer | 'N/A'>"
    mean: "<number as printed in paper | 'N/A'>"
    sd: "<number as printed | 'N/A'>"
    median: "<number as printed | 'N/A'>"
    p25: "<number as printed | 'N/A'>"
    p75: "<number as printed | 'N/A'>"
    other_stats: "<any additional moments reported (min, max, skewness, etc.), as printed>"
    panel: "<treatment/control split if reported separately | 'pooled' | 'N/A'>"
  uncertainty: <"none" | one verbatim sentence flagging ambiguity (e.g., 'definition split across two tables', 'multiple constructions for the same variable name', 'symbol clash with another variable')>
```

### RULES

1. **Verbatim only** for definitions. No paraphrase. If the paper uses a formula, transcribe the formula in Unicode mathematical notation, not as a description.
2. **Verbatim only** for summary stats. Transcribe the cell values EXACTLY as printed (preserve decimal places, sign, scientific notation).
3. **DO NOT compute** summary stats. Only report what the paper EXPLICITLY prints.
4. **DO NOT skip** variables because they "seem trivial" or because they're "obviously just lagged total assets". The point of this audit is exhaustive inventory.
5. **Repeated variable names**: if the same name is used for two different things in different parts of the paper (e.g., a generic `i` subscript vs. a variable name `i`), list each instance as a separate VAR_NN block.
6. **Same variable, multiple definition locations**: prefer the FIRST place defined; if the definition is split across multiple locations (e.g., text + table notes), list the most complete location in `primary_definition` and note the secondary location in `uncertainty`.
7. **Table-only variables**: if a variable appears in Table 2's regression columns but is never named in the text, return it anyway with `definition_verbatim` taken from the table column header + table notes.
8. **Moderator interactions**: each interaction term is a SEPARATE variable (e.g., `POST_t × HIGH_UK_EXPOSURE_i` is one block; `POST_t × HIGH_UK_EXPOSURE_i × HIGH_REDEPLOYABILITY_i` is another).
9. **Fixed effects**: list FIRM, INDUSTRY, QUARTER fixed effects as variables (role = "Fixed effect").
10. **Cluster-robust standard error groups**: list clustering groups as variables (role = "Standard error cluster group").

### WHAT TO AVOID

- Do not invent variables not in the paper.
- Do not consolidate distinct variables that share notation.
- Do not assume "standard" empirical-finance variables — only what THIS paper actually uses.
- Do not transcribe Table 1 keyword lists from IA Appendix E as variables (those are PARAMETERS of the AUTOMATION construction, not separate variables).
- Do not report computed/derived statistics ("mean of subgroup A minus subgroup B") unless the paper explicitly prints that comparison.

### HONESTY GUARD

- If you cannot locate a definition for a variable that appears in a regression, RETURN THE VARIABLE with `definition_verbatim: "NOT DEFINED IN TEXT — appears in [Table X col Y] without explicit definition"` and `primary_definition.section_or_table` set to where it appears.
- If summary statistics for a variable are not reported in any table, set `reported_summary_stats.found_in: "NOT REPORTED in the paper"` and all stat fields to `"N/A"`.
- If your source has corrupted text (mojibake on equations, lost subscripts), set `uncertainty` to that effect; do NOT guess.
- If you cannot access the supplementary material (Internet Appendix), state that in a single ACCESS_LIMITATIONS block at the END of your response.

### NO COMMENTARY

No introduction, no caveats outside the formal blocks, no closing remarks. Only VAR_NN blocks + END block + optional ACCESS_LIMITATIONS block.

### END BLOCK

```
TOTAL_VARIABLES_RETURNED: <integer>
EXTRACTION_DATE: <YYYY-MM-DD>
PAPER_ACCESS_METHOD: <"NLM-notebook-with-supplement" | "NLM-notebook-without-supplement" | "PDF-attached" | "programmatic-PyMuPDF" | "other">
SUPPLEMENT_AVAILABLE: <"yes" | "no">
TABLES_FOUND:
  - Table 1: <page number | "not found">
  - Table 2: <page number | "not found">
  - Table 3: <page number | "not found">
  - Table 4: <page number | "not found">
  - Table 5: <page number | "not found">
  - Table 6: <page number | "not found">
  - Table 7: <page number | "not found">
  - Table 8: <page number | "not found">
  - Table 9: <page number | "not found">
  - Table 10: <page number | "not found">
  - Table 11: <page number | "not found">
  - Table 12: <page number | "not found">
  - (add any tables beyond 12)
```

---

## Expected cross-check after Sina returns 3 responses
- 3 AIs return variable inventories → I compute set-intersection (variables in all 3), set-difference (variables in only 1-2)
- For each variable in all 3: compare `definition_verbatim` char-for-char + compare `reported_summary_stats` cell-by-cell
- Variables in only 1 or 2 AIs → FLAG for inspection (likely real variable missed by some AIs, NOT hallucination)
- My PyMuPDF anchor extraction of Tables 1, 2, ... will be the ground truth for cell values (per `feedback_no_llm_cell_transcription` — LLM cell transcription is unreliable; use programmatic extraction)



//////////////////
NLM
//////////////////


VAR_01:
name_as_printed: "INVESTMENT"
role: "DV"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "INVESTMENT is capital expenditures (Compustat item capxq) scaled by lagged total assets (item atq)."
data_source_or_formula: "Compustat Quarterly Fundamentals, item capxq / item atq (lagged)"
unit_or_transformation: "ratio (no unit)"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "48554"
mean: "0.012"
sd: "0.016"
median: "0.007"
p25: "0.003"
p75: "0.015"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_02:
name_as_printed: "EMPLOYMENT GROWTH"
role: "DV"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "EMPLOYMENT GROWTH is the log difference in the number of employees (item emp) between year t and t−1."
data_source_or_formula: "Compustat Fundamentals, log(emp_t) - log(emp_{t-1})"
unit_or_transformation: "logged difference"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "45781"
mean: "0.019"
sd: "0.170"
median: "0.013"
p25: "-0.038"
p75: "0.076"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_03:
name_as_printed: "CASH"
role: "DV"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "CASH is cash and short-term investments (item cheq) scaled by lagged total assets."
data_source_or_formula: "Compustat Quarterly Fundamentals, item cheq / item atq (lagged)"
unit_or_transformation: "ratio (no unit)"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "48554"
mean: "0.220"
sd: "0.250"
median: "0.120"
p25: "0.040"
p75: "0.310"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_04:
name_as_printed: "ACQUISITIONS"
role: "DV"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "ACQUISITIONS is acquisitions (item aqcy) scaled by lagged total assets."
data_source_or_formula: "Compustat Fundamentals, item aqcy / item atq (lagged)"
unit_or_transformation: "ratio (no unit)"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "48554"
mean: "0.004"
sd: "0.018"
median: "0.000"
p25: "0.000"
p75: "0.000"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_05:
name_as_printed: "TOBIN’S Q"
role: "Control"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "TOBIN’S Q is the sum of total assets and the market value of equity (item prccq times item cshoq) minus the book value of equity (item ceqq), scaled by total assets."
data_source_or_formula: "(atq + (prccq * cshoq) - ceqq) / atq"
unit_or_transformation: "ratio (no unit)"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "48554"
mean: "1.970"
sd: "1.490"
median: "1.420"
p25: "1.050"
p75: "2.230"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_06:
name_as_printed: "SIZE"
role: "Control"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "SIZE is the natural logarithm of total assets."
data_source_or_formula: "log(atq)"
unit_or_transformation: "logged"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "48554"
mean: "7.220"
sd: "1.860"
median: "7.170"
p25: "5.870"
p75: "8.480"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_07:
name_as_printed: "CASH FLOW"
role: "Control"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "CASH FLOW is the sum of net income (item niq) and depreciation and amortization (item dpq) scaled by lagged total assets."
data_source_or_formula: "(niq + dpq) / atq (lagged)"
unit_or_transformation: "ratio (no unit)"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "48554"
mean: "0.010"
sd: "0.040"
median: "0.015"
p25: "0.003"
p75: "0.028"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_08:
name_as_printed: "DIVIDEND PAYER"
role: "Control"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "DIVIDEND PAYER is an indicator variable equal to 1 if the firm pays a cash dividend (item dvpspq), and 0 otherwise."
data_source_or_formula: "1 if dvpspq > 0, else 0"
unit_or_transformation: "indicator (0 or 1)"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "48554"
mean: "0.450"
sd: "0.500"
median: "0.000"
p25: "0.000"
p75: "1.000"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_09:
name_as_printed: "U.K. SALES (%)"
role: "Treatment base"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "U.K. SALES (%) is the share of sales generated in the U.K. (U.K. Sales/Total Sales)."
data_source_or_formula: "FactSet Revere / Compustat Geographic Segments, UK Sales / Total Sales"
unit_or_transformation: "percentage"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "3230"
mean: "0.041"
sd: "0.076"
median: "0.000"
p25: "0.000"
p75: "0.056"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_10:
name_as_printed: "U.K. SUBSIDIARIES (%)"
role: "Treatment base"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "U.K. SUBSIDIARIES (%) is the share of subsidiaries located in the U.K. (U.K. Subsidiaries/Total Subsidiaries)."
data_source_or_formula: "Bureau van Dijk’s Orbis database, UK Subsidiaries / Total Subsidiaries"
unit_or_transformation: "percentage"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "3230"
mean: "0.038"
sd: "0.081"
median: "0.000"
p25: "0.000"
p75: "0.044"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_11:
name_as_printed: "β^UK"
role: "Treatment base"
raw_or_derived: "derived"
primary_definition:
page: 3186
section_or_table: "Table 1 notes"
paragraph_position: "N/A for table-only"
definition_verbatim: "βUK is the firm-level stock return sensitivity to the British Pound."
data_source_or_formula: "Coefficient from rolling regressions of firm stock returns on GBP/USD exchange rate changes"
unit_or_transformation: "coefficient"
reported_summary_stats:
found_in: "Table 1, p. 3186"
N: "3230"
mean: "0.009"
sd: "0.550"
median: "-0.021"
p25: "-0.260"
p75: "0.230"
other_stats: "N/A"
panel: "pooled"
uncertainty: "none"

VAR_12:
name_as_printed: "POST_t"
role: "Treatment (time)"
raw_or_derived: "derived"
primary_definition:
page: 3185
section_or_table: "§IV.A, ¶2"
paragraph_position: 2
definition_verbatim: "POST_t is a dummy variable equal to 1 for the 6 quarters after the referendum (i.e., 2016:Q3 to 2017:Q4), and 0 for the 6 quarters prior (2015:Q1 to 2016:Q2)."
data_source_or_formula: "1 if quarter is between 2016:Q3 and 2017:Q4, else 0"
unit_or_transformation: "indicator (0 or 1)"
reported_summary_stats:
found_in: "NOT REPORTED in the paper"
N: "N/A"
mean: "N/A"
sd: "N/A"
median: "N/A"
p25: "N/A"
p75: "N/A"
other_stats: "N/A"
panel: "N/A"
uncertainty: "none"

VAR_13:
name_as_printed: "HIGH_UK_EXPOSURE_i"
role: "Treatment"
raw_or_derived: "derived"
primary_definition:
page: 3185
section_or_table: "§IV.A, ¶2"
paragraph_position: 2
definition_verbatim: "HIGH_UK_EXPOSURE_i is a dummy variable equal to 1 if firm i’s U.K. exposure is above the sample median, and 0 otherwise."
data_source_or_formula: "1 if firm's UK exposure proxy > sample median, else 0"
unit_or_transformation: "indicator (0 or 1)"
reported_summary_stats:
found_in: "NOT REPORTED in the paper"
N: "N/A"
mean: "N/A"
sd: "N/A"
median: "N/A"
p25: "N/A"
p75: "N/A"
other_stats: "N/A"
panel: "N/A"
uncertainty: "none"

VAR_14:
name_as_printed: "POST_t × HIGH_UK_EXPOSURE_i"
role: "Treatment interaction"
raw_or_derived: "derived"
primary_definition:
page: 3185
section_or_table: "§IV.A, ¶1"
paragraph_position: 1
definition_verbatim: "y_{i,t} = α + δ(POST_t × HIGH_UK_EXPOSURE_i) + γX_{i,t-1} + η_i + λ_{j,t} + ε_{i,t}"
data_source_or_formula: "POST_t * HIGH_UK_EXPOSURE_i"
unit_or_transformation: "indicator (0 or 1)"
reported_summary_stats:
found_in: "NOT REPORTED in the paper"
N: "N/A"
mean: "N/A"
sd: "N/A"
median: "N/A"
p25: "N/A"
p75: "N/A"
other_stats: "N/A"
panel: "N/A"
uncertainty: "none"

VAR_15:
name_as_printed: "AUTOMATION_i"
role: "Robustness / Moderator"
raw_or_derived: "derived"
primary_definition:
page: 16
section_or_table: "IA Appendix E.1 ¶3"
paragraph_position: 3
definition_verbatim: "AUTOMATION_i = log(1 + AUTOMATION_KEYWORDS_i), where AUTOMATION_KEYWORDS_i is the number of mentions of the top 100 automation-related keywords in firm i’s 10-K forms."
data_source_or_formula: "log(1 + AUTOMATION_KEYWORDS_i)"
unit_or_transformation: "logged count"
reported_summary_stats:
found_in: "NOT REPORTED in the paper"
N: "N/A"
mean: "N/A"
sd: "N/A"
median: "N/A"
p25: "N/A"
p75: "N/A"
other_stats: "N/A"
panel: "N/A"
uncertainty: "none"

VAR_16:
name_as_printed: "Firm"
role: "Fixed effect"
raw_or_derived: "derived"
primary_definition:
page: 3185
section_or_table: "§IV.A, ¶2"
paragraph_position: 2
definition_verbatim: "η_i represents firm fixed effects"
data_source_or_formula: "Firm identifier"
unit_or_transformation: "categorical"
reported_summary_stats:
found_in: "NOT REPORTED in the paper"
N: "N/A"
mean: "N/A"
sd: "N/A"
median: "N/A"
p25: "N/A"
p75: "N/A"
other_stats: "N/A"
panel: "N/A"
uncertainty: "none"

VAR_17:
name_as_printed: "Industry × Quarter"
role: "Fixed effect"
raw_or_derived: "derived"
primary_definition:
page: 3185
section_or_table: "§IV.A, ¶2"
paragraph_position: 2
definition_verbatim: "λ_{j,t} represents industry-by-quarter fixed effects"
data_source_or_formula: "Industry identifier interacted with Quarter identifier"
unit_or_transformation: "categorical"
reported_summary_stats:
found_in: "NOT REPORTED in the paper"
N: "N/A"
mean: "N/A"
sd: "N/A"
median: "N/A"
p25: "N/A"
p75: "N/A"
other_stats: "N/A"
panel: "N/A"
uncertainty: "none"

TOTAL_VARIABLES_RETURNED: 17
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: "PDF-attached"
SUPPLEMENT_AVAILABLE: "yes"
TABLES_FOUND:

* Table 1: 3186
* Table 2: 3188
* Table 3: 3190
* Table 4: 3192
* Table 5: 3195
* Table 6: 3197
* Table 7: 3199
* Table 8: 3201
* Table 9: 3204
* Table 10: 3206
* Table 11: 3208
* Table 12: 3209




///////////////////////////////////
claude web
///////////////////////////////////



```
VAR_01:
  name_as_printed: "INVESTMENT"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "INVESTMENT is defined as capital expenditures divided by lagged total assets."
  data_source_or_formula: "INVESTMENT = capital expenditures / lagged total assets. COMPUSTAT Quarterly Fundamentals. Table 10/C.7 notes add '(quarterly)'."
  unit_or_transformation: "ratio (no unit), firm-quarter; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 76,094"
    mean: "Panel A: 0.01"
    sd: "Panel A: 0.02"
    median: "Panel A: 0.01"
    p25: "N/A (paper reports IQR, not separate quartiles)"
    p75: "N/A (paper reports IQR, not separate quartiles)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.01/0.02/0.01/0.01/76,094; B 0.02/0.02/0.01/0.02/11,083; C 0.01/0.01/0.01/0.01/12,067; D 0.01/0.02/0.01/0.01/35,828; E 0.01/0.02/0.01/0.01/9,389. Matched-sample means in Table C.2; pre-Brexit period means in C.4/C.5."
    panel: "5 panels (A universe; B/C market-based treated/control; D/E text-based treated/control)"
  uncertainty: "Source PDF text layer strips minus signs from table cells; transcribed values are unsigned — verify against PyMuPDF anchor."

VAR_02:
  name_as_printed: "EMPLOYMENT_GROWTH"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "EMPLOYMENT_GROWTH is defined as the percentage change in the number of employees (annual)."
  data_source_or_formula: "Percentage change in number of employees, annual. COMPUSTAT Annual Fundamentals (firm-level employment). Establishment-level analogue uses YTS (see VAR_08)."
  unit_or_transformation: "percentage change (annual), firm-year; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 17,620"
    mean: "Panel A: 0.08"
    sd: "Panel A: 0.28"
    median: "Panel A: 0.03"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.08/0.28/0.03/0.16/17,620; B 0.08/0.29/0.03/0.19/2,659; C 0.06/0.20/0.03/0.11/2,965; D 0.08/0.30/0.03/0.17/8,004; E 0.08/0.30/0.03/0.16/2,248. Also C.2, C.4/C.5."
    panel: "5 panels"
  uncertainty: "Minus signs stripped by PDF text layer; verify signs against PyMuPDF anchor."

VAR_03:
  name_as_printed: "R&D"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "R&D is defined as R&D expenditures divided by lagged total assets, considering only firms with non-missing R&D expenditures."
  data_source_or_formula: "R&D = R&D expenditures / lagged total assets. COMPUSTAT. Table 3 notes give: 'R&D is defined as total R&D expenditures divided by lagged total assets.'"
  unit_or_transformation: "ratio (no unit), firm-quarter; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 40,864"
    mean: "Panel A: 0.03"
    sd: "Panel A: 0.04"
    median: "Panel A: 0.02"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.03/0.04/0.02/0.04/40,864; B 0.03/0.04/0.02/0.04/5,019; C 0.02/0.03/0.01/0.02/6,200; D 0.03/0.04/0.02/0.04/19,988; E 0.03/0.04/0.01/0.03/4,745. Also C.2, C.4/C.5."
    panel: "5 panels"
  uncertainty: "Definition appears in two slightly different wordings (Table 1 vs Table 3 notes)."

VAR_04:
  name_as_printed: "DIVESTITURES"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "DIVESTITURES is defined as the value of sale of plant, property, and equipment divided by lagged total assets."
  data_source_or_formula: "DIVESTITURES = value of sale of plant, property, and equipment (SPP&E) / lagged total assets. COMPUSTAT. Table 3 notes: 'DIVESTITURES are defined as the value of SPP&E (Sale of Plant, Property, and Equipment) divided by lagged total assets.'"
  unit_or_transformation: "ratio; printed as DIVESTITURES (×100) in Table 1; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 61,151"
    mean: "Panel A: 0.06"
    sd: "Panel A: 0.28"
    median: "Panel A: 0.00"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Reported as DIVESTITURES (×100). Per-panel [Mean/SD/Median/IQR/N]: A 0.06/0.28/0.00/0.00/61,151; B 0.10/0.38/0.00/0.00/8,604; C 0.08/0.32/0.00/0.01/9,422; D 0.05/0.26/0.00/0.00/29,009; E 0.05/0.24/0.00/0.00/7,377. C.2 reports DIVESTITURES (×100): treated 0.129 / control 0.088 (Panel A)."
    panel: "5 panels"
  uncertainty: "Table 1 scaling label '(×100)' partially garbled in source text layer."

VAR_05:
  name_as_printed: "CASH"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "CASH is defined as cash and short-term investments divided by lagged total assets."
  data_source_or_formula: "CASH = cash and short-term investments / lagged total assets. COMPUSTAT."
  unit_or_transformation: "ratio; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 78,044"
    mean: "Panel A: 0.22"
    sd: "Panel A: 0.25"
    median: "Panel A: 0.12"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.22/0.25/0.12/0.27/78,044; B 0.20/0.24/0.11/0.26/11,176; C 0.17/0.18/0.11/0.19/12,097; D 0.23/0.25/0.13/0.29/36,985; E 0.22/0.24/0.12/0.26/9,533."
    panel: "5 panels"
  uncertainty: "CONFLICTING DEFINITION: Table 8 notes (p. 3208) redefine CASH as 'total cash holdings divided by lagged total assets net of cash holdings.' Table 1 vs Table 8 denominators differ — the Table 8 specification (Section V.C) is the one used in the CASH regression tests."

VAR_06:
  name_as_printed: "NON_CASH_WORKING_CAPITAL (NWC)"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "NON_CASH_WORKING_CAPITAL is defined as working capital (net of cash) divided by lagged total assets."
  data_source_or_formula: "NWC = working capital (net of cash) / lagged total assets. COMPUSTAT. Same wording in Table 8 notes."
  unit_or_transformation: "ratio; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 76,323"
    mean: "Panel A: 0.04"
    sd: "Panel A: 0.19"
    median: "Panel A: 0.03"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.04/0.19/0.03/0.20/76,323; B 0.05/0.18/0.04/0.19/10,846; C 0.08/0.16/0.07/0.20/11,738; D 0.01/0.20/0.02/0.20/36,292; E 0.06/0.19/0.04/0.21/9,260."
    panel: "5 panels"
  uncertainty: "Working-capital component can be negative; minus signs stripped in source text layer — verify means/medians signs against PyMuPDF anchor."

VAR_07:
  name_as_printed: "PROFITS"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3208
    section_or_table: "Table 8 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "PROFITS is defined as the quarterly percentage change in profits (operating income before depreciation divided by sales)."
  data_source_or_formula: "PROFITS = quarterly % change in (operating income before depreciation / sales). COMPUSTAT."
  unit_or_transformation: "percentage change (quarterly), firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Not in Table 1; only regression coefficients (Table 8, cols 5–6, p. 3208) are reported."
    panel: "N/A"
  uncertainty: "none"

VAR_08:
  name_as_printed: "ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH (column header: 'ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH')"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3202
    section_or_table: "§V.B.1.b text + Table 5 header/notes"
    paragraph_position: 2
    definition_verbatim: "We first repeat the analysis of Table 2 using establishment-level employment growth calculated based on YTS data on the number of employees across all establishments operated by sample firms in the United States."
  data_source_or_formula: "Percentage change in number of employees aggregated across all U.S. establishments of a firm, from YTS (Your-Economy Time-Series) database."
  unit_or_transformation: "percentage change, firm-year (U.S. establishments only)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Only regression coefficients reported (Table 5, cols 1–2, p. 3203)."
    panel: "N/A"
  uncertainty: "Table 5 column structure is heavily garbled in the source text layer (page 3203); column-to-coefficient mapping should be confirmed against PyMuPDF anchor."

VAR_09:
  name_as_printed: "ESTABLISHMENT_TURNOVER"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3203
    section_or_table: "Footnote 24"
    paragraph_position: "N/A (footnote)"
    definition_verbatim: "Establishment turnover is defined as the sum of establishment openings and closings, divided by the lagged number of total establishments."
  data_source_or_formula: "(establishment openings + establishment closings) / lagged total number of establishments. YTS database."
  unit_or_transformation: "ratio, firm-year"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Only regression coefficients reported (Table 5, cols 3–4, p. 3203)."
    panel: "N/A"
  uncertainty: "none"

VAR_10:
  name_as_printed: "INVESTMENT (U.S.-based subsidiaries)"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3201
    section_or_table: "§V.B.1.a text + Table 4 notes"
    paragraph_position: 2
    definition_verbatim: "For each parent firm, in each year, we compute their U.S.-based investment by summing fixed capital spending across their U.S. subsidiaries."
  data_source_or_formula: "Sum of fixed capital spending across a parent firm's U.S. subsidiaries (then scaled as INVESTMENT). Bureau van Dijk Orbis subsidiary-level data."
  unit_or_transformation: "ratio, firm-year (parent firm, U.S. subsidiaries)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Regression coefficients only (Table 4, cols 1–2, p. 3203)."
    panel: "N/A"
  uncertainty: "Text (p. 3201) refers to results 'in columns 1 and 2 of Table 3' but Table 4 holds the subsidiary results; cross-reference appears to be a typo in the body text."

VAR_11:
  name_as_printed: "INVESTMENT (U.K.-based subsidiaries)"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: 3201
    section_or_table: "§V.B.1.a text + Table 4 notes"
    paragraph_position: 3
    definition_verbatim: "We similarly calculate the total U.K.-based investment of each U.S. parent firm by summing spending figures across U.K. subsidiaries."
  data_source_or_formula: "Sum of fixed capital spending across a parent firm's U.K. subsidiaries (then scaled as INVESTMENT). Orbis subsidiary-level data."
  unit_or_transformation: "ratio, firm-year (parent firm, U.K. subsidiaries)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Regression coefficients only (Table 4, cols 3–4, p. 3203)."
    panel: "N/A"
  uncertainty: "none"

VAR_12:
  name_as_printed: "AUTOMATIONi,t"
  role: "DV"
  raw_or_derived: "derived"
  primary_definition:
    page: "IA p. 18 (Internet Appendix)"
    section_or_table: "Table E.2 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "The dependent variable is AUTOMATIONi,t, which is constructed from a dictionary of keywords that capture exposure to automation at the firm level, as described in Appendix E. This text-based continuous variable is the logarithm of the total number of automation-related keywords that appear in firm i's business description (10-K Section 1) and management discussion (10-K Section 7), at the firm-year level."
  data_source_or_formula: "Time-varying analogue of AUTOMATIONi = log(total automation-related keyword count in 10-K Sections 1 and 7), at firm-year level. Firms' 10-K filings."
  unit_or_transformation: "log count, firm-year"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Distribution of the (time-averaged) AUTOMATIONi shown as a histogram in Figure E.1 (IA p. 16); no numeric moments printed. Table E.2 reports only regression coefficients (cols 1–2)."
    panel: "N/A"
  uncertainty: "AUTOMATIONi,t (time-varying, firm-year, DV in Table E.2) differs from AUTOMATIONi (time-averaged 2010–2015, RHS control in Table 11). Both share the AUTOMATION root — list separately (see VAR_59)."

VAR_13:
  name_as_printed: "βUK_i (β_i^UK)"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.1 text + equation (13)"
    paragraph_position: 1
    definition_verbatim: "Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i as vol(r_it) = α_i + β_i^UK vol(FTSE100_t) + θCONTROLS_t + ϵ_it (13). … For each firm, we take the estimated value of β_i^UK from regression (13) as the empirical counterpart to β_i in our framework."
  data_source_or_formula: "Firm-by-firm OLS slope on vol(FTSE100) in eq (13): vol(r_it) = α_i + β_i^UK·vol(FTSE100_t) + θ·CONTROLS_t + ϵ_it, where CONTROLS_t = vol(SP500) and vol(FX$£). Monthly data 2010:M1–2014:M12. Empirical counterpart to theoretical sensitivity parameter β_i."
  unit_or_transformation: "regression coefficient (no unit), firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (no distributional moments table)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Cutoffs given in §IV.C.1 (p. 3193): treated = β_i^UK > 0.68 (449 unique firms); control = β_i^UK < 0.28 (360 unique firms)."
    panel: "N/A"
  uncertainty: "Superscript UK and subscript i are reconstructed from garbled glyphs 'βUKi' in the source text layer."

VAR_14:
  name_as_printed: "HIGH_UK_EXPOSURE_i / HIGH_βUK_i"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3196
    section_or_table: "§IV.C.3 text (equation (14) variable definitions)"
    paragraph_position: 2
    definition_verbatim: "HIGH_UK_EXPOSURE_i is a dummy variable that equals 1 if firm i is U.K.-exposed, and 0 otherwise. A firm is considered to be U.K.-exposed according to two measures: i) if it belongs to the top tercile of β_i^UK (market-based measure); or ii) if it has a high number of Brexit-related entries in its 2015 10-K form (textual-search-based measure)."
  data_source_or_formula: "Dummy = 1 if firm in top tercile of β_i^UK (market-based) OR has >5 Brexit-related 10-K entries (text-based); control = bottom tercile of β_i^UK or zero 10-K entries."
  unit_or_transformation: "binary {0,1}, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Group sizes (market-based): 449 treated / 360 control (§IV.C.1, p. 3193)."
    panel: "N/A"
  uncertainty: "Printed as both 'HIGH_UK_EXPOSURE' and 'HIGH_βUK_i' / 'HIGH_β_i^UK' across text and table column headers for the same market-based dummy."

VAR_15:
  name_as_printed: "number of Brexit-related entries in 2015 10-K (count)"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.2"
    paragraph_position: 1
    definition_verbatim: "we look for the number of entries of keywords related to uncertainty about Brexit (\"Brexit,\" \"Great Britain,\" and \"Uncertainty\") in firms' disclosures, classifying firms with a \"high\" number of entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control firms."
  data_source_or_formula: "Word count of Brexit-related keywords ('Brexit,' 'Great Britain,' 'Uncertainty') in firms' 2015 10-K filings. Footnote 14: 'Referendum,' 'Uncertain,' 'United Kingdom,' 'UK,' 'U.K.,' and 'G.B.' are subsumed by the above wording."
  unit_or_transformation: "count, firm-level (2015 10-K)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (as distribution)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Cutoff >5 entries. 807 firms cite Brexit more than 5 times; 433 cite zero (p. 3192/3193)."
    panel: "N/A"
  uncertainty: "none"

VAR_16:
  name_as_printed: "HIGH_10K_ENTRIES (printed: 'HIGH_10K_ENTRIES' / 'Treatment is > 5 Brexit Entries in 10-Ks')"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3193
    section_or_table: "§IV.C.1"
    paragraph_position: 1
    definition_verbatim: "Under this approach, 807 firms are assigned to the treated category (2015 10-K mentions of Brexit terms > 5). A total of 433 firms in the control category have no mentions of Brexit-related terms in their 10-Ks."
  data_source_or_formula: "Dummy = 1 if 2015 10-K Brexit-related entry count >5; 0 if zero entries (control). Derived from VAR_15."
  unit_or_transformation: "binary {0,1}, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "807 treated / 433 control."
    panel: "N/A"
  uncertainty: "none"

VAR_17:
  name_as_printed: "POST_t"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3196
    section_or_table: "§IV.C.3 (equation (14) variable definitions)"
    paragraph_position: 2
    definition_verbatim: "POST_t equals 1 if the time period is in the 2016:Q3–Q4 window."
  data_source_or_formula: "Time dummy = 1 for 2016:Q3–Q4 window (compared against 2015:Q3–Q4). Alternative windows in robustness (Table 12): 2016:Q3 vs 2015:Q3; 2015:Q3 vs 2014:Q3; 2011:Q2–Q4 vs 2010:Q2–Q4."
  unit_or_transformation: "binary {0,1}, time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Standalone POST coefficients reported in linear-model specifications (e.g., Table 2 col 1: 0.022; Table C.7 Panel A col 1: −0.042)."
    panel: "N/A"
  uncertainty: "none"

VAR_18:
  name_as_printed: "βUK_i,CF (β_i,CF^UK)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3191
    section_or_table: "Footnote 13"
    paragraph_position: "N/A (footnote)"
    definition_verbatim: "Following Vuolteenaho (2002), we also decompose the volatility of each firm's returns into cash flow and discount rate components and reestimate equation (13) with the cash flow component (only) as the dependent variable, obtaining an alternative uncertainty measure, β_i,CF^UK."
  data_source_or_formula: "Re-estimate eq (13) using the cash-flow-news component of return volatility (Campbell–Shiller (1988) / Vuolteenaho (2002) decomposition) as the dependent variable. IA Table C.6 notes give full construction."
  unit_or_transformation: "regression coefficient, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Rank correlation with β_i^UK = 0.8; 86% overlap of top-tercile sets (footnote 13). Results in IA Table C.6."
    panel: "N/A"
  uncertainty: "none"

VAR_19:
  name_as_printed: "βEU_i (β_i^EU)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3216
    section_or_table: "§VI.F text + Table 13"
    paragraph_position: 1
    definition_verbatim: "we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility."
  data_source_or_formula: "Analogue of eq (13) re-estimated with the EU main equity index volatility; controls = FTSE100 vol, USD/GBP FX-rate vol, and USD/EUR FX-rate vol. Pre-Brexit window 2010:M1–2014:M12."
  unit_or_transformation: "regression coefficient, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Treatment = top tercile of positive values. Coefficient in Table 13 col 2."
    panel: "N/A"
  uncertainty: "none"

VAR_20:
  name_as_printed: "βCHINA_i (β_i^CHINA)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3216
    section_or_table: "§VI.F text + Table 13"
    paragraph_position: 1
    definition_verbatim: "we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility."
  data_source_or_formula: "Analogue of eq (13) using China's main equity index volatility; controls include FTSE100 vol, USD/GBP FX vol, and USD/CNY FX vol."
  unit_or_transformation: "regression coefficient, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 13 col 3 (statistically insignificant)."
    panel: "N/A"
  uncertainty: "none"

VAR_21:
  name_as_printed: "βMEXICO_i (β_i^MEXICO)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3216
    section_or_table: "§VI.F text + Table 13"
    paragraph_position: 1
    definition_verbatim: "we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility."
  data_source_or_formula: "Analogue of eq (13) using Mexico's main equity index volatility; FX controls include USD/MXN."
  unit_or_transformation: "regression coefficient, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 13 col 4 (insignificant)."
    panel: "N/A"
  uncertainty: "none"

VAR_22:
  name_as_printed: "βJAPAN_i (β_i^JAPAN)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3216
    section_or_table: "§VI.F text + Table 13"
    paragraph_position: 1
    definition_verbatim: "we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility."
  data_source_or_formula: "Analogue of eq (13) using Japan's main equity index volatility; FX controls include USD/JPY."
  unit_or_transformation: "regression coefficient, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 13 col 5 (insignificant)."
    panel: "N/A"
  uncertainty: "none"

VAR_23:
  name_as_printed: "βINDIA_i (β_i^INDIA)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3216
    section_or_table: "§VI.F text + Table 13"
    paragraph_position: 1
    definition_verbatim: "we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility."
  data_source_or_formula: "Analogue of eq (13) using India's main equity index volatility; FX controls include USD/INR."
  unit_or_transformation: "regression coefficient, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 13 col 6 (insignificant)."
    panel: "N/A"
  uncertainty: "none"

VAR_24:
  name_as_printed: "βBRAZIL_i (β_i^BRAZIL)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3216
    section_or_table: "§VI.F text + Table 13"
    paragraph_position: 1
    definition_verbatim: "we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility."
  data_source_or_formula: "Analogue of eq (13) using Brazil's main equity index volatility; FX controls include USD/BRL."
  unit_or_transformation: "regression coefficient, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 13 col 7 (insignificant)."
    panel: "N/A"
  uncertainty: "none"

VAR_25:
  name_as_printed: "U.K. Offshoring Index (Input and Output / Total) — 'HIGH_UK_OFFSHORING_INDEX'"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3205
    section_or_table: "§V.B.2 text + Table 6 notes"
    paragraph_position: 1
    definition_verbatim: "We do this using the index of firms' offshoring activities developed by Hoberg and Moon (2017). This index, derived from firms' 10-K filings, counts mentions of words related to the purchase of inputs (\"Input\") and sale of outputs (\"Output\") from each country a firm does business with within a year. For each sample firm, we compute the sum of the Input and Output indices associated with the United Kingdom over the 2010–2014 period … We define as highly U.K.-offshoring-exposed firms those with a value of greater than 5 on a given offshoring index. Control firms are those with scores of 0 on the same index."
  data_source_or_formula: "Hoberg and Moon (2017) offshoring index summed over 2010–2014, combining Input + Output mentions for the U.K.; treatment dummy = 1 if total >5, control = 0."
  unit_or_transformation: "binary {0,1} treatment dummy from a count index, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 6 col 3 (0.074***)."
    panel: "N/A"
  uncertainty: "none"

VAR_26:
  name_as_printed: "U.K. Offshoring Index (Input Only)"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3205
    section_or_table: "§V.B.2 text + Table 6 notes"
    paragraph_position: 2
    definition_verbatim: "In the fourth column, the treatment group consists of firms with scores of greater than 5 on the Hoberg–Moon U.K. Offshoring Index summed up over years 2010–2014, considering only input offshoring activities, whereas the control group is made of firms with scores of 0 on this index."
  data_source_or_formula: "Hoberg and Moon (2017) Input offshoring index for the U.K., summed 2010–2014; treatment dummy = 1 if >5, control = 0."
  unit_or_transformation: "binary {0,1}, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 6 col 4 (0.095***)."
    panel: "N/A"
  uncertainty: "none"

VAR_27:
  name_as_printed: "U.K. Offshoring Index (Output Only)"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3206
    section_or_table: "Table 6 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "In the final specification, the treatment group consists of firms with scores of greater than 5 on the Hoberg and Moon (2017) U.K. Offshoring Index summed up over years 2010–2014, considering only output offshoring activities, whereas the control group is made of firms with scores of 0 on this index."
  data_source_or_formula: "Hoberg and Moon (2017) Output offshoring index for the U.K., summed 2010–2014; treatment dummy = 1 if >5, control = 0."
  unit_or_transformation: "binary {0,1}, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficient in Table 6 col 5 (0.000; effect zero)."
    panel: "N/A"
  uncertainty: "none"

VAR_28:
  name_as_printed: "asset redeployability index (Kim and Kung (2016)) / HIGH_INPUT_IRREVERSIBILITY (capital)"
  role: "Moderator"
  raw_or_derived: "derived"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.3 text"
    paragraph_position: 1
    definition_verbatim: "To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016). That index classifies fixed capital liquidity in terms of salability of assets in secondary markets. … Higher values of the asset redeployability index are associated with a lower degree of capital irreversibility, corresponding to a lower value of F_iK in our framework."
  data_source_or_formula: "Kim and Kung (2016) asset redeployability index. Table 7 notes: 'High capital irreversibility is defined as the top tercile of the Kim and Kung (2016) index of asset redeployability (at the firm level).' (Bottom tercile of redeployability = high irreversibility.)"
  unit_or_transformation: "index (no unit) → tercile partition, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Used to form High/Low irreversibility subsamples (Table 7, cols 1–3)."
    panel: "N/A"
  uncertainty: "Table 7 notes call the top tercile 'High capital irreversibility' while §IV.A.3 ties high redeployability to LOW irreversibility — confirm the exact direction of the tercile cut against the code."

VAR_29:
  name_as_printed: "labor unionization rate (BEA) / High labor irreversibility"
  role: "Moderator"
  raw_or_derived: "derived"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.3 text"
    paragraph_position: 2
    definition_verbatim: "we measure the percentage of total employees who are unionized at the 4-digit SIC level using data from the Bureau of Economic Analysis."
  data_source_or_formula: "Percentage of unionized employees at 4-digit SIC level, from BEA. Table 7 notes: 'High labor irreversibility is defined as the top tercile of the labor unionization rate (at the industry level).'"
  unit_or_transformation: "percentage → tercile partition, industry-level (4-digit SIC)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Used to form High/Low irreversibility subsamples (Table 7, cols 4–6)."
    panel: "N/A"
  uncertainty: "Table 7 notes describe its proxy role: 'The proxy for labor adjustment costs is the labor unionization rate from the Bureau of Economic Analysis.'"

VAR_30:
  name_as_printed: "labor skills index (LSI) (Ghaly, Dang, and Stathopoulos (2017))"
  role: "Moderator"
  raw_or_derived: "derived"
  primary_definition:
    page: 3203
    section_or_table: "§V.B.1.b text"
    paragraph_position: 3
    definition_verbatim: "As a proxy for labor skills, we use the industry-level labor skills index (LSI) proposed by Ghaly, Dang, and Stathopoulos (2017). The LSI is based on data from the Occupational Employment Statistics compiled by the Bureau of Labor Statistics (BLS) and the Department of Labor's O*NET program classification."
  data_source_or_formula: "Weighted-average O*NET occupational skills classification (1–5 scale) across all occupations in an industry, weighted by fraction of workers per occupation (BLS Occupational Employment Statistics + O*NET). Table 5 notes: 'Low (high) skills firms are defined as firms in the bottom (top) tercile of the 2015 LSI (at the industry level).'"
  unit_or_transformation: "index (1–5 scale, weighted average) → tercile partition, industry-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Used to form Low/High Skills subsamples (Table 5, cols 5–8)."
    panel: "N/A"
  uncertainty: "Construction text continued on p. 3204."

VAR_31:
  name_as_printed: "POST_t × βUK_i  (POST·β_i^UK, linear continuous treatment)"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3199
    section_or_table: "§V.A text + Table 2 col 1 header"
    paragraph_position: 1
    definition_verbatim: "We begin with a firm-fixed effects estimation in which β_i^UK enters the specification as a linear continuous-treatment variable in column 1, allowing for the entire range of β_i^UK values. The POST·β_i^UK interaction coefficient is negative and highly significant, consistent with Prediction 1."
  data_source_or_formula: "Interaction of POST_t (VAR_17) with continuous β_i^UK (VAR_13) in eq (14)."
  unit_or_transformation: "interaction term, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (regression coefficient only)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Coefficients: INVESTMENT −0.047*** (Table 2 col 1); EMPLOYMENT_GROWTH −4.173** (Table 2 col 4); R&D 0.361*** (Table 3 col 1); DIVESTITURES 0.012*** (Table 3 col 4)."
    panel: "N/A"
  uncertainty: "Table 2 column block in source text layer interleaves INVESTMENT and EMPLOYMENT_GROWTH coefficient rows; confirm sign/column mapping against PyMuPDF anchor."

VAR_32:
  name_as_printed: "POST × HIGH_βUK_i  (POST·HIGH_β_i^UK)"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3196
    section_or_table: "equation (14), §IV.C.3"
    paragraph_position: 1
    definition_verbatim: "Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}."
  data_source_or_formula: "Interaction POST_t × HIGH_β_i^UK (top-vs-bottom-tercile market-based treatment dummy). δ is the DID estimator."
  unit_or_transformation: "interaction term, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (regression coefficient only)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Baseline coefficients: INVESTMENT −0.165*** (Table 2); EMPLOYMENT_GROWTH −4.912*** (Table 2); R&D 0.238*** (Table 3); DIVESTITURES −0.027** (Table 3); CASH 0.231*** (Table 8); NWC −0.687*** (Table 8); PROFITS 0.135 n.s. (Table 8)."
    panel: "N/A"
  uncertainty: "Signs reconstructed where stripped; verify against anchor."

VAR_33:
  name_as_printed: "POST × HIGH_10K_ENTRIES"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3196
    section_or_table: "equation (14), §IV.C.3"
    paragraph_position: 1
    definition_verbatim: "Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}."
  data_source_or_formula: "Interaction POST_t × HIGH_10K_ENTRIES (text-based treatment dummy, VAR_16). δ is the DID estimator under the text-based scheme."
  unit_or_transformation: "interaction term, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (regression coefficient only)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Baseline coefficients: INVESTMENT −0.077*** (Table 2); EMPLOYMENT_GROWTH −2.617*** (Table 2); R&D 0.213*** (Table 3); DIVESTITURES −0.027*** (Table 3); CASH 0.357*** (Table 8); NWC −0.608*** (Table 8); PROFITS 0.343 n.s. (Table 8)."
    panel: "N/A"
  uncertainty: "none"

VAR_34:
  name_as_printed: "POST × HIGH_UK_OFFSHORING_INDEX"
  role: "Treatment"
  raw_or_derived: "derived"
  primary_definition:
    page: 3206
    section_or_table: "Table 6 (column headers + notes)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "In the third column, the treatment group consists of firms with scores of greater than five on the Hoberg–Moon U.K. Offshoring Index summed up over years 2010–2014, considering both input and output offshoring activities, whereas the control group is made of firms with scores of 0 on this index."
  data_source_or_formula: "Interaction POST_t × HIGH_UK_OFFSHORING_INDEX (Total / Input-only / Output-only treatment dummies, VAR_25/26/27)."
  unit_or_transformation: "interaction term, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (regression coefficient only)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "INVESTMENT coefficients (Table 6): Total −0.074***; Input-only −0.095***; Output-only 0.000."
    panel: "N/A"
  uncertainty: "none"

VAR_35:
  name_as_printed: "POST × HIGH_βUK_i × HIGH_INPUT_IRREVERSIBILITY (DIDID triple interaction)"
  role: "Moderator"
  raw_or_derived: "derived"
  primary_definition:
    page: 3207
    section_or_table: "§V.B.3 text + Table 7 (col 3 / col 6 rows)"
    paragraph_position: 1
    definition_verbatim: "The estimation under column 3 uses the entire sample of firms, introducing a dummy variable High Irreversibility that equals 1 if the firm is in the high irreversibility group. The coefficient on this variable can be interpreted as a third difference in a differences-test framework, that is, as a difference-in-difference-in-differences (DIDID) estimate."
  data_source_or_formula: "Triple interaction POST_t × HIGH_β_i^UK × HIGH_INPUT_IRREVERSIBILITY, printed in Table 7 as 'POST·HIGH_βUK_i·HIGH_INPUT_IRREVERSIBILITY'. Capital version uses Kim–Kung redeployability (VAR_28); labor version uses unionization (VAR_29)."
  unit_or_transformation: "triple interaction term, firm-quarter (investment) / firm-year (employment)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (regression coefficient only)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Triple-interaction coefficients (Table 7): INVESTMENT −0.397*** (col 3); EMPLOYMENT_GROWTH −3.577*** (col 6)."
    panel: "N/A"
  uncertainty: "Table 7 row label printed as 'POSTHIGH_βUKiHIGH_INPUT_IRREVERSIBILITY' (operators dropped in source text layer)."

VAR_36:
  name_as_printed: "POST × HIGH_βCOUNTRY_i  (POST·HIGH_β^COUNTRY)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3216
    section_or_table: "Table 13 (row header)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "treated firms are in the highest tercile of positive values of exposure of firm-level volatility to equity index volatility in the European Union, China, Mexico, Japan, India, and Brazil, respectively."
  data_source_or_formula: "Generic interaction POST_t × HIGH_β_i^COUNTRY; instantiated per country (VAR_19–24). Investment DV."
  unit_or_transformation: "interaction term, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (regression coefficient only)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 13 INVESTMENT coefficients: UK −0.165***; EU −0.066***; China −0.048; Mexico −0.069; Japan −0.084; India −0.058; Brazil −0.054. (Only UK and EU significant.)"
    panel: "N/A"
  uncertainty: "Signs stripped in source; reconstructed from text discussion (§VI.F)."

VAR_37:
  name_as_printed: "POST × HIGH_βUK_i,CF  (POST·HIGH_β_i,CF^UK)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: "IA p. 11"
    section_or_table: "Table C.6 (row header + notes)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "The treatment group is composed by the top tercile of β^UK_i,CF, while the control group is composed by firms in the bottom tercile of β^UK_i,CF."
  data_source_or_formula: "Interaction POST_t × top-tercile dummy of β_i,CF^UK (VAR_18). DVs: INVESTMENT, EMPLOYMENT_GROWTH, R&D, DIVESTITURES."
  unit_or_transformation: "interaction term, firm-quarter / firm-year"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (regression coefficient only)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "IA Table C.6 coefficients: INVESTMENT −0.330***; EMPLOYMENT_GROWTH −5.147**; R&D 0.348***; DIVESTITURES −0.034***."
    panel: "N/A"
  uncertainty: "none"

VAR_38:
  name_as_printed: "TOBIN_Q (Tobin's Q)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "TOBIN_Q is defined as the market value of assets divided by the book value of assets, and is calculated as the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets."
  data_source_or_formula: "TOBIN_Q = (market value of equity + book value of assets − book value of equity + deferred taxes) / book value of assets. COMPUSTAT + CRSP."
  unit_or_transformation: "ratio (no unit); winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 73,353"
    mean: "Panel A: 2.11"
    sd: "Panel A: 1.59"
    median: "Panel A: 1.57"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 2.11/1.59/1.57/1.26/73,353; B 1.92/1.51/1.41/1.01/11,090; C 1.98/1.25/1.62/1.07/12,055; D 2.10/1.59/1.55/1.29/34,108; E 2.06/1.54/1.55/1.17/9,138."
    panel: "5 panels"
  uncertainty: "Also enters as firm-level control (p. 3197) and is reported in Table C.7 with coefficients."

VAR_39:
  name_as_printed: "CASH_FLOW"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "CASH_FLOW is defined as operating income before depreciation divided by lagged total assets."
  data_source_or_formula: "CASH_FLOW = operating income before depreciation / lagged total assets. COMPUSTAT."
  unit_or_transformation: "ratio; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 75,287"
    mean: "Panel A: 0.01"
    sd: "Panel A: 0.06"
    median: "Panel A: 0.03"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.01/0.06/0.03/0.04/75,287; B 0.01/0.06/0.02/0.04/10,972; C 0.03/0.04/0.03/0.03/11,871; D 0.01/0.07/0.02/0.04/35,432; E 0.01/0.07/0.02/0.04/9,240. Table C.7 reports CASH_FLOW control coefficients."
    panel: "5 panels"
  uncertainty: "Cash flow is frequently negative; minus signs stripped in source — mean values likely include dropped signs (e.g., several panel means may be negative). Verify against anchor."

VAR_40:
  name_as_printed: "SIZE (Log Assets)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "SIZE is defined as the logarithm of total assets."
  data_source_or_formula: "SIZE = log(total assets). COMPUSTAT."
  unit_or_transformation: "log of USD; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 78,062"
    mean: "Panel A: 6.19"
    sd: "Panel A: 2.08"
    median: "Panel A: 6.15"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 6.19/2.08/6.15/3.08/78,062; B 6.11/1.87/6.12/2.86/11,176; C 7.25/1.99/7.25/2.65/12,097; D 6.08/2.06/6.02/3.12/37,002; E 5.95/2.15/5.86/3.23/9,533. Table C.7 reports SIZE coefficients."
    panel: "5 panels"
  uncertainty: "none"

VAR_41:
  name_as_printed: "SALES_GROWTH"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales."
  data_source_or_formula: "SALES_GROWTH = year-on-year % change in quarterly sales. COMPUSTAT."
  unit_or_transformation: "percentage change; winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 71,637"
    mean: "Panel A: 0.16"
    sd: "Panel A: 0.62"
    median: "Panel A: 0.06"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.16/0.62/0.06/0.23/71,637; B 0.18/0.71/0.06/0.31/10,624; C 0.10/0.36/0.06/0.16/11,969; D 0.17/0.66/0.06/0.25/33,647; E 0.17/0.67/0.05/0.22/8,835. Table C.7 reports SALES_GROWTH coefficients."
    panel: "5 panels"
  uncertainty: "none"

VAR_42:
  name_as_printed: "CONSENSUS_EARNINGS_FORECAST"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "CONSENSUS_EARNINGS_FORECAST is defined as the standardized mean 1-quarter ahead earnings per share forecast."
  data_source_or_formula: "Standardized mean 1-quarter-ahead EPS forecast. I/B/E/S. Added 'As an additional control for first-moment effects of Brexit' (p. 3197)."
  unit_or_transformation: "standardized (mean 0, SD 1)"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 42,031"
    mean: "Panel A: 0.07"
    sd: "Panel A: 3.51"
    median: "Panel A: 0.09"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.07/3.51/0.09/2.05/42,031; B 0.01/3.40/0.01/1.83/8,963; C 0.07/2.33/0.04/2.40/10,720; D 0.04/3.46/0.04/2.06/26,008; E 0.01/4.46/0.04/1.79/6,929. Table C.7 reports coefficients."
    panel: "5 panels"
  uncertainty: "Standardized variable can be negative; signs stripped in source — several means/medians likely negative. Verify against anchor."

VAR_43:
  name_as_printed: "STOCK_RETURNS (lagged stock returns)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "STOCK_RETURNS are defined as the quarterly buy-and-hold return."
  data_source_or_formula: "Quarterly buy-and-hold equity return (entered lagged as a firm control). CRSP."
  unit_or_transformation: "return (ratio); winsorized at 1%"
  reported_summary_stats:
    found_in: "Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)"
    N: "Panel A: 67,226"
    mean: "Panel A: 0.03"
    sd: "Panel A: 0.24"
    median: "Panel A: 0.02"
    p25: "N/A (paper reports IQR)"
    p75: "N/A (paper reports IQR)"
    other_stats: "Per-panel [Mean/SD/Median/IQR/N]: A 0.03/0.24/0.02/0.25/67,226; B 0.02/0.27/0.00/0.30/11,088; C 0.04/0.18/0.03/0.20/12,063; D 0.02/0.25/0.01/0.27/29,983; E 0.03/0.24/0.02/0.24/8,523. Table C.7 reports STOCK_RETURNS coefficients (some negative)."
    panel: "5 panels"
  uncertainty: "Returns can be negative; signs stripped in source. Verify against anchor."

VAR_44:
  name_as_printed: "lagged U.S. dollar/British pound FX rate"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (Empirical Model, control list)"
    paragraph_position: 1
    definition_verbatim: "Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingstone Survey, the lagged Consumer Sentiment Index from the University of Michigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia."
  data_source_or_formula: "Lagged USD/GBP exchange-rate level. Bloomberg currency data; macro series cross-checked via FRED."
  unit_or_transformation: "exchange-rate level (lagged), time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Macro control; used only in linear-model specifications (industry×time FE absorb macro factors otherwise)."
    panel: "N/A"
  uncertainty: "Distinct from the vol(FX$£) input to eq (13) (VAR_76) and from the FX-exposure controls in Table 9 (VAR_49–52)."

VAR_45:
  name_as_printed: "lagged VIX implied volatility index"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (control list)"
    paragraph_position: 1
    definition_verbatim: "Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingstone Survey, the lagged Consumer Sentiment Index from the University of Michigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia."
  data_source_or_formula: "Lagged VIX index level. CBOE VIX (via FRED/Bloomberg)."
  unit_or_transformation: "index level (lagged), time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Macro control."
    panel: "N/A"
  uncertainty: "none"

VAR_46:
  name_as_printed: "lagged mean GDP growth 1-year-ahead forecast (Livingstone Survey)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (control list)"
    paragraph_position: 1
    definition_verbatim: "the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingstone Survey"
  data_source_or_formula: "Lagged mean 1-year-ahead GDP growth forecast, Federal Reserve Bank of Philadelphia Livingstone Survey."
  unit_or_transformation: "forecast growth rate (lagged), time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Macro control."
    panel: "N/A"
  uncertainty: "Printed 'Livingstone Survey'; the Philadelphia Fed series is commonly spelled 'Livingston Survey' — transcribed as printed."

VAR_47:
  name_as_printed: "lagged Consumer Sentiment Index (University of Michigan)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (control list)"
    paragraph_position: 1
    definition_verbatim: "the lagged Consumer Sentiment Index from the University of Michigan"
  data_source_or_formula: "Lagged University of Michigan Consumer Sentiment Index level."
  unit_or_transformation: "index level (lagged), time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Macro control."
    panel: "N/A"
  uncertainty: "none"

VAR_48:
  name_as_printed: "lagged Leading Economic Indicator (Federal Reserve Bank of Philadelphia)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (control list)"
    paragraph_position: 1
    definition_verbatim: "the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia"
  data_source_or_formula: "Lagged Leading Economic Indicator, Federal Reserve Bank of Philadelphia."
  unit_or_transformation: "index level (lagged), time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Macro control."
    panel: "N/A"
  uncertainty: "none"

VAR_49:
  name_as_printed: "βFX£_i,t (β_i,t^FX£)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3209
    section_or_table: "§VI.A text + Table 9 notes"
    paragraph_position: 2
    definition_verbatim: "We include as an additional control each firm's end-of-quarter coefficient on FX£, namely β^FX£_i,t, which captures the time-varying sensitivity of firm i's equity returns to changes in the British pound."
  data_source_or_formula: "Firm-by-firm rolling regression of equity-return levels on U.S. and U.K. equity index returns and USD–GBP FX-rate changes; 24-month rolling windows over 2010:M1–2016:M12 (footnote 27). β^FX£_i,t is the end-of-quarter GBP-sensitivity coefficient."
  unit_or_transformation: "regression coefficient (time-varying), firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Used as control in Table 9 cols 1–2 (INVESTMENT DID coefficients −0.172*** / −0.080***)."
    panel: "N/A"
  uncertainty: "none"

VAR_50:
  name_as_printed: "Alfaro et al. (2018) GBP Instruments (first- and second-moment)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3209
    section_or_table: "§VI.A text + Table 9 notes"
    paragraph_position: 2
    definition_verbatim: "Second, we include in our estimations the Alfaro et al. (2018) firm-level instruments for first- and second-moment shocks to the USD–GBP rate."
  data_source_or_formula: "Alfaro, Bloom, and Lin (2018) firm-level instruments for first- and second-moment shocks to the USD–GBP rate (Finance Uncertainty Multiplier instruments)."
  unit_or_transformation: "firm-level instrument controls"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 9 cols 3–4 (INVESTMENT DID −0.145*** / −0.097***)."
    panel: "N/A"
  uncertainty: "Related to but distinct from the first-moment-only instrument set used in Table C.7 (VAR_57)."

VAR_51:
  name_as_printed: "FX hedging dummy (prior-year)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3209
    section_or_table: "§VI.A text + Table 9 notes"
    paragraph_position: 2
    definition_verbatim: "We include as additional controls a dummy variable for whether a firm engaged in FX hedging activity in the prior year, and the intensity of hedging in the prior year as measured by the number of keywords mentioned."
  data_source_or_formula: "Dummy = 1 if firm engaged in FX hedging in prior year. Keyword search of 10-K disclosures following Campello, Lin, Ma, and Zou (2011)."
  unit_or_transformation: "binary {0,1}, firm-year (lagged)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 9 'FX Hedging' columns (cols 5–6)."
    panel: "N/A"
  uncertainty: "none"

VAR_52:
  name_as_printed: "FX hedging intensity (number of keywords)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3209
    section_or_table: "§VI.A text + Table 9 notes"
    paragraph_position: 2
    definition_verbatim: "the intensity of hedging in the prior year as measured by the number of keywords mentioned."
  data_source_or_formula: "Count of FX-hedging-related keywords (from Campello, Lin, Ma, and Zou (2011) list) mentioned in prior-year 10-K."
  unit_or_transformation: "count (lagged), firm-year"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 9 'FX Hedging' columns."
    panel: "N/A"
  uncertainty: "none"

VAR_53:
  name_as_printed: "existing bond yields (yields to maturity on existing bonds)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3211
    section_or_table: "§VI.B text + Table 10 notes"
    paragraph_position: 1
    definition_verbatim: "we reestimate the analysis of Table 2 controlling for yields on existing bonds (obtained from TRACE)"
  data_source_or_formula: "Yields to maturity on firms' existing traded bonds. TRACE."
  unit_or_transformation: "yield (%, lagged), firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 10 'Existing Bond Yields' (cols 1–2); INVESTMENT DID −0.168*** / −0.072***."
    panel: "N/A"
  uncertainty: "none"

VAR_54:
  name_as_printed: "new bond yields (yields on new bond issues)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3211
    section_or_table: "§VI.B text + Table 10 notes"
    paragraph_position: 1
    definition_verbatim: "yields on new bond issues (from SDC)"
  data_source_or_formula: "Yields to maturity on new bond issues. SDC."
  unit_or_transformation: "yield (%), firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 10 'New Bond Yields' (cols 3–4)."
    panel: "N/A"
  uncertainty: "none"

VAR_55:
  name_as_printed: "new syndicated loan spreads / markups (all-in spread)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3211
    section_or_table: "§VI.B text + Table 10 notes"
    paragraph_position: 1
    definition_verbatim: "markups on new syndicated loans (from DealScan)"
  data_source_or_formula: "All-in spreads/markups on new syndicated loans. WRDS–Reuters DealScan."
  unit_or_transformation: "spread (bps), firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 10 'New Syndicated Loan Spreads' (cols 5–6)."
    panel: "N/A"
  uncertainty: "Table 10 note phrasing partially garbled ('all-d...'); confirm exact term against anchor."

VAR_56:
  name_as_printed: "discount rate news component of returns (equity discount rate news)"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3211
    section_or_table: "§VI.B text + Table 10 notes"
    paragraph_position: 1
    definition_verbatim: "for the discount rate news component of returns (from the decomposition of returns news into cash flow news and discount rate news components as in Vuolteenaho (2002))."
  data_source_or_formula: "Discount-rate-news residual from Campbell–Shiller (1988) / Vuolteenaho (2002) decomposition of firm equity returns. CRSP."
  unit_or_transformation: "news component (return units), firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Table 10 final pair of columns."
    panel: "N/A"
  uncertainty: "none"

VAR_57:
  name_as_printed: "first-moment instruments for USD–GBP exchange rate, price of oil, and Treasury rate (Alfaro et al. (2018))"
  role: "Control"
  raw_or_derived: "derived"
  primary_definition:
    page: 3200
    section_or_table: "Footnote 23 (main); IA Table C.7 notes"
    paragraph_position: "N/A (footnote)"
    definition_verbatim: "we include the firm-level first-moment instruments for the USD–GBP exchange rate, the price of oil, and the Treasury rate from alfaro2018. These variables jointly serve as proxies for changes in firms' expected profitability coinciding with the Brexit vote."
  data_source_or_formula: "Alfaro, Bloom, and Lin (2018) firm-level first-moment instruments for (i) USD–GBP exchange rate, (ii) price of oil, (iii) Treasury rate. Used in IA Table C.7 first-moment-controls robustness."
  unit_or_transformation: "firm-level instrument controls"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (as distribution)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "IA Table C.7 reports the augmented INVESTMENT/EMPLOYMENT_GROWTH DID coefficients with these instruments and lists control coefficients (SIZE, TOBIN_Q, CASH_FLOW, SALES_GROWTH, CONSENSUS_EARNINGS_FORECAST, STOCK_RETURNS)."
    panel: "N/A"
  uncertainty: "Citation rendered 'alfaro2018' (unresolved BibTeX key) in main-paper footnote 23; resolves to Alfaro, Bloom, and Lin (2018). Distinct from the GBP first-AND-second-moment set in Table 9 (VAR_50)."

VAR_58:
  name_as_printed: "AUTOMATION{i∈CZ} (AUTOMATION_{i∈CZ})"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3211
    section_or_table: "§VI.C text + Table 11 notes"
    paragraph_position: 1
    definition_verbatim: "We define our first, geography-based variable capturing firms' exposure to automation technologies, AUTOMATION{i∈CZ}, by matching each firm i in our sample to a CZ (based on the firm's headquarters location)."
  data_source_or_formula: "Acemoglu and Restrepo (2020) commuting-zone-level exposure to robots (robot-integrator data from Leigh and Kraft (2018)), assigned to firm i by HQ commuting zone. Table 11 notes: 'AUTOMATION{i∈CZ} is the Acemoglu and Restrepo (2020) commuting-zone-level exposure to robots for all firms i headquartered in commuting [zone].'"
  unit_or_transformation: "CZ-level exposure measure, firm-level (by HQ)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Used as control in Table 11; coefficients e.g. 0.029 (INVESTMENT col 1, n.s.), 0.261*** (R&D)."
    panel: "N/A"
  uncertainty: "Construction detailed in IA Appendix E.1 ¶1, which refers reader to Acemoglu and Restrepo (2020) and Leigh and Kraft (2018)."

VAR_59:
  name_as_printed: "AUTOMATIONi (AUTOMATION_i, text-based)"
  role: "Robustness"
  raw_or_derived: "derived"
  primary_definition:
    page: 3211
    section_or_table: "§VI.C text (full construction in IA Appendix E.1 ¶2)"
    paragraph_position: 2
    definition_verbatim: "We define AUTOMATIONi as a continuous variable that measures how frequently the top 100 automation keywords appear in each firm's business description (10-K Section 1) and management discussion (10-K Section 7). To capture cases in which a firm discusses automation efforts in only 1 year, we average the word count across the pre-Brexit years in our sample (2010–2015)."
  data_source_or_formula: "AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi); top-100 automation keywords from TextRank (Mihalcea and Tarau (2004)) on Benhabib (2003) textbook; counted in 10-K Sections 1 and 7; averaged over 2010–2015 (IA Appendix E.1 ¶2)."
  unit_or_transformation: "continuous, log scale; firm-level (time-averaged 2010–2015)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (numeric)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Distribution shown as histogram in Figure E.1 (IA p. 16); no numeric moments printed. Used as control in Table 11 (coefficients e.g. INVESTMENT 0.052 n.s.)."
    panel: "N/A"
  uncertainty: "Averaging window stated as '2010–2015' in main §VI.C and Figure E.1 caption, but 'all years in our sample' in IA E.1 ¶2 — confirm exact window."

VAR_60:
  name_as_printed: "AUTOMATION_KEYWORDSi"
  role: "Other: intermediate input to AUTOMATIONi"
  raw_or_derived: "derived"
  primary_definition:
    page: "IA p. 15"
    section_or_table: "IA Appendix E.1 ¶2"
    paragraph_position: 2
    definition_verbatim: "AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi), where AUTOMATION_KEYWORDSi is the number of mentions of the top 100 automation-related keywords in firm i's 10-K forms."
  data_source_or_formula: "Count of mentions of the top-100 automation keywords (Table E.1) in firm i's 10-K Sections 1 and 7."
  unit_or_transformation: "count, firm (per-year then averaged)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Keyword list = Table E.1 (IA p. 17); per audit rule, the 100 keywords are parameters, not separate variables."
    panel: "N/A"
  uncertainty: "none"

VAR_61:
  name_as_printed: "capital expenditures"
  role: "Other: raw input to derived DVs/controls"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within INVESTMENT definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "INVESTMENT is defined as capital expenditures divided by lagged total assets."
  data_source_or_formula: "Capital expenditures, COMPUSTAT Quarterly Fundamentals (item named in prose, not by code in the paper)."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (only the scaled ratio INVESTMENT is reported)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "Paper names raw items in prose; no COMPUSTAT item codes given."

VAR_62:
  name_as_printed: "lagged total assets / total assets"
  role: "Other: raw input (scaling denominator) / Sample-filter"
  raw_or_derived: "raw"
  primary_definition:
    page: 3192
    section_or_table: "§IV.B + Table 1 notes"
    paragraph_position: 1
    definition_verbatim: "We use COMPUSTAT Quarterly to gather basic information on firm investment and financial data. … we drop … companies whose market value or book assets are lower than $10 million."
  data_source_or_formula: "Total assets, COMPUSTAT. Used (lagged) as the denominator for INVESTMENT, R&D, DIVESTITURES, CASH, NWC, CASH_FLOW, and (logged) for SIZE; also a sample filter (<$10M dropped)."
  unit_or_transformation: "USD, firm-quarter (lagged for scaling; logged for SIZE)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (only logged form SIZE reported)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "See SIZE (VAR_40) for the logged distribution. Footnote 22: average assets of top-tercile β^UK firms = $2.81 billion in 2016:Q2."
    panel: "N/A"
  uncertainty: "Serves multiple roles (scaling, SIZE, sample filter)."

VAR_63:
  name_as_printed: "number of employees"
  role: "Other: raw input to EMPLOYMENT_GROWTH"
  raw_or_derived: "raw"
  primary_definition:
    page: 3192
    section_or_table: "§IV.B"
    paragraph_position: 2
    definition_verbatim: "Firm-level employment data are taken from COMPUSTAT's Annual Fundamentals. We measure employment growth based on the change in the number of employees of the firm."
  data_source_or_formula: "Number of employees, COMPUSTAT Annual Fundamentals (firm level); YTS for U.S. establishment-level employment."
  unit_or_transformation: "count, firm-year"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (only EMPLOYMENT_GROWTH reported)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Employment sample = 11,345 firm-years (p. 3192)."
    panel: "N/A"
  uncertainty: "none"

VAR_64:
  name_as_printed: "R&D expenditures"
  role: "Other: raw input to R&D ratio"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within R&D definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "R&D is defined as R&D expenditures divided by lagged total assets, considering only firms with non-missing R&D expenditures."
  data_source_or_formula: "R&D expenditures, COMPUSTAT."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (only scaled R&D reported)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_65:
  name_as_printed: "sale of plant, property, and equipment (SPP&E)"
  role: "Other: raw input to DIVESTITURES"
  raw_or_derived: "raw"
  primary_definition:
    page: 3202
    section_or_table: "Table 3 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "DIVESTITURES are defined as the value of SPP&E (Sale of Plant, Property, and Equipment) divided by lagged total assets."
  data_source_or_formula: "Value of sale of plant, property, and equipment, COMPUSTAT."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (only scaled DIVESTITURES)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_66:
  name_as_printed: "cash and short-term investments"
  role: "Other: raw input to CASH"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within CASH definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "CASH is defined as cash and short-term investments divided by lagged total assets."
  data_source_or_formula: "Cash and short-term investments, COMPUSTAT. (Table 8 uses 'total cash holdings' with a net-of-cash denominator — see VAR_05 conflict.)"
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (only scaled CASH)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_67:
  name_as_printed: "working capital (net of cash)"
  role: "Other: raw input to NWC"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within NWC definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "NON_CASH_WORKING_CAPITAL is defined as working capital (net of cash) divided by lagged total assets."
  data_source_or_formula: "Working capital net of cash, COMPUSTAT."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (only scaled NWC)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_68:
  name_as_printed: "operating income before depreciation"
  role: "Other: raw input to CASH_FLOW and PROFITS"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within CASH_FLOW definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "CASH_FLOW is defined as operating income before depreciation divided by lagged total assets."
  data_source_or_formula: "Operating income before depreciation, COMPUSTAT. Also numerator of PROFITS (over sales)."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_69:
  name_as_printed: "sales"
  role: "Other: raw input to SALES_GROWTH and PROFITS"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within SALES_GROWTH definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales."
  data_source_or_formula: "Quarterly sales, COMPUSTAT. Denominator of PROFITS; basis of SALES_GROWTH."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_70:
  name_as_printed: "market value of equity"
  role: "Other: raw input to TOBIN_Q (and SIZE / sample filter via market value)"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within TOBIN_Q definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "TOBIN_Q … is calculated as the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets."
  data_source_or_formula: "Market value of equity, CRSP/COMPUSTAT. Also used in $10M market-value sample filter (§IV.B)."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_71:
  name_as_printed: "book value of assets"
  role: "Other: raw input to TOBIN_Q"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within TOBIN_Q definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "TOBIN_Q is defined as the market value of assets divided by the book value of assets …"
  data_source_or_formula: "Book value of assets, COMPUSTAT. Denominator of TOBIN_Q."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "Likely the same item as 'total assets' (VAR_62); the paper names it 'book value of assets' only inside the TOBIN_Q formula — listed separately per rule 5."

VAR_72:
  name_as_printed: "book value of equity"
  role: "Other: raw input to TOBIN_Q"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within TOBIN_Q definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "… the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets."
  data_source_or_formula: "Book value of equity, COMPUSTAT."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_73:
  name_as_printed: "deferred taxes"
  role: "Other: raw input to TOBIN_Q"
  raw_or_derived: "raw"
  primary_definition:
    page: 3198
    section_or_table: "Table 1 notes (within TOBIN_Q definition)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "… minus book value of equity plus deferred taxes, all divided by book value of assets."
  data_source_or_formula: "Deferred taxes, COMPUSTAT."
  unit_or_transformation: "USD, firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_74:
  name_as_printed: "FTSE100 Index / vol(FTSE100_t)"
  role: "Other: raw input to β_i^UK (eq 13)"
  raw_or_derived: "raw"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.1 (equation (13) discussion)"
    paragraph_position: 1
    definition_verbatim: "It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting)."
  data_source_or_formula: "FTSE100 Index returns and their volatility, vol(FTSE100_t). Bloomberg equity index data. RHS regressor in eq (13)."
  unit_or_transformation: "index returns / return volatility, monthly (2010:M1–2014:M12)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (as summary stats)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Implied-volatility term structure plotted in Figure 3 (p. 3194)."
    panel: "N/A"
  uncertainty: "none"

VAR_75:
  name_as_printed: "S&P 500 Index / vol(SP500)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.1 (equation (13) controls)"
    paragraph_position: 1
    definition_verbatim: "We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound."
  data_source_or_formula: "S&P 500 Index return volatility, vol(SP500). Bloomberg/CRSP. Control in eq (13)."
  unit_or_transformation: "return volatility, monthly"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_76:
  name_as_printed: "USD/British pound FX rate / vol(FX$£)"
  role: "Control"
  raw_or_derived: "raw"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.1 (equation (13) controls)"
    paragraph_position: 1
    definition_verbatim: "We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) …"
  data_source_or_formula: "USD/GBP FX-rate changes and their volatility, vol(FX$£). Bloomberg currency data. Control in eq (13); FX-rate changes also used in the §VI.A dynamic levels regression."
  unit_or_transformation: "FX-rate change / volatility, monthly"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "Distinct use from the lagged USD/GBP level macro control (VAR_44)."

VAR_77:
  name_as_printed: "equity returns / vol(r_it)"
  role: "Other: raw input (LHS of eq 13)"
  raw_or_derived: "raw"
  primary_definition:
    page: 3191
    section_or_table: "§IV.A.1 (equation (13))"
    paragraph_position: 1
    definition_verbatim: "Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it)."
  data_source_or_formula: "Firm equity returns and their volatility, vol(r_it). CRSP. LHS of eq (13)."
  unit_or_transformation: "return / return volatility, monthly (firm-level)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Quarterly buy-and-hold version reported as STOCK_RETURNS (VAR_43)."
    panel: "N/A"
  uncertainty: "Related to but distinct from STOCK_RETURNS (quarterly buy-and-hold control, VAR_43)."

VAR_78:
  name_as_printed: "I/B/E/S 1-year-ahead EPS forecasts (mean and standard deviation)"
  role: "Other: raw input to forecast-uncertainty figures + CONSENSUS_EARNINGS_FORECAST"
  raw_or_derived: "raw"
  primary_definition:
    page: 3195
    section_or_table: "§IV.C.2 text"
    paragraph_position: 1
    definition_verbatim: "Beginning in 2015:Q1, we obtain the 1-year-ahead earnings per share (EPS) forecasts for each firm in our sample and compute the mean and standard deviation of forecasts."
  data_source_or_formula: "Analyst 1-year-ahead EPS forecasts (mean, SD, dispersion). I/B/E/S. Underlies Figure 4 forecast bands and CONSENSUS_EARNINGS_FORECAST (1-quarter-ahead, VAR_42)."
  unit_or_transformation: "EPS (USD), firm-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (as table); plotted in Figure 4 (p. 3195)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Figure 4 plots 1.5-SD bands around group-mean forecasts for high/low β^UK groups."
    panel: "N/A"
  uncertainty: "Figure 4 uses 1-year-ahead forecasts; the regression control (VAR_42) is the standardized 1-quarter-ahead consensus — two different horizons."

VAR_79:
  name_as_printed: "YTS establishment-level employment / establishment counts"
  role: "Other: raw input to establishment-level DVs"
  raw_or_derived: "raw"
  primary_definition:
    page: 3193
    section_or_table: "§IV.B text"
    paragraph_position: 1
    definition_verbatim: "The YTS database is compiled from historical business files from Infogroup and are linked longitudinally to track establishment location, employment, and sales information at the establishment-year level for public and private firms in the United States."
  data_source_or_formula: "Your-Economy Time-Series (YTS) database (Business Dynamics Research Consortium, U. Wisconsin); establishment-year location, employment, sales. Matched to sample firms via tickers + manual name searches."
  unit_or_transformation: "establishment-year (employment counts, establishment counts)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper (as moments)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Sample coverage: 757,083 unique establishments; 1,809,301 establishment-year observations (2010–2016); 51,750 U.S.-based subsidiaries; final U.S. establishment-level employment-growth sample 11,345 firm-years (pp. 3193, 3201)."
    panel: "N/A"
  uncertainty: "none"

VAR_80:
  name_as_printed: "establishment openings and closings"
  role: "Other: raw input to ESTABLISHMENT_TURNOVER"
  raw_or_derived: "raw"
  primary_definition:
    page: 3203
    section_or_table: "Footnote 24"
    paragraph_position: "N/A (footnote)"
    definition_verbatim: "Establishment turnover is defined as the sum of establishment openings and closings, divided by the lagged number of total establishments."
  data_source_or_formula: "Counts of U.S. establishment openings and closings per firm-year. YTS database."
  unit_or_transformation: "counts, firm-year"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_81:
  name_as_printed: "Hoberg and Moon (2017) Input and Output offshoring indices (raw counts)"
  role: "Other: raw input to U.K. offshoring treatment dummies"
  raw_or_derived: "raw"
  primary_definition:
    page: 3205
    section_or_table: "§V.B.2 text"
    paragraph_position: 1
    definition_verbatim: "This index, derived from firms' 10-K filings, counts mentions of words related to the purchase of inputs (\"Input\") and sale of outputs (\"Output\") from each country a firm does business with within a year."
  data_source_or_formula: "Hoberg and Moon (2017) Input and Output offshoring word-count indices, by country, per firm-year. Underlies VAR_25/26/27."
  unit_or_transformation: "word-count index, firm-year (summed 2010–2014 for U.K.)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_82:
  name_as_printed: "FIRM_i (firm-fixed effects)"
  role: "Fixed effect"
  raw_or_derived: "derived"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (equation (14) discussion)"
    paragraph_position: 1
    definition_verbatim: "FIRM_i represents firm-fixed effects, INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100), and QUARTER_t are calendar-quarter dummies."
  data_source_or_formula: "Firm dummies Σ_i FIRM_i in eq (14)."
  unit_or_transformation: "fixed-effect dummies, firm-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Marked 'Yes' in all baseline tables' Fixed effects rows."
    panel: "N/A"
  uncertainty: "none"

VAR_83:
  name_as_printed: "INDUSTRY_j (Hoberg and Phillips (2016) FIC 100)"
  role: "Fixed effect"
  raw_or_derived: "derived"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (equation (14) discussion)"
    paragraph_position: 1
    definition_verbatim: "INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100)"
  data_source_or_formula: "Hoberg and Phillips (2016) FIC 100 industry dummies (text-based network industries)."
  unit_or_transformation: "fixed-effect dummies, industry-level (FIC 100)"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Enters mainly via INDUSTRY×QUARTER interaction (VAR_85)."
    panel: "N/A"
  uncertainty: "none"

VAR_84:
  name_as_printed: "QUARTER_t (calendar-quarter dummies)"
  role: "Fixed effect"
  raw_or_derived: "derived"
  primary_definition:
    page: 3197
    section_or_table: "§IV.C.3 (equation (14) discussion)"
    paragraph_position: 1
    definition_verbatim: "QUARTER_t are calendar-quarter dummies."
  data_source_or_formula: "Calendar-quarter dummies."
  unit_or_transformation: "fixed-effect dummies, time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_85:
  name_as_printed: "INDUSTRY_j × QUARTER_t (Industry × time fixed effects)"
  role: "Fixed effect"
  raw_or_derived: "derived"
  primary_definition:
    page: 3196
    section_or_table: "equation (14)"
    paragraph_position: 1
    definition_verbatim: "Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}."
  data_source_or_formula: "Time-varying industry fixed effects = interaction of FIC-100 industry dummies with calendar-quarter dummies. Printed in tables as 'Industry × time'."
  unit_or_transformation: "interacted fixed-effect dummies, industry-quarter"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Marked 'Yes' in baseline (tercile / 10-K) specs; 'No' in macro-control linear specs (which use Firm FE only)."
    panel: "N/A"
  uncertainty: "none"

VAR_86:
  name_as_printed: "TIME (time fixed effects)"
  role: "Fixed effect"
  raw_or_derived: "derived"
  primary_definition:
    page: 3207
    section_or_table: "Table 7 Fixed-effects rows + Table 5 notes"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "NOT DEFINED IN TEXT — appears in Table 5 and Table 7 'Fixed effects' rows as separate 'Industry' and 'Time' entries (used in employment-growth specifications in place of Firm + Industry×time)."
  data_source_or_formula: "Time (calendar period) fixed effects, used together with standalone Industry FE in the employment-growth / labor-unionization specifications (e.g., Table 7 cols 4–6; Table 5 cols 5–8)."
  unit_or_transformation: "fixed-effect dummies, time-level"
  reported_summary_stats:
    found_in: "NOT REPORTED in the paper"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "Some employment specs replace Firm FE + Industry×time with Industry FE + Time FE (Table 7 rows)."
    panel: "N/A"
  uncertainty: "Distinct FE structure for annual employment specs vs quarterly investment specs; confirm exact FE set per column against anchor."

VAR_87:
  name_as_printed: "firm (standard-error cluster group)"
  role: "Standard error cluster group"
  raw_or_derived: "derived"
  primary_definition:
    page: 3200
    section_or_table: "Table 2 notes (recurring in all regression tables)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels."
  data_source_or_formula: "First clustering dimension (firm) for double-clustered robust standard errors."
  unit_or_transformation: "clustering dimension"
  reported_summary_stats:
    found_in: "N/A (not a measured variable)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

VAR_88:
  name_as_printed: "calendar quarter (standard-error cluster group)"
  role: "Standard error cluster group"
  raw_or_derived: "derived"
  primary_definition:
    page: 3200
    section_or_table: "Table 2 notes (recurring in all regression tables)"
    paragraph_position: "N/A for table-only"
    definition_verbatim: "T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels."
  data_source_or_formula: "Second clustering dimension (calendar quarter) for double-clustered robust standard errors."
  unit_or_transformation: "clustering dimension"
  reported_summary_stats:
    found_in: "N/A (not a measured variable)"
    N: "N/A"
    mean: "N/A"
    sd: "N/A"
    median: "N/A"
    p25: "N/A"
    p75: "N/A"
    other_stats: "N/A"
    panel: "N/A"
  uncertainty: "none"

TOTAL_VARIABLES_RETURNED: 88
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: "PDF-attached"
SUPPLEMENT_AVAILABLE: "yes"
TABLES_FOUND:
  - Table 1: 3198 (Panels A–C); 3199 (Panels D–E)
  - Table 2: 3200
  - Table 3: 3202
  - Table 4: 3203
  - Table 5: 3203
  - Table 6: 3206
  - Table 7: 3207
  - Table 8: 3208
  - Table 9: 3210 (printed body spans 3209–3210)
  - Table 10: 3212 (printed body spans 3211–3212)
  - Table 11: 3214 (printed body spans 3213–3214)
  - Table 12: 3215
  - Table 13: 3216
  - IA Table C.1: IA p. 7 (Sample Selection)
  - IA Table C.2: IA p. 6 (Summary Statistics: Matched Sample)
  - IA Table C.3: IA p. 8 (PSM results)
  - IA Table C.4: IA p. 9 (Parallel Trends: Market-Based)
  - IA Table C.5: IA p. 10 (Parallel Trends: Textual-Search-Based)
  - IA Table C.6: IA p. 11 (Cash Flow News Decomposition)
  - IA Table C.7: IA pp. 12–13 (First-Moment Controls; Panel A INVESTMENT / Panel B EMPLOYMENT_GROWTH)
  - IA Table E.1: IA p. 17 (List of Automation-Related Keywords — parameters, not variables)
  - IA Table E.2: IA p. 18 (Impact of Brexit Vote on Automation Exposure)

ACCESS_LIMITATIONS:
  supplement_access: "Full — Internet Appendix (Appendices A–E, Tables C.1–C.7, E.1–E.2, Figures C.1, D.1, E.1) is available and was used."
  cell_transcription_caveat: "Per the audit's feedback_no_llm_cell_transcription rule, all reported_summary_stats cell values above should be treated as provisional and verified against the PyMuPDF anchor extraction. The provided PDF text layer (i) strips leading minus signs from numeric cells, so signs on means/medians for variables that can go negative (CASH_FLOW, NWC, CONSENSUS_EARNINGS_FORECAST, STOCK_RETURNS, EMPLOYMENT_GROWTH) are unreliable here, and (ii) garbles multi-column table headers (notably Tables 5, 9, 10, 11, 12, which render as landscape blocks with collapsed column/coefficient alignment). Table 1 Panel A–E moments were the most cleanly recoverable and are reported in full."
  page_numbering_note: "Two page systems coexist: printed JFQA pages (3178–3222) and Internet Appendix internal pages (1–18). Main-paper variable locations use printed JFQA pages; IA variable locations are flagged 'IA p. N'."
```

