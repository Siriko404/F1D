# Process Extraction — Prompt 01b: Paragraph-level reverification (targeted)
**Stage**: Round 1.5 — verbatim reverification of paragraphs that contain the 11 EQUATION-tier and 2 PAPER_OK-tier steps from Round 1 lock-in
**Design principle**: Solution-free, paragraph-level, no prior text given to AIs
**Run on**: NLM (Campello notebook), Claude-web (Sina attaches PDF), Claude Code (pdfplumber/PyMuPDF anchor)
**Created**: 2026-05-26
**Why**: Round 1 sentence-level extraction left 11 steps with equation-glyph residue and 2 with cross-page/footnote PDF-extraction artifacts. Going up to paragraph-level captures the full context cleanly.

---

## PROMPT (copy-paste below this line, identical to all 3 AIs)

The paper is:
> **Campello, Cortes, d'Almeida, Kankanhalli** — "Exporting Uncertainty: The Impact of Brexit on Corporate America" — *Journal of Financial and Quantitative Analysis*, Vol. 57, No. 8, Dec. 2022, pp. 3178–3222 — DOI 10.1017/S0022109022000308

### TASK
For each of the **9 paragraphs** listed below, return the COMPLETE VERBATIM TEXT of that paragraph from the paper, character-for-character.

Each paragraph is identified by **section + paragraph position within section + printed page number**. Locate the paragraph by these coordinates; do not infer or guess from descriptions.

### THE 9 PARAGRAPHS

```
PARA_01: §IV.A.1, paragraph 1, printed page 3191
PARA_02: §IV.A.1, paragraph 2, printed page 3191
PARA_03: §IV.A.1, paragraph 3, printed page 3191
PARA_04: §IV.A.2, paragraph 2, printed page 3192
PARA_05: §IV.B, paragraph 4, printed page 3192-3193 (may span page break)
PARA_06: §IV.B, paragraph 5, printed page 3193
PARA_07: §IV.C.1, paragraph 1, printed page 3193
PARA_08: §IV.C.2, paragraph 3, printed page 3195
PARA_09: §IV.C.3, paragraph 1, printed page 3196
```

### OUTPUT FORMAT (strict)

For each paragraph, return a block:

```
PARA_NN:
  section: <e.g. IV.A.1>
  paragraph_position: <integer — Nth paragraph within the section, counting from 1>
  page: <printed page; if paragraph spans pages, list start-end>
  first_word_verbatim: "<the first word of the paragraph, EXACTLY>"
  last_word_verbatim: "<the last word of the paragraph, EXACTLY (the word immediately before the next paragraph starts)>"
  paragraph_text_verbatim: |
    <COMPLETE paragraph text. Preserve:
       - all sentences in order
       - all in-line equations (write them out symbolically — use Unicode β, σ, ε, θ, ≈, etc., NOT placeholder text)
       - all footnote anchors (e.g., "...firms.14" where 14 is the footnote number)
       - all parenthetical citations (e.g., "(Bloom (2014))")
       - all capitalization, punctuation, italics indicators if present
       - line breaks within the paragraph as single spaces (collapse soft-hyphen word wraps: "aggre-\ngate" → "aggregate")
     Do NOT include:
       - the footnote BODY text (just the anchor number is enough)
       - the page header / running title
       - the page footer / page number>
  contains_equation: <"yes" | "no">
  contains_footnote_anchor: <"yes" | "no">
  uncertainty: <"none" | one verbatim sentence from the paragraph explaining why you are uncertain about its boundaries (e.g., page-spanning ambiguity, embedded equation breaks visual paragraph flow)>
```

### RULES

1. **Verbatim only.** Reproduce the paper's text exactly. No paraphrase, no summary, no reformatting.
2. **Equations**: write them out using Unicode mathematical symbols (β, σ, ε, θ, α, δ, π, κ, λ, μ, ≈, ≤, ≥, ∗). For subscripts/superscripts, write `β_i^UK` or `β_i^{UK}` (LaTeX-style is OK). DO NOT use PDF text-extraction mojibake (no `vol vitð$Þ≈βivol$`).
3. **Soft-hyphen word wraps**: collapse `aggre-\ngate` to `aggregate`. Cross-page hyphens too.
4. **Footnote anchors**: include the number as a trailing digit on the previous word (e.g., `firms.14`).
5. **Do not consolidate paragraphs** that the paper visually separates. If a paragraph is interrupted by an indented equation, treat that as the same paragraph (the prose surrounds the equation).
6. **Paragraph boundaries**: a new paragraph in the printed paper is signaled by indentation of the first line. Treat that as the boundary.

### HONESTY GUARD

If you cannot locate a paragraph, cannot determine its boundaries, cannot reproduce equation glyphs because your text source is corrupted, or are unsure between two adjacent paragraphs — STATE THAT EXPLICITLY in the `uncertainty:` field. Do not guess. Better to return `INCOMPLETE: <reason>` than fabricate.

### NO COMMENTARY

No introduction, no caveats, no "I hope this helps", no closing remarks. Only the 9 PARA_NN blocks + the END block.

### END BLOCK

```
TOTAL_PARAGRAPHS_RETURNED: <integer — should be 9>
EXTRACTION_DATE: <YYYY-MM-DD>
PAPER_ACCESS_METHOD: <"NLM-notebook" | "PDF-attached" | "programmatic-pdfplumber" | "other">
```

---

## Expected cross-check (after Sina returns 3 responses)
- 3 AIs return paragraph_text_verbatim → compare char-for-char (after the same normalization as Round 1)
- 3/3 match → LOCKED at paragraph level
- 2/3 match → FLAGGED; 3rd AI inspected for transcription drift
- ≤1/3 match → HALT; I open PDF, arbitrate
- Round 1 sentence-level EQUATION-tier steps inherit their containing paragraph's lock status



///////////////////////////////
NLM
///////////////////////////////

PARA_01:
section: IV.A.1
paragraph_position: 1
page: 3191
first_word_verbatim: "We"
last_word_verbatim: "INCOMPLETE"
paragraph_text_verbatim: |
INCOMPLETE: cannot reproduce equation glyphs because the text source is heavily corrupted with mojibake for equation 12 (e.g., "ffiffiffiffiffiffiffiffiffiffiffi").
contains_equation: yes
contains_footnote_anchor: no
uncertainty: "Text source is corrupted for the inline/block equation, making accurate verbatim transcription of the math symbols impossible."

PARA_02:
section: IV.A.1
paragraph_position: 2
page: 3191
first_word_verbatim: "Following"
last_word_verbatim: "pound."
paragraph_text_verbatim: |
Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i as12 vol(r_{it}) = α_i + β_i^{UK} vol(FTSE100_t) + θ CONTROLS_t + ε_{it} (13) We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX£) into equation (13) to absorb effects arising through firms’ exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound.
contains_equation: yes
contains_footnote_anchor: yes
uncertainty: "none"

PARA_03:
section: IV.A.1
paragraph_position: 3
page: 3191
first_word_verbatim: "For"
last_word_verbatim: "framework.13"
paragraph_text_verbatim: |
For each firm, we take the estimated value of β_i^{UK} from regression (13) as the empirical counterpart to β_i in our framework.13
contains_equation: yes
contains_footnote_anchor: yes
uncertainty: "none"

PARA_04:
section: IV.A.2
paragraph_position: 2
page: 3191-3192
first_word_verbatim: "Textual"
last_word_verbatim: "choices."
paragraph_text_verbatim: |
Textual analysis reveals that most firms cite concerns about Brexit a half dozen times or more in their 10-Ks, or not at all. As such, we arbitrarily set a cutoff for high Brexit cites at more than 5 entries. There are 807 firms citing Brexit more than 5 times in their 10-Ks. On the other hand, 433 do not cite any Brexit-related terms in their public filings. Although the heuristic cutoff we consider is naturally arbitrary, our results are robust to many sensible alternative choices.
contains_equation: no
contains_footnote_anchor: no
uncertainty: "none"

PARA_05:
section: IV.B
paragraph_position: 4
page: 3192-3193
first_word_verbatim: "We"
last_word_verbatim: "firm-years."
paragraph_text_verbatim: |
We rely on the Your-Economy Time-Series (YTS) database, maintained by the Business Dynamics Research Consortium at the University of Wisconsin, for information on U.S.-based employment. The YTS database is compiled from historical business files from Infogroup and are linked longitudinally to track establishment location, employment, and sales information at the establishment-year level for public and private firms in the United States. We match our sample firms (both parents and their U.S. subsidiaries) to YTS primarily using tickers, and augment this match through manual searches by firm name. The firms in our sample collectively operated 757,083 unique establishments, and this results in 1,809,301 establishment-year observations over the 2010–2016 period. We aggregate YTS employment growth at the firm level, giving a final U.S. establishment-level employment growth sample of 11,345 firm-years.
contains_equation: no
contains_footnote_anchor: no
uncertainty: "none"

PARA_06:
section: IV.B
paragraph_position: 5
page: 3193
first_word_verbatim: "We"
last_word_verbatim: "events."
paragraph_text_verbatim: |
We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13)). We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events.
contains_equation: no
contains_footnote_anchor: no
uncertainty: "Not 100% sure if the next sentence starting with 'Analyst forecast...' is a new paragraph or a continuation of this one; assuming new paragraph based on typical visual layout and prior step extractions."

PARA_07:
section: IV.C.1
paragraph_position: 1
page: 3193
first_word_verbatim: "We"
last_word_verbatim: "0.28)."
paragraph_text_verbatim: |
We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms. Following our framework, in our base analysis, we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the β_i^{UK} distribution. For group contrasting, we do not include firms that benefit from uncertainty in the United Kingdom in the control group (firms with β_i^{UK} < 0) as this could lead to overestimation biases attached to the treatment effects we seek to identify. Nevertheless, in specifications where we use β_i^{UK} as a continuous treatment variable, we relax this restriction and include all values of β_i^{UK}.17 Under this market-based approach, a total of 449 unique firms are assigned to the treated category (β_i^{UK} > 0.68). In contrast, 360 unique firms are assigned to the control category (β_i^{UK} < 0.28).
contains_equation: yes
contains_footnote_anchor: yes
uncertainty: "none"

PARA_08:
section: IV.C.2
paragraph_position: 3
page: 3195
first_word_verbatim: "Having"
last_word_verbatim: "2016."
paragraph_text_verbatim: |
Having examined market uncertainty in the United Kingdom based on implied options volatility, we set out to verify in our U.S. firm-level data if this period coincided with increased perceived income uncertainty for HIGH_UK_EXPOSURE firms. We do so using data on analysts’ forecasts from the I/B/E/S database. Beginning in 2015:Q1, we obtain the 1-year-ahead earnings per share (EPS) forecasts for each firm in our sample and compute the mean and standard deviation of forecasts. We quantify earnings forecast uncertainty for firms in the high and low β_i^{UK} groups by constructing ±1.5-standard-deviation intervals around their group mean forecasts in Figure 4. The figure shows no discernible difference in mean forecasted earnings between high and low β_i^{UK} firms, suggesting analysts did not expect U.K.-exposed firms to do any worse, on average, in terms of earnings performance following the Brexit vote.19 The fact that mean EPS forecasts stay virtually the same over the 2-year window for both high and low β_i^{UK} firms suggests that there is no clear sign of a “first-moment” (negative) effect of Brexit on U.S. corporate earnings. That same earnings forecasts evidence points to the Brexit vote having a “second-moment” effect in terms of increased uncertainty regarding U.K.-exposed firms’ expectations in 2016:Q1–Q2. In particular, EPS forecast dispersion of HIGH_UK_EXPOSURE firms increases significantly in early 2016.
contains_equation: yes
contains_footnote_anchor: yes
uncertainty: "Structurally, this may be the 4th paragraph in IV.C.2 due to page breaks, but I am extracting it as it aligns with the requested content from page 3195."

PARA_09:
section: IV.C.3
paragraph_position: 1
page: 3196
first_word_verbatim: "We"
last_word_verbatim: "window."
paragraph_text_verbatim: |
We compare differences in outcomes of interest between treated (HIGH_UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms. Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects. This is equivalent to estimating the following model: Y_{i,t} = α + δ [POST_t × HIGH_UK_EXPOSURE_i] + θ CONTROLS_{i,t-1} + \sum_i FIRM_i + \sum_j \sum_t INDUSTRY_j × QUARTER_t + ε_{i,t} (14) The outcomes of interest, Y_{i,t}, are fixed capital investment, employment growth, R&D expenditures, divestitures, cash holdings, and NWC. HIGH_UK_EXPOSURE_i is a dummy variable that equals 1 if firm i is U.K.-exposed, and 0 otherwise. A firm is considered to be U.K.-exposed according to two measures: i) if it belongs to the top tercile of β_i^{UK} (market-based measure); or ii) if it has a high number of Brexit-related entries in its 2015 10-K form (textual-search-based measure). POST_t equals 1 if the time period is in the 2016:Q3–Q4 window.
contains_equation: yes
contains_footnote_anchor: no
uncertainty: "Uncertain if the variable definitions following equation 14 constitute one large continuous paragraph or multiple separated ones; included up to the POST_t definition based on logical grouping."

TOTAL_PARAGRAPHS_RETURNED: 9
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: NLM-notebook


///////////////////////////////
Claude web
///////////////////////////////

PARA_01:
  section: IV.A.1
  paragraph_position: 1
  page: 3190
  first_word_verbatim: "In"
  last_word_verbatim: "(11)"
  paragraph_text_verbatim: |
    In the context of our study, the increase in aggregate uncertainty, V_t, comes from the rise in uncertainty associated with the Brexit vote. Accordingly, we take variances on both sides of equation (1) (alternatively, equation (2)) to capture the notion of uncertainty in the MPS framework:

    var(v_it) = β_i² var(V_t) + σ_ε²    (11)
  contains_equation: "yes"
  contains_footnote_anchor: "no"
  uncertainty: "PAGE MISMATCH: the prompt lists PARA_01 on printed page 3191, but paragraph 1 of §IV.A.1 (the section's first paragraph, counting from the '1. Theoretical Framework-Based Measure of Uncertainty' heading) is printed on page 3190; equation (11) sits at the bottom of 3190, and paragraph 2 ('We can employ...') is the first §IV.A.1 paragraph on 3191."

PARA_02:
  section: IV.A.1
  paragraph_position: 2
  page: 3191
  first_word_verbatim: "We"
  last_word_verbatim: "(13)"
  paragraph_text_verbatim: |
    We can employ a regression-like approach to operationalize an empirical counterpart to βi. Specifically, taking square roots of both sides of equation (11), we obtain

    vol(v_it) ≈ β_i vol(V_t) + σ_ε − √(2 β_i vol(V_t) σ_ε)    (12)

    Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i as12

    vol(r_it) = α_i + β_i^UK vol(FTSE100)_t + θ CONTROLS_t + ε_it    (13)
  contains_equation: "yes"
  contains_footnote_anchor: "yes"
  uncertainty: "EQUATION-GLYPH CAVEAT: the prose of this paragraph is fully recoverable, but the body of equation (12) is garbled in my text source ('volð Þ vit ≈βivolð Þþ Vt σε ... 2βivolð Þ Vt σε p'). I have decoded it as vol(v_it) ≈ β_i vol(V_t) + σ_ε − √(2 β_i vol(V_t) σ_ε); the sign preceding the square-root term and the exact grouping cannot be confidently verified from my source. Footnote 13 (attached to eq. 13's containing paragraph, PARA_03) confirms eq. (12) has a final square-root term ('The last term in equation (12) is subsumed by the idiosyncratic volatility term, εit, in equation (13).'), but does not fix its sign. Equation (13) is recovered cleanly. RECOMMEND PDF arbitration of eq. (12)."

PARA_03:
  section: IV.A.1
  paragraph_position: 3
  page: 3191
  first_word_verbatim: "Equation"
  last_word_verbatim: "framework.13"
  paragraph_text_verbatim: |
    Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it). It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting). We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound. For each firm, we take the estimated value of β_i^UK from regression (13) as the empirical counterpart to βi in our framework.13
  contains_equation: "yes"
  contains_footnote_anchor: "yes"
  uncertainty: "contains_equation = yes refers to inline equation expressions only (vol(r_it), vol(v_it), vol(SP500), vol(FX$£), β_i^UK); there is no display equation in this paragraph."

PARA_04:
  section: IV.A.2
  paragraph_position: 2
  page: 3191-3192
  first_word_verbatim: "Textual"
  last_word_verbatim: "choices."
  paragraph_text_verbatim: |
    Textual analysis reveals that most firms cite concerns about Brexit a half dozen times or more in their 10-Ks, or not at all. As such, we arbitrarily set a cutoff for high Brexit cites at more than 5 entries. There are 807 firms citing Brexit more than 5 times in their 10-Ks. On the other hand, 433 do not cite any Brexit-related terms in their public filings. Although the heuristic cutoff we consider is naturally arbitrary, our results are robust to many sensible alternative choices.
  contains_equation: "no"
  contains_footnote_anchor: "no"
  uncertainty: "PAGE SPAN: the prompt lists PARA_04 on printed page 3192, but this paragraph begins on 3191 ('Textual analysis reveals that most firms cite concerns about Brexit a half dozen times or more in their 10-Ks, or not at all.') and continues onto 3192 ('As such, we arbitrarily set a cutoff...'). Boundaries themselves are unambiguous; only the page label differs."

PARA_05:
  section: IV.B
  paragraph_position: 4
  page: 3192-3193
  first_word_verbatim: "We"
  last_word_verbatim: "firm-years."
  paragraph_text_verbatim: |
    We rely on the Your-Economy Time-Series (YTS) database, maintained by the Business Dynamics Research Consortium at the University of Wisconsin, for information on U.S.-based employment. The YTS database is compiled from historical business files from Infogroup and are linked longitudinally to track establishment location, employment, and sales information at the establishment-year level for public and private firms in the United States. We match our sample firms (both parents and their U.S. subsidiaries) to YTS primarily using tickers, and augment this match through manual searches by firm name. The firms in our sample collectively operated 757,083 unique establishments, and this results in 1,809,301 establishment-year observations over the 2010–2016 period. We aggregate YTS employment growth at the firm level, giving a final U.S. establishment-level employment growth sample of 11,345 firm-years.
  contains_equation: "no"
  contains_footnote_anchor: "no"
  uncertainty: "PARAGRAPH-COUNT RECONCILIATION: this YTS paragraph is the one that spans the 3192→3193 break ('...at the University' / 'of Wisconsin...'), matching the prompt's '3192-3193 (may span page break)' hint, and is reached as §IV.B paragraph 4 only under the counting COMPUSTAT(¶1) / Orbis(¶2) / employment-COMPUSTAT-Annual(¶3) / YTS(¶4) / CRSP(¶5). This differs from my Round 1 numbering (STEP_18), where I treated YTS as §IV.B ¶3 because COMPUSTAT+Orbis were merged into one paragraph. PDF text extraction collapses paragraph indentation, so §IV.B paragraph boundaries are not directly observable; I adopt the finer (5-paragraph) count here because it is the only one under which the prompt's PARA_05 and PARA_06 page labels are both satisfiable."

PARA_06:
  section: IV.B
  paragraph_position: 5
  page: 3193
  first_word_verbatim: "We"
  last_word_verbatim: "database."
  paragraph_text_verbatim: |
    We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13)). We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events. Analyst forecast data are obtained from I/B/E/S. Data on bond yields are from TRACE and SDC, whereas syndicated loan spreads are drawn from WRDS–Reuters DealScan. Macroeconomic variables are taken from the Federal Reserve Bank of St. Louis' FRED database.
  contains_equation: "no"
  contains_footnote_anchor: "no"
  uncertainty: "PARAGRAPH-COUNT RECONCILIATION: this is §IV.B ¶5 under the 5-paragraph count described in PARA_05's note (it was §IV.B ¶4 / STEP_19 in Round 1). The paragraph is entirely on 3193; the inline 'equation (13)' is a cross-reference, not a display equation."

PARA_07:
  section: IV.C.1
  paragraph_position: 1
  page: 3193
  first_word_verbatim: "We"
  last_word_verbatim: "10-Ks."
  paragraph_text_verbatim: |
    We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms. Following our framework, in our base analysis, we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the β_i^UK distribution. For group contrasting, we do not include firms that benefit from uncertainty in the United Kingdom in the control group (firms with β_i^UK < 0) as this could lead to overestimation biases attached to the treatment effects we seek to identify. Nevertheless, in specifications where we use β_i^UK as a continuous treatment variable, we relax this restriction and include all values of β_i^UK.17 Under this market-based approach, a total of 449 unique firms are assigned to the treated category (β_i^UK > 0.68). In contrast, 360 unique firms are assigned to the control category (β_i^UK < 0.28). We also consider an alternative, text-based measure of exposure to Brexit. Under this approach, 807 firms are assigned to the treated category (2015 10-K mentions of Brexit terms > 5). A total of 433 firms in the control category have no mentions of Brexit-related terms in their 10-Ks.
  contains_equation: "yes"
  contains_footnote_anchor: "yes"
  uncertainty: "contains_equation = yes refers to inline expressions only (β_i^UK and the thresholds β_i^UK > 0.68, β_i^UK < 0.28); no display equation is present. The threshold values 0.68 and 0.28 are recovered from a source where the inequality glyphs were partially garbled; the digits are legible and consistent with the treated/control tercile description, but warrant a glance at the PDF."

PARA_08:
  section: IV.C.2
  paragraph_position: 3
  page: 3194-3195
  first_word_verbatim: "Responses"
  last_word_verbatim: "2014."
  paragraph_text_verbatim: |
    Responses to official news about the exact referendum date suggest that market participants were quick to incorporate uncertainty embedded by Brexit in their trading activity (before the actual outcome of the vote). In particular, options trading taking place on Feb. 22, 2016 (continuous red curve in Figure 3), the first trading day following David Cameron's announcement of the Brexit vote date, were priced to reflect a significant drop in market volatility for the period leading up to the Brexit vote date (on June 23), only to show a spike in volatility right after the vote. On June 24, 2016 (dashed yellow curve), the first trading day following the vote, market uncertainty seemed unusually high. Resolution about the vote outcome, nonetheless, seems to quell uncertainty forecasts. In particular, the 1-year-ahead implied volatility immediately after the vote date is not significantly different from that registered back in Dec. 2014.
  contains_equation: "no"
  contains_footnote_anchor: "no"
  uncertainty: "PAGE SPAN: the prompt lists PARA_08 on printed page 3195, but §IV.C.2 paragraph 3 (counting Once-firms(¶1) / first-dotted-blue-curve(¶2) / Responses-to-official-news(¶3)) begins on 3194 and continues onto 3195 ('...about the vote' / 'outcome, nonetheless, seems to quell...'). Footnote 18 belongs to ¶1 and footnote 19 to ¶4, so this paragraph carries no footnote anchor."

PARA_09:
  section: IV.C.3
  paragraph_position: 1
  page: 3196
  first_word_verbatim: "We"
  last_word_verbatim: "(14)"
  paragraph_text_verbatim: |
    We compare differences in outcomes of interest between treated (HIGH_UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms. Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects. This is equivalent to estimating the following model:

    Y_i,t = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θ CONTROLS_i,t−1 + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ε_i,t.    (14)
  contains_equation: "yes"
  contains_footnote_anchor: "no"
  uncertainty: "none"

TOTAL_PARAGRAPHS_RETURNED: 9
EXTRACTION_DATE: 2026-05-26
PAPER_ACCESS_METHOD: PDF-attached