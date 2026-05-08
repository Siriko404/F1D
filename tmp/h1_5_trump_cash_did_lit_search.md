# Lit search — Trump 2016 DiD on firm cash holdings (Phase 1: abstract screening)

Run date: 2026-05-08
Method: WebSearch + WebFetch (open-access sources only — SSRN, ScienceDirect, Springer all paywalled and 403'd)
Anti-fabrication discipline: no candidate listed without verbatim source quote OR confirmed open abstract

## Search queries run

1. `"Trump 2016" "cash holdings" difference-in-differences firm`
2. `"presidential election" "corporate cash holdings" 2016 DiD precautionary`
3. `"Trump tariff" "cash holdings" DiD treatment exposure`
4. `"Tax Cuts and Jobs Act" "cash holdings" difference-in-differences 2017`
5. `"Section 301" OR "Section 232" tariff "cash holdings" difference-in-differences firm 2018`
6. `"trade policy uncertainty" "cash holdings" DiD treatment firm exposure SSRN`
7. `"Economic Policy Uncertainty" "cash holdings" Trump election DiD precautionary`
8. `"trade war" "cash holdings" 2018 2019 firm DiD precautionary tariff`
9. `"PRisk" "cash holdings" Trump 2016 election DiD firm political risk Hassan`
10. `"Trump election" 2016 firm "cash holdings" precautionary savings difference-in-differences working paper`
11. `"Trump 2016" OR "November 2016" cash holdings DiD treatment "treatment group" precautionary`
12. `"Acemoglu" OR "Auer" OR "Cavallo" OR "Amiti" Trump tariff 2018 firm cash precautionary working paper`
13. `"Does firm-level political risk affect cash holdings" Review Quantitative Finance Accounting 2022 author`
14. `"firm-level political risk" "cash holdings" "1 standard deviation" "6.8%" cash reserves`

## Verdict (UPDATED 2026-05-08 PM after OpenAlex programmatic + citation-chase)

**Phase 2 — programmatic OpenAlex search:**
- 17 keyword queries × 30 results each (deduped): **223 unique works**
- 4 anchor-paper citation chases (Hassan 2019 PRisk QJE, Hasan 2022 RQFA, Hu et al 2024 RAST, Wagner et al 2018 JFE): **902 unique citing-papers**
- Combined deduped: **1,092 unique scholarly works examined**
- Of those: **2** mention BOTH (Trump-era shock) AND (cash holdings); **0** also have a DiD design term in title/abstract

**The two cash + Trump-era hits both fail on inspection:**
1. *Fiscal Year-Ends and Financial Benefits: The Role of Prospective Measurement Dates in Tax Reform* (JATA 2024, 0 cites) — TCJA + cash mention, but no DiD vocabulary in abstract; tax-accounting paper not finance-DiD.
2. *Impact of Cash Holdings on Firm Value: Role of Election Induced Political Uncertainty* (AAMJAF 2023, 0 cites) — election proxy + cash on RHS as moderator, **firm value as DV not cash**.

**Only one Trump-era + cash + DiD paper surfaced via OpenAlex citation-chase (no Trump in abstract because empty in OpenAlex but identified by title):**
- *The Real and Financial Effects of Internal Liquidity: Evidence From the Tax Cuts and Jobs Act* — Albertus, Glover & Levine (2025) JFE; SSRN 4471259; 13 OpenAlex cites
- Shock: **TCJA Dec 2017** (Trump-policy lever), NOT the Nov 2016 election event
- DV: cash holdings (downward adjustment) + share repurchases ✓
- Channel: financing-friction (repatriation-tax relief), **NOT precautionary**
- DiD: yes; treatment = MNCs with overseas cash subject to repatriation tax

**Final empirical conclusion (after 1,092-paper sweep):**

> Zero published papers use the November 2016 Trump election event itself as a difference-in-differences shock with cash holdings as the dependent variable, regardless of channel. The Albertus-Glover-Levine 2025 JFE paper is the unique published precedent for "Trump-era policy shock + cash DV + DiD design", but the shock is TCJA Dec 2017 (not the election event) and the channel is financing-friction (not precautionary).

## Candidates examined (verbatim provenance where available)

### A. Wagner, Zeckhauser & Ziegler (2018) JFE
- Title: "Company stock price reactions to the 2016 election shock: Trump, taxes, and trade"
- Journal: *Journal of Financial Economics*, 130(2), Nov 2018, 428-451
- NBER w23152; SSRN 2909835
- Shock: Trump Nov 2016 election ✓
- DV: **stock returns** (NOT cash)
- DiD: yes
- Verdict: **WRONG OUTCOME** — uses cash variables only as moderators/sector-classifiers, not as DV

### B. Wagner, Zeckhauser & Ziegler (2018) AEA P&P
- Title: "Unequal Rewards to Firms: Stock Market Responses to the Trump Election and the 2017 Corporate Tax Reform"
- Journal: *AEA Papers and Proceedings*, 108
- Abstract verbatim: "Massive dollars shuttled back and forth among firms on the twisted path to and passage of the 2017 tax reform... Daily price movements show that the aggregate market responded positively to lower expected taxes."
- Shock: Trump 2016 + TCJA passage
- DV: **stock prices** (NOT cash)
- Verdict: **WRONG OUTCOME**

### C. Hu, Kang, Li & Lin (2024) RAST [our existing anchor for H1.5 template]
- Shock: Trump Nov 2016 ✓
- DV: Q&A speech tone (Net_Negative)
- Treatment: minority-CEO status
- Verdict: **WRONG OUTCOME, WRONG TREATMENT** — already known; this is what we adapted

### D. Hasan, Alam, Paramati & Islam (2022) RQFA [our existing H1.6 anchor]
- Title: "Does firm-level political risk affect cash holdings?"
- Journal: *Review of Quantitative Finance and Accounting*
- DOI: 10.1007/s11156-022-01049-9
- Sample: 5,424 firms × 129,750 firm-quarter obs, 2002Q1-2021Q3
- DV: cash holdings (cheq/atq) ✓
- Channel: precautionary ✓
- Shock used: 2010 Census redistricting (DiD) + 2SLS PCI-IV + PSM + subsamples
- Trump 2016: NOT used as DiD shock anywhere
- Verdict: **WRONG SHOCK** — perfect on DV + channel + DiD, but redistricting not Trump (this IS our H1.6)

### E. Hassan, Hollander, vanLent & Tahoun (2019) QJE [our existing PRisk anchor]
- Title: "Firm-Level Political Risk: Measurement and Effects"
- NBER w24029
- DV outcomes: hiring, investment, lobbying, donations
- Trump 2016: validation case only ("Q4 2016, 89.6% SD jump"); NOT a DiD shock
- Cash holdings: explicitly NOT among outcomes (per memory verbatim file)
- Verdict: **WRONG OUTCOME**

### F. Albertus, Glover & Levine (2025) JFE
- Title: "The Real and Financial Effects of Internal Liquidity: Evidence From the Tax Cuts and Jobs Act"
- SSRN 4471259; ScienceDirect S0304405X25000145
- Shock: TCJA Dec 2017 repatriation-tax change (Trump's signature law, but POLICY-level not election-event)
- DV: cash holdings (downward adjustment) + share repurchases ✓
- DiD: yes; treatment = multinationals with overseas cash subject to repatriation tax
- Channel: financing-friction relaxation, NOT precautionary
- Verdict: **TRUMP POLICY ✓ / DV ✓ / WRONG CHANNEL** — closest TCJA candidate but channel mismatch

### G. De Simone, Piotroski & Tomy (2019) RFS
- Title: "Repatriation Taxes and Foreign Cash Holdings: The Impact of Anticipated Tax Reform"
- SSRN 2927120; *RFS* 32(8), 3105-3143
- Shock: Anticipation of TCJA reform (pre-passage Congressional proposals)
- DV: foreign cash holdings ✓
- DiD: yes; treatment = MNCs likely to benefit from repat-tax cut
- Channel: strategic tax positioning, NOT precautionary
- Verdict: **PRE-TCJA / WRONG CHANNEL**

### H. Beyer, Downes, Mathis & Rapley (2025) RAST
- Title: "U.S. multinationals' foreign cash holdings: an empirical estimate and the impact of the tax cuts and jobs act of 2017 on the value of foreign cash"
- DOI: 10.1007/s11142-025-09888-2
- Shock: TCJA Dec 2017
- DV: VALUE of foreign cash (not levels of cash holdings)
- Verdict: **WRONG OUTCOME** (cash valuation, not holdings level)

### I. Jens & Page (2020 WP) "Corporate Cash and Political Uncertainty"
- SSRN 3094415
- Sample: 1987-2016, 385 elections
- Shock: **gubernatorial** elections (NOT Trump 2016)
- DV: cash holdings ✓
- DiD: yes; treatment = firms in election-state vs non-election-state
- Channel: precautionary ✓
- Verdict: **WRONG SHOCK** — perfect on DV/DiD/channel but gubernatorial not Trump

### J. Jens (2024) Financial Management
- Title: "Uncertainty, precautionary saving, and investment: Evidence from prescheduled election cycles"
- *Financial Management*, 53(3)
- Shock: prescheduled gubernatorial elections (NOT Trump 2016)
- DV: cash holdings + investment ✓
- Channel: precautionary ✓
- Verdict: **WRONG SHOCK**

### K. Phan, Nguyen, Nguyen & Hegde (2019) JBR
- Title: "Policy uncertainty and firm cash holdings"
- Abstract verbatim: "This research examines the relation between government economic policy uncertainty and firm cash holdings... policy uncertainty is positively related to firm cash holdings due to firms' precautionary motives and, to a lesser extent, investment delays."
- Shock: NONE — uses Baker-Bloom-Davis EPU index as continuous regressor, no DiD identification
- Verdict: **NOT A DiD DESIGN** — pure correlation/regression on EPU index

### L. Fakhfakh (2026) RBF "Politics of precaution"
- DV: cash holdings via cash-flow sensitivity
- Sample: 2012-2021
- Identification: interaction effects, NOT DiD
- Trump 2016: NOT mentioned
- Verdict: **NOT A DiD DESIGN**

### M. Demir, Javorcik et al. — ScienceDirect S0022199623000971
- Topic: Trump 2018-2019 trade war + firm value
- DV: firm value (NOT cash)
- Verdict: **WRONG OUTCOME**

### N. NBER w31602 — Supply Chain Adjustments to Tariff Shocks
- DV: trade linkages (NOT cash)
- Verdict: **WRONG OUTCOME**

## Eliminated as paywalled / unverifiable
- Springer s11156-022-01049-9 abstract direct fetch failed (403/redirect to login). Identified via search summary as Hasan-Alam-Paramati-Islam 2022 = our H1.6 anchor. Confirmed.
- Tandfonline 2025 RBF paper — paywalled

## Recommendation

Three viable paths forward, none ideal:

| Path | Description | Cost |
|---|---|---|
| **A) Drop H1.5** | Remove from §III.E.4. Lean only on H1.6 (Hasan 2022 redistricting verbatim). Cleaner narrative. | 1-2 hrs prose update |
| **B) Pivot to TCJA** | Replicate Albertus-Glover-Levine 2025 JFE verbatim. Trump POLICY (TCJA Dec 2017) instead of Trump ELECTION (Nov 2016). Channel mismatch (financing not precautionary) — would need framing prose to bridge. | ~5 days redesign + redata + rerun |
| **C) Pivot to Jens-Page** | Replicate Jens-Page 2020 verbatim — gubernatorial elections (NOT Trump). Right channel + right DV + right DiD design. Lose the "Trump shock" narrative entirely. | ~5 days redesign + multi-state data acquisition |

The strict-verbatim-replication user requirement combined with the empirical absence of a Trump-2016-cash-DiD-precautionary precedent leaves no path that satisfies all three: (Trump shock) AND (cash DV) AND (precautionary channel) AND (DiD design) AND (verbatim replication).

The current H1.5 spec is a deliberate template-adaptation (Hu 2024 frame + custom BothHigh treatment) — explicitly NOT verbatim. Per the user's "no inventing" rule, this is unacceptable.

Path A (drop H1.5) is the cleanest no-invention path.

═══════════════════════════════════════════════════════════════════════════════
PHASE 4 — RELAXED CRITERIA SEARCH (added 2026-05-08 PM)
═══════════════════════════════════════════════════════════════════════════════

After Phase 3 confirmed no Trump-2016-election-cash-DiD-precautionary paper exists, user pivoted criteria: "ANY DiD design for cash holdings, through precautionary channel, which potentially would fit our CEO speech uncertainty story."

## Phase 4 search (v4 OpenAlex script)

`tmp/openalex_lit_search_v4.py`:
- 27 keyword queries (broad shock-DiD-cash-precautionary patterns)
- 6 anchor citation chases (ACW 2004 JF, BKS 2009 JF, ACW 2007 JFE, Hassan Brexit 2022 JFQA, Hasan 2022 RQFA, HHLT 2019 QJE)
- Total 1,779 unique works examined
- Filter funnel: 380 mention cash → 19 + DiD term → 10 + precautionary

## Top 3 candidates after Phase 4

| # | Paper | Cites | Journal | Shock |
|---|---|---|---|---|
| 1 | Campello, Cortés, d'Almeida, Kankanhalli (2022) "Exporting Uncertainty: The Impact of Brexit on Corporate America" | 66 | JFQA (top) | June 23 2016 Brexit Referendum |
| 2 | Javadi, Al Masum, Aram, Rao (2023) "Climate change and corporate cash holdings: Global evidence" | 134 | Financial Management | Stern Review release Oct 30 2006 |
| 3 | Chen, Chen, Dhaliwal, Huang (2017) "Accounting Restatements and Corporate Cash Policy" | 11 | JAAF | Irregularity-related restatement events |

## NLM Q1 — verbatim methodology extraction (2026-05-08 PM)

User uploaded all 3 PDFs to NotebookLM. Q1 asked 8 standard methodology questions.

### Paper A (Campello et al 2022 JFQA Brexit) — Q1 verbatim

- **DiD spec:** "Y_{i,t} = α + δ(POST_t × HIGH_UK_EXPOSURE_i) + θ CONTROLS_{i,t-1} + Σ FIRM_i + Σ Σ INDUSTRY_j × QUARTER_t + ε_{i,t}". Treated/control: "we characterize firms as treated (control) units if they are in the upper (bottom) tercile of the nonnegative range of the β_i^UK distribution." Alt 10-K measure: "807 firms are assigned to the treated category (2015 10-K mentions of Brexit terms > 5). A total of 433 firms in the control category have no mentions of Brexit-related terms in their 10-Ks."
- **Sample:** "U.S. companies from the first calendar quarter of 2010 to the fourth quarter of 2016. We drop utility and financial firms, as well as companies whose market value or book assets are lower than $10 million. The sample used in our baseline investment tests consists of 41,630 observations (firm-quarters)."
- **DV CASH:** "CASH is defined as cash and short-term investments divided by lagged total assets." Table 8 alt: "CASH is defined as total cash holdings divided by lagged total assets net of cash holdings." Winsorized 1%.
- **Channel verbatim:** "in line with literature on corporate liquidity management suggesting that, in times of heightened volatility, firms with higher market exposure are likely to increase liquid asset holdings for precautionary reasons (e.g., Acharya, Almeida, and Campello (2013))." "precautionary behavior will lead firms to change the composition of assets on their balance sheets, leading to the accumulation of the most liquid assets."
- **Identification:** Parallel trends "formal tests supporting the presence of parallel trends across all outcome variables" (Tables C4, C5). Two placebo events: David Cameron's election as PM (2015:Q3) + U.S. Debt Ceiling Crisis (2011:Q2-Q4). "DID coefficients are statistically insignificant in all such cases" (Table 12 cols 5-8).
- **Headline result:** Table 8: "POST × HIGH_β^UK = 0.231*** (0.059); POST × HIGH_10K_ENTRIES = 0.357*** (0.062)"
- **Caveats:** USD-GBP depreciation (9% pound depreciation) confound on first-moment expectations; "confounding uncertainty effects associated with the election of President Donald Trump in the United States."
- **Earnings calls:** Authors EXPLICITLY REJECT calls: "We choose not to rely on conference calls in light of ample evidence on severe problems with the information content of such calls (see Hollander, Pronk, and Roelofsen (2010), Matsumoto, Pronk, and Roelofsen (2011), and Bushee, Jung, and Miller (2011))."

### Paper B (Javadi et al 2023 FM Climate) — Q1 verbatim

- **DiD spec:** "Following Painter (2020), we use the release of the Stern Review on October 30, 2006, as an exogenous shock to climate change awareness and conduct a quasi-natural experiment." STERN dummy = 1 after 2006, 0 otherwise. Predicted positive coefficient on DROUGHT_TREND × STERN. Exact equation extracted in Q2 below.
- **Sample:** "unbalanced panel of 384,966 firm-year global observations from 41 different countries, including the United States, from 1985 to 2014." "37,361 unique firms in the data set of which 11,632 are U.S. firms." Drop SIC 49 + 60-69, MV<$10M, missing SIC, >100% asset/sales change.
- **DV CASH:** "CASHi,x,t is our dependent variable, which we define as the ratio of cash and marketable securities to total assets of firm i located in country x in year t." Source: Compustat. Winsorized 1% top + bottom (except DROUGHT_TREND).
- **Channel verbatim:** "Overall, results fit consistently within the precautionary motive framework and suggest that firms hold more cash to safeguard against the adverse impact of climate change." "Bolton et al. (2011, 2013) predicts that firms will hold more cash for precautionary savings, leading to our main hypothesis."
- **Identification:** Stern Review as exogenous shock + placebo via DROUGHT_TREND replacement: "match firms in locations with the highest and lowest DROUGHT_TREND exposures... replace the DROUGHT_TREND of those with the highest exposure with that of their matched firms with the lowest exposure... placebo tests show no relationship between DROUGHT_TREND and cash holdings."
- **Headline result:** "interaction term is significantly positive." "corporate cash holdings increased significantly by about 4.1% following the release of the Stern Review." Exact coef extracted in Q2 below.
- **Caveats:** "hard to fully rule out that the observed effects are not driven by some country-level characteristics correlated with climate change exposure and this is a caveat of our analysis." "results may be driven by an omitted variable that affects both firms' decisions to hold cash and the climate risks." Authors acknowledge they "cannot completely rule out spurious correlations."
- **Earnings calls:** YES — uses Sautner et al (2023) firm-level climate-exposure measure: "These authors use a machine learning methodology to measure the attention paid to climate change risk by the participants in earnings calls." "The exposure measure counts the number of times that climate change bigrams occur in an earnings call over the total number of bigrams in the same transcript."

### Paper C (Chen et al 2017 JAAF Restatements) — Q1 verbatim

- **DiD spec:** "We identify a sample of 949 firms that announced accounting restatements from 1997 through 2006... we match each restatement firm with a non-restatement firm based on a propensity score, and we conduct a difference-in-differences test." "We define the fiscal year of the restatement announcement as year 0." Equation: "CASH_{i,t} = a_i + b POST_{i,t} + CONTROLS + e_{i,t}, (1)." "POST is a dummy variable that equals 1 after the restatement, and 0 before the restatement. The treatment effect of the restatements on the level of cash holdings is captured by the difference in the coefficient on POST (b) between the restatement and control firms."
- **Sample:** "restatements announced from January 1997 through June 2006." Drop SIC 6000-6999 + 4900-4999, missing fin data, cash > total assets, MV/BV < $10M, growth >100%. Final 949 restatements (679 errors + 270 irregularities).
- **DV CASH:** "CASH is the level of cash holdings, defined as cash and short-term investments (Compustat data item #CHE) scaled by total assets (#AT)." Winsorization NOT IN PAPER.
- **Channel verbatim:** "firms increase cash holdings after the restatements due to a higher demand for precautionary savings." "strengthened shareholder control after restatements forces managers to disgorge excess cash and reduce cash holdings. The effect of precautionary savings dominates the effect of strengthened shareholder control, so we observe a net increase in cash."
- **Identification:** "ensure that any change in cash holdings is not driven by a time trend (Bates et al., 2009)" via PSM matching. "We also include the level of and the change in cash holdings (CASH and DCASH) in the regression (X3) to control for the trends in the cash holdings before the restatements." Pre-trends placebo NOT IN PAPER.
- **Headline result:** "In column 5, the coefficient on POST for the irregularity firms is positive and highly significant (0.046, t = 4.84) and in column 6, the corresponding coefficient for the control firms is positive but smaller (0.012, t = 1.90). The treatment effect of irregularity-related restatements is significant (0.034; p = .002)."
- **Caveats:** Real-option uncertainty channel acknowledged: "Restatements can increase managers' uncertainty about investment opportunities. Real option theory (Dixit & Pindyck, 1994) suggests that this uncertainty decreases a firm's (partially) irreversible investment... To the extent that any funds reallocated from investment opportunities are saved as cash, restatements will increase firms' cash holdings." Agency caveat: "it is not clear whether this is sufficient to offset the negative effect of perceived agency problems."
- **Earnings calls:** NOT IN PAPER.

## NLM Q2 — fault-probing verbatim (2026-05-08 PM)

### Paper A — Q2 fault probes

- **A1 (earnings-call critique full):** Single sentence; cites Hollander-Pronk-Roelofsen 2010, Matsumoto-Pronk-Roelofsen 2011, Bushee-Jung-Miller 2011. Just "severe problems with the information content of such calls" — no deeper argument. NOT a blocker for our extension.
- **A2 (Trump-2016 contamination):** Two methods: "(i) consider an alternative event window that excludes 2016:Q4 from our treatment evaluation period... we compare the third quarter of 2016 with the same quarter of 2015"; (ii) use Wagner-Zeckhauser-Ziegler 2018 methodology to identify Trump "winners/losers" via "10-day cumulative capital asset pricing model (CAPM)-adjusted abnormal stock returns around the Trump election date" then "replicate our baseline tests on investment omitting firms labeled as 'losers' by Wagner et al. (2018)." Solid mitigation.

### Paper B — Q2 fault probes (CRITICAL FAULT FOUND)

- **B1 (regression + DROUGHT_TREND construction):** Equation: "CASH_{i,x,t} = α_0 + β DROUGHT_TREND_{x,t} + γ X_{i,x,t} + δ Macro Factors_{x,t} + Year FE + Industry FE + Country FE + ε_{i,x,t}. (2)". DROUGHT_TREND data sources: NOAA NCEI (US) + UCAR (other countries). Computation: "PDSI_{i,m} = α_i + β_i Time + γ_i PDSI_{i,m-1} + ε_{i,m}. (1) ... We run separate regressions for each country every month." "monthly β_i are obtained by running regression (1) in month m of year t for country i ... We then aggregate the monthly β_i to yearly by taking their arithmetic average during year t. For the ease of exposition, we flip the sign of β_i and multiply it by 1000." Critical: **"DROUGHT_TREND is a country-level measure"** and **"DROUGHT_TREND has only time series variation within each country."** Measurement window: "...using the time-series PDSI data of that country from that time (year t, month m) going back to January 1900."
- **B2 (headline coef):** Table 5 Panel A col 1: "DROUGHT_TREND × STERN coefficient... 0.041*** (5.34)" — t-statistic in parentheses (not SE).
- **B3 (Sautner DiD replication):** NOT IN PAPER. "they do not use it to replicate the Difference-in-Differences quasi-natural experiment using the STERN shock." Authors only use Sautner in baseline panel regressions (Table 8), NOT in the STERN DiD.

⚠⚠ **FATAL FAULT for our purposes:** DROUGHT_TREND is COUNTRY-LEVEL. In a US-only sample (which is what F1D is), DROUGHT_TREND collapses to a single time-series with no firm-level cross-section variation. The DiD identification relies on cross-COUNTRY variation in drought trend, which evaporates in US-only replication. Cannot do verbatim replication on F1D US sample.

### Paper C — Q2 fault probes (UNVERIFIABLE)

- **C1 (PSM procedure):** NOT IN PAPER per NLM extraction. PolyU PDF excerpt is missing the methodology text.
- **C2 (channel-distinguishing test):** NOT IN PAPER per NLM extraction.

⚠ **Replication blocker:** without verbatim PSM procedure + channel-distinguishing test, we cannot do "verbatim replication" as user requires.

## Phase 4 final verdict

| | Paper A Brexit JFQA | Paper B Climate FM | Paper C Restate JAAF |
|---|---|---|---|
| Verbatim replicable in F1D US sample | YES ✓ | NO ✗✗ (country-level treatment kills US-only) | UNKNOWN ? (PDF incomplete) |
| Speech-uncertainty extension feasible | YES ✓ (UncResCEO available) | partial (Sautner-style call exposure exists) | NO ✗ (paper has no calls) |
| Identification rigor | STRONG (parallel trends + 2 placebos) | MODERATE (one placebo via swap) | WEAK (no formal pre-trends) |
| Channel verbatim precautionary | YES ✓✓✓ | YES ✓✓✓ | YES ✓✓ (with agency caveat) |
| Top-tier publication | JFQA ✓ | FM (mid) | JAAF (low) |
| Sample compatible with F1D timeline | 2010Q1-2016Q4 ✓ | 1985-2014 ✓ | 1997-Jun 2006 ✗ (pre-F1D-call era) |

## Final recommendation (pending user decision)

**Pivot H1.5 to verbatim Campello-Cortés-d'Almeida-Kankanhalli 2022 JFQA Brexit replication on cash, plus parallel UncResCEO regression as our novel extension.**

Why Paper A wins:
1. JFQA is top-tier — best journal of the 3
2. F1D earnings-call data covers 2010-2016 robustly
3. Treatment heterogeneity is firm-level (β^UK or 10-K mentions) — replicable in F1D
4. Cash-savings result is strong: β = 0.231-0.357 SE 0.06 ***
5. Identification is rigorous (parallel-trends formal tests + 2 placebo dates)
6. Trump-2016 contamination thoughtfully addressed
7. Earnings-call critique is one sentence — non-blocker; we cite Hassan 2019 PRisk + Sautner 2023 + Dzielinski 2021 as countervailing evidence in §III.E.4 limitation paragraph
8. Speech extension is unambiguous: CEOs of UK-exposed firms talked about Brexit constantly during 2016 calls → UncResCEO parallel regression is natural

Why Paper B fails:
- DROUGHT_TREND country-level → US-only DiD identification collapses
- Authors don't replicate STERN DiD with Sautner earnings-call measure (we'd be combining 2 papers, NOT verbatim)
- Authors flag OVB as caveat themselves

Why Paper C blocks:
- Uploaded PDF is incomplete (PSM procedure + channel test absent from extraction)
- Sample 1997-2006 doesn't overlap F1D earnings-call coverage well (most calls 2008+)

User decision still pending after compaction. If approved, next phase = design H1.5.brexit_did spec verbatim per Campello et al + parallel UncResCEO regression.
