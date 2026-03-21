# H12 Payout Ratio -- Second-Layer Red-Team Audit

**Generated:** 2026-03-21
**Suite ID:** H12
**Auditor role:** Hostile-but-fair replication auditor (second layer)
**Target:** First-layer audit doc `docs/provenance/H12.md` (2026-03-18)

---

## A. Scope & Objective

This audit independently verifies the factual claims, line-number references, and analytical completeness of the first-layer provenance audit for the H12 (Payout Ratio) suite. The second-layer auditor re-opens the runner (`src/f1d/econometric/run_h12_div_intensity.py`), panel builder (`src/f1d/variables/build_h12_div_intensity_panel.py`), and engine (`src/f1d/shared/variables/_compustat_engine.py`) to verify claims against the actual codebase.

---

## B. First-Layer Claims Verification

### B1. Line-number reference accuracy

The first-layer audit embeds dozens of line-number references to the engine, runner, and builder. Many are systematically off by 1-3 lines due to code drift since the audit was written. While the spirit of each reference is correct (the cited code exists nearby), the exact line numbers no longer match.

| Audit claim | Cited line | Actual line | Status |
|------------|-----------|-------------|--------|
| `dvy_annual` via `_compute_annual_q4_variable` | Engine L1089 | Engine L1091 | OFF-BY-2 |
| `iby_annual` via `_compute_annual_q4_variable` | Engine L1057 | Engine L1059 | OFF-BY-2 |
| `dvy_for_payout = ...fillna(0)` | Engine L1106 | Engine L1108 | OFF-BY-2 |
| `np.where(iby_for_payout > 0, ...)` | Engine L1108-1112 | Engine L1110-1114 | OFF-BY-2 |
| `Size = np.where(atq > 0, ...)` | Engine L1034 | Engine L1036 | OFF-BY-2 |
| `PayoutRatio` in `ratio_cols` | Engine L1163 | Engine L1176 | OFF-BY-13 |
| `inf -> NaN cleanup` | Engine L1151-1172 | Engine L1164-1186 | OFF-BY-13 |
| `ratio_cols list` | Engine L1152-1170 | Engine L1165-1184 | OFF-BY-13 |
| `skip_winsorize` set | Engine L1185-1193 | Engine L1199-1207 | OFF-BY-14 |
| `winsorize_cols loop` | Engine L1194-1201 | Engine L1208-1215 | OFF-BY-14 |
| `merge_asof backward` | Engine L1287-1294 | Engine L1301-1308 | OFF-BY-14 |
| `_compute_annual_q4_variable` function | Engine L234-274 | Engine L236-276 | OFF-BY-2 |
| `_winsorize_by_year min_obs=10` | Engine L444, L462 | Engine L446, L464 | OFF-BY-2 |
| `OCF_Volatility rolling` | Engine L336-340 | Engine L340-342 | OFF-BY-4 |

**Verdict:** All references point to the correct code construct but are systematically offset. This is consistent with minor edits (added/removed lines) since the audit was authored. The references are **directionally correct but not pinpoint-accurate**.

### B2. Formula accuracy

| Variable | Audit claim | Actual code | Verdict |
|----------|------------|-------------|---------|
| PayoutRatio | `dvy / iby when iby > 0` | `np.where(iby_for_payout > 0, dvy_for_payout / iby_for_payout, np.nan)` (L1110-1114) | **CORRECT** |
| dvy fillna(0) | `fillna(0)` before division | `pd.Series(dvy_annual, ...).fillna(0)` (L1108) | **CORRECT** |
| Size | `ln(atq)` | `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` (L1036) | **CORRECT** |
| TobinsQ | `(atq + cshoq * prccq - ceqq) / atq` | `(mktcap + debt_book) / atq` where `mktcap = cshoq * prccq`, `debt_book = dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)` (L1069-1078) | **INCORRECT** -- see C1 |
| BookLev | `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` | Same (L1041) | **CORRECT** |
| ROA | `iby_annual / avg_assets` | Same (L1060-1062) | **CORRECT** |
| CashHoldings | `cheq / atq` | Same (L1068) | **CORRECT** |
| CapexAt | `capxy_annual / atq_annual_lag1` | Same (L1082-1087) | **CORRECT** |
| RD_Intensity | `xrdq.fillna(0) / atq` | Same (L1065) | **CORRECT** |

### B3. Structural claims verification

| # | Claim | Verification | Verdict |
|---|-------|-------------|---------|
| V5 | 4 simultaneous IVs in every model | Runner L90-95: `KEY_IVS` list with 4 entries; L289: `exog = KEY_IVS + controls` | **CONFIRMED** |
| V6 | 8 model specifications | Runner L116-125: `MODEL_SPECS` list, 8 entries | **CONFIRMED** |
| V7 | Industry FE: absorbed via `other_effects` | Runner L306-314: `PanelOLS(... other_effects=industry_data ...)` | **CONFIRMED** |
| V8 | Firm FE: `EntityEffects + TimeEffects` via `from_formula` | Runner L318-320 | **CONFIRMED** |
| V9 | Firm-clustered SEs | Runner L315, L321: `.fit(cov_type="clustered", cluster_entity=True)` | **CONFIRMED** |
| V10 | One-tailed test: beta < 0 | Runner L350-351 | **CONFIRMED** |
| V12 | Main sample excludes FF12={8,11} | Runner L214 | **CONFIRMED** |
| V16 | PayoutRatio_lead: shift(-1) with consecutive-year check | Builder L184-191 | **CONFIRMED** |
| V18 | IV aggregation = arithmetic mean | Builder L157-158 | **CONFIRMED** |
| V19 | No MIN_CALLS_PER_FIRM filter | Runner L254 comment, no filter code | **CONFIRMED** |

---

## C. Errors Found in First-Layer Audit

### C1. TobinsQ formula is WRONG in the audit doc (MODERATE)

**Audit doc Section 6c (TobinsQ) states:**
> Formula: `(atq + cshoq * prccq - ceqq) / atq`

**Actual code (Engine L1069-1078):**
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

The actual formula is `(market_cap + book_debt) / total_assets`, NOT `(total_assets + market_cap - book_equity) / total_assets`. While both are approximations of Tobin's Q, they are algebraically distinct: the audit's claimed formula replaces book equity (ceqq) with assets minus market cap, whereas the code uses the standard Chung & Pruitt (1994) approximation `(MVE + Debt) / TA`. The audit doc's formula is not what the code implements.

Additionally, the audit doc description mentions `debt_book = np.where(dlcq.isna() & dlttq.isna(), np.nan, dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0))` in the "Intermediate" row, which IS correct, but then contradicts this with the top-level formula. The audit is internally inconsistent.

### C2. RD_Intensity inf cleanup claim is WRONG (MINOR)

**Audit doc Section 6c (RD_Intensity) states:**
> Inf cleanup: Not in explicit `ratio_cols` list, but any inf from division by zero atq would persist.

**Actual code (Engine L1171):** `RD_Intensity` IS in the `ratio_cols` list at line 1171. The audit doc falsely claims it is absent. Inf values from `xrdq.fillna(0) / atq` where `atq = 0` ARE properly cleaned to NaN.

### C3. OCF_Volatility line references are stale (MINOR)

The audit doc Section 6c claims OCF_Volatility's `rolling("1826D", min_periods=3).std()` is at Engine L336-340. The actual code is at L340-342. The audit also says the function spans Engine L307-356; it actually spans L309-358.

---

## D. Omissions in First-Layer Audit

### D1. No mention of `PayoutRatio_q` (MINOR)

The engine computes both `PayoutRatio` (annual, dvy/iby) and `PayoutRatio_q` (quarterly, `dvpspq * cshoq / ibq`) at Engine L1116-1125. The quarterly variant is in `COMPUSTAT_COLS`, in `ratio_cols`, and gets winsorized. The first-layer audit never mentions `PayoutRatio_q`. While it is not used in the H12 runner, its existence in the engine and its presence in `ratio_cols` alongside `PayoutRatio` should be documented for completeness. No impact on results.

### D2. No mention of `DivIntensity` still being computed (MINOR)

The engine still computes `DivIntensity = dvy_annual / atq_annual_lag1` at Engine L1096-1103 (the old H12 DV). This variable is in `COMPUSTAT_COLS` and is computed alongside `PayoutRatio`. The first-layer audit discusses the "redesign from old H12" in Section 14a but does not mention that the old DV is still being computed and carried through the engine. No impact on H12 results, but creates potential for confusion.

### D3. Absence of VIF or correlation diagnostics (already noted but underweighted)

The first-layer audit notes multicollinearity among the 4 IVs in Section 11c but treats it as a minor concern. Given that CEO is a subset of Manager (the audit doc correctly notes "All managers (includes CEO)"), the Manager QA and CEO QA variables are likely highly collinear. This is more than a documentation gap -- it is a material inference concern that could make individual IV coefficients unreliable and unstable across specifications.

### D4. No discussion of `drop_absorbed=True` interaction with `entity_effects=False`

In the industry FE model (Runner L306-314), `entity_effects=False` is set explicitly while `other_effects=industry_data` provides the industry dummies. The audit mentions `check_rank=False` but does not discuss whether `drop_absorbed=True` correctly handles the interaction between `time_effects=True` and `other_effects` when some industry-year cells may be singletons or empty. This is a potential edge-case concern for PanelOLS.

---

## E. Analytical Gaps in First-Layer Audit

### E1. PayoutRatio winsorization before lead construction creates look-ahead concern

The first-layer audit (Section 6a, step 6-8) correctly documents that PayoutRatio is winsorized at the engine level (1%/99% per fiscal year) before the lead is constructed in the panel builder. However, it does not flag the subtle timing implication: the winsorization percentiles for year t+1's PayoutRatio are computed using ALL firms in year t+1, including those that will later be filtered out by FF12 exclusion or complete-case restrictions. The lead variable thus inherits winsorization bounds computed on a different population than the estimation sample. This is standard practice but should be explicitly acknowledged.

### E2. `groupby.last()` on `Volatility` conflates distinct values

The audit doc (Section 6c, Volatility) correctly notes that "Volatility varies across calls within a firm-year because different calls have different inter-call windows." It then states the aggregation takes "the last call's volatility value." However, `groupby.last()` in pandas returns the last NON-NULL value, not the last row's value. If the last call within a firm-year has a NaN Volatility (e.g., fewer than 10 trading days in its window), the penultimate call's Volatility would be used instead. The audit mentions this semantic issue generically (L7) but does not flag the specific concern for Volatility, which is the one variable where within-firm-year variation is expected.

### E3. No Hausman test or RE comparison mentioned

The audit doc Section 11d states "No Hausman test for RE vs FE is reported, which is standard practice in applied corporate finance." This is a fair characterization but the audit should note that the absence of RE specifications means there is no efficiency comparison available. If FE is strictly more restrictive and the data supports RE, the FE estimates will be consistent but inefficient.

---

## F. Verification of Red-Team Findings Disposition (Section 13)

| Red-team ID | First-layer disposition | Second-layer assessment |
|-------------|------------------------|------------------------|
| C1 (no upper-bound censoring) | Documented as L1 (MAJOR) | **AGREE.** Real concern, correctly elevated. |
| C2 (ROA-PayoutRatio Kronmal overlap) | Documented as L2 (MODERATE) | **AGREE.** Correctly identified. |
| C3 (`check_rank=False`) | Documented as L6 (MINOR) | **AGREE.** Negligible with `drop_absorbed=True`. |
| C4 (`groupby.last()` semantics) | Documented as L7 (MINOR) | **AGREE** but **UNDERWEIGHTED** for Volatility specifically (see E2). |
| C5 (no intercept in industry FE) | Documented as NEGLIGIBLE | **AGREE.** Non-issue. |
| C6 (summary stats pre-complete-case) | Documented as L4 (MINOR) | **AGREE.** Standard practice but should be disclosed. |
| C7 (attrition table Col 1 only) | Documented as L5 (MINOR) | **AGREE.** |
| C8 (mass point at zero) | Documented as L3 (MODERATE) | **AGREE.** Correctly identified. |

---

## G. Design Decision Review

### G1. PayoutRatio = dvy/iby vs. dvy/atq

The audit doc Section 14a correctly explains the redesign rationale. The Attig et al. (2013) formulation is standard. **No objection.**

### G2. Four simultaneous IVs

The design choice to enter all four IVs simultaneously is well-motivated by the cited literature (Brochet et al., Hassan et al.). However, the high collinearity between CEO and Manager measures (CEO is a subset of Manager) makes interpretation of individual coefficients problematic. The audit should recommend examining each IV pair separately as a robustness check.

### G3. Main sample only

Excluding Finance (FF12=11) and Utility (FF12=8) is standard in corporate finance empirical work. **No objection.**

---

## H. Output File Verification

| Audit claim | Verification | Verdict |
|------------|-------------|---------|
| 8 output files listed in docstring | Runner L49-57 lists 8 files (omits `sample_attrition.tex`) | **CONFIRMED** -- audit correctly flags this mismatch |
| 9 files produced in code | Runner produces: 8 regression results + table + diagnostics + summary stats (csv+tex) + report + attrition (csv+tex) + manifest = up to 14 files for a full run | **PARTIALLY INCORRECT** -- the audit says 9 files but the actual count is higher. The docstring lists 8, the audit claims 9, but a full run with all 8 regressions completing produces: 8 regression_results + 1 table + 1 diagnostics + 2 summary_stats + 1 report + 2 attrition + 1 manifest = 16 files. The audit's characterization of "9 files" is misleading. |

---

## I. Reproducibility Assessment

| Property | Audit claim | Verification | Verdict |
|----------|------------|-------------|---------|
| Deterministic | Yes | No random seeds, no sampling, no stochastic operations | **CONFIRMED** |
| Panel builder command | `python -m f1d.variables.build_h12_div_intensity_panel` | Builder has `__main__` block | **CONFIRMED** |
| Dry-run command | `python -m f1d.econometric.run_h12_div_intensity --dry-run` | Runner L799-808 | **CONFIRMED** |
| Timestamp-based dirs | Yes | Builder L416 and Runner L663 use datetime-stamped subdirectories | **CONFIRMED** (line refs off by ~2) |

---

## J. Estimation Implementation Audit

### J1. Industry FE implementation

The runner uses `PanelOLS` constructor with `other_effects=industry_data` where `industry_data = df_panel["ff12_code"]` (Runner L305). This absorbs industry FE correctly. Combined with `time_effects=True`, this gives Industry + FiscalYear two-way FE. **CONFIRMED correct.**

### J2. Firm FE implementation

The runner uses `PanelOLS.from_formula` with `EntityEffects + TimeEffects` (Runner L318-321). The entity index is `gvkey` (set at L298). **CONFIRMED correct.**

### J3. Clustering implementation

All models use `.fit(cov_type="clustered", cluster_entity=True)` (Runner L315, L321). Entity = gvkey = firm. **CONFIRMED correct.**

### J4. One-tailed p-value computation

Runner L350-351: `p_one = p_two / 2 if beta < 0 else 1 - p_two / 2`. This is the standard one-tailed conversion for a left-tail test (H0: beta >= 0 vs H1: beta < 0). When beta < 0 (in the predicted direction), p_one = p_two / 2 (more significant). When beta > 0 (against prediction), p_one = 1 - p_two / 2 (less significant). **CONFIRMED correct.**

---

## K. Panel Construction Audit

### K1. Merge integrity

Builder L264-269: Each builder's data is merged on `file_name` with `how="left"`. After each merge, `delta = after_len - before_len` is checked and must equal 0 (no row inflation). **CONFIRMED correct.**

### K2. Aggregation integrity

Builder L151-153: Financial variables aggregated via `groupby(["gvkey", "fyearq"]).last()`.
Builder L157-158: IVs aggregated via `groupby(["gvkey", "fyearq"]).mean()`.
Builder L160: Rename with `Avg_` prefix.
**CONFIRMED correct.**

### K3. Lead variable construction

Builder L183-195: `shift(-1)` within gvkey, consecutive-year check using Int64 arithmetic, non-consecutive years set to NaN. **CONFIRMED correct.**

---

## L. Summary of Findings

### Errors in first-layer audit

| ID | Severity | Description |
|----|----------|-------------|
| RT-C1 | **MODERATE** | TobinsQ formula incorrectly stated as `(atq + cshoq*prccq - ceqq) / atq`. Actual code computes `(mktcap + debt_book) / atq`. The audit's own "Intermediate" section contradicts its "Formula" row. |
| RT-C2 | **MINOR** | RD_Intensity falsely claimed to be absent from `ratio_cols`. It IS in `ratio_cols` at Engine L1171. Inf values are properly cleaned. |
| RT-C3 | **MINOR** | Systematic line-number drift (off by 2-14 lines) across all engine references. Directionally correct but not pinpoint-accurate. |
| RT-C4 | **MINOR** | Output file count claimed as "9" is misleading. A full successful run produces 16 files (8 regression results + 8 other files). |

### Omissions in first-layer audit

| ID | Severity | Description |
|----|----------|-------------|
| RT-D1 | **MINOR** | `PayoutRatio_q` (quarterly variant) exists in the engine but is never mentioned. |
| RT-D2 | **MINOR** | `DivIntensity` (old H12 DV) still computed in engine but not flagged as legacy. |
| RT-D3 | **MODERATE** | CEO-subset-of-Manager collinearity concern underweighted. The 4-IV design enters Manager (which includes CEO) alongside CEO measures -- near-perfect collinearity for the same context segment is likely. |
| RT-D4 | **MINOR** | Winsorization applied pre-sample-filter means lead variable inherits bounds from broader population. |

### Analytical gaps

| ID | Severity | Description |
|----|----------|-------------|
| RT-E1 | **MINOR** | `groupby.last()` for Volatility specifically (the one variable with within-firm-year variation) deserves dedicated discussion, not just generic mention. |
| RT-E2 | **MINOR** | No mention of whether `drop_absorbed=True` correctly handles industry-year singletons in the `other_effects` specification. |

---

## M. Corrective Actions Required

1. **Fix TobinsQ formula** in Section 6c to match the actual code: `(cshoq * prccq + debt_book) / atq` where `debt_book = np.where(dlcq.isna() & dlttq.isna(), np.nan, dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0))`.
2. **Fix RD_Intensity inf cleanup claim** in Section 6c: RD_Intensity IS in `ratio_cols` and inf values ARE cleaned to NaN.
3. **Update line-number references** or add a disclaimer that line numbers are approximate.
4. **Fix output file count** in Section 8 to accurately reflect that a full run produces 16 files (8 regression result texts + 8 other outputs), not 9.
5. **Strengthen multicollinearity discussion** in Section 11c to explicitly note that Manager measures include CEO, creating near-mechanical collinearity.

---

## N. Assessment of First-Layer Audit Quality

**Overall grade: B+**

The first-layer audit is thorough and well-structured. It correctly identifies the major econometric concerns (unbounded PayoutRatio, Kronmal overlap, mass point at zero) and documents the full construction chain with impressive detail. The verification log is comprehensive and all 25 verification claims are substantively correct.

However, the audit contains one material formula error (TobinsQ), one factual error (RD_Intensity inf cleanup), and pervasive line-number drift. These issues are individually minor to moderate but collectively suggest the audit was written against a slightly different version of the codebase and was not fully re-verified against the current state.

The identification and inference assessment (Section 11) is strong, particularly the Kronmal (1993) discussion and the mass-point-at-zero concern. The design decisions section is well-justified with literature citations.

---

## O. Materiality Assessment for Thesis Defense

| Concern | Impact on H12 conclusions | Remediation urgency |
|---------|--------------------------|---------------------|
| Unbounded PayoutRatio (L1) | Could affect coefficient magnitudes if extreme values drive results | **HIGH** -- robustness check with censoring at 1.0 recommended |
| ROA-PayoutRatio Kronmal overlap (L2) | May bias ROA coefficient negative, potentially inflating uncertainty IV significance | **MEDIUM** -- sensitivity analysis dropping ROA recommended |
| Mass point at zero (L3) | OLS on mixed continuous/mass-point DV is econometrically suboptimal | **MEDIUM** -- Tobit or two-part model as robustness |
| CEO-Manager collinearity (RT-D3) | Individual IV coefficients may be unreliable | **MEDIUM** -- report VIFs or run separate IV pairs |
| TobinsQ formula error in audit (RT-C1) | No impact on code (code is correct), but audit doc is misleading | **LOW** -- fix audit doc |

---

## P. Sign-Off

This second-layer red-team audit has independently verified the H12 first-layer provenance document against the current codebase. The code implementation is sound and the major econometric concerns identified in the first layer are legitimate and well-characterized. The errors found (TobinsQ formula, RD_Intensity claim, line drift, output count) are documentation errors that do not affect the actual regression pipeline.

**The H12 suite code is fit for purpose, subject to the robustness recommendations in Sections 11 and 12 of the first-layer audit and the additional concerns raised in this document.**

Auditor: Second-layer red-team (automated)
Date: 2026-03-21
