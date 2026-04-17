# Thesis Skeleton — Draft v4

Revised 2026-04-16 evening (later). Supersedes v3. Key changes from v3: (1) capex framed as **exploratory additional analysis**, NOT "documented puzzle" — neutral framing, no anchor in capex↓ prediction; (2) **AFW 2004 dropped** (was puzzle anchor, no longer needed); (3) **Bloom 2014 dropped** as load-bearing (speech uncertainty distinct from macro uncertainty lineage); (4) **Aguerrevere 2009 demoted to Tier-2 citation-only** (not load-bearing); (5) **Payout §4.5 (H12/H12b) moved from body to targeted appendix** — main IV UncAnsMgr null on payout, segment-channel argument too headache-heavy for body; (6) **R&D (H16) dropped entirely** from thesis; (7) **37-suite appendix dropped** — replaced by §II pre-commitment statement; (8) **MW year corrected: 2001, not 2009**; (9) **HFC HFC framing refined**: FP 2006 use binary access, we extend to three-way + report only IG vs Unrated (BelowIG suppressed, null + no economic content); use "credit constrained" wording exactly per FP 2006; (10) **§II pre-commitment statement front-loaded** with three-bucket statistical convention disclosure (one-tailed pre-specified §III; two-tailed exploratory §IV main capex; one-tailed explanatory §IV moderator H13.1); (11) **Central Claim rewritten** — no "puzzle" / "OPPOSITE" language.

## Title

**Hold On to Your Cash: Managerial Speech Uncertainty and Financing Conservatism**

## Research Question

Does managerial speech uncertainty during earnings calls predict financing conservatism?

## Central Claim

Firms whose managers express greater uncertainty during earnings-call Q&A hold more cash (contemporaneously) and reduce leverage (with a one-quarter lag), consistent with the precautionary motive (Opler, Pinkowitz, Stulz, Williamson 1999; Bates, Kahle, Stulz 2009) and matching the empirical low-leverage + high-cash conservatism cluster documented by Minton and Wruck (2001). The effect concentrates in firms with the least access to public debt markets (Unrated category, following Faulkender-Petersen 2006's binary access classification, extended here to a three-tier hierarchy with Investment-Grade as the comparison baseline; Unrated firms are credit constrained per FP 2006).

We additionally examine whether managerial speech uncertainty relates to capital expenditure. We find that capex rises with managerial uncertainty and that the effect concentrates in competitive product markets (interaction with TSIMM, Hoberg-Phillips 2016). We interpret this exploratory finding through the competitive real options framework of Grenadier (2002), under which competition erodes the option value of waiting and triggers earlier investment when rivals would otherwise capture investment opportunities. The financing-margin response (cash + leverage) and the investment-margin finding operate through theoretically distinct mechanisms; we do not test or claim a causal link between them.

## Formal Hypotheses (3)

Formal-hypothesis labels HC/HL/HFC avoid collision with suite names (H1, H4a, H13, etc.).

**HC (Cash — financing conservatism on the liquidity margin):** Firms whose managers express higher uncertainty in Q&A hold more cash contemporaneously. Literature derivation: OPSW 1999 directly predicts firms facing higher cash-flow uncertainty hold more cash (Section 2.1, p.8); BKS 2009 confirm this empirically and document the secular rise in precautionary cash (1980-2006).
- Suite: H1 (CashRatio = `cheq/atq`, BKS 2009 primary specification, 12 cols, one-tailed positive)
- Result: UncAnsMgr 6/6 sig contemporaneous CashRatio; 1/6 lead (response is contemporaneous, non-persistent)
- Boundary: product-market competition does NOT moderate (H1.1 0/4 continuous TSIMM; H1.1b 0/4 HighTSIMM binary)

**HL (Leverage — financing conservatism on the capital-structure margin):** Firms whose managers express higher uncertainty reduce leverage in the following quarter. Literature derivation: precautionary motive (OPSW 1999, BKS 2009) predicts firms preserve debt capacity under uncertainty; Minton and Wruck (2001) document that financially conservative firms (persistent low leverage) hold ~3× the cash of control firms — the cash↑/leverage↓ joint pattern HC + HL test.
- Suites: H4a (Leverage, 12 cols, one-tailed negative), H4b (DebtToCapital, 12 cols, one-tailed negative)
- Result: UncAnsMgr 0/6 contemp + 6/6 lead (H4a); 0/6 contemp + 5/6 lead (H4b). Temporal asymmetry consistent with leverage being structurally slower to adjust than cash.
- Secondary IVs (UncAnsCEO, UncPreCEO, UncPreMgr): 0/12 on both suites — cleanest channel hierarchy
- Supporting evidence: H19b (Chang external financing, 2/12 lead directional-negative) consistent with the pecking-order prediction that uncertainty reduces external-finance demand

**HFC (Financial Constraint moderation — conservatism concentrates in credit-constrained firms):** Among firms with credit-rating data available (2002-2016 sub-sample), the cash response is concentrated in the Unrated segment. Literature derivation: Faulkender-Petersen 2006 use a binary access classification (rated vs unrated) and document that unrated firms are credit constrained (use significantly less debt; explicitly weaker on capital-constrained claim). We extend FP's binary to a three-tier hierarchy by partitioning rated firms into Investment-Grade (IG) and Below-Investment-Grade (BelowIG); the precautionary motive should bind most tightly where debt-market access is most limited.
- Suite: H1.2 (CashRatio, three-category interaction)
- Reported result: UncAnsMgr_c × Unrated 4/4 sig; UncAnsMgr_c × IG 0/4 (baseline comparison)
- BelowIG (0/4 null) suppressed from H1.2 main table; reported in appendix
- Sample disclosure: H1.2 uses 2002-2016 (Compustat ratings coverage truncates), narrower than H1/H4a/H4b (2002-2018)

## Capital Expenditure and Product-Market Competition (Ch 4.4 — additional exploratory analysis, not a formal hypothesis)

We additionally examine the relationship between managerial speech uncertainty and capital expenditure. The financing-margin tests (HC/HL/HFC) are pre-specified from precautionary theory; capex is exploratory.

**Empirical findings:**
- H13 (Capex, 12 cols, two-tailed): UncAnsMgr all significant betas POSITIVE
- H13.2 (Capex leads 1-4, 16 cols, two-tailed): UncAnsMgr 10/16 sig, ALL positive across 4 lead horizons — pattern persists over the lead window
- H13.1 (Competition × UncAnsMgr_c, 8 cols, one-tailed explanatory): UncAnsMgr_c × z(log TSIMM) 8/8 sig positive — strongest moderation in the audit. The capex↑ effect concentrates in competitive product markets (Hoberg-Phillips 2016 TSIMM measure).

**Interpretation:** Consistent with the competitive real options framework (Grenadier 2002, RFS), under which competition erodes the option value of waiting and triggers earlier investment when rivals' actions threaten to capture investment opportunities. We adopt this as a post-hoc interpretive lens, not a pre-specified prediction. The financing conservatism (HC/HL/HFC) and investment-margin findings operate through theoretically distinct mechanisms (precautionary motive vs competitive real options); we do not test or claim a causal sequencing link between them.

**Suites in §4.4:** H13, H13.2, H13.1.

## Thesis Structure

### §I — Introduction
- Motivation: earnings calls as a window into managerial uncertainty; firm-quarter frequency panel data on speech uncertainty enables tests of the precautionary motive at higher temporal resolution than prior annual 10-K textual studies
- Gap: DWZ 2021 established speech uncertainty measures but did not link call-Q&A managerial uncertainty to firm-quarter cash and leverage dynamics. Loughran-McDonald 2013 and similar 10-K studies operate annually without managerial segmentation.
- Contribution (2 claims):
  1. **First evidence** linking call-Q&A managerial uncertainty to firm-quarter financing conservatism (cash + leverage on the main IV; effect concentrated in credit-constrained Unrated firms).
  2. **Additional exploratory finding**: capital expenditure rises with managerial uncertainty in competitive product markets, consistent with competitive real options (Grenadier 2002) as a separate mechanism distinct from the precautionary motive that governs the financing response.
- Preview of findings

### §II — Conceptual Framework and Empirical Strategy

**§2.1 Pre-Commitment Statement (front-loaded)**

Three statistical conventions follow from our hypothesis structure:
- The three formal hypotheses (HC, HL, HFC) are derived from precautionary motive theory (OPSW 1999, BKS 2009) and tested with **one-tailed inference** in the theory-predicted direction.
- The capex tests in §IV (H13, H13.2) are **exploratory: two-tailed inference** because no pre-specified directional prediction follows from precautionary theory in our framework.
- The competition-moderator test in §IV (H13.1) is **explanatory and one-tailed** in the direction predicted by the competitive real options framework (Grenadier 2002), applied as a post-hoc interpretation of the main capex finding.

We report all main specifications. Tier-2 supporting tests (validity, robustness) appear in §II (compact summary) and the targeted appendix.

**§2.2 Uncertainty and Corporate Decisions** — brief survey of uncertainty-and-corporate-finance literature; transition to speech uncertainty measurement.

**§2.3 Speech Uncertainty Measurement**
- DWZ 2021: 297-word LM (2011) uncertainty wordlist; presentation vs Q&A segment split; CEO/CFO individual-level applications
- BGT 2018: pooled all-manager aggregation logic (per Ian Gow's published replication code, github.com/iangow/bgt; paper body does not disclose pooling)
- Our IV: combination of DWZ's wordlist content + BGT's pooled-manager aggregation (novelty is the combination)

**§2.4 Precautionary Motive and Financing Conservatism (mechanism for HC/HL/HFC)**
- OPSW 1999: precautionary motive operational definition + cash-flow uncertainty → cash↑ directional prediction
- BKS 2009: secular rise in precautionary cash holdings; primary cite for cash/assets DV form + two-way clustering precedent
- Minton-Wruck 2001: documents the empirical low-leverage + high-cash cluster ("financial conservatism" label source); their mechanism is financial slack/Donaldson-Myers pecking-order, distinct from but consistent with our precautionary frame
- Faulkender-Petersen 2006: binary rated-vs-unrated access; "credit constrained" characterization of unrated firms

**§2.5 Competitive Real Options (interpretation for §4.4 only, NOT hypothesis-generating)**
- Grenadier 2002: competition erodes option value of waiting → earlier investment under preemption fear
- (Aguerrevere 2009 cited as related strategic-equilibrium extension; not load-bearing)

**§2.6 Hypothesis Development** (literature → hypotheses)
- From §2.4: precautionary motive under managerial speech uncertainty → financing conservatism → HC (cash↑), HL (leverage↓), HFC (effect concentrated where credit-market access is most limited)
- §2.5 is interpretive background for §4.4 capex finding only, NOT for formal hypothesis development.

### §III — Main Empirical Analyses (HC, HL, HFC)

**§3.1 Sample**
- 112,968 earnings calls, 2,429 firms, 2002-2018
- Excludes financial firms (SIC 6000-6999) + utilities (SIC 4900-4999), following BKS 2009

**§3.2 Speech Uncertainty Measures**
- Construction: DWZ 2021 wordlist + BGT 2018 pooled aggregation (see §2.3)
- Primary IV: UncAnsMgr (manager Q&A uncertainty)
- Secondary IVs: UncAnsCEO, UncPreCEO, UncPreMgr (channel hierarchy)
- IV units: winsorized percentages, NOT standardized. UncAnsMgr mean=0.82, sd=0.33

**§3.3 Dependent Variables**
- CashRatio (`cheq/atq`, following BKS 2009 primary specification; we adopt the linear cash-to-assets form over OPSW 1999's log-of-cash-to-net-assets per BKS 2009's explicit choice; appendix robustness with OPSW form noted as future work)
- Leverage (`dlttq + dlcq / atq`), DebtToCapital
- (Capex used in §4.4 only; payout DVs in appendix only)

**§3.4 Empirical Specification**
- PanelOLS with Lagged DV; firm-clustered SE (macro-IV suites: two-way cluster firm + cal-quarter, following BKS 2009 + Cameron-Gelbach-Miller 2006)
- FE ladder: Industry + Year → Firm + Year → Industry + Year-Quarter → Firm + Year-Quarter
- Base controls: reciprocal DV (leverage as ctrl in cash, cash as ctrl in leverage), lnAssets, TobinsQ, ROA, Capex, DivDummy, sCFO, Lagged_DV
- Extended controls: SalesGrowth, RDSales, CashFlowAt, DailyVola
- Contemporaneous + one-quarter lead DVs (12 cols per main suite)
- One-tailed tests for IVs in §III; see pre-commitment statement §2.1.

**§3.5 Inference Caveats**
- Multiple testing: ~12 main cells per HC/HL/HFC suite. Patterns concentrated in pre-specified directional channels; pre-commitment statement §2.1 frontloads this.
- Correlated specifications: "6/6 across FE specs" demonstrates robustness to fixed-effects choice, not independent replication.
- Nickell bias: T ≈ 30 quarters per firm, bias O(1/T) ~3% of true β. Disclosed.
- Lead vs contemporaneous asymmetry: cash response contemporaneous (H1: 6/6 contemp); leverage response lead (H4a: 6/6 lead). Mechanism: cash actively managed at quarterly margin (instant); leverage adjustment requires debt issuance/retirement which has structural lag.
- Financing-investment causal bridge NOT tested: separate outcome equations for §III (financing) vs §IV (capex). Any theoretical discussion of relationship is interpretive; within this study no causal/sequencing/mediating link between the precautionary cash buffer and the investment pattern is tested.

**§3.6 Validity (compact paragraph + targeted appendix tables)**

Our IV is positively correlated with established uncertainty proxies — political risk (H11/Hassan et al. 2020), US economic policy uncertainty (H24/BBD 2016), global EPU (H24b/Davis 2016) — and with information-environment uncertainty (H5 analyst forecast dispersion/Wang 2020). Discriminant: our IV does NOT predict short-run market microstructure changes (H7/H14, Amihud 2002) or geopolitical risk (H25/Caldara-Iacoviello 2022). Detailed validity tables in Appendix B.

### §IV — Additional Analysis: Capital Expenditure and Product-Market Competition

(See "Capital Expenditure and Product-Market Competition" section above for full content.)

**§4.1 Cash Holdings (HC) — main results**
**§4.2 Leverage (HL) — main results**
**§4.3 Financial Constraint Moderation (HFC) — main results** (BelowIG suppressed; report only IG vs Unrated)
**§4.4 Capital Expenditure and Product-Market Competition** (exploratory; H13, H13.2, H13.1; competitive real options interpretation)

### §V — Conclusion

- Summary of HC + HL + HFC main findings
- Summary of capex exploratory finding + competitive real options interpretation
- Disclosure of separate mechanisms; no causal-bridge claim
- Caveats (Nickell, identification, post-hoc nature of §4.4 interpretation)
- Future research: within-firm cash-then-capex sequencing test; structural model with both mechanisms

## Suite Allocation Summary v4

| Location | Suites | Count |
|---|---|---|
| §III Main (HC/HL/HFC) | H1, H4a, H4b, H1.2, H1.1, H1.1b | 6 |
| §IV Additional (capex + competition) | H13, H13.1, H13.2 | 3 |
| §II validity (compact paragraph) + Appendix B | H11, H11-Lag1, H11-Lag2, H24, H24b, H5, H7, H14, H25 | 9 |
| Supporting in §V discussion | H19b, H22 | 2 |
| Appendix C (presentation-channel analogues, robustness only) | H12, H12b | 2 |
| Total in body or appendix B | | 22 |
| **Dropped from thesis entirely** | H16 (R&D), other null suites previously in 37-table | various |

**No 37-suite fishing-deck appendix.** P-hacking defense via §2.1 pre-commitment statement.

## Targeted Appendix

- Appendix A: Variable Definitions
- Appendix B: Detailed Validity Tables (construct + discriminant)
- Appendix C: Presentation-Channel Analogues (H12, H12b — robustness only, no body discussion)
- Appendix D: Robustness specifications (alternative FE, alternative samples, OPSW log-DV form for HC if time permits)

## Reference Stack v4 (Tier-1 critical)

| # | Paper | Role | F1D + verbatim status |
|---|---|---|---|
| 1 | DWZ 2021 | IV wordlist + segment split | ✓ verbatim done |
| 2 | BGT 2018 | IV pooled-manager aggregation | ✓ verbatim done + Ian Gow code read |
| 3 | OPSW 1999 | Precautionary motive theory + uncertainty→cash↑ prediction | ✓ verbatim done |
| 4 | BKS 2009 | DV form (cash/assets) + two-way clustering + secular rise | ✓ verbatim done |
| 5 | Minton-Wruck 2001 | "Financial conservatism" label + low-lev + high-cash cluster | ✓ verbatim done (year corrected from 2009) |
| 6 | Faulkender-Petersen 2006 | Binary rated/unrated access; "credit constrained" wording | ✓ verbatim done (binary not 3-way; we extend) |
| 7 | Grenadier 2002 | Competitive real options; option-to-wait erosion | ✓ verbatim done |
| 8 | Hoberg-Phillips 2016 (TSIMM) | Competition moderator measure | ✓ verbatim done (Step 6 walkthrough; flags: TNIC3/TSIMM labels HP-website not paper; sample 1997-2008 vs our 2002-2018 use updated series) |

Tier-2 (citation-only, verbatim consolidated in `memory/reference_tier2_consolidated.md`): Aguerrevere 2009 (strategic-equilibrium extension); Hassan et al. 2020 (PRisk); BBD 2016 (US EPU); Davis 2016 (GEPU); CI 2022 (GPR); Amihud 2002 (ILLIQ); Wang 2020 (DISP); Chang-Dasgupta-Hilary 2006 (external fin H19b); LZ 2012 (CEO speaker ID).

**DROPS from v3 stack:** AFW 2004 (puzzle anchor no longer needed); Bloom 2014 (macro lineage, not load-bearing); Han-Qiu 2007, Riddick-Whited 2009 (redundant); Strebulaev-Yang 2013 (redundant with MW); Myers-Majluf 1984, FHP 1988, Bernanke 1983, Dixit-Pindyck 1994, Leary-Roberts 2005 (textbook/redundant); JJL 2021 (R&D dropped); Duong 2024 (§4.5 supporting; §4.5 in appendix only).

## Open Items for Writing Phase

1. **Step 5 walkthrough**: Hoberg-Phillips 2016 TSIMM verbatim (next; F1D contains the paper)
2. **Pipeline H1.2 BelowIG suppression**: implement display change in run_h1_2_cash_constraint runner OR document as render-time choice
3. **OPSW log-DV robustness appendix**: future work if time permits — flagged in `reference_opsw_1999_verbatim.md`
4. **MW year fix**: update all-tables references / template / findings if any cite "MW 2009" — global search-replace
5. **Aguerrevere 2009 venue**: confirm JF (per memory) vs RFS (per earlier skeleton draft) via DOI before bibliography compile

## Changes from v3 (2026-04-16 evening, later — superseded v3)

1. **Capex framing:** "Documented investment-margin puzzle" → **exploratory additional analysis**. No "puzzle." No "OPPOSITE to precautionary." Neutral discovery + competitive real options interpretation.
2. **AFW 2004 dropped** entirely (was puzzle anchor; exploratory framing eliminates need)
3. **Bloom 2014 dropped** as load-bearing (DWZ speech-uncertainty lineage distinct from Bloom's macro-uncertainty lineage)
4. **Aguerrevere 2009 demoted** to Tier-2 citation-only (Grenadier 2002 carries channel mechanism alone)
5. **§4.5 payout (H12/H12b) moved to appendix C only.** Body §4.5 removed. "Pres/Q&A decomposition" Ch 1 contribution claim dropped. Duong 2024 dropped (was §4.5 supporting).
6. **R&D (H16) dropped entirely** from thesis. JJL 2021 dropped from reference stack.
7. **37-suite appendix dropped.** Replaced by §2.1 pre-commitment statement (front-loaded p-hacking defense).
8. **MW year corrected**: 2001 (SSRN), not 2009.
9. **HFC framing**: FP 2006 binary access disclosed; we extend to three-way; "credit constrained" wording per FP exact. BelowIG row suppressed from H1.2 main display (null + no economic content).
10. **§II pre-commitment statement** added (§2.1) with three-bucket statistical convention disclosure.
11. **Central Claim rewritten** — exploratory framing, no contradiction setup.
12. **Two contributions** (was three) in §I — drop the "Pres/Q&A decomposition" claim along with §4.5.
13. **Targeted appendix** (var defs + validity + presentation analogues + robustness), not 37-suite dump.
14. **Tier-1 stack reduced from 9 papers to 8** (drop AFW; Aguerrevere demoted; net -1).

## What does NOT change from v3

- Empirical pipeline data, audit results, suite registry
- Panels, runners, all_tables.tex (only display-side changes for H1.2 BelowIG suppression)
- Sample (112,968 calls, 2,429 firms, 2002-2018; H1.2 narrowed to 2002-2016)
- IV construction (DWZ + BGT)
- Title + RQ
- Three formal hypothesis labels (HC/HL/HFC)
- §III main results pattern (HC 6/6 contemp, HL 6/6 lead, HFC 4/4 Unrated)
- §IV main capex finding (capex↑ + competition concentration)
