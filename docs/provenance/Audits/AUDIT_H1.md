# Audit Report: Suite H1 (Cash Holdings)

**Date:** 2026-02-28
**Auditor:** Adversarial AI Research Auditor
**Target Suite:** H1 (Cash Holdings Hypothesis)
**Stage 3 Artifact:** `outputs/variables/h1_cash_holdings/2026-02-27_223354/h1_cash_holdings_panel.parquet`
**Stage 4 Artifact:** `outputs/econometric/h1_cash_holdings/2026-02-27_223515/`

## 1) Executive Summary

- **Top Risk [BLOCKER]: Manual Within-R² Computation Bug.** The manual `within_r2` computation (the "B8 fix" imported from other suites) uses the grand mean instead of the group-demeaned mean in the $SS_{tot}$ denominator. This inflates the reported Within-$R^2$ from the true value (~0.06, correctly computed by `PanelOLS.rsquared_within`) to ~0.84 (which is effectively the LSDV $R^2$). The LaTeX tables report this inflated ~0.84 value, constituting a major misrepresentation of the model's explanatory power.
- **Top Risk [MINOR]: Inaccurate Provenance Claim regarding DV constancy.** The provenance document claims `CashHoldings_lead` is "constant within firm-year clusters". This is true for *fiscal* year, but the `PanelOLS` estimator clusters and absorbs on *calendar* year (`C(year)`). Because calls within a calendar year can span two fiscal years, ~75% of (gvkey, calendar_year) clusters contain multiple unique DV values. While clustering on firm (`cluster_entity=True`) remains econometrically sound for the Moulton problem, the documentation's claim is technically false regarding the estimator's actual time dimension.
- **Top Risk [NOTE]: Stale Docstrings.** The docstring in `run_h1_cash_holdings.py` claims it uses "HC1 standard errors," but the actual code correctly uses firm-clustered standard errors (`cluster_entity=True`).
- **Are results trustworthy as-is?** Yes, the coefficient estimates, standard errors, and hypothesis test logic (one-tailed p-values) are **correct and highly robust**. The data construction (zero row-delta merges, correct lead timings, absence of look-ahead bias) is flawless. Only the reported Within-$R^2$ statistic in the LaTeX tables is wrong.
- **What must be rerun?** Stage 4 must be rerun after removing the manual `within_r2` computation block and mapping the LaTeX table to use `PanelOLS.rsquared_within`. Stage 3 does not need to be rerun.

## 2) Suite Contract (what H1 claims it does)

- **Estimation unit:** Call-level (one row per earnings call).
- **Primary keys:** `file_name` (unique).
- **Sample filters:** Dropped if `CashHoldings_lead` is NaN; dropped if missing required controls; dropped if firm has < 5 calls (`MIN_CALLS_PER_FIRM`). Split by `ff12_code` into Main/Finance/Utility.
- **Outcome (DV):** `CashHoldings_lead` (t+1 end-of-fiscal-year cash ratio).
- **RHS Variables:** 6 Uncertainty measures + `Lev` + `Uncertainty_x_Lev` (raw product, no pre-centering).
- **Controls:** `Size`, `TobinsQ`, `ROA`, `CapexAt`, `DividendPayer`, `OCF_Volatility`. (Note: `CurrentRatio` explicitly excluded; contemporaneous `CashHoldings` excluded).
- **Fixed Effects:** Firm + Calendar Year (via `PanelOLS` `EntityEffects` + `TimeEffects`).
- **Standard Errors:** Firm-clustered (`cov_type="clustered", cluster_entity=True`).
- **Outputs Expected:** Stage 3 panel (parquet), 18 Stage 4 regression txt files, `model_diagnostics.csv`, LaTeX table, summary stats.

## 3) Verification Matrix

| Claim (from provenance) | Location Claimed | Location Checked | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Panel has 112,968 rows, `file_name` unique** | `H1.md:109` | `h1_cash_holdings_panel.parquet` | PASS | `len(df)==112968`, `is_unique==True` |
| **`CashHoldings_lead` is correctly lead by 1 fiscal year** | `H1.md:162` | `build_h1...py:243` | PASS | 100% match in spot-checks; strictly enforces `fyearq+1` |
| **Zero row-delta on all panel merges** | `H1.md:118` | `build_h1...py:214` | PASS | Code explicitly asserts `after_len == before_len` |
| **Contemporaneous `CashHoldings` is not a control** | `H1.md:420` | `run_h1...py:101` | PASS | Confirmed absent from `CONTROL_VARS` |
| **`CurrentRatio` excluded from controls** | `H1.md:408` | `run_h1...py:101` | PASS | Confirmed absent from `CONTROL_VARS` |
| **Interaction `Uncertainty_x_Lev` uses raw product** | `H1.md:454` | `run_h1...py:304` | PASS | `df["Uncertainty_x_Lev"] = df["Uncertainty"] * df["Lev"]` |
| **Firm-clustered standard errors used** | `H1.md:434` | `run_h1...py:378` | PASS | `fit(cov_type="clustered", cluster_entity=True)` |
| **18 regressions (6 measures × 3 samples)** | `H1.md:262` | `model_diagnostics.csv` | PASS | Exactly 18 rows in diagnostics CSV |
| **One-tailed tests: H1a $\beta_1 > 0$, H1b $\beta_3 < 0$** | `H1.md:24` | `run_h1...py:437` | PASS | Validated logic: `p1_one = p1_two/2 if beta1>0 else 1-p1_two/2` |
| **Winsorization at 1%/99% per-year** | `H1.md:219` | `_compustat_engine.py` | PASS | Lev max (3.95) inherited correctly from Compustat fyearq p99 |
| **`CashHoldings_lead` constant within firm-year** | `H1.md:430` | `h1_cash_holdings_panel.parquet` | **FAIL** | Constant within *fiscal* year, but varies within *calendar* year (PanelOLS time dimension). |
| **Within-$R^2$ accurately reported in LaTeX** | `H1.md:45` | `run_h1_cash_holdings_table.tex` | **FAIL** | LaTeX reports ~0.84, but true within-$R^2$ is ~0.06. |

## 4) Findings

### 1. [BLOCKER] Inflated Within-$R^2$ via Manual Computation Bug
- **Symptom:** The LaTeX table reports Within-$R^2$ values of ~0.84, while the `regression_results_*.txt` files report ~0.06.
- **Evidence:** `run_h1_cash_holdings.py` lines 416-418 calculate `SS_tot = float(((y_dm - float(np.mean(y))) ** 2).sum())`. The grand mean `mean(y)` is used instead of the demeaned mean `mean(y_dm)`.
- **Why it matters:** Using the grand mean on double-demeaned data inflates the total sum of squares, causing the ratio $SS_{res}/SS_{tot}$ to shrink, artificially inflating the $R^2$ from 0.06 to 0.84. This misrepresents the model's explanatory power and could invalidate the paper's summary statistics.
- **Fix:** Remove the entire manual `within_r2` block. Use `model.rsquared_within` directly from `linearmodels.PanelOLS`. Update `_save_latex_table` to pull `rsquared` (the true within-$R^2$) instead of `within_r2`.
- **Rerun impact:** Re-run Stage 4 ONLY to regenerate `model_diagnostics.csv` and the LaTeX tables.

### 2. [MINOR] Provenance Claims Constant DV within Firm-Year Clusters
- **Symptom:** `H1.md` states `CashHoldings_lead` is constant within firm-year clusters to justify Moulton correction.
- **Evidence:** `df.groupby(['gvkey','year'])['CashHoldings_lead'].nunique()` shows 21,377 groups (~75%) have 2 distinct DV values.
- **Why it matters:** The PanelOLS uses *calendar* year (`year`), but the DV is measured at *fiscal* year end (`fyearq_int`). Calls in Q1 and Q3 of the same calendar year for a non-December FYE firm map to different fiscal years.
- **Fix:** Update `H1.md` section J.4 to state: "While `CashHoldings_lead` is constant within *fiscal* year, the panel uses *calendar* year for time FE, meaning the DV is not strictly constant within the PanelOLS `(gvkey, year)` index. However, firm-level clustering is still the econometrically correct approach for handling arbitrary within-firm serial correlation." No code changes required.
- **Rerun impact:** None.

### 3. [NOTE] Stale Docstrings
- **Symptom:** The module docstring claims HC1 standard errors are used.
- **Evidence:** `run_h1_cash_holdings.py` line 13.
- **Why it matters:** Contradicts the actual correct implementation on line 378 (`cluster_entity=True`).
- **Fix:** Update line 13 to read: "same firm-clustered standard errors".
- **Rerun impact:** None.

## 5) Rerun Plan

1. **Code Edit:** Edit `src/f1d/econometric/run_h1_cash_holdings.py`:
   - Delete lines 389-425 (the `try/except` block calculating `within_r2`).
   - In the `meta` dictionary (line 479), remove `"within_r2": within_r2,`.
   - In `_save_latex_table` (line 639), change `r2v = meta.get("within_r2", float("nan"))` to `r2v = meta.get("rsquared", float("nan"))`.
   - Fix docstring on line 13.
2. **Execute Stage 4:**
   ```bash
   python -m f1d.econometric.run_h1_cash_holdings
   ```
3. **Acceptance Tests:**
   - Check `h1_cash_holdings_table.tex`: The "Within-R$^2$" row should now report values around 0.05-0.06, matching the `.txt` outputs.
   - Run `python -c "import pandas as pd; print('within_r2' in pd.read_csv('outputs/econometric/h1_cash_holdings/latest/model_diagnostics.csv').columns)"` -> Should be `False`.

## 6) Hardening Recommendations

- **Repo-level:** The manual `within_r2` bug is systemic (identified as the "B8 fix" in other suites). Perform a global grep (`rg "within_r2 = 1.0 - ss_res"`) and remove this block from ALL Stage 4 scripts (`run_h2`, `run_h3`, `run_h4`, `run_h5`, `run_h7`). `PanelOLS.rsquared_within` is correct and should be trusted.
- **Suite-level:** Add an explicit assertion in `build_h1_cash_holdings_panel.py` checking `panel['CashHoldings_lead'].min() >= 0` to catch negative cash ratios early.

## 7) Command Log

1. `grep "H1|cash_holdings"` on `docs/provenance` to locate suite files.
2. Read `H1.md`, `build_h1_cash_holdings_panel.py`, and `run_h1_cash_holdings.py` to establish the contract.
3. Used `python -c` to verify Stage 3 panel integrity (`len=112968`, `is_unique(file_name)=True`).
4. Spot-checked the `CashHoldings_lead` fiscal-year shift logic, verifying 100% exact match against the subsequent year's latest call.
5. Cross-checked regression textual outputs against `model_diagnostics.csv` (100% match on coefficients, SEs, N, and t-stats).
6. Discovered the discrepancy between `model_diagnostics.csv` (`rsquared` = ~0.06) and the LaTeX table (`Within-R2` = ~0.84).
7. Audited the manual `within_r2` computation logic in Python, identifying the mathematical error (using grand mean instead of demeaned mean).
8. Analyzed `PanelOLS` index structure and confirmed the calendar vs. fiscal year mismatch causing DV non-constancy.

## 8) Open Gaps
- None. The audit was able to conclusively verify all claims and trace the root cause of the $R^2$ discrepancy using local artifacts.
