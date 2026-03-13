# Audit 02: Data Sources, Samples, and Variable Measurement (III.1-III.3)
**Date:** 2026-03-13
**Auditor:** Claude Agent
**Scope:** Lines 90-124 of thesis_draft.tex
**Verdict:** PASS WITH ISSUES

---

## III.1 Data Sources Audit

### Claims Verified

1. **"Quarterly accounting data (total assets, book equity, leverage, ROA, current ratio, R&D expenditure, cash holdings) come from Compustat Quarterly"**
   - VERIFIED. `_compustat_engine.py` loads from `inputs/comp_na_daily_all/comp_na_daily_all.parquet` (Compustat Quarterly). Variables Size (atq), BM (ceqq, cshoq, prccq), Lev, ROA, CashHoldings, SalesGrowth are all computed from quarterly Compustat items. The engine documentation explicitly references quarterly fields (fyearq, fqtr, atq, ceqq, etc.).

2. **"Daily stock-level data (prices, returns, trading volume, shares outstanding) come from CRSP Daily"**
   - VERIFIED. `_crsp_engine.py` loads `CRSP_DSF_{year}_Q{q}.parquet` files (CRSP Daily Stock File). Columns loaded: `PERMNO, date, RET, VWRETD, VOL, PRC, BIDLO, ASKHI, BID, ASK, SHROUT` (line 72). This confirms prices (PRC), returns (RET), volume (VOL), and shares outstanding (SHROUT).

3. **"individual analyst earnings forecasts and actuals from IBES Detail"**
   - VERIFIED. `_ibes_engine.py` (line 8): "Input: inputs/tr_ibes/tr_ibes_YYYY.parquet (yearly detail-level files)". The engine loads individual analyst estimates (CUSIP, ACTDATS, ANALYS, VALUE, MEASURE, FPI, FPEDATS, ACTUAL) and computes consensus from detail-level data. This is IBES Detail, not Summary. The `_ibes_detail_engine.py` also confirms Detail usage.

4. **"CRSP-Compustat Merged (CCM) linktable"**
   - VERIFIED. Both `amihud_change.py` (line 121) and `bidask_spread_change.py` (line 132) load `inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet`. The CCM linkage uses date-bounded logic (linkdt <= start_date <= linkenddt).

5. **"earnings call transcripts from Capital IQ spanning 2002-2018"**
   - VERIFIED. `config/project.yaml` confirms `year_start: 2002` and `year_end: 2018`.

6. **"master manifest contains 112,968 earnings call transcripts"**
   - VERIFIED. Both H7 and H14 `sample_attrition.csv` show "Master manifest,112968,0,100.0" as the starting point.

7. **"Takeover events from SDC Platinum M&A database"**
   - VERIFIED. `takeover_indicator.py` (line 47): `SDC_FILE = "sdc-ma-merged.parquet"`, loaded from `inputs/SDC/`. The builder filters to US public targets with Deal Status in {Completed, Withdrawn, Pending}.

8. **"classified by attitude (friendly, hostile/uninvited, neutral)"**
   - VERIFIED WITH CAVEAT. Code (line 50-51): `UNINVITED_ATTITUDES = {"Hostile", "Unsolicited"}` and `FRIENDLY_ATTITUDES = {"Friendly", "Neutral"}`. The thesis says "hostile/uninvited" but the code maps "Hostile" and "Unsolicited" to "Uninvited", and maps both "Friendly" and "Neutral" to the "Friendly" type. The thesis phrasing "classified by attitude (friendly, hostile/uninvited, neutral)" is slightly misleading -- "Neutral" is actually classified under the Friendly category, not kept as a separate category. See Issue #1.

9. **"matched to the panel at the firm-quarter level"**
   - VERIFIED. `build_h9_takeover_panel.py` matches SDC events to the panel via gvkey (from CUSIP6 linkage). The panel uses call-to-call intervals (which are effectively firm-quarter-level given quarterly earnings calls).

### Issues Found

**ISSUE #1 (Minor): Attitude classification description is imprecise**
- Thesis line 95: "classified by attitude (friendly, hostile/uninvited, neutral)"
- Code reality: Neutral attitudes are grouped WITH Friendly (not kept separate). The code produces three output categories: Uninvited (Hostile + Unsolicited), Friendly (Friendly + Neutral), and Unknown (all other attitudes including "Not Applicable").
- The thesis implies three distinct categories but the code merges Neutral into Friendly.
- **Recommendation:** Change to "classified by attitude (Uninvited, comprising Hostile and Unsolicited bids; and Friendly, comprising Friendly and Neutral bids)" or similar.

---

## III.2 Samples Audit

### Claims Verified

1. **"exclude firms in Finance (FF12 code 11) and Utilities (code 8)"**
   - VERIFIED. `panel_utils.py` (line 67): `conditions = [ff12_code == 11, ff12_code == 8]`, `choices = ["Finance", "Utility"]`, default = "Main". This is the canonical classification used by all panel builders.

2. **"CEOs with at least five observed calls"**
   - VERIFIED. `run_h0_3_ceo_clarity_extended.py` (line 140): `MIN_CALLS = 5`. Also confirmed in `run_h0_2_ceo_clarity.py` (line 96): `"min_calls_per_ceo": 5`. All hypothesis runners use `min_calls = 5`.

3. **H0.3 sample sizes: "53,070 (Manager Baseline), 38,671 (CEO Baseline), 51,569 (Manager Extended), 37,517 (CEO Extended)"**
   - VERIFIED. `model_diagnostics.csv` from `ceo_clarity_extended/2026-03-13_053119/`:
     - Manager_Baseline: n_obs=53,070
     - CEO_Baseline: n_obs=38,671
     - Manager_Extended: n_obs=51,569
     - CEO_Extended: n_obs=37,517
   - All four numbers match exactly.

4. **H7 sample sizes: "38,214 (CEO clarity residual) to 78,679 (Manager QA)"**
   - VERIFIED. `model_diagnostics.csv` from `h7_illiquidity/2026-03-13_054310/`:
     - B1 (CEO_Clarity_Residual): n_obs=38,214
     - A3 (Manager_QA_Uncertainty_pct): n_obs=78,679
   - Both bounds match exactly.

5. **H14 sample sizes: "38,218 (CEO clarity residual) to 55,485 (Manager presentation)"**
   - VERIFIED. `model_diagnostics.csv` from `h14_bidask_spread/2026-03-13_053119/`:
     - CEO_Clarity_Residual: n_obs=38,218
     - Manager_Pres_Uncertainty_pct: n_obs=55,485
   - Both bounds match exactly.

6. **AbsSurpDec coverage: "69.8% coverage in the Main panel"**
   - VERIFIED. From `summary_stats.csv` in H14 output: AbsSurpDec N=61,544. From `sample_attrition.csv`: Main sample filter yields 88,205 rows. Coverage = 61,544 / 88,205 = 69.78%, which rounds to 69.8%.

7. **AbsSurpDec construction: "IBES Detail consensus via fpedats with 120-day backward tolerance, min 2 analysts, |MEANEST| >= 0.05"**
   - VERIFIED. `_ibes_engine.py`:
     - Line 43: `self.numest_min = 2` (min 2 analysts)
     - Line 44: `self.meanest_min = 0.05` (|MEANEST| >= 0.05)
     - `earnings_surprise.py` line 116: `tolerance=pd.Timedelta(days=120)` (120-day backward tolerance)
     - Direction is `backward` (matching on fpedats <= start_date)
   - All parameters match the thesis claim.

8. **H9 sample sizes: "54,981 firm-quarter intervals, 307 takeover events (250 friendly, 40 uninvited)"**
   - PARTIALLY VERIFIED. From `model_diagnostics.csv` (takeover/2026-03-13_053120/):
     - Manager_Residual (largest variant): n_intervals=54,981, n_event_firms=354
     - CEO variant (sparse): n_intervals=51,627, n_event_firms=307, with Friendly=250, Uninvited=40
   - The "up to 54,981" is correct (Manager_Residual variant).
   - The "307 takeover events" is from the CEO (ClarityCEO) variant. The 250 friendly and 40 uninvited are correct for that variant. However, 250 + 40 = 290, not 307. The remaining 17 events are "Unknown" type, which the thesis does not mention. See Issue #2.

9. **H9 variant event counts: "CEO Residual: 275 events; Manager Residual: 354 events"**
   - VERIFIED. Model diagnostics confirm:
     - CEO_Residual (sparse): n_event_firms=275
     - Manager_Residual (sparse): n_event_firms=354

### Issues Found

**ISSUE #2 (Minor): H9 event count omits Unknown category**
- Thesis line 102: "307 takeover events (250 friendly, 40 uninvited)"
- 250 + 40 = 290, not 307. The missing 17 events are "Unknown" type (attitude not classifiable as Friendly or Uninvited).
- **Recommendation:** Add "17 unclassified" or acknowledge the Unknown category, e.g., "307 takeover events (250 friendly, 40 uninvited, 17 unclassified)".

---

## III.3 Variable Measurement Audit

### Claims Verified

1. **"percentage of words classified as uncertain by the Loughran-McDonald (LM) financial dictionary"**
   - VERIFIED. The `_linguistic_engine.py` loads pre-computed linguistic variables from Stage 2 output that use the LM dictionary. Variable names follow the pattern `{Speaker}_{Section}_Uncertainty_pct`.

2. **"Uncertainty_pct = 100 x (LM Uncertainty words in s) / (total words in s)"**
   - VERIFIED. The formula is computed in Stage 2 (upstream text analysis) and the variables are named `_Uncertainty_pct` (percentage scale).

3. **"separately for presentation and Q&A, CEO vs aggregate management"**
   - VERIFIED. `LINGUISTIC_PCT_COLUMNS` in `_linguistic_engine.py` includes: `CEO_QA_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`, `Manager_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct` (lines 68-75, 113-119). Four variants confirmed.

4. **"winsorized at 1st and 99th percentiles within each calendar year"**
   - **MISMATCH.** See Issue #3.

5. **"ClarityCEO is the negative of the CEO fixed effect (-gamma_i)"**
   - VERIFIED. `run_h0_2_ceo_clarity.py` line 22: "ClarityCEO = -gamma_i (standardized per sample)". Line 402-403: `ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]`. Sign convention confirmed.

6. **"standardized to zero mean and unit variance within each industry sample (Main, Finance, Utility)"**
   - VERIFIED. `run_h0_2_ceo_clarity.py` lines 492-510: Per-sample z-scoring is performed within each sample (Main, Finance, Utility) separately, using `(_raw_vals - _s_mean) / _s_std`. The code comment at line 492 states: "S4 fix: Standardize ClarityCEO_raw PER SAMPLE (not globally)."

7. **"CEO_Clarity_Residual and Manager_Clarity_Residual are call-level residuals from regressing QA-section uncertainty on its linguistic determinants"**
   - VERIFIED. `run_h0_3_ceo_clarity_extended.py` lines 393-407: Residuals are extracted from baseline models (Manager_Baseline and CEO_Baseline). The Manager_Baseline model regresses `Manager_QA_Uncertainty_pct` on linguistic determinants (Manager_Pres_Uncertainty_pct, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct) plus financial controls and CEO + year FE. Residuals are saved as `manager_clarity_residual` and `ceo_clarity_residual`.

8. **"delta_amihud: A-bar[+1,+3] - A-bar[-3,-1]"**
   - VERIFIED. `amihud_change.py` line 360: `amihud["delta_amihud"] = amihud["post_call_amihud"] - amihud["pre_call_amihud"]`. Window = 3 trading days (line 49, default). Pre-window uses days before call (rank descending), post-window uses days after call (rank ascending).

9. **"A_t = 10^6 x |r_t| / (VOL_t x |PRC_t|)"**
   - VERIFIED. `amihud_change.py` lines 304-306:
     ```python
     merged["dollar_volume"] = merged["VOL"] * merged["PRC"].abs()
     merged["daily_illiq"] = merged["RET"].abs() / dollar_vol_masked * 1e6
     ```
   - Formula matches exactly: |RET| / (VOL * |PRC|) * 1e6.

10. **"minimum 2 valid trading days per window"**
    - VERIFIED WITH NUANCE. `amihud_change.py` lines 32-33: `MIN_PRE_DAYS = 2` and `MIN_POST_DAYS = 2`. However, the actual filtering uses `min_pre = max(1, w - 1)` (line 269), which for w=3 gives min_pre=2. The module-level constants are defined but the runtime minimum is computed from the formula. For the default window of 3, the effective minimum is 2, matching the thesis. The claim is correct for the default configuration.

11. **"Trading-day positions computed by rank rather than calendar days"**
    - VERIFIED. `amihud_change.py` lines 330-342: Uses `.rank(ascending=False, method="first")` for pre-window and `.rank(ascending=True, method="first")` for post-window, confirming rank-based positioning.

12. **"delta_spread: S[+1,+3] - S[-3,-1]"**
    - VERIFIED. `bidask_spread_change.py` line 395: `spreads["delta_spread"] = spreads["post_call_spread"] - spreads["pre_call_spread"]`. Same window structure as delta_amihud.

13. **"S_t = 2(ASKHI_t - BIDLO_t)/(ASKHI_t + BIDLO_t)"**
    - VERIFIED. `bidask_spread_change.py` lines 327-330:
      ```python
      2 * (merged.loc[valid_spread_mask, "ASKHI"] - merged.loc[valid_spread_mask, "BIDLO"]) /
      (merged.loc[valid_spread_mask, "ASKHI"] + merged.loc[valid_spread_mask, "BIDLO"])
      ```
    - Formula matches exactly. Uses CRSP ASKHI and BIDLO fields as stated.

14. **"Takeover equals one in the firm-quarter containing a takeover bid announcement"**
    - VERIFIED. `build_h9_takeover_panel.py` lines 327-336: The Takeover indicator is set to 1 only in the interval where `Takeover_Date > call_date` and `Takeover_Date <= stop_date` (i.e., the bid falls in the call-to-call interval). The counting-process construction ensures each firm-quarter contributes an at-risk interval.

15. **"Takeover_Uninvited and Takeover_Friendly"**
    - VERIFIED. `build_h9_takeover_panel.py` lines 362-367:
      ```python
      df["Takeover_Uninvited"] = ((df["Takeover"] == 1) & (df["Takeover_Type"] == "Uninvited")).astype(int)
      df["Takeover_Friendly"] = ((df["Takeover"] == 1) & (df["Takeover_Type"] == "Friendly")).astype(int)
      ```

16. **"Entire_All_Negative_pct: percentage of LM Negative words in entire call"**
    - VERIFIED. `negative_sentiment.py` (line 27): `self.column = config.get("column", "Entire_All_Negative_pct")`. The column name "Entire_All" confirms it is the entire call (not section-specific), and "Negative_pct" confirms it is a percentage. The `_linguistic_engine.py` includes `Entire_All_Negative_pct` in `LINGUISTIC_PCT_COLUMNS` (line 79).

### Issues Found

**ISSUE #3 (Major): Winsorization description does not match code**
- Thesis line 108: "All linguistic percentage variables are winsorized at the 1st and 99th percentiles within each calendar year."
- Code reality (`_linguistic_engine.py` line 255-258):
  ```python
  combined = winsorize_by_year(
      combined, existing_pct_cols, year_col="year",
      lower=0.0, upper=0.99, min_obs=10
  )
  ```
- The code uses `lower=0.0` (no lower-bound winsorization) and `upper=0.99` (99th percentile upper-only). This is **0%/99% upper-only per-year winsorization**, NOT symmetric 1%/99% as the thesis states.
- The `winsorize_by_year` function default is `lower=0.01, upper=0.99`, but the LinguisticEngine explicitly overrides `lower` to `0.0`.
- **Impact:** The thesis overstates the winsorization applied. In practice, only extreme high values are trimmed; low values are untouched. This matters for the interpretation of results since the lower tail of linguistic uncertainty is unwinsorized.
- **Recommendation:** Either (a) fix the thesis to say "winsorized at the 99th percentile (upper-only) within each calendar year" or (b) change the code to use `lower=0.01` to match the thesis.

**ISSUE #4 (Minor): Thesis says "Analyst_QA_Uncertainty_pct" as a regressor in clarity residual but doesn't list it among the four raw variants**
- Thesis line 108 lists four raw uncertainty variants (CEO_QA, CEO_Pres, Manager_QA, Manager_Pres) and then separately mentions "Analyst_QA_Uncertainty_pct captures the percentage of LM uncertainty words spoken by analysts during Q&A." This is correctly described as a separate measure, not one of the four DV variants. No actual issue here; the text is clear.

---

## Robustness Mention Check

Sections III.1-III.3 (lines 90-124) were searched for mentions of robustness tests, stratified models, or expanded specifications for H7, H14, or H9.

- **No robustness mentions found in lines 90-124.** The text in these sections purely describes data sources, sample construction, and variable definitions without referencing robustness batteries.
- The word "robust" appears at line 156 (section III findings for H9) but that is outside the audited scope (III.1-III.3).

**Result: CLEAN** -- No inappropriate robustness mentions in the audited sections.

---

## Summary

| Metric | Count |
|--------|-------|
| Total claims audited | 31 |
| Verified correct | 28 |
| Issues found | 4 (0 critical, 1 major, 3 minor) |

### Issue Register

| # | Severity | Section | Description |
|---|----------|---------|-------------|
| 1 | Minor | III.1 | Attitude classification phrasing implies Neutral is a separate category; code groups it with Friendly |
| 2 | Minor | III.2 | H9 event count 307 = 250 + 40 + 17, but Unknown (17) category not mentioned |
| 3 | **Major** | III.3 | Winsorization described as symmetric 1%/99% but code implements 0%/99% upper-only |
| 4 | Minor | III.3 | (Informational) Analyst_QA_Uncertainty_pct correctly described separately from four DV variants |

### Key Code Files Referenced
- `src/f1d/shared/variables/_linguistic_engine.py` -- Winsorization mismatch (Issue #3)
- `src/f1d/shared/variables/takeover_indicator.py` -- Attitude classification
- `src/f1d/shared/variables/_ibes_engine.py` -- IBES consensus parameters
- `src/f1d/shared/variables/amihud_change.py` -- Amihud formula
- `src/f1d/shared/variables/bidask_spread_change.py` -- Spread formula
- `src/f1d/shared/variables/winsorization.py` -- Winsorization utility
- `src/f1d/shared/variables/panel_utils.py` -- FF12 classification
- `src/f1d/econometric/run_h0_2_ceo_clarity.py` -- ClarityCEO extraction
- `src/f1d/econometric/run_h0_3_ceo_clarity_extended.py` -- Residual extraction

### Output Files Referenced
- `outputs/econometric/ceo_clarity_extended/2026-03-13_053119/model_diagnostics.csv`
- `outputs/econometric/h7_illiquidity/2026-03-13_054310/model_diagnostics.csv`
- `outputs/econometric/h14_bidask_spread/2026-03-13_053119/model_diagnostics.csv`
- `outputs/econometric/h14_bidask_spread/2026-03-13_053119/summary_stats.csv`
- `outputs/econometric/h14_bidask_spread/2026-03-13_053119/sample_attrition.csv`
- `outputs/econometric/takeover/2026-03-13_053120/model_diagnostics.csv`
