# Proposition-Chain Referee Audit — SPEC (2026-06-26)

Single source of truth for the harness-led referee audit of the Phase-3 masking proposed-fixes.
Audit-only: finds problems + proposes a fix **in the artifact**; applies nothing. Prose comes later.

## Goal
Referee-simulate the **whole proposition chain** — all 16 sections, masking fixes APPLIED to a throwaway
corpus, read as ONE ordered corpus — and emit ONE `audit.json` of confirmed problems, each with an
investigated, redteam-hardened proposed fix. Judges the LOGIC supporting the findings, not the prose.

## Pipeline
```
0  build ONE compact corpus = 16 chains, fixes APPLIED, thesis order        [code, no agent]
     + evidence appendix (NLM verbatim, keyed by prop_id)
     + provenance tags per prop/field: ORIGINAL-locked | ADDED | REWORDED | SWEPT
   GATE-0  deterministic corpus verify (below) MUST pass before any agent runs
1  SMOKE  run dimension #4 (overclaim/honesty-floor) ALONE on full corpus;
          read its COMPLETE output; confirm corpus+prompt+schema produce real findings
2  6 auditors · 1 dimension each · all read the corpus → 6 reports
3  2 redteams × 3 reports → confirm/reject/dedup each finding + VALIDATE each proposed fix
4  merge → ONE audit.json (group by locus; adjudicate conflicts)            [code, no agent]
```

## The 6 dimensions (each reads ALL 16 sections)
| # | dimension | catches |
|---|---|---|
| 1 | logic | prop doesn't follow from its evidence; broken `depends_on`; non-sequitur |
| 2 | coherence | §1↔§2.1↔§5 contradictions; masking framed inconsistently across sections |
| 3 | cite-redundancy | over-repeated cite; prop that references without adding; useless cross-ref |
| 4 | overclaim / honesty-floor | claim exceeds evidence; honesty-floor / register_lock breach |
| 5 | evidence-sufficiency | recorded verbatim doesn't actually support the statement |
| 6 | completeness | a finding (C1/C2/C4/C6) with no supporting prop; orphan claim |

## BLOCKER 1 — Honesty floor = PROTECTED bright lines fed to EVERY agent
A "find weaknesses + strengthen" agent is structurally biased to flag deliberate hedges as problems and
"fix" them into overclaim — the exact failure the thesis avoids. So every agent is told: these are bright
lines a fix may NEVER cross. "Stronger" never means "more than the evidence."
- masking = **MOTIVATION, not mechanism / not identification**
- **NO "stock suppressed"** — stock −0.0429 n.s. (noisy flat null); the gap is **cash rising**
- cite **Shleifer-Vishny + Louis as EARNINGS/VALUATION, NEVER tone**; thewissen = tone (preprint, supplementary)
- **source** mechanism (compliance-constrained vs strategic) stays **OPEN**
- **war-chest / cash-accumulation CAUSE** stays **OPEN** (C6 cause 0.0064 n.s.)
- concentration = motivated, NOT identified; correlational, within-firm, no causal id
- concentration-not-strict-specificity · "we interpret, we do not detect"
- each ledger's own `register_locks` are bright lines for that section.
A finding that asks to harden/remove a bright-line hedge is itself INVALID → redteam must REJECT it.

## BLOCKER 2 — GATE-0: verify the corpus before the panel (apply-bug = 8 agents audit garbage)
Deterministic, cheap, run by the corpus-build script; abort the run on any failure:
- every fix `from` string matched exactly in its locus (applied count == proposed count)
- prop count conserved: original props + ADD_PROPs == corpus props
- no `prop_id` referenced in any `depends_on` is missing (no orphan)
- identifier tokens intact: `tab:empire_drop_placebo`, `placebo_cash_PRE1`, `placebo_stock_PRE1`
- no `comparison_cash_PRE1` / `comparison_stock_PRE1` / `empire_drop_comparison` corruption
(This GATE doubles as the apply-step dry-run.)

## Schema A — corpus item (STEP 0 output; what agents read)
```json
{ "order": 12, "section": "2.1", "para_id": "P5", "prop_id": "P5.5",
  "provenance": "ADDED",                         // ORIGINAL-locked | ADDED | REWORDED | SWEPT
  "type": "framing-nonverifiable",
  "statement_applied": "…the prop as it reads AFTER the fix…",
  "statement_original": "…only for REWORDED/SWEPT; else null…",
  "role_in_paragraph": "…", "reason": "…",
  "register_locks": ["…"], "depends_on": ["P5.4"],
  "cite_keys": ["shleifer_vishny2003"], "numbers": ["…"],
  "evidence_ref": ["appendix:P5.5"] }              // verbatim quotes live in the appendix
```

## Schema B — auditor finding (one per problem; auditor fills, redteam appends)
```json
{ "id": "OV-01", "dimension": "overclaim", "severity": "critical|major|minor",
  "locus": { "section": "2.1", "prop_id": "P5.5", "field": "statement" },
  "issue": "…what's wrong, concretely…",
  "evidence": "…verbatim from the prop / cross-ref proving it…",
  "rule_broken": "…honesty-floor line / register_lock / logic rule…",
  "proposed_fix": { "action": "REWORD|DROP|ADD|MERGE", "from": "…", "to": "…", "why": "…" },
  "confidence": "high|med|low",
  "redteam": null }
```

## Schema C — redteam verdict (appended into each finding's `redteam`)
```json
"redteam": {
  "by": "redteam-A", "verdict": "CONFIRMED|REJECTED|DOWNGRADED|UPGRADED|DUPLICATE",
  "verdict_reason": "…adversarial…",
  "fix_check": { "honesty_floor": "PASS|FAIL", "evidence_still_supports": "PASS|FAIL|N/A",
                 "verdict": "SOUND|HARDENED|WRONG", "hardened_to": "…better fix if weak…" },
  "duplicate_of": "EV-03|null" }
```
Redteam MUST validate the proposed FIX itself (a fix is an unverified claim): does it cross a bright line?
does the statement still match its recorded NLM evidence after the reword? A REJECTED-bright-line finding
is dropped from the artifact.

## Schema D — final audit.json (STEP 4, code merge)
```json
{ "meta": { "run_id": "…", "corpus_props": 0, "agents": "6+2", "gate0": "PASS" },
  "summary": { "critical": 0, "major": 0, "minor": 0, "by_dimension": {} },
  "problems": [ /* Schema-B objects with redteam filled, confirmed-only, deduped */ ],
  "conflicts_adjudicated": [ { "locus": "…", "chosen": "OV-01", "alternatives": ["LG-04"] } ] }
```

## Merge + conflict resolution (STEP 4)
Group findings by `locus` (section+prop_id+field). Identical loci → dedup (keep highest severity, union evidence).
**Contradictory** fixes at one locus (e.g. DROP vs REWORD, possibly across the two redteams) → ONE small
adjudication pass picks the single fix; losers become `alternatives`. Two contradictory fixes never both ship.

## Inputs per agent
- ALL agents: the corpus (Schema A) + the BLOCKER-1 bright-lines block.
- evidence (5), overclaim (4), cite-redundancy (3): + the evidence appendix (NLM verbatim).
- completeness (6): + `claim_findings_ledger.json` (C1/C2/C4/C6) to confirm each finding has props.
- redteams: their 3 reports + corpus + appendix + bright-lines.

## Redteam grouping
- redteam-A ← reports {1 logic, 2 coherence, 6 completeness}   (structural)
- redteam-B ← reports {3 cite-redundancy, 4 overclaim, 5 evidence}  (evidence/claim)

## Trees
Clones + corpus + audit.json live in `F1D-phase3/docs/Thesis/rewrite/` (`_phase3_clones/`, `_audit/`).
Workflow runs from `F1D` cwd (data + `f1d` pkg); agents read the fork by absolute path.

## Status
SPEC drafted, advisor-vetted (blockers 1+2 folded). NEXT: build STEP-0 corpus script → GATE-0 → smoke #4 → fan out.
