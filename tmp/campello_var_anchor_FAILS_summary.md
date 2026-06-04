# Aggregated FAIL / INCONCLUSIVE verdicts — 88-var anchor check

Source: `tmp/campello_var_anchor_check_batch_*.md`
**Totals**: 16 FAIL, 2 INCONCLUSIVE (of 88 vars)


### From `campello_var_anchor_check_batch_03.md`

## VAR_12 — AUTOMATIONi,t
- **role**: DV
- **claimed**: §Table E.2 notes, page IA p. 18 (Internet Appendix)
- **definition (first 200ch)**: The dependent variable is AUTOMATIONi,t, which is constructed from a dictionary of keywords that capture exposure to automation at the firm level, as described in Appendix E. This text-based continuou…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_03.md`

## VAR_14 — HIGH_UK_EXPOSURE_i / HIGH_βUK_i
- **role**: Treatment
- **claimed**: §§IV.C.3 text (equation (14) variable definitions), page 3196
- **definition (first 200ch)**: HIGH_UK_EXPOSURE_i is a dummy variable that equals 1 if firm i is U.K.-exposed, and 0 otherwise. A firm is considered to be U.K.-exposed according to two measures: i) if it belongs to the top tercile …
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_04.md`

## VAR_17 — POST_t
- **role**: Treatment
- **claimed**: §§IV.C.3 (equation (14) variable definitions), page 3196
- **definition (first 200ch)**: POST_t equals 1 if the time period is in the 2016:Q3–Q4 window.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_07.md`

## VAR_32 — POST × HIGH_βUK_i  (POST·HIGH_β_i^UK)
- **role**: Treatment
- **claimed**: §equation (14), §IV.C.3, page 3196
- **definition (first 200ch)**: Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_07.md`

## VAR_33 — POST × HIGH_10K_ENTRIES
- **role**: Treatment
- **claimed**: §equation (14), §IV.C.3, page 3196
- **definition (first 200ch)**: Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_08.md`

## VAR_37 — POST × HIGH_βUK_i,CF  (POST·HIGH_β_i,CF^UK)
- **role**: Robustness
- **claimed**: §Table C.6 (row header + notes), page IA p. 11
- **definition (first 200ch)**: The treatment group is composed by the top tercile of β^UK_i,CF, while the control group is composed by firms in the bottom tercile of β^UK_i,CF.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p23 (printed p3200)
- **CHECK 2 — page match**: `MISMATCH` — claimed=IA p. 11, found=p3200
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **FAIL (page mismatch)**

### From `campello_var_anchor_check_batch_09.md`

## VAR_43 — STOCK_RETURNS (lagged stock returns)
- **role**: Control
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: STOCK_RETURNS are defined as the quarterly buy-and-hold return.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NAME_MISMATCH` — normalized=STOCKRETURNSLAGGEDSTOCKRETURNS, no anchor variant matched
- **VERDICT**: **INCONCLUSIVE**

### From `campello_var_anchor_check_batch_14.md`

## VAR_70 — market value of equity
- **role**: Other: raw input to TOBIN_Q (and SIZE / sample filter via market value)
- **claimed**: §Table 1 notes (within TOBIN_Q definition), page 3198
- **definition (first 200ch)**: TOBIN_Q … is calculated as the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## Batch summary
- PASS: 4
- FAIL: 1
- INCONCLUSIVE: 0
- OTHER: 0

### From `campello_var_anchor_check_batch_15.md`

## VAR_72 — book value of equity
- **role**: Other: raw input to TOBIN_Q
- **claimed**: §Table 1 notes (within TOBIN_Q definition), page 3198
- **definition (first 200ch)**: … the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_15.md`

## VAR_73 — deferred taxes
- **role**: Other: raw input to TOBIN_Q
- **claimed**: §Table 1 notes (within TOBIN_Q definition), page 3198
- **definition (first 200ch)**: … minus book value of equity plus deferred taxes, all divided by book value of assets.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_15.md`

## VAR_75 — S&P 500 Index / vol(SP500)
- **role**: Control
- **claimed**: §§IV.A.1 (equation (13) controls), page 3191
- **definition (first 200ch)**: We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluc…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## Batch summary
- PASS: 2
- FAIL: 3
- INCONCLUSIVE: 0
- OTHER: 0

### From `campello_var_anchor_check_batch_16.md`

## VAR_76 — USD/British pound FX rate / vol(FX$£)
- **role**: Control
- **claimed**: §§IV.A.1 (equation (13) controls), page 3191
- **definition (first 200ch)**: We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) ……
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_16.md`

## VAR_78 — I/B/E/S 1-year-ahead EPS forecasts (mean and standard deviation)
- **role**: Other: raw input to forecast-uncertainty figures + CONSENSUS_EARNINGS_FORECAST
- **claimed**: §§IV.C.2 text, page 3195
- **definition (first 200ch)**: Beginning in 2015:Q1, we obtain the 1-year-ahead earnings per share (EPS) forecasts for each firm in our sample and compute the mean and standard deviation of forecasts.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (as table); plotted in Figure 4 (p. 3195)
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_17.md`

## VAR_82 — FIRM_i (firm-fixed effects)
- **role**: Fixed effect
- **claimed**: §§IV.C.3 (equation (14) discussion), page 3197
- **definition (first 200ch)**: FIRM_i represents firm-fixed effects, INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100), and QUARTER_t are calendar-quarter dummies.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_17.md`

## VAR_83 — INDUSTRY_j (Hoberg and Phillips (2016) FIC 100)
- **role**: Fixed effect
- **claimed**: §§IV.C.3 (equation (14) discussion), page 3197
- **definition (first 200ch)**: INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100)…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_17.md`

## VAR_84 — QUARTER_t (calendar-quarter dummies)
- **role**: Fixed effect
- **claimed**: §§IV.C.3 (equation (14) discussion), page 3197
- **definition (first 200ch)**: QUARTER_t are calendar-quarter dummies.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

### From `campello_var_anchor_check_batch_17.md`

## VAR_85 — INDUSTRY_j × QUARTER_t (Industry × time fixed effects)
- **role**: Fixed effect
- **claimed**: §equation (14), page 3196
- **definition (first 200ch)**: Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## Batch summary
- PASS: 1
- FAIL: 4
- INCONCLUSIVE: 0
- OTHER: 0

### From `campello_var_anchor_check_batch_18.md`

## VAR_86 — TIME (time fixed effects)
- **role**: Fixed effect
- **claimed**: §Table 7 Fixed-effects rows + Table 5 notes, page 3207
- **definition (first 200ch)**: NOT DEFINED IN TEXT — appears in Table 5 and Table 7 'Fixed effects' rows as separate 'Industry' and 'Time' entries (used in employment-growth specifications in place of Firm + Industry×time).…
- **CHECK 1 — definition in paper**: `N/A` — no definition text to check
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **INCONCLUSIVE**
