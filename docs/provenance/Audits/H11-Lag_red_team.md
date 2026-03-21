# H11-Lag Red-Team Audit (Second Layer)

**Suite ID:** H11-Lag
**Red-team date:** 2026-03-21
**First-layer doc:** `docs/provenance/H11-Lag.md`
**Method:** Independent code inspection against all first-layer claims

---

## A. Red-Team Bottom Line

The first-layer audit is **substantially correct** in its core findings and appropriately skeptical on identification concerns. It correctly identifies the two most important issues (false standardization claim in LaTeX, incomplete latest run) and raises valid econometric concerns (omitted lagged DV, multiple testing). However, the audit contains **three factual errors of its own**, **one missed code-level issue**, and **one under-severity rating**. After correction, the overall readiness verdict (CONDITIONAL) remains appropriate.

---

## B. Scope and Objects Audited

| Object | Path | Audited by L1 | Verified by L2 |
|--------|------|---------------|----------------|
| Runner | `src/f1d/econometric/run_h11_prisk_uncertainty_lag.py` | Yes | Yes |
| Panel builder | `src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py` | Yes | Yes |
| PRiskQLagBuilder | `src/f1d/shared/variables/prisk_q_lag.py` | Yes | Yes |
| PRiskQLag2Builder | `src/f1d/shared/variables/prisk_q_lag2.py` | Yes | Yes |
| CompustatEngine (firm_maturity, ROA) | `src/f1d/shared/variables/_compustat_engine.py` | Partially | Spot-checked |
| panel_utils (assign_industry_sample) | `src/f1d/shared/variables/panel_utils.py` | Yes | Yes |
| winsorization.py | `src/f1d/shared/variables/winsorization.py` | Yes | Spot-checked |
| LaTeX table generation | Runner lines 260-400 | Yes | Yes |

---

## C. Audit-of-Audit Scorecard

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Factual accuracy | 4 | Three factual errors found (firm_maturity label, docstring error missed, n_clusters source) |
| Completeness | 4 | Missed one code-level issue (LaTeX stars based on one-tailed p without disclosure), missed docstring bug |
| Appropriate skepticism | 5 | Identification concerns (omitted lagged DV, multiple testing, cluster count) are well-reasoned |
| Severity calibration | 4 | One under-severity (LaTeX star basis); otherwise well-calibrated |
| Reproducibility guidance | 4 | Commands and prerequisites are correct; minor gap on version pinning specifics |
| Econometric rigor | 5 | Correctly identifies all major inference concerns; economic magnitude calculation is valuable |

**Overall L1 quality: 4.3 / 5** -- A strong first-layer audit with minor factual issues that do not undermine its conclusions.

---

## D. Claim Verification Matrix

| L1 Claim | L1 Location | Verified | Method | Finding |
|----------|-------------|----------|--------|---------|
| 24 regressions (4 DV x 3 samples x 2 IV) | Section A | CONFIRMED | Code: CONFIG dict lines 88-98 | Correct |
| Panel index is (gvkey, year) | Section A | CONFIRMED | Runner line 200: `df_panel = df_sample.set_index(["gvkey", "year"])` | Correct |
| Entity + Time FE, clustered by entity | Section H3 | CONFIRMED | Runner lines 203-204 | Correct |
| One-tailed test: p_two/2 when beta > 0 | Section H4 | CONFIRMED | Runner lines 224-225 | Correct |
| PRES_CONTROL_MAP adds presentation control for QA DVs | Section A | CONFIRMED | Runner lines 112-117 | Correct |
| Min-calls filter >= 5 | Section A | CONFIRMED | Runner lines 523-528, CONFIG line 89 | Correct |
| Skip spec if < 100 obs | Section A | CONFIRMED | Runner line 534 | Correct |
| BookLev built but unused by runner | Section E5 / J-01 | CONFIRMED | Panel builder line 111 (BookLevBuilder), runner columns list 445-468 excludes BookLev | Correct |
| `_get_prev_quarter`: 2010q1 -> 2009q4 | Section I | CONFIRMED | prisk_q_lag.py lines 73-77 | Correct |
| `_get_prev2_quarter`: 2010q1 -> 2009q3, 2010q2 -> 2009q4 | Section I | CONFIRMED | prisk_q_lag2.py lines 73-80 | Correct |
| PRisk dedup keeps max | Section D3 / J-02 | CONFIRMED | prisk_q_lag.py lines 110-113 | Correct |
| PRisk winsorization: per-year 1%/99% | Section G1 | CONFIRMED | prisk_q_lag.py line 165, winsorize_by_year defaults lower=0.01, upper=0.99 | Correct |
| LaTeX notes claim "All continuous controls are standardized" | Section K6 / I-02 | CONFIRMED | Runner line 396 | Correct |
| Zero row-delta enforced in panel builder | Section E1 | CONFIRMED | Panel builder lines 142-147 | Correct |
| `firm_maturity = req / atq` | Section K4 | CONFIRMED | _compustat_engine.py lines 848-849 | Correct formula, but L1 labels it "RE / TE" which is wrong (see Section E) |
| `ROA = iby_annual / avg_assets` | Section A | CONFIRMED | _compustat_engine.py lines 1059-1061 | Correct |
| FF12==11 -> Finance, FF12==8 -> Utility | Section A | CONFIRMED | panel_utils.py lines 53-55 | Correct |
| Year filter uses min_year - 1 for lag builder | Section E2 | CONFIRMED | prisk_q_lag.py line 107 | Correct |
| Year filter uses min_year - 1 AND min_year - 2 for lag2 builder | Section E3 | CONFIRMED | prisk_q_lag2.py line 110 | Correct |

---

## E. Unsupported Claims

| ID | L1 Claim | L1 Location | Finding |
|----|----------|-------------|---------|
| E-01 | `firm_maturity` is "RE / TE (req / atq)" | Sections A, F, I-07 | **Internally contradictory.** `req / atq` is retained earnings / total assets (RE/TA), not RE/TE (retained earnings / total equity, which would be `req / seqq`). The formula in parentheses is correct; the label "RE / TE" is wrong. This same error was already identified and flagged in the archived H3 audit (`docs/provenance/_archived/H3.md`) and the H11 red-team (`docs/provenance/H11_red_team.md`), suggesting it was copy-pasted without correction. |
| E-02 | Audit doc Section I says `_get_prev2_quarter` examples are "2010q1->2009q3, 2010q2->2009q4, etc." | Section I verification log | These examples are correct, but the audit FAILS to note the docstring bug in `prisk_q_lag2.py` line 71: the docstring says `"2010q3" -> "2009q1"` but the code returns `"2010q1"`. The audit claims to have verified the function but missed the docstring error. |

---

## F. False Positives

None identified. All issues raised by the first-layer audit are genuine.

---

## G. Missed Issues

| ID | Severity | Description | Code Location |
|----|----------|-------------|---------------|
| G-01 | **LOW** | `_get_prev2_quarter` docstring example is wrong: says `"2010q3" -> "2009q1"` but code correctly returns `"2010q1"`. The code logic is correct; only the docstring is wrong. | `prisk_q_lag2.py` line 71 |
| G-02 | **MEDIUM** | LaTeX table stars use one-tailed p-values (`beta_prisk_p_one`) but neither the table notes nor the table itself disclose this. Standard academic convention assumes two-tailed p-values unless explicitly stated. A reader would interpret `***` as p<0.01 two-tailed when the actual threshold is p<0.01 one-tailed (equivalent to p<0.02 two-tailed). This overstates significance. | Runner lines 287-297 (star thresholds) called with `r_mq_1['beta_prisk_p_one']` at lines 327-330 |
| G-03 | **LOW** | `n_firms` and `n_clusters` in the metadata dict (runner lines 244-245) are computed from `df_sample` (the input parameter), which is actually `df_filtered`. However, PanelOLS with `drop_absorbed=True` may drop additional singleton entities, meaning `model.nobs` could correspond to fewer entities than `df_sample["gvkey"].nunique()`. The correct cluster count should come from the model object, not the input DataFrame. | Runner lines 244-245 vs. line 243 (`model.nobs`) |

---

## H. Severity Recalibration

| L1 Issue | L1 Severity | Recommended Severity | Rationale |
|----------|-------------|---------------------|-----------|
| I-02 (false standardization claim) | HIGH | HIGH | Agree. This is a factual error in a submitted artifact. |
| I-01 (incomplete latest run) | HIGH | MEDIUM | The 24/24 regression files exist. The missing files (diagnostics CSV, LaTeX table, attrition table) are post-hoc aggregation artifacts. The core results are present. A re-run resolves this trivially. |
| I-03 (no lagged DV control) | MEDIUM | MEDIUM | Agree. Standard concern for lag designs. |
| I-04 (no multiple-testing correction) | MEDIUM | MEDIUM | Agree. 24 tests at alpha=0.05 one-tailed. |
| I-05 (no standardized coefficients) | MEDIUM | MEDIUM | Agree. |
| G-02 (LaTeX stars based on one-tailed p) | Not flagged | **MEDIUM** | Star thresholds applied to one-tailed p-values without disclosure is a non-trivial presentation issue. A coefficient with two-tailed p=0.015 would receive `**` (since one-tailed p=0.0075 < 0.01), which readers would interpret as p<0.01 two-tailed. |
| I-06 (unused BookLev) | LOW | LOW | Agree. |
| I-07 (firm_maturity naming) | LOW | LOW | Agree, but the audit itself propagates the error by calling it "RE/TE." |
| I-08 (winsorization asymmetry) | LOW | LOW | Agree. |
| I-09 (panel structure) | INFO | INFO | Agree. |

---

## I. Completeness Gaps

| ID | Gap | Impact |
|----|-----|--------|
| I-01 | The audit does not trace the `file_name` column through the merge chain to verify there are no spurious duplicates created by the PRisk merge step (prisk_q_lag.py lines 169-184). The builder does a left merge then `drop_duplicates(subset=["file_name"])`, which silently drops rows if the merge inflates the row count. If a single file_name matches multiple PRisk rows (e.g., due to gvkey ambiguity), the dedup keeps only the first match, which is arbitrary. | Low -- defensive code, but the audit should have noted the arbitrary selection mechanism. |
| I-02 | The audit does not examine whether the `generate_attrition_table` function (runner line 565) correctly computes attrition. The function receives `len(panel)` as the starting count, but this is the full panel including Finance and Utility samples, while the Main sample filter step correctly reports `(panel["sample"] == "Main").sum()`. The attrition table's first row is thus "Master manifest: 112,968" which is the total panel, not the manifest count before any variable construction. | Low -- presentation issue only. |
| I-03 | The audit does not verify that the `prepare_regression_data` function (runner line 172) applies `dropna` on all `required` columns simultaneously, meaning a firm missing only one control is dropped entirely. No sensitivity analysis for alternative missing-data strategies is discussed. | Info -- standard complete-case approach, but worth noting. |

---

## J. Reproducibility Red-Team

| Check | Result |
|-------|--------|
| Can Stage 3 be run from documented command? | Yes: `python -m f1d.variables.build_h11_prisk_uncertainty_lag_panel` |
| Can Stage 4 be run from documented command? | Yes: `python -m f1d.econometric.run_h11_prisk_uncertainty_lag` |
| Are all input paths documented? | Yes |
| Are all output paths documented? | Yes |
| Is random seed documented? | Yes (42 via project.yaml), though PanelOLS is deterministic regardless |
| Are package versions pinned? | **No** -- the audit correctly flags this (K7.3) but does not list specific version sensitivity risks |
| Is the panel builder deterministic? | Yes, assuming upstream inputs are fixed |
| Is the runner deterministic? | Yes |

---

## K. Econometric Meta-Audit

The first-layer audit's econometric assessment (Section K) is well-constructed and raises the right concerns. Specific verification:

1. **Identification critique (K1):** Correct. The lag design mitigates same-transcript confounding but does not address persistent within-entity communication style. Entity FE remove levels but not autocorrelated trends. The suggestion to add lagged DV is appropriate.

2. **Cluster count concern (K2):** Correct. Finance (~20K calls) and Utility (~4K calls) subsamples may have insufficient clusters for reliable inference. The audit should have provided estimated cluster counts per subsample (Finance likely ~500-600 firms, Utility likely ~100-150 firms -- both above the 50-cluster rule of thumb, but Utility is closer to the boundary after min-calls filtering).

3. **Economic magnitude (K3.1):** The audit's calculation is valuable: a 1-SD increase in PRisk (~147) increases Manager_QA_Uncertainty_pct by ~0.006 pp, which is ~0.8% of the mean. This is indeed economically small and would be a natural referee question.

4. **Multiple testing (K2):** Correct framing. 24 tests, no correction.

5. **One-tailed test justification (K2):** Appropriately skeptical. The one-tailed test requires a strong theoretical prior.

**Additional econometric concern not raised by L1:** The panel is indexed by (gvkey, year) but has multiple observations per cell (quarterly calls). PanelOLS entity FE are at the gvkey level and time FE at the year level. This means within-year variation across quarters is not absorbed by time FE. If there are common quarterly shocks (e.g., election quarters), these could confound the PRisk-uncertainty relationship. The audit mentions this structure (I-09) but rates it INFO without discussing the quarterly shock implication.

---

## L. Audit-Safety Assessment

| Dimension | Assessment |
|-----------|------------|
| Does the audit create false confidence? | No. The CONDITIONAL verdict is appropriate. |
| Does the audit miss any thesis-blocking issue? | No. The false standardization claim (I-02) is correctly identified as must-fix. G-02 (one-tailed stars without disclosure) is thesis-relevant but correctable with a single line edit. |
| Could a committee member find a fatal flaw not in the audit? | Unlikely for mechanical issues. The omitted lagged DV (I-03) and economic magnitude question (K3.1) are the most likely referee pushback points, and both are documented. |
| Is the audit internally consistent? | Mostly. The `firm_maturity` label error (E-01) is an internal inconsistency within the audit itself. |

---

## M. Master Red-Team Issue Register

| ID | Source | Severity | Description | Status |
|----|--------|----------|-------------|--------|
| RT-01 | E-01 | LOW | First-layer audit labels `firm_maturity` as "RE / TE" in three places but the formula is `req / atq` = RE/TA. The audit's parenthetical formula is correct; the label is wrong. | L1 audit doc error -- correct in output doc |
| RT-02 | E-02 | LOW | First-layer audit claims verification of `_get_prev2_quarter` but misses docstring bug: line 71 of `prisk_q_lag2.py` says "2010q3 -> 2009q1" when code returns "2010q1". | Missed by L1 |
| RT-03 | G-01 | LOW | Docstring bug in `_get_prev2_quarter` (code is correct, docstring example is wrong). | New finding |
| RT-04 | G-02 | MEDIUM | LaTeX table stars use one-tailed p-values without disclosure in table notes. Readers would assume two-tailed convention. | New finding -- must fix |
| RT-05 | G-03 | LOW | `n_firms`/`n_clusters` in metadata may overcount if PanelOLS drops absorbed entities. | New finding |
| RT-06 | H (I-01) | MEDIUM | Recalibrated from HIGH to MEDIUM. Core regression files (24/24) are present; missing files are post-hoc aggregation artifacts. | Severity adjustment |
| RT-07 | L1 I-02 | HIGH | False "standardized" claim in LaTeX notes. Confirmed at runner line 396. | Confirmed -- must fix |
| RT-08 | L1 I-03 | MEDIUM | No lagged DV control. Confirmed as valid concern. | Confirmed |
| RT-09 | L1 I-04 | MEDIUM | No multiple-testing correction across 24 regressions. | Confirmed |
| RT-10 | L1 I-05 | MEDIUM | No standardized coefficients reported. | Confirmed |

---

## N. What Committee Wouldn't Know

From the first-layer audit alone, a committee member would NOT know:

1. **Stars may overstate significance.** The LaTeX table applies star thresholds to one-tailed p-values without disclosing this convention. A coefficient shown as `***` (p<0.01 one-tailed) could have a two-tailed p-value as high as 0.02. This is a presentation integrity issue (RT-04).

2. **The `firm_maturity` label in the audit is wrong.** The audit says "RE / TE" (retained earnings / total equity) three times, but the code computes RE / TA (retained earnings / total assets). A committee member reading the audit might form incorrect expectations about what this control captures (RT-01).

3. **The `_get_prev2_quarter` function has a docstring bug.** While the code is correct, the docstring would mislead any reviewer reading the source code directly (RT-03).

4. **Metadata cluster counts may be slightly inflated** relative to the actual estimation sample after PanelOLS drops absorbed entities (RT-05).

---

## O. Priority Fixes

### Must-fix before submission

1. **RT-07 / I-02:** Remove or correct "All continuous controls are standardized" from runner line 396. This is a factual error in a submitted LaTeX artifact.
2. **RT-04 / G-02:** Either (a) change LaTeX stars to use two-tailed p-values, or (b) add explicit note to the table: "Significance levels based on one-tailed tests." One line edit in runner.

### Should-fix

3. **RT-06 / I-01:** Re-run Stage 4 to regenerate model_diagnostics.csv, LaTeX table, and attrition table.
4. **RT-08 / I-03:** Add lagged DV as robustness specification.
5. **RT-10 / I-05:** Report standardized coefficients.
6. **RT-09 / I-04:** Discuss multiple-testing correction in paper text.

### Nice-to-fix

7. **RT-01:** Correct `firm_maturity` label in provenance doc from "RE / TE" to "RE / TA."
8. **RT-03:** Fix docstring in `prisk_q_lag2.py` line 71.
9. **RT-05:** Compute `n_clusters` from model object rather than input DataFrame.

---

## P. Final Red-Team Readiness Statement

**Readiness: CONDITIONAL -- same verdict as L1, with one additional must-fix.**

The first-layer audit is a strong document that correctly identifies the most important mechanical and econometric issues in the H11-Lag suite. Its CONDITIONAL verdict is appropriate. The red-team adds one additional must-fix item (RT-04: LaTeX stars based on undisclosed one-tailed p-values) that requires a single-line code edit or a single-line table note addition.

After resolving RT-07 (false standardization claim) and RT-04 (star basis disclosure), the H11-Lag suite is mechanically sound for thesis submission. The econometric concerns (omitted lagged DV, multiple testing, economic magnitude) are legitimate robustness suggestions that strengthen but do not block the submission.

The first-layer audit earned a quality score of 4.3/5. Its main weakness is three instances of propagating the `firm_maturity` "RE/TE" label error from earlier audit documents, and failing to catch the `_get_prev2_quarter` docstring bug despite claiming to have verified the function. These are minor issues that do not undermine the audit's core conclusions.
