export const meta = {
  name: 'introconcl-phaseA-subsection-chains',
  description: 'Phase A: per-unit purpose + proposition chain for the Abstract, Introduction, and Conclusion (3 identical opus planners + 1 opus red-team synthesis); planned FRESH from the locked body + the NLM-derived conventions; results QUALITATIVE; reason+evidence atomic on every item',
  phases: [
    { title: 'Plan', detail: '3 independent opus planners read the full manifest, plan purpose + proposition chain for all 3 units (Abstract, Intro, Conclusion)' },
    { title: 'Redteam', detail: '1 opus reads the same manifest, scrutinizes all 3 plans, synthesizes the single best plan + coverage matrix' },
  ],
}

const R = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D'

const MANIFEST = `READING MANIFEST -- read every unit yourself, in full, before planning (absolute paths):

THE BODY IS LOCKED. The Abstract, Introduction, and Conclusion are planned FRESH from the CURRENT locked body below. There is NO prior draft to re-plan; do not look for one, do not import stale prose.

1. ${R}/docs/Thesis/rewrite/claim_findings_ledger.json -- claims C1-C7 -> finding -> thinnest referee-proof version + register locks + C-traps + _open_decisions_resolved_2026_06_14 (SD-basis RESOLVED to 0.3010). THE claim ceiling: the abstract's findings line, the intro's preview, and the conclusion's summary may say NO MORE than this supports. The four LIVE results: C2 (pre-announcement cash run-up), C1 (differential timing -- elevated before, indistinguishable from zero once the deal is announced -- the STRONGEST), C6 (cash-vs-stock gap via the FORMAL pooled Wald test), C4 (analyst scrutiny ruled out).
2. ${R}/docs/Thesis/rewrite/section2.1_paragraph_ledger.json .. section2.5_paragraph_ledger.json (5 files) -- the FINAL, LOCKED Section 2 prose: the conceptual framework, the three hypotheses (H1 run-up / H1a cash-specificity / H1b differential-timing), the UncResCEO residual measure + the DWZ eq-4 decomposition, the three estimating equations, convergent validity + the analyst-scrutiny construct. The intro MOTIVATES these; the conclusion REFLECTS on them. Read the planning substance + final_prose; SKIP the verbatim NLM receipt blocks (verification.{answer,quotes,located,span_pin}).
3. ${R}/docs/Thesis/rewrite/section3.1_paragraph_ledger.json , section3.2_..., section3.3_..., section3.4_..., section4.1_paragraph_ledger.json (5 files) -- the FINAL, LOCKED Section 3/4 prose (final_prose) + proposition chains. This is the body the intro previews and the conclusion summarizes. Read final_prose for the exact findings, their DIRECTION, and their register (3.1 data/sample/measure; 3.2 = C2 run-up; 3.3 = C1 timing, strongest; 3.4 = C6 cash-specificity; 4.1 = C4 scrutiny rule-out).
4. ${R}/docs/Thesis/DraftTemplate.txt -- BINDING CONVENTION. Holds the NLM-derived SECTION-WRITING CONVENTIONS for the ABSTRACT (5-element single paragraph), the INTRODUCTION (4 moves: context/gap; objective+method/sample; preview of findings; roadmap), and the CONCLUSION (3 moves: restate objective; qualitative summary; implications+limitations+future), each with per-move depth + style. Your proposition chain for each unit MUST deliver its convention moves, in order, at the stated depth. RESULTS ARE QUALITATIVE (resolved): NO regression coefficients/SEs in any of these three units.
5. ${R}/docs/Thesis/_tables_from_bible.tex -- the 11 result tables byte-exact. NOT for placing numbers in this prose (these units are qualitative), but as the SOURCE OF TRUTH for the SIGN + SIGNIFICANCE behind every directional claim (e.g. "no comparable rise for stock" must match the stock coefficient being negative and nonsignificant). Cite the relevant table cell in a proposition's evidence as the basis for its direction.
6. ${R}/docs/Thesis/variable_ledger.json -- variable -> definition -> construction (ignore DROPPED entries); for NAMING the measure (UncResCEO) and the data sources (Capital IQ transcripts, SDC deals, Execucomp CEO identity, Compustat, the EPU/PRisk indices) correctly. Do NOT re-derive definitions; the intro NAMES, it does not construct.
7. ${R}/docs/Thesis/thesis_draft.tex -- read ONLY the bibliography (the \\bibitem list) to know which references are LIVE. The four bibitems orphaned when Section 4.2 was dropped (everhart2025, gokkaya2025, bushee2018, lerman2026) are NOT in the live list. (Section 2.1 prose here still shows em-dashes -- do NOT copy that dash style; later prose is dash-free.)
8. ${R}/tmp/nlm_*.json (the NLM verification receipts already captured) + ${R}/docs/Thesis/rewrite/NLM_QUERY_GUIDE.md -- the external-literature evidence + the rule that NLM is the SOLE paper authority (never a PDF, never memory). Every external-literature proposition is typed external-NLM and carries its bibkey + the receipt it rests on; if no live receipt exists, FLAG it for NLM verification (do not assume the paper says it).
9. ${R}/docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md (E1-E7) + ${R}/docs/Thesis/_archive/audit_20260612/PROPOSITION_RULES.md -- the verification discipline (E1: no Pagan/generated-regressand disclaimer) + the proposition taxonomy.`

const SCOPE = `SCOPE -- exactly 3 units, planned FRESH from the locked body (NO old draft):
- ABSTRACT -> the 5-element single paragraph: (1) motivation/prior practice; (2) the objective/gap; (3) data + sample; (4) the UncResCEO measure + setting; (5) the qualitative findings + contribution. No citations, no numbers beyond sample scale, no roadmap.
- INTRODUCTION (Subsection 1) -> the 4 convention moves: (M1) context + the disclosure-bind phenomenon + the literature gap, with the external-NLM positioning cites; (M2) the research question + the UncResCEO measure + the cash-acquisition setting + sample; (M3) a QUALITATIVE preview of the three findings + the scrutiny rule-out, with the explicit no-identification / correlational caveat; (M4) the section roadmap.
- CONCLUSION (Subsection 5) -> the 3 convention moves: (M1) restate the objective (mirror the intro); (M2) a QUALITATIVE summary of the three findings; (M3) implications + limitations (no-identification, correlational, mechanism-open) + future research. Drops the roadmap; does NOT re-do the literature review.`

const RULES = `HARD RULES:
- BUILD FRESH: there is NO source draft to re-plan. Plan each unit's proposition chain from the claim ceiling (unit 1), the locked Section 2-4 prose (units 2-3), and the binding convention (unit 4). Invent NO finding; the only results are C1/C2/C4/C6 as the body states them.
- FOLLOW THE CONVENTION (unit 4) per unit: the Abstract delivers its 5 elements; the Introduction its 4 moves in order; the Conclusion its 3 moves in order. Honor the per-move depth + the style (we-voice; present tense for findings; citations high in intro Move 1, ~zero in the conclusion and abstract).
- RESULTS ARE QUALITATIVE (RESOLVED 2026-06-14): the abstract, intro, and conclusion state results DIRECTIONALLY, in words, with NO regression coefficients, SEs, p-values, or t-stats. Numbers are allowed ONLY for sample scale (years, counts). Each directional claim ("rises in the quarter before a cash deal", "no comparable rise among stock acquirers", "indistinguishable from zero once the deal is announced", "the gap survives a formal pooled test", "analyst scrutiny does not account for it") MUST match the SIGN + SIGNIFICANCE the body/table reports; record that table cell in the proposition's evidence as the basis.
- THIN-CLAIM CEILING + REGISTER LOCKS bind every proposition: correlational; no-identification; concentration-not-strict-specificity; mechanism-open; supportive-not-definitive. The intro AND the conclusion state the no-identification / correlational caveat EXPLICITLY (it is part of the convention's honesty); the abstract stays within the ceiling implicitly.
- C-TRAPS survive even in compressed summary: C1 -> the negative POST is NOT a finding; resolution = "indistinguishable from zero once announced", not a reversal. C6 -> the cash-vs-stock gap is the FORMAL pooled (Wald) difference, NEVER a Gelman-Stern "significant-for-cash vs not-for-stock" contrast. C4 -> "analyst scrutiny does not account for THIS run-up", NEVER "scrutiny never matters". E1 -> insert NO Pagan/generated-regressand disclaimer.
- EXTERNAL LITERATURE (intro Move 1 + positioning): every cited prior-work claim is typed external-NLM and carries its bibkey + the NLM-receipt pointer it rests on (unit 8). If a needed claim has NO live receipt yet, mark it in open_decisions as "needs NLM verification before Phase C". The four dropped bibkeys (everhart2025, gokkaya2025, bushee2018, lerman2026): cite ONLY if load-bearing AND a live receipt exists AND mark "re-add bibitem at Phase D"; else drop the claim. The gap statement ("no prior work measures...") is typed framing (a negative cannot be NLM-proven) -- mark and keep.
- BOUNDARY: the intro NAMES the measure + the equations and points to Section 2; it does not re-derive them. The abstract names the measure in one phrase. The conclusion does not re-run the literature review.
- DASH-FREE for any later prose (commas/colons/parentheses; no em-dash or en-dash).
- REASON + EVIDENCE ATOMIC (MOST IMPORTANT): every unit PURPOSE and every proposition carries "reason" (WHY it is in the chain / which convention move it serves) and "evidence" (an array of manifest pointers it is BASED ON: a claim_findings C-id, a body final_prose ref, a table cell for the underlying sign, the convention move in DraftTemplate, an NLM receipt, a Section-2 ledger ref). No purpose or proposition without both.`

const TASK = `TASK: For EACH of the 3 units (Abstract, Introduction, Conclusion): (1) identify its PURPOSE -- what it must deliver 100%, mapped to its convention moves -- with reason + evidence; and (2) design the PROPOSITION CHAIN that delivers that purpose completely, move by move. A proposition chain is an ordered set of atomic propositions (premise -> result -> inference -> caveat -> transition/roadmap), each typed, each with reason + evidence + the register locks it honors + depends_on. Keep result propositions QUALITATIVE, but record in evidence the table cell that grounds their sign/significance. Do NOT allocate paragraphs (a later phase). Make the chain COMPLETE: in coverage.purpose_fully_delivered, argue the chain delivers every convention move with no gap. Return the SUBSECTION_PLAN_SET structured object (one entry per unit).`

const PROP = {
  type: 'object',
  required: ['prop_id', 'statement', 'role', 'type', 'reason', 'evidence'],
  properties: {
    prop_id: { type: 'string' },
    statement: { type: 'string' },
    role: { type: 'string', description: 'premise | result | inference | caveat | definition | transition | roadmap' },
    type: { type: 'string', enum: ['result-number', 'design-method', 'definitional', 'framing', 'external-NLM', 'callback-verified'] },
    reason: { type: 'string', description: 'WHY this proposition is in the chain / which convention move it serves / what gap in the purpose it fills' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'manifest pointers this is BASED ON' },
    numbers: { type: 'array', items: { type: 'string' }, description: 'QUALITATIVE units: only sample-scale numbers (years, N) belong in prose; for result props, record the table cell that grounds the sign/significance here, e.g. "stock coef negative + n.s. (tab:empire_building_did col 3)"' },
    register_locks: { type: 'array', items: { type: 'string' } },
    depends_on: { type: 'array', items: { type: 'string' } },
  },
}

const SUBSECTION = {
  type: 'object',
  required: ['subsection_id', 'title', 'purpose', 'delivers_claims', 'tables_referenced', 'proposition_chain', 'coverage'],
  properties: {
    subsection_id: { type: 'string', description: 'abstract | 1 | 5' },
    title: { type: 'string' },
    purpose: {
      type: 'object',
      required: ['statement', 'reason', 'evidence'],
      properties: { statement: { type: 'string' }, reason: { type: 'string' }, evidence: { type: 'array', items: { type: 'string' } } },
    },
    delivers_claims: { type: 'array', items: { type: 'string' } },
    tables_referenced: { type: 'array', items: { type: 'string' }, description: 'tables that ground the directional claims (not referenced in prose; basis only)' },
    hypotheses_paid_off: { type: 'array', items: { type: 'string' } },
    pays_off_section2: { type: 'array', items: { type: 'string' } },
    proposition_chain: { type: 'array', items: PROP },
    coverage: {
      type: 'object',
      required: ['purpose_fully_delivered'],
      properties: { purpose_fully_delivered: { type: 'string', description: 'argue the chain delivers every DraftTemplate convention move for this unit, in order, with no gap' }, gaps: { type: 'array', items: { type: 'string' } } },
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
  required: ['subsections', 'redteam_report', 'coverage_matrix'],
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
    coverage_matrix: {
      type: 'array',
      items: { type: 'object', required: ['claim', 'subsection', 'tables', 'status'],
        properties: { claim: { type: 'string' }, subsection: { type: 'string', description: 'the unit: abstract | 1 | 5' }, tables: { type: 'array', items: { type: 'string' } }, status: { type: 'string' } } },
    },
  },
}

const RUBRIC = `RED-TEAM RUBRIC -- apply to all 3 plans against the manifest; be adversarial, default to flagging:
1. Convention adherence: each unit delivers its DraftTemplate moves IN ORDER at the stated depth (Abstract 5 elements / Intro 4 moves / Conclusion 3 moves). Flag a missing move, a wrong order, or drift (e.g. a roadmap in the conclusion or abstract; a literature review re-run in the conclusion; the abstract carrying a citation or a coefficient).
2. Thin-claim ceiling: any proposition claiming more than the body / claim_findings supports -> flaw.
3. Register locks intact (correlational; no-identification; concentration-not-specificity; mechanism-open; supportive-not-definitive); the intro AND the conclusion state the no-identification / correlational caveat explicitly.
4. QUALITATIVE results: flag ANY regression coefficient / SE / p-value / t-stat placed in the abstract, intro, or conclusion. Every directional claim must match the SIGN + SIGNIFICANCE of its cited table cell -> flag a direction that contradicts the table.
5. C-traps: C1 POST not over-read (resolution = indistinguishable from zero); C6 formal Wald not Gelman-Stern; C4 not strengthened; E1 no Pagan disclaimer.
6. External literature: every prior-work claim typed external-NLM with a bibkey + receipt, or flagged "needs NLM verification"; NO dropped bibkey (everhart/gokkaya/bushee/lerman) cited without a live receipt + "re-add bibitem at Phase D" note; the gap claim typed framing.
7. Coverage: the three live findings (C2 run-up, C1 timing, C6 cash-specificity) + the C4 rule-out each appear in the intro preview AND the conclusion summary AND (qualitatively) the abstract; every hypothesis (H1/H1a/H1b) is reflected; the measure (UncResCEO) + the cash-acquisition setting are named.
8. Boundary: the intro/abstract NAME the measure + equations (no re-derivation); the conclusion adds meaning + limitations + future work and does NOT repeat the lit review.
9. Reason + evidence present AND sound on every purpose + proposition.
10. Coherence across the three units: the abstract is a faithful compression of the intro; the conclusion mirrors the intro's setup without re-opening it; no claim contradicts another across the three.
SYNTHESIZE: produce the single BEST proposition chain per unit (best convention-adherence, ceiling-faithful, qualitative, most referee-proof version of each proposition across the 3 plans; fix every flaw). Record reason + evidence on every synthesized proposition; record flaws_found (with which_planner + reason + evidence), synthesis_decisions, and a coverage_matrix (claim -> unit -> status). Return REDTEAM_OUTPUT.`

phase('Plan')
const PLANNER_PROMPT = `You are an independent, hard-nosed empirical-finance proposition planner. Plan from scratch; do not assume any other planner's work. You plan the Abstract, Introduction, and Conclusion FRESH from the locked body + the binding conventions; there is no prior draft.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${TASK}`
const planners = (await parallel([1, 2, 3].map(i => () =>
  agent(PLANNER_PROMPT, { label: `planner-${i}`, phase: 'Plan', schema: SUBSECTION_PLAN_SET, model: 'opus' })
))).filter(Boolean)
log(`${planners.length}/3 planners returned`)

phase('Redteam')
const REDTEAM_PROMPT = `You are an adversarial red-team referee. You have the same manifest the planners used; read it yourself to judge their work against the sources.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${RUBRIC}\n\nHere are the ${planners.length} independent plans to scrutinize and synthesize:\n${JSON.stringify(planners)}`
const synthesis = await agent(REDTEAM_PROMPT, { label: 'redteam-synth', phase: 'Redteam', schema: REDTEAM_OUTPUT, model: 'opus' })

return { planners, synthesis }
