# Process Extraction — Prompt 01: Step Overview
**Stage**: 0 — Big-picture enumeration of methodological steps
**Design principle**: Solution-free (discovery, not leading). Verbatim only. Pre-paper-read.
**Run on**: NLM (Campello notebook), Claude-web (Sina attaches PDF), Claude Code (programmatic via pdfplumber on stored extracts)
**Created**: 2026-05-26
**Note to AI**: Read this prompt in full before responding. Do not begin output until you have read every section.

---

## PROMPT (copy-paste below this line, identical to all 3 AIs)

The paper is:
> **Campello, Kankanhalli, Muthukrishnan** — [exact title], [journal], [year], [DOI / URL]
> *(Sina to fill the bracketed metadata before sending.)*

### TASK
Enumerate every distinct step of the AUTHORS' research design / empirical strategy / identification / estimation procedure, in the order the paper presents them.

A **step** is any methodological choice or procedure the authors describe themselves doing — including but NOT LIMITED TO: sample selection, treatment definition, control definition, variable construction within the design, model specification, estimation technique, inference, robustness presented within the methodology section.

Do NOT pre-judge what counts as a step. If you are uncertain whether something qualifies, INCLUDE IT with the uncertainty note (see output format).

### SCOPE — STATE BEFORE LISTING STEPS
Before listing any steps, return a **SCOPE** block:

```
SCOPE:
  included_sections:
    - section_number: <e.g. "III", "3.2", "IV.A">
      section_heading_verbatim: "<copied EXACTLY from the paper>"
      page_range: <start>-<end>
  excluded_sections:
    - section_number: <e.g. "II", "V">
      section_heading_verbatim: "<copied EXACTLY>"
      first_sentence_verbatim: "<one verbatim sentence from that section showing it is data / results / discussion / introduction / conclusion>"
      reason_excluded: <"data description" | "results" | "discussion" | "introduction" | "conclusion" | "literature review" | "other: <verbatim phrase>">
```

### STEP OUTPUT FORMAT (strict — one block per step)

```
STEP_NN:
  identifying_sentence_verbatim: "<one sentence from the paper that names or initiates the step, copied EXACTLY. Preserve capitalization, punctuation, citations, italics, parenthetical references. No paraphrase, no [...] omissions, no ellipsis.>"
  page: <integer — printed page number; if no printed page number is visible, use PDF page number and write "(pdf)" next to it>
  section: <e.g. III.A, 3.2, Section IV>
  paragraph_position: <integer — Nth paragraph within the section, counting from 1 at the section heading>
  uncertainty: <"none" | one verbatim sentence from the paper explaining why you are unsure this qualifies as a methodological step (e.g. boundary with data description, boundary with results, boundary with robustness)>
```

### RULES
1. **Verbatim only.** No paraphrase. No summarization. No "the authors use X" prose.
2. **Do NOT consolidate** adjacent steps the paper describes as separate.
3. **Do NOT invent** steps the paper does not describe.
4. **Do NOT impose ordering** different from the paper's own ordering.
5. **Page numbers** must be the printed page number. If absent, state PDF page + mark "(pdf)".
6. **Multi-page sentences** — give the start page.
7. **Over-include with uncertainty notes** rather than silently omit.

### WHAT TO AVOID
- Do not name an identification design (DiD, IV, PSM, event study, RDD, matching, GMM, OLS, etc.) UNLESS the paper itself uses that exact word in the verbatim sentence you quote.
- Do not assume the methodology lives in any specific section number.
- Do not assume the paper has one design or many — enumerate what the paper actually does.
- Do not pre-classify steps as "main" vs "robustness" — the paper's own scope block decides.
- Do not skip steps because they "seem obvious" or "are standard".

### HONESTY GUARD
If you cannot access the paper, cannot read a specific section, cannot find a step you believe should exist, or cannot determine a page number — STATE THAT EXPLICITLY in the SCOPE block under a new field `access_limitations`. Do not guess. Do not infer from the abstract. Do not fabricate page numbers. Better to return "INCOMPLETE: <reason>" than fabricate.

### NO COMMENTARY
Do not add commentary, introduction, caveats, "I hope this helps", "let me know if you need more", or any prose outside the SCOPE block + STEP_NN blocks + END block.

### END BLOCK
After your final STEP block, write:
```
TOTAL_STEPS_RETURNED: <integer>
EXTRACTION_DATE: <YYYY-MM-DD>
PAPER_ACCESS_METHOD: <"NLM-notebook" | "PDF-attached" | "programmatic-pdfplumber" | "other: <describe>">
```

---

## Expected cross-check after Sina returns 3 responses
- 3 AIs return SCOPE blocks → compare `included_sections` set + page ranges → consensus = locked scope
- 3 AIs return step counts + identifying_sentence_verbatim → compare char-for-char
- Disagreement on step count or sentence text → I open PDF, arbitrate, escalate to Sina if ambiguous
- pdfplumber output (my answer) = ground-truth anchor for verbatim text


/////////////////////////////////
NLM
/////////////////////////////////

SCOPE:
included_sections:
- section_number: "IV"
section_heading_verbatim: "IV. Data and Methodology"
page_range: 3190-3197
excluded_sections:
- section_number: "I"
section_heading_verbatim: "I. Introduction"
first_sentence_verbatim: "On June 23, 2016, voters in the United Kingdom elected to leave the European Union."
reason_excluded: "introduction"
- section_number: "II"
section_heading_verbatim: "II. Background on the 2016 Brexit Referendum"
first_sentence_verbatim: "The 2016 Brexit referendum is said to be rooted in long-standing political and social tensions within Europe, fueled by nationalistic and populist move-ments in the United Kingdom (see, e.g., Becker et al. (2017))."
reason_excluded: "institutional background"
- section_number: "III"
section_heading_verbatim: "III. Theoretical Framework"
first_sentence_verbatim: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."
reason_excluded: "theoretical model"
- section_number: "V"
section_heading_verbatim: "V. Results"
first_sentence_verbatim: "Results from our baseline estimations for investment and employment are shown in Table 2."
reason_excluded: "results"
- section_number: "VI"
section_heading_verbatim: "VI. Robustness"
first_sentence_verbatim: "The Brexit vote was followed by a depreciation of the British pound (9% relative to theU.S. dollar)."
reason_excluded: "robustness"

STEP_01:
identifying_sentence_verbatim: "We can employ a regression-like approach to operationalize an empirical counterpart to $βi.$"
page: 3191
section: "IV.A.1"
paragraph_position: 1
uncertainty: "none"

STEP_02:
identifying_sentence_verbatim: "Specifically, taking square roots of both sides of equation (11), we obtain vol vitð $Þ≈βivol$ V tð $Þþσε$ ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi $2βivol$ V tð $Þσε$ p :(12)"
page: 3191
section: "IV.A.1"
paragraph_position: 1
uncertainty: "none"

STEP_03:
identifying_sentence_verbatim: "Following Bloom (2014), we use stock market volatility as a gauge of aggre-gate uncertainty and estimate equation (12) for each firm i as12 vol ritð Þ¼ $αiþβUKi$ vol FTSE100tð $ÞþθCONTROLStþ ϵit:(13)$"
page: 3191
section: "IV.A.1"
paragraph_position: 2
uncertainty: "none"

STEP_04:
identifying_sentence_verbatim: "We include control variables, CONTROLSt, consisting of vol SP500ð Þ and vol(FX$£) into equation (13) to absorb effects arising through firms’ exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound."
page: 3191
section: "IV.A.1"
paragraph_position: 2
uncertainty: "none"

STEP_05:
identifying_sentence_verbatim: "For each firm, we take the estimated value of $βUKi$ from regression (13) as the empirical counterpart to $βi$ in our framework.13"
page: 3191
section: "IV.A.1"
paragraph_position: 3
uncertainty: "none"

STEP_06:
identifying_sentence_verbatim: "In particular, we look for the number of entries of keywords related to uncertainty about Brexit (“Brexit,” “Great Britain,” and “Uncertainty”) in firms’ disclosures, classifying firms with a “high” number of entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control firms.14"
page: 3191
section: "IV.A.2"
paragraph_position: 1
uncertainty: "none"

STEP_07:
identifying_sentence_verbatim: "By computing these wordcounts from firms’ 10-K disclosures (before the actual vote takes place, yet after the referendum is announced), we build a measure of exposure to the United Kingdom based on what firms consider relevant to communicate to their investors on the eve of the 2016 Brexit vote."
page: 3191
section: "IV.A.2"
paragraph_position: 1
uncertainty: "none"

STEP_08:
identifying_sentence_verbatim: "As such, we arbitrarily set a cutoff for high Brexit cites at more than 5 entries."
page: 3192
section: "IV.A.2"
paragraph_position: 2
uncertainty: "none"

STEP_09:
identifying_sentence_verbatim: "To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016)."
page: 3192
section: "IV.A.3"
paragraph_position: 1
uncertainty: "none"

STEP_10:
identifying_sentence_verbatim: "We resort to the use of worker unionization as an empirical proxy for frictions in labor input."
page: 3192
section: "IV.A.3"
paragraph_position: 2
uncertainty: "none"

STEP_11:
identifying_sentence_verbatim: "In using this strategy, we measure the percentage of total employees who are unionized at the 4-digit SIC level using data from the Bureau of Economic Analysis."
page: 3192
section: "IV.A.3"
paragraph_position: 2
uncertainty: "none"

STEP_12:
identifying_sentence_verbatim: "We use COMPUSTAT Quarterly to gather basic information on firm invest-ment and financial data."
page: 3192
section: "IV.B"
paragraph_position: 1
uncertainty: "none"

STEP_13:
identifying_sentence_verbatim: "We consider U.S. companies from the first calendar quarter of 2010 to the fourth quarter of 2016."
page: 3192
section: "IV.B"
paragraph_position: 1
uncertainty: "none"

STEP_14:
identifying_sentence_verbatim: "We drop utility and financial firms, as well as companies whose market value or book assets are lower than $10 million."
page: 3192
section: "IV.B"
paragraph_position: 1
uncertainty: "none"

STEP_15:
identifying_sentence_verbatim: "For additional analysis on firms’ investment in the United States, we obtain subsidiary-level investment data from the Bureau van Dijk’s Orbis data set (see Cravino and Levchenko (2016))."
page: 3192
section: "IV.B"
paragraph_position: 2
uncertainty: "none"

STEP_16:
identifying_sentence_verbatim: "We use Orbis’s company search tool to match parent firms in our COMPUSTAT sample to ultimate owner firms in Orbis."
page: 3192
section: "IV.B"
paragraph_position: 2
uncertainty: "none"

STEP_17:
identifying_sentence_verbatim: "By doing so, we obtain separate information on their U.S.-based and U.K.-based subsidiaries."
page: 3192
section: "IV.B"
paragraph_position: 2
uncertainty: "none"

STEP_18:
identifying_sentence_verbatim: "Firm-level employment data are taken from COMPUSTAT’s Annual Fun-damentals."
page: 3192
section: "IV.B"
paragraph_position: 3
uncertainty: "none"

STEP_19:
identifying_sentence_verbatim: "We measure employment growth based on the change in the number of employees of the firm."
page: 3192
section: "IV.B"
paragraph_position: 3
uncertainty: "none"

STEP_20:
identifying_sentence_verbatim: "We rely on the Your-Economy Time-Series (YTS) database, maintained by the Business Dynamics Research Consortium at the University of Wisconsin, for information on U.S.-based employment."
page: 3192
section: "IV.B"
paragraph_position: 4
uncertainty: "none"

STEP_21:
identifying_sentence_verbatim: "We match our sample firms (both parents and their U.S. subsidiaries) to YTS primar-ily using tickers, and augment this match through manual searches by firm name."
page: 3193
section: "IV.B"
paragraph_position: 4
uncertainty: "none"

STEP_22:
identifying_sentence_verbatim: "We aggregate YTS employment growth at the firm level, giving a final U.S. establishment-level employment growth sample of 11,345 firm-years."
page: 3193
section: "IV.B"
paragraph_position: 4
uncertainty: "none"

STEP_23:
identifying_sentence_verbatim: "We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-basedmeasure of firm exposure to theUnited Kingdom (see equation (13))."
page: 3193
section: "IV.B"
paragraph_position: 5
uncertainty: "none"

STEP_24:
identifying_sentence_verbatim: "We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events."
page: 3193
section: "IV.B"
paragraph_position: 5
uncertainty: "none"

STEP_25:
identifying_sentence_verbatim: "Analyst forecast data are obtained from I/B/E/S."
page: 3193
section: "IV.B"
paragraph_position: 6
uncertainty: "none"

STEP_26:
identifying_sentence_verbatim: "Data on bond yields are from TRACE and SDC, whereas syndicated loan spreads are drawn fromWRDS– Reuters DealScan."
page: 3193
section: "IV.B"
paragraph_position: 6
uncertainty: "none"

STEP_27:
identifying_sentence_verbatim: "Macroeconomic variables are taken from the Federal Reserve Bank of St. Louis’ FRED database."
page: 3193
section: "IV.B"
paragraph_position: 6
uncertainty: "none"

STEP_28:
identifying_sentence_verbatim: "We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms."
page: 3193
section: "IV.C.1"
paragraph_position: 1
uncertainty: "none"

STEP_29:
identifying_sentence_verbatim: "Following our framework, in our base analysis, we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the $βUKi$ distribution."
page: 3193
section: "IV.C.1"
paragraph_position: 1
uncertainty: "none"

STEP_30:
identifying_sentence_verbatim: "For group contrasting, we do not include firms that benefit from uncertainty in the United Kingdom in the control group (firms with $βUKi$ < 0) as this could lead to overestimation biases attached to the treatment effects we seek to identify."
page: 3193
section: "IV.C.1"
paragraph_position: 1
uncertainty: "none"

STEP_31:
identifying_sentence_verbatim: "Nevertheless, in specifications where we use $βUKi$ as a continuous treatment variable, we relax this restriction and include all values of $βUKi$ .17"
page: 3193
section: "IV.C.1"
paragraph_position: 1
uncertainty: "none"

STEP_32:
identifying_sentence_verbatim: "We also consider an alternative, text-based measure of exposure to Brexit."
page: 3193
section: "IV.C.1"
paragraph_position: 2
uncertainty: "none"

STEP_33:
identifying_sentence_verbatim: "We make this determination by mapping key events of our institutional setting into market-based measures of perceived uncertainty."
page: 3193
section: "IV.C.2"
paragraph_position: 1
uncertainty: "none"

STEP_34:
identifying_sentence_verbatim: "Begin-ning in 2015:Q1, we obtain the 1-year-ahead earnings per share (EPS) forecasts for each firm inour sample and compute themeanand standarddeviationof forecasts."
page: 3195
section: "IV.C.2"
paragraph_position: 3
uncertainty: "none"

STEP_35:
identifying_sentence_verbatim: "We quantify earnings forecast uncertainty for firms in the high and low $βUKi$ groups by constructing1:5-standard-deviation intervals around their group mean forecasts in Figure 4."
page: 3195
section: "IV.C.2"
paragraph_position: 3
uncertainty: "none"

STEP_36:
identifying_sentence_verbatim: "In our empirical tests, we compare two quarters before versus two quarters after the two key Brexit events we have just identified (Feb. 22 and June 23, 2016)."
page: 3195
section: "IV.C.2"
paragraph_position: 4
uncertainty: "none"

STEP_37:
identifying_sentence_verbatim: "We limit our analysis to the end of 2016 due to the start of the Trump administration in Jan. 2017."
page: 3196
section: "IV.C.2"
paragraph_position: 4
uncertainty: "none"

STEP_38:
identifying_sentence_verbatim: "We compare differences in outcomes of interest between treated (HIGH_ UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms."
page: 3196
section: "IV.C.3"
paragraph_position: 1
uncertainty: "none"

STEP_39:
identifying_sentence_verbatim: "Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects."
page: 3196
section: "IV.C.3"
paragraph_position: 1
uncertainty: "none"

STEP_40:
identifying_sentence_verbatim: "This is equivalent to estimating the following model: Y i,t ¼ $αþδ$ POSTtHIGH_UK_EXPOSUREi½ $þθCONTROLSi,t1$ þ X i FIRMiþ X j X t INDUSTRYjQUARTERt  þ $ϵi,t:$ (14)"
page: 3196
section: "IV.C.3"
paragraph_position: 1
uncertainty: "none"

STEP_41:
identifying_sentence_verbatim: "Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia’s Livingstone Survey, the lagged Consumer Sentiment Index from the University ofMichigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia."
page: 3197
section: "IV.C.3"
paragraph_position: 2
uncertainty: "none"

STEP_42:
identifying_sentence_verbatim: "Firm-level controls include lagged stock returns, Tobin’s Q, cash flow, logged assets, and sales growth."
page: 3197
section: "IV.C.3"
paragraph_position: 2
uncertainty: "none"

STEP_43:
identifying_sentence_verbatim: "As an additional control for first-moment effects of Brexit, we add 1-quarter-ahead consensus earnings forecasts to our model."
page: 3197
section: "IV.C.3"
paragraph_position: 2
uncertainty: "none"

STEP_44:
identifying_sentence_verbatim: "FIRMi repre-sents firm-fixed effects, INDUSTRYj is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100),21 and QUARTERt are calendar-quarter dummies."
page: 3197
section: "IV.C.3"
paragraph_position: 2
uncertainty: "none"

STEP_45:
identifying_sentence_verbatim: "Standard errors are double-clustered by firm and cal-endar quarters."
page: 3197
section: "IV.C.3"
paragraph_position: 3
uncertainty: "none"

STEP_46:
identifying_sentence_verbatim: "Firm-level accounting vari-ables are normalized by lagged total assets."
page: 3197
section: "IV.D"
paragraph_position: 1
uncertainty: "none"

STEP_47:
identifying_sentence_verbatim: "To ensure that differences in firm characteristics do not drive our results, we redo all of our tests on propensity score matched samples in which firm-level characteristics are balanced before any esti-mations are conducted."
page: 3197
section: "IV.D"
paragraph_position: 3
uncertainty: "none"

TOTAL_STEPS_RETURNED: 47
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: "PDF-attached"

/////////////////////////////////
Claude Web
/////////////////////////////////

SCOPE:
  paper_identified:
    title_verbatim: "Exporting Uncertainty: The Impact of Brexit on Corporate America"
    authors_verbatim: "Murillo Campello, Gustavo S. Cortes, Fabrício d’Almeida, Gaurav Kankanhalli"
    journal: "Journal of Financial and Quantitative Analysis, Vol. 57, No. 8, Dec. 2022, pp. 3178–3222"
    doi: "10.1017/S0022109022000308"
    files_considered: ["main JFQA article", "Internet Appendix (supplementary)", "Corrigendum doi:10.1017/S0022109022001259"]

  included_sections:
    - section_number: "III"
      section_heading_verbatim: "Theoretical Framework"
      page_range: 3184-3189
    - section_number: "IV"
      section_heading_verbatim: "Data and Methodology"
      page_range: 3189-3197
    - section_number: "V"
      section_heading_verbatim: "Results"
      page_range: 3197-3208
      note: "included only for the procedural / variable-construction / treatment-definition steps embedded within it; results-reporting sentences are not enumerated as steps"
    - section_number: "VI"
      section_heading_verbatim: "Robustness"
      page_range: 3208-3216
      note: "included only for the procedural / variable-construction steps embedded within it"
    - section_number: "Appendix A"
      section_heading_verbatim: "Model Analysis and Results"
      page_range: 3217-3218
    - section_number: "Internet Appendix E"
      section_heading_verbatim: "Measures of Exposure to Automation"
      page_range: 15-16

  excluded_sections:
    - section_number: "I"
      section_heading_verbatim: "Introduction"
      first_sentence_verbatim: "On June 23, 2016, voters in the United Kingdom elected to leave the European Union."
      reason_excluded: "introduction"
    - section_number: "II"
      section_heading_verbatim: "Background on the 2016 Brexit Referendum"
      first_sentence_verbatim: "The 2016 Brexit referendum is said to be rooted in long-standing political and social tensions within Europe, fueled by nationalistic and populist movements in the United Kingdom (see, e.g., Becker et al. (2017))."
      reason_excluded: "other: institutional background"
    - section_number: "IV.D"
      section_heading_verbatim: "Descriptive Statistics"
      first_sentence_verbatim: "Table 1 presents our sample summary statistics."
      reason_excluded: "data description (NOTE: two methodological procedures embedded in this subsection ARE enumerated below as STEP_26 and STEP_27 under the over-inclusion rule)"
    - section_number: "VII"
      section_heading_verbatim: "Concluding Remarks"
      first_sentence_verbatim: "Political uncertainty appears to be a growing phenomenon, seemingly fueled by populism and a rejection of institutions associated with international finance, migration, and trade."
      reason_excluded: "conclusion"
    - section_number: "Appendix B"
      section_heading_verbatim: "Proofs"
      first_sentence_verbatim: "To guarantee the existence of n∗ as characterized by equation (6), it suffices to show that H(n∗) = 0 for some n∗ ∈ [0,N]."
      reason_excluded: "other: mathematical proofs of stated lemmas/propositions (not described design procedures)"
    - section_number: "Corrigendum"
      section_heading_verbatim: "Exporting Uncertainty: The Impact of Brexit on Corporate America—CORRIGENDUM"
      first_sentence_verbatim: "In the original publication of this article, appendices A and B were missing."
      reason_excluded: "other: administrative corrigendum (no methodology)"
    - section_number: "Internet Appendix A"
      section_heading_verbatim: "Model Analysis and Results"
      first_sentence_verbatim: "In solving a firm’s disinvestment problem, we first consider its decision at t = 1."
      reason_excluded: "other: duplicate of main-text Appendix A (steps sourced from main text instead)"
    - section_number: "Internet Appendix B"
      section_heading_verbatim: "Proofs"
      first_sentence_verbatim: "To guarantee the existence of n∗ as characterized by equation (6), it suffices to show that H(n∗) = 0 for some n∗ ∈ [0,N]."
      reason_excluded: "other: proofs (duplicate of main-text Appendix B)"
    - section_number: "Internet Appendix C"
      section_heading_verbatim: "Additional Results and Robustness Tests"
      first_sentence_verbatim: "This figure displays coefficients of investment regressions for the timeline of the main events related to Brexit."
      reason_excluded: "results"
    - section_number: "Internet Appendix D"
      section_heading_verbatim: "Timeline of Brexit Key Events"
      first_sentence_verbatim: "David Cameron is elected with support of the UK Independent Party"
      reason_excluded: "other: event timeline / background"

  access_limitations:
    - "The prompt template named the authors as 'Campello, Kankanhalli, Muthukrishnan'. The actual paper's authors are Campello, Cortes, d’Almeida, and Kankanhalli. 'Pradeep Muthukrishnan' appears only in the article's acknowledgments, not as an author. Extraction proceeds on the actual uploaded paper."
    - "All three PDFs were available as in-context text; paper access was not blocked. PAPER_ACCESS_METHOD = PDF-attached."
    - "Verbatim sentences are reproduced as the paper's true text; obvious PDF text-extraction artifacts (e.g., '¼' for '=', broken superscript/subscript rendering of β^UK_i, mojibake around equations) have been normalized to the intended characters. Equation bodies were not transcribed where the extraction garbled them; identifying sentences were chosen from clean prose."
    - "paragraph_position values are best estimates. The PDF text extraction frequently merges or splits paragraphs around equations, figures, and footnotes, so some counts may be off by one; footnote-anchored steps (e.g., STEP_10) use the paragraph the footnote is attached to."
    - "Section III and Appendix A (the theoretical framework) are enumerated as 'research-design' steps under the over-inclusion rule, but each carries an uncertainty note because they are theoretical-model construction rather than empirical strategy/identification/estimation; a strict reading could exclude them as 'theoretical framework'."

STEP_01:
  identifying_sentence_verbatim: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."
  page: 3184
  section: III
  paragraph_position: 1
  uncertainty: "To this end, we characterize increases in uncertainty using the concept of mean-preserving spread (MPS)."

STEP_02:
  identifying_sentence_verbatim: "Consider the investment decision of a firm, i, that operates for three periods, t = 0, 1, and 2."
  page: 3184
  section: III.A
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_03:
  identifying_sentence_verbatim: "If the firm decides to invest in a capital project n, its income at t = 1,2, v(n)it > 0, is an independent and identically distributed (IID) random variable:"
  page: 3185
  section: III.A.1
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_04:
  identifying_sentence_verbatim: "In order to undertake investment project n, the firm must incur a one-time fixed cost of capital, denoted by FiK(κ,n) = κn, and a one-time fixed cost of labor, denoted by FiL(λ,n) = λn."
  page: 3185
  section: III.A.2
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_05:
  identifying_sentence_verbatim: "In solving the firm’s capital investment problem, we first consider its decision at t = 1."
  page: 3186
  section: III.B.1
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_06:
  identifying_sentence_verbatim: "Consider the firm’s decision at t = 0, when it may opt to invest in a portfolio of R&D projects."
  page: 3188
  section: III.B.2
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_07:
  identifying_sentence_verbatim: "Our framework implies that an increase in aggregate uncertainty reduces firm investments in standard-type projects, and that the effect is modulated by the degree of exposure to uncertainty, βi."
  page: 3189
  section: III.C
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_08:
  identifying_sentence_verbatim: "The implementation of our tests calls for identifying empirical counterparts to the constructs of our theoretical framework."
  page: 3189
  section: IV.A
  paragraph_position: 1
  uncertainty: "none"

STEP_09:
  identifying_sentence_verbatim: "Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i as"
  page: 3191
  section: IV.A.1
  paragraph_position: 2
  uncertainty: "none"

STEP_10:
  identifying_sentence_verbatim: "Following Vuolteenaho (2002), we also decompose the volatility of each firm’s returns into cash flow and discount rate components and reestimate equation (13) with the cash flow component (only) as the dependent variable, obtaining an alternative uncertainty measure, βUK_i,CF."
  page: 3191
  section: IV.A.1 (footnote 13)
  paragraph_position: 2
  uncertainty: "As shown in Table C6, our inferences are unchanged whether using βUKi or βUKi,CF to conduct our tests."

STEP_11:
  identifying_sentence_verbatim: "As an alternative measure of U.S. firms’ exposure to Brexit-induced uncertainty, we develop a textual-search-based metric that is constructed by parsing firms’ 2015 10-K filings."
  page: 3191
  section: IV.A.2
  paragraph_position: 1
  uncertainty: "none"

STEP_12:
  identifying_sentence_verbatim: "As such, we arbitrarily set a cutoff for high Brexit cites at more than 5 entries."
  page: 3192
  section: IV.A.2
  paragraph_position: 2
  uncertainty: "none"

STEP_13:
  identifying_sentence_verbatim: "To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016)."
  page: 3192
  section: IV.A.3
  paragraph_position: 1
  uncertainty: "none"

STEP_14:
  identifying_sentence_verbatim: "We resort to the use of worker unionization as an empirical proxy for frictions in labor input."
  page: 3192
  section: IV.A.3
  paragraph_position: 2
  uncertainty: "none"

STEP_15:
  identifying_sentence_verbatim: "We use COMPUSTAT Quarterly to gather basic information on firm investment and financial data."
  page: 3192
  section: IV.B
  paragraph_position: 1
  uncertainty: "none"

STEP_16:
  identifying_sentence_verbatim: "For additional analysis on firms’ investment in the United States, we obtain subsidiary-level investment data from the Bureau van Dijk’s Orbis data set (see Cravino and Levchenko (2016))."
  page: 3192
  section: IV.B
  paragraph_position: 1
  uncertainty: "none"

STEP_17:
  identifying_sentence_verbatim: "Firm-level employment data are taken from COMPUSTAT’s Annual Fundamentals."
  page: 3192
  section: IV.B
  paragraph_position: 2
  uncertainty: "none"

STEP_18:
  identifying_sentence_verbatim: "We rely on the Your-Economy Time-Series (YTS) database, maintained by the Business Dynamics Research Consortium at the University of Wisconsin, for information on U.S.-based employment."
  page: 3192
  section: IV.B
  paragraph_position: 3
  uncertainty: "none"

STEP_19:
  identifying_sentence_verbatim: "We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13))."
  page: 3193
  section: IV.B
  paragraph_position: 4
  uncertainty: "none"

STEP_20:
  identifying_sentence_verbatim: "Analyst forecast data are obtained from I/B/E/S."
  page: 3193
  section: IV.B
  paragraph_position: 4
  uncertainty: "Data on bond yields are from TRACE and SDC, whereas syndicated loan spreads are drawn from WRDS–Reuters DealScan."

STEP_21:
  identifying_sentence_verbatim: "We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms."
  page: 3193
  section: IV.C.1
  paragraph_position: 1
  uncertainty: "none"

STEP_22:
  identifying_sentence_verbatim: "Once firms are identified as exposed and nonexposed, we need to set the time frame of our DID analysis."
  page: 3193
  section: IV.C.2
  paragraph_position: 1
  uncertainty: "none"

STEP_23:
  identifying_sentence_verbatim: "Having examined market uncertainty in the United Kingdom based on implied options volatility, we set out to verify in our U.S. firm-level data if this period coincided with increased perceived income uncertainty for HIGH_UK_ EXPOSURE firms."
  page: 3195
  section: IV.C.2
  paragraph_position: 4
  uncertainty: "none"

STEP_24:
  identifying_sentence_verbatim: "In our empirical tests, we compare two quarters before versus two quarters after the two key Brexit events we have just identified (Feb. 22 and June 23, 2016)."
  page: 3195
  section: IV.C.2
  paragraph_position: 5
  uncertainty: "none"

STEP_25:
  identifying_sentence_verbatim: "We compare differences in outcomes of interest between treated (HIGH_ UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms."
  page: 3196
  section: IV.C.3
  paragraph_position: 1
  uncertainty: "none"

STEP_26:
  identifying_sentence_verbatim: "To ensure that differences in firm characteristics do not drive our results, we redo all of our tests on propensity score matched samples in which firm-level characteristics are balanced before any estimations are conducted."
  page: 3197
  section: IV.D
  paragraph_position: 2
  uncertainty: "Table 1 presents our sample summary statistics."

STEP_27:
  identifying_sentence_verbatim: "To further verify that treated and control firms are not fundamentally different, we examine the validity of the parallel trends assumption."
  page: 3197
  section: IV.D
  paragraph_position: 2
  uncertainty: "Table 1 presents our sample summary statistics."

STEP_28:
  identifying_sentence_verbatim: "We determine the location of investment cuts using data from Orbis."
  page: 3201
  section: V.B.1.a
  paragraph_position: 1
  uncertainty: "Results in columns 1 and 2 of Table 3 indicate that U.K.-exposed American firms cut investment in their U.S.-located subsidiaries in response to the Brexit vote."

STEP_29:
  identifying_sentence_verbatim: "As a further check, we investigate whether these U.K.-exposed American firms cut investment in their U.K.-based subsidiaries as well."
  page: 3201
  section: V.B.1.a
  paragraph_position: 2
  uncertainty: "Results in columns 3 and 4 of Table 4 suggest that U.K.-exposed American firms cut investment in their U.K.-based subsidiaries even more than they do across their U.S.-based subsidiaries."

STEP_30:
  identifying_sentence_verbatim: "We first repeat the analysis of Table 2 using establishment-level employment growth calculated based on YTS data on the number of employees across all establishments operated by sample firms in the United States."
  page: 3203
  section: V.B.1.b
  paragraph_position: 1
  uncertainty: "Results in columns 1 and 2 of Table 5 suggest that U.K. exposed American firms reduced their employment in the United States following the Brexit vote."

STEP_31:
  identifying_sentence_verbatim: "We thus analyze if Brexit affected exposed firms’ decisions on opening and closing establishments in the United States, which we define as establishment turnover."
  page: 3204
  section: V.B.1.b
  paragraph_position: 1
  uncertainty: "Columns 3 and 4 display negative and significant coefficients, suggesting that U.K.-exposed firms indeed reduce their establishment turnover and confirms our predictions about firm inaction."

STEP_32:
  identifying_sentence_verbatim: "As a proxy for labor skills, we use the industry-level labor skills index (LSI) proposed by Ghaly, Dang, and Stathopoulos (2017)."
  page: 3204
  section: V.B.1.b
  paragraph_position: 2
  uncertainty: "The results in columns 5 and 6 show that U.K.-exposed American firms in Low Skill industries (including food, chemical, and primary metal manufacturing, mining, and clothing retail) cut their employment substantially more (relative to control firms)."

STEP_33:
  identifying_sentence_verbatim: "We do this using the index of firms’ offshoring activities developed by Hoberg and Moon (2017)."
  page: 3205
  section: V.B.2
  paragraph_position: 1
  uncertainty: "The estimate in column 3 indicates that U.S. firms with a high degree of total offshoring activity with the United Kingdom significantly cut their investment relative to U.S. firms with no U.K. offshoring."

STEP_34:
  identifying_sentence_verbatim: "We begin by looking at fixed capital adjustment costs."
  page: 3206
  section: V.B.3
  paragraph_position: 1
  uncertainty: "Columns 1–3 of Table 7 show results on the amplification effect of capital adjustment costs."

STEP_35:
  identifying_sentence_verbatim: "We next turn to the impact of labor adjustment costs, using industry-level unionization rates as a proxy for such costs."
  page: 3207
  section: V.B.3
  paragraph_position: 2
  uncertainty: "Columns 4–6 of Table 7 show that the response of firms in more unionized industries is significantly different from that of firms in less unionized industries."

STEP_36:
  identifying_sentence_verbatim: "We also study how the 2016 Brexit vote affected other firms’ policies, especially their liquidity management."
  page: 3208
  section: V.C
  paragraph_position: 1
  uncertainty: "The positive and highly significant coefficients in columns 1 and 2 of Table 8 show that U.K.-exposed firms increased their cash savings in the face of higher uncertainty induced by the Brexit vote."

STEP_37:
  identifying_sentence_verbatim: "First, we estimate a dynamic analogue of equation (13), firm by firm, over our testing period."
  page: 3209
  section: VI.A
  paragraph_position: 2
  uncertainty: "Results in Table 9 indicate that our inferences on firm responses to the Brexit vote continue to hold even in the presence of various controls for their possible heterogeneous exposures to the depreciation of the British pound."

STEP_38:
  identifying_sentence_verbatim: "We accommodate for this channel in our analysis by accounting for several proxies of firms’ ability to raise financing in the debt and equity markets following the Brexit vote."
  page: 3209
  section: VI.B
  paragraph_position: 1
  uncertainty: "Results in Table 10 indicate that our findings continue to obtain when accounting for possible tightening of firms’ financing costs."

STEP_39:
  identifying_sentence_verbatim: "We test for this channel using two different approaches."
  page: 3211
  section: VI.C
  paragraph_position: 1
  uncertainty: "Table 11 shows our baseline DID specifications augmented with both controls for exposure to automation."

STEP_40:
  identifying_sentence_verbatim: "First, we consider an alternative event window that excludes 2016:Q4 from our treatment evaluation period."
  page: 3213
  section: VI.D
  paragraph_position: 1
  uncertainty: "As shown in columns 1 and 2 of Table 12, results are similar to our baseline estimates in Table 2."

STEP_41:
  identifying_sentence_verbatim: "In doing so, we reestimate our tests considering two “treatment periods” that occurred prior to the 2016 Brexit vote: i) David Cameron’s election as Prime Minister (2015:Q3) and ii) the U.S. Debt Ceiling Crisis of 2011 (2011:Q2–2011:Q4)."
  page: 3213
  section: VI.E
  paragraph_position: 1
  uncertainty: "As shown in columns 5–8 of Table 12, the DID coefficients are statistically insignificant in all such cases."

STEP_42:
  identifying_sentence_verbatim: "To do so, we construct metrics analogous to our baseline U.K. exposure measure, βUK_i, by reestimating equation (13) for developed and emerging markets with relevant trade ties to the United States: European Union, China, Mexico, Japan, India, and Brazil."
  page: 3215
  section: VI.F
  paragraph_position: 1
  uncertainty: "Our main results are unlikely to be driven by American firms’ exposures to events other than the 2016 Brexit vote in the United Kingdom."

STEP_43:
  identifying_sentence_verbatim: "In solving a firm’s disinvestment problem, we first consider its decision at t = 1."
  page: 3217
  section: Appendix A.1
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_44:
  identifying_sentence_verbatim: "We now address the role played by the degree of irreversibility of capital and labor, as captured by their associated fixed costs."
  page: 3218
  section: Appendix A.2
  paragraph_position: 1
  uncertainty: "We develop a simple theoretical framework to guide our tests of the impact of uncertainty on various types of corporate activities."

STEP_45:
  identifying_sentence_verbatim: "In this appendix, we describe in more detail the procedure to construct our text-based measure of automation exposure at the firm level."
  page: 15
  section: Internet Appendix E.1
  paragraph_position: 1
  uncertainty: "none"

TOTAL_STEPS_RETURNED: 45
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: PDF-attached