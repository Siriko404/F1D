# Audit Report: H3 — Payout Policy

**Suite ID:** H3
**Audit date:** 2026-02-28
**Auditor:** Adversarial manual audit (claim-by-claim)
**Artifacts audited:**
- Stage 3 panel: `outputs/variables/h3_payout_policy/2026-02-27_223717/`
- Stage 4 results: `outputs/econometric/h3_payout_policy/2026-02-27_223841/`
- Prior Stage 4 run: `outputs/econometric/h3_payout_policy/2026-02-27_151907/`

---

## 1) Executive Summary

| # | Finding | Severity |
|---|---------|----------|
| 1 | **`div_stability` formula: provenance/docstring claims `-StdDev(Delta DPS)/|Mean(DPS)|` but code computes `-StdDev(lagged payout ratio)`** — these are fundamentally different measures. The paper must describe the correct formula. | **MAJOR** |
| 2 | **LaTeX table Within-R² values are inflated** — manual double-demeaned R² (0.176 for Main/DS) is reported instead of linearmodels `rsquared_within` (0.016). The manual computation is not the standard within-R² used in econometrics. | **MAJOR** |
| 3 | `model_diagnostics.csv` column `rsquared_adj` is actually `model.rsquared_inclusive` (overall R² including FE), not adjusted R². Mislabeled internal artifact. | MINOR |
| 4 | README line 303 says "H3b: 2/12 significant interactions" — actual count is 3/36 (provenance is correct). README denominator and numerator are both wrong. | MINOR |
| 5 | Test file `test_h3_regression.py` assumes centered interaction terms; actual runner uses uncentered raw product. Tests do not cover actual code path. | MINOR |
| 6 | Prior run drift (N_obs up to +1,029) explained by updated Stage 2 linguistic variables between Stage 3 rebuilds — not a bug. | NOTE |
| 7 | No reruns required for correctness — regression coefficients, p-values, and significance calls are all correct and internally consistent. | NOTE |

**Are results trustworthy as-is?** YES, with caveats:
- The regression coefficients, standard errors, p-values, and significance decisions are all correct and internally consistent across txt/CSV/LaTeX artifacts.
- The `div_stability` variable works as coded (negative SD of lagged payout ratio) and is a valid measure of dividend stability — but the provenance and docstring must be corrected to match.
- The LaTeX Within-R² values should be replaced with the standard linearmodels `rsquared_within` or clearly labeled as "double-demeaned R²."

**What must be rerun?** Nothing mandatory. The findings are documentation/labeling issues, not computational errors. However:
- If `div_stability` formula is changed to match provenance (unlikely), Stage 3 + Stage 4 must be rerun.
- If Within-R² in LaTeX is corrected to use `rsquared_within`, only the LaTeX generation code needs updating (no rerun of regressions).

---

## 2) Suite Contract (what H3 claims it does)

| Field | Value |
|---|---|
| **Estimation unit** | Earnings call (one row per `file_name`) |
| **Primary keys** | `file_name` (unique), `gvkey` + `year` (panel index, non-unique due to multiple calls per firm-year) |
| **Sample filters** | FF12 industry split (Main/Finance/Utility); `is_div_payer_5yr == 1`; `MIN_CALLS >= 5` per firm; complete-case listwise deletion |
| **Dependent variables** | `div_stability_lead` (t+1 fiscal year); `payout_flexibility_lead` (t+1 fiscal year) |
| **Main RHS** | 6 uncertainty measures: Manager/CEO x QA_Uncertainty/QA_Weak_Modal/Pres_Uncertainty |
| **Interaction** | `Uncertainty_x_Lev = Uncertainty * Lev` (uncentered raw product) |
| **Controls** | `earnings_volatility`, `fcf_growth`, `firm_maturity`, `Size`, `ROA`, `TobinsQ`, `CashHoldings` |
| **Fixed effects** | Entity (firm) + Time (year) via `PanelOLS` `EntityEffects + TimeEffects` |
| **Standard errors** | Firm-clustered (`cov_type="clustered"`, `cluster_entity=True`) |
| **Total models** | 36 = 2 DVs x 3 samples x 6 uncertainty measures |
| **Hypothesis tests** | One-tailed: H3a (beta1 direction depends on DV), H3b (beta3 direction depends on DV) |
| **Expected outputs** | 36 regression_results txt + model_diagnostics.csv + h3_payout_policy_table.tex + summary_stats.csv/.tex |

---

## 3) Verification Matrix

| # | Claim | Where claimed | Where checked | Status | Notes |
|---|-------|---------------|---------------|--------|-------|
| 1 | Panel has 112,968 rows | H3.md:137 | `python -c "len(df)"` on panel parquet | **PASS** | Exact: 112,968 rows, 31 columns |
| 2 | `file_name` is unique (zero duplicates) | H3.md:137, 170, 180 | `df['file_name'].is_unique` | **PASS** | 0 duplicates confirmed |
| 3 | Zero row-delta on all merges | H3.md:137, 154 | Code trace: `build_h3_payout_policy_panel.py:227-228` raises `ValueError` on non-zero delta | **PASS** | Hard-fail enforcement verified in code |
| 4 | Sample split: Main 88,205 / Finance 20,482 / Utility 4,281 | H3.md:170, 396 | `df['sample'].value_counts()` | **PASS** | Exact match |
| 5 | `div_stability_lead` valid: 86,459 (76.5%) | H3.md:201 | `df['div_stability_lead'].notna().sum()` | **PASS** | 86,459 confirmed |
| 6 | `payout_flexibility_lead` valid: 105,301 (93.2%) | H3.md:201 | `df['payout_flexibility_lead'].notna().sum()` | **PASS** | 105,301 confirmed |
| 7 | `is_div_payer_5yr`: 64,553 payers / 48,302 non-payers / 113 NaN | H3.md:211-215 | `df['is_div_payer_5yr'].value_counts(dropna=False)` | **PASS** | Exact match |
| 8 | `div_stability_lead` all <= 0 (negated SD) | H3.md:350 | `(valid <= 0).all()` | **PASS** | Range [-18.10, -0.0] |
| 9 | `payout_flexibility_lead` in [0, 1] | H3.md:352 | `((valid >= 0) & (valid <= 1)).all()` | **PASS** | Range [0.0, 1.0] |
| 10 | 36 regression models run | H3.md:142, 372-380 | `len(diag) == 36` and 36 txt files | **PASS** | Exact |
| 11 | PanelOLS with EntityEffects + TimeEffects | H3.md:368 | Code: `run_h3_payout_policy.py:189,205` | **PASS** | Formula confirmed |
| 12 | Firm-clustered SEs (`cluster_entity=True`) | H3.md:21, 368 | Code: `run_h3_payout_policy.py:206` | **PASS** | `cov_type="clustered", cluster_entity=True` |
| 13 | `MIN_CALLS = 5` filter | H3.md:156 | Code: `run_h3_payout_policy.py:82,593` | **PASS** | `gvkey_count >= CONFIG["min_calls"]` |
| 14 | `is_div_payer_5yr == 1` filter applied at regression time | H3.md:217 | Code: `run_h3_payout_policy.py:170` | **PASS** | `df = df[df["is_div_payer_5yr"] == 1]` |
| 15 | H3a: 1/36 significant | H3.md:380 | `diag['h3a_sig'].sum() == 1` | **PASS** | Finance/payout_flexibility/Manager_QA_Unc |
| 16 | H3b: 3/36 significant | H3.md:380 | `diag['h3b_sig'].sum() == 3` | **PASS** | Main/DS/Mgr_QA, Main/DS/CEO_QA, Utility/PF/CEO_Pres |
| 17 | One-tailed p-value logic correct | H3.md:26-31 | Manual recomputation: `p_two/2 if sign correct else 1-p_two/2` | **PASS** | Verified for both H3a and H3b directions |
| 18 | Lead variables use consecutive-year validation | H3.md:198 | Spot-check: gap>1 rows have NaN leads | **PASS** | 260 gap rows, all have NaN leads |
| 19 | Lead variables = next fiscal year's value | H3.md:190-198 | Spot-check: 17,304 (div_stab) / 23,883 (payout_flex) rows verified, max diff < 1e-10 | **PASS** | Perfect match |
| 20 | `div_stability` formula = `-StdDev(Delta DPS) / |Mean(DPS)|` | H3.md:242, `_compustat_engine.py:763` | Code trace: `_compustat_engine.py:857-865` | **FAIL** | Code computes `-StdDev(lagged payout ratio)` — different formula |
| 21 | LaTeX table coefficients match model_diagnostics.csv | H3.md:71 | Cross-check all 4 LaTeX columns | **PASS** | Perfect match for beta1, beta3, N, R² |
| 22 | Regression txt coefficients match model_diagnostics.csv | H3.md:72 | Cross-check Main/DS/Mgr_QA txt vs CSV | **PASS** | N=35,353, beta1=0.0976, beta3=-0.3326 |
| 23 | LaTeX Within-R² = standard within-R² | Implicit | linearmodels `rsquared_within` vs LaTeX value | **FAIL** | LaTeX uses manual double-demeaned R² (0.176), not linearmodels within-R² (0.016) |
| 24 | Year range 2002-2018 | H3.md:396 | `df['year'].min()`, `df['year'].max()` | **PASS** | 2002-2018 confirmed |
| 25 | Per-year 1%/99% winsorization at engine level | H3.md:309-311 | Code trace: `_compustat_engine.py:_winsorize_by_year()` | **PASS** | Confirmed in CompustatEngine; linguistic at upper 99th only |
| 26 | No additional winsorization at panel or regression level | H3.md:309 | Code trace: no `.clip()` or winsorize calls in builder or runner | **PASS** | Consistent with repo policy |
| 27 | `merge_asof` in `attach_fyearq` uses backward direction | H3.md:154-155 | Code: `panel_utils.py:158` `direction="backward"` | **PASS** | No look-ahead bias |
| 28 | Random seed 42, thread_count 1 | H3.md:90-91 | `config/project.yaml` | **PASS** | `random_seed: 42, thread_count: 1` |
| 29 | `model_diagnostics.csv` column `rsquared_adj` = adjusted R² | Implicit (column name) | Code: `run_h3_payout_policy.py:313` | **FAIL** | Actually stores `model.rsquared_inclusive` (overall R² with FE) |

---

## 4) Findings (grouped by severity)

### FINDING 1: `div_stability` Formula Mismatch (MAJOR)

**Severity:** MAJOR

**Symptom:** Provenance Section F.1 and code docstring (`_compustat_engine.py:763`) describe `div_stability` as:
> `-StdDev(Delta DPS) / |Mean(DPS)|` over trailing 5 years

But the actual code implementation (`_compustat_engine.py:841-865`) computes:
```
payout_ratio = dvy / iby           # total dividends / income before extraordinary items
payout_ratio_lag = shift(1)        # lagged 1 year within gvkey
std_payout = rolling("1826D", min_periods=3).std() of payout_ratio_lag
div_stability = -std_payout
```

**Evidence:**
- `_compustat_engine.py:763` — docstring claims `-StdDev(Delta DPS) / |Mean(DPS)|`
- `_compustat_engine.py:841-843` — computes `payout_ratio = dvy / iby`
- `_compustat_engine.py:844` — lags by 1 year
- `_compustat_engine.py:858-865` — rolling SD of lagged payout ratio, negated
- `docs/provenance/H3.md:242` — repeats the incorrect formula

**Why it matters:**
1. `StdDev(Delta DPS) / |Mean(DPS)|` is a coefficient of variation of DPS changes — measures normalized volatility of dividend changes
2. `StdDev(lagged payout ratio)` is the volatility of the lagged payout ratio itself — measures how much the payout ratio level varies
3. These are conceptually and numerically different. The paper must describe the correct formula.
4. The variable `payout_ratio` uses total dividends (`dvy`) and income (`iby`), NOT dividends per share (DPS/`dvpspq`), adding another discrepancy with the docstring.

**How to verify:**
```bash
python -c "
# Read lines 841-865 of _compustat_engine.py
# Confirm payout_ratio = dvy/iby, not DPS-based
# Confirm rolling SD is on payout_ratio_lag, not delta_dps
"
```

**Fix:**
- Option A (recommended): Update provenance F.1, docstring at line 763, and paper text to match code: `div_stability = -StdDev(lagged payout ratio) over trailing 5 fiscal years`
- Option B: Change code to match docstring — would require Stage 3 + Stage 4 rerun

**Rerun impact:** None if Option A (documentation fix). Full rerun if Option B.

---

### FINDING 2: LaTeX Table Within-R² is Inflated (MAJOR)

**Severity:** MAJOR

**Symptom:** The LaTeX table (`h3_payout_policy_table.tex`) reports "Within-R²" values that are 10-50x higher than the standard `rsquared_within` from `linearmodels.PanelOLS`.

| Model | linearmodels `rsquared_within` | Manual "within_r2" (in LaTeX) | Ratio |
|-------|-------------------------------|-------------------------------|-------|
| Main/DS/Mgr_QA | 0.0157 | 0.1762 | 11.2x |
| Main/DS/CEO_QA | 0.0183 | 0.1813 | 9.9x |
| Main/PF/Mgr_QA | 0.0450 | 0.8978 | 20.0x |
| Finance/DS/Mgr_QA | 0.0314 | 0.3383 | 10.8x |
| Utility/DS/Mgr_QA | 0.0520 | 0.4914 | 9.5x |

**Evidence:**
- `run_h3_payout_policy.py:226-240` — manual R² computation double-demeans both `y` and `y_hat` by entity AND time
- `run_h3_payout_policy.py:312` — stores `float(model.rsquared_within)` as `rsquared`
- `run_h3_payout_policy.py:314` — stores manual value as `within_r2`
- `run_h3_payout_policy.py:474-477` — LaTeX table uses `within_r2` (the inflated manual value)
- Regression txt headers show `R-squared (Within): 0.0157` — the linearmodels standard value

**Why it matters:**
- The standard within-R² for panel FE models (as computed by linearmodels) measures the fraction of within-entity variation explained by exogenous regressors after absorbing entity FE
- The manual computation double-demeans by both entity and time, reducing the total sum of squares denominator, which inflates the R² measure
- Reporting 0.176 instead of 0.016 materially misrepresents model fit
- For `payout_flexibility_lead`, the manual R² (0.898) suggests near-perfect fit, while the standard within-R² (0.045) shows regressors explain very little

**How to verify:**
```bash
python -c "
import pandas as pd
diag = pd.read_csv('outputs/econometric/h3_payout_policy/2026-02-27_223841/model_diagnostics.csv')
print(diag[['sample','dv','uncertainty_measure','rsquared','within_r2']].head(6))
# rsquared = linearmodels standard; within_r2 = manual inflated
"
```

**Fix:** In `run_h3_payout_policy.py`, change LaTeX table generation (lines 474-477) to use `model.rsquared_within` instead of the manual `within_r2`. Alternatively, label the manual R² as "Double-demeaned R²" to avoid confusion.

**Rerun impact:** LaTeX table regeneration only (no regression rerun needed). Change `_save_latex_table()` to use `rsquared` instead of `within_r2` from meta dict.

---

### FINDING 3: `rsquared_adj` Column Mislabeled in model_diagnostics.csv (MINOR)

**Severity:** MINOR

**Symptom:** `model_diagnostics.csv` column `rsquared_adj` stores `model.rsquared_inclusive` (R² including entity+time effects), not the adjusted R².

**Evidence:**
- `run_h3_payout_policy.py:313` — `"rsquared_adj": float(model.rsquared_inclusive)`
- For Main/DS/Mgr_QA: `rsquared_adj = 0.452` — this is `rsquared_inclusive` (overall model R² with FE), not adjusted R²

**Fix:** Rename column to `rsquared_inclusive` in the meta dict at line 313.

**Rerun impact:** None (cosmetic fix to internal artifact).

---

### FINDING 4: README H3 Summary Inaccurate (MINOR)

**Severity:** MINOR

**Symptom:** README.md line 303 says "H3b: 2/12 significant interactions" but the actual count is 3/36.

**Evidence:**
- `README.md:303` — "H3b: 2/12 significant interactions"
- `README.md:411-412` — detailed table shows "H3b: 2/6" for Main div_stability only (this cell is correct)
- `model_diagnostics.csv` — `h3b_sig.sum() == 3` across 36 total models
- `docs/provenance/H3.md:380` — correctly states "H3b: 3/36"

**Fix:** Update README line 303 to "H3b: 3/36 significant interactions" or "H3b: limited support (3/36)".

**Rerun impact:** None (documentation fix).

---

### FINDING 5: Test File Assumes Centered Interactions (MINOR)

**Severity:** MINOR

**Symptom:** `test_h3_regression.py` (lines 177-182) tests interaction term creation using centered variables (`Uncertainty_c * leverage_c`), but the actual runner (`run_h3_payout_policy.py:172-173`) uses uncentered raw products (`Uncertainty * Lev`).

**Evidence:**
- `test_h3_regression.py:177-178` — centers both uncertainty and leverage by subtracting means
- `test_h3_regression.py:182` — creates interaction from centered values
- `run_h3_payout_policy.py:172` — `df["Uncertainty"] = df[uncertainty_var]` (raw, no centering)
- `run_h3_payout_policy.py:173` — `df["Uncertainty_x_Lev"] = df["Uncertainty"] * df["Lev"]` (raw product)

**Why it matters:**
- Centering does NOT affect the interaction coefficient (beta3) — H3b results are unaffected
- Centering DOES affect beta1 and beta2 interpretation: in the uncentered model, beta1 = effect of Uncertainty when Lev=0, not at mean Lev
- The test file does not exercise the actual code path, reducing test coverage value

**Fix:** Update test to match actual code (uncentered interactions), or add centering to the runner (and rerun).

**Rerun impact:** None if tests are updated. Stage 4 rerun if centering is added to runner.

---

### FINDING 6: Prior Run Drift Explained (NOTE)

**Severity:** NOTE

**Symptom:** Comparing Stage 4 runs `2026-02-27_151907` vs `2026-02-27_223841`, N_obs differs by up to +1,029 and coefficients differ by up to 0.064.

**Evidence:**
- Both runs: 36 models each
- N_obs diff: max +1,029 (Main/PF/Manager_Pres_Uncertainty)
- Beta1 diff: max 0.025
- Beta3 diff: max 0.064
- Root cause: Stage 3 panel `2026-02-26_101916` had fewer non-null linguistic variables (e.g., Manager_QA_Uncertainty: 105,482 vs 108,215 = +2,733 more in latest)
- Linguistic variable improvement came from updated Stage 2 outputs between 2026-02-26 and 2026-02-27

**Why it matters:** This is NOT a bug — it reflects a legitimate upstream data update. The `get_latest_output_dir()` mechanism correctly resolved different Stage 3 panels for each Stage 4 run.

**Fix:** No fix needed. Document in provenance that results depend on Stage 2 linguistic variable coverage.

---

## 5) Rerun Plan

### Current state: No mandatory rerun required

The regression results are computationally correct. All findings are documentation/labeling issues.

### If fixes are applied:

```bash
# Step 1: Fix documentation (Finding 1, 3, 4) — no rerun needed
# Edit docs/provenance/H3.md Section F.1 div_stability formula
# Edit _compustat_engine.py:763 docstring
# Edit README.md:303
# Edit run_h3_payout_policy.py:313 column name

# Step 2: Fix LaTeX R² (Finding 2) — regenerate LaTeX only
# Edit run_h3_payout_policy.py to use rsquared instead of within_r2 in _save_latex_table()
# Then rerun Stage 4:
python -m f1d.econometric.run_h3_payout_policy

# Step 3: Fix tests (Finding 5) — update test file only
# Edit tests/unit/test_h3_regression.py to use uncentered interactions
```

### Acceptance tests after rerun:

| Test | Command | Expected |
|------|---------|----------|
| Panel row count | `python -c "import pandas as pd; df=pd.read_parquet('...panel.parquet'); print(len(df))"` | 112,968 |
| `file_name` unique | `python -c "...print(df['file_name'].is_unique)"` | True |
| Model count | `python -c "...diag=pd.read_csv('...diagnostics.csv'); print(len(diag))"` | 36 |
| H3a sig count | `diag['h3a_sig'].sum()` | 1 |
| H3b sig count | `diag['h3b_sig'].sum()` | 3 |
| Main/DS/Mgr_QA beta1 | `diag[...]['beta1']` | 0.0976 (tolerance ±0.001) |
| Main/DS/Mgr_QA beta3 | `diag[...]['beta3']` | -0.3326 (tolerance ±0.001) |
| LaTeX R² matches linearmodels | Compare `rsquared` column vs LaTeX Within-R² | Must match after fix |
| Txt N matches CSV N | Cross-check any regression txt vs diagnostics | Must match exactly |

---

## 6) Hardening Recommendations

### 6.1 Suite-Level

| # | Recommendation | Priority |
|---|---------------|----------|
| 1 | **Add within-R² assertion**: assert `abs(within_r2 - model.rsquared_within) < 0.01` or remove manual computation entirely | High |
| 2 | **Add interaction centering option**: provide a `center_interaction=True` flag in CONFIG to support both centered and uncentered specifications | Medium |
| 3 | **Log panel path in Stage 4 output**: write the actual panel path used to a metadata file in the Stage 4 output directory, so panel-to-results traceability is guaranteed | High |
| 4 | **Add docstring-vs-code formula tests**: unit test that `div_stability` values match the documented formula by computing on synthetic data | High |
| 5 | **Assert `is_div_payer_5yr` is binary**: add `assert df['is_div_payer_5yr'].isin([0.0, 1.0, np.nan]).all()` in panel builder | Low |

### 6.2 Repo-Level

| # | Recommendation | Priority |
|---|---------------|----------|
| 1 | **Standardize R² reporting**: choose either `model.rsquared_within` or a clearly labeled alternative, and use consistently across all Stage 4 suites | High |
| 2 | **Add panel provenance hash**: write SHA-256 of input panel to Stage 4 output directory for reproducibility audit | Medium |
| 3 | **Add Stage 3 → Stage 4 linkage test**: CI test that verifies `get_latest_output_dir()` resolves the expected panel | Medium |
| 4 | **Reconcile test centering with code**: audit all test files for code path divergence from actual runners | Medium |
| 5 | **Add formula documentation tests**: for each variable in `_compustat_engine.py`, verify docstring matches implementation on small synthetic data | High |

### 6.3 Assertions to Add

```python
# In build_h3_payout_policy_panel.py, after create_lead_variables():
assert panel['file_name'].is_unique, "file_name must be unique"
assert len(panel) == 112_968, f"Expected 112,968 rows, got {len(panel)}"
assert (panel['div_stability_lead'].dropna() <= 0).all(), "div_stability_lead must be <= 0"
assert panel['payout_flexibility_lead'].dropna().between(0, 1).all(), "payout_flexibility_lead must be in [0,1]"

# In run_h3_payout_policy.py, after regression:
assert int(model.nobs) == len(df_filtered), "model nobs must match filtered data"
```

### 6.4 Tests to Add

| Test | File | Description |
|------|------|-------------|
| `test_div_stability_formula` | `tests/unit/test_compustat_engine.py` | Compute `div_stability` on synthetic Compustat data; verify formula matches `-StdDev(lagged payout ratio)` |
| `test_uncentered_interaction` | `tests/unit/test_h3_regression.py` | Verify interaction is `Uncertainty * Lev` (raw product), not centered |
| `test_within_r2_consistency` | `tests/unit/test_h3_regression.py` | Verify manual within-R² matches linearmodels `rsquared_within` within tolerance |
| `test_latex_r2_source` | `tests/unit/test_h3_regression.py` | Verify LaTeX table uses `rsquared_within`, not manual inflated value |
| `test_panel_linkage` | `tests/integration/test_h3_e2e.py` | Run Stage 3 + Stage 4; verify Stage 4 used the expected panel file |

---

## 7) Command Log

| # | Command | Purpose | Key Result |
|---|---------|---------|------------|
| 1 | `read README.md` | Extract pipeline contract | 4-stage architecture, zero row-delta, timestamped outputs, per-year winsorization |
| 2 | `read docs/Prompts/P_Audit.txt` | Get audit instructions | Adversarial claim-by-claim audit protocol |
| 3 | `read docs/provenance/H3.md` | Extract claim register | 443-line provenance with 29+ verifiable claims |
| 4 | `read src/f1d/variables/build_h3_payout_policy_panel.py` | Trace Stage 3 builder | 20 variable builders, left-merge on file_name, lead variable construction |
| 5 | `read src/f1d/econometric/run_h3_payout_policy.py` | Trace Stage 4 runner | 36 PanelOLS regressions, one-tailed tests, LaTeX generation |
| 6 | `read src/f1d/shared/variables/payout_flexibility.py` | Trace variable builder | Delegates to CompustatEngine singleton |
| 7 | `read src/f1d/shared/variables/panel_utils.py` | Trace `attach_fyearq` and `assign_industry_sample` | merge_asof backward, file_name uniqueness guard, 80% match threshold |
| 8 | `read _compustat_engine.py:757-956` | Trace H3 variable formulas | Found div_stability formula discrepancy (Finding 1) |
| 9 | `ls outputs/variables/h3_payout_policy` | Identify Stage 3 runs | 5 runs: 2026-02-20 (x3), 2026-02-26, 2026-02-27 |
| 10 | `ls outputs/econometric/h3_payout_policy` | Identify Stage 4 runs | 9 runs: 2026-02-20 (x3), 2026-02-21 (x3), 2026-02-26, 2026-02-27 (x2) |
| 11 | `ls outputs/econometric/h3_payout_policy/2026-02-27_223841` | Verify output files | 36 txt + model_diagnostics.csv + table.tex + summary_stats.csv/.tex |
| 12 | `python -c "...df.shape, df.columns, is_unique..."` | Verify panel shape and uniqueness | 112,968 rows, 31 cols, file_name unique |
| 13 | `python -c "...isna().mean()..."` | Verify missingness rates | CEO_QA: 32%, div_stability_lead: 23.5%, all others <7% |
| 14 | `python -c "...value_counts(), year range..."` | Verify sample split and year range | Main 88,205 / Finance 20,482 / Utility 4,281; 2002-2018 |
| 15 | `python -c "...div_stability_lead <= 0, payout_flexibility in [0,1]..."` | Verify DV bounds | All constraints satisfied |
| 16 | `python -c "...cross-check diagnostics CSV vs txt..."` | Cross-artifact consistency | N, beta1, beta3, SEs all match between txt and CSV |
| 17 | `python -c "...cross-check LaTeX vs CSV..."` | Cross-artifact consistency | All 4 LaTeX columns match CSV exactly |
| 18 | `python -c "...verify one-tailed p-value logic..."` | Hypothesis test correctness | p_one = p_two/2 when sign correct; logic verified |
| 19 | `python -c "...look-ahead bias check (div_stability_lead)..."` | Lead variable correctness | 17,304 rows verified, max diff < 1e-10 |
| 20 | `python -c "...gap protection check..."` | Consecutive-year validation | 260 gap rows, all leads = NaN |
| 21 | `python -c "...payout_flexibility_lead spot-check..."` | Lead variable correctness | 23,883 rows verified, max diff < 1e-10 |
| 22 | `python -c "...count H3a/H3b significant..."` | Verify significance counts | H3a: 1/36, H3b: 3/36 (matches provenance) |
| 23 | `python -c "...prior run comparison..."` | Reproducibility check | N_obs diff up to +1,029; explained by Stage 2 update |
| 24 | `python -c "...compare prior vs latest panels..."` | Investigate drift | Same shape (112,968 x 31), linguistic vars gained ~2,700 non-null values |
| 25 | `python -c "...rsquared vs within_r2..."` | R² discrepancy check | ALL 36 models show massive discrepancy (Finding 2) |
| 26 | `python -c "...verify LaTeX star logic..."` | Star annotation correctness | Stars use one-tailed p-values, correct for hypothesis tests |
| 27 | `python -c "...div_stability formula trace..."` | Formula verification | Found MAJOR discrepancy (Finding 1) |
| 28 | `python -c "...README vs provenance discrepancy..."` | Documentation consistency | README says 2/12, provenance says 3/36 (Finding 4) |
| 29 | `python -c "...config/project.yaml..."` | Determinism settings | seed=42, thread_count=1, sort_inputs=True |
| 30 | `python -c "...high-risk checks: PanelOLS index, min_calls, inf, outliers..."` | Silent failure checks | All passed; no inf values; 53/975 firms filtered by min_calls |
| 31 | `python -c "...verify provenance significance claims..."` | Final claim verification | All 4 claimed significant results match model_diagnostics.csv |
| 32 | `read tests/unit/test_h3_regression.py` | Audit test coverage | Found centering discrepancy (Finding 5) |

---

## 8) Open Gaps

| # | Gap | What would close it |
|---|-----|---------------------|
| 1 | **Unified-info raw row count unverified** — provenance marks this UNVERIFIED | Run `python -c "import pandas as pd; print(len(pd.read_parquet('inputs/Earnings_Calls_Transcripts/Unified-info.parquet')))"` |
| 2 | **Which linearmodels R² is "correct"** — the manual double-demeaned R² vs linearmodels `rsquared_within` represents a methodological choice. Need to confirm with thesis advisor which to report. | Consult econometrics literature on two-way FE R² reporting conventions; Stata's `xtreg, fe` reports `within R-sq` analogous to linearmodels `rsquared_within` |
| 3 | **Centering decision not documented** — whether to center interactions is a design choice that should be stated in the paper | Add to provenance: "Interaction terms use uncentered raw products. Beta1 represents the effect of Uncertainty when Lev=0." |
| 4 | **Stage 2 linguistic variable update not tracked** — the 2,733 additional non-null Manager_QA_Uncertainty values between Stage 2 runs are not documented anywhere | Add Stage 2 run log or hash to Stage 3 provenance |
| 5 | **Other suites' within-R² not audited** — the manual within-R² inflation likely affects ALL Stage 4 suites, not just H3 | Audit `within_r2` computation in H1, H2, H4, H5, H7 runners |
| 6 | **`payout_flexibility` formula verification** — the docstring describes `% of years with |Delta DPS| > 5% of prior DPS` and the code (`_compustat_engine.py:868-878`) uses `(delta_dps.abs() > 0.05 * dps_lag.abs())` which does match the docstring, but this was not independently verified on synthetic data | Create unit test with known DPS series to verify payout_flexibility computation |
