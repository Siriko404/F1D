# PAPER ARTIFACTS AUDIT REPORT: H8 Political Risk and CEO Speech Vagueness

**Suite ID:** H8
**Audit Date:** 2026-03-01
**Auditor:** Claude Code (AI Coding Assistant)
**Audit Protocol:** Paper_Ready_artifacts.txt

---

## 1) Executive Summary

**Is suite H8 paper-submission ready?** **NO** — Two MAJOR issues require correction before submission.

| Verdict | Status | Notes |
|---------|--------|-------|
| **Presence verdict** | **Partial** | Core outputs present; missing run_manifest, attrition table |
| **Quality verdict** | **Partial** | Numbers correct but LaTeX table unusable; documentation errors |
| **Top BLOCKERS** | 0 | No blockers — results are trustworthy |
| **Top MAJOR issues** | 3 | (1) LaTeX displays 0.0000; (2) Provenance wrong on winsorization; (3) Missing manifests |

### Top 3 Issues Requiring Action:
1. **MAJOR:** LaTeX table displays PRiskFY and interact coefficients as "0.0000" due to `.4f` formatting — coefficients are O(1e-6)
2. **MAJOR:** Provenance H8.md Section G claims "pooled" winsorization but code uses per-year winsorization
3. **MAJOR:** Missing reproducibility artifacts: no run_manifest.json, no attrition table

### Positive Findings:
- Results are **scientifically trustworthy** — cross-artifact consistency verified
- Null finding (β₃ not significant) is valid and correctly interpreted
- Panel construction verified: zero row-delta, unique keys, correct lead construction
- Cross-run reproducibility confirmed (identical results to 10+ decimal places)

---

## 2) Suite & Run Identification

| Field | Value | Evidence Command |
|-------|-------|------------------|
| **Suite ID** | H8 | `docs/provenance/H8.md` |
| **Stage 3 Builder** | `src/f1d/variables/build_h8_political_risk_panel.py` | File exists (313 lines) |
| **Stage 4 Runner** | `src/f1d/econometric/run_h8_political_risk.py` | File exists (565 lines) |
| **Stage 3 Run ID** | `2026-02-28_152717` | `ls outputs/variables/h8_political_risk/` |
| **Stage 4 Run ID** | `2026-02-28_152914` | `ls outputs/econometric/h8_political_risk/` |
| **Stage 3 Panel Path** | `outputs/variables/h8_political_risk/2026-02-28_152717/h8_political_risk_panel.parquet` | 2.4 MB |
| **Stage 4 Output Path** | `outputs/econometric/h8_political_risk/2026-02-28_152914/` | 7 files |
| **Git Commit (HEAD)** | `c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50` | `git rev-parse HEAD` |
| **Git Commit (from run)** | NOT CAPTURED | No run_manifest.json exists |

**Stage 3 → Stage 4 Linkage Verification:**
```python
from f1d.shared.path_utils import get_latest_output_dir
panel_dir = get_latest_output_dir('outputs/variables/h8_political_risk', required_file='h8_political_risk_panel.parquet')
# Returns: outputs\variables\h8_political_risk\2026-02-28_152717
# Stage 4 (2026-02-28_152914) uses this panel via get_latest_output_dir()
```
**Status:** PASS — Stage 4 correctly references Stage 3 panel via timestamp ordering.

---

## 3) Estimator Family Detection

| Field | Value | Evidence |
|-------|-------|----------|
| **Model Family** | Panel OLS with Fixed Effects | `linearmodels.panel.PanelOLS` |
| **Estimator** | `PanelOLS.from_formula()` with `EntityEffects + TimeEffects` | `run_h8_political_risk.py:239-242` |
| **Variance Estimator** | Firm-clustered SEs (`cov_type="clustered", cluster_entity=True`) | `run_h8_political_risk.py:260` |
| **Within-transformation** | Yes — entity and time effects absorbed | `drop_absorbed=True` |
| **Software** | Python `linearmodels`, `pandas` | `requirements.txt` |

**Model-Specific Requirements (Panel FE):**
- Within-R²: Required ✓ (present in diagnostics and LaTeX)
- FE indicators: Required ✓ ("Firm FE" and "Year FE" rows in table)
- Cluster summary (# firms): Required ✓ (in diagnostics)
- N entities + N time periods: Required ✓ (in raw output)

---

## 4) Artifact Requirements & Quality Matrix

### Layer A — Required for All Suites

| Artifact | Required? | Found Path | Presence | Quality | Tests Run | Notes |
|----------|-----------|------------|----------|---------|-----------|-------|
| **A1: Provenance Doc** | Yes | `docs/provenance/H8.md` | ✅ Present | ⚠️ PARTIAL | 27 claims verified | 396 lines; winsorization error (Finding #2) |
| **A1: Variable Dictionary** | Yes | `H8.md Section F` | ✅ Present | ✅ PASS | Formula/source verified | 12 variables documented |
| **A1: Variable Lineage JSON** | Yes | — | ❌ Missing | N/A | — | Not generated |
| **A1: Sample Attrition Table** | Yes | — | ❌ Missing | N/A | — | No tex/pdf attrition table |
| **A2: run_manifest.json** | Yes | — | ❌ Missing | N/A | — | No manifest generated |
| **A2: Environment Lock** | Yes | `requirements.txt` | ⚠️ Partial | ⚠️ PARTIAL | — | Pinned versions exist |
| **A2: Stage 3 Log** | Yes | `report_step3_h8.md` | ✅ Present | ✅ PASS | Row count verified | Minimal but present |
| **A2: Stage 4 Log** | Yes | Console output only | ⚠️ Partial | ⚠️ PARTIAL | — | No saved log file |
| **A3: Summary Stats CSV** | Yes | `summary_stats.csv` | ✅ Present | ✅ PASS | Cross-checked vs panel | 8 vars |
| **A3: Summary Stats TeX** | Yes | `summary_stats.tex` | ⚠️ PARTIAL | ⚠️ PARTIAL | — | Wrong note ("call level") |
| **A3: Baseline Results TeX** | Yes | `h8_political_risk_table.tex` | ✅ Present | ⚠️ PARTIAL | Coeffs display as 0.0000 | Finding #1 |
| **A3: Baseline Results CSV** | Yes | `model_diagnostics.csv` | ✅ Present | ✅ PASS | 2 rows, all fields valid | Complete |
| **A3: Raw Regression Output** | Yes | `regression_primary.txt` | ✅ Present | ✅ PASS | PanelOLS summary | Complete |

### Layer B — Model-Family Required (Panel FE)

| Artifact | Required? | Found Path | Presence | Quality | Notes |
|----------|-----------|------------|----------|---------|-------|
| **Within-R²** | Yes | `model_diagnostics.csv` | ✅ Present | ✅ PASS | 0.0249 (Primary), 0.0212 (Main) |
| **FE Indicators** | Yes | `h8_political_risk_table.tex` | ✅ Present | ✅ PASS | "Firm FE" and "Year FE" rows |
| **N Firms (Clusters)** | Yes | `model_diagnostics.csv` | ✅ Present | ✅ PASS | Column `n_firms`: 1,665 / 1,331 |
| **SE Type Documentation** | Yes | Not in table | ⚠️ Partial | ⚠️ PARTIAL | Missing from LaTeX notes |

### Layer C — Figures (Paper-Ready)

| Artifact | Required? | Found Path | Presence | Quality | Notes |
|----------|-----------|------------|----------|---------|-------|
| **Coefficient Forest Plot** | Recommended | — | ❌ Missing | N/A | No forest plot generated |
| **Distribution Plots** | Optional | — | ❌ Missing | N/A | Not generated |

---

## 5) Notes-as-Claims Register

### 5.1) LaTeX Table Claims (`h8_political_risk_table.tex`)

| # | Claim | Location | Verification | Status |
|---|-------|----------|--------------|--------|
| 1 | "Firm and year fixed effects are included" | Table rows 18-19 | Code: `EntityEffects + TimeEffects` | **PASS** |
| 2 | "Controls include Size, Lev, ROA, TobinsQ" | Table row 17 | Code: `run_h8_political_risk.py:87` | **PASS** |
| 3 | "N obs for Primary = 15,721" | Table row 21 | CSV: `n_obs = 15721` | **PASS** |
| 4 | "N obs for Main = 12,627" | Table row 21 | CSV: `n_obs = 12627` | **PASS** |
| 5 | "Within-R² for Primary = 0.0249" | Table row 22 | CSV: `within_r2 = 0.024889...` | **PASS** |
| 6 | "Style Frozen β = -0.0077**" | Table row 12 | CSV: `beta2 = -0.00773..., p = 0.0498` | **PASS** |
| 7 | "PRiskFY β = -0.0000" | Table row 10 | CSV: `beta1 = -8.06e-06` | **FAIL** — Formatting hides value |
| 8 | "Interact β = 0.0000" | Table row 14 | CSV: `beta3 = 1.71e-06` | **FAIL** — Formatting hides value |

### 5.2) Provenance Document Claims (`H8.md`)

| # | Claim | Location | Verification | Status |
|---|-------|----------|--------------|--------|
| 9 | "Panel has 29,343 firm-years" | H8.md:286 | Ad-hoc: `len(panel) = 29343` | **PASS** |
| 10 | "AbsAbInv_lead valid: 25,759 (87.8%)" | H8.md:291 | Ad-hoc: `25759 / 29343 = 87.8%` | **PASS** |
| 11 | "PRiskFY valid: 27,501 (93.7%)" | H8.md:292 | Ad-hoc: `27501 / 29343 = 93.7%` | **PASS** |
| 12 | "style_frozen valid: 18,439 (62.8%)" | H8.md:293 | Ad-hoc: `18439 / 29343 = 62.8%` | **PASS** |
| 13 | "interact valid: 17,930 (61.1%)" | H8.md:294 | Ad-hoc: `17930 / 29343 = 61.1%` | **PASS** |
| 14 | "PRiskFY: mean=119.8, SD=143.6" | H8.md:297 | Ad-hoc: `mean=119.8488, SD=143.6371` | **PASS** |
| 15 | "style_frozen: mean≈0, SD≈1" | H8.md:298 | Ad-hoc: `mean=-0.1023, SD=1.0063` | **PASS** |
| 16 | "beta3 = 1.71e-06, p = 0.776" | H8.md:267 | CSV: `1.7135e-06, p = 0.7760` | **PASS** |
| 17 | "Within-R² = 0.0249" | H8.md:271 | CSV: `0.024889...` | **PASS** |
| 18 | "Winsorization: Lev, ROA, TobinsQ at 1/99% pooled" | H8.md:227 | Code: `_winsorize_by_year()` = **per-year** | **FAIL** — See Finding #2 |
| 19 | "Regression N = 15,721, firms = 1,665" | H8.md:269-270 | CSV: `n_obs=15721, n_firms=1665` | **PASS** |
| 20 | "Zero row-delta on all merges" | H8.md:182 | Code: raises ValueError on delta | **PASS** |

### 5.3) README Claims (Lines 504-525)

| # | Claim | Location | Actual Value | Status |
|---|-------|----------|--------------|--------|
| 21 | "Stage 3: 29,343 firm-years" | README:516 | 29,343 | **PASS** |
| 22 | "Valid AbsAbInv_lead: 25,759" | README:516 | 25,759 | **PASS** |
| 23 | "PRiskFY matched: 27,501" | README:516 | 27,501 | **PASS** |
| 24 | "StyleFrozen: 18,439 valid (62.8%)" | README:517 | 18,439 (62.8%) | **PASS** |
| 25 | "N Obs = 15,721" | README:521 | 15,721 | **PASS** |
| 26 | "N Firms = 1,665" | README:521 | 1,665 | **PASS** |
| 27 | "Within-R² = 0.025" | README:521 | 0.024889... | **PASS** |
| 28 | "β₃ = 0.0000, p = 0.776" | README:521 | 1.71e-06, p = 0.776 | **PASS** (value correct, display rounded) |
| 29 | "H8 NOT SUPPORTED" | README:523 | β₃ p = 0.776 | **PASS** — Correct conclusion |

---

## 6) Findings (Grouped by Severity)

### Finding #1 — MAJOR: LaTeX Table Displays Key Coefficients as "0.0000"

**Severity:** MAJOR (publication readability)

**Symptom:** The LaTeX table (`h8_political_risk_table.tex`) displays PRiskFY coefficient as `-0.0000`, interact coefficient as `0.0000`, and their SEs as `(0.0000)`. All are O(1e-6) values formatted with `.4f`. The table is technically correct but uninformative — a reader cannot distinguish the coefficients from zero.

**Evidence:**
```latex
% h8_political_risk_table.tex lines 10-15:
Political Risk & -0.0000 & -0.0000 \\
 & (0.0000) & (0.0000) \\
...
PRisk $\times$ Style Frozen & 0.0000 & 0.0000 \\
 & (0.0000) & (0.0000) \\
```

**Actual values:**
- PRiskFY β = -8.057e-06, SE = 6.456e-06
- Interact β = 1.713e-06, SE = 6.021e-06

**Why it matters:** A reader/reviewer looking at the table sees identical "0.0000" for coefficients and SEs, providing no information about magnitudes or relative precision. This is a presentation failure for a thesis/paper table.

**How to verify:**
```bash
cat outputs/econometric/h8_political_risk/2026-02-28_152914/h8_political_risk_table.tex
```

**Fix:** Modify `_save_latex_table()` in `run_h8_political_risk.py` to use scientific notation or scale PRiskFY:
```python
# Option A: Scientific notation for small coefficients
def fmt_coef(val, pval):
    if pd.isna(val):
        return ""
    stars = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.10 else ""
    if abs(val) < 0.0001:
        return f"{val:.2e}{stars}"
    return f"{val:.4f}{stars}"

# Option B: Scale PRiskFY by 100 before regression
# Then report "per 100-unit increase in PRisk"
```

**Rerun impact:** Stage 4 rerun required to regenerate LaTeX table.

---

### Finding #2 — MAJOR: Provenance Claims "Pooled" Winsorization; Code Uses Per-Year

**Severity:** MAJOR (documentation error)

**Symptom:** Provenance H8.md Section G states:
> "Lev, ROA, TobinsQ, CashFlow, etc. | 1%/99% | Pooled (all years) | `_compustat_engine.py:1050-1057`"

The actual code at `_compustat_engine.py:1036-1058` uses `_winsorize_by_year()` which applies 1/99% within each `fyearq` group, not pooled across all years.

**Evidence:**
```bash
# From _compustat_engine.py:1036-1038:
# B3 fix: Apply per-year winsorization (1%/99% within each fyearq)

# From _compustat_engine.py:429-453:
def _winsorize_by_year(series, year_col, lower=0.01, upper=0.99):
    """Winsorize within each year group."""
```

**Why it matters:** Per-year winsorization is the correct approach for panel data (as the README correctly explains). The provenance document's claim of "pooled" winsorization is factually wrong and could mislead a reviewer checking the pipeline.

**How to verify:**
```bash
grep -A3 "winsoriz" src/f1d/shared/variables/_compustat_engine.py | head -20
grep "pooled" docs/provenance/H8.md
```

**Fix:** Update H8.md Section G to replace "Pooled (all years)" with "Per-year (within each fyearq)" for Lev, ROA, TobinsQ. Update line reference from `1050-1057` to `1036-1058`.

**Rerun impact:** Documentation-only fix. No rerun needed.

---

### Finding #3 — MAJOR: Missing Reproducibility Artifacts

**Severity:** MAJOR

**Symptom:** The following reproducibility artifacts are missing:
1. No `run_manifest.json` with git commit, timestamp, config snapshot
2. No sample attrition table (tex/pdf)
3. No machine-readable variable lineage (JSON)

**Evidence:**
```bash
ls outputs/**/run_manifest*.json  # No files found
ls outputs/**/*attrition*         # No files found
ls **/*lineage*.json              # No files found
```

**Why it matters:** Without a run manifest, the link between outputs and code version is not captured. Sample flow from 112,968 calls → 29,343 firm-years → 15,721 regression obs is not documented in paper-ready form.

**How to verify:**
```bash
find outputs -name "*manifest*" -o -name "*attrition*"
```

**Fix:**
1. Generate `run_manifest.json` at Stage 4 completion with: git_commit, timestamp, panel_path, config snapshot
2. Create attrition table showing: Total calls → Firm-years → After controls dropna → Final regression N
3. Optional: Generate variable lineage JSON from `H8.md` Section F

**Rerun impact:** Code enhancement for future runs; manual generation possible for current run.

---

### Finding #4 — MINOR: LaTeX Summary Stats Claims "Call Level"

**Severity:** MINOR

**Symptom:** `summary_stats.tex` table note says "All variables are measured at the call level" but H8 is a firm-year level panel.

**Evidence:**
```latex
% summary_stats.tex lines 19-23:
\begin{tablenotes}
\small
\item This table reports summary statistics for variables used in the regression.
All variables are measured at the call level.
\end{tablenotes}
```

**Why it matters:** The note is incorrect. H8 uses firm-year level observations. A reviewer would notice the discrepancy between N=29,343 (firm-years) and the note claiming call-level.

**Fix:** Change "call level" to "firm-year level" in `summary_stats.tex` generation.

**Rerun impact:** Stage 4 rerun required.

---

### Finding #5 — MINOR: Panel Includes Fiscal Years Outside Config Range

**Severity:** MINOR

**Symptom:** Panel contains fyearq=2000 (1 row) and fyearq=2019 (78 rows), outside the configured `year_start=2002, year_end=2018`.

**Evidence:**
```
fyearq < 2002: 141 rows
fyearq > 2018: 78 rows
AbsAbInv_lead valid with fyearq < 2002: 125 (used as RHS for 2002 DVs)
AbsAbInv_lead valid with fyearq > 2018: 0
```

**Why it matters:** These edge rows arise because `attach_fyearq()` uses backward `merge_asof` on `start_date → datadate`, which can match calls near fiscal year boundaries to adjacent fiscal years. All 78 rows with fyearq > 2018 have `AbsAbInv_lead=NaN` and cannot enter regressions. The 141 rows with fyearq < 2002 contribute as RHS observations (with valid leads for fyearq=2002). Benign but undocumented.

**Fix:** Document in provenance that the panel includes edge years from merge_asof. Optionally filter to `fyearq.between(2002, 2018)` after aggregation.

**Rerun impact:** None if documented. Stage 3 rerun if filtering added.

---

### Finding #6 — MINOR: style_frozen Absorbed by Firm FE for 84.5% of Firms

**Severity:** MINOR (identification concern, not bug)

**Symptom:** Only 258 of 1,665 firms in the regression sample have any within-firm variation in `style_frozen`. For 1,337 firms (80.3%), `style_frozen` has zero variance within the firm; for 70 firms, there is only one observation (variance undefined). Only firms with CEO turnover during the sample period contribute to identifying β₂ and β₃.

**Evidence:**
```python
df_reg = df.dropna(subset=required)
within_var = df_reg.groupby('gvkey')['style_frozen'].var()
# Zero variance: 1,337 firms
# Positive variance: 258 firms
# Single obs (NaN var): 70 firms
```

**Why it matters:** With Firm FE, the coefficient on style_frozen is identified only from within-firm variation (CEO turnover). 84.5% of firms contribute zero identifying variation. The interaction term (PRiskFY × style_frozen) inherits this weakness. This doesn't invalidate the test, but it means:
1. The effective sample for identification is ~258 firms, not 1,665
2. Statistical power is very low for detecting the interaction
3. The null result may reflect low power rather than a true null

**Fix:** Add a paragraph to the provenance and thesis discussing the identification limitation. Consider supplementary analysis:
- Report the effective number of identifying firms (258)
- Run a between-effects model or pooled OLS as robustness

**Rerun impact:** Documentation-only. No rerun needed.

---

### Finding #7 — NOTE: LaTeX Table Missing SE Cluster Documentation

**Severity:** NOTE

**Symptom:** The LaTeX table does not include a note documenting that standard errors are clustered at the firm level.

**Evidence:**
```latex
% h8_political_risk_table.tex has no notes section
```

**Why it matters:** Per econometric conventions, the clustering method should be documented in the table notes.

**Fix:** Add table note: "Standard errors clustered at the firm level. **p<0.05, *p<0.10"

**Rerun impact:** Stage 4 rerun required.

---

## 7) Cross-Artifact Consistency Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| **C1: N consistency** | diag N == raw output N | 15,721 == 15,721 | **PASS** |
| **C2: Coef consistency** | CSV == raw (within rounding) | -8.057e-06 == -8.057e-06 | **PASS** |
| **C3: SE consistency** | CSV == raw | 6.456e-06 == 6.456e-06 | **PASS** |
| **C4: Run linkage** | Stage 4 uses correct Stage 3 panel | `get_latest_output_dir()` → 2026-02-28_152717 | **PASS** |
| **C5: Lead construction** | AbsAbInv_lead[t] = AbsAbInv[t+1] | Max diff = 0.0 | **PASS** |
| **C6: Interaction construction** | interact = PRiskFY × style_frozen | Max diff = 0.0 | **PASS** |
| **C7: Cross-run reproducibility** | Prior run == Latest run | Identical to 10+ dp | **PASS** |

**High-Risk Silent-Failure Checks Performed:**
1. **Lead variable look-ahead bias:** Manually reconstructed `AbsAbInv_lead` from `AbsAbInv` with gap-year nulling. Max absolute difference = 0.0 across all 25,759 valid observations. No look-ahead detected.

2. **Interaction term algebraic correctness:** Verified `interact == PRiskFY * style_frozen` exactly (max diff = 0.0). Verified NaN propagation: interact is NaN whenever either PRiskFY or style_frozen is NaN.

3. **Cross-run determinism:** Compared 2026-02-27 and 2026-02-28 panel builds (identical row counts, means, N for all key variables) and econometric runs (identical N, R-squared, β₃, p₃ to 10+ decimal places).

---

## 8) Rerun / Regeneration Plan (Minimal)

### Stage 4 Only (for LaTeX fix):

```bash
# After fixing fmt_coef() to use scientific notation
python -m f1d.econometric.run_h8_political_risk
```

**Acceptance tests:**
- [ ] LaTeX table shows PRiskFY coefficient in scientific notation (e.g., "-8.06e-06")
- [ ] LaTeX table shows interact coefficient in scientific notation (e.g., "1.71e-06")
- [ ] Model diagnostics N = 15,721 (Primary), 12,627 (Main)
- [ ] β₃ ≈ 1.71e-06, p₃ ≈ 0.776

### Full Rerun (if panel filtering applied):

```bash
# Stage 3
python -m f1d.variables.build_h8_political_risk_panel

# Stage 4
python -m f1d.econometric.run_h8_political_risk
```

---

## 9) Hardening Recommendations

### 9.1 Code Changes

1. **LaTeX scientific notation** — Auto-detect small coefficients:
```python
def fmt_coef(val, pval):
    if pd.isna(val):
        return ""
    stars = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.10 else ""
    if abs(val) < 0.0001:
        return f"{val:.2e}{stars}"
    return f"{val:.4f}{stars}"
```

2. **run_manifest.json generation** — Add at end of Stage 4:
```python
manifest = {
    "git_commit": subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
    "timestamp": timestamp,
    "panel_path": str(panel_file),
    "config": var_config,
}
with open(out_dir / "run_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
```

3. **Add SE cluster note to LaTeX** — Include in table:
```latex
\begin{tablenotes}
\item Standard errors clustered at the firm level.
\end{tablenotes}
```

### 9.2 Documentation Updates

4. **Fix H8.md Section G** — Change "Pooled" to "Per-year" for winsorization
5. **Fix summary_stats.tex note** — Change "call level" to "firm-year level"
6. **Add identification discussion** — Document that 84.5% of firms have zero within-firm style_frozen variance

### 9.3 Tests to Add

7. **Unit test: LaTeX coefficient readability** — Verify no non-zero coefficient displays as "0.0000"
8. **Unit test: summary_stats level** — Verify note matches panel level
9. **Integration test: cross-artifact consistency** — Compare CSV vs raw output for all specs

---

## 10) Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | `read README.md` | Extract pipeline contract | 932 lines; 4-stage architecture |
| 2 | `read docs/Prompts/Paper_Ready_artifacts.txt` | Load audit protocol | 320 lines; 7-phase audit |
| 3 | `glob **/*h8*` | Locate H8 files | Found 18 H8-related files |
| 4 | `read docs/provenance/H8.md` | Extract provenance claims | 396 lines |
| 5 | `read docs/provenance/AUDIT_H8.md` | Review prior audit | 428 lines |
| 6 | `read src/f1d/variables/build_h8_political_risk_panel.py` | Audit Stage 3 | 313 lines |
| 7 | `read src/f1d/econometric/run_h8_political_risk.py` | Audit Stage 4 | 565 lines |
| 8 | `ls outputs/variables/h8_political_risk/` | List Stage 3 runs | 3 directories |
| 9 | `ls outputs/econometric/h8_political_risk/` | List Stage 4 runs | 4 directories |
| 10 | `read model_diagnostics.csv` | Cross-check diagnostics | 2 specs |
| 11 | `read regression_primary.txt` | Cross-check raw output | PanelOLS summary |
| 12 | `read sanity_checks.txt` | Verify sanity checks | 27 lines |
| 13 | `read h8_political_risk_table.tex` | Audit LaTeX table | 25 lines; 0.0000 issue |
| 14 | `read summary_stats.csv` | Cross-check summary | 8 vars |
| 15 | `read summary_stats.tex` | Check summary LaTeX | Wrong "call level" note |
| 16 | `python -c "panel basic stats"` | Verify panel | 29,343 rows, 0 duplicates |
| 17 | `python -c "interaction verification"` | Verify interact term | Max diff = 0.0 |
| 18 | `python -c "lead verification"` | Verify lead construction | Max diff = 0.0 |
| 19 | `python -c "within-firm variation"` | Check FE absorption | 1,337/1,665 zero variance |
| 20 | `python -c "CEO clarity scores"` | Verify input | 2,486 CEOs, mean=0, SD=1 |
| 21 | `git rev-parse HEAD` | Get commit hash | c9b00bef... |
| 22 | `grep README H8` | Check README claims | Lines 504-525 verified |
| 23 | `read _hassan_engine.py` | Audit PRiskFY source | 216 lines |
| 24 | `read prisk_fy.py` | Audit PRiskFY builder | 110 lines |
| 25 | `read ceo_clarity_style.py` | Audit style_frozen | 241 lines |
| 26 | `glob outputs/**/run_manifest*.json` | Find manifests | None found |

---

## Summary

**H8 Political Risk suite is mechanically sound:**
- Panel construction: zero row-delta, unique keys, correct lead construction
- Output generation: 2 regression specs, complete diagnostics
- Cross-artifact consistency: All checks PASS

**Two issues require correction before paper submission:**

1. **MAJOR: LaTeX table displays coefficients as 0.0000** — Must use scientific notation
2. **MAJOR: Provenance claims wrong winsorization method** — Documentation error

**Scientific interpretation:**
- The null finding (β₃ not significant) is **valid**
- However, low identification power (only 258 firms with CEO turnover) means the test has low power
- The result should be interpreted as "insufficient evidence" rather than "evidence of no effect"

**Recommended actions before submission:**
1. Fix LaTeX coefficient formatting (Finding #1)
2. Fix provenance winsorization claim (Finding #2)
3. Fix summary_stats.tex note (Finding #4)
4. Add SE cluster documentation to LaTeX (Finding #7)
5. Generate run_manifest.json (Finding #3)
6. Add identification limitation discussion (Finding #6)
