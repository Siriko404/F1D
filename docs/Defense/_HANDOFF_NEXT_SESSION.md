# HANDOFF — Thesis defense (rewritten 2026-07-21)

Read this file, then `_SESSION_STATE.json` beside it. Between them they carry the
whole state. You do not need the previous conversation.

## 0. The deck to present

```
docs/Defense/REV22/production/thesis_defense_main_deck_slides_01-13_rev22.pdf
```

**REV22, not REV21.** REV21 is the audited artifact and the fidelity reference;
it stays untouched. REV22 is REV21 with eleven edits: the audit's four wording
findings, the em and en dash removed from the PDF title, one limitation added to
slide 12 and then corrected, and one overclaim removed from slide 5. **Slides 5,
8, 11, 12 and 13 differ; the other eight are identical span for span.** Read
`REV22/REV22_CHANGE_LOG.md` before quoting any slide.

## 1. Where the work stands

Sina defends his MSc thesis at Telfer, uOttawa. The 13-slide main deck is
finished, approved, and production-locked.

- **Deliverable 1, audit the deck: DONE.** No blocker, no major defect. Every
  finding is applied in REV22.
- **Deliverable 2, speaker notes for all 13 slides: DONE, 2026-07-22.** Written,
  independently audited, corrected, and passing every deterministic check.
  `SPEAKER_NOTES.md`, 2108 words. **See section 5a, which supersedes section 5.**
- Deliverable 3, the indexed Q&A appendix: architecture approved, content not
  designed. Now the next piece of writing work.

**What is actually left is not writing.** It is a timed rehearsal, which has
never happened, and two questions the thesis cannot answer. Section 5a.

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
| Claim strength | No causal, mechanism, or cash-only overstatement. One hedge-dropping overclaim on slide 5 was missed here and later caught by the adversarial audit, fixed as `R22-11` |
| Rendering | All 13 pages clean |

Four cosmetic wording items were left open as decision `D-OPEN-1`. Sina chose to
fix them. They are fixed in REV22 and the decision is closed. None changed a
claim, a number, or an interpretation.

Slide 12 then gained a fifth change that is **not** cosmetic. It now carries the
CEO-timing limitation, which the thesis states nowhere and which no other slide
or prepared answer covered. Recorded as `D-OPEN-2`. The rule that settled what
belongs there: if the thesis discloses a caveat, answer it aloud and cite the
page; if the thesis discloses it nowhere, it goes on the slide.

**Read `_DEFENSE_LEDGER.md`.** It holds committee dossiers, sixteen prepared
examiner questions with answers, and fifteen defensive assets already inside the
thesis. It was missed for an entire working session because nothing pointed at
it. It is the richest single input to the speaker notes. Its section C slide
numbers refer to a retired Beamer draft and do not map to REV22.

**The sharpest question, and the answer it does have.** An examiner can ask what
evidence there is that the executive knew of the acquisition at the
pre-announcement call. Sharpened, the attack is about onset, not knowledge: a
chief executive is party to their own negotiations by definition, but SDC gives
only the announcement date, so a flagged call could predate the point there was
anything to withhold.

An earlier reading of this file said there was no answer and only a clean
concession. That was too defeatist. Two real rebuttals exist and belong in the
speaker notes:

1. Misflagged quarters dilute a binary treatment indicator, which drags the
   estimate toward zero. **State this conditionally, never flatly.** An
   adversarial audit rated the flat version MAJOR: attenuation requires the
   misclassification to be nondifferential, and onset is unobserved, so the bias
   cannot be signed. The safe sentence is *"Under classical nondifferential
   contamination it would attenuate, but onset is unobserved, so I cannot sign
   the bias. The coefficient is an announcement-anchored average association, not
   an identified effect of negotiation exposure."*
2. The event study shows the signal is concentrated. `PRE2` is 0.0068 and
   insignificant; `PRE1` is 0.0473 at the one-percent level. **Say "no
   statistically detected elevation at PRE2", never "no pre-trend".** PRE2's
   approximate interval runs from about -0.028 to 0.042, which is wide enough to
   contain real earlier drift, and the same audit rated the certainty claim
   MAJOR. The thesis avoids this trap elsewhere by calling its scrutiny rule-out
   *"a failure to find, not a powered equivalence test"*.

**Do not confuse the two.** The onset can be wrong in two directions and `PRE2`
only catches one of them:

| | What went wrong | Flat `PRE2` catches it? |
|---|---|---|
| A | negotiations began earlier than the window | yes |
| B | negotiations began after the flagged call | **no** |

A firm in case B contributes nothing to `PRE1` and nothing to `PRE2` alike, so a
flat `PRE2` is consistent with any amount of B. Nor does a significant `PRE1` rule
B out: `PRE1` is an average, so contamination attenuates it rather than flattening
it. **Only rebuttal 1 answers direction B.** A guard clause pointing at `PRE2` was
briefly shipped on slide 12 and removed as `R22-10`; do not reintroduce it.

Rebuttal 1 holds only while the misflagging is unrelated to deal timing. Noise
that tracks the pre-announcement window is a confound, not noise, and runs the
other way. The thesis claims no mechanism, which is what bounds the damage.

Slide 12 states the boundary in one line. Both rebuttals stay off the slide and go
in the notes.

Full detail: `audit/AUDIT_REGISTER.md`. Raw pass outputs: `audit/findings/`.

REV22 was then audited adversarially in its own right; that response is at
`REV22/audit_call/response/`. It reproduced the PDF diff independently and found
the artifact clean, but it caught one overclaim the first audit missed. Slide 5
had asserted *"No prior work occupies this exact cell"* where the thesis says
*"To our knowledge..."* and calls it a positioning claim. Fixed as `R22-11`. The
lesson generalises: slide 5 was never edited, so nobody re-read it.

## 4. Reproduce everything instead of believing it

```
python docs/Defense/REV22/verify_rev22.py          # 23 checks, the deck you present
python docs/Defense/audit/scripts/verify_deck.py   # 13 checks, the audited REV21
```

No model is involved in either. Exit code 0 means every check reproduced.

`verify_rev22.py` answers two questions that must not be merged. First, does this
machine render like the machine that built the locked deck? It renders a
byte-identical copy of the REV21 source and compares all 13 slides against the
locked PDF; the answer is yes, 538 spans, 0.0000 pt drift. Second, did the edit
touch only what it should? Exactly slides 5, 8, 11, 12 and 13 differ, the charts
on slides 8, 9 and 10 are untouched, no drawing moved on any slide the edits did
not reach, and nothing overflows its page.

`verify_deck.py` targets REV21 and still expects the two dash constructions REV22
removed. That is correct. It checks the audited artifact, not the deck to be
presented. Do not repoint it at REV22.

One trap is encoded in that script and worth knowing: **slide 8 must be measured
against the drawn axis ticks, never the tick labels.** Text centres sit about two
points below the rules they annotate, which looks exactly like a real defect.

## 5a. The next action, concretely. This supersedes section 5.

The notes exist. `SPEAKER_NOTES.md`, 2108 words, every slide inside its measured
budget. Section 5 below is kept only as the record of how they were planned.

**Before editing a single word of them, run the gate.**

```
cd docs/Defense/notes_plan_call
python gate.py ../SPEAKER_NOTES.md
```

It checks length against the measured budget, sentence complexity, dashes,
first-use glossing of technical terms, sixteen forbidden phrasings, and that
every number spoken on a slide is visible on that slide.

**A green gate does not mean the notes are correct.** It means they are worth
auditing. An independent audit found sixteen meaning-level defects in a draft
that passed every one of these checks. The gate is a floor, never a ceiling.

### The mistake this project keeps making

Four times now, in different clothes: treating a statistically insignificant
result as evidence the thing is absent.

It appeared as "no pre-trend" from a flat PRE2 coefficient. It appeared in the
attenuation argument, where an unsigned bias was called conservative. It appeared
as "indistinguishable from baseline" on slide 9. And it appeared in the first
draft of these notes, where the script explained the discipline carefully and
then, two paragraphs later, said flatly that cash does not fall at announcement.

**If you edit any sentence about a null result, check it against this first.**
The correct form is "no detected decline", never "no decline".

### What is genuinely left

**A timed rehearsal.** Never done. The budget contains a fifteen percent delivery
discount that is a judgement, not a measurement, and only a rehearsal against a
clock tests it. Until then 2108 words is a ceiling, not a target. Count filler
while doing it: the rate test asked for recordings so filler could be heard, the
recordings were made, and no count ever came back.

**Two questions the thesis cannot answer.** Both confirmed by reading it.

1. Why the sample ends in 2018. The thesis states the window repeatedly and never
   justifies the endpoint. Only Sina knows the real reason.
2. How accurate the speaker attribution is. The thesis says transcripts are
   parsed to identify speaker role and never quantifies error. **Do not answer
   that misattribution just adds noise.** That is the unsigned-bias error above
   wearing another hat.

**The Q&A pack.** The two conditional rebuttals live there rather than on the
podium, because slide 12 has about 120 words and the pair costs about 129.
Passage 5 of `SPEAKING_RATE_TEST.md` is close to the wording both should use.

### Where the supporting work lives

| Path | What it holds |
|---|---|
| `notes_plan_call/u01_claim_ledger.md` | What may and may not be said, every ceiling quoted from a verified source |
| `notes_plan_call/u02_response/` | Script architecture, twelve transitions, thirty six plain-language framings with word costs |
| `notes_plan_call/u03_response/` | Examiner attack map across all thirteen slides |
| `notes_plan_call/u10_response/` | Audit of the finished scripts, sixteen findings, all applied |
| `notes_plan_call/EXECUTION_ALLOCATION.md` | Which work runs locally, which needs an outside reader, and why difficulty is the wrong criterion |

### One thing about the tooling

`GptWebCall` used to report an honest `PARTIAL` response as an **invalid file**,
sending the reader to repair something that was perfectly fine. Prompts here
explicitly ask for `PARTIAL`, so the system punished the behaviour it requested.
Fixed 2026-07-22 with five regression tests; delivery integrity and work
completeness are now separate fields. If the watcher says `READY (PARTIAL)`,
**read it**: the files are intact and the responder has named its own gaps.

## 5. How the notes were planned. History only, superseded by 5a.

Write speaker notes for all 13 slides, against **REV22**. Slides 5, 8, 11, 12 and
13 were reworded, so quote REV22 and never REV21.

The full notes plan is in `audit/DECK_AUDIT_PLAN.md` under "Speaker-notes
production plan". The essentials:

**Step one, before drafting anything: `SPEAKING_RATE_TEST.md` beside this file.**
It holds two timed passages for Sina to read aloud, one prose and one
number-heavy, because his rate differs between them and the lower one is what to
budget on. Until `_SESSION_STATE.json` carries
`speaker_notes_brief_when_that_work_starts.measured_speaking_rate`, the
measurement has not happened and every per-slide word count would be invented.

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
first. It is the authority; this is only orientation.

**Every exchange is two files each way.** Up: the generated `PROMPT_<time>.md`
and one `<subject>_inputs.zip` holding everything else, both built by the
companion from the ordinary `input_files` list. Down: the main JSON and one
`<pass>_outputs.zip`. `expected_artifacts` must be either empty or a single
`.zip`, and `prepare` refuses anything else.

One cost of that rule, and it matters whenever thoroughness is the point:
natively attached files are read directly, while an archive has to be extracted
first, and a model that extracts carelessly skims. **Require an inventory** in
the prompt, every extracted filename with its byte size, echoed before any
answer. The REV22 audit did this, and its inventory is what proves it actually
read the archive rather than glancing at it.

Calls can run in parallel, each bound to its own tab, and a delivery that fails
validation can be repaired inside the same conversation. Two deliverable
filenames may never collide across calls that can still receive files.

**Download every returned file before clicking Done and validate.** Done stops
monitoring and anything arriving afterwards is not collected. The side panel now
guards this: each running call shows its expected files as a checklist, ticked
with a size as they land, and Done stays disabled until they all have. Forcing it
takes a second, deliberate click. If files are missed anyway, copy them into the
exchange's `response/` directory and run `validate --exchange <id>`.

## 8a. Durability, unresolved

Everything here is committed on both trees, so a lost conversation costs nothing.
A lost disk costs all of it.

`phase4/masking-rewrite-harness`, the branch holding every REV22 artifact, has
never been pushed and does not exist on the remote; it is 406 commits ahead of
`origin/master`. The `F1D` tree is 291 ahead. `GptWebCall` has no remote at all,
so the two-file protocol, the rebuilt side panel and every preserved exchange sit
on one machine.

OneDrive is sync, not backup. It propagates a deletion exactly as faithfully as
it propagates a file.

Pushing is Sina's call and was not authorized. If he says the word, push; do not
do it quietly.

## 9. Superseded, do not use

`defense_slides.tex` and `defense_slides.pdf`, a 15-slide Beamer draft, and
`_CODEX_HANDOFF_2026-07-12.md`. All predate the REV21 deck. History only.

`_CURRENT_HANDOFF_LEDGER.md` is also superseded and carries a banner saying so.
It belongs to the July 14 web-call workstream and its "immediate next action" was
finished a week ago. Do not act on it.
