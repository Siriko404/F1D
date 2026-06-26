export const meta = {
  name: 'phase2-principles-harness',
  description: 'Phase-2: turn the 157 Phase-1 style findings into a minimal, exemplar-anchored writing-principle list PER WRITING-TYPE (8 self-contained rulebooks: abstract, intro, lit_review, hypotheses, data, methods, results, conclusion). Writes NO thesis prose. The findings already live in 8 type buckets (avg ~20 each, 14-32) so 8 is the data-native grain; a Phase-4 subsection reads its type rulebook (3.2/3.3/3.4 -> results, 2.3-2.5 -> methods, ...). THREE agent layers (max): LAYER 1 = neurodiverse PANEL of 3 paraphrased EXTRACT agents per profile (different minds catch different gaps) -> deterministic JS gate (exemplar-anchor verbatim + no foreign number, scaffolding-refs exempt); LAYER 2 = cull-by-reference REDTEAM (1 independent skeptic per profile, refute-by-default + within-profile dedup); LAYER 3 = a SINGLE global FINALIZE agent that dedups same-rule twins ACROSS profiles AND tags each canonical universal-vs-type-specific in one pass. Then JS MATERIALIZE fans out to 8 rulebooks with a coverage reconcile. Profiles run in capped-concurrency batches (args.maxProfiles, default 2 -> peak ~6 agents) to respect the server rate-limit scar. Every agent TOOL_LOCK + forced StructuredOutput; checkers describe-only / by-reference; null-degrade never crashes.',
  phases: [
    { title: 'Extract',  detail: 'LAYER 1: neurodiverse panel of 3 agents per profile -> candidate principles' },
    { title: 'Cull',     detail: 'LAYER 2: redteam culls fabricated/absolute + dedups within profile, by reference' },
    { title: 'Finalize', detail: 'LAYER 3: one agent dedups across profiles + tags universal vs type-specific (default-include)' },
  ],
}

// =====================================================================================
// args (injected by the caller; the script has NO filesystem access):
// {
//   profiles: [ { type, findings: [ {                         // ONLY the surviving profile[] array — NOT rejected/merged
//       id, aspect, exemplar_pattern,
//       exemplar_quotes: [{paper, quote}],                    // the REAL published target register (the anchor)
//       our_pattern, our_quotes: [{para_id, quote}],
//       gap, materiality, guardrail_collision } ] } ],        // 8 profiles, 157 findings total
//   types:    [ "abstract","intro","lit_review","hypotheses","data","methods","results","conclusion" ],  // the 8 writing-type rulebooks
//   roster:   { "<type>": "one-line description of that writing situation" },   // context for the universal-vs-specific call
//   convention: "short statement of the corp-fin convention (DraftTemplate gist)"
// }
// Output: { rulebooks: { <type>: [principles...] }, canonical_count, coverage:{...}, audit:{...} }
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
// by-reference checker contract (style + referee pattern): keep/merge/cull on IDs; invents nothing
const CULL_SCHEMA = {
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
// LAYER 3 (merged judge+classify): in ONE pass dedup same-rule twins across profiles AND tag each canonical
// universal (every type) vs specific (its source types). Every input id lands in exactly one group OR one singleton.
const FINALIZE_SCHEMA = {
  type: 'object', required: ['groups', 'singletons', 'side_notes'], additionalProperties: false,
  properties: {
    groups: { type: 'array', items: { type: 'object', required: ['member_ids', 'canonical', 'universal'], additionalProperties: false,
              properties: { member_ids: { type: 'array', items: { type: 'string' } }, canonical: { type: 'string' }, universal: { type: 'boolean' } } } },
    singletons: { type: 'array', items: { type: 'object', required: ['id', 'universal'], additionalProperties: false,
              properties: { id: { type: 'string' }, universal: { type: 'boolean' } } } },   // no cross-profile twin; still tagged
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

function cullPrompt(type, cands) {
  return `${TOOL_LOCK}

You are the REDTEAM for the "${type}" writing principles. Three extract agents produced the candidates below (IDs assigned). Every exemplar_anchor quote here has ALREADY been script-verified verbatim and every gap_fix is already free of foreign numbers — do NOT re-check those.

YOUR PRIMARY JOB IS TO CULL, BY REFERENCE ONLY. You do NOT write or reword any principle. You emit decisions that reference principle IDs. Refute by default: a principle survives ONLY if it passes ALL of these on judgment:
- (F1) NOT a fabricated absolute — it must NOT impose a target/threshold/direction the cited finding never stated ("be short", "max N words"). The legitimate target is the finding's exemplar, stated relatively.
- (F2) NOT relative->absolute hardening — it must not turn "our prose is heavier than the exemplars" into "must be <plain absolute>".
- FAITHFUL — gap_fix actually matches the finding's gap; exemplar_anchor is the right target for that gap.
- DESCRIBE-only — reject any principle that rewrites our prose or claims a phrasing "means the same".
Anything failing -> cull{id, reason}.

- meaning_flag=true means the principle sits near load-bearing meaning. This is NOT a reason to cull — KEEP such principles (a human MUST see them); never silently drop them.
- MERGE duplicates/near-duplicates across the three agents: group their IDs and name ONE canonical to keep (tiebreak: more finding_ids / better anchor). If a merge is DEBATABLE, prefer keeping them SEPARATE.
- keep: IDs that survive as-is.  side_notes: ONLY human-facing under-coverage flags — NEVER new principles.

You invent nothing. The main loop copies kept/canonical principles verbatim.

===== CANDIDATES =====
${JSON.stringify(cands.map(c => ({ id: c.id, agent: c.agent, trigger: c.trigger, gap_fix: c.gap_fix, exemplar_anchor: c.exemplar_anchor, finding_ids: c.finding_ids, meaning_flag: c.meaning_flag })), null, 1)}

Return decisions via the structured tool.`
}

function finalizePrompt(all, types, roster, convention) {
  return `${TOOL_LOCK}

You are the FINALIZE editor (chief editor). Below are the surviving writing principles from the type profiles (IDs assigned; each carries its source type). Do TWO jobs in ONE pass, BY REFERENCE ONLY — you invent nothing and reword nothing:

(1) DEDUP ACROSS PROFILES. Different types often produced the SAME underlying rule in different words (e.g. "split long conjoined sentences" appears under several types). Group genuine same-rule twins and name ONE canonical to keep (tiebreak: more finding_ids / clearer trigger / stronger exemplar_anchor). Merge ONLY genuine same-rule duplicates; if two principles target DIFFERENT writing devices, keep them SEPARATE even if both are "about sentences".

(2) CLASSIFY each surviving canonical: UNIVERSAL (a register/structure rule every writing type should follow — sentence length, nominalization, metaphor, plain verbs) or SPECIFIC to its source type(s) (e.g. "report each coefficient's sign plainly" has no place in an abstract or a literature review). DEFAULT TO UNIVERSAL when unsure: a type ignoring an extra general rule is cheap; a type MISSING a rule it needs is the costly error. Mark universal=false ONLY when the rule clearly cannot apply outside its own content type.

OUTPUT (every id below MUST appear in exactly ONE group OR ONE singleton):
- groups: each = {member_ids:[two+ ids stating the SAME rule], canonical:<id to keep>, universal:<bool>}.
- singletons: each = {id:<id with no cross-profile twin>, universal:<bool>}.
- side_notes: human-facing notes only (e.g. under-coverage); NEVER new principles.

===== CONVENTION =====
${convention}

===== THE WRITING TYPES =====
${JSON.stringify(types.map(t => ({ type: t, is: roster[t] || '' })), null, 1)}

===== PRINCIPLES (all profiles) =====
${JSON.stringify(all.map(p => ({ id: p.id, type: p.type, trigger: p.trigger, gap_fix: p.gap_fix, finding_ids: p.finding_ids, meaning_flag: p.meaning_flag })), null, 1)}

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
// digits kept (the anti-foreign-number check): every NON-scaffolding digit-run in gap_fix must appear in the finding text
// (this catches fabricated absolute targets like "<=35 words" / "max 2 nouns" while ignoring process refs)
function numbersOK(gapFix, findingText) {
  const nums = (stripScaffolding(gapFix)).match(/\d+(?:\.\d+)?/g) || []
  return nums.every(d => (findingText || '').includes(d))
}

// =====================================================================================
//  LAYER 1 + LAYER 2 — per profile: neurodiverse panel x3 EXTRACT -> deterministic JS gate -> REDTEAM cull.
//  (profiles themselves run in capped-concurrency batches; see the workflow body.)
// =====================================================================================
async function runProfile(P) {
  const findings = P.findings || []
  const byFinding = {}; findings.forEach(f => { byFinding[f.id] = f })
  const findingText = {}
  findings.forEach(f => {
    findingText[f.id] = [f.exemplar_pattern, f.our_pattern, f.gap,
      ...(f.exemplar_quotes || []).map(q => q.quote), ...(f.our_quotes || []).map(q => q.quote)].join(' ')
  })

  const raw = await parallel([1, 2, 3].map(v => () =>
    agent(extractPrompt(v, P.type, findings), { schema: EXTRACT_SCHEMA, phase: `Extract:${P.type}`, label: `${P.type}/extract-${v}` })))

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

  // ---- cull-by-reference REDTEAM (null-degrade) ----
  const decisions = await agent(cullPrompt(P.type, clean), { schema: CULL_SCHEMA, phase: `Cull:${P.type}`, label: `${P.type}/cull` })
  if (!decisions) {
    log(`[${P.type}] cull redteam returned NULL -> degrading to ${clean.length} gate-clean principles (no cull/merge)`)
    return { type: P.type, principles: clean, gate_rejected: rejected, culled: [], merges: [], unhandled: [],
             side_notes: ['CULL REDTEAM FAILED (null) — principles are raw gate-clean, NOT deduped/verified; re-run this profile'], note: 'cull_failed' }
  }
  const byId = {}; clean.forEach(p => { byId[p.id] = p })
  const cullIds = new Set((decisions.cull || []).map(c => c.id))
  const keepIds = new Set((decisions.keep || []).filter(id => !cullIds.has(id)))
  ;(decisions.merge || []).forEach(m => { if (m.canonical && !cullIds.has(m.canonical)) keepIds.add(m.canonical) })
  const principles = [...keepIds].map(id => byId[id]).filter(Boolean)
  const handled = new Set([...keepIds, ...cullIds]); (decisions.merge || []).forEach(m => (m.ids || []).forEach(id => handled.add(id)))
  const unhandled = clean.map(p => p.id).filter(id => !handled.has(id))
  log(`[${P.type}] ${principles.length} kept after cull; ${cullIds.size} culled; ${unhandled.length} unhandled`)
  return { type: P.type, principles, gate_rejected: rejected, culled: decisions.cull || [], merges: decisions.merge || [], unhandled, side_notes: decisions.side_notes || [] }
}

// =====================================================================================
//  LAYER 3 — FINALIZE (ONE global agent): cross-profile dedup + universal/specific tag, by reference, null-degrade.
//  Each canonical carries source_types (the types its members came from) and applies_to (= all types if universal).
// =====================================================================================
async function finalize(allClean, A) {
  const validType = new Set(A.types)
  const byId = {}; allClean.forEach(p => { byId[p.id] = p })
  const srcTypes = ids => [...new Set(ids.map(id => byId[id] && byId[id].type).filter(Boolean))]
  const scoped = [], used = new Set()
  const pushCanon = (canonId, memberIds, universal) => {
    if (!byId[canonId] || used.has(canonId)) return
    const members = [...new Set((memberIds || []).filter(id => byId[id]).concat(canonId))]
    members.forEach(id => used.add(id))
    const st = srcTypes(members)
    const applies = universal ? A.types.slice() : [...new Set(st.filter(t => validType.has(t)))]
    scoped.push({ ...byId[canonId], member_ids: members,
      finding_ids: [...new Set(members.flatMap(id => byId[id].finding_ids || []))],
      meaning_flag: members.some(id => byId[id].meaning_flag),
      source_types: st, universal: !!universal,
      applies_to: applies.length ? applies : (st.length ? st : [byId[canonId].type]) })   // never empty
  }

  const decisions = await agent(finalizePrompt(allClean, A.types, A.roster || {}, A.convention || ''),
    { schema: FINALIZE_SCHEMA, phase: 'Finalize', label: 'finalize/dedup+classify' })
  if (!decisions) {
    log(`[finalize] returned NULL -> degrading: every principle its own canonical, ALL universal (safe over-include)`)
    allClean.forEach(p => pushCanon(p.id, [p.id], true))
    return { scoped, note: 'finalize_failed', side_notes: ['FINALIZE FAILED (null) — no cross-profile dedup; every rule marked universal (over-include); re-run finalize'] }
  }
  ;(decisions.groups || []).forEach(g => {
    const canonId = g.canonical && byId[g.canonical] ? g.canonical : (g.member_ids || []).find(id => byId[id])
    if (canonId) pushCanon(canonId, g.member_ids || [], g.universal)
  })
  ;(decisions.singletons || []).forEach(s => { if (s && byId[s.id]) pushCanon(s.id, [s.id], s.universal) })
  allClean.forEach(p => { if (!used.has(p.id)) pushCanon(p.id, [p.id], false) })   // no silent drop; un-returned -> keep in its own type book
  log(`[finalize] ${allClean.length} principles -> ${scoped.length} canonical; ${scoped.filter(p => p.universal).length} universal`)
  return { scoped, side_notes: decisions.side_notes || [] }
}

// =====================================================================================
//  Stage D — MATERIALIZE (JS fan-out) + COVERAGE reconcile (set ops; mechanical, paired with the agent checks above)
// =====================================================================================
function materialize(scoped, A) {
  const books = {}; A.types.forEach(t => { books[t] = [] })
  scoped.forEach(p => p.applies_to.forEach(t => {
    if (books[t]) books[t].push({ principle_id: p.id, trigger: p.trigger, gap_fix: p.gap_fix, exemplar_anchor: p.exemplar_anchor, finding_ids: p.finding_ids, meaning_flag: p.meaning_flag, universal: p.universal })
  }))
  const allFindingIds = new Set((A.profiles || []).flatMap(P => (P.findings || []).map(f => f.id)))
  const coveredFindingIds = new Set(scoped.flatMap(p => p.finding_ids || []))
  const uncovered = [...allFindingIds].filter(id => !coveredFindingIds.has(id))
  const typeCounts = {}; A.types.forEach(t => { typeCounts[t] = books[t].length })
  const emptyTypes = A.types.filter(t => books[t].length === 0)
  return { books, coverage: { total_findings: allFindingIds.size, covered_findings: coveredFindingIds.size, uncovered_finding_ids: uncovered, type_counts: typeCounts, empty_types: emptyTypes } }
}

// ================================= workflow body =================================
phase('Extract')
// the runner may deliver args as a JSON string (observed: typeof args === 'string'); parse so the script always sees an object
if (typeof args === 'string') { try { args = JSON.parse(args) } catch (e) { return { error: 'args string failed to JSON.parse: ' + e.message } } }
if (!args || !Array.isArray(args.profiles) || !Array.isArray(args.types)) {
  return { error: 'args must provide { profiles:[...8 with findings], types:[...8 type ids], roster:{}, convention:"" }' }
}

// profiles run in capped-concurrency BATCHES (peak ~maxProfiles*3 agents): parallelizes the bulk of the work while
// respecting the server rate-limit scar. maxProfiles is the safety knob (default 2 -> peak ~6; raise once a cap proves safe).
const MAXP = Math.max(1, args.maxProfiles || 2)
const perProfile = []
for (let i = 0; i < args.profiles.length; i += MAXP) {
  const batch = await parallel(args.profiles.slice(i, i + MAXP).map(P => () => runProfile(P)))
  perProfile.push(...batch.filter(Boolean))
}

const allClean = perProfile.flatMap(r => r.principles || [])
log(`[wave] ${allClean.length} principles survived gate+cull across ${perProfile.length} profiles (batch size ${MAXP})`)
if (allClean.length === 0) return { error: 'no principles survived gate+cull', perProfile }

phase('Finalize')
const F = await finalize(allClean, args)

const out = materialize(F.scoped, args)
log(`[done] ${F.scoped.length} canonical principles -> ${args.types.length} type-rulebooks; ${out.coverage.uncovered_finding_ids.length} findings uncovered; ${out.coverage.empty_types.length} empty types`)

return {
  rulebooks: out.books,
  canonical_count: F.scoped.length,
  coverage: out.coverage,
  audit: {
    per_profile: perProfile.map(r => ({ type: r.type, kept: (r.principles || []).length, gate_rejected: r.gate_rejected || [], culled: r.culled || [], unhandled: r.unhandled || [], note: r.note, side_notes: r.side_notes || [] })),
    finalize_side_notes: F.side_notes || [], finalize_note: F.note,
  },
}
