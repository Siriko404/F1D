# H12 Payout Ratio -- Second-Layer Red-Team Audit

**Generated:** 2026-03-18
**Auditor context:** Fresh-context, adversarial, doctoral-referee standard
**Suite ID:** H12
**First-layer audit:** `docs/provenance/H12.md`
**Runner:** `src/f1d/econometric/run_h12_div_intensity.py`
**Panel builder:** `src/f1d/variables/build_h12_div_intensity_panel.py`
**PayoutRatio engine:** `src/f1d/shared/variables/_compustat_engine.py` (lines 1103-1112)

---

## A. First-Layer Audit Claim Verification

| # | Audit Claim | Code Evidence | Verdict |
|---|-------------|---------------|---------|
| A1 | "PayoutRatio = dvy / iby when iby > 0; NaN when iby <= 0" | `_compustat_engine.py` L1108-1112: `np.where(iby_for_payout > 0, dvy_for_payout / iby_for_payout, np.nan)` | **VERIFIED FACT** |
| A2 | "Missing dvy with iby > 0 treated as PayoutRatio = 0" | L1106: `dvy_for_payout = pd.Series(dvy_annual, index=comp.index).fillna(0)` -- NaN dvy becomes 0 before division | **VERIFIED FACT** |
| A3 | "dvy = annual common dividends, Q4 cumulative from Compustat" | L1089: `dvy_annual = _compute_annual_q4_variable(comp, "dvy", "_dvy_annual")` -- Q4-only join back pattern | **VERIFIED FACT** |
| A4 | "iby = income before extraordinary items, annual, Q4 cumulative" | L1057: `iby_annual = _compute_annual_q4_variable(comp, "iby", "_iby_annual")` | **VERIFIED FACT** |
| A5 | "4 simultaneous IVs" | `run_h12_div_intensity.py` L90-95: `KEY_IVS` list of 4 variables; L289: `exog = KEY_IVS + controls` | **VERIFIED FACT** |
| A6 | "8 model specifications" | L116-125: `MODEL_SPECS` list with 8 dicts, cols 1-8 | **VERIFIED FACT** |
| A7 | "Industry FE: Absorbed via constructor other_effects (FF12 dummies, not C() formula)" | L306-314: `PanelOLS(... other_effects=industry_data ...)` with `entity_effects=False` | **VERIFIED FACT** |
| A8 | "Firm FE: EntityEffects + TimeEffects via from_formula" | L318-320: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` | **VERIFIED FACT** |
| A9 | "Firm-clustered SEs" | L315 and L321: `.fit(cov_type="clustered", cluster_entity=True)` | **VERIFIED FACT** |
| A10 | "One-tailed test: beta < 0" | L349-351: `p_one = p_two / 2 if beta < 0 else 1 - p_two / 2` | **VERIFIED FACT** |
| A11 | "Time FE: fyearq_int (fiscal year)" | L298: `df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])` -- MultiIndex with fyearq_int as time dimension | **VERIFIED FACT** |
| A12 | "Main sample only: FF12 codes 1-7, 9-10, 12" | L212-215: `panel[~panel["ff12_code"].isin([8, 11])]` -- excludes FF12=8 (Utility) and FF12=11 (Finance) | **VERIFIED FACT** |
| A13 | "Base Controls (7): Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility" | L99-107: `BASE_CONTROLS` matches exactly | **VERIFIED FACT** |
| A14 | "Extended Controls: Base + SalesGrowth, RD_Intensity, CashFlow, Volatility" | L109-114: `EXTENDED_CONTROLS = BASE_CONTROLS + [...]` matches exactly | **VERIFIED FACT** |
| A15 | "DividendPayer is NOT a control" | L98 comment: `DividendPayer is NOT a control (endogenous with DV)` -- not in BASE_CONTROLS or EXTENDED_CONTROLS | **VERIFIED FACT** |
| A16 | "PayoutRatio_lead = PayoutRatio shifted forward one fiscal year" | `build_h12_div_intensity_panel.py` L176-195: `create_lead_payout_ratio()` shifts by -1 within gvkey, NaN for non-consecutive years | **VERIFIED FACT** |
| A17 | "ROA shares iby with PayoutRatio denominator -- mechanical linkage documented" | Engine L1057-1060: ROA = iby_annual / avg_assets; L1108: PayoutRatio = dvy / iby_annual. Same iby_annual variable. Audit A5 table notes this. | **VERIFIED FACT** |
| A18 | "Aggregation: arithmetic mean across all quarterly calls within fiscal year" | Panel builder L157-158: `df.groupby(["gvkey", "fyearq"])[existing_ivs].mean()` | **VERIFIED FACT** |
| A19 | "No MIN_CALLS_PER_FIRM filter" | Runner L254: comment "No MIN_CALLS_PER_FIRM filter (include all firms)" -- no filter code present | **VERIFIED FACT** |
| A20 | "Winsorized at 1%/99% by year at engine level" | Engine L1194-1201: `_winsorize_by_year` applied to all COMPUSTAT_COLS except skip set; PayoutRatio is in COMPUSTAT_COLS and not in skip set | **VERIFIED FACT** |

---

## B. Verified Errors in First-Layer Audit

| # | Error | Details | Severity |
|---|-------|---------|----------|
| B1 | Output list incomplete | Audit Section D lists 9 output files including `sample_attrition.tex` (item 8), but the runner at L756 calls `generate_attrition_table(attrition_stages, out_dir, "H12 Payout Ratio")` which produces both `.csv` and `.tex`. The doc correctly lists both. However, the docstring in the runner (L48-57) lists only 8 outputs and omits `sample_attrition.tex` and `sample_attrition.csv`. This is a docstring-vs-code mismatch, not an audit error per se. | MINOR |
| B2 | No verified errors in substance | All 20 factual claims checked against code are accurate. | N/A |

---

## C. Verified Missed Issues in First-Layer Audit

| # | Issue | Details | Severity |
|---|-------|---------|----------|
| C1 | **PayoutRatio has no upper bound or economic censoring** | PayoutRatio = dvy / iby can exceed 1.0 (and theoretically be very large when iby is positive but small). Attig et al. (2013) typically censor/bound payout ratios at 1.0 or 100% because values exceeding 100% represent firms paying out more than their earnings (drawing on reserves, borrowing for dividends). The implementation relies solely on winsorization at 1%/99% by year (engine level), but if many firms have PR > 1 in a given year, the 99th percentile could itself be well above 1.0. The first-layer audit does not flag or discuss this at all. **This is the single most material econometric concern for H12.** A referee would ask: what is the empirical distribution of PayoutRatio? What fraction exceeds 1.0? Is OLS on an unbounded DV with a natural lower bound of 0 appropriate? | **MAJOR** |
| C2 | **ROA-PayoutRatio mechanical linkage is acknowledged but not addressed** | The audit notes "shares iby with PayoutRatio denominator -- mechanical linkage documented" but does not discuss the econometric implications. When ROA is high (denominator is large for given iby), PayoutRatio's denominator is also large (same iby). Thus ROA and PayoutRatio share a denominator component (iby), creating a spurious negative correlation: higher iby -> higher ROA AND lower PayoutRatio (for given dvy). This is a textbook denominator problem (Kronmal 1993). A sensitivity analysis dropping ROA or replacing it with a rank-based measure would be prudent. The first audit mentions it but treats documentation as sufficient. | **MODERATE** |
| C3 | **`check_rank=False` in industry FE models** | Runner L313: `check_rank=False` disables rank verification for industry FE PanelOLS models. With `drop_absorbed=True`, collinear variables should be dropped, but skipping the rank check means the user will not be warned if unexpected collinearity exists (e.g., if an industry has too few observations to identify all controls). The audit does not mention this flag. | **MINOR** |
| C4 | **`groupby.last()` is "last non-null", not "last row"** | Panel builder L151-153: `df.groupby(["gvkey", "fyearq"])[existing_financial].last()` -- pandas `groupby.last()` returns the last non-null value per group, not strictly the last row's value. If the last call in a fiscal year has a NaN for a financial variable but an earlier call has a valid value, the earlier value will be silently used. This is typically benign (financial variables are usually identical across calls in the same FY), but the behavior is undocumented and could be surprising. The first audit does not mention this. | **MINOR** |
| C5 | **No intercept explicitly added to industry FE model exog** | Runner L289: `exog = KEY_IVS + controls` -- no constant column. For the industry FE specification (constructor-based, not from_formula), PanelOLS does not add a constant by default. The absorbed `other_effects` (industry) and `time_effects` (year) jointly serve as group means, so an intercept would be collinear and dropped by `drop_absorbed=True` anyway. However, if the number of absorbed effects is insufficient to span the constant, the model would be estimated without an intercept. Practically, with both industry and year effects, the constant IS spanned. Not an error, but undocumented. | **NEGLIGIBLE** |
| C6 | **Summary statistics computed on pre-complete-case sample** | Runner L706-718: `make_summary_stats_table` is called on the full main-sample panel BEFORE complete-case filtering per regression. This means the summary statistics table describes a potentially larger sample than any regression actually uses. A referee might ask why summary stats don't match regression N. The first audit does not mention this discrepancy. | **MINOR** |
| C7 | **Attrition table uses Col 1 N only** | Runner L749-756: attrition stages use `first_meta.get("n_obs", 0)` -- only Col 1's N. Cols 5-8 (PayoutRatio_lead) will have different (smaller) N due to the lead construction dropping non-consecutive years. The attrition table does not separately track lead DV attrition. | **MINOR** |
| C8 | **No discussion of PayoutRatio = 0 mass point** | When dvy is NaN (or truly 0) and iby > 0, PayoutRatio is set to 0. This creates a mass point at zero (non-dividend-paying firms with positive earnings). OLS on a DV with a mass at zero and a long right tail is econometrically questionable. A Tobit model or two-part model (first stage: payer vs non-payer; second stage: conditional payout ratio) would be more appropriate. The first audit mentions "J3: 45.4% zeros in DivIntensity modeled with OLS" as fixed, but the fix (switching to PayoutRatio) may not fully resolve the issue -- the PayoutRatio DV likely still has many zeros. | **MODERATE** |

---

## D. Verified False Positives in First-Layer Audit

| # | Claim | Assessment |
|---|-------|------------|
| D1 | None identified | The first-layer audit does not make claims that are contradicted by the code. All bug-fix claims (J1-J11, calendar-year fix) are consistent with the current implementation. |

---

## E. Referee Judgments (Not Verifiable from Code Alone)

| # | Concern | Assessment |
|---|---------|------------|
| E1 | **Attig et al. citation accuracy** | The audit cites "Attig et al." for PayoutRatio = DVC/IB. Attig, Boubakri, El Ghoul & Guedhami (2013, JFI) do use DVC/IB as the payout ratio. However, their exact handling of negative earnings may differ (some papers exclude firm-years with negative earnings entirely from the sample, others set PR=0 or NaN). The code sets NaN for iby<=0, which is the most conservative approach. Cannot verify without the original paper, but the approach is defensible. |
| E2 | **One-tailed test direction justification** | H12 predicts beta < 0 (higher uncertainty -> lower payout). This is economically reasonable: uncertain managers may retain earnings as precautionary savings rather than committing to dividends. However, one-tailed tests are controversial when the theoretical prediction is not universally accepted. A two-tailed alternative should be reported for robustness. |
| E3 | **Simultaneous-IV interpretation** | With 4 uncertainty IVs entering simultaneously, multicollinearity is a concern. CEO QA and Manager QA likely correlate, as do CEO Pres and Manager Pres. The audit does not report variance inflation factors (VIFs) or IV correlation matrices. |
| E4 | **OLS appropriateness for bounded DV** | PayoutRatio is bounded [0, +inf) with iby>0 condition. With winsorization, it is bounded [p1, p99] per year. OLS does not respect bounds. A fractional response model (Papke and Wooldridge 1996/2008) would be more appropriate if most values are in [0,1]. If a substantial fraction exceeds 1.0, the distribution is problematic for any standard model. |

---

## F. Variable Construction Deep-Dive

### F1. PayoutRatio Construction Chain

| Step | Location | Operation | Verified |
|------|----------|-----------|----------|
| 1 | Engine L1089 | `dvy_annual = _compute_annual_q4_variable(comp, "dvy", "_dvy_annual")` -- extracts Q4 dvy, joins to all quarters via gvkey+fyearq | YES |
| 2 | Engine L1057 | `iby_annual = _compute_annual_q4_variable(comp, "iby", "_iby_annual")` -- same pattern for iby | YES |
| 3 | Engine L1106 | `dvy_for_payout = pd.Series(dvy_annual).fillna(0)` -- NaN dvy -> 0 | YES |
| 4 | Engine L1107 | `iby_for_payout = pd.Series(iby_annual)` -- no fillna, preserves NaN | YES |
| 5 | Engine L1108-1112 | `np.where(iby_for_payout > 0, dvy_for_payout / iby_for_payout, np.nan)` | YES |
| 6 | Engine L1163 | PayoutRatio included in inf->NaN cleanup | YES |
| 7 | Engine L1194-1201 | PayoutRatio winsorized at 1%/99% per fyearq (not in skip_winsorize set) | YES |
| 8 | PayoutRatioBuilder L51 | Builder extracts `["file_name", "PayoutRatio"]` from engine-computed data | YES |
| 9 | Panel builder L151-153 | Financial aggregation via `groupby.last()` -- takes last non-null per firm-year | YES |
| 10 | Panel builder L176-195 | Lead construction: shift(-1) within gvkey, NaN for non-consecutive fyearq | YES |

### F2. PayoutRatio Boundary Analysis

| Condition | Treatment | Concern Level |
|-----------|-----------|---------------|
| iby <= 0 | NaN (excluded from regression) | LOW -- appropriate |
| iby > 0, dvy = NaN | PayoutRatio = 0 | MODERATE -- reasonable assumption but inflates zero mass |
| iby > 0, dvy = 0 | PayoutRatio = 0 | LOW -- correct |
| iby > 0, dvy > iby | PayoutRatio > 1.0 | **HIGH -- no censoring, only winsorization** |
| iby very small but > 0 | PayoutRatio potentially very large | **HIGH -- division by near-zero denominator** |

---

## G. Lead Variable Verification

| Check | Result |
|-------|--------|
| Lead constructed in panel builder (not runner) | YES -- `create_lead_payout_ratio()` in panel builder L176-195 |
| Consecutive-year check | YES -- L188-191: `is_consecutive = (next_fyearq_int - fyearq_int) == 1`; non-consecutive -> NaN |
| Direction correct (t+1, not t-1) | YES -- L184: `shift(-1)` on PayoutRatio within gvkey (next row = future) |
| Lead uses same fyearq as base | YES -- both use fyearq from Compustat |
| Lead survives NaN propagation | YES -- only NaN for non-consecutive years; PayoutRatio NaN in t+1 propagates correctly |

---

## H. Fixed Effects Implementation Verification

| Model | FE Implementation | Correct? | Notes |
|-------|-------------------|----------|-------|
| Industry + FiscalYear (odd cols) | `PanelOLS(... entity_effects=False, time_effects=True, other_effects=ff12_code, check_rank=False, drop_absorbed=True)` | YES | `check_rank=False` is noted concern (C3) |
| Firm + FiscalYear (even cols) | `PanelOLS.from_formula("DV ~ 1 + ... + EntityEffects + TimeEffects", drop_absorbed=True)` | YES | Standard implementation |
| Time index | `fyearq_int` (integer fiscal year) | YES | Correctly aligns with fiscal year DV timing |
| Clustering | `cov_type="clustered", cluster_entity=True` (all models) | YES | Clusters by gvkey (firm) |

---

## I. Sample Accounting

| Stage | Description | Code Location |
|-------|-------------|---------------|
| 1 | Full firm-year panel loaded from Stage 3 parquet | Runner L183-208 |
| 2 | Main sample filter: exclude FF12 = 8 (Utility), 11 (Finance) | Runner L211-216 |
| 3 | DV non-null filter: PayoutRatio not NaN (i.e., iby > 0) | Runner L245-247 |
| 4 | Complete-case filter: all required variables non-null | Runner L250-252 |
| 5 | N < 100 guard: skip model if too few obs | Runner L285-287 |

**Concern:** Stages 3-4 are applied per model specification, so different DVs (PayoutRatio vs PayoutRatio_lead) and different control sets (Base vs Extended) produce different sample sizes. The attrition table only records Col 1's trajectory (C7 above).

---

## J. Merge/Provenance Verification

| Check | Result |
|-------|--------|
| Panel builder merges all variables on `file_name` (1:1) | YES -- L264-269: validates `delta == 0` (no row change) |
| Compustat matching via merge_asof (backward) | YES -- engine `match_to_manifest` L1287-1294 |
| fyearq attached via canonical `attach_fyearq` | YES -- panel builder L274 |
| Industry sample assigned via canonical `assign_industry_sample` | YES -- panel builder L310 |
| Output parquet saved with all columns | YES -- panel builder L326 |

---

## K. One-Tailed P-Value Implementation Verification

| Check | Code | Correct? |
|-------|------|----------|
| Two-tailed p from PanelOLS | L346: `p_two = float(model.pvalues.get(iv, np.nan))` | YES |
| One-tailed conversion when beta < 0 | L351: `p_one = p_two / 2 if beta < 0 else 1 - p_two / 2` | YES |
| Stars applied to one-tailed p | L361: `stars = _sig_stars(p_one)` | YES |
| LaTeX table notes specify one-tailed | L504: `$^{*}p<0.10$, ... (one-tailed; H12: $\beta < 0$)` | YES |

---

## L. LaTeX Table Verification

| Check | Result |
|-------|--------|
| 8 columns generated | YES -- L399: `n_cols = 8` |
| Columns 1-4 = PayoutRatio, 5-8 = PayoutRatio_lead | YES -- L434-437: multicolumn headers |
| Controls indicator row | YES -- L462-466 |
| Industry/Firm/Year FE indicator rows | YES -- L469-479 |
| N and Within-R2 rows | YES -- L483-496 |
| Table notes complete | YES -- includes one-tailed note, clustering, sample, Attig citation, winsorization |

---

## M. Robustness and Identification Concerns

| # | Concern | Severity | Addressed by Audit? |
|---|---------|----------|---------------------|
| M1 | No upper-bound censoring of PayoutRatio | MAJOR | NO |
| M2 | ROA-PayoutRatio denominator overlap (Kronmal 1993) | MODERATE | Mentioned but not addressed |
| M3 | Mass point at PayoutRatio = 0 (OLS vs Tobit/two-part) | MODERATE | NO |
| M4 | No VIF reporting for 4 correlated uncertainty IVs | MINOR | NO |
| M5 | Survivorship bias in lead variable (only consecutive years) | LOW | YES -- documented |
| M6 | No Hausman test for FE vs RE model choice | LOW | Common omission in applied work |
| M7 | No alternative estimator sensitivity (fractional logit, Tobit) | MODERATE | NO |
| M8 | Winsorization applied before lead construction (engine level) | LOW | Appropriate -- ensures lead is from winsorized data |

---

## N. Reproducibility Assessment

| Check | Result |
|-------|--------|
| Deterministic output (no random seeds needed) | YES |
| Panel builder reproducible from manifest + Compustat | YES |
| Runner reproducible from panel parquet | YES |
| Manifest generated with input/output paths | YES -- runner L759-770 |
| Timestamp-based output directories | YES -- runner L661 |
| Dry-run mode available | YES -- runner L799-806, panel builder L454-455 |

---

## O. Audit-Craft Assessment of First-Layer Audit

| Dimension | Grade | Notes |
|-----------|-------|-------|
| Factual accuracy | A | All 20 claims verified against code. Zero errors found. |
| Completeness | B- | Misses critical PayoutRatio bounding/censoring issue (C1), mass-point concern (C8), and ROA mechanical linkage resolution (C2). |
| Variable dictionary | A- | Clear DV and IV definitions. ROA linkage noted but not resolved. |
| Sample accounting | B | Attrition table described but only for Col 1; no discussion of sample variation across specs. |
| Identification discussion | C+ | No discussion of DV distributional properties, estimator appropriateness, or VIF. |
| Bug-fix documentation | A | Clear J1-J11 table with before/after. |
| Redesign rationale | A | Well-justified switch from DivIntensity to PayoutRatio with Attig citation. |

---

## P. Summary Verdict

### First-Layer Audit Quality

The first-layer audit (H12.md) is **factually accurate on every claim checked** (20/20). It provides a thorough description of the implementation, clearly documents the redesign rationale, and correctly catalogs the bug fixes from the old H12. The variable dictionary is clear and the model specifications are precisely documented.

### Material Gaps

The audit's primary weakness is in **distributional and econometric appropriateness** analysis:

1. **MAJOR (C1):** PayoutRatio has no upper-bound censoring. Firms paying dividends exceeding earnings (e.g., from retained earnings or debt) produce PayoutRatio > 1.0. Near-zero iby produces very large PayoutRatio. Winsorization at 99th percentile mitigates extreme outliers but does not address the fundamental problem that OLS on an unbounded ratio with a mass at zero is questionable. A referee would likely require either (a) censoring at 1.0 per Attig et al., (b) a robustness check with censored PayoutRatio, or (c) an alternative estimator (Tobit, fractional logit).

2. **MODERATE (C2, C8):** The ROA-PayoutRatio denominator overlap creates mechanical correlation. Combined with the mass point at zero (non-dividend payers with positive earnings), OLS coefficients may be biased or misleading. These are not novel concerns in the payout literature but should be explicitly acknowledged and addressed.

### Overall Assessment

The first-layer audit is a solid implementation-level document that accurately describes what the code does. It falls short of thesis-referee standard primarily in its silence on the econometric appropriateness of the chosen estimator for the specific DV distribution. A doctoral referee examining H12 would almost certainly ask about PayoutRatio bounding, the zero-mass-point problem, and the ROA denominator overlap -- none of which are adequately addressed in the current audit.

**Recommended actions (priority order):**
1. Investigate empirical distribution of PayoutRatio (what fraction > 1.0? what is the 99th percentile?).
2. Add a robustness specification with PayoutRatio censored at 1.0 (or report sensitivity).
3. Report VIFs for the 4 uncertainty IVs.
4. Acknowledge the ROA-PayoutRatio denominator linkage in the thesis text and consider a sensitivity check dropping ROA.
5. Consider reporting Tobit or two-part model results as robustness.
