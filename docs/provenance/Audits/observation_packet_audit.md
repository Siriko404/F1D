# Audit: Observation Packet & Result Surface Map

**Audit date:** 2026-03-19
**Scope:** Cross-reference every factual claim in the observation packet (Sections A–D) against the actual codebase (`src/f1d/econometric/run_h*.py`) and model diagnostics (`outputs/econometric/*/2026-03-18_*/model_diagnostics.csv`).

**Methodology:** Every significance claim, test-type label, column mapping, and structural assertion was verified against (a) the runner source code and (b) the stored `model_diagnostics.csv` files from the most recent run (2026-03-18).

---

## SEVERITY LEGEND

| Severity | Meaning |
|----------|---------|
| **CRITICAL** | Factual error that invalidates a promoted finding or reverses a claim |
| **HIGH** | Material mischaracterization that could mislead interpretation |
| **MEDIUM** | Incomplete or imprecise claim that omits relevant information |
| **LOW** | Minor imprecision with no material impact |

---

## 1. SECTION A — RESULT SURFACE MAP AUDIT

### 1.1 Table Structure Claims

| Suite | Claim | Actual | Verdict |
|-------|-------|--------|---------|
| H1 | 8-column table | 8 columns: 4 IVs simultaneous, 2 DVs × 2 FE × 2 controls | **CORRECT** |
| H2 | 8-column table | 8 columns: same structure as H1 | **CORRECT** |
| H4a | 8-column table (BookLev) | Runner produces 16 models; `generate_all_tables.py` splits into h4a (BookLev, cols 1–8) and h4b (DebtToCapital, cols 9–16 renumbered to 1–8) | **CORRECT** |
| H4b | 8-column table (DebtToCapital) | Same runner, second table | **CORRECT** |
| H5 | 4-column table | 4 columns, single DV (PostCallDispersion), no lead | **CORRECT** |
| H7 | 4-column table | 4 columns, single DV (delta_amihud), no lead | **CORRECT** |
| H12 | 8-column table | 8 columns: 2 DVs (PayoutRatio, PayoutRatio_lead) × 2 FE × 2 controls | **CORRECT** |
| H13 | 8-column table | 8 columns: 2 DVs (CapexAt, CapexAt_lead) × 2 FE × 2 controls | **CORRECT** |
| H14 | 4-column table | 4 columns, single DV (DSPREAD), no lead | **CORRECT** |
| H15 | 4-column table | 4 columns, single DV (REPO_callqtr), no lead | **CORRECT** |

### 1.2 Column Structure Claims

**Claim:** 8-column tables follow (1)/(5) = Industry FE baseline, (2)/(6) = Firm FE baseline, (3)/(7) = Industry FE extended, (4)/(8) = Firm FE extended.

**Actual:** Verified from all runners. Odd columns = Industry FE, even columns = Firm FE. Cols 1–2/5–6 = base controls, cols 3–4/7–8 = extended controls.

**Verdict:** **CORRECT.**

### 1.3 IV Block Claims

**Claim:** Most tables use 4 call-level IVs; H12 switches to averaged annual-style IVs.

**Actual:** H12 uses `Avg_CEO_QA_Uncertainty_pct`, `Avg_CEO_Pres_Uncertainty_pct`, `Avg_Manager_QA_Uncertainty_pct`, `Avg_Manager_Pres_Uncertainty_pct` at the firm-fiscal-year level. All other suites use call-level IVs.

**Verdict:** **CORRECT.**

### 1.4 Test Type Claims — CRITICAL ERROR FOUND

**Claim:** "h1, h2, h5, h7, h14 use one-tailed IV tests; h4a, h4b, h12, h13, h15 use two-tailed tests."

**Actual verification from runner source code:**

| Suite | Document claims | Actual test type | Direction | Verdict |
|-------|----------------|-----------------|-----------|---------|
| H1 | One-tailed | One-tailed (β > 0) | Match | **CORRECT** |
| H2 | One-tailed | One-tailed (β < 0) | Match | **CORRECT** |
| H4 | Two-tailed | Two-tailed | Match | **CORRECT** |
| H5 | One-tailed | One-tailed (β > 0) | Match | **CORRECT** |
| H7 | One-tailed | One-tailed (β > 0) | Match | **CORRECT** |
| **H12** | **Two-tailed** | **One-tailed (β < 0)** | **MISMATCH** | **CRITICAL ERROR** |
| H13 | Two-tailed | Two-tailed | Match | **CORRECT** |
| H14 | One-tailed | One-tailed (β > 0) | Match | **CORRECT** |
| H15 | Two-tailed | Two-tailed | Match | **CORRECT** |

**Evidence:** `run_h12_div_intensity.py` contains:
- `"Hypothesis Test (one-tailed): H12: beta < 0 -- higher uncertainty language -> lower payout ratio."`
- `"Stars based on one-tailed p-values."`
- LaTeX notes: `$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed; H12: $\beta < 0$).`
- One-tailed p-value computation: `p_one = p_two / 2 if beta < 0 else 1 - p_two / 2`

**Severity: CRITICAL.** This error propagates into Finding F4 (see Section 2.4 below).

---

## 2. SECTION B — PROMOTED FINDINGS AUDIT

### 2.1 Finding F1: Manager-side cash-holdings signature

**Claim:** "Manager_Pres significant in h1 cols 1, 3, 5, 7; Manager_QA significant in cols 2, 4 only; CEO rows null."

**Actual from model_diagnostics.csv (one-tailed, β > 0):**

| IV | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
|----|-------|-------|-------|-------|-------|-------|-------|-------|
| Manager_Pres | +*** p=0.003 | ns | +*** p=0.004 | ns | +*** p=0.009 | ns | +** p=0.014 | ns |
| Manager_QA | ns | +*** p=0.002 | ns | +*** p=0.001 | ns | ns | ns | ns |
| CEO_Pres | ns (−, wrong sign) | ns | ns | ns | ns | ns | ns | ns |
| CEO_QA | ns | ns | ns | ns | ns | ns | ns | ns |

**Verdict:** Significance claims are **CORRECT**. Column mapping is accurate. Manager_Pres is significant in all four industry-FE columns (1, 3, 5, 7). Manager_QA is significant only in contemporaneous firm-FE columns (2, 4). CEO rows are null under the one-tailed positive test.

**Confidence grade B:** Justified. The pattern is repeated but FE-dependent.

### 2.2 Finding F2: CEO-presentation leverage signature

**Claim:** "CEO_Pres significant in h4a and h4b cols 1, 3, 5, 7; matching firm-FE cols 2, 4, 6, 8 are null. CEO_QA only weakly negative contemporaneously, and manager-presentation coefficients are null."

**Actual from model_diagnostics.csv (two-tailed):**

**BookLev (h4a):**

| IV | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
|----|-------|-------|-------|-------|-------|-------|-------|-------|
| CEO_Pres | +*** p=0.006 | ns | +** p=0.021 | ns | +*** p=0.004 | ns | +** p=0.016 | ns |
| CEO_QA | −* p=0.096 | ns | −* p=0.097 | ns | ns | ns | ns | ns |
| **Mgr_QA** | **+** p=0.041** | ns | **+* p=0.058** | ns | ns | ns | ns | ns |
| Mgr_Pres | ns | ns | ns | ns | ns | ns | ns | ns |

**DebtToCapital (h4b):**

| IV | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
|----|-------|-------|-------|-------|-------|-------|-------|-------|
| CEO_Pres | +** p=0.017 | ns | +** p=0.040 | ns | +** p=0.016 | ns | +* p=0.052 | ns |
| CEO_QA | −* p=0.099 | ns | −* p=0.098 | ns | ns | ns | ns | ns |
| Mgr_QA | ns | ns | ns | ns | ns | ns | ns | ns |
| Mgr_Pres | ns | ns | ns | ns | ns | ns | ns | ns |

**Verdict: MEDIUM — omission of Manager_QA significance in BookLev.**

The CEO_Pres pattern is correctly reported. However, the document states "manager-presentation coefficients are null" — this is correct for Manager_Pres, but the document **omits** that **Manager_QA is significantly positive** in BookLev cols 1 (p=0.041) and 3 (p=0.058). This is a secondary finding within the leverage surface that the observation packet fails to capture.

Additionally, CEO_QA is weakly negative in contemporaneous industry-FE columns for BOTH BookLev and DebtToCapital — this is correctly characterized as "weakly negative contemporaneously."

### 2.3 Finding F3: Manager-Q&A CapEx signature

**Claim:** "Manager_QA significant in h13 cols 1, 3, 5, 7; matching firm-FE cols 2, 4, 6, 8 are null."

**Actual from model_diagnostics.csv (two-tailed):**

| IV | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
|----|-------|-------|-------|-------|-------|-------|-------|-------|
| Mgr_QA | +*** p=0.005 | ns | +*** p=0.001 | ns | +*** p=0.001 | ns | +*** p=0.000 | ns |
| CEO_QA | ns | +* p=0.056 | ns | +* p=0.084 | ns | ns | ns | ns |
| CEO_Pres | ns | ns | ns | ns | ns | ns | ns | ns |
| Mgr_Pres | ns | ns | ns | ns | ns | ns | ns | ns |

**Verdict:** Manager_QA pattern is **CORRECT**. The document also correctly notes "CEO-Q&A is only weakly positive in contemporaneous firm-FE columns" — verified at p=0.056 and p=0.084.

**Confidence grade B:** Justified.

### 2.4 Finding F4: Lead-only payout-ratio signal — CRITICAL ERROR

**Claim:** "Averaged CEO presentation uncertainty is positive only for t+1 payout ratio and only under firm FE, with significance in both base and extended-control columns [cols 6 and 8]."

**Actual from model_diagnostics.csv:**

```
Col 6: Avg_CEO_Pres beta=+0.0706, p_two=0.0279, p_one(β<0)=0.9860
Col 8: Avg_CEO_Pres beta=+0.0693, p_two=0.0311, p_one(β<0)=0.9844
```

**The document claims H12 uses two-tailed tests (Section A). The runner actually uses one-tailed (β < 0).**

Under the actual one-tailed test (H12: β < 0), the positive coefficient gives p_one ≈ 0.986. This is **not significant at any conventional level**. The coefficient is in the **opposite direction** of the hypothesis.

**This means:**
1. The Avg_CEO_Pres result in cols 6 and 8 is a **counter-hypothesis result** — positive when the test expects negative.
2. Under the one-tailed stars used in the LaTeX table, these cells show **no significance stars**.
3. **Finding F4 as stated is INVALID.** It promotes a result that is significant two-tailed but runs counter to the stated hypothesis direction.

**Severity: CRITICAL.** The observation packet misclassifies H12's test type and then promotes a counter-directional result as a finding. Either:
- (a) The test direction was wrong in the runner (should be two-tailed or β > 0), in which case the runner needs fixing and F4 stands on different grounds, OR
- (b) The test direction is correct (β < 0), in which case the positive CEO_Pres result is a null/counter-hypothesis result and F4 must be retracted.

### 2.5 Finding F5: Disagreement vs trading-friction

**Claim (H5 part):** "CEO_Pres_Uncertainty_pct is positive and significant in cols 1, 2 but not 3, 4."

**Actual:**

| IV | Col 1 | Col 2 | Col 3 | Col 4 |
|----|-------|-------|-------|-------|
| CEO_Pres | +*** p=0.004 | +** p=0.042 | ns | ns |
| **Mgr_Pres** | ns | **+** p=0.026** | ns | ns |
| CEO_QA | ns | ns | ns | ns |
| Mgr_QA | ns | ns | ns | ns |

**Verdict: MEDIUM — omission.** The CEO_Pres pattern is correctly reported. However, the document **omits Manager_Pres significance in col 2** (p=0.026, one-tailed). This is a second significant IV in the baseline firm-FE specification that the observation packet fails to report.

**Claim (H7 part):** "All four uncertainty rows are non-significant in all four columns."

**Actual:** All IVs null across all 4 columns.

**Verdict:** **CORRECT.**

**Claim (H14 part):** "Significance appears only in small manager-side pockets (Manager_Pres in cols 2, 3; Manager_QA in col 3) with no full-spec repetition."

**Actual:**

| IV | Col 1 (N=57,044) | Col 2 (N=57,044) | Col 3 (N=39,074) | Col 4 (N=39,074) |
|----|-------|-------|-------|-------|
| Mgr_Pres | ns | +*** p=0.009 | +*** p=0.000 | ns |
| Mgr_QA | ns | ns | +*** p=0.000 | ns |
| CEO_Pres | ns | ns | ns | ns |
| CEO_QA | ns | ns | ns | ns |

**Verdict: HIGH — misleading characterization.**

The column assignments are correct (Manager_Pres in cols 2, 3; Manager_QA in col 3). However:

1. **"Tiny, isolated cells" is misleading.** Both Mgr_QA and Mgr_Pres are significant at p<0.001 in col 3. Mgr_Pres is significant at p=0.009 in col 2. These are not "tiny" — they are strongly significant.
2. **"No full-spec repetition" is debatable.** Manager_Pres IS significant in both col 2 (firm FE, base) AND col 3 (industry FE, extended). These are two different FE/control combinations. That constitutes repetition across spec dimensions, even though it's not repetition within the same FE or the same control set.
3. The sharp N drop from cols 1–2 (57,044) to cols 3–4 (39,074) — a 31% reduction — is correctly noted in the artifact flags but not adequately weighted in the interpretation. The extended-control significance may be a different-sample effect rather than a control-set effect.

---

## 3. SECTION C — DISCARD BIN AUDIT

### 3.1 D1: Investment residual

**Claim:** "CEO_Pres is negative only in limited cells; Manager_QA is negative only in contemporaneous industry-FE columns."

**Actual (one-tailed, β < 0):**

| IV | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
|----|-------|-------|-------|-------|-------|-------|-------|-------|
| CEO_Pres | −** p=0.029 | ns | ns | ns | −* p=0.085 | −* p=0.095 | ns | ns |
| Mgr_QA | −* p=0.095 | ns | −** p=0.015 | ns | ns | ns | ns | ns |

**Verdict: LOW.** The description is roughly accurate. CEO_Pres shows some lead-spec significance (cols 5, 6) that could be noted. The "keep under watch: Yes" designation is appropriate given the scattered but non-trivial signals.

### 3.2 D2: Bid-ask spread

**Claim:** "Bid-ask spread changes are driven by tiny isolated manager-side coefficients rather than a repeated pattern."

**Verdict: HIGH — misleading.** As documented in F5 audit above, the significance levels are p<0.001 (not "tiny"), and Manager_Pres appears in two different specification combinations (cols 2, 3). The "keep under watch: No" designation may be premature given the strength of the col 3 extended-controls result. See F5 audit for details.

### 3.3 D3: Share repurchase

**Claim:** "All H15 uncertainty coefficients are non-significant."

**Actual:** All IVs null across all 4 columns (two-tailed).

**Verdict:** **CORRECT.** Discard justified.

### 3.4 D4: CEO-Q&A leverage

**Claim:** "Negative CEO_QA leverage coefficients appear only in contemporaneous industry-FE columns and disappear elsewhere."

**Actual:** CEO_QA is negative at p≈0.097 in BookLev cols 1, 3 and DebtToCapital cols 9, 11 (all contemporaneous, industry FE). Disappears in lead and firm FE.

**Verdict:** **CORRECT.** Discard justified — dominated by the stronger CEO_Pres pattern.

---

## 4. SECTION D — OBSERVATION PACKET STRUCTURAL AUDIT

### 4.1 Comparison margin completeness

The observation packet defines comparison margins for each finding. These are generally well-structured but:

- **F2 omits the peer-IV margin for Manager_QA.** Manager_QA is significant in BookLev industry-FE columns (p=0.041, 0.058), but the finding's peer_axis says "CEO_Pres_vs_other_uncertainty_rows" without noting that one "other" row is itself significant.

- **F5's H14 characterization conflicts with the data.** The finding says the spread result is "isolated" when Manager_Pres spans two specification types.

### 4.2 Artifact flags

The artifact flags are consistent across findings:
- `differential N across columns` — verified: all suites show N reductions in extended-control columns.
- `complete-case attrition` — appropriate flag.
- `timing-construction asymmetry` — appropriate for suites with lead DVs.
- `incomplete breakdown of attrition in outputs` — verified: most runners do not produce detailed attrition tables.
- `annual-vs-call-level mismatch` for H12 — correctly flagged.

### 4.3 Confidence grades

| Finding | Assigned | Reassessment | Reason |
|---------|----------|-------------|--------|
| F1 | B | **B** — no change | Pattern is well-replicated across cols, correctly noted as FE-dependent |
| F2 | B | **B** — no change | Strong CEO_Pres repetition; omission of Mgr_QA is a documentation issue, not a grade issue |
| F3 | B | **B** — no change | Strong Mgr_QA repetition across all industry-FE cols |
| F4 | B | **RETRACT or downgrade to D** | Test-type error invalidates the promoted pattern (see §2.4) |
| F5 | C | **C** — no change | Fragile by design; H14 undercharacterization doesn't change overall C grade |

---

## 5. CRITICAL FINDINGS SUMMARY

### CRITICAL-1: H12 Test Type Misclassification → F4 Invalid

**What happened:** The observation packet states H12 uses two-tailed tests. The actual runner uses one-tailed (β < 0). The promoted F4 finding (Avg_CEO_Pres positive in cols 6, 8) is two-tailed-significant but **counter-directional** to the hypothesis. Under the actual one-tailed test, the p-values are 0.986 (not significant).

**Impact:** Finding F4 must be retracted or the H12 test direction must be reconsidered. If the economic theory permits a positive relationship (higher uncertainty → higher payout), the runner's test direction should be changed to two-tailed or β > 0, and F4 would stand on different grounds.

**Required action:** Decide whether H12's hypothesis direction (β < 0) is correct. If yes, F4 is invalid. If the direction should be reconsidered, the runner needs updating.

### HIGH-1: H14 Significance Undercharacterized

**What happened:** Manager_Pres and Manager_QA show p<0.001 significance in H14 col 3, and Manager_Pres shows p=0.009 in col 2. The document dismisses these as "tiny, isolated cells" and discards H14 from findings.

**Impact:** D2 (discard of H14) may be premature. The extended-controls specification reveals a manager-side spread signal that is stronger than the observation packet acknowledges.

**Required action:** Reassess whether H14 warrants promotion or at minimum "keep under watch: Yes."

### MEDIUM-1: F2 Omits Manager_QA in BookLev

**What happened:** Manager_QA is significantly positive in BookLev cols 1 (p=0.041) and 3 (p=0.058) under industry FE. The observation packet focuses exclusively on CEO_Pres and misses this secondary pattern.

**Required action:** Note Manager_QA in the F2 evidence signature, even if it doesn't change the dominant CEO_Pres narrative.

### MEDIUM-2: F5 Omits Manager_Pres in H5

**What happened:** Manager_Pres is significantly positive in H5 col 2 (p=0.026) alongside CEO_Pres (p=0.042). The observation packet reports only CEO_Pres for the H5 component.

**Required action:** Add Manager_Pres to the H5 evidence signature in F5.

---

## 6. ITEMS VERIFIED CORRECT (NO ACTION NEEDED)

- All table dimensions (4-col vs 8-col) match the codebase
- Column ordering (Industry/Firm × Base/Extended) is accurately described
- H12's use of averaged IVs is correctly noted
- H1 (F1) significance pattern is fully accurate
- H13 (F3) significance pattern is fully accurate
- H7 null surface is correctly described
- H15 null surface (D3) is correctly described
- D4 (CEO_QA leverage discard) is correctly justified
- D1 (investment residual watch) is appropriately flagged
- Timing splits (which suites have t/t+1 vs single DV) are all correct
- FE structure descriptions are all correct
- All artifact flags are appropriate

---

## 7. RECOMMENDED ACTIONS (PRIORITIZED)

1. **[CRITICAL]** Resolve H12 test direction. Either fix runner to two-tailed/positive, or retract F4.
2. **[HIGH]** Reassess D2 (H14 discard). Change to "keep under watch: Yes" at minimum.
3. **[MEDIUM]** Add Manager_QA to F2 evidence signature.
4. **[MEDIUM]** Add Manager_Pres to F5/H5 evidence signature.
5. **[LOW]** Correct the test-type table in Section A (H12: one-tailed, not two-tailed).
