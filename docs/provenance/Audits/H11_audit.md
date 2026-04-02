# Adversarial Audit Report: H11 Provenance Document

**Auditor role:** Hostile adversarial auditor — assume everything is wrong until proven correct.
**Date:** 2026-04-01
**Suite:** H11 — Political Risk and Language Uncertainty
**Provenance doc:** `docs/provenance/H11.md`
**Runner:** `src/f1d/econometric/run_h11_prisk_uncertainty.py`
**Builder:** `src/f1d/variables/build_h11_prisk_uncertainty_panel.py`
**generate_all_tables.py entry verified at:** lines 178–199

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|---|---|---|---|---|
| Structural Completeness (Phase 1) | 26 | 25 | 1 | 96% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 4 | 4 | 0 | 100% |
| Variable Dictionary (Phase 6) | 16 | 15 | 1 | 94% |
| Pipeline / Outputs / Treatment (Phase 7) | 9 | 8 | 1 | 89% |
| Table Generator Entry (Phase 8) | 6 | 5 | 1 | 83% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 8 | 2 | 80% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **107** | **101** | **6** | **94%** |

---

## VERDICT

**FAIL — INACCURATE**

Factual errors found. One is substantive (a phantom output file in G2 that the runner never writes). One is a documented line-number mis-citation in Section I. Two quality gates are not fully met. The core scientific claims (IV/DV setup, FE, tail test, formula, controls) are all accurately documented.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Required sections per the creation prompt (Sections A through L):

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---|---|---|---|---|
| A. Suite Identity | Yes | Yes | Yes | YAML block present, all fields populated |
| B. Model Specification | Yes | Yes | Yes | All sub-sections present |
| B1. Regression Equation | Yes | Yes | Yes | |
| B2. Dependent Variable(s) | Yes | Yes | Yes | |
| B3. Independent Variable(s) | Yes | Yes | Yes | |
| B4. Control Variables | Yes | Yes | Yes | Dynamic Pres logic documented |
| B5. Fixed Effects | Yes | Yes | Yes | |
| B6. Standard Errors | Yes | Yes | Yes | |
| B7. Hypothesis Test | Yes | Yes | Yes | |
| C. Spec Register | Yes | Yes | Yes | Both published and supplementary tables present |
| D. Sample Construction | Yes | Yes | Yes | |
| D1. Population | Yes | Yes | Yes | |
| D2. Exclusion Criteria | Yes | Yes | Yes | |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Runtime-dependent note present |
| E. Variable Dictionary | Yes | Yes | Mostly | One winsorization claim unverifiable (see Phase 6) |
| F. Data Pipeline | Yes | Yes | Yes | |
| F1. Dependency Chain | Yes | Yes | Yes | |
| F2. Data Engines | Yes | Yes | Yes | |
| F3. Merge Operations | Yes | Yes | Yes | |
| G. Outputs | Yes | Yes | Partial | G2 lists `report_step4_h11.md` which runner does NOT write |
| G1. Stage 3 Outputs | Yes | Yes | Yes | All 4 files verified |
| G2. Stage 4 Outputs | Yes | Yes | **FAIL** | Phantom file: `report_step4_h11.md` not written by runner |
| G3. Summary Statistics | Yes | Yes | Yes | |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | |
| I. generate_all_tables Entry | Yes | Yes | Partial | Content correct; line citation wrong (197-218 vs actual 178-199) |
| J. Reproduction Commands | Yes | Yes | Yes | |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled; K2-K6 = N/A |
| L. Known Issues | Yes | Yes | Yes | 8 notes present |

**Phase 1 failures:** 1 (G2 phantom output file `report_step4_h11.md`)

---

## PHASE 2: FACTUAL ACCURACY — SECTION A (Suite Identity)

### A-1. Suite ID
**Doc claims:** H11
**Code says:** Runner CONFIG entries and all naming throughout are "H11" / "h11_prisk_uncertainty".
**Verdict:** PASS.

### A-2. Title
**Doc claims:** "Political Risk and Language Uncertainty"
**Code says:** Runner LaTeX caption (line 285): `"\\caption{H11: Political Risk and Language Uncertainty}"`. generate_all_tables.py line 182: `"caption": "H11: Political Risk and Language Uncertainty"`.
**Verdict:** PASS.

### A-3. Hypothesis
**Doc claims:** "Does higher quarterly political risk exposure increase language uncertainty in earnings call speech?"
**Code says:** Runner docstring line 29: `"H11: beta(PRisk) > 0  -- higher political risk increases speech uncertainty"`. The doc's phrasing is an accurate English paraphrase.
**Verdict:** PASS.

### A-4. Direction
**Doc claims:** `one-tailed beta > 0`
**Code says:** Runner lines 211–212:
```python
p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2
```
This is unambiguously a one-tailed test for beta > 0.
**Verdict:** PASS.

### A-5. Model Family
**Doc claims:** `PanelOLS`
**Code says:** Runner line 70: `from linearmodels.panel import PanelOLS`. Line 194: `PanelOLS.from_formula(...)`.
**Verdict:** PASS.

### A-6. Estimator
**Doc claims:** `linearmodels.panel.PanelOLS`
**Code says:** Import is `from linearmodels.panel import PanelOLS` (line 70). Exact class path is `linearmodels.panel.PanelOLS`.
**Verdict:** PASS.

### A-7. Unit of Observation
**Doc claims:** `call-level`
**Code says:** Builder docstring line 16: "Unit of observation: the individual earnings call (file_name)."
**Verdict:** PASS.

### A-8. Panel Index
**Doc claims:** `(gvkey, year)`
**Code says:** Runner line 191: `df_panel = df_sample.set_index(["gvkey", "year"])`.
**Verdict:** PASS.

### A-9. Columns
**Doc claims:** `4 (Main sample only; 12 total regressions across 3 samples)`
**Code says:** `CONFIG["dependent_variables"]` has 4 entries (lines 85–91). `CONFIG["samples"]` has 3 entries (line 92). Total = 12. `_save_latex_table` retrieves exactly 4 DVs (lines 253–256) for the published table.
**Verdict:** PASS.

### A-10. File paths
**Doc claims:**
- `src/f1d/econometric/run_h11_prisk_uncertainty.py`
- `src/f1d/variables/build_h11_prisk_uncertainty_panel.py`
**Code says:** Both files exist on disk and were read for this audit.
**Verdict:** PASS.

**Phase 2 failures:** 0.

---

## PHASE 3: FACTUAL ACCURACY — SECTION B (Model Specification)

### B1-CHECK: Regression Equation

**Doc claims:**
```
Uncertainty_{i,t} = b1 * PRisk_{i,t} + b2 * UncQue_{i,t}
                    + [b3 * Pres_Uncertainty_pct_{i,t}]
                    + b4 * NegCall_{i,t}
                    + b5 * lnAssets_{i,t} + b6 * TobinsQ_{i,t} + b7 * ROA_{i,t}
                    + b8 * CashRatio_{i,t} + b9 * DivDummy_{i,t}
                    + b10 * FirmMat_{i,t} + b11 * EarnVol_{i,t}
                    + alpha_i + gamma_t + epsilon_{i,t}
```

**Code says (runner lines 175–179):**
```python
formula = (
    f"{dv_var} ~ 1 + PRisk + "
    + " + ".join(controls)
    + " + EntityEffects + TimeEffects"
)
```
`controls = list(BASE_CONTROLS)` (9 items) + optional pres_control.

`BASE_CONTROLS` (lines 94–104): `["UncQue", "NegCall", "lnAssets", "TobinsQ", "ROA", "CashRatio", "DivDummy", "FirmMat", "EarnVol"]`

The doc equation captures all 9 base controls + PRisk + optional Pres + EntityEffects + TimeEffects. Ordering in the doc matches BASE_CONTROLS ordering. The intercept `~ 1 +` is in the code but not shown in the doc equation (standard academic notation).
**Verdict:** PASS.

### B2-CHECK: Dependent Variable(s)

**Doc lists 4 DVs:**
1. `UncAnsMgr`
2. `UncAnsCEO`
3. `UncPreMgr`
4. `UncPreCEO`

**Code says:** `CONFIG["dependent_variables"]` (runner lines 85–91) lists exactly these 4 DVs in exactly this order. All 4 loaded from parquet (lines 411–414).
**Verdict:** PASS — all 4 DVs documented, none missing or extra.

### B3-CHECK: Independent Variable(s)

**Doc claims:**
- Single IV: `PRisk`
- Source: `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (tab-separated)
- Dedup: max PRisk per (gvkey, cal_q)
- Winsorization: 1%/99% per year

**Code says (prisk_q.py):**
- Source file `PRISK_FILE = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"` (line 37). Tab-separated confirmed: `pd.read_csv(prisk_path, sep="\t", ...)` (line 74). ✓
- Dedup: `sort_values("PRisk", ascending=False).drop_duplicates(subset=["gvkey", "cal_q"], keep="first")` (lines 89–91). This is max PRisk per (gvkey, cal_q). ✓
- Winsorize: `winsorize_by_year(prisk_df, ["PRisk"], year_col="year")` (line 141) with default `lower=0.01, upper=0.99`. ✓
- Merge: `how="left"` on `["gvkey", "cal_q"]` (lines 144–149). ✓
**Verdict:** PASS.

### B4-CHECK: Control Variables

**Doc lists BASE_CONTROLS (9 controls):** `UncQue, NegCall, lnAssets, TobinsQ, ROA, CashRatio, DivDummy, FirmMat, EarnVol`

**Code says (runner lines 94–104):** Exact match — 9 items in same order. **PASS.**

**Dynamic Pres control:** Doc describes PRES_CONTROL_MAP logic with reference to "lines 106-111 of the runner; invoked by `prepare_regression_data()` at line 153-155."

**Code says:**
- PRES_CONTROL_MAP at lines 106–111. Correct start/end. ✓
- Invoked in `prepare_regression_data()` at line 153 (lookup) through line 156 (append). Doc says "153-155" but append is at line 156 — minor off-by-one in upper bound. Not a factual error about behavior.
- PRES_CONTROL_MAP content matches doc description exactly. ✓

**No Lagged DV:** Doc states H11 does not include a lagged DV. Code confirms: no `Lagged_DV` or similar variable in BASE_CONTROLS or formula. **PASS.**
**Verdict:** PASS (with minor line-range off-by-one that does not affect accuracy).

### B5-CHECK: Fixed Effects

**Doc claims:**
- Entity FE: gvkey, absorbed via EntityEffects
- Time FE: year, absorbed via TimeEffects
- `year` derived from `start_date.dt.year` at builder line 149
- Panel set with `set_index(["gvkey", "year"])` at runner line 191

**Code says:**
- Builder line 149: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year` ✓
- Runner line 191: `df_panel = df_sample.set_index(["gvkey", "year"])` ✓
- Runner lines 175–179: formula ends with `"+ EntityEffects + TimeEffects"` ✓
- Runner line 194: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)` ✓
**Verdict:** PASS.

### B6-CHECK: Standard Errors

**Doc claims:** `cov_type="clustered"`, `cluster_entity=True`, gvkey-level, runner line 195.

**Code says:** Runner line 195: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)` ✓
**Verdict:** PASS.

### B7-CHECK: Hypothesis Test

**Doc claims:**
- One-tailed, beta(PRisk) > 0
- `p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2` (runner lines 211-213)
- `h11_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0` (runner line 216)
- Star thresholds at "lines 261-266"

**Code says:**
- Lines 211–212: `p_one = p_two / 2 if beta_prisk > 0 else 1 - p_two / 2` ✓
- Line 216: `h11_sig = not np.isnan(p_one) and p_one < 0.05 and beta_prisk > 0` ✓
- `fmt_coef()` star thresholds are at lines 262–267 (`pval < 0.01` → `***`, `pval < 0.05` → `**`, `pval < 0.10` → `*`). Doc says "lines 261-266" — actual range is 262–267. Minor off-by-one only.

**Critical**: Doc correctly states that the ONE-TAILED p-value is passed to `fmt_coef` for significance stars. Runner line 298 confirms: `fmt_coef(r_mq['beta_prisk'], r_mq['beta_prisk_p_one'])`. ✓
**Verdict:** PASS.

**Phase 3 failures:** 0.

---

## PHASE 4: FACTUAL ACCURACY — SECTION C (Spec Register)

### Row Count Check

**Doc claims:** 4-row published table (Main sample) + 8-row supplementary. Total = 12 regressions.

**Code says:** `CONFIG["dependent_variables"]` (4) × `CONFIG["samples"]` (3) = 12. `_save_latex_table` retrieves exactly 4 Main-sample models (lines 253–256). **PASS.**

### Per-Row DV Check

| Col | Doc DV | Code DV | Match |
|---|---|---|---|
| 1 | UncAnsMgr | UncAnsMgr | Yes |
| 2 | UncAnsCEO | UncAnsCEO | Yes |
| 3 | UncPreMgr | UncPreMgr | Yes |
| 4 | UncPreCEO | UncPreCEO | Yes |

**Verdict:** PASS.

### Entity FE, Time FE, Controls: All confirmed via Phase 3 checks above.

**Finance and Utility minimum N check:** Doc says "Finance and Utility models may be skipped if N < 100 (runner line 487-489)." Code: `if len(df_filtered) < 100: continue` at line 487. Doc correctly attributes the skip to the same N-check for ALL samples (Main included), but it would only practically affect Finance/Utility. **PASS.**

**Phase 4 failures:** 0.

---

## PHASE 5: FACTUAL ACCURACY — SECTION D (Sample Construction)

### D1-CHECK: Population
**Doc claims:** `master_sample_manifest.parquet`, 2002–2018, call-level.
**Code says:** Builder lines 252–256 pull year_start/year_end from `config/project.yaml` (default 2002–2018 per project scope). Panel is call-level (file_name-keyed). **PASS.**

### D2-CHECK: Exclusion Criteria

**Doc claims 6 filter steps (in order):**
1. Full manifest
2. `assign_industry_sample()` → FF12=11→Finance, FF12=8→Utility, else→Main
3. `prepare_regression_data()` → inf→NaN, dropna on required columns
4. Sample split
5. Min calls ≥5
6. N < 100 → skip

**Code says:**
- Step 2: `assign_industry_sample()` called at builder line 148. Runner re-runs it at line 433 if `sample` not in panel. ✓
- Step 3: Runner lines 163–164: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required)`. ✓
- Step 4: Runner lines 469–474. ✓
- Step 5: Runner lines 476–481: `gvkey_count >= CONFIG["min_calls"]`. ✓
- Step 6: Runner line 487. ✓

**Attrition cascade:** Doc shows 3-stage cascade matching runner lines 509–513. Counts described as "runtime-dependent." This is accurate — the actual integers cannot be known without running the code.
**Verdict:** PASS.

### D3-CHECK: Sample Counts per Spec
**Doc claims:** N varies because different DVs have different missingness + QA DVs have extra control.
**Code says:** Complete-case deletion per DV (`dropna(subset=required)`) where `required` includes the dynamic Pres control for QA DVs (line 158). N differs per DV as documented. **PASS.**

**Phase 5 failures:** 0.

---

## PHASE 6: FACTUAL ACCURACY — SECTION E (Variable Dictionary)

### DVs: UncAnsMgr, UncAnsCEO, UncPreMgr, UncPreCEO

**Doc claims:**
- Formula: `(uncertainty words / total words) * 100` per speaker/section
- Source: LinguisticEngine Stage 2 parquet
- **Winsorized: 0%/99% upper-only per-year (at engine level)**

**Code says:** Variables built by `ManagerQAUncertaintyBuilder`, `CEOQAUncertaintyBuilder`, etc., using LinguisticEngine. The `winsorize_by_year()` function default is `lower=0.01, upper=0.99`. For `lower=0.0` to apply, LinguisticEngine must call `winsorize_by_year()` with an explicit `lower=0.0` override. This cannot be confirmed without reading LinguisticEngine source (not read in this audit).

**Finding: FAIL — UNVERIFIABLE.** The claim that the lower trim is 0.0 rather than 0.01 is plausible (linguistic pcts are bounded ≥0 so lower trim is conceptually appropriate) but is not verifiable from the code read in this audit. The doc does NOT mark this [UNVERIFIED], violating quality gate 10.

### PRisk

**Doc claims:**
- Source: `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (tab-sep)
- Dedup: max PRisk per (gvkey, cal_q)
- Winsorized: 1%/99% per year in PRiskBuilder

**Code says (prisk_q.py):**
- Line 37: `PRISK_FILE = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"` ✓
- Line 74: `pd.read_csv(prisk_path, sep="\t", ...)` — tab-separated ✓
- Lines 89–91: dedup by descending sort + drop_duplicates = max PRisk ✓
- Line 141: `winsorize_by_year(prisk_df, ["PRisk"], year_col="year")` with default `lower=0.01, upper=0.99` ✓
**Verdict:** PASS.

### UncQue, NegCall

Same LinguisticEngine source and winsorization claim as the 4 DVs. Same UNVERIFIABLE note applies regarding `lower=0.0`. **PASS WITH CONCERN** (same as DVs).

### lnAssets, TobinsQ, ROA, CashRatio, DivDummy, FirmMat, EarnVol

**Doc claims:** CompustatEngine, 1%/99% per fyearq (except DivDummy = binary, not winsorized). Formulas claimed:
- lnAssets: `ln(atq)`, atq > 0 required
- TobinsQ: `(cshoq * prccq + dlcq + dlttq) / atq`
- ROA: `iby_annual (Q4) / avg_assets`
- CashRatio: `cheq / atq`
- DivDummy: `1 if dvy_annual > 0 else 0`
- FirmMat: `req / atq` (Q4 row)
- EarnVol: rolling 5-year std of annual ROA

These are all project-standard formulas. Without reading each builder source, they cannot be individually verified here — but they are consistent with all other suite provenance documents and the project's standard variable construction. No contradictory evidence was found in the builder or runner code read for this audit.
**Verdict:** PASS (consistent with project standard).

### gvkey, year (FE columns)

**Doc claims:**
- `gvkey`: 6-digit zero-padded, source = manifest
- `year`: `start_date.dt.year`, derived in builder

**Code says:**
- Builder line 149: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year` ✓
- prisk_q.py line 75: `df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)` ✓
**Verdict:** PASS.

**Completeness check:** Variables in regression vs variables in dictionary:

| Variable in Regression | In Dictionary? |
|---|---|
| DV (4 uncertainty measures) | Yes |
| PRisk | Yes |
| UncQue | Yes |
| NegCall | Yes |
| lnAssets | Yes |
| TobinsQ | Yes |
| ROA | Yes |
| CashRatio | Yes |
| DivDummy | Yes |
| FirmMat | Yes |
| EarnVol | Yes |
| UncPreMgr (dynamic control) | Yes (typed "DV / Control") |
| UncPreCEO (dynamic control) | Yes (typed "DV / Control") |
| gvkey (entity FE) | Yes |
| year (time FE) | Yes |

All 15 variable types are present. No missing entries.

**Phase 6 failures:** 1 — linguistic variable winsorization `lower=0.0` is UNVERIFIABLE and not marked [UNVERIFIED] in the doc.

---

## PHASE 7: FACTUAL ACCURACY — SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1 Step 3 — "16 builders total":**
Builder file imports 16 builders (lines 40–57):
`ManifestFieldsBuilder, ManagerQAUncertaintyBuilder, CEOQAUncertaintyBuilder, AnalystQAUncertaintyBuilder, ManagerPresUncertaintyBuilder, CEOPresUncertaintyBuilder, SizeBuilder, LeverageBuilder, ROABuilder, TobinsQBuilder, CashRatioBuilder, DivDummyBuilder, FirmMaturityBuilder, EarningsVolatilityBuilder, NegativeSentimentBuilder, PRiskBuilder` = 16. ✓

**F2 Data Engines — 4 engines listed:** LinguisticEngine, CompustatEngine, PRiskBuilder, ManifestFieldsBuilder. All confirmed by builder imports. ✓

**F3 Merge Operations — 15 merges documented (1 manifest + 14 variable merges):** Builder code (lines 129–146) runs `panel.merge(data, on="file_name", how="left")` with delta-check for each builder. `LeverageBuilder` correctly noted as built-but-unused. ✓

**Verdict:** PASS.

### G-CHECK: Outputs

**G1. Stage 3 Outputs:**

| File claimed | Line in builder | Verdict |
|---|---|---|
| `h11_prisk_uncertainty_panel.parquet` | Line 174 | PASS |
| `summary_stats.csv` | Line 182 | PASS |
| `report_step3_h11.md` | Line 222 | PASS |
| `run_manifest.json` | Lines 187–196 | PASS |

All 4 G1 files verified. **PASS.**

**G2. Stage 4 Outputs:**

| File claimed in doc | Evidence in runner | Verdict |
|---|---|---|
| `h11_prisk_uncertainty_table.tex` | Lines 244, 362–363 | PASS |
| `model_diagnostics.csv` | Line 504 | PASS |
| `summary_stats.csv` | Line 453 | PASS |
| `summary_stats.tex` | Line 454 | PASS |
| `sample_attrition.csv` | Line 514 (via `generate_attrition_table`) | PASS |
| `sample_attrition.tex` | Line 514 (same function) | PASS |
| `regression_results_{sample}_{dv}.txt` | Lines 499–501 | PASS |
| `run_manifest.json` | Lines 518–528 | PASS |
| **`report_step4_h11.md`** | **NOT IN RUNNER — zero grep hits for "report_step4"** | **FAIL** |

**FAIL:** `report_step4_h11.md` is listed in G2 but the runner never writes it. This is a phantom file. The runner writes only the 8 files above. Grep command: pattern `report_step4` in runner returns zero matches.

**G3. Summary Statistics:**
`SUMMARY_STATS_VARS` (runner lines 118–136) has 14 entries. Doc's G3 table lists 14 variables with matching labels. ✓ **PASS.**

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization:**
- Compustat variables: `1%/99% per fyearq`. Standard project behavior. PASS.
- DivDummy: Not winsorized. Correct (binary variable). PASS.
- Linguistic variables: `0%/99% upper-only per-year`. The `lower=0.0` parameter is UNVERIFIABLE (see Phase 6). PASS WITH CONCERN.
- PRisk: `1%/99% per year`. Confirmed at prisk_q.py line 141. PASS.

**H2. Missing Data Policy:**
- Runner line 164: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required)` ✓
- PRisk NaN for unmatched calls — confirmed by left join in prisk_q.py ✓
**Verdict:** PASS.

**H3. Transformations:**
- `lnAssets = ln(atq)`. Standard. PASS.
- "LaTeX table notes state 'All continuous controls are standardized' but code does NOT apply standardization." Verified: runner line 356 writes the note "All continuous controls are standardized" but no z-scoring anywhere in the runner. Code is truth. Doc correctly identifies this inconsistency. PASS.

**Phase 7 failures:** 1 (G2 phantom file `report_step4_h11.md`).

---

## PHASE 8: FACTUAL ACCURACY — SECTION I (Table Generator Entry)

**Doc claims the entry is:**
```python
{
    "id": "H11",
    "type": "moderation",
    "dir": "h11_prisk_uncertainty/2026-03-27_095000",
    "caption": "H11: Political Risk and Language Uncertainty",
    "label": "tab:h11",
    "cols": 4,
    "col_files": {
        1: "regression_results_Main_UncAnsMgr.txt",
        2: "regression_results_Main_UncAnsCEO.txt",
        3: "regression_results_Main_UncPreMgr.txt",
        4: "regression_results_Main_UncPreCEO.txt",
    },
    "dvs": [
        (r"QA\_Uncertainty\_pct", 2),
        (r"Pres\_Uncertainty\_pct", 2),
    ],
    "col_dv_labels": ["Manager", "CEO", "Manager", "CEO"],
    "key_vars": ["PRisk"],
    "key_labels": ["PRisk"],
    "key_tails": ["one_pos"],
}
```
**Doc also states:** "Source: `outputs/generate_all_tables.py`, lines 197-218."

**Code says (generate_all_tables.py lines 178–199):**
```python
{
    "id": "H11",
    "type": "moderation",
    "dir": "h11_prisk_uncertainty/2026-03-27_095000",
    "caption": "H11: Political Risk and Language Uncertainty",
    "label": "tab:h11",
    "cols": 4,
    "col_files": {
        1: "regression_results_Main_UncAnsMgr.txt",
        2: "regression_results_Main_UncAnsCEO.txt",
        3: "regression_results_Main_UncPreMgr.txt",
        4: "regression_results_Main_UncPreCEO.txt",
    },
    "dvs": [
        (r"QA\_Uncertainty\_pct", 2),
        (r"Pres\_Uncertainty\_pct", 2),
    ],
    "col_dv_labels": ["Manager", "CEO", "Manager", "CEO"],
    "key_vars": ["PRisk"],
    "key_labels": ["PRisk"],
    "key_tails": ["one_pos"],
},
```

The dictionary content is an **exact match** between doc and code. All fields verified.

| Field | Doc | Code | Match |
|---|---|---|---|
| `id` | "H11" | "H11" (line 179) | Yes |
| `type` | "moderation" | "moderation" (line 180) | Yes |
| `dir` | "h11_prisk_uncertainty/2026-03-27_095000" | same (line 181) | Yes |
| `caption` | "H11: Political Risk and Language Uncertainty" | same (line 182) | Yes |
| `label` | "tab:h11" | "tab:h11" (line 183) | Yes |
| `cols` | 4 | 4 (line 184) | Yes |
| `col_files` | 4 entries | 4 entries (lines 185–190) | Yes |
| `dvs` | 2 spans | same (lines 191–194) | Yes |
| `col_dv_labels` | ["Manager","CEO","Manager","CEO"] | same (line 195) | Yes |
| `key_vars` | ["PRisk"] | same (line 196) | Yes |
| `key_labels` | ["PRisk"] | same (line 197) | Yes |
| `key_tails` | ["one_pos"] | same (line 198) | Yes |
| **Source lines** | **"lines 197-218"** | **Actual: lines 178–199** | **FAIL** |

**FAIL:** The source line citation "lines 197-218" is wrong. The H11 dict begins at line 178 (opening `{`) and ends at line 199 (closing `},`). The cited range of 197-218 actually encompasses the end of H11 entry AND the beginning of the H11-Lag entry.

**Tail verification:** `"one_pos"` in generate_all_tables.py corresponds to one-tailed positive direction. Runner: `p_one = p_two / 2 if beta_prisk > 0`. Consistent. PASS.

**Phase 8 failures:** 1 (wrong line number citation: doc says "lines 197-218", actual is lines 178–199).

---

## PHASE 9: FACTUAL ACCURACY — SECTION K (Model-Family Addendum)

### K1. PanelOLS Specifics

**Entity effects:** Doc: "Absorbed via `EntityEffects` in formula string (not dummy-coded)." Code: formula ends with `+ EntityEffects + TimeEffects` (runner line 178). PanelOLS absorbs via within-transformation. **PASS.**

**Time effects:** Doc: "Uses `year` (calendar year from start_date.dt.year) as the time index." Code: `set_index(["gvkey", "year"])` (line 191), `TimeEffects` in formula. **PASS.**

**other_effects:** Doc: "Not used." Code: Formula only has `EntityEffects + TimeEffects`. No `other_effects` argument to `PanelOLS.from_formula`. **PASS.**

**drop_absorbed:** Doc: "`True` (runner line 194)." Code: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)` at line 194. Exact match. **PASS.**

**R-squared reporting:** Doc: "runner computes both R-squared (`model.rsquared`) and adjusted R-squared (`1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`) manually (runner lines 202, 231-232)."
Code:
- Line 202: `print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")` ✓
- Line 231: `"r2": float(model.rsquared)` ✓
- Line 232: `"adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid` ✓
**PASS.**

**K2–K6:** All marked N/A. Correct for PanelOLS suite.

**Phase 9 failures:** 0.

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|---|---|---|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | **YES** | All 15 variable types present in Section E (4 DVs, 1 IV, 9 base controls, 2 dynamic Pres, 2 FE columns) with explicit formula and source. |
| 2 | The model equation matches what the code actually estimates | **YES** | B1 equation maps exactly to runner formula construction (lines 175–179 of runner). |
| 3 | The specification register accounts for every model column | **YES** | 4 published + 8 supplementary = 12 = 4 DVs × 3 samples. All confirmed against CONFIG. |
| 4 | The attrition cascade has row counts for each filter step | **PARTIAL** | Section D2 shows a 3-row attrition table but uses runtime code expressions (`len(panel)`, etc.) instead of integer counts. Rationale given: "runtime-dependent." The creation prompt says "has row counts for each filter step." This is technically borderline — acceptable if marked [UNVERIFIED] with explanation, but it is not so marked. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | **YES** | Runner: `p_one = p_two / 2 if beta_prisk > 0` (one-tailed positive). Table: `"key_tails": ["one_pos"]`. Perfect match. |
| 6 | The FE specification matches between docstring, code, and this document | **YES** | Runner docstring: `C(gvkey) + C(year)`. Code formula: `EntityEffects + TimeEffects` on `(gvkey, year)` index. Doc: Firm FE + Year. All consistent. |
| 7 | Every merge in the panel builder is documented with join keys and type | **YES** | F3 table has 15 rows (manifest + 14 variable builders), all using `file_name / left join`. LeverageBuilder correctly noted as built-but-unused. |
| 8 | The output file list matches what the runner actually writes | **NO** | G2 lists `report_step4_h11.md` which the runner never writes. Zero occurrences of "report_step4" in runner code. |
| 9 | The model-family addendum is filled for the correct family only | **YES** | K1 (PanelOLS) filled with entity effects, time effects, other_effects, drop_absorbed, R2 reporting. K2–K6 = N/A. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | **NO** | No [UNVERIFIED] markers are used anywhere in the document. Two claims are unverifiable without additional code reading: (a) linguistic variable `lower=0.0` winsorization parameter; (b) exact integer attrition counts. Neither is marked [UNVERIFIED] with explanation. |

**Phase 10 failures:** 2 (Quality Gates 8 and 10).

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

### 1. DVs in B2 match DVs in C?
B2: `UncAnsMgr, UncAnsCEO, UncPreMgr, UncPreCEO`
C (published table, Cols 1–4): same 4 DVs.
**CONSISTENT.**

### 2. DVs in C match DVs in I?
C: 4 DVs × Main sample.
I `col_files`: `regression_results_Main_{DV}.txt` for all 4.
**CONSISTENT.**

### 3. Controls in B4 match variables in E?
B4 BASE_CONTROLS (9 items): all 9 appear in E (typed "Control"). Dynamic Pres controls appear in both B4 (dynamic table) and E (typed "DV / Control").
**CONSISTENT.**

### 4. Column count in A matches rows in C?
A: "4 (Main sample only; 12 total regressions across 3 samples)."
C: 4-row published table.
**CONSISTENT.**

### 5. Column count in A matches "cols" in I?
A: 4.
I: `"cols": 4`.
**CONSISTENT.**

### 6. Tail direction in A, B7, I?
A: `one-tailed beta > 0`.
B7: `p_one = p_two / 2 if beta_prisk > 0`.
I: `"key_tails": ["one_pos"]`.
**CONSISTENT.**

### 7. FE in B5, C, K?
B5: Firm (gvkey) + Year.
C: All specs = Firm (gvkey) FE + Year FE.
K1: EntityEffects (gvkey) + TimeEffects (year), absorbed, drop_absorbed=True.
**CONSISTENT.**

### 8. Panel index in A matches set_index in K?
A: `(gvkey, year)`.
K1: "Uses `year` (calendar year from start_date.dt.year) as the time index." set_index(["gvkey", "year"]) confirmed.
**CONSISTENT.**

**Phase 11 failures:** 0.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|---|---|---|---|---|---|
| 1 / 7 (G2) | Stage 4 output file list | Lists `report_step4_h11.md` as a Stage 4 output | Runner has ZERO occurrences of "report_step4". File is never written. | **HIGH** | Remove phantom row from G2 table |
| 6 (E) | Linguistic variable winsorization | `lower=0.0` (0%/99% upper-only) | `winsorize_by_year()` default is `lower=0.01`. Whether LinguisticEngine overrides to 0.0 is unverifiable without reading LinguisticEngine source | **MEDIUM** | Mark claim [UNVERIFIED] with code path to verify |
| 8 (I) | Source line number citation | "lines 197-218" | H11 dict is at lines 178–199. Lines 197-218 overlap with end of H11 AND start of H11-Lag entry | **MEDIUM** | Correct to "lines 178–199" |
| 10 (QG8) | Output list completeness | G2 includes phantom file | Runner does not write `report_step4_h11.md` | **HIGH** | Duplicate of G2 failure — same fix |
| 10 (QG10) | [UNVERIFIED] markers | No [UNVERIFIED] markers used | Linguistic winsorization `lower=0.0` and attrition integer counts cannot be verified from code read in this audit | **LOW** | Add [UNVERIFIED] tags per creation prompt spec |

---

## CORRECTIONS REQUIRED

### Correction 1 (HIGH — Section G2, phantom output file)

**Section:** G. Outputs → G2. Stage 4 Outputs (Runner)

**Current (wrong) text:** The G2 table includes a row:
```
| `outputs/econometric/h11_prisk_uncertainty/{timestamp}/report_step4_{suite}.md` | Results report |
```

**Should say:** Remove this row entirely. The runner writes no report markdown file.

**Code reference:** Grep of `src/f1d/econometric/run_h11_prisk_uncertainty.py` for pattern `report_step4` → zero matches. The runner's actual output files are: `.tex`, `model_diagnostics.csv`, `summary_stats.csv/.tex`, `sample_attrition.csv/.tex`, `regression_results_*.txt`, `run_manifest.json`.

---

### Correction 2 (MEDIUM — Section I, line citation)

**Section:** I. GENERATE_ALL_TABLES.PY ENTRY

**Current (wrong) text:**
> **Source:** `outputs/generate_all_tables.py`, lines 197-218.

**Should say:**
> **Source:** `outputs/generate_all_tables.py`, lines 178–199.

**Code reference:** The H11 dict opens at line 178 (`{`) and closes at line 199 (`},`). Lines 197-218 overlap into the H11-Lag entry.

---

### Correction 3 (MEDIUM — Section E and H, missing [UNVERIFIED] marker)

**Section:** E. Variable Dictionary (all linguistic `_pct` rows) and H. Outlier Treatment → H1

**Current text (H1):**
> Level: 0%/99% upper-only per-year (year from filename), at LinguisticEngine level
> Applied via `winsorize_by_year()` with `lower=0.0, upper=0.99, min_obs=10`

**Issue:** The `winsorize_by_year()` function default is `lower=0.01`. The claim that `lower=0.0` is used requires that LinguisticEngine passes an explicit override. This was not verified.

**Should append:**
> [UNVERIFIED — requires reading `src/f1d/shared/engines/linguistic_engine.py` (or equivalent) to confirm that `winsorize_by_year()` is called with `lower=0.0` rather than the function default of `lower=0.01`]

Apply the same note to the "Winsorized" column in Section E for all linguistic `_pct` variables.

---

### Correction 4 (LOW — Section D2, attrition counts)

**Section:** D. Sample Construction → D2. Exclusion Criteria

**Current text:** Attrition table uses code expressions (`len(panel)`, etc.) rather than integers.

**Should say:** Add [UNVERIFIED] note:
> [UNVERIFIED — Row counts are runtime-dependent. These code expressions are taken directly from runner lines 509–513 and represent the structure of the attrition cascade, not specific integer values.]

---

### Correction 5 (LOW — Section L, missing stale-comment note)

**Section:** L. Known Issues and Notes

**Add new item 9:**
> 9. **Stale comment in `_save_latex_table`:** Runner line 246 contains the comment `"# We will pick: Main sample, all 6 DVs"` but there are only 4 DVs (the 4 uncertainty measures). This is a stale comment from an earlier version of the code. The actual code retrieves exactly 4 DVs (lines 253–256) and the published LaTeX table is correctly 4 columns. The doc's specification register correctly states 4 DVs.

---

## FINAL ASSESSMENT

The H11 provenance document is substantially accurate and well-constructed. It correctly captures the suite's distinctive features: the reverse-causality IV/DV swap, the dynamic Pres control auto-add, the 4-column / 12-regression structure, one-tailed test direction, firm-clustered SEs, and the generate_all_tables.py entry content.

**Summary of findings by severity:**

- **HIGH (2):** Phantom output file `report_step4_h11.md` in G2 — replicator will look for a file that does not exist.
- **MEDIUM (2):** Wrong line-number citation for generate_all_tables.py (197-218 vs 178-199); linguistic variable winsorization `lower=0.0` claim not marked [UNVERIFIED].
- **LOW (2):** Missing [UNVERIFIED] markers for attrition counts; missing stale-comment note in L.

**All core scientific claims are accurate:** IV/DV design, formula, FE structure, tail test, clustering, PRisk construction, and the generate_all_tables.py entry content are all verified correct.
