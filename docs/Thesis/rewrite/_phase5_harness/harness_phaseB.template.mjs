// harness_phaseB.template.mjs -- Phase B only (write phase already done; prose loaded from DATA).
// Sina's design: 3 exhaustive red-team auditors (each reads the WHOLE thesis: every aspect + coherence
// across body+findings + best-fix proposals) -> ONE boss applies the well-supported fixes as MINIMAL
// PATCHES (changed paragraphs only; rest passes through) -> deterministic gate. Build injects DATA + gates.
export const meta = {
  name: 'prose-harness-phaseB',
  description: '3 exhaustive red-teams -> 1 patch-boss -> gate, on the already-written thesis prose',
  phases: [{ title: 'RedTeam' }, { title: 'Boss' }],
};

const DATA = __DATA__;   // [{section, stem, title, paragraphs:[{para_id,final_prose}], bright_lines, register_global, allowed_tokens_all, allowed_cites_all, number_table_map_all, table_xwalk, table_labels, number_context:{val:meaning}, props:[{prop_id, register_locks, quote}]}]
__GATES__                // defines runGates(par) etc.

// ---- assemble the whole thesis in reading order (for red-team + boss context) ----
function thesisText() {
  return DATA.map(s => `\n===== SECTION ${s.section}${s.title ? ' (' + s.title + ')' : ''} =====\n` +
    s.paragraphs.map(p => `[${p.para_id}] ${p.final_prose}`).join('\n\n')).join('\n');
}

// ---- the locked SOURCE FACTS each red-team judges the prose against ----
function sourceFacts() {
  const out = [];
  for (const s of DATA) {
    const locks = [...new Set(s.props.flatMap(p => p.register_locks || []))];
    const quotes = s.props.filter(p => p.quote).map(p => `  PROP ${p.prop_id}: "${p.quote}"`);
    const nums = Object.entries(s.number_context || {}).map(([v, d]) => `  ${v} = ${d}`);
    out.push(`SECTION ${s.section}:` +
      (s.bright_lines && s.bright_lines.length ? `\n HONESTY FLOOR: ${s.bright_lines.join(' | ')}` : '') +
      (locks.length ? `\n REGISTER LOCKS: ${locks.join(' | ')}` : '') +
      (nums.length ? `\n NUMBERS IN CONTEXT (value = its only correct meaning):\n${nums.join('\n')}` : '') +
      (quotes.length ? `\n VERBATIM SOURCE QUOTES (a claim may not say more than its quote):\n${quotes.join('\n')}` : ''));
  }
  return out.join('\n\n');
}

const FORBIDDEN = 'suppress, dampen, manipulat(e), "to mask"/"in order to mask", "we are the first"; and -- EXCEPT in an explicit denial ("we do NOT detect", "concentration, NOT strict specificity") -- the words "detect" and "strict specificity"';

// ===== LAYER 1: 3 exhaustive red-team auditors (paraphrased), each reads the WHOLE thesis =====
const RT_HEADS = [
  'You are an adversarial referee auditing this entire empirical corporate-finance thesis. Assume every sentence is wrong until the prose earns it.',
  'You are a hostile journal reviewer reading the whole thesis to find every flaw before it reaches print.',
  'You are a skeptical thesis examiner reading the complete thesis end to end, hunting overclaims and incoherence.',
];
const REPORT_SCHEMA = { type: 'object', required: ['issues'], properties: { issues: { type: 'array', items: {
  type: 'object', required: ['section', 'para_id', 'aspect', 'problem', 'best_fix'], properties: {
    section: { type: 'string' }, para_id: { type: 'string' },
    aspect: { enum: ['honesty', 'number', 'plain_language', 'flow', 'coherence', 'completeness', 'other'] },
    problem: { type: 'string' },
    best_fix: { type: 'string', description: 'the exact, minimal rewrite that fixes it' } } } } } };

async function redTeam(fullThesis, facts) {
  const panel = await parallel(RT_HEADS.map((h, v) => () => agent(
    `${h}\n\nYou have NO access to the repository and no need for it -- everything to judge is in the SOURCE FACTS and WHOLE THESIS below. Do NOT use Grep/Glob/Bash/Read or any tool to look anything up; judge ONLY from the text given, and return your report ONLY via the StructuredOutput tool.\n\n` +
    `A deterministic gate already enforces the MECHANICAL checks (citation keys valid, numbers and stars present, \\ref table tags, forbidden words, LaTeX) -- do NOT audit those, they are handled. Audit ONLY what a careful reader must judge, all fully answerable from what is given. For every real problem give the BEST concrete minimal fix.\n\nCHECK:\n` +
    `- OVERCLAIM vs SOURCE: does any sentence say MORE than its verbatim quote or register lock allows? (correlational not causal; the stock arm a noisy flat null; concentration not strict specificity; we interpret, we do not detect; supportive not definitive; mechanism stays open.)\n` +
    `- NUMBER-IN-CONTEXT: is each figure attached to its ONE correct meaning per NUMBERS IN CONTEXT (right arm, right clock, right comparison)? flag a real number used on the wrong claim.\n` +
    `- PLAIN LANGUAGE: would a smart reader with NO finance training follow on first read? flag over-long/dense sentences and un-glossed jargon.\n` +
    `- FLOW + COHERENCE & COHESIVENESS across the WHOLE body and findings: do all sections tell ONE consistent story (framing Sec 2, findings Sec 3-4, conclusion Sec 5)? consistent terms/notation, no contradictions, transitions and seams hold.\n` +
    `- COMPLETENESS: nothing load-bearing dropped or duplicated.\n\n` +
    `BE SELECTIVE AND TERSE: report only issues that matter (aim for ~15-20, not every nitpick); make "problem" and "best_fix" ONE short sentence each.\n\n` +
    `SOURCE FACTS (judge against THIS; never invent new facts):\n${facts}\n\nWHOLE THESIS:\n${fullThesis}`,
    { label: `redteam:v${v + 1}`, phase: 'RedTeam', schema: REPORT_SCHEMA, effort: 'medium' })));
  return panel.filter(Boolean).flatMap(r => (r && r.issues) || []);
}

// ===== LAYER 2: ONE boss -- whole thesis + all reports -> MINIMAL PATCHES (changed paragraphs only) =====
const PATCH_SCHEMA = { type: 'object', required: ['patches'], properties: { patches: { type: 'array', items: {
  type: 'object', required: ['section', 'para_id', 'final_prose'], properties: {
    section: { type: 'string' }, para_id: { type: 'string' },
    final_prose: { type: 'string', description: 'the full final LaTeX text of this one paragraph, after the edit' } } } } } };

async function boss(fullThesis, facts, issues) {
  return await agent(
    `You are the chief editor delivering the FINAL thesis. Below are the whole thesis, the locked SOURCE FACTS, and the red-team's issues with proposed fixes. Apply the WELL-SUPPORTED fixes by MINIMAL EDIT, working section by section. Rules:\n` +
    `- You have everything below; do NOT use Grep/Glob/Bash/Read or any tool to look at the repository -- edit only from the text given, and return ONLY via the StructuredOutput tool.\n` +
    `- Change only what a fix truly requires; keep wording that is already clean.\n` +
    `- REJECT any fix that weakens a hedge, alters a number/sign/significance star, or softens an honesty or register lock (refute-by-default on those).\n` +
    `- Keep every number, citation, \\ref, hedge and register lock exact. Invent nothing -- no new fact, number, citation, or table.\n` +
    `- Never write a forbidden word as a positive claim (${FORBIDDEN}).\n` +
    `- Improve plain language and cross-section coherence where the red team flags it, without changing meaning.\n` +
    `- OUTPUT ONLY THE PARAGRAPHS YOU CHANGED, each as {section, para_id, final_prose} carrying that paragraph's COMPLETE final text. Omit every paragraph you did not change.\n\n` +
    `SOURCE FACTS:\n${facts}\n\nRED-TEAM ISSUES + PROPOSED FIXES:\n${JSON.stringify(issues, null, 1)}\n\nWHOLE THESIS:\n${fullThesis}`,
    { label: 'boss:final', phase: 'Boss', schema: PATCH_SCHEMA, effort: 'medium' });
}

function gateProse(s, prose) {
  return runGates({ prose: prose || '', allowedTokens: s.allowed_tokens_all || [], allowedKeys: s.allowed_cites_all || [],
    numberTables: s.number_table_map_all || null, props: [] });
}

// ===== RUN =====
const facts = sourceFacts();
const fullThesis = thesisText();
log(`PHASE-B: 3 exhaustive red-teams on the WHOLE thesis (${DATA.length} sections)`);
const issues = await redTeam(fullThesis, facts);
log(`red-team: ${issues.length} issue(s)`);
log('BOSS: applying well-supported fixes as minimal patches');
const bres = await boss(fullThesis, facts, issues);
const patches = (bres && bres.patches) || [];
log(`boss: ${patches.length} paragraph patch(es) proposed`);

// assemble final = DATA prose with patches applied -- but ONLY if the patched paragraph stays gate-clean
const patchMap = {};
for (const pt of patches) patchMap[`${pt.section}|${pt.para_id}`] = pt.final_prose;
let edited = 0, rejected = 0;
const sections = DATA.map(s => {
  const paras = s.paragraphs.map(p => {
    const cand = patchMap[`${s.section}|${p.para_id}`];
    if (cand != null && cand !== p.final_prose) {
      const g = gateProse(s, cand);
      if (g.pass) { edited++; return { para_id: p.para_id, final_prose: cand, edited: true }; }
      rejected++; return { para_id: p.para_id, final_prose: p.final_prose, edited: false, patch_rejected: g.blocks };
    }
    return { para_id: p.para_id, final_prose: p.final_prose, edited: false };
  });
  const blocks = [], flags = [];
  for (const p of paras) { const g = gateProse(s, p.final_prose); blocks.push(...g.blocks.map(x => `${p.para_id}: ${x}`)); flags.push(...g.flags.map(x => `${p.para_id}: ${x}`)); }
  return { section: s.section, stem: s.stem, status: blocks.length ? 'BLOCKED' : 'OK', paragraphs: paras, blocks, flags };
});
const ok = sections.filter(s => s.status === 'OK').length;
const blocked = sections.filter(s => s.status === 'BLOCKED');
log(`DONE: ${ok}/${DATA.length} OK, ${blocked.length} BLOCKED, ${edited} paras edited, ${rejected} patches rejected (would break gate)`);
return { ok, blocked: blocked.map(b => ({ section: b.section, blocks: b.blocks })), edited, rejected, sections, issues, patches };
