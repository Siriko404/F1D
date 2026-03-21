# H1.1 Red-Team Audit (Second Layer)

**Suite ID:** H1.1
**First-layer audit:** `docs/provenance/H1_1.md` (v1, 2026-03-19)
**Red-team auditor mode:** Hostile-but-fair replication audit of the audit itself
**Date:** 2026-03-21
**Code inspected:** `src/f1d/econometric/run_h1_1_cash_tsimm.py` (current working-tree version)
**Runs inspected:** `2026-03-18_235755` (referenced by first-layer) and `2026-03-19_001554` (latest, post-centering)

---

## A. Red-Team Bottom Line

**The first-layer audit is factually stale. It was written against an earlier version of the code (run `2026-03-18_235755`) that did NOT mean-center the IV. The code was subsequently updated to add IV mean-centering and re-run (`2026-03-19_001554`). The audit doc was never updated to reflect this change.** As a result:

1. The audit's single highest-severity issue (J1: multicollinearity from non-centered IV, Corr=0.93) and its top Priority 1 fix ("mean-center the IV") are **already implemented** in the current code. The audit presents a solved problem as an open critical issue.
2. All coefficient values for the moderator's direct effect (z(log(TSIMM))) are wrong -- the audit reports 0.0283 (old run, uncentered), but the current code produces 0.0361 (new run, centered).
3. Multiple line-number references are incorrect (code was expanded by ~20 lines when centering logic was added).
4. The summary statistics now include a centered IV column (`Manager_Pres_Unc_c`) that the audit does not mention.

Despite these staleness issues, the audit's deeper structural criticisms (Moulton problem, lack of robustness checks, fragile interaction significance, sample composition mismatch with parent) remain valid and well-articulated. The audit is thorough and appropriately skeptical on econometric substance, but its factual substrate is outdated.

---

## B. Scope

| Dimension | Coverage |
|-----------|----------|
| Code version inspected | Current working-tree `run_h1_1_cash_tsimm.py` (820 lines, post-centering) |
| Output runs verified | Both `2026-03-18_235755` (old, uncentered) and `2026-03-19_001554` (new, centered) |
| First-layer doc length | 722 lines, 13 issues, 8 priority fixes |
| Artifacts cross-checked | `model_diagnostics.csv`, `regression_results_col1.txt`, `sample_attrition.csv`, `summary_stats.csv`, `h1_1_cash_tsimm_table.tex` (both runs) |

---

## C. Scorecard

| Dimension | Grade | Notes |
|-----------|-------|-------|
| Factual accuracy | **D** | Major staleness: coefficients, line numbers, and the #1 issue are wrong vs current code |
| Completeness | **B+** | Thorough coverage of data, merge, estimation, and econometric concerns |
| Appropriate skepticism | **A-** | Correctly identifies marginal significance, Moulton, and lack of robustness |
| Econometric rigor | **A-** | Referee-quality assessment of identification, inference, and robustness gaps |
| Reproducibility guidance | **C+** | Verified run is the old run; the current code produces different moderator coefficients |
| Staleness risk | **F** | Doc describes code state that no longer exists; priority fixes are already done |

**Overall: C+.** Excellent econometric analysis undermined by describing a codebase that has already been modified.

---

## D. Claim Verification Matrix

| # | Audit Claim | Location in Audit | Verified? | Finding |
|---|-------------|-------------------|-----------|---------|
| 1 | IV = `Manager_Pres_Uncertainty_pct` in regression | A.4 line 54 | **FALSE** | Regression uses `Manager_Pres_Unc_c` (mean-centered). Raw IV is loaded but not entered into the model. Code line 329: `exog = [IV_CENTERED, MODERATOR, INTERACTION] + all_controls` |
| 2 | Interaction = `Manager_Pres_Uncertainty_pct * z_log_tnic3tsimm` | F.4.1 | **FALSE** | Interaction uses centered IV: `df[IV_CENTERED] * df[MODERATOR]` (code line 284) |
| 3 | Function `transform_moderator()` at lines 197-226 | E.2 | **FALSE** | Function is `transform_moderator_and_center_iv()` at lines 199-247. Adds IV centering logic (lines 232-246) |
| 4 | "No centering of IV before interaction" (J5) | J5 | **FALSE** | IV IS mean-centered (code lines 80, 232-236, 284) |
| 5 | Corr(moderator, interaction) = 0.9331 (J1) | J1, F.4.1, K2 | **STALE** | This was true for the old (uncentered) run. With centering, the correlation should be ~0.12 per the audit's own prediction. The audit's #1 issue is already resolved. |
| 6 | Col 1 beta_moderator = 0.0283, SE = 0.0058 | H.1 | **STALE** | Current code produces beta_moderator = 0.0361, SE = 0.0034 (from `2026-03-19_001554` diagnostics) |
| 7 | Col 2 beta_moderator = 0.0068, SE = 0.0022 | H.1 | **STALE** | Current code produces beta_moderator = 0.0070, SE = 0.0012 |
| 8 | Interaction p = 0.0851 (Col 1) | H.1 | **TRUE** | Identical in both runs (centering does not change interaction coefficient in OLS) |
| 9 | Interaction vanishes in Col 2 (p = 0.94) | H.1 | **TRUE** | Identical in both runs |
| 10 | N = 76,239 (Col 1), N = 72,618 (Col 2) | H.1, E.3 | **TRUE** | Same in both runs; centering does not change sample |
| 11 | Left merge with row-count assertion | E.1 | **TRUE** | Code line 189 confirmed |
| 12 | `entity_effects=False` | E.4 | **TRUE** | Code line 344 |
| 13 | `time_effects=True` | E.4 | **TRUE** | Code line 345 |
| 14 | `other_effects=df_panel["ff12_code"]` | E.4 | **TRUE** | Code line 346 |
| 15 | `drop_absorbed=True`, `check_rank=False` | E.4 | **TRUE** | Code lines 347-348 |
| 16 | Firm-clustered SEs | A.5 | **TRUE** | Code line 350 |
| 17 | One-tailed transform: `p/2 if beta>0 else 1-p/2` | A.5 | **TRUE** | Code lines 363-364 |
| 18 | `MIN_CALLS_PER_FIRM = 5` at line 82 | A.4 | **MINOR ERROR** | Actually at line 83 in current code |
| 19 | `prepare_regression_data()` line 261 creates interaction | F.4.1, line 70 | **FALSE** | Interaction at line 284; function starts at line 264 |
| 20 | `filter_main_sample()` at line 237 | A.4 | **FALSE** | At line 255 in current code |
| 21 | Summary stats computed on Main sample pre-complete-case | G.5 | **TRUE** | Code lines 728-736 confirm stats on `panel` after `filter_main_sample()` |
| 22 | LaTeX notes distinguish one-tailed from two-tailed | K5 | **TRUE** | Confirmed in `h1_1_cash_tsimm_table.tex` (both runs) |
| 23 | z-score computed on Main sample, applied to full panel | E.2 | **TRUE** | Code lines 215-224 |
| 24 | TNIC merge on `(_gvkey_int, fyearq_int)` | E.1 | **TRUE** | Code lines 179-188 |
| 25 | Col 2 includes CashHoldings_t as extra control | A.6, MODEL_SPECS | **TRUE** | Code line 87 |

---

## E. Unsupported Claims

| # | Claim | Why unsupported |
|---|-------|-----------------|
| E1 | "Corr(z_log_TSIMM, Interaction) = 0.9331" presented as current state | This correlation was computed on the OLD (uncentered) interaction. The current code forms the interaction using the centered IV. The audit does not report the correlation for the current specification. |
| E2 | "VIF for the interaction likely exceeds 10" (J1) | May no longer be true after centering. No VIF was computed for either the old or new specification. |
| E3 | "The interaction SE (0.0052) may be inflated by 2-3x" (K2 point 2) | With centering, the SE is unchanged at 0.0052, which suggests the inflation estimate was incorrect OR centering alone was insufficient. The audit's prediction that centering would reduce the SE was not tested. |
| E4 | "CashHoldings AR(1) median=0.595, mean=0.550" (I, check 18) | The audit reports AR(1) > 0.9 in the text (Section A.3, MODEL_SPECS description) but the verification log shows AR(1) median=0.595. These are contradictory. |

---

## F. False Positives (Issues That Are Not Actually Issues)

| # | Audit Issue | Why it is a false positive |
|---|-------------|--------------------------|
| F1 | **J1 (High): Severe multicollinearity from non-centered IV** | The code already mean-centers the IV. This issue is resolved. However, the interaction SE did not change (0.0052 in both runs), which is unexpected -- see Section K below for discussion. |
| F2 | **J5 (Medium): No centering of IV before interaction** | Already implemented (code line 236). |
| F3 | **M Priority 1 item 1: "Mean-center the IV"** | Already done. |

---

## G. Missed Issues (Not Identified by First-Layer Audit)

| # | Severity | Issue |
|---|----------|-------|
| G1 | **High** | **Audit-code version mismatch is undisclosed.** The audit references run `2026-03-18_235755` but the code has been modified since that run (centering added, function renamed). A second run `2026-03-19_001554` exists with different results. The audit does not acknowledge this. Any reader relying on the audit will have incorrect coefficient values for the moderator. |
| G2 | **Medium-High** | **Centering did not improve the interaction SE.** The interaction SE = 0.0052 is identical in both the centered and uncentered runs. This contradicts the audit's prediction that centering would reduce the SE by "2-3x." The likely explanation is that with firm-clustered SEs, the multicollinearity-induced SE inflation is absorbed by the cluster-robust variance estimator, so centering has no effect on inference. This deserves investigation -- it suggests the multicollinearity concern (while textbook-correct for classical OLS SEs) may be immaterial under clustered inference. |
| G3 | **Medium** | **The regression variable name in the output is `Manager_Pres_Unc_c`, not `Manager_Pres_Uncertainty_pct`.** A reader comparing the regression output to the variable dictionary will not find the variable name. The audit's variable dictionary (F.2) documents only the raw IV, not the centered version actually used in estimation. |
| G4 | **Medium** | **The `regression_results_col1.txt` header says `IV: Manager_Pres_Uncertainty_pct` but the parameter table shows `Manager_Pres_Unc_c`.** This is a code-level documentation inconsistency (line 599 prints the raw IV name, but the regression uses the centered version). The audit did not catch this. |
| G5 | **Low-Medium** | **Summary stats now include `Manager_Pres_Unc_c` (centered IV) with mean=0.0000.** The audit's summary stats section (F.2.1) does not mention this variable. The centered mean confirms centering is working, but the audit doesn't document it. |
| G6 | **Low** | **LaTeX table note says "IV coefficient represents effect at sample-mean uncertainty"** -- this is correct for the centered specification but was NOT in the old run's LaTeX table (which used the uncentered IV). The audit's K5 discussion of the LaTeX notes may be based on the old table, not the current one. |

---

## H. Severity Recalibration

| Audit Issue | Audit Severity | Recalibrated Severity | Rationale |
|-------------|---------------|----------------------|-----------|
| J1 (multicollinearity) | High | **Resolved** (but new question emerges) | Code already centers. But the fact that SE didn't change raises a new, more subtle question about clustered-SE robustness to multicollinearity. |
| J2 (interaction p=0.085) | High | **High** (unchanged) | Still marginal, still vanishes in Col 2. This is the real problem. |
| J3 (sample differs from parent) | High | **High** (unchanged) | Valid and important. |
| J4 (Moulton problem) | Medium-High | **High** (upgrade) | With J1 resolved, J4 becomes the primary econometric concern. The call-level repetition of firm-year variables is the most actionable issue remaining. |
| J5 (no centering) | Medium | **Resolved** | Already implemented. |
| J6 (8.3% within-firm variation) | Medium | **Medium** (unchanged) | Valid concern for causal interpretation. |
| J7 (no robustness checks) | Medium | **High** (upgrade) | With the top Priority 1 fix already done, the absence of robustness checks is now the binding constraint for thesis readiness. |
| J8 (Nickell bias) | Medium | **Low** (downgrade) | With Industry FE (not Firm FE) and T=17, Nickell bias is negligible. The audit correctly notes this but still rates it Medium. |
| J9 (z-score on pre-regression sample) | Low-Medium | **Low-Medium** (unchanged) | Valid minor point. |
| J10 (summary stats on wrong sample) | Low-Medium | **Low-Medium** (unchanged) | Valid. |
| J11-J13 | Low | **Low** (unchanged) | Valid minor points. |

---

## I. Completeness Gaps

| # | Gap | Impact |
|---|-----|--------|
| I1 | **No verification of the new run (`2026-03-19_001554`).** The audit only verifies the old run. All coefficient values, R-squared figures, and verification checks in Section I need to be re-done against the current code's output. | High -- the audit's factual substrate is wrong for the moderator coefficient. |
| I2 | **No comparison between old and new runs.** The audit could have caught the centering update by comparing the two output directories. | Medium |
| I3 | **No check of whether the summary stats CSV includes the centered IV.** The new run's `summary_stats.csv` includes `Manager_Pres_Unc_c` (mean=0.0000, confirming centering), but the audit does not report this. | Low |
| I4 | **The audit does not verify the LaTeX table against the new run.** The moderator coefficient in the LaTeX table changed from 0.0283 to 0.0361, but the audit reports the old value. | Medium |
| I5 | **No discussion of what centering means for coefficient interpretation.** The moderator coefficient changes from 0.0283 to 0.0361 after centering. This is because the "main effect" of the moderator now represents the effect at the mean IV (0.863) rather than at IV=0. The audit should discuss this. | Medium |

---

## J. Reproducibility Red-Team

| Check | Result |
|-------|--------|
| Can the old run be reproduced? | **No** -- the code has been modified (centering added). Running the current code produces run `2026-03-19_001554` results, not the audit-referenced `2026-03-18_235755` results. The old run is an orphan artifact from a previous code version. |
| Can the new run be reproduced? | **Presumably yes** -- the current code should reproduce `2026-03-19_001554` given the same inputs. Not independently verified (would require running the code). |
| Are input hashes recorded? | **Yes** -- `run_manifest.json` includes panel and TNIC hashes. |
| Is the git commit recorded? | **Yes** -- but the audit references commit `8f5e929` which is the commit BEFORE the centering change. The current working tree has uncommitted modifications to `run_h1_1_cash_tsimm.py`. |
| Attrition table correctness | **Correct** -- identical across both runs (centering doesn't change sample). Verified: 112,968 -> 88,205 -> 86,807 -> 76,239. |

---

## K. Econometric Meta-Audit

### K1. Did the first-layer audit's econometric assessment hold up?

**Partially.** The structural criticisms are sound:

1. **Interaction fragility (J2):** Correct. p=0.085 is marginal and vanishes in Col 2. This is the suite's fundamental problem, and centering did not fix it (nor should it -- centering changes interpretability, not the interaction's t-stat).

2. **Moulton problem (J4):** Correct and well-articulated. The moderator is a firm-year variable repeated across ~3.85 calls. Firm-year collapse is the right robustness check.

3. **Multicollinearity (J1):** The diagnosis was correct for the old code, but the audit's PREDICTION was wrong. The audit claimed centering would reduce the interaction SE by "2-3x." In fact, centering had ZERO effect on the interaction SE (0.0052 in both runs). This is because:
   - The interaction coefficient and its SE are algebraically invariant to mean-centering of the IV in OLS (centering only changes the interpretation of the moderator's "main effect," not the interaction's test statistic).
   - The Corr(moderator, interaction) metric is misleading in clustered-SE contexts -- high pairwise correlation does not necessarily inflate cluster-robust SEs the way it inflates classical SEs.

   This is an important econometric subtlety that the audit missed. The multicollinearity concern was textbook-correct but practically irrelevant for inference on the interaction. It DID matter for interpretability of the moderator coefficient, which is now more meaningful.

4. **Sample composition (J3):** Correct. H1.1 has N=76k vs parent H1 N=55k. The parent main effect should be replicated on the H1.1 sample.

5. **Robustness (J7):** Correct. No robustness checks for a marginal result is a fatal gap for thesis submission.

### K2. Are the priority fixes still valid?

| Fix | Status | Still needed? |
|-----|--------|---------------|
| Priority 1.1: Mean-center IV | **Done** | No (already implemented). But the audit should note that centering did not change the interaction t-stat, only the moderator coefficient interpretation. |
| Priority 1.2: Firm-year collapse | Not done | **Yes** -- this is now the #1 priority. |
| Priority 1.3: Replicate parent effect on H1.1 sample | Not done | **Yes** -- still critical. |
| Priority 2.1: Alternative moderator (TNIC3HHI) | Not done | **Yes** -- useful robustness. |
| Priority 2.2: Subsample split | Not done | **Yes** -- useful robustness. |

---

## L. Audit-Safety Assessment

| Dimension | Assessment |
|-----------|------------|
| Could the audit mislead a committee? | **Yes.** A committee member reading J1 ("severe multicollinearity from non-centered IV") and M Priority 1 ("mean-center the IV -- this is a 1-line code change") would believe the code has a critical deficiency that has already been fixed. They might question why the author hasn't implemented such an obvious fix, damaging credibility unnecessarily. |
| Could the audit lead to incorrect code changes? | **Yes.** If someone follows Priority 1.1 literally ("add `df[IV] = df[IV] - df[IV].mean()` before line 261"), they would double-center the IV (since centering is already implemented), producing incorrect results. |
| Does the audit accurately represent the current state? | **No.** The audit describes a code version that no longer exists. The moderator coefficient, the variable name in the regression, and the function name are all different in the current code. |
| Is the audit's overall conclusion still valid? | **Partially.** "Not thesis-ready" is likely still correct due to marginal significance (p=0.085), absence of robustness checks, and Moulton concerns. But the specific reasons cited (multicollinearity, non-centered IV) are no longer applicable. |

---

## M. Master Issue Register

### Issues inherited from first-layer audit (still valid)

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| J2 | High | Interaction p=0.085, marginal, vanishes in Col 2 | Open -- fundamental limitation |
| J3 | High | Sample differs from parent (N=76k vs 55k); parent effect not replicated | Open -- needs replication check |
| J4 | High (upgraded) | Double Moulton: firm-year moderator repeated across calls | Open -- needs firm-year collapse |
| J7 | High (upgraded) | No robustness checks for a marginal result | Open -- blocking for thesis |
| J6 | Medium | Only 8.3% within-firm moderator variation | Open -- acknowledge |
| J8 | Low | Nickell bias under Industry FE with T=17 | Open -- minor; acknowledge |
| J9 | Low-Medium | z-score on pre-regression sample | Open -- minor |
| J10 | Low-Medium | Summary stats on Main sample, not regression sample | Open -- fix or document |
| J11-J13 | Low | Nonlinear moderation, TNIC alignment, heteroskedasticity | Open -- minor |

### Issues resolved since first-layer audit

| ID | Description | Resolution |
|----|-------------|------------|
| J1 | Multicollinearity from non-centered IV | Code now mean-centers IV (but SE unchanged -- multicollinearity was not materially inflating SEs under clustering) |
| J5 | IV not mean-centered before interaction | Implemented in current code |

### New issues identified by red-team

| ID | Severity | Description |
|----|----------|-------------|
| RT1 | **High** | First-layer audit is stale: describes code version that no longer exists. All moderator coefficients, line references, and the top issue are wrong. |
| RT2 | **Medium-High** | Audit's prediction that centering would reduce interaction SE by "2-3x" was empirically falsified (SE unchanged at 0.0052). The multicollinearity concern, while textbook-valid, was practically immaterial for interaction inference under clustering. Audit overstated this risk. |
| RT3 | **Medium** | Code-level inconsistency: `regression_results_col1.txt` header says `IV: Manager_Pres_Uncertainty_pct` but the parameter table shows `Manager_Pres_Unc_c`. Undiscovered by first-layer audit. |
| RT4 | **Medium** | Old run (`2026-03-18_235755`) is an orphan artifact -- cannot be reproduced from the current code. Audit references this run as the "verified run" but it corresponds to a code state that no longer exists in the working tree. |
| RT5 | **Low-Medium** | Audit's AR(1) claim is contradictory: Section A.3/MODEL_SPECS description says "AR(1) > 0.9" but verification check 18 says median=0.595. The value 0.595 appears to be the correct one. |

---

## N. What a Committee Wouldn't Know (From Reading Only the First-Layer Audit)

1. **The IV is already mean-centered.** The audit says it isn't. A committee member would wrongly believe this is an open deficiency.

2. **The moderator coefficient changed substantially after centering** (0.0283 to 0.0361). The committee would have incorrect coefficient values for the moderator's direct effect.

3. **Centering had zero effect on the interaction's significance.** The t-stat (1.7218), SE (0.0052), and p-value (0.0851) are identical pre- and post-centering. The committee would not know that the audit's #1 recommended fix was already implemented and had no effect on the key result.

4. **The multicollinearity concern was practically irrelevant** under cluster-robust inference. The committee would believe this is a severe problem requiring urgent action, when in fact the fix has already been applied with no change to the interaction estimate.

5. **There are TWO output runs** (`2026-03-18` and `2026-03-19`), and they differ in the moderator coefficient. The committee would not know which set of results to trust.

6. **The code-to-output documentation chain is broken.** The current code cannot reproduce the run cited in the audit. The verified run is from an earlier code version.

---

## O. Priority Fixes

### For the first-layer audit document itself

1. **[CRITICAL] Update the entire audit to reference the current code and latest run (`2026-03-19_001554`).** Update all coefficient values, line numbers, function names, and variable names. Remove J1 and J5 from the issue register or mark them as resolved. Update the Priority fixes to reflect what's already done.

2. **[CRITICAL] Correct the multicollinearity analysis.** Note that centering had no effect on the interaction SE. Revise the econometric discussion: the Corr(moderator, interaction) metric was misleading under clustering. Remove claims that centering would reduce the SE by "2-3x."

3. **[HIGH] Fix the AR(1) inconsistency.** The text says AR(1) > 0.9 in some places but the verification log says median=0.595. Reconcile.

4. **[MEDIUM] Document both runs and explain why the old run is superseded.** Or delete the old run's output directory to avoid confusion.

### For the H1.1 suite code

1. **[HIGH] Implement firm-year collapsed regression** as a robustness check. This is the #1 remaining issue.

2. **[HIGH] Replicate the parent main effect** on the H1.1 sample before the moderation table.

3. **[MEDIUM] Add at least one alternative moderator** (TNIC3HHI) or subsample split.

4. **[LOW] Fix the output file header inconsistency** (`IV: Manager_Pres_Uncertainty_pct` vs actual variable `Manager_Pres_Unc_c` in regression_results_col*.txt).

---

## P. Final Statement

The first-layer audit of H1.1 is a thorough, referee-grade econometric assessment that is undermined by a critical factual problem: it describes a version of the code that no longer exists. The audit's #1 issue (multicollinearity from non-centered IV) has been resolved in the current code, and its prediction that the fix would improve inference was empirically falsified -- the interaction SE and p-value are identical before and after centering.

The audit's deeper structural criticisms remain valid and important: the interaction is marginal (p=0.085), it vanishes in the lead specification, no robustness checks exist, and the Moulton problem from call-level repetition of firm-year variables is unaddressed. These issues, not multicollinearity, are the binding constraints for thesis readiness.

**Recommendation:** The first-layer audit must be rewritten against the current code before being shared with any committee member. In its current form, it would create confusion about which code/results are authoritative and would incorrectly identify solved problems as open deficiencies. After the doc is updated, the remaining open issues (firm-year collapse, parent-effect replication, robustness checks) should be the focus of pre-submission work.

**Audit-of-audit verdict:** Structurally excellent, factually stale, needs immediate revision.

---

## Revision History

- **2026-03-21 (v1):** Initial red-team audit. Identified code-audit version mismatch as primary deficiency. 5 new issues (RT1-RT5), 2 resolved issues (J1, J5), severity recalibration on 3 issues.
