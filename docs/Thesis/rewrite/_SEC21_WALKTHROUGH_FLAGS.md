# §2.1 sentence-by-sentence walkthrough — flags for later

Running list of issues raised while reading the §2.1 prose with the author.
Nothing here is edited yet; these are parked for a later decision pass.

## FLAG 1 — graded materiality vs binary treatment (¶1, sentence 2)
- Prose grounds the disclosure state in *Basic* (1988): materiality = probability of
  consummation × magnitude to the firm, and can attach "well before any definitive agreement."
- BUT the empirical design never measures or conditions on either. Every pre-announcement
  quarter is treated as equally "bound" via a single 0/1 indicator (PreAnnounceQtr, e=-1).
- Tension: the bind is graded in law, uniform in the design. Whether each deal was actually
  material/probable at e=-1 is assumed, not verified.
- Editorial option (smaller fix): trim the balancing-test detail to just "can be material
  well before a definitive agreement" — keeps the early-materiality grounding, drops the
  prob×magnitude machinery the paper never uses.
- Status: PARKED (user: flag for later).

## Walkthrough progress (durable, for resume)
- Activity: reading the §2.1 prose sentence-by-sentence WITH the author (Sina), ultra-terse,
  ONE sentence per turn, quote-then-plain. He drives with "go"/"next".
- Source of truth for the prose: thesis_draft_uottawa.tex lines 170-182 (the seven §2.1 paragraphs,
  inline). Quote VERBATIM, render \citep as author-year, --- as em-dash, NO ellipsis / NO trimming.
- Covered so far: P1 (the bind), P2 (venue + LM uncertainty word list), P3 (Dimension 1 = timing).
  P4 SKIPPED (residual/persistent-style; one-line summary only). P5 (cash = Dimension 2) reached
  S1-S4 (claim / cash-vs-stock difference / Harford / the fence).
- NEXT (user instruction): RESTART §2.1 from the very beginning, sentence by sentence, verbatim.
- Format that works for him: short, one idea, a small visual; stop-and-check each sentence.

## Agent analysis from this session (NOT ratified -- Sina still working through it)
- Where cash enters: ¶1-¶4 build Dimension 1 (timing) with NO cash. Cash is a SEPARATE second
  dimension introduced fresh at ¶5, justified ONLY as a design contrast (stock = same disclosure
  bind, minus cash). Ledger P1 boundary literally says "No cash yet (P5)."
- "Why cash" is intentionally open. The §2.2 design ledger rule: hypotheses are "WHERE/WHEN, never
  WHY"; locks "EFFECT not CAUSE", "concentration not strict specificity", "mechanism open". The
  tempting behavioral why ("visible cash -> analysts probe -> CEO hedges") is the analyst-scrutiny
  confound that Section 4.1 rules out, so it cannot be asserted in 2.1.
- H1a is NOT deduced from a mechanism; it is a falsifiable SIGN RESTRICTION (cash run-up > stock
  run-up) that the stock placebo can refute. The "reason to suspect" = the single asymmetry in ¶5
  S2 (a cash bid draws on an accumulated cash position; a stock exchange need not). That motivates
  the guess; it does not prove a cause.
- The cash-hoarding worry, examined against the findings: cash IS elevated one quarter before the
  deal (CashRatio PRE1 = 0.0061**, sec34 §3.3) -- which is WEAKLY CONSISTENT with some pre-positioning,
  so Sina's instinct is PARTLY RIGHT, not wrong. What we CANNOT show is that the build-up is
  cash-SPECIFIC: the cause-leg test (cash-minus-stock difference in the cash ratio) is NOT significant
  = 0.0064 n.s. (matched), 0.0092 p<.10 (full panel), §3.4. CAREFUL: a null FAILS TO ESTABLISH
  cash-specificity; it does NOT confirm the build-up is non-deal-specific (absence of evidence, not
  evidence of absence -- the same discipline §4.1 uses for scrutiny). So ¶5 S4's fence ("not that firms
  stockpile to fund planned acquisitions") is CONSERVATIVE CAUTION, not a finding our data confirms;
  the thesis correctly stays "mechanism left open." Bottom line, matching the prose: EFFECT
  (uncertainty) is cash-specific (diff 0.0983, p=.039); CAUSE (cash build-up) is NOT established and is
  LEFT OPEN.
