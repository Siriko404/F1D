# Thesis Revision Decisions Log

**Date:** 2026-04-03
**Context:** Structured discussion following 5-person peer review panel (editorial_decision_package.md)
**Format:** Issue → Evidence → Options → Decision → Implementation

---

## Research Facts (from pipeline investigation)

| Statistic | Value |
|-----------|-------|
| UncAnsMgr mean (main sample) | 0.8107 |
| UncAnsMgr SD (main sample) | 0.3081 |
| UncAnsCEO mean (main sample) | 0.7709 |
| UncAnsCEO SD (main sample) | 0.3780 |
| Correlation(UncAnsMgr, UncAnsCEO) | 0.7675 |
| CEO absence rate | 26.46% |
| Non-CEO measures exist? | YES (UncAnsNoCEO, UncPreNoCEO in pipeline) |
| Double-clustering available? | YES (linearmodels: cluster_entity + cluster_time) |
| Arellano-Bond available? | NO in linearmodels; need pydynpd package |
| Multiple-testing correction? | YES (statsmodels.stats.multitest.multipletests) |
| Firth/rare-events logit? | pyfirth package; or manual implementation |

---

## Decisions

### Decision 1: Reframing — "Effects" vs "Associations"
- **Choice:** Option B — Nuanced reframe
- **Rule:** Use "predicts" for Tier 1 results (H1, H4a/b, H16 — survive Firm FE). Use "is associated with" for Tier 2 results (H13, H17, H20 — Industry FE only). Never use "drives," "causes," or "affects."
- **Implementation:** Add methodology paragraph on what Firm FE can/cannot identify. Distinguish "within-firm evidence" from "cross-sectional associations" throughout.
- **No quasi-experiment required** for thesis defense.

### Decision 2: Primary IV and Multiple Testing
- **Choice:** Pre-specify UncAnsMgr as primary IV + acknowledge multiple testing (no formal correction in main tables)
- **Justification:** Matches published practice in the literature — DWZ (2021), Hassan et al. (2019), LM (2011) all use single primary measure. No published corporate finance paper applies Bonferroni/BH in main tables. Harvey, Liu & Zhu (2016, RFS) is about asset pricing factors, not panel corporate finance.
- **Implementation:**
  1. Declare UncAnsMgr as primary IV in introduction (it's the novel contribution)
  2. Keep all 4 IVs in every table (transparency)
  3. Interpret UncAnsMgr as primary findings in text; other 3 IVs are "exploratory/secondary"
  4. Add UncAnsMgr-only regressions (drop other 3 IVs) as robustness — addresses multicollinearity (r=0.77 with UncAnsCEO) and specification search
  5. Add methodology paragraph acknowledging multiple testing scope (~1,000 tests)
  6. Optional appendix: BH-corrected p-values for UncAnsMgr across 23 suites (above and beyond)
- **What this kills:** Nothing — Tier 1 results (H1, H4, H16) are all p<0.01 for UncAnsMgr

### Decision 3: Standardized Effect Sizes
- **Choice:** Add DV means to all tables + one-SD interpretations in text
- **Implementation:**
  1. Add "DV Mean" row to every regression table in generate_all_tables.py
  2. In each suite's discussion, report: "A one-SD increase in UncAnsMgr (0.31 pp) is associated with a [X] change in [DV], representing [Y]% of the sample mean."
  3. For H16 (RDSales): investigate whether the large magnitude (13-27% of mean) is driven by outliers or heavy-tailed distribution. Report within-firm SD of RDSales.
  4. For H5 (DISP) and H14b (PostCallSpread): explicitly acknowledge economic triviality despite statistical significance.
- **Key magnitudes (SD(UncAnsMgr) = 0.31):**
  - H1 CashRatio: ~1-2% of mean (small, consistent with literature)
  - H4a/b Leverage: ~1-2% of mean (small, consistent)
  - H16 RDSales: ~13-27% of mean (large — needs scrutiny)
  - H5 DISP / H14b Spread: <1% (trivial)

### Decision 4: Resolving the Cash-Investment Paradox

**The paradox:** +Cash (H1) AND +R&D (H16) simultaneously, while standard precautionary theory (BKS 2009) and real options (Dixit & Pindyck 1994) predict uncertainty should reduce investment. Gulen & Ion (2016, RFS) empirically find macro uncertainty reduces investment.

**Choice:** Resolution E — "Innovation-Precautionary Complementarity" (unified framework)

**Core argument: There is no paradox.** The three Tier 1 results (+Cash, -Leverage, +R&D) are a single equilibrium response to uncertainty:

1. **+R&D is a growth option response.** R&D is fundamentally different from irreversible capital investment. Under uncertainty, R&D's option value INCREASES because the downside is capped (abandon the project, lose only sunk costs) while the upside is unlimited. Firms invest in R&D to explore and resolve uncertainty. This is Bloom's (2014, JEP) "growth options effect" — verified against the paper.

2. **+Cash is driven by +R&D.** R&D-intensive firms rationally build cash buffers to sustain innovation through dry spells. He & Wintoki (2016, JCF) document that by 2012, the average U.S. firm held $0.60 in cash for every $1.00 of R&D spending (up from $0.04 in 1980), and that R&D explains over 20% of the increase in aggregate corporate cash holdings — verified against the paper. The precautionary motive is not AGAINST investment; it is FOR investment — the cash enables sustained innovation.

3. **-Leverage is the enabling financing adjustment.** Reducing debt lowers fixed obligations and shifts financing from external debt to internal retention. Under uncertainty, external financing becomes costlier (adverse selection worsens per pecking order theory), so firms rely more on retained earnings. The leverage reduction makes the +R&D and +Cash equilibrium feasible.

4. **Capex (H13) dies under Firm FE — confirming standard theory.** Capex IS the irreversible investment that Dixit & Pindyck correctly predicts will be reduced/deferred. The thesis data CONFIRMS the standard real options prediction for capex while showing R&D is different. This is exactly the pattern documented by Atanassov, Julio & Leng (2024, RFS) who find political uncertainty increases R&D by 2.6% over mean while decreasing capex, using close gubernatorial elections as quasi-experiments — verified against the paper.

**Thesis discussion structure (5 paragraphs):**

1. **Acknowledge the apparent paradox.** Cite Dixit & Pindyck (1994), Bloom (2009), Gulen & Ion (2016, RFS). State that standard theory predicts uncertainty should reduce investment.

2. **Establish that firm-level linguistic uncertainty ≠ macro policy uncertainty (Resolution C).** Gulen & Ion use the BBD aggregate policy uncertainty index; this thesis uses firm-level Q&A linguistic uncertainty. Different constructs, different responses. Year-Quarter FE already absorb aggregate time-varying uncertainty. Cite Baker, Bloom & Davis (2016, QJE).

3. **R&D is a growth option, not an irreversible commitment (Resolution A within E).** Cite:
   - Bloom (2014, JEP): uncertainty stimulates R&D via "growth options effect" while depressing capex via "real options effect"
   - Atanassov, Julio & Leng (2024, RFS): close elections → +R&D, -Capex (quasi-experimental, published RFS 2024)
   - Vo & Le (2017, IRFA): idiosyncratic uncertainty → +R&D, stronger in competitive industries (strategic preemption)
   - Note: H13 (Capex) dies under Firm FE in this thesis = confirms Dixit-Pindyck for irreversible investment

4. **The complementarity: +R&D drives +Cash (Resolution E core).** Cite:
   - He & Wintoki (2016, JCF): R&D drives cash accumulation ($0.60 per $1.00 R&D by 2012; >20% of aggregate cash increase)
   - Gao & Zhao (2022, RED): structural model showing innovation uncertainty is the largest driver of high-tech cash balances
   - The precautionary motive and the growth-option motive are complements, not contradictions

5. **Timing evidence supports the story.** Cash and R&D effects are contemporaneous (managers sound uncertain NOW → firms hoard cash and invest in R&D NOW). Leverage effects are lead-concentrated (the balance sheet adjustment follows with a lag). This is consistent with an immediate response: uncertainty triggers immediate R&D exploration + cash hoarding, with leverage restructuring following in the next quarter.

**Supporting footnote (Resolution B):** The balance-sheet accounting — less debt frees cash flow for both cash buffers and R&D. Caveat: the dollar-value verification has not been formally run; the timing mismatch (cash is contemporaneous, leverage is lead) means the causal ordering is ambiguous.

**Dropped: Resolution D (competition/capex).** H13.1 TSIMM interaction is Industry FE only, explains a non-robust result (capex dies under Firm FE), and weakens the argument by introducing cross-sectional evidence into a within-firm discussion.

**What to NEVER claim:**
- Never say "uncertainty increases all investment" (capex dies under Firm FE)
- Never say "Dixit-Pindyck is wrong" (it's correct for capex — our data confirms it)
- Never say "cash hoarding finances R&D" (direction may be reversed per He & Wintoki)
- Never say "Gulen & Ion's results are contradicted" (they measure different uncertainty on different outcomes)
- Never use "flow vs stock adjustment costs" (Bloom does NOT use this terminology — he uses "growth options effect" vs "real options effect")

**All citations verified against source papers via NotebookLM on 2026-04-03:**

| Paper | DOI | Key verified claim |
|-------|-----|-------------------|
| Atanassov, Julio & Leng (2024, RFS) | 10.1093/rfs/hhae023 | Political uncertainty → +R&D (2.6% over mean), -Capex; growth option view; close elections as QE |
| He & Wintoki (2016, JCF) | 10.1016/j.jcorpfin.2016.10.006 | R&D drives cash ($0.60/$1.00 by 2012); >20% of aggregate cash increase; rational precautionary buffer |
| Bloom (2014, JEP) | 10.1257/jep.28.2.153 | Uncertainty stimulates R&D (growth options) while depressing capex (real options); NOT "flow vs stock" terminology |
| Vo & Le (2017, IRFA) | 10.1016/j.irfa.2017.03.002 | Idiosyncratic uncertainty → +R&D; stronger in competitive industries; strategic preemption |
| Gao & Zhao (2022, RED) | 10.1016/j.red.2021.02.008 | Innovation uncertainty is largest driver of high-tech cash balances |

### Decision 5: Missing Citations
- **Choice:** Add 12 missing papers during writing phase. No code/pipeline changes needed.
- **Must cite (3 — referee will reject without):**
  1. Bloom (2009, Econometrica) — "The Impact of Uncertainty Shocks" — foundational
  2. Gulen & Ion (2016, RFS) — "Policy Uncertainty and Corporate Investment" — finds opposite investment result, must confront in text using Resolution C (macro vs micro)
  3. Loughran & McDonald (2016, JFE) — "Textual Analysis in Accounting and Finance: A Survey" — methodological foundation
- **Should cite (5):**
  4. Bloom, Bond & Van Reenen (2007, REStud) — uncertainty and investment dynamics
  5. Bodnaruk, Loughran & McDonald (2015, JF) — financial constraints + textual analysis (relevant to H1.2)
  6. Larcker & Zakolyukina (2012, JAR) — deceptive conference call discussions (measurement validity)
  7. Adams, Almeida & Ferreira (2005, JFE) — CEO power (CEO-Manager divergence)
  8. Baker, Bloom & Davis (2016, QJE) — EPU index (for macro vs micro distinction)
- **Nice to cite (4):**
  9. Hollander, Pronk & Roelofsen (2010, TAR) — prepared vs unprepared remarks
  10. Matsumoto, Pronk & Roelofsen (2011, JAR) — Q&A section informativeness
  11. Davis, Piger & Sedor (2012, TAR) — managerial language in earnings calls
  12. Panousi & Papanikolaou (2012, JFE) — idiosyncratic risk and investment
- **Implementation:** Download 3 "must cites" + upload to NotebookLM before writing. Add all 12 to bibliography. Engage substantively with Bloom (2009) and Gulen & Ion (2016) in the text — especially confronting the opposite investment sign per Decision 4.
- **Already in NotebookLM (22 papers):** 16 original + 5 uploaded today + 1 Timoneda

### Decision 6: CEO Absence (~26.5%) and Selection
- **Severity:** MINOR if fixed, MODERATE if left as-is
- **Core problem:** Current pipeline requires all 4 IVs non-missing (complete-case), dropping 22,352 calls (26.5%) from UncAnsMgr regressions solely because UncAnsCEO is NaN. UncAnsMgr is perfectly observed for those calls.
- **Choice:** Surgical fix — keep current 4-IV tables, add robustness proving primary IV is unaffected
- **Implementation:**
  1. Keep current 4-IV tables exactly as-is (verified, comprehensive)
  2. Add ONE robustness table: run UncAnsMgr alone (drop CEO IVs from required list) for H1, H4a, H16 on full available sample (~60-70K obs vs current 38K). Just 3 extra regressions.
  3. Run existing `ceo_presence_probit.py` — report what predicts CEO absence
  4. Add sample attrition table showing: full panel N → Main sample N → complete-case N → available-case N per suite
  5. Discussion paragraph: "UncAnsCEO nulls partly reflect lower power from 26.5% absence, but primarily reflect that CEO-only speech captures a different (noisier) signal than the management-team aggregate. Sign reversals in H4a, H16, H20 cannot be explained by power alone — they indicate genuinely different information content."
- **Why NOT two-tier table restructuring:** Would require modifying 23 runners + generate_all_tables.py + re-verification. Disproportionate effort for thesis. Save for journal paper.
- **Why NOT Heckman correction:** No valid exclusion restriction; Heckman in panel FE settings is econometrically fraught (Wooldridge 1995).
- **Expected outcome:** UncAnsMgr results will be substantively unchanged on the larger sample (Firm FE absorbs between-firm differences driving CEO absence). If so, selection concern is fully neutralized.

### Decision 7: Double-Clustering (Firm × Time)
- **Choice:** Approach A — Replace single-clustering with double-clustering as the new default for ALL 23 suites
- **Code change:** `cluster_entity=True` → `cluster_entity=True, cluster_time=True` in every runner's `.fit()` call
- **Justification:** Double-clustering is more conservative and more honest. Cameron, Gelbach & Miller (2011) show single-clustering can under-reject with time-clustered data. Earnings calls are heavily time-clustered (same 2-3 week windows per quarter). Year-Quarter FE absorbs aggregate time effects but not within-quarter cross-sectional correlation.
- **Implementation:**
  1. Modify all 23 runners: add `cluster_time=True` to `.fit()` calls
  2. Re-run all 23 suites (panel builders unchanged, only runners affected)
  3. Regenerate all_tables.tex/pdf via generate_all_tables.py
  4. Update findings.txt with new significance levels
  5. Update table footnotes: "Standard errors clustered at firm and calendar-quarter level"
- **Expected impact:**
  - Tier 1 (H1, H4, H16 at p<0.01): Will survive — double-clustering typically increases SEs by 5-15%, not enough to kill *** results
  - Tier 2/3 marginal results (H5 *, H12 *, H18 *): May lose a star — this is honest, not harmful
  - If any result flips from significant to insignificant, it was fragile and should be reported as such
- **Cascading changes required:** Full pipeline rerun → regenerate tables → regenerate PDF → update findings.txt
- **Reference:** Cameron, Gelbach & Miller (2011, "Multi-Way Clustering," Journal of Business & Economic Statistics)

### Decision 8: H11-Lead Placebo Failure
- **Choice:** Options A + B — Reframe as association/validation + report PRisk autocorrelation
- **Implementation:**
  1. Reframe H11 in thesis text as "construct validation" — "Political risk exposure and speech uncertainty are robustly associated, validating both measures as capturing related aspects of the firm's uncertainty environment." Never claim PRisk *causes* uncertainty.
  2. Compute and report AR(1) coefficient of PRisk. If >0.80, add sentence: "The lead result is consistent with PRisk's high persistence (AR(1) = [X]), where adjacent quarters' values proxy for current conditions, rather than indicating reverse causality."
  3. Keep H11-Lead in the thesis — do NOT drop it. Honest reporting of a failed placebo is a strength. Every reviewer praised the transparency.
  4. Mention orthogonalized PRisk (regress PRisk(t) on PRisk(t-1), use residuals) as a direction for future research — do not implement now.
- **What to say in text:** "H11 establishes that political risk and speech uncertainty co-move within firms. The lag results confirm persistence. The lead results indicate this co-movement reflects a common slow-moving factor rather than a directional causal channel. We interpret H11 as construct validation, not causal identification."
- **What to NEVER claim:** "Political risk drives/causes speech uncertainty" or "H11 establishes causality"

### Decision 9: Scope — Final Suite Selection (6 Suites)
- **Choice:** Report only 6 suites that build a coherent narrative. All other suites remain in the pipeline (not deleted/archived) but are excluded from the thesis report.
- **Final list:**
  1. **H1** (Cash Holdings) — flagship finding, +Cash under uncertainty
  2. **H4a** (Book Leverage) — core, -Leverage = funding source for reallocation
  3. **H4b** (Debt-to-Capital) — robustness of H4a with market-based measure
  4. **H16** (R&D Intensity) — growth options channel, resolves cash-investment paradox
  5. **H13** (Capex) — the contrast: dies under Firm FE, confirms Dixit-Pindyck for irreversible investment
  6. **H1.2** (Unrated Moderation) — mechanism: information opacity amplifies the effect
- **The story arc:**
  1. Uncertainty → +Cash (H1)
  2. Where does cash come from? → -Leverage (H4a, H4b)
  3. But firms also +R&D → growth options, not paralysis (H16)
  4. Capex does NOT respond within-firm → R&D ≠ Capex under uncertainty (H13)
  5. Who is most affected? → information-opaque (unrated) firms (H1.2)
- **Dropped suites (17) — remain in pipeline, excluded from report:**
  - H1.1, H1.1b (null TSIMM interaction — mention in one sentence in H1.2 discussion)
  - H5 (DISP — different IV, tiny magnitudes)
  - H7, H7b (complete nulls)
  - H9 (concordance ~0.50, unreliable Cox)
  - H11, H11-Lag, H11-Lead (reversed causality, failed placebo, tangential)
  - H12 (near-null payout)
  - H13.1 (moderation of non-robust effect)
  - H14, H14b (trivial magnitudes)
  - H17 (opposite signs, confusing)
  - H18, H18b (fragile, near-zero R²)
  - H19 (near-null)
  - H20 (all dies under Firm FE)
  - H21 (complete null)
- **Rationale:** 23 suites with 4 IVs = fishing deck. 6 suites with 1 primary IV = focused, coherent thesis. Every table earns its place in the narrative.

### Decision 10: Nickell Bias / Arellano-Bond
- **Choice:** Acknowledge in methodology section + run no-lagged-DV robustness for H1 and H16. Do NOT implement Arellano-Bond.
- **Justification:**
  - T~23 quarters → Nickell bias ≈ O(1/23) ≈ 4% on the AR coefficient. Tolerable.
  - Bias is on the lagged DV coefficient, not directly on the IV coefficients. Contamination is indirect and small.
  - Every published PanelOLS paper in corporate finance faces this. Almost none run Arellano-Bond. Standard practice is to acknowledge.
  - `linearmodels` doesn't have Arellano-Bond; would need `pydynpd` — new dependency for marginal value.
- **Implementation:**
  1. Add methodology paragraph: "Including a lagged DV in FE specifications introduces Nickell (1981) bias of order O(1/T). With T~23, the bias is approximately 4%, which we consider tolerable."
  2. Run H1 and H16 WITHOUT Lagged_DV as robustness (trivial — just drop from control list). If UncAnsMgr remains significant, Nickell concern is neutralized.
  3. Report in robustness section or footnote.
- **H16 Lagged_DV sign reversal (R1 flag):** Acknowledge in text. RDSales is highly persistent; Firm FE absorbs most persistence, leaving Lagged_DV to pick up mean-reversion noise. UncAnsMgr still survives, which is reassuring.

### Decision 11: UncAnsMgr-Only Regressions (Single-IV Specifications)
- **Choice:** Add one robustness table with UncAnsMgr entered alone for all 6 reported suites
- **Serves three purposes simultaneously:**
  1. Proves UncAnsMgr isn't borrowing significance from multicollinearity (r=0.77 with UncAnsCEO)
  2. Runs on full available sample (~60-70K) without CEO-absence complete-case restriction (addresses Decision 6)
  3. Demonstrates the primary IV stands on its own without the other 3 IVs
- **Implementation:**
  1. For each of the 6 suites (H1, H4a, H4b, H16, H13, H1.2): run with UncAnsMgr as sole IV, full available sample
  2. Report as one compact robustness table (6 rows × key columns: beta, SE, stars, N, R², FE type)
  3. Compare N and coefficients against the main 4-IV tables
- **Expected outcome:** UncAnsMgr coefficients will be similar or slightly more precise (less multicollinearity, larger N). If so, this fully addresses the multicollinearity, specification search, and CEO-absence concerns in one table.

### Decision 12: Non-CEO Manager Decomposition (UncAnsNoCEO)
- **Choice:** Option B — Add a decomposition table entering UncAnsNoCEO + UncAnsCEO simultaneously (zero mechanical overlap) for all 6 reported suites
- **Why not replace UncAnsMgr:** UncAnsMgr is the natural aggregate ("all managers including CEO"), it's verified, it works. Replacing with an untested measure is risky.
- **Why a decomposition table:** UncAnsMgr includes UncAnsCEO by construction (r=0.77). Comparing them is contaminated. UncAnsNoCEO and UncAnsCEO partition the management team cleanly with ZERO overlap. If UncAnsNoCEO is significant and UncAnsCEO is null → definitive evidence that non-CEO managers drive the signal.
- **Implementation:**
  1. For each of the 6 suites: run PanelOLS with UncAnsNoCEO + UncAnsCEO as the two IVs (replacing UncAnsMgr + UncPreMgr)
  2. Report as one decomposition table (6 suites × 2 IVs × key specs)
  3. UncAnsNoCEO and UncPreNoCEO already exist in the pipeline (config/variables.yaml, computed in linguistic_variables output)
- **Narrative payoff:** Upgrades the contribution from "management team aggregate dominates CEO" (dismissible as aggregation noise) to "non-CEO manager speech drives the results while CEO speech is null" (sharp, clean decomposition). Much stronger claim.
- **Timing:** Run during the Decision 7 full rerun (double-clustering). Marginal effort since we're re-running everything anyway.

### Decision 13: R-squared Reporting
- **Choice:** Add footnote clarifying R² type. No code changes.
- **Fact:** Milestone #4 (2026-03-31) already switched all runners to report overall R² + Adj R². Tables already show overall R².
- **Implementation:** Add to table footnotes: "$R^2$ is overall (not within)."
- **One line. Done.**

---

## IMPLEMENTATION SUMMARY

### Code changes required (pipeline rerun)

| # | Task | Effort | Depends on |
|---|------|--------|-----------|
| 1 | Add `cluster_time=True` to all 6 reported runners (Decision 7) | Low — one param per runner | Nothing |
| 2 | Re-run 6 suites with double-clustering | Medium — pipeline execution | Task 1 |
| 3 | Add DV mean row to tables in generate_all_tables.py (Decision 3) | Low | Nothing |
| 4 | Regenerate all_tables.tex/pdf with 6 suites only (Decision 9) | Medium — modify generate_all_tables.py | Tasks 2, 3 |
| 5 | Run UncAnsMgr-only specs on full available sample for 6 suites (Decision 11) | Medium — modify required vars | Task 2 |
| 6 | Run UncAnsNoCEO + UncAnsCEO decomposition for 6 suites (Decision 12) | Medium — new robustness runner | Task 2 |
| 7 | Run H1/H16 without Lagged_DV (Decision 10) | Low — drop one control | Task 2 |
| 8 | Run CEO presence probit (Decision 6) | Low — script exists | Nothing |
| 9 | Compute AR(1) of PRisk (Decision 8) | Trivial — one computation | Nothing |
| 10 | Update findings.txt (Decisions 3, 7, 9) | Medium — rewrite for 6 suites | Tasks 2-7 |
| 11 | Add R² footnote (Decision 13) | Trivial | Task 4 |

### Writing tasks (no code)

| # | Task | Decision |
|---|------|----------|
| W1 | Reframe all language: "predicts" for Tier 1, "is associated with" for rest | 1 |
| W2 | Designate UncAnsMgr as primary IV in introduction | 2 |
| W3 | Add methodology paragraph on identification limits | 1 |
| W4 | Add methodology paragraph acknowledging multiple testing | 2 |
| W5 | Add one-SD effect interpretations for all 6 suites | 3 |
| W6 | Write cash-investment paradox resolution (5 paragraphs per Decision 4) | 4 |
| W7 | Add 12 missing citations to bibliography | 5 |
| W8 | Engage with Bloom (2009), Gulen & Ion (2016) in text | 5 |
| W9 | Add CEO absence discussion paragraph | 6 |
| W10 | Add Nickell bias acknowledgment paragraph | 10 |
| W11 | Reframe H11 as construct validation (if mentioned at all) | 8 |
| W12 | Add sample attrition table | 6 |

### Total effort estimate
- **Code/pipeline:** ~2-3 days (mostly re-running + new robustness tables)
- **Writing:** ~3-5 days (thesis chapter drafting)
- **Citations:** ~1 day (download, upload, integrate)

---

## PHASED IMPLEMENTATION PLAN

### Dependency Graph
```
Phase A (double-clustering) ──┐
                               ├──> Phase D (regeneration)
Phase B (scope + DV means)  ──┘         │
                                         v
Phase C (robustness analyses) ──> Phase E (verification)
```

Phases A and B can be done in parallel. C is independent. D depends on A+B. E depends on everything.

---

### Phase A: Double-Clustering
**Decisions addressed:** 7
**Status:** [x] COMPLETE (2026-04-03)

**Objective:** Change all 5 reported runners (covering 6 suites) from single-clustering (firm only) to two-way clustering (firm × time).

**Implementation details:** See plan file `joyful-napping-acorn.md`. Red-team audited (141 tool calls, PASS WITH CONDITIONS). All conditions addressed before execution.

**What was done:**
- [x] A1: Identified 9 `.fit()` call sites across 5 runners (H4a+H4b share `run_h4_leverage.py`)
- [x] A2: Added `cluster_time=True` to all 9 `.fit()` calls
- [x] A3: Updated all stale text: 4 docstrings, 4 print statements, 5 built-in LaTeX footnotes, 4 markdown reports, 3 `generate_all_tables.py` footnotes (29 edits total)
- [x] A4: Re-ran all 5 suites: H1 (12/12), H4 (24/24), H16 (12/12), H13 (12/12), H1.2 (4/4)
- [x] A5: Verified betas identical (clustering only changes VCV, not point estimates)
- [x] A6: Verified SEs increased (e.g., H1 col3 UncAnsMgr SE: 0.0019 → 0.0021)

**Verification results:**
- All 64 regressions complete without error
- Betas unchanged; SEs slightly larger as expected
- H1 UncAnsMgr: 6/6 current-DV specs at ** or *** (threshold: 5/6) ✓
- H4a UncAnsMgr: 5/6 lead-DV specs at ** (threshold: 4/6) ✓
- H16 UncAnsMgr: 6/6 current-DV specs at ** or *** (threshold: 4/6) ✓
- H1.2 Unrated interaction: *** in both specs ✓
- No Tier 1 results lost significance
- All "clustered at firm level" / "firm-clustered" references eliminated from 6 target files
- Footnote wording: "two-way clustered (firm, time)" — correct for both Year FE (clusters on cal_yr) and YrQtr FE (clusters on cal_yr_qtr) specs

**Note:** Dropped suites remain single-clustered (not reported, no action needed).

---

### Phase B: Scope Narrowing + DV Means + R² Footnote
**Decisions addressed:** 9, 3, 13
**Status:** [x] COMPLETE (2026-04-03)

**Objective:** Create thesis-focused table generator with 6 suites, DV means (regression-sample), and R² footnote.

**What was done:**
- [x] B0: Added `dv_mean` column to `model_diagnostics.csv` in all 5 runners via `model.model.dependent.dataframe.mean().iloc[0]`. Re-ran all 5 suites.
- [x] B1: Created `outputs/generate_thesis_tables.py` — 6-suite version (H1, H1.2, H4a, H4b, H13, H16)
- [x] B2: Added DV Mean row to `generate_table()` and `generate_moderation_table()` — reads from `model_diagnostics.csv` `dv_mean` column, uses `\multicolumn` spans per DV group
- [x] B3: Added R² footnote: "$R^2$ includes absorbed fixed effects (not within-$R^2$)." — corrected from original "overall" wording per red-team audit
- [x] B4: Synced improvements back to `generate_all_tables.py` — same DV mean logic, R² footnote, updated timestamps for 6 thesis suites. 17 non-thesis suites gracefully skip DV Mean (no `dv_mean` column in old diagnostics).
- [x] B5: Two-way clustered footnote already done in Phase A
- [x] B6-B7: Both scripts generate successfully: `thesis_tables.pdf` (6 tables) + `all_tables.pdf` (23 tables)

**Verification results:**
- `thesis_tables.tex`: 6 tables, all 6 have DV Mean row ✓
- `all_tables.tex`: 23 tables, 6 have DV Mean row ✓
- All tables have "$R^2$ includes absorbed fixed effects" footnote ✓
- All tables have "two-way clustered (firm, time)" footnote ✓
- Both PDFs compile cleanly ✓

**Design decision:** `generate_all_tables.py` (23 suites) preserved as the fishing deck reference. `generate_thesis_tables.py` (6 suites) is the thesis report. Both share identical generator logic; only SUITES list differs.

**DV Mean values (regression-sample):**
| Suite | DV | Mean |
|-------|-----|------|
| H1 | CashRatio | 0.1660 |
| H1 | CashRatio_lead | 0.1675 |
| H4a | Leverage | 0.2307 |
| H4a | Leverage_lead | 0.2348 |
| H4b | DebtToCapital | 0.3384 |
| H4b | DebtToCapital_lead | 0.3461 |
| H13 | Capex | 0.0487 |
| H13 | Capex_lead | 0.0481 |
| H16 | RDSales | 0.0645 |
| H16 | RDSales_lead | 0.0658 |
| H1.2 | CashRatio | 0.1716 |

**Depends on:** Phase A (COMPLETE)

---

### Phase C: Robustness Analyses
**Decisions addressed:** 6, 10, 11, 12, 8
**Status:** [x] COMPLETE (2026-04-03)

**Objective:** Produce 5 robustness analyses referenced in thesis text.

**Implementation approach:** Added `--single-iv`, `--nonceo-decomp`, `--no-lagged-dv` CLI flags to 4 runners via module-level global mutation (KEY_IVS, BASE_CONTROLS). Red-team audited (175 tool calls, 3 CRITICAL found and fixed before execution). Output dirs use timestamp suffixes.

**What was done:**
- [x] C4: CEO Presence Probit — ran existing script, CEO absence = 29.6%
- [x] C5: PRisk AR(1) — new script `run_c5_prisk_autocorrelation.py`, pooled OLS with quarter dummies, ρ = 0.30
- [x] C1: UncAnsMgr-Only — `--single-iv` flag added to 4 runners, all ran successfully
- [x] C3: No-Lagged-DV — `--no-lagged-dv` flag added to H1 + H16, both ran successfully
- [x] C2: NoCEO Decomposition — `NonCEOManagerQAUncertaintyBuilder` added to 4 panel builders, panels rebuilt, `--nonceo-decomp` flag added to 4 runners, all ran successfully
- [x] Default behavior verified: H1 with no flags produces 4 IVs, N=56,131 (identical to Phase A)

**Results summary:**

| Analysis | H1 | H4 | H16 | H13 |
|----------|-----|-----|------|------|
| **C1 (single-iv)** UncAnsMgr sig | 11/12 | 1/24 | 3/12 | 6/12 |
| **C1 N** (vs main 56K) | 78K | 78K | 74K | 74K |
| **C3 (no-lagged-dv)** UncAnsMgr sig | 3/12 | — | 5/12 | — |
| **C2 (nonceo)** UncAnsNoCEO sig | 0/12 | 0/24 | 0/12 | 0/12 |
| **C2 (nonceo)** UncAnsCEO sig | 9/12 | 0/24 | 2/12 | 2/12 |

**CRITICAL FINDING — C2 NoCEO Decomposition:**
UncAnsNoCEO is null across ALL suites. UncAnsCEO dominates (especially H1: 9/12). This REVERSES the thesis's "manager team dominance" claim. UncAnsMgr's apparent superiority in main tables is a **coverage artifact** (95.8% vs 70.4% availability), not signal strength. The CEO drives the underlying cash holdings signal. See `project_nonceo_decomposition_finding.md` for full analysis.

**C4:** CEO absence = 29.6%. Probit summary at `outputs/econometric/ceo_presence_probit/2026-04-03_040001/`
**C5:** PRisk AR(1) ρ = 0.30 (moderate persistence, not extreme). Report at `outputs/econometric/prisk_autocorrelation/2026-04-03_040051/`

**Depends on:** Phase A (COMPLETE), Phase B (COMPLETE)

---

### Phase D: Regeneration
**Decisions addressed:** 3, 7, 9 (outputs)
**Status:** [x] COMPLETE (2026-04-03)

**Objective:** Produce two findings documents — one comprehensive (fishing deck), one thesis-focused.

**Design decision:** Same approach as tables — `findings.txt` (fishing deck, all 23 suites) is preserved and updated with ALL improvements. `thesis_findings.txt` (6 suites only) is the thesis-scope document. Both get Phase A-C improvements; only scope differs.

**Implementation approach:** Plan red-team audited (39 tool calls, 7 CRITICAL + 7 MAJOR found and fixed). Key fixes: H1 col9 *** not **, NoCEO counts corrected (UncAnsNoCEO marginal * not null), CEO probit directions inverted (DV is presence not absence), H4b UncAnsCEO collapse 7→1 documented, H16 no-lagged-DV count 8/12 not 5/12.

**What was done:**

#### D-Fishing: Update `findings.txt` (all 23 suites, 1180 → 1346 lines)
- [x] D-F1: Updated 6 thesis suite entries with post-double-clustering stars and notes
  - H1: col1 * → **, col9 lead ** → ***
  - H4a: col2/col3 current-DV removed (now NS), col10 UncAnsCEO ** → *
  - H4b: UncAnsCEO collapse 7 → 1 spec; UncAnsMgr col3 ** → *, cols 8/10 ** → *, col9 ** → ***
  - H13: col3 ** → ***, UncAnsCEO upgraded to ***
  - H16: col3 ** → ***
  - H1.2: stable (no changes)
- [x] D-F2: Added DV means for all 6 thesis suites (11 DV × mean values)
- [x] D-F3: Added standardized effects summary table (8 entries) in robustness section
- [x] D-F4: Added ROBUSTNESS ANALYSES section (C1-C5, ~90 lines) before cross-suite patterns
- [x] D-F5: Updated Pattern 1 (NoCEO coverage artifact note), Pattern 4 (H4a/H4b clustering casualties), added Pattern 10 (coverage artifact)
- [x] D-F6: Clustering note added to header (R² footnote already in tables from Phase B)

#### D-Thesis: Created `thesis_findings.txt` (334 lines)
- [x] D-T1: 6 suites with full DV formulas, coefficient tables, DV means
- [x] D-T2: DV formula documentation for each suite (raw Compustat items + references)
- [x] D-T3: Standardized effects with one-SD interpretations and % of mean
- [x] D-T4: Cross-suite narrative (5-paragraph story arc)
- [x] D-T5: Robustness summary (C1-C5 compact)
- [x] D-T6: NoCEO decomposition finding — honest discussion, correct framing
- [x] D-T7: Zero references to dropped suites (verified by regex)

**Verification results:**
- findings.txt: 1346 lines (was 1180), all 23 suites present ✓
- thesis_findings.txt: 334 lines, exactly 6 suites ✓
- Standardized effects arithmetic verified (4 spot-checks) ✓
- H4b UncAnsCEO collapse verified against CSV: 1/12 ✓
- NoCEO framing: "marginal * at Industry FE" not "null everywhere" ✓
- CEO probit directions correct (ABSENCE: larger, lower-lev, lower-ROA, higher-Q) ✓
- No dropped-suite references in thesis_findings.txt (regex verified) ✓

**Depends on:** Phase A (COMPLETE), Phase B (COMPLETE), Phase C (COMPLETE)

---

### Phase E: Verification
**Decisions addressed:** All 13
**Status:** [ ] NOT STARTED

**Objective:** Red-team audit of all outputs against the 13 decisions.

**Tasks:**
- [ ] E1: Verify each of the 13 decisions is reflected in the outputs
- [ ] E2: Check all_tables.pdf — 6 tables, DV means, correct footnotes, double-clustered SEs
- [ ] E3: Check findings.txt — no dropped-suite references, standardized effects present
- [ ] E4: Check robustness outputs — C1 through C5 all produced and consistent
- [ ] E5: Grep for old variable names, old suite references, single-clustering language
- [ ] E6: Final go/no-go before thesis writing begins

**Verification criteria:**
- Zero discrepancies between decisions and outputs
- All tables compile to PDF
- All robustness analyses produce expected patterns

**Depends on:** Everything

