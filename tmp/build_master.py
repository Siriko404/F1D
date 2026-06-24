"""Build the multi-type WAVE runner template from the proven, patched single-type template.
Keeps ALL helpers/schemas/prompts VERBATIM (zero divergence); replaces only the workflow body
with a wave loop that runs N types concurrently (each: panel x3 -> deterministic gate -> redteam)."""
from pathlib import Path
ROOT = Path(".").resolve()
tpl = (ROOT/"docs/Thesis/rewrite/style_phase1_pilot.js").read_text(encoding="utf-8")
MARK = "// ================= workflow ================="
assert MARK in tpl, "workflow marker not found in template"
header = tpl.split(MARK)[0]
header = header.replace("name: 'style-phase1-pilot'", "name: 'style-phase1-wave'")
header = header.replace("Phase-1 style ANALYSIS for one section type:",
                        "Phase-1 style ANALYSIS for a WAVE of section types (each runs concurrently):")

body = r'''// ================= workflow (multi-type WAVE) =================
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
'''
out = header + body
dest = ROOT/"docs/Thesis/rewrite/style_phase1_master.js"
dest.write_text(out, encoding="utf-8")
print(f"wrote master template: {dest}  | {len(out):,} chars")
