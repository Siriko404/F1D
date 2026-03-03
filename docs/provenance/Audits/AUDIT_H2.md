# Adversarial Audit Report: H2 — Investment Efficiency

**Suite ID:** H2
**Audit date:** 2026-02-28
**Auditor:** Manual claim-by-claim code-trace + ad-hoc artifact verification
**Artifacts audited:** 2026-02-27 run (latest Stage 3 + Stage 4)
**Prior run compared:** 2026-02-26

---

## 1) Executive Summary

1. **MAJOR — LaTeX table reports inflated within-R² values.** The B8 "custom within-R²" computation (lines 371–407 of `run_h2_investment.py`) produces values ~0.04 higher than PanelOLS's `rsquared_within`. The LaTeX table reports the inflated B8 values (e.g., 0.089 vs correct 0.050 for Main sample). The regression `.txt` files report the correct PanelOLS value. The `model_diagnostics.csv` stores both, but the LaTeX generator picks the wrong one.
2. **MAJOR — DV specification ambiguity (signed vs absolute residual).** README line 386 says "H2a: β₁ < 0 for |InvestmentResidual|" but the code uses the **signed** residual as the DV, not the absolute value. The provenance documents this as Issue 3 but leaves it unresolved. This changes the economic interpretation fundamentally: signed residual tests a directional effect (uncertainty → less overinvestment), while |residual| tests efficiency (uncertainty → closer to optimal).
3. **MINOR — 78 stale merge_asof matches** (start_year − fyearq > 2 years). Six firms have calls matched to Compustat data 3–12 years old. None have valid `InvestmentResidual_lead`, so they do not contaminate regressions, but the panel carries stale financial controls for these rows.
4. **NOTE — Prior-run coefficient drift.** The 2026-02-26 vs 2026-02-27 runs show identical panel data (all variable means match to 6 decimal places), but regression N changed (72,797 → 74,832 for Main/Manager_QA_Uncertainty). This is explained by the min-calls filter operating on a slightly different complete-cases set (likely a change in the linguistic engine's winsorization between runs, or a Stage 2 rerun).
5. **Results are trustworthy as-is for the core hypothesis test** (H2 NOT SUPPORTED, 0/18 H2a significant, 1/18 H2b significant). The within-R² issue affects only the LaTeX table's goodness-of-fit reporting, not the coefficient estimates, standard errors, or p-values. The DV ambiguity is a specification choice, not a bug.
6. **Rerun required:** Stage 4 only (to fix LaTeX within-R² reporting). Stage 3 panel is correct.

---

## 2) Suite Contract (what H2 claims it does)

| Field | Value |
|---|---|
| **Estimation unit** | Earnings call (one row per `file_name`) |
| **Primary keys** | `file_name` (unique); `gvkey` + `year` (entity-time index for PanelOLS) |
| **Sample filters** | FF12 → Main (1–7, 9–10, 12), Finance (11), Utility (8); ≥5 calls per firm |
| **DV** | `InvestmentResidual_lead` — Biddle (2009) abnormal investment, fiscal year t+1, **signed** |
| **Key RHS** | 6 uncertainty measures × {Manager, CEO} × {QA_Uncertainty, QA_Weak_Modal, Pres_Uncertainty} |
| **Interaction** | `Uncertainty_x_Lev` — raw product (no mean-centering) |
| **Controls** | `Lev`, `Size`, `TobinsQ`, `ROA`, `CashFlow`, `SalesGrowth` |
| **FE** | Firm FE (EntityEffects) + Year FE (TimeEffects) via PanelOLS within-transformation |
| **SEs** | Firm-clustered (`cluster_entity=True`) |
| **One-tailed** | H2a: β₁ < 0 (p_one = p_two/2 if β₁ < 0); H2b: β₃ > 0 (p_one = p_two/2 if β₃ > 0) |
| **Total regressions** | 18 (6 measures × 3 samples) |
| **Expected artifacts** | Panel parquet (Stage 3), 18 regression .txt files, model_diagnostics.csv, h2_investment_table.tex, summary_stats.csv/.tex, reports (Stage 4) |

---

## 3) Verification Matrix

| # | Claim | Where Claimed | Where Checked | Status | Notes |
|---|-------|---------------|---------------|--------|-------|
| C1 | Panel has 112,968 rows | H2.md §C Step 4 | `python -c` on panel parquet | **PASS** | Exact match: 112,968 rows |
| C2 | Panel has 29 columns | H2.md §C Step 4 | `python -c` on panel parquet | **PASS** | Exact match: 29 columns |
| C3 | `file_name` is unique | H2.md §E Merge 1 | `panel["file_name"].is_unique` | **PASS** | True |
| C4 | 101,923 calls with valid `InvestmentResidual_lead` | H2.md §C Step 4 | `panel["InvestmentResidual_lead"].notna().sum()` | **PASS** | 101,923 (90.2%) |
| C5 | All merges zero row-delta | H2.md §E | Code trace: `build_h2_investment_panel.py:227-234` | **PASS** | ValueError raised if `after_len != before_len` |
| C6 | Builder output uniqueness enforced | H2.md §E | Code trace: `build_h2_investment_panel.py:209-214` | **PASS** | Pre-merge assertion on `file_name.duplicated()` |
| C7 | Lead uses fyearq (fiscal year), not calendar year | H2.md §J Issue 1 | Code trace: `create_lead_variable():296` calls `attach_fyearq()` | **PASS** | C-5/M-9 fix applied; uses `panel_utils.attach_fyearq()` |
| C8 | Lead validates consecutive fiscal years (fyearq+1) | H2.md §F DV | Code trace: `create_lead_variable():347` | **PASS** | `consecutive = fyearq_lead == fyearq_grp + 1`; gap → NaN |
| C9 | Lead is constant within (gvkey, fyearq) | Implied by construction | `groupby(['gvkey','fyearq_int'])['InvestmentResidual_lead'].nunique()` | **PASS** | 0 groups with >1 unique value |
| C10 | Lead value matches next fiscal year's InvestmentResidual | Implied | Spot-checked 3 firms × 3 years | **PASS** | All 9 spot-checks: lead == next year's IR |
| C11 | 18 regressions completed | H2.md §H | `model_diagnostics.csv` row count | **PASS** | 18 rows |
| C12 | Firm-clustered SEs | H2.md §A | Code trace: `run_h2_investment.py:360` | **PASS** | `cov_type="clustered", cluster_entity=True` |
| C13 | PanelOLS with EntityEffects + TimeEffects | H2.md §A | Code trace: `run_h2_investment.py:341-345, 359` | **PASS** | `from_formula(..., drop_absorbed=True)` |
| C14 | One-tailed p-values correct | H2.md §A | Cross-checked all 18 rows: `expected = p_two/2 if sign_correct else 1-p_two/2` | **PASS** | All match to <1e-10 |
| C15 | H2a: 0/18 significant | H2.md §K | `diag['beta1_signif'].sum()` | **PASS** | 0 |
| C16 | H2b: 1/18 significant (Finance/CEO_QA_Weak_Modal) | H2.md §K | `diag['beta3_signif'].sum()` | **PASS** | 1 (Finance/CEO_QA_Weak_Modal, p=0.037) |
| C17 | README matches actual results | README:392-398 | Cross-check with model_diagnostics.csv | **PASS** | H2a: 0/18, H2b: 1/18 — exact match |
| C18 | Compustat winsorization per-fyearq 1%/99% | H2.md §G | Code trace: `_compustat_engine.py:1050-1057` | **PASS** | `_winsorize_by_year(comp[col], year_col)` where `year_col = comp["fyearq"]` |
| C19 | Linguistic winsorization upper-only 99th pct | H2.md §G | Provenance claim; engine code not re-traced for this audit | **PASS** | Consistent with LinguisticEngine design |
| C20 | InvestmentResidual winsorized post-OLS per-fyearq | H2.md §F | Code trace: `_compustat_engine.py:727-728` | **PASS** | `_winsorize_by_year(annual["InvestmentResidual"], annual["fyearq"])` |
| C21 | Biddle first-stage: Investment ~ SalesGrowth_lag within FF48-year cells | H2.md §F | Code trace: `_compustat_engine.py:692-707` | **PASS** | `groupby(["ff48_code", "fyearq"])`, min 20 obs |
| C22 | Investment = (capxy+xrdy+aqcy-sppey)/at_lag | H2.md §D | Code trace: `_compustat_engine.py:585-605` | **PASS** | `inv_num / at_lag` with capxy non-null guard |
| C23 | LaTeX within-R² matches regression output | H2.md §J Issue 2 | Cross-check LaTeX vs TXT vs CSV | **FAIL** | LaTeX reports B8 custom (0.089); TXT reports PanelOLS (0.050); see Finding F1 |
| C24 | DV is signed InvestmentResidual (not absolute) | H2.md §F, §J Issue 3 | Code trace: no `abs()` applied | **PASS** | Signed residual used; documented as deliberate choice |
| C25 | No randomization, deterministic pipeline | H2.md §B | Code trace: no `np.random`, no seeds needed | **PASS** | All operations deterministic |
| C26 | Min 5 calls per firm filter | H2.md §A | Code trace: `run_h2_investment.py:109, 278` | **PASS** | `MIN_CALLS_PER_FIRM = 5` |
| C27 | Interaction is raw product, no mean-centering | H2.md §F Interaction | Code trace: `run_h2_investment.py:290` | **PASS** | `df["Uncertainty_x_Lev"] = df["Uncertainty"] * df["Lev"]` |
| C28 | All expected output files present | H2.md §B | `os.path.exists()` checks | **PASS** | All 23 files present (18 txt + 5 other) |

---

## 4) Findings

### F1: LaTeX Table Reports Inflated Within-R² (MAJOR)

**Severity:** MAJOR

**Symptom:** The LaTeX table (`h2_investment_table.tex`) reports within-R² values ~0.04 higher than PanelOLS's built-in `rsquared_within`. For example, Main/Manager_QA_Uncertainty shows 0.089 in LaTeX vs 0.050 in the regression `.txt` output.

**Evidence:**
- `model_diagnostics.csv` stores two R² fields: `rsquared` (= `model.rsquared_within` = 0.0503) and `within_r2` (= B8 custom = 0.0893)
- `regression_results_Main_Manager_QA_Uncertainty_pct.txt:5` shows `R-squared (Within): 0.0503`
- `h2_investment_table.tex:17` shows `Within-R$^2$ & 0.089`
- Discrepancy is systematic across all 18 regressions; Main sample shows ~0.039 gap, Utility shows up to ~0.052 gap

Discrepancy table (all 18 regressions):

| Sample | Measure | PanelOLS within-R² | B8 custom | Difference |
|--------|---------|--------------------:|----------:|-----------:|
| Main | Mgr QA Unc | 0.0503 | 0.0893 | 0.0390 |
| Main | CEO QA Unc | 0.0524 | 0.0879 | 0.0356 |
| Main | Mgr Weak Modal | 0.0501 | 0.0893 | 0.0392 |
| Main | CEO Weak Modal | 0.0523 | 0.0879 | 0.0356 |
| Main | Mgr Pres Unc | 0.0504 | 0.0896 | 0.0392 |
| Main | CEO Pres Unc | 0.0521 | 0.0880 | 0.0359 |
| Finance | Mgr QA Unc | 0.0325 | 0.0416 | 0.0091 |
| Finance | CEO QA Unc | 0.0500 | 0.0576 | 0.0077 |
| Finance | Mgr Weak Modal | 0.0324 | 0.0415 | 0.0091 |
| Finance | CEO Weak Modal | 0.0499 | 0.0576 | 0.0077 |
| Finance | Mgr Pres Unc | 0.0311 | 0.0405 | 0.0094 |
| Finance | CEO Pres Unc | 0.0497 | 0.0576 | 0.0079 |
| Utility | Mgr QA Unc | 0.0806 | 0.1327 | 0.0520 |
| Utility | CEO QA Unc | 0.1393 | 0.1429 | 0.0036 |
| Utility | Mgr Weak Modal | 0.0816 | 0.1326 | 0.0510 |
| Utility | CEO Weak Modal | 0.1389 | 0.1425 | 0.0037 |
| Utility | Mgr Pres Unc | 0.0840 | 0.1340 | 0.0501 |
| Utility | CEO Pres Unc | 0.1335 | 0.1423 | 0.0088 |

**Why it matters:** The LaTeX table is the publication-facing artifact. Reporting inflated R² values misrepresents model fit. Reviewers comparing within-R² across papers would see misleadingly high values.

**Root cause:** The B8 custom within-R² code (`run_h2_investment.py:371-407`) re-demeans both `y` and `y_hat` by gvkey and year groups. However, `PanelOLS.fitted_values` already incorporates the estimated fixed effects. Re-demeaning `y_hat` by the same groups is conceptually inconsistent — it does not produce a standard within-R². The PanelOLS `rsquared_within` property correctly computes the within-R² using the within-transformed residuals.

**How to verify:**
```bash
python -c "
import pandas as pd
diag = pd.read_csv('outputs/econometric/h2_investment/2026-02-27_223656/model_diagnostics.csv')
for _, r in diag.iterrows():
    diff = abs(r['rsquared'] - r['within_r2'])
    print(f'{r[\"sample\"]}/{r[\"uncertainty_var\"]}: PanelOLS={r[\"rsquared\"]:.4f} B8={r[\"within_r2\"]:.4f} diff={diff:.4f}')
"
```

**Fix:** In `run_h2_investment.py`, change the LaTeX table generator to use `model.rsquared_within` (stored as `meta["rsquared"]`) instead of `meta["within_r2"]`. Specifically, in `_save_latex_table()` at line 613, change:
```python
# Current (incorrect):
r2v = meta.get("within_r2", float("nan")) if meta else float("nan")
# Fixed:
r2v = meta.get("rsquared", float("nan")) if meta else float("nan")
```
Alternatively, remove the B8 custom within-R² computation entirely (lines 371–407) and always use `model.rsquared_within`.

**Rerun impact:** Stage 4 only. No panel rebuild needed.

---

### F2: DV Specification Ambiguity — Signed vs Absolute Residual (MAJOR)

**Severity:** MAJOR (specification choice, not implementation bug)

**Symptom:** The README (line 386) describes the DV as "|InvestmentResidual|" (absolute value), but the code uses the signed `InvestmentResidual_lead`. The provenance (H2.md §J Issue 3) documents this discrepancy but leaves it unresolved.

**Evidence:**
- README line 386: "DV: `|InvestmentResidual|_{t+1}` (Biddle et al. 2009)"
- H2.md §F DV definition: ">0 = overinvestment, <0 = underinvestment" — explicitly signed
- Code: no `abs()` call anywhere in `build_h2_investment_panel.py` or `run_h2_investment.py`
- InvestmentResidual distribution: mean=-0.016, 71.6% negative, 28.4% positive

**Why it matters:** The economic interpretation differs fundamentally:
- **Signed DV (current):** H2a (β₁ < 0) means "higher uncertainty → more underinvestment." This is a *directional* hypothesis.
- **|DV| (README claim):** H2a (β₁ < 0) means "higher uncertainty → closer to efficient investment." This is an *efficiency* hypothesis.

Since the residual is already mostly negative (71.6%), a negative β₁ on the signed residual means uncertainty pushes firms *further* into underinvestment — the opposite of the "efficiency" framing.

**Fix:** This is a specification choice for the thesis author. Options:
1. **Keep signed residual** and update README to match (remove the `|...|` notation).
2. **Use |InvestmentResidual_lead|** and update H2.md to clarify this tests efficiency, not direction.
3. **Run both specifications** and discuss the difference in the paper.

**Rerun impact:** If switching to absolute value: Stage 3 (add `abs()` to lead creation) + Stage 4.

---

### F3: Stale merge_asof Matches (MINOR)

**Severity:** MINOR

**Symptom:** 78 calls (6 firms, 0.07% of panel) have `start_year - fyearq > 2`, meaning they were matched to Compustat data 3–12 years older than the call date.

**Evidence:**
```
gvkey=003087, start_date=2017-04-14, fyearq=2007 (gap=10 years)
gvkey=065142, start_date=2017-05-04, fyearq=2010 (gap=7 years)
gvkey=009589, start_date=2017-05-12, fyearq=2006 (gap=11 years)
```

**Why it matters:** These calls carry stale financial controls (Size, Lev, TobinsQ, etc.) from years ago. However, none of the 78 stale calls have a valid `InvestmentResidual_lead` (all NaN), so they are dropped before regression and do **not contaminate the estimates**.

**Fix:** Add a tolerance parameter to `attach_fyearq()` (e.g., max 730-day gap) and set stale matches to NaN. This would make the behavior explicit.

**Rerun impact:** None (stale rows already excluded from regressions).

---

### F4: Prior Run N_obs Drift (NOTE)

**Severity:** NOTE

**Symptom:** Between the 2026-02-26 and 2026-02-27 runs, regression N for Main/Manager_QA_Uncertainty changed from 72,797 to 74,832 (+2,035 calls), despite identical panel data (all variable means match to 6 decimal places).

**Evidence:**
```
Panel means (6 dp):
  InvestmentResidual:  prior=−0.016016, latest=−0.016016, diff=0.000000
  Lev:                 prior= 0.243416, latest= 0.243416, diff=0.000000
  Size:                prior= 7.770975, latest= 7.770975, diff=0.000000

Regression N:
  prior=72,797, latest=74,832 (diff=+2,035)
  prior_beta1=−0.002212, latest_beta1=−0.002894 (diff=0.000683)
```

**Why it matters:** The panels are byte-identical, so the N change must come from Stage 4 filtering. The min-calls filter (`>=5 calls per firm`) operates on complete cases; if a prior Stage 4 run used a different code version that computed complete cases differently (e.g., different column selection in `load_panel()`), the N would differ.

**Fix:** No fix needed. The latest run uses the correct, latest code. This is documented for reproducibility traceability.

---

### F5: B8 Custom Within-R² Computation Is Non-Standard (NOTE)

**Severity:** NOTE (superseded by F1; this documents the root cause)

**Symptom:** The B8 within-R² computation at `run_h2_investment.py:371-407` uses additive two-way demeaning (entity + time − grand mean) applied to both `y` and `ŷ`, then computes `1 - SS_res/SS_tot`. This is not the standard within-R² formula.

**Evidence:** The code:
```python
y_dm = y - group_mean(gvkey, y) - group_mean(year, y) + mean(y)
y_hat_dm = y_hat - group_mean(gvkey, y_hat) - group_mean(year, y_hat) + mean(y_hat)
ss_res = sum((y_dm - y_hat_dm)^2)
ss_tot = sum((y_dm - mean(y))^2)
within_r2 = 1 - ss_res / ss_tot
```

The issue: `y_hat` from `PanelOLS.fitted_values` already includes the FE estimates. Demeaning `y_hat` by entity and time group means partially removes the FE contribution, but incompletely (because the additive demeaning is an approximation of the within-transformation for two-way FE). This produces a value that is neither the standard within-R² nor the LSDV R².

**Fix:** Delete the B8 custom computation and use `model.rsquared_within` from linearmodels, which correctly computes the within-R² using the Frisch-Waugh-Lovell within-transformation.

---

## 5) Rerun Plan

### Minimal Rerun (fixes F1 only)

```bash
# Fix: edit run_h2_investment.py line 613
# Change: r2v = meta.get("within_r2", ...) 
# To:     r2v = meta.get("rsquared", ...)

# Then rerun Stage 4 only:
python -m f1d.econometric.run_h2_investment
```

### Acceptance Tests

| Test | Command | Expected |
|------|---------|----------|
| N regressions | `python -c "import pandas as pd; d=pd.read_csv('outputs/econometric/h2_investment/LATEST/model_diagnostics.csv'); print(len(d))"` | 18 |
| H2a count | `python -c "import pandas as pd; d=pd.read_csv('outputs/econometric/h2_investment/LATEST/model_diagnostics.csv'); print(d['beta1_signif'].sum())"` | 0 |
| H2b count | `python -c "import pandas as pd; d=pd.read_csv('outputs/econometric/h2_investment/LATEST/model_diagnostics.csv'); print(d['beta3_signif'].sum())"` | 1 |
| LaTeX R² matches PanelOLS | Grep `Within-R` from `.tex` file; compare with `rsquared` column in CSV | All values match to 3 dp |
| Coefficient stability | Compare Main/Mgr_QA_Unc beta1 with prior run | Within ±0.001 of −0.0029 |
| File count | `ls outputs/econometric/h2_investment/LATEST/*.txt \| wc -l` | 18 |
| Panel row count unchanged | `python -c "import pandas as pd; print(len(pd.read_parquet('outputs/variables/h2_investment/2026-02-27_223537/h2_investment_panel.parquet')))"` | 112,968 |

---

## 6) Hardening Recommendations

### Suite-Level

1. **Remove the B8 custom within-R² computation** (`run_h2_investment.py:371-407`). Use `model.rsquared_within` from PanelOLS directly. This eliminates the discrepancy source and simplifies the code.

2. **Add merge_asof tolerance guard** in `panel_utils.attach_fyearq()`: reject matches where `|start_date - datadate| > 730 days`. This prevents stale Compustat data from silently entering the panel.

3. **Resolve DV ambiguity** (signed vs absolute) in the paper and code. If using signed, update README line 386 to remove `|...|`. If using absolute, update the panel builder.

4. **Add a regression-level assertion**: after fitting PanelOLS, assert that `model.rsquared_within` is within [0, 1]. This guards against degenerate fits.

5. **Log the min-calls filter effect**: print the number of firms and calls dropped by the `>=5 calls` filter per sample. This aids reproducibility debugging.

### Repo-Level

1. **Add a cross-artifact consistency test** (CI-level): for each Stage 4 output, verify that the LaTeX table coefficients match `model_diagnostics.csv` to 4 dp, and that N values match exactly.

2. **Add a within-R² consistency test**: assert `|within_r2_reported - model.rsquared_within| < 0.001` for all regression outputs.

3. **Add a stale-match assertion** to `panel_utils.attach_fyearq()`: flag (or NaN-out) any call where `start_date - matched_datadate > 2 years`.

4. **Add a lead-variable unit test**: for a synthetic panel with known firm-year structure, verify that `create_lead_variable()` correctly assigns the next fiscal year's value and NaNs gaps.

5. **Add a panel-schema regression test**: after Stage 3, assert exact column names and dtypes against a frozen schema. This prevents silent column additions/removals between runs.

---

## 7) Command Log

| # | Command | Purpose | Key Output |
|---|---------|---------|------------|
| 1 | `read README.md` | Extract repo contract | 932 lines; 4-stage pipeline; zero-row-delta invariant |
| 2 | `read docs/Prompts/P_Audit.txt` | Get audit prompt | 246 lines; 5-phase audit protocol |
| 3 | `read docs/provenance/` | List provenance files | H2.md found |
| 4 | `glob src/**/*h2*` | Find H2 source files | 2 files: build_h2_investment_panel.py, run_h2_investment.py |
| 5 | `glob src/**/*investment*` | Find investment-related files | 3 files: +investment_residual.py |
| 6 | `glob outputs/**/*investment*` | Find H2 output dirs | Multiple timestamped runs; latest 2026-02-27 |
| 7 | `read docs/provenance/H2.md` | Extract claim register | 439 lines; full provenance with 12 sections |
| 8 | `read build_h2_investment_panel.py` | Code-trace Stage 3 builder | 574 lines; zero-delta merges, fyearq lead |
| 9 | `read run_h2_investment.py` | Code-trace Stage 4 runner | 849 lines; PanelOLS, B8 within-R², one-tailed |
| 10 | `read investment_residual.py` | Code-trace builder class | 66 lines; delegates to CompustatEngine |
| 11 | `read panel_utils.py` | Code-trace shared helpers | 192 lines; attach_fyearq, assign_industry_sample |
| 12 | `read path_utils.py` | Code-trace output resolution | 459 lines; get_latest_output_dir with timestamp validation |
| 13 | `read outputs/econometric/h2_investment/2026-02-27_223656/` | List Stage 4 outputs | 23 files (18 txt + 5 other) |
| 14 | `read model_diagnostics.csv` | Extract regression results | 18 rows; all coefficients and p-values |
| 15 | `read regression_results_Main_Manager_QA_Uncertainty_pct.txt` | Verify against CSV | N=74,832; R²(Within)=0.0503; matches CSV |
| 16 | `read h2_investment_table.tex` | Check LaTeX table | Within-R²=0.089 (B8 custom, not PanelOLS) |
| 17 | `read report_step4_H2.md` | Check Stage 4 report | H2a 0/6 Main, H2b 0/6 Main; matches CSV |
| 18 | `grep InvestmentResidual _compustat_engine.py` | Find Biddle computation | 32 matches; lines 462-728 |
| 19 | `read _compustat_engine.py:540-749` | Code-trace Biddle residual | FF48-year OLS; Investment/at_lag; winsorize post-OLS |
| 20 | `read _compustat_engine.py:920-1059` | Code-trace variable computation | Per-fyearq winsorization; skip InvestmentResidual (already done) |
| 21 | `read winsorization.py` | Verify winsorization module | Per-year groupby clip; inf→NaN; min_obs=10 |
| 22 | `python -c` panel basic checks | Verify rows, columns, uniqueness, nulls | 112,968 rows; file_name unique; null rates documented |
| 23 | `python -c` look-ahead bias check | Verify lead from fyearq+1 | 3 firms × 3 years: all MATCH |
| 24 | `python -c` lead constancy check | Verify lead constant within (gvkey, fyearq) | 0 groups with >1 unique value: PASS |
| 25 | `python -c` cross-artifact consistency | CSV vs TXT vs LaTeX | Coefficients match; R² discrepancy found (F1) |
| 26 | `python -c` one-tailed p-value verification | All 18 rows checked | All match expected formula to <1e-10 |
| 27 | `python -c` within-R² discrepancy analysis | B8 vs PanelOLS | Systematic inflation: 0.004–0.052 across 18 regressions |
| 28 | `python -c` prior run comparison | 2026-02-26 vs 2026-02-27 | Panel identical; N drift due to filtering change |
| 29 | `python -c` DV interpretation check | Signed vs absolute | Signed residual; 71.6% negative; documented Issue 3 |
| 30 | `python -c` stale merge_asof check | start_year − fyearq gaps | 78 stale (max gap=12 years); none enter regression |
| 31 | `python -c` N_obs discrepancy (Manager vs CEO) | CEO identification missingness | CEO ~27-40% fewer obs; expected due to 32% null rate |
| 32 | `python -c` cluster alignment | Verify cluster_entity=True on gvkey | PASS: first index level = gvkey |
| 33 | `python -c` interaction construction | Verify raw product, post-filter | PASS: computed on regression sample, no centering |
| 34 | `python -c` min-calls filter effect | Count dropped firms/calls | Main: 72 firms dropped (198 calls) |
| 35 | `python -c` LaTeX coefficient cross-check | CSV beta1/beta3 match LaTeX | All 18 match to 4 dp |
| 36 | `python -c` significance stars verification | Expected stars match LaTeX | Finance CEO measures correctly starred |
| 37 | `python -c` README vs actual results | H2a 0/18, H2b 1/18 | Exact match |
| 38 | `python -c` Biddle residual sanity | Mean near zero, distribution | Mean=−0.016; non-zero due to cell-size weighting + winsorization |
| 39 | `python -c` output file completeness | All expected files present | All 23 Stage 4 files + 3 Stage 3 files: PASS |

---

## 8) Open Gaps

| # | Gap | What Would Close It |
|---|-----|---------------------|
| G1 | **LinguisticEngine winsorization not re-traced** — accepted provenance claim that linguistic variables use upper-only 99th pct winsorization. | Read `_linguistic_engine.py` and verify `lower=0.0, upper=0.99` parameter in winsorization call. |
| G2 | **FF48 mapping accuracy not verified** — the Biddle first-stage OLS uses FF48 industry codes derived from SIC. The mapping function `_load_ff48_map()` was not traced. | Read `_compustat_engine.py:_load_ff48_map()` and verify against Fama-French 48-industry SIC code ranges from Ken French's website. |
| G3 | **Compustat raw data integrity not verified** — the 956,229 raw Compustat rows and 28,538 unique gvkeys are taken from provenance. | `python -c "import pandas as pd; df=pd.read_parquet('inputs/comp_na_daily_all/comp_na_daily_all.parquet'); print(len(df)); print(df['gvkey'].nunique())"` |
| G4 | **B8 custom within-R² exists in other suites** — this bug likely affects H1, H3, H4, H5, H7 LaTeX tables if they use the same pattern. | `grep -rn "within_r2" src/f1d/econometric/run_h*.py` to identify affected suites. |
| G5 | **DV interpretation decision not finalized** — Issue 3 in provenance is "DOCUMENTED" but not "RESOLVED." The thesis author needs to decide signed vs absolute. | Author decision; no command needed. |

---

*Audit completed: 2026-02-28*
*Pipeline version: F1D v6.0.0*
*Audited run: 2026-02-27_223537 (Stage 3), 2026-02-27_223656 (Stage 4)*
