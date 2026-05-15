# Campello 2022 JFQA Brexit DiD — F1D Implementation Audit

**Phase 2 of strict replication audit.** Each item compares Phase-1 verbatim Campello spec (`tmp/campello_brexit_verbatim_step_by_step_2026_05_14.md`) against the F1D code at `src/f1d/`. Verdict ladder:

- **STRICT MATCH** — F1D follows Campello formula verbatim, no deviation.
- **FIXABLE** — clear deviation, simple code fix recoverable.
- **DESIGN** — design-level deviation that requires methodological re-thinking, not a one-line code change.
- **UNKNOWN** — Campello underspecifies; F1D's choice may or may not match.

Per `/systematic-debugging` Iron Law: **NO fixes proposed in this file**. Diagnostic catalog only.

---

## §1. Sample universe

| Item | Campello (Phase 1 §1) | F1D code | Verdict |
|---|---|---|---|
| Frequency | Compustat **Quarterly** Fundamentals | `comp_na_daily_all.parquet` quarterly fields | MATCH |
| Window | 2010Q1 – 2016Q4 | `WINDOW_START_YQ=20101 .. WINDOW_END_YQ=20164` (`run_h1_5_brexit_did.py:122-123`) | MATCH |
| Util+fin drop | "drop utility and financial firms" | `panel[~panel["ff12_code"].isin([8, 11])]` (`run_h1_5_brexit_did.py:283`) | MATCH (FF12 8 Util + 11 Fin ≈ SIC 4900-4999 + 6000-6999) |
| $10M filter | "drop … companies whose market value or book assets are lower than $10 million" | `(mkvaltq >= 10) & (atq >= 10)` AND-keep (`run_h1_5_brexit_did.py:326`) | MATCH |
| **Universe** | **Universe of Compustat-listed firms** matching above filters (Campello reports 41,630 firm-quarters; 449 treated + 360 control unique firms under β^UK; 807 treated + 433 control under 10-K) | **Earnings-call-panel firms only** — `panel = pd.read_parquet(h1_cash_holdings_panel.parquet)` (`run_h1_5_brexit_did.py:153-167`), inherits the F1D **call-panel restriction** of firms with quarterly earnings-call transcripts | **DESIGN — STRUCTURAL UNIVERSE DEVIATION** |

> The single biggest deviation: F1D analyzes the **subset** of Compustat firms with quarterly conference-call transcripts in the F1D speech corpus. Campello analyzes **all** Compustat firms (excluding util/fin, ≥$10M). F1D's call-panel selects toward larger, more sophisticated, S&P 500-tilted firms — excluding private, IPO-recent, distressed, and small-cap firms. Sample size reduction ≈ 10× (Campello cash N=17,170; F1D cash baseline N drops to single-thousands range per recent runs). This **selection effect alone** is sufficient to flip the cash coefficient sign and kill statistical power — the precautionary-cash response Campello documents is driven by smaller, capital-constrained UK-exposed firms that the F1D call-panel systematically drops.

---

## §2. Treatment β^UK (market-based)

### §2.1. Equation form

| Item | Campello (Phase 1 §2.1) | F1D code | Verdict |
|---|---|---|---|
| Regression eq (13) | `vol(r_it) = α_i + β_i^UK · vol(FTSE100_t) + θ · {vol(SP500_t), vol(FX£_t)} + ε_it` | `_vectorized_ols`, design matrix `[1, vol_ftse, vol_sp500, vol_fx]` (`brexit_treatment_beta_uk.py:386-394`) | MATCH |
| Window | 2010M1 – 2014M12 monthly (60 obs) | `BETA_UK_START="2010-01-01" .. BETA_UK_END="2014-12-31"; N_MONTHS_FULL=60` (`brexit_treatment_beta_uk.py:62-66`) | MATCH |
| vol(r_it) data | CRSP equity returns | CRSP DSF `RET` field, monthly std of daily log-returns (`brexit_treatment_beta_uk.py:221-261`) | MATCH |
| vol(FTSE100) data | Bloomberg | **yfinance daily ^FTSE close** (`brexit_treatment_beta_uk.py:114-122`) | UNKNOWN — same index, different vendor; minor data deviation; minor numerical impact expected |
| vol(SP500) data | (implicit S&P 500 daily) | CRSP DSF `sprtrn` field (S&P 500 simple daily return) → `log1p` → monthly std (`brexit_treatment_beta_uk.py:138-155`) | MATCH (CRSP sprtrn is the S&P 500 daily index return) |
| vol(FX£) data | (implicit USD/GBP daily) | BoE `USD_GBP_daily_2008-2018.csv` field `XUDLUSS` (`brexit_treatment_beta_uk.py:124-135`) | MATCH |
| Realized-vol convention | "volatility of equity returns" | monthly std of daily log-returns (`_monthly_std` → `vol_r`) | MATCH (academic standard) |
| **MIN_DAYS_PER_MONTH = 15** | Not specified | `brexit_treatment_beta_uk.py:71` (drops firm-months with <15 trading days) | UNKNOWN — judgment call; potentially excludes thinly-traded firms |
| **Drop firms with any missing month** | Not specified | `complete = wide.dropna(how="any")` (`brexit_treatment_beta_uk.py:383`) | UNKNOWN — strict; Campello may keep firms with partial coverage |
| Inference SE | Not used downstream | Classical homoskedastic OLS SE (`brexit_treatment_beta_uk.py:299`) | MATCH (treatment dummy reads point estimate only) |

### §2.2. Tercile classification

| Item | Campello (Phase 1 §2.4) | F1D code | Verdict |
|---|---|---|---|
| β^UK ≥ 0 only | "we do not include firms that benefit from uncertainty (β^UK < 0)" | `nonneg = beta_uk[beta_uk >= 0]` (`brexit_treatment_beta_uk.py:320`) | MATCH |
| Top tercile cut | β^UK > **0.68** (449 firms) | `p67 = 0.68` (`brexit_treatment_beta_uk.py:328`) | MATCH (Campello-absolute, locked 2026-05-13) |
| Bottom tercile cut | β^UK < **0.28** (360 firms) | `p33 = 0.28` (`brexit_treatment_beta_uk.py:327`) | MATCH |
| Middle tercile | Dropped | `high[(beta_uk ≥ 0) & (≤p33)]=0; [(beta_uk ≥ 0) & (≥p67)]=1; else NaN` (`brexit_treatment_beta_uk.py:343-346`) | MATCH (mid + negs left NaN; runner drops NaN) |
| **Realized treated N** | Campello: 449 firms | F1D realized: previously logged as "≈50-150 treated firms" due to call-panel + β^UK shift (per memory `feedback_endo_defense_final_hierarchy.md`) | **DESIGN — POWER PROBLEM** |

> Cuts are Campello-verbatim, but the **F1D β^UK distribution is shifted left of Campello's** (F1D-relative tercile quantiles 0.20/0.53 per memory vs Campello-absolute 0.28/0.68). Reason: F1D call-panel firms are larger, more diversified, and have lower realized β^UK on average. Applying Campello-absolute cuts on a left-shifted F1D distribution → most F1D firms classified as control (β<0.28), tiny treated group (β>0.68). Statistical power collapses; sign sensitivity rises.

---

## §3. Treatment HIGH_10K (textual)

| Item | Campello (Phase 1 §2.3) | F1D code | Verdict |
|---|---|---|---|
| Source | 2015 10-K filings | parsed via `scripts/brexit/parse_10k_keywords.py` cache (`brexit_treatment_10k.py:65-95`) | MATCH (corpus = SRAF Notre Dame 10-K archive 2015) |
| Keywords (3 primary) | "Brexit", "Great Britain", "Uncertainty" | (9 keywords combined — primary + 6 subsumed per Campello fn 14) | MATCH (text count level) |
| Keywords (6 subsumed) | "Referendum", "Uncertain", "United Kingdom", "UK", "U.K.", "G.B." | F1D 9-keyword tally (per builder docstring lines 14-31) | MATCH (text count level) |
| Cutoff HIGH | total_count > 5 | `total_count > HIGH_THRESHOLD=5` (`brexit_treatment_10k.py:61, 72`) | MATCH |
| Cutoff CONTROL | total_count == 0 | `total_count == ZERO_THRESHOLD=0` (`brexit_treatment_10k.py:62, 73`) | MATCH |
| Mid (1-5) | Excluded | NaN, runner drops | MATCH |
| **Realized HIGH N** | Campello: 807 firms | F1D: **2,847 firms** (3.5× over-count; builder doc lines 14-23) | **DESIGN — KEYWORD-MATCHING MECHANISM DIFFERS** |
| **Realized CONTROL N** | Campello: 433 firms | F1D: **261 firms** (0.6× under-count) | **DESIGN — same root cause** |

> Builder doc localizes the gap: dropping "uncertainty" + "uncertain" from the tally drops F1D HIGH from 2,847 to 994 (close to Campello 807). Suggests Campello's "uncertainty" matching had an undisclosed proximity constraint to UK/Brexit terms, OR an Item-scope restriction to risk-factors sections only. F1D's verbatim pure-9-keyword tally over-includes general "uncertainty" mentions unrelated to UK exposure.

---

## §4. DiD design (POST_t + sample)

| Item | Campello (Phase 1 §3) | F1D code | Verdict |
|---|---|---|---|
| Model eq (14) | `Y = α + δ·[POST × HIGH] + θ·CONTROLS_{t-1} + FIRM_i + Σ INDUSTRY_j × QUARTER_t + ε` | `exog_full = [treatment, level_dummy] + macros + firm_lag1 + EPS_lag1 + Post_brexit` + `entity_effects=True, other_effects=fic100_qtr_id, drop_absorbed=True` (`run_h1_5_brexit_did.py:422-437`) | MATCH (structurally identical) |
| POST_t | =1 iff cal_yr_qtr ∈ {2016Q3, 2016Q4} | `(cal_yr_qtr >= POST_START_YQ=20163).astype(int)` (`run_h1_5_brexit_did.py:124, 336`) | MATCH |
| Sample frame | Full 2010Q1-2016Q4 panel of treated+control firms; Table 8 col 1 N=17,170 firm-qtr obs (449+360 unique firms × ≤28 quarters with attrition) | Full 2010Q1-2016Q4 panel of call-panel firms × treatment-non-NaN (`run_h1_5_brexit_did.py:282, 401-410`) | MATCH on time dimension; **mis-match on cross-section** (see §1 above) |

> Earlier in this audit cycle (prior turn) the "4-quarter sample restriction" hypothesis was raised based on Table 8 caption phrasing. **Refuted by N evidence**: Table 2 col 2 N=17,199 and Table 12 Cameron-placebo (2015:Q3 vs 2014:Q3) also N=17,199. Same sample, different POST_t. Sample = full panel; "compare X vs Y" is rhetorical DID description, not literal sample restriction. F1D matches.

---

## §5. Dependent variable (cash regression)

| Item | Campello Table 8 caption (Phase 1 §5) | F1D code | Verdict |
|---|---|---|---|
| Cash DV formula | "total cash holdings divided by **lagged total assets net of cash holdings**" → `cheq_t / (atq_{t-1} − cheq_{t-1})` | `cell["denom"] = cell["atq_lag1"] - cell["cheq_lag1"]; cell["cash_brexit_dv"] = cell["cheq"] / cell["denom"]` (`run_h1_5_brexit_did.py:316-318`) | MATCH |
| Denominator filter | (implicit denom > 0) | `cell = cell[cell["denom"] > 0]` (`run_h1_5_brexit_did.py:317`) | MATCH |
| Lag mechanism | Calendar previous quarter | **Calendar-prev-qtr merge** via `prev_qtr_id` (`run_h1_5_brexit_did.py:306-315`) — correctly handles firms with missing quarters | MATCH (bug fix 2026-05-13: previously row-order `shift(1)`) |

---

## §6. Control variables (5 macro + 6 firm)

### §6.1. Macro controls (5)

| Campello (Phase 1 §4) | F1D code | Verdict |
|---|---|---|
| Lagged USD/GBP FX rate | `usd_gbp_lag1` ← BoE XUDLUSS daily → quarterly mean → 1Q-lag (`brexit_macro_controls.py:84-93`) | MATCH |
| Lagged VIX implied vol | `vix_lag1` ← CBOE VIX daily close → quarterly mean → 1Q-lag (`brexit_macro_controls.py:96-105`) | MATCH |
| Lagged Livingstone Survey 1Y-ahead GDP growth forecast | `gdp_fcst_1y_lag1` ← Philly Fed Livingston RGDPX_1Y biannual → fwd-fill to quarterly → 1Q-lag (`brexit_macro_controls.py:108-128`) | MATCH |
| Lagged UMich Consumer Sentiment | `umcsent_lag1` ← UMich UMCSENT monthly → quarterly mean → 1Q-lag (`brexit_macro_controls.py:131-140`) | MATCH |
| **Lagged Philly Fed Leading Economic Indicator** | `ads_lag1` ← Philly Fed **ADS Index** daily → quarterly mean → 1Q-lag (`brexit_macro_controls.py:143-153`) | **DESIGN — SUBSTITUTION** |

> Builder doc admits: "Philly Fed has no national LEI series → substitute ADS (document in builder)" (`brexit_macro_controls.py:11-14`). ADS (Aruoba-Diebold-Scotti business conditions index) ≠ LEI (Leading Economic Indicator). Different statistical properties: ADS is a contemporaneous business-conditions index from a Kalman-filter model; LEI is a forward-looking composite (Conference Board uses 10 components incl. yield curve, building permits, jobless claims). Campello's "Philly Fed LEI" most likely refers to **Philly Fed Aggregated State Leading Indexes** (50 state LIs averaged — Philly does publish this). F1D's ADS substitution is a real macro-signal deviation, not equivalent.

### §6.2. Firm controls (6, all 1Q-lagged)

| Campello Table 1 + eq (14) verbatim | F1D code | Verdict |
|---|---|---|
| Stock returns: "quarterly buy-and-hold return" | `(prccq_t/ajexq_t)/(prccq_{t-1}/ajexq_{t-1}) − 1` (`brexit_stock_return.py:81`) | **FIXABLE — MISSING DIVIDENDS** |
| Tobin's Q: "MV equity + BV assets − BV equity + deferred tax, divided by BV assets" → `(cshoq*prccq + atq − ceqq + txditcq) / atq` | `(atq + cshoq*prccq) / atq` (`brexit_tobins_q.py:72`) | **FIXABLE — MISSING −ceqq + txditcq** |
| Cash flow: "operating income before depreciation / lagged total assets" → `oibdpq_t / atq_{t-1}` | `oibdpq_t / atq_{t-1}` (`brexit_cash_flow.py:71`) | MATCH |
| Logged assets: "logarithm of total assets" | `np.log(atq.clip(lower=1.0))` (`run_h1_5_brexit_did.py:350`) | MATCH (clip floor at 1.0 is defensive) |
| Sales growth: "year-on-year percentage change in quarterly sales" | `(saleq_t − saleq_{t-4}) / |saleq_{t-4}|` (`brexit_sales_growth.py:75-77`) | **FIXABLE — `|saleq|` denominator non-standard (Campello would use signed `saleq_{t-4}`)** + **FIXABLE — `shift(4)` row-order lag, not calendar-aware** |
| Consensus EPS: "standardized mean 1-quarter ahead EPS forecast" | IBES FPI=6 → mean per (gvkey, fpedats) → **within-firm z-score over 2000-2025** (`brexit_consensus_eps.py:98-109`) | **DESIGN — STANDARDIZATION FRAME** |
| 1Q-lag mechanism | All 6 firm controls: `cell.groupby("gvkey").shift(1)` row-order (`run_h1_5_brexit_did.py:354-360`) | **FIXABLE — ROW-ORDER LAG BUG** |

> **Tobin's Q deviation**: F1D's `(AT + MV_eq) / AT = 1 + MV_eq/AT` is not Tobin's Q — it's "1 + Market-to-Book of total assets". Missing two Campello terms: `−ceqq` (subtract book equity) and `+txditcq` (add deferred taxes). Builder docstring (lines 7-11) admits the deviation but justifies it with "(per audit MAJOR-3 + Sina decision)" — that justification is stale and inconsistent with the Phase-1 verbatim Table 1 caption.
>
> **Stock return deviation**: Campello's "buy-and-hold return" academic standard includes **dividends**. F1D uses Compustat `prccq/ajexq` (capital gains only). To match Campello you'd compound CRSP daily `RET` (which includes dividends) over the calendar quarter.
>
> **Sales growth deviation**: `|saleq_{t-4}|` denominator handles negative sales unconventionally — a firm with saleq going from −10 to +20 gets `(+20−(−10))/|−10|=+3.0` instead of the signed `−3.0`. Most published replications use signed denominator. Also `shift(4)` on (gvkey, cal_yr_qtr)-sorted dataframe is **wrong** for unbalanced panels with missing quarters — the builder doc admits this (line 73-75).
>
> **Consensus EPS deviation**: Campello's "standardized" most naturally means **cross-sectional standardization at time t** (across all firms in period t, the standardized analyst forecast); F1D does **within-firm time-series z-score over 2000-2025**. These are different normalizations — F1D's removes firm-level mean (similar to absorbing firm FE), Campello's likely retains firm cross-section.
>
> **Row-order shift bug**: lines 354-360 use `groupby("gvkey").shift(1)` for firm-control 1Q-lag. Same bug pattern as the Lagged_DV bug fixed elsewhere — if firm has missing 2014Q3, the 2014Q4 row's `shift(1)` returns 2014Q2 value (wrong) instead of NaN. The DV calculation uses the correct calendar-prev-qtr merge (line 306-315) but the firm controls do not. Inconsistent within the same runner.

---

## §7. Fixed effects

| Item | Campello (Phase 1 §4 + Table 8 caption) | F1D code | Verdict |
|---|---|---|---|
| Firm FE | `FIRM_i` | `entity_effects=True` (`run_h1_5_brexit_did.py:432`) | MATCH |
| Industry × Quarter FE | "INDUSTRY_j × QUARTER_t … Hoberg and Phillips (2016) classification (FIC 100)" | `other_effects=df_fe["fic100_qtr_id"]` where `fic100_qtr_id = fic100_industry_id + "_" + cal_yr_qtr` (`run_h1_5_brexit_did.py:370-372, 434`) | MATCH (manual string-concat interaction passed via `other_effects`) |
| FIC100 source | Hoberg-Phillips data library | F1D `hoberg_phillips_fic100` builder | MATCH (data-source assumed correct, not re-audited here) |
| `drop_absorbed=True` | (implicit; necessary for time-invariant level dummies under firm FE) | `drop_absorbed=True, check_rank=False` (`run_h1_5_brexit_did.py:435-436`) | MATCH (HIGH and POST are absorbed by firm + FIC100×Qtr FE; drop_absorbed handles) |

---

## §8. Standard errors

| Item | Campello (Phase 1 §4 + Table 8 caption) | F1D code | Verdict |
|---|---|---|---|
| Two-way cluster | "double-clustered by firm and calendar quarters" | `cov_type="clustered", cluster_entity=True, cluster_time=True` (`run_h1_5_brexit_did.py:146, 416-420`) | MATCH |

---

## §9. Winsorization

| Item | Campello (Phase 1 §5 Table 1 caption) | F1D code | Verdict |
|---|---|---|---|
| Level | "winsorized at the 1% level" | `WINSOR_PCT = 0.01` (`run_h1_5_brexit_did.py:130` + all builders) | MATCH on level |
| **Scope** | "All variables are winsorized at the 1% level" — pooled scope (Campello does not say within-quarter) | F1D winsorizes **within cal_yr_qtr** at builder time + at panel-assembly time on newly-created vars (`run_h1_5_brexit_did.py:380-385`; `brexit_tobins_q.py:40-48`; same pattern in all builders) | **UNKNOWN — DEVIATION on scope** |

> Campello's exact winsorization scope is underspecified; many published replications use pooled-panel winsorization (one 1% cut over the full 2010Q1-2016Q4 sample), while F1D uses per-quarter winsorization (one 1% cut within each cal_yr_qtr). Within-quarter is more conservative (less data clipped) and produces a different control distribution.

---

## §10. Regression mechanics (extraction)

| Item | Campello | F1D code | Verdict |
|---|---|---|---|
| One-tailed p-value direction | Tail not specified per coefficient; reported as 2-tailed t | F1D reports `p_one = p_two/2 if beta>=0 else 1−p_two/2` (`run_h1_5_brexit_did.py:493-494`) | MATCH on construction; tail direction = positive per F1D thesis convention |
| Coefficient table emission | LaTeX Table 8 | `_emit_canonical_suite_spec` + `write_suite_spec` (`run_h1_5_brexit_did.py:598-746`) | MATCH (downstream rendering) |

---

## §11. Robustness ladder (Phase 1 §7)

| Robustness item | Campello | F1D code | Verdict |
|---|---|---|---|
| PSM matched sample (Table C2/C3) | Reported on PSM-balanced subsample | `brexit_psm_matching.py` builder exists (not in baseline 4-cell runner) | NOT INTEGRATED — separate runner needed |
| Parallel trends (Table C4/C5) | Formal pre-trend tests | `brexit_parallel_trends.py` builder exists (not in baseline) | NOT INTEGRATED |
| Trump exclusion (Table 12 col 1-2) | Compare 2016:Q3 vs 2015:Q3 only | Not in baseline runner | NOT INTEGRATED |
| Trump-loser exclusion (Table 12 col 3-4) | Drop Wagner et al. (2018) losers | Not in baseline runner | NOT INTEGRATED |
| Cameron placebo (Table 12 col 5-6) | POST=2015:Q3 vs 2014:Q3 | Not in baseline runner | NOT INTEGRATED |
| Debt-Ceiling placebo (Table 12 col 7-8) | POST=2011:Q2-Q4 vs 2010:Q2-Q4 | Not in baseline runner | NOT INTEGRATED |
| FX hedging controls (Table 9) | 4 alternative FX-exposure controls | Not in baseline runner | NOT INTEGRATED |
| Other-country falsification (Table 13) | Replace β^UK with β^EU/CN/MX/JP/IN/BR | Not in baseline runner | NOT INTEGRATED |
| Financing-constraints controls (Table 10) | Bond yields + loan spreads + discount-rate news | Not in baseline runner | NOT INTEGRATED |
| Automation channel (Table 11) | Acemoglu-Restrepo automation index | Not in baseline runner | NOT INTEGRATED |
| Irreversibility moderator (Table 7) | Kim-Kung index + unionization | Not in baseline runner | NOT INTEGRATED |

> Per memory, irreversibility/PSM/parallel-trends modules exist in F1D builder folder but are not wired into the baseline 4-cell H1.5.brexit_did runner. Out-of-scope for the cash-sign-flip diagnosis but documented for completeness.

---

## §12. Deviation summary table (ranked by suspected magnitude on cash β sign flip)

| # | Item | Severity | Suspected effect on cash β |
|---|---|---|---|
| 1 | **Universe = earnings-call panel, not Compustat** (§1) | **DESIGN — STRUCTURAL** | **High**: drops the precautionary-cash-active small/mid-cap UK-exposed firms that drive Campello's +0.231***. F1D analyzes the wrong population for this effect. |
| 2 | **β^UK distribution shifted left + Campello-absolute cuts** (§2.2) | **DESIGN — STATISTICAL POWER** | **High**: tiny treated group (likely 50-150 firms); high standard errors; sign sensitivity to a handful of outliers. |
| 3 | **Tobin's Q formula missing −ceqq + txditcq** (§6.2) | **FIXABLE** | **Medium**: bias in lagged Tobin's Q control; if cash is correlated with Q via M/B, mis-specified control leaks into the treatment coef. |
| 4 | **10-K HIGH count 3.5× Campello** (§3) | **DESIGN — KEYWORD MATCHING** | **Medium**: affects only the 10-K column, not the β^UK column. But 10-K column = primary text-based check; over-counting "uncertainty" mentions floods treatment with non-UK-exposed firms. |
| 5 | **LEI substituted with ADS** (§6.1) | **DESIGN — MACRO SIGNAL** | **Low-Medium**: different macro control; affects coefficient on the macro control but only indirectly affects POST×HIGH via collinearity. |
| 6 | **Stock return missing dividends** (§6.2) | **FIXABLE** | **Low**: capital-gains-only return is a noisier proxy; effect on control coefficient, indirect on treatment. |
| 7 | **Sales growth uses `|saleq_{t-4}|` denominator + `shift(4)` row-order** (§6.2) | **FIXABLE** | **Low**: rare cases of negative saleq + rare missing-quarter pattern. |
| 8 | **Consensus EPS within-firm z-score over 2000-2025** (§6.2) | **DESIGN — STANDARDIZATION** | **Low**: different normalization; firm FE partially absorbs within-firm centering anyway. |
| 9 | **Firm controls `groupby.shift(1)` row-order lag** (§6.2) | **FIXABLE** | **Low-Medium**: depends on quarter-gap frequency in call panel; if gaps are rare, lag is mostly correct. |
| 10 | **Winsor within cal_yr_qtr vs pooled** (§9) | **UNKNOWN** | **Low**: less data clipped; small effect on extreme observations. |
| 11 | **β^UK `MIN_DAYS_PER_MONTH=15` + drop firms with any missing month** (§2.1) | **UNKNOWN** | **Low**: excludes thinly-traded firms from β^UK estimation; sample composition. |
| 12 | **vol(FTSE100) from yfinance, not Bloomberg** (§2.1) | **UNKNOWN** | **Trivial**: same index, different vendor; numerical differences negligible. |

---

## §13. Verdict on "are we 100% replicating Campello?"

**No.** Phase 1 verbatim spec is the target. F1D current implementation **MATCHES Campello strictly** on:
- Sample window 2010Q1-2016Q4
- $10M filter + util/fin exclusion
- DV formula `cheq_t/(atq_{t-1}−cheq_{t-1})` (Table 8)
- Cash flow control formula `oibdpq/atq_{t-1}`
- Log assets
- β^UK estimation equation + window + tercile cuts (Campello-absolute 0.28/0.68)
- 10-K cutoff thresholds (>5 / =0)
- POST_t = 2016Q3-Q4 indicator
- Firm FE + FIC100 × Quarter FE structure
- Double-cluster firm + cal_yr_qtr SE
- Winsorization at 1% level

F1D **DEVIATES from Campello** on:
- Universe (call-panel subset, not Compustat universe) ← **STRUCTURAL**
- Tobin's Q formula (missing two terms) ← **FIXABLE**
- 10-K keyword tally (over-counts "uncertainty") ← **DESIGN**
- LEI macro substituted with ADS ← **DESIGN**
- Stock return (price-only, no dividends) ← **FIXABLE**
- Sales growth denominator + lag mechanism ← **FIXABLE**
- Consensus EPS standardization frame ← **DESIGN**
- Firm controls 1Q-lag via row-order `shift(1)` ← **FIXABLE**
- Winsorization scope within-quarter vs pooled ← **UNKNOWN**
- vol(FTSE100) source (yfinance vs Bloomberg) ← **UNKNOWN**
- β^UK firm-month coverage rules ← **UNKNOWN**

**11 deviations total**: 4 FIXABLE, 4 DESIGN, 3 UNKNOWN, 0 STRICT-FAIL-NO-RECOVERY.

The **#1 deviation (call-panel universe)** is the bridge between F1D and Campello that cannot be closed by code fixes alone — F1D's thesis question is about CEO-speech firms, which is a different population than Campello's broader U.S. corporate-America firms. Any "100% replication" requires either:
1. Rebuild a full-Compustat baseline runner without the call-panel filter (proves the replication works on Campello's population, then separately study the speech subsample as an extension), OR
2. Explicitly document the call-panel restriction as a scope-narrowing of Campello, accept that the cash β estimate is conditional on this subsample, and demonstrate that the SIGN remains positive on the broader Compustat sample (cross-check).

The **#2 deviation (β^UK distribution shift)** compounds #1: even if you broaden the sample to full Compustat, the F1D F2D estimation pipeline produces a left-shifted β^UK distribution relative to Campello's 1240+ firms; Campello-absolute cuts will produce a thin treated group. May need to use F1D-relative tercile cuts as the "Campello-method-on-F1D-data" baseline, then validate with Campello-absolute cuts as a sensitivity.

---

## §14. Recommendation (per /systematic-debugging: hypothesize, then test ONE thing at a time)

Per **Iron Law** — do not bundle fixes. Test the universe deviation first since it dominates the others. Order:

1. **First**: build a Compustat-universe parallel runner (drop call-panel restriction). Compare cash β to Campello's +0.231***. If matches → confirms universe was the deviation; if still flips → eliminates universe as the cause.
2. **Second** (if #1 matches): re-introduce call-panel restriction → confirm the sign flip is a population effect (legitimate scientific finding, not a bug).
3. **Third** (if #1 still flips): fix Tobin's Q formula (highest-priority FIXABLE) → re-run.
4. **Fourth** (if #1 + #3 still flip): fix stock return (add dividends) + sales growth + EPS standardization + LEI source one at a time.
5. **Fifth** (if all fixed and still flips): the call-panel result is a robust population-level finding that contradicts Campello — DOCUMENT as such, not a bug.

Speech DV integration **remains blocked** until at least step 1 or step 2 produces a Campello-matching cash sign, per user's instruction.

---

**END Phase 2 audit. NO CODE FIXED. Diagnostic only.**
