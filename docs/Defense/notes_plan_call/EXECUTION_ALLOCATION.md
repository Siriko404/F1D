# Which units run as web calls and which run locally

The returned process design specifies thirteen units. It does not say who
executes them, because it was not asked. Every unit run as a web call costs Sina
five manual actions: Go, Attach, Send, download each file, Done. Thirteen units
is sixty-five actions by an exhausted presenter. That cost is real and the design
did not price it.

This file allocates each unit. It does not change the design.

## The criterion

The wrong question is which units are hard. Both the web model and the local
agent are strong reasoners, so difficulty does not discriminate.

The right question is what each side structurally has that the other cannot get.

**What only the web call has.**

*Independence from the author.* An agent that drafts a script and then audits it
brings the same blind spots to both jobs. This is a conflict of interest, not a
capability gap, and no amount of care fixes it. The project has direct evidence.
The REV22 deck was declared airtight by the agent that edited it, and an outside
audit returned nine findings including two real errors of judgement. In this same
session an outside reviewer caught a budget that allocated 110 words to slide 12
while requiring 129 words of content there, a contradiction inside a file the
agent had written and reread.

*Absence of anchoring.* The local agent carries the entire session and has
already committed to positions. On divergent searches, where the question is what
else could be true or what else could be attacked, prior commitments narrow the
search. A cold reader searches wider. The design call just demonstrated this: it
surfaced the cash versus stock Wald requirement and the cash GAP two clock
nuance, neither of which the local agent had raised across a long session with
the same files open.

**What only the local agent has.**

*Programmatic verification.* Word counts, character scans, quote traces and
coverage are computable. A web call reporting that a slide is 264 words is
asserting arithmetic it cannot run. The local agent computes it. This session
already used that difference to check all twelve grounding quotes verbatim
against source, which no amount of careful reading would have established.

*Zero click cost and free iteration.* Thirteen scripts can be revised in one
local pass. Each web revision is a full round trip that Sina has to drive.

## The allocation

| Unit | Work | Owner | Why |
|---|---|---|---|
| U01 | Claim and scope ledger | Local | Retrieval and verification, not divergent search. Every cited thesis location can be programmatically confirmed to contain the claimed text, which a web call can only assert. Coverage is checkable by extracting every numeral from the slide text and asserting a ledger row exists for each. |
| U02 | Script architecture, audience job, cut hierarchy, and a lay framing bank | **Web** | This is where a listener either follows or is lost. The local agent has lived in this material for a long session and is the worst possible judge of what is obvious to a stranger, and has been told four times this session that its prose was too dense to follow. |
| U03 | Examiner attack map | **Web** | Divergent adversarial search against material the local agent has been defending. Maximum conflict of interest and maximum anchoring. Non-negotiable. |
| U04 | Merge into a drafting contract | Local | Mechanical reconciliation under a stated precedence rule, thesis first. |
| U05 to U08 | Draft the 13 scripts | Local | Generation constrained by an approved contract, where the binding constraint is an exact word count. Only the local agent can hit 265 words rather than approximately 265, and the budget is the whole reason this process exists. Independence is preserved at both ends: the architecture comes from a web call and the audit goes to one. |
| U09 | Assemble and write 12 transitions | Local | Small generative work that depends on all thirteen scripts having just been written. |
| U10 | Evidence and inference audit | **Web** | Audits the local agent's own writing. Non-negotiable for the same reason U03 is. |
| U11 | Timing, surface and speakability audit | **Split** | Word counts, the dash scan and boundary enumeration are computable and run locally as a gate. The blind one job test, dense clause detection and listener load are judgement and go to a web call, which then spends none of its reasoning on arithmetic. |
| U12 | Repair from findings | Local | Editing to constraints, then recomputing every deterministic gate. |
| U13 | Final signoff | Local, with a conditional web audit | Almost every hard gate is deterministic: counts, character scan, elapsed time against budget. The exception is the repair regression hole. U12's repairs are the one substantive edit nothing independent has seen. |

## The correction this allocation needed

The first version of this file had a hole, and the evidence for it is in the
session that produced it.

Sina named plain language as the thing he cares about most: simple enough that
you are explaining it to your mother, so the audience is never lost, while
staying completely accurate. Across this same session he replied "too dense,
didn't follow" or "didn't follow" four separate times to the local agent's own
prose. Dense writing is the local agent's demonstrated default failure.

The first allocation then gave drafting to the local agent, gave repair to the
local agent, put only an advisory web audit between them, and made the final
re-audit conditional on a rule keyed to numbers and claims. A purely stylistic
problem could pass through every gate: the dense author drafts, an outsider flags
density, the same dense author decides what that means, and the conditional rule
never fires because no number changed.

That is the conflict of interest used to justify sending U10 out, applied in
reverse on the axis that matters most. Three changes close it.

**One. Plain language becomes arithmetic instead of a self-assessment.** A local
deterministic readability gate runs before the candidate is frozen. It measures
mean words per sentence, the share of sentences over twenty-five words, any
sentence over thirty words, and first use of every listed technical term without
a gloss in the same sentence. This fits the criterion already stated above:
anything computable belongs local, and turning simplicity into a computation
takes it out of the hands of the author who would otherwise grade himself.

**The thresholds are fixed now, before a single script exists.** Setting them
after drafting would let them be tuned until the drafts pass, which is the same
self-grading failure wearing a different hat.

| Gate | Threshold |
|---|---|
| Mean words per sentence, per slide | 18 or fewer |
| Sentences over 25 words | 10 percent or fewer of the script |
| Any sentence over 30 words | Zero. Hard fail. |
| First use of a listed technical term | Must carry a plain gloss in the same sentence |

The gloss list is drawn from the deck and the thesis: attenuation, estimand,
residual, endogeneity, fixed effects, clustered standard errors, confidence
interval, coefficient, event study, counterfactual, identification, parallel
trends, nondifferential, Wald test, Tobin's Q. These are not banned. A defense
that refuses to say "coefficient" is not a defense. The gate only requires that
the first time each one is spoken, the sentence also explains it.

**Two. The plain-language framing does not originate with the local agent.** U02
expands from architecture alone to architecture plus a lay framing bank: for
every technical concept in the deck, the sentence a non-specialist would
understand. The local agent then drafts to exact word counts using those
framings. This costs no extra call and no extra sitting, and it puts the
first articulation of every hard idea in the hands of a reader who has not spent
a long session buried in the material.

**Three. Speakability findings force a re-audit rather than qualifying for one.**
If U11 returns any speakability or listener-load finding, the post-repair audit
is mandatory. The conditional rule below governs everything else.

## The conditional final audit

Repairs are the gap. U10 and U11 audit the candidate, then U12 changes it, and
if nothing independent reads the result then the last edit to the script is the
one edit no outsider ever checked.

Firing a full web audit for three cosmetic fixes is waste. Skipping it after a
substantive rewrite is the failure the whole architecture exists to prevent.

So the final audit fires on a rule rather than a mood. It is required if U12
changes any sentence carrying a number, a result, a causal word or a limitation,
or if more than roughly fifteen percent of spoken sentences changed. Otherwise
the local deterministic re-check stands and the diff is reported to Sina.

## What this costs

| | Web calls | Sina's manual actions |
|---|---|---|
| Design as returned | 13 | about 65 |
| This allocation | 4, plus 1 conditional | about 20 to 25 |

Every unit whose value depends on someone other than the drafting agent doing it
stays a web call. Nothing that provides independence was moved local.

**Running two calls at once cuts waiting, not clicking.** Each call still needs
its own Go, Attach, Send, downloads and Done. Parallel means Sina is not sitting
idle between them, and that both results arrive in one sitting rather than two.
The click count is per call regardless.

## Sequence

The allocation also improves the ordering. The original design ran U01, U02 and
U03 concurrently, so the architecture and the attack map were both built without
the claim ledger. Running U01 locally first costs no clicks and arms both web
calls with it.

1. **Local.** U01 ledger, plus a deterministic coverage check.
2. **Web, two at once.** U02 architecture and U03 examiner map, both holding the ledger.
3. **Local.** U04 contract, U05 to U08 drafts using U02's lay framings, U09 assembly and transitions, then the deterministic gate: per slide counts, global count, dash scan, trace existence, all twelve boundaries enumerated, and the readability thresholds fixed above. The candidate does not freeze until every one of these passes.
4. **Web, two at once.** U10 evidence audit and U11 speakability, on a frozen candidate that has already passed arithmetic.
5. **Local.** U12 repair, then recompute every gate.
6. **Conditional web.** Final audit if the repair rule above triggers.
7. **Sina rehearses.** Then local U13 signoff against the rehearsal log.

Two sittings for Sina, three if the post-repair audit fires.
