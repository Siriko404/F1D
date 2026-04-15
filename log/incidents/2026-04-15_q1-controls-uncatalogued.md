# Lessons Learned: Q1 Cluster Controls Un-Catalogued in §4.2 Records

**Date:** 2026-04-15
**Severity:** Medium-High — affects 10 of 37 audit records; user explicitly declined retroactive rework so the gap is permanent in Q1 audit memory.
**Status:** Resolved going forward (rule 24 added); Q1 records frozen with gap per user decision.

---

## Incident Summary

Across all 10 Q1 cluster suites (H1, H4a, H4b, H12, H12b, H13, H16, H17, H19b, H20b), the per-suite §4.2 "Key cell fact" line catalogued only the 4 IVs (`UncAnsMgr`, `UncAnsCEO`, `UncPreMgr`, `UncPreCEO`) and `Lagged_DV`. Controls (`Size`, `MTB`, `Profitability`, `CashFlow`, `Tangibility`, cross-DV controls like `CashRatio` / `Leverage`, etc.) were read linearly per rule 6 when reading `outputs/all_tables.tex` but were not catalogued in the §4.2 record except in 2 incidental cases (H4a `CashRatio` β=-0.0297***, H4b `CashRatio` β=-0.0674***).

The gap surfaced at the Q1→Q2 boundary 2026-04-15 when the user asked: *"are you telling me that you have not read the contorl behavior in each suite so far?"*. I clarified: I had READ controls (rule 6 mandates linear read of every line), but I had not RECORDED them in §4.2 (no rule covered cataloguing scope of controls).

**Impact**: 10 audited suites have permanent records missing systematic control behavior. User explicitly declined retroactive re-cataloguing (*"no"* on Q1-retroactive question). Any future audit-time question about "what did the controls do in suite X" requires re-opening the LaTeX table for that suite — cost deferred to Q5 synthesis, not zero.

---

## Timeline

| Turn | Action | Actor | Outcome |
|---|---|---|---|
| 2026-04-14 | H1 §4.2 block written under new rules 21+22+23. "Key cell fact" line includes 4 IVs + Lagged_DV; no controls. **§4.2 template established.** | Claude | First instance of IV-only recording |
| 2026-04-14 → 2026-04-15 | H4a/H4b/H12/H12b/H13/H16/H17/H19b/H20b §4.2 blocks all copy the H1 template structure. Rule 23 added 2026-04-15 explicitly framed audit observables as "sig-star count + FE survival + sig direction" for IVs — implicitly endorsing the IV-only template format. | Claude | 9 more IV-only records produced; gap propagates suite-by-suite |
| 2026-04-15 T-1 | At Q2 cluster start, user directive: *"we must read ALL results in the suites for all variables in their tables!"* | User | Reading + recording scope challenged |
| 2026-04-15 T-2 | I propose three options for Q2 §4.2 recording format (full-table / load-bearing subset / hybrid) and ask whether Q1 needs retroactive rework | Claude | Surface gap as forward question |
| 2026-04-15 T-3 | User asks (verbatim): *"are you telling me that you have not read the contorl behavior in each suite so far?"* + decides "no" on retroactive Q1 rework | User | Direct interrogation; gap acknowledged + Q1 frozen |
| 2026-04-15 T-4 | I admit: read yes (rule 6), recorded no (no rule covered recording scope of controls) | Claude | Gap formalized |
| 2026-04-15 T-5 | User invokes /research-lessons-learned | User | This retro begins |

**Trigger**: H1 §4.2 template establishment under rules 21-23. Rule 23's framing of audit observables as IV-specific was internalized as "the cataloguing layer is also IV-only" — even though rule 23's actual scope was "what NOT to read as IV signal" (β magnitudes), not "what NOT to record".

**Point of no return**: H1 §4.2 first write (2026-04-14). Once the IV-only "Key cell fact" template was established, all subsequent suites copied it structurally without reconsideration. By H4a the template was treated as immutable.

---

## Root Cause (5 Whys)

1. **Why did controls go un-recorded across 10 Q1 §4.2 blocks?**
   → Because the H1 §4.2 "Key cell fact" template I established catalogued only the 4 IVs + Lagged_DV.

2. **Why did the H1 template exclude controls?**
   → Because rule 23 framed audit observables as "sig-star count + FE survival + sig direction" for IVs specifically. I read this as "the audit cataloguing layer is IV-only".

3. **Why did I read rule 23 as IV-only?**
   → Because rule 23's narrative was about what to NOT read as signal (β magnitudes), and the negative-space (controls, R², N) was unspecified. Rule 23 closed the magnitudes-as-signal hole but opened a new controls-uncatalogued hole because it framed audit observables as IV-specific without saying "what about everything else".

4. **Why did unspecified-in-rule become out-of-cataloguing?**
   → Because I conflated **verdict scope** (what determines KEEP/DROP per rule 21: any IV × FE × DV combo with informative pattern) with **record scope** (what gets catalogued in §4.2). Controls don't bear on the verdict per rule 21, so I cut them from the record by default.

5. **Why did I conflate verdict scope with record scope?**
   → Because the §4.2 block contains both the cataloguing artifact ("Key cell fact") AND the verdict artifact ("Verdict + Rationale"). I treated them as a single unit and reduced both to "what's load-bearing for the decision". The empirical record is broader than the verdict signal — controls belong in the record even if they don't bear on the verdict. **Root cause**: the rule set distinguished READ scope (rule 6 — every line) and VERDICT scope (rule 21 — any informative pattern), but had no separate rule for RECORD scope. Cataloguing collapsed into verdict-relevance by default.

**Stop here**: addressable by rule 24.

---

## Contributing Factors

| Category | Factor | Contribution |
|---|---|---|
| Process | No rule distinguishing record-scope from verdict-scope. Rules 6 / 21 covered read / verdict; rule 23 narrowed IV signal but didn't address record completeness. | Primary mechanism |
| Process | Rule 23 wording was negative-space ("NOT in audit signal: β magnitudes") not positive-scope ("RECORD includes: every row"). Negative-space rules leave gaps. | Conflation pathway |
| Communication | User assumed "complete catalogue" in rule 21 meant "all rows of the table". I read rule 21 as "all 4 IVs × all 6 FE × all 2 DVs" — IV-axes only. The wording asymmetry was never tested with the user. | Wording mismatch |
| Context | H1 was the first suite under rules 21-23; I established §4.2 template under those rules and locked in the IV-only format on suite 1. By suite 2 (H4a) the template was treated as fixed. | Template-lock cascade |
| Human | Path-of-least-resistance bias: IVs are the headline, controls are nuisance. Reflexively cut nuisance variables to keep records concise. Reduction-to-headline. | Cognitive bias toward "what matters" |
| Technical | No pre-write checklist for §4.2 blocks ("did this record contain every row of the table?"). Rule 20 durability checkpoint covered grounding/state-counters/git but not record-completeness. | No active gate |

---

## Fixes Implemented

| Fix | Type | Location | Status |
|---|---|---|---|
| **Rule 24 — Read / verdict / record are three different scopes.** RECORD scope = every row of the table catalogued in §4.2 (IVs, controls, Lagged_DV, R², N), regardless of verdict relevance. Cataloguing is the empirical record; the verdict is a downstream summary. Do NOT use "load-bearing for verdict" as a filter on what to record. | Rule | `memory/feedback_phase5_methodology.md` | Adding |
| **Pattern B update in MEMORY.md** — extend "audit first, narrative last" pattern to include "the empirical record is broader than the audit signal; record-scope ≠ verdict-scope". | Pattern | `memory/MEMORY.md` | Adding |
| **Index update** — `feedback_phase5_methodology.md` entry through rule 24. | Doc | `memory/MEMORY.md` | Adding |
| **Tracker update** — note rule 24 + Q1 frozen-with-gap + Q2 cataloguing format = full-row recording. | Doc | `memory/project_phase5_audit_progress.md` | Adding |
| **DECISIONS.md §5.12** — methodology-shift cross-cutting flag: Q1 records frozen with controls-cataloguing gap; Q2 onward uses full-row format per rule 24. | Doc | `docs/Draft/DECISIONS.md` | Adding |
| **This incident report** | Doc | `log/incidents/2026-04-15_q1-controls-uncatalogued.md` | Writing now |
| **Commit** | Git | HEAD `e3265ef` → next | After writes |

---

## Prevention

**Rule 24 directly prevents the failure mode**: §4.2 "Key cell fact" must list every row in the table. The verdict and rationale lines are separate from the empirical record. Cataloguing completeness is decoupled from verdict-decision-making.

**What rule 24 does NOT cover**:
- Q1 retroactive rework — user declined. Q1 records stay with gap. If Q5 synthesis needs control behavior on a Q1 DV, re-open the table at that point.
- Recording-format checklists for non-Phase-5 work.

---

## Verification

**Test scenario**: First Q2 batch §4.2 blocks (H1.1, H1.1b, H1.2). Each block's "Key cell fact" line must catalogue every row of the suite's regression table — main IV, moderator, interaction term, all controls, Lagged_DV, R²/N. Missing any row = rule 24 violation.

**Success criteria**:
- Each H1.1 / H1.1b / H1.2 §4.2 block has a complete row-by-row catalogue.
- A skeptic re-reading the §4.2 block alone (without re-opening the LaTeX table) can answer "what was the sig pattern of every variable in this suite" without needing to re-open the source.
- No selective reduction. "Control X behaves as expected, no flag" is acceptable but the row is still listed.

**Review date**: After H1.1 / H1.1b / H1.2 batch lands. If any block omits a row, escalate rule 24 to a hard pre-write structural check (analogous to rule 17 post-edit Read-back).

---

## Lessons

1. **Read scope ≠ Verdict scope ≠ Record scope.** Three different things. Rules 6 (read every line) and 21 (verdict on any informative pattern) covered two of three. The middle scope (record-scope) was implicit and collapsed into verdict-scope by default. Negative-space in rule wording is not safe — explicit positive-scope rules are.
2. **First suite under a new rule sets the template; lock errors propagate.** H1 §4.2 was the template-fix point. By H4a the template was treated as immutable. When establishing a new artifact format under new rules, ask "is this format complete?" before stamping out 10 copies of it. The cost of fixing 1 template at suite 1 is ~10× the cost of fixing 10 already-written templates at suite 11.
3. **Rules-as-responses-to-failures leave negative space.** Rules 21, 22, 23 were all responses to specific failure modes (Q-as-filter, null-sign-as-signal, magnitude-as-signal). Each tightened what counts as IV signal. None addressed what to do with controls. The implicit assumption "controls are not under audit" (true for the verdict) was conflated with "controls are not catalogued" (false for the record).
4. **The "are you telling me..." question shape is a discipline signal.** When a user re-asks something I should have already done, the question itself is the surface of an undocumented assumption gap. The right response is: "no, here's the gap" + "here's the fix" + "here's the new rule".
5. **Second time in two days I've conflated cataloguing with a downstream filter.** H12 incident (rule 21) was filtering cataloguing through Q-as-target. This incident is filtering cataloguing through verdict-relevance. Same root family: cataloguing layer keeps getting collapsed into a downstream layer (Q wording, verdict relevance, IV-signal narrowness). Pattern B in MEMORY.md needs a corollary: "the empirical record is broader than the audit signal; preserving the record is non-negotiable even when downstream filtering is appropriate".
