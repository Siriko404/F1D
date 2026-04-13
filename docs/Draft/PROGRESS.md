# Thesis Draft — Progress Tracker

**Purpose:** persistent memory for Claude across context compactions. Claude appends/updates this file as work progresses. Read at start of every draft session.

**Current phase:** **Phase 2.5 + Phase 3 tier 1 + tier 2A COMPLETE and COMMITTED** (commits 6a98792, 513b001). Tier 2B/C/D pending: H11, H11-Lag, H20b.
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

## Phase 3 progress

**Clustering downgrades — uniform firm-only rule** — **DONE 2026-04-13** (commit 6a98792 + 513b001):
- [x] 17 runners downgraded: H1, H1.2, H4, H7, H7b, H7c, H7d, H7e, H12b, H13, H13.2, H14, H14b, H14c, H14d, H14e, H16
- [x] All cluster_time args + footnotes + docstrings + prints updated to "firm-level clustered"
- [x] H7d silent NaN SE bug auto-fixed by downgrade
- [x] H14/H14d defensive fallback branches preserved (dead but harmless per advisor)
- [x] `scripts/findings_template.txt` 7 clustering references updated

**Moderation suite FE expansion** — **DONE 2026-04-13** (commit 6a98792):
- [x] H1.1 — 2 → 4 cols (industry + firm + industry_yq + firm_yq; extended controls only). Smoke test passed.
- [x] H1.1b — 2 → 4 cols (same pattern). Smoke test passed.
- [x] H1.2 — 4 → 8 cols (4 unconditional + 4 interaction, each with full FE ladder). Smoke test passed.
- [x] H13.1 — 4 → 8 cols (4 Capex + 4 Capex_lead, each with full FE ladder). Smoke test passed.
- [x] `outputs/generate_all_tables.py` entries updated: cols + col_files + base_iv + dvs mappings

**Directional tailing fixes** — **DONE 2026-04-13** (commit 6a98792):
- [x] H4 → one-tailed β<0 (uncertainty reduces leverage per user). Smoke test passed. FINDING: contemp Leverage cols 1-4 NOT sig at 10% one-tailed; user accepted.
- [x] H23 → one-tailed β>0 (competition increases uncertainty per user). Smoke test passed. Col 1 p_one=0.031 sig.
- [x] H17 silent naming bug fixed: field `_p_one` stored `p_two` values → renamed to `_p_two`. Effective tailing unchanged (still two-tailed per user).
- [x] H13, H16, H20b remain two-tailed per user explicit decision.

**STILL PENDING (tier 2B/C/D)**:
- [ ] **H11 spec ladder expansion** (4 → 8 cols, add firm/industry split). Complexity: H11 loops over 4 DVs × 3 samples (Main/Finance/Utility); only Main appears in thesis table. Has its own `_save_latex_table` function. Need to refactor `run_regression` to accept FE type, double the main loop, and update `generate_all_tables.py` H11 entry (currently maps 4 files; needs 8).
- [ ] **H11-Lag spec ladder** (8 → 16 cols). Same pattern as H11 but for 2 lag variants.
- [ ] **H20b add `ChangDebtChoice_lead` DV** (6 → 12 cols matching H19b). Check if panel has lead column or needs panel-builder extension.

**Deferred to Phase 5 (no code fix)**:
- Sample/methodological notes (H12, H20b, H14 family, H22 — document in limitations).
- Within-family contradictions (H18 vs H21 UncPreMgr sign; H25 GPR wrong-sign QA).

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

1. **Read PROGRESS.md first** — authoritative current state.
2. **Phase 2.5 + tier 1 + tier 2A are DONE and COMMITTED** (6a98792 + 513b001). Do NOT re-run those. Next action is tier 2B/C/D (H11, H11-Lag, H20b) then Phase 4 reruns.
3. **DECISIONS.md §2 and §4 are authoritative** — §2.1.1 shows the 17 runners as [x] done. §2.2 moderation suites as done. §2.3 tailing items: H4/H17/H23 done; H13, H16, H20b kept two-tailed per user.
4. **H1 clustering evidence directory**: `outputs/econometric/h1_cash_holdings/2026-04-13_162202/` — DO NOT DELETE.
5. **Commit risk flag**: `513b001` includes 57 files of prior-session WIP in shared/ and variables/. If Phase 4 reruns break, revert `513b001` and investigate.
6. **H11 refactor entry point**: read `src/f1d/econometric/run_h11_prisk_uncertainty.py` fully first. The `run_regression` function uses `from_formula` with `EntityEffects + TimeEffects`. Add a base_fe dispatch like the moderation suites. Main loop at line 463 iterates `for dv: for sample:`; need to wrap in `for fe in ['firm', 'industry']:`. Filenames become `regression_results_{sample}_{dv}_{fe}.txt`. Update `outputs/generate_all_tables.py` H11 entry at line 295 to map 8 col_files.
7. **H20b entry point**: read `src/f1d/econometric/run_h20b_debt_choice.py` MODEL_SPECS; check panel for `ChangDebtChoice_lead`. If missing, extend the panel builder then rebuild.
8. **Phase 4 command**: `python outputs/generate_all_tables.py` regenerates `outputs/all_tables.tex` + PDFs.
9. **User preferences (active feedback)**: concise by default (`feedback_concise_default.md`), adversarial challenge (CLAUDE.md global rule), audit-first discipline (`feedback_audit_first_no_narrative.md`).

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
- **2026-04-13**: Phase 3 clustering downgrades executed across 17 runners (H1, H1.2, H4, H7, H7b, H7c, H7d, H7e, H12b, H13, H13.2, H14, H14b, H14c, H14d, H14e, H16). All docstrings, print statements, LaTeX footnotes updated to "firm-level clustered". H1 re-smoke-test (`2026-04-13_165454/`) confirmed bit-identical to Phase 2.5 test baseline. scripts/findings_template.txt cleaned. 17 runners compile. DECISIONS.md §2.1.1 marked [x] DONE.
- **2026-04-13**: Phase 3 tier 1 tailing: H17 naming bug fixed (field `_p_one` held `p_two` values; renamed to `_p_two`); H4 flipped to one-tailed β<0 (user: "uncertainty should decrease leverage"); H23 flipped to one-tailed β>0 (user: "higher uncertainty"). H4/H23 smoke-tested; H4 finding: contemp Leverage cols 1-4 NOT sig at 10% under one-tailed (user accepted, said proceed). H13/H16/H20b remain two-tailed per user decision.
- **2026-04-13**: Phase 3 tier 2A moderation FE expansion: H1.1 (2→4), H1.1b (2→4), H1.2 (4→8), H13.1 (4→8). Added firm-FE dispatch branch to each regression function. All smoke tests passed. `outputs/generate_all_tables.py` entries updated for 4 suites. User D1 rule: extended controls only, full FE ladder consistent across all moderation suites.
- **2026-04-13**: Committed `6a98792` (18 files, my session work: Phase 2.5 + Phase 3 tier 1 + tier 2A + DECISIONS.md + PROGRESS.md) and `513b001` (57 files, prior-session WIP batch including H7c/d/e, H14c/d/e, H12b runners from prior audit cleanup; RISK: shared/ + variables/ modules untested). Working tree clean.
- **2026-04-13**: Third compaction prep. Memory + PROGRESS.md + MEMORY.md updated. Tier 2B/C/D (H11, H11-Lag, H20b) explicitly documented as next work with file entry points for post-compaction pickup.
