# CEO Speech Analysis — Anchor Literature Review

**Task**: single-paper anchor (with 1-2 backups) for "CEO-specific speech analysis is material in finance."
**Constraint**: top-tier journals; DOIs Crossref-verified.
**Date**: 2026-04-23

## TOP RECOMMENDATION

### Mayew & Venkatachalam (2012) — "The Power of Voice: Managerial Affective States and Future Firm Performance"
- **Journal**: The Journal of Finance, 67(1), Feb 2012
- **DOI**: https://doi.org/10.1111/j.1540-6261.2011.01705.x
- **Citation count** (Crossref): 497
- **Setup**: Applies vocal-emotion analysis software to CEO and CFO audio segments from earnings conference calls, extracting speaker-identified measures of positive and negative affect.
- **Finding**: Managerial vocal cues contain incremental information about firm fundamentals beyond quantitative disclosures — positive (negative) CEO/CFO affect predicts future unexpected earnings and abnormal returns positively (negatively).
- **Why this anchors the claim**: The paper is the canonical top-tier finance-journal demonstration that identifying *which executive is speaking* on an earnings call carries unique, priced information. Its headline — "The Power of Voice" — directly supports the premise that CEO-specific speech signals are material, not a subset of pooled-firm disclosure. Publication venue (JF, the flagship finance journal) is the strongest possible placement for the claim.
- **Fit to our case**: Same data setting (earnings calls), same speaker-identification discipline (CEO vs CFO vs other managers), same empirical payoff (predictive of firm outcomes). Licenses our choice to carve CEO speech out of pooled-manager text as a first-order measurement decision rather than a robustness afterthought.
- **Caveats**: Their measure is vocal acoustic features (LVA software-based affect) rather than textual LM uncertainty wordlist; we extend the speaker-identified premise to text-based uncertainty.

## RUNNER-UP #1

### Larcker & Zakolyukina (2012) — "Detecting Deceptive Discussions in Conference Calls"
- **Journal**: Journal of Accounting Research, 50(2), 2012
- **DOI**: https://doi.org/10.1111/j.1475-679x.2012.00450.x
- **Citation count** (Crossref): 519
- **Setup**: Builds textual linguistic classifiers on separately-identified CEO and CFO narratives from earnings call Q&A transcripts to flag firms likely engaging in material restatements.
- **Finding**: CEO- and CFO-specific word use (e.g., references to general knowledge, extreme positive emotion, hesitation markers) outperforms random-chance in identifying deceptive reporting, with CEO and CFO linguistic profiles behaving differently — i.e., the speaker identity matters.
- **Why this anchors the claim**: It is the primary top-tier accounting-journal precedent for text-based, speaker-identified CEO speech analysis in earnings calls. Establishes that splitting CEO from CFO from other managers is informative and that textual features of executive speech predict firm-level outcomes — directly analogous to our LM-uncertainty-on-CEO-speech design.
- **Fit to our case**: Uses the exact primitive we use — earnings-call transcripts split by speaker role — and uses textual word-list / dictionary analysis, closer to our Loughran-McDonald uncertainty methodology than Mayew-Venkatachalam's vocal features.
- **Caveats**: DV is deception/restatement rather than uncertainty; our dependent variables are downstream firm financial outcomes rather than misreporting.

## RUNNER-UP #2

### Hobson, Mayew & Venkatachalam (2012) — "Analyzing Speech to Detect Financial Misreporting"
- **Journal**: Journal of Accounting Research, 50(2), 2012
- **DOI**: https://doi.org/10.1111/j.1475-679x.2011.00433.x
- **Citation count** (Crossref): 297
- **Setup**: Applies vocal dissonance markers extracted from CEO audio on earnings calls to classify firms with material misreporting risk.
- **Finding**: CEO-specific vocal cognitive dissonance correlates with ex-post restatement probability, again establishing that CEO-identified speech carries incremental information beyond quantitative disclosures.
- **Why this anchors the claim**: Complements the top pick (same vocal framework) and RU#1 (same CEO-identified, earnings-call, misreporting DV) — triangulates that CEO speech analysis is a mature finance/accounting research primitive across both vocal and textual modalities in top journals.
- **Fit to our case**: Direct precedent for isolating the CEO (not CFO, not pooled-manager) as the unit of analysis on earnings calls.
- **Caveats**: Vocal rather than textual; smaller citation base than the other two finalists; DV is again misreporting.

## BRIEFLY CONSIDERED + REJECTED

- **Matsumoto, Pronk & Roelofsen (2011), TAR** — DOI 10.2308/accr-10034 — 632 cites. Rejected because the unit of analysis is the pooled "managers' presentation" segment vs "analysts' discussion session," not CEO-identified speech. Explicitly fails the task's "CEO-specific (as opposed to pooled-manager)" constraint.
- **Bertrand & Schoar (2003), QJE** — DOI 10.1162/003355303322552775 — 3,088 cites. Rejected because CEO fixed effects on firm policy is a *person* effect, not a *speech* effect. Fails the "speech analysis" leg of the claim even though it powerfully supports "the CEO matters."
- **Price, Doran, Peterson & Bliss (2012)** — DOI 10.1016/j.jbankfin.2011.10.013 — 559 cites. Rejected: Journal of Banking & Finance is a second-tier journal per the task's hard constraint on JF/JFE/RFS/JAR/TAR/JAE/QJE/AER/MS only; a top-tier alternative exists so no justification to include.
- **Doran, Peterson & Price (2012)**, J Real Estate Finance & Economics — DOI 10.1007/s11146-010-9266-z — 109 cites. Rejected: specialty-journal / REIT subsample; not top-tier.
- **Blau, DeLisle & Price (2015)**, J Corporate Finance — DOI 10.1016/j.jcorpfin.2015.02.003 — 164 cites. Rejected: second-tier journal; conference-call tone but not CEO-identified.
- **Hobson, Mayew, Peecher & Venkatachalam (2017), JAR** — DOI 10.1111/1475-679x.12181 — 48 cites. Rejected: relevant but lower citation impact than the 2012 JAR paper by same lead authors; experimental auditor-training setting less transportable to our observational firm-panel design.
- **Hollander, Pronk & Roelofsen (2010), JAR** — DOI 10.1111/j.1475-679x.2010.00365.x — 318 cites. Rejected: studies managerial *silence* (refusals to answer) rather than analyzed speech content; indirect fit.
- **Li (2010), JAE (not re-verified here, well-known)** — 10-K tone. Rejected because 10-K annual-report text is firm-level disclosure, not CEO-identified speech; user pre-flagged as weaker fit.
- **Throckmorton et al. (2015), Decision Support Systems** — DOI 10.1016/j.dss.2015.04.006 — 102 cites. Rejected: not a top-tier finance/accounting journal.

## SEARCH SUMMARY

Crossref query strategies used:
- Direct DOI resolution on known candidate (Mayew & Venkatachalam 2012) to verify venue, year, citation count.
- Author + title-fragment queries for each prior (Larcker-Zakolyukina; Hobson-Mayew-Venkatachalam 2012 and 2017; Matsumoto-Pronk-Roelofsen; Price-Doran-Peterson-Bliss; Bertrand-Schoar).
- Title-targeted Crossref query `query.title=analyzing+speech+detect+financial+misreporting` + author filter to confirm the 2012 JAR paper and distinguish it from the 2017 sequel.
- Broad topic sweeps (`CEO tone earnings call`; `manager presentation qa earnings call`; `manager sentiment tone`) sorted by citation count — these produced mostly off-domain results (biomedical, ML, marketing), confirming that Crossref's cross-discipline ranking is noisy for this niche and that author/title-targeted queries are the reliable strategy.

Top-tier papers identified meeting the CEO-speech-specific + top-tier-journal constraints: N=3 (Mayew-Venkatachalam 2012 JF; Larcker-Zakolyukina 2012 JAR; Hobson-Mayew-Venkatachalam 2012 JAR).

How the top recommendation was chosen: Mayew & Venkatachalam (2012) wins on three independent axes. (1) Venue — Journal of Finance is the flagship journal in the eligible set and the most credentialing placement for a finance-thesis anchor. (2) Title framing — "The Power of Voice" is maximally load-bearing for the exact claim we are anchoring (CEO speech is material). (3) Same author duo is behind much of this literature, so one citation transports the reader into the full CEO-speech research program. The thesis's LM-uncertainty-on-text methodology is closer technique-wise to Larcker-Zakolyukina, but the anchor's job is to establish materiality of CEO speech broadly, not method identity — and L-Z is retained as RU#1 for the closer methodological fit.
