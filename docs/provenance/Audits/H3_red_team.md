# H3 Suite: Second-Layer Red-Team Audit

**Suite ID:** H3 -- Payout Policy
**Red-team date:** 2026-03-15
**First-layer audit date:** 2026-02-28 / 2026-03-15 (two versions concatenated)
**Auditor posture:** Adversarial, independent, fresh-context

---

## A. Red-Team Bottom Line

The first-layer audit document for H3 is structurally unusual: it contains **two separate audits concatenated into one file**, an older version (sections A-J, dated 2026-02-28) and a newer version (sections A-N, dated 2026-03-15). These two versions contradict each other on critical facts -- the older version references verified regression results from run 2026-02-27_223841 with within-R^2 of 0.18-0.91 and 1/36 significant, while the newer version claims "no regression output exists." In reality, archived econometric outputs exist (15 timestamped runs in `outputs/econometric/_archived/h3_payout_policy/`), with the latest (2026-03-07_230800) showing dramatically different within-R^2 values (0.01-0.11) and 5/36 significant tests. The newer audit version failed to discover these archived outputs, making its "Critical" severity rating on missing output incorrect.

The newer audit version is substantially more thorough than the older one and identifies several genuine issues (false standardization claim, is_div_payer_5yr docstring mismatch, missing robustness). However, it missed or underplayed several material issues: (1) payout_flexibility_lead is effectively a discrete variable with only 11 unique values, 46% at zero, making OLS problematic; (2) 39% of firms have zero within-firm variation in payout_flexibility_lead, meaning firm FE absorbs all their information; (3) only 28.5% of total payout_flexibility_lead variance is within-firm; (4) Compustat H3-specific variables (div_stability, payout_flexibility, etc.) are NOT in the inf-to-NaN ratio_cols cleanup, relying solely on the regression script's replace(); (5) the two-audit concatenation creates an internally contradictory document.

**Overall grade for first-layer audit: PARTIALLY RELIABLE**

The newer version is useful for identifying surface-level implementation issues but misses deeper econometric concerns about DV distributional properties and contains a critical factual error about output existence.

**Suite as implemented: SALVAGEABLE WITH MAJOR REVISIONS**

**Risk assessment:** The first audit **mixed both** -- it understated econometric risk (DV distributional properties, within-variation exhaustion) while overstating the reproducibility risk (claiming no output exists when archived runs are available).

---

## B. Scope and Objects Audited

| Item | Path/Description |
|------|-----------------|
| Suite ID | H3 -- Payout Policy |
| Suite entrypoint | `src/f1d/econometric/run_h3_payout_policy.py` (601 lines) |
| Panel builder | `src/f1d/variables/build_h3_payout_policy_panel.py` (352 lines) |
| First-layer audit | `docs/provenance/H3.md` (two versions concatenated, ~988 lines) |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` (lines 764-938 for H3, lines 1020-1161 for winsorization) |
| Panel utils | `src/f1d/shared/variables/panel_utils.py` (193 lines) |
| Linguistic engine | `src/f1d/shared/variables/_linguistic_engine.py` (lines 240-260 for winsorization) |
| is_div_payer_5yr builder | `src/f1d/shared/variables/is_div_payer_5yr.py` (52 lines) |
| Panel artifact (latest) | `outputs/variables/h3_payout_policy/2026-03-02_224406/h3_payout_policy_panel.parquet` |
| Archived econometric output (latest) | `outputs/econometric/_archived/h3_payout_policy/2026-03-07_230800/` |
| Archived econometric output (old) | `outputs/econometric/_archived/h3_payout_policy/2026-02-27_223841/` |
| Run manifest | `outputs/econometric/_archived/h3_payout_policy/2026-03-07_230800/run_manifest.json` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|---------------|---------------|
| Model/spec identification | Pass | Both versions correctly identify PanelOLS, 2 DVs x 6 measures x 3 samples = 36 models | Verified: formula, estimator, clustering all correctly described |
| Reproducibility commands | Partial | Newer version provides correct commands; older version more complete with upstream stages | Newer version omits Stage 1-2 prerequisites; no versioning of which panel artifact to use |
| Dependency tracing | Pass | Newer version traces Compustat engine, linguistic engine, panel builders, and lead construction | Verified: all material code paths documented |
| Raw data provenance | Pass | Both versions document Compustat (956,229 rows), manifest (112,968 rows) | Verified: counts match |
| Merge/sample audit | Partial | Newer version provides stepwise attrition; older version gives ranges | Neither version documents that the min-calls filter is applied AFTER the div-payer filter and sample split, not before |
| Variable dictionary completeness | Pass | Both versions cover all 16 regression variables + FE identifiers | Verified: all variables in CONFIG and CONTROL_VARS accounted for |
| Outlier/missing-data rules | Partial | Winsorization documented but H3-specific inf-to-NaN gap not flagged | H3 vars (div_stability, etc.) are NOT in the `ratio_cols` list for inf replacement at engine level |
| Estimation spec register | Pass | Full 36-model grid documented in both versions | Verified |
| Verification log quality | Fail | Newer version claims "no regression output exists" -- this is factually wrong | 15 archived runs exist; the latest (2026-03-07) used the same panel artifact |
| Known issues section | Partial | Newer version identifies 16 issues, many genuine; older version identifies 6 | Several material issues missed (see Section G) |
| Identification critique | Pass | Newer version covers reverse causality, OVB, endogenous selection, look-ahead bias | Thorough but underweights the DV distributional issue |
| Econometric implementation critique | Partial | Calendar year vs fiscal quarter FE noted; standardization claim flagged | Misses: payout_flexibility_lead is effectively discrete (11 values); massive zero-inflation |
| Robustness critique | Pass | Both versions correctly flag zero robustness tests as critical | Verified: no alt specs, no placebo, no alt clustering in codebase |
| Academic-integrity critique | Partial | False standardization claim and docstring errors flagged | Underweights the contradictory first-audit itself as an integrity risk |
| Severity calibration | Partial | Most severities reasonable; "Critical" on missing output is wrong | Archived outputs exist; severity should be "Low" (organizational, not missing) |
| Final thesis verdict support | Pass | "SALVAGEABLE WITH MAJOR REVISIONS" is appropriate | Agree, but for partly different reasons |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|------------------|---------|-----------|----------|-----------------|-------|
| C01 | Panel has 112,968 rows, 31 columns, file_name unique | A/D | Y | `pd.read_parquet()` confirms 112,968 rows, 31 cols, 112,968 unique file_name | Correct | |
| C02 | Sample split: Main 88,205 / Finance 20,482 / Utility 4,281 | E | Y | `value_counts()` confirms | Correct | |
| C03 | 36 PanelOLS models run | H | Y | model_diagnostics.csv (latest archived) has 36 rows | Correct | |
| C04 | No regression output exists (newer version, I-03) | J | **N** | 15 archived timestamped runs in `outputs/econometric/_archived/h3_payout_policy/`; latest 2026-03-07_230800 has 36 regression files, diagnostics, table | **FALSE** | The newer audit checked `outputs/econometric/h3_payout_policy/` but not `_archived/` |
| C05 | Within-R^2 0.176-0.497 for div_stability (older version) | H (v1) | **Partial** | Old run (2026-02-27) shows these values but newer run (2026-03-07) shows 0.015-0.058 | **Stale** | Older version based on a run that used a different R^2 calculation or different code version |
| C06 | Within-R^2 0.818-0.909 for payout_flexibility (older version) | H (v1) | **Partial** | Old run confirms; new run shows 0.011-0.110 | **Stale** | Same issue; dramatic change indicates code-level changes between runs |
| C07 | 1/36 significant (older version) | H (v1) | **N** | Latest run (2026-03-07) shows 5/36 significant (all Finance payout_flex) | **Stale** | Old run had 1/36; evidence has changed |
| C08 | Table note falsely claims standardized controls | J-01 | Y | Line 407 of `run_h3_payout_policy.py`: "All continuous controls are standardized." No standardization code in file. | Correct | Verified via grep |
| C09 | is_div_payer_5yr uses rolling max not min | J-02/I-02 | Y | `_compustat_engine.py` line 897-901: `.rolling("1826D", min_periods=1).max()` | Correct | Docstring at `is_div_payer_5yr.py` line 6-7 says "each of the previous 5 years" |
| C10 | firm_maturity docstring says RE/TE, code computes RE/AT | J-02/I-05 | Y | Line 775: "RE / TE"; line 839-841: `req / atq` | Correct | |
| C11 | Lev uses fillna(0) creating false zeros | I-07 | Y | Line 1032: `dlcq.fillna(0) + dlttq.fillna(0)` | Correct | 14,156 Lev=0 rows (12.5%), 4,258 among div payers |
| C12 | CEO_QA measures 32% missing | Multiple | Y | 36,150/112,968 = 32.0% missing | Correct | |
| C13 | div_stability_lead coverage 76.5% | E | Y | 86,459/112,968 = 76.5% | Correct | |
| C14 | payout_flexibility_lead coverage 93.2% | E | Y | 105,301/112,968 = 93.2% | Correct | |
| C15 | Utility sample has ~80 firms | E/I-11 | Y | Utility/MgrQA: 80 firms; Utility/CEO_Pres: 67 firms | Correct; actually worse for some measures |
| C16 | Zero robustness tests | K5/I-04 | Y | No alt specs, no placebo, no alt clustering in `run_h3_payout_policy.py` | Correct | |
| C17 | Multiple calls per firm-year share same lead DV | I-09 | Partial | Within (gvkey, fyearq), DV is always identical. Within (gvkey, year), 68% have 2 values due to fiscal-year vs calendar-year mismatch | **Overstated** | The pseudo-replication is at fiscal-year level, not calendar-year; since PanelOLS indexes by (gvkey, year), calls in different fyearq within the same year actually have different DVs |
| C18 | fillna(0) on oancfy and capxy in FCF | I-06 | Y | Line 827: `oancfy.fillna(0) - capxy.fillna(0)` | Correct | |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim/statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|----------------|------------------------|----------|-----------------|----------------------|
| E01 | "No regression output exists" (I-03, rated Critical) | 15 archived runs exist in `outputs/econometric/_archived/h3_payout_policy/`; latest is 2026-03-07_230800 using the same panel | High | The audit did not search `_archived/` subdirectory | "Regression output exists in archived location; no output in the primary `outputs/econometric/h3_payout_policy/` directory" |
| E02 | "All complete cases are already div payers (coincidence of missingness)" (E3, newer version) | This claim is not verified; 82,295 complete cases reduced to 51,568 after div-payer filter = 37% drop, not "coincidence" | Medium | No evidence provided for this claim | Drop this claim; the div-payer filter removes 30,727 rows from the complete-case sample |
| E03 | Older version: within-R^2 0.82-0.91 for payout_flexibility | Based on stale run (2026-02-27); latest run shows 0.01-0.11 | High | No versioning of which run these results come from | R^2 values are code-version dependent; must specify run timestamp |
| E04 | Older version: "1/36 tests significant" | Latest run shows 5/36 significant (Finance payout_flexibility) | High | Different code version produced different results | Results vary across code versions; must specify which run |
| E05 | "payout_flexibility_lead has std=0.386, suggesting reasonable variation" (J.3, older version) | Total SD is not relevant; within-firm SD averages 0.133, and 39% of firms have zero within-firm variation; only 28.5% of total variance is within-firm | Medium | Within-firm variation not tested | Within-firm variation is limited; 39% of firms contribute nothing after firm FE demeaning |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why false/overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|---------------------|----------|------------------------|----------------|
| F01 | I-03: "No regression output exists" (Critical) | Archived outputs exist with full 36-model grid; latest run (2026-03-07) used the correct panel | `outputs/econometric/_archived/h3_payout_policy/2026-03-07_230800/model_diagnostics.csv` has 36 rows; `run_manifest.json` confirms panel hash matches | High | Output exists in `_archived/` directory; issue is organizational (no symlink/latest), not missing |
| F02 | I-09: "Multiple calls per firm-year share the same lead DV, inflating effective sample" | The DV is constant within (gvkey, fyearq), not (gvkey, year). Since PanelOLS indexes by (gvkey, year), and 68% of (gvkey, year) pairs span two fiscal years, many intra-year calls actually have DIFFERENT DV values | Data check: within (gvkey, year) only 32% have exactly 1 unique DV value; 68% have 2 | Medium | The pseudo-replication is real at the fiscal-year level but is partially mitigated by the calendar-year indexing. The concern should be reframed: calls within the same fiscal year share a DV, but the unit of observation (call) does provide independent RHS variation |

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|--------------------------|-------------|-----------------|
| G01 | DV distributional pathology | `payout_flexibility_lead` has only 11 unique values, with 46.4% at exactly 0.0 and 14.8% at exactly 1.0; it is effectively a discrete/ordinal variable | `nunique()=11`; `value_counts()` shows mass points at 0, 0.2, 0.4, 0.6, 0.8, 1.0 (all multiples of 0.2 from 5-year rolling window) | High | Neither audit version examined the DV's distributional properties beyond summary stats | OLS on a heavily zero-inflated discrete DV violates distributional assumptions; standard errors and inference are unreliable; a fractional response model (Papke-Wooldridge) or ordered probit would be more appropriate | Use fractional logit/probit for payout_flexibility; document discreteness |
| G02 | Within-variation exhaustion | 39.3% of firms (951/2,421) have zero within-firm variation in payout_flexibility_lead; only 28.5% of total variance is within-firm | `groupby('gvkey').std()` shows 951 firms with SD=0 | High | First audit noted "high within-R^2" but did not investigate within-firm variation directly | Firm FE absorbs most variation; the regression identifies only from the ~61% of firms with any within-firm DV change; effective sample is much smaller than reported N | Report effective number of identifying firms; test sensitivity to dropping zero-variation firms |
| G03 | Two contradictory audits in one file | The first-layer audit file contains two complete audits concatenated: version 1 (sections A-J, dated 2026-02-28) and version 2 (sections A-N, dated 2026-03-15), with contradictory claims about R^2, significance, and output existence | Structural examination of the H3.md file: two "## A. Suite Overview" headers, contradictory R^2 values, contradictory output-existence claims | Medium | N/A (self-referential) | A committee member reading the file encounters contradictions and cannot determine which facts are current | Remove older version or clearly mark it as superseded |
| G04 | Archived output not discovered | Latest econometric run (2026-03-07_230800) exists in `_archived/` with 36 models, matching the current panel artifact | `outputs/econometric/_archived/h3_payout_policy/2026-03-07_230800/run_manifest.json` confirms panel_hash matches 2026-03-02 panel | Medium | Newer audit only checked primary directory, not `_archived/` | Audit based its "Critical" reproducibility finding on incomplete search | Search `_archived/` directories; document archive conventions |
| G05 | H3-specific Compustat vars excluded from inf-to-NaN cleanup | The `ratio_cols` list in `_compute_and_winsorize()` (lines 1115-1131) does NOT include `div_stability`, `payout_flexibility`, `earnings_volatility`, `fcf_growth`, `firm_maturity` | These vars are absent from ratio_cols; inf replacement only happens at regression time via `replace([np.inf, -np.inf], np.nan)` | Low | Neither audit version checked whether H3 vars are in the engine-level inf-replacement list | If inf values exist in these vars, they persist in the panel until regression stage; verified: no inf values currently present, so impact is nil | Add H3 vars to ratio_cols for defensive consistency |
| G06 | R-squared discrepancy across code versions unexamined | Old run (2026-02-27) within-R^2: 0.18-0.91; new run (2026-03-07) within-R^2: 0.01-0.11. Same panel, same N, different R^2 by 10-80x | Old run `model_diagnostics.csv` vs new run `model_diagnostics.csv`; N values identical | High | Version 2 of audit did not compare old vs new runs | Either the R^2 definition changed (rsquared_within vs rsquared_inclusive) or the code changed; the old "within_r2" column was actually the inclusive R^2; the new run correctly reports within-R^2 | Clarify which R^2 is being reported; verify old run used different PanelOLS settings |
| G07 | 5/36 significant in latest run, not 1/36 | Latest run (2026-03-07) shows 5/36 significant tests, all in Finance/payout_flexibility | Rows 24-28 of model_diagnostics.csv: h3_sig=True for 5 Finance payout_flex specs | Medium | Version 1 used old run; version 2 did not check archived outputs | Results are more favorable than either audit version reported (but still weak overall, and concentrated in one subsample) | Report results from latest run; discuss that significance is concentrated in Finance subsample |
| G08 | Utility CEO_Pres spec has only 67 firm clusters | Utility/CEO_Pres_Uncertainty_pct: 67 firms for div_stability_lead, 70 firms for payout_flexibility_lead | Verified via sample reconstruction | Medium | First audit (newer version) only noted 80 firms for Utility generally, not the worse specs | 67 clusters is dangerously low for cluster-robust inference; rule of thumb requires >50 (Cameron/Miller) but 67 is marginal | Report per-spec cluster counts; consider dropping Utility CEO specs |

---

## H. Severity Recalibration

| Issue ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----------|--------|-------------------|-------------------|------------------|---------------|
| I-01 (false standardization) | First audit | High | High | Agree: false documentation in LaTeX table | Misleading; must fix before submission |
| I-02 (is_div_payer_5yr docstring) | First audit | High | Medium | Genuine mismatch but rolling-max is arguably more standard in payout literature; docstring fix is trivial | Fix docstring; does not invalidate results |
| I-03 (no regression output) | First audit | Critical | **Low** | Archived outputs exist; issue is organizational | Downgraded: outputs are available |
| I-04 (zero robustness) | First audit | Critical | Critical | Agree: zero robustness is disqualifying | Must implement robustness battery |
| I-05 (firm_maturity docstring) | First audit | Medium | Low | RE/AT (code) is the standard measure (DeAngelo et al. 2006); docstring is simply wrong | Trivial fix |
| I-06 (fillna(0) on oancfy/capxy) | First audit | Medium | Medium | Agree; creates false zeros for truly missing data | Should use conditional NaN |
| I-07 (fillna(0) on Lev) | First audit | Medium | Medium | 14,156 Lev=0 rows (12.5%); 4,258 among div payers; some are genuine zero-leverage firms, others are misclassified | Investigate proportion that is genuinely zero vs data artifact |
| I-08 (no linguistic controls) | First audit | High | High | Agree: OVB risk from omitting sentiment/analyst uncertainty | Already in panel; easy fix |
| I-09 (pseudo-replication) | First audit | High | **Medium** | Overstated: within (gvkey, year), 68% of firm-years have 2 different DV values due to fiscal/calendar mismatch; the issue exists at fiscal-year level but is less severe than claimed | Still a concern; firm-year clustering or collapse warranted |
| I-10 (year vs quarter FE) | First audit | Medium | Medium | Agree | Align with other suites |
| I-11 (Utility thin clusters) | First audit | Medium | Medium | Some specs have only 67 clusters, worse than reported 80 | Per-spec reporting needed |
| I-12 (no lagged DV) | First audit | High | High | Agree: standard in payout literature | Must add |
| I-13 (no multiple testing correction) | First audit | Medium | Medium | Agree | Apply BH correction |
| G01 (payout_flex discrete) | Red-team | -- | **High** | 11 unique values, 46% at zero; OLS inappropriate | Consider fractional response model |
| G02 (within-variation exhausted) | Red-team | -- | **High** | 39% of firms have zero within-firm DV variation | Report identifying variation; test sensitivity |
| G03 (contradictory audit file) | Red-team | -- | Medium | Two audits concatenated with conflicting facts | Remove older version |
| G06 (R^2 discrepancy) | Red-team | -- | High | 10-80x difference in within-R^2 across runs | Investigate and document |
| G07 (5/36 not 1/36 significant) | Red-team | -- | Medium | Results more favorable than reported | Use latest run results |

---

## I. Completeness Gaps in the First Audit

| Missing/incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|------------------------|---------------|----------|----------|-------------------------------|
| DV distributional properties | Neither version examined distributional shape of DVs beyond summary stats | payout_flexibility_lead has 11 unique values, 46% zeros; div_stability_lead has 34% zeros in contemporaneous version | High | Histograms or tabulations of DV mass points; discussion of OLS appropriateness for heavily discrete/zero-inflated outcomes |
| Within-firm variation audit | Neither version computed within-firm SD or fraction of variance within firms | Only 28.5% of payout_flexibility_lead variance is within-firm; 39% of firms have zero within-firm variation | High | Standard FE diagnostic: within-firm variation fraction, number of firms with positive variation |
| Archived output discovery | Newer version did not search `_archived/` subdirectory | 15 archived runs exist | Medium | Search all output directories including archives |
| Cross-run comparison | No comparison of results across the 15 archived runs | Old run: within-R^2 0.18-0.91; new run: 0.01-0.11; same N but dramatically different R^2 | High | Document which run is canonical; explain R^2 discrepancy |
| Per-spec cluster counts | Reported 80 firms for Utility generically; did not check per-measure | CEO_Pres Utility: 67 firms | Low | Report minimum cluster count across all 36 specs |
| H3 vars in inf-replacement list | Not checked whether H3-specific vars are cleaned for inf at engine level | `ratio_cols` excludes all H3 vars | Low | Verify inf handling at each stage |
| Effective identifying sample | Reported total N but not the number of firms with positive within-firm DV variation | 951/2,421 firms have zero within-firm variation in payout_flexibility_lead | High | Report N_eff (firms contributing to identification) alongside total N |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|------------------|----------------------|-----------|-------------------|------|---------------|
| Stage 1-2 prerequisites | Older version: Yes; newer version: No | Partial | Y: Newer version assumes upstream exists | Low | Newer version omits upstream commands |
| Panel build (Stage 3) | Yes | Y | N | Low | `python -m f1d.variables.build_h3_payout_policy_panel` works; panel artifact exists at 2026-03-02_224406 |
| Regression run (Stage 4) | Yes | Y | Y: Output goes to `_archived/` not primary directory | Medium | Archived outputs exist but primary directory is empty; convention unclear |
| Archived output discovery | No | N/A | Y: `_archived/` subdirectory not documented | Medium | A replicator following only the audit would believe no outputs exist |
| Panel-to-regression linkage | Partial (run_manifest.json) | Y | N | Low | Panel hash in manifest matches 2026-03-02 panel |
| Environment specification | Newer version specifies exact versions; older uses ranges | Y | N | Low | Python 3.13.5, linearmodels 7.0 documented |
| Output enumeration | Yes (both versions) | Partial | Y: `run.log` output not documented in older version | Low | Latest run includes run.log |
| Stale artifact risk | Not addressed | N/A | Y: 15 archived runs exist; no clear "canonical" designation | Medium | Which of 15 runs is the canonical result? |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|------------------|----------------------|---------------|----------------------|----------|
| Identification threats | Y | Covers reverse causality, OVB, endogenous selection, look-ahead | None missed at conceptual level | -- |
| Inference / clustering | Partial | Notes thin Utility clusters and suggests firm-year clustering | Does not compute cluster-size distribution; does not note that 67 is the minimum (not 80) | Medium |
| FE and within-variation | Partial | Notes year vs quarter FE inconsistency | Does not audit within-firm variation fraction; does not flag that 39% of firms have zero DV variation under firm FE | High |
| Timing alignment | Y | Correctly identifies fiscal-year lead construction and calendar-year indexing | -- | -- |
| Post-treatment controls | Y | Notes no lagged DV; correctly identifies potential post-treatment concern with firm_maturity | -- | -- |
| Reverse causality | Y | Identifies anticipated dividend changes as threat | -- | -- |
| Endogenous sample selection | Y | Notes dynamic is_div_payer_5yr creates time-varying selection | -- | -- |
| Model-family-specific threats | **N** | Does not discuss OLS appropriateness for a DV with only 11 unique values and 46% zero inflation | payout_flexibility_lead is effectively discrete; fractional response model literature not referenced | High |
| Robustness adequacy | Y | Correctly flags zero robustness as critical | -- | -- |
| Interpretation discipline | Y | Notes causal language risk, specification mining, economic magnitude interpretation | -- | -- |
| Academic-integrity risks | Partial | Flags false standardization claim, docstring mismatches | Does not flag the contradictory two-audit file as an integrity risk for the documentation itself | Medium |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|------------------|----------|----------|---------------|-----|
| Two contradictory audits concatenated in one file | Two "## A. Suite Overview" headers; contradictory R^2 values (0.18-0.91 vs "no output exists"); contradictory significance counts (1/36 vs unverifiable) | High | A reader cannot determine which facts are current; creates confusion about the state of the suite | Remove the older version or clearly partition with "SUPERSEDED" markers |
| Critical finding based on incomplete search | I-03 "no regression output exists" is false; 15 archived runs available | High | The audit's most alarming finding is incorrect, undermining trust in the audit itself | Verify output existence across all directories including `_archived/` |
| Stale results reported as current (older version) | Within-R^2 of 0.18-0.91 and 1/36 significant from old run; latest run shows 0.01-0.11 and 5/36 | High | Committee would be given wrong quantitative results | Use only latest-run results; deprecate old results |
| Verified facts clearly separated from judgments | Newer version uses "Verified" tags and structured tables | Low | Newer version is generally well-structured | Acceptable in newer version |
| Unverified claims labeled | Partially: newer version sometimes marks "UNVERIFIED" but older version does not | Medium | Older version presents all claims as facts | Remove older version |
| Traceable evidentiary trail | Newer version provides verification log with 21 commands | Low | Adequate traceability | Good practice |

---

## M. Master Red-Team Issue Register

| Issue ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance on first audit? |
|----------|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|---------------------------------------|
| RT-01 | First-audit factual error | Reproducibility | Y | High | I-03 in newer version | "No regression output exists" -- FALSE. 15 archived runs exist | `outputs/econometric/_archived/h3_payout_policy/` contains 15 timestamped runs | Audit's most alarming finding is wrong; inflates perceived risk | Search `_archived/`; downgrade to organizational issue | Y |
| RT-02 | First-audit omission | Econometric validity | Y | High | Not in either version | payout_flexibility_lead has only 11 unique values, 46% at zero; effectively discrete | `nunique()=11`; `(pf==0).mean()=0.464` | OLS on discrete DV with massive zero-inflation violates assumptions | Discuss model appropriateness; consider fractional response model | Y |
| RT-03 | First-audit omission | Econometric validity | Y | High | Not in either version | 39% of firms have zero within-firm variation in payout_flexibility_lead; only 28.5% of variance is within-firm | `groupby('gvkey').std()`: 951/2421 firms have SD=0 | FE regression identifies only from ~61% of firms; effective sample much smaller than reported N | Report identifying-firm count; sensitivity test | Y |
| RT-04 | First-audit factual error | Results accuracy | Y | High | H (v1) and implicit in v2 | Old run within-R^2 (0.18-0.91) vs new run (0.01-0.11); 1/36 vs 5/36 significant; discrepancy not examined | Two model_diagnostics.csv files with same N but dramatically different R^2 | Committee would receive wrong quantitative results from either version | Use latest run; explain R^2 discrepancy; designate canonical run | Y |
| RT-05 | First-audit false positive | Reproducibility | Y | High | I-03 rated "Critical" | Critical severity for non-existent output when output exists in archive | `run_manifest.json` confirms panel provenance | Overstates risk; distorts priority ordering | Downgrade to Low (organizational) | Y |
| RT-06 | Underlying implementation issue missed | Table documentation | Y | High | `run_h3_payout_policy.py` L407 | "All continuous controls are standardized" -- no standardization code | grep confirms only in table note text | FALSE statement in published table | Remove claim or implement standardization | N (correctly flagged by first audit) |
| RT-07 | First-audit severity error | Identification | Y | Medium | I-09 rated "High" | Pseudo-replication claim overstated: 68% of (gvkey, year) pairs have 2 different DV values | Within (gvkey, fyearq): always 1 unique DV. Within (gvkey, year): 68% have 2 values | Fiscal-year-level duplication is real but less severe than claimed because calendar-year indexing partially differentiates | Reframe as fiscal-year clustering concern, not "pseudo-replication" | N |
| RT-08 | Underlying implementation issue missed | DV construction | Y | Medium | `_compustat_engine.py` L876 | payout_flexibility computed from 5-year rolling window with min_periods=2 produces only k/n fractional values (k changes out of n years) | Values are 0, 0.2, 0.25, 0.33, 0.4, 0.5, 0.6, 0.75, 0.8, 1.0, plus 0 for no changes | Inherently discrete DV treated as continuous | Document; consider ordinal/fractional model | Y |
| RT-09 | First-audit omission | Audit structure | Y | Medium | H3.md file structure | Two complete audits concatenated with contradictory claims | Two "## A" headers; conflicting R^2, output existence, significance | Reader confusion; undermines audit credibility | Remove older version; keep only latest | Y |
| RT-10 | Underlying implementation issue underplayed | Robustness | Y | Critical | I-04 | Zero robustness tests across 36 specs | No alt FE, no alt clustering, no placebo, no lagged DV | Disqualifying for thesis | Implement robustness battery | N (correctly flagged) |
| RT-11 | First-audit unsupported claim | Sample construction | Y | Low | E3 newer version | "All complete cases are already div payers (coincidence of missingness)" | Complete cases: 82,295; after div-payer filter: 51,568 = 37% drop | Claim is demonstrably false | Remove this claim | N |
| RT-12 | Underlying implementation issue missed | Inference | Y | Medium | Utility specs | Utility/CEO_Pres has only 67 firm clusters (not 80 as generically reported) | Sample reconstruction for each (sample, measure) combination | Cluster-robust SEs may be unreliable at 67 clusters | Report per-spec minimum cluster count | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **payout_flexibility_lead is effectively a discrete variable with 11 unique values and 46% zero inflation.** OLS is a questionable choice. No version of the first audit raises this.

2. **39% of firms have zero within-firm variation in payout_flexibility_lead.** The effective identifying sample for FE regressions is much smaller than the reported N. No version raises this.

3. **Regression output DOES exist in archived directories.** The newer audit's "Critical: no output" finding is factually wrong. A committee member would incorrectly believe no results have ever been produced.

4. **The latest run (2026-03-07) shows 5/36 significant tests (all in Finance/payout_flexibility), not 1/36 as the older audit version states.** Neither version reports the current results accurately.

5. **Within-R^2 values in the latest run are extremely low (0.01-0.06 for div_stability, 0.01-0.11 for payout_flexibility).** The older version reported 0.18-0.91, which was either the inclusive R^2 or from a different code version. A committee member would have a dramatically wrong impression of model fit.

6. **Only 28.5% of total payout_flexibility_lead variance is within-firm.** With firm FE absorbing 71.5% of variance, the design has very limited power to detect effects of time-varying speech characteristics.

7. **The first-layer audit file is self-contradictory**, containing two concatenated versions that disagree on key facts (R^2 ranges, output existence, significance counts).

---

## O. Priority Fixes to the First Audit

| Priority | Fix | Why it matters | Effort | Credibility gain |
|----------|-----|---------------|--------|-----------------|
| 1 | Remove older audit version from H3.md; keep only the newer, more thorough version | Contradictory facts confuse readers and undermine trust | Low | Eliminates self-contradiction |
| 2 | Correct I-03: output exists in `_archived/`; downgrade from Critical to Low | The audit's most alarming finding is false | Low | Removes false alarm; corrects priority ordering |
| 3 | Add DV distributional analysis: document 11-value discreteness, 46% zero inflation, 39% zero within-firm variation | These are the most important missed econometric issues | Medium | Transforms audit from implementation-focused to econometrics-focused |
| 4 | Update all quantitative results to latest run (2026-03-07): within-R^2 0.01-0.11, 5/36 significant | Current results are wrong in both versions | Low | Accurate results reporting |
| 5 | Add within-firm variation diagnostic for both DVs | Standard FE validity check; currently absent | Low | Demonstrates econometric rigor |
| 6 | Remove false claim E-02 ("all complete cases are already div payers") | Demonstrably false; creates confusion about sample construction | Low | Factual accuracy |
| 7 | Report per-spec minimum cluster counts (67 for Utility/CEO_Pres) | Generic "80 firms" understates the problem for some specs | Low | More precise risk assessment |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
No. The concatenated two-version structure creates internal contradictions. The critical false finding about missing output and the failure to discover archived results undermine factual reliability. The absence of DV distributional analysis misses the most important econometric concern.

**What is its biggest factual weakness?**
The claim that no regression output exists (I-03, rated Critical) when 15 archived runs are available, including one from 2026-03-07 using the correct panel.

**What is its biggest completeness weakness?**
The failure to examine DV distributional properties. payout_flexibility_lead has only 11 unique values with 46% zero inflation and 39% of firms having zero within-firm variation. This is a fundamental challenge to the OLS-based estimation strategy that neither audit version addresses.

**What is its biggest severity/judgment weakness?**
Rating missing output as "Critical" while not investigating the massive discrepancy between old-run and new-run R^2 values (0.18-0.91 vs 0.01-0.11). The R^2 discrepancy is far more consequential for result interpretation than output directory organization.

**What is the single most important missed issue?**
G01/G02: payout_flexibility_lead is an inherently discrete variable (11 values, 46% zeros) with exhausted within-firm variation (only 28.5% within, 39% of firms at zero SD). This combination means the PanelOLS FE framework is poorly suited to this DV. A fractional response model or ordered probit should be considered, and at minimum the effective identifying sample (firms with positive within-firm variation) must be reported alongside total N.

**What is the single most misleading claim?**
The newer version's I-03: "No regression output exists -- Stage 4 never run" (rated Critical). This is factually false. Stage 4 has been run at least 15 times, with the latest run (2026-03-07) using the current panel and producing a full 36-model grid with 5/36 significant results. A committee member reading this would wrongly believe the suite has never been estimated.

**What should a thesis committee believe after reading this red-team review?**
The H3 suite is implementationally sound at the mechanical level (panel construction, merges, lead variables, PanelOLS estimation) but has two categories of problems: (1) documentation/integrity issues (false standardization claim, docstring mismatches, contradictory audit file) that are easily fixable, and (2) deeper econometric concerns (discrete DV, within-variation exhaustion, zero robustness) that require substantive methodological decisions. The most important next step is not running Stage 4 (it has been run), but rather investigating whether OLS is appropriate for payout_flexibility_lead given its discrete nature, implementing a robustness battery, and fixing the false standardization claim in the LaTeX table.
