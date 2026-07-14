// Tests for verify-readback.js — the deterministic read-back GATE (Fix 1, meta-trial run 0).
// Adversarial fixtures per the v1 audit's F1 demand: an untested gate is not a gate.
// Plain node, no framework. Prints "N passed, M failed", exit 1 on any failure.
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const VRB = path.join(__dirname, 'verify-readback.js');
let n = 0, pass = 0, fail = 0;
function t(name, cond) {
  n++;
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name); }
}
function run(runDir) {
  try { return { code: 0, out: execFileSync('node', [VRB, runDir], { encoding: 'utf8' }) }; }
  catch (e) { return { code: e.status, out: (e.stdout || '') + (e.stderr || '') }; }
}
function mkRun(name) {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'atc-vrb-' + name + '-'));
  for (const sub of ['journal', 'context', 'downloads', 'src']) fs.mkdirSync(path.join(d, sub));
  return d;
}
function writeManifest(runDir, slug, ids) {
  const manifest = Object.entries(ids).map(([id, p]) => ({ id, source: id, path: p, what: 'fixture', must_read: false }));
  fs.writeFileSync(path.join(runDir, 'context', slug + '-manifest.json'), JSON.stringify({ aspect: slug, manifest }), 'utf8');
}
function writeJournal(runDir, slug, entries) {
  fs.writeFileSync(path.join(runDir, 'journal', slug + '.jsonl'), entries.map((e) => JSON.stringify(e)).join('\n') + '\n', 'utf8');
}
const rec = (id, ref, quote, loc) => ({ t: 'record', class: 'finding', claim: id, step: 1, confidence: 'high', id, evidence: [{ ref, loc: loc || 'line 1', quote }] });
const INIT = { t: 'init', aspect: 'fixture', cids: ['C1', 'C2'] };
const STEP = { t: 'step', did: 'x', found: 'y', step: 1 };
const DONE = { t: 'done', summary: 's', counts: {} };

// ---------- DIRTY RUN: every fabrication class must be caught ----------
const dirty = mkRun('dirty');
const srcOne = path.join(dirty, 'src', 'one.md');
fs.writeFileSync(srcOne, [
  'Revenue grew 12 percent this year in totality across all divisions.',
  '',
  'The enforcer validates every entry at write time and rejects bad ones.',
  '',
  'alpha beta gamma delta lives here as the first paragraph anchor text.',
  '',
  'epsilon zeta eta theta lives here as the second paragraph anchor text.',
  '',
  "**Bold** claim | with pipes - and 'smart' quotes inside a table cell here.",
  '',
  'START of the long passage: the journal is append-only and validated.',
  'Irrelevant middle text sits here between the two quoted fragments.',
  'END of the long passage: the seal refuses while must_read items stay unread.',
].join('\n'), 'utf8');
const srcTwo = path.join(dirty, 'src', 'two.md');
fs.writeFileSync(srcTwo, 'This sentence lives only in source two and nowhere else at all today.', 'utf8');
fs.writeFileSync(path.join(dirty, 'downloads', 'snap.md'), 'the framework guarantees deterministic replay of every recorded interaction', 'utf8');

writeManifest(dirty, 'expert-a', { C1: srcOne, C2: srcTwo });
writeJournal(dirty, 'expert-a', [
  INIT, STEP,
  { t: 'source', url: 'https://ex.com/p', title: 'Ex', via: 'WebFetch', snapshot: 'downloads/snap.md', sid: 'W1' },
  rec('a1', 'C1', 'The enforcer validates every entry at write time and rejects bad ones.'),          // clean -> pass
  rec('a2', 'C1', 'THIS FABRICATED TEXT APPEARS NOWHERE IN THE SOURCE FILE AT ALL'),                   // fabricated -> FAIL
  rec('a3', 'C1', 'Revenue grew 13 percent this year in totality across all divisions.'),              // number-swap -> FAIL
  rec('a4', 'C1', 'START of the long passage: the journal is append-only and validated. ... END of the long passage: the seal refuses'), // elision stitch -> FAIL
  rec('a5', 'C1', 'This sentence lives only in source two and nowhere else at all today.'),            // mislabeled source -> FAIL
  rec('a6', 'C1', 'Bold claim with pipes - and "smart" quotes inside a table cell here.'),             // reformat: markdown ** and | DROPPED -> FAIL (literal contract)
  rec('a8', 'W1', 'the framework guarantees deterministic replay of every recorded interaction'),      // web vs snapshot -> pass
  rec('a9', 'W1', 'this fabricated web quote was never present in the saved snapshot file'),           // web fabricated -> FAIL
  DONE,
]);
let r = run(dirty);
t('dirty run: gate FAILS (non-zero exit)', r.code !== 0);
t('fabricated quote caught (a2)', /expert-a\/a2/.test(r.out));
t('number-swap caught (a3) — digits are load-bearing', /expert-a\/a3/.test(r.out));
t('elision stitch caught (a4) — "..." joins are not contiguous', /expert-a\/a4/.test(r.out));
t('mislabeled source caught (a5) — quote checked vs CLAIMED ref only', /expert-a\/a5/.test(r.out));
t('web quote fabricated vs snapshot caught (a9)', /expert-a\/a9/.test(r.out));
t('clean quote passes (a1 not in failures)', !/expert-a\/a1/.test(r.out));
t('reformat dropping markdown/pipes now FAILS (a6) — literal contract', /expert-a\/a6/.test(r.out));
t('web quote verified against saved snapshot passes (a8)', !/expert-a\/a8/.test(r.out));
t('scorecard shows 2/8 verified', /grounded-quotes 2\/8/.test(r.out));
t('failures announced as UNTRUSTED', /UNTRUSTED/.test(r.out));

// ---------- Item 5 (LH a21): gate persists readback-verdict.json on every run ----------
const readV = (d) => JSON.parse(fs.readFileSync(path.join(d, 'readback-verdict.json'), 'utf8'));
let v = readV(dirty);
t('verdict file written on FAIL run, gate field FAIL', v.gate === 'FAIL');
t('verdict untrusted ids match the failed records exactly', (() => {
  const ids = (v.journals['expert-a'].untrusted || []).map((u) => u.id).sort().join(',');
  return ids === 'a2,a3,a4,a5,a6,a9';
})());
t('verdict promptIdentity honestly not-checked (no persisted spec)', v.journals['expert-a'].promptIdentity === 'not-checked');
t('verdict carries a sha256 binding to the journal bytes', /^[0-9a-f]{64}$/.test(v.journals['expert-a'].journalSha256));

// ---------- LITERAL contract: tolerate invisible noise, reject fabrication + reformats ----------
// Built pure-ASCII via String.fromCharCode so this source file carries no raw unicode.
const lit = mkRun('lit');
const CQ = String.fromCharCode(0x2019), LQ = String.fromCharCode(0x201c), RQ = String.fromCharCode(0x201d), EM = String.fromCharCode(0x2014);
const litSrc = path.join(lit, 'src', 'one.md');
fs.writeFileSync(litSrc, [
  'The Enforcer validates every entry at write time and rejects bad ones.',
  '**Bold heading** with `code` and | pipes | kept exactly as written here.',
  'We talked about the deployment cadence and nothing much else here today.',
  'The user' + CQ + 's ' + LQ + 'token' + RQ + ' never expires ' + EM + ' in prod builds today.',
].join('\n'), 'utf8');
writeManifest(lit, 'expert-a', { C1: litSrc, C2: litSrc });
writeJournal(lit, 'expert-a', [INIT, STEP,
  rec('p1', 'C1', 'the enforcer validates every entry\nat write time and rejects bad ones.'), // PASS: case + hard-wrap only
  rec('p2', 'C1', 'The user\'s "token" never expires - in prod builds today.'),                // PASS: curly->straight + dash folded
  rec('p3', 'C1', '**Bold heading** with `code` and | pipes | kept exactly as written here.'), // PASS: faithful markdown copy
  rec('f1', 'C1', '!!!!!!!!!!!!!!!!!!!!!!!!!'),                                                 // FAIL: F1 all-punctuation attack
  rec('f2', 'C1', 'about?!?!?!?!?!?!?!?!?!?!?!'),                                               // FAIL: junk padded around real word
  rec('f3', 'C1', '                              '),                                           // FAIL: whitespace-only -> empty fold
  DONE]);
r = run(lit);
t('literal: gate FAILS (attacks present)', r.code !== 0);
t('literal PASS: case + hard-wrap tolerated (p1)', !/expert-a\/p1/.test(r.out));
t('literal PASS: curly quotes + dash folded (p2)', !/expert-a\/p2/.test(r.out));
t('literal PASS: faithful markdown copy kept verbatim (p3)', !/expert-a\/p3/.test(r.out));
t('F1 attack: all-punctuation quote FAILS (f1)', /expert-a\/f1/.test(r.out));
t('F1 attack: junk-padded real word FAILS (f2)', /expert-a\/f2/.test(r.out));
t('F1 attack: whitespace-only quote FAILS as too short/empty (f3)', /expert-a\/f3/.test(r.out) && /too short\/empty/.test(r.out));
t('literal scorecard shows 3/6 verified', /grounded-quotes 3\/6/.test(r.out));

// ---------- CLEAN RUN: gate passes, exit 0 ----------
const clean = mkRun('clean');
const cSrc = path.join(clean, 'src', 'one.md');
fs.writeFileSync(cSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
writeManifest(clean, 'expert-a', { C1: cSrc, C2: cSrc });
writeJournal(clean, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'A perfectly quotable sentence that the expert copies verbatim and contiguously.'), DONE]);
r = run(clean);
t('clean run: gate PASSES (exit 0)', r.code === 0 && /GATE: PASS/.test(r.out));
v = readV(clean);
t('verdict file written on PASS run too, empty untrusted/tainted', v.gate === 'PASS'
  && v.journals['expert-a'].untrusted.length === 0 && v.journals['expert-a'].tainted.length === 0 && v.journals['expert-a'].zeroGrounded === false);

// ---------- Item 4: block grain — the old whole-file residual is CLOSED ----------
// (Was the pinned KNOWN RESIDUAL; the pin existed so this change would be visible.
// The cost is accepted knowingly: an honest cross-paragraph quote must be recorded
// as one evidence item per block — the append-time bounce teaches this in-flight.)
const resid = mkRun('resid');
const rSrc = path.join(resid, 'src', 'one.md');
fs.writeFileSync(rSrc, 'alpha beta gamma delta first paragraph anchor.\n\nepsilon zeta eta theta second paragraph anchor.', 'utf8');
writeManifest(resid, 'expert-a', { C1: rSrc, C2: rSrc });
writeJournal(resid, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'alpha beta gamma delta first paragraph anchor. epsilon zeta eta theta second paragraph anchor.'), DONE]);
r = run(resid);
t('item 4: adjacent-paragraph stitch now FAILS (spans blank-line blocks)', r.code !== 0 && /spans blank-line blocks/.test(r.out));
writeJournal(resid, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'epsilon zeta eta theta second paragraph anchor.'), DONE]);
r = run(resid);
t('item 4: quote fully inside the SECOND block still passes', r.code === 0);

// ---------- CRLF source does not false-reject (M10 lesson) ----------
const crlf = mkRun('crlf');
const wSrc = path.join(crlf, 'src', 'one.md');
fs.writeFileSync(wSrc, 'Windows line endings\r\nlive inside this fixture source file today.', 'utf8');
writeManifest(crlf, 'expert-a', { C1: wSrc, C2: wSrc });
writeJournal(crlf, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'Windows line endings live inside this fixture source file today.'), DONE]);
r = run(crlf);
t('CRLF in source does not false-reject', r.code === 0);

// ---------- unsealed journal fails the gate ----------
const unsealed = mkRun('unsealed');
const uSrc = path.join(unsealed, 'src', 'one.md');
fs.writeFileSync(uSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
writeManifest(unsealed, 'expert-a', { C1: uSrc, C2: uSrc });
writeJournal(unsealed, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'A perfectly quotable sentence that the expert copies verbatim and contiguously.')]); // no done
r = run(unsealed);
t('unsealed journal: gate FAILS even with clean quotes', r.code !== 0 && /unsealed/.test(r.out));

// ---------- missing manifest: degrade (UNVERIFIABLE + fail), never crash ----------
const noman = mkRun('noman');
writeJournal(noman, 'ghost', [INIT, STEP, DONE]);
r = run(noman);
t('missing manifest: no crash, journal marked UNVERIFIABLE', /UNVERIFIABLE/.test(r.out));
t('missing manifest: gate FAILS', r.code !== 0);

// ---------- BOM-prefixed manifest still parses (PowerShell utf8 trap) ----------
const bom = mkRun('bom');
const bSrc = path.join(bom, 'src', 'one.md');
fs.writeFileSync(bSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
const bMan = { aspect: 'expert-a', manifest: [{ id: 'C1', source: 'C1', path: bSrc, what: 'x', must_read: false }] };
fs.writeFileSync(path.join(bom, 'context', 'expert-a-manifest.json'), String.fromCharCode(0xfeff) + JSON.stringify(bMan), 'utf8');
writeJournal(bom, 'expert-a', [{ t: 'init', aspect: 'x', cids: ['C1'] }, STEP,
  rec('a1', 'C1', 'A perfectly quotable sentence that the expert copies verbatim and contiguously.'), DONE]);
r = run(bom);
t('BOM-prefixed manifest still parses and gate PASSES', r.code === 0);

// ---------- Fix 2 defense-in-depth: escaped snapshot path fails even if text exists ----------
const esc = mkRun('esc');
fs.writeFileSync(path.join(esc, 'evil.md'), 'this text really does exist inside the escaped out-of-tree file', 'utf8');
writeManifest(esc, 'expert-a', {});
writeJournal(esc, 'expert-a', [{ t: 'init', aspect: 'x', cids: [] }, STEP,
  { t: 'source', url: 'https://ex.com/e', title: 'Escape', via: 'WebFetch', snapshot: 'evil.md', sid: 'W1' },
  rec('a1', 'W1', 'this text really does exist inside the escaped out-of-tree file'), DONE]);
r = run(esc);
t('snapshot escaped outside downloads/: quotes FAIL despite text present', r.code !== 0 && /expert-a\/a1/.test(r.out));

// ---------- missing source file: quote fails, no crash ----------
const gone = mkRun('gone');
writeManifest(gone, 'expert-a', { C1: path.join(gone, 'src', 'deleted.md'), C2: path.join(gone, 'src', 'deleted.md') });
writeJournal(gone, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'quoting a file that no longer exists on disk anywhere at all'), DONE]);
r = run(gone);
t('missing source file: quote FAILS (no crash)', r.code !== 0 && /expert-a\/a1/.test(r.out));

// ---------- F10: corrupt journal line DEGRADES (UNVERIFIABLE), never crashes ----------
const corrupt = mkRun('corrupt');
fs.writeFileSync(path.join(corrupt, 'src', 'one.md'), 'anything here for the fixture source file today.', 'utf8');
writeManifest(corrupt, 'expert-a', { C1: path.join(corrupt, 'src', 'one.md'), C2: path.join(corrupt, 'src', 'one.md') });
fs.writeFileSync(path.join(corrupt, 'journal', 'expert-a.jsonl'), JSON.stringify(INIT) + '\n{ this is not valid json at all\n' + JSON.stringify(DONE) + '\n', 'utf8');
r = run(corrupt);
t('corrupt journal line: marked UNVERIFIABLE, no uncaught crash', /UNVERIFIABLE/.test(r.out) && !/SyntaxError|at Object\.<anonymous>/.test(r.out));
t('corrupt journal line: gate FAILS', r.code !== 0);

// BOM-prefixed journal now parses (BOM stripped) instead of crashing.
const bomj = mkRun('bomj');
const bjSrc = path.join(bomj, 'src', 'one.md');
fs.writeFileSync(bjSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
writeManifest(bomj, 'expert-a', { C1: bjSrc, C2: bjSrc });
fs.writeFileSync(path.join(bomj, 'journal', 'expert-a.jsonl'), String.fromCharCode(0xfeff) + [JSON.stringify(INIT), JSON.stringify(STEP),
  JSON.stringify(rec('a1', 'C1', 'A perfectly quotable sentence that the expert copies verbatim and contiguously.')), JSON.stringify(DONE)].join('\n') + '\n', 'utf8');
r = run(bomj);
t('BOM-prefixed journal parses (BOM stripped), gate PASSES', r.code === 0 && /GATE: PASS/.test(r.out));

// ---------- F11: zero-grounded journal reports honestly, not a vacuous "verified" ----------
const zg = mkRun('zg');
const zSrc = path.join(zg, 'src', 'one.md');
fs.writeFileSync(zSrc, 'irrelevant source body here for the fixture file today.', 'utf8');
writeManifest(zg, 'expert-a', { C1: zSrc, C2: zSrc });
writeJournal(zg, 'expert-a', [INIT, STEP, { t: 'record', class: 'finding', claim: 'assertion only, no evidence', step: 1, confidence: 'low', id: 'a1' }, DONE]);
r = run(zg);
t('zero-grounded journal: honest "nothing to verify" note (not vacuous verified)', /nothing to verify/.test(r.out));
t('zero-grounded journal: gate PASSES (nothing failed), exit 0', r.code === 0);
// Item 7 (LH a32): quiet note upgraded to a loud banner + persisted verdict flag.
t('zero-grounded journal: loud WARNING banner names it', /WARNING: 1 journal\(s\) contain ZERO grounded records/.test(r.out) && /expert-a/.test(r.out));
t('zero-grounded journal: verdict flag persisted', readV(zg).journals['expert-a'].zeroGrounded === true);

// ---------- Item 7: mixed run — banner names ONLY the zero-grounded journal ----------
const mix = mkRun('mix');
const mSrc = path.join(mix, 'src', 'one.md');
fs.writeFileSync(mSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
writeManifest(mix, 'empty-one', { C1: mSrc, C2: mSrc });
writeManifest(mix, 'full-two', { C1: mSrc, C2: mSrc });
writeJournal(mix, 'empty-one', [INIT, STEP, { t: 'record', class: 'finding', claim: 'assertion only', step: 1, confidence: 'low', id: 'a1' }, DONE]);
writeJournal(mix, 'full-two', [INIT, STEP,
  rec('a1', 'C1', 'A perfectly quotable sentence that the expert copies verbatim and contiguously.'), DONE]);
r = run(mix);
t('mixed run: banner names only the zero-grounded slug', /ZERO grounded records[^\n]*empty-one/.test(r.out) && !/ZERO grounded records[^\n]*full-two/.test(r.out));

// ---------- Item 6 (LH a27): based_on unresolvable = tamper signal, hard FAIL ----------
const dang = mkRun('dang');
const dSrc = path.join(dang, 'src', 'one.md');
fs.writeFileSync(dSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
writeManifest(dang, 'expert-a', { C1: dSrc, C2: dSrc });
writeJournal(dang, 'expert-a', [INIT, STEP,
  { t: 'record', class: 'recommendation', claim: 'dangling', step: 1, confidence: 'low', id: 'a1', based_on: ['a99'], reasoning: 'cites a ghost' }, DONE]);
r = run(dang);
t('dangling based_on: gate FAILS with named reason', r.code !== 0 && /based_on 'a99' unresolvable/.test(r.out));
writeJournal(dang, 'expert-a', [INIT, STEP,
  { t: 'record', class: 'recommendation', claim: 'forward', step: 1, confidence: 'low', id: 'a1', based_on: ['a2'], reasoning: 'cites the future' },
  { t: 'record', class: 'finding', claim: 'later', step: 1, confidence: 'low', id: 'a2' }, DONE]);
r = run(dang);
t('forward-reference based_on: gate FAILS (order violation = tamper)', r.code !== 0 && /based_on 'a2' unresolvable/.test(r.out));

// ---------- Items 5+6 (LH a23/a29/a30): taint propagation, labels not exit causes ----------
const tnt = mkRun('tnt');
const tSrc = path.join(tnt, 'src', 'one.md');
fs.writeFileSync(tSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
writeManifest(tnt, 'expert-a', { C1: tSrc, C2: tSrc });
writeJournal(tnt, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'THIS FABRICATED QUOTE IS NOWHERE IN THE FIXTURE SOURCE'),
  { t: 'record', class: 'recommendation', claim: 'child of bad', step: 1, confidence: 'low', id: 'a2', based_on: ['a1'], reasoning: 'rests on a1' },
  { t: 'record', class: 'recommendation', claim: 'grandchild', step: 1, confidence: 'low', id: 'a3', based_on: ['a2'], reasoning: 'rests on a2' },
  rec('a4', 'C1', 'A perfectly quotable sentence that the expert copies verbatim and contiguously.'),
  { t: 'record', class: 'finding', claim: 'verified quote, poisoned basis', step: 1, confidence: 'low', id: 'a5', based_on: ['a1'], reasoning: 'quote stands alone',
    evidence: [{ ref: 'C1', loc: 'line 1', quote: 'A perfectly quotable sentence that the expert copies verbatim and contiguously.' }] },
  DONE]);
r = run(tnt);
v = readV(tnt);
t('taint chain: a2 and a3 tainted transitively with via-path', (() => {
  const tn = v.journals['expert-a'].tainted;
  return tn.length === 2 && tn[0].id === 'a2' && tn[0].via === 'a1' && tn[1].id === 'a3' && tn[1].via === 'a2';
})());
t('taint: clean sibling a4 NOT tainted', !v.journals['expert-a'].tainted.some((x) => x.id === 'a4'));
t('taint: verified-quote record with poisoned basis -> taintedBasis, stays verified', (() => {
  const j = v.journals['expert-a'];
  return j.taintedBasis.length === 1 && j.taintedBasis[0] === 'a5' && !j.tainted.some((x) => x.id === 'a5');
})());
t('taint never double-counts: exactly 1 failed check (the parent quote)', /1 failed check/.test(r.out));
t('taint announced as labels-only summary line', /TAINTED 2 record\(s\) via untrusted parents/.test(r.out));
t('scorecard: 2/3 verified (a4 + a5 quotes stand)', /grounded-quotes 2\/3/.test(r.out));

// ---------- Item 10 (PH a20): directory C-id fails with a diagnosable reason ----------
const dcid = mkRun('dircid');
writeManifest(dcid, 'expert-a', { C1: path.join(dcid, 'src'), C2: path.join(dcid, 'src') });
writeJournal(dcid, 'expert-a', [INIT, STEP,
  rec('a1', 'C1', 'quoting against a directory shaped source path here'), DONE]);
r = run(dcid);
t('directory C-id: gate FAILS with "source is a directory" (not a mystery null)', r.code !== 0 && /source is a directory/.test(r.out));

// ---------- Item 12 (PH a27): prompt identity re-proof at read-back ----------
const idr = mkRun('idr');
const idrSrc = path.join(idr, 'src', 'one.md');
fs.writeFileSync(idrSrc, 'A perfectly quotable sentence that the expert copies verbatim and contiguously.', 'utf8');
fs.writeFileSync(path.join(idr, 'spec.json'), JSON.stringify({
  template: path.join(__dirname, 'prompt-template.md'), journal_js: path.join(__dirname, 'journal.js'), run_dir: idr,
  subject: 'Question for the identity fixture panel to answer.',
  sources: { s1: { path: idrSrc, what: 'fixture' } },
  experts: [{ slug: 'expert-a', aspect: 'identity facet', role: 'You check things.', duties: ['Inspect the fixture source.'], tools: 'Read', cids: ['s1'], must_read: [] }],
}), 'utf8');
execFileSync('node', [path.join(__dirname, 'generate-prompts.js'), path.join(idr, 'spec.json')], { encoding: 'utf8' });
writeJournal(idr, 'expert-a', [{ t: 'init', aspect: 'x', cids: ['C1'] }, STEP,
  rec('a1', 'C1', 'A perfectly quotable sentence that the expert copies verbatim and contiguously.'), DONE]);
r = run(idr);
t('prompt identity: untouched prompts verify ok, gate PASSES', r.code === 0 && /prompt identity: expert-a ok/.test(r.out));
t('verdict promptIdentity ok', readV(idr).journals['expert-a'].promptIdentity === 'ok');
fs.appendFileSync(path.join(idr, 'prompts', 'expert-a.md'), '\nHAND EDIT AFTER GENERATION', 'utf8');
r = run(idr);
t('prompt identity: hand-edited prompt FAILS the gate with named reason', r.code !== 0 && /MISMATCH/.test(r.out) && /hand-edited after generation/.test(r.out));
t('verdict promptIdentity mismatch persisted', readV(idr).journals['expert-a'].promptIdentity === 'mismatch');

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
