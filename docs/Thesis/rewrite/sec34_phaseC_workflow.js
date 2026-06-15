export const meta = {
  name: 'sec34-phaseC-prose-drafting',
  description: 'Phase C: draft the final PROSE for every paragraph of Sec 3 and Sec 4, from the ratified Phase-B paragraph ledgers (3 identical opus drafters + 1 opus red-team scrutinize-then-synthesize); dash-free, every number table-sourced, in the locked Section 2 voice; reason+evidence atomic on every paragraph',
  phases: [
    { title: 'Draft', detail: '3 independent opus drafters read the Phase-B paragraph ledgers + the Section 2 voice exemplar + tables, and draft final_prose for every paragraph of all 5 subsections' },
    { title: 'Redteam', detail: '1 opus reads the same inputs, scrutinizes all 3 prose drafts, then synthesizes the single best dash-free prose + a number-audit matrix' },
  ],
}

const R = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D'

const MANIFEST = `READING MANIFEST -- read every unit yourself, in full, before drafting (absolute paths):

UNIT 0 -- THE PRIMARY INPUT (what you write prose FOR; the chains are RATIFIED and LOCKED):
  ${R}/docs/Thesis/rewrite/section3.1_paragraph_ledger.json
  ${R}/docs/Thesis/rewrite/section3.2_paragraph_ledger.json
  ${R}/docs/Thesis/rewrite/section3.3_paragraph_ledger.json
  ${R}/docs/Thesis/rewrite/section3.4_paragraph_ledger.json
  ${R}/docs/Thesis/rewrite/section4.1_paragraph_ledger.json
  Each holds the ratified PARAGRAPHS in order; each paragraph carries intent / serves / boundary / thin_claim / guardrails / an ordered proposition_chain (each prop has statement, role_in_paragraph, type, reason, evidence, numbers WITH table cells, register_locks, depends_on) and an EMPTY final_prose you must fill. Write each paragraph's prose to deliver its proposition chain EXACTLY: every proposition realized, every register_lock honored in the wording, no claim added, no caveat dropped.

UNIT V -- THE VOICE EXEMPLAR (match this register + LaTeX style EXACTLY):
  ${R}/docs/Thesis/thesis_draft.tex -- the LOCKED Section 2 prose. Study its register (correlational, hedged, no overclaim), its sentence rhythm, and its LaTeX conventions: \\emph{...} for emphasis, \\citet{key}/\\citep{key} for cites, inline math $...$, set-off display via \\begin{quote}...\\end{quote} ONLY where a plan calls for it, tables referenced as Table~\\ref{tab:...}. Your Section 3/4 prose must read as the SAME author wrote it. IMPORTANT: mirror the voice of Section 2.2 through 2.5 specifically -- those were written under the current rules and are DASH-FREE. Section 2.1 is locked but still contains em-dashes ('---'); do NOT copy its dash style. Your Section 3/4 prose is dash-free like 2.2-2.5.
  ${R}/docs/Thesis/rewrite/section2.2_paragraph_ledger.json (and 2.1, 2.3, 2.4, 2.5 ledgers) -- read the final_prose fields as worked EXEMPLARS of how a verified proposition chain becomes a finished paragraph. Read the planning substance; SKIP the verbatim NLM receipt blocks.

UNIT 2 -- ${R}/docs/Thesis/_tables_from_bible.tex -- the 11 result tables byte-exact. Every number you write must be the exact cell the paragraph plan names. NEVER type a number from memory.
UNIT 3 -- ${R}/docs/Thesis/rewrite/claim_findings_ledger.json -- claims C1-C7 -> thinnest claim + register locks + C-traps + RERUN risks. CONTAINS _open_decisions_resolved_2026_06_14: SD-basis is RESOLVED -> 0.3010 (all-universe Table-1 Panel B); use 0.3010 in any economic-magnitude sentence; do NOT re-surface it. THE claim ceiling: prose may not say more than the ledger supports.
UNIT 4 -- ${R}/docs/Thesis/variable_ledger.json -- variable -> definition -> construction (ignore DROPPED entries); for 3.1 construction-mechanics wording.
UNIT 5 -- ${R}/docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md (E1-E7) + ${R}/docs/Thesis/_archive/audit_20260612/PROPOSITION_RULES.md -- the discipline (E1 no Pagan disclaimer; method claims cite the executable line) the prose must respect.
REFERENCE ONLY -- ${R}/tmp/old_draft_81efc78.tex (lines ~97-176): the prior Section 3/4 prose. You may borrow a clean phrasing, but the ratified plan + the claim ceiling OVERRIDE it; it carries stale SDs and the dropped 4.2. Do NOT copy its numbers.`

const SCOPE = `SCOPE -- draft prose for every paragraph of all 5 subsections (deliver BOTH Section 3 and Section 4):
- 3.1 Data, Sample, and Variable Construction (no headline claim) -> Table~\\ref{tab:summary_stats}.
- 3.2 Main Analysis 1: The Pre-Announcement Run-Up (C2/H1) -> tab:empire_building_did.
- 3.3 Main Analysis 2: Differential Timing (C1/H1b, the strongest result) -> tab:empire_drop_matched + placebo.
- 3.4 Main Analysis 3: Cash-Specificity (C6/H1a) -> tab:empire_cashspec + placebo.
- 4.1 Ruling Out Analyst Scrutiny (C4) -> reason_gating + cash_scrutiny_validity + cash_scrutiny_channel + empire_building_did col 4.
Use the paragraph COUNT and ORDER fixed by the Phase-B ledgers; one final_prose per paragraph.`

const RULES = `HARD RULES (prose drafting):
- DELIVER THE PLAN, NOTHING MORE: write prose that realizes the paragraph's proposition_chain completely and stops there. Add no claim, introduce no number the plan does not list, drop no caveat or register_lock. The Phase-B ledgers are the contract.
- DASH-FREE (MANDATORY): no em-dash ('---') and no en-dash ('--') anywhere in the prose. Use commas, colons, parentheses, or restructure. (Section 2 from 2.2 onward is dash-free; match it.)
- NUMBERS ARE TABLE-SOURCED: every coefficient/SE/N/percentage in the prose is the exact value the paragraph plan names, traceable to its table cell (e.g. "0.0473" with three stars from tab:empire_drop_matched col 1). NEVER from memory. Economic-magnitude SD scaling uses 0.3010 (resolved). Record each number you use in number_audit with its table cell.
- REGISTER + CEILING IN THE WORDING: honor every register_lock (correlational; no-identification; concentration-not-strict-specificity; mechanism-open; supportive-not-definitive). Do NOT over-read: C1 the negative POST (-0.0250*) is not a finding; C6 is the FORMAL Wald difference (0.0983**), never a Gelman-Stern significant-vs-insignificant side-by-side; C4 is NULL-only and underpowered, never strengthened ("does not account for THIS run-up, not that scrutiny never matters"). E1: insert NO Pagan/generated-regressand disclaimer.
- VOICE: match Section 2 exactly (the correlational, hedged register; the cadence; the LaTeX conventions). Section 3/4 are RESULTS: state each coefficient in prose, attribute it to the table, and read it descriptively. Reference each table by Table~\\ref{...}.
- BOUNDARY: 3.1 gives construction mechanics + sample and POINTS BACK to 2.3/2.5/Appendix for definitions (do not re-derive). No subsection re-enters Section 2 turf or another subsection's lane; the 2.5-P4 scrutiny verdict is owned by 4.1.
- LATEX: valid fragments (balanced math, \\emph, \\citet, Table~\\ref, \\begin{quote} only where the plan sets a statement off). Escape % and & and $ correctly. Do not invent labels.
- REASON + EVIDENCE ATOMIC (MOST IMPORTANT): every drafted paragraph carries reason (WHY this wording delivers the chain at the ceiling) and evidence (an array of pointers: the Phase-B paragraph prop_ids it realizes, the table cells for its numbers, and the Section-2 paragraph whose voice it mirrors). No paragraph prose without both.`

const TASK = `TASK: For EACH paragraph of EACH of the 5 subsections, write final_prose -- finished, dash-free LaTeX that realizes that paragraph's proposition_chain completely, at the claim ceiling, in the Section 2 voice, with every number traced to its table cell. Fill number_audit (each number -> table cell), list delivers_props (the paragraph prop_ids realized) and register_locks_honored, and give reason + evidence. Return the PROSE_SET structured object covering all 5 subsections.`

const PARA_PROSE = {
  type: 'object',
  required: ['para_id', 'final_prose', 'delivers_props', 'number_audit', 'reason', 'evidence'],
  properties: {
    para_id: { type: 'string', description: 'the Phase-B paragraph id, e.g. 3.2-P1' },
    final_prose: { type: 'string', description: 'finished dash-free LaTeX prose for this paragraph' },
    delivers_props: { type: 'array', items: { type: 'string' }, description: 'the Phase-B paragraph prop_ids this prose realizes (all of them)' },
    number_audit: { type: 'array', items: {
      type: 'object', required: ['number', 'table_cell'],
      properties: { number: { type: 'string' }, table_cell: { type: 'string' } } },
      description: 'every number that appears in final_prose, with its source table cell' },
    register_locks_honored: { type: 'array', items: { type: 'string' } },
    dash_free: { type: 'boolean', description: 'true iff no --- or -- appears in final_prose' },
    reason: { type: 'string', description: 'WHY this wording delivers the chain at the ceiling' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'Phase-B prop_ids realized + table cells + the Section-2 paragraph whose voice it mirrors' },
    open_items: { type: 'array', items: { type: 'string' } },
  },
}

const SUBSECTION = {
  type: 'object',
  required: ['subsection_id', 'title', 'paragraphs'],
  properties: {
    subsection_id: { type: 'string' },
    title: { type: 'string' },
    paragraphs: { type: 'array', items: PARA_PROSE },
    coherence_note: { type: 'string', description: 'how the paragraphs flow as one subsection; transitions; no cross-paragraph repetition' },
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
  required: ['subsections', 'redteam_report', 'number_audit_matrix'],
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
    number_audit_matrix: {
      type: 'array',
      items: { type: 'object', required: ['number', 'table_cell', 'paragraph', 'status'],
        properties: { number: { type: 'string' }, table_cell: { type: 'string' }, paragraph: { type: 'string' }, status: { type: 'string' } } },
    },
  },
}

const RUBRIC = `RED-TEAM RUBRIC -- apply to all 3 prose drafts against the Phase-B ledgers + tables + the Section 2 voice; be adversarial, default to flagging:
1. Number fidelity: every number in every paragraph's prose equals the value the Phase-B plan names and traces to that table cell; build number_audit_matrix; flag any memory number, drifted value, wrong cell, or SD that is not 0.3010.
2. Dash-free: scan every paragraph for '---' and '--'; flag each occurrence (MAJOR -- the rule is mandatory).
3. Register + ceiling: the wording honors every register_lock and says no more than the ledger supports; flag C1 POST over-reading, C6 Gelman-Stern phrasing, C4 strengthening, any E1 Pagan disclaimer, or any claim above the thin-claim ceiling.
4. Completeness: the prose realizes EVERY proposition in the paragraph's chain (nothing dropped) and introduces nothing the chain does not contain (nothing added).
5. Voice + LaTeX: matches Section 2's correlational, hedged register and cadence; valid LaTeX (balanced math, \\emph, \\citet, Table~\\ref, correct escaping); tables referenced by \\ref; flag tonal drift or broken LaTeX.
6. Boundary: 3.1 points definitions back (no re-derivation); no Section-2 turf; no cross-subsection bleed; 2.5-P4 verdict only in 4.1.
7. Coherence: the paragraphs flow as one piece across Section 3 and Section 4; transitions present; no number or sentence repeated across paragraphs that should appear once.
8. Reason + evidence present AND sound on every drafted paragraph.
SCRUTINIZE first, then SYNTHESIZE: produce the single BEST dash-free prose per paragraph (the wording that most faithfully and cleanly delivers the chain at the ceiling in the Section 2 voice; fix every flaw). Record reason + evidence on every synthesized paragraph; record flaws_found (with which_planner + reason + evidence), synthesis_decisions, and the number_audit_matrix. Return REDTEAM_OUTPUT.`

phase('Draft')
const DRAFTER_PROMPT = `You are an independent, hard-nosed empirical-finance prose writer drafting the results sections of a thesis. Draft from scratch; do not assume any other drafter's work. You realize a RATIFIED plan in prose; you do not change the plan.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${TASK}`
const drafters = (await parallel([1, 2, 3].map(i => () =>
  agent(DRAFTER_PROMPT, { label: `prose-drafter-${i}`, phase: 'Draft', schema: PROSE_SET, model: 'opus' })
))).filter(Boolean)
log(`${drafters.length}/3 prose drafters returned`)

phase('Redteam')
const REDTEAM_PROMPT = `You are an adversarial red-team referee for thesis results prose. You have the same manifest + ratified paragraph ledgers + tables the drafters used; read them yourself to judge the prose against the locked plan and the Section 2 voice.\n\n${MANIFEST}\n\n${SCOPE}\n\n${RULES}\n\n${RUBRIC}\n\nHere are the ${drafters.length} independent prose drafts to scrutinize and synthesize:\n${JSON.stringify(drafters)}`
const synthesis = await agent(REDTEAM_PROMPT, { label: 'redteam-synth-C', phase: 'Redteam', schema: REDTEAM_OUTPUT, model: 'opus' })

return { drafters, synthesis }
