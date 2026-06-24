# lit_review — RAW harness output (all 14 findings, fate-tagged)

Panels: 4+5+5 = 14. Redteam: keep 3 + merge 4 (folds 6) + reject 1. Profile = 7 kept.

## KEPT (7) — these became the profile

### a1-f4  (KEPT)  [minor]
**Litotes / double-negation instead of a plain positive statement**

EXEMPLAR:
  - (bushee2018) "Conference calls are informative to market participants and lead to reductions in information asymmetry"
  - (ragozzino2024) "this information plays a central role in influencing shareholders' future expectations of companies and hence valuations"
OURS:
  - (section2.1-U1) "such a withholding state is not informationally empty"
  - (section2.1-U3) "they are not informationally empty"
GAP: Exemplars state the positive directly ('Conference calls are informative'); we use litotes ('is not informationally empty') that says the same thing but requires the reader to undo a double negative.
AIM: Where the intended meaning is simply that the state is informative, state it positively ('the withholding state is informative' / 'these non-answers are informative') instead of via double negation, keeping the claim identical.

### a2-f3  (KEPT)  [major]
**Multiple cited results fused into one colon-led, multi-clause sentence vs one result per sentence**

EXEMPLAR:
  - (bushee2018) "Li [2008] uses the Gunning [1952] Fog Index to measure the "linguistic complexity" of firms' 10-K filings."
  - (thewissen2024) "Erickson and Wang (1999) study the earnings of acquiring firms in the quarters before the announcement and agreement dates when the acquisitions are paid with acquirers' own stock."
OURS:
  - (section2.1-U1) "Disclosure theory tells us such a withholding state is not informationally empty: an informed manager may rationally withhold private information when disclosure is costly, sustaining a threshold below which information is withheld \citep{verrecchia1983}, and non-disclosure persists in equilibrium precisely because outside investors cannot distinguish a manager who is uninformed from one who is informed but silent \citep{dye1985}."
GAP: Where the exemplars allot one sentence per cited result, we pack a setup plus two cited mechanisms into one colon-and-comma chain; the discriminator is not raw length but the stacking of multiple attributions and clauses inside a single sentence, which raises the parse cost for a non-specialist.
AIM: Distribute the framing claim and each cited result across separate sentences (one study/one finding per sentence, as the exemplars do), rather than fusing them behind a single colon, so each result can be absorbed before the next.

### a2-f5  (KEPT)  [minor]
**Formal/Latinate verb and predicate choice where a plain word would serve**

EXEMPLAR:
  - (bushee2018) "He finds that firms with higher 10-K Fog have lower current earnings performance"
  - (thewissen2024) "Their results show that acquiring firms inflate earnings in the quarter before the deal announcement."
OURS:
  - (section2.1-U1) "A pending acquisition that is material to the acquirer constitutes material nonpublic information"
GAP: Against the exemplars' plain is/find/show, our elevated verbs (occupies, constitutes) and predicates (informationally empty) raise the diction a notch above the simplest end of the register without adding meaning, making the non-specialist work slightly harder to read through the wording.
AIM: Prefer the plainest verb that carries the meaning (is, has, shows), matching the exemplars' invisible connective tissue, rather than a more formal near-synonym; do not alter any claim, number, or hedge.

### a1-f2  (KEPT)  [major]
**Coined abstract metaphor-nouns for ordinary referents (sometimes coined-then-glossed)**

EXEMPLAR:
  - (ragozzino2024) "The basic idea, which mirrors the market for used cars discussed by Akerlof, is that sellers in M&A often hold better information on their own firm than buyers."
  - (ragozzino2024) "In a nutshell, Akerlof relied on the market for used cars as the context of his analysis"
  - (bushee2018) "Li [2008] uses the Gunning [1952] Fog Index to measure the "linguistic complexity" of firms' 10-K filings."
OURS:
  - (section2.1-U1) "is the organizing primitive of our analysis"
  - (section2.1-U2) "We adopt this established apparatus"
  - (section2.1-U5) "The two dimensions also run on different clocks"
  - (section2.1-U7) "It is in this deliberately bounded register that the empirical strategy of the following sections puts the pattern to the test."
GAP: Where exemplars name the thing plainly ('The basic idea... is that sellers... hold better information'), we substitute an invented abstraction ('the organizing primitive', 'this established apparatus', 'run on different clocks') that the non-specialist reader must translate back into the ordinary referent.
AIM: Refer to each thing by its plain name -- 'the central setup', 'the LM dictionary and Q&A split', 'a placebo comparison', 'the two run on different timelines', 'the gap these literatures leave', 'in this bounded way' -- conveying the identical content without the coined metaphor.

### a2-f1  (KEPT)  [major]
**Mid-sentence em-dash interruptions (parenthetical dashes that split the subject from its verb)**

EXEMPLAR:
  - (bertrand_schoar2003) "Two firms sharing similar technologies, factor, and product market conditions will make similar choices, whether or not they also share the same management team."
  - (bushee2018) "He finds that firms with higher 10-K Fog have lower current earnings performance and less persistent future earnings performance, consistent with managers using linguistic complexity to obfuscate poor performance."
OURS:
  - (section2.1-U1) "This withholding bind---material information held back while the firm keeps fielding questions---is the organizing primitive of our analysis"
  - (section2.1-U5) "the cash commitment serves the purchase itself and---mechanically---persists until it is paid at completion"
GAP: Where the exemplars deliver a claim in one straight-through declarative, we interrupt the main clause with a dashed aside and resume it, forcing the reader to buffer the subject across the insertion. The contrast is one of density: even the exemplar that uses paired dashes does so sparingly, while we make the interruption a default sentence shape.
AIM: Match the top-journal default of carrying subject-to-verb without a mid-clause dashed interruption, so the reader does not have to suspend and resume the main clause; reserve the paired-dash insertion for the rare case rather than the recurring frame.

### a1-f1  (KEPT)  [major]
**Aim/scope stated as an abstract nominalized 'move-label' instead of a plain-verb sentence**

EXEMPLAR:
  - (bushee2018) "Our goal is to show that the construct validity of linguistic complexity measures like Fog can be substantially improved"
  - (bushee2018) "We seek to recover empirical estimates of the latent variables"
  - (bertrand_schoar2003) "While our primary goal in this paper is not to distinguish between these different interpretations"
OURS:
  - (section2.1-U4) "The implication for our purpose is a locating one."
  - (section2.1-U6) "we offer it as a positioning claim about where the contribution sits"
GAP: The exemplars say the aim with a verb a non-specialist parses instantly ('Our goal is to show...'); we state it as an abstract noun phrase ('the implication... is a locating one') that must be unpacked before its meaning is clear.
AIM: State the same scope/aim point with a plain verb sentence (e.g. 'this locates where the signal must be' / 'we offer this as positioning, not a tested mechanism') rather than as a nominalized move-label, keeping the identical claim and hedge.

### a1-f3  (KEPT)  [major]
**Fronted / inverted abstract-subject sentence openers instead of plain subject-verb**

EXEMPLAR:
  - (bushee2018) "We focus on the use of complex language in conference calls, rather than in mandatory SEC filings."
  - (thewissen2024) "Prior literature extensively analyses the implication of the method of payment on managers' M&A decisions."
  - (ragozzino2024) "The theory of information economics provides important insights into the structure and functioning of exchanges in various markets."
OURS:
  - (section2.1-U2) "The venue in which this bind becomes observable is the quarterly earnings conference call"
  - (section2.1-U6) "The cell these literatures leave empty is the one this paper occupies"
GAP: Exemplars front the concrete actor and verb ('We focus on...', 'Prior literature extensively analyses...'); we front an abstract relative-clause subject and postpone the concrete noun behind an 'is', adding parsing load for no added content.
AIM: Lead with the concrete subject and verb (e.g. 'The earnings call is where this bind becomes observable' / 'This paper occupies the cell these literatures leave empty'), preserving the same meaning without the inverted abstract opener.

## MERGED-AWAY (6) — folded into a canonical (verify they truly duplicate)

### a2-f2  (MERGED -> a1-f2)  [major]
**Coined abstract nouns and neologistic labels used as the grammatical anchor of sentences**

EXEMPLAR:
  - (ragozzino2024) "The basic idea, which mirrors the market for used cars discussed by Akerlof, is that sellers in M&A often hold better information on their own firm than buyers."
  - (thewissen2024) "They suggest that M&As are a form of arbitrage by rational managers operating in inefficient markets."
OURS:
  - (section2.1-U4) "The implication for our purpose is a locating one."
  - (section2.1-U7) "It is in this deliberately bounded register that the empirical strategy of the following sections puts the pattern to the test."
GAP: The exemplars let the reader stand on familiar nouns and learn only the new claim; we ask the reader to first absorb a coined term (and our own label for it) and only then the claim, so the abstraction itself becomes an extra processing step the non-specialist must clear.
AIM: Carry the same content on plainer, already-grasped subjects rather than on coined labels, so a non-specialist parses the claim without first having to internalize a neologism.

### a3-f1  (MERGED -> a1-f2)  [major]
**Coined, metaphorical noun-phrases used as the names for the paper's own recurring analytic objects, where the exemplars name their central constructs with plain technical terms**

EXEMPLAR:
  - (ragozzino2024) "moral hazard focuses on the problem of hidden actions"
  - (bertrand_schoar2003) "agency models attribute variations in corporate behavior to heterogene-ity in the strength of governance mechanisms"
OURS:
  - (section2.1-U1) "is the organizing primitive of our analysis"
  - (section2.1-U5) "The two dimensions also run on different clocks"
  - (section2.1-U6) "This paper's nearest neighbors read deal-related language"
GAP: Our prose adds a figurative naming layer (a metaphor the reader must unpack) on top of the concept itself, where the exemplars name the concept directly. This is heavier doing the same job: each coined label is a small decoding tax that the plain term in QJE/LRP avoids, and it recurs across U1, U5, and U6.
AIM: Match the exemplars' habit of naming the analytic object with a plain, literal term rather than a coined metaphor, so a non-specialist reads the concept directly instead of first decoding the figure of speech.

### a3-f2  (MERGED -> a2-f1)  [major]
**Quantitative facts and explanatory asides dropped inside em-dash interruptions that suspend the main clause between its subject and verb, rather than being given their own sentence**

EXEMPLAR:
  - (thewissen2024) "In fact, they find that the unexpected accruals are significantly higher by 2 to 3% before the event."
  - (bushee2018) "In a conference call, analysts and investors have 30-60 minutes of interactive discussion with managers on the earnings announcement date."
OURS:
  - (section2.1-U2) "because general-purpose word lists misclassify financial text---nearly three-quarters of the Harvard dictionary's negative-word counts are attributable to words that are typically not negative in a financial context---\citet{lm2011} construct dictionaries specific to financial disclosure"
  - (section2.1-U1) "This withholding bind---material information held back while the firm keeps fielding questions---is the organizing primitive"
GAP: Suspending the main clause across a long dash-bounded aside raises the reader's working-memory load relative to the exemplars' default, which is to let the number or detail occupy its own independent sentence. This is a phrasing/density difference (not a request to cut the dash or the fact), and it recurs, so the burden is structural rather than incidental. Ragozzino uses a single dash aside, so the issue is the pervasiveness and the clause-suspension, not that a dash ever appears.
AIM: Where an em-dash insertion currently suspends the subject from its verb, follow the exemplars' default of carrying the number or aside in its own subject-verb sentence, so the main clause reads straight through.

### a3-f3  (MERGED -> a1-f1)  [minor]
**The gap / contribution statement phrased through a figurative spatial image rather than the exemplars' plain declarative contribution sentence**

EXEMPLAR:
  - (bushee2018) "Our goal is to show that the construct validity of linguistic complexity measures like Fog can be substantially improved by decomposing the measure into its latent components."
  - (ragozzino2024) "It remains for us to explicate why a shift in focus from information asymmetries between buyers and sellers in M&A markets to information asymmetries between those acquirers and their shareholders is warranted and interesting."
OURS:
  - (section2.1-U6) "The cell these literatures leave empty is the one this paper occupies"
GAP: Casting the contribution as occupying an 'empty cell' is heavier doing the same job than the exemplars' plain 'Our goal is to show...' / 'It remains for us to explicate...'; the figure adds a decoding step to a sentence whose only job is to state plainly where the paper sits.
AIM: State the gap/contribution with the exemplars' plain declarative register ('our goal is to', 'it remains to') rather than through a spatial figure, while keeping the same scope and the existing 'to our knowledge' hedge that follows it.

### a3-f4  (MERGED -> a1-f3)  [minor]
**An abstract cleft construction ('The venue in which X becomes observable is ...') to introduce the earnings call as the setting, where the exemplars introduce the same setting with a concrete subject**

EXEMPLAR:
  - (ragozzino2024) "In addition to the mandated financial performance disclosures, capital market participants also rely on voluntary quarterly earnings conference calls."
  - (bushee2018) "We focus on the use of complex language in conference calls, rather than in mandatory SEC filings."
OURS:
  - (section2.1-U2) "The venue in which this bind becomes observable is the quarterly earnings conference call"
GAP: The cleft 'The venue in which ... is the quarterly earnings conference call' is a denser way to introduce the setting than the exemplars' concrete-subject openers; it makes the reader parse an abstract relative clause before reaching the thing being named.
AIM: Introduce the call with a concrete subject in the exemplars' manner rather than an abstract 'The venue in which ... is ...' cleft, keeping the same content.

### a3-f5  (MERGED -> a1-f1)  [minor]
**A nominalized, abstract predicate ('The implication for our purpose is a locating one') in place of the exemplars' plain verbal framing of a logical move**

EXEMPLAR:
  - (ragozzino2024) "It is worth drawing a quick distinction between the two problems"
  - (bertrand_schoar2003) "These two main variants of the "managers matter" view of corporate decisions have very different efficiency implications."
OURS:
  - (section2.1-U4) "The implication for our purpose is a locating one."
GAP: 'The implication for our purpose is a locating one' packs the signposting into an abstract nominal predicate, which is denser than the exemplars' plain verbal framing of the same kind of move; the reader has to unpack 'a locating one' to recover what is otherwise a simple 'this tells us where to look'.
AIM: Render the signpost in the exemplars' plain verbal register rather than as an abstract nominalized predicate, preserving the logical point it makes.

## REJECTED (1)

### a2-f4  (REJECTED)  [minor]
**Concrete instance / plain-language gloss to ground an abstraction**

EXEMPLAR:
  - (thewissen2024) "For example, the exchange ratio is four if the acquirer agrees to exchange four of its stocks for one target firm share."
  - (ragozzino2024) "In a nutshell, Akerlof relied on the market for used cars as the context of his analysis and proposed that in a world in which buyers cannot distinguish good and bad cars, buyers either refrain from buying cars altogether"
OURS:
  - (section2.1-U1) "A firm that has privately committed to an acquisition but not yet announced it occupies a distinct \emph{disclosure state}."
GAP: The exemplars give the reader a concrete foothold (a number, a familiar market, an explicit gloss) when introducing an idea; our prose more often explains abstraction with further abstraction, offering fewer tangible anchors for a non-specialist to grab onto.
AIM: Where an abstract claim is introduced, offer a concrete instance or plain-language gloss alongside it, as the exemplars do, so the reader has a tangible handle and is not asked to follow abstraction-to-abstraction.

## REDTEAM side_notes

- Coverage gap (all three agents): every finding is sentence- or phrase-level. Inter-paragraph flow, paragraph-internal ordering, and the section's overall architecture (the P1-P7 spine) were never examined -- no agent assessed whether paragraphs are sequenced or proportioned more heavily than the exemplars.
- Surfaced inside rejected a2-f4 and preserved here for the human: the panel observed that abstract claims are sometimes introduced without a concrete foothold (number / familiar market / explicit gloss). That is a legitimate under-coverage observation, but it is a 'do more grounding' note, not a 'we are needlessly more complex' STYLE fix, so it cannot be emitted as a finding.
- Hygiene note on the U6 sentence 'The cell these literatures leave empty is the one this paper occupies': it drew three separate hits (cleft inversion a1-f3, spatial-metaphor a3-f3, positioning-claim a1-f1). a3-f3 was merged into the a1-f1 contribution/positioning cluster and the cleft example stays with canonical a1-f3, so the surviving canonicals make distinct device complaints (grammatical inversion vs. abstract/figurative contribution phrasing) rather than flagging the same sentence twice for the same reason.