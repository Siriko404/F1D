# Campello et al. 2022 JFQA — Brexit DiD Strict Replication Audit

**Project**: F1D thesis §III.E.4 endo-defense — Brexit DiD H1.5.brexit_did
**Source PDF**: `docs/papers/campello_etal_2022_brexit_jfqa.pdf` (793KB, 45 pages, j.3178–3222)
**Method**: Programmatic PyMuPDF read (PDF-first per locked rule) → NLM cross-verify when auth restored.
**Audit date**: 2026-05-13
**Audit target**: Cash DV (Table 8) — Y = cheq/(atq−cheq), per BKS net-assets style.
**Trigger**: Bug fixes (S4 $10M filter, S5 lag, S20 winsor) did NOT recover β^UK cash sign (still −0.0197 vs Campello +0.231***). User demands 100% replication, not 99%.

## How to use this file

Each "Step" = ONE verbatim Campello spec item. Three columns:
- **Spec** — verbatim quote + page anchor (PDF page // journal page).
- **F1D current** — what `run_h1_5_brexit_did.py` / `brexit_treatment_beta_uk.py` actually does (with file:line).
- **Match status** — STRICT MATCH / FIXABLE DEVIATION / DESIGN-LEVEL DEVIATION / UNKNOWN.

A non-MATCH on ANY step = candidate root cause for the sign flip.

---

## Phase 0 — Paper acquisition + scope

- ✅ PDF in repo, 45p, all text-extractable.
- ✅ Spec lock at `tmp/3did_replication_v2_2026_05_08.md` Section A lines 74–960.
- ✅ Prior NLM rounds: 4 Brexit (Q-A/B/C/D) + 1 Brexit-Q6 (`c87e7449`) — re-verify after re-auth.

---

## Phase 1 — PAPER EXTRACTION (verbatim)

> **Methodology**: Read each PDF page sequentially. For each spec-relevant claim, capture VERBATIM quote + PDF page (1-N) + journal page (j.XXXX). No paraphrasing in this section.

### 1.1 Sample universe

**VERBATIM p.3192 §IV.B (PDF p.15)**:
> "We use COMPUSTAT Quarterly to gather basic information on firm investment and financial data. We consider U.S. companies from the first calendar quarter of 2010 to the fourth quarter of 2016. We drop utility and financial firms, as well as companies whose market value or book assets are lower than $10 million. The sample used in our baseline investment tests consists of 41,630 observations (firm-quarters)."

- Universe = US Compustat Quarterly 2010Q1–2016Q4.
- **EXCLUSIONS**: utility + financial firms; firms with `mkvaltq < 10 OR atq < 10` ($M).
- Baseline N=41,630 firm-quarter obs (investment table). Cash table has different N (Table 8 — to capture next).

### 1.2 Treatment definitions

#### 1.2a β^UK (market-based)

**VERBATIM p.3191 eq (13)**:
> "vol(r_it) = α_i + β_i^UK · vol(FTSE100_t) + θ · CONTROLS_t + ε_it"
>
> "Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it). It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting). We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound. For each firm, we take the estimated value of β̂_i^UK from regression (13) as the empirical counterpart to β_i in our framework."

**Estimation window p.3193**:
> "We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events."

**Source p.3193**:
> "We use CRSP stock price data and **Bloomberg** equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13))."

**Treatment classification p.3193 §IV.C.1**:
> "We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms. Following our framework, in our base analysis, we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the **nonnegative range of the β_i^UK distribution**. For group contrasting, we do not include firms that benefit from uncertainty in the United Kingdom in the control group (firms with β_i^UK<0) as this could lead to overestimation biases attached to the treatment effects we seek to identify."
>
> "Under this market-based approach, a total of **449 unique firms** are assigned to the treated category (β^UK > 0.68). In contrast, **360 unique firms** are assigned to the control category (β^UK < 0.28)."

- Estimation: monthly std-dev of daily log-returns over 60 months 2010M1-2014M12 per firm; OLS eq (13) with vol(SP500) + vol(FX£) as controls.
- Drop firms with β^UK < 0 (NOT just middle tercile — drop NEGATIVES too).
- Tercile cuts on **nonneg distribution**: HIGH at β > 0.68, LOW at β < 0.28.
- Treated N=449, Control N=360 (these are unique-firm counts in Campello universe).

#### 1.2b 10-K keyword count

**VERBATIM p.3191 §IV.A.2 + fn 14**:
> "We develop a textual-search-based metric that is constructed by parsing firms' 2015 10-K filings. In particular, we look for the number of entries of keywords related to uncertainty about Brexit ('Brexit', 'Great Britain', and 'Uncertainty') in firms' disclosures, classifying firms with a 'high' number of entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control firms."
>
> "fn 14: Entries like 'Referendum', 'Uncertain', 'United Kingdom', 'UK', 'U.K.', and 'G.B.' are subsumed by the above wording."

**Cutoff p.3192**:
> "Brexit cites at more than 5 entries. There are 807 firms citing Brexit more than 5 times in their 10-Ks. On the other hand, 433 do not cite any Brexit-related terms in their public filings."

- 9 keywords total (3 primary + 6 subsumed).
- HIGH_10K = 1 if total_count > 5; CONTROL_10K = 1 if total_count == 0; intermediate (1-5) excluded.
- Treated N=807, Control N=433.

### 1.3 Cash dependent variable

**VERBATIM Table 8 caption** (PDF p.31, j.3208):
> "TABLE 8. The Impact of the Brexit Vote on Cash Holdings, Noncash Working Capital, and Profitability. Table 8 reports output from equation (14). The dependent variables are CASH, NON_CASH_WORKING_CAPITAL, and PROFITS. **CASH is defined as total cash holdings divided by lagged total assets net of cash holdings.** NON_CASH_WORKING_CAPITAL (NWC) is defined as working capital (net of cash) divided by lagged total assets. PROFITS is defined as the quarterly percentage change in profits (operating income before depreciation divided by sales)."
>
> "The time dimension of the DID estimator is set so as to compare the two quarters following the announcement of the vote (2016:Q3–Q4) versus the two quarters preceding the announcement of the vote date (2015:Q3–Q4). T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels."

- **DV CASH = cheq_t / (atq_{t−1} − cheq_{t−1})** — BKS net-of-cash assets denominator. F1D current matches.
- **Window in regression**: 2015Q3+Q4 (POST=0) vs 2016Q3+Q4 (POST=1) per firm.

**⚠️ Note Table 1 summary-stats uses DIFFERENT cash def** (verbatim p.3198 caption):
> "CASH is defined as **cash and short-term investments divided by lagged total assets**."
That's CHE/lag(AT). NOT used in regression — only summary. Regression uses Table 8 BKS form.

### 1.4 Control variables (5 macro + 6 firm)

**VERBATIM p.3197 §IV.C.3** (post-eq-14):
> "CONTROLS_{i,t−1} is a vector of macroeconomic and firm-level control variables. Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingston Survey, the lagged Consumer Sentiment Index from the University of Michigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia. Firm-level controls include lagged stock returns, Tobin's Q, cash flow, logged assets, and sales growth. As an additional control for first-moment effects of Brexit, we add 1-quarter-ahead consensus earnings forecasts to our model."

- **5 MACROS (all 1Q-lagged)**: USD/GBP FX, VIX, Livingston GDP-1Y-fcst (biannual→quarterly fwd-fill), UMCSENT, **Philly Fed LEI** (F1D uses ADS substitute — known deviation; Philly has no LEI series per memory).
- **6 FIRM CONTROLS (all 1Q-lagged)**: stock_returns, Tobin's Q, cash_flow, logged_assets, sales_growth, **consensus_EPS_1Q-ahead** (the "first-moment" control).

### 1.5 Fixed effects

**VERBATIM p.3197**:
> "FIRM_i represents firm-fixed effects, INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100), and QUARTER_t are calendar-quarter dummies."

- FE structure = **firm + industry(FIC100) × quarter**.
- Industry classification: Hoberg-Phillips FIC100 (NOT SIC, NOT FF12/FF48).

### 1.6 Standard errors (clustering)

**VERBATIM p.3197**:
> "Standard errors are double-clustered by firm and calendar quarters."

- 2-way cluster: firm + calendar quarter. Strictly two-way.

### 1.7 Window + POST definition — 🚨 SMOKING GUN

**VERBATIM p.3196 §IV.C.3 + eq (14)**:
> "We compare differences in outcomes of interest between treated (HIGH_UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms. **Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects.** This is equivalent to estimating the following model:"
>
> "(14) Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θ·CONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ε_{i,t}"
>
> "**POST_t equals 1 if the time period is in the 2016:Q3–Q4 window.**"

🚨 **CRITICAL DEVIATION CANDIDATE**: This is **NOT** a full-panel DiD with POST=1{cal_yr_qtr ≥ 2016Q3}. It is a **2×2 tight-window DiD**:
- **Pre-period**: 2015:Q3 + 2015:Q4 (POST=0)
- **Post-period**: 2016:Q3 + 2016:Q4 (POST=1)
- **All other quarters (2010Q1–2015Q2, 2016Q1–2016Q2): EXCLUDED**

So per firm, max 4 observations (one per quarter × 4 quarters). Campello N=41,630 firm-quarters / 4 ≈ 10,408 firms in baseline (matches "449 + 360 + ..." across full universe ~10K firms).

**F1D current** (`run_h1_5_brexit_did.py:WINDOW_START_YQ=20101, WINDOW_END_YQ=20164` then full inclusive panel + POST=1{cal_yr_qtr ≥ 20163}) uses **28 quarters per firm** → ~7× more observations → completely different sample composition → firm FE absorbs years of within-firm time variation that Campello's 4-quarter design never sees.

### 1.8 Industry / utility-financial exclusion

**VERBATIM p.3192 §IV.B**:
> "We drop utility and financial firms…"

- F1D current = drop FF12 ∈ {8 Util, 11 Fin}. Campello does not specify SIC ranges in main text — likely SIC 4900-4999 + 6000-6999 (common convention).

### 1.9 Winsorization

(to capture from p.3197+ or Online Appendix — likely 1% both tails within calendar quarter)

### 1.10 $10M filter

Captured in §1.1 above: `mkvaltq < 10 OR atq < 10` ($M) → DROP.

### 1.11 Robustness ladder (PSM, parallel trends, Cameron, Debt-Ceiling, Trump-excl)

(to fill — pages 26-45 + Online Appendix)

---

## Phase 2 — IMPLEMENTATION AUDIT (strict)

Per spec item: F1D current code vs Phase-1 verbatim. STRICT MATCH or NOT.

(to fill after Phase 1 complete)

---

## Phase 3 — DEVIATION LIST (root-cause ranking)

Likely root cause for β^UK sign flip ordered by suspected magnitude.

(to fill)

---

## Phase 4 — FIX PLAN

ONE fix per hypothesis. Test after each. NO BUNDLED FIXES (per /systematic-debugging Iron Law).

(to fill)
