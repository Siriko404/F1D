# ADVERSARIAL AUDIT REPORT — H11-Lag Provenance Document

**Audit Date:** 2026-04-01
**Auditor:** Hostile adversarial auditor (Claude Sonnet 4.6)
**Suite ID:** H11-Lag
**Provenance Doc:** docs/provenance/H11-Lag.md
**Runner:** src/f1d/econometric/run_h11_prisk_uncertainty_lag.py
**Panel Builder:** src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py
**Method:** Manual line-by-line code reading. Every factual claim verified against source.

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 26 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 6 | 1 | 86% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 3 | 0 | 100% |
| Variable Dictionary (Phase 6) | 17 | 16 | 1 | 94% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 8 | 1 | 89% |
| Table Generator Entry (Phase 8) | 5 | 5 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 5 | 5 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **105** | **101** | **3** | **96%** |

---

## VERDICT

**PASS WITH NOTES**

Three issues found, none affecting structural completeness or spec-register accuracy. Two are factual errors about the TobinsQ formula (duplicated across B4 and E). One is an omission from Known Issues: the runner's LaTeX footnote falsely claims standardization when no standardization code exists anywhere in the runner.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Reading the creation prompt (Suite Provenance Doc.txt) to extract all required sections.

Required sections per prompt: A (Suite Identity), B (B1–B7), C (Spec Register), D (D1–D3), E (Variable Dictionary), F (F1–F3), G (G1–G3), H (H1–H3), I (generate_all_tables Entry), J (Reproduction Commands), K (K1–K6), L (Known Issues).

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block present with all required fields |
| B. Model Specification | Yes | Yes | Yes | Present with all subsections |
| B1. Regression Equation | Yes | Yes | Yes | Two equations for QA DVs and Pres DVs |
| B2. Dependent Variable(s) | Yes | Yes | Yes | 4 DVs with full table |
| B3. Independent Variable(s) | Yes | Yes | Yes | 2 IVs with full table |
| B4. Control Variables | Yes | Yes | Yes | 9 base controls + dynamic Pres control map |
| B5. Fixed Effects | Yes | Yes | Yes | Entity (gvkey) + Time (year) documented |
| B6. Standard Errors | Yes | Yes | Yes | clustered, cluster_entity=True |
| B7. Hypothesis Test | Yes | Yes | Yes | One-tailed beta > 0; p computation documented |
| C. Spec Register | Yes | Yes | Yes | 8-row table covering all 8 columns |
| D. Sample Construction | Yes | Yes | Yes | All subsections present |
| D1. Population | Yes | Yes | Yes | 112,968 calls, ~2,429 firms, 2002–2018 |
| D2. Exclusion Criteria | Yes | Yes | Yes | 6-step attrition cascade with [RUNTIME] counts |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Documented as varying by DV/IV |
| E. Variable Dictionary | Yes | Yes | Yes | 17-row table |
| F. Data Pipeline | Yes | Yes | Yes | All subsections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 4 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | 16 merges documented |
| G. Outputs | Yes | Yes | Yes | All subsections present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 8 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 15 variables listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1–H3 present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Full Python dict reproduced verbatim |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled; K2–K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 7 items documented |

**Phase 1 Result: PASS — all 26 required structural elements are present and complete.**

---

## PHASE 2: SUITE IDENTITY (Section A)

### A-1. Suite ID
- Doc: `H11-Lag`
- File name: `H11-Lag.md`; runner module: `run_h11_prisk_uncertainty_lag.py`
- **PASS**

### A-2. Title
- Doc: `H11-Lag: Lagged Political Risk and Language Uncertainty`
- generate_all_tables.py line 204: `"caption": "H11-Lag: Lagged Political Risk and Language Uncertainty"` — exact match.
- Runner docstring title (lines 4–5): `"STAGE 4: Test H11-Lag Political Risk (Lagged) - Language Uncertainty Hypothesis"` — different phrasing but same content.
- **PASS**

### A-3. Hypothesis
- Doc: "Higher political risk in quarter t-1 (and t-2) is associated with higher language uncertainty in subsequent earnings calls."
- Runner docstring lines 32–34: `"H11-Lag: beta(PRisk_lag) > 0 -- higher prior-quarter political risk increases speech uncertainty"` and `"H11-Lag2: beta(PRisk_lag2) > 0 -- higher 2-quarter prior political risk increases speech uncertainty"`
- **PASS — consistent**

### A-4. Direction (tail test)
- Doc: `One-tailed (beta > 0)`
- Runner line 221: `p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2`
- Runner line 225: `h_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0`
- **PASS**

### A-5. Model Family
- Doc: `Linear panel regression with absorbed fixed effects`
- Runner imports `from linearmodels.panel import PanelOLS` (line 75) and instantiates it.
- **PASS**

### A-6. Estimator
- Doc: `linearmodels.panel.PanelOLS`
- Runner line 75: `from linearmodels.panel import PanelOLS`; line 203: `PanelOLS.from_formula(...)`
- **PASS**

### A-7. Unit of Observation
- Doc: `Individual earnings call (file_name)`
- Panel builder docstring line 16: `"Unit of observation: the individual earnings call (file_name)."`
- **PASS**

### A-8. Panel Index
- Doc: `(gvkey, year) -- year = calendar year from start_date`
- Runner line 200: `df_panel = df_sample.set_index(["gvkey", "year"])`
- Panel builder line 151: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year`
- **PASS**

### A-9. Columns
- Doc: `8 (in generate_all_tables.py); runner also produces Finance and Utility sub-sample regressions (24 total regressions)`
- Runner CONFIG: 4 DVs × 2 IVs × 3 samples = 24 max regressions; only Main sample 4×2=8 in generate_all_tables.py.
- **PASS**

### A-10. Runner and Panel Builder paths
- Both files verified to exist on disk at the stated paths.
- **PASS**

**Phase 2 Summary: 10/10 PASS**

---

## PHASE 3: MODEL SPECIFICATION (Section B)

### B1-CHECK: Regression Equation
- Doc provides two equations: QA DVs (with Pres control) and Pres DVs (without Pres control).
- Runner formula construction (lines 184–188):
  ```python
  formula = f"{dv_var} ~ 1 + {iv_var} + " + " + ".join(controls) + " + EntityEffects + TimeEffects"
  ```
  where `controls` = BASE_CONTROLS + pres_control (for QA DVs) or BASE_CONTROLS alone (for Pres DVs).
- The split into two equations is correct and accurately reflects the code's PRES_CONTROL_MAP logic.
- **PASS**

### B2-CHECK: Dependent Variable(s)
All 4 DVs verified:

1. `UncAnsMgr` — runner line 91 (CONFIG); runner load line 454; panel builder ManagerQAUncertaintyBuilder line 87. **PASS**
2. `UncAnsCEO` — runner line 92; load line 455; panel builder CEOQAUncertaintyBuilder line 90. **PASS**
3. `UncPreMgr` — runner line 93; load line 456; panel builder ManagerPresUncertaintyBuilder line 93. **PASS**
4. `UncPreCEO` — runner line 94; load line 457; panel builder CEOPresUncertaintyBuilder line 96. **PASS**

Timing (contemporaneous call-level), source (LinguisticEngine), and formula description verified against LinguisticEngine builder pattern. **PASS**

### B3-CHECK: Independent Variable(s)
1. `PRisk_lag`:
   - Runner CONFIG["iv_vars"] line 97: `"PRisk_lag"`. Runner loads at line 459. **PASS**
   - Source file: `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (prisk_q_lag.py line 40). **PASS**
   - Lag mechanism: manifest `cal_q_lag = _get_prev_quarter(cal_q)` merged to PRisk `cal_q` (prisk_q_lag.py lines 156, 169–175). **PASS**
   - Output column `PRisk_lag` (prisk_q_lag.py line 178). **PASS**

2. `PRisk_lag2`:
   - Same structure; 2-quarter lag via `_get_prev2_quarter` (prisk_q_lag2.py line 64–80). **PASS**
   - Output column `PRisk_lag2` (prisk_q_lag2.py line 181). **PASS**

### B4-CHECK: Control Variables
BASE_CONTROLS (runner lines 100–110) — 9 controls:
```
UncQue, NegCall, lnAssets, TobinsQ, ROA,
CashRatio, DivDummy, FirmMat, EarnVol
```
Provenance doc B4 base controls table lists exactly these 9 variables. **PASS**

PRES_CONTROL_MAP (runner lines 112–117):
```python
"UncAnsMgr": "UncPreMgr",
"UncAnsCEO": "UncPreCEO",
"UncPreMgr": None,
"UncPreCEO": None,
```
Doc's Dynamic Presentation Control sub-table matches exactly. **PASS**

No Lagged_DV: confirmed — absent from BASE_CONTROLS and all formulas. **PASS**

**TobinsQ formula — FAIL:**

Doc B4 formula: `(cshoq * prccq + dlcq + dlttq) / atq`

Actual code (`_compustat_engine.py` lines 987–997):
```python
mktcap = comp["cshoq"] * comp["prccq"]
debt_c = comp["dlcq"].clip(lower=0).fillna(0)        # negative dlcq clamped to 0; NaN → 0
debt_t = comp["dlttq"].clip(lower=0).fillna(0)       # negative dlttq clamped to 0; NaN → 0
debt_book = np.where(
    comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t
)                                                     # NaN only if BOTH are NaN
comp["TobinsQ"] = np.where(
    comp["atq"].notna() & (comp["atq"] > 0) & mktcap.notna(),
    (mktcap + debt_book) / comp["atq"],
    np.nan,
)
```

The documented formula omits: (a) lower-clipping of debt components at 0, (b) fillna(0) when only one debt component is missing, (c) the specific NaN propagation rule (NaN only if BOTH dlcq and dlttq are missing). These are material details that affect the actual computed values.

**FAIL — B4 TobinsQ formula description is inaccurate**

### B5-CHECK: Fixed Effects
- Doc: Entity = `gvkey` (Firm FE via EntityEffects), Time = `year` (Cal Year FE via TimeEffects)
- Runner line 200: `set_index(["gvkey", "year"])`; line 203: formula includes `EntityEffects + TimeEffects`
- Panel builder line 151: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year` (calendar year)
- **PASS**

### B6-CHECK: Standard Errors
- Doc: `cov_type="clustered"`, `cluster_entity=True`, cluster = gvkey
- Runner line 204: `model_obj.fit(cov_type="clustered", cluster_entity=True)`
- **PASS**

### B7-CHECK: Hypothesis Test
- Doc: one-tailed beta > 0; `p_one = p_two/2 if beta > 0 else 1 - p_two/2`; confirmed at `p_one < 0.05 AND beta > 0`
- Runner lines 220–225: exact match.
- Stars at fmt_coef (lines 287–291): `pval < 0.01 → ***; pval < 0.05 → **; pval < 0.10 → *`. Stars use `p_one` values (lines 323–326). **PASS**

**Phase 3 Summary: 6/7 PASS (TobinsQ formula fails)**

---

## PHASE 4: SPEC REGISTER (Section C)

### Row count
- Doc: 8 rows. Code: 4 DVs × 2 IVs = 8 main-sample specs. **PASS**

### Column-by-column verification against code

Runner outer loop = CONFIG["iv_vars"] (PRisk_lag first, then PRisk_lag2); inner = CONFIG["dependent_variables"] (4 DVs in declared order); sample filter = Main. File suffix = "lag1" or "lag2".

| Col | DV (Doc) | DV (Code) | IV (Doc) | IV (Code) | Entity FE | Time FE | Controls (Doc) | Match? |
|-----|---------|----------|---------|----------|-----------|---------|----------------|--------|
| 1 | UncAnsMgr | UncAnsMgr | PRisk_lag | PRisk_lag | Firm | Cal Year | Base + Mgr Pres | PASS |
| 2 | UncAnsCEO | UncAnsCEO | PRisk_lag | PRisk_lag | Firm | Cal Year | Base + CEO Pres | PASS |
| 3 | UncPreMgr | UncPreMgr | PRisk_lag | PRisk_lag | Firm | Cal Year | Base only | PASS |
| 4 | UncPreCEO | UncPreCEO | PRisk_lag | PRisk_lag | Firm | Cal Year | Base only | PASS |
| 5 | UncAnsMgr | UncAnsMgr | PRisk_lag2 | PRisk_lag2 | Firm | Cal Year | Base + Mgr Pres | PASS |
| 6 | UncAnsCEO | UncAnsCEO | PRisk_lag2 | PRisk_lag2 | Firm | Cal Year | Base + CEO Pres | PASS |
| 7 | UncPreMgr | UncPreMgr | PRisk_lag2 | PRisk_lag2 | Firm | Cal Year | Base only | PASS |
| 8 | UncPreCEO | UncPreCEO | PRisk_lag2 | PRisk_lag2 | Firm | Cal Year | Base only | PASS |

The generate_all_tables.py col_files (lines 207–215) confirm this exact DV-IV-lag ordering.

**Phase 4 Summary: 5/5 PASS**

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

### D1-CHECK: Population
- Doc: 112,968 calls, ~2,429 firms, 2002–2018
- Project scope (MEMORY): 112,968 calls, 2,429 firms, 2002–2018. **PASS**

### D2-CHECK: Exclusion Criteria
Provenance doc 6-step attrition cascade:

| Step | Filter described | Code reference | Match? |
|------|-----------------|----------------|--------|
| 1 | Full manifest loaded | runner line 446: `pd.read_parquet(panel_file, columns=[...])` | PASS |
| 2 | Industry sample assignment | panel builder line 150: `assign_industry_sample(panel["ff12_code"])` | PASS |
| 3 | Sample selection (Main/Finance/Utility) | runner lines 519–524 | PASS |
| 4 | Complete case (inf→NaN, dropna) | runner line 172: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required)` | PASS |
| 5 | Min calls per firm ≥ 5 | runner lines 526–531: `gvkey_count >= CONFIG["min_calls"]` (= 5) | PASS |
| 6 | Min 100 rows check (skip if insufficient) | runner line 537: `if len(df_filtered) < 100: continue` | PASS |

Row counts [RUNTIME] with explanation — acceptable per project policy. **PASS**

### D3-CHECK: Sample Counts per Spec
- Doc notes N varies by DV/IV combination; tracked in `model_diagnostics.csv` (runner line 556). **PASS**

**Phase 5 Summary: 3/3 PASS**

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

Checking all 17 rows.

### Linguistic variables (DVs and controls)

All 6 linguistic percentage variables:
- Formula pattern: "(LM [sentiment] count / total words) × 100 for [speaker] in [section]"
- Source: LinguisticEngine (stage 2 year-partitioned parquets). **PASS**
- Winsorization: "0%/99% upper-only per-year" — verified vs `_linguistic_engine.py` line 255–258: `winsorize_by_year(combined, existing_pct_cols, lower=0.0, upper=0.99, min_obs=10)`. **PASS**

### IVs

`PRisk_lag`:
- Formula: "PRisk from Hassan et al. (2019) for cal quarter Q-1". **PASS**
- Winsorization: "1%/99% per-year (builder level)" — `prisk_q_lag.py` line 165: `winsorize_by_year(prisk_df, ["PRisk"], year_col="year")`. Default is 1%/99%. **PASS**
- Source: `PRiskLagBuilder: firmquarter_2022q1.csv`. **PASS**

`PRisk_lag2`:
- Same structure; `prisk_q_lag2.py` line 168. **PASS**

### Financial controls

`lnAssets`:
- Doc: `ln(atq) where atq > 0; else NaN`
- Code: `comp["lnAssets"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` (line 943)
- **PASS — exact match**

`TobinsQ` — **FAIL** (same issue as B4 above):
- Doc formula: `(cshoq * prccq + debt_book) / atq` — implies `debt_book = dlcq + dlttq`
- Actual code: debt components are clipped (lower=0), individual NaN filled to 0, overall debt_book=NaN only when BOTH are NaN. Missing this detail.
- Evidence: `_compustat_engine.py` lines 987–997 (reproduced in Phase 3 B4-CHECK above).
- **FAIL**

`ROA`:
- Doc: `iby_annual (Q4 value) / avg_assets, where avg_assets = (atq_t + atq_{t-1}) / 2`
- Code: `_compute_annual_q4_variable(comp, "iby", ...)` and `(atq_annual + atq_annual_lag1) / 2` (lines 960–968). ROA = NaN if avg_assets ≤ 0. **PASS**

`CashRatio`:
- Doc: `cheq / atq`
- Code: `comp["CashRatio"] = comp["cheq"] / comp["atq"]` (line 986). **PASS**

`DivDummy`:
- Doc: `1 if dvy_annual (Q4 cumulative) > 0, else 0`; No winsorization (binary)
- Code: `dvy_annual = _compute_annual_q4_variable(comp, "dvy", ...)`. `(pd.Series(dvy_annual).fillna(0) > 0).astype(float)` (lines 1009–1012). In `skip_winsorize` (line 1218). **PASS**

`FirmMat`:
- Doc: `req / atq (retained earnings / total assets)`
- Code: `np.where((df["atq"].notna()) & (df["atq"] > 0), df["req"] / df["atq"], np.nan)` (lines 807–809). **PASS**

`EarnVol`:
- Doc: `rolling std(iby/atq) over trailing 1826 days (~5 years), min 3 obs`
- Code: `df_ts.groupby("gvkey")["roa_annual"].rolling("1826D", min_periods=3).std()` (lines 822–824). `roa_annual = where(atq > 0, iby/atq, NaN)` (line 812–814). **PASS**

`gvkey` (FE — Entity):
- "6-digit Compustat identifier; Manifest". **PASS**

`year` (FE — Time):
- `start_date.dt.year`; panel builder line 151. **PASS**

### Completeness check
All variables referenced in any regression spec (DVs, IVs, BASE_CONTROLS, dynamic Pres controls, FE columns) are present in the dictionary. Leverage is built but not in regressions — correctly excluded from the dictionary and flagged in L item 1 and F2. The omission is appropriate per the creation prompt which requires only "every variable in every regression spec".

**Phase 6 Summary: 16/17 PASS (TobinsQ formula fails)**

---

## PHASE 7: PIPELINE, OUTPUTS, AND TREATMENT (Sections F, G, H)

### F-CHECK: Data Pipeline

**F1. Dependency Chain (7 steps):**
- Step 3 states "16 builders"; panel builder `builders` dict (lines 83–120) has exactly 16 entries (manifest + 15 variable builders). **PASS**
- Step 6: "4 × 2 × 3 = 24 regressions maximum" — consistent with CONFIG. **PASS**
- Step 7: "generate_all_tables.py reads 8 Main-sample .txt files" — consistent with col_files. **PASS**

**F2. Data Engines (4 engines):**
All 4 verified against panel builder imports (lines 40–58): LinguisticEngine (indirectly via ManagerQAUncertaintyBuilder etc.), CompustatEngine (indirectly via SizeBuilder etc.), PRiskLagBuilder, PRiskLag2Builder. **PASS**

Note on Leverage: doc states "built but NOT used in runner" — confirmed: Leverage absent from runner column list (lines 448–471). **PASS**

**F3. Merge Operations (16 merges):**
Panel builder merge loop (lines 131–148): iterates over all 15 non-manifest builders; each merges on `file_name`, `how="left"`, zero row-delta enforced. 16 total operations (including manifest base load). **PASS**

### G-CHECK: Outputs

**G1. Stage 3 Outputs (4 files):**
- `h11_prisk_uncertainty_lag_panel.parquet` → builder line 185. **PASS**
- `summary_stats.csv` → builder lines 192–193. **PASS**
- `report_step3_h11_lag.md` → builder line 235. **PASS**
- `run_manifest.json` → builder lines 197–208 via `generate_manifest()`. **PASS**

**G2. Stage 4 Outputs (8 file types):**
- `h11_prisk_uncertainty_lag_table.tex` → runner line 555 → `_save_latex_table()` line 257. **PASS**
- `model_diagnostics.csv` → runner line 556. **PASS**
- `summary_stats.csv` and `.tex` → runner lines 492–503 via `make_summary_stats_table()`. **PASS**
- `sample_attrition.csv` and `.tex` → runner line 569 via `generate_attrition_table()` (confirmed in attrition_table.py lines 47, 51). **PASS**
- `regression_results_{sample}_{dv}_{lag_suffix}.txt` → runner line 551. **PASS**
- `run_manifest.json` → runner lines 573–583. **PASS**

### H-CHECK: Outlier and Missing Data Treatment

**H1. Winsorization:**

Linguistic variables:
- Doc: "0%/99% upper-only per calendar year"
- Code `_linguistic_engine.py` line 255–258: `winsorize_by_year(..., lower=0.0, upper=0.99, min_obs=10)`. **PASS**

Compustat variables:
- Doc: "1%/99% per fiscal year (fyearq)"
- Code `_compustat_engine.py` lines 1229–1232: `year_col = comp["fyearq"]`; `_winsorize_by_year(comp[col], year_col)` (1%/99% by default). **PASS**

PRisk variables:
- Doc: "1%/99% per calendar year at builder level"
- Code `prisk_q_lag.py` line 165 and `prisk_q_lag2.py` line 168: `winsorize_by_year(prisk_df, ["PRisk"], year_col="year")`. **PASS**

DivDummy skip:
- Doc: "No (binary variable, skip_winsorize)"
- Code: in `skip_winsorize` set (`_compustat_engine.py` line 1218). **PASS**

**H2. Missing Data Policy:**
- Doc: "Complete-case deletion; inf/−inf → NaN before dropna"
- Code line 172: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()`. **PASS**

**H3. Transformations — FAIL (omission in Section L):**

Doc states: "No centering, z-scoring, or scaling is applied to IVs. Only lnAssets uses natural log."

This is correct for the actual regression code. However, the runner's internal LaTeX table footnote (`_save_latex_table` line 399) states:
> `"All continuous controls are standardized. "`

There is NO standardization code anywhere in the runner — no `.mean()` subtraction, no `.std()` scaling, no z-score transform, no call to any scaling library. The footnote is **factually false** and appears in the runner's standalone LaTeX output (`h11_prisk_uncertainty_lag_table.tex`). The provenance doc does not flag this in Section L.

Evidence of absence: grep for `standardiz`, `z_score`, `zscore`, `scale`, `normalize`, `mean()`, `std()` applied to controls in the runner returns only line 399 (the false footnote itself). No scaling code found.

**FAIL — Section L should document this runner footnote inaccuracy**

**Phase 7 Summary: 8/9 PASS (H3: omission of LaTeX footnote bug from Section L)**

---

## PHASE 8: TABLE GENERATOR ENTRY (Section I)

Full entry from generate_all_tables.py (lines 200–228) — reproduced verbatim in the provenance doc:

```python
{
    "id": "H11-Lag",
    "type": "moderation",
    "dir": "h11_prisk_uncertainty_lag/2026-03-27_095002",
    "caption": "H11-Lag: Lagged Political Risk and Language Uncertainty",
    "label": "tab:h11_lag",
    "cols": 8,
    "col_files": {
        1: "regression_results_Main_UncAnsMgr_lag1.txt",
        2: "regression_results_Main_UncAnsCEO_lag1.txt",
        3: "regression_results_Main_UncPreMgr_lag1.txt",
        4: "regression_results_Main_UncPreCEO_lag1.txt",
        5: "regression_results_Main_UncAnsMgr_lag2.txt",
        6: "regression_results_Main_UncAnsCEO_lag2.txt",
        7: "regression_results_Main_UncPreMgr_lag2.txt",
        8: "regression_results_Main_UncPreCEO_lag2.txt",
    },
    "dvs": [(r"PRisk\_lag", 4), (r"PRisk\_lag2", 4)],
    "col_dv_labels": ["Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres",
                      "Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres"],
    "key_vars": ["PRisk_lag", "PRisk_lag2"],
    "key_labels": [r"PRisk\_lag", r"PRisk\_lag2"],
    "key_tails": ["one_pos", "one_pos"],
}
```

Field-by-field verification:

| Field | Doc value | Actual generate_all_tables.py | Match? |
|-------|----------|-------------------------------|--------|
| "id" | "H11-Lag" | "H11-Lag" | PASS |
| "type" | "moderation" | "moderation" | PASS |
| "cols" | 8 | 8 | PASS |
| "key_tails" | ["one_pos","one_pos"] | ["one_pos","one_pos"] | PASS |
| "key_vars" | ["PRisk_lag","PRisk_lag2"] | ["PRisk_lag","PRisk_lag2"] | PASS |
| col_files naming | lag1/lag2 suffix | runner line 550: `"lag1" if iv_var == "PRisk_lag" else "lag2"` | PASS |

Tail direction: `key_tails = ["one_pos","one_pos"]` (one-tailed beta > 0) matches runner line 221 (one-tailed, beta > 0). **PASS**

No top-level "tail" or "hyp_dir" field — correctly noted; type="moderation" uses key_tails. **PASS**

**Phase 8 Summary: 5/5 PASS**

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

### K1. PanelOLS Specifics (filled section)

- **Entity effects:** "Absorbed via EntityEffects; first level of MultiIndex (gvkey, year) = gvkey (firm FE)"
  - Code: `set_index(["gvkey", "year"])` (line 200); `EntityEffects` in formula. **PASS**

- **Time effects:** "Absorbed via TimeEffects; second level = year (calendar year FE)"
  - Code: second index = year (calendar year); `TimeEffects` in formula. **PASS**

- **other_effects usage:** "Not used. All specs use firm FE (no industry FE variant in this suite)."
  - Code: no `other_effects` parameter anywhere in runner. No ff12_code in set_index or formula. **PASS**

- **drop_absorbed:** "True (line 203)"
  - Code line 203: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`. **PASS**

- **Singleton handling:** "PanelOLS default behavior; no explicit singleton filter"
  - Code: no singleton filter. **PASS**

### K2–K6: N/A
All marked N/A. Correct — suite uses PanelOLS only. **PASS**

**Phase 9 Summary: 5/5 PASS**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec in Variable Dictionary with explicit formula and source engine | PARTIALLY | All 17 regression variables present; TobinsQ formula omits clipping/NaN-propagation details |
| 2 | The model equation matches what the code actually estimates | PASS | Two-equation structure (QA/Pres split) correctly mirrors PRES_CONTROL_MAP logic |
| 3 | The specification register accounts for every model column | PASS | 8 rows; all 8 col_files in generate_all_tables.py accounted for |
| 4 | The attrition cascade has row counts for each filter step | PASS | [RUNTIME] counts with explanation; acceptable per project policy |
| 5 | Tail test direction matches between runner and generate_all_tables.py | PASS | Runner: one-tailed beta > 0 (line 221); table: key_tails=["one_pos","one_pos"] |
| 6 | FE specification matches docstring, code, and document | PASS | Entity=gvkey, Time=year (calendar), consistent throughout all three |
| 7 | Every merge in panel builder documented with join keys and type | PASS | 16 merges, all on file_name, left join, documented in F3 |
| 8 | Output file list matches what the runner actually writes | PASS | All 8 Stage 4 output types confirmed against runner code |
| 9 | Model-family addendum filled for correct family only | PASS | K1 (PanelOLS) filled; K2–K6 marked N/A |
| 10 | Any [UNVERIFIED] claim has explanation of what blocks verification | PASS | One [UNVERIFIED] at D2 with clear explanation (row counts require runtime execution) |

**Phase 10 Summary: 9/10 PASS with notes (Gate 1: TobinsQ formula imprecise)**

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

### Check 1: DVs in B2 match DVs in C
- B2 DVs: UncAnsMgr, UncAnsCEO, UncPreMgr, UncPreCEO
- Spec register C: same 4 DVs across 8 rows. **PASS**

### Check 2: DVs in C match DVs in I
- Col_files in I contain the same 4 DV names in filenames. (Note: "dvs" field in I lists IV group labels per type="moderation" — correctly documented in L item 5.) **PASS**

### Check 3: Controls in B4 match variables in E
- 9 BASE_CONTROLS from B4: all 9 present in E dictionary. Dynamic Pres controls (dual role DV/Control) present in E. **PASS**

### Check 4: Column count in A matches rows in C
- A: 8 columns. C: 8 rows. **PASS**

### Check 5: Column count in A matches "cols" in I
- A: 8. I: `"cols": 8`. **PASS**

### Check 6: Tail direction in A matches B7 matches I
- A: "One-tailed (beta > 0)"
- B7: "One-tailed, beta > 0"
- I: `"key_tails": ["one_pos", "one_pos"]`
- **PASS — internally consistent throughout**

### Check 7: FE in B5 matches C matches K
- B5: Entity=gvkey (Firm FE), Time=year (Cal Year FE)
- C: all 8 rows: "Firm" entity FE, "Cal Year" time FE
- K1: "Absorbed via EntityEffects; gvkey" / "Absorbed via TimeEffects; year"
- **PASS**

### Check 8: Panel index in A matches set_index in K
- A: `(gvkey, year)`
- K1: "first level of MultiIndex (gvkey, year) = gvkey"
- Code line 200: `set_index(["gvkey", "year"])`
- **PASS**

**Phase 11 Summary: 8/8 PASS**

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 3/6 | TobinsQ formula in B4 and E | `(cshoq * prccq + dlcq + dlttq) / atq` (simplified) | `(mktcap + debt_book) / atq` where `debt_c = dlcq.clip(lower=0).fillna(0)`, `debt_t = dlttq.clip(lower=0).fillna(0)`, `debt_book = NaN if both are NaN else debt_c + debt_t`; result NaN if atq missing/≤0 or mktcap missing | Medium — omits negative-value clipping and NaN-propagation logic that materially affect computed values | Update B4 formula and E dictionary entry to document full construction |
| 7 | Section L — runner LaTeX footnote inaccuracy | Not documented anywhere in Section L | `_save_latex_table()` line 399 writes `"All continuous controls are standardized."` but no standardization code exists in the runner; the claim is factually false | Medium — published LaTeX output carries a false methodological claim; future reproducers reading the .tex file will be misled | Add item 8 to Section L documenting this discrepancy |

---

## CORRECTIONS REQUIRED

### Correction 1 — Section B4 (Control Variables table, TobinsQ row)

**Section:** B4, Control Variables table

**Current text (formula column):**
```
(cshoq * prccq + dlcq + dlttq) / atq
```

**Should say:**
```
(cshoq×prccq + debt_book) / atq, where:
  debt_book = clip(dlcq, 0).fillna(0) + clip(dlttq, 0).fillna(0),
  except debt_book = NaN if both dlcq and dlttq are NaN;
  result = NaN if atq missing/≤0 or mktcap (cshoq×prccq) missing
```

**Code reference:** `src/f1d/shared/variables/_compustat_engine.py` lines 987–997.

---

### Correction 2 — Section E (Variable Dictionary, TobinsQ row)

**Section:** E, Variable Dictionary

**Current Formula column:**
```
(cshoq * prccq + debt_book) / atq
```
(Slightly better than B4 but still omits the clipping and NaN logic.)

**Should say:**
```
(cshoq×prccq + debt_book) / atq, where debt_book = clip(dlcq,0).fillna(0) + clip(dlttq,0).fillna(0); debt_book=NaN if both dlcq and dlttq are NaN; overall NaN if atq ≤ 0 or mktcap missing
```

**Code reference:** `src/f1d/shared/variables/_compustat_engine.py` lines 987–997.

---

### Correction 3 — Section L (Known Issues, add item 8)

**Section:** L, Known Issues and Notes

**Current state:** 7 items. Item 8 is missing.

**Add as item 8:**

```markdown
8. **Runner's internal LaTeX footnote incorrectly claims standardization.**
   The `_save_latex_table` function (line 399) writes the table note
   "All continuous controls are standardized." into the runner's own LaTeX
   output (`h11_prisk_uncertainty_lag_table.tex`). However, no standardization
   (z-scoring, centering, or any other scaling) code exists anywhere in the
   runner or panel builder. This note is factually incorrect. The
   generate_all_tables.py publication table does not reproduce this footnote
   and is unaffected. The runner's standalone LaTeX file carries a false
   methodological claim that should be corrected by removing that footnote line.
   Source: run_h11_prisk_uncertainty_lag.py line 399.
```

---

## ADDITIONAL OBSERVATIONS (not failures)

1. **PRisk builder merge description:** The doc states PRiskLagBuilder matches "via (gvkey, cal_q_lag)." The actual merge uses `left_on=["gvkey", "cal_q_lag"], right_on=["gvkey", "cal_q"]` — joining the call's lagged quarter key to the PRisk table's contemporaneous quarter column. The description is correct in substance. Not a failure.

2. **Compustat winsorization uses fyearq (integer) as year grouper:** The doc says "per fiscal year (fyearq)" which correctly identifies this. Code confirmed: `year_col = comp["fyearq"]` (line 1229). Not a failure.

3. **EarnVol uses annual Q4 panel internally then joins back:** The rolling window is computed on an annual panel (`dummy_date = fyearq-12-31`) then joined back to all quarters via `(gvkey, fyearq)`. The doc describes this accurately as "Rolling std(iby/atq) over trailing 1826 days, min 3 obs". Not a failure.

4. **Panel builder does not include report file in `generate_manifest()` output_files dict:** `save_outputs()` lines 197–208 records only `panel_path` and `stats_path`. The `report_step3_h11_lag.md` (line 235) is written by `generate_report()` separately and is not in the manifest JSON. The doc's G1 output list correctly lists the report as a produced file (it is written to disk). This is a minor implementation detail, not a provenance doc error.

5. **"standardized" in table note vs. reality:** As documented in Correction 3, this is a bug in the runner itself. The provenance doc accurately documents what the code does (no standardization) but should flag that the runner's own LaTeX output contradicts this.

---

*End of adversarial audit — H11-Lag provenance document. 101/105 checks pass (96%). Three corrections required.*
