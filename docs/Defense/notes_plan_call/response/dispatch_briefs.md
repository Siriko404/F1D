# Dispatch Briefs

## Shared protocol for every unit

Upload exactly two files: the unit prompt and one input zip. Download exactly two files: one response JSON and one output zip. Do not return loose files. Read every file inside the input zip before reasoning. Inventory every input file with byte size and read status in the response JSON. Follow the authority hierarchy. Return PARTIAL or BLOCKED rather than guessing.

Pre-draft and audit units must not draft speaker-note prose. Draft units must produce full spoken scripts only for their assigned slides. All trace IDs, cut tags, and pointing cues belong in separate files, not in audience-facing script text.

The operator should preserve every unit response JSON and extract every unit output zip into the next dependency's input zip. The next call still receives only one prompt file and one zip.

## U01: Build the claim and scope ledger

### Dispatch assignment

Create a proposition-level ledger for all 13 slides. For every visible number, result, academic claim, sample fact, and interpretation that the eventual script may need, record the visible anchor, exact thesis source, permitted claim ceiling, forbidden expansion, and whether the thesis is silent. Include explicit rows for speaker-attribution accuracy, the 2002 to 2018 endpoint rationale, residual versus raw uncertainty, PRE2, negotiation onset, the cash GAP coefficient, the cash-versus-stock Wald test, novelty hedging, and the three unapplied deck-audit findings. Do not draft speaker notes.

### Input files

- Upload prompt: `U01_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U01_INPUTS.zip` containing Core source archive: thesis_flat.tex, thesis_tables.tex, thesis_robustness_tables.tex, rev22_deck.pdf, rev22_slide_text.md, SPEAKER_NOTES_BUDGET.md, DEFENSE_LEDGER.md, rev22audit_response.json, audit_findings.md, REV22_CHANGE_LOG.md.

### Required return

- Download JSON: `U01_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U01_OUTPUTS.zip`. claim_scope_ledger.csv, source_silence_register.md, and u01_acceptance_report.md.

### Acceptance check

Reject the unit unless all 13 slides are represented, every numeric row resolves to an exact thesis location, each open item is explicit, and no ledger, audit, or deck text is treated as higher authority than the thesis.

**Concurrency:** May run with U02, U03.

## U02: Build the spoken architecture, budget, and transition contract

### Dispatch assignment

Design the non-prose architecture for the 13 scripts. For each slide define one audience job, must-land content, optional support, first-cut content, target words, ten-percent stopwatch corridor, seconds, register, pause allowance, and transition interface. For slides 8 to 10 define pointing beats separately from spoken words. Charge each cross-slide transition to the incoming slide. Preserve slides 11 to 13 before allocating discretionary words elsewhere. Do not draft speaker notes.

### Input files

- Upload prompt: `U02_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U02_INPUTS.zip` containing Core source archive: rev22_deck.pdf, rev22_slide_text.md, SPEAKER_NOTES_BUDGET.md, SPEAKING_RATE_TEST.md, DEFENSE_LEDGER.md, WEB_REVIEW_REQUEST.json.

### Required return

- Download JSON: `U02_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U02_OUTPUTS.zip`. spoken_architecture.csv, transition_interfaces.csv, chart_pointing_plan.csv, and u02_budget_proof.md.

### Acceptance check

Reject the unit unless the word targets sum to 2110, the pre-rehearsal ceiling is 2110, chart pauses remain time rather than words, every slide has exactly one job and a cut order, and all 12 boundaries have an owner and purpose.

**Concurrency:** May run with U01, U03.

## U03: Build an independent examiner-attack and podium-boundary map

### Dispatch assignment

Act as an adversarial examiner, not a drafter. Identify the exact oral overclaims or ambiguities most likely to be attacked in this locked deck, using the prior audit and committee ledger. Separate podium obligations from Q&A-only defenses. Confirm the conditional placement of the onset-bias and PRE2 rebuttals. Include the locked slide 12 wording, the 'Imperfect instruments' ambiguity, the residual/exact-point issue, the cash GAP nuance, and the cash-versus-stock comparison. Do not write speaker notes or prepared answer prose.

### Input files

- Upload prompt: `U03_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U03_INPUTS.zip` containing Core source archive: rev22_deck.pdf, rev22_slide_text.md, DEFENSE_LEDGER.md, rev22audit_response.json, audit_findings.md, REV22_CHANGE_LOG.md, thesis_flat.tex, thesis_tables.tex, SPEAKER_NOTES_BUDGET.md.

### Required return

- Download JSON: `U03_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U03_OUTPUTS.zip`. examiner_attack_map.csv, podium_qa_boundary.csv, and u03_risk_report.md.

### Acceptance check

Reject the unit if it merely repeats the audit, if an attack lacks a deck location and thesis ceiling, or if either conditional rebuttal is moved into the podium script without a quantified time cost.

**Concurrency:** May run with U01, U02.

## U04: Integrate the drafting contract

### Dispatch assignment

Merge U01 and U02 into one 13-slide drafting contract. Resolve any conflict in favor of thesis authority first, then visible-slide scope, then the measured budget. Each slide contract must specify its audience job, exact claim IDs, mandatory content, prohibited content, target and corridor, cut order, transition interface, and acceptance tests. Preserve source-silence flags. This unit produces specifications only, not note text.

### Input files

- Upload prompt: `U04_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U04_INPUTS.zip` containing Core source archive plus the complete U01 and U02 output zips and response JSONs, all packaged inside one input zip.

### Required return

- Download JSON: `U04_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U04_OUTPUTS.zip`. drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, automated_checks_spec.md, and u04_conflict_log.md.

### Acceptance check

Reject the unit unless there are exactly 13 slide contracts, every mandatory proposition has a trace ID, all 12 transitions are specified but not yet worded, and the contract can be split into four drafting bundles without hidden cross-bundle assumptions.

**Real dependencies:** U01, U02.

## U05: Draft slides 11 to 13 first

### Dispatch assignment

Write the complete spoken scripts for slides 11, 12, and 13 from the approved drafting contract. Use full sentences and no em dash or en dash. Stay within each slide's corridor and the bundle total. Keep the contribution distinct from a result recap, keep the limitations descriptive and noncausal, and preserve the approved conclusion hedge. Do not insert the two full conditional rebuttals. Attach trace IDs to a separate trace file, not inside the spoken script.

### Input files

- Upload prompt: `U05_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U05_INPUTS.zip` containing Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, and automated_checks_spec.md in one input zip.

### Required return

- Download JSON: `U05_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U05_OUTPUTS.zip`. notes_11_13.md, trace_11_13.csv, counts_11_13.csv, entry_exit_11_13.json, and u05_self_check.md.

### Acceptance check

Reject the unit if any slide is missing, if spoken text contains a forbidden dash, if a claim lacks a trace ID, if slide 12 contains the full rebuttals, or if the three scripts exceed their protected allocation.

**Concurrency:** May run with U06, U07, U08.

**Real dependencies:** U04.

## U06: Draft slides 1 to 4

### Dispatch assignment

Write the complete spoken scripts for slides 1 through 4 from the approved drafting contract. Establish the problem, the two-clock intuition, and the research questions without causal or mechanism inflation. Use full, short sentences and no em dash or en dash. Keep trace IDs outside the spoken script and return explicit entry and exit intents for later cross-bundle integration.

### Input files

- Upload prompt: `U06_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U06_INPUTS.zip` containing Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, and automated_checks_spec.md in one input zip.

### Required return

- Download JSON: `U06_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U06_OUTPUTS.zip`. notes_01_04.md, trace_01_04.csv, counts_01_04.csv, entry_exit_01_04.json, and u06_self_check.md.

### Acceptance check

Reject the unit if the motivation outruns the thesis, any literature or sample claim is untraced, research questions are converted into causal hypotheses, or the bundle violates its word allocation.

**Concurrency:** May run with U05, U07, U08.

**Real dependencies:** U04.

## U07: Draft slides 5 to 7

### Dispatch assignment

Write the complete spoken scripts for slides 5 through 7 from the approved drafting contract. Narrate the literature cell, sample narrowing, and residual-measure construction in plain language while retaining exact methodological meaning. Use the thesis's novelty hedge and distinguish first-stage residualization from second-stage fixed-effect designs. Use full sentences and no em dash or en dash. Keep trace IDs outside spoken text.

### Input files

- Upload prompt: `U07_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U07_INPUTS.zip` containing Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, and automated_checks_spec.md in one input zip.

### Required return

- Download JSON: `U07_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U07_OUTPUTS.zip`. notes_05_07.md, trace_05_07.csv, counts_05_07.csv, entry_exit_05_07.json, and u07_self_check.md.

### Acceptance check

Reject the unit if residual uncertainty is described as raw uncertainty, if the sample endpoint is rationalized beyond the thesis, if speaker-attribution accuracy is invented, if novelty is asserted without its hedge, or if the bundle violates its allocation.

**Concurrency:** May run with U05, U06, U08.

**Real dependencies:** U04.

## U08: Draft slides 8 to 10

### Dispatch assignment

Write the complete spoken scripts for slides 8 through 10 from the approved drafting contract. Build a separate nonspoken pointing sequence for each figure. Preserve the PRE2 limitation, the PRE1-to-GAP information-clock contrast, the cash GAP nuance, and the pooled cash-versus-stock Wald estimand. Use full sentences and no em dash or en dash. Do not infer significance from comparing separate stars. Keep trace IDs and pointing cues outside spoken text.

### Input files

- Upload prompt: `U08_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U08_INPUTS.zip` containing Core source archive plus U04 drafting_contract.csv, claim_trace_pack.csv, transition_contract.csv, chart requirements, and automated_checks_spec.md in one input zip.

### Required return

- Download JSON: `U08_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U08_OUTPUTS.zip`. notes_08_10.md, trace_08_10.csv, counts_08_10.csv, entry_exit_08_10.json, chart_cues_08_10.csv, and u08_self_check.md.

### Acceptance check

Reject the unit if PRE2 becomes proof of no pre-trend, cash is said to have a significantly elevated GAP level, cash-versus-stock is argued from separate significance, chart cues are counted as spoken words, or pause allowances are ignored.

**Concurrency:** May run with U05, U06, U07.

**Real dependencies:** U04.

## U09: Assemble the full script and write cross-slide bridges

### Dispatch assignment

Assemble U05 through U08 into one 13-slide candidate without silently rewriting claims. Write exactly one functional bridge at every slide boundary using the transition contract, charge its words to the incoming slide, and remove repeated openings or conclusions. Rebalance only by removing or replacing complete lowest-priority thoughts, never by stripping necessary qualifications or converting sentences into fragments. Preserve trace IDs in a separate file.

### Input files

- Upload prompt: `U09_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U09_INPUTS.zip` containing Core source archive, U04 contract outputs, and all U05 through U08 output zips and response JSONs, packaged inside one input zip.

### Required return

- Download JSON: `U09_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U09_OUTPUTS.zip`. full_notes_candidate.md, full_trace.csv, word_budget.csv, transition_register.csv, chart_cue_map.csv, assembly_diff.md, and u09_acceptance_report.md.

### Acceptance check

Reject the unit unless all 13 scripts appear in order, all 12 bridges are present, the global spoken count is at most 2110 before rehearsal, each slide is inside its corridor or has a documented neutral transfer, slides 11 to 13 remain protected, and no trace was lost during assembly.

**Real dependencies:** U05, U06, U07, U08.

## U10: Run the independent evidence and inference audit

### Dispatch assignment

Audit the assembled script sentence by sentence against the thesis and locked deck. Classify every spoken sentence as transition, visible explanation, thesis fact, number, result, interpretation, or limitation. Verify every claim trace and find any scope breach. Explicitly test residual-object wording, exact-point implications, negotiation onset, attenuation direction, PRE2, the cash GAP level, pooled cash-versus-stock comparison, novelty, causality, mechanisms, source-silent questions, and unapplied deck-audit findings. Report findings only; do not repair the script.

### Input files

- Upload prompt: `U10_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U10_INPUTS.zip` containing Core source archive, U09 full candidate and trace files, and U03 examiner-attack outputs in one input zip. In minimum-viable mode, omit U03 and derive the reduced attack list directly from audit_findings.md..

### Required return

- Download JSON: `U10_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U10_OUTPUTS.zip`. sentence_evidence_matrix.csv, evidence_findings.json, scope_findings.csv, and u10_audit_summary.md.

### Acceptance check

Reject the audit if any spoken sentence is unclassified, any number is sampled rather than exhaustively checked, findings lack exact script and source locations, or the auditor edits the script it is judging.

**Concurrency:** May run with U11.

**Real dependencies:** U09, U03.

## U11: Run the independent timing, speakability, transition, and surface audit

### Dispatch assignment

Audit the assembled script without changing it. Count spoken words per slide and globally, scan every audience-facing character for em dash and en dash, verify complete sentences, detect dense clauses and duplicate setup, test the last sentence and first sentence at every boundary as a pair, and compare chart pointing beats with pause allowances. Perform a blind one-job test: infer each slide's audience job from the script and compare it with the contract. Report findings only.

### Input files

- Upload prompt: `U11_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U11_INPUTS.zip` containing U09 full candidate, word budget, transition register, chart cue map, U04 drafting contract, SPEAKER_NOTES_BUDGET.md, SPEAKING_RATE_TEST.md, and the locked deck in one input zip.

### Required return

- Download JSON: `U11_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U11_OUTPUTS.zip`. timing_surface_findings.json, word_recount.csv, transition_test.csv, chart_pacing_test.csv, speakability_flags.csv, and u11_audit_summary.md.

### Acceptance check

Reject the audit if it treats 2110 as a target rather than a pre-rehearsal ceiling, counts nonspoken cues as words, omits a character scan, fails to inspect all 12 boundaries, or rewrites the candidate.

**Concurrency:** May run with U10.

**Real dependencies:** U09.

## U12: Apply controlled repairs

### Dispatch assignment

Repair the candidate using U10 and U11 findings. Resolve every critical and major finding and explicitly adjudicate each minor one. Preserve thesis meaning and visible-slide scope. When length is high, remove a complete lowest-priority thought and rebuild the local bridge rather than compressing qualifications into fragments. Re-run the deterministic checks after revision. Produce a sentence-level change log showing the finding, action, trace impact, and word impact.

### Input files

- Upload prompt: `U12_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U12_INPUTS.zip` containing Core source archive, U09 candidate package, U10 audit package, and U11 audit package in one input zip. In minimum-viable mode, U11 may be absent, but the unit must run the basic word, transition, and forbidden-character tests itself..

### Required return

- Download JSON: `U12_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U12_OUTPUTS.zip`. full_notes_repaired.md, full_trace_repaired.csv, word_budget_repaired.csv, transition_register_repaired.csv, chart_cue_map_repaired.csv, audit_resolution.csv, revision_diff.md, and rehearsal_log_template.csv.

### Acceptance check

Reject the unit if any critical or major item remains open, a repair creates an untraced claim, an essential hedge is cut for length, the global count exceeds 2110, a forbidden dash remains, or slides 11 to 13 are weakened to pay for earlier slides.

**Real dependencies:** U10, U11.

## U13: Rehearsal-backed final signoff

### Dispatch assignment

Perform final signoff on the repaired scripts using the completed full-deck rehearsal log. Re-run exhaustive claim, scope, word, character, transition, and chart-cue checks. Compare actual per-slide and total time with the budget, count filler and unscripted additions, and verify that the presenter used the actual projected figures for chart pacing. Return PASS only if every hard gate passes. Otherwise return FAIL with a bounded repair order that can be sent back through U12; do not issue a conditional pass.

### Input files

- Upload prompt: `U13_PROMPT.md` containing this assignment and the shared protocol.
- Upload zip: `U13_INPUTS.zip` containing Core source archive, all U12 repaired outputs, completed rehearsal_log.csv, and any rehearsal transcript or recording packaged inside one input zip.

### Required return

- Download JSON: `U13_RESPONSE.json` with status, inventory, checks, failures, and output manifest.
- Download zip: `U13_OUTPUTS.zip`. final_signoff.json, final_notes_package.zip, final_trace.csv, final_word_and_time_report.csv, final_transition_report.csv, and signoff_failures.md.

### Acceptance check

PASS requires 13 complete scripts; zero untraced numbers or academic claims; zero slide-scope breaches; zero em dash or en dash; global words between 1930 and 2110; actual full-deck elapsed time at or below 18:00; all 12 transition tests passed; chart pauses executed; no unsafe onset, PRE2, GAP, Wald, novelty, causal, or mechanism language; no fabricated answers to source-silent items; and no unresolved critical or major audit finding.

**Real dependencies:** U12.
