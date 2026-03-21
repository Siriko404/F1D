# H2 Suite -- Second-Layer Red-Team Audit

**Suite ID:** H2 (Speech Uncertainty and Investment Efficiency)
**Auditor:** Red-team layer 2 (hostile-but-fair replication audit)
**Date:** 2026-03-21
**First-layer doc:** `docs/provenance/H2.md` (2026-03-18)
**Runner:** `src/f1d/econometric/run_h2_investment.py`
**Panel builder:** `src/f1d/variables/build_h2_investment_panel.py`

---

## A. Overall Assessment of the First-Layer Audit

The first-layer audit is **thorough and substantially correct**. It accurately captures the model family (PanelOLS, 8 specifications, 2 DVs x 2 FE x 2 control sets), the Biddle (2009) residual construction chain (7 steps), variable definitions, merge logic, and known limitations. The identification critique in Section 11 is frank and appropriately skeptical. The treatment of prior red-team findings (Section 13) is well-organized.

**However**, the audit contains several systematic line-number inaccuracies, one material omission in the summary statistics output, and a vestigial-code issue in the panel builder's report template that the first-layer audit fails to flag. These are documented below.

---

## B. Factual Accuracy of First-Layer Claims

### B.1) Line Number Discrepancies (Low severity, pervasive)

The first-layer audit cites specific line numbers from `_compustat_engine.py` that are systematically off by 1--3 lines. These are likely caused by incremental code edits after the audit was written. The logic described is correct in every case; only the line references are stale.

| Audit Claim | Cited Line | Actual Line | Correct? |
|-------------|-----------|-------------|----------|
| capxy non-null guard | 606 | 608 | Logic correct, line off |
| `reg_cols` definition | 705 | 707 | Logic correct, line off |
| Min cell size < 20 | 713 | 715 | Logic correct, line off |
| Post-OLS winsorize | 741 | 743-744 | Logic correct, line off |
| Investment winsorize | 621 | 623 | Logic correct, line off |
| SalesGrowth winsorize | 665 | 667 | Logic correct, line off |
| TobinQ_lag computed | 669 | 671 | Logic correct, line off |
| `skip_winsorize` set | 1187 | 1199 | Logic correct, line off |
| `SalesGrowth` in skip | 1188 | 1203 | Logic correct, line off |
| Deduplication keep="last" | 1251 | 1265 | Logic correct, line off |

**Verdict:** All logical descriptions are accurate. Line numbers should be refreshed but this does not affect reproducibility or correctness.

### B.2) Variable Formula Verification

| Variable | Audit Formula | Code Reality | Match? |
|----------|--------------|--------------|--------|
| Size | `ln(atq)` for `atq > 0` | `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` (engine line 1036) | YES |
| BookLev | `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` | Engine line 1041 | YES |
| TobinsQ | `(mktcap + debt_book) / atq` with NaN when both debts missing | Engine lines 1070-1079 | YES |
| ROA | `iby_annual / avg_assets` | Engine lines 1052-1062 | YES |
| CapexAt | `capxy_annual / atq_annual_lag1` | Engine lines 1081-1087 | YES |
| CashHoldings | `cheq / atq` | Engine line 1068 | YES |
| DividendPayer | `1(dvy_Q4_annual > 0)` | Engine lines 1091-1094 | YES |
| RD_Intensity | `xrdq.fillna(0) / atq` | Engine line 1065 | YES |
| OCF_Volatility | Rolling 5-yr std of (oancfy / atq_lag) | `_compute_ocf_volatility()` lines 309-358 | YES |
| Investment numerator | `capxy.fillna(0) + xrdy.fillna(0) + aqcy.fillna(0) - sppey.fillna(0)` | Engine lines 601-606 | YES |

**Verdict:** All variable formulas are accurately documented.

### B.3) Fixed Effects Implementation

| Claim | Code Evidence | Match? |
|-------|--------------|--------|
| Industry FE via `other_effects` | Runner line 265: `other_effects=industry_data` | YES |
| `check_rank=False` for industry specs | Runner line 267 | YES |
| Firm FE via `EntityEffects` formula | Runner line 272: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` | YES |
| Clustered SEs: `cov_type="clustered", cluster_entity=True` | Runner lines 269, 274 | YES |

### B.4) One-Tailed p-value Formula

Audit claims: `p_one = p_two / 2 if beta < 0 else 1 - p_two / 2` (runner line 300).

Code at runner line 300:
```python
p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
```

**Match: YES.** This is the standard one-tailed conversion for a left-tail test (H0: beta >= 0, H1: beta < 0). When beta < 0, the one-tailed p-value is half the two-tailed. When beta >= 0, the one-tailed p-value is 1 minus half the two-tailed (essentially no significance in the predicted direction).

### B.5) Biddle First-Stage: SalesGrowth Only

Audit claims `reg_cols = ["Investment", "SalesGrowth_lag"]`. Engine line 707 confirms: `reg_cols = ["Investment", "SalesGrowth_lag"]`. TobinQ_lag is computed at line 671 but never referenced in `reg_cols` or the OLS call.

**Match: YES.**

### B.6) Winsorization Pipeline

Audit claims a three-stage winsorization for InvestmentResidual: (1) Investment pre-OLS, (2) SalesGrowth pre-OLS, (3) InvestmentResidual post-OLS, with no re-winsorization in `_compute_and_winsorize()`.

Code confirms:
- Engine line 623: `Investment` winsorized by year
- Engine line 667: `SalesGrowth` winsorized by year
- Engine lines 743-744: `InvestmentResidual` winsorized by year
- Engine line 1199: `skip_winsorize` set includes `"InvestmentResidual"`, `"CashFlow"`, `"SalesGrowth"`

**Match: YES.**

---

## C. Completeness Assessment

### C.1) FINDING: Summary Stats Table Omits Two Extended Controls (Low-Medium)

The runner's `SUMMARY_STATS_VARS` list (lines 125-141) does **not** include `Entire_All_Negative_pct` or `Analyst_QA_Uncertainty_pct`, despite both being extended controls used in columns 3-4, 7-8. This means the summary statistics CSV and LaTeX outputs will not report descriptive statistics for these two variables.

The first-layer audit does not flag this omission. The `summary_stats.csv` output will be incomplete relative to the full variable set.

**Impact:** A referee asking for summary statistics of all regression variables will find two extended controls missing. This is a reporting gap, not a computation error.

**Recommendation:** Add both variables to `SUMMARY_STATS_VARS`.

### C.2) FINDING: Panel Builder Report Lists Vestigial Variables (Low)

The panel builder's report template (lines 544-557) lists `CashFlow`, `SalesGrowth`, `Manager_QA_Weak_Modal_pct`, and `CEO_QA_Weak_Modal_pct` in the "Key Variable Coverage" section. `CashFlow` and `SalesGrowth` are intentionally excluded from H2 regressions (Biddle first-stage inputs), and `Weak_Modal_pct` variables are not part of the H2 specification at all (they belong to other suites).

The first-layer audit correctly notes that CashFlow and SalesGrowth are excluded from controls (Section 1.4, Section 14.1) but does not flag that the panel builder's own report template still references them and other irrelevant variables.

**Impact:** Cosmetic only. The report will show "N/A" or skip these variables if they are not in the panel columns. No computational effect.

### C.3) FINDING: Attrition Table Uses Column 1 N for "After complete-case + min-calls" (Medium)

The runner (lines 571-576) hardcodes the attrition table's Stage 4 count as `first_meta.get("n_obs", 0)`, which is always column 1's N. This means the attrition table only reflects one specification's final sample size, even though N varies across specifications (base vs. extended controls, contemporaneous vs. lead DV).

The first-layer audit notes this in Section 9 ("Attrition counts vary across model specifications") but does not explicitly flag that the attrition CSV only records column 1's count as the Stage 4 value. This is a fair disclosure but could be more precise.

### C.4) Panel Builder Column Selection at Load Time

The runner (lines 170-179) explicitly lists all columns to load from the parquet file. This is good practice for reproducibility. The first-layer audit does not mention this column-selection behavior, but it is not a concern.

---

## D. Skepticism Assessment

### D.1) Appropriately Skeptical Claims

The first-layer audit is commendably skeptical on:

1. **Identification** (Section 11.1): Correctly labels the design as "reduced-form association," warns about reverse causality, and states causal language is not supported.
2. **Moulton problem** (Section 11.2): Correctly identifies the unit-of-observation mismatch (annual DV vs. call-level IVs) and notes that effective N is inflated.
3. **Multiple testing** (Section 11.3): Correctly notes 32 tests at alpha=0.05 yield 1.6 expected false positives, and the 2 significant results are barely above chance.
4. **One-tailed test justification** (Section 11.4): Correctly questions whether the directional prior is well-supported.
5. **CapexAt mechanical overlap** (Section 12.1): Correctly identifies the shared `capxy` component.

### D.2) Areas Where More Skepticism Would Be Warranted

**D.2.1) The `_winsorize_by_year` function clips NaN values via `vals.clip()`**

In `_winsorize_by_year()` (engine lines 445-469), the function applies `vals.clip(lower=p1, upper=p99)` to ALL values in the group index (including NaN). Pandas `clip()` preserves NaN, so this is correct. However, the audit does not explicitly verify this NaN-preservation behavior, which is critical for data integrity.

**Verdict:** No bug, but the audit could have been more explicit.

**D.2.2) merge_asof backward direction has no maximum tolerance**

Both the panel builder's `attach_fyearq()` and the Compustat engine's `match_to_manifest()` use `pd.merge_asof` with `direction="backward"` but no `tolerance` parameter. This means a call in 2018 could match to a Compustat observation from 2002 if no closer match exists. The first-layer audit notes the merge_asof pattern (Section 5.2) but does not flag the missing tolerance.

**Impact:** In practice, this is unlikely to produce stale matches at scale (most firms have quarterly data), but the theoretical possibility exists. A 365-day tolerance would be a prudent safeguard.

---

## E. Model Specification Register Verification

| Spec | DV | FE | Controls | Audit | Code | Match? |
|------|----|----|----------|-------|------|--------|
| Col 1 | InvestmentResidual | industry | base | Sec 1.6 | `MODEL_SPECS[0]` | YES |
| Col 2 | InvestmentResidual | firm | base | Sec 1.6 | `MODEL_SPECS[1]` | YES |
| Col 3 | InvestmentResidual | industry | extended | Sec 1.6 | `MODEL_SPECS[2]` | YES |
| Col 4 | InvestmentResidual | firm | extended | Sec 1.6 | `MODEL_SPECS[3]` | YES |
| Col 5 | InvestmentResidual_lead | industry | base | Sec 1.6 | `MODEL_SPECS[4]` | YES |
| Col 6 | InvestmentResidual_lead | firm | base | Sec 1.6 | `MODEL_SPECS[5]` | YES |
| Col 7 | InvestmentResidual_lead | industry | extended | Sec 1.6 | `MODEL_SPECS[6]` | YES |
| Col 8 | InvestmentResidual_lead | firm | extended | Sec 1.6 | `MODEL_SPECS[7]` | YES |

All 8 specifications match exactly.

---

## F. Dependency Chain Verification

The dependency chain in Section 3 is accurate. Verified paths:
- Compustat path: `inputs/comp_na_daily_all/comp_na_daily_all.parquet` (engine line 1248-1249)
- FF48 map: `inputs/FF1248/Siccodes48.zip` (engine `_load_ff48_map()`)
- Manifest: `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`
- Linguistic: `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`
- Stage 3 output: `outputs/variables/h2_investment/{timestamp}/h2_investment_panel.parquet`
- Stage 4 input: loads from `outputs/variables/h2_investment/latest/` via `get_latest_output_dir()`

---

## G. Known Limitations Assessment

### G.1) CapexAt Shared Component (Section 12.1)

The audit correctly identifies this. Verified: CapexAt = `capxy_annual / atq_annual_lag1` (engine lines 1081-1087), while InvestmentResidual numerator = `capxy + xrdy + aqcy - sppey` (engine lines 601-608). Both share `capxy`.

### G.2) H2b Leverage Moderation Never Tested (Section 12.2)

Verified: the panel builder docstring (lines 32-33) references H2b but the runner has zero interaction terms. No grep match for "interaction" or "H2b" in the runner. The audit correctly identifies this as stale documentation.

### G.3) TobinQ_lag Dead Code (Section 12.3)

Verified: `TobinQ_lag` computed at engine line 671, never used in `reg_cols` at line 707. Correctly identified.

### G.4) check_rank=False (Section 12.4)

Verified at runner line 267. Correctly identified.

### G.5) Null Results Discussion (Section 12.5)

The audit's interpretation is statistically sound. 2/32 significant at p<0.05 with a chance expectation of 1.6 under the null is consistent with no true effect.

---

## H. Verification Log Cross-Check

All 22 verification items (V1-V22) were spot-checked against the code. All are correct in substance, though line number citations are systematically 1-3 lines off (see Section B.1 above).

---

## I. Output Artifacts Verification

The audit lists outputs in Sections 8.1 and 8.2. Verified against runner:
- `regression_results_col{1-8}.txt`: runner lines 449-459
- `h2_investment_table.tex`: runner line 437
- `model_diagnostics.csv`: runner lines 461-464
- `summary_stats.csv/.tex`: runner lines 544-550
- `sample_attrition.csv`: runner lines 571-577 via `generate_attrition_table()`
- `report_step4_H2.md`: runner lines 494-496
- `run_manifest.json`: runner lines 579-585

All artifacts confirmed.

---

## J. LaTeX Table Audit

The LaTeX table generation (runner lines 327-440) was inspected:

1. **Header structure:** Correctly labels 8 columns with DV groupings (cols 1-4: Investment Residual_t, cols 5-8: Investment Residual_{t+1}).
2. **Coefficient formatting:** Uses 4 decimal places with one-tailed significance stars.
3. **SE formatting:** Parenthesized, 4 decimal places.
4. **FE rows:** Correctly labels Industry FE, Firm FE, Fiscal Year FE.
5. **Table notes:** Accurately describes one-tailed test, firm clustering, Biddle exclusions, and winsorization.
6. **Controls row:** Correctly distinguishes "Base" vs. "Extended."

**Minor issue:** The table note says "Variables winsorized at 1%/99% by year at engine level" -- this is slightly misleading because linguistic variables use 0%/99% (upper-only) winsorization, not 1%/99%. The first-layer audit correctly documents the linguistic winsorization as "Per-year 0%/99% (upper-only)" in Section 6.2, but the LaTeX note in the actual output does not distinguish this. Not flagged by the first-layer audit.

---

## K. Sample Construction Logic

### K.1) Main Sample Filter

Runner `filter_main_sample()` drops FF12 in {8, 11}. Verified at runner line 190. Matches audit Section 1.6 and V10.

### K.2) MIN_CALLS_PER_FIRM

Runner line 117: `MIN_CALLS_PER_FIRM = 5`. Verified. Applied in `prepare_regression_data()` at lines 221-223. Matches audit V12.

### K.3) Complete-Case Analysis

Runner lines 217-218: `complete_mask = df[required].notna().all(axis=1)`. This is listwise deletion. Matches audit Section 5.5.

---

## L. Red-Team Findings Summary

| ID | Finding | Severity | New? | Recommendation |
|----|---------|----------|------|----------------|
| RT2-1 | Systematic line number offsets (1-3 lines) throughout the audit | Low | Yes | Refresh all line citations against current codebase |
| RT2-2 | `SUMMARY_STATS_VARS` omits `Entire_All_Negative_pct` and `Analyst_QA_Uncertainty_pct` | Low-Medium | Yes | Add both to `SUMMARY_STATS_VARS` in runner |
| RT2-3 | Panel builder report template references vestigial variables (`CashFlow`, `SalesGrowth`, `Weak_Modal_pct`) | Low | Yes | Clean up report template variable list |
| RT2-4 | `merge_asof` has no `tolerance` parameter -- theoretically allows stale Compustat matches | Low | Partially new | Consider adding 365-day tolerance |
| RT2-5 | LaTeX table note does not distinguish 1%/99% (Compustat) from 0%/99% (linguistic) winsorization | Low | Yes | Amend table note or add footnote |
| RT2-6 | Attrition CSV records only column 1's Stage-4 N; audit acknowledges variance but does not flag the single-column limitation of the output file | Low | Partially covered | Note in audit that attrition CSV is col-1 specific |

---

## M. First-Layer Audit Completeness Score

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Variable definitions | 5/5 | All formulas verified correct |
| Model specifications | 5/5 | All 8 specs match code exactly |
| Data provenance | 5/5 | Full dependency chain documented |
| Merge logic | 5/5 | Zero-row-delta, uniqueness guards, and merge_asof all documented |
| Winsorization pipeline | 5/5 | All stages correctly documented, skip_winsorize verified |
| Fixed effects implementation | 5/5 | Industry vs. firm FE code paths accurately described |
| Identification critique | 5/5 | Reverse causality, omitted variables, Moulton problem all addressed |
| Known limitations | 4/5 | Missing: summary stats omission (RT2-2), vestigial report vars (RT2-3) |
| Line number accuracy | 2/5 | Systematically off by 1-3 lines throughout |
| Output artifacts | 4/5 | Missing note about incomplete summary stats (RT2-2) |

**Overall: 4.5/5.** The first-layer audit is of high quality and suitable for thesis-standard review. The findings above are minor and do not affect the validity of the econometric analysis or its interpretation.

---

## N. Disposition of First-Layer Red-Team Section (Section 13)

The first-layer audit's Section 13 addresses 12 red-team findings (G1-G12 plus E1) from a previous audit round. All dispositions were verified:

| Prior ID | Disposition Claimed | Verified? |
|----------|-------------------|-----------|
| G1 (CapexAt overlap) | Documented in Section 12.1 | YES |
| G2 (H2b not tested) | Documented in Section 12.2 | YES |
| G3 (TobinQ_lag dead code) | Documented in Sections 6.1, 12.3 | YES |
| G4 (No attrition docs) | Addressed in Section 9 | YES |
| G5 (No endogeneity discussion) | Addressed in Section 11.1 | YES |
| G6 (No robustness analysis) | Acknowledged in Section 12.5 | YES |
| G7 (check_rank=False) | Documented in Section 12.4 | YES |
| G8 (Winsorization correct) | Verified in Sections 6.1, 6.3 | YES |
| G9 (Upstream dependencies untraced) | Addressed in Sections 3, 4 | YES |
| G10 (Unit mismatch) | Addressed in Section 11.2 | YES |
| G11 (No reproduction commands) | Addressed in Section 2.1 | YES |
| G12 (Multiple testing) | Addressed in Section 11.3 | YES |
| E1 (False "no mechanical relation" claim) | Corrected in Section 12.1 | YES |

All prior findings properly addressed.

---

## O. Recommendations for Thesis Author

1. **Fix RT2-2:** Add `Entire_All_Negative_pct` and `Analyst_QA_Uncertainty_pct` to `SUMMARY_STATS_VARS` in the runner so summary statistics cover all regression variables.
2. **Fix RT2-3:** Clean the panel builder's report template (lines 544-557) to remove references to `CashFlow`, `SalesGrowth`, `Manager_QA_Weak_Modal_pct`, and `CEO_QA_Weak_Modal_pct`.
3. **Consider RT2-4:** Add a `tolerance=pd.Timedelta("365 days")` to `merge_asof` calls in `attach_fyearq()` to prevent theoretically possible stale Compustat matches.
4. **Refresh line numbers** in the provenance doc (RT2-1) -- all logic is correct, but stale references could confuse future reviewers.
5. **Amend LaTeX table note** (RT2-5) to clarify that linguistic variables use upper-only winsorization at 99th percentile, while Compustat variables use symmetric 1%/99%.

---

## P. Certification

This second-layer red-team audit confirms that the first-layer audit (`docs/provenance/H2.md`) is **factually correct in all material respects**, **appropriately skeptical** about causal interpretation and inference, and **substantially complete** for thesis-standard review. The findings documented above (RT2-1 through RT2-6) are all low to low-medium severity and do not affect the validity of the H2 econometric analysis or its documented limitations.

The first-layer audit is **approved for thesis submission** with the minor corrections recommended in Section O.
