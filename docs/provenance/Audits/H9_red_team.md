# H9: Second-Layer Red-Team Audit — Audit of the Audit

**Audit target:** First-layer audit document `docs/provenance/H9.md`
**Suite entrypoint:** `src/f1d/econometric/run_h9_takeover_hazards.py`
**Panel builder:** `src/f1d/variables/build_h9_takeover_panel.py`
**Auditor context:** Fresh-context, adversarial review of both implementation and first-layer audit
**Date:** 2026-03-18

**Verification classification key:**
- **[VERIFIED FACT]** — confirmed by code inspection and/or data verification
- **[VERIFIED ERROR]** — confirmed factual error in the first-layer audit
- **[VERIFIED MISSED ISSUE]** — confirmed issue not identified in the first-layer audit
- **[VERIFIED FALSE POSITIVE]** — issue flagged in first-layer audit that is not actually a problem
- **[REFEREE JUDGMENT]** — substantive concern about inference or credibility, based on verified evidence
- **[UNVERIFIED CONCERN]** — suspected issue that cannot be fully confirmed from available artifacts

---

## A. Red-Team Bottom Line

The first-layer audit is a thorough, well-structured document that correctly identifies the most critical methodological issue (model-based SEs, neither robust nor clustered) and the major survival-specific concerns (no PH test, calendar-time scale). However, the audit suffers from a **critical temporal-consistency failure**: it mixes sample counts, HR row counts, and EPV diagnostics from **two different panel builds** (2026-03-12 with `Lev` column and 59.7% ClarityCEO coverage vs. 2026-03-18 with `BookLev` column and 0% ClarityCEO coverage) without clearly distinguishing which run produced which numbers. The canonical run (2026-03-18_160645) uses a panel with **zero ClarityCEO observations**, meaning the primary clarity construct is entirely absent from the reported results. The audit buries this critical finding in parenthetical notes within the dependency chain (steps 9-10) rather than elevating it to a top-level blocking issue.

Additionally, the audit contains an internal inconsistency in HR row counts (243 vs 162), an unflagged docstring/code mismatch (`Lev` vs `BookLev` in sparse controls description), and several missing issues related to the `BookLev` definition and the concordance index methodology.

**Overall audit quality: GOOD with critical factual errors requiring correction.**

---

## B. Scope and Objects Audited

| Object | Path | Audited by L1? | Re-audited by L2? |
|--------|------|----------------|-------------------|
| Econometric runner | `src/f1d/econometric/run_h9_takeover_hazards.py` | Yes | Yes |
| Panel builder | `src/f1d/variables/build_h9_takeover_panel.py` | Yes | Yes |
| TakeoverIndicatorBuilder | `src/f1d/shared/variables/takeover_indicator.py` | Yes | Yes |
| CompustatEngine (BookLev) | `src/f1d/shared/variables/_compustat_engine.py` | Partially | Yes |
| First-layer audit | `docs/provenance/H9.md` | N/A (target) | Yes |
| Canonical panel output | `outputs/variables/takeover/2026-03-18_160406/` | Claimed | Yes (verified 0% ClarityCEO) |
| Canonical econometric output | `outputs/econometric/takeover/2026-03-18_160645/` | Claimed | Yes (verified 162 HR rows, 24 diag rows) |
| Earlier panel output | `outputs/variables/takeover/2026-03-12_024947/` | Yes (numbers match) | Yes (verified 59.7% ClarityCEO) |
| Earlier econometric output | `outputs/econometric/takeover/2026-03-13_053120/` | Yes (numbers match) | Yes (verified 243 HR rows) |

---

## C. Audit-of-Audit Scorecard

| Criterion | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| Factual accuracy | 3 | Correct on most code-level claims; critical errors on row counts and run consistency |
| Completeness of issue identification | 4 | Identified most major issues; missed BookLev naming inconsistency and ClarityCEO upstream breakage severity |
| Severity calibration | 4 | Appropriate calibration of SE/clustering as Critical; appropriate downgrade of placebo tests for null-result suite |
| Internal consistency | 2 | HR row count contradicts itself (243 vs 162); E5 sample counts from different panel build than canonical run |
| Evidence quality | 3 | Many claims verified with code line references; but canonical run outputs contradict stated numbers |
| Actionability of recommendations | 4 | Concrete fix recommendations with effort estimates; CoxPHFitter migration path well-specified |
| Survival-analysis expertise | 4 | Correctly identifies counting-process format, Efron ties, cause-specific competing risks, EPV diagnostics |
| Audit-craft discipline | 2 | Mixes data from multiple runs; does not clearly state which run each number comes from |

---

## D. Claim Verification Matrix

| # | Claim (from L1 audit) | Location in L1 | Verified? | Evidence | Verdict |
|---|----------------------|----------------|-----------|----------|---------|
| D1 | Panel has 107,644 rows x 31 columns | B, line 115; E4 line 253 | **YES** | Both panels (2026-03-12, 2026-03-18) confirmed 107,644 x 31 | [VERIFIED FACT] |
| D2 | 2,410 unique firms, 663 event firms | E4 line 253 | **YES** | `df['gvkey'].nunique()` = 2,410; `groupby('gvkey')['Takeover'].max().sum()` = 663 | [VERIFIED FACT] |
| D3 | hazard_ratios.csv has 243 coefficient rows | B, line 125 | **NO** | Canonical run (2026-03-18_160645) has 162 rows. The 2026-03-13 run has 243. Audit mixes runs. | [VERIFIED ERROR] |
| D4 | model_diagnostics.csv has 24 rows | B, line 126 | **YES** | Both canonical and latest runs have 24 diagnostic rows | [VERIFIED FACT] |
| D5 | ClarityCEO coverage: 59.7% (64,217/107,644) | D, line 187; E2 line 215 | **STALE** | True for 2026-03-12 panel. **FALSE** for canonical panel (2026-03-18_160406): 0/107,644 = 0%. | [VERIFIED ERROR] — numbers from wrong run |
| D6 | Complete-case CEO: 51,627 intervals, 1,349 firms, 307 events | E5 line 261 | **STALE** | True for 2026-03-12 panel with `Lev`. Zero for canonical panel with `BookLev`. | [VERIFIED ERROR] — numbers from wrong run |
| D7 | Complete-case CEO_Res: 40,310 intervals, 1,318 firms, 275 events | E5 line 262 | **STALE** | True for 2026-03-12 panel. For canonical: 36,860 / 1,272 / 78 events. | [VERIFIED ERROR] — numbers from wrong run |
| D8 | Complete-case Mgr_Res: 54,981 intervals, 1,543 firms, 354 events | E5 line 263 | **STALE** | True for 2026-03-12 panel. For canonical: 50,628 / 1,488 / 101 events. | [VERIFIED ERROR] — numbers from wrong run |
| D9 | SEs are model-based (inverse Hessian), not robust, not clustered | A5, J1, K3, L-01 | **YES** | Code at `run_h9_takeover_hazards.py:474-484` — no `robust=True` passed; confirmed default is `robust=False` | [VERIFIED FACT] |
| D10 | No PH assumption test anywhere in H9 codebase | J6, K3, L-02 | **YES** | `grep -ri 'schoenfeld\|check_assumptions\|proportional_hazard' src/f1d/` returns no H9 hits | [VERIFIED FACT] |
| D11 | Docstring says `takeover_hazard_table.tex`; code writes `takeover_table.tex` | J7, L-22 | **YES** | Docstring line 64 vs code line 940 confirmed | [VERIFIED FACT] |
| D12 | Main sample: 84,104 intervals, 1,870 firms, 560 events | E5 line 260 | **YES** | Run log confirms; verified against both panels | [VERIFIED FACT] |
| D13 | Uninvited events in Main: 73; Friendly: 461; Unknown: 26 | E4 line 251; I verification 4 | **YES** | Run log lines 20-24 confirm | [VERIFIED FACT] |
| D14 | Sparse controls: Size, BM, BookLev, ROA, CashHoldings | A4 line 65 | **YES** | Code at `run_h9_takeover_hazards.py:130-136` confirms | [VERIFIED FACT] |
| D15 | Cause-specific indicators created redundantly in panel builder and runner | J8, L-23 | **YES** | `build_h9_takeover_panel.py:362-367` and `run_h9_takeover_hazards.py:287-288` confirmed | [VERIFIED FACT] |
| D16 | Counting-process format with start/stop in days since 2000-01-01 | A6, F line 291-292 | **YES** | `build_h9_takeover_panel.py:339-340` confirms REFERENCE_DATE = 2000-01-01 | [VERIFIED FACT] |
| D17 | 4-year interval cap (1,461 days) | A6, G line 342 | **YES** | `build_h9_takeover_panel.py:343` confirms MAX_INTERVAL_DAYS = 1461 | [VERIFIED FACT] |
| D18 | Multi-event validation: at most 1 event per firm | A6, line 96 | **YES** | `build_h9_takeover_panel.py:384-390` raises ValueError if >1 event per firm | [VERIFIED FACT] |
| D19 | merge_asof has no tolerance | K4, L-09 | **YES** | `_compustat_engine.py:1287-1294` — no tolerance parameter in merge_asof call | [VERIFIED FACT] |
| D20 | SDC first-bid-only approach | K4 line 547 | **YES** | `takeover_indicator.py:167-168` sorts by Date Announced and takes `.first()` per gvkey | [VERIFIED FACT] |
| D21 | Year-stratified uninvited models have 14/17 strata <5 events | J5, H-spec line 386 | **UNVERIFIABLE** | Cannot independently verify from code alone; depends on data. Audit claims run_log evidence. | [UNVERIFIED CONCERN] — plausible given 24-33 total uninvited events across 17 years |
| D22 | Concordance range 0.43-0.59 | I verification 13, line 427 | **PARTIALLY** | Canonical run diagnostics show range ~0.35-0.52. The 0.43-0.59 range may be from the earlier run with ClarityCEO. | [VERIFIED ERROR] — numbers from wrong run |
| D23 | All clarity coefficients statistically insignificant (all p > 0.48) | I verification 14, line 428 | **UNVERIFIABLE for canonical** | May be true for 2026-03-13 run (with ClarityCEO). Cannot verify for canonical run which has only CEO_Res and Mgr_Res. | [UNVERIFIED CONCERN] |
| D24 | Audit claims "canonical run is 2026-03-18_160645" | B, line 142 | **YES** | File exists with 23 output files | [VERIFIED FACT] — but canonical run has 0% ClarityCEO |
| D25 | Docstring line 33 says "Sparse block: Size, BM, Lev, ROA, CashHoldings" | Not flagged | **MISSED** | Docstring says `Lev`; code SPARSE_CONTROLS says `BookLev`. This is a docstring/code mismatch. | [VERIFIED MISSED ISSUE] |

---

## E. Unsupported/Overstated Claims

| # | Claim | Location | Why unsupported/overstated |
|---|-------|----------|---------------------------|
| E1 | "243 coefficient rows" | B, line 125 | The canonical run (2026-03-18_160645) produces 162 HR rows, not 243. The 243 count comes from the 2026-03-13 run which used an older panel with ClarityCEO. The audit claims the canonical run is 2026-03-18 but reports numbers from 2026-03-13. |
| E2 | "The null association between clarity and takeover hazard is consistently observed across 36 specifications" | N, line 662 | (a) The audit earlier notes only 24 models estimated, not 36. (b) The canonical run estimates only 24 models, of which 12 are CEO_Res and 12 are Mgr_Res — zero ClarityCEO models. The "36 specifications" number is unsupported by any run. |
| E3 | Section E5 complete-case counts (51,627 / 40,310 / 54,981) | E5 lines 261-263 | These numbers come from the 2026-03-12 panel (with `Lev` column). The canonical panel (2026-03-18) has `BookLev` and 0% ClarityCEO, producing entirely different complete-case counts. The audit does not state which panel build these numbers come from. |
| E4 | EPV values in H-spec register (51.2, 45.8, 59.0 for CEO, CRes, MRes sparse All) | H lines 355-357 | These EPV values derive from event counts (307, 275, 354) from the older panel. The canonical panel's event counts are (0, 78, 101), yielding EPV of (N/A, 13.0, 16.8). The entire estimation spec register is computed from stale data. |
| E5 | "ClarityCEO: 40.3% missing" characterized as structural missingness | J2, L-03, K2, K4, N | While structural missingness was a valid concern at 40.3%, the actual problem is now 100% missing (0% coverage). The audit buries the 0% finding in parenthetical notes rather than elevating it to the primary blocking issue. |

---

## F. False Positives

| # | Issue flagged in L1 | Location | Why it is a false positive or overcounted |
|---|---------------------|----------|------------------------------------------|
| F1 | No verified false positives | — | The issues flagged in the first-layer audit are genuine. The SE/clustering concern (L-01), PH test absence (L-02), and structural missingness (L-03) are all real. The audit does not flag phantom issues. |

---

## G. Missed Issues

| # | Issue | Severity | Evidence | Why it matters |
|---|-------|----------|----------|---------------|
| G1 | **ClarityCEO upstream breakage: 0% coverage in canonical panel** | **BLOCKING** | `python -c "import pandas as pd; df=pd.read_parquet('.../2026-03-18_185306/takeover_panel.parquet'); print(df['ClarityCEO'].notna().sum())"` returns 0. Same for 2026-03-18_160406 panel. | The PRIMARY clarity construct has zero observations. All 12 ClarityCEO-variant models are skipped in the canonical run. The audit mentions this in passing (dependency chain step 9) but does not create a top-level blocking issue for it. A thesis committee would need to know that the primary construct is entirely absent from results. |
| G2 | **Docstring/code mismatch: `Lev` vs `BookLev` in sparse controls description** | Low | Docstring line 33: "Sparse block (all models): Size, BM, Lev, ROA, CashHoldings". Code SPARSE_CONTROLS line 133: `"BookLev"`. | The audit flagged the `takeover_hazard_table.tex` vs `takeover_table.tex` mismatch (J7/L-22) but missed this parallel mismatch in the same file. |
| G3 | **BookLev vs Lev column name change breaks panel compatibility** | Medium | Old panel (2026-03-12) has column `Lev`; new panel (2026-03-18) has column `BookLev`. The runner expects `BookLev`. If the old panel is loaded, the `BookLev` covariate would not be found, and all observations for that covariate would be dropped as NaN. | The audit does not discuss the column rename or its impact on backward compatibility with older panel builds. |
| G4 | **BookLev definition inconsistency: no `.clip(lower=0)` for quarterly computation** | Low-Medium | `_compustat_engine.py:1039`: `comp["BookLev"] = (comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]` — no clipping of negative debt values. But the annual debt computation at line 628-629 uses `.clip(lower=0)`. | Negative dlcq values (which can occur for firms with net current asset positions) are included in quarterly BookLev but excluded from annual debt calculations. This creates inconsistency and could produce negative leverage values (though these would be winsorized). |
| G5 | **Internal inconsistency in HR row counts** | Medium (audit-craft) | Section B line 125 says "243 coefficient rows." Dependency chain step 9 says "162 hazard ratio rows." These cannot both be correct for the same run. | A committee member reading the audit would be confused by contradictory numbers. The 243 comes from the 2026-03-13 run; the 162 from the canonical 2026-03-18 run. |
| G6 | **Complete-case event counts in diagnostics do not match audit's E5 table** | High (audit-craft) | Canonical run diagnostics: CEO_Res All = 78 events, Mgr_Res All = 101 events. Audit E5: CRes = 275 events, MRes = 354 events. These are from different panel builds. | The audit's EPV calculations, event-count-based conclusions, and power analysis concerns are all computed from stale data. |
| G7 | **No discussion of `formula` parameter in CoxTimeVaryingFitter** | Low | Code at line 482: `formula=" + ".join(covariates)`. The `formula` parameter in `CoxTimeVaryingFitter.fit()` was added in lifelines 0.27.0+. Earlier versions may not support it. | Reinforces the unpinned-version concern (L-21) but also means the audit's description of the model specification is incomplete — it does not mention how covariates are selected for the model. |
| G8 | **Concordance sign convention not verified** | Low | `lifelines.utils.concordance_index` expects higher predicted_scores to correspond to shorter event_times (higher risk). The code passes partial hazard directly, which is correct. But the audit does not verify the sign convention, only noting the "approximation" aspect. | If a future code change inadvertently negated the hazard, the concordance would be inverted (showing ~0.50 as spurious good fit rather than genuine null). |

---

## H. Severity Recalibration

| Issue | L1 Severity | L2 Severity | Rationale for change |
|-------|-------------|-------------|---------------------|
| L-01: Model-based SE (no robust/cluster) | Critical | Critical | **Agree.** Correctly identified as the most severe methodological issue. |
| L-02: No PH assumption test | High | High | **Agree.** Mandatory for any Cox model publication. |
| L-03: ClarityCEO structural missingness (40.3%) | High | **BLOCKING** | **Upgrade.** The audit characterizes this as 40.3% missing. The actual situation is far worse: the canonical panel has 0% ClarityCEO coverage. This is not "structural missingness" — it is a complete upstream data pipeline failure. The primary clarity construct is entirely absent from results. |
| L-04: No governance/ownership controls | High | High | **Agree.** Standard omitted variable concern for takeover prediction. |
| L-05: No placebo/falsification tests | Medium | Medium | **Agree.** Correctly downgraded for null-result suite. |
| L-09: merge_asof no tolerance | Medium | Medium | **Agree.** Real issue but not thesis-blocking. |
| L-10: Unknown-type events censored | Medium | Medium | **Agree.** 26 events of unknown type; sensitivity analysis warranted. |
| L-19: No power analysis | Medium | Medium-High | **Slight upgrade.** With the canonical run having only 78-101 events (not 275-354), power analysis is even more critical. |
| L-22: Docstring/code filename mismatch | Low | Low | **Agree.** Minor documentation issue. |
| NEW G1: ClarityCEO 0% coverage in canonical panel | Not flagged as blocking | **BLOCKING** | The primary clarity construct has zero observations in the canonical run. This supersedes L-03 in severity. |
| NEW G5: Internal inconsistency in HR row counts | Not flagged | Medium (audit-craft) | Undermines audit document reliability. |

---

## I. Completeness Gaps

| Gap | Impact on committee/referee understanding | L1 coverage |
|-----|------------------------------------------|-------------|
| Which panel build each number comes from | Committee cannot tell if E5 counts are current or stale | Not distinguished |
| ClarityCEO upstream pipeline status | Committee would not know the primary construct is entirely missing from canonical results | Mentioned in passing at step 9, not elevated |
| Column rename (Lev -> BookLev) impact | Committee would not know the panel structure changed between builds | Not mentioned |
| Actual event counts in canonical run (78/101) vs audit's stated counts (275/354) | Committee would use wrong numbers for power assessment | Stale numbers reported |
| Concordance range in canonical run (~0.35-0.52) vs audit's range (0.43-0.59) | Committee would have wrong discrimination quality assessment | Stale numbers reported |
| Number of models actually producing results (24 vs 36 vs "all specifications") | Committee would think ClarityCEO models exist in results | Partially acknowledged but inconsistently |

---

## J. Reproducibility Assessment

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Can panel builder run end-to-end? | **YES** | Multiple timestamped outputs exist; code has no hardcoded paths |
| Can econometric runner run end-to-end? | **YES** | Multiple timestamped outputs exist; latest run (2026-03-18_185558) completed |
| Do reported numbers match actual outputs? | **NO** | Section B says 243 HR rows; canonical run has 162. E5 sample counts from different panel build than canonical. Concordance range stale. |
| Are results deterministic? | **YES** | Cox PH is deterministic given data; no random seeds needed |
| Is environment fully specified? | **PARTIALLY** | lifelines version not pinned (L-21). Column name change (Lev->BookLev) could break reproducibility across panel versions. |
| Can a third party reproduce from code alone? | **YES with caveats** | Code is self-contained; but reproducer would get different results depending on which panel build they use (pre- or post-BookLev rename) and whether ClarityCEO upstream is functioning |

---

## K. Econometric Meta-Audit

| Econometric concern | L1 audit handling | L2 assessment |
|--------------------|-------------------|---------------|
| **SE/clustering** | Correctly identified as Critical; correctly notes `robust=True` raises NotImplementedError; correctly specifies CoxPHFitter migration path | **Adequate.** This is well-handled. |
| **PH assumption testing** | Correctly identified as absent; rated High | **Adequate.** Correctly flags mandatory diagnostic. |
| **Counting-process construction** | Thoroughly documented; start/stop intervals, post-takeover removal, 4-year cap | **Adequate.** Interval construction is sound. |
| **Tied events handling** | States "Efron (lifelines default)" | **Adequate.** Efron is appropriate for tied events and is indeed the lifelines default. |
| **Censoring mechanism** | Correctly describes administrative censoring (2018-12-31), 4-year cap censoring, Unknown-type censoring | **Adequate.** Censoring is well-documented. |
| **Time-varying covariates** | Correctly notes covariates measured at call opening each interval | **Adequate.** ClarityCEO is time-invariant (CEO FE); residuals are time-varying. Both correctly handled. |
| **Risk-set construction** | Correctly describes counting-process format with late entry | **Adequate.** lifelines CoxTimeVaryingFitter handles late entry natively. |
| **Competing risks** | Correctly describes cause-specific Cox PH approach; notes Unknown events as censored | **Adequate.** Standard cause-specific approach. |
| **EPV diagnostics** | Comprehensive EPV reporting with critical/low/ok flags; suppression from LaTeX for EPV<5 | **Adequate** for the earlier run. **Stale** for canonical run (event counts differ substantially). |
| **Calendar time scale** | Flagged as L-20; correctly notes alternative scales not tested | **Adequate.** Good catch for a survival-specific concern. |
| **Power analysis** | Flagged as L-19; correctly notes null-result needs power assessment | **Adequate** in identification; **stale** in specifics (uses 307 events from older run; canonical has 78-101). |

---

## L. Audit-Safety Assessment

| Safety criterion | Status | Evidence |
|-----------------|--------|---------|
| Does audit clearly distinguish verified from unverified claims? | **YES** | Verification classification key used throughout (VERIFIED FACT, VERIFIED IMPLEMENTATION ISSUE, etc.) |
| Does audit avoid rubber-stamping? | **YES** | Critical issues correctly flagged; "SALVAGEABLE WITH MAJOR REVISIONS" verdict is appropriately skeptical |
| Does audit cite specific code lines? | **YES** | Line references provided for most claims (e.g., `run_h9_takeover_hazards.py:474-484`) |
| Does audit flag its own limitations? | **PARTIALLY** | Does not flag that its numbers come from multiple runs; does not flag that the ClarityCEO breakage makes many of its statistics obsolete |
| Is the audit internally consistent? | **NO** | HR row count: 243 (B) vs 162 (step 9). E5 counts from different panel than canonical. "36 specifications" (N) vs "24 models" (H). |
| Could the audit mislead a committee? | **YES** | A committee reading E5 would believe CEO clarity models exist with 307 events. They do not — the canonical run has 0 ClarityCEO observations. |

---

## M. Master Issue Register

| ID | Category | Severity | Source | Description | Evidence | Consequence | Recommended fix |
|----|----------|----------|--------|-------------|----------|-------------|----------------|
| RT-01 | Audit-craft / data pipeline | **BLOCKING** | L2 (new) | ClarityCEO has 0% coverage in canonical panel (2026-03-18_160406). All 12 primary-style models fail silently (skipped due to 0 observations). Upstream ClarityCEO pipeline is broken. | `pd.read_parquet('.../2026-03-18_160406/takeover_panel.parquet')['ClarityCEO'].notna().sum()` = 0 | Primary clarity construct entirely absent from canonical results. The suite produces only secondary residual models. | Fix upstream ClarityCEO merge in panel builder; rebuild panel; re-run econometric suite. |
| RT-02 | Audit-craft | High | L2 (new) | First-layer audit mixes numbers from 2026-03-12 panel (with `Lev`, 59.7% ClarityCEO) and 2026-03-18 panel (with `BookLev`, 0% ClarityCEO). E5 sample counts, EPV values, concordance ranges, and HR row counts are internally inconsistent. | B line 125 says 243 HR rows; step 9 says 162. E5 counts verified against old panel, not canonical. | Committee would have incorrect understanding of sample composition, event counts, and model estimates. | Re-run audit against a single, current panel build. Clearly state which run each number comes from. |
| RT-03 | Documentation | Medium | L2 (new) | Docstring line 33 says sparse controls include `Lev`; actual SPARSE_CONTROLS at line 133 says `BookLev`. Second docstring/code naming mismatch in same file (first is takeover_hazard_table.tex at line 64). | Code inspection of `run_h9_takeover_hazards.py:33` vs `:133` | Reproducers checking docstring would expect `Lev` column but find `BookLev`. | Fix docstring to say `BookLev`. |
| RT-04 | Data pipeline | Medium | L2 (new) | Column rename from `Lev` to `BookLev` between panel builds (2026-03-12 vs 2026-03-18) is undocumented. The runner expects `BookLev`; older panels have `Lev`. | Old panel columns include `Lev`; new panel has `BookLev`; code expects `BookLev` | Backward incompatibility; older panels cannot be used with current runner. | Document the rename; consider migration script for older panels. |
| RT-05 | Audit-craft | Medium | L2 (new) | Internal HR row count inconsistency: Section B claims 243; dependency chain step 9 claims 162. Both cannot be correct for the same run. | Line 125: "243 coefficient rows"; step 9: "162 hazard ratio rows" | Undermines audit credibility. | Correct to 162 for canonical run (or specify which run produced 243). |
| RT-06 | Implementation | Low-Medium | L2 (new) | BookLev quarterly computation at `_compustat_engine.py:1039` does not clip negative dlcq/dlttq values, unlike the annual debt computation at lines 628-629 which uses `.clip(lower=0)`. | `comp["BookLev"] = (comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]` vs `debt_c = annual["dlcq"].clip(lower=0).fillna(0)` | Negative debt values could produce anomalous leverage ratios. After winsorization, impact is likely minor. | Add `.clip(lower=0)` to quarterly BookLev computation for consistency. |
| L-01 | Inference/SEs | **Critical** | L1 (confirmed) | SEs are model-based (inverse Hessian), neither robust nor clustered. CoxTimeVaryingFitter does not support robust=True or cluster_col. | Code at `run_h9_takeover_hazards.py:474-484` | SE underestimated; fix requires estimator class change. | Confirmed. Switch to CoxPHFitter or block bootstrap. |
| L-02 | Econometric implementation | High | L1 (confirmed) | No PH assumption test. | No Schoenfeld/check_assumptions code found | PH assumption unverified. | Confirmed. Add PH test. |
| L-03 | Identification | **BLOCKING** (upgraded from High) | L1 (recalibrated) | ClarityCEO has 0% coverage in canonical panel, not 40.3% as characterized. | Data verification of canonical panel | Primary construct entirely absent. | Superseded by RT-01. Fix upstream pipeline first. |

---

## N. What Committee Would Not Know

Based solely on reading the first-layer audit (H9.md), a thesis committee would NOT know:

1. **The primary clarity construct (ClarityCEO) has zero observations in the canonical run.** The audit mentions this in parenthetical notes at dependency chain step 9 but does not create a top-level blocking issue. A committee member reading Section E5 would believe that 51,627 intervals with 307 events exist for CEO clarity models.

2. **The EPV values in the H-spec register are stale.** The audit reports EPV of 51.2 for the primary CEO All-Takeover model (H9-S1-CEO). This model does not exist in the canonical run output.

3. **The actual event counts in the canonical run's secondary models are substantially lower** than those reported in E5 (78 vs 275 for CEO_Res; 101 vs 354 for Mgr_Res). This makes the power analysis concern (L-19) far more acute than the audit suggests.

4. **The concordance range reported (0.43-0.59) is from an earlier run.** The canonical run shows concordance ranging from ~0.35 to ~0.52, with several cause-specific models below 0.40.

5. **The `Lev` to `BookLev` column rename** occurred between panel builds and affects backward compatibility.

6. **The 243 HR row count is from a non-canonical run.** The canonical run produces 162 HR rows.

---

## O. Priority Fixes

| Priority | Fix | Rationale | Effort |
|----------|-----|-----------|--------|
| 1 | **Fix ClarityCEO upstream pipeline** | Primary clarity construct has 0% coverage in canonical panel. Until fixed, the suite cannot test its primary hypothesis. | Medium — investigate why ClarityCEO merge produces zero matches in the latest panel builder run |
| 2 | **Re-audit H9.md against a single, current panel build** | Current audit mixes numbers from multiple runs, creating internal inconsistencies. All E5 counts, EPV values, concordance ranges, and HR row counts need updating. | Medium — re-run verification commands against canonical outputs |
| 3 | **Switch to robust, clustered SE** (L-01) | Foundation of valid inference. | Medium-High — estimator class change required |
| 4 | **Add PH assumption test** (L-02) | Mandatory Cox diagnostic. | Low |
| 5 | **Add power analysis** (L-19) | Essential for null-result credibility. Even more critical now that event counts are lower than reported. | Low |
| 6 | **Fix docstring inconsistencies** (L-22, RT-03) | Two naming mismatches in runner docstring. | Trivial |
| 7 | **Pin lifelines version** (L-21) | Reproducibility safeguard. | Trivial |

---

## P. Final Readiness Statement

**Is the first-layer audit factually correct?**
PARTIALLY. The audit correctly identifies the major methodological issues (SE/clustering, PH testing, structural missingness) and provides thorough code-level documentation. However, it contains critical factual errors: it mixes sample counts from different panel builds, reports stale EPV values and concordance ranges, and internally contradicts itself on HR row counts (243 vs 162). Most importantly, it fails to elevate the 0% ClarityCEO coverage to a top-level blocking issue.

**Is the first-layer audit complete enough for thesis-standard review?**
NO — not in its current state. The audit would give a committee an incorrect picture of the sample composition and event counts. The committee would believe that ClarityCEO models exist with 307 events when the canonical run has zero CEO observations. The audit needs to be re-run against the current canonical panel and outputs with all numbers verified from a single, consistent run.

**Did the first-layer audit miss material issues?**
YES. It missed:
- The severity of the ClarityCEO upstream breakage (burying it in parenthetical notes instead of flagging it as blocking)
- The docstring `Lev` vs code `BookLev` naming mismatch
- The column rename breaking backward panel compatibility
- The internal inconsistency in its own reported numbers

**Are there unsupported or exaggerated claims?**
YES. The claim of "243 coefficient rows" (Section B) does not match the canonical run (162 rows). The claim that "the null association is consistently observed across 36 specifications" (Section N) is unsupported — the canonical run estimates only 24 models (none with ClarityCEO). The E5 sample counts are presented as current but come from a different panel build.

**What is the single biggest gap between the audit and reality?**
The audit presents ClarityCEO missingness as a 40.3% structural issue requiring characterization (L-03), when the actual situation is a 100% pipeline failure requiring immediate fixing (RT-01). A committee reading the audit would believe that CEO clarity models exist with ~307 events. They do not — zero ClarityCEO observations exist in the canonical panel.

**Overall L2 verdict: The first-layer audit is a GOOD document with CRITICAL factual errors. It must be re-run against the canonical panel outputs to correct stale numbers, and the ClarityCEO upstream breakage must be elevated to a top-level blocking issue before the audit is thesis-ready.**
