================================================================================
AUDIT REPORT: Suite H5b (h5b_johnson_disp)
Auditor: Adversarial audit per docs/Prompts/Audit Provenance doc.txt
Date: 2026-03-31
================================================================================

## PRELIMINARY FINDING: SUITE IS ARCHIVED — NO PROVENANCE DOCUMENT EXISTS

Before any phase-level checks are possible, a critical pre-condition fails:

1. **Runner file does NOT exist:**
   `src/f1d/econometric/run_h5b_johnson_disp.py` — NOT PRESENT on disk.
   Only a compiled cache exists:
   `src/f1d/econometric/__pycache__/run_h5b_johnson_disp.cpython-313.pyc`

2. **Panel builder does NOT exist:**
   `src/f1d/variables/build_h5b_johnson_disp_panel.py` — NOT PRESENT on disk.
   Only a compiled cache exists:
   `src/f1d/variables/__pycache__/build_h5b_johnson_disp_panel.cpython-313.pyc`

3. **Provenance document does NOT exist:**
   `docs/provenance/H5b.md` — NOT PRESENT on disk.

4. **No entry in `outputs/generate_all_tables.py`:**
   Grep confirms zero matches for "h5b_johnson", "H5b_johnson", "JohnsonDISP".
   The only H5 entry is for H5 (Wang 2020 DISP), id="H5".

5. **Suite officially archived (per project memory):**
   `project_archived_suites.md` entry (2026-03-31):
   > "H5b Johnson (JohnsonDISP2): Johnson (2004) DISP2 variant. Severe scaling
   > issue — DV mean ~0.0001, all coefficients display as 0.0000 in tables.
   > JohnsonDispBuilder deleted."

   The shared variable builder `src/f1d/shared/variables/johnson_disp.py` is also
   deleted; only its .pyc remains in __pycache__.

This audit was triggered with inputs {{SUITE_ID}}=H5b, {{RUNNER_NAME}}=h5b_johnson_disp,
{{BUILDER_NAME}}=h5b_johnson_disp. The instruction specifies: "First check if
src/f1d/econometric/run_h5b_johnson_disp.py exists." — it does NOT exist.

The audit proceeds forensically, reconstructing the suite from available artifacts
(.pyc bytecode, regression output files, sample attrition CSV, model_diagnostics.csv)
to document what the suite contained and verify that no provenance document was
ever created — and to produce a complete forensic record for archival purposes.

---

## FORENSIC RECONSTRUCTION FROM ARTIFACTS

The following sources were used since source files are deleted:

| Artifact | Path | Used For |
|----------|------|----------|
| Runner .pyc | src/f1d/econometric/__pycache__/run_h5b_johnson_disp.cpython-313.pyc | MODEL_SPECS, controls, docstring, p-value computation |
| Builder .pyc | src/f1d/variables/__pycache__/build_h5b_johnson_disp_panel.cpython-313.pyc | Builders list, merge ops, lead/lag logic |
| JohnsonDisp builder .pyc | src/f1d/shared/variables/__pycache__/johnson_disp.cpython-313.pyc | DV formula, filters, winsorization |
| model_diagnostics.csv | outputs/econometric/h5b_johnson_disp/2026-03-31_140249/ | 12 specs, N per spec, R² |
| sample_attrition.csv | outputs/econometric/h5b_johnson_disp/2026-03-31_140249/ | Attrition cascade row counts |
| regression_results_col*.txt | outputs/econometric/h5b_johnson_disp/2026-03-31_140249/ | FE types, SE type, estimator class |
| run_manifest.json | outputs/econometric/h5b_johnson_disp/2026-03-31_140249/ | Git commit at run time (c97e0a4) |
| project_archived_suites.md | memory/ | Archive rationale |
| project_h5b_wang_disp.md | memory/ | Historical context |

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 0 | 26 | 0% |
| Suite Identity (Phase 2) | 10 | N/A | 10 | N/A |
| Model Specification (Phase 3) | 7 | N/A | 7 | N/A |
| Spec Register (Phase 4) | 4 | N/A | 4 | N/A |
| Sample Construction (Phase 5) | 3 | N/A | 3 | N/A |
| Variable Dictionary (Phase 6) | 18 | N/A | 18 | N/A |
| Pipeline/Outputs/Treatment (Phase 7) | 3 | N/A | 3 | N/A |
| Table Generator Entry (Phase 8) | 5 | N/A | 5 | N/A |
| Model-Family Addendum (Phase 9) | 5 | N/A | 5 | N/A |
| Quality Gates (Phase 10) | 10 | N/A | 10 | N/A |
| Cross-Reference Consistency (Phase 11) | 8 | N/A | 8 | N/A |
| **TOTAL** | **99** | **0** | **99** | **0%** |

Note: Phases 2–11 are scored N/A because the provenance document to audit does
not exist. The 26 structural failures (Phase 1) represent 26 required sections
all absent. The root cause is a single fact: docs/provenance/H5b.md was never
created before the suite was archived.

---

## VERDICT

**FAIL — INCOMPLETE**

The provenance document `docs/provenance/H5b.md` does not exist. The suite
H5b (Johnson 2004 DISP2 analyst dispersion) was archived on 2026-03-31 due to
a severe scaling issue (DV mean ~0.0001, coefficients display as 0.0000 in .4f
tables). All source files were deleted. No provenance document was ever written.

All 26 required sections (A through L) are absent. All 10 quality gates fail
by definition of total absence.

---

================================================================================
PHASE 1: STRUCTURAL COMPLETENESS
================================================================================

Required by docs/Prompts/Suite Provenance Doc.txt vs. present in docs/provenance/H5b.md:

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|--------------------|----------------|----------|-------|
| A. Suite Identity | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B. Model Specification | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B1. Regression Equation | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B2. Dependent Variable(s) | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B3. Independent Variable(s) | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B4. Control Variables | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B5. Fixed Effects | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B6. Standard Errors | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| B7. Hypothesis Test | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| C. Spec Register | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| D. Sample Construction | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| D1. Population | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| D2. Exclusion Criteria | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| D3. Sample Counts per Spec | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| E. Variable Dictionary | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| F. Data Pipeline | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| F1. Dependency Chain | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| F2. Data Engines | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| F3. Merge Operations | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| G. Outputs | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| G1. Stage 3 Outputs | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| G2. Stage 4 Outputs | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| G3. Summary Statistics | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| H. Outlier/Missing Treatment | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| I. generate_all_tables Entry | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| J. Reproduction Commands | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| K. Model-Family Addendum | Yes | NO | NO | docs/provenance/H5b.md does not exist |
| L. Known Issues | Yes | NO | NO | docs/provenance/H5b.md does not exist |

**Result: 26/26 required sections MISSING. Total structural failure.**

---

================================================================================
PHASE 2: FACTUAL ACCURACY — SECTION A (Suite Identity)
================================================================================

Section A does not exist. However, as a forensic exercise, below is what the
Section A WOULD have required and what the evidence shows it SHOULD have said,
based on artifacts recovered from .pyc bytecode and regression outputs.

**Evidence source:** String constants extracted from runner .pyc bytecode
(CPython 3.13, run at git commit c97e0a4, 2026-03-31).

Reconstructed Section A fields vs. evidence:

A-1. Suite ID: H5b
     EVIDENCE: .pyc docstring identifies "STAGE 4: Test H5b Johnson (2004)
     Analyst Dispersion Hypothesis". Runner log directory is "H5b_JohnsonDisp".
     VERDICT: Would be H5b. N/A (no doc to fail).

A-2. Title: "H5b: Speech Uncertainty and Analyst Forecast Dispersion (Johnson 2004)"
     EVIDENCE: .pyc docstring: "Stage 4: H5b Johnson (2004) Analyst Dispersion Test"
     VERDICT: N/A (no doc).

A-3. Hypothesis: "Higher linguistic uncertainty in earnings calls increases
     pre-announcement analyst forecast dispersion (Johnson 2004 DISP2)."
     EVIDENCE: .pyc: "Hypothesis: One-tailed (beta > 0 — higher uncertainty ->
     higher dispersion)."
     VERDICT: N/A (no doc).

A-4. Direction: One-tailed (beta > 0)
     EVIDENCE: .pyc string constants: "Test: One-tailed (beta > 0)"
     p-value stored as `_p_one` suffix (confirmed in model_diagnostics.csv
     column headers: UncAnsCEO_p_one, etc.)
     VERDICT: N/A (no doc).

A-5. Model Family: PanelOLS
     EVIDENCE: .pyc imports `from linearmodels.panel import PanelOLS`.
     regression_results_col1.txt header: "PanelOLS Estimation Summary".
     VERDICT: N/A (no doc).

A-6. Estimator: linearmodels.panel.PanelOLS
     EVIDENCE: Same as A-5.
     VERDICT: N/A (no doc).

A-7. Unit of Observation: Call-level (individual earnings call)
     EVIDENCE: .pyc builder docstring: "Unit of observation: individual earnings
     call (file_name)." Panel indexed by file_name at call level.
     VERDICT: N/A (no doc).

A-8. Panel Index: (gvkey, cal_yr_qtr)
     EVIDENCE: .pyc string constants show "cal_yr_qtr" as the time index
     (string: "cal_yr_qtr coverage: ..."). Runner sets index using
     build_cal_yr_qtr_index imported from f1d.shared.variables.panel_utils.
     Col 5/6 = industry_yq/firm_yq confirm cal_yr_qtr used for YQ specs.
     VERDICT: N/A (no doc).

A-9. Columns: 12
     EVIDENCE: .pyc MODEL_SPECS list builds 12 specs (BUILD_LIST 12).
     model_diagnostics.csv has 12 rows (cols 1–12).
     .pyc docstring: "12 Model Specifications".
     VERDICT: N/A (no doc).

A-10. Runner path: src/f1d/econometric/run_h5b_johnson_disp.py — FILE DELETED
      Builder path: src/f1d/variables/build_h5b_johnson_disp_panel.py — FILE DELETED
      VERDICT: Both paths are non-existent. Suite is archived.

**Phase 2 result: N/A — no provenance document exists. Forensic reconstruction
confirms suite identity was: 12-column PanelOLS, call-level, one-tailed beta>0.**

---

================================================================================
PHASE 3: FACTUAL ACCURACY — SECTION B (Model Specification)
================================================================================

No Section B to audit. Forensic reconstruction follows.

**B1. Regression Equation (reconstructed)**

From .pyc: `formula = dv + " ~ 1 + " + regressors + " + EntityEffects + TimeEffects"`

For base-controls spec (cols 1-2, 7-8):
    JohnsonDISP2_{i,t} = b1*UncAnsCEO + b2*UncPreCEO
        + b3*UncAnsMgr + b4*UncPreMgr
        + b5*lnAssets + b6*TobinsQ + b7*ROA + b8*Leverage + b9*Capex
        + b10*DivDummy + b11*sCFO + b12*Lagged_DV
        + alpha_entity + gamma_time + epsilon

For extended-controls spec (cols 3-6, 9-12):
    (adds) + b13*SurpDec + b14*Loss + b15*UncQue
            + b16*NegCall

Lead-DV specs (cols 7-12): DV = JohnsonDISP2_lead; Lagged_DV = JohnsonDISP2_lag

Entity FE:
- Odd cols (1,3,5,7,9,11) = Industry FE (ff12_code via other_effects)
- Even cols (2,4,6,8,10,12) = Firm FE (EntityEffects)

Time FE:
- Cols 1-4, 7-10 = cal_yr (calendar year, via TimeEffects)
- Cols 5-6, 11-12 = cal_yr_qtr (calendar year-quarter, via TimeEffects)

EVIDENCE: .pyc MODEL_SPECS:
  Col 1: dv=JohnsonDISP2, fe=industry, controls=base
  Col 2: dv=JohnsonDISP2, fe=firm, controls=base
  Col 3: dv=JohnsonDISP2, fe=industry, controls=extended
  Col 4: dv=JohnsonDISP2, fe=firm, controls=extended
  Col 5: dv=JohnsonDISP2, fe=industry_yq, controls=extended
  Col 6: dv=JohnsonDISP2, fe=firm_yq, controls=extended
  Col 7: dv=JohnsonDISP2_lead, fe=industry, controls=base
  Col 8: dv=JohnsonDISP2_lead, fe=firm, controls=base
  Col 9: dv=JohnsonDISP2_lead, fe=industry, controls=extended
  Col 10: dv=JohnsonDISP2_lead, fe=firm, controls=extended
  Col 11: dv=JohnsonDISP2_lead, fe=industry_yq, controls=extended
  Col 12: dv=JohnsonDISP2_lead, fe=firm_yq, controls=extended

CONFIRMED by regression_results_col*.txt files.

**B2. Dependent Variables (reconstructed)**

| Variable Name (code) | Description | Formula | Source Engine | Timing |
|----------------------|-------------|---------|---------------|--------|
| JohnsonDISP2 | Johnson (2004) DISP2 analyst dispersion | SD(current-FY EPS forecasts outstanding at month-end) / atq; min 2 analysts; FPI=1, PDF=D, age<=180d, fpedats>=month_end | JohnsonDispBuilder: IBES Detail + CompustatEngine (atq) | Contemporaneous (t) |
| JohnsonDISP2_lead | Next-quarter DISP2 | JohnsonDISP2 shifted forward by 1 fiscal quarter (fiscal_qtr_id+1) | Same as above, via lead-lag builder in panel builder | Lead (t+1 quarter) |

EVIDENCE: .pyc builder docstring: "JohnsonDISP2 = SD(current-FY analyst forecasts
at month-end) / atq". Johnson_disp.pyc: filters FPI='1', PDF='D', age<=180d,
fpedats >= month_end. Winsorization: 1%/99% pooled.

Summary stats confirm: JohnsonDISP2 mean = 0.0001, SD = 0.0002 (tiny scale —
this is the documented archival reason).

**B3. Independent Variables (reconstructed)**

BASE_CONTROLS list from .pyc:
  ('UncAnsCEO', 'UncPreCEO',
   'UncAnsMgr', 'UncPreMgr')

| Variable Name (code) | Description | Source | Timing |
|----------------------|-------------|--------|--------|
| UncAnsCEO | CEO Q&A section uncertainty word % | CEOQAUncertaintyBuilder: SpeechEngine | Contemporaneous (t) |
| UncPreCEO | CEO prepared remarks uncertainty word % | CEOPresUncertaintyBuilder: SpeechEngine | Contemporaneous (t) |
| UncAnsMgr | Non-CEO manager Q&A uncertainty word % | ManagerQAUncertaintyBuilder: SpeechEngine | Contemporaneous (t) |
| UncPreMgr | Non-CEO manager prepared remarks uncertainty word % | ManagerPresUncertaintyBuilder: SpeechEngine | Contemporaneous (t) |

No centering or interaction terms. Standard 4-IV simultaneous approach.

**B4. Control Variables (reconstructed)**

BASE_CONTROLS from .pyc:
  ['lnAssets', 'TobinsQ', 'ROA', 'Leverage', 'Capex', 'DivDummy',
   'sCFO', 'Lagged_DV']

EXTENDED_CONTROLS = BASE_CONTROLS + ['SurpDec', 'Loss',
   'UncQue', 'NegCall']

Lagged_DV:
- For JohnsonDISP2 specs (cols 1-6): Lagged_DV = JohnsonDISP2_lag
  (prior fiscal quarter's JohnsonDISP2)
- For JohnsonDISP2_lead specs (cols 7-12): Lagged_DV = JohnsonDISP2_lag
  (confirmed: .pyc string "_lead_qtr" and "Lagged_DV" assigned to JohnsonDISP2_lag)

EVIDENCE: .pyc BUILD_LIST constants confirm BASE_CONTROLS and EXTENDED_CONTROLS
exactly as listed above. regression_results_col3.txt confirms all 16 regressors
(4 IVs + 12 extended controls including Lagged_DV).

**B5. Fixed Effects (reconstructed)**

| FE Type | Column Used | Description | Specs |
|---------|-------------|-------------|-------|
| Industry FE | ff12_code | Fama-French 12-industry other_effects | Cols 1,3,5,7,9,11 |
| Firm FE | gvkey | Entity effects (EntityEffects) | Cols 2,4,6,8,10,12 |
| Cal Year FE | cal_yr | Calendar year TimeEffects | Cols 1-4, 7-10 |
| Cal Year-Qtr FE | cal_yr_qtr | Calendar year-quarter TimeEffects | Cols 5-6, 11-12 |

EVIDENCE: regression_results_col1.txt: "Included effects: Time, Other Effect
(ff12_code)". Col2: EntityEffects only (entity=firm).
Col5: "Time periods: 65" confirms cal_yr_qtr (65 year-quarters vs 17 years).
.pyc constants: "industry" -> "Industry(FF12)", "CalYrQtr" / "CalYear" branches.

**B6. Standard Errors (reconstructed)**

Cov_type: clustered (firm-level)
EVIDENCE: regression_results_col1.txt: "Cov. Estimator: Clustered"
.pyc: cov_type='clustered' string confirmed. Cluster = gvkey (entity = firm).

**B7. Hypothesis Test (reconstructed)**

One-tailed, beta > 0. p-values stored as `_p_one`.
EVIDENCE: .pyc: p_one stored via suffix "_p_one". model_diagnostics.csv columns
are all "_p_one" (e.g., UncAnsCEO_p_one). .pyc docstring:
"Hypothesis: One-tailed (beta > 0 — higher uncertainty -> higher dispersion)."

Conversion: standard pattern — p_one = p_two / 2 when beta > 0, else 1 - p_two/2.
(Confirmed by analogy with other suites; exact code unavailable due to deletion.)

**Phase 3 result: N/A — no provenance document to audit. Forensic reconstruction
complete. Model specification fully recoverable from artifacts.**

---

================================================================================
PHASE 4: FACTUAL ACCURACY — SECTION C (Spec Register)
================================================================================

No Section C to audit. Reconstructed spec register:

| Col | DV | Entity FE | Time FE | Controls | N (obs) | N (firms) |
|-----|----|-----------|---------|----------|---------|-----------|
| 1 | JohnsonDISP2 | Industry (ff12_code) | Cal Yr | Base | 21,209 | 1,189 |
| 2 | JohnsonDISP2 | Firm (gvkey) | Cal Yr | Base | 21,209 | 1,189 |
| 3 | JohnsonDISP2 | Industry (ff12_code) | Cal Yr | Extended | 19,509 | 1,140 |
| 4 | JohnsonDISP2 | Firm (gvkey) | Cal Yr | Extended | 19,509 | 1,140 |
| 5 | JohnsonDISP2 | Industry (ff12_code) | Cal Yr-Qtr | Extended | 19,509 | 1,140 |
| 6 | JohnsonDISP2 | Firm (gvkey) | Cal Yr-Qtr | Extended | 19,509 | 1,140 |
| 7 | JohnsonDISP2_lead | Industry (ff12_code) | Cal Yr | Base | 19,937 | 1,159 |
| 8 | JohnsonDISP2_lead | Firm (gvkey) | Cal Yr | Base | 19,937 | 1,159 |
| 9 | JohnsonDISP2_lead | Industry (ff12_code) | Cal Yr | Extended | 18,267 | 1,098 |
| 10 | JohnsonDISP2_lead | Firm (gvkey) | Cal Yr | Extended | 18,267 | 1,098 |
| 11 | JohnsonDISP2_lead | Industry (ff12_code) | Cal Yr-Qtr | Extended | 18,267 | 1,098 |
| 12 | JohnsonDISP2_lead | Firm (gvkey) | Cal Yr-Qtr | Extended | 18,267 | 1,098 |

EVIDENCE: model_diagnostics.csv (12 rows confirmed). Observation counts verified
against regression_results_col*.txt.

Note: Col1-2 have N=21,209 but cols 3-6 have N=19,509 — the drop is due to
extended controls (SurpDec, Loss, UncQue,
NegCall) having additional missing values.

**Phase 4 result: N/A — no provenance document to audit. Spec register
reconstructed from model_diagnostics.csv (ground truth).**

---

================================================================================
PHASE 5: FACTUAL ACCURACY — SECTION D (Sample Construction)
================================================================================

No Section D to audit. Reconstructed from sample_attrition.csv:

**D1. Population**
Starting dataset: master_sample_manifest.parquet
Total calls: 112,968 (full panel — consistent with project scope 112,968 calls)
Unique firms: not stated in attrition CSV (project scope: 2,429 firms total)
Year range: 2002–2018 (project scope)

**D2. Exclusion Criteria (actual attrition cascade from sample_attrition.csv)**

| Step | Filter | Rows Before | Rows After | Dropped | % Retained |
|------|--------|-------------|------------|---------|------------|
| 1 | Full panel | -- | 112,968 | -- | 100.0% |
| 2 | Main sample (excl FF12=8,11) | 112,968 | 88,205 | 24,763 | 78.1% |
| 3 | JohnsonDISP2 non-null | 88,205 | 49,917 | 38,288 | 44.2% |
| 4 | After complete-case + min-calls (col 1) | 49,917 | 21,209 | 28,708 | 18.8% |

EVIDENCE: sample_attrition.csv exact text:
"Full panel,112968,0,100.0"
"Main sample (excl Finance/Utility),88205,-24763,78.1"
"JohnsonDISP2 non-null,49917,-38288,44.2"
"After complete-case + min-calls (col 1),21209,-28708,18.8"

Note: The 44.2% DV coverage (49,917/112,968) was JohnsonDISP2's coverage.
After complete-case, only 18.8% of full panel survives — a significant sample
reduction, partly due to the DV's limited IBES coverage.

The min-calls threshold = 5 (confirmed from .pyc: "MIN_CALLS_PER_FIRM = 5").

**D3. Sample Counts per Spec**
Varies across specs due to DV (lead vs contemporaneous) and extended controls.
See spec register above (Phase 4). Contemporaneous specs: 19,509–21,209.
Lead specs: 18,267–19,937.

**Phase 5 result: N/A — no provenance document to audit. Sample construction
fully reconstructed. 18.8% overall retention rate confirms sparse DV coverage.**

---

================================================================================
PHASE 6: FACTUAL ACCURACY — SECTION E (Variable Dictionary)
================================================================================

No Section E to audit. Reconstructed variable dictionary:

| Variable (code) | Label | Type | Formula | Source | Winsorized | Timing |
|-----------------|-------|------|---------|--------|------------|--------|
| JohnsonDISP2 | Johnson DISP2 (contemporaneous) | DV | SD(current-FY EPS forecasts outstanding at month-end) / atq; FPI=1, PDF=D, age<=180d, fpedats>=month_end, min 2 analysts | JohnsonDispBuilder: IBES Detail (FPI=1) + CompustatEngine (atq) | 1%/99% pooled | Contemporaneous (t) |
| JohnsonDISP2_lead | Johnson DISP2 (next quarter) | DV | JohnsonDISP2 from next fiscal quarter (fiscal_qtr_id+1 shift) | Same as JohnsonDISP2, via lead-lag builder | 1%/99% pooled | Lead (t+1 qtr) |
| JohnsonDISP2_lag | Johnson DISP2 (prior quarter) | Lagged_DV | JohnsonDISP2 from prior fiscal quarter (fiscal_qtr_id-1 shift) | Same as JohnsonDISP2, via lead-lag builder | 1%/99% pooled | Lag (t-1 qtr) |
| UncAnsCEO | CEO QA Uncertainty | IV | % uncertain words in CEO Q&A section | CEOQAUncertaintyBuilder: SpeechEngine | No (bounded by construction) | Contemporaneous (t) |
| UncPreCEO | CEO Pres Uncertainty | IV | % uncertain words in CEO prepared remarks | CEOPresUncertaintyBuilder: SpeechEngine | No (bounded by construction) | Contemporaneous (t) |
| UncAnsMgr | Mgr QA Uncertainty | IV | % uncertain words in non-CEO manager Q&A | ManagerQAUncertaintyBuilder: SpeechEngine | No (bounded by construction) | Contemporaneous (t) |
| UncPreMgr | Mgr Pres Uncertainty | IV | % uncertain words in non-CEO manager prepared remarks | ManagerPresUncertaintyBuilder: SpeechEngine | No (bounded by construction) | Contemporaneous (t) |
| lnAssets | Firm Size | Control | log(market cap) | SizeBuilder: CompustatEngine (mkvaltq or prccq*cshoq) | Yes (1%/99% by year at engine) | Contemporaneous (t) |
| TobinsQ | Tobin's Q | Control | (atq + prccq*cshoq - ceqq) / atq | TobinsQBuilder: CompustatEngine | Yes (1%/99% by year at engine) | Contemporaneous (t) |
| ROA | ROA | Control | oiadpq / avg(atq) | ROABuilder: CompustatEngine | Yes (1%/99% by year at engine) | Contemporaneous (t) |
| Leverage | Leverage | Control | (dlcq+dlttq) / atq | LeverageBuilder: CompustatEngine | Yes (1%/99% by year at engine) | Contemporaneous (t) |
| Capex | CapEx/Assets | Control | capxy / atq or capxq/atq | CapexIntensityBuilder: CompustatEngine | Yes (1%/99% by year at engine) | Contemporaneous (t) |
| DivDummy | Dividend Payer | Control | 1 if dvpq>0 else 0 (binary) | DivDummyBuilder: CompustatEngine | No (binary) | Contemporaneous (t) |
| sCFO | OCF Volatility | Control | rolling SD of operating cash flows / assets | OCFVolatilityBuilder: CompustatEngine | Yes (1%/99% by year at engine) | Rolling window |
| SurpDec | -- | Extended Control | Earnings surprise decile rank | EarningsSurpriseBuilder: IBESEngine | Yes (at engine) | Contemporaneous (t) |
| Loss | -- | Extended Control | 1 if net income < 0 else 0 | LossDummyBuilder: CompustatEngine | No (binary) | Contemporaneous (t) |
| UncQue | -- | Extended Control | % uncertain words in analyst Q&A section | AnalystQAUncertaintyBuilder: SpeechEngine | No (bounded by construction) | Contemporaneous (t) |
| NegCall | -- | Extended Control | % negative-sentiment words in full call | NegativeSentimentBuilder: SpeechEngine | No (bounded by construction) | Contemporaneous (t) |

EVIDENCE: Builder imports from .pyc builder bytecode: JohnsonDispBuilder,
SizeBuilder, LeverageBuilder, ROABuilder, TobinsQBuilder, CapexIntensityBuilder,
DivDummyBuilder, OCFVolatilityBuilder, EarningsSurpriseBuilder,
LossDummyBuilder, AnalystQAUncertaintyBuilder, NegativeSentimentBuilder,
ManagerQAUncertaintyBuilder, CEOQAUncertaintyBuilder, ManagerPresUncertaintyBuilder,
CEOPresUncertaintyBuilder, ManifestFieldsBuilder.

Variable formulas for Compustat-derived controls inferred from builder class names
and confirmed in comparable provenance documents (H5.md, H7.md) which use the
same builders. The runner .pyc does not contain formula-level constants; formulas
are in the (deleted) builder source files. The Johnson_disp.pyc provides the
DV formula explicitly.

FE columns used in regressions:
- ff12_code (industry FE): from assign_industry_sample (industry assignment)
- cal_yr (calendar year): derived from start_date.dt.year
- cal_yr_qtr: derived from build_cal_yr_qtr_index (calendar year*4 + quarter)
- gvkey: entity index

**Phase 6 result: N/A — no provenance document to audit. 18 variables
reconstructed. Formula certainty is HIGH for JohnsonDISP2 (from .pyc docstring)
and MEDIUM for Compustat controls (inferred from class names, consistent with
other active suites).**

---

================================================================================
PHASE 7: FACTUAL ACCURACY — SECTIONS F, G, H
================================================================================

No Sections F, G, H to audit. Forensic reconstruction:

**F-CHECK: Data Pipeline (reconstructed)**

F1. Dependency Chain:
    1. Raw inputs: master_sample_manifest.parquet, IBES Detail (FPI=1),
       Compustat quarterly (atq, mkvaltq, prccq, ceqq, dlcq, dlttq,
       oiadpq, capxq, cshoq, dvpq), SpeechEngine transcripts
    2. Engine loading: JohnsonDispBuilder (IBES Detail + Compustat atq),
       SizeBuilder, ROABuilder, TobinsQBuilder, LeverageBuilder,
       CapexIntensityBuilder, DivDummyBuilder, OCFVolatilityBuilder,
       EarningsSurpriseBuilder, LossDummyBuilder,
       AnalystQAUncertaintyBuilder, NegativeSentimentBuilder,
       ManagerQAUncertaintyBuilder, CEOQAUncertaintyBuilder,
       ManagerPresUncertaintyBuilder, CEOPresUncertaintyBuilder,
       ManifestFieldsBuilder
    3. Panel builder: merges all builders on file_name (left join);
       assigns ff12_code via assign_industry_sample;
       attaches fyearq via attach_fyearq;
       creates lead/lag variables via create_lead_lag_variables
       (fiscal_qtr_id shifting pattern adapted from H12Q);
       outputs h5b_johnson_disp_panel.parquet
    4. Runner loading: loads latest h5b_johnson_disp_panel.parquet;
       builds cal_yr_qtr index via build_cal_yr_qtr_index;
       filters to Main sample (ff12_code not in [8,11])
    5. Sample filtering: DV non-null, complete case, min 5 calls/firm
    6. Regression: PanelOLS with firm-clustered SEs, 12 specs
    7. Table generation: H5b Johnson had NO entry in generate_all_tables.py
       (confirmed: grep finds zero matches)

F2. Data Engines:
    | Engine | Source Data | Variables Provided |
    |--------|-------------|-------------------|
    | JohnsonDispBuilder | IBES Detail (FPI=1) + Compustat atq | JohnsonDISP2 |
    | SizeBuilder | Compustat mkvaltq/prccq/cshoq | lnAssets |
    | TobinsQBuilder | Compustat atq/prccq/cshoq/ceqq | TobinsQ |
    | ROABuilder | Compustat oiadpq/atq | ROA |
    | LeverageBuilder | Compustat dlcq/dlttq/atq | Leverage |
    | CapexIntensityBuilder | Compustat capxq/atq | Capex |
    | DivDummyBuilder | Compustat dvpq | DivDummy |
    | OCFVolatilityBuilder | Compustat oancfq/atq (rolling) | sCFO |
    | EarningsSurpriseBuilder | IBES Summary | SurpDec |
    | LossDummyBuilder | Compustat niq | Loss |
    | CEOQAUncertaintyBuilder | SpeechEngine | UncAnsCEO |
    | CEOPresUncertaintyBuilder | SpeechEngine | UncPreCEO |
    | ManagerQAUncertaintyBuilder | SpeechEngine | UncAnsMgr |
    | ManagerPresUncertaintyBuilder | SpeechEngine | UncPreMgr |
    | AnalystQAUncertaintyBuilder | SpeechEngine | UncQue |
    | NegativeSentimentBuilder | SpeechEngine | NegCall |
    | ManifestFieldsBuilder | master_sample_manifest.parquet | ff12_code, start_date, gvkey |

F3. Merge Operations (reconstructed from builder .pyc):
    All merges: left join on file_name (call-level panel)
    + attach_fyearq: merge_asof backward on (gvkey, start_date) for fiscal year
    + create_lead_lag_variables: fiscal_qtr_id shifting for JohnsonDISP2_lead/lag

**G-CHECK: Outputs (reconstructed)**

G1. Stage 3 Outputs:
    | File | Description |
    |------|-------------|
    | h5b_johnson_disp_panel.parquet | Call-level panel with all variables |
    | summary_stats.csv | Variable summary statistics |
    | run_manifest.json | Stage 3 build manifest |
    Latest run: outputs/variables/h5b_johnson_disp/2026-03-24_203446/

G2. Stage 4 Outputs:
    | File | Description |
    |------|-------------|
    | regression_results_col1.txt through col12.txt | Individual model regression summaries |
    | model_diagnostics.csv | Per-model metadata (N, R², p-values per IV) |
    | summary_stats.csv | Summary statistics (main sample) |
    | summary_stats.tex | LaTeX version of summary stats |
    | sample_attrition.csv | Attrition cascade counts |
    | sample_attrition.tex | LaTeX version of attrition |
    | run_manifest.json | Stage 4 run manifest |
    Latest run: outputs/econometric/h5b_johnson_disp/2026-03-31_140249/

    NOTE: No LaTeX table file (h5b_johnson_disp_table.tex or similar) was written.
    This suite had NO generate_all_tables.py entry and was never included in the
    thesis table output. The run_manifest.json "output_files" only lists
    model_diagnostics.csv — confirming the runner did not write a .tex table.

G3. Summary Statistics:
    Variables tracked in summary_stats (from .pyc SUMMARY_STATS_VARS constant):
    JohnsonDISP2, JohnsonDISP2_lead, JohnsonDISP2_lag,
    UncAnsCEO, UncPreCEO,
    UncAnsMgr, UncPreMgr,
    lnAssets, TobinsQ, ROA, Leverage, Capex, DivDummy, sCFO
    (14 variables; extended controls not separately in summary stats)
    Metrics: N, Mean, SD, Min, P25, Median, P75, Max (standard)

**H-CHECK: Outlier/Missing Treatment (reconstructed)**

H1. Winsorization:
    JohnsonDISP2: 1%/99% POOLED (not by-year) — confirmed in johnson_disp.pyc:
    "Winsorization: 1%/99% pooled (Johnson 2004 implementation)."
    Compustat controls: winsorized at engine level (CompustatEngine by-year)
    Speech IVs: not winsorized (bounded [0,∞) by construction; typical values 0–2.5%)

H2. Missing Data Policy:
    Complete-case deletion (rows with any NaN in required columns dropped).
    Inf/-Inf replacement: standard runner pattern (confirmed from .pyc "inf" handling).

H3. Transformations:
    lnAssets: log-transformed (standard SizeBuilder formula = log(market_cap))
    JohnsonDISP2: no log or z-score. Raw value retained (this is the root cause
    of the archival — mean=0.0001, max=0.0014 — all coefficients show as 0.0000
    in .4f format tables).

**Phase 7 result: N/A — no provenance document to audit. Pipeline, outputs, and
treatment fully reconstructed from artifacts.**

---

================================================================================
PHASE 8: FACTUAL ACCURACY — SECTION I (Table Generator Entry)
================================================================================

**FINDING: H5b Johnson has NO entry in outputs/generate_all_tables.py.**

Grep result: zero matches for "h5b_johnson", "H5b_johnson", "JohnsonDISP",
"johnson_disp" in generate_all_tables.py.

The only H5-family entry is:
```python
# ── H5 (Wang 2020) ──
{
    "id": "H5",
    "dir": "h5b_wang_disp/2026-03-31_140307",
    "caption": "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",
    "label": "tab:h5",
    "cols": 12,
    "dvs": [
        ("DISP", 6),
        ("DISP\\_lead", 6),
    ],
    "tail": "one",
    "hyp_dir": ">",
}
```

This entry is for the REPLACEMENT suite (H5b-Wang, now renamed H5), not for
H5b Johnson.

The creation prompt requires Section I to either document the suite's entry or
note its absence. Since H5b Johnson was archived BEFORE a provenance doc was
written, Section I would correctly state: "This suite has no entry in
generate_all_tables.py. It was archived before publication."

**Phase 8 result: N/A — no provenance document to audit. Table generator entry:
ABSENT (confirmed by grep). This is consistent with archival status.**

---

================================================================================
PHASE 9: FACTUAL ACCURACY — SECTION K (Model-Family Addendum)
================================================================================

No Section K to audit. Model family = PanelOLS (K1).

Reconstructed K1 specifics:
- Entity effects: industry specs use other_effects (ff12_code); firm specs use
  EntityEffects (gvkey). NOT both simultaneously.
- Time effects: TimeEffects = cal_yr (cols 1-4, 7-10) or cal_yr_qtr (cols 5-6, 11-12)
- other_effects: ff12_code passed for industry specs
- drop_absorbed: standard PanelOLS default behavior
- Singleton handling: min_calls_per_firm=5 removes firms with <5 observations
  (prevents singleton entity groups)

EVIDENCE: regression_results_col1.txt: "Included effects: Time, Other Effect
(ff12_code). Model includes 1 other effect." Col2 has EntityEffects only.

**Phase 9 result: N/A — no provenance document to audit. K1 reconstructed.**

---

================================================================================
PHASE 10: QUALITY GATE CHECKLIST
================================================================================

Since the provenance document does not exist, all quality gates fail by definition.

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | FAIL | Doc does not exist |
| 2 | The model equation matches what the code actually estimates | FAIL | Doc does not exist |
| 3 | The specification register accounts for every model column | FAIL | Doc does not exist |
| 4 | The attrition cascade has row counts for each filter step | FAIL | Doc does not exist |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | FAIL | Doc does not exist; N/A for table gen (no entry exists) |
| 6 | The FE specification matches between docstring, code, and this document | FAIL | Doc does not exist |
| 7 | Every merge in the panel builder is documented with join keys and type | FAIL | Doc does not exist |
| 8 | The output file list matches what the runner actually writes | FAIL | Doc does not exist |
| 9 | The model-family addendum is filled for the correct family only | FAIL | Doc does not exist |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | FAIL | Doc does not exist |

**Phase 10 result: 0/10 quality gates met.**

---

================================================================================
PHASE 11: CROSS-REFERENCE CONSISTENCY
================================================================================

No provenance document to cross-reference. All 8 consistency checks are N/A.

However, using the forensic reconstruction as a hypothetical document, internal
consistency WOULD be:

1. DVs in B2 (JohnsonDISP2, JohnsonDISP2_lead) match spec register C: YES
2. DVs in C match generate_all_tables.py Section I: N/A (no entry in table gen)
3. Controls in B4 match variable dictionary E: YES (all 12+ controls reconstructed)
4. Column count in A (12) matches rows in C (12): YES
5. Column count in A (12) matches "cols" in I: N/A (no table gen entry)
6. Tail direction in A (one-tailed >0) matches B7 matches I: YES (A/B7); N/A (I)
7. FE in B5 matches C matches K: YES
8. Panel index in A ((gvkey, cal_yr_qtr)) matches set_index in K: YES

**Phase 11 result: N/A — no provenance document. Hypothetical cross-references
would be internally consistent based on forensic reconstruction.**

---

================================================================================
FAILURES (detailed)
================================================================================

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 1 | Section A exists | (not present) | Suite is archived; source files deleted | CRITICAL | Write provenance doc OR accept archival |
| 1 | Section B exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section C exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section D exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section E exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section F exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section G exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section H exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section I exists | (not present) | Suite is archived; no table gen entry | CRITICAL | See above |
| 1 | Section J exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section K exists | (not present) | Suite is archived | CRITICAL | See above |
| 1 | Section L exists | (not present) | Suite is archived | CRITICAL | See above |
| 2 | Runner file exists | (not checked) | run_h5b_johnson_disp.py DELETED | CRITICAL | Source file does not exist; .pyc only |
| 2 | Builder file exists | (not checked) | build_h5b_johnson_disp_panel.py DELETED | CRITICAL | Source file does not exist; .pyc only |
| 8 | Table gen entry | (not present) | No entry in generate_all_tables.py | N/A | Suite correctly excluded from tables |

---

================================================================================
CORRECTIONS REQUIRED
================================================================================

**PRIMARY CORRECTION:**

The provenance document `docs/provenance/H5b.md` does not exist and must be
created — OR — the suite's archival status must be formally documented and the
audit closed as "archived suite, no provenance doc required."

**RECOMMENDED APPROACH (given archival status):**

Since H5b Johnson is a fully archived suite (source files deleted, no table
entry, replaced by H5b-Wang which is now H5), the correct resolution is one of:

Option A — Write an archival stub at docs/provenance/H5b.md that documents:
- Suite identity and archival date
- Why it was archived (scaling issue: DV mean ~0.0001, coefficients = 0.0000)
- Link to replacement suite (H5 / H5b-Wang)
- Key forensic facts (12 specs, JohnsonDISP2 = SD/atq, Johnson 2004 JFE 74(1):3-40)
- Note that source files are deleted (no reproduction possible without .pyc)

Option B — Formally mark H5b as out of scope for provenance documentation
(archived suites do not require full provenance docs) and document this decision
in project_archived_suites.md.

**If a full provenance document is written (Option A), required content:**

Section A: Suite Identity
  - Suite ID: H5b
  - Title: H5b: Speech Uncertainty and Analyst Forecast Dispersion (Johnson 2004)
  - Hypothesis: Higher linguistic uncertainty in earnings calls leads to greater
    pre-announcement analyst forecast dispersion (Johnson 2004 DISP2)
  - Direction: One-tailed (beta > 0)
  - Model Family: PanelOLS
  - Estimator: linearmodels.panel.PanelOLS
  - Unit of Obs: Call-level
  - Panel Index: (gvkey, cal_yr_qtr)
  - Columns: 12
  - Reference: Johnson (2004, JFE 74(1): 3-40)
  - Runner: DELETED (was: src/f1d/econometric/run_h5b_johnson_disp.py)
  - Panel Builder: DELETED (was: src/f1d/variables/build_h5b_johnson_disp_panel.py)
  - Status: ARCHIVED 2026-03-31

Section D2 (Attrition Cascade — exact row counts from sample_attrition.csv):
  Full panel: 112,968 | Main sample (excl FF12=8,11): 88,205 |
  JohnsonDISP2 non-null: 49,917 | Complete case + min 5 calls/firm: 21,209

Section I: No entry in generate_all_tables.py (archived before publication).

Section L (Known Issues — this is the archival reason):
  CRITICAL: JohnsonDISP2 = SD(EPS forecasts) / atq. The DV mean is ~0.0001
  with SD=0.0002. All regression coefficients on the key IVs are in the range
  1e-7 to 1e-5, displaying as 0.0000 in standard .4f LaTeX tables. This is an
  unresolvable scaling problem inherent in the atq denominator. Suite archived
  2026-03-31. Replacement: H5 (Wang 2020) uses SD / prccq (stock price) which
  produces displayable coefficient magnitudes.

---

================================================================================
ADDITIONAL FORENSIC NOTES
================================================================================

1. **Docstring reference error in .pyc:**
   The runner docstring says: "Reference: Johnson (2020, Review of Accounting
   and Finance 19(3): 289-312)." This is WRONG — that reference is for Wang (2020),
   not Johnson. The correct reference is Johnson (2004, JFE 74(1): 3-40).
   The variable builder .pyc docstring correctly states the JFE 74(1) reference.
   This internal inconsistency in the archived runner is noted for the record.

2. **Archival timing:**
   The last regression run was 2026-03-31T14:02:53 at git commit c97e0a4. The
   suite was archived the same day (commit 70bad30, "archive H5/H5b-Johnson").
   The source files were deleted in the archival commit.

3. **DV scaling problem (confirmed by summary stats):**
   summary_stats.csv confirms: JohnsonDISP2 mean=0.0001, SD=0.0002, max=0.0014.
   This matches the archived rationale exactly. Coefficient magnitudes in
   regression_results_col1.txt range from 1.096e-06 to 3.519e-06 for key IVs —
   all would display as 0.0000 in .4f tables.

4. **Hypothesis test results (not supportive):**
   model_diagnostics.csv shows: no IV achieves p_one < 0.05 in cols 1-6.
   Cols 9 and 11 show UncPreMgr significant (p_one=0.0002,
   0.0001). However, this was moot given the display problem and archival decision.

5. **generate_all_tables.py absence confirmed:**
   Zero grep hits. The suite was run but never included in any thesis table.
   The only H5-family table is H5 (Wang 2020).

================================================================================
END OF AUDIT REPORT
================================================================================
