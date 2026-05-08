# 3-DiD Replication Spec v2 — PDF-first, human-vetted NLM

**Started 2026-05-08 PM-late+1h after spec-reset decision.**
Trust hierarchy: peer-reviewed PDF text > NLM Q+A > orchestrator paraphrase. Per-paper sequential build. PDF read first; NLM queries emitted to Sina (NOT MCP) for verification; spec section locked only after PDF + NLM agree.

## Why this exists
Predecessor `tmp/3did_replication_instructions_2026_05_08_DEPRECATED.md` had ~60% accuracy on top-15 corrections per orchestrator's Round-5 PDF audit. Reset path: rebuild from PDF primacy with human-driven NLM verify (bypasses MCP-paraphrase risk).

## Workflow per chunk

```
   READ PDF chunk (≤15 pages)
        │
        ▼
   DRAFT spec section verbatim quotes + page tags
        │
        ▼
   EMIT NLM queries to Sina (numbered, copy-paste ready)
        │
        ▼
   SINA runs in NotebookLM browser → returns response
        │
        ▼
   RECONCILE NLM ↔ PDF (PDF wins per trust hierarchy)
        │
        ▼
   LOCK section, advance to next chunk
```

## ⚠️ NLM page-citation calibration (programmatic verify, 2026-05-08 PM-late+2h)

**PDF→journal page mapping (programmatic via PyMuPDF text extraction, 45-page Brexit PDF):**

```
   Brexit:  PDF p.N  =  journal p.(3177 + N)   for all 42 body pages
            ─────────────────────────────────
            PDF p. 1 → journal p.3178 (title)
            PDF p.14 → journal p.3191 (eq 13)
            PDF p.16 → journal p.3193 (β^UK window)
            PDF p.32 → journal p.3209 (fn 27)
```

**NLM showed CONSISTENT 1-page-EARLY drift vs PDF-verified journal pages:**

| Item                       | NLM cited            | PDF programmatic find          | Drift      |
|----------------------------|----------------------|--------------------------------|------------|
| Eq (13) definition         | journal p.3190       | PDF p.14 = journal p.**3191**  | NLM −1     |
| "2010:M1-2014:M12" quote   | journal p.3192       | PDF p.16 = journal p.**3193**  | NLM −1     |
| Footnote 27                | journal p.3208-3209  | PDF p.32 = journal p.**3209**  | NLM −1/0   |

**Verified facts:**
1. Journal pages 3178-3222 are REAL — not NLM internal index (PDF print headers confirm)
2. NLM cites journal pages but with **+1 calibration** correction needed on body-text quotes
3. PDF page index can be programmatically mapped: PDF p.N = journal p.(3177+N)

**Discipline going forward:**
- Spec retains NLM-cited journal page WITH +1 calibration note; AND PDF-verified page where I have programmatic find
- Chunk-2+ NLM queries explicitly demand BOTH **PDF page number (1-45 index)** AND journal page
- Cross-checking NLM-cited PDF-page-index against the journal-page mapping detects future drift
- All spec page tags verifiable via per-page text extract: `python -c "import fitz; doc=fitz.open('.../campello*.pdf'); print(doc[N].get_text())"`

---

## Status tracker

| Paper                        | PDF p. read   | Spec     | NLM verify | Locked |
|------------------------------|---------------|----------|------------|--------|
| Brexit (Campello 2022 JFQA)  | 1-30 of 45 (programmatic verify ✓) | chunks 1-2 PDF-locked | ✅ chunk-1 / ⏳ chunks 2-3 NLM | partial (need 31-45) |
| Boasiako 2020 EFM databreach | 0 / 24        | none     | none       | NO     |
| Chen 2017 JAAF restatement   | 0 / 28        | none     | none       | NO     |

---

# PAPER 1 — Campello, Cortés, d'Almeida, Kankanhalli (2022) JFQA

**File:** `docs/papers/campello_etal_2022_brexit_jfqa.pdf`
**Citation:** Journal of Financial and Quantitative Analysis, Vol. 57, No. 8 (Dec 2022), pp. 3178–3222
**DOI:** 10.1017/S0022109022000308
**Title (verbatim p.3178):** "Exporting Uncertainty: The Impact of Brexit on Corporate America"
**Authors (verbatim p.3178):** Murillo Campello (Cornell + NBER, corresponding) · Gustavo S. Cortes (UFlorida) · Fabrício d'Almeida (Purdue) · Gaurav Kankanhalli (UPittsburgh)

---

## CHUNK 1 — pages 3178-3192 (Title + Abstract + I + II + III + IV.A + IV.B start)

### 1A. Abstract (verbatim, p.3178)

> "We show that the 2016 Brexit Referendum had multifaceted consequences for corporate America, shaping employment, investment, divestitures, R&D, and savings. The unexpected vote outcome led U.S. firms to cut jobs and investment within U.S. borders. Using establishment-level data, we document that these effects were modulated by the reversibility of capital and labor."

### 1B. Cash holdings result — Introduction (verbatim, p.3181)

> "Looking beyond investment and employment, we examine several auxiliary firm policies and find that U.K.-exposed firms also saved more cash and accumulated less inventory (noncash working capital (NWC)) in the aftermath of the Brexit vote. Our estimates imply that following the vote, U.K.-exposed firms increased their cash holdings by 12% relative to their baseline level."

> "The results we report are in line with literature on corporate liquidity management suggesting that, in times of heightened volatility, firms with higher market exposure are likely to increase liquid asset holdings for precautionary reasons (e.g., Acharya, Almeida, and Campello (2013))."

⚠️ **Open from chunk 1**: 12% relative increase mentioned. Exact β + SE + N + table not yet read (Section V or tables, p.16-45).
✅ **Locked from chunk 1**: precautionary channel cite = ACW 2013.

### 1C. Earnings-call critique (verbatim, p.3182, footnote 4)

> "Recently, Hassan, Hollander, van Lent, and Tahoun (2020) study the international effects of Brexit relying exclusively on firms' 'conference calls' to gauge their exposure to Brexit. In contrast, our textual analysis of mandatory 10-K filings is complemented by a market-based approach in order to comprehensively gauge a firm's exposure to events in the United Kingdom. We choose not to rely on conference calls in light of ample evidence on severe problems with the information content of such calls (see Hollander, Pronk, and Roelofsen (2010), Matsumoto, Pronk, and Roelofsen (2011), and Bushee, Jung, and Miller (2011))."

✅ **Locked**: Hassan-style earnings-call substitute is REJECTED in this paper. Replication MUST use 10-K parsing as the textual measure.

### 1D. Brexit timeline anchors (verbatim, p.3183)

> "On Feb. 20, 2016, he announced that voting would take place on June 23, 2016."
> "On the eve of the referendum, bookmakers' odds showed chances of more than 90% that the United Kingdom would remain in the European Union."

EPU magnitude (verbatim p.3183):
> "The average quarterly U.K. EPU index before 2016 was 133 (starting from the beginning of the modern series in 1997). The index jumped by 410 points in 2016 (nearly 4 times the baseline average, or a 3.4-standard-deviation from the series)."

### 1E. β^UK regression — Section IV.A.1 (verbatim, p.3190-3191)

**Setup (p.3190):**
> "We adopt two approaches. The first follows the framework very closely, yielding an empirical proxy for β_i that is derived from the capital markets. The second is based on expectations of corporate decision-makers regarding uncertainty, taken from firms' disclosures to market investors."

**Estimation (p.3191):**
> "Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i"

**Equation (13) (verbatim, p.3191):**

```
   ┌────────────────────────────────────────────────────────────────────┐
   │   vol(r_it) = α_i + β_i^UK · vol(FTSE100_t) + θ · CONTROLS_t + ε   │
   └────────────────────────────────────────────────────────────────────┘
```

**CONTROLS verbatim (p.3191):**
> "Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it). It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting). We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound."

**Output verbatim (p.3191):**
> "For each firm, we take the estimated value of β_i^UK from regression (13) as the empirical counterpart to β_i in our framework."

**Robustness twin (verbatim, p.3191 fn 13):**
> "Following Vuolteenaho (2002), we also decompose the volatility of each firm's returns into cash flow and discount rate components, and reestimate equation (13) with the cash flow component (only) as the dependent variable, obtaining an alternative uncertainty measure, β_i,CF^UK. The estimates for β_i^UK and β_i,CF^UK have a rank correlation of 0.8, and there is an 86% overlap in the set of firms at the top tercile of both β_i^UK and β_i,CF^UK. As shown in Table C6, our inferences are unchanged whether using β_i^UK or β_i,CF^UK to conduct our tests."

⚠️ **Open from chunk 1 — must verify in p.16-45 OR via NLM**:
- vol() window length (rolling 24-mo? full sample 2010-2016? pre-Brexit only?)
- vol() frequency (monthly returns? daily returns aggregated to monthly vol?)
- Frequency of t in eq (13) — monthly or quarterly observations?
- β^UK static-per-firm (single coefficient) or time-varying β_{i,t} (rolling)?
- Whether FTSE100 + SP500 + FX£ are themselves volatilities or levels

### 1F. 10-K classifier — Section IV.A.2 (verbatim, p.3191-3192)

**Approach verbatim (p.3191):**
> "As an alternative measure of U.S. firms' exposure to Brexit-induced uncertainty, we develop a textual-search-based metric that is constructed by parsing firms' 2015 10-K filings."

**Keywords PRIMARY verbatim (p.3191):**
> "In particular, we look for the number of entries of keywords related to uncertainty about Brexit ('Brexit', 'Great Britain', and 'Uncertainty') in firms' disclosures, classifying firms with a 'high' number of entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control firms."

**Keywords SUBSUMED verbatim (p.3191, footnote 14):**
> "Entries like 'Referendum,' 'Uncertain,' 'United Kingdom,' 'UK,' 'U.K.,' and 'G.B.' are subsumed by the above wording."

**Filing window verbatim (p.3191):**
> "Notably, the vast majority of firms file their 10-Ks with the SEC between March and June of each year. By computing these wordcounts from firms' 2015 10-K disclosures (before the actual vote takes place, yet after the referendum is announced), we build a measure of exposure to the United Kingdom based on what firms consider relevant to communicate to their investors on the eve of the 2016 Brexit vote."

**Cutoffs verbatim (p.3192):**
> "Brexit cites at more than 5 entries. There are 807 firms citing Brexit more than 5 times in their 10-Ks. On the other hand, 433 do not cite any Brexit-related terms in their public filings. Although the heuristic cutoff we consider is naturally arbitrary, our results are robust to many sensible alternative choices."

✅ **Locked from chunk 1:**
- 9 keywords total: 3 primary + 6 subsumed
- Filing year: 2015 (March-June calendar filing window)
- TREATED cutoff: count > 5 → 807 firms
- CONTROL cutoff: count = 0 → 433 firms
- Total 10-K-classified firms: 1,240

⚠️ **Open from chunk 1 — must verify in p.16-45 OR via NLM**:
- 10-K Item scope (whole filing / Item 1A "Risk Factors" / Item 7 "MD&A")
- Word matching rules (case-sensitive? whole-word boundary? regex?)
- Equivocation handling ("U.K." vs "UK" vs "uk")
- Whether forward 10-Ks (10-K/A amendments, 10-KT transitions) included

### 1G. Sample — Section IV.B (verbatim, p.3192)

> "We use COMPUSTAT Quarterly to gather basic information on firm investment and financial data."
> "We consider U.S. companies from the first calendar quarter of 2010 to the fourth quarter of 2016."
> "We drop utility and financial firms, as well as companies whose market value or book assets are lower than $10 million."
> "The sample used in our baseline investment tests consists of 41,630 observations (firm-quarters)."

**Footnote 15 (p.3192):**
> "For details of the sample selection filters, see Table C1 in the Supplementary Material."

✅ **Locked from chunk 1:**
- Window: 2010Q1-2016Q4 (28 quarters)
- N investment baseline: 41,630 firm-quarters
- Industry exclusion: utility + financial (SIC ranges in Table C1 supplementary, NOT main text)
- Size cutoff: market value OR book assets ≥ $10M

⚠️ **Open from chunk 1**:
- SIC ranges defining "utility" and "financial" — F1D default 4900-4999 + 6000-6999; need confirmation from Table C1 (supplementary, NLM-accessible)
- Cash-DiD sample N differs from 41,630 (cash test in §V is auxiliary; needs separate N) — not yet PDF-verified
- Whether Compustat Quarterly variants (Compustat NA / Industrial / Financial Services) all included

### 1H. Chunk 1 NLM reconciliation (2026-05-08 PM-late+1.5h)

Sina ran Q1-Q4 in NLM `f1d` notebook (Q1+Q2 ran twice for cross-check). Verbatim responses captured below.

#### Q1 — β^UK eq (13) spec ✅ ALL LOCKED

PDF p.3191 ↔ NLM substance match. Eq (13) form, DV, regressor, controls, per-firm output all confirmed.

⚠️ **NLM-page-citation calibration**: NLM cited eq (13) on **p.3190**; PDF shows eq (13) on **p.3191**. NLM has 1-page-early citation drift on this item. Substance is trustable; **verify pages independently via PDF reads going forward**.

#### Q2 — β^UK estimation details ⚠️ PROVISIONAL LOCK (NLM-cited; PDF chunk 2/3 verify pending)

Items NOT in p.1-15 but provided by NLM:

- **Estimation window**: **2010M1-2014M12** (60 months pre-Brexit). NLM verbatim:
  > "We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events"

  NLM citation ambiguous: Run-1 said "(Section IV.B, Page 3192)"; Run-2 said "(Section V.B.1)". Will resolve via PDF chunk-2 read.

- **Frequency of t**: **monthly** (returns data; same NLM quote)
- **Type**: **STATIC baseline** (one β_i^UK per firm). **ROLLING 24-mo** is Section VI.A FX-robustness analogue, NOT baseline. NLM verbatim from fn 27:
  > "Specifically, we perform our estimation using monthly returns data, with 24-month rolling windows, over the period from 2010:M1 to 2016:M12" (Section VI.A, p.3208-3209, fn 27)
  > "we estimate a dynamic analogue of equation (13), firm by firm, over our testing period" (p.3208)

- **vol() input frequency/window**: **NOT IN PAPER** ✅ (NLM confirmed silence)

#### Q3 — 10-K keywords + cutoffs ✅ ALL LOCKED

PDF ↔ NLM full match. NEW verbatim quote captured:
> "We arbitrarily set a cutoff for high Brexit cites at more than 5 entries." (p.3191-3192, NLM-cited)

#### Q4 — 10-K Item scope + matching rules ✅ ALL "NOT IN PAPER" CONFIRMED

NLM confirmed paper silent on Item scope, matching rules, amendments, text source. fn 14 covers spelling variants only.

**Locked F1D defaults for chunk-1 silent items:**

| Item                | Default                                          | Justification |
|---------------------|--------------------------------------------------|---------------|
| 10-K Item scope     | whole 10-K                                       | most permissive; paper says "parsing firms' 2015 10-K filings" without restriction |
| Matching rules      | case-insensitive + whole-word boundary           | standard NLP; fn 14 listing "UK"/"U.K."/"G.B." implies case-insensitive intent |
| 10-K amendments     | include 10-K, 10-K/A, 10-KT, 10-KT/A             | already filtered in prior-session SRAF archive (9,275 files) |
| 10-K text source    | SRAF Notre Dame 10-X_C archive                   | acquired prior session; filtered to 9,275 2015 files |

#### Open after chunk 1 (carry to chunks 2/3)

1. PDF-verify "2010M1-2014M12" quote location (NLM cited Section IV.B vs Section V.B.1 ambiguous) — chunk 2 p.3193-3207
2. PDF-verify fn 27 verbatim (Section VI.A) — chunk 3 p.3208-3209
3. Cash DiD spec details (DV / POST / FE / SE / N / β / SE) — chunk 2/3
4. SIC ranges defining utility + financial — Table C1 supplementary (NLM-only; not in paper main text)

---

## NLM verification queries — chunk 1 (p.1-15)

Run each in NotebookLM (`f1d` notebook). Each query is standalone copy-paste-ready. Return verbatim NLM response. I will cross-check NLM ↔ PDF, then either lock spec or flag conflict.

**Hint to NLM-side prompting:** queries demand verbatim with page numbers + footnote numbers because the deprecated audit's failure mode was paraphrase-drift. Don't accept paraphrase.

```
QUERY 1 — β^UK regression spec (Section IV.A.1)

In Campello, Cortés, d'Almeida, Kankanhalli (2022) "Exporting Uncertainty: The
Impact of Brexit on Corporate America", JFQA Vol. 57 No. 8: quote verbatim the
COMPLETE functional form of equation (13) used to estimate β_i^UK. Also quote
verbatim: (a) the dependent variable definition, (b) the regressor of interest,
(c) all controls, (d) the per-firm output (β_i^UK). All from Section IV.A.1.
Provide page numbers for each quote.
```

```
QUERY 2 — β^UK estimation window, frequency, static vs rolling

In Campello et al. (2022) JFQA equation (13) used to estimate β_i^UK:
1. What TIME WINDOW is used to estimate β_i^UK for each firm i? (Full sample
   2010Q1-2016Q4? Pre-Brexit only? Specific subperiod?)
2. What is the FREQUENCY of observations indexed by t in equation (13)?
   (Monthly? Quarterly? Daily?)
3. Is β_i^UK estimated ONCE per firm (static, single coefficient) or as a
   time-varying β_{i,t} (rolling-window)?
4. What is the FREQUENCY and WINDOW of the volatility computations
   vol(r_it), vol(FTSE100_t), vol(SP500_t), vol(FX£_t) themselves?

Quote any text from Sections IV, V, VI, or footnotes addressing these. Cite
page + footnote numbers. If silent on any sub-question, say "NOT IN PAPER".
```

```
QUERY 3 — 10-K keyword list, cutoffs, firm counts (Section IV.A.2)

In Campello et al. (2022) JFQA Section IV.A.2: list ALL keywords searched in
firms' 10-K filings, including BOTH primary keywords AND keywords subsumed by
them (per footnote). Then quote verbatim:
1. The cutoff defining HIGH_UK_EXPOSURE (treated) firms.
2. The cutoff defining control firms.
3. The number of firms in each group.
4. The total firms across treated + control.
5. The filing year of the 10-Ks searched.
6. The filing window (months) within that year.

Provide page numbers and footnote numbers for each.
```

```
QUERY 4 — 10-K Item scope + matching rules (Section IV.A.2)

In Campello et al. (2022) JFQA Section IV.A.2 on parsing 10-K filings:
1. Is the keyword search applied to the WHOLE 10-K document, or restricted
   to a specific Item (Item 1 Business, Item 1A Risk Factors, Item 7 MD&A,
   etc.)?
2. What are the matching rules — case-sensitive? Case-insensitive?
   Whole-word match? Substring? Regex?
3. Are equivocations like "U.K." / "UK" / "uk" / "U. K." treated as the
   same match?
4. Are 10-K amendments (10-K/A) and transitional filings (10-KT)
   included in the search universe?
5. What is the source of the 10-K text data? (EDGAR full-text? SRAF Notre
   Dame? Self-extraction?)

Quote verbatim with page + footnote numbers. If silent on any sub-question,
say "NOT IN PAPER".
```

---

## Next steps after chunk-1 NLM verify

1. Sina runs Q1-Q4 in NotebookLM, returns responses
2. Orchestrator reconciles NLM ↔ PDF chunk 1
3. LOCK 1A-1G or flag conflicts
4. Read PDF chunk 2 (p.16-30 = Section IV.C onward + V baseline)
5. Repeat draft + NLM verify
6. After Brexit fully locked → start Boasiako (paper 2)
7. After Boasiako fully locked → start Chen (paper 3)

---

## CHUNK 2 — PDF p.16-30 = journal p.3193-3207

PDF read complete 2026-05-08 PM-late+2h. Programmatic anchor verification via PyMuPDF text extraction confirms all key facts.

### 2A. β^UK estimation window — VERIFIED (PDF p.16 = journal p.3193, Section IV.B continuation) ✅

> "We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13)). We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events."

✅ **LOCKED:**
- Window: **2010M1-2014M12** (60 months pre-Brexit)
- Frequency: **monthly returns**
- Data sources: **CRSP** (firm equity returns) + **Bloomberg** (FTSE100 index + USD/GBP)

### 2B. β^UK tercile cuts — VERIFIED (PDF p.16 = journal p.3193, Section IV.C.1) ✅

> "we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the β_i^UK distribution. For pure contrasting, we do not include firms that *benefit* from uncertainty in the United Kingdom in the control group (firms with β_i^UK < 0) as this could lead to overestimation biases attached to the treatment effects we seek to identify. Nevertheless, in specifications where we use β_i^UK as a continuous treatment variable, we relax this restriction and include all values of β_i^UK."

> "Under this market-based approach, a total of 449 unique firms are assigned to the treated category (β_i^UK > 0.68). In contrast, 360 unique firms are assigned to the control category (β_i^UK < 0.28)."

✅ **LOCKED:**
- Tercile-based: **nonnegative β^UK only** (drop β^UK<0 from BOTH treated and control)
- TREATED: top tercile, β^UK > **0.68** → **449 firms**
- CONTROL: bottom tercile of nonnegative, β^UK < **0.28** → **360 firms**
- Continuous-treatment col 1: includes ALL β^UK (incl. β^UK<0)

**Footnote 17 (PDF p.16 = journal p.3193, robustness):**
> "In unreported tests, we only label those firms with statistically significant positive β_i^UK estimates as treated firms, and those with β_i^UK statistically indistinguishable from 0 as controls. We find that our results hold across a range of sensible treatment assignment thresholds."

### 2C. DiD Empirical Model Equation (14) — VERIFIED (PDF p.19 = journal p.3196, Section IV.C.3) ✅

> "We compare differences in outcomes of interest between treated (HIGH_UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms. Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects. This is equivalent to estimating the following model:"

```
   ┌──────────────────────────────────────────────────────────────────────┐
   │  Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θ·CONTROLS_{i,t-1}   │
   │           + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ε_{i,t}  │   (14)
   └──────────────────────────────────────────────────────────────────────┘
```

> "The outcomes of interest, Y_{i,t}, are fixed capital investment, employment growth, R&D expenditures, divestitures, **cash holdings**, and NWC. HIGH_UK_EXPOSURE_i is a dummy variable that equals 1 if firm i is U.K.-exposed, and 0 otherwise. A firm is considered to be U.K.-exposed according to two measures: i) if it belongs to the top tercile of β_i^UK (market-based measure); or ii) if it has a high number of Brexit-related entries in its 2015 10-K form (textual-search-based measure). POST_t equals 1 if the time period is in the 2016:Q3–Q4 window."

✅ **LOCKED:**
- Y outcomes: 6 listed including **cash holdings** ← target for our DiD replication
- POST_t = 1 if t ∈ {2016Q3, 2016Q4}; 0 otherwise
- HIGH_UK_EXPOSURE_i = top-tercile β^UK (col 2) OR >5 10-K entries (col 3); SEPARATE specs not combined
- DiD identification anchor: **2016Q3-Q4 vs 2015Q3-Q4** comparison

### 2D. Controls + FE + SE — VERIFIED (PDF p.20 = journal p.3197, Section IV.C.3) ✅

> "CONTROLS_{i,t-1} is a vector of macroeconomic and firm-level control variables. **Macro controls** include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingston Survey, the lagged Consumer Sentiment Index from the University of Michigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia. **Firm-level controls** include lagged stock returns, Tobin's Q, cash flow, logged assets, and sales growth. **As an additional control for first-moment effects of Brexit, we add 1-quarter-ahead consensus earnings forecasts to our model.** FIRM_i represents firm-fixed effects, INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100), and QUARTER_t are calendar-quarter dummies. **Standard errors are double-clustered by firm and calendar quarters.**"

✅ **LOCKED CONTROLS (all 1Q-LAGGED):**

**Macro (5):**
1. USD/GBP FX rate
2. VIX implied volatility index
3. GDP growth 1Y-ahead forecast (Philly Fed Livingston Survey)
4. Consumer Sentiment Index (UMich UMCSENT)
5. Leading Economic Indicator (Philly Fed)

**Firm-level (5 baseline + 1 additional in baseline = 6 total):**
1. Stock returns
2. Tobin's Q
3. Cash flow
4. Logged assets (size)
5. Sales growth
6. **1Q-ahead consensus EPS forecast** ← in baseline per "we add ... to our model"

✅ **OVERRULES Round-5 verdict + CONFIRMS Round-6 concession** — direct PDF main-text verbatim p.3197 confirms consensus EPS forecast IS in baseline. Agent's Round-4 reading correct; my Round-5 wrong-verdict overstepped; Round-6 NLM concession was right.

✅ **LOCKED FE:** FIRM_i + Hoberg-Phillips FIC100 INDUSTRY_j × QUARTER_t
✅ **LOCKED SE:** double-cluster firm + calendar-quarter

**Footnote 21 (PDF p.20 = journal p.3197):**
> "These industries are formed by grouping firms with textually similar product descriptions in their 10-Ks. Hoberg and Phillips (2016) show that the resulting industry classification is more granular and captures the locus of product-market competitors of a given firm better than the standard SIC or NAICS industry schemes."

### 2E. CASH variable definition — VERIFIED (PDF p.21 = journal p.3198, Table 1 footer) ✅

> "**CASH is defined as cash and short-term investments divided by lagged total assets.** ... All variables are winsorized at the 1% level."

✅ **LOCKED:** CASH = Compustat **CHEQ / lag(ATQ)**, winsorized 1% both tails

Other variables from same Table 1 footer (all winsorized 1%):
- INVESTMENT = capx / lag(AT) (quarterly)
- EMPLOYMENT_GROWTH = annual % change in # employees
- R&D = R&D / lag(AT) (firms with non-missing R&D only)
- DIVESTITURES = SPPE / lag(AT)
- NON_CASH_WORKING_CAPITAL = (working capital − cash) / lag(AT)
- TOBIN_Q = (market equity + book assets) / book assets
- CASH_FLOW = OIBDP / lag(AT)
- SIZE = ln(AT)
- SALES_GROWTH = year-on-year % change in **quarterly EPS** ⚠️ likely paper typo
- CONSENSUS_EARNINGS_FORECAST = standardized mean 1Q-ahead EPS forecast
- STOCK_RETURNS = quarterly buy-and-hold return

⚠️ **OPEN — SALES_GROWTH oddity**: footer literally says "year-on-year percentage change in quarterly earnings per share" — likely typo (var name SALES_GROWTH but def via EPS). NLM query Q7 below.

### 2F. PSM + parallel trends — IN SUPPLEMENTARY (PDF p.20 = journal p.3197) ⚠️

> "we redo all of our tests on propensity score matched samples in which firm-level characteristics are balanced before any estimations are conducted. Table C2 in the Supplementary Material displays the summary statistics of the matched samples. Table C3 in the Supplementary Material reports the results of our main estimations on these matched samples."

> "we examine the validity of the parallel trends assumption. Visual evidence for that assumption regarding the investment process is provided in Figure C1 in the Supplementary Material. Tables C4 and C5 in the Supplementary Material report formal tests supporting the presence of parallel trends across all outcome variables."

⚠️ PSM (Tables C2 + C3) and parallel-trends (Figure C1, Tables C4 + C5) in **SUPPLEMENTARY only** — not in main paper text. Will need NLM access OR F1D-default replication.

### 2G. Investment + Employment results — Table 2 (PDF p.23 = journal p.3200) ✅

| Spec | DID coef | SE | N | R² |
|------|----------|-----|----|----|
| INV col 1 (linear β^UK) | POST×β^UK = **−0.047*** ** | 0.010 | 43,025 | 0.67 |
| INV col 2 (top tercile) | POST × HIGH_β^UK = **−0.165*** ** | 0.019 | 17,199 | 0.75 |
| INV col 3 (>5 10-K) | POST × HIGH_10K_ENTRIES = **−0.077*** ** | 0.008 | 21,253 | 0.73 |
| EMP_GROWTH col 4 | POST×β^UK = **−4.173** ** | 2.133 | 9,143 | 0.35 |
| EMP_GROWTH col 5 (top tercile) | POST × HIGH_β^UK = **−4.912*** ** | 1.552 | 3,540 | 0.45 |
| EMP_GROWTH col 6 (>5 10-K) | POST × HIGH_10K_ENTRIES = **−2.617*** ** | 0.402 | 4,173 | 0.45 |

Pre-Brexit avg INV = 1.1% of assets → −0.165 ppt = **15% drop** in investment rates ($2B aggregate).

**Footnote 23** (PDF p.23 = journal p.3200, Table 2 footnote):
> "In Table C7 in the Supplementary Material, we show that our baseline findings are robust to the inclusion of numerous controls for simultaneous changes in the first-moment component of the Brexit shock. These include Tobin's Q, Cash Flow, Sales Growth, Consensus Earnings Forecasts, and 1-year Stock Returns. In addition, we include the firm-level first-moment instruments for the USD–GBP exchange rate, the price of oil, and the Treasury rate from alfaro2018."

⚠️ **Cash holdings DiD result NOT in Table 2.** Programmatic search for "0.68" landed on **PDF p.31 = journal p.3208** in a 6-column table. Coefficients glimpsed (POST×HIGH_β^UK row: 0.231***/0.687***/0.135 with SEs 0.059/0.281/0.391; POST×HIGH_10K_ENTRIES row: 0.357***/0.608***/0.343 with SEs 0.062/0.079/0.550). Full table structure (which cols = CASH vs NWC vs other) requires chunk 3 PDF read.

### 2H. Open after chunk 2 (carry to chunk 3 read)

1. **Cash DiD result full table** (β/SE/N/R² for all cols) — PDF p.31 = journal p.3208 ← THE MONEY RESULT
2. **Footnote 27 verbatim** (FX-robustness rolling β^UK) — PDF p.32 = journal p.3209
3. **Trump-2016 exclusion robustness**, Cameron 2015 placebo, debt-ceiling 2011 placebo
4. **Sample window question** — eq (14) regression uses full 28-quarter panel OR 4-quarter restricted? Table 2 col 1 N=43,025 ≫ 4×809 firms ⇒ full panel suspected
5. **SALES_GROWTH definition typo?** EPS-based vs sales-based
6. **SIC ranges utility/financial** — Table C1 supplementary

---

## NLM verification queries — chunks 2-3 (PDF p.16-45)

**⚠️ NEW DISCIPLINE**: All queries demand BOTH **PDF page number (1-45 index in uploaded PDF) AND journal page number** (printed in page header). NLM's prior 1-page-early drift on journal pages can be detected by cross-checking against PDF page index.

```
QUERY 5 — Cash holdings DiD specification + table

In Campello et al. (2022) JFQA, eq (14) [journal p.3196] lists "cash holdings"
as outcome Y. Quote verbatim from Section V results discussion + relevant table:
1. The CASH dependent variable definition (Table 1 footer journal p.3198 gives
   "cash and short-term investments divided by lagged total assets" — confirm).
2. The headline DiD coefficient (POST × HIGH_UK_EXPOSURE) for CASH separately
   under: (a) tercile-based β^UK, (b) 10-K-based >5 entries, (c) linear β^UK.
3. Standard errors for each (paper double-clusters firm + calendar-quarter).
4. Sample size N for each spec.
5. Table number where this CASH result appears.
6. Any text discussion of the cash result in Section V or VI.

For each verbatim quote, provide BOTH:
(a) PDF page number (1-45 index in the uploaded PDF)
(b) Journal page number printed in the page header
If they differ, list both clearly.
```

```
QUERY 6 — Regression sample window for eq (14) DiD

In Campello et al. (2022) JFQA eq (14) DiD regression Y_it = α + δ[POST × HIGH] + ...
[journal p.3196]: what is the EXACT sample period used IN THE REGRESSION?
1. Is the regression estimated on the FULL panel 2010Q1-2016Q4 (~28 quarters per
   firm, with POST_t = 1 only when t ∈ {2016Q3, 2016Q4})?
2. OR a RESTRICTED 4-quarter window (only 2015Q3, 2015Q4, 2016Q3, 2016Q4)?
3. The Table 2 footer (journal p.3200) states "The time dimension of the DID
   estimator is set so as to compare the two quarters following the announcement
   of the referendum and Brexit's victory (2016:Q3–Q4) versus the two quarters
   preceding the announcement (2015:Q3–Q4)" — does this imply 4-quarter sample
   restriction OR identification interpretation only?
4. Empirical clue: Table 2 col 2 N=17,199 with treated 449 + control 360 = 809
   firms × 4 quarters = 3,236 ≫ 17,199. So sample is NOT just 4 quarters.
   What IS the sample period? Quote any clarifying text in Section IV.B, IV.C,
   or footnotes.

For each verbatim quote: PDF page (1-45) AND journal page.
```

```
QUERY 7 — SALES_GROWTH variable definition (Table 1 footer)

In Campello et al. (2022) JFQA Table 1 footer [journal p.3198], SALES_GROWTH is
defined verbatim as "the year-on-year percentage change in quarterly earnings
per share." Is this a TYPO for "quarterly sales" or is SALES_GROWTH actually
EPS-based as the footer literally states? Search the rest of the paper +
Supplementary description for any other mention of SALES_GROWTH or sales-growth
metric to disambiguate.

For each verbatim quote: PDF page (1-45) AND journal page.
```

```
QUERY 8 — SIC ranges for utility + financial exclusions

In Campello et al. (2022) JFQA, Footnote 15 [journal p.3192] says "see Table C1
in the Supplementary Material" for sample selection filter details. Quote
verbatim from the Supplementary Material:
1. The exact SIC code ranges for "utility firms" and "financial firms" excluded.
2. Any other sample selection filters applied.
3. Where the supplementary material is located (separate PDF file? embedded
   appendix? published online via Cambridge Core?).

For each verbatim quote: PDF page (1-45 of either main paper or supplementary)
AND journal page if applicable.
```

```
QUERY 9 — Trump-exclusion + Cameron placebo + other falsifications

In Campello et al. (2022) JFQA, the paper mentions:
1. Excluding the Trump 2016 election period as robustness check.
2. Using David Cameron's 2015 election as a placebo.
3. Possibly: debt-ceiling 2011 placebo, other major-trading-partner countries
   (China, Mexico, Japan, India, Brazil) as falsification.

Quote verbatim each robustness/placebo check, including:
- The specification (sample window, treatment definition, etc.)
- The result (DiD coefficient, SE, N).
- The table or section number where it appears.

For each verbatim quote: PDF page (1-45) AND journal page.
```

---

## CHUNK 3 — PDF p.31-45 = journal p.3208-3222 (PENDING)

(p.31-45 not yet read; programmatic anchor finds suggest CASH DiD on PDF p.31, fn 27 on PDF p.32, other-country re-estimation on PDF p.39. Will read after chunk-2 NLM verify reconciliation.)

---

# PAPER 2 — Boasiako, O'Connor Keefe (2020) EFM

(Pending — start after Brexit locked.)

# PAPER 3 — Chen, Cheng, Lin, Tang (2017) JAAF

(Pending — start after Boasiako locked.)
