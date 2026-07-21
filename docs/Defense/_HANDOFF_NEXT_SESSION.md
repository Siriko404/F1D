# HANDOFF — Thesis defense (rewritten 2026-07-21)

Read this file, then `_SESSION_STATE.json` beside it. Between them they carry the
whole state. You do not need the previous conversation.

## 0. The deck to present

```
docs/Defense/REV22/production/thesis_defense_main_deck_slides_01-13_rev22.pdf
```

**REV22, not REV21.** REV21 is the audited artifact and the fidelity reference;
it stays untouched. REV22 is REV21 with the audit's four wording findings fixed
and nothing else changed. Slides 8, 11, 12 and 13 differ; the other nine are
identical span for span. Read `REV22/REV22_CHANGE_LOG.md` before quoting any
slide.

## 1. Where the work stands

Sina defends his MSc thesis at Telfer, uOttawa. The 13-slide main deck is
finished, approved, and production-locked.

- **Deliverable 1, audit the deck: DONE.** No blocker, no major defect. Every
  finding is applied in REV22.
- **Deliverable 2, speaker notes for all 13 slides: NOT STARTED.** This is next,
  and nothing blocks it.
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

Four cosmetic wording items were left open as decision `D-OPEN-1`. Sina chose to
fix them. They are fixed in REV22 and the decision is closed. None changed a
claim, a number, or an interpretation.

**The one thing that matters is not a deck defect.** An examiner can ask what
evidence there is that the CEO knew about the acquisition at the pre-announcement
call. The event clock is anchored on the announcement date; the thesis observes
neither the negotiation start nor the CEO's knowledge. There is no answer. The
only route is a clean concession. It belongs in preparation, not on a slide.

Full detail: `audit/AUDIT_REGISTER.md`. Raw pass outputs: `audit/findings/`.

## 4. Reproduce everything instead of believing it

```
python docs/Defense/REV22/verify_rev22.py          # 16 checks, the deck you present
python docs/Defense/audit/scripts/verify_deck.py   # 13 checks, the audited REV21
```

No model is involved in either. Exit code 0 means every check reproduced.

`verify_rev22.py` answers two questions that must not be merged. First, does this
machine render like the machine that built the locked deck? It renders a
byte-identical copy of the REV21 source and compares all 13 slides against the
locked PDF; the answer is yes, 538 spans, 0.0000 pt drift. Second, did the edit
touch only what it should? Exactly slides 8, 11, 12 and 13 differ, no drawing
moved anywhere, and nothing overflows its page.

`verify_deck.py` targets REV21 and still expects the two dash constructions REV22
removed. That is correct. It checks the audited artifact, not the deck to be
presented. Do not repoint it at REV22.

One trap is encoded in that script and worth knowing: **slide 8 must be measured
against the drawn axis ticks, never the tick labels.** Text centres sit about two
points below the rules they annotate, which looks exactly like a real defect.

## 5. The next action, concretely

Write speaker notes for all 13 slides, against **REV22**. Nothing blocks this.
Slides 8, 11, 12 and 13 were reworded, so quote REV22 and never REV21.

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

## 7a. If you need to render the deck

```
python docs/Defense/REV22/render.py both
```

WeasyPrint works on this machine, but only because `render.py` calls
`os.add_dll_directory(r"C:\Program Files\Tesseract-OCR")` before importing it.
Tesseract bundles the full GLib and Pango stack that WeasyPrint needs.

**Do not try to fix a WeasyPrint import error by putting anything on `PATH`.**
Since Python 3.8, Windows DLL resolution for ctypes and cffi ignores `PATH`
entirely. It looks like it should work and it does nothing. This cost real time
once already.

Fontconfig prints `Cannot load default config file` on every run. Ignore it.
Every font is embedded in the HTML as base64, so no system font is consulted.

Do not substitute Chrome or any other engine. A different layout engine reflows
all 13 slides and destroys the standardization lock. After any render, run
`verify_rev22.py`, then look at the changed slides as images. Clipped text still
extracts cleanly, so only the eye catches overflow.

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
