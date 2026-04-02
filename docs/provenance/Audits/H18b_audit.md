# Adversarial Audit Report: H18b Provenance Document

**Suite ID:** H18b
**Provenance Doc:** `docs/provenance/H18b.md`
**Runner:** `src/f1d/econometric/run_h18b_cccl_logit.py`
**Panel Builder:** `src/f1d/variables/build_h18_cccl_received_panel.py`
**Audit Date:** 2026-04-01
**Auditor:** Hostile adversarial audit — every claim treated as wrong until proven correct

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 29 | 29 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 17 | 14 | 3 | 82% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 5 | 5 | 0 | 100% |
| Variable Dictionary (Phase 6) | 22 | 19 | 3 | 86% |
| Pipeline/Outputs/Treatment (Phase 7) | 15 | 13 | 2 | 87% |
| Table Generator Entry (Phase 8) | 6 | 6 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 8 | 8 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 8 | 2 | 80% |
| Cross-Reference Consistency (Phase 11) | 8 | 7 | 1 | 88% |
| **TOTAL** | **135** | **124** | **11** | **92%** |

---

## VERDICT

**FAIL — INACCURATE**: The provenance document is structurally complete but contains 5 factual errors of varying severity. The most material errors are (1) the wrong TobinsQ formula throughout (copied from an outdated engine comment rather than actual code), (2) the wrong ROA fallback claim (fallback exists for CashFlowAt only, not ROA), and (3) an internal inconsistency between F1 and F3 on builder count. Remaining errors are minor line-number and label precision issues.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 3/B4 | TobinsQ formula | `(atq + cshoq*prccq - ceqq) / atq` | `(cshoq*prccq + dlcq_clipped + dlttq_clipped) / atq` — i.e., Market Cap + Book Debt, not Market Cap minus Book Equity | HIGH | Correct formula in B4 and E |
| 3/B4 | TobinsQ source fields | Lists `cshoq, prccq, ceqq, atq` | Actual code uses `cshoq, prccq, dlcq, dlttq, atq` (ceqq NOT used; dlcq, dlttq instead) | HIGH | Correct source field list |
| 3/B4 | ROA fallback | "avg_assets falls back to atq_t when prior year missing" | No fallback exists for ROA. `avg_assets = (atq_t + atq_{t-1}) / 2`; if lag is NaN, avg_assets is NaN and ROA is NaN. The fallback logic exists only for CashFlowAt (engine line 685-686), not ROA. | MEDIUM | Remove fallback claim from ROA in B4 and E |
| 3/B6 | cov_kwds line number | "cov_kwds={"groups": ...} (runner line 271)" | Line 271 is `)` (closing parenthesis). Both `cov_type` and `cov_kwds` are on the same line 270. | LOW | Update to "runner line 270 (both cov_type and cov_kwds)" |
| 7/F1 | AME get_margeff line number | "model.get_margeff(at=\"overall\") (runner line 306)" | Line 305 is the `get_margeff` call; line 306 is `mfx_df = mfx.summary_frame()` | LOW | Update citation to runner line 305 |
| 7/F3 | Builder count | "each of 15 builder outputs" (F3 merge table) | 16 non-manifest builders: manager_qa_uncertainty, manager_pres_uncertainty, ceo_qa_uncertainty, ceo_pres_uncertainty, size, book_lev, tobins_q, roa, cash_holdings, capex_intensity, dividend_payer, ocf_volatility, sales_growth, rd_intensity, cash_flow, volatility | MEDIUM | Update F3 merge table from "15 builder outputs" to "16 builder outputs" |
| 11/cross | F1 vs F3 builder count | F1 says "16 builder outputs"; F3 says "15 builder outputs" | Code has 17 builders total (1 manifest + 16 others). F1 is correct. F3 is wrong. | MEDIUM | Fix internal inconsistency: update F3 to match F1 count of 16 |
| 6/E | TobinsQ formula (E table) | Same wrong formula as B4 | Same error propagated from B4 — wrong formula and wrong source fields | HIGH | (Same fix as B4 — correct E table row) |
| 6/E | ROA fallback (E table) | "avg_assets falls back to atq_t when prior year missing" | No fallback in engine for ROA | MEDIUM | (Same fix as B4 — remove fallback claim from E table) |

---

## PHASE 1: STRUCTURAL COMPLETENESS

Verified against `docs/Prompts/Suite Provenance Doc.txt` required sections.

| Section | Required | Present | Complete | Notes |
|---------|----------|---------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block present and filled |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX-compatible equation with FE note |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table + construction detail |
| B3. Independent Variable(s) | Yes | Yes | Yes | All 4 IVs with formula and source |
| B4. Control Variables | Yes | Yes | Yes* | Both base and extended tables present; TobinsQ formula wrong; ROA fallback wrong |
| B5. Fixed Effects | Yes | Yes | Yes | Both FE types documented |
| B6. Standard Errors | Yes | Yes | Yes* | Correct type/cluster; minor line citation error |
| B7. Hypothesis Test | Yes | Yes | Yes | Direction, p-value formula, thresholds |
| C. Spec Register | Yes | Yes | Yes | 2-row table matches 2 MODEL_SPECS |
| D. Sample Construction | Yes | Yes | Yes | |
| D1. Population | Yes | Yes | Yes | |
| D2. Exclusion Criteria | Yes | Yes | Yes | 4-step cascade with N counts |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Counts per col including events and pseudo-R2 |
| E. Variable Dictionary | Yes | Yes | Yes* | All required variables present; 2 formula errors |
| F. Data Pipeline | Yes | Yes | Yes | |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain, F1 builder count (16) is correct |
| F2. Data Engines | Yes | Yes | Yes | 5 engines documented |
| F3. Merge Operations | Yes | Yes | Yes* | 4 merges; builder count (15) is wrong (should be 16) |
| G. Outputs | Yes | Yes | Yes | |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 3 files; no false report_step3 claim |
| G2. Stage 4 Outputs | Yes | Yes | Yes | All 8 output files correctly listed |
| G3. Summary Statistics | Yes | Yes | Yes | All 17 variables listed with metrics |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1/H2/H3 all present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Entry transcribed correctly |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands including --panel-path and --dry-run |
| K. Model-Family Addendum | Yes | Yes | Yes | K3 filled; K1/K2/K4/K5/K6 all N/A |
| L. Known Issues | Yes | Yes | Yes | 9 issues documented |

**Phase 1 Result: 29/29 PASS** (with notes on errors found in later phases)

---

## PHASE 2: SUITE IDENTITY (Section A)

Read Section A YAML block against `run_h18b_cccl_logit.py` docstring and code.

**A-1. Suite ID: H18b**
- Doc: `H18b`
- Code: docstring line 5 `ID: econometric/run_h18b_cccl_logit`; runner comment `# ── H18b (Logit robustness) ──`
- **PASS**

**A-2. Title: "Logit Robustness — Speech Uncertainty and SEC Comment Letters"**
- Doc claims this title.
- Runner docstring lines 3-4: `STAGE 4: H18b Logit Robustness — SEC Comment Letter Receipt`
- The doc title is a slight paraphrase but matches intent. Legitimate interpretation.
- **PASS**

**A-3. Hypothesis: "Does speech uncertainty during earnings calls predict SEC comment letter receipt in the subsequent calendar quarter?"**
- Runner docstring lines 10-12: "Logit robustness check for H18. Same DV (CCCL binary), same IVs, same controls — replaces LPM with logistic regression."
- Hypothesis content is consistent.
- **PASS**

**A-4. Direction: One-tailed (beta > 0)**
- Runner docstring line 28: `Hypothesis: One-tailed (beta > 0 — higher uncertainty -> more SEC scrutiny).`
- Runner code lines 317-319: `ame_p_one = ame_p_two / 2 if ame > 0 else 1 - ame_p_two / 2`
- Doc: `Direction: One-tailed (beta > 0)`
- **PASS**

**A-5. Model Family: Logit (average marginal effects reported)**
- Runner line 268: `model = smf.logit(formula, data=df_prepared).fit(...)`
- Import line 57: `import statsmodels.formula.api as smf`
- Doc: `Model Family: Logit (average marginal effects reported)`
- **PASS**

**A-6. Estimator: statsmodels.formula.api.logit with BFGS optimizer**
- Runner lines 268-271: `smf.logit(formula, data=df_prepared).fit(maxiter=300, disp=False, method="bfgs", cov_type="cluster", ...)`
- Doc: `Estimator: statsmodels.formula.api.logit with BFGS optimizer`
- **PASS**

**A-7. Unit of Observation: Call-level (individual earnings call)**
- Builder docstring line 8: `Unit of observation: individual earnings call (file_name).`
- Panel builder loops over `file_name` as the row identifier.
- **PASS**

**A-8. Panel Index: None (logit with formula-based dummies, no PanelOLS panel index)**
- The runner does not call `set_index()` — it uses `smf.logit(formula, data=df)`.
- No `PanelOLS` used; no entity/time index set.
- Doc: `Panel Index: None (logit with formula-based dummies, no PanelOLS panel index)`
- **PASS**

**A-9. Columns: 2**
- Runner `MODEL_SPECS` (lines 91-94): 2 entries.
- Doc: `Columns: 2`
- **PASS**

**A-10. Runner and Panel Builder paths**
- `src/f1d/econometric/run_h18b_cccl_logit.py` — file exists on disk.
- `src/f1d/variables/build_h18_cccl_received_panel.py` — file exists on disk.
- **PASS**

**Phase 2 Result: 10/10 PASS**

---

## PHASE 3: MODEL SPECIFICATION (Section B)

### B1-CHECK: Regression Equation

Doc equation:
```
P(CCCL_{i,t} = 1 | X) = Lambda(
    b1*UncAnsCEO + b2*UncPreCEO
    + b3*UncAnsMgr + b4*UncPreMgr
    + Controls + C(ff12_code) + C(cal_yr)
)
```

Runner formula construction (lines 253-254):
```python
rhs = " + ".join(KEY_IVS + controls) + " + " + fe_formula
formula = f"{dv} ~ {rhs}"
```
where `fe_formula = "C(ff12_code) + C(cal_yr)"` for both specs.

All 4 IVs in the equation? Keys: UncAnsCEO ✓, UncPreCEO ✓, UncAnsMgr ✓, UncPreMgr ✓.
FE terms: C(ff12_code) ✓, C(cal_yr) ✓.
Lambda (logistic CDF) notation correct for smf.logit ✓.
**PASS**

### B2-CHECK: Dependent Variable(s)

Doc: `CCCL | Binary | 1 if firm received CCCL in cal quarter Q+1 | Lead (Q+1)`

Runner line 92: `"dv": "CCCL"` in MODEL_SPECS.
Runner line 484: `n_dv_valid = panel["CCCL"].notna().sum()` — CCCL used as DV.
Builder `create_cccl_dvs` lines 276-279: `cccl_fwd[i] = 1.0 if (g, q_next) in cccl_set else 0.0; panel["CCCL"] = cccl_fwd`
Construction detail (B2 step 4): "CCCL = 1 if (gvkey, Q+1) is in the event set; 0 otherwise" — verified correct.
CCCL_lag created: `cccl_lag[i] = 1.0 if (g, q_prev) in cccl_set else 0.0; panel["CCCL_lag"] = cccl_lag` — used for Lagged_DV.
**PASS**

### B3-CHECK: Independent Variable(s)

Runner `KEY_IVS` (lines 72-77):
```python
KEY_IVS = [
    "UncAnsCEO",
    "UncPreCEO",
    "UncAnsMgr",
    "UncPreMgr",
]
```
Doc lists all 4 with correct names ✓. Formula "(Uncertainty word count / total word count) * 100" — confirmed in LinguisticEngine docstring.
Winsorization claim: "0%/99% per-year (upper-only)" — verified in `_linguistic_engine.py` lines 255-257: `winsorize_by_year(combined, existing_pct_cols, year_col="year", lower=0.0, upper=0.99, min_obs=10)` ✓
"No centering, z-scoring, or log-transformation" — no such operations visible in runner or builder ✓.
**PASS**

### B4-CHECK: Control Variables

Runner `BASE_CONTROLS` (lines 79-83):
```python
BASE_CONTROLS = [
    "lnAssets", "TobinsQ", "ROA", "Leverage", "Capex",
    "CashRatio", "DivDummy", "sCFO",
    "Lagged_DV",
]
```
Runner `EXTENDED_CONTROLS` (lines 85-87):
```python
EXTENDED_CONTROLS = BASE_CONTROLS + [
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
]
```

Doc B4 base controls table: `lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, DivDummy, sCFO, Lagged_DV` — 9 entries ✓ matches code.
Doc B4 extended adds: `SalesGrowth, RDSales, CashFlowAt, DailyVola` — 4 entries ✓ matches code.

**TobinsQ formula — FAIL:**
- Doc B4 claims: `(atq + cshoq*prccq - ceqq) / atq`
- Actual `_compustat_engine.py` lines 987-997:
  ```python
  mktcap = comp["cshoq"] * comp["prccq"]
  debt_c = comp["dlcq"].clip(lower=0).fillna(0)
  debt_t = comp["dlttq"].clip(lower=0).fillna(0)
  debt_book = np.where(comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t)
  comp["TobinsQ"] = np.where(
      comp["atq"].notna() & (comp["atq"] > 0) & mktcap.notna(),
      (mktcap + debt_book) / comp["atq"],
      np.nan,
  )
  ```
  Formula is `(cshoq*prccq + dlcq + dlttq) / atq`.
- The doc's formula `(atq + cshoq*prccq - ceqq) / atq` matches an outdated comment in the engine's header (lines 24-27) which reads "Fixed to (atq + cshoq*prccq - ceqq)/atq which matches v2 design". This comment is wrong/outdated; the actual code uses book debt (dlcq+dlttq), not book equity (ceqq). The doc should have read the code, not the comment.
- Source fields: doc says `cshoq, prccq, ceqq, atq`; code uses `cshoq, prccq, dlcq, dlttq, atq` — ceqq NOT used, dlcq and dlttq missing from doc.
- **FAIL (HIGH severity)**

**ROA fallback — FAIL:**
- Doc B4 claims: "avg_assets falls back to atq_t when prior year missing"
- Actual `_compustat_engine.py` lines 959-969:
  ```python
  atq_annual = _compute_annual_q4_variable(comp, "atq", "_atq_annual")
  atq_annual_lag1 = _compute_annual_q4_variable_lag(comp, "atq", "_atq_annual_lag1")
  avg_assets = (pd.Series(atq_annual, ...) + pd.Series(atq_annual_lag1, ...)) / 2
  comp["ROA"] = np.where(avg_assets > 0, iby_annual / avg_assets, np.nan)
  ```
  No fallback. If `atq_{t-1}` is NaN, `avg_assets` is NaN, ROA is NaN.
- The fallback logic EXISTS for CashFlowAt (`_compustat_engine.py` line 686: `avg_assets = avg_assets.where(avg_assets.notna(), annual["atq"])`), but NOT for ROA.
- The doc incorrectly applies the CashFlowAt fallback description to ROA.
- **FAIL (MEDIUM severity)**

All other B4 control formulas: lnAssets (ln(atq), atq>0→NaN ✓), Leverage ((dlcq+dlttq)/atq ✓ — note: actual code does `fillna(0)` on individual components unless BOTH NaN, doc slightly simplifies to "missing=0" which is acceptable), Capex (capxy_annual/atq_lag ✓), CashRatio (cheq/atq ✓), DivDummy (dvy_annual>0 ✓), sCFO (5yr rolling std oancfy/atq_{t-1} ✓), SalesGrowth ((saley-saley_lag)/|saley_lag| ✓), RDSales (xrdq.fillna(0)/atq ✓), CashFlowAt (oancfy/avg_assets with fallback ✓), DailyVola (std*sqrt(252)*100 over [prev+5d,call-5d] min 10 days ✓).

Lagged_DV construction: Runner line 191: `panel["Lagged_DV"] = panel["CCCL_lag"]` ✓

**B4 Result: 2 FAIL, 12 PASS**

### B5-CHECK: Fixed Effects

Runner `MODEL_SPECS` (lines 91-94):
```python
{"col": 1, "dv": "CCCL", "controls": "base",     "fe_formula": "C(ff12_code) + C(cal_yr)"},
{"col": 2, "dv": "CCCL", "controls": "extended",  "fe_formula": "C(ff12_code) + C(cal_yr)"},
```
Both specs use identical `fe_formula = "C(ff12_code) + C(cal_yr)"`.
Doc table: Industry FE=`C(ff12_code)`, Calendar Year FE=`C(cal_yr)`, no Firm FE, no Year-Qtr FE ✓.
Doc correctly explains why firm FE and year-quarter FE are excluded (separation concerns) ✓.
**PASS**

### B6-CHECK: Standard Errors

Runner lines 268-271:
```python
model = smf.logit(formula, data=df_prepared).fit(
    maxiter=300, disp=False, method="bfgs",
    cov_type="cluster", cov_kwds={"groups": df_prepared["gvkey"].values},
)
```
- `cov_type="cluster"` ✓
- Groups: `df_prepared["gvkey"].values` (firm-clustered) ✓
- Doc: "cov_type=\"cluster\" passed to .fit() (runner line 270)" ✓
- Doc: "cov_kwds={"groups": df_prepared["gvkey"].values} (runner line 271)" — **MINOR ERROR**: both `cov_type` and `cov_kwds` are on line 270; line 271 is `)`. Content is correct; line citation is wrong.
- Delta method for AME SEs via `get_margeff()` ✓
- **PASS with minor note**

### B7-CHECK: Hypothesis Test

Runner lines 317-319:
```python
# One-tailed: H18b expects beta > 0
if not np.isnan(ame_p_two) and not np.isnan(ame):
    ame_p_one = ame_p_two / 2 if ame > 0 else 1 - ame_p_two / 2
```
Doc: `ame_p_one = ame_p_two / 2 if ame > 0 else 1 - ame_p_two / 2` — exact match ✓
Source of `ame_p_two`: `mfx_df.loc[iv, "Pr(>|z|)"]` (line 313) ✓
Significance stars: runner lines 339-347 — `***` p<0.01, `**` p<0.05, `*` p<0.10 ✓
All four IVs use same direction ✓
Reported as AMEs not log-odds ✓
**PASS**

**Phase 3 Result: 14/17 PASS** (3 FAIL: TobinsQ formula, TobinsQ source fields, ROA fallback)

---

## PHASE 4: SPEC REGISTER (Section C)

Runner `MODEL_SPECS` (lines 91-94) has exactly 2 entries.

| Code Col | Code DV | Code Controls | Code FE |
|----------|---------|---------------|---------|
| 1 | CCCL | base | C(ff12_code) + C(cal_yr) |
| 2 | CCCL | extended | C(ff12_code) + C(cal_yr) |

Doc spec register:
| Col | DV | Industry FE | Year FE | Firm FE | Year-Qtr FE | Controls |
|-----|----|----|----|----|----|----|
| 1 | CCCL | FF12 dummies | Cal Year dummies | No | No | Base |
| 2 | CCCL | FF12 dummies | Cal Year dummies | No | No | Extended |

- Row count matches: 2 ✓
- DV matches: CCCL both cols ✓
- Industry FE: FF12 dummies (C(ff12_code)) ✓
- Year FE: Cal Year dummies (C(cal_yr)) ✓
- Firm FE: No ✓ (intentionally omitted due to separation)
- Year-Qtr FE: No ✓ (intentionally omitted due to separation)
- Controls: Base/Extended ✓
- No specs in code missing from table ✓
- No specs in table not in code ✓

**Phase 4 Result: 5/5 PASS**

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

### D1-CHECK: Population

Doc: "Starting dataset: `outputs/variables/h18_cccl_received/latest/h18_cccl_received_panel.parquet`"
Runner `load_panel` (lines 143-167): `get_latest_output_dir(root_path / "outputs" / "variables" / "h18_cccl_received", required_file="h18_cccl_received_panel.parquet")` ✓
Doc: "Total calls in panel: 112,968" — consistent with project-scope claim of 112,968 calls total ✓
Doc: "Year range: 2002-2018" — consistent with project scope ✓
Doc: "Unique firms: per manifest" — acceptable given H18b doesn't re-build the panel ✓
**PASS**

### D2-CHECK: Exclusion Criteria (Attrition Cascade)

Doc attrition cascade:
| Step | Filter | N | Dropped |
|------|--------|---|---------|
| 1 | Full panel | 112,968 | -- |
| 2 | Main sample (excl FF12=8 Utility, FF12=11 Finance) | 88,205 | 24,763 |
| 3 | CCCL=1 in Main (informational) | 280 | -- |
| 4 | After complete-case + min-calls (col 1) | 57,216 | 30,989 |

Code verification:
- Step 1: `full_n = len(panel)` (runner line 480) ✓
- Step 2: `filter_main_sample` (runner line 481): `~ff12_code.isin([8, 11])` ✓
  - FF12=8: Utility, FF12=11: Finance — matches `panel_utils.py` lines 53-54 ✓
- Step 3: `n_dv1 = (panel["CCCL"] == 1).sum()` (runner line 485); added to attrition_stages as informational ✓
- Step 4: `generate_attrition_table` with `first["n_obs"]` (runner lines 521-528) ✓
  Filter sequence (runner `prepare_regression_data`, lines 179-225):
  a) Inf→NaN (line 199) ✓
  b) Drop DV NaN (lines 203-205) ✓
  c) Complete case (lines 207-209) ✓
  d) Min 5 calls/firm (lines 212-216) ✓

N counts cited from `outputs/econometric/h18b_cccl_logit/2026-03-31_195228/sample_attrition.csv` — reasonable source, noted as from actual run output.
**PASS**

### D3-CHECK: Sample Counts per Specification

Doc:
| Col | N obs | N firms | N events | Pseudo R² | Converged |
|-----|-------|---------|----------|-----------|-----------|
| 1 | 57,216 | 1,615 | 200 | 0.0926 | True |
| 2 | 54,915 | 1,595 | 196 | 0.0935 | True |

These values are from `model_diagnostics.csv` (actual run output). The doc correctly distinguishes col 1 (base) and col 2 (extended) counts. Col 2 having fewer obs is expected given extended controls add 4 more variables to the complete-case filter. Col 2 event count (196 < 200) is explained in L7. **PASS**

**Phase 5 Result: 5/5 PASS**

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

The E table must contain every variable in every regression spec. Verified against runner MODEL_SPECS and builder code.

**Completeness check**: Variables in any spec:
- DV: CCCL ✓ (in E)
- Key IVs (4): UncAnsCEO ✓, UncPreCEO ✓, UncAnsMgr ✓, UncPreMgr ✓
- Base controls (8 + Lagged_DV): lnAssets ✓, TobinsQ ✓, ROA ✓, Leverage ✓, Capex ✓, CashRatio ✓, DivDummy ✓, sCFO ✓, Lagged_DV ✓
- Extended controls (+4): SalesGrowth ✓, RDSales ✓, CashFlowAt ✓, DailyVola ✓
- FE/cluster: ff12_code ✓, cal_yr ✓, gvkey ✓
- `fyearq_int`: In `required` list (runner line 193) but NOT in the Variable Dictionary. This is a borderline omission — fyearq_int is not a regression variable; it is used only for the complete-case check. The doc covers its construction in F1 step 3 ("Converts `fyearq` to numeric as `fyearq_int`"). Marginal omission, not a material quality gate failure.

**Formula accuracy checks:**

| Variable | Doc Formula | Code Formula | Status |
|----------|-------------|--------------|--------|
| CCCL | 1 if (gvkey, Q+1) in CCCL event set | `cccl_fwd[i] = 1.0 if (g, q_next) in cccl_set else 0.0` | PASS |
| UncAnsCEO | Uncertainty words / total words * 100 | LinguisticEngine Stage 2 parquets | PASS |
| Lagged_DV | CCCL_lag from runner line 191 | `panel["Lagged_DV"] = panel["CCCL_lag"]` | PASS |
| lnAssets | ln(atq), atq > 0; zero/neg → NaN | `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` | PASS |
| **TobinsQ** | **(atq + cshoq*prccq - ceqq) / atq** | **(cshoq*prccq + dlcq_clipped + dlttq_clipped) / atq** | **FAIL** |
| TobinsQ source | cshoq, prccq, ceqq, atq | cshoq, prccq, dlcq, dlttq, atq — ceqq NOT used | **FAIL** |
| **ROA** | **avg_assets falls back to atq_t when prior year missing** | **No fallback — NaN when lag missing** | **FAIL** |
| Leverage | (dlcq + dlttq) / atq; missing=0 | `fillna(0)` on individual components; NaN if BOTH missing | PASS (acceptable simplification) |
| Capex | capxy_annual / atq_lag | `capxy_annual / atq_annual_lag1` | PASS |
| CashRatio | cheq / atq | `comp["cheq"] / comp["atq"]` | PASS |
| DivDummy | 1 if dvy_annual (Q4) > 0 | `(dvy_annual.fillna(0) > 0).astype(float)` | PASS |
| sCFO | 5yr rolling std (min 3 yrs) oancfy/atq_{t-1} | `_compute_ocf_volatility`: 5yr min 3, uses atq_lag | PASS |
| SalesGrowth | (saley-saley_lag)/|saley_lag|; saleq fallback | `annual["sale_annual"] = saley.fillna(saleq)` | PASS |
| RDSales | xrdq.fillna(0) / atq | `comp["xrdq"].fillna(0) / comp["atq"]` | PASS |
| CashFlowAt | oancfy / avg(atq_t, atq_{t-1}); fallback to atq_t | Engine line 686 fallback confirmed | PASS |
| DailyVola | std(daily_ret)*sqrt(252)*100 over [prev+5d, call-5d] min 10 days | `volatility.py` docstring line 6-8: same | PASS |
| ff12_code | Integer FF12 code; enters as C(ff12_code) | From manifest; cast to int runner line 223 | PASS |
| cal_yr | start_date.dt.year; built by build_cal_yr_qtr_index() | panel_utils.py line 215: `panel["cal_yr"] = dt.dt.year.astype("Int64")` | PASS |
| gvkey | 6-digit zero-padded Compustat ID | Builder line 255, runner preserves | PASS |

**Winsorization claims:**
- Linguistic IVs: 0%/99% per-year (upper-only) — verified in `_linguistic_engine.py` lines 255-257 ✓
- Compustat controls (lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, sCFO, SalesGrowth, RDSales, CashFlowAt): 1%/99% per-fyearq — verified as CompustatEngine applies winsorization ✓
- DivDummy: Not winsorized (binary) ✓
- CCCL, CCCL_lag: Not winsorized (binary) ✓
- DailyVola: Not winsorized ✓

**Phase 6 Result: 19/22 PASS** (3 FAIL: TobinsQ formula, TobinsQ source fields, ROA fallback — same root errors as Phase 3)

---

## PHASE 7: PIPELINE / OUTPUTS / TREATMENT (Sections F, G, H)

### F-CHECK: Data Pipeline

**F1. Dependency Chain:**
Step 1 (Raw inputs): manifest, CCCL letters, CCM, Compustat, Stage 2 linguistic, CRSP ✓
Step 2 (Engine loading): LinguisticEngine, CompustatEngine, CRSPEngine ✓
Step 3 (Panel builder): "merges 16 builder outputs" — **verified as correct** (17 total, 16 non-manifest) ✓
Step 4 (Runner loading): `get_latest_output_dir()` → parquet load → `build_cal_yr_qtr_index()` ✓
Step 5 (Sample filtering): filter sequence documented with correct line numbers ✓
Step 6 (Regression): Patsy formula construction, BFGS fit, AME computation ✓
Step 7 (Table generation): `generate_all_tables.py` entry documented ✓

**F2. Data Engines:**
| Engine | Source | Variables | Status |
|--------|--------|-----------|--------|
| LinguisticEngine | Stage 2 year-partitioned parquets | 4 uncertainty IVs | PASS |
| CompustatEngine | comp_na_daily_all.parquet | 11 controls | PASS |
| CRSPEngine | CRSP daily files | DailyVola | PASS |
| Direct load (CCCL) | cccl_conversations_all_years.parquet + CCM | CCCL, CCCL_lag | PASS |
| ManifestFieldsBuilder | master_sample_manifest.parquet | file_name, gvkey, ff12_code, start_date | PASS |

**F3. Merge Operations:**
| Doc Row | Left | Right | Key | Type | Status |
|---------|------|-------|-----|------|--------|
| 1 | manifest | each of **15** builder outputs | file_name | left | **FAIL: should be 16** |
| 2 | panel | CompustatEngine (fyearq) | gvkey+start_date→datadate (asof) | asof | PASS |
| 3 | CCCL letters | CIK-gvkey map | cik_int | inner | PASS |
| 4 | CCM map | Compustat CIK map | cik_int | outer (concat+dedup) | PASS |

The F3 merge table states "15 builder outputs" but the actual `builders` dict in the panel builder has 17 entries (manifest + 16 others), meaning 16 non-manifest outputs are merged. This is WRONG. F1 step 3 correctly says "16 builder outputs".

**F-CHECK Result: F1 PASS, F2 PASS, F3 FAIL (builder count)**

### G-CHECK: Outputs

**G1. Stage 3 Outputs (Panel Builder):**
Builder `main()` function writes:
1. `h18_cccl_received_panel.parquet` (line 343: `panel.to_parquet`) ✓
2. `summary_stats.csv` (line 348: `stats_df.to_csv`) ✓
3. `run_manifest.json` (lines 352-356: `generate_manifest(stage="stage3")`) ✓

Doc lists exactly these 3 files. No phantom outputs claimed. **PASS**

**G2. Stage 4 Outputs (Runner):**
Runner writes (from `save_outputs` and `main`):
1. `regression_results_col1.txt` (lines 370-411 loop) ✓
2. `regression_results_col2.txt` (same loop for col 2) ✓
3. `model_diagnostics.csv` (line 422: `diag_df.to_csv`) ✓
4. `marginal_effects.csv` (lines 442-444: conditional write) ✓
5. `summary_stats.csv` (line 493) ✓
6. `summary_stats.tex` (line 494) ✓
7. `sample_attrition.csv` (lines 528-529: `generate_attrition_table`) ✓
8. `sample_attrition.tex` (same call) ✓
9. `run_manifest.json` (lines 531-536: `generate_manifest(stage="stage4")`) ✓

Doc G2 lists 8 rows (combining csv/tex where applicable) and explicitly notes no `report_step4` file. **PASS**. Doc note at G2 end: "The runner itself does not write a separate h18b_table.tex" — confirmed by absence of any `.tex` table write in runner. ✓

**G3. Summary Statistics:**
Runner `SUMMARY_STATS_VARS` (lines 103-121): 17 variables — CCCL, 4 IVs, lnAssets, TobinsQ, ROA, Leverage, CashRatio, Capex, DivDummy, sCFO, SalesGrowth, RDSales, CashFlowAt, DailyVola.
Doc G3 lists same 17 variables ✓.
Metrics: N, Mean, SD, Min, P25, Median, P75, Max via `make_summary_stats_table` ✓.
Summary stats computed on main sample BEFORE complete-case filtering (runner line 491: called after `filter_main_sample` but before regression loops) ✓.

**G-CHECK Result: All PASS**

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization:**
- Compustat controls 1%/99% per-fyearq: verified in CompustatEngine ✓
- DivDummy excluded from winsorization (binary) ✓
- Linguistic IVs 0%/99% per-year upper-only: verified in `_linguistic_engine.py` lines 255-257 ✓
- CCCL DV and CCCL_lag not winsorized (binary) ✓
- DailyVola not winsorized at Compustat level (CRSP-sourced) ✓
**PASS**

**H2. Missing Data Policy:**
- Inf→NaN: runner line 199: `df = panel.replace([np.inf, -np.inf], np.nan)` ✓
- Complete-case deletion: runner lines 207-209 ✓
- Missing xrdq→0 (CompustatEngine): engine line 972: `comp["xrdq"].fillna(0) / comp["atq"]` ✓
- Missing dlcq/dlttq→0 (CompustatEngine): engine lines 988-989: `fillna(0)` ✓
- Patsy implicit drop for NaN in formula variables: noted in H2 ✓
**PASS**

**H3. Transformations:**
- lnAssets: ln(atq) ✓
- DailyVola: annualized (*sqrt(252)) and percentage (*100) ✓
- AMEs = dy/dx post-estimation ✓
- No centering/z-scoring ✓
**PASS**

**Phase 7 Result: 13/15 PASS** (2 FAIL: F3 builder count error — "15" should be "16"; and the same inconsistency between F1 and F3 counted in Phase 11)

---

## PHASE 8: TABLE GENERATOR ENTRY (Section I)

Doc transcription:
```python
{
    "id": "H18b",
    "dir": "h18b_cccl_logit/2026-03-31_195228",
    "caption": "H18b: Logit Robustness --- Speech Uncertainty and SEC Comment Letters",
    "label": "tab:h18b",
    "cols": 2,
    "dvs": [(r"CCCL", 2)],
    "tail": "one",
    "hyp_dir": ">",
    "r2_label": r"Pseudo~$R^2$",
    "skip_adj_r2": True,
},
```

Actual `outputs/generate_all_tables.py` lines 370-384 (verified by direct read):
```python
# ── H18b (Logit robustness) ──
{
    "id": "H18b",
    "dir": "h18b_cccl_logit/2026-03-31_195228",
    "caption": "H18b: Logit Robustness --- Speech Uncertainty and SEC Comment Letters",
    "label": "tab:h18b",
    "cols": 2,
    "dvs": [
        (r"CCCL", 2),
    ],
    "tail": "one",
    "hyp_dir": ">",
    "r2_label": r"Pseudo~$R^2$",
    "skip_adj_r2": True,
},
```

Verification:
- `id: "H18b"` ✓
- `dir` matches run timestamp ✓
- `caption` exact match ✓
- `label: "tab:h18b"` ✓
- `cols: 2` matches `len(MODEL_SPECS) = 2` ✓
- `dvs: [(r"CCCL", 2)]` — single DV across both cols ✓
- `tail: "one"` matches runner one-tailed test ✓
- `hyp_dir: ">"` matches beta > 0 direction ✓
- `r2_label: r"Pseudo~$R^2$"` — runner writes `pseudo_r2` to txt file; label override is correct ✓
- `skip_adj_r2: True` — runner writes identical value for both R-squared and Adj_R2 (lines 378-379); table generator instructed to skip duplicate ✓
- No `key_vars` field in code or doc — correct absence (logit with 4 simultaneous IVs, all equally reported) ✓

Doc correctly notes line numbers 370-384 for the generate_all_tables.py entry ✓.

**Phase 8 Result: 6/6 PASS**

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

**Correct family: Logit → K3 should be filled**

Doc fills K3 (Logit/Probit/LPM) and marks K1, K2, K4, K5, K6 as N/A.

The creation prompt offers K3 for Logit/Probit/LPM and K6 for "Other Model Family". Since statsmodels Logit is explicitly listed under K3's scope, using K3 is correct.

**K3 content verification:**

**Link function:** "Logistic (sigmoid). smf.logit() uses the logistic CDF." — correct for smf.logit ✓

**Binary outcome construction:** "CCCL ∈ {0, 1}; identical to H18 LPM." — builder creates 0.0/1.0 float values ✓

**Separation handling:**
- "~95% of firms have CCCL=0 for all observations" — matches runner docstring line 18 ✓
- "26 of 67 quarters have zero CCCL events" — matches runner docstring line 20 ✓
- "Only Industry FE + Calendar Year FE are feasible" — matches MODEL_SPECS ✓
- Per-FE-group zero-event warnings at runtime (runner lines 259-263) ✓
- Timoneda (2021) citation consistent with runner docstring ✓

**Marginal effects computation:** 
- `model.get_margeff(at="overall")` — verified at runner line 305 ✓
- "`at='overall'` is the statsmodels default" — verified: `def get_margeff(self, at='overall', ...)` in statsmodels source ✓
- AME columns `dy/dx`, `Std. Err.`, `z`, `Pr(>|z|)` — verified at runner lines 311-313 ✓
- Delta method for AME SEs ✓

**Pseudo-R-squared type:** 
- "McFadden's pseudo-R² = 1 - (log-likelihood of fitted model) / (log-likelihood of intercept-only model)" ✓
- "Accessed via `model.prsquared` (runner line 279)" — line 279 is `print(f"  Pseudo R²: {model.prsquared:.6f}")`. The actual storage is at `meta["pseudo_r2"] = float(model.prsquared)` (line 292). Minor imprecision (line 279 is print, not storage), but confirmed `model.prsquared` is the access method ✓
- Written as both R-squared and Adj_R2 (runner lines 378-379) ✓
- `skip_adj_r2: True` in table generator ✓

**Log-odds vs AMEs:** Both stored — `model.params` for log-odds (line 300), `mfx_df["dy/dx"]` for AMEs (line 311) ✓

**Optimizer:** BFGS, maxiter=300, disp=False, convergence via `model.mle_retvals.get("converged", False)` (line 276) ✓

**K1, K2, K4, K5, K6:** All marked N/A ✓

**Phase 9 Result: 8/8 PASS**

---

## PHASE 10: QUALITY GATES

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | MOSTLY MET | All spec variables in dictionary; fyearq_int absent (minor); TobinsQ formula wrong; ROA fallback wrong |
| 2 | The model equation matches what the code actually estimates | PASS | B1 equation verified against Patsy formula construction in runner |
| 3 | The specification register accounts for every model column | PASS | 2 specs in MODEL_SPECS, 2 rows in spec register |
| 4 | The attrition cascade has row counts for each filter step | PASS | 4 steps with N counts sourced from actual run output |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | PASS | Runner: one-tailed ame_p_two/2 when ame>0; GAT: tail="one", hyp_dir=">" |
| 6 | The FE specification matches between docstring, code, and this document | PASS | Docstring: Industry + Cal Yr; code: C(ff12_code) + C(cal_yr); doc: same |
| 7 | Every merge in the panel builder is documented with join keys and type | FAIL | F3 lists 15 builder outputs but code has 16; F1 and F3 are internally inconsistent |
| 8 | The output file list matches what the runner actually writes | PASS | G2 lists 8 file entries covering all 9 runner write operations |
| 9 | The model-family addendum is filled for the correct family only | PASS | K3 filled; K1/K2/K4/K5/K6 = N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation | PASS | No [UNVERIFIED] markers; all claims verified or explicitly cited to run output |

**Phase 10 Result: 8/10 PASS** (2 FAIL: QG1 has TobinsQ/ROA formula errors; QG7 has merge count error)

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

1. **DVs in B2 match DVs in C?**
   B2: `CCCL`. C: Col 1 and Col 2 both DV=`CCCL`. **CONSISTENT ✓**

2. **DVs in C match DVs in I?**
   C: `CCCL`. I: `"dvs": [(r"CCCL", 2)]` — CCCL across both columns. **CONSISTENT ✓**

3. **Controls in B4 match variables in E?**
   B4 lists: lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, DivDummy, sCFO, Lagged_DV (base) + SalesGrowth, RDSales, CashFlowAt, DailyVola (extended).
   E table contains all 13 control variables. **CONSISTENT ✓** (formula errors present in both, internally consistent)

4. **Column count in A matches rows in C?**
   A: `Columns: 2`. C: 2 rows. **CONSISTENT ✓**

5. **Column count in A matches "cols" in I?**
   A: `Columns: 2`. I: `"cols": 2`. **CONSISTENT ✓**

6. **Tail direction in A matches B7 matches I?**
   A: `Direction: One-tailed (beta > 0)`. B7: `ame_p_one = ame_p_two / 2 if ame > 0`. I: `"tail": "one", "hyp_dir": ">"`. **CONSISTENT ✓**

7. **FE in B5 matches C matches K?**
   B5: `C(ff12_code) + C(cal_yr)`. C: "FF12 dummies | Cal Year dummies | No firm FE | No year-qtr FE". K3: "Industry FE with 12 categories feasible; Calendar Year FE feasible". **CONSISTENT ✓**

8. **Panel index in A matches set_index in K?**
   A: `Panel Index: None`. K3 section confirms no panel index for logit. Runner has no `set_index()` call. **CONSISTENT ✓**

9. **F1 builder count vs F3 builder count — INTERNAL INCONSISTENCY:**
   F1 step 3: "Merges **16** builder outputs on `file_name`"
   F3 merge table: "each of **15** builder outputs"
   Actual code: 16 non-manifest builders.
   F1 is correct; F3 is wrong. Internal contradiction within Section F. **FAIL ✓**

**Phase 11 Result: 7/8 PASS** (1 FAIL: F1 vs F3 internal inconsistency on builder count)

---

## CORRECTIONS REQUIRED

### Correction 1 (HIGH): Fix TobinsQ formula in Section B4

**Location:** Section B4, Base Controls table, TobinsQ row
**Current wrong text:** `(atq + cshoq*prccq - ceqq) / atq`
**Correct text:** `(cshoq*prccq + dlcq + dlttq) / atq` (where dlcq and dlttq are clipped at 0 and treated as 0 when missing unless both are NaN)
**Code reference:** `_compustat_engine.py` lines 987-997

The source fields column must also be corrected:
**Current wrong text:** `CompustatEngine: atq, cshoq, prccq, ceqq`
**Correct text:** `CompustatEngine: atq, cshoq, prccq, dlcq, dlttq` (ceqq is NOT used; dlcq and dlttq are required instead)

**Root cause:** The doc copied the formula from the engine's header comment (line 25: "Fixed to (atq + cshoq*prccq - ceqq)/atq which matches v2 design") which is itself an outdated comment. The actual code was changed after that comment was written and now uses book debt, not book equity.

### Correction 2 (HIGH): Fix TobinsQ formula in Section E (Variable Dictionary)

**Location:** Section E, TobinsQ row — formula and source columns
**Current wrong text (formula):** `(atq + cshoq*prccq - ceqq) / atq; uses cshoq*prccq (shares * price) for market equity`
**Correct text (formula):** `(cshoq*prccq + dlcq + dlttq) / atq; where dlcq and dlttq are clipped at 0 and fillna(0) per component, NaN if both missing`
**Current wrong text (source):** `CompustatEngine: atq, cshoq, prccq, ceqq`
**Correct text (source):** `CompustatEngine: atq, cshoq, prccq, dlcq, dlttq`
**Code reference:** `_compustat_engine.py` lines 987-997

### Correction 3 (MEDIUM): Fix ROA fallback claim in Section B4

**Location:** Section B4, Base Controls table, ROA row, Formula column
**Current wrong text:** `iby_annual (Q4 row only) / avg(atq_t, atq_{t-1}); avg_assets falls back to atq_t when prior year missing`
**Correct text:** `iby_annual (Q4 row only) / avg(atq_t, atq_{t-1}); ROA is NaN when prior year atq is missing (no fallback)`
**Code reference:** `_compustat_engine.py` lines 959-969 — no fallback logic present, in contrast to CashFlowAt which has explicit fallback at line 686

### Correction 4 (MEDIUM): Fix ROA fallback claim in Section E (Variable Dictionary)

**Location:** Section E, ROA row, Formula column
**Current wrong text:** `iby_annual (Q4 row only) / avg(atq_t, atq_{t-1}); avg_assets falls back to atq_t when prior year missing`
**Correct text:** `iby_annual (Q4 row only) / avg(atq_t, atq_{t-1}); NaN when prior year atq missing (no fallback — contrast with CashFlowAt)`
**Code reference:** `_compustat_engine.py` lines 959-969

### Correction 5 (MEDIUM): Fix builder count in Section F3

**Location:** Section F3, Merge Operations table, Row 1 (manifest + builders)
**Current wrong text:** `manifest (base panel) | each of 15 builder outputs | file_name | left`
**Correct text:** `manifest (base panel) | each of 16 builder outputs | file_name | left`
**Code reference:** `build_h18_cccl_received_panel.py` lines 158-184 — `builders` dict has 17 entries: 1 manifest + 16 non-manifest builders (manager_qa_uncertainty, manager_pres_uncertainty, ceo_qa_uncertainty, ceo_pres_uncertainty, size, book_lev, tobins_q, roa, cash_holdings, capex_intensity, dividend_payer, ocf_volatility, sales_growth, rd_intensity, cash_flow, volatility)
**Internal consistency note:** F1 step 3 correctly says "16 builder outputs"; F3 must be corrected to match.

### Correction 6 (LOW): Fix cov_kwds line citation in Section B6

**Location:** Section B6, bullet point for cov_kwds
**Current wrong text:** "cov_kwds={"groups": df_prepared["gvkey"].values} (runner line 271)"
**Correct text:** "cov_kwds={"groups": df_prepared["gvkey"].values} — on same line as cov_type (runner line 270)"
**Code reference:** `run_h18b_cccl_logit.py` line 270: `cov_type="cluster", cov_kwds={"groups": df_prepared["gvkey"].values},`; line 271 is just `)`

### Correction 7 (LOW): Fix get_margeff line citation in Section F1 step 6 and K3

**Location:** Section F1 step 6 and Section K3 (marginal effects computation paragraph)
**Current wrong text:** "model.get_margeff(at=\"overall\") (runner line 306)"
**Correct text:** "model.get_margeff(at=\"overall\") (runner line 305)"
**Code reference:** `run_h18b_cccl_logit.py` line 305: `mfx = model.get_margeff(at="overall")`; line 306 is `mfx_df = mfx.summary_frame()`

---

## ADDITIONAL OBSERVATIONS (not failures, but notes for completeness)

**Note 1: Engine header comment is misleading**
`_compustat_engine.py` lines 24-27 contain an outdated comment: "Fixed to (atq + cshoq*prccq - ceqq)/atq which matches v2 design." This comment no longer reflects the actual code at lines 987-997. This is a documentation debt in the engine itself (outside the scope of H18b provenance), but it caused the provenance doc error. The engine comment should be updated to reflect the actual formula.

**Note 2: fyearq_int absent from Variable Dictionary**
`fyearq_int` appears in the `required` columns list (runner line 193) and is used for the complete-case check, but is not listed in the Variable Dictionary (Section E). Its construction is documented in F1 step 3 ("Converts `fyearq` to numeric as `fyearq_int`"). This is a minor gap — the Quality Gate requires dictionary entries for "every variable in every regression spec," and `fyearq_int` is not in any regression formula. However, a complete dictionary would include it as a "filter variable." This is a borderline issue, not cited as a formal failure.

**Note 3: Pseudo-R² line citation in K3**
K3 says "Accessed via `model.prsquared` (runner line 279)." Line 279 is the print statement; the actual stored value is at line 292: `meta["pseudo_r2"] = float(model.prsquared)`. The `.prsquared` attribute is correct; the line number is the print rather than the storage assignment. Very minor.

**Note 4: Leverage missing-value edge case**
Doc says "missing dlcq or dlttq treated as 0." The actual code uses `fillna(0)` on individual components but preserves NaN if BOTH dlcq AND dlttq are NaN (engine line 990: `np.where(comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, ...)`). The doc's simplification is slightly inaccurate (would imply 0/atq=0 in the both-null case, but actual result is NaN). This is a low-severity imprecision but not counted as a formal failure given the acceptable simplification convention.

**Note 5: AME `at="overall"` default**
The doc claims `at="overall"` is the statsmodels default. Verified via statsmodels source: `def get_margeff(self, at='overall', ...)`. Confirmed correct.

**Note 6: L7 event count discrepancy**
Known Issue 7 in the doc explains that col 2 has 196 events vs col 1's 200 events because extended-controls complete-case filtering drops some CCCL=1 rows. This is correctly documented.
