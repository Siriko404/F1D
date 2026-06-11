# Novelty lit-check — OpenAlex/pyalex (2026-06-06)

**Question:** has any prior work shown the *acquirer's earnings-call linguistic
uncertainty rises anticipating an undisclosed (cash) deal and resolves at
announcement* — under ANY measure?

## Methods (multi-method, high-recall)
1. 18-query relevance sweep → 660 unique works. Tier1 (deal×call×lang) = 0 — but
   **bad recall** (missed DWZ/Mayew/Larcker), so this null was NOT trusted.
2. **Forward-citation screen** of 5 canonical call-language seeds — DWZ
   (W2612664114 +3 variants), Bushee-Gow-Taylor (W2750514253), Mayew-Venkatachalam
   (W2075051605), Larcker-Zakolyukina (W2313384944), Loughran-McDonald
   (W2152136804). ~2,600 citers; **67 mention M&A/deal terms.**
3. Hand-screened the 11 closest (channel×deal) abstracts.
4. Crossref backfill + full DWZ-variant citer screen.

Raw: tmp/litcheck_openalex_results.json, tmp/litcheck_citenet_results.json.

## Verdict: NOVELTY SURVIVES for the specific contribution — but narrow the claim.

**No prior establishes our phenomenon.** The DWZ *residual* measure has never been
applied to deals (across all 4 DWZ records, only one tangential citer: "Appraisal
rights and corporate disclosure during M&A," 2022).

**BUT an adjacent cluster EXISTS — must cite + distinguish (do NOT claim "first to
link M&A and call language"):**
- Deal-**announcement** calls: "What's really in a deal?" (2021 RFE); "Voluntary
  Disclosure to Influence Investor Reactions to Merger Announcements" (2010 TAR,
  164c). → the call that *announces* the deal; market-reaction focus. NOT anticipatory.
- Acquirer disclosure around/after deals: "International Corporate Development…
  Earnings Calls" (2025 MIR) — M&A augments call info-asymmetry; "Impact of M&A on
  Acquiring Firm Voluntary Disclosure" (2025). → disclosure *levels*, not anticipatory
  residual-uncertainty timing.
- Stock-deal tone-inflation: "Manipulating Disclosure Tone: Acquiring Firms'
  Strategies in Stock-for-Stock M&A" (2024). → TONE (not uncertainty), STOCK arm
  (our placebo), prop-the-currency motive (different mechanism).

**What is genuinely NEW (the defensible claim):**
- the **anticipatory disclosure-state timing** (uncertainty rises in the secret
  pre-announcement window, collapses at announcement) — no prior does this event study;
- applying the **DWZ residual** speech-uncertainty measure to deals (never done);
- **cash-specificity** vs the stock placebo.

→ Headline must be "call *residual uncertainty* anticipates undisclosed deals /
tracks the disclosure state," NOT "previously-unrecognized that M&A affects call
language" (that's known).

## Gate paper READ IN FULL (2026-06-06) — CLEARED
"Implications of M&A for information disclosures in earnings calls" (Ragozzino &
Reuer, 2024 *Long Range Planning*; docs/papers/1-s2.0-S0024630123001000-main.pdf)
— the single closest title. Read pp.1-9 (abstract→methods→results). **Does NOT
scoop us:**
- Measure = *volume* of corporate-strategy DICTIONARY keywords (Feldman 2020:
  ACQUIRE/MERGE/DIVEST…) spoken by analysts + executives — a topic-coverage
  quantity, NOT linguistic uncertainty. We use the DWZ residual *uncertainty*.
- Timing = TRAILING 5-year M&A activity (already-public/ongoing deals) →
  contemporaneous strategy discussion. NOT the anticipatory pre-announcement
  secret window; no disclosure-state event study; no announcement-time collapse.
- Mechanism = adverse selection insiders↔shareholders → MORE strategy disclosure
  + analyst questioning. Ours = MNPI gag → MORE vagueness in the secret window.
- Design = PSM active-vs-inactive + keyword Tobit + forecast-error OLS. No
  cash-vs-stock placebo, no event-time bins.
→ ADJACENT cluster, perfect cite-and-distinguish anchor (shares Seeking Alpha
data). Novelty (reframed: anticipatory residual-uncertainty timing + cash
concentration) SURVIVES.

## The other 3 closest — ALL READ IN FULL (2026-06-06) — none scoops us
1. **Everhart, Kravet, McVay & Warren (2025), "The Impact of M&A on Acquiring
   Firm Guidance"** — DV = management EARNINGS GUIDANCE (issuance / precision /
   accuracy), 2yr around deal. M&A↑ fundamental uncertainty → guidance less
   precise. NOT call speech uncertainty; quantitative guidance, around/post-deal.
   (They too null-test withdrawn deals.) → adjacent, distinct. Cite.
2. **Gokkaya, Liu & Stulz (2025), "Is there information in corporate acquisition
   plans?"** — PUBLICLY ANNOUNCED acquisition plans → market reaction + predicts
   deals. DISCLOSED intentions (opposite of our undisclosed window); measure =
   abnormal return/turnover, not linguistic uncertainty. → distinct. Cite.
3. **Thewissen, Yan, Arslan-Ayaydin & Yan (2024), "Manipulating Disclosure Tone:
   Acquiring Firms in Stock-for-Stock M&A"** — THE CLOSEST. Shares the
   *acquirer pre-announcement (4-5 qtrs before) disclosure-language* frame. BUT:
   TONE/optimism (Henry 2008), EARNINGS PRESS RELEASES, **STOCK** deals (our
   placebo), motive = inflate tone to prop the stock currency & cut target cost.
   Mirror-image of us (CASH + UNCERTAINTY + MNPI-gag). NOT a scoop — complementary.

## Thewissen CERTAINTY — full 62-page extraction (2026-06-06)
Re-read all 62pp (tmp/thewissen_fulltext.txt) + keyword grep. Confirmed NOT a scoop:
- MEASURE = TONE only (Henry 2008 pos−neg; LM 2011 used only for pos/neg robustness).
  "uncertain" 2× incidental; Dzielinski/Zeckhauser/DWZ = ZERO; fog/vague/hedge = ZERO.
  ("residual" = their abnormal-tone AbTone + Heckman GENRES, not a DWZ uncertainty residual.)
- CHANNEL = earnings PRESS RELEASES (89×). "earnings call"/"Q&A" = ZERO; conference
  calls explicitly FILTERED OUT (p17). We use call Q&A.
- TREATMENT = stock-for-stock only; CASH deals explicitly NULL on tone (p7, p23:
  "tone of earnings press releases of cash deals does not significantly change").

Clean 2x2 (complementary, non-overlapping):
                TONE (sentiment)      UNCERTAINTY (vagueness)
  STOCK deal    ↑ Thewissen           flat (our placebo)
  CASH  deal    flat (Thewissen)      ↑ US  <- the empty cell we fill

## Positioning implications (load-bearing for the writeup)
- Do NOT claim "first to show acquirers manage pre-announcement disclosure" —
  Thewissen has that for stock+tone. Our novelty = the UNCERTAINTY channel, CASH
  deals, disclosure-state timing (rise→collapse at announcement), DWZ residual.
- Cash-vs-stock placebo is STRENGTHENED but must be stated precisely: stock is a
  placebo *for the uncertainty channel* (stock UncRes null) — NOT "stock bidders
  do nothing pre-announcement" (Thewissen: they inflate TONE). Cite Thewissen so
  the placebo isn't naive.
- Robustness to add when writing (referee will ask): control for / distinguish
  TONE from uncertainty in the cash run-up. Flag only; no re-estimation now.

## Coverage boundary (disclosed, not silently capped)
NOT run (advisor: lower-probability, stop after gate): citer screen of
working-paper variants of BGT/Mayew/Larcker/LM; non-citation keyword sweep
(strategic silence / quiet period / MNPI). A phenomenon prior would almost
certainly cite an LM/BGT/Mayew seed (already screened).

## NLM direct-query verification (2026-06-06) — both MUST-cite papers, gate CONFIRMED
Queried the two closest papers DIRECTLY via the `notebooklm` CLI (f1d notebook
63e3b970…), 8 atomic exploratory prompts × 2 papers, each source-scoped (`-s`)
with `clear` between calls for self-containment. Harness: tmp/nlm.py; raw:
tmp/nlm_verification.json. Both papers, asked directly, EXPLICITLY disclaim any
linguistic uncertainty/vagueness/hedging measure (verbatim-cited):

- **Thewissen 2024** (src 731d56ed…): measure = tone (Henry 2008; AbTone =
  residual of *expected tone*, Eq 7; ARF tone dispersion). Channel = earnings
  PRESS RELEASES (8-K Item 2.02); "earnings call"/"Q&A" = 0, "press release" = 87, "conference call" = 2
  (incidental — the exclusion mention); this-session grep of
  tmp/thewissen_fulltext.txt. NOT a call-transcript study. (Caution: their methods
  drop non-earnings 8-K *notices* incl. call announcements; that is 8-K-type
  filtering, not evaluating-then-excluding call transcripts — do NOT rest the
  distinction on "they excluded calls"; rest it on the 0-occurrence grep fact.)
  Sample 302 stock / 1,168
  cash / 4,088 hybrid; "tone of cash deals does not significantly change" (cash =
  null control). Timing anticipatory (peaks Q−2) for STOCK. Mechanism = hype
  stock to cut the exchange-ratio cost. Corroborates the earlier full-text grep.
- **Ragozzino-Reuer 2024** (src f84c6cd2…): measure = Feldman (2020)
  corporate-strategy KEYWORD intensity + transcript length. Channel = earnings
  CALL transcripts (shares OUR channel). Method of payment NOT analyzed (cash-vs-
  stock = their stated future work). Timing TRAILING (M&A in the 5yr/1yr BEFORE
  the call). Mechanism = adverse selection insiders↔shareholders → more disclosure.

**Ragozzino absence grep-backed** (advisor: for an absence claim a clean NLM "no"
is the trigger to grep, not grounds to skip; + it is the title-collision paper).
Full 18pp extract (tmp/_ragozzino_extract.py → tmp/ragozzino_fulltext.txt):
loughran/mcdonald/dzielinski/dwz/residual/abnormal/fog/vague/modal/sentiment = 0;
"uncertain" = 2 incidental (crisis confound; Akerlof title); tone/hedg/optimis =
others' work / "hedge fund" / a ref title. Measure = feldman/keyword/dictionary
(2/15/25). NLM-absence → verbatim-absence.

**Positioning refinement (honest):** Ragozzino shares our CHANNEL (calls);
Thewissen shares our anticipatory FRAME. Novelty rests on MEASURE (residual
uncertainty) + CASH + anticipatory timing — NOT on "studying call language around
deals" (do not overclaim the channel).

**Locked gap (Q1, hedged):** "To our knowledge (5-seed forward-citation screen,
coverage boundary disclosed), acquirer earnings-call linguistic UNCERTAINTY around
M&A is unmeasured; adjacent work measures tone (Thewissen) or strategy-keyword
volume (Ragozzino-Reuer), in stock deals or trailing activity. Contribution =
APPLYING a residual call-uncertainty measure to deals (anticipatory,
cash-concentrated). DWZ residual = borrowed tool, not the novelty pillar."

**Locked distinguishing sentences:**
- Thewissen: anticipatory acquirer disclosure mgmt, orthogonal — tone (Henry;
  AbTone = residual of expected tone), earnings press releases (8-K 2.02;
  "press release" x87, "earnings call"/"Q&A" = 0, this-session grep), stock deals (cash = their null). We do
  call-Q&A uncertainty in cash — the complementary cell their cash-null leaves.
- Ragozzino-Reuer (EXTENSION framing, not deficit): they ESTABLISH that M&A
  activity raises analysts'/executives' ATTENTION to strategy on calls (Feldman
  keyword volume, trailing 5yr); we EXTEND the call-language lens to a different
  construct — residual UNCERTAINTY — in the anticipatory pre-announcement window.
  (Their text carries no uncertainty/tone construct: LM/DWZ/modal/fog/residual =
  0, full-text verified — stated as scope, not as a deficit of their work.)
