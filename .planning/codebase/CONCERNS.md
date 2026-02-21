# ALL CONCERNS RESOLVED (2026-02-21)


# Codebase Concerns

**Analysis Date:** 2026-02-20

---

## Tech Debt

**Deprecated `observability_utils.py` Still Widely Imported:**
- Issue: `src/f1d/shared/observability_utils.py` is marked `[DEPRECATED]` in its docstring. The real implementation was split into `src/f1d/shared/observability/` sub-package. However, 8 production files still import from the deprecated shim instead of the new package.
- Files: `src/f1d/econometric/generate_summary_stats.py`, `src/f1d/econometric/test_ceo_tone.py`, `src/f1d/econometric/test_takeover_hazards.py`, `src/f1d/sample/assemble_manifest.py`, `src/f1d/sample/build_sample_manifest.py`, `src/f1d/sample/build_tenure_map.py`, `src/f1d/sample/clean_metadata.py`, `src/f1d/sample/link_entities.py`, `src/f1d/shared/dual_writer.py`
- Impact: Every import goes through a re-export layer. If the shim is ever removed without updating callers, all these modules break.
- Fix approach: Update each caller to `from f1d.shared.observability import DualWriter` etc., then remove `observability_utils.py`.

**`regression_utils.py` Is Dead Code:**
- Issue: `src/f1d/shared/regression_utils.py` (119 lines) is never imported by any source file. The 3-file regression utility split (`regression_helpers.py`, `regression_utils.py`, `regression_validation.py`) left `regression_utils.py` as an orphan.
- Files: `src/f1d/shared/regression_utils.py`
- Impact: Confusion about which regression utility to use; dead code bloat.
- Fix approach: Confirm no callers exist (`grep -r "regression_utils" src/`), then delete the file.

**Econometric Stage-4 Scripts Named `test_*.py` (Confusing Convention):**
- Issue: All 10 production econometric regression scripts in `src/f1d/econometric/` are named with a `test_` prefix (e.g., `test_h1_cash_holdings.py`, `test_ceo_clarity.py`). These are NOT pytest test files — they are hypothesis-testing scripts run as `python -m f1d.econometric.test_h1_cash_holdings`. This causes confusion with pytest, which may attempt to collect them as test modules.
- Files: `src/f1d/econometric/test_h1_cash_holdings.py`, `src/f1d/econometric/test_h2_investment.py`, `src/f1d/econometric/test_h3_payout_policy.py`, `src/f1d/econometric/test_h4_leverage.py`, `src/f1d/econometric/test_h5_dispersion.py`, `src/f1d/econometric/test_h6_cccl.py`, `src/f1d/econometric/test_h7_illiquidity.py`, `src/f1d/econometric/test_h8_policy_risk.py`, `src/f1d/econometric/test_ceo_clarity.py`, `src/f1d/econometric/test_manager_clarity.py`, etc.
- Impact: Developer confusion; pytest's `--collect-only` tries to parse them; naming conflicts with the actual test suite in `tests/`.
- Fix approach: Rename to `run_h1_cash_holdings.py` or `estimate_h1_cash_holdings.py` to distinguish from pytest files.

**V1 Methodology References in `__init__.py` Without Actual V1 Subpackages:**
- Issue: Both `src/f1d/econometric/__init__.py` and `src/f1d/financial/__init__.py` document import paths like `from f1d.econometric.v1 import ...` and `from f1d.financial.v1 import ...`, but neither `v1` nor `v2` subdirectories exist inside these packages. The `src/f1d/financial/` directory contains only `__init__.py`.
- Files: `src/f1d/econometric/__init__.py`, `src/f1d/financial/__init__.py`
- Impact: Misleading documentation; following the documented import paths raises `ModuleNotFoundError`.
- Fix approach: Remove v1/v2 import guidance from `__init__.py` or create the actual subpackages.

**`observability/stats.py` Monolith (5,309 Lines, 57 Functions):**
- Issue: `src/f1d/shared/observability/stats.py` is 5,309 lines with 57+ functions spanning tokenization stats, linking stats, manifest stats, financial stats, event flags stats, and step-specific stats. It was extracted from `observability_utils.py` but was not further split.
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Extremely hard to navigate; high cognitive load; single-file merge conflicts; violates single-responsibility. Most step-specific `compute_step3X_*` functions are used only by one pipeline script.
- Fix approach: Split into per-stage stat modules (e.g., `stats_tokenize.py`, `stats_manifest.py`, `stats_financial.py`).

**`src/f1d/financial/` Module Is Empty:**
- Issue: `src/f1d/financial/` contains only `__init__.py` with documentation referencing V1/V2 subpackages. No actual financial feature scripts exist in the `src/` layout; financial features live directly in `src/f1d/variables/`.
- Files: `src/f1d/financial/__init__.py`
- Impact: Structural confusion; the module is useless as-is.
- Fix approach: Either populate with actual financial logic or remove the empty module.

---

## Known Bugs

**Two Test Files Fail to Collect Due to Missing `v1/4.3_TakeoverHazards.py`:**
- Symptoms: Running `pytest --collect-only` terminates with `FileNotFoundError` on two test files, preventing collection of the entire test suite.
- Files: `tests/regression/test_survival_analysis_integration.py`, `tests/unit/test_takeover_survival_analysis.py`
- Trigger: Both files call `runpy.run_path(str(_MODULE_PATH))` at import time where `_MODULE_PATH` is `src/f1d/econometric/v1/4.3_TakeoverHazards.py` — a path that does not exist.
- Workaround: Run pytest with `--ignore=tests/regression/test_survival_analysis_integration.py --ignore=tests/unit/test_takeover_survival_analysis.py`.
- Fix approach: Update `_MODULE_PATH` to point to the current takeover hazard script (`src/f1d/econometric/test_takeover_hazards.py`), or add a guard at module import time.

**Verification Tests Reference Non-Existent V1 Script Paths:**
- Symptoms: `tests/verification/test_stage4_dryrun.py` and `tests/verification/test_all_scripts_dryrun.py` reference 8 scripts under `src/f1d/econometric/v1/` (e.g., `4.1_EstimateCeoClarity.py`, `4.3_TakeoverHazards.py`) that do not exist on disk.
- Files: `tests/verification/test_stage4_dryrun.py`, `tests/verification/test_all_scripts_dryrun.py`
- Trigger: Any test run targeting these verification tests.
- Fix approach: Update script paths to the current `src/f1d/econometric/test_*.py` layout.

**`pytest-asyncio` Deprecation Warning on Every Test Run:**
- Symptoms: Every test run emits `PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset`. This is logged as a warning but not failing, yet indicates a future breaking change.
- Files: `pyproject.toml` (missing `asyncio_mode` or `asyncio_default_fixture_loop_scope` setting)
- Fix approach: Add `asyncio_mode = "auto"` or `asyncio_default_fixture_loop_scope = "function"` to `[tool.pytest.ini_options]` in `pyproject.toml`.

---

## Security Considerations

**No Hardcoded Secrets Detected:**
- Risk: No actual API keys or credentials appear hardcoded in source files.
- Current mitigation: `.env.example` exists; `pydantic-settings` reads from environment variables with `F1D_` prefix; `.gitignore` excludes `.env`.
- Recommendations: Ensure `.env` files are never committed (already in `.gitignore`).

**Bandit Security Scan `continue-on-error: true`:**
- Risk: The Bandit SAST step in `.github/workflows/test.yml` runs with `continue-on-error: true`, meaning security failures do not block CI.
- Files: `.github/workflows/test.yml` (line 30)
- Current mitigation: Bandit runs and uploads a report artifact.
- Recommendations: Once the baseline is clean, change `continue-on-error: false` to enforce security gates.

**`assert` Statements in Path Validation Code:**
- Risk: `src/f1d/shared/config/paths.py` uses `assert isinstance(...)` for runtime path validation. If Python is run with `-O` (optimize), assertions are stripped and the validation silently disappears.
- Files: `src/f1d/shared/config/paths.py` (lines 119, 126, 132, 138, 142)
- Current mitigation: Production runs do not appear to use `-O`.
- Recommendations: Replace `assert isinstance(x, Path)` with `if not isinstance(x, Path): raise TypeError(...)`.

---

## Performance Bottlenecks

**Whole-File Parquet Loads for Large Panels in Econometric Scripts:**
- Problem: Every econometric Stage-4 script calls `pd.read_parquet(panel_file)` loading the entire panel into memory without column filtering.
- Files: `src/f1d/econometric/test_h1_cash_holdings.py:172`, `src/f1d/econometric/test_h2_investment.py:164`, `src/f1d/econometric/test_ceo_clarity.py:168`, and 12 other econometric scripts.
- Cause: No `columns=` argument passed to `pd.read_parquet()`.
- Improvement path: Identify the columns each script actually uses and pass them explicitly to exploit Parquet column pruning.

**`src/f1d/shared/observability/stats.py` Loaded Fully on Import:**
- Problem: The 5,309-line stats module loads entirely on first import, even when only one function is needed (e.g., `compute_tokenize_input_stats`). This creates unnecessary import time for scripts that use only a small subset.
- Files: `src/f1d/shared/observability/stats.py`
- Cause: Monolithic module design; all 57 functions defined at module level.
- Improvement path: Split by stage as described under Tech Debt; lazy-load stage-specific function groups.

**63 `copy()` Calls in `src/f1d/variables/` Panel Builders:**
- Problem: Variable panel builders make 63 DataFrame `.copy()` calls, many of which may be defensive copies that create unnecessary memory allocations.
- Files: All `src/f1d/variables/build_*.py` files.
- Cause: Defensive programming pattern; not all copies are necessary if the underlying data is not mutated.
- Improvement path: Profile with `memory_profiler` to identify which copies can be eliminated using `copy=False` or in-place operations.

**IBES Engine Loads 25M-Row Parquet Unfiltered:**
- Problem: `IbesEngine._build_ibes_panel()` loads the full `tr_ibes.parquet` (~25M rows) without filtering, then filters in memory.
- Files: `src/f1d/shared/variables/_ibes_engine.py:50–166`
- Cause: No predicate pushdown applied to the parquet read.
- Improvement path: Use `pyarrow.parquet.read_table(..., filters=[...])` to push filters to the Parquet layer before loading into pandas.

---

## Fragile Areas

**`chunked_reader.py` Loads `project.yaml` on Every Call:**
- Files: `src/f1d/shared/chunked_reader.py:189–201`
- Why fragile: `process_in_chunks()` opens and parses `config/project.yaml` every invocation using a relative path computed from `__file__`. If the file is missing, it logs at DEBUG and falls back silently. If the path changes, throttling silently uses hardcoded defaults.
- Safe modification: Inject the config dict as a parameter rather than loading it internally, or use `get_config()` from `src/f1d/shared/config/loader.py` which has caching.
- Test coverage: Chunked reader is tested (`tests/unit/test_chunked_reader.py`) but the config-loading branch is not directly tested.

**CompustatEngine and CRSPEngine Singletons Lack Thread Locks:**
- Files: `src/f1d/shared/variables/_compustat_engine.py:1072–1081`, `src/f1d/shared/variables/_crsp_engine.py:377–382`
- Why fragile: Both engines use module-level singletons initialized at import time (`_engine = CompustatEngine()`). Unlike `IbesEngine` which uses `threading.Lock()`, Compustat and CRSP singletons have no thread safety mechanism. If multiple threads call `get_engine()` concurrently before initialization, a race could produce duplicate loads.
- Safe modification: In practice, `ProcessPoolExecutor` (not `ThreadPoolExecutor`) is used, so inter-process isolation protects the singleton. Document this assumption explicitly. If threads are ever used, add a `threading.Lock` pattern as in `_ibes_engine.py`.

**Output Schema Validation Is Warn-Only Everywhere:**
- Files: `src/f1d/text/build_linguistic_variables.py:592` (the only caller of `validate_linguistic_variables`), `src/f1d/shared/output_schemas.py:178`
- Why fragile: The pandera schema validation framework is designed to catch column-type and nullable violations, but `warn_only=True` means corrupted output will be silently passed downstream to econometric scripts where it fails later with less clear errors.
- Safe modification: Change to `warn_only=False` during development; add to CI test assertions that schema validation passes.
- Test coverage: Schema validation has no dedicated test; it is only exercised as a side effect of running the full pipeline.

**Integration Tests Permanently Skipped Due to Missing Fixtures:**
- Files: `tests/integration/test_pipeline_step1.py:50` (`pytest.skip("Sample input data not yet available in tests/fixtures/")`), `tests/integration/test_pipeline_step2.py`, `tests/integration/test_pipeline_step3.py`
- Why fragile: All pipeline integration tests skip immediately because real input data is not committed to the repository. These tests provide zero coverage assurance of the pipeline stages they claim to test.
- Safe modification: Create minimal synthetic fixture data in `tests/fixtures/` that exercises each pipeline step without requiring proprietary financial databases.
- Test coverage: Zero — all integration tests marked `@pytest.mark.integration` are unconditionally skipped.

**`print()` Statements as Logging in Production Code (1,274 calls):**
- Files: Most heavily in `src/f1d/econometric/generate_summary_stats.py` (40+ calls), `src/f1d/shared/variables/_compustat_engine.py` (10+ calls), `src/f1d/shared/variables/_ibes_engine.py` (4 calls), `src/f1d/text/tokenize_transcripts.py`.
- Why fragile: `print()` bypasses the structured logging system (`structlog`). Output is not captured by log handlers, cannot be filtered by log level, and cannot be redirected to log files without shell redirection. The `DualWriter` wrapper is used in some scripts but not in the shared engine modules.
- Safe modification: Replace with `logger.info()` from `logging.getLogger(__name__)` in shared modules; use `logger.debug()` for diagnostic prints.

**`FutureWarning` Suppressed Globally in 8 Scripts:**
- Files: `src/f1d/econometric/generate_summary_stats.py:51`, `src/f1d/econometric/test_ceo_clarity.py:59`, `src/f1d/econometric/test_ceo_clarity_extended.py:55`, `src/f1d/econometric/test_ceo_clarity_regime.py:73`, `src/f1d/econometric/test_ceo_tone.py:73`, `src/f1d/econometric/test_h7_illiquidity.py:47`, `src/f1d/econometric/test_h8_policy_risk.py:53`, `src/f1d/econometric/test_manager_clarity.py:59`
- Why fragile: `warnings.filterwarnings("ignore", category=FutureWarning)` is set at module level, suppressing all future warnings from all libraries for the process lifetime. This masks upcoming API changes in pandas, statsmodels, or linearmodels that could cause silent behavior changes on library upgrades.
- Safe modification: Suppress only specific warnings from known offending modules using `warnings.filterwarnings("ignore", ..., module="linearmodels.*")`.

---

## Scaling Limits

**Thread Count Locked at 1 in Config:**
- Current capacity: `config/project.yaml` sets `determinism.thread_count: 1`, meaning `tokenize_transcripts.py` runs sequentially by default.
- Limit: Sequential tokenization of multi-year transcript corpus takes ~558 seconds (per `PERFORMANCE NOTE` comment at line 1174 of `src/f1d/text/tokenize_transcripts.py`).
- Scaling path: Increase `thread_count` to match available CPU cores (tested up to 4 workers); near-linear speedup expected per the inline comment.

**No Pagination/Streaming for Econometric Panel Loads:**
- Current capacity: Econometric scripts load entire panels into memory (e.g., `pd.read_parquet(panel_file)`) with no chunk processing.
- Limit: If panel files grow beyond available RAM, scripts will OOM without warning.
- Scaling path: Implement column-pruned reads; use `pyarrow` table scan with filter pushdown; process in year-group chunks where regressions permit.

---

## Dependencies at Risk

**`statsmodels==0.14.6` Pinned with Known Breaking Changes at 0.14.0:**
- Risk: `requirements.txt` documents: *"Pinned to 0.14.6 for reproducible regression analysis. 0.14.0 introduced breaking changes (deprecated GLM link names)."* The pin prevents security and bug fixes in 0.14.7+.
- Impact: Downstream upgrade of linearmodels may require a newer statsmodels, creating a version conflict.
- Migration plan: See `docs/` for `DEPENDENCIES.md` (referenced in `requirements.txt`); test upgrade to latest 0.14.x in a branch.

**`pyarrow==21.0.0` Pinned for Python 3.8 Compatibility:**
- Risk: `requirements.txt` documents: *"Pinned to 21.0.0 for Python 3.8-3.13 compatibility. 23.0.0+ requires Python >= 3.10."* This is an unusually aggressive pin that lags several major versions.
- Impact: Missing performance improvements and bug fixes in pyarrow 22+. The `pyproject.toml` declares `requires-python = ">=3.9"`, but the pyarrow pin is justified by 3.8 compatibility — a contradiction.
- Migration plan: Drop Python 3.8 from the support matrix (already dropped in `pyproject.toml`), then upgrade pyarrow pin to >=22.0.

**`linearmodels` and `lifelines` Not Pinned in `requirements.txt`:**
- Risk: `requirements.txt` does not include `linearmodels` or `lifelines` despite both being used in production econometric scripts (`test_ceo_clarity.py`, `test_takeover_hazards.py`). They are declared as optional in source (`try: import linearmodels`).
- Impact: CI/CD installs may pull incompatible versions; reproducibility of regression results is not guaranteed.
- Migration plan: Add explicit version pins for `linearmodels>=0.60` and `lifelines>=0.28` to `requirements.txt`; remove the try/except import guards or add explicit `pytest.skip` for missing optional deps in tests.

---

## Missing Critical Features

**No Fixture Data for Integration Tests:**
- Problem: `tests/fixtures/` directory exists but contains no synthetic data. All integration tests that run pipeline stages skip unconditionally.
- Blocks: True end-to-end pipeline testing in CI without proprietary input data; confidence in stage boundary contracts.

**Output Schema Validation Not Applied to Financial/Econometric Outputs:**
- Problem: `src/f1d/shared/output_schemas.py` defines only 6 schemas (linguistic variables, firm controls, event flags, manager clarity, investment residual, PRisk uncertainty). Financial variable panel outputs and econometric regression outputs have no pandera schemas.
- Blocks: Automated verification that intermediate parquet files passed between stages maintain expected schema contracts.

---

## Test Coverage Gaps

**Econometric Regression Scripts (Stage 4) Have No Unit Tests:**
- What's not tested: The 10+ `src/f1d/econometric/test_*.py` scripts (hypothesis regression logic, LaTeX table generation, hypothesis significance evaluation). `tests/unit/test_h1_regression.py` through `test_h9_regression.py` exist but test regression *helper utilities*, not the full econometric script logic.
- Files: `src/f1d/econometric/test_h1_cash_holdings.py` through `test_h8_policy_risk.py`, `test_ceo_clarity.py`, `test_manager_clarity.py`
- Risk: Regression logic changes (significance thresholds, variable selection, output formatting) can silently produce incorrect academic results.
- Priority: High — these scripts produce the final thesis outputs.

**Variable Builder Panel Scripts Have No Tests:**
- What's not tested: `src/f1d/variables/build_h3_payout_policy_panel.py`, `build_h4_leverage_panel.py`, `build_h5_dispersion_panel.py`, `build_h6_cccl_panel.py`, `build_h7_illiquidity_panel.py`, `build_h8_policy_risk_panel.py`. Tests exist for H1 and H2 variable building but not for H3–H8.
- Files: `src/f1d/variables/build_h3_payout_policy_panel.py` through `build_h8_policy_risk_panel.py`
- Risk: Incorrect variable construction (winsorization, merge logic, lag computation) produces silently wrong data fed to regressions.
- Priority: High.

**CI Coverage Threshold Set Below Actual Coverage:**
- What's not tested: `pyproject.toml` sets `fail_under = 30` but comments document *"Current coverage is ~25%. Target is 40%"*. The CI `test.yml` uses `--cov-fail-under=25` (even lower). Tier 1 and Tier 2 coverage gates use `--cov-fail-under=10`.
- Files: `.github/workflows/ci.yml`, `.github/workflows/test.yml`, `pyproject.toml`
- Risk: The coverage threshold is below actual coverage, providing a false sense of coverage enforcement. Regressions that drop coverage below 25% will not be caught.
- Priority: Medium — raise thresholds incrementally as new tests are added.

**`src/f1d/shared/diagnostics.py` Not Tested:**
- What's not tested: VIF diagnostics, Durbin-Watson tests, Hausman test helpers.
- Files: `src/f1d/shared/diagnostics.py`
- Risk: Diagnostic utilities used in regressions could produce incorrect statistical diagnostics silently.
- Priority: Medium.

**`src/f1d/shared/latex_tables.py` and `latex_tables_accounting.py` Not Tested:**
- What's not tested: LaTeX table rendering, significance star logic, column formatting.
- Files: `src/f1d/shared/latex_tables.py`, `src/f1d/shared/latex_tables_accounting.py`
- Risk: Formatting errors in output tables go undetected until manual review of generated `.tex` files.
- Priority: Low — cosmetic but can affect academic submission quality.

---

## Type Safety Issues (LSP/Mypy Errors)

**`src/f1d/shared/observability/stats.py` Has 30+ TypedDict Assignment Type Errors:**
- Problem: The `TypedDict` definitions (`VarStatsDict`, `CategoryStatsDict`, `DateRangeDict`) declare strict value types (e.g., `int`, `float`, `str`), but the code assigns mismatched types (e.g., `dict[str, float]` assigned to a `float` field, `float` assigned to `int` field). Pyright reports 30+ errors across lines 718–2060.
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Runtime `TypedDict` violations do not raise exceptions in Python (TypedDicts are structural only), but downstream consumers reading stats dicts may receive unexpected types. The mypy `strict` mode applied to `f1d.shared.*` should catch these but may be obscured by `ignore_missing_imports`.
- Fix approach: Fix the TypedDict field types to use `Union` where nested dicts are valid, or restructure to use Pydantic models for stats dicts.

**`src/f1d/shared/panel_ols.py` Has Type Errors in PanelOLS Integration:**
- Problem: Pyright reports errors on `condition_number` attribute access on `PanelEffectsResults`, parameter name mismatches in callable type assignments, and `None`-callable errors. 7 type errors across lines 348–530.
- Files: `src/f1d/shared/panel_ols.py`
- Impact: Possible `AttributeError` at runtime if `condition_number` is accessed on result objects that do not carry it. Function type mismatch suggests a callable is reassigned incorrectly.
- Fix approach: Add `hasattr` guard before `condition_number` access; standardize callable parameter names between inner function definitions and their declared types.

**`src/f1d/shared/data_loading.py` Passes Bare Strings to `how=` and `validate=` Parameters:**
- Problem: Pyright reports that `str` is not assignable to `MergeHow` (a Literal union) and `ValidationOptions` at lines 126–136.
- Files: `src/f1d/shared/data_loading.py`
- Impact: No runtime impact (pandas accepts string `how=` arguments), but mypy strict mode reports errors, masking real type errors in the same file.
- Fix approach: Cast to `Literal["left"]` etc., or use `typing.cast()` at call sites.

**`src/f1d/shared/chunked_reader.py` Has Possibly-Unbound Variable:**
- Problem: `row_group_size` is used at lines 91–92 but is only set inside a conditional block; Pyright flags it as "possibly unbound."
- Files: `src/f1d/shared/chunked_reader.py`
- Impact: `UnboundLocalError` at runtime if the conditional block is not entered.
- Fix approach: Initialize `row_group_size = None` before the conditional block and guard the usage.

---

*Concerns audit: 2026-02-20*
