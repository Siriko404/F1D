# §4.5 ROBUSTNESS-INSERT + FE — RESUME 2026-06-28

## ⛳ NEXT-SESSION ENTRY POINT — read FIRST
§4.5 is now PLACED + WIRED into the live thesis. **PLACE (step 1) DONE `5f831e7c`; WIRE (step 2) DONE `b9c2b83d`.**
- **PLACE**: `section4.5_MERGED.json` → live `_final/section4.5_paragraph_ledger.json` (new file). PLACEMENT GATE 18/18.
  At source, also: inserted the 6 per-prop `reason` fields agents dropped (universal in all 80 live props; build-time
  chain-ordering scaffolding, NOT BIMODAL prose; authored within-chain-ordering register only) + reordered keys to
  canonical Format-B. MERGED == placed byte-identical (single source of truth).
- **WIRE**: appended ONE §4.5 forward-pointer to each target paragraph's `serves` (the audit-safe home — corpus keeps
  cross-refs in scaffolding, never in frozen `statement`s). 8 appends across `section3.2/3.3/3.4` + `section2.4` P5,
  mirroring the §4.5 depends_on back-edges. **7 §3 targets, not 6**: the prior list missed `3.4-PARA4` (the war-chest
  CAUSE, cited by 4.5-PARA3-a as staying 0.0071 n.s.) — wired as cause-stays-open, mechanism-open preserved.
  GATE: every statement byte-identical pre/post, every non-target paragraph untouched, proper §, fully git-reversible.

**What remains, IN ORDER:**
1. **CHAIN RATIFICATION** — §4.5 is still flagged `PROPOSAL` (prose_gate all_supported/unlocked=false). Sina reviews the
   6-prop chain incl. the 6 authored `reason` strings (shown in the PLACE turn) + the 8 serves pointers; then unlock.
2. **PROSE phase** — write `final_prose` for all 79 paras incl. §4.5's 3 paras + the RATIFIED caveat-2 + 6 framing drafts
   (Sina authors load-bearing claims, BIMODAL). The 6 framing drafts live in the agent reports + the spec.
3. **TABLES** — when §4.5 tables enter the thesis, add the `Firm + Year-Qtr FE: Yes` row to 5.2–5.5 (rob PDF omitted it).

§4.5 PLACEMENT GATE (passed 18/18): valid Format-B · 6 props · para+prop key-order == sibling 4.4 · final_prose="" ·
numbers frozen+verified-at-build vs rob_4tables.tex · every depends_on resolves in LIVE ledgers · 0 honesty/interp
violations · honest PROPOSAL meta (no false 74b7a0f8 provenance). Scripts: scratchpad `normalize_place_45.py`, `wire_45.py`.

## WHAT THIS SESSION DID
Place 2 orphaned logit tests + the all-deals robustness tables (in `docs/Thesis/rob_ALL.pdf`) into the thesis.

### Selection + 3-dimension map (Sina-ratified)
rob_ALL.pdf = 8 tables. SELECTED 6 — **all-deals-stacked panel ONLY** (first-deal panels are redundant; they ARE
the existing main thesis tables):
- **RUN-UP**: Table 5.2 (all-deals) + Logit A (uncertainty→deal next q)
- **TIMING**: Table 5.3 (matched, all-deals) + Table 5.4 (placebo by payment, all-deals)
- **CASH-CONC**: Table 5.5 (Wald, all-deals) + Logit B (uncertainty→cash vs stock)
DROPPED: the 4 first-deal panels (redundant) · p5 round-trip · p6 materiality (null interactions).
5.4 placebo → TIMING (its content is the event-study round-trip; the FORMAL cash-vs-stock test is 5.5's Wald).

### FEATURE decision (NOT swap) — settled + measured
First-deal stays the MAIN spec (conservative, clean single-event-per-firm design, no overlapping windows);
all-deals + logits = robustness that SURVIVES + ANSWERS the already-disclosed first-deal threat (§2.4 **P5.2**:
"only the first deal sets the event clock... an assumption, not identification"). Measured cost: swap = ~21 props
touched (+ the locked honesty floor) across abstract/§1/§3/§4/§5; feature = ~5 additive props. Placement = ONE
consolidated §4.5 at the end of the §4 robustness chapter.

### Build (2-agent + mechanical merge)
- Clean insert spec: `rewrite/_robustness_insert_spec.json` (6 objects · numbers VERIFIED vs rob_4tables.tex ·
  register-locks · caveats · framing). FE-synced (carries the ratified caveat-2 in `_fe_addendum_ratified_caveat_2`).
- 2 background general-purpose agents each wrote a Format-B §4.5 clone (`section4.5_agentA.json` / `_agentB.json`).
  They CONVERGED (identical 6 numbers, same 3-paragraph RU/TI/CC structure, both schema-clean).
- MERGED = `section4.5_MERGED.json`: **B = base** (correct "residual UncResCEO" wording); 2 GATE'd patches:
  TI-2 `depends_on` → A's (`3.3-PARA5-a` cash-arm + `3.4-PARA1-a` stock-arm = Table 5.4's real homes);
  honest meta → A's (`_derived_from`="PROPOSAL", prose_gate/prose_status un-ratified). CC-1 KEPT `3.4-PARA4-a`
  (it cites the cause 0.0071). caveat-iii = A's sharper "two-stock-cells-distinct" version (lives in FRAMING, not JSON).

### FE (fixed-effects) addendum — ran it, threaded everywhere
Ran FE-LPM (Firm + Year-Qtr FE, PanelOLS EntityEffects+TimeEffects, firm-clustered) for BOTH binary tests
(`scratchpad/fe_data.py` → `tmp/fe_results.json`):
- **Logit A (deal-next): FE-LPM 0.0078*** (SE .00275, N 39,557).** within-R²=0.003 (≈0, rare 2.84% event)
  → frame as **ROBUST to FE**, NOT "within-firm signal".
- **Logit B (cash/stock): FE-LPM 0.0644 (SE .05076, n.s., N 1,063).** Same sign, loses significance.
  Only **48/563 = 8.5%** of firms make BOTH a cash & a stock deal → too few to identify within-firm.
- **logit-FE INFEASIBLE both** (perfect separation: 59% (A) / 91% (B) of firms have no within-firm outcome variation).
Threaded: (a) `tmp/logit_tables_final.tex` → 3rd "LPM + FE" column + "Firm/Year-Qtr FE: Yes" row + "logit-FE
infeasible" note → recompiled → `rob_ALL.pdf` re-merged (**8pp, BOTH trees**); (b) clone props RU-2/CC-2 synced
(mechanical); (c) spec synced; (d) caveat-2 RATIFIED.
ALSO RESOLVED: the rob TABLES 5.2-5.5 DO carry Firm+Year-Qtr FE (verified: EntityEffects+TimeEffects in all 4
estimators — gen_empire_did_table.py:141, empire_drop_matched:54, empire_drop_test:150, empire_cashspec:91);
the rob PDF merely omitted the FE row. → ACTION when §4.5 tables enter the thesis: add the `Firm FE / Year-Qtr FE: Yes` row.

## HONESTY FLOOR — re-verify vs source before acting; NEVER re-derive blind
- run-up: cash first-deal **+0.0461\*\*\*** / all-deals **0.0391\*\*\*** · stock **−0.0429 / −0.0348 n.s.** = NOISY FLAT NULL
  (NEVER "stock suppressed/dampened"; the gap is CASH RISING).
- cash-spec Wald: first-deal **0.0983\*\* (p.039)** / all-deals **0.1056\*\* (p.013)** · cause **0.0064 / 0.0071 n.s.** = mechanism OPEN.
- FE binary: A **0.0078\*\*\* (within-R² 0.003)** · B **0.0644 n.s. (8.5% dual-arm)** · logit-FE infeasible (59%/91%).
- Logit predictor = **residual UncResCEO** (NOT raw; agent-A's "raw" reading was WRONG — src `logit_fullcontrols_rerun.py:21` RHS=["UncResCEO"]).
- Logit A pools ALL payment types → GENERAL run-up (H1) only, CANNOT separate cash/stock (that is Logit B).
- stock Table-5.4 Drop PRE1−GAP **−0.0585\*** = opposite-direction, NOT a flat-null crack (echoes first-deal −0.0756\*).
- Register: correlational · within-firm (TABLES) / pooled-cross-section (LOGITS) · no-identification ·
  concentration-not-strict-specificity · mechanism-open · supportive-not-definitive.

## ARTIFACTS (durable, committed)
- DELIVERABLE: `_final/_proposals/section4.5_MERGED.json` ← PLACE THIS.
- agent clones: `_final/_proposals/section4.5_agentA.json` + `_agentB.json`.
- spec: `rewrite/_robustness_insert_spec.json` (FE-synced; ratified caveat-2 inside).
- FE numbers: `tmp/fe_results.json`. Logit table source: `tmp/logit_tables_final.tex` (3-col). PDF: `docs/Thesis/rob_ALL.pdf` (8pp).
- main rob-table numbers (Sina trusts the .tex): `F1D/outputs/econometric/firstdeal_robustness/2026-06-23_162451/rob_4tables.tex`.

## CANONICAL REPO + REPRODUCIBILITY (cross-tree — read carefully)
- **Canonical repo = F1D-phase3** (this commit `b8e3748b`, branch `phase4/masking-rewrite-harness`): the
  `_proposals/` clones, `_robustness_insert_spec.json`, both resumes, and the **F1D-phase3 copy** of `rob_ALL.pdf`.
- **F1D repo (SEPARATE working tree — NOT committed by this session)** holds the DATA-side provenance:
  `rob_4tables.tex`, `outputs/econometric/firstdeal_robustness/2026-06-23_162451/`, and the F1D-tree copy of
  `rob_ALL.pdf`. `merge_rob.py` writes rob_ALL.pdf to BOTH trees, but only the phase3 copy is committed here.
  → treat the F1D-side files as potentially dirty/regenerated; re-verify before trusting.
- **FE RECIPE now committed under `F1D-phase3/tmp/`** (reproducible): `fe_data.py` (FE numbers→`fe_results.json`),
  `fe_binary.py`, `check_fe.py` (within-R² + dual-arm), `render_logit_3col.py` (3-col table), `merge_45.py` (the merge),
  `sync_fe_props.py`, `sync_spec.py`. (To re-run FE: `python tmp/fe_data.py`, run from / pointed at the F1D data home.)
- **`rob_ALL.pdf` pages 7-8 VISUALLY VERIFIED**: the 3rd `LPM + FE` column renders + aligns; `Firm/Year-Qtr FE: Yes`
  row present; infeasible-logit note present. ("tables ✓" is a verified claim, not just a page-count.)
- Other scratchpad scripts (blast_inventory · build_final · arsenal_probe · gen_schema_tree) are session-only
  (build_final + gen_schema_tree's OUTPUTS are committed; the scripts are not critical to re-run).

## BIMODAL still holds
JSON prop statements = MECHANICAL only (number + "survives/holds/n.s."). Interpretive framing (caveat-2, the
FEATURE/answers-P5.2 narrative, the 6 framing sentences) = Sina authors at the PROSE phase. The drafts live in the
two agent reports (this transcript) + the spec. The broader thesis state (16 `_final` ledgers, all `final_prose`
empty, the 17-fix audit) is in `_AUDIT_RESUME_2026-06-27.md`.
