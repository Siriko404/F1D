# Hasan-Verbatim H1.6 Redistricting DiD Replication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replicate Hasan, Alam, Paramati & Islam (2022) Table 4 redistricting DiD verbatim — every formula, sample restriction, and variable definition matches the paper. Report whatever significance level emerges; no iteration on Hasan-silent defaults to chase sig.

**Architecture:** Incremental fix-and-verify path on a single runner file. After each fix step, re-run `--hasan18` flag and capture β / p / N / adj R² for all 4 columns. Final spec compared apples-to-apples to Hasan Table 4: Col 1 (Firm FE) +0.007*** | Col 2 (Industry FE) +0.006**.

**Tech Stack:** Python 3.13, pandas, linearmodels.PanelOLS, geopandas (existing). Compustat parquet (existing). Lewis 2013 CD shapefiles (existing). Census Geocoder lat/lon (existing).

**Spec:** `docs/superpowers/specs/2026-05-06-hasan-verbatim-h1-6-replication-design.md`

---

## File Structure

**Modified file:**
- `src/f1d/econometric/run_h1_6_test5_full_compustat.py` — runner with control list, Cashflow formula, window, filters, movers-only filter, winsorization, R&D fillna

**Untouched (do not modify):**
- `src/f1d/shared/variables/redistricting_treatment_geocode.py` — used by F1D body-table runner; runner-local changes only
- `src/f1d/econometric/run_h1_6_redistricting_did.py` — F1D body-table runner

**Output:**
- `outputs/econometric/h1_6_test5_full_compustat/2026-05-06_<HHMMSS>_HASAN_VERBATIM/model_diagnostics.csv` per-step run

---

## Pre-flight: Confirmed Compustat fields available

Verified via parquet schema (`pq.ParquetFile.schema_arrow`):

```
oibdpq  ✓  (Operating Income Before D&A, quarterly)
xintq   ✓  (Interest Expense, quarterly)
txtq    ✓  (Total Tax, quarterly)
dvy     ✓  (Total Dividends, YTD — needs quarterly conversion)
dlcq    ✓  (Debt Current, quarterly)
dlttq   ✓  (Debt Long-Term, quarterly)
aqcy    ✓  (Acquisitions, YTD)

NOT FOUND: dvcy (Common Dividends YTD)
DEVIATION: substitute DVY for DVC in Cashflow formula. DVY = total dividends 
           includes preferred. Document as minor deviation — Compustat lacks 
           DVCY in our parquet. Effect on β should be negligible (preferred 
           dividends are tiny share for non-financial firms).
```

---

### Task 1: D4 — Drop ROA, sCFO, SalesGrowth from CONTROLS

**Files:**
- Modify: `src/f1d/econometric/run_h1_6_test5_full_compustat.py:72-77`

- [ ] **Step 1.1: Read current CONTROLS list**

The current code at lines 72-77:
```python
CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt",
    "NWC", "Acquisition", "IndustrySigma",
]
```

- [ ] **Step 1.2: Replace with Hasan-verbatim 10-control list**

Edit to:
```python
# Hasan 2022 Table 4 verbatim 10-control list (Appendix A Table 12).
# Hasan does NOT include ROA, sCFO, or SalesGrowth — dropped 2026-05-06.
# PRisk also NOT used as a separate control in Table 4 (NLM Q3+Q4 confirmed).
CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ",
    "Capex", "DivDummy",
    "RDSales", "CashFlowAt",
    "NWC", "Acquisition", "IndustrySigma",
]
```

- [ ] **Step 1.3: Run --hasan18 to verify still works + capture β baseline**

Run: `PYTHONPATH=src python -m f1d.econometric.run_h1_6_test5_full_compustat --hasan18 2>&1 | tail -15`

Expected: 4 specs print β/p/N/adj_R² without errors. Record values:
```
Col (1) FE=industry        β=____  p_one=____  N=____  adj_R²=____
Col (2) FE=firm            β=____  p_one=____  N=____  adj_R²=____
Col (3) FE=industry_yq     β=____  p_one=____  N=____  adj_R²=____
Col (4) FE=firm_yq         β=____  p_one=____  N=____  adj_R²=____
```

Pre-task baseline (current code with all 13 controls + 2002-2021):
```
Col 1 industry FE        β=+0.0186  p_one=0.098  N=25,906  adj_R²=0.292
Col 2 firm FE            β=+0.0057  p_one=0.31   N=25,906  adj_R²=0.072
```

- [ ] **Step 1.4: Commit**

```bash
git add src/f1d/econometric/run_h1_6_test5_full_compustat.py
git commit -m "Hasan-verbatim D4: drop ROA, sCFO, SalesGrowth from CONTROLS

Hasan 2022 Table 4 11-control list (Appendix A) does not include ROA, sCFO, 
or SalesGrowth. Removing per verbatim audit. PRisk also not a Table 4 
control per NLM Q3+Q4.

Pre: β industry-FE +0.0186 p_one=0.098 N=25,906 (13 controls)
Post: β industry-FE [filled in from Step 1.3] (10 controls)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: D5 — fillna(0) on RDSales for missing R&D

**Files:**
- Modify: `src/f1d/econometric/run_h1_6_test5_full_compustat.py:185`

- [ ] **Step 2.1: Read current R&D computation**

Line 185:
```python
df["RDSales"] = df["xrdq"] / df["saleq"].replace({0: np.nan})
```

- [ ] **Step 2.2: Add fillna(0) per Hasan verbatim**

Replace with:
```python
# Hasan 2022 verbatim: "the value of R&D is set to zero" for missing.
df["RDSales"] = (df["xrdq"] / df["saleq"].replace({0: np.nan})).fillna(0.0)
```

- [ ] **Step 2.3: Run --hasan18, capture results**

Run: `PYTHONPATH=src python -m f1d.econometric.run_h1_6_test5_full_compustat --hasan18 2>&1 | tail -15`

Expected: N firms may increase if R&D missing was dropping firms.

- [ ] **Step 2.4: Commit**

```bash
git add src/f1d/econometric/run_h1_6_test5_full_compustat.py
git commit -m "Hasan-verbatim D5: R&D missing -> 0 (verbatim from paper)

Per Hasan 2022: 'the value of R&D is set to zero'. Previously NaN
propagated, dropping firms with missing XRD.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: D3 — Industry sigma rolling window 5y → 10y

**Files:**
- Modify: `src/f1d/econometric/run_h1_6_test5_full_compustat.py:211-217`

- [ ] **Step 3.1: Read current industry sigma logic**

Lines 211-217:
```python
# IndustrySigma: SIC2-level avg SD of cashflow/atq over the past 5 years
# (Hasan: 10 years; we use 5 because data starts 2002 and pre-window 2006).
df["sic2"] = (df["sic_int"] // 100).astype(int)
# Per-firm rolling 5-yr SD of CashFlowAt; then average per (sic2, datadate)
df["__cfa_5yr_sd"] = df.groupby("gvkey", sort=False)["__cf_at"].transform(
    lambda s: s.rolling(20, min_periods=8).std()
)
```

- [ ] **Step 3.2: Change rolling window 20q → 40q (10y)**

Replace with:
```python
# IndustrySigma: SIC2-level avg SD of cashflow/atq over the past 10 years
# (Hasan 2022 verbatim: "for the past 10 years"). Reverted from 5y after
# Hasan-verbatim audit 2026-05-06.
df["sic2"] = (df["sic_int"] // 100).astype(int)
df["__cfa_10yr_sd"] = df.groupby("gvkey", sort=False)["__cf_at"].transform(
    lambda s: s.rolling(40, min_periods=8).std()
)
```

Also update line 219:
```python
industry_sigma = (
    df.groupby(["sic2", "datadate"])["__cfa_10yr_sd"].mean()
    .rename("IndustrySigma").reset_index()
)
```

- [ ] **Step 3.3: Run --hasan18, capture results**

Run: `PYTHONPATH=src python -m f1d.econometric.run_h1_6_test5_full_compustat --hasan18 2>&1 | tail -15`

Note: 10y window may shift β because earlier-period sigma uses fewer obs.

- [ ] **Step 3.4: Commit**

```bash
git add src/f1d/econometric/run_h1_6_test5_full_compustat.py
git commit -m "Hasan-verbatim D3: industry sigma 5y -> 10y rolling window

Per Hasan 2022 verbatim: 'standard deviation of cash flow is firm-level cash
flow scaled by total assets for the past 10 years'. Was 5y. Aligns with
Hasan's verbatim Industry sigma definition.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Drop our 1/99 winsorization

**Files:**
- Modify: `src/f1d/econometric/run_h1_6_test5_full_compustat.py:232-240`

- [ ] **Step 4.1: Read current winsorization**

Lines 232-240:
```python
# Light winsorization on CashRatio + extreme-tail controls
for col in ("CashRatio", "Leverage", "TobinsQ", "ROA", "Capex",
            "CashFlowAt", "RDSales", "SalesGrowth", "sCFO",
            "NWC", "Acquisition", "IndustrySigma"):
    if col not in df.columns:
        continue
    lo = df[col].quantile(0.01)
    hi = df[col].quantile(0.99)
    df[col] = df[col].clip(lower=lo, upper=hi)
```

- [ ] **Step 4.2: Remove winsorization block entirely**

Replace with comment-only block:
```python
# Hasan 2022 NLM-VERIFIED Q4 EXHAUSTIVE SEARCH: winsorization is ABSENT
# from Hasan's paper. We drop our 1/99 winsorization to match Hasan's
# silent default (raw values).
```

- [ ] **Step 4.3: Run --hasan18, capture results**

Run: `PYTHONPATH=src python -m f1d.econometric.run_h1_6_test5_full_compustat --hasan18 2>&1 | tail -15`

Note: dropping winsorization may introduce extreme outliers; β / SE could change substantially.

- [ ] **Step 4.4: Commit**

```bash
git add src/f1d/econometric/run_h1_6_test5_full_compustat.py
git commit -m "Hasan-verbatim: drop our 1/99 winsorization (Hasan silent)

NLM Query 4 EXHAUSTIVE SEARCH confirmed Hasan 2022 paper has no mention
of winsorization, truncation, or outlier handling anywhere. We drop our
1/99 winsorization to match Hasan's silent default.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Drop ≥8 PRisk filter, change to ≥1

**Files:**
- Modify: `src/f1d/econometric/run_h1_6_test5_full_compustat.py:333-336`

- [ ] **Step 5.1: Read current PRisk filter**

Lines 333-336:
```python
firm_qcount = prisk.groupby("gvkey")["cal_q"].nunique().rename("n_pre")
firm_prisk = firm_prisk.merge(firm_qcount, on="gvkey", how="left")
# F1 attempt (relax to >=1): increased N to 29,045 but DILUTED beta from
# +0.01855* to +0.00745 ns. Noisy short-window firms hurt signal.
# Reverted to >=8.
firm_prisk = firm_prisk[firm_prisk["n_pre"] >= 8].copy()
```

- [ ] **Step 5.2: Change to ≥1**

Replace with:
```python
firm_qcount = prisk.groupby("gvkey")["cal_q"].nunique().rename("n_pre")
firm_prisk = firm_prisk.merge(firm_qcount, on="gvkey", how="left")
# Hasan 2022 NLM-VERIFIED Q4 EXHAUSTIVE SEARCH: no min-PRisk-obs filter
# is mentioned in the paper. We use >=1 (any pre-window PRisk obs) to
# match Hasan's silent default.
firm_prisk = firm_prisk[firm_prisk["n_pre"] >= 1].copy()
```

- [ ] **Step 5.3: Run --hasan18, capture results**

Run: `PYTHONPATH=src python -m f1d.econometric.run_h1_6_test5_full_compustat --hasan18 2>&1 | tail -15`

Note: drops min-obs filter; brings in firms with as little as 1 quarter PRisk in 2006-2010 pre-window.

- [ ] **Step 5.4: Commit**

```bash
git add src/f1d/econometric/run_h1_6_test5_full_compustat.py
git commit -m "Hasan-verbatim: relax PRisk filter >=8 to >=1 (Hasan silent)

NLM Query 4 EXHAUSTIVE SEARCH confirmed Hasan 2022 paper has no mention
of any min-quarters / min-obs / continuity filter on firms beyond the
SIC industry exclusions. We relax our >=8 to >=1 to match Hasan's
silent default.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: D2 — Cashflow formula = (OIBDPQ - XINTQ - TXTQ - DVY_q) / ATQ

**Files:**
- Modify: `src/f1d/econometric/run_h1_6_test5_full_compustat.py:122-128, 149-156, 158-163, 166-184`

- [ ] **Step 6.1: Add new Compustat fields to load**

At line 122-128, modify `cols` list to add `oibdpq, xintq, txtq`:
```python
cols = [
    "gvkey", "datadate", "fqtr", "sic",
    "atq", "cheq", "dlcq", "dlttq", "ceqq", "cshoq", "prccq",
    "niq", "capxy", "dvy", "saleq", "xrdq", "oancfy",
    "wcapq", "aqcy",
    "oibdpq", "xintq", "txtq",  # Hasan-verbatim Cashflow components
]
```

- [ ] **Step 6.2: Add new fields to numeric_cols cast**

At line 149-156, modify `numeric_cols`:
```python
numeric_cols = [
    "atq", "cheq", "dlcq", "dlttq", "ceqq", "cshoq", "prccq",
    "niq", "capxy", "dvy", "saleq", "xrdq", "oancfy", "fqtr",
    "wcapq", "aqcy",
    "oibdpq", "xintq", "txtq",  # Hasan-verbatim Cashflow components
]
```

- [ ] **Step 6.3: Add Cashflow numerator computation**

At line 158-163 (after ytd_to_quarterly converters), the existing code converts YTD fields. Add a comment + nothing else here (oibdpq, xintq, txtq are already QUARTERLY in Compustat — no YTD conversion needed):
```python
# ---- Convert YTD fields to quarterly ----
df = df.dropna(subset=["fqtr"])
df = _ytd_to_quarterly(df, "capxy", "capx_q")
df = _ytd_to_quarterly(df, "dvy", "dv_q")
df = _ytd_to_quarterly(df, "oancfy", "oancf_q")
df = _ytd_to_quarterly(df, "aqcy", "aqc_q")
# Note: oibdpq, xintq, txtq are already quarterly in Compustat — no
# YTD conversion needed.
```

- [ ] **Step 6.4: Replace CashFlowAt formula**

At line 184 currently:
```python
df["CashFlowAt"] = df["oancf_q"] / df["atq"]
```

Replace with:
```python
# Hasan 2022 verbatim Cashflow formula:
# (OIBDP - XINT - TXT - DVC) / AT
# Compustat substitution: DVCY not in our parquet, use DVY (total div) as proxy.
# Preferred dividends are negligible for non-financial firms in this sample.
df["CashFlowAt"] = (
    df["oibdpq"] - df["xintq"] - df["txtq"] - df["dv_q"]
) / df["atq"]
```

- [ ] **Step 6.5: Verify the __cf_at helper still works**

The helper `__cf_at` at line 195 uses `oancf_q / __atq_lag` for sCFO + IndustrySigma. After this change, sCFO is dropped (Task 1) but IndustrySigma still uses `__cf_at`. We need IndustrySigma to use the SAME Hasan Cashflow formula scaled by AT lag.

Modify line 193-195:
```python
df["__atq_lag"] = df.groupby("gvkey", sort=False)["atq"].shift(1)
# Use Hasan-verbatim Cashflow formula for IndustrySigma input
df["__cf_at"] = (
    df["oibdpq"] - df["xintq"] - df["txtq"] - df["dv_q"]
) / df["__atq_lag"]
```

- [ ] **Step 6.6: Remove sCFO computation block**

At line 196-198 (after the change above), delete:
```python
df["sCFO"] = df.groupby("gvkey", sort=False)["__cf_at"].transform(
    lambda s: s.rolling(20, min_periods=12).std()
)
```

- [ ] **Step 6.7: Run --hasan18, capture results**

Run: `PYTHONPATH=src python -m f1d.econometric.run_h1_6_test5_full_compustat --hasan18 2>&1 | tail -15`

Note: this is a substantive variable change. β / SE may shift materially.

- [ ] **Step 6.8: Commit**

```bash
git add src/f1d/econometric/run_h1_6_test5_full_compustat.py
git commit -m "Hasan-verbatim D2: Cashflow = (OIBDP-XINT-TXT-DVC)/AT formula

Per Hasan 2022 verbatim Appendix A: 'Cashflow = earnings before
depreciation minus interest expenses minus taxes minus dividends
(OIBDP - XINT - TXT - DVC) all scaled by total assets (AT)'. Replaced
our OANCF (cash flow statement) -based proxy with Hasan's income-statement
formula. DVCY not in parquet -> substitute DVY (preferred dividends
negligible for non-financials).

IndustrySigma input also uses new Cashflow formula now.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: D1 — Sample = MOVERS ONLY (state_cd_pre != state_cd_post)

**Files:**
- Modify: `src/f1d/econometric/run_h1_6_test5_full_compustat.py:337-360, 477-505, 540-560`

- [ ] **Step 7.1: Identify mover label upstream**

The runner builds Treated_redist via tertile shift. To filter to movers,
we need to expose `state_cd_pre` + `state_cd_post` columns alongside the
tertile output. Modify the inline geocode chain (around lines 337-360) to
also return `state_cd_pre` and `state_cd_post` per firm.

Read existing logic at line 337-360 first via:

```bash
sed -n '337,365p' src/f1d/econometric/run_h1_6_test5_full_compustat.py
```

- [ ] **Step 7.2: Persist state_cd_pre + state_cd_post on per-firm Treated DataFrame**

Inside `attach_redist_treatment`, after the existing tertile block, the function builds a `firm` DataFrame with columns including `state_cd_pre`, `state_cd_post`, `pre_tertile`, `post_tertile`, `Treated_redist`. Currently only `Treated_redist` propagates to the panel.

Find the merge step that attaches treatment to panel (around line 360-370). Add `state_cd_pre` + `state_cd_post` to the columns merged into panel.

Apply this edit pattern (exact location + line numbers depend on current file state — read with `sed` first):

```python
# Before:
panel = panel.merge(
    firm[["gvkey", "Treated_redist", "Post_redist", "DiD_Redist"]],
    on=["gvkey", "year"], how="left",
)

# After:
panel = panel.merge(
    firm[["gvkey", "Treated_redist", "Post_redist", "DiD_Redist",
          "state_cd_pre", "state_cd_post"]],
    on=["gvkey", "year"], how="left",
)
```

- [ ] **Step 7.3: Add filter_movers_only function**

Add a new function near `filter_hasan_18` and `filter_drop_unchanged`:

```python
def filter_movers_only(panel: pd.DataFrame) -> pd.DataFrame:
    """Hasan 2022 verbatim: 'these moving firms constitute our treated firms'.
    Sample restricted to firms whose pre- and post-redistricting CD differ
    (state_cd_pre != state_cd_post). Firms whose CD assignment did not
    change between 111th and 113th Congress are excluded entirely.
    """
    n_before = len(panel)
    firms_before = panel["gvkey"].nunique()
    panel = panel[
        panel["state_cd_pre"].notna()
        & panel["state_cd_post"].notna()
        & (panel["state_cd_pre"] != panel["state_cd_post"])
    ].copy()
    n_after = len(panel)
    firms_after = panel["gvkey"].nunique()
    print(
        f"  Movers-only filter: {n_after:,} / {n_before:,} firm-qtrs "
        f"({firms_after:,} / {firms_before:,} firms)"
    )
    return panel
```

- [ ] **Step 7.4: Add CLI flag --movers-only**

Add to argparse near `--hasan18` and `--drop-unchanged`:
```python
p.add_argument("--movers-only", action="store_true",
               help="Hasan 2022 verbatim sample restriction: keep only "
                    "firms whose pre/post congressional district differs "
                    "(state_cd_pre != state_cd_post). 'These moving firms "
                    "constitute our treated firms' (Hasan §5.1).")
```

- [ ] **Step 7.5: Wire up --movers-only into main**

Add to `main()` function signature + body:
```python
def main(hasan18: bool = False, drop_unchanged: bool = False,
         movers_only: bool = False) -> int:
    ...
    print(f"Diag flags:   hasan18={hasan18} drop_unchanged={drop_unchanged} "
          f"movers_only={movers_only}")
    ...
    # After hasan18 filter:
    if hasan18:
        panel = filter_hasan_18(panel, root)
    if movers_only:
        panel = filter_movers_only(panel)
    ...
```

And update the `__main__` block:
```python
if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(main(
        hasan18=args.hasan18,
        drop_unchanged=args.drop_unchanged,
        movers_only=args.movers_only,
    ))
```

- [ ] **Step 7.6: Run FINAL spec — Hasan-verbatim**

Run:
```bash
PYTHONPATH=src python -m f1d.econometric.run_h1_6_test5_full_compustat --hasan18 --movers-only 2>&1 | tail -15
```

Expected: smaller N (only movers); β/p compared to Hasan Table 4.

- [ ] **Step 7.7: Compare to Hasan Table 4**

Document in commit message:
```
                          OURS                         HASAN Table 4
Industry FE col 1+3       β = ____  p = ____ N = ____  β = +0.006**  p = 0.050  N = 24,311
Firm FE col 2+4           β = ____  p = ____ N = ____  β = +0.007*** p = 0.007  N = 24,311
Adj R² industry-FE        ____                          0.286
Adj R² firm-FE            ____                          0.063
```

- [ ] **Step 7.8: Commit**

```bash
git add src/f1d/econometric/run_h1_6_test5_full_compustat.py
git commit -m "Hasan-verbatim D1: sample = movers only (state_cd_pre != post)

Per Hasan 2022 verbatim Section 5.1: 'these moving firms constitute our
treated firms'. Restricts the regression sample to the 941-firm-equivalent
subset whose pre/post congressional district differs.

FINAL SPEC: --hasan18 --movers-only

Comparison vs Hasan Table 4:
  [filled in from Step 7.6 + 7.7]

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Final result documentation + memory + §V decision

**Files:**
- Create: memory file `~/.claude/projects/<id>/memory/project_session_2026_05_06_hasan_verbatim_replication.md`
- Modify: MEMORY.md index

- [ ] **Step 8.1: Write durable memory with full result table**

Memory contents must include:
- Hasan Table 4 verbatim numbers (Col 1 + Col 2)
- Our final spec result (β, p, N, adj R²) for all 4 columns
- 5 deviations corrected (D1-D5)
- Hasan-silent defaults adopted (sample window, no filters, no winsorization)
- Comparison verdict (replication achieved / partially / failed)
- §V update decision deferred to user

- [ ] **Step 8.2: Update MEMORY.md index**

Add entry with newest-entry pattern.

- [ ] **Step 8.3: Commit memory**

```bash
git add memory/project_session_2026_05_06_hasan_verbatim_replication.md memory/MEMORY.md
git commit -m "memory: Hasan-verbatim H1.6 replication — full result table

Documents the verbatim replication attempt: 5 deviations corrected
(D1-D5), Hasan-silent defaults adopted (window, filters, winsorization,
tie-break, missing-data, lag, PRisk-control), final result vs Hasan
Table 4 verbatim. §V update is a separate decision, deferred.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 8.4: Optional — Stop and ask user about §V update**

Per design doc out-of-scope section: §V prose update is a separate phase. Present comparison table to user, ask whether to:
A) Replace Step 3 result with Hasan-verbatim result in §V auxiliary paragraph
B) Add Hasan-verbatim result alongside Step 3 (side-by-side disclosure)
C) Keep Step 3 in §V; document Hasan-verbatim as memory-only finding

---

## Self-review checklist

After all 8 tasks, verify:

1. **Spec coverage:**
   - D1 movers-only filter → Task 7 ✓
   - D2 Cashflow formula → Task 6 ✓
   - D3 industry sigma 10y → Task 3 ✓
   - D4 drop extras → Task 1 ✓
   - D5 R&D fillna → Task 2 ✓
   - Hasan-silent defaults → Tasks 4 + 5 ✓
   - PRisk-control NOT added → not a task (already excluded) ✓

2. **Placeholder scan:** Tasks 1-7 each have:
   - Exact file:line refs
   - Complete code blocks (no "..." in important code)
   - Run-then-record verification step
   - Commit with template message

   Task 8 has placeholder for "filled in from Step 7.6 + 7.7" — that's
   intentional (results unknown until executed). All other placeholders
   eliminated.

3. **Type/name consistency:**
   - `state_cd_pre`, `state_cd_post` — consistent across Tasks 7.2-7.6 ✓
   - `Treated_redist`, `Post_redist`, `DiD_Redist` — preserved ✓
   - `oibdpq`, `xintq`, `txtq`, `dv_q` — Task 6 fields consistent ✓

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-06-hasan-verbatim-h1-6-replication.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review, fast iteration
2. **Inline Execution** — execute tasks in this session using executing-plans, checkpoints

Which approach?
