# Thesis Skeleton — Draft v3

Revised 2026-04-16 evening. Supersedes v2. Key changes: (1) single-question RQ on financial conservatism (observed pattern) motivated by precautionary motive (theoretical mechanism); (2) HK retired as formal hypothesis — H13/H13.1/H13.2 relocate to Ch 4.4 as "documented investment-margin puzzle" with competitive real options interpretation; (3) reverse-engineered cash-buffer-bridge claim removed; (4) 3 formal hypotheses HC/HL/HFC (was 4); (5) title word changed from "Precaution" to "Conservatism" for RQ-title alignment.

## Title

**Hold On to Your Cash: Managerial Speech Uncertainty and Corporate Financial Conservatism**

## Research Question

Does managerial speech uncertainty during earnings calls predict financial conservatism in firms' financing decisions?

## Central Claim

Firms whose managers express greater uncertainty during earnings call Q&A adopt a **financially conservative posture** on the financing margin (cash↑, leverage↓, payout↓, external-finance↓), consistent with the precautionary motive developed in Almeida-Campello-Weisbach 2004, Bates-Kahle-Stulz 2009, Opler-Pinkowitz-Stulz-Williamson 1999, and Riddick-Whited 2009. The effect concentrates in firms with the least capital-market access (Unrated category per Faulkender-Petersen 2006), consistent with the precautionary motive being most binding where external finance is costly.

We additionally document an investment-margin pattern — firms' capital expenditure INCREASES under managerial uncertainty, with the effect concentrated in competitive product markets (H13.1 interaction 8/8 sig positive). This runs OPPOSITE to the precautionary prediction of reduced irreversible investment under uncertainty (AFW 2004; Bernanke 1983). We interpret this documented puzzle through the competitive real options lens (Grenadier 2002; Aguerrevere 2009), under which competitive pressure erodes the option value of waiting. The financing-side conservatism and the investment-margin puzzle are theoretically distinct mechanisms operating on different margins; we do not claim or test a causal or sequencing link between them within this study.

## Formal Hypotheses (3)

Formal-hypothesis labels HC/HL/HFC avoid collision with suite names (H1, H4a, H13, etc.).

**HC (Cash — financial conservatism on the liquidity margin):** Firms whose managers express higher uncertainty in Q&A hold more cash contemporaneously. Literature derivation: AFW 2004 cash-flow sensitivity of cash implies uncertainty increases the marginal value of internal liquidity; BKS 2009 document secular rise in precautionary cash holdings among US firms.
- Suite: H1 (CashRatio, 12 cols, one-tailed positive)
- Result: UncAnsMgr 6/6 sig contemporaneous CashRatio; 1/6 lead (response is contemporaneous, non-persistent)
- Boundary: product-market competition does NOT moderate (H1.1 0/4 continuous TSIMM; H1.1b 0/4 HighTSIMM binary) — the cash response is universal across competitive-structure segments, not concentrated in competitive-threat firms

**HL (Leverage — financial conservatism on the capital-structure margin):** Firms whose managers express higher uncertainty reduce leverage in the following quarter. Literature derivation: precautionary motive implies preserving debt capacity (Minton-Wruck 2009 financial conservatism; Strebulaev-Yang 2013 zero-leverage mystery); Leary-Roberts 2005 establish structural lag in leverage adjustment relative to cash.
- Suites: H4a (Leverage, 12 cols, one-tailed negative), H4b (DebtToCapital, 12 cols, one-tailed negative)
- Result: UncAnsMgr 0/6 contemp + 6/6 lead (H4a); 0/6 contemp + 5/6 lead (H4b). Temporal asymmetry consistent with leverage being structurally slower to adjust than cash.
- Secondary IVs (UncAnsCEO, UncPreCEO, UncPreMgr): 0/12 on both suites — cleanest channel hierarchy
- Supporting evidence: H19b (Chang external financing, 2/12 lead directional-negative) consistent with the pecking-order prediction that uncertainty reduces external-finance demand

**HFC (Financial Constraint moderation — conservatism concentrates where external finance is hardest):** Among firms with credit-rating data available (2002-2016 sub-sample), the cash response is concentrated in the most credit-market-opaque segment. Literature derivation: Faulkender-Petersen 2006 classify Unrated firms as having least-developed access to public debt markets; the precautionary motive binds most tightly where external finance is costliest.
- Suite: H1.2 (CashRatio, 4 cols, three-category interaction: IG / BelowIG / Unrated)
- Result: UncAnsMgr_c × Unrated 4/4 sig; UncAnsMgr_c × IG 0/4; UncAnsMgr_c × BelowIG 0/4. The moderation is NOT monotone across the rating ladder — it is concentrated in Unrated firms.
- Sample disclosure: H1.2 uses 2002-2016 (Compustat ratings coverage truncates), narrower than H1/H4a/H4b (2002-2018)

## Documented Investment-Margin Puzzle (Ch 4.4 — not a formal hypothesis)

We present, as an additional empirical investigation, the relationship between managerial speech uncertainty and the investment margin. The precautionary motive predicts reduced irreversible investment under uncertainty (AFW 2004; Bernanke 1983 irreversibility; Bloom 2009 wait-and-see). The data show the opposite: capital expenditure INCREASES under managerial Q&A uncertainty, robust to firm FE, year-quarter FE, and lead horizons. This is a **documented puzzle** relative to the precautionary prediction, not a tested formal hypothesis.

**Interpretation:** The sign is reconciled by the competitive real options literature — Grenadier (2002) models option-exercise games where competition erodes the value of waiting and triggers preemptive investment; Aguerrevere (2009) shows competitive industry dynamics raise investment under uncertainty relative to the monopolist benchmark. Our data support this reading: the capex↑ response is concentrated in competitive product markets (H13.1 interaction 8/8 sig positive; strongest moderation in the audit).

**Why documented puzzle rather than formal HK:** A formal hypothesis would require literature-driven directional prediction and tested confirmation. Here the prediction from precautionary theory is capex↓; the observed sign is capex↑. Presenting this as "confirmation of HK" would conflate a directional test with a separate-mechanism interpretation. The honest treatment — consistent with standard finance-paper practice — is to document the empirical pattern, flag its opposition to the precautionary prediction, and interpret it through the competitive real options literature without forcing it into the conservatism frame.

**Suites in §4.4:** H13 (Capex, 12 cols, two-tailed), H13.2 (Capex leads 1-4, 16 cols, two-tailed), H13.1 (Competition × UncAnsMgr_c, 8 cols, one-tailed — interpretation subsection).

## Presentation-Channel Substructure (Ch 4.5 — not a formal hypothesis)

Payout DVs (H12 PayoutRatio_q, H12b DivPayerQ) show a distinct channel pattern: primary UncAnsMgr 0/12 null, but UncPreMgr (presentation-segment uncertainty) 6/6 negative sig industry-FE across BOTH suites. Under a channel-substructure theory, this is expected rather than anomalous: **payout decisions are formally disclosed and justified in the scripted presentation segment**, while the Q&A segment captures reactive uncertainty about future operations. Different decision margins load on different speech segments. This section:

1. Motivates the channel-split with a priori reasoning (payouts announced in prepared remarks → presentation captures disclosure uncertainty; Q&A captures contingency response)
2. Presents H12/H12b results on the UncPreMgr channel
3. Connects back to the conservatism frame: payout retention preserves internal resources, consistent with HC/HL/HFC direction
4. Acknowledges theoretical novelty: prior literature (DWZ 2021, BGT 2018) treats Q&A as the dominant measurement channel; the payout evidence suggests segment-specific DV loading
5. Caveat: this is a post-hoc channel-split reading; the pattern would need pre-registered replication before being treated as an established decomposition

## Thesis Structure

### Chapter 1: Introduction
- Motivation: earnings calls as a window into managerial uncertainty; firm-quarter frequency panel data on speech uncertainty enables tests of the precautionary motive at higher temporal resolution than prior annual 10-K textual studies
- Gap: DWZ 2021 established speech uncertainty measures but did not link call-Q&A managerial uncertainty to firm-quarter cash and leverage dynamics. Loughran-McDonald 2013 and Bodnaruk-Loughran-McDonald 2015 link 10-K uncertainty language to financing but on annual frequency without managerial segmentation.
- Contribution: (1) first evidence linking call-Q&A managerial uncertainty to firm-quarter financial conservatism; (2) first decomposition of Q&A vs presentation channels showing segment-specific DV loading on payout outcomes; (3) documented investment-margin puzzle — capex rises under managerial uncertainty with the effect concentrated in competitive product markets, a pattern consistent with competitive real options (Grenadier 2002) as a mechanism distinct from the precautionary motive that governs the financing-margin response. The financing and investment findings are presented as operating under separate theoretical mechanisms; we do not test a causal or sequencing bridge between them.
- Preview of findings

### Chapter 2: Literature Review and Theoretical Framework

**2.1 Uncertainty and Corporate Decisions**
- Bloom 2009 "wait-and-see" model; Gulen-Ion 2016 policy uncertainty and investment; Bernanke 1983 irreversibility

**2.2 Textual Analysis of Earnings Calls**
- DWZ 2021 speech uncertainty measurement; Loughran-McDonald 2013 10-K tone; BGT 2018 Q&A segment treatment precedent; Larcker-Zakolyukina 2012 CFO identification precedent

**2.3 Precautionary Motive and Financial Conservatism (mechanism for HC/HL/HFC)**
- Cash holdings: Opler-Pinkowitz-Stulz-Williamson 1999 determinants; Bates-Kahle-Stulz 2009 secular rise
- Cash-flow sensitivity of cash: Almeida-Campello-Weisbach 2004; Han-Qiu 2007 extension with financial constraints
- Pecking order: Myers-Majluf 1984; Fazzari-Hubbard-Petersen 1988 financing constraints
- Financial conservatism: Minton-Wruck 2009; Strebulaev-Yang 2013 zero-leverage
- Financial constraints classification: Faulkender-Petersen 2006 credit-rating-access hierarchy
- Propensity to save: Riddick-Whited 2009

**2.4 Competitive Real Options (interpretation for Ch 4.4 investment-margin puzzle)**
- Option exercise under competition: Grenadier 2002 RFS
- Product-market competition and real investment: Aguerrevere 2009 RFS
- Preemption under uncertainty: Dixit-Pindyck 1994 (cited via Grenadier/Aguerrevere); note that AFW 2004 and the precautionary literature alone predict capex↓ under uncertainty; the competitive real options literature provides a separate mechanism that predicts capex↑ in competitive settings

**2.5 Hypothesis Development** (literature → hypotheses)
- From §2.3: precautionary motive under managerial speech uncertainty → financial conservatism on financing margin → HC (cash↑), HL (leverage↓), HFC (effect strongest where external finance is costly)
- §2.4 is theoretical background for Ch 4.4 investment-margin interpretation, NOT for formal hypothesis development. The investment-margin pattern is documented empirically and interpreted post-hoc through Grenadier/Aguerrevere, consistent with standard practice when observed patterns fall outside the main literature-driven prediction.

### Chapter 3: Data and Methodology

**3.1 Sample**
- 112,968 earnings calls, 2,429 firms, 2002-2018
- Main sample excludes financial and utility firms

**3.2 Speech Uncertainty Measures**
- Construction following DWZ 2021: UncAnsMgr (manager Q&A), UncAnsCEO (CEO Q&A), UncPreMgr (manager presentation), UncPreCEO (CEO presentation)
- Primary channel: UncAnsMgr (manager Q&A uncertainty, all core formal tests)
- Secondary channel: UncPreMgr (manager presentation uncertainty, Ch 4.5 payout substructure only)
- IV units: winsorized percentages, NOT standardized. UncAnsMgr mean=0.82, sd=0.33 (relevant for magnitude discussion)

**3.3 Dependent Variables**
- CashRatio (cash + short-term investments / total assets)
- Leverage (total debt / total assets), DebtToCapital (total debt / (debt + market equity))
- Capex (capital expenditures / total assets) — used in documented investment-margin puzzle only
- PayoutRatio_q (quarterly payout / net income), DivPayerQ (binary: dvpspq > 0) — presentation-channel substructure only
- ChangExternalFunding (Chang et al. 2006 external financing indicator) — supporting evidence for HL

**3.4 Empirical Specification**
- PanelOLS with Lagged DV; firm-clustered SE (macro IVs: two-way cluster firm + cal-quarter)
- FE ladder: Industry + Year → Firm + Year → Industry + Year-Quarter → Firm + Year-Quarter
- Base controls: reciprocal DV (leverage as ctrl in cash, cash as ctrl in leverage), lnAssets, TobinsQ, ROA, Capex, DivDummy, sCFO, Lagged_DV
- Extended controls: SalesGrowth, RDSales, CashFlowAt, DailyVola (+ DV-specific: UncQue, NegCall, StockPrice, Turnover, AbsSurpDec depending on suite)
- Contemporaneous + one-quarter lead DVs (12 cols per main suite)
- One-tailed tests for IVs where theory is directional (HC, HL, HFC main hypothesis-driven tests); two-tailed for the documented investment-margin puzzle (H13, H13.2) where the prediction from precautionary theory is directional (capex↓) but the observed result goes the opposite way

**3.5 Inference Caveats**
- **Multiple testing:** main empirical argument tests UncAnsMgr across 37 suites × up to 12 cols per suite (~444 cells). Primary conclusions rely on patterns concentrated in pre-specified directional channels, not on any individual *p<0.05* cell. FWER note: Bonferroni-adjusted α across 37 suites ≈ 0.0014; the reported "6/6 sig" patterns hold under this threshold (UncAnsMgr on H1 contemp: minimum t ≈ 2.1, p ≈ 0.036 — marginal at single-test; but joint pattern of 6 consecutive cells, each p < 0.05, is itself unlikely under null).
- **Correlated specifications:** "6/6 across FE specs" is not 6 independent tests — same sample, nested/overlapping FE. The pattern demonstrates robustness to fixed-effects choice, not independent replication.
- **Nickell bias:** Lagged_DV with firm FE produces O(1/T) bias (Nickell 1981). Sample has T ≈ 30 quarters per firm on average, so bias is small (~3% of true β). Disclosed rather than ignored; Arellano-Bond GMM not used because T/N ratio is favorable.
- **Lead vs contemporaneous asymmetry:** cash response is contemporaneous-only (H1: 6/6 contemp, 1/6 lead); leverage response is lead-only (H4a: 0/6 contemp, 6/6 lead). Mechanism interpretation: cash is actively managed at the quarterly margin (deposit, revolver draw, money-market reallocation — instant); leverage adjustment requires debt issuance or retirement which has structural lag (Leary-Roberts 2005, Faulkender-Flannery-Hankins-Smith 2012 estimate half-life ~2 years for leverage target reversion vs weeks for cash). Contemporaneous leverage is mechanically anchored to the start-of-quarter value; the uncertainty signal propagates into next-quarter adjustments.
- **Financing-investment causal bridge NOT tested:** We estimate the financing-margin responses (HC/HL/HFC) and the investment-margin pattern (Ch 4.4 puzzle) on separate outcome equations. Any theoretical discussion of the relationship between them in Ch 5 is interpretive; within this study no causal, sequencing, or mediating link between the precautionary cash buffer and the investment pattern is tested. A within-firm panel test of "firms accumulating cash THEN increasing capex" would require a different identification strategy and is noted as future work.

**3.6 Construct Validity**
- Macro validation: political risk (H11-series, UncAnsMgr 8/8 sig on contemporaneous PRisk and 1/2-quarter lags), US EPU (H24, 6/8 sig), global EPU (H24b, 8/8 sig). Speech uncertainty co-moves with measured macro uncertainty.
- Market validation: analyst forecast dispersion (H5, UncAnsMgr 6/12 sig industry-FE). Consistent with managerial uncertainty reflecting information-environment uncertainty.
- Discriminant validity (narrow scope — the measure does NOT predict all outcomes): short-window liquidity changes (H7 1/48 on 3-day ΔIlliquidity, H14 1/48 on 3-day ΔSpread) null. The measure is NOT merely a proxy for short-run market microstructure reactions. R&D intensity (H16 0/48) null — speech uncertainty does not drive R&D, suggesting specificity to decisions with working-capital/financing margins rather than innovation pipelines. Geopolitical risk (H25 1/8 on GPR) near-null — the measure captures firm-relevant uncertainty, not broad geopolitical tension.

### Chapter 4: Results

**4.1 Cash Holdings (HC)**
- UncAnsMgr 6/6 sig on contemporaneous CashRatio, all six FE specifications
- Firm-FE estimate stable at ~0.0034; industry-FE estimate ~0.0038–0.0072 across control sets
- Lead CashRatio: UncAnsMgr 1/6 sig — the response is contemporaneous, not persistent
- Boundary: neither continuous TSIMM (H1.1 0/4) nor binary HighTSIMM (H1.1b 0/4) moderates the cash response — competition is not relevant on the financing margin
- Supporting evidence: H19b lead 2/12 directional-negative on external financing consistent with "more cash + less external draw" pecking-order prediction

**4.2 Leverage (HL)**
- H4a (Leverage): UncAnsMgr 0/6 contemp, 6/6 sig lead
- H4b (DebtToCapital): UncAnsMgr 0/6 contemp, 5/6 sig lead
- Secondary IVs 0/12 on both suites — cleanest channel hierarchy
- Temporal asymmetry defense: see §3.5

**4.3 Financial Constraint Moderation (HFC)**
- H1.2: UncAnsMgr_c × Unrated 4/4 sig — firms with least capital-market access show strongest cash response
- IG interaction 0/4, BelowIG interaction 0/4 — moderation is NOT monotone; concentrated in the Unrated (most opaque) category
- Sample disclosure: 2002-2016 (Compustat ratings coverage)

**4.4 Documented Investment-Margin Puzzle (not a formal hypothesis)**
- H13 (Capex, 12 cols, two-tailed): UncAnsMgr all significant betas POSITIVE — opposite of the precautionary-motive prediction (capex↓ per AFW 2004, Bernanke 1983)
- H13.2 (Capex leads 1-4, 16 cols, two-tailed): UncAnsMgr 10/16 sig, ALL positive across 4 lead horizons — pattern persists over the lead window
- *Interpretation subsection — H13.1 competition moderation:* UncAnsMgr_c × z(log TSIMM) 8/8 sig positive — strongest moderation in the audit. The capex↑ effect is concentrated in competitive product markets, consistent with the competitive real options literature (Grenadier 2002 option exercise games; Aguerrevere 2009 competitive industry equilibrium). Under this interpretation, competition erodes the option value of waiting, triggering preemptive investment when rivals force action.
- *Honest framing:* This is documented empirical evidence interpreted post-hoc through the competitive real options literature — a separate mechanism from the precautionary motive that governs §4.1-4.3. We do not claim the two responses are causally linked or that the cash accumulation in §4.1 funds the investment in §4.4; these are separate outcome equations on the same IV, and any sequencing interpretation is theoretical not tested.

**4.5 Presentation-Channel Substructure: Payout (non-hypothesis)**
- H12 PayoutRatio_q, H12b DivPayerQ: UncAnsMgr 0/12 null
- UncPreMgr 6/6 negative sig industry-FE on BOTH suites
- Theoretical interpretation: payout decisions disclosed/justified in scripted presentation segment, not Q&A. Segment-specific DV loading is a priori plausible.
- Economically consistent with conservatism frame: payout retention preserves internal resources (cash↑ is the mirror image)
- Caveat: this is a post-hoc channel-split reading; the pattern would need pre-registered replication before being treated as an established decomposition

### Chapter 5: Discussion

**5.1 Financial Conservatism Under Managerial Speech Uncertainty**
- HC/HL/HFC together describe a consistent conservatism pattern: cash↑, leverage↓, effect concentrated among Unrated firms
- Consistent with precautionary motive literature (AFW 2004, BKS 2009, OPSW 1999, Riddick-Whited 2009) adapted to a novel IV (call-Q&A managerial uncertainty) at a higher temporal resolution (firm-quarter) than prior annual-10-K studies
- Temporal asymmetry mechanism (§3.5 elaborated): cash responds contemporaneously, leverage with a lag — consistent with adjustment-cost asymmetry

**5.2 Investment-Margin Puzzle and Competitive Real Options**
- The capex↑ pattern is inconsistent with a pure precautionary-motive reading of the IV
- Grenadier 2002 + Aguerrevere 2009 provide an alternative theoretical lens specific to competitive industry dynamics: competition erodes the option to wait, inducing preemptive investment
- H13.1 8/8 competition × uncertainty positive interaction empirically supports this interpretation
- We frame this as a documented finding with a separate theoretical mechanism, not a unification of two literatures. Attempting to frame capex↑ as also "precautionary" (under a coined umbrella) was rejected because the precautionary and competitive real options literatures model the two motives as distinct (e.g., Gao-Zhao 2022 explicitly models them as "competing forces"), and "preemptive precaution" is not an established concept in top-tier finance literature

**5.3 Relationship Between the Financing and Investment Responses**
- Both responses share a common IV (UncAnsMgr) but operate through different mechanisms (precautionary motive for financing; competitive real options for investment)
- A cross-literature synthesis would require new theoretical work connecting the two mechanisms; this thesis does not attempt that synthesis
- Future research directions: within-firm panel identification of sequencing (cash accumulation → capex deployment), or joint estimation in a structural model with both mechanisms active

**5.4 Presentation-Channel Substructure (payout)**
- H12/H12b presentation-channel reading is framed as a post-hoc observation requiring pre-registered replication
- Consistent with conservatism (payout retention = internal resource preservation) but channel-specific loading is a novel measurement claim, not established in prior segment-decomposition work

**5.5 Identification and Caveats**
- Lagged_DV adjustment + temporal ordering (HL lead) provides quasi-dynamic identification
- Nickell bias small (§3.5)
- Hausman-style endogeneity from unobserved firm-time shocks cannot be fully ruled out — caveat disclosed

### Chapter 6: Conclusion

## Suite Allocation Summary

| Location | Suites | Count |
|---|---|---|
| **Core formal hypotheses (Ch 4.1–4.3)** | H1, H4a, H4b, H1.2, H1.1, H1.1b | 6 |
| **Documented investment-margin puzzle (Ch 4.4)** | H13, H13.1, H13.2 | 3 |
| **Presentation-channel substructure (Ch 4.5)** | H12, H12b | 2 |
| **Construct validity (Ch 3.6)** | H11, H11-Lag1, H11-Lag2, H24, H24b, H5 | 6 |
| **Discriminant validity (Ch 3.6)** | H7, H14, H16, H25 | 4 |
| **Supporting in discussion (Ch 5)** | H19b, H22 | 2 |
| **Excluded from narrative (full appendix table)** | H7b, H7c, H7d, H7e, H14b, H14c, H14d, H14e, H17, H18, H18b, H20b, H21, H23 | 14 |
| **Total referenced in thesis body** | | **23** |
| **Total catalogued in appendix 37-suite table** | | **37** |

## Appendix Requirement

Full 37-suite table (appendix A) with columns: suite ID / hypothesis class / primary IV pattern / secondary IV pattern / verdict (core-formal / puzzle / validation / discriminant / supporting / null-excluded) / brief notes. This pre-empts p-hacking / selective-reporting concerns by disclosing the full search space.

## Open items for writing phase

1. **Grenadier 2002 + Aguerrevere 2009 NotebookLM verbatim review** — confirm the "competition reduces option value of waiting" mechanism is stated in the primary source before building Ch 2.4 and Ch 4.4 interpretation on it. [Pending — NotebookLM F1D notebook is authenticated; run verbatim extraction in next writing session.]
2. **Replication of DWZ 2021 segment treatment (BGT 2018 presentation-vs-Q&A decomposition precedent)** — confirm the a priori channel-split argument for Ch 4.5 is defensible from prior literature, not invented here.
3. **AFW 2004 verbatim** — confirm their cash-flow-sensitivity-of-cash claim DOES predict capex↓ under constraints+uncertainty (so the "precautionary prediction is capex↓, which is contradicted by the data" framing in Ch 4.4 is rigorously grounded).
4. **Minton-Wruck 2009 + Strebulaev-Yang 2013 verbatim** — confirm "financial conservatism" usage in top-tier literature for cash↑/leverage↓ cluster (HL section grounding).
5. **Hypothesis labels HC/HL/HFC** — committee convention check. Current labels chosen to avoid suite-name collision; willing to revert to H1/H2/H3 if committee prefers.

## Changes from v2 (2026-04-16 evening)

1. **Title word:** "Precaution" → "Conservatism" (RQ-title alignment)
2. **RQ:** single-question; Part 2 on competition/investment REMOVED. "Financial response" → "financial conservatism in firms' financing decisions" — scope restricted to financing side
3. **Formal hypotheses:** 4 (HC/HL/HK/HFC) → 3 (HC/HL/HFC). HK retired as formal hypothesis — literature-driven prediction from precautionary theory was capex↓, observed sign was capex↑, so forcing HK into the precautionary frame was reverse-engineered
4. **HK content (H13/H13.1/H13.2) relocated** from "formal hypothesis" to "Ch 4.4 documented investment-margin puzzle with competitive real options interpretation"
5. **Cash-buffer-bridge claim REMOVED** — v2 claimed firms "HOLD cash to DEPLOY under competition" as the mechanism linking financing conservatism and capex↑. This was a reverse-engineered post-hoc synthesis; no paper in the top-tier literature unifies precautionary motive and competitive real options, and Gao-Zhao (2022) explicitly models them as "competing forces." The bridge is removed from the thesis claims; the two responses are presented as operating on separate mechanisms
6. **Contribution claim (Ch 1) restructured:** "first empirical bridge from precautionary cash accumulation to competitive-preemption capex via internal-fund deployment" → "documented investment-margin puzzle consistent with competitive real options as a separate mechanism"
7. **§3.5 adds new caveat:** financing-investment causal bridge NOT tested — separate outcome equations, any sequencing interpretation is theoretical
8. **§5 restructured** into 5 subsections: financial conservatism (§5.1), investment puzzle (§5.2), relationship (§5.3, theoretical only), presentation substructure (§5.4), identification (§5.5)
9. **Literature section Ch 2** restructured to separate precautionary-motive background (§2.3, drives HC/HL/HFC formal hypotheses) from competitive-real-options background (§2.4, interpretive frame for Ch 4.4 puzzle only, NOT used in formal hypothesis development)
10. **Suite allocation:** 9 core → 6 core + 3 puzzle (total 23 body unchanged)
11. **Hypothesis-development flow** (§2.5): literature → hypotheses explicit; §2.4 flagged as interpretive background not hypothesis-generating

## What does NOT change from v2

- Empirical data, audit results, 37-suite inventory
- Panels, runners, all_tables.tex
- Sample (112,968 calls, 2,429 firms, 2002-2018; H1.2 narrowed to 2002-2016)
- IV construction (DWZ 2021 following)
- "First evidence" novelty claim on call-Q&A managerial uncertainty at firm-quarter frequency
- 37-suite appendix requirement for p-hacking defense
- Presentation-channel substructure (Ch 4.5) reading
- Construct + discriminant validity Ch 3.6 treatment
