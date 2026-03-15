# Codebase Concerns

**Analysis Date:** 2026-03-15

## Tech Debt

**Massive Stats Module (God Object):**
- Issue: `src/f1d/shared/observability/stats.py` is 5,350 lines -- a single monolithic file containing all observability statistics functions for every pipeline stage. It exports 50+ functions and has grown into a god object.
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Difficult to navigate, slow to import, high merge conflict risk. Any change to one stage's stats risks breaking another.
- Fix approach: Split into per-stage stat modules (e.g., `stats_linking.py`, `stats_tenure.py`, `stats_tokenize.py`) and re-export from `stats/__init__.py`.

**Econometric Module Uses print() Instead of Logger:**
- Issue: The entire `src/f1d/econometric/` package uses `print()` for all output (1,088 occurrences across 19 active files) with zero `logger` calls. The shared module has structured logging (`structlog`) configured and used elsewhere. Econometric scripts rely on a `DualWriter` that captures stdout to log files, but this bypasses log levels, filtering, and structured context.
- Files: All files in `src/f1d/econometric/`, especially `run_h1_cash_holdings.py` (58 prints), `run_h0_2_ceo_clarity.py` (60 prints), `run_h9_takeover_hazards.py` (73 prints), `run_h7_illiquidity.py` (61 prints)
- Impact: Cannot filter by log level, no structured metadata, inconsistent with `src/f1d/shared/` which uses `logger`. Error messages go to `print(... file=sys.stderr)` which the DualWriter may not capture.
- Fix approach: Replace `print()` calls with `logger.info()` / `logger.warning()` / `logger.error()`. Keep DualWriter as a handler but route through the logging framework.

**Duplicated Regression Boilerplate Across Econometric Scripts:**
- Issue: Each `run_h*.py` script (16 active files, 600-1,043 lines each) contains its own copy of: panel loading, sample filtering, industry split logic, minimum-calls filter, regression loop, LaTeX table generation, output directory setup, and manifest generation. The `run_regression()` function is defined independently in every single file with near-identical structure.
- Files: `src/f1d/econometric/run_h1_cash_holdings.py`, `src/f1d/econometric/run_h2_investment.py`, `src/f1d/econometric/run_h3_payout_policy.py`, `src/f1d/econometric/run_h4_leverage.py`, `src/f1d/econometric/run_h5_dispersion.py`, `src/f1d/econometric/run_h6_cccl.py`, `src/f1d/econometric/run_h7_illiquidity.py`, `src/f1d/econometric/run_h9_takeover_hazards.py`, `src/f1d/econometric/run_h11_prisk_uncertainty.py`, `src/f1d/econometric/run_h11_prisk_uncertainty_lag.py`, `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, `src/f1d/econometric/run_h12_div_intensity.py`, `src/f1d/econometric/run_h13_1_capex.py`, `src/f1d/econometric/run_h13_2_employment.py`, `src/f1d/econometric/run_h14_bidask_spread.py`
- Impact: Bug fixes must be applied to 15+ files. Inconsistencies creep in (e.g., some use `Optional[str]`, others use `str | None` for the same parameter). Total econometric source is ~11,000 lines; estimated 40-50% is duplicated scaffolding.
- Fix approach: Extract a `RegressionRunner` base class or `run_hypothesis()` orchestrator function into `src/f1d/shared/` that handles panel loading, sample splitting, output directory creation, manifest generation, and LaTeX table writing. Each hypothesis script provides only its specification config (variables, controls, model type).

**H11 Triplicated Scripts (Lag/Lead/Contemporaneous):**
- Issue: `run_h11_prisk_uncertainty.py` (555 lines), `run_h11_prisk_uncertainty_lag.py` (616 lines), and `run_h11_prisk_uncertainty_lead.py` (620 lines) are nearly identical scripts that differ only in which PRiskQ variable (contemporaneous, lag, lead) is used as the independent variable. Same for the corresponding panel builders.
- Files: `src/f1d/econometric/run_h11_prisk_uncertainty.py`, `src/f1d/econometric/run_h11_prisk_uncertainty_lag.py`, `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`, `src/f1d/variables/build_h11_prisk_uncertainty_panel.py`, `src/f1d/variables/build_h11_prisk_uncertainty_lag_panel.py`, `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py`
- Impact: ~1,800 lines of near-duplicate code across 3 econometric scripts and 3 panel builders. Any fix to H11 logic requires triple application.
- Fix approach: Parameterize with a `timing` argument (`contemporaneous`, `lag`, `lead`) in a single script.

**Archived Code Committed to Git:**
- Issue: Two archive directories are tracked in git: `_archived/` (549 MB, containing H10 hypothesis code and docs) and `.archive/` (18 MB, containing H8 removal artifacts including output data files). The `.gitignore` has `_archive/` (without 'd') but not `_archived/`, so the larger directory was never excluded.
- Files: `_archived/h10_tone_at_top/` (code + docs), `.archive/h8_removal/` (code + outputs + cache)
- Impact: Repository bloat (567 MB of archived data in git history). Clone times are unnecessarily long. Output parquet/CSV files in `.archive/` should never be in version control.
- Fix approach: Remove from tracking with `git rm -r --cached _archived/ .archive/`, add `_archived/` and `.archive/` to `.gitignore` (`.archive/` is already partially covered but the pattern `_archive/` misses `_archived/`). Consider `git filter-repo` to purge from history if size is a concern.

**Inconsistent Type Annotation Style:**
- Issue: Some econometric scripts use `Optional[str]` (old style) while others use `str | None` (PEP 604, Python 3.10+). The project targets Python 3.9+ per `pyproject.toml`, but `str | None` is not valid at runtime in 3.9 without `from __future__ import annotations`.
- Files: `src/f1d/econometric/run_h3_payout_policy.py`, `src/f1d/econometric/run_h4_leverage.py`, `src/f1d/econometric/run_h5_dispersion.py` use `str | None`; others use `Optional[str]`
- Impact: May fail on Python 3.9 if `from __future__ import annotations` is not present (it IS present in most files via line 1 imports, but the inconsistency signals lack of convention enforcement).
- Fix approach: Standardize on one style. Since the codebase already uses `from __future__ import annotations`, `str | None` is safe. Enforce via ruff rule.

## Known Bugs

**pandas/numpy Compatibility Issue in Financial Utils:**
- Symptoms: Two tests are marked `@pytest.mark.xfail` due to pandas/numpy compatibility issues with `.clip()` and `.fillna()` internal `sum()` operations.
- Files: `tests/unit/test_financial_utils.py` (lines 687, 724)
- Trigger: Running `test_winsorize_parameter_affects_output` or `test_handles_missing_xrdq_treats_as_zero` with certain pandas/numpy version combinations.
- Workaround: Tests are marked xfail so CI passes. The underlying financial utils functions (`compute_financial_controls_quarterly`) may produce unexpected results with edge-case inputs.

**H9 Test Suite Disabled on Windows:**
- Symptoms: Two H9 regression tests are permanently skipped with `reason="Module has subprocess I/O cleanup issues on Windows"` and `reason="Subprocess I/O cleanup issues on Windows"`.
- Files: `tests/unit/test_h9_regression.py` (lines 320, 327)
- Trigger: Running tests on Windows (the development platform).
- Workaround: Tests are `@pytest.mark.skip`. H9 module has no regression test coverage on Windows.

**Stale Test Fixture for H9:**
- Symptoms: The H9 test fixture (`sample_h9_data`) generates data with columns like `guidance_precision` which do not match the actual H9 module's Cox proportional hazards implementation (which uses survival analysis with takeover indicators, not guidance precision). The test docstring says "Tests verify data loading for H9-specific variables (earnings guidance precision)" which is incorrect.
- Files: `tests/unit/test_h9_regression.py` (line 30-50)
- Trigger: Test fixture was written for an earlier H9 specification and never updated when H9 was rewritten as a survival analysis module.
- Workaround: Tests are skipped anyway due to the Windows I/O issue, masking this problem.

## Security Considerations

**No Critical Security Issues Detected:**
- Risk: Low. This is a research data processing pipeline, not a web application. No user input from untrusted sources.
- Files: `.gitignore` properly excludes `.env`, credentials, and key files.
- Current mitigation: Bandit security scanning configured in `pyproject.toml`. Subprocess validation module (`src/f1d/shared/subprocess_validation.py`) validates paths before shell operations.
- Recommendations: The `bash.exe.stackdump` file in the project root should be added to `.gitignore` and removed from the working directory.

**`nul` File in Project Root:**
- Risk: A Windows `nul` device artifact exists as a physical file in the project root. This is a Windows quirk where redirecting output to `NUL` sometimes creates a file.
- Files: `nul` (project root)
- Current mitigation: Listed in `.gitignore` so not tracked, but pollutes the working directory.
- Recommendations: Delete the file. Ensure scripts do not create it.

## Performance Bottlenecks

**Excessive DataFrame Copies in Econometric Scripts:**
- Problem: Econometric scripts make numerous `.copy()` calls (124 total across 21 files, averaging 6 per file). Many of these copies are defensive but unnecessary, doubling memory usage for large panels.
- Files: `src/f1d/econometric/run_h7_illiquidity.py` (13 copies), `src/f1d/econometric/run_h12_div_intensity.py` (7 copies), `src/f1d/econometric/run_h13_1_capex.py` (7 copies)
- Cause: Each industry sample split and regression specification creates a full DataFrame copy. For panels with ~50k+ rows and 30+ columns, this is significant.
- Improvement path: Use DataFrame views or `.loc[]` slicing where mutation is not needed. Only copy when the downstream code modifies data in place.

**Observability Stats Module Import Weight:**
- Problem: `src/f1d/shared/observability/stats.py` is 5,350 lines and is imported as part of the observability package. Even if only one stats function is needed, the entire module is parsed.
- Files: `src/f1d/shared/observability/stats.py`
- Cause: Single-file design for all pipeline stage statistics.
- Improvement path: Split into submodules with lazy imports.

## Fragile Areas

**Econometric Output Directory Resolution:**
- Files: All `src/f1d/econometric/run_h*.py` files, `src/f1d/shared/path_utils.py`
- Why fragile: Each econometric script independently resolves its panel input via `get_latest_output_dir()` which finds the latest timestamped directory. If two pipeline runs overlap or a partial run leaves an incomplete output directory, the wrong panel may be loaded. The `except Exception as e` catch-all pattern (58 occurrences across 32 files) masks resolution failures.
- Safe modification: When changing path resolution logic in `path_utils.py`, test against all hypothesis scripts. The broad `except Exception` catches may hide new errors.
- Test coverage: Path utils has ~86% coverage, but the interaction between `get_latest_output_dir()` and each hypothesis script's loading logic is not integration-tested.

**LaTeX Table Generation:**
- Files: `src/f1d/shared/latex_tables_accounting.py` (811 lines), `src/f1d/shared/latex_tables.py`, `src/f1d/shared/latex_tables_complete.py`
- Why fragile: Three separate LaTeX table modules exist with overlapping functionality. `latex_tables_accounting.py` is the primary one used by econometric scripts, but `latex_tables.py` and `latex_tables_complete.py` also exist. Changes to table formatting in one module do not propagate to others.
- Safe modification: Determine which module is actually used by each hypothesis script before modifying. `latex_tables_accounting.py` is the canonical one for Accounting Review style output.
- Test coverage: No dedicated tests for LaTeX table generation modules.

**Warning Suppression via Custom showwarning:**
- Files: `src/f1d/econometric/run_h9_takeover_hazards.py` (lines 91-94)
- Why fragile: H9 monkey-patches `warnings.showwarning` to route warnings through `print()` for DualWriter capture. This is a global side effect that affects all warnings in the Python process. If H9 is imported as a module rather than run as a script, it will change warning behavior for all other code.
- Safe modification: Use `warnings.formatwarning` or a logging filter instead. Scope the change to a context manager.
- Test coverage: No test coverage for warning routing behavior.

## Scaling Limits

**Single-Process Execution:**
- Current capacity: Each hypothesis test runs as a single-process Python script. The pipeline processes ~50k panel observations across 15 hypothesis tests sequentially.
- Limit: Adding more hypotheses or larger panels linearly increases total execution time. No parallelism within or across hypothesis tests.
- Scaling path: Hypothesis tests are independent and can run in parallel. A task runner (e.g., `make -j`, `dask`, or simple `multiprocessing`) could execute all 15 H-tests simultaneously.

## Dependencies at Risk

**linearmodels Version Constraint:**
- Risk: `linearmodels>=0.6.0` is a loose lower bound. The `PanelOLS` API has changed across versions. The codebase uses `cov_type="clustered"` and `cluster_entity=True` which are version-specific parameter names.
- Impact: Upgrading linearmodels could silently change regression behavior or break the API.
- Migration plan: Pin to a specific major version range (e.g., `linearmodels>=6.0,<7.0`). Add regression tests that verify coefficient values.

**lifelines Optional Import Pattern:**
- Risk: `src/f1d/econometric/run_h9_takeover_hazards.py` wraps `lifelines` import in try/except and sets `LIFELINES_AVAILABLE = False` on failure. If lifelines is not installed, the script prints a warning but proceeds until it crashes at runtime when trying to use `CoxTimeVaryingFitter`.
- Impact: Fails late with an unhelpful `NoneType` error rather than failing fast.
- Migration plan: Fail at import time with a clear error message, or check `LIFELINES_AVAILABLE` at the top of `main()` and exit immediately.

## Missing Critical Features

**No Automated Pipeline Orchestration:**
- Problem: There is no pipeline runner or DAG. Each stage (sample, text, variables, econometric) is run as individual scripts. Dependencies between stages are documented in docstrings but not enforced programmatically.
- Blocks: Cannot run the full pipeline with a single command. Manual sequencing of 30+ scripts is error-prone.

**No LaTeX Table Tests:**
- Problem: The three LaTeX table generation modules (`latex_tables.py`, `latex_tables_accounting.py`, `latex_tables_complete.py`) totaling ~1,800+ lines have zero test coverage.
- Blocks: Table formatting changes cannot be validated automatically. Regression risk for thesis output.

## Test Coverage Gaps

**Econometric Module (Stage 4) Has Minimal Unit Test Coverage:**
- What's not tested: The `run_regression()` function in each hypothesis script is not tested with real regression execution. Tests exist for some hypotheses but many are `skipif` gated on `linearmodels` availability or skipped for Windows I/O issues.
- Files: `src/f1d/econometric/run_h*.py` (16 active files)
- Risk: Regression specification errors (wrong variables, wrong fixed effects, wrong clustering) go undetected. The econometric module is the final output stage of the pipeline.
- Priority: High

**Variable Builder Engines Have Limited Coverage:**
- What's not tested: The engine modules (`_compustat_engine.py` at 1,273 lines, `_crsp_engine.py`, `_ibes_engine.py`, `_ibes_detail_engine.py`, `_linguistic_engine.py`) that load and transform raw data have minimal test coverage. These are the data foundation for all downstream analysis.
- Files: `src/f1d/shared/variables/_compustat_engine.py`, `src/f1d/shared/variables/_crsp_engine.py`, `src/f1d/shared/variables/_ibes_engine.py`, `src/f1d/shared/variables/_ibes_detail_engine.py`, `src/f1d/shared/variables/_linguistic_engine.py`
- Risk: Data loading bugs could silently corrupt all hypothesis test results. Integration tests exist but are gated on real data availability.
- Priority: High

**Overall Coverage at ~25-30%:**
- What's not tested: Per `pyproject.toml` comments, overall coverage is ~25% with a threshold of 30%. Many shared modules (diagnostics, observability, regression_helpers) have 0% coverage.
- Files: `src/f1d/shared/diagnostics.py`, `src/f1d/shared/observability/`, `src/f1d/shared/regression_helpers.py`, `src/f1d/shared/latex_tables*.py`
- Risk: Untested shared utilities are used by all pipeline stages. Bugs propagate widely.
- Priority: Medium (individual tested modules have 70-97% coverage; the low overall number is diluted by untested modules)

---

*Concerns audit: 2026-03-15*
