# Lessons Learned: Red-Team Caught 3 HIGH Findings After H1/H4a/H4b

**Date:** 2026-04-14
**Severity:** High — 3 independent HIGH-severity discipline failures, all in load-bearing audit artifacts, all surviving 3 suite dialogues undetected. Would have propagated into future sessions without external intervention.
**Status:** Resolved — all 6 findings fixed and committed (commit `453aa90`); rule 20 (per-suite durability checkpoint) added to `feedback_phase5_methodology.md`.

---

## Incident Summary

After finishing H1, H4a, and H4b dialogues with KEEP verdicts, an adversarial red-team agent spawned at user request discovered 3 HIGH-severity problems in the session's output:

1. **Factual error in H1 Argument**: Claimed "β ≈ 0.003-0.007 on a standardized IV" — `UncAnsMgr` is a winsorized percentage (mean=0.82, sd=0.33 per `summary_stats.csv:6`), NOT standardized. The "modest magnitude" verdict was correct but the reasoning used a false premise that any committee member would have caught.
2. **State counter staleness across 5 locations**: `DECISIONS.md:3` said "1/37", `MEMORY.md:77` said "0/37", `PROGRESS.md:68` said "1/37 next=H4a", tracker YAML description said "1/37 next=H4a", and tracker table had DUPLICATE rows (H4b and H12 each appearing twice — once updated, once stale).
3. **Zero git commits across the full session**: 3 suite audits + 2 retrospective reports + 4 discipline rules (16-19) + red-team-found fixes all sat in working tree / untracked state. A context reset or compaction would have lost all of it.

None of these were caught by me. All three were flagged by the adversarial agent. I then verified each from primary sources, confirmed the findings, fixed them, and committed.

---

## Timeline

| Turn | Action | Actor | Outcome |
|---|---|---|---|
| T0-T1 | H1 dialogue writes §4.2 Argument including "on a standardized IV" phrase without verifying the claim | Claude | Factual error planted (not caught) |
| T2-T6 | H1 → H4a → H4b writes. Each write updates ONE state counter location (DECISIONS.md *or* MEMORY.md *or* PROGRESS.md *or* tracker YAML) but never the full set | Claude | 5-location inconsistency accumulates |
| T7 | Tracker table update after H4a inserts "next H4b" row but leaves old "H4b pending" row intact. Same after H4b. | Claude | Duplicate rows planted |
| T8 | H1, H4a, H4b writes + incident reports + rule additions → never committed | Claude | Durability risk accumulates |
| T9 | User requests adversarial red-team agent | User | External verification triggered |
| T10 | Red-team reports 3 HIGH + 5 MEDIUM/LOW findings from primary-source verification | Agent | Failures surfaced |
| T11 | I verify each finding against `summary_stats.csv`, source files, git status — all confirmed | Claude | Recovery |
| T12-T15 | 6 fixes applied: H1 Argument rewritten with true sd + correct magnitudes; 5 state counters reconciled; duplicate tracker rows removed; §5.1 depth precision added; H4b narrow-miss disclosed; commit `453aa90` lands | Claude | Resolved |

**Trigger:** user invoked adversarial red-team agent. Without this, all 3 HIGH findings would have persisted.

**Point of no return for finding #1:** the moment the H1 Argument prose was typed with "standardized IV" — I never went back to verify it before committing to paper. Every subsequent read-back preserved the error because I was reading for structural consistency, not fact-checking.

**Point of no return for finding #2:** the moment the second state-counter location got updated in a different edit from the first. Once two files disagree, every subsequent edit has to decide "which is right?" and usually defaults to updating the local file only, not sweeping.

**Point of no return for finding #3:** the first uncommitted write. After that, momentum favors "keep going".

---

## Root Cause Analysis (5 Whys)

Applied to the shared pattern across all 3 findings: **no per-work-unit durability discipline**.

1. **Why did 3 HIGH-severity discipline failures accumulate across 3 suite dialogues without me catching any?**
   → Because I treated each suite dialogue as complete after the §4.2 block was written and read back. "Write → read back → verdict → move on" was my loop.

2. **Why was the loop incomplete?**
   → Because the loop only verifies *what I just wrote* (rule 17 read-back) and not *what I just wrote in relation to other files* (consistency) or *what I claimed factually* (grounding) or *what the work represents outside this session* (durability).

3. **Why does my dialogue loop only check local correctness?**
   → Because rule 17 was added for a specific failure mode (garbled Edit payloads) and was scoped narrowly to that failure. Rules 16-19 are all about *while working*, none are about *before moving to the next work unit*.

4. **Why is there no "before moving to the next work unit" rule?**
   → Because no prior retrospective caught the specific cross-file / cross-session hygiene pattern. The earlier retrospectives were triggered by tool-discipline slips (rule 16) and narrative-spin (rules 18-19), both intra-turn failures. Cross-work-unit hygiene was invisible until the red-team made it visible.

5. **Why was cross-work-unit hygiene invisible to me?**
   → Because I internally treated each suite as a self-contained dialogue turn and optimized for "finish this suite cleanly, then start the next". That optimization is locally correct but systematically produces the three failures above: (a) unverified claims slip past the local read-back; (b) state counters drift because updating multiple files in one edit pass is slower than updating the "current" file; (c) durability/commit is someone-else's-problem because the dialogue framing has no "ship it" step.

**Root cause:** Phase 5 dialogue rules optimize for intra-dialogue correctness and have no explicit checkpoint for cross-dialogue hygiene (fact-grounding, cross-file consistency, git durability). Without an explicit checkpoint, each of those three concerns is systematically under-executed.

---

## Contributing Factors

| Category | Factor | Contribution |
|---|---|---|
| Process | Rules 16-19 scope to intra-turn behavior; no rule on cross-turn hygiene | Allowed all 3 failures to accumulate |
| Process | Rule 17 (post-edit read-back) reads only for structural correctness, not fact grounding | Finding #1 slipped past read-back |
| Technical | State counters live in 5 separate files across 2 git repos (F1D + memory) | Updating one at a time becomes the path of least resistance |
| Technical | Git commits are never triggered automatically; require explicit user or model action | Zero-commit state is the default, not a deviation |
| Context | Long session, many writes, momentum pressure | "Just one more suite then I'll reconcile" |
| Human | I trust claims I've just written more than claims from others — self-verification bias | Finding #1 "standardized IV" felt true because I wrote it |

---

## Fixes Implemented

| Fix | Type | Location | Status |
|---|---|---|---|
| **Rule 20: per-suite durability checkpoint.** After the write phase of each per-suite dialogue (writes to §4.1 row, §4.2 block, §5 flags, memory tracker, PROGRESS.md), and BEFORE the "say go for next suite" transition, run a 3-item checkpoint: (a) **grounding** — any factual claim I introduced in the §4.2 Argument or §5 Status? If yes, name the primary source and verify. (b) **consistency** — did I touch any state counter? If yes, sweep all 5 canonical locations (DECISIONS.md:3, PROGRESS.md header + Phase 5 bullet, MEMORY.md index line for tracker, tracker YAML description, tracker body). (c) **durability** — are DECISIONS.md + PROGRESS.md committed? If no, commit before starting the next dialogue. | Rule (feedback memory) | `memory/feedback_phase5_methodology.md` | Updated |
| MEMORY.md index note about rule 20 + incident pointer | Documentation | `memory/MEMORY.md` | Updated |
| Cross-link in `feedback_verification_depth.md` to rule 20 grounding clause | Documentation | `memory/feedback_verification_depth.md` | Updated |

---

## Verification

**Test scenario:** H12 dialogue (next). After writing the §4.1 row, §4.2 block, memory tracker, and PROGRESS.md updates, run the rule 20 checkpoint: (a) fact-ground any factual claims (e.g., "PayoutRatio_q has X mean" → verify against `summary_stats.csv`); (b) sweep all 5 state counter locations; (c) commit before transitioning to H12b.

**Success criteria:**
- Zero factual errors discoverable by a post-hoc red-team verification on any H12+ write.
- All 5 state counter locations agree after each suite closes.
- Every suite completion is followed by a git commit before the next suite begins.
- No "uncommitted working tree" state at the start of any new dialogue turn.

**Review date:** after next 5 suites (H12, H12b, H13, H16, H17). If the red-team rerun or a spot-check finds ANY of the 3 failure categories, escalate: rule 20 needs to be converted to a hard hook (e.g., a pre-dialogue-start script that rejects state if counters disagree or git working tree is dirty).

---

## Prevention

- **Rule 20 grounding clause** directly prevents finding #1 class: unverified factual claims must be grounded in a named primary source before landing in §4 text.
- **Rule 20 consistency clause** prevents finding #2 class: all 5 state counter locations are swept as a single action, not piecemeal.
- **Rule 20 durability clause** prevents finding #3 class: zero-commit states are rejected at the dialogue boundary.
- **What this does NOT cover:** factual errors in the initial cell-plain read (transcription errors from `all_tables.tex`). Those are covered by rule 17 read-back + the red-team's Category 1 verification. Rule 20 addresses *derived* claims (magnitudes, standardizations, comparisons), not raw transcription.

---

## Lessons

1. **Self-verification is structurally insufficient.** I re-read what I write, but I re-read for structure not grounding. "Did I write it correctly" and "is what I wrote true" are different checks. Only the latter catches finding #1-class errors, and only an external verifier or an explicit grounding step catches them reliably.
2. **State counter updates are a sweep operation, not a local edit.** Every time a state changes (count, next pointer, date, verdict), ALL copies of that state must update atomically. Updating file-by-file produces inconsistency windows that harden into bugs when not closed immediately.
3. **Three retrospectives in one session is a signal, not just a count.** The rate suggests the baseline discipline rules have systematic gaps, not isolated slips. Each retrospective added rules targeting the specific surfaced failure. The better mental model: **audit discipline needs a pre-launch checklist, a during-work guardrail, and a post-work verification** — rules 16-17 are during-work, rules 18-19 are pre-writing shape constraints, rule 20 is post-work verification. The set is now closing on three-phase coverage.
4. **Red-team agents catch what self-review misses.** The agent caught three HIGH findings I would not have caught on any number of re-reads because self-review biases toward preserving authored content. Schedule red-team verification at regular intervals, not only when the user asks.
5. **Commit is not optional for long work.** Compaction risk and context-reset risk make "I'll commit later" equivalent to "I'll lose this". Treat every commit-worthy unit as "commit now or accept loss".
