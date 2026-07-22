# Speaking rate calibration, five registers

Read each passage aloud at real presentation pace, recording as you go. Report
five times in seconds. Nothing about the speaker notes can be written until
these exist, because a per-slide word budget is a rate multiplied by a time
budget, and an assumed rate makes the whole budget fiction.

**These passages are not the script.** They are calibration text sized to match
the registers the deck actually uses. Do not memorise them.

## Why five and not one

Speaking rate is not a constant. The same person runs 110 to 180 words a minute
depending on what the words are doing. Prose runs fast, digits run slow, and
pointing at a chart inserts pauses that no word count predicts. One global rate
applied to a deck that is half numbers produces a talk that overruns.

Five passages give a rate per register, and each register maps to specific
slides. That is the difference between a budget and a guess.

| Passage | Register | Budgets slides |
|---|---|---|
| 1 | Narrative, motivation | 1 to 4 |
| 2 | Numbers read aloud | Results text on 8 to 10 |
| 3 | Method, dense clauses | 5 to 7 |
| 4 | Walking a chart, deictic | Figures on 8, 9, 10 |
| 5 | Hedged rebuttal, careful | 11 to 13, and all Q&A |

## How to run it

1. Start recording. Start a timer. Read one passage. Stop both.
2. Presentation pace. Not a race, not a lecture to a slow room.
3. Stumble badly, discard the take and redo it. Never average in a bad take.
4. Do all five in one sitting so fatigue does not vary between them.
5. Report five times in seconds.

Listen back to at least passage 5. It is the one where filler words appear,
because it is the register you will be in when an examiner is pressing.

---

## Passage 1, narrative (128 words)

> A firm has privately committed to an acquisition it has not announced. The
> information is material. The law does not require the firm to announce merger
> talks, so silence is legal. But the earnings call still happens, and the chief
> executive still has to take questions. Once he speaks he may not mislead, so
> denial is not available either. He cannot confirm, he cannot deny, and he
> cannot leave. The only thing left is to answer around it.
>
> That is the bind this thesis reads. The question is whether the bind leaves a
> trace in the words themselves, in the part of the call nobody scripted. If it
> does, the language of an earnings call carries information about a deal before
> the deal is public.

Time: ______ s. Rate = 128 / (s / 60) = ______ wpm.

---

## Passage 2, numbers (126 words)

> The estimated within-firm shift is plus zero point zero four six one, with a
> standard error of zero point zero one seven two, and a two-tailed p-value of
> zero point zero zero seven four. The approximate ninety-five percent confidence
> interval runs from zero point zero one two to zero point zero eight zero.
> Against a residual standard deviation of zero point three zero one, that is
> about fifteen percent of the usual across-call spread.
>
> The sample is twenty-seven thousand six hundred and twenty-two firm-quarters,
> across one thousand two hundred and forty-eight firms. Standard errors are
> clustered by firm. Controls are leverage, log assets, Tobin's Q, return on
> assets, capital expenditure, a dividend indicator, and cash-flow volatility.

Time: ______ s. Rate = 126 / (s / 60) = ______ wpm.

---

## Passage 3, method (131 words)

> The design is a within-firm comparison. Every firm serves as its own control,
> because firm fixed effects absorb anything constant about the firm, and quarter
> fixed effects absorb anything common to the market in that quarter. What
> remains is variation within a firm over time. The treated observation is the
> earnings call in the quarter immediately before an acquisition announcement.
> The comparison observations are that same firm's other calls. So the
> coefficient answers a narrow question: when this firm is sitting on an
> undisclosed deal, does the language of its call differ from that same firm's
> language when it is not. Standard errors are clustered by firm, because a
> firm's calls are not independent draws. The identifying assumption is that
> nothing else systematically changes for that firm in that same quarter.

Time: ______ s. Rate = 131 / (s / 60) = ______ wpm.

---

## Passage 4, walking a chart (116 words)

Read this the way you would read it standing beside the projected figure,
pointing. Let the pauses happen. Do not read through them.

> Look at the left panel first. Time runs across the bottom, in quarters relative
> to the announcement, and zero is the announcement quarter. The dots are point
> estimates. The vertical bars through them are ninety-five percent confidence
> intervals. The horizontal line at zero is the null.
>
> Now walk left to right with me. Two quarters before, the estimate sits on the
> line. One quarter before, it lifts, and the bar clears zero. That is the
> flagged call. After the announcement it falls back, which is what we would
> expect, because once the deal is public there is nothing left to be evasive
> about.

Time: ______ s. Rate = 116 / (s / 60) = ______ wpm.

---

## Passage 5, hedged rebuttal (129 words)

This is the register of a Q&A answer under pressure. It is deliberately careful,
and the care is the point. Read it as if an examiner has just challenged you.

> That is a fair challenge, and I want to be careful about how I answer it.
>
> Some firms in my comparison group were probably already in undisclosed talks.
> If that contamination is unrelated to how a chief executive speaks, it pushes
> the estimate toward zero, and what I report is a floor. But I cannot observe
> when negotiations actually began, so I cannot rule out that the contamination
> is related to speech, and in that case I cannot sign the direction of the bias.
> I would rather say that plainly than claim the estimate is conservative.
>
> On the quarter two before the announcement, the coefficient is small and not
> statistically distinguishable from zero. That is an absence of detected
> elevation. It is not a demonstration that no pre-trend exists.

Time: ______ s. Rate = 129 / (s / 60) = ______ wpm.

---

## What happens with the five numbers

Each slide gets budgeted at the rate of its own register, not at a blended
average. Chart slides are budgeted on passage 4, which will come out slowest,
and that is the correct conservatism because those are the slides where running
long is most likely.

The total is checked against 17 minutes rather than 18, leaving a minute for
pauses and slide changes. One examiner prefers defenses that finish promptly, so
overrunning is the expensive failure and underrunning is nearly free.

## Recording the answer

Write all five times and all five rates into `_SESSION_STATE.json` under
`speaker_notes_brief_when_that_work_starts.measured_speaking_rate` before
drafting a single note. If a later session finds that field absent, the
measurement has not happened and the notes cannot start.
