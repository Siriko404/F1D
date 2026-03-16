# H1 Suite -- Second-Layer Red-Team Audit

**Suite ID:** H1
**Red-team date:** 2026-03-15
**Auditor posture:** Adversarial, fresh-context
**First-layer audit:** `docs/provenance/H1.md`

---

## A. Red-Team Bottom Line

The first-layer audit is a thorough, well-structured document that correctly identifies the suite boundary, traces the dependency chain, and raises several legitimate identification and robustness concerns. However, it contains material omissions and at least two factual misses that would mislead a thesis committee: (1) it fails to notice that the LaTeX table note falsely claims controls are standardized when no standardization is implemented anywhere in the runner; (2) it fails to notice that the latest (and all prior) econometric output directories contain only 6 of the expected 18 regression result `.txt` files (Main sample only -- Finance and Utility `.txt` summaries are missing despite all 18 models appearing in `model_diagnostics.csv`). The first audit also inherits and repeats the table note error about "All models use the Main industry sample" but does not connect this to the broader pattern of artifact inaccuracy. Several severity assignments are defensible but the document understates the false-claim risk in the LaTeX table while spending proportionally too much text on low-severity documentation issues.

**Overall grade for the first audit: PARTIALLY RELIABLE**

**Verdict on the suite as implemented: SALVAGEABLE WITH MAJOR REVISIONS**

**Risk characterization of first audit: Mixed -- understated artifact-integrity risk and certain omissions, while appropriately flagging identification and robustness gaps.**

---

## B. Scope and Objects Audited

| Object | Path / identifier |
|--------|-------------------|
| Suite ID | H1 |
| Suite entrypoint | `src/f1d/econometric/run_h1_cash_holdings.py` |
| Panel builder | `src/f1d/variables/build_h1_cash_holdings_panel.py` |
| First-layer audit | `docs/provenance/H1.md` |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` |
| Linguistic engine | `src/f1d/shared/variables/_linguistic_engine.py` |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` |
| Winsorization module | `src/f1d/shared/variables/winsorization.py` |
| CashHoldings builder | `src/f1d/shared/variables/cash_holdings.py` |
| Project config | `config/project.yaml` |
| Latest econometric output | `outputs/econometric/h1_cash_holdings/2026-03-06_192445/` |
| Latest panel output | `outputs/variables/h1_cash_holdings/2026-02-20_024619/` |
| Run manifest | `outputs/econometric/h1_cash_holdings/2026-03-06_192445/run_manifest.json` |
| Model diagnostics | `outputs/econometric/h1_cash_holdings/2026-03-06_192445/model_diagnostics.csv` |
| LaTeX table | `outputs/econometric/h1_cash_holdings/2026-03-06_192445/h1_cash_holdings_table.tex` |
| All 4 historical output directories inspected | `2026-03-01_234219`, `2026-03-02_230812`, `2026-03-06_192103`, `2026-03-06_192445` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | Pass | Correctly identifies PanelOLS, EntityEffects+TimeEffects, 6 measures x 3 samples = 18 specs | Matches code exactly |
| Reproducibility commands | Partial | Commands listed but not tested; doesn't note stages 1-2 modules aren't importable as `python -m` without checking | Commands plausible but untested |
| Dependency tracing | Pass | Traces from Compustat engine through builders to runner | Comprehensive and correct |
| Raw data provenance | Pass | Lists Compustat, manifest, linguistic sources with locations | Correct |
| Merge/sample audit | Pass | Correctly documents zero-row-delta enforcement, merge_asof, uniqueness guards | Verified against code |
| Variable dictionary completeness | Pass | All 6 uncertainty measures + 7 controls + identifiers documented with formulas | Formulas verified against `_compustat_engine.py` |
| Outlier/missing-data rules | Pass | Winsorization thresholds, inf->NaN, listwise deletion all documented | Verified; minor gap on linguistic 0%/99% vs Compustat 1%/99% correctly noted |
| Estimation spec register | Pass | All 18 specs with N, R2, beta, p-values | Cross-checked against `model_diagnostics.csv` -- values match |
| Verification log quality | Partial | 20 checks listed, but several are described rather than shown (no command outputs pasted) | Claims are plausible but not independently reproducible from the audit text alone |
| Known issues section | Pass | 5 issues (J1-J5) all verified as legitimate | Correct |
| Identification critique | Pass | Reverse causality, OVB, selection, look-ahead, confounds, survivorship, multiple testing all raised | Comprehensive for a panel FE suite |
| Econometric implementation critique | Pass | Calendar/fiscal FE mismatch, call-level DV, no lagged DV, singleton dropping all flagged | Correct |
| Robustness critique | Pass | Near-complete absence of robustness correctly identified as high-severity | Appropriately severe |
| Academic-integrity critique | Partial | Catches table note error (L12) and raw-data-not-committed (L14), but **misses the false standardization claim** and **missing .txt files** | Material omission |
| Severity calibration | Partial | L1-L3 (High) are correctly calibrated; some Medium issues could be upgraded | See Section H |
| Final thesis verdict support | Pass | "SALVAGEABLE WITH MAJOR REVISIONS" is defensible | Agrees with red-team assessment |

---

## D. Claim Verification Matrix (First Audit Claims Tested)

| Claim ID | First-layer claim | Section | Verified? | Evidence checked | Red-team verdict | Notes |
|----------|-------------------|---------|-----------|------------------|------------------|-------|
| C1 | Estimator is `linearmodels.panel.PanelOLS` with `EntityEffects + TimeEffects`, `drop_absorbed=True` | A2 | Y | `run_h1_cash_holdings.py` lines 78, 342-347, 362 | Correct | Formula string includes `EntityEffects + TimeEffects`; `drop_absorbed=True` at line 362 |
| C2 | SEs are firm-clustered (`cov_type="clustered"`, `cluster_entity=True`) | A5 | Y | `run_h1_cash_holdings.py` line 363 | Correct | `model_obj.fit(cov_type="clustered", cluster_entity=True)` |
| C3 | DV is `CashHoldings_lead` = `cheq/atq` shifted by -1 fiscal year | A3 | Y | `_compustat_engine.py` line 1049, `build_h1_cash_holdings_panel.py` `create_lead_variable()` | Correct | Construction verified step by step |
| C4 | Fiscal year continuity validated (non-consecutive get NaN) | A3 | Y | `build_h1_cash_holdings_panel.py` lines 337-339 | Correct | `consecutive = firm_year_eoy["fyearq_lead"] == (firm_year_eoy["fyearq_grp"] + 1)` |
| C5 | Panel has 112,968 rows, 0 duplicate file_name, 2,429 unique gvkey | C (Step 4) | Partial | Cannot re-run; but `build_h1_cash_holdings_panel.py` enforces uniqueness assertions (lines 178-183, 198-203) | Plausible | Code guards exist; exact counts unverified without re-execution |
| C6 | 18 regression result .txt files produced | B | **N** | All 4 output directories inspected; each contains only 6 `.txt` files (Main sample only) | **First-audit factual error** | `model_diagnostics.csv` has 18 rows but only Main `.txt` summaries exist on disk |
| C7 | Compustat deduplicated on (gvkey, datadate), 0 dups found | D | Partial | `_compustat_engine.py` lines 1208-1216 enforce dedup | Code path exists; 0-dup claim unverified without re-execution |
| C8 | Linguistic variables winsorized at 0%/99% per-year (upper-only) | G | Y | `_linguistic_engine.py` lines 255-258: `lower=0.0, upper=0.99` | Correct |
| C9 | Compustat controls winsorized at 1%/99% by fiscal year | G | Y | `_compustat_engine.py` lines 1146-1160: `_winsorize_by_year()` | Correct; uses `fyearq` as grouping |
| C10 | CashHoldings and Lev lack explicit `atq > 0` guard | J2 | Y | `_compustat_engine.py` line 1049: `comp["CashHoldings"] = comp["cheq"] / comp["atq"]`; line 1032: similar for Lev | Correct | inf->NaN catches `atq=0` but not `atq<0` |
| C11 | TobinsQ code implements `(mktcap + debt_book) / atq` | J4/K4 | Y | `_compustat_engine.py` lines 1050-1060 | Correct | Docstring says different formula; code is `(mktcap + debt_book) / atq` |
| C12 | OCF_Volatility max = 32.4, p99 = 0.36 | J3 | Partial | Cannot re-run descriptive stats; first audit claims verification check #8 | Plausible but unverified by red-team |
| C13 | 24.2% of calls have `year != fyearq` | J1/K2/K3 | Partial | Cannot re-run; but this is a mechanical consequence of non-December FYE firms (~30% of S&P) | Plausible |
| C14 | DV std within (gvkey, fyearq) = 0 for all groups | I (#10) | Partial | By construction (lead variable is firm-fiscal-year level, assigned identically to all calls in that group) | Mechanically true by construction logic |
| C15 | LaTeX table note says "All models use the Main industry sample" | L12 | Y | `h1_cash_holdings_table.tex` line 33-34 | Correct -- this is indeed a table note error | First audit correctly caught this |
| C16 | LaTeX table note claims "All continuous controls are standardized within each model's estimation sample" | Not in first audit | Y | `h1_cash_holdings_table.tex` line 38; `run_h1_cash_holdings.py` has zero standardization code | **First-audit omission** | False claim in output artifact; no standardization is performed |
| C17 | `run_manifest.json` records input/output paths but not file hashes | L14 | **N** | `run_manifest.json` lines 8-9: `"input_hashes": {"panel": "f05975..."}` and `"panel_hash": "f05975..."` | **First-audit factual error** | Hashes ARE recorded in the manifest |
| C18 | Main sample: 2/6 significant at 5% one-tailed | H | Y | `model_diagnostics.csv` rows 2-7: M1 p=0.005, M2 p=0.009, M3 p=0.054, M4 p=0.097, M5 p=0.624, M6 p=0.203 | Correct |
| C19 | Finance sample: 4/6 significant | H | Y | `model_diagnostics.csv` rows 8-13: F1 p=0.003, F2 p=0.025, F3 p=0.006, F4 p=0.042, F5 p=0.661, F6 p=0.685 | Correct |
| C20 | One-tailed p-value computed as `p_two/2 if beta>0 else 1-p_two/2` | K6 | Y | `run_h1_cash_holdings.py` lines 384-386 | Correct |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| Issue ID | Claim / statement | Why unsupported or weak | Severity | What evidence was missing | Corrected formulation |
|----------|-------------------|-------------------------|----------|---------------------------|-----------------------|
| E1 | "18 regression_results_{sample}_{measure}.txt files" (Section B) | All 4 output directories contain only 6 .txt files (Main sample only). Finance and Utility .txt files do not exist. | Medium | Directory listing of actual output | "6 regression_results .txt files (Main sample only); 18 regressions recorded in model_diagnostics.csv" |
| E2 | "No output hash verification" / "run_manifest.json records input/output paths but not file hashes" (L14) | The run_manifest.json actually contains `input_hashes` and `panel_hash` with SHA-256 values | Low | Inspection of `run_manifest.json` | "run_manifest.json records panel input hash (SHA-256) but not output file hashes" |
| E3 | Verification log check #10 "0/20,757 groups have >0 std" | This is mechanically true by construction (lead variable is assigned at firm-fiscal-year level to all calls) and requires no empirical verification | Low | N/A -- the claim is trivially true by design | Should be stated as "by construction" rather than presented as an empirical finding |
| E4 | "Python >= 3.8" environment assumption (Section B) | PanelOLS `from_formula` with `EntityEffects + TimeEffects` syntax and `drop_absorbed` parameter require linearmodels >= 4.x; specific version not pinned | Low | Version pinning check | Should specify minimum linearmodels version and note that `drop_absorbed` is version-dependent |
| E5 | "Linguistic Variables ... 112,968 total rows across 17 year files" (Section D) | Asserted but not cross-referenced against the year filtering that occurs in the linguistic engine (`get_data()` filters by `years` parameter) | Low | Counting across year files | Claim is plausible but evidence is described, not shown |

---

## F. False Positives in the First Audit

| Issue ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|----------|----------------------|-----------------------------------|----------|------------------------|----------------|
| F1 | L14: "No output hash verification" -- "run_manifest.json records input/output paths but not file hashes" | The manifest DOES record `input_hashes` and `panel_hash` (SHA-256). It is true that individual output file hashes are not recorded, but the claim as stated is misleading. | `run_manifest.json` contains `"input_hashes": {"panel": "f05975..."}` and `"panel_hash"` | Low | Input hashes are recorded; output file hashes are not. Restate precisely. |
| F2 | J4/L13: "TobinsQ formula inconsistency" labeled as an issue | Both `(mktcap + debt)/atq` and `(atq + mktcap - ceqq)/atq` are standard Tobin's Q approximations. The docstring mismatch is a documentation issue, not a variable construction issue. The first audit correctly labels this as Low severity but includes it in J (Known Issues) alongside substantive problems. | Code inspection | Negligible | This is a docstring cleanup item, not a known issue that affects results |

---

## G. Missed Issues (Second-Layer Discoveries)

| Issue ID | Category | Description | Evidence | Severity | Why first audit missed/underplayed it | Consequence | Recommended fix |
|----------|----------|-------------|----------|----------|--------------------------------------|-------------|-----------------|
| G1 | **Artifact integrity** | LaTeX table note falsely claims "All continuous controls are standardized within each model's estimation sample" | `h1_cash_holdings_table.tex` line 38; `run_h1_cash_holdings.py` contains zero standardization code (grep for `standardiz/zscore/scale/normalize` returns only the table note string literal at line 582) | **High** | First audit caught the "Main industry sample" note error (L12) but did not check other note claims | If this table is included in the thesis, it makes a false methodological claim that could be caught by any referee who examines the code. This is an academic integrity risk. | Remove the standardization claim from the table note, or implement actual standardization |
| G2 | **Output completeness** | Only 6 of 18 expected `regression_results_*.txt` files exist in ALL 4 output directories (only Main sample) | `ls` of all 4 output dirs: `2026-03-01_234219`, `2026-03-02_230812`, `2026-03-06_192103`, `2026-03-06_192445` -- each contains only `regression_results_Main_*.txt` | **Medium** | First audit assumed 18 .txt files without verifying disk contents | Finance and Utility model summaries are not preserved as text files. If a referee requests full regression output for non-Main samples, only `model_diagnostics.csv` (which has limited detail) is available. | Debug why `save_outputs()` only writes Main .txt files; possibly a PanelOLS model object GC issue or encoding error on Windows |
| G3 | **LaTeX table accuracy** | Negative within-R2 values (-0.002, -0.003, -0.013) displayed for Utility CEO specs in the LaTeX table | `h1_cash_holdings_table.tex` lines 25-27; `model_diagnostics.csv` confirms negative within-R2 for Utility CEO specs | **Low-Medium** | First audit did not comment on negative within-R2 in the Utility CEO specifications | Negative within-R2 indicates the model with regressors fits worse than the FE-only model. While possible in PanelOLS, it signals that the regressors add noise for these specs. A referee may question why these specs are reported without comment. | Add a note to the table or thesis text explaining negative within-R2 for small-N specs |
| G4 | **Attrition table incompleteness** | `sample_attrition.csv` only tracks Main sample attrition (112,968 -> 88,205 -> 82,236 -> 74,241). No attrition table for Finance or Utility samples. | `sample_attrition.csv` in output directory | **Low** | First audit documents attrition for Main (Section E5) but does not note absence of Finance/Utility attrition tables | A referee interested in the Finance subsample (which shows stronger results) cannot trace its attrition from the output artifacts | Generate attrition tables for all three samples |
| G5 | **Min-calls filter applies AFTER complete-case** | `prepare_regression_data()` applies the >= 5 calls/firm filter AFTER complete-case filtering (line 285-288). A firm that has 10 calls pre-filtering but only 4 with complete data is excluded. This order-dependence is not documented. | `run_h1_cash_holdings.py` lines 274-291 | **Low** | First audit describes the filter sequence but does not flag the order-dependence as a potential concern | If the thesis reports "firms with >= 5 calls," the actual criterion is "firms with >= 5 complete-case calls for this specific measure," which differs across measures | Document that the min-calls filter is applied to the measure-specific estimation sample, not the raw panel |
| G6 | **Panel builder includes variables not used by H1** | `build_h1_cash_holdings_panel.py` loads `AnalystQAUncertaintyBuilder`, `NegativeSentimentBuilder`, `CurrentRatioBuilder`, `ManagerPresWeakModalBuilder`, `CEOPresWeakModalBuilder` which are not used in the H1 regression | `build_h1_cash_holdings_panel.py` lines 135-163 vs `run_h1_cash_holdings.py` CONTROL_VARS and UNCERTAINTY_MEASURES | **Low** | First audit notes CurrentRatio is built but excluded; does not flag the other unused builders | Unused variables increase panel build time and memory but do not affect results. Minor reproducibility/cleanliness concern. | Remove unused builders from H1 panel or document why they are included (e.g., shared panel for multiple suites) |

---

## H. Severity Recalibration

| Issue ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----------|--------|-------------------|-------------------|------------------|---------------|
| L1 | First audit | High | High | Agree -- reverse causality is the primary identification threat | Cannot support causal claims |
| L2 | First audit | High | High | Agree -- OVB from missing controls is material | Coefficient interpretation limited |
| L3 | First audit | High | High | Agree -- absence of robustness battery is the single biggest practical gap | Thesis defense at risk |
| L4 | First audit | Medium | Medium | Agree -- calendar/fiscal FE mismatch introduces noise but unlikely systematic bias | Should fix but not blocking |
| L5 | First audit | Medium | Medium | Agree -- effective N is overstated | Report firm-year counts |
| L6 | First audit | Medium | Medium-High | **Upgrade** -- omitting lagged DV in a highly persistent series (AR(1) > 0.9 for cash holdings) biases ALL coefficients, not just the treatment. This is a more serious omission than the first audit's framing suggests. | Coefficient estimates may be materially biased |
| L7 | First audit | Medium | Medium | Agree | Selection into CEO sample is endogenous |
| L8 | First audit | Medium | Low-Medium | **Downgrade** -- docstring/comment language is cosmetic; what matters is the thesis text | Fix language but not blocking |
| L9 | First audit | Medium | Medium | Agree -- 18 one-tailed tests need correction | Apply multiple testing correction |
| L10 | First audit | Medium | Low | **Downgrade** -- negative `atq` is extremely rare in the Compustat-manifest intersection; winsorization likely handles any outliers | Add guard as best practice but not material |
| L11 | First audit | Medium | Medium | Agree -- OCF_Volatility outliers can influence results | Add pooled winsorization fallback |
| L12 | First audit | Low | Low | Agree | Fix table note |
| L13 | First audit | Low | Negligible | **Downgrade** -- docstring alignment is pure documentation housekeeping | N/A |
| L14 | First audit | Low | **Partially false** | Input hashes ARE recorded; output hashes are not. Restate. | N/A |
| L15 | First audit | Low | Low | Agree | Add balanced panel check |
| G1 | Red-team | N/A | **High** | False standardization claim in LaTeX table is an academic integrity risk | Must fix before thesis submission |
| G2 | Red-team | N/A | Medium | Missing .txt files for 12/18 regressions | Debug and regenerate |
| G3 | Red-team | N/A | Low-Medium | Negative within-R2 unreported | Add explanatory note |
| G4 | Red-team | N/A | Low | Finance/Utility attrition not tracked | Generate attrition for all samples |
| G5 | Red-team | N/A | Low | Min-calls filter order-dependence undocumented | Document |
| G6 | Red-team | N/A | Low | Unused builders in panel | Clean up or document |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|--------------------------|----------------|----------|----------|-------------------------------|
| LaTeX table note verification | First audit caught one table note error (L12: "Main industry sample") but did not systematically verify all note claims | `h1_cash_holdings_table.tex` line 38 claims standardization; line 33-34 claims Main-only. First audit only caught the second. | High | Systematic check of all LaTeX table note claims against implementation |
| Output file completeness check | First audit assumed 18 .txt files without listing the directory | All 4 output directories contain only 6 Main .txt files | Medium | Directory listing showing actual output files |
| Negative within-R2 discussion | Not mentioned anywhere in the first audit despite appearing in the diagnostics | `model_diagnostics.csv` and `h1_cash_holdings_table.tex` show negative within-R2 for Utility CEO specs | Low-Medium | Discussion of model fit for small-sample specs |
| Run manifest content verification | First audit claimed no hash verification, but manifest contains hashes | `run_manifest.json` has `input_hashes` and `panel_hash` | Low | Inspection of manifest contents |
| Finance sample result discussion | First audit notes Finance has 4/6 significant (stronger than Main), but does not discuss why financial firms show stronger effects or whether this is econometrically suspect | Results table shows Finance effects are systematically larger | Low | Discussion of why Finance results diverge from Main; possible concerns about financial firm cash holdings measurement |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented it? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|---------------------------|-----------|-------------------|------|---------------|
| Stage 1: assemble_manifest | Y (command listed) | N (not re-run) | Y -- requires raw inputs/ data | Medium | Cannot reproduce without external data |
| Stage 2: build_linguistic_variables | Y (command listed) | N | Y -- requires raw transcript parquets | Medium | Same as above |
| Stage 3: build_h1_cash_holdings_panel | Y (command listed) | N | Y -- requires Stage 1+2 outputs | Low | Straightforward if prerequisites exist |
| Stage 4: run_h1_cash_holdings | Y (command listed) | N | Partial -- `get_latest_output_dir` resolution is fragile | Low-Medium | First audit correctly flags this |
| Panel parquet stale-artifact risk | Y (noted in L14 area) | Y | Y -- panel build timestamp (2026-02-20) != econometric run timestamp (2026-03-06); separated by 14 days | Medium | If panel builder code changed between panel build and econometric run, outputs may not match current code. `run_manifest.json` records panel hash, mitigating this. |
| Output completeness | **N** | Y (verified) | N/A | Medium | Only 6/18 .txt files exist in output directory; first audit claims 18 |
| Standardization claim in LaTeX | **N** | Y (verified as false) | N/A | High | LaTeX table note makes false methodological claim |
| Environment/package versions | Partially | N | N/A | Low | First audit lists pandas, numpy, linearmodels, statsmodels versions but these were not pinned from a lockfile |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Identification threats | Y | Reverse causality, OVB, selection, look-ahead, confounds, survivorship all raised with appropriate severity | None significant | N/A |
| Inference / clustering | Y | Firm-clustered SEs correctly identified as addressing Moulton problem; effective-N concern raised | Could note that cluster count for Utility (70-83 firms) is borderline for cluster asymptotics (Cameron, Gelbach & Miller 2008 suggest 50+ as minimum) | Low |
| FE and within-variation | Partial | Calendar vs fiscal year mismatch flagged; singleton dropping noted | Does not discuss whether `drop_absorbed=True` might be dropping time periods (not just entities), which could affect the year FE structure | Low |
| Timing alignment | Y | Look-ahead bias in DV discussed; calendar vs fiscal year mismatch flagged | Adequately covered | N/A |
| Post-treatment controls | Partial | Not explicitly discussed as a separate concern | Some controls (ROA, TobinsQ) reflect outcomes that may be affected by the same shocks that drive uncertainty language. If uncertainty in Q1 call predicts cash at year-end t+1, and ROA at year-end t also responds to those shocks, ROA is partly post-treatment. | Low-Medium |
| Reverse causality | Y | Correctly identified as high severity | None | N/A |
| Endogenous sample selection | Y | CEO speaking selection correctly flagged | None | N/A |
| Model-family-specific threats | Partial | Singleton dropping, within-variation, persistence all noted | Does not discuss incidental parameters problem (Nickell bias) -- with T=17 years and firm FE, Nickell bias is small but exists. Not material for this suite since no lagged DV is included. | Negligible |
| Robustness adequacy | Y | Near-complete absence of robustness correctly flagged as High severity | None -- this is the strongest part of the first audit | N/A |
| Interpretation discipline | Y | Causal language in docstrings flagged; fragile results documented | None | N/A |
| Academic-integrity / auditability | **Partial** | Catches table note error (L12), raw data not committed (L14), fragile latest-dir resolution | **Misses false standardization claim (G1) and missing .txt files (G2)** | High |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk in first audit | Evidence | Severity | Why it matters | Fix |
|---------------------------------|----------|----------|----------------|-----|
| False claim about output hash verification | L14 states "No output hash verification" / "run_manifest.json records paths but not file hashes" -- but manifest contains `input_hashes` and `panel_hash` | Low | Understates the existing reproducibility infrastructure | Correct L14 to accurately describe what manifest records |
| Verification log lacks reproducible evidence | Section I lists 20 checks but provides no command outputs, no screenshots, no logs | Medium | A third party cannot independently confirm the verification checks were actually performed | Include command outputs or log excerpts for material checks |
| Claimed output count not verified against disk | Section B claims 18 regression_results .txt files | Medium | Creates false expectation of complete output set | Verify output directory contents before claiming file counts |
| Did not systematically audit LaTeX table notes | Only caught "Main industry sample" note error | High | Missed the false standardization claim which is an academic integrity risk | Systematically verify all table note claims against code |
| Presents mechanically-true facts as empirical findings | Verification check #10 ("DV std = 0 within firm-year") is true by construction | Low | Inflates appearance of verification thoroughness | Label construction-derived properties as "by construction" |

---

## M. Master Red-Team Issue Register

| Issue ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance on first audit? |
|----------|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|---------------------------------------|
| G1 | First-audit omission | Artifact integrity | Y | High | `h1_cash_holdings_table.tex` line 38 | LaTeX table note falsely claims controls are standardized; no standardization code exists | grep of `run_h1_cash_holdings.py` for standardiz/zscore/scale returns only the string literal | False methodological claim in thesis output | Remove claim or implement standardization | Y |
| G2 | First-audit omission | Output completeness | Y | Medium | All 4 output directories | Only 6/18 regression_results .txt files exist (Main only) | `ls` of all output dirs | Finance/Utility detailed regression output unavailable | Debug save_outputs() for non-Main samples | N |
| L1 | Underlying implementation issue underplayed by first audit | Identification | Y | High | Design-level | Reverse causality not addressable without IV or quasi-experiment | No IV implemented | Cannot support causal claims | Add IV or event study | Y |
| L2 | Underlying implementation issue underplayed by first audit | Identification | Y | High | Design-level | OVB from missing controls (analyst uncertainty, earnings surprise, macro) | Control set is accounting-only | Coefficient conflates multiple channels | Add omitted controls | Y |
| L3 | Underlying implementation issue missed by first audit | Robustness | Y | High | `run_h1_cash_holdings.py` | No robustness battery (alt FE, alt clustering, alt samples, placebo, nonlinearity) | Code inspection | Results not stress-tested | Implement robustness battery | Y |
| L6-up | First-audit severity error | Econometric implementation | Y | Medium-High | `run_h1_cash_holdings.py` | Omitted lagged DV in highly persistent series (AR(1) > 0.9 for cash) biases all coefficients | Code comment "GAP-5" | Systematic bias in coefficient estimates | Add contemporaneous CashHoldings as control | Y |
| E1 | First-audit factual error | Output documentation | Y | Medium | Section B | Claims 18 .txt files; only 6 exist | Directory listing | Misleading output enumeration | Correct to 6 | N |
| E2 | First-audit factual error | Reproducibility | Y | Low | L14 | Claims no hash verification; manifest has input hashes | `run_manifest.json` inspection | Understates existing infrastructure | Correct statement | N |
| G3 | First-audit omission | Model fit | Y | Low-Medium | `model_diagnostics.csv` | Negative within-R2 for Utility CEO specs not discussed | diagnostics CSV and LaTeX table | Unexplained model fit anomaly | Add discussion | N |
| G4 | First-audit omission | Sample documentation | Y | Low | `sample_attrition.csv` | Finance/Utility attrition not tracked | Output file inspection | Incomplete attrition documentation | Generate for all samples | N |
| G5 | First-audit omission | Sample construction | Y | Low | `run_h1_cash_holdings.py` lines 274-291 | Min-calls filter order-dependence undocumented | Code inspection | Actual filter criterion differs from stated | Document order | N |
| L4 | Underlying implementation issue correctly identified | Inference | Y | Medium | `run_h1_cash_holdings.py` line 359 | Calendar year time FE vs fiscal year DV (24.2% mismatch) | Code inspection | Time FE misaligned | Use fyearq_int | N |
| L5 | Underlying implementation issue correctly identified | Econometric | Y | Medium | Design-level | Call-level obs with firm-year DV; effective N overstated | By construction | Misleading sample size | Report firm-year counts; consider collapse | N |
| L9 | Underlying implementation issue correctly identified | Inference | Y | Medium | All 18 specs | Multiple testing without correction | 18 one-tailed tests | False positive risk | Apply correction | N |
| L11 | Underlying implementation issue correctly identified | Variable construction | Y | Medium | `_compustat_engine.py` | OCF_Volatility extreme outliers (max=32.4, p99=0.36) | First audit Section G | Single observations can drive results | Pooled winsorization fallback | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The LaTeX table output claims controls are standardized when they are not.** This is a false methodological claim that would appear in the thesis if the table is included as-is. No first-audit section flags this.

2. **Only 6 of 18 expected regression result text files actually exist on disk.** The Finance and Utility detailed PanelOLS summary outputs are missing from all historical runs. A referee requesting full regression output for non-Main samples would find it unavailable.

3. **The run manifest DOES contain input file hashes (SHA-256).** The first audit incorrectly states otherwise, potentially causing the committee to undervalue the existing reproducibility infrastructure.

4. **Negative within-R2 values appear for several Utility specifications.** This signals that the model with regressors fits worse than the FE-only model for these small-sample specs, a fact not discussed anywhere in the first audit.

5. **The omission of lagged cash holdings (contemporaneous CashHoldings) as a control may be more consequential than the first audit's "Medium" severity suggests**, given that cash holdings have AR(1) coefficients exceeding 0.9 in most panels.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|----------|-------------------|----------------|--------|------------------|
| 1 | **Add G1: Flag false standardization claim in LaTeX table note** | Academic integrity risk -- false methodological claim in thesis output artifact | Low | Critical |
| 2 | **Correct E1: Fix output file count from 18 to 6 .txt files** | Factual error in output enumeration | Low | Medium |
| 3 | **Upgrade L6 severity to Medium-High** | Omitting lagged DV in AR(1)>0.9 series is more consequential than current framing | Low | Medium |
| 4 | **Correct E2/L14: Note that run_manifest has input hashes** | Factual error about existing reproducibility infrastructure | Low | Low-Medium |
| 5 | **Add G3: Note negative within-R2 for Utility CEO specs** | Unreported model fit anomaly | Low | Low |
| 6 | **Strengthen verification log with reproducible evidence** | Currently lists checks but provides no outputs; a third party cannot confirm | Medium | Medium |
| 7 | **Add systematic table-note verification protocol** | Prevents future false-claim risks | Low | Medium |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
Partially. It correctly identifies the suite boundary, traces dependencies, and raises the most important identification and robustness concerns. However, it contains two factual errors (output file count, hash verification claim) and one critical omission (false standardization claim in LaTeX table), which collectively mean a committee relying solely on this audit would be misinformed about the artifact integrity of the suite.

**What is its biggest factual weakness?**
Claiming 18 regression result .txt files exist when only 6 are on disk, and claiming no hash verification exists when input hashes are recorded in the run manifest.

**What is its biggest completeness weakness?**
Failure to systematically verify all claims in the LaTeX table note, leading to the missed false standardization claim (G1).

**What is its biggest severity/judgment weakness?**
L6 (omitted lagged DV) is underweighted at Medium. Given the extreme persistence of cash holdings (AR(1) > 0.9), this omission likely biases all coefficient estimates and should be Medium-High.

**What is the single most important missed issue?**
G1: The LaTeX table note falsely claims "All continuous controls are standardized within each model's estimation sample." No standardization is performed. If this table appears in the thesis, it contains a verifiably false methodological statement.

**What is the single most misleading claim?**
E1: The first audit's statement that 18 regression result .txt files are produced creates a false impression of complete output coverage. Only Main sample summaries are available.

**What should a thesis committee believe after reading this red-team review?**
The first-layer audit is substantially correct in its identification of the H1 suite's primary weaknesses (reverse causality, OVB, missing robustness battery) and its "SALVAGEABLE WITH MAJOR REVISIONS" verdict is appropriate. The suite implementation is technically competent but econometrically incomplete. However, the first audit should not be treated as a complete artifact-integrity review: the false standardization claim in the LaTeX table must be fixed before thesis submission, the missing regression output files should be investigated, and the lagged DV omission deserves higher severity weight. After these corrections, the first audit plus this red-team supplement would constitute an adequate basis for committee review.
