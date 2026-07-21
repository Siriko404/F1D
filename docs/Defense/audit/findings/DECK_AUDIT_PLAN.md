# Deck Audit and Speaker-Notes Production Plan

**Request:** thesis-defense-deck-audit-plan-v2

**Boundary:** This document specifies how to audit the production-locked deck and how to produce speaker notes after the audit. It does not perform the audit, verify any deck number, judge any individual slide, draft any speaker note, change the thesis, or propose a new deck architecture.

## Governing rules

- Use only the attached ledger, production PDF, extracted text, audit context, and the operator-held approved-thesis files described in the context.
- Treat the approved thesis as the sole academic authority and the ledger as the process and production authority.
- Audit the exact final PDF and PDF-derived rasters, never HTML alone.
- Do not edit during discovery. Complete the finding record and triage before any reopening decision.
- Keep deck defects, speaker-notes needs, appendix needs, thesis-silent exposures, logistics issues, and stylistic preferences separate.
- Preserve the 13-slide architecture, 18-minute target, 2-minute buffer, descriptive interpretation, mechanism boundary, qualified cash language, and war-chest boundary.

## Required execution outputs

- AUDIT_SOURCE_MANIFEST.json: frozen input and thesis-source identities, hashes, roles, and tool versions.
- DECK_CLAIM_SOURCE_MAP.csv: one row per visible substantive claim with source filename and exact location.
- DECK_NUMERIC_INVENTORY.csv and DECK_CALCULATION_LOG.csv: all quantitative items and reproducible derived calculations.
- DECK_AUDIT_EXECUTION_LOG.json: status and evidence path for every check ID.
- DECK_AUDIT_FINDINGS.json: candidate findings, violated authority, evidence, severity, and disposition.
- DECK_DEFENSE_EXPOSURE_REGISTER.csv: predictable questions routed to deck, notes, appendix, acknowledged gap, or logistics.
- DECK_REOPENING_DECISION.json: application of the two-key reopening rule.
- MAIN_DECK_SPEAKER_NOTES.md, SPEAKER_NOTES_SOURCE_MAP.csv, and REHEARSAL_LOG.csv: created only after the deck audit closes.
- DECK_AUDIT_EVIDENCE.zip: frozen inputs, rasters, reports, logs, and SHA-256 manifest.

## Audit dimensions and executable checks

### D01 - Artifact identity, provenance, and frozen baseline

**Why it matters:** Every later conclusion is invalid if the wrong deck, text extraction, or render is audited.

**Cost of failure at defense:** The operator may approve or repair a file that is not the production-locked deck, making all downstream work non-reproducible.

#### D01-C01

- **Check:** Confirm that the audit target is the exact production PDF recorded in the ledger by filename, byte size, and SHA-256.
- **Evidence:** THESIS_DEFENSE_CONTINUITY_LEDGER_REV21(5).json; thesis_defense_main_deck_slides_01-13_standardized_v2(1).pdf
- **Method:** deterministic. Identity and byte equality are exact facts. Model inspection cannot reliably establish them.
- **Pass:** The computed SHA-256, byte size, and production role all match the ledger record, with duplicate upload suffixes treated only as storage artifacts.
- **Fail:** Any mismatch, missing hash record, or ambiguity about which PDF is authoritative.
- **Default severity:** blocker

#### D01-C02

- **Check:** Freeze an immutable audit snapshot containing the target PDF, extracted text JSON, ledger, context file, and tool-version record.
- **Evidence:** All attached files; locally generated AUDIT_SOURCE_MANIFEST.json
- **Method:** deterministic. A frozen snapshot prevents later edits or tool changes from silently invalidating evidence.
- **Pass:** Each input has a recorded path, size, SHA-256, modification time, and role before any check runs.
- **Fail:** Any input is overwritten, untracked, or used without a recorded hash.
- **Default severity:** blocker

#### D01-C03

- **Check:** Record PDF structure facts required for reproducibility: page count, page boxes, embedded fonts, producer, encryption, and annotations.
- **Evidence:** Production PDF; PyMuPDF or pdf_inspect output stored in the audit evidence folder
- **Method:** deterministic. These properties are machine-readable and must not depend on visual estimation.
- **Pass:** A machine report is saved and all structural facts are internally consistent with the frozen baseline.
- **Fail:** The report is absent, incomplete, or indicates inconsistent page geometry, missing fonts, encryption, or unexpected interactive content.
- **Default severity:** major

#### D01-C04

- **Check:** Separate audit capability from repair capability by recording the canonical renderer state before triage.
- **Evidence:** AUDIT_CONTEXT.md; local WeasyPrint dependency test; production_and_qa_workflow in the ledger
- **Method:** deterministic. Whether the canonical renderer starts successfully is an executable condition, not a matter of opinion.
- **Pass:** The audit record states either RENDERER_READY with a successful smoke render or RENDERER_BLOCKED with the exact dependency error; no edit is attempted while blocked.
- **Fail:** A repair is attempted through a different renderer or without a successful canonical-renderer smoke test.
- **Default severity:** blocker

### D02 - Source authority and claim-to-source traceability

**Why it matters:** The thesis is the sole academic authority, so every substantive slide claim must have a precise source path.

**Cost of failure at defense:** An examiner can expose an unsupported statement even when the deck looks polished and internally coherent.

#### D02-C01

- **Check:** Create a source manifest that records the exact local filename, SHA-256, and authority status of the flattened thesis and every newer build file used for verification.
- **Evidence:** _thesis_FLAT(2).tex; operator-held byte-exact tables, introduction, main-analysis, conclusion, robustness, replication, and appendix files; AUDIT_CONTEXT.md
- **Method:** deterministic. File identity and version relationships must be fixed before claims are checked.
- **Pass:** Every source used later has an exact filename, hash, role, and authority note. Any newer build file is confirmed as part of the approved thesis build before it can supersede a flattened-file passage for verification.
- **Fail:** A check cites an unnamed file, an unverified derivative, or a file whose relationship to the approved thesis is unresolved.
- **Default severity:** blocker

#### D02-C02

- **Check:** Extract and classify every substantive deck statement as bibliographic identity, conceptual claim, research question, sample fact, method, numerical result, interpretation, limitation, contribution, or citation.
- **Evidence:** deck_text_extracted.json; 300-DPI page rasters of the production PDF
- **Method:** hybrid. Text extraction supplies exhaustive wording, while visual inspection is needed to capture meaning encoded by layout, charts, and labels.
- **Pass:** Every substantive visible statement and visual proposition has one claim ID and one classification in DECK_CLAIM_SOURCE_MAP.
- **Fail:** Any substantive statement, chart proposition, or source footer is unmapped or multiply classified without resolution.
- **Default severity:** major

#### D02-C03

- **Check:** Map every claim ID to an exact source filename and line range, table label, equation, or explicitly approved ledger decision.
- **Evidence:** Source manifest from D02-C01; _thesis_FLAT(2).tex; verified approved-build files; ledger approved decisions
- **Method:** hybrid. Exact locations are deterministic once found, but identifying the passage that truly supports a paraphrase requires semantic judgment.
- **Pass:** Each claim has one controlling source citation with exact location and a short support rationale; purely process or design claims point to the ledger rather than the thesis.
- **Fail:** A claim relies on memory, a broad section name without location, an outside source, or a passage that does not support its stated strength.
- **Default severity:** blocker

#### D02-C04

- **Check:** Apply a conflict protocol whenever the flattened thesis, newer build files, ledger summary, and deck wording differ.
- **Evidence:** Ledger authority_and_source_protocol; source manifest; conflicting passages
- **Method:** judgment. The conflict must be interpreted in light of approval status and source provenance, not resolved by string matching alone.
- **Pass:** The conflict is logged, the approved thesis source is identified, and no deck verdict or notes drafting proceeds until the controlling version is explicit.
- **Fail:** The operator silently chooses the most convenient wording or merges incompatible versions.
- **Default severity:** blocker

### D03 - Visible-text, text-layer, and glyph parity

**Why it matters:** The audience sees the rasterized page, while search and automated checks operate on the text layer. Both must represent the same content.

**Cost of failure at defense:** Hidden, duplicated, malformed, or missing text can escape one inspection channel and surface during projection, copying, or accessibility use.

#### D03-C01

- **Check:** Compare each page text layer with the visible 300-DPI raster and account for every difference, allowing only known letter-spacing extraction artifacts.
- **Evidence:** deck_text_extracted.json; exact production PDF rasters at 300 DPI or higher
- **Method:** hybrid. Programmatic diff finds omissions and duplicates, while a human must distinguish true discrepancies from extraction artifacts.
- **Pass:** All visible words, symbols, page numbers, and source lines are represented in the text layer, and every extra text-layer item is visibly present or explicitly explained.
- **Fail:** Visible text is missing, hidden text is present, ordering changes meaning, or an unexplained discrepancy remains.
- **Default severity:** major

#### D03-C02

- **Check:** Search for malformed Unicode, replacement characters, broken ligatures, control characters, and encoding artifacts in extracted text.
- **Evidence:** deck_text_extracted.json; raw PDF character extraction
- **Method:** deterministic. Exhaustive character-set checks are safer and faster than visual memory.
- **Pass:** The character inventory contains only approved punctuation, symbols, and explained extraction artifacts.
- **Fail:** Unexpected control characters, replacement glyphs, private-use characters, or malformed statistical symbols appear.
- **Default severity:** major

#### D03-C03

- **Check:** Detect duplicate, off-page, zero-size, or invisible text objects that could contaminate extraction or copying.
- **Evidence:** Production PDF object and word-coordinate extraction
- **Method:** deterministic. Object coordinates, opacity, and duplication are exact PDF properties.
- **Pass:** No substantive text object is duplicated, outside the page box, effectively invisible, or unrelated to the visible slide.
- **Fail:** Any hidden or duplicate substantive text object is found without an intentional documented reason.
- **Default severity:** major

#### D03-C04

- **Check:** Confirm that source footers and page-number text are extractable and ordered consistently on all applicable pages.
- **Evidence:** Production PDF text coordinates; ledger footer standard
- **Method:** deterministic. Footer presence and page sequence are enumerable facts.
- **Pass:** The title-slide exception is preserved, and every content page contains the expected footer text and sequential page marker in a stable reading order.
- **Fail:** A footer or marker is missing, duplicated, out of sequence, or inserted into the main reading order in a misleading way.
- **Default severity:** major

### D04 - Numerical, statistical, and specification fidelity

**Why it matters:** Load-bearing numbers and econometric descriptors must reproduce the approved thesis exactly and consistently.

**Cost of failure at defense:** A single wrong coefficient, sample, baseline, test, or derived quantity can dominate the defense and undermine trust in the entire analysis.

#### D04-C01

- **Check:** Build an exhaustive inventory of every number, threshold, date range, inequality, sample count, coefficient, uncertainty measure, standard error, p-value, confidence interval, effect-size calculation, and axis label in the deck.
- **Evidence:** deck_text_extracted.json; visible chart labels in 300-DPI rasters
- **Method:** hybrid. Regex can enumerate textual numbers, but chart scales and visual values require image-based confirmation.
- **Pass:** Every visible numerical token and visually encoded quantitative value has a unique audit ID and slide location.
- **Fail:** Any number or quantitative visual is omitted from the inventory.
- **Default severity:** major

#### D04-C02

- **Check:** Verify each non-derived numerical item against a named approved-thesis source file and exact line or table cell.
- **Evidence:** D02 source manifest and claim map; named approved-thesis files and table labels
- **Method:** deterministic. Once the source cell is identified, exact equality and sign/decimal-format checks must not be left to model memory.
- **Pass:** The deck value, sign, unit, rounding, sample definition, and test label match the controlling source.
- **Fail:** Any mismatch, unsupported rounding, transposed value, omitted unit, or wrong source cell is found.
- **Default severity:** blocker

#### D04-C03

- **Check:** Recompute every derived value using a documented formula, full-precision inputs from the thesis, and a fixed rounding rule.
- **Evidence:** D04 inventory; controlling thesis values; local calculation log
- **Method:** deterministic. Arithmetic and rounding are reproducible and are especially unsafe to trust to language-model estimation.
- **Pass:** Every derived interval, difference, ratio, percentage, or effect-size statement reproduces under the recorded formula and rounding rule.
- **Fail:** A derived item cannot be reproduced exactly or depends on rounded display values when full-precision inputs exist.
- **Default severity:** blocker

#### D04-C04

- **Check:** Verify that each chart point, whisker, bracket, label, and axis range is generated from the intended estimate, uncertainty measure, and comparison.
- **Evidence:** Production PDF chart coordinates and labels; D04 calculation log; named thesis table cells
- **Method:** hybrid. Data equality is deterministic, while deciding whether the visual mapping communicates the intended estimand requires judgment.
- **Pass:** Every graphical mark maps to the correct audit ID, and its position, uncertainty interval, and comparison label agree with the source map within the rendering tolerance recorded by the operator.
- **Fail:** A mark uses the wrong value, wrong uncertainty measure, wrong baseline, wrong test, or materially misleading scale.
- **Default severity:** blocker

#### D04-C05

- **Check:** Verify specification descriptors as a complete bundle: outcome, event window, omitted baseline, sample restrictions, controls, fixed effects, clustering, tails, and matched-row status.
- **Evidence:** Deck claim map; main-analysis source files; table notes; thesis methods text
- **Method:** hybrid. Exact descriptors can be compared mechanically, but completeness and equivalence across prose and table notes require interpretation.
- **Pass:** Each empirical display has a source-matched specification record and no descriptor is borrowed from a different model or sample.
- **Fail:** A descriptor is absent where needed, inconsistent across the deck, or attached to the wrong analysis.
- **Default severity:** blocker

### D05 - Claim strength, causal boundaries, and inferential discipline

**Why it matters:** The deck must state exactly what the descriptive evidence supports and no more.

**Cost of failure at defense:** Overstatement gives examiners an immediate route to challenge identification, mechanism, payment-method specificity, or statistical logic.

#### D05-C01

- **Check:** Scan every audience-facing claim for causal verbs, causal nouns, treatment-effect language, or implied identification.
- **Evidence:** Deck claim map; ledger fidelity_protocol; approved thesis interpretation passages
- **Method:** hybrid. Keyword search is exhaustive, but causal implication can arise without an explicit forbidden word.
- **Pass:** Every claim is either plainly descriptive or directly supported by an approved causal design stated in the thesis; no implied causality remains.
- **Fail:** Any wording converts a within-firm association into cause, impact, effect, consequence, or identified response beyond the thesis.
- **Default severity:** blocker

#### D05-C02

- **Check:** Test all mechanism language against the thesis boundary that the reason for the language pattern is not identified.
- **Evidence:** Deck claim map; ledger mechanism and cash_mechanism rules; thesis conceptual and limitation passages
- **Method:** judgment. Mechanism overstatement is semantic and can be conveyed through framing, sequence, or implication rather than a single phrase.
- **Pass:** Mechanisms are presented only as motivation, observationally equivalent possibilities, or open questions, with no established intent or channel.
- **Fail:** The deck states or implies that legal constraint, strategic silence, cash accumulation, war-chest behavior, or another channel is established.
- **Default severity:** blocker

#### D05-C03

- **Check:** Test payment-method language for the approved qualification: stronger for or concentrated in cash, not strictly cash-only.
- **Evidence:** Deck claim map; ledger cash_language rule; controlling thesis conclusion and payment-method analysis
- **Method:** hybrid. Exact prohibited phrases can be found programmatically, but equivalent overstatement requires semantic review.
- **Pass:** Every payment-method conclusion preserves the thesis qualification and does not infer absence of an effect from imprecision.
- **Fail:** Any claim says cash-specific, cash-only, unique to cash, or treats an imprecise comparison estimate as proof of no pattern.
- **Default severity:** blocker

#### D05-C04

- **Check:** Check that statistical conclusions rely on the correct formal contrast rather than comparing separate significance labels.
- **Evidence:** Deck claim map; named thesis tests; ledger do_not_repeat_lessons
- **Method:** hybrid. Test labels and values are exact, but whether prose commits the difference-in-significance fallacy requires judgment.
- **Pass:** Every between-stage or between-payment claim is tied to the direct thesis contrast intended to test it.
- **Fail:** A conclusion is based only on one estimate being significant and another not significant, or on visual separation without a formal test.
- **Default severity:** blocker

#### D05-C05

- **Check:** Check that uncertainty, fragility, limitations, and non-significant or marginal evidence are neither hidden nor overemphasized.
- **Evidence:** Deck claim map; thesis result and limitation passages; ledger approved slide boundaries
- **Method:** judgment. Balanced evidentiary strength depends on context, hierarchy, and wording rather than token equality.
- **Pass:** Qualifications appear where needed to prevent a reasonable audience from drawing a stronger conclusion than the thesis supports, without burying the main finding.
- **Fail:** A load-bearing qualification is absent, visually inaccessible, contradicted, or repeated so heavily that it distorts the approved narrative.
- **Default severity:** major

### D06 - Definitions, terminology, and cross-slide semantic consistency

**Why it matters:** A defense deck is one argument. Terms, stages, samples, and baselines must retain the same meaning across all pages.

**Cost of failure at defense:** Inconsistent labels force the presenter to repair definitions live and can make correct analyses appear contradictory.

#### D06-C01

- **Check:** Create a controlled vocabulary for constructs, datasets, units, event stages, payment categories, and abbreviations.
- **Evidence:** Deck claim map; thesis variable definitions; ledger thesis_digest and approved decisions
- **Method:** hybrid. Term extraction can be automated, but deciding which variants are legitimate simplifications requires semantic comparison.
- **Pass:** Every recurring concept has one preferred audience label, an exact thesis term, and an approved-shortening rule.
- **Fail:** Two labels imply different constructs, an abbreviation is undefined, or a simplification changes the estimand.
- **Default severity:** major

#### D06-C02

- **Check:** Compare event-stage names, temporal boundaries, omitted baselines, and pooled-period definitions wherever they recur.
- **Evidence:** Deck text and visuals; named thesis event-study definitions; ledger timing lessons
- **Method:** hybrid. Repeated strings can be compared mechanically, while equivalence of temporal definitions requires interpretation.
- **Pass:** Each recurring stage and baseline has the same definition, or any analysis-specific difference is explicit at the point of use.
- **Fail:** The same label refers to different periods, a different label refers to the same period without explanation, or a pooled stage is visually presented as a single equal-duration quarter.
- **Default severity:** blocker

#### D06-C03

- **Check:** Compare sample, unit-of-observation, and restriction wording across data, measurement, and finding sections.
- **Evidence:** Deck claim map; source-matched specification records from D04-C05
- **Method:** deterministic. Once sample descriptors are normalized, cross-slide mismatches can be exhaustively compared.
- **Pass:** Every sample statement matches its analysis and changes in observations or firms are explained by explicit filters rather than implied continuity.
- **Fail:** A sample count or definition is carried across analyses without the correct restriction, or two panels appear directly comparable when they are not.
- **Default severity:** major

#### D06-C04

- **Check:** Trace each approved research question through its roadmap, empirical design, finding, contribution, boundary, and conclusion.
- **Evidence:** Presentation architecture; deck claim map; thesis_digest research questions and main findings
- **Method:** judgment. The mapping is conceptual and depends on whether the audience can follow the argument, not only on label recurrence.
- **Pass:** Each research question has one identifiable evidence path and no finding is orphaned, duplicated, or assigned to the wrong question.
- **Fail:** A question lacks a result, a result answers a different question, or the conclusion introduces a claim not established earlier.
- **Default severity:** major

#### D06-C05

- **Check:** Run a contradiction matrix across all slide claims and approved ledger boundaries.
- **Evidence:** DECK_CLAIM_SOURCE_MAP; ledger fidelity protocol and approved decisions
- **Method:** hybrid. Exact oppositions can be flagged by rules, but subtle contradiction and scope drift need judgment.
- **Pass:** No pair of claims differs in direction, scope, sample, timing, or evidentiary strength without an explicit analysis-specific reason.
- **Fail:** Any unresolved contradiction, silent scope change, or stronger restatement appears.
- **Default severity:** blocker

### D07 - Citation, legal-authority, and source-footer hygiene

**Why it matters:** Citations must establish provenance without confusing legal authority, academic evidence, and thesis sourcing.

**Cost of failure at defense:** A citation-category error or unsupported positioning claim can distract the committee from the thesis and invite avoidable credibility questions.

#### D07-C01

- **Check:** Inventory every author-year reference, legal authority, rule, dataset attribution, and thesis-source footer.
- **Evidence:** deck_text_extracted.json; visible 300-DPI rasters; thesis reference list
- **Method:** deterministic. Citation tokens are enumerable and should not depend on visual memory.
- **Pass:** Every citation-like item has a type, full source identity, deck location, and thesis/reference-list status.
- **Fail:** A citation-like item is omitted, malformed, or has no identified authority type.
- **Default severity:** major

#### D07-C02

- **Check:** Check that legal authorities and academic papers are visually and verbally distinguished where their roles differ.
- **Evidence:** Citation inventory; relevant deck raster; thesis conceptual framework and reference list
- **Method:** judgment. The problem is categorical interpretation and audience expectation, not only punctuation.
- **Pass:** A reasonable reader can tell whether each item is legal authority, theoretical literature, empirical literature, data source, or thesis section.
- **Fail:** Different authority types are presented as an undifferentiated scholarly list or their evidentiary roles are ambiguous.
- **Default severity:** major

#### D07-C03

- **Check:** Verify that every cited work or authority appears in the approved thesis and is used for the same proposition.
- **Evidence:** Citation inventory; _thesis_FLAT(2).tex reference list and cited passages
- **Method:** hybrid. Presence is deterministic, but proposition-level support needs semantic judgment.
- **Pass:** Each citation is present in the thesis and supports the local claim at the strength shown.
- **Fail:** A source is outside the thesis, absent from the reference list where applicable, or attached to a claim it does not support.
- **Default severity:** blocker

#### D07-C04

- **Check:** Check footer style, density, legibility, and consistency against the locked visual system.
- **Evidence:** 300-DPI production PDF rasters; ledger visual_system.footer and typography rules
- **Method:** hybrid. Presence and size can be measured, while readability and excessive density require projection-oriented judgment.
- **Pass:** Applicable pages use the approved footer convention, remain legible, and do not compete with the slide message.
- **Fail:** A footer is missing, inconsistent, unreadable, clipped, or visually dominant.
- **Default severity:** major

#### D07-C05

- **Check:** Test novelty and positioning statements against the exact literature scope claimed in the thesis.
- **Evidence:** Deck claim map; thesis introduction and literature review; cited nearest-work passages
- **Method:** judgment. Novelty claims are scope-sensitive and cannot be validated through citation presence alone.
- **Pass:** The statement matches the thesis qualification and defines the comparison cell precisely enough to avoid a universal priority claim.
- **Fail:** The deck broadens the thesis positioning claim, treats an incomplete search as proof, or omits the dimensions that make the claim defensible.
- **Default severity:** major

### D08 - Narrative architecture, reading order, and cognitive economy

**Why it matters:** The approved 13-slide structure must produce one coherent, findings-forward argument within the time limit.

**Cost of failure at defense:** A correct deck can still fail if the audience cannot see why each slide exists or how the evidence answers the questions.

#### D08-C01

- **Check:** Confirm that the approved Intro, Message, and Outro architecture, slide count, sequence, and section boundaries remain unchanged.
- **Evidence:** Ledger presentation_architecture and approved decisions; production PDF page order
- **Method:** deterministic. The approved map and page order are exact and should be compared mechanically.
- **Pass:** All 13 pages appear once, in approved order, with no new or missing architecture element.
- **Fail:** A page is missing, duplicated, reordered, substituted, or functions as an unapproved new slide category.
- **Default severity:** blocker

#### D08-C02

- **Check:** State the single communication job of each slide and test every visible element against that job.
- **Evidence:** Ledger per-slide communication goals; production PDF rasters; deck claim map
- **Method:** judgment. Relevance and cognitive load are functions of meaning, hierarchy, and audience attention.
- **Pass:** Each element either advances the slide job, supplies necessary evidence, or provides an essential boundary/source.
- **Fail:** An element is decorative, redundant, premature, or competes with the slide job.
- **Default severity:** minor

#### D08-C03

- **Check:** Audit prerequisite order: every term, design choice, and inference must be introduced before it is required.
- **Evidence:** Production PDF sequence; controlled vocabulary; claim map
- **Method:** judgment. Audience presupposition is semantic and sequence-dependent.
- **Pass:** A first-time viewer can understand each slide without knowledge introduced only later.
- **Fail:** A slide relies on an undefined construct, baseline, event stage, or comparison that appears later.
- **Default severity:** major

#### D08-C04

- **Check:** Audit cross-slide redundancy and deliberate reinforcement.
- **Evidence:** Claim matrix grouped by proposition; production PDF sequence
- **Method:** hybrid. Duplicate propositions can be detected programmatically, but useful reinforcement must be distinguished from repetition.
- **Pass:** Repeated claims serve a different narrative function or are shortened appropriately; no slide re-teaches completed material.
- **Fail:** Substantial wording, evidence, or qualification repeats without advancing the argument, or a key claim appears only once with no closure.
- **Default severity:** minor

#### D08-C05

- **Check:** Assess whether the deck remains findings-forward for the known committee while preserving methods needed to defend the evidence.
- **Evidence:** AUDIT_CONTEXT.md committee intelligence; presentation architecture; production PDF
- **Method:** judgment. The balance between speed, technical defensibility, and narrative emphasis is audience-specific.
- **Pass:** The main results receive the greatest explanatory time and visual emphasis, while method detail is sufficient to support rather than delay them.
- **Fail:** Background crowds out findings, or findings are presented without enough design context to withstand immediate questioning.
- **Default severity:** major

### D09 - Quantitative visual encoding and statistical readability

**Why it matters:** Charts and diagrams must encode the intended estimands without creating false comparisons or temporal implications.

**Cost of failure at defense:** Misleading geometry can cause the committee to infer a result the regression does not establish, even if every printed number is correct.

#### D09-C01

- **Check:** Extract or reconstruct the coordinate map for every quantitative mark and compare it with the source-matched values.
- **Evidence:** Production PDF vector/object coordinates or high-resolution raster measurements; D04 calculation log
- **Method:** deterministic. Point and interval positions are measurable and should be checked independently of visual impression.
- **Pass:** Coordinates reproduce the intended values under the documented scale within a predeclared rendering tolerance.
- **Fail:** A point, interval, endpoint, or bracket is positioned inconsistently with the documented scale.
- **Default severity:** blocker

#### D09-C02

- **Check:** Check axes, zero lines, units, scale ranges, direction, and separate-scale treatment for every quantitative visual.
- **Evidence:** Production PDF rasters; D04 specification records; ledger chart-treatment rules
- **Method:** hybrid. Labels and ranges are exact, while whether scale choices invite a false magnitude comparison requires judgment.
- **Pass:** Every scale is explicit enough for the intended comparison, and different units are visibly separated rather than compared by height.
- **Fail:** A unit, baseline, or scale is ambiguous, truncated without explanation, reversed, or visually invites an invalid magnitude comparison.
- **Default severity:** blocker

#### D09-C03

- **Check:** Check temporal diagrams and event studies for accurate stage boundaries and pooled-duration communication.
- **Evidence:** Production PDF rasters; thesis event definitions; ledger do_not_repeat_lessons
- **Method:** hybrid. Boundary locations can be measured, but implied continuity and equal duration are perception questions.
- **Pass:** Announcement and completion are explicit, categorical stages are labeled, and pooled stages are not silently depicted as equal-duration continuous time.
- **Fail:** The visual implies a continuous time series, equal interval lengths, or an event order inconsistent with the design.
- **Default severity:** major

#### D09-C04

- **Check:** Check direct-test annotations, uncertainty intervals, significance labels, and nearby interpretation for one-to-one correspondence.
- **Evidence:** Production PDF rasters; D04 inventory; thesis test records
- **Method:** hybrid. Annotation identity can be matched mechanically, while proximity and reading order require visual judgment.
- **Pass:** Each annotation is visually attached to the correct mark or contrast, with no plausible alternative reading.
- **Fail:** An annotation can be read as applying to the wrong series, stage, estimate, or test.
- **Default severity:** blocker

#### D09-C05

- **Check:** Check that visual hierarchy reflects evidentiary importance rather than statistical drama.
- **Evidence:** Production PDF rasters; ledger visual hierarchy rules; thesis interpretation strength
- **Method:** judgment. Emphasis is a perceptual design property and cannot be reduced to exact text matching.
- **Pass:** The formal estimand and its uncertainty are prominent together; non-significant or fragile elements are not visually sensationalized.
- **Fail:** Color, size, position, or annotation overstates a coefficient, hides uncertainty, or makes a descriptive comparison look definitive.
- **Default severity:** major

### D10 - Final-PDF rendering, geometry, typography, and projection robustness

**Why it matters:** The exact PDF used at the defense must remain clean and readable after real rendering, not merely in source code.

**Cost of failure at defense:** Clipping, overlap, poor contrast, or small labels can make correct content unusable in the room.

#### D10-C01

- **Check:** Rasterize the exact frozen PDF at 300 DPI or higher and record the command, engine, page images, and dimensions.
- **Evidence:** Production PDF; ledger production_and_qa_workflow
- **Method:** deterministic. Render provenance and pixel dimensions are exact and required by the locked workflow.
- **Pass:** All pages are rasterized from the exact frozen PDF at the required resolution, with hashes recorded for the page images.
- **Fail:** Images come from HTML, a different PDF, an unknown engine, a lower resolution, or an unrecorded command.
- **Default severity:** blocker

#### D10-C02

- **Check:** Inspect every page for clipping, overflow, overlap, missing glyphs, malformed lines, broken symbols, and object collisions.
- **Evidence:** Exact 300-DPI or higher PDF-derived page rasters
- **Method:** judgment. These defects can be subtle and contextual; visual inspection is the authority.
- **Pass:** No text or graphical object is clipped, overlapped, malformed, or lost at full-page and zoomed inspection.
- **Fail:** Any substantive content is obscured, malformed, or outside its intended bounds.
- **Default severity:** blocker

#### D10-C03

- **Check:** Measure alignment of correspondence-encoding objects: dots, lines, cells, axes, connectors, labels, rules, and repeated margins.
- **Evidence:** PDF object coordinates where available; high-resolution rasters; ledger visual system
- **Method:** hybrid. Coordinates reveal exact deviations, while perceptual alignment determines whether the deviation is visible and meaningful.
- **Pass:** Objects intended to correspond share the same documented centerline or baseline within tolerance, and repeated margins remain consistent.
- **Fail:** A visible misalignment weakens correspondence, reading order, or polish.
- **Default severity:** major

#### D10-C04

- **Check:** Inspect hierarchy, white-space balance, grouping, line wrapping, orphaned words, and title/body/footnote separation.
- **Evidence:** Exact PDF rasters; ledger hierarchy_and_spacing and typography ranges
- **Method:** judgment. These are perceptual layout properties that require page-level and deck-level viewing.
- **Pass:** Each page has a clear first, second, and supporting reading level; line breaks appear intentional; whitespace supports grouping.
- **Fail:** The eye is pulled to the wrong element, groups are ambiguous, or wrapping and whitespace look accidental.
- **Default severity:** major

#### D10-C05

- **Check:** Run a projection-simulation review at full-screen fit, reduced contrast, and typical back-of-room thumbnail scale without altering the source file.
- **Evidence:** PDF-derived rasters and a documented display simulation
- **Method:** judgment. Legibility depends on perceptual conditions not captured by source font sizes alone.
- **Pass:** All load-bearing text, labels, series distinctions, and boundaries remain readable and distinguishable in the simulation.
- **Fail:** A load-bearing item disappears, merges, or requires close zoom to interpret.
- **Default severity:** major

#### D10-C06

- **Check:** Confirm deck-wide visual-system invariants: page size, font family, palette roles, footer convention, page sequence, and logo placement.
- **Evidence:** Production PDF metadata and rasters; ledger visual_system
- **Method:** hybrid. Metadata can test dimensions and fonts, while palette roles and visual exceptions require judgment.
- **Pass:** All pages comply with the locked system and only documented exceptions occur.
- **Fail:** An undocumented font, page box, logo, footer, palette role, or numbering exception appears.
- **Default severity:** major

### D11 - Language, punctuation, and audience-facing wording compliance

**Why it matters:** The deck has explicit wording constraints and must remain simple enough to speak naturally.

**Cost of failure at defense:** A small wording violation can trigger needless reopening, while dense or ambiguous prose can cause live delivery errors.

#### D11-C01

- **Check:** Run an exact search for em dashes and dash-based sentence constructions prohibited by the ledger, then review all hyphens in context.
- **Evidence:** deck_text_extracted.json; raw PDF character inventory; ledger collaboration_protocol.language_preference
- **Method:** hybrid. Character detection is deterministic, but distinguishing compound-word hyphens from sentence constructions requires context.
- **Pass:** No prohibited dash character or sentence construction remains; legitimate compound terms are documented as allowed.
- **Fail:** Any prohibited construction appears in audience-facing wording.
- **Default severity:** major

#### D11-C02

- **Check:** Run spelling, grammar, punctuation, capitalization, spacing, and duplicate-word checks with a project-specific dictionary.
- **Evidence:** deck_text_extracted.json; controlled vocabulary from D06; visible rasters
- **Method:** hybrid. Automated checking finds candidates, while finance terms, names, and deliberate labels require human adjudication.
- **Pass:** All flagged items are corrected or explicitly accepted as proper names, notation, or intentional style.
- **Fail:** An unexplained typo, punctuation error, doubled word, spacing defect, or inconsistent capitalization remains.
- **Default severity:** minor

#### D11-C03

- **Check:** Check acronym introduction, symbol pronunciation, and audience-friendly expansion of technical shorthand.
- **Evidence:** Deck sequence; controlled vocabulary; speaker-notes production rules
- **Method:** judgment. Whether a first-time listener can decode shorthand is an audience comprehension question.
- **Pass:** Every acronym or symbol is expanded before first use or is universally clear within the deck itself, and later short forms remain consistent.
- **Fail:** The presenter must improvise an expansion or a symbol can be pronounced or interpreted in multiple ways.
- **Default severity:** major

#### D11-C04

- **Check:** Check that simplifications preserve thesis meaning and that sentences are speakable without silently repairing them.
- **Evidence:** Deck claim map; source passages; oral read-through recording
- **Method:** judgment. Speakability and faithful paraphrase are semantic and performance properties.
- **Pass:** Each sentence can be read aloud once, in its written order, without adding qualifiers or changing the claim.
- **Fail:** The presenter must insert missing logic, reverse clauses, or add a qualification not shown on the slide.
- **Default severity:** major

#### D11-C05

- **Check:** Check source and limitation text for minimum necessary density rather than deletion or overloading.
- **Evidence:** PDF rasters; claim map; ledger approved boundaries
- **Method:** judgment. The correct density balances provenance, evidence boundaries, and projection readability.
- **Pass:** The main message remains dominant while necessary source and boundary language is accessible.
- **Fail:** Essential provenance or qualification is omitted, or supporting text becomes unreadable and performatively useless.
- **Default severity:** major

### D12 - Timing, density, and spoken-slide interface

**Why it matters:** The deck is approved for an 18-minute talk with a 2-minute buffer, so visual density and speech must be tested as one system.

**Cost of failure at defense:** A deck that requires more than 18 minutes forces rushed findings, skipped limitations, or a breach of the hard limit.

#### D12-C01

- **Check:** Time a slide-only walkthrough that explains each visible element without drafted notes and records section and total duration.
- **Evidence:** Production PDF; approved section budgets of 5, 10, and 3 minutes; rehearsal log
- **Method:** judgment. The walkthrough tests the natural explanatory burden of the artifact before script optimization.
- **Pass:** The operator can explain the deck coherently within the approved section structure and identify no slide that requires reading all text verbatim.
- **Fail:** A slide cannot be explained without skipping load-bearing content or exceeding its section budget.
- **Default severity:** major

#### D12-C02

- **Check:** After notes exist, run at least three complete timed rehearsals and record total, section, slide, interruption, and recovery times.
- **Evidence:** Approved speaker-notes draft; production PDF; REHEARSAL_LOG.csv
- **Method:** deterministic. Elapsed time is objective and must be measured, not estimated from word count alone.
- **Pass:** All three clean runs finish at or below 18:00, no run approaches the hard 20:00 limit, and section overruns are corrected rather than offset by rushing later sections.
- **Fail:** Any clean run exceeds 18:00, timing varies enough to threaten 20:00, or the presenter relies on rushing to recover.
- **Default severity:** major

#### D12-C03

- **Check:** Measure the ratio of visible text to spoken content and identify any page that tempts verbatim reading or leaves unexplained visual evidence.
- **Evidence:** Deck text inventory; speaker-notes beat map; rehearsal recordings
- **Method:** hybrid. Text counts are exact, while whether the slide and speech complement each other requires judgment.
- **Pass:** Notes guide attention to the key visual evidence and do not duplicate all visible wording; every load-bearing visual receives spoken interpretation.
- **Fail:** The presenter reads paragraphs, ignores a central chart, or speaks claims not anchored to the visible page.
- **Default severity:** major

#### D12-C04

- **Check:** Count transitions, pauses, chart-orientation time, and likely examiner interruptions inside the timing model.
- **Evidence:** Rehearsal log; slide transition plan; AUDIT_CONTEXT.md
- **Method:** deterministic. These durations can be timed and otherwise tend to be omitted from word-based estimates.
- **Pass:** The timing record includes non-script time and still preserves the approved buffer.
- **Fail:** Timing is calculated from spoken words only or excludes navigation and orientation time.
- **Default severity:** major

#### D12-C05

- **Check:** Define a safe cut hierarchy that removes optional explanation without deleting a research question, main finding, or required boundary.
- **Evidence:** Claim map; presentation architecture; speaker-notes beat map
- **Method:** judgment. Safe cuts depend on narrative function and evidentiary priority.
- **Pass:** Each slide has a marked core beat and optional elaboration; the total emergency cut recovers time without changing claims.
- **Fail:** The only available cuts remove a main finding, qualification, or transition needed for comprehension.
- **Default severity:** major

### D13 - Examiner attack surface and defense-exposure register

**Why it matters:** Some high-risk questions are not deck defects. They must be identified, sourced, and routed to notes or the appendix without inventing answers.

**Cost of failure at defense:** The presenter may be surprised by predictable questions even when the deck is fully correct.

#### D13-C01

- **Check:** Build an examiner-question inventory from the ledger risk register, committee intelligence, each slide claim, each method choice, and every stated limitation.
- **Evidence:** qa_risk_register in the ledger; AUDIT_CONTEXT.md; deck claim map; thesis limitations and methods
- **Method:** hybrid. Existing risks can be imported deterministically, while claim-specific follow-ups require expert judgment.
- **Pass:** Every load-bearing claim and design choice has at least one plausible challenge, and duplicate questions are consolidated without losing scope.
- **Fail:** A central construct, sample choice, identification boundary, data pipeline step, or result has no challenge entry.
- **Default severity:** major

#### D13-C02

- **Check:** Classify each exposure as deck defect, speaker-notes need, appendix need, acknowledged thesis gap, logistics question, or stylistic preference.
- **Evidence:** Examiner-question inventory; thesis source map; ledger scope boundaries
- **Method:** judgment. The disposition depends on whether the deck violates an authority or merely cannot answer a broader question.
- **Pass:** Every exposure has exactly one primary class, a rationale, an owner, and a next action.
- **Fail:** An exposure is mislabeled as a deck defect merely because it is uncomfortable, or a true deck error is deferred to Q&A.
- **Default severity:** major

#### D13-C03

- **Check:** For known thesis-silent issues, record the absence explicitly and prepare a bounded response strategy that does not invent a rationale or procedure.
- **Evidence:** AUDIT_CONTEXT.md known unresolved gaps; exhaustive search log across approved thesis files
- **Method:** hybrid. The absence can be established by search, while the safest response strategy requires judgment.
- **Pass:** The search scope and negative result are recorded; the planned response distinguishes what the thesis states, what the presenter knows from verified project records, and what remains unknown.
- **Fail:** The plan fills the gap with speculation, outside assumptions, or an unverified recollection.
- **Default severity:** blocker

#### D13-C04

- **Check:** Prioritize exposures by probability, consequence, thesis answerability, and committee relevance without changing the deck solely to pre-answer every question.
- **Evidence:** AUDIT_CONTEXT.md; risk register; completed finding log
- **Method:** judgment. Priority is context-sensitive and must balance preparedness against slide overload.
- **Pass:** High-priority answerable exposures receive notes or appendix coverage; unresolved gaps receive explicit acknowledgment; low-priority items do not bloat the main deck.
- **Fail:** The main deck becomes a defensive appendix, or high-consequence predictable questions remain unprepared.
- **Default severity:** major

#### D13-C05

- **Check:** Check that every exposure disposition is compatible with the locked appendix architecture and main-deck scope.
- **Evidence:** Ledger appendix_architecture; presentation_vs_appendix rule; exposure register
- **Method:** deterministic. Once categories are defined, routing can be checked systematically.
- **Pass:** Each appendix-routed issue maps to an approved appendix category, and no appendix-only analysis is moved into the main talk without authorization.
- **Fail:** An exposure has no destination, creates a new architecture, or causes scope leakage into the main deck.
- **Default severity:** major

### D14 - Locked-deck triage, remediation safety, and re-lock governance

**Why it matters:** The cost of any fix includes a full render, raster, audit, hash, and ledger cascade.

**Cost of failure at defense:** Unnecessary reopening can create more defects than it removes and can destroy the value of the production lock.

#### D14-C01

- **Check:** Record every candidate finding in a structured log with violated authority, evidence, defense consequence, scope, reproducibility, and proposed disposition.
- **Evidence:** All completed audit evidence; DECK_AUDIT_FINDINGS.json schema defined in this plan
- **Method:** hybrid. Evidence fields are objective, while consequence and scope require reasoned classification.
- **Pass:** No finding enters triage without a reproducible evidence packet and an identified thesis, ledger, or functional-render requirement.
- **Fail:** A preference, hunch, or unsupported concern is treated as a defect.
- **Default severity:** major

#### D14-C02

- **Check:** Apply the severity rubric and must-fix threshold consistently, with a second reviewer blind to the proposed fix.
- **Evidence:** Finding log; severity rubric in this plan; independent reviewer record
- **Method:** judgment. Severity depends on defense consequence, but blind review limits builder bias and solution anchoring.
- **Pass:** Two reviewers agree on severity or record a resolved disagreement using the rubric definitions.
- **Fail:** Severity is chosen to justify a desired edit, or disagreement remains undocumented.
- **Default severity:** major

#### D14-C03

- **Check:** Apply the fix-versus-record gate before reopening the deck.
- **Evidence:** Finding log; fix_versus_record_rule in the response JSON; renderer readiness record
- **Method:** deterministic. The gate is a fixed decision rule designed to prevent ad hoc editing.
- **Pass:** Only blocker or major defects that satisfy all reopening conditions are authorized for repair; all other items are recorded and left alone.
- **Fail:** A minor, note, or stylistic preference triggers reopening, or a must-fix defect is ignored without explicit risk acceptance.
- **Default severity:** blocker

#### D14-C04

- **Check:** Require a bounded patch specification before editing: exact object or wording, authoritative replacement, affected files, reflow risk, and rollback path.
- **Evidence:** Authorized finding; source map; merged standardized-v2 HTML; ledger D037 precedent
- **Method:** hybrid. The patch can be precisely specified, but its likely cascade and semantic equivalence need review.
- **Pass:** The patch changes only the proven defect, preserves architecture and thesis meaning, and has a tested rollback.
- **Fail:** The patch broadens scope, redesigns a slide, changes an unconnected claim, or lacks a rollback.
- **Default severity:** blocker

#### D14-C05

- **Check:** Do not apply any patch until the canonical WeasyPrint environment is restored and a parity smoke test succeeds.
- **Evidence:** Renderer readiness record; merged standardized-v2 HTML; a one-page smoke test and representative full-deck test
- **Method:** deterministic. Renderer availability and output parity are executable facts.
- **Pass:** WeasyPrint runs successfully and representative page geometry/font output matches the production pipeline before the real patch.
- **Fail:** Chrome or another layout engine is substituted, or the canonical renderer remains broken.
- **Default severity:** blocker

#### D14-C06

- **Check:** After any authorized fix, rebuild every dependent artifact and repeat the full audit delta: merged HTML, PDF, 300-DPI rasters, filmstrip, applied-audit record, hashes, and programmatic ledger update.
- **Evidence:** Ledger production workflow and update protocol; patched source; pre-fix evidence package
- **Method:** deterministic. Artifact regeneration, hashing, page comparison, and ledger assertions are reproducible steps.
- **Pass:** All dependencies are rebuilt from the patched source, exact final rasters are inspected, unintended pixel/text changes are absent, hashes are recorded, and user approval precedes re-lock.
- **Fail:** A later file is delivered than the one inspected, a dependent artifact remains stale, or the ledger is rewritten manually without assertions.
- **Default severity:** blocker

### D15 - Audit-process completeness, bias control, and evidence retention

**Why it matters:** The audit itself must be auditable and resistant to missed checks, candidate-finding anchoring, and inconsistent judgment.

**Cost of failure at defense:** An incomplete or biased audit can falsely certify the deck and make later review impossible to reproduce.

#### D15-C01

- **Check:** Use one execution register containing every check ID, operator, timestamp, evidence path, result, finding IDs, and completion state.
- **Evidence:** This plan; locally generated DECK_AUDIT_EXECUTION_LOG.json
- **Method:** deterministic. Coverage is a checklist property and should be machine-verifiable.
- **Pass:** Every check is marked PASS, FAIL, NOT_APPLICABLE with rationale, or BLOCKED with exact missing condition; no blank status remains.
- **Fail:** A check is skipped, merged with another without trace, or closed without evidence.
- **Default severity:** blocker

#### D15-C02

- **Check:** Run one blind second pass that receives the frozen inputs and plan but not the operator candidate-finding list.
- **Evidence:** Frozen audit snapshot; second-pass report
- **Method:** judgment. Blind review reduces anchoring on already noticed issues and builder familiarity.
- **Pass:** The second pass independently records possible blocker and major issues, including an explicit NONE result if none are found.
- **Fail:** The reviewer is primed with existing findings or asked for general aesthetic suggestions.
- **Default severity:** major

#### D15-C03

- **Check:** Audit the audit for false positives, especially typography preferences, harmless extraction artifacts, and thesis-silent exposures.
- **Evidence:** Finding log; raw evidence; triage classifications
- **Method:** judgment. The plan must distinguish an actual violation from taste or broader defense preparation.
- **Pass:** Every retained defect cites a violated authority and measurable defense consequence; preferences and exposures are routed separately.
- **Fail:** A finding survives only because multiple reviewers dislike it or because it may attract a question.
- **Default severity:** major

#### D15-C04

- **Check:** Declare completion only when all checks close and no unresolved blocker or must-fix major remains.
- **Evidence:** Execution log; finding log; remediation record
- **Method:** deterministic. Completion criteria are binary and must not be softened near a deadline.
- **Pass:** All checks are closed, blocker count is zero, must-fix major count is zero, and recorded-only items have explicit owners.
- **Fail:** The audit is called complete with open checks, unresolved must-fix items, or missing evidence.
- **Default severity:** blocker

#### D15-C05

- **Check:** Archive the complete evidence package and produce a machine-readable summary for later independent review.
- **Evidence:** All audit outputs; frozen input manifest; final hashes
- **Method:** deterministic. Retention and manifest integrity are exact package properties.
- **Pass:** The archive contains inputs, tool records, source map, calculation log, rasters, execution log, findings, dispositions, rehearsal logs when available, and SHA-256 for every member.
- **Fail:** Evidence cannot be traced to a frozen input or a package member is missing or unhashed.
- **Default severity:** major

## Dependency-ordered execution sequence

1. **D01**. Depends on: none. Freeze the exact production artifact and determine whether audit and repair capabilities are separately available.
2. **D02**. Depends on: 1. No substantive check can run until the authority, source versions, and claim map are explicit.
3. **D03, D11**. Depends on: 1, 2. Establish a trustworthy wording layer and run exhaustive language checks before interpreting claims.
4. **D04**. Depends on: 2, 3. Verify the complete numerical and specification inventory only after every visible item is mapped and sourced.
5. **D05, D06, D07**. Depends on: 2, 3, 4. Interpretive strength, terminology, contradictions, and citation roles depend on settled source and numeric records.
6. **D09**. Depends on: 4, 5. Quantitative geometry can be judged only after the intended values, estimands, and inferential boundaries are known.
7. **D10**. Depends on: 1, 3, 6. Inspect the exact final-PDF render after the content and visual mappings to avoid treating a rendering symptom as a content issue.
8. **D08**. Depends on: 5, 7. Narrative and cognitive review should use a content-correct, visually understood deck.
9. **D12**. Depends on: 8. Timing must be tested against the settled narrative and actual slide burden.
10. **D13**. Depends on: 2, 5, 8. Defense exposures can now be separated cleanly from deck defects and routed to notes or the appendix.
11. **D14**. Depends on: 3, 4, 5, 6, 7, 8, 9, 10. Triage only after the complete defect and exposure record exists; do not edit during discovery.
12. **D15**. Depends on: 11. Close coverage, blind review, and evidence packaging after dispositions are fixed. Speaker-note production begins only after this deck freeze.

## Severity rubric

### BLOCKER

**Definition:** A reproducible defect that makes the artifact non-authoritative, academically false or unsupported, materially misleading, unusable, or impossible to re-lock safely. Examples include wrong source artifact, wrong number or specification, causal or mechanism overclaim, materially incorrect quantitative encoding, clipped load-bearing content, or an attempted fix through a noncanonical renderer.

**Action:** Must not be accepted for defense use. Authorize a bounded fix only after the reopening gate passes. If safe repair is blocked, record BLOCKED, preserve the locked original, and escalate to the user with the exact risk.

### MAJOR

**Definition:** A reproducible defect likely to confuse an examiner, weaken a load-bearing claim, threaten the 18-minute delivery, or materially reduce readability or cross-slide coherence, but without making the entire artifact non-authoritative.

**Action:** Must be fixed before the final defense package when the reopening gate passes. If repair is technically blocked, record it as an unresolved major and do not relabel it minor.

### MINOR

**Definition:** A real but low-consequence defect that does not change academic meaning, statistical interpretation, navigation, projection readability, or timing. It is more than taste, but the defense would remain credible if left unchanged.

**Action:** Do not reopen the locked deck for this item alone. Fix only inside an already authorized blocker/major batch when the patch is isolated, renderer-safe, and creates no reflow risk; otherwise record and leave unchanged.

### NOTE

**Definition:** A stylistic preference, optional polish idea, examiner exposure, thesis-silent question, or future appendix/notes need that is not a defect in the locked deck.

**Action:** Never reopen the deck on this basis. Route it to speaker notes, appendix planning, rehearsal, logistics, or the exposure register.

## Fix-versus-record decision rule

Use a two-key reopening rule. Key 1, necessity: the finding must be evidence-backed, violate the approved thesis, ledger, or a functional final-PDF requirement, and be rated blocker or major under the rubric. Key 2, safe executability: the exact bounded patch, authoritative replacement, canonical WeasyPrint path, full dependent-artifact rebuild, 300-DPI reinspection, hash update, rollback, and user authorization must all be available. Fix only when both keys are true. If Key 1 is false, record as minor or note and leave the lock intact. If Key 1 is true but Key 2 is false, record the confirmed defect as BLOCKED and do not substitute Chrome or another renderer. A minor item may be bundled only into an already authorized must-fix batch when it is isolated and zero-reflow; it can never initiate reopening.

## Finding-log minimum schema

- `finding_id`
- `check_id`
- `slide_or_deck_scope`
- `candidate_description`
- `violated_authority`
- `evidence_paths`
- `reproduction_steps`
- `defense_consequence`
- `severity`
- `classification`
- `proposed_patch_or_nonpatch_action`
- `renderer_gate`
- `reopening_key_1`
- `reopening_key_2`
- `disposition`
- `reviewer_1`
- `reviewer_2`
- `user_authorization`
- `final_status`

## Speaker-notes production plan

### Structure

Produce notes only after the deck audit closes and the final PDF is frozen. For each slide, use a fixed record: slide job; opening cue; two to four ordered speaking beats tied to visible elements; exact academic claim IDs; interpretation; required boundary or qualification; transition cue; optional cut beat; interruption-resume cue; likely examiner follow-up; source filename and line range; prohibited claims. Keep the notes in a separate MAIN_DECK_SPEAKER_NOTES.md and maintain a SPEAKER_NOTES_SOURCE_MAP.csv so the locked PDF is not modified merely to store notes.

### Word and time budget

Do not invent approved per-slide times. Measure the presenter twice on 90-second thesis-grounded passages and use the lower clean words-per-minute rate. Set the total drafted-word cap to that rate multiplied by 17.0 minutes, leaving one minute inside the approved 18-minute target for pauses, navigation, and recovery. Allocate the cap by the approved section ratio 5:10:3: Intro 27.8 percent, Message 55.6 percent, Outro 16.7 percent, with transitions counted inside each section. Allocate slide-level caps only after the first timed slide-only walkthrough; record them as provisional, then cut until three complete rehearsals are at or below 18:00 without rushing. The hard 20-minute limit is never used as the drafting target.

### Grounding rules

- Every academic sentence and every number in the notes must cite a claim ID that maps to an exact approved-thesis filename and line range or table cell.
- Notes may explain the visible slide but may not add a new result, mechanism, causal claim, sample rationale, data procedure, or appendix-only analysis to the main talk.
- When the thesis is silent, the notes must say that the thesis does not specify the point; they may record a verified project fact separately, but must not invent an answer.
- Use the approved descriptive, mechanism, cash-language, and war-chest boundaries from the ledger. A spoken qualification cannot be used to excuse misleading slide wording.
- Keep one terminology dictionary across slides and notes. The first spoken expansion of each acronym or symbol must match the slide sequence.
- Source-map and note edits are versioned and hashed. Any change to a substantive claim triggers a source recheck and a fresh timed rehearsal.
- Speaker notes remain a delivery artifact, not a substitute for appendix evidence. Detailed robustness, additional analyses, and examiner-specific tables stay in the approved appendix architecture.

### Quality gates

- Grounding gate: 100 percent of academic sentences and numbers have valid source-map entries; no unresolved source conflict remains.
- Slide-alignment gate: every speaking beat points to a visible slide element or is a short transition; no central visual is left uninterpreted.
- Boundary gate: automated and human review find no causal, mechanism, cash-only, war-chest, or difference-in-significance drift.
- Speakability gate: the presenter can deliver each slide without silently rewriting the sentence order or reading dense text verbatim.
- Timing gate: three complete clean runs finish at or below 18:00, section timing remains close to 5:10:3, and no run relies on rushing.
- Interruption gate: every slide has a resume cue and the presenter can answer or defer a likely question without losing the narrative path.
- Freeze gate: the approved notes, source map, and rehearsal log are hashed and archived beside the final deck audit package.

## Plan self-critique and detection signals

- **Blind spot:** Official defense requirements were not provided, so the plan cannot test unknown mandatory branding, citation, submission, or procedure rules. **Detection signal:** A later official guideline introduces a requirement not represented in D01-D15 or conflicts with the locked architecture.
- **Blind spot:** The approved thesis source files used for execution were not attached to this planning call; the plan relies on the operator-held, hash-verified files described in AUDIT_CONTEXT.md. **Detection signal:** D02-C01 cannot produce exact filenames, hashes, and authority status for every source before substantive checks begin.
- **Blind spot:** Committee intelligence may overweight expected questions and underweight an examiner concern not represented in the risk register. **Detection signal:** A blind reviewer generates a high-consequence question that cannot be mapped to any D13 exposure category.
- **Blind spot:** Known candidate findings can anchor the operator and cause excessive attention to already noticed issue classes. **Detection signal:** The blind second pass finds blocker or major issues in dimensions that received little evidence in the first pass.
- **Blind spot:** Semantic checks for causality, mechanism, novelty, and speakability can vary across reviewers. **Detection signal:** Reviewers repeatedly disagree on D05, D07-C05, D08, or D11-C04 classifications despite reading the same evidence.
- **Blind spot:** Projection simulation cannot reproduce the actual room, projector, lighting, or viewer distance. **Detection signal:** A real-room equipment test reveals unreadable or low-contrast elements that passed D10-C05.
- **Blind spot:** The canonical renderer outage can turn a confirmed must-fix issue into an unresolved operational risk. **Detection signal:** D14-C05 remains BLOCKED after the audit has identified a blocker or must-fix major.
- **Blind spot:** A highly detailed checklist can produce mechanical completion without understanding the argument. **Detection signal:** All check boxes are closed, but a fresh reviewer cannot state the three research-question-to-finding paths or identifies a cross-slide contradiction.
- **Blind spot:** Text-layer and coordinate checks can miss a perceptual ambiguity that is technically well formed. **Detection signal:** Independent viewers choose different intended reading orders, chart associations, or comparison targets on the same raster.
- **Blind spot:** The speaker-notes timing model depends on the presenter's measured pace and may change under defense stress or interruption. **Detection signal:** Timed runs vary widely or interrupted rehearsals approach the 20-minute limit despite clean runs meeting 18:00.

## Later independent review

Yes, one later independent review is warranted after the local audit is executed and the first full speaker-notes draft and rehearsal log exist. Its scope must be limited to false-negative detection and triage consistency: identify only missed blocker or major deck defects, unsupported or drifting note claims, missing evidence, and misclassified exposures. It must not redesign slides, propose a new architecture, re-open minor preferences, or draft replacement notes. Inputs must include the final PDF and hash, exact 300-DPI rasters, extracted text, ledger, this plan, completed execution and findings logs, source manifest and claim map, calculation log, dispositions, notes draft and source map, and rehearsal log. The reviewer should not receive the operator's original candidate-finding list until after its blind report.

## Completion rule

The audit is complete only when every check ID has a closed status and evidence path, no blocker or must-fix major remains unresolved, all recorded-only items have owners, the deck disposition is frozen, and the evidence package hash manifest validates. Speaker-note production begins only after that point.
