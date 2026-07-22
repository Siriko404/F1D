# Measure the speaking rate before writing any speaker note

This is the first step of the speaker-notes work and the only one Sina has to do
himself. Nothing else about the notes can be right until it is done.

## Why it cannot be skipped or assumed

A per-slide word budget is a speaking rate multiplied by a time budget. Assume
the rate and the budget is fiction, the notes are the wrong length, and the talk
either runs long or gets cut on the day. One examiner prefers defenses that
finish promptly, so running long is the expensive failure.

Rates vary far more than people expect, from roughly 110 to 180 words a minute
for the same person depending on material. That range is the difference between
a 15 minute talk and a 24 minute one on identical notes.

Two passages, not one, because the rate is not constant. Prose runs fast and
numbers run slow, and this deck is half numbers. Take the **lower** of the two
clean rates. A budget built on the faster rate overruns.

## How to run it

1. Start a timer, read passage A aloud at presentation pace, stop the timer.
2. Do the same for passage B.
3. Read at the pace you would actually use in the room. Not fast, not careful.
4. If you stumble badly, discard that run and repeat. Do not average in a bad
   take.
5. Report both times in seconds.

Then: rate = words / minutes, take the lower, multiply by 17 minutes, and split
the result 5:10:3 across slides 1-5, 6-10 and 11-13. Seventeen rather than
eighteen leaves a minute for pauses and slide changes.

---

## Passage A, narrative register (128 words)

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

Words: 128. Time it: ______ seconds. Rate: 128 / (seconds / 60) = ______ wpm.

---

## Passage B, number register (126 words)

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

Words: 126. Time it: ______ seconds. Rate: 126 / (seconds / 60) = ______ wpm.

---

## Recording the answer

Write both times and both rates into `_SESSION_STATE.json` under
`speaker_notes_brief_when_that_work_starts.measured_speaking_rate` as soon as
Sina reports them, before drafting a single note. If a later session finds that
field still absent, the measurement has not happened and the notes cannot start.
