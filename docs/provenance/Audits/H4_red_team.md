# H4 Leverage --- Second-Layer Red-Team Audit

**Auditor:** Independent red-team (hostile-but-fair replication auditor)
**Date:** 2026-03-21
**Suite ID:** H4
**First-layer audit:** `docs/provenance/H4.md` (dated 2026-03-18)
**Runner:** `src/f1d/econometric/run_h4_leverage.py`
**Panel builder:** `src/f1d/variables/build_h4_leverage_panel.py`

---

## A. Overall Assessment of First-Layer Audit

The first-layer audit is thorough in its coverage of variable construction chains, winsorization, merge logic, and fixed-effects specifications. However, it contains one **critical factual omission** (the lagged DV control that is present in every model specification) and numerous **stale line-number references** that suggest the audit was performed on a prior version of the code and not re-verified. The omission of the lagged DV control cascades into multiple downstream errors in the audit document (incorrect control counts, incorrect claim about no lagged DV control in Section 11.5).

**Verdict:** The first-layer audit is substantially useful but requires material corrections before it meets thesis-standard review requirements.

---

## B. Critical Findings (Errors of Fact)

### RT2-H4-01 | CRITICAL | Lagged DV control completely omitted from audit

The first-layer audit states there are "7 base controls" (Section 6.3) and "base + 4 extended controls" (Section 6.4), listing `Size, TobinsQ, ROA, CapexAt, DividendPayer, OCF_Volatility, CashHoldings` as the base set. The audit further states in Section 11.5: "No lagged DV control is included (which would help isolate the incremental effect but risks absorbing the signal)."

**This is factually wrong.** Every entry in `MODEL_SPECS` (runner L111-126) includes a `lag_control` field:
- BookLev models (cols 1-8): `"lag_control": "BookLev_lag"`
- DebtToCapital models (cols 9-16): `"lag_control": "DebtToCapital_lag"`

The `prepare_regression_data()` function (runner L249-252) and `run_regression()` (L312-315) both check for `lag_control` and append it to the controls list:

```python
lag_control = spec.get("lag_control")
if lag_control:
    controls = controls + [lag_control]
```

The lagged DV then enters the exog matrix at L327: `exog = KEY_IVS + controls`.

**Impact:** The actual base model has 8 controls (7 base + 1 lag), and the extended model has 12 controls (7 base + 4 extended + 1 lag). Every regression includes a lagged dependent variable as a control. This fundamentally changes the interpretation of the model: it is a partial-adjustment / dynamic panel specification, not a static panel regression. The first-layer audit's Section 11.5 critique about "no lagged DV control" is the exact opposite of reality. The SUMMARY_STATS_VARS list (runner L143-144) also includes `BookLev_lag` and `DebtToCapital_lag`, confirming these are first-class variables.

**Implications for inference:**
- Including a lagged DV as a regressor in a firm-FE model (Nickell bias) is a well-known econometric concern. With T potentially large (many fiscal years), the bias may be small, but it should be acknowledged.
- The lagged DV is likely to absorb most of the cross-sectional and within-firm variation in leverage, potentially attenuating the uncertainty IV coefficients toward zero. If significant results survive the lagged DV control, they are more credible than the audit suggests.

### RT2-H4-02 | MAJOR | Systematic line-number drift across all code references

The first-layer audit cites dozens of line numbers that are consistently off by 2-12 lines from the actual current code. A sample of discrepancies:

| Audit citation | Claimed line | Actual line | Offset |
|----------------|-------------|-------------|--------|
| BookLev formula | `_compustat_engine.py` L1039 | L1041 | +2 |
| DebtToCapital formula | L1042-1048 | L1043-1050 | +1 |
| CashHoldings | L1066 | L1068 | +2 |
| TobinsQ | L1067-1077 | L1069-1079 | +2 |
| CapexAt | L1079-1085 | L1081-1087 | +2 |
| DividendPayer | L1087-1092 | L1089-1094 (approx) | +2 |
| Inf replacement | L1171-1172 | L1185-1186 | +14 |
| skip_winsorize set | L1186 | L1199 | +13 |
| Winsorize loop | L1194-1201 | L1208-1216 | +14 |
| match_to_manifest | L1287-1294 | L1301-1308 | +14 |
| `exog = KEY_IVS + controls` | runner L315 | L327 | +12 |
| `n_cols = 8` | runner L418 | L430 | +12 |
| MultiIndex set_index | runner L324 | L336 | +12 |
| PanelOLS industry | runner L332-339 | L344-352 | +12 |
| PanelOLS firm | runner L345-346 | L357-358 | +12 |
| Two-tailed p | runner L372 | L384 | +12 |
| Panel builder temporal vars | L73-104 | L73-104 | 0 (correct) |
| Panel builder merge | L237-238 | L237-238 | 0 (correct) |

The runner offsets are consistently +12 (suggesting ~12 lines were added after the audit, likely the `lag_control` lines and related `BookLev_lag`/`DebtToCapital_lag` columns). The engine offsets have two regimes: +2 for early lines, +13-14 for later lines, suggesting multiple insertions.

**Impact:** A reviewer following the audit's line references will land on the wrong code. While the surrounding context usually makes the intent clear, this undermines confidence in the audit's claim of independent verification.

---

## C. Completeness Gaps

### RT2-H4-03 | MAJOR | LaTeX table does not disclose lagged DV control

The `_save_latex_table()` function (runner L416-548) renders coefficient rows for the 4 key IVs and indicator rows for "Controls" (Base/Extended), "Industry FE", "Firm FE", and "Fiscal Year FE". There is no row indicating that a lagged DV control is included. The table notes (L536-545) also do not mention the lagged DV.

A reader examining the LaTeX table would not know that `BookLev_lag` (or `DebtToCapital_lag`) is in the model. This is a separate issue from L1 (table truncation) -- even if the table were expanded to 16 columns, the lagged DV presence would remain undisclosed.

**Recommendation:** Add a "Lagged DV" indicator row to the table (Yes/Yes for all columns) and mention the lagged DV in the table notes.

### RT2-H4-04 | MODERATE | Nickell bias not discussed

With firm FE and a lagged DV, the standard Nickell (1981) bias applies. The bias is of order O(1/T). If the average firm has >10 fiscal years, the bias may be small, but this should be explicitly acknowledged. The first-layer audit's Section 11 (Identification & Inference Assessment) does not mention Nickell bias because it incorrectly believed no lagged DV was present.

### RT2-H4-05 | LOW | `lag_control` absent from variable dictionary

Section 6 of the first-layer audit provides a detailed variable dictionary but does not include entries for `BookLev_lag` or `DebtToCapital_lag`. These are created by `_create_temporal_vars_for_col()` (panel builder L73-104) using the same deduplication/shift logic as the lead variables, but shifted +1 instead of -1. The audit documents the lead construction chain but omits the lag.

---

## D. Verification of First-Layer Claims

### D.1 Claims confirmed as correct

| Claim | Verified | Notes |
|-------|----------|-------|
| BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq | CORRECT | Engine L1041 |
| DebtToCapital = total_debt / (seqq + total_debt); NaN when denom <= 0 | CORRECT | Engine L1043-1050 |
| 4 simultaneous IVs | CORRECT | `KEY_IVS` list, runner L85-89 |
| Industry FE via `other_effects` | CORRECT | Runner L349 |
| Firm FE via `EntityEffects + TimeEffects` | CORRECT | Runner L357 |
| Time index = `fyearq_int` | CORRECT | Runner L336 |
| Firm-clustered SEs | CORRECT | Runner L353, L359 |
| Two-tailed p-values from linearmodels `.pvalues` | CORRECT | Runner L384 |
| Main sample = FF12 codes excluding 8, 11 | CORRECT | Runner L237 |
| MIN_CALLS_PER_FIRM = 5 | CORRECT | Runner L129 |
| `drop_absorbed=True` | CORRECT | Runner L350, L358 |
| `check_rank=False` on industry spec only | CORRECT | Runner L351 |
| LaTeX table = 8 columns (BookLev only) | CORRECT | `n_cols = 8` at runner L430 |
| model_diagnostics.csv contains all 16 models | CORRECT | Runner L586 |
| Lead DVs require consecutive fiscal years | CORRECT | Panel builder L101-102 |
| No tolerance on merge_asof | CORRECT | Engine L1301-1308, no `tolerance` param |
| Winsorization 1%/99% by fiscal year | CORRECT | Engine L1208-1216 |
| Runner docstring says col{1-8} | CORRECT | Runner L44 |
| 16 MODEL_SPECS entries | CORRECT | Runner L110-127 |
| Zero row-delta enforced on merges | CORRECT | Panel builder L237-238 |
| Temporal var deduplication keeps last call | CORRECT | Panel builder L83 `keep="last"` |
| Consecutive-year NaN guard | CORRECT | Panel builder L93-94, L101-102 |

### D.2 Claims found incorrect or incomplete

| Claim | Assessment | Detail |
|-------|-----------|--------|
| "7 base controls" | INCORRECT | 7 base + 1 lag_control = 8 per spec |
| "Base + 4 extended controls" | INCORRECT | 7 base + 4 extended + 1 lag = 12 per spec |
| "No lagged DV control is included" (Section 11.5) | INCORRECT | Every spec includes lag_control |
| `exog = KEY_IVS + controls` at runner L315 | STALE LINE | Actual: L327 |
| "controls" at L315 | INCOMPLETE | `controls` already includes the lag_control by this point |
| `n_cols = 8` at runner L418 | STALE LINE | Actual: L430 |
| Inf replaced at engine L1171-1172 | STALE LINE | Actual: L1185-1186 |
| match_to_manifest at L1287-1294 | STALE LINE | Actual: L1282-1308 |

---

## E. Assessment of Known Limitations List

The first-layer audit's 10 known limitations (L1-L10) are reviewed:

| ID | Audit assessment | Red-team verdict |
|----|-----------------|-----------------|
| L1 (LaTeX table 8 cols) | CRITICAL | **CONFIRMED.** Genuine defect. |
| L2 (No VIF diagnostics) | MAJOR | **CONFIRMED** but less severe with lagged DV -- collinearity of the 4 IVs is the relevant concern, and the lagged DV does not affect this. |
| L3 (check_rank=False) | MAJOR | **CONFIRMED.** |
| L4 (Asymmetric DV construction) | MODERATE | **CONFIRMED.** |
| L5 (No merge_asof tolerance) | MODERATE | **CONFIRMED.** Shared-engine issue. |
| L6 (Summary stats != estimation sample) | MODERATE | **CONFIRMED.** |
| L7 (fillna(0) for debt, no clip) | MODERATE | **CONFIRMED.** |
| L8 (Attrition tracks BookLev only) | LOW-MOD | **CONFIRMED.** |
| L9 (Stale docstring) | LOW | **CONFIRMED.** |
| L10 (No double-clustering) | LOW | **CONFIRMED.** |

**Missing from L-list:**

| New ID | Severity | Description |
|--------|----------|-------------|
| L11 | **MAJOR** | **Lagged DV control not disclosed in LaTeX table or table notes.** All 16 models include BookLev_lag or DebtToCapital_lag as a regressor, but the table has no indicator row for this, and the notes do not mention it. |
| L12 | **MAJOR** | **Nickell bias with firm FE + lagged DV.** Even-numbered columns use firm FE alongside a lagged DV control. With finite T, the lagged DV coefficient is biased downward and other coefficients may inherit bias. Severity depends on average T per firm. |
| L13 | **MODERATE** | **Lag-control creates matching asymmetry.** BookLev models (cols 1-8) control for BookLev_lag; DebtToCapital models (cols 9-16) control for DebtToCapital_lag. Since the lag variable is constructed from the same temporal-var pipeline as the lead, it inherits the same deduplication (keep-last-call) and consecutive-year requirements. Missing lag values create additional complete-case attrition not tracked in the attrition table. |

---

## F. Assessment of Identification & Inference Section

Section 11 of the first-layer audit is well-structured but contains one critical factual error (11.5 re: lagged DV). With the lagged DV correction:

| Subsection | Assessment |
|------------|-----------|
| 11.1 Endogeneity | Adequate. Correctly notes co-determination concern. |
| 11.2 Moulton Problem | Good. The "precision" clarification (within-quarter, not within-year) is a useful addition. |
| 11.3 Multicollinearity Among IVs | Adequate. VIF recommendation is appropriate. |
| 11.4 Simultaneous IV Interpretation | Adequate. |
| 11.5 Leverage Persistence | **FACTUALLY INCORRECT.** States "No lagged DV control is included." The code includes BookLev_lag/DebtToCapital_lag in every model. Needs complete rewrite. With the lagged DV present, the relevant concern shifts from "leverage persistence biasing results" to "Nickell bias in firm-FE models" and "lagged DV potentially absorbing the signal." |
| 11.6 Multiple Testing | Adequate. |
| 11.7 Clustering | Adequate. |

**Missing from Section 11:**

- **Nickell bias** (as above).
- **Dynamic panel interpretation**: With a lagged DV, the model is a partial-adjustment specification. The IV coefficients now represent the short-run impact conditional on the prior level, and the long-run multiplier is beta_IV / (1 - rho), where rho is the lagged DV coefficient. The thesis text should report both.
- **Potential for post-treatment bias**: BookLev_lag is measured at t-1 but could itself be influenced by uncertainty at t-1 (if the hypothesis is correct). Conditioning on it could attenuate the contemporaneous effect. This is a standard concern in dynamic panel models but should be noted.

---

## G. Assessment of Variable Dictionary

The variable dictionary (Section 6) is detailed and mostly accurate for the variables it covers. The main gap is the omission of `BookLev_lag` and `DebtToCapital_lag`, which are constructed by the same `_create_temporal_vars_for_col()` function documented for the lead variables (Section 6.1.2, 6.1.4) but using `shift(+1)` instead of `shift(-1)`.

---

## H. Assessment of Design Decisions Section

Section 14 is comprehensive. One entry needs correction:

- The row "8-column LaTeX table (BookLev only)" correctly identifies this as a code defect.
- **Missing row:** A design-decision entry for the lagged DV control should be added, explaining the rationale (partial-adjustment model, isolating incremental effect of uncertainty beyond persistence).

---

## I. Assessment of Winsorization Summary

Section 6.6 is complete and accurate for the variables it covers. No issues found with the winsorization pipeline documentation.

---

## J. Assessment of Output Inventory

Section 8 is accurate. The note about summary_stats.csv sample and attrition table limitations are correct.

---

## K. Assessment of Red-Team Findings Disposition (Section 13)

Section 13.2 lists 12 red-team findings (RT-H4-01 through RT-H4-12). These are all confirmed as correctly documented. However, the most significant finding that should have been in this list -- the lagged DV control -- was missed entirely because the first-layer auditor did not notice the `lag_control` field in MODEL_SPECS.

---

## L. Line Reference Accuracy Summary

Of approximately 35 line-number citations in the first-layer audit:
- **Panel builder references:** Mostly correct (L73-104, L237-238, L140-142).
- **Runner references:** Systematically off by +12 lines. All runner line refs need updating.
- **Engine references:** Off by +2 for early sections, +13-14 for later sections. All engine line refs need updating.

---

## M. Severity Summary

| Severity | Count | IDs |
|----------|-------|-----|
| CRITICAL | 1 | RT2-H4-01 (lagged DV omission) |
| MAJOR | 3 | RT2-H4-02 (line drift), RT2-H4-03 (LaTeX no lag indicator), RT2-H4-04 (Nickell bias) |
| MODERATE | 1 | RT2-H4-05 (lag-control matching asymmetry, new L13) |
| LOW | 1 | RT2-H4-06 (lag absent from variable dictionary) |

---

## N. Required Corrections Before Thesis Submission

1. **Add `BookLev_lag` / `DebtToCapital_lag` to the variable dictionary** (Section 6) with full construction chain documentation.
2. **Rewrite Section 11.5** to reflect the actual presence of the lagged DV control, and add Nickell bias discussion.
3. **Update all line references** to match the current codebase.
4. **Add L11, L12, L13** to the Known Limitations table.
5. **Update control counts** throughout the document (8 base, 12 extended when including the lag control).
6. **Add a design-decision entry** for the lagged DV control.
7. **Fix the LaTeX table** (runner code change): add a "Lagged DV" indicator row and mention in table notes.

---

## O. Items NOT Requiring Correction

The following aspects of the first-layer audit were verified as correct and complete:
- DV construction chains (BookLev, DebtToCapital, and their leads)
- IV construction chain (4 uncertainty measures)
- Merge strategy documentation (merge_asof, zero row-delta)
- FE specification documentation (industry vs firm)
- Clustering documentation
- P-value interpretation
- Sample filtering logic
- Winsorization pipeline
- Temporal variable construction (deduplication, consecutive-year guard)
- Output inventory

---

## P. Conclusion

The first-layer audit is a high-quality document that covers most of the H4 suite's complexity accurately. Its single critical flaw -- missing the lagged DV control -- propagates into the identification discussion and control-count claims. The systematic line-number drift indicates the audit was not re-verified after a code revision that added the lag_control feature. Once the corrections in Section N are applied, the document will meet thesis-standard review requirements.

---

*Second-layer red-team audit conducted 2026-03-21. All findings verified against current codebase. No regression output was examined (no fresh run was executed).*
