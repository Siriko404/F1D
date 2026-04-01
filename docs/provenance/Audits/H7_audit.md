# Adversarial Audit Report: H7 Provenance Document

**Auditor:** Claude Code (hostile, adversarial)
**Date:** 2026-04-01
**Suite:** H7 — Speech Uncertainty and Post-Call Illiquidity
**Provenance doc:** `docs/provenance/H7.md`
**Runner:** `src/f1d/econometric/run_h7_illiquidity.py`
**Builder:** `src/f1d/variables/build_h7_illiquidity_panel.py`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|---|---|---|---|---|
| Structural Completeness (Phase 1) | 26 | 26 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 7 | 7 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 2 | 1 | 67% |
| Variable Dictionary (Phase 6) | 18 | 17 | 1 | 94% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 6 | 3 | 67% |
| Table Generator Entry (Phase 8) | 5 | 4 | 1 | 80% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **109** | **102** | **7** | **94%** |

---

## VERDICT

**FAIL — INACCURATE**: The document is structurally complete and internally self-consistent, but contains 4 distinct factual errors — all wrong line-number citations and one off-by-one column count. Specifically:

1. Section H1 cites `_compustat_engine.py, line 1134` for Compustat winsorization; actual line is 1232.
2. Section H2 cites `prepare_regression_data() line 193` for Inf-replacement; actual line is 192.
3. Section F1 Step 4 says "21 columns"; actual runner loads 22 columns.
4. Section I cites `generate_all_tables.py, lines 183--195`; actual H7 entry is lines 164--176.

None of these errors affect the conceptual accuracy of what the suite does, but each is a verifiably wrong factual claim and must be corrected.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Read `docs/Prompts/Suite Provenance Doc.txt` to extract required sections. Verified presence and completeness in `docs/provenance/H7.md`.

| Section | Required | Present | Complete | Notes |
|---|---|---|---|---|
| A. Suite Identity | Yes | Yes | Yes | YAML block present |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equation present |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table with 1 DV |
| B3. Independent Variable(s) | Yes | Yes | Yes | Table with 4 IVs |
| B4. Control Variables | Yes | Yes | Yes | Base (8) + Extended (4 additional) tables |
| B5. Fixed Effects | Yes | Yes | Yes | 4-row FE table with specs column |
| B6. Standard Errors | Yes | Yes | Yes | cov_type and clustering documented |
| B7. Hypothesis Test | Yes | Yes | Yes | Direction, p-value formula, thresholds |
| C. Spec Register | Yes | Yes | Yes | 6-row table with notes column |
| D. Sample Construction | Yes | Yes | Yes | All 3 subsections present |
| D1. Population | Yes | Yes | Yes | Manifest source and year range stated |
| D2. Exclusion Criteria | Yes | Yes | Yes | 5-step cascade; counts [UNVERIFIED] with explanation |
| D3. Sample Counts | Yes | Yes | Yes | Deferred to runtime with explanation |
| E. Variable Dictionary | Yes | Yes | Yes | 17 rows covering all regression variables + FE cols |
| F. Data Pipeline | Yes | Yes | Yes | All 3 subsections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain from raw to table |
| F2. Data Engines | Yes | Yes | Yes | 4 engine rows |
| F3. Merge Operations | Yes | Yes | Yes | 16 builder merges + 2 internal AmihudChange merges |
| G. Outputs | Yes | Yes | Yes | All 3 subsections present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 9 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 14 variables listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | 3 subsections |
| I. generate_all_tables Entry | Yes | Yes | Yes | Python block and verification notes |
| J. Reproduction Commands | Yes | Yes | Yes | 3-command bash block |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled; K2-K6 = N/A |
| L. Known Issues | Yes | Yes | Yes | 9 documented issues |

**Phase 1 verdict: ALL 26 structural checks PASS.**

---

## PHASE 2: SUITE IDENTITY (Section A)

**A-1. Suite ID**
- Doc: `H7`
- Evidence: Runner filename `run_h7_illiquidity.py`, suite prints "H7_Illiquidity", generate_all_tables.py entry `"id": "H7"`.
- **PASS**

**A-2. Title**
- Doc: `Speech Uncertainty and Post-Call Illiquidity`
- Runner `_save_latex_table()` line 316: `r"\caption{Speech Uncertainty and Post-Call Illiquidity}"` — exact match.
- **PASS**

**A-3. Hypothesis**
- Doc: "Does higher managerial speech uncertainty during earnings calls increase stock illiquidity in the post-call window?"
- Runner docstring lines 31-32: `H7: beta(uncertainty_var) > 0 — higher uncertainty -> more illiquidity.`
- Runner line 425: `print(f"Test: One-tailed (beta > 0)")`
- Doc is a valid expanded statement of the runner's concise hypothesis statement.
- **PASS**

**A-4. Direction**
- Doc: `one-tailed beta > 0`
- Runner line 272 comment: `# One-tailed: H7 beta > 0 (higher uncertainty -> more illiquidity)`
- Runner line 279: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` — one-tailed with beta > 0 direction.
- **PASS**

**A-5. Model Family**
- Doc: `PanelOLS`
- Runner line 54: `from linearmodels.panel import PanelOLS`; used at lines 244 and 254 in `run_regression()`.
- **PASS**

**A-6. Estimator**
- Doc: `linearmodels.panel.PanelOLS`
- Runner import: `from linearmodels.panel import PanelOLS` — module path `linearmodels.panel` confirmed.
- **PASS**

**A-7. Unit of Observation**
- Doc: `call-level (individual earnings call)`
- Builder docstring line 17: "Unit of observation: the individual earnings call (file_name)."
- **PASS**

**A-8. Panel Index**
- Doc: `(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6`
- Runner line 231: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`
- Runner line 240: `df_panel = df_prepared.set_index(["gvkey", time_col])`
- Cols 1-4 use `fe = "industry"/"firm"` (no `_yq` suffix) → `cal_yr`; cols 5-6 use `fe = "industry_yq"/"firm_yq"` → `cal_yr_qtr`. Exact match.
- **PASS**

**A-9. Columns**
- Doc: `6`
- Runner `MODEL_SPECS` lines 92-100: 6 dict entries (col 1, 2, 3, 4, 5, 6). `len(MODEL_SPECS) = 6`.
- **PASS**

**A-10. File paths**
- Runner: `src/f1d/econometric/run_h7_illiquidity.py` — confirmed to exist (was read).
- Builder: `src/f1d/variables/build_h7_illiquidity_panel.py` — confirmed to exist (was read).
- **PASS**

**Phase 2 verdict: 10/10 PASS.**

---

## PHASE 3: MODEL SPECIFICATION (Section B)

**B1-CHECK: Regression Equation**

Doc equation:
$$\Delta\text{Amihud}_{i,t} = \beta_1 \text{CEO\_QA\_Unc} + \beta_2 \text{CEO\_Pres\_Unc} + \beta_3 \text{Mgr\_QA\_Unc} + \beta_4 \text{Mgr\_Pres\_Unc} + \gamma' \mathbf{Controls} + \alpha_i + \delta_t + \varepsilon_{i,t}$$

Verification:
- DV `delta_amihud` — runner `MODEL_SPECS` entries all have `"dv": "delta_amihud"`. MATCH.
- 4 IVs: `KEY_IVS` (lines 67-71) = `CEO_QA_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`, `Manager_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct`. MATCH.
- Controls: `exog = KEY_IVS + controls` (runner line 228). MATCH.
- Entity FE (`alpha_i`): industry or firm depending on spec. MATCH.
- Time FE (`delta_t`): `cal_yr` or `cal_yr_qtr`. MATCH.
- **PASS**

**B2-CHECK: Dependent Variable**

Doc claims `delta_amihud` = PostAmihud - PreAmihud, daily_illiq = |RET| / (VOL * |PRC|) * 1e6, Pre = mean([-3,-1] trading days), Post = mean([+1,+3] trading days).

`amihud_change.py`:
- Line 319: `merged["daily_illiq"] = merged["RET"].abs() / dollar_vol_masked * 1e6` where `dollar_vol_masked = merged["VOL"] * merged["PRC"].abs()` (lines 317-318). Formula is `|RET| / (|VOL| * |PRC|) * 1e6`. MATCH.
- Lines 343-355: pre-window uses `pre_rank <= w` (w=3), post-window uses `post_rank <= w` (w=3). Trading-day positions 1–3 pre and post. MATCH.
- Line 373: `amihud["delta_amihud"] = amihud["post_call_amihud"] - amihud["pre_call_amihud"]`. MATCH.
- Source: `CRSPEngine.get_raw_daily_data()` — `amihud_change.py` line 75: `crsp_data = engine.get_raw_daily_data(root_path, years=list(years))`. MATCH.
- **PASS**

**B3-CHECK: Independent Variables**

All 4 IVs in `KEY_IVS` (lines 67-71):
- `CEO_QA_Uncertainty_pct` — MATCH
- `CEO_Pres_Uncertainty_pct` — MATCH
- `Manager_QA_Uncertainty_pct` — MATCH
- `Manager_Pres_Uncertainty_pct` — MATCH

Source: LinguisticEngine (via `CEOQAUncertaintyBuilder`, etc. imported in builder). MATCH.
No centering, log-transform, or z-scoring applied to IVs. MATCH.
- **PASS**

**B4-CHECK: Control Variables**

BASE_CONTROLS (runner lines 74-83):
- Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, pre_call_amihud

Doc Base Controls table: Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, pre_call_amihud — 8 variables, exact match.

EXTENDED_CONTROLS (runner lines 85-90) = BASE_CONTROLS + Volatility, StockPrice, Turnover, Analyst_QA_Uncertainty_pct

Doc Extended Controls table: Volatility, StockPrice, Turnover, Analyst_QA_Uncertainty_pct — 4 additional, exact match.

`pre_call_amihud` correctly noted as "Lagged DV / pre-event level control."
- **PASS**

**B5-CHECK: Fixed Effects**

Doc table:
| FE Type | Column | Specs |
|---|---|---|
| Industry | ff12_code | Cols 1, 3, 5 |
| Firm | gvkey | Cols 2, 4, 6 |
| Calendar Year | cal_yr | Cols 1, 2, 3, 4 |
| Calendar Year-Quarter | cal_yr_qtr | Cols 5, 6 |

Runner:
- Industry specs (MODEL_SPECS cols 1, 3, 5): `entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"]` (lines 246-248). MATCH.
- Firm specs (cols 2, 4, 6): `EntityEffects + TimeEffects` in formula (line 253). MATCH.
- `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` (line 231). Cols 5-6 use `_yq` suffix. MATCH.
- **PASS**

**B6-CHECK: Standard Errors**

Doc: `cov_type="clustered"`, `cluster_entity=True` (firm/gvkey level).
Runner lines 250 and 255: `model_obj.fit(cov_type="clustered", cluster_entity=True)` — both industry and firm branches use identical SE specification. MATCH.
Doc cites "runner lines 250, 255" — confirmed.
- **PASS**

**B7-CHECK: Hypothesis Test**

Doc: one-tailed beta > 0; `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2`; *** p<0.01, ** p<0.05, * p<0.10.
Runner line 279: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` — exact match.
Runner `_sig_stars()` lines 292-297: `if p < 0.01: return "***"`, `if p < 0.05: return "**"`, `if p < 0.10: return "*"` — exact match.
- **PASS**

**Phase 3 verdict: 7/7 PASS.**

---

## PHASE 4: SPEC REGISTER (Section C)

Runner MODEL_SPECS (lines 92-100), 6 entries:

| Col | Code DV | Code fe | Code controls |
|---|---|---|---|
| 1 | delta_amihud | industry | base |
| 2 | delta_amihud | firm | base |
| 3 | delta_amihud | industry | extended |
| 4 | delta_amihud | firm | extended |
| 5 | delta_amihud | industry_yq | extended |
| 6 | delta_amihud | firm_yq | extended |

Doc spec register (6 rows):

| Col | Doc DV | Doc Entity FE | Doc Time FE | Doc Controls |
|---|---|---|---|---|
| 1 | delta_amihud | Industry (FF12) | Cal Yr | Base (8) |
| 2 | delta_amihud | Firm | Cal Yr | Base (8) |
| 3 | delta_amihud | Industry (FF12) | Cal Yr | Extended (12) |
| 4 | delta_amihud | Firm | Cal Yr | Extended (12) |
| 5 | delta_amihud | Industry (FF12) | Cal Yr-Qtr | Extended (12) |
| 6 | delta_amihud | Firm | Cal Yr-Qtr | Extended (12) |

Row-by-row verification:
- Col 1: DV match, industry FE (`entity_effects=False, other_effects=ff12_code`), cal_yr, base. MATCH.
- Col 2: DV match, firm FE (`EntityEffects`), cal_yr, base. MATCH.
- Col 3: DV match, industry FE, cal_yr, extended. MATCH.
- Col 4: DV match, firm FE, cal_yr, extended. MATCH.
- Col 5: DV match, `industry_yq` → Industry FF12 + cal_yr_qtr, extended. MATCH.
- Col 6: DV match, `firm_yq` → Firm + cal_yr_qtr, extended. MATCH.

Notes in spec register verified:
- Col 1 note: "PanelOLS constructor: `entity_effects=False`, `time_effects=True`, `other_effects=ff12_code`" — confirmed lines 244-249. PASS.
- Col 2 note: "PanelOLS.from_formula: `EntityEffects + TimeEffects`" — confirmed lines 252-254. PASS.

Extended controls count: doc says 12. `len(EXTENDED_CONTROLS) = len(BASE_CONTROLS) + 4 = 8 + 4 = 12`. MATCH.

**Phase 4 verdict: 7/7 PASS.**

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

**D1-CHECK: Population**

Doc: `master_sample_manifest.parquet`, year range 2002-2018, unit = individual earnings call.

Evidence:
- Runner `load_panel()` loads `h7_illiquidity_panel.parquet` built from manifest.
- `AmihudChangeBuilder.build()` line 53-57 loads `master_sample_manifest.parquet` from `get_latest_output_dir()`.
- Project scope: 2002-2018, 112,968 calls, 2,429 firms — consistent.
- **PASS**

**D2-CHECK: Exclusion Criteria**

Step-by-step verification against runner code:

| Step | Doc Description | Runner Code |
|---|---|---|
| 1 | Full manifest | Panel builder loads all manifest rows for year range |
| 2 | Main sample (excl FF12=8,11) | `filter_main_sample()` lines 172-177: `~panel["ff12_code"].isin([8, 11])` |
| 3 | DV non-missing (delta_amihud) | `prepare_regression_data()` line 199: `df = df[df[dv].notna()]` |
| 4 | Complete case (all required vars non-NaN) | Lines 202-203: `complete_mask = df[required].notna().all(axis=1)` |
| 5 | Min calls per firm (>=5) | Lines 206-208: `firm_counts >= MIN_CALLS_PER_FIRM` where `MIN_CALLS_PER_FIRM = 5` |

All steps match.

Doc additionally notes: "Inf/-Inf values are replaced with NaN before filtering (runner line 193)."
**FAIL (minor line citation)**: Actual code is runner line 192: `df = df.replace([np.inf, -np.inf], np.nan)`. Line 193 is the start of the `for iv in KEY_IVS:` loop. The inf-replacement is at line 192, not 193.

**D3-CHECK: Sample Counts**

Doc correctly notes counts are runtime-dependent and defers to `sample_attrition.csv`. The attrition table generator is called at runner lines 470-475 with 4 stages: Full panel, Main sample, delta_amihud non-null, Complete-case + min-calls (col 1). This matches the doc's description of the 5-step cascade (the attrition table itself collapses steps 3-5 from D2 into a single "Complete-case + min-calls (col 1)" entry).

Runner line reference for attrition: "runner line 470--475" — confirmed.
- **PASS**

**Phase 5 verdict: 2/3 checks PASS; 1 FAIL (Inf-replacement line 193 should be 192).**

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

Verified all 17 rows:

**`delta_amihud` (DV)**
- Formula: PostAmihud - PreAmihud, daily_illiq = |RET|/(VOL*|PRC|)*1e6, Pre mean([-3,-1]), Post mean([+1,+3]).
- Code: `amihud_change.py` lines 317-319, 362-373. MATCH.
- Winsorized: "1%/99% by calendar year (at AmihudChangeBuilder level)" — lines 110-112: `winsorize_by_year(results, winsorize_cols, year_col="year", lower=0.01, upper=0.99)`. MATCH.
- Source: CRSPEngine via `get_raw_daily_data()`. MATCH.
- **PASS**

**`pre_call_amihud` (Control/Lagged DV proxy)**
- Formula: mean(daily_illiq for trading days [-3,-1]).
- Code: `amihud_change.py` pre_avg computation lines 362-365. MATCH.
- Winsorized: same as delta_amihud. MATCH.
- **PASS**

**`CEO_QA_Uncertainty_pct` (IV)**
- Formula: (uncertainty words by CEO in Q&A) / (total CEO words in Q&A) * 100.
- Source: LinguisticEngine. MATCH.
- Winsorized: "0%/99% upper-only per-year" — `_linguistic_engine.py` lines 254-258: `winsorize_by_year(combined, existing_pct_cols, year_col="year", lower=0.0, upper=0.99, min_obs=10)`. MATCH.
- **PASS**

**`CEO_Pres_Uncertainty_pct`, `Manager_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct` (IVs)**
- Same structure and source as CEO_QA_Uncertainty_pct. All verified through same LinguisticEngine path. MATCH.
- **PASS (3 variables)**

**`Size` (Control)**
- Formula: `ln(atq), for atq > 0; else NaN`.
- `_compustat_engine.py` line 943: `comp["Size"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)`. MATCH.
- Source: CompustatEngine: atq. MATCH.
- Winsorized: "1%/99% by fiscal year (at engine level)" — `_compute_and_winsorize()` lines 1229-1232 apply `_winsorize_by_year(comp[col], year_col)` where `year_col = comp["fyearq"]`. MATCH.
- **PASS**

**`TobinsQ` (Control)**
- Formula doc: `(cshoq * prccq + dlcq + dlttq) / atq; requires atq > 0 and mktcap non-missing`.
- Engine code (`_compustat_engine.py` lines 987-997):
  ```python
  mktcap = comp["cshoq"] * comp["prccq"]
  debt_c = comp["dlcq"].clip(lower=0).fillna(0)
  debt_t = comp["dlttq"].clip(lower=0).fillna(0)
  debt_book = np.where(comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t)
  comp["TobinsQ"] = np.where(atq>0 & mktcap.notna(), (mktcap + debt_book) / comp["atq"], np.nan)
  ```
- The simplified formula `(cshoq*prccq + dlcq + dlttq) / atq` is directionally correct but omits: (a) dlcq/dlttq are clipped to 0 (negative debt → 0), (b) both-NaN guard: if dlcq AND dlttq are both NaN, debt_book = NaN not 0. Section L.1 documents the full discrepancy including the builder docstring vs engine difference. Section B4 formula matches the engine code. The Section E formula is a reasonable summary.
- **PASS (with note about imprecision acknowledged in L.1)**

**`ROA` (Control)**
- Formula: `iby_annual (Q4) / avg_assets` where `avg_assets = (atq_t + atq_{t-1}) / 2`.
- Source: CompustatEngine: iby, atq. Annual via Q4 filing.
- Consistent with engine construction pattern. PASS.
- **PASS**

**`BookLev` (Control)**
- Formula: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq`.
- Engine: line 947 area — confirmed (dlcq + dlttq) / atq with fillna(0) treatment. MATCH.
- **PASS**

**`CapexAt` (Control)**
- Formula: `capxy_annual (Q4 only) / atq_lag (prior year Q4 total assets)`.
- Engine lines 999-1003: `capxy_annual / atq_annual_lag1`. MATCH.
- **PASS**

**`DividendPayer` (Control)**
- Formula: `1 if dvy_annual (Q4 only) > 0, else 0`. Not winsorized (binary).
- Consistent with engine construction. PASS.
- **PASS**

**`OCF_Volatility` (Control)**
- Formula: rolling 5-year std (min 3 yrs) of (oancfy / atq_{t-1}) per gvkey.
- Source: CompustatEngine: oancfy, atq. Rolling window via 1826-day dummy date approach.
- **PASS**

**`Volatility` (Control)**
- Formula: `std(daily RET) * sqrt(252) * 100` over inter-call window, min 10 trading days.
- Source: CRSPEngine `get_data()`. Winsorized 1%/99% by calendar year via `CRSP_RETURN_COLS` path (`_crsp_engine.py` lines 445-447).
- **PASS**

**`StockPrice` (Control)**
- Formula: PRC at call date or nearest prior trading day. Not winsorized.
- Source: CRSPEngine `get_raw_daily_data()`.
- **PASS**

**`Turnover` (Control)**
- Formula: `VOL / (SHROUT * 1000)` at call date. Not winsorized.
- Source: CRSPEngine `get_raw_daily_data()`.
- **PASS**

**`Analyst_QA_Uncertainty_pct` (Control/Extended)**
- Formula: (uncertainty words by analysts in Q&A) / (total analyst words in Q&A) * 100.
- Source: LinguisticEngine. Winsorized 0%/99% upper-only. MATCH.
- **PASS**

**`ff12_code` (FE)**
- FE column, static per firm. ManifestFieldsBuilder. PASS.

**`gvkey` (FE/Entity)**
- Entity FE. CompustatEngine / manifest. PASS.

**`cal_yr` (FE/Time)**
- Formula: `start_date.dt.year`. Derived via `build_cal_yr_qtr_index()`. PASS.

**`cal_yr_qtr` (FE/Time)**
- Formula: `cal_yr * 10 + start_date.dt.quarter`. `panel_utils.py` `build_cal_yr_qtr_index()` line 201: `cal_yr_qtr = cal_yr * 10 + cal_qtr`. MATCH.

**COMPLETENESS:**
- All 4 KEY_IVS: present ✓
- All 8 BASE_CONTROLS: present ✓
- All 4 extended-only controls: present ✓
- DV delta_amihud: present ✓
- FE columns (gvkey, ff12_code, cal_yr, cal_yr_qtr): present ✓
- No regression variable missing from the dictionary.

**ISSUE: Compustat winsorization line citation in H1 (also relevant to E)**
Section E states "1%/99% by fiscal year (at engine level)" for Compustat controls, which is correct conceptually. The specific line citation error (1134 vs 1232) is in Section H1, not in Section E itself. Section E does not cite a specific line number. No error in E.

**Phase 6 verdict: 17/18 checks PASS; 1 borderline (TobinsQ formula simplified but conceptually documented in L.1).**

Formally: **17/18 PASS** (treating TobinsQ formula imprecision as a minor imprecision, not a factual error, since L.1 documents the exact code).

---

## PHASE 7: PIPELINE, OUTPUTS, TREATMENT (Sections F, G, H)

### F-CHECK: Data Pipeline

**F1 Dependency Chain — Step-by-step verification:**

Step 1 (Raw inputs): Doc lists CRSP_DSF parquets, comp_na_daily_all.parquet, CRSPCompustat_CCM.parquet, linguistic variables, master_sample_manifest.parquet. All confirmed by builder import paths and engine source references. **PASS.**

Step 2 (Engine loading): CompustatEngine, CRSPEngine, LinguisticEngine. All 3 confirmed in builder's import block. **PASS.**

Step 3 (Panel builder): Doc says "merges all on file_name (left join, zero row-delta enforced)." Builder `build_panel()` lines 126-143 iterates all builder results, merges on `file_name` with `how="left"`, raises `ValueError` if `delta != 0`. MATCH. **PASS.**

Step 4 (Runner loading): **FAIL.** Doc says "selecting 21 columns." Runner `load_panel()` lines 149-159:
```python
columns = [
    "start_date",                                          # 1
    "gvkey", "year", "fyearq_int", "ff12_code",           # 2-5
    "delta_amihud", "pre_call_amihud",                    # 6-7
    "CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct", # 8-9
    "Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct", # 10-11
    "Size", "TobinsQ", "ROA", "BookLev", "CapexAt",       # 12-16
    "DividendPayer", "OCF_Volatility",                    # 17-18
    "Volatility", "StockPrice", "Turnover",               # 19-21
    "Analyst_QA_Uncertainty_pct",                         # 22
]
```
Count = **22 columns**, not 21.

Step 5 (Sample filtering): Main sample filter → inf replace → DV filter → complete case → min calls. Matches doc description. **PASS.**

Step 6 (Regression): PanelOLS, 6 specs, one-tailed p-values. **PASS.**

Step 7 (Table generation): generate_all_tables.py entry documented. **PASS.**

**F2 Data Engines (4 engines):**

| Engine | Source | Variables |
|---|---|---|
| CompustatEngine | comp_na_daily_all.parquet | Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility |
| CRSPEngine (get_data) | CRSP_DSF parquets | Volatility |
| CRSPEngine (get_raw_daily_data) | CRSP_DSF parquets | delta_amihud, pre_call_amihud, StockPrice, Turnover |
| LinguisticEngine | linguistic_variables_{year}.parquet | 4 IVs + Analyst_QA_Uncertainty_pct |

Doc lists exactly these 4 engines. Verified against builder imports and builder code. **PASS.**

**F3 Merge Operations:**

Builder `build_panel()` iterates the `builders` dict (lines 85-115), 16 builders excluding manifest. Doc table lists 16 merges. Verified all on `file_name`, all `how="left"`, all zero-row-delta enforced. MATCH.

Internal AmihudChangeBuilder merges: manifest → CCM (on gvkey, left), then year_calls → year_crsp (on permno_int=PERMNO, inner). Doc documents both. **PASS.**

### G-CHECK: Outputs

**G1 Stage 3 outputs (4 files listed):**
1. `h7_illiquidity_panel.parquet` — builder line 159: `panel.to_parquet(panel_path, index=False)`. ✓
2. `summary_stats.csv` — builder line 167: `stats_df.to_csv(stats_path, index=False)`. ✓
3. `run_manifest.json` — `generate_manifest()` call at lines 172-182. ✓
4. `report_step3_h7.md` — `generate_report()` line 201: `out_dir / "report_step3_h7.md"`. ✓
- **PASS**

**G2 Stage 4 outputs (9 files listed) — full cross-check against runner:**

Runner actually writes:
1. `h7_illiquidity_table.tex` — line 378 (`open(out_dir / "h7_illiquidity_table.tex", ...)`) ✓
2. `regression_results_col{1-6}.txt` — line 392 (loop over results) ✓
3. `model_diagnostics.csv` — line 400 (`diag_df.to_csv(out_dir / "model_diagnostics.csv", ...)`) ✓
4. `summary_stats.csv` — line 446 (`output_csv=out_dir / "summary_stats.csv"`) ✓
5. `summary_stats.tex` — line 447 (`output_tex=out_dir / "summary_stats.tex"`) ✓
6. `sample_attrition.csv` — via `generate_attrition_table()` (lines 470-475) → `attrition_table.py` line 48 ✓
7. `sample_attrition.tex` — same call → `attrition_table.py` line 52 ✓
8. `report_step4_H7.md` — line 486 (`open(out_dir / "report_step4_H7.md", ...)`) ✓
9. `run_manifest.json` — `generate_manifest()` lines 477-483 ✓

Doc lists all 9 files. No file in doc that runner does NOT write. No file written by runner that is missing from doc. **PASS.**

**G3 Summary Statistics (14 variables):**
Runner `SUMMARY_STATS_VARS` (lines 110-124): 14 entries. Doc lists all 14 with matching labels. Doc correctly notes (Section L, note 6) that StockPrice and Turnover are omitted. **PASS.**

### H-CHECK: Outlier/Missing Treatment

**H1 Winsorization:**

*Compustat variables:*
Doc: "Level: 1%/99% by fiscal year — Applied at: CompustatEngine level (`_winsorize_by_year` in `_compustat_engine.py`, line 1134) — Min obs per year group: 10"

**FAIL**: Line 1134 in `_compustat_engine.py` is inside `_net_equity_raw` computation (part of `ExternalFunding`/`DebtChoice` code), not `_winsorize_by_year`. The correct references are:
- Function definition: `_compustat_engine.py` line 444 (`def _winsorize_by_year(...)`)
- Application to all Compustat variables: `_compustat_engine.py` line 1232 (`comp[col] = _winsorize_by_year(comp[col], year_col)`)

The min_obs threshold of 10 is correct (`_winsorize_by_year` signature line 445: `min_obs: int = 10`). The level 1%/99% and by-fiscal-year grouping are correct. Only the line citation is wrong.

*CRSP variables (Volatility):*
Doc: "Applied at: CRSPEngine `get_data()` level (`winsorize_by_year` in `_crsp_engine.py`, line 445)"
Code: `_crsp_engine.py` line 445: `result_with_year = winsorize_by_year(result_with_year, CRSP_RETURN_COLS, year_col="year")`. MATCH. **PASS.**

*DV and pre-call control:*
Doc: "Applied at: AmihudChangeBuilder level (`amihud_change.py`, lines 106--112)"
Code: lines 110-112: `results = winsorize_by_year(results, winsorize_cols, year_col="year", lower=0.01, upper=0.99)`. Lines 106-112 span the import and setup; the actual call is 110-112. Close enough — substance is correct. **PASS.**

*Linguistic IVs:*
Doc: "0%/99% upper-only per-year winsorization at LinguisticEngine level (`_linguistic_engine.py` lines 254-258)"
Code: lines 254-258: `combined = winsorize_by_year(combined, existing_pct_cols, year_col="year", lower=0.0, upper=0.99, min_obs=10)`. EXACT MATCH. **PASS.**

**H2 Missing Data Policy:**
- Complete-case deletion: runner line 202-203. Doc says "line 203" — technically line 203 is `df = df[complete_mask].copy()` (the application), while 202 is the mask. Acceptable.
- Inf/-Inf replaced: runner line 192. Doc says "line 193". **FAIL** (off by 1).
- Min valid trading days: `amihud_change.py` MIN_PRE_DAYS=2, MIN_POST_DAYS=2, `min_pre = max(1, w-1)` = 2. MATCH.
- Dollar volume zero → NaN: `amihud_change.py` line 318. Doc cites line 318. MATCH. **PASS.**

**H3 Transformations:**
- Size = ln(atq). Correct.
- No centering/z-scoring. Correct.
- 1e6 scaling for Amihud. Correct.
- **PASS.**

**Phase 7 verdict: 6/9 checks fully PASS; 3 failures:**
1. F1 Step 4: "21 columns" should be "22 columns"
2. H1 Compustat: winsorize line "1134" should be "1232"
3. H2: Inf-replacement "line 193" should be "line 192"

---

## PHASE 8: TABLE GENERATOR ENTRY (Section I)

**Actual entry in `generate_all_tables.py`** (located by manual inspection):
```
Line 164: # ── H7 ──
Line 165: {
Line 166:     "id": "H7",
Line 167:     "dir": "h7_illiquidity/2026-03-27_094957",
Line 168:     "caption": "H7: Speech Uncertainty and Post-Call Illiquidity",
Line 169:     "label": "tab:h7",
Line 170:     "cols": 6,
Line 171:     "dvs": [
Line 172:         (r"delta\_amihud", 6),
Line 173:     ],
Line 174:     "tail": "one",
Line 175:     "hyp_dir": ">",
Line 176: },
```

**Provenance doc (Section I) claims the block with "Source: lines 183--195":**

Content comparison:
- `"id": "H7"` — doc: ✓ MATCH
- `"dir": "h7_illiquidity/2026-03-27_094957"` — doc: ✓ MATCH
- `"caption": "H7: Speech Uncertainty and Post-Call Illiquidity"` — doc: ✓ MATCH
- `"label": "tab:h7"` — doc: ✓ MATCH
- `"cols": 6` — doc: ✓ MATCH
- `"dvs": [(r"delta\_amihud", 6)]` — doc: ✓ MATCH
- `"tail": "one"` — doc: ✓ MATCH
- `"hyp_dir": ">"` — doc: ✓ MATCH

All 5 content fields (id, tail, cols, dvs, hyp_dir) verified PASS.

**Verification bullets in doc:**
- `tail: "one"` and `hyp_dir: ">"` match runner one-tailed beta>0 — PASS.
- `cols: 6` matches `len(MODEL_SPECS) = 6` — PASS.
- `dvs: [("delta_amihud", 6)]` matches single DV across all 6 specs — PASS.
- No `key_vars` field — confirmed: entry has no `key_vars` key. PASS.

**FAIL — line range citation:**
Doc states: "Source: `outputs/generate_all_tables.py`, lines 183--195."
Actual location: lines 164–176. Lines 183–195 are the start of the H11 entry (`"label": "tab:h11"` at line 183, `"cols": 4` at line 184, etc.). The doc is citing the wrong entry entirely.

**Phase 8 verdict: 4/5 checks PASS; 1 FAIL (line range 183-195 should be 164-176).**

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

**K1 PanelOLS Specifics — Industry FE specs:**

Doc claims:
- `entity_effects=False` — runner line 246: confirmed ✓
- `time_effects=True` — runner line 246: confirmed ✓
- `other_effects=df_panel["ff12_code"]` — runner line 247: confirmed ✓
- `drop_absorbed=True` — runner line 248: confirmed ✓
- `check_rank=False` — runner line 248: confirmed ✓
- Fitted via `model_obj.fit(cov_type="clustered", cluster_entity=True)` — runner line 250: confirmed ✓
- Source: "runner lines 244--250" — lines 244-250 span the `if base_fe == "industry":` block. Confirmed.
- **PASS**

**K1 PanelOLS Specifics — Firm FE specs:**

Doc claims:
- `PanelOLS.from_formula()` with `EntityEffects + TimeEffects` — runner lines 252-254: confirmed ✓
- Formula: `"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` — runner line 253: confirmed ✓
- `drop_absorbed=True` — runner line 254: confirmed ✓
- Fitted via `model_obj.fit(cov_type="clustered", cluster_entity=True)` — runner line 255: confirmed ✓
- Source: "runner lines 253--255" — confirmed ✓
- **PASS**

**Panel index:**
- "Cols 1--4: `df_prepared.set_index(["gvkey", "cal_yr"])`" — confirmed via `time_col = "cal_yr"` (for non-`_yq` specs) at line 231, used at line 240. ✓
- "Cols 5--6: `df_prepared.set_index(["gvkey", "cal_yr_qtr"])`" — confirmed via `time_col = "cal_yr_qtr"` (for `_yq` specs). ✓
- "Source: runner line 240" — confirmed: `df_panel = df_prepared.set_index(["gvkey", time_col])`. ✓
- **PASS**

**R-squared reporting:**
- `model.rsquared` (overall, not within) — runner line 268: `"r2": float(model.rsquared)`. ✓
- Adj R2: `1 - (1 - R2) * (nobs - 1) / df_resid` — runner lines 269-270: `"adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`. ✓
- "Source: runner lines 262, 269--270" — line 262 is the print statement; lines 269-270 are the meta dict. Confirmed. ✓
- **PASS**

**Singleton handling:** "PanelOLS default behavior with `drop_absorbed=True`" — correct, no explicit singleton handling beyond PanelOLS defaults. **PASS.**

**K2-K6: All N/A** — confirmed these are the non-applicable model families. Correct since suite uses PanelOLS. **PASS.**

**Phase 9 verdict: 6/6 PASS.**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|---|---|---|
| 1 | Every variable in every regression spec in Variable Dictionary with explicit formula and source engine | PASS | All 4 IVs, 12 controls (8 base + 4 extended), 1 DV, 4 FE columns present; formulas explicit for all; TobinsQ formula simplified but documented in L.1 |
| 2 | Model equation matches what the code actually estimates | PASS | Verified against KEY_IVS, BASE_CONTROLS, EXTENDED_CONTROLS, FE implementation |
| 3 | Specification register accounts for every model column | PASS | 6 rows = 6 MODEL_SPECS, all fields verified against code |
| 4 | Attrition cascade has row counts for each filter step | FAIL | All 5 attrition cascade steps have [UNVERIFIED] counts. Doc correctly marks and explains: "Row counts are runtime-dependent...Fill from sample_attrition.csv." The quality gate strictly requires counts; [UNVERIFIED] is the correct approach when counts are unavailable pre-run but is still technically a gap |
| 5 | Tail test direction matches between runner code and generate_all_tables.py | PASS | Runner: `p_one = p_two / 2 if beta > 0` (one-tailed, positive direction); generate_all_tables.py: `"tail": "one", "hyp_dir": ">"` |
| 6 | FE specification matches between docstring, code, and this document | PASS | Runner code confirmed; doc matches code; runner docstring stale but correctly noted in L.9 |
| 7 | Every merge in panel builder documented with join keys and type | PASS | 16 builder merges + 2 internal AmihudChange merges, all with keys (file_name/gvkey/permno_int) and types (left/inner) |
| 8 | Output file list matches what runner actually writes | PASS | 9 files in G2 = 9 files confirmed written |
| 9 | Model-family addendum filled for correct family only | PASS | K1 (PanelOLS) filled; K2-K6 = N/A |
| 10 | Any claim marked [UNVERIFIED] has explanation of what blocks verification | PASS | D2 attrition counts: "runtime-dependent and vary per specification...Fill from sample_attrition.csv in Stage 4 output directory after runtime execution" |

**Phase 10 verdict: 9/10 checks PASS; 1 borderline FAIL (QG4: attrition counts all [UNVERIFIED]).**

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

1. **DVs in B2 vs C**: B2 table: `delta_amihud`. C register: all 6 rows have `delta_amihud`. CONSISTENT ✓
2. **DVs in C vs I**: C: `delta_amihud` (6 specs). I: `"dvs": [(r"delta\_amihud", 6)]`. CONSISTENT ✓
3. **Controls in B4 vs E**: B4 lists 8 base + 4 extended = 12 controls. Section E contains all 12 as `Control` type rows. CONSISTENT ✓
4. **Column count A vs C**: A: `Columns: 6`. C: 6 rows. CONSISTENT ✓
5. **Column count A vs I**: A: `Columns: 6`. I: `"cols": 6`. CONSISTENT ✓
6. **Tail direction A vs B7 vs I**: A: "one-tailed beta > 0". B7: "one-tailed (beta > 0)". I: `"tail": "one", "hyp_dir": ">"`. CONSISTENT ✓
7. **FE in B5 vs C vs K1**: B5 table: Industry(ff12_code) for cols 1,3,5; Firm(gvkey) for cols 2,4,6; cal_yr for cols 1-4; cal_yr_qtr for cols 5-6. C notes confirm same structure. K1 details confirm implementation. CONSISTENT ✓
8. **Panel index in A vs K**: A: `(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6`. K1: "Cols 1–4: `set_index(["gvkey", "cal_yr"])`; Cols 5–6: `set_index(["gvkey", "cal_yr_qtr"])`". CONSISTENT ✓

**Phase 11 verdict: 8/8 PASS. No internal contradictions found.**

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|---|---|---|---|---|---|
| Phase 5 / D2 | Inf-replacement line number | "runner line 193" | `df = df.replace([np.inf, -np.inf], np.nan)` is at runner **line 192** | Low | Change "line 193" to "line 192" in Section H2 and D2 note |
| Phase 6/7 / H1 | Compustat winsorization line citation | "`_winsorize_by_year` in `_compustat_engine.py`, line 1134" | Function defined at line 444; bulk application loop at **line 1232** (`comp[col] = _winsorize_by_year(comp[col], year_col)`). Line 1134 is unrelated `_net_equity_raw` code. | Medium | Change "line 1134" to "line 1232" in Section H1 |
| Phase 7 / F1 | Runner column count | "selecting 21 columns" | Runner `load_panel()` lines 149-159 selects **22 columns** | Low | Change "21 columns" to "22 columns" in Section F1 Step 4 |
| Phase 8 / I | generate_all_tables.py line range | "lines 183--195" | H7 entry is at **lines 164--176**. Lines 183-195 contain the H11 entry. | Low | Change "lines 183--195" to "lines 164--176" in Section I |

---

## CORRECTIONS REQUIRED

**Correction 1: Section H1, Compustat variables paragraph**
- Location: Section H ("Outlier and Missing Data Treatment") → H1 → "Compustat variables" paragraph → second bullet
- Current text: `Applied at: CompustatEngine level (\`_winsorize_by_year\` in \`_compustat_engine.py\`, line 1134)`
- Correct text: `Applied at: CompustatEngine level (\`_winsorize_by_year\` in \`_compustat_engine.py\`, line 1232 — bulk loop in \`_compute_and_winsorize()\` applying per-year 1%/99% to all \`COMPUSTAT_COLS\`)`
- Proof: `_compustat_engine.py` line 1232: `comp[col] = _winsorize_by_year(comp[col], year_col)` inside the `for col in winsorize_cols:` loop at lines 1230-1232. Line 1134 is inside the `_net_equity_raw` computation (prstkcy subtraction).

**Correction 2: Section H2, Missing Data Policy, second bullet**
- Location: Section H → H2 → second bullet
- Current text: `Inf/-Inf replaced with NaN before regression (\`prepare_regression_data()\` line 193)`
- Correct text: `Inf/-Inf replaced with NaN before regression (\`prepare_regression_data()\` line 192)`
- Proof: `run_h7_illiquidity.py` line 192: `df = df.replace([np.inf, -np.inf], np.nan)`. Line 193 is `for iv in KEY_IVS:`.

**Correction 3: Section F1, Step 4**
- Location: Section F ("Data Pipeline") → F1 → Step 4 ("Runner loading")
- Current text: `Loads panel parquet, selecting 21 columns`
- Correct text: `Loads panel parquet, selecting 22 columns`
- Proof: `run_h7_illiquidity.py` lines 149-159 define `columns = [...]` with 22 entries: start_date, gvkey, year, fyearq_int, ff12_code, delta_amihud, pre_call_amihud, CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, Volatility, StockPrice, Turnover, Analyst_QA_Uncertainty_pct.

**Correction 4: Section I, source citation line**
- Location: Section I ("generate_all_tables.py Entry") → line immediately after the Python code block
- Current text: `Source: \`outputs/generate_all_tables.py\`, lines 183--195.`
- Correct text: `Source: \`outputs/generate_all_tables.py\`, lines 164--176.`
- Proof: `generate_all_tables.py` lines 164-176 contain the H7 entry (`# ── H7 ──` comment at 164, opening brace at 165, closing brace with trailing comma at 176). Lines 183-195 contain the H11 entry (`"label": "tab:h11"` at line 183).

---

## ADDITIONAL NOTES (not failures)

**Note 1: Stale runner docstring**
The runner docstring (lines 7-11) says "4 model specifications" and "4 columns in one table" but MODEL_SPECS has 6 entries. Correctly flagged in provenance doc Section L, note 9. Not a provenance doc error.

**Note 2: TobinsQ formula precision**
Section E simplifies TobinsQ to `(cshoq*prccq + dlcq + dlttq) / atq`. The engine code clips dlcq/dlttq to 0 (via `.clip(lower=0)`) and applies a both-NaN guard. This detail is documented in Section L.1. Acceptable as a summary-level formula in E.

**Note 3: Attrition counts all [UNVERIFIED]**
Correctly marked with explanation. Cannot be verified without pipeline execution. This is a structural limitation of documenting a pipeline before running it, not an error.

**Note 4: SUMMARY_STATS_VARS omits StockPrice and Turnover**
Correctly documented in Section L, note 6. The 14-variable list is consistent with runner code.

**Note 5: No `key_vars` field in generate_all_tables.py entry**
Correctly documented: "No `key_vars` field — uses standard 4-IV layout (default table generator behavior)." Verified: actual entry has no `key_vars` key.

---

*End of H7 Provenance Audit — 2026-04-01*
