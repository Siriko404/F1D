# CURRENT DEFENSE HANDOFF LEDGER

Last updated: 2026-07-13 22:37 EDT, America/Toronto
Status: ACTIVE CANONICAL HANDOFF

## 1. READ THIS FIRST

This is the compaction-safe continuity file for the current thesis-defense work.
After any context reset, read this file before taking action.

For targeted work after reading this ledger, use
`docs/Defense/_TARGETED_READING_MAP.md`. It assigns conservative, task-specific
line ranges from the thesis, historical master, and audit report so that all three
sources are consulted without requiring a full reread for every small task.

Update it whenever any of the following changes:

- the current task or next action;
- a factual correction;
- a user-approved presentation decision;
- the active deck or render;
- an unresolved risk or blocker.

Keep the `CURRENT STATE` section current. Append material decisions to the change
log. Do not turn this into a transcript or research dump.

## 2. USER DIRECTIVES

- Start from the beginning. Previous presentation work is outdated and is input
  only, not authority.
- The current task is a full presentation redesign from first principles, beginning
  with the story and overall architecture rather than continuing a slide-by-slide
  patch of the old master.
- Read and reason from the complete flattened thesis.
- The prior master audit was completed directly. Do not use a counsel or subagents
  for the redesign.
- Work gradually. Do not produce the whole presentation at once.
- Keep chat concise.
- Use visualizations where they genuinely clarify the thesis.
- The presentation is 20 minutes.
- Supervisors: Ali Akyol and Harshit Rajaiya.
- Examiners: Shantanu Dutta and Rengong (Alex) Zhang.
- The active slide implementation is HTML/CSS rendered to PDF, not Beamer.
- Screenshots used for visual review must come from the compiled PDF.
- Do not resume the interrupted Slide 5 audit-approval prompt after compaction.
- Do not edit the master reference or deck until the new story architecture has
  been evaluated and approved by Sina.
- The ChatGPT Web reasoning gate applies to every task in this collaboration, not
  only thesis or defense work. Before substantive work, explicitly classify the
  task as reasoning-heavy or routine.
- Reasoning-heavy work includes planning, architecture, investigation, diagnosis,
  deep or multi-source web research, consequential judgment or trade-offs,
  synthesis across substantial evidence, and substantial artifact design or
  creation. For such work, pause and prepare a self-contained package in
  `docs/Defense/chatgpt/current_upload/` before doing the substantive work.
- Routine deterministic work—simple file operations, direct authoritative
  lookups, mechanical formatting, execution of an approved plan, and small
  unambiguous corrections—may proceed locally without a Web call.
- ChatGPT Web may reason, research, investigate, plan, execute authorized work,
  and create artifacts from uploaded files or authorized web sources.
- Every Web call must return an actual downloadable main `.json` response file
  conforming to the supplied schema. Requested artifacts must be returned as
  additional files and enumerated in the JSON artifact manifest.
- ChatGPT Web must say nothing in chat. Its complete delivery is only the main
  JSON attachment and any artifact attachments. No acknowledgment, prose,
  markdown, code block, or link text is permitted.
- Existing audit approvals remain evidence-backed guardrails and useful input, but
  they do not lock the slide count, order, titles, timing, or architecture of the
  redesigned presentation.
- Commit each meaningful checkpoint as work proceeds so the redesign, review
  packages, returned artifacts, and continuity records remain recoverable. Stage
  only in-scope work and preserve unrelated user changes.

## 3. SOURCE AUTHORITY

### Primary thesis authority

`docs/Thesis/_uottawa_rewrite/_thesis_FLAT.tex`

- Verified length: 1,621 lines.
- Read completely during the pre-compaction audit session, including front matter, all
  narrative sections, every table and note, references, robustness analyses,
  appendices, and `\end{document}`.
- SHA-256 at the completed read:
  `6F2E003FF63EEBB23BED8FE26DBD1601D0B5392A6628320D8782F60D5F936310`

### Completed audit input

`docs/Defense/2026-07-13-master-reference-audit-report.md`

- Complete audit of the prior master against the thesis and presentation standards.
- Verified length: 429 lines.
- SHA-256:
  `50BF843D9DF16822E9F3616166697A05A8EDD89CDAAC43F22FAAF9D06415A499`
- Treat its findings as diagnostic input and guardrails, not as a mandatory new
  architecture.

### Prior presentation draft

`docs/Defense/DEFENSE_PRESENTATION_MASTER_REFERENCE.txt`

Treat this as historical design input. Do not incrementally patch it or accept its
story structure by default. Evaluate what should be retained, changed, merged, or
discarded after the new narrative spine is approved.

### Presentation-design evidence

- The completed audit contains the official uOttawa/Telfer and reputable university
  presentation-design sources already researched.
- External sources may inform presentation convention, accessibility, branding,
  timing, and visual design only. All empirical claims and plotted values must come
  from the flattened thesis.

### Historical files

The following are historical input only and are not current authority:

- `_DEFENSE_LEDGER.md`
- `_DEFENSE_PREP_STATE.md`
- `_CODEX_HANDOFF_2026-07-12.md`
- older Beamer `.tex` and `.pdf` files
- archived counsel material

### Targeted reading protocol

`docs/Defense/_TARGETED_READING_MAP.md`

- Verified length: 235 lines.
- SHA-256:
  `53DB02CA972A2328651CB8FCC0DB2552DF78A247EA5C94F9978CEA5BD1125C16`
- Use after reading this ledger.
- Every substantive task bundle includes readings from the thesis, historical
  master, and audit report.
- Each bundle is additive to the map's always-on baseline.
- The map is pinned to the current line counts and SHA-256 hashes. Refresh it if
  any source hash changes.
- Escalate to broader sections or a full reread when a claim crosses bundles,
  remains ambiguous, or affects the whole story.

## 4. CURRENT STATE

### Active task

Redesign the defense presentation from the beginning. Start with the big-picture
storyline and audience journey, using the flattened thesis as empirical authority,
the completed audit as diagnostic evidence, the old master/deck as historical input,
and the sourced presentation standards as design guidance.

Do not resume the prior slide-by-slide audit sequence. Do not revise the master
reference or HTML/CSS deck until Sina approves the new story architecture.

Sina has approved the disclosure-boundary narrative spine. The current design
task is to develop and approve that story one narrative act at a time before
deciding the slide map.

An independent ChatGPT Web review returned `REVISE` on Act 1 while explicitly
confirming that no alternative materially outperforms the disclosure-boundary
spine. Its five corrections were checked against the thesis and adopted. The
current Act 1 is:

> Consider a firm that has privately committed to an acquisition. The firm knows;
> the market does not. It may remain silent about the deal. Yet a routine earnings
> call still occurs, and once management speaks, it cannot mislead.
>
> Prior work documents pre-announcement price run-ups, managed tone before
> stock-for-stock acquisitions, and strategy vocabulary around acquisition
> activity. To our knowledge, it has not examined uncertainty language in the
> CEO's unscripted Q&A answers during the anticipatory window before an
> undisclosed acquisition.
>
> Is uncertainty in the CEO's unscripted Q&A answers elevated while a cash
> acquisition remains undisclosed—and does it recede once the deal becomes public?
>
> The evidence suggests that it does.
>
> **Transition:** How can we separate call-specific uncertainty from persistent
> CEO speaking style and other predictable call conditions?

### ChatGPT Web protocol state

- Protocol: `docs/Defense/chatgpt/CHATGPT_WEB_PROTOCOL.json`
  - Version: `2.0`, universal reasoning gate.
  - SHA-256: `ED2493A2EC680845A6F2B36CEF3A3EFF004EDCC2B4F488422B56EFEDDB848DC0`
- Request schema: `docs/Defense/chatgpt/current_upload/WEB_REQUEST_SCHEMA.json`
  - SHA-256: `044889EA731E8066A5FA6AA0D1A66CB82F6B266172C9EFD2A25D5463BEBF5F1F`
- Response schema: `docs/Defense/chatgpt/current_upload/WEB_RESPONSE_SCHEMA.json`
  - SHA-256: `4DD078CF1A0D56FA6EBED0A5B1CAF6A377505D08E035646C6835C8DC0EE54B59`
- Silent paste prompt:
  `docs/Defense/chatgpt/current_upload/PASTE_THIS_PROMPT.txt`
  - SHA-256: `F6697B008CB46FA004BAE2C45103B78893323EB82A82E08CD3844C4CE290E6CA`
- Active request:
  `docs/Defense/chatgpt/current_upload/WEB_REVIEW_REQUEST.json`
  - Request ID: `defense-act2-measure-design-bridge-2026-07-13-v1`.
  - SHA-256: `26BBFC79181B2BC70E29687845EF5D8FEFA89634AF175EB3A0127273FC9EC6EE`.
  - Expected main response: `2026-07-13_act2_measure_design_review.json`.
  - Required artifact: `ACT2_DESIGN_PROPOSAL.md`.
  - Web research is disabled; only uploaded files may be used.
- Normalized first response:
  `docs/Defense/chatgpt/received/2026-07-13_act1_review_response.json`
  - SHA-256: `57902076B7D2A44BD47AF43057B7247E3B5FFFC103FDE8238BEF073D2D0BA120`
  - Provenance is explicitly `CODEX_NORMALIZED_LEGACY_PROSE`; the first response
    was pasted as prose before the downloadable-JSON rule existed.
- `current_upload/` is now the active Act 2 submission package. It contains the
  four refreshed source copies, the two schemas, the silent paste prompt, and the
  task-specific `WEB_REVIEW_REQUEST.json`—eight files in total. Sina must upload
  every file in this directory and paste `PASTE_THIS_PROMPT.txt` verbatim.
- The prior prose-based Act 1 request is preserved under
  `docs/Defense/chatgpt/archive/001_act1_review_legacy_text_request/`.
  That archive also preserves protocol and schema version 1, which governs the
  normalized legacy response. New responses use universal schema version 2.
- Persistent workspace instructions were added to `F1D/AGENTS.md` so the triage
  and silent file-delivery gate survives beyond the defense workflow.
  - SHA-256: `AFDE4A0652680CED960BB5BD9D402258448F8408A9D6D78F67E6F2F4C127D20E`
- Fresh end-to-end package verification at 2026-07-13 22:35 EDT found exactly
  eight expected upload files, parsed every JSON file, validated both version-2
  schemas and the active request, matched all four source copies, matched the
  active request/response/artifact contract, scanned the package for API-key
  patterns, and returned `FAILURES=0`.

### Work completed

- The Act 2 task was classified as reasoning-heavy. A task-specific ChatGPT Web
  request was created to compare two or three measure-and-design bridge
  architectures, recommend one concise narrative, partition core versus deferred
  methods content, preserve the first-stage/second-stage distinction, and produce
  `ACT2_DESIGN_PROPOSAL.md`. The request and complete eight-file upload package
  passed fresh verification with `FAILURES=0`.
- The first external ChatGPT Web review was received in prose, normalized into a
  local JSON record, and used to revise Act 1. It confirmed the selected spine and
  corrected the novelty qualifier, literature descriptions, cash-deal scope, and
  transition attribution.
- A structured ChatGPT Web protocol was established under
  `docs/Defense/chatgpt/` and then generalized to every task in the collaboration.
  Task questions and requested work live in a JSON request; the response must
  validate against a supplied JSON schema; artifact outputs are allowed and
  manifest-controlled; and ChatGPT Web must return files without chat text.
- The targeted reading map's always-on baseline and Bundle 1 were read after the
  compaction checkpoint. All three source hashes still match the map's source
  lock. The essential argument was reconstructed independently of the old slide
  order, and three possible narrative spines were compared. The recommended
  spine is the disclosure-boundary story, but Sina has not yet approved it.
- A conservative targeted reading map was created at
  `docs/Defense/_TARGETED_READING_MAP.md`. It divides future work into fourteen
  task bundles, each drawing from all three authoritative inputs, and defines
  source-hash, numerical-plot, overlap, and full-reread escalation rules.
- At the start of the first-principles redesign, the complete 1,621-line flattened
  thesis, complete 1,651-line historical master reference, and complete 429-line
  audit report were reread directly in verified line-numbered sections. Their
  SHA-256 hashes remained unchanged from the values recorded below.
- The obsolete counsel run was archived without deletion.
- No DeepSeek counsel run was launched and no API charges were incurred.
- The entire flattened thesis was read and mechanically verified.
- The master reference was read completely.
- The active web-deck files and latest PDF were located and verified.
- The audit goal, scope, evidence rules, output format, and stopping rule were
  clarified with Sina one decision at a time.
- Sina selected the integrated evidence-matrix audit approach.
- The written audit contract was created and self-reviewed at
  `docs/Defense/2026-07-13-master-reference-audit-design.md`.
- Sina directed that the audit be redone in the current session.
- The complete 1,621-line flattened thesis and complete 1,651-line master
  reference were reread directly in the current session.
- Official uOttawa/Telfer requirements and reputable university presentation
  guidance were researched and cited under the approved evidence hierarchy.
- The integrated audit report was completed and self-verified at
  `docs/Defense/2026-07-13-master-reference-audit-report.md`.
- Report verification: 429 lines, SHA-256
  `50BF843D9DF16822E9F3616166697A05A8EDD89CDAAC43F22FAAF9D06415A499`,
  five critical findings, eight web citations, eleven proposed core slides,
  and an exactly 18:00 provisional timing map.
- At verification, the thesis and master hashes were unchanged from the start
  of the current session. The active deck was not modified.

### Work not yet completed

- The active Act 2 Web request has not yet been submitted, and no response or
  artifact has been received or adopted. The request is a review brief, not an
  approved Act 2 design.
- The disclosure-boundary story is approved as the first-principles narrative
  spine, and the thesis-corrected version of Act 1 above is the current design.
  Acts 2 onward, the slide count, order, timing allocation, and visualization
  program remain open and must be designed rather than inherited.
- The prior audit review stopped before Slide 5 was approved; do not resume there.
- The old master reference has not been revised and is no longer the document to
  patch incrementally.
- The audit's proposed eleven-slide architecture remains unratified input only.
- The existing four-slide HTML/CSS deck has not been audited against the
  new story and should not be treated as a design baseline or final work.
- No timing has been validated by a spoken rehearsal.
- Exact handling of deals that are precisely 50% cash and 50% stock is not
  documented in the two permitted content sources. Sina directed us to use the
  working assumption that these deals are dropped; this remains unverified.

### Immediate next action

1. Do not restart the Slide 5 audit prompt and do not design Act 2 locally before
   the external response.
2. Sina uploads all eight files from `docs/Defense/chatgpt/current_upload/` to
   ChatGPT Web and pastes `PASTE_THIS_PROMPT.txt` verbatim.
3. ChatGPT Web must return no chat text—only
   `2026-07-13_act2_measure_design_review.json` and
   `ACT2_DESIGN_PROPOSAL.md` as downloadable attachments.
4. Sina returns both downloaded files. Validate the JSON against the response
   schema, verify the artifact hash and manifest, and independently check important
   thesis claims before use.
5. Integrate only warranted conclusions, then present Act 2 concisely for Sina's
   approval. Continue the same process for later heavy design decisions.
6. Only after the story is approved, define the slide map and revise or replace the
   master reference. Build HTML/CSS slides only after content approval.

## 5. EXISTING DECK LOCATION

Directory:

`docs/Defense/web_deck/`

Current source:

- `index.html`
- `styles.css`

Latest located PDF:

- `defense-web-review-4.pdf`
- verified as four pages at 1440 x 810 points;
- the HTML currently contains four slide sections.

The older Beamer deck remains on disk but is not part of the redesign path.
The current four-slide web deck is now a historical prototype only. It may be
reused selectively after the new story is approved, but it is not the starting
architecture for the redesign.

## 6. KEY AUDIT FINDINGS

These are selected findings established by the completed audit. The complete audit
report is `docs/Defense/2026-07-13-master-reference-audit-report.md`.

### Definite factual correction

The master reference labels the matched event-study sample as `28,102 calls` in
two places. The thesis reports `28,102 firm-quarters` across 1,320 firms. Replace
`calls` with `firm-quarters`.

Relevant thesis evidence:

- narrative line 286;
- matched-event-study table line 630.

### Timing limitation

The twelve `Suggested spoken` blocks total approximately 685 words. That is only
about six minutes at a normal defense pace. Therefore the slide timings in the
master are desired allocations, not validated durations. They must not be called
realistic until fuller speaker notes and a rehearsal exist.

### Narrative duplication to scrutinize

Slides 8 and 9 repeat the matched-sample language event-study result. Slide 9
adds the cash path, but much of Slide 8 is shown again. Decide during the story
audit whether to merge them or give them sharply different jobs.

### Wording requiring tightening

- A single insignificant PRE2 estimate is a limited pretrend check. It does not
  establish the absence of all earlier pretrends.
- `The trace ends when the deal becomes public` is stronger than the direct
  evidence. The evidence is that GAP is indistinguishable from zero and the
  PRE1-minus-GAP contrast is significant.
- The analyst-scrutiny interaction is underpowered. Prefer `the run-up survives
  the measured scrutiny control` over wording that sounds like scrutiny has been
  ruled out.

### Data-source wording

The thesis describes IBES as supplying earnings records used for the
earnings-surprise control. Avoid describing IBES broadly as a source of `analyst
information` unless a more specific thesis-supported use is stated.

### Important unresolved design-definition question

The thesis defines cash deals as at least 50% cash and stock deals as at least
50% stock. The two-file audit cannot determine how exact 50/50 deals are handled.
Sina directed us to proceed on the working assumption that exact 50/50 deals are
dropped. Preserve that status as an assumption unless it is independently verified.

## 7. NON-NEGOTIABLE INTERPRETIVE BOUNDARIES

- The evidence is descriptive, correlational, and within firm.
- No causal mechanism is identified.
- Compliance-constrained speech and strategic silence are observationally
  equivalent in these data.
- The stock estimate is negative, imprecise, and statistically insignificant.
  Do not describe it as a fall or suppression.
- The cash-versus-stock result supports concentration, not strict specificity.
- The cash-accumulation mechanism remains open.
- Cash persistence through GAP rests on the absence of a PRE1-to-GAP decline;
  the GAP cash coefficient itself is not statistically significant.
- The generated-regressand standard-error caveat is real and belongs in the core
  limitations slide, with fuller technical detail available in backup/Q&A.
- The bid-ask analysis reports component-specific associations. It does not test
  the difference between scripted and unscripted components directly.

## 8. ARCHIVE LOCATION

Abandoned counsel run:

`docs/Defense/archive/counsel-runs/2026-07-13-master-reference-hard-scrutiny-abandoned-before-fire/`

It is archived for provenance only. Do not resume it.

## 9. UPDATE PROTOCOL

For every meaningful work unit:

1. update `Last updated`;
2. rewrite `CURRENT STATE` so it describes the present, not history;
3. add or revise verified findings;
4. record user-approved decisions in the log below;
5. keep the immediate next action executable and unambiguous;
6. never store API keys, passwords, or secrets here.

## 10. DECISION AND CHANGE LOG

### 2026-07-13

- Sina rejected the prior-session presentation work as authority and requested a
  fresh thesis-first approach.
- Sina ended the counsel workflow and chose a direct self-audit.
- The counsel run was archived rather than deleted.
- Sina required a complete line-by-line read of the flattened thesis; completed
  and verified at 1,621 lines.
- Sina clarified that the current task remains auditing the master reference,
  not beginning a new redesign.
- The active HTML/CSS deck was located with four current slides.
- This living handoff ledger was created as the canonical continuity file.
- Audit deliverable decision: produce the audit report first; do not modify the
  master reference until Sina approves the findings.
- Academic-standards evidence hierarchy: official uOttawa/Telfer requirements
  first, followed by reputable university and research-communication guidance.
- Audit-depth decision: check the entire scope internally, but report only
  actionable findings, organized by severity and slide.
- Scope decision: audit the full master reference, including the core slide plan,
  timing, suggested speech, Q&A bank, backup-slide plan, and build standards.
- Sequence decision: exclude the existing four-slide HTML deck from this audit.
  Audit the deck separately after the master-reference audit is approved.
- Claim-grading decision: classify thesis-related claims as `verified`,
  `defensible inference`, or `unsupported/overstated`.
- Timing decision: evaluate the presentation against an approximately 18-minute
  rehearsed target, preserving a two-minute buffer within the 20-minute limit.
- Visualization-source decision: new statistical charts and explanatory diagrams
  are strongly encouraged, but every data value and empirical claim they encode
  must come only from `docs/Thesis/_uottawa_rewrite/_thesis_FLAT.tex`. Do not use
  datasets, generating code, other repository outputs, or outside empirical data.
  External sources may be used only to establish presentation-design standards.
- Visual-density goal: because the thesis contains no figures, the audit must
  research academic presentation conventions and determine the appropriate
  amount and placement of meaningful visualization. Do not impose a visual quota
  in advance and do not ask Sina to choose the convention.
- Audit-report detail: every actionable issue must include the evidence, why the
  issue matters, and an exact recommended correction or replacement.
- Standards-authority labels: distinguish `formal requirement`, `strong academic
  convention`, and `design judgment`; never present a recommendation as a rule
  when no governing rule exists.
- Architecture decision: everything is subject to scrutiny. The audit may
  recommend merging, splitting, reordering, adding, or removing slides. The
  current 12-slide structure, timing map, narrative, and implementation standards
  are not fixed constraints.
- Audit-method decision: use the integrated evidence-matrix approach combining
  thesis fidelity, sourced academic-presentation standards, and whole-deck
  architecture. Design recorded in
  `docs/Defense/2026-07-13-master-reference-audit-design.md`.
- Historical audit checkpoint, now superseded: the written audit contract existed
  and was self-reviewed before the audit was authorized. At that time, no audit
  execution or master/deck modification had started under the new protocol.
- Sina then explicitly required the audit to be redone in the current session,
  which served as authorization to execute the approved audit protocol inline
  without subagents.
- The full thesis and master were reread directly in the current session before
  audit conclusions were drawn.
- The completed audit report is
  `docs/Defense/2026-07-13-master-reference-audit-report.md`. It recommends five
  critical corrections, merging the duplicated timing slides, an eleven-slide
  provisional architecture, eight substantive visuals, consolidated backups,
  and stronger typography/citation standards.
- The audit stopped at the report as required. The master reference, thesis, and
  HTML/CSS deck were left unchanged pending Sina's decision.
- Sina approved critical finding C1: replace both erroneous instances of
  `28,102 calls` with `28,102 firm-quarters across 1,320 firms` when the master
  reference is revised.
- Sina approved critical finding C2: replace the overstated Slide 2 title with
  `The firm knows; the market does not.`
- Sina approved critical finding C3: qualify the final takeaway as evidence that
  `suggests` a readable anticipatory trace, followed by the explicit boundary:
  `The pattern is within-firm and correlational; the mechanism remains open.`
- Sina approved critical finding C4: remove `cognitive load` and `planning
  uncertainty` and state that the data cannot distinguish compliance-constrained
  speech from strategic silence or identify a broader mechanism.
- For critical finding C5, Sina directed us to assume that exact 50/50 cash/stock
  deals are dropped. This is a presentation working assumption, not a fact
  documented in the flattened thesis.
- Sina approved timing finding M1: target a rehearsed duration of 17:30--18:00,
  preserve the two-minute buffer, treat slide timings as provisional, and validate
  them through at least three complete rehearsals.
- Sina approved whole-story finding M2: merge the duplicated Slides 8 and 9 into one
  approximately three-minute `Two clocks` slide with aligned UncResCEO and CashRatio
  panels on the matched 28,102-firm-quarter sample.
- Sina approved whole-story finding M3: remove the premature event clock from the
  title slide, introduce it on the disclosure-setting slide, and formalize it on the
  research-design slide.
- Sina approved whole-story finding M4: keep the secondary bid--ask result in backup
  and retitle the final core slide `Core result and boundaries` so it does not imply
  an exhaustive account of every thesis contribution.
- Sina approved the Slide 2 recommendations: retain the careful silence/misleading
  legal formulation, cite *Basic v. Levinson* and SEC Rule 10b-5, use one
  disclosure-bind diagram instead of bullet-heavy explanation, and introduce the
  event clock visually without technical detail.
- Sina approved the Slide 3 recommendations: use `undisclosed acquisition`, retain
  `To our knowledge` on the positioning claim, cite the three adjacent literatures,
  and keep the slide focused on one research question and its gap.
- Sina approved the Slide 4 recommendations: describe UncResCEO as a call-specific
  residual rather than mental state, visualize its decomposition, distinguish the
  first- and second-stage control layers, and include the generated-regressand
  standard-error caveat on the core limitations slide.
- Sina stopped the slide-by-slide audit review before approving Slide 5 because the
  individual corrections were difficult to evaluate without the whole storyline.
- Sina directed a full redesign from the beginning. The next session must first
  build and evaluate the presentation's narrative spine from the flattened thesis,
  completed audit findings, relevant presentation standards, and useful historical
  input. Existing approvals remain guardrails, but the old master, proposed
  eleven-slide audit architecture, and four-slide web deck are not binding designs.
- Before any redesign decision, Sina required another complete read of the flattened
  thesis, historical master reference, and audit report. All three were reread in
  full in verified line-numbered sections; no presentation architecture has yet
  been selected.
- Sina requested a conservative section-by-section reading allocation so future
  small tasks would not require rereading all three complete files. The resulting
  `_TARGETED_READING_MAP.md` requires relevant readings from all three files for
  every substantive task and is hash-pinned to the current source versions.
- Compaction checkpoint after creating the targeted map: the next executable task
  is to read the map's always-on baseline plus Bundle 1, reconstruct the essential
  defense argument, and then compare narrative architectures. No story architecture,
  slide map, master revision, or deck implementation has yet been approved.
- Sina selected narrative option 1: the disclosure-boundary story. This is now the
  approved spine. No detailed narrative act, slide map, timing map, or deck build
  has yet been approved under that spine.
- The first ChatGPT Web review returned `REVISE`, retained the disclosure-boundary
  spine, and supplied a thesis-faithful Act 1. Its corrections were adopted:
  qualify novelty with `To our knowledge`; describe each adjacent literature
  precisely; scope the question to cash acquisitions; and replace the attributive
  `deal-related trace` transition with a neutral measure-construction question.
- Sina expanded the external-review protocol into a universal gate for every work
  item. Codex must first decide whether each task is reasoning-heavy. Planning,
  investigating, deep web research, consequential synthesis, and substantial
  artifact work require a Web package; routine deterministic tasks do not.
- ChatGPT Web may be asked to perform work and create artifacts. Its response must
  be silent and file-only: one schema-valid downloadable JSON file as the main
  response, plus any requested artifact files listed in its artifact manifest.
- The first task-specific request under universal protocol version 2 was prepared
  for Act 2. It requests an independent measure-and-design bridge analysis and the
  standalone artifact `ACT2_DESIGN_PROPOSAL.md`, prohibits web research and
  outside empirical content, and does not authorize finished slides or code.
- Sina directed that meaningful work be committed continuously. The first
  preservation checkpoint includes the defense sources, historical review
  artifacts, archives, current Web package, and continuity records; reproducible
  Chromium profile caches and LaTeX intermediate files remain ignored.
