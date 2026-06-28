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
      allowedTokens: b.allowed_tokens,
      allowedKeys: b.allowed_cites.concat(['harford1999','shleifer_vishny2003','louis2004','verrecchia1983','dye1985','hollander2010','matsumoto2011','lm2011','bertrand_schoar2003']),
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
  if (!g.pass) return { section: brief.section, status: 'BLOCKED', stage: 'L2', detail: g.blocks.slice(0, 12) };
  return { section: brief.section, status: 'WRITTEN', brief, merged, flags: g.flags };
}

// collect the verbatim source quotes for a section's theory props (the load-bearing honesty evidence)
function quoteBlock(brief) {
  const qs = [];
  for (const pa of brief.paragraphs) for (const p of pa.props)
    if (p.verification && p.verification.evidence_quotes)
      qs.push(`PROP ${p.prop_id} claims: "${p.statement}"\nSOURCE (verbatim, from ${(p.verification.source && p.verification.source.title) || 'the cited paper'}; verdict ${p.verification.verdict}):\n${p.verification.evidence_quotes}`);
  return qs.length ? `\nVERBATIM SOURCE SUPPORT (check each theory claim against its source; flag any claim that says MORE than the quote supports):\n${qs.join('\n\n')}\n` : '';
}

async function auditSection(prev, thesisMap, coherenceIssues) {
  if (prev.status !== 'WRITTEN') return prev;
  const { brief, merged } = prev;
  const map = thesisMap ? `\nWHOLE-THESIS MAP (for cross-reference awareness; audit ONLY this section's prose, but know the rest exists):\n${thesisMap}\n` : '';
  const draft = `${map}DRAFT UNDER AUDIT (this section):\n${JSON.stringify(merged.paragraphs, null, 1)}`;
  const HONESTY = LANES[0][1];                 // lane-1 body
  const OTHERS = LANES.slice(1);               // the other 5 lanes
  // L3a: HONESTY sub-panel (3 agents, refute-by-default, WITH the verbatim source quotes) -- thesis-killer gets redundancy
  const honestyTasks = [0, 1, 2].map(v => () =>
    agent(`${HONESTY}\n\nREFUTE-BY-DEFAULT: treat every theory/result claim as OVER-stated until the prop+quote clearly support it; if uncertain, FLAG. You PROPOSE fixes, never rewrite.\n\n${brmain(brief)}\n${quoteBlock(brief)}\n${draft}`,
      { label: `audit:${brief.section}:honesty${v + 1}`, phase: 'Audit', schema: AUDIT_SCHEMA }).then(a => ({ lane: 'honesty', issues: (a && a.issues) || [] })));
  // L3b: the other 5 exclusive lanes, 1 agent each (PROPOSE only)
  const otherTasks = OTHERS.map(([key, body]) => () =>
    agent(`${body}\n\nYou audit ONLY this lane; PROPOSE fixes, do not rewrite. If a paragraph is clean in your lane, emit nothing for it.\n\n${brmain(brief)}\n${draft}`,
      { label: `audit:${brief.section}:${key}`, phase: 'Audit', schema: AUDIT_SCHEMA }).then(a => ({ lane: key, issues: (a && a.issues) || [] })));
  const audits = (await parallel([...honestyTasks, ...otherTasks])).filter(Boolean);
  // fold in the WHOLE-THESIS coherence issues that touch this section
  const mine = (coherenceIssues || []).filter(i => (i.section && (i.section === brief.section || i.section === brief.stem)) || (i.para_id || '').includes(brief.section));
  const allIssues = audits.flatMap(a => a.issues.map(i => ({ ...i, lane: a.lane }))).concat(mine.map(i => ({ ...i, lane: 'coherence' })));
  // L4: judge applies high-confidence fixes by MINIMAL edit, refute-by-default on honesty/number claims
  const final = await agent(
    `You are the chief editor. Apply ONLY well-supported audit fixes to the draft by MINIMAL edit (prefer the existing wording; change the least). Reject spurious or hedge-weakening fixes (refute-by-default for honesty/number claims). Invent no new numbers/citations. Output the full corrected section.\n\n${brmain(brief)}\n\nDRAFT:\n${JSON.stringify(merged.paragraphs, null, 1)}\n\nAUDIT ISSUES (${allIssues.length}):\n${JSON.stringify(allIssues, null, 1)}`,
    { label: `judge:${brief.section}`, phase: 'Audit', schema: WRITER_SCHEMA });
  const g = sectionGate(final, brief);
  if (!g.pass) return { section: brief.section, status: 'BLOCKED', stage: 'FINAL-GATE', detail: g.blocks.slice(0, 12), final };
  return { section: brief.section, status: 'OK', final, flags: g.flags, audit_count: allIssues.length };
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

// ===== BARRIER: ALL prose written before ANY audit =====
// ===== PHASE B -- AUDIT the WHOLE thesis at once =====
log(`PHASE B: audit -- whole thesis at once (${writtenOK.length} written, ${written.length - writtenOK.length} blocked at write)`);
const thesisFull = JSON.stringify(writtenOK.map(w => ({ section: w.section, paragraphs: w.merged.paragraphs.map(p => ({ para_id: p.para_id, final_prose: p.final_prose })) })));
// (1) GLOBAL COHERENCE PANEL -- 3 agents each read the FULL thesis, cross-section ONLY (thesis-level scrutiny gets redundancy)
const COH_HEADS = [
  'You are the thesis coherence auditor.',
  'Act as a journal referee reading the whole thesis end-to-end for internal consistency.',
  'You are the consistency editor responsible for the complete thesis reading as one document.',
];
const cohPanel = (await parallel(COH_HEADS.map((h, v) => () =>
  agent(`${h} Read the ENTIRE drafted thesis below and flag ONLY cross-section problems: the abstract or Section 1 preview contradicting the results; terminology or notation drifting between sections; a claim in one section inconsistent with another; a "see Section X" reference that does not match X's content; a broken narrative arc. Do NOT re-audit within-section wording (other auditors own that). Tag each issue with the section it belongs to (e.g. "3.4"). PROPOSE fixes, never rewrite.\n\nFULL THESIS:\n${thesisFull}`,
    { label: `audit:coherence${v + 1}-WHOLE`, phase: 'Audit', schema: AUDIT_SCHEMA })
))).filter(Boolean);
const coherenceIssues = cohPanel.flatMap(c => (c && c.issues) || []);
log(`coherence panel (3): ${coherenceIssues.length} cross-section issue(s)`);
// (2) per-section DEEP audit + judge, each given a compact whole-thesis map + the coherence issues that touch it
const compactMap = JSON.stringify(writtenOK.map(w => ({ section: w.section, summary: w.brief.paragraphs.map(p => p.thin_claim).filter(Boolean) })));
const results = await parallel(writtenOK.map(w => () => auditSection(w, compactMap, coherenceIssues)));
results.push(...written.filter(w => w.status !== 'WRITTEN'));
const ok = results.filter(r => r && r.status === 'OK');
const blocked = results.filter(r => r && r.status === 'BLOCKED');
log(`DONE: ${ok.length} OK, ${blocked.length} BLOCKED`);
return { ok: ok.map(r => r.section), blocked: blocked.map(r => ({ section: r.section, stage: r.stage, detail: r.detail })), results };
