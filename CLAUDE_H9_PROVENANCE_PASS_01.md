File: CLAUDE_H9_PROVENANCE_PASS_01.md
Scope: H9 provenance accuracy audit only
Edits made: None
Model/code changes made: None
Status: Complete

# H9 Provenance Audit — Pass 01

# Task 1 — File Inventory

| Item Type | Path | Exists? | Referenced by H9 provenance? | Notes |
|-----------|------|---------|------------------------------|-------|
| Provenance | `docs/provenance/H9.md` | Yes | Yes (primary) | Main provenance file (741 lines), authoritative |
| Provenance | `docs/provenance/Audits/AUDIT_H9.md` | Yes | Yes | Prior audit (2026-03-01), supplementary |
| Provenance | `docs/provenance/Audits/AUDIT_REVERIFICATION_H9.md` | Yes | No | Re-verification record |
| Script | `src/f1d/variables/build_h9_takeover_panel.py` | Yes | Yes | Stage 3 panel builder |
| Script | `src/f1d/econometric/run_h9_takeover_hazards.py` | Yes | Yes | Stage 4 regression |
| Script | `src/f1d/shared/variables/takeover_indicator.py` | Yes | Yes | SDC takeover builder |
| Panel (referenced) | `outputs/variables/takeover/2026-03-10_175246/` | **Yes** | Yes (H9.md:734) | **VERIFIED EXISTS** |
| Regression (referenced) | `outputs/econometric/takeover/2026-03-10_175654/` | **Yes** | Yes (H9.md:735) | **VERIFIED EXISTS** |
| Panel (legacy cmd) | `outputs/variables/takeover/2026-02-28_152253/` | Yes | Yes (H9.md:214, 305-337) | Stale reference in verification commands |
| Output | `takeover_panel.parquet` | Yes | Yes | Latest: 27,773 rows |
| Output | `model_diagnostics.csv` | Yes | Yes | 9 models (3 variants × 3 event types) |
| Output | `hazard_ratios.csv` | Yes | Yes | 91 coefficient rows |
| Output | `takeover_table.tex` | Yes | Yes | **MALFORMED** — Issue 7 OPEN |
| Output | `report_step4_takeover.md` | Yes | Yes | Stale description on line 8 |
| Output | `report_step3_takeover.md` | Yes | Yes | Correct counts |
| SDC Data | `inputs/SDC/sdc-ma-merged.parquet` | Yes | Yes | 142,457 raw rows |
| Manifest | `outputs/1.4_AssembleManifest/.../master_sample_manifest.parquet` | Yes | Yes | 112,968 rows |
| Clarity Scores | `outputs/econometric/ceo_clarity/.../clarity_scores.parquet` | Yes | Yes | 2,486 CEO scores |
| Manager Scores | `outputs/econometric/manager_clarity/.../clarity_scores.parquet` | No | Yes (H9.md:198) | "NOT GENERATED" per provenance |

**Authority Assessment:** `docs/provenance/H9.md` is the authoritative provenance file. It is the most comprehensive (741 lines) and is actively maintained (last updated 2026-03-10 per changelog at line 738-740).

---

# Task 2 — Auditable Claims Register

| Claim ID | Claim Category | Exact Claim Text | Where It Appears (path + heading) | Needs Verification Against |
|----------|----------------|------------------|-----------------------------------|---------------------------|
| C001 | Research Question | "Does CEO speech clarity affect the probability of receiving a takeover bid?" | H9.md:10 | N/A (conceptual) |
| C002 | Estimation Unit | "Firm-year interval (counting-process format for survival analysis)" | H9.md:11 | Panel structure |
| C003 | Model Family | "Cox Proportional Hazards with Time-Varying Covariates" | H9.md:18 | Code implementation |
| C004 | Estimator | "lifelines.CoxTimeVaryingFitter (counting-process format)" | H9.md:19 | Code imports |
| C005 | Event Variables | "Takeover, Takeover_Uninvited, Takeover_Friendly" | H9.md:28 | Panel columns + code |
| C006 | Event Coding | "Binary: 1 if firm received takeover bid in that interval, 0 otherwise (censored)" | H9.md:29 | Panel data + code |
| C007 | Sample Filter | "Main sample: FF12 codes 1-7, 9-10, 12 (excludes Finance=11, Utility=8)" | H9.md:40 | Code filter |
| C008 | Model Variants | "CEO, CEO_Residual, Manager_Residual" | H9.md:44-48 | Code MODEL_VARIANTS |
| C009 | Controls | "Size, BM, Lev, ROA, EPS_Growth, StockRet, MarketRet, SurpDec" | H9.md:39 | Code FINANCIAL_CONTROLS |
| C010 | Standard Errors | "Robust (default from lifelines)" | H9.md:58 | Code implementation |
| C011 | No Stratification | "Stratification: None" | H9.md:56 | Code implementation |
| C012 | No Frailty | "Frailty/Random Effects: None" | H9.md:57 | Code implementation |
| C013 | Panel Row Count | "27,773 firm-year intervals" | H9.md:169, 303 | Panel parquet |
| C014 | Unique Firms | "2,415" | H9.md Change Log:738 | Panel data |
| C015 | Event Firms | "676 / 2,415 (28.0%)" | H9.md:302 | Panel data |
| C016 | Takeover Types | "Friendly: 556, Uninvited: 83, Unknown: 37" | H9.md:537-540 | Panel firm-level breakdown |
| C017 | ClarityCEO Coverage | "16,519 / 27,773 = 59.5%" | H9.md:423 | Panel null check |
| C018 | CEO_Clarity_Residual Coverage | "11,802 / 27,773 = 42.5%" | H9.md:424 | Panel null check |
| C019 | Manager_Clarity_Residual Coverage | "15,499 / 27,773 = 55.8%" | H9.md:425 | Panel null check |
| C020 | CEO_QA_Uncertainty Coverage | "20,983 / 27,773 = 75.6%" | H9.md:426 | Panel null check |
| C021 | Manager_QA_Uncertainty Coverage | "27,498 / 27,773 = 99.0%" | H9.md:427 | Panel null check |
| C022 | SDC Raw Row Count | "142,457" | H9.md:196 | SDC parquet |
| C023 | SDC US Public Count | "8,784 US Public" | H9.md:196 | SDC parquet (unfiltered) |
| C024 | SDC Filtered Count | "5,820" (implied by takeover_indicator.py filter) | Code:takeover_indicator.py:115-121 | SDC parquet (filtered) |
| C025 | SDC "No Applicable" Count | "81 deals in filtered SDC" | H9.md:654 | SDC parquet |
| C026 | Main Sample Intervals | "21,652 intervals" | H9.md:176, report_step3 | Panel filter |
| C027 | CEO Variant N Intervals | "12,139 intervals" | H9.md:177, model_diagnostics.csv | Regression output |
| C028 | CEO Variant Event Firms | "349" (All), "45" (Uninvited), "346" (Friendly) | model_diagnostics.csv | Regression output |
| C029 | CEO_Clarity_Residual HR | "1.9959" (All), "2.0913" (Uninvited), "1.4831" (Friendly) | H9.md:588, 591, 594 | hazard_ratios.csv |
| C030 | Issue 1 Status | "RESOLVED 2026-03-10" | H9.md:637, 647 | Code MODEL_VARIANTS |
| C031 | Issue 2 Status | "INVESTIGATED 2026-03-10" | H9.md:649, 663 | Code logging |
| C032 | Issue 3 Status | "VERIFIED via model_diagnostics.csv" | H9.md:665, 673 | model_diagnostics.csv |
| C033 | Issue 4 Status | "VERIFIED via coverage check" | H9.md:675, 683 | Panel data |
| C034 | Issue 5 Status | "VERIFIED via hazard_ratios.csv" | H9.md:685, 693 | hazard_ratios.csv |
| C035 | Issue 6 Status | "RESOLVED 2026-03-10" | H9.md:695, 706 | Panel data (negative durations) |
| C036 | Issue 7 Status | "OPEN" | H9.md:708, 727 | takeover_table.tex |
| C037 | Panel Run ID | "2026-03-10_175246" | H9.md:734 | Directory existence |
| C038 | Regression Run ID | "2026-03-10_175654" | H9.md:735 | Directory existence |
| C039 | ClarityManager NOT GENERATED | "NOT GENERATED" | H9.md:198 | File existence |
| C040 | Negative Duration Fix | "Invalid firms are now skipped with warning" | H9.md:704, code:382-391 | Code implementation |
| C041 | Negative Duration Assert | "assertion after panel construction" | H9.md:703, code:466-473 | Code implementation |
| C042 | Duration Column | "duration" variable listed | H9.md:133 (SUMMARY_STATS_VARS) | Panel columns |
| C043 | Report Description | "Regime and CEO variants" | report_step4_takeover.md:8 | Report content |
| C044 | Issue 1 Claim | "Only CEO variant remains" | H9.md:647 | Model variants documentation |
| C045 | Cause-Specific Event Coding | "Takeover_Uninvited = 1 if Takeover_Type == 'Uninvited'" | H9.md:348, code:250 | Code implementation |
| C046 | Min Event Firms Threshold | "Minimum 5 event firms required to fit a model" | H9.md:450-456, code:419-421 | Code implementation |

---

# Task 3 — Internal Contradictions

### CONTRADICTION #1: "Only CEO variant remains" vs. 3 Variants Documented
**Severity: MAJOR**

| Field | Value |
|-------|-------|
| **Statement A** | "Verification Status: RESOLVED. Dead code removed. **Only CEO variant remains.**" (H9.md:647) |
| **Statement B** | "**Model Variants** (extended 2026-03-10): CEO, CEO_Residual, Manager_Residual" (H9.md:42-48) |
| **Why they conflict** | Statement A claims only CEO variant exists, but Statement B documents 3 variants including two residual variants. The Estimation Spec Register (H9.md:460-485) also documents 9 models (3 variants × 3 event types). |
| **Resolution** | Statement A is FALSE. There are 3 variants, not 1. The text should say "Regime variant removed" not "Only CEO variant remains." |

### CONTRADICTION #2: Verification Command Assert Value Mismatch
**Severity: MINOR**

| Field | Value |
|-------|-------|
| **Statement A** | `assert len(h9_panel) == 27_787` (H9.md:215) |
| **Statement B** | "Panel rows: 27,773" (H9.md:520) and changelog "corrected row counts (27,787→27,773)" (H9.md:738) |
| **Why they conflict** | The verification command has stale assert value 27,787 but the corrected value is 27,773. |
| **Resolution** | The assert should be updated to 27,773. |

### CONTRADICTION #3: SDC Count "8,784 US Public" is Misleading
**Severity: MINOR**

| Field | Value |
|-------|-------|
| **Statement A** | "142,457" raw rows, "8,784 US Public" post-clean rows (H9.md:196) |
| **Statement B** | The actual filtered SDC used by the pipeline is **5,820** deals (2002-2018, US Public, Completed/Withdrawn/Pending) |
| **Why they conflict** | The 8,784 count is pre-filter (all years, all statuses). The actual pipeline uses 5,820. This is misleading because the provenance claims "Post-Clean Rows: 8,784" but that's not what the pipeline uses. |
| **Resolution** | Clarify: "8,784 US Public (unfiltered); 5,820 filtered (2002-2018, Completed/Withdrawn/Pending)" |

### CONTRADICTION #4: Report Description "Regime and CEO variants" is Stale
**Severity: MINOR**

| Field | Value |
|-------|-------|
| **Statement A** | "Model 1 (Cox PH All): All takeovers — **Regime and CEO variants**" (report_step4_takeover.md:8) |
| **Statement B** | Model diagnostics show 3 variants: CEO, CEO_Residual, Manager_Residual (model_diagnostics.csv, H9.md:44-48) |
| **Why they conflict** | The report description references deprecated "Regime" variant and omits the two residual variants. |
| **Resolution** | Update report description to "CEO, CEO_Residual, Manager_Residual variants" |

### CONTRADICTION #5: "duration" Column Listed But Never Created
**Severity: MINOR**

| Field | Value |
|-------|-------|
| **Statement A** | SUMMARY_STATS_VARS includes `{"col": "duration", "label": "Duration (years)"}` (H9.md:133, code:133) |
| **Statement B** | The `duration` column is **NOT** in the panel. It is computed implicitly as `stop - start` but never materialized. |
| **Why they conflict** | The variable list includes a column that doesn't exist. The code silently skips it (`if v["col"] in df.columns`), but this is misleading. |
| **Resolution** | Either create the duration column or remove it from SUMMARY_STATS_VARS. |

---

# Task 4 — Repo Truth Check

| Claim ID | Verification Status | Evidence | Source Path(s) | Exact Follow-up Needed |
|----------|---------------------|----------|----------------|------------------------|
| C003 | **VERIFIED** | `from lifelines import CoxTimeVaryingFitter` at line 80 | `run_h9_takeover_hazards.py:80` | None |
| C005 | **VERIFIED** | `Takeover`, `Takeover_Type` columns in panel; cause-specific indicators created at lines 250-251 | Panel parquet, `run_h9_takeover_hazards.py:250-251` | None |
| C006 | **PARTIAL** | `Takeover=1` only in last interval per firm (correct), but cause-specific indicators are BUGGED (see C045) | Panel data, code:250-251 | Fix cause-specific event coding |
| C007 | **VERIFIED** | `MAIN_SAMPLE_EXCLUDE_FF12 = [8, 11]` at line 175; `~panel["ff12_code"].isin([8, 11])` at line 243 | `run_h9_takeover_hazards.py:175, 243` | None |
| C008 | **VERIFIED** | `MODEL_VARIANTS` dict has 3 entries: CEO, CEO_Residual, Manager_Residual at lines 149-165 | `run_h9_takeover_hazards.py:149-165` | None |
| C009 | **VERIFIED** | `FINANCIAL_CONTROLS = ["Size", "BM", "Lev", "ROA", "EPS_Growth", "StockRet", "MarketRet", "SurpDec"]` at lines 108-117 | `run_h9_takeover_hazards.py:108-117` | None |
| C010 | **VERIFIED** | No explicit robust=True; lifelines uses robust by default. No cluster argument passed. | `run_h9_takeover_hazards.py:424-432` | None |
| C011 | **VERIFIED** | No stratification argument passed to CoxTimeVaryingFitter | `run_h9_takeover_hazards.py:424-432` | None |
| C012 | **VERIFIED** | No frailty argument passed to CoxTimeVaryingFitter | `run_h9_takeover_hazards.py:424-432` | None |
| C013 | **VERIFIED** | `len(panel) = 27,773` confirmed via query | Panel parquet query | None |
| C014 | **VERIFIED** | `panel['gvkey'].nunique() = 2,415` confirmed via query | Panel parquet query | None |
| C015 | **VERIFIED** | `groupby('gvkey')['Takeover'].max().sum() = 676` confirmed via query | Panel parquet query | None |
| C016 | **VERIFIED** | Firm-level breakdown: Friendly=556, Uninvited=83, Unknown=37, None=1,739 confirmed | Panel parquet query | None |
| C017 | **VERIFIED** | ClarityCEO: 16,519 non-null (59.5%) confirmed via query | Panel parquet query | None |
| C018 | **VERIFIED** | CEO_Clarity_Residual: 11,802 non-null (42.5%) confirmed via query | Panel parquet query | None |
| C019 | **VERIFIED** | Manager_Clarity_Residual: 15,499 non-null (55.8%) confirmed via query | Panel parquet query | None |
| C020 | **VERIFIED** | CEO_QA_Uncertainty_pct: 20,983 non-null (75.6%) confirmed via query | Panel parquet query | None |
| C021 | **VERIFIED** | Manager_QA_Uncertainty_pct: 27,498 non-null (99.0%) confirmed via query | Panel parquet query | None |
| C022 | **VERIFIED** | SDC raw count: 142,457 confirmed via query | `inputs/SDC/sdc-ma-merged.parquet` | None |
| C023 | **VERIFIED** | US Public (unfiltered): 8,784 confirmed via query | SDC parquet query | Clarify in provenance |
| C024 | **VERIFIED** | Filtered SDC (2002-2018, US Public, Completed/Withdrawn/Pending): 5,820 confirmed via query | SDC parquet query | Add to provenance |
| C025 | **VERIFIED** | "No Applicable" count in filtered SDC: 81 confirmed via query | SDC parquet query | None |
| C026 | **VERIFIED** | Main sample rows = 21,652 confirmed via query | Panel parquet query | None |
| C027 | **VERIFIED** | CEO variant n_intervals = 12,139 confirmed | `model_diagnostics.csv` row 0 | None |
| C028 | **VERIFIED** | CEO All: 349 events; CEO Uninvited: 45; CEO Friendly: 346 confirmed | `model_diagnostics.csv` | None |
| C029 | **VERIFIED** | CEO_Clarity_Residual HR values match: 1.9959 (All), 2.0913 (Uninvited), 1.4831 (Friendly) | `hazard_ratios.csv` rows 10, 40, 70 | None |
| C030 | **PARTIAL** | Regime entry removed from MODEL_VARIANTS, but Issue 1 text says "Only CEO variant remains" which is FALSE (3 variants exist) | `run_h9_takeover_hazards.py:149-165`, H9.md:647 | Fix Issue 1 text |
| C031 | **VERIFIED** | Unknown logging added at lines 137-147 in takeover_indicator.py | `takeover_indicator.py:137-147` | None |
| C032 | **VERIFIED** | n_event_firms=45 for Uninvited confirmed | `model_diagnostics.csv` | None |
| C033 | **VERIFIED** | Coverage 16,519/27,773 = 59.5% confirmed | Panel parquet query | None |
| C034 | **VERIFIED** | HR > 1 for residual clarity confirmed | `hazard_ratios.csv` | None |
| C035 | **VERIFIED** | Negative duration rows = 0 confirmed (fix working) | Panel parquet query | None |
| C036 | **VERIFIED** | Issue 7 is OPEN — LaTeX table malformed with wrong headers and empty rows | `takeover_table.tex:10, 29-31` | Fix LaTeX table generator |
| C037 | **VERIFIED** | `outputs/variables/takeover/2026-03-10_175246/` directory exists with all expected files | `ls` command | None |
| C038 | **VERIFIED** | `outputs/econometric/takeover/2026-03-10_175654/` directory exists with all expected files | `ls` command | None |
| C039 | **VERIFIED** | `ClarityManager` NOT in panel columns; only CEO clarity loaded | Panel parquet query | None |
| C040 | **VERIFIED** | Warning + skip at lines 382-391 for firms with exit_year < entry_year | `build_h9_takeover_panel.py:382-391` | None |
| C041 | **VERIFIED** | Assertion at lines 466-473 raises ValueError if negative durations found | `build_h9_takeover_panel.py:466-473` | None |
| C042 | **CONTRADICTED** | `duration` column NOT in panel; SUMMARY_STATS_VARS includes it but code silently skips | Panel columns, code:133 | Remove from SUMMARY_STATS_VARS or create column |
| C043 | **CONTRADICTED** | Report says "Regime and CEO variants" but 3 variants exist | `report_step4_takeover.md:8` | Update report template |
| C044 | **CONTRADICTED** | "Only CEO variant remains" is FALSE — 3 variants exist | H9.md:647 | Update Issue 1 text |
| C045 | **CONTRADICTED** | **CRITICAL BUG**: Cause-specific event coding creates inflated events. Code at line 250: `df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)` sets event=1 for ALL rows of Uninvited firms, not just the last row where Takeover=1. Ratio: 8.5x inflation for Uninvited, 9.2x for Friendly. | `run_h9_takeover_hazards.py:250-251`, panel query | **FIX REQUIRED**: Change to `((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Uninvited")).astype(int)` |
| C046 | **VERIFIED** | `if n_event_firms < 5: return None` at lines 419-421 | `run_h9_takeover_hazards.py:419-421` | None |

---

# Task 5 — Required Redlines

## DELETE

| Target | Location | Problematic Text Summary | Why It Is Wrong |
|--------|----------|--------------------------|-----------------|
| Issue 1 status text | H9.md:647 | "Only CEO variant remains" | FALSE — 3 variants exist (CEO, CEO_Residual, Manager_Residual) |
| Stale verification commands | H9.md:202-218 | Entire verification code block referencing 2026-02-28_152253 and assert 27,787 | Stale paths and wrong assert value |

## REPLACE

| Target | Location | Current Text | Corrected Content |
|--------|----------|--------------|-------------------|
| Issue 1 status | H9.md:647 | "Only CEO variant remains" | "Regime variant removed; 3 variants remain (CEO, CEO_Residual, Manager_Residual)" |
| SDC count row | H9.md:196 | "8,784 US Public" | "5,820 filtered (US Public, 2002-2018, Completed/Withdrawn/Pending); 8,784 unfiltered" |
| Verification assert | H9.md:215 | `assert len(h9_panel) == 27_787` | `assert len(h9_panel) == 27_773` |
| Verification panel path | H9.md:214, 305-337 | `2026-02-28_152253` | `2026-03-10_175246` (or generalize) |
| Report description | run_h9_takeover_hazards.py:531 | "Regime and CEO variants" | "CEO, CEO_Residual, Manager_Residual variants" |
| Cause-specific event coding | run_h9_takeover_hazards.py:250-251 | `(df["Takeover_Type"] == "Uninvited").astype(int)` | `((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Uninvited")).astype(int)` |

## ADD

| Target | Location | Content to Add | Why |
|--------|----------|----------------|-----|
| SDC filtered count | H9.md:196 (table) | New row: "Filtered SDC (pipeline use)" with count 5,820 | Document what pipeline actually uses |
| Issue 7 severity | H9.md:708-727 | "**CRITICAL**: This issue blocks publication of the 9-model structure. Residual variant results are invisible in the table output." | Clarify severity |
| Cause-specific bug documentation | H9.md J.Issues | New Issue 8: "Cause-specific event coding inflates event counts 8-9x. NOT FIXED." | Document the critical bug |
| "What provenance claims about cause-specific coding" note | H9.md:348 | Add note: "WARNING: This definition is incorrectly implemented in code. See Issue 8." | Alert readers |

## LEAVE AS-IS

| Target | Location | Why |
|--------|----------|-----|
| Model variants table | H9.md:44-48 | Correctly reflects 3 variants |
| Coverage statistics table | H9.md:419-435 | Correctly matches panel data |
| Estimation spec register | H9.md:460-485 | Correctly documents 9 models |
| Hypothesis direction notes | H9.md:486-501 | Correctly notes HR > 1 opposite to H9-A |
| Negative duration fix documentation | H9.md:695-706 | Correctly describes the fix |
| SDC "No Applicable" count | H9.md:654 | Correctly states 81 |
| Run IDs | H9.md:734-735 | Correct; directories exist |

---

# Task 6 — Audit Verdict

## 1. Overall Verdict

**FAIL — MAJOR REVISIONS REQUIRED**

The provenance file documents important claims accurately (row counts, coverage, model structure), but contains several critical issues:

1. **CRITICAL UNFIXED BUG**: The cause-specific event coding (Issue 8 — newly discovered in this audit) inflates event counts 8-9x, invalidating all cause-specific model results. This was identified in the prior audit (AUDIT_H9.md Finding #1) but was **NOT FIXED** despite the prior audit claiming "RESOLVED" status.

2. **CRITICAL OPEN ISSUE**: The LaTeX table (Issue 7) is completely broken — wrong column headers, empty rows for residual variants, misaligned standard errors. This blocks publication.

3. **FALSE CLAIM**: Issue 1 states "Only CEO variant remains" but 3 variants exist.

## 2. Top 10 Most Serious Problems (Ranked)

| Rank | Problem | Severity | Impact |
|------|---------|----------|--------|
| 1 | **Cause-specific event coding bug (Issue 8)** | CRITICAL | Event counts inflated 8-9x. All cause-specific model coefficients, SEs, and p-values are unreliable. Uninvited HR=1.337 (p=0.0015) is NOT trustworthy. |
| 2 | **LaTeX table broken (Issue 7)** | CRITICAL | Residual variant results invisible in table. SEs misaligned. Not publication-ready. |
| 3 | **Issue 1 false claim "Only CEO variant remains"** | MAJOR | Provenance contradicts itself. 3 variants exist but Issue 1 claims 1. |
| 4 | **Report description stale** | MAJOR | Says "Regime and CEO variants" when 3 variants exist. |
| 5 | **SDC count misleading** | MINOR | Claims 8,784 but pipeline uses 5,820. Unfiltered vs filtered not distinguished. |
| 6 | **Verification commands stale** | MINOR | Wrong paths (2026-02-28) and wrong assert (27,787 vs 27,773). |
| 7 | **"duration" column referenced but not created** | MINOR | SUMMARY_STATS_VARS includes it but code silently skips. |
| 8 | **H9-A not supported (substantive finding)** | NOTE | HR > 1 for residual clarity in multiple models. Correctly documented. |
| 9 | **Low residual clarity coverage (42.5%)** | NOTE | Limits sample size for residual variants. Correctly documented. |
| 10 | **Few Uninvited events (N=45)** | NOTE | Wide CIs, potential overfitting. Correctly documented. |

## 3. Safe-to-Do Next (Provenance Cleanup Only)

### Immediate (Before Any Model Interpretation):
1. **Fix cause-specific event coding bug** (run_h9_takeover_hazards.py:250-251)
   ```python
   # CURRENT (BUG):
   df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
   df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)

   # FIXED:
   df[EVENT_UNINVITED_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Uninvited")).astype(int)
   df[EVENT_FRIENDLY_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Friendly")).astype(int)
   ```

2. **Rerun Stage 4** after fix:
   ```bash
   python -m f1d.econometric.run_h9_takeover_hazards
   ```

3. **Acceptance test** after rerun:
   ```python
   for col in ['Takeover_Uninvited', 'Takeover_Friendly']:
       event_rows = df_clean[col].sum()
       event_firms = df_clean.groupby('gvkey')[col].max().sum()
       assert event_rows == event_firms, f"FAIL: {col} has {event_rows} rows != {event_firms} firms"
   ```

### Provenance Updates Only (No Code Changes):
4. Update H9.md:647 — change "Only CEO variant remains" to "Regime variant removed; 3 variants remain"
5. Update H9.md:196 — clarify SDC count (5,820 filtered / 8,784 unfiltered)
6. Update H9.md:202-218 — fix verification commands with correct paths and asserts
7. Add Issue 8 to H9.md documenting the cause-specific event coding bug
8. Escalate Issue 7 severity to CRITICAL with explicit note about invisible residual results

## 4. What I Am NOT Claiming

1. **I did not verify engine-level winsorization.** The provenance claims per-year 1%/99% winsorization for Compustat/CRSP and 0%/99% for linguistic variables. I did not trace through `_compustat_engine.py`, `_crsp_engine.py`, or `_linguistic_engine.py` to verify this.

2. **I did not test the proportional hazards assumption.** No Schoenfeld residual test or log-log plot was run. PH violations would invalidate the Cox model.

3. **I did not verify the CEO clarity score generation.** The provenance claims ClarityCEO comes from `run_h0_2_ceo_clarity.py`. I did not audit that upstream process.

4. **I did not verify the CEO/Manager clarity residual extraction.** The `_clarity_residual_engine.py` file was not audited.

5. **I did not verify the SDC-CUSIP linkage quality.** The 6-char CUSIP match rate was not independently verified.

6. **I did not re-run the regression models.** I verified outputs exist and match provenance claims but did not independently execute the pipeline.

7. **I did not verify the panel builder's call-to-firm-year aggregation logic.** I assumed the aggregation (mean for uncertainty, last for controls) is correctly implemented.

8. **I did not audit the Compustat/CRSP/IBES engines.** I verified the controls list matches the code but did not trace the data construction logic.

---

## Appendix: Evidence for Critical Findings

### Evidence for Cause-Specific Event Coding Bug (Issue 8)

**Code location**: `run_h9_takeover_hazards.py:250-251`
```python
df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)
```

**Panel data verification**:
```
Uninvited event ROWS: 648
Uninvited event FIRMS: 76
Ratio (rows/firms): 8.5x  ← SHOULD BE 1.0x

Friendly event ROWS: 4,311
Friendly event FIRMS: 469
Ratio (rows/firms): 9.2x  ← SHOULD BE 1.0x
```

**Example firm (gvkey=001659, Uninvited takeover)**:
```
start  stop  Takeover  Takeover_Type  Takeover_Uninvited
2002   2003  0         Uninvited      1  ← BUG: should be 0
2003   2004  0         Uninvited      1  ← BUG: should be 0
...
2014   2015  0         Uninvited      1  ← BUG: should be 0
2015   2016  1         Uninvited      1  ← CORRECT: event=1 only here
```

### Evidence for LaTeX Table Bug (Issue 7)

**File**: `outputs/econometric/takeover/2026-03-10_175654/takeover_table.tex`

**Line 10** (wrong headers):
```latex
 & Regime & CEO & Regime & CEO & Regime & CEO \\
```
Should be:
```latex
 & CEO & CEO_Residual & Manager_Residual & CEO & CEO_Residual & Manager_Residual \\
```

**Lines 29-31** (empty rows):
```latex
CEO Clarity Residual &  &  &  &  &  &  \\
Manager Clarity Residual &  &  &  &  &  &  \\
Manager QA Uncertainty &  &  &  &  &  &  \\
```

**Lines 32-41** (SEs without variable names):
```latex
 &  & (0.0845) &  & (0.0915) &  & (0.0290) \\
...
```

### Evidence for Run ID Existence

```
Panel dir (2026-03-10_175246): EXISTS
  - takeover_panel.parquet
  - summary_stats.csv
  - report_step3_takeover.md
  - run_manifest.json

Regression dir (2026-03-10_175654): EXISTS
  - model_diagnostics.csv
  - hazard_ratios.csv
  - takeover_table.tex
  - report_step4_takeover.md
  - cox_ph_all.txt
  - cox_cs_uninvited.txt
  - cox_cs_friendly.txt
  - summary_stats.csv
  - summary_stats.tex
  - sample_attrition.csv
  - sample_attrition.tex
  - run_log.txt
  - run_manifest.json
```

---

**Audit Completed:** 2026-03-11
**Panel Version Audited:** `outputs/variables/takeover/2026-03-10_175246`
**Regression Version Audited:** `outputs/econometric/takeover/2026-03-10_175654`
**Confidence Level:** 95%
