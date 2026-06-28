# ⚠️ NEXT-SESSION REVIEW REQUIRED — Proposition-chain referee AUDIT (2026-06-27)

## ✅ SESSION 2026-06-27 (cont.2) — FINAL-FILE BUILD DONE, read this FIRST
> Supersedes the Q1/Q2 fork in the (cont.) banner below — BOTH RESOLVED.

**Q1 RESOLVED = A (skip normalization):** the only deterministic downstream tool (`push_*_to_tex.py`) reads
ONLY `final_prose`; everything else feeds the prose-WRITER (human/LLM), so the two schemas are fine — no
normalization needed. **Q2 RESOLVED = β (per-section, NOT one merged file):** per-section files are each
single-format (the two-schema headache vanishes), reuse the §2.x pushers, match the retire-old/clone-new model.

**BUILT: 16 prose-ready per-section ledgers in `docs/Thesis/rewrite/_final/`** (`section{X}_paragraph_ledger.json`),
by `scratchpad/build_final.py`, derived from FROZEN `corpus_audited.json` (@74b7a0f8). Surgical strip of EXACTLY
9 audit-only fields (`_provenance · _original_statement · verification · verification_plan · status ·
nlm_query_draft · fetch_target · from_phaseA_prop · fix_summary`); ALL else KEPT incl. audit-named-but-SACRED
(`source · guards_added · number_audit · _phaseC_audit · reason · relation_to_2_1 · anchor_2_1 · depends_on ·
numbers · register_locks · evidence`). **GATE all-pass:** surgical-diff (only the 9 removed, 0 value-changes,
0 adds) · sacred-survival · 16/149/79 counts · prose-empty · refs-resolve · round-trip zero-loss (on-disk
verified). `corpus_audited.json` + the v1 live ledgers (`rewrite/section*.json`) = UNTOUCHED.
Each `_final/` file = self-contained honest substrate: claims (statement/role/type/citations/refs) + per-paragraph
`intent·boundary·thin_claim·guardrails` + 8 global `_bright_lines`; **`final_prose` EMPTY everywhere — ALL prose
to be written FRESH** (NO harvest of v1 prose — Sina: old prose = old argument, would smuggle pre-redesign framing).

**⛳ NEXT (gated on Sina — said "wait for me" after this commit): WRITE FRESH PROSE** into the 16 `_final/`
ledgers, paragraph by paragraph — Sina authors load-bearing claims; Claude drafts + source-anchors + honesty-gates
(BIMODAL CADENCE still holds). **THEN DEFERRED:** build the 11 missing `push_*_to_tex` scripts + reconcile each
pusher's hardcoded bibitems vs the new chains' citations; +2 `\bibitem` (`shleifer_vishny2003`, `louis2004`);
`git mv` the 3 stale ledger-sets (`rewrite/section*`, `_phase3_clones/*`, `_rewrite_working/*`) → `_archive/`
(Sina sign-off); compile + verify.

---

## ✅ SESSION CLOSE 2026-06-27 (cont.) — CURRENT TRUTH, read this FIRST
> Everything below the next divider is EARLIER-layer narrative (some now STALE, e.g. "Nothing is applied" /
> "14 of 17"). THIS banner is the authoritative current state.

**STATE: ALL 17 audit fixes are APPLIED** to `_audit/corpus_audited.json` — one merged file, 16 sections
(`_abstract`,§1,§2.1–2.5,§3.1–3.4,§4.1–4.4,§5), 149 props. Every fix was script-applied by **exact-match +
GATE-verified**; final GATE = **0 suppression flavor (dampen/sits-lower/suppress/below-baseline) in all LIVE
statements** (archival `_original_statement`/`_phaseC_audit` fields may retain traces by design — do NOT panic on a grep hit).
`corpus.json` + the v1 originals = **PRISTINE**. Fully reversible. (The 17 = all of `audit.json`'s findings,
incl. the P3.4/P3.3/P5.5 masking cluster, the DiD scrub, the $1M SDC disclosure, P6.1 dedup.)

**NEW THIS SESSION (post-apply), and where we stopped:**
- **SCHEMA FINDING (verified by `scratchpad/schema_profile.py`):** corpus_audited.json is **TWO merged ledger
  formats** — **Format A** (§2.1–2.5: `paragraphs`=DICT {P1..}, prop-list=`propositions`, `intent`=str,
  fields relation_to_2_1/anchor_2_1/verification_plan/status) vs **Format B** (abstract,§1,§3,§4,§5:
  `paragraphs`=LIST, prop-list=`proposition_chain`, `intent`=dict, fields reason/evidence/numbers/
  register_locks/depends_on). 3 STRUCTURAL diffs + field-presence variance. Uniform everywhere: core prop
  fields (prop_id/statement/role/type/_provenance) + para fields (order/intent/serves/.../final_prose).
  **No prop field has a mixed value-type** (union is type-safe).
- **NORMALIZATION: investigated + planned, then DEFERRED (advisor).** NOT a confirmed bottleneck — prose works
  with both formats (every section has the prose-needed fields). My plan had a **ref-integrity hole**: §2
  paragraphs are referenced by their dict key (`anchor_2_1:['P5']`, callbacks, depends_on), so dict→list could
  silently break refs. Only normalize IF the prose-writer is a strict deterministic tool.

**⛳ THE NEXT DECISION [RESOLVED 2026-06-27 cont.2 — Q1=A, Q2=β, 16 ledgers BUILT; see top banner]:**
```
Q1  prose-writer =  A) by hand / an LLM reading the file  → SKIP normalization
                    B) a deterministic tool needing one schema → normalize first (with the 2 missing
                       safety checks: synthesize para_id=P-key on dict→list; GATE that every
                       anchor/callback/depends_on resolves after)
Q2  propagation  =  clone-forward (corpus_audited.json IS the source) OR regenerate the per-section
                    ledgers from it.  (If B regenerates ledgers, normalizing the merged clone = wasted.)
```

**REMAINING BIG-PLAN (after Q1/Q2):** build the final file (clone corpus_audited.json → strip the audit-only
fields: _provenance/from_phaseA_prop/reason/verification*/​*_audit/_original_statement; keep statement/role/
type/source/register_locks/numbers + paragraph intent/guardrails/final_prose) → **write `final_prose`** (now
empty everywhere) → **+2 `\bibitem`** (`shleifer_vishny2003`, `louis2004`) in `thesis_draft.tex` → **compile+verify**.

**SCRIPTS (session scratchpad — reproducible, NOT cross-session durable):** `apply_11.py` · `apply_2_meta.py` ·
`strip_did.py` · `fix_1m.py` · `apply_p34_cluster.py` · `schema_profile.py` · `capture_p34_findings.py`.

---

> **THE current entry point for the audit layer.** Supersedes nothing in `_PHASE3_RESUME_2026-06-26.md`
> (that doc = the masking PROPOSED-FIXES; this doc = the AUDIT of those fixes + 2 new data-level catches).
> **ALL 17 NOW APPLIED** to `corpus_audited.json` (see SESSION CLOSE banner above); `corpus.json` + originals
> pristine. Treat memory as unverified; the files + `audit.json` + `corpus_audited.json` are truth.

## ONE LINE
We referee-audited the Phase-3 masking proposed-fix proposition chain. **17 findings, each verbatim-verified
+ blast-radius mapped + investigated fix + fix-safety checked.** Deliverable = `audit.json`. NOTHING applied.

> **2026-06-27 (cont.) — P3.4 deep-dive CAPTURED to `audit.json` → `problems[2.2|P3.4].session_findings_2026_06_27_cont` (logic advisor-SIGNED; wording NOT written; nothing applied).** Key results: (A) "is it deliberate?" is a NON-threat — §2.1 P7 keeps both readings open (strategic silence = deliberate), H1 = a timing pattern, mechanism open. (B/C) the masking work splits into 3 objections: A=deliberate→P7 (done) · B=is-it-just-tone-mgmt→P5.6 (now LIGHT: signal is the OPPOSITE direction) · C=why-cash→motive+thewissen(~15%)+C6 (NOT P5.6; the UncPre control is BOTH-arms, can't justify cash). P3.4 is NOT structurally broken (scan: 88/128 ORIGINAL props equally paragraph-grained). NEXT: write P5.6(B)+P3.4(C) to the A/B/C skeleton, then apply.

## ⚙️ APPLY STARTED (2026-06-27 cont.) — `corpus_audited.json`  `[SUPERSEDED — now 17/17; see SESSION CLOSE banner at top]`
**`_audit/corpus_audited.json`** = a CLONE of `corpus.json` (the masking-applied substrate) with **14 of 17 audit fixes applied**, each script-applied by exact-match + GATE-verified (149 props stable, provenance enum clean, depends_on resolves, 0 "DiD" left). `corpus.json` is UNTOUCHED (pristine substrate); fully reversible. Apply scripts in the session scratchpad (`apply_11.py`, `apply_2_meta.py`, `strip_did.py`, `fix_1m.py`).
- **+ `2.1|P6.1`** (Sina-ratified reword: thewissen back-reference, cite key intact, no fresh re-intro) · **`3.1|sample-selection`** (added the ONE undisclosed filter — "$1 million" deal-value floor — to 3.1-PARA1-a's SDC item, PLAIN text not LaTeX; verified the other 9 filters already disclosed via the matched call-panel + "first ≥50%-cash" event def, so re-stating them = redundant; Filters.txt NOT cited).
- **`2.2|P3.4` CLUSTER — DONE (Sina-ratified, advisor-vetted, GATE-clean).** Applied as 4 coherent moves: P3.2 unchanged (the managed-comparison contrast) · **P3.3 reverted** (dropped the added no-suppression clause — it was a circular patch for P3.4's "dampens"; now moot) · **P3.4 rewritten** ("Because the stock arm is a managed comparison (P3.2), a pre-deal signal there is entangled with documented management -- a competing story the cash setting lacks; the masking asymmetry therefore motivates H1a's direction, the run-up concentrating in cash. Motivation for the prediction's direction, not detection.") · **P5.5 reframed** ("why stock sits lower" → "why the run-up concentrates in cash"). FINAL GATE: **0 suppression flavor (dampen/sits-lower/suppress/below-baseline) in ANY statement.** `2.1|P4.2` = no action (watch-item).
- **✅ ALL 17 APPLIED to `corpus_audited.json` (149 props, every GATE clean).**

## ⚠️ TRUE STATE — 17/17 ≠ thesis done
`corpus_audited.json` is a **CLONE** (masking-applied substrate + the 17 audit fixes). NOT the thesis. Downstream remaining (NEXT SESSION):
1. **Propagate to the REAL section ledgers** — the masking `_proposed_fixes` are STILL not applied to the live `_phase3_clones/section*.json` chains; corpus_audited.json holds masking+audit together but the real ledgers don't. Decide: regenerate ledgers from corpus_audited.json, or apply both layers to the ledgers directly.
2. **Regenerate `final_prose`** for every changed paragraph (currently stripped/empty).
3. **+2 `\bibitem`** (`shleifer_vishny2003`, `louis2004`) in `thesis_draft.tex`.
4. **Compile + verify** the draft.
- **APPLIED (12, all GATE-verified):** `1-P7-a` · `4.2-PARA4-a` · `1-P9-a` · `4.2-PARA2-a` · `5-P5-a` · `2.2-P5.2` (statement swaps) · `1-P7-b` (provenance: 5 props ORIGINAL-locked→ADDED, meta→123/11/7/8) · `5-P3-c` (statement) · `2.4|DiD-label` (scrubbed all 3 "DiD" at source — spine/lit_body→"main run-up", thin_claim→"not an identification design") · `4.4-PARA1-a` (depends_on→['3.3-PARA3-a']) · `4.2-PARA1-a` (depends_on prose→IDs: '2.3:P2.2', 3.2-PARA2-a) · `3.1-PARA1-a` (source-count own-labels four→five; statement already five).
- **REMAINING (4 prose-bearing — need FRESH session + USER authorship, NOT tonight):** `2.1|P6.1` (dedupe thewissen → back-reference) · `3.1|sample-selection` (SDC disclosure, MAJOR, code-verified content, needs placement) · `2.2|P3.4` + coupled `2.1|P5.5` (THE supervisor-answer cluster — Sina authors the claim, I verify + anchor).
- **NO ACTION:** `2.1|P4.2` (watch-item).
- **BIMODAL CADENCE (locked, advisor):** internal/zero-prose fixes → apply on GATE authority, show after-diff. Prose-bearing fixes → Sina authors the claim in his words, I verify + source-anchor + honesty-floor-check (drift enters when I author). Mechanical = script exact-match only, never hand-typed.

## THE DELIVERABLE — read this first
`F1D-phase3/docs/Thesis/rewrite/_audit/audit.json`
- `problems[]` (17): each has `locus`, `severity`, verbatim `issue`, `evidence`, `proposed_fix{action,from,to,why,honesty_floor,evidence_ok}`, and `deep_analysis{verified, blast_radius, agents_missed, fix_safe, status, ...}`.
- `meta.signoff` = the calibrated advisor sign-off (below). `meta.conclusion`, `meta.lesson_internalized`.

## ⚠️ DECISIONS PENDING (this is the review flag)  `[SUPERSEDED — all resolved + applied; see SESSION CLOSE banner at top. The ONLY open decision now is Q1/Q2 in that banner.]`
1. **P3.4 → SINA MUST RATIFY.** It's THE prop answering the supervisor's "cash motivation not justified."
   Reformulated 4× (v1 dampens→suppression ✗ · v2 hidden comparative ✗ · v3 Q&A-cleaner ✗ ·
   **v4 SETTING-level: cash setting is management-free → run-up there is clean; NO Q&A comparative; gap is
   empirical C6**). v4 is in `audit.json` (locus `2.2|P3.4`). Judgment call — ratify or adjust the framing.
2. **Spine-vs-DATA sweep — DO or DEFER?** 15 of 17 findings are spine-INTERNAL (claims vs each other).
   Only 2 are spine-vs-DATA (claims vs code/tables) — and BOTH came from Sina, not the panel. The ONE data
   area sampled (SDC filters) hit **~100%**: 1 major + 4 `Filters.txt` discrepancies. So the data dimension
   is barely explored and high-yield. **Decide: bounded data sweep first, or apply now + sweep later.**
3. **Then:** apply ratified fixes → regenerate `final_prose` → +2 `\bibitem` (shleifer_vishny2003, louis2004)
   → compile.

## THE 17 AT A GLANCE — 0 critical · 5 major · 12 minor
**Majors:**
- `2.2|P3.4` masking motivation (v4 → ratify) — was the only "critical-contested"
- `1|1-P7-a` "three contributions" but four enumerated → "four"
- `1|1-P9-a` roadmap omits delivered §4.2/4.3/4.4
- `4.2|4.2-PARA4-a` null→"cannot be artifact/identification" OVERCLAIM — **8 sites** (L4,5,6,219,220,229,232,244), not 1
- `3.1|sample-selection` **(NEW, user-flagged)** SDC sample filters undisclosed; `Filters.txt` inaccurate (below)

**Minors (12):** §2.1 P5.5 "sits lower", §2.1 P6.1 thewissen dup, §1 1-P7-b provenance mislabel (5 drift props
tagged ORIGINAL-locked), §3.1 source-count (=FIVE), §4.2 PARA2 number, §4.2 PARA1 dangling depends_on,
§5 5-P5-a "so" couples 2 open whys, §5 5-P3-c "holds" overstates 4.3, §2.2 P5.2 "rejected"→4.1 register,
§2.1 P4.2 DWZ-decomposition thin span (NO ACTION; watch if referee probes the measure),
`2.4|DiD-label` **(NEW, user-flagged)** guard.

## VERIFIED GROUND-TRUTH (do NOT re-derive — confirmed this session)
- **Honesty-floor numbers — MATCH the tables:** cash **+0.0461\*\*\*** & stock **−0.0429** (`docs/Draft/_empire_building_did.tex:13`);
  C6 Wald **0.0983\*\*** & cause **0.0064** (`docs/Draft/_empire_cashspec.tex:18`). [F1D tree]
- **NO DiD in the thesis (Sina was right).** `thesis_draft.tex:94` = "within-firm, two-way fixed-effects regression."
  "DiD" lives only in §2.4 planning notes + code/table names + the disclaimer. Guard added so prose-regen can't introduce it.
- **SDC actual applied filters (code-verified, `scripts/gen_empire_did_table.py:97-128`):** 2002–2018 · US **ACQUIRERS**
  (not targets) · public acquirers · deal-status {Completed,Pending,Withdrawn} · payment-known · ≥50% cash/stock arm ·
  **$1M minimum** (parquet) · ≥1 transcript · first deal per firm · fin/util excluded via the main firm-sample match.
- **`Filters.txt` is INACCURATE — do NOT disclose from it:** #9 says "US targets" but code filters US acquirers;
  #2/#3 (control thresholds) NOT applied (no SDC field); #4/#5 (asset/self-tender) NOT applied; #6 reinterpreted.
- **§3.1 source count = FIVE** (Execucomp is a real primary source: `comp_execucomp.parquet` → CEO FE via `build_tenure_map.py`).

## CALIBRATED SIGN-OFF (advisor, NOT blanket-100%)
SIGNED: the spine-INTERNAL audit is complete + sound (17 verified, spine holds, no finding broken, no data touched,
honesty-floor + US-targets checks passed). NOT signed: (1) P3.4 → Sina ratify; (2) spine-vs-data barely sampled
(high-yield) → a bounded next pass is warranted. Claiming "100% on everything" would be the verified≠asserted reflex again.

## LESSON (recurred ~4× this session — internalize)
Every verdict needs BOTH "did I remove the error?" AND "is the replacement correct/complete/canonical/**applied**?"
**Absence-of-error ≠ presence-of-correctness.** And: the referee panel is BLIND to spine-vs-data (it had only the
proposition spine, not the code/tables/parquets) — that whole dimension needs code/data access.

## HOW WE GOT HERE (brief)
STEP-0 corpus (`build_corpus.py` → `corpus.json`, GATE-0 PASS, fixes applied to a throwaway copy) → smoke (1 overclaim
auditor, caught P3.4) → 2 referee panels (6 dimension auditors + 2 redteams each; EACH panel lost ONE redteam to API
"stalled mid-stream" — output-size, not concurrency) → union both + smoke (`audit_union.json`, 15 loci) → per-locus
adjudication was attempted (15 agents, killed as token-wasteful — verdicts were already on disk) → **deterministic
Python merge → `audit.json`** → manual per-finding deep-dive (read verbatim · verify exists · blast-radius grep ·
advisor on fix-safety) → 2 NEW user-flagged data catches (SDC $1M; DiD label).

## DURABLE FILES (all under `F1D-phase3/docs/Thesis/rewrite/_audit/`)
- `audit.json` — THE deliverable (17 findings + fixes + deep_analysis + sign-off)
- `AUDIT_SPEC.md` — the audit design
- `corpus.json` + `build_corpus.py` — the fixes-applied corpus + GATE-0 (rebuildable)
- `audit_run1.json`, `audit_run2.json`, `smoke_overclaim.json`, `audit_union.json` — raw audit data
- (workflow scripts live in the session dir `.claude/.../workflows/scripts/` — NOT cross-session durable, but reproducible)

## HARD RULES
- NOTHING applied. Clones + originals pristine. P3.4 needs Sina's ratify before apply.
- Disclose only CODE-VERIFIED sample filters, NEVER `Filters.txt` (it overstates).
- Honesty floor intact: motivation-not-mechanism · no stock-suppressed · S-V/Louis = earnings not tone · two whys stay open.
