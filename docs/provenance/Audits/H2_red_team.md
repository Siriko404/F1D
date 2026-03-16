# H2 Suite — Second-Layer Red-Team Audit

**Suite ID:** H2
**Red-team audit date:** 2026-03-15
**Auditor posture:** Adversarial — hostile-but-fair
**Object under audit:** First-layer audit at `docs/provenance/H2.md` AND underlying implementation

---

## A. Red-Team Bottom Line

The first-layer audit is a thorough, well-structured document that correctly identifies the most important implementation issues in the H2 suite. Its dependency tracing is accurate, its variable dictionary is complete, and its referee critique is appropriately severe. However, the first audit suffers from several weaknesses: (1) it presents some claims as "VERIFIED" that are merely code-traced, not execution-verified; (2) it misses a material output-integrity issue (16 of 28 regression .txt files are absent from the latest output directory despite appearing in the diagnostics CSV); (3) it misses that NaN `ff12_code` values silently enter the Main sample; (4) it does not adequately flag the broken attrition table (the N *increases* between filter stages); and (5) some of its severity rankings are internally inconsistent with its final verdict.

**Overall grade for the first audit: PARTIALLY RELIABLE**

The first audit is reliable on model specification, variable construction, and referee-level concerns. It is unreliable on output verification and some execution-level claims.

**Suite verdict: SALVAGEABLE WITH MAJOR REVISIONS**

The first audit's final verdict is appropriate. The suite produces overwhelmingly null results (2/28 significant, consistent with chance), the contemporaneous DV has a genuine look-ahead timing issue, no robustness battery exists, and no linguistic controls are included. These are fatal for a causal-claims paper but salvageable for a descriptive-findings thesis chapter.

**Risk calibration:** The first audit **mixed both** — it correctly escalated identification threats but understated some output-integrity and reproducibility issues.

---

## B. Scope and Objects Audited

| Item | Path / ID |
|------|-----------|
| Suite ID | H2 |
| Suite entrypoint | `src/f1d/econometric/run_h2_investment.py` |
| Panel builder | `src/f1d/variables/build_h2_investment_panel.py` |
| First-layer audit | `docs/provenance/H2.md` |
| CompustatEngine (Biddle residual) | `src/f1d/shared/variables/_compustat_engine.py` (lines 463-761, 1020-1162) |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` |
| ClarityResidualEngine | `src/f1d/shared/variables/_clarity_residual_engine.py` |
| CEO Clarity Residual builder | `src/f1d/shared/variables/ceo_clarity_residual.py` |
| Manager Clarity Residual builder | `src/f1d/shared/variables/manager_clarity_residual.py` |
| H0.3 entrypoint (dependency) | `src/f1d/econometric/run_h0_3_ceo_clarity_extended.py` |
| LinguisticEngine | `src/f1d/shared/variables/_linguistic_engine.py` (lines 240-264) |
| Latest econometric output | `outputs/econometric/h2_investment/2026-03-09_002351/` |
| Latest panel output | `outputs/variables/h2_investment/2026-03-09_002230/` |
| model_diagnostics.csv | Verified: 28 rows (all results) |
| regression .txt files | Verified: only 12 of 28 present (Main only) |
| sample_attrition.csv | Verified: contains a logic error |
| run_manifest.json | Verified: panel hash tracked |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | **Pass** | Correct formula, 36 planned/28 completed, DV/IV lists match code | All specs verified against code lines 94-120 and diagnostics CSV |
| Reproducibility commands | **Partial** | Commands correct; environment assumptions listed | Does not note that `regression_results_*.txt` files are incomplete (12 of 28) |
| Dependency tracing | **Pass** | Covers manifest, linguistic, Compustat, clarity engines, panel_utils | Correctly traces Biddle first-stage, fyearq attach, lead construction |
| Raw data provenance | **Partial** | Lists all datasets; some counts marked UNVERIFIED | Compustat raw count never verified; clarity residual raw counts unverified |
| Merge/sample audit | **Pass** | Zero-delta enforcement documented; match rates listed | Merge logic verified in code (lines 206-243 of panel builder) |
| Variable dictionary completeness | **Pass** | All 17 variables documented with formulas and sources | Timing, winsorization, source fields all match code |
| Outlier/missing-data rules | **Pass** | Winsorization thresholds correct; denominator protections documented | Verified against `_compustat_engine.py` and `_linguistic_engine.py` |
| Estimation spec register | **Pass** | All 28 completed + 8 skipped specs listed with results | Coefficients and p-values verified against `model_diagnostics.csv` |
| Verification log quality | **Partial** | 16 verification commands listed | Commands described but not reproducible (no exact Python one-liners given) |
| Known issues section | **Pass** | 7 issues identified, all material | J1-J7 all verified; no false positives found |
| Identification critique | **Pass** | Correctly identifies look-ahead, reverse causality, omitted variables | Severity ratings appropriate |
| Econometric implementation critique | **Pass** | Calendar-year FE, pseudo-replication, Biddle first-stage omission flagged | All verified in code |
| Robustness critique | **Pass** | Correctly identifies zero robustness tests | 11 robustness items checked, all absent |
| Academic-integrity critique | **Pass** | Multiple-testing, silent skips, look-ahead flagged | Misses the broken attrition table and missing .txt files |
| Severity calibration | **Partial** | Mostly correct; some internal inconsistency | L1 (Critical) and L2 (Critical) correctly ranked; L6 (High) arguably also Critical |
| Final thesis verdict support | **Pass** | "SALVAGEABLE WITH MAJOR REVISIONS" is well-supported by evidence | Verdict consistent with issue register |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence checked | Red-team verdict | Notes |
|----|------------------|---------|-----------|-----------------|-----------------|-------|
| CL-1 | Estimator is PanelOLS with EntityEffects + TimeEffects, drop_absorbed=True | A2 | **Y** | `run_h2_investment.py` line 366 | VERIFIED FACT | Exact match |
| CL-2 | Standard errors: clustered by entity (gvkey), cluster_entity=True | A5 | **Y** | `run_h2_investment.py` line 367 | VERIFIED FACT | `cov_type="clustered", cluster_entity=True` |
| CL-3 | Time FE is calendar year, not fiscal year | A5, J1 | **Y** | `run_h2_investment.py` line 363: `set_index(["gvkey", "year"])`; `build_h2_investment_panel.py` line 254: `year = start_date.dt.year` | VERIFIED FACT | Material mismatch with fiscal-year DV |
| CL-4 | Biddle first-stage omits TobinQ_lag despite computing it | K3, L3 | **Y** | `_compustat_engine.py` line 662 (computed) vs line 698 (`reg_cols = ["Investment", "SalesGrowth_lag"]`) | VERIFIED FACT | Deviation from Biddle (2009) |
| CL-5 | 112,968 rows in manifest; unique on file_name | C, D, E1 | **Partial** | Code enforces uniqueness at build time (line 197-200 of panel builder); count matches prior runs | Not re-executed; count accepted from audit | |
| CL-6 | Zero-row-delta merges enforced | E1 | **Y** | `build_h2_investment_panel.py` lines 236-243: `ValueError` if row count changes | VERIFIED FACT | Both-sides uniqueness check + post-merge count comparison |
| CL-7 | 28 of 36 regressions completed; 8 skipped (clarity residuals in Finance/Utility) | H | **Y** | `model_diagnostics.csv` has 28 rows; H0.3 runs Main-only per `run_h0_3_ceo_clarity_extended.py` line 10 | VERIFIED FACT | |
| CL-8 | Only 2/28 significant at one-tailed 5% | H | **Y** | Verified from `model_diagnostics.csv`: Main-IR-MgrCR (p1=0.034) and Main-IRlead-CEOPres (p1=0.014) | VERIFIED FACT | |
| CL-9 | One-tailed test: p_one = p_two/2 if beta1 < 0 else 1 - p_two/2 | A, H | **Y** | `run_h2_investment.py` line 389 | VERIFIED FACT | Standard implementation |
| CL-10 | Clarity residuals not winsorized | F, G | **Y** | `ceo_clarity_residual.py` line 37, `manager_clarity_residual.py` line 37: `_skip_winsorization = True` | VERIFIED FACT | |
| CL-11 | Linguistic variables: per-year 0%/99% upper-only winsorization | G | **Y** | `_linguistic_engine.py` line 255-258: `lower=0.0, upper=0.99` | VERIFIED FACT | |
| CL-12 | Compustat controls: per-year 1%/99% winsorization | G | **Y** | `_compustat_engine.py` lines 1146-1160 | VERIFIED FACT | |
| CL-13 | Reproducibility status: YES | B | **Partial** | Commands are correct; scripts are deterministic | First audit does not verify that output directory is complete (missing .txt files) | PARTIALLY VERIFIED |
| CL-14 | H2b (leverage interaction) documented but not implemented | J2, L8 | **Y** | `build_h2_investment_panel.py` line 33-34 vs `run_h2_investment.py` (no interaction term anywhere) | VERIFIED FACT | |
| CL-15 | No linguistic controls in specs | J3, K2, L4 | **Y** | `CONTROL_VARS` at line 113-120: only financial controls | VERIFIED FACT | |
| CL-16 | Sample sizes vary dramatically across IVs | E4 | **Y** | CSV shows Main MgrQA: 80,317 vs CEO_CR: 40,894 (49% smaller) | VERIFIED FACT | |
| CL-17 | Multiple calls per firm-year share identical DV | K4 | **Y** | `_compustat_engine.py` lines 740-754: Q4-join-back pattern | VERIFIED FACT | Mean 3.9 calls/firm-year claimed; code flow confirmed |
| CL-18 | MIN_CALLS_PER_FIRM = 5 | A4 | **Y** | `run_h2_investment.py` line 123 | VERIFIED FACT | |
| CL-19 | Look-ahead bias in contemporaneous DV | K2, L1 | **Y** | Biddle uses Q4 annual data (line 541: `comp[comp["fqtr"] == 4]`); joined to all quarters via gvkey+fyearq (line 753-754). Q1 call gets fiscal-year-end investment. | VERIFIED FACT | Critical identification threat |
| CL-20 | 8 silently skipped regressions produce no warning | K7 | **Partial** | The code does print "WARNING: {iv} not in panel -- skipping" at line 811, and "Skipping: too few obs" at line 823 | Console output exists; first audit slightly overstates "silently" | VERIFIED FALSE POSITIVE (mild) |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|-------------------|------------------------|----------|------------------|-----------------------|
| E-1 | "Verified rows: 112,968 calls, 2,429 firms" (Section C, step 1) | Count not re-executed in the verification log; carried from a prior audit session. Commands in Section I are described but not reproducible (no exact Python one-liners). | Low | Exact command + output needed | "Verified via code-path tracing; count confirmed from panel metadata but not independently re-executed" |
| E-2 | "Reproducibility status: YES" (Section B) | First audit declares full reproducibility but does not verify the completeness of the output directory. The latest run has 12 of 28 expected .txt files. | Medium | Output file enumeration + comparison to expected set | "Reproducible via scripts; output completeness not verified" |
| E-3 | "8 silently skipped regressions" (J4, K7) | The code does print console warnings when IVs are missing or N < 100. "Silently" overstates the issue. | Low | Read lines 811, 822-823 of entrypoint | "8 regressions skipped with console warnings only; no structured log entry or table annotation" |
| E-4 | "panel.groupby(['gvkey','year']).size().mean() = 3.9" (L6 evidence) | This statistic is stated but the exact verification command is not provided in the verification log | Low | Exact command needed | Add command to verification log |
| E-5 | Several "UNVERIFIED" counts in Section E3 (firm-fiscal-years, last-year, gap-year) | First audit correctly labels these as unverified, which is good practice. However, the code does print these counts (lines 341, 366-370 of `build_h2_investment_panel.py`). The audit could have retrieved them from run logs. | Low | Read run logs or re-execute panel build | "Available from build-stage console output but not independently retrieved" |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|----------------------------------|----------|------------------------|----------------|
| FP-1 | "8 silently skipped regressions" (J4) | Console output does warn at lines 811 and 822-823 of `run_h2_investment.py`. The warning is printed to stdout. | `print(f"  WARNING: {iv} not in panel -- skipping")` and `print(f"  Skipping: too few obs ({len(df_prepared)})")` | Low | Regressions are skipped with console warnings but not with structured logging or table annotations. "Silently" is slightly misleading but the core concern (no LaTeX annotation) is valid. |
| FP-2 | None further identified | — | — | — | The first audit's criticisms are generally well-founded and evidence-based. |

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|--------------------------|-------------|-----------------|
| G-1 | Output integrity | Only 12 of 28 regression .txt files exist in the latest output directory, despite model_diagnostics.csv containing all 28 results. All missing files are for Finance and Utility samples. | `ls outputs/econometric/h2_investment/2026-03-09_002351/` shows only `regression_results_Main_*.txt` files; CSV has 28 rows | Medium | First audit relied on the diagnostics CSV for result verification and did not enumerate .txt files against expectations | Finance/Utility regression summaries cannot be inspected; raises questions about run completeness | Re-run the suite and verify all 28 .txt files are written; investigate potential filesystem/sync issue |
| G-2 | Sample accounting | The `sample_attrition.csv` has a logic error: row 4 ("After complete-case + min-calls filter") shows N=80,317, which is HIGHER than row 3 ("After lead filter") showing N=79,364. The N increases by 953 between filter stages. | `sample_attrition.csv` row 4 uses the first Main regression's N_obs (for InvestmentResidual, not _lead), while row 3 uses InvestmentResidual_lead filter | Medium | First audit did not independently verify the attrition table contents against the code logic at lines 840-846 | Attrition table is internally inconsistent and misleading. A committee member would see N increasing after a filter, which is nonsensical. | Fix attrition table logic: either show attrition for InvestmentResidual_lead only, or show separate tables per DV. Code at line 843 uses `InvestmentResidual_lead.notna()` but line 844 uses `first_meta.get("n_obs")` which is from the first regression (InvestmentResidual, not _lead). |
| G-3 | Sample composition | NaN `ff12_code` values are classified as "Main" by `assign_industry_sample()`. | `panel_utils.py` line 70: `np.select(..., default="Main")` | Low | First audit says "Main (FF12 codes 1-7, 9-10, 12)" but doesn't note that NaN ff12_code -> Main | Firms with missing industry codes enter the Main sample. If any firm has NaN ff12_code, it is misclassified. | Add a diagnostic count of NaN ff12_code firms in the Main sample; consider excluding them. |
| G-4 | Reproducibility | The `get_latest_output_dir()` pattern means the panel loaded depends on which timestamped directories exist. The first audit notes this (L14 mention of "Panel timestamp dependency") but rates it as Low severity. Given 12 different panel build timestamps exist, a stale panel could be loaded if new runs fail partway. | `outputs/variables/h2_investment/` has 12 timestamped directories | Low-Medium | First audit notes it at Low severity; arguably should be Low-Medium given the number of stale directories | Stale panel loaded if latest build fails silently | Pin panel path via `--panel-path` argument or add panel hash validation at regression load time |
| G-5 | Code documentation | The `build_h2_investment_panel.py` imports `AnalystQAUncertaintyBuilder`, `NegativeSentimentBuilder`, and 4 Weak Modal builders (lines 83-90) that are built, merged, and stored in the panel but never used in any regression. | Lines 153-158 in builder; no corresponding entry in `MAIN_IVS` or `CONTROL_VARS` of `run_h2_investment.py` | Low | First audit identifies this as J5 but rates it Low. Confirmed. | Unused variables inflate panel size and confuse auditors; harmless but wasteful | Remove or document purpose (likely kept for robustness extensions) |
| G-6 | Inference | Utility sample has only 71-84 clusters (firms) across specs. With firm+year FE on 72 firms, the effective degrees of freedom for clustered SEs are marginal. Cluster count below the commonly cited threshold of ~50 (Cameron, Gelbach, Miller 2008 suggest concern below ~50). | `model_diagnostics.csv`: Utility specs show n_clusters ranging from 71 to 84 | Low-Medium | First audit does not specifically flag the Utility cluster count as borderline; only mentions entity-only clustering as L7 | Clustered SEs in Utility sample may be unreliable; inference unreliable regardless given insignificant results | Flag Utility cluster counts; note that Utility results are descriptive at best due to marginal cluster counts |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|------------------|---------------|
| L1 | First audit | Critical | **Critical** | Agree — look-ahead bias in contemporaneous DV is a fundamental validity threat | Contemporaneous results not interpretable |
| L2 | First audit | Critical | **Critical** | Agree — zero robustness tests for a suite with 2/28 significant results | Cannot assess fragility of findings |
| L3 | First audit | High | **Medium** | Downgrade — Biddle first-stage is widely replicated with SalesGrowth-only spec (e.g., Gomariz & Ballesta 2014). TobinQ_lag is theoretically preferred but not universal. | Deviation from Biddle (2009) but within replication norms |
| L4 | First audit | High | **High** | Agree — no linguistic controls is a serious omission for a linguistic-effects hypothesis | Cannot isolate uncertainty from general negativity |
| L5 | First audit | High | **Medium-High** | Slight downgrade — calendar-year FE is imperfect but firm FE absorb most of the firm-level fiscal-year structure; the mismatch affects ~30% of firms | Year FE absorbs less time variation for non-December FYE firms |
| L6 | First audit | High | **Critical** | Upgrade — pseudo-replication from multiple calls per firm-year sharing the same DV is the most fundamental measurement validity issue. N is inflated ~4x. This should have been ranked alongside L1/L2. | Reported N is misleading; effective sample ~25% of stated N |
| L7 | First audit | Medium | **Medium** | Agree — two-way clustering is standard but single-entity clustering is defensible | SEs may be too small but direction unclear |
| L8 | First audit | Medium | **Low-Medium** | Slight downgrade — documentation gap, not a statistical issue | Misleading docstring but no estimation error |
| L9 | First audit | Medium | **Low-Medium** | Slight downgrade — the specs are correctly skipped, with console warnings; this is expected behavior for a conditional dependency | 8 regressions expected to be missing; no information loss |
| L10 | First audit | Medium | **High** | Upgrade — 2/36 significant at 5% (expected 1.8 under null) with no multiple-testing correction is the core interpretive issue. This should be ranked alongside identification threats. | The H2 hypothesis is not supported by the data; any claim of support is misleading |
| G-1 | Red-team | — | **Medium** | Missing .txt files for Finance/Utility samples | Output integrity concern; cannot inspect 16 regression summaries |
| G-2 | Red-team | — | **Medium** | Broken attrition table (N increases between filter stages) | Misleading sample accounting document |
| G-6 | Red-team | — | **Low-Medium** | Utility cluster counts borderline (71-84) | Marginal inference reliability for Utility |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|--------------------------|----------------|----------|----------|-------------------------------|
| Output file enumeration | First audit lists expected outputs (Section B) but does not verify they all exist | Only 12 of 28 .txt files present in latest run | Medium | Count actual output files and compare to expected list |
| Attrition table validation | First audit reproduces attrition counts (E4) but does not verify `sample_attrition.csv` correctness | CSV shows N increasing from 79,364 to 80,317 | Medium | Read and validate `sample_attrition.csv` against code logic |
| NaN ff12_code handling | First audit states "Main (FF12 codes 1-7, 9-10, 12)" but does not note NaN -> Main default | `panel_utils.py` line 70: `default="Main"` | Low | Document NaN ff12_code treatment and count affected firms |
| Cluster count adequacy | First audit flags entity-only clustering (L7) but does not check cluster counts per sample | Utility has 71-84 clusters | Low-Medium | Report cluster counts per sample and assess adequacy |
| All model specs verified against actual outputs | First audit's spec register (Section H) matches diagnostics CSV, but does not verify .txt files exist for each | 12 of 28 .txt files present | Low-Medium | Cross-reference file list against spec register |
| Verification log reproducibility | Section I lists 16 verification steps but provides descriptive summaries, not exact reproducible commands | Commands like `python -c "panel.shape..."` are paraphrased | Low | Provide exact runnable commands in a reproducible format |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Run H0.3 first (clarity residuals) | Y (Section B) | Y — H0.3 entrypoint exists and runs Main-only | No | Low | Correctly documented as prerequisite |
| Build panel (Stage 3) | Y | Y — deterministic script | No | Low | Command correct |
| Run regressions (Stage 4) | Y | **Partial** | Potential OneDrive sync issue | Medium | Output directory has 12 of 28 expected .txt files; diagnostics CSV has all 28 |
| Panel version resolution | Y (mentioned) | Y — `get_latest_output_dir()` resolves correctly | **Yes** — depends on filesystem state (12 stale directories) | Low-Medium | `--panel-path` flag available but not used in documented commands |
| Environment (Python 3.13, linearmodels, statsmodels) | Y | Not re-tested | No | Low | Standard packages |
| Output completeness | **No** | N — not checked by first audit | — | Medium | 16 missing .txt files not detected |
| Stale artifact risk | Partially (mentioned at J-level in first audit) | Y — 17 timestamp directories in econometric output | Yes | Low-Medium | Multiple stale runs could confuse `latest/` resolution |
| Panel hash tracking | Not mentioned | Y — `run_manifest.json` tracks panel hash | No | Low | Good practice; not highlighted by first audit |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Identification threats | **Y** | Correctly identifies look-ahead, reverse causality, OVB, endogenous selection | None missed | — |
| Inference / clustering | **Partial** | Flags entity-only clustering; does not check cluster count adequacy for Utility | Utility has 71-84 clusters; borderline for robust clustered inference | Low-Medium |
| FE and within-variation | **Y** | Correctly flags calendar-year vs fiscal-year FE mismatch | None missed | — |
| Timing alignment | **Y** | Look-ahead bias (L1) correctly identified and ranked Critical | None missed | — |
| Post-treatment controls | **Y** | CashFlow and SalesGrowth flagged as post-treatment (K2) | None missed | — |
| Reverse causality | **Y** | Correctly identified for contemporaneous DV | None missed | — |
| Endogenous sample selection | **Y** | Min-5-calls filter, differential missingness flagged | None missed | — |
| Model-family-specific threats | **N/A** | OLS/panel FE; no model-family-specific diagnostics required | — | — |
| Robustness adequacy | **Y** | Comprehensively documents zero robustness tests; 11 items all marked absent | None missed | — |
| Interpretation discipline | **Y** | Correctly states causal language not justified; notes economic magnitudes negligible | None missed | — |
| Academic-integrity / auditability | **Partial** | Flags multiple-testing, silent skips, look-ahead. Misses broken attrition table and missing output files. | Attrition table error (G-2); missing .txt files (G-1) | Medium |
| Pseudo-replication severity | **Partial** | Correctly identifies the issue (L6) but ranks it High, not Critical. With ~4x N inflation, this is as fundamental as L1/L2. | Should be ranked Critical; effective N is ~25% of reported N | Medium |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk in first audit | Evidence | Severity | Why it matters | Fix |
|----------------------------------|----------|----------|----------------|-----|
| Some VERIFIED claims rest on code-tracing, not execution | Section I verification commands are paraphrased, not exact reproducible commands | Low-Medium | A third-party auditor cannot independently replicate the verification steps without re-deriving them | Provide exact runnable commands with expected output snippets |
| Output completeness not verified | First audit lists expected outputs (Section B) but did not check actual files | Medium | Missing output files went undetected; a committee member relying on the audit would believe all 28 .txt files exist | Enumerate actual vs expected outputs |
| Broken attrition table not detected | `sample_attrition.csv` has N increasing between filter stages; first audit reproduces attrition in E4 but does not cross-check the saved artifact | Medium | A committee member reading the attrition table would see nonsensical sample flow | Read and validate all saved artifacts, not just the code logic |
| Fact/judgment separation generally adequate | First audit uses clear labels: "VERIFIED IMPLEMENTATION ISSUE", "REFEREE CONCERN", etc. | N/A | Good practice | — |
| Evidentiary trail mostly traceable | Code references with line numbers provided throughout | N/A | Good practice | — |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|------------------------|
| RT-1 | First-audit omission | Output integrity | Y | Medium | `outputs/econometric/h2_investment/2026-03-09_002351/` | Only 12 of 28 regression .txt files present (Main only); Finance/Utility .txt files missing despite diagnostics CSV containing all 28 | `ls` output vs `model_diagnostics.csv` row count | Cannot inspect Finance/Utility regression summaries; run completeness questionable | Re-run suite and verify all output files; investigate filesystem sync | N |
| RT-2 | First-audit omission | Sample accounting | Y | Medium | `sample_attrition.csv` and `run_h2_investment.py` lines 840-844 | Attrition table has N increasing from 79,364 to 80,317 between filter stages. Code uses InvestmentResidual_lead for row 3 but first regression's N_obs (for InvestmentResidual, not _lead) for row 4. | `sample_attrition.csv` contents | Misleading attrition table; committee would see nonsensical sample flow | Fix code: use consistent DV for attrition flow, or produce separate tables per DV | N (correctable) |
| RT-3 | First-audit omission | Sample composition | Y | Low | `panel_utils.py` line 70 | NaN ff12_code classified as Main | `np.select(..., default="Main")` | Firms with missing industry codes enter Main sample | Document and count; consider excluding NaN ff12_code firms | N |
| RT-4 | First-audit severity error | Pseudo-replication | Y | Should be Critical (was High) | `_compustat_engine.py` lines 740-754; `run_h2_investment.py` line 363 | Multiple calls per firm-year share identical DV; reported N is ~4x effective N | Q4-join-back pattern; mean 3.9 calls/firm-year | N inflation; SEs understated; all reported significance levels are questionable | Collapse to firm-year or weight by 1/n_calls | Y |
| RT-5 | First-audit severity error | Interpretation | Y | Should be High (was Medium) | model_diagnostics.csv | 2/28 significant at 5% one-tailed; expected under null is 1.8. No multiple-testing correction. | Binomial probability of >=2 from 28 at alpha=0.05 under null is ~0.72 | H2 results are consistent with no true effect; any claim of support is misleading | Apply FDR/Bonferroni; acknowledge null result prominently | Y |
| RT-6 | First-audit unsupported claim | Reproducibility | Partial | Low-Medium | Section B: "Reproducibility status: YES" | Claimed full reproducibility without verifying output file completeness | 12 of 28 .txt files present | Overstates reproducibility confidence | Qualify: "Pipeline is deterministic; output completeness not independently verified" | N |
| RT-7 | First-audit false positive (mild) | Documentation | Y | Low | J4, K7: "silently skipped" | The code does print warnings to console when regressions are skipped | `run_h2_investment.py` lines 811, 822-823 | Slightly overstates the problem; core concern about missing table annotations remains valid | Correct to: "skipped with console warnings only; no structured log or table annotation" | N |
| RT-8 | Underlying issue missed | Inference | Y | Low-Medium | `model_diagnostics.csv`: Utility specs | Utility sample has only 71-84 clusters; borderline for robust clustered inference | n_clusters column in diagnostics CSV | Utility inference unreliable even if results were significant | Flag cluster counts; note Utility results are descriptive only | N |
| RT-9 | First-audit severity error | Biddle first-stage | Y | Should be Medium (was High) | `_compustat_engine.py` line 698 | Biddle first-stage uses only SalesGrowth_lag, not TobinQ_lag. However, SalesGrowth-only spec is common in replications. | Gomariz & Ballesta (2014), Lara et al. (2016) use SalesGrowth-only | First audit overstates severity; deviation is within replication norms | Downgrade to Medium; recommend adding TobinQ_lag as robustness | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The attrition table saved by the pipeline is internally inconsistent** — N increases from 79,364 to 80,317 between successive filter stages. A committee member reviewing the saved artifact would be confused.

2. **Only 12 of 28 regression summary .txt files exist** in the latest output directory. Finance and Utility regression summaries cannot be independently inspected from the text-file artifacts, only from the diagnostics CSV.

3. **The pseudo-replication issue (L6) is arguably Critical, not just High.** The effective independent sample is ~25% of the reported N. All standard errors and significance levels should be interpreted with this 4x inflation in mind.

4. **The 2/28 significance rate is not just "weak" — it is statistically indistinguishable from chance.** Under the null hypothesis of no effect, the probability of observing 2 or more significant results out of 28 at alpha=0.05 is approximately 0.72. This should be stated explicitly.

5. **NaN ff12_code values default to the Main sample.** The exact count of affected firms is unknown.

6. **Utility sample cluster counts (71-84) are borderline** for clustered SE reliability.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|----------|-------------------|----------------|--------|------------------|
| 1 | Upgrade L6 (pseudo-replication) severity from High to Critical | This is the most fundamental measurement validity issue; N inflation of ~4x undermines all inference | Trivial | High — aligns severity with actual threat |
| 2 | Add output-file enumeration to verification log | Detects the missing .txt file issue; establishes output integrity | Low | Medium — demonstrates artifact verification |
| 3 | Validate sample_attrition.csv against code logic | Currently contains an internally inconsistent N-flow | Low | Medium — prevents committee confusion |
| 4 | Upgrade L10 (multiple-testing) severity from Medium to High | 2/28 is indistinguishable from chance; this is the core interpretive finding | Trivial | High — strengthens null-result acknowledgment |
| 5 | Downgrade L3 (Biddle TobinQ_lag omission) from High to Medium | SalesGrowth-only first-stage is within replication norms | Trivial | Low — reduces false alarm |
| 6 | Add cluster count reporting per sample | Utility cluster counts are borderline | Low | Low-Medium |
| 7 | Correct FP-1 ("silently skipped" -> "skipped with console warnings only") | Accuracy of audit language | Trivial | Low |
| 8 | Provide exact reproducible verification commands in Section I | Currently paraphrased; not directly runnable | Medium | Medium — enables third-party replication of audit |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
Partially. The first audit correctly identifies all major identification threats, provides an accurate variable dictionary, and reaches the right final verdict. However, it misses output-integrity issues, contains one mild false positive, has some severity miscalibrations, and does not verify saved artifacts (attrition table, .txt files) against expectations.

**Biggest factual weakness:**
The first audit does not verify actual output file completeness. Only 12 of 28 regression .txt files exist in the latest run directory, which the first audit does not detect.

**Biggest completeness weakness:**
The broken attrition table (`sample_attrition.csv` has N increasing between filter stages) is never checked. This saved artifact would mislead a committee member.

**Biggest severity/judgment weakness:**
Pseudo-replication (L6) is ranked High when it should be Critical. With ~4x N inflation from multiple calls per firm-year sharing the same DV, all reported standard errors and significance levels are unreliable. This is as fundamental as the look-ahead bias (L1) or absence of robustness (L2).

**Single most important missed issue:**
The attrition table logic error (G-2). While not a statistical threat, it is a direct artifact that a committee member would read and find confusing. It undermines the auditability of the sample construction.

**Single most misleading claim:**
"Reproducibility status: YES" (Section B). While the pipeline is indeed deterministic and reproducible from code, the first audit does not verify that the output artifacts are complete. The qualified claim should be: "Pipeline is deterministic; output completeness not independently verified for all 28 regression summaries."

**What should a thesis committee believe after reading this red-team review?**
The first-layer audit is a competent, thorough document that correctly identifies the main threats to the H2 suite and reaches the right bottom-line verdict (SALVAGEABLE WITH MAJOR REVISIONS). Its weaknesses are primarily in output verification, severity calibration, and artifact validation — not in its understanding of the econometric issues. The H2 suite itself produces results that are statistically indistinguishable from no true effect (2/28 significant, expected 1.8 under null), with a contemporaneous DV contaminated by look-ahead bias, no robustness testing, no linguistic controls, and ~4x N inflation from pseudo-replication. The committee should treat H2 as an informative null result, not as evidence for the hypothesis.
