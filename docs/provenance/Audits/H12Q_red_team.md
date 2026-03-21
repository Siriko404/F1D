# H12Q -- Second-Layer Red-Team Audit

**Generated:** 2026-03-21
**Suite ID:** H12Q
**First-layer audit:** `docs/provenance/H12Q.md`
**Red-team auditor standard:** Hostile-but-fair replication audit of the audit itself

---

## A. Red-Team Bottom Line

**PASS -- first-layer audit is substantially correct, thorough, and appropriately skeptical.**

The H12Q first-layer audit is one of the strongest provenance documents in this project. It correctly traces the full variable construction chain from raw Compustat fields through to final regression output, identifies the three genuinely important issues (inflated N from call-level estimation, zero mass point, contemporaneous timing), and provides actionable fixes. I independently verified all code-path claims, formula transcriptions, and line references against the actual source. The audit is thesis-committee-ready with minor corrections noted below.

---

## B. Scope and Objects Audited

| Object | Path | Audited by L1 | Independently verified by L2 |
|--------|------|:-:|:-:|
| Runner | `src/f1d/econometric/run_h12q_payout.py` | Yes | Yes |
| Panel builder | `src/f1d/variables/build_h12q_payout_panel.py` | Yes | Yes |
| PayoutRatioQuarterlyBuilder | `src/f1d/shared/variables/payout_ratio_quarterly.py` | Yes | Yes |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` | Yes (relevant sections) | Yes |
| `_winsorize_by_year()` | Engine L445-469 | Yes | Yes |
| `_compute_and_winsorize()` | Engine L1029-1217 | Yes | Yes |
| `match_to_manifest()` | Engine L1282-1316 | Yes | Yes |
| `panel_utils.py` (`attach_fyearq`, `assign_industry_sample`) | `src/f1d/shared/variables/panel_utils.py` | Yes (mentioned) | Yes (spot-checked) |
| LaTeX table generation | Runner L336-451 | Partially (not audited in detail) | Spot-checked |

---

## C. Audit-of-Audit Scorecard

| Dimension | Grade | Comment |
|-----------|-------|---------|
| **Factual accuracy** | A | All formula transcriptions, line references, and code-path descriptions verified correct. |
| **Completeness** | A- | Covers DV construction, leads, controls, FE, SEs, filtering, winsorization. Minor gap: LaTeX table formatting not audited in detail. |
| **Skepticism level** | A | Correctly identifies all three major issues (inflated N, zero mass point, contemporaneous timing). Does not hand-wave. |
| **Actionability** | A | Priority fixes are specific and implementable. |
| **Line-reference accuracy** | A | Spot-checked 15+ line references; all verified correct within +/-2 lines. |
| **Variable-chain completeness** | A | Full chain from raw Compustat through winsorization, merge_asof, builder merge, lead construction, and regression. |

---

## D. Claim Verification Matrix

| Audit claim | Section | Verdict | Evidence |
|-------------|---------|---------|----------|
| PayoutRatio_q = (dvpspq.fillna(0) * cshoq) / ibq | F1 | **CONFIRMED** | Engine L1120-1125: exact match. |
| ibq > 0 guard (strict) | F1 | **CONFIRMED** | Engine L1122: `comp["ibq"] > 0`. |
| dvpspq.fillna(0) for missing dividends | F1 | **CONFIRMED** | Engine L1120: `comp["dvpspq"].fillna(0)`. |
| Inf cleanup on PayoutRatio_q | F1 | **CONFIRMED** | Engine L1177: PayoutRatio_q in ratio_cols; L1185-1186: inf -> NaN. |
| Per-year winsorization 1%/99% | F1 | **CONFIRMED** | PayoutRatio_q in COMPUSTAT_COLS (L124), not in skip_winsorize (L1199-1206). _winsorize_by_year L466-468: 0.01/0.99. |
| Min 10 obs threshold for winsorization | G1 | **CONFIRMED** | _winsorize_by_year L464: `if valid.sum() < min_obs: continue` with min_obs=10. |
| fiscal_qtr_id = fyearq_int * 10 + fqtr_int | F2 | **CONFIRMED** | Builder L226. |
| Lead-qtr consecutive check logic | F2 | **CONFIRMED** | Builder L256-264: expected_next uses np.where on fqtr < 4. |
| Lead-yr self-join lookup | F2 | **CONFIRMED** | Builder L271-277: target = (fyearq_int + 1) * 10 + fqtr_int, dict lookup. |
| 4 IVs enter simultaneously | A | **CONFIRMED** | Runner L73-78 (KEY_IVS), L251 (exog = KEY_IVS + controls). |
| IVs are call-level (no Avg_ prefix) | E2 | **CONFIRMED** | Runner L73-78: raw column names. No aggregation in builder. |
| 12 model specs: 3 DVs x 2 FE x 2 controls | A | **CONFIRMED** | Runner L91-107: 12 entries verified. |
| Lead specs include PayoutRatio_q as extra control | H3 | **CONFIRMED** | Runner L98-106: `"extra_controls": ["PayoutRatio_q"]` for cols 5-12. |
| Panel index is (gvkey, cal_yearqtr) | H1 | **CONFIRMED** | Runner L260: `set_index(["gvkey", "cal_yearqtr"])`. |
| Industry FE via other_effects + time_effects | H1 | **CONFIRMED** | Runner L264-271. |
| Firm FE via EntityEffects + TimeEffects formula | H1 | **CONFIRMED** | Runner L276-278. |
| Firm-clustered SEs | H1 | **CONFIRMED** | Runner L273, L278: `cov_type="clustered", cluster_entity=True`. |
| One-tailed p: p_two/2 if beta < 0, else 1 - p_two/2 | I | **CONFIRMED** | Runner L304-305. |
| MIN_CALLS_PER_FIRM = 5 | E3 | **CONFIRMED** | Runner L89. |
| N guard: skip if < 100 obs | E3 | **CONFIRMED** | Runner L247-249 and L557-559. |
| cal_yearqtr = year * 10 + quarter | H2 | **CONFIRMED** | Builder L295-297. |
| FF12 exclusion: {8, 11} | E3 | **CONFIRMED** | Runner L184. |
| Duplicate file_name guards | I | **CONFIRMED** | Builder L124-126 (manifest), L136-138 (each builder). |
| Row-count preservation assertion | I | **CONFIRMED** | Builder L144-145, L287-288. |
| Size = ln(atq), NaN if atq <= 0 | F4 | **CONFIRMED** | Engine L1036. |
| BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq | F4 | **CONFIRMED** | Engine L1041. |
| CashHoldings = cheq / atq | F4 | **CONFIRMED** | Engine L1068. |
| TobinsQ formula | F4 | **CONFIRMED** | Engine L1075-1079. |
| CapexAt = capxy_Q4_annual / atq_lag1 | F4 | **CONFIRMED** | Engine L1082-1087. |
| CashFlow and SalesGrowth already winsorized in _compute_biddle_residual | F5 | **CONFIRMED** | Engine L667 (SalesGrowth), L694 (CashFlow); both in skip_winsorize L1199-1206. |
| Attrition table records only Col 1 | K4b | **CONFIRMED** | Runner L571-577: uses `first = all_results[0]["meta"]`. |

---

## E. Unsupported Claims

**None found.** All factual claims in the first-layer audit are supported by corresponding code.

---

## F. False Positives

| L1 Issue ID | L1 severity | Red-team assessment | Rationale |
|-------------|-------------|---------------------|-----------|
| L12 | MINOR | **Agree, but slightly overstated.** | PanelOLS with duplicate entity-time entries is non-standard, but `linearmodels` handles it by treating each row as a separate observation within the entity-time cell. The within-transformation averages across the entity dimension, not the entity-time dimension. This is functionally equivalent to OLS with dummy variables. The real concern is L1 (inflated N), which L12 is a symptom of. L12 as a separate issue is partially redundant with L1. |

---

## G. Missed Issues

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| G1 | MINOR | Variable construction | **No upper bound on PayoutRatio_q.** After winsorization at 99th percentile, PayoutRatio_q can still be well above 1.0 (firms paying out more than quarterly income as dividends). The audit correctly documents the 1%/99% winsorization but does not flag that a payout ratio > 1 is economically anomalous and may warrant a cap at 1.0 or further investigation. This is a design choice, not a bug, but should be documented. |
| G2 | MINOR | Reporting | **LaTeX table structure not fully audited.** The LaTeX generation function (Runner L336-451) is non-trivial (3 panels, lagged DV indicator, footnotes). The first-layer audit does not verify that the table correctly maps columns to panels or that the footnotes match the methodology. I spot-checked: the mapping is correct (Panel A = cols 1-4, Panel B = cols 5-8, Panel C = cols 9-12), and the footnote text accurately reflects the methodology. |
| G3 | MINOR | Data provenance | **No explicit tolerance window on merge_asof.** The `match_to_manifest()` call (Engine L1301-1308) uses `direction="backward"` with no `tolerance` parameter. A call could match to a Compustat quarter arbitrarily far in the past if recent quarters are missing. The first-layer audit describes the merge_asof correctly but does not flag the missing tolerance. |

---

## H. Severity Recalibration

| L1 Issue ID | L1 severity | Red-team severity | Rationale |
|-------------|-------------|-------------------|-----------|
| L1 | MAJOR | **MAJOR -- agree** | Inflated N is a genuine concern. The DV is constant within firm-quarter; call-level IVs create pseudo-replication. Firm-clustered SEs partially mitigate but do not fully address this. Firm-quarter collapse robustness is essential. |
| L2 | MAJOR | **MODERATE** | Downgraded. The contemporaneous timing issue is real but is a framing/interpretation problem, not a methodological error. The merge_asof backward direction is standard in the literature (match call to most recent Compustat quarter). The audit correctly identifies the issue and the fix (reframe in thesis text) is appropriate. Since the fix is textual rather than computational, MODERATE is more appropriate. |
| L3 | MAJOR | **MAJOR -- agree** | The 57% zero mass point is a first-order concern for OLS. The audit's recommendation for a Tobit or fractional response robustness check is well-founded. |
| L4 | MODERATE | **MODERATE -- agree** | dvpspq timing (pay date vs. ex-date) is a known Compustat limitation. Documented appropriately. |
| L5 | MODERATE | **MODERATE -- agree** | 48 tests with no correction is standard in finance empirics but should be flagged. |
| L6 | MODERATE | **MODERATE -- agree** | Selection on profitability is inherent in the design (payout ratio undefined for ibq <= 0). |
| L7 | MODERATE | **MODERATE -- agree** | No causal identification strategy. Standard limitation for observational panel studies. |
| L8 | MINOR | **MINOR -- agree** | Placebo test is nice-to-have. |
| L9 | MINOR | **MINOR -- agree** | Subsample analysis is standard robustness. |
| L10 | MINOR | **MINOR -- agree** | fqtr validation is defensive coding, not a bug. Compustat fqtr is reliably in {1,2,3,4}. |
| L11 | MINOR | **MINOR -- agree** | Attrition for all 12 specs is good practice but not essential. |
| L12 | MINOR | **Demote to NOTE** | Redundant with L1. See Section F. |

**Net recalibration:** L2 downgraded from MAJOR to MODERATE. L12 demoted to NOTE. All other severity ratings confirmed.

---

## I. Completeness Gaps

| Gap | Severity | Comment |
|-----|----------|---------|
| LaTeX table audit | MINOR | L1 audit mentions the table exists but does not verify column-to-panel mapping or footnote accuracy. Independently verified: correct. |
| Volatility builder chain | MINOR | The audit says "Via `VolatilityBuilder` (CRSP)" but does not trace the full CRSP engine chain (daily returns -> annualized std). This is acceptable since Volatility is a control, not the DV. |
| `check_rank=False` justification | MINOR | The audit notes `check_rank=False` for industry FE path (Runner L271) but does not explain why. This is a performance optimization for PanelOLS with many absorbed effects. Not a concern but could be documented. |
| `drop_absorbed=True` | MINOR | Mentioned but not critically assessed. This flag silently drops collinear variables. If a control is absorbed by FE, it disappears without warning in the coefficient table. The audit should have noted this risk. |

---

## J. Reproducibility Red-Team

| Check | Result |
|-------|--------|
| Panel builder has `__main__` block | Yes (Builder L386-391) |
| Runner has `__main__` block | Yes (Runner L608-616) |
| Dry-run mode available | Yes (both builder and runner) |
| Timestamp-based output dirs prevent overwrite | Yes (Builder L315, Runner L502) |
| Manifest records input paths | Yes (Runner L581-586) |
| Config-driven year range | Yes (Builder L323-324, `get_config()`) |
| No random seeds or sampling | Confirmed -- fully deterministic |
| Panel path overridable via CLI | Yes (Runner L148, `--panel-path`) |

**Reproducibility verdict:** Fully reproducible. No stochastic components. Output isolation via timestamps is correct.

---

## K. Econometric Meta-Audit

| Concern | L1 assessment | Red-team assessment |
|---------|---------------|---------------------|
| **DV construction** | Correct | **Confirmed correct.** Formula, guard, fillna(0), inf cleanup, winsorization -- all verified. |
| **Lead construction** | Correct | **Confirmed correct.** Consecutive-quarter check is rigorous. Self-join for same-quarter-next-year is sound. |
| **FE specification** | Calendar year-quarter + (Industry or Firm) | **Confirmed correct.** Industry FE via `other_effects`, Firm FE via `EntityEffects`. Time FE via `time_effects=True` (industry) or `TimeEffects` (firm formula). |
| **Standard errors** | Firm-clustered | **Confirmed correct.** `cluster_entity=True` clusters on the first index level (gvkey). |
| **One-tailed test** | Correct | **Confirmed correct.** p_two/2 when beta < 0, 1 - p_two/2 otherwise. |
| **Inflated N** | Flagged as MAJOR (L1) | **Agree.** The DV is firm-quarter level; call-level estimation inflates N without adding DV variation. The first-layer audit correctly identifies this and proposes firm-quarter collapse. |
| **Zero mass point** | Flagged as MAJOR (L3) | **Agree.** OLS with ~57% zeros is suboptimal. Tobit or two-part model would be more appropriate. |
| **Multicollinearity among 4 IVs** | Not explicitly flagged | **Minor gap.** CEO_QA and Manager_QA likely highly correlated (CEO is a subset of Manager). The audit should have noted that multicollinearity among the 4 IVs could inflate standard errors and make individual IV coefficients unstable. This does not invalidate the approach (simultaneous entry is a design choice) but should be acknowledged. |

---

## L. Audit-Safety Assessment

| Risk | Assessment |
|------|-----------|
| **Data leakage** | No leakage detected. merge_asof backward ensures no future Compustat data enters contemporaneous variables. Lead construction uses fiscal quarter shifting with proper consecutive checks. |
| **Survivorship bias** | MIN_CALLS_PER_FIRM = 5 filter could introduce survivorship bias (correctly flagged by L1 audit as L4a). |
| **Look-ahead bias in leads** | No look-ahead bias. Lead variables are constructed from future fiscal quarters, which is the intended design. The contemporaneous timing issue (L2) is a framing problem, not look-ahead bias. |
| **Selection on DV** | ibq <= 0 exclusion is selection on the DV's denominator, not the DV itself. This is methodologically defensible (payout ratio is undefined for negative earnings) but creates a non-random sample. Correctly flagged by L1 audit. |

---

## M. Master Red-Team Issue Register

| ID | Severity | Source | Description | Status |
|----|----------|--------|-------------|--------|
| L1 | MAJOR | L1 audit | Call-level estimation inflates N vs. firm-quarter DV variation | Confirmed. Must-fix. |
| L3 | MAJOR | L1 audit | ~57% zero mass point; OLS suboptimal | Confirmed. Must-fix. |
| L2 | MODERATE | L1 audit (recalibrated) | Contemporaneous DV reflects past payout; framing issue | Confirmed. Reframe in text. |
| L4 | MODERATE | L1 audit | dvpspq pay-date timing | Confirmed. Acknowledge. |
| L5 | MODERATE | L1 audit | 48 tests, no multiple-testing correction | Confirmed. Add footnote. |
| L6 | MODERATE | L1 audit | Selection on profitability (ibq > 0) | Confirmed. Report fraction excluded. |
| L7 | MODERATE | L1 audit | No causal identification | Confirmed. Standard limitation. |
| G1 | MINOR | Red-team new | PayoutRatio_q can exceed 1.0; no cap documented | New. Document design choice. |
| G3 | MINOR | Red-team new | merge_asof has no tolerance window | New. Consider adding tolerance or documenting. |
| K-MC | MINOR | Red-team new | Potential multicollinearity among 4 IVs (CEO subset of Manager) | New. Acknowledge in thesis text. |
| L8 | MINOR | L1 audit | No placebo test | Confirmed. |
| L9 | MINOR | L1 audit | No subsample heterogeneity | Confirmed. |
| L10 | MINOR | L1 audit | No fqtr range validation | Confirmed. |
| L11 | MINOR | L1 audit | Attrition table records only Col 1 | Confirmed. |

---

## N. What Committee Wouldn't Know

Reading only the first-layer audit, a thesis committee would NOT know:

1. **IV multicollinearity risk:** The 4 IVs are not independent -- CEO speakers are a subset of "all managers," so CEO_QA_Uncertainty_pct and Manager_QA_Uncertainty_pct are mechanically correlated. This could produce unstable individual coefficients even if the joint F-test is significant. The committee should be told whether VIF diagnostics were computed.

2. **PayoutRatio_q can exceed 1.0:** After winsorization at 99th percentile, extreme payout ratios (e.g., 3.0) survive. This is not inherently wrong (special dividends, share repurchase-related effects) but the committee should know the distribution shape beyond "57% zeros."

3. **No tolerance on merge_asof:** If a firm has a data gap of several quarters in Compustat, the merge_asof will match a call to a stale quarter. The committee should know whether this affects more than a trivial fraction of observations.

4. **`drop_absorbed=True` silently removes collinear controls:** If a control variable is perfectly collinear with the FE structure, it is dropped without appearing in the coefficient table. The committee should know whether any controls were absorbed in practice.

---

## O. Priority Fixes

### Must-fix (before thesis submission)

1. **L1: Firm-quarter collapse robustness.** Average IVs within firm-quarter, re-estimate all 12 specs. Compare N and coefficients. This is the single most important robustness check.

2. **L3: Zero mass point robustness.** At minimum, add a probit on binary "paid dividend this quarter" indicator. Tobit or fractional logit preferred.

### Should-fix

3. **L2: Reframe contemporaneous models** in thesis text as "association with recent payout," not prediction.

4. **K-MC: Report VIF or condition number** for the 4 IVs to address multicollinearity concern.

5. **L5: Add multiple-testing footnote** (Bonferroni or BH-adjusted thresholds).

### Nice-to-have

6. **G1: Document that PayoutRatio_q can exceed 1.0** and report the 95th/99th percentile values.

7. **G3: Consider adding a tolerance parameter** to merge_asof (e.g., 180 days) or report the distribution of match distances.

---

## P. Final Red-Team Readiness Statement

**The first-layer audit is APPROVED with minor supplements.**

The H12Q first-layer audit is factually accurate, appropriately skeptical, and actionable. All 28 verified claims match the source code. The audit correctly identifies the two genuinely important methodological issues (inflated N from call-level estimation, zero mass point) and provides specific, implementable fixes.

Three minor supplements from the red-team:
- IV multicollinearity (CEO is subset of Manager) should be acknowledged
- PayoutRatio_q > 1.0 should be documented as a design choice
- merge_asof tolerance should be noted

The audit's severity calibration is accurate with one exception: L2 (contemporaneous timing) is better classified as MODERATE rather than MAJOR, since the fix is textual reframing rather than re-estimation.

**Conditional on implementing the two must-fix items (firm-quarter collapse robustness, zero mass point robustness), this suite is thesis-committee-ready.**
