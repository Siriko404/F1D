#!/usr/bin/env node
// generate-prompts.js — mechanical S2 build: slot-fill prompt-template.md per expert
// from a panel-spec.json, prove the hard-rules block is byte-exact from the template
// (template-anchored — a filled-text slice point was hijacked by duty strings twice),
// enforce the answer-key seal (paths hard-fail; pasted expectations TEXT warns for the
// human gate), lint manifest paths to FILES, and persist spec + template snapshot so
// verify-readback.js can re-derive every prompt and catch post-generation hand-edits.
//
//   node generate-prompts.js <panel-spec.json>
// Writes <run_dir>/prompts/<slug>.md, <run_dir>/context/<slug>-manifest.json,
// <run_dir>/context/panel-spec.json, <run_dir>/context/prompt-template.snapshot.md.
// Exports buildAll() — ONE derivation shared by generation and re-verification.
const fs = require('fs');
const path = require('path');
const { norm } = require('./norm');

const HEADING = 'HARD RULES (identical for every expert on this panel)';

function fail(m) { const e = new Error(m); e.atc = true; throw e; }

// Anchor on the TEMPLATE (skill-controlled), never on filled output (slot-influenced).
// A duty legitimately containing the heading words is harmless.
function splitTemplate(templateText) {
  const parts = templateText.split('---TEMPLATE BEGINS---');
  if (parts.length !== 2) fail('template missing ---TEMPLATE BEGINS--- marker');
  const body = parts[1].split('---TEMPLATE ENDS---')[0].trim();
  const i = body.indexOf(HEADING);
  if (i === -1) fail('template body missing the HARD RULES heading');
  if (body.indexOf(HEADING, i + HEADING.length) !== -1) fail('template body must contain the HARD RULES heading exactly once');
  return { pre: body.slice(0, i), rules: body.slice(i) };
}

// Slot-value sanitization. Fill is sequential split/join, so a value containing a later
// '{{SLOT}}' would get substituted — '{{' is the one dangerous token. Cost: a duty that
// must quote slot syntax has to describe it without the braces.
function checkSlotValue(slug, name, v) {
  if (typeof v !== 'string' || !v.trim()) fail(`${slug}: ${name} required (non-empty string)`);
  if (v.includes('{{')) fail(`${slug}: ${name} contains '{{' (slot-injection guard) — describe slot syntax without braces`);
  if (/[\x00-\x09\x0b-\x1f\x7f]/.test(v)) fail(`${slug}: ${name} contains control characters`);
}

function sanitizeSpec(spec) {
  if (!spec || !Array.isArray(spec.experts) || !spec.sources || typeof spec.run_dir !== 'string') fail('spec needs run_dir, sources, experts');
  // subject slot carries the QUESTION verbatim — the brief FILE never enters panel context.
  checkSlotValue('spec', 'subject', spec.subject);
  checkSlotValue('spec', 'journal_js', spec.journal_js);
  for (const ex of spec.experts) {
    checkSlotValue(ex.slug || '(unnamed expert)', 'slug', ex.slug);
    checkSlotValue(ex.slug, 'aspect', ex.aspect);
    if (/\n/.test(ex.aspect)) fail(`${ex.slug}: aspect must be single-line`);
    checkSlotValue(ex.slug, 'role', ex.role);
    checkSlotValue(ex.slug, 'tools', ex.tools);
    if (!Array.isArray(ex.duties) || ex.duties.length === 0) fail(`${ex.slug}: duties must be a non-empty array`);
    ex.duties.forEach((d, i) => checkSlotValue(ex.slug, `duties[${i}]`, d));
    if (!Array.isArray(ex.cids) || ex.cids.length === 0) fail(`${ex.slug}: cids must be a non-empty array`);
    if (!Array.isArray(ex.must_read)) fail(`${ex.slug}: must_read must be an array`);
  }
}

function fill(part, ex, manifest, spec) {
  const runDir = spec.run_dir;
  const mustReadCids = manifest.filter((m) => m.must_read).map((m) => m.id);
  const journalPath = runDir + '/journal/' + ex.slug + '.jsonl';
  return part
    .split('{{ASPECT}}').join(ex.aspect)
    .split('{{ROLE}}').join(ex.role)
    .split('{{DUTIES}}').join(ex.duties.map((d) => '- ' + d).join('\n'))
    .split('{{SUBJECT}}').join(spec.subject)
    .split('{{MANIFEST_JSON}}').join(JSON.stringify(manifest, null, 2))
    .split('{{ALL_CIDS}}').join(JSON.stringify(manifest.map((m) => m.id)))
    .split('{{MUST_READ_CIDS}}').join(JSON.stringify(mustReadCids))
    .split('{{TOOLS}}').join(ex.tools)
    .split('{{RUN_DIR}}').join(runDir)
    .split('{{JOURNAL_JS}}').join(spec.journal_js)
    .split('{{JOURNAL_PATH}}').join(journalPath);
}

// Pure derivation: spec + template text -> per-expert filled prompt + manifest.
// Used at S2 generation AND at read-back re-verification (PH a27).
function buildAll(spec, templateText) {
  sanitizeSpec(spec);
  const { pre, rules } = splitTemplate(templateText);
  return spec.experts.map((ex) => {
    const manifest = ex.cids.map((cid, i) => {
      const s = spec.sources[cid];
      if (!s) fail(`expert ${ex.slug}: unknown source id ${cid}`);
      return { id: 'C' + (i + 1), source: cid, path: s.path, what: s.what, must_read: ex.must_read.includes(cid) };
    });
    const filledRules = fill(rules, ex, manifest, spec);
    const filled = fill(pre, ex, manifest, spec) + filledRules;
    if (/\{\{[A-Z_]+\}\}/.test(filled)) fail(`expert ${ex.slug}: unfilled slot ${filled.match(/\{\{[A-Z_]+\}\}/)[0]}`);
    return { ex, manifest, filled, filledRules };
  });
}

function realLower(p) { try { return fs.realpathSync(p).toLowerCase(); } catch { return null; } }

function main() {
  const specPath = process.argv[2];
  if (!specPath) fail('usage: generate-prompts.js <panel-spec.json>');
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const template = fs.readFileSync(spec.template, 'utf8');
  const runDir = spec.run_dir;

  // --- Seal part 1 (hard-fail): no source path may BE the brief or expectations file
  // (realpath — a symlinked alias is the same file).
  const banned = [path.join(runDir, 'subject-brief.md'), path.join(runDir, 'expectations-sealed.md')].map(realLower).filter(Boolean);
  for (const [cid, s] of Object.entries(spec.sources)) {
    const rp = realLower(s.path);
    if (rp && banned.includes(rp)) fail(`answer-key seal: source '${cid}' points at ${s.path} — the brief/expectations file never enters panel context (the subject slot carries the question)`);
    // Manifest lint: C-ids must point at existing FILES — a directory C-id silently
    // wiped 47 honest quotes to 'source unreadable' in Test 1.
    let st = null;
    try { st = fs.statSync(s.path); } catch { /* missing */ }
    if (!st) fail(`manifest lint: source '${cid}' path does not exist: ${s.path}`);
    if (!st.isFile()) fail(`manifest lint: source '${cid}' is not a FILE: ${s.path} — expand directories into explicit file entries at S3`);
  }

  // --- Seal part 2: expectations must be sealed BEFORE generation. A brief with a real
  // Expectations section (not the N/A sentinel) but no expectations-sealed.md = Test 1 leak layout.
  const expPath = path.join(runDir, 'expectations-sealed.md');
  const briefPath = path.join(runDir, 'subject-brief.md');
  if (!fs.existsSync(expPath) && fs.existsSync(briefPath)) {
    const brief = fs.readFileSync(briefPath, 'utf8');
    const m = brief.match(/^#{1,6}[^\n]*expectations[^\n]*\n([\s\S]*?)(?=^#{1,6}\s|\n*$(?![\s\S]))/im);
    if (m && m[1].trim() && !/N\/A/i.test(m[1])) fail('answer-key seal: subject-brief.md carries an Expectations section but expectations-sealed.md does not exist — move the expectations there BEFORE generating prompts');
  }

  const built = buildAll(spec, template);

  for (const b of built) {
    // --- Seal part 3 (hard-fail): no prompt or manifest may reference the sealed files
    // by name (a leaked pointer is as good as leaked content).
    const manJson = JSON.stringify(b.manifest);
    for (const bad of ['subject-brief', 'expectations-sealed']) {
      if (b.filled.includes(bad)) fail(`answer-key seal: expert ${b.ex.slug}'s prompt contains '${bad}' — prompts must never reference the sealed files`);
      if (manJson.includes(bad)) fail(`answer-key seal: expert ${b.ex.slug}'s manifest contains '${bad}'`);
    }
    // --- Seal part 4 (WARN, not fail: expectations legitimately quote the same sources
    // duties quote, so text-overlap can't hard-fail; the human gate judges the printed span).
    if (fs.existsSync(expPath)) {
      const E = norm(fs.readFileSync(expPath, 'utf8'));
      const F = norm(b.filled);
      // Stride-40 windows + the final window (a short file's tail must not slip past).
      const starts = [];
      for (let i = 0; i + 80 <= E.length; i += 40) starts.push(i);
      if (E.length >= 80) starts.push(E.length - 80);
      for (const i of starts) {
        const w = E.slice(i, i + 80);
        if (F.includes(w)) {
          process.stdout.write(`WARNING answer-key overlap in ${b.ex.slug}'s prompt — an 80-char span of expectations-sealed.md appears in it. Judge at ratification:\n  "...${w}..."\n`);
          break;
        }
      }
    }
    // Identity proof, template-anchored: the rules half re-derived from this expert's
    // slot values must equal the tail of the written prompt byte-for-byte. Cross-expert
    // drift is impossible (ONE template, fill-only); hand-edits are caught at read-back.
    const expected = fill(splitTemplate(template).rules, b.ex, b.manifest, spec);
    if (!b.filled.endsWith(expected)) fail(`HARD RULES DRIFT in ${b.ex.slug} — written prompt does not end with the template-derived rules block`);
  }

  fs.mkdirSync(path.join(runDir, 'prompts'), { recursive: true });
  fs.mkdirSync(path.join(runDir, 'context'), { recursive: true });
  fs.mkdirSync(path.join(runDir, 'journal'), { recursive: true });
  fs.mkdirSync(path.join(runDir, 'downloads'), { recursive: true });
  const summary = [];
  for (const b of built) {
    fs.writeFileSync(path.join(runDir, 'prompts', b.ex.slug + '.md'), b.filled, 'utf8');
    fs.writeFileSync(path.join(runDir, 'context', b.ex.slug + '-manifest.json'), JSON.stringify({ aspect: b.ex.aspect, journal: runDir + '/journal/' + b.ex.slug + '.jsonl', manifest: b.manifest }, null, 2), 'utf8');
    summary.push(`  ${b.ex.slug}: ${b.manifest.length} sources (${b.ex.must_read.length} must_read), prompt ${b.filled.length} chars`);
  }
  // Persist derivation inputs so verify-readback.js can re-prove prompt identity later.
  // Editing prompt AND spec AND snapshot together defeats this — that residual is the S2 gate.
  fs.writeFileSync(path.join(runDir, 'context', 'panel-spec.json'), JSON.stringify(spec, null, 2), 'utf8');
  fs.writeFileSync(path.join(runDir, 'context', 'prompt-template.snapshot.md'), template, 'utf8');
  process.stdout.write(`OK — ${spec.experts.length} prompts generated; rules block template-derived byte-exact; spec + template snapshot persisted for read-back identity re-proof.\n` + summary.join('\n') + '\n');
}

module.exports = { buildAll, splitTemplate, HEADING };
if (require.main === module) {
  try { main(); }
  catch (e) { process.stdout.write('ERROR: ' + e.message + '\n'); process.exit(1); }
}
