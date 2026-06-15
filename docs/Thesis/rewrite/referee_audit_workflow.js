export const meta = {
  name: 'referee-audit',
  description: 'READ-ONLY referee audit of the uOttawa thesis draft across 5 aspects (cohesion, coherence, logic, argument-weaknesses, citation-accuracy). Each aspect = 3 independent finders run the SAME job in parallel + 1 adversarial red-team that CULLS non-binding findings and synthesizes. A final pass dedups across aspects and severity-ranks into ONE findings ledger. Nothing in the repo is edited; the only output is the returned ledger (the caller writes it to disk).',
  phases: [
    { title: 'Cohesion' },
    { title: 'Coherence' },
    { title: 'Logic' },
    { title: 'Weaknesses' },
    { title: 'Citation' },
    { title: 'Synthesize' },
  ],
}

const R = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D'

// ---------------------------------------------------------------------------
// READING MANIFEST -- every agent reads the ACTUAL draft itself, in full.
// ---------------------------------------------------------------------------
const MANIFEST = `READING MANIFEST -- read every file yourself, in full, before judging (absolute paths):

THE DRAFT UNDER AUDIT (this is what you referee):
  ${R}/docs/Thesis/thesis_draft_uottawa.tex   -- master: title/abstract, Section 1, Section 2.x, Section 5, the \\bibitem bibliography, the appendix. It \\input's the two files below.
  ${R}/docs/Thesis/sec34_body_from_ledgers.tex -- Section 3 (Main Analyses) + Section 4 (Additional Analyses, incl. 4.2 Bid-Ask Spread).
  ${R}/docs/Thesis/_tables_from_bible.tex      -- the 12 result tables, byte-exact (summary_stats ... h14c_ceo2_decomp). Numbers in prose must match these cells.

GROUNDING (the claim ceiling + house register; do NOT treat deliberate hedging as a fault):
  ${R}/docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md -- read sections 6 (severity), 9 (anti-patterns), 10 (E1: test a critique's PRECONDITION before its mechanism; E2: cite the executable line, not the comment).
  ${R}/docs/Thesis/rewrite/claim_findings_ledger.json -- the ratified claim ceiling (C1-C7): the prose may not say MORE than these support. Over-reading above the ceiling is a finding; staying at/below it is correct, not a fault.
  ${R}/docs/Thesis/variable_ledger.json -- variable -> definition (ignore DROPPED entries).`

const REGISTER_LOCKS = `HOUSE REGISTER (binding -- do NOT flag these as weaknesses; flag only their VIOLATION i.e. OVER-claiming):
- Results are correlational, NOT causal. "No identification" is stated on purpose.
- A null is a failure-to-find, NOT a proof of equivalence ("does not account for THIS run-up, not that scrutiny never matters anywhere").
- A significant-vs-insignificant contrast is NOT a formal difference test (Gelman-Stern); only a Wald/interaction is.
- Concentration, not strict specificity. Change-in-cash, not level. Correct hedging is the target, not a defect.`

const GLOBAL_RULES = `HARD RULES (every agent):
- READ-ONLY. You MUST NOT edit, write, or create any file. You only read and return the structured object. This is an audit, not a fix.
- EVIDENCE OR IT DOES NOT EXIST. Every finding carries: a VERBATIM draft quote (copy it exactly), its location (section + nearest \\label or paragraph id, e.g. "Section 4.2 PARA3"), and a ground-truth pointer. A finding whose quote you cannot reproduce verbatim in the draft is INADMISSIBLE -- drop it.
- TEST THE PRECONDITION BEFORE THE MECHANISM (AUDIT_PROTOCOL E1). Before raising any named critique, state the draft's exact claim and its estimand in one line, then the critique's trigger condition; raise it ONLY if the trigger holds. mechanism-present != critique-binds.
- STAY IN YOUR LANE. Report ONLY your assigned aspect. If you notice something in another lane, ignore it -- another team owns it.
- SEVERITY: CRITICAL (a claim/number/citation is wrong) / MAJOR (referee-exploitable: overclaim, unsupported attribution, real logic gap) / MINOR (local) / NIT (style). No fixes at any level.
- COVERAGE: list every section you examined. The audit must be able to prove the whole draft was checked.
${REGISTER_LOCKS}`

// ---------------------------------------------------------------------------
// STRUCTURED OUTPUT SCHEMAS
// ---------------------------------------------------------------------------
const FINDING = {
  type: 'object',
  required: ['aspect', 'severity', 'location', 'draft_quote', 'issue', 'reason', 'recommendation', 'evidence'],
  properties: {
    aspect: { type: 'string', enum: ['cohesion', 'coherence', 'logic', 'weaknesses', 'citation'] },
    severity: { type: 'string', enum: ['CRITICAL', 'MAJOR', 'MINOR', 'NIT'] },
    location: { type: 'string', description: 'section + nearest label/paragraph id, e.g. "Section 4.2 PARA3"' },
    draft_quote: { type: 'string', description: 'VERBATIM text from the draft that is the problem (must reproduce exactly)' },
    ground_truth_pointer: { type: 'string', description: 'citation: receipt file + the cited_text span. coherence/logic: the other location it conflicts with. else "".' },
    issue: { type: 'string', description: 'what is wrong, in one sentence' },
    reason: { type: 'string', description: 'why it binds: the draft claim/estimand + the trigger that holds (E1)' },
    recommendation: { type: 'string', description: 'what a fix would do -- NOT applied' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'pointers: quotes, table cells, receipt spans, conflicting locations' },
    verdict: { type: 'string', enum: ['CONFIRMED', 'UNVERIFIABLE', 'FALSE_POSITIVE'], description: 'set by the red-team only' },
  },
}

const FINDER_OUTPUT = {
  type: 'object',
  required: ['aspect', 'sections_examined', 'findings'],
  properties: {
    aspect: { type: 'string' },
    sections_examined: { type: 'array', items: { type: 'string' } },
    findings: { type: 'array', items: FINDING },
    coverage_note: { type: 'string', description: 'confirm every section was read; name any not reached' },
  },
}

const REDTEAM_OUTPUT = {
  type: 'object',
  required: ['aspect', 'sections_examined', 'confirmed_findings', 'culled', 'coverage_complete'],
  properties: {
    aspect: { type: 'string' },
    sections_examined: { type: 'array', items: { type: 'string' } },
    confirmed_findings: { type: 'array', items: FINDING, description: 'survivors only, each with verdict=CONFIRMED or UNVERIFIABLE, deduped within the aspect' },
    culled: {
      type: 'array',
      items: {
        type: 'object', required: ['finding', 'why_killed'],
        properties: { finding: { type: 'string' }, why_killed: { type: 'string', description: 'precondition fails / quote not reproducible / duplicate / register-lock (deliberate hedging)' } },
      },
    },
    synthesis_note: { type: 'string' },
    coverage_complete: { type: 'boolean', description: 'true iff every draft section was examined for this aspect' },
  },
}

const LEDGER = {
  type: 'object',
  required: ['by_severity', 'coverage_matrix', 'totals'],
  properties: {
    by_severity: {
      type: 'object',
      properties: {
        CRITICAL: { type: 'array', items: FINDING },
        MAJOR: { type: 'array', items: FINDING },
        MINOR: { type: 'array', items: FINDING },
        NIT: { type: 'array', items: FINDING },
      },
    },
    dedup_note: { type: 'string', description: 'cross-aspect duplicates collapsed (same quote/location) -> one entry under its primary aspect' },
    coverage_matrix: {
      type: 'array',
      items: {
        type: 'object', required: ['aspect', 'coverage_complete'],
        properties: { aspect: { type: 'string' }, sections_covered: { type: 'array', items: { type: 'string' } }, coverage_complete: { type: 'boolean' } },
      },
    },
    totals: { type: 'string', description: 'count by severity, e.g. "2 CRITICAL, 6 MAJOR, 9 MINOR, 4 NIT"' },
  },
}

// ---------------------------------------------------------------------------
// ASPECTS -- five exclusive lanes (sharp boundaries so two teams never report
// the same issue; cross-aspect dups are collapsed in the final synth).
// ---------------------------------------------------------------------------
const ASPECTS = [
  {
    key: 'cohesion', phase: 'Cohesion',
    rubric: `ASPECT = COHESION (local textual flow ONLY).
Check: transitions between sentences and paragraphs; referring expressions ("this", "that", "the latter") resolve cleanly; ONE construct = ONE term everywhere (no nickname drift, e.g. residual vs UncResCEO vs the Q&A residual); no abrupt topic jumps; paragraph-to-paragraph linkage reads as one author.
NOT yours: whether the argument is valid (logic), whether sections agree (coherence), whether a claim is attackable (weaknesses), whether a cite is accurate (citation).`,
  },
  {
    key: 'coherence', phase: 'Coherence',
    rubric: `ASPECT = COHERENCE (global argument unity + cross-section consistency).
Check: one continuous thread from intro to conclusion; each section follows from the last; the ABSTRACT, INTRODUCTION, BODY, and CONCLUSION agree and the claim STRENGTH is monotone non-increasing toward the front matter (the abstract must not claim more than the body proves); the CONTRIBUTION is stated clearly and consistently across abstract/intro/conclusion ("what is new, why care"); no section contradicts another; no result described two incompatible ways.
NOT yours: local wording (cohesion), internal inference validity (logic), referee attacks (weaknesses), cite accuracy (citation).`,
  },
  {
    key: 'logic', phase: 'Logic',
    rubric: `ASPECT = LOGIC & OVER-CLAIM (internal validity of the written argument).
Check: does each conclusion VALIDLY follow from the evidence the draft itself states? Flag causal language on correlational evidence, a null treated as equivalence, Gelman-Stern significant-vs-insignificant contrasts, hidden assumptions, non-sequiturs, and any wording ABOVE the claim ceiling in claim_findings_ledger.json.
ALSO (number-trace, Section 4.2 only): every number in the Section 4.2 prose must equal its cell in tab:h14c_ceo2_decomp (these numbers postdate the earlier number gate). Flag any mismatch CRITICAL.
NOT yours: what is MISSING / attackable from outside (weaknesses), flow (cohesion), cross-section agreement (coherence).`,
  },
  {
    key: 'weaknesses', phase: 'Weaknesses',
    rubric: `ASPECT = ARGUMENT WEAKNESSES (hostile-referee attacks, from the TEXT only).
Adopt a hostile but fair referee. What would you attack even if the draft is internally consistent? Identification gaps and untested alternative explanations; power / equivalence (is a null underpowered?); generalizability (sample, period, ex-financial/utility); robustness holes; a measure that may not capture what it claims. For each, say whether the draft already DISCLOSES/defends it (then it is at most MINOR) or not (MAJOR).
A referee never sees your code -- judge from the prose, not from pipeline internals.
NOT yours: internal inference validity (logic), flow (cohesion), agreement (coherence), cite accuracy (citation).`,
  },
  {
    key: 'citation', phase: 'Citation',
    rubric: `ASPECT = CITATION ACCURACY (every \\citet/\\citep claim vs what the paper actually says).
Ground truth = our SAVED NLM RECEIPTS (verbatim cited_text spans). Read:
  ${R}/tmp/nlm_*.json
  ${R}/docs/Thesis/_archive/audit_20260612/p3_citation_ledger.json
  ${R}/docs/Thesis/rewrite/section2.1_paragraph_ledger.json + section2.3_paragraph_ledger.json (anchors_verified / verification blocks hold receipts for dye, bertrand_schoar, etc.)
For EACH in-text claim attributed to a cited paper: find the receipt span; verdict SUPPORTED / OVERCLAIM / UNSUPPORTED.
If NO receipt exists for that paper (known gaps: matsumoto2011, keown1981, verrecchia1983; legal: basic1988, rule10b5) -> verdict UNVERIFIABLE, severity MINOR, recommendation "fresh NLM capture needed" -- do NOT guess, do NOT call NLM (you have no auth and the guide forbids parallel NLM).
Only the structured cited_text span is admissible evidence; never the receipt's answer-prose.
NOT yours: anything that is not a citation attribution.`,
  },
]

// ---------------------------------------------------------------------------
// ORCHESTRATION: 5 teams run concurrently; each team = 3 finders (parallel)
// then 1 culling red-team. Then a final cross-aspect dedup+rank synth.
// ---------------------------------------------------------------------------
function finderPrompt(a, i) {
  return `You are independent referee #${i} auditing ONE aspect of a finance PhD thesis draft. Work alone; assume no other referee's output. Be hard-nosed and specific.\n\n${MANIFEST}\n\n${GLOBAL_RULES}\n\n${a.rubric}\n\nRead every draft section yourself, then return FINDER_OUTPUT: your findings (each evidence-bound, with a verbatim draft_quote and location), the sections you examined, and a coverage note. READ-ONLY -- edit nothing.`
}

function redteamPrompt(a, finders) {
  return `You are the adversarial RED-TEAM for the ${a.key} aspect. Three independent finders audited it. Your PRIMARY job is to CULL, not to merge.\n\n${MANIFEST}\n\n${GLOBAL_RULES}\n\n${a.rubric}\n\nFor every finding the finders raised: (1) reproduce its draft_quote verbatim in the draft -- if you cannot, KILL it; (2) test its precondition before its mechanism (E1) -- if the trigger does not hold, KILL it; (3) check it is not the draft's deliberate, correct hedging (register locks) -- if it is, KILL it; (4) dedup. Keep ONLY survivors, each with verdict CONFIRMED (or UNVERIFIABLE for citations with no receipt). Record what you killed and why. Assert whether coverage is complete.\n\nThe three finder reports:\n${JSON.stringify(finders)}\n\nReturn REDTEAM_OUTPUT.`
}

const teamReports = await parallel(ASPECTS.map(a => async () => {
  const finders = (await parallel([1, 2, 3].map(i => () =>
    agent(finderPrompt(a, i), { label: `${a.key}-finder-${i}`, phase: a.phase, schema: FINDER_OUTPUT })
  ))).filter(Boolean)
  log(`${a.key}: ${finders.length}/3 finders returned`)
  if (!finders.length) return null
  return agent(redteamPrompt(a, finders), { label: `${a.key}-redteam`, phase: a.phase, schema: REDTEAM_OUTPUT })
}))

const reports = teamReports.filter(Boolean)
log(`${reports.length}/${ASPECTS.length} aspect teams completed`)

phase('Synthesize')
const SYNTH_PROMPT = `You are the chief editor assembling ONE referee ledger from five aspect red-team reports (cohesion, coherence, logic, weaknesses, citation).\n\nDedup ACROSS aspects: if the same draft_quote+location was flagged by more than one aspect, keep ONE entry under its most-fitting aspect and note the merge. Then sort every surviving finding into by_severity (CRITICAL, MAJOR, MINOR, NIT). Build the coverage_matrix (per aspect: sections covered + coverage_complete). Give totals. Change nothing else; invent no new findings.\n\nThe five red-team reports:\n${JSON.stringify(reports)}\n\nReturn LEDGER.`
const ledger = await agent(SYNTH_PROMPT, { label: 'final-synth', phase: 'Synthesize', schema: LEDGER })

return { teamReports: reports, ledger }
