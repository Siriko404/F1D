# Thesis Draft — Progress Tracker

**Purpose:** persistent memory for Claude across context compactions. Claude appends/updates this file as work progresses. Read at start of every draft session.

**Current phase:** **Phases 2 and 2.5 COMPLETE.** Clustering methodology committed: uniform firm-only + macro exception. Phase 3 ready.
**Last updated:** 2026-04-13

---

## Protocol (5 rules — DO NOT VIOLATE DURING AUDIT)

1. **Reporting ≠ interpreting.** Cell facts only. NO labels like "channel", "mechanism", "noise", "staging", "persistent style", "2×2".
2. **Contradictions logged, never rescued.** If Pre/CEO findings contradict the directional prediction, log the contradiction. Do NOT build sub-narratives to rescue the framework.
3. **FE-rule frozen.** Set once upfront (see DECISIONS.md §1.2.1 — this section is structural, not narrative, stays valid). Do not revisit per family.
4. **No writes to DECISIONS.md §1.2 / §2 / §3 / §5.1 during audit.** Those sections are narrative-polluted from pre-reset work. Ignore as authoritative; clean at Phase 5. Audit writes only to §10 (audit table) and §11 (raw findings catalogue — create on first Phase 2 resume session).
5. **Advisor calls at phase boundaries only**, not mid-family. Mid-review advisor calls caused the rebuild loop.

---

## Workflow phases

- [x] **Phase 1** — Diagnose + protocol (2026-04-13)
- [x] **Phase 2** — Suite audit with discipline (COMPLETE 2026-04-13)
- [x] **Phase 2.5** — Clustering methodology decision (COMPLETE 2026-04-13 — uniform firm-only + macro exception, empirical H1 test confirmed direction)
- [ ] **Phase 3** — Apply all pipeline fixes
- [ ] **Phase 4** — Rerun affected suites + regenerate tables
- [ ] **Phase 5** — Clean read of post-fix data + synthesize narrative on blank slate

---

## Phase 2 progress — family audit

**Completed (pre-reset, audit facts usable; interpretive labels in §5.1 polluted, ignore):**
- [x] H1 family (H1, H1.1, H1.1b, H1.2)
- [x] H4 family (H4a, H4b)
- [x] H12 family (H12, H12b)
- [x] H17 (repurchase intensity)
- [x] H13 family + H16 (H13, H13.1, H13.2, H16)

**Remaining (process in order):**
- [x] H19b, H20b — audited 2026-04-13 (raw catalogue §4, 5 new audit entries in §3, 2 new clustering bugs in §2.1, 1 new tailing inconsistency in §2.3, 1 new sample note in §2.4, 1 new structural gap in §2.5)
- [x] H5 — audited 2026-04-13 (raw catalogue §4, 1 new clustering bug §2.1 `run_h5b_wang_disp.py:263, 268`)
- [x] H11, H11-Lag — audited 2026-04-13 (raw catalogue §4, 2 new clustering bugs, 1 new spec-ladder gap)
- [x] H23 — audited 2026-04-13 (raw catalogue §4, 1 new clustering bug `run_h23:287, 292`, 1 new two-tailed entry)
- [x] H24, H24b, H25 — audited 2026-04-13 (raw catalogue §4; two-way clustering verified OK; no bugs; H25 mostly null with wrong-sign QA cells)
- [x] H7 family (H7, H7b, H7c, H7d, H7e) — audited 2026-04-13 (raw catalogue §4; two-way clustering OK for all 5 runners; sparse scattered signals; H7d has silent NaN SE bug — needs Phase 3 fix)
- [x] H14 family (H14, H14b, H14c, H14d, H14e) — audited 2026-04-13 (raw catalogue §4; two-way clustering OK for all; H14/H14d have defensive fallback; mostly null signals in 3-day DVs, sparse in 25-day)
- [x] H18, H18b, H21 — audited 2026-04-13 (raw catalogue §4; 3 new clustering bugs; H18 vs H21 UncPreMgr sign contradiction flagged)
- [x] H22 — audited 2026-04-13 (raw catalogue §4; 1 new clustering bug `run_h22:282, 287`; 1 new structural gap; smallest N in panel at 8,621)

---

## Phase 2 — COMPLETE (2026-04-13)

All 14 remaining families audited. Full bug inventory and raw cell facts in DECISIONS.md §2 (bugs) and §4 (catalogue).

---

## Phase 2.5 — CLUSTERING METHODOLOGY DECISION (COMPLETE 2026-04-13)

**Decision**: Uniform firm-only clustering across all suites EXCEPT H24/H24b/H25 macro (which keep two-way firm × `cal_yr_qtr`). See DECISIONS.md §2.1 for full rule + empirical evidence + Phase 3 action lists.

**H1 empirical test result (summary)**: Firm-only SEs are 0.5%–27.1% LARGER than two-way across 12 specs (baseline `outputs/econometric/h1_cash_holdings/2026-04-09_232352/` vs firm-only test `outputs/econometric/h1_cash_holdings/2026-04-13_162202/`). All 6 significant contemp UncAnsMgr results survive; col 9 (Ind+lead+ext) weakens from p=.009 to p=.032 but remains significant at 5% one-tailed.

**Interpretation**: The advisor's >10% threshold was a concern about the switch *loosening* SEs (false-positive risk). The actual result is the opposite — firm-only is MORE conservative. CGM 2011 decomposition `Var_two-way = Var_firm + Var_time − Var_White` implies `Var_time < Var_White` — consistent with the 17-annual-cluster panel sitting below Thompson (2011)'s ~25–40 floor for two-way. Firm-only eliminates this small-T instability.

**Phase 3 clustering action lists (see DECISIONS.md §2.1)**:
- §2.1.1 — downgrade 16 currently-two-way non-macro runners (H1, H1.2, H4, H7/b/c/d/e, H12b, H13, H13.2, H14/b/c/d/e, H16) to firm-only; also update each runner's footnote string.
- §2.1.2 — 13 already-correct firm-only runners reclassified as NO ACTION (H5b, H11, H11-Lag, H12, H13.1, H17, H18, H18b, H19b, H20b, H21, H22, H23).
- §2.1.3 — 3 macro runners (H24, H24b, H25) keep two-way. NO ACTION.
- §2.1.4 — H7d silent NaN SE bug fixed automatically by the §2.1.1 downgrade (rank-deficient two-way VCV eliminated).
- §2.1.5 — H14/H14d defensive fallback becomes dead code. NO ACTION — leave in place.

**Evidence preserved**: `outputs/econometric/h1_cash_holdings/2026-04-13_162202/` — DO NOT DELETE.

**Phase 5 write-up line**: *"We cluster standard errors at the firm level following Petersen (2009), who shows firm-level clustering is sufficient when time fixed effects are included. For macro-uncertainty specifications where the independent variable varies at the aggregate time level, we additionally cluster by calendar quarter."*

---

## Verified Phase 3 bugs

**Clustering downgrades — uniform firm-only rule** (see DECISIONS.md §2.1.1 for full list + line numbers):
- [ ] 16 currently-two-way non-macro runners: H1, H1.2, H4, H7, H7b, H7c, H7d, H7e, H12b, H13, H13.2, H14, H14b, H14c, H14d, H14e, H16
- [ ] For each: switch `cluster_time=True` → `cluster_time=False` AND update runner footnote string ("two-way clustered" → "firm-level clustered")
- [ ] H7d is part of this batch and automatically fixes the silent NaN SE bug (see §2.1.4)
- [ ] Leave H14/H14d defensive fallback code in place — becomes dead but harmless (see §2.1.5)

**Missing firm-FE specs on moderation suites** (add firm-FE cols for spec-ladder consistency):
- [ ] H1.1 (TSIMM continuous × cash)
- [ ] H1.1b (TSIMM binary × cash)
- [ ] H1.2 (rating × cash)
- [ ] H13.1 (TSIMM × capex)

**Missing spec ladder** (only 4/8 cols; single FE spec):
- [ ] H11 / H11-Lag — expand to spec ladder or document as deliberate
- [ ] H22 — 4 cols, no YrQtr variant (small N=8.6k may justify)

**Missing lead DV variant** (unilateral 6-col suite):
- [ ] H20b (vs H19b which has 12 cols / 2 DVs)
- [ ] H18 (CCCL receipt; single DV; H21 is the count variant but different DV entirely)

**Directional test convention (two-tailed on directional hypotheses):**
- [ ] H4a, H4b — leverage direction negative
- [ ] H13, H13.1, H13.2 — capex direction positive
- [ ] H17 — repurchase intensity
- [ ] H19b vs H20b — within-family tailing inconsistency (H19b one-tailed β<0, H20b two-tailed)
- [ ] H20b — two-tailed while directional
- [ ] H23 — two-tailed while reverse-direction with directional expectation
- (user decision pending: per-IV vs uniform one-tailed; H1 already per-IV one-tailed for IVs only)

**Sample / methodological notes (document in Phase 5, no code fix):**
- [ ] H12 sample selection: DV NaN when `ibq ≤ 0`; N=45k vs H12b N=64k
- [ ] H12 low R² (0.079 cross-sectional / 0.015 firm-FE) from noisy quarterly payout DV
- [ ] H20b N=13k vs H19b N=65k (reason unverified — flag for investigation)
- [ ] H14/H14c/H14d/H14e: extended-controls cols drop from N=64k to N=44k (~20k loss from AbsSurpDec/StockPrice/DailyVola/Turnover)
- [ ] H22 smallest N=8,621 (Hoberg-Maksimovic firm-year)

**Within-family data contradictions (flag for Phase 5 interpretation, no code fix):**
- [ ] H18 vs H21: UncPreMgr +0.0017\* in H18 (CCCL indicator LPM) vs −0.018 (wrong-sign, not sig) in H21 (SEC letter count fwd). Same base panel.
- [ ] H25 (GPR): mostly null, QA cells show wrong-sign point estimates in both FE specs.

---

## Session-resume notes (for post-compaction pickup)

1. **Read PROGRESS.md first** — authoritative current state
2. **Phases 2 and 2.5 are COMPLETE.** Do NOT re-audit families. Do NOT re-run the H1 clustering test. Next action is Phase 3 (pipeline fixes).
3. **DECISIONS.md §2 and §4 are authoritative** — §2.1 now encodes the uniform firm-only + macro exception rule with full empirical H1 evidence (delta table + CGM 2011 decomposition). §4 has raw cell facts for all 14 post-reset families plus pre-reset rounds. §1.3 FE-selection rule is structural, stays valid.
4. **H1 clustering evidence directory**: `outputs/econometric/h1_cash_holdings/2026-04-13_162202/` — DO NOT DELETE. This is the empirical basis for the Phase 2.5 decision.
5. **Phase 3 entry point**: DECISIONS.md §2.1.1 has the 16-runner clustering downgrade list with line numbers. Start there. §2.2–§2.5 have the non-clustering Phase 3 work (moderation FE specs, spec ladder, directional tailing, sample notes).
6. **Pipeline source verified for these runners** (14 post-reset families all done + the pre-reset ones): H1, H4, H5, H7, H7b-e, H11, H11-Lag, H12, H12b, H13, H13.1, H13.2, H14, H14b-e, H16, H17, H18, H18b, H19b, H20b, H21, H22, H23, H24, H24b, H25. All audited for clustering + FE spec + tailing + cell facts.
7. **Files to reference**:
   - `docs/Draft/PROGRESS.md` — current workflow state (this file)
   - `docs/Draft/DECISIONS.md` — bug inventory (§2), audit table (§3), raw cell catalogue (§4)
   - `draft.tex` — IGNORE (pre-reset placeholder skeleton; Phase 5 rewrite)
8. **Memory entries that stay valid**: `feedback_audit_first_no_narrative.md` (the 5-rule discipline), `feedback_ceo_noisy_mgr_central.md` (secondary-measure rule), `feedback_pres_is_presentation.md`, `feedback_macro_iv_handling.md`, `project_notebooklm_papers.md`, `reference_paper_search_mcp.md`. Pre-reset narrative framings in `project_duong_2024_buyback_staging.md` and `project_grenadier_2002_competitive_real_options.md` are IGNORED for now — Phase 5 decision.

---

## Update log

- **2026-04-13**: File created. Phase 1 complete. Ready to resume Phase 2 with first new family audit (H19b/H20b).
- **2026-04-13**: H19b/H20b audited. DECISIONS.md cleaned to 80 lines (old polluted sections removed). §4 raw catalogue created. 2 new clustering bugs verified in source (H19b, H20b firm-only). H19b vs H20b tailing convention inconsistency flagged. H20b structural gap flagged (no lead DV variant, N=13k).
- **2026-04-13**: H5 audited. Clustering bug verified (`run_h5b_wang_disp.py:263, 268` firm-only). UncPreMgr significant in all 12 cells including all 6 firm-FE; UncAnsMgr significant in 6/6 Ind-FE cells, 0/6 firm-FE; CEO measures all null. N=20k. One-tailed β>0 for IVs. Raw facts in §4.
- **2026-04-13**: First compaction prep: memory consolidation performed (1 deleted, 2 rewritten, 2 created, MEMORY.md updated).
- **2026-04-13**: Post-compaction resume. H11 audited (2 clustering bugs, 1 spec-ladder gap). H23 audited (1 clustering bug, 1 two-tailed entry). H24/H24b/H25 audited (two-way clustering OK for macro via other_effects+cal_yr_qtr). H7 family audited (2-way OK for all 5 runners; H7d has silent NaN SE bug). H14 family audited (2-way OK; H14/H14d have defensive fallback with disclosed columns). H18/H18b/H21 audited (3 new clustering bugs; H18 vs H21 UncPreMgr sign contradiction). H22 audited (1 clustering bug, firm-year with smallest N=8.6k). Phase 2 COMPLETE.
- **2026-04-13**: Investigated empty SE cells in H7d. Root cause: NaN SEs from rank-deficient two-way VCV for CEO IVs in Ind-FE cols 1/3 and Capex col 6. No cluster fallback in source (unlike H14/H14d which disclose). Fix: downgrade to firm-only.
- **2026-04-13**: Clustering methodology reconsideration. User raised whether two-way clustering is universally appropriate given time FE inclusion. Advisor (second opinion) confirmed direction: uniform firm-only defensible via Petersen (2009); keep macro-IV two-way exception; verify H1 empirically before committing. Phase 2.5 milestone added to workflow. DECISIONS.md §2.1 NOT yet updated — awaiting H1 test. §2.1 remains authoritative as conservative fallback.
- **2026-04-13**: Second compaction prep: memory consolidation methodical update (PROGRESS.md Phase 2.5 added, project_draft_playing_it_safe.md rewritten).
- **2026-04-13**: Phase 2.5 COMPLETE. H1 empirical test run (`outputs/econometric/h1_cash_holdings/2026-04-13_162202/`). Result: firm-only SEs are 0.5%–27.1% LARGER than two-way across 12 specs; all 6 significant contemp UncAnsMgr cells survive; col 9 weakens from p=.009 to p=.032 but remains sig at 5% one-tailed. Direction is CONSERVATIVE (firm-only tightens inference, not loosens). Advisor confirmed: proceed with commit. DECISIONS.md §2.1 fully rewritten — uniform firm-only + macro exception rule, delta table preserved, 16-runner Phase 3 downgrade list in §2.1.1, 13 already-correct firm-only runners reclassified in §2.1.2, 3 macro runners in §2.1.3, H7d NaN fix subsumed in §2.1.4, H14/H14d fallback becomes dead code in §2.1.5. PROGRESS.md updated accordingly. Phase 3 ready.
