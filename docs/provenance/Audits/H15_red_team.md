# H15 Share Repurchase -- Second-Layer Red-Team Audit

**Generated:** 2026-03-18
**Auditor context:** Fresh (no prior involvement in H15 development or first-layer audit)
**Suite ID:** H15
**Estimation method:** Linear Probability Model (PanelOLS)
**DV:** REPO_callqtr (binary: cshopq > 0 in call quarter)

---

## A. Red-Team Bottom Line

The first-layer audit (H15.md) is **substantially accurate** but contains one **factually incorrect variable formula** (TobinsQ), has **stale results from a prior 6-IV specification** that are presented as current, and **omits several material econometric concerns** specific to the LPM choice with a 70.5% base-rate binary DV. The implementation itself is well-constructed with proper safeguards (merge deduplication, quarter-lead validation, year restriction for cshopq availability). However, the audit document fails to discuss LPM-specific diagnostics (predicted probabilities outside [0,1], heteroskedasticity inherent in binary DV with OLS, Horrace-Oaxaca bounds), and does not flag the non-unique (gvkey, fyearq_int) panel index that allows multiple calls per firm-year cell. No critical implementation bugs were found. The suite is at **CONDITIONAL PASS** readiness -- the TobinsQ formula claim needs correction, results need a fresh run, and the thesis text must address LPM limitations.

**Verdict: CONDITIONAL PASS -- fixable issues, no fatal implementation flaws.**

---

## B. Scope and Objects Audited

| Object | Path | Audited |
|--------|------|---------|
| First-layer audit | `docs/provenance/H15.md` | Full |
| Econometric runner | `src/f1d/econometric/run_h15_repurchase.py` | Full (761 lines) |
| Panel builder | `src/f1d/variables/build_h15_repurchase_panel.py` | Full (457 lines) |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` | Targeted (REPO, TobinsQ, BookLev, ROA, CapexAt, DividendPayer, OCF_Volatility, CashHoldings, winsorization) |
| RepurchaseIndicatorBuilder | `src/f1d/shared/variables/repurchase_indicator.py` | Full |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` | Full |
| Variables __init__ | `src/f1d/shared/variables/__init__.py` | Targeted |
| BookLevBuilder | `src/f1d/shared/variables/book_lev.py` | Full |
| LevBuilder | `src/f1d/shared/variables/lev.py` | Full |

---

## C. Audit-of-Audit Scorecard

| Dimension | Grade | Notes |
|-----------|-------|-------|
| Factual accuracy | B- | TobinsQ formula is wrong; results are stale (6-IV, not 4-IV) |
| Completeness | C+ | Missing LPM-specific diagnostics, no discussion of non-unique panel index |
| Variable dictionary accuracy | B | 7/8 controls correctly described; TobinsQ formula error |
| Econometric rigor | C | LPM choice justified but no discussion of heteroskedasticity, predicted probabilities, or Horrace-Oaxaca |
| Reproducibility | B+ | Year restriction enforced, merge guards present, attrition tracked |
| Sample accounting | B+ | Base rate reported, year restriction justified with data evidence |
| Identification discussion | C+ | No discussion of endogeneity, reverse causality, or omitted variables |
| Audit craft | B- | Well-structured but rubber-stamps several aspects without verification |

---

## D. Claim Verification Matrix

| # | Claim (from H15.md) | Verdict | Evidence |
|---|---------------------|---------|----------|
| D1 | "DV: REPO_callqtr = 1 if cshopq > 0 in the fiscal quarter containing the call" | **VERIFIED FACT** | `build_h15_repurchase_panel.py` lines 251-254: `np.where(comp["cshopq"].notna() & (comp["cshopq"] > 0), 1.0, ...)` |
| D2 | "cshopq = Total Shares Repurchased (Compustat quarterly, NOT YTD cumulative)" | **VERIFIED FACT** | Compustat documentation confirms cshopq is quarterly (unlike capxy/dvy). Engine comment at line 1143 confirms. |
| D3 | "merge_asof(direction='backward') matches calls to the reporting quarter" | **VERIFIED FACT** | `_compustat_engine.py` line 1287-1294: `pd.merge_asof(..., direction="backward")` |
| D4 | "Panel builder leads REPO by one fiscal quarter to get the call quarter" | **VERIFIED FACT** | `build_h15_repurchase_panel.py` lines 271-272: `next_fqtr = fqtr_int % 4 + 1`, `next_fyearq = fyearq_int + (fqtr_int == 4)` |
| D5 | "Quarter continuity validated: next_fqtr = fqtr % 4 + 1, with fiscal year rollover at Q4->Q1" | **VERIFIED FACT** | Arithmetic verified: 1->2, 2->3, 3->4, 4->1; fyearq incremented when fqtr==4 |
| D6 | "TobinsQ = (atq + cshoq*prccq - ceqq) / atq" | **VERIFIED ERROR** | Actual code at `_compustat_engine.py` lines 1067-1077: `TobinsQ = (cshoq*prccq + dlcq + dlttq) / atq`. These are NOT algebraically equivalent: `atq - ceqq` includes all non-equity liabilities (AP, accruals, deferred revenue, etc.), while `dlcq + dlttq` is interest-bearing debt only. |
| D7 | "BookLev = (dlcq + dlttq) / atq" | **VERIFIED FACT** | `_compustat_engine.py` line 1039: `comp["BookLev"] = (comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]` |
| D8 | "ROA = Annual income / average assets" | **VERIFIED FACT** | Lines 1050-1060: `iby_annual / ((atq_annual + atq_annual_lag1) / 2)` |
| D9 | "CapexAt = Q4 capxy / lagged assets" | **VERIFIED FACT** | Lines 1079-1084: `capxy_annual / atq_annual_lag1` |
| D10 | "DividendPayer = dvy > 0" | **VERIFIED FACT** | Lines 1089-1092: Q4 annual dvy, `fillna(0) > 0` |
| D11 | "OCF_Volatility = Rolling 5yr std of oancfy/lagged_atq" | **VERIFIED FACT** | `_compute_ocf_volatility()` lines 307-356: rolling 1826D, min_periods=3, oancfy/atq_lag |
| D12 | "Size = ln(total assets)" | **VERIFIED FACT** | Line 1034: `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` |
| D13 | "CashHoldings = cheq / atq" | **VERIFIED FACT** | Line 1066: `comp["CashHoldings"] = comp["cheq"] / comp["atq"]` |
| D14 | "Industry FE: Absorbed via PanelOLS constructor other_effects" | **VERIFIED FACT** | Runner lines 290-298: `other_effects=industry_data, entity_effects=False, time_effects=True` |
| D15 | "Firm FE: EntityEffects + TimeEffects via from_formula" | **VERIFIED FACT** | Runner lines 301-304 |
| D16 | "Standard Errors: Firm-clustered, heteroscedasticity-robust" | **VERIFIED FACT** | Lines 299, 304: `cov_type="clustered", cluster_entity=True` |
| D17 | "Year Range: 2004-2018 (cshopq unavailable in 2002-2003)" | **VERIFIED FACT** | Panel builder line 335: `year_start = max(config.data.year_start, 2004)` |
| D18 | "Min calls/firm: 5" | **VERIFIED FACT** | Runner line 114: `MIN_CALLS_PER_FIRM = 5` |
| D19 | "4 simultaneous IVs" | **VERIFIED FACT** | Runner lines 82-86: `KEY_IVS = [CEO_QA, CEO_Pres, Manager_QA, Manager_Pres]` |
| D20 | "8 base controls" | **VERIFIED FACT** | Runner lines 89-98: 8 controls listed |
| D21 | "Extended = Base + 4" | **VERIFIED FACT** | Runner lines 100-105: SalesGrowth, RD_Intensity, CashFlow, Volatility |
| D22 | "Excluded: Finance (FF12=11), Utility (FF12=8)" | **VERIFIED FACT** | Runner line 206: `~panel["ff12_code"].isin([8, 11])` |
| D23 | "Base rate: 70.5% of calls with REPO data have REPO_callqtr=1" | **UNVERIFIED** | Cannot verify without running the code; value from a prior run |
| D24 | "Results are from pre-4IV run (6 IVs including CEO/Manager Clarity Residuals, N~27K)" | **VERIFIED FACT** | Audit explicitly states results are stale: "A fresh run is needed" |
| D25 | "REPO not in {BookLev, CashHoldings, CapexAt}, so all three are controls" | **VERIFIED FACT** | REPO is binary indicator from cshopq; BookLev uses dlcq/dlttq/atq; CashHoldings uses cheq/atq; CapexAt uses capxy/atq_lag. No overlap. |
| D26 | "P-values: Raw model.pvalues (two-tailed)" | **VERIFIED FACT** | Runner line 328: `p_two = float(model.pvalues.get(iv, np.nan))` |
| D27 | "drop_absorbed=True" | **VERIFIED FACT** | Lines 296, 303 |
| D28 | "Panel index: gvkey (entity) + fyearq_int (fiscal year)" | **VERIFIED FACT** | Runner line 283: `df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])` |
| D29 | "Added REPO and fqtr to COMPUSTAT_COLS" | **VERIFIED FACT** | Engine lines 138-139 |
| D30 | "REPO and fqtr added to skip_winsorize set" | **VERIFIED FACT** | Engine lines 1191-1192 |
| D31 | "RepurchaseIndicatorBuilder follows DividendPayer pattern" | **VERIFIED FACT** | `repurchase_indicator.py`: uses same engine.match_to_manifest pattern |
| D32 | "77% of firms have within-firm variation in REPO" | **UNVERIFIED** | Cannot verify without running; from a prior run |

---

## E. Unsupported/Overstated Claims

| # | Claim | Issue | Severity |
|---|-------|-------|----------|
| E1 | "TobinsQ = (atq + cshoq*prccq - ceqq) / atq" (audit Section A5) | **Formula is wrong.** Actual code computes `(cshoq*prccq + dlcq + dlttq) / atq`. The difference is material: `atq - ceqq` captures ALL non-equity liabilities (operating + financial), while `dlcq + dlttq` is financial debt only. For a typical S&P 500 firm, operating liabilities (AP, accruals, deferred revenue) are 15-30% of total assets, so the discrepancy is economically large. | **MAJOR** |
| E2 | "Standard Errors: Firm-clustered, heteroscedasticity-robust" | Partially overstated. While clustered SEs are heteroskedasticity-consistent (HC1 by default in linearmodels), the audit does not note that with a binary DV, heteroskedasticity is **guaranteed** (Var(e|X) = p(1-p)), making this a minimum requirement, not a robustness feature. The audit implies this is sufficient without discussing LPM-specific limitations. | **MINOR** |
| E3 | Results section presents 6 IVs including "CEO Clarity Residual" and "Manager Clarity Residual" | While the audit does note results are stale, the table structure implies 6 IVs are the current design. The actual code has 4 IVs only. A reader could misunderstand the current specification. | **MINOR** |

---

## F. False Positives

No false positives identified in the first-layer audit. The audit does not raise any issues that are incorrect.

---

## G. Missed Issues

| # | Issue | Severity | Category |
|---|-------|----------|----------|
| G1 | **Non-unique panel index.** The panel is indexed by (gvkey, fyearq_int), but the data is call-level with potentially 4+ calls per firm per fiscal year. PanelOLS accepts this but the econometric interpretation differs from standard two-way FE: "within-R2" measures variation within entity-time cells, not the standard panel within-estimator. The audit does not discuss this at all. | **MAJOR** | Econometric |
| G2 | **No predicted probability diagnostics.** LPM produces predicted probabilities outside [0,1]. With a 70.5% base rate, the probability mass is concentrated near the upper bound, increasing the likelihood of predictions > 1. No diagnostic is computed or reported (e.g., fraction of fitted values outside [0,1]). Horrace and Oaxaca (2006) show that if >5% of predictions are outside [0,1], LPM coefficient estimates may be inconsistent. | **MAJOR** | Econometric |
| G3 | **No logit/probit robustness check.** The audit justifies LPM over logit/probit by citing the incidental parameters problem with firm FE. This is correct for short panels (T small), but with T up to 15 years (2004-2018) and the industry FE models (Cols 1, 3) having no incidental parameters issue, a logit robustness check for the industry FE specifications is straightforward and would strengthen the thesis. | **MODERATE** | Robustness |
| G4 | **No marginal effects comparison.** LPM coefficients are directly interpretable as marginal effects, but only at the mean. The audit claims "Coefficients represent marginal effects on the probability of share repurchase" (LaTeX table note, runner line 467) without noting this is an average marginal effect, not a marginal effect at specific covariate values. | **MINOR** | Interpretation |
| G5 | **check_rank=False for industry FE but not for firm FE.** Runner line 297 sets `check_rank=False` for industry FE models, but the firm FE models (from_formula, line 303) do not set this parameter. This inconsistency is not discussed. If check_rank is needed for industry FE, why not for firm FE? | **MINOR** | Implementation |
| G6 | **RepurchaseIndicatorBuilder loads REPO from engine (reporting quarter) but it is never used as DV.** The panel builder at line 222 checks `if "REPO" not in panel.columns` as a guard, but then constructs REPO_callqtr independently from raw Compustat data. The engine's REPO column is a wasted computation. This is not a bug but an inefficiency that the audit should document for clarity. | **MINOR** | Design |
| G7 | **No discussion of Duong et al. (2025) methodology fidelity.** The audit cites Duong, Do, and Do (2025) for the REPO construction but does not detail which of their methods (they propose 5 methods) is implemented. The code uses their simplest method (quarterly cshopq > 0). The audit should note this and explain why the simpler method is sufficient. | **MODERATE** | Provenance |
| G8 | **No endogeneity discussion.** Repurchase decisions and managerial speech uncertainty may be jointly determined by unobservable factors (e.g., board pressure, insider information). The audit does not discuss this or mention potential instruments/identification strategies. | **MODERATE** | Identification |
| G9 | **70.5% base rate implications not discussed.** With a DV that is 1 in 70.5% of observations, the unconditional probability is far from 0.5. This means (a) the binary outcome is imbalanced, (b) within-firm variation in the DV is limited for firms that always repurchase, and (c) R-squared of 2% is partially due to the DV being near its ceiling. The audit notes the base rate but does not discuss its econometric implications. | **MODERATE** | Econometric |
| G10 | **No collinearity diagnostics.** Four uncertainty measures enter simultaneously (CEO QA, CEO Pres, Manager QA, Manager Pres). These are likely highly correlated (especially Manager vs CEO for the same section). No VIF or condition number is reported. With null results across all IVs, multicollinearity could be masking individual effects. | **MODERATE** | Econometric |

---

## H. Severity Recalibration

| Issue | First-Layer Severity | Red-Team Severity | Rationale |
|-------|---------------------|-------------------|-----------|
| TobinsQ formula error (E1) | Not flagged | **MAJOR** | Formula is factually wrong; affects thesis documentation. The regression itself is unaffected (code is correct), but the provenance document misstates the formula. |
| Non-unique panel index (G1) | Not flagged | **MAJOR** | Affects econometric interpretation. Not a bug per se (PanelOLS handles it), but thesis committee will ask. |
| No predicted probability diagnostics (G2) | Not flagged | **MAJOR** | Standard LPM requirement per Horrace-Oaxaca (2006). Must be reported even if results are null. |
| No logit/probit robustness (G3) | Not flagged | **MODERATE** | Industry FE models could trivially add logit; null results reduce urgency but committee will expect. |
| LPM justification (design decision E3 in H15.md) | Adequate | Adequate | The incidental parameters argument is correctly stated for firm FE specs. |
| Stale results (E3) | Noted by audit | **MODERATE** | Audit correctly flags this, but the results table structure is misleading. |

---

## I. Completeness Gaps

| Gap | Description | Impact |
|-----|-------------|--------|
| I1 | No LPM diagnostic section (predicted probabilities, Horrace-Oaxaca bounds) | Committee will ask for this |
| I2 | No collinearity diagnostics (VIF/condition number for 4 correlated IVs) | Could explain null results |
| I3 | No discussion of alternative DV definitions (dollar-based repurchase intensity, repurchase yield) | Limits robustness assessment |
| I4 | No discussion of quarterly vs annual repurchase aggregation | Duong et al. discuss this; thesis should too |
| I5 | No Hausman test or motivation for FE choice beyond incidental parameters | Standard panel econometrics requirement |
| I6 | No economic magnitude discussion | Even with null results, coefficient bounds are informative |
| I7 | No placebo/falsification test | E.g., does uncertainty predict repurchases 2+ quarters ahead? |

---

## J. Reproducibility Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Data inputs specified | PASS | Compustat quarterly parquet, master manifest |
| Year restriction enforced in code | PASS | `max(config.data.year_start, 2004)` at line 335 |
| Merge guards present | PASS | Deduplication checks, row-count validation after every merge |
| Attrition table generated | PASS | `generate_attrition_table()` at runner line 703 |
| Manifest generated | PASS | `generate_manifest()` at runner line 713 |
| Deterministic output paths | PASS | Timestamped output directories |
| Random seed needed | N/A | No random operations |
| Fresh run needed | **YES** | Current results are from a 6-IV specification; current code uses 4 IVs |

---

## K. Econometric Meta-Audit

### K1. LPM Appropriateness

The LPM (OLS with binary DV) is a defensible choice when:
- Fixed effects create incidental parameters problems in nonlinear models (firm FE in Cols 2, 4)
- The primary interest is average marginal effects rather than individual predictions
- Clustered SEs correct for heteroskedasticity

However, the following LPM-specific concerns are not addressed:

1. **Heteroskedasticity is guaranteed.** With Bernoulli DV, Var(e|X) = p(X)(1-p(X)). Clustered SEs handle this, but the audit should explicitly state this.

2. **Predicted probabilities outside [0,1].** With a 70.5% base rate, predictions near 1.0 are common, and some will exceed 1.0. The Horrace-Oaxaca (2006) bound should be checked: if >5% of fitted values are outside [0,1], coefficient estimates may be inconsistent.

3. **Industry FE models (Cols 1, 3) have no incidental parameters problem.** The justification for LPM over logit/probit applies only to firm FE models. The industry FE models could be estimated via logit as a robustness check at near-zero cost.

### K2. Panel Structure

The panel index is (gvkey, fyearq_int), but the unit of observation is the individual earnings call. A firm with 4 quarterly calls in a fiscal year has 4 rows with the same (gvkey, fyearq_int). PanelOLS treats this as a panel with repeated observations per cell. The "within-R2" of 2% should be interpreted as within-cell variation, not the standard panel within-estimator R2.

### K3. Standard Errors

Firm-clustered SEs with `cluster_entity=True` are appropriate. linearmodels clusters on the entity dimension of the multi-index (gvkey). This is correct for arbitrary within-firm serial correlation.

### K4. Identification

The identifying variation comes from within-firm, within-fiscal-year variation in quarterly uncertainty measures predicting quarterly repurchase decisions, after absorbing firm (or industry) and fiscal year fixed effects. This is a valid identification strategy if:
- Uncertainty is measured before or contemporaneous with the repurchase decision (call quarter alignment addresses this)
- No reverse causality (firms adjusting speech because they plan to repurchase)
- No omitted time-varying confounders at the quarterly level

The audit does not discuss any of these.

### K5. Multiple Comparisons

4 IVs x 4 specifications = 16 tests. All null. No multiple comparison correction is needed when all results are null (corrections only matter for false positive control).

---

## L. Audit-Safety Assessment

| Risk | Status | Notes |
|------|--------|-------|
| Implementation matches documentation | PARTIAL | TobinsQ formula mismatch. All other variables verified. |
| Results match current specification | NO | Results are from 6-IV run; code currently has 4 IVs |
| Sample construction is reproducible | YES | Year restriction, merge guards, attrition logging all present |
| No silent data loss | YES | Every merge has before/after row count checks |
| No incorrect inference | LOW RISK | Results are null across all specifications; risk of false positive is zero |
| Audit covers all code paths | PARTIAL | Audit does not discuss `check_rank=False` inconsistency or REPO column redundancy |

---

## M. Master Issue Register

| ID | Severity | Category | Description | Source | Fix Required |
|----|----------|----------|-------------|--------|--------------|
| M1 | **MAJOR** | Documentation | TobinsQ formula in H15.md is wrong: states `(atq + cshoq*prccq - ceqq) / atq`, actual code uses `(cshoq*prccq + dlcq + dlttq) / atq` | D6, E1 | Correct formula in H15.md and all other provenance docs using this formula |
| M2 | **MAJOR** | Econometric | Non-unique (gvkey, fyearq_int) panel index with call-level data not discussed | G1 | Add discussion in thesis text explaining multi-call-per-cell design |
| M3 | **MAJOR** | Econometric | No predicted probability diagnostic for LPM | G2 | Add code to compute fraction of fitted values outside [0,1]; report in diagnostic output |
| M4 | **MODERATE** | Robustness | No logit/probit robustness check for industry FE specifications | G3 | Add logit for Cols 1/3 as robustness; report in appendix |
| M5 | **MODERATE** | Results | Stale results from 6-IV specification; current code uses 4 IVs | E3 | Run fresh with 4-IV specification; update results in H15.md |
| M6 | **MODERATE** | Provenance | No discussion of which Duong et al. (2025) method is implemented | G7 | Add explicit statement that Method 1 (quarterly cshopq) is used |
| M7 | **MODERATE** | Identification | No endogeneity discussion | G8 | Add paragraph in thesis text |
| M8 | **MODERATE** | Econometric | No collinearity diagnostics for 4 correlated IVs | G10 | Add VIF computation to runner; report in diagnostics |
| M9 | **MODERATE** | Econometric | 70.5% base rate implications not discussed | G9 | Add discussion of within-firm DV variation |
| M10 | **MINOR** | Implementation | check_rank=False inconsistency between industry and firm FE models | G5 | Harmonize: either set for both or neither |
| M11 | **MINOR** | Design | RepurchaseIndicatorBuilder loads engine REPO column but it is never used as DV | G6 | Document or remove the REPO check guard |
| M12 | **MINOR** | Interpretation | LPM marginal effects are average, not at-the-mean | G4 | Clarify in LaTeX table note |

---

## N. What Committee Would Not Know

Reading only the first-layer audit (H15.md), a thesis committee would NOT know:

1. **The TobinsQ formula is misstated.** The committee would believe TobinsQ = (atq + cshoq*prccq - ceqq)/atq (a common approximation using the accounting identity), when the code actually uses (mktcap + interest-bearing debt)/atq (a different standard approximation). Both are valid Tobin's Q proxies, but they are NOT the same formula.

2. **The panel has multiple observations per (firm, year) cell.** The committee would assume standard two-way FE panel structure with one observation per (entity, time). The actual structure has 1-4 calls per cell, which changes the interpretation of "within" variation.

3. **No LPM diagnostics have been computed.** The committee would not know whether predicted probabilities exceed [0,1], which is the primary econometric concern with LPM.

4. **The results are stale.** While the audit notes this, the table layout (6 IVs) contradicts the stated 4-IV design, creating confusion about what was actually estimated.

5. **No robustness to logit has been checked.** The committee would not know if the null results are robust to the functional form assumption.

6. **Which Duong et al. (2025) method is used.** Duong et al. propose 5 methods; the simplest is implemented. Committee members familiar with the paper may question whether the more precise methods would yield different results.

---

## O. Priority Fixes

### Tier 1 (Required before thesis submission)

1. **Fix TobinsQ formula in H15.md** (and cross-check all other provenance docs). Change to: `TobinsQ = (cshoq*prccq + dlcq + dlttq) / atq` (market cap + book debt / total assets).

2. **Run fresh 4-IV specification** and update results table in H15.md. Remove the 6-IV results and clarity residual rows.

3. **Add predicted probability diagnostics.** Compute and report: (a) fraction of fitted values < 0, (b) fraction > 1, (c) mean and range of fitted values. Add to `model_diagnostics.csv`.

4. **Add paragraph to thesis text** explaining (a) call-level panel with fiscal year FE, (b) multiple calls per (firm, year) cell, (c) LPM justification and limitations.

### Tier 2 (Strongly recommended)

5. **Add logit robustness check** for Cols 1/3 (industry FE). Report in appendix or footnote.

6. **Add VIF computation** for the 4 IVs. Include in diagnostic output.

7. **Add Duong et al. method identification** to the provenance document.

### Tier 3 (Nice to have)

8. **Harmonize check_rank parameter** across industry and firm FE models.

9. **Document or simplify** the REPO column redundancy between engine and panel builder.

10. **Add placebo test** (uncertainty -> REPO 2+ quarters ahead) to demonstrate temporal specificity.

---

## P. Final Readiness Statement

**H15 is at CONDITIONAL PASS readiness.**

The implementation is mechanically sound: the DV is correctly constructed from quarterly Compustat data with proper quarter-lead logic, merge guards prevent row multiplication, year restrictions are enforced for cshopq availability, and the estimation uses appropriate firm-clustered standard errors. The null results across all 16 IV-specification combinations are informative and internally consistent.

However, the first-layer audit has a factually incorrect TobinsQ formula (MAJOR), stale results from a prior specification (MODERATE), and fails to address standard LPM diagnostic requirements (MAJOR). The non-unique panel index is a legitimate design choice but must be discussed in the thesis text (MAJOR for documentation, not for implementation).

None of these issues require re-architecting the suite. All are fixable with (1) a documentation correction, (2) a fresh run, (3) adding ~20 lines of diagnostic code, and (4) a few paragraphs of thesis text discussing LPM limitations and the call-level panel structure.

**Blocking items for thesis submission:** M1 (TobinsQ formula), M3 (LPM diagnostics), M5 (fresh run).
**Non-blocking but committee will ask:** M2 (panel structure), M4 (logit robustness), M8 (VIF).
