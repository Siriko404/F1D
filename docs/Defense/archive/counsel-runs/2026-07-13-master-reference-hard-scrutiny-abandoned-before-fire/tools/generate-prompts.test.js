// Tests for generate-prompts.js -- the S2 mechanical prompt builder (new 5th suite;
// the generator had ZERO coverage anywhere in the old 100-test baseline, PH a10).
// Plain node, no framework. Prints "N passed, M failed", exit 1 on any failure.
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const GP = path.join(__dirname, 'generate-prompts.js');
const TPL = path.join(__dirname, 'prompt-template.md');
let pass = 0, fail = 0;
function t(name, cond) { if (cond) { pass++; console.log('  ok   ' + name); } else { fail++; console.log('  FAIL ' + name); } }
function mk(name) { return fs.mkdtempSync(path.join(os.tmpdir(), 'atc-gp-' + name + '-')); }
function runSpec(d, spec) {
  const sp = path.join(d, 'spec.json');
  fs.writeFileSync(sp, JSON.stringify(spec), 'utf8');
  try { return { code: 0, out: execFileSync('node', [GP, sp], { encoding: 'utf8' }) }; }
  catch (e) { return { code: e.status, out: (e.stdout || '') + (e.stderr || '') }; }
}
function baseSpec(d, over) {
  fs.writeFileSync(path.join(d, 'src.md'), 'source fixture content for the panel to read here', 'utf8');
  return Object.assign({
    template: TPL,
    journal_js: path.join(__dirname, 'journal.js'),
    run_dir: d,
    subject: 'The exact question under study, pasted verbatim for the panel to answer.',
    sources: { s1: { path: path.join(d, 'src.md'), what: 'fixture source' } },
    experts: [{ slug: 'e1', aspect: 'facet one', role: 'You inspect things closely.', duties: ['Do the assigned work thoroughly.'], tools: 'Read, Grep', cids: ['s1'], must_read: ['s1'] }],
  }, over || {});
}

// -- clean generation: prompts + manifests + persisted derivation inputs --
let d = mk('clean');
let r = runSpec(d, baseSpec(d));
t('clean spec generates (exit 0)', r.code === 0 && /OK /.test(r.out));
let prompt = fs.readFileSync(path.join(d, 'prompts', 'e1.md'), 'utf8');
t('prompt carries the subject text verbatim (no brief pointer)', prompt.includes('The exact question under study, pasted verbatim'));
t('prompt never references the sealed files', !prompt.includes('subject-brief') && !prompt.includes('expectations-sealed'));
t('spec + template snapshot persisted for read-back identity re-proof',
  fs.existsSync(path.join(d, 'context', 'panel-spec.json')) && fs.existsSync(path.join(d, 'context', 'prompt-template.snapshot.md')));
t('manifest written with C-ids', fs.readFileSync(path.join(d, 'context', 'e1-manifest.json'), 'utf8').includes('"C1"'));

// -- regression: THIS run's live bug -- a duty containing the rules heading is LEGAL
// (template-anchored split; the old indexOf-on-filled-text sliced at the wrong offset) --
d = mk('heading');
r = runSpec(d, baseSpec(d, { experts: [{ slug: 'e1', aspect: 'facet one', role: 'You inspect.', tools: 'Read',
  duties: ['Note that the heading HARD RULES (identical for every expert on this panel) is discussed here.'], cids: ['s1'], must_read: [] }] }));
t('duty containing the HARD RULES heading generates fine (indexOf fragility dead)', r.code === 0);

// -- answer-key seal part 1: source path IS the brief/expectations file -> die --
d = mk('sealpath');
fs.writeFileSync(path.join(d, 'subject-brief.md'), 'brief with expectations inside it', 'utf8');
let s = baseSpec(d);
s.sources.s1 = { path: path.join(d, 'subject-brief.md'), what: 'oops' };
r = runSpec(d, s);
t('source path = subject-brief.md rejected', r.code !== 0 && /answer-key seal/.test(r.out));
let linked = false;
try { fs.symlinkSync(path.join(d, 'subject-brief.md'), path.join(d, 'alias.md'), 'file'); linked = true; } catch { /* no symlink perms */ }
if (linked) {
  s = baseSpec(d);
  s.sources.s1 = { path: path.join(d, 'alias.md'), what: 'aliased' };
  r = runSpec(d, s);
  t('symlinked alias of the brief rejected (realpath, not string compare)', r.code !== 0 && /answer-key seal/.test(r.out));
} else { console.log('  skip symlink alias test (no perms)'); }

// -- answer-key seal part 2: brief carries real Expectations while nothing is sealed --
d = mk('sealbrief');
fs.writeFileSync(path.join(d, 'subject-brief.md'), '# Brief\n\n## Expectations\n\n1. The panel should find the rar file.\n', 'utf8');
r = runSpec(d, baseSpec(d));
t('brief with real Expectations section + no sealed file rejected', r.code !== 0 && /answer-key seal/.test(r.out));
fs.writeFileSync(path.join(d, 'subject-brief.md'), '# Brief\n\n## Expectations\n\nN/A by design (advise-type run).\n', 'utf8');
r = runSpec(d, baseSpec(d));
t('brief with N/A sentinel Expectations section accepted', r.code === 0);

// -- answer-key seal part 3: prompt text referencing the sealed files -> die --
d = mk('sealref');
r = runSpec(d, baseSpec(d, { subject: 'Answer the question; see subject-brief.md for details.' }));
t('prompt containing subject-brief reference rejected', r.code !== 0 && /answer-key seal/.test(r.out));

// -- answer-key seal part 4 (wave-2 amendment): pasted expectations TEXT warns, never dies --
d = mk('sealtext');
const expLine = 'The panel is expected to independently rediscover the junk archive sitting in the skills directory tree.';
fs.writeFileSync(path.join(d, 'expectations-sealed.md'), '# Expectations\n\n' + expLine + '\n', 'utf8');
r = runSpec(d, baseSpec(d, { experts: [{ slug: 'e1', aspect: 'facet one', role: 'You inspect.', tools: 'Read',
  duties: [expLine], cids: ['s1'], must_read: [] }] }));
t('pasted expectations text: WARNING printed, generation proceeds', r.code === 0 && /WARNING answer-key overlap/.test(r.out));
d = mk('sealword');
r = runSpec(d, baseSpec(d, { experts: [{ slug: 'e1', aspect: 'facet one', role: 'You inspect.', tools: 'Read',
  duties: ['Attack every candidate mechanism and state your expectations honestly.'], cids: ['s1'], must_read: [] }] }));
t('duty merely using the word expectations: clean pass, no warning', r.code === 0 && !/WARNING/.test(r.out));

// -- slot-injection + shape sanitization (PH a26) --
d = mk('inject');
r = runSpec(d, baseSpec(d, { experts: [{ slug: 'e1', aspect: 'facet one', role: 'You inspect.', tools: 'Read',
  duties: ['Sneak the {{TOOLS}} token into the rules region.'], cids: ['s1'], must_read: [] }] }));
t('duty containing a slot token rejected at spec load', r.code !== 0 && /slot-injection/.test(r.out));
d = mk('nosubj');
s = baseSpec(d); delete s.subject;
r = runSpec(d, s);
t('missing spec.subject rejected', r.code !== 0 && /subject/.test(r.out));
d = mk('mlaspect');
r = runSpec(d, baseSpec(d, { experts: [{ slug: 'e1', aspect: 'facet\none', role: 'You inspect.', tools: 'Read', duties: ['Work.'], cids: ['s1'], must_read: [] }] }));
t('multi-line aspect rejected', r.code !== 0 && /single-line/.test(r.out));

// -- manifest lint (PH a20): C-ids must point at existing FILES --
d = mk('lintdir');
s = baseSpec(d);
s.sources.s1 = { path: d, what: 'a directory' };
r = runSpec(d, s);
t('directory source path rejected, cid named', r.code !== 0 && /manifest lint/.test(r.out) && /s1/.test(r.out));
d = mk('lintgone');
s = baseSpec(d);
s.sources.s1 = { path: path.join(d, 'nope.md'), what: 'missing' };
r = runSpec(d, s);
t('missing source path rejected', r.code !== 0 && /does not exist/.test(r.out));

// -- multi-expert: per-expert derivation, shared rules text differs only by slots --
d = mk('multi');
s = baseSpec(d);
s.experts.push({ slug: 'e2', aspect: 'facet two', role: 'You audit numbers.', duties: ['Check the arithmetic.'], tools: 'Read, Bash', cids: ['s1'], must_read: ['s1'] });
r = runSpec(d, s);
t('two experts generate, both prompts written', r.code === 0
  && fs.existsSync(path.join(d, 'prompts', 'e1.md')) && fs.existsSync(path.join(d, 'prompts', 'e2.md')));

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
