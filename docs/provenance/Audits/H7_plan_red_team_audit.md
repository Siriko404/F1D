# H7 Implementation Plan — Red Team Audit
**Auditor:** Adversarial code reviewer
**Date:** 2026-03-12
**Scope:** Full line-by-line verification of every claim in the H7 fix plan against actual source code

---

## File Location Correction (Pre-Audit)

The plan states engine files are under `src/f1d/variables/engines/`. That directory **does not exist**.

Actual locations:
- `_crsp_engine.py` → `src/f1d/shared/variables/_crsp_engine.py`
- `_linguistic_engine.py` → `src/f1d/shared/variables/_linguistic_engine.py`
- `_clarity_residual_engine.py` → `src/f1d/shared/variables/_clarity_residual_engine.py`
- `ceo_clarity_residual.py` → `src/f1d/shared/variables/ceo_clarity_residual.py`
- `panel_utils.py` → `src/f1d/shared/variables/panel_utils.py`

This is cosmetic for the plan steps but means any instructions to "edit `variables/engines/_crsp_engine.py`" will find the wrong path.

---

## L1/L3 — DV Timing Fix

### Plan Claim
`_crsp_engine.py:357–363` computes `amihud_illiq` over window `[prev_call+5d, current_call−5d]`. Proposed fix: change to post-call window `[call+1d, next_call−5d]`.

### Verdict: WRONG LINE NUMBER + INCOMPLETE FIX

**Line numbers are partially wrong.** The window is set at lines 358–363:

```python
# Lines 358-363 of src/f1d/shared/variables/_crsp_engine.py
year_manifest["window_start"] = year_manifest[
    "prev_call_date"
] + pd.Timedelta(days=DAYS_AFTER_PREV_CALL)
year_manifest["window_end"] = year_manifest[
    "start_date"
] - pd.Timedelta(days=DAYS_BEFORE_CURRENT_CALL)
```

The plan says lines 357–363. Actual content at line 357 is merely `year_manifest = full_manifest[full_manifest["year"] == year].copy()` — the year-filtering line, not the window. The window assignment starts at line 358. The off-by-one is minor but the plan's line numbers are stale.

**The window described in the plan is correct:** current code uses `[prev_call_date + 5d, start_date − 5d]`. This is a **pre-call** window measuring illiquidity *leading up to* the call.

**The proposed fix has a critical dependency that is NOT addressed:**

To change to post-call window `[call+1d, next_call−5d]`, the code needs `next_call_date` for each call. `next_call_date` is **not computed anywhere** in `_crsp_engine.py`. The current code computes `prev_call_date` via `full_manifest.groupby("gvkey")["start_date"].shift(1)` (line 323). A `next_call_date` would require `shift(-1)` on the same sorted column. The plan does not specify where to add this derivation. The change is a 3-line edit to the window formula but requires a 1-line precursor to compute `next_call_date`.

**Additionally:** `_compute_returns_for_manifest()` at line 182 has a guard:

```python
valid = manifest[
    manifest["permno_int"].notna()
    & manifest["prev_call_date"].notna()   # <-- checks prev_call_date
    & (manifest["window_end"] > manifest["window_start"])
].copy()
```

If the window changes to post-call, the `prev_call_date.notna()` guard becomes semantically wrong — it should check `next_call_date.notna()`. The plan does not mention updating this guard. **This is a missed dependency that would silently over-include or under-include observations after the fix.**

**MISSED ISSUE — Last-call edge case:** For the last call a firm ever makes, `next_call_date` will be NaN (shift(-1) returns NaN at the boundary). This means every firm's final call is dropped from the DV sample. With ~4 calls/year across 2002–2018 (≈17 years, ≈68 calls per firm), the last call represents roughly 1.5% of each firm's observations. The plan does not address how to handle this boundary case. The H9 panel builder (which also needs `next_call_date`) fills it with a censor date (`censor_date = pd.Timestamp("2019-01-01")`). The plan should specify the analogous treatment for H7 — either a fixed censor date or simply dropping the last call.

---

## L2 — Panel Index Fix

### Plan Claim
`run_h7_illiquidity.py:212` sets index as `(gvkey, year)` — non-unique. Fix: derive `call_quarter` in panel builder; switch index to `(gvkey, call_quarter)` in runner. Also remove redundant year derivation at line 169.

### Verdict: CORRECT LINE NUMBER, TECHNICALLY INVALID FIX

**Line 212 is correct.** The actual code is:

```python
# Line 212 of src/f1d/econometric/run_h7_illiquidity.py
df_panel = df_reg.set_index(["gvkey", "year"])
```

This is called inside `run_regression()`. The `(gvkey, year)` index is indeed non-unique if a firm has multiple calls in the same year — which is the norm (4 calls/year typically).

**The proposed fix is TECHNICALLY INVALID.** The plan proposes deriving `call_quarter` via `dt.to_period('Q').astype(str)`, producing strings like `"2007Q3"`. This was empirically tested against linearmodels 7.0 (the installed version):

```
PanelOLS FAILED: The index on the time dimension must be either numeric or date-like
```

`linearmodels.panel.PanelOLS` requires the time dimension index to be **numeric or date-like**. A string such as `"2007Q3"` is neither. The string period index will raise a `ValueError` at model estimation time, not a warning.

**Correct alternatives the plan could use:**
1. Use a `pd.Period` object (not cast to string): `df["call_quarter"] = pd.to_datetime(df["start_date"]).dt.to_period("Q")` — pandas Period objects are accepted by linearmodels as date-like.
2. Use a numeric quarter index: `df["quarter_int"] = year * 4 + quarter_number`.
3. Keep `year` as the time index but accept that quarter-level variation within a year is absorbed into the entity FE.

**The non-uniqueness problem also persists with quarterly index:** If a firm has 2 calls in Q3 2007 (e.g., two supplemental calls), then `(gvkey, "2007Q3")` is still non-unique. The plan does not address this. With 4 calls/year on average across 17 years, the median firm has roughly 1 call per quarter. But firms with more frequent quarterly reporting can still have duplicates. The plan does not specify how to deduplicate (e.g., keep first, aggregate, or require uniqueness).

**Line 169 claim is correct** — there is a guard at line 168–169:

```python
if "year" not in df.columns:
    df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year
```

The panel builder already derives `year` at line 147 (`panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year`), so the runner's derivation at line 169 is indeed redundant. But removing it is only safe once `year` is guaranteed to be in the panel output. This is currently satisfied, but the plan should note the dependency.

---

## L4 — Winsorization Table Notes

### Plan Claim
Linguistic IVs use `winsorize_by_year(lower=0.0, upper=0.99)` in `_linguistic_engine.py`. Decision: correct table notes only (no code change).

### Verdict: VERIFIED — but LaTeX table note is PARTIALLY WRONG

**The code claim is correct.** `_linguistic_engine.py` line 256:

```python
combined = winsorize_by_year(
    combined, existing_pct_cols, year_col="year",
    lower=0.0, upper=0.99, min_obs=10  # Harmonized with Compustat/CRSP engines
)
```

`lower=0.0` means no lower-tail winsorization. This is intentional (percentage variables are bounded below at 0).

**The LaTeX table note in `run_h7_illiquidity.py` at line 350 currently says:**

```
r"All continuous controls are winsorized at 1\%/99\% per year. "
```

This is wrong for the linguistic IVs, which are winsorized at 0%/99% (upper-only). The note lumps all variables together. The plan's decision to "correct table notes only" is the right call, but the fix needs to distinguish: financial controls (CRSP variables, Compustat) use 1%/99% (`winsorize_by_year` default `lower=0.01`), while linguistic IVs use 0%/99%.

**IMPORTANT — The plan does not state what the note should be changed TO.** "Correct table notes only" is not actionable without a specific replacement string.

---

## L5 — CEO Selection Bias

### Plan Claim
Run probit: `CEO_present ~ Size + Lev + ROA + TobinsQ + Volatility + year FE`.

### Verdict: TECHNICALLY INFEASIBLE AS STATED

**`CEO_present` does not exist as a column anywhere in the codebase.** Searched the entire `src/f1d/` tree. There is no variable builder for it, no reference in any panel builder, and no manifest field for it. The manifest fields loaded by `ManifestFieldsBuilder` are: `file_name, ceo_id, ceo_name, gvkey, ff12_code, ff12_name, start_date`.

**The `ceo_id` and `ceo_name` fields exist** in the manifest, but `CEO_present` (a binary indicator that the CEO participated in the call) would need to be derived from raw transcript data or a separate parsing step. The plan does not specify where this variable comes from.

**This step cannot be executed without first defining and building `CEO_present`.** The plan says "CEO presence characterisation — After Step 10 — new probit script" but does not acknowledge that the variable itself is missing from the pipeline. This is a data gap, not just a script gap.

---

## L8 — B-Spec Silent NaN

### Plan Claim
`ceo_clarity_residual.py:43` has `except FileNotFoundError: return empty VariableResult`. Decision: add `RuntimeError` check in runner before B1/B2 specs.

### Verdict: VERIFIED LINE, INCOMPLETE FIX

**Line 43 is correct.** The actual code at `src/f1d/shared/variables/ceo_clarity_residual.py` lines 41–52:

```python
try:
    source_df = engine.get_ceo_residuals(root_path)
except FileNotFoundError as e:
    # Return empty result if residuals not yet computed
    return VariableResult(
        data=pd.DataFrame(columns=["file_name", self.column]),
        stats=VariableStats(
            name=self.column, n=0, mean=0.0, std=0.0, min=0.0,
            p25=0.0, median=0.0, p75=0.0, max=0.0, n_missing=0, pct_missing=100.0
        ),
        ...
    )
```

The silent failure mechanism is correctly identified. When `FileNotFoundError` is caught, the builder returns an empty DataFrame, which merges cleanly into the panel as all-NaN `CEO_Clarity_Residual`. The runner then runs B1/B2 with a column that is entirely NaN, producing a regression with zero observations (since `dropna(subset=required)` drops all rows). The current code at line 466–467 in the runner does catch the all-NaN DV case but not the all-NaN IV case.

**The plan's proposed fix ("add RuntimeError check before B1/B2 specs") is incomplete:** The plan does not specify the exact check. The correct check in `run_regression()` would be:

```python
if df_sample[iv_var].isna().all():
    print(f"  SKIP: {iv_var} is entirely NaN (residuals not computed)")
    return None, {}
```

However, this only covers the all-NaN case. The residual could also be mostly-NaN (e.g., if H0.3 was run on a different sample period), producing a regression with far fewer observations than expected with no warning. The plan does not address partial coverage.

**MISSED DEPENDENCY:** The `_clarity_residual_engine.py` (`ClarityResidualEngine._get_output_dir`) calls `get_latest_output_dir(base_dir)` without `required_file=` argument. This means it will return any timestamped directory, even one that doesn't contain `ceo_clarity_residual.parquet`. The `FileNotFoundError` is raised inside `_load_residuals()` when `file_path.exists()` is False, but only after the directory lookup succeeds. If the `ceo_clarity_extended/` output directory doesn't exist at all, `get_latest_output_dir` raises `OutputResolutionError`, not `FileNotFoundError`. The `except FileNotFoundError` in `CEOClarityResidualBuilder.build()` would **not** catch `OutputResolutionError`. This is a bug: the builder silently fails only for `FileNotFoundError`; an `OutputResolutionError` would propagate upward and crash the panel build.

---

## L9 — Artifact Pinning / Hash Logging

### Plan Claim
`get_latest_output_dir()` used without hash verification. Decision: add MD5 hash logging to `run_manifest.json`.

### Verdict: PARTIALLY SUPERSEDED + WRONG HASH ALGORITHM

**`run_manifest.json` already exists and already computes file hashes.** The `generate_manifest()` function in `src/f1d/shared/outputs/manifest_generator.py` is called at the end of both the panel builder and the runner. It already:
1. Computes SHA256 hashes of input files via `_sha256_file()` (lines 130–145).
2. Writes to `run_manifest.json`.
3. Uses **chunked reading** (`iter(lambda: f.read(8192), b"")`) — no memory risk for large parquet files.

**The plan proposes MD5** but the codebase already uses **SHA256**. MD5 is cryptographically weaker. The plan's fix is not only unnecessary (hash logging already exists) but proposes the wrong algorithm.

**What is actually missing:** The runner does not hash the panel file that `get_latest_output_dir()` resolves at runtime. Looking at the runner's `generate_manifest()` call (lines 565–575):

```python
generate_manifest(
    output_dir=out_dir,
    stage="stage4",
    timestamp=timestamp,
    input_paths={"panel": panel_file},
    output_files={...},
    panel_path=panel_file,
)
```

`panel_file` is passed as both `input_paths["panel"]` and `panel_path`. Both trigger SHA256 hashing in the existing implementation (`_compute_input_hashes` and the `if panel_path:` block). **The panel hash is already logged.** The plan's L9 is solving a problem that was already solved.

---

## L11 — Absorbed Variables Logging

### Plan Claim
Model has `.absorbed_variables` attribute. Decision: log via `warnings.warn()`.

### Verdict: TECHNICALLY INVALID — ATTRIBUTE DOES NOT EXIST

**`linearmodels.panel.results.PanelEffectsResults` does NOT have an `.absorbed_variables` attribute.** Verified against linearmodels 7.0 (the installed version):

```python
from linearmodels.panel.results import PanelEffectsResults
attrs = [a for a in dir(PanelEffectsResults) if 'absorb' in a.lower()]
# Result: []
```

The attribute list is empty. The plan invented this attribute name.

The runner passes `drop_absorbed=True` to `PanelOLS.from_formula()`. When variables are absorbed by fixed effects, linearmodels silently drops them from the model. There is no result attribute that records which variables were absorbed.

**To log absorbed variables the plan would need a different approach:** Compare the set of regressors in `formula` to `model.params.index` after estimation. Any IV in the formula not appearing in `model.params` was absorbed. This is the correct implementation, but it is not what the plan proposes.

---

## L14 — ff12_code NaN Default

### Plan Claim
`panel_utils.py:67` uses `np.select(default="Main")`. Decision: log NaN count.

### Verdict: CORRECT LINE, INCOMPLETE DIAGNOSIS

**Line 67 in `src/f1d/shared/variables/panel_utils.py` is correct.** The `assign_industry_sample` function:

```python
# Lines 67-73 of panel_utils.py
conditions = [ff12_code == 11, ff12_code == 8]
choices = ["Finance", "Utility"]
return pd.Series(
    np.select(conditions, choices, default="Main"),
    index=ff12_code.index,
    dtype=object,
)
```

NaN `ff12_code` values evaluate to False in `conditions` (since `NaN == 11` is False), so they fall through to `default="Main"`. The plan's description is accurate.

**The plan's fix ("log NaN count") is correct but trivially incomplete:** It proposes only logging. A NaN `ff12_code` means Compustat's FF12 assignment failed — the observation has unknown industry. Silently classifying unknowns as "Main" could inflate the Main sample with misclassified firms. Logging is necessary but the plan does not discuss whether any remediation is needed.

---

## L16/L19 — H7-C Formal Test

### Plan Claim
`run_h7_illiquidity.py:503–543` extracts CEO betas but never uses them; only Manager pair compared. Decision: new joint spec with both Manager IVs + linearmodels Wald test.

### Verdict: CORRECT LINES, VALID BUT INCOMPLETE FIX

**Lines 503–543 are correct.** The code at lines 503–543 extracts `qa_ceo` (A1), `qa_mgr` (A3), `pres_ceo` (A2), and `pres_mgr` (A4). However, only the Manager pair (A3 vs A4) is used in the comparison at lines 536–542. The CEO betas `qa_ceo` and `pres_ceo` are extracted (lines 503–526) but **never referenced after extraction**. The plan's observation is correct.

**The Wald test proposal is technically sound:** `wald_test` exists on `PanelEffectsResults` with signature:

```python
def wald_test(self, restriction=None, value=None, *, formula=None) -> WaldTestStatistic
```

Using `formula="Manager_QA_Uncertainty_pct = Manager_Pres_Uncertainty_pct"` is valid syntax. The `formula` kwarg accepts string equality constraints.

**CRITICAL GAP — The plan does not address collinearity:** A joint regression with both `Manager_QA_Uncertainty_pct` and `Manager_Pres_Uncertainty_pct` as regressors is valid econometrically, but these two variables are correlated (both measure manager language uncertainty, differing only by context). The plan does not state the expected correlation or whether multicollinearity could inflate standard errors enough to make the Wald test uninformative. This is a statistical design choice, not an implementation error, but it is a gap.

**MISSED ISSUE — The restriction matrix comment in the plan is ambiguous:** The plan mentions `[[1,-1,0,...]]` as the restriction matrix but the number of zeros depends on the exact order of regressors in the estimated model, which is determined by the formula string. The `formula=` kwarg to `wald_test` avoids this problem entirely (it does not need the restriction matrix). The plan should commit to one approach and not describe both.

---

## L17 — Orphan Variables

### Plan Claim
`build_h7_illiquidity_panel.py:89–94` loads `Manager_QA_Weak_Modal_pct` and `CEO_QA_Weak_Modal_pct`. Decision: delete these from panel builder.

### Verdict: CORRECT LINE NUMBERS, INCOMPLETE DELETION SCOPE

**Lines 89–94 are correct.** The builder dict entries at lines 89–94:

```python
"manager_qa_weak_modal": ManagerQAWeakModalBuilder(
    var_config.get("manager_qa_weak_modal", {})
),
"ceo_qa_weak_modal": CEOQAWeakModalBuilder(
    var_config.get("ceo_qa_weak_modal", {})
),
```

**The deletion scope is incomplete.** The plan says to delete from the builder dict (lines 89–94) but does not mention the **import statements at lines 40–41**:

```python
from f1d.shared.variables import (
    ...
    ManagerQAWeakModalBuilder,   # line 40
    CEOQAWeakModalBuilder,       # line 41
    ...
)
```

If only lines 89–94 are deleted but lines 40–41 are left, Python will import the builders but not use them — no crash, but dead imports. If lines 40–41 are deleted without removing the entries in the import list from the surrounding import block, the import statement will fail with `ImportError`. The plan must specify both the dict entries (89–94) **and** the import names (40–41) for deletion.

**The runner at line 165 already documents the absence:**

```python
# Note: Weak_Modal_Gap not computed - Manager_Pres_Weak_Modal_pct not in panel
```

This comment is a forward dependency: once the panel builder stops including weak modal columns, this comment becomes the only indicator. The runner's parquet `columns=` load list (lines 403–430) does **not** request any `Weak_Modal` columns, so the runner itself has no changes needed.

---

## L18 — Dead Guard

### Plan Claim
`run_h7_illiquidity.py:483` has a guard `if spec_id in MAIN_ONLY_SPECS and sample != "Main": skip` that cannot trigger.

### Verdict: CORRECT — DEAD CODE CONFIRMED, BUT LINE NUMBER IS WRONG

**The guard exists at line 483, but the surrounding context must be understood.** Line 483:

```python
if spec_id in MAIN_ONLY_SPECS and sample != "Main":
```

`CONFIG["samples"]` at line 91 is `["Main"]` — only the Main sample is in the loop. The outer loop at line 476 is `for sample in CONFIG["samples"]`, so `sample` is always `"Main"`. Therefore `sample != "Main"` is always False, and the guard is permanently dead code.

**Verdict: VERIFIED.** The guard is dead. The plan's diagnosis is correct.

**Minor issue:** The dead guard's `print` at line 484 (`print(f"\n--- {sample} / {spec_id}: SKIPPED (Main-only spec) ---")`) is unreachable. The enclosing `for sample in CONFIG["samples"]` at line 476 is the only place to add additional samples. The guard was presumably left over from when the runner previously iterated multiple samples. Removing it is safe.

---

## L20 — Docstring

### Plan Claim
Module docstring at lines 18–23 says "4 specs (A1–A4)" but 6 are run.

### Verdict: CORRECT, PARTIALLY

**Lines 18–23 of `run_h7_illiquidity.py`:**

```python
Specifications (4 single-IV regressions):
    A1: CEO_QA_Uncertainty_pct
    A2: CEO_Pres_Uncertainty_pct
    A3: Manager_QA_Uncertainty_pct
    A4: Manager_Pres_Uncertainty_pct
```

The docstring says "4 single-IV regressions (A1–A4)". The `SPECS` list at lines 104–113 defines 6 specs: A1, A2, A3, A4, B1, B2. The docstring is outdated — it predates B1/B2 addition.

**Lines 19–23 are the correct location.** The fix should update "4 single-IV regressions" to "6 regressions (A1–A4 raw uncertainty; B1–B2 clarity residuals)" and add B1/B2 to the spec list. This is mechanical and the plan is correct.

---

## L12/L13 — Two-Way Clustering Robustness Battery

### Plan Claim
`linearmodels` supports `cluster_entity=True, cluster_time=True` simultaneously.

### Verdict: VERIFIED — TWO-WAY CLUSTERING IS SUPPORTED

**Confirmed against linearmodels 7.0 source.** The `PanelOLS.fit()` docstring (verified in source):

```
"cluster_time" - Boolean indicating to use time clusters
"cluster_entity" - Boolean flag indicating to use entity clusters
```

`ClusteredCovariance` supports up to 2-way clustering (verified: `if clusters.ndim > 2 or dim1 > 2: raise ValueError("Only 1 or 2-way clustering supported.")`). Using both `cluster_entity=True` and `cluster_time=True` is valid.

**INCOMPLETE SPECIFICATION — Pre/post-GFC subperiods:** The plan proposes pre/post-GFC subsamples but does not define the break date. Options differ: 2007-Q3 (Bear Stearns), 2008-Q3 (Lehman), or 2009-Q1 (NBER trough). The plan must commit to one.

**INCOMPLETE SPECIFICATION — Balanced panel:** The plan mentions "balanced panel (firms present in all years 2002–2018)". With 17 years and at minimum 4 calls/year required, firms must have ≥68 calls over the full period. The original unbalanced panel may have ~4,000 unique firms; a balanced panel over 17 years likely retains fewer than 500 firms (large, long-lived firms only). This survivorship bias means the balanced panel is not a robustness check — it is a completely different sample of large incumbents. The plan does not acknowledge this.

---

## MISSED ISSUES (Plan Omissions)

### M1 — `_compute_returns_for_manifest` guard must be updated with window change

If L1/L3 is implemented (post-call window), the validity guard at line 182 of `_crsp_engine.py`:

```python
valid = manifest[
    manifest["permno_int"].notna()
    & manifest["prev_call_date"].notna()   # THIS MUST CHANGE
    & (manifest["window_end"] > manifest["window_start"])
].copy()
```

`manifest["prev_call_date"].notna()` will always be True for any call with a prior call (since `prev_call_date` is still computed for the MAJOR-2 fix) but semantically it's the wrong guard. After the window change, the guard should be `manifest["next_call_date"].notna()`. The plan does not mention this function or its guard.

### M2 — `DAYS_AFTER_PREV_CALL` and `DAYS_BEFORE_CURRENT_CALL` constants become wrong

The constants at lines 41–42 of `_crsp_engine.py`:

```python
DAYS_AFTER_PREV_CALL = 5
DAYS_BEFORE_CURRENT_CALL = 5
```

For a post-call window `[call+1d, next_call−5d]`, the names become semantically incorrect. `DAYS_AFTER_PREV_CALL` would need renaming to `DAYS_AFTER_CURRENT_CALL` (value 1) and `DAYS_BEFORE_CURRENT_CALL` to `DAYS_BEFORE_NEXT_CALL` (value 5). The plan does not mention constant renaming.

### M3 — `call_quarter` index fix does not handle the `year` column in existing panel

The panel builder at line 147 already computes `year`:

```python
panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year
```

If `call_quarter` is added to the panel builder, and the runner's `set_index(["gvkey", "year"])` is changed to `set_index(["gvkey", "call_quarter"])`, the `year` column still exists in the panel and is loaded by the runner (line 407: `"year"` is in the `columns=` list). This means `year` persists as a plain column in the regression data. If `year` is kept as a column but not the index, the `TimeEffects` in the formula (which uses the index) will absorb `call_quarter` variation, not `year` variation. The interpretive meaning of the time FE changes. This is a design decision the plan glosses over.

### M4 — `OutputResolutionError` not caught in `CEOClarityResidualBuilder`

As noted under L8: `ClarityResidualEngine._get_output_dir()` calls `get_latest_output_dir()` which raises `OutputResolutionError` (a custom exception class) if no timestamp directory is found. The `except FileNotFoundError` in `ceo_clarity_residual.py` line 43 does **not** catch `OutputResolutionError`. This means if H0.3 has never been run (i.e., `outputs/econometric/ceo_clarity_extended/` doesn't exist), the entire panel build crashes rather than silently producing all-NaN residuals. The plan proposes adding a `RuntimeError` check in the runner — but the crash happens in the panel builder, before the runner is involved.

### M5 — The LaTeX table note for the winsorization fix (L4) is ambiguous

The current note says: `"All continuous controls are winsorized at 1%/99% per year."` This is wrong for linguistic IVs. The correct note should distinguish:
- CRSP financial variables: 1%/99% per year (default lower=0.01)
- Linguistic variables: 0%/99% per year (lower=0.0, upper-tail only)
- Compustat variables: need verification (not audited here)

The plan says "correct table notes only" but does not provide the replacement text. Without a specific string, this step is unexecutable.

### M6 — `run_h7_illiquidity.py` reads `year` from the panel but `call_quarter` would need to be added to the parquet read

If `call_quarter` is added to the panel builder (for the L2 fix), the runner's `pd.read_parquet(..., columns=[...])` at lines 403–430 **does not include `call_quarter`** in its column list. The column would be in the parquet file but not loaded. The L2 fix requires adding `"call_quarter"` to the `columns=` list in the runner. The plan does not mention this.

---

## Execution Order Concerns

The plan's execution table claims Step 1 (CRSP engine fix) blocks Step 2 (panel index). This is correct in the sense that both affect the panel rebuild (Step 4). However:

- Step 2's fix (call_quarter) is **technically invalid** as written (string period index). Must be resolved before Step 4 or the panel rebuild succeeds but Step 10 (regression re-run) fails at estimation time.
- Step 3 (L17 deletion) requires deleting **both** the dict entries (89–94) and the import names (40–41). The plan only specifies the dict entries.
- Step 6 (L8 RuntimeError check) is in the wrong layer — the crash originates in the panel builder, not the runner.

---

## Summary Table

| Plan Item | Verdict | Key Finding |
|-----------|---------|-------------|
| L1/L3 CRSP window lines | WRONG LINE NUMBER (358 not 357) + INCOMPLETE FIX | `next_call_date` not computed; validity guard at line 182 not updated; last-call edge case unaddressed |
| L2 panel index | CORRECT LINE (212) + TECHNICALLY INVALID FIX | String period `"2007Q3"` rejected by linearmodels; must use `pd.Period` or integer |
| L4 winsorization | CODE CLAIM VERIFIED | Table note fix is correct but replacement text not specified; `lower=0.0` confirmed |
| L5 CEO selection bias | TECHNICALLY INFEASIBLE | `CEO_present` column does not exist anywhere in the pipeline |
| L8 B-spec silent NaN | CORRECT LINE (43) + INCOMPLETE FIX | `OutputResolutionError` not caught; partial NaN coverage not addressed |
| L9 artifact pinning | FALSE CLAIM — ALREADY IMPLEMENTED | SHA256 hash logging already exists in `generate_manifest()`; uses chunked reads (no memory risk); plan proposes MD5 which is weaker |
| L11 absorbed variables | TECHNICALLY INVALID | `PanelEffectsResults` has no `.absorbed_variables` attribute; correct approach is `set(formula_vars) - set(model.params.index)` |
| L14 ff12_code NaN | VERIFIED | Logging fix is correct but silently reclassifying unknowns as "Main" is a substantive issue |
| L16/L19 H7-C Wald test | CORRECT LINES (503–543) + VALID FIX | `wald_test(formula=...)` API confirmed; collinearity risk not addressed |
| L17 orphan variables | CORRECT LINES (89–94) + INCOMPLETE | Import names at lines 40–41 also need deletion |
| L18 dead guard | VERIFIED (line 483) | Dead code confirmed; safe to remove |
| L20 docstring | VERIFIED (lines 19–23) | "4 specs" should be "6 specs"; fix is straightforward |
| L12/L13 two-way clustering | VERIFIED — SUPPORTED | `cluster_entity=True, cluster_time=True` valid in linearmodels 7.0; balanced panel is survivorship-biased, not a true robustness check |
