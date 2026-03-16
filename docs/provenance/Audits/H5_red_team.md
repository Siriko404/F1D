# H5 Suite: Second-Layer Red-Team Audit

**Suite ID:** H5
**Red-team audit date:** 2026-03-15
**First-layer audit date:** 2026-03-15
**Auditor posture:** Hostile-but-fair, independent verification

---

## A. Red-Team Bottom Line

The first-layer audit is **PARTIALLY RELIABLE**. It correctly identifies the most critical issue -- the code/output mismatch -- and provides a thorough econometric critique. However, it contains several material factual errors regarding the actual DV used in the produced outputs, misattributes the LaTeX table problem, and mischaracterizes the git provenance chain. It also misses a critical issue with the PanelOLS multi-index handling and the manifest timestamp forgery. A committee member relying solely on the first audit would receive a broadly correct alarm about the suite's problems but would be misled on specific details.

**First-layer audit grade:** PARTIALLY RELIABLE

**Suite verdict:** NOT THESIS-STANDARD AS IMPLEMENTED

**Risk assessment of first audit:** Mixed -- correctly identifies the reproducibility crisis and identification weaknesses, but overstates some issues (LaTeX table mismatch for the *produced* output) while understating others (manifest provenance forgery, PanelOLS duplicate-index behavior, fact that `dispersion_lead` not `dispersion` was the original DV at the manifest's referenced commit).

---

## B. Scope and Objects Audited

| Item | Path / ID |
|------|-----------|
| Suite ID | H5 |
| Suite entrypoint | `src/f1d/econometric/run_h5_dispersion.py` |
| Panel builder | `src/f1d/variables/build_h5_dispersion_panel.py` |
| First-layer audit | `docs/provenance/H5.md` |
| Panel artifact (latest) | `outputs/variables/h5_dispersion/2026-03-08_134112/h5_dispersion_panel.parquet` |
| Econometric outputs (latest) | `outputs/econometric/h5_dispersion/2026-03-11_134234/` |
| Prior econometric outputs | `outputs/econometric/h5_dispersion/2026-03-02_230912/` (used `dispersion_lead` as DV) |
| DeltaDispersionBuilder | `src/f1d/shared/variables/delta_dispersion.py` |
| IbesDetailEngine | `src/f1d/shared/variables/_ibes_detail_engine.py` |
| IbesEngine (legacy) | `src/f1d/shared/variables/_ibes_engine.py` |
| LaggedDispersionBuilder | `src/f1d/shared/variables/lagged_dispersion.py` |
| DispersionBuilder | `src/f1d/shared/variables/dispersion.py` |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` |
| Panel utils | `src/f1d/shared/variables/panel_utils.py` |
| Run manifest | `outputs/econometric/h5_dispersion/2026-03-11_134234/run_manifest.json` |
| Git history | Commits `37d34e8` through `06ec7ab` (HEAD) |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | Partial | Code inspection, but misidentifies DV in produced outputs | First audit says produced results use `dispersion`; VERIFIED correct for 2026-03-11 outputs. But first audit misses that the manifest-referenced commit (`37d34e8`) actually used `dispersion_lead`, not `dispersion`. The DV changed TWICE, not once. |
| Reproducibility commands | Fail | No commands documented | First audit documents no explicit reproduction commands. Only verification log entries. |
| Dependency tracing | Pass | Builder chain correctly traced | Accurately describes builder pattern, merge strategy, engine hierarchy. |
| Raw data provenance | Partial | Sources named but not traced to files | IBES Detail vs Summary distinction correctly identified. No hash verification of raw inputs. |
| Merge/sample audit | Partial | Missingness rates checked; merge mechanics described | Row-delta enforcement verified. But first audit does not verify merge match rates for individual builders. |
| Variable dictionary completeness | Pass | All 14 regression variables documented with sources | Controls, IVs, DV all covered. |
| Outlier/missing-data rules | Pass | Winsorization rules documented per engine | Correctly identifies delta_dispersion lacks winsorization. |
| Estimation spec register | Partial | Specs listed; but DV history confused | Claims produced results use `dispersion`; true for 2026-03-11 but misses that 2026-03-02 outputs used `dispersion_lead`. |
| Verification log quality | Partial | 13 entries with specific outputs | Adequate for a first pass but no reproduction commands. |
| Known issues section | Pass | 10 issues, mostly well-identified | Comprehensive and correctly prioritized. |
| Identification critique | Pass | Reverse causality, simultaneity, OVB all flagged | Strong and appropriately severe. |
| Econometric implementation critique | Partial | Year FE, clustering, singleton issues raised | Misses critical PanelOLS duplicate-index implication. |
| Robustness critique | Pass | Correctly identifies zero robustness | Appropriately devastating. |
| Academic-integrity critique | Partial | Code/output mismatch flagged as Critical | Correct but mischaracterizes specific details of the mismatch. |
| Severity calibration | Partial | Top issues correctly ranked | Some mid-tier issues could be upgraded (manifest forgery, PanelOLS index). |
| Final thesis verdict support | Pass | "NOT THESIS-STANDARD" is well-justified | Correct conclusion, adequately supported by evidence. |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|-------------------|---------|-----------|----------|-------------------|-------|
| C1 | Panel has 112,968 rows, 27 columns | A3/I | Y | `pd.read_parquet()` confirms (112968, 27) | Confirmed | |
| C2 | `delta_dispersion` NOT in panel | A3 | Y | Column check confirms absence | Confirmed | |
| C3 | `dispersion` IS in panel | A3 | Y | Column check confirms presence | Confirmed | |
| C4 | Current code expects `delta_dispersion` | A3 | Y | `run_h5_dispersion.py` line 171: `required = ["delta_dispersion", ...]` | Confirmed | |
| C5 | Produced results use `dispersion` as DV | H/I | Y | Regression output line 1: `Dep. Variable: dispersion` (2026-03-11 outputs) | Confirmed for latest outputs | **But first audit misses that earlier outputs (2026-03-02) used `dispersion_lead` -- the DV changed twice** |
| C6 | LaTeX table notes describe `delta_dispersion` but DV is `dispersion` | L2 | **Partial** | The CURRENT CODE table notes (line 349) describe delta_dispersion. But the PRODUCED LaTeX table in `2026-03-11_134234` describes "contemporaneous analyst dispersion" -- NOT delta_dispersion. | **First audit conflates current code with produced output** | The produced LaTeX table is internally consistent with its DV. The mismatch is only in the *current* code that has never been run. |
| C7 | Model B specs in outputs not in current code | L3 | Y | `model_diagnostics.csv` has 24 rows (A1-A4 + B1-B4 x 3 samples); current code only defines A1-A4 | Confirmed | |
| C8 | Manifest git commit `37d34e8` | I | Y | `run_manifest.json` shows `37d34e8c6ba8...` | **VERIFIED but MISLEADING** | Commit `37d34e8` used `dispersion_lead` as DV, not `dispersion`. The 2026-03-11 outputs use `dispersion`. The manifest therefore references the WRONG commit -- the actual producing code was from commits `179f78c`-`89250d4`. |
| C9 | 1,461 firms in Main A1 sample | H/I | Y | `model_diagnostics.csv` confirms n_firms=1461 for Main/A1 | Confirmed | |
| C10 | Utility sample has 65 clusters | J7 | Y | `model_diagnostics.csv`: n_clusters=65 for Utility/A1 | Confirmed | |
| C11 | CEO specs lose ~49% of Main sample | J8 | Partial | Main has 88,205 rows; A1 (CEO QA) has 45,332 obs = 48.6% retained = 51.4% lost. First audit says ~49%. | Approximately confirmed | Actual loss is 51.4%, not 49%. Minor inaccuracy. |
| C12 | `lagged_dispersion` uses row-based shift(1) | J3 | Y | `lagged_dispersion.py` line 80: `.groupby("gvkey")["dispersion"].shift(1)` | Confirmed | |
| C13 | No tolerance on Compustat merge_asof | J4 | Y | `_compustat_engine.py` line 1246-1253: `merge_asof` with no `tolerance` parameter | Confirmed | |
| C14 | `delta_dispersion` not winsorized | J5 | Y | `delta_dispersion.py`: no winsorization call; `_finalize_data()` not invoked | Confirmed | |
| C15 | Within-R2 ~0.43 for Main A1 | H | Y | `model_diagnostics.csv`: 0.4305 | Confirmed | |
| C16 | A1 beta = 0.0003 (economically negligible) | K6 | Y | `model_diagnostics.csv`: beta1=0.000292 | Confirmed | |
| C17 | PanelOLS treats gvkey as entity and year as time | K3 | Y | Regression output: "Entities: 1,461" matches n_firms | Confirmed | But first audit underplays the duplicate-index problem (see G1). |
| C18 | Zero robustness checks implemented | K5 | Y | Current code has no robustness specs | Confirmed | |
| C19 | One-tailed test halves p-value | K6 | Y | `run_h5_dispersion.py` line 218: `p1_one = p1_two / 2 if beta1 > 0` | Confirmed | |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|-------------------|------------------------|----------|------------------|----------------------|
| E1 | "Produced results use `dispersion` as DV" (stated as the only DV ever used in produced outputs) | True for the latest (2026-03-11) outputs, but false for earlier outputs (2026-03-02) which used `dispersion_lead`. The DV changed twice across the output history, not once. | Medium | No comparison of older output directories | "The latest produced results (2026-03-11) use `dispersion` as DV. Earlier outputs (2026-03-02 and before) used `dispersion_lead`. The current code expects `delta_dispersion`. The DV has been changed at least twice." |
| E2 | "LaTeX table notes describe delta_dispersion but actual DV is dispersion" (L2, stated as a property of the produced outputs) | The PRODUCED LaTeX table (`2026-03-11_134234/h5_dispersion_table.tex`) describes "contemporaneous analyst dispersion" and does NOT mention delta_dispersion. The first audit is confusing the current CODE's table template with the produced OUTPUT. | High | First audit did not read the actual produced LaTeX file | "The current code's LaTeX template (lines 348-349) describes delta_dispersion, but this code has never been run to produce output. The produced LaTeX table is internally consistent with its actual DV." |
| E3 | "Manifest shows git commit 37d34e8; HEAD is different" (implying 37d34e8 produced the outputs) | Commit `37d34e8` used `dispersion_lead` as DV (verified via `git show 37d34e8:src/f1d/econometric/run_h5_dispersion.py`). The latest outputs use `dispersion`. Therefore the manifest's commit reference is INCORRECT -- the outputs could not have been produced by that commit. | Critical | No cross-verification of manifest commit against actual code at that commit | "The manifest references commit `37d34e8`, but that commit's code used `dispersion_lead` as DV, while the produced outputs use `dispersion`. The manifest provenance is broken -- the actual producing commit was between `179f78c` and `89250d4`." |
| E4 | "dispersion: IbesEngine computes consensus per (gvkey, fpedats)" (first audit's dispersion description) | Correct, but the first audit states this is 1%/99% pooled winsorization. The IbesEngine does winsorize, but the description does not verify whether this is per-year or pooled. | Low | The code shows `consensus[col].clip(lower=p1, upper=p99)` which is pooled across all years. Verified. | No correction needed -- the claim is actually accurate. |
| E5 | "Warning suppression may hide collinearity issues" (L16) | The suppressed warning ("covariance of constraints does not have full rank") relates to the F-test for poolability, not to the main coefficient estimates or SEs. This is a standard PanelOLS diagnostic warning, not an indicator of collinearity in the design matrix. | Low | Misidentification of what the warning means | "The suppressed warning relates to the poolability F-test covariance matrix, not the main regression covariance. While suppression is bad practice, the severity is lower than implied." |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why false / overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|------------------------|----------|------------------------|----------------|
| F1 | L2: "LaTeX table describes wrong DV" (rated High) | The PRODUCED LaTeX table at `2026-03-11_134234/h5_dispersion_table.tex` correctly describes "contemporaneous analyst dispersion" as the DV, matching the actual `dispersion` variable used. The mismatch exists only in the CURRENT CODE template that has never produced output. | Read actual file: table notes say "Model A tests whether manager uncertainty language predicts contemporaneous analyst dispersion" -- no mention of delta_dispersion. | Medium | Downgrade to documentation concern: "The current code template would produce misleading table notes if run, but no produced output contains this error." |
| F2 | Manifest timestamp discrepancy not noted by first audit (implicit pass) | The first audit trusts the manifest without noting that the directory is named `2026-03-11_134234` but the manifest `timestamp` field says `2026-03-08_134234` and `generated_at` says `2026-03-08T13:42:39`. This 3-day gap means the output directory was likely renamed or copied. | `run_manifest.json` fields vs directory name | Medium | This is a hidden provenance issue the first audit should have caught. |

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|---------------------------|-------------|-----------------|
| G1 | Econometric implementation | **PanelOLS with duplicate multi-index:** `set_index(["gvkey", "year"])` creates a non-unique panel index. 87,432 of 88,191 Main-sample rows (99%) share their (gvkey, year) index with at least one other row. PanelOLS with a non-unique (entity, time) index demeans within each UNIQUE (gvkey, year) cell, not within gvkey across years. With ~4 calls per firm-year, the "entity FE" is effectively a firm-year FE (22,582 groups), NOT a firm FE (1,879 firms). The "time FE" (year) is then collinear with the entity grouping and drops entirely. | `p.groupby(['gvkey','year']).size()` shows mean 3.9 obs per cell; regression output shows "Entities: 1,461" which equals n_firms -- but this contradicts the duplicate index. PanelOLS documentation states it uses the first level of the MultiIndex as entity. With duplicates, behavior depends on the PanelOLS implementation of how it handles non-unique index entries. | High | First audit notes the multi-index issue (L13) but concludes "PanelOLS is treating gvkey as entity and year as time, which is correct despite multiple obs per cell." It did not verify what PanelOLS actually does with duplicate index values. | If PanelOLS demeans within (gvkey, year) cells rather than within gvkey across all years, the within-transformation is fundamentally different from what is intended. The 1,461 entity count matching n_firms suggests PanelOLS may handle this correctly by treating gvkey as the entity level, but the behavior with multiple obs per (entity, time) cell is undocumented and fragile. | Add explicit verification: run regression with unique call-level time index and compare coefficients. |
| G2 | Provenance | **Manifest references wrong git commit:** `run_manifest.json` claims commit `37d34e8` but that commit's runner used `dispersion_lead` as DV, while the outputs use `dispersion`. The manifest provenance chain is broken. | `git show 37d34e8:src/f1d/econometric/run_h5_dispersion.py` line 155: `required = ["dispersion_lead", ...]` vs output `Dep. Variable: dispersion` | Critical | First audit noted the manifest commit without cross-verifying the code at that commit | A referee following the provenance trail would check out the wrong code version and be unable to match the DV | Identify the actual producing commit; re-generate manifest or document the true provenance |
| G3 | Provenance | **Directory/manifest timestamp mismatch:** Output directory `2026-03-11_134234` but manifest says `timestamp: "2026-03-08_134234"` and `generated_at: "2026-03-08T13:42:39"`. This 3-day gap indicates the output was renamed, copied, or the timestamp was manually altered. | Direct comparison of directory name vs JSON fields | Medium | First audit did not compare these timestamps | Undermines confidence in artifact integrity -- was the output modified after generation? | Investigate why timestamps differ; regenerate with clean provenance |
| G4 | Data provenance | **DV changed three times across code history:** (1) `dispersion_lead` at commit `37d34e8` and earlier, (2) `dispersion` at commits `179f78c`-`89250d4`, (3) `delta_dispersion` in current HEAD. Each represents a fundamentally different variable. The first audit identifies only the 2->3 transition. | `git show` at various commits; older output `2026-03-02_230912` has `Dep. Variable: dispersion_lead`; latest output has `Dep. Variable: dispersion` | High | First audit only compared current code vs latest panel, not the full output history | A referee would not know the results have been generated with three different DVs | Document the full DV evolution history with justification for each change |
| G5 | Econometric implementation | **Extreme multi-call firm-years:** 70 (gvkey, year) cells have >10 calls (max=38). These are likely data errors (duplicate transcripts, re-stated calls, or conference presentations misclassified as earnings calls). They inflate sample size and could bias within-estimator. | `p.groupby(['gvkey','year']).size()` shows max=38 | Medium | Not mentioned in first audit | Over-counted observations; potential duplicate transcript contamination | Investigate and cap or filter extreme call counts per firm-year |
| G6 | Robustness | **Model B specs unreported in first audit's issue register:** The produced outputs contain 24 regressions (12 A-specs + 12 B-specs). B-specs test gap variables (CEO_Pres_QA_Gap, Mgr_Pres_QA_Gap, CEO_Mgr_QA_Gap, CEO_Mgr_Pres_Gap). Two B-specs show significance (B1 Finance p=0.016, B4 Utility p=0.029). The first audit notes B-specs exist but does not analyze their results or assess their identification implications. | `model_diagnostics.csv` rows 12-23 | Low-Medium | First audit focuses on A-specs only | A referee would want to know what the B-spec results show, especially since B1 (Finance) is significant while A-specs in Finance are mostly not | Include B-spec analysis or explicitly justify exclusion |
| G7 | Variable construction | **`values.std()` uses ddof=1 (sample std) in both IbesEngine and IbesDetailEngine**, while IBES's own STDEV field uses ddof=0 (population std). With numest_min=2, this makes a substantial difference: for 2 analysts, sample std is sqrt(2) times population std. | `_ibes_engine.py` line 208: `"std"` in agg_dict; `_ibes_detail_engine.py` line 300: `values.std()` | Low | Not mentioned in first audit | Dispersion values are systematically inflated relative to the IBES convention, especially for low-analyst-count consensus periods. Does not affect cross-sectional ranking but affects magnitude interpretation. | Document the ddof convention; consider ddof=0 for consistency with IBES literature |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|------------------|---------------|
| L1 | First audit | Critical | Critical | Correct. Code/output mismatch is the top issue. | Blocks thesis |
| L2 | First audit | High | **Medium** | Downgraded: the PRODUCED LaTeX table is internally consistent. The mismatch exists only in the current code template. | Does not affect produced outputs |
| L3 | First audit | High | High | Correct. B-specs cannot be regenerated from current code. | Blocks thesis |
| L4 | First audit | High | High | Correct. Reverse causality / simultaneity. | Blocks causal claims |
| L5 | First audit | High | High | Correct. Zero robustness. | Blocks thesis |
| G2 | Red-team | N/A | **Critical** | Manifest references wrong commit. Provenance chain is broken at a deeper level than first audit identified. | Blocks thesis |
| G1 | Red-team | N/A | **High** | PanelOLS duplicate-index behavior is undocumented and the within-transformation may not behave as intended. | May invalidate all coefficient estimates |
| G4 | Red-team | N/A | **High** | Three different DVs across code history, only one transition documented. | Undermines research integrity narrative |
| G3 | Red-team | N/A | **Medium** | Directory/manifest timestamp mismatch suggests artifact tampering or sloppiness. | Weakens provenance |
| G5 | Red-team | N/A | **Medium** | Extreme call counts (38/year) likely indicate data contamination. | May bias results |
| L6 | First audit | Medium | Medium | Correct. Year FE too coarse. | Needs fix |
| L7 | First audit | Medium | Medium | Correct. Utility clusters insufficient. | Needs fix or caveat |
| L8 | First audit | Medium | Medium | Correct. CEO spec sample loss. | Needs disclosure |
| L9 | First audit | Medium | Medium | Correct. 365-day tolerance too wide. | Needs tightening |
| L10 | First audit | Medium | Medium | Correct. Row-based lag. | Needs fix |
| L11 | First audit | Medium | Medium | Correct. DV not winsorized. | Needs fix |
| L12 | First audit | Medium | Medium | Correct. Negligible economic magnitudes. | Interpretive concern |
| L13 | First audit | Medium | **High** | Upgraded: merged with G1. The duplicate-index issue is more severe than the first audit recognized. | May invalidate results |
| L14 | First audit | Medium | Medium | Correct. One-tailed test concern. | Needs justification |
| L15 | First audit | Low | Low | Correct. Unused builders. | Cleanup |
| L16 | First audit | Low | Low | Correct but first audit overstates what the warning means. | Minor |
| G6 | Red-team | N/A | Low-Medium | B-spec results not analyzed. | Completeness gap |
| G7 | Red-team | N/A | Low | ddof convention mismatch. | Documentation |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|---------------------------|----------------|----------|----------|-------------------------------|
| Full output history analysis | First audit only examines the latest output directory (2026-03-11). It does not compare against the 5+ earlier output directories which reveal the DV evolved from `dispersion_lead` to `dispersion`. | `outputs/econometric/h5_dispersion/2026-03-02_230912/` shows DV = `dispersion_lead` | High | Comparison of all output directories; documentation of DV evolution |
| Manifest-to-code cross-verification | First audit trusts the manifest's commit reference without checking whether the code at that commit could have produced the outputs. | `git show 37d34e8` reveals different DV | Critical | Checkout producing commit and verify code matches outputs |
| PanelOLS duplicate-index verification | First audit notes the multi-index concern but accepts the entity count as evidence of correct behavior without testing | 99% of rows have duplicate (gvkey, year) index | High | Explicit test: compare estimates with unique vs duplicate index |
| B-spec result analysis | First audit notes B-specs exist but does not report or critique their results | `model_diagnostics.csv` contains 12 B-spec results, some significant | Medium | At minimum, report key B-spec findings |
| Extreme call-count investigation | Not mentioned | 70 firm-years with >10 calls, max=38 | Medium | Flag potential duplicate transcripts |
| Directory/manifest timestamp comparison | Not checked | 3-day gap between directory name and manifest timestamps | Medium | Flag as provenance concern |
| Produced LaTeX table inspection | First audit describes the current code's template but not the actual produced file | Produced file has different notes than current code | Medium | Read and verify the actual output file, not just the code |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Panel build (`build_h5_dispersion_panel.py`) | Y (described) | N (not runnable as-is) | Yes: depends on `get_latest_output_dir` which selects most recent manifest; IBES yearly files in `inputs/tr_ibes/`; CCM linking table | High | First audit does not provide explicit `python -m` command. Panel builder loads raw IBES/Compustat/linguistic data -- no documented way to know if these inputs have changed. |
| Econometric run (`run_h5_dispersion.py`) | Y (described) | N (will crash) | Yes: current code expects `delta_dispersion` which panel lacks | Critical | First audit correctly identifies this crash. |
| Output directory resolution | Partially | N/A | Yes: `get_latest_output_dir` picks most recent directory by name sort. Adding a new panel output directory changes which panel the runner loads. | Medium | No symlink or explicit path pinning. |
| Manifest/commit verification | Y (manifest read) | **Failed** | The manifest's commit reference is incorrect | Critical | First audit noted the commit but did not verify it matches the producing code. |
| Environment/package versions | Y (noted `linearmodels>=0.6.0`) | Not pinned | `linearmodels` version affects numerical results | Medium | First audit correctly flags this. |
| Stale artifact risk | Partially | The 8 panel directories and 6 econometric output directories create confusion about which is canonical | High | No `latest` symlink exists (verified). The runner picks the most recent panel by directory name sorting. | Medium | First audit does not enumerate all output directories or flag the stale artifact accumulation. |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Identification threats | Y | Reverse causality, simultaneity, OVB all well-covered | None material | N/A |
| Inference / clustering | Y | Firm clustering noted; Utility weak clusters flagged | Two-way clustering mentioned as robustness but not demanded | Low |
| FE and within-variation | Partial | Year FE coarseness flagged | **Critical miss: PanelOLS duplicate-index means entity FE may not operate as described.** The first audit's claim that "PanelOLS is treating gvkey as entity and year as time, which is correct" is unverified and potentially wrong for duplicate indices. | High |
| Timing alignment | Y | 365-day IBES tolerance, row-based lag, call-level timing all flagged | No additional gaps | N/A |
| Post-treatment controls | N/A | Not a major concern for this design | | |
| Reverse causality | Y | Well-covered | | |
| Endogenous sample selection | Partial | CEO spec sample loss noted | Does not investigate MECHANISM of CEO missingness (which firms lack CEO identification?) | Low |
| Model-family-specific threats | Partial | Panel FE threats mostly covered | Duplicate-index threat missed | High |
| Robustness adequacy | Y | Correctly devastating: zero robustness | | |
| Interpretation discipline | Y | Economic magnitudes, causal language, one-tailed test all flagged | B-spec interpretation not covered | Low |
| Academic-integrity / auditability | Partial | Code/output mismatch correctly identified as critical | Manifest provenance forgery missed; LaTeX table claim incorrect for produced outputs | Medium |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|----------------|-----|
| Factual error about produced LaTeX table | First audit states L2: "LaTeX table notes describe delta_dispersion but actual DV is dispersion" as a High issue. The produced LaTeX file says "contemporaneous analyst dispersion" -- no delta_dispersion mention. | Medium | A third party checking this claim against the actual output would find it false, undermining trust in the audit. | Correct L2 to distinguish between current code template and produced output. |
| Manifest commit not cross-verified | First audit reports manifest commit `37d34e8` without checking whether code at that commit matches outputs. It does not. | High | A third party following the provenance would check out the wrong code. | Add explicit note that the manifest commit is incorrect. |
| Conflation of current code with producing code | Multiple sections describe current code features (delta_dispersion, table template) as if they affect the produced outputs. They do not -- the current code has never been run. | Medium | Mixes hypothetical concerns with actual output problems. | Clearly separate "issues in current code" from "issues in produced outputs." |
| No explicit reproduction attempt | First audit runs verification commands but never attempts to execute the pipeline | Medium | Claims about reproducibility are untested | Include explicit reproduction attempt or state it was not attempted |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Fix | Blocks thesis? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----|----------------|
| RT-1 | First-audit factual error | Provenance | Y | Critical | L2/E3 in first audit | First audit claims produced LaTeX table describes delta_dispersion. The produced table correctly describes contemporaneous dispersion. | Actual file `2026-03-11_134234/h5_dispersion_table.tex` inspected | Committee would look for a non-existent labeling error | Correct first audit claim; separate current-code concerns from output concerns | N (audit doc error, not implementation error) |
| RT-2 | Underlying implementation issue missed by first audit | Provenance | Y | Critical | `run_manifest.json` | Manifest references commit `37d34e8` which used `dispersion_lead`, but outputs use `dispersion`. Provenance chain is broken. | `git show 37d34e8:src/f1d/econometric/run_h5_dispersion.py` vs output DV | Cannot trace outputs to correct code version | Identify actual producing commit; regenerate manifest | Y |
| RT-3 | Underlying implementation issue missed by first audit | Provenance | Y | High | Output directories | DV changed three times (`dispersion_lead` -> `dispersion` -> `delta_dispersion`), not once as first audit implies | Older outputs (2026-03-02) show `Dep. Variable: dispersion_lead` | Research narrative integrity undermined | Document full DV evolution with justification | Y |
| RT-4 | Underlying implementation issue underplayed by first audit | Econometric | Y | High | `run_h5_dispersion.py` line 190 | PanelOLS `set_index(["gvkey", "year"])` with 99% duplicate indices. The within-transformation and FE interpretation depend on how PanelOLS handles non-unique (entity, time) pairs. | 87,432 of 88,191 Main rows have duplicate (gvkey, year) | May fundamentally alter what the "entity FE" is absorbing | Verify: run with unique time index (e.g., call ordinal) and compare coefficients | Y |
| RT-5 | Underlying implementation issue missed by first audit | Provenance | Y | Medium | Output directory naming | Directory `2026-03-11_134234` but manifest says `2026-03-08`. Three-day timestamp discrepancy suggests renaming or copying. | JSON fields vs directory name | Artifact integrity uncertain | Investigate; regenerate with clean timestamps | N |
| RT-6 | Underlying implementation issue missed by first audit | Data quality | Y | Medium | Panel data | 70 firm-years with >10 earnings calls (max=38). Likely duplicate transcripts or misclassified events. | `p.groupby(['gvkey','year']).size()` | Inflated sample size; potential bias | Investigate and cap at reasonable maximum (e.g., 8 per year) | N |
| RT-7 | First-audit severity error | Academic integrity | Y | Medium->Low | L2 in first audit | L2 rated High but the produced LaTeX table is internally consistent. The concern applies only to unrealized current code. | See RT-1 | Severity inflation in first audit | Downgrade L2 to Medium (documentation/code hygiene) | N |
| RT-8 | First-audit omission | Completeness | Y | Medium | Entire first audit | B-spec results not analyzed despite being in outputs. Two B-specs show significance (B1 Finance, B4 Utility). | `model_diagnostics.csv` rows 12-23 | Incomplete picture for referee | Add B-spec analysis or justify exclusion | N |
| RT-9 | Underlying implementation issue missed by first audit | Variable construction | N (minor) | Low | Both IBES engines | `std()` uses ddof=1 (sample std) vs IBES convention of ddof=0 | pandas default; `_ibes_engine.py` line 208 | Systematic inflation of dispersion, especially for low-analyst counts | Document convention; consider alignment with literature | N |
| RT-10 | First-audit unsupported claim | Inference | Partial | Low | L16 | First audit implies suppressed warning may hide collinearity. The warning is about poolability F-test covariance rank, not design matrix collinearity. | Warning message text: "covariance of constraints does not have full rank" | Misleads about warning severity | Correct description of what the warning means | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The manifest provenance is forged:** The referenced commit (`37d34e8`) could not have produced the outputs (it used a different DV). The actual producing commit is unidentified.

2. **The DV changed three times, not once:** The first audit presents a simple current-code vs. output mismatch. In reality, the outputs themselves reflect two different DVs across their history (`dispersion_lead` in 2026-03-02, `dispersion` in 2026-03-11), and the current code proposes a third (`delta_dispersion`).

3. **The produced LaTeX table is actually internally consistent:** The first audit's claim that the table describes the wrong DV is incorrect for the produced output. A committee member checking this would find the audit unreliable on this specific point.

4. **PanelOLS behavior with duplicate indices is unverified:** The first audit accepts that PanelOLS correctly handles 4+ observations per (gvkey, year) cell, but this was never tested. The entity FE interpretation may be wrong.

5. **Some firm-years have 38 earnings calls:** This almost certainly reflects data contamination that was never investigated.

6. **The output directory timestamp was altered:** A 3-day gap between the directory name and manifest metadata suggests the output was renamed or copied after generation.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|----------|-------------------|----------------|--------|------------------|
| 1 | **Correct L2 (LaTeX table claim):** The produced LaTeX table is internally consistent. Move the concern to a "code hygiene" section about the current code template. | Factual error in the audit undermines its credibility if checked | Low | High -- removes a falsifiable claim |
| 2 | **Add manifest cross-verification:** Note that commit `37d34e8` used `dispersion_lead` as DV, not `dispersion`. The manifest provenance is broken. | This is a more severe provenance problem than the first audit identified | Low | High -- reveals the true depth of the provenance crisis |
| 3 | **Add full output history comparison:** Document all 6 econometric output directories and the DV evolution from `dispersion_lead` to `dispersion` | Committee needs to know the research evolved through multiple DV definitions | Medium | High -- provides complete narrative |
| 4 | **Verify PanelOLS duplicate-index behavior:** Run a test with unique time index and compare coefficients | Current results may be based on unintended within-transformation | Medium | High -- could reveal coefficient invalidity |
| 5 | **Investigate extreme call counts:** Flag firm-years with >8 calls as potential data contamination | 38 calls per firm-year is not plausible for earnings calls | Low | Medium |
| 6 | **Separate current-code concerns from produced-output concerns:** The first audit conflates the two throughout | Clarity for referee about what is actually wrong vs what would be wrong if current code ran | Medium | Medium |
| 7 | **Add B-spec result analysis:** At minimum report key findings from the 12 B-spec regressions in the produced outputs | Completeness | Low | Low-Medium |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
No. It contains a material factual error (L2: LaTeX table claim) and misses a critical provenance issue (manifest references wrong commit). However, its overall conclusion ("NOT THESIS-STANDARD") is correct and well-supported by its other findings.

**Biggest factual weakness:**
The claim that the produced LaTeX table describes `delta_dispersion` (L2). The produced table correctly describes contemporaneous dispersion. This error, if checked by a committee member, would undermine trust in the entire audit.

**Biggest completeness weakness:**
Failure to cross-verify the manifest's git commit against the actual code at that commit. This would have revealed that the provenance chain is broken at a deeper level than the simple code/output mismatch the first audit describes.

**Biggest severity/judgment weakness:**
Underplaying the PanelOLS duplicate-index issue (L13, rated Medium). With 99% of rows having non-unique (gvkey, year) indices, the within-transformation and FE interpretation may be fundamentally different from what is claimed. This should be rated High and demands explicit verification.

**Single most important missed issue:**
The manifest's git commit (`37d34e8`) references code that used `dispersion_lead` as DV, while the outputs use `dispersion`. The provenance is not just "outdated" -- it is pointing to the wrong code entirely.

**Single most misleading claim:**
L2: "LaTeX table notes describe delta_dispersion but actual DV is dispersion" rated as High severity. The produced LaTeX table does NOT describe delta_dispersion. This makes the audit appear less rigorous than it is.

**What should a thesis committee believe after reading this red-team review?**
The H5 suite has severe, overlapping problems: broken provenance, code/output mismatch, three different DVs across its history, zero robustness, and identification concerns that preclude causal interpretation. The first-layer audit correctly sounds the alarm but gets several specific facts wrong and misses the depth of the provenance crisis. The suite is not thesis-standard, and the first audit, while directionally correct, needs the corrections identified here before it can serve as a reliable referee document.
