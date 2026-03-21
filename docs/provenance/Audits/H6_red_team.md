# H6 Suite -- Second-Layer Red-Team Audit

**Suite ID:** H6 -- SEC Scrutiny (CCCL) and Speech Vagueness
**Audit type:** Second-layer red-team (audit of the first-layer audit)
**First-layer doc:** `docs/provenance/H6.md` (v3.0, 2026-03-18)
**Auditor:** Claude Opus 4.6 (hostile-but-fair replication auditor)
**Date:** 2026-03-21
**Code files inspected:** `run_h6_cccl.py`, `build_h6_cccl_panel.py`, `cccl_instrument.py`, `_compustat_engine.py`, `_linguistic_engine.py`, `winsorization.py`, `panel_utils.py`, `config/variables.yaml`

---

## A. Scope of the First-Layer Audit

The first-layer audit (H6.md v3.0) is comprehensive, covering 690 lines across 14 sections. It documents the full variable dictionary, estimation specification, merge chain, identification threats, and 23 known limitations. It incorporates findings from a prior red-team round (Section 13).

**Coverage assessment:** The audit covers all major components: panel builder, runner, shared engines (Compustat, CRSP, Linguistic), CCCL instrument builder, config overrides, and output files. It traces variable construction chains in detail.

**Gaps in scope:** The audit does not independently verify the linguistic pipeline (tokenization/aggregation in `tokenize_transcripts.py` and `build_linguistic_variables.py`), relying on descriptions of upstream Stage 2 code. This is acceptable given the shared-engine architecture.

---

## B. Factual Errors Found in First-Layer Audit

### B1. False claim: `rsquared` column mislabeled in diagnostics CSV (INCORRECT)

**Audit claim (Section 7.4, line 474):** "line 237 assigns `'rsquared': float(model.rsquared_within)` rather than the overall R-squared. The `rsquared` column is therefore mislabeled; it is a duplicate of within-R2."

**Actual code (line 237):** `"within_r2": within_r2`

The meta dictionary at lines 230-245 contains keys `"within_r2"` and `"rsquared_inclusive"`. There is NO `"rsquared"` key. The audit's claim that a mislabeled `rsquared` column exists in `model_diagnostics.csv` is factually wrong for the current codebase. The CSV will contain columns `within_r2` and `rsquared_inclusive`, both correctly labeled.

**Severity:** The audit fabricated an issue that does not exist. This is a false positive that should be retracted.

**Disposition:** Section 7.4 should be deleted. Section 12 item 12 ("rsquared column in diagnostics CSV is mislabeled duplicate of within_r2") should be removed.

### B2. Verification item 11 references wrong code

**Audit claim (Verification Log #11):** "Read `run_h6_cccl.py` lines 237-239: `rsquared` column in diagnostics -- `'rsquared': float(model.rsquared_within)` -- mislabeled duplicate of within_r2."

**Actual code at lines 237-239:**
```python
"within_r2": within_r2,
"rsquared_inclusive": float(model.rsquared_inclusive),
"beta1": float(beta1),
```

The verification log entry describes code that does not exist at the cited lines. This indicates the first-layer auditor either inspected a different version of the file or fabricated the verification.

---

## C. Claims Verified as Correct

| # | Audit claim | Verification | Status |
|---|-------------|-------------|--------|
| C1 | Only `PanelOLS` imported; no `IV2SLS` (Section 1) | Line 66: `from linearmodels.panel import PanelOLS`. No IV2SLS import anywhere. | CONFIRMED |
| C2 | `iv_cols = ["shift_intensity_mkvalt_ff48"]` at line 154 | Verified at line 154. | CONFIRMED |
| C3 | Lag variable constructed but never used in runner | `shift_intensity_mkvalt_ff48_lag` appears in `build_h6_cccl_panel.py` (lines 105-109, 132) but is never loaded by `run_h6_cccl.py` (lines 401-425 column list omits it). | CONFIRMED |
| C4 | `prepare_regression_data()` is a no-op (lines 136-138) | Returns `panel.copy()` with no transformation. | CONFIRMED |
| C5 | Table note falsely claims standardization (line 353) | Line 353: `"All continuous controls are standardized. "` -- no standardization code exists. | CONFIRMED |
| C6 | Table note inaccurate on winsorization (line 354) | Line 354: `"Variables are winsorized at 1\\%/99\\% by year. "` -- linguistic DVs use 0%/99% upper-only (`_linguistic_engine.py` line 257: `lower=0.0, upper=0.99`). | CONFIRMED |
| C7 | One-tailed p-value correctly implemented (line 219) | `p1_two / 2 if beta1 < 0 else 1 - p1_two / 2` -- standard one-tailed conversion. | CONFIRMED |
| C8 | LaTeX stars use one-tailed p-values (lines 264-274, 304) | `fmt_coef(r_1['beta1'], r_1['beta1_p_one'])` at line 304 -- stars applied to one-tailed p. | CONFIRMED |
| C9 | `drop_absorbed=True` at line 196 | Verified. | CONFIRMED |
| C10 | Warning suppression at lines 75-77 | Verified: `warnings.filterwarnings("ignore", message="covariance of constraints does not have full rank")`. | CONFIRMED |
| C11 | CCCL config override: `shift_intensity_mkvalt_ff48` | `config/variables.yaml` line 499: `column: "shift_intensity_mkvalt_ff48"`. Default in `cccl_instrument.py` line 45 is `"shift_intensity_sale_ff48"`. Override confirmed. | CONFIRMED |
| C12 | Zero-row-delta enforcement in panel builder | Lines 225-227 of `build_h6_cccl_panel.py`: raises `ValueError` if delta != 0. | CONFIRMED |
| C13 | CCCL uniqueness assertion before merge | `cccl_instrument.py` lines 124-129: checks for duplicates on `["gvkey", "fyearq_int"]`, raises `ValueError`. | CONFIRMED |
| C14 | Min-calls filter counts non-null contemporaneous CCCL | Lines 475-479: `groupby("gvkey")["shift_intensity_mkvalt_ff48"].transform("count")` -- `count` excludes NaN. | CONFIRMED |
| C15 | Consecutive-year gap detection in lag/lead construction | Lines 108-109, 116-117, 124-125 of `build_h6_cccl_panel.py`: non-consecutive years set to NaN. | CONFIRMED |
| C16 | Attrition table covers only Main/MgrQA path | Line 507: `main_result = next((r for r in all_results if r.get("sample") == "Main"), all_results[0])` -- single path. | CONFIRMED |
| C17 | Industry sample assignment: NaN maps to Main | `panel_utils.py` line 57: "NaN ff12_code values are classified as 'Main'". Uses `np.select` with default "Main". | CONFIRMED |
| C18 | Compustat winsorization at 1%/99% per fyearq | `_compustat_engine.py` lines 1208-1215: `_winsorize_by_year(comp[col], year_col)` with default 1%/99%. | CONFIRMED |
| C19 | CRSP winsorization at 1%/99% per year | `winsorization.py` defaults: `lower=0.01, upper=0.99`. | CONFIRMED |
| C20 | CCCL instrument not winsorized | No winsorization call on CCCL in `cccl_instrument.py`. | CONFIRMED |
| C21 | BookLev formula: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` | `_compustat_engine.py` line 1041. | CONFIRMED |
| C22 | `RD_Intensity` uses `fillna(0)` for missing xrdq | `_compustat_engine.py` line 1065: `comp["xrdq"].fillna(0) / comp["atq"]`. | CONFIRMED |

---

## D. Severity Assessments Reviewed

### D1. Contemporaneous treatment (rated Critical) -- AGREE

The audit rates using contemporaneous CCCL(t) as "Critical." This is appropriate. The lag variable was explicitly constructed (`shift_intensity_mkvalt_ff48_lag`) but is never loaded by the runner. This eliminates temporal separation between treatment and outcome and makes causal interpretation indefensible. The severity is correctly calibrated.

### D2. IV labeling on OLS (rated High) -- AGREE

The suite name says "CCCL" (instrument), the variable is named `iv_cols`, but only `PanelOLS` is used. No IV/2SLS estimation occurs. The audit correctly rates this as High (naming/framing issue, not estimation error). Renaming would resolve it.

### D3. Pre-trends violation (rated High with caveat) -- AGREE

Lead1 p=0.038 (two-tailed) with the caveat that the pre-trends regression uses 15.2% fewer observations. The audit's nuanced treatment is appropriate: the violation is concerning but the sample composition difference warrants caution.

### D4. Look-ahead bias (rated High) -- AGREE

CCCL is at fiscal-year level. A Q1 call receives full-year CCCL exposure including future months. This is a legitimate concern correctly rated.

### D5. False standardization claim (rated High) -- AGREE

A LaTeX table note claiming standardization when none occurs is a materially misleading claim to readers. High severity is warranted.

### D6. Non-unique panel index (rated Low-Medium) -- AGREE

PanelOLS handles non-unique `(entity, time)` indices. Firm-level clustering addresses within-firm correlation. This is correctly downgraded from earlier severity levels.

### D7. Multiple testing (rated Medium) -- SLIGHT UPGRADE to Medium-High

The audit notes 8 tests with no MHC, and that neither result survives Bonferroni. It then caveats that Bonferroni is too conservative. However, the broader point stands: 2/8 significant at p<0.05 one-tailed is entirely consistent with chance under the null. The audit could more forcefully state that the overall evidence for H6 is weak. Medium-High would be more appropriate.

---

## E. Missing Issues Not Identified by First-Layer Audit

### E1. Panel index set as `(gvkey, year)` with non-unique entries -- entity effects interpretation

The audit notes the non-unique panel index (Section 11.4) but does not fully explore the consequence: when PanelOLS encounters multiple rows per `(gvkey, year)`, the entity demeaning removes the within-gvkey mean across ALL calls for that firm (not per-year). The time demeaning removes the within-year mean. With ~3.9 calls per firm-year, within-firm-year variation in the DV (e.g., differences between Q1 and Q3 calls for the same firm in the same year) is used for identification, but the CCCL treatment variable is constant within firm-year (since it's assigned at fiscal-year level). This means the within-firm-year DV variation contributes to the residual but not to beta estimation. The effective N for identification is closer to the number of firm-years (~27,000) than the number of calls (~67,000), inflating apparent precision. Firm-level clustering partially addresses this, but the reported N overrepresents independent variation.

**Severity:** Medium. Not an error, but the reported N is misleading for precision assessment.

### E2. Lead2 gap check allows skipping one year

The audit documents lead2 gap detection at line 124: `(next_fyearq2 - fyearq_int) == 2`. However, `shift(-2)` on a sorted firm-year panel skips exactly 2 positions, not 2 calendar years. If a firm has years [2010, 2012, 2014], `shift(-2)` at 2010 gives the value at 2014, and `(2014 - 2010) == 2` is false (gap is 4), so it correctly sets to NaN. But if a firm has [2010, 2011, 2013], `shift(-2)` at 2010 gives 2013, and `(2013 - 2010) == 2` is false (gap is 3), also correctly NaN. The logic is actually correct for its stated purpose (requiring exactly 2 fiscal years ahead). The audit's description is accurate.

**Finding: no new issue here.** Retracted upon verification.

### E3. `file_name` filter in CCCLInstrumentBuilder limits to year range

At `cccl_instrument.py` line 61: `manifest = manifest[manifest["_cal_year"].isin(list(years))]`. The manifest is filtered by calendar year before the CCCL merge. This is a year-range filter that depends on `config/project.yaml` settings. If the year range is narrower than the full sample, the CCCL builder produces a smaller output. This filter is not mentioned in the audit. However, since the panel builder passes the project-configured year range (typically 2002-2018), this is standard behavior and not an error.

**Severity:** Informational. No issue, but undocumented in the audit.

### E4. Pre-trends meta not saved to `all_results`

At line 495 of `run_h6_cccl.py`: `model_pt, _ = run_regression(df_filtered, dv, sample, pre_trends=True)`. The pre-trends meta dictionary is discarded (assigned to `_`). This means:
- Pre-trends results are never added to `all_results`
- They never appear in `model_diagnostics.csv`
- They never appear in the LaTeX table
- The only record is the `.txt` summary file

The audit mentions this at Section 7.3 ("not included in model_diagnostics.csv or LaTeX table") and Section 12 item 9, but does not trace it to this specific line where the meta is explicitly discarded. The code intentionally ignores the pre-trends metadata.

**Severity:** Already documented. No new finding, but the root cause (line 495's `_` assignment) is not cited.

---

## F. Identification and Inference Assessment Review

### F1. Reduced-form framing (Section 11.1)

The audit correctly identifies the suite as reduced-form OLS and provides appropriate caveats. The equation is accurate. No errors.

### F2. Identification threats table (Section 11.3)

The seven threats listed are comprehensive and appropriately rated. The look-ahead bias (a Q1 call receiving full-year CCCL) is well-articulated. The own-firm contamination concern is legitimate but inherently limited without access to the external CCCL construction code.

### F3. Economic magnitude assessment (Section 11.4)

The audit computes: 0.038 (one-SD CCCL) * 0.1125 (beta) = 0.004 pp decrease, which is 0.5% of the mean (~0.82%). This is correctly characterized as economically trivial.

### F4. Supported interpretation (Section 11.5)

The characterization as "descriptive association" with causal language unsupported is accurate and appropriately hedged.

---

## G. Variable Construction Verification

### G1. Dependent variables

The audit's description of the linguistic pipeline (Section 6.1) is thorough and accurate. The winsorization at `lower=0.0, upper=0.99` is correctly documented. The 7-step construction chain matches the code.

### G2. CCCL instrument

The audit's description (Section 6.2) is accurate. The config override path is verified. The merge chain (fyearq attachment via merge_asof, then left join on gvkey+fyearq_int) matches `cccl_instrument.py` lines 77-84 and 133-136.

### G3. Compustat controls

The audit's variable formulas (Section 6.4) are verified against `_compustat_engine.py`:
- Size: `np.log(atq)` where `atq > 0` -- correct (line 1036)
- BookLev: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` -- correct (line 1041)
- ROA: annualized via Q4-only join -- correct (lines 1052-1061)
- CashHoldings: `cheq / atq` -- correct (line 1068)
- TobinsQ: `(mktcap + debt_book) / atq` -- correct (lines 1075-1078)
- RD_Intensity: `xrdq.fillna(0) / atq` -- correct (line 1065)

### G4. Earnings volatility

The audit's detailed description (Section 6.4, rolling-std subsection) is comprehensive. The 5-year rolling window (`1826D`), `min_periods=3`, and Q4-only annual ROA construction are accurately described. Not independently re-verified at the line level but consistent with the code structure.

### G5. CRSP Volatility

The audit's description (Section 6.5) of `std(daily_ret) * sqrt(252) * 100` with minimum 10 trading days is consistent with the CRSP engine architecture. Winsorization at 1%/99% via the shared `winsorize_by_year` function (defaults confirmed in `winsorization.py` lines 27-28) is accurate.

---

## H. Merge Chain Verification

The audit's merge table (Section 5.1) lists 13 builders merged via `file_name` left join with zero-row-delta enforcement. This matches `build_h6_cccl_panel.py` lines 211-228. The merge logic (drop conflicting columns, check delta) is correctly described.

The CCCL-specific merge chain (Section 5.2) is verified against `cccl_instrument.py`:
1. fyearq attachment via `merge_asof` backward (lines 77-84): confirmed
2. CCCL left join on `gvkey + fyearq_int` (lines 133-136): confirmed
3. Uniqueness assertion (lines 124-129): confirmed
4. Zero-row-delta enforcement (lines 140-144): confirmed

---

## I. Output Inventory Verification

The audit claims 23 files: 16 regression .txt + 7 other. The code produces:
- 16 regression .txt files (4 DVs x 2 successful samples x {base, pre-trends}): consistent with the loop at lines 462-500
- `model_diagnostics.csv` (line 503)
- `h6_cccl_table.tex` (line 502)
- `summary_stats.csv` and `summary_stats.tex` (lines 452-453)
- `sample_attrition.csv` and `sample_attrition.tex` (line 513)
- `run_manifest.json` (line 527)

That is 16 + 7 = 23 files. **Confirmed.**

Note: Utility failures produce no output files (caught by try/except at line 198). The audit correctly documents 8 Utility failures.

---

## J. Reproducibility Assessment

The audit's reproducibility status of "PARTIAL" is accurate. The dependencies on raw inputs, prior stages, and `get_latest_output_dir()` resolution are correctly identified. The determinism claim (fully deterministic OLS) is correct.

---

## K. LaTeX Table Accuracy

### K1. Stars on one-tailed p-values

The audit correctly identifies that `fmt_coef` at line 264-274 applies standard thresholds (0.01/0.05/0.10) to one-tailed p-values (passed at line 304 via `r_1['beta1_p_one']`). This inflates apparent significance. The audit's example (Finance MgrQA: two-tailed p=0.066, one-tailed p=0.033, receives ** stars) is accurate.

### K2. Table note claims

Two false claims in the table note:
1. "All continuous controls are standardized" (line 353) -- FALSE, no standardization
2. "Variables are winsorized at 1%/99% by year" (line 354) -- PARTIALLY FALSE, linguistic DVs use 0%/99%

Both correctly identified by the audit.

### K3. Table label

Line 303: the row label is `"CCCL Exposure$_t$"` -- this correctly uses subscript `t` for contemporaneous treatment. No issue.

---

## L. Design Decision Documentation

The audit's design decisions table (Section 14) covers 9 decisions with rationale and trade-offs. The entries are balanced and accurate. Notable:

- The contemporaneous-vs-lag decision is characterized as "appears to be a design oversight" which is a fair interpretation given that the lag was explicitly constructed.
- The one-tailed test decision is correctly flagged as appropriate for directional hypotheses but problematic when combined with standard star thresholds.

---

## M. Known Limitations Completeness

The audit lists 23 limitations. Independent verification:

| # | Issue | Still valid? |
|---|-------|-------------|
| 1 | Contemporaneous CCCL | Yes |
| 2 | IV label on OLS | Yes |
| 3 | Pre-trends violation | Yes |
| 4 | Look-ahead bias | Yes |
| 5 | Standardization claim | Yes |
| 6 | Winsorization claim | Yes |
| 7 | One-tailed stars | Yes |
| 8 | Utility failures silent | Yes |
| 9 | Pre-trends not in CSV | Yes |
| 10 | No MHC | Yes |
| 11 | `drop_absorbed` silent | Yes |
| 12 | `rsquared` mislabeled | **FALSE -- should be removed** |
| 13 | Attrition single path | Yes |
| 14 | Warning suppression | Yes |
| 15-20 | Missing robustness checks | Yes (design choices, not bugs) |
| 21 | Stale directories | Yes (housekeeping) |
| 22 | Low within-R2 | Yes (informational) |
| 23 | RD_Intensity fillna(0) | Yes (standard practice) |

**Missing limitation (from Section E1 above):** The reported N overrepresents independent variation because CCCL is constant within firm-year but multiple calls per firm-year are counted as separate observations.

---

## N. Prior Red-Team Disposition Review (Section 13)

The audit's Section 13 incorporates 5 prior red-team findings (RT2-4 through RT2-8) and accepts 5 severity recalibrations. These are well-documented.

The disposition of RT2-1 (Finance files claim) and RT2-6 (rsquared mislabeling) may be based on a prior version of the code. The current code does not have the `rsquared` key issue. If the code was modified between the first red-team and the v3.0 audit, the audit should note this. Instead, it claims to have "incorporated" the finding and documents it as current (Sections 7.4 and 12 item 12), which is incorrect for the current codebase.

---

## O. Summary of Red-Team Findings

### Errors in the first-layer audit

| ID | Finding | Severity |
|----|---------|----------|
| RT3-1 | False claim: `rsquared` column mislabeled in diagnostics CSV. The meta dict has `within_r2` and `rsquared_inclusive`, not `rsquared`. Section 7.4 and Section 12 item 12 should be retracted. | Medium (false positive pollutes the audit) |
| RT3-2 | Verification item 11 cites code that does not exist at the referenced lines. | Low (documentation error) |

### New findings not in the first-layer audit

| ID | Finding | Severity |
|----|---------|----------|
| RT3-3 | Effective N for beta identification is closer to firm-years (~27,000) than calls (~67,000) because CCCL is constant within firm-year. Reported N overrepresents independent variation for the treatment variable. | Medium |

### Severity recalibrations

| Issue | Audit severity | Recommended | Rationale |
|-------|---------------|-------------|-----------|
| Multiple testing (item 10) | Medium | Medium-High | 2/8 significant under one-tailed testing is consistent with chance. Neither survives any MHC. The overall evidence for H6 is weak. |

### Confirmed findings (no change needed)

22 of 23 listed limitations are confirmed valid. The audit's identification and inference assessment (Section 11) is thorough and accurate. The variable dictionary (Section 6) is verified against source code. The merge chain (Section 5) is correctly documented.

---

## P. Overall Assessment

The first-layer audit (H6.md v3.0) is a high-quality, detailed provenance document. It correctly identifies the most critical issues: contemporaneous treatment, IV mislabeling, pre-trends violation, look-ahead bias, and false table-note claims. The variable construction chains are accurately traced, and the identification assessment is appropriately cautious.

**One factual error requires correction:** The `rsquared` mislabeling claim (Sections 7.4, 12 item 12, Verification Log #11) is a false positive based on code that does not match the current codebase. This should be retracted.

**One new issue merits addition:** The effective sample size for treatment-variable identification is overstated because CCCL is constant within firm-year but multiple calls per firm-year inflate the reported N.

**Overall reliability of the first-layer audit:** HIGH. 22/23 specific claims verified correct. The single error (rsquared column naming) is a localized false positive that does not affect the audit's main conclusions about identification, inference, or code correctness.
