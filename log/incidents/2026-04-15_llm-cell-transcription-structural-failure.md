# Lessons Learned: LLM Cell Transcription Produces Structurally Inevitable Errors

**Date:** 2026-04-15
**Severity:** High
**Status:** Open — fix proposed, implementation pending user decision

## Incident Summary

**What happened:** After completing the full 37/37 Phase 5 audit cataloguing layer, 4 parallel red-team agents independently audited all 37 suite records in `DECISIONS.md §4.2` against the raw `outputs/all_tables.tex` source. Found **13 HIGH severity factual errors** + 5 MEDIUM + 4 LOW across the 37 suites. Every HIGH error is a cell-transcription mistake: sig count miscounts, fabricated values (copy-paste from adjacent columns/suites), non-existent column references, and cell-to-FE-strata misattributions.

**When:** 2026-04-15 (red-team audit session, post Q1-Q4 audit completion)

**Impact:** 13 factual errors in the thesis audit record. Any of these would mislead a committee reader relying on the §4.2 cell catalogue. The errors span all Q-clusters (Q1: 5 HIGH, Q2: 5 HIGH, Q3-mid: 3 HIGH, Q3-late: 0 HIGH, Q4: TBD pending respin).

**Resolution:** Not yet resolved. User proposed architectural fix: eliminate LLM cell transcription entirely, replace with programmatic extraction from spec JSON files.

**Time to resolution:** Ongoing.

## Timeline

| Step | Action | Actor | Outcome |
|------|--------|-------|---------|
| 1 | Phase 5 audit — 37 suites catalogued into DECISIONS.md §4.2 under rule 24 full-row format | Claude | 37 §4.2 blocks written, each containing hand-transcribed cell values for every IV + control + Lagged_DV + R²/N |
| 2 | Rule 24 added 2026-04-15 requiring full-row cataloguing (every variable in the table, not just IVs) | User + Claude | Scope of transcription expanded from ~20 cells/suite (IVs only) to ~120 cells/suite (full row catalogue) |
| 3 | Advisor reviews during audit | Claude advisor | Caught 1 fabrication (H23 Lagged_DV copy-paste from H24). Spot-checked IV counts. Did NOT systematically verify control sig counts. |
| 4 | User ordered 4 parallel adversarial red-team agents | User | 4 sonnet agents each tasked with manual cell-by-cell verification of assigned suites against raw LaTeX |
| 5 | Red-team results returned | Red-team agents | 13 HIGH + 5 MEDIUM + 4 LOW errors found |
| 6 | User questioned entire approach: "how about removing decisions file and use the latex file directly?" | User | Identified that the intermediate file IS the error source |
| 7 | Claude proposed stripping cell-copying, keeping interpretive layer | Claude | User pushed back: "we cannot have hallucination risk, which LLMs reading from the latex file is obviously an issue" |
| 8 | Claude proposed programmatic extraction from spec JSON | Claude | Pending user decision |

## Root Cause (5 Whys)

1. Why were there 13 factual errors in DECISIONS.md?
   → Because an LLM hand-transcribed ~4,000 cells from LaTeX into markdown text.

2. Why did the LLM hand-transcribe 4,000 cells?
   → Because rule 24 (full-row cataloguing) required every variable row in every table to be catalogued in §4.2.

3. Why did rule 24 require full-row cataloguing?
   → Because a prior incident (2026-04-15 q1-controls-uncatalogued) showed that cataloguing only IVs missed control-behavior patterns needed for synthesis.

4. Why was hand-transcription the implementation of "cataloguing"?
   → Because the audit rules (rule 6: read-tool-linear only, no Grep, no automation) combined with the §4.2 block format assumed that "reading" = "re-typing into a record". No distinction was made between "the LLM reads and understands" vs "the LLM re-types values into a durable file".

5. Why was no distinction made?
   → **Because the process treated LLM text generation as a reliable transcription channel.** LLMs are good at understanding patterns in data but BAD at faithful character-level reproduction of numeric values. The process conflated "audit comprehension" (which the LLM did well — verdicts, arguments, cross-cutting patterns are all sound) with "cell transcription" (which the LLM does poorly — 0.3% error rate on individual cells, compounding to 35% suite error rate).

**Root cause:** The audit process used an LLM as a transcription tool for numeric cell values, when LLMs are structurally unreliable for exact numeric reproduction. The error is architectural, not behavioral — no amount of "be more careful" or additional rules fixes a ~0.3% per-cell hallucination rate at 4,000-cell scale.

## Contributing Factors

| Category | Factor | Contribution |
|----------|--------|--------------|
| **Process** | Rule 24 expanded transcription scope 6× (from IVs-only to full-row) without reassessing the transcription channel's reliability | Multiplied the number of cells at risk from ~700 to ~4,000 |
| **Process** | Rule 6 (no Grep, no automation) blocked programmatic verification | Prevented automated cross-checks that would have caught errors earlier |
| **Process** | Advisor reviews spot-checked IVs but not controls | 10 of 13 HIGHs are on CONTROL rows (TobinsQ, CashRatio, sCFO, DailyVola, Capex, DivDummy, Leverage, Lagged_DV), which advisors didn't systematically verify |
| **Technical** | No programmatic validation pipeline for §4.2 claims | Even a simple script reading spec JSONs could have caught every error instantly |
| **Context** | "5 at a time" batch cadence + context compactions | Later batches had less working memory of earlier cell patterns, increasing copy-paste risk |
| **Human** | Overconfidence from advisor "zero errors found" stamps | Created false assurance that the transcription was clean |

## Error Taxonomy

| Error type | Count | Examples |
|---|---|---|
| **Sig count overcount** | 7 | H1 TobinsQ 11→9, H4a TobinsQ 9→7, H12 TobinsQ 12→9, H13.1 CashRatio 5→6, H13.1 sCFO 6→7, H13.1 DailyVola 8→7, H7e Capex 10→9 |
| **Value fabrication** (copy from adjacent column/suite) | 3 | H7b Lagged_DV "0.39" from R² column, H13.2 Lagged_DV "0.625" from H13.1, H1 DailyVola col 6 fabricated as sig |
| **Non-existent column reference** | 1 | H1.2 "cols 3, 5" when table has only 4 cols |
| **Cell-to-column misattribution** | 2 | H14b DivDummy col 5 cited as sig (null in LaTeX), H14c StockPrice header vs cell mismatch |

**Systematic pattern**: TobinsQ sig was consistently overcounted in firm-FE lead columns (cols 8, 10, 12) across H1/H4a/H12. The LLM appears to have over-applied "TobinsQ is usually significant" as a prior, producing false-positive sig claims on null cells.

## Fixes — Classification and Implementation

| # | Fix | Type | Location | Status |
|---|---|---|---|---|
| 1 | **Eliminate LLM cell transcription from §4.2.** Replace rule-24 full-row cell catalogue with programmatic extraction from spec JSON files. Script reads machine-generated coefficients/p-values, computes sig counts, outputs machine-verified summary. | Technical | New script + DECISIONS.md restructure | **Proposed — pending user decision** |
| 2 | **New rule: LLMs must not re-type numeric values from source files into derived records.** If a durable record needs exact cell values, the values must come from a programmatic source (spec JSON, script output), not LLM transcription. LLMs may REFERENCE ("see line 812") but not TRANSCRIBE ("β=0.0002"). | Rule | `feedback_phase5_methodology.md` rule 25 (or new memory file) | **Proposed — pending user decision** |
| 3 | **Keep DECISIONS.md for interpretive layer only.** §1-§3 (philosophy/design) + §4.1 summary table (verdicts, headline patterns) + §4.2 blocks stripped to: DV, N, FE, tail, cluster, reader-Q, argument, verdict, rationale + LaTeX line reference. No cell-value reproduction. §5 cross-cutting observations reference programmatic output. | Documentation | `docs/Draft/DECISIONS.md` restructure | **Proposed — pending user decision** |
| 4 | **Advisor reviews must verify controls, not just IVs.** Prior advisor verification stamps covered IV sig counts but never systematically checked controls — where 10 of 13 HIGHs were. | Process | Advisor prompt improvement | Noted |
| 5 | **Red-team audits before committing transcription-heavy records.** The red-team approach WORKED — it found what advisors missed. But it was run post-hoc, not as a gate. For future transcription-heavy work (if any), red-team before commit. | Process | Workflow change | Noted |

## Prevention

The architectural fix (programmatic extraction) eliminates the entire error class. The LLM never touches cell values in the durable record → zero transcription errors → no need for red-team verification of cell values.

The interpretive layer (verdicts, arguments, §5 patterns) remains LLM-generated but is MUCH less error-prone because it's qualitative judgment, not character-level numeric reproduction. The 13 HIGHs are ALL numeric; zero are interpretive.

## Lessons

1. **LLMs are comprehension tools, not transcription tools.** The audit reading WAS valuable — it produced correct verdicts, sound arguments, and genuine analytical insights (§5 cross-cutting observations). The failure was using the same channel to reproduce exact numeric values. Comprehension and transcription are different capabilities; LLMs excel at one and fail at the other.

2. **Rule 24's intent was correct; its implementation was wrong.** Cataloguing every control was necessary for thorough synthesis. But "cataloguing" should mean "a machine-verified record exists" not "the LLM re-types every number". The intent (completeness) can be satisfied by programmatic means without the transcription liability.

3. **Advisor reviews have blind spots on "boring" rows.** Advisors verified IV cells (the interesting part) and missed control cells (the boring part). Errors cluster in exactly the boring parts. Automated verification has no attention bias.

4. **0.3% cell error rate × 4,000 cells = structural inevitability.** This is not a "be more careful" problem. It's a process architecture problem. The fix is architectural (remove LLM from the transcription chain), not behavioral (add more rules about counting carefully).

5. **Red-team audits work.** The 4-agent parallel adversarial approach found 13 HIGHs that two prior advisor reviews missed. For any future work where LLM output is the record of truth, red-team verification is essential — but the better answer is to not put LLM output in the record of truth for numeric values.

## Verification

**Test scenario:** If fix #1 (programmatic extraction) is implemented, re-run the red-team audit against the programmatic output. The script-generated cell summary should have 0 errors by construction (it reads the same spec JSONs that generated the LaTeX).

**Success criteria:** Red-team finds 0 HIGH errors in the programmatic summary. DECISIONS.md contains zero re-transcribed cell values.

**Review date:** Next session after implementation.
