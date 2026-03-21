# H1 Suite -- Second-Layer Red-Team Audit

**Suite ID:** H1
**Audit date:** 2026-03-21
**Auditor mode:** Hostile-but-fair second-layer red-team (audit the audit)
**First-layer doc:** `docs/provenance/H1.md` (v3, 2026-03-18)
**Runner:** `src/f1d/econometric/run_h1_cash_holdings.py`
**Panel builder:** `src/f1d/variables/build_h1_cash_holdings_panel.py`
**Compustat engine:** `src/f1d/shared/variables/_compustat_engine.py`

---

## A. Red-Team Bottom Line

The first-layer audit is **substantially correct, thorough, and appropriately skeptical**. It is one of the strongest provenance documents in the project. Quantitative claims (N values, coefficient signs, significance patterns, model specifications) are verified against the code. The audit correctly identifies the key limitations (reverse causality, effective N inflation, multiple testing, CEO selection, missing VIF) and does not overstate findings. However, I identify three issues: (1) several line-number references are stale or off by 10+ lines; (2) a stale docstring in the panel builder contradicts the code's actual lead-variable construction; (3) the BookLev formula silently maps both-NaN debt to zero rather than NaN, which is documented but whose implications are under-discussed. None of these block thesis submission.

**Verdict: PASS with minor corrections.**

---

## B. Scope

| Item | Covered? |
|------|----------|
| Runner code (run_h1_cash_holdings.py) | Yes, thoroughly |
| Panel builder (build_h1_cash_holdings_panel.py) | Yes, thoroughly |
| Compustat engine (_compustat_engine.py) | Yes, key variable formulas verified |
| Linguistic engine (_linguistic_engine.py) | Yes, winsorization verified |
| CRSP engine (_crsp_engine.py) | Referenced, not independently deep-verified |
| Variable builders (book_lev.py, cash_holdings.py, etc.) | Yes |
| Output artifacts (LaTeX, CSV, diagnostics) | Yes |
| Attrition pipeline | Yes, with noted limitations |
| Econometric specification | Yes |
| Identification strategy | Yes, with appropriate caveats |

---

## C. Scorecard

| Dimension | Grade | Comment |
|-----------|-------|---------|
| Factual accuracy | A- | All major claims verified; several line-number references are stale (off by ~10-20 lines due to code evolution) |
| Completeness | A- | Covers all major paths; misses one stale docstring and one minor formula edge case |
| Appropriate skepticism | A | Correctly identifies reverse causality, OVB, Moulton, multiple testing; does not over-flag |
| Econometric rigor | A- | One-tailed justification sound; missing double-clustering robustness acknowledged; no VIF acknowledged |
| Reproducibility | A | Commands, timestamps, file counts all verified |
| Transparency | A | Limitation table is honest and well-calibrated |

**Overall: A-**

---

## D. Claim Verification Matrix

| # | Audit claim | Code location | Verified? | Notes |
|---|-------------|---------------|-----------|-------|
| D1 | KEY_IVS = 4 variables (CEO_QA, CEO_Pres, Mgr_QA, Mgr_Pres) | Runner L80-84 | CORRECT | Exact match |
| D2 | BASE_CONTROLS = 7 variables | Runner L86-94 | CORRECT | Exact match |
| D3 | EXTENDED_CONTROLS = Base + 4 | Runner L96-101 | CORRECT | Exact match |
| D4 | MODEL_SPECS = 8 specifications (2 DV x 2 FE x 2 controls) | Runner L103-112 | CORRECT | Exact match |
| D5 | MIN_CALLS_PER_FIRM = 5 | Runner L114 | CORRECT | |
| D6 | Main sample excludes FF12 codes 8, 11 | Runner L214 | CORRECT | `~panel["ff12_code"].isin([8, 11])` |
| D7 | CashHoldings = cheq / atq | Engine L1068 | CORRECT | |
| D8 | BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq | Engine L1041 | CORRECT | |
| D9 | TobinsQ = (cshoq*prccq + dlcq + dlttq) / atq | Engine L1069-1078 | CORRECT | With clipping and both-NaN guard |
| D10 | One-tailed p: p_two/2 if beta > 0 else 1 - p_two/2 | Runner L379-380 | CORRECT | |
| D11 | _sig_stars: ***<0.01, **<0.05, *<0.10 | Runner L400-410 | CORRECT | |
| D12 | Industry FE via other_effects, check_rank=False | Runner L336-343 | CORRECT | |
| D13 | Firm FE via from_formula with EntityEffects + TimeEffects | Runner L349 | CORRECT | |
| D14 | Firm-clustered SEs in all specs | Runner L345, 351 | CORRECT | |
| D15 | Lead variable uses latest call per (gvkey, fyearq_int) | Panel builder L309 | CORRECT | `idxmax()` on start_date_dt |
| D16 | Lead validated for fiscal-year continuity | Panel builder L331-334 | CORRECT | |
| D17 | Summary stats computed on Main sample (not regression sample) | Runner L735-745 | CORRECT | `make_summary_stats_table(df=panel, ...)` called after `filter_main_sample()` but before prepare_regression_data() |
| D18 | Linguistic variables: 0%/99% upper-only winsorization | _linguistic_engine.py L255-258 | CORRECT | `lower=0.0, upper=0.99` |
| D19 | Compustat variables: 1%/99% per-fyearq winsorization | Engine L445-468, L1208-1215 | CORRECT | |
| D20 | 20 builders (1 manifest + 19 variable) | Panel builder L121-157 | CORRECT | Count verified |
| D21 | Zero row-delta enforced on all merges | Panel builder L209-217 | CORRECT | `ValueError` raised if after != before |
| D22 | file_name uniqueness asserted before merges | Panel builder L172-177, L192-197 | CORRECT | |
| D23 | Report says "All 4 key IVs" (not 6) | Runner L614 | CORRECT | |
| D24 | Panel builder docstring says "Average CashHoldings" for lead | Panel builder L17-18 | **STALE** | Code uses `idxmax()` (latest call), not average. Audit describes code correctly but did not flag the stale docstring. |

---

## E. Unsupported Claims

| # | Claim in audit | Issue | Severity |
|---|----------------|-------|----------|
| E1 | "Inf cleanup at L1159, L1171-1172" (Section 6.1.1, step 5) | L1159 is actually part of REPO computation. Actual inf cleanup for CashHoldings is in the ratio_cols loop at L1164-1186 (CashHoldings is at L1172 in the list). The line numbers are stale but the factual claim (inf -> NaN) is correct. | Low |
| E2 | Multiple line references throughout Sections 6.1-6.4 cite specific line numbers | Several are off by 5-20 lines, likely due to code additions after the audit was written. E.g., the audit cites "L1066" for CashHoldings but it is at L1068. | Low |

No substantively incorrect claims found. All factual assertions about formulas, data flows, and econometric specifications are verified.

---

## F. False Positives

| # | First-layer finding | Assessment |
|---|---------------------|------------|
| F1 | L10: check_rank=False could mask collinearity | **Not a false positive but appropriately low severity.** With 10 industry dummies and 11 regressors over 57k obs, rank deficiency is extremely unlikely. The flag is warranted as documentation but correctly marked Low. |
| F2 | L11: Negative within-R2 may confuse readers | **Not a false positive.** This is a real interpretive issue for industry FE models. Correctly flagged as Low. |

No false positives identified. All flagged issues are real.

---

## G. Missed Issues

| # | Issue | Severity | Description |
|---|-------|----------|-------------|
| G1 | Stale panel builder docstring for lead construction | Low | Panel builder lines 17-18 say "Average CashHoldings within (gvkey, call_year) -> firm-year mean". The actual code at L309 uses `idxmax()` to select the latest call per firm-fiscal-year, not an average. The first-layer audit correctly describes the code's behavior in Section 5.4 but does not flag the docstring as stale. |
| G2 | BookLev both-NaN-debt edge case under-discussed | Low-Medium | The audit correctly documents that `dlcq.fillna(0) + dlttq.fillna(0)` maps both-NaN to 0/atq = 0. This differs from TobinsQ, where both-NaN debt produces NaN via explicit guard (L1072-1073). The audit notes this asymmetry factually but does not discuss whether BookLev = 0 for firms with truly missing debt data is economically appropriate. For most firms, missing `dlcq`/`dlttq` likely means zero debt (small firms not reporting), so the fillna(0) convention is defensible. But it should be acknowledged as a choice. |
| G3 | Attrition table logical ordering issue | Low | The runner's attrition table (L778-783) lists "After lead filter (col 5-8 only)" as stage 3 and "After complete-case + min-calls (col 1)" as stage 4. This mixes the contemporaneous DV path (col 1) with a lead-DV-specific filter, creating a non-monotonic attrition sequence. The audit notes the table's limitations but doesn't flag this specific ordering inconsistency. |
| G4 | Line number drift throughout | Low | Multiple line references are stale by 5-20 lines. While the factual claims are correct, a committee member cross-checking specific line numbers would find mismatches. |
| G5 | No discussion of `drop_absorbed=True` implications for singleton detection | Low | The audit notes `drop_absorbed=True` is used but does not discuss whether singleton observations (firms appearing in only one time period) are dropped and what this does to the effective sample. With MIN_CALLS_PER_FIRM = 5, this is unlikely to matter, but the interaction is worth noting. |

---

## H. Severity Recalibration

| First-layer ID | First-layer severity | Red-team severity | Rationale |
|----------------|----------------------|-------------------|-----------|
| L1 (Reverse causality) | High (no block) | High (no block) | Agree. Standard for descriptive corporate finance. |
| L2 (OVB) | Medium-High (no block) | Medium-High (no block) | Agree. Additional controls would strengthen but are not required. |
| L3 (No lagged DV) | High (blocks for lead specs) | **Medium-High** (blocks is too strong) | Downgrade slightly. While lagged DV is ideal for highly persistent series, the lead specs use t+1 DV, meaning the concern is about omitting CashHoldings_t as a control, not CashHoldings_{t-1}. This is a robustness enhancement, not a specification error. The contemporaneous specs (cols 1-4) are unaffected. |
| L4 (Effective N) | Medium-High | Medium-High | Agree. The Moulton concern is real but partially addressed by firm clustering. |
| L5 (Multiple testing) | Medium | Medium | Agree. 32 tests without correction is standard in empirical finance but should be discussed. |
| L6 (CEO selection) | Medium | Medium | Agree. CEO missingness is endogenous but the manager variables provide a less-selected alternative. |
| L7 (No VIF) | Medium | Medium | Agree. CEO and Manager measures are correlated by construction (CEO is subset of Manager). |
| L8 (Summary stats on full Main) | Medium | **Low-Medium** | Downgrade. Summary stats on the full Main sample is actually more informative about the population; regression-sample stats would be nice as a supplement but are not essential. |
| L9 (TobinsQ formula inconsistency) | Medium | Medium | Agree. The `__init__.py` comment should be fixed. |
| L10 (check_rank=False) | Low-Medium | Low | Agree with current placement or slight downgrade. |
| L11 (Negative within-R2) | Low | Low | Agree. |
| L12 (No economic magnitude) | Low | Low-Medium | Slight upgrade. A committee will ask about economic significance. |

---

## I. Completeness Gaps

| # | Gap | Severity |
|---|-----|----------|
| I1 | **No verification of Volatility builder's CRSP date-bounding logic.** The audit references the CRSP engine's PERMNO linkage and window computation (Section 6.4.4) but does not independently verify the `window_end = next_call_date - 5 days` logic against the code. This is a complex computation with multiple edge cases. | Low |
| I2 | **No cross-check of coefficient magnitudes against output files.** The audit reports coefficients from Section 7 but does not state whether these were independently verified against the `regression_results_col{1-8}.txt` files or `model_diagnostics.csv`. The v3 rewrite claims verification against run `2026-03-18_185323` but no hash or checksum is provided. | Low |
| I3 | **No discussion of pandas version sensitivity.** The audit lists Python 3.13, pandas 2.2.3, numpy 2.3.2, linearmodels. PanelOLS behavior (especially `from_formula` with `drop_absorbed`) can change across versions. No version pinning or lockfile reference is provided. | Low |

---

## J. Reproducibility Red-Team

| # | Check | Result |
|---|-------|--------|
| J1 | Stage 3 command correct? | YES: `python -m f1d.variables.build_h1_cash_holdings_panel` matches module path |
| J2 | Stage 4 command correct? | YES: `python -m f1d.econometric.run_h1_cash_holdings` matches module path |
| J3 | Output file paths consistent? | YES: `outputs/variables/h1_cash_holdings/{ts}/` and `outputs/econometric/h1_cash_holdings/{ts}/` match code |
| J4 | Determinism claim valid? | YES: OLS is deterministic given fixed inputs; no random seeds or stochastic components |
| J5 | Input paths documented? | YES: All raw data paths documented in Section 3 |
| J6 | Expected output file count? | YES: 16 Stage 4 files documented; matches code (8 regression .txt + diagnostics CSV + LaTeX table + summary CSV/TEX + attrition CSV/TEX + report + manifest) |

---

## K. Econometric Meta-Audit

| # | Check | Assessment |
|---|-------|------------|
| K1 | Is the FE structure appropriate for the hypothesis? | YES. Industry + Year FE for between-firm variation; Firm + Year FE for within-firm variation. Both are standard. |
| K2 | Is the one-tailed test justified? | YES. The precautionary savings hypothesis makes a directional prediction (uncertainty -> more cash). The formula `p_two/2 if beta > 0 else 1 - p_two/2` is correct. |
| K3 | Are clustered SEs appropriate? | YES. Firm clustering is standard for panel data with firm-level persistence. 1,615 clusters is well above the minimum (~50) for asymptotic validity. |
| K4 | Is the simultaneous IV specification defensible? | YES, with caveats. The horse-racing approach is standard but creates multicollinearity risk (CEO measures are a subset of Manager measures). The audit acknowledges this (L7) but VIF should be computed. |
| K5 | Is the lead variable construction correct? | YES. Latest call per firm-fiscal-year, shift -1 within gvkey, consecutive-year validation. This is a clean implementation. |
| K6 | Is the Moulton concern adequately flagged? | YES. The audit quantifies it (avg 35 calls/firm, DV constant within firm-quarter) and recommends firm-year collapse robustness. |
| K7 | Are the negative within-R2 values explained? | YES. The explanation (industry FE absorbs less than entity FE) is correct for PanelOLS's within-R2 computation. |
| K8 | Missing econometric checks? | Double-clustering (Petersen 2009) is noted as missing. Hausman test for FE vs RE not discussed (reasonable omission since theory dictates FE). No Driscoll-Kraay SEs considered for cross-sectional dependence. |

---

## L. Audit-Safety Assessment

| # | Check | Result |
|---|-------|--------|
| L1 | Does the audit hide unfavorable results? | NO. CEO variables showing no significance (0/8) and wrong-sign betas are prominently documented. |
| L2 | Does the audit overstate statistical significance? | NO. Stars and p-values are correctly reported with one-tailed notation. |
| L3 | Does the audit claim causality? | NO. Section 11.1 explicitly states "Causal interpretation is not claimed and not supported." |
| L4 | Are limitations downplayed? | NO. 12 limitations are documented with honest severity ratings. |
| L5 | Is the red-team disposition transparent? | YES. Section 13 provides item-by-item responses to the prior red-team. |

---

## M. Master Issue Register

| # | Source | Description | Severity | Blocks thesis? | Recommended fix |
|---|--------|-------------|----------|----------------|-----------------|
| M1 | G1 | Stale panel builder docstring (says "average" but code uses "latest call") | Low | No | Update docstring at panel builder L17-18 |
| M2 | G2 | BookLev both-NaN-debt -> 0 asymmetry with TobinsQ guard | Low-Medium | No | Add footnote in thesis acknowledging convention |
| M3 | G4 | Stale line-number references throughout audit doc (5-20 lines off) | Low | No | Update line numbers if code is frozen; otherwise add caveat that line numbers are approximate |
| M4 | E1-E2 | Specific line citations for inf cleanup are incorrect | Low | No | Correct in next doc revision |
| M5 | H/L3 | No lagged DV control for lead specs | Medium-High | Robustness needed | Add CashHoldings_t as control in cols 5-8 as robustness check |
| M6 | H/L12 | No economic magnitude interpretation | Low-Medium | No | Add back-of-envelope: 1-SD increase in Mgr Pres Unc -> X% change in cash ratio |
| M7 | K8 | No double-clustered SEs robustness | Medium | No | Add as robustness table in appendix |

---

## N. What a Committee Would Not Know from Reading the Audit

1. **The panel builder's own docstring contradicts its implementation** for lead-variable construction. A committee member reading both the docstring and the audit would be confused (the audit correctly describes the code, but the code's own documentation is wrong).

2. **The BookLev formula treats missing debt as zero debt**, which is a defensible but non-obvious convention. A firm with truly missing Compustat debt fields gets BookLev = 0, making it look like a zero-leverage firm. This could bias results if debt missingness is correlated with uncertainty language.

3. **The attrition table in the output artifact has a non-monotonic structure** that mixes column-specific filters. A committee member reading the CSV would see "After lead filter (col 5-8 only)" as a universal intermediate step, which it is not.

4. **Line numbers in the audit are approximate.** Any committee member attempting to verify specific claims by line number will find mismatches of 5-20 lines.

---

## O. Priority Fixes

**Before thesis submission (ordered by priority):**

1. **Update panel builder docstring** (L17-18): Change "Average CashHoldings" to "Latest-call CashHoldings" to match actual code. (5 minutes)

2. **Add lagged-DV robustness check** for lead specs (cols 5-8): Include CashHoldings_t as a control and report as supplementary table. (2-4 hours)

3. **Compute VIF** for the 4 simultaneous IVs and report. CEO and Manager measures are correlated by construction. (1 hour)

4. **Add economic magnitude interpretation**: A 1-SD increase in Mgr Pres Uncertainty is associated with X basis-point increase in cash-to-assets ratio, equivalent to $Y million for the median firm. (30 minutes)

5. **Fix TobinsQ formula in `__init__.py`** line 21 to match actual engine code. (5 minutes)

**Nice-to-have (not blocking):**

6. Update line-number references in provenance doc to match current code.
7. Add double-clustered SEs (firm + year) as robustness.
8. Add regression-sample summary statistics alongside Main-sample summary statistics.

---

## P. Final Statement

The first-layer audit (H1.md v3) is a high-quality, thesis-standard provenance document. It accurately describes the 4-IV simultaneous specification, correctly reports all model specifications and their results, and identifies the key econometric limitations with appropriate severity calibration. The document is honest about null results (CEO variables 0/8 significant, wrong-sign betas) and does not overstate the evidence.

The issues I identify are minor: stale line numbers, one stale docstring, and a few under-discussed edge cases. None affect the validity of the econometric results or the audit's conclusions. The recommended priority fixes (lagged-DV robustness, VIF computation, economic magnitude) would strengthen the thesis defense but are enhancements rather than corrections.

**Second-layer verdict: The first-layer audit is trustworthy and sufficient for thesis-standard review. PASS.**
