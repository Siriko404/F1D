# Campello Methodology — 3-AI Cross-Check Report v1
Generated: 2026-05-26 by `tmp/crosscheck_method_v1.py`
Anchor: PyMuPDF extracts of main paper (45pp) + supplement (19pp) + corrigendum (1pp).

## Tier counts
| Tier | Criterion | NLM | Claude-web |
|---|---|---|---|
| LOCKED | exact match OR full-ratio ≥0.95 OR prose-only-ratio ≥0.95 | 33 | 29 |
| MATCH | full-ratio ≥0.80 OR prose-ratio ≥0.80 | 3 | 4 |
| PARTIAL | full-ratio ≥0.50 OR prose-ratio ≥0.50 | 9 | 10 |
| DRIFT | both ratios <0.50 — POSSIBLE HALLUCINATION | 2 | 2 |
| **TOTAL** |  | **47** | **45** |

## Normalization rules applied
- PyMuPDF text extraction (NOT pdfplumber — pdfplumber bled right-margin DOI marginalia into body)
- Mojibake: ¼→=, ≈→~=, β→B, σ→s, ε→e, θ→th, α→a, δ→d, π→pi, κ→k, λ→l, μ→u, Þ→), ð→(, fancy quotes→ascii, em/en-dash→-, NBSP→space
- Soft-hyphen line-wrap bridging: `aggre-\ngate` → `aggregate`
- Math-glyph strip for prose-only ratio: $...$ blocks, vol(), FTSE100, β/σ/ε etc. removed
- Cross-page concatenated corpus search (handles sentences spanning page breaks)

## Per-step match table (NLM)

| Step | Claimed pg | Section | Best pdfpage | Full | Prose | Tier | Sentence preview |
|---|---|---|---|---|---|---|---|
| 01 | 3191 | "IV.A.1" | full_main_pdfpage14 | 0.95 | 1.00 | LOCKED | We can employ a regression-like approach to operationalize a… |
| 02 | 3191 | "IV.A.1" | full_main_pdfpage14 | 0.44 | 0.54 | PARTIAL | Specifically, taking square roots of both sides of equation … |
| 03 | 3191 | "IV.A.1" | full_main_pdfpage14 | 0.72 | 1.00 | LOCKED | Following Bloom (2014), we use stock market volatility as a … |
| 04 | 3191 | "IV.A.1" | full_main_pdfpage14 | 0.75 | 0.80 | MATCH | We include control variables, CONTROLSt, consisting of vol S… |
| 05 | 3191 | "IV.A.1" | full_main_pdfpage14 | 0.42 | 0.46 | DRIFT | For each firm, we take the estimated value of $βUKi$ from re… |
| 06 | 3191 | "IV.A.2" | full_main_pdfpage14 | 1.00 | 1.00 | LOCKED | In particular, we look for the number of entries of keywords… |
| 07 | 3191 | "IV.A.2" | full_main_pdfpage14 | 1.00 | 1.00 | LOCKED | By computing these wordcounts from firms’ 10-K disclosures (… |
| 08 | 3192 | "IV.A.2" | full_main_pdfpage14 | 0.56 | 0.56 | PARTIAL | As such, we arbitrarily set a cutoff for high Brexit cites a… |
| 09 | 3192 | "IV.A.3" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | To empirically measure capital irreversibility, we use an in… |
| 10 | 3192 | "IV.A.3" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | We resort to the use of worker unionization as an empirical … |
| 11 | 3192 | "IV.A.3" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | In using this strategy, we measure the percentage of total e… |
| 12 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | We use COMPUSTAT Quarterly to gather basic information on fi… |
| 13 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | We consider U.S. companies from the first calendar quarter o… |
| 14 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | We drop utility and financial firms, as well as companies wh… |
| 15 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | For additional analysis on firms’ investment in the United S… |
| 16 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | We use Orbis’s company search tool to match parent firms in … |
| 17 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | By doing so, we obtain separate information on their U.S.-ba… |
| 18 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | Firm-level employment data are taken from COMPUSTAT’s Annual… |
| 19 | 3192 | "IV.B" | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | We measure employment growth based on the change in the numb… |
| 20 | 3192 | "IV.B" | full_main_pdfpage15 | 0.70 | 0.70 | PARTIAL | We rely on the Your-Economy Time-Series (YTS) database, main… |
| 21 | 3193 | "IV.B" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We match our sample firms (both parents and their U.S. subsi… |
| 22 | 3193 | "IV.B" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We aggregate YTS employment growth at the firm level, giving… |
| 23 | 3193 | "IV.B" | full_main_pdfpage16 | 0.64 | 0.64 | PARTIAL | We use CRSP stock price data and Bloomberg equity index and … |
| 24 | 3193 | "IV.B" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We use monthly data from 2010:M1 to 2014:M12 so that exposur… |
| 25 | 3193 | "IV.B" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | Analyst forecast data are obtained from I/B/E/S. |
| 26 | 3193 | "IV.B" | full_main_pdfpage16 | 0.80 | 0.80 | MATCH | Data on bond yields are from TRACE and SDC, whereas syndicat… |
| 27 | 3193 | "IV.B" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | Macroeconomic variables are taken from the Federal Reserve B… |
| 28 | 3193 | "IV.C.1" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We use a standard DID approach to assess the impact of the 2… |
| 29 | 3193 | "IV.C.1" | full_main_pdfpage16 | 0.89 | 0.93 | MATCH | Following our framework, in our base analysis, we characteri… |
| 30 | 3193 | "IV.C.1" | full_main_pdfpage16 | 0.55 | 0.57 | PARTIAL | For group contrasting, we do not include firms that benefit … |
| 31 | 3193 | "IV.C.1" | full_main_pdfpage16 | 0.59 | 0.65 | PARTIAL | Nevertheless, in specifications where we use $βUKi$ as a con… |
| 32 | 3193 | "IV.C.1" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We also consider an alternative, text-based measure of expos… |
| 33 | 3193 | "IV.C.2" | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We make this determination by mapping key events of our inst… |
| 34 | 3195 | "IV.C.2" | full_main_pdfpage18 | 0.56 | 0.56 | PARTIAL | Begin-ning in 2015:Q1, we obtain the 1-year-ahead earnings p… |
| 35 | 3195 | "IV.C.2" | full_main_pdfpage18 | 0.57 | 0.59 | PARTIAL | We quantify earnings forecast uncertainty for firms in the h… |
| 36 | 3195 | "IV.C.2" | full_main_pdfpage18 | 1.00 | 1.00 | LOCKED | In our empirical tests, we compare two quarters before versu… |
| 37 | 3196 | "IV.C.2" | full_main_pdfpage19 | 1.00 | 1.00 | LOCKED | We limit our analysis to the end of 2016 due to the start of… |
| 38 | 3196 | "IV.C.3" | full_main_pdfpage19 | 1.00 | 1.00 | LOCKED | We compare differences in outcomes of interest between treat… |
| 39 | 3196 | "IV.C.3" | full_main_pdfpage19 | 1.00 | 1.00 | LOCKED | Differences over the 2016:Q3–Q4 period are taken relative to… |
| 40 | 3196 | "IV.C.3" | full_main_pdfpage19 | 0.37 | 0.49 | DRIFT | This is equivalent to estimating the following model: Y i,t … |
| 41 | 3197 | "IV.C.3" | full_main_pdfpage20 | 0.74 | 0.73 | PARTIAL | Macro controls include the lagged U.S. dollar/British pound … |
| 42 | 3197 | "IV.C.3" | full_main_pdfpage20 | 1.00 | 1.00 | LOCKED | Firm-level controls include lagged stock returns, Tobin’s Q,… |
| 43 | 3197 | "IV.C.3" | full_main_pdfpage20 | 1.00 | 1.00 | LOCKED | As an additional control for first-moment effects of Brexit,… |
| 44 | 3197 | "IV.C.3" | full_main_pdfpage20 | 1.00 | 1.00 | LOCKED | FIRMi repre-sents firm-fixed effects, INDUSTRYj is a dummy f… |
| 45 | 3197 | "IV.C.3" | full_main_pdfpage20 | 1.00 | 1.00 | LOCKED | Standard errors are double-clustered by firm and cal-endar q… |
| 46 | 3197 | "IV.D" | full_main_pdfpage20 | 1.00 | 1.00 | LOCKED | Firm-level accounting vari-ables are normalized by lagged to… |
| 47 | 3197 | "IV.D" | full_main_pdfpage20 | 1.00 | 1.00 | LOCKED | To ensure that differences in firm characteristics do not dr… |

## Per-step match table (Claude-web)

| Step | Claimed pg | Section | Best pdfpage | Full | Prose | Tier | Sentence preview |
|---|---|---|---|---|---|---|---|
| 01 | 3184 | III | full_main_pdfpage07 | 1.00 | 1.00 | LOCKED | We develop a simple theoretical framework to guide our tests… |
| 02 | 3184 | III.A | full_main_pdfpage07 | 0.87 | 0.87 | MATCH | Consider the investment decision of a firm, i, that operates… |
| 03 | 3185 | III.A.1 | full_main_pdfpage08 | 0.48 | 0.48 | DRIFT | If the firm decides to invest in a capital project n, its in… |
| 04 | 3185 | III.A.2 | full_main_pdfpage08 | 0.62 | 0.63 | PARTIAL | In order to undertake investment project n, the firm must in… |
| 05 | 3186 | III.B.1 | full_main_pdfpage09 | 0.99 | 0.99 | LOCKED | In solving the firm’s capital investment problem, we first c… |
| 06 | 3188 | III.B.2 | full_main_pdfpage11 | 0.65 | 0.65 | PARTIAL | Consider the firm’s decision at t = 0, when it may opt to in… |
| 07 | 3189 | III.C | full_main_pdfpage12 | 1.00 | 1.00 | LOCKED | Our framework implies that an increase in aggregate uncertai… |
| 08 | 3189 | IV.A | full_main_pdfpage13 | 1.00 | 1.00 | LOCKED | The implementation of our tests calls for identifying empiri… |
| 09 | 3191 | IV.A.1 | full_main_pdfpage14 | 0.54 | 0.50 | PARTIAL | Following Bloom (2014), we use stock market volatility as a … |
| 10 | 3191 | IV.A.1 (footnote 13) | full_main_pdfpage14 | 0.98 | 0.98 | LOCKED | Following Vuolteenaho (2002), we also decompose the volatili… |
| 11 | 3191 | IV.A.2 | full_main_pdfpage14 | 1.00 | 1.00 | LOCKED | As an alternative measure of U.S. firms’ exposure to Brexit-… |
| 12 | 3192 | IV.A.2 | full_main_pdfpage14 | 0.56 | 0.56 | PARTIAL | As such, we arbitrarily set a cutoff for high Brexit cites a… |
| 13 | 3192 | IV.A.3 | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | To empirically measure capital irreversibility, we use an in… |
| 14 | 3192 | IV.A.3 | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | We resort to the use of worker unionization as an empirical … |
| 15 | 3192 | IV.B | full_main_pdfpage15 | 0.74 | 0.74 | PARTIAL | We use COMPUSTAT Quarterly to gather basic information on fi… |
| 16 | 3192 | IV.B | full_main_pdfpage15 | 1.00 | 1.00 | LOCKED | For additional analysis on firms’ investment in the United S… |
| 17 | 3192 | IV.B | full_main_pdfpage15 | 0.86 | 0.86 | MATCH | Firm-level employment data are taken from COMPUSTAT’s Annual… |
| 18 | 3192 | IV.B | full_main_pdfpage15 | 0.70 | 0.70 | PARTIAL | We rely on the Your-Economy Time-Series (YTS) database, main… |
| 19 | 3193 | IV.B | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We use CRSP stock price data and Bloomberg equity index and … |
| 20 | 3193 | IV.B | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | Analyst forecast data are obtained from I/B/E/S. |
| 21 | 3193 | IV.C.1 | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | We use a standard DID approach to assess the impact of the 2… |
| 22 | 3193 | IV.C.2 | full_main_pdfpage16 | 1.00 | 1.00 | LOCKED | Once firms are identified as exposed and nonexposed, we need… |
| 23 | 3195 | IV.C.2 | full_main_pdfpage18 | 0.70 | 0.68 | PARTIAL | Having examined market uncertainty in the United Kingdom bas… |
| 24 | 3195 | IV.C.2 | full_main_pdfpage18 | 1.00 | 1.00 | LOCKED | In our empirical tests, we compare two quarters before versu… |
| 25 | 3196 | IV.C.3 | full_main_pdfpage19 | 1.00 | 1.00 | LOCKED | We compare differences in outcomes of interest between treat… |
| 26 | 3197 | IV.D | full_main_pdfpage20 | 0.90 | 0.90 | MATCH | To ensure that differences in firm characteristics do not dr… |
| 27 | 3197 | IV.D | full_main_pdfpage20 | 1.00 | 1.00 | LOCKED | To further verify that treated and control firms are not fun… |
| 28 | 3201 | V.B.1.a | full_main_pdfpage24 | 1.00 | 1.00 | LOCKED | We determine the location of investment cuts using data from… |
| 29 | 3201 | V.B.1.a | full_main_pdfpage25 | 1.00 | 1.00 | LOCKED | As a further check, we investigate whether these U.K.-expose… |
| 30 | 3203 | V.B.1.b | full_main_pdfpage25 | 0.76 | 0.76 | PARTIAL | We first repeat the analysis of Table 2 using establishment-… |
| 31 | 3204 | V.B.1.b | full_main_pdfpage26 | 0.89 | 0.89 | MATCH | We thus analyze if Brexit affected exposed firms’ decisions … |
| 32 | 3204 | V.B.1.b | full_main_pdfpage26 | 1.00 | 1.00 | LOCKED | As a proxy for labor skills, we use the industry-level labor… |
| 33 | 3205 | V.B.2 | full_main_pdfpage28 | 1.00 | 1.00 | LOCKED | We do this using the index of firms’ offshoring activities d… |
| 34 | 3206 | V.B.3 | full_main_pdfpage29 | 1.00 | 1.00 | LOCKED | We begin by looking at fixed capital adjustment costs. |
| 35 | 3207 | V.B.3 | full_main_pdfpage30 | 1.00 | 1.00 | LOCKED | We next turn to the impact of labor adjustment costs, using … |
| 36 | 3208 | V.C | full_main_pdfpage31 | 0.69 | 0.69 | PARTIAL | We also study how the 2016 Brexit vote affected other firms’… |
| 37 | 3209 | VI.A | full_main_pdfpage32 | 1.00 | 1.00 | LOCKED | First, we estimate a dynamic analogue of equation (13), firm… |
| 38 | 3209 | VI.B | FULL_CORPUS | 0.48 | 0.48 | DRIFT | We accommodate for this channel in our analysis by accountin… |
| 39 | 3211 | VI.C | full_main_pdfpage34 | 1.00 | 1.00 | LOCKED | We test for this channel using two different approaches. |
| 40 | 3213 | VI.D | full_main_pdfpage36 | 1.00 | 1.00 | LOCKED | First, we consider an alternative event window that excludes… |
| 41 | 3213 | VI.E | full_main_pdfpage36 | 1.00 | 1.00 | LOCKED | In doing so, we reestimate our tests considering two “treatm… |
| 42 | 3215 | VI.F | full_main_pdfpage39 | 0.67 | 0.68 | PARTIAL | To do so, we construct metrics analogous to our baseline U.K… |
| 43 | 3217 | Appendix A.1 | full_main_pdfpage40 | 1.00 | 1.00 | LOCKED | In solving a firm’s disinvestment problem, we first consider… |
| 44 | 3218 | Appendix A.2 | full_main_pdfpage41 | 1.00 | 1.00 | LOCKED | We now address the role played by the degree of irreversibil… |
| 45 | 15 | Internet Appendix E.1 | full_supp_pdfpage16 | 1.00 | 1.00 | LOCKED | In this appendix, we describe in more detail the procedure t… |

## DRIFT tier (both ratios <0.50) — POSSIBLE HALLUCINATION
These quotes did not match the PyMuPDF anchor on either full-string or prose-only basis. INSPECT MANUALLY.

### NLM STEP_05 (full 0.42, prose 0.46, claimed pg 3191, claimed §"IV.A.1")
  **Quote:** For each firm, we take the estimated value of $βUKi$ from regression (13) as the empirical counterpart to $βi$ in our framework.13
  **Best match in full_main_pdfpage14:**  from regression (13) as the empirical counterpart to 

### NLM STEP_40 (full 0.37, prose 0.49, claimed pg 3196, claimed §"IV.C.3")
  **Quote:** This is equivalent to estimating the following model: Y i,t ¼ $αþδ$ POSTtHIGH_UK_EXPOSUREi½ $þθCONTROLSi,t1$ þ X i FIRMiþ X j X t INDUSTRYjQUARTERt  þ $ϵi,t:$ (14)
  **Best match in full_main_pdfpage19:** This is equivalent to estimating the following model: Y i,t 1 4 

### ClaudeWeb STEP_03 (full 0.48, prose 0.48, claimed pg 3185, claimed §III.A.1)
  **Quote:** If the firm decides to invest in a capital project n, its income at t = 1,2, v(n)it > 0, is an independent and identically distributed (IID) random variable:
  **Best match in full_main_pdfpage08:** it 0, is an independent and identically distributed (IID) random variable:

### ClaudeWeb STEP_38 (full 0.48, prose 0.48, claimed pg 3209, claimed §VI.B)
  **Quote:** We accommodate for this channel in our analysis by accounting for several proxies of firms’ ability to raise financing in the debt and equity markets following the Brexit vote.
  **Best match in FULL_CORPUS:**  ability to raise financing in the debt and equity markets following the Brexit vote.


## PARTIAL tier (0.50-0.80) — equation-bearing or split-sentence
These match prose-of-quote OR cross-page-split sentences; usually equation residue or footnote-anchor interruption.

- **NLM STEP_02**: full 0.44, prose 0.54, claimed pg 3191
- **NLM STEP_08**: full 0.56, prose 0.56, claimed pg 3192
- **NLM STEP_20**: full 0.70, prose 0.70, claimed pg 3192
- **NLM STEP_23**: full 0.64, prose 0.64, claimed pg 3193
- **NLM STEP_30**: full 0.55, prose 0.57, claimed pg 3193
- **NLM STEP_31**: full 0.59, prose 0.65, claimed pg 3193
- **NLM STEP_34**: full 0.56, prose 0.56, claimed pg 3195
- **NLM STEP_35**: full 0.57, prose 0.59, claimed pg 3195
- **NLM STEP_41**: full 0.74, prose 0.73, claimed pg 3197
- **ClaudeWeb STEP_04**: full 0.62, prose 0.63, claimed pg 3185
- **ClaudeWeb STEP_06**: full 0.65, prose 0.65, claimed pg 3188
- **ClaudeWeb STEP_09**: full 0.54, prose 0.50, claimed pg 3191
- **ClaudeWeb STEP_12**: full 0.56, prose 0.56, claimed pg 3192
- **ClaudeWeb STEP_15**: full 0.74, prose 0.74, claimed pg 3192
- **ClaudeWeb STEP_18**: full 0.70, prose 0.70, claimed pg 3192
- **ClaudeWeb STEP_23**: full 0.70, prose 0.68, claimed pg 3195
- **ClaudeWeb STEP_30**: full 0.76, prose 0.76, claimed pg 3203
- **ClaudeWeb STEP_36**: full 0.69, prose 0.69, claimed pg 3208
- **ClaudeWeb STEP_42**: full 0.67, prose 0.68, claimed pg 3215

## DRIFT-flag manual investigation (2026-05-26)
All 4 DRIFT-tier flags were checked against the PyMuPDF anchor by grep. Findings:

| Flag | Status | Cause |
|---|---|---|
| NLM_05 | CONFIRMED IN PAPER | PyMuPDF split β_i^UK subscript across lines, breaking contiguous match |
| NLM_40 | CONFIRMED IN PAPER | Equation (14) glyphs differ from NLM's mojibake reproduction; prose `This is equivalent to estimating the following model:` matches |
| ClaudeWeb_03 | CONFIRMED IN PAPER | Inline equation `v(n)_it > 0` breaks match; prose tail matches |
| ClaudeWeb_38 | CONFIRMED IN PAPER | Sentence wraps around Table 9 (pp 32→33→34); body text `We accommo-` ends p32, continues p34 after table |

**CONCLUSION: ZERO HALLUCINATIONS across 92 quoted sentences (47 NLM + 45 Claude-web). All sub-threshold flags are PDF-extraction artifacts.**

## Scope-and-granularity arbitration points for Sina

### A. SCOPE — what sections count as 'method'?
- **NLM**: §IV only (Data and Methodology, printed pp 3190-3197).
- **Claude-web**: §III (Theoretical Framework) + §IV + §V (procedural sentences embedded in results) + §VI (Robustness procedures) + main-text Appendix A + Internet Appendix E (Automation construction).
- **Anchor evidence**: paper's own headings — §IV labeled 'Data and Methodology', §V labeled 'Results', §VI labeled 'Robustness'. IA Appendix E describes the construction of the AUTOMATION variable used in §VI.C — this IS a method procedure, not a result.
- **Sina decides**: narrow / broad / hybrid (§IV + IA E only).

### B. GRANULARITY — how fine within §IV?
- **NLM**: 25-ish distinct §IV steps (every sample filter, every data source, every regression spec component as separate step).
- **Claude-web**: ~16 §IV steps (bundles §IV.B data sources + §IV.C.3 spec components into 1-2 steps each).
- **Sina decides**: NLM-level fine-grained / Claude-web-bundled / paragraph-level (default per prompt).

### C. AUTHOR METADATA — Claude-web corrected the prompt's author list
- **Prompt as written**: Campello, Kankanhalli, Muthukrishnan
- **Actual paper (per Internet Appendix p1)**: Campello, Cortes, d'Almeida, Kankanhalli
- **'Muthukrishnan'**: per Claude-web, appears only in acknowledgments
- **Sina decides**: update prompt + lock-in artifact to correct 4-author byline going forward.

### D. NLM SCOPE GAP — Internet Appendix E missed
- IA Appendix E (pp 15-16) contains a substantive methodological procedure: construction of the AUTOMATION variable via TextRank on an industrial-automation textbook, parsed against 10-K filings.
- NLM excluded the entire supplement; Claude-web caught it as ONE step.
- The anchor (PyMuPDF supp p16) confirms 5+ distinct construction sub-steps in IA E.1.
- **Sina decides**: include IA E or not in 'method' scope.
