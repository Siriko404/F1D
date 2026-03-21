# H5 Analyst Dispersion -- Second-Layer Red-Team Audit

**Suite ID:** H5
**Red-team audit date:** 2026-03-18
**First-layer audit date:** 2026-03-17 (docs/provenance/H5.md)
**Auditor posture:** Hostile-but-fair, independent fresh-context verification
**Code state:** Post-redesign (commit 32e5e6e and later)

---

## A. Red-Team Bottom Line

The first-layer audit (H5.md) is a **post-redesign provenance document**, not a traditional red-team audit. It documents the new design decisions, model specifications, and resolved issues from the redesign. As a provenance/design document it is **largely accurate and well-structured**. However, it is **incomplete as a thesis-standard audit** because it does not adversarially probe the redesigned implementation for new issues introduced by the redesign itself.

**First-layer document grade:** LARGELY ACCURATE as provenance; INCOMPLETE as audit

**Suite implementation verdict:** CONDITIONALLY THESIS-STANDARD -- the redesign addresses the catastrophic issues from the prior implementation (broken DV, stale architecture), but introduces two material concerns that require verification or disclosure before thesis submission.

**Key red-team findings:**
1. The PanelOLS duplicate multi-index problem persists in the redesigned code (MAJOR).
2. The IBES Detail engine loads FPI=['6','7'] while the audit and all documentation claim FPI='6' only (MAJOR -- documentation mismatch, though likely functionally benign).
3. No winsorization of control variables at the panel-builder level; winsorization is split across multiple engines with inconsistent strategies (MINOR -- documented but fragmented).
4. The `check_rank=False` in the industry FE specification suppresses rank-deficiency warnings (MINOR).

---

## B. Scope and Objects Audited

| Item | Path / ID |
|------|-----------|
| Suite ID | H5 |
| Suite entrypoint | `src/f1d/econometric/run_h5_dispersion.py` |
| Panel builder | `src/f1d/variables/build_h5_dispersion_panel.py` |
| First-layer audit | `docs/provenance/H5.md` |
| PostCallDispersionBuilder | `src/f1d/shared/variables/postcall_dispersion.py` |
| IbesDetailEngine | `src/f1d/shared/variables/_ibes_detail_engine.py` |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` |
| Panel utils | `src/f1d/shared/variables/panel_utils.py` |
| Winsorization module | `src/f1d/shared/variables/winsorization.py` |
| LossDummyBuilder | `src/f1d/shared/variables/loss_dummy.py` |
| BookLevBuilder | `src/f1d/shared/variables/book_lev.py` |
| ROABuilder | `src/f1d/shared/variables/roa.py` |
| Prior red-team audit (obsolete) | `docs/provenance/Audits/H5_red_team.md` |
| Shared variables __init__ | `src/f1d/shared/variables/__init__.py` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team verdict |
|-----------|-------------------|----------------|-----------------|
| Model/spec identification | Pass | 4 specs correctly documented (Industry/Firm FE x Base/Extended) | Accurate -- matches code MODEL_SPECS lines 109-114 |
| Reproducibility commands | Pass | 3 explicit commands documented (build, dry-run, full run) | Commands match module paths |
| Dependency tracing | Partial | Builder chain listed but not fully traced to raw sources | Does not trace IBES Detail engine's FPI/PDF filter settings |
| Raw data provenance | Partial | IBES Detail, Compustat mentioned; no file hashes or versions | Adequate for provenance doc; insufficient for full audit |
| Merge/sample audit | Partial | Zero-row-delta enforcement documented; merge match rates not | Panel builder enforces delta=0 (lines 155-159) -- verified |
| Variable dictionary completeness | Pass | All 18 regression variables documented with sources | Matches code KEY_IVS + BASE_CONTROLS + EXTENDED_CONTROLS |
| Outlier/missing-data rules | Partial | Winsorization documented for DV; control winsorization implicit | See issue MI-1 below |
| Estimation spec register | Pass | 4 columns fully specified with DV/FE/controls | Matches code exactly |
| Verification log quality | Fail | No verification log; this is a design document, not an audit | No evidence of independent execution or output inspection |
| Known issues section | Pass | 7 issues documented with severity and resolution | All resolutions verified in code |
| Identification critique | Fail | No identification critique present | Provenance doc, not audit -- but thesis standard requires it |
| Econometric implementation critique | Fail | Not present | Missing from document scope |
| Robustness critique | Fail | Not present | Missing from document scope |
| Academic-integrity critique | Fail | Not present | Missing from document scope |
| Severity calibration | Pass (for scope) | Red-team resolutions correctly prioritized | CRITICAL/MAJOR/MINOR labels appropriate |
| Final thesis verdict support | Partial | "REDESIGNED" verdict stated; no readiness assessment | Does not assess whether redesign is itself thesis-ready |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|-------------------|---------|-----------|----------|-------------------|-------|
| C1 | DV = PostCallDispersion = SD(next-Q EPS) / abs(Mean) x 100 | A3 | YES | `postcall_dispersion.py` lines 265-276: `agg["_sd"] / agg["_mean"].abs() * 100` | Confirmed | Formula matches code exactly |
| C2 | Post-call timing: 3 trading days after call (USFederalHolidayCalendar) | A3 | YES | `postcall_dispersion.py` line 56: `self.days_after = 3`; line 61: `CustomBusinessDay(calendar=USFederalHolidayCalendar())` | Confirmed | |
| C3 | FPI='6' (next-quarter EPS) | A3 | **PARTIAL** | Builder docstring says FPI=6 (line 15, 47), but IbesDetailEngine loads FPI=['6','7'] (line 64). Builder does NOT filter to FPI=6 only before computing dispersion. | **Documentation mismatch** | See MI-2 |
| C4 | PDF='D' (diluted EPS) | A3 | YES | `_ibes_detail_engine.py` line 65: `self.pdf_valid = ['D']` | Confirmed | |
| C5 | 120-day FPEDATS fence | A3/C | YES | `postcall_dispersion.py` line 58: `self.fpedats_max_days = 120`; line 169: `tolerance=pd.Timedelta(days=self.fpedats_max_days)` | Confirmed | |
| C6 | Stale estimate filter: 180 days | A3 | YES | `postcall_dispersion.py` line 57: `self.max_stale_days = config.get("max_stale_days", 180)`; line 245: filter applied | Confirmed | |
| C7 | Min 2 analysts | A3 | YES | `postcall_dispersion.py` line 51: `NUMEST_MIN = 2`; line 259-260: filter applied | Confirmed | |
| C8 | 4 simultaneous IVs: CEO_QA, CEO_Pres, Mgr_QA, Mgr_Pres Uncertainty_pct | A4 | YES | `run_h5_dispersion.py` lines 83-87: KEY_IVS matches exactly | Confirmed | |
| C9 | Base Controls (8): Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, PreCallDispersion | A5 | YES | `run_h5_dispersion.py` lines 91-100: BASE_CONTROLS = 8 items matching | Confirmed | |
| C10 | Extended Controls (Base + 4) | A5 | YES | `run_h5_dispersion.py` lines 102-107: EXTENDED_CONTROLS = BASE + 4 | Confirmed | |
| C11 | Main sample: FF12 codes 1-7, 9-10, 12 | A7 | YES | `run_h5_dispersion.py` lines 210-213: excludes ff12_code in [8, 11]; remaining = 1-7, 9-10, 12 | Confirmed | |
| C12 | Min 5 calls per firm | A7 | YES | `run_h5_dispersion.py` line 116: `MIN_CALLS_PER_FIRM = 5` | Confirmed | |
| C13 | One-tailed test: p_one = p_two / 2 if beta > 0 else 1 - p_two / 2 | A8 | YES | `run_h5_dispersion.py` line 340: exact match | Confirmed | |
| C14 | Firm-clustered SEs | A9 | YES | `run_h5_dispersion.py` line 307, 312: `cov_type="clustered", cluster_entity=True` | Confirmed | |
| C15 | Industry FE absorbed via PanelOLS other_effects (FF12) | A2 | YES | `run_h5_dispersion.py` lines 298-303: `entity_effects=False, time_effects=True, other_effects=industry_data` | Confirmed | |
| C16 | Firm FE via EntityEffects + TimeEffects from_formula | A2 | YES | `run_h5_dispersion.py` lines 309-311: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` | Confirmed | |
| C17 | Panel Index: gvkey + fyearq_int | A1 | YES | `run_h5_dispersion.py` line 291: `df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])` | Confirmed | But see MI-3 for implications |
| C18 | Winsorization 1%/99% pooled on DV | A3 | YES | `postcall_dispersion.py` lines 91-97: pooled winsorization of both Pre/PostCallDispersion | Confirmed | |
| C19 | `attach_fyearq()` produces `fyearq` not `fyearq_int` -- resolution: explicit conversion | C | YES | `build_h5_dispersion_panel.py` lines 170-173: `attach_fyearq` + `np.floor(...).astype("Int64")` | Confirmed | |
| C20 | ROABuilder added to builders list | C | YES | `build_h5_dispersion_panel.py` line 107: `"roa": ROABuilder(...)` | Confirmed | |
| C21 | Unique Record Identifier: file_name | A1 | **PARTIAL** | file_name is the unique key in the PANEL (build step), but the runner does NOT load file_name (line 187-200 columns list excludes it) | Partial -- true for panel, not for regression | |
| C22 | drop_absorbed=True | A2 | YES | Lines 305 (industry spec) and 311 (firm spec) | Confirmed | |
| C23 | PreCallDispersion: 1 trading day before call | A3 | YES | `postcall_dispersion.py` line 55: `self.days_before = 1` | Confirmed | |

---

## E. Unsupported/Overstated Claims

| ID | Claim | Why weak | Severity | Missing evidence | Corrected formulation |
|----|-------|----------|----------|------------------|----------------------|
| E1 | "FPI=6 (next-quarter EPS forecasts only)" (A3, repeated throughout) | The IbesDetailEngine loads FPI=['6','7']. The PostCallDispersionBuilder does not filter to FPI=6 before computing dispersion. It joins on (gvkey, fpedats), pooling estimates from both FPI horizons targeting the same period end date. | MAJOR (documentation) | No code inspection of engine defaults | "IBES Detail data loaded with FPI in ['6','7']. Estimates are pooled by target FPEDATS regardless of FPI horizon. Both FPI=6 and FPI=7 estimates targeting the same period end date are included in the dispersion computation." |
| E2 | "Estimation Unit: Call-level (individual earnings call)" (A1) | While the panel is built at call level, the PanelOLS regression uses (gvkey, fyearq_int) as its MultiIndex. Multiple calls per firm-year are treated as observations within the same (entity, time) cell. The estimation unit is effectively the call, but PanelOLS's demeaning operates at the (gvkey, fyearq_int) cell level. | MINOR (imprecise) | No discussion of PanelOLS behavior with duplicate indices | "Estimation unit is the individual earnings call. PanelOLS index is (gvkey, fyearq_int); firms with multiple calls per fiscal year have duplicate index entries. PanelOLS demeans at the index-cell level." |
| E3 | "Variables winsorized at 1%/99%" (LaTeX table notes, line 486) | This blanket statement is imprecise. DV/control winsorization happens in different places: PostCallDispersion is pooled-winsorized in the builder; Compustat controls are year-winsorized in the engine; linguistic IVs are NOT winsorized in this pipeline (they may be winsorized upstream in Stage 2, but this is not documented here). | MINOR | No tracing of per-variable winsorization path | "PostCallDispersion and PreCallDispersion winsorized at 1%/99% pooled. Compustat controls winsorized at 1%/99% per fiscal year. Linguistic variables' winsorization depends on upstream Stage 2 processing." |

---

## F. False Positives

| ID | Criticism (if any) | Why false | Evidence | Severity | Corrected view |
|----|-------------------|-----------|----------|----------|----------------|
| F1 | (No explicit criticisms in first-layer doc -- it is a provenance document, not an adversarial audit) | N/A | N/A | N/A | N/A |

The first-layer document does not contain adversarial claims to evaluate as false positives. Its red-team resolutions (Section C) are all verified as correctly resolved in the current code.

---

## G. Missed Issues

| ID | Category | Description | Evidence | Severity | Why missed | Consequence | Fix |
|----|----------|-------------|----------|----------|------------|-------------|-----|
| MI-1 | Econometric | **PanelOLS duplicate multi-index persists.** `set_index(["gvkey", "fyearq_int"])` creates non-unique (entity, time) pairs because multiple earnings calls occur per firm-year. PanelOLS with EntityEffects demeans within each unique entity across time, but with TimeEffects, the time FE is estimated on a non-unique time index. For the industry FE spec (entity_effects=False, time_effects=True, other_effects=ff12_code), there is no entity demeaning at all -- just time FE and industry FE with clustered SEs. The firm FE spec uses EntityEffects which groups by gvkey (first index level), so the entity demeaning is correct, but the time demeaning pools all calls within a firm-year. | `run_h5_dispersion.py` line 291: `set_index(["gvkey", "fyearq_int"])`. Call-level data means ~3-4 calls per firm-year. | MAJOR | Provenance doc does not audit econometric implementation details | For industry FE specs (cols 1,3): coefficients are correct (no entity demeaning claimed). For firm FE specs (cols 2,4): entity demeaning groups by gvkey correctly, but time demeaning treats all calls in the same firm-year identically. Standard errors may be slightly affected but clustering at entity level should absorb within-firm-year correlation. | Document the duplicate-index behavior. Optionally verify coefficients match a manually-demeaned specification. Consider using a unique call-level time index (e.g., quarter rather than year). |
| MI-2 | Variable construction | **FPI mismatch between documentation and engine.** The audit, builder docstrings, and metadata all state FPI='6' (next-quarter only). The IbesDetailEngine loads FPI=['6','7']. The dispersion computation joins on (gvkey, fpedats) without filtering by FPI, pooling estimates from both horizons that target the same period end date. | `_ibes_detail_engine.py` line 64: `self.fpi_valid = ['6', '7']` vs. `postcall_dispersion.py` line 15: "FPI='6' (next-quarter EPS forecasts only)" | MAJOR (doc) / MINOR (functional) | Provenance doc accepted builder docstrings at face value without tracing to engine defaults | Functionally, pooling FPI=6 and FPI=7 estimates for the same fpedats is defensible -- these are estimates targeting the same fiscal period. But the documentation is wrong and could mislead a replicator. | Correct all documentation to state FPI in ['6','7']. Add explicit justification for pooling both FPI horizons. Alternatively, filter to FPI=6 only in the builder if strict adherence to Druz et al. (2020) is desired. |
| MI-3 | Econometric | **`check_rank=False` suppresses rank-deficiency detection in industry FE spec.** Line 305 sets `check_rank=False` for the industry FE specification. This means if the FF12 industry dummies are collinear with the time FE or regressors, PanelOLS will not warn. | `run_h5_dispersion.py` line 305 | MINOR | Not within scope of provenance doc | Could mask absorbed-variable pathologies. The `drop_absorbed=True` should handle collinearity, but suppressing the rank check reduces transparency. | Remove `check_rank=False` or document why it is needed (e.g., performance, known-benign rank deficiency). |
| MI-4 | Identification | **No identification strategy critique in the provenance document.** The redesign follows the H1/H4 pattern but does not discuss reverse causality (managers adjust speech when they know analysts are dispersed), simultaneity, or omitted variable bias. | Absence from H5.md | MAJOR (for thesis standard) | Provenance doc scope did not include identification critique | A thesis committee would expect discussion of why speech uncertainty is not merely reflecting information already in analyst estimates (which PreCallDispersion partially controls for). | Add identification discussion to provenance or create separate audit document. |
| MI-5 | Robustness | **No robustness specifications documented or implemented.** The 4-column design varies FE type and control set, which is specification sensitivity, not robustness. No IV/2SLS, placebo tests, or subsample stability checks. | `run_h5_dispersion.py`: only MODEL_SPECS with 4 entries | MAJOR (for thesis standard) | Outside provenance doc scope | Thesis committee will demand robustness evidence | Implement at minimum: (a) alternative DV timing windows, (b) placebo test with pre-call uncertainty, (c) subsample by firm size or analyst coverage |
| MI-6 | Variable construction | **`std()` uses ddof=1 (sample std) in dispersion computation.** With NUMEST_MIN=2, two-analyst dispersion uses ddof=1, making the standard deviation sqrt(2) times larger than population std (ddof=0). This systematically inflates dispersion for low-analyst-count calls. | `postcall_dispersion.py` line 266: `agg(["std", "mean"])` -- pandas default ddof=1 | MINOR | Technical detail below provenance doc level | Does not affect cross-sectional ranking but inflates magnitude for low-coverage calls. Affects economic magnitude interpretation. | Document the ddof=1 convention. Consider ddof=0 for consistency with IBES literature, or raise NUMEST_MIN. |
| MI-7 | Sample | **No discussion of IBES-Compustat linking methodology.** The IBES Detail engine uses CCM CUSIP8-to-GVKEY mapping with LINKPRIM in ['P','C'] and keeps first duplicate (line 120-121). Drop-duplicates on cusip8 keeping "first" is arbitrary when multiple gvkeys map to the same CUSIP8. | `_ibes_detail_engine.py` lines 115-121 | MINOR | Infrastructure-level detail | Could cause a small number of mislinked estimates. Standard in the literature but should be documented. | Document the CCM linking choices (LINKPRIM filter, duplicate resolution). |
| MI-8 | Panel construction | **Linguistic IVs not explicitly winsorized in the panel builder.** The panel builder does not call any winsorization on the 4 key IVs or the extended linguistic controls. Winsorization depends entirely on whether Stage 2 outputs are pre-winsorized. | `build_h5_dispersion_panel.py`: no winsorize call | MINOR | Implicit assumption about upstream processing | If Stage 2 does not winsorize, extreme linguistic variable values enter regressions raw. The LaTeX table note "Variables winsorized at 1%/99%" would be inaccurate for these variables. | Verify Stage 2 winsorization or add explicit winsorization in the panel builder. Document the full winsorization chain. |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why | Thesis impact |
|----|--------|-------------------|-------------------|-----|---------------|
| C-res-1 | H5.md Section C | CRITICAL (fyearq issue) | CRITICAL | Correctly identified and resolved. The fix is verified in code. | Resolved -- no longer blocks |
| C-res-2 | H5.md Section C | CRITICAL (PDF column) | CRITICAL | Correctly identified and resolved. PDF in engine COLUMNS dict verified. | Resolved -- no longer blocks |
| C-res-3 | H5.md Section C | MAJOR (120-day fence) | MAJOR | Correctly identified and resolved. Tolerance parameter verified in merge_asof. | Resolved -- no longer blocks |
| C-res-4 | H5.md Section C | MAJOR (cache key) | MAJOR | Correctly identified and resolved. Cache key includes fpi/pdf (lines 81-82). | Resolved -- no longer blocks |
| C-res-5 | H5.md Section C | MAJOR (ROABuilder) | MAJOR | Correctly identified and resolved. ROABuilder in builders dict (line 107). | Resolved -- no longer blocks |
| C-res-6 | H5.md Section C | MAJOR (winsorization) | MAJOR | Correctly identified and resolved. Pooled 1%/99% in PostCallDispersionBuilder. | Resolved -- no longer blocks |
| MI-1 | Red-team | N/A | MAJOR | PanelOLS duplicate index affects interpretation of within-estimator. Not a crash bug but an econometric interpretation concern. | Requires disclosure or verification |
| MI-2 | Red-team | N/A | MAJOR (doc) / MINOR (functional) | Documentation systematically misstates FPI filter. Functionally defensible. | Requires documentation correction |
| MI-4 | Red-team | N/A | MAJOR (thesis standard) | No identification discussion. | Blocks thesis without supplementary discussion |
| MI-5 | Red-team | N/A | MAJOR (thesis standard) | No robustness. | Blocks thesis without supplementary tests |
| MI-3 | Red-team | N/A | MINOR | check_rank=False is non-standard but not harmful with drop_absorbed=True. | Cosmetic / best practice |
| MI-6 | Red-team | N/A | MINOR | ddof=1 convention well-known; affects magnitude not ranking. | Documentation only |
| MI-7 | Red-team | N/A | MINOR | CCM linking is standard; documentation gap only. | Documentation only |
| MI-8 | Red-team | N/A | MINOR | Linguistic variable winsorization chain unclear. | Requires verification |

---

## I. Completeness Gaps

| Area | Why incomplete | Evidence | Severity | What should have been included |
|------|----------------|----------|----------|-------------------------------|
| Identification strategy | Provenance doc does not discuss threats to causal interpretation | Absence from H5.md | MAJOR | Discussion of reverse causality (managers adjust speech based on expected dispersion), simultaneity, and OVB. PreCallDispersion as control partially addresses this but is insufficient. |
| Robustness specification | No robustness tests documented or planned | Only 4 specs varying FE/controls | MAJOR | At minimum: alternative timing windows, placebo tests, subsample checks, alternative clustering |
| Verification log | No evidence of pipeline execution or output inspection | No output statistics, no sample sizes from actual runs | MAJOR | Should include at minimum: actual sample sizes, R-squared values, key coefficient signs from a run |
| Winsorization chain | Winsorization documented for DV but not traced for all variables | PostCallDispersion: builder-level pooled. Compustat controls: engine-level per-year. Linguistic IVs: undocumented. | MINOR | Full variable-by-variable winsorization register |
| IBES FPI filter | Documentation states FPI=6 throughout; engine loads FPI=['6','7'] | Code vs. documentation mismatch | MINOR-MAJOR | Accurate description of what the engine actually loads |
| PanelOLS index behavior | Not discussed despite call-level data with fiscal-year time index | set_index creates duplicates | MAJOR | Discussion of how PanelOLS handles non-unique (entity, time) pairs |
| Prior audit relationship | H5.md does not reference or supersede the old red-team audit in `docs/provenance/Audits/H5_red_team.md` | Both documents exist | MINOR | Explicit statement that the prior audit applies to the pre-redesign code and is superseded |

---

## J. Reproducibility Assessment

| Step | Documented? | Verified? | Hidden dependency? | Risk | Note |
|------|-------------|-----------|-------------------|------|------|
| Panel build: `python -m f1d.variables.build_h5_dispersion_panel` | YES (D) | Not executed | Yes: requires master_manifest.parquet, IBES yearly files, Compustat, CCM linking table, config YAML files | Medium | Command is correct per module structure. Depends on `get_latest_output_dir` for manifest path resolution. |
| Dry-run: `python -m f1d.econometric.run_h5_dispersion --dry-run` | YES (D) | Not executed | No: only validates config constants | Low | Useful sanity check. Only prints variable counts, does not load data. |
| Full run: `python -m f1d.econometric.run_h5_dispersion` | YES (D) | Not executed | Yes: requires panel parquet from previous step; depends on `get_latest_output_dir` for panel resolution | Medium | Should work if panel step completed successfully. |
| Environment/packages | NOT documented | N/A | Yes: linearmodels, pandas, numpy, pyarrow versions affect results | Medium | No requirements.txt or version pinning documented in H5.md |
| Input data versions | NOT documented | N/A | Yes: IBES Detail yearly files, Compustat parquet, CCM parquet -- no hashes or dates | High | A replicator would not know which data vintage was used |
| Output validation | NOT documented | N/A | N/A | Medium | No expected output statistics to compare against |

---

## K. Econometric Meta-Audit

| Dimension | Adequate? | Why | Weak points | Severity |
|-----------|-----------|-----|-------------|----------|
| Identification strategy | NO | Not discussed in provenance doc | Reverse causality: managers may adjust speech when aware of analyst disagreement. PreCallDispersion as control is necessary but not sufficient -- it controls for level but not for the information flow from analyst community to management. | MAJOR |
| Inference / clustering | YES | Firm-clustered SEs correctly implemented | Could consider two-way clustering (firm + time) as robustness | MINOR |
| FE specification | YES | Industry(FF12)/Firm + FiscalYear FE well-specified | Industry FE uses other_effects (correct for PanelOLS); Firm FE uses EntityEffects (correct). FiscalYear as time FE is appropriate for annual variation. | -- |
| Within-variation exploitation | PARTIAL | Firm FE specs absorb firm-level heterogeneity | With fiscal-year time FE, identification comes from within-firm deviations from annual average. Adequate if enough within-firm-year variation exists. | MINOR |
| Standard error validity | YES | Entity clustering appropriate for call-level panel nested within firms | Robust to within-firm serial correlation and heteroskedasticity | -- |
| Model specification | PARTIAL | 4 specs adequate for main results | No interaction terms, no nonlinear specifications, no quantile regressions | MINOR |
| Economic magnitude | NOT ASSESSED | No output from actual runs in the provenance doc | Cannot evaluate without results | -- |
| Multicollinearity | NOT ASSESSED | 4 simultaneous IVs (CEO/Manager x QA/Pres) likely correlated | VIF or correlation matrix not documented | MINOR |
| Timing alignment | YES | Post-call dispersion at +3 trading days; pre-call at -1 trading day | Well-defined and literature-consistent | -- |
| Lagged DV control | YES | PreCallDispersion included in all specs | Controls for persistence in dispersion levels; appropriate for change interpretation | -- |

---

## L. Audit-Safety Assessment

| Risk | Evidence | Severity | Why it matters | Fix |
|------|----------|----------|----------------|-----|
| Provenance doc mistaken for audit | H5.md is titled "Provenance & Reproducibility & Referee Audit" but contains no adversarial testing, no output verification, no identification critique | Medium | A committee member reading "Referee Audit" would expect adversarial evaluation and find none | Retitle as "Provenance & Design Document" or add genuine audit content |
| Stale prior red-team audit | `docs/provenance/Audits/H5_red_team.md` dated 2026-03-15 audits pre-redesign code that no longer exists. It references `delta_dispersion`, `dispersion_lead`, and multi-sample architectures that are completely gone. | Medium | A reader finding this file would be confused about which audit applies | Archive or delete the old audit; add explicit supersession note |
| FPI documentation error propagates | Every documentation layer (builder docstring, provenance doc, LaTeX table metadata) states FPI=6 only. The engine loads FPI=['6','7']. If a replicator implements FPI=6 only, they will get different results. | Medium | Replication failure risk | Correct all FPI documentation to match actual engine behavior |
| No output artifacts referenced | H5.md documents no actual output directory, sample size, or coefficient from a run | Low | Cannot verify that the redesigned code has been successfully executed | Add at least one reference run with key statistics |

---

## M. Master Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Fix | Blocks thesis? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----|----------------|
| MI-1 | Implementation concern | Econometric | YES | MAJOR | `run_h5_dispersion.py` line 291 | PanelOLS duplicate multi-index: set_index(["gvkey", "fyearq_int"]) with call-level data creates non-unique (entity, time) pairs. ~3-4 calls per firm-year typical. | Code line 291; call-level panel with fiscal-year time index | Entity demeaning (firm FE specs) groups correctly by gvkey. Time demeaning treats all calls in same firm-year identically. SEs should be robust due to entity clustering. Main risk: interpretation, not bias. | Document behavior; optionally verify with unique time index. Consider fyearq+fqtr as time index. | Conditional -- needs disclosure |
| MI-2 | Documentation error | Variable construction | YES | MAJOR (doc) | `_ibes_detail_engine.py` line 64; `postcall_dispersion.py` line 15; `H5.md` A3 | FPI stated as '6' only throughout documentation; engine loads ['6','7']. Dispersion computed from all estimates targeting same fpedats regardless of FPI. | Engine default vs. all documentation | Replicator implementing FPI=6 only would get different results. Functionally, pooling is defensible. | Correct all documentation. Add justification for FPI pooling. | No (functional) / Yes (documentation accuracy) |
| MI-3 | Implementation concern | Econometric | YES | MINOR | `run_h5_dispersion.py` line 305 | `check_rank=False` suppresses rank-deficiency detection in industry FE spec | Code line 305 | Could mask absorbed-variable issues; mitigated by drop_absorbed=True | Remove check_rank=False | No |
| MI-4 | Completeness gap | Identification | YES | MAJOR | H5.md (absence) | No identification strategy discussion | Document scope | Committee will require identification discussion | Add identification section | Yes (thesis standard) |
| MI-5 | Completeness gap | Robustness | YES | MAJOR | H5.md (absence); `run_h5_dispersion.py` (absence) | No robustness tests | Only 4 main specs exist | Committee will require robustness evidence | Implement robustness specifications | Yes (thesis standard) |
| MI-6 | Implementation detail | Variable construction | YES | MINOR | `postcall_dispersion.py` line 266 | std() uses ddof=1; with 2 analysts, sample std is sqrt(2) times population std | pandas default | Magnitude inflation for low-coverage calls | Document convention | No |
| MI-7 | Documentation gap | Data provenance | YES | MINOR | `_ibes_detail_engine.py` lines 115-121 | CCM linking: LINKPRIM in ['P','C'], first duplicate kept | Code inspection | Small mislink risk | Document | No |
| MI-8 | Documentation gap | Winsorization | YES | MINOR | `build_h5_dispersion_panel.py` (absence) | Linguistic IVs not explicitly winsorized in panel builder | No winsorize call in builder | LaTeX note "Variables winsorized at 1%/99%" may be inaccurate for IVs | Verify Stage 2 winsorization | No |

---

## N. What Committee Would Not Know

1. **The PanelOLS multi-index has duplicates.** With ~3-4 calls per firm-year, the (gvkey, fyearq_int) index is non-unique. The provenance document does not discuss how PanelOLS handles this or what it means for the entity/time demeaning. A committee member would assume each observation has a unique (entity, time) pair.

2. **The IBES engine loads both FPI=6 and FPI=7 estimates.** Every layer of documentation says FPI=6 only. A replicator following the documentation would get different dispersion values than the actual code produces.

3. **Winsorization is fragmented across three different locations** with different strategies (pooled for DV in builder, per-year for Compustat controls in engine, unknown for linguistic variables). The blanket "Variables winsorized at 1%/99%" in the LaTeX notes obscures this heterogeneity.

4. **There is no evidence the redesigned code has been executed.** The provenance document describes the design but cites no output directory, no sample sizes from an actual run, no coefficient values. The old red-team audit in `docs/provenance/Audits/H5_red_team.md` audits completely different code.

5. **No identification strategy has been articulated.** The hypothesis that speech uncertainty predicts analyst dispersion faces the obvious challenge that uncertain managers may be uncertain precisely because they know analysts disagree, or because both are driven by the same underlying information environment. PreCallDispersion controls for level persistence but not for the information channel.

6. **No robustness tests exist.** The 4 specifications vary FE type and control sets, but no alternative timing windows, placebo tests, IV strategies, or subsample analyses are implemented.

---

## O. Priority Fixes

| Priority | Fix | Why | Effort | Credibility gain |
|----------|-----|-----|--------|------------------|
| 1 | **Add identification discussion** to provenance document or separate audit | Committee will demand it; currently absent entirely | Low (writing) | High -- addresses the most obvious gap for any econometrics referee |
| 2 | **Correct FPI documentation** throughout: builder docstrings, provenance doc, metadata. State FPI in ['6','7'] with justification for pooling. | Factual error that would cause replication failure | Low | High -- removes a falsifiable documentation error |
| 3 | **Execute and document a reference run** with key statistics: sample sizes per spec, R-squared, key IV coefficient signs | Currently no evidence the redesigned code runs successfully | Medium | High -- proves the implementation works |
| 4 | **Add robustness specifications**: alternative DV timing (+1 and +5 days), pre-call placebo test, subsample by analyst coverage | Zero robustness is thesis-blocking | High | Critical -- transforms from exploratory to thesis-standard |
| 5 | **Document PanelOLS duplicate-index behavior**: verify coefficients match manually-demeaned version or document why duplicates are acceptable | Econometric interpretation concern | Medium | Medium -- preempts committee questions |
| 6 | **Archive or supersede old red-team audit** at `docs/provenance/Audits/H5_red_team.md` which references completely different (pre-redesign) code | Stale audit causes confusion | Low | Medium -- removes outdated conflicting information |
| 7 | **Trace and document full winsorization chain** per variable: which variables are winsorized, where, and how (pooled vs. per-year) | Current blanket claim is imprecise | Low | Low-Medium |
| 8 | **Remove `check_rank=False`** from industry FE specification | Suppresses useful diagnostic; not needed with drop_absorbed=True | Trivial | Low |

---

## P. Final Readiness Statement

**Is the first-layer document factually correct?**
Mostly yes. Of 23 verified claims, 21 are fully confirmed. Two are partially correct: (1) FPI is documented as '6' but the engine loads ['6','7'], and (2) file_name is listed as the unique record identifier but is not loaded by the regression runner. The resolved issues in Section C are all verified as correctly fixed in the current code.

**Is the first-layer document complete enough for thesis-standard review?**
No. It is a design/provenance document, not an adversarial audit. It lacks: identification critique, robustness assessment, verification log with output statistics, econometric implementation review, and evidence of successful execution. These gaps are structural (document scope) rather than errors of commission.

**Did it miss material issues?**
Yes. The two most material missed issues are:
1. The PanelOLS duplicate multi-index (MI-1), which persists from the old architecture and affects econometric interpretation.
2. The FPI documentation mismatch (MI-2), which would cause replication failure for anyone following the documentation.

**Any unsupported/exaggerated claims?**
Three claims are imprecise (E1-E3), none are fabricated. The most consequential is the FPI='6' claim which appears in the provenance doc, builder docstrings, and LaTeX notes -- all incorrect relative to the engine's actual behavior.

**Overall suite readiness:**
The H5 redesign represents a substantial improvement over the prior implementation (which had a broken DV, stale architecture, and provenance crisis). The current implementation is architecturally sound. However, thesis submission requires: (1) an identification strategy discussion, (2) robustness tests, (3) FPI documentation correction, and (4) evidence from an actual executed run. With these additions, the suite would be thesis-ready.

**Can the committee trust the first-layer document?**
As a design/provenance record: yes, with the FPI correction. As a standalone thesis audit: no -- it requires supplementation with adversarial evaluation covering identification, robustness, and output verification.
