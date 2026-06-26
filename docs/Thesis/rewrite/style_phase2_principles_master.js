export const meta = {
  name: 'phase2-principles-harness',
  description: "Phase-2: turn each writing-TYPE's Phase-1 style findings into a minimal, exemplar-anchored writing-principle rulebook for THAT type. Writes NO thesis prose. TWO agent layers, run PER TYPE, fully independent (NO global / cross-type step, ever): LAYER 1 = neurodiverse PANEL of 3 paraphrased EXTRACT agents (findings -> candidate principles) -> deterministic JS gate (exemplar-anchor verbatim + no foreign number, scaffolding-refs exempt); LAYER 2 = ONE RED-TEAM agent that SCRUTINIZES (refute fabricated/absolute/unfaithful, by reference) AND SYNTHESIZES (merge near-duplicates -> the minimal final rulebook for the type). JS materialize writes each type its own rulebook. Types run in capped-concurrency batches (args.maxProfiles, default 2 -> peak ~6 agents) to respect the server rate-limit scar. Every agent TOOL_LOCK + forced StructuredOutput; the red-team is describe-only / by-reference; null-degrade never crashes. Each rulebook = ONLY its own type's findings (cross-type dedup is forbidden; a universal rule naturally recurs because each type's findings surface it).",
  phases: [
    { title: 'Extract',  detail: 'LAYER 1: neurodiverse panel of 3 agents per type -> candidate principles' },
    { title: 'RedTeam',  detail: 'LAYER 2: one agent scrutinizes + synthesizes the minimal final rulebook, by reference' },
  ],
}

// =====================================================================================
// args (injected by the caller; the script has NO filesystem access):
// {
//   profiles: [ { type, findings: [ {                         // ONLY the surviving profile[] array
//       id, aspect, exemplar_pattern,
//       exemplar_quotes: [{paper, quote}],                    // the REAL published target register (the anchor)
//       our_pattern, our_quotes: [{para_id, quote}],
//       gap, materiality, guardrail_collision } ] } ],
//   maxProfiles?: 2                                           // how many TYPES run concurrently (peak ~maxProfiles*3 agents)
// }
// Output: { rulebooks: { <type>: [principles...] }, coverage: { <type>:{...} }, audit:{...} }
// =====================================================================================

// ---------- output contracts (forced via schema; no free prose) ----------
const EXTRACT_SCHEMA = {
  type: 'object', required: ['principles'], additionalProperties: false,
  properties: { principles: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    required: ['trigger', 'gap_fix', 'exemplar_anchor', 'finding_ids', 'meaning_flag'],
    properties: {
      trigger: { type: 'string' },                                   // the bad pattern to DETECT (from our_pattern/our_quotes)
      gap_fix: { type: 'string' },                                   // the delta to close, RELATIVE to the exemplar — NEVER an absolute target
      exemplar_anchor: {                                             // the REAL target: a verbatim exemplar quote from a cited finding
        type: 'object', additionalProperties: false, required: ['finding_id', 'quote'],
        properties: { finding_id: { type: 'string' }, quote: { type: 'string' } } },
      finding_ids: { type: 'array', minItems: 1, items: { type: 'string' } },
      meaning_flag: { type: 'boolean' },                             // = the finding's guardrail_collision (near load-bearing meaning -> Phase-4 handle-with-care)
    } } } },
}
// LAYER 2 red-team contract (scrutinize + synthesize, BY REFERENCE): keep/merge/cull on IDs; invents nothing.
const REDTEAM_SCHEMA = {
  type: 'object', required: ['keep', 'merge', 'cull', 'side_notes'], additionalProperties: false,
  properties: {
    keep:  { type: 'array', items: { type: 'string' } },
    merge: { type: 'array', items: { type: 'object', required: ['ids', 'canonical'], additionalProperties: false,
             properties: { ids: { type: 'array', items: { type: 'string' } }, canonical: { type: 'string' } } } },
    cull:  { type: 'array', items: { type: 'object', required: ['id', 'reason'], additionalProperties: false,
             properties: { id: { type: 'string' }, reason: { type: 'string' } } } },
    side_notes: { type: 'array', items: { type: 'string' } },
  },
}

// ---------- HARD execution constraint (verbatim from the proven Phase-1 harness) ----------
const TOOL_LOCK = `[HARD EXECUTION CONSTRAINT — OBEY EXACTLY, THIS OVERRIDES EVERYTHING BELOW]
You have EXACTLY ONE permitted action: a SINGLE call to the StructuredOutput function that returns your result object. Make it your FIRST and ONLY action.
ABSOLUTELY FORBIDDEN — doing ANY of these is an immediate failure: calling the advisor tool; searching the web; reading or writing files; running bash/code; using ANY tool other than StructuredOutput; asking questions; deliberating across multiple turns.
Everything you need is already in this prompt. Reason SILENTLY, then emit the StructuredOutput object in ONE turn. Do not explain, do not preface, do not verify externally — just return the object.`

// ---------- the load-bearing anti-hallucination rule (shared by every EXTRACT head) ----------
const EXTRACT_RULES = `WHAT YOU PRODUCE: WRITING PRINCIPLES the Phase-4 rewrite will obey — one per distinct finding (merge only near-identical findings, citing ALL their finding_ids). Each principle = {trigger, gap_fix, exemplar_anchor, finding_ids, meaning_flag}.

ANTI-HALLUCINATION — THIS IS THE LOAD-BEARING RULE. Every finding is a RELATIVE, exemplar-anchored observation: "OUR prose does X where the published exemplars do Y." Your principle's TARGET is the finding's OWN exemplar — you may NEVER invent an absolute target, threshold, number, or direction the finding did not state.
- WRONG (fabricated absolute): "sentences must be short / <=35 words / max 2 nouns".  The finding never said "short"; it said "longer than the exemplars".
- RIGHT (relative, anchored): "split conjoined clauses toward the exemplar register" / "name the construct plainly as the exemplars do".
- exemplar_anchor.quote MUST be copied VERBATIM (character-for-character) from the exemplar_quotes of the finding whose id you put in exemplar_anchor.finding_id. A quote that is not an exact substring is discarded automatically by a script.
- gap_fix may cite a number ONLY if that exact number already appears in the cited finding (e.g. an exemplar average); state it as "the exemplar average", NEVER as a cap. A gap_fix containing any number not in the finding is discarded automatically.
- meaning_flag = the finding's guardrail_collision verbatim. If true, the principle sits near load-bearing meaning — STILL describe-only, never propose altering the claim.

DESCRIBE ONLY: you NAME the pattern and POINT at the exemplar target. You do NOT rewrite our prose, do NOT assert two phrasings "mean the same". The rewrite is a separate, human-gated phase (Phase 4).
finding_ids: cite ONLY ids that appear in the FINDINGS below.`

function extractPrompt(version, type, findings) {
  const head = {
    1: `You are converting the Phase-1 STYLE findings for the "${type}" writing into actionable writing principles. Each finding compares OUR prose against published corporate-finance exemplars. Turn every finding into one principle whose target is the finding's own exemplar.`,
    2: `Task: read the "${type}" style findings below (each = where our prose is needlessly heavier than the published exemplars), and distil each into a writing principle. The principle must point at the exemplar the finding cites, never at an invented standard.`,
    3: `Work through the "${type}" findings one by one. For each, write the principle the Phase-4 rewriter should follow to close the gap to the exemplar — anchored to the exemplar's real wording, stated relative to it, never as an absolute rule.`,
  }[version]
  return `${TOOL_LOCK}\n\n${head}\n\n===== FINDINGS ("${type}") — these are the surviving findings; cite only these ids =====\n${JSON.stringify(findings.map(f => ({ id: f.id, aspect: f.aspect, exemplar_pattern: f.exemplar_pattern, exemplar_quotes: f.exemplar_quotes, our_pattern: f.our_pattern, our_quotes: f.our_quotes, gap: f.gap, materiality: f.materiality, guardrail_collision: f.guardrail_collision })), null, 1)}\n\n===== INSTRUCTIONS =====\n${EXTRACT_RULES}\n\nReturn principles via the structured tool. Your returned object IS the data, not a message.`
}

function redteamPrompt(type, cands) {
  return `${TOOL_LOCK}

You are the RED TEAM for the "${type}" writing-type. Three EXTRACT agents produced the candidate principles below (IDs assigned). Every exemplar_anchor quote is ALREADY script-verified verbatim and every gap_fix is already free of foreign numbers — do NOT re-check those.

YOUR JOB IS TWO THINGS, BY REFERENCE ONLY — you do NOT write or reword any principle; you emit decisions that reference principle IDs:

(1) SCRUTINIZE — refute by default. A principle survives ONLY if it passes ALL of these on judgment:
- (F1) NOT a fabricated absolute — it must NOT impose a target/threshold/direction the cited finding never stated ("be short", "max N words"). The legitimate target is the finding's exemplar, stated relatively.
- (F2) NOT relative->absolute hardening — it must not turn "our prose is heavier than the exemplars" into "must be <plain absolute>".
- FAITHFUL — gap_fix actually matches the finding's gap; exemplar_anchor is the right target for that gap.
- DESCRIBE-only — reject any principle that rewrites our prose or claims a phrasing "means the same".
Anything failing -> cull{id, reason}.

(2) SYNTHESIZE the FINAL rulebook for this type — your kept + merged set IS the deliverable. Merge duplicates / near-duplicates across the three agents into ONE canonical (tiebreak: more finding_ids / clearer trigger / stronger anchor); if a merge is DEBATABLE, keep them SEPARATE. Aim for the MINIMAL set that still covers every distinct finding — no redundant principle within this type's rulebook.

- meaning_flag=true sits near load-bearing meaning. This is NOT a reason to cull — KEEP such principles (a human MUST see them); never silently drop them.
- keep: IDs that survive as-is.  side_notes: ONLY human-facing under-coverage flags — NEVER new principles.

You invent nothing. The main loop copies kept/canonical principles VERBATIM into the "${type}" rulebook.

===== CANDIDATES =====
${JSON.stringify(cands.map(c => ({ id: c.id, agent: c.agent, trigger: c.trigger, gap_fix: c.gap_fix, exemplar_anchor: c.exemplar_anchor, finding_ids: c.finding_ids, meaning_flag: c.meaning_flag })), null, 1)}

Return decisions via the structured tool.`
}

// ---------- deterministic in-script GATE (pure JS, no LLM) — verbatim norm/isSub from Phase-1 ----------
function norm(s) {
  return (s || '')
    .toLowerCase()
    .replace(/[‘’‛′]/g, "'")
    .replace(/[“”″]/g, '"')
    .replace(/[‐-―−]/g, '-')
    .replace(/[^\w]+/g, ' ')
    .replace(/\b\d+\b/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}
function isSub(q, hay) { const n = norm(q); return n.length > 0 && norm(hay).includes(n) }
// process-scaffolding refs the agents legitimately cite (the EXTRACT prompt itself says "flag for Phase-4");
// their incidental digits are NOT fabricated magnitudes, so strip them before the foreign-number check
function stripScaffolding(s) {
  return (s || '')
    .replace(/\bphases?[\s~-]?\d+\b/gi, ' ')                 // Phase-4, Phase 3
    .replace(/\bsections?[\s~]?\d+(?:\.\d+)*\b/gi, ' ')      // Section 2.4
    .replace(/\btables?[\s~]?\d+\b/gi, ' ')                  // Table 3
    .replace(/\bpanels?[\s~]?[a-z0-9]+\b/gi, ' ')            // Panel B
    .replace(/\bcolumns?[\s~]?\(?\d+\)?\b/gi, ' ')           // column 2, column (1)
    .replace(/\bsteps?[\s~]?\d+\b/gi, ' ')                   // step 3
    .replace(/\bequations?[\s~]?\(?\d+\)?\b/gi, ' ')         // equation (2)
    .replace(/\bH\d+\b/gi, ' ')                              // hypothesis refs H1, H2
}
// every NON-scaffolding digit-run in gap_fix must appear in the finding text (catches fabricated absolutes like "<=35 words")
function numbersOK(gapFix, findingText) {
  const nums = (stripScaffolding(gapFix)).match(/\d+(?:\.\d+)?/g) || []
  return nums.every(d => (findingText || '').includes(d))
}

// =====================================================================================
//  PER TYPE — the whole pipeline for ONE writing-type, fully independent:
//  LAYER 1 panel x3 EXTRACT -> JS gate -> LAYER 2 RED TEAM (scrutinize + synthesize) -> the type's rulebook.
//  (types run in capped-concurrency batches; see the workflow body.)
// =====================================================================================
async function runProfile(P) {
  const findings = P.findings || []
  const byFinding = {}; findings.forEach(f => { byFinding[f.id] = f })
  const findingText = {}
  findings.forEach(f => {
    findingText[f.id] = [f.exemplar_pattern, f.our_pattern, f.gap,
      ...(f.exemplar_quotes || []).map(q => q.quote), ...(f.our_quotes || []).map(q => q.quote)].join(' ')
  })

  // ---- LAYER 1: neurodiverse panel x3 (parallel) ----
  const raw = await parallel([1, 2, 3].map(v => () =>
    agent(extractPrompt(v, P.type, findings), { schema: EXTRACT_SCHEMA, phase: 'Extract', label: `${P.type}/extract-${v}` })))

  // ---- deterministic GATE: drop fabricated / unanchored principles ----
  const clean = [], rejected = []
  raw.forEach((r, ai) => ((r && r.principles) || []).forEach((p, pi) => {
    const id = `${P.type}__a${ai + 1}f${pi + 1}`
    const fids = p.finding_ids || []
    const anchor = p.exemplar_anchor || {}
    const fidsOK = fids.length >= 1 && fids.every(fid => byFinding[fid])
    const anchorFinding = byFinding[anchor.finding_id]
    const anchorOK = !!anchorFinding && (anchorFinding.exemplar_quotes || []).some(q => isSub(anchor.quote, q.quote))
    const numOK = fids.some(fid => numbersOK(p.gap_fix, findingText[fid]))
    if (fidsOK && anchorOK && numOK) clean.push({ id, agent: ai + 1, type: P.type, ...p })
    else rejected.push({ id, reason: !fidsOK ? 'finding_id_not_in_profile' : (!anchorOK ? 'exemplar_anchor_not_verbatim' : 'gap_fix_has_foreign_number') })
  }))
  log(`[${P.type}] ${clean.length} passed gate, ${rejected.length} rejected`)
  if (clean.length === 0) return { type: P.type, principles: [], gate_rejected: rejected, culled: [], merges: [], unhandled: [], note: 'no principles survived the gate' }

  // ---- LAYER 2: ONE red-team agent — scrutinize + synthesize the final rulebook (by reference, null-degrade) ----
  const decisions = await agent(redteamPrompt(P.type, clean), { schema: REDTEAM_SCHEMA, phase: 'RedTeam', label: `${P.type}/redteam` })
  if (!decisions) {
    log(`[${P.type}] red-team returned NULL -> degrading to ${clean.length} gate-clean principles (no scrutiny/merge)`)
    return { type: P.type, principles: clean, gate_rejected: rejected, culled: [], merges: [], unhandled: [],
             side_notes: ['RED-TEAM FAILED (null) — principles are raw gate-clean, NOT scrutinized/synthesized; re-run this type'], note: 'redteam_failed' }
  }
  const byId = {}; clean.forEach(p => { byId[p.id] = p })
  const cullIds = new Set((decisions.cull || []).map(c => c.id))
  const keepIds = new Set((decisions.keep || []).filter(id => !cullIds.has(id)))
  ;(decisions.merge || []).forEach(m => { if (m.canonical && !cullIds.has(m.canonical)) keepIds.add(m.canonical) })
  const principles = [...keepIds].map(id => byId[id]).filter(Boolean)
  const handled = new Set([...keepIds, ...cullIds]); (decisions.merge || []).forEach(m => (m.ids || []).forEach(id => handled.add(id)))
  const unhandled = clean.map(p => p.id).filter(id => !handled.has(id))
  // robustness: a non-null red-team whose keep/merge IDs don't match ANY candidate (seen on the 87-candidate
  // results set) must NOT zero out the rulebook — degrade to gate-clean instead of returning an empty book.
  if (principles.length === 0 && clean.length > 0) {
    log(`[${P.type}] red-team kept 0 of ${clean.length} (decision IDs unmatched) -> degrading to gate-clean`)
    return { type: P.type, principles: clean, gate_rejected: rejected, culled: [], merges: [], unhandled: [],
             side_notes: ['RED-TEAM kept 0 (decision IDs did not match the candidates) — degraded to gate-clean (un-deduped); re-run this type'], note: 'redteam_zero_degraded' }
  }
  log(`[${P.type}] ${principles.length} kept after red-team; ${cullIds.size} culled; ${unhandled.length} unhandled`)
  return { type: P.type, principles, gate_rejected: rejected, culled: decisions.cull || [], merges: decisions.merge || [], unhandled, side_notes: decisions.side_notes || [] }
}

// =====================================================================================
//  MATERIALIZE (JS) — each type gets its OWN rulebook = its kept principles. No cross-type anything.
// =====================================================================================
function materialize(perType, A) {
  const findingsByType = {}; (A.profiles || []).forEach(P => { findingsByType[P.type] = (P.findings || []).map(f => f.id) })
  const books = {}, coverage = {}
  perType.forEach(r => {
    const t = r.type
    books[t] = (r.principles || []).map(p => ({ principle_id: p.id, trigger: p.trigger, gap_fix: p.gap_fix, exemplar_anchor: p.exemplar_anchor, finding_ids: p.finding_ids, meaning_flag: p.meaning_flag }))
    const all = findingsByType[t] || []
    const covered = new Set((r.principles || []).flatMap(p => p.finding_ids || []))
    coverage[t] = { total_findings: all.length, covered_findings: all.filter(id => covered.has(id)).length, uncovered_finding_ids: all.filter(id => !covered.has(id)), rule_count: books[t].length, note: r.note || null }
  })
  return { books, coverage }
}

// ================================= workflow body =================================
phase('Extract')
// the runner may deliver args as a JSON string (observed: typeof args === 'string'); parse so the script always sees an object
if (typeof args === 'string') { try { args = JSON.parse(args) } catch (e) { return { error: 'args string failed to JSON.parse: ' + e.message } } }
if (!args || !Array.isArray(args.profiles)) {
  return { error: 'args must provide { profiles:[{type, findings:[...]}], maxProfiles? }' }
}

// input-count guard: echo the per-type finding counts the harness actually received, so a lossy caller-side
// paste (dropped findings) is visible in the journal within seconds instead of only at end-of-run coverage.
log('[input] received -> ' + args.profiles.map(P => `${P.type}:${(P.findings || []).length}`).join('  '))

// types are INDEPENDENT — run them in capped-concurrency batches (peak ~maxProfiles*3 agents) to respect the rate-limit scar
const MAXP = Math.max(1, args.maxProfiles || 2)
const perType = []
for (let i = 0; i < args.profiles.length; i += MAXP) {
  const batch = await parallel(args.profiles.slice(i, i + MAXP).map(P => () => runProfile(P)))
  perType.push(...batch.filter(Boolean))
}

const out = materialize(perType, args)
log(`[done] ${perType.length} type-rulebooks -> ` + perType.map(r => `${r.type}:${(r.principles || []).length}`).join(' '))

return {
  rulebooks: out.books,
  coverage: out.coverage,
  audit: {
    per_type: perType.map(r => ({ type: r.type, kept: (r.principles || []).length, gate_rejected: r.gate_rejected || [], culled: r.culled || [], unhandled: r.unhandled || [], note: r.note, side_notes: r.side_notes || [] })),
  },
}
