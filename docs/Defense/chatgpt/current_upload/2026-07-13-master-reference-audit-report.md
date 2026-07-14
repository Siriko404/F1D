# Defense Presentation Master Reference — Hard Audit

Date: 2026-07-13  
Scope: `DEFENSE_PRESENTATION_MASTER_REFERENCE.txt` only  
Thesis authority: `docs/Thesis/_uottawa_rewrite/_thesis_FLAT.tex`  
Deck status: not audited and not modified

## 1. Executive verdict

The master has the right central story, the correct main coefficients, and unusually
good causal and mechanism guardrails. It is not yet safe to use as the authoritative
build specification.

The required revision is substantive rather than cosmetic:

- correct two occurrences of the wrong event-study unit;
- remove legal and empirical overstatement;
- merge the duplicated timing slides;
- distinguish the base call panel from the residual-feasible and regression samples;
- surface the generated-regressand limitation in the core presentation;
- replace the unsupported timing map with an 18-minute rehearsal target;
- raise the projection typography standard;
- add thesis citations to conceptual as well as quantitative slides;
- consolidate the backup deck around actual examination risks.

No external empirical content is needed. The thesis contains enough information to
build all recommended charts and diagrams.

## 2. Standards baseline

### Formal requirements

1. uOttawa has no single general oral-defence format for all master's programs; the
   program determines its evaluation process. The chair asks the student to present
   the thesis topic, and the chair specifies the available time. Therefore the
   confirmed 20-minute limit is the operative constraint, but it should still be
   reconfirmed with the chair or graduate office before the final rehearsal.
   [uOttawa Regulation C-7](https://www.uottawa.ca/about-us/leadership-governance/policies-regulations/c-7-thesis)
   and [uOttawa oral-defence procedure](https://www.uottawa.ca/study/graduate-studies/thesis/oral-defence).

2. The Telfer handbook's approximate 20-minute language applies to the master's
   **proposal** defence, not the final thesis defence. The master correctly refuses
   to use it as proof of the final limit. The handbook is also a 2021–2022 document,
   so it is contextual rather than current governing authority.
   [Telfer Graduate Student Handbook, pp. 26–27](https://telfer.uottawa.ca/assets/phd/documents/Telfer-Graduate-Students-Handbook-for-Research-Programs_Final-_April-2021.pdf).

3. uOttawa formally applies research-ethics and academic-integrity obligations to
   oral thesis presentations. The regulation does not prescribe slide-footer design;
   visibly and consistently identifying conceptual, legal, and quantitative sources
   is the strong academic convention used here to implement that obligation.
   [uOttawa Regulation C-7.5](https://www.uottawa.ca/about-us/leadership-governance/policies-regulations/c-7-thesis).

4. Telfer branding in the master is substantially correct: garnet `#8F001A`, dark
   grey `#231F20`, light beige `#F4F2EF`, Roboto body text, and Roboto Condensed
   titles. Official logo artwork, clear space, and undistorted proportions are
   required. The brand manual explicitly provides a non-logo page element to avoid
   crowding every page with logos.
   [Telfer Brand Manual](https://telfer.uottawa.ca/assets/documents/2020/brand/DOC_Brand-Guidelines_2021_E_Final.pdf).

### Strong academic conventions

- A defence presentation should move through background, problem, approach, results,
  and conclusion, with illustrative graphics and rehearsal.
  [MIT thesis-defence guide](https://web.mit.edu/course/21/21.guide/th-defen.htm).
- Each slide should operate as a single message unit; simple diagrams and direct
  annotations are preferred to bullet-heavy explanation.
  [Northwestern scientific-slide guidance](https://www.northwestern.edu/climb/resources/oral-communication-skills/designing-PowerPoint-slides.html).
- One point per slide, simplified graphics, 16:9 format, high contrast, and no
  color-only encoding are strong accessibility practices. Northern Illinois
  University recommends at least 24-point type.
  [NIU effective-slide guidance](https://www.niu.edu/citl/resources/toolkits/flexible-teaching/guide-to-course-materials/how-do-i-create-effective-slide-presentations.shtml).

There is no credible universal rule requiring a fixed number of visuals. Visual
density must follow the analytical jobs of the slides. For this thesis, the evidence
supports eight substantive visuals in an eleven-slide core deck: one disclosure
diagram, one measure-decomposition diagram, one data/sample flow, one event-clock
design diagram, and four results/credibility graphics.

## 3. Critical corrections

### C1 — Wrong unit for the matched event-study sample

- **Location:** master lines 690–692 and 1109–1111; Slides 8 and the result register.
- **Grade:** unsupported/incorrect.
- **Master:** `28,102 calls`.
- **Thesis:** `28,102 firm-quarters` across 1,320 firms (thesis lines 286 and
  630–631).
- **Why it matters:** unit-of-analysis errors are high-risk in a quantitative defence.
- **Exact correction:** replace both instances with `28,102 firm-quarters across
  1,320 firms`.

### C2 — “A firm knows, but cannot say” overstates the legal premise

- **Location:** Slide 2 title, master line 297.
- **Grade:** unsupported/overstated.
- **Evidence:** the thesis says a firm may remain silent and, once it speaks, may not
  mislead; it does not establish that the firm categorically cannot say anything
  about the deal (thesis lines 170 and 195).
- **Why it matters:** the title contradicts the more careful legal guardrails later on
  the same slide.
- **Exact replacement:** `A firm knows while the deal remains private` or
  `The firm knows; the market does not`.

### C3 — The final takeaway converts a suggestive pattern into a categorical claim

- **Location:** master lines 1017–1029 and 1634–1647; Slide 12 and final message.
- **Grade:** unsupported/overstated.
- **Master:** `A withheld acquisition leaves a readable, anticipatory trace...`
- **Thesis:** the abstract says answers “appear to carry” a trace; the conclusion says
  the patterns “suggest” a trace and repeatedly disclaims causal identification and
  mechanism (thesis lines 125, 374, and 376–378).
- **Why it matters:** the strongest sentence is also the sentence most likely to be
  repeated by an examiner.
- **Exact replacement:** `The evidence suggests that a withheld acquisition leaves a
  readable, anticipatory trace in the CEO's unscripted answers.` Follow immediately
  with: `The pattern is within-firm and correlational; the mechanism remains open.`

### C4 — The mechanism list adds explanations not contained in the thesis

- **Location:** master lines 1207–1210.
- **Grade:** unsupported.
- **Problem:** `cognitive load` and `planning uncertainty` are introduced as candidate
  mechanisms, but the thesis does not advance or test them. Its stated ambiguity is
  compliance-constrained speech versus strategic silence, with the broader mechanism
  left open (thesis lines 184, 207, and 376).
- **Exact replacement:** `The data cannot distinguish compliance-constrained speech
  from strategic silence, and they do not identify a broader mechanism.`

### C5 — Exact 50/50 deal treatment is unresolved

- **Location:** Slide 5, backup 5, and anticipated payment-method questions.
- **Grade:** unresolved from the permitted sources.
- **Evidence:** the thesis defines the cash arm as at least 50% cash and the stock arm
  as at least 50% stock (thesis line 268), but neither permitted file explains whether
  exact 50/50 deals overlap, are assigned by another rule, or are excluded.
- **Why it matters:** the two stated definitions overlap mathematically at exactly
  50/50. An examiner can reasonably ask.
- **Exact action:** do not invent an answer. Mark this as a pre-defence verification
  item. Until verified, avoid saying the two classifications are mutually exclusive.

## 4. Whole-story and timing findings

### M1 — The 18:20 map is an allocation, not validated timing

- **Severity:** major.
- **Location:** master lines 189–212 and all slide timing claims.
- **Evidence:** the twelve quoted spoken blocks contain 685 words—about 4.9 to 5.7
  minutes at 140 to 120 words per minute. They cannot validate an 18:20 delivery.
- **Additional conflict:** 18:20 leaves only 1:40, while the approved audit target is
  approximately 18:00 with a two-minute buffer.
- **Exact correction:** label every duration `provisional until rehearsed`; set the
  rehearsal target to `17:30–18:00`; prepare complete spoken notes or a detailed
  speaking outline; validate with at least three full timed rehearsals.

### M2 — Slides 8 and 9 duplicate the same language event study

- **Severity:** major.
- **Location:** Slides 8–9.
- **Evidence:** Slide 8 presents PRE2/PRE1/GAP/POST for UncResCEO; Slide 9 repeats
  PRE1, GAP, and the PRE1–GAP contrast before adding cash.
- **Why it matters:** the strongest result is narrated twice, producing visual fatigue
  and consuming time that should go to interpretation and limitations.
- **Exact correction:** merge them into one `Two clocks` slide with aligned panels for
  UncResCEO and CashRatio on the matched 28,102-firm-quarter sample. Allocate about
  three minutes to this single slide.

### M3 — The title slide repeats the event clock before it has meaning

- **Severity:** minor.
- **Location:** Slide 1 lines 261–272.
- **Authority:** design judgment supported by the single-message convention.
- **Exact correction:** remove the mini event clock from the title slide. Keep title,
  subtitle, candidate, program, supervisors, date, and official branding. Introduce
  the event clock once on the disclosure-setting slide and formalize it on the design
  slide.

### M4 — The architecture gives methods and results the right priority, but not the
secondary contribution

- **Severity:** major.
- **Location:** Slides 11–12 and the `What the thesis establishes` title.
- **Evidence:** the thesis states four descriptive contributions, including the
  secondary bid-ask result (thesis lines 180 and 182). The core deck omits that result.
- **Exact correction:** keeping the bid-ask analysis in backup is defensible within 20
  minutes, but retitle the final slide `Core result and boundaries`. Do not use a title
  that implies an exhaustive account of everything the thesis establishes.

## 5. Slide-by-slide actionable findings

### Slide 2 — Disclosure setting

- Replace the categorical title as required by C2.
- Preserve the safe on-slide legal formulation: `The firm may remain silent; if it
  speaks, it cannot mislead.`
- Add a compact source footer: `Basic v. Levinson (1988); SEC Rule 10b-5`, matching
  the thesis's own authorities.
- Use one disclosure-bind diagram, not six narrated bullets.

### Slide 3 — Research question and contribution

- **Minor:** replace `hidden deal` with the thesis term `undisclosed acquisition`.
- Cite the prior-work categories in a small footer: Keown and Pinkerton (prices),
  Thewissen et al. (managed tone), and Ragozzino and Reuer (strategy vocabulary).
- Keep `To our knowledge` attached to the novelty claim; the thesis expressly treats
  it as a positioning claim, not an empirical finding (thesis line 174).

### Slide 4 — Language measure

- Replace `State, not personality` with `Call-specific residual, not persistent CEO
  style`. A residual is not a direct measurement of the CEO's mental state.
- Show the two distinct control layers correctly: the first stage builds UncResCEO
  using CEO/year effects, speech variables, and performance controls; the main
  second stage adds firm financial controls with firm and year-quarter fixed effects
  (thesis lines 225 and 237).
- Move one sentence of the generated-regressand caveat into the core limitations
  slide. It affects every main design and should not exist only in backup/Q&A
  (thesis lines 227 and 239).

### Slide 5 — Data and sample

- **Major factual wording:** change `IBES: analyst and earnings information` to
  `IBES: earnings records used for the earnings-surprise control` (thesis line 262).
- Distinguish three quantities visibly:
  - base language panel: 88,205 calls, 1,884 firms;
  - UncResCEO available: 44,900 observations;
  - MA1 cash uncertainty regression: 27,622 firm-quarters, 1,248 firms.
- Do not call 88,205 the effective sample for every result.
- Add the exact-50/50 unresolved note to backup, not the crowded core slide.
- Replace four decorative number tiles with a compact sample-and-source flow that
  makes the shrinking estimation universe visible.

### Slide 6 — Design and event clock

- Add the omitted baseline: `e ≤ −3 plus never-acquirers`.
- State in speech or backup that never-acquirers primarily identify calendar-time
  effects; the treated-firm contrast is within firm (thesis line 231).
- Do not call PRE2 proof of no pretrend. It is one limited pre-period check.
- Put post-window capping, truncation at the next announcement, withdrawn-deal
  treatment, and first-deal timing in backup; these are too detailed for the core
  clock but must be available for examination.

### Slide 7 — Main run-up

- Change the title from `rises` to `is elevated`. A single-quarter coefficient does
  not establish a trend.
- The cash and stock estimates come from separate arms with different samples
  (cash: 27,622 firm-quarters/1,248 firms; stock: 39,377/1,338). If both estimates are
  plotted, label them `separate specifications` and show the sample sizes.
- Better architecture: show the cash estimate and economic scale here; reserve the
  cash-versus-stock visual comparison for the pooled Wald slide. This prevents the
  later formal comparison from feeling repetitive.
- Include a zero line, 95% interval, sample/specification footer, and numerical label.

### Slides 8–9 — Timing and two clocks

- Merge as required by M2.
- Replace `The language trace ends when the deal becomes public` with
  `Uncertainty is concentrated in the last private quarter` or
  `Uncertainty drops across the announcement boundary`.
- Replace `There is no pretrend` with `PRE2 is near zero and provides one limited
  pretrend check` (thesis line 288).
- Correct the sample unit to firm-quarters.
- Preserve the essential cash caveat: persistence through GAP is inferred from the
  insignificant PRE1–GAP change; the GAP level itself is not significant.
- Use separate axes and direct labels. The visual should emphasize within-outcome
  timing contrasts, never cross-panel magnitude comparisons.

### Slide 10 — Cash versus stock

- Values are verified against thesis lines 302–308 and table lines 712–718.
- Add one visible qualifier: `The significant difference partly reflects an
  imprecise negative stock estimate.`
- Keep the nonsignificant CashRatio difference close to the mechanism statement so
  the slide cannot be read as evidence for a proven war-chest channel.
- Use a direct difference bracket or annotation for the Wald estimate; significance
  must not be inferred by comparing the two separate confidence intervals.

### Slide 11 — Scrutiny and robustness

- The title is acceptable only with `measured` retained.
- Show the interaction estimate with its approximate 95% interval
  (`−0.027` to `0.016`) to make the power limitation visible.
- The withdrawal-resolution check adds only 89 firm-quarters and one firm. If it is
  mentioned, label it `limited incremental evidence`, not an independent rule-out
  (thesis lines 340–342).
- `Static fixed effects` specifically validates the **cash timing path** without the
  lag; the residual column is unchanged. Do not imply it is a new robustness test of
  the language result (thesis lines 344–352).
- The all-deals cash-minus-stock difference (`0.1056`, `p≈.013`) is the strongest
  compact robustness result for the core slide; move the rest to backup.

### Slide 12 — Conclusion and limits

- Retitle `Core result and boundaries`.
- Hedge the closing sentence as required by C3.
- Include four core boundaries, no more:
  1. correlational, within-firm evidence;
  2. no identified mechanism;
  3. generated-regressand uncertainty is not propagated;
  4. sample selection toward larger, better-covered firms.
- Keep compliance-constrained speech versus strategic silence as the named
  observational equivalence.

## 6. Visualization and table plan

No full regression table belongs in the core deck. Full tables belong in backup.
The following eight visuals are justified by a distinct analytical job:

| Core slide | Visual | Thesis-only inputs | Job |
|---|---|---|---|
| 2 | Disclosure-bind diagram | Thesis lines 170, 195 | Establish the private/public information state |
| 4 | Measure decomposition | Thesis lines 223–227 | Separate persistent style from call-specific residual |
| 5 | Sample/source flow | Thesis lines 262–270 | Show data roles and sample attrition |
| 6 | Event clock + three tests | Thesis lines 231–235 | Define PRE2, PRE1, GAP, POST and boundaries |
| 7 | Cash MA1 coefficient plot | 0.0461, SE 0.0172 | Establish the simple run-up |
| 8 | Aligned two-clock plots | Matched event-study table | Show disclosure timing versus completion timing |
| 9 | Pooled cash/stock comparison + Wald bracket | MA3 table | Present the actual between-arm test |
| 10 | Scrutiny interaction interval + compact robustness result | Scrutiny and all-deals tables | Show what survives and what remains underpowered |

Slides 1, 3, and 11 should still be visually structured but need no decorative
chart. This yields substantial visualization without manufacturing a quota or
repeating the same graph.

Every statistical visual should include:

- exact point estimates and 95% confidence intervals derived from thesis values;
- a visible zero reference;
- axes/units and direct labels;
- regression sample size and specification in a concise footer;
- thesis table/section citation;
- a non-color cue for significance or group identity.

## 7. Q&A and backup findings

The existing twelve-backup plan is redundant. Consolidate it to seven navigable
backup sections:

1. **Sample, sources, and deal classification** — include the unresolved exact-50/50
   treatment.
2. **UncResCEO construction and validity** — include the DWZ replication,
   dictionary limitations, and generated-regressand inference.
3. **Design details** — first deal, baselines, control layers, event-window trims,
   clustering, and one- versus two-tailed reporting.
4. **Main regression evidence** — MA1, matched event study, and pooled Wald table.
5. **Analyst scrutiny** — construction, validity, interaction, interval, and power.
6. **Robustness** — withdrawal's small increment, static cash model, all-deals tests,
   and later-deal contamination.
7. **Secondary bid-ask analysis and limitations** — component-specific results, no
   between-segment test, sample selection, and external validity.

Add or strengthen short answers for:

- the first-deal restriction and later-deal contamination;
- why never-acquirers are present when identification is within firm;
- the difference between first-stage and second-stage controls;
- why one PRE2 coefficient is only a limited pretrend check;
- one-tailed versus two-tailed inference and which load-bearing results survive;
- the exact-50/50 classification issue;
- why the withdrawal check has little incremental power;
- why the static specification changes CashRatio coefficient interpretation;
- why the bid-ask analysis does not test a direct difference between call segments.

## 8. Build-standard and accessibility findings

### B1 — Current body/source size rules are too small to certify as projection-safe

- **Severity:** major.
- **Location:** master lines 1497–1501.
- **Evidence:** 27–28 CSS px corresponds to 20.25–21 points under the standard CSS
  absolute-unit conversion before any print scaling; 19 CSS px is about 14.25 points.
  NIU's accessibility guidance recommends a 24-point minimum.
- **Exact correction:** define minimum size using the final PDF, not CSS alone. Under
  unscaled CSS, start body text at 32 px (24 pt) or larger and keep source footers
  comfortably legible. Validate by projecting the compiled PDF in the actual room.

### B2 — The rendering pipeline is sound but needs two additional checks

- Keep the existing HTML/CSS → Chromium PDF → PDF-derived PNG review rule.
- Add automated or manual checks for font embedding/substitution and clipped/overflowing
  content in the compiled PDF.
- Review every page at high resolution and also at realistic presentation distance;
  high-resolution screenshots alone do not establish legibility.

### B3 — Citation policy is too narrow

- **Severity:** major.
- **Location:** master lines 1515–1522.
- **Problem:** source footers are required for quantitative plots, but no equivalent
  rule covers legal, theoretical, prior-literature, or measurement claims.
- **Exact correction:** require concise citations on every slide that relies on
  external authority. Quantitative charts cite the thesis table; conceptual slides
  cite the original works already cited in the thesis.

## 9. Proposed corrected core architecture

This architecture retains the thesis's strongest story while removing duplication.
Times are rehearsal targets, not validated durations.

| # | Slide job | Target |
|---:|---|---:|
| 1 | Title — minimal branding and topic | 0:20 |
| 2 | Disclosure setting — private information, permitted silence, no misleading speech | 1:30 |
| 3 | Research question and contribution — what prior work sees and this thesis adds | 1:20 |
| 4 | UncResCEO construction — raw language, persistent style, call-specific residual | 1:50 |
| 5 | Data and estimation samples — sources, 88,205 base calls, residual/sample attrition | 1:20 |
| 6 | Event clock and empirical design — three tests, baseline, within-firm structure | 1:50 |
| 7 | MA1 run-up — cash estimate and economic scale | 1:30 |
| 8 | Two clocks — matched language and cash paths on one slide | 3:00 |
| 9 | Cash concentration — pooled Wald comparison and mechanism boundary | 2:00 |
| 10 | Credibility — measured scrutiny, power limit, strongest robustness | 1:30 |
| 11 | Core result and boundaries — contribution, limitations, hedged close | 1:50 |
|  | **Total rehearsal target** | **18:00** |

This is not a mandatory eleven-slide rule. It is the smallest architecture that gives
each major inferential job one slide while preserving an 18-minute target.

## 10. Items unresolved from the permitted sources

1. Exact handling of deals that are precisely 50% cash and 50% stock.
2. The final presentation time until confirmed by the chair/academic unit; Sina's
   confirmed working limit remains 20 minutes.
3. Actual delivery timing until complete speaking notes and timed rehearsals exist.
4. Final projection legibility until the compiled PDF is tested in the room.

## 11. Stopping point

This report audits the master reference only. It does not modify the master reference,
the HTML/CSS deck, or any thesis content. Revision should begin only after Sina
approves or rejects these findings.
