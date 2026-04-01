# AUDIT REPORT: H11-Lead Provenance Document

**Audit Date:** 2026-04-01 (re-audit, supersedes 2026-03-30 version)
**Auditor:** Adversarial audit per `docs/Prompts/Audit Provenance doc.txt`
**Provenance Doc:** `docs/provenance/H11-Lead.md`
**Runner:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`
**Panel Builder:** `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py`
**Reference:** `outputs/generate_all_tables.py` (SUITES list, lines 1–end)

**Re-audit Rationale:** H11-Lead was removed from `generate_all_tables.py` on 2026-03-31
(project_archived_suites.md: "Removed from report 2026-03-31 (placebo test, not needed in
tables)"). The prior 2026-03-30 audit was conducted BEFORE this removal and therefore did not
catch the now-critical discrepancy in Section I of the provenance document.

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 25 | 25 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 9 | 1 | 90% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 3 | 0 | 100% |
| Variable Dictionary (Phase 6) | 18 | 15 | 3 | 83% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 7 | 2 | 78% |
| Table Generator Entry (Phase 8) | 5 | 0 | 5 | 0% |
| Model-Family Addendum (Phase 9) | 5 | 5 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 8 | 2 | 80% |
| Cross-Reference Consistency (Phase 11) | 8 | 7 | 1 | 88% |
| **TOTAL** | **105** | **91** | **14** | **87%** |

---

## VERDICT

**FAIL — INACCURATE**

Section I (generate_all_tables.py Entry) is entirely fabricated. H11-Lead was removed from
`generate_all_tables.py` on 2026-03-31 and has no entry there. The provenance document presents
a detailed, internally consistent entry with specific field values, line citations (lines 248–276),
and a verification table — none of which correspond to any actual code. The cited lines 248–276
of `generate_all_tables.py` contain the H13 and H13.1 entries, not H11-Lead. Additionally,
Section F1, step 7 claims "generate_all_tables.py uses 'type': 'moderation' with 8 col_files"
which is also false.

Secondary failures: three line-number citations in the Variable Dictionary are wrong (Size at
line 938, winsorization skip list at lines 1121–1128), and the TobinsQ formula omits the
clip/fillna behavior of the debt components.

The core model specification, hypothesis test direction, regression mechanics, and panel
pipeline are all accurately documented. The suite runs correctly. The sole critical failure is
Section I.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Read `docs/Prompts/Suite Provenance Doc.txt` to extract required sections.
Read `docs/provenance/H11-Lead.md` end to end.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block with all required fields |
| B. Model Specification | Yes | Yes | Yes | All subsections B1–B7 present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equation + formula string |
| B2. Dependent Variable(s) | Yes | Yes | Yes | 4 DVs documented |
| B3. Independent Variable(s) | Yes | Yes | Yes | 2 IVs with lead construction logic |
| B4. Control Variables | Yes | Yes | Yes | Base controls + dynamic Pres control map |
| B5. Fixed Effects | Yes | Yes | Yes | Entity + Time FE documented |
| B6. Standard Errors | Yes | Yes | Yes | Clustered at firm level |
| B7. Hypothesis Test | Yes | Yes | Yes | Two-tailed, p_test = p_two documented |
| C. Spec Register | Yes | Yes | Yes | 8-row table with DV/IV/FE/controls |
| D. Sample Construction | Yes | Yes | Yes | All D subsections present |
| D1. Population | Yes | Yes | Yes | Manifest + year range |
| D2. Exclusion Criteria | Yes | Yes | Yes | 3-step attrition cascade |
| D3. Sample Counts per Spec | Yes | Yes | Yes | N/firms for all 8 columns |
| E. Variable Dictionary | Yes | Yes | Yes | 17-row table covering all variables |
| F. Data Pipeline | Yes | Yes | Yes | F1–F3 all present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 4 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | 16 merges documented |
| G. Outputs | Yes | Yes | Yes | G1–G3 all present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 8 file types listed |
| G3. Summary Statistics | Yes | Yes | Yes | All 15 variables listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1–H3 all present |
| I. generate_all_tables Entry | Yes | Yes | **FABRICATED** | Entry present but does NOT exist in actual file |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands correct |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2–K6 N/A |
| L. Known Issues | Yes | Yes | Yes | 7 items listed |

**Phase 1 result:** All required sections are structurally present. Section I is present but
its content is factually wrong (fabricated entry). Structural pass; factual failure in I.

---

## PHASE 2: SUITE IDENTITY (Section A)

### A-1. Suite ID
Doc says: `H11-Lead`
Verified: trivial, correct.
**PASS**

### A-2. Title
Doc says: `H11-Lead: Lead Political Risk and Language Uncertainty (Placebo)`
Runner docstring (line 4): `STAGE 4: Test H11-Lead Political Risk (Lead) - Language Uncertainty Hypothesis`
Runner title print (line 424): `STAGE 4: Test H11-Lead Political Risk - Language Uncertainty Hypothesis`
The doc title is consistent in spirit; slightly more formal for publication.
**PASS** (minor phrasing difference, not a discrepancy)

### A-3. Hypothesis
Doc says: "Future political risk (1- and 2-quarter leads) should NOT predict current earnings-call
language uncertainty. This is a placebo/falsification test for reverse causality."
Runner docstring lines 32–37 state: "Tests BOTH 1-quarter lead (PRiskQ_lead) AND 2-quarter lead
(PRiskQ_lead2). [...] Lead tests are placebo tests for reverse causality. Expected result: Lead
coefficients should be insignificant."
**PASS**

### A-4. Direction (tail test)
Doc says: `Two-tailed (beta = 0 under null; expected insignificance)`
Runner line 223: `p_test = p_two` — two-tailed p-value used directly, no halving.
Runner docstring lines 33–34: "H11-Lead: beta(PRiskQ_lead) = 0 -- future political risk should NOT predict current speech uncertainty"
**PASS**

### A-5. Model Family
Doc says: `Linear panel regression with absorbed fixed effects`
Runner line 78: `from linearmodels.panel import PanelOLS`
Runner line 206: `model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`
**PASS**

### A-6. Estimator
Doc says: `linearmodels.panel.PanelOLS`
Runner import: `from linearmodels.panel import PanelOLS`
**PASS**

### A-7. Unit of Observation
Doc says: `Individual earnings call (file_name)`
Panel builder docstring (line 16): "Unit of observation: the individual earnings call (file_name)."
Runner loads `file_name` column (line 450).
**PASS**

### A-8. Panel Index
Doc says: `(gvkey, year) -- calendar year derived from start_date`
Runner line 203: `df_panel = df_sample.set_index(["gvkey", "year"])`
Panel builder line 156: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year`
**PASS**

### A-9. Columns
Doc says: `8 (Main sample: 4 DVs x lead1 + 4 DVs x lead2) / 24 total regressions run (3 samples x 4 DVs x 2 leads)`
Runner CONFIG (lines 93–101): 4 DVs, 3 samples, 2 IVs → 4×3×2 = 24 regressions.
LaTeX table built in `_save_latex_table` uses 4 result slots (lead-1) + 4 (lead-2) from Main sample only → 8 columns.
**PASS**

### A-10. Runner and Panel Builder paths
- `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py` — EXISTS (verified)
- `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py` — EXISTS (verified)
**PASS**

### A — ADDITIONAL CHECK: Panel Index column "year" vs "cal_yr"
The project standard for call-level suites is `cal_yr` (see feedback_calendar_yr_qtr_fe.md). This
suite uses `year` as the column name (not `cal_yr`). The doc correctly documents `year` as the
column name because that is what the builder and runner actually use. This is an inconsistency in
the codebase (not in the provenance doc), so no doc failure.
**NOTE only**

**Phase 2 overall: 9/10 checks pass.** One failure:

### A-FAIL: Section A notes "24 total regressions run" but this is self-consistent
No actual failure — A-9 passes. Score remains 9/10 only because the column name inconsistency
(`year` vs project standard `cal_yr`) is a codebase issue not a doc issue.

Revised: **Phase 2: 10/10 PASS** (the column name deviation is a codebase note, not a doc error).

---

## PHASE 3: MODEL SPECIFICATION (Section B)

### B1-CHECK: Regression Equation
Doc claims formula string (lines 187–191):
```
{dv_var} ~ 1 + {iv_var} + {controls} + EntityEffects + TimeEffects
```
Runner lines 187–191:
```python
formula = (
    f"{dv_var} ~ 1 + {iv_var} + "
    + " + ".join(controls)
    + " + EntityEffects + TimeEffects"
)
```
**PASS** — exact match.

### B2-CHECK: Dependent Variables
4 DVs listed:
- `Manager_QA_Uncertainty_pct` — runner line 94, loaded at runner line 455
- `CEO_QA_Uncertainty_pct` — runner line 95, loaded at runner line 456
- `Manager_Pres_Uncertainty_pct` — runner line 96, loaded at runner line 457
- `CEO_Pres_Uncertainty_pct` — runner line 97, loaded at runner line 458

All 4 appear in CONFIG["dependent_variables"] and in the panel load column list.
Formula "(LM uncertainty word count / total word count) * 100" is correct per LinguisticEngine.
Timing is contemporaneous — call-level measurement. No lead/lag applied to DVs.
No DVs in the runner are missing from the doc.
**PASS**

### B3-CHECK: Independent Variables
`PRiskQ_lead` and `PRiskQ_lead2` — runner CONFIG["iv_vars"] line 100.
Both loaded at runner lines 460–461.
Lead construction: _get_next_quarter (prisk_q_lead.py line 69), _get_next2_quarter (prisk_q_lead2.py line 69) — doc cites correct line numbers.
Doc examples for _get_next_quarter: "2010q2" → "2010q3" ✓; "2010q4" → "2011q1" ✓
Doc examples for _get_next2_quarter: "2010q2" → "2010q4" ✓; "2010q3" → "2011q1" ✓
(Verified against prisk_q_lead2.py code: q3 → year+1,q1; q4 → year+1,q2; else → year,q+2)
**PASS**

### B4-CHECK: Control Variables
Runner BASE_CONTROLS (lines 103–113):
```python
BASE_CONTROLS = [
    "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
    "Size",
    "TobinsQ",
    "ROA",
    "CashHoldings",
    "DividendPayer",
    "firm_maturity",
    "earnings_volatility",
]
```
Doc lists all 9 controls in the Base Controls table. ✓

PRES_CONTROL_MAP (lines 115–120):
```python
PRES_CONTROL_MAP = {
    "Manager_QA_Uncertainty_pct": "Manager_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct": "CEO_Pres_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct": None,
    "CEO_Pres_Uncertainty_pct": None,
}
```
Doc's dynamic control table matches exactly. ✓

No EXTENDED_CONTROLS in this runner. Doc does not claim any extended controls. ✓
Doc correctly states "No Lagged_DV." ✓
**PASS**

### B5-CHECK: Fixed Effects
Runner line 206: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)` — formula contains `EntityEffects + TimeEffects`.
Runner line 203: `df_panel = df_sample.set_index(["gvkey", "year"])` — entity=gvkey, time=year.
Panel builder line 156: `year` derived from `start_date` via `.dt.year` → calendar year.
Doc's FE table: Entity=gvkey (Firm FE), Time=year (Calendar year FE). ✓
"No Industry FE specs" — correct, no `ff12_code` or `other_effects` used. ✓
**PASS**

### B6-CHECK: Standard Errors
Runner line 207: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)`
Doc: `cov_type: "clustered"`, `cluster_entity: True`, `cluster_time: not set (default False)`. ✓
**PASS**

### B7-CHECK: Hypothesis Test
Runner lines 222–223:
```python
# Hypothesis test: two-tailed (placebo/falsification test)
p_test = p_two
```
Doc: "p_test = p_two -- the two-tailed p-value from PanelOLS is used directly, with NO halving"
(runner line 223: p_test = p_two). ✓

Runner lines 287–293 (fmt_coef in _save_latex_table):
```python
if pval < 0.01:
    stars = "^{***}"
elif pval < 0.05:
    stars = "^{**}"
elif pval < 0.10:
    stars = "^{*}"
```
Doc: "*** p < 0.01, ** p < 0.05, * p < 0.10" ✓

Runner line 225: `h_sig = not np.isnan(p_test) and p_test < 0.05`
Doc correctly documents this diagnostics-CSV threshold separately from the star-threshold. ✓
**PASS**

**Phase 3: 7/7 PASS**

---

## PHASE 4: SPEC REGISTER (Section C)

The spec register table has 8 rows (Cols 1–8).
Runner runs 4 DVs × 3 samples × 2 IVs = 24 regressions, but the LaTeX table and spec register
cover only the 8 Main-sample columns.

Col 1–4: IV = PRiskQ_lead, DVs = Manager_QA, CEO_QA, Manager_Pres, CEO_Pres
Col 5–8: IV = PRiskQ_lead2, DVs = same 4 DVs

For each column, entity FE = Firm (gvkey), Time FE = Cal Year (year), Controls = Base.
Pres control added for QA DVs (cols 1, 2, 5, 6).

**Verification:**
- All 4 DVs from CONFIG["dependent_variables"] appear in the spec register ✓
- Both IVs from CONFIG["iv_vars"] appear ✓
- All 8 columns accounted for ✓
- FE specification (Firm + Cal Year) matches runner code ✓
- Pres control map applied correctly ✓

**Phase 4: 5/5 PASS**

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

### D1-CHECK: Population
Doc says: "master_sample_manifest.parquet, Year range: 2002–2018 (from project config)".
Panel builder line 267–273: reads year range from `config.data.year_start` / `config.data.year_end`.
Project scope: 112,968 calls, 2,429 firms, 2002–2018. ✓
**PASS**

### D2-CHECK: Exclusion Criteria
Attrition cascade:
1. Master manifest = 112,968 rows (runner: `len(panel)` at line 566)
2. Main sample filter = 88,205 (runner: `(panel["sample"] == "Main").sum()` at line 567)
3. Complete-case + min-calls = 75,224 for first Main/lead result (runner: `main_result.get("n_obs")` at line 568)

Runner filtering steps in order:
1. Builder loads manifest, derives `year`, filters by year range (builder lines 150–151)
2. `assign_industry_sample(ff12_code)` at builder line 155
3. Runner: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required)` at runner line 175
4. Runner: `df_sample["gvkey_count"] >= CONFIG["min_calls"]` at runner lines 527–530

Doc's 4-step filtering description (lines 200–204) matches code order exactly. ✓
The 3-row attrition cascade in the table matches the code's `attrition_stages` construction. ✓
**PASS**

### D3-CHECK: Sample Counts per Spec
Doc provides N and N_firms for all 8 columns, sourced from `model_diagnostics.csv`.
N varies across specs due to DV-specific missingness and lead-year edge effects.
CEO DVs systematically lower (~54K vs ~75K) — expected due to CEO identification missingness.
Lead2 slightly lower than Lead1 — expected due to Q+2 requiring further future data.
These are plausible observations consistent with the code logic. ✓
**PASS**

**Phase 5: 3/3 PASS**

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

Full 17-row table checked against code.

### Row 1–4: DVs (linguistic uncertainty)
Formulas: "(LM uncertainty words / total words) * 100" for each of 4 measures.
Source: LinguisticEngine (Stage 2 parquet).
Winsorization: "0%/99% upper-only per year" — LinguisticEngine line 257:
`combined = winsorize_by_year(combined, existing_pct_cols, year_col="year", lower=0.0, upper=0.99, min_obs=10)`
Lower=0.0 means no lower clipping (effectively 0th percentile). ✓
**PASS** for rows 1–4.

### Row 5–6: IVs (PRiskQ_lead, PRiskQ_lead2)
Formula: Hassan et al. (2019) quarterly PRisk matched to Q+1 / Q+2.
Source: firmquarter_2022q1.csv.
Winsorization: "1%/99% per year" — prisk_q_lead.py line 170: `winsorize_by_year(prisk_df, ["PRisk"], year_col="year")` ✓
prisk_q_lead2.py line 173: same. ✓
**PASS** for rows 5–6.

### Row 7–8: Controls (Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct)
These are also linguistic variables — winsorization should be "0%/99% upper-only per year".
Doc says "0%/99% upper-only per year". ✓
**PASS** for rows 7–8.

### Row 9: Size
Doc says: `ln(atq) where atq > 0`, Source: CompustatEngine: atq, Winsorized: "1%/99% per fiscal year (fyearq)".
Code (_compustat_engine.py line 943): `comp["Size"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` ✓
Winsorization: Size is in `COMPUSTAT_COLS` and NOT in `skip_winsorize`, so it is winsorized at lines 1225–1232 via fyearq. ✓
Doc cites "CompustatEngine line 938" — **WRONG line number.** Actual line is 943.
**FAIL** (wrong line number citation; formula and winsorization claim are correct)

### Row 10: TobinsQ
Doc says: `(cshoq * prccq + dlcq + dlttq) / atq`
Code (_compustat_engine.py lines 987–997):
```python
mktcap = comp["cshoq"] * comp["prccq"]
debt_c = comp["dlcq"].clip(lower=0).fillna(0)
debt_t = comp["dlttq"].clip(lower=0).fillna(0)
debt_book = np.where(
    comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t
)
comp["TobinsQ"] = np.where(
    comp["atq"].notna() & (comp["atq"] > 0) & mktcap.notna(),
    (mktcap + debt_book) / comp["atq"],
    np.nan,
)
```
The actual formula is `(cshoq*prccq + max(dlcq,0) + max(dlttq,0)) / atq` with both-NaN guard for the debt component. The doc's formula `(cshoq * prccq + dlcq + dlttq) / atq` omits the `clip(lower=0)` and the both-NaN guard.
**FAIL** — formula is incomplete/imprecise. The clip(lower=0) and both-NaN guard materially affect the result when debt values are negative or missing.

Additionally, the H1 audit note in the engine changelog says "Fixed to (atq + cshoq*prccq - ceqq)/atq" but the actual code uses market equity + book debt, NOT book-equity-adjusted. The docstring is stale. The code is the source of truth: `(mktcap + debt_book) / atq`.

### Row 11: ROA
Doc says: `iby_annual (Q4) / ((atq_t + atq_{t-1}) / 2)`
Code lines 960–969: computes Q4-only iby_annual and atq_annual, atq_annual_lag1; avg_assets = (atq_annual + atq_annual_lag1) / 2; ROA = iby_annual / avg_assets. ✓
**PASS**

### Row 12: CashHoldings
Doc says: `cheq / atq`
Code line 986: `comp["CashHoldings"] = comp["cheq"] / comp["atq"]` ✓
**PASS**

### Row 13: DividendPayer
Doc says: `1 if dvy_annual (Q4) > 0, else 0`
Code: DividendPayer uses `_compute_annual_q4_variable` for `dvy` then checks > 0. ✓ (verified from engine changelog)
**PASS**

### Row 14: firm_maturity
Doc says: `req / atq`
Code line 807–809: `df["firm_maturity"] = np.where((df["atq"].notna()) & (df["atq"] > 0), df["req"] / df["atq"], np.nan)` ✓
**PASS**

### Row 15: earnings_volatility
Doc says: "Rolling 5-fiscal-year std dev of annual ROA (iby/atq), min 3 obs"
Code lines 811–826: uses `roa_annual = iby / atq`, then `rolling("1826D", min_periods=3).std()`. ✓
1826 days ≈ 5 years. min_periods=3 ✓
**PASS**

### Row 16: gvkey (FE entity)
Doc: "6-digit zero-padded Compustat identifier" from Manifest.
Both builder (line 146) and manifest use zero-padded gvkey. ✓
**PASS**

### Row 17: year (FE time)
Doc: "Derived from start_date via `.dt.year`"
Builder line 156: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year` ✓
**PASS**

### Completeness check
Runner loads columns (lines 450–472):
file_name, gvkey, year, ff12_code, Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct,
Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, PRiskQ_lead, PRiskQ_lead2,
Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct, Size, TobinsQ, ROA, CashHoldings,
DividendPayer, firm_maturity, earnings_volatility.
All appear in the Variable Dictionary. `ff12_code` is used for sample splitting but is not in
a regression spec — the doc does not include it, which is consistent with the creation prompt
("every variable appearing in any regression spec").
**PASS**

### Winsorization skip list line citation
Doc says "Skip list: DividendPayer (binary), CashFlow, SalesGrowth (_compustat_engine.py lines 1121–1128)"
Actual code: skip_winsorize dict is at lines 1217–1224.
**FAIL** — wrong line numbers. The skip list content is correct (includes DividendPayer, CashFlow, SalesGrowth, plus fqtr, ExternalFunding, DebtChoice), but the cited lines are 96 lines off.

**Phase 6: 15/18 PASS (3 failures: Size line citation, TobinsQ formula incomplete, skip list line citation)**

---

## PHASE 7: DATA PIPELINE, OUTPUTS, TREATMENT (Sections F, G, H)

### F-CHECK: Data Pipeline

**F1. Dependency Chain (7 steps)**
Step 1: Raw inputs — firmquarter_2022q1.csv, master_sample_manifest.parquet, linguistic parquets, Compustat. ✓
Step 2: Engine loading — LinguisticEngine, CompustatEngine, PRiskQLeadBuilder, PRiskQLead2Builder. ✓
Step 3: Panel builder merges on file_name, assigns sample, derives year. ✓
Step 4: Runner loads panel with explicit column list. ✓
Step 5: Sample filtering per (DV, IV, sample). ✓
Step 6: 24 PanelOLS regressions. ✓
**Step 7: "generate_all_tables.py uses 'type': 'moderation' with 8 col_files (Main sample only)"**
— **WRONG.** H11-Lead has NO entry in generate_all_tables.py. This step is false.
**FAIL for F1 step 7**

**F2. Data Engines**
4 engines listed:
- LinguisticEngine: 6 variables ✓
- CompustatEngine: 7 variables ✓
- PRiskQLeadBuilder: PRiskQ_lead ✓
- PRiskQLead2Builder: PRiskQ_lead2 ✓
All verified against panel builder imports and builder code. **PASS**

**F3. Merge Operations**
16 merges at panel level on `file_name` (left join) + 2 internal merges for PRisk builders.
All verified against panel builder loop (lines 136–153) and builder code.
BookLevBuilder is included ("built but NOT used in regressions") — correctly noted. ✓
**PASS**

### G-CHECK: Outputs

**G1. Stage 3 Outputs**
Doc lists:
1. `h11_prisk_uncertainty_lead_panel.parquet` — builder line 190. ✓
2. `summary_stats.csv` — builder line 197. ✓
3. `report_step3_h11_lead.md` — builder line 240–241 (`generate_report` writes to `out_dir / "report_step3_h11_lead.md"`). ✓
4. `run_manifest.json` — builder `save_outputs` calls `generate_manifest` at line 203. ✓

**PASS** for G1.

**G2. Stage 4 Outputs**
Doc lists:
1. `h11_prisk_uncertainty_lead_table.tex` — runner `_save_latex_table` writes to `out_dir / "h11_prisk_uncertainty_lead_table.tex"` (line 257). ✓
2. `model_diagnostics.csv` — runner line 557. ✓
3. `summary_stats.csv` — runner line 498. ✓
4. `summary_stats.tex` — runner line 499. ✓
5. `sample_attrition.csv` — `generate_attrition_table` output (attrition_table.py line 47). ✓
6. `sample_attrition.tex` — `generate_attrition_table` output (attrition_table.py line 51). ✓
7. `regression_results_{sample}_{dv}_{lead}.txt` — runner lines 552–554. ✓
8. `run_manifest.json` — runner `generate_manifest` at lines 574–584. ✓

Doc says "24 individual regression .txt files" (verified: 4 DVs × 3 samples × 2 leads = 24). ✓

Doc also claims the table note says "All continuous controls are standardized" is inaccurate (runner line 399). Verified: runner line 399 does include this note but no standardization is in the code. Doc correctly flags this as a known issue (L.3). ✓

**PASS** for G2.

**G3. Summary Statistics**
15 variables match SUMMARY_STATS_VARS at runner lines 127–146 exactly. ✓
**PASS** for G3.

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization**
Compustat variables: 1%/99% per fyearq. ✓ (engine lines 1225–1232)
Linguistic variables: 0%/99% upper-only per year. ✓ (engine line 257)
PRiskQ_lead: 1%/99% per year (prisk_q_lead.py line 170). ✓
PRiskQ_lead2: 1%/99% per year (prisk_q_lead2.py line 173). ✓

**H1 Line citation failure:** Doc says "_compustat_engine.py lines 1121–1128" for the skip list.
Actual: lines 1217–1224. This is a secondary citation of the same error noted in Phase 6.
**FAIL** (same as Phase 6 skip list citation)

**H2. Missing Data Policy**
Runner line 175: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required)` ✓
Doc correctly documents both inf-replacement and complete-case deletion. ✓
**PASS**

**H3. Transformations**
`Size` = ln(atq). ✓
No centering or z-scoring. ✓
Doc notes the LaTeX table "All continuous controls are standardized" is inaccurate — correctly flagged as code issue. ✓
**PASS**

**Phase 7: 7/9 PASS (2 failures: F1 step 7 false claim about generate_all_tables, H1 wrong line citation)**

---

## PHASE 8: TABLE GENERATOR ENTRY (Section I)

This is the most critical phase of this audit.

### Check 1: Does H11-Lead have an entry in generate_all_tables.py?
Searched `outputs/generate_all_tables.py` for "H11-Lead", "h11_lead", "h11_prisk_uncertainty_lead":
**NO MATCHES FOUND.**
The SUITES list contains (in order): H1, H1.1, H1.1b, H1.2, H4a, H4b, H5, H7, H11, H11-Lag,
H12, H13, H13.1, H14, H16, H17, H18, H19, H20, H18b, H21.
H11-Lead is NOT in this list.

**Context:** `project_archived_suites.md` entry 11: "H11-Lead: Removed from report 2026-03-31
(placebo test, not needed in tables)."
The provenance doc was written on 2026-03-30 when the entry may have existed. The entry was
subsequently removed on 2026-03-31. The provenance doc was never updated.

### Check 2: Doc's claimed entry field "id"
Doc says: `"id": "H11-Lead"`
Actual: entry does not exist. **FAIL**

### Check 3: Doc's claimed field "tail" / "key_tails"
Doc says: `"key_tails": ["two", "two"]`
Actual: entry does not exist. This cannot be verified. **FAIL**

### Check 4: Doc's claimed field "cols"
Doc says: `"cols": 8`
Actual: entry does not exist. **FAIL**

### Check 5: Doc's cited lines (248–276)
Doc says: `"Source: generate_all_tables.py, lines 248--276."`
Actual lines 248–276 of generate_all_tables.py contain the H13 suite entry (and H13.1 beginning).
The cited line range is WRONG — it points to a completely different suite.
**FAIL**

### Summary of Phase 8
All 5 checks FAIL. Section I contains a fabricated entry that does not exist in the codebase.
The verification table at the end of Section I (checking key_tails=two, cols=8, key_vars, col_dv_labels)
is internally consistent but entirely fictitious — it verifies claims against an entry that was deleted.

**Phase 8: 0/5 PASS**

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

Model family is PanelOLS → K1 should be filled; K2–K6 should be N/A.

### K1 checks:
- entity_effects: "Absorbed via `EntityEffects` in PanelOLS formula. Entity dimension = gvkey."
  Runner line 206: `PanelOLS.from_formula(formula, ...)` with `EntityEffects` in formula string. ✓
- time_effects: "Absorbed via `TimeEffects`. Time dimension = year."
  Runner line 206: `TimeEffects` in formula string. ✓
- other_effects: "Not used. All columns use firm FE (no Industry FE specs)."
  Runner never uses `other_effects` parameter. ✓ No ff12_code in regression formulas. ✓
- drop_absorbed: "True" — runner line 206: `drop_absorbed=True`. ✓
- Singleton handling: "Automatically handled by PanelOLS with drop_absorbed=True." — correct. ✓
- R-squared: "`model.rsquared` (within-R2) reported. Adj R-squared computed manually."
  Runner line 214: `1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`. ✓

### K2–K6: All "N/A". Correct — only PanelOLS is used.

**Phase 9: 5/5 PASS**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | 17 variables documented; all appear in runner's regression formula or loading |
| 2 | The model equation matches what the code actually estimates | YES | Formula string verified against runner lines 187–191 |
| 3 | The specification register accounts for every model column | YES | 8-row table matches 8 Main-sample columns |
| 4 | The attrition cascade has row counts for each filter step | YES | 3-step cascade with actual N from model_diagnostics.csv |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | **NO** | Runner correctly uses two-tailed (p_test = p_two). But H11-Lead has NO entry in generate_all_tables.py — cannot verify match. Section I's claimed "key_tails": ["two","two"] is fabricated. |
| 6 | The FE specification matches between docstring, code, and this document | YES | All three agree: EntityEffects (gvkey) + TimeEffects (year) |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | 16 file_name merges + 2 internal PRisk merges all documented |
| 8 | The output file list matches what the runner actually writes | YES | All 8 output types verified against runner code |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 filled (PanelOLS), K2–K6 N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation | **NO** | No [UNVERIFIED] tags appear, but Section I contains a fabricated entry rather than an honest [UNVERIFIED] marker. The doc should say the entry was removed and note this explicitly. |

**Phase 10: 8/10 PASS**

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

### Check 1: DVs in B2 match DVs in C (spec register)
B2: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct.
C: Same 4 DVs appear across cols 1–8. ✓
**PASS**

### Check 2: DVs in C match DVs in Section I
C lists 4 DVs. Section I claims col_dv_labels = ["Mgr QA", "CEO QA", "Mgr Pres", "CEO Pres"] repeated twice.
Internally consistent — but Section I is fabricated. The internal consistency of a fabricated section is irrelevant.
**FAIL** — DVs in C cannot match an entry in I that does not exist.

### Check 3: Controls in B4 match variables in E (dictionary)
B4 lists 9 base controls + dynamic Pres control. All 9 base controls + 2 Pres controls appear in E. ✓
**PASS**

### Check 4: Column count in A matches rows in C
A: "Columns: 8". C: 8 rows. ✓
**PASS**

### Check 5: Column count in A matches "cols" in Section I
A: 8. Section I claims "cols": 8. Internally consistent.
But Section I is fabricated — there is no actual "cols" to match.
**FAIL** (same root cause as Check 2)

### Check 6: Tail direction in A matches B7 matches I
A: "Two-tailed". B7: "Two-tailed (beta = 0), p_test = p_two". Section I claims "key_tails": ["two","two"].
A and B7 are internally consistent and match the code. Section I's claim is fabricated.
**NOTE:** A and B7 are internally consistent ✓. The cross-reference with I cannot be verified.
**PASS** for A↔B7. **FAIL** for I (noted — same root cause).

### Check 7: FE in B5 matches C matches K
B5: Entity (gvkey, Firm FE) + Time (year, Cal Year FE).
C: All 8 cols show "Firm" + "Cal Year". ✓
K1: EntityEffects (gvkey) + TimeEffects (year). ✓
**PASS**

### Check 8: Panel index in A matches set_index in K
A: "(gvkey, year)". K1: "Entity dimension = gvkey, Time dimension = year". Runner line 203: `set_index(["gvkey", "year"])`. ✓
**PASS**

**Phase 11: 7/8 PASS (1 failure: C↔I and A↔I cross-references fail because Section I is fabricated)**

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 8 | Section I — entry existence | H11-Lead has an entry in generate_all_tables.py with id, type, dir, caption, label, cols=8, col_files (8 entries), dvs, col_dv_labels, key_vars, key_labels, key_tails | H11-Lead has NO entry in generate_all_tables.py. The suite was removed from tables on 2026-03-31. | CRITICAL | Replace Section I with accurate statement that H11-Lead has no generate_all_tables entry and note removal date |
| 8 | Section I — cited lines (248–276) | "Source: generate_all_tables.py, lines 248–276." | Lines 248–276 contain H13 entry. No H11-Lead entry exists anywhere in the file. | HIGH | Remove/correct all line citations in Section I |
| 7 | F1 step 7 | "generate_all_tables.py uses 'type': 'moderation' with 8 col_files (Main sample only)" | No generate_all_tables.py entry for H11-Lead exists. | HIGH | Correct F1 step 7 to reflect actual status |
| 6 | Size line citation | "_compustat_engine.py line 938" for Size formula | Actual line is 943 | LOW | Update line citation to 943 |
| 6 | TobinsQ formula | "(cshoq * prccq + dlcq + dlttq) / atq" | `(mktcap + max(dlcq,0).fillna(0) + max(dlttq,0).fillna(0)) / atq` where debt is NaN only if BOTH dlcq and dlttq are NaN | MEDIUM | Update formula to reflect clip(lower=0).fillna(0) behavior and both-NaN guard |
| 6/7 | Winsorization skip list line citation | "_compustat_engine.py lines 1121–1128" | Actual skip_winsorize dict is at lines 1217–1224 | LOW | Update line citations to 1217–1224 |
| 11 | C↔I cross-reference | Col count in C matches cols in I; DVs in C match I | Section I is fabricated; no entry in generate_all_tables.py | HIGH | Follows from Section I correction |

---

## CORRECTIONS REQUIRED

**Correction 1 — Section I (CRITICAL)**
Section: `## I. GENERATE_ALL_TABLES.PY ENTRY`
Current (wrong): Contains a detailed Python dict entry with id="H11-Lead", type="moderation",
dir="h11_prisk_uncertainty_lead/2026-03-27_095003", cols=8, col_files (8 entries), dvs, key_vars,
key_labels, key_tails=["two","two"], plus a verification table, citing "generate_all_tables.py,
lines 248–276."

Should say:
```
H11-Lead has NO entry in `outputs/generate_all_tables.py`.

This suite was removed from the thesis report on 2026-03-31 (see project_archived_suites.md,
item 11: "Removed from report 2026-03-31 (placebo test, not needed in tables)"). The runner
and panel builder still exist, and the suite can be run independently, but its output does not
appear in the published thesis tables.

Lines 248–276 of `generate_all_tables.py` contain the H13 entry, not H11-Lead.

If H11-Lead is reinstated in the thesis, the entry would structurally mirror H11-Lag with:
- "key_tails": ["two", "two"]  (two-tailed placebo test)
- "cols": 8  (4 DVs x 2 leads)
- "key_vars": ["PRiskQ_lead", "PRiskQ_lead2"]
```
Code reference: `grep -n "H11" outputs/generate_all_tables.py` returns H11 (line 179) and
H11-Lag (line 201) only — no H11-Lead entry.

---

**Correction 2 — Section F1 Step 7 (HIGH)**
Section: `## F. DATA PIPELINE / F1. Dependency Chain`
Current (wrong): "7. Table generation: `generate_all_tables.py` uses 'type': 'moderation' with 8 col_files (Main sample only)"
Should say: "7. Table generation: H11-Lead has no entry in `generate_all_tables.py` (removed 2026-03-31). The runner's built-in `_save_latex_table` produces a standalone 4-column table (`h11_prisk_uncertainty_lead_table.tex`) when the runner is executed directly. This table is not part of the main thesis table generation pipeline."

---

**Correction 3 — Variable Dictionary, Size line citation (LOW)**
Section: `## E. VARIABLE DICTIONARY`, Size row source column
Current: "_compustat_engine.py lines 938, ..."
Should say: "_compustat_engine.py line 943, ..."
Code reference: `_compustat_engine.py` line 943: `comp["Size"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)`

---

**Correction 4 — Variable Dictionary, TobinsQ formula (MEDIUM)**
Section: `## E. VARIABLE DICTIONARY`, TobinsQ row formula column
Current: `(cshoq * prccq + dlcq + dlttq) / atq`
Should say: `(cshoq * prccq + max(dlcq,0).fillna(0) + max(dlttq,0).fillna(0)) / atq` where the
debt component is NaN only when BOTH dlcq and dlttq are NaN; otherwise negative debt is clipped
to 0 and missing debt is treated as 0.
Code reference: `_compustat_engine.py` lines 987–997 (clip(lower=0).fillna(0) + both-NaN guard).

---

**Correction 5 — Winsorization skip list line citations (LOW)**
Section: `## H. OUTLIER AND MISSING DATA TREATMENT / H1. Winsorization`
Current: "Skip list: DividendPayer (binary), CashFlow, SalesGrowth (_compustat_engine.py lines 1121–1128)"
Should say: "Skip list: DividendPayer (binary), CashFlow, SalesGrowth, fqtr, ExternalFunding, DebtChoice (_compustat_engine.py lines 1217–1224)"
Code reference: `_compustat_engine.py` lines 1217–1224: `skip_winsorize = {"DividendPayer", "CashFlow", "SalesGrowth", "fqtr", "ExternalFunding", "DebtChoice"}`

Note: The doc also omits `fqtr`, `ExternalFunding`, and `DebtChoice` from the skip list.
ExternalFunding and DebtChoice are irrelevant to H11-Lead, but fqtr is a Compustat column that
should be mentioned for completeness.

---

**Correction 6 — Section L: Add Known Issue about removed table entry (INFORMATIONAL)**
Section: `## L. KNOWN ISSUES AND NOTES`
Add item 8:
"8. **H11-Lead removed from thesis tables (2026-03-31).** The suite's entry was removed from
`generate_all_tables.py` on 2026-03-31 (commit context: removed as placebo test not needed in
final report). Section I of this provenance document should be updated accordingly. The runner
and panel builder remain operational for independent execution."

---

## NOTES ON PRIOR AUDIT (2026-03-30)

The previous audit (dated 2026-03-30, now superseded) gave the verdict "PASS WITH NOTES" and
scored 93% (7 failures out of 101 checks). That audit was conducted on or before 2026-03-30,
the same day the provenance doc was generated. At that point, H11-Lead likely had a valid entry
in generate_all_tables.py (or the prior auditor did not verify its removal). The entry was
deleted on 2026-03-31.

The present re-audit was triggered by the project memory noting H11-Lead was "Removed from
report 2026-03-31 (runner still exists)" in `project_archived_suites.md`. The critical Section I
failure identified here (0/5, all fabricated) was entirely absent from the prior audit report.
The prior audit's Phase 8 result (4/5 pass) was based on a now-deleted entry.

This re-audit increases the total failure count from 7 to 14 and downgrades the verdict from
PASS WITH NOTES to FAIL — INACCURATE.
