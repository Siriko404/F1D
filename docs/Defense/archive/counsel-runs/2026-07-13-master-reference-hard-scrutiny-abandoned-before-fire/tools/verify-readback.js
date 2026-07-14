#!/usr/bin/env node
// verify-readback.js — the deterministic GATE half of read-back. For every journal,
// resolve each grounded record's evidence (manifest C-id -> path, W-id -> snapshot) and
// re-verify the quote is present INSIDE ONE blank-line block of the source (norm.js
// containsQuote — same predicate journal.js runs at append time). Prints a per-expert
// scorecard + a GATE verdict line, EXITS NON-ZERO on any failed quote, unresolvable
// based_on (tamper signal), unsealed journal, or unverifiable journal (missing manifest).
// Failed records are flagged UNTRUSTED. Persists <run>/readback-verdict.json atomically
// (PASS + FAIL) with per-journal untrusted ids, taint via based_on, zero-grounded flags,
// and a sha256 binding to the verified bytes — `render` consumes it; a later edit shows
// as STALE, never silent wrong labels. Taint LABELS only, never an exit cause.
// Run the gate BEFORE editing any audited source file. Human judgement of findings
// follows; this gate only proves quote presence.
//
//   node verify-readback.js <run_dir>
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
// ONE shared fold + containment predicate (norm.js): a quote verifies only if it appears
// LITERALLY inside ONE blank-line block. Stitched or reformatted quotes fail, by design.
const { norm, MIN_QUOTE_LEN, containsQuote } = require('./norm');

const runDir = process.argv[2];
if (!runDir) { console.log('usage: verify-readback.js <run_dir>'); process.exit(1); }

const journalDir = path.join(runDir, 'journal');
const ctxDir = path.join(runDir, 'context');
const fileCache = {};
function readFile(p) { if (!(p in fileCache)) { try { fileCache[p] = fs.readFileSync(p, 'utf8'); } catch { fileCache[p] = null; } } return fileCache[p]; }
function isDir(p) { try { return fs.statSync(p).isDirectory(); } catch { return false; } }

const journals = fs.readdirSync(journalDir).filter((f) => f.endsWith('.jsonl'));
let totalGrounded = 0, totalOk = 0, unsealedCount = 0, unverifiable = 0, totalTainted = 0;
const failures = [];
const zeroGroundedSlugs = [];
// Per-journal verdict data — persisted for render (LH a21). Untrust is RECORD-grained.
const verdictJournals = {};

// BOM-safe JSON read; null instead of crashing (degrade, never crash). BOM stripped by
// code point (0xFEFF) to keep this source pure-ASCII.
function readJson(p) {
  try {
    let s = fs.readFileSync(p, 'utf8');
    if (s.charCodeAt(0) === 0xfeff) s = s.slice(1);
    return JSON.parse(s);
  } catch { return null; }
}

// Prompt identity re-check: when the generator persisted spec + template snapshot,
// re-derive every prompt with the SAME buildAll and compare byte-for-byte against
// prompts/<slug>.md — catches post-generation hand-edits. Absent/unreadable ->
// 'not-checked'. Residual: editing prompt AND spec AND snapshot together defeats this (the S2 gate).
const specPersisted = fs.existsSync(path.join(ctxDir, 'panel-spec.json'));
let identity = null; // slug -> 'ok' | 'mismatch'
const identityFailures = [];
if (specPersisted) {
  try {
    const { buildAll } = require('./generate-prompts');
    const pSpec = readJson(path.join(ctxDir, 'panel-spec.json'));
    const tplSnap = fs.readFileSync(path.join(ctxDir, 'prompt-template.snapshot.md'), 'utf8');
    identity = {};
    for (const b of buildAll(pSpec, tplSnap)) {
      const onDisk = readFile(path.join(runDir, 'prompts', b.ex.slug + '.md'));
      identity[b.ex.slug] = onDisk === b.filled ? 'ok' : 'mismatch';
      if (identity[b.ex.slug] === 'mismatch') identityFailures.push({ slug: b.ex.slug, id: '(prompt)', ref: '-', loc: 'prompts/' + b.ex.slug + '.md', quote: '', reason: 'prompt differs from spec+template derivation (hand-edited after generation?)' });
    }
  } catch { identity = null; }
}

for (const jf of journals.sort()) {
  const slug = jf.replace('.jsonl', '');
  // Degrade, never crash (F1D §6): a corrupt or BOM-prefixed journal is marked
  // unverifiable (which FAILS the gate), not thrown as an uncaught stack trace.
  let lines, rawBytes;
  try {
    rawBytes = fs.readFileSync(path.join(journalDir, jf));
    let raw = rawBytes.toString('utf8');
    if (raw.charCodeAt(0) === 0xfeff) raw = raw.slice(1);
    lines = raw.split('\n').filter(Boolean).map((l) => JSON.parse(l));
  } catch {
    unverifiable++;
    verdictJournals[slug] = { sealed: false, unverifiable: true, zeroGrounded: true, journalSha256: rawBytes ? crypto.createHash('sha256').update(rawBytes).digest('hex') : null, promptIdentity: 'not-checked', untrusted: [], tainted: [], taintedBasis: [] };
    console.log(`UNVERIFIABLE ${slug.padEnd(22)} journal corrupt/unparseable at journal/${jf} — cannot verify`);
    continue;
  }
  const sha = crypto.createHash('sha256').update(rawBytes).digest('hex');
  const sealed = lines.some((l) => l.t === 'done');
  if (!sealed) unsealedCount++;
  const records = lines.filter((l) => l.t === 'record');
  const grounded = records.filter((r) => Array.isArray(r.evidence) && r.evidence.length > 0);

  // Build C-id -> source path from this expert's manifest; W-ids -> downloads snapshot.
  const man = readJson(path.join(ctxDir, slug + '-manifest.json'));
  if (!man || !Array.isArray(man.manifest)) {
    unverifiable++;
    verdictJournals[slug] = { sealed, unverifiable: true, zeroGrounded: grounded.length === 0, journalSha256: sha, promptIdentity: 'not-checked', untrusted: [], tainted: [], taintedBasis: [] };
    console.log(`UNVERIFIABLE ${slug.padEnd(22)} manifest missing/corrupt at context/${slug}-manifest.json — cannot verify ${grounded.length} grounded record(s)`);
    continue;
  }
  const cidPath = {};
  for (const m of man.manifest) cidPath[m.id] = m.path;
  // W-id snapshots must resolve INSIDE <run>/downloads/ (defense-in-depth: a journal
  // is a plain file — a tampered one could carry an escaped path past the enforcer).
  // Outside/unresolvable -> null -> every quote citing it FAILS.
  const wSnap = {};
  for (const s of lines.filter((l) => l.t === 'source')) {
    let real = null;
    try {
      const cand = fs.realpathSync(path.resolve(runDir, s.snapshot));
      const rel = path.relative(fs.realpathSync(path.join(runDir, 'downloads')), cand);
      if (rel !== '' && !rel.startsWith('..') && !path.isAbsolute(rel)) real = cand;
    } catch { /* missing snapshot or downloads dir -> unverifiable -> fail */ }
    wSnap[s.sid] = real;
  }

  // Per-record failure reasons (record-grained untrust — one bad quote fails the record).
  const recFail = {};
  let ok = 0, bad = 0;
  for (const r of grounded) {
    for (const q of r.evidence) {
      const nq = norm(q.quote);
      const src = cidPath[q.ref] || wSnap[q.ref];
      // Length floor first (empty-after-fold can't satisfy it -> `includes("")`-always-true
      // is impossible here; defense-in-depth vs a journal that bypassed the write-time guard).
      let reason;
      if (nq.length < MIN_QUOTE_LEN) reason = 'too short/empty after folding';
      else if (src && isDir(src)) reason = 'source is a directory'; // dir C-id: diagnosable, not a mystery null (PH a20)
      else {
        const body = src && readFile(src);
        if (!body) reason = 'source unreadable';
        else reason = containsQuote(body, q.quote); // null | 'not literally present' | 'spans blank-line blocks'
      }
      if (!reason) ok++;
      else { bad++; failures.push({ slug, id: r.id, ref: q.ref, loc: q.loc, quote: q.quote.slice(0, 60), reason }); (recFail[r.id] = recFail[r.id] || []).push(reason); }
    }
  }

  // based_on resolution: journal.js rejects unknown based_on at write time, so a
  // violation here proves the journal was edited outside the enforcer — hard FAIL.
  const seen = new Set();
  for (const r of records) {
    for (const d of (Array.isArray(r.based_on) ? r.based_on : [])) {
      if (!seen.has(d)) { failures.push({ slug, id: r.id, ref: '-', loc: '-', quote: '', reason: `based_on '${d}' unresolvable` }); (recFail[r.id] = recFail[r.id] || []).push('based_on unresolvable'); }
    }
    seen.add(r.id);
  }

  // Taint propagation: ONE forward pass (complete — journal.js assigns ids only after
  // validating based_on, so every parent precedes its child; cycles impossible). A
  // grounded record whose OWN quotes verified keeps its tier but lists in taintedBasis
  // (evidence stands, inference cites poison) and does NOT propagate. Taint never drives exit.
  const taint = new Set(Object.keys(recFail));
  const tainted = [], taintedBasis = [];
  for (const r of records) {
    if (taint.has(r.id)) continue;
    const dep = Array.isArray(r.based_on) ? r.based_on : [];
    const via = dep.find((d) => taint.has(d));
    if (!via) continue;
    const hasVerifiedEvidence = Array.isArray(r.evidence) && r.evidence.length > 0 && !recFail[r.id];
    if (hasVerifiedEvidence) taintedBasis.push(r.id);
    else { tainted.push({ id: r.id, via }); taint.add(r.id); }
  }
  totalTainted += tainted.length;

  const nQuotes = grounded.reduce((n, r) => n + r.evidence.length, 0);
  totalGrounded += nQuotes; totalOk += ok;
  if (grounded.length === 0) zeroGroundedSlugs.push(slug);
  verdictJournals[slug] = {
    sealed,
    unverifiable: false,
    zeroGrounded: grounded.length === 0,
    journalSha256: sha,
    promptIdentity: 'not-checked',
    untrusted: Object.entries(recFail).map(([id, reasons]) => ({ id, reasons })),
    tainted,
    taintedBasis,
  };
  const tiers = { grounded: grounded.length, derived: records.filter((r) => (r.based_on || []).length && !(r.evidence || []).length).length, assertion: records.filter((r) => !(r.evidence || []).length && !(r.based_on || []).length).length };
  // Honest scorecard: 0 grounded records verified NOTHING — say so, not a vacuous "0/0".
  const quoteCol = nQuotes === 0 ? 'no grounded records — nothing to verify' : `grounded-quotes ${ok}/${nQuotes} verified${bad ? '  <-- ' + bad + ' FAILED' : ''}`;
  console.log(`${sealed ? 'SEALED ' : 'UNSEALED'} ${slug.padEnd(22)} records ${String(records.length).padStart(3)} | tiers g/d/a ${tiers.grounded}/${tiers.derived}/${tiers.assertion} | ${quoteCol}${tainted.length ? ` | TAINTED ${tainted.length} via untrusted parents` : ''}`);
}

console.log(`\nTOTAL grounded quotes re-verified: ${totalOk}/${totalGrounded}`);
// Prompt-identity results join the same failure list and the per-journal verdict.
failures.push(...identityFailures);
for (const slug of Object.keys(verdictJournals)) {
  verdictJournals[slug].promptIdentity = identity ? (identity[slug] || 'not-checked') : 'not-checked';
}
if (!identity) console.log(specPersisted
  ? 'prompt identity: not checked (persisted spec/template snapshot unreadable)'
  : 'prompt identity: not checked (no persisted spec at context/panel-spec.json)');
else for (const [slug, st] of Object.entries(identity)) console.log(`prompt identity: ${slug} ${st === 'ok' ? 'ok' : 'MISMATCH'}`);

// Zero-grounded loudness: a journal of only unverified assertions must not hide in a green gate.
if (zeroGroundedSlugs.length) {
  console.log(`\nWARNING: ${zeroGroundedSlugs.length} journal(s) contain ZERO grounded records — their findings carry NO verified evidence: ${zeroGroundedSlugs.join(', ')}`);
}

if (failures.length) {
  console.log('\nFAILED checks (treat each named record as UNTRUSTED — the persisted verdict carries this to render):');
  for (const f of failures) console.log(`  [${f.slug}/${f.id}] ref ${f.ref} @ ${f.loc}: "${f.quote}..." (${f.reason})`);
}
if (totalTainted) console.log(`\nTAINTED ${totalTainted} record(s) via untrusted parents (labels only — not gate causes; see readback-verdict.json)`);

// Persist the verdict ATOMICALLY every run (render consumes it; no half-written file on crash).
const gateFail = failures.length || unsealedCount || unverifiable;
const verdict = { ranAt: new Date().toISOString(), gate: gateFail ? 'FAIL' : 'PASS', journals: verdictJournals };
const vPath = path.join(runDir, 'readback-verdict.json');
fs.writeFileSync(vPath + '.tmp', JSON.stringify(verdict, null, 2), 'utf8');
fs.renameSync(vPath + '.tmp', vPath);

// GATE verdict: non-zero unless every quote re-verifies, every based_on resolves, every
// journal sealed + verifiable. An untrusted record is never grounded; re-fire if load-bearing.
if (gateFail) {
  console.log(`\nGATE: FAIL — ${failures.length} failed check(s) (quotes/based_on), ${unsealedCount} journal(s) unsealed, ${unverifiable} unverifiable`);
  process.exit(1);
}
// PASS is honest about the vacuous case: 0 grounded quotes = nothing verified (green
// attests only nothing FAILED). Claim soundness is always the human read-back's job.
console.log(totalGrounded === 0
  ? '\nGATE: PASS — all journals sealed and verifiable; NOTE: 0 grounded quotes to verify (nothing was checked)'
  : '\nGATE: PASS — all grounded quotes re-verified, all journals sealed');
