# Campello Variables — Round 1 Cross-Check

Generated: 2026-05-26 by `tmp/var_crosscheck_v1.py`
Sources: NLM (17 vars) + Claude-web (88 vars) responses in `process_prompt_03_variable_inventory_2026_05_26.md`
Anchor: programmatic PyMuPDF extraction of Table 1 (5 panels × 12 variables × 5 stats = 300 cells) in `campello_table1_anchor_2026_05_26.json`

## Summary

- Variables in **both AIs**: 8
- Variables only in **Claude-web**: 77
- Variables only in **NLM**: 9
- Variables with **Table 1 anchor**: 12 (the 12 Table 1 variables)

## Table 1 anchor cross-check (the 12 variables with Panel A reported moments)

For each Table 1 variable, compare AI's reported_summary_stats vs PyMuPDF anchor Panel A (universe).

| Variable | NLM (anchor match) | Claude-web (anchor match) | Anchor (Panel A, mean/SD/median/IQR/N) |
|---|---|---|---|
| **CASH** | ⚠ 0/4 match (VAR_03) | ✓ all match (VAR_05) | 0.22/0.25/0.12/0.27/78,044 |
| **CASH_FLOW** | ⚠ 0/4 match (VAR_07) | ✓ all match (VAR_39) | 0.01/0.06/0.03/0.04/75,287 |
| **CONSENSUS_EARNINGS_FORECAST** | _(not found)_ | ✓ all match (VAR_42) | 0.07/3.51/0.09/2.05/42,031 |
| **DIVESTITURES (100)** | _(not found)_ | ✓ all match (VAR_04) | 0.06/0.28/0.00/0.00/61,151 |
| **EMPLOYMENT_GROWTH (Annual)** | ⚠ 0/4 match (VAR_02) | ✓ all match (VAR_02) | 0.08/0.28/0.03/0.16/17,620 |
| **INVESTMENT** | ⚠ 0/4 match (VAR_01) | ✓ all match (VAR_01) | 0.01/0.02/0.01/0.01/76,094 |
| **NON_CASH_WORKING_CAPITAL** | _(not found)_ | ✓ all match (VAR_06) | 0.04/0.19/0.03/0.20/76,323 |
| **R&D** | _(not found)_ | ✓ all match (VAR_03) | 0.03/0.04/0.02/0.04/40,864 |
| **SALES_GROWTH** | _(not found)_ | ✓ all match (VAR_41) | 0.16/0.62/0.06/0.23/71,637 |
| **SIZE (Log Assets)** | ⚠ 0/4 match (VAR_06) | ✓ all match (VAR_40) | 6.19/2.08/6.15/3.08/78,062 |
| **STOCK_RETURNS** | _(not found)_ | ✓ all match (VAR_43) | 0.03/0.24/0.02/0.25/67,226 |
| **TOBIN_Q** | _(not found)_ | ✓ all match (VAR_38) | 2.11/1.59/1.57/1.26/73,353 |

## Table 1 anchor — detailed AI stat comparison

### CASH
  Anchor Panel A: mean=0.22, SD=0.25, median=0.12, IQR=0.27, N=78,044
  - NLM VAR_03: ⚠ 0/4 cell match  | found_in: Table 1, p. 3186
      - mismatch: mean: AI=0.220 | anchor=0.22
      - mismatch: SD: AI=0.250 | anchor=0.25
      - mismatch: median: AI=0.120 | anchor=0.12
      - mismatch: N: AI=48554 | anchor=78,044
  - Claude-web VAR_05: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### CASH_FLOW
  Anchor Panel A: mean=0.01, SD=0.06, median=0.03, IQR=0.04, N=75,287
  - NLM VAR_07: ⚠ 0/4 cell match  | found_in: Table 1, p. 3186
      - mismatch: mean: AI=0.010 | anchor=0.01
      - mismatch: SD: AI=0.040 | anchor=0.06
      - mismatch: median: AI=0.015 | anchor=0.03
      - mismatch: N: AI=48554 | anchor=75,287
  - Claude-web VAR_39: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### CONSENSUS_EARNINGS_FORECAST
  Anchor Panel A: mean=0.07, SD=3.51, median=0.09, IQR=2.05, N=42,031
  - NLM: _(variable not in inventory)_
  - Claude-web VAR_42: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### DIVESTITURES (100)
  Anchor Panel A: mean=0.06, SD=0.28, median=0.00, IQR=0.00, N=61,151
  - NLM: _(variable not in inventory)_
  - Claude-web VAR_04: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### EMPLOYMENT_GROWTH (Annual)
  Anchor Panel A: mean=0.08, SD=0.28, median=0.03, IQR=0.16, N=17,620
  - NLM VAR_02: ⚠ 0/4 cell match  | found_in: Table 1, p. 3186
      - mismatch: mean: AI=0.019 | anchor=0.08
      - mismatch: SD: AI=0.170 | anchor=0.28
      - mismatch: median: AI=0.013 | anchor=0.03
      - mismatch: N: AI=45781 | anchor=17,620
  - Claude-web VAR_02: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### INVESTMENT
  Anchor Panel A: mean=0.01, SD=0.02, median=0.01, IQR=0.01, N=76,094
  - NLM VAR_01: ⚠ 0/4 cell match  | found_in: Table 1, p. 3186
      - mismatch: mean: AI=0.012 | anchor=0.01
      - mismatch: SD: AI=0.016 | anchor=0.02
      - mismatch: median: AI=0.007 | anchor=0.01
      - mismatch: N: AI=48554 | anchor=76,094
  - Claude-web VAR_01: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### NON_CASH_WORKING_CAPITAL
  Anchor Panel A: mean=0.04, SD=0.19, median=0.03, IQR=0.20, N=76,323
  - NLM: _(variable not in inventory)_
  - Claude-web VAR_06: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### R&D
  Anchor Panel A: mean=0.03, SD=0.04, median=0.02, IQR=0.04, N=40,864
  - NLM: _(variable not in inventory)_
  - Claude-web VAR_03: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### SALES_GROWTH
  Anchor Panel A: mean=0.16, SD=0.62, median=0.06, IQR=0.23, N=71,637
  - NLM: _(variable not in inventory)_
  - Claude-web VAR_41: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### SIZE (Log Assets)
  Anchor Panel A: mean=6.19, SD=2.08, median=6.15, IQR=3.08, N=78,062
  - NLM VAR_06: ⚠ 0/4 cell match  | found_in: Table 1, p. 3186
      - mismatch: mean: AI=7.220 | anchor=6.19
      - mismatch: SD: AI=1.860 | anchor=2.08
      - mismatch: median: AI=7.170 | anchor=6.15
      - mismatch: N: AI=48554 | anchor=78,062
  - Claude-web VAR_40: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### STOCK_RETURNS
  Anchor Panel A: mean=0.03, SD=0.24, median=0.02, IQR=0.25, N=67,226
  - NLM: _(variable not in inventory)_
  - Claude-web VAR_43: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)

### TOBIN_Q
  Anchor Panel A: mean=2.11, SD=1.59, median=1.57, IQR=1.26, N=73,353
  - NLM: _(variable not in inventory)_
  - Claude-web VAR_38: ✓ 4/4 cell match  | found_in: Table 1, p. 3198 (Panels A–C); p. 3199 (Panels D–E)


## Claude-web-only variables (not in NLM, not in Table 1 anchor) — 70 variables

These are variables Claude-web caught but NLM missed (NLM enumerated only Table-1 vars + a few). Most are from Tables 2-12, IA Tables C.1-C.7, IA E.2, equation (14) controls, robustness specs.

- **Alfaro et al. (2018) GBP Instruments (first- and second-moment)** (CW VAR_50, role: Control)
- **asset redeployability index (Kim and Kung (2016)) / HIGH_INPUT_IRREVERSIBILITY (capital)** (CW VAR_28, role: Moderator)
- **AUTOMATION{i∈CZ} (AUTOMATION_{i∈CZ})** (CW VAR_58, role: Robustness)
- **AUTOMATIONi,t** (CW VAR_12, role: DV)
- **AUTOMATION_KEYWORDSi** (CW VAR_60, role: Other: intermediate input to AUTOMATIONi)
- **book value of assets** (CW VAR_71, role: Other: raw input to TOBIN_Q)
- **book value of equity** (CW VAR_72, role: Other: raw input to TOBIN_Q)
- **βBRAZIL_i (β_i^BRAZIL)** (CW VAR_24, role: Robustness)
- **calendar quarter (standard-error cluster group)** (CW VAR_88, role: Standard error cluster group)
- **capital expenditures** (CW VAR_61, role: Other: raw input to derived DVs/controls)
- **cash and short-term investments** (CW VAR_66, role: Other: raw input to CASH)
- **βCHINA_i (β_i^CHINA)** (CW VAR_20, role: Robustness)
- **deferred taxes** (CW VAR_73, role: Other: raw input to TOBIN_Q)
- **discount rate news component of returns (equity discount rate news)** (CW VAR_56, role: Control)
- **equity returns / vol(r_it)** (CW VAR_77, role: Other: raw input (LHS of eq 13))
- **ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH (column header: 'ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH')** (CW VAR_08, role: DV)
- **establishment openings and closings** (CW VAR_80, role: Other: raw input to ESTABLISHMENT_TURNOVER)
- **ESTABLISHMENT_TURNOVER** (CW VAR_09, role: DV)
- **βEU_i (β_i^EU)** (CW VAR_19, role: Robustness)
- **existing bond yields (yields to maturity on existing bonds)** (CW VAR_53, role: Control)
- **FIRM_i (firm-fixed effects)** (CW VAR_82, role: Fixed effect)
- **first-moment instruments for USD–GBP exchange rate, price of oil, and Treasury rate (Alfaro et al. (2018))** (CW VAR_57, role: Control)
- **FTSE100 Index / vol(FTSE100_t)** (CW VAR_74, role: Other: raw input to β_i^UK (eq 13))
- **FX hedging dummy (prior-year)** (CW VAR_51, role: Control)
- **FX hedging intensity (number of keywords)** (CW VAR_52, role: Control)
- **βFX£_i,t (β_i,t^FX£)** (CW VAR_49, role: Control)
- **HIGH_10K_ENTRIES (printed: 'HIGH_10K_ENTRIES' / 'Treatment is > 5 Brexit Entries in 10-Ks')** (CW VAR_16, role: Treatment)
- **HIGH_UK_EXPOSURE_i / HIGH_βUK_i** (CW VAR_14, role: Treatment)
- **Hoberg and Moon (2017) Input and Output offshoring indices (raw counts)** (CW VAR_81, role: Other: raw input to U.K. offshoring treatment dummies)
- **I/B/E/S 1-year-ahead EPS forecasts (mean and standard deviation)** (CW VAR_78, role: Other: raw input to forecast-uncertainty figures + CONSENSUS_EARNINGS_FORECAST)
- **βINDIA_i (β_i^INDIA)** (CW VAR_23, role: Robustness)
- **INDUSTRY_j (Hoberg and Phillips (2016) FIC 100)** (CW VAR_83, role: Fixed effect)
- **INDUSTRY_j × QUARTER_t (Industry × time fixed effects)** (CW VAR_85, role: Fixed effect)
- **βJAPAN_i (β_i^JAPAN)** (CW VAR_22, role: Robustness)
- **labor skills index (LSI) (Ghaly, Dang, and Stathopoulos (2017))** (CW VAR_30, role: Moderator)
- **labor unionization rate (BEA) / High labor irreversibility** (CW VAR_29, role: Moderator)
- **lagged Consumer Sentiment Index (University of Michigan)** (CW VAR_47, role: Control)
- **lagged Leading Economic Indicator (Federal Reserve Bank of Philadelphia)** (CW VAR_48, role: Control)
- **lagged mean GDP growth 1-year-ahead forecast (Livingstone Survey)** (CW VAR_46, role: Control)
- **lagged total assets / total assets** (CW VAR_62, role: Other: raw input (scaling denominator) / Sample-filter)
- **lagged U.S. dollar/British pound FX rate** (CW VAR_44, role: Control)
- **lagged VIX implied volatility index** (CW VAR_45, role: Control)
- **market value of equity** (CW VAR_70, role: Other: raw input to TOBIN_Q (and SIZE / sample filter via market value))
- **βMEXICO_i (β_i^MEXICO)** (CW VAR_21, role: Robustness)
- **new bond yields (yields on new bond issues)** (CW VAR_54, role: Control)
- **new syndicated loan spreads / markups (all-in spread)** (CW VAR_55, role: Control)
- **number of Brexit-related entries in 2015 10-K (count)** (CW VAR_15, role: Treatment)
- **number of employees** (CW VAR_63, role: Other: raw input to EMPLOYMENT_GROWTH)
- **operating income before depreciation** (CW VAR_68, role: Other: raw input to CASH_FLOW and PROFITS)
- **POST × HIGH_10K_ENTRIES** (CW VAR_33, role: Treatment)
- **POST × HIGH_βCOUNTRY_i  (POST·HIGH_β^COUNTRY)** (CW VAR_36, role: Robustness)
- **POST × HIGH_βUK_i  (POST·HIGH_β_i^UK)** (CW VAR_32, role: Treatment)
- **POST × HIGH_βUK_i,CF  (POST·HIGH_β_i,CF^UK)** (CW VAR_37, role: Robustness)
- **POST × HIGH_βUK_i × HIGH_INPUT_IRREVERSIBILITY (DIDID triple interaction)** (CW VAR_35, role: Moderator)
- **POST × HIGH_UK_OFFSHORING_INDEX** (CW VAR_34, role: Treatment)
- **POST_t × βUK_i  (POST·β_i^UK, linear continuous treatment)** (CW VAR_31, role: Treatment)
- **PROFITS** (CW VAR_07, role: DV)
- **QUARTER_t (calendar-quarter dummies)** (CW VAR_84, role: Fixed effect)
- **R&D expenditures** (CW VAR_64, role: Other: raw input to R&D ratio)
- **sale of plant, property, and equipment (SPP&E)** (CW VAR_65, role: Other: raw input to DIVESTITURES)
- **sales** (CW VAR_69, role: Other: raw input to SALES_GROWTH and PROFITS)
- **S&P 500 Index / vol(SP500)** (CW VAR_75, role: Control)
- **TIME (time fixed effects)** (CW VAR_86, role: Fixed effect)
- **βUK_i (β_i^UK)** (CW VAR_13, role: Treatment)
- **βUK_i,CF (β_i,CF^UK)** (CW VAR_18, role: Robustness)
- **U.K. Offshoring Index (Input Only)** (CW VAR_26, role: Treatment)
- **U.K. Offshoring Index (Input and Output / Total) — 'HIGH_UK_OFFSHORING_INDEX'** (CW VAR_25, role: Treatment)
- **USD/British pound FX rate / vol(FX$£)** (CW VAR_76, role: Control)
- **working capital (net of cash)** (CW VAR_67, role: Other: raw input to NWC)
- **YTS establishment-level employment / establishment counts** (CW VAR_79, role: Other: raw input to establishment-level DVs)