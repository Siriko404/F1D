# H14 Bid-Ask Spread: Second-Layer Red-Team Audit

**Audit date:** 2026-03-21
**Auditor role:** Hostile-but-fair replication auditor (second layer)
**Target:** First-layer provenance doc `docs/provenance/H14.md` (v3.0, 2026-03-18)
**Code verified against:** Current working tree as of 2026-03-21

---

## A. Does the first-layer doc accurately describe the runner?

**Verdict: MOSTLY ACCURATE, with minor issues.**

The first-layer doc correctly identifies:
- KEY_IVS: 4 simultaneous uncertainty measures (runner lines 87-91) -- verified.
- BASE_CONTROLS: 8 variables including PreCallSpread (runner lines 96-105) -- verified.
- EXTENDED_CONTROLS: Base + 4 (runner lines 107-112) -- verified.
- MODEL_SPECS: 4 columns, 2 FE x 2 controls (runner lines 114-119) -- verified.
- MIN_CALLS_PER_FIRM = 5 (runner line 121) -- verified.
- DV = DSPREAD (runner line 115) -- verified.
- One-tailed p-value: `p_two / 2 if beta > 0 else 1 - p_two / 2` (runner lines 343-344) -- verified.
- Industry FE via PanelOLS constructor with `entity_effects=False, time_effects=True, other_effects=ff12_code, drop_absorbed=True, check_rank=False` (runner lines 302-310) -- verified.
- Firm FE via `PanelOLS.from_formula` with `EntityEffects + TimeEffects` (runner lines 313-315) -- verified.
- SE: `cov_type="clustered", cluster_entity=True` (runner lines 311, 316) -- verified.

**Issues found:**
- None material in the runner description.

---

## B. Does the first-layer doc accurately describe the panel builder?

**Verdict: MOSTLY ACCURATE, with one factual error.**

Verified claims:
- Builder order and builder names (builder lines 103-141) -- verified.
- Zero-row-delta merge assertion (builder lines 164-169) -- verified.
- Rename `delta_spread_closing` -> `DSPREAD` (builder line 181) -- verified.
- Rename `pre_call_spread_closing` -> `PreCallSpread` (builder line 182) -- verified.
- AbsSurpDec = |SurpDec| (builder lines 186-187) -- verified.
- Winsorize cols = [DSPREAD, PreCallSpread, StockPrice, Turnover, AbsSurpDec] pooled 1%/99% (builder lines 202-203) -- verified.
- fyearq_int = floor(fyearq) (builder lines 195-197) -- verified.

**Issues found:**
- None material in the panel builder description.

---

## C. Raw Data Provenance accuracy

**Verdict: ONE FACTUAL ERROR.**

| Audit doc claim | Actual code | Severity |
|-----------------|-------------|----------|
| Section 4 states Compustat source is `inputs/Compustat/Compustat.parquet` | Code uses `inputs/comp_na_daily_all/comp_na_daily_all.parquet` (`_compustat_engine.py` line 1249) | **ERROR** -- the path `inputs/Compustat/Compustat.parquet` is only used in archived code. The live CompustatEngine loads from a different file. |
| Section 4 states IBES source is `inputs/IBES/IBES.parquet` | Actual IBES engine uses `inputs/tr_ibes/tr_ibes_{YYYY}.parquet` (Section 6.5.4 of the same audit doc correctly states this) | **INCONSISTENCY** -- Section 4 and Section 6.5.4 contradict each other on the IBES path |

The Section 4 "Raw Data Provenance" table lists incorrect file paths for both Compustat and IBES. The detailed construction chains elsewhere in the document use the correct paths, creating an internal contradiction.

---

## D. LINKPRIM inconsistency -- is the audit's characterization accurate?

**Verdict: ACCURATE.**

Independently verified:
- `bidask_spread_change.py` lines 144, 159-161: loads `linkprim` column, filters `linkprim in ["P", "C"]` -- confirmed.
- `stock_price.py` lines 96-101: loads only `[linkdt, linkenddt]`, no `linkprim` -- confirmed.
- `turnover.py` lines 97-101: loads only `[linkdt, linkenddt]`, no `linkprim` -- confirmed.
- `_crsp_engine.py` lines 335-349: loads only `[linkdt, linkenddt]`, no `linkprim` -- confirmed.
- `_ibes_engine.py` lines 70-76: loads `LINKPRIM`, filters `["P", "C"]` -- confirmed.

The first-layer doc's builder-by-builder table (Section 5.2, Section 6.6) is accurate and complete.

---

## E. Variable construction chains -- spot checks

**Verdict: ACCURATE on spot-checked variables.**

1. **DSPREAD construction:** `spread_closing = 2 * (ASK - BID) / (ASK + BID)` at `bidask_spread_change.py` lines 346-348 -- confirmed. Event windows [-3,-1] pre and [+1,+3] post at lines 386-387 -- confirmed. Minimum valid days = `max(1, w-1) = 2` at lines 300-302 -- confirmed.

2. **Volatility formula:** `std_ret * sqrt(252) * 100` with `MIN_TRADING_DAYS = 10` guard (`_crsp_engine.py` lines 247-256) -- confirmed.

3. **BookLev:** Thin wrapper calling CompustatEngine, confirmed via `book_lev.py`.

---

## F. Volatility measurement window description

**Verdict: HEADER DESCRIPTION IS MISLEADING.**

Section 6.5.3's header table says:
> **Measurement window** | Inter-call window: `[prev_call_date + 5 trading days, current_call_date - 5 trading days]`

But the actual code (`_crsp_engine.py` lines 361-366) implements:
```
window_start = start_date + 1 calendar day    (DAYS_AFTER_CURRENT_CALL = 1)
window_end   = next_call_date - 5 calendar days (DAYS_BEFORE_NEXT_CALL = 5)
```

The header describes a **backward-looking** window (from the previous call to the current call), but the code implements a **forward-looking** window (from the current call to the next call). The detailed construction chain (Steps 1-4) within the same section correctly describes the forward-looking window. This internal contradiction could mislead a reader who only reads the summary table.

Additionally, the audit says "trading days" but the offsets are applied via `pd.Timedelta(days=...)`, which uses **calendar days**, not trading days. The actual trading-day filtering happens downstream when CRSP data (which only has trading days) is matched within the window.

---

## G. Attrition table accuracy

**Verdict: MINOR DISCREPANCY.**

The first-layer audit (Section 5.3) documents 5 attrition stages:
1. Full panel
2. Main sample
3. DSPREAD non-null
4. Complete cases
5. MIN_CALLS_PER_FIRM >= 5

But the actual runner code (lines 720-725) only generates 4 attrition stages, merging stages 4 and 5 into one:
```
("After complete-case + min-calls (col 1)", first_meta.get("n_obs", 0))
```

The audit's conceptual decomposition into 5 stages is correct from a logical standpoint, but the actual output artifact will show only 4 rows. This is a documentation-vs-artifact discrepancy, not a code error.

---

## H. Winsorization description accuracy

**Verdict: ACCURATE.**

- Pooled 1%/99% on [DSPREAD, PreCallSpread, StockPrice, Turnover, AbsSurpDec] at builder level -- confirmed (builder lines 202-203).
- Per-year 1%/99% on Volatility via CRSPEngine -- confirmed (`_crsp_engine.py` lines 444-447).
- Per-year 1%/99% on Compustat variables via CompustatEngine -- confirmed.
- DividendPayer not winsorized (binary) -- confirmed.
- Winsorization computed on full panel before Main-sample filter -- correctly flagged in Section 12 (L6).

The winsorization summary table is complete and accurate.

---

## I. P-value and significance star accuracy

**Verdict: ACCURATE.**

One-tailed conversion: `p_two / 2 if beta > 0 else 1 - p_two / 2` (runner lines 343-344) -- confirmed.
Stars: `*** < 0.01, ** < 0.05, * < 0.10` (runner lines 368-374) -- confirmed.
LaTeX table note correctly states one-tailed with H14: beta > 0 -- confirmed.

---

## J. Fixed effects specification accuracy

**Verdict: ACCURATE.**

- Time index: `set_index(["gvkey", "fyearq_int"])` (runner line 295) -- confirmed.
- Industry FE: absorbed via `other_effects=ff12_code` (not C() dummies) -- confirmed.
- Firm FE: via `EntityEffects` in formula -- confirmed.
- The audit correctly notes that `fyearq_int = floor(fyearq)` is fiscal year, not quarter, and that quarterly seasonality is uncontrolled (Section 11.3).

---

## K. Known limitations completeness

**Verdict: THOROUGH, with one gap.**

The 9 limitations (L1-L9) are well-documented and properly severity-rated. However:

**Missing limitation:** The summary statistics in the runner (lines 683-691) are computed on the Main sample **before** complete-case filtering and MIN_CALLS_PER_FIRM filtering. This means the summary stats describe a broader sample than the regression sample. While this is standard practice, the audit doc does not mention this discrepancy. A replicator might be confused when the summary stats N exceeds the regression N.

---

## L. Design decisions -- are they honestly stated?

**Verdict: HONEST AND TRANSPARENT.**

The audit doc is commendably transparent about:
- The removal of clarity residuals (Decision 2) and the admission that pre-redesign clarity results were theoretically puzzling.
- The removal of 174-spec robustness grid (Decision 3) and the admission that prior H14 results were essentially null.
- The LINKPRIM inconsistency being characterized as an "incomplete fix" (Decision 4).
- The prior red-team finding that the only significant result (CEO_Pres, p=0.024) failed the placebo test (Section 11.6, L8).

This level of honesty is appropriate for a provenance document.

---

## M. Red-team disposition table (Section 13) -- completeness

**Verdict: THOROUGH.**

The first-layer audit addresses all 16 prior red-team findings (RT-1 through RT-8, G1 through G8, E1 through E4) with specific cross-references to where each is addressed. No prior findings appear to be dropped or ignored.

---

## N. What the first-layer audit missed

| ID | Finding | Severity | Evidence |
|----|---------|----------|----------|
| RT2-1 | **Compustat source path wrong in Section 4.** Table states `inputs/Compustat/Compustat.parquet` but code uses `inputs/comp_na_daily_all/comp_na_daily_all.parquet`. | Medium | `_compustat_engine.py` line 1249 vs. audit Section 4 |
| RT2-2 | **IBES source path inconsistent.** Section 4 says `inputs/IBES/IBES.parquet` but Section 6.5.4 correctly says `inputs/tr_ibes/tr_ibes_{YYYY}.parquet`. Internal contradiction. | Low | Audit Section 4 vs. Section 6.5.4 |
| RT2-3 | **Volatility window description internally contradictory.** Section 6.5.3 header says backward-looking `[prev_call_date + 5, current_call_date - 5]` but detailed chain and code show forward-looking `[start_date + 1, next_call_date - 5]`. | Medium | `_crsp_engine.py` lines 361-366 vs. audit Section 6.5.3 header |
| RT2-4 | **Calendar days vs. trading days.** Volatility window offsets use `pd.Timedelta(days=...)` (calendar days), not trading days. Audit header says "trading days" which is inaccurate. | Low | `_crsp_engine.py` lines 363-366 |
| RT2-5 | **Summary stats sample != regression sample.** Runner computes summary stats on Main-filtered sample before complete-case and MIN_CALLS_PER_FIRM filters. Not documented. | Low | Runner lines 667-691 |
| RT2-6 | **Attrition output has 4 stages, not 5.** Audit describes 5 conceptual stages but runner code produces 4-row attrition table (merging complete-case and min-calls). | Low | Runner lines 720-725 vs. audit Section 5.3 |

---

## O. Overall assessment

The first-layer audit is **high quality**. It demonstrates thorough code reading, honest disclosure of limitations, and transparent treatment of prior negative findings. The variable construction chains are detailed and, with the exceptions noted above, accurate.

The errors found are:
- **2 factual errors** (wrong Compustat path in Section 4, wrong Volatility window direction in Section 6.5.3 header)
- **2 internal contradictions** (IBES path between Section 4 and Section 6.5.4; Volatility window direction between header table and detailed chain)
- **2 minor documentation gaps** (summary stats sample scope; attrition stage count)

None of these errors would affect the reproducibility of the suite itself -- they are documentation-only issues. The code is correctly described in the detailed construction chains, which is where a careful replicator would look.

---

## P. Recommendations

1. **Fix Section 4 raw data paths.** Replace `inputs/Compustat/Compustat.parquet` with `inputs/comp_na_daily_all/comp_na_daily_all.parquet`. Replace `inputs/IBES/IBES.parquet` with `inputs/tr_ibes/tr_ibes_{YYYY}.parquet`.

2. **Fix Volatility window header.** Change Section 6.5.3 header from "[prev_call_date + 5 trading days, current_call_date - 5 trading days]" to "[current_call_date + 1 calendar day, next_call_date - 5 calendar days]".

3. **Add note about summary stats sample scope.** State that summary stats are computed on Main-filtered sample before complete-case filtering.

4. **Clarify attrition stage count.** Note that the runner output combines complete-case and MIN_CALLS_PER_FIRM into a single attrition stage.

5. **Run the suite.** L1 (no post-redesign results) remains the highest-severity issue. No amount of documentation improvement substitutes for an actual execution.
