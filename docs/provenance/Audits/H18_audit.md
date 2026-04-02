# Adversarial Audit: Provenance Document for Suite H18

**Audit Date**: 2026-04-01
**Auditor**: Hostile Auditor (Claude Sonnet 4.6) — Assume Everything Is Wrong
**Provenance Doc**: `docs/provenance/H18.md`
**Runner**: `src/f1d/econometric/run_h18_cccl_received.py`
**Panel Builder**: `src/f1d/variables/build_h18_cccl_received_panel.py`
**Creation Prompt**: `docs/Prompts/Suite Provenance Doc.txt`
**Audit Prompt**: `docs/Prompts/Audit Provenance doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 25 | 25 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 9 | 1 | 90% |
| Model Specification (Phase 3) | 7 | 6 | 1 | 86% |
| Spec Register (Phase 4) | 7 | 7 | 0 | 100% |
| Sample Construction (Phase 5) | 5 | 5 | 0 | 100% |
| Variable Dictionary (Phase 6) | 22 | 22 | 0 | 100% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 7 | 2 | 78% |
| Table Generator Entry (Phase 8) | 5 | 3 | 2 | 60% |
| Model-Family Addendum (Phase 9) | 6 | 5 | 1 | 83% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **114** | **106** | **8** | **93.0%** |

---

## VERDICT

**FAIL — INACCURATE**: Eight factual errors found. Most are wrong line number references (stale from a prior code version), one is a stale directory timestamp in the generate_all_tables.py entry, one is a misrepresented code snippet in B7, and one is an undocumented discrepancy between the runner docstring and the builder implementation. None of the errors affect the substantive description of variable construction, model specification, or hypothesis test direction, but they violate the "cite file path + line for every claim about code behavior" requirement of the creation prompt.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 8 | I — generate_all_tables.py dir field | `"dir": "h18_cccl_received/2026-03-27_095021"` | `"dir": "h18_cccl_received/2026-03-31_151907"` (generate_all_tables.py line 333) | Medium | Update dir to match current generate_all_tables.py entry |
| 8 | I — generate_all_tables.py line numbers | "lines 405-417" | H18 entry is at lines 330-342 | Medium | Update line citation |
| 7 | H2 — CompustatEngine line for `_compute_and_winsorize` | "CompustatEngine line 1134" | `_compute_and_winsorize` defined at line 936; line 1134 is inside a repurchase computation, unrelated | Medium | Correct to line 936 |
| 7 | H2 — CompustatEngine line for missing xrdq = 0 | "CompustatEngine line 967" | `comp["RDSales"] = comp["xrdq"].fillna(0) / comp["atq"]` is at line 972 | Minor | Correct to line 972 |
| 7 | H2 — CompustatEngine line for missing debt = 0 | "CompustatEngine line 943" | `comp["Leverage"] = (comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]` is at line 948; line 943 is lnAssets computation | Minor | Correct to line 948 |
| 3 | B7 — p-value code snippet | Shows 4-line if/else with bare `if beta > 0:` check | Actual is a ternary inside a NaN guard: `if not np.isnan(p_two) and not np.isnan(beta): p_one = p_two / 2 if beta > 0 else 1 - p_two / 2 else: p_one = np.nan` (runner lines 310-313) | Minor | Replace simplified snippet with exact code from runner |
| 9 | K1 — check_rank line number | "runner line 278" | `check_rank=False` is at line 277 | Minor | Correct to line 277 |
| 2/L | Known Issues — runner docstring vs builder contradiction not flagged | L.4 flags the `_fwd` label vs `CCCL` column name; does NOT flag that runner docstring line 10-11 says "between this call and the next call / Window: (start_date_current, start_date_next_call]" — contradicting builder's calendar-quarter (Q+1) implementation | Builder `create_cccl_dvs()` computes `CCCL = 1 if (gvkey, Q+1_calendar_quarter) in cccl_set` — a forward-looking calendar-quarter lookup, NOT a call-to-next-call window | Medium | Add to L. Known Issues that runner docstring lines 10-11 describe a call-to-call window that does not match the builder's calendar-quarter Q+1 implementation |

---

## PHASE 1: STRUCTURAL COMPLETENESS

Read creation prompt `docs/Prompts/Suite Provenance Doc.txt` for required sections A-L. Read `docs/provenance/H18.md` for presence and completeness.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | All 11 YAML fields populated |
| B. Model Specification | Yes | Yes | Yes | |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX-compatible equation with alpha_j / gamma_t notation |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table + 5-step construction detail |
| B3. Independent Variable(s) | Yes | Yes | Yes | 4-row IV table |
| B4. Control Variables | Yes | Yes | Yes | Separate Base + Extended tables; Lagged_DV detail paragraph |
| B5. Fixed Effects | Yes | Yes | Yes | 4-row FE table with col assignments |
| B6. Standard Errors | Yes | Yes | Yes | cov_type and cluster_entity documented |
| B7. Hypothesis Test | Yes | Yes | Yes | Direction, p-value conversion, significance thresholds |
| C. Spec Register | Yes | Yes | Yes | 6-row table, one per MODEL_SPEC |
| D. Sample Construction | Yes | Yes | Yes | |
| D1. Population | Yes | Yes | Yes | Starting dataset, counts, year range |
| D2. Exclusion Criteria | Yes | Yes | Yes | 4-step attrition cascade |
| D3. Sample Counts per Spec | Yes | Yes | Yes | 6-row table |
| E. Variable Dictionary | Yes | Yes | Yes | 21-row table (all DVs, IVs, controls, FE cols) |
| F. Data Pipeline | Yes | Yes | Yes | |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 5-engine table |
| F3. Merge Operations | Yes | Yes | Yes | 3-row merge table |
| G. Outputs | Yes | Yes | Yes | |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 3 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 13 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 17 variables listed with metrics |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1 winsorization, H2 missing policy, H3 transformations |
| I. generate_all_tables Entry | Yes | Yes | Partial | Entry present but dir is stale and line numbers wrong |
| J. Reproduction Commands | Yes | Yes | Yes | Three commands with correct module paths |
| K. Model-Family Addendum | Yes | Yes | Partial | K1 filled (correct); K3 also filled (LPM specifics); K2/K4/K5/K6 = N/A |
| L. Known Issues | Yes | Yes | Yes | 6 items documented |

**Phase 1 verdict**: PASS (all required sections present; two incomplete items noted for Phase 8 and Phase 9 follow-up)

---

## PHASE 2: FACTUAL ACCURACY — SECTION A (Suite Identity)

**A-1. Suite ID**
- Doc: `H18`
- Verification: matches runner filename and builder filename.
- **PASS**

**A-2. Title**
- Doc: "Speech Uncertainty and SEC Comment Letters"
- Runner: no single `Title:` field, but runner docstring description says "H18 hypothesis test — does speech uncertainty predict SEC comment letter receipt in subsequent quarters?" and LaTeX caption at line 369 says `\caption{Speech Uncertainty and SEC Comment Letters}`.
- Evidence: runner line 369: `r"\caption{Speech Uncertainty and SEC Comment Letters}"`
- **PASS**

**A-3. Hypothesis**
- Doc: "Does speech uncertainty during earnings calls predict SEC comment letter receipt in the subsequent calendar quarter?"
- Runner docstring line 7-8: "does speech uncertainty predict SEC comment letter receipt in subsequent quarters?"
- Substance matches. Doc specifies "calendar quarter" which is the builder's implementation; runner docstring says "subsequent quarters." Minor wording difference, substantively correct.
- **PASS**

**A-4. Direction (tail test)**
- Doc: "One-tailed (beta > 0)"
- Runner docstring line 26: "One-tailed (beta > 0 — higher uncertainty -> more SEC scrutiny)"
- Runner lines 310-311: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2`
- generate_all_tables.py line 341: `"hyp_dir": ">"`
- **PASS**

**A-5. Model Family**
- Doc: "LPM (Linear Probability Model)"
- Runner import line 59: `from linearmodels.panel import PanelOLS`
- Runner line 270-284: `PanelOLS(...)` and `PanelOLS.from_formula(...)`
- Runner docstring line 28: "Estimator: LPM via PanelOLS (Linear Probability Model)"
- **PASS**

**A-6. Estimator**
- Doc: `linearmodels.panel.PanelOLS`
- Runner line 59: `from linearmodels.panel import PanelOLS`
- **PASS**

**A-7. Unit of Observation**
- Doc: "Call-level (individual earnings call)"
- Builder docstring line 8: "Unit of observation: individual earnings call (file_name)"
- **PASS**

**A-8. Panel Index**
- Doc: "(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6"
- Runner line 266: `df_panel = df_prepared.set_index(["gvkey", time_col])`
- Runner line 249: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`
- Cols 1-4 have fe "industry" or "firm" (no "_yq" suffix) → time_col = "cal_yr". Cols 5-6 have "industry_yq" or "firm_yq" → time_col = "cal_yr_qtr"
- **PASS**

**A-9. Columns**
- Doc: 6
- Runner MODEL_SPECS (lines 91-99): 6 entries (col 1 through col 6)
- **PASS**

**A-10. Runner and Panel Builder paths**
- Doc: `src/f1d/econometric/run_h18_cccl_received.py` — file confirmed to exist.
- Doc: `src/f1d/variables/build_h18_cccl_received_panel.py` — file confirmed to exist.
- **PASS**

**PHASE 2 FAILURE:**
- A-2 sub-note: Runner docstring says "predict SEC comment letter receipt in subsequent quarters?" (plural, no "calendar quarter" qualifier). Doc says "subsequent **calendar** quarter." The doc uses the builder's implementation (Q+1 calendar quarter), which is more accurate than the runner docstring. However, the runner docstring further contradicts itself by saying DV window is "(start_date_current, start_date_next_call]" (a call-to-call window), which is NOT what the builder implements. This contradiction is partially flagged in L.4 but the runner docstring vs builder implementation discrepancy is not fully articulated. Mark as **FAIL** — see Corrections item 8.

**Phase 2 Score**: 9/10 — A-2 partially fails (runner docstring vs builder discrepancy not fully captured in Known Issues).

---

## PHASE 3: FACTUAL ACCURACY — SECTION B (Model Specification)

**B1-CHECK: Regression Equation**
- Doc equation: `CCCL_{i,t} = b1*UncAnsCEO + b2*UncPreCEO + b3*UncAnsMgr + b4*UncPreMgr + Controls + alpha_j + gamma_t + epsilon_{i,t}`
- Runner lines 261: `exog = KEY_IVS + controls` where KEY_IVS has 4 items and controls is BASE_CONTROLS or EXTENDED_CONTROLS. DV is always "CCCL" (all 6 specs use the same DV).
- Alpha_j notation: for industry FE (odd cols) = other_effects on ff12_code; for firm FE (even cols) = EntityEffects on gvkey. Both documented.
- Gamma_t notation: cal_yr or cal_yr_qtr. Documented.
- **PASS**

**B2-CHECK: Dependent Variable(s)**
- Doc: CCCL = "1 if `(gvkey, cal_qtr_id+1)` exists in CCCL event set"
- Builder `create_cccl_dvs()` (lines 272-276): `q_next = _next_cal_qtr(q)` then `cccl_fwd[i] = 1.0 if (g, q_next) in cccl_set else 0.0`. Then `panel["CCCL"] = cccl_fwd` at line 279.
- This is "next calendar quarter Q+1" — matches doc.
- Timing claim: "Lead (Q+1)" — PASS
- Source: "CCCL input file + CIK-gvkey map" — PASS
- **PASS**

**B3-CHECK: Independent Variable(s)**
- Doc lists 4 IVs: UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr
- Runner KEY_IVS (lines 72-77): exactly these 4. **PASS**
- Winsorization claim: "0%/99% per-year (upper-only)" — verified at `_linguistic_engine.py` line 255-257: `winsorize_by_year(combined, cols, year_col="year", lower=0.0, upper=0.99)`. **PASS**
- Source: "LinguisticEngine (Stage 2 outputs)" — verified by builder imports: `CEOQAUncertaintyBuilder`, `CEOPresUncertaintyBuilder`, `ManagerQAUncertaintyBuilder`, `ManagerPresUncertaintyBuilder` all call `engine.get_data()` from `_linguistic_engine`. **PASS**
- NOTE: `ceo_qa_uncertainty.py` docstring says "Winsorization (pooled 1%/99%)" but the engine applies "0%/99% per-year (upper-only)." The provenance doc correctly uses the engine's actual behavior, not the stale builder docstring. This is an engine-level fix not yet reflected in the builder docstring, but the provenance doc is correct.
- **PASS**

**B4-CHECK: Control Variables**
- BASE_CONTROLS (runner lines 79-83): lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, DivDummy, sCFO, Lagged_DV — 9 variables.
- Doc base controls table: lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, DivDummy, sCFO, Lagged_DV — 9 variables. **PASS**
- EXTENDED_CONTROLS (runner lines 85-87): BASE_CONTROLS + SalesGrowth, RDSales, CashFlowAt, DailyVola — 13 total.
- Doc extended controls: "Base Controls plus: SalesGrowth, RDSales, CashFlowAt, DailyVola" — **PASS**
- Lagged_DV detail: runner line 200 `panel["Lagged_DV"] = panel["CCCL_lag"]`. Doc says "assigned from CCCL_lag, which is the binary indicator for whether the firm received a comment letter in the calendar quarter preceding the call (Q-1)." Builder confirms: `cccl_lag[i] = 1.0 if (g, q_prev) in cccl_set` at line 277. **PASS**
- **PASS**

**B5-CHECK: Fixed Effects**
- Industry FE: runner lines 270-278 use `entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"]`. Doc says "Industry | ff12_code | … via `other_effects`". **PASS**
- Firm FE: runner lines 282-283 use `EntityEffects + TimeEffects` in formula. Doc says "Firm | gvkey | Entity FE via `EntityEffects`". **PASS**
- Cal Yr: time_col = "cal_yr" for non-_yq specs. **PASS**
- Cal Yr-Qtr: time_col = "cal_yr_qtr" for _yq specs. **PASS**
- Calendar derivation: `build_cal_yr_qtr_index()` at panel_utils.py line 195-218; cal_yr = start_date.dt.year, cal_yr_qtr = year*10+quarter. Doc says "start_date.dt.year via `time_effects=True`". Correctly documented.
- **PASS**

**B6-CHECK: Standard Errors**
- Doc: `cov_type="clustered"`, `cluster_entity=True`, firm-clustered
- Runner line 279: `model_obj.fit(cov_type="clustered", cluster_entity=True)`
- Runner line 284: `model_obj.fit(cov_type="clustered", cluster_entity=True)`
- **PASS**

**B7-CHECK: Hypothesis Test**
- Doc direction: one-tailed (beta > 0). **PASS**
- Doc p-value code snippet:
  ```python
  if beta > 0:
      p_one = p_two / 2
  else:
      p_one = 1 - p_two / 2
  ```
- Actual runner lines 310-313:
  ```python
  if not np.isnan(p_two) and not np.isnan(beta):
      p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
  else:
      p_one = np.nan
  ```
- **FAIL**: The provenance doc simplifies the code into a bare if/else without the NaN guard. The actual code (a) uses a ternary expression, not a standalone `if beta > 0:`, and (b) wraps the entire computation in a NaN-guard block. The simplified form misrepresents the actual implementation. Semantically the net effect is identical (the NaN case produces NaN either way), but the code as cited is incorrect.

**Phase 3 Score**: 6/7 — B7 code snippet misrepresents the actual implementation.

---

## PHASE 4: FACTUAL ACCURACY — SECTION C (Spec Register)

**Row count**: Doc has 6 rows. MODEL_SPECS has 6 entries. **PASS**

| Col | Doc DV | Code DV | Doc Entity FE | Code fe | Doc Time FE | Code time_col | Doc Controls | Code controls | PASS? |
|-----|--------|---------|---------------|---------|-------------|---------------|--------------|---------------|-------|
| 1 | CCCL | CCCL | Industry (FF12) | industry | Cal Year | cal_yr | Base | base | PASS |
| 2 | CCCL | CCCL | Firm | firm | Cal Year | cal_yr | Base | base | PASS |
| 3 | CCCL | CCCL | Industry (FF12) | industry | Cal Year | cal_yr | Extended | extended | PASS |
| 4 | CCCL | CCCL | Firm | firm | Cal Year | cal_yr | Extended | extended | PASS |
| 5 | CCCL | CCCL | Industry (FF12) | industry_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |
| 6 | CCCL | CCCL | Firm | firm_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |

Doc says "Confirmed 6 entries" and "runner lines 91-99" — MODEL_SPECS starts at line 91 and has 6 entries ending at line 99. **PASS**

No specs missing. No specs extra. **Phase 4 Score**: 7/7.

---

## PHASE 5: FACTUAL ACCURACY — SECTION D (Sample Construction)

**D1-CHECK: Population**
- Doc: 112,968 calls, year range 2002-2018
- Cross-reference: project scope per memory says 112,968 calls, 2,429 firms, 2002-2018. **PASS**
- Doc: "Unique firms (full panel): per manifest" — acknowledges the firm count is not stated directly. Reasonable.
- **PASS**

**D2-CHECK: Exclusion Criteria**
- Step 1: "Full panel | 112,968". Runner line 538: `full_n = len(panel)` before filter. Main function loads panel then records full_n. **PASS**
- Step 2: "Main sample (excl FF12=8,11 Finance/Utility) | 88,205". Runner line 182: `main = panel[~panel["ff12_code"].isin([8, 11])]`. **PASS**
- Step 3: "CCCL=1 in Main (informational) | 280". Runner lines 545-546: `n_dv1 = (panel["CCCL"] == 1).sum()`. Used in attrition table at line 583. This is informational, not a filter. **PASS**
- Step 4: "After complete-case + min-calls (col 1) | 57,216". Runner lines 215-228: DV filter → complete-case → min 5 calls per firm. **PASS**
- Doc note: "CCCL is fully populated for all main sample rows because any firm-quarter without a CCCL event is coded as 0." Builder: `cccl_fwd = np.zeros(len(panel), dtype=np.float64)` then only set to 1 or NaN. NaN only when `pd.isna(q)` (no start_date). For firms with valid start_date, CCCL is always 0 or 1. **PASS**

**D3-CHECK: Sample Counts per Spec**
- Doc shows cols 1-2: N=57,216, firms=1,615; cols 3-6: N=54,915, firms=1,595
- These come from actual run outputs. Cannot verify from code alone (runtime-dependent). Plausible: cols 1-2 use fewer controls (base) so fewer rows dropped for missingness. **UNVERIFIED by code — depends on run data, but reported from actual output files.**
- **PASS (plausible, sourced from actual outputs)**

**Phase 5 Score**: 5/5.

---

## PHASE 6: FACTUAL ACCURACY — SECTION E (Variable Dictionary)

For each variable: checked name, formula, source, winsorization, timing against code.

| Variable | Code Name | Formula | Source | Winsorized | Timing | Status |
|----------|-----------|---------|--------|------------|--------|--------|
| CCCL | Matches | "1 if (gvkey, Q+1) in cccl_set" — matches builder lines 272-276, 279 | CCCL input + CIK-gvkey map — matches | No (binary) — correct | Lead (Q+1) | PASS |
| UncAnsCEO | Matches runner KEY_IVS | "Uncertainty words / total words * 100, CEO Q&A" — matches LinguisticEngine output column description | LinguisticEngine: Stage 2 — matches builder import | 0%/99% per-year (upper-only) — matches `_linguistic_engine.py` line 255-257 with lower=0.0, upper=0.99 | Contemporaneous | PASS |
| UncPreCEO | Matches | Same formula, CEO Pres section | Same engine | Same winsorization | Contemporaneous | PASS |
| UncAnsMgr | Matches | Same formula, Mgr Q&A | Same engine | Same winsorization | Contemporaneous | PASS |
| UncPreMgr | Matches | Same formula, Mgr Pres | Same engine | Same winsorization | Contemporaneous | PASS |
| Lagged_DV | "CCCL_lag" in code, "Lagged_DV" in regression | "CCCL_lag = 1 if firm received CCCL in cal quarter Q-1" — matches builder lines 274, 277 (`q_prev = _prev_cal_qtr(q)`) | CCCL input + CIK-gvkey map | No (binary) | Lag (Q-1) | PASS |
| lnAssets | Matches BASE_CONTROLS | "ln(atq), atq > 0" — matches `_compustat_engine.py` line 943: `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` | CompustatEngine: atq | 1%/99% per-fyearq — lnAssets is in COMPUSTAT_CONTROL_COLUMNS list (line 117) which gets winsorized | Contemporaneous | PASS |
| TobinsQ | Matches | "(cshoq*prccq + debt_book) / atq, where debt_book = dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0) (NaN if both missing)" — matches engine lines 987-996 exactly | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq | 1%/99% per-fyearq | Contemporaneous | PASS |
| ROA | Matches | "iby_annual (Q4) / avg(atq_t, atq_{t-1})" — matches engine lines 960-969 | CompustatEngine: iby, atq | 1%/99% per-fyearq | Contemporaneous | PASS |
| Leverage | Matches | "(dlcq + dlttq) / atq, missing debt = 0" — matches engine line 948: fillna(0) | CompustatEngine: dlcq, dlttq, atq | 1%/99% per-fyearq | Contemporaneous | PASS |
| Capex | Matches | "capxy_annual (Q4) / atq_lag" — matches engine lines 999-1005 | CompustatEngine: capxy, atq | 1%/99% per-fyearq | Contemporaneous | PASS |
| CashRatio | Matches | "cheq / atq" — matches engine line 986 | CompustatEngine: cheq, atq | 1%/99% per-fyearq | Contemporaneous | PASS |
| DivDummy | Matches | "1 if dvy_annual (Q4) > 0, else 0" — matches engine lines 1009-1012 | CompustatEngine: dvy | No (binary) — doc says "No (binary)" — PASS | Contemporaneous | PASS |
| sCFO | Matches | "Rolling 5-yr std (min 3 yrs) of oancfy/atq_{t-1} per gvkey" — matches `_compute_ocf_volatility()` lines 308-357 | CompustatEngine: oancfy, atq | 1%/99% per-fyearq (listed in COMPUSTAT_CONTROL_COLUMNS) | Rolling window | PASS |
| SalesGrowth | Matches | "(saley_t - saley_{t-1}) / abs(saley_{t-1}), Q4 annual" — matches `_compute_biddle_residual` docstring line 484 and implementation | CompustatEngine: saley (saleq fallback) — matches M-1 note in Biddle docstring | 1%/99% per-fyearq (Biddle pipeline) — verified at engine line 666 | Contemporaneous | PASS |
| RDSales | Matches | "xrdq / atq, missing xrdq = 0" — matches engine line 972: `comp["xrdq"].fillna(0) / comp["atq"]` | CompustatEngine: xrdq, atq | 1%/99% per-fyearq | Contemporaneous | PASS |
| CashFlowAt | Matches | "oancfy / avg(atq_t, atq_{t-1}), Q4 annual" — matches Biddle docstring M-2 and implementation | CompustatEngine: oancfy, atq | 1%/99% per-fyearq (Biddle pipeline) | Contemporaneous | PASS |
| DailyVola | Matches | "std(daily_ret) * sqrt(252) * 100 over [prev_call+5d, call-5d], min 10 days" — matches `volatility.py` lines 6-9 exactly | CRSPEngine: daily stock returns | No — doc says "Not in Compustat winsorization; bounded by construction." DailyVola is not in any winsorize call. PASS | Inter-call window | PASS |
| gvkey | FE identifier | -- | Manifest | -- | -- | PASS |
| ff12_code | Fama-French 12 | -- | Manifest | -- | -- | PASS |
| cal_yr | FE time (cols 1-4) | "start_date.dt.year" — panel_utils.py line 215 | Derived | -- | -- | PASS |
| cal_yr_qtr | FE time (cols 5-6) | "year*10 + quarter from start_date" — panel_utils.py line 217 | Derived | -- | -- | PASS |

All 22 variable dictionary rows verified. **Phase 6 Score**: 22/22.

---

## PHASE 7: FACTUAL ACCURACY — SECTIONS F, G, H

**F-CHECK: Data Pipeline**

F1. Dependency Chain — 7 steps documented:
- Step 1 (Raw inputs): manifest, CCCL file, CCM, Compustat, Stage 2, CRSP. All inputs verified in builder code lines 90-102 (CIK map), lines 133-145 (CCCL load), builder imports. **PASS**
- Step 2 (Engine loading): LinguisticEngine (linguistic IVs), CompustatEngine (controls), CRSPEngine (DailyVola). Builder imports at lines 51-69. **PASS**
- Step 3 (Panel builder): merge sequence (file_name, left join), fyearq via merge_asof, CCCL DV creation, sample assignment. All verified in builder main() lines 327-337. **PASS**
- Step 4 (Runner loading): panel parquet → `build_cal_yr_qtr_index()` → main sample filter. Runner lines 158-185. **PASS**
- Step 5 (Sample filtering): Lagged_DV assignment → inf→NaN → DV filter → complete-case → min 5 calls. Runner lines 200-228. **PASS**
- Step 6 (Regression): PanelOLS, 6 specs, firm-clustered SEs. **PASS**
- Step 7 (Table generation): runner writes its own LaTeX table; also entry in generate_all_tables.py. **PASS**

F2. Data Engines — 5 engines:
- LinguisticEngine: verified via builder imports and `_linguistic_engine.get_engine()`. **PASS**
- CompustatEngine: verified via SizeBuilder, LeverageBuilder, etc. **PASS**
- CRSPEngine: verified via VolatilityBuilder → `_crsp_engine.get_engine()`. **PASS**
- Direct load: CIK-gvkey from CCM/Compustat. Builder `_build_cik_gvkey_map()` lines 83-109. **PASS**
- ManifestFieldsBuilder: builder import line 68, `ManifestFieldsBuilder`. **PASS**

F3. Merge Operations — 3 merges:
- manifest ← each builder output on file_name, left: builder lines 200-216. **PASS**
- panel ← CompustatEngine fyearq via merge_asof: `attach_fyearq()` called at builder line 330. **PASS**
- CCCL letters ← CIK-gvkey map on cik_int, inner: `cccl.merge(cik_gvkey_map, on="cik_int", how="inner")` at builder line 142. **PASS**

**G-CHECK: Outputs**

G1. Stage 3 Outputs — builder writes:
- `h18_cccl_received_panel.parquet` (line 343) — doc lists this. **PASS**
- `summary_stats.csv` (line 348) — doc lists this. **PASS**
- `run_manifest.json` (line 352-356) — doc lists this. **PASS**
- No `report_step3_h18.md` written by builder (creation prompt template mentions this but it's not in the code). Doc correctly omits it. **PASS**

G2. Stage 4 Outputs — runner writes:
- `h18_cccl_received_table.tex` (runner line 465): `tex_path = out_dir / "h18_cccl_received_table.tex"`. Doc lists this. **PASS**
- `model_diagnostics.csv` (runner line 500). Doc lists this. **PASS**
- `summary_stats.csv` and `summary_stats.tex` (runner lines 549-555). Doc lists both. **PASS**
- `sample_attrition.csv` and `sample_attrition.tex` (runner line 586). Doc lists both. **PASS**
- `regression_results_col1.txt` through `col6.txt` (runner lines 485-496). Doc lists all 6. **PASS**
- `run_manifest.json` (runner lines 589-594). Doc lists this. **PASS**
- Doc says "Verified against: `outputs/econometric/h18_cccl_received/2026-03-27_095021/` (13 files)" — count verified: listing that directory shows exactly 13 files. **PASS** for count. But this timestamp is now stale — generate_all_tables.py points to `2026-03-31_151907`.

**FAIL on G2 directory timestamp**: The "Verified against" note cites the old directory. This is the same stale timestamp cited in Section I.

**H-CHECK: Outlier/Missing Treatment**

H1. Winsorization:
- Compustat controls 1%/99% per fyearq at CompustatEngine level. Doc references "_compustat_engine.py line 1134" for this. **FAIL**: `_compute_and_winsorize` is defined at line 936, not 1134. Line 1134 is inside the repurchase-variable computation, unrelated to winsorization logic.
- Doc says missing debt = 0 at "CompustatEngine line 943" — actual: line 948 (Leverage fillna). Line 943 is the lnAssets computation.
- Doc says missing xrdq = 0 at "CompustatEngine line 967" — actual: line 972.
- Linguistic IVs 0%/99% per-year upper-only at "_linguistic_engine.py line 255" — **PASS**, verified at line 255.

H2. Missing Data Policy:
- Complete-case deletion: runner lines 219-220. Doc says "runner lines 219-220". **PASS**
- Inf/-Inf → NaN: runner line 211. Doc says "runner line 211". **PASS**

H3. Transformations:
- lnAssets = ln(atq). **PASS**
- DailyVola = std * sqrt(252) * 100. **PASS**
- No centering/z-score on IVs. **PASS**

**Phase 7 Score**: 7/9 (2 failures: stale G2 directory, wrong CompustatEngine line for `_compute_and_winsorize`)

---

## PHASE 8: FACTUAL ACCURACY — SECTION I (Table Generator Entry)

Read `outputs/generate_all_tables.py`. H18 entry is at lines 330-342:

```python
    # ── H18 ──
    {
        "id": "H18",
        "dir": "h18_cccl_received/2026-03-31_151907",
        "caption": "H18: Speech Uncertainty and SEC Comment Letters",
        "label": "tab:h18",
        "cols": 6,
        "dvs": [
            (r"CCCL", 6),
        ],
        "tail": "one",
        "hyp_dir": ">",
    },
```

**Field-by-field comparison**:

| Field | Doc Claims | Actual Code | Status |
|-------|-----------|-------------|--------|
| `"id"` | `"H18"` | `"H18"` | PASS |
| `"dir"` | `"h18_cccl_received/2026-03-27_095021"` | `"h18_cccl_received/2026-03-31_151907"` | **FAIL** |
| `"caption"` | `"H18: Speech Uncertainty and SEC Comment Letters"` | `"H18: Speech Uncertainty and SEC Comment Letters"` | PASS |
| `"label"` | `"tab:h18"` | `"tab:h18"` | PASS |
| `"cols"` | `6` | `6` | PASS |
| `"dvs"` | `[(r"CCCL", 6)]` | `[(r"CCCL", 6)]` | PASS |
| `"tail"` | `"one"` | `"one"` | PASS |
| `"hyp_dir"` | `">"` | `">"` | PASS |
| Line numbers | "lines 405-417" | Lines 330-342 | **FAIL** |

**FAIL on dir**: The provenance doc documents a stale directory (`2026-03-27_095021`). The current generate_all_tables.py entry points to `2026-03-31_151907`. This means when generate_all_tables.py is executed, it reads from the newer directory, not the one documented.

**FAIL on line numbers**: The doc says "lines 405-417" but the H18 entry is at lines 330-342. The discrepancy is approximately 75 lines — consistent with the H18 entry having been moved earlier in the file (or other suites having been inserted/removed after the provenance doc was written).

**Phase 8 Score**: 3/5.

---

## PHASE 9: FACTUAL ACCURACY — SECTION K (Model-Family Addendum)

Model family identified in Section A: LPM via PanelOLS.

**K1. PanelOLS Specifics (LPM)** — filled. Verify each claim:

- "Industry FE: absorbed via `other_effects=df_panel["ff12_code"]`, `entity_effects=False`, `time_effects=True`" — runner lines 270-278: `entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"]`. **PASS**
- "Firm FE: absorbed via `EntityEffects` in PanelOLS formula, `TimeEffects`" — runner lines 282-283: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`. **PASS**
- "`drop_absorbed=True` in all specifications" — runner line 276 (industry): `drop_absorbed=True`; runner line 283 (firm): `drop_absorbed=True`. **PASS**
- "Time effects absorbed via `time_effects=True` (industry specs) or `TimeEffects` in formula (firm specs)" — **PASS**
- "Panel index time dimension is `cal_yr` (cols 1-4) or `cal_yr_qtr` (cols 5-6), determined at runner line 249" — runner line 249: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`. **PASS**
- "`check_rank=False` set for industry FE specs (runner line 278)" — Actual: `check_rank=False` is at **line 277**, not 278. Line 278 is `check_rank=False,` but within the PanelOLS constructor args, the closing `)` of that argument block is at line 278. The actual `check_rank=False` parameter appears at runner line 277. **FAIL** — minor line number error.
- "Adj R-squared computed manually as `1 - (1 - R2) * (nobs - 1) / df_resid` (runner line 300)" — runner line 300: `"adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`. **PASS**

**K2. Cox PH**: N/A — correct.
**K3. Logit/Probit/LPM Specifics** — also filled:
- Link function: Identity (LPM — linear). **PASS**
- Binary outcome construction: matches builder implementation. **PASS**
- Separation handling: "Not applicable (LPM does not suffer from quasi-complete separation)". **PASS**
- Marginal effects: "Coefficients are directly interpretable as marginal effects". **PASS**
- R-squared type: "Standard OLS R-squared". **PASS**

**K4, K5, K6**: N/A — correct.

**Phase 9 Score**: 5/6 (1 failure: check_rank line number cited as 278, actual is 277).

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | Phase 6 verified all 22 variables. All have formula and source engine. |
| 2 | The model equation matches what the code actually estimates | YES | Phase 3 B1-CHECK: equation verified against KEY_IVS, controls, FE structure. |
| 3 | The specification register accounts for every model column | YES | Phase 4: all 6 MODEL_SPECS mapped to 6 table rows. |
| 4 | The attrition cascade has row counts for each filter step | YES | Phase 5: 4 steps with N values. Step 3 is informational (not a filter), documented as such. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner: `p_one = p_two / 2 if beta > 0`. generate_all_tables.py: `"tail": "one", "hyp_dir": ">"`. Consistent. |
| 6 | The FE specification matches between docstring, code, and this document | YES | B5 verified: industry FE via other_effects, firm FE via EntityEffects, cal_yr / cal_yr_qtr. Consistent across docstring, code, doc. |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | F3 table: 3 merges (file_name/left, merge_asof backward, cik_int/inner). All verified. |
| 8 | The output file list matches what the runner actually writes | YES | G2: all 13 files verified. The "Verified against" directory is stale (old timestamp), but the file list itself is accurate. |
| 9 | The model-family addendum is filled for the correct family only | NO | K1 (PanelOLS) is filled — correct. K3 (LPM specifics) is also filled — acceptable since the suite IS an LPM. However, filling both K1 and K3 is unconventional given that K1 IS the LPM section for PanelOLS. Quality gate is borderline met; the duplication is informative rather than misleading. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | No [UNVERIFIED] tags in the document. All claims are stated as verified. |

**Phase 10 Score**: 9/10 (QG9 borderline — both K1 and K3 filled; K3 is supplementary and correct).

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

1. **DVs in B2 vs C**: B2 lists CCCL. Section C shows CCCL for all 6 cols. **PASS**

2. **DVs in C vs I**: Section C shows CCCL. Section I `"dvs": [(r"CCCL", 6)]`. **PASS**

3. **Controls in B4 vs E**: B4 lists 9 base + 4 extended = 13 controls. Variable dictionary has entries for all 13 (lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, DivDummy, sCFO, Lagged_DV, SalesGrowth, RDSales, CashFlowAt, DailyVola). **PASS**

4. **Column count in A vs C**: A says 6 columns. C has 6 rows. **PASS**

5. **Column count in A vs I**: A says 6 columns. I says `"cols": 6`. **PASS**

6. **Tail direction in A vs B7 vs I**:
   - A: "One-tailed (beta > 0)"
   - B7: "one-tailed (beta > 0)"
   - I: `"tail": "one", "hyp_dir": ">"`
   - **PASS**

7. **FE in B5 vs C vs K**:
   - B5: Industry (ff12_code) + Firm (gvkey) + Cal Yr + Cal Yr-Qtr
   - C: odd cols = industry, even = firm, cols 1-4 = Cal Year, cols 5-6 = Cal Year-Quarter
   - K1: other_effects=ff12_code for industry; EntityEffects for firm; cal_yr or cal_yr_qtr as time index
   - **PASS**

8. **Panel index in A vs K**:
   - A: "(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6"
   - K1: "Panel index time dimension is `cal_yr` (cols 1-4) or `cal_yr_qtr` (cols 5-6), determined at runner line 249"
   - **PASS**

**Phase 11 Score**: 8/8.

---

## CORRECTIONS REQUIRED

The following edits are needed to bring the provenance doc to PASS status:

**Correction 1 — Section I: Update `dir` field**
- Section: I. generate_all_tables.py Entry
- Current text: `"dir": "h18_cccl_received/2026-03-27_095021",`
- Should be: `"dir": "h18_cccl_received/2026-03-31_151907",`
- Code reference: `outputs/generate_all_tables.py` line 333

**Correction 2 — Section I: Update line number reference**
- Section: I. generate_all_tables.py Entry
- Current text: "From `outputs/generate_all_tables.py` (lines 405-417):"
- Should be: "From `outputs/generate_all_tables.py` (lines 330-342):"
- Code reference: H18 entry begins at line 330 (`# ── H18 ──`) and ends at line 342 (`},`)

**Correction 3 — Section H2: Correct CompustatEngine line for `_compute_and_winsorize`**
- Section: H. Outlier/Missing Data Treatment, H2. Missing Data Policy
- Current text: "CompustatEngine line 1134"
- Should be: "CompustatEngine line 936"
- Code reference: `_compustat_engine.py`: `def _compute_and_winsorize(` at line 936. Line 1134 is inside repurchase-variable computation unrelated to winsorization.

**Correction 4 — Section H2: Correct CompustatEngine line for missing xrdq = 0**
- Section: H2. Missing Data Policy
- Current text: "Missing R&D (xrdq) treated as zero per standard convention (CompustatEngine line 967)"
- Should be: "Missing R&D (xrdq) treated as zero per standard convention (CompustatEngine line 972)"
- Code reference: `_compustat_engine.py` line 972: `comp["RDSales"] = comp["xrdq"].fillna(0) / comp["atq"]`

**Correction 5 — Section H2: Correct CompustatEngine line for missing debt = 0**
- Section: H2. Missing Data Policy
- Current text: "Missing debt (dlcq, dlttq) treated as zero for Leverage (CompustatEngine line 943)"
- Should be: "Missing debt (dlcq, dlttq) treated as zero for Leverage (CompustatEngine line 948)"
- Code reference: `_compustat_engine.py` line 948: `comp["Leverage"] = (comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]`; line 943 is the lnAssets computation.

**Correction 6 — Section B7: Replace simplified p-value code snippet with accurate version**
- Section: B7. Hypothesis Test
- Current text (simplified pseudo-code):
  ```python
  if beta > 0:
      p_one = p_two / 2
  else:
      p_one = 1 - p_two / 2
  ```
- Should be (exact code from runner lines 310-313):
  ```python
  if not np.isnan(p_two) and not np.isnan(beta):
      p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
  else:
      p_one = np.nan
  ```
- Code reference: runner lines 310-313

**Correction 7 — Section K1: Correct `check_rank=False` line number**
- Section: K1. PanelOLS Specifics
- Current text: "`check_rank=False` set for industry FE specs (runner line 278)"
- Should be: "`check_rank=False` set for industry FE specs (runner line 277)"
- Code reference: runner line 277: `check_rank=False,` (inside PanelOLS constructor; line 278 closes the argument/parenthesis)

**Correction 8 — Section L: Add known issue for runner docstring vs builder discrepancy**
- Section: L. Known Issues and Notes
- Add new item (e.g., item 7):
  > **7. Runner docstring contradicts builder implementation**: Runner docstring (line 10-11) describes the DV window as "received SEC comment letter **between this call and the next call** / Window: (start_date_current, start_date_next_call]." This implies a call-to-call time window. However, `create_cccl_dvs()` in the panel builder implements a **next calendar quarter (Q+1)** lookup: `cccl_fwd[i] = 1.0 if (g, q_next) in cccl_set else 0.0` where `q_next = _next_cal_qtr(q)`. The two constructions differ whenever the next calendar quarter does not contain the next earnings call, or when the next earnings call falls in the same quarter. The builder's calendar-quarter implementation is the operative code. The runner docstring is incorrect and should be updated.

---

## APPENDIX: LINE NUMBER VERIFICATION TABLE

Critical line references cited in the provenance document, verified against actual code:

| Doc Section | Doc Claims Line | File | Actual Line | Content | Status |
|-------------|----------------|------|-------------|---------|--------|
| B2 | "lines 231-287" for `create_cccl_dvs` | `build_h18_cccl_received_panel.py` | 231-287 | Function `create_cccl_dvs(...)` | PASS |
| B4 / F1 | "runner line 200" for Lagged_DV | `run_h18_cccl_received.py` | 200 | `panel["Lagged_DV"] = panel["CCCL_lag"]` | PASS |
| B4 | "runner line 202" for required list | `run_h18_cccl_received.py` | 202 | `required = [dv] + KEY_IVS + controls + [...]` | PASS |
| C | "runner lines 91-99" for MODEL_SPECS | `run_h18_cccl_received.py` | 91-99 | MODEL_SPECS list | PASS |
| D2 | "Runner line 183" for FF12 filter | `run_h18_cccl_received.py` | 182 | `main = panel[~panel["ff12_code"].isin([8, 11])]` | MINOR (line 182 has the filter; 183 is a print) |
| D2 | "Runner lines 215-228" for complete-case/min-calls | `run_h18_cccl_received.py` | 215-228 | DV filter, complete_mask, min calls | PASS |
| B5 / K1 | "runner lines 270-278" for industry FE | `run_h18_cccl_received.py` | 269-278 | PanelOLS(entity_effects=False,...) | PASS (minor: 269 opens try, 270 has PanelOLS) |
| B6 | "runner lines 279, 284" for cov_type | `run_h18_cccl_received.py` | 279, 284 | `.fit(cov_type="clustered", cluster_entity=True)` | PASS |
| B7 | "runner lines 310-313" for p-value | `run_h18_cccl_received.py` | 310-313 | NaN guard + ternary p_one | PASS (lines correct, snippet inaccurate) |
| B7 | "runner lines 326-334" for sig stars | `run_h18_cccl_received.py` | 325-334 | `def _sig_stars(p: float)` through return "" | MINOR (325 is function def, 326 starts body) |
| G1 | "30 columns, 112,968 rows" for panel parquet | runtime claim | Cannot verify from code alone | UNVERIFIABLE from code alone |
| G3 | "runner SUMMARY_STATS_VARS, lines 109-127" | `run_h18_cccl_received.py` | 109-127 | SUMMARY_STATS_VARS list | PASS |
| H1 | "_linguistic_engine.py line 255" for winsorize | `_linguistic_engine.py` | 255 | `combined = winsorize_by_year(...)` | PASS |
| H2 | "CompustatEngine line 1134" for `_compute_and_winsorize` | `_compustat_engine.py` | 936 | `def _compute_and_winsorize(` | **FAIL** |
| H2 | "CompustatEngine line 967" for xrdq fillna(0) | `_compustat_engine.py` | 972 | `comp["RDSales"] = comp["xrdq"].fillna(0) / comp["atq"]` | **FAIL** |
| H2 | "CompustatEngine line 943" for Leverage fillna(0) | `_compustat_engine.py` | 948 | `comp["Leverage"] = (comp["dlcq"].fillna(0) + ...)` | **FAIL** |
| I | "lines 405-417" for H18 entry | `outputs/generate_all_tables.py` | 330-342 | H18 dict entry | **FAIL** |
| K1 | "runner line 249" for time_col assignment | `run_h18_cccl_received.py` | 249 | `time_col = "cal_yr_qtr" if ...` | PASS |
| K1 | "runner line 278" for check_rank=False | `run_h18_cccl_received.py` | 277 | `check_rank=False,` | **FAIL** |
| K1 | "runner line 300" for adj_r2 formula | `run_h18_cccl_received.py` | 300 | `"adj_r2": 1 - (1 - model.rsquared) * ...` | PASS |
| B5 | "panel_utils.py lines 195-218" for `build_cal_yr_qtr_index` | `panel_utils.py` | 195-218 | `def build_cal_yr_qtr_index(panel)` through return | PASS |
