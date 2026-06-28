# §4.5 ROBUSTNESS-INSERT + FE — RESUME 2026-06-28

## ⛳ NEXT-SESSION ENTRY POINT — read FIRST
The §4.5 robustness subsection is BUILT as a proposal + GATE-passed, but **NOT yet placed into the live thesis**.
Two steps remain, IN ORDER:
1. **PLACE** `_final/_proposals/section4.5_MERGED.json` → real `_final/section4.5_paragraph_ledger.json`
   (a NEW file — safe, nothing overwritten). Re-run the §4.5 PLACEMENT GATE (below) on the placed file.
2. **WIRE** the forward-pointers into the LIVE `_final/section3.2/3.3/3.4` + `section2.4` (P5.2) ledgers.
   ⚠ THIS IS THE FIRST EDIT TO REAL, COMMITTED, AUDITED LEDGERS → own exact-match + GATE + **Sina sign-off**.
   Pointer text: "...holds across all deals (§4.5)"; §2.4 P5.2 gets "...this disclosed threat is answered by §4.5".
Then (later, PROSE phase): write `final_prose` incl. the RATIFIED caveat-2 + the 6 framing drafts (Sina authors load-bearing).

§4.5 PLACEMENT GATE: valid Format-B · 6 props · exact field-order · final_prose="" · numbers==.tex ·
every depends_on resolves in LIVE ledgers · 0 honesty/interp violations · honest meta (no false 74b7a0f8 provenance).

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

## SCRIPTS (session scratchpad — reproducible, NOT cross-session durable)
blast_inventory.py · build_final.py · merge_45.py · sync_fe_props.py · fe_binary.py · fe_data.py ·
render_logit_3col.py · check_fe.py · sync_spec.py · arsenal_probe.py · gen_schema_tree.py.

## BIMODAL still holds
JSON prop statements = MECHANICAL only (number + "survives/holds/n.s."). Interpretive framing (caveat-2, the
FEATURE/answers-P5.2 narrative, the 6 framing sentences) = Sina authors at the PROSE phase. The drafts live in the
two agent reports (this transcript) + the spec. The broader thesis state (16 `_final` ledgers, all `final_prose`
empty, the 17-fix audit) is in `_AUDIT_RESUME_2026-06-27.md`.
