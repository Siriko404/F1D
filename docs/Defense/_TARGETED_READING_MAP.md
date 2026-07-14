# Defense Redesign — Conservative Targeted Reading Map

Last updated: 2026-07-13

## Purpose

Use this map to avoid rereading all three long source files for every small task.
It is intentionally conservative: each bundle includes contextual overlap, and every
substantive task requires reading from all three files.

This map does not replace the canonical handoff ledger. After compaction, read
`_CURRENT_HANDOFF_LEDGER.md` first, then use the relevant bundle below.

## Source lock

The line ranges below are valid only for these exact files and hashes:

| Code | File | Lines | SHA-256 |
|---|---|---:|---|
| T | `docs/Thesis/_uottawa_rewrite/_thesis_FLAT.tex` | 1,621 | `6F2E003FF63EEBB23BED8FE26DBD1601D0B5392A6628320D8782F60D5F936310` |
| M | `docs/Defense/DEFENSE_PRESENTATION_MASTER_REFERENCE.txt` | 1,651 | `6C2D772CDC0FC9482FCB815C10923F936089D62B329B2DB5781BFFFA536328F1` |
| A | `docs/Defense/2026-07-13-master-reference-audit-report.md` | 429 | `50BF843D9DF16822E9F3616166697A05A8EDD89CDAAC43F22FAAF9D06415A499` |

If any hash changes, treat the affected line ranges as stale and refresh this map
before relying on them.

## Reading rules

1. Read the canonical ledger before selecting a bundle.
2. For every substantive task, read the **Always-on baseline** and the relevant
   task bundle. Do not omit T, M, or A.
3. When a task spans multiple topics, take the union of their ranges.
4. For any numerical claim or plot, read both the thesis prose and the complete
   corresponding table, including its notes.
5. For any wording not clearly supported inside the assigned thesis ranges, expand
   to the complete surrounding thesis section. If ambiguity remains, search the
   entire thesis before drafting the claim.
6. The thesis remains empirical authority. The master is historical input; the audit
   supplies corrections and design guardrails.
7. A full-file reread is still required after major source revisions, for a new
   end-to-end audit, or when several sections interact in a way this map does not
   cover safely.

## Always-on baseline — read for every content decision

| Source | Required reading | Why |
|---|---|---|
| T | 121–186; 365–380 | Abstract, introduction, findings, contributions, boundaries, conclusion, limitations |
| M | 30–100; 1,162–1,210; 1,630–1,647 | Historical big picture, wording guardrails, final remembered message |
| A | 8–27; 79–140; 141–187 | Executive verdict, critical corrections, whole-story findings |

## Task bundles

### 1. Narrative architecture, timing, or whole-deck storyline

| Source | Required reading |
|---|---|
| T | 167–251; 258–380 |
| M | 182–247; 1,039–1,210; 1,550–1,647 |
| A | 29–78; 141–187; 304–331; 394–423 |

Use for: choosing the defense spine, narrative acts, slide count, time allocation,
result priority, and the final takeaway.

### 2. Title, opening, disclosure setting, research gap, or contribution

| Source | Required reading |
|---|---|
| T | 55–60; 121–135; 167–207 |
| M | 1–179; 247–408; 1,465–1,492; 1,588–1,600 |
| A | 29–78; 92–127; 167–205; 363–392 |

Use for: Slides 1–3 or any alternative opening. Preserve the careful legal premise,
the `To our knowledge` positioning boundary, and citations to the adjacent literature.

### 3. UncResCEO measure, construct validity, or inference limitation

| Source | Required reading |
|---|---|
| T | 197–227; 241–251; 1,492–1,555 |
| M | 409–482; 1,043–1,083; 1,162–1,210; 1,235–1,267; 1,357–1,363 |
| A | 207–217; 292–302; 304–313; 324–331; 338–343 |

Use for: measure explanation, decomposition visuals, first-stage controls, DWZ
replication, dictionary limitations, and the generated-regressand caveat.

### 4. Data sources, sample construction, sample attrition, or external validity

| Source | Required reading |
|---|---|
| T | 239–251; 258–270; 469–530; 1,558–1,618 |
| M | 484–541; 1,043–1,083; 1,311–1,316; 1,351–1,355; 1,415–1,417 |
| A | 129–139; 219–231; 333–349 |

Use for: the source/sample flow, base panel versus residual-feasible sample, data-role
attribution, five-call/Execucomp selection, and deal classification.

### 5. Empirical design, event clock, identification, or baseline

| Source | Required reading |
|---|---|
| T | 209–239; 266–270 |
| M | 543–610; 1,085–1,132; 1,269–1,308; 1,364–1,385 |
| A | 232–240; 254–276; 351–361 |

Use for: MA1/MA2/MA3 logic, PRE2/PRE1/GAP/POST, announcement and completion
boundaries, omitted baseline, never-acquirers, fixed effects, first-deal restrictions,
and why the design remains correlational.

### 6. Main Analysis 1 — pre-announcement cash run-up

| Source | Required reading |
|---|---|
| T | 272–282; 533–582 |
| M | 612–676; 1,059–1,083 |
| A | 242–253; 304–331 |

Use for: the `0.0461` cash estimate, standard error, two-tailed p-value, economic
scale, separate cash/stock samples, and the distinction between elevation and trend.

### 7. Main Analysis 2 — disclosure timing and the two clocks

| Source | Required reading |
|---|---|
| T | 284–296; 584–638; 334–352; 1,106–1,217 |
| M | 678–838; 1,085–1,112 |
| A | 155–165; 254–266; 283–288; 304–331 |

Use for: the matched 28,102-firm-quarter event study, PRE1-to-GAP contrast,
cash persistence caveat, completion timing, aligned panels, withdrawal treatment,
and the static cash specification.

### 8. Main Analysis 3 — cash versus stock concentration

| Source | Required reading |
|---|---|
| T | 298–308; 698–748; 354–360; 1,374–1,413 |
| M | 841–914; 1,114–1,132 |
| A | 268–276; 289–290; 304–331 |

Use for: the pooled Wald test, imprecise negative stock estimate, concentration rather
than strict specificity, the unsupported war-chest mechanism, and all-deals evidence.

### 9. Analyst scrutiny and measured alternative explanation

| Source | Required reading |
|---|---|
| T | 241–249; 310–322; 920–1,039 |
| M | 916–984; 1,134–1,153; 1,277–1,283; 1,387–1,391 |
| A | 278–290; 333–347 |

Use for: CashScrutiny construction/validity, the controlled run-up, interaction and
confidence interval, the 89% zero-scrutiny fact, and the underpowered-test boundary.

### 10. Robustness checks

| Source | Required reading |
|---|---|
| T | 334–360; 1,106–1,217; 1,223–1,489 |
| M | 950–972; 1,150–1,159; 1,335–1,341; 1,393–1,406 |
| A | 283–290; 333–361 |

Use for: withdrawal-as-resolution, limited incremental observations, the static cash
model, all-deals stacked results, and the forward/logit evidence.

### 11. Secondary bid–ask analysis

| Source | Required reading |
|---|---|
| T | 324–332; 1,042–1,103 |
| M | 1,154–1,159; 1,319–1,324; 1,402–1,406 |
| A | 177–186; 333–349 |

Use for: secondary contribution or Q&A only. Preserve the component-specific
interpretation, one-tailed reporting, contemporaneous-only pattern, and absence of a
direct between-segment test.

### 12. Conclusion, contribution, limitations, or closing language

| Source | Required reading |
|---|---|
| T | 178–186; 365–380 |
| M | 987–1,037; 1,162–1,210; 1,269–1,274; 1,303–1,341; 1,408–1,413; 1,630–1,647 |
| A | 104–127; 177–186; 292–302; 417–423 |

Use for: the final core result, contribution, causal/mechanism boundaries, sample
selection, dictionary limitation, generated-regressand inference, and future work.

### 13. Visual design, branding, accessibility, or PDF review

| Source | Required reading |
|---|---|
| T | The complete task-specific thesis bundle above, including the relevant table notes |
| M | 1,420–1,548 plus the complete task-specific master bundle |
| A | 29–78; 304–331; 363–392 plus the complete task-specific audit bundle |

Use for: HTML/CSS implementation, statistical charts, diagrams, typography, branding,
citations, accessibility, and PDF-derived visual review. This bundle never authorizes
a thesis-free visualization.

### 14. Speaker notes, rehearsal, Q&A, or backup deck

| Source | Required reading |
|---|---|
| T | The complete relevant content bundle; for definitions also 1,558–1,618 |
| M | 1,213–1,418; 1,550–1,585 plus the complete relevant slide bundle |
| A | 141–165; 333–361; 394–423 plus the complete relevant finding bundle |

Use for: spoken explanations, transitions, likely examination questions, timing,
backup navigation, and preserving caveats under questioning.

## Quick selection guide

| Immediate task | Minimum safe reading |
|---|---|
| Choose the presentation story | Always-on + Bundle 1 |
| Design an opening slide | Always-on + Bundle 2 + Bundle 13 |
| Draft a content slide | Always-on + its topic bundle |
| Create a statistical plot | Always-on + its result bundle + Bundle 13 |
| Write speaker notes | Always-on + its topic bundle + Bundle 14 |
| Prepare Q&A or backup | Always-on + relevant topic bundle + Bundle 14 |
| Audit the complete redesigned deck | Full reread of T, current master/specification, and current audit criteria |

## Escalation triggers

Stop targeted reading and broaden the source review when:

- a claim touches more than two empirical analyses;
- a proposed title makes a stronger claim than the thesis prose;
- a number, unit, sample, significance level, or test direction is uncertain;
- a visualization combines outcomes from different samples or units;
- a legal, theoretical, or prior-literature claim lacks a direct citation;
- the task changes the full story, final contribution, or limitation hierarchy;
- any source hash differs from the source lock above.

