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

**Permitted wording.** The approximate 95 percent interval implied by the
estimate and its standard error runs from about 0.012 to about 0.080.

**Forbidden wording.** The thesis reports a confidence interval of. It does not.

An examiner who asks where that interval is printed must get the honest answer
that it is computed from the reported estimate and standard error, given
immediately and without hesitation. Hesitating on a question with a clean answer
costs more than the question does.

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

**Ceiling.** No note may invent a reason. If asked, the only honest answers are
the ones the presenter actually knows, such as data licensing or coverage, and
the presenter is the only person who can supply that. This is not a writing
problem and cannot be solved by drafting.

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
