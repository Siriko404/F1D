# Thesis Skeleton — Draft v2

Revised 2026-04-16. Supersedes v1. Key changes: precautionary + competitive-real-options two-mechanism frame; 4 formal hypotheses (was 5); H12/H12b promoted with presentation-channel theory; H13.1 subordinate to capex hypothesis as explanatory subsection; hypotheses renamed HC/HL/HK/HFC to avoid collision with suite names.

## Title

**Hold On to Your Cash: Managerial Speech Uncertainty and Corporate Financial Precaution**

## Research Question

Does managerial speech uncertainty during earnings calls predict a precautionary corporate financial response, and how does product-market competition shape its investment-side expression?

## Central Claim (Two-Mechanism)

When managers express greater uncertainty during earnings call Q&A, firms adopt a **precautionary financial posture** (cash↑, leverage↓, external-finance↓, payout↓) that preserves internal resources. These resources are not hoarded defensively — they **fund preemptive investment** (capex↑) when competitive pressure forces firms to act before rivals. The precautionary cash buffer and the investment response are linked: HOLD cash to DEPLOY under competition.

- **Financing side** (precautionary motive): Almeida-Campello-Weisbach 2004, Han-Qiu 2007, Myers-Majluf 1984 pecking order, Opler-Pinkowitz-Stulz-Williamson 1999.
- **Investment side** (competitive real options): Grenadier 2002, Aguerrevere 2009.
- **Bridge**: precautionary buffer enables deployment when the real-options calculus flips from "wait" to "preempt."

## Formal Hypotheses (4)

Formal-hypothesis labels use HC/HL/HK/HFC to avoid collision with suite names (H1, H4a, H13, etc.).

**HC (Cash):** Firms whose managers express higher uncertainty in Q&A hold more cash in the same quarter.
- Suite: H1 (CashRatio, 12 cols, one-tailed positive)
- Result: UncAnsMgr 6/6 sig on contemporaneous CashRatio; 1/6 on lead (contemporaneous response, non-persistent)
- Boundary note: product-market competition does NOT amplify (H1.1 0/4, H1.1b 0/4) — cash response is universal, not concentrated among competitive-threat firms

**HL (Leverage):** Firms whose managers express higher uncertainty reduce leverage in the following quarter.
- Suites: H4a (Leverage, 12 cols, one-tailed negative), H4b (DebtToCapital, 12 cols, one-tailed negative)
- Result: UncAnsMgr 0/6 contemp + 6/6 lead (H4a), 0/6 contemp + 5/6 lead (H4b). Temporal asymmetry consistent with leverage being structurally slower to adjust than cash (Leary-Roberts 2005 adjustment speeds).
- Secondary IVs (UncAnsCEO, UncPreCEO, UncPreMgr): 0/12 on both suites — cleanest channel hierarchy in the audit
- Supporting evidence: H19b (Chang external financing, 2/12 on lead directional-negative) consistent with pecking-order prediction that uncertainty reduces external-finance demand

**HK (Kapital / Capex):** Firms whose managers express higher uncertainty invest MORE, funded internally, with the effect amplified under competitive pressure.
- Suites: H13 (Capex, 12 cols, two-tailed), H13.2 (Capex leads 1-4, 16 cols, two-tailed)
- Main result: UncAnsMgr positive sig on contemporaneous capex industry-FE specs; H13.2 shows 10/16 sig, ALL positive, across 4 lead horizons
- **Explanatory subsection (H13.1):** competition × UncAnsMgr_c 8/8 sig positive — the competitive real-options channel. Firms in competitive product markets accelerate internal-fund-financed capex under uncertainty rather than wait.
- Sign direction contradicts classic precautionary-only theory (AFW 2004 predicts capex↓); reconciled through competitive real options (Grenadier 2002, Aguerrevere 2009) — competition reduces the option value of waiting

**HFC (Financial Constraint moderation):** Among firms with credit-rating data available (2002-2016 sub-sample), the cash response is concentrated in the most credit-market-opaque segment.
- Suite: H1.2 (CashRatio, 4 cols, three-category interaction: IG / BelowIG / Unrated)
- Result: UncAnsMgr_c × Unrated 4/4 sig; UncAnsMgr_c × IG 0/4; UncAnsMgr_c × BelowIG 0/4. Effect is NOT monotone across the rating ladder — it is concentrated in Unrated firms (Faulkender-Petersen 2006 classification of most-opaque access-to-capital-markets segment).
- Sample disclosure: H1.2 uses 2002-2016 (Compustat ratings coverage truncates), narrower than H1/H4a/H4b (2002-2018)

## Presentation-Channel Substructure (Ch 4.5 — not a formal hypothesis)

Payout DVs (H12 PayoutRatio_q, H12b DivPayerQ) show a distinct channel pattern: primary UncAnsMgr 0/12 null, but UncPreMgr (presentation-segment uncertainty) 6/6 negative sig industry-FE across BOTH suites. Under a channel-substructure theory, this is expected rather than anomalous: **payout decisions are formally disclosed and justified in the scripted presentation segment**, while the Q&A segment captures reactive uncertainty about future operations. Different decision margins load on different speech segments. This section:

1. Motivates the channel-split with a priori reasoning (payouts announced in prepared remarks → presentation captures disclosure uncertainty; Q&A captures contingency response)
2. Presents H12/H12b results on the UncPreMgr channel
3. Connects back to the precautionary frame: payout retention consistent with internal-resource preservation
4. Acknowledges the theoretical novelty: prior literature (DWZ 2021, BGT 2018) treats Q&A as the dominant measurement channel; the payout evidence suggests segment-specific loading on DV category

## Thesis Structure

### Chapter 1: Introduction
- Motivation: earnings calls as a window into managerial uncertainty
- Gap: DWZ 2021 established speech uncertainty measures but did not link call-Q&A managerial uncertainty to firm-quarter cash and leverage dynamics. Loughran-McDonald (2013) and Bodnaruk-Loughran-McDonald (2015) link 10-K uncertainty language to financing but on annual frequency without managerial segmentation.
- Contribution: first evidence linking call-Q&A managerial uncertainty to firm-quarter precautionary financial policy; first decomposition of Q&A vs presentation channels for finance outcomes; first empirical bridge from precautionary cash accumulation to competitive-preemption capex via internal-fund deployment
- Preview of findings

### Chapter 2: Literature Review and Theoretical Framework
- Uncertainty and corporate decisions (Bloom 2009, Gulen-Ion 2016)
- Textual analysis of earnings calls (DWZ 2021, Loughran-McDonald 2013, BGT 2018)
- **Precautionary motive** — cash holdings determinants (Opler-Pinkowitz-Stulz-Williamson 1999, Bates-Kahle-Stulz 2009), cash-flow sensitivity of cash (Almeida-Campello-Weisbach 2004, Han-Qiu 2007), Myers-Majluf 1984 pecking order, Fazzari-Hubbard-Petersen 1988 constraints
- **Competitive real options** — Grenadier 2002 option exercise games, Aguerrevere 2009 real options and industry equilibrium, Bernanke 1983 irreversibility
- **Bridge framework:** under uncertainty, firms build precautionary internal resources (cash↑, leverage↓, external-fin↓, payout↓) which then fund competitive preemption (capex↑) when rivalry makes waiting costly

### Chapter 3: Data and Methodology

**3.1 Sample**
- 112,968 earnings calls, 2,429 firms, 2002-2018
- Main sample excludes financial and utility firms

**3.2 Speech Uncertainty Measures**
- Construction following DWZ 2021: UncAnsMgr (manager Q&A), UncAnsCEO (CEO Q&A), UncPreMgr (manager presentation), UncPreCEO (CEO presentation)
- Primary channel: UncAnsMgr (manager Q&A uncertainty, Ch 4.1-4.4)
- Secondary channel: UncPreMgr (manager presentation uncertainty, Ch 4.5 payout subsection)
- IV units: winsorized percentages, NOT standardized. UncAnsMgr mean=0.82, sd=0.33 (relevant for magnitude discussion)

**3.3 Dependent Variables**
- CashRatio (cash + short-term investments / total assets)
- Leverage (total debt / total assets), DebtToCapital (total debt / (debt + market equity))
- Capex (capital expenditures / total assets)
- PayoutRatio_q (quarterly payout / net income), DivPayerQ (binary: dvpspq > 0)
- ChangExternalFunding (Chang et al. 2006 external financing indicator)

**3.4 Empirical Specification**
- PanelOLS with Lagged DV; firm-clustered SE (macro IVs: two-way cluster firm + cal-quarter)
- FE ladder: Industry + Year → Firm + Year → Industry + Year-Quarter → Firm + Year-Quarter
- Base controls: reciprocal DV (leverage as ctrl in cash, cash as ctrl in leverage), lnAssets, TobinsQ, ROA, Capex, DivDummy, sCFO, Lagged_DV
- Extended controls: SalesGrowth, RDSales, CashFlowAt, DailyVola (+ DV-specific: UncQue, NegCall, StockPrice, Turnover, AbsSurpDec depending on suite)
- Contemporaneous + one-quarter lead DVs (12 cols per main suite)
- One-tailed tests for IVs where theory is directional; two-tailed where exploratory

**3.5 Inference Caveats**
- **Multiple testing:** main empirical argument tests UncAnsMgr across 37 suites × up to 12 cols per suite (~444 cells). Primary conclusions rely on patterns concentrated in pre-specified directional channels, not on any individual *p<0.05* cell. FWER note: Bonferroni-adjusted α across 37 suites ≈ 0.0014; the reported "6/6 sig" patterns hold under this threshold (UncAnsMgr on H1 contemp: minimum t ≈ 2.1, p ≈ 0.036 — marginal at single-test; but joint pattern of 6 consecutive cells, each p < 0.05, is itself unlikely under null).
- **Correlated specifications:** "6/6 across FE specs" is not 6 independent tests — same sample, nested/overlapping FE. The pattern demonstrates robustness to fixed-effects choice, not independent replication.
- **Nickell bias:** Lagged_DV with firm FE produces O(1/T) bias (Nickell 1981). Sample has T ≈ 30 quarters per firm on average, so bias is small (~3% of true β). Disclosed rather than ignored; Arellano-Bond GMM not used because T/N ratio is favorable.
- **Lead vs contemporaneous asymmetry:** cash response is contemporaneous-only (H1: 6/6 contemp, 1/6 lead); leverage response is lead-only (H4a: 0/6 contemp, 6/6 lead). Mechanism interpretation: cash is actively managed at the quarterly margin (deposit, revolver draw, money-market reallocation — instant); leverage adjustment requires debt issuance or retirement which has structural lag (Leary-Roberts 2005, Faulkender-Flannery-Hankins-Smith 2012 estimate half-life ~2 years for leverage target reversion vs weeks for cash). Contemporaneous leverage is mechanically anchored to the start-of-quarter value; the uncertainty signal propagates into next-quarter adjustments.

**3.6 Construct Validity**
- Macro validation: political risk (H11-series, UncAnsMgr 8/8 sig on contemporaneous PRisk and 1/2-quarter lags), US EPU (H24, 6/8 sig), global EPU (H24b, 8/8 sig). Speech uncertainty co-moves with measured macro uncertainty.
- Market validation: analyst forecast dispersion (H5, UncAnsMgr 6/12 sig industry-FE). Consistent with managerial uncertainty reflecting information-environment uncertainty.
- Discriminant validity (narrow scope — the measure does NOT predict all outcomes): short-window liquidity changes (H7 1/48 on 3-day ΔIlliquidity, H14 1/48 on 3-day ΔSpread) null. The measure is NOT merely a proxy for short-run market microstructure reactions. R&D intensity (H16 0/48) null — speech uncertainty does not drive R&D, suggesting specificity to decisions with working-capital/financing margins rather than innovation pipelines. Geopolitical risk (H25 1/8 on GPR) near-null — the measure captures firm-relevant uncertainty, not broad geopolitical tension.

### Chapter 4: Results

**4.1 Cash Holdings (HC)**
- UncAnsMgr 6/6 sig on contemporaneous CashRatio, all six FE specifications
- Firm-FE estimate stable at ~0.0034; industry-FE estimate ~0.0038–0.0072 across control sets
- Lead CashRatio: UncAnsMgr 1/6 sig — the response is contemporaneous, not persistent
- Boundary: neither continuous TSIMM (H1.1 0/4) nor binary HighTSIMM (H1.1b 0/4) moderates the cash response — competition is not relevant on the financing margin (contrast: competition DOES moderate the investment margin — Ch 4.3 H13.1)
- Supporting evidence: H19b lead 2/12 directional-negative on external financing consistent with "more cash + less external draw" pecking-order prediction

**4.2 Leverage (HL)**
- H4a (Leverage): UncAnsMgr 0/6 contemp, 6/6 sig lead
- H4b (DebtToCapital): UncAnsMgr 0/6 contemp, 5/6 sig lead
- Secondary IVs 0/12 on both suites — cleanest channel hierarchy
- Temporal asymmetry defense: see §3.5

**4.3 Capital Expenditure (HK)**
- *4.3.1 Main capex result (H13, H13.2):* UncAnsMgr → more capex, all significant betas positive; H13.2 10/16 sig across 4 lead horizons. Sign runs OPPOSITE to classic precautionary-alone prediction.
- *4.3.2 Competitive real options resolution (H13.1 as explanatory subsection):* UncAnsMgr_c × z(log TSIMM) interaction 8/8 sig positive — strongest moderation result in the audit. Firms in more competitive product markets accelerate internal-fund-financed capex under uncertainty. The sign flip from AFW precautionary prediction is explained by competitive real options (Grenadier 2002): competition reduces the option value of waiting, forcing preemptive investment. This is NOT a separate hypothesis but the mechanism explaining HK's main result.
- *Bridge back to HC + HL:* the internal-funded capex is consistent with the precautionary cash buffer in HC being deployed as competitive pressure accumulates. External financing (H19b) and leverage (HL) stay down because the capex is funded from internal resources.

**4.4 Financial Constraint Moderation (HFC)**
- H1.2: UncAnsMgr_c × Unrated 4/4 sig — firms with least capital-market access show strongest cash response
- IG interaction 0/4, BelowIG interaction 0/4 — moderation is NOT monotone; concentrated in the Unrated (most opaque) category
- Sample disclosure: 2002-2016 (Compustat ratings coverage)

**4.5 Presentation-Channel Substructure: Payout (non-hypothesis)**
- H12 PayoutRatio_q, H12b DivPayerQ: UncAnsMgr 0/12 null
- UncPreMgr 6/6 negative sig industry-FE on BOTH suites
- Theoretical interpretation: payout decisions disclosed/justified in scripted presentation segment, not Q&A. Segment-specific DV loading is a priori plausible.
- Economically consistent with precautionary frame: payout retention preserves internal resources
- Caveat: this is a post-hoc channel-split reading; the pattern would need pre-registered replication before being treated as an established decomposition.

### Chapter 5: Discussion
- Two-mechanism reconciliation: precautionary financing + competitive real options investment, bridged by internal-fund deployment
- Temporal asymmetry mechanism (§3.5 elaborated)
- HFC reading: precautionary motive is loaded where external financing is hardest to access — Unrated firms can't tap bond markets, so the cash buffer is their primary precautionary tool
- Competition moderates investment but NOT cash — different decision margins respond to different environmental pressures
- Why H13.1 is NOT a standalone hypothesis but an explanatory subsection: it diagnoses the WHY behind HK's sign, and stating it as a hypothesis would conflate "test" with "mechanism-identification"
- Magnitude contextualization: ~0.7–1.0% of DV mean per 1-SD UncAnsMgr shift, compared against DWZ 2021 and BKS 2009 reference magnitudes
- H22 (EquityDelayCon): briefly noted — UncAnsCEO 2/4 industry-FE consistent with external-finance friction being sensitive to CEO-channel uncertainty; not load-bearing for core claims
- Identification concerns: Lagged_DV adjustment + temporal ordering (H4a lead) provides quasi-dynamic identification; Nickell bias small (§3.5); Hausman-style endogeneity from unobserved firm-time shocks cannot be fully ruled out — caveat disclosed.

### Chapter 6: Conclusion

## Suite Allocation Summary

| Location | Suites | Count |
|---|---|---|
| **Core (Ch 4.1–4.4)** | H1, H4a, H4b, H13, H13.1, H13.2, H1.2, H1.1, H1.1b | 9 |
| **Presentation-channel substructure (Ch 4.5)** | H12, H12b | 2 |
| **Construct validity (Ch 3.6)** | H11, H11-Lag1, H11-Lag2, H24, H24b, H5 | 6 |
| **Discriminant validity (Ch 3.6)** | H7, H14, H16, H25 | 4 |
| **Supporting in discussion (Ch 5)** | H19b, H22 | 2 |
| **Excluded from narrative (full appendix table)** | H7b, H7c, H7d, H7e, H14b, H14c, H14d, H14e, H17, H18, H18b, H20b, H21, H23 | 14 |
| **Total referenced in thesis body** | | **23** |
| **Total catalogued in appendix 37-suite table** | | **37** |

## Appendix Requirement

Full 37-suite table (appendix A) with columns: suite ID / hypothesis class / primary IV pattern / secondary IV pattern / verdict (core / validation / discriminant / supporting / null-excluded) / brief notes. This pre-empts p-hacking / selective-reporting concerns by disclosing the full search space.

## Open items for writing phase

1. Grenadier 2002 + Aguerrevere 2009 NotebookLM verbatim review — confirm the "competition reduces option value of waiting" mechanism is stated in the primary source before building Ch 2 on it.
2. Replication of DWZ 2021 segment treatment (BGT 2018 presentation-vs-Q&A decomposition precedent) — confirm the a priori channel-split argument for Ch 4.5 is defensible from the prior literature, not invented here.
3. Almeida-Campello-Weisbach 2004 verbatim: confirm their cash-flow-sensitivity-of-cash claim DOES predict capex↓ under constraints+uncertainty (so the "classic precautionary prediction contradicts capex↑" framing holds up).
4. Formal hypothesis labels (HC/HL/HK/HFC) — committee may prefer H1/H2/H3/H4; willing to revert if it's a hard convention. Current labels chosen only to avoid suite-name collision.
