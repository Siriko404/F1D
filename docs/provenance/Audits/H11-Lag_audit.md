# ADVERSARIAL AUDIT: H11-Lag Provenance Document

**Audit Date:** 2026-03-30
**Auditor:** Hostile adversarial audit per docs/Prompts/Audit Provenance doc.txt
**Suite:** H11-Lag
**Runner:** `src/f1d/econometric/run_h11_prisk_uncertainty_lag.py`
**Panel Builder:** `src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py`
**Provenance Doc:** `docs/provenance/H11-Lag.md`
**Creation Prompt:** `docs/Prompts/Suite Provenance Doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 27 | 26 | 1 | 96.3% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100.0% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100.0% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100.0% |
| Sample Construction (Phase 5) | 3 | 2 | 1 | 66.7% |
| Variable Dictionary (Phase 6) | 18 | 18 | 0 | 100.0% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 8 | 1 | 88.9% |
| Table Generator Entry (Phase 8) | 5 | 5 | 0 | 100.0% |
| Model-Family Addendum (Phase 9) | 5 | 5 | 0 | 100.0% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90.0% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100.0% |
| **TOTAL** | **107** | **103** | **4** | **96.3%** |

---

## VERDICT

**PASS WITH NOTES**: The provenance document is substantially accurate and complete. Four minor issues were found, none of which affect the correctness of the model specification, variable dictionary, or regression logic. All are documentation precision issues (wrong column count in F1, missing row counts in the attrition cascade).

---

## PHASE 1: STRUCTURAL COMPLETENESS

Requirement: Every section (A through L) required by the creation prompt must exist in the provenance doc.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | All YAML fields present |
| B. Model Specification | Yes | Yes | Yes | |
| B1. Regression Equation | Yes | Yes | Yes | Two equations given (QA / Pres) |
| B2. Dependent Variable(s) | Yes | Yes | Yes | 4 DVs tabulated |
| B3. Independent Variable(s) | Yes | Yes | Yes | 2 IVs tabulated |
| B4. Control Variables | Yes | Yes | Yes | Base + dynamic control map |
| B5. Fixed Effects | Yes | Yes | Yes | |
| B6. Standard Errors | Yes | Yes | Yes | |
| B7. Hypothesis Test | Yes | Yes | Yes | |
| C. Spec Register | Yes | Yes | Yes | 8-row table |
| D. Sample Construction | Yes | Yes | Partial | D2 attrition table lacks "Rows Before/After/Dropped" numeric columns -- see Phase 5 |
| D1. Population | Yes | Yes | Yes | |
| D2. Exclusion Criteria | Yes | Yes | Partial | Steps are listed but no actual row counts |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Notes runtime-dependent N |
| E. Variable Dictionary | Yes | Yes | Yes | 17 variables tabulated |
| F. Data Pipeline | Yes | Yes | Yes | |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | |
| F3. Merge Operations | Yes | Yes | Yes | 17 merge rows |
| G. Outputs | Yes | Yes | Yes | |
| G1. Stage 3 Outputs | Yes | Yes | Yes | |
| G2. Stage 4 Outputs | Yes | Yes | Yes | |
| G3. Summary Statistics | Yes | Yes | Yes | |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | |
| I. generate_all_tables Entry | Yes | Yes | Yes | Full Python dict + verification table |
| J. Reproduction Commands | Yes | Yes | Yes | |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled; K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 7 issues documented |

**Phase 1 Result:** 26 PASS, 1 FAIL (D2 attrition table lacks the required "Rows Before / Rows After / Dropped" numeric columns per the creation prompt template).

---

## PHASE 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

**A-1. Suite ID: `H11-Lag`**
- Provenance doc: "H11-Lag"
- Runner docstring (line 6): `econometric/test_h11_prisk_uncertainty_lag`; generate_all_tables.py line 220: `"id": "H11-Lag"`
- **PASS**

**A-2. Title: `H11-Lag: Lagged Political Risk and Language Uncertainty`**
- Runner line 4: "STAGE 4: Test H11-Lag Political Risk (Lagged) - Language Uncertainty Hypothesis"
- generate_all_tables.py line 223: `"caption": "H11-Lag: Lagged Political Risk and Language Uncertainty"`
- The provenance doc title matches the generate_all_tables caption. The runner's title is slightly different ("Test H11-Lag Political Risk (Lagged) - Language Uncertainty Hypothesis") but the doc uses the table caption, which is reasonable.
- **PASS**

**A-3. Hypothesis**
- Provenance doc: "Higher political risk in quarter t-1 (and t-2) is associated with higher language uncertainty in subsequent earnings calls. Lagged variant of H11 to establish temporal ordering."
- Runner docstring lines 33--34: "beta(PRiskQ_lag) > 0 -- higher prior-quarter political risk increases speech uncertainty" and "beta(PRiskQ_lag2) > 0 -- higher 2-quarter prior political risk increases speech uncertainty"
- These are consistent. **PASS**

**A-4. Direction: `One-tailed (beta > 0)`**
- Runner line 219: "# Hypothesis test: beta > 0 (one-tailed)"
- Runner line 221: `p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2`
- Runner line 225: `h_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0`
- generate_all_tables.py line 246: `"key_tails": ["one_pos", "one_pos"]`
- **PASS**

**A-5. Model Family: `Linear panel regression with absorbed fixed effects`**
- Runner line 76: `from linearmodels.panel import PanelOLS`
- Runner line 203: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`
- This is PanelOLS with absorbed EntityEffects + TimeEffects. Description is accurate.
- **PASS**

**A-6. Estimator: `linearmodels.panel.PanelOLS`**
- Runner line 76: `from linearmodels.panel import PanelOLS`
- **PASS**

**A-7. Unit of Obs: `Individual earnings call (file_name)`**
- Panel builder: each row in the manifest corresponds to one file_name (one call). All merges are on file_name with zero row-delta enforcement (lines 142--147).
- **PASS**

**A-8. Panel Index: `(gvkey, year) -- year = calendar year from start_date`**
- Runner line 200: `df_panel = df_sample.set_index(["gvkey", "year"])`
- Panel builder line 151: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year`
- **PASS**

**A-9. Columns: `8 (in generate_all_tables.py); runner also produces Finance and Utility sub-sample regressions (24 total regressions)`**
- generate_all_tables.py line 225: `"cols": 8`
- Runner loop: 4 DVs x 2 IVs x 3 samples = 24 regressions maximum. Published table = 8 (Main sample, 4 DVs x 2 IVs).
- However, the provenance doc then says "selecting 17 specific columns (lines 448--472)" in Section F1. Actual column count in the read_parquet call (lines 448--471) is **19 columns**: file_name, gvkey, year, ff12_code, Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, PRiskQ_lag, PRiskQ_lag2, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct, Size, TobinsQ, ROA, CashHoldings, DividendPayer, firm_maturity, earnings_volatility.
- The "8 columns" for the published table is correct. The "17 specific columns" sub-claim in Section F1 is wrong (should be 19). This is a Section F error but relates to the accuracy of A-9's scope.
- **PASS** for A-9 itself (the "8 columns" claim is correct). The "17 columns" error is flagged in Phase 7.

**A-10. Runner and Panel Builder paths**
- `src/f1d/econometric/run_h11_prisk_uncertainty_lag.py` -- verified exists on disk.
- `src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py` -- verified exists on disk.
- **PASS**

**Phase 2 Result:** 10 checks, 10 PASS. (The "17 columns" sub-claim in Section F1 is scored in Phase 7, not here.)

---

## PHASE 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

**B1-CHECK: Regression Equation**

Provenance doc shows two equation forms:
- QA DVs: `DV = beta*IV + gamma1*Presentation_control + gamma2*Analyst_QA_Uncertainty_pct + gamma*X + alpha_i + delta_t + epsilon`
- Pres DVs: `DV = beta*IV + gamma1*Analyst_QA_Uncertainty_pct + gamma*X + alpha_i + delta_t + epsilon`

Runner lines 184--188:
```python
formula = f"{dv_var} ~ 1 + {iv_var} + " + " + ".join(controls) + " + EntityEffects + TimeEffects"
```

Where `controls` = BASE_CONTROLS + optional pres_control (lines 161--164).

For QA DVs: controls = 9 base + 1 pres control = 10 controls total.
For Pres DVs: controls = 9 base controls.

The equation correctly distinguishes QA vs Pres DVs. The Analyst_QA_Uncertainty_pct is within BASE_CONTROLS (line 101), so it's always included, consistent with the equation.

Note: The formula includes an explicit intercept (`~ 1 +`), which the provenance equation doesn't show explicitly. But since PanelOLS with EntityEffects absorbs the intercept, this is absorbed and irrelevant.

**PASS**

**B2-CHECK: Dependent Variables**

Provenance doc lists 4 DVs: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct.

Runner CONFIG lines 90--95: exact same 4 DVs.

Formula: "(LM uncertainty word count / total words) * 100" -- verified in `build_linguistic_variables.py` line 496: `pct = (sums[col] / total_tokens) * 100.0`

Source: LinguisticEngine -- verified (linguistic variable builders use LinguisticEngine).

Timing: Contemporaneous (call-level) -- correct, these are computed from the call transcript itself.

**PASS**

**B3-CHECK: Independent Variables**

Provenance doc lists 2 IVs: PRiskQ_lag, PRiskQ_lag2.

Runner line 97: `"iv_vars": ["PRiskQ_lag", "PRiskQ_lag2"]`

PRiskQ_lag formula: PRisk from Hassan (2019) for quarter Q-1 matched via (gvkey, cal_q_lag). Verified in `prisk_q_lag.py` lines 156 (cal_q_lag computation), 169--175 (merge on gvkey + cal_q_lag).

PRiskQ_lag2 formula: PRisk for quarter Q-2 matched via (gvkey, cal_q_lag2). Verified in `prisk_q_lag2.py` lines 159 (cal_q_lag2 computation), 172--178 (merge on gvkey + cal_q_lag2).

Source: `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (TAB-separated). Confirmed in both builder files, line 40: `PRISK_FILE = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"`.

Timing: Lag t-1 and t-2 respectively. Verified.

**PASS**

**B4-CHECK: Control Variables**

Provenance doc lists 9 base controls:
1. Analyst_QA_Uncertainty_pct
2. Entire_All_Negative_pct
3. Size
4. TobinsQ
5. ROA
6. CashHoldings
7. DividendPayer
8. firm_maturity
9. earnings_volatility

Runner BASE_CONTROLS lines 100--110: exact same 9 controls in the same order.

Dynamic Presentation Control: PRES_CONTROL_MAP at lines 112--117 adds Manager_Pres_Uncertainty_pct for Manager_QA DV and CEO_Pres_Uncertainty_pct for CEO_QA DV; no addition for Pres DVs. Verified.

No Lagged_DV: The provenance doc states "This suite does not include a lagged dependent variable control." Verified: no Lagged_DV in BASE_CONTROLS, no lag_dv construction anywhere in runner or builder. **PASS** but noted: the creation prompt says "Include Lagged_DV and specify exactly what it lags." The provenance doc explicitly states the absence, which is the correct way to handle a missing Lagged_DV.

**PASS**

**B5-CHECK: Fixed Effects**

Provenance doc: Entity = gvkey (firm FE, absorbed), Time = year (calendar year FE, absorbed).

Runner line 187: `+ " + EntityEffects + TimeEffects"`
Runner line 200: `df_panel = df_sample.set_index(["gvkey", "year"])`
Runner line 203: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`

PanelOLS MultiIndex: first level = gvkey (entity), second level = year (time). EntityEffects absorbs gvkey FE, TimeEffects absorbs year FE.

Panel builder line 151: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year` -- confirms year = calendar year from start_date.

**PASS**

**B6-CHECK: Standard Errors**

Provenance doc: cov_type="clustered", cluster_entity=True (firm-level clustering).

Runner line 204: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)`

**PASS**

**B7-CHECK: Hypothesis Test**

Provenance doc: One-tailed beta > 0; p_two / 2 if beta > 0; 1 - p_two/2 if beta < 0; significance at *** p<0.01, ** p<0.05, * p<0.10; hypothesis confirmed at p_one < 0.05 AND beta > 0.

Runner lines 220--225:
```python
if not np.isnan(p_two) and not np.isnan(beta_prisk):
    p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2
else:
    p_one = np.nan
h_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0
```

Runner fmt_coef function lines 287--292:
```python
if pval < 0.01: stars = "^{***}"
elif pval < 0.05: stars = "^{**}"
elif pval < 0.10: stars = "^{*}"
```

All confirmed. **PASS**

**Phase 3 Result:** 7 checks, 7 PASS.

---

## PHASE 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

The provenance doc shows an 8-row spec register table.

**Row count check:** 8 rows in table. generate_all_tables.py `"cols": 8`. Runner produces 4 DVs x 2 IVs x 3 samples = 24 regressions, but only the 8 Main-sample results are in the published table. **PASS**

**Per-row verification:**

| Col | Doc DV | Actual DV | Doc IV | Actual IV | Doc Entity FE | Actual | Doc Time FE | Actual | Doc Controls | Actual |
|-----|--------|-----------|--------|-----------|---------------|--------|-------------|--------|-------------|--------|
| 1 | Manager_QA_Uncertainty_pct | Manager_QA_Uncertainty_pct | PRiskQ_lag | PRiskQ_lag | Firm | Firm | Cal Year | Cal Year | Base + Mgr_Pres | Base + Mgr_Pres | PASS |
| 2 | CEO_QA_Uncertainty_pct | CEO_QA_Uncertainty_pct | PRiskQ_lag | PRiskQ_lag | Firm | Firm | Cal Year | Cal Year | Base + CEO_Pres | Base + CEO_Pres | PASS |
| 3 | Manager_Pres_Uncertainty_pct | Manager_Pres_Uncertainty_pct | PRiskQ_lag | PRiskQ_lag | Firm | Firm | Cal Year | Cal Year | Base only | Base only | PASS |
| 4 | CEO_Pres_Uncertainty_pct | CEO_Pres_Uncertainty_pct | PRiskQ_lag | PRiskQ_lag | Firm | Firm | Cal Year | Cal Year | Base only | Base only | PASS |
| 5 | Manager_QA_Uncertainty_pct | Manager_QA_Uncertainty_pct | PRiskQ_lag2 | PRiskQ_lag2 | Firm | Firm | Cal Year | Cal Year | Base + Mgr_Pres | Base + Mgr_Pres | PASS |
| 6 | CEO_QA_Uncertainty_pct | CEO_QA_Uncertainty_pct | PRiskQ_lag2 | PRiskQ_lag2 | Firm | Firm | Cal Year | Cal Year | Base + CEO_Pres | Base + CEO_Pres | PASS |
| 7 | Manager_Pres_Uncertainty_pct | Manager_Pres_Uncertainty_pct | PRiskQ_lag2 | PRiskQ_lag2 | Firm | Firm | Cal Year | Cal Year | Base only | Base only | PASS |
| 8 | CEO_Pres_Uncertainty_pct | CEO_Pres_Uncertainty_pct | PRiskQ_lag2 | PRiskQ_lag2 | Firm | Firm | Cal Year | Cal Year | Base only | Base only | PASS |

The column order matches the generate_all_tables.py col_files mapping (lag1 cols 1-4, lag2 cols 5-8).

Verification of ordering against the runner loop: The runner iterates `for iv_var in CONFIG["iv_vars"]` (PRiskQ_lag first, then PRiskQ_lag2), then `for dv in CONFIG["dependent_variables"]` (Manager_QA, CEO_QA, Manager_Pres, CEO_Pres), then `for sample in CONFIG["samples"]`. The col_files in generate_all_tables.py map Main sample results in the exact (IV, DV) order: lag1 x [MgrQA, CEOQA, MgrPres, CEOPres], then lag2 x same.

**No missing specs.** **No extra specs.**

**Phase 4 Result:** 5 checks, 5 PASS.

---

## PHASE 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

**D1-CHECK: Population**

Provenance doc: Starting dataset = `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`, 112,968 calls, ~2,429 firms, 2002--2018.

Runner line 431--435: loads from `outputs/variables/h11_prisk_uncertainty_lag/latest/h11_prisk_uncertainty_lag_panel.parquet` (which was built from the manifest).

Project scope (per MEMORY.md): 112,968 calls, 2,429 firms, 2002--2018. Consistent. **PASS**

**D2-CHECK: Exclusion Criteria**

Provenance doc lists 6 filter steps:
1. Full manifest -- correct, panel loaded from parquet
2. Industry sample assignment -- verified: panel builder line 150 (`assign_industry_sample`), runner line 477
3. Sample selection -- verified: runner lines 519--524 (filter to sample)
4. Complete case -- verified: runner line 172 (`replace([inf, -inf], NaN).dropna(subset=required)`)
5. Min calls per firm -- verified: runner lines 526--531 (gvkey_count >= 5)
6. Minimum rows check -- verified: runner line 537 (`if len(df_filtered) < 100: ... skip`)

**However:** The creation prompt's template specifies an attrition cascade with columns "Rows Before | Rows After | Dropped". The provenance doc's D2 table only has "Step | Filter | Description" columns with no numeric row counts. The provenance doc acknowledges this at the bottom: "The exact row counts per step depend on runtime data and vary by DV." The runner's attrition table (lines 564--568) only records 3 stages, confirming that detailed per-step counts are not available without runtime data.

This is a structural deficiency vs. the creation prompt specification. The prompt says the attrition cascade must have row counts. The doc acknowledges they're runtime-dependent but provides no numbers. **FAIL** -- incomplete per the specification.

**D3-CHECK: Sample Counts per Specification**

Provenance doc: "N varies across model specs due to: Different DVs having different missingness patterns, QA specs include an extra Presentation control, PRiskQ_lag vs PRiskQ_lag2 have different coverage." This is logically correct and documented at a reasonable level. Runtime counts are referenced as being in model_diagnostics.csv.

**PASS**

**Phase 5 Result:** 3 checks, 2 PASS, 1 FAIL (D2 lacks numeric row counts).

---

## PHASE 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

Checking each variable:

**1. Manager_QA_Uncertainty_pct**
- Name: matches code. Formula: (LM uncertainty count / total words) * 100 for managers in Q&A. Verified: `build_linguistic_variables.py` line 496 does `pct = (sums[col] / total_tokens) * 100.0`. Source: LinguisticEngine. Winsorization: 0%/99% upper-only per year. Verified: `_linguistic_engine.py` line 257 (`lower=0.0, upper=0.99`). **PASS**

**2. CEO_QA_Uncertainty_pct**
- Same structure as above, for CEO in Q&A. **PASS**

**3. Manager_Pres_Uncertainty_pct**
- Same structure, for managers in presentation. Type = DV / Control (dual role documented). **PASS**

**4. CEO_Pres_Uncertainty_pct**
- Same structure, for CEO in presentation. Type = DV / Control. **PASS**

**5. PRiskQ_lag**
- Name: matches code. Formula: PRisk from Hassan (2019) for cal quarter Q-1. Source: PRiskQLagBuilder from `firmquarter_2022q1.csv`. Winsorization: "1%/99% per-year (builder level)". Verified: `prisk_q_lag.py` line 165: `prisk_df = winsorize_by_year(prisk_df, ["PRisk"], year_col="year")`. The `winsorize_by_year` defaults are `lower=0.01, upper=0.99`. **PASS**

**6. PRiskQ_lag2**
- Same as above with Q-2 lag. `prisk_q_lag2.py` line 168: same winsorization call. **PASS**

**7. Analyst_QA_Uncertainty_pct**
- Control. Same formula pattern as DV uncertainty variables. Source: LinguisticEngine. **PASS**

**8. Entire_All_Negative_pct**
- Control. Formula: (LM negative count / total words) * 100 for entire call. Source: LinguisticEngine. Same winsorization (0%/99%). **PASS**

**9. Size**
- Formula in doc: "ln(atq) where atq > 0; else NaN". Code: `_compustat_engine.py` line 938: `comp["Size"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)`. Match. Source: CompustatEngine. Winsorization: "1%/99% per fiscal year (engine level)". Verified: winsorize_cols loop at `_compustat_engine.py` lines 1129--1136, using `fyearq` as year_col. **PASS**

**10. TobinsQ**
- Formula in doc: "(cshoq * prccq + debt_book) / atq". Code: `_compustat_engine.py` lines 982--992:
  ```python
  mktcap = comp["cshoq"] * comp["prccq"]
  debt_c = comp["dlcq"].clip(lower=0).fillna(0)
  debt_t = comp["dlttq"].clip(lower=0).fillna(0)
  debt_book = np.where(comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t)
  comp["TobinsQ"] = np.where(comp["atq"].notna() & (comp["atq"] > 0) & mktcap.notna(), (mktcap + debt_book) / comp["atq"], np.nan)
  ```
  The provenance doc's formula "(cshoq * prccq + dlcq + dlttq) / atq" in the B4 table simplifies the actual logic: the code clips negative debt to 0, uses fillna(0), and checks for both components being NaN. The doc's shorthand is a reasonable approximation.
  **PASS** (with note: the doc simplifies the null-handling logic)

**11. ROA**
- Formula in doc: "iby_annual / avg_assets, where avg_assets = (atq_t + atq_{t-1}) / 2". Code: `_compustat_engine.py` lines 954--964:
  ```python
  atq_annual = _compute_annual_q4_variable(comp, "atq", "_atq_annual")
  atq_annual_lag1 = _compute_annual_q4_variable_lag(comp, "atq", "_atq_annual_lag1")
  avg_assets = (pd.Series(atq_annual, ...) + pd.Series(atq_annual_lag1, ...)) / 2
  iby_annual = _compute_annual_q4_variable(comp, "iby", "_iby_annual")
  comp["ROA"] = np.where(avg_assets > 0, pd.Series(iby_annual, ...) / avg_assets, np.nan)
  ```
  The doc says "iby_annual (Q4 value)" which is correct -- `_compute_annual_q4_variable` extracts the Q4 observation and joins it back. The formula is correct.
  However, the provenance doc B4 table says "iby_annual / avg_assets" -- in the variable dictionary (Section E), it says "iby_annual (Q4 value) / avg_assets, where avg_assets = (atq_t + atq_{t-1}) / 2". This is accurate.
  **PASS**

**12. CashHoldings**
- Formula in doc: "cheq / atq". Code: `_compustat_engine.py` line 981: `comp["CashHoldings"] = comp["cheq"] / comp["atq"]`. Match. **PASS**

**13. DividendPayer**
- Formula in doc: "1 if dvy_annual > 0, else 0". Code: `_compustat_engine.py` lines 1004--1007:
  ```python
  dvy_annual = _compute_annual_q4_variable(comp, "dvy", "_dvy_annual")
  comp["DividendPayer"] = (pd.Series(dvy_annual, ...).fillna(0) > 0).astype(float)
  ```
  Doc says "1 if dvy_annual (Q4 cumulative) > 0, else 0". Code uses Q4 annual dvy. Match.
  Winsorization: "No (binary variable, skip_winsorize)". Verified: `skip_winsorize` set at line 1123 includes `"DividendPayer"`. **PASS**

**14. firm_maturity**
- Formula in doc: "req / atq (retained earnings / total assets)". Code: `_compustat_engine.py` lines 802--804:
  ```python
  df["firm_maturity"] = np.where((df["atq"].notna()) & (df["atq"] > 0), df["req"] / df["atq"], np.nan)
  ```
  Match. **PASS**

**15. earnings_volatility**
- Formula in doc: "rolling std(iby/atq) over trailing 1826 days (~5 years), min 3 obs". Code: `_compustat_engine.py` lines 807--819:
  ```python
  df["roa_annual"] = np.where((df["atq"].notna()) & (df["atq"] > 0), df["iby"] / df["atq"], np.nan)
  ...
  earn_vol = df_ts.groupby("gvkey")["roa_annual"].rolling("1826D", min_periods=3).std()
  ```
  Match. Note: the rolling window uses a dummy_date built from fyearq (not calendar date), so "1826 days" is effectively "5 fiscal years" since each annual observation is spaced ~365 days apart. **PASS**

**16. gvkey** (FE column)
- Type: FE (Entity). Source: Manifest. **PASS**

**17. year** (FE column)
- Formula in doc: "start_date.dt.year". Code: builder line 151: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year`. Match. **PASS**

**Completeness check:**

Variables in runner MODEL_SPECS / formulas:
- DVs: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct (4) -- all in dictionary
- IVs: PRiskQ_lag, PRiskQ_lag2 (2) -- all in dictionary
- BASE_CONTROLS: Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct, Size, TobinsQ, ROA, CashHoldings, DividendPayer, firm_maturity, earnings_volatility (9) -- all in dictionary
- Dynamic controls: Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct -- already covered as DVs/Controls in dictionary
- FE columns: gvkey, year -- both in dictionary

All 17 variables accounted for. No missing variables.

**One imprecision:** The provenance doc Section E says the ROA source is "CompustatEngine: iby, atq" -- while accurate, the actual computation involves `_compute_annual_q4_variable` and `_compute_annual_q4_variable_lag` helper functions that extract Q4 observations and compute lagged assets. The doc's variable dictionary row for ROA is slightly less precise than other entries but not wrong. **PASS with note.**

**Phase 6 Result:** 18 checks (17 variables + 1 completeness), 18 PASS.

All variable dictionary entries are factually accurate. The "17 specific columns" miscount is in Section F1 and is scored in Phase 7 (Pipeline).

---

## PHASE 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1. Dependency Chain**

7-step chain documented. Verified against code:

1. Raw inputs: manifest parquet, firmquarter CSV, Compustat data, Stage 2 linguistic parquets. All correct.
2. Engine loading: LinguisticEngine (0%/99% upper-only), CompustatEngine (1%/99% per fiscal year, merge_asof). Correct.
3. Panel builder: loads manifest via ManifestFieldsBuilder, builds via 16 builders (correct: panel builder `builders` dict has 17 entries including "manifest", so 16 non-manifest builders), merges on file_name with zero row-delta. Correct.
4. Runner loading: loads panel parquet. Provenance doc says "selecting 17 specific columns (lines 448--472)" but actual count is **19 columns** (lines 448--471 list the column names). **FAIL** -- 17 should be 19.
5. Sample filtering: correct description of complete-case + min-calls.
6. Regression estimation: PanelOLS, 4x2x3=24 regressions, correct.
7. Table generation: runner produces its own .tex, generate_all_tables reads 8 Main .txt files. Correct.

**F2. Data Engines Used**

4 engines listed: LinguisticEngine, CompustatEngine, PRiskQLagBuilder, PRiskQLag2Builder.
- LinguisticEngine provides 6 variables (4 DV uncertainty + Analyst_QA + Entire_All_Negative). Correct.
- CompustatEngine provides Size, TobinsQ, ROA, CashHoldings, DividendPayer, firm_maturity, earnings_volatility, BookLev (built but unused). Correct.
- PRiskQLagBuilder provides PRiskQ_lag. Correct.
- PRiskQLag2Builder provides PRiskQ_lag2. Correct.
**PASS**

**F3. Merge Operations**

17 merge rows documented (one per non-manifest builder). All are left joins on file_name with zero row-delta enforcement. Verified against panel builder lines 131--148. The builder iterates over all_results (excluding "manifest") and merges each on file_name.

The provenance doc correctly notes that BookLev is "built but NOT used in runner" (runner's column selection does not include BookLev).

**PASS**

### G-CHECK: Outputs

**G1. Stage 3 Outputs:**
- `h11_prisk_uncertainty_lag_panel.parquet` -- verified: builder line 186
- `summary_stats.csv` -- verified: builder line 193
- `report_step3_h11_lag.md` -- verified: builder line 235
- `run_manifest.json` -- verified: builder lines 198--207

**PASS**

**G2. Stage 4 Outputs:**
- `h11_prisk_uncertainty_lag_table.tex` -- verified: runner line 555 via `_save_latex_table`
- `model_diagnostics.csv` -- verified: runner line 556
- `summary_stats.csv` -- verified: runner line 497
- `summary_stats.tex` -- verified: runner line 498
- `sample_attrition.csv` -- verified: runner line 569 via `generate_attrition_table`
- `sample_attrition.tex` -- verified: same function writes both CSV and TeX
- `regression_results_{sample}_{dv}_{lag}.txt` -- verified: runner line 551
- `run_manifest.json` -- verified: runner lines 573--583

All outputs accounted for. No phantom files (files listed that aren't written). No missing files (files written but not listed).

**PASS**

**G3. Summary Statistics:**
15 variables listed with labels. Verified against SUMMARY_STATS_VARS (runner lines 124--143): exact same 15 variables.

**PASS**

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization:**

Linguistic variables: 0%/99% upper-only per calendar year. Verified: `_linguistic_engine.py` line 257 (`lower=0.0, upper=0.99`). **PASS**

Compustat variables: 1%/99% per fiscal year (fyearq). Verified: `_compustat_engine.py` lines 1129--1136. DividendPayer in skip_winsorize set (line 1123--1124). **PASS**

PRisk variables: 1%/99% per calendar year. Verified: `prisk_q_lag.py` line 165 calls `winsorize_by_year(prisk_df, ["PRisk"], year_col="year")` with defaults (lower=0.01, upper=0.99). Same for `prisk_q_lag2.py` line 168. **PASS**

**H2. Missing Data Policy:**
Complete-case deletion with inf replacement. Verified: runner line 172: `df = panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()`. **PASS**

**H3. Transformations:**
Size = ln(atq). No centering/z-scoring/scaling on IVs. Verified. **PASS**

**Phase 7 Result:** 9 checks, 8 PASS, 1 FAIL (F1 paragraph 4 column count: claims "17 specific columns" but actual code lists 19).

---

## PHASE 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

The provenance doc reproduces the generate_all_tables.py entry verbatim. Verified line-by-line against actual code at lines 219--247:

**a) "id": "H11-Lag"** -- matches line 220. **PASS**

**b) "key_tails": ["one_pos", "one_pos"]** -- matches line 246. No top-level "tail" or "hyp_dir" field (type="moderation" uses key_tails). Correct. **PASS**

**c) "cols": 8** -- matches line 225. **PASS**

**d) "dvs": [(r"PRiskQ\_lag", 4), (r"PRiskQ\_lag2", 4)]** -- matches lines 236--239. The provenance doc correctly notes (in Known Issues L5) that this "dvs" field is misleading because PRiskQ_lag/lag2 are actually IVs, not DVs. **PASS**

**e) "key_vars": ["PRiskQ_lag", "PRiskQ_lag2"]** -- matches line 244. **PASS**

**Phase 8 Result:** 5 checks, 5 PASS.

---

## PHASE 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

Model family: PanelOLS. K1 should be filled; K2-K6 should be N/A.

**K1. PanelOLS Specifics:**

- Entity effects: "Absorbed via EntityEffects in PanelOLS formula; first level of MultiIndex (gvkey, year) = gvkey (firm FE)". Verified: runner line 187 (`+ EntityEffects`) and line 200 (`set_index(["gvkey", "year"])`). **PASS**

- Time effects: "Absorbed via TimeEffects; second level of MultiIndex = year (calendar year FE)". Verified: same lines. **PASS**

- other_effects: "Not used." Verified: no `other_effects` in any formula or PanelOLS call. **PASS**

- drop_absorbed: "True (line 203)". Verified: runner line 203: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`. **PASS**

- Singleton handling: "PanelOLS default behavior; no explicit singleton filter". Verified: no singleton logic in runner. **PASS**

**K2-K6:** All marked N/A. Correct for a PanelOLS suite. **PASS**

**Phase 9 Result:** 5 checks, 5 PASS.

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | **PASS** | All 17 variables (4 DVs, 2 IVs, 9 base controls, 2 dynamic controls [overlapping with DVs], 2 FE cols) are in Section E with formulas and sources |
| 2 | The model equation matches what the code actually estimates | **PASS** | Verified: formula at lines 184-188 matches B1 equations; QA/Pres distinction is correct |
| 3 | The specification register accounts for every model column | **PASS** | 8 rows in Section C match 8 columns in generate_all_tables.py; all DV/IV/FE/control combinations verified |
| 4 | The attrition cascade has row counts for each filter step | **FAIL** | Section D2 describes filter steps qualitatively but provides no numeric row counts. The provenance doc acknowledges this is runtime-dependent, but the quality gate requires row counts |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | **PASS** | Runner: one-tailed beta > 0 (lines 219-225). generate_all_tables.py: key_tails=["one_pos","one_pos"] (line 246). Provenance doc: "One-tailed (beta > 0)". All consistent |
| 6 | The FE specification matches between docstring, code, and this document | **PASS** | Docstring: "EntityEffects + TimeEffects" (line 14). Code: firm FE (gvkey) + cal year FE (year) (lines 187, 200). Doc: "Entity=gvkey, Time=year". All match |
| 7 | Every merge in the panel builder is documented with join keys and type | **PASS** | Section F3 documents 17 merges, all on file_name, all left joins. Verified against builder lines 131-148 |
| 8 | The output file list matches what the runner actually writes | **PASS** | All 8 output types in G2 verified against runner code. No phantom or missing files |
| 9 | The model-family addendum is filled for the correct family only | **PASS** | K1 (PanelOLS) filled with 5 specific items. K2-K6 all marked N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | **PASS** | No [UNVERIFIED] claims found in the document. All claims are either verified or annotated with runtime-dependency notes |

**Phase 10 Result:** 10 checks, 9 PASS, 1 FAIL (Quality Gate 4: attrition cascade lacks row counts).

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

**1. DVs in B2 match DVs in C (spec register)?**
B2: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct.
C: Same 4 DVs across 8 specs. **PASS**

**2. DVs in C match DVs in I (table generator)?**
C has 4 DVs. I has `col_dv_labels: ["Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres", ...]` (labels for same 4 DVs, repeated for lag-1 and lag-2). The "dvs" field in I lists the IVs, not DVs (noted in L5). Cross-reference is logically consistent when accounting for the reversed IV/DV structure. **PASS**

**3. Controls in B4 match variables in E (dictionary)?**
B4 lists 9 base controls + 2 dynamic presentation controls. All 11 appear in E. **PASS**

**4. Column count in A matches rows in C?**
A: "Columns: 8". C: 8 rows. **PASS**

**5. Column count in A matches "cols" in I?**
A: 8. I: `"cols": 8`. **PASS**

**6. Tail direction: A matches B7 matches I?**
A: "One-tailed (beta > 0)". B7: "One-tailed, beta > 0". I: `key_tails: ["one_pos", "one_pos"]`. All consistent. **PASS**

**7. FE in B5 matches C matches K?**
B5: Entity=gvkey (firm), Time=year (cal year). C: All 8 specs show "Firm" and "Cal Year". K1: "EntityEffects" (gvkey) + "TimeEffects" (year). All match. **PASS**

**8. Panel index in A matches set_index in K?**
A: "(gvkey, year)". K1: "first level of MultiIndex (gvkey, year) = gvkey". Consistent. **PASS**

**Phase 11 Result:** 8 checks, 8 PASS.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 1 | D2 Structural Completeness | Attrition table has descriptive rows but no numeric "Rows Before / Rows After / Dropped" columns | Creation prompt template requires numeric row counts in the attrition cascade | Minor | Add row counts or [UNVERIFIED] tags (see Correction 2) |
| 5 | D2 Attrition Row Counts | "The exact row counts per step depend on runtime data" (no numbers given) | Runner lines 564-568 produce a 3-stage attrition table at runtime; counts not available without execution | Minor | Either run the suite and fill in row counts, or explicitly mark each step as [RUNTIME-DEPENDENT] |
| 7 (F1) | Column Count in Runner Loading | "selecting 17 specific columns (lines 448--472)" | Actual code lists 19 columns at lines 448-471 | Minor | Change "17" to "19" and adjust line range to "448--471" |
| 10 | Quality Gate 4 | Attrition cascade should have row counts | No row counts provided | Minor | Same root cause as the Phase 1/5 D2 failures |

Note: Failures in Phases 1, 5, and 10 all stem from the same root cause (missing attrition row counts). The F1 column count error (Phase 7) is an independent issue. Total unique root causes: 2.

---

## CORRECTIONS REQUIRED

**Correction 1: Section F1, Paragraph 4 -- Column Count**
- **Section:** F. Data Pipeline > F1. Dependency Chain > Step 4
- **Current text:** "Loads panel parquet, selecting 17 specific columns (lines 448--472)"
- **Should say:** "Loads panel parquet, selecting 19 specific columns (lines 448--471)"
- **Code reference:** `run_h11_prisk_uncertainty_lag.py` lines 448--471 (count the entries in the `columns=` list: file_name, gvkey, year, ff12_code, Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, PRiskQ_lag, PRiskQ_lag2, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct, Size, TobinsQ, ROA, CashHoldings, DividendPayer, firm_maturity, earnings_volatility = 19)

**Correction 2: Section D2 -- Add Row Counts or [UNVERIFIED] Tags**
- **Section:** D. Sample Construction > D2. Exclusion Criteria
- **Current text:** Table has "Step | Filter | Description" columns with no numeric row counts. The note at the bottom says "The exact row counts per step depend on runtime data."
- **Should say:** Either (a) run the suite and fill in the actual row counts, or (b) add a column with `[RUNTIME]` tags and change the note to formally satisfy Quality Gate 4 by adding: `[UNVERIFIED — row counts require runtime execution of the panel builder and runner. The runner's attrition table (lines 564--568) records only 3 coarse stages at runtime.]`
- **Code reference:** `run_h11_prisk_uncertainty_lag.py` lines 564--568 define a 3-stage attrition cascade populated at runtime.

---

## ADDITIONAL NOTES (non-blocking observations)

1. **Line number references are mostly accurate.** The provenance doc cites specific line numbers throughout. Nearly all were verified to be correct or within 1-2 lines of the actual code. This is unusually good for a manually-traced document.

2. **Known Issues section is thorough.** The 7 known issues documented in Section L are all genuine observations confirmed by code reading. Notably, L5 (misleading "dvs" field) and L1 (BookLev dead weight) are real code observations that a reader would want to know.

3. **The reversed IV/DV structure is well-documented.** The provenance doc consistently explains that this suite reverses the standard 4-IV pattern (uncertainty measures are DVs, political risk is IV), which is an important architectural distinction.

4. **No Lagged_DV is correctly flagged.** The provenance doc explicitly states this suite lacks a Lagged_DV control and provides a reasonable justification (call-level linguistic measures lack a natural prior-call lag structure).

5. **The `file_name` column is in the runner's read_parquet but not used in regressions.** It is used for the min-calls filter (`groupby("gvkey")["file_name"].transform("count")`), so its inclusion is justified even though it's not a regression variable.
