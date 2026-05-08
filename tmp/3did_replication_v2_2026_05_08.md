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
| Brexit (Campello 2022 JFQA)  | 1-45 of 45 (full read ✓) | chunks 1-3 PDF-locked + Q-A/Q-B/Q-D NLM-locked | ✅ chunk-1 + unified batch | **LOCKED** (Q-C SIC supplementary = F1D default) |
| Boasiako 2021 EFM databreach | 1-24 of 24 (full read ✓) | full PDF + NLM batch reconciled | ✅ Q-A/B/C/E LOCKED ⏳ Q-D online appendix deferred | **LOCKED** (online appendix open) |
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
- SALES_GROWTH = year-on-year % change in **quarterly sales** ✅ (corrected — my prior visual read of "quarterly EPS" was wrong; programmatic + NLM both confirm "sales")
- CONSENSUS_EARNINGS_FORECAST = standardized mean 1Q-ahead EPS forecast
- STOCK_RETURNS = quarterly buy-and-hold return

✅ **CORRECTED 2026-05-08 PM-late+3h**: programmatic PyMuPDF text extract from PDF p.21 (j.3198) confirms SALES_GROWTH = "year-on-year percentage change in **quarterly sales**". My prior visual read claimed "quarterly EPS" — wrong. NLM batch Q-B independently confirmed "quarterly sales". NO TYPO. LOCKED. Calibration: visual PDF image reading unreliable for fine wording; programmatic text extract is source-of-truth.

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

## NLM verification queries — chunks 2-3 (Q5-Q9, OBSOLETE — see UNIFIED batch above)

**⚠️ NEW DISCIPLINE**: All queries demand BOTH **PDF page number (1-45 index in uploaded PDF) AND journal page number** (printed in page header). NLM's prior 1-page-early drift on journal pages can be detected by cross-checking against PDF page index.

**⚠️ DO NOT RUN Q5-Q9 BELOW.** They were emitted before full PDF read; most resolved directly via PDF; remainders subsumed in UNIFIED Brexit verification batch above. Kept here only for audit trail.

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

## CHUNK 3 — PDF p.31-45 = journal p.3208-3222 (Section V.C + VI Robustness + VII + Appendices)

PDF read complete 2026-05-08 PM-late+2.5h. /pdf skill (pdfplumber) attempted; default + text-strategy table extraction failed for academic-paper layout. Fell back to pymupdf text + visual image read for Table 8 / Table 12 / Table 13 cell values.

### 3A. Cash + NWC + Profits result — Table 8 (PDF p.31 = journal p.3208) ✅✅ THE MONEY RESULT

**Section V.C body text (verbatim p.3208):**
> "We also study how the 2016 Brexit vote affected other firms' policies, especially their liquidity management. We do so looking at how firms adjusted their cash holdings and NWC. The positive and highly significant coefficients in columns 1 and 2 of Table 8 show that U.K.-exposed firms increased their cash savings in the face of higher uncertainty induced by the Brexit vote. Negative and highly significant coefficients in columns 3 and 4 show that firms concomitantly accumulated less inventory by adjusting their NWC downward. Although not explicitly modeled in our framework, this behavior is consistent with the theoretical underpinnings from the liquidity management literature. In particular, precautionary behavior will lead firms to change the composition of assets on their balance sheets, leading to the accumulation of the most liquid assets."

> "We further use Table 8 to report results on profit growth. The estimates in columns 5 and 6 are not statistically significant, suggesting that the Brexit vote did not affect the profitability of U.K.-exposed American firms relative to those of nonexposed firms. They support the idea that the investment and employment drops previously reported are arguably due to a 'second-moment' shock to income uncertainty, rather than a negative 'first-moment' shock to firms' cash flows."

**Table 8 footer — verbatim CASH definition (PDF p.31 = j.3208):**
> "Table 8 reports output from equation (14). The dependent variables are CASH, NON_CASH_WORKING_CAPITAL, and PROFITS. **CASH is defined as total cash holdings divided by lagged total assets net of cash holdings.** NON_CASH_WORKING_CAPITAL (NWC) is defined as working capital (net of cash) divided by lagged total assets. PROFITS is defined as the quarterly percentage change in profits (operating income before depreciation divided by sales)."

⚠️⚠️ **CRITICAL — CASH definition DIFFERS between Table 1 footer (descriptive stats) and Table 8 footer (regression):**

| Source | CASH definition | Form |
|--------|-----------------|------|
| Table 1 footer (j.3198) | "cash and short-term investments divided by lagged total assets" | CHE / lag(AT) |
| Table 8 footer (j.3208) | "total cash holdings divided by lagged total assets net of cash holdings" | **CHE / lag(AT − CHE)** |

**Table 8 IS the cash DiD regression table → CHE / lag(AT − CHE) is the regression DV** (BKS-style net-assets scaling, avoids mechanical CHE/AT relationship). This SUPERSEDES the Table 1 footer scaling for replication purposes.

**Table 8 coefficient cells (PDF p.31 = j.3208):**

| Outcome   | CASH (β^UK tercile) | CASH (>5 10-K) | NWC (β^UK tercile) | NWC (>5 10-K) | PROFITS (β^UK) | PROFITS (10-K) |
|-----------|---------------------|----------------|---------------------|---------------|----------------|----------------|
| col       | 1                   | 2              | 3                   | 4             | 5              | 6              |
| POST × HIGH_β^UK | **+0.231*** ** | —             | **−0.687*** **      | —             | −0.135 NS      | —              |
| POST × HIGH_10K  | —             | **+0.357*** ** | —                  | **−0.608*** ** | —              | 0.343 NS       |
| SE        | (0.059)             | (0.062)        | (0.281)             | (0.079)       | (0.391)        | (0.550)        |
| N         | 17,170              | 24,195         | 16,630              | 23,806        | 16,630         | 24,051         |
| R²        | 0.21                | 0.24           | 0.89                | 0.87          | 0.89           | 0.15           |
| Controls Firm | Yes             | Yes            | Yes                 | Yes           | Yes            | Yes            |
| FE Firm   | Yes                 | Yes            | Yes                 | Yes           | Yes            | Yes            |
| FE Industry × time | Yes        | Yes            | Yes                 | Yes           | Yes            | Yes            |

✅ **LOCKED Cash DiD result (the headline for our replication target):**
- β^UK tercile spec: **+0.231*** (SE 0.059), N=17,170, R²=0.21**
- 10-K >5 entries spec: **+0.357*** (SE 0.062), N=24,195, R²=0.24**
- Both highly significant (1% level)
- CASH RATIO INCREASES with U.K. exposure post-Brexit → precautionary
- Profits NS in cols 5-6 → supports second-moment uncertainty interpretation, NOT first-moment cash-flow shock

### 3B. Section VI.A FX-Robustness — Table 9 + Footnote 27 (PDF p.32-33 = j.3209-3210) ✅

**Section VI.A intro verbatim (PDF p.32 = j.3209):**
> "The Brexit vote was followed by a depreciation of the British pound (9% relative to the U.S. dollar). To the extent that our treatment assignment schemes may be correlated with firms' exposures to U.S. dollar/British pound (henceforth, USD–GBP) fluctuations, our results could reflect U.K.-exposed firms' heterogeneous responses to the British pound depreciation (affecting first-moment expectations) rather than to uncertainty generated by the Brexit vote (second-moment expectations)."

> "First, we estimate a dynamic analogue of equation (13), firm by firm, over our testing period. Instead of regressing the volatility of firm equity returns on the volatilities of U.S. and U.K. equity index returns and the volatility of changes in the USD–GBP FX rate, we regress the levels of firms' equity returns on the levels of U.S. and U.K. equity index returns and USD–GBP FX rate changes."

**Footnote 27 — verbatim (PDF p.32 = j.3209):**
> "Specifically, we perform our estimation using monthly returns data, with 24-month rolling windows, over the period from 2010:M1 to 2016:M12."

✅ **LOCKED:** rolling 24-month β^UK is **Section VI.A FX-robustness analogue, NOT baseline**. Baseline β^UK is static-per-firm 2010M1-2014M12.

**Table 9 (Investment, FX-controlled, 8 cols × 4 augmentations × 2 treatments):**

Across all 8 specs, POST×HIGH_β^UK ranges −0.097*** to −0.202***; POST×HIGH_10K ranges −0.080*** to −0.111*** — all *** sig. Result: investment cuts are NOT confounded by FX exposure.

### 3C. Section VI.B Financing Costs — Table 10 (PDF p.34-35 = j.3211-3212) ✅

> "We next investigate whether any of the effects we observe may be ascribed to U.K.-exposed firms experiencing higher financing costs as a result of heightened uncertainty induced by the Brexit vote."

4 financing-cost controls in Table 10 (investment outcome): Existing Bond Yields (TRACE), New Bond Yields (SDC), New Syndicated Loan Spreads (DealScan), Equity Discount Rate News (Vuolteenaho 2002). All 8 specs preserve sig.

### 3D. Section VI.C Automation — Table 11 (PDF p.34, 37 = j.3211, 3214) ✅

Two automation measures controlled:
1. **AUTOMATION_{i∈CZ}**: Acemoglu-Restrepo (2020) commuting-zone-level robot exposure
2. **AUTOMATION_i**: ln(count of top 100 automation keywords from 10-K Section 1 + 7); LM 2011 dictionary derivation, top-100 keywords from engineering syllabi + Benhabib (2003) textbook

Result: investment + employment + R&D + divestitures coefficients robust to automation channel.

### 3E. Section VI.D Trump's Election (PDF p.36 = j.3213) ✅

> "One could be concerned about confounding uncertainty effects associated with the election of President Donald Trump in the United States. We address this issue in two different ways. First, we consider an alternative event window that excludes 2016:Q4 from our treatment evaluation period. This narrower time window helps mitigate concerns that forward-looking behavior of firms regarding Trump's election in the United States could influence our results... we compare the third quarter of 2016 with the same quarter of 2015. As shown in columns 1 and 2 of Table 12, results are similar to our baseline estimates in Table 2."

> "Second, we look at the recent literature on the effect of Trump's election on U.S. firms. Wagner, Zeckhauser, and Ziegler (2018) detail a methodology identifying what the authors label as 'winners' and 'losers' from that election... Our treatment group based on β_i^UK (10-K mentions) contains 57 (23) 'loser' firms."

### 3F. Section VI.E Falsification — Cameron + Debt Ceiling — Table 12 (PDF p.36, 38 = j.3213, 3215) ✅

> "We also address concerns that our test design is set up in a way that may generate results not necessarily tied to the June 2016 referendum result. In doing so, we reestimate our tests considering two 'treatment periods' that occurred prior to the 2016 Brexit vote: i) David Cameron's election as Prime Minister (2015:Q3) and ii) the U.S. Debt Ceiling Crisis of 2011 (2011:Q2–2011:Q4). The first falsification test mitigates concerns that firms anticipated the process leading to the Brexit referendum at the time of Cameron's election. The second addresses concerns that our investment results could be driven by episodes of uncertainty in the United States (and not the United Kingdom) that affect global firms in general."

> "As shown in columns 5–8 of Table 12, the DID coefficients are statistically insignificant in all such cases."

**Table 12 numerical cells (PDF p.38 = j.3215):**

| Spec | Treatment Window / Event | DID coef | SE | N | R² | Sig? |
|------|--------------------------|----------|----|---|----|------|
| col 1 | Excl Trump 2016Q3 vs 2015Q3 (β^UK) | −0.216*** | 0.019 | 17,199 | 0.74 | *** |
| col 2 | Excl Trump (10-K) | −0.064*** | 0.012 | 21,253 | 0.73 | *** |
| col 3 | Excl Trump losers 2016Q3-Q4 vs 2015Q3-Q4 (β^UK) | −0.197*** | 0.010 | 15,967 | 0.75 | *** |
| col 4 | Excl Trump losers (10-K) | −0.074*** | 0.010 | 20,669 | 0.72 | *** |
| col 5 | Cameron 2015Q3 vs 2014Q3 (β^UK) | **0.018 NS** | 0.011 | 17,199 | 0.74 | NS ✓ |
| col 6 | Cameron (10-K) | **0.017 NS** | 0.011 | 21,253 | 0.75 | NS ✓ |
| col 7 | Debt Ceiling 2011Q2-Q4 vs 2010Q2-Q4 (β^UK) | **0.014 NS** | 0.082 | 17,199 | 0.74 | NS ✓ |
| col 8 | Debt Ceiling (10-K) | N/A (10-K not avail pre-2015) | — | — | — | — |

✅ **LOCKED falsifications**: Cameron + Debt Ceiling NS as expected. Trump-exclusion robust (still highly sig).

### 3G. Section VI.F Other-country falsification — Table 13 (PDF p.39 = j.3216) ✅

> "We conduct a battery of supplementary tests to rule out the possibility that our results on investment cuts in the United States may be driven by coincident, potentially uncertainty-inducing events that take place in economies other than the United Kingdom. To do so, we construct metrics analogous to our baseline U.K. exposure measure, β_i^UK, by reestimating equation (13) for developed and emerging markets with relevant trade ties to the United States: European Union, China, Mexico, Japan, India, and Brazil."

> "In this estimation, performed over the same pre-Brexit sample period of 2010:M1–2014:M12, we control for the FTSE100 volatility, the U.S. dollar/British pound exchange rate volatility, and the volatility in the exchange rate of the U.S. dollar and the currency of each country."

**Table 13 (other-country β-exposure, INVESTMENT outcome, PDF p.39 = j.3216):**

| col | Country | DID coef | SE | N | R² | Sig? |
|-----|---------|----------|-----|---|----|------|
| 1 | UK (baseline) | −0.165*** | 0.019 | 17,199 | 0.75 | *** |
| 2 | EU | −0.066*** | 0.018 | 12,301 | 0.76 | *** |
| 3 | CHINA | +0.048 | 0.033 | 8,714 | 0.75 | NS ✓ |
| 4 | MEXICO | +0.069 | 0.044 | 11,870 | 0.76 | NS ✓ |
| 5 | JAPAN | +0.084 | 0.092 | 8,909 | 0.71 | NS ✓ |
| 6 | INDIA | +0.058 | 0.036 | 14,694 | 0.74 | NS ✓ |
| 7 | BRAZIL | −0.054 | 0.045 | 15,485 | 0.74 | NS ✓ |

✅ **LOCKED**: UK + EU sig (geographic spillover plausible); CHN/MEX/JPN/IND/BRA NS — confirms Brexit-specific effect.

### 3H. Sample window — RESOLVED via N inspection (no NLM needed) ✅

**Q6 from chunk-2 batch was: full-panel sample vs 4-quarter restriction?**

**Resolution**:
- Table 2 col 2 (β^UK tercile) N=17,199; treated 449 + control 360 = 809 firms
- 4-quarter window would yield 4 × 809 = 3,236 obs → **way less than 17,199**
- 17,199 / 809 ≈ 21 quarters average per firm → consistent with full 28-quarter panel (2010Q1-2016Q4) with ~25% missing observations from unbalanced entry/exit
- Trump-exclusion (Table 12 col 1) N=17,199 SAME as baseline → POST_t indicator narrows to 2016Q3 only, sample stays full-panel

✅ **LOCKED:** regression sample = **full panel 2010Q1-2016Q4** restricted to top + bottom tercile β^UK firms (~809 firms × ~21 avg quarters per firm). POST_t = 1 only when t ∈ {2016Q3, 2016Q4}; INDUSTRY_j × QUARTER_t FE absorb common time variation.

### 3I. Section VII Concluding + Appendices A-B Theoretical Proofs (PDF p.40-44 = j.3217-3221)

Concluding summary + theoretical proofs (Lemma 3, Propositions 1-5). Replication-irrelevant — skip.

### 3J. References (PDF p.43-45 = j.3220-3222)

Key references for replication infrastructure:
- Acharya, Almeida, Campello (2013) — precautionary channel (cited in cash result discussion)
- Bates, Kahle, Stulz [implicit BKS net-assets cash scaling — Table 8 footer]
- Bloom (2009, 2014) — uncertainty literature
- Hoberg-Phillips (2016) — FIC100 industry classification
- Vuolteenaho (2002) — return decomposition
- Loughran-McDonald (2011) — 10-K text dictionary
- Acemoglu-Restrepo (2020) — automation CZ exposure
- Wagner-Zeckhauser-Ziegler (2018) — Trump winners/losers methodology
- Alfaro et al. (2018) — USD-GBP first/second-moment instruments
- Campello-Lin-Ma-Zou (2011) — FX hedging keyword search

### 3K. Items NOT FOUND in 45-page PDF (vs deprecated session memory claims)

- **WZZ 2018 Wang-Zou-Zhao**: deprecated session memory mentions a "WZZ 2018 'Trump losers' filter (DEFER to v2)". Programmatic grep returned nothing. **Not in this paper.** May have been confused with Wagner-Zeckhauser-Ziegler (2018) which IS in the paper for Trump-loser filter.

### 3L. Open after full PDF read (only items needing NLM verify)

1. **Confirm Table 8 cash definition** = CHE / lag(AT − CHE) [BKS net-assets] applies to regression vs Table 1 footer's CHE / lag(AT). Critical for replication.
2. **SALES_GROWTH definition** — Table 1 footer says "year-on-year % change in **quarterly EPS**"; var name suggests sales-based. Typo or intentional?
3. **SIC ranges utility/financial** — Table C1 supplementary location.
4. **Anything I missed?** — catch-all for major spec items not captured in my full read.

---

## ⚡ UNIFIED Brexit verification batch (post full-PDF read)

**Discipline**: ALL queries demand BOTH **PDF page (1-45 index) AND journal page**. Cross-check detects future drift.

**Replaces previously-emitted Q5-Q9** (now subsumed; full PDF read resolved most via direct PDF). Only 4 queries below.

```
QUERY A — CASH definition disambiguation (Table 1 vs Table 8)

In Campello et al. (2022) JFQA, two CASH definitions appear:

(1) Table 1 footer [journal p.3198]:
    "CASH is defined as cash and short-term investments divided by lagged
    total assets" → CHE / lag(AT)

(2) Table 8 footer [journal p.3208]:
    "CASH is defined as total cash holdings divided by lagged total assets
    net of cash holdings" → CHE / lag(AT − CHE)  [BKS net-assets style]

Table 8 IS the cash DiD regression table; Table 1 is descriptive statistics.

CONFIRM:
1. Table 8 footer applies to the cash DiD regression in eq (14)?
2. Quote the EXACT verbatim Table 8 footer sentence defining CASH.
3. Is "lagged total assets net of cash holdings" parsed as
   lag(AT − CHE) [option B, BKS style] or (lag(AT)) − CHE_t [option A]?
4. Any additional sentence in Section V.C body or Table 8 footer that
   clarifies the CHE_t numerator (just CHE? or CHE + STI?
   or include marketable securities)?

Provide PDF page (1-45) AND journal page for each citation.
```

```
QUERY B — SALES_GROWTH typo or intentional?

In Campello et al. (2022) JFQA Table 1 footer [journal p.3198],
SALES_GROWTH is defined verbatim as "year-on-year percentage change in
quarterly earnings per share."

Variable name says SALES_GROWTH; definition uses EPS. Search Table 1 +
Section IV.D + supplementary descriptions for ANY clarifying mention.

Is this:
1. A typo for "quarterly sales"?
2. An intentional EPS-based metric the authors call SALES_GROWTH?
3. Some standardization metric (e.g., ΔEPS/Sales)?

Quote any verbatim text + PDF page (1-45) + journal page.
```

```
QUERY C — Sample selection filters in Table C1 supplementary

Footnote 15 [journal p.3192] directs to Table C1 in Supplementary Material
for sample selection details.

Quote verbatim from Table C1 (or anywhere in Supplementary Material):
1. Exact SIC code RANGES for "utility firms" excluded.
2. Exact SIC code RANGES for "financial firms" excluded.
3. Any additional sample filters (Compustat universe restrictions, listing
   rules, currency, primary stock exchange, etc.).
4. Where the supplementary material is located in NotebookLM (separate
   PDF file uploaded? Embedded in main paper PDF? Online via Cambridge
   Core link?).

PDF page of supplementary (if separate file: indicate file name) AND
journal page if applicable.
```

```
QUERY D — Catch-all: anything else I missed?

Post my full 45-page PDF read of Campello et al. (2022) JFQA, my locked
spec items are:

SAMPLE
- Universe: U.S. companies, COMPUSTAT Quarterly, 2010Q1-2016Q4
- Drop utility + financial firms (SIC ranges in Table C1 supplementary)
- Drop firms with market value OR book assets < $10M
- Baseline N = 41,630 firm-quarters

β^UK ESTIMATION (Section IV.A.1, eq 13)
- Static per-firm OLS over 2010M1-2014M12 (60 monthly obs/firm)
- vol(r_it) = α_i + β_i^UK · vol(FTSE100_t) + θ · CONTROLS_t + ε
- CONTROLS = vol(SP500) + vol(FX£)
- Sources: CRSP firm equity + Bloomberg FTSE100 + Bloomberg USD/GBP
- Tercile cuts on NONNEGATIVE β^UK only:
    TREATED  >  0.68 → 449 firms
    CONTROL  <  0.28 → 360 firms

10-K CLASSIFIER (Section IV.A.2)
- Filing year: 2015 (Mar-Jun)
- Keywords: 9 total (3 primary + 6 subsumed via fn 14)
- TREATED: >5 entries → 807 firms
- CONTROL: =0 entries → 433 firms
- Item scope: NOT IN PAPER → F1D default = whole 10-K

DiD MODEL (Section IV.C, eq 14)
- Y_it = α + δ(POST × HIGH) + θ·CONTROLS_{i,t-1} + FIRM + IND_FIC100×QUARTER + ε
- POST = 1 if t ∈ {2016Q3, 2016Q4}
- HIGH = top-tercile β^UK (col 2) OR >5 10-K entries (col 3); separate specs
- Sample = full 2010Q1-2016Q4 panel (~21 avg quarters/firm), unbalanced
- Controls (1Q-lagged): 5 macro + 5 firm + 1 add'l (1Q-ahead consensus EPS forecast)
- FE: FIRM + Hoberg-Phillips FIC100 INDUSTRY × calendar-quarter
- SE: double-cluster firm + calendar-quarter
- Variables winsorized 1% level

CASH DIDIT RESULT (Table 8 = THE TARGET)
- β^UK tercile col 1: POST×HIGH_β^UK = +0.231*** (SE 0.059), N=17,170, R²=0.21
- 10-K col 2: POST×HIGH_10K = +0.357*** (SE 0.062), N=24,195, R²=0.24
- DV: CHE / lag(AT − CHE) [BKS net-assets, per Table 8 footer]

ROBUSTNESS LADDER
- FX exposure: Table 9 (4 augmentations × 2 treatments — all preserve sig)
- Financial constraints: Table 10 (4 augmentations — all preserve sig)
- Automation: Table 11 (CZ-level + 10-K-keyword measures — preserve sig)
- Trump-exclusion: Table 12 cols 1-4 (preserve sig)
- Cameron + Debt Ceiling falsifications: Table 12 cols 5-8 (NS as expected)
- Other-country falsification: Table 13 (UK + EU sig; CHN/MEX/JPN/IND/BRA NS)

PSM + parallel trends: in supplementary Tables C2-C5 + Figure C1.

QUESTION: are there ANY important details for replication purposes that
my spec is missing? Specifically — quote any verbatim sentences anywhere
in the paper or supplementary that describe:
- Compustat variant (NA / Industrial / Financial Services / global)
- Currency requirements (USD only? exchange-rate-hedged?)
- Primary stock listing requirements
- Active-firm requirements (consecutive quarters?)
- Treatment of mergers, spin-offs, delistings during sample period
- Any other variable transformations beyond winsorization
- Estimation library/option specifics (Stata reghdfe? OLS-with-cluster?)
- Auxiliary checks not in headline tables

Quote verbatim with PDF page (1-45) + journal page.

If silent on any sub-question, say "NOT IN PAPER" — I will use F1D defaults.
```

---

## OBSOLETE: NLM verification queries — chunks 2-3 (Q5-Q9, REPLACED by unified batch)

(Q5-Q9 above subsumed by unified batch above. Don't run Q5-Q9. The unified batch is the canonical source going forward.)

---

## ✅ Brexit unified-batch reconciliation (2026-05-08 PM-late+3h)

Sina ran Q-A through Q-D in NotebookLM `f1d` notebook. Verbatim responses returned. Reconciliation:

### Q-A — CASH definition disambiguation ✅ ALL LOCKED

| Sub-item | NLM verdict | PDF programmatic verify | Status |
|----------|-------------|--------------------------|--------|
| (1) Table 8 footer applies to eq (14) | ✅ confirmed verbatim "Table 8 reports output from equation (14)" | ✅ matched | LOCKED |
| (2) Verbatim CASH def | "CASH is defined as total cash holdings divided by lagged total assets net of cash holdings" | ✅ matched | LOCKED |
| (3) Parsing | lag(AT − CHE) [BKS-style] per grammatical reading | ✅ same parsing | LOCKED |
| (4) Numerator components (CHE / CHE+STI / + securities) | NLM silent — "no additional sentence" | paper silent | F1D default = Compustat **#CHEQ** (which is cash + STI combined) |

**LOCKED CASH DV for replication**: `CHEQ_t / lag(ATQ - CHEQ)` — BKS net-assets style.

### Q-B — SALES_GROWTH ✅ LOCKED (with correction to spec)

NLM verbatim: "SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales" → **quarterly SALES, not EPS**.

Programmatic PyMuPDF text extract confirms: PDF p.21 (j.3198) Table 1 footer reads: "SALES_GROWTH is defined as the year-on-year percentage change in **quarterly sales**."

**Spec correction applied**: my prior visual reading of "quarterly EPS" was wrong. No typo. SALES_GROWTH IS sales-based.

✅ **LOCKED**: SALES_GROWTH = year-on-year % change in quarterly sales (Compustat #SALEQ).

### Q-C — SIC ranges + Table C1 supplementary ⚠️ DEFERRED to F1D default

NLM verdict: "The exact Supplementary Material containing Table C1 is not included in the provided sources... You may need to independently verify or upload the supplementary file."

Sina's NotebookLM does not have JFQA Cambridge Core supplementary uploaded.

**Locked F1D default**:
- Utility firms: SIC 4900-4999 (electric, gas, sanitary, communications)
- Financial firms: SIC 6000-6999 (depository institutions, securities, insurance, real estate, holding companies)
- Other filters: F1D defaults (10M$ size cutoff already locked from main paper p.3192)

⚠️ Open: if Table C1 is later acquired (Cambridge Core supplementary download), revisit SIC ranges.

### Q-D — Catch-all ✅ MOSTLY LOCKED + 1 NEW finding

| Sub-item | Verdict | Source |
|----------|---------|--------|
| Compustat variant | ✅ "COMPUSTAT Quarterly North America Fundamentals" | NLM verbatim, j.3197 (Table 1 footer); confirmed PDF programmatic |
| Currency requirements | ✅ NOT a sample filter; FX hedging accounted for via controls | j.3208 (Section VI.A) verbatim "all firms in our sample report using derivatives to hedge against FX risk" |
| Primary stock listing | ⚠️ NOT IN PAPER (CRSP-based universe; no exchange filter specified) | F1D default = CRSP-Compustat merged sample (no listing-exchange filter) |
| Active-firm requirements | ⚠️ NOT IN PAPER (likely Table C1) | F1D default = no minimum-quarter requirement |
| Mergers/spin-offs/delistings | ⚠️ NOT IN PAPER (likely Table C1) | F1D default = standard CRSP delisting handling |
| Variable transforms (beyond winsorization) | ✅ SIZE = ln(AT); CONSENSUS_EARNINGS_FORECAST standardized; PROFITS = quarterly Δ(OIBDP/Sales); all winsorized 1% | NLM + PDF |
| Estimation library | ⚠️ NOT IN PAPER (no Stata/SAS/R specified) | F1D default = `linearmodels.PanelOLS` with double-clustered SE |
| Auxiliary checks beyond headlines | ✅ Footnote 17 (sig-positive β^UK alt threshold) + **Footnote 25 NEW**: Hoberg-Moon 2017 Offshoring Index intersection | PDF p.16 (j.3193) fn 17; PDF p.28 (j.3205) fn 25 |

**NEW FINDING from Q-D — Hoberg-Moon 2017 Offshoring Index 3rd treatment definition:**

Verbatim from PDF p.29 (j.3206), Table 6 description:
> "the final specification, the treatment group consists of firms with scores of greater than 5 on the Hoberg and Moon (2017) U.K. Offshoring Index summed up over years 2010–2014, considering only output offshoring activities, whereas the control group is made of firms with scores of 0 on this index."

**Interpretation**: Brexit paper has THREE treatment definitions, not just two:
1. Top-tercile β^UK (449 firms; market-based)
2. >5 vs 0 Brexit 10-K mentions in 2015 (807/433 firms; text-based)
3. **>5 vs 0 Hoberg-Moon UK Offshoring Index summed over 2010-2014, OUTPUT only** (text-based; INVESTMENT outcome only; channel decomposition)

For OUR cash-DiD replication: we only need treatments 1 + 2 (cash result is in Table 8 with treatments 1 + 2). Hoberg-Moon Offshoring is an Investment-channel decomposition only, NOT applied to cash.

✅ **NOTED** in spec for completeness; not blocking for cash replication.

### Calibration: NLM accuracy this batch

| Citation given | NLM said | Actual (programmatic) | Match? |
|----------------|----------|------------------------|--------|
| Q-A.1 Table 8 → eq 14 | "PDF page 31, Journal page 3208" | PDF p.31 = j.3208 ✓ | ✅ |
| Q-A.2 cash def | "PDF page 31, Journal page 3208" | PDF p.31 = j.3208 ✓ | ✅ |
| Q-D.1 Compustat NA | "PDF page 20, Journal page 3197" | PDF p.20 = j.3197 ✓ | ✅ |
| Q-D.6 SIZE = ln(AT) | "PDF page 20, Journal page 3197" | PDF p.21 = j.3198 (Table 1 footer) | ⚠️ NLM 1-page early on Table 1 footer |
| Q-D.6 PROFITS def | "PDF page 31, Journal page 3208" | PDF p.31 = j.3208 ✓ | ✅ |
| Q-D.8 fn 25 Hoberg-Moon | "PDF page 28, Journal page 3205" | PDF p.28 = j.3205 ✓ | ✅ |

**Conclusion**: NLM citations are USUALLY accurate when explicit PDF-page-number demand is in the query. Occasional 1-page-early drift remains on Table 1 footer item. **Discipline confirmed**: keep demanding PDF page (1-45) AND journal page in queries; cross-check programmatically when conflicts arise.

### Brexit verdict — POST FULL VERIFICATION ✅ GO

All locked spec items + F1D defaults documented. 0 deal-breakers surfaced. Cash-as-auxiliary status remains the only documented caveat — handle via §III.E.4 prose framing.

**Brexit replication can proceed.** Phase 1 builders unblocked.

Next paper: Boasiako, O'Connor Keefe (2020) EFM Data Breaches.

---

# PAPER 2 — Boasiako, O'Connor Keefe (2021) EFM

**File:** `docs/papers/boasiako_oconnor_keefe_2020_databreach_efm.pdf`
**Citation:** European Financial Management, Vol. 27, Issue 3 (2021), pp. 528–551 (©2020 online)
**DOI:** 10.1111/eufm.12289
**Title (verbatim p.528):** "Data breaches and corporate liquidity management"
**Authors:** Kwabena A. Boasiako (Victoria University of Wellington), Michael O'Connor Keefe (corresponding)
**Pages:** 24 PDF pages = j.528-551 (PDF p.N = j.(527+N))
**PDF read complete:** 2026-05-08 PM-late+4h (full single-pass per workflow discipline)

---

### B1. Sample — Section 3.1 (PDF p.7 = j.534) ✅

**Disclosure Law sample (eq 1) verbatim:**
> "we collect initial firm-level data from the merged Center for Research in Security Prices (CRSP)/Compustat database for the period 1997-2015. This period covers the majority of the years in which the states passed data breach disclosure laws. Our sample period begins 5 years before California passed the first state-level data breach disclosure law, in 2002, and ends 5 years after Mississippi passed a similar law, in 2010. Following prior literature (Bates et al., 2009; Opler et al., 1999), we exclude all financial firms—that is, those with Standard Industrial Classification (SIC) codes 6000-6999—because their cash holdings include inventories of marketable securities and they are also required to meet statutory capital requirements. We exclude utility companies (SIC codes 4900-4999) because their cash holdings are possibly subject to regulatory supervision in some states. We further drop observations with negative or missing total book assets. This yields a final sample of 56,646 firm-year observations."

✅ **LOCKED:**
- Disclosure-law sample: **1997-2015** (annual)
- Source: merged CRSP/Compustat
- Industry exclusions: **SIC 6000-6999** (financial) + **SIC 4900-4999** (utility)
- Drop negative/missing AT
- N = **56,646 firm-year observations**

**Data Breach sample (eq 2) verbatim (PDF p.7-8 = j.534-535):**
> "Next, to examine the effect of actual data breaches on corporate cash holdings, we obtain data on data breaches from a chronological listing of disclosed data breaches available from the Privacy Rights Clearinghouse (PRC) for the period 2005-2018. ... We identify 329 nonfinancial business firms as having disclosed a data breach over the 2005-2018 sample period."

✅ **LOCKED:**
- Data-breach sample: **2005-2018** (annual)
- Source: Privacy Rights Clearinghouse (PRC) — `https://www.privacyrights.org`
- N = **329** firms with breach event disclosed; **42,893** firm-year observations total
- Manually merged with CRSP/Compustat

### B2. Disclosure Law DiD — Equation (1) (PDF p.8 = j.535, Section 3.2) ✅

```
   ┌────────────────────────────────────────────────────────────────────┐
   │   Cash_{i,s,t} = α + β · Disclosure_Law(0/1)_{s,t} + γ · X_{i,s,t} │
   │              + θ_s (state FE) + δ_t (year FE)                      │
   │              + ρ_j (industry FF49 FE) + v_i (firm FE) + ε         │   (1)
   └────────────────────────────────────────────────────────────────────┘
```

Verbatim:
> "where i, s, and t index firm, state, and time, respectively. The dependent variable, Cash, is cash and marketable securities scaled by total book assets; **Disclosure Law(0/1)_{s,t} is a dummy variable that switches to one the year after the focal state passed the disclosure law**; X_{i,s,t} is a vector of controls; θ_s represents a set of state dummies that account for state-level unobservable factors that could be correlated with the data breach disclosure laws, and thus bias our estimates; δ_t represents year dummies to control for secular shocks in cash holdings coinciding with the passage of the disclosure laws; and ρ_j and v_i capture industry and firm fixed effects, respectively. The term ε_{i,s,t} is a random error term. **We cluster standard errors by state, because the treatment is defined at the state level.**"

✅ **LOCKED Eq (1):**
- DV: Cash = (cash + marketable securities) / total book assets [BoY]
- Treatment: Disclosure_Law(0/1)_{s,t} = 1 the **YEAR AFTER** focal state passed law (Y+1 timing)
- FE: state + year + industry (FF49) + firm (varies by spec)
- SE clustering: by **STATE** (cols 1-4 baseline); two-way state+year (col 5 alternative); first differences (col 6 alternative)
- Footnote 5: "The industry dummies are constructed based on the 49-industry classification of Fama and French (1997)."

### B3. State assignment — by HQ state (PDF p.8 = j.535, verbatim) ✅

> "state-level disclosure laws charge firms operating within the state (with data breach laws) with the responsibility of disclosing data breaches. Firms can operate in additional states besides their headquarters state and can thus be partly exposed to a data breach disclosure law before their home state passing a similar law. However, **focusing on the states in which firms are headquartered is a conservative approach, since it essentially downward biases β in Equation (1), which should result in an underestimation of our treatment effect**. In other words, firms that are partly pre-exposed to a data breach disclosure law will have a weaker reaction when a similar law is passed in their home state."

✅ **LOCKED:** State assignment = **HQ state** (Compustat ADDZIP/STATE field). Conservative downward bias acknowledged.

### B4. Data Breach DiD — Equation (2) (PDF p.8 = j.535, Section 3.2) ✅

```
   ┌──────────────────────────────────────────────────────────────────┐
   │   Cash_{i,t} = α + β · Breach(0/1)_t + γ · X_{i,t}             │
   │            + ρ_j (industry FE) + δ_t (year FE) + ε              │   (2)
   └──────────────────────────────────────────────────────────────────┘
```

> "where Breach(0/1) is a dummy variable set to one if a firm i discloses a data breach in time t; and zero otherwise. All other variables maintain their previous definitions, and **robust standard errors are estimated by clustering at the firm level**."

✅ **LOCKED Eq (2):**
- Treatment: Breach(0/1)_t = 1 if firm i year t discloses breach
- FE: industry FF49 + year (+ firm FE in some specs)
- SE clustering: by **FIRM** (different from Eq 1's state-cluster)

### B5. Controls + Winsorization (PDF p.9 = j.536, Section 3.3) ✅

Verbatim:
> "We follow the literature (Bates et al., 2009; Opler et al., 1999) in our empirical testing and control for several variables that affect firm cash policy. Specifically, we control for **Firm Size, Firm Age, Book Leverage, Market-to-book, Cash Flow, Capital Expenditure, Acquisition Expenditure, Dividend Paying Firms(0/1), R&D Expenditure, Net Working Capital, and Industry Cash Flow Volatility**. The definitions of all the variables are detailed in the Appendix. We winsorize all variables at the 1st and 99th percentiles to minimize the influence of outliers."

✅ **LOCKED CONTROLS (11 total):**
1. Firm Size = log(AT)
2. Firm Age = log(years_in_CRSP_Compustat)
3. Book Leverage = (DLC + DLTT) / AT
4. Market-to-book = (AT − BVE + MVE) / AT
5. **Cash Flow** ⚠️ "earnings after interest, dividends, and taxes but before depreciation" / AT — non-standard wording; need NLM for exact Compustat formula
6. Capital Expenditure = CAPX / lag(AT_BoY) (BoY scaling)
7. Acquisition Expenditure = AQC / lag(AT_BoY)
8. Dividend Paying Firms(0/1) = 1 if pays dividends in year
9. R&D Expenditure = XRD / lag(AT_BoY)
10. **Net Working Capital** ⚠️ "ratio of net working capital to net assets" — denominator NOT AT; Q for NLM
11. **Industry Cash Flow Volatility** ⚠️ "SD of industry-AVERAGE cash flows for previous 10 years (≥3 yrs required)" — σ over time of industry-mean (not firm-σ averaged)

⚠️ Winsorize 1% both tails.

### B6. Variable Definitions — Appendix Table A1 (PDF p.24 = j.551) ✅

Verbatim from Appendix A:
- **Cash**: "Cash and marketable securities scaled by total book assets at the beginning of the year"
- **External Debt Financing**: (DLTIS − DLTR) / AT_BoY
- **External Equity Financing**: (SSTK − PRSTKC) / AT_BoY
- **Disclosure Law(0/1)**: "1 for periods after the enactment of the state-level data breach notification laws, and 0 otherwise"
  - ⚠️ Section 3.2 says "year after" passage; Table A1 says "after enactment". Y+1 vs Y assignment ambiguous — verify NLM.
- **Firm Age**: log(years_in_CRSP_Compustat)
- **Market-to-book**: (AT − BVE + MVE) / AT
- **Firm Size**: log(AT)
- **Book Leverage**: (DLC + DLTT) / AT
- **Cash Flow**: "earnings after interest, dividends, and taxes but before depreciation" / AT — non-standard
- **Capital Expenditure**: CAPX / AT_BoY
- **Acquisition Expenditure**: AQC / AT_BoY
- **Dividend Paying Firms(0/1)**: 1 if firm pays dividends; 0 otherwise (incl. missing → 0)
- **R&D Expenditure**: XRD / AT_BoY
- **Net Working Capital**: NWC / NET_ASSETS — denominator unspecified Compustat-side
- **Industry Cash Flow Volatility**: σ of industry-AVERAGE cash flows over prior 10 years (≥3 yrs required)

### B7. Headline Results — Table 2 Disclosure Law (PDF p.11 = j.538) ✅

| Spec | Disclosure Law(0/1) | SE | FE | N | Adj R² |
|------|---------------------|------|-----|---|--------|
| Col 1 (year+ind+state FE) **= BASELINE** | **+0.0076** ** | (0.0031) | year+ind+state | 56,646 | 0.4939 |
| Col 2 (year+firm FE) | +0.0056** | (0.0027) | year+firm | 56,646 | 0.0691 |
| Col 3 (excl California — 18% of obs) | +0.0032 NS | (0.0042) | year+ind+state | 47,526 | 0.4658 |
| Col 4 (excl 2007-2009 crisis) | +0.0078** | (0.0038) | year+ind+state | 48,551 | 0.5083 |
| Col 5 (two-way SE state+year) | +0.0076*** | (0.0028) | year+ind+state | 56,646 | 0.4287 |
| Col 6 (first differences) | +0.0026* | (0.0015) | year+ind+state (FD) | 47,117 | 0.1291 |

✅ **HEADLINE: Col 1 baseline β = +0.0076** SE 0.0031** (5% sig)

> "an increase in cash holdings by 0.0076 corresponds to a **3.8% increase from mean cash holdings (0.2008)** and 7.3% of median cash holdings (0.1044) for our sample firms"

⚠️ **Note**: California excluded col 3 → β NS. Footnote 6: "Firms headquartered in California account for 18% of the observations in our sample." Suggests CA-tech-heavy firms drive part of effect.

Other Disclosure Law controls (col 1 verbatim from Table 2 image):
- Firm Size: -0.0110*** (0.0022)
- Market-to-book: +0.0080*** (0.0015)
- Firm Age: -0.0213*** (0.0044)
- Book Leverage: -0.1400*** (0.0206)
- Cash Flow: -0.0049*** (0.0018)
- Capital Expenditure: -0.0709** (0.0280)
- Acquisition Expenditure: -0.0052 NS (0.0048)
- Dividend Paying Firms: -0.0072** (0.0028)
- R&D Expenditure: +0.1909*** (0.0281)
- Net Working Capital: -0.0001 NS (0.0004)
- Industry Cash Flow Volatility: +0.0273*** (0.0068)

### B8. Falsification Test — Table 3 (PDF p.12 = j.539) ✅

> "We follow a two-step process. First, for each year, we randomly assign firms to the various states. Next, we randomly assign the states into the distribution of years when the various disclosure laws were passed."

| Spec | Disclosure Law(0/1) | FE | N | Adj R² |
|------|---------------------|-----|----|--------|
| Col 1 | +0.0008 NS (0.0024) | year+ind | 56,272 | 0.4613 |
| Col 2 | +0.0008 NS (0.0023) | year+state | 56,272 | 0.4446 |
| Col 3 | +0.0007 NS (0.0023) | year+ind+state | 56,272 | 0.4938 |
| Col 4 | +0.0008 NS (0.0022) | year+firm | 56,272 | 0.0688 |

✅ **Falsification PASS** — random state-year reassignment all NS as expected.

### B9. Financial Constraint Channel — Table 4 (PDF p.14 = j.541) ✅

> "we sort firms into financially constrained and unconstrained groups based on firm size, firm age, and dividend payout ratio. For each year, we rank the firms over the sample period and categorize firms in the bottom terciles of the size, age, and dividend payout distributions as financially constrained."

| Spec | Interaction term | Coef | SE |
|------|------------------|------|-----|
| Col 1 | Small Firms × Disclosure_Law | **+0.0344** ** | (0.0153) |
| Col 2 | Young Firms × Disclosure_Law | **+0.0216*** | (0.0128) |
| Col 3 | Non-dividend Payer × Disclosure_Law | **+0.0369*** ** | (0.0085) |

✅ **Channel verified**: financial-constraint firms drive cash-buildup response.

### B10. Data Breach Result — Table 6 (PDF p.16 = j.543) ✅

| Spec | Variable | Coef | SE | N | Adj R² |
|------|----------|------|-----|---|--------|
| Col 1 | Breach(0/1)_t | **+0.0299*** ** | (0.0101) | 42,893 | 0.4981 |
| Col 2 | Breach(0/1)_{t-1} | **+0.0282*** ** | (0.0104) | 42,893 | 0.4981 |
| Col 3 | Severe Breach(0/1)_t | **+0.0348** ** | (0.0151) | 42,878 | 0.4982 |
|        | Moderate Breach | +0.0285* | (0.0163) | | |
|        | Low Breach | +0.0224 NS | (0.0170) | | |
| Col 4 | Severe Breach(0/1)_{t-1} | **+0.0379** ** | (0.0187) | 42,866 | 0.4982 |

> "an increase in cash holdings of 0.03 corresponds to a **13.7% increase from mean cash holdings (0.2185)** in the year following the data breach"

✅ **Severity gradient**: Severe > Moderate > Low — supports causal precautionary interpretation.

### B11. External Financing Channel — Table 7 (PDF p.19 = j.546) ✅

| Spec | Variable | Equity (col 1-2) | Debt (col 3-4) |
|------|----------|------------------|------------------|
| Col 1 | Breach(0/1) | -0.0140*** (0.0051) | — |
| Col 2 | Severe/Mod/Low | -0.0228*** / -0.0132 NS / -0.0056 NS | — |
| Col 3 | Breach(0/1) | — | -0.0171*** (0.0048) |
| Col 4 | Severe/Mod/Low | — | -0.0232*** / -0.0179** / -0.0142* |

> "a decrease in External Equity Financing by 0.014 corresponds to a 32% decrease from mean External Equity Financing (0.0436), and a decrease in External Debt Financing by 0.0171 corresponds to a 62% decrease from mean External Debt Financing (0.0275)"

✅ Breached firms cut external financing → cash buildup must come from somewhere → see investment.

### B12. Investment Channel — Table 8 (PDF p.21 = j.548) ✅

| Spec | Variable | CapEx (col 1-2) | Acq (col 3-4) |
|------|----------|------------------|------------------|
| Col 1 | Breach(0/1) | -0.0072** (0.0031) | — |
| Col 2 | Severe/Mod/Low | -0.0092** / -0.0074* / -0.0068 NS | — |
| Col 3 | Breach(0/1) | — | -0.0209*** (0.0040) |
| Col 4 | Severe/Mod/Low | — | -0.0219*** / -0.0211*** / -0.0136* |

> "a decrease in Capital Expenditure by 0.0072 corresponds to an 11.8% decrease from mean Capital Expenditure (0.061), and a decrease in Acquisition Expenditure by 0.0209 corresponds to a 52% decrease from mean Acquisition Expenditure (0.0399)"

✅ Investment cuts substitute for cash buildup; precautionary story complete.

### B13. Conclusion + Channel — Section 6 (PDF p.21-22 = j.548-549) ✅

> "we argue that, holding constant the underlying likelihood of experiencing a data breach, mandatory data breach disclosure laws increase the cash flow risk associated with future data breaches, and **firms build up balance sheet liquidity as a precautionary measure**."

> "The finding is also robust to a dynamic effect estimation that addresses the parallel trends assumption."

✅ **CHANNEL = precautionary** (verbatim). Parallel trends + entropy balancing in Online Appendix.

### B14. Online Appendix location — Footnote 7 (PDF p.11 = j.538) ⚠️

> "The Online Appendix is available at https://sites.google.com/site/mockeefe/Data."

⚠️ **OPEN**: Online Appendix not in Sina's NotebookLM upload. Need to access URL for parallel trends + entropy balancing details.

### B15. Open after full PDF read — for Boasiako unified NLM batch

1. **Cash Flow definition** — "earnings after interest, dividends, and taxes but before depreciation" — Compustat fields? (NI + DP)/AT or (NI − DV + DP)/AT?
2. **NWC scaling** — "ratio of NWC to net assets" — denominator AT−CHE? AT−LIAB? Other?
3. **Industry Cash Flow Volatility** — exact construction: σ-of-industry-mean over 10 years
4. **Disclosure_Law timing** — Section 3.2 "year after" vs Table A1 "after enactment" — Y+1 starting?
5. **Online Appendix accessibility** — parallel trends + entropy balancing details
6. **Cash numerator** — CHE only? Or CH + IVST separately?

---

## ⚡ UNIFIED Boasiako verification batch (post full-PDF read)

**Discipline**: ALL queries demand BOTH **PDF page (1-24 index in uploaded PDF) AND journal page** (528-551 in header). Cross-check detects drift.

```
QUERY A — Cash Flow + Cash (DV) Compustat field formulas

In Boasiako & O'Connor Keefe (2021) EFM Appendix Table A1 [j.551]:

(1) Cash Flow definition: "Ratio of earnings after interest, dividends, and
taxes but before depreciation to book assets"
   What Compustat fields? Likely candidates:
   (a) (NI + DP) / AT — standard "cash flow" form (NI is after taxes; DP added back)
   (b) (NI − DV + DP) / AT — subtracts dividends paid (literal "after dividends")
   (c) (EBITDA − tax − interest − dividends) / AT — fully literal parsing
   The "after dividends" wording is unusual; (a) is standard but doesn't match
   text literally. Confirm exact formula or quote any clarifying text.

(2) Cash (DV) definition: "Cash and marketable securities scaled by total
book assets at the beginning of the year"
   Compustat fields for numerator?
   (a) CHE alone (which is cash + ST investments combined)
   (b) CH + IVST separately
   (c) CHE + IVAEQ (long-term investments — unlikely)
   Confirm "beginning of the year" = lag(AT_t-1).

For each verbatim quote, provide BOTH:
(a) PDF page (1-24 in the uploaded PDF)
(b) Journal page printed in the page header
```

```
QUERY B — NWC scaling + Industry Cash Flow Volatility construction

In Boasiako & O'Connor Keefe (2021) EFM Table A1 [j.551]:

(1) Net Working Capital: "Ratio of net working capital to net assets"
   Numerator: NWC = ACT − LCT (current assets minus current liabilities)?
              Or specific Compustat fields?
   Denominator "net assets": AT − CHE? AT − LIAB? Other?
   Both numerator and denominator are non-standard in cash-holdings literature.
   Confirm exact Compustat formula.

(2) Industry Cash Flow Volatility: "Standard deviation of industry-average
cash flows for the previous 10 years; at least 3 years of observations
required"
   Construction:
   (a) average cash flow ACROSS FIRMS WITHIN INDUSTRY for each year, then
       SD over 10-year window? (industry-time series of means)
   (b) FIRM-σ for each firm, then averaged within industry?
   The wording "industry-AVERAGE cash flows" suggests (a). Confirm.
   Industry classification: FF49 (matched eq 1)? Or different?
   10-year window: rolling or fixed?

For each verbatim quote: PDF page (1-24) AND journal page.
```

```
QUERY C — Disclosure_Law(0/1) timing assignment

Two slightly different statements in Boasiako & O'Connor Keefe (2021) EFM:

(1) Section 3.2 [j.535]: "Disclosure Law(0/1)_{s,t} is a dummy variable that
switches to one **the year after** the focal state passed the disclosure law"
→ Y+1 timing (e.g., CA passes 2002 → dummy=1 starting 2003).

(2) Table A1 Appendix [j.551]: "Disclosure Law(0/1) — 1 for periods after
the enactment of the state-level data breach notification laws, and 0
otherwise"
→ "after enactment" timing — could be Y or Y+1.

CONFIRM operationally:
1. If California passed law in 2002 (year of enactment), when does the
   dummy switch to 1?
   - 2002 (year of passage)
   - 2003 (year after passage = Y+1)
2. Quote any verbatim sentence resolving this ambiguity. Section 3.2 vs
   Table A1.

PDF page (1-24) AND journal page.
```

```
QUERY D — Online Appendix accessibility + parallel trends + entropy balancing

Section 4.1 [j.538] mentions parallel trends test in Online Appendix
(Footnote 7: https://sites.google.com/site/mockeefe/Data).
Section 5.2 [j.545] mentions entropy balancing dynamic-effect estimation
in Online Appendix.

CONFIRM:
1. Is the Online Appendix available in your NotebookLM? (Or just URL link in
   the main paper PDF?)
2. If accessible: quote the EXACT parallel-trends test specification + result
   (timing dummies? event-study form? coefficient on pre-treatment leads?).
3. If accessible: quote the entropy-balancing implementation + dynamic effect
   estimation result.
4. If NOT in NotebookLM, indicate the URL needs separate retrieval.

PDF page (1-24) AND journal page if Online Appendix is in NLM. Otherwise
confirm "Online Appendix not in current NotebookLM sources."
```

```
QUERY E — Catch-all: anything else for replication?

Post my full 24-page PDF read of Boasiako-O'Connor Keefe (2021) EFM, locked
spec:

DISCLOSURE LAW DiD (Eq 1)
- Sample: 1997-2015, CRSP/Compustat, N=56,646 firm-years (annual)
- Exclusions: SIC 6000-6999 + 4900-4999 + missing AT
- DV: Cash = (cash + marketable securities) / AT [BoY]
- Treatment: Disclosure_Law(0/1) Y+1 timing per §3.2 (Y vs Y+1 ambiguous per Table A1)
- State assignment: HQ state (Compustat ADDZIP/STATE)
- FE: state + year + industry (FF49) + firm (varies by spec)
- SE: state-cluster (cols 1-4); two-way state+year (col 5 alt); FD (col 6)
- Winsorize 1% both tails
- 11 controls (3 non-standard: Cash Flow, NWC, Industry CF Vol)

DATA BREACH DiD (Eq 2)
- Sample: 2005-2018, PRC + CRSP/Compustat, N=42,893 firm-years
- Treatment: Breach(0/1) firm-year
- SE: firm-cluster

HEADLINE RESULTS
- Table 2 col 1 (disclosure law): β=+0.0076** SE 0.0031 N=56,646 (3.8% relative ↑)
- Table 6 col 1 (data breach): β=+0.0299*** SE 0.0101 N=42,893 (13.7% relative ↑)
- Table 4 financial-constraint channel: small/young/non-div firms drive effect
- Table 7 external financing channel: equity ↓32%; debt ↓62%
- Table 8 investment channel: capex ↓11.8%; acq ↓52%

QUESTION: are there any spec items missing from my extraction? Specifically —
quote any verbatim sentences anywhere in main text + Appendix + Online
Appendix that describe:

- Compustat variant (NA Fundamentals? Industrial? Annual?)
- Currency requirements (USD only?)
- Stock listing requirements (NYSE/AMEX/NASDAQ? Common stocks only?)
- Active-firm requirements (consecutive years? minimum quarters?)
- Treatment of mergers, spin-offs, delistings during sample
- State-assignment edge cases: HQ moves during sample? IPO firms?
- Multi-state firms (operate in multiple states): how exposure assigned?
  (Section 3.2 says HQ state = conservative bias, but quote any further detail)
- Specific state law-passage year crosswalk source (NCSL? legislative records?
  manually compiled? authors' Online Appendix?)
- Estimation library/specifics
- Whether controls are lagged vs contemporaneous
- Any auxiliary results not in 8 main tables

For each verbatim quote: PDF page (1-24) AND journal page.
If silent on any sub-question, say "NOT IN PAPER" — I will use F1D defaults.
```

---

## ✅ Boasiako unified-batch reconciliation (2026-05-08 PM-late+5h)

Sina ran Q-A through Q-E in NotebookLM `f1d`. Verbatim returned. Programmatic PyMuPDF verify confirmed NLM substance.

### Q-A — Cash Flow + Cash (DV) Compustat formulas ✅ ALL LOCKED

NLM cited Bates et al. (2009) verbatim, applying their formula directly to Boasiako (Boasiako §3.3 says "we follow the literature (Bates et al., 2009; Opler et al., 1999)" — paper-text inheritance valid):

| Variable | Formula | Bates 2009 source |
|----------|---------|-------------------|
| **Cash Flow** | (OIBDP − XINT − TXT − DVC) / AT | "(#13 − #15 − #16 − #21) / #6" Bates 2009 |
| **Cash (DV)** | CHE / lag(AT_BoY) | Bates 2009 #1 / #6 form |

✅ **F1D Compustat fields:** Cash Flow = `(OIBDP_t − XINT_t − TXT_t − DVC_t) / AT_t`; Cash DV = `CHE_t / lag(AT_t-1)`.

### Q-B — NWC + Industry CF Vol ✅ LOCKED (Bates inheritance for NWC denominator)

| Variable | Formula | Confidence |
|----------|---------|------------|
| **NWC** | (ACT − LCT) / (AT − CHE) | Bates/Opler "net assets" convention; NLM-implied; not explicit in Boasiako Table A1 |
| **Industry CF Vol** | σ over 10-year ROLLING of industry-MEAN cash flows | NLM confirms interpretation (a); paper says "industry-AVERAGE" |
| **Industry classification** | FF49 | Footnote 5 confirms FF49 for industry dummies in eq 1; likely same for Industry CF Vol |

### Q-C — Disclosure_Law timing ✅ LOCKED Y+1

**NEW VERBATIM (Table 2 caption PDF p.11 = j.538):**
> "The variable Disclosure Law(0/1) is a dummy that switches to one **the year after** the focal state passes the disclosure law."

This + Section 3.2 [PDF p.8 = j.535] resolves Table A1's vague "after enactment" wording.

✅ **LOCKED**: Disclosure_Law(0/1)_{s,t} = 1 if **calendar_year > year_state_passed_law**; CA passes 2002 → dummy=1 starting **2003**.

### Q-D — Online Appendix ⚠️ DEFERRED

NLM verdict: "Online Appendix not in current NotebookLM sources."

Online Appendix at `https://sites.google.com/site/mockeefe/Data` (Footnote 7 PDF p.11 = j.538). Contains parallel-trends test + entropy-balancing dynamic effect estimation.

⚠️ **F1D builder action**: either (a) WebFetch the Online Appendix separately, (b) skip parallel-trends + entropy verification (use F1D-default standard event-study + EBalance package), or (c) treat as out-of-scope for v1 replication.

### Q-E — Catch-all ✅ MOSTLY LOCKED + 2 CRITICAL FINDINGS

| Sub-item | Verdict | Source |
|----------|---------|--------|
| Compustat variant | NOT IN PAPER → F1D default = NA Annual | NLM confirmed |
| Currency | NOT IN PAPER → F1D default = USD only | NLM confirmed |
| Stock listing | NOT IN PAPER → F1D default | NLM confirmed |
| Active-firm reqs | NOT IN PAPER → F1D default | NLM confirmed |
| M&A treatment | NOT IN PAPER → F1D default | NLM confirmed |
| HQ-state edge cases | NOT IN PAPER → F1D default | locked |
| Multi-state firms | HQ state with conservative bias acknowledged §3.2 | locked |
| **State law crosswalk** | ✅ **NEW: NCSL public URL** | Footnote 3 PDF p.6 = j.533 |
| Estimation library | NOT IN PAPER → F1D default = `linearmodels.PanelOLS` | locked |
| **Lagged vs contemporaneous controls** | ⚠️ **CONTEMPORANEOUS** by paper notation | NLM + programmatic verify |
| Auxiliary results | Online Appendix dynamic effect + entropy balancing | deferred |

#### 🔑 NEW VERBATIM — State law crosswalk source (Footnote 3, PDF p.6 = j.533)

PDF programmatic confirmation:
> "See the various state disclosure laws from the National Conference of State Legislatures, at http://www.ncsl.org/research/telecommunications-and-information-technology/security-breach-notification-laws.aspx."

✅ **LOCKED**: NCSL public URL = source of truth for 50-state law passage years. Replicators acquire crosswalk from NCSL.

#### 🔑 CRITICAL FINDING — Controls are CONTEMPORANEOUS, NOT lagged

Eq (1) uses notation **X_{i,s,t}** without _{t-1} subscript. Programmatic search confirmed: only "lagged" mention in main text is for Breach(0/1)_t vs Breach(0/1)_{t-1} in Eq (2) [PDF p.18 = j.545].

⚠️ **CRITICAL DIFFERENCE FROM BREXIT**: Brexit (Campello 2022) uses **1Q-LAGGED** controls (eq 14 notation θ·CONTROLS_{i,t-1}). Boasiako uses **CONTEMPORANEOUS** controls. F1D builder must respect each paper's convention.

### NLM accuracy this batch

NLM didn't provide PDF page numbers for Boasiako (correctly noted: "the provided document excerpts...do not contain the printed journal page numbers or the PDF page numbers in the text headers"). NLM identified section/footnote anchor correctly. Programmatic verify confirmed all NLM substance via direct PyMuPDF text extract.

### Boasiako verdict — POST FULL VERIFICATION ✅ GO

All 13 spec items locked or NOT-IN-PAPER + F1D default + 1 deferred (Online Appendix).

**Critical caveats locked for F1D builder:**
1. Cash Flow formula = `(OIBDP − XINT − TXT − DVC) / AT` (Bates 2009)
2. NWC denominator = "net assets" = AT − CHE (Bates/Opler convention)
3. Industry CF Vol = σ over time of industry-MEAN cash flows (10-year rolling, FF49)
4. **Controls are CONTEMPORANEOUS** (NOT lagged) — DIFFERENT from Brexit
5. State law data → NCSL public URL (Footnote 3)
6. State assignment by HQ state — Compustat ADDZIP/STATE
7. Online Appendix → fetch separately or use F1D-default parallel-trends + entropy balancing

**Boasiako replication unblocked.** Phase 1 builders may proceed (Boasiako module set: ~3-4 days estimated).

---

# PAPER 3 — Chen, Cheng, Lin, Tang (2017) JAAF

(Pending — start after Boasiako locked.)
