# U01. Claim and scope ledger

What a speaker note is permitted to say, and where the thesis stops.

Built locally rather than as a web call because every row here is checkable by
computation against the source, and a web call reporting that a number appears in
the thesis would be asserting a lookup it cannot run.

## 1. Numeral coverage

Every numeral on all 13 slides was extracted programmatically from the deck text.
155 numerals, of which 90 are substantive once slide numbers, axis ticks and the
repeated 95 percent label are removed.

Each was then matched against the thesis, the tables, the robustness tables, the
replication section and the analysis body, using an exact numeral match rather
than a substring search.

| Result | Count |
|---|---|
| Substantive numerals on the deck | 90 |
| Present in the thesis as an exact number | 86 |
| Not present | 4 |

**The substring trap, recorded because it nearly stood.** The first pass used a
plain substring search and reported only one missing numeral. That was wrong.
Searching for `0.012` matches inside `0.0124`, a different coefficient in a
different table on a different topic, and the check reported a hit for a number
the thesis never states. Re-running with a numeral boundary raised the miss count
from one to four. A check that passes while the property it names is false is
worse than no check, and this one passed for exactly that reason.

### The four numerals the thesis does not state

| Numeral | Slide | What it actually is | May a note say it |
|---|---|---|---|
| 0.301 | 8 | The thesis reports 0.3010. Trailing zero only. | Yes, freely |
| 0.012 | 8 | Lower bound of 0.0461 minus 1.96 times 0.0172, which is 0.0124 | Yes, with the wording below |
| 0.080 | 8 | Upper bound of the same interval, which is 0.0798 | Yes, with the wording below |
| 0.192 | 10 | Upper bound of 0.0983 plus 1.96 times 0.0476, which is 0.1916 | Yes, with the wording below |

The three interval bounds are arithmetically correct and were confirmed by
computation. They are nonetheless **the deck's own derivation, not a thesis
result.** The thesis reports coefficients and standard errors and does not print
these confidence intervals anywhere.

**Correction to this section, made after checking the deck rather than assuming.**
The first version of this entry treated the derived intervals as a live risk. They
are not, because the deck already says so on screen. Slide 8 carries "Approximate
95% CI derived from the reported estimate and SE" and slide 10 carries
"Approximate 95% CIs derived from reported SEs."

So the deck is already honest and the risk is not that the audience is misled by
the slide. The risk is that the **note upgrades what the slide downgrades**, by
saying the thesis reports an interval when the slide behind the presenter says it
was derived.

**Permitted wording.** The approximate 95 percent interval implied by the
estimate and its standard error runs from about 0.012 to about 0.080.

**Forbidden wording.** The thesis reports a confidence interval of. It does not,
and the slide says as much.

An examiner who asks where that interval is printed must get the honest answer
that it is computed from the reported estimate and standard error, given
immediately and without hesitation. Hesitating on a question the slide already
answers costs more than the question does.

## 1b. Coefficient and standard error pairs

Matching a number one at a time proves only that the string occurs somewhere in
the thesis. It does not prove it is the same quantity from the same
specification. A coefficient could match a number in an unrelated table and the
check would pass while the property it names is false, which is the same failure
that made the first substring pass unreliable.

The stronger test pairs each coefficient with its own standard error, as the deck
prints them, and requires the two to occur **together** in the thesis within a
short window. A spurious single match will not survive it, because an unrelated
table would have to contain both numbers side by side.

Twenty-five coefficient and standard error pairs were parsed from the structure
of slides 8, 9 and 10.

| Result | Count |
|---|---|
| Structured coefficient and SE pairs on the deck | 25 |
| Confirmed co-occurring in the thesis | **25** |
| Not confirmed | 0 |

That covers every statistical result the deck displays, including all four event
study bins on both clocks, both adjacent-stage Wald tests, the cash lag, the
cash-minus-stock Wald difference and every cash and stock subsample coefficient.

**This is the check the previous audit could not run.** Its own limitations
recorded that the thesis tables were absent from the archive it was given, so the
deck's numbers had never been verified against the thesis by anyone until now.
The tables were packaged for this call specifically to close that gap.

A worked example of why the pairing matters: the deck's 15.3 percent on slide 8
matches the thesis not as a loose coincidence but as an explicit derivation, since
the thesis itself writes "roughly 15.3\%, taking $0.0461$ against the all-universe
standard deviation of $0.3010$".

## 2. Source silence register

Three places where the thesis does not answer a question the notes might be
tempted to answer. Each was confirmed by reading the thesis, not assumed.

### 2.1 Why the sample ends in 2018

**The thesis is silent.** It states the window repeatedly and never justifies the
endpoint. Verbatim, from `_thesis_FLAT.tex`:

> "We study the earnings-call transcripts and acquisition records of United
> States public firms from 2002 to 2018, covering 88,205 calls from 1,884 firms."

That is a statement of scope, not a rationale. The limitations passage treats the
window as a boundary on generality rather than as a choice it defends:

> "the sample, United States public firms from 2002 to 2018, approximately the
> S&P 1500, may not extend to other periods, other markets, or the smaller"

**Ceiling.** No note may invent a reason. The thesis gives none, so nothing may
be read into it.

**ANSWERED BY THE PRESENTER, 2026-07-22.** The window is a data-availability
boundary, not a design choice. The Capital IQ transcript data was accessed
through the school's finance lab, and 2002 to 2018 is the coverage that
subscription provided.

That is a clean answer and it should be given plainly and without apology. Data
access boundaries are ordinary and every empirical committee has met them. The
only way to lose marks here is to sound as though the endpoint were a choice
being defended, because that invites the follow-up about what happens after 2018.

If pressed on whether the period is unrepresentative, the honest position is the
one already on slide 12: it is a limit on generalisation, and the thesis claims
nothing about other periods.

### 2.2 How accurate the speaker attribution is

**The thesis is silent on accuracy.** It asserts the capability and never
quantifies error. Verbatim:

> "download Capital IQ earnings-call transcripts for U.S. public firms over
> 2002--2018, parsed so that we know each speaker's role and whether a turn falls
> in the scripted presentation or in the back-and-forth question-and-answer (Q&A)
> segment"

Knowing a role is not the same as measuring how often the parse gets it wrong. No
validation rate, no hand-checked subsample and no error bound appears.

**Ceiling.** A note may say the transcripts identify the speaker and the segment.
No note may claim the attribution was validated or state any accuracy figure.

**The trap worth naming.** The instinct under pressure is to say misattribution
would just add noise and therefore work against finding anything. That is the
same unsigned-bias error caught on the attenuation argument, and it fails for the
same reason: it holds only if misattribution is unrelated to the thing being
measured, and nothing in the thesis establishes that.

**ANSWERED BY THE PRESENTER, 2026-07-22, then corrected against the code.**

Sina's answer was that attribution comes from the speaker labels in the Capital
IQ data, so the study relies on Capital IQ's data quality. That is true but
incomplete, and the incomplete version is weaker than the real one. **Do not give
it in that form.**

The code was read directly. `src/f1d/text/build_linguistic_variables.py` lines
486 to 495:

```python
is_ceo_exact = (speaker_lower == df["ceo_name_lower"]) | (
    speaker_lower == df["prev_ceo_name_lower"]
)
is_ceo_last = (speaker_last == df["ceo_last"]) | (
    speaker_last == df["prev_ceo_last"]
)
df["is_ceo"] = is_ceo_exact | is_ceo_last
```

So the procedure is a **two-source join, not a label lookup**. Capital IQ supplies
the speaker's name. Execucomp supplies who the chief executive was at that firm
in that period, through `ceoann` and `becameceo` in `build_tenure_map.py`. A turn
counts as the chief executive's when the Capital IQ name matches the Execucomp
name, with the previous chief executive included to cover turnover.

**Say that instead.** It is a stronger answer because it does not rest on one
vendor's labelling. It rests on agreement between two independent sources, and an
examiner who distrusts Capital IQ's labels still has to explain why the
Execucomp name would agree with them wrongly.

**The one real weakness, and it should be conceded before it is found.** The
match is tiered: an exact full-name match, or failing that a **surname-only**
match. A surname match misfires when two people with the same surname speak on
the same call, which family firms and coincidence both produce. The thesis
quantifies no rate for this, and no note may invent one.

The honest concession: the fallback trades a small amount of precision for
coverage, the direction of any resulting error is not established, and it is not
argued to be harmless.

**Verified and not a defect.** The parallel chief financial officer branch below
it carries an explicit empty-value guard that the chief executive branch lacks.
That asymmetry is safe rather than a bug: the CFO comparison applies `fillna("")`
and therefore needs protection against an empty string matching an empty string,
while `ceo_last` stays missing when absent and a missing value never matches.
Checked so that nobody re-raises it as a finding later.

### 2.3 The confidence intervals

Covered in section 1. Derived by the deck, correct, not printed in the thesis.

## 3. Claim ceilings on the dangerous sentences

Six claims where the natural spoken phrasing exceeds what the thesis supports.
Each ceiling is quoted from a source, and each source was verified verbatim.

### 3.1 Contamination and the direction of bias

**Ceiling, from the deck audit:**

> "The design does not establish that unobserved negotiation-onset error must
> attenuate the PRE1 coefficient toward zero."

**Forbidden.** Contamination makes this conservative. It is a lower bound.
**Permitted.** Under classical nondifferential contamination it would attenuate,
but onset is unobserved, so the direction of the bias cannot be signed.

### 3.2 The quarter two before the announcement

**Ceiling, from the deck audit:**

> "A single statistically insignificant PRE2 coefficient does not establish that
> there is no pre-trend or that the signal is tightly timed."

**Forbidden.** There is no pre-trend. The timing is tight.
**Permitted.** No statistically detected elevation at that quarter.

### 3.3 Cash against stock

**Ceiling, from the deck itself, slide 11:**

> "The direct Wald difference, not two separate significance results, is the
> test."

**Forbidden.** Cash is significant and stock is not, therefore they differ.
Comparing one significant coefficient with one insignificant coefficient is not a
test of difference, and the slide already says so, which means narrating it the
loose way contradicts the deck on screen behind the presenter.

### 3.4 Cash through the gap

**Ceiling, from the thesis, verbatim:**

> "the persistence of cash through the gap rests on the *absence* of a *PRE1*-to-*GAP*
> decline, not on a significantly elevated gap level."

**Forbidden.** Cash stays significantly elevated after the announcement.
**Permitted.** Cash does not decline from the pre-announcement quarter to the gap,
and that absence of a decline is what persistence means here.

This is the most dangerous sentence in the deck, because the wrong version is
more fluent than the right one and describes a stronger, cleaner result.

### 3.5 Novelty

**Ceiling, from REV22 change R22-11.** Slide 5 now reads "To our knowledge", which
matches the thesis. No note may drop the qualifier and assert that no prior work
occupies the cell.

### 3.6 What the measure observes

**Ceiling, from the deck audit:**

> "The sentence drops 'residual' and implies exact-point timing, although the
> estimated outcome is residual CEO-answer uncertainty observed on quarterly calls"

**Forbidden.** Any phrasing implying the method observes the moment knowledge
changed. The unit is a quarterly call, and the object is residual uncertainty in
the CEO's answers, not raw uncertainty and not a timestamp.

## 4. What this ledger hands to the next stage

- The four derived numerals, with permitted and forbidden wording for each.
- Two questions the thesis cannot answer, so no draft attempts them.
- Six claim ceilings, each quoted, for the sentences most likely to be overstated
  aloud.

Both web calls receive this. The original design ran the architecture and the
examiner map without it, which would have had both reasoning about claims whose
support had never been checked.

## 5. What this ledger does not cover

Stated plainly rather than left for someone to discover.

**Numbers are complete. Prose claims are not.** Every numeral and every
coefficient and standard error pair on the deck has been checked. The unit
specification also asked for every academic claim and interpretation on all
thirteen slides to be laddered with a permitted ceiling, and that was done for
the six sentences already known to be dangerous, not for the full surface.

The gap is therefore the ordinary interpretive sentence on a slide nobody has
flagged. That is precisely the shape of the last error caught in this project,
where slide 5 carried an overclaim for a long time because it had never been
re-read after the slides around it were edited.

**How it is closed.** The examiner map, run as a web call, sweeps all thirteen
slides for attackable oral claims with fresh eyes, which is a better instrument
for this than the local agent extending its own list. Its output merges into the
drafting contract alongside this ledger. Until that merge happens, this ledger
must not be treated as the complete permitted-claim surface, and no drafting may
begin from it alone.

## 6. Design parameters, all verified

Checked because two of them were nearly lost. `50%` and `-3` were excluded from
the numeral sweep by hand as decoration, and both turned out to be load-bearing:
one defines the treatment arms, the other the omitted baseline. A number excluded
by eye is a number no check ever sees.

| Deck says | Thesis says | Status |
|---|---|---|
| Cash arm at least 50% cash, stock at least 50% stock | "the cash arm, deals that are at least half cash, and the stock comparison arm, deals that are at least half stock" | Confirmed |
| Omitted baseline e <= -3 plus never-acquirers | "The omitted baseline is the set of quarters three or more before the announcement ($e \leq -3$) together with the never-acquirers" | Confirmed |
| POST after completion, 4 quarters or fewer | "We cap the post-window at four quarters" | Confirmed |
| Deal value at least $1 million | "keeping only deals with a transaction value of at least \$1~million" | Confirmed |
| Residual needs repeated calls | "We drop any CEO with fewer than five calls, because with so few calls we cannot estimate a speaking style" | Confirmed |

## 7. One thing that does not reconcile, deliberately left open

Slide 10 shows GAP and POST bins for the cash and stock panels. The thesis, when
describing the cash and stock arms, says:

> "For treated firms we drop the quarters after the announcement, so the design
> sees only the run-up into the deal."

Those two statements cannot both describe the same regression.

The likely resolution is that slide 10 carries two different things, which its
own text supports: a descriptive side-by-side event study with all four bins, and
a separate formal pooled test. The sample sizes point the same way, since 29,535
and 39,819 belong to the "Disclosure-window event study estimated separately for
cash and stock" while 25,600 and 1,191 belong to the "Pooled cash-specificity
test".

**This is not being resolved here, on purpose.** Deciding which specification
produced which panel is exactly the judgement that the examiner map and the
evidence audit exist to make independently, and a local guess recorded as fact
would contaminate both. It is recorded as an open row so both web calls see it.

The examiner question it implies is direct: your slide shows post-announcement
bins for cash and stock, and your thesis says that design drops post-announcement
quarters, so which is it. The presenter needs an answer that does not begin with
hesitation.
