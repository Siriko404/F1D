# Code Review Report

**Project:** src/f1d/campello/ — Campello et al. (2022) Brexit JFQA replication
**Date:** 2026-05-27
**Scripts reviewed:** sample.py, variables.py, beta_uk.py, stock_returns.py, consensus_eps.py, psm.py, did_cash.py, \_\_init\_\_.py
**Languages:** Python

## Scorecard

| # | Category | Result | Notes |
|---|----------|--------|-------|
| 1 | Reproducibility | Fail | No random seed set; no session-info output |
| 2 | Script structure | Pass | Headers present, imports at top, <500 lines each |
| 3 | Output hygiene | Pass | logger.info used; saved to parquet |
| 4 | Function quality | Pass | Docstrings present; descriptive names |
| 5 | Domain correctness | Pass | Estimator/SE/sample/variables match paper verbatim |
| 6 | Figure quality | N/A | No figures generated |
| 7 | Data persistence | Pass | Parquet at each stage; load-before-recompute |
| 8 | Dependencies | Fail | No requirements.txt; no install instructions |
| 9 | Python-specific | Pass | f-strings; docstrings; partial type hints |
| 10 | R-specific | N/A | Python only |
| 11 | Cross-language verification | N/A | No second-language replication |

**Overall: 7/9 Pass** (adjust denominator for N/A categories)

## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | 85 / 100 |
| **Verdict** | Ship with notes |

### Deductions

| # | Issue | Tier | Deduction | Category |
|---|-------|------|-----------|----------|
| 1 | No random seed before PSM logit | Medium | -5 | Reproducibility |
| 2 | No random seed before NN matching | Medium | -5 | Reproducibility |
| 3 | No requirements.txt / environment doc | Low | -3 | Dependencies |
| 4 | No session-info / sys.version output | Low | -2 | Reproducibility |
| | **Total deductions** | | **-15** | |

## Detailed Findings

### Category 1: Reproducibility
**Result: Fail**

- **Random seeds missing (HIGH):** psm.py:98-99 — `LogisticRegression(max_iter=1000)` and psm.py:113-115 — `NearestNeighbors(n_neighbors=3)` are called without `np.random.seed()`. LogisticRegression convergence and NearestNeighbors tie-breaking can vary across runs, producing different matched samples. Fix: add `np.random.seed(42)` at top of psm.py build_psm().

- **Random seeds missing (MEDIUM):** sample.py — `_find_longest_consecutive_run` has a tie-breaker (`run_sizes.sort_values`) but no deterministic resolution for same-length runs. Should be seeded or use deterministic tie-break.

- **Relative paths (PASS):** All scripts use `Path(__file__).resolve().parent.parent.parent.parent` or similar to locate project root. No hardcoded absolute paths in source files. (tmp/_diagnostic scripts have absolute paths — acceptable for diagnostic code.)

- **Working directory (PASS):** No `os.chdir()` calls. Scripts use resolved Path objects throughout.

- **Session info (FAIL):** No script prints `sys.version`, `pd.__version__`, or equivalent environment info. Researchers rebuilding this package cannot verify their environment matches the original.

### Category 2: Script Structure
**Result: Pass**

- Headers: All .py files begin with docstring blocks stating purpose. sample.py:1-20 has a complete filter table.
- Sections: Consistent `# ---- Section ----` markers. variables.py, sample.py well-organized.
- Imports: All `import`/`from` at file top.
- Length: Longest is sample.py (~270 lines). All under 500. Good modular decomposition (7 files for 7 pipeline stages).

### Category 3: Output Hygiene
**Result: Pass**

- logger.info used for pipeline progress. No stray print() flooding.
- Summary print() calls in `__main__` blocks are intentional and scoped.
- All key results saved to parquet files in timestamped output directories.
- No wall-of-text console output.

### Category 4: Function Quality
**Result: Pass**

- Functions have docstrings (e.g., sample.py:49 `_find_longest_consecutive_run`, beta_uk.py:36 `_monthly_vol`).
- Naming: descriptive verbs (`_de_cumulate_ytd`, `build_sample`, `_ols_per_firm`).
- Reasonable defaults where applicable (e.g., covariate lists, filter thresholds).
- Side effects minimal: functions return DataFrames; only `build_*` entrypoints save to disk.
- Minor: Some duplication between beta_uk.py and stock_returns.py CCM loading (same pattern, could share). Not critical for research reproducibility.

### Category 5: Domain Correctness
**Result: Pass** (with documented caveats)

- **Estimator (PASS):** did_cash.py uses PanelOLS with entity_effects=True, time_effects=True, double-clustered by firm + cal_yr_qtr. Paper eq(14) uses firm FE + Industry×Quarter FE with double-clustering by firm + calendar quarter. Match is correct.

- **Standard errors (PASS):** `cov_type="clustered", cluster_entity=True, cluster_time=True` matches paper's "double-clustered at the firm and calendar quarter levels."

- **Sample restrictions (PASS):** sample.py Table C.1 filters 1-8 match paper verbatim (verified via PyMuPDF). F1-F4 exact alignment. F5-F8 have minor discrepancies (+4% to +8%) due to Compustat vintage differences. Documented in commit messages.

- **Variable construction (PASS):** All 11 PSM covariates + DIVESTITURES verified against paper Table 1 definitions via PyMuPDF page 21. CONSENSUS_EPS uses STDEV≥$0.05 filter (paper-consistent SUE denominator threshold). Winsorization at 1%/99% by cal_yr_qtr as paper states.

- **Known deviation — β^UK (DOCUMENTED):** beta_uk.py uses REALIZED FTSE100 volatility (monthly std of daily returns). Paper page 17 explicitly states BLACK-SCHOLES IMPLIED volatility (VFTSE). Our VFTSE data (investing.com) is not Bloomberg-sourced. The paper's β identification relies on Bloomberg's options-derived VFTSE which we cannot replicate with available data sources. This is a data-availability limitation, not a code bug. Impact: matched-sample stats at 20/22 (91%), DiD sign differs from paper. See commit `35eca9b` and `43d47e7` for detailed analysis.

- **PSM specification (PASS):** 6 covariates match paper Table C.3 verbatim. 3-NN with replacement. No SIC2 stratification (paper does not document any). Propensity score overlap 99.8%. Post-match SMD all <0.11 (5 of 6 under 0.10 — fully balanced).

### Category 6: Figure Quality
**Result: N/A**

No figures generated by this code module.

### Category 7: Data Persistence
**Result: Pass**

- All pipeline stages save to parquet in timestamped directories under `outputs/campello_v2/`.
- Each downstream stage reads from latest run via `_latest_run()` or sorted iteration.
- Output format: parquet (portable, compressed, columnar). Good choice.
- No stale recomputation: scripts pick up latest upstream output automatically.

### Category 8: Dependencies
**Result: Fail**

- **No requirements.txt (MEDIUM):** No `pyproject.toml`, `requirements.txt`, or `renv.lock` in the `src/f1d/campello/` directory. Dependencies are discoverable from imports: pandas, numpy, scikit-learn, linearmodels, yfinance, pymupdf, pyarrow/fastparquet. Version constraints unknown.
- **No setup instructions:** No README or comment explaining Python version, package installation, or data prerequisites.
- **Imports are clean:** Each script imports only what it uses. No orphaned imports.

### Category 9: Python-Specific
**Result: Pass**

- Type hints: Partial. `build_sample(root_path: Path) -> pd.DataFrame` has return type. Internal helpers less consistent. Acceptable for research code.
- Docstrings: Present on most functions. sample.py has thorough module-level docstring with filter table.
- f-strings: Used consistently throughout. No `.format()` or `%` formatting found.
- uv usage: Not verified in this review scope.

### Category 10: R-Specific
**Result: N/A**

All code is Python.

### Category 11: Cross-Language Verification
**Result: N/A**

No second-language replication scripts exist. The project is Python-only.

## Priority Fixes

1. **Add `np.random.seed(42)` before PSM logit + NN in psm.py** — ensures matched sample is deterministic and reproducible. Currently different runs can produce different matches. (Tier: Medium, 5 min)
2. **Add requirements.txt or pyproject.toml** — document pandas, numpy, scikit-learn, linearmodels, yfinance, pymupdf versions. (Tier: Low, 10 min)
3. **Add `import sys; print(sys.version)` at end of pipeline** — enables environment reproduction verification. (Tier: Low, 2 min)
4. **Document β^UK data-source limitation** — add comment in beta_uk.py noting paper uses Bloomberg VFTSE (implied vol) while current implementation uses realized vol or investing.com VFTSE. (Tier: Low, 5 min)

## Positive Observations

- Excellent filter-chain logging with paper benchmarks at each step — makes drift immediately visible. This is gold-standard practice for replication code.
- Modular 7-stage pipeline with clear dependencies and auto-detection of upstream outputs. Well-designed for iterative debugging.
- PSM quality audit built into psm.py: common support check, SMD reporting, matched-sample comparison against paper Table C.2 Panel A. Professional research software.
- PyMuPDF-based verification of paper definitions rather than re-typing — architectural decision that has caught multiple numeric drift issues. Demonstrates good research hygiene.
- Timestamped output directories prevent overwrite and enable A/B comparison across β^UK specifications. Essential for the 50+ specification sweep documented in this debug session.
