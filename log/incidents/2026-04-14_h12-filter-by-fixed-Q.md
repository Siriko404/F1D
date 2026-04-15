# Lessons Learned: H12 DROP-by-Filter on Provisional Q1

**Date:** 2026-04-14
**Severity:** High — misread discipline intent on first post-compaction suite; would have DROPped informative empirical pattern from the audit record.
**Status:** Resolved — revised verdict to KEEP mixed-pattern, rule 21 added to `feedback_phase5_methodology.md`.

---

## Incident Summary

During the H12 dialogue (step iii), I catalogued cells for all 4 IVs × 12 columns, found UncAnsMgr 0/12 sig and UncPreMgr 6/12 sig β<0 *industry-FE only*, and issued a **DROP** verdict with rationale "primary null, secondary answers wrong Q". I also described UncAnsMgr's null lead cells as "6/6 wrong-signed" — that framing is itself a discipline failure (rule 22, added 2026-04-15) because null cell signs are noise, not signal. The user immediately corrected the Q-as-filter framing: *"we have not yet decided on Q1 and no other Qs! Q1 and others will be shaped by what we have! so you must consider, audit, discuss and record all IVs, all FEs, and all DVs to make sure we have the complete picture of our empirical findings"* — and then separately corrected the wrong-sign framing: *"null coefficient signs doesnt matter, as they literally are more noise than signal"*.

My DROP was grounded in §1.3 DECISIONS.md Q1 wording ("within-firm association with contemporaneous corporate financial state") treated as a locked filter. H12's cross-sectional-only UncPreMgr pattern didn't match "within-firm" literally, so I issued DROP. The user's correction is that the Q wording is PROVISIONAL and the audit must catalogue the complete empirical pattern without Q-as-filter — because the Q will be shaped by the pattern, not the reverse.

Had the user not caught this, H12 would have been recorded as DROP with a rationale that filtered out a real finding (cross-sectional scripted-language payout association) because it didn't match an unfinalized Q framing.

---

## Timeline

| Turn | Action | Actor | Outcome |
|---|---|---|---|
| T0 | Post-compaction, user says "i want you to do the next 3 suites results" | User | Task begins: H12, H12b, H13 sequentially |
| T1 | I challenge: rule 3 per-suite dialogue vs batch. User: "go!" | User | Default sequential |
| T2 | I read 4 remaining canonical docs (DECISIONS.md, philosophy, ceo-noisy-mgr, audit-first) | Claude | Pre-audit reads done |
| T3 | I scan `all_tables.tex` forward with parallel Read, locate H12 at line 973, H12b at 1037, H13 at 1103 | Claude | Cells acquired |
| T4 | I report H12 cells (all 4 IVs) and argue for DROP: "primary 0/12 null; UncPreMgr industry-FE only = cross-sectional, doesn't answer Q1 as written (within-firm)" | Claude | **Filter-by-fixed-Q failure planted** |
| T5 | User pushback: "mgrpres significant! consider ALL 4 measures!" | User | I interpret this as "you're hand-waving PreMgr" |
| T6 | I double down: I DID show PreMgr, but it's ind-FE only which is §5.2 cross-sectional flag, doesn't answer within-firm Q1. Still DROP. | Claude | Wrong — I was defending the filter, not the pattern |
| T7 | User hard correction: "Q1 and other Qs will be shaped by what we have! consider, audit, record all IVs/FEs/DVs for complete picture" | User | Filter-failure surfaced |
| T8 | I accept, re-catalogue H12 with complete 4×12 matrix, revised loose verdict KEEP mixed-pattern | Claude | Recovery |
| T9 | User invokes /research-lessons-learned | User | This retro begins |

**Trigger:** DECISIONS.md §1.3 Q1 wording was written in full prose at the H1 boundary ("within-firm association with contemporaneous financial state"), and the per-suite record shape §4.2 requires naming a reader-Q + arguing cells answer it. When H12 cells did not match the Q1 prose literally, I reached for DROP.

**Point of no return:** T4 when I wrote "UncPreMgr industry-FE only = cross-sectional, doesn't answer within-firm Q1" in the argument block. Before that, I was reporting cells. After that, I was filtering them through the unfinalized Q.

---

## Root Cause (5 Whys)

1. **Why did I issue DROP on H12 when informative empirical findings were present?**
   → Because I filtered cells through "Q1 = within-firm association with financial conservatism" and H12's cross-sectional UncPreMgr pattern didn't match that framing literally.

2. **Why did I filter cells through a specific Q1 framing during audit?**
   → Because DECISIONS.md §1.3 contains a Q1 wording and the philosophy requires naming a reader-Q + arguing cells answer it in step (iii). I treated §1.3 Q1 prose as the audit target.

3. **Why did I treat provisional Q1 wording as a fixed audit target?**
   → Because the philosophy's "name Q + argue cells answer it" process, when the Q is treated as fixed, functions as a rubric — the exact failure mode the philosophy doc explicitly warned against ("rubrics produce mechanical verdicts that collapse"). I didn't internalize that Q-wording during audit is *shaped by data*, not filtering it.

4. **Why didn't I internalize "Q is shaped by data" during audit?**
   → Because the audit-first principle (data first, narrative last) and the "name a Q + argue" process are in tension: the Q is a narrative object; naming one pre-commits a narrative framing. No explicit rule said "during audit, provisional Q wording is a recording-target placeholder, not a cells filter". The process gap was implicit.

5. **Why was the process gap implicit?**
   → Because rules 16-20 in `feedback_phase5_methodology.md` covered tool-usage, writing shape, verbosity, and durability. None addressed the semantic role of the provisional Q during per-suite dialogue. The philosophy doc phrased it ("Q is provisional, shaped post-audit") but the operational rule set didn't encode a guard against filtering cells through it.

**Root cause:** Provisional reader-Q wording during audit functions as a de facto rubric when no explicit rule frames it as a placeholder. The philosophy's "name Q + argue cells answer it" step gates verdicts on Q-answering, which collapses into Q-as-filter unless an operational rule forbids it.

---

## Contributing Factors

| Category | Factor | Contribution |
|---|---|---|
| Process | No rule distinguishing "name Q as placeholder" from "test cells against fixed Q" during step (iii) | Primary mechanism of the failure |
| Process | H1/H4a/H4b §4.2 rationales used "Q1 (provisional)" labels — I read these as "Q1 is the audit target" not "Q1 is the current placeholder" | Primed me to treat Q1 as locked |
| Communication | DECISIONS.md §1.3 Q1 wording is full prose with "within-firm" baked in, not flagged as provisional in the wording itself | Easy to read as locked |
| Context | First suite post-compaction, narrative-discipline-lock context was in the summary but not salient | Lost the "shaped post-audit" nuance |
| Human | Pattern-matching to H1/H4a/H4b KEEP rationales ("cells answer Q1") without re-asking "is Q1 actually locked?" | Reflexive reuse of prior-suite scaffold |
| Technical | No pre-dialogue guard checking "am I about to treat a provisional Q as a filter?" | Nothing interrupted the DROP draft |

---

## Fixes Implemented

| Fix | Type | Location | Status |
|---|---|---|---|
| **Rule 21 — Provisional Q is a placeholder, not a filter.** During step (iii), the named Q is a working hypothesis, not a locked target. Cells are catalogued in full across all 4 IVs × FE ladders × DVs. DROP is reserved for suites where NO informative pattern exists across ANY IV/FE combo. KEEP is the default when any informative pattern exists — including primary-null + secondary-sig, within-firm-null + cross-sectional-sig, or mixed-sign patterns. The pattern shapes the Q; the Q does not filter the pattern. | Rule | `memory/feedback_phase5_methodology.md` | Added |
| MEMORY.md index note | Doc | `memory/MEMORY.md` | Updated (rules 16-21 note) |
| Incident pointer cross-reference | Doc | Rule 21 body references this incident path | Added |

---

## Prevention

**Rule 21 directly prevents the failure mode:** cells must be catalogued completely before any verdict language. The audit's output is a pattern description, not a Q-answer check. DROP requires a null-across-everything finding, not a "doesn't match current Q wording" finding.

**What rule 21 does NOT cover:**
- Retroactive review of H1/H4a/H4b §4.2 rationales. Those KEEPs were verdicts reached via a Q1 framing that was active at the time but has since been narrative-locked as provisional. The verdicts are probably still correct (substantive primary-IV patterns exist in all 3), but the *rationale wording* may over-commit to the Q1 frame. Flag for post-audit review when the final Q is set.
- Cross-suite pattern building — that is still deferred to post-audit synthesis per `feedback_audit_first_no_narrative.md`.

---

## Verification

**Test scenario:** H12b and H13 dialogues (next 2 suites). Must catalogue all 4 IVs × 12 cells, describe the pattern neutrally, issue KEEP unless a null-across-everything finding, and NOT filter through any §1.3 Q wording.

**Success criteria:**
- No DROP verdict based on "doesn't answer Q1 as written".
- Complete 4-IV × 12-cell matrix shown for each suite in dialogue step (i).
- Pattern description in step (iii) is a factual description, not a Q-match check.
- Verdicts recorded in §4.2 use "pattern" language, not "answers Q" language.

**Review date:** after H12b + H13 + H16 + H17 (4 more Q1 suites). If ANY of those re-trigger Q-as-filter, escalate rule 21 to a harder guard (e.g., a pre-dialogue checklist that forces cell-matrix presentation before any interpretive sentence).

---

## Lessons

1. **"Provisional" is a semantic label, not an operational one.** A Q that is "locked as provisional" still reads as locked unless an operational rule explicitly reframes its role during audit. Naming a Q + arguing cells answer it = rubric-in-disguise when the Q isn't finalized.
2. **Fourth retrospective in 2 sessions is a signal.** Rules 16-20 cover tool discipline, writing shape, verbosity, durability — all mechanical. Rule 21 is the first semantic-role rule. The prior rules closed the mechanical gaps; the semantic gaps are still opening and need their own retrospectives.
3. **User correction shape matters.** The user's first pushback ("you must consider ALL 4 measures") was easy to misread as "you missed PreMgr" — which I had not. The harder pushback ("Q1 will be shaped by what we have!") was the actual correction. Lesson: when a correction lands and I defend, the defense may be technically right (I did report PreMgr) but miss the deeper issue (I was filtering, not cataloguing). Two pushbacks in one dialogue turn is a signal that the correction is at a level I haven't heard yet.
4. **The "reader-question dialogue" process and the "audit-first data-first" principle are in tension.** The philosophy resolved the tension by calling Q provisional, but that verbal resolution was not enough to prevent operational collapse. Rule 21 is the operational patch.
5. **Cataloguing is the primary audit output.** Verdicts are a side effect. A suite with complete cells and a pattern description is already audit-complete in the cataloguing sense. KEEP/DROP/REFRAME are post-hoc labels applied to the pattern, not filters used to produce it.
