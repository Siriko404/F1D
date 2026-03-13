# H9 — Second-Layer Red-Team Audit

**Suite ID:** H9 (Takeover Hazard Models)
**Red-team date:** 2026-03-12
**First-layer audit:** `docs/provenance/H9.md`
**Red-team output:** `docs/provenance/H9_red_team.md`

---

## A. Red-Team Bottom Line

The first-layer audit (H9.md) is technically sound, well-structured, and covers the primary implementation risks honestly. It correctly identifies the three High-severity issues that would stop a corporate finance referee cold — missing cluster-robust SEs, missing PH test, and the table-note standardization falsehood — and it does so with direct code evidence. It is not a rubber-stamp document.

However, the audit contains one verifiable factual error (git commit attribution), misses a concrete output-labeling bug that would confuse any referee reading the CSV (**n_intervals is stored as "n_firms"** in hazard_ratios.csv), fails to reconcile a 19-firm discrepancy between its two event-count figures (690 builder vs 671 panel), and underplays the implication that the three clarity variants are not estimated on the same sample — invalidating the "robustness" framing. The attrition table's one-variant coverage is also an unreported limitation.

None of these missed issues are thesis-killing on their own, but together they mean a referee using only H9.md would be left with an incorrect description of the hazard_ratios.csv schema, unaware of the sample-composition confound across variants, and unable to reconcile the event-count figures.

**Overall grade for the first-layer audit: PARTIALLY RELIABLE**

**Suite implementation verdict: SALVAGEABLE WITH MAJOR REVISIONS**

**Risk direction:** The first audit **understated risk** on two dimensions (n_firms labeling bug; sample-incomparability of variants as "robustness") and **correctly stated** risk on all others.

---

## B. Scope and Objects Audited

| Item | Path |
|---|---|
| Suite ID | H9 |
| Suite entrypoint | `src/f1d/econometric/run_h9_takeover_hazards.py` (957 lines) |
| Panel builder | `src/f1d/variables/build_h9_takeover_panel.py` (651 lines) |
| Event indicator helper | `src/f1d/shared/variables/takeover_indicator.py` (246 lines) |
| First-layer audit | `docs/provenance/H9.md` (626 lines) |
| Latest econometric report | `outputs/econometric/takeover/2026-03-11_233707/report_h9_takeover.md` |
| Run log | `outputs/econometric/takeover/2026-03-11_233707/run_log.txt` |
| Model diagnostics | `outputs/econometric/takeover/2026-03-11_233707/model_diagnostics.csv` (37 rows) |
| Hazard ratios | `outputs/econometric/takeover/2026-03-11_233707/hazard_ratios.csv` |
| Cox result files | `cox_ph_all.txt`, `cox_cs_uninvited.txt`, `cox_cs_friendly.txt` (and expanded/strata variants) |
| Sample attrition | `outputs/econometric/takeover/2026-03-11_233707/sample_attrition.csv` |
| Run manifest | `outputs/econometric/takeover/2026-03-11_233707/run_manifest.json` |
| Git status at session start | HEAD = `9e50de8`; H9.md unstaged modified (M) |

Additional inspected code paths: `run_cox_tv()` (lines 389–497), `extract_results()` (lines 500–541), `_run_variant()` (lines 725–797), `prepare_main_sample()` (lines 268–306), `build_call_to_call_panel()` (lines 256–389), `TakeoverIndicatorBuilder.build()` (lines 58–242).

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer audit status | Evidence basis | Red-team note |
|---|---|---|---|
| Model/spec identification | **Pass** | Estimator (`CoxTimeVaryingFitter`), tie method (Efron default), 36-model count (3×3×4) all verified from code | VERIFIED FACT |
| Reproducibility commands | **Partial** | Commands are runnable; `get_latest_output_dir()` hazard correctly documented; Python version not pinned | Missing: environment.yml / requirements.txt version lock |
| Dependency tracing | **Pass** | Full dependency chain in section C is accurate end-to-end | VERIFIED FACT |
| Raw data provenance | **Partial** | SDC, Compustat, transcripts, H1, H0.3 all identified; raw row counts for SDC/Compustat/H1 all listed as "Unknown" | "Unknown" is acknowledged but weakens audit-safety |
| Merge / sample audit | **Partial** | Merge chain correct; delta=0 enforcement verified; but 690 vs 671 event firm discrepancy unreconciled | VERIFIED MISSED ISSUE (see RT-4) |
| Variable dictionary completeness | **Pass** | All variables in all specs documented with formula, source field, timing, transform, winsorization flag | No gaps found |
| Outlier / missing-data rules | **Pass** | Winsorization method, missing-data policy, denominator protections all correctly described | VERIFIED FACT |
| Estimation spec register | **Pass** | All 36 specs enumerated with correct event type, controls, strata, SE type | VERIFIED FACT |
| Verification log quality | **Partial** | 11 verification entries listed; most are file-reads, not reproducible shell commands with logged output | Evidence quality is "reading" not "running"; audit-safety risk |
| Known issues section | **Pass** | 10 known issues, most verified and material | Adequate; two missed issues not listed (see G) |
| Identification critique | **Pass** | Correctly identifies reverse causality, OVB, endogenous selection, CUSIP6 risk | No gaps in identification section |
| Econometric implementation critique | **Pass** | No cluster-robust SEs, no PH test, EPV concern all correctly flagged as High | Concordance computation critique (L-15) is correctly low-severity |
| Robustness critique | **Pass** | Missing alt-window, non-linearity, placebo, competing definitions all flagged | Adequate |
| Academic-integrity critique | **Pass** | Table note standardization error flagged as High | Correct |
| Severity calibration | **Partial** | Generally accurate; n_firms labeling bug missed; EPV concern could be stronger | See H for recalibration |
| Final thesis verdict support | **Pass** | "SALVAGEABLE WITH MAJOR REVISIONS" is defensible given the evidence presented | Correct given null results + structural gaps |

---

## D. Claim Verification Matrix (First Audit Claims Tested)

| Claim ID | First-layer claim | Section in first audit | Verified? | Evidence checked | Red-team verdict | Notes |
|---|---|---|---|---|---|---|
| C-01 | Estimator is `lifelines.CoxTimeVaryingFitter` | A2 | **Y** | `run_h9_takeover_hazards.py:93` — `from lifelines import CoxTimeVaryingFitter` | VERIFIED FACT | Correct |
| C-02 | Tie method: Efron (default, not configurable) | A2 | **Y** | `ctv = CoxTimeVaryingFitter()` at line 468 — no `method` arg | VERIFIED FACT | Efron is lifelines default |
| C-03 | 36 models total (3×3×4) | A2 | **Y** | Code sections A–E in main(): 3 events × 3 variants × 4 control blocks | VERIFIED FACT | Correct |
| C-04 | No cluster-robust SEs | A5 | **Y** | `ctv.fit(...)` at lines 469–477 has no `robust` or `cluster` argument | VERIFIED FACT | `cluster_var="gvkey"` collected in diagnostics (line 789) but NOT passed to fitter |
| C-05 | `warnings.filterwarnings("ignore")` at line 87 | A5, L-10 | **Y** | Line 87 of runner | VERIFIED FACT | Correct |
| C-06 | Main sample excludes FF12=8 (Utility) and FF12=11 (Finance) | A4 | **Y** | `MAIN_SAMPLE_EXCLUDE_FF12 = [8, 11]` (line 198); `prepare_main_sample()` line 270 | VERIFIED FACT | Correct |
| C-07 | Table note claims standardization; no standardization in code | G, L-4 | **Y** | LaTeX note at line 898: "All continuous controls are standardized..."; no standardization code in `_run_variant()` (lines 725–797) | VERIFIED FACT — table note is wrong | High severity, correctly flagged |
| C-08 | ClarityCEO is time-invariant (one value per CEO-tenure) | A4, L-8 | **Y** | `build_h9_takeover_panel.py:26`: "ClarityCEO (time-invariant CEO FE): merged per ceo_id x sample" | VERIFIED FACT | Correct |
| C-09 | Panel: 107,644 intervals, 2,410 firms, 671 event firms | E4 | **Y** | run_log.txt line 15: "Rows (call-to-call intervals): 107,644; Unique firms: 2,410; Takeover event firms: 671 / 2,410" | VERIFIED FACT | Correct |
| C-10 | Main sample: 84,104 intervals, 1,870 firms, 568 event firms | E5 | **Y** | run_log.txt line 18–19: "84,104 call-to-call intervals, 1,870 firms; 568" | VERIFIED FACT | Correct |
| C-11 | Uninvited: 75 events; Friendly: 467; Unknown: 26 in Main | E5 | **Y** | run_log.txt lines 21–22 | VERIFIED FACT | Correct |
| C-12 | CEO variant: 51,627 intervals, 308 event firms | E5 | **Y** | model_diagnostics.csv row 1; run_log.txt | VERIFIED FACT | Correct |
| C-13 | CEO_Residual: 40,310 intervals, 276 event firms | E5 | **Y** | model_diagnostics.csv row 2 | VERIFIED FACT | Correct |
| C-14 | Manager_Residual: 54,981 intervals, 355 event firms | E5 | **Y** | model_diagnostics.csv row 3 | VERIFIED FACT | Correct |
| C-15 | All clarity p-values > 0.48 (null result) | I, K1 | **Y** | report_h9_takeover.md: all clarity HR p-values range 0.493–0.998 | VERIFIED FACT | Correct; null result robust across 36 specs |
| C-16 | CUSIP6 linkage may have false positives | E3, L-5 | **Partial** | Code logic at `takeover_indicator.py:84` confirmed CUSIP6; accuracy unverified against external source | VERIFIED code path; UNVERIFIED match accuracy | Correctly flagged as unverified |
| C-17 | Max interval duration = 5,550 days | E4 | **Y** | First-layer audit cites `report_h9_panel.md`; I read run_log.txt which confirms "median=91, mean=97" but not the max explicitly; max appears in builder panel report (not re-read) | PARTIALLY VERIFIED — plausible but not independently confirmed by red-team | UNVERIFIED CONCERN — take as stated |
| C-18 | Last econometric run at git commit `9f0fe6f` | Header | **N** | Git log shows 9f0fe6f = "refactor(h9): replace legacy 4.x version numbering"; HEAD = 9e50de8 = "chore: add Intangibility/AssetGrowth builders, remove audit docs, add H9 session logs"; the run 2026-03-11_233707 was likely committed at 9e50de8 | **VERIFIED ERROR IN FIRST AUDIT** | Run directories were committed at HEAD (9e50de8), not 9f0fe6f |
| C-19 | ClarityCEO coverage in Main = 52,080 / 84,104 = 61.9% | E2 | **Partial** | The CEO variant uses 51,627 complete-case intervals. 84,104 – 51,627 = 32,477 dropped. This drop combines missing ClarityCEO AND missing financial controls. 52,080 match figure is not logged in run_log.txt | UNVERIFIED — figure sourced from summary stats, not directly logged in run | Plausible but conflates two distinct drop sources |
| C-20 | Attrition table "After complete-case filter = 51,627" | I | **Y** | `sample_attrition.csv` shows 51,627 (first model only). Code at lines 910–916 uses `diag_rows[0]` — only CEO-sparse-All | VERIFIED FACT — but audit does not flag that only CEO variant is shown | MISSED ISSUE: attrition table omits CEO_Residual (40,310) and Manager_Residual (54,981) |
| C-21 | No PH test implemented | K3, L-2 | **Y** | Full runner code inspected; no call to `proportional_hazard_test` or Schoenfeld test anywhere | VERIFIED FACT | Correctly flagged as High |
| C-22 | Variable summary stats "from summary_stats.csv, call-level panel, 112,968 rows" | I | **Partial** | Two different summary_stats.csv files exist (builder and runner). Builder stats come from `VariableStats` objects (not from the final counting-process panel). Takeover N=690 in builder stats vs 671 event firms in panel. Discrepancy unexplained. | VERIFIED INCONSISTENCY — see RT-4 | The audit's table header says 112,968 rows but Takeover N=690 implies builder-level aggregation, not panel row-level count |
| C-23 | H9-B coefficient comparison not statistically tested | J-8, L-7 | **Y** | No cross-model test in any output file | VERIFIED FACT | Correctly flagged as High |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| Issue ID | Claim / statement | Why unsupported or weak | Severity | What evidence was missing | Corrected formulation |
|---|---|---|---|---|---|
| E-01 | "Last econometric run at `9f0fe6f`" (audit header) | Git log places `9f0fe6f` before `9e50de8` (HEAD). The commit message for 9e50de8 is "add H9 session logs" which would include the 2026-03-11 run directories. So the latest run was produced under HEAD, not 9f0fe6f. | Low–Medium | A `git log --oneline --follow outputs/econometric/takeover/2026-03-11_233707` would have confirmed the commit | "Last econometric run and related session logs committed at HEAD (`9e50de8`)" |
| E-02 | "ClarityCEO coverage in Main = 52,080 / 84,104 = 61.9%" presented as VERIFIED | The figure 52,080 does not appear in run_log.txt or any output file I could find; it is computed indirectly from builder summary stats. The complete-case CEO sample (51,627) already includes financial control missingness on top of ClarityCEO missingness, so 52,080 overstates ClarityCEO-specific coverage within the estimation sample. | Low | Logging ClarityCEO missingness separately from control missingness in the run log | "ClarityCEO match rate within Main sample is approximately 61–65% based on call-level builder stats; exact estimation-sample coverage is lower due to compound missingness" |
| E-03 | "BM min=−20.77" listed in variable table labeled "after winsorization" | Winsorization is at 1%/99% by fyearq; the -20.77 is the GLOBAL minimum across years, which is the minimum of each year's 1st percentile. Whether the 1st percentile is truly -20.77 in some year is plausible but the audit presents it as if this is post-winsorization within a single estimation sample. The builder summary_stats.csv covers 112,968 calls across all years; the Main-sample BM minimum could differ. | Low | Run: `python -c "import pandas as pd; df=pd.read_parquet('...takeover_panel.parquet'); print(df[df.sample=='Main']['BM'].describe())"` | State as "global minimum in call-level panel; Main-sample BM minimum unverified separately" |
| E-04 | Summary stats table header: "call-level panel, all 112,968 rows" but Takeover N=690 implies builder-level gvkey count | The builder's VariableStats for Takeover reports n=Takeover.sum() over manifest gvkeys (firm-level), which would be 690 if 690 gvkeys in the manifest matched SDC. This is NOT a call-level count (which would be 671 matching the panel's 671 event firms). The 112,968 row label and the 690 Takeover N are from different aggregations. | Medium | Clearly distinguish builder stats (firm-level Takeover counts) from call-level panel stats | "Takeover N=690 reflects firm-level SDC matches in manifest; final panel has 671 event firms; 19-firm gap unexplained" |

---

## F. False Positives in the First Audit

| Issue ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|---|---|---|---|---|---|
| F-01 | Audit implies concordance computation is "non-standard" and "may not be comparable to benchmarks" (L-15, Low severity) | The mean-partial-hazard approach for TV-Cox C-index is a reasonable pragmatic choice because `CoxTimeVaryingFitter` in lifelines does not expose a direct `concordance_index_` attribute. The code at lines 346–382 is internally consistent, documents its methodology in the docstring, and the result is correctly used only for model comparison (not as a primary result). | Code docstring lines 328–342: "For time-varying covariates, using the mean hazard... provides a more stable estimate". Lifelines docs confirm no built-in C-index for TV-Cox. | Low (audit error is low-severity) | The approach is non-standard but defensible and well-documented. Calling it a concern for "benchmarking" is slightly overstated; it is fine for internal comparison across the 36 specs. |
| F-02 | None of the other flagged issues appear to be false positives. | — | — | — | — |

---

## G. Missed Issues (Second-Layer Discoveries)

| Issue ID | Category | Description | Evidence | Severity | Why first audit missed/underplayed it | Consequence | Recommended fix |
|---|---|---|---|---|---|---|---|
| RT-1 | **Output schema / labeling bug** | `hazard_ratios.csv` column `n_firms` contains **n_intervals**, not unique firm count. In `extract_results()` (line 532), the parameter `df_clean_len` (passed as `n_intervals` from `_run_variant()` line 762) is stored as `"n_firms"`. Model diagnostics CSV separately stores correct `n_intervals` and `n_event_firms`. | `extract_results()` line 532: `"n_firms": df_clean_len`; `_run_variant()` line 762: `hr_rows = extract_results(ctv, n_intervals, ...)` | **High** | Audit did not trace the data flow from `_run_variant()` into `extract_results()` output keys | Any referee reading hazard_ratios.csv sees "n_firms=51,627" and interprets it as unique firms; actual unique firms for CEO-sparse is ~1,349 (from model_diagnostics.csv). Inflates apparent sample by ~38×. | Rename `"n_firms"` to `"n_intervals"` in `extract_results()` return dict (line 532); add `"n_firms"` = `n_intervals` / clusters as a separate key |
| RT-2 | **Sample attrition table: incomplete** | The sample attrition table (`generate_attrition_table()` at lines 910–916) uses `first_diag = diag_rows[0]` — the CEO-sparse-All model — and shows only one "After complete-case filter" row (51,627). The other two variants (CEO_Residual: 40,310; Manager_Residual: 54,981) are silently omitted. A referee sees attrition to 51,627 but does not know the sample varies by 14,000 rows across variants. | `run_h9_takeover_hazards.py:910–916`; `sample_attrition.csv` contains exactly 3 rows (Full, Main, CEO-only complete-case) | **Medium** | Audit lists the attrition table in output enumeration and cites E5 counts correctly, but does not note that the table itself only documents one variant | Reader cannot reconstruct that only 40,310 intervals are used for CEO_Residual; the thesis table would show N=40,310 without the attrition path being documented | Extend attrition table to include all three variant complete-case rows, or add a note |
| RT-3 | **Three clarity variants are NOT a robustness check — they use different samples with different compositions** | CEO variant: 51,627 intervals, 308 event firms, ~1,349 unique firms. Manager_Residual: 54,981 intervals, 355 event firms, ~1,543 unique firms. CEO_Residual: 40,310 intervals, 276 event firms, ~1,318 unique firms. These are structurally different samples — ClarityCEO requires H1 estimation (≥5 calls per CEO), while residuals require H0.3 estimation. A firm with a CEO who had <5 calls is excluded from CEO but included in Manager_Residual. Firms excluded from CEO_Residual may have fewer calls than needed for H0.3. The samples differ by 14,671 intervals (CEO_Residual vs Manager_Residual). | model_diagnostics.csv: n_clusters: CEO=1,349, Manager_Residual=1,543, CEO_Residual=1,318. These are distinct populations. | **High** | First audit correctly notes ClarityCEO identification differs (L-8, Medium) but frames all three variants as "robustness" (Section H header). It does not compute or flag the sample-composition difference as incomparability. | If CEO and Manager_Residual give different results, it is impossible to tell whether this reflects different clarity constructs or different sample composition (firms with CEO ≥5 calls vs all firms). The "robustness" framing is incorrect — these are sensitivity tests, not robustness tests. | Label variants explicitly as "sensitivity across clarity constructs and estimation samples" not "robustness". Report a table of sample characteristics by variant. |
| RT-4 | **690 builder-level event firms vs 671 final-panel event firms: 19-firm gap unexplained** | `TakeoverIndicatorBuilder` reports n=690 targeted gvkeys in manifest (VariableStats.n = Takeover.sum()). Final counting-process panel reports 671 event firms (run_log.txt). The 19 missing firms likely had their first call on/after the takeover date (dropped as post-takeover) or produced only zero-duration intervals (filtered). But neither the builder report nor the econometric report reconciles this. | `takeover_indicator.py:205–208`: `n_takeover = result["Takeover"].sum()` → 690; `run_log.txt`: "Takeover event firms: 671 / 2,410" | **Medium** | First audit's summary table notes N=690 for Takeover (from builder stats) and separately notes 671 event firms (from panel report) but never explicitly reconciles the two or flags the gap | 19 firms classified as takeover targets in SDC have no valid at-risk interval. A referee would note the discrepancy between the SDC match count and the analysis event count. | Log explicitly which gvkeys have Takeover=1 in SDC but no valid interval in the counting-process panel; provide a reconciliation note |
| RT-5 | **EPV for uninvited models is critically low (EPV = 6–7), not merely "at the limit"** | With 36–46 uninvited events and 6 covariates (sparse), EPV = 36/6 = 6.0. The conventional minimum is EPV ≥ 10 (Peduzzi et al., 1995). The expanded model adds 3 controls → EPV = 40/9 = 4.4. EPV <10 causes biased estimates, inflated type-I error, convergence instability, and unreliable SEs — not just "wider confidence intervals". | model_diagnostics.csv: CEO uninvited n_event_firms=40; CEO_Residual uninvited n_event_firms=36; expanded variants have same event counts | **High** | First audit labels this "High" (L-3) but characterizes it as "at the limit" and "unreliable". It does not compute the EPV explicitly or note that expanded models fall below EPV=5, making them critically underpowered. The audit also does not flag that lifelines may generate convergence warnings (which are silently suppressed) specifically for these models. | Every uninvited model coefficient and SE is statistically unreliable. The expanded uninvited models (EPV=4.4) should not be reported without strong caveats. | Report exact EPV for all uninvited models; suppress or clearly caveat all uninvited expanded results; investigate run_log for suppressed convergence warnings |
| RT-6 | **Cause-specific event indicators derived at run time, not stored in panel — replication gap** | `Takeover_Uninvited` and `Takeover_Friendly` are computed inside `prepare_main_sample()` at runner lines 280–281 using `df["Takeover_Type"]`. They are NOT stored in the panel parquet. A replicator who loads `takeover_panel.parquet` directly does not get these indicators; they must re-run the runner or replicate the derivation independently. | `prepare_main_sample()` lines 280–281; panel parquet inspection would show `Takeover_Type` but not `Takeover_Uninvited` or `Takeover_Friendly` | **Medium** | First audit correctly notes where these are derived (A3, citing lines 280–281) but does not flag the replication implication: the panel is not self-contained for cause-specific replication | A replicator who uses the panel directly for cause-specific analysis would get wrong results without this derivation step | Store `Takeover_Uninvited` and `Takeover_Friendly` in the panel parquet; or document the derivation as a required step in the reproducibility section |

---

## H. Severity Recalibration

| Issue ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|---|---|---|---|---|---|
| L-1 | First audit | High | **High** (unchanged) | No cluster-robust SEs; correct severity | All 36 model p-values overstated |
| L-2 | First audit | High | **High** (unchanged) | PH test missing; correct severity | HR interpretation unverified |
| L-3 | First audit | High | **High+ (critical for uninvited)** | EPV=6.0 is not "at the limit" — it is a violation. Expanded uninvited EPV=4.4 is critically insufficient. Should be flagged more strongly. | All uninvited expanded results are statistically unreliable |
| L-4 | First audit | High | **High** (unchanged) | Table note standardization wrong | Reader misinterprets coefficient scale |
| L-5 | First audit | High (unverified) | **Medium** | CUSIP6 false-positive risk is real but structural; in a null-result suite, false positives dilute (not inflate) the signal. Downgrade slightly pending verification. | Moderate — false positives would dilute takeover signal, consistent with null |
| L-6 | First audit | High | **High** (unchanged) | 5,550-day interval is a real data quality issue | Baseline hazard distorted for many years |
| L-7 | First audit | High | **High** (unchanged) | H9-B untested | Core hypothesis claim unsubstantiated |
| L-8 | First audit | Medium | **Medium** (unchanged) | ClarityCEO time-invariance documented; conceptually important | Cross-sectional vs longitudinal identification confusion |
| L-9 | First audit | Medium | **Medium** (unchanged) | Reproducibility risk from latest-dir resolution | Correct |
| L-10 | First audit | Medium | **Medium–High** | Warning suppression is especially consequential for uninvited models with EPV<10 where convergence warnings are likely. Promote slightly. | Uninvited model convergence failures may be silently lost |
| L-12 | First audit | Low | **Low** (unchanged) | BM negative values post-winsorization; plausible for distressed firms | Minimal impact on takeover hazard analysis |
| RT-1 | Red-team | (new) | **High** | `n_firms` column in hazard_ratios.csv = n_intervals; directly misleads any referee reading the CSV | Reader believes CEO model has N=308 firms when it actually has N=51,627 intervals; firms = ~1,349 |
| RT-2 | Red-team | (new) | **Medium** | Attrition table incomplete; only CEO variant shown | Thesis reader cannot verify sample for other variants from provided output |
| RT-3 | Red-team | (new) | **High** | Variants are not comparable robustness checks; sample composition differs materially | Cross-variant comparisons may reflect sample differences, not construct differences |
| RT-4 | Red-team | (new) | **Medium** | 19-firm gap between SDC match count and panel event count unexplained | Minor in absolute terms but noteworthy for audit completeness |
| RT-5 | Red-team | (upgrade of L-3) | **High** | EPV explicitly computed: uninvited sparse EPV=6, uninvited expanded EPV=4.4 | Uninvited expanded models should not be reported |
| RT-6 | Red-team | (new) | **Medium** | Cause-specific indicators not in panel; replication requires re-deriving | Affects self-contained replication |

**Issues to merge:** L-3 and RT-5 address the same root cause (uninvited EPV); treat as a single issue with upgraded severity.

**Issues to downgrade:** L-5 (CUSIP6 false positives) from High to Medium given null results.

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|---|---|---|---|---|
| `n_firms` vs `n_intervals` in hazard_ratios.csv schema | First audit described the output files but did not inspect the column-level schema of hazard_ratios.csv to check the `n_firms` field definition | `extract_results()` line 532 | High | Inspection of hazard_ratios.csv column meanings against the generating code |
| Sample attrition for all three variants | Audit correctly lists all three sample sizes in E5 but does not note that the published attrition table (`sample_attrition.csv`) only documents one variant | `run_h9_takeover_hazards.py:910–916` | Medium | Note that attrition table is variant-specific; recommend extending |
| Cause-specific indicator derivation replication path | Audit notes where indicators are derived but does not flag that they are absent from the panel parquet, creating a replication gap | `prepare_main_sample()` lines 280–281; panel parquet structure | Medium | State explicitly that `Takeover_Uninvited` and `Takeover_Friendly` are not in the panel file and must be re-derived |
| EPV explicit computation for all uninvited/expanded model combinations | Audit correctly notes "36–46 events" and EPV concern but does not compute EPV for each model combination (especially expanded models with 9 covariates) | model_diagnostics.csv; covariates = 6 (sparse) or 9 (expanded) | High | Table: event_type × variant × control_block → EPV value; flag any EPV<10 |
| 690 vs 671 event firm reconciliation | Builder-level event count vs panel-level event count discrepancy noted implicitly (section I table) but never reconciled or explained | builder summary_stats vs run_log.txt | Medium | Explicit reconciliation: identify the 19 gvkeys present in SDC match but absent from final panel |
| Convergence / estimation health for uninvited models | Warnings are globally suppressed; audit flags this but does not investigate whether uninvited models actually triggered convergence warnings | `warnings.filterwarnings("ignore")` line 87; no warning-capture mechanism | High (for uninvited) | Extract warnings from lifelines for the 36–46 event uninvited runs by temporarily re-enabling; or check raw cox_cs_uninvited.txt for diagnostic flags |
| Inter-variant sample-composition comparison | Audit documents each variant's N but doesn't present a systematic comparison of covariate means/distributions across variants to check for compositional differences | model_diagnostics.csv: n_clusters 1,349 / 1,318 / 1,543 | High | Table: mean Size, BM, ClarityCEO, Takeover rate by variant sample |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented it? | Verified? | Hidden dependency? | Risk | Red-team note |
|---|---|---|---|---|---|
| Run `build_h9_takeover_panel.py` | Y — Step 2 in B | Partially | YES: `get_latest_output_dir()` resolves upstream clarity and manifest dynamically | High | Documented as J-1; correct |
| Run `run_h9_takeover_hazards.py` | Y — Step 3 in B | Partially | YES: `get_latest_output_dir()` for panel; different run = different panel if new builder runs added | High | Documented as J-1; correct |
| Upstream H1 clarity scores available | Y — listed as prerequisite | Unverified | YES: H1 must be re-run if not present; no pinned version | Medium | Noted in B commands but not in run_manifest hash |
| Upstream H0.3 residuals available | Y — listed as prerequisite | Unverified | YES: same resolution logic | Medium | Noted; hashes not in manifest |
| Python environment / version | N — not documented | No | YES: Python version not pinned; lifelines version not pinned | Medium | requirements.txt / environment.yml absent or not referenced |
| Output: `cox_ph_all_expanded.txt` etc. (expanded + strata variants) | Y — listed in B | Y | No | Low | All expanded and strata output files confirmed present in 2026-03-11_233707 |
| Output: `takeover_table.tex` | Y (correct name) | Y | No | Low | Docstring names it `takeover_hazard_table.tex` (incorrect) but first-layer audit gives correct name |
| Cause-specific indicators (Takeover_Uninvited, Takeover_Friendly) | Partial — derivation noted but panel incompleteness not flagged | Partial | YES: must run runner to derive; not in panel file | Medium | Replication gap — see RT-6 |
| Sample attrition table complete-case counts for all variants | N | N | YES: attrition table only documents CEO variant | Medium | Replicator cannot reproduce attrition path for CEO_Residual or Manager_Residual from the published attrition table |
| Random seed | Y — noted as non-issue | Y | No | Low | Deterministic; correct |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|---|---|---|---|---|
| Identification threats | **Y** | OVB (governance controls absent), endogenous selection (ClarityCEO ≥5 call requirement), reverse causality (correctly handled) all discussed | Endogenous sample selection could have been quantified (takeover rate in excluded CEO-group vs included) | Medium |
| Inference / clustering | **Y** | No cluster-robust SEs clearly flagged as High; firm-level serial correlation acknowledged | No investigation of whether lifelines' counting-process `id_col` partially mitigates the problem | Medium |
| FE / within-variation | **Y** | Time-invariant ClarityCEO correctly characterized as cross-sectional identification | Could note that stratified models (year/industry) do not add within-CEO variation; they stratify baseline hazard only | Low |
| Timing alignment | **Y** | Covariate-as-of-call timing, backward merge_asof (up to ~3 months stale) documented | Minimal concern for the research question | Low |
| Post-treatment controls | **Y** | Financial controls predate call; no post-treatment control issue | Correctly handled | — |
| Reverse causality | **Y** | Correctly noted as handled by interval structure; takeover date after call | Correct | — |
| Endogenous sample selection | **Partial** | ClarityCEO selection noted (≥5 calls); magnitude of resulting sample restriction discussed | Does not compare characteristics (takeover rate, size, leverage) of CEO-variant sample vs excluded firms. This comparison could reveal if the estimation sample is systematically different. | High |
| Model-family-specific threats | **Partial** | PH assumption test flagged (L-2). Left truncation noted (L-14, Low). | PH test absence is more consequential for time-varying residual variants than for time-invariant ClarityCEO. This calibration is absent. Also: no discussion of whether competing-risk analysis is complete (only two causes: uninvited and friendly; death, delisting, going-private are competing events not modeled). | High |
| Robustness adequacy | **Y** | Missing subsample tests, placebo, nonlinearity all flagged | Correct |  |
| Interpretation discipline | **Y** | Null results correctly characterized; no causal overreach | Correct | — |
| Academic-integrity / auditability | **Partial** | Table note standardization error flagged; global warning suppression flagged | `n_firms` mislabeling in hazard_ratios.csv not caught | High |
| Competing risks completeness | **Not covered** | The audit discusses uninvited vs friendly as competing causes, but does not address firm death (bankruptcy, going-private, merger-of-equals) as a competing risk event that may informatively censor the sample | No discussion in K2 or K3 sections | Medium |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk in first audit | Evidence | Severity | Why it matters | Fix |
|---|---|---|---|---|
| Verification log relies on "reading" not "running" | Section I lists 11 verifications, mostly stated as "Read [file]" — not as reproducible commands with logged output. No hash verification of outputs. | Medium | A third-party auditor cannot reproduce the verification; trusts the audit author to have read correctly | Convert file-read verifications to logged shell commands with outputs appended to a session log |
| Git commit attribution error (C-18) | Audit header claims "last econometric run at `9f0fe6f`" but run 2026-03-11_233707 was committed at `9e50de8` (HEAD) | Low–Medium | Creates false impression about which code version produced the results | Correct to "run 2026-03-11_233707 committed at HEAD (`9e50de8`)" |
| Variable summary table mixes builder and panel aggregations (C-22, E-04) | Takeover N=690 is a builder-level firm count; other variables are call-level means from the 112,968-row panel. The mixed aggregation is not disclosed. | Medium | Reader may interpret N=690 as the number of call rows with Takeover=1, not as the number of targeted gvkeys | Add footnote: "Takeover N reflects firm-level SDC matches in manifest; call-level event count is 671 (panel) or 568 (Main)" |
| `n_firms` column in hazard_ratios.csv is actually n_intervals (RT-1) | `extract_results()` line 532 stores n_intervals as `"n_firms"` | High | Any referee or replicator reading hazard_ratios.csv directly would misidentify the sample size. If cited as N in a table, it would report ~51,627 as "firms" rather than intervals. | Fix the column name in code; note in audit |
| "VERIFIED" label on some claims supported only by code reading, not execution | E.g., C-19 (ClarityCEO 61.9% coverage) — computed indirectly | Low | Overstates certainty for inferred figures | Distinguish "verified via execution" from "inferred from code logic" |
| First-layer audit does not separate verified facts from referee judgments systematically | Section K (referee assessment) mixes verified implementation facts with normative judgments about acceptability without clear labeling | Low | A committee relying on the audit may treat recommendations as implementation facts | Add a consistent tag (VERIFIED FACT / REFEREE JUDGMENT) to each K-section row |

---

## M. Master Red-Team Issue Register

| Issue ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis-standard reliance? |
|---|---|---|---|---|---|---|---|---|---|---|
| L-1 | First-audit correct (no change) | Econometric implementation | Y | High | `run_h9_takeover_hazards.py:468–477` | No cluster-robust SEs at firm level | `ctv.fit()` no robust arg | SEs understated; p-values overstated | Implement robust SEs or bootstrap | Y |
| L-2 | First-audit correct (no change) | Econometric implementation | Y | High | Runner — all models | No PH test (Schoenfeld) | Absent from all outputs | HR interpretation unverified | Implement `proportional_hazard_test` | Y |
| L-3/RT-5 | Underlying issue underplayed by first audit | Inference / EPV | Y | High | Uninvited models (all variants) | EPV = 6.0 (sparse) / 4.4 (expanded) — well below minimum of 10 | model_diagnostics: 36–46 events; 6 or 9 covariates | All uninvited estimates unreliable; expanded uninvited results invalid | Report as exploratory; suppress expanded uninvited | Y |
| L-4 | First-audit correct (no change) | Documentation / table | Y | High | `run_h9_takeover_hazards.py:898` | Table note claims standardization not in code | Line 898 vs no standardization code | Referee misinterprets coefficient scale | Remove standardization claim | Y |
| L-6 | First-audit correct (no change) | Data quality | Y | High | `build_call_to_call_panel.py` | Max interval = 5,550 days (15.2 yrs) | Panel report median=91 vs max=5,550 | Stale covariates; distorted baseline | Identify firm; cap interval | Medium |
| L-7 | First-audit correct (no change) | Inference | Y | High | Runner — H9-B | H9-B coefficient comparison never tested | No cross-model test in any output | H9-B is a stated but untested hypothesis | Bootstrap or stacked model | Y |
| RT-1 | Underlying implementation issue missed by first audit | Output schema / labeling | Y | High | `extract_results()` line 532 | `n_firms` in hazard_ratios.csv = n_intervals | `"n_firms": df_clean_len` where df_clean_len = n_intervals | Referee reading CSV believes N=51,627 "firms"; actual firms ~1,349 | Rename column to `n_intervals`; add `n_firms` = cluster count | Y |
| RT-3 | First-audit omission | Identification | Y | High | Runner — all variant comparisons | Three clarity variants estimated on different samples; cross-variant comparison conflates construct with sample differences | n_clusters: 1,349 / 1,318 / 1,543 from model_diagnostics.csv | "Robustness" across variants is not robustness — it is sample-conditional sensitivity | Reframe as sensitivity; add variant-by-variant sample-characteristic table | Y |
| L-5 | First-audit correct (unverified concern) | Identification | N | Medium | `takeover_indicator.py:84` | CUSIP6 linkage may produce false positive takeover assignments | Code logic confirmed; match accuracy not validated | False positives dilute takeover signal (consistent with null) | Cross-validate against PERMNO linkage | Partial |
| L-8 | First-audit correct (no change) | Identification | Y | Medium | Builder, line 26 | ClarityCEO time-invariant; identification purely cross-sectional | Code confirmed | Apples-to-oranges vs residual variants | Document explicitly in paper | Partial |
| L-9 | First-audit correct (no change) | Reproducibility | Y | Medium | Both scripts | `get_latest_output_dir()` for all upstream inputs | Code confirmed | Re-run may use different upstream artifacts | Pin or hash all upstream paths | Medium |
| L-10 | First-audit severity understate | Transparency | Y | Medium–High | `run_h9_takeover_hazards.py:87` | Global warning suppression; especially risky for EPV<10 uninvited models | Line 87 | Convergence failures/separation silently lost | Log warnings to file | Partial |
| RT-2 | First-audit omission | Reproducibility / documentation | Y | Medium | `run_h9_takeover_hazards.py:910–916` | Attrition table shows only CEO-variant complete-case count | Code: `first_diag = diag_rows[0]` | Reader cannot verify CEO_Residual (40,310) or Manager_Residual (54,981) attrition | Extend attrition table to all three variants | Low |
| RT-4 | First-audit omission | Data provenance | Partial | Medium | Builder vs panel event counts | 690 SDC-matched gvkeys vs 671 event firms in panel — 19-firm gap unexplained | VariableStats n=690 vs run_log.txt 671 | Unreconciled discrepancy; source unknown | Identify and log the 19 missing gvkeys | Low |
| RT-6 | First-audit omission | Reproducibility | Y | Medium | `prepare_main_sample()` lines 280–281 | Cause-specific indicators not stored in panel parquet | Panel lacks `Takeover_Uninvited`, `Takeover_Friendly` | Replication requires re-running runner or re-deriving | Store indicators in panel; or document as required step | Low |
| E-01 | First-audit factual error | Documentation | Y | Low–Medium | Audit header | "Last econometric run at 9f0fe6f" — incorrect; run at 2026-03-11_233707 committed at 9e50de8 | Git log ordering | Minor historical inaccuracy | Correct git commit reference | Low |
| L-13 | First-audit correct (no change) | Robustness | Y | Medium | Runner | No alternative sample windows (pre/post-GFC) | Absent | Results may be period-specific | Add subsample analyses | Partial |
| L-14 | First-audit correct (no change) | Identification | Y | Low | Panel construction | Left truncation not modeled | No entry variable | Slight downward bias early-sample hazard | Acknowledge limitation | Low |
| L-15 | First-audit false positive (mild) | Econometric | Y | Low | `compute_concordance_time_varying()` | Non-standard C-index: defensible for TV-Cox | Code documented; lifelines limitation confirmed | Minor benchmarking limitation | Cite or use standard if feasible | Low |
| L-16 | First-audit correct (no change) | Documentation | Y | Low | Builder summary stats | Builder stats reflect 112,968-row panel, not estimation sample | Two different summary_stats.csv files | Missingness rates not representative of estimation sample | Add Main-sample-only coverage table | Low |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **That `n_firms` in hazard_ratios.csv is actually n_intervals.** Any referee reading the primary result CSV directly would report the wrong sample size unit. This is the single largest factual omission.

2. **That the three clarity variants are estimated on materially different sub-samples** (1,349 vs 1,318 vs 1,543 unique firms), making cross-variant comparisons potentially confounded by sample composition. The audit uses "robustness" language but these are not robustness checks.

3. **That the cause-specific event indicators (Takeover_Uninvited, Takeover_Friendly) are not in the panel file** and must be re-derived — a replication blocker for anyone using the panel directly.

4. **That the sample attrition table covers only one of three variants.** A referee verifying attrition for the CEO_Residual or Manager_Residual model would find no documented path.

5. **That uninvited expanded models have EPV ≈ 4.4 — critically below any accepted minimum.** The audit says "at the limit" for sparse models (EPV=6) but does not compute or flag that the expanded uninvited models are worse.

6. **That global warning suppression may be masking convergence failures specifically in the 36–46 event uninvited models**, where lifelines Newton-Raphson is most likely to struggle. The audit flags the suppression but does not flag the risk is highest precisely for the models where EPV < 10.

7. **That competing risks are incomplete**: death, delisting, and going-private are not modeled as competing events. Only uninvited vs friendly are treated as competing causes; all other exits are treated as censored, which may be informative censoring.

8. **The exact git commit under which the reported results were produced** (the audit misattributes the run to 9f0fe6f rather than 9e50de8).

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|---|---|---|---|---|
| 1 | Document and flag `n_firms` mislabeling bug in hazard_ratios.csv (RT-1) | Directly misleads any referee or replicator who reads the output CSV; schema error in primary result artifact | Low — add one paragraph and flag for code fix | High — prevents published misrepresentation of N |
| 2 | Reframe three clarity variants as "sensitivity across different samples" not "robustness" (RT-3) | Cross-variant comparison currently misleads on what is being varied | Low — editorial change to section descriptions | High — prevents incorrect robustness claim |
| 3 | Compute and tabulate EPV for ALL 12 uninvited model variants (sparse + expanded) (RT-5, upgrade of L-3) | EPV<10 for all; EPV<5 for expanded; these results need stronger caveats or suppression | Low — arithmetic from model_diagnostics.csv | High — changes which results can be reported |
| 4 | Reconcile 690 builder vs 671 panel event firms (RT-4) | Unexplained discrepancy in event count; any referee will notice | Medium — requires inspecting builder pipeline | Medium — closes an audit gap |
| 5 | Flag that cause-specific indicators are absent from panel (RT-6) | Replication gap; panel not self-contained for cause-specific analysis | Low — add one note to section B reproducibility | Medium — directly affects replication usability |
| 6 | Correct git commit attribution error (E-01) | Minor factual inaccuracy; committee may check | Low | Low–Medium |
| 7 | Extend sample attrition documentation to all three variants (RT-2) | Published attrition table is incomplete | Low — add one paragraph to section I | Medium — transparency for committee |
| 8 | Note competing-risk incompleteness (exit from transcripts corpus not modeled) | Informative censoring risk not covered | Low — add to K2 identification threats | Medium — referee question |
| 9 | Distinguish "verified via execution" from "inferred from code logic" in verification log | Audit-safety; prevents false-certainty claims | Low — editorial | Low–Medium |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
Mostly yes, with significant reservations. The first audit correctly identifies the three primary threats (no cluster SEs, no PH test, false standardization claim) and is honest about the null result. A referee reading only H9.md would form an accurate overall picture of the suite's weaknesses. However, they would form one materially incorrect factual belief (that the n_firms column in hazard_ratios.csv contains firm counts) and two incorrect structural beliefs (that the three variants constitute robustness checks, and that attrition is fully documented).

**What is its biggest factual weakness?**
The `n_firms` mislabeling bug in hazard_ratios.csv (RT-1). This is not audited at all, and any referee who reads the CSV would see, for example, "n_firms = 51,627" for the CEO-All model and believe the study uses 51,627 firms rather than 51,627 call-to-call intervals from ~1,349 unique firms.

**What is its biggest completeness weakness?**
Failure to expose that the three clarity variants are estimated on structurally different samples (differing by up to 14,671 intervals and 194 unique firms), making cross-variant comparisons sample-confounded. The audit correctly notes different identification strategies but does not compute or flag the sample-composition difference.

**What is its biggest severity/judgment weakness?**
EPV for uninvited expanded models is critically low (EPV=4.4) but the audit characterizes the EPV issue as being "at the limit" for sparse models only. The expanded uninvited models should not be reported without a much stronger caveat — the audit does not separately flag these as below EPV=5.

**What is the single most important missed issue?**
RT-1 (`n_firms` mislabeling in hazard_ratios.csv). This is a verified code-level labeling bug with direct consequences for any reader using the output file, and it is not flagged anywhere in the first-layer audit.

**What is the single most misleading claim?**
The framing in Section H that the four control configurations (sparse, expanded, strata_year, strata_industry) and three clarity variants constitute "36 models" as a robustness matrix. While the model count is arithmetically correct, presenting CEO vs CEO_Residual vs Manager_Residual as "robustness" checks is misleading because they test different sub-populations with different data sources. These are sensitivity analyses, not robustness checks.

**What should a thesis committee believe after reading this red-team review?**
The H9 suite is well-engineered for the complexity of time-varying survival analysis, and the first-layer audit is genuinely useful documentation. However, before H9 results can be presented in a thesis or to any referee:
1. The `n_firms` column in hazard_ratios.csv must be renamed to `n_intervals` (code fix).
2. Cluster-robust SEs and Schoenfeld PH tests must be implemented (these are minimum referee requirements for survival analysis in corporate finance).
3. All uninvited expanded model results must be suppressed or caveated as EPV<5.
4. The table note standardization claim must be removed.
5. The three variants must be reframed as sample-conditional sensitivity, not robustness.
The null result itself is robustly stable and honestly reported; these fixes affect how confidently the null can be claimed, not the direction of the result.
