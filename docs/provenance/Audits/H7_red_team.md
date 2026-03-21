# H7 Post-Call Illiquidity -- Second-Layer Red-Team Audit

**Generated:** 2026-03-21
**Auditor role:** Hostile-but-fair replication auditor (second layer)
**Audit target:** `docs/provenance/H7.md` (first-layer audit, dated 2026-03-18)
**Suite ID:** H7
**Verdict:** CONDITIONAL PASS -- the first-layer audit is thorough and accurate on all verified claims, but contains one material omission (summary statistics computed on wrong sample) and the critical winsorization gap it flagged remains open.

---

## A. Scope & Objectives

This second-layer audit verifies the accuracy, completeness, and intellectual honesty of the first-layer provenance document (`docs/provenance/H7.md`). The audit independently inspects the runner (`src/f1d/econometric/run_h7_illiquidity.py`), panel builder (`src/f1d/variables/build_h7_illiquidity_panel.py`), DV builder (`src/f1d/shared/variables/amihud_change.py`), selection supplement (`src/f1d/econometric/ceo_presence_probit.py`), and supporting infrastructure to verify all claims made in the first-layer document.

---

## B. First-Layer Audit Quality Assessment

**Overall grade: HIGH.** The first-layer audit is unusually detailed and well-structured. It includes:
- A 10-step DV construction provenance chain with line-number references
- Full Compustat control construction provenance for all 8 base controls
- 26 independent verification items (V1-V26) with code references
- Transparent disclosure of the critical winsorization gap (Section 12.1)
- Integration of the CEO Presence Probit supplement into the identification discussion

**Weaknesses identified:**
1. One material omission found (Section G below)
2. The document references itself in Section 13 (`docs/provenance/H7_red_team.md`) as though the red-team audit already existed at the time of writing -- this is a forward reference that could confuse readers
3. No actual sample sizes are provided (deferred to "production run")

---

## C. Verification of Runner Code Claims

| Claim (from H7.md) | Code reference | Independently verified? | Notes |
|---------------------|----------------|------------------------|-------|
| 4 IVs enter simultaneously (V6) | `run_h7_illiquidity.py` L66-70 | YES | `KEY_IVS` list contains exactly 4 variables |
| Base controls = 8 (V7) | L73-82 | YES | 8 items in `BASE_CONTROLS` list |
| Extended = Base + 4 (V8) | L84-89 | YES | 4 additional items appended |
| 4 model specs: 1 DV x 2 FE x 2 controls (V16) | L91-96 | YES | `MODEL_SPECS` list with cols 1-4 |
| MIN_CALLS_PER_FIRM = 5 (V15) | L98 | YES | Exact match |
| Main sample: FF12 not in {8, 11} (V14) | L163 | YES | `~panel["ff12_code"].isin([8, 11])` |
| Inf replacement before complete-case (doc S5) | L178 | YES | `df.replace([np.inf, -np.inf], np.nan)` |
| DV non-null filter (doc S5) | L185 | YES | `df[df[dv].notna()]` |
| Complete-case filter (doc S5) | L188-189 | YES | `df[required].notna().all(axis=1)` |
| Min-calls filter (doc S5) | L192-194 | YES | `value_counts >= MIN_CALLS_PER_FIRM` |
| Industry FE via other_effects (V9) | L224-230 | YES | `other_effects=df_panel["ff12_code"]`, `time_effects=True` |
| Firm FE via EntityEffects formula (V10) | L232-235 | YES | `EntityEffects + TimeEffects` in formula string |
| Firm-clustered SEs (V12) | L230, L235 | YES | `cov_type="clustered", cluster_entity=True` |
| One-tailed p-value formula (V13) | L257-258 | YES | `p_two / 2 if beta > 0 else 1 - p_two / 2` |
| Min 100 obs guard | L210-212, L423-424 | YES | Both locations verified |
| LaTeX note claims winsorization (V21) | L339 | YES | Note says "Variables winsorized at 1%/99% by year at engine level" -- confirmed FALSE for delta_amihud and pre_call_amihud |

**Verdict: All runner claims verified. No false claims found.**

---

## D. Verification of Panel Builder Claims

| Claim | Code reference | Verified? | Notes |
|-------|----------------|-----------|-------|
| 17 builders merged on file_name (doc S5.1) | `build_h7_illiquidity_panel.py` L85-115 | YES | Count matches: 1 manifest + 4 IVs + 1 DV + 7 base controls + 4 extended controls = 17 |
| Left joins with zero-delta enforcement | L137-142 | YES | `if delta != 0: raise ValueError(...)` |
| assign_industry_sample on ff12_code | L145 | YES | |
| attach_fyearq via merge_asof | L149 | YES | |
| fyearq_int = pd.to_numeric(fyearq) | L150 | YES | |

**Minor finding:** The panel builder's docstring at L18 says `DV: amihud_illiq (contemporaneous Amihud illiquidity measure)`. The first-layer audit correctly flags this in Section 12.5 as a documentation error -- the actual DV is `delta_amihud`.

**Verdict: All panel builder claims verified.**

---

## E. Verification of DV Construction Claims (AmihudChangeBuilder)

| Claim | Code reference | Verified? | Notes |
|-------|----------------|-----------|-------|
| daily_illiq = |RET| / (VOL * |PRC|) * 1e6 (V2) | `amihud_change.py` L304-306 | YES | `merged["RET"].abs() / dollar_vol_masked * 1e6` where `dollar_volume = VOL * PRC.abs()` |
| Zero dollar volume -> NaN (doc S6.1 step 3) | L305 | YES | `replace(0, np.nan)` |
| Inf -> NaN (doc S6.1 step 3) | L308 | YES | `replace([np.inf, -np.inf], np.nan)` |
| Reference date = last trading day on or before call (V3) | L314-318 | YES | `is_on_or_before_call`, groupby last |
| Call-day exclusion: days_from_ref == 0 excluded (V4) | L327-328 | YES | `pre_mask = days_from_ref < 0`, `post_mask = days_from_ref > 0` (strict inequalities exclude 0) |
| Window size w=3 (doc D8) | L49 (`config.get("window_days", 3)`) | YES | Default 3, configurable |
| Min valid days: 2 per window (V5) | L269-270 | YES | `min_pre = max(1, 3-1) = 2`, `min_post = max(1, 3-1) = 2` |
| delta_amihud = post - pre (doc S6.1 step 9) | L360 | YES | `post_call_amihud - pre_call_amihud` |
| Calls failing min-days get NaN for both DV and control | L367-368 | YES | Both `delta_amihud` and `pre_call_amihud` set to NaN |
| Uses get_raw_daily_data (V25) | L75 | YES | `engine.get_raw_daily_data(root_path, years=list(years))` |
| NOT winsorized (V17, V18) | Full file search | YES | Zero references to any winsorization function in amihud_change.py |

**Verdict: All DV construction claims verified. The 10-step provenance chain in the first-layer audit is accurate.**

---

## F. Verification of Control Variable Claims

| Variable | Audit claim | Verified? | Notes |
|----------|-------------|-----------|-------|
| Size = ln(atq) | `_compustat_engine.py` L1036 | YES | `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` |
| BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq | L1041 | YES | Exact formula match |
| TobinsQ = (mktcap + debt_book) / atq | L1069-1079 | YES | With negative-debt clipping and NaN handling |
| ROA = iby_annual / avg_assets | L1052-1062 | YES | Q4 extraction via `_compute_annual_q4_variable` |
| CapexAt = capxy_annual / atq_annual_lag1 | L1081-1087 | YES | Q4 annual, lagged denominator |
| Compustat controls winsorized 1%/99% by fyearq (V19) | L1191-1215 | YES | Loop over `winsorize_cols`, using `_winsorize_by_year` |
| DividendPayer excluded from winsorization | L1199-1207 | YES | In `skip_winsorize` set |
| StockPrice NOT winsorized | `stock_price.py` full file | YES | Uses `get_raw_daily_data()`, no winsorization calls |
| Turnover NOT winsorized | `turnover.py` full file | YES | Uses `get_raw_daily_data()`, no winsorization calls |
| pre_call_amihud NOT winsorized | amihud_change.py | YES | Same pipeline as delta_amihud |

**Verdict: All control variable claims verified.**

---

## G. Material Omission Found: Summary Statistics Computed on Wrong Sample

**Severity: MAJOR**
**Code:** `run_h7_illiquidity.py` L408-413

The first-layer audit does not flag that `make_summary_stats_table` is called on the Main-filtered `panel` (L408, where `df=panel`) BEFORE the complete-case filter is applied (which happens inside `prepare_regression_data` at L416-419). This means:

1. The summary statistics table includes observations with missing IVs, missing controls, and missing DV values.
2. The summary statistics do not represent the actual regression sample.
3. Firms excluded by the min-calls filter (MIN_CALLS_PER_FIRM=5) are included in the summary statistics.

This is a **standard empirical-methods error** -- summary statistics should describe the regression sample, not the pre-filter sample. The N in the summary statistics table will be larger than the N in the regression table, which is confusing and potentially misleading to reviewers.

The first-layer audit documents the summary statistics output (Section 8.2, line "summary_stats.csv") but does not flag this sample mismatch.

**Recommended fix:** Move `make_summary_stats_table` inside the regression loop (after `prepare_regression_data`) or compute it on the col-1 regression sample (the most restrictive base-controls sample).

---

## H. Verification of CEO Presence Probit Claims

| Claim | Code reference | Verified? | Notes |
|-------|----------------|-----------|-------|
| CEO_present_QA = CEO_QA_Uncertainty_pct.notna() (V22) | `ceo_presence_probit.py` L103 | YES | `.notna().astype(int)` |
| Controls: Size, BookLev, ROA, TobinsQ, Volatility (V23) | L46 | YES | `PROBIT_CONTROLS` list |
| + C(year) in formula (V23) | L117 | YES | `" + C(year)"` appended |
| Main sample only (V24) | L96-98 | YES | `panel["sample"] == "Main"` |
| Newton method, maxiter=200 | L122 | YES | `method="newton"`, `maxiter=200` |
| Marginal effects computed | L132-143 | YES | `model.get_margeff()` |

**Verdict: All probit claims verified.**

---

## I. Attrition Table Assessment

The first-layer audit (Section 9) correctly documents the attrition structure and stages. However:

1. **No actual numbers provided.** The audit defers to "production run" for exact counts. This is acceptable for a living document but weakens the audit's value as a standalone reference.
2. **Attrition granularity is coarse.** The generated table (L434-439) jumps from "delta_amihud non-null" to "Complete-case + min-calls (col 1)" without separating:
   - Complete-case before min-calls
   - Min-calls filter separately
   - Breakdown of missingness by variable (which IV/control drives the most attrition)

   The first-layer audit notes CEO absence as the "largest single source of attrition" (~29.6%) but this is not verifiable without actual numbers.

**Severity: MINOR** -- the structure is correct; the granularity could be improved.

---

## J. Identification & Inference Assessment

The first-layer audit's Section 11 is well-reasoned and appropriately skeptical. The identification threats table covers the key concerns (reverse causality, omitted variables, multicollinearity, CEO selection, functional form). The discussion of pre_call_amihud as a lagged-DV control (Section 11.3) is appropriate.

**No issues found with the identification discussion.**

---

## K. Known Limitations Assessment

The first-layer audit identifies 7 limitations (Sections 12.1-12.7). Independent assessment:

| # | Limitation | Correctly identified? | Severity assessment correct? | Notes |
|---|-----------|----------------------|------------------------------|-------|
| 12.1 | delta_amihud/pre_call_amihud not winsorized | YES | YES (CRITICAL) | The audit correctly identifies the LaTeX note as misleading and the H14 comparability failure |
| 12.2 | No log-transform or alternative DV | YES | Reasonable (OPEN) | Standard practice concern |
| 12.3 | No VIF/multicollinearity diagnostics | YES | Reasonable (OPEN) | 4 correlated IVs is a real concern |
| 12.4 | Panel index non-uniqueness | YES | Correctly downgraded to disclosure | PanelOLS handles this correctly |
| 12.5 | Docstring error (amihud_illiq vs delta_amihud) | YES | Correctly rated MINOR | Documentation only |
| 12.6 | CRSP VOL units assumption | YES | Correctly rated MINOR | Sample likely post-2001 |
| 12.7 | No Heckman correction | YES | Appropriately flagged | Probit disclosure is the chosen approach |

**Verdict: Limitations section is thorough and correctly prioritized.**

---

## L. Cross-Suite Consistency Check

The first-layer audit explicitly compares H7 to H14 (bid-ask spread) in several places:
- D2: "Mirrors H14 pattern"
- Section 12.1: H14 winsorizes its event-window DV but H7 does not
- D3: pre_call_amihud analogous to H14's PreCallSpread

This cross-reference is valuable. The asymmetry in winsorization treatment between H7 and H14 is a genuine concern that the first-layer audit correctly elevates to CRITICAL status.

**Additional cross-suite concern not flagged:** The first-layer audit does not explicitly note whether the 4 IVs in H7 use the same winsorization (0%/99% upper-only per year) as in all other suites. It documents this in Section 6.2 but does not verify consistency across suites. This is a minor gap.

---

## M. LaTeX Table Audit

The first-layer audit correctly identifies the misleading winsorization note at L339. Additional LaTeX table issues found:

1. **No issue with coefficient formatting.** The `fmt_coef` function at L283 uses 4 decimal places, which is reasonable for the Amihud scale.
2. **R-squared formatting handles near-zero values.** L289-291 uses scientific notation for R-squared < 0.001, which is appropriate given that within-R-squared for event-window DVs can be extremely small.
3. **Table note is otherwise accurate.** The one-tailed direction, clustering, sample description, DV definition, and FE descriptions are all correct.

---

## N. Reproducibility Assessment

The first-layer audit's Section 2 (Reproducibility Snapshot) is correct:
- No random seed is needed (no randomization in pipeline)
- Deterministic given identical inputs
- All input paths, output paths, and timestamps are documented
- The `generate_manifest` call at L441-447 creates a machine-readable reproducibility record

**One concern:** The panel builder and runner each resolve paths via `get_latest_output_dir`, which selects the most recent timestamped directory. This means re-running the panel builder creates a new directory, and the runner will pick up the new panel automatically. While this is convenient, it means the exact panel used by the runner is not locked -- it depends on execution order. The `run_manifest.json` captures the actual path used, so this is a workflow concern, not a reproducibility failure.

---

## O. Second-Layer Findings Summary

| ID | Severity | Finding | Disposition |
|----|----------|---------|-------------|
| RT2-1 | MAJOR | Summary statistics computed on pre-filter Main sample, not regression sample (Section G) | NEW finding. Must be fixed before thesis submission. |
| RT2-2 | CONFIRMED-CRITICAL | delta_amihud and pre_call_amihud not winsorized (Section 12.1 of first-layer) | First-layer audit correctly identified. Remains OPEN. |
| RT2-3 | CONFIRMED-CRITICAL | LaTeX table note falsely claims winsorization | First-layer audit correctly identified. Remains OPEN. |
| RT2-4 | MINOR | Attrition table lacks intermediate-step granularity (Section I) | Would improve transparency but is not blocking. |
| RT2-5 | MINOR | No actual sample sizes anywhere in the audit | Deferred to production run; acceptable for living doc. |
| RT2-6 | COSMETIC | Section 13 forward-references this red-team document before it existed | Confusing but not substantively wrong. |

---

## P. Overall Verdict

**CONDITIONAL PASS.**

The first-layer audit is thorough, accurate, and intellectually honest. All 26 verification items (V1-V26) were independently confirmed against the codebase. The DV construction provenance chain is detailed and correct. The identification of the winsorization gap as CRITICAL is appropriate and well-documented.

The one material omission (RT2-1: summary statistics on wrong sample) should be documented in the first-layer audit and fixed in the runner before thesis submission. The two CRITICAL items from the first layer (RT2-2, RT2-3) remain open and must also be resolved.

**Conditions for full PASS:**
1. Fix summary statistics to reflect the regression sample (RT2-1)
2. Resolve the winsorization gap: add `winsorize_pooled` for delta_amihud and pre_call_amihud in the panel builder (RT2-2)
3. Correct the LaTeX table note to exclude delta_amihud and pre_call_amihud from the winsorization claim (RT2-3)
