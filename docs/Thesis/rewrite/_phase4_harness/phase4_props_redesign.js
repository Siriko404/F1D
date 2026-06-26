export const meta = {
  name: 'phase4-props-redesign',
  description: 'Phase-4: redesign a thesis SECTION proposition chain so it carries the locked Phase-3 why-cash motivation (the masking asymmetry) in place of the older cash-focus motivation. SECTION-AGNOSTIC: the same prompts run for any section; an external build step embeds that section subsections chain (skeleton) + the fixed evidence map at the anchors. Per section, two agent layers then one red team: PANEL-1 = 3 neurodiverse agents (identical task, heavily paraphrased, NO examples) each DECIDE which propositions carry the why-cash motivation and redesign ONLY those (add / re-derive / reword / demote / relocate / delete), evidence by reference (evidence IDs, never transcribe), rationale per change; everything else stays. PANEL-2 = 3 neurodiverse agents each read all 3 Panel-1 change-sets, damage-red-team them (no proposition outside the why-cash motivation altered; honesty floor; cite-axis; chain logic) and emit one hardened change-set + scrutiny log. RED-TEAM = 1 agent synthesizes the 3 hardened change-sets BY REFERENCE (keep/merge/reject over IDs) into one final change-set. The JS copies kept changes verbatim; an external finalize step applies them ADDITIVELY to cloned ledgers (originals byte-identical, final_prose stays BLOCKED).',
  phases: [
    { title: 'Panel-1', detail: '3 paraphrased agents (identical task) -> 3 proposed why-cash redesign change-sets' },
    { title: 'Panel-2', detail: '3 paraphrased agents -> damage-red-team all 3 + emit 3 hardened change-sets' },
    { title: 'Red-team', detail: 'synthesize the 3 hardened change-sets BY REFERENCE -> 1 final change-set' },
  ],
}

// SECTION = { section, subsections:[ { subsection, title, section_job, spine, logic_chain_validated:{}, paragraphs:[ {pid, intent, thin_claim, guardrails:[], props:[ {prop_id, type, verdict, statement, role} ] } ] } ] }
// EVIDENCE = { ev_id: { cite, text, page, section } }   (the fixed, NLM-verified quote pool; agents cite by ev_id and NEVER retype a quote)
// Both embedded by an EXTERNAL build step (_phase4_harness/build_phase4.py) at the anchors below. The harness never reads files at runtime.
const SECTION = {} // __SECTION_ANCHOR__
const EVIDENCE = {} // __EVIDENCE_ANCHOR__

if (typeof args === 'string') { try { args = JSON.parse(args) } catch (e) { args = {} } }
if (!args || typeof args !== 'object') args = {}

// ===================== locked Phase-3 inputs (section-agnostic constants; ASCII only) =====================
const MASKING_DECISION = `LOCKED why-cash motivation (Phase 3) -- the MASKING ASYMMETRY:
- A STOCK deal pays in equity, a currency whose price matters, so the acquirer has an incentive to keep its valuation high and manages perceptions UP before the deal (scripted optimism).
- A CASH deal pays in cash, with no currency to protect, so there is no such incentive.
- Therefore cash is the (relatively) UNMANAGED window where the disclosure-strain surfaces as unscripted Q&A uncertainty, and the run-up CONCENTRATES in cash.
This is a MOTIVATION (an ex-ante reason to focus on cash), NOT a tested mechanism.`

const HONESTY_FLOOR = `HONESTY FLOOR -- non-negotiable; every proposed change must obey it:
- Data: cash run-up +0.0461 (p=.0074, significant); stock -0.0429 (not significant -- a noisy flat null); Wald cash-minus-stock 0.0983 (p=.039, two-tailed).
- NEVER say or imply "stock suppressed" or that stock is pushed below its baseline. The cash>stock differential is ATTENUATION (the stock effect is smaller and noisier), and the observed gap is CASH RISING. We interpret, we do not detect.
- Cross-channel bridge: the cited papers document management in SCRIPTED channels (earnings numbers, press-release tone); our dependent variable is the UNSCRIPTED Q&A residual, net of the scripted presentation, so we read the hardest-to-manage channel -- frame this as a STRENGTH, not a gap.
- Register locks stay intact: correlational; no-identification; concentration-not-strict-specificity; mechanism-open; supportive-not-definitive.
- The timing round-trip result (C1) carries the paper independently of masking; if a reader rejects the why-cash, the empirical contribution still stands.`

const CITE_STACK = `CITE STACK -- the ONLY admissible sources for the new motivation. Cite each on its correct axis; mixing axes is an error:
- shleifer_vishny2003 (Shleifer and Vishny 2003, JFE 70:295-311): the currency/valuation MOTIVE -- equity is the acquisition currency, so an overvalued bidder has an incentive to keep its price high to pay with stock. Cite as VALUATION, NEVER as tone. (evidence IDs prefixed SV)
- louis2004 (Louis 2004, JFE 74:121-148): pre-deal EARNINGS behavior -- bidders overstate earnings in the quarter before a stock-swap announcement. Cite as EARNINGS-NUMBER management at the genre level, NEVER as tone. (evidence IDs prefixed LO)
- thewissen2024 (SSRN preprint): the TONE leg (our own axis), a supplementary one-clause pointer only; its verbatim anchor already lives in the current chain. Do NOT lean on it for the motive, and it carries no ev_id here.`

// ===================== output contracts (schema-forced; no free prose) =====================
const ACTIONS = ['add', 're-derive', 'reword', 'demote', 'relocate', 'delete']
const SOURCES = ['shleifer_vishny2003', 'louis2004', 'thewissen2024', 'internal', 'none']

const CHANGE_ITEM = {
  type: 'object', additionalProperties: false,
  required: ['subsection', 'paragraph', 'target_prop_id', 'action', 'new_prop_id', 'statement', 'role_in_paragraph', 'source', 'ev_ids', 'rationale'],
  properties: {
    subsection: { type: 'string' },         // e.g. "2.1"
    paragraph: { type: 'string' },           // the paragraph key, e.g. "P5"
    target_prop_id: { type: 'string' },      // the existing prop this modifies, or "NEW"
    action: { type: 'string', enum: ACTIONS },
    new_prop_id: { type: 'string' },         // proposed id for the new/changed prop, e.g. "P5.2"
    statement: { type: 'string' },           // the proposed proposition text (one or two sentences)
    role_in_paragraph: { type: 'string' },
    source: { type: 'string', enum: SOURCES },
    ev_ids: { type: 'array', items: { type: 'string' } },  // evidence IDs from EVIDENCE; [] only for internal/none/thewissen
    rationale: { type: 'string' },           // why this change, tied to the masking motivation + honesty floor
  },
}
const LOGIC_ITEM = {
  type: 'object', additionalProperties: false,
  required: ['subsection', 'link', 'change', 'rationale'],
  properties: {
    subsection: { type: 'string' },
    link: { type: 'string' },                // "spine" or a logic_chain_validated key (e.g. "P4_necessity")
    change: { type: 'string' },              // the proposed new text for that link
    rationale: { type: 'string' },
  },
}
const PANEL1_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['changes', 'chain_logic_updates', 'honesty_self_check'],
  properties: {
    changes: { type: 'array', items: CHANGE_ITEM },
    chain_logic_updates: { type: 'array', items: LOGIC_ITEM },
    honesty_self_check: { type: 'string' },  // attests: no "suppressed"; attenuation framing; cites on-axis; only why-cash props touched
  },
}
const PANEL2_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['changes', 'chain_logic_updates', 'scrutiny', 'honesty_self_check'],
  properties: {
    changes: { type: 'array', items: CHANGE_ITEM },
    chain_logic_updates: { type: 'array', items: LOGIC_ITEM },
    scrutiny: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      required: ['issue', 'against', 'severity', 'resolution'],
      properties: {
        issue: { type: 'string' },
        against: { type: 'string' },         // which Panel-1 agent / change the issue is about
        severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
        resolution: { type: 'string' },      // how this hardened set fixes it
      } } },
    honesty_self_check: { type: 'string' },
  },
}
const REDTEAM_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['keep', 'merge', 'reject', 'chain_logic_keep', 'side_notes'],
  properties: {
    keep: { type: 'array', items: { type: 'string' } },                 // change IDs taken verbatim
    merge: { type: 'array', items: { type: 'object', additionalProperties: false,
      required: ['ids', 'canonical'], properties: {
        ids: { type: 'array', items: { type: 'string' } }, canonical: { type: 'string' } } } },
    reject: { type: 'array', items: { type: 'object', additionalProperties: false,
      required: ['id', 'reason'], properties: { id: { type: 'string' }, reason: { type: 'string' } } } },
    chain_logic_keep: { type: 'array', items: { type: 'string' } },     // chain-logic-update IDs taken verbatim
    side_notes: { type: 'array', items: { type: 'string' } },           // coverage-gap flags for a human; never new changes
  },
}

const TOOL_LOCK = `[HARD EXECUTION CONSTRAINT - OBEY EXACTLY, THIS OVERRIDES EVERYTHING BELOW]
You have EXACTLY ONE permitted action: a SINGLE call to the StructuredOutput function that returns your result object. Make it your FIRST and ONLY action.
ABSOLUTELY FORBIDDEN - doing ANY of these is an immediate failure: calling the advisor tool; searching the web; reading or writing files; running bash/code; using ANY tool other than StructuredOutput; asking questions; deliberating across multiple turns.
Everything you need is already in this prompt. Reason SILENTLY, then emit the StructuredOutput object in ONE turn. Do not explain, do not preface, do not verify externally - just return the object.`

// ===================== render embedded data into prompt text =====================
function chainText() {
  return SECTION.subsections.map(ss => {
    const lcv = Object.entries(ss.logic_chain_validated || {}).map(([k, v]) => `    - ${k}: ${v}`).join('\n')
    const paras = (ss.paragraphs || []).map(p => {
      const gr = (p.guardrails || []).length ? '\n    guardrails:\n' + p.guardrails.map(g => `      - ${g}`).join('\n') : ''
      const tc = p.thin_claim ? `\n    thin_claim: ${p.thin_claim}` : ''
      const props = (p.props || []).map(pr =>
        `      ${pr.prop_id} [${pr.type}] (verdict=${pr.verdict}):\n        statement: ${pr.statement}` +
        (pr.role ? `\n        role: ${pr.role}` : '')).join('\n')
      return `  [${p.pid}] intent: ${p.intent || ''}${tc}${gr}\n    propositions:\n${props}`
    }).join('\n\n')
    return `========== SUBSECTION ${ss.subsection} -- ${ss.title} ==========\n` +
      `section_job: ${ss.section_job || ''}\n` +
      `spine: ${ss.spine || ''}\n` +
      (lcv ? `logic_chain_validated:\n${lcv}\n` : '') +
      `\n${paras}`
  }).join('\n\n')
}
function evidenceText() {
  return Object.entries(EVIDENCE).map(([id, e]) =>
    `  ${id}  [${e.cite}, p.${e.page}, sec ${e.section}]\n    "${e.text}"`).join('\n')
}
const SHARED_INPUTS = () => `===== LOCKED DECISION =====\n${MASKING_DECISION}\n\n${HONESTY_FLOOR}\n\n${CITE_STACK}\n\n` +
  `===== EVIDENCE POOL (cite by ev_id; NEVER retype a quote) =====\n${evidenceText()}\n\n` +
  `===== CURRENT PROPOSITION CHAIN (section ${SECTION.section}) =====\n${chainText()}`

// ===================== PANEL-1: 3 identical-task prompts, heavily paraphrased; NO examples =====================
function panel1Prompt(version) {
  const body = {
    1: `You are a thesis-argument analyst. The project has just locked a NEW reason for why the measured language run-up should concentrate in CASH acquisitions (the masking asymmetry, stated under LOCKED DECISION). The proposition chain below still rests on an OLDER reason for singling out cash. Your task is to redesign the chain so it carries the new reason instead.
Decide for yourself, from the chain and the locked decision, exactly which propositions establish or depend on the why-cash motivation, and rework ONLY those. For each, choose the right move -- add a proposition, re-derive it, reword it, demote it, relocate it, or delete it -- so the argument now flows from the masking asymmetry. Leave every proposition that is not part of the why-cash motivation exactly as it stands; most of the chain is untouched. Hunt down every place the old motivation does work, including any wording (for instance the term used for the stock comparison) that quietly carries identification weight.
Ground each change: name its source from the cite stack on the correct axis, attach the supporting evidence by its ev_id (never retype a quote), and give a rationale that ties the change to the masking motivation and shows it respects the honesty floor. Also propose any needed edits to the section spine or the named logic links. Do not write final prose.`,
    2: `Act as a referee of this section's logical chain. A new motivation for the cash focus has been fixed (the masking asymmetry under LOCKED DECISION); the propositions below were built on a different, earlier motivation. Convert the chain so the cash focus is justified by the new motivation.
Work out yourself which propositions carry the why-cash reasoning -- and which merely lean on it -- and change only those. Pick the appropriate operation per proposition (introduce, re-derive, rephrase, downgrade, move, or remove) so the chain reads coherently start to finish under the masking account. Anything outside the why-cash motivation must remain verbatim; the redesign is surgical. Be thorough about locating the old reasoning wherever it hides, including any single word that does identification work in a proposition's claim.
Every change must be evidenced: cite the proper source on its proper axis, reference the backing quote by ev_id only (do not transcribe it), and justify the change against the masking motivation while honouring the honesty floor. Where the spine or a named logic link needs updating, propose that too. Do not produce final prose.`,
    3: `You are reverse-engineering and repairing a section's argument. The thesis now commits to a specific account of why the language run-up should be concentrated in CASH deals -- the masking asymmetry given under LOCKED DECISION -- but the chain below was written around an older account. Re-engineer the chain to run on the new account.
Determine independently which propositions do the why-cash work, then redesign just those, selecting for each the fitting action (add, re-derive, reword, demote, relocate, or delete) so the whole chain coheres under the masking story. Do not disturb any proposition that is not part of the why-cash motivation -- the great majority stay as written. Search out every trace of the old motivation, including any terminology that silently performs identification within a claim.
Support each modification with evidence: assign the right cite on the right axis, point to the proof by ev_id without ever rewriting the quote, and explain the change in terms of the masking motivation and the honesty floor. Add any spine or named-logic-link revisions the redesign requires. Final prose is out of scope.`,
  }[version]
  return `${TOOL_LOCK}\n\n${body}\n\n${SHARED_INPUTS()}\n\n===== RETURN =====\nReturn your redesign via the structured tool. Your returned object IS the data, not a message. Only propose changes to propositions that carry the why-cash motivation; cite evidence by ev_id; keep final prose blocked.`
}

// ===================== PANEL-2: 3 paraphrased; damage-red-team the 3 Panel-1 sets + emit one hardened set =====================
function panel2Prompt(version, p1) {
  const proposals = p1.map((r, i) => `----- PANEL-1 AGENT ${i + 1} -----\n${JSON.stringify(r, null, 1)}`).join('\n\n')
  const body = {
    1: `You are a hardening reviewer. Three analysts each independently proposed how to swap this section's why-cash motivation over to the masking asymmetry; their change-sets are below. Produce ONE corrected, hardened change-set of your own by scrutinising all three.
Check every proposed change for: (a) any breach of the honesty floor -- above all the faintest hint that the stock effect is "suppressed" or pushed below baseline (the framing must be attenuation, with the observed gap being cash rising); (b) a cite used off its axis (valuation motive vs earnings behaviour vs tone); (c) evidence that does not actually support the claim it is attached to; (d) damage to the chain -- confirm that NO proposition outside the why-cash motivation is altered and that the new propositions contradict nothing before or after them; (e) gaps -- every place the old motivation appears must be handled, including terminology that does identification work. Keep what is sound, repair what is weak, discard what is wrong, and add anything all three missed. Record each finding in the scrutiny log. Reference evidence by ev_id only; write no final prose.`,
    2: `Serve as the quality gate over three independent redesigns of this section's why-cash motivation (below), each shifting it onto the masking asymmetry. Your output is a single, stronger change-set built by interrogating all three.
Interrogate each change on five fronts: honesty-floor safety -- reject any wording implying the stock effect was suppressed or driven under baseline, since the licensed reading is attenuation and the measured gap is cash climbing; cite-axis correctness -- valuation, earnings, and tone must not be conflated; evidence fit -- every ev_id must genuinely back its claim; structural safety -- verify nothing beyond the why-cash propositions is touched and that additions cohere with the rest of the chain; and completeness -- no residue of the old motivation is left behind, including load-bearing single words. Retain the good, mend the shaky, drop the unsound, and supply whatever the trio overlooked. Log every issue you act on. Cite evidence only by ev_id, and leave final prose blocked.`,
    3: `You are the adversarial checker for three proposed rewrites of this section's why-cash motivation onto the masking asymmetry (shown below). Deliver one hardened change-set after stress-testing all three.
Stress-test each proposed change against: honesty-floor compliance -- the single most important trap is any suggestion the stock effect is "suppressed" or pressed below its baseline, when the only sanctioned framing is attenuation and the visible gap is cash rising; correct cite axis -- keep valuation, earnings, and tone strictly separate; sound evidence -- each ev_id must truly support its proposition; no collateral damage -- ensure not one proposition outside the why-cash motivation is changed and that new material is consistent up and down the chain; and full coverage -- every appearance of the superseded motivation, down to a single identification-bearing word, is addressed. Preserve the solid, fix the fragile, cut the broken, and add what the three failed to. Capture each issue in your scrutiny log. Use ev_id references for all evidence; do not write final prose.`,
  }[version]
  return `${TOOL_LOCK}\n\n${body}\n\n${SHARED_INPUTS()}\n\n===== THE THREE PANEL-1 PROPOSALS TO SCRUTINISE =====\n${proposals}\n\n===== RETURN =====\nReturn your hardened change-set + scrutiny log via the structured tool. Your returned object IS the data. Touch only why-cash propositions; cite by ev_id; final prose stays blocked.`
}

// ===================== RED-TEAM: synthesize the 3 hardened sets BY REFERENCE =====================
function redteamPrompt(pool, logicPool) {
  return `${TOOL_LOCK}

You are the RED TEAM for this section's why-cash redesign. Three reviewers each produced a hardened change-set; every individual change and every chain-logic update below carries an ID. The evidence behind each change has fixed ev_ids already -- do NOT re-check quotes.

Your job is SCRUTINISE + SYNTHESISE, BY REFERENCE ONLY. You never rewrite a change; you emit decisions that reference IDs, and the main loop copies the referenced changes verbatim.

SCRUTINISE -- reject a change (reject{id,reason}) when ANY of these holds:
- it breaches the honesty floor (implies the stock effect is suppressed or pushed below baseline; the only allowed framing is attenuation, observed gap = cash rising);
- it uses a cite off its axis (valuation motive vs earnings behaviour vs tone conflated);
- it alters or damages a proposition that is NOT part of the why-cash motivation;
- it is incoherent with the rest of the chain, or internally vacuous.

SYNTHESISE -- across the three reviewers, changes that make the SAME edit to the SAME proposition are duplicates: group their IDs in merge{ids,canonical} and name the ONE canonical to keep (tiebreak: stronger/cleaner evidence, then cleaner honesty-floor compliance, then better fit with the surrounding chain). Genuinely distinct changes each stay on their own in keep.
- keep: change IDs that survive as-is (the deduplicated set that together forms ONE coherent, complete why-cash rewire).
- chain_logic_keep: the chain-logic-update IDs that the kept rewire needs.
- side_notes: ONLY coverage-gap flags for a human (e.g. a place the old motivation may still linger that no reviewer caught). NEVER new changes.

You invent nothing. Keep the set minimal but complete: enough to carry the masking motivation end to end, nothing redundant. The LOCKED DECISION, HONESTY FLOOR, CITE STACK, EVIDENCE POOL, and the CURRENT chain are all provided below -- use them to ground every honesty-floor, cite-axis, evidence-misuse, and chain-damage rejection; each change's ev_ids point into the EVIDENCE POOL.

${SHARED_INPUTS()}

===== CHANGES (id, source-agent, content) =====
${JSON.stringify(pool, null, 1)}

===== CHAIN-LOGIC UPDATES (id, source-agent, content) =====
${JSON.stringify(logicPool, null, 1)}

Return your decisions via the structured tool.`
}

// ===================== pipeline (one section; genuine barriers between layers) =====================
phase('Panel-1')
log(`[input] section ${SECTION.section}: ${SECTION.subsections.length} subsections, ` +
  `${SECTION.subsections.reduce((n, s) => n + (s.paragraphs || []).length, 0)} paragraphs, ` +
  `${SECTION.subsections.reduce((n, s) => n + (s.paragraphs || []).reduce((m, p) => m + (p.props || []).length, 0), 0)} props; ` +
  `${Object.keys(EVIDENCE).length} evidence quotes`)

const p1 = (await parallel([1, 2, 3].map(v => () =>
  agent(panel1Prompt(v), { schema: PANEL1_SCHEMA, phase: 'Panel-1', label: `s${SECTION.section}/panel1-${v}` }))))
  .map(r => r || { changes: [], chain_logic_updates: [], honesty_self_check: 'NULL (agent failed)' })
log(`[panel-1] proposals: ${p1.map(r => (r.changes || []).length).join(', ')} changes`)

phase('Panel-2')
const p2 = (await parallel([1, 2, 3].map(v => () =>
  agent(panel2Prompt(v, p1), { schema: PANEL2_SCHEMA, phase: 'Panel-2', label: `s${SECTION.section}/panel2-${v}` }))))
  .map(r => r || { changes: [], chain_logic_updates: [], scrutiny: [], honesty_self_check: 'NULL (agent failed)' })
log(`[panel-2] hardened: ${p2.map(r => (r.changes || []).length).join(', ')} changes`)

// assign stable IDs across the Panel-2 pool for by-reference synthesis
const pool = [], logicPool = []
p2.forEach((r, ai) => {
  ;(r.changes || []).forEach((c, ci) => pool.push({ id: `p2-${ai + 1}-c${ci + 1}`, agent: ai + 1, ...c }))
  ;(r.chain_logic_updates || []).forEach((l, li) => logicPool.push({ id: `p2-${ai + 1}-l${li + 1}`, agent: ai + 1, ...l }))
})

phase('Red-team')
let redteam = null
if (pool.length > 0) {
  redteam = await agent(redteamPrompt(pool, logicPool), { schema: REDTEAM_SCHEMA, phase: 'Red-team', label: `s${SECTION.section}/redteam` })
}
let final_changes = [], final_logic = [], note = 'ok'
if (!redteam) {
  // degrade: no red team -> union of Panel-2 changes, flagged for manual synthesis
  final_changes = pool
  final_logic = logicPool
  note = pool.length ? 'redteam_failed_degraded_to_panel2_union' : 'no_panel2_changes'
  log(`[red-team] NULL or skipped -> degrading to Panel-2 union (${pool.length} changes); FLAG manual synthesis`)
} else {
  const byId = {}; pool.forEach(c => byId[c.id] = c)
  const byLid = {}; logicPool.forEach(l => byLid[l.id] = l)
  const rejectIds = new Set((redteam.reject || []).map(r => r.id))
  const keepIds = new Set((redteam.keep || []).filter(id => !rejectIds.has(id)))
  ;(redteam.merge || []).forEach(m => { if (m.canonical && !rejectIds.has(m.canonical)) keepIds.add(m.canonical) })
  final_changes = [...keepIds].map(id => byId[id]).filter(Boolean)
  final_logic = (redteam.chain_logic_keep || []).map(id => byLid[id]).filter(Boolean)
  if (final_changes.length === 0 && pool.length > 0) {
    final_changes = pool; final_logic = logicPool; note = 'redteam_kept_zero_degraded_to_union'
    log(`[red-team] kept 0 of ${pool.length} -> degrading to union; FLAG`)
  } else {
    log(`[red-team] final: ${final_changes.length} changes, ${final_logic.length} logic updates kept`)
  }
}

return {
  section: SECTION.section,
  subsections: SECTION.subsections.map(s => s.subsection),
  panel1: p1, panel2: p2,
  pool, logicPool,
  redteam, final_changes, final_logic, note,
}
