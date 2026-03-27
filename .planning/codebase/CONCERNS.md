# Codebase Concerns

**Analysis Date:** 2026-03-25

## Critical Issues

**H9 ClarityCEO 0% Coverage (BLOCKED):**
- Issue: The primary clarity construct `ClarityCEO` has 0% coverage in the canonical H9 takeover panel. The panel builder (`src/f1d/variables/build_h9_takeover_panel.py`) attempts to merge ClarityCEO scores from upstream clarity outputs, but the merge produces all NaN values. The econometric script (`src/f1d/econometric/run_h9_takeover_hazards.py`) runs all 3 Cox models without this variable.
- Files: `src/f1d/variables/build_h9_takeover_panel.py` (lines 114-131, 450-467), `src/f1d/econometric/run_h9_takeover_hazards.py` (line 152, 175-180)
- Impact: H9 is the only survival analysis suite. Without ClarityCEO, the primary CEO communication style construct is absent from all hazard model results. This is a thesis-blocking gap.
- Fix approach: Debug the ClarityCEO merge path. The panel builder falls back to `float("nan")` at line 467 when the merge fails. Likely cause: upstream clarity residual output is not generated or the join keys (`ceo_id`, `sample`) do not align with the H9 panel.

**H7 Winsorization Gap (CONDITIONAL PASS):**
- Issue: The H7 panel builder (`src/f1d/variables/build_h7_illiquidity_panel.py`) does NOT winsorize `delta_amihud` or `pre_call_amihud`. All other continuous DVs across all other suites are winsorized via `winsorize_by_year` or `winsorize_pooled` from `src/f1d/shared/variables/winsorization.py`. The H7 provenance doc and red-team audit both flag this as a critical gap.
- Files: `src/f1d/variables/build_h7_illiquidity_panel.py` (entire file -- no `winsorize` import or call), `docs/provenance/H7.md` (line 8), `docs/provenance/Audits/H7_red_team.md` (lines 23, 198, 247)
- Impact: Amihud illiquidity is known to have extreme right-tail outliers. Without winsorization, a small number of extreme observations can drive regression coefficients. Results may not be robust. This must be resolved before thesis submission.
- Fix approach: Add `from f1d.shared.variables.winsorization import winsorize_pooled` and apply to `delta_amihud` and `pre_call_amihud` at 1%/99% after the merge step, consistent with other suites. Re-run the econometric script.

**H6 Utility Rank-Deficiency:**
- Issue: All 8 Utility-sample regressions (4 DVs x 2 model variants) in H6 fail with `ValueError: exog does not have full column rank`. The error is caught by a bare `except Exception` at line 198 of `src/f1d/econometric/run_h6_cccl.py`, printed to stderr, and silently discarded. No Utility results exist in H6 output.
- Files: `src/f1d/econometric/run_h6_cccl.py` (lines 194-200), `docs/provenance/H6.md` (lines 104, 253, 456)
- Impact: The Utility industry subsample (~72-85 firms after min-calls filter) has too few firms for firm FE + 8 controls. This is documented in provenance but the code does not degrade gracefully -- it catches ALL exceptions at line 198 including genuine bugs, then returns `None`.
- Fix approach: (1) Narrow the except clause to `ValueError` or `np.linalg.LinAlgError`. (2) Consider dropping Firm FE for Utility and running Industry FE only. (3) Document in the thesis that Utility subsample is too small for firm-level identification.

**H5b and H16 Missing Provenance Documents:**
- Issue: Three new suites (H5b Johnson DISP, H5b Wang DISP, H16 R&D/Sales) have active econometric scripts and panel builders but NO provenance documents and NO red-team audits. Every other active suite (19 of 22) has both.
- Files: `src/f1d/econometric/run_h5b_johnson_disp.py` (421 lines), `src/f1d/econometric/run_h5b_wang_disp.py` (421 lines), `src/f1d/econometric/run_h16_rd_sales.py` (844 lines), `src/f1d/variables/build_h5b_johnson_disp_panel.py`, `src/f1d/variables/build_h5b_wang_disp_panel.py`, `src/f1d/variables/build_h16_rd_sales_panel.py`
- Impact: No external verification of variable construction, no DV provenance chain, no red-team audit for correctness. These suites cannot be included in a thesis submission without provenance.
- Fix approach: Write provenance docs following the template used for H1-H15. Commission red-team audits for each.

## Technical Debt

**Massive Stats Module (God Object):**
- Issue: `src/f1d/shared/observability/stats.py` is 5,350 lines -- a single monolithic file containing all observability statistics functions for every pipeline stage.
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Difficult to navigate, slow to parse on import. Any change to one stage's stats risks breaking another.
- Fix approach: Split into per-stage stat modules and re-export from `stats/__init__.py`.

**Econometric Module Uses print() Instead of Logger (1,673 occurrences):**
- Issue: All 22 active econometric scripts use `print()` exclusively (1,673 total occurrences across 31 files including archived). Zero `logger` calls in the entire econometric package. The shared module has `structlog` configured and used elsewhere. Econometric scripts rely on `DualWriter` (used by 14 files) that captures stdout to log files, bypassing log levels, filtering, and structured context.
- Files: All files in `src/f1d/econometric/`, especially `run_h1_2_cash_constraint.py` (83 prints), `run_h9_takeover_hazards.py` (73 prints), `run_h1_1_cash_tsimm.py` (72 prints)
- Impact: Cannot filter by log level, no structured metadata, inconsistent with `src/f1d/shared/` which uses `logger`.
- Fix approach: Replace `print()` with `logger.info()` / `logger.warning()` / `logger.error()`. Keep DualWriter as a handler but route through the logging framework.

**Duplicated Regression Boilerplate Across 22 Econometric Scripts:**
- Issue: Each `run_h*.py` script contains its own copy of: panel loading, sample filtering, industry split logic, minimum-calls filter, regression loop, LaTeX table generation, output directory setup, and manifest generation. Total active econometric source is ~15,500 lines; estimated 40-50% is duplicated scaffolding.
- Files: All 22 `src/f1d/econometric/run_h*.py` files (active)
- Impact: Bug fixes must be applied to 22 files. Inconsistencies have crept in (e.g., H6 uses `from_formula` while others use constructor API; some use `Optional[str]`, others `str | None`).
- Fix approach: Extract a `RegressionRunner` base class or `run_hypothesis()` orchestrator into `src/f1d/shared/` that handles common scaffolding. Each hypothesis script provides only its spec config.

**H11 Triplicated Scripts (Lag/Lead/Contemporaneous):**
- Issue: H11 exists as 3 near-identical econometric scripts (535 + 590 + 594 = 1,719 lines) and 3 near-identical panel builders (279 + 292 + 297 = 868 lines). They differ only in which PRiskQ timing variable is used.
- Files: `src/f1d/econometric/run_h11_prisk_uncertainty.py`, `src/f1d/econometric/run_h11_prisk_uncertainty_lag.py`, `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, `src/f1d/variables/build_h11_prisk_uncertainty_panel.py`, `src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py`, `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py`
- Impact: ~2,587 lines of near-duplicate code. Any fix to H11 logic requires triple application.
- Fix approach: Parameterize with a `timing` argument in a single script.

**H5b Duplicated Scripts (Johnson vs Wang):**
- Issue: `run_h5b_johnson_disp.py` and `run_h5b_wang_disp.py` are 421 lines each and differ only in the DV variable name (`JohnsonDISP2` vs `WangDISP`). Similarly, two panel builders exist.
- Files: `src/f1d/econometric/run_h5b_johnson_disp.py`, `src/f1d/econometric/run_h5b_wang_disp.py`, `src/f1d/variables/build_h5b_johnson_disp_panel.py`, `src/f1d/variables/build_h5b_wang_disp_panel.py`
- Impact: 842 lines of near-duplicate econometric code. Note: per memory, H5b now uses Johnson (2004) DISP2, making `run_h5b_wang_disp.py` potentially dead code.
- Fix approach: Confirm whether Wang DISP is still needed. If not, archive it. If both needed, parameterize into a single script.

**Dead Code in Shared Module (1,540+ lines):**
- Issue: Three shared modules have zero imports from live code:
  - `src/f1d/shared/latex_tables.py` (553 lines) -- not imported by any live file
  - `src/f1d/shared/latex_tables_complete.py` (537 lines) -- only self-references in its own docstring
  - `src/f1d/shared/regression_helpers.py` (450 lines) -- not imported by any live file
- Files: `src/f1d/shared/latex_tables.py`, `src/f1d/shared/latex_tables_complete.py`, `src/f1d/shared/regression_helpers.py`
- Impact: 1,540+ lines of dead code that increases cognitive load and shows up in coverage reports as untested.
- Fix approach: Archive or delete. Only `latex_tables_accounting.py` (811 lines) is the canonical LaTeX table module.

**Stale Module Registries (init files and verification tests):**
- Issue: Both `src/f1d/econometric/__init__.py` and `src/f1d/variables/__init__.py` list only the original 11-12 suites. They are missing H1.1, H1.2, H5b (Johnson/Wang), H11-lag, H11-lead, H12, H12Q, H13.1, H15, H16. Similarly, `tests/verification/test_stage4_dryrun.py` and `tests/verification/test_all_scripts_dryrun.py` only list 12 original scripts -- all 10+ newer scripts are not included.
- Files: `src/f1d/econometric/__init__.py`, `src/f1d/variables/__init__.py`, `tests/verification/test_stage4_dryrun.py` (lines 43-56), `tests/verification/test_all_scripts_dryrun.py` (lines 36-68)
- Impact: Verification tests do not cover newer suites. Module docstrings are misleading. New developers cannot discover which suites are active by reading `__init__.py`.
- Fix approach: Update all four files to include the complete list of 22 active econometric scripts and 19 active panel builders.

**Archived Code in Git History:**
- Issue: `.archive/h8_removal/` (18 MB, 108 tracked files including output parquet/CSV files) and `_archived/h10_tone_at_top/` (11 tracked files) remain in git history. The `.gitignore` has `_archive/` (without 'd') but NOT `_archived/`, so the H10 directory was never excluded. Additionally, the top-level `_archived/` directory no longer exists on disk (files deleted in working tree per `git status`), but is still tracked.
- Files: `_archived/h10_tone_at_top/` (tracked, deleted from working tree), `.archive/h8_removal/` (tracked and present)
- Impact: Repository bloat. Output parquet/CSV files should never be in version control.
- Fix approach: `git rm -r --cached _archived/ .archive/`. Add `_archived/` and `.archive/` to `.gitignore`. The in-source `_archived/` directories under `src/f1d/econometric/_archived/` and `src/f1d/variables/_archived/` are correctly tracked (they contain Python source, not data).

## Performance Concerns

**Excessive DataFrame Copies in Econometric Scripts (157 occurrences):**
- Problem: 157 `.copy()` calls across 29 econometric files (including archived). Many copies are defensive but unnecessary -- industry sample splits create full DataFrame copies even when downstream code does not mutate.
- Files: `src/f1d/econometric/run_h16_rd_sales.py` (8 copies), `src/f1d/econometric/run_h1_2_cash_constraint.py` (7 copies), `src/f1d/econometric/run_h6_cccl.py` (6 copies)
- Cause: Each industry sample split and regression specification creates a full DataFrame copy.
- Improvement path: Use `.loc[]` slicing where mutation is not needed. Only copy when downstream code modifies data in place.

**Observability Stats Module Import Weight:**
- Problem: `src/f1d/shared/observability/stats.py` at 5,350 lines is imported as part of the observability package. Even if only one stats function is needed, the entire module is parsed.
- Files: `src/f1d/shared/observability/stats.py`
- Improvement path: Split into submodules with lazy imports.

**Single-Process Execution:**
- Current capacity: All 22 hypothesis tests run as independent single-process scripts. The pipeline processes ~50k-112k panel observations across 22 hypothesis tests sequentially.
- Limit: No parallelism within or across hypothesis tests.
- Scaling path: Tests are independent and can run in parallel via `make -j` or `multiprocessing`.

## Data Quality Risks

**H9 ClarityCEO Merge Failure (silent degradation):**
- Issue: `build_h9_takeover_panel.py` line 130-131 catches the missing ClarityCEO file and prints "WARNING: ClarityCEO not found -- will be NaN" but continues to build the panel. At line 467, it sets `ClarityCEO = float("nan")` for all rows. The econometric script then runs all models without realizing the key variable is entirely missing.
- Files: `src/f1d/variables/build_h9_takeover_panel.py` (lines 128-131, 465-467)
- Risk: Silent data quality degradation. The pipeline runs to completion with no error exit code, producing results that look valid but are missing the primary construct.
- Fix: Fail loudly (raise or exit non-zero) when ClarityCEO coverage is below a threshold.

**Broad Exception Catching (57 occurrences across 40 files):**
- Issue: 57 `except Exception` blocks across 40 files catch all exceptions including `KeyError`, `TypeError`, and other genuine bugs. The most dangerous pattern is in econometric scripts where regression failures are caught with bare `except Exception` and return `None` -- masking data issues as "model did not converge."
- Files: `src/f1d/econometric/run_h9_takeover_hazards.py` (4 occurrences), `src/f1d/shared/panel_ols.py` (3), `src/f1d/econometric/run_h6_cccl.py` (2), plus 34 other files
- Risk: Real bugs (wrong column name, type error, null pointer) get swallowed and produce incomplete output instead of a clear failure.
- Fix: Narrow except clauses to specific expected exceptions (`ValueError`, `np.linalg.LinAlgError`, etc.).

**Pervasive type: ignore Comments (80+ occurrences):**
- Issue: 80+ `# type: ignore` comments across the codebase suppress mypy warnings. Many are legitimate (library limitations with pandas/sklearn/lifelines), but some suppress meaningful type errors that could indicate runtime bugs.
- Files: `src/f1d/shared/output_schemas.py` (12 occurrences), `src/f1d/text/tokenize_transcripts.py` (9), `src/f1d/shared/variables/_compustat_engine.py` (8), `src/f1d/shared/iv_regression.py` (6)
- Risk: Genuine type errors hidden behind blanket suppressions. The `output_schemas.py` pattern of setting schemas to `None` when pandera is unavailable means schema validation silently becomes a no-op.
- Fix: Audit each `type: ignore` and narrow to specific error codes where possible.

## Maintenance Risks

**Econometric Output Directory Resolution:**
- Files: All 22 `src/f1d/econometric/run_h*.py` files, `src/f1d/shared/path_utils.py`
- Why fragile: Each script independently resolves its panel input via `get_latest_output_dir()` which finds the latest timestamped directory. If two pipeline runs overlap or a partial run leaves an incomplete output directory, the wrong panel may be loaded.
- Safe modification: When changing path resolution in `path_utils.py`, test against all hypothesis scripts.
- Test coverage: Path utils has ~86% coverage, but the interaction with each hypothesis script's loading logic is not integration-tested.

**LaTeX Table Generation:**
- Files: `src/f1d/shared/latex_tables_accounting.py` (811 lines -- the canonical module)
- Why fragile: Zero test coverage. This module generates thesis-quality LaTeX tables that are included directly in the paper. A formatting regression (wrong significance stars, wrong decimal places, missing controls row) would propagate to the thesis document.
- Safe modification: Always visually inspect LaTeX output after changes. Consider adding snapshot tests.
- Note: `latex_tables.py` and `latex_tables_complete.py` are dead code (see Technical Debt section).

**Warning Suppression via Monkey-Patching:**
- Files: `src/f1d/econometric/run_h9_takeover_hazards.py` (lines 91-94), `src/f1d/econometric/run_h6_cccl.py` (lines 74-77)
- Why fragile: H9 monkey-patches `warnings.showwarning` globally. H6 uses `warnings.filterwarnings("ignore")` to suppress rank-deficiency warnings that may be diagnostically important. Both are global side effects.
- Safe modification: Use context managers to scope warning changes. Route through logging framework instead.

**No Automated Pipeline Orchestration:**
- Problem: No pipeline runner or DAG. Each stage (sample, text, variables, econometric) is run as individual scripts. Dependencies between stages are documented in docstrings but not enforced. There are 19 panel builders and 22 econometric scripts that must run in a specific order.
- Blocks: Cannot run the full pipeline with a single command. Manual sequencing is error-prone.

## Test Coverage Gaps

**Zero Tests for Newer Suites (5,588+ lines untested):**
- What's not tested: H1.1 (cash_tsimm, 819 lines), H1.2 (cash_constraint, 885 lines), H5b Johnson (421 lines), H5b Wang (421 lines), H16 (rd_sales, 844 lines), H12Q (payout, 605 lines), H13.1 (competition, 831 lines), H15 (repurchase, 762 lines) have NO dedicated unit tests and are NOT included in the verification dry-run test lists.
- Files: `src/f1d/econometric/run_h1_1_cash_tsimm.py`, `src/f1d/econometric/run_h1_2_cash_constraint.py`, `src/f1d/econometric/run_h5b_johnson_disp.py`, `src/f1d/econometric/run_h5b_wang_disp.py`, `src/f1d/econometric/run_h16_rd_sales.py`, `src/f1d/econometric/run_h12q_payout.py`, `src/f1d/econometric/run_h13_1_competition.py`, `src/f1d/econometric/run_h15_repurchase.py`
- Risk: Regression specification errors (wrong variables, wrong FE, wrong clustering, wrong p-value tail) are completely undetectable by automated testing.
- Priority: High

**H9 Tests Disabled on Windows:**
- What's not tested: Two H9 regression tests are permanently skipped (`reason="Module has subprocess I/O cleanup issues on Windows"`). The test fixture (`sample_h9_data`) was written for an earlier H9 specification (earnings guidance precision) and never updated when H9 was rewritten as survival analysis. Tests are skipped anyway, masking this stale fixture.
- Files: `tests/unit/test_h9_regression.py` (lines 30-50, 320, 327)
- Risk: H9 is the only survival analysis suite and has NO effective test coverage on the development platform (Windows).
- Priority: High

**LaTeX Table Generation (1,901 lines, 0% coverage):**
- What's not tested: All three LaTeX table modules (`latex_tables.py`, `latex_tables_accounting.py`, `latex_tables_complete.py`) have zero test coverage.
- Files: `src/f1d/shared/latex_tables_accounting.py` (811 lines -- the only live one)
- Risk: Table formatting changes cannot be validated automatically. Since these produce thesis output, any regression is visible to reviewers.
- Priority: Medium (only `latex_tables_accounting.py` is live; the other two are dead code)

**Variable Builder Engines Limited Coverage:**
- What's not tested: The 5 engine modules (`_compustat_engine.py` 1,342 lines, `_crsp_engine.py` 518 lines, `_ibes_engine.py`, `_ibes_detail_engine.py`, `_linguistic_engine.py`) are the data foundation for all downstream analysis. Integration tests exist but are gated on real data availability.
- Files: `src/f1d/shared/variables/_compustat_engine.py`, `src/f1d/shared/variables/_crsp_engine.py`, `src/f1d/shared/variables/_ibes_engine.py`, `src/f1d/shared/variables/_ibes_detail_engine.py`, `src/f1d/shared/variables/_linguistic_engine.py`
- Risk: Data loading bugs could silently corrupt all hypothesis test results.
- Priority: High

**pandas/numpy Compatibility (2 xfail tests):**
- What's failing: Two tests in `tests/unit/test_financial_utils.py` (lines 687, 724) are marked `@pytest.mark.xfail` for pandas/numpy `.clip()` and `.fillna()` compatibility issues.
- Files: `tests/unit/test_financial_utils.py`
- Risk: Underlying financial utils functions may produce unexpected results with edge-case inputs.
- Priority: Low (edge cases, not main path)

**Overall Coverage ~25-30%:**
- Many shared modules have 0% coverage: `src/f1d/shared/diagnostics.py`, `src/f1d/shared/observability/`, `src/f1d/shared/regression_helpers.py` (dead code), all `latex_tables*.py`.
- Individual tested modules have 70-97% coverage (financial_utils 97.75%, data_validation 92%, iv_regression 88.21%).
- Coverage threshold is set to 30% (`pyproject.toml` line 144) but actual is ~25%.

## Security Considerations

**No Critical Security Issues:**
- This is a research data pipeline, not a web application. No untrusted user input.
- `.gitignore` properly excludes `.env`, credentials, and key files.
- Bandit security scanning configured in `pyproject.toml`.
- Subprocess validation module exists: `src/f1d/shared/subprocess_validation.py`.

**Minor Hygiene:**
- `.archive/h8_removal/` contains 108 tracked files including output data. While not a security issue, committed data files in git increase attack surface for data exfiltration.
- The `nul` file artifact in project root (Windows quirk) is in `.gitignore` but pollutes the working directory.

## Dependencies at Risk

**linearmodels Version Constraint:**
- Risk: `linearmodels>=0.6.0` is a loose lower bound. The `PanelOLS` API has changed across versions. The codebase uses `cov_type="clustered"` and `cluster_entity=True` which are version-specific.
- Impact: Upgrading could silently change regression behavior.
- Fix: Pin to specific major version range (e.g., `linearmodels>=6.0,<7.0`).

**lifelines Optional Import Pattern:**
- Risk: `src/f1d/econometric/run_h9_takeover_hazards.py` wraps `lifelines` import in try/except and sets `LIFELINES_AVAILABLE = False`. If lifelines is not installed, the script prints a warning but proceeds until it crashes at runtime.
- Fix: Fail at import time with a clear error message.

---

*Concerns audit: 2026-03-25*
