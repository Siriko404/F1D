# H4 Leverage Discipline — Adversarial Audit Report

**Audit Date:** 2026-02-28
**Auditor:** Adversarial Code Audit (Manual Inspection, No Automated Scripts)
**Suite ID:** H4
**Provenance Doc:** `docs/provenance/H4.md`
**Prior Audit:** `docs/provenance/_archive/AUDIT_H4.md` (superseded by this report)

---

## 1) Executive Summary

1. **MAJOR — Within-R² in LaTeX table is inflated by 34x–5293x** due to incorrect one-step additive demeaning. The LaTeX table reports R² values of 0.63–0.92 when the true linearmodels `rsquared_within` is 0.0002–0.027. This is materially misleading. Stage 4 must be rerun after fixing.
2. **MAJOR — Provenance doc claims "Balanced panel"** (H4.md:A1 line 19) but the panel is unbalanced (Min Obs=5, Max Obs=171 per entity). Terminological error; no impact on results.
3. **MINOR — Cross-run N drift of +2.7%** between the prior Stage 4 run (2026-02-27_152751) and the latest (2026-02-27_224046) due to Stage 2 re-run (2026-02-27_200910) reducing linguistic variable missingness. This is expected and correct behavior — not a bug — but one spec (Utility/MgrQA) changed significance status.
4. **MINOR — PRES_CONTROL_MAP asymmetry** underdocumented: Weak_Modal QA DVs control for Presentation **Uncertainty** (not Weak_Modal). Provenance doc says "corresponding Pres measure" without clarifying this.
5. **NOTE — Linguistic engine log message** says "per-year 1%/99%" but code uses `lower=0.0, upper=0.99` (0%/99% upper-only).
6. **Core econometric results are trustworthy.** Coefficients, standard errors, p-values, and significance determinations are consistent across all three output artifacts (diagnostics CSV, regression .txt, LaTeX table). Panel construction is sound: unique PKs, zero row-delta enforcement, correct Lev_lag timing with gap handling.
7. **What must be rerun:** Stage 4 only (after fixing within-R² computation). Stage 3 panel is correct.
8. **No blockers identified.** The within-R² issue is the only material problem and it affects reporting only (not coefficient estimates).

---

## 2) Suite Contract (What H4 Claims It Does)

Extracted verbatim from `docs/provenance/H4.md`:

| Field | Value |
|-------|-------|
| **Estimation unit** | Call-level (individual earnings call), keyed by `file_name` |
| **Panel type** | "Balanced panel with firm + year fixed effects" (doc A1) — **INCORRECT, see Finding #1** |
| **DVs (6)** | Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_QA_Weak_Modal_pct, CEO_QA_Weak_Modal_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct |
| **Key IV** | `Lev_lag` — one-year lagged leverage via fiscal year shift within gvkey; NaN if non-consecutive years |
| **Dynamic covariate** | QA DVs add corresponding Pres measure as control; Pres DVs have no Pres control |
| **Base controls** | Analyst_QA_Uncertainty_pct, Size, TobinsQ, ROA, CashHoldings, DividendPayer, firm_maturity, earnings_volatility |
| **Fixed effects** | Entity (gvkey) + Time (year), absorbed via PanelOLS `EntityEffects + TimeEffects` |
| **Standard errors** | Clustered by firm (`cov_type="clustered", cluster_entity=True`) |
| **Winsorization** | Engine-level: Compustat per-year 1%/99%, Linguistic per-year 0%/99% upper-only |
| **Missingness** | Listwise deletion per regression (`run_h4_leverage.py:168`) |
| **Sample filters** | `min_calls >= 5` per firm; 3 industry samples (Main FF12≠8,11; Finance FF12=11; Utility FF12=8) |
| **Panel rows** | 112,968 calls; Lev_lag coverage 93.3% (105,380 valid) |
| **Regressions** | 18 total (6 DVs × 3 samples); 2 significant (Main MgrPres p=0.009, Main CEOPres p=0.044) |
| **Expected outputs** | Panel parquet, 18 regression .txt, LaTeX table, diagnostics CSV, summary stats CSV+TeX |

---

## 3) Verification Matrix (Claim → Evidence → Status)

| # | Claim | Where Claimed | Where Checked | Status | Notes |
|---|-------|---------------|---------------|--------|-------|
| 1 | Panel = 112,968 rows | H4.md:B:108, C:160 | `python -c` → `len(df) = 112,968` | **PASS** | Verified directly on parquet |
| 2 | Panel type: "Balanced panel" | H4.md:A1 line 19 | Regression .txt: Min Obs=5.0, Max Obs=171.0 | **FAIL** | Panel is unbalanced. See Finding #1 |
| 3 | 26 columns in panel | H4.md:B:108 | `python -c` → `len(df.columns) = 26` | **PASS** | Exact match |
| 4 | file_name is unique PK | H4.md:A1, D:206 | `python -c` → `df['file_name'].is_unique = True` | **PASS** | Verified on artifact |
| 5 | Lev_lag coverage = 93.3% (105,380) | H4.md:E:254, I:417 | `python -c` → `notna().sum() = 105,380` | **PASS** | 105,380/112,968 = 93.3% |
| 6 | Zero row-delta on all merges | H4.md:E:239 | `build_h4_leverage_panel.py:191-196`: `if delta != 0: raise ValueError(...)` | **PASS** | Code enforces |
| 7 | Merge join type = LEFT on file_name | H4.md:E table | `build_h4_leverage_panel.py:192`: `panel.merge(data, on="file_name", how="left")` | **PASS** | All 15 merges |
| 8 | Lev = (dlcq + dlttq) / atq | H4.md:F:285 | `_compustat_engine.py:945`: `(comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]` | **PASS** | Formula matches |
| 9 | Lev_lag consecutive-year validation | H4.md:E:251 | `build_h4_leverage_panel.py:104-105`: NaN if `(fyearq_int - prev_fyearq) != 1` | **PASS** | Also verified on artifact: firm 001045 FY2013 has NaN Lev_lag due to FY2012 gap |
| 10 | Compustat winsor per-year 1%/99% | H4.md:G:318 | `_compustat_engine.py:1050-1057`: `_winsorize_by_year(comp[col], year_col)` with hardcoded 1%/99% | **PASS** | |
| 11 | Linguistic winsor per-year 0%/99% upper-only | H4.md:F:274-279 | `_linguistic_engine.py:255-258`: `lower=0.0, upper=0.99, min_obs=1` | **PASS** | Code matches doc |
| 12 | PanelOLS with EntityEffects + TimeEffects | H4.md:A2:28-29 | `run_h4_leverage.py:179-183` | **PASS** | Formula confirmed |
| 13 | Clustered SEs by firm | H4.md:A5:80 | `run_h4_leverage.py:199`: `.fit(cov_type="clustered", cluster_entity=True)` | **PASS** | |
| 14 | min_calls >= 5 filter | H4.md:A4:71 | `run_h4_leverage.py:492-497`: `gvkey_count >= CONFIG["min_calls"]` with `min_calls=5` | **PASS** | |
| 15 | Dynamic pres control for QA DVs | H4.md:A4:52-55 | `run_h4_leverage.py:107-114`: PRES_CONTROL_MAP | **PASS** with caveat | Weak_Modal QA DVs use Uncertainty Pres control. See Finding #4 |
| 16 | Industry samples: Main/Finance/Utility | H4.md:E:260-265 | `panel_utils.py:46-73`: FF12=11→Finance, FF12=8→Utility, else→Main | **PASS** | Verified on artifact: Main=88,205, Finance=20,482, Utility=4,281 |
| 17 | Main MgrPres: β₁ = -0.055, p = 0.009 | H4.md:H:362 | CSV: beta1=-0.05519, p_one=0.00871; .txt: Parameter=-0.0552, P-value=0.0174 (two-tailed → 0.0087 one-tailed); LaTeX: -0.0552^{***} | **PASS** | Consistent across 3 sources |
| 18 | Main CEOPres: β₁ = -0.042, p = 0.044 | H4.md:H:363 | CSV: beta1=-0.04237, p_one=0.04438; .txt: Parameter=-0.0424, P-value=0.0888 (two-tailed → 0.0444 one-tailed); LaTeX: -0.0424^{**} | **PASS** | Consistent |
| 19 | Main MgrQA: β₁ = 0.0008, p = 0.52, NS | H4.md:H:352 | CSV: beta1=0.000766, p_one=0.5213; .txt: Parameter=0.0008, P-value=0.9575 (two-tailed) | **PASS** | |
| 20 | 2/18 regressions significant | H4.md:H:361 | CSV: exactly 2 rows with h4_sig=True (Main MgrPres, Main CEOPres) | **PASS** | |
| 21 | One-tailed test: β₁ < 0 | H4.md:A4 | `run_h4_leverage.py:250-253`: `p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2` | **PASS** | Correct sign-conditional halving |
| 22 | LaTeX table Within-R² values accurate | H4.md (implied) | LaTeX shows 0.83-0.92; linearmodels `rsquared_within` is 0.0002-0.027 | **FAIL** | See Finding #2 |
| 23 | Compustat dedup (gvkey, datadate) keep=last | H4.md:D:195 | `_compustat_engine.py:1107` | **PASS** | |
| 24 | attach_fyearq match rate ≥ 80% | H4.md:C:182 | `panel_utils.py:170`: `< 0.8` threshold | **PASS** | Docstring at line 95 says 50% (stale) but code uses 80% |
| 25 | ROA = Annualized Q4 iby / avg assets | H4.md:F:294 | `_compustat_engine.py:947-956` | **PASS** | |
| 26 | firm_maturity = req / atq | H4.md:F:297 | `_compustat_engine.py:831-833` | **PASS** | |
| 27 | earnings_volatility = 5-yr rolling SD of ROA | H4.md:F:298 | `_compustat_engine.py:881-884`: `rolling("1826D", min_periods=3).std()` | **PASS** | 1826 days ≈ 5 years |
| 28 | DividendPayer = dvy > 0 (Q4 annual) | H4.md:F:296 | `_compustat_engine.py:985-988` | **PASS** | |
| 29 | Size = ln(atq) where atq > 0 | H4.md:F:292 | `_compustat_engine.py:940` | **PASS** | |
| 30 | Inf → NaN before winsorization | H4.md:G:344 | `_compustat_engine.py:1029-1030` and `winsorization.py:56-58` | **PASS** | |
| 31 | No hidden Stage 3 dependencies | H4.md:C chain | Code inspection: only manifest + linguistic + Compustat | **PASS** | |
| 32 | 18 regression .txt files produced | H4.md:B:109 | `ls` output: 18 regression_results_*.txt + 2 extra (Utility files present despite provenance showing all NS) | **PASS** | 18 files present (actually 18 regression + 2 summary = 22 total files) |
| 33 | Lev_lag bounds reasonable | Implied | Min=0.0, Max=3.77, Mean=0.24, No inf | **PASS** | Upper tail from winsorized Lev |
| 34 | Lev_lag timing correctness | Implied | Spot-checked 3 firms: all FY(t) Lev_lag values match FY(t-1) Lev exactly | **PASS** | Perfect match on all 42 checked transitions |

---

## 4) Findings (Grouped by Severity)

### Finding #1 — MAJOR: Provenance doc claims "Balanced panel"

- **Severity:** MAJOR (misleading documentation)
- **Symptom:** H4.md Section A1 line 19 states "Panel Type: Balanced panel with firm + year fixed effects."
- **Evidence:** Regression output `regression_results_Main_Manager_QA_Uncertainty_pct.txt` lines 10-12: `Avg Obs: 42.023`, `Min Obs: 5.0000`, `Max Obs: 171.00`. A balanced panel requires all entities to have the same number of observations. Additionally: `python -c` check showed 75,852 calls across 20,268 unique (gvkey, year) pairs, with 1-38 calls per firm-year. This is clearly an unbalanced panel.
- **Why it matters:** A referee would flag this. "Balanced" vs "unbalanced" has specific meaning in panel econometrics. The distinction affects standard error estimation (though PanelOLS handles both correctly).
- **Fix:** Change "Balanced panel" to "Unbalanced panel" in `docs/provenance/H4.md` Section A1.
- **Rerun impact:** None (documentation only).

### Finding #2 — MAJOR: Manual within_r² computation is incorrect; LaTeX table misreports Within-R²

- **Severity:** MAJOR (materially misleading table output)
- **Symptom:** LaTeX table (`h4_leverage_table.tex` line 21) reports Within-R² values of 0.63–0.92 across all 6 Main-sample specifications, while linearmodels' `rsquared_within` (the correct value) ranges from 0.0002–0.027 for the same regressions.
- **Evidence:**
  - `run_h4_leverage.py:219-233`: One-step additive demeaning: `y - mu_i(y) - mu_t(y) + mu(y)` applied to both y and y_hat.
  - `model_diagnostics.csv`: `rsquared=0.022373` (linearmodels correct) vs `within_r2=0.911286` (manual incorrect) for Main/MgrQA.
  - Full discrepancy table (all 18 specs):

| Spec | linearmodels R²(Within) | Manual within_r2 | Inflation |
|------|----------------------:|------------------:|----------:|
| Main/MgrQA Unc | 0.0224 | 0.9113 | 41x |
| Main/CEO QA Unc | 0.0193 | 0.8522 | 44x |
| Main/MgrQA WM | 0.0078 | 0.8350 | 106x |
| Main/CEO QA WM | 0.0071 | 0.7417 | 105x |
| Main/MgrPres Unc | 0.0002 | 0.9168 | **3759x** |
| Main/CEOPres Unc | 0.0002 | 0.8198 | **5293x** |
| Finance/MgrQA | 0.0270 | 0.9241 | 34x |
| Finance/CEO QA | 0.0134 | 0.8566 | 64x |
| Finance/MgrQA WM | 0.0059 | 0.8482 | 143x |
| Finance/CEO QA WM | 0.0022 | 0.7342 | 332x |
| Finance/MgrPres | 0.0053 | 0.9254 | 174x |
| Finance/CEOPres | 0.0040 | 0.8425 | 213x |
| Utility/MgrQA | 0.0161 | 0.8997 | 56x |
| Utility/CEO QA | 0.0110 | 0.7709 | 70x |
| Utility/MgrQA WM | 0.0057 | 0.8122 | 142x |
| Utility/CEO QA WM | 0.0077 | 0.6339 | 83x |
| Utility/MgrPres | 0.0102 | 0.9293 | 91x |
| Utility/CEOPres | 0.0106 | 0.8479 | 80x |

- **Root cause:** The one-step additive demeaning `y - mu_i - mu_t + mu` does NOT correctly implement the within transformation for **two-way** fixed effects. The correct approach requires iterative demeaning (alternating projections between entity and time dimensions until convergence), as linearmodels implements internally via the Frisch-Waugh-Lovell theorem. The one-step approximation leaves residual entity/time variation, inflating `ss_tot` relative to `ss_res` and producing artificially high R². The inflation is worst for Pres DVs (3759x–5293x) because Pres uncertainty has strong entity effects that are not fully removed by one-step demeaning.
- **Impact on conclusions:** Coefficient estimates (β, SE, p-values) are **NOT affected** — they come from linearmodels' correct internal computation. Only the reported Within-R² in the LaTeX table is wrong. However, a reviewer seeing R²=0.91 would question the entire analysis.
- **Fix:**
  1. In `run_h4_leverage.py`, replace lines 210-236 with: `within_r2 = float(model.rsquared_within)`
  2. In `_save_latex_table()` at line 374-381: use `r['rsquared']` (which stores `model.rsquared_within`) instead of `r['within_r2']`
  3. Either drop the `within_r2` column from `model_diagnostics.csv` or fix the computation
- **Rerun impact:** Stage 4 must be rerun. Stage 3 panel is unaffected.

### Finding #3 — MINOR: Cross-run N drift due to Stage 2 re-run

- **Severity:** MINOR (expected behavior, but causes one significance change)
- **Symptom:** The prior Stage 4 run (2026-02-27_152751) has ~2.0–2.7% fewer observations than the latest run (2026-02-27_224046) across all specs. One specification (Utility/MgrQA) changed from significant (p=0.043) to non-significant (p=0.058).
- **Evidence:**
  - Prior run used Stage 3 panel from 2026-02-26_102714 (built with Stage 2 from 2026-02-19)
  - Latest run used Stage 3 panel from 2026-02-27_223928 (built with Stage 2 from 2026-02-27_200910)
  - Missingness comparison: `Manager_QA_Uncertainty_pct` had 7,486 missing in prior panel vs 4,753 in latest (-2,733). `Analyst_QA_Uncertainty_pct` had 11,750 vs 9,110 (-2,640). Financial variables unchanged.
  - The Stage 2 re-run on 2026-02-27 improved linguistic variable coverage, reducing listwise deletion at regression time.
- **Why it matters:** The cross-run difference is fully explainable and correct (improved upstream data → more obs). However, the Utility/MgrQA significance change shows the result is fragile near the boundary.
- **Fix:** Document the Stage 2 dependency in the provenance doc. Consider pinning Stage 2 output timestamps in the provenance for exact reproducibility.
- **Rerun impact:** None needed — this is informational.

### Finding #4 — MINOR: PRES_CONTROL_MAP asymmetry underdocumented

- **Severity:** MINOR (documentation ambiguity)
- **Symptom:** When DV is `Manager_QA_Weak_Modal_pct` or `CEO_QA_Weak_Modal_pct`, the added presentation control is the **Uncertainty** measure, NOT the Weak_Modal presentation measure.
- **Evidence:** `run_h4_leverage.py:110-111`:
  ```python
  "Manager_QA_Weak_Modal_pct": "Manager_Pres_Uncertainty_pct",
  "CEO_QA_Weak_Modal_pct": "CEO_Pres_Uncertainty_pct",
  ```
- **Why it matters:** H4.md:A4 says "If DV is a QA measure → corresponding Pres measure added as control" which could be interpreted as Weak_Modal → Weak_Modal. The actual mapping is always to Uncertainty. This is likely intentional (Uncertainty is the primary measure) but ambiguous.
- **Fix:** Clarify in H4.md: "For QA DVs, the **Presentation Uncertainty** measure for the corresponding speaker role is added as a control (always Uncertainty, regardless of whether the DV is Uncertainty or Weak_Modal)."
- **Rerun impact:** None (documentation only, unless the intent was to use Weak_Modal pres controls).

### Finding #5 — NOTE: LinguisticEngine winsorization log message is misleading

- **Severity:** NOTE
- **Symptom:** `_linguistic_engine.py:259` logs: `"Winsorized {n} percentage columns (per-year 1%/99%)"` but actual bounds are `lower=0.0, upper=0.99` (0%/99%, upper-only).
- **Evidence:** `_linguistic_engine.py:257`: `lower=0.0, upper=0.99` vs line 259: `"per-year 1%/99%"`
- **Fix:** Change log message to `"per-year 0%/99% (upper-only)"`.
- **Rerun impact:** None.

### Finding #6 — NOTE: panel_utils.py docstring says 50% threshold but code uses 80%

- **Severity:** NOTE
- **Symptom:** `panel_utils.py:95` docstring says "Raises ValueError if fewer than 50% of panel rows match" but code at line 170 checks `< 0.8` (80%).
- **Evidence:** Line 95: `"50%"` vs line 170: `if (n_matched / n_total) < 0.8`
- **Fix:** Update docstring to say "80%".
- **Rerun impact:** None.

### Finding #7 — NOTE: No merge_asof tolerance in CompustatEngine

- **Severity:** NOTE
- **Symptom:** `_compustat_engine.py:1143-1150` (via `match_to_manifest`) uses `pd.merge_asof(..., direction="backward")` without a `tolerance` parameter.
- **Why it matters:** Theoretically allows a call to match a Compustat row from years earlier if no closer match exists. Mitigated by dense quarterly Compustat coverage and ≥80% match rate enforcement.
- **Fix:** Consider adding `tolerance=pd.Timedelta("365 days")` in a future hardening pass.
- **Rerun impact:** Would require Stage 3 rerun if implemented.

### Finding #8 — NOTE: No contemporaneous Lev control

- **Severity:** NOTE (design choice, not a bug)
- **Symptom:** Model regresses current uncertainty on lagged leverage (Lev_lag) without controlling for contemporaneous leverage (Lev).
- **Evidence:** `BASE_CONTROLS` at `run_h4_leverage.py:96-105` does not include "Lev".
- **Why it matters:** Including contemporaneous Lev could introduce a "bad control" problem if current leverage is endogenous to current speech. Omitting it is defensible but should be discussed.
- **Fix:** Document the exclusion rationale. Optionally add a robustness spec with Lev included.
- **Rerun impact:** None.

---

## 5) Rerun Plan (Actionable)

### Minimal Fix

In `run_h4_leverage.py`, replace the manual within-R² computation (lines 210-236) with:
```python
within_r2 = float(model.rsquared_within)
```

In `_save_latex_table()` (lines 374-381), change `r['within_r2']` to `r['rsquared']` (which stores `model.rsquared_within`).

### Minimal Rerun Commands

```bash
# Stage 3: NOT NEEDED (panel is correct)
# Stage 4: Rerun after fixing within-R² computation
python -m f1d.econometric.run_h4_leverage
```

### Acceptance Tests

After rerun, verify:

```python
import pandas as pd

# 1. Panel row count unchanged (Stage 3 not rerun)
panel = pd.read_parquet('outputs/variables/h4_leverage/2026-02-27_223928/h4_leverage_panel.parquet')
assert len(panel) == 112_968

# 2. Diagnostics: 18 regressions, 2 significant
diag = pd.read_csv('outputs/econometric/h4_leverage/LATEST/model_diagnostics.csv')
assert len(diag) == 18
assert diag['h4_sig'].sum() == 2

# 3. Key coefficients stable (within rounding)
main_mgr_pres = diag[(diag['dv'] == 'Manager_Pres_Uncertainty_pct') & (diag['sample'] == 'Main')]
assert abs(main_mgr_pres['beta1'].values[0] - (-0.0552)) < 0.005
assert main_mgr_pres['beta1_p_one'].values[0] < 0.01

main_ceo_pres = diag[(diag['dv'] == 'CEO_Pres_Uncertainty_pct') & (diag['sample'] == 'Main')]
assert abs(main_ceo_pres['beta1'].values[0] - (-0.0424)) < 0.005
assert main_ceo_pres['beta1_p_one'].values[0] < 0.05

# 4. Within-R² now in correct range (NOT 0.63-0.92)
for _, r in diag.iterrows():
    assert r['within_r2'] < 0.10, f"within_r2={r['within_r2']:.4f} for {r['dv']}/{r['sample']} still inflated!"

# 5. LaTeX table Within-R² values match diagnostics CSV rsquared column
import re
with open('outputs/econometric/h4_leverage/LATEST/h4_leverage_table.tex') as f:
    tex = f.read()
# Verify no R² > 0.10 in the LaTeX table
r2_matches = re.findall(r'(\d+\.\d{4})', tex.split('Within')[1].split('\\\\')[0])
for val in r2_matches:
    assert float(val) < 0.10, f"LaTeX Within-R² value {val} still inflated!"

# 6. N_obs unchanged (within-R² fix doesn't affect sample selection)
assert diag[(diag['dv'] == 'Manager_QA_Uncertainty_pct') & (diag['sample'] == 'Main')]['n_obs'].values[0] == 75852
```

---

## 6) Hardening Recommendations

### Suite-Level (H4)

1. **Fix within-R²** (Finding #2): Replace manual computation with `model.rsquared_within`. Priority: HIGH.
2. **Add Lev_lag bounds assertion** in Stage 3:
   ```python
   assert panel['Lev_lag'].dropna().between(-0.5, 10).all(), "Lev_lag out of expected bounds"
   ```
3. **Add column-list assertion** in Stage 4:
   ```python
   EXPECTED_COLS = ['file_name', 'gvkey', 'year', 'ff12_code', ...]
   missing = [c for c in EXPECTED_COLS if c not in panel.columns]
   assert not missing, f"Missing columns: {missing}"
   ```
4. **Log both R² values** for transparency:
   ```python
   print(f"  linearmodels R²(Within): {model.rsquared_within:.6f}")
   print(f"  Manual within_r2:        {within_r2:.6f}")
   ```
5. **Pin Stage 2 timestamp in Stage 3 report** for full reproducibility chain.

### Repo-Level

1. **Audit all other suites for the same manual within-R² bug.** If the same `y - mu_i - mu_t + mu` pattern exists in other `run_h*.py` files, it produces the same inflated values everywhere.
2. **Add integration test** asserting `abs(manual_within_r2 - model.rsquared_within) < 0.01` for any suite using within-R².
3. **Standardize PRES_CONTROL_MAP documentation** across all suites that use dynamic covariates.
4. **Add merge_asof tolerance** to CompustatEngine as a defensive measure.
5. **Fix stale docstring** in `panel_utils.py:95` (50% → 80%).

---

## 7) Command Log (Chronological)

| # | Command | Purpose | Output |
|---|---------|---------|--------|
| 1 | `read README.md` | Extract repo contract, stage boundaries, invariants | 932 lines, four-stage architecture with zero row-delta, timestamped outputs |
| 2 | `glob **/provenance/**` | Locate H4 provenance doc | Found `docs/provenance/H4.md` and `_archive/AUDIT_H4.md` |
| 3 | `read docs/provenance/H4.md` | Build claim register from provenance | 553 lines, 10 sections A-J |
| 4 | `read docs/provenance/_archive/AUDIT_H4.md` | Review prior audit findings | 523 lines, identified known within-R² issue |
| 5 | `glob **/*h4*` and `**/*leverage*` in src/f1d | Locate Stage 3/4 source files | `build_h4_leverage_panel.py`, `run_h4_leverage.py` |
| 6 | `read build_h4_leverage_panel.py` | Trace Stage 3 panel construction | 283 lines, 15 LEFT merges + Lev_lag creation |
| 7 | `read run_h4_leverage.py` | Trace Stage 4 estimation logic | 529 lines, PanelOLS with EntityEffects + TimeEffects |
| 8 | `ls outputs/variables/h4_leverage` | Find Stage 3 output timestamps | 4 dirs: 2026-02-20 through 2026-02-27_223928 |
| 9 | `ls outputs/econometric/h4_leverage` | Find Stage 4 output timestamps | 9 dirs: 2026-02-20 through 2026-02-27_224046 |
| 10 | `read panel_utils.py` | Verify assign_industry_sample + attach_fyearq | 192 lines, canonical definitions |
| 11 | `ls outputs/econometric/h4_leverage/2026-02-27_224046` | List latest Stage 4 outputs | 22 files (18 reg + table + diag + 2 summary) |
| 12 | `python -c` panel structure check | Verify 112,968 rows, 26 cols, unique file_name, dtypes | All match provenance claims |
| 13 | `python -c` missingness rates | Check all columns for NaN rates | Manager_QA: 4.2%, CEO_QA: 32.0%, Lev_lag: 6.7% — all match provenance |
| 14 | `read model_diagnostics.csv` | Verify all 18 regressions present, coefficients match | 18 rows, 2 significant |
| 15 | `read h4_leverage_table.tex` | Cross-check LaTeX against CSV | Coefficients, SEs, stars, N all match. Within-R² uses inflated manual values |
| 16 | `python -c` Lev_lag statistics | Check bounds, distribution, inf | Min=0, Max=3.77, 0 negatives, 0 inf |
| 17 | `python -c` spot-check Lev_lag timing | Verify FY(t) Lev_lag = FY(t-1) Lev for 3 firms | All 42 transitions MATCH exactly |
| 18 | `python -c` duplicates check | Verify file_name uniqueness, (gvkey,year) duplication | file_name unique, 98.9% of (gvkey,year) have duplicates (expected for call-level) |
| 19 | `read regression_results_Main_Manager_Pres_Uncertainty_pct.txt` | Cross-check significant result | β=-0.0552, SE=0.0232, p(two)=0.0174, N=75,870, R²(Within)=0.0002 |
| 20 | `read regression_results_Main_CEO_Pres_Uncertainty_pct.txt` | Cross-check significant result | β=-0.0424, SE=0.0249, p(two)=0.0888, N=55,149, R²(Within)=0.0002 |
| 21 | `read regression_results_Main_Manager_QA_Uncertainty_pct.txt` | Cross-check NS result | β=0.0008, SE=0.0144, p(two)=0.9575, N=75,852 |
| 22 | `python -c` within-R² discrepancy | Quantify inflation across all 18 specs | Range: 34x to 5293x inflation |
| 23 | `grep winsorize_by_year` | Verify winsorization implementation locations | Found in compustat_engine, linguistic_engine, crsp_engine, winsorization.py |
| 24 | `python -c` summary stats Stage 4 | Read summary_stats.csv | 45 rows (15 vars × 3 samples), values reasonable |
| 25 | `python -c` summary stats Stage 3 | Read summary_stats.csv | 16 rows, matches panel-level counts |
| 26 | `read winsorization.py` | Verify winsorize_by_year implementation | 134 lines, correct per-year clipping with inf→NaN |
| 27 | `read _compustat_engine.py:920-999` | Verify Lev, Size, ROA, TobinsQ formulas | All match provenance doc |
| 28 | `read _compustat_engine.py:1030-1129` | Verify winsorization application | Per-year 1%/99% with skip list (DividendPayer, Biddle vars) |
| 29 | `read _linguistic_engine.py:230-269` | Verify linguistic winsorization | lower=0.0, upper=0.99, min_obs=1, log message incorrect |
| 30 | `read _compustat_engine.py:420-469` | Verify _winsorize_by_year implementation | Hardcoded 1%/99%, min_obs=10 |
| 31 | `python -c` prior run diagnostics | Check reproducibility against 2026-02-27_152751 run | 18 specs, 3 significant (Utility/MgrQA sig in prior, NS in latest) |
| 32 | `python -c` cross-run N comparison | Quantify observation count changes | +2.0% to +2.7% across all specs |
| 33 | `python -c` cross-run coefficient comparison | Check coefficient stability | Most stable; Utility specs show larger shifts (small N) |
| 34 | `python -c` prior vs latest panel missingness | Explain N differences | Linguistic vars have 2,640-2,733 fewer missing in latest panel |
| 35 | `ls Stage 2 output timestamps` | Identify cause of N drift | Stage 2 re-run on 2026-02-27 explains coverage improvement |
| 36 | `python -c` non-consecutive gap check | Verify FY2013 Lev_lag=NaN for firm 001045 with FY2012 gap | Confirmed: NaN (correct) |
| 37 | `python -c` PanelOLS index check | Verify PanelOLS handles duplicate (gvkey,year) correctly | 98.9% duplicates, PanelOLS handles correctly for call-level data |
| 38 | `python -c` final LaTeX cross-check | Verify all N_obs in LaTeX match CSV | All 6 N values match exactly |
| 39 | `python -c` summary_stats.tex check | Verify LaTeX file validity | 69 lines, proper begin/end table structure |

---

## 8) Open Gaps

| # | Item | Status | What Would Close It |
|---|------|--------|---------------------|
| 1 | Exact within-R² values after fix | UNVERIFIED | Rerun Stage 4 with `model.rsquared_within` and verify LaTeX values in 0.001–0.03 range |
| 2 | Whether PRES_CONTROL_MAP Weak_Modal mapping is intentional | UNVERIFIED | Author confirmation that controlling for Pres Uncertainty (not Pres Weak_Modal) is by design |
| 3 | Whether the same manual within-R² bug exists in other suites | UNVERIFIED | `grep -n "y_dm\|y_hat_dm\|within_r2" src/f1d/econometric/run_h*.py` to check all suites |
| 4 | Maximum merge_asof gap in attach_fyearq | UNVERIFIED | Requires re-exposing matched_datadate: `(panel.start_date - merged.datadate).max()` |
| 5 | Compustat source file currency | UNVERIFIED | Check modification date of `inputs/comp_na_daily_all/comp_na_daily_all.parquet` |
| 6 | Utility/MgrQA significance fragility | UNVERIFIED | Bootstrap confidence interval for the p-value or sensitivity analysis near the boundary |

---

## High-Risk Silent-Failure Checks Performed

1. **Lev_lag timing correctness**: Spot-checked 3 firms (42 transitions), all Lev_lag values exactly match prior-year Lev. Non-consecutive gaps correctly produce NaN. **PASS**.
2. **PanelOLS duplicate index handling**: Verified that PanelOLS correctly handles call-level data with duplicate (gvkey, year) indices. 75,852 observations across 20,268 unique (gvkey, year) pairs; entity effects correctly absorb firm-level heterogeneity. **PASS**.
3. **One-tailed p-value sign conditioning**: Verified Main MgrPres: β=-0.0552, p(two)=0.0174, p(one)=0.0174/2=0.0087. Code at `run_h4_leverage.py:251` correctly halves p when β<0. **PASS**.
4. **Cross-artifact coefficient consistency**: Compared β, SE, p, N across CSV, .txt, and LaTeX for all 6 Main specs. All match to 4+ significant figures. **PASS**.
5. **Winsorization order**: Confirmed Compustat winsorization happens at engine load time (before merge to panel), linguistic at engine load time. No double-winsorization in panel builder or regression runner. **PASS**.

---

## Additional Safeguards Recommended

1. Add assertion: `assert abs(within_r2 - model.rsquared_within) < 0.01` after computing within-R² in any suite.
2. Add assertion: `panel['Lev_lag'].dropna().between(-0.5, 10).all()` in Stage 3 builder.
3. Add assertion: `assert len(all_results) == 18` before writing diagnostics CSV.
4. Log the exact Stage 3 panel path used by Stage 4 for provenance traceability.
5. Add assertion: `assert df_panel.index.get_level_values(0).nunique() >= 50` to catch catastrophic entity count drops.

---

*Audit complete. Manual inspection only — no automated scripts created.*
*Supersedes prior audit at `docs/provenance/_archive/AUDIT_H4.md`.*
