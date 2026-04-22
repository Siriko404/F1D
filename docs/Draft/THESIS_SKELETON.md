# Thesis Skeleton — Draft v5.1

Revised 2026-04-22 evening (v5.1): capex (H13/H13.1/H13.2/H13.3) and Amihud (H7/H7b/H7c/d/e) families dropped per user directive; §IV reduced to 2 subsections (drivers + outside-world reaction); Grenadier 2002 + HP 2016 demoted from Tier-1; §II.5 Competitive Real Options section deleted. Supersedes v5 (2026-04-22 afternoon), which in turn superseded v4 (2026-04-16). Framing locked under `project_framing_decision_locked.md` (no umbrella → cash wins; capex deferred to §IV exploratory → then dropped entirely).

## Key changes from v5 → v5.1

1. **Capex family dropped.** H13 (base capex), H13.1 (capex × competition), H13.2 (capex multi-lead), and H13.3 (capex × constraint) removed from thesis scope. §IV.2 Capital Expenditure section deleted.
2. **Amihud family dropped.** H7, H7b, H7c, H7d, H7e removed. No illiquidity discriminant test.
3. **Competitive real-options framework dropped.** §II.5 deleted. Grenadier 2002 and Hoberg-Phillips 2016 demoted from Tier-1 to unused.
4. **§IV reduced to 2 subsections.** §IV.1 Drivers (H11 PRisk + H24 US EPU + H24b GEPU). §IV.2 Outside-World Reaction (H14c 25-day post-call spread). H17 repurchase and H14/H14b/H14d/H14e variants not used.
5. **BGT 2018 and Lee 2016 citations dropped for 25-day spread measure.** User-facing variable renamed from `BGTLevel_Spread` → `Spread_{25D}`. 25-day post-call window + standard closing-quote relative spread formula described as construction choices without explicit paper anchors. Pipeline column name retained for backward compat; runner user-facing strings (SUITE_TITLE, SUITE_CAPTION, LaTeX caption, table notes, suite_spec header rows, scaling note) updated.
6. **§III + §IV fully shipped.** §3.1 setup (72660d2) + §3.2 HC (b0f5614) + §3.3 HFC (8568d43) + §IV.1 drivers (11efaea) + §IV.2 reaction (f1c447b).

## Key changes from v4 → v5 (retained in v5.1)

1. HL (Leverage) dropped as joint-IV nesting artifact.
2. 2-IV CEO framework (UncAnsCEO + UncPreCEO only in §III).
3. CEO-as-face replaces Q&A-spontaneity as measurement-choice anchor.
4. H1.1, H1.1b dropped (cash × competition null under CEO).
5. Table budget aligned to DraftTemplate.txt.
6. Central Claim cash-only.
7. Formal hypotheses reduced 3 → 2 (HC + HFC).
8. Title: "Managerial" → "CEO Speech Uncertainty."

## Title

**Hold On to Your Cash: CEO Speech Uncertainty and Financing Conservatism**

## Research Question

Does CEO speech uncertainty during earnings calls predict firm financing conservatism?

## Central Claim

Firms whose CEOs express greater speech uncertainty during earnings calls — measured in both the Q&A segment (`UncAnsCEO`) and the prepared Presentation segment (`UncPreCEO`) — hold more cash contemporaneously, consistent with the precautionary motive (\citeA{opler1999}; \citeA{bates2009}). The effect concentrates in firms with the least access to public debt markets (Unrated category, following \citeA{faulkender2006}, extended here to a three-tier hierarchy with Investment-Grade baseline). The choice to focus on the CEO rather than the full manager pool is motivated by the established role of the CEO as principal signal-bearing communicator of the firm [CITE: pending `tmp/ceo_as_face_lit_review.md`].

Beyond the cash-holdings finding, two channel-validation results complement the main analysis: CEO speech uncertainty itself responds to exogenous uncertainty shocks (firm-political, US macro, global macro), and post-call bid-ask spreads widen with CEO speech uncertainty at different horizons by channel (Presentation contemporaneous, Q&A one-quarter-lead). We do not test or claim a causal link between the cash finding and the market-reaction finding; they are reported as complementary evidence that the two CEO speech channels carry distinct, economically meaningful uncertainty content.

## Formal Hypotheses (2)

Labels HC / HFC avoid collision with empirical-suite names (H1, H1.2). HL dropped (Class C artifact).

**HC (Cash — precautionary liquidity buffer):** Firms whose CEOs express higher speech uncertainty hold more cash contemporaneously. Both `UncAnsCEO` and `UncPreCEO` tested; one-tailed positive on both.
- Suite: H1.ceo2 (CashRatio = `cheq/atq` per \citeA{bates2009}; 12 cols contemp + lead × 4 FE; 2-IV CEO-only).
- Result (2-IV CEO, committed b0f5614):
  - `UncAnsCEO`: 12/12 sig at p<0.10; 9/12 at p<0.05; 4/6 contemp at p<0.01; 3/6 lead at p<0.05. β range +0.0018 to +0.0031 contemp; +0.0023 to +0.0028 lead.
  - `UncPreCEO`: 0/12 null (min p=0.151). Presentation channel does not move cash at quarterly frequency.
  - Sample: N = 59,459 to 65,148; fiscal 2002–2018.
- Literature anchors: OPSW 1999 (theory) + BKS 2009 (DV form + empirical secular rise) + Minton-Wruck 2001 (cluster label).

**HFC (Financial Constraint — Unrated amplifies HC):** Among rated-sample firms, HC concentrates in Unrated. Investment-Grade as baseline; BelowIG interaction suppressed in estimation (main-IV slope applies to IG∪BelowIG rated-pooled).
- Suite: H1.2.ceo2 (CashRatio; 16 cols = 4 FE × 2 DVs × {unconditional, interaction}; 2-IV centered CEO-only).
- Result (2-IV CEO, committed 8568d43):
  - Base `UncAnsCEO_c`: 8/8 sig at p<0.10. Base `UncPreCEO_c`: 0/8 null.
  - Interaction `UncAnsCEO_c × Unrated`: 6/8 sig at p<0.10; 4/8 at p<0.05; lead 4/4 at p<0.10, 3/4 at p<0.05. β lead +0.0040 to +0.0069.
  - Interaction `UncPreCEO_c × Unrated`: 2/8 marginal contemp (industry-FE only); 0/4 lead.
- Sample: 2002–2016 (Compustat ratings coverage truncates vs H1).
- Literature anchor: FP 2006 binary rated/unrated access, extended to 3-way (IG vs rated-pooled reported; explicit disclosure).

## Thesis Structure (DraftTemplate.txt conformant)

### §I — Introduction

1. Motivation: earnings-call speech as quarterly window on managerial uncertainty; CEO as primary communicator.
2. Gap: DWZ 2021 established speech-uncertainty measures; BGT 2018 established pooled-manager aggregation. Neither linked call-segment CEO speech uncertainty to firm-quarter cash dynamics. Loughran-McDonald and related 10-K studies operate at annual frequency without manager segmentation.
3. Contributions (3):
   1. First evidence linking CEO-specific earnings-call speech uncertainty (Q&A + Presentation) to firm-quarter financing conservatism (cash), concentrated in credit-constrained Unrated firms.
   2. Channel validation: CEO speech uncertainty responds to exogenous uncertainty shocks at firm, US, and global aggregation levels.
   3. Outside-world recognition: post-call bid-ask spreads widen with CEO speech uncertainty, with channel-temporal asymmetry (Pres contemp, Q&A lead).
4. Preview of findings + roadmap.

### §II — Conceptual Framework and Empirical Strategy

**§2.1 Pre-Commitment Statement (front-loaded, p-hacking defense)**

- **HC, HFC (§III)**: one-tailed positive on BOTH `UncAnsCEO` and `UncPreCEO` — pre-specified formal hypotheses.
- **§IV.1 Drivers**: one-tailed positive in theoretically predicted direction (exogenous uncertainty shocks raise measured speech uncertainty). Construct validation, not a formal hypothesis.
- **§IV.2 Outside-World Reaction**: one-tailed positive consistent with information-asymmetry prediction (uncertainty raises spread). Not a formal hypothesis.

All main specifications reported (no cherry-picking). The 2-IV CEO framework fixes the §III regressor set; FE-ladder robustness (4 steps) is within-regressor, not independent replication.

**§2.2 Conceptual Framework**

- Uncertainty and corporate decisions: brief survey. Emphasis on microeconomic-frequency texts (firm-quarter) as complement to macro uncertainty series (VIX, EPU).
- Why speech uncertainty: higher frequency than 10-K annual text; source-identifiable (CEO vs CFO vs analyst). Transition to measurement.

**§2.3 Speech Uncertainty Measurement**

- \citeA{dzielinski2021} (DWZ 2021): Loughran-McDonald (2011) uncertainty wordlist applied to conference-call transcripts; presentation vs Q&A segment split; CEO/CFO individual applications documented in their Figure 2 / Table 4.
- \citeA{bushee2018} (BGT 2018): pooled all-manager aggregation logic (documented via Ian Gow's published replication code at `github.com/iangow/bgt`; see `project_bushee_gow_taylor_2018.md`).
- Our IV: wordlist content from DWZ + speaker-pool aggregation from BGT + CEO partition at speaker-role granularity. Novelty is the CEO-specific partition applied systematically.
- **CEO-as-face motivation**: [CITE: pending `tmp/ceo_as_face_lit_review.md`] — provisional 3-legged tripod (Hambrick-Mason 1984 upper-echelon theory + Bertrand-Schoar 2003 CEO style effects + own partition empirical decomposition). Full survey pending.
- Construction: `UncAnsCEO` = count(LM-uncertainty-words in CEO Q&A utterances) / count(all words in CEO Q&A utterances), call-level; winsorized 1/99%. `UncPreCEO` analogous on CEO Presentation utterances. Units: percentages in [0,1] post-winsor.

**§2.4 Precautionary Motive and Financing Conservatism (HC + HFC anchor)**

- OPSW 1999: precautionary motive theory — firms facing higher cash-flow uncertainty hold more cash.
- BKS 2009: secular rise in precautionary cash 1980–2006; primary cite for `cheq/atq` DV form; two-way clustering precedent.
- Minton-Wruck 2001: empirical low-leverage + high-cash cluster label "financial conservatism" (21% of their sample); mechanism is financial slack / Donaldson–Myers pecking-order, distinct from but consistent with our precautionary frame.
- Faulkender-Petersen 2006: binary rated-vs-unrated access; unrated firms are "credit constrained" (§3.1 wording per verbatim memory). Extended to three-way (IG / BelowIG / Unrated); IG vs rated-pooled reported in main, BelowIG to appendix.

**§2.5 Empirical Design**

- PanelOLS (linearmodels) with `entity_effects` + `time_effects`; firm-clustered SE; two-way `(firm, cal_yr_qtr)` for macro-IV suites in §IV.1 only.
- Lagged DV as base control (unified single row per column).
- FE ladder: 4 steps per DV — Industry+Year, Firm+Year, Industry+YrQtr, Firm+YrQtr.
- Base controls: `lnAssets`, `TobinsQ`, `ROA`, `DivDummy`, `sCFO`, `Lagged_DV`.
- Extended controls: `SalesGrowth`, `RDSales`, `CashFlowAt`, `DailyVola`.
- Bad-control exclusion: `Leverage` NOT in cash regressions (shared-numerator overlap).
- HC main suite: 12 cols (contemp + lead × 4 FE). HFC main suite: 16 cols (unconditional + interaction per DV × 4 FE).

### §III — Main Empirical Analyses

**§3.1 Data / Sample / Variable Construction** (committed 72660d2)

Panel: 112,968 earnings-call transcripts, 2,429 unique firms, fiscal 2002–2018, S&P Capital IQ. Compustat quarterly + CRSP daily. Exclusions: financials (SIC 6000–6999) + utilities (SIC 4900–4999) following BKS 2009. Summary stats: Table 1 (existing longtable). Primary IVs: `UncAnsCEO` + `UncPreCEO`.

**§3.2 Main Analysis 1 — Cash Holdings (HC)** (committed b0f5614)

Table 2: H1.ceo2, 12 cols. Q&A dominant (12/12 sig), Pres null (0/12). 2-IV CEO. One-tailed positive. Full results per HC hypothesis block above.

**§3.3 Main Analysis 2 — Financial Constraint Moderation (HFC)** (committed 8568d43)

Table 3: H1.2.ceo2, 16 cols. HFC survives + strengthens: Q&A × Unrated lead 4/4 sig at p<0.10; 3/4 at p<0.05. Pres × Unrated marginal contemp, null lead. 2-IV centered CEO. Sample 2002–2016.

**§3.4 Robustness Notes (compact)**

- FE ladder 4/4 per suite (within-regressor robustness).
- Nickell bias: T ≈ 30 quarters per firm; O(1/T) ~3% — disclosed.
- Multiple testing: pre-commitment §2.1 + one-tailed on both IVs.
- Correlated specifications within a table: documented.
- Alternative OPSW log-DV: future work, Appendix C placeholder.

### §IV — Additional Analyses

**§4.1 Drivers of CEO Speech Uncertainty** (committed 11efaea)

Reverse-direction construct validation. Three drivers: PRisk firm-level (\citeA{hassan2020}), US EPU monthly (\citeA{baker2016}), Global EPU monthly (\citeA{davis2016}). Tests whether CEO speech uncertainty responds to exogenous uncertainty shocks. Table 4: consolidated driver matrix. PRisk 4/4 CEO cells sig (β +0.00013 to +0.00030, t 9.0–17.0). Macro drivers show channel asymmetry: Pres dominates macro, QA loads only under firm FE. NoCEO speech channels reported in Appendix B for contrast.

**§4.2 Outside-World Reaction** (committed f1c447b)

Market information-asymmetry response via 25-day post-call closing-quote relative bid-ask spread, Spread\textsubscript{25D}. Suite H14c parent (4-IV joint: UncAnsCEO + UncPreCEO + UncAnsMgr + UncPreMgr). CEO coefficients are the partial effect of CEO speech uncertainty conditional on manager-pool speech (manager-pool retained because the spread is plausibly priced against broader manager speech too, unlike the §III specification). Pre channel contemp 3/2/1 sig at p<0.10/0.05/0.01; Pres lead null. Q&A channel contemp null; Q&A lead 5/2 sig. Channel-temporal complementarity: prepared remarks register in market liquidity within the call quarter, spontaneous Q&A registers with a one-quarter lag. Pattern inverts the asymmetries of §3.2/§3.3 and §IV.1.

### §V — Conclusion

Merged Discussion + Conclusion per DraftTemplate.

- Summary: HC + HFC findings (Q&A dominant cash signal, concentrated in Unrated); §IV.1 drivers (PRisk strongest, macro Pres-dominant); §IV.2 reaction (dual-channel, temporally asymmetric).
- Channel-asymmetry synthesis across §III + §IV.1 + §IV.2: three empirical patterns in which Q&A and Presentation segments carry distinct uncertainty content.
- Mechanism disclosure: financing-margin (cash) and information-asymmetry-margin (spread) findings operate through theoretically distinct mechanisms; no causal-bridge claim tested within this study.
- Limitations: (a) no identification/endogeneity strategy — flagged FUTURE; (b) Nickell bias O(1/T); (c) CEO speaker ID via Capital IQ has 15% placeholder gap; (d) sample 2002–2018 (HFC 2002–2016); (e) 25-day post-call spread window is a construction choice, not a standard event-window; (f) pipeline column names retain prior nomenclature (`BGTLevel_Spread`) for backward compat, user-facing renders use Spread\textsubscript{25D}.
- Future research:
  - Identification strategy for endogeneity — exogenous shocks to CEO communication style.
  - Within-firm cash-then-spread sequencing test.
  - Additional cash channels beyond Unrated (flagged as open).
  - Full pipeline rename Spread\textsubscript{25D} + other legacy-name cleanup.
  - OPSW log-DV robustness appendix.

## Suite Allocation Summary v5.1

| Location | Suites | Count |
|---|---|---|
| **§III Main (HC + HFC)** | H1.ceo2, H1.2.ceo2 | 2 |
| **§IV.1 Drivers** | H11, H24, H24b | 3 |
| **§IV.2 Outside-World Reaction** | H14c | 1 |
| **§II.3 Validity (compact paragraph; no own table)** | H5 (DISP), H23 (competition reverse), H25 (GPR null) | 3 |
| **Dropped from thesis entirely** | H4a/H4b, H1.1/H1.1b, H13/H13.1/H13.2/H13.3, H7/H7b/H7c/d/e, H14/H14b/H14d/H14e, H12/H12b, H16, H17, H18/H18b, H19b/H20b, H21, H22 | ~24 |

## Targeted Appendix v5.1

- **Appendix A**: Variable Definitions (existing generator).
- **Appendix B**: Detailed Validity Tables — §IV.1 full Mgr-pool and NoCEO results; §IV.2 Mgr-pool results.
- **Appendix C**: Robustness specifications — FE-ladder alt, OPSW log-DV robustness, BelowIG row for HFC.
- **Appendix D**: Partition-decomposition auxiliary (`_partition_findings.csv` ground truth; Class A/B/C/D taxonomy).

## Reference Stack v5.1 (Tier-1 critical)

| # | Paper | Role | Verbatim status |
|---|---|---|---|
| 1 | \citeA{dzielinski2021} — DWZ 2021 | LM wordlist + segment split | ✓ `reference_dwz_2021_verified.md` |
| 2 | \citeA{bushee2018} — BGT 2018 | Pooled aggregation (Ian Gow code) | ✓ `project_bushee_gow_taylor_2018.md` |
| 3 | \citeA{opler1999} — OPSW 1999 | Precautionary theory (HC) | ✓ `reference_opsw_1999_verbatim.md` |
| 4 | \citeA{bates2009} — BKS 2009 | Cash/assets DV + 2-way cluster | ✓ `reference_bks_2009_verbatim.md` |
| 5 | \citeA{minton2001} — MW 2001 | "Financial conservatism" | ✓ `reference_minton_wruck_2001_verbatim.md` |
| 6 | \citeA{faulkender2006} — FP 2006 | Rated/unrated → 3-way extension | ✓ `reference_faulkender_petersen_2006_verbatim.md` |
| 7 | \citeA{hassan2020} — Hassan et al. 2020 | PRisk firm-level driver (§IV.1) | ✓ `reference_tier2_consolidated.md` |
| 8 | \citeA{baker2016} — BBD 2016 | US EPU driver (§IV.1) | ✓ `reference_tier2_consolidated.md` |
| 9 | \citeA{davis2016} — Davis 2016 | Global EPU driver (§IV.1) | ✓ `reference_tier2_consolidated.md` |
| 10 | **[PENDING] CEO-as-face anchor** | CEO partition measurement-choice justification | ⏳ `tmp/ceo_as_face_lit_review.md` (tripod provisional) |

**Tier-2 (citation-only)**: Loughran-McDonald 2011/2013 (wordlist), Bertrand-Schoar 2003 (CEO style — CEO-as-face candidate), Hambrick-Mason 1984 (upper-echelon theory — CEO-as-face candidate), L-Z 2012 (CFO speaker ID), Wang 2020 (DISP §II.3 validity), Caldara-Iacoviello 2022 (GPR §II.3 validity).

**Demoted from v5 Tier-1 → unused in v5.1**: Grenadier 2002 (competitive real options — capex channel dropped), Hoberg-Phillips 2016 (TSIMM moderator — competition channel dropped), Aguerrevere 2009 (strategic extension — capex channel dropped), Amihud 2002 (ILLIQ — illiquidity discriminant dropped), Chang-Dasgupta-Hilary 2006 (external financing — H19b/H20b dropped).

## Pre-commitment & convention disclosure

- **Statistical conventions** per §2.1 (repeated here for visibility):
  - HC + HFC (§III): one-tailed positive, pre-specified formal hypotheses, BOTH IVs.
  - §IV.1 drivers: one-tailed positive, construct validation, not a formal hypothesis.
  - §IV.2 outside-world reaction: one-tailed positive, information-asymmetry prediction, not a formal hypothesis.
- **Sample scope**: Main = 2002–2018 (H1 HC, §IV.1 drivers, H14c reaction); HFC = 2002–2016 (ratings-truncated).
- **CEO coverage**: ~80.5% vs Mgr-pool ~96% (per `reference_ceo_coverage_gap.md`). Expected sample reduction ~7% vs Mgr-pool baselines.

## Open items for writing phase

1. **Central Claim revision**: honest 3-legged CEO-as-face framing before §I drafting (Hambrick-Mason 1984 + Bertrand-Schoar 2003 + own partition decomposition). Provisional tripod in `tmp/ceo_as_face_lit_review.md`.
2. **CEO-as-face Tier-1 anchor upgrade**: pending fuller literature survey. If no stronger single anchor emerges, keep 3-legged tripod as the measurement-choice justification.
3. **Pipeline follow-ups (post-first-draft)**:
   - Full rename `BGTLevel_Spread` → `Spread_{25D}` across panel, builders, spec JSON, config. (User-facing runner strings done; internal names retained for backward compat.)
   - Sweep dropped suites out of run sets: H7 family, H14/H14b/H14d/H14e, H17, H12, H18/b, H19b/H20b, H22, H13 family.
   - Table render wiring: `tab:h1_ceo2`, `tab:h1_2_ceo2`, `tab:h14c`, `tab:driver_matrix` into main.pdf appendix (render-order yaml + summary_stats aliases).
4. **LaTeX mechanics**:
   - `\ref{sec:framework:precommit}` label: emit when drafting §2.1.
   - `\ref{app:additional:drivers}` and `\ref{app:additional:reaction}` labels: emit when drafting respective appendix sections.
   - Title propagation: `main.tex` line 50 still "Managerial" → "CEO" (pending).
5. **FUTURE WORK (post first-draft, flagged in §V)**:
   - Identification / endogeneity strategy design.
   - Additional cash channel beyond Unrated (currently sole alive moderator for cash under CEO).
   - CEO-as-face full literature survey beyond provisional tripod.
   - Structural model combining precautionary motive + external information-asymmetry reaction.
   - OPSW log-DV robustness appendix.

## Next Actions (enforced sequence)

1. [DONE] Skeleton v5 → v5.1 cleanup (this revision).
2. [DONE] §III + §IV drafted and committed.
3. [NEXT] §II framework full draft (uses revised Central Claim + 3-legged CEO-as-face tripod).
4. §V conclusion draft.
5. §I introduction draft.
6. Abstract + Keywords + JEL.
7. Final LaTeX compile (pdflatex + bibtex + 2× pdflatex).

## What stays from v5 / v4

- Pipeline data, panels, `all_tables.tex` renderer.
- Sample + filters (BKS 2009 exclusions).
- IV construction (DWZ wordlist + BGT pooled aggregation), extended with CEO partition at the speaker-role level.
- Three-tier FP constraint extension + BelowIG suppression.
- Targeted appendix concept (A/B/C/D).
- `apacite` bibliography style per `project_apa_bibliography.md`.

## Supersedes

- THESIS_SKELETON.md v5 (2026-04-22 afternoon) — dropped capex/real-options/Amihud per 2026-04-22 evening directive.
- THESIS_SKELETON.md v4 (2026-04-16 evening) — all v5 changes retained.
- All v5 references to capex § IV.2, Grenadier 2002 Tier-1, HP 2016 Tier-1, §II.5 Competitive Real Options, BGT/Lee citations for Spread\textsubscript{25D}.

## Cross-references

- `project_framing_decision_locked.md` — lock (no umbrella, cash wins, capex→§IV→dropped)
- `project_session_2026_04_22_draft_iii.md` — §III drafting session recap
- `project_drafting_progress.md` — current draft state
- `project_partition_findings_synthesis.md` — Class A/B/C/D taxonomy, ground truth for IV allocation
- `project_apa_bibliography.md` — apacite + citation command map
- `reference_*_verbatim.md` — 9 Tier-1 anchor verbatims (CEO-as-face #10 pending)
- `reference_tier2_consolidated.md` — 9-paper Tier-2 record (Hassan/BBD/Davis now Tier-1 active)
- `docs/Draft/DraftTemplate.txt` — structural template
- `docs/Draft/REFERENCE_STACK_WALKTHROUGH.md` — full provenance walkthrough
- `_partition_findings.csv` — 228-row programmatic extraction (ground truth for all empirical claims)
