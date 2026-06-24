# Spine↔Prose Drift Audit — 2026-06-24 (compaction-safe)

> ## ✅ RESOLVED 2026-06-24 — all 3 summary plans synced (METADATA ONLY, no thesis prose touched)
> User decisions: **bid-ask KEEP**, **robustness KEEP** (both 2026-06-24). Edits applied + JSON-validated + prop-counts confirmed:
> - **abstract**: guardrail #7 amended (permits C7/bid-ask channel); added `abstract-P1-i` (bid-ask) → 9 props; +direction_audit; allocation_coverage note.
> - **intro**: added `1-P6-c` (bid-ask) + `1-P7-b` (4th contribution, three→four); +direction_audit.
> - **conclusion**: added `5-P3-b` (bid-ask) + `5-P3-c` (robustness); +2 direction_audit entries.
> All 3 files `json.load`-valid; props verified present. Bodies needed no change.
> **2nd pass (advisor catch 2026-06-24):** the proposition layer was synced but the SIBLING plan fields (`intent.statement`, `thin_claim`, `boundary`, `serves`, `allocation_coverage`) still described the old finding-set (intro literally said "three contributions"; conclusion boundary "C4 rule-out only"; abstract capped to C2/C1/C6/C4). All patched with dated reconciliation notes (originals preserved, notes appended). Re-validated: 13 reconciliation notes across the 3 files; all `json.load`-valid.
> **Phase-2 spine now matches prose for the summaries** at both the proposition AND plan-description tiers. (Detail below kept for the record.)


**Why:** Phase 2 = "reword but PRESERVE the spine (propositions/guardrails/number_audit)." If prose ≠ spine, that contract is broken: preserve-spine would DELETE real results; preserve-prose means the spine isn't constraining. Advisor flagged this as the real Phase-2 blocker. This audit sizes the blast radius.

**Method (by hand, no code):** per paragraph, map each `final_prose` sentence → its proposition; an orphan sentence (a result/number with no proposition) = drift. Cross-check numbers vs `number_audit`. Ledgers: `docs/Thesis/rewrite/section*_paragraph_ledger.json`.

## VERDICT: drift is confined to the 3 SUMMARY sections. Bodies are clean.

| section | ledger | drift? | prose content with NO backing proposition |
|---|---|---|---|
| abstract | section_abstract | **YES** | bid-ask sentence ("residual unrelated to post-call bid-ask spread, presentation positively associated…") |
| intro | section1 | **YES** | bid-ask "**Fourth** contribution" in 1-P7 (chain says "three"); bid-ask sentence appended to 1-P6 |
| conclusion | section5 | **YES** | bid-ask sentence + **robustness** sentence ("holds when a withdrawal is treated as a resolution… without its dynamic term") appended to P3 (plan = C4 scrutiny only) |
| data | section3.1 | clean | every number logged in number_audit (88,205 / 1,884 / 0.3010 …) |
| results MA1 | section3.2 | clean | props carry 0.0461***, 0.0051***, p=.0074; number_audit complete |
| results MA2 | section3.3 | clean | props carry 0.0473/0.0455/0.0723 round-trip; number_audit complete |
| cash-spec | section3.4 | clean | props carry 0.0983**, z=2.07, p=.039; cause leg 0.0064 n.s. logged |
| scrutiny | section4.1 | clean | props carry 0.7530***, 0.0408**, −0.0000 n.s.; number_audit complete |
| bid-ask | section4.2 | clean (HOME) | "Outsider Reactions: Bid-Ask Spread"; tab:h14c_ceo2_decomp; DWZ+BGT anchored. This is where the bid-ask result legitimately lives. |
| robustness (withdrawal) | section4.3 | clean (HOME) | props carry 0.0687/0.0457/0.0204 vs main 0.0723/0.0455 |
| robustness (no-dyn-term) | section4.4 | clean (HOME) | props carry 0.0012/0.0318/0.0305 static-FE check |
| framework | section2.1–2.5 | clean | conceptual; no empirical findings to drift. 2.5 = EPU/PRisk validity HOME (logs 0.0124/0.0181/0.7530 in props). |

> Coverage note: summaries got the full prose→prop mapping. The 11 "clean" bodies are **spot-clean / low-risk INFERRED** (rich numeric props + strict build-gate + targeted spot-checks), NOT the same exhaustive sentence→prop map. The pass that actually de-risks Phase 2 is **number-in-prose ⊆ number_audit** per section — run that before any rewrite. 2.x checked by grep for leaked numbers/result-phrases (none) + 2.1 partial read; framework carries no empirical findings, so finding-drift is structurally impossible there.

## Root cause
**Phase-C synthesis** (drafting the abstract/intro/conclusion) pulled real findings from the body — **§4.2 bid-ask** and **§4.3/4.4 robustness** — into the summary PROSE, but never updated those summary ledgers' `proposition_chain` / `guardrails` / `number_audit` / `allocation_coverage`. So the summary spine is STALE; the summary self-audits still claim "every prop homed, no orphans."

**The prose is RIGHT** (verified real analyses with tables). The summary **metadata is stale**.

## Important distinctions (advisor-corrected 2026-06-24)
- **Two different "C5/C7"s.** `C5_convergent_validity` = residual vs **EPU/PRisk indices** (home §2.5); abstract guardrail #7's "C5 NOT elevated" correctly refers to THAT (no EPU sentence in the abstract — fine). **BUT** the bid-ask sentence also says "the scripted **presentation is positively associated** with [the spread]" = **C7 presentation, which guardrail #7 ALSO forbids ("C7 presentation NOT elevated").** So the abstract is NOT merely "plan forgot a finding" — **prose does what the guardrail explicitly bans.** Fix = a DELIBERATE guardrail-#7 amendment.
- **Authority for keeping abstract bid-ask = user's "we included it" (2026-06-24), NOT the FD-override.** The FD-override 2026-06-14 promoted the **EPU** convergent validity (§2.5), not the §4.2 spread. Do not cite it here.

## Fix (Phase-2 prerequisite) — METADATA ONLY, no thesis-prose edit, per-case ratification
For each summary ledger, sync spine to prose:
1. **abstract** — AMEND guardrail #7 to permit the C7-presentation / bid-ask channel sentence (record authority: user 2026-06-24); add the backing proposition (+register_locks: correlational, channel-difference-not-tested); update allocation_coverage (8→9). [bid-ask KEEP = confirmed]
2. **intro** — add "Fourth contribution" proposition to 1-P7 (three→four) + bid-ask proposition to 1-P6; fix the "three contributions" count. [bid-ask KEEP = confirmed]
3. **conclusion** — bid-ask: add proposition [KEEP confirmed]. **Robustness sentence: DECISION PENDING** — keep (add proposition + number_audit) OR cut from prose (belongs in §4.3/4.4; previewing it in the conclusion is a separate editorial call, NOT yet authorized).

Then the Phase-2 number/guardrail-survival gate (keyed off number_audit + guardrail strings, NOT the advisory style-flags) can run safely.

## Locked lessons (carry forward)
- The style harness `guardrail_collision` flag is **advisory only, never the gate.** It misses numbers (proven: "2002 to 2018" unflagged in abstract a2-f2 + intro a2-f7). Phase-2 gate = `number_audit` + guardrail-string verbatim survival across 100% of edits.
- Bodies were built prop-first under a strict prose-gate → clean. Summaries were synthesized → drifted. Any future summary edit must re-sync the spine.
