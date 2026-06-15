export const meta = {
  name: 'introconcl-phaseB-paragraph-allocation',
  description: 'Phase B: allocate each RATIFIED unit chain (Abstract, Introduction, Conclusion) into paragraphs (atomic intent + per-paragraph proposition chain) (3 identical opus planners + 1 opus red-team synthesis); results QUALITATIVE; reason+evidence atomic on every item',
  phases: [
    { title: 'Plan', detail: '3 independent opus planners read the ratified Phase-A plans + manifest, allocate each chain into paragraphs for all 3 units' },
    { title: 'Redteam', detail: '1 opus reads the same inputs, scrutinizes all 3 allocations, synthesizes the single best paragraph plan + allocation matrix' },
  ],
}

const R = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D'

const MANIFEST = `READING MANIFEST -- read every unit yourself, in full, before allocating (absolute paths):

UNIT 0 -- THE PRIMARY INPUT (this is what you ALLOCATE; the chains here are RATIFIED and LOCKED):
  ${R}/docs/Thesis/rewrite/section_abstract_subsection_plan.json
  ${R}/docs/Thesis/rewrite/section1_subsection_plan.json
  ${R}/docs/Thesis/rewrite/section5_subsection_plan.json
  Each holds the ratified unit PURPOSE + an ordered proposition_chain (props with id, statement, role, type, reason, evidence, numbers, register_locks, depends_on) + coverage + open_decisions. EVERY proposition in these chains must land in EXACTLY ONE paragraph (you may SPLIT one prop across two paragraphs or MERGE two short props into one, but only with an explicit reason+evidence; nothing may be dropped or silently duplicated). You do NOT re-plan, re-claim, re-number, or re-justify the chain -- it is locked. Also read ${R}/docs/Thesis/rewrite/introconcl_phaseA_redteam.json (the coverage_matrix + why each claim is homed) for cross-unit context.

UNIT T -- THE FORMAT TEMPLATE you mirror:
  ${R}/docs/Thesis/rewrite/section2.2_paragraph_ledger.json -- the EXACT paragraph-ledger shape: paragraphs keyed in order, each with intent / serves / boundary / thin_claim / guardrails[] / lit_body / propositions[] (each prop has role_in_paragraph + type + reason + evidence) / prose_gate / final_prose / prose_status. Your output mirrors this shape EXACTLY, with two differences: (a) final_prose stays EMPTY and prose_status = BLOCKED (this is PLANNING, not prose), and (b) every paragraph intent AND every proposition additionally carries reason + evidence atomically (the hard requirement).

UNIT C -- THE BINDING CONVENTION:
  ${R}/docs/Thesis/DraftTemplate.txt -- the NLM-derived per-unit SECTION-WRITING CONVENTION (Abstract = 1 single paragraph, 5 elements; Introduction = 4 moves; Conclusion = 3 moves), with per-move depth + style. Your paragraph COUNT and ORDER must realize these moves: the ABSTRACT is exactly ONE paragraph; the INTRODUCTION runs roughly one paragraph per move (4-6 paragraphs: context/gap may take 1-2, the findings preview 1-2, the roadmap exactly 1); the CONCLUSION runs roughly 3 paragraphs (restate; summary; implications/limitations/future). Results stay QUALITATIVE: no coefficients land in any paragraph.

UNITS 1-7 -- the grounding sources (same as Phase A; read them to keep allocation faithful):
1. ${R}/docs/Thesis/rewrite/claim_findings_ledger.json -- claims C1-C7 -> thinnest claim + register locks + C-traps + _open_decisions_resolved_2026_06_14 (SD=0.3010). THE claim ceiling.
2. ${R}/docs/Thesis/rewrite/section2.1_paragraph_ledger.json .. section2.5_paragraph_ledger.json (5) AND section3.1_paragraph_ledger.json , 3.2, 3.3, 3.4, 4.1 (5) -- the FINAL, LOCKED body the intro previews and the conclusion summarizes. Read the planning substance + final_prose; SKIP the verbatim NLM receipt blocks. 2.2 is the format template.
3. ${R}/docs/Thesis/_tables_from_bible.tex -- the 11 result tables byte-exact. The SOURCE OF TRUTH for the SIGN + SIGNIFICANCE behind each directional claim (no number enters the prose; the table grounds the direction).
4. ${R}/docs/Thesis/variable_ledger.json -- variable -> definition -> construction file:line (ignore DROPPED entries); for naming the measure (UncResCEO) + the data sources.
5. ${R}/docs/Thesis/thesis_draft.tex -- read ONLY the bibliography (live \\bibitem list). The four dropped bibitems (everhart2025, gokkaya2025, bushee2018, lerman2026) are NOT live. PROSE STYLE for any later prose: NO em-dash/en-dash; results read correlationally and qualitatively.
6. ${R}/tmp/nlm_*.json + ${R}/docs/Thesis/rewrite/NLM_QUERY_GUIDE.md -- the external-literature receipts (the cites Phase A discovered were NLM-verified BETWEEN Phase A and Phase B, so their receipts are now present here) + the rule that NLM is the SOLE paper authority. Keep every external-NLM prop tied to its receipt; flag in open_items any external-NLM prop that STILL lacks a live receipt (it must not be allocated into a paragraph as supported). The abstract carries no citations regardless.
7. ${R}/docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md (E1-E7) + ${R}/docs/Thesis/_archive/audit_20260612/PROPOSITION_RULES.md -- discipline + taxonomy.`

const SCOPE = `SCOPE -- exactly the 3 ratified units (allocate each one's locked chain into paragraphs):
- ABSTRACT -> exactly ONE paragraph delivering all 5 elements in order (motivation; objective/gap; data+sample; measure; qualitative findings+contribution).
- INTRODUCTION (Subsection 1) -> roughly 4-6 paragraphs realizing the 4 moves in order (M1 context/gap; M2 objective+method/sample; M3 qualitative findings preview + the no-id/correlational caveat; M4 the roadmap, exactly one paragraph).
- CONCLUSION (Subsection 5) -> roughly 3 paragraphs realizing the 3 moves in order (M1 restate objective; M2 qualitative summary; M3 implications + limitations + future research). No roadmap; no lit-review re-run.`

const RULES = `HARD RULES:
- ALLOCATION, NOT RE-PLANNING: the Phase-A chains (Unit 0) are RATIFIED. Your job is to allocate their propositions into PARAGRAPHS, give each paragraph an ATOMIC intent, and order the propositions within each paragraph. Do NOT add new claims, re-number Phase-A props, change any number, drop a register lock, or re-open a settled decision.
- EVERY Phase-A proposition is HOMED in exactly one paragraph. A prop may be SPLIT across two paragraphs or two short props MERGED into one, ONLY with an explicit reason+evidence. In allocation_coverage list every Phase-A prop -> its paragraph; the red-team will reject any orphaned or duplicated prop.
- CONVENTION-DRIVEN PARAGRAPHS: realize the per-unit convention moves (Unit C). The ABSTRACT is exactly ONE paragraph. The INTRO roadmap is exactly ONE paragraph. Argue the paragraph COUNT in paragraph_count_rationale (reason+evidence) against the convention; do NOT pad or cram.
- ATOMIC PARAGRAPHS: each paragraph does ONE job (one intent / one move). No paragraph spans two unrelated moves; no two paragraphs share one move (except a move the convention says may run 1-2 paragraphs).
- ORDER + TRANSITIONS: paragraphs follow the convention order (and the chain's logic premise -> result -> inference -> caveat). A transition prop is allowed, typed framing, with reason+evidence.
- QUALITATIVE + PRESERVE EVERYTHING: every directional claim stays tied to the table cell that grounds its SIGN/significance (recorded in the prop, NOT printed as a coefficient); every register lock that bound a Phase-A prop binds the paragraph it lands in. C-traps stay honored at paragraph level (C6 formal Wald not Gelman-Stern; C4 NULL-only not strengthened; C1 POST not over-read). E1: no Pagan re-insert.
- BOUNDARY: the intro/abstract NAME the measure + equations and point to Section 2; no re-derivation. The conclusion does not re-run the literature review. No unit re-enters another unit's lane.
- FORMAT: mirror section2.2_paragraph_ledger.json exactly (intent/serves/boundary/thin_claim/guardrails/lit_body/propositions[role_in_paragraph,type,reason,evidence,...]/prose_gate/final_prose/prose_status). final_prose = "" ; prose_status = "BLOCKED -- planning only". lit_body is "none new" except the intro Move-1 paragraph(s), where it lists the external-NLM positioning cites.
- REASON + EVIDENCE ATOMIC (MOST IMPORTANT): every paragraph intent AND every proposition carries reason (WHY this paragraph / why this prop here, in this order) and evidence (an array of pointers: the Phase-A prop_id it derives from, a table cell, a claim_findings C-id, a body/Section-2 ledger ref, the 2.2 template, the convention move). No intent or proposition without both.`

const TASK = `TASK: For EACH of the 3 units, take its RATIFIED proposition chain (Unit 0) and design the PARAGRAPH ALLOCATION: (1) decide how many paragraphs and why, against the convention (paragraph_count_rationale with reason+evidence); (2) for each paragraph give an ATOMIC intent {statement, reason, evidence}, its serves / boundary / thin_claim / guardrails / lit_body; (3) place the Phase-A propositions into that paragraph as an ordered proposition_chain, each paragraph-proposition carrying from_phaseA_prop, role_in_paragraph, type, reason, evidence, numbers (the table cell grounding the direction; sample-scale numbers only), register_locks, depends_on; (4) in allocation_coverage, map every Phase-A prop to exactly one paragraph and argue no prop is orphaned or duplicated. Leave final_prose EMPTY and prose_status BLOCKED. Return the PARAGRAPH_PLAN_SET structured object.`

const PARA_PROP = {
  type: 'object',
  required: ['prop_id', 'from_phaseA_prop', 'statement', 'role_in_paragraph', 'type', 'reason', 'evidence'],
  properties: {
    prop_id: { type: 'string', description: 'paragraph-local id, e.g. 1-P2-a' },
    from_phaseA_prop: { type: 'string', description: 'the ratified Phase-A prop_id it derives from, or "new-transition"' },
    statement: { type: 'string' },
    role_in_paragraph: { type: 'string', description: 'premise | result | inference | caveat | transition | definition | roadmap + a short note on its role in THIS paragraph' },
    type: { type: 'string', enum: ['result-number', 'design-method', 'definitional', 'framing', 'external-NLM', 'callback-verified'] },
    reason: { type: 'string', description: 'WHY this prop is in this paragraph, in this order' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'pointers: Phase-A prop_id, table cell, claim C-id, body/Section-2 ledger ref, template, convention move' },
    numbers: { type: 'array', items: { type: 'string' }, description: 'QUALITATIVE: prose carries only sample-scale numbers (years, N); for result props record the table cell that grounds the SIGN/significance here, e.g. "stock coef negative + n.s. (tab:empire_building_did col 3)"' },
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
    para_id: { type: 'string', description: 'e.g. 1-P1 (intro), 5-P1 (conclusion), abstract-P1' },
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
    subsection_id: { type: 'string', description: 'abstract | 1 | 5' },
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
3. Convention realization: the ABSTRACT is exactly ONE paragraph; the INTRO realizes its 4 moves in order with the roadmap as exactly ONE paragraph; the CONCLUSION realizes its 3 moves in order with NO roadmap and NO lit-review re-run; flag any drift, pad, or cram against the convention (Unit C).
4. Paragraph atomicity: each paragraph has ONE intent/move; flag a paragraph doing two unrelated moves, or two paragraphs sharing one move beyond what the convention allows.
5. QUALITATIVE + number traceability: flag ANY coefficient/SE/p-value placed in a paragraph; every directional claim still traces to the table cell that grounds its sign; SD-magnitudes (if any sample-scale figure) use 0.3010; flag a direction that contradicts the table.
6. C-traps preserved at paragraph level: C6 formal Wald not Gelman-Stern; C4 NULL-only not strengthened; C1 POST not over-read; E1 no Pagan re-insert.
7. Boundary: intro/abstract NAME the measure + equations (point back to Section 2); the conclusion adds meaning+limitations+future and does not repeat the lit review; no cross-unit bleed.
8. Order + transitions: paragraph order follows the convention + premise->result->inference->caveat; flag a result before its premise, or a missing hand-off.
9. Format fidelity: mirrors section2.2_paragraph_ledger.json; final_prose EMPTY; prose_status BLOCKED; intent + every prop carry reason+evidence (flag any missing or unsound reason/evidence).
10. Coverage handoff: every unit's allocation_coverage maps all props; open_items surfaced (e.g. any "needs NLM verification" prop carried from Phase A; dropped-bibkey dispositions).
SYNTHESIZE: produce the single BEST paragraph allocation per unit (best atomicity, convention-realization, order, and faithful homing across the 3 plans; fix every flaw). Record reason+evidence on every synthesized paragraph intent + proposition; record flaws_found (with which_planner + reason + evidence), synthesis_decisions, and the allocation_matrix (every Phase-A prop -> paragraph -> status). Return REDTEAM_OUTPUT.`

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
