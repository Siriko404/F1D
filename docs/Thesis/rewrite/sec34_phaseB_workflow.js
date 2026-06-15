export const meta = {
  name: 'sec34-phaseB-paragraph-allocation',
  description: 'Phase B: allocate each RATIFIED Sec 3/4 subsection chain into paragraphs (atomic purpose + per-paragraph proposition chain) (3 identical opus planners + 1 opus red-team synthesis); reason+evidence atomic on every item',
  phases: [
    { title: 'Plan', detail: '3 independent opus planners read the ratified Phase-A plans + manifest, allocate each chain into paragraphs for all 5 subsections' },
    { title: 'Redteam', detail: '1 opus reads the same inputs, scrutinizes all 3 allocations, synthesizes the single best paragraph plan + allocation matrix' },
  ],
}

const R = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D'

const MANIFEST = `READING MANIFEST -- read every unit yourself, in full, before allocating (absolute paths):

UNIT 0 -- THE PRIMARY INPUT (this is what you ALLOCATE; the chains here are RATIFIED and LOCKED):
  ${R}/docs/Thesis/rewrite/section3.1_subsection_plan.json
  ${R}/docs/Thesis/rewrite/section3.2_subsection_plan.json
  ${R}/docs/Thesis/rewrite/section3.3_subsection_plan.json
  ${R}/docs/Thesis/rewrite/section3.4_subsection_plan.json
  ${R}/docs/Thesis/rewrite/section4.1_subsection_plan.json
  Each holds the ratified subsection PURPOSE + an ordered proposition_chain (props with id, statement, role, type, reason, evidence, numbers, register_locks, depends_on) + coverage + open_decisions. EVERY proposition in these chains must land in EXACTLY ONE paragraph (you may SPLIT one prop across two paragraphs or MERGE two short props into one, but only with an explicit reason+evidence; nothing may be dropped or silently duplicated). You do NOT re-plan, re-claim, re-number, or re-justify the chain -- it is locked. Also read ${R}/docs/Thesis/rewrite/section34_phaseA_redteam.json (the coverage_matrix + why each claim is homed) for cross-subsection context.

UNIT T -- THE FORMAT TEMPLATE you mirror:
  ${R}/docs/Thesis/rewrite/section2.2_paragraph_ledger.json -- the EXACT paragraph-ledger shape: paragraphs keyed in order, each with intent / serves / boundary / thin_claim / guardrails[] / lit_body / propositions[] (each prop has role_in_paragraph + type + reason + evidence) / prose_gate / final_prose / prose_status. Your output mirrors this shape EXACTLY, with two differences: (a) final_prose stays EMPTY and prose_status = BLOCKED (this is PLANNING, not prose), and (b) every paragraph intent AND every proposition additionally carries reason + evidence atomically (the hard requirement).

UNITS 1-8 -- the grounding sources (same as Phase A; read them to keep allocation faithful):
1. ${R}/docs/Thesis/thesis_draft.tex -- LOCKED Section 2 prose (2.1 framework, 2.2 H1/H1a/H1b, 2.3 UncResCEO/eq-4, 2.4 the three estimating equations, 2.5 convergent validity + the scrutiny promise) + bibliography. Section 3/4 paragraphs deliver what Section 2 set up; the 2.2-P5 + 2.5-P4 scrutiny promise is paid off in 4.1. PROSE STYLE for any later prose: NO em-dash/en-dash; results read correlationally.
2. ${R}/docs/Thesis/_tables_from_bible.tex -- the 11 result tables byte-exact. Confirm every number you place is the right table cell.
3. ${R}/docs/Thesis/rewrite/claim_findings_ledger.json -- claims C1-C7 -> thinnest claim + register locks + C-traps + RERUN risks. CONTAINS _open_decisions_resolved_2026_06_14 (READ IT): SD-basis is RESOLVED -> 0.3010 (all-universe Table-1 Panel B); the 0.3072 alternative is RETIRED; apply 0.3010 in any economic-magnitude number and do NOT re-surface the SD decision. Orphan bibitems already dropped; Appendix I already titled; C6 two-way-clustering rerun already done (table stays firm-clustered).
4. ${R}/docs/Thesis/rewrite/section2.1_paragraph_ledger.json .. section2.5_paragraph_ledger.json (5) -- read the PLANNING SUBSTANCE for how paragraphs are structured (intent/serves/boundary/thin_claim/guardrails/propositions); SKIP the verbatim NLM receipt blocks (verification.{answer,quotes,located,span_pin}). 2.2 is the format template.
5. ${R}/docs/Thesis/rewrite/section2_roadmap.md -- Section 2 backbone + coherence flags + forward-refs into 3/4.
6. ${R}/docs/Thesis/variable_ledger.json -- variable -> definition -> construction file:line (ignore DROPPED entries).
7. ${R}/docs/Thesis/DraftTemplate.txt (binding section structure) AND ${R}/tmp/old_draft_81efc78.tex (lines ~97-176) -- the COMPLETE prior Section 3/4 prose: use it as a REFERENCE for natural PARAGRAPH BREAKS only (where the prior draft broke paragraphs). It is NOT ratified; the ratified chains (Unit 0) + the claim ceiling OVERRIDE it; it carries stale SDs and the dropped 4.2.
8. ${R}/docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md (E1-E7) + ${R}/docs/Thesis/_archive/audit_20260612/PROPOSITION_RULES.md + ${R}/docs/Thesis/rewrite/paragraph_workflow.json -- discipline + taxonomy + the verify-then-write pipeline these ledgers feed.`

const SCOPE = `SCOPE -- exactly the 5 ratified subsections (allocate each one's locked chain into paragraphs):
- 3.1 Data, Sample, and Variable Construction (6 ratified props; no headline claim) -> tab:summary_stats.
- 3.2 Main Analysis 1: The Pre-Announcement Run-Up (5 ratified props; claim C2/H1) -> tab:empire_building_did.
- 3.3 Main Analysis 2: Differential Timing (6 ratified props; claim C1/H1b, STRONGEST) -> tab:empire_drop_matched + placebo (cash col).
- 3.4 Main Analysis 3: Cash-Specificity (5 ratified props; claim C6/H1a) -> tab:empire_cashspec + placebo (stock col).
- 4.1 Ruling Out Analyst Scrutiny (5 ratified props; claim C4) -> reason_gating + cash_scrutiny_validity + cash_scrutiny_channel + empire_building_did col 4.`

const RULES = `HARD RULES:
- ALLOCATION, NOT RE-PLANNING: the Phase-A chains (Unit 0) are RATIFIED. Your job is to allocate their propositions into PARAGRAPHS, give each paragraph an ATOMIC purpose, and order the propositions within each paragraph. Do NOT add new claims, re-number Phase-A props, change any number, drop a register lock, or re-open a settled decision.
- EVERY Phase-A proposition is HOMED in exactly one paragraph. A prop may be SPLIT across two paragraphs or two short props MERGED into one, ONLY with an explicit reason+evidence. In allocation_coverage list every Phase-A prop -> its paragraph; the red-team will reject any orphaned or duplicated prop.
- ATOMIC PARAGRAPHS: each paragraph does ONE job (one intent). No paragraph spans two unrelated purposes; no two paragraphs share the same job. Argue the paragraph COUNT in paragraph_count_rationale (reason+evidence); do NOT pad. A results subsection typically runs 3-5 paragraphs; 3.1 may run a little longer (data/sample/variables/Table 1).
- ORDER + TRANSITIONS: paragraphs follow the chain's logic (design/premise -> result -> inference -> caveat). Where a paragraph opens or closes a move, mark it (a transition prop is allowed, typed framing, with reason+evidence).
- PRESERVE EVERYTHING: every number stays tied to its named table cell (e.g. "0.0473*** (tab:empire_drop_matched col 1)"); SD-magnitude numbers use 0.3010 (resolved); every register lock that bound a Phase-A prop binds the paragraph it lands in. C-traps stay honored at paragraph level (C6 formal Wald not Gelman-Stern; C4 NULL-only not strengthened; C1 POST not over-read). E1: no Pagan re-insert.
- BOUNDARY: 3.1 gives construction mechanics + sample and POINTS BACK to 2.3/2.5/Appendix; no subsection re-enters Section 2 turf or another subsection's lane. The 2.5-P4 scrutiny verdict is owned by 4.1.
- FORMAT: mirror section2.2_paragraph_ledger.json exactly (intent/serves/boundary/thin_claim/guardrails/lit_body/propositions[role_in_paragraph,type,reason,evidence,...]/prose_gate/final_prose/prose_status). final_prose = "" ; prose_status = "BLOCKED -- planning only". lit_body is usually "none new" for results paragraphs.
- REASON + EVIDENCE ATOMIC (MOST IMPORTANT): every paragraph intent AND every proposition carries reason (WHY this paragraph / why this prop here, in this order) and evidence (an array of pointers: the Phase-A prop_id it derives from, a table cell, a claim_findings C-id, a Section-2 ledger ref, the 2.2 template, or the old-draft paragraph break). No intent or proposition without both.`

const TASK = `TASK: For EACH of the 5 subsections, take its RATIFIED proposition chain (Unit 0) and design the PARAGRAPH ALLOCATION: (1) decide how many paragraphs and why (paragraph_count_rationale with reason+evidence); (2) for each paragraph give an ATOMIC intent {statement, reason, evidence}, its serves / boundary / thin_claim / guardrails / lit_body; (3) place the Phase-A propositions into that paragraph as an ordered proposition_chain, each paragraph-proposition carrying from_phaseA_prop, role_in_paragraph, type, reason, evidence, numbers (table-sourced), register_locks, depends_on; (4) in allocation_coverage, map every Phase-A prop to exactly one paragraph and argue no prop is orphaned or duplicated. Leave final_prose EMPTY and prose_status BLOCKED. Return the PARAGRAPH_PLAN_SET structured object.`

const PARA_PROP = {
  type: 'object',
  required: ['prop_id', 'from_phaseA_prop', 'statement', 'role_in_paragraph', 'type', 'reason', 'evidence'],
  properties: {
    prop_id: { type: 'string', description: 'paragraph-local id, e.g. 3.2-P2-a' },
    from_phaseA_prop: { type: 'string', description: 'the ratified Phase-A prop_id it derives from (e.g. 3.2-P2), or "new-transition"' },
    statement: { type: 'string' },
    role_in_paragraph: { type: 'string', description: 'premise | result | inference | caveat | transition | definition + a short note on its role in THIS paragraph' },
    type: { type: 'string', enum: ['result-number', 'design-method', 'definitional', 'framing', 'external-NLM', 'callback-verified'] },
    reason: { type: 'string', description: 'WHY this prop is in this paragraph, in this order' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'pointers: Phase-A prop_id, table cell, claim C-id, Section-2 ledger ref, template, old-draft break' },
    numbers: { type: 'array', items: { type: 'string' }, description: 'each number token WITH its table source; SD-magnitudes use 0.3010' },
    register_locks: { type: 'array', items: { type: 'string' } },
    depends_on: { type: 'array', items: { type: 'string' } },
  },
}

const RE = { type: 'object', required: ['statement', 'reason', 'evidence'],
  properties: { statement: { type: 'string' }, reason: { type: 'string' }, evidence: { type: 'array', items: { type: 'string' } } } }

const PARAGRAPH = {
  type: 'object',
  required: ['para_id', 'order', 'intent', 'serves', 'boundary', 'proposition_chain'],
  properties: {
    para_id: { type: 'string', description: 'e.g. 3.2-P1' },
    order: { type: 'number' },
    intent: RE,
    serves: { type: 'array', items: { type: 'string' } },
    boundary: { type: 'string' },
    thin_claim: { type: 'string' },
    guardrails: { type: 'array', items: { type: 'string' } },
    lit_body: { type: 'string' },
    proposition_chain: { type: 'array', items: PARA_PROP },
    prose_gate: { type: 'object', properties: { rule: { type: 'string' }, all_supported: { type: 'boolean' }, unlocked: { type: 'boolean' } } },
    final_prose: { type: 'string', description: 'MUST be empty string at this stage' },
    prose_status: { type: 'string', description: 'MUST be "BLOCKED -- planning only"' },
  },
}

const SUBSECTION = {
  type: 'object',
  required: ['subsection_id', 'title', 'paragraphs', 'allocation_coverage'],
  properties: {
    subsection_id: { type: 'string' },
    title: { type: 'string' },
    paragraph_count_rationale: RE,
    paragraphs: { type: 'array', items: PARAGRAPH },
    allocation_coverage: {
      type: 'object',
      required: ['all_phaseA_props_homed', 'prop_to_paragraph'],
      properties: {
        all_phaseA_props_homed: { type: 'string', description: 'argue no Phase-A prop orphaned or duplicated' },
        prop_to_paragraph: { type: 'array', items: { type: 'object', required: ['phaseA_prop', 'paragraph'],
          properties: { phaseA_prop: { type: 'string' }, paragraph: { type: 'string' }, note: { type: 'string' } } } },
        gaps: { type: 'array', items: { type: 'string' } },
      },
    },
    open_items: { type: 'array', items: { type: 'string' } },
  },
}

const PARAGRAPH_PLAN_SET = {
  type: 'object',
  required: ['subsections'],
  properties: {
    subsections: { type: 'array', items: SUBSECTION },
    global_notes: { type: 'array', items: { type: 'string' } },
  },
}

const REDTEAM_OUTPUT = {
  type: 'object',
  required: ['subsections', 'redteam_report', 'allocation_matrix'],
  properties: {
    subsections: { type: 'array', items: SUBSECTION },
    redteam_report: {
      type: 'array',
      items: {
        type: 'object',
        required: ['subsection_id', 'flaws_found', 'synthesis_decisions'],
        properties: {
          subsection_id: { type: 'string' },
          planners_compared: { type: 'array', items: { type: 'string' } },
          flaws_found: { type: 'array', items: {
            type: 'object', required: ['flaw', 'severity', 'reason', 'evidence'],
            properties: { flaw: { type: 'string' }, severity: { type: 'string', enum: ['CRITICAL', 'MAJOR', 'MINOR'] }, which_planner: { type: 'string' }, reason: { type: 'string' }, evidence: { type: 'array', items: { type: 'string' } } },
          } },
          synthesis_decisions: { type: 'array', items: {
            type: 'object', required: ['decision', 'reason', 'evidence'],
            properties: { decision: { type: 'string' }, reason: { type: 'string' }, evidence: { type: 'array', items: { type: 'string' } } },
          } },
        },
      },
    },
    allocation_matrix: {
      type: 'array',
      items: { type: 'object', required: ['subsection_id', 'phaseA_prop', 'paragraph', 'status'],
        properties: { subsection_id: { type: 'string' }, phaseA_prop: { type: 'string' }, paragraph: { type: 'string' }, status: { type: 'string' } } },
    },
  },
}

const RUBRIC = `RED-TEAM RUBRIC -- apply to all 3 paragraph allocations against the ratified chains + the manifest; be adversarial, default to flagging:
1. Allocation completeness: every Phase-A proposition lands in EXACTLY one paragraph; flag any orphaned, dropped, or duplicated prop (build the allocation_matrix to prove it). A split/merge is allowed ONLY with a stated reason+evidence.
2. No re-planning: the chain's claims, numbers, and register locks are UNCHANGED; flag any new claim, altered number, re-numbered/renamed Phase-A prop, or dropped lock.
3. Paragraph atomicity: each paragraph has ONE intent; flag a paragraph doing two unrelated jobs, or two paragraphs sharing one job.
4. Number traceability: every number still traces to its named table cell; SD-magnitudes use 0.3010 (resolved); flag any memory number, wrong cell, or re-surfaced 0.3072.
5. C-traps preserved at paragraph level: C6 formal Wald not Gelman-Stern; C4 NULL-only not strengthened; C1 POST not over-read; E1 no Pagan re-insert.
6. Boundary: 3.1 construction+sample only (defs point back to 2.3/2.5/Appendix); no Section-2 turf or cross-subsection bleed; 2.5-P4 scrutiny verdict owned by 4.1.
7. Order + transitions: paragraph order follows premise->result->inference->caveat; flag a result before its design premise, or a missing hand-off (e.g. 3.2->3.4 deferral of the formal cash-vs-stock test).
8. Paragraph count justified: flag padding (a paragraph that should merge) or cramming (a paragraph that should split).
9. Format fidelity: mirrors section2.2_paragraph_ledger.json; final_prose EMPTY; prose_status BLOCKED; intent + every prop carry reason+evidence (flag any missing or unsound reason/evidence).
10. Coverage handoff: every subsection's allocation_coverage maps all props; open_items surfaced (e.g. Appendix-I content edits still pending for 3.1/4.1).
SYNTHESIZE: produce the single BEST paragraph allocation per subsection (best atomicity, order, and faithful homing across the 3 plans; fix every flaw). Record reason+evidence on every synthesized paragraph intent + proposition; record flaws_found (with which_planner + reason + evidence), synthesis_decisions, and the allocation_matrix (every Phase-A prop -> paragraph -> status). Return REDTEAM_OUTPUT.`

phase('Plan')
const PLANNER_PROMPT = `You are an independent, hard-nosed empirical-finance paragraph architect. Allocate from scratch; do not assume any other planner's work. You ALLOCATE a ratified chain into paragraphs; you do NOT re-plan it.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${TASK}`
const planners = (await parallel([1, 2, 3].map(i => () =>
  agent(PLANNER_PROMPT, { label: `para-planner-${i}`, phase: 'Plan', schema: PARAGRAPH_PLAN_SET, model: 'opus' })
))).filter(Boolean)
log(`${planners.length}/3 paragraph planners returned`)

phase('Redteam')
const REDTEAM_PROMPT = `You are an adversarial red-team referee for paragraph allocation. You have the same manifest + ratified chains the planners used; read them yourself to judge the allocations against the locked chains.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${RUBRIC}\n\nHere are the ${planners.length} independent paragraph allocations to scrutinize and synthesize:\n${JSON.stringify(planners)}`
const synthesis = await agent(REDTEAM_PROMPT, { label: 'redteam-synth-B', phase: 'Redteam', schema: REDTEAM_OUTPUT, model: 'opus' })

return { planners, synthesis }
