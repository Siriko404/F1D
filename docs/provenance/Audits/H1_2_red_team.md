# H1.2 Red-Team Audit (Second-Layer)

**Suite ID:** H1.2
**Red-team auditor:** Independent second-layer review
**Date:** 2026-03-21
**First-layer audit doc:** `docs/provenance/H1_2.md` (v1, 2026-03-19)
**Runner inspected:** `src/f1d/econometric/run_h1_2_cash_constraint.py` (current HEAD)
**Latest verified run:** `2026-03-19_014100` (three-category moderator)
**First-layer verified run:** `2026-03-19_005934` (binary moderator -- STALE)

---

## A. Overall Assessment

**VERDICT: FAIL -- STALE AUDIT. The first-layer audit documents a previous version of the code that no longer exists.**

The first-layer audit describes a binary moderator (`Unrated_or_NonIG`) producing one interaction term (`MgrPresUnc_x_Unrated`), two model columns with coefficients b1-b3, and a specific set of regression results. The current code implements a three-category moderator (`BelowIG` + `Unrated` dummies, with IG as reference group), producing two interaction terms (`MgrPresUnc_x_BelowIG` and `MgrPresUnc_x_Unrated`), and coefficients b1-b5. The string `Unrated_or_NonIG` does not appear anywhere in the current runner file.

The code was refactored between run `2026-03-19_005934` (binary, documented by L1 audit) and run `2026-03-19_014100` (three-category, current code). The first-layer audit was never updated.

---

## B. Factual Accuracy of First-Layer Claims

### B.1 INCORRECT claims (code has changed)

| L1 Section | L1 Claim | Actual (current code) | Severity |
|------------|----------|----------------------|----------|
| A.1 | Moderator is `Unrated_or_NonIG` (binary) | Moderator is two dummies: `BelowIG` + `Unrated` (three-category, IG=reference) | CRITICAL |
| A.4 | One interaction term `MgrPresUnc_x_Unrated` | Two interaction terms: `MgrPresUnc_x_BelowIG` and `MgrPresUnc_x_Unrated` | CRITICAL |
| A.4 | Moderator source field classified as "BBB- and above = IG (0); below BBB- or unrated = 1" | IG=reference (both dummies=0); BelowIG=1 for rated junk; Unrated=1 for no rating match | CRITICAL |
| A.6 | Col 1: b1=0.0050, p=0.2703, within-R2=-0.2095 | Col 1: b1=0.0074, p=0.1812, within-R2=-0.1871 | CRITICAL |
| A.6 | Col 2: b1=0.0039, p=0.1304, within-R2=0.0462 | Col 2: b1=0.0040, p=0.1255, within-R2=0.0417 | CRITICAL |
| A.6 | One interaction coefficient b3 per column | Two interaction coefficients (b4, b5) per column | CRITICAL |
| E.2 | Match rates: IG=19,887; Unrated/Non-IG=59,600 | IG=19,887; Below-IG=18,589; Unrated=41,011 (three-way split) | CRITICAL |
| E.4 | Corr(Unrated_or_NonIG, Size) = -0.6130 | Variable `Unrated_or_NonIG` does not exist in current code | CRITICAL |
| H.1-H.2 | Full coefficient tables with binary moderator results | All coefficients are from stale run; current run has different estimates | CRITICAL |
| F.3.1 | Variable dictionary for `Unrated_or_NonIG` | Should document `BelowIG` and `Unrated` separately | CRITICAL |
| F.4.1 | Interaction `MgrPresUnc_x_Unrated` only, VIF=4.76/4.72 | Two interactions; VIF(int_below_ig)=2.09/2.08, VIF(int_unrated)=3.68/3.66 | CRITICAL |
| A.2 | Model formula shows 3 key coefficients (b1, b2, b3) | Model formula has 5 key coefficients (b1, b2, b3, b4, b5) | CRITICAL |

### B.2 Claims that remain correct (invariant across versions)

| L1 Section | Claim | Status |
|------------|-------|--------|
| A.1 | IV = `Manager_Pres_Uncertainty_pct` | CORRECT |
| A.2 | Estimator: PanelOLS, Industry+FY FE, firm-clustered SEs | CORRECT |
| A.3 | DVs: `CashHoldings` and `CashHoldings_lead` | CORRECT |
| A.4 | 11 control variables (same list) | CORRECT |
| A.4 | IG_RATINGS set = {AAA, AA+, ..., BBB-} (10 codes) | CORRECT |
| A.5 | FE config: Industry(FF12) + FY, no entity FE | CORRECT |
| A.5 | SEs: firm-clustered | CORRECT |
| B | Panel hash: `3aaee0a...` | CORRECT (same panel used in both runs) |
| B | Ratings hash: `d411fc9...` | CORRECT |
| C.1-C.2 | Dependency chain and raw data sources | CORRECT |
| D.1 | H1 panel: 112,968 rows x 31 cols | CORRECT |
| D.2 | Ratings CSV: 2,064,429 rows, 22 rating codes | CORRECT |
| E.1 | merge_asof implementation (backward, by gvkey) | CORRECT |
| E.6 | IV centering mean = 0.8687 | CORRECT (confirmed in latest summary_stats.csv) |
| G.1 | Winsorization rules | CORRECT (inherited, unchanged) |

### B.3 Partially correct claims

| L1 Section | Claim | Issue |
|------------|-------|-------|
| A.6 | N_obs Col 1 = 69,899; N_obs Col 2 = 68,545 | Same N in both versions (sample unchanged, only moderator parameterization differs) |
| A.6 | N_firms Col 1 = 1,759; N_firms Col 2 = 1,736 | Same N_firms (correct) |
| E.3 | 86% of firms have zero within-firm moderator variation | This was for the binary moderator. For the three-category moderator the within-firm variation statistics may differ (not re-verified) |
| E.5 | Attrition table structure | Now includes three-way split (IG/Below-IG/Unrated) instead of two-way |
| J.1 | Moderator conflates unrated with below-IG | This was the L1 issue that the code FIX addressed. The three-category design resolves J.1. The audit simultaneously documents the problem AND fails to notice the fix. |

---

## C. Completeness of First-Layer Audit

### C.1 Missing coverage (would be missing even if audit were current)

1. **No verification of the three-category classification logic.** The code at lines 233-237 creates `BelowIG = (has_rating & ~is_ig)` and `Unrated = (~has_rating)`. This means firms with a NaN `splticrm` after merge_asof are classified as Unrated, while firms with a non-IG rating code are classified as BelowIG. The audit should verify that the three categories are mutually exclusive and exhaustive (i.e., every row has exactly one of: both dummies=0, BelowIG=1, or Unrated=1).

2. **No verification of VIF changes.** The three-category design substantially reduces VIF: from 4.76 (binary interaction) to 2.09 (BelowIG interaction) and 3.68 (Unrated interaction). This is a material improvement that should be documented.

3. **No verification that the BelowIG group size is adequate.** From the latest diagnostics: N_below_ig = 16,214 in Col 1 (23.2% of sample). This is sufficient but should be explicitly noted.

### C.2 Stale coverage (documented but now wrong)

Every section that discusses the moderator, interaction term, regression results, VIF, or model interpretation is stale. This includes sections A.4, A.6, E.2-E.4, F.3, F.4, H.1-H.2, J.1, K.2-K.6, L1-L5, and M.

---

## D. Appropriateness of Skepticism

### D.1 L1 issues that are now resolved by the code fix

| L1 Issue | Status |
|----------|--------|
| J.1 / L1 (Moderator heterogeneity: conflating unrated with below-IG) | RESOLVED by three-category design |
| L4 (No alternative constraint measures) | PARTIALLY RESOLVED -- below-IG is now separated as a cleaner constraint proxy |
| L5 (No subsample analysis) | PARTIALLY RESOLVED -- the three-category design is functionally equivalent to a three-way subsample comparison within a single regression |

### D.2 New issues the L1 audit should have raised (for the current code)

1. **BelowIG interaction is negative and insignificant in both columns** (b4 = -0.0115 in Col 1, p=0.239; b4 = -0.0062 in Col 2, p=0.166). The sign is opposite to the CH1 prediction (expected positive: constrained firms hoard more cash when uncertainty is high). This is a stronger null than the binary version -- even for genuinely credit-constrained firms, no amplification is detected.

2. **Unrated interaction is positive but insignificant in Col 1** (b5 = +0.0139, p=0.226), and negative/insignificant in Col 2 (b5 = -0.0032, p=0.473). The sign instability across columns weakens any interpretation.

3. **Level effects are informative.** BelowIG level = +0.030 (p<0.001) and Unrated level = +0.063 (p<0.001) in Col 1. Both constrained groups hold more cash than IG at mean uncertainty, but the effect is twice as large for unrated firms. This confirms the L1 audit's observation about heterogeneity between the two groups and validates the three-category redesign.

4. **The docstring in the runner (lines 15-29) describes the three-category model and explicitly references "L1 fix."** This confirms the code was updated in response to the first-layer audit's Issue J.1/L1, but the audit document was not updated to reflect the fix.

---

## E. Verified Run Correspondence

| Field | L1 Audit Claims | Current Code/Output |
|-------|----------------|---------------------|
| Verified run | `2026-03-19_005934` | Stale. Latest run is `2026-03-19_014100` |
| Git commit | `8f5e929...` | Same commit hash in both run manifests |
| Panel hash | `3aaee0a...` | Matches latest manifest |
| Ratings hash | `d411fc9...` | Matches latest manifest |

**Note:** Both runs share the same git commit hash (`8f5e929...`), which means the code change happened within the same commit. The older run used a previous version of the file that was subsequently modified and re-run, both under the same commit. This is plausible if the commit was made after the second run.

---

## F. Code Path Verification (Current Code)

### F.1 Moderator construction (lines 232-237)

```python
is_ig = panel["splticrm"].isin(IG_RATINGS)
has_rating = panel["splticrm"].notna()
panel[MOD_BELOW_IG] = (has_rating & ~is_ig).astype(float)
panel[MOD_UNRATED] = (~has_rating).astype(float)
```

Verified: three categories are mutually exclusive and exhaustive. `is_ig & has_rating` -> IG (both dummies=0). `~is_ig & has_rating` -> BelowIG=1. `~has_rating` -> Unrated=1.

### F.2 Interaction construction (lines 315-316)

```python
df[INT_BELOW_IG] = df[IV_CENTERED] * df[MOD_BELOW_IG]
df[INT_UNRATED] = df[IV_CENTERED] * df[MOD_UNRATED]
```

Verified: interactions use centered IV, correctly computed.

### F.3 Exogenous variables (lines 397-398)

```python
exog = [IV_CENTERED, MOD_BELOW_IG, MOD_UNRATED,
        INT_BELOW_IG, INT_UNRATED] + all_controls
```

Verified: 5 key variables + 11 controls (+ CashHoldings in Col 2) = 16 or 17 regressors.

### F.4 One-tailed p-value (lines 442-443)

```python
p_one_iv = p_two_iv / 2 if beta_iv > 0 else 1 - p_two_iv / 2
```

Verified: correct one-tailed transformation for directional test (b1 > 0).

### F.5 Stars functions (lines 497-510)

Verified: one-tailed stars for main IV, two-tailed stars for interactions. Standard thresholds (0.01, 0.05, 0.10).

---

## G. Latest Run Results (for reference)

### Col 1: DV = CashHoldings

| Variable | Beta | SE | p (2-tail) | p (1-tail) |
|----------|------|----|------------|------------|
| Manager_Pres_Unc_c (IV) | 0.0074 | 0.0081 | 0.3624 | 0.1812 |
| BelowIG (level) | 0.0304 | 0.0055 | 0.0000 | -- |
| Unrated (level) | 0.0632 | 0.0057 | 0.0000 | -- |
| MgrPresUnc_x_BelowIG | -0.0115 | 0.0098 | 0.2387 | -- |
| MgrPresUnc_x_Unrated | 0.0139 | 0.0115 | 0.2260 | -- |

N=69,899. Within-R2=-0.1871. VIF(int_below_ig)=2.09. VIF(int_unrated)=3.68.

### Col 2: DV = CashHoldings_lead

| Variable | Beta | SE | p (2-tail) | p (1-tail) |
|----------|------|----|------------|------------|
| Manager_Pres_Unc_c (IV) | 0.0040 | 0.0035 | 0.2510 | 0.1255 |
| BelowIG (level) | 0.0028 | 0.0020 | 0.1579 | -- |
| Unrated (level) | 0.0102 | 0.0018 | 0.0000 | -- |
| MgrPresUnc_x_BelowIG | -0.0062 | 0.0044 | 0.1656 | -- |
| MgrPresUnc_x_Unrated | -0.0032 | 0.0044 | 0.4734 | -- |
| CashHoldings_t (control) | 0.7657 | 0.0097 | 0.0000 | -- |

N=68,545. Within-R2=0.0417. VIF(int_below_ig)=2.08. VIF(int_unrated)=3.66.

---

## H. Attrition Table Verification (Latest Run)

| Stage | N | Note |
|-------|---|------|
| Full panel (H1) | 134,790 | Matches L1 audit |
| Year filter (2002-2016) | 101,309 | Matches |
| Main sample | 79,487 | Matches |
| IG firms (reference) | 19,887 | Matches |
| Below-IG firms | 18,589 | NEW category (not in L1 audit) |
| Unrated firms | 41,011 | Was 59,600 in L1 audit (which combined below-IG + unrated) |
| Complete-case + min-calls (Col 1) | 69,899 | Matches (sample N unchanged) |

**Verification:** 19,887 + 18,589 + 41,011 = 79,487. Three categories sum to Main sample total. PASS.

**Cross-check with L1 audit:** L1 reported Unrated/Non-IG = 59,600. Splitting: 59,600 = 18,589 (below-IG) + 41,011 (unrated). Confirmed: 18,589 + 41,011 = 59,600. PASS.

---

## I. Summary Statistics Verification (Latest Run)

| Variable | N | Mean |
|----------|---|------|
| BelowIG | 79,487 | 0.2339 |
| Unrated | 79,487 | 0.5159 |
| Manager_Pres_Unc_c | 77,908 | 0.0000 |

Verified: BelowIG mean (0.234) implies 23.4% of Main sample; Unrated mean (0.516) implies 51.6%. Remaining 25.0% are IG. These match the attrition splits. Centering mean is zero (correct).

---

## J. L1 Audit Issue Register Re-Assessment

| L1 Issue | L1 Severity | Red-Team Re-Assessment |
|----------|-------------|----------------------|
| L1 (Moderator conflates unrated with below-IG) | MODERATE | **RESOLVED** by three-category design in current code. L1 audit simultaneously identifies this problem and fails to note the fix. |
| L2 (Corr with Size = -0.61) | MODERATE | **PARTIALLY RESOLVED**. The three-category design separates the correlation. BelowIG may have lower correlation with Size than the combined moderator. Should be re-verified with current variables. |
| L3 (86% zero within-firm variation) | MODERATE | **STATUS UNKNOWN** for current variables. Within-firm variation should be re-assessed for both BelowIG and Unrated dummies separately. |
| L4 (No alternative constraint measures) | MODERATE | **PARTIALLY ADDRESSED**. BelowIG is now a cleaner constraint proxy. The WW/SA/HP suggestion remains valid but is less urgent. |
| L5 (No subsample analysis) | LOW | **PARTIALLY ADDRESSED**. Three-category design with two interactions is functionally a within-regression subsample comparison. |
| L6 (Sample 2002-2016 vs H1's 2002-2018) | LOW | UNCHANGED. Still valid. |
| L7 (Negative within-R2) | LOW | UNCHANGED. Col 1 within-R2 is still negative (-0.187 vs -0.209 in stale run). |
| L8 (Summary stats on full Main sample) | LOW | UNCHANGED. Still valid. |
| L9 (Moulton problem) | LOW | UNCHANGED. Still valid. |
| L10 (Attrition table structure) | COSMETIC | UNCHANGED. Still mixes sequential filters with descriptive splits. |

---

## K. New Issues Identified by Red-Team

| # | Severity | Description |
|---|----------|-------------|
| RT-1 | **CRITICAL** | The entire L1 audit document is stale. It documents a binary moderator that no longer exists in the code. All regression results, model specifications, variable dictionaries, and coefficient tables are wrong relative to the current code and latest run. |
| RT-2 | MODERATE | The BelowIG interaction (b4) is negative in both columns (-0.0115 and -0.0062), opposite to the CH1 prediction. This is a stronger null than the binary version and should be discussed: genuinely junk-rated firms do NOT show amplified uncertainty-cash sensitivity. |
| RT-3 | MODERATE | The Unrated interaction (b5) flips sign across columns (+0.0139 in Col 1 vs -0.0032 in Col 2). This sign instability is interpretable: the positive contemporaneous association disappears after controlling for lagged CashHoldings, suggesting it reflects persistent cross-sectional differences rather than a dynamic effect. |
| RT-4 | LOW | The attrition table in the latest run has a structural issue: the "N Lost" column for "Unrated firms" shows +22,422 (a gain, not a loss), because the table format assumes monotonic decreasing stages. This is because the three descriptive-split rows (IG/BelowIG/Unrated) are not sequential attrition stages. |
| RT-5 | LOW | The runner docstring (line 26) mentions "L1 fix" and describes the rationale for the three-category redesign, but the provenance doc was not updated. This indicates a process failure: code fixes derived from audit findings should trigger audit doc updates. |

---

## L. Referee Priority Fixes (Updated)

### Priority 0 (Blocking -- must be done before any other work)

1. **Rewrite the entire H1.2 provenance document** to reflect the current three-category moderator design, the latest run `2026-03-19_014100`, and the current regression results. Every section from A through N must be updated. The current document is not usable.

### Priority 1 (Required before defense)

2. **Discuss the negative BelowIG interaction** in the thesis text. The CH1 prediction is b4 > 0 (constrained firms hoard more cash under uncertainty). The estimate is b4 = -0.012 (p=0.24). Even the sign is wrong. This is a clean null for the specific channel.

3. **Re-verify within-firm variation** for both BelowIG and Unrated dummies separately. The 86% figure from the L1 audit was for the binary moderator and may not apply to the components.

### Priority 2 (Strongly recommended)

4. **Report VIF improvement.** The three-category design reduced max VIF from 4.76 to 3.68 (Unrated interaction). This is a material improvement worth noting.

5. **Re-compute moderator-Size correlations** for BelowIG and Unrated separately. The -0.61 figure was for the binary moderator.

---

## M. Conclusion

The first-layer audit document for H1.2 is **entirely stale** and must be rewritten from scratch. The code was refactored from a binary to a three-category moderator (implementing the L1 audit's own recommendation in Issue J.1/L1), but the audit document was not updated. As a result:

- Every regression coefficient, p-value, and model diagnostic in the document is wrong.
- The variable dictionary describes a variable (`Unrated_or_NonIG`) that does not exist in the code.
- The model specification shows 3 key coefficients when the code produces 5.
- The VIF values, moderator splits, and correlation checks are all stale.

The underlying code is well-implemented. The three-category design is a genuine improvement over the binary moderator. The results are a clean null for the CH1 channel. But the provenance document does not document any of this.

**Red-team verdict: FAIL. Full rewrite of H1_2.md required.**

---

## N. Verification Checklist

| # | Check | Result |
|---|-------|--------|
| 1 | L1 audit run matches current code | FAIL -- audit documents stale run `2026-03-19_005934`; current code produces `2026-03-19_014100` |
| 2 | L1 moderator description matches code | FAIL -- L1 says binary; code is three-category |
| 3 | L1 coefficient values match current output | FAIL -- all coefficients differ |
| 4 | L1 VIF values match current output | FAIL -- L1 says 4.76; current code produces 2.09/3.68 |
| 5 | L1 sample counts match current output | PARTIAL -- N_obs matches; moderator split is different parameterization |
| 6 | L1 variable dictionary is complete | FAIL -- documents nonexistent `Unrated_or_NonIG`; missing `BelowIG` and `Unrated` |
| 7 | L1 model specification matches code | FAIL -- L1 shows 3 key variables; code has 5 |
| 8 | L1 data provenance (panel, ratings) | PASS -- hashes and paths correct |
| 9 | L1 merge logic description | PASS -- merge_asof logic unchanged |
| 10 | L1 centering verification | PASS -- IV mean 0.8687 confirmed in latest run |
| 11 | L1 FE configuration matches code | PASS -- Industry+FY FE, no entity FE |
| 12 | L1 SE configuration matches code | PASS -- firm-clustered |
| 13 | L1 controls list matches code | PASS -- same 11 controls |
| 14 | L1 issue register addresses real concerns | PARTIAL -- J.1/L1 was correct but is now resolved by code fix |
| 15 | L1 referee recommendations are actionable | STALE -- most recommendations were implemented in the code fix |

---

## O. Process Observation

The H1.2 audit reveals a process gap: when a code fix is implemented in response to an audit finding, the audit document must be updated in the same commit or immediately after. In this case, the code was refactored (binary -> three-category moderator) explicitly to address the L1 audit's Issue J.1, but the provenance document was left unchanged. This creates a dangerous situation where the "verified" document gives a false sense of assurance while describing code that no longer exists.

**Recommendation:** Establish a workflow rule that any code change to a runner script triggers a mandatory provenance document update before the next commit.

---

## P. Files Examined

| File | Purpose |
|------|---------|
| `docs/provenance/H1_2.md` | First-layer audit (stale) |
| `src/f1d/econometric/run_h1_2_cash_constraint.py` | Runner (current, three-category) |
| `outputs/econometric/h1_2_cash_constraint/2026-03-19_005934/model_diagnostics.csv` | Stale run diagnostics (binary moderator) |
| `outputs/econometric/h1_2_cash_constraint/2026-03-19_014100/model_diagnostics.csv` | Latest run diagnostics (three-category) |
| `outputs/econometric/h1_2_cash_constraint/2026-03-19_014100/run_manifest.json` | Latest run manifest |
| `outputs/econometric/h1_2_cash_constraint/2026-03-19_014100/summary_stats.csv` | Latest summary statistics |
| `outputs/econometric/h1_2_cash_constraint/2026-03-19_014100/sample_attrition.csv` | Latest attrition table |
| `outputs/econometric/h1_2_cash_constraint/2026-03-19_014100/report_step4_H1_2.md` | Latest auto-generated report |

*Red-team audit completed 2026-03-21. All claims verified against source code and output artifacts.*
