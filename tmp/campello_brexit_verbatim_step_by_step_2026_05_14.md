# Campello et al. 2022 JFQA Brexit — Verbatim Step-by-Step Replication Recipe

**Phase 1 of strict replication audit. PURE VERBATIM ONLY. No interpretation, no implementation comparison.**

**Source**: Campello, M., G. S. Cortes, F. d'Almeida, and G. Kankanhalli. 2022. "Exporting Uncertainty: The Impact of Brexit on Corporate America." *Journal of Financial and Quantitative Analysis* 57(8): 3178-3222. doi:10.1017/S0022109022000308.

**Local file**: `docs/papers/campello_etal_2022_brexit_jfqa.pdf` (793KB, 45 pages, j.3178–3222).

**Extract method**: `pdftotext -layout` (poppler-utils 24.04.0). Output per-page text → `tmp/campello_pages/p01.txt` … `p45.txt`. Body text is column-stripped clean; only top-line page header (running title + URL) is noise.

**Anchor convention**: `[PDF p.N // j.XXXX]`. PDF p.1 = j.3178.

---

## §1. Sample universe

**[PDF p.15 // j.3192, lines 33–43]**, §IV.B Data Sources and Sample Construction:

> "We use COMPUSTAT Quarterly to gather basic information on firm investment and financial data. We consider U.S. companies from the first calendar quarter of 2010 to the fourth quarter of 2016. We drop utility and financial firms, as well as companies whose market value or book assets are lower than $10 million. The sample used in our baseline investment tests consists of 41,630 observations (firm-quarters). For additional analysis on firms' investment in the United States, we obtain subsidiary-level investment data from the Bureau van Dijk's Orbis data set (see Cravino and Levchenko (2016))."

**[PDF p.15 // j.3192, footnotes 15-16]**:

> "15. For details of the sample selection filters, see Table C1 in the Supplementary Material."
> "16. The same filters described in Table C1 in the Supplementary Material are also applied to obtain this sample."

**[PDF p.16 // j.3193, lines 14-21]**:

> "We use CRSP stock price data and Bloomberg equity index and currency data to compute our theoretical framework-based measure of firm exposure to the United Kingdom (see equation (13)). We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events. Analyst forecast data are obtained from I/B/E/S. Data on bond yields are from TRACE and SDC, whereas syndicated loan spreads are drawn from WRDS–Reuters DealScan. Macroeconomic variables are taken from the Federal Reserve Bank of St. Louis' FRED database."

---

## §2. Treatment definitions

### §2.1. β^UK market-based — equation (13)

**[PDF p.14 // j.3191, eq (13)]**:

> "(13) vol(r_it) = α_i + β_i^UK · vol(FTSE100_t) + θ · CONTROLS_t + ε_it"

**[PDF p.14 // j.3191, lines 16-26]**:

> "Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it). It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting). We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound. For each firm, we take the estimated value of β̂_i^UK from regression (13) as the empirical counterpart to β_i in our framework."

**Estimation window — [PDF p.16 // j.3193, line 16]**:

> "We use monthly data from 2010:M1 to 2014:M12 so that exposure to the United Kingdom is measured before any major Brexit-related events."

### §2.2. β^UK,CF (cash-flow component) — alternative measure

**[PDF p.14 // j.3191, fn 13]**:

> "Following Vuolteenaho (2002), we also decompose the volatility of each firm's returns into cash flow and discount rate components and reestimate equation (13) with the cash flow component (only) as the dependent variable, obtaining an alternative uncertainty measure, β_i,CF^UK. The estimates for β_i^UK and β_i,CF^UK have a rank correlation of 0.8, and there is an 86% overlap in the set of firms at the top tercile of both β_i^UK and β_i,CF^UK. As shown in Table C6, our inferences are unchanged whether using β_i^UK or β_i,CF^UK to conduct our tests."

### §2.3. 10-K textual-search measure

**[PDF p.14 // j.3191, lines 30-41]**, §IV.A.2:

> "As an alternative measure of U.S. firms' exposure to Brexit-induced uncertainty, we develop a textual-search-based metric that is constructed by parsing firms' 2015 10-K filings. In particular, we look for the number of entries of keywords related to uncertainty about Brexit ('Brexit', 'Great Britain', and 'Uncertainty') in firms' disclosures, classifying firms with a 'high' number of entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control firms. Notably, the vast majority of firms file their 10-Ks with the SEC between March and June of each year. By computing these wordcounts from firms' 10-K disclosures (before the actual vote takes place, yet after the referendum is announced), we build a measure of exposure to the United Kingdom based on what firms consider relevant to communicate to their investors on the eve of the 2016 Brexit vote."

**Subsumed keywords — [PDF p.14 // j.3191, fn 14]**:

> "Entries like 'Referendum', 'Uncertain', 'United Kingdom', 'UK', 'U.K.', and 'G.B.' are subsumed by the above wording."

**Cutoff — [PDF p.15 // j.3192, lines 3-6]**:

> "Brexit cites at more than 5 entries. There are 807 firms citing Brexit more than 5 times in their 10-Ks. On the other hand, 433 do not cite any Brexit-related terms in their public filings. Although the heuristic cutoff we consider is naturally arbitrary, our results are robust to many sensible alternative choices."

### §2.4. Treatment classification rules

**[PDF p.16 // j.3193, lines 27-54]**, §IV.C.1 Identification:

> "We use a standard DID approach to assess the impact of the 2016 Brexit vote on American firms. Following our framework, in our base analysis, we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the β_i^UK distribution. For group contrasting, we do not include firms that benefit from uncertainty in the United Kingdom in the control group (firms with β_i^UK < 0) as this could lead to overestimation biases attached to the treatment effects we seek to identify. Nevertheless, in specifications where we use β_i^UK as a continuous treatment variable, we relax this restriction and include all values of β_i^UK."
>
> "Under this market-based approach, a total of 449 unique firms are assigned to the treated category (β_i^UK > 0.68). In contrast, 360 unique firms are assigned to the control category (β_i^UK < 0.28). We also consider an alternative, text-based measure of exposure to Brexit. Under this approach, 807 firms are assigned to the treated category (2015 10-K mentions of Brexit terms > 5). A total of 433 firms in the control category have no mentions of Brexit-related terms in their 10-Ks."

**[PDF p.16 // j.3193, fn 17]**:

> "In unreported tests, we only label those firms with statistically significant positive β_i^UK estimates as treated firms, and those with β_i^UK statistically indistinguishable from 0 as controls. We find that our results hold across a range of sensible treatment assignment thresholds."

---

## §3. DiD time dimension (POST_t)

**[PDF p.19 // j.3196, lines 8-29]**, §IV.C.3 Empirical Model:

> "We compare differences in outcomes of interest between treated (HIGH_UK_EXPOSURE) and control (LOW_UK_EXPOSURE) firms. Differences over the 2016:Q3–Q4 period are taken relative to the same two quarters in the previous year (2015:Q3–Q4) in order to minimize the impact of seasonal effects. This is equivalent to estimating the following model:"
>
> "(14) Y_{i,t} = α + δ · [POST_t × HIGH_UK_EXPOSURE_i] + θ · CONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ε_{i,t}"
>
> "The outcomes of interest, Y_{i,t}, are fixed capital investment, employment growth, R&D expenditures, divestitures, cash holdings, and NWC. HIGH_UK_EXPOSURE_i is a dummy variable that equals 1 if firm i is U.K.-exposed, and 0 otherwise. A firm is considered to be U.K.-exposed according to two measures: i) if it belongs to the top tercile of β_i^UK (market-based measure); or ii) if it has a high number of Brexit-related entries in its 2015 10-K form (textual-search-based measure). **POST_t equals 1 if the time period is in the 2016:Q3–Q4 window.**"

**Window cutoff — [PDF p.19 // j.3196, lines 3-6]**:

> "We limit our analysis to the end of 2016 due to the start of the Trump administration in Jan. 2017. We show in later robustness checks that results also hold for a window that excludes Trump's election."

---

## §4. Control variables (eq 14)

**[PDF p.20 // j.3197, lines 3-15]**, §IV.C.3 cont.:

> "CONTROLS_{i,t−1} is a vector of macroeconomic and firm-level control variables. Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingstone Survey, the lagged Consumer Sentiment Index from the University of Michigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia. Firm-level controls include lagged stock returns, Tobin's Q, cash flow, logged assets, and sales growth. As an additional control for first-moment effects of Brexit, we add 1-quarter-ahead consensus earnings forecasts to our model. FIRM_i represents firm-fixed effects, INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100), and QUARTER_t are calendar-quarter dummies. Standard errors are double-clustered by firm and calendar quarters."

---

## §5. Variable definitions (verbatim from Table 1 + Table 8)

**[PDF p.21 // j.3198, Table 1 caption, lines 7-25]**:

> "Table 1 reports summary statistics for the main variables used in our empirical analyses. The final sample is a match between COMPUSTAT Quarterly North America Fundamentals and the estimated β_i^UK sample for the period from 2010:Q1 to 2015:Q4. Each panel reports the mean, standard deviation, median, interquartile range (IQR), and the number of observations conditional on firms belonging to each subsample.
>
> - INVESTMENT is defined as capital expenditures divided by lagged total assets.
> - EMPLOYMENT_GROWTH is defined as the percentage change in the number of employees (annual).
> - R&D is defined as R&D expenditures divided by lagged total assets, considering only firms with non-missing R&D expenditures.
> - DIVESTITURES is defined as the value of sale of plant, property, and equipment divided by lagged total assets.
> - CASH is defined as cash and short-term investments divided by lagged total assets.    ← [Table 1 summary-stats definition]
> - NON_CASH_WORKING_CAPITAL is defined as working capital (net of cash) divided by lagged total assets.
> - TOBIN_Q is defined as the market value of assets divided by the book value of assets, and is calculated as the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.
> - CASH_FLOW is defined as operating income before depreciation divided by lagged total assets.
> - SIZE is defined as the logarithm of total assets.
> - SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales.
> - CONSENSUS_EARNINGS_FORECAST is defined as the standardized mean 1-quarter ahead earnings per share forecast.
> - STOCK_RETURNS are defined as the quarterly buy-and-hold return.
> - All variables are winsorized at the 1% level."

**[PDF p.31 // j.3208, Table 8 caption, lines 3-25]**:

> "Table 8 reports output from equation (14). The dependent variables are CASH, NON_CASH_WORKING_CAPITAL, and PROFITS.
>
> - **CASH is defined as total cash holdings divided by lagged total assets net of cash holdings.**    ← [Table 8 regression DV definition — differs from Table 1 summary-stats]
> - NON_CASH_WORKING_CAPITAL (NWC) is defined as working capital (net of cash) divided by lagged total assets.
> - PROFITS is defined as the quarterly percentage change in profits (operating income before depreciation divided by sales).
>
> In the first specification, the treatment group is composed by the top tercile of β_i^UK, whereas the control group is composed by firms in the bottom tercile of β_i^UK. The second specification is a textual-search-based measure of U.K. exposure that sums up the number of Brexit-related words in firms' 2015 10-K forms. The treatment group is made of firms with more than five entries, whereas the control group are firms with zero entries.
>
> **The time dimension of the DID estimator is set so as to compare the two quarters following the announcement of the referendum and Brexit's victory (2016:Q3–Q4) versus the two quarters preceding the announcement (2015:Q3–Q4).** T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels. *, **, and *** indicate statistical significance at the 10%, 5%, and 1% levels, respectively."

---

## §6. Baseline reported results (for replication target)

**[PDF p.23 // j.3200, Table 2 — Investment + Employment]**:

```
                          INVESTMENT                          EMPLOYMENT_GROWTH
                  Linear   βUK         > 5 Brexit    Linear   βUK         > 5 Brexit
                  βUK      Tercile     Entries       βUK      Tercile     Entries
                   1        2           3             4        5           6
POST              −0.022                              1.055
                  (0.020)                            (2.843)
POST × βUK        −0.047***                         −4.173**
                  (0.010)                            (2.133)
POST × HIGH_βUK            −0.165***                         −4.912***
                            (0.019)                           (1.552)
POST × HIGH_                            −0.077***                         −2.617***
   10K_ENTRIES                            (0.008)                          (0.402)

Controls          Yes      Yes          Yes          Yes      Yes          Yes
Firm FE           Yes      Yes          Yes          Yes      Yes          Yes
Industry×Time FE  No       Yes          Yes          No       Yes          Yes

No. of obs.       43,025   17,199       21,253       9,143    3,540        4,173
R²                0.67     0.75         0.73         0.35     0.45         0.45
```

**[PDF p.31 // j.3208, Table 8 — Cash + NWC + Profits]**:

```
                  CASH                       NWC                       PROFITS
                  βUK         > 5 Brexit     βUK        > 5 Brexit     βUK         > 5 Brexit
                  Tercile     Entries        Tercile    Entries        Tercile     Entries
                   1           2              3          4              5            6

POST × HIGH_βUK   +0.231***                 −0.687***                 −0.135
                  (0.059)                   (0.281)                   (0.391)
POST × HIGH_                  +0.357***                −0.608***                  +0.343
   10K_ENTRIES                (0.062)                  (0.079)                    (0.550)

Controls          Yes         Yes            Yes        Yes            Yes         Yes
Firm FE           Yes         Yes            Yes        Yes            Yes         Yes
Industry×Time FE  Yes         Yes            Yes        Yes            Yes         Yes

No. of obs.       17,170      24,195         16,630     23,806         16,630      24,051
R²                0.21        0.24           0.89       0.87           0.89        0.15
```

---

## §7. Robustness ladder

### §7.1. Propensity Score Matching — [PDF p.22 // j.3199, lines 38-43]

> "To ensure that differences in firm characteristics do not drive our results, we redo all of our tests on propensity score matched samples in which firm-level characteristics are balanced before any estimations are conducted. Table C2 in the Supplementary Material displays the summary statistics of the matched samples. Table C3 in the Supplementary Material reports the results of our main estimations on these matched samples."

### §7.2. Parallel Trends — [PDF p.22 // j.3199, lines 43-46 + p.22 lines 61-63]

> "To further verify that treated and control firms are not fundamentally different, we examine the validity of the parallel trends assumption. Visual evidence for that assumption [is provided] in Figure C1 in the Supplementary Material. Tables C4 and C5 in the Supplementary Material report formal tests supporting the presence of parallel trends across all outcome variables."

### §7.3. Accounting for Trump's Election — [PDF p.36 // j.3213, §VI.D, lines 8-30]

> "One could be concerned about confounding uncertainty effects associated with the election of President Donald Trump in the United States. We address this issue in two different ways. First, we consider an alternative event window that excludes 2016:Q4 from our treatment evaluation period. This narrower time window helps mitigate concerns that forward-looking behavior of firms regarding Trump's election in the United States could influence our results (Trump's victory was an unlikely event as of 2016:Q3). Accordingly, we compare the third quarter of 2016 with the same quarter of 2015. As shown in columns 1 and 2 of Table 12, results are similar to our baseline estimates in Table 2. The patterns we report are consistent with relatively short-lived, 'drop-and-rebound' effects of uncertainty."
>
> "Second, we look at the recent literature on the effect of Trump's election on U.S. firms. Wagner, Zeckhauser, and Ziegler (2018) detail a methodology identifying what the authors label as 'winners' and 'losers' from that election. We use their method, which is based on 10-day cumulative capital asset pricing model (CAPM)-adjusted abnormal stock returns around the Trump election date, to check for the presence of either of these sets of firms in our sample. Our treatment group based on β_i^UK (10-K mentions) contains 57 (23) 'loser' firms. In columns 3 and 4 of Table 11, we replicate our baseline tests on investment omitting firms labeled as 'losers' by Wagner et al. (2018), that is, firms that might invest less because of Trump's election. The estimates show that our inferences are unaffected by these firms."

### §7.4. Falsification Tests — [PDF p.36 // j.3213, §VI.E, lines 32-44]

> "We also address concerns that our test design is set up in a way that may generate results not necessarily tied to the June 2016 referendum result. In doing so, we reestimate our tests considering two 'treatment periods' that occurred prior to the 2016 Brexit vote: i) David Cameron's election as Prime Minister (2015:Q3) and ii) the U.S. Debt Ceiling Crisis of 2011 (2011:Q2–2011:Q4). The first falsification test mitigates concerns that firms anticipated the process leading to the Brexit referendum at the time of Cameron's election. The second addresses concerns that our investment results could be driven by episodes of uncertainty in the United States (and not the United Kingdom) that affect global firms in general. As shown in columns 5–8 of Table 12, the DID coefficients are statistically insignificant in all such cases."

### §7.5. Table 12 windows + N — [PDF p.38 // j.3215, Table 12 caption + data]

> "Table 12 reports output from equation (14) under alternative treatment windows and alternative treatment samples. The dependent variable is INVESTMENT. … In the first two columns, the time dimension of the DID estimator is set so as to compare 2016:Q3 versus 2015:Q3. In the second two columns, the time dimension of the DID estimator is set so as to compare 2016:Q3–Q4 versus 2015:Q3–Q4, excluding firms deemed as 'losers' from Trump's election as in Wagner et al. (2018). In the next two columns, the time dimension of the DID estimator is set so as to compare 2015:Q3 versus 2014:Q3. In the final two columns, the time dimension of the DID estimator is set so as to compare 2011:Q2–Q4 versus 2010:Q2–Q4."

```
Treatment Window:  2016:Q3 vs. 2015:Q3   2016:Q3–Q4 vs. 2015:Q3–Q4  2015:Q3 vs. 2014:Q3  2011:Q2–Q4 vs. 2010:Q2–Q4
Event:             Excluding Trump        Excluding Trump losers     Cameron's Election   U.S. Debt Ceiling Crisis
                   βUK     10K            βUK     10K                βUK     10K          βUK     10K
                    1       2              3       4                  5       6            7       8
POST×HIGH_βUK    −0.216***                −0.197***                  +0.018             +0.014
                  (0.019)                  (0.010)                    (0.011)             (0.082)
POST×HIGH_10K            −0.064***                −0.074***                  +0.017               N/A
                          (0.012)                  (0.010)                    (0.011)
N                 17,199   21,253         15,967   20,669            17,199   21,253     17,199   N/A
R²                0.74     0.73            0.75     0.72              0.74     0.75       0.74    —
```

### §7.6. FX exposure — [Table 9, PDF p.33 // j.3210]
Baseline + 4 additional FX controls: (a) firm's quarterly equity-returns exposure to GBP (β_FX£_i,t); (b) Alfaro et al. (2018) firm-level USD-GBP first- and second-moment instruments; (c) annual dummy for FX hedging mention in most recent 10-K; (d) intensity of FX hedging via Campello et al. (2011) word list.

### §7.7. Other-country falsification — [Table 13, PDF p.40 // j.3217]
Replace βUK with β^EU, β^China, β^Mexico, β^Japan, β^India, β^Brazil. βUK baseline = −0.165***; β^EU = −0.066***; all others insignificant.

### §7.8. Automation channel — [Table 11, PDF p.36 // j.3213]
Acemoglu-Restrepo (2020) geographic-based + alternative text-based automation exposure as additional controls.

### §7.9. Financing constraints — [Table 10, PDF p.34 // j.3211]
Add bond yields (TRACE), new bond issue yields (SDC), syndicated loan markups (DealScan), discount-rate news component (Vuolteenaho 2002 decomposition) as additional controls.

### §7.10. Capital irreversibility — [Table 7, PDF p.30 // j.3207]
Kim and Kung (2016) asset-redeployability index. Treated firms split by top/bottom tercile of irreversibility.

### §7.11. Labor irreversibility — [Table 7]
Unionization rate at 4-digit SIC level from BEA.

---

## §8. Capital + labor irreversibility measures (background for moderator splits)

**[PDF p.15 // j.3192, lines 8-29]**, §IV.A.3:

> "Our predicted uncertainty–investment relationships are modulated by fixed costs F_iK, which capture the degree of irreversibility of capital. To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016). … Our next task is to find an empirical proxy for the irreversibility of labor, F_iL. We resort to the use of worker unionization as an empirical proxy for frictions in labor input. We do so as ample research highlights the difficulties faced by firms with unionized employees in adjusting their workforce in response to changes in aggregate conditions (see, among others, Bloom (2009)). In using this strategy, we measure the percentage of total employees who are unionized at the 4-digit SIC level using data from the Bureau of Economic Analysis."

---

## §9. Open ambiguities to resolve in Online Appendix / Supplementary Material

The following items reference Tables C1–C7 or Appendix D/E in the Supplementary Material. Not in main PDF; require download of supplementary file.

| Ref | What it covers |
|---|---|
| Table C1 | Sample-selection filter details (SIC ranges for utility/financial exclusion; precise $10M filter mechanics; missing-value handling) |
| Table C2 | PSM matched-sample summary stats |
| Table C3 | Main estimations on PSM matched samples |
| Table C4 | Formal parallel-trends tests, all outcomes |
| Table C5 | Formal parallel-trends tests, additional outcomes |
| Table C6 | Sensitivity to using β^UK,CF instead of β^UK |
| Table C7 | First-moment robustness: bond yields, loan spreads, Tobin's Q, Cash Flow, Sales Growth, Consensus EPS, Stock Returns, Alfaro et al. (2018) instruments |
| Appendix D | Timeline of events leading to Brexit referendum |
| Appendix E | Automation time-varying analogue (Automation_{i,t}) |

---

## END Phase 1.

Audit vs F1D code begins in a separate file: `tmp/campello_brexit_implementation_audit_2026_05_14.md` (not yet written).
