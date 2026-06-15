export const meta = {
  name: 'introconcl-phaseC-prose-drafting',
  description: 'Phase C: draft the final PROSE for every paragraph of the Abstract, Introduction, and Conclusion, from the ratified Phase-B paragraph ledgers (3 identical opus drafters + 1 opus red-team scrutinize-then-synthesize); dash-free, QUALITATIVE (no coefficients), in the locked Section 2 voice + the per-unit convention; reason+evidence atomic on every paragraph',
  phases: [
    { title: 'Draft', detail: '3 independent opus drafters read the Phase-B paragraph ledgers + the Section 2 voice exemplar + the conventions, and draft final_prose for every paragraph of all 3 units' },
    { title: 'Redteam', detail: '1 opus reads the same inputs, scrutinizes all 3 prose drafts, then synthesizes the single best dash-free prose + a number/direction-audit matrix' },
  ],
}

const R = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D'

const MANIFEST = `READING MANIFEST -- read every unit yourself, in full, before drafting (absolute paths):

UNIT 0 -- THE PRIMARY INPUT (what you write prose FOR; the chains are RATIFIED and LOCKED):
  ${R}/docs/Thesis/rewrite/section_abstract_paragraph_ledger.json
  ${R}/docs/Thesis/rewrite/section1_paragraph_ledger.json
  ${R}/docs/Thesis/rewrite/section5_paragraph_ledger.json
  Each holds the ratified PARAGRAPHS in order; each paragraph carries intent / serves / boundary / thin_claim / guardrails / an ordered proposition_chain (each prop has statement, role_in_paragraph, type, reason, evidence, numbers WITH the table cell grounding its direction, register_locks, depends_on) and an EMPTY final_prose you must fill. Write each paragraph's prose to deliver its proposition chain EXACTLY: every proposition realized, every register_lock honored in the wording, no claim added, no caveat dropped.

UNIT V -- THE VOICE EXEMPLAR (match this register + LaTeX style EXACTLY):
  ${R}/docs/Thesis/thesis_draft.tex -- the LOCKED Section 2 prose. Study its register (correlational, hedged, no overclaim), its sentence rhythm, and its LaTeX conventions: \\emph{...} for emphasis, \\citet{key}/\\citep{key} for cites, inline math $...$, tables NOT referenced in the abstract/intro/conclusion prose (these units are qualitative; no Table~\\ref needed). IMPORTANT: mirror the voice of Section 2.2 through 2.5 specifically -- those were written under the current rules and are DASH-FREE. Section 2.1 is locked but still contains em-dashes ('---'); do NOT copy its dash style. Your Abstract/Intro/Conclusion prose is dash-free like 2.2-2.5.
  ${R}/docs/Thesis/rewrite/section2.2_paragraph_ledger.json (and 2.1, 2.3, 2.4, 2.5 ledgers) AND ${R}/docs/Thesis/rewrite/section3.1_paragraph_ledger.json , 3.2, 3.3, 3.4, 4.1 -- read the final_prose fields as worked EXEMPLARS of how a verified proposition chain becomes a finished paragraph, AND as the body whose findings the intro previews and the conclusion summarizes (match how the body states each result's direction). Read the planning substance; SKIP the verbatim NLM receipt blocks.

UNIT W -- THE BINDING CONVENTION:
  ${R}/docs/Thesis/DraftTemplate.txt -- the NLM-derived per-unit SECTION-WRITING CONVENTION. The ABSTRACT is ONE single compressed paragraph (5 elements; present tense; "we"; NO citations, NO coefficients, NO roadmap). The INTRODUCTION follows its 4 moves (Move-1 high citation density; Move-4 the roadmap). The CONCLUSION follows its 3 moves (no roadmap; ~zero citations; no lit-review re-run). Honor each unit's style.

UNIT 2 -- ${R}/docs/Thesis/_tables_from_bible.tex -- the 11 result tables byte-exact. You do NOT print coefficients in this prose; the table is the SOURCE OF TRUTH for the SIGN + SIGNIFICANCE of each directional claim. Confirm every directional statement matches its cell.
UNIT 3 -- ${R}/docs/Thesis/rewrite/claim_findings_ledger.json -- claims C1-C7 -> thinnest claim + register locks + C-traps + _open_decisions_resolved_2026_06_14 (SD=0.3010). THE claim ceiling: prose may not say more than the ledger supports.
UNIT 4 -- ${R}/docs/Thesis/variable_ledger.json -- variable -> definition -> construction (ignore DROPPED entries); for naming the measure (UncResCEO) + data sources in one phrase (no re-derivation).
UNIT 5 -- ${R}/docs/Thesis/thesis_draft.tex bibliography (live \\bibitem list) + ${R}/tmp/nlm_*.json + ${R}/docs/Thesis/rewrite/NLM_QUERY_GUIDE.md -- the live references + the external-literature receipts. Cite (\\citet/\\citep) ONLY a live bibkey backed by a Phase-A/B external-NLM receipt; never a dropped bibkey, never an unverified claim. NLM is the SOLE paper authority.
UNIT 6 -- ${R}/docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md (E1-E7) + PROPOSITION_RULES.md -- the discipline (E1 no Pagan disclaimer) the prose must respect.`

const SCOPE = `SCOPE -- draft prose for every paragraph of all 3 units:
- ABSTRACT -> one single paragraph: motivation; objective/gap; data+sample; the UncResCEO measure; the qualitative findings + contribution. Compressed; present tense; "we"; no citations, no numbers beyond sample scale, no roadmap.
- INTRODUCTION (Subsection 1) -> the paragraphs fixed by the Phase-B ledger, realizing the 4 moves (context/gap with cites; objective+method/sample; qualitative findings preview + the no-id/correlational caveat; roadmap).
- CONCLUSION (Subsection 5) -> the paragraphs fixed by the Phase-B ledger, realizing the 3 moves (restate objective; qualitative summary; implications+limitations+future). No roadmap.
Use the paragraph COUNT and ORDER fixed by the Phase-B ledgers; one final_prose per paragraph.`

const RULES = `HARD RULES (prose drafting):
- DELIVER THE PLAN, NOTHING MORE: write prose that realizes the paragraph's proposition_chain completely and stops there. Add no claim, introduce no number the plan does not list, drop no caveat or register_lock. The Phase-B ledgers are the contract.
- DASH-FREE (MANDATORY): no em-dash ('---') and no en-dash ('--') anywhere in the prose. Use commas, colons, parentheses, or restructure. (Section 2 from 2.2 onward is dash-free; match it.)
- QUALITATIVE RESULTS (MANDATORY): NO regression coefficients, SEs, p-values, or t-stats in the abstract, intro, or conclusion. State each result directionally in words ("rises in the quarter before a cash acquisition", "no comparable rise among stock acquirers", "indistinguishable from zero once the deal is announced", "the gap survives a formal pooled test", "analyst scrutiny does not account for it"). Numbers are allowed ONLY for sample scale (the years 2002 to 2018, counts). Every directional phrase MUST match the SIGN + SIGNIFICANCE of the table cell the plan names; record each in direction_audit (claim -> table cell). Record any sample-scale number in number_audit.
- REGISTER + CEILING IN THE WORDING: honor every register_lock (correlational; no-identification; concentration-not-strict-specificity; mechanism-open; supportive-not-definitive). Do NOT over-read: C1 the negative POST is NOT a finding (resolution = indistinguishable from zero); C6 is the FORMAL Wald difference, never a Gelman-Stern significant-vs-insignificant side-by-side; C4 is NULL-only and underpowered, never strengthened ("does not account for THIS run-up, not that scrutiny never matters"). E1: insert NO Pagan/generated-regressand disclaimer. The intro AND conclusion voice the no-identification / correlational caveat explicitly.
- VOICE + CONVENTION: match Section 2 exactly (the correlational, hedged register; the cadence; the LaTeX conventions) AND the per-unit convention (Unit W): the abstract compressed and citation-free; the intro Move-1 citation-dense, the roadmap mechanical; the conclusion citation-free with no roadmap. Present tense for findings; first-person "we" for our actions.
- LATEX: valid fragments (balanced math, \\emph, \\citet/\\citep, correct escaping of % & $). The abstract/intro/conclusion do NOT use Table~\\ref (qualitative). Do not invent labels or cite a non-live bibkey.
- REASON + EVIDENCE ATOMIC (MOST IMPORTANT): every drafted paragraph carries reason (WHY this wording delivers the chain at the ceiling in the convention voice) and evidence (an array of pointers: the Phase-B paragraph prop_ids it realizes, the table cells grounding its directions, the live bibkeys/receipts for any cite, and the Section-2/body paragraph whose voice it mirrors). No paragraph prose without both.`

const TASK = `TASK: For EACH paragraph of EACH of the 3 units, write final_prose -- finished, dash-free, QUALITATIVE LaTeX that realizes that paragraph's proposition_chain completely, at the claim ceiling, in the Section 2 voice + the per-unit convention, with every directional claim matching its table cell and no coefficient printed. Fill number_audit (each sample-scale number -> table/source) and direction_audit (each directional claim -> the table cell that grounds its sign), list delivers_props (the paragraph prop_ids realized) and register_locks_honored, and give reason + evidence. Return the PROSE_SET structured object covering all 3 units.`

const PARA_PROSE = {
  type: 'object',
  required: ['para_id', 'final_prose', 'delivers_props', 'direction_audit', 'reason', 'evidence'],
  properties: {
    para_id: { type: 'string', description: 'the Phase-B paragraph id, e.g. 1-P1, 5-P2, abstract-P1' },
    final_prose: { type: 'string', description: 'finished dash-free, qualitative LaTeX prose for this paragraph' },
    delivers_props: { type: 'array', items: { type: 'string' }, description: 'the Phase-B paragraph prop_ids this prose realizes (all of them)' },
    direction_audit: { type: 'array', items: {
      type: 'object', required: ['claim', 'table_cell', 'sign'],
      properties: { claim: { type: 'string' }, table_cell: { type: 'string' }, sign: { type: 'string', description: 'the sign + significance the cell shows, e.g. "positive, p<0.01" / "negative, n.s."' } } },
      description: 'every directional result-claim in the prose -> the table cell that grounds it + that cell sign/significance' },
    number_audit: { type: 'array', items: {
      type: 'object', required: ['number', 'source'],
      properties: { number: { type: 'string' }, source: { type: 'string' } } },
      description: 'any sample-scale number in the prose (years, N) -> its source; usually short or empty' },
    register_locks_honored: { type: 'array', items: { type: 'string' } },
    dash_free: { type: 'boolean', description: 'true iff no --- or -- appears in final_prose' },
    no_coefficients: { type: 'boolean', description: 'true iff no regression coefficient/SE/p-value/t-stat appears in final_prose' },
    reason: { type: 'string', description: 'WHY this wording delivers the chain at the ceiling in the convention voice' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'Phase-B prop_ids realized + table cells + live bibkeys/receipts + the Section-2/body paragraph whose voice it mirrors' },
    open_items: { type: 'array', items: { type: 'string' } },
  },
}

const SUBSECTION = {
  type: 'object',
  required: ['subsection_id', 'title', 'paragraphs'],
  properties: {
    subsection_id: { type: 'string', description: 'abstract | 1 | 5' },
    title: { type: 'string' },
    paragraphs: { type: 'array', items: PARA_PROSE },
    coherence_note: { type: 'string', description: 'how the paragraphs flow as one unit; transitions; no cross-paragraph repetition; the abstract compresses the intro; the conclusion mirrors the intro' },
  },
}

const PROSE_SET = {
  type: 'object',
  required: ['subsections'],
  properties: {
    subsections: { type: 'array', items: SUBSECTION },
    global_notes: { type: 'array', items: { type: 'string' } },
  },
}

const REDTEAM_OUTPUT = {
  type: 'object',
  required: ['subsections', 'redteam_report', 'audit_matrix'],
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
    audit_matrix: {
      type: 'array',
      items: { type: 'object', required: ['claim', 'table_cell', 'paragraph', 'status'],
        properties: { claim: { type: 'string' }, table_cell: { type: 'string' }, paragraph: { type: 'string' }, status: { type: 'string', description: 'direction matches cell / mismatch / no-coefficient-ok' } } },
    },
  },
}

const RUBRIC = `RED-TEAM RUBRIC -- apply to all 3 prose drafts against the Phase-B ledgers + tables + the Section 2 voice + the conventions; be adversarial, default to flagging:
1. QUALITATIVE fidelity: flag ANY regression coefficient/SE/p-value/t-stat in the abstract, intro, or conclusion (MAJOR). Every directional claim must match the SIGN + SIGNIFICANCE of its table cell; build audit_matrix; flag any direction that contradicts the table, or a claim with no grounding cell.
2. Dash-free: scan every paragraph for '---' and '--'; flag each occurrence (MAJOR -- the rule is mandatory).
3. Register + ceiling: the wording honors every register_lock and says no more than the ledger supports; flag C1 POST over-reading, C6 Gelman-Stern phrasing, C4 strengthening, any E1 Pagan disclaimer, or any claim above the thin-claim ceiling. Intro + conclusion must state the no-id/correlational caveat.
4. Convention: the abstract is ONE compressed citation-free paragraph (5 elements, no roadmap); the intro realizes its 4 moves (Move-1 cite-dense, the roadmap mechanical); the conclusion has no roadmap, ~zero cites, no lit-review re-run. Flag drift.
5. Completeness: the prose realizes EVERY proposition in the paragraph's chain (nothing dropped) and introduces nothing the chain does not contain (nothing added).
6. Voice + LaTeX: matches Section 2's correlational, hedged register and cadence; valid LaTeX (balanced math, \\emph, \\citet/\\citep, correct escaping); cites ONLY live bibkeys backed by receipts; no Table~\\ref in these qualitative units; flag tonal drift, broken LaTeX, or a non-live/unverified cite.
7. Coherence: the paragraphs flow as one unit; the abstract is a faithful compression of the intro; the conclusion mirrors the intro's setup without re-opening it; no sentence or claim repeated across paragraphs that should appear once; no contradiction across the three units.
8. Reason + evidence present AND sound on every drafted paragraph.
SCRUTINIZE first, then SYNTHESIZE: produce the single BEST dash-free, qualitative prose per paragraph (the wording that most faithfully and cleanly delivers the chain at the ceiling in the Section 2 voice + convention; fix every flaw). Record reason + evidence on every synthesized paragraph; record flaws_found (with which_planner + reason + evidence), synthesis_decisions, and the audit_matrix. Return REDTEAM_OUTPUT.`

phase('Draft')
const DRAFTER_PROMPT = `You are an independent, hard-nosed empirical-finance prose writer drafting the abstract, introduction, and conclusion of a thesis. Draft from scratch; do not assume any other drafter's work. You realize a RATIFIED plan in prose; you do not change the plan.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${TASK}`
const drafters = (await parallel([1, 2, 3].map(i => () =>
  agent(DRAFTER_PROMPT, { label: `prose-drafter-${i}`, phase: 'Draft', schema: PROSE_SET, model: 'opus' })
))).filter(Boolean)
log(`${drafters.length}/3 prose drafters returned`)

phase('Redteam')
const REDTEAM_PROMPT = `You are an adversarial red-team referee for thesis abstract/intro/conclusion prose. You have the same manifest + ratified paragraph ledgers + tables the drafters used; read them yourself to judge the prose against the locked plan, the Section 2 voice, and the conventions.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${RUBRIC}\n\nHere are the ${drafters.length} independent prose drafts to scrutinize and synthesize:\n${JSON.stringify(drafters)}`
const synthesis = await agent(REDTEAM_PROMPT, { label: 'redteam-synth-C', phase: 'Redteam', schema: REDTEAM_OUTPUT, model: 'opus' })

return { drafters, synthesis }
