// harness.template.mjs — Phase 3: the prose-writing Workflow (the agentic core).
// TEMPLATE: the build step (build_harness.py) replaces __BRIEFS__ with briefs.json and
// __GATES__ with gates.mjs source, emitting a self-contained ASCII script for the Workflow tool.
// Unit = one section. Per section: L1 writers(3) -> GATE -> L2 editor -> GATE -> L3 audit(6 lanes) -> L4 judge -> FINAL GATE.
// Lessons: §2 paraphrased panel, NO examples, identical hard constraints · §3 deterministic JS gate is the spine ·
// §4 red-team synthesizes by reference · P9 auditors PROPOSE only · P8 null-degrade · B5 sequential batches.

export const meta = {
  name: 'prose-harness',
  description: 'Write + self-audit final LaTeX prose for each thesis section from its locked propositions + rulebook',
  phases: [{ title: 'Write' }, { title: 'Audit' }],
};

// ---- embedded (injected by build step; pure ASCII) ----
const BRIEFS = __BRIEFS__;
__GATES__   // defines runGates(par) etc.

// run all 5 gates on a writer/judge output (array of {para_id, final_prose, prop_ids?}) against a brief
function sectionGate(out, brief) {
  const blocks = [], flags = [];
  const byId = Object.fromEntries(brief.paragraphs.map(p => [p.para_id, p]));
  for (const par of (out.paragraphs || [])) {
    const b = byId[par.para_id]; if (!b) { blocks.push(`${par.para_id}: unknown paragraph`); continue; }
    const r = runGates({
      prose: par.final_prose || '',
      allowedTokens: (brief.allowed_tokens_all && brief.allowed_tokens_all.length ? brief.allowed_tokens_all : b.allowed_tokens),
      allowedKeys: (b.allowed_cites_all && b.allowed_cites_all.length ? b.allowed_cites_all : b.allowed_cites),
      props: b.props.map(p => ({ prop_id: p.prop_id, signature: p.signature })),
    });
    blocks.push(...r.blocks.map(x => `${par.para_id}: ${x}`));
    flags.push(...r.flags.map(x => `${par.para_id}: ${x}`));
  }
  // completeness: every brief paragraph must be present
  const got = new Set((out.paragraphs || []).map(p => p.para_id));
  for (const b of brief.paragraphs) if (!got.has(b.para_id)) blocks.push(`${b.para_id}: paragraph missing from output`);
  return { pass: blocks.length === 0, blocks, flags };
}

// ---- shared constraint block (BYTE-IDENTICAL across all writers; lessons §2 vary voice not constraints) ----
function constraints(brief) {
  return [
    'HARD CONSTRAINTS (identical for every writer; non-negotiable):',
    '- Render ONLY the propositions below into flowing LaTeX prose. Add NO new claim, number, citation, or fact.',
    '- NUMBERS: use ONLY the exact figures printed in each prop (with their exact significance stars in LaTeX form, e.g. $0.0391^{***}$). Never invent, round, or restate a number with different/extra stars. A figure may be cited bare (no stars) only as a magnitude.',
    '- CITATIONS: use \\citep{}/\\citet{} ONLY with the cite keys the props carry. No other keys.',
    '- HONESTY FLOOR (verbatim, do not cross): ' + (brief.bright_lines || []).join(' | '),
    '- Respect every prop\'s register_locks exactly. Never say "suppressed"/"dampened" for a null; never claim detection or causation the prop does not state; keep hedges (these are mandatory, not optional).',
    '- Output valid LaTeX with balanced braces and math; escape % & _ #.',
    '- Cover EVERY proposition exactly once, in the given order; tag each paragraph with its para_id.',
  ].join('\n');
}
function brmain(brief) {
  return [
    `SECTION ${brief.section} ("${brief.title}") — type: ${brief.type}.`,
    '\nWRITE THIS SECTION\'S TYPE RULEBOOK (follow each principle):',
    ...brief.rulebook.map((r, i) => `  ${i + 1}. ${r.device}: ${r.principle}`),
    '\nPROPOSITIONS (ordered; render each, faithfully):',
    JSON.stringify(brief.paragraphs.map(p => ({ para_id: p.para_id, intent: (p.intent && p.intent.statement) || p.intent, props: p.props.map(x => ({ id: x.prop_id, statement: x.statement, numbers: x.numbers, register_locks: x.register_locks, evidence: x.evidence, verification_quotes: x.verification && x.verification.evidence_quotes ? '(verbatim source support on file)' : undefined })) })), null, 1),
    `\nSEAMS (for flow only, do not restate): prev ends "${(brief.seam_prev || []).join(' ')}"; next opens "${(brief.seam_next || []).join(' ')}"`,
    '\n' + constraints(brief),
  ].join('\n');
}

// 3 paraphrased writer heads (voice differs; constraints identical)
const HEADS = [
  'You are an empirical corporate-finance author drafting this section of your own thesis. Write the section\'s final prose now, in your own steady scholarly voice.',
  'Act as the paper\'s writer. Turn the locked propositions below into the finished section text, faithful and readable, in clean academic register.',
  'Compose this section as the thesis author. Convert each proposition into publishable LaTeX prose that a finance referee would find precise and well-built.',
];
const WRITER_SCHEMA = { type: 'object', required: ['paragraphs'], properties: { paragraphs: { type: 'array', items: {
  type: 'object', required: ['para_id', 'final_prose'], properties: {
    para_id: { type: 'string' }, final_prose: { type: 'string', description: 'LaTeX prose for this paragraph' },
    prop_ids: { type: 'array', items: { type: 'string' } } } } } } };

// 6 exclusive audit lanes (P7 stay-in-lane; P9 PROPOSE only, never rewrite)
const LANES = [
  ['honesty', 'HONESTY/REGISTER lane. Read every sentence: does any say MORE than its prop supports — a causal or detection claim, "suppressed/dampened" for a null, an un-hedged claim where the prop hedges, or strict-specificity where the prop says concentration? You hunt over-claims, never weaken a correct hedge. This is the thesis-killer lane.'],
  ['numbers', 'NUMBER-CONTEXT lane. For every figure: is it one of the prop\'s numbers, with the prop\'s exact stars/sign, used in the prop\'s context (right arm, right clock, right comparison)? Flag any mismatch of value, stars, sign, or context.'],
  ['rulebook', 'RULEBOOK lane. Does the prose follow this section type\'s principles (exhibit-anchored sentences, report-then-gloss, concrete magnitudes, hedging, etc.)? Flag specific principle violations.'],
  ['citation', 'CITATION lane. Is every \\cite key allowed and attached to a claim that source actually supports? Is any needed attribution missing? Flag mis-cites and missing cites.'],
  ['flow', 'FLOW/VOICE lane. Topic-sentence placement, paragraph architecture, first-person author voice, transitions, the seams to adjacent sections. Flag breaks in cohesion or register.'],
  ['completeness', 'COMPLETENESS lane. Is every locked proposition rendered exactly once, none added, none dropped, order preserved, depends_on cross-refs correct? Flag omissions/additions.'],
];
const AUDIT_SCHEMA = { type: 'object', required: ['issues'], properties: { issues: { type: 'array', items: {
  type: 'object', required: ['para_id', 'severity', 'issue', 'proposed_fix'], properties: {
    para_id: { type: 'string' }, severity: { enum: ['critical', 'major', 'minor'] },
    issue: { type: 'string' }, proposed_fix: { type: 'string' }, evidence: { type: 'string' } } } } } };

async function writeSection(brief) {
  // L1: 3 paraphrased writers
  const drafts = (await parallel(HEADS.map((h, v) => () =>
    agent(`${h}\n\n${brmain(brief)}`, { label: `write:${brief.section}:v${v + 1}`, phase: 'Write', schema: WRITER_SCHEMA })
  ))).filter(Boolean);
  // GATE each draft; keep only gate-clean ones
  const clean = drafts.filter(d => sectionGate(d, brief).pass);
  if (!clean.length) return { section: brief.section, status: 'BLOCKED', stage: 'L1', detail: drafts.map(d => sectionGate(d, brief).blocks).flat().slice(0, 12) };
  // L2: editor synthesizes the best single draft BY REFERENCE (no new claims)
  const merged = await agent(
    `You are the section editor. Below are ${clean.length} independent drafts of the SAME section, each already number- and honesty-gate-clean. Produce ONE best version: choose the strongest rendering of each paragraph and smooth the flow. Invent nothing; every number/citation must already appear in one of the drafts; keep all hedges.\n\n${brmain(brief)}\n\nDRAFTS:\n${JSON.stringify(clean.map(d => d.paragraphs), null, 1)}`,
    { label: `edit:${brief.section}`, phase: 'Write', schema: WRITER_SCHEMA });
  const g = sectionGate(merged, brief);
  if (!g.pass) return { section: brief.section, status: 'BLOCKED', stage: 'L2', detail: g.blocks.slice(0, 12), drafts: clean.map(d => d.paragraphs) };
  return { section: brief.section, status: 'WRITTEN', brief, merged, drafts: clean.map(d => d.paragraphs), flags: g.flags };
}

// collect verbatim source quotes across the WHOLE thesis (the honesty evidence for the whole-thesis honesty audit)
function quoteBlockAll(written) {
  const qs = [];
  for (const w of written) for (const pa of w.brief.paragraphs) for (const p of pa.props)
    if (p.verification && p.verification.evidence_quotes)
      qs.push(`[Sec.${w.section}] PROP ${p.prop_id} claims: "${p.statement}"\nSOURCE (verbatim, ${(p.verification.source && p.verification.source.title) || 'cited paper'}; verdict ${p.verification.verdict}):\n${p.verification.evidence_quotes}`);
  return qs.length ? `\nVERBATIM SOURCE SUPPORT (whole thesis; flag ANY claim that says more than its quote supports):\n${qs.join('\n\n')}\n` : '';
}

// ===== RED-TEAM (whole thesis): 3 agents read the FULL draft adversarially, flag, PROPOSE -- never rewrite =====
async function redteamWhole(fullDraft) {
  const heads = [
    'You are the thesis red team. Read the WHOLE drafted thesis adversarially, top to bottom.',
    'Act as a hostile journal referee reading the entire thesis to find everything wrong.',
    'You are a skeptical examiner reading the complete thesis end to end.',
  ];
  const panel = (await parallel(heads.map((h, v) => () =>
    agent(`${h} Assume every claim is wrong until the prose earns it. Flag overclaims, weakened hedges, numbers that look off, broken "see Section X" references, incoherence between sections -- anything a referee would attack. Tag each issue with its section. PROPOSE a fix; never rewrite.\n\nFULL THESIS:\n${fullDraft}`,
      { label: `redteam${v + 1}-WHOLE`, phase: 'Audit', schema: AUDIT_SCHEMA })
  ))).filter(Boolean);
  return panel.flatMap(p => (p && p.issues) || []).map(i => ({ ...i, lane: 'redteam' }));
}

// ===== AUDIT (whole thesis): honesty x3 (with all quotes) + 5 lanes; each reads the FULL thesis. 2 staggered panels (rate limit). =====
async function auditWhole(fullDraft, quotesAll) {
  const HONESTY = LANES[0][1], OTHERS = LANES.slice(1);
  const honestyTasks = [0, 1, 2].map(v => () =>
    agent(`${HONESTY}\n\nYou audit the WHOLE thesis. REFUTE-BY-DEFAULT: treat every claim as over-stated until its prop+quote support it; if uncertain, FLAG. Tag each issue with its section. PROPOSE fixes, never rewrite.\n${quotesAll}\n\nFULL THESIS:\n${fullDraft}`,
      { label: `audit:honesty${v + 1}-WHOLE`, phase: 'Audit', schema: AUDIT_SCHEMA }).then(a => ({ lane: 'honesty', issues: (a && a.issues) || [] })));
  const otherTasks = OTHERS.map(([key, body]) => () =>
    agent(`${body}\n\nYou audit ONLY this lane, across the WHOLE thesis; tag each issue with its section. PROPOSE fixes, do not rewrite.\n\nFULL THESIS:\n${fullDraft}`,
      { label: `audit:${key}-WHOLE`, phase: 'Audit', schema: AUDIT_SCHEMA }).then(a => ({ lane: key, issues: (a && a.issues) || [] })));
  const all = [...honestyTasks, ...otherTasks];
  log(`AUDIT PANEL 1/2 (${Math.ceil(all.length / 2)} lanes, whole thesis)`);
  const a1 = (await parallel(all.slice(0, Math.ceil(all.length / 2)))).filter(Boolean);
  log(`AUDIT PANEL 2/2 -- after Panel 1`);
  const a2 = (await parallel(all.slice(Math.ceil(all.length / 2)))).filter(Boolean);
  return [...a1, ...a2].flatMap(a => a.issues.map(i => ({ ...i, lane: a.lane })));
}

// ===== BOSS (whole-thesis CONTEXT, writes one section's final per call -- step by step) =====
async function bossSection(w, fullDraft, allReports) {
  const brief = w.brief;
  const mine = allReports.filter(i => (i.section && (i.section === brief.section || i.section === brief.stem)) || (i.para_id || '').includes(brief.section));
  const final = await agent(
    `You are the chief editor of the WHOLE thesis. EDIT the current draft of Section ${brief.section} below into its FINAL form by applying the well-supported reports: minimal edit (change the least; keep wording that is already clean), reject spurious or hedge-weakening fixes (refute-by-default on honesty/number claims), keep consistency with the rest of the thesis you can see, invent no new numbers or citations. Output just this section's paragraphs.\n\n${brmain(brief)}\n\nCURRENT DRAFT OF SECTION ${brief.section} (edit THIS):\n${JSON.stringify(w.merged.paragraphs, null, 1)}\n\nWHOLE THESIS (context/consistency only):\n${fullDraft}\n\nREPORTS (${mine.length} touch this section -- apply those):\n${JSON.stringify(mine, null, 1)}`,
    { label: `boss:${brief.section}`, phase: 'Audit', schema: WRITER_SCHEMA });
  const g = sectionGate(final, brief);
  const trail = { drafts: w.drafts, merged: w.merged.paragraphs, reports_for_section: mine };
  if (!g.pass) return { section: brief.section, status: 'BLOCKED', stage: 'FINAL-GATE', detail: g.blocks.slice(0, 12), final, trail };
  return { section: brief.section, status: 'OK', final, flags: g.flags, audit_count: mine.length, trail };
}

// ---- run: 3 PARALLEL TEAMS, each owning a section-group (Sina's design). Rate-limit-safe:
// only 3 streams run at once (one section per team in flight), not a 51-agent fan-out (lessons B5).
let A = args; if (typeof A === 'string') { try { A = JSON.parse(A); } catch (e) { A = {}; } } A = A || {};
const ONLY = Array.isArray(A.only) ? A.only : (A.only ? [A.only] : null);
const TEAMS = [
  { name: 'T1-framework', stems: ['section2.1', 'section2.2', 'section2.3', 'section2.4', 'section2.5'] },
  { name: 'T2-results', stems: ['section3.1', 'section3.2', 'section3.3', 'section3.4', 'section4.1', 'section4.2', 'section4.3', 'section4.4', 'section4.5'] },
  { name: 'T3-framing', stems: ['section_abstract', 'section1', 'section5'] },
];
// ===== PHASE A -- WRITE: 3 thematic teams in parallel; each writes its sections (writers->gate->editor->gate). NO audit yet. =====
async function writeTeam(team) {
  const out = [];
  for (const stem of team.stems) {                 // sequential within a team -> low concurrency
    if (ONLY && !ONLY.includes(stem)) continue;
    const brief = BRIEFS.find(b => b.stem === stem); if (!brief) continue;
    log(`[${team.name} WRITE] ${stem}`);
    out.push(await writeSection(brief));
  }
  return out;
}
log('PHASE A: write -- 3 thematic teams, parallel');
const written = (await parallel(TEAMS.map(t => () => writeTeam(t)))).flat().filter(Boolean);
const writtenOK = written.filter(w => w.status === 'WRITTEN');

// ===== BARRIER: ALL prose written before ANY review =====
// ===== PHASE B -- RED-TEAM + AUDIT, both reading the WHOLE thesis =====
log(`PHASE B: red-team + audit -- WHOLE thesis (${writtenOK.length} written, ${written.length - writtenOK.length} blocked at write)`);
const thesisFull = JSON.stringify(writtenOK.map(w => ({ section: w.section, paragraphs: w.merged.paragraphs.map(p => ({ para_id: p.para_id, final_prose: p.final_prose })) })));
const quotesAll = quoteBlockAll(writtenOK);
const redteamIssues = await redteamWhole(thesisFull);
log(`red-team (whole thesis): ${redteamIssues.length} issue(s)`);
const auditIssues = await auditWhole(thesisFull, quotesAll);
log(`audit (whole thesis): ${auditIssues.length} issue(s)`);
const allReports = [...redteamIssues, ...auditIssues];
// ===== PHASE C -- BOSS: whole-thesis-aware, writes the FINAL section by section (step by step) =====
log(`PHASE C: boss -- final prose section by section (sees whole thesis + all ${allReports.length} reports each step)`);
const results = [];
for (const w of writtenOK) { log(`[boss] ${w.section}`); results.push(await bossSection(w, thesisFull, allReports)); }
results.push(...written.filter(w => w.status !== 'WRITTEN'));
const ok = results.filter(r => r && r.status === 'OK');
const blocked = results.filter(r => r && r.status === 'BLOCKED');
log(`DONE: ${ok.length} OK, ${blocked.length} BLOCKED`);
return { ok: ok.map(r => r.section), blocked: blocked.map(r => ({ section: r.section, stage: r.stage, detail: r.detail })), results, reports: allReports };
