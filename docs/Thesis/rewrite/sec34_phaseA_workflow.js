export const meta = {
  name: 'sec34-phaseA-subsection-chains',
  description: 'Phase A: per-subsection purpose + proposition chain for Sec 3/4 (3 identical opus planners + 1 opus red-team synthesis); reason+evidence atomic on every item',
  phases: [
    { title: 'Plan', detail: '3 independent opus planners read the full manifest, plan purpose + proposition chain for all 5 subsections' },
    { title: 'Redteam', detail: '1 opus reads the same manifest, scrutinizes all 3 plans, synthesizes the single best plan + coverage matrix' },
  ],
}

const R = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D'

const MANIFEST = `READING MANIFEST -- read every unit yourself, in full, before planning (absolute paths):
1. ${R}/docs/Thesis/thesis_draft.tex -- the LOCKED Section 2 prose (2.1 framework, 2.2 H1/H1a/H1b, 2.3 UncResCEO/DWZ eq-4, 2.4 the three estimating equations, 2.5 convergent validity + scrutiny construct) + the 20-entry bibliography. Section 3/4 must DELIVER what Section 2 set up.
2. ${R}/docs/Thesis/_tables_from_bible.tex -- the 11 result tables, byte-exact (coefficients, SEs, N, notes). THE source for every number.
3. ${R}/docs/Thesis/rewrite/claim_findings_ledger.json -- claims C1-C7 -> finding -> thinnest referee-proof version + register locks + RERUN risks + the _sd_basis_note_2026_06_14. THE claim ceiling.
4. ${R}/docs/Thesis/rewrite/section2.1_paragraph_ledger.json , section2.2_..., section2.3_..., section2.4_..., section2.5_paragraph_ledger.json (5 files) -- per-subsection purpose, typed propositions (verdicts SUPPORTED), guardrails, forward-refs (e.g. 2.5-P4 -> 4.1). These are large ONLY because of verbatim NLM receipt blocks: read the PLANNING SUBSTANCE (_plan, each paragraph intent/serves/boundary/thin_claim/guardrails, propositions[].{statement,type,verification.verdict}, final_prose, next_action) and SKIP verification.{answer,quotes,located,span_pin}.
5. ${R}/docs/Thesis/rewrite/section2_roadmap.md -- Section 2 backbone + cross-cutting coherence flags.
6. ${R}/docs/Thesis/variable_ledger.json -- every variable -> definition -> construction code (file:line). Refreshed: summary-stats numbers now point to the table; 12 variables and 3 tables are marked DROPPED -- ignore the DROPPED ones.
7. ${R}/docs/Thesis/DraftTemplate.txt -- the binding section structure. AND ${R}/tmp/old_draft_81efc78.tex (lines ~97 to ~176) -- the COMPLETE prior Section 3/4 prose: a structural + numerical REFERENCE you re-plan to the thin-claim ceiling. NOT ratified; the claim ceiling OVERRIDES it; it still carries STALE SDs and the now-DROPPED Section 4.2.
8. ${R}/docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md (lessons E1-E7) + ${R}/docs/Thesis/_archive/audit_20260612/PROPOSITION_RULES.md + ${R}/docs/Thesis/rewrite/paragraph_workflow.json -- the verification discipline, the proposition taxonomy, and the downstream verify-then-write pipeline.`

const SCOPE = `SCOPE -- exactly 5 subsections (Section 4.2 / C7 presentation-contrast is DROPPED; convergent validity h11/h24/h24b belongs to Section 2.5, NOT here):
- 3.1 Data, Sample, and Variable Construction -> Table 1 (summary_stats); 4 data sources; the build; key variable defs POINTING BACK to 2.3/2.5/Appendix (do not re-derive); 3-layer sample.
- 3.2 Main Analysis 1: The Pre-Announcement Run-Up -> claim C2, table tab:empire_building_did; pays off H1 + the 2.4 MA1 design.
- 3.3 Main Analysis 2: Differential Timing Around the Announcement -> claim C1 (strongest), tables tab:empire_drop_matched + tab:empire_drop_placebo; pays off H1b + the 2.4 MA2 event study.
- 3.4 Main Analysis 3: Cash-Specificity -> claim C6, tables tab:empire_cashspec + tab:empire_drop_placebo; pays off H1a + the 2.4 MA3 pooled-interacted design.
- 4.1 Ruling Out Analyst Scrutiny -> claim C4, tables tab:reason_gating + tab:cash_scrutiny_validity + tab:cash_scrutiny_channel; pays off the 2.2-P5 + 2.5-P4 promise ("tested in Section 4.1").`

const RULES = `HARD RULES:
- This is RE-PLAN to the thin-claim ceiling of an existing coherent draft, NOT invent-from-scratch.
- PLAN-ONLY: design the proposition chain. Do NOT write prose, do NOT run NLM or number verification. Tag each proposition by type + what later-stage verification it will need.
- NUMBERS: every number comes from a named table cell (claim_findings_ledger / _tables_from_bible). NEVER from memory. In each proposition "numbers" array, write each number token WITH its table source, e.g. "0.0461*** (tab:empire_building_did col 2)".
- REGISTER LOCKS bind every proposition (from claim_findings): correlational / no-identification / concentration-not-strict-specificity / mechanism-open / supportive-not-definitive.
- C-TRAPS: C6 -> keep the FORMAL Wald cash-minus-stock test (0.0983**); do NOT use a Gelman-Stern "significant-for-cash vs n.s.-for-stock" comparison. C4 -> NULL-only, underpowered; keep "does not account for THIS run-up, not that scrutiny never matters"; do NOT strengthen. C1 -> do NOT over-read the negative POST (-0.0250*).
- E1 LESSON: the generated-regressand / Pagan two-step-SE critique was WITHDRAWN (UncResCEO is an operationally-defined measure, not a latent proxy). Do NOT insert a Pagan disclaimer as a Section 3 defect; Section 2.3 already states the honest flag once.
- BOUNDARY: variable DEFINITIONS live in 2.3/2.5/Appendix; 3.1 gives construction MECHANICS + sample and POINTS BACK. Do not reach into Section 2 turf or another subsection.
- SURFACE (do not solve) the known open decisions: 3.2 SD-basis (estimation-sample 0.3072 vs all-universe Table-1 0.3010, see _sd_basis_note); orphan bibitems after the 4.2 drop (lerman2026, bushee2018, everhart2025, gokkaya2025 -> cite-or-remove); Appendix I pending edits.
- REASON + EVIDENCE ATOMIC (MOST IMPORTANT): every purpose AND every proposition carries "reason" (WHY it exists / why in the chain) and "evidence" (an array of manifest pointers it is BASED ON: a table cell, a claim_findings C-id, a Section-2 ledger ref, variable_ledger, the template, or the old-draft prose). No purpose or proposition without both.`

const TASK = `TASK: For EACH of the 5 subsections: (1) identify its PURPOSE -- what it must deliver 100% -- with reason + evidence; and (2) design the PROPOSITION CHAIN that delivers that purpose completely. A proposition chain is an ordered set of atomic propositions (premise -> result -> inference -> caveat), each typed, each with reason + evidence + table-sourced numbers + the register locks it must honor + depends_on. Do NOT allocate paragraphs (a later phase). Make the chain COMPLETE: in coverage.purpose_fully_delivered, argue the chain delivers the purpose with no gap. Return the SUBSECTION_PLAN_SET structured object.`

const PROP = {
  type: 'object',
  required: ['prop_id','statement','role','type','reason','evidence'],
  properties: {
    prop_id: { type: 'string' },
    statement: { type: 'string' },
    role: { type: 'string', description: 'premise | result | inference | caveat | definition | transition' },
    type: { type: 'string', enum: ['result-number','design-method','definitional','framing','external-NLM','callback-verified'] },
    reason: { type: 'string', description: 'WHY this proposition is in the chain / what gap in the purpose it fills' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'manifest pointers this is BASED ON' },
    numbers: { type: 'array', items: { type: 'string' }, description: 'each number token WITH its table source' },
    register_locks: { type: 'array', items: { type: 'string' } },
    depends_on: { type: 'array', items: { type: 'string' } },
  },
}

const SUBSECTION = {
  type: 'object',
  required: ['subsection_id','title','purpose','delivers_claims','tables_referenced','proposition_chain','coverage'],
  properties: {
    subsection_id: { type: 'string' },
    title: { type: 'string' },
    purpose: {
      type: 'object',
      required: ['statement','reason','evidence'],
      properties: { statement: { type: 'string' }, reason: { type: 'string' }, evidence: { type: 'array', items: { type: 'string' } } },
    },
    delivers_claims: { type: 'array', items: { type: 'string' } },
    tables_referenced: { type: 'array', items: { type: 'string' } },
    hypotheses_paid_off: { type: 'array', items: { type: 'string' } },
    pays_off_section2: { type: 'array', items: { type: 'string' } },
    proposition_chain: { type: 'array', items: PROP },
    coverage: {
      type: 'object',
      required: ['purpose_fully_delivered'],
      properties: { purpose_fully_delivered: { type: 'string' }, gaps: { type: 'array', items: { type: 'string' } } },
    },
    open_decisions: { type: 'array', items: { type: 'string' } },
  },
}

const SUBSECTION_PLAN_SET = {
  type: 'object',
  required: ['subsections'],
  properties: {
    subsections: { type: 'array', items: SUBSECTION },
    global_notes: { type: 'array', items: { type: 'string' } },
  },
}

const REDTEAM_OUTPUT = {
  type: 'object',
  required: ['subsections','redteam_report','coverage_matrix'],
  properties: {
    subsections: { type: 'array', items: SUBSECTION },
    redteam_report: {
      type: 'array',
      items: {
        type: 'object',
        required: ['subsection_id','flaws_found','synthesis_decisions'],
        properties: {
          subsection_id: { type: 'string' },
          planners_compared: { type: 'array', items: { type: 'string' } },
          flaws_found: { type: 'array', items: {
            type: 'object', required: ['flaw','severity','reason','evidence'],
            properties: { flaw: { type: 'string' }, severity: { type: 'string', enum: ['CRITICAL','MAJOR','MINOR'] }, which_planner: { type: 'string' }, reason: { type: 'string' }, evidence: { type: 'array', items: { type: 'string' } } },
          } },
          synthesis_decisions: { type: 'array', items: {
            type: 'object', required: ['decision','reason','evidence'],
            properties: { decision: { type: 'string' }, reason: { type: 'string' }, evidence: { type: 'array', items: { type: 'string' } } },
          } },
        },
      },
    },
    coverage_matrix: {
      type: 'array',
      items: { type: 'object', required: ['claim','subsection','tables','status'],
        properties: { claim: { type: 'string' }, subsection: { type: 'string' }, tables: { type: 'array', items: { type: 'string' } }, status: { type: 'string' } } },
    },
  },
}

const RUBRIC = `RED-TEAM RUBRIC -- apply to all 3 plans against the manifest; be adversarial, default to flagging:
1. Thin-claim ceiling: any proposition claiming more than its finding supports (vs claim_findings) -> flaw.
2. Register locks intact (correlational / no-identification / concentration-not-specificity / mechanism-open / supportive-not-definitive).
3. Number traceability: every number traces to a named table cell; NO memory numbers; flag any untraceable or wrong-table number.
4. C-traps: C6 no Gelman-Stern (formal Wald only); C4 not strengthened; C1 POST not over-read.
5. Boundary: each subsection stays in its lane; definitions not re-derived (belong to 2.3/2.5/Appendix); 3.1 = construction + sample only.
6. Coverage: every live claim (C1/C2/C4/C6) + every live table (empire_building_did, empire_drop_matched, empire_drop_placebo, empire_cashspec, reason_gating, cash_scrutiny_validity, cash_scrutiny_channel, summary_stats) has EXACTLY one home; every hypothesis (H1/H1a/H1b) paid off; the 2.5-P4 scrutiny promise delivered in 4.1.
7. E-lessons: E1 (no re-inserted Pagan disclaimer), E2 (method claims cite the executable line), register locks.
8. Purpose-completeness: does each chain deliver its purpose 100%? Flag gaps.
9. Reason + evidence present AND sound on every proposition.
10. Open decisions surfaced (SD-basis, orphan bibitems, Appendix I).
SYNTHESIZE: produce the single BEST proposition chain per subsection (take the best-covered, most-referee-proof version of each proposition across the 3 plans; fix every flaw). Record reason + evidence on every synthesized proposition; record flaws_found (with which_planner + reason + evidence), synthesis_decisions, and a coverage_matrix (claim -> subsection -> tables -> status). Return REDTEAM_OUTPUT.`

phase('Plan')
const PLANNER_PROMPT = `You are an independent, hard-nosed empirical-finance proposition planner. Plan from scratch; do not assume any other planner's work.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${TASK}`
const planners = (await parallel([1,2,3].map(i => () =>
  agent(PLANNER_PROMPT, { label: `planner-${i}`, phase: 'Plan', schema: SUBSECTION_PLAN_SET, model: 'opus' })
))).filter(Boolean)
log(`${planners.length}/3 planners returned`)

phase('Redteam')
const REDTEAM_PROMPT = `You are an adversarial red-team referee. You have the same manifest the planners used; read it yourself to judge their work against the sources.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${RUBRIC}\n\nHere are the ${planners.length} independent plans to scrutinize and synthesize:\n${JSON.stringify(planners)}`
const synthesis = await agent(REDTEAM_PROMPT, { label: 'redteam-synth', phase: 'Redteam', schema: REDTEAM_OUTPUT, model: 'opus' })

return { planners, synthesis }