// Tests for prompt-template.md — the slot contract (Fix 5a regression guard).
// Every {{SLOT}} used in the template BODY must be declared on the `Slots:` line, so a
// human building/reading a generator can never miss one (the ALL_CIDS/MUST_READ_CIDS gap).
// Plain node, no framework. Prints "N passed, M failed", exit 1 on any failure.
const fs = require('fs');
const path = require('path');

const tpl = fs.readFileSync(path.join(__dirname, 'prompt-template.md'), 'utf8');
let n = 0, pass = 0, fail = 0;
function t(name, cond) {
  n++;
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name); }
}

const lines = tpl.split('\n');

// The `Slots:` declaration may wrap across the line(s) immediately after the header.
const slotsIdx = lines.findIndex((l) => l.startsWith('Slots:'));
t('template has a Slots: declaration line', slotsIdx !== -1);
let decl = lines[slotsIdx] || '';
for (let i = slotsIdx + 1; i < lines.length && /\{\{[A-Z_]+\}\}/.test(lines[i]) && !lines[i].includes('---'); i++) decl += ' ' + lines[i];
const declared = new Set((decl.match(/\{\{[A-Z_]+\}\}/g) || []).map((s) => s.slice(2, -2)));

// Body = everything AFTER ---TEMPLATE BEGINS--- (the actual instrument the agent gets).
const body = tpl.split('---TEMPLATE BEGINS---')[1] || '';
const used = new Set((body.match(/\{\{[A-Z_]+\}\}/g) || []).map((s) => s.slice(2, -2)));

const missing = [...used].filter((s) => !declared.has(s)).sort();
t('every {{SLOT}} used in the body is declared on the Slots: line', missing.length === 0);
if (missing.length) console.log('       undeclared slots used in body: ' + missing.join(', '));

// The two slots the Fix-5a gap was about must now be present.
t('ALL_CIDS declared', declared.has('ALL_CIDS'));
t('MUST_READ_CIDS declared', declared.has('MUST_READ_CIDS'));

// Sanity: the declared set should not list phantom slots the body never uses (keeps the
// contract tight both ways).
const phantom = [...declared].filter((s) => !used.has(s)).sort();
t('no declared slot is unused by the body', phantom.length === 0);
if (phantom.length) console.log('       declared but unused: ' + phantom.join(', '));

// Item 8 honesty pins: the template claims only what a mechanism actually does.
t('false batch claim removed (no code fails a run on batching)', !body.includes('fails the run'));
t('loc honestly marked advisory (file-level mechanical check)', body.includes('Location is advisory'));
// Item 1: raw-capture mandate present; discovery tools never snapshot.
t('raw-capture mandate present (NON-LLM channel)', body.includes('NON-LLM channel') && body.includes('DISCOVERY'));
// Item 3: programmatic quoting duty present.
t('programmatic quoting duty present (text-extraction tool)', body.includes('text-extraction tool'));
// Item 4 cost taught in the rules: one evidence item per block.
t('block rule taught (one evidence item per block)', body.includes('one evidence item per block'));
// The brief pointer is gone for good (item 9).
t('no reference to the subject-brief file anywhere in the body', !body.includes('subject-brief'));

// Regeneration proof: the revised template still generates end-to-end.
const { execFileSync } = require('child_process');
const os = require('os');
const d = fs.mkdtempSync(path.join(os.tmpdir(), 'atc-tpl-regen-'));
fs.writeFileSync(path.join(d, 'src.md'), 'regeneration fixture source content here', 'utf8');
fs.writeFileSync(path.join(d, 'spec.json'), JSON.stringify({
  template: path.join(__dirname, 'prompt-template.md'), journal_js: path.join(__dirname, 'journal.js'), run_dir: d,
  subject: 'Regeneration-proof question for the panel.',
  sources: { s1: { path: path.join(d, 'src.md'), what: 'fixture' } },
  experts: [{ slug: 'e1', aspect: 'facet', role: 'You inspect.', duties: ['Work the facet.'], tools: 'Read', cids: ['s1'], must_read: [] }],
}), 'utf8');
let regen = true;
try { execFileSync('node', [path.join(__dirname, 'generate-prompts.js'), path.join(d, 'spec.json')], { encoding: 'utf8' }); } catch { regen = false; }
t('revised template regenerates through generate-prompts.js', regen);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
