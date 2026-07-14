# ACT 2 DESIGN PROPOSAL

## The measure-and-design bridge

**Task:** Continue the approved disclosure-boundary story from the question, “How can we separate call-specific uncertainty from persistent CEO speaking style and other predictable call conditions?”, and leave the committee ready for the empirical evidence.

**Status:** Independent design proposal for Sina’s review. It is not an approved Act 2, a slide map, or a layout specification.

**Authority rule:** `_thesis_FLAT.tex` is the sole authority for thesis facts. `_CURRENT_HANDOFF_LEDGER.md` supplies approved presentation decisions; the audit supplies guardrails; the historical master is diagnostic input only. No external sources or evidence are used.

### Label key

- **THESIS FACT** — a statement supported by the thesis, with exact line citations.
- **DESIGN JUDGMENT** — a recommendation about narrative, emphasis, pacing, or visualization.
- **UNRESOLVED CHOICE** — a decision intentionally left open for later discussion.

---

## 1. Executive recommendation

**DESIGN JUDGMENT — Recommend the “answer first, then track it” architecture.** Act 2 should first answer Act 1’s transition in plain language: start with the uncertainty-word share in the CEO’s unscripted answers, explain why raw language confounds the moment with the speaker’s usual style and observable call conditions, and define the residual left after the first-stage decomposition. Only then should the narrative show the sample funnel, place that residual on the disclosure clock, and introduce the three second-stage questions.

This order is preferable because it follows the audience’s immediate dependency chain:

1. What is observed?
2. What is removed?
3. What remains?
4. On which calls can it be measured?
5. How is it carried into the acquisition tests?
6. What is the first empirical question?

It directly answers the approved transition, keeps the first- and second-stage controls separate, and avoids turning the bridge into either a data-source inventory or a regression lecture. It also preserves the current workflow boundary: the disclosure spine and Act 1 are approved, while Act 2, slide count, timing allocation, and visualization program remain open. [`_CURRENT_HANDOFF_LEDGER.md`, lines 152–177 and 280–315]

**THESIS FACT — Essential inference boundary.** `UncResCEO` is the call-varying residual from an established Dzieliński, Wagner, and Zeckhauser decomposition re-estimated on this thesis sample. It is not a newly invented measure, a direct reading of the CEO’s knowledge or mental state, or a deal-specific signal by construction. The thesis contribution is the residual’s application around undisclosed acquisitions. [`_thesis_FLAT.tex`, lines 223–227 and 376–378]

**DESIGN JUDGMENT — Recommended closing transition.**

> Once the predictable voice has been removed and every call is placed on the disclosure clock, the first empirical test follows directly: within the same firm, is `UncResCEO` elevated in PRE1—the final private quarter before a cash acquisition is announced?

This transition sets up MA1 without announcing its coefficient, making a causal claim, or attributing the residual to the deal before the regression is shown.

---

## 2. W1 — Minimum thesis-faithful evidence map

### 2.1 The minimum conceptual chain

| Order | Concept the committee must understand | Minimum thesis-faithful statement | Why it is essential now | Authority |
|---:|---|---|---|---|
| 1 | Raw CEO answer uncertainty | **THESIS FACT:** `UncAnsCEO` is the share of Loughran–McDonald uncertainty words in the CEO’s Q&A answers: uncertainty words divided by all words in those answers. Prepared-remarks uncertainty (`UncPreCEO`) and analyst-question uncertainty (`UncQue`) are computed separately. | Defines the observed language object and keeps “CEO answers” distinct from the full call. | `_thesis_FLAT.tex`, lines 223–224 and 262–264 |
| 2 | Persistent CEO style | **THESIS FACT:** Some language variation is persistent to the executive; the decomposition uses CEO fixed effects to capture that manager-specific speaking style. | Explains why the raw word share cannot answer the research question. | `_thesis_FLAT.tex`, lines 201 and 225 |
| 3 | Predictable call conditions | **THESIS FACT:** The first stage also accounts for prepared-remarks uncertainty, analyst-question uncertainty, call negativity, contemporaneous performance variables, and year effects. | Prevents the residual from being described as merely “raw uncertainty minus personality.” | `_thesis_FLAT.tex`, line 225 |
| 4 | `UncResCEO` | **THESIS FACT:** `UncResCEO` is the first-stage residual—the component of CEO answer uncertainty left unexplained by persistent style and the included observable call conditions. It is narrower than a style-only residual. | Directly answers Act 1’s transition and defines the main outcome. | `_thesis_FLAT.tex`, lines 225–227 |
| 5 | Measure ownership | **THESIS FACT:** The specification is adapted from Dzieliński, Wagner, and Zeckhauser and re-estimated on this thesis sample; the residual is this thesis’s sample-specific estimate, but the measure itself is not the thesis’s invention. | Avoids an examiner-correctable novelty overclaim. | `_thesis_FLAT.tex`, lines 225 and 245; replication evidence at lines 1507–1552 |
| 6 | Estimation universe | **THESIS FACT:** The language panel contains 88,205 calls across 1,884 firms; `UncResCEO` is available for 44,900 observations. At least five calls per CEO and Execucomp coverage are required to estimate speaking style, shifting the uncertainty sample toward larger, better-covered firms. | Makes the sample contraction and external-validity boundary visible before results. | `_thesis_FLAT.tex`, lines 239, 268–270 and 506–508 |
| 7 | Stage-one/stage-two handoff | **THESIS FACT:** The first-stage language and performance controls construct `UncResCEO`. The second-stage acquisition regressions instead add firm-financial controls, firm fixed effects, and calendar year-quarter fixed effects, with firm-clustered standard errors. | Prevents the two control layers from being merged or described as one regression. | `_thesis_FLAT.tex`, lines 231 and 237–239 |
| 8 | Event-time use | **THESIS FACT:** MA1 tests the PRE1 run-up; MA2 uses PRE2, PRE1, GAP, and POST to distinguish announcement from completion; MA3 pools the cash and stock indicators and formally tests their difference. | Shows why the residual is the relevant outcome and prepares the results sequence. | `_thesis_FLAT.tex`, lines 211–217 and 231–237 |
| 9 | Inference boundary | **THESIS FACT:** The designs are descriptive, correlational, and within firm; they do not identify a causal mechanism. `UncResCEO` is a generated regressand, and conventional second-stage standard errors do not propagate the uncertainty from estimating it in the first stage. | Stops “residualized” from being heard as “causally isolated” or “fully measured.” | `_thesis_FLAT.tex`, lines 227, 237–239 and 376–378 |

### 2.2 The two stages must remain visibly distinct

| Feature | Stage 1: construct the measure | Stage 2: study acquisition timing |
|---|---|---|
| Narrative question | **THESIS FACT:** What part of the CEO’s Q&A uncertainty is not explained by persistent style and included call conditions? [`_thesis_FLAT.tex`, lines 223–225] | **THESIS FACT:** Is that residual elevated in acquisition event time, when does it recede, and is the run-up stronger for cash than stock? [`_thesis_FLAT.tex`, lines 211–217 and 231–237] |
| Input / dependent variable | **THESIS FACT:** Raw CEO-answer uncertainty, `UncAnsCEO`. [`_thesis_FLAT.tex`, lines 223–225] | **THESIS FACT:** `UncResCEO` is the focal language outcome; other designs also use `CashRatio`. [`_thesis_FLAT.tex`, lines 231–235 and 274–290] |
| Main adjustment | **THESIS FACT:** CEO fixed effects; prepared-remarks uncertainty; analyst-question uncertainty; call negativity; earnings surprise, EPS growth, stock return, market return; year effects. [`_thesis_FLAT.tex`, line 225] | **THESIS FACT:** Event indicator(s); leverage, log assets, Tobin’s Q, ROA, capex, dividend indicator, cash-flow volatility; firm and year-quarter fixed effects. [`_thesis_FLAT.tex`, lines 231 and 237] |
| Output | **THESIS FACT:** `UncResCEO`, the estimated residual. [`_thesis_FLAT.tex`, lines 225–227] | **THESIS FACT:** Within-firm, correlational event-time coefficients and Wald contrasts. [`_thesis_FLAT.tex`, lines 231–239] |
| Inference caution | **THESIS FACT:** The residual is estimated rather than directly observed. [`_thesis_FLAT.tex`, line 227] | **THESIS FACT:** Conventional standard errors are firm-clustered but do not carry first-stage estimation uncertainty through the second step. [`_thesis_FLAT.tex`, lines 227, 231 and 239] |

### 2.3 Sample facts that are essential at this bridge

**THESIS FACT:** The base language panel is 88,205 earnings-call observations across 1,884 firms from 2002–2018, but the availability of `UncResCEO` falls to 44,900 observations. [`_thesis_FLAT.tex`, lines 262–270 and 506–508]

**THESIS FACT:** The first cash-arm uncertainty regression uses 27,622 firm-quarters across 1,248 firms, while the broader cash-ratio regression uses a different universe. [`_thesis_FLAT.tex`, lines 278 and 571–579]

**DESIGN JUDGMENT:** Act 2 should show these as a shrinking estimation universe, not as three interchangeable headline sample sizes:

`88,205 calls / 1,884 firms` → `44,900 residual observations` → `27,622 firm-quarters / 1,248 firms in the first cash-run-up uncertainty test`.

The matched timing result later uses 28,102 firm-quarters across 1,320 firms; that denominator belongs beside the timing evidence, not in the opening sample sentence. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 286 and 630–636]

### 2.4 Event-clock facts needed before the first result

**THESIS FACT:** In MA1, PRE1 is the quarter immediately before the firm’s first qualifying cash-acquisition announcement; treated firms’ post-announcement quarters are dropped, the within-firm comparison is to the same firm’s earlier quarters, and never-acquirers mainly identify calendar-time effects. [`_thesis_FLAT.tex`, lines 211 and 231]

**THESIS FACT:** In MA2, PRE2 is two quarters before announcement, PRE1 is the last pre-announcement quarter, GAP is announced but not yet closed, and POST is after completion. Announcement and completion are boundaries, while the omitted baseline is `e ≤ −3` plus never-acquirers. [`_thesis_FLAT.tex`, lines 233 and 286; table note at lines 630–636]

**DESIGN JUDGMENT:** The core explanation should define PRE1 now because it is needed for the first result. It should also preview the full clock so the later announcement-versus-completion result has a conceptual home. Post-window caps, truncation at the next announcement, and treatment of withdrawn deals should stay out of the spoken bridge and remain available in backup. The audit reaches the same density judgment. [`2026-07-13-master-reference-audit-report.md`, lines 232–240]

---

## 3. W2 — Three genuinely distinct Act 2 architectures

| Architecture | Narrative logic | Strengths | Weaknesses | Committee risk | Continuity from Act 1 |
|---|---|---|---|---|---|
| **A. Answer first, then track it** **(recommended)** | Begin with the raw CEO-answer word share; remove persistent style and predictable conditions; name the residual; show the feasible sample; carry the residual onto the disclosure clock and into the three tests. | Immediately answers Act 1’s stated transition; gives `UncResCEO` a memorable meaning before equations or samples; makes the two-stage distinction easy to preserve; creates a natural transition to MA1. | Requires discipline not to narrate the full first-stage control list or validation suite. | The residual may still be mistaken for a mental state unless its boundary is stated in the same beat as its definition. | Excellent: it answers the exact question Act 1 leaves hanging. |
| **B. Clock first, then derive the outcome** | Re-enter the private-to-public timeline; ask what variable could move within CEO across that boundary; derive the need for a call-varying residual; then show sample and regressions. | Strong thematic continuity with the disclosure boundary; foregrounds why fixed style cannot explain an appearing-and-disappearing pattern. The thesis itself motivates that logic. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 201 and 217] | Delays the direct answer to the transition; introduces PRE/GAP/POST before the audience knows what is being measured; risks repeating Act 1’s setting. | Audience may confuse the event clock with evidence already observed, or assume the measure was built to fit the event. | Good, but circular if the clock is over-developed before the outcome exists. |
| **C. Audit trail from data to regression** | Start with transcript, CEO, accounting, market, and deal sources; show sample filters; construct the residual; then present stage-one and stage-two equations. | Maximally transparent about provenance, linkage, and sample attrition; defensible under detailed data questioning. **THESIS FACT:** The five source roles and linkage are documented in the thesis. [`_thesis_FLAT.tex`, lines 262–268] | Makes the bridge procedural; the economic question disappears behind source names and filters; likely to consume scarce core time before results. | Highest risk of becoming a methods lecture and leaving the committee unsure why `UncResCEO` is the relevant outcome. | Weak: it answers “where did the data come from?” before answering Act 1’s conceptual question. |

### Comparative judgment

**DESIGN JUDGMENT:** Architecture A is the best balance of comprehension, pacing, and academic defensibility. Architecture B contains one useful idea—fixed style cannot produce a within-CEO pattern that appears and disappears around an event—but that idea should be one sentence inside Architecture A, not the organizing structure. Architecture C should supply backup/Q&A material and a compact sample funnel, not the core story.

The recommendation also corrects the historical master’s main risks without inheriting its slide map: the master already had useful measure language but called the residual “state, not personality,” put the generated-regressand issue only in backup, and treated the data/source inventory as a standalone procedural unit. [`DEFENSE_PRESENTATION_MASTER_REFERENCE.txt`, lines 410–481 and 484–540] The audit’s exact corrections are to call it a call-specific residual rather than a mental state, separate the two control layers, surface the generated-regressand limitation, and make sample contraction visible. [`2026-07-13-master-reference-audit-report.md`, lines 207–230]

---

## 4. W3 — Recommended Act 2 architecture

### 4.1 Narrative role

**DESIGN JUDGMENT:** Act 2 is a bridge, not a miniature methods chapter. Its job is to convert the research question into a credible outcome and a legible test sequence. It should leave the audience able to answer four questions before the first coefficient appears:

1. What is `UncResCEO`?
2. What was removed to construct it?
3. Why is it not a direct measure of a mental state or of the deal?
4. How will it be compared around the private-to-public boundary?

### 4.2 Ordered beats — narrative units, not slides

#### Beat 1 — Observe the words

**THESIS FACT:** Begin with the uncertainty-word share in the CEO’s unscripted Q&A answers, not the whole transcript or the prepared remarks. [`_thesis_FLAT.tex`, lines 223–224 and 264]

**DESIGN JUDGMENT:** One plain-language sentence is enough: “I begin with how frequently the CEO uses finance-specific uncertainty words while answering analysts.” The formula may be visible, but it need not be narrated symbol by symbol.

#### Beat 2 — Explain why raw uncertainty is insufficient

**THESIS FACT:** Raw language combines persistent executive style with call-varying conditions; an anticipatory pattern tied to a particular event cannot reside in a fixed executive trait because it must appear and disappear within the same tenure. [`_thesis_FLAT.tex`, line 201]

**DESIGN JUDGMENT:** This is the conceptual answer to “why residualize?” and should precede any control list.

#### Beat 3 — Construct and bound `UncResCEO`

**THESIS FACT:** Following the Dzieliński, Wagner, and Zeckhauser specification, re-estimated on this sample, the first stage absorbs CEO style and the included observable speech, performance, and year factors; its residual is `UncResCEO`. [`_thesis_FLAT.tex`, lines 225–227]

**DESIGN JUDGMENT:** Define the measure and its boundary together: “call-specific residual, not a direct mental-state measure and not deal uncertainty by construction.” State that the thesis applies an established measure rather than inventing it.

#### Beat 4 — Show the feasible estimation universe

**THESIS FACT:** The language panel contains 88,205 calls across 1,884 firms; the residual is available for 44,900 observations; the first cash-run-up uncertainty regression uses 27,622 firm-quarters across 1,248 firms. The five-call and Execucomp requirements create selection toward larger, better-covered firms. [`_thesis_FLAT.tex`, lines 239, 268–270, 506–508 and 571–579]

**DESIGN JUDGMENT:** Present this as a funnel. Do not narrate all five databases unless asked.

#### Beat 5 — Make the stage handoff explicit

**THESIS FACT:** Stage 1 builds the language outcome with CEO/year effects and language/performance controls; stage 2 studies acquisition timing with firm-financial controls, firm effects, year-quarter effects, and firm-clustered standard errors. [`_thesis_FLAT.tex`, lines 225, 231 and 237–239]

**DESIGN JUDGMENT:** Use a verbal hinge: “That is the measurement regression. The acquisition regressions are a second step with a different job and a different control set.”

#### Beat 6 — Place the outcome on the disclosure clock

**THESIS FACT:** MA1 asks whether the residual is elevated in PRE1; MA2 tracks PRE2, PRE1, GAP, and POST to distinguish announcement from completion; MA3 formally compares cash and stock in one pooled regression. [`_thesis_FLAT.tex`, lines 211–217 and 231–237]

**DESIGN JUDGMENT:** Explain the jobs of the three tests, not their full equations. The audience needs the logic “run-up → disclosure timing → pooled payment-method difference.”

#### Beat 7 — State inference boundaries and turn to evidence

**THESIS FACT:** The tests are within-firm and correlational; no mechanism is identified. The residual is generated in a first step, and its first-stage estimation uncertainty is not propagated into the conventional second-stage standard errors. [`_thesis_FLAT.tex`, lines 227, 237–239 and 376–378]

**DESIGN JUDGMENT:** State both boundaries once, without apologetic detail, then use the recommended closing transition.

### 4.3 Presentation-ready spoken narrative

*The bracketed citations are production annotations and are not meant to be spoken.*

> How do I separate a moment from a manner of speaking? I begin with the raw share of finance-specific uncertainty words in the CEO’s Q&A answers—the unscripted part of the call. [`_thesis_FLAT.tex`, lines 223–224]
>
> Raw language is not enough. Some executives speak more tentatively than others, and calls differ in predictable ways. An acquisition-timed pattern cannot be a fixed speaking trait; it must vary from one call to the next within the same executive’s tenure. [`_thesis_FLAT.tex`, line 201]
>
> I therefore follow the Dzieliński, Wagner, and Zeckhauser decomposition and re-estimate it on this sample. CEO fixed effects absorb persistent speaking style. The model also accounts for uncertainty in the prepared remarks and analyst questions, overall call negativity, contemporaneous performance, and year effects. The residual is `UncResCEO`: the call-specific portion of the CEO’s answer uncertainty left after those included predictable components are removed. This is an established measure applied in a new setting; it is not a direct measure of the CEO’s mental state, and the residual is not attributed to an acquisition by construction. [`_thesis_FLAT.tex`, lines 225–227 and 376–378]
>
> The construction is stage one. Stage two asks how that residual behaves around acquisition event time. The control layer changes: the acquisition regressions use firm financial controls, firm fixed effects, and calendar year-quarter fixed effects, with standard errors clustered by firm. The resulting comparisons are within firm and correlational. [`_thesis_FLAT.tex`, lines 231 and 237–239]
>
> The base language panel contains 88,205 calls across 1,884 firms. `UncResCEO` is available for 44,900 observations, and the first cash-run-up uncertainty regression uses 27,622 firm-quarters across 1,248 firms. Estimating speaking style requires repeated calls and CEO coverage, which tilts the language sample toward larger, better-covered firms, so each result will carry its own denominator. [`_thesis_FLAT.tex`, lines 239, 268–270, 506–508 and 571–579]
>
> I then place each call on the disclosure clock. PRE1 is the final private quarter before announcement; GAP is public but not yet completed; POST follows completion. The first design tests the PRE1 run-up, the second asks whether the pattern changes at announcement rather than completion, and the third formally compares cash and stock deals in one pooled model. [`_thesis_FLAT.tex`, lines 231–237 and 286]
>
> One inference caveat follows from this sequence: `UncResCEO` is estimated in stage one, and the conventional stage-two standard errors do not propagate that first-stage uncertainty. [`_thesis_FLAT.tex`, lines 227 and 239]
>
> Once the predictable voice has been removed and every call is placed on the disclosure clock, the first empirical test follows directly: within the same firm, is `UncResCEO` elevated in PRE1—the final private quarter before a cash acquisition is announced?

### 4.4 Entry and exit transitions

**Entry from approved Act 1:**

> The answer begins with the distinction between how a CEO usually speaks and what is unusual about one particular call.

**Exit into the first empirical result:**

> Once the predictable voice has been removed and every call is placed on the disclosure clock, the first empirical test follows directly: within the same firm, is `UncResCEO` elevated in PRE1—the final private quarter before a cash acquisition is announced?

**DESIGN JUDGMENT:** The exit is preferable to “the first result is…” because it completes a chain of necessity: define the outcome, locate it in time, then ask the coefficient question.

---

## 5. W4 — Keep/defer partition

| Content | Placement | Rationale | Support |
|---|---|---|---|
| Raw CEO Q&A uncertainty-word share | **Act 2 core** | The audience needs the observable input before it can understand the residual. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 223–224 |
| Persistent style versus predictable call conditions versus residual | **Act 2 core** | This is the direct answer to the approved transition. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 201 and 225 |
| DWZ attribution and “application, not invention” | **Act 2 core** | Measure ownership is a load-bearing academic boundary. | **THESIS FACT:** `_thesis_FLAT.tex`, line 225 |
| “Call-specific residual, not mental state or deal signal” | **Act 2 core** | Without this, the bridge overstates construct validity before evidence appears. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 225–227 and 376–378 |
| First-stage versus second-stage control layers | **Act 2 core** | Prevents the most likely methods confusion. State the purpose of each layer, not every variable. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 225 and 237 |
| Base panel, residual availability, first-result estimation sample | **Act 2 core, compactly** | Prevents 88,205 calls from being misreported as every result’s effective sample. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 270, 506–508 and 571–579 |
| Five-call/Execucomp selection toward larger, better-covered firms | **Act 2 core, one sentence** | It is the immediate reason the sample contracts and a material external-validity boundary. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 239 and 268–270 |
| PRE1 and the jobs of MA1, MA2, MA3 | **Act 2 core** | Required to make the first result and later result hierarchy intelligible. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 211–217 and 231–237 |
| Full PRE2–PRE1–GAP–POST clock and omitted baseline | **Act 2 core, conceptually** | Announcement and completion must be distinguished before results. Avoid detailed window mechanics. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 233 and 286; lines 630–636 |
| Within-firm, correlational, no identified mechanism | **Act 2 core** | “Residualized” and fixed effects must not be heard as causal identification. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 237–239 and 376–378 |
| Generated-regressand status and non-propagated uncertainty | **Act 2 core, one sentence; repeat on core limitations** | It applies to every main design. Mentioning it once here explains the two-stage inference issue; the later limitations treatment prevents it from disappearing. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 227 and 239; audit lines 207–217 and 292–302 |
| Word-list abstraction from context | **Later core limitations** | Material construct boundary, but elaborating it during measure construction would interrupt comprehension. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 376–378 |
| Sample generalization beyond larger, better-covered U.S. firms, 2002–2018 | **Later core limitations, after the one-sentence Act 2 selection note** | Act 2 explains why the sample shrinks; the final boundary explains external validity fully. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 376–378 |
| Compliance-constrained speech versus strategic silence | **Later core interpretation/limitations** | Approved Act 1 already establishes the disclosure bind; Act 2 need not reopen mechanism theory while explaining the measure. It must remain prominent before the close. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 184 and 207 |
| Exact first-stage equation and every first-stage coefficient | **Backup/Q&A** | Needed for scrutiny, not for immediate understanding. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 223–227 and 1507–1552 |
| Replication and convergent-validity tables | **Backup/Q&A** | They answer construct-validity challenges but would turn the bridge into a validation lecture. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 243–249 and 1507–1552 |
| All database roles, identifiers, and link mechanics | **Backup/Q&A** | Provenance is documented but does not answer the Act 1 transition. | **THESIS FACT:** `_thesis_FLAT.tex`, line 262 |
| Full second-stage equations and every financial control | **Backup/Q&A** | The core should explain the estimand and fixed-effect logic, not narrate an inventory. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 231–239 |
| Four-quarter post cap, next-announcement truncation, withdrawn-deal rows, first-deal detail | **Backup/Q&A** | These are examination-relevant event-window mechanics but overload the bridge. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 231–239 and 268 |
| Never-acquirers’ precise role | **Brief core phrase; fuller backup** | Core: identification is within firm. Backup: never-acquirers mainly identify calendar-time effects. | **THESIS FACT:** `_thesis_FLAT.tex`, line 231 |
| PRE2 as a “no pretrend” claim | **Do not state that way** | One PRE2 estimate is a limited check, not proof of no earlier pretrend or identification. | **THESIS FACT:** `_thesis_FLAT.tex`, lines 233, 237 and 288; audit lines 232–240 |
| Exact 50/50 cash/stock treatment | **Backup as unresolved verification item** | The thesis definitions overlap at exactly 50/50 and do not resolve treatment. Do not call the groups mutually exclusive. | **THESIS FACT:** `_thesis_FLAT.tex`, line 268; audit lines 129–139; ledger lines 296–298 |

### Proportionate wording for the generated-regressand limitation

**Recommended Act 2 sentence:**

> Because `UncResCEO` is estimated in the first stage, the conventional second-stage standard errors do not propagate that first-stage estimation uncertainty; I return to this in the limitations.

**Recommended later core-limitation sentence:**

> The reported second-stage inference is conventional and does not carry uncertainty from estimating `UncResCEO` through the two-step procedure.

**Backup/Q&A detail:** The thesis identifies a bootstrap or explicit two-step correction as an extension. **THESIS FACT:** [`_thesis_FLAT.tex`, line 227]

---

## 6. Q6 / W6 — Conceptual visualization jobs

These are explanatory jobs, not finished slides, layout directions, or a fixed visual quota.

### Essential job 1 — Decomposition and handoff

**DESIGN JUDGMENT:** Show one conceptual flow with two clearly separated stages:

1. Raw CEO Q&A uncertainty.
2. Predictable component: persistent CEO style plus included call/performance conditions.
3. Residual: `UncResCEO`.
4. Handoff into the acquisition event regressions.

The stage boundary should be explicit because the control sets and purposes differ. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 223–227 and 237]

**What it must not imply:** that the residual is “the deal,” “the CEO’s state,” or a fully purified causal shock.

### Essential job 2 — Disclosure clock with test jobs

**DESIGN JUDGMENT:** Show baseline → PRE2 → PRE1 → announcement boundary → GAP → completion boundary → POST, then label only the jobs of the three designs: run-up, announcement-versus-completion timing, and pooled cash-stock comparison. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 231–237 and 286; lines 630–636]

**What it must not imply:** announcement and completion are observation bins; PRE2 proves all pretrends are absent; or MA3 is a causal payment-method experiment.

### Useful if the later slide map has room — Sample funnel

**DESIGN JUDGMENT:** A compact flow from the 88,205-call panel to 44,900 residual observations to the design-specific first-result sample materially prevents denominator confusion. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 270, 506–508 and 571–579]

This job could be integrated with the stage-handoff visual or remain a separate narrative unit. That choice should be made only when the slide map is discussed.

### Do not use in the Act 2 core

- A decorative database-logo map.
- A full regression table.
- A control-variable constellation.
- A causal DAG that implies an identified mechanism.
- A repeated event clock with no new analytical job.

The audit independently recommends a decomposition visual, sample flow, and event-clock design, while warning against dense tables and decorative complexity. [`2026-07-13-master-reference-audit-report.md`, lines 304–331]

---

## 7. W5 — Adversarial thesis-fidelity and committee-comprehension audit

| Priority | Risk / likely objection | Exact correction or defense language | Thesis check |
|---:|---|---|---|
| 1 | **Critical — Mental-state attribution:** “So `UncResCEO` measures what the CEO knows or feels?” | “No. It is one operationalization of call-specific language uncertainty: a regression residual after included predictable components are removed. It is not a direct reading of knowledge or mental state.” | `_thesis_FLAT.tex`, lines 225–227 and 376–378 |
| 2 | **Critical — Deal attribution by construction:** “You residualized the deal out of the text?” | “No. The first stage contains no acquisition-event indicator. It constructs a call-specific residual; the second-stage event regressions test whether that residual is associated with acquisition timing.” | `_thesis_FLAT.tex`, lines 225 and 231–237 |
| 3 | **Critical — Measure ownership:** “Did this thesis invent `UncResCEO`?” | “No. The Dzieliński, Wagner, and Zeckhauser specification is re-estimated on this sample; the contribution is applying the residual around undisclosed acquisitions.” | `_thesis_FLAT.tex`, line 225 |
| 4 | **Critical — Control-layer confusion:** “Are the financial controls already inside the residual?” | “The first stage uses CEO/year effects plus language and performance controls. The second stage adds firm financial controls with firm and year-quarter effects. They are separate regressions with separate jobs.” | `_thesis_FLAT.tex`, lines 225 and 237 |
| 5 | **Critical — Generated-regressand inference:** “Do the reported standard errors include first-stage estimation error?” | “No. The second-stage standard errors are conventional and firm-clustered; the thesis does not propagate first-stage estimation uncertainty. A bootstrap or two-step correction is an extension.” | `_thesis_FLAT.tex`, lines 227, 231 and 239 |
| 6 | **Major — Denominator inflation:** “Are all results based on 88,205 calls?” | “No. That is the base language panel. `UncResCEO` is available for 44,900 observations, and the first cash-run-up uncertainty regression uses 27,622 firm-quarters across 1,248 firms. Each result carries its own denominator.” | `_thesis_FLAT.tex`, lines 270, 506–508 and 571–579 |
| 7 | **Major — Sample selection:** “What firms are lost?” | “Estimating speaking style requires at least five CEO calls and Execucomp coverage, shifting the uncertainty sample toward larger, better-covered firms; external validity is limited accordingly.” | `_thesis_FLAT.tex`, lines 239, 268–270 and 376–378 |
| 8 | **Major — Causal overreading:** “Do firm fixed effects identify the acquisition’s effect on speech?” | “No. They organize a within-firm descriptive contrast; timing is endogenous and no exogenous assignment or mechanism is identified.” | `_thesis_FLAT.tex`, lines 231, 237–239 and 376 |
| 9 | **Major — Residual as perfect purification:** “Have all ordinary sources of uncertainty been removed?” | “Only the included predictable components are removed. Time-varying omitted states can remain, which is why the interpretation stays correlational.” | `_thesis_FLAT.tex`, lines 225, 239 and 376–378 |
| 10 | **Major — Unit confusion:** “Is the unit a call or a firm-quarter?” | “The language measure is constructed at the call level and the acquisition tables report design-specific firm-quarter samples. Label the unit with every denominator.” | `_thesis_FLAT.tex`, lines 225, 231, 270 and 571–579 |
| 11 | **Major — Clock confusion:** “Are announcement and completion event bins?” | “No. They are boundaries. PRE1 precedes announcement, GAP lies after announcement but before closing, and POST follows completion.” | `_thesis_FLAT.tex`, lines 233 and 286 |
| 12 | **Major — Baseline ambiguity:** “Against what is PRE1 compared?” | “Against the firm’s own earlier ordinary quarters; in the event study the omitted baseline is `e ≤ −3` plus never-acquirers, which mainly help identify calendar-time effects.” | `_thesis_FLAT.tex`, lines 231 and 233; lines 630–636 |
| 13 | **Major — PRE2 overclaim:** “Does PRE2 prove there is no pretrend?” | “No. PRE2 is one limited pre-period check. It does not establish the absence of all earlier dynamics or causal identification.” | `_thesis_FLAT.tex`, lines 233, 237 and 288 |
| 14 | **Major — Cash/stock category overlap:** “Where does an exact 50/50 deal go?” | “The flattened thesis does not resolve that overlap. Keep it as a pre-defense verification item and avoid saying the groups are mutually exclusive.” | `_thesis_FLAT.tex`, line 268; audit lines 129–139 |
| 15 | **Minor — Methods density:** A spoken inventory of every source, variable, or coefficient obscures the bridge. | Explain the job of each stage; keep equations, full controls, data joins, replication estimates, and window mechanics in backup. | Thesis detail: `_thesis_FLAT.tex`, lines 223–270; design guardrail: audit lines 207–240 |
| 16 | **Minor — Abrupt result transition:** “Now here are the results” feels merely sequential. | Close on the question the design has just made estimable: “Within the same firm, is `UncResCEO` elevated in PRE1?” | Design judgment grounded in MA1: `_thesis_FLAT.tex`, lines 211, 231 and 274–276 |

### Audit verdict

**DESIGN JUDGMENT — Pass, conditional on the exact guardrails above.** The recommended Act 2 is thesis-faithful and committee-comprehensible if it:

- defines the residual without calling it a state, signal, mechanism, or purified deal measure;
- attributes the construction correctly;
- marks the first-stage/second-stage boundary;
- displays sample contraction;
- states within-firm/correlational interpretation;
- surfaces the generated-regressand limitation once now and again in the core limitations;
- introduces the clock by conceptual job rather than by technical window inventory.

If any of those conditions is removed, the proposal should be revised before it is converted into slides.

---

## 8. Direct answers to Q1–Q6

### Q1 — Minimum conceptual chain

**Answer:** Raw CEO Q&A uncertainty → persistent CEO style plus included predictable call factors → first-stage residual `UncResCEO` → sample-feasibility funnel → second-stage acquisition clock and within-firm tests → explicit correlational and generated-regressand boundaries. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 223–239, 268–270 and 376–378]

### Q2 — Best architecture

**Answer:** Architecture A, “answer first, then track it.” It answers Act 1’s transition immediately, preserves the two-stage distinction, and reaches the evidence without an intervening data inventory. This is a **DESIGN JUDGMENT** consistent with the approved disclosure spine and the audit’s measure/sample/design corrections. [`_CURRENT_HANDOFF_LEDGER.md`, lines 152–177; audit lines 207–240]

### Q3 — Sequence

**Answer:** Measure dependency first; then attribution and construct boundary; then sample funnel; then the stage handoff; then the disclosure clock; finally the three test jobs. These are narrative units, not a fixed slide count. The sequence follows the thesis’s methodological dependency: the residual must exist before it can become the outcome in MA1–MA3. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 223–239 and 260–270]

### Q4 — Caveat placement

**Answer:** State during Act 2 that the measure is an adapted, call-specific residual rather than a mental-state or deal measure; distinguish the two stages; acknowledge within-firm/correlational interpretation, selection, and non-propagated first-stage uncertainty. Revisit generated-regressand inference, word-list construct limits, selection/external validity, observational equivalence, and lack of mechanism in the later core limitations. Keep equations, bootstrapping detail, replication/validity tables, data joins, event-window mechanics, and exact 50/50 treatment in backup/Q&A. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 225–239, 243–249 and 376–380]

### Q5 — Closing transition

**Answer:**

> Once the predictable voice has been removed and every call is placed on the disclosure clock, the first empirical test follows directly: within the same firm, is `UncResCEO` elevated in PRE1—the final private quarter before a cash acquisition is announced?

This transition sets up H1/MA1, while reserving the announcement-versus-completion round trip for MA2 and the formal cash-stock difference for MA3. **THESIS FACT:** [`_thesis_FLAT.tex`, lines 211–217 and 231–237]

### Q6 — Conceptual visualizations

**Answer:** Use an essential decomposition-and-stage-handoff graphic and an essential disclosure-clock/test-job graphic. Add a sample funnel only if it cannot be integrated legibly with the handoff. No other conceptual visual has a distinct enough job before the statistical evidence. **THESIS FACT for encoded content:** [`_thesis_FLAT.tex`, lines 223–239, 268–270 and 286]

---

## 9. Unresolved choices intentionally left open

1. **UNRESOLVED CHOICE:** Whether the decomposition, stage handoff, and sample funnel occupy one narrative unit or more than one. This must be decided during the later slide-map discussion, not here.
2. **UNRESOLVED CHOICE:** Whether the full PRE2–PRE1–GAP–POST clock is formalized within Act 2 or introduced conceptually here and formalized immediately before MA2. The recommendation is to preview the full clock now but emphasize PRE1 for the first result.
3. **UNRESOLVED CHOICE:** Exact spoken duration. The approved rehearsal target is 17:30–18:00 for the full presentation, but no Act-level allocation should be locked before complete notes and rehearsal. [`_CURRENT_HANDOFF_LEDGER.md`, lines 507–509]
4. **UNRESOLVED CHOICE:** Exact treatment of deals that are precisely 50% cash and 50% stock. The thesis definitions do not resolve the overlap. [`_thesis_FLAT.tex`, line 268; `_CURRENT_HANDOFF_LEDGER.md`, lines 296–298]
5. **UNRESOLVED CHOICE:** Final slide titles, layouts, typography, and styling. They are outside this task.

---

## 10. Compact handoff for subsequent validation and discussion

**Proposal in one sentence:** Define `UncResCEO` by moving from raw CEO-answer uncertainty through a thesis-sample re-estimation of the DWZ decomposition, bound it as a call-specific generated residual, show the feasible sample, distinguish the two control stages, and then place the residual on the disclosure clock so MA1 becomes the next necessary question. **THESIS FACT for the encoded methodological chain:** [`_thesis_FLAT.tex`, lines 223–239 and 268–270]

**Approval decision requested later:** Approve, revise, or reject this Act 2 narrative architecture before any final slide map or implementation is created.
