# Skeleton v2 → v3 reframe — retired HK, removed reverse-engineered bridge

**Date:** 2026-04-16 evening
**Commits:** db51080 (v3), 83ffdf1 (v3.1 title tightening)

## What happened

V2 skeleton had:
- 4 formal hypotheses: HC (cash), HL (leverage), **HK (capex)**, HFC (financial constraint)
- Two-mechanism architecture: precautionary financing + competitive real options investment
- **Bridge claim:** firms "HOLD cash to DEPLOY under competition" — the precautionary cash buffer is HELD to fund competitive preemption when rivals force action
- RQ Part 2: "how does product-market competition shape investment-side expression?"

User flagged two problems in sequence:

### Problem 1: RQ Part 2 asymmetric
"the second part of the RQ about competition effect, feels force fed, since we have one other channel and its not framed as a main part."

Competition moderator tested across suites:
- H1.1 / H1.1b (competition × cash): 0/4 — competition does NOT moderate cash
- H13.1 (competition × capex): 8/8 — competition moderates capex
- HL: no competition suite
- HFC: no competition suite

So RQ Part 2 gave 50% of the question weight to a moderator that loads on 1/4 formal hyps. Asymmetric.

### Problem 2: Bridge was reverse-engineered
After multiple RQ-wording iterations that kept recreating the same asymmetry, user escalated:

> "we have a TON of data for conservatism in financing, and capex and it's channel has a totally different mechanism. so either we find a channel or explanation which can be inclusive, grounded in literature, and the RQ SHOULD NOT feel force fed, reverse engineered, or a justification attempt, rather a believable literature should drive the hypothesis developments, then to the hypothesis framing, then the results"

The v2 bridge ("HOLD cash to DEPLOY") was a theoretical synthesis constructed AFTER seeing data support both precautionary financing and competitive-capex. We stitched two distinct literatures together post-hoc. That's reverse-engineering, not literature-driven hypothesis development.

## Verification performed before the fix

Used anti-capitulation-required evidence check — re-authed NotebookLM (after Chrome kill) and ran paper-search-mcp in parallel:

1. **NotebookLM (F1D, 38 papers):** queried for "preemptive precaution" / "precautionary preemption" / "preemptive precautionary motive" / "precautionary capacity" / "precautionary investment" across Grenadier 2002, Aguerrevere 2009, AFW 2004, BKS 2009, Riddick-Whited 2009, OPSW 1999, Bernanke 1983, Bloom 2009, Dixit-Pindyck 1994.
   - Result: NONE appear verbatim. Gao-Zhao 2022 explicitly models precaution and preemption as **"competing forces battling for the firm's resources"** — direct contradictory model.

2. **paper-search-mcp (21 sources):** 4 parallel exact-phrase searches. Hundreds of papers scanned.
   - Result: ZERO hits for the 4 compound phrases. Adjacent finance hit (Aydin-Kim 2024 SSRN "Precautionary Debt Capacity") applies to DEBT not CAPEX, and isn't top-tier yet.

Advisor call also flagged: "preemption ≠ precaution motivationally. A concept that covers both ↑ and ↓ is unfalsifiable." Triangulated with the literature evidence.

See: `memory/reference_preemptive_precaution_verified_novel.md`

## Resolution (v3)

**Pattern adopted:** "Main test + documented puzzle" (advisor's suggestion after I kept looping on RQ wording).

- **Formal hypotheses reduced to 3:** HC, HL, HFC — all financing-side, all literature-driven from AFW 2004 / BKS 2009 / OPSW 1999 / Riddick-Whited 2009 precautionary motive
- **HK retired.** H13 / H13.1 / H13.2 relocated to Ch 4.4 "documented investment-margin puzzle" — empirical finding with post-hoc interpretation via competitive real options (Grenadier 2002 RFS, Aguerrevere 2009 RFS)
- **Bridge claim REMOVED.** §3.5 adds caveat: financing-investment causal/sequencing link NOT tested, separate outcome equations, any relationship discussion is theoretical not empirical
- **Single-question RQ:** "Does managerial speech uncertainty during earnings calls predict financing conservatism?"
- **Title:** "Hold On to Your Cash: Managerial Speech Uncertainty and Financing Conservatism" (v3.1 tightening from "Corporate Financial Conservatism")
- **Terminology hierarchy:** "financing conservatism" = observed pattern; "precautionary motive" = theoretical mechanism

## Patterns this incident reinforces

### Pattern B (audit first, narrative last)
I built an interpretive framework (two-mechanism bridge) before fully recognizing the data asymmetry in moderator loadings. Bridge was a narrative rescue for a sign conflict; documentation of the conflict (puzzle framing) is the honest alternative.

### Pattern C (concise, decisive, defended)
User's "feels force fed" observation triggered 3 rounds of increasingly clever RQ wording attempts on my part before advisor caught the structural issue. I should have escalated to structural question earlier instead of iterating on wording.

### New feedback captured
`feedback_literature_drives_hypotheses.md` — literature → hypothesis → framing → results flow, never backward. Rescue by relabeling is a red flag.

## Lessons for future hypothesis-development sessions

1. **When counting moderator loadings across hyps, check SYMMETRY before writing the RQ.** If a construct loads on 1/N hyps, it shouldn't be Part 2 of the RQ.
2. **When data surprises in sign:** documented puzzle + second literature beats unified coinage every time. Even if the unified concept sounds cool.
3. **When user says "feels force fed / reverse engineered":** STOP iterating on wording. Structural issue. Get advisor, get literature verification, propose architectural fix.
4. **Literature-driven hypothesis development is a first-principles check, not an afterthought.** Before stating a formal hypothesis, name the specific top-tier paper that predicts the direction. If you can't, it's not a formal hypothesis — it's a documented empirical finding.

## Artifacts produced in this session

- `docs/Draft/THESIS_SKELETON.md` — v3 → v3.1 (commits db51080, 83ffdf1)
- `docs/Draft/DraftTemplate.txt` — user added "two-column mandatory" directive (commit 556b210)
- `memory/project_thesis_skeleton.md` — v2 → v3 memory update
- `memory/project_capex_reframe.md` — marked SUPERSEDED (v2 two-mechanism bridge)
- `memory/project_capex_documented_puzzle.md` — new, CURRENT state
- `memory/reference_preemptive_precaution_verified_novel.md` — new, prevents re-search
- `memory/feedback_literature_drives_hypotheses.md` — new, process rule
- `memory/MEMORY.md` — index updated
- This incident log
