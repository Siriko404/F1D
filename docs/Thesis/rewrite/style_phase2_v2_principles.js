export const meta = {
  name: 'style-phase2-principles',
  description: 'Phase-2 v2: extract WRITING-STYLE PRINCIPLES per section TYPE, learned DIRECTLY from the corporate-finance exemplar papers (never our prose). Each type runs fully independently - NO cross-type step, ever. Per type: 3 panel agents with IDENTICAL task but HEAVILY paraphrased instructions (the only source of panel neurodiversity; zero content examples, which would anchor them) discover the style principles the papers SHARE, each with verbatim cross-paper evidence. A deterministic in-script gate keeps only principles whose quotes are verbatim in their CLAIMED paper and span >=2 distinct papers, and computes the exact paragraph pointer for the red team. ONE red team then SCRUTINIZES (drops false/absolute/non-style/vague) and SYNTHESIZES (merges duplicate devices) BY REFERENCE - it never re-authors. JS materializes the survivors verbatim into that type rulebook.',
  phases: [
    { title: 'Panel',   detail: '3 paraphrased agents (identical task) -> style principles + verbatim cross-paper evidence' },
    { title: 'Redteam', detail: 'scrutinize + merge-by-reference on gate-clean principles' },
  ],
}

// TYPES = [ { type, exemplars:[ {paper, venue, head, paragraphs[]} ] } ]   (papers ONLY; the `ours` half is stripped by the build step)
// Embedded by an EXTERNAL build step (_phase2_v2/build_v2.py) that reads docs/papers/style_exemplars/bundles/<type>.json.
// The harness NEVER reads files at runtime (Workflow tool has no filesystem access).
const TYPES = [] // __TYPES_ANCHOR__

// optional run knob (default batch of 2 types to respect rate limits)
if (typeof args === 'string') { try { args = JSON.parse(args) } catch (e) { args = {} } }
if (!args || typeof args !== 'object') args = {}

// ---------- output contracts (forced via schema; no free prose) ----------
const PRINCIPLES_SCHEMA = {
  type: 'object', required: ['principles'], additionalProperties: false,
  properties: { principles: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    required: ['device', 'principle', 'why', 'evidence'],
    properties: {
      device: { type: 'string' },        // short name of the style device
      principle: { type: 'string' },     // the rule, stated as a generalization of the evidence
      why: { type: 'string' },           // why it makes the writing effective
      evidence: { type: 'array', minItems: 2, items: {
        type: 'object', required: ['paper', 'quote'], additionalProperties: false,
        properties: { paper: { type: 'string' }, quote: { type: 'string' } } } },
    } } } },
}
const REDTEAM_SCHEMA = {
  type: 'object', required: ['keep', 'merge', 'reject', 'side_notes'], additionalProperties: false,
  properties: {
    keep:  { type: 'array', items: { type: 'string' } },
    merge: { type: 'array', items: { type: 'object', required: ['ids', 'canonical'], additionalProperties: false,
             properties: { ids: { type: 'array', items: { type: 'string' } }, canonical: { type: 'string' } } } },
    reject:{ type: 'array', items: { type: 'object', required: ['id', 'reason'], additionalProperties: false,
             properties: { id: { type: 'string' }, reason: { type: 'string' } } } },
    side_notes: { type: 'array', items: { type: 'string' } },
  },
}

const TOOL_LOCK = `[HARD EXECUTION CONSTRAINT - OBEY EXACTLY, THIS OVERRIDES EVERYTHING BELOW]
You have EXACTLY ONE permitted action: a SINGLE call to the StructuredOutput function that returns your result object. Make it your FIRST and ONLY action.
ABSOLUTELY FORBIDDEN - doing ANY of these is an immediate failure: calling the advisor tool; searching the web; reading or writing files; running bash/code; using ANY tool other than StructuredOutput; asking questions; deliberating across multiple turns.
Everything you need is already in this prompt. Reason SILENTLY, then emit the StructuredOutput object in ONE turn. Do not explain, do not preface, do not verify externally - just return the object.`

// ---------- shared context block (papers only, paragraphs numbered) ----------
function buildContext(T) {
  return T.exemplars.map(s =>
    `[${s.paper} | ${s.venue} | "${s.head}"]\n` +
    s.paragraphs.map((p, j) => `  (p${j}) ${p}`).join('\n')).join('\n\n')
}

// ---------- PANEL: 3 IDENTICAL-task prompts, HEAVILY paraphrased (the only diversity; NO examples) ----------
// The hard clauses (open-discovery / style-only / grounded-no-invented-threshold / verbatim cross-paper evidence)
// are SEMANTICALLY IDENTICAL across all three - only the voice differs.
function panelPrompt(version, type, ctx) {
  const body = {
    1: `You are a writing-style analyst. Below are the ${type} passages from several published corporate-finance papers. Your job: identify the style principles these papers SHARE - the recurring ways of writing a ${type} that make the prose work for a reader.
Work without any checklist: look at the writing at every level - word choice, sentence construction, how sentences combine, how each paragraph is built, how the larger argument is staged - and capture the MAJOR, load-bearing principles - the handful that most define how these papers write a ${type}. Consolidate related observations under one principle; do not split every micro-variation into its own rule. Aim for a short, high-level list, not an exhaustive catalogue.
Capture STYLE, never substance: a principle is about HOW these papers write, not WHAT they find or claim. Set aside their results, data, and domain content entirely.
Stay grounded: every principle must be one the passages genuinely exhibit, stated as a generalization of what you see. Never assert a numeric threshold - a word count, a sentence length, a ratio - that the passages do not themselves establish.
Evidence is mandatory and must be exact: each principle carries at least two quotes copied character-for-character from the passages above, drawn from at least two DIFFERENT papers, with the source paper named on each quote. A quote that is not an exact copy is discarded automatically, so transcribe precisely.
Give, per distinct principle: a short device name, the principle stated plainly, why it makes the writing effective, and its evidence.`,
    2: `Read the ${type} passages below - each is the ${type} of a corporate-finance paper. Work out what these writers DO IN COMMON when they craft a ${type}: the shared craft, the repeated moves, the habits of construction that give this kind of section its characteristic, readable form.
Do not work from a fixed list. Examine the prose top to bottom - diction, the shape of individual sentences, the way sentences are joined, paragraph architecture, the sequencing of the whole - and name the FEW principles that genuinely characterize this register. Fold closely-related devices together under one principle rather than itemizing every surface variation; a tight set of high-level principles beats a long catalogue of fine-grained ones.
Keep strictly to STYLE. You are describing the MANNER of writing, not the content - findings, numbers, and subject matter are out of scope.
Anchor every claim in the text: state each principle as a pattern the passages actually display; do not invent a fixed measurement - length caps, counts, proportions - the passages never set.
Prove each one: every principle needs two or more quotations lifted verbatim, exactly as written, from two or more SEPARATE papers, each tagged with the paper it came from. Inexact quotes are dropped by an automatic check, so copy them letter-perfect.
For each principle provide: a brief device name, the principle itself, the reason it works on the reader, and the quotes.`,
    3: `Below are ${type} sections from a set of corporate-finance papers. Reverse-engineer the writing: which shared principles of style do these ${type}s follow? You are after the patterns common ACROSS the papers - the recurring authorial choices behind this section type's readable form.
No checklist - discover, do not confirm. Inspect every layer of the writing, from word and sentence up through paragraph and overall arrangement, and distill the SMALL set of principles that most define this section's craft. Group kindred devices into one principle instead of cataloguing every minor variant; prefer a concise list of major principles over exhaustive coverage.
Confine yourself to STYLE - the how, not the what. The papers' claims, evidence, and topic are out of scope; only the writing craft is in scope.
Stay tethered to what is on the page: each principle must be visibly present in the passages and phrased as a generalization of that evidence - never a concocted threshold (no invented word limits, sentence counts, or ratios the text does not itself fix).
Back each principle with proof: at minimum two quotes, reproduced exactly as printed, taken from at least two DISTINCT papers, each labeled with its paper. A quote that is not an exact substring is discarded automatically, so copy with care.
Report, per principle: a short device label, the stated principle, why it is effective, and the supporting quotes.`,
  }[version]
  return `${TOOL_LOCK}\n\n${body}\n\n===== ${type.toUpperCase()} PASSAGES (corporate-finance papers) =====\n${ctx}\n\n===== RETURN =====\nReturn your principles via the structured tool. Your returned object IS the data, not a message.`
}

// ---------- RED TEAM: scrutinize + merge BY REFERENCE (its own role; gets the FULL evidence) ----------
function redteamPrompt(type, clean) {
  return `${TOOL_LOCK}

You are the RED TEAM for the "${type}" writing-style principles. Three panel agents independently produced the principles below; each carries an ID. Every quote has ALREADY been verified verbatim by a script and located to its paper and paragraph - do NOT re-check quotes.

Your job is SCRUTINIZE + SYNTHESIZE, BY REFERENCE ONLY. You never write or reword a principle; you emit decisions that reference IDs.

SCRUTINIZE - reject a principle when ANY of these holds:
- its quotes do not actually exhibit the device it names (the evidence does not show the claimed pattern);
- it asserts an absolute threshold - a fixed word count, sentence length, or ratio - that its evidence does not establish;
- it describes content, findings, or subject matter rather than writing style;
- it is too vague to act on.
Put each rejected ID in reject{id,reason}.

SYNTHESIZE - across the three agents, principles that name the SAME underlying device are duplicates: group their IDs and name ONE canonical to keep (tiebreak: the one with more / more authoritative evidence - published JF, JAR, QJE outweigh working papers). Where two principles are genuinely DISTINCT devices, keep them separate rather than folding them together.
- keep: IDs that survive as-is.
- merge: [{ids, canonical}].
- side_notes: ONLY coverage-gap flags for a human (e.g. a level of the writing all three agents left unexamined). NEVER new principles.

You invent nothing. The main loop copies the kept/canonical principles verbatim.

===== PRINCIPLES =====
${JSON.stringify(clean.map(f => ({ id: f.id, agent: f.agent, device: f.device, principle: f.principle, why: f.why, evidence: f.evidence })), null, 1)}

Return decisions via the structured tool.`
}

// ---------- deterministic in-script gate (pure JS, no LLM) ----------
// forgiving normalization: fold unicode quotes/dashes to ASCII, drop punctuation + stray
// digit-runs (inlined footnote markers), collapse whitespace. Both sides normalized identically.
function norm(s) {
  return (s || '')
    .toLowerCase()
    .replace(/[\u2018\u2019\u201b\u2032]/g, "'")   // fold unicode single quotes/prime
    .replace(/[\u201c\u201d\u2033]/g, '"')          // fold unicode double quotes
    .replace(/[\u2010-\u2015\u2212]/g, '-')         // fold unicode dashes/minus
    .replace(/[^\w]+/g, ' ')      // punctuation -> space
    .replace(/\b\d+\b/g, ' ')     // drop standalone digit runs (footnote numbers, stray refs)
    .replace(/\s+/g, ' ')
    .trim()
}
function isSub(q, hay) { const n = norm(q); return n.length > 0 && norm(hay).includes(n) }

// ================= per-type pipeline (fully independent) =================
async function runType(T) {
  const ctx = buildContext(T)
  const raw = await parallel([1, 2, 3].map(v => () =>
    agent(panelPrompt(v, T.type, ctx), { schema: PRINCIPLES_SCHEMA, phase: `Panel:${T.type}`, label: `${T.type}/panel-${v}` })))

  const byPaper = {}   // accumulate ALL paragraphs per paper (a paper appears as many section-entries; don't overwrite)
  for (const s of T.exemplars) (byPaper[s.paper] = byPaper[s.paper] || []).push(...(s.paragraphs || []))

  const clean = [], rejected = []
  raw.forEach((r, ai) => (r && r.principles || []).forEach((pr, pi) => {
    const id = `a${ai + 1}-p${pi + 1}`
    const ev = pr.evidence || []
    // GATE: each quote must be verbatim in its CLAIMED paper (no all-papers fallback, so "2 papers"
    // cannot be faked by a mislabel); compute the true paragraph index as a reliable locator.
    const located = []
    let allMatch = ev.length > 0
    for (const q of ev) {
      const ps = byPaper[q.paper]
      const idx = ps ? ps.findIndex(p => isSub(q.quote, p)) : -1
      if (idx < 0) { allMatch = false; break }
      located.push({ paper: q.paper, para_idx: idx, quote: q.quote })
    }
    const distinctPapers = new Set(located.map(l => l.paper))
    const cardOK = ev.length >= 2 && distinctPapers.size >= 2
    if (allMatch && cardOK) clean.push({ id, agent: ai + 1, device: pr.device, principle: pr.principle, why: pr.why, evidence: located })
    else rejected.push({ id, reason: !allMatch ? 'quote_not_verbatim_in_claimed_paper' : 'need_2_distinct_papers' })
  }))
  log(`[${T.type}] ${clean.length} passed gate, ${rejected.length} rejected`)
  if (clean.length === 0) return { type: T.type, principles: [], gate_rejected: rejected, redteam_rejected: [], merges: [], unhandled: [], side_notes: [], note: 'no principles survived the gate' }

  const decisions = await agent(redteamPrompt(T.type, clean), { schema: REDTEAM_SCHEMA, phase: `Redteam:${T.type}`, label: `${T.type}/redteam` })
  if (!decisions) {   // redteam died (timeout/error) -> degrade gracefully, never crash the type
    log(`[${T.type}] redteam returned NULL -> degrading to ${clean.length} gate-clean principles (no merge/verify)`)
    return { type: T.type, principles: clean, gate_rejected: rejected, redteam_rejected: [], merges: [], unhandled: [], side_notes: ['REDTEAM FAILED (null) - principles are raw gate-clean, NOT deduped/verified; re-run this type'], note: 'redteam_failed' }
  }
  const byId = {}; clean.forEach(f => { byId[f.id] = f })
  const rejectIds = new Set((decisions.reject || []).map(r => r.id))
  const keepIds = new Set((decisions.keep || []).filter(id => !rejectIds.has(id)))
  ;(decisions.merge || []).forEach(m => { if (m.canonical && !rejectIds.has(m.canonical)) keepIds.add(m.canonical) })
  let principles = [...keepIds].map(id => byId[id]).filter(Boolean)
  if (principles.length === 0 && clean.length > 0) {   // keeps-0 -> degrade (the Phase-2 Bug-3 fix)
    log(`[${T.type}] red-team kept 0 of ${clean.length} (decision IDs unmatched) -> degrading to gate-clean`)
    return { type: T.type, principles: clean, gate_rejected: rejected, redteam_rejected: decisions.reject || [], merges: decisions.merge || [], unhandled: [], side_notes: (decisions.side_notes || []).concat(['RED-TEAM kept 0 - degraded to gate-clean (un-deduped); re-run this type']), note: 'redteam_zero_degraded' }
  }
  const handled = new Set([...keepIds, ...rejectIds])
  ;(decisions.merge || []).forEach(m => (m.ids || []).forEach(id => handled.add(id)))
  const unhandled = clean.map(f => f.id).filter(id => !handled.has(id))
  log(`[${T.type}] ${principles.length} principles kept; ${rejected.length} gate-rejected; ${(decisions.reject || []).length} redteam-rejected`)
  return { type: T.type, principles, gate_rejected: rejected, redteam_rejected: decisions.reject || [], merges: decisions.merge || [], unhandled, side_notes: decisions.side_notes || [], note: 'ok' }
}

// ================= body: independent types, batched to respect rate limits =================
phase('Panel')
log('[input] ' + TYPES.map(T => `${T.type}:${T.exemplars.length}papers/${T.exemplars.reduce((n, s) => n + (s.paragraphs || []).length, 0)}paras`).join('  '))
const MAXT = Math.max(1, args.maxTypes || 2)
const results = []
for (let i = 0; i < TYPES.length; i += MAXT) {
  const batch = await parallel(TYPES.slice(i, i + MAXT).map(T => () => runType(T)))
  results.push(...batch.filter(Boolean))
}
return { types: TYPES.map(t => t.type), results }
