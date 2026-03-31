# H7 Provenance Document -- Adversarial Audit Report

**Audit Date:** 2026-03-30
**Auditor:** Hostile Auditor (automated adversarial audit)
**Suite:** H7 (Speech Uncertainty and Post-Call Illiquidity)
**Provenance Doc:** `docs/provenance/H7.md`
**Runner:** `src/f1d/econometric/run_h7_illiquidity.py`
**Panel Builder:** `src/f1d/variables/build_h7_illiquidity_panel.py`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 25 | 1 | 96% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 5 | 2 | 71% |
| Spec Register (Phase 4) | 7 | 7 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 2 | 1 | 67% |
| Variable Dictionary (Phase 6) | 21 | 17 | 4 | 81% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 8 | 1 | 89% |
| Table Generator Entry (Phase 8) | 5 | 5 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 8 | 2 | 80% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **112** | **101** | **11** | **90%** |

---

## VERDICT

**FAIL -- INACCURATE**: Factual errors found. The provenance document is structurally complete and largely accurate, but contains 11 failures including 2 significant factual errors (linguistic IV winsorization claim, Volatility window description) and several minor issues (missing attrition row counts, line number off-by-ones). See FAILURES section below.

---

## Phase 1: STRUCTURAL COMPLETENESS

Compared required sections from `docs/Prompts/Suite Provenance Doc.txt` against `docs/provenance/H7.md`.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block present with all fields |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equation present |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table with DV |
| B3. Independent Variable(s) | Yes | Yes | Yes | Table with 4 IVs |
| B4. Control Variables | Yes | Yes | Yes | Base + Extended tables |
| B5. Fixed Effects | Yes | Yes | Yes | Table with 4 FE types |
| B6. Standard Errors | Yes | Yes | Yes | Clustering documented |
| B7. Hypothesis Test | Yes | Yes | Yes | Direction + computation |
| C. Spec Register | Yes | Yes | Yes | 6-row table |
| D. Sample Construction | Yes | Yes | Partial | **Missing actual row counts in attrition** |
| D1. Population | Yes | Yes | Yes | |
| D2. Exclusion Criteria | Yes | Yes | Partial | Steps described but no Rows Before/After/Dropped columns |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Notes runtime-dependent |
| E. Variable Dictionary | Yes | Yes | Yes | 21-variable table |
| F. Data Pipeline | Yes | Yes | Yes | All 3 subsections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 4-engine table |
| F3. Merge Operations | Yes | Yes | Yes | 16 merges + 2 internal merges |
| G. Outputs | Yes | Yes | Yes | All 3 subsections present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 9 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 14 variables listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1, H2, H3 subsections |
| I. generate_all_tables Entry | Yes | Yes | Yes | Python dict + verification |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 N/A |
| L. Known Issues | Yes | Yes | Yes | 8 items |

**FAIL (1):** Section D2 is missing the "Rows Before | Rows After | Dropped" columns required by the creation prompt. The prompt specifies an attrition cascade table with row counts, but the provenance doc only provides a qualitative description of filter steps without actual numbers. The doc acknowledges "Exact counts depend on runtime execution" at D3, but the creation prompt requires at least placeholder counts or a reference to where they can be found.

---

## Phase 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

| Check | Claim | Verified Against | Result | Evidence |
|-------|-------|-----------------|--------|----------|
| A-1. Suite ID | H7 | Runner docstring line 6 | **PASS** | `ID: econometric/test_h7_illiquidity` |
| A-2. Title | "Speech Uncertainty and Post-Call Illiquidity" | Runner docstring line 4 | **PASS** | Docstring: "Test H7 Post-Call Illiquidity Hypothesis" -- semantically equivalent |
| A-3. Hypothesis | "Does higher managerial speech uncertainty during earnings calls increase stock illiquidity in the post-call window?" | Runner docstring lines 31-32 | **PASS** | Docstring: "H7: beta(uncertainty_var) > 0 -- higher uncertainty -> more illiquidity." |
| A-4. Direction | "one-tailed beta > 0" | Runner line 272, 279 | **PASS** | Code: `# One-tailed: H7 beta > 0` and `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` |
| A-5. Model Family | PanelOLS | Runner line 54 | **PASS** | `from linearmodels.panel import PanelOLS` |
| A-6. Estimator | `linearmodels.panel.PanelOLS` | Runner line 54 | **PASS** | Import statement confirms |
| A-7. Unit of Obs | "call-level (individual earnings call)" | Panel builder docstring line 17 | **PASS** | "Unit of observation: the individual earnings call (file_name)." |
| A-8. Panel Index | "(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6" | Runner line 231, 240 | **PASS** | `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` then `df_panel = df_prepared.set_index(["gvkey", time_col])` |
| A-9. Columns | 6 | Runner lines 92-100 | **PASS** | `MODEL_SPECS` has 6 entries (cols 1-6). Note: docstring says "4 model specifications" (stale) but `MODEL_SPECS` is the source of truth |
| A-10. File paths | Runner + Panel Builder exist | Disk check | **PASS** | Both files exist on disk |

**All 10 checks PASS.**

---

## Phase 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

### B1-CHECK: Regression Equation

**Claim:** `delta_amihud = b1*CEO_QA_Unc + b2*CEO_Pres_Unc + b3*Mgr_QA_Unc + b4*Mgr_Pres_Unc + Controls + alpha_i + delta_t + epsilon`

**Code (runner lines 228, 243-254):**
- `exog = KEY_IVS + controls` (line 228)
- Industry FE: `PanelOLS(dependent=df_panel[dv], exog=df_panel[exog], entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"])` (lines 244-249)
- Firm FE: `"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` (line 253)

The equation correctly includes all 4 IVs, controls, entity FE (alpha_i), and time FE (delta_t).

**Result: PASS**

### B2-CHECK: Dependent Variable(s)

**Claim:** `delta_amihud` = PostAmihud - PreAmihud, with daily_illiq = |RET| / (VOL * |PRC|) * 1e6.

**Code (amihud_change.py lines 317-319, 373):**
```python
merged["dollar_volume"] = merged["VOL"] * merged["PRC"].abs()
dollar_vol_masked = merged["dollar_volume"].replace(0, np.nan)
merged["daily_illiq"] = merged["RET"].abs() / dollar_vol_masked * 1e6
...
amihud["delta_amihud"] = amihud["post_call_amihud"] - amihud["pre_call_amihud"]
```

The formula matches. The timing claim of [-3,-1] pre and [+1,+3] post is verified by `window_days=3` (default, line 49) and ranking logic (lines 344-355, 358-359).

**Result: PASS**

### B3-CHECK: Independent Variable(s)

**Claim:** 4 IVs all enter simultaneously in every specification.

**Code (runner lines 67-71, 228):**
```python
KEY_IVS = ["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct",
           "Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct"]
...
exog = KEY_IVS + controls
```

All 4 IVs are included in `exog` for every spec. No IVs are missing from the provenance doc.

**Result: PASS**

### B4-CHECK: Control Variables

**Claim:** Base = 8 controls (Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, pre_call_amihud). Extended = Base + 4 (Volatility, StockPrice, Turnover, Analyst_QA_Uncertainty_pct).

**Code (runner lines 74-90):**
```python
BASE_CONTROLS = ["Size", "TobinsQ", "ROA", "BookLev", "CapexAt",
                 "DividendPayer", "OCF_Volatility", "pre_call_amihud"]
EXTENDED_CONTROLS = BASE_CONTROLS + ["Volatility", "StockPrice", "Turnover",
                                      "Analyst_QA_Uncertainty_pct"]
```

Exact match. Base has 8, Extended has 12.

**Volatility window description (FAILURE):**
The provenance doc B4 table says Volatility = "std(daily RET) * sqrt(252) * 100, over inter-call window [prev_call+1d, current_call-5d], min 10 trading days."

The code (`_crsp_engine.py` lines 361-366) computes:
```python
year_manifest["window_start"] = year_manifest["start_date"] + pd.Timedelta(days=DAYS_AFTER_CURRENT_CALL)  # +1d
year_manifest["window_end"] = year_manifest["next_call_date"] - pd.Timedelta(days=DAYS_BEFORE_NEXT_CALL)  # -5d
```

The actual window is **[current_call+1d, next_call-5d]** (a FORWARD-looking inter-call window), NOT [prev_call+1d, current_call-5d] (a backward-looking window) as claimed.

**Result: FAIL** -- Volatility window description is factually wrong.

### B5-CHECK: Fixed Effects

**Claim:**
- Industry FE via ff12_code in other_effects (cols 1, 3, 5)
- Firm FE via EntityEffects (cols 2, 4, 6)
- Cal Year via time_effects=True (cols 1-4)
- Cal Year-Quarter via time_effects=True (cols 5-6)

**Code (runner lines 231, 243-254):**
- `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` (line 231)
- Industry: `other_effects=df_panel["ff12_code"]` (line 247)
- Firm: `EntityEffects + TimeEffects` (line 253)

Exact match for all FE types and spec assignments.

**Result: PASS**

### B6-CHECK: Standard Errors

**Claim:** `cov_type="clustered"`, `cluster_entity=True`

**Code (runner lines 250, 255):**
```python
model = model_obj.fit(cov_type="clustered", cluster_entity=True)
```

Exact match.

**Result: PASS**

### B7-CHECK: Hypothesis Test

**Claim:** One-tailed beta > 0; `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` (runner line 279). Stars: *** < 0.01, ** < 0.05, * < 0.10.

**Code (runner lines 278-279, 292-297):**
```python
p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
...
def _sig_stars(p):
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""
```

Exact match.

**Result: PASS**

### Phase 3 Summary: 5 PASS, 2 FAIL (Volatility window description incorrect)

---

## Phase 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

| Check | Result | Evidence |
|-------|--------|----------|
| Row count matches MODEL_SPECS | **PASS** | 6 rows in table, 6 entries in MODEL_SPECS (lines 92-100) |
| Col 1: DV=delta_amihud, Entity=Industry(FF12), Time=Cal Yr, Controls=Base | **PASS** | Matches `{"col": 1, "dv": "delta_amihud", "fe": "industry", "controls": "base"}` |
| Col 2: DV=delta_amihud, Entity=Firm, Time=Cal Yr, Controls=Base | **PASS** | Matches `{"col": 2, "dv": "delta_amihud", "fe": "firm", "controls": "base"}` |
| Col 3: DV=delta_amihud, Entity=Industry(FF12), Time=Cal Yr, Controls=Extended | **PASS** | Matches `{"col": 3, "dv": "delta_amihud", "fe": "industry", "controls": "extended"}` |
| Col 4: DV=delta_amihud, Entity=Firm, Time=Cal Yr, Controls=Extended | **PASS** | Matches `{"col": 4, "dv": "delta_amihud", "fe": "firm", "controls": "extended"}` |
| Col 5: DV=delta_amihud, Entity=Industry(FF12), Time=Cal Yr-Qtr, Controls=Extended | **PASS** | Matches `{"col": 5, "dv": "delta_amihud", "fe": "industry_yq", "controls": "extended"}` |
| Col 6: DV=delta_amihud, Entity=Firm, Time=Cal Yr-Qtr, Controls=Extended | **PASS** | Matches `{"col": 6, "dv": "delta_amihud", "fe": "firm_yq", "controls": "extended"}` |

**All 7 checks PASS.**

---

## Phase 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

### D1-CHECK: Population

**Claim:** Starting dataset = master_sample_manifest.parquet, Year range 2002-2018, Unit = individual earnings call.

**Code (panel builder line 57, runner line 141-145):**
Panel builder loads manifest via `get_latest_output_dir(root_path / "outputs" / "1.4_AssembleManifest")`. Year range is configured via `project.yaml` (panel builder lines 228-235). Unit is call-level (file_name).

Cross-reference: project scope states 112,968 calls, 2,429 firms, 2002-2018.

**Result: PASS**

### D2-CHECK: Exclusion Criteria

**Claim:** 5 steps: (1) Full manifest, (2) Main sample (excl FF12=8,11), (3) DV non-missing, (4) Complete case, (5) Min calls >= 5.

**Code (runner lines 172-211):**
1. `load_panel()` loads full panel
2. `filter_main_sample()`: `panel[~panel["ff12_code"].isin([8, 11])]` (line 174)
3. `prepare_regression_data()`: `df[df[dv].notna()]` (line 199)
4. `df[complete_mask]` (line 203)
5. `firm_counts >= MIN_CALLS_PER_FIRM` where `MIN_CALLS_PER_FIRM = 5` (lines 102, 206-208)

Filter steps match. But the creation prompt requires "Rows Before | Rows After | Dropped" columns in the attrition cascade table. The provenance doc only provides qualitative descriptions without actual numbers.

The attrition table in the runner (lines 470-475) outputs to `sample_attrition.csv` with 4 steps, which does not include per-specification counts for steps 3-5.

**Result: FAIL** -- Missing actual row counts as required by the creation prompt's attrition table format.

### D3-CHECK: Sample Counts per Specification

**Claim:** "Exact counts depend on runtime execution."

This is accurate -- N varies across specs because extended controls introduce more NaN rows, and YQ specs add cal_yr_qtr to the required columns. The doc notes the attrition cascade is saved to output files.

**Result: PASS**

### Phase 5 Summary: 2 PASS, 1 FAIL

---

## Phase 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

Verified each variable against its source code.

### DV: delta_amihud

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Name | delta_amihud | Runner line 93 | **PASS** |
| Formula | PostAmihud - PreAmihud; daily_illiq = \|RET\| / (VOL * \|PRC\|) * 1e6 | amihud_change.py lines 317-319, 373 | **PASS** |
| Source | CRSPEngine: RET, VOL, PRC via get_raw_daily_data() | amihud_change.py lines 74-75 | **PASS** |
| Winsorized | 1%/99% by calendar year (at AmihudChangeBuilder level) | amihud_change.py lines 110-112 | **PASS** |
| Timing | Event window around call | amihud_change.py lines 358-359 (pre/post ranks <= window_days) | **PASS** |

### Control: pre_call_amihud

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Name | pre_call_amihud | Runner line 82 | **PASS** |
| Formula | mean(daily_illiq for trading days [-3,-1]) | amihud_change.py lines 362-365 | **PASS** |
| Source | CRSPEngine: RET, VOL, PRC | amihud_change.py lines 74-75 | **PASS** |
| Winsorized | 1%/99% by calendar year | amihud_change.py lines 109-112 | **PASS** |

### IVs: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Names | Exact match | Runner lines 67-71 | **PASS** |
| Source | LinguisticEngine | Builder files import from `_linguistic_engine.get_engine()` | **PASS** |
| Winsorized | "Not winsorized (bounded [0,100] by construction)" | _linguistic_engine.py lines 255-258 | **FAIL** |

**FAILURE:** The provenance doc claims all 5 `*_Uncertainty_pct` variables are "Not winsorized (bounded [0,100] by construction)." However, the LinguisticEngine (`_linguistic_engine.py` lines 254-258) applies **0%/99% upper-only per-year winsorization** to ALL `_pct` columns:

```python
combined = winsorize_by_year(
    combined, existing_pct_cols, year_col="year",
    lower=0.0, upper=0.99, min_obs=10
)
```

This means all 5 uncertainty pct variables (CEO_QA, CEO_Pres, Manager_QA, Manager_Pres, and Analyst_QA) ARE winsorized at 0%/99% (upper-only) per year. The 0% lower bound effectively means no lower clipping (since values are already >= 0 by construction), but the 99% upper bound does clip extreme values.

This affects 5 variables in the dictionary: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, and Analyst_QA_Uncertainty_pct.

### Control: Size

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | ln(atq), for atq > 0 | _compustat_engine.py line 938: `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` | **PASS** |
| Winsorized | 1%/99% by fiscal year | _compustat_engine.py line 1134-1136 | **PASS** |

### Control: TobinsQ

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | (cshoq * prccq + dlcq + dlttq) / atq | _compustat_engine.py lines 982-991 | **PASS** |
| Note | Docstring discrepancy: builder says (AT + cshoq*prccq - CEQ)/AT | TobinsQBuilder line 24 vs _compustat_engine.py line 988-991 | **PASS** -- doc correctly notes this in L.1 |

### Control: ROA

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | iby_annual (Q4) / avg_assets | _compustat_engine.py lines 954-963 | **PASS** |

### Control: BookLev

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | (dlcq.fillna(0) + dlttq.fillna(0)) / atq | _compustat_engine.py line 943 | **PASS** |

### Control: CapexAt

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | capxy_annual (Q4 only) / atq_lag | _compustat_engine.py lines 994-999 | **PASS** |

### Control: DividendPayer

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | 1 if dvy_annual (Q4 only) > 0, else 0 | _compustat_engine.py lines 1005-1007 | **PASS** |
| Winsorized | No (binary) | Correct -- binary indicator | **PASS** |

### Control: OCF_Volatility

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | Rolling 5-year std (min 3 yrs) of (oancfy / atq_{t-1}) | _compustat_engine.py lines 334-335 | **PASS** |
| Rolling window | 1826-day rolling window | _compustat_engine.py line 335: `.rolling("1826D", min_periods=3)` | **PASS** |

### Control: Volatility

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | std(daily RET) * sqrt(252) * 100 | _crsp_engine.py line 255: `(std_ret * np.sqrt(252) * 100)` | **PASS** |
| Window | "over inter-call window [prev_call+1d, current_call-5d]" | _crsp_engine.py lines 361-366 | **FAIL** |

**FAILURE:** Same as B4 Volatility window error. The actual window is [current_call+1d, next_call-5d] per `DAYS_AFTER_CURRENT_CALL=1` (line 41), `DAYS_BEFORE_NEXT_CALL=5` (line 42), and `window_start = start_date + 1d`, `window_end = next_call_date - 5d` (lines 361-366).

### Control: StockPrice

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | PRC at call date or nearest prior trading day | stock_price.py lines 207-214 | **PASS** |
| Winsorized | No | stock_price.py -- no winsorization code | **PASS** |

### Control: Turnover

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | VOL / (SHROUT * 1000) | turnover.py lines 231-235 | **PASS** |
| Winsorized | No | turnover.py -- no winsorization code | **PASS** |

### Control: Analyst_QA_Uncertainty_pct

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| Formula | Percentage of analyst words in Q&A classified as uncertainty | analyst_qa_uncertainty.py -- queries LinguisticEngine | **PASS** |
| Winsorized | "Not winsorized (bounded [0,100] by construction)" | _linguistic_engine.py lines 254-258 | **FAIL** -- Same winsorization error as other linguistic IVs |

### FE variables: ff12_code, gvkey, cal_yr, cal_yr_qtr

| Field | Claim | Code Reference | Result |
|-------|-------|---------------|--------|
| ff12_code | FF12 industry code from manifest | panel_builder line 145 | **PASS** |
| gvkey | Compustat GVKEY | panel_builder line 151 | **PASS** |
| cal_yr | start_date.dt.year | panel_utils.py line 195 | **PASS** |
| cal_yr_qtr | cal_yr * 10 + start_date.dt.quarter | panel_utils.py line 201 | **PASS** |

### Completeness Check

All variables in MODEL_SPECS, KEY_IVS, BASE_CONTROLS, and EXTENDED_CONTROLS are present in the dictionary. FE columns (gvkey, ff12_code, cal_yr, cal_yr_qtr) are also present.

No missing variables.

### Phase 6 Summary: 17 PASS, 4 FAIL (linguistic winsorization x4: 4 IVs + Analyst_QA)

---

## Phase 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1. Dependency Chain:**
The 7-step chain in the provenance doc matches the actual data flow:
1. Raw inputs: CRSP DSF, Compustat, CCM, Stage 2 linguistic, manifest -- **PASS**
2. Engine loading: CompustatEngine, CRSPEngine, LinguisticEngine -- **PASS**
3. Panel builder: merges on file_name, zero row-delta enforced -- **PASS** (verified in build_h7_illiquidity_panel.py lines 126-143)
4. Runner loading: loads 21 columns (count verified: runner lines 149-159 lists 21 column names) -- **PASS**
5. Sample filtering: correct order documented -- **PASS**
6. Regression: PanelOLS, 6 specs -- **PASS**
7. Table generation: generate_all_tables.py entry exists -- **PASS**

**F2. Data Engines:**
All 4 engines correctly listed with correct source data and variables provided. **PASS**

**F3. Merge Operations:**
All 16 builder merges documented with correct keys (file_name) and type (left). Internal AmihudChangeBuilder merges also documented. **PASS**

### G-CHECK: Outputs

**G1. Stage 3 Outputs:**

| File Claimed | Actually Written | Result |
|------|------|--------|
| h7_illiquidity_panel.parquet | panel_builder line 160 | **PASS** |
| summary_stats.csv | panel_builder lines 165-168 | **PASS** |
| run_manifest.json | panel_builder lines 170-182 | **PASS** |
| report_step3_h7.md | panel_builder lines 201-203 | **PASS** |

**G2. Stage 4 Outputs:**

| File Claimed | Actually Written | Result |
|------|------|--------|
| h7_illiquidity_table.tex | runner line 378 | **PASS** |
| model_diagnostics.csv | runner line 400 | **PASS** |
| summary_stats.csv | runner line 448 | **PASS** |
| summary_stats.tex | runner line 448 | **PASS** |
| sample_attrition.csv | runner line 470-475 (via generate_attrition_table) | **PASS** |
| sample_attrition.tex | runner line 470-475 | **PASS** |
| regression_results_col{1-6}.txt | runner line 392 | **PASS** |
| report_step4_H7.md | runner line 486 | **PASS** |
| run_manifest.json | runner line 477-483 | **PASS** |

All output files verified. **PASS**

**G3. Summary Statistics:**
The doc lists 14 variables. The code (runner lines 110-124) has 14 entries in SUMMARY_STATS_VARS. Variable names match. The doc correctly notes in L.6 that StockPrice and Turnover are omitted. **PASS**

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization:**

| Claim | Code Reference | Result |
|-------|---------------|--------|
| Compustat vars: 1%/99% by fiscal year | _compustat_engine.py lines 1130-1136 | **PASS** |
| CRSP Volatility: 1%/99% by calendar year | _crsp_engine.py lines 421, 445-447 | **PASS** |
| delta_amihud + pre_call_amihud: 1%/99% by calendar year | amihud_change.py lines 110-112 | **PASS** |
| Linguistic IVs: "Not winsorized" | _linguistic_engine.py lines 254-258 | **FAIL** |
| StockPrice, Turnover: Not winsorized | stock_price.py, turnover.py | **PASS** |
| DividendPayer: Not winsorized (binary) | Correct | **PASS** |

**FAILURE:** H1 repeats the linguistic IV winsorization error. The LinguisticEngine applies 0%/99% upper-only per-year winsorization to all _pct columns. This is documented nowhere in Section H.

**H2. Missing Data Policy:**
- Complete-case deletion: verified at runner line 202-203. **PASS**
- Inf/-Inf replacement: verified at runner line 192. **PASS**
- Min trading days: verified at amihud_change.py lines 282-283. **PASS**
- Dollar volume zero to NaN: verified at amihud_change.py line 318. **PASS**

**H3. Transformations:**
- Size = ln(atq): verified. **PASS**
- 1e6 Amihud scaling: verified. **PASS**
- No centering/z-scoring: correct -- no such transforms in the code. **PASS**

### Phase 7 Summary: 8 PASS, 1 FAIL (linguistic winsorization in H1)

---

## Phase 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

Verified against `outputs/generate_all_tables.py` lines 183-195.

| Field | Doc Claims | Code Says | Result |
|-------|-----------|----------|--------|
| id | "H7" | "H7" | **PASS** |
| cols | 6 | 6 | **PASS** |
| dvs | [("delta_amihud", 6)] | `[(r"delta\_amihud", 6)]` | **PASS** |
| tail | "one" | "one" | **PASS** |
| hyp_dir | ">" | ">" | **PASS** |

The provenance doc says "lines 208-219" for the entry. The actual lines are 183-195. This is a minor line number discrepancy but the content is correct.

The doc correctly notes there is no `key_vars` field -- H7 uses the standard 4-IV layout rendered by the default table generator path (not the moderation path).

**All 5 checks PASS.**

---

## Phase 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

### K1. PanelOLS Specifics

| Claim | Code Reference | Result |
|-------|---------------|--------|
| Industry FE: entity_effects=False, time_effects=True, other_effects=ff12_code | Runner lines 244-249 | **PASS** |
| Industry FE: drop_absorbed=True, check_rank=False | Runner line 248 | **PASS** |
| Firm FE: from_formula with EntityEffects + TimeEffects | Runner lines 252-254 | **PASS** |
| Firm FE: drop_absorbed=True | Runner line 254 | **PASS** |
| Panel index: cols 1-4 = (gvkey, cal_yr); cols 5-6 = (gvkey, cal_yr_qtr) | Runner line 231, 240 | **PASS** |
| R-squared: model.rsquared; Adj R2: manual formula | Runner lines 262, 269-270 | **PASS** |

### K2-K6: N/A

Correctly marked N/A for Cox PH, Logit/Probit/LPM, IV/2SLS, OLS, Other.

**All 6 checks PASS.**

---

## Phase 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | **Yes** | All 21 variables present with formulas |
| 2 | The model equation matches what the code actually estimates | **Yes** | B1 verified; all 4 IVs + controls + FE in equation |
| 3 | The specification register accounts for every model column | **Yes** | 6 rows matching 6 MODEL_SPECS entries |
| 4 | The attrition cascade has row counts for each filter step | **No** | D2 has qualitative steps but no actual row counts (Rows Before/After/Dropped). The creation prompt requires a table with these columns. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | **Yes** | Runner: one-tailed beta>0; generate_all_tables: tail="one", hyp_dir=">" |
| 6 | The FE specification matches between docstring, code, and this document | **Yes** | All three consistent (note: docstring says "4 specs" but code has 6 -- this is a stale docstring, not an FE mismatch) |
| 7 | Every merge in the panel builder is documented with join keys and type | **Yes** | 16 merges + 2 internal merges all documented |
| 8 | The output file list matches what the runner actually writes | **Yes** | All 9 Stage 4 files verified |
| 9 | The model-family addendum is filled for the correct family only | **Yes** | K1 (PanelOLS) filled; K2-K6 marked N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | **No** | No [UNVERIFIED] claims exist, but the linguistic variable winsorization claim is factually wrong and should have been marked [UNVERIFIED] if the author was unsure |

**8 of 10 quality gates met. 2 failed.**

---

## Phase 11: CROSS-REFERENCE CONSISTENCY

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | DVs in B2 match DVs in C | **PASS** | B2: delta_amihud. C: all 6 rows show delta_amihud. |
| 2 | DVs in C match DVs in I | **PASS** | C: delta_amihud for all 6 specs. I: dvs=[("delta_amihud", 6)]. |
| 3 | Controls in B4 match variables in E | **PASS** | All 8 base + 4 extended controls appear in dictionary. |
| 4 | Column count in A matches rows in C | **PASS** | A: Columns=6. C: 6 rows. |
| 5 | Column count in A matches "cols" in I | **PASS** | A: Columns=6. I: cols=6. |
| 6 | Tail direction: A matches B7 matches I | **PASS** | A: "one-tailed beta > 0". B7: "one-tailed (beta > 0)". I: tail="one", hyp_dir=">". |
| 7 | FE in B5 matches C matches K | **PASS** | B5: Industry/Firm x CalYr/CalYrQtr. C: matches per spec. K1: matches implementation. |
| 8 | Panel index in A matches set_index in K | **PASS** | A: "(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6". K1: same. |

**All 8 cross-reference checks PASS.** No internal contradictions detected.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 1 | D2 attrition table format | Qualitative steps without row counts | Creation prompt requires "Rows Before / Rows After / Dropped" columns | Medium | Add row count columns (runtime-dependent; mark as [UNVERIFIED] with instructions to fill from sample_attrition.csv) |
| 3 | B4 Volatility window | "[prev_call+1d, current_call-5d]" | `window_start = start_date + 1d, window_end = next_call_date - 5d`, i.e., [current_call+1d, next_call-5d] | **High** | Fix window description to [current_call+1d, next_call-5d] |
| 5 | D2 row counts | No actual numbers in attrition cascade | Creation prompt spec requires them | Medium | Same as Phase 1 D2 failure |
| 6 | E: CEO_QA_Uncertainty_pct winsorization | "Not winsorized (bounded [0,100] by construction)" | LinguisticEngine applies 0%/99% upper-only per-year winsorization (_linguistic_engine.py lines 254-258) | **High** | Change to "0%/99% upper-only per-year (at LinguisticEngine level)" |
| 6 | E: CEO_Pres_Uncertainty_pct winsorization | "Not winsorized (bounded [0,100] by construction)" | Same as above | **High** | Same fix |
| 6 | E: Manager_QA_Uncertainty_pct winsorization | "Not winsorized (bounded [0,100] by construction)" | Same as above | **High** | Same fix |
| 6 | E: Manager_Pres_Uncertainty_pct winsorization | "Not winsorized (bounded [0,100] by construction)" | Same as above | **High** | Same fix |
| 6 | E: Volatility window | "[prev_call+1d, current_call-5d]" | [current_call+1d, next_call-5d] | **High** | Same as Phase 3 B4 fix |
| 6 | E: Analyst_QA_Uncertainty_pct winsorization | "Not winsorized (bounded [0,100] by construction)" | LinguisticEngine applies 0%/99% upper-only per-year winsorization | **High** | Change to "0%/99% upper-only per-year (at LinguisticEngine level)" |
| 7 | H1 Linguistic IVs winsorization | "Not winsorized: bounded [0, 100] by construction" | LinguisticEngine applies 0%/99% upper-only per-year winsorization | **High** | Fix H1 to document actual winsorization treatment |
| 10 | QG4 attrition row counts | No row counts | Required by creation prompt | Medium | Add counts or mark [UNVERIFIED] |

---

## CORRECTIONS REQUIRED

### Correction 1: Volatility window description (HIGH)

**Sections to edit:** B4 (Volatility row in Extended Controls table), E (Volatility row in Variable Dictionary), F2 (Volatility entry)

**Current (wrong) text in B4:**
> "std(daily RET) * sqrt(252) * 100, over inter-call window [prev_call+1d, current_call-5d], min 10 trading days"

**Should say:**
> "std(daily RET) * sqrt(252) * 100, over inter-call window [current_call+1d, next_call-5d], min 10 trading days"

**Code reference:** `_crsp_engine.py` lines 41-42 (`DAYS_AFTER_CURRENT_CALL = 1`, `DAYS_BEFORE_NEXT_CALL = 5`) and lines 361-366.

**Same fix needed in Section E (Volatility row):**

Current: "std(daily RET) * sqrt(252) * 100 over inter-call window, min 10 trading days"

This is vague enough to be acceptable, but the detailed description in B4 is wrong.

### Correction 2: Linguistic variable winsorization (HIGH)

**Sections to edit:** B3 (all 4 IV rows), E (all 5 linguistic variable rows), H1 (Linguistic IVs subsection)

**Current (wrong) text in E for each linguistic variable:**
> "Not winsorized (bounded [0,100] by construction)"

**Should say:**
> "0%/99% upper-only per-year (at LinguisticEngine level)"

**Current (wrong) text in H1:**
> "**Linguistic IVs** (all 5 `*_Uncertainty_pct` variables): Not winsorized: bounded [0, 100] by construction"

**Should say:**
> "**Linguistic IVs** (all 5 `*_Uncertainty_pct` variables): 0%/99% upper-only per-year winsorization at LinguisticEngine level (`_linguistic_engine.py` lines 254-258, `winsorize_by_year(..., lower=0.0, upper=0.99, min_obs=10)`). The 0% lower bound is a no-op since values are >= 0 by construction, but the 99% upper bound clips extreme values per year."

**Code reference:** `_linguistic_engine.py` lines 235-259.

### Correction 3: Attrition cascade row counts (MEDIUM)

**Section to edit:** D2

**Current text:**
> 5-step table with qualitative descriptions only

**Should say:**
> Add columns "Rows Before | Rows After | Dropped" with either actual runtime counts or "[UNVERIFIED -- fill from sample_attrition.csv after runtime execution]" placeholders.

**Code reference:** Runner lines 470-475 output attrition to `sample_attrition.csv`. If runtime data is available, populate from that file. Otherwise, mark as [UNVERIFIED] per creation prompt quality gate 10.

### Correction 4: generate_all_tables.py line reference (MINOR)

**Section to edit:** I

**Current text:**
> "Source: `outputs/generate_all_tables.py`, lines 208-219."

**Should say:**
> "Source: `outputs/generate_all_tables.py`, lines 183-195."

**Code reference:** The H7 entry starts at line 184 (`"id": "H7"`) and ends at line 195 (closing brace).

### Correction 5 (advisory, not required): Runner docstring stale spec count

The runner docstring (lines 7, 11) says "4 model specifications" and "4 columns in one table," but MODEL_SPECS has 6 entries. This is not a provenance doc error (the doc correctly says "Columns: 6"), but it should be noted in Section L as a known docstring/code discrepancy.

---

## ADDITIONAL NOTES

1. **Line number precision:** Several line references in the provenance doc are off by 1-2 lines (e.g., "line 193" for Inf replacement when the actual code is line 192; "line 281-282" for min days when the actual code is lines 282-283). These are minor and do not affect correctness, but could be tightened.

2. **Runner docstring stale:** The docstring says "4 model specifications" (lines 7, 11) but MODEL_SPECS has 6 entries (cols 5-6 added for YQ FE specs). The provenance doc does not flag this discrepancy in Section L.

3. **AmihudChangeBuilder internal merge key:** The provenance doc F3 says the internal AmihudChangeBuilder merges manifest to CCM on "gvkey" (left join). The actual code (amihud_change.py line 181) merges on "gvkey" with `how="left"`. However, the second internal merge (line 294-298) merges `year_calls` with `year_crsp` as `left_on="permno_int", right_on="PERMNO", how="inner"`. The doc says the key is "permno_int = PERMNO" and type is "inner" which is correct.

4. **CRSPEngine Amihud scaling:** The provenance doc L.3 says the CRSPEngine's inter-call Amihud computation uses 1e6 scaling at `_crsp_engine.py line 256`. The actual code at line 256 is `illiq = (mean_illiq * 1e6).where(sufficient)`. This is correct, though note that `mean_illiq` is already `mean(daily_illiq)` where `daily_illiq = |RET| / dollar_volume` (no 1e6 at the daily level in the engine), and the 1e6 is applied to the aggregate. This differs from the AmihudChangeBuilder which applies 1e6 at the daily level (line 319). The net result is the same if there is exactly 1 day in the window, but may differ slightly for multi-day windows due to the order of operations (mean of scaled vs scale of mean). This is a minor inconsistency between the two Amihud implementations but is not relevant to H7 since H7 uses AmihudChangeBuilder, not the CRSPEngine's Amihud.
