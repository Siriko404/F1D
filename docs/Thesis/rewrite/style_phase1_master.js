export const meta = {
  name: 'style-phase1-wave',
  description: 'Phase-1 style ANALYSIS for a WAVE of section types (each runs concurrently): 3 paraphrased panel agents discover where our prose is needlessly more complex than the corp-fin exemplars, a deterministic in-script gate drops any finding whose quotes are not verbatim, then a redteam verifies+merges by reference (never re-authors). Analysis only — no rewriting.',
  phases: [
    { title: 'Panel',   detail: '3 identical-task, paraphrased agents → evidence-backed findings' },
    { title: 'Redteam', detail: 'verify + merge-by-reference on gate-cleaned findings' },
  ],
}

// args = one type bundle: { type, exemplars:[{paper,venue,head,paragraphs[]}], ours:[{ledger,para_id,final_prose,propositions[],guardrails[],number_audit[]}] }

// ---------- output contracts (forced via schema; no free prose) ----------
const FINDINGS_SCHEMA = {
  type: 'object', required: ['findings'], additionalProperties: false,
  properties: { findings: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    required: ['aspect','exemplar_pattern','exemplar_quotes','our_pattern','our_quotes','gap','materiality','guardrail_collision'],
    properties: {
      aspect: { type: 'string' },
      exemplar_pattern: { type: 'string' },
      exemplar_quotes: { type: 'array', minItems: 2, items: {
        type: 'object', required: ['paper','quote'], additionalProperties: false,
        properties: { paper: { type: 'string' }, quote: { type: 'string' } } } },
      our_pattern: { type: 'string' },
      our_quotes: { type: 'array', minItems: 1, items: {
        type: 'object', required: ['para_id','quote'], additionalProperties: false,
        properties: { para_id: { type: 'string' }, quote: { type: 'string' } } } },
      gap: { type: 'string' },
      materiality: { type: 'string', enum: ['major','minor'] },
      guardrail_collision: { type: 'boolean' },   // true = observation sits near load-bearing meaning -> human MUST see
    } } } },
}
const REDTEAM_SCHEMA = {
  type: 'object', required: ['keep','merge','reject','side_notes'], additionalProperties: false,
  properties: {
    keep:  { type: 'array', items: { type: 'string' } },
    merge: { type: 'array', items: { type: 'object', required: ['ids','canonical'], additionalProperties: false,
             properties: { ids: { type: 'array', items: { type: 'string' } }, canonical: { type: 'string' } } } },
    reject:{ type: 'array', items: { type: 'object', required: ['id','reason'], additionalProperties: false,
             properties: { id: { type: 'string' }, reason: { type: 'string' } } } },
    side_notes: { type: 'array', items: { type: 'string' } },
  },
}

// ---------- shared context block (the bundle, formatted) ----------
function buildContext(a) {
  const ex = a.exemplars.map((s, i) =>
    `[EX ${i + 1}] paper=${s.paper} venue=${s.venue} head="${s.head}"\n` +
    s.paragraphs.map(p => `  • ${p}`).join('\n')).join('\n\n')
  const ours = a.ours.map(u =>
    `[OUR ${u.para_id}] (ledger ${u.ledger})\n  PROSE: ${u.final_prose}\n` +
    `  GUARDRAILS — DO NOT TOUCH (load-bearing meaning; if an observation implicates ANY of these, set guardrail_collision=true): ${JSON.stringify(u.guardrails)}`).join('\n\n')
  return { ex, ours }
}

const RULES = `
OBJECTIVE (your yardstick): the SIMPLEST end of the corporate-finance academic register — the supervisor's "a non-specialist could read it" bar. You are looking ONLY for places where OUR prose is needlessly MORE complex than the exemplars. NEVER flag a difference where our prose is already simpler/clearer than an exemplar. When exemplars disagree, weight published journals (JF, JAR, QJE) above working papers.
DESCRIBE ONLY — THIS IS THE LOAD-BEARING RULE. You OBSERVE and NAME where our phrasing is heavier than the exemplars. You do NOT propose a reworded fix, a replacement sentence, or "say it like X". You do NOT assert that two phrasings "mean the same", are "equivalent", or that a change would keep "the claim identical". The rewrite is a SEPARATE, human-gated phase — here you only POINT. (A self-certified "meaning unchanged" is exactly the failure this rule removes.)
GUARDRAILS: each OUR paragraph lists GUARDRAILS = load-bearing meaning (hedges, qualifiers, scoped claims) that must NEVER be touched. If an observation would implicate ANY guardrail, set guardrail_collision=true on that finding (still describe-only — never propose altering it). Otherwise set guardrail_collision=false.
WHAT TO PRODUCE: an OPEN set of findings — discover every aspect of language YOU observe, do not work from a fixed checklist. One finding per distinct difference.
EVIDENCE (mandatory, copied VERBATIM — do not paraphrase a quote): each finding needs >=2 exemplar quotes drawn from >=2 DIFFERENT papers, and >=1 quote from our prose. Copy quotes character-for-character from the text above; a quote that is not an exact substring will be discarded automatically.
HARD LIMITS: STYLE ONLY. Stay strictly within this one section type.
Grade each finding materiality: "major" (heavy/structural complexity) or "minor".`

function panelPrompt(version, type, ctx) {
  const head = {
    1: `You are analyzing the writing STYLE of the "${type}" sections of finance papers. Below are exemplar passages from published/working corporate-finance papers, then our own ${type} prose. Compare them and list every way OUR wording is needlessly more complex than theirs.`,
    2: `Task: study how the exemplar "${type}" passages below are written, then look at our ${type} prose. Wherever our phrasing carries complexity that the exemplars shed, record it. Where do we make the reader work harder than these papers do?`,
    3: `Work through the exemplar "${type}" passages first, then our ${type} paragraphs. Each time our sentence- or paragraph-level phrasing is heavier or denser than the register requires — compared with how the exemplars handle the same job — write it down with proof.`,
  }[version]
  return `${TOOL_LOCK}\n\n${head}\n\n===== EXEMPLARS (how they write "${type}") =====\n${ctx.ex}\n\n===== OUR PROSE ("${type}") =====\n${ctx.ours}\n\n===== INSTRUCTIONS =====${RULES}\n\nReturn findings via the structured tool. Your returned object IS the data, not a message.`
}

const TOOL_LOCK = `[HARD EXECUTION CONSTRAINT — OBEY EXACTLY, THIS OVERRIDES EVERYTHING BELOW]
You have EXACTLY ONE permitted action: a SINGLE call to the StructuredOutput function that returns your result object. Make it your FIRST and ONLY action.
ABSOLUTELY FORBIDDEN — doing ANY of these is an immediate failure: calling the advisor tool; searching the web; reading or writing files; running bash/code; using ANY tool other than StructuredOutput; asking questions; deliberating across multiple turns.
Everything you need is already in this prompt, and every quote is already script-verified. Reason SILENTLY, then emit the StructuredOutput object in ONE turn. Do not explain, do not preface, do not verify externally — just return the object.`

function redteamPrompt(type, clean) {
  return `${TOOL_LOCK}

You are the REDTEAM for the "${type}" style analysis. Three panel agents produced the findings below (IDs assigned). Every quote here has ALREADY been verified verbatim by a script and every finding already meets the cardinality rule — do NOT re-check quotes.

YOUR JOB IS VERIFY + SYNTHESIZE BY REFERENCE ONLY. You do NOT write or reword any finding. You emit decisions that reference finding IDs:
- VERIFY each finding on judgment only: (1) DIRECTION — it must show OUR prose is needlessly MORE complex, not the reverse; (2) the evidence actually supports the stated gap; (3) it is STYLE-only AND DESCRIBE-only — reject any finding that proposes a reword/replacement or asserts two phrasings "mean the same"/"claim identical"; (4) materiality grade is sane. Anything failing -> reject{id,reason}.
- guardrail_collision=true means the observation sits near load-bearing meaning. This is NOT a reason to reject — KEEP such findings (they are the ones a human MUST see); never silently drop them.
- MERGE duplicates/overlaps across the three agents: group their IDs and name ONE canonical ID to keep (tiebreak: the finding with more quotes / journal-weighted quotes). If a merge is DEBATABLE (members target different devices), prefer keeping them SEPARATE over folding.
- keep: IDs that survive as-is.
- side_notes: ONLY segregated under-coverage flags (e.g. "all three stayed at sentence level; paragraph structure unexamined"). These are notes for a human — NEVER new findings.

You invent nothing. The main loop will copy the kept/canonical findings verbatim.

===== FINDINGS =====
${JSON.stringify(clean.map(f => ({ id: f.id, agent: f.agent, aspect: f.aspect, gap: f.gap, materiality: f.materiality, guardrail_collision: f.guardrail_collision, exemplar_quotes: f.exemplar_quotes, our_quotes: f.our_quotes })), null, 1)}

Return decisions via the structured tool.`
}

// ---------- deterministic in-script gate (pure JS, no LLM) ----------
// forgiving normalization: fold unicode quotes/dashes to ASCII, drop punctuation + stray
// digit-runs (inlined footnote markers), collapse whitespace. Both sides normalized identically.
function norm(s) {
  return (s || '')
    .toLowerCase()
    .replace(/[‘’‛′]/g, "'")
    .replace(/[“”″]/g, '"')
    .replace(/[‐-―−]/g, '-')
    .replace(/[^\w]+/g, ' ')      // punctuation -> space
    .replace(/\b\d+\b/g, ' ')     // drop standalone digit runs (footnote numbers, stray refs)
    .replace(/\s+/g, ' ')
    .trim()
}
function isSub(q, hay) { const n = norm(q); return n.length > 0 && norm(hay).includes(n) }

// ================= workflow (multi-type WAVE) =================
const BUNDLES = [] // __BUNDLES_ANCHOR__  (embed_master injects the array of type bundles here)

async function runType(A) {
  const ctx = buildContext(A)
  const raw = await parallel([1, 2, 3].map(v => () =>
    agent(panelPrompt(v, A.type, ctx), { schema: FINDINGS_SCHEMA, phase: `Panel:${A.type}`, label: `${A.type}/panel-${v}` })))

  const exByPaper = {}
  for (const s of A.exemplars) { (exByPaper[s.paper] = exByPaper[s.paper] || []).push(...s.paragraphs) }
  const exAll = Object.values(exByPaper).flat()
  const ourById = {}
  for (const u of A.ours) { ourById[u.para_id] = u.final_prose }
  const ourAll = A.ours.map(u => u.final_prose).join(' \n ')

  const clean = [], rejected = []
  raw.forEach((r, ai) => (r && r.findings || []).forEach((f, fi) => {
    const id = `a${ai + 1}-f${fi + 1}`
    const exQ = f.exemplar_quotes || [], ourQ = f.our_quotes || []
    const papers = new Set(exQ.map(q => q.paper))
    const cardOK = exQ.length >= 2 && papers.size >= 2 && ourQ.length >= 1
    const exOK = exQ.every(q => (exByPaper[q.paper] || []).some(p => isSub(q.quote, p)) || exAll.some(p => isSub(q.quote, p)))
    const ourOK = ourQ.every(q => isSub(q.quote, ourById[q.para_id] || ourAll) || isSub(q.quote, ourAll))
    if (cardOK && exOK && ourOK) clean.push({ id, agent: ai + 1, ...f })
    else rejected.push({ id, reason: !cardOK ? 'cardinality' : (!exOK ? 'exemplar_quote_not_verbatim' : 'our_quote_not_verbatim') })
  }))
  log(`[${A.type}] ${clean.length} passed gate, ${rejected.length} rejected`)
  if (clean.length === 0) return { type: A.type, profile: [], guardrail_collisions: [], side_notes: [], gate_rejected: rejected, redteam_rejected: [], merges: [], unhandled: [], note: 'no findings survived the gate' }

  const decisions = await agent(redteamPrompt(A.type, clean), { schema: REDTEAM_SCHEMA, phase: `Redteam:${A.type}`, label: `${A.type}/redteam` })
  if (!decisions) {   // redteam died (timeout/error) -> degrade gracefully, never crash the whole type
    log(`[${A.type}] redteam returned NULL (timeout/error) -> degrading to ${clean.length} gate-clean findings (no merge/verify)`)
    return { type: A.type, profile: clean, guardrail_collisions: clean.filter(f => f.guardrail_collision).map(f => f.id), side_notes: ['REDTEAM FAILED (null) — profile is raw gate-clean findings, NOT deduped/verified; re-run this type'], gate_rejected: rejected, redteam_rejected: [], merges: [], unhandled: [], note: 'redteam_failed' }
  }
  const byId = {}; clean.forEach(f => { byId[f.id] = f })
  const rejectIds = new Set((decisions.reject || []).map(r => r.id))
  const keepIds = new Set((decisions.keep || []).filter(id => !rejectIds.has(id)))
  ;(decisions.merge || []).forEach(m => { if (m.canonical && !rejectIds.has(m.canonical)) keepIds.add(m.canonical) })
  const profile = [...keepIds].map(id => byId[id]).filter(Boolean)
  const handled = new Set([...keepIds, ...rejectIds])
  ;(decisions.merge || []).forEach(m => (m.ids || []).forEach(id => handled.add(id)))
  const unhandled = clean.map(f => f.id).filter(id => !handled.has(id))
  const guardrail_collisions = profile.filter(f => f.guardrail_collision).map(f => f.id)
  log(`[${A.type}] profile ${profile.length} kept; ${guardrail_collisions.length} guardrail-flagged; ${rejected.length} gate-rejected`)
  return { type: A.type, profile, guardrail_collisions, side_notes: decisions.side_notes || [], gate_rejected: rejected, redteam_rejected: decisions.reject || [], merges: decisions.merge || [], unhandled }
}

phase('Wave')
const results = await parallel(BUNDLES.map(A => () => runType(A)))
return { wave: BUNDLES.map(b => b.type), results }
