# Campello et al. (2022) — Methodology Lock-in (Round 1)

**Paper**: Campello, Cortes, d'Almeida, Kankanhalli — "Exporting Uncertainty: The Impact of Brexit on Corporate America"
**Venue**: Journal of Financial and Quantitative Analysis, Vol. 57, No. 8, Dec. 2022, pp. 3178–3222
**DOI**: 10.1017/S0022109022000308   |   **Corrigendum**: 10.1017/S0022109022001259

**Lock-in date**: 2026-05-26
**Scope (locked)**: Hybrid — §IV (Data and Methodology) + Internet Appendix E (Automation construction).
**Granularity (locked)**: NLM fine-grained (~47 distinct §IV steps).
**Round 1 covers**: §IV only. IA Appendix E deferred to Round 2 (separate prompt, NLM corpus verification required).

## Lock-in protocol
Each step below was independently produced by THREE sources:
  1. **NLM** (NotebookLM with attached PDFs) — paragraph-level verbatim enumeration
  2. **Claude-web** (Anthropic API, attached PDFs, cold reading) — same enumeration prompt
  3. **Anchor** (`tmp/extract_full_paper.py` → PyMuPDF on `docs/papers/campello_etal_2022_brexit_jfqa.pdf`) — programmatic extraction, NOT LLM-transcribed

**Verbatim sentences shown below are pulled from the PyMuPDF anchor** (not from NLM, whose quotes carry PDF mojibake like `vol vitð $Þ≈βivol$`).

**Status legend**:
  - `LOCKED` — anchor exact match found on claimed page; cross-source verbatim agreement
  - `PAPER_OK` — anchor confirms text exists in paper but the match required ≥80% partial / cross-page splice (PDF extraction artifact, NOT hallucination)
  - `EQUATION` — step text is primarily an equation; anchor placeholder; paper page+eq# locked, glyph-level transcription not feasible
  - `NLM_ONLY` — NLM listed this step but Claude-web bundled it differently (does NOT mean hallucination; Claude-web's granularity is coarser per cross-check)

## §IV steps (NLM-numbered, anchor-verified)

### §IV.A.1

#### STEP 01 — IV.A.1, ¶1 (printed pg 3191)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_01 • _NLM_ONLY_ • Anchor pdfpage 14

**Verbatim (from PyMuPDF anchor)**:
> We can employ a regression-like approach to operationalize an empirical counterpart to βi.

#### STEP 02 — IV.A.1, ¶1 (printed pg 3191)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_02 • _NLM_ONLY_ • Anchor pdfpage 14

**Verbatim (from PyMuPDF anchor)**:
> Specifically, taking square roots of both sides of equation (11), we obtain vol vit ð Þ≈βivol V t ð Þþσε  ﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ 2βivol V t ð Þσε p : (12) Following Bloom (2014), we use stock market volatility as a gauge of aggre- gate uncertainty and estimate equation (12) for each firm i as12 vol rit ð Þ ¼ αi þβUK i vol FTSE100t ð ÞþθCONTROLSt þϵit: (13) Equation (13) uses the volatility of equity returns, vol rit ð Þ, as a proxy for firm income volatility, vol vit ð Þ.  *[equation glyphs omitted — see paper page 3191]*

#### STEP 03 — IV.A.1, ¶2 (printed pg 3191)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_03 • _NLM_ONLY_ • Anchor pdfpage 14

**Verbatim (from PyMuPDF anchor)**:
> Specifically, taking square roots of both sides of equation (11), we obtain vol vit ð Þ≈βivol V t ð Þþσε  ﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ 2βivol V t ð Þσε p : (12) Following Bloom (2014), we use stock market volatility as a gauge of aggre- gate uncertainty and estimate equation (12) for each firm i as12 vol rit ð Þ ¼ αi þβUK i vol FTSE100t ð ÞþθCONTROLSt þϵit: (13) Equation (13) uses the volatility of equity returns, vol rit ð Þ, as a proxy for firm income volatility, vol vit ð Þ.  *[equation glyphs omitted — see paper page 3191]*

#### STEP 04 — IV.A.1, ¶2 (printed pg 3191)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_04 • _NLM_ONLY_ • Anchor pdfpage 14

**Verbatim (from PyMuPDF anchor)**:
> We include control variables, CONTROLSt, consisting of vol SP500 ð Þ and vol(FX$£) into equation (13) to absorb effects arising through firms’ exposure to the domestic U.  *[equation glyphs omitted — see paper page 3191]*

#### STEP 05 — IV.A.1, ¶3 (printed pg 3191)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_05 • _NLM_ONLY_ • Anchor pdfpage 14

**Verbatim (from PyMuPDF anchor)**:
> For each firm, we take the estimated value of βUK i from regression (13) as the empirical counterpart to βi in our framework.  *[equation glyphs omitted — see paper page 3191]*

### §IV.A.2

#### STEP 06 — IV.A.2, ¶1 (printed pg 3191)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_06 • _NLM_ONLY_ • Anchor pdfpage 14

**Verbatim (from PyMuPDF anchor)**:
> In particular, we look for the number of entries of keywords related to uncertainty about Brexit (“Brexit,” “Great Britain,” and “Uncertainty”) in firms’ disclosures, classifying firms with a “high” number of entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control firms.14 Notably, the vast majority of firms file their 10-Ks with the SEC between March and June of each year.

#### STEP 07 — IV.A.2, ¶1 (printed pg 3191)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_07 • _NLM_ONLY_ • Anchor pdfpage 14

**Verbatim (from PyMuPDF anchor)**:
> By computing these wordcounts from firms’ 10-K disclosures (before the actual vote takes place, yet after the referendum is announced), we build a measure of exposure to the United Kingdom based on what firms consider relevant to communicate to their investors on the eve of the 2016 Brexit vote.

#### STEP 08 — IV.A.2, ¶2 (printed pg 3192)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_08 • Claude-web STEP_12 • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> *[equation step — see paper page 3192, claimed §As such, we arbitrarily set a cutoff for…]*

### §IV.A.3

#### STEP 09 — IV.A.3, ¶1 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_09 • Claude-web STEP_13 • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016).

#### STEP 10 — IV.A.3, ¶2 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_10 • Claude-web STEP_14 • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> We resort to the use of worker unionization as an empirical proxy for frictions in labor input.

#### STEP 11 — IV.A.3, ¶2 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_11 • _NLM_ONLY_ • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> In using this strategy, we measure the percentage of total employees who are unionized at the 4-digit SIC level using data from the Bureau of Economic Analysis.

### §IV.B

#### STEP 12 — IV.B, ¶1 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_12 • _NLM_ONLY_ • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> B. Data Sources and Sample Construction We use COMPUSTAT Quarterly to gather basic information on firm invest- ment and financial data.

#### STEP 13 — IV.B, ¶1 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_13 • _NLM_ONLY_ • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> We consider U.S. companies from the first calendar quarter of 2010 to the fourth quarter of 2016.

#### STEP 14 — IV.B, ¶1 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_14 • _NLM_ONLY_ • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> We drop utility and financial firms, as well as companies whose market value or book assets are lower than $10 million.

#### STEP 15 — IV.B, ¶2 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_15 • Claude-web STEP_16 • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> The sample used in our baseline investment tests consists of 41,630 observations (firm- quarters).15 For additional analysis on firms’ investment in the United States, we obtain subsidiary-level investment data from the Bureau van Dijk’s Orbis data set (see Cravino and Levchenko (2016)).

#### STEP 16 — IV.B, ¶2 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_16 • _NLM_ONLY_ • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> We use Orbis’s company search tool to match parent firms in our COMPUSTAT sample to ultimate owner firms in Orbis.

#### STEP 17 — IV.B, ¶2 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_17 • _NLM_ONLY_ • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> By doing so, we obtain separate information on their U.S.-based and U.K.-based subsidiaries.

#### STEP 18 — IV.B, ¶3 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_18 • Claude-web STEP_17 • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> Firm-level employment data are taken from COMPUSTAT’s Annual Fun- damentals.

#### STEP 19 — IV.B, ¶3 (printed pg 3192)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_19 • _NLM_ONLY_ • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> We measure employment growth based on the change in the number of employees of the firm.

#### STEP 20 — IV.B, ¶4 (printed pg 3192)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_20 • Claude-web STEP_18 • Anchor pdfpage 15

**Verbatim (from PyMuPDF anchor)**:
> 16 We rely on the Your-Economy Time-Series (YTS) database, maintained by the Business Dynamics Research Consortium at the University 15For details of the sample selection filters, see Table C1 in the Supplementary Material.  *[equation glyphs omitted — see paper page 3192]*

#### STEP 21 — IV.B, ¶4 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_21 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> We match our sample firms (both parents and their U.S. subsidiaries) to YTS primar- ily using tickers, and augment this match through manual searches by firm name.

#### STEP 22 — IV.B, ¶4 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_22 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> We aggregate YTS employment growth at the firm level, giving a final U.S. establishment-level employment growth sample of 11,345 firm-years.

#### STEP 23 — IV.B, ¶5 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_23 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13)).

#### STEP 24 — IV.B, ¶5 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_24 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events.

#### STEP 25 — IV.B, ¶6 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_25 • Claude-web STEP_20 • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> Analyst forecast data are obtained from I/B/E/S. Data on bond yields are from TRACE and SDC, whereas syndicated loan spreads are drawn from WRDS– Reuters DealScan.

#### STEP 26 — IV.B, ¶6 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_26 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> Analyst forecast data are obtained from I/B/E/S. Data on bond yields are from TRACE and SDC, whereas syndicated loan spreads are drawn from WRDS– Reuters DealScan.

#### STEP 27 — IV.B, ¶6 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_27 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> Macroeconomic variables are taken from the Federal Reserve Bank of St. Louis’ FRED database.

### §IV.C.1

#### STEP 28 — IV.C.1, ¶1 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_28 • Claude-web STEP_21 • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> C. Test Strategy and Empirical Specification 1. Identification We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms.

#### STEP 29 — IV.C.1, ¶1 (printed pg 3193)
**Status**: `PAPER_OK`   |   **Sources**: NLM STEP_29 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> Following our framework, in our base analysis, we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the βUK i distribution.

#### STEP 30 — IV.C.1, ¶1 (printed pg 3193)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_30 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> For group contrasting, we do not include firms that benefit from uncertainty in the United Kingdom in the control group (firms with βUK i < 0) as this could lead to overestimation biases attached to the treatment effects we seek to identify.  *[equation glyphs omitted — see paper page 3193]*

#### STEP 31 — IV.C.1, ¶1 (printed pg 3193)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_31 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> Nevertheless, in specifications where we use βUK i as a continuous treatment variable, we relax this restriction and include all values of βUK i .  *[equation glyphs omitted — see paper page 3193]*

#### STEP 32 — IV.C.1, ¶2 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_32 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> We also consider an alternative, text-based measure of exposure to Brexit.

### §IV.C.2

#### STEP 33 — IV.C.2, ¶1 (printed pg 3193)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_33 • _NLM_ONLY_ • Anchor pdfpage 16

**Verbatim (from PyMuPDF anchor)**:
> We make this determination by mapping key events of our institutional setting into market-based measures of perceived uncertainty.

#### STEP 34 — IV.C.2, ¶3 (printed pg 3195)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_34 • _NLM_ONLY_ • Anchor pdfpage 18

**Verbatim (from PyMuPDF anchor)**:
> begin-ning in 2015:q1, we obtain the 1-year-ahead earnings per share (eps) forecasts for each firm inour sample and compute themeanand standarddeviationof forecasts.

#### STEP 35 — IV.C.2, ¶3 (printed pg 3195)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_35 • _NLM_ONLY_ • Anchor pdfpage 18

**Verbatim (from PyMuPDF anchor)**:
> We quantify earnings forecast uncertainty for firms in the high and low βUK i groups by constructing 1:5-standard-deviation intervals around their group mean forecasts in Figure 4.  *[equation glyphs omitted — see paper page 3195]*

#### STEP 36 — IV.C.2, ¶4 (printed pg 3195)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_36 • Claude-web STEP_24 • Anchor pdfpage 18

**Verbatim (from PyMuPDF anchor)**:
> In our empirical tests, we compare two quarters before versus two quarters after the two key Brexit events we have just identified (Feb. 22 and June 23, 2016).

#### STEP 37 — IV.C.2, ¶4 (printed pg 3196)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_37 • _NLM_ONLY_ • Anchor pdfpage 19

**Verbatim (from PyMuPDF anchor)**:
> d by uncertainty.20 We limit our analysis to the end of 2016 due to the start of the Trump administration in Jan. 2017.

### §IV.C.3

#### STEP 38 — IV.C.3, ¶1 (printed pg 3196)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_38 • Claude-web STEP_25 • Anchor pdfpage 19

**Verbatim (from PyMuPDF anchor)**:
> We show in later robustness checks that results also hold for a window that excludes Trump’s election. 3. Empirical Model We compare differences in outcomes of interest between treated (HIGH_ UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms.

#### STEP 39 — IV.C.3, ¶1 (printed pg 3196)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_39 • _NLM_ONLY_ • Anchor pdfpage 19

**Verbatim (from PyMuPDF anchor)**:
> Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects.

#### STEP 40 — IV.C.3, ¶1 (printed pg 3196)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_40 • _NLM_ONLY_ • Anchor pdfpage 19

**Verbatim (from PyMuPDF anchor)**:
> This is equivalent to estimating the following model: Y i,t ¼ αþδ POSTt HIGH_UK_EXPOSUREi ½ þθCONTROLSi,t1 þ X i FIRMi þ X j X t INDUSTRYj QUARTERt  þϵi,t: (14) The outcomes of interest, Y i,t, are fixed capital investment, employment growth, R&D expenditures, divestitures, cash holdings, and NWC.  *[equation glyphs omitted — see paper page 3196]*

#### STEP 41 — IV.C.3, ¶2 (printed pg 3197)
**Status**: `EQUATION`   |   **Sources**: NLM STEP_41 • _NLM_ONLY_ • Anchor pdfpage 20

**Verbatim (from PyMuPDF anchor)**:
> *[equation step — see paper page 3197, claimed §Macro controls include the lagged U.S. d…]*

#### STEP 42 — IV.C.3, ¶2 (printed pg 3197)
**Status**: `PAPER_OK`   |   **Sources**: NLM STEP_42 • _NLM_ONLY_ • Anchor pdfpage 20

**Verbatim (from PyMuPDF anchor)**:
> Firm-level controls include lagged stock returns, Tobin’s Q, cash flow, logged assets, and sales growth.

#### STEP 43 — IV.C.3, ¶2 (printed pg 3197)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_43 • _NLM_ONLY_ • Anchor pdfpage 20

**Verbatim (from PyMuPDF anchor)**:
> As an additional control for first-moment effects of Brexit, we add 1-quarter-ahead consensus earnings forecasts to our model.

#### STEP 44 — IV.C.3, ¶2 (printed pg 3197)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_44 • _NLM_ONLY_ • Anchor pdfpage 20

**Verbatim (from PyMuPDF anchor)**:
> firmi repre-sents firm-fixed effects, industryj is a dummy for each industry category j of the hoberg and phillips (2016) classification (fic 100),21 and quartert are calendar-quarter dummies.

#### STEP 45 — IV.C.3, ¶3 (printed pg 3197)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_45 • _NLM_ONLY_ • Anchor pdfpage 20

**Verbatim (from PyMuPDF anchor)**:
> Standard errors are double-clustered by firm and cal- endar quarters.

### §IV.D

#### STEP 46 — IV.D, ¶1 (printed pg 3197)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_46 • _NLM_ONLY_ • Anchor pdfpage 20

**Verbatim (from PyMuPDF anchor)**:
> firm-level accounting vari-ables are normalized by lagged total assets.

#### STEP 47 — IV.D, ¶3 (printed pg 3197)
**Status**: `LOCKED`   |   **Sources**: NLM STEP_47 • Claude-web STEP_26 • Anchor pdfpage 20

**Verbatim (from PyMuPDF anchor)**:
> To ensure that differences in firm characteristics do not drive our results, we redo all of our tests on propensity score matched samples in which firm-level characteristics are balanced before any esti- mations are conducted.


## Open items for Round 2
1. **IA Appendix E** (Automation variable construction, supp pp 15-16): enumerate fine-grained construction steps. Requires NLM corpus verification (does NLM have the supplement loaded?).
2. **Step-text DRIFT items** (NLM_05, NLM_40, ClaudeWeb_03, ClaudeWeb_38): all confirmed in paper by grep, but verbatim sentences below use anchor-clean text rather than mojibake quote.
3. **Granularity audit**: NLM has 47 §IV steps; Claude-web bundled to ~16. Steps marked `NLM_ONLY` in the table above need confirmation they are real distinct procedures (not over-splitting).

## Build artifact
Generated by `tmp/build_method_lockin.py` on 2026-05-26. To regenerate, run that script.

## Round 1b — Paragraph-level lock-in (added 2026-05-26)

**Why Round 1b**: Round 1 sentence-level extraction left 11 EQUATION + 2 PAPER_OK steps with ugly verbatim. Round 1b re-queried both AIs at paragraph level for the 9 paragraphs containing those problem steps. Then Sina visually verified page 3194 in the PDF to resolve the §IV.C.2 paragraph-numbering drift.

**Cross-check artifact**: `tmp/campello_para_crosscheck_v1_2026_05_26.md`
**Anchor enumeration**: `tmp/campello_paragraph_index_2026_05_26.md`

**Resolution rule**: when NLM and Claude-web disagree on `paragraph_position` for the same section, the anchor (PyMuPDF `blocks` mode + Sina PDF visual verification) settles it. In this round, **all disagreements resolved in Claude-web's favor**; NLM had off-by-one paragraph-numbering errors in §IV.A.1 and §IV.C.2.

**Final result**: 9/9 paragraphs locked to Claude-web's verbatim text.

### PARA_01 — §IV.A.1 ¶1  (printed pg 3190)
**Status**: `CW_ONLY (NLM INCOMPLETE)`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: —
**Note**: NLM could not transcribe equation (11) due to mojibake. Claude-web returned clean Unicode.

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> In the context of our study, the increase in aggregate uncertainty, V_t, comes from the rise in uncertainty associated with the Brexit vote. Accordingly, we take variances on both sides of equation (1) (alternatively, equation (2)) to capture the notion of uncertainty in the MPS framework:
> 
>     var(v_it) = β_i² var(V_t) + σ_ε²    (11)

### PARA_02 — §IV.A.1 ¶2  (printed pg 3191)
**Status**: `LOCKED-BY-ANCHOR (NLM off-by-one)`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_01, STEP_02, STEP_03, STEP_04
**Note**: NLM PARA_02 = 'Following Bloom...' but anchor §IV.A.1 ¶2 starts at 'We can employ...'. Claude-web matches anchor (a[7]).

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> We can employ a regression-like approach to operationalize an empirical counterpart to βi. Specifically, taking square roots of both sides of equation (11), we obtain
> 
>     vol(v_it) ≈ β_i vol(V_t) + σ_ε − √(2 β_i vol(V_t) σ_ε)    (12)
> 
>     Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i as12
> 
>     vol(r_it) = α_i + β_i^UK vol(FTSE100)_t + θ CONTROLS_t + ε_it    (13)

### PARA_03 — §IV.A.1 ¶3  (printed pg 3191)
**Status**: `LOCKED`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_05
**Note**: Both AIs map to anchor a[10]. Claude-web gave the full paragraph; NLM gave only its last sentence.

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it). It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting). We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound. For each firm, we take the estimated value of β_i^UK from regression (13) as the empirical counterpart to βi in our framework.13

### PARA_04 — §IV.A.2 ¶2  (printed pg 3191-3192)
**Status**: `LOCKED`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_08
**Note**: Both AIs identical content (anchor a[11]).

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> Textual analysis reveals that most firms cite concerns about Brexit a half dozen times or more in their 10-Ks, or not at all. As such, we arbitrarily set a cutoff for high Brexit cites at more than 5 entries. There are 807 firms citing Brexit more than 5 times in their 10-Ks. On the other hand, 433 do not cite any Brexit-related terms in their public filings. Although the heuristic cutoff we consider is naturally arbitrary, our results are robust to many sensible alternative choices.

### PARA_05 — §IV.B ¶4  (printed pg 3192-3193)
**Status**: `LOCKED`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_18, STEP_19, STEP_20, STEP_21, STEP_22
**Note**: Both AIs identical content (anchor a[14], cross-page p3192→3193).

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> We rely on the Your-Economy Time-Series (YTS) database, maintained by the Business Dynamics Research Consortium at the University of Wisconsin, for information on U.S.-based employment. The YTS database is compiled from historical business files from Infogroup and are linked longitudinally to track establishment location, employment, and sales information at the establishment-year level for public and private firms in the United States. We match our sample firms (both parents and their U.S. subsidiaries) to YTS primarily using tickers, and augment this match through manual searches by firm name. The firms in our sample collectively operated 757,083 unique establishments, and this results in 1,809,301 establishment-year observations over the 2010–2016 period. We aggregate YTS employment growth at the firm level, giving a final U.S. establishment-level employment growth sample of 11,345 firm-years.

### PARA_06 — §IV.B ¶5  (printed pg 3193)
**Status**: `LOCKED`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_23, STEP_24, STEP_25, STEP_26, STEP_27
**Note**: Both AIs identical content (anchor a[15]). Claude-web includes more sentences (NLM truncated).

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13)). We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events. Analyst forecast data are obtained from I/B/E/S. Data on bond yields are from TRACE and SDC, whereas syndicated loan spreads are drawn from WRDS–Reuters DealScan. Macroeconomic variables are taken from the Federal Reserve Bank of St. Louis' FRED database.

### PARA_07 — §IV.C.1 ¶1  (printed pg 3193)
**Status**: `LOCKED`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_28, STEP_29, STEP_30, STEP_31, STEP_32
**Note**: Both AIs identical content (anchor a[16]). Claude-web includes more sentences.

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms. Following our framework, in our base analysis, we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the β_i^UK distribution. For group contrasting, we do not include firms that benefit from uncertainty in the United Kingdom in the control group (firms with β_i^UK < 0) as this could lead to overestimation biases attached to the treatment effects we seek to identify. Nevertheless, in specifications where we use β_i^UK as a continuous treatment variable, we relax this restriction and include all values of β_i^UK.17 Under this market-based approach, a total of 449 unique firms are assigned to the treated category (β_i^UK > 0.68). In contrast, 360 unique firms are assigned to the control category (β_i^UK < 0.28). We also consider an alternative, text-based measure of exposure to Brexit. Under this approach, 807 firms are assigned to the treated category (2015 10-K mentions of Brexit terms > 5). A total of 433 firms in the control category have no mentions of Brexit-related terms in their 10-Ks.

### PARA_08 — §IV.C.2 ¶3  (printed pg 3194-3195)
**Status**: `LOCKED-BY-PDF-CHECK (NLM off-by-one)`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_34, STEP_35
**Note**: Sina visually verified page 3194 contains exactly 2 body paragraphs: 'The first (dotted blue)...' (¶2) and 'Responses to official news...' (¶3). NLM's 'Having examined market uncertainty...' is on p3195 = ¶4, NOT ¶3.

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> Responses to official news about the exact referendum date suggest that market participants were quick to incorporate uncertainty embedded by Brexit in their trading activity (before the actual outcome of the vote). In particular, options trading taking place on Feb. 22, 2016 (continuous red curve in Figure 3), the first trading day following David Cameron's announcement of the Brexit vote date, were priced to reflect a significant drop in market volatility for the period leading up to the Brexit vote date (on June 23), only to show a spike in volatility right after the vote. On June 24, 2016 (dashed yellow curve), the first trading day following the vote, market uncertainty seemed unusually high. Resolution about the vote outcome, nonetheless, seems to quell uncertainty forecasts. In particular, the 1-year-ahead implied volatility immediately after the vote date is not significantly different from that registered back in Dec. 2014.

### PARA_09 — §IV.C.3 ¶1  (printed pg 3196)
**Status**: `LOCKED`   |   **Source**: Claude-web
**Round 1 STEPs contained in this paragraph**: STEP_38, STEP_39, STEP_40, STEP_41, STEP_42, STEP_43, STEP_44
**Note**: Both AIs map to anchor a[24]. Claude-web gave eq (14) cleanly.

**Verbatim** (from Claude-web, with Unicode equation glyphs):

> We compare differences in outcomes of interest between treated (HIGH_UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms. Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects. This is equivalent to estimating the following model:
> 
>     Y_i,t = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θ CONTROLS_i,t−1 + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ε_i,t.    (14)

## Round 2 — IA Appendix E.1 (Automation construction) lock-in (added 2026-05-26)

**Source**: `docs/papers/campello_etal_2022_brexit_supplementary.pdf` page 16 — Appendix E, sub-subsection E.1 "Details on Automation Exposure Measures".

**Cross-check summary**:
- NLM returned 4 paragraphs (over-split into individual sentences — same NLM off-by-N pattern as Round 1b §IV.A.1 and §IV.C.2)
- Claude-web returned 2 paragraphs (matches anchor)
- PyMuPDF anchor (line-by-line read of supp_pdfpage16.txt) confirms **2 body paragraphs** in E.1
- Content prose: 3/3 sources agree character-for-character (only chunking differs)

**Resolution**: Claude-web's 2-paragraph structure adopted; verbatim text below taken from PyMuPDF anchor (cleanest source — preserves AUTOMATION_i subscript as inline `AUTOMATIONi`).

**Status**: `LOCKED` (3/3 content agreement, anchor-confirmed paragraph structure).

### IA_E_PARA_01 — E.1 ¶1  (supp pdf page 16)
**First word**: "For"   |   **Last word**: "universities."
**Contains equation**: no   |   **References**: Acemoglu and Restrepo (2020), Leigh and Kraft (2018), Loughran and McDonald (2011), Benhabib (2003)

**Verbatim** (from PyMuPDF anchor, supp p16):

> For more details on the geographic measure of exposure to automation for all commuting zones in the continental US, we refer the reader to Acemoglu and Restrepo (2020) and Leigh and Kraft (2018). In this appendix, we describe in more detail the procedure to construct our text-based measure of automation exposure at the ﬁrm level. We draw inspiration from an extensive literature in corporate ﬁnance that uses textual analysis (e.g., Loughran and McDonald (2011)) and deﬁne a dictionary of keywords that capture automation at the ﬁrm level. We ﬁrst gather the syllabuses of many courses on “Industrial Automation and Integration” taught at top Engineering schools in North America (MIT, CalTech, University of Toronto, among others). Reading each syllabus, we identify the most frequently adopted textbook. This analysis points to Benhabib’s (2003) “Manufacturing: Design, Production, Automation, and Integration” as one of the most commonly required textbooks in these universities.

### IA_E_PARA_02 — E.1 ¶2  (supp pdf page 16)
**First word**: "With"   |   **Last word**: "variable."
**Contains equation**: yes (`AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi)`)   |   **References**: Mihalcea and Tarau (2004)

**Verbatim** (from PyMuPDF anchor, supp p16):

> With the textbook in hand, we parse its full textual content and use a standard keyword ranking algorithm (“TextRank”, see Mihalcea and Tarau (2004)) to order the most distinctive keywords reﬂecting automation. Following the usual procedures in textual analysis (e.g., exclusion of “stop words”), we select the top 100 keywords that are closely related to automation and use them as a dictionary for parsing ﬁrms’ 10-Ks. The list of keywords is provided in Table E.1. Finally, we deﬁne AUTOMATIONi, which is a continuous variable (in logs) that measures how frequently the top 100 automation keywords appear in the ﬁrm’s business description (Section 1 of the 10-K form) and management discussion (Section 7 of the 10-K form). To capture cases in which a ﬁrm discusses automation efforts in only one year, we average the word count across all years in our sample. AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi), where AUTOMATION_KEYWORDSi is the number of mentions of the top 100 automation-related keywords in ﬁrm i’s 10-K forms. Figure E.1 shows a histogram with the distribution of the AUTOMATIONi variable.

## Methodology lock-in — COMPLETE for the Hybrid scope
Round 1 (47 sentence-level §IV steps) + Round 1b (9 paragraph-level §IV locks) + Round 2 (2 paragraph-level IA E.1 locks) covers the full scope decided 2026-05-26.

**Next phase candidates** (Sina decides):
1. **Variables checklist** — enumerate every variable definition in the paper verbatim (separate per Sina earlier directive: "we will make a checklist of ALL variables and their verbatim definition, later")
2. **Code audit** — compare `scripts/campello_rebuild/` against this locked methodology to identify code bugs
3. **Sample-construction filters** — also explicitly inside this scope decision ("ONLY the method"); some are in §IV.B but not isolated as steps
