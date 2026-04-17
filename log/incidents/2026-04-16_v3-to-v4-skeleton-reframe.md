# Skeleton v3 → v4 reframe — exploratory capex, drop appendix dump, refine HFC

**Date:** 2026-04-16 evening (later than the v2→v3 reframe earlier same day)
**Skeleton file:** `docs/Draft/THESIS_SKELETON.md` overwritten v3 → v4
**Walkthrough record:** `docs/Draft/REFERENCE_STACK_WALKTHROUGH.md` Steps 4-5 + v4 re-scoping summary

## What happened

Step-by-step reference-stack walkthrough surfaced multiple structural decisions that propagated into a full skeleton v4 rewrite. The core changes: capex reframed from "puzzle" to "exploratory," 37-suite appendix dropped, payout §4.5 moved to appendix only, R&D dropped, MW year corrected to 2001, FP 2006 binary disclosed.

## Sequence of decisions

### 1. Step 1 (DWZ + BGT) — co-foundational verification
- User challenge: "I remember identifying our mgr following BGT" — initial attribution to DWZ alone was wrong.
- Verified via Ian Gow's public replication code at `github.com/iangow/bgt` + our pipeline `build_linguistic_variables.py:509-606` self-attribution to BGT 2018.
- Outcome: DWZ 2021 + BGT 2018 co-foundational for IV construction (DWZ wordlist + BGT pooling).

### 2. Step 2-3 (OPSW + BKS) — DV form clarification
- Discovered our `cheq/atq` DV matches BKS 2009 primary specification exactly (verbatim p.1991).
- BKS 2009 explicitly rejected OPSW's `ln(cash/(assets-cash))` form (p.1998-1999) — our choice is the modern standard.
- User probed: "why not OPSW definition?" → defended via 5 grounds (advisor-confirmed).
- User probed: "do we need to cite OPSW?" → kept both per advisor: theory anchor (OPSW) + method anchor (BKS) is convention pattern.
- Future work flagged: OPSW log-DV robustness appendix if time permits.

### 3. R&D + appendix decision (user pivot)
- User: "if RD is null, why are you including it in the additional analyses? our additional analyses must be macro, market, and capex + its channel"
- User: "we are not going to append the entire 37 tables as appendix!! the RD is dropped"
- Triggered re-examination of §IV structure + appendix scope.

### 4. Payout fit check (user adversarial)
- User: "does it fit to our financing conservatism narrative?"
- Investigation: main IV UncAnsMgr 0/12 NULL on payout. Only UncPreMgr (presentation channel) loads 6/6 sig.
- User rule established: "If something doesn't fit cleanly within the theoretical frame, we must either include it as additional analyses and/or the methodology section, OR drop it completely if it looks like a headache more than value."
- Applied: payout = headache > value → moved §4.5 to appendix only. Drop "Pres/Q&A decomposition" Ch 1 contribution claim.

### 5. Capex framing pivot (user)
- User: "remember, dont frame capex as puzzle. present it as exploratory tests we did, and the channel which explains it, in the additional analyses section."
- Major reframe: §4.4 "documented investment-margin puzzle" → "exploratory additional analysis with competitive real options interpretation."
- Eliminates need for capex↓ counter-prediction anchor → AFW 2004 dropped, Bloom 2014 demoted/dropped.

### 6. Advisor flagged 2 blockers + 3 optimizations
- BLOCKER 1: central claim still carried puzzle language — rewrote.
- BLOCKER 2: pre-commitment statement must distinguish §III/§IV statistical conventions — added §2.1.
- OPT 3: drop Bloom 2014 entirely (speech vs macro lineage) — applied.
- OPT 4: demote Aguerrevere 2009 to Tier-2 citation-only — applied.
- OPT 5: commit v4 skeleton to file before drafting — applied (overwrote v3).

### 7. MW + FP newly uploaded by user → batched verbatim query
- User uploaded MW 2009 (turned out to be MW 2001 per NotebookLM source) + FP 2006 to F1D.
- Single batched query returned both papers' verbatim cleanly.
- Critical findings:
  - MW year = 2001 (not 2009 as memory had said) — corrected throughout
  - MW mechanism = financial slack / Donaldson-Myers, NOT precautionary motive — disclosed split
  - **FP 2006 use BINARY (rated vs unrated), NOT three-way (IG/BelowIG/Unrated)** — our H1.2 deviates and must disclose extension
  - FP say "credit constrained" not "capital constrained" — corrected throughout v4

### 8. User decisions on H1.2 BelowIG + terminology
- User: "we wont report belowIG variable, since its null. we have the unrated significance, which is the main one according to the reference paper"
- Outcome: H1.2 reports IG (0/4 baseline) vs Unrated (4/4 sig) only; BelowIG (0/4 null) suppressed to appendix.
- Confirmed: switch from "capital constrained" to "credit constrained" wording per FP 2006.

## Files affected

### New memory files
- `memory/reference_grenadier_2002_verbatim.md` (7 quotes, earlier today)
- `memory/reference_aguerrevere_2009_verbatim.md` (3 quotes, earlier today)
- `memory/reference_opsw_1999_verbatim.md` (7 quotes)
- `memory/reference_bks_2009_verbatim.md` (7 quotes)
- `memory/reference_minton_wruck_2001_verbatim.md` (5 quotes)
- `memory/reference_faulkender_petersen_2006_verbatim.md` (5 quotes)
- `memory/project_capex_exploratory.md` (v4 capex framing)
- `memory/feedback_credit_vs_capital_constrained.md` (terminology rule)

### Updated memory files
- `memory/project_thesis_skeleton.md` — v3 → v4 (overwrite)
- `memory/project_capex_documented_puzzle.md` — marked SUPERSEDED
- `memory/project_notebooklm_papers.md` — 38 → 40 papers (added MW + FP)
- `memory/MEMORY.md` — index updated for new entries

### Thesis draft files
- `docs/Draft/THESIS_SKELETON.md` — overwritten v3 → v4
- `docs/Draft/REFERENCE_STACK_WALKTHROUGH.md` — major append (Steps 4-5 + v4 re-scoping)

### Pending pipeline change
- `src/f1d/econometric/run_h1_2_cash_constraint.py` — H1.2 BelowIG row suppression in display (T53 pending)

## Reference stack changes (v3 → v4)

### Tier-1 KEEP (8 papers, all in F1D, all verbatim done)
1. DWZ 2021
2. BGT 2018
3. OPSW 1999
4. BKS 2009
5. MW 2001 (year corrected from 2009)
6. FP 2006 (binary; we extend to 3-way)
7. Grenadier 2002
8. Hoberg-Phillips 2016 (PENDING Step 6)

### Tier-2 (citation-only, no verbatim writeup)
- Aguerrevere 2009 (demoted from Tier-1)
- Hassan 2019 (PRisk)
- BBD 2016 (US EPU)
- Davis 2016 (GEPU)
- CI 2022 (GPR)
- Amihud 2002 (ILLIQ)
- Wang 2020 (DISP)
- Chang-Dasgupta-Hilary 2006 (external fin H19b)
- LZ 2012 (CEO speaker ID)

### DROPS
- AFW 2004 (was puzzle anchor; exploratory framing eliminates need)
- Bloom 2014 (load-bearing role removed; speech vs macro lineage distinct)
- Han-Qiu 2007 (redundant with OPSW/BKS)
- Riddick-Whited 2009 (redundant with OPSW/BKS)
- Strebulaev-Yang 2013 (redundant with MW)
- Myers-Majluf 1984 (textbook citation only)
- FHP 1988 (redundant with FP 2006)
- Bernanke 1983 (not needed for exploratory framing)
- Dixit-Pindyck 1994 (covered by Grenadier)
- Leary-Roberts 2005 (not needed; temporal asymmetry described in prose)
- JJL 2021 (R&D dropped from thesis)
- Duong 2024 (was §4.5 supporting; §4.5 in appendix only)

## Patterns this reinforces

### Pattern A — don't delegate understanding
Three primary-source verifications drove decisions:
- Ian Gow's BGT replication code (verified pooling)
- Our pipeline's `cash_holdings.py` (verified DV formula matches BKS not OPSW)
- FP 2006 verbatim (revealed binary not 3-way; "credit constrained" not "capital constrained")
Without primary-source reads, all three would have been wrong-attributions.

### Pattern B — audit first, narrative last
Capex puzzle framing (v3) was a narrative built before considering whether the data fit cleanly. v4 exploratory framing acknowledges that capex doesn't fit precautionary cleanly + presents it neutrally. User's "fits cleanly OR additional OR drop" rule (2026-04-16) is Pattern B distilled.

### New rule captured
`feedback_credit_vs_capital_constrained.md` — terminology discipline derived from FP 2006 verbatim.

## Lessons for future sessions

1. **Year-claim verification:** when memory says "Author Year," verify against source (MW year-flag caught only because NotebookLM cited 2001 directly).
2. **Method-paper vs theory-paper split:** standard in finance; cite both, attribute roles separately. OPSW/BKS, MW/precautionary, FP-binary/we-extend — same pattern recurring.
3. **User's "fits-cleanly OR additional OR drop" rule:** apply systematically to every additional analysis component before writing. Headache > value = drop, even if pipeline investment exists.
4. **Pre-commitment statement is the modern p-hacking defense.** Front-load §II with explicit statistical convention disclosure. 37-suite fishing-deck appendix is one option but not the only one.
5. **Exploratory > puzzle when the data doesn't fit primary theory.** Less defensive overhead, more honest epistemic positioning, fewer required citations.

## Related

- `log/incidents/2026-04-16_skeleton-v2-to-v3-reframe.md` — earlier same-day reframe (v2 bridge → v3 puzzle)
- `log/incidents/2026-04-16_capex-framing-fold-under-pushback.md` — earlier capex fold incident
- `feedback_literature_drives_hypotheses.md` — related process rule
- `feedback_credit_vs_capital_constrained.md` — new terminology rule from this session
