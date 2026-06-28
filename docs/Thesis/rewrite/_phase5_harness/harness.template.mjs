// harness.template.mjs — Phase 3: the prose-writing Workflow (the agentic core).
// TEMPLATE: the build step (build_harness.py) injects briefs.json + gates.mjs source at the two
// placeholders below (one each), emitting a self-contained ASCII script for the Workflow tool.
// WRITE: 3 teams, each = 3 paraphrased BLOCK-writers that render the team's WHOLE block (all its sections)
// in one go, step by step (1M ctx). Then per section: GATE -> editor merges the clean drafts -> GATE.
// Then BARRIER -> whole-thesis red-team -> whole-thesis audit (honesty x3 + 5 lanes) -> boss writes the final, section by section.
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
      numberTables: brief.number_table_map_all || null,
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

// table-reference hint: this section's labels + the hardcoded-number crosswalk (writers must emit \ref, never a literal number)
function tableHint(brief) {
  const xw = brief.table_xwalk || {};
  const labs = brief.table_labels || [];
  const a = labs.length ? `Tables this section may cite: ${labs.join(', ')}.` : '';
  const b = Object.keys(xw).length ? ` When a prop names a table as "Table N", render it as: ${Object.entries(xw).map(([n, l]) => `Table ${n} -> \\ref{${l}}`).join('; ')}.` : '';
  return (a + b).trim();
}

// ---- shared constraint block (BYTE-IDENTICAL across all writers; lessons §2 vary voice not constraints) ----
function constraints(brief) {
  return [
    'HARD CONSTRAINTS (identical for every writer; non-negotiable):',
    '- Render ONLY the propositions below into flowing LaTeX prose. Add NO new claim, number, citation, or fact.',
    '- NUMBERS: use ONLY the exact figures printed in each prop (with their exact significance stars in LaTeX form, e.g. $0.0391^{***}$). Never invent, round, or restate a number with different/extra stars. A figure may be cited bare (no stars) only as a magnitude.',
    '- CITATIONS: use \\citep{}/\\citet{} ONLY with the cite keys the props carry. No other keys.',
    '- TABLE REFERENCES: cite every table with \\ref{<tab:label>} (write e.g. "Table~\\ref{tab:empire_building_did}"). NEVER hardcode a table number such as "Table 5.2" (LaTeX auto-numbers; a literal number drifts), and never print a bare "tab:..." as visible text. ' + tableHint(brief),
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

// per-section editor / boss output: one section's paragraphs
const WRITER_SCHEMA = { type: 'object', required: ['paragraphs'], properties: { paragraphs: { type: 'array', items: {
  type: 'object', required: ['para_id', 'final_prose'], properties: {
    para_id: { type: 'string' }, final_prose: { type: 'string', description: 'LaTeX prose for this paragraph' },
    prop_ids: { type: 'array', items: { type: 'string' } } } } } } };
// a BLOCK-writer returns prose for EVERY section in its team's block (Sina's design: each of a team's 3
// paraphrased writers writes the team's WHOLE block in one go, step by step, using the 1M-token context).
const BLOCK_WRITER_SCHEMA = { type: 'object', required: ['sections'], properties: { sections: { type: 'array', items: {
  type: 'object', required: ['section', 'paragraphs'], properties: {
    section: { type: 'string', description: 'section id, e.g. "2.1"' },
    paragraphs: { type: 'array', items: { type: 'object', required: ['para_id', 'final_prose'], properties: {
      para_id: { type: 'string' }, final_prose: { type: 'string', description: 'LaTeX prose for this paragraph' } } } } } } } } };
// 3 paraphrased block-writer heads (voice differs; constraints identical)
const BLOCK_HEADS = [
  'You are an empirical corporate-finance author drafting these sections of your own thesis. Write each section\'s final prose now, in your own steady scholarly voice.',
  'Act as the paper\'s writer. Turn the locked propositions below into the finished text for every section, faithful and readable, in clean academic register.',
  'Compose these sections as the thesis author. Convert each proposition into publishable LaTeX prose that a finance referee would find precise and well-built.',
];
// concatenate the team's per-section briefs (rulebook+props+constraints+seams) into one block prompt
function blockMain(briefs) {
  return briefs.map((b, i) => `\n======== SECTION ${b.section} (${i + 1}/${briefs.length}) ========\n${brmain(b)}`).join('\n');
}

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

// (write logic lives in writeTeam below: 3 block-writers -> per-section GATE -> editor merge -> GATE)

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

// ---- run: 3 PARALLEL TEAMS, each owning a section-group (Sina's design). Each team's 3 writers render the
// whole block in one go -> peak ~9 block-writers concurrent (under the 16 cap), not a 51-agent fan-out (lessons B5).
let A = args; if (typeof A === 'string') { try { A = JSON.parse(A); } catch (e) { A = {}; } } A = A || {};
const ONLY = Array.isArray(A.only) ? A.only : (A.only ? [A.only] : null);
const TEAMS = [
  { name: 'T1-framework', stems: ['section2.1', 'section2.2', 'section2.3', 'section2.4', 'section2.5'] },
  { name: 'T2-results', stems: ['section3.1', 'section3.2', 'section3.3', 'section3.4', 'section4.1', 'section4.2', 'section4.3', 'section4.4', 'section4.5'] },
  { name: 'T3-framing', stems: ['section_abstract', 'section1', 'section5'] },
];
// ===== PHASE A -- WRITE: 3 thematic teams in parallel. Each team = 3 block-writers (each renders the team's
// WHOLE block in one go) -> per section: GATE the 3 versions, editor merges the clean ones, GATE. NO audit yet. =====
async function writeTeam(team) {
  let briefs = team.stems.map(s => BRIEFS.find(b => b.stem === s)).filter(Boolean);
  if (ONLY) briefs = briefs.filter(b => ONLY.includes(b.stem) || ONLY.includes(b.section));
  if (!briefs.length) return [];
  const ids = briefs.map(b => b.section).join(', ');
  log(`[${team.name} WRITE] block: ${ids}`);
  // L1: 3 paraphrased block-writers, each renders ALL of the team's sections, step by step
  const blocks = (await parallel(BLOCK_HEADS.map((h, v) => () =>
    agent(`${h}\n\nWrite the FINAL LaTeX prose for ALL of the following sections, in order, working through them step by step. Return EXACTLY one entry per section (sections: ${ids}) and, within each, one entry per paragraph tagged with its para_id. Omit no section and no paragraph.\n${blockMain(briefs)}`,
      { label: `write:${team.name}:v${v + 1}`, phase: 'Write', schema: BLOCK_WRITER_SCHEMA })
  ))).filter(Boolean);
  // L2: per section -> gather the 3 versions, GATE, editor merges the clean ones, GATE
  return await parallel(briefs.map(brief => async () => {
    const versions = blocks.map(bk => (bk.sections || []).find(s => s.section === brief.section || s.section === brief.stem)).filter(Boolean);
    const clean = versions.filter(v => sectionGate(v, brief).pass);
    if (!clean.length) return { section: brief.section, status: 'BLOCKED', stage: 'L1', detail: versions.map(v => sectionGate(v, brief).blocks).flat().slice(0, 12) };
    const merged = await agent(
      `You are the section editor. Below are ${clean.length} independent drafts of the SAME section, each already number- and honesty-gate-clean. Produce ONE best version: choose the strongest rendering of each paragraph and smooth the flow. Invent nothing; every number/citation must already appear in one of the drafts; keep all hedges.\n\n${brmain(brief)}\n\nDRAFTS:\n${JSON.stringify(clean.map(d => d.paragraphs), null, 1)}`,
      { label: `edit:${brief.section}`, phase: 'Write', schema: WRITER_SCHEMA });
    if (!merged) return { section: brief.section, status: 'BLOCKED', stage: 'L2', detail: ['editor returned null'], drafts: clean.map(d => d.paragraphs) };
    const g = sectionGate(merged, brief);
    if (!g.pass) return { section: brief.section, status: 'BLOCKED', stage: 'L2', detail: g.blocks.slice(0, 12), drafts: clean.map(d => d.paragraphs) };
    return { section: brief.section, status: 'WRITTEN', brief, merged, drafts: clean.map(d => d.paragraphs), flags: g.flags };
  }));
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
