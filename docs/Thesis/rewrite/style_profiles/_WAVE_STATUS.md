# Phase-1 style analysis — WAVE STATUS (compaction-safe)  2026-06-24

## Harness patches applied (template: `docs/Thesis/rewrite/style_phase1_pilot.js`; master: `style_phase1_master.js`)
- **DESCRIBE-ONLY**: panels removed `aim` field; forbidden from proposing rewords or claiming "same meaning". (Kills the litotes-style meaning-leak class.)
- **guardrail_collision** boolean added to schema; findings near a paragraph's declared guardrails get flagged for mandatory human review (not dropped).
- Redteam: rejects any reword/equivalence finding; prefers keeping debatable merges SEPARATE.
- **TOOL_LOCK (2026-06-24, after wave-1 abstract redteam idle-timeout):** ALL agents (panel + redteam) forbidden from advisor / web / Read / bash — ONLY StructuredOutput, ONE turn. Root cause: abstract redteam called `Read` on project files → stream idle timeout → null → crashed the type. Panels also wandered (intro/panel-1 made 42 tool calls).
- **null-guard:** a redteam returning null now degrades to raw gate-clean findings instead of crashing the whole type.

## KEY REFRAME (advisor-confirmed)
- Phase-1 produces **NOTES, not prose** → nothing it writes touches the thesis → **meaning-leak is a Phase-2 risk, not Phase-1.**
- "describe-only" still leaves equivalence judgments in the `gap` field (a1-f4 gap says "says the same thing") — HARMLESS now (it's a note).
- **Real safety lives in Phase-2 rewrite**: human sees 100% of diffs + mechanical check that every `number_audit` value + guardrail string survives verbatim.
- **Guardrail-completeness pass = Phase-2 PREREQUISITE** (current guardrails are concept-notes, not exact protected strings; "not informationally empty" is NOT in U1/U3 guardrails).

## Wave plan (user: "3 runs, 2 2 3"; checkpoint between waves)
| Wave | Types | Runnable | Status |
|---|---|---|---|
| pilot | lit_review | (done) | ✅ profile saved: `lit_review_profile.json` (+ `lit_review_RAW_digest.md`) |
| 1a | intro | (done) | ✅ saved `intro_profile.json` (14 findings, 7 guardrail-flagged) |
| 1b | abstract | resume `wf_411aba26-748` | 🟡 RE-RUNNING under TOOL_LOCK (orig redteam timed out), task `ww14pn1i3` |
| 1a | abstract | (done) | ✅ saved `abstract_profile.json` (15 findings, 8 guardrail-flagged) — re-ran clean under TOOL_LOCK |
| 2 | hypotheses, data | `tmp/run_wave_hypotheses-data.js` | ✅ done + reproducibility-checked (run-2 richer; saved hyp 23 / data 20) |
| 3a | methods, conclusion | `tmp/run_wave_methods-conclusion.js` | 🟡 RUNNING — task `wua8lpi67` / run `wf_fde9fe40-9dc` |
| 3b | results | `tmp/run_wave_results.js` | ✅ done — 32 findings, 18 guardrail-flagged, 7 gate-rejected (run `wf_1ada80a2-6b9`) |

## ✅ PHASE 1 (ANALYSIS) COMPLETE — 2026-06-24 — all 8 profiles in `style_profiles/`
| type | findings | type | findings |
|---|---|---|---|
| lit_review | 18 | data | 20 |
| abstract | 15 | methods | 18 |
| intro | 14 | conclusion | 17 |
| hypotheses | 23 | results | 32 |
Total = 157 style findings. Each = aspect + ≥2 exemplar quotes (≥2 papers) + ≥1 our_quote, all verbatim-gated, redteam-merged, describe-only (no reword/no equivalence claim) + `guardrail_collision` flag.

> ✅ **SCHEMA UNIFIED (2026-06-24):** all 8 profiles are describe-only + carry `guardrail_collision` — verified `grep`: 0 with `aim`, 0 missing the flag. lit_review was re-run under the locked master (`wf_57e48372-712`, 18 findings) to replace the stale original-pilot profile; the old pre-patch version is kept as `_lit_review_profile_OLDSCHEMA.json` for reference.

### Phase-2 prerequisites (carry forward — NOT started)
- **Number-survival gate (load-bearing):** results has 14/32 findings touching real numbers; 6 have guardrail_flag=FALSE → the collision flag MISSES numbers. Phase-2 rewrite must mechanically verify every `number_audit` value + guardrail string survives, scanning ALL findings not just flagged ones.
- **Guardrail-completeness pass** (human-ratified) before guardrails can auto-gate — current guardrails are concept-notes, not exact protected strings.
- **Spine frozen:** propositions/guardrails/number_audit unchanged; only sentence wording editable. No thesis-prose edit without Sina's ratification.
- Phase 2 (rewrite) design = LATER.

Reproducibility check (2026-06-24): wave 2 re-run identical mechanics (408k tok, 8 tool calls, ~2min) + theme overlap hyp 7/8, data 5/6. Harness trustworthy; finding COUNT varies (LLM stochastic) but no theme lost. TOOL_LOCK cut tool calls 84→8 (the 17x speedup = killing Read/web round-trips, not shorted work; per-agent tokens 40-67k = real).

## Logit tests (supervisor Ask 3) — CONCLUDED 2026-06-24: CASH HOLDS
Script `tmp/logit_cash_gate.py` → `tmp/logit_cash_gate_results.json`. Regressor = z(UncResCEO) at e=−1, all-deals stacked, cluster firm, LPM primary.
- **Test A** (UncRes → deal next qtr): AME +0.27pp, p=0.001 → ✅ supports.
- **Test B** (UncRes → cash vs stock): AME +1.9pp, p=0.02 (robust to controls + logit) → ✅ supports. Stock N=124 (underpowered but came out sig).
- **Persistent channel** (ClarityCEO): null → it's the TRANSIENT uncertainty spike, not chronic CEO style.
- Caveat: effect modest (~2pp on 89% cash base); CI sits below the pre-set 5pp SESOI. Significant but small.
- **Decision: do NOT drop cash, do NOT retitle.** Logits = supporting evidence; continuous event study (Table 5.5) stays the backbone.
- Event-study-style (binarized) logit: advisor said SKIP (binarizing only loses power vs an already-won continuous result; a weak result would be uninterpretable). Optional outlier-robustness only.

## On each wave completion
1. Read result `{wave, results:[{type, profile, guardrail_collisions, side_notes, gate_rejected, ...}]}`.
2. Persist each `type`'s full result verbatim → `docs/Thesis/rewrite/style_profiles/<type>_profile.json`.
3. Eyeball gate_rejected + guardrail_collisions; confirm harness sane.
4. If sane → fire next staged wave: `Workflow({scriptPath: tmp/run_wave_<...>.js})`.

## Standing constraints (carry across compaction)
- Phase-1 = ANALYSIS only. NO thesis-prose edit without Sina's ratification.
- All agents programmatic / no free-authored prose. Redteam verifies+merges, never adds.
- Build/embed scripts: `tmp/build_master.py`, `tmp/embed_master.py` (regen any wave deterministically).
