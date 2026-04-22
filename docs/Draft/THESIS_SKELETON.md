# Thesis Skeleton — Draft v5

Revised 2026-04-22. Supersedes v4 (2026-04-16). Locked under `project_framing_decision_locked.md` (no umbrella → cash wins, capex → §IV exploratory).

## Key changes from v4

1. **HL (Leverage) dropped entirely.** Partition decomposition revealed the `UncAnsMgr` leverage signal (H4a 6/6 lead, H4b 5/6 lead) was a joint-IV nesting artifact — it collapses under `UncAnsCEO` and `UncAnsNoCEO` individually (Class C in `project_partition_findings_synthesis.md`). Cash-only main.
2. **Main IV framework: 2-IV CEO.** Primary regressors per spec are `UncAnsCEO` (CEO Q&A uncertainty) + `UncPreCEO` (CEO Presentation uncertainty). `UncAnsMgr` (pool) dropped from all §III specs. Both CEO measures reported equally; QA-vs-Pre asymmetry is an empirical question, NOT a pre-committed theoretical claim.
3. **CEO-as-face replaces Q&A-spontaneity** as the measurement-choice anchor. The justification for CEO partition (vs full manager pool) is the established role of the CEO as principal external communicator; new Tier-1 citation pending lit-search agent.
4. **H1.1, H1.1b dropped from main.** Cash × Competition interaction null under CEO partition (`UncAnsCEO_c × TSIMM` 0/4, `UncAnsCEO_c × HighTSIMM` 0/4 both `.r` variants).
5. **H13.3 dropped.** Capex × Constraint interaction null under CEO (0/8 across all columns).
6. **Table budget aligned to DraftTemplate.txt** (9 tables: T1 summary stats + ~T2-T9 main/additional).
7. **Central Claim rewritten** — cash-only financing conservatism + exploratory capex. No leverage. No CausaL bridge claim.
8. **Formal hypotheses reduced 3 → 2**: HC + HFC only.
9. **§IV reorganized** per template: (1) drivers of speech uncertainty, (2) capex + competition exploratory, (3) outside-world reaction.
10. **Title amended**: "Managerial Speech Uncertainty" → "CEO Speech Uncertainty."

## Title

**Hold On to Your Cash: CEO Speech Uncertainty and Financing Conservatism**

## Research Question

Does CEO speech uncertainty during earnings calls predict firm financing conservatism?

## Central Claim

Firms whose CEOs express greater speech uncertainty during earnings calls — measured in both the Q&A segment (`UncAnsCEO`) and the prepared Presentation segment (`UncPreCEO`) — hold more cash contemporaneously, consistent with the precautionary motive \cite{opler1999}; \cite{bates2009}. The effect concentrates in firms with the least access to public debt markets (Unrated category, following the binary rated/unrated classification of \cite{faulkender2006}, extended here to a three-tier hierarchy with Investment-Grade as comparison baseline). The choice to focus on the CEO rather than the full manager pool is motivated by the established role of the CEO as principal signal-bearing communicator of the firm [CITE: pending `tmp/ceo_as_face_lit_review.md`].

We additionally examine the capital-expenditure margin as an exploratory finding: capex rises with CEO speech uncertainty, and the effect concentrates in competitive product markets. We interpret this through the Grenadier (2002) competitive-real-options framework, under which competition erodes the option value of waiting. The financing-margin response (cash) and investment-margin finding operate through theoretically distinct mechanisms; we do not test or claim a causal link between them.

## Formal Hypotheses (2)

Labels HC / HFC avoid collision with empirical-suite names (H1, H1.2). HL dropped (Class C artifact). HK was never formal (capex exploratory throughout v4; now §IV.2).

**HC (Cash — precautionary liquidity buffer):** Firms whose CEOs express higher speech uncertainty hold more cash contemporaneously. Both `UncAnsCEO` and `UncPreCEO` tested; one-tailed positive on both.
- Suite: H1 (CashRatio = `cheq/atq` per \cite{bates2009}; 12 cols contemp + lead × 4 FE; 2-IV CEO)
- Result (2-IV CEO): [TBD: β, (SE), p] — pending spec rerun.
- `.r` partition baseline for calibration: `UncAnsCEO` 6/6 at p<0.10 contemp, 6/4 lead; `UncPreCEO` null under `.r` (0/6+0/6).
- Literature anchors: OPSW 1999 (theory) + BKS 2009 (DV form + empirical secular rise) + Minton-Wruck 2001 (cluster label).

**HFC (Financial Constraint — Unrated amplifies HC):** Among rated-sample firms, HC concentrates in Unrated. Investment-Grade as baseline; BelowIG suppressed (null + no economic content per `project_step8_infrastructure_progress.md`).
- Suite: H1.2 (CashRatio; 16 cols = 4 FE × 2 DVs × {unconditional, interaction}; 2-IV centered)
- Result (2-IV CEO): [TBD: β, (SE), p] — pending spec rerun.
- `.r` baseline: `UncAnsCEO_c × Unrated` 2/0/0 contemp + 2/1/0 lead (MARGINAL; survival under 2-IV CEO partialing uncertain; verify before committing §3.3).
- Sample: 2002–2016 (Compustat ratings coverage truncates vs H1 2002–2018).
- Literature anchor: FP 2006 binary access, extended to 3-way (we report IG vs Unrated only; explicit disclosure per `project_thesis_skeleton.md` v4 carry-over).

## Capital Expenditure (exploratory, §IV.2 per template)

Not a formal hypothesis. Two-tailed for H13 base; one-tailed explanatory for H13.1 moderator (Grenadier directional).

**Empirical findings under CEO measures** (source: `_partition_findings.csv` H13.r + H13.1.r rows):
- H13 (base capex, two-tailed): `UncAnsCEO` 4/2/1 contemp + 3/3/2 lead; `UncAnsNoCEO` 1/1/0 contemp + 3/3/1 lead — CEO dominates but signal distributes.
- H13.1 (Capex × z(log TSIMM), Hoberg-Phillips 2016 moderator, one-tailed explanatory): `UncAnsCEO_c × TSIMM` 0/0/0 contemp + 4/3/0 lead — lead-only interaction.

**Interpretation (post-hoc, §4.2 header, NOT §II hypothesis development):** consistent with Grenadier 2002 competition erosion of option-to-wait. Financing-margin (HC/HFC) and investment-margin findings operate through theoretically distinct mechanisms (precautionary vs competitive real options); no causal-bridge claim within this study.

## Thesis Structure (DraftTemplate.txt conformant)

### §I — Introduction

1. Motivation: earnings-call speech as quarterly window on managerial uncertainty; CEO as primary communicator.
2. Gap: DWZ 2021 established speech-uncertainty measures; BGT 2018 established pooled-manager aggregation. Neither linked call-segment CEO speech uncertainty to firm-quarter cash dynamics. \cite{loughran2013} and related 10-K studies operate at annual frequency without manager segmentation.
3. Contributions (2):
   1. First evidence linking CEO-specific earnings-call speech uncertainty (Q&A + Presentation, both) to firm-quarter financing conservatism (cash), with effect concentrating in credit-constrained Unrated firms.
   2. Exploratory: capex rises with CEO speech uncertainty, concentrated in competitive product markets, interpreted via Grenadier 2002 competitive real options.
4. Preview of findings + roadmap.

### §II — Conceptual Framework and Empirical Strategy

**§2.1 Pre-Commitment Statement (front-loaded, p-hacking defense)**

Three statistical conventions:
- HC, HFC: **one-tailed** inference in the theory-predicted direction on BOTH `UncAnsCEO` and `UncPreCEO`.
- Capex §IV.2 (H13 base): **two-tailed** exploratory.
- Capex-competition moderator §IV.2 (H13.1): **one-tailed** explanatory in Grenadier-predicted direction.

All main specifications reported (no cherry-picking). The 2-IV CEO framework fixes the regressor set; FE-ladder robustness (4 steps) is within-regressor robustness, not independent replication.

**§2.2 Conceptual Framework**

- Uncertainty and corporate decisions: brief survey. Emphasis on microeconomic-frequency texts (firm-quarter) as a complement to macro uncertainty series (VIX, EPU).
- Why speech uncertainty: higher frequency than 10-K annual text; source-identifiable (CEO vs CFO vs analyst). Transition to measurement.

**§2.3 Speech Uncertainty Measurement**

- `\cite{dzielinski2021}` (DWZ 2021): Loughran-McDonald (2011) uncertainty wordlist applied to conference-call transcripts; presentation vs Q&A segment split; CEO/CFO individual applications documented in their Figure 2 / Table 4.
- `\cite{bushee2018}` (BGT 2018): pooled all-manager aggregation logic (documented via Ian Gow's published replication code at `github.com/iangow/bgt`; the paper body does not disclose pooling explicitly — see `project_bushee_gow_taylor_2018.md`).
- Our IV: wordlist content from DWZ + speaker-pool aggregation from BGT + CEO partition at speaker-role granularity. Novelty is the CEO-specific partition applied systematically.
- **CEO-as-face motivation**: [CITE: pending `tmp/ceo_as_face_lit_review.md`] — empirical finance literature establishing the CEO as firm's principal external communicator and primary signal-bearer. This motivates the CEO partition (vs broader manager pool).
- Construction: `UncAnsCEO` = count(LM-uncertainty-words in CEO Q&A utterances) / count(all words in CEO Q&A utterances), call-level; winsorized 1/99%. `UncPreCEO` analogous on CEO Presentation utterances. Units: percentages in [0,1] post-winsor (raw mean/sd reported in §3.1 + Table 1).

**§2.4 Precautionary Motive and Financing Conservatism (HC + HFC anchor)**

- OPSW 1999 (`\cite{opler1999}`): precautionary motive theory — firms facing higher cash-flow uncertainty hold more cash (§2.1 of their paper). Directly predicts HC.
- BKS 2009 (`\cite{bates2009}`): secular rise in precautionary cash 1980–2006; primary cite for `cheq/atq` DV form; two-way clustering precedent adopted.
- Minton-Wruck 2001 (`\cite{minton2001}`): empirical low-leverage + high-cash cluster label "financial conservatism" (21% of their sample); mechanism is financial slack / Donaldson–Myers pecking-order, distinct from but consistent with our precautionary frame.
- Faulkender-Petersen 2006 (`\cite{faulkender2006}`): binary rated-vs-unrated access; unrated firms are "credit constrained" (§3.1 wording, per `reference_faulkender_petersen_2006_verbatim.md`). We extend to three-way (IG / BelowIG / Unrated), report IG vs Unrated in main, suppress BelowIG to appendix.

**§2.5 Competitive Real Options (interpretive only, §IV.2)**

- Grenadier 2002 (`\cite{grenadier2002}`): in perfectly competitive product markets, option value of waiting erodes — rivals' exercise accelerates own exercise. Predicts capex↑ under uncertainty when competition is high.
- Aguerrevere 2009 demoted Tier-2 (strategic-equilibrium extension; not load-bearing).

**§2.6 Empirical Design**

- PanelOLS (linearmodels) with `entity_effects` + `time_effects`; firm-clustered SE per `feedback_bks2009_twoway_cluster.md` (two-way firm × `cal_yr_qtr` for macro-IV suites in §IV.1 only).
- Lagged DV as base control (unified single row per column).
- FE ladder: 4 steps per DV — Industry+Year, Firm+Year, Industry+YrQtr, Firm+YrQtr.
- Base controls: `lnAssets`, `TobinsQ`, `ROA`, `DivDummy`, `sCFO`, `Lagged_DV`.
- Extended controls: `SalesGrowth`, `RDSales`, `CashFlowAt`, `DailyVola`.
- Bad-control exclusion: `Leverage` NOT in cash regressions (shared numerator overlap per `feedback_bad_control_exclusion.md`).
- Each main suite: contemp + 1-quarter lead DV = 12 cols.

### §III — Main Empirical Analyses

**§3.1 Data / Sample / Variable Construction**

- Panel: 112,968 earnings-call transcripts, 2,429 unique firms, fiscal 2002–2018, sourced S&P Capital IQ.
- Merged: Compustat quarterly fundamentals + CRSP daily security data.
- Exclusions: financials (SIC 6000–6999) + regulated utilities (SIC 4900–4999), following `\cite{bates2009}`.
- Summary statistics: Table 1 (existing longtable in appendix; `docs/Draft/generate_summary_stats.py`).
- Primary IVs: `UncAnsCEO` + `UncPreCEO` (2-IV CEO framework; see §2.3).

**§3.2 Main Analysis 1 — Cash Holdings (HC)**

- Table 2: H1 CashRatio + CashRatio_lead × 4 FE = 12 cols.
- 2-IV CEO: `UncAnsCEO` + `UncPreCEO` per spec.
- One-tailed positive on both IVs.
- Result (post-rerun): [TBD: β, (SE), p per IV per column].
- Interpretation: precautionary cash buffer; quarterly margin (cash actively managed at firm-quarter frequency).
- Robustness within-table: 4 FE steps.
- QA vs Pre: report empirical dominance descriptively; do NOT pre-argue directional asymmetry.

**§3.3 Main Analysis 2 — Financial Constraint Moderation (HFC) — CONDITIONAL ON RERUN**

- Table 3: H1.2 CashRatio + CashRatio_lead × 4 FE × {unconditional, interaction} = 16 cols.
- 2-IV centered CEO: `UncAnsCEO_c`, `UncPreCEO_c`, `UncAnsCEO_c × Unrated`, `UncPreCEO_c × Unrated`.
- One-tailed positive on main + interaction.
- Result (post-rerun): [TBD: β, (SE), p].
- **Block**: verify interaction survives 2-IV CEO partialing before drafting §3.3 (`.r` baseline marginal 2/0/0 contemp + 2/1/0 lead for `UncAnsCEO_c × Unrated`).
- BelowIG row suppressed (null + appendix only).
- Sample: 2002–2016.

**§3.4 Robustness Notes (compact)**

- FE ladder 4/4 specs per suite (within-regressor robustness).
- Nickell bias: T ≈ 30 quarters per firm; O(1/T) ~3% of true β — disclosed.
- Multiple testing: 12 main cells per HC suite + 16 for HFC. Pre-commitment §2.1 + one-tailed.
- Correlated specifications within a table: 4 FE steps not independent replication; documented.
- Alternative OPSW log-DV: future work, Appendix D placeholder.

### §IV — Additional Analyses

**§4.1 Drivers of CEO Speech Uncertainty (reverse direction)**

Establishes: the CEO speech uncertainty IV responds to exogenous uncertainty shocks. Validates construct.
- Table 4: H11 (PRisk firm-level; `\cite{hassan2020}`) + H24 (US EPU; `\cite{bakerbloomdavis2016}`) + H24b (Global EPU; `\cite{davis2016}`).
- DVs: `UncAnsCEO` + `UncPreCEO` (also `UncAnsNoCEO` + `UncPreNoCEO` reported in appendix for contrast).
- Expected: all IVs positive on CEO DVs.
- Currently (pre-rerun): H11 all 12/12 p<0.01 CEO/NoCEO; H24/H24b CEO 2/1/0, Pre-CEO 2/2/2 strongest (per partition synthesis).

**§4.2 Capital Expenditure and Product-Market Competition (exploratory)**

- Table 5: H13 Capex base (12 cols, two-tailed).
- Table 6: H13.1 Capex × z(log TSIMM) (4 cols × contemp + lead = 8 cols, one-tailed explanatory).
- IV: `UncAnsCEO` + `UncPreCEO` for H13; centered forms for H13.1.
- Interpretation: Grenadier 2002 (§2.5 foreshadowed). Post-hoc, NOT pre-specified.
- Candidate optional: H13.2 (4-lead-horizon, 16 cols) if space — likely to appendix.

**§4.3 Outside-World Reaction (candidate table, TBD based on §III results)**

Purpose: show external agents recognize the CEO speech uncertainty signal and react.
- Candidate A: H17 Repurchase Intensity — `UncPreCEO` 3/3/1 contemp + 3/3/3 lead; `UncAnsCEO` 3/1/0 contemp + 3/2/0 lead. Clean Pre signal.
- Candidate B: H14c BGT 25-day Spread — `UncAnsCEO` lead 5/2/0 (market liquidity reaction, thin under QA; Pre 0).
- Selection TBD after §3.2/§3.3 drafted.

### §V — Conclusion

Merged Discussion + Conclusion per DraftTemplate.

- Summary HC + HFC findings + capex exploratory.
- Mechanism disclosure: financing vs investment margins operate through distinct mechanisms; no causal-bridge claim tested.
- Limitations: (a) no identification / endogeneity strategy (flagged FUTURE); (b) Nickell bias O(1/T); (c) CEO speaker ID via Capital IQ metadata has 15% placeholder gap (per `project_speaker_data_empirical`); (d) sample 2002–2018.
- Future research:
  - Identification strategy for endogeneity — candidate instrumental variables (exogenous shocks to CEO communication style).
  - Within-firm cash-then-capex sequencing test.
  - One additional channel beyond Unrated (Unrated is sole alive moderator for cash under CEO; flagged as limitation for now).
  - Structural model combining precautionary motive + competitive real options.
  - OPSW log-DV robustness appendix.

## Suite Allocation Summary v5

| Location | Suites | Count |
|---|---|---|
| **§III Main (HC + HFC)** | H1, H1.2 | 2 |
| **§IV.1 Drivers of speech uncertainty** | H11, H24, H24b | 3 |
| **§IV.2 Capex exploratory** | H13, H13.1 | 2 |
| **§IV.3 Outside-world reaction** | 1 of {H17, H14c} | 1 |
| **§II.3 Validity (compact paragraph; no own table)** | H5 (dispersion), H23 (competition-IV), H25 (GPR null) | 3 |
| **Dropped from thesis entirely** | H4a/H4b (Class C), H1.1/H1.1b (null int), H13.2 (optional), H13.3 (null int), H7/H7b/c/d/e (liq null CEO), H14/H14b/H14d/H14e (spread null CEO), H12/H12b (payout null CEO), H16 (R&D, v4), H18/H18b (CCCL marginal), H19b (weak), H20b (weak), H21 (Class C), H22 (tiny n) | ~20 |

## Targeted Appendix v5

- **Appendix A**: Variable Definitions (exists — `docs/Draft/generate_var_defs_appendix.py`).
- **Appendix B**: Detailed Validity Tables (H11, H24, H24b full tables — body has compact paragraph only).
- **Appendix C**: Robustness specifications (FE-ladder alt, OPSW log-DV robustness, BelowIG row for HFC).
- **Appendix D**: Partition-decomposition auxiliary (`_partition_findings.csv` results summary showing why HL dropped and why cash-only).

## Reference Stack v5 (Tier-1 critical)

| # | Paper | Role | Verbatim status |
|---|---|---|---|
| 1 | `\cite{dzielinski2021}` — DWZ 2021 | LM wordlist + segment split | ✓ `reference_dwz_2021_verified.md` |
| 2 | `\cite{bushee2018}` — BGT 2018 | Pooled aggregation (Ian Gow code) | ✓ `project_bushee_gow_taylor_2018.md` |
| 3 | `\cite{opler1999}` — OPSW 1999 | Precautionary theory | ✓ `reference_opsw_1999_verbatim.md` |
| 4 | `\cite{bates2009}` — BKS 2009 | Cash/assets DV + 2-way cluster | ✓ `reference_bks_2009_verbatim.md` |
| 5 | `\cite{minton2001}` — MW 2001 | "Financial conservatism" | ✓ `reference_minton_wruck_2001_verbatim.md` |
| 6 | `\cite{faulkender2006}` — FP 2006 | Binary rated/unrated; "credit constrained" | ✓ `reference_faulkender_petersen_2006_verbatim.md` |
| 7 | `\cite{grenadier2002}` — Grenadier 2002 | Competitive real options | ✓ `reference_grenadier_2002_verbatim.md` |
| 8 | `\cite{hoberg2016}` — HP 2016 (TSIMM) | Competition moderator | ✓ `reference_hoberg_phillips_2016_verbatim.md` |
| 9 | **[PENDING] CEO-as-face anchor** | CEO partition measurement-choice justification | ⏳ `tmp/ceo_as_face_lit_review.md` |

Tier-2 (citation-only): Aguerrevere 2009 (strategic-equilibrium, §2.5), Hassan et al. 2020 (PRisk), Baker-Bloom-Davis 2016 (US EPU), Davis 2016 (GEPU), Caldara-Iacoviello 2022 (GPR — null result), Amihud 2002 (ILLIQ), Wang 2020 (DISP), Chang-Dasgupta-Hilary 2006 (external fin), L-Z 2012 (CFO measure methodology precedent), Loughran-McDonald 2011/2013 (wordlist + 10-K textual studies), Bertrand-Schoar 2003 (CEO style effects — standing anchor pending CEO-as-face lit search).

## Pre-commitment & convention disclosure

- **Statistical conventions** per §2.1 (repeated here for visibility):
  - HC + HFC: one-tailed positive, pre-specified, BOTH IVs.
  - §IV.2 capex (H13): two-tailed exploratory.
  - §IV.2 capex × competition (H13.1): one-tailed explanatory (Grenadier directional).
- **Sample scope**: Main = 2002–2018 (H1, H4a/b dropped anyway, H13); HFC = 2002–2016 (ratings-truncated).
- **CEO coverage**: ~80.5% vs Mgr-pool ~96% (per `reference_ceo_coverage_gap.md`). Expected ~7% N hit vs `.r` baselines.

## Open items for writing phase

1. **Pending deliverables (parallel background agents)**:
   - `tmp/ceo_as_face_lit_review.md` — Tier-1 CEO-as-face anchor paper(s) + verbatim quotes.
   - `tmp/ceo2iv_rerun_results.md` — H1 + H1.2 2-IV CEO spec reruns. **Block on §3.3**: if `UncAnsCEO_c × Unrated` interaction collapses to NULL under 2-IV CEO, HFC must be restructured.
2. **Contingent structural decisions**:
   - If HFC collapses: §III = HC-only main; Unrated becomes "moderator not robust to CEO partition" in appendix. 1 main analysis instead of 2.
   - If HFC survives weakly (1–2/8 cells): frame as suggestive, caveat.
   - If HFC survives strongly (4+/8 cells): frame as main finding per current plan.
3. **Title decision**: "CEO Speech Uncertainty" changes all memory references + prior-drafted `section_3_main.tex` IV framing. Surgical swap needed.
4. **FUTURE WORK (post first-draft)**:
   - Identification / endogeneity strategy design.
   - One additional channel search (cash-side, under CEO QA — presently only Unrated alive).
   - CEO-as-face full literature survey beyond lit-search agent's initial 3-5 anchors.

## Next Actions (enforced sequence)

1. [DONE] Background agents spawned: lit-search + spec rerun.
2. [THIS UNIT] Skeleton v5 write — this file.
3. [NEXT UNIT] Advisor call on v5.
4. [NEXT UNIT] §3.1 surgical edit (`docs/Draft/sections/section_3_main.tex` lines 1–15).
5. [CHECKPOINT] Await `tmp/ceo2iv_rerun_results.md` — HFC verdict.
6. [UNIT] §3.2 HC draft w/ real 2-IV CEO numbers.
7. [GATE] §3.3 HFC draft if rerun confirms survival; otherwise restructure.
8. [SEQUENCE] §IV → §II → §V → §I → Abstract.

## What stays from v4

- Pipeline data, panels, all_tables.tex renderer.
- Sample + filters (BKS 2009).
- IV construction (DWZ + BGT), extended to CEO partition.
- Three-tier FP constraint extension + BelowIG suppression.
- Tier-2 citation list (mostly unchanged).
- Targeted appendix concept.
- `apacite` bibliography style per `project_apa_bibliography.md`.

## Cross-references

- `project_framing_decision_locked.md` — THE lock (no umbrella, cash wins, capex §IV)
- `project_partition_findings_synthesis.md` — 4-class taxonomy, Class C leverage artifact
- `project_capex_exploratory.md` v4 — capex framing (still valid)
- `project_apa_bibliography.md` — apacite + citation command map
- `reference_*_verbatim.md` — 8 Tier-1 anchor verbatims (CEO-as-face #9 pending)
- `docs/Draft/DraftTemplate.txt` — structural template
- `docs/Draft/REFERENCE_STACK_WALKTHROUGH.md` — 17-paper provenance
- `_partition_findings.csv` — 228-row programmatic extraction (ground truth for all empirical claims)

## Supersedes

- `THESIS_SKELETON.md` v4 (2026-04-16 evening)
- All v4 references to HL / "three formal hypotheses" / `UncAnsMgr` as primary / QA-vs-Pres asymmetry argument.
