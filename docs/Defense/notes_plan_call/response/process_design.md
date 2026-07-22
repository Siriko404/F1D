# Speaker Notes Production Process

## Deliverable boundary

This is a process for producing the full spoken scripts for the locked 13-slide defense. It does not contain speaker-note prose, sample lines, a deck redesign, or a thesis revision.

## Non-negotiable production rules

1. The thesis files are the sole authority for every number, result, academic claim, and interpretation.
2. The locked deck defines what may be explained on the podium. Appendix-only results, new mechanisms, and causal claims stay out.
3. The pre-rehearsal spoken-word ceiling is 2110. The honest measurement band is 2110 plus or minus about 180, but the asymmetry of error means the process drafts at or below 2110.
4. Slides 8 to 10 carry separate pointing pauses. Nonspoken cues are never counted as spoken words.
5. Slides 11 to 13 are drafted first and cannot be weakened to pay for earlier slides.
6. Full conditional onset-bias and PRE2 rebuttals remain in Q&A preparation, not podium notes.
7. No em dash or en dash may appear in audience-facing text.
8. Every call uses exactly two uploads, one prompt file and one zip, and exactly two downloads, one JSON and one zip.

## Standard call envelope

For unit Uxx, upload `Uxx_PROMPT.md` and `Uxx_INPUTS.zip`. Download `Uxx_RESPONSE.json` and `Uxx_OUTPUTS.zip`. The input zip contains all source files and dependency outputs needed by that unit. Nothing else is uploaded or downloaded loose. Integration units receive prior JSON files and extracted prior zip contents inside their single input zip.

Each response JSON must report status, input inventory, checks performed, failures, and an output-zip manifest. Each output zip contains only the substantive files named in the dispatch brief. A PARTIAL or BLOCKED unit cannot be consumed by a dependent unit until the named gap is repaired.

## Derived dimensions

| Dimension | What it checks | Live failure prevented | Grounding |
|---|---|---|---|
| Utterance-level thesis traceability | Every spoken number, result, literature statement, sample fact, and interpretation receives a trace ID that resolves to an exact thesis location. A silent thesis produces an explicit silence flag, not a plausible explanation. | It prevents the notes from inventing a rationale for the 2002 to 2018 endpoint, inventing quantified speaker-attribution accuracy, or repeating a ledger number that was previously conflated with a different variable. | "Every number, every quoted result and every academic claim in the notes must trace to an exact location in the thesis. Where the thesis is silent, the notes must say so rather than fill the gap." (WEB_REVIEW_REQUEST.json) |
| Slide-visible scope containment | Each spoken proposition is tied to a visible slide element and may clarify that element without importing appendix-only tests, new mechanisms, causal language, or extra results. | It prevents the large robustness appendix and side analyses in the thesis from leaking into an 18-minute podium script and turning the locked deck into a different argument. | "The notes may explain what is visible on the slide. They may not introduce a result, a mechanism, a causal claim or an appendix only analysis that the slide does not show." (WEB_REVIEW_REQUEST.json) |
| Residual-object and quarterly-state fidelity | The script consistently names the measured object as residual CEO-answer uncertainty and describes PRE2, PRE1, GAP, and POST as quarterly announcement-relative states rather than exact instants or direct knowledge readings. | It prevents the presenter from orally amplifying slide 12's locked wording into a claim that the method observes an exact point when knowledge changes. | "The sentence drops 'residual' and implies exact-point timing, although the estimated outcome is residual CEO-answer uncertainty observed on quarterly calls and grouped into announcement-relative states." (audit_findings.md) |
| Unobserved-onset bias discipline | Any discussion of negotiation onset distinguishes the observed announcement clock from the unobserved start of negotiations and refuses to assign a direction to misclassification bias without the missing assumptions. | It prevents the unsafe claim that onset contamination necessarily weakens the PRE1 estimate and therefore makes the result conservative. | "The design does not establish that unobserved negotiation-onset error must attenuate the PRE1 coefficient toward zero." (audit_findings.md) |
| PRE2 non-equivalence discipline | The notes treat the insignificant PRE2 coefficient as no statistically detected elevation, not as proof of no earlier drift, no pre-trend, or tightly identified negotiation timing. | It prevents an examiner from defeating an overstatement with an equivalence-test, power, or additional-leads question. | "A single statistically insignificant PRE2 coefficient does not establish that there is no pre-trend or that the signal is tightly timed." (audit_findings.md) |
| Cash-versus-stock estimand fidelity | The payment-method result is narrated from the pooled interaction and direct Wald contrast, while preserving the thesis's 'concentrated' language and the imprecision of the stock estimate. | It prevents the forbidden comparison of one significant coefficient with one insignificant coefficient and prevents the stronger, unsupported claim that the pattern is strictly cash-specific. | "The direct Wald difference, not two separate significance results, is the test." (rev22_slide_text.md) |
| Two-clock cash-GAP nuance | The slide 9 script distinguishes the information clock from the transaction clock and states cash persistence through GAP through the PRE1-to-GAP contrast, not through a significant GAP level. | It prevents the presenter from saying cash remains significantly elevated after announcement when the thesis reports a positive but insignificant GAP coefficient. | "the persistence of cash through the gap rests on the \emph{absence} of a \textit{PRE1}-to-\textit{GAP} decline, not on a significantly elevated gap level." (thesis_flat.tex) |
| Deictic chart pacing | Slides 8 to 10 receive a separate pointing plan for axes, markers, confidence intervals, and the minimum result features, with pause seconds excluded from the spoken-word allowance. | It prevents a word-compliant chart script from overrunning because the desk rate omitted the physical pauses needed to point at the projected figure. | "Walking a figure is the slowest thing a presenter does, because pointing inserts pauses that no word count predicts. It read fast because it was read at a desk with no projected figure to point at, so the pauses never happened." (SPEAKER_NOTES_BUDGET.md) |
| Podium and Q&A boundary control | The two conditional rebuttals are indexed for Q&A but excluded from the podium script; slide 12 names the limitations without preemptively litigating them. | It prevents spending roughly seventy seconds defending attacks that may never be made, while also preventing the two rebuttals from drifting back into unsafe unconditional forms. | "The full conditional rebuttals live in the Q&A preparation, not in the podium notes." (SPEAKER_NOTES_BUDGET.md) |
| Terminal-slide budget protection | Word allocation, drafting order, and cuts protect slides 11 to 13 so contribution, limitations, and conclusion are complete and unrushed even if earlier slides expand. | It prevents the common local optimization in which early slides feel complete but consume the time and energy reserved for the most consequential closing slides. | "Overrunning a slide's count is not a rounding error. It is time taken from a later slide, and the later slides are the limitations and contribution, which are the ones that must not be rushed." (SPEAKER_NOTES_BUDGET.md) |
| Presenter-owned sentence architecture | The scripts use complete, short, speakable sentences, explain the actual empirical case without analogies, and keep one audience job per slide rather than packing every available qualification into prose. | It prevents a technically accurate script from becoming a dense wall the exhausted presenter cannot internalize and therefore begins to paraphrase unsafely under pressure. | "NO analogies. Explain the ACTUAL case. Short sentences. Many small titled sections. Lists over prose. "One idea" beats completeness. Verbose enough to walk each step, never a wall." (DEFENSE_LEDGER.md) |
| Transition debt | Every slide boundary has a defined logical handoff, one written cross-slide bridge, an assigned word-budget owner, and a last-sentence/first-sentence continuity check. | It prevents the talk from sounding like thirteen isolated mini-presentations, especially at the critical handoffs from measure to finding, timing to payment method, result to contribution, and limitation to conclusion. | "How does the process handle the transition between slides, which is where a talk audibly falls apart and which no per slide budget covers?" (WEB_REVIEW_REQUEST.json) |

## Dimensions considered and rejected

- **Generic delivery mechanics:** Breathing, posture, clothing, remote handling, and eye contact may matter, but they do not change the written-note production process and are explicitly out of scope.
- **Deck visual redesign:** The deck is locked and already audited. Reopening layout would create uncontrolled scope, invalidate continuity, and distract from the missing spoken layer.
- **Thesis revision or new analysis:** The thesis is submitted and is the authority. A process that fixes silence by changing the thesis would evade rather than solve the note-design problem.
- **Exhaustive robustness narration:** The thesis contains extensive robustness material, but importing it into podium notes violates the visible-slide rule and the word budget. Relevant defenses remain Q&A assets.
- **Charisma or confidence as a standalone score:** It is not artifact-verifiable and can reward stronger delivery of an overclaim. The process instead checks speakability, ownership, and rehearsal evidence.
- **A complete new Q&A bank:** The ledger already contains a question bank. This process only controls the interface between podium notes and Q&A, including the two conditional rebuttals.
- **Maximum detail:** Completeness is not the objective under a measured 18-minute ceiling. The process uses one job per slide and a cut hierarchy, retaining exactness while rejecting low-value detail.
- **Memorization as a drafting dimension:** Internalization matters, but it cannot be certified from text. It is handled as a rehearsal gate and a defense risk, not falsely scored by a writing call.

## Process architecture

The full process is 13 planned calls in seven waves. One failed signoff can add a bounded two-call loop by repeating U12 and U13.

1. Wave A: U01, U02, and U03 run concurrently.
2. Wave B: U04 integrates U01 and U02.
3. Wave C: U05, U06, U07, and U08 run concurrently. Dispatch U05 first, then launch the other three.
4. Wave D: U09 assembles the frozen full candidate and writes cross-slide bridges.
5. Wave E: U10 and U11 audit the same frozen candidate concurrently.
6. Wave F: U12 performs controlled repairs.
7. Human gate: one uninterrupted rehearsal with the real deck produces the completed rehearsal log.
8. Wave G: U13 issues PASS or FAIL. FAIL returns to U12 and then U13.

## Phase 1: Derive evidence, architecture, and risk controls

**Purpose:** Turn the thesis, locked deck, measured budget, prior audit, and committee ledger into explicit pre-draft contracts so drafting is constrained before attractive prose exists.

**If skipped:** Drafting begins from memory and visual impression. The writer then self-grades, thesis-silent gaps are plausibly filled, chart pauses disappear from the budget, and late slides remain unprotected.

### Units

#### U01: Build the claim and scope ledger

**Assignment:** Create a proposition-level ledger for all 13 slides. For every visible number, result, academic claim, sample fact, and interpretation that the eventual script may need, record the visible anchor, exact thesis source, permitted claim ceiling, forbidden expansion, and whether the thesis is silent. Include explicit rows for speaker-attribution accuracy, the 2002 to 2018 endpoint rationale, residual versus raw uncertainty, PRE2, negotiation onset, the cash GAP coefficient, the cash-versus-stock Wald test, novelty hedging, and the three unapplied deck-audit findings. Do not draft speaker notes.

**Inputs:** Core source archive: thesis_flat.tex, thesis_tables.tex, thesis_robustness_tables.tex, rev22_deck.pdf, rev22_slide_text.md, SPEAKER_NOTES_BUDGET.md, DEFENSE_LEDGER.md, rev22audit_response.json, audit_findings.md, REV22_CHANGE_LOG.md

**Returns:** A call-status JSON plus a zip containing claim_scope_ledger.csv, source_silence_register.md, and u01_acceptance_report.md.

**Check:** Reject the unit unless all 13 slides are represented, every numeric row resolves to an exact thesis location, each open item is explicit, and no ledger, audit, or deck text is treated as higher authority than the thesis.

#### U02: Build the spoken architecture, budget, and transition contract

**Assignment:** Design the non-prose architecture for the 13 scripts. For each slide define one audience job, must-land content, optional support, first-cut content, target words, ten-percent stopwatch corridor, seconds, register, pause allowance, and transition interface. For slides 8 to 10 define pointing beats separately from spoken words. Charge each cross-slide transition to the incoming slide. Preserve slides 11 to 13 before allocating discretionary words elsewhere. Do not draft speaker notes.

**Inputs:** Core source archive: rev22_deck.pdf, rev22_slide_text.md, SPEAKER_NOTES_BUDGET.md, SPEAKING_RATE_TEST.md, DEFENSE_LEDGER.md, WEB_REVIEW_REQUEST.json

**Returns:** A call-status JSON plus a zip containing spoken_architecture.csv, transition_interfaces.csv, chart_pointing_plan.csv, and u02_budget_proof.md.

**Check:** Reject the unit unless the word targets sum to 2110, the pre-rehearsal ceiling is 2110, chart pauses remain time rather than words, every slide has exactly one job and a cut order, and all 12 boundaries have an owner and purpose.

#### U03: Build an independent examiner-attack and podium-boundary map

**Assignment:** Act as an adversarial examiner, not a drafter. Identify the exact oral overclaims or ambiguities most likely to be attacked in this locked deck, using the prior audit and committee ledger. Separate podium obligations from Q&A-only defenses. Confirm the conditional placement of the onset-bias and PRE2 rebuttals. Include the locked slide 12 wording, the 'Imperfect instruments' ambiguity, the residual/exact-point issue, the cash GAP nuance, and the cash-versus-stock comparison. Do not write speaker notes or prepared answer prose.

**Inputs:** Core source archive: rev22_deck.pdf, rev22_slide_text.md, DEFENSE_LEDGER.md, rev22audit_response.json, audit_findings.md, REV22_CHANGE_LOG.md, thesis_flat.tex, thesis_tables.tex, SPEAKER_NOTES_BUDGET.md

**Returns:** A call-status JSON plus a zip containing examiner_attack_map.csv, podium_qa_boundary.csv, and u03_risk_report.md.

**Check:** Reject the unit if it merely repeats the audit, if an attack lacks a deck location and thesis ceiling, or if either conditional rebuttal is moved into the podium script without a quantified time cost.

#### U04: Integrate the drafting contract

**Assignment:** Merge U01 and U02 into one 13-slide drafting contract. Resolve any conflict in favor of thesis authority first, then visible-slide scope, then the measured budget. Each slide contract must specify its audience job, exact claim IDs, mandatory content, prohibited content, target and corridor, cut order, transition interface, and acceptance tests. Preserve source-silence flags. This unit produces specifications only, not note text.

**Inputs:** Core source archive plus the complete U01 and U02 output zips and response JSONs, all packaged inside one input zip

**Returns:** A call-status JSON plus a zip containing drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, automated_checks_spec.md, and u04_conflict_log.md.

**Check:** Reject the unit unless there are exactly 13 slide contracts, every mandatory proposition has a trace ID, all 12 transitions are specified but not yet worded, and the contract can be split into four drafting bundles without hidden cross-bundle assumptions.

**Phase exit:** U01, U02, and U03 pass their own checks; U04 then contains exactly 13 drafting contracts, 12 transition interfaces, a 2110-word total, protected terminal slides, explicit source-silence flags, and no prose speaker notes.

## Phase 2: Draft complete scripts in independent bundles

**Purpose:** Produce all 13 full spoken scripts with bounded context, parallel wall-clock execution, and terminal slides secured first.

**If skipped:** There are no notes. If this phase is performed serially from slide 1, fatigue and schedule pressure are most likely to leave slides 11 to 13 unfinished or rushed.

### Units

#### U05: Draft slides 11 to 13 first

**Assignment:** Write the complete spoken scripts for slides 11, 12, and 13 from the approved drafting contract. Use full sentences and no em dash or en dash. Stay within each slide's corridor and the bundle total. Keep the contribution distinct from a result recap, keep the limitations descriptive and noncausal, and preserve the approved conclusion hedge. Do not insert the two full conditional rebuttals. Attach trace IDs to a separate trace file, not inside the spoken script.

**Inputs:** Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, and automated_checks_spec.md in one input zip

**Returns:** A call-status JSON plus a zip containing notes_11_13.md, trace_11_13.csv, counts_11_13.csv, entry_exit_11_13.json, and u05_self_check.md.

**Check:** Reject the unit if any slide is missing, if spoken text contains a forbidden dash, if a claim lacks a trace ID, if slide 12 contains the full rebuttals, or if the three scripts exceed their protected allocation.

#### U06: Draft slides 1 to 4

**Assignment:** Write the complete spoken scripts for slides 1 through 4 from the approved drafting contract. Establish the problem, the two-clock intuition, and the research questions without causal or mechanism inflation. Use full, short sentences and no em dash or en dash. Keep trace IDs outside the spoken script and return explicit entry and exit intents for later cross-bundle integration.

**Inputs:** Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, and automated_checks_spec.md in one input zip

**Returns:** A call-status JSON plus a zip containing notes_01_04.md, trace_01_04.csv, counts_01_04.csv, entry_exit_01_04.json, and u06_self_check.md.

**Check:** Reject the unit if the motivation outruns the thesis, any literature or sample claim is untraced, research questions are converted into causal hypotheses, or the bundle violates its word allocation.

#### U07: Draft slides 5 to 7

**Assignment:** Write the complete spoken scripts for slides 5 through 7 from the approved drafting contract. Narrate the literature cell, sample narrowing, and residual-measure construction in plain language while retaining exact methodological meaning. Use the thesis's novelty hedge and distinguish first-stage residualization from second-stage fixed-effect designs. Use full sentences and no em dash or en dash. Keep trace IDs outside spoken text.

**Inputs:** Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, and automated_checks_spec.md in one input zip

**Returns:** A call-status JSON plus a zip containing notes_05_07.md, trace_05_07.csv, counts_05_07.csv, entry_exit_05_07.json, and u07_self_check.md.

**Check:** Reject the unit if residual uncertainty is described as raw uncertainty, if the sample endpoint is rationalized beyond the thesis, if speaker-attribution accuracy is invented, if novelty is asserted without its hedge, or if the bundle violates its allocation.

#### U08: Draft slides 8 to 10

**Assignment:** Write the complete spoken scripts for slides 8 through 10 from the approved drafting contract. Build a separate nonspoken pointing sequence for each figure. Preserve the PRE2 limitation, the PRE1-to-GAP information-clock contrast, the cash GAP nuance, and the pooled cash-versus-stock Wald estimand. Use full sentences and no em dash or en dash. Do not infer significance from comparing separate stars. Keep trace IDs and pointing cues outside spoken text.

**Inputs:** Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, chart requirements, and automated_checks_spec.md in one input zip

**Returns:** A call-status JSON plus a zip containing notes_08_10.md, trace_08_10.csv, counts_08_10.csv, entry_exit_08_10.json, chart_cues_08_10.csv, and u08_self_check.md.

**Check:** Reject the unit if PRE2 becomes proof of no pre-trend, cash is said to have a significantly elevated GAP level, cash-versus-stock is argued from separate significance, chart cues are counted as spoken words, or pause allowances are ignored.

**Phase exit:** All four bundles pass, every slide has a complete script and separate trace file, slide-level counts remain in corridor, chart cues are nonspoken, no forbidden dash is present, and U05 was dispatched first so the ending exists even if later calls are interrupted.

## Phase 3: Integrate once, then audit from two independent perspectives

**Purpose:** Create one coherent talk and then prevent the assembler from certifying its own evidence, inference, timing, and listener-load decisions.

**If skipped:** Bundle seams remain audible, transitions are unpaid word debt, duplicate framing inflates time, and a polished script can preserve the exact overclaims the previous deck audit showed authors miss in their own work.

### Units

#### U09: Assemble the full script and write cross-slide bridges

**Assignment:** Assemble U05 through U08 into one 13-slide candidate without silently rewriting claims. Write exactly one functional bridge at every slide boundary using the transition contract, charge its words to the incoming slide, and remove repeated openings or conclusions. Rebalance only by removing or replacing complete lowest-priority thoughts, never by stripping necessary qualifications or converting sentences into fragments. Preserve trace IDs in a separate file.

**Inputs:** Core source archive, U04 contract outputs, and all U05 through U08 output zips and response JSONs, packaged inside one input zip

**Returns:** A call-status JSON plus a zip containing full_notes_candidate.md, full_trace.csv, word_budget.csv, transition_register.csv, chart_cue_map.csv, assembly_diff.md, and u09_acceptance_report.md.

**Check:** Reject the unit unless all 13 scripts appear in order, all 12 bridges are present, the global spoken count is at most 2110 before rehearsal, each slide is inside its corridor or has a documented neutral transfer, slides 11 to 13 remain protected, and no trace was lost during assembly.

#### U10: Run the independent evidence and inference audit

**Assignment:** Audit the assembled script sentence by sentence against the thesis and locked deck. Classify every spoken sentence as transition, visible explanation, thesis fact, number, result, interpretation, or limitation. Verify every claim trace and find any scope breach. Explicitly test residual-object wording, exact-point implications, negotiation onset, attenuation direction, PRE2, the cash GAP level, pooled cash-versus-stock comparison, novelty, causality, mechanisms, source-silent questions, and unapplied deck-audit findings. Report findings only; do not repair the script.

**Inputs:** Core source archive, U09 full candidate and trace files, and U03 examiner-attack outputs in one input zip. In minimum-viable mode, omit U03 and derive the reduced attack list directly from audit_findings.md.

**Returns:** A call-status JSON plus a zip containing sentence_evidence_matrix.csv, evidence_findings.json, scope_findings.csv, and u10_audit_summary.md.

**Check:** Reject the audit if any spoken sentence is unclassified, any number is sampled rather than exhaustively checked, findings lack exact script and source locations, or the auditor edits the script it is judging.

#### U11: Run the independent timing, speakability, transition, and surface audit

**Assignment:** Audit the assembled script without changing it. Count spoken words per slide and globally, scan every audience-facing character for em dash and en dash, verify complete sentences, detect dense clauses and duplicate setup, test the last sentence and first sentence at every boundary as a pair, and compare chart pointing beats with pause allowances. Perform a blind one-job test: infer each slide's audience job from the script and compare it with the contract. Report findings only.

**Inputs:** U09 full candidate, word budget, transition register, chart cue map, U04 drafting contract, SPEAKER_NOTES_BUDGET.md, SPEAKING_RATE_TEST.md, and the locked deck in one input zip

**Returns:** A call-status JSON plus a zip containing timing_surface_findings.json, word_recount.csv, transition_test.csv, chart_pacing_test.csv, speakability_flags.csv, and u11_audit_summary.md.

**Check:** Reject the audit if it treats 2110 as a target rather than a pre-rehearsal ceiling, counts nonspoken cues as words, omits a character scan, fails to inspect all 12 boundaries, or rewrites the candidate.

**Phase exit:** U09 yields one 13-slide candidate with 12 bridges and full traces. U10 and U11 then independently inspect the frozen candidate, return findings rather than edits, and cover every sentence, slide boundary, chart beat, word count, and audience-facing character.

## Phase 4: Repair under change control

**Purpose:** Convert audit findings into a single revised script without allowing local fixes to create new claim, timing, or transition failures elsewhere.

**If skipped:** Known major errors remain, or multiple editors make untracked changes that break source traces, word totals, and terminal-slide protection.

### Units

#### U12: Apply controlled repairs

**Assignment:** Repair the candidate using U10 and U11 findings. Resolve every critical and major finding and explicitly adjudicate each minor one. Preserve thesis meaning and visible-slide scope. When length is high, remove a complete lowest-priority thought and rebuild the local bridge rather than compressing qualifications into fragments. Re-run the deterministic checks after revision. Produce a sentence-level change log showing the finding, action, trace impact, and word impact.

**Inputs:** Core source archive, U09 candidate package, U10 audit package, and U11 audit package in one input zip. In minimum-viable mode, U11 may be absent, but the unit must run the basic word, transition, and forbidden-character tests itself.

**Returns:** A call-status JSON plus a zip containing full_notes_repaired.md, full_trace_repaired.csv, word_budget_repaired.csv, transition_register_repaired.csv, chart_cue_map_repaired.csv, audit_resolution.csv, revision_diff.md, and rehearsal_log_template.csv.

**Check:** Reject the unit if any critical or major item remains open, a repair creates an untraced claim, an essential hedge is cut for length, the global count exceeds 2110, a forbidden dash remains, or slides 11 to 13 are weakened to pay for earlier slides.

**Phase exit:** Every critical and major audit item is resolved, each change has source and word-impact records, deterministic checks pass, total words do not exceed 2110, and a rehearsal-ready package plus log template exists.

## Phase 5: Rehearse against the real deck and sign off

**Purpose:** Replace the unverified delivery discount with actual evidence and catch filler, improvisation, chart-pointing delay, and transition breakdown before declaring the notes finished.

**If skipped:** A word-compliant script can still run long, and the presenter may add filler or unsafe paraphrases that no document audit can see.

### Units

#### U13: Rehearsal-backed final signoff

**Assignment:** Perform final signoff on the repaired scripts using the completed full-deck rehearsal log. Re-run exhaustive claim, scope, word, character, transition, and chart-cue checks. Compare actual per-slide and total time with the budget, count filler and unscripted additions, and verify that the presenter used the actual projected figures for chart pacing. Return PASS only if every hard gate passes. Otherwise return FAIL with a bounded repair order that can be sent back through U12; do not issue a conditional pass.

**Inputs:** Core source archive, all U12 repaired outputs, completed rehearsal_log.csv, and any rehearsal transcript or recording packaged inside one input zip

**Returns:** A call-status JSON plus a zip containing final_signoff.json, final_notes_package.zip, final_trace.csv, final_word_and_time_report.csv, final_transition_report.csv, and signoff_failures.md.

**Check:** PASS requires 13 complete scripts; zero untraced numbers or academic claims; zero slide-scope breaches; zero em dash or en dash; global words between 1930 and 2110; actual full-deck elapsed time at or below 18:00; all 12 transition tests passed; chart pauses executed; no unsafe onset, PRE2, GAP, Wald, novelty, causal, or mechanism language; no fabricated answers to source-silent items; and no unresolved critical or major audit finding.

**Phase exit:** The presenter completes one uninterrupted rehearsal with the real deck and records per-slide time, total time, filler, stumbles, additions, and chart pauses. U13 returns PASS only when every documentary and measured gate passes; FAIL routes a bounded list back to U12 and then repeats U13.

## Word-budget mechanism

The process does not write freely and compress later. U02 first assigns one audience job, mandatory content, optional support, and a first-cut tier to every slide. The ten-percent slide corridor reflects the stopwatch precision reported in the budget file. U04 locks those choices before prose exists.

Drafting uses complete sentences. If a bundle is long, the first response is to remove a complete lowest-priority thought. The local bridge is then rewritten. Necessary qualifiers are never shaved into fragments. U09 may make a neutral transfer within a section only when it documents both sides and keeps the global count at or below 2110. Slides 11 to 13 are not donors. U11 independently recounts. U12 repeats the count after every repair.

## Transition mechanism

U02 defines each boundary as an interface: the outgoing question or completed job, the incoming job, and the word-budget owner. Draft units return entry and exit intents but do not write cross-bundle bridges. U09 writes one bridge per boundary and charges its words to the incoming slide. U11 tests each last-sentence and first-sentence pair in isolation. A bridge fails when it only repeats content, introduces an untraced claim, or does not make the next slide logically necessary.

## Placement of the two conditional rebuttals

The Q&A placement is correct. The pair takes about 129 words and roughly seventy seconds in the measured hedged register. Slide 12 has 120 words and sixty seconds for all four limitations. Putting the pair on the podium would make the allocation impossible and spend time answering attacks that may never occur. The process keeps their logic in the examiner-attack map and fails any podium draft that includes the full defenses or converts them into unconditional claims.

## Final signoff gates

U13 returns PASS only when all of the following are true:

- All 13 slide scripts are complete and ordered.
- Every spoken number and academic claim has an exact thesis trace.
- Every sentence remains inside visible-slide scope.
- There is no em dash or en dash in audience-facing text.
- Global spoken words are between 1930 and 2110, with per-slide deviations documented.
- One uninterrupted full-deck rehearsal finishes at or below 18:00.
- The rehearsal log includes per-slide time, filler, unscripted additions, stumbles, transition breaks, and chart-pause execution.
- All 12 transition tests pass.
- Slides 8 to 10 execute the planned pointing pauses without counting cues as words.
- No script signs onset bias, treats PRE2 as equivalence, overstates the cash GAP level, compares separate stars, invents source-silent facts, asserts a causal mechanism, or removes required novelty and conclusion hedges.
- No critical or major audit finding remains open.

Any failed gate produces FAIL and a bounded return to U12. There is no conditional pass.

## Minimum viable subset

The minimum viable subset is U01, U02, U04, U05, U06, U07, U08, U09, U10, U12, and U13, plus the human rehearsal. It omits the separate U03 attack map and the independent U11 timing and speakability audit. U10 and U13 must perform reduced versions of those checks. This path is still usable only if U13 passes. No drafting bundle can be omitted, because missing slides make the podium script unusable.

## Most likely process failure

The most likely failure is a skipped or thin rehearsal log. That would allow the operator to declare the documents complete while the delivery discount, filler, chart delays, and improvised overclaims remain unmeasured. U13 therefore treats missing per-slide rehearsal evidence as an automatic failure.

## What this process does not check

- Actual transcript-vendor speaker-attribution accuracy, because no quantified validation is supplied.
- Why the approved sample ends in 2018, because the thesis states no rationale.
- A redesign of the locked slide 12 sentence or the locked 'Imperfect instruments' heading.
- A complete Q&A answer bank beyond podium-boundary control and indexing of the two conditional rebuttals.
- Room hardware, projection reliability, remote operation, audio level, or back-row slide legibility.
- Breathing, posture, clothing, eye contact, and other delivery mechanics.
- The committee's actual questions, mood, interruptions, or enforcement of time.
- Whether internalization survives acute stress; rehearsal provides evidence but not a guarantee.
