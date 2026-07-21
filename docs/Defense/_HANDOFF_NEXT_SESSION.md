# HANDOFF — Thesis defense (rewritten 2026-07-21)

Read this file, then `_SESSION_STATE.json` beside it. Between them they carry the
whole state. You do not need the previous conversation.

## 1. Where the work stands

Sina defends his MSc thesis at Telfer, uOttawa. The 13-slide main deck is
finished, approved, and production-locked.

- **Deliverable 1, audit the deck: DONE.** No blocker, no major defect.
- **Deliverable 2, speaker notes for all 13 slides: NOT STARTED.** This is next.
- Deliverable 3, the indexed Q&A appendix: architecture approved, content not
  designed, out of scope until the notes exist.

## 2. Read this before trusting the REV21 ledger

`REV21/THESIS_DEFENSE_CONTINUITY_LEDGER_REV21.json` says the next action is to
resume the Q&A appendix. **That is stale.** Sina redirected to an audit plus
speaker notes, and the audit is complete.

The ledger was left byte-unchanged on purpose. It is a 346 KB control document
from another workstream and hand-editing it risks corrupting it. It remains the
authority for everything else: the operating contract, the 38 approved decisions,
the visual system, the production workflow, the do-not-repeat lessons, and the
appendix architecture. It is not the authority for what to do next. This file is.

## 3. What the audit found

Five independent passes, plus mechanical verification by the operator.

| Dimension | Result |
|---|---|
| Numbers | 136 items on slides 6 to 13, zero exceptions, verified twice |
| Chart geometry | Every plotted point within 0.01 pt of its coefficient |
| Citations | All twelve exist, correct years, correct propositions |
| Claim strength | No causal, mechanism, or cash-only overstatement |
| Rendering | All 13 pages clean |

Four cosmetic wording items remain, listed as decision `D-OPEN-1` in the state
file. None changes a claim, a number, or an interpretation.

**The one thing that matters is not a deck defect.** An examiner can ask what
evidence there is that the CEO knew about the acquisition at the pre-announcement
call. The event clock is anchored on the announcement date; the thesis observes
neither the negotiation start nor the CEO's knowledge. There is no answer. The
only route is a clean concession. It belongs in preparation, not on a slide.

Full detail: `audit/AUDIT_REGISTER.md`. Raw pass outputs: `audit/findings/`.

## 4. Reproduce the audit instead of believing it

```
python docs/Defense/audit/scripts/verify_deck.py
```

Thirteen checks, no model involved, exit code 0 when they all reproduce. It
verifies the deck hash and geometry, the absence of em and en dashes, that
exactly the two recorded dash constructions remain, and that every plotted point
on slides 8, 9 and 10 sits where its printed coefficient puts it.

One trap is encoded in that script and worth knowing: **slide 8 must be measured
against the drawn axis ticks, never the tick labels.** Text centres sit about two
points below the rules they annotate, which looks exactly like a real defect.

## 5. The next action, concretely

Write speaker notes for all 13 slides.

Before drafting, settle `D-OPEN-1` with Sina, because notes quote slide wording
and a change to slide 12 or 13 means reworking those notes. The recommendation on
file is to ship the deck as is.

The full notes plan is in `audit/DECK_AUDIT_PLAN.md` under "Speaker-notes
production plan". The essentials:

- 18 minutes with a 2 minute buffer, split 5 minutes for slides 1 to 5,
  10 minutes for 6 to 10, 3 minutes for 11 to 13.
- Do not invent per-slide times. Measure Sina's own speaking rate first.
- Every academic sentence and every number traces to an exact thesis file and
  location. Where the thesis is silent, say so; never fill the gap.
- Notes explain the visible slide. They never add a result, a mechanism, a causal
  claim, or appendix-only material to the main talk.
- One examiner prefers a defense that finishes promptly. Tight beats complete.

## 6. Thesis sources, for verification

Base: `docs/Thesis/_uottawa_rewrite/`

| File | Use |
|---|---|
| `_tables_from_bible.tex` | Every results table, byte-exact. Truth for any number |
| `sec34_body_from_ledgers.tex` | Main-analysis prose and interpretation |
| `_intro_body.tex` | Positioning claim, contributions, stated limits |
| `_conclusion_body.tex` | Findings summary and every limitation |
| `_thesis_FLAT.tex` | One-file read including the complete reference list |

Never edit anything under `_uottawa_rewrite`. The thesis is submitted and
approved, and it was not audited; it is out of scope.

## 7. Working rules with Sina, non-negotiable

1. Do exactly what he asks. His literal instruction beats your judgement.
2. Replies must be very short. He is exhausted and a long reply goes unread.
3. One decision at a time. Never batch. Never produce a finished artifact before
   its content is approved.
4. Verify every number and quote against the primary file before using it.
5. No em dashes and no dash-based sentence constructions in anything
   audience-facing.
6. Do the work yourself. He has banned subagent delegation on this task.
7. Record decisions as they happen. Anything unrecorded is lost.

## 8. If you need another ChatGPT web call

Read `C:\Users\sinas\OneDrive\Desktop\Projects\GptWebCall\WEB_CALL_PROTOCOL.md`
first. Calls can now run in parallel, each bound to its own tab, and a delivery
that fails validation can be repaired inside the same conversation.

Two filenames may never collide across calls that can still receive files;
`prepare` enforces this and will refuse the second one.

**Download every returned file before clicking Done and validate.** Done stops
monitoring and anything arriving afterwards is not collected. If that happens,
copy the files into the exchange's `response/` directory and run
`validate --exchange <id>`.

## 9. Superseded, do not use

`defense_slides.tex` and `defense_slides.pdf`, a 15-slide Beamer draft, and
`_CODEX_HANDOFF_2026-07-12.md`. Both predate the REV21 deck. History only.
