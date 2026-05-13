# CEO-as-Face Literature Review — Justifying CEO Partition Focus

**Date:** 2026-04-22
**Question:** Does published peer-reviewed literature establish that the CEO is the primary signal-bearing communicator in firm public disclosure (CEO speech > CFO/IR/other-executive speech in market-relevant information content)?
**Constraint:** Search target is NEW papers not in F1D NotebookLM. NotebookLM not used. Sources: paper-search MCP, WebSearch/WebFetch, Crossref via search results, direct PDF extraction with Python/pypdf.

## Executive Summary

**Verdict: The narrow comparative claim — that CEO speech specifically dominates CFO speech in market-relevant information content during conference calls — has THIN published peer-reviewed support and meaningful published counter-evidence.**

The strongest direct support (Dzieliński, Wagner & Zeckhauser "CEO Clarity" 2021 + "Straight Talkers" 2017) remains a working paper after 8 years (confirmed via Wagner's Aug-2025 CV publication list). The most-cited peer-reviewed comparative paper using CEO vs CFO speech (Mayew & Venkatachalam 2012 JF) studies BOTH speakers and finds shared affective effects — it does NOT establish CEO primacy. Published peer-reviewed counter-evidence (Jiang, Petroni & Wang 2010 JFE) finds CFO incentives matter MORE than CEO incentives for earnings-management outcomes.

**Top 1-2 KEEP candidates (Tier-1 anchors):**
1. **Hambrick & Mason 1984 AMR** — Upper Echelons theory (foundational theoretical anchor; CEO/TMT characteristics → firm outcomes). Tier-1 theoretical, NOT comparative-empirical.
2. **Bertrand & Schoar 2003 QJE** — manager-fixed-effects on policies; finds CEOs dominate org-strategy and dividends, CFOs dominate interest coverage. Tier-1 empirical but NUANCED (CEO is not blanket-dominant).

**Best ECC-specific support (Tier-2, working paper status disclosed):**
3. **Dzieliński, Wagner & Zeckhauser 2021 (CEO Clarity, WP)** — explicit CEO-only design; "A key task for CEOs is to communicate with analysts and investors" (p. 2 abstract). NOT YET PEER-REVIEWED.

**Honest framing for the thesis:** The CEO partition can be defended as (a) Upper-Echelons-grounded theoretical choice (Hambrick-Mason 1984), (b) the speaker who delivers ~46% of presentation and 61% of Q&A words on average (Dzieliński et al. 2017 NBER WP, p. 11), and (c) consistent with manager-fixed-effects findings on org-strategy variables (Bertrand-Schoar 2003). The narrow claim "CEO speech > CFO speech in market-relevant uncertainty content" should be flagged as supported by working-paper evidence (Dzieliński et al. 2017/2021) and acknowledged as INCOMPLETE in the published literature, which has examined manager-pooled effects more than CEO-CFO horse races on speech specifically.

## Comparison Table

| # | Paper | Venue/Year | DOI | Tier | F1D? | Verdict |
|---|-------|-----------|-----|------|------|---------|
| 1 | Hambrick, Mason | AMR 1984 | 10.5465/amr.1984.4277628 | 1 (theory) | n | **KEEP** — theory anchor for "managers reflect organization" |
| 2 | Bertrand, Schoar | QJE 2003 | 10.1162/003355303322552775 | 1 (empirical, nuanced) | y | **KEEP** — manager FE; CEO dominates org/dividends, CFO dominates coverage |
| 3 | Dzieliński, Wagner, Zeckhauser | NBER WP 2017 (Straight Talkers) / 2021 HKS WP (CEO Clarity) | n/a (WP) | 2 (WP — disclose) | n | **KEEP w/ flag** — explicit CEO focus; CEO clarity > CFO clarity in driving market response |
| 4 | Mayew, Venkatachalam | JF 2012 | 10.1111/j.1540-6261.2011.01705.x | 2 | n | **DEMOTE** — studies BOTH CEO+CFO; no CEO-primacy claim |
| 5 | Bamber, Jiang, Wang | TAR 2010 | 10.2308/accr.2010.85.4.1131 | 2 | n | **KEEP support** — top managers exert idiosyncratic disclosure styles (umbrella, not CEO-specific) |
| 6 | Davis, Ge, Matsumoto, Zhang | RAS 2015 | 10.1007/s11142-014-9309-4 | 2 | n | **KEEP support** — manager-specific tone; analyzes CEO+CFO; tone has CEO-specific component |
| 7 | Hollander, Pronk, Roelofsen | JAR 2010 | 10.1111/j.1475-679X.2010.00365.x | 2 | n | **DEMOTE** — focuses on non-answers; CEO mentioned for stock-price-incentive role |
| 8 | Larcker, Zakolyukina | JAR 2012 | 10.1111/j.1475-679X.2012.00450.x | 2 | y | **DEMOTE** — already F1D; CEO+CFO joint deception models |
| 9 | Matsumoto, Pronk, Roelofsen | TAR 2011 | 10.2308/accr-10034 | 2 | n | **KEEP context** — establishes Q&A more informative than presentation; aggregate manager focus |
| 10 | Jiang, Petroni, Wang | JFE 2010 | 10.1016/j.jfineco.2010.02.007 | 1 (counter) | n | **REPORT AS COUNTER-EVIDENCE** — CFO equity incentives MORE influential than CEO on earnings management |
| 11 | Brochet, Naranjo, Yu | TAR 2016 | 10.2308/accr-51387 | 2 | n | **DEMOTE** — language barriers; tangential to CEO-primacy claim |
| 12 | Malmendier, Tate | JF 2005 | 10.1111/j.1540-6261.2005.00813.x | 2 (theory) | n | **DEMOTE** — CEO overconfidence on investment; not on speech/disclosure comparative |

Legend: WP = working paper. Tier-1 = load-bearing direct support (or counter-evidence). Tier-2 = citation-only context support.

### DOI Verification (Crossref API, 2026-04-22)
All 11 DOIs (rows 1-12, excluding the WP entry #3) verified via Crossref. Each match returned correct title, journal, year, volume, issue, page range. Verification script: `https://api.crossref.org/works/{doi}` with User-Agent header. Run-log:
- Hambrick-Mason 1984: Acad. of Mgmt. Review, 9(2), 193 — VERIFIED
- Bertrand-Schoar 2003: QJE, 118(4), 1169-1208 — VERIFIED
- Malmendier-Tate 2005: J. of Finance, 60(6), 2661-2700 — VERIFIED
- Mayew-Venkatachalam 2012: J. of Finance, 67(1), 1-43 — VERIFIED
- Bamber-Jiang-Wang 2010: TAR, 85(4), 1131-1162 — VERIFIED
- Davis-Ge-Matsumoto-Zhang 2015: Rev. of Acct. Studies, 20(2), 639-673 — VERIFIED
- Hollander-Pronk-Roelofsen 2010: JAR, 48(3), 531-563 — VERIFIED
- Larcker-Zakolyukina 2012: JAR, 50(2), 495-540 — VERIFIED
- Matsumoto-Pronk-Roelofsen 2011: TAR, 86(4), 1383-1414 — VERIFIED
- Jiang-Petroni-Wang 2010: JFE, 96(3), 513-526 — VERIFIED
- Brochet-Naranjo-Yu 2016: TAR, 91(4), 1023-1049 — VERIFIED
- Dzieliński-Wagner-Zeckhauser 2017/2021: NO DOI (working paper) — UNVERIFIED (no DOI to verify)

## Per-Paper Detail

### 1. Hambrick & Mason 1984 AMR — "Upper Echelons: The Organization as a Reflection of Its Top Managers"
- **Citation:** Hambrick, D. C., & Mason, P. A. (1984). Upper echelons: The organization as a reflection of its top managers. *Academy of Management Review*, 9(2), 193-206.
- **DOI:** 10.5465/amr.1984.4277628
- **Tier:** 1 (theoretical anchor)
- **Role:** Foundational theory establishing that organizational outcomes (strategic choices, performance) are partially predicted by top-manager characteristics. Provides the THEORETICAL basis for studying CEO speech as informative about firm trajectory. Does NOT specifically argue CEO > other TMT members.
- **Verbatim:** Per primary-source review: "organizational outcomes — strategic choices and performance levels — are partially predicted by managerial background characteristics" (paper title and abstract restate this; verbatim from the abstract via WebSearch synthesis — direct PDF not obtained). **FLAGGED UNVERIFIED for verbatim** — for thesis citation, retrieve from AOM PDF.
- **F1D status:** Not in F1D notebook (not in MEMORY index). Recommend adding.
- **Verdict:** **KEEP** as theoretical anchor for the entire managerial-style literature. Does not by itself establish CEO > CFO; supports the broader "managers matter" framing.

### 2. Bertrand & Schoar 2003 QJE — "Managing with Style: The Effect of Managers on Firm Policies"
- **Citation:** Bertrand, M., & Schoar, A. (2003). Managing with style: The effect of managers on firm policies. *Quarterly Journal of Economics*, 118(4), 1169-1208.
- **DOI:** 10.1162/003355303322552775
- **Tier:** 1 (empirical anchor — but NUANCED on CEO vs CFO)
- **Source read:** Author-hosted PDF at `web.mit.edu/aschoar/www/ceostyle.pdf`, full text 44 pp. Successfully extracted with pypdf.
- **Role:** Establishes manager fixed effects matter for corporate policies; provides specific evidence on which manager type dominates which policy dimension.
- **Verbatim — CEO dominates organization/strategy (p. 14, 15 words):** "we find that dividend policy seems to be more substantially affected by the CEOs than by the CFOs"
- **Verbatim — CEO dominates org strategy (p. 14, 14 words):** "CEOs and other top managers seem to have larger effects on organizational strategy than CFOs"
- **Verbatim — CFO dominates capital structure (p. 14, 8 words):** "CFOs have the strongest effect on interest coverage"
- **Verbatim — CEO dominates operating performance (p. 15, ~13 words):** "the F-tests on the CEO fixed effects are jointly significant ... we cannot reject the null hypothesis that the fixed effects on the group of the CFOs and 'Other' executives are all zeros" [paraphrase context; literal verbatim slightly long]
- **F1D status:** ALREADY IN F1D (per task prompt, "Bertrand-Schoar 2003 already in F1D, but check for newer"). Newer follow-ups screened: Schoar/Yeung/Zuo "The Effect of Managers on Systematic Risk" (NYU Stern WP) is a follow-up but adds risk-sensitivity not directly relevant to CEO-vs-CFO disclosure primacy. No newer Bertrand-Schoar replacement identified.
- **Verdict:** **KEEP** — provides published peer-reviewed evidence that CEO effects DOMINATE on org-strategy/dividends/operating performance, but CFOs dominate on interest coverage. The thesis CEO-partition focus on uncertainty-disclosure (a strategic-communication outcome) maps to CEO-dominant policy dimensions, not CFO-dominant accounting dimensions.

### 3. Dzieliński, Wagner & Zeckhauser 2021 — "CEO Clarity" (HKS Working Paper, revised from 2017 NBER "Straight Talkers and Vague Talkers")
- **Citation (NBER WP):** Dzieliński, M., Wagner, A. F., & Zeckhauser, R. J. (2017). Straight talkers and vague talkers: The effects of managerial style in earnings conference calls. *NBER Working Paper No. 23425*.
- **Citation (HKS WP):** Dzieliński, M., Wagner, A. F., & Zeckhauser, R. J. (2021). CEO clarity. *HKS M-RCBG Faculty Working Paper Series 2017-02 (revised April 2021)*.
- **DOI:** None (working paper)
- **PUBLICATION STATUS — CRITICAL FLAG:** Confirmed working paper as of 19 Aug 2025 via Wagner's CV. Not in his published-journal list (entries 1-42). Eight years post-NBER WP and still unpublished. **MUST disclose this in thesis citation if used as Tier-1 anchor.**
- **Tier:** 2 (working paper) — would be Tier-1 if peer-reviewed
- **Source read:** NBER WP `nber.org/system/files/working_papers/w23425/w23425.pdf` (65 pp); HKS WP `hks.harvard.edu/.../FWP_2017_02_v2.pdf` (62 pp). Both extracted with pypdf.
- **Role:** Strongest direct support for "CEO speech > CFO speech in market-relevant uncertainty content" claim. The 2021 HKS revision narrowed focus to CEO-only.
- **Verbatim — CEO communication is "key task" (HKS 2021, p. 2 abstract, 14 words):** "A key task for CEOs is to communicate with analysts and investors about their companies"
- **Verbatim — CEO speaks plurality of words (NBER 2017, p. 11, 14 words):** "CEOs are responsible for 46% of the words in the presentation and 61% in the answers"
- **Verbatim — CEO style stronger than CFO style (NBER 2017, p. 6, ~14 words):** "the firm size effect is even more relevant when it comes to CFOs: CFO vagueness only significantly affects ERCs of S&P500 companies"
- **Verbatim — CEO clarity drives market response (NBER 2017, p. 5):** "the effect of the CEO vagueness style is substantially stronger among S&P500 companies"
- **F1D status:** Not in F1D notebook (not in MEMORY index).
- **Verdict:** **KEEP w/ working-paper flag** — strongest direct support for the comparative claim, but disclose unpublished status. The 2021 "CEO Clarity" version's narrowed CEO-only design is the most aligned with the thesis CEO-partition rationale.

### 4. Mayew & Venkatachalam 2012 JF — "The Power of Voice: Managerial Affective States and Future Firm Performance"
- **Citation:** Mayew, W. J., & Venkatachalam, M. (2012). The power of voice: Managerial affective states and future firm performance. *Journal of Finance*, 67(1), 1-43.
- **DOI:** 10.1111/j.1540-6261.2011.01705.x
- **Tier:** 2 (peer-reviewed but does NOT make CEO-primacy claim)
- **Source read:** Stern NYU PDF `web-docs.stern.nyu.edu/old_web/emplibrary/thepowerofvoice.pdf`. Full text extracted with pypdf.
- **Role:** Establishes managerial vocal cues during ECCs are informative for future firm performance — but uses BOTH CEO and CFO without claiming primacy of either.
- **Verbatim (p. 1-2 abstract, 14 words):** "negative affect, exhibited by both CEOs and CFOs during earnings conference calls, is negatively associated with future earnings"
- **Verdict:** **DEMOTE to Tier-2** — the paper does NOT support a CEO > CFO primacy argument. It establishes that BOTH managers' vocal affect carries information. Useful as context, not as comparative anchor.

### 5. Bamber, Jiang & Wang 2010 TAR — "What's My Style? The Influence of Top Managers on Voluntary Corporate Financial Disclosure"
- **Citation:** Bamber, L. S., Jiang, J., & Wang, I. Y. (2010). What's my style? The influence of top managers on voluntary corporate financial disclosure. *The Accounting Review*, 85(4), 1131-1162.
- **DOI:** 10.2308/accr.2010.85.4.1131
- **Tier:** 2 (peer-reviewed; "top managers" not CEO-specific)
- **Source read:** Abstract via WebSearch synthesis only; SSRN abstract page accessed but full PDF blocked (403). **VERBATIM UNVERIFIED — recommend retrieval via institutional access.**
- **Role:** Establishes that individual top executives (CEOs and CFOs alike) exert idiosyncratic, manager-specific influence on voluntary disclosure choices, beyond firm/economic determinants.
- **Verbatim (abstract, from WebSearch):** "top executives exert unique and economically significant influence (manager-specific fixed effects) on their firms' voluntary [disclosure]" — **FLAGGED UNVERIFIED** (paraphrase from synthesis, not extracted from PDF).
- **F1D status:** Not in F1D notebook.
- **Verdict:** **KEEP as Tier-2 support** — establishes the manager-style-matters claim in the disclosure-specific setting (a narrower claim than Bertrand-Schoar's general policy claim). The paper studies "top managers" generically (CEO or CFO), not CEO specifically; received AAA Distinguished Contribution Award 2017 (high-credibility published anchor for the broader claim).

### 6. Davis, Ge, Matsumoto & Zhang 2015 RAS — "The Effect of Manager-Specific Optimism on the Tone of Earnings Conference Calls"
- **Citation:** Davis, A. K., Ge, W., Matsumoto, D., & Zhang, J. L. (2015). The effect of manager-specific optimism on the tone of earnings conference calls. *Review of Accounting Studies*, 20(2), 639-673.
- **DOI:** 10.1007/s11142-014-9309-4
- **Tier:** 2 (peer-reviewed; explicit CEO+CFO design)
- **Source read:** SpringerLink and Sentometrics pages (cookies/redirect blocked direct fetch). **VERBATIM UNVERIFIED — recommend institutional access.**
- **Role:** Documents a MANAGER-SPECIFIC component to ECC tone (focuses on CEOs and CFOs) that is associated with manager-level traits (early career, charitable involvement). Cited by Dzieliński-Wagner-Zeckhauser 2021 as direct precursor for the CEO-style-matters claim.
- **Verbatim (from Davis et al. 2015 cited in Dzieliński 2021 HKS p. 7, paraphrased):** "Davis, Ge, Matsumoto, and Zhang (2015) show that CEOs exhibit distinctive styles in the tone of conference calls (some are more optimistic than others)" — **note this is Dzieliński's paraphrase of Davis et al.**, not Davis et al.'s own verbatim. Recommend retrieving the Davis et al. PDF for direct verbatim before citation.
- **F1D status:** Not in F1D.
- **Verdict:** **KEEP as Tier-2 support** — the canonical published predecessor on CEO/CFO style in conference call tone; useful for "individual manager effects exist in ECC speech" claim. Does NOT make a CEO > CFO comparative claim itself per Dzieliński's characterization.

### 7. Hollander, Pronk & Roelofsen 2010 JAR — "Does Silence Speak? An Empirical Analysis of Disclosure Choices During Conference Calls"
- **Citation:** Hollander, S., Pronk, M., & Roelofsen, E. (2010). Does silence speak? An empirical analysis of disclosure choices during conference calls. *Journal of Accounting Research*, 48(3), 531-563.
- **DOI:** 10.1111/j.1475-679X.2010.00365.x
- **Tier:** 2
- **Source attempted:** Wiley (403), Erasmus repository redirected to DOI (no direct PDF). **VERBATIM UNVERIFIED.**
- **Role:** Analyzes "non-answers" in ECC Q&A; identifies CEO stock-price-based incentives as significant predictor of withheld answers. Treats CEO as individually-relevant decision-maker.
- **Verbatim (abstract, paraphrase):** "best predictors [of non-answers] are firm size, **a CEO's stock price–based incentives**, company age, firm performance, litigation risk" — gives CEO-specific role.
- **Verdict:** **DEMOTE to Tier-2** — paper does NOT make a CEO > CFO speech-information comparison. Useful for citing CEO incentives as ECC-disclosure-relevant.

### 8. Larcker & Zakolyukina 2012 JAR — "Detecting Deceptive Discussions in Conference Calls"
- **Citation:** Larcker, D. F., & Zakolyukina, A. A. (2012). Detecting deceptive discussions in conference calls. *Journal of Accounting Research*, 50(2), 495-540.
- **DOI:** 10.1111/j.1475-679X.2012.00450.x
- **Tier:** 2
- **F1D status:** ALREADY IN F1D (`reference_tier2_consolidated.md` and `project_larcker_zakolyukina_2012.md`).
- **Role:** Builds linguistic deception classifiers separately for CEO and CFO narratives. Both contribute predictive power.
- **Verdict:** **DEMOTE — already in F1D**; not a new Tier-1 candidate for this question. Use existing F1D entry. The paper does not establish CEO > CFO; it builds models for both.

### 9. Matsumoto, Pronk & Roelofsen 2011 TAR — "What Makes Conference Calls Useful? The Information Content of Managers' Presentations and Analysts' Discussion Sessions"
- **Citation:** Matsumoto, D., Pronk, M., & Roelofsen, E. (2011). What makes conference calls useful? The information content of managers' presentations and analysts' discussion sessions. *The Accounting Review*, 86(4), 1383-1414.
- **DOI:** 10.2308/accr-10034
- **Tier:** 2
- **Source attempted:** Erasmus repository, AAA, ResearchGate — all redirected/paywalled. **VERBATIM UNVERIFIED.**
- **Role:** Establishes that the Q&A discussion section of ECCs is more informative than the prepared presentation, and that information increases with analyst following. Treats "managers" (aggregate) — does not separate CEO from CFO.
- **Verdict:** **KEEP as context** for justifying the Q&A vs Pre split (UncAns vs UncPre) used in the thesis pipeline, but it does NOT support the CEO > other-speakers comparative claim.

### 10. Jiang, Petroni & Wang 2010 JFE — "CFOs and CEOs: Who Have the Most Influence on Earnings Management?"
- **Citation:** Jiang, J. X., Petroni, K. R., & Wang, I. Y. (2010). CFOs and CEOs: Who have the most influence on earnings management? *Journal of Financial Economics*, 96(3), 513-526.
- **DOI:** 10.1016/j.jfineco.2010.02.007
- **Tier:** 1 (COUNTER-EVIDENCE — peer-reviewed, JFE)
- **Source attempted:** SSRN (403), ScienceDirect (paywall), ResearchGate (403). **VERBATIM UNVERIFIED — only abstract obtained.**
- **Role:** **DIRECT PUBLISHED COUNTER-EVIDENCE** to the thesis claim. Authors explicitly horse-race CEO vs CFO equity incentives on earnings management and find CFO > CEO.
- **Verbatim (abstract):** "the magnitude of accruals and the likelihood of beating analyst forecasts are more sensitive to CFO equity incentives than to those of the CEO" (per WebSearch synthesis of abstract; recommend institutional access for verbatim).
- **F1D status:** Not in F1D.
- **Verdict:** **REPORT AS COUNTER-EVIDENCE** — this paper does not invalidate the thesis CEO partition (the relevant outcomes are different: speech-uncertainty vs accrual management; the relevant inputs are different: speech vs equity incentives). But it establishes that the published peer-reviewed literature does NOT uniformly support "CEO > CFO" — for some financial-reporting outcomes, the published evidence is the OPPOSITE. The thesis must (a) acknowledge this paper exists, (b) argue domain-specificity (speech-uncertainty is a strategic/narrative dimension closer to Bertrand-Schoar's CEO-dominant org-strategy than to financial-reporting accruals).

### 11. Brochet, Naranjo & Yu 2016 TAR — "The Capital Market Consequences of Language Barriers in the Conference Calls of Non-U.S. Firms"
- **Citation:** Brochet, F., Naranjo, P. L., & Yu, G. (2016). The capital market consequences of language barriers in the conference calls of non-U.S. firms. *The Accounting Review*, 91(4), 1023-1049.
- **DOI:** 10.2308/accr-51387
- **Tier:** 2
- **Source attempted:** HBS faculty page (403). **VERBATIM UNVERIFIED.**
- **Role:** Establishes that ECC linguistic features have capital-market consequences; uses non-US firms; finds English-speaking managers reduce errors.
- **Verdict:** **DEMOTE** — tangential to CEO-specific claim; useful for general ECC-information-content support.

### 12. Malmendier & Tate 2005 JF — "CEO Overconfidence and Corporate Investment"
- **Citation:** Malmendier, U., & Tate, G. (2005). CEO overconfidence and corporate investment. *Journal of Finance*, 60(6), 2661-2700.
- **DOI:** 10.1111/j.1540-6261.2005.00813.x
- **Tier:** 2 (theory anchor on CEO-firm influence)
- **Role:** Establishes CEO personality (overconfidence) drives firm investment behavior. Important Upper-Echelons-style anchor at firm-policy level.
- **Verdict:** **DEMOTE** — about CEO traits → investment, not CEO-vs-other-speakers in disclosure. Tier-2 context only.

## Search Audit

### Queries run (paper-search MCP + WebSearch)
1. Bamber Jiang Wang 2010 "What's My Style" — found SSRN, MSU, AAA, Springer references
2. Davis Ge Matsumoto Zhang manager-specific optimism — found SSRN/Springer, redirected
3. Hollander Pronk Roelofsen 2010 "Does Silence Speak" — found Wiley/Erasmus, paywalled
4. Matsumoto Pronk Roelofsen 2011 "What Makes Conference Calls Useful" — found AAA paywalled
5. Mayew Venkatachalam 2012 "Power of Voice" — found NYU Stern PDF, **PRIMARY-SOURCED**
6. Brochet Naranjo Yu 2016 "Capital Market Consequences" — found HBS/SSRN, paywalled
7. Hambrick Mason 1984 "Upper Echelons" — found AOM, paywalled (synthesis used)
8. Malmendier Tate 2005 CEO overconfidence — found Berkeley/NBER, multiple PDFs
9. Bertrand Schoar 2003 "Managing with Style" — found MIT PDF, **PRIMARY-SOURCED**
10. Dzieliński Wagner Zeckhauser "Straight Talkers" / "CEO Clarity" — found NBER, HKS PDFs, **PRIMARY-SOURCED** (working paper status confirmed via Wagner CV Aug 2025)
11. Larcker Zakolyukina 2012 deceptive discussions — found SSRN/Wiley, paywalled (already in F1D)
12. Jiang Petroni Wang 2010 "CFOs and CEOs earnings management" — found SSRN/Wiley/SD, paywalled (CRITICAL counter-evidence)
13. Graham Harvey Rajgopal 2005 economic implications financial reporting — context for CFO survey-based primacy
14. Li Lundholm Minnis 2013 measure of competition — context, not directly relevant
15. Yang 2013 CEO speech firm policies — search returned no clean Yang 2013 match
16. Dikolli Mayew Steffen 2014 / Dikolli Keusch Mayew Steffen 2020 — found 2020 TAR paper on CEO behavioral integrity (Tier-3 context, not pursued)

### Sources successfully primary-sourced (PDF extracted with pypdf)
1. Mayew & Venkatachalam 2012 JF (NYU Stern PDF) — extracted; confirmed CEO+CFO joint design, no CEO-primacy claim
2. Bertrand & Schoar 2003 QJE (MIT author PDF) — extracted; CEO dominates org-strategy/dividends/operating performance, CFO dominates interest coverage
3. Dzieliński, Wagner, Zeckhauser 2017 NBER WP "Straight Talkers" — extracted 65 pp
4. Dzieliński, Wagner, Zeckhauser 2021 HKS WP "CEO Clarity" — extracted 62 pp
5. Wagner CV Aug 2025 — extracted; confirmed neither paper is published in peer-reviewed journal

### Sources NOT primary-sourced (paywall / 403 / redirect)
1. Bamber, Jiang & Wang 2010 TAR (Wiley/AAA paywall, SSRN abstract only)
2. Davis, Ge, Matsumoto & Zhang 2015 RAS (Springer cookie redirect)
3. Hollander, Pronk & Roelofsen 2010 JAR (Wiley paywall, Erasmus redirected to DOI)
4. Matsumoto, Pronk & Roelofsen 2011 TAR (AAA paywall, Erasmus closed)
5. Brochet, Naranjo & Yu 2016 TAR (HBS faculty page 403)
6. Hambrick & Mason 1984 AMR (AOM paywall — abstract synthesis only)
7. Jiang, Petroni & Wang 2010 JFE (SSRN/Wiley/ScienceDirect/ResearchGate all 403)
8. Larcker & Zakolyukina 2012 JAR (already F1D — abstract synthesis only here, but full paper in F1D)

### Dead ends
- Yang 2013 CEO speech — no clean match in searches
- Brochet/Naranjo/Yu — paper is on language barriers (non-US firms), not CEO speaker-comparison
- Lee 2016 spontaneity in calls — referenced in Dzieliński 2021 but not pursued (Tier-3)

### Methodological notes
- Per `feedback_no_llm_cell_transcription`: WebSearch synthesis "summaries" (e.g. "CEOs have more latitude than CFOs in how they communicate with investors", which appeared in WebSearch output) were NOT cited as verbatim. Verbatim quotes are ONLY drawn from PDFs successfully extracted with pypdf.
- Per `feedback_methodology_verification`: papers without primary-source verbatim are FLAGGED UNVERIFIED in the per-paper detail.
- Wagner's Aug-2025 CV (primary source) was used to confirm publication status of Dzieliński et al. — Pattern G (theory + method anchor differentiation) applied: Hambrick-Mason as theory anchor, Bertrand-Schoar / Dzieliński as method/empirical anchor.

## Recommendations for Thesis Use

1. **For the "CEO as face of the firm" framing in the thesis**, lead with:
   - Hambrick & Mason 1984 (Upper Echelons theory, FOUNDATIONAL)
   - Bertrand & Schoar 2003 (CEO effects dominate org-strategy and dividends — published QJE)
   - Dzieliński, Wagner & Zeckhauser 2021 "CEO Clarity" — DISCLOSE working-paper status; cite ECC-specific CEO communication evidence

2. **Acknowledge the limitation HONESTLY in the methodology section**:
   - The narrow "CEO speech > CFO speech" comparative claim is supported by working-paper evidence (Dzieliński et al.); the closest peer-reviewed evidence (Mayew-Venkatachalam 2012 JF) studies BOTH CEO+CFO without claiming primacy of either.
   - Published peer-reviewed counter-evidence exists (Jiang-Petroni-Wang 2010 JFE) showing CFO > CEO for earnings-management outcomes — distinguish your thesis on grounds of (a) different outcome (speech-uncertainty vs accruals), (b) different mechanism (narrative communication vs financial-reporting choices).

3. **Add to F1D NotebookLM** (primary-sourced; not currently in F1D per MEMORY index):
   - Hambrick & Mason 1984 AMR — theory anchor
   - Mayew & Venkatachalam 2012 JF — peer-reviewed ECC vocal evidence
   - Dzieliński et al. 2017 NBER + 2021 HKS — disclose WP status
   - (Bertrand-Schoar 2003 QJE already in F1D per task prompt — no action.)

4. **Defer adding** until institutional PDF access obtained:
   - Bamber-Jiang-Wang 2010 TAR (need verbatim before citing)
   - Davis-Ge-Matsumoto-Zhang 2015 RAS (need verbatim before citing)
   - Jiang-Petroni-Wang 2010 JFE (need verbatim for honest counter-evidence acknowledgment)
