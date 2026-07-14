// Tests for journal.js -- the append-only JSONL journal gate (atom design 4).
// Plain node, no framework. Prints "N passed, M failed", exit 1 on any failure.
// Pure ASCII on purpose (PowerShell encoding traps corrupted unicode comments once).
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const JS = path.join(__dirname, 'journal.js');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'atc-journal-'));
// Real run-folder layout: journals in <run>/journal/, snapshots in <run>/downloads/.
fs.mkdirSync(path.join(tmp, 'journal'), { recursive: true });
fs.mkdirSync(path.join(tmp, 'downloads'), { recursive: true });
// Content must CONTAIN the quote the W1-citing record uses: append-time containment
// (EC a27) now verifies W-id quotes against their snapshot at write time.
fs.writeFileSync(path.join(tmp, 'downloads', 'exa.md'), 'verbatim web text from the saved snapshot, and the page body continues here.', 'utf8');
let n = 0, pass = 0, fail = 0;

function run(args, input) {
  try {
    const out = execFileSync('node', [JS, ...args], { encoding: 'utf8', input });
    return { code: 0, out };
  } catch (e) {
    return { code: e.status, out: (e.stdout || '') + (e.stderr || '') };
  }
}
function ap(file, obj) { return run(['append', file, JSON.stringify(obj)]); }
function t(name, cond) {
  n++;
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name); }
}
function lines(file) { return fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l)); }

const J = path.join(tmp, 'journal', 'sec.jsonl');

// -- init --
let r = ap(J, { t: 'step', did: 'x', found: 'y' });
t('append before init rejected', r.code !== 0 && /init/i.test(r.out));
r = ap(J, { t: 'init', aspect: 'security', cids: ['C1', 'C2'] });
t('init accepted', r.code === 0);
r = ap(J, { t: 'init', aspect: 'security', cids: ['C1'] });
t('second init rejected', r.code !== 0);

// -- step --
r = ap(J, { t: 'step', did: 'read C1 hook config', found: 'hook fires every turn' });
t('step 1 accepted + numbered', r.code === 0 && /step 1/.test(r.out));
r = ap(J, { t: 'step', did: 'grep for enforcement', found: 'none in code path' });
t('step 2 numbered', r.code === 0 && /step 2/.test(r.out));
r = ap(J, { t: 'step', did: 'missing found field' });
t('step without found rejected', r.code !== 0);

// -- context --
r = ap(J, { t: 'context', cid: 'C1', status: 'read', note: 'full read' });
t('context check-in accepted', r.code === 0);
r = ap(J, { t: 'context', cid: 'C9', status: 'read' });
t('context unknown cid rejected', r.code !== 0);
r = ap(J, { t: 'context', cid: 'C2', status: 'glanced' });
t('context bad status rejected', r.code !== 0);

// -- source (F2: snapshot mandatory + must EXIST) --
r = ap(J, { t: 'source', url: 'https://ex.com/a', title: 'Ex A', via: 'curl -o', query: 'x' });
t('source without snapshot rejected', r.code !== 0 && /snapshot/i.test(r.out));
r = ap(J, { t: 'source', url: 'https://ex.com/a', title: 'Ex A', via: 'curl -o', snapshot: 'downloads/nope.md' });
t('source with NONEXISTENT snapshot rejected', r.code !== 0 && /not found/i.test(r.out));
r = ap(J, { t: 'source', url: 'https://ex.com/a', title: 'Ex A', via: 'curl -o', snapshot: 'downloads/exa.md' });
t('source with real snapshot registered as W1', r.code === 0 && /W1/.test(r.out));

// -- Fix 2: snapshot containment -- must be a non-empty FILE inside <run>/downloads/ --
// runDir == tmp (journal lives in tmp/journal/). outside.md sits at run root, outside downloads/.
fs.writeFileSync(path.join(tmp, 'outside.md'), 'existing file OUTSIDE downloads, e.g. the subject brief', 'utf8');
r = ap(J, { t: 'source', url: 'https://ex.com/t', title: 'Traversal', via: 'curl -o', snapshot: 'downloads/../outside.md' });
t('snapshot path traversal (downloads/../) onto a real file rejected', r.code !== 0 && /INSIDE/i.test(r.out));
r = ap(J, { t: 'source', url: 'https://ex.com/t', title: 'Absolute escape', via: 'curl -o', snapshot: path.join(tmp, 'outside.md') });
t('absolute snapshot path outside downloads rejected', r.code !== 0 && /INSIDE/i.test(r.out));
fs.mkdirSync(path.join(tmp, 'downloads-evil'), { recursive: true });
fs.writeFileSync(path.join(tmp, 'downloads-evil', 'x.md'), 'prefix-sibling dir content', 'utf8');
r = ap(J, { t: 'source', url: 'https://ex.com/t', title: 'Prefix sibling', via: 'curl -o', snapshot: 'downloads-evil/x.md' });
t('prefix-sibling dir (downloads-evil/) rejected', r.code !== 0 && /INSIDE/i.test(r.out));
r = ap(J, { t: 'source', url: 'https://ex.com/t', title: 'Dir as snapshot', via: 'curl -o', snapshot: 'downloads' });
t('downloads dir itself as snapshot rejected', r.code !== 0 && /INSIDE|FILE/i.test(r.out));
fs.writeFileSync(path.join(tmp, 'downloads', 'empty.md'), '', 'utf8');
r = ap(J, { t: 'source', url: 'https://ex.com/t', title: 'Empty decoy', via: 'curl -o', snapshot: 'downloads/empty.md' });
t('empty snapshot file rejected', r.code !== 0 && /non-empty/i.test(r.out));
let linked = false;
try { fs.symlinkSync(path.join(tmp, 'outside.md'), path.join(tmp, 'downloads', 'link.md'), 'file'); linked = true; } catch { /* no symlink perms on this box */ }
if (linked) {
  r = ap(J, { t: 'source', url: 'https://ex.com/t', title: 'Symlink escape', via: 'curl -o', snapshot: 'downloads/link.md' });
  t('symlink escaping downloads rejected (realpath)', r.code !== 0 && /INSIDE/i.test(r.out));
} else { console.log('  skip symlink test (no perms)'); }

// -- record --
// C1 has no manifest behind it in this layout -> append-time containment falls back to
// ACCEPT (structural-only contract pinned; the read-back gate proves literal presence).
r = ap(J, { t: 'record', class: 'finding', claim: 'Hook output is injected unverified.', step: 1,
  evidence: [{ ref: 'C1', loc: 'line 12-14', quote: 'inject top hits every turn' }], confidence: 'high', caveats: [] });
t('grounded record accepted as a1', r.code === 0 && /a1/.test(r.out));
r = ap(J, { t: 'record', class: 'finding', claim: 'Cited from web.', step: 2,
  evidence: [{ ref: 'W1', loc: 'sec 2', quote: 'verbatim web text from the saved snapshot' }], confidence: 'medium' });
t('record citing W1 accepted', r.code === 0 && /a2/.test(r.out));
r = ap(J, { t: 'record', class: 'finding', claim: 'Web quote not in snapshot.', step: 2,
  evidence: [{ ref: 'W1', loc: 'sec 2', quote: 'this fabricated web quote was never inside the saved snapshot' }], confidence: 'medium' });
t('W-id quote absent from snapshot BOUNCES at append (EC a27)', r.code !== 0 && /not literally present/.test(r.out));
r = ap(J, { t: 'record', class: 'finding', claim: 'Short quote attempt.', step: 2,
  evidence: [{ ref: 'C1', loc: 'line 1', quote: 'the user' }], confidence: 'high' });
t('sub-25-char quote rejected (M12)', r.code !== 0 && /too short/i.test(r.out));
r = ap(J, { t: 'record', class: 'risk', claim: 'Bad ref.', step: 1,
  evidence: [{ ref: 'C7', loc: 'x', quote: 'y' }], confidence: 'low' });
t('record with unknown evidence ref rejected', r.code !== 0);
r = ap(J, { t: 'record', class: 'risk', claim: 'No step.', evidence: [], confidence: 'low' });
t('record without step rejected', r.code !== 0);
r = ap(J, { t: 'record', class: 'risk', claim: 'Future step.', step: 99, confidence: 'low' });
t('record with nonexistent step rejected', r.code !== 0);
r = ap(J, { t: 'record', class: 'recommendation', claim: 'Derived rec.', step: 2,
  based_on: ['a1', 'a2'], reasoning: 'follows from both', confidence: 'medium' });
t('derived record (based_on) accepted as a3', r.code === 0 && /a3/.test(r.out));
r = ap(J, { t: 'record', class: 'recommendation', claim: 'Bad chain.', step: 2,
  based_on: ['a9'], reasoning: 'long enough reasoning here', confidence: 'low' });
t('based_on unknown record rejected', r.code !== 0);
r = ap(J, { t: 'record', class: 'recommendation', claim: 'No reasoning.', step: 2,
  based_on: ['a1'], confidence: 'low' });
t('based_on without reasoning rejected', r.code !== 0);
r = ap(J, { t: 'record', class: 'recommendation', claim: 'Stub reasoning.', step: 2,
  based_on: ['a1'], reasoning: 'x', confidence: 'low' });
t('reasoning under 10 folded chars rejected (PH a29)', r.code !== 0 && /too short/i.test(r.out));
r = ap(J, { t: 'record', class: 'finding', claim: 'Pure assertion, no receipt.', step: 2, confidence: 'low' });
t('assertion record allowed', r.code === 0 && /a4/.test(r.out));

// -- stdin append (quoting-proof path for agents) --
r = run(['append', J], JSON.stringify({ t: 'step', did: 'via stdin with "quotes" and $chars', found: 'works' }));
t('append via STDIN accepted (step 3)', r.code === 0 && /step 3/.test(r.out));

// -- gap / bad json / ts --
r = ap(J, { t: 'gap', what: 'could not test live hook' });
t('gap accepted', r.code === 0);
r = run(['append', J, '{not json']);
t('invalid json rejected', r.code !== 0);
t('every line script-stamped with ts', lines(J).every((l) => typeof l.ts === 'string' && l.ts.length > 10));

// -- done / seal --
r = ap(J, { t: 'done', summary: 'finished' });
t('done accepted with counts', r.code === 0);
const doneLine = lines(J).find((l) => l.t === 'done');
t('done counts correct', doneLine.counts.records === 4 && doneLine.counts.steps === 3 && doneLine.counts.sources === 1 && doneLine.counts.gaps === 1);
r = ap(J, { t: 'step', did: 'late', found: 'late' });
t('append after done rejected (sealed)', r.code !== 0 && /seal/i.test(r.out));

// -- assemble --
r = run(['assemble', J]);
const rep = JSON.parse(r.out);
t('assemble: basis derived from shape', (() => {
  const b = Object.fromEntries(rep.records.map((x) => [x.id, x.basis]));
  return b.a1 === 'grounded' && b.a2 === 'grounded' && b.a3 === 'derived' && b.a4 === 'assertion';
})());
t('assemble: ledger + sources + gaps present', rep.context_ledger.length === 1 && rep.sources.length === 1 && rep.gaps.length === 1);

// -- render --
r = run(['render', J]);
t('render: contains claim + verbatim quote + tiers', r.out.includes('Hook output is injected unverified.')
  && r.out.includes('inject top hits every turn') && /GROUNDED/.test(r.out) && /ASSERTION/.test(r.out));

// -- must_read seal enforcement (separate journal) --
const J2 = path.join(tmp, 'journal', 'mr.jsonl');
r = ap(J2, { t: 'init', aspect: 'x', cids: ['C1', 'C2'], must_read: ['C1', 'C9'] });
t('init must_read outside cids rejected', r.code !== 0);
r = ap(J2, { t: 'init', aspect: 'x', cids: ['C1', 'C2'], must_read: ['C1'] });
t('init with must_read accepted', r.code === 0);
r = ap(J2, { t: 'done' });
t('seal REFUSED while must_read unread', r.code !== 0 && /must_read/.test(r.out));
ap(J2, { t: 'context', cid: 'C1', status: 'read' });
r = ap(J2, { t: 'done' });
t('seal allowed once must_read is read', r.code === 0);

// -- Fix 3: template<->enforcer contract -- the 4 fields the template now marks OPTIONAL
// must actually be accepted when absent (executable proof the contract matches). --
const J3 = path.join(tmp, 'journal', 'opt.jsonl');
ap(J3, { t: 'init', aspect: 'opt', cids: ['C1'] });
r = ap(J3, { t: 'step', did: 'read x', found: 'y' });
t('contract: step without next accepted', r.code === 0);
r = ap(J3, { t: 'context', cid: 'C1', status: 'read' });
t('contract: context without note accepted', r.code === 0);
r = ap(J3, { t: 'record', class: 'finding', claim: 'a claim with no caveats field at all', step: 1, confidence: 'low' });
t('contract: record without caveats accepted', r.code === 0);
r = ap(J3, { t: 'done' });
t('contract: done without summary accepted', r.code === 0);

// -- F1 fix: min-quote-length is measured on the FOLDED quote. Punctuation is real
// content and counts; whitespace/invisible noise folds away and does NOT count. journal
// is structural when the ref has no file behind it -- literal-presence for such refs
// is the read-back gate's job. --
const J4 = path.join(tmp, 'journal', 'len.jsonl');
ap(J4, { t: 'init', aspect: 'len', cids: ['C1'] });
ap(J4, { t: 'step', did: 'x', found: 'y' });
r = ap(J4, { t: 'record', class: 'finding', claim: 'folds short', step: 1, confidence: 'low', evidence: [{ ref: 'C1', loc: 'l1', quote: 'short' + ' '.repeat(40) }] });
t('quote folding to <25 chars rejected (whitespace padding does not count)', r.code !== 0 && /too short/i.test(r.out));
r = ap(J4, { t: 'record', class: 'finding', claim: 'punct is content', step: 1, confidence: 'low', evidence: [{ ref: 'C1', loc: 'l1', quote: '!!!!!!!!!!!!!!!!!!!!!!!!!' }] });
t('25-char punctuation quote ACCEPTED by journal (no file behind C1; read-back proves presence)', r.code === 0);

// -- Item 1 (EC a24): via blocklist -- LLM-processed fetch channels rejected at registration --
const J5 = path.join(tmp, 'journal', 'via.jsonl');
ap(J5, { t: 'init', aspect: 'via', cids: [] });
r = ap(J5, { t: 'source', url: 'https://ex.com/w', title: 'W', via: 'WebFetch', snapshot: 'downloads/exa.md' });
t('via WebFetch rejected (LLM-processed channel)', r.code !== 0 && /LLM-processed/i.test(r.out));
r = ap(J5, { t: 'source', url: 'https://ex.com/w', title: 'W', via: 'WebSearch (mcp tool)', snapshot: 'downloads/exa.md' });
t('via containing websearch rejected case-insensitively', r.code !== 0 && /LLM-processed/i.test(r.out));
r = ap(J5, { t: 'source', url: 'https://ex.com/w', title: 'W', via: 'curl -o', snapshot: 'downloads/exa.md' });
t('via curl -o accepted', r.code === 0 && /W1/.test(r.out));

// -- Item 1 (EC a25 as amended): small-snapshot tripwire FLAGS http(s) sources, never rejects --
t('small http snapshot: accepted WITH warning printed', /small-snapshot/.test(r.out));
t('small http snapshot: flag persisted on the stored line', lines(J5).some((l) => l.t === 'source' && l.flag === 'small-snapshot'));
fs.writeFileSync(path.join(tmp, 'downloads', 'big.md'), ('full raw capture content line.\n').repeat(300), 'utf8'); // > 8192 bytes
r = ap(J5, { t: 'source', url: 'https://ex.com/big', title: 'Big', via: 'curl -o', snapshot: 'downloads/big.md' });
t('large http snapshot: no flag', r.code === 0 && !/small-snapshot/.test(r.out));
r = ap(J5, { t: 'source', url: 'file://local/copy', title: 'Local', via: 'file copy', snapshot: 'downloads/exa.md' });
t('small NON-http source: no flag', r.code === 0 && !/small-snapshot/.test(r.out));

// -- Item 2 (EC a27): append-time containment against a real manifest (run layout) --
const tmpA = fs.mkdtempSync(path.join(os.tmpdir(), 'atc-journal-atv-'));
for (const sub of ['journal', 'context', 'downloads', 'src']) fs.mkdirSync(path.join(tmpA, sub));
const atvSrc = path.join(tmpA, 'src', 'one.md');
fs.writeFileSync(atvSrc, 'The enforcer validates every entry at write time and rejects bad ones.\n\nThe seal refuses while must_read items stay unread in this fixture.', 'utf8');
fs.writeFileSync(path.join(tmpA, 'context', 'atv-manifest.json'),
  JSON.stringify({ aspect: 'atv', manifest: [{ id: 'C1', source: 'C1', path: atvSrc, what: 'fixture', must_read: false }] }), 'utf8');
const JA = path.join(tmpA, 'journal', 'atv.jsonl');
r = ap(JA, { t: 'init', aspect: 'atv', cids: ['C1'] });
t('init.cids matching the manifest accepted', r.code === 0);
ap(JA, { t: 'step', did: 'x', found: 'y' });
r = ap(JA, { t: 'record', class: 'finding', claim: 'True quote.', step: 1, confidence: 'high',
  evidence: [{ ref: 'C1', loc: 'para 1', quote: 'validates every entry at write time and rejects' }] });
t('append-time: true in-block quote accepted', r.code === 0);
r = ap(JA, { t: 'record', class: 'finding', claim: 'Fabricated.', step: 1, confidence: 'high',
  evidence: [{ ref: 'C1', loc: 'para 1', quote: 'THIS TEXT IS NOWHERE IN THE FIXTURE SOURCE AT ALL' }] });
t('append-time: fabricated quote BOUNCES (not literally present)', r.code !== 0 && /not literally present/.test(r.out));
r = ap(JA, { t: 'record', class: 'finding', claim: 'Stitch.', step: 1, confidence: 'high',
  evidence: [{ ref: 'C1', loc: 'both', quote: 'rejects bad ones. The seal refuses while must_read' }] });
t('append-time: blank-line stitch BOUNCES (spans blank-line blocks)', r.code !== 0 && /spans blank-line blocks/.test(r.out));

// -- Item 12 (PH a28): init.cids must exactly match the ratified manifest when present --
fs.writeFileSync(path.join(tmpA, 'context', 'cids-manifest.json'),
  JSON.stringify({ aspect: 'cids', manifest: [{ id: 'C1', source: 'a', path: atvSrc, what: 'x', must_read: false }, { id: 'C2', source: 'b', path: atvSrc, what: 'x', must_read: false }] }), 'utf8');
const JC = path.join(tmpA, 'journal', 'cids.jsonl');
r = ap(JC, { t: 'init', aspect: 'cids', cids: ['C1'] });
t('init.cids subset of manifest rejected (phantom/dropped context)', r.code !== 0 && /exactly match/.test(r.out));
r = ap(JC, { t: 'init', aspect: 'cids', cids: ['C2', 'C1'] });
t('init.cids matching manifest order-insensitively accepted', r.code === 0);

// -- qcheck: script-written check stamp on record lines (verified vs unresolvable) --
r = ap(JA, { t: 'record', class: 'finding', claim: 'Stamped verified.', step: 1, confidence: 'high',
  evidence: [{ ref: 'C1', loc: 'para 2', quote: 'seal refuses while must_read items stay unread' }] });
t('qcheck: checked-and-passed record stamped verified (OK output + stored line)', r.code === 0
  && /\[qcheck: verified\]/.test(r.out)
  && lines(JA).some((l) => l.t === 'record' && l.claim === 'Stamped verified.' && l.qcheck === 'verified'));
r = ap(J4, { t: 'record', class: 'finding', claim: 'Unresolvable ref made visible.', step: 1, confidence: 'low',
  evidence: [{ ref: 'C1', loc: 'l1', quote: 'twenty-five-plus chars of quotable text here' }] });
t('qcheck: unresolvable ref stamped unresolvable (accepted unchecked)', r.code === 0
  && /\[qcheck: unresolvable\]/.test(r.out)
  && lines(J4).some((l) => l.t === 'record' && l.qcheck === 'unresolvable'));
r = ap(JA, { t: 'record', class: 'finding', claim: 'No evidence no stamp.', step: 1, confidence: 'low', qcheck: 'verified' });
t('qcheck: agent-supplied stamp on a no-evidence record discarded', r.code === 0 && !/qcheck/.test(r.out)
  && lines(JA).some((l) => l.t === 'record' && l.claim === 'No evidence no stamp.' && !('qcheck' in l)));

// -- Item 5 (LH a22/a33): render consults the persisted gate verdict --
const crypto = require('crypto');
const tmpR = fs.mkdtempSync(path.join(os.tmpdir(), 'atc-journal-rnd-'));
fs.mkdirSync(path.join(tmpR, 'journal'));
const RJ = path.join(tmpR, 'journal', 'rj.jsonl');
ap(RJ, { t: 'init', aspect: 'render-fixture', cids: ['C1'] });
ap(RJ, { t: 'step', did: 'x', found: 'y' });
ap(RJ, { t: 'record', class: 'finding', claim: 'Bad quote record.', step: 1, confidence: 'high',
  evidence: [{ ref: 'C1', loc: 'l1', quote: 'inject top hits every turn now' }] });
ap(RJ, { t: 'record', class: 'recommendation', claim: 'Child of bad.', step: 1, confidence: 'low',
  based_on: ['a1'], reasoning: 'rests on a1 entirely' });
ap(RJ, { t: 'record', class: 'finding', claim: 'Verified quote, poisoned basis.', step: 1, confidence: 'low',
  based_on: ['a1'], reasoning: 'quote stands alone', evidence: [{ ref: 'C1', loc: 'l2', quote: 'another verified quote that stands alone here' }] });
ap(RJ, { t: 'done' });
r = run(['render', RJ]);
t('render without verdict: loud NO GATE VERDICT line', /NO GATE VERDICT/.test(r.out));
const rjSha = crypto.createHash('sha256').update(fs.readFileSync(RJ)).digest('hex');
fs.writeFileSync(path.join(tmpR, 'readback-verdict.json'), JSON.stringify({
  ranAt: '2026-07-07T00:00:00Z', gate: 'FAIL',
  journals: { rj: { sealed: true, unverifiable: false, zeroGrounded: false, journalSha256: rjSha, promptIdentity: 'not-checked',
    untrusted: [{ id: 'a1', reasons: ['not literally present'] }], tainted: [{ id: 'a2', via: 'a1' }], taintedBasis: ['a3'] } },
}), 'utf8');
r = run(['render', RJ]);
t('render with fresh verdict: UNTRUSTED section holds gate-failed + tainted', /## UNTRUSTED \(read-back gate\) -- 2/.test(r.out)
  && /gate: not literally present/.test(r.out) && /tainted via a1/.test(r.out));
t('render: untrusted a1 pulled OUT of the GROUNDED tier', r.out.indexOf('[a1]') < r.out.indexOf('## GROUNDED'));
t('render: taintedBasis record keeps its tier with a CAVEAT line', r.out.indexOf('[a3]') > r.out.indexOf('## GROUNDED')
  && /CAVEAT: based_on cites untrusted a1/.test(r.out));
t('render header names the gate verdict', /gate verdict: FAIL \(verified /.test(r.out));
fs.appendFileSync(RJ, '\n', 'utf8'); // journal bytes changed after the gate ran
r = run(['render', RJ]);
t('render with stale verdict: loud STALE line, shape tiers only', /STALE GATE VERDICT/.test(r.out) && !/## UNTRUSTED/.test(r.out));
r = run(['render', J]);
t('render of grounded journal has NO zero-grounded warning', !/ZERO GROUNDED/.test(r.out));
r = run(['render', J5]);
t('render of zero-grounded journal warns loudly + shows source flags', /ZERO GROUNDED RECORDS/.test(r.out) && /\[small-snapshot\]/.test(r.out));

// -- Item 11 (PH a23): status subcommand -- poll target for FIRE discipline --
r = run(['status', tmp]);
t('status: non-zero exit while any journal unsealed', r.code !== 0 && /UNSEALED/.test(r.out) && /SEALED/.test(r.out));
const tmpS = fs.mkdtempSync(path.join(os.tmpdir(), 'atc-journal-st-'));
fs.mkdirSync(path.join(tmpS, 'journal'));
const JSld = path.join(tmpS, 'journal', 'onlyone.jsonl');
ap(JSld, { t: 'init', aspect: 'x', cids: [] });
ap(JSld, { t: 'done' });
r = run(['status', tmpS]);
t('status: exit 0 when every journal sealed', r.code === 0 && /SEALED/.test(r.out) && !/UNSEALED/.test(r.out));
r = run(['status', path.join(tmpS, 'nope')]);
t('status: missing journal/ dir dies with reason', r.code !== 0 && /journal/.test(r.out));

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
