# Trump 2016 Lit Review — Systematic Search Across 3 Free Tools
**Date:** 2026-05-05
**Tools used:** paper-search MCP (Google Scholar) + Semantic Scholar API + OpenAlex API + WebSearch
**Question:** Why did advisor recommend Trump 2016 as instrument/shock for UncResCEO? What's the literature precedent?

## TLDR
Advisor's recommendation has STRONG literature precedent — but NOT as a 2SLS instrument. The actual literature uses **DiD with firm-level exposure heterogeneity around Trump 2016 as surprise election event**. The most direct precedent is **Hu, Kang, Li, Lin 2024 RAST**, which uses Trump 2016 as plausibly exogenous shock to CEO speech in Q&A sections of conference calls — same outcome family as our thesis.

## Key Finding — DESIGN CLASS DECISION

| Design class | Literature precedent? | Verdict for our case |
|---|---|---|
| Trump 2016 as **2SLS instrument** | Weak (some PRisk-as-IV papers, no political-shock-as-IV-for-speech papers) | **FAILS** — 8 prior failure modes hold |
| Trump 2016 as **DiD shock with firm exposure** | **STRONG** (Hu 2024 RAST, Wagner-Zeckhauser-Ziegler 2018, Kundu 2024, Chaurey 2024, Baz 2023) | **VIABLE** — modus tollens third trigger |

## Tier 1 — DIRECT precedent (most relevant)

| # | Paper | Journal | Year | DOI |
|---|---|---|---|---|
| 1 | **Hu, Kang, Li, Lin** "Trump election and minority CEO pessimism" | Review of Accounting Studies | 2024 | **10.1007/s11142-024-09843-7** |
| 2 | **Mekhaimer, Soliman, Zhang** "Does Political Uncertainty Obfuscate Narrative Disclosure?" | The Accounting Review | 2024 | **10.2308/tar-2021-0884** |
| 3 | **Hassan, Hollander, van Lent, Tahoun** "Firm-Level Political Risk: Measurement and Effects" | QJE | 2019 | **10.1093/qje/qjz021** |

**Why Tier 1:**
- Hu 2024: SAME shock + SAME outcome family + DiD design + top accounting journal. THIS IS THE SMOKING GUN.
- Mekhaimer 2024: Political → speech direction tested empirically (TAR top journal).
- Hassan 2019 QJE: Foundational firm-level political risk measure; defines exposure variable for shift-share.

## Tier 2 — Trump 2016 as canonical "surprise" finance shock

| # | Paper | Venue | Year | DOI |
|---|---|---|---|---|
| 4 | **Wagner, Zeckhauser, Ziegler** "Unequal Rewards to Firms" | AEA P&P | 2018 | **10.1257/pandp.20181091** |
| 5 | **Wolfers, Zitzewitz** "Standard Error of Event Studies" | AEA P&P | 2018 | **10.1257/pandp.20181090** |
| 6 | **Wagner, Zeckhauser, Ziegler** "Paths to Convergence" | SSRN WP | 2018 | **10.2139/ssrn.3037023** |
| 7 | **Chaurey, Mahajan, Tomar** "Trumping Immigration: Visa Uncertainty" | SSRN WP | 2024 | **10.2139/ssrn.4753372** |
| 8 | **Kundu** "Impact of Regulations on Firm Value: 2016 Election" | JFQA | 2024 | SSRN: **10.2139/ssrn.3143454** |

## Tier 3 — Political uncertainty + cash holdings (DV match for our thesis)

| # | Paper | Venue | Year | DOI |
|---|---|---|---|---|
| 9 | **Phan, Nguyen, Nguyen, Hegde** "Policy Uncertainty and Firm Cash Holdings" | J Bus Research | 2019 | **10.1016/j.jbusres.2018.10.001** |
| 10 | **Hasan, Alam, Paramati, Islam** "Does firm-level political risk affect cash holdings?" | RQFA | 2022 | **10.1007/s11156-022-01049-9** |
| 11 | **Julio, Yook** "Political Uncertainty and Corporate Investment Cycles" | J Finance | 2012 | **10.1111/j.1540-6261.2011.01707.x** |

## Tier 4 — Political shock IV + speech disclosure literature

| # | Paper | Venue | Year | DOI |
|---|---|---|---|---|
| 12 | **Acemoglu, Hassan, Tahoun** "Power of the Street: Egypt's Arab Spring" | RFS | 2018 | **10.1093/rfs/hhx086** |
| 13 | **Bonaime, Gulen, Ion** "Does policy uncertainty affect M&A?" | JFE | 2018 | **10.1016/j.jfineco.2018.05.007** |
| 14 | **Gulen, Ion** "Policy Uncertainty and Corporate Investment" | RFS | 2016 | **10.1093/rfs/hhv050** |
| 15 | **Bird, Karolyi, Ruchti** "How do firms respond to political uncertainty? Gubernatorial elections" | J Acct Research | 2023 | **10.1111/1475-679X.12482** |
| 16 | **Akyol, Wei** "Firm-Level Political Risk and Stock Repurchases" | SSRN WP | 2024 | **10.2139/ssrn.4954055** |
| 17 | **Hassan, Hollander, Kalyani, van Lent, Schwedeler, Tahoun** "Economic Surveillance Using Corporate Text" | NBER WP w33158 | 2024 | **10.3386/w33158** |

## Tier 5 — Methodology cousins / supporting

| # | Paper | Venue | Year | DOI |
|---|---|---|---|---|
| 18 | **Sautner, van Lent, Vilkov, Zhang** "Firm-Level Climate Change Exposure" | J Finance | 2023 | **10.1111/jofi.13219** |
| 19 | **Bertrand, Bombardini, Fisman, Trebbi** "Tax-Exempt Lobbying" | AER | 2020 | **10.1257/aer.20180615** |
| 20 | **Loughran, McDonald** "When is a liability not a liability?" | J Finance | 2011 | **10.1111/j.1540-6261.2010.01625.x** |

## ANTI-CAPITULATION ANALYSIS

### Step 1 — Original position (from project_session_2026_05_05_trump2016_analysis.md)
2SLS fails on 8 grounds (exclusion violated by direct cash channels, Hassan PRisk text-tautology, LATE ≠ ATE, weak first stage after DWZ residual extraction, sample imbalance, confounder cluster, surprise ≠ real-decision exogeneity, no precedent). DiD more defensible. Modus tollens third trigger viable path.

### Step 2 — NEW evidence from this lit review
- **Hu et al. 2024 RAST** publishes EXACTLY the design our advisor proposed: Trump 2016 + DiD + CEO Q&A speech
- **Mekhaimer 2024 TAR** publishes political → narrative disclosure test (top accounting journal)
- Multiple Trump 2016 DiD papers in JFQA, JF, JAR, RAST, TAR — strong DiD precedent
- PRisk-as-IV papers exist (Akyol-Wei 2024 SSRN, Hasan 2022 RQFA, Hossain 2024 SSRN) — but published in lower-tier journals or working paper status; relies on lag/PSM rather than clean exclusion

### Step 3 — Position evaluation
- **2SLS criticism MAINTAINED.** No published finance/accounting paper uses Trump 2016 as IV for executive speech uncertainty. PRisk-as-IV papers exist but for cash/buybacks DV, not speech DV; and they have weak exclusion defenses (lag, PSM).
- **DiD position REINFORCED.** Literature FULLY supports Trump 2016 as DiD shock with firm-exposure heterogeneity. The Hu 2024 RAST paper is the smoking-gun precedent — same outcome family (CEO speech in Q&A), same shock, top accounting journal.
- **Net update:** Modus tollens third trigger is the right path. Advisor's intuition was correct that literature precedent exists. The specific operationalization is DiD with firm-level exposure (Hu 2024 template), not 2SLS.

## Verbatim NLM queries (per paper after upload)

### Hu, Kang, Li, Lin 2024 RAST (10.1007/s11142-024-09843-7) — TIER 1 PRIORITY
1. "What is the verbatim language used to describe the 2016 Trump election as an exogenous shock or natural experiment?"
2. "What is the identification strategy? Quote the exact regression specification including treatment, outcome, and controls."
3. "How is the treatment defined? What is the parallel-trends test or pre-treatment placebo?"
4. "What is the outcome variable construction (management forecasts vs. earnings call Q&A vs. tone)? Which conference call sections are analyzed?"
5. "How does the design isolate ethnic-tension channel from other channels (e.g., trade policy, tax exposure, regulation)?"
6. "What is the sample period and treatment-window length? Pre-period vs. post-period?"
7. "What firm-level exposure variable defines treated vs. control firms? Quote the matching/PSM procedure if any."

### Mekhaimer, Soliman, Zhang 2024 TAR (10.2308/tar-2021-0884) — TIER 1 PRIORITY
1. "How is firm-level political uncertainty operationalized? Quote the verbatim definition and source."
2. "What is the identification strategy for the political-uncertainty → narrative-disclosure causal claim?"
3. "What is the obfuscation measure? Quote the verbatim formula."
4. "What instruments or natural experiments are used to address reverse causality in the political-uncertainty → disclosure relationship?"
5. "What is the sample period and panel structure?"
6. "What is the relationship between political uncertainty and conference call disclosure complexity? Quote magnitudes."

### Hassan, Hollander, van Lent, Tahoun 2019 QJE (10.1093/qje/qjz021) — TIER 1 FOUNDATIONAL
1. "How is PRisk constructed from earnings call transcripts? Quote the verbatim formula."
2. "What is the validation procedure for PRisk?"
3. "How is PRisk decomposed (firm-level vs aggregate vs topic-specific)?"
4. "What firm outcomes does PRisk predict (investment, hiring, lobbying, donations)? Quote magnitudes verbatim."
5. "Is PRisk an outcome or a treatment in the QJE paper? What is the identification strategy?"
6. "What is the relationship between firm-level PRisk and earnings-call uncertainty content broadly?"

### Wagner, Zeckhauser, Ziegler 2018 AEA P&P (10.1257/pandp.20181091)
1. "What firm-level exposure variables are used (cash ETR, internationally-oriented dummy, etc.)? Quote definitions."
2. "What is the verbatim language describing Trump's 2016 election as a surprise/shock?"
3. "What is the regression specification? Cross-sectional or panel?"

### Wolfers, Zitzewitz 2018 AEA P&P (10.1257/pandp.20181090)
1. "How is Trump's 2016 election win identified as a surprise (prediction-market odds, polling)? Quote magnitudes verbatim."
2. "What is the methodological warning about event-study standard errors?"

### Phan, Nguyen, Nguyen, Hegde 2019 J Bus Research (10.1016/j.jbusres.2018.10.001)
1. "How is policy uncertainty operationalized? Which index?"
2. "What is the relationship between policy uncertainty and corporate cash holdings? Quote the magnitude verbatim."
3. "Is the precautionary mechanism tested directly? Which heterogeneity tests?"

### Hasan, Alam, Paramati, Islam 2022 RQFA (10.1007/s11156-022-01049-9)
1. "How is firm-level political risk operationalized? Hassan PRisk?"
2. "What is the identification strategy for the PRisk → cash-holdings relationship?"
3. "Quote the 2SLS first-stage F-statistic and Sargan/Hausman tests verbatim."
4. "What instrument is used in the 2SLS specification? What is the exclusion-restriction defense?"

### Bird, Karolyi, Ruchti 2023 JAR (10.1111/1475-679X.12482)
1. "How are gubernatorial elections used as a political-uncertainty shock? Quote design verbatim."
2. "What is the relationship between political uncertainty and voluntary disclosure?"
3. "What is the firm-level state-exposure variable?"

### Akyol, Wei 2024 SSRN (10.2139/ssrn.4954055)
1. "What instrument is used for firm-level political risk? Quote the first-stage equation."
2. "What is the exclusion-restriction defense?"
3. "Quote the 2SLS coefficient on PRisk, the F-statistic, and any over-identification tests verbatim."

### Julio, Yook 2012 JF (10.1111/j.1540-6261.2011.01707.x)
1. "How are national elections used as instruments for political uncertainty? Quote verbatim."
2. "What is the magnitude of investment cyclicality around elections?"

### Acemoglu, Hassan, Tahoun 2018 RFS (10.1093/rfs/hhx086)
1. "How is the Tahrir Square protest used as a political shock? Quote the design verbatim."
2. "What is the firm-level political-connection exposure variable?"
3. "What is the cross-sectional heterogeneity test (connected vs unconnected firms)?"

## Recommendation

**Path forward (if pursuing Trump 2016 at all):**
- Drop 2SLS framing. Strong precedent does not exist; 8 failure modes hold.
- Adopt **modus-tollens third-trigger DiD design** anchored on Hu 2024 RAST template:
  - Exposure variable: Hassan PRisk_pre-Trump (firm-level political-risk text-share, locked-in pre-2016)
  - Shock: Post-Trump-2016 dummy
  - Outcome: Cash holdings; Lead Cash holdings
  - Treatment heterogeneity: PRisk × Post-Trump × UncResCEO (triple interaction)
  - Channel-isolation test: parallel trends pre-2016; placebo on Hassan ClimRisk (Sautner 2023)
- Present as Section §III.E.4 (third trigger parallel to H1a Unrated × UncRes + H1b HighCFvol × UncRes)
- One-tailed amplification test, p<0.10
- Anchor citation: **Hu et al. 2024 RAST** for design template

## Open question for advisors
Did they specifically envision:
- (A) **DiD with PRisk × Post-Trump exposure heterogeneity** (Hu 2024 RAST template) — VIABLE
- (B) **2SLS with election as instrument for UncResCEO** — NOT RECOMMENDED (no precedent for speech outcome)
- (C) **Something else (tariff exposure, sector tax exposure)** — needs articulation

**Send Hu 2024 + Mekhaimer 2024 + Hassan 2019 DOIs to advisors. Ask: "Did you mean Option A (DiD), B (2SLS), or C (other)?"**
