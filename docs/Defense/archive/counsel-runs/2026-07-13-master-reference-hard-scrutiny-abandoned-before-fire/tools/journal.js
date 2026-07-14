#!/usr/bin/env node
// journal.js — mechanical enforcer of the ATC counsel journal. Agents write ONLY through
// `append`: each line is schema-validated at write time, gets script-stamped ts +
// script-assigned ids (a1.., W1.., step numbers), referential integrity enforced
// (evidence.ref must be a known C/W id, based_on must name existing records), seals on
// `done`. Guaranteed utf8 + '\n' (kills the PowerShell UTF-16 append trap).
//
// Usage:
//   node journal.js append <file> ['<json>'|stdin]  -> validate + append one entry
//                                       (stdin path is quoting-proof; agents heredoc it)
//   node journal.js assemble <file>  -> single clean JSON report to stdout
//   node journal.js render <file>    -> tiered markdown, verbatim fields only
//   node journal.js status <run_dir> -> one line/journal, non-zero while any unsealed
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { norm, MIN_QUOTE_LEN, containsQuote } = require('./norm');

const CLASSES = ['finding', 'risk', 'recommendation'];
const CONF = ['high', 'medium', 'low'];
const CTX_STATUS = ['read', 'partial', 'missing', 'skipped'];

function die(msg) { process.stdout.write('ERROR: ' + msg + '\n'); process.exit(1); }
function reqStr(e, f) { if (typeof e[f] !== 'string' || !e[f].trim()) die(`'${f}' required (non-empty string)`); }

function readLines(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map((l, i) => {
    try { return JSON.parse(l); } catch { die(`corrupt journal: line ${i + 1} unparseable`); }
  });
}

// Replay the file to know what ids exist right now.
function state(lines) {
  const s = { init: null, steps: 0, recordIds: [], sids: [], snapById: {}, readCids: new Set(), counts: { steps: 0, records: 0, sources: 0, gaps: 0 }, sealed: false };
  for (const e of lines) {
    if (e.t === 'init') s.init = e;
    else if (e.t === 'step') { s.steps = e.step; s.counts.steps++; }
    else if (e.t === 'context') { if (e.status === 'read') s.readCids.add(e.cid); }
    else if (e.t === 'source') { s.sids.push(e.sid); s.snapById[e.sid] = e.snapshot; s.counts.sources++; }
    else if (e.t === 'record') { s.recordIds.push(e.id); s.counts.records++; }
    else if (e.t === 'gap') s.counts.gaps++;
    else if (e.t === 'done') s.sealed = true;
  }
  return s;
}

// THE shared manifest resolver — one derivation, used by init validation AND the
// append-time quote check (two resolvers would disagree). Layout: journal at
// <run>/journal/<slug>.jsonl, manifest at <run>/context/<slug>-manifest.json. Null when
// absent/corrupt -> callers fall back to structural-only (the read-back gate stays authoritative).
function manifestFor(file) {
  const runDir = path.resolve(path.dirname(file), '..');
  const p = path.join(runDir, 'context', path.basename(file).replace(/\.jsonl$/, '') + '-manifest.json');
  try {
    let s = fs.readFileSync(p, 'utf8');
    if (s.charCodeAt(0) === 0xfeff) s = s.slice(1); // BOM-safe (PowerShell utf8 trap)
    const man = JSON.parse(s);
    return man && Array.isArray(man.manifest) ? man : null;
  } catch { return null; }
}

function append(file, raw) {
  let e;
  try { e = JSON.parse(raw); } catch { die('invalid json'); }
  if (!e || typeof e !== 'object' || Array.isArray(e)) die('entry must be a json object');

  const lines = readLines(file);
  const st = state(lines);

  if (e.t === 'init') {
    if (lines.length > 0) die('init must be the first line, once');
    reqStr(e, 'aspect');
    if (!Array.isArray(e.cids) || e.cids.some((c) => typeof c !== 'string')) die("'cids' required (array of C-ids)");
    if (e.must_read !== undefined) {
      if (!Array.isArray(e.must_read) || e.must_read.some((c) => !e.cids.includes(c))) die("'must_read' must be an array of ids from cids");
    }
    // Phantom-cid guard: with a ratified manifest, init.cids must EXACTLY match its
    // C-ids (subset drops assigned context; extra id is a phantom citable forever).
    // No manifest -> accept (ad-hoc journals legal; read-back closes the hole downstream).
    const iman = manifestFor(file);
    if (iman) {
      const want = iman.manifest.map((m) => m.id).sort().join(',');
      if ([...e.cids].sort().join(',') !== want) die(`init.cids must exactly match the ratified manifest C-ids (${want})`);
    }
  } else {
    if (!st.init) die('journal not initialized (append an init entry first)');
    if (st.sealed) die('journal sealed by done — no further appends');
  }

  let assigned = '';
  switch (e.t) {
    case 'init': break;
    case 'step': {
      reqStr(e, 'did'); reqStr(e, 'found');
      e.step = st.steps + 1; assigned = 'step ' + e.step; break;
    }
    case 'context': {
      reqStr(e, 'cid');
      if (!st.init.cids.includes(e.cid)) die(`unknown cid '${e.cid}' (not in manifest)`);
      if (!CTX_STATUS.includes(e.status)) die(`'status' must be one of ${CTX_STATUS.join('|')}`);
      break;
    }
    case 'source': {
      reqStr(e, 'url'); reqStr(e, 'title'); reqStr(e, 'via');
      // Raw-capture mandate: WebFetch/WebSearch return AI digests, never raw text (74/83
      // snapshots in the failed run were digests). via is self-declared -> rejects honest
      // mistakes, not liars (documented honest limit).
      if (/webfetch|websearch/.test(norm(e.via))) die(`via '${e.via}' is an LLM-processed channel — its output is a digest, not the source. Re-capture RAW (curl -o, gh api, wget, file copy) and register that file; use WebFetch/WebSearch for DISCOVERY only`);
      if (typeof e.snapshot !== 'string' || !e.snapshot.trim()) die("'snapshot' required — cite-requires-snapshot: save the retrieved content to downloads/ first");
      // Snapshot must be a real, non-empty FILE INSIDE <run>/downloads/. realpath +
      // path.relative kills traversal (../x), absolute escapes, prefix-siblings
      // (downloads-evil/), symlink escapes. Content-vs-url authenticity stays a red-team duty.
      const runDir = path.resolve(path.dirname(file), '..');
      const snapRaw = path.isAbsolute(e.snapshot) ? e.snapshot : path.resolve(runDir, e.snapshot);
      let snapReal, snapStat;
      try { snapReal = fs.realpathSync(snapRaw); snapStat = fs.statSync(snapReal); }
      catch { die(`snapshot file not found: ${snapRaw} — save the content BEFORE registering the source`); }
      let dlReal;
      try { dlReal = fs.realpathSync(path.join(runDir, 'downloads')); }
      catch { die(`run downloads/ folder not found at ${path.join(runDir, 'downloads')} — save the snapshot there first`); }
      const rel = path.relative(dlReal, snapReal);
      if (rel === '' || rel.startsWith('..') || path.isAbsolute(rel)) die(`snapshot must live INSIDE the run downloads/ folder — got ${e.snapshot}`);
      if (!snapStat.isFile() || snapStat.size === 0) die("snapshot must be a non-empty FILE — an empty or directory 'snapshot' is not saved content");
      // Snapshot-size tripwire: a small http(s) snapshot smells like a digest, but size
      // CANNOT safely reject (honest raw gh-api JSON is smaller), so this FLAGS, never
      // rejects. Script-written, persists on the line; not an authenticity proof.
      let warn = '';
      if (/^https?:\/\//i.test(e.url) && snapStat.size < 8192) {
        e.flag = 'small-snapshot';
        warn = ` [WARNING small-snapshot: ${snapStat.size} bytes for an http(s) source — verify this is a full RAW capture, not a digest]`;
      }
      e.sid = 'W' + (st.sids.length + 1); assigned = e.sid + warn; break;
    }
    case 'record': {
      if (!CLASSES.includes(e.class)) die(`'class' must be one of ${CLASSES.join('|')}`);
      reqStr(e, 'claim');
      if (!CONF.includes(e.confidence)) die(`'confidence' must be one of ${CONF.join('|')}`);
      if (!Number.isInteger(e.step)) die("'step' required — the step number this record came from");
      if (e.step < 1 || e.step > st.steps) die(`step ${e.step} does not exist yet`);
      const known = new Set([...st.init.cids, ...st.sids]);
      // Append-time quote verification: resolve each evidence.ref to a file and run the
      // SAME containsQuote the read-back gate runs — bad quotes bounce in-flight (65
      // accumulated in the incident run). Verify-when-resolvable, else ACCEPT (no manifest
      // / missing path / dir) — structural-only contract; the read-back gate is authoritative.
      const rman = manifestFor(file);
      const runDirR = path.resolve(path.dirname(file), '..');
      const cidPath = {};
      if (rman) for (const m of rman.manifest) if (typeof m.path === 'string') cidPath[m.id] = path.isAbsolute(m.path) ? m.path : path.resolve(runDirR, m.path);
      const ev = Array.isArray(e.evidence) ? e.evidence : [];
      let checked = 0;
      for (const q of ev) {
        if (!q || typeof q !== 'object') die('evidence items must be objects');
        for (const f of ['ref', 'loc', 'quote']) if (typeof q[f] !== 'string' || !q[f].trim()) die(`evidence.${f} required`);
        if (!known.has(q.ref)) die(`evidence.ref '${q.ref}' is not a registered source (manifest C-id or source W-id)`);
        if (norm(q.quote).length < MIN_QUOTE_LEN) die(`evidence.quote too short (<${MIN_QUOTE_LEN} locatable chars after folding) — quote more exact verbatim text (whitespace/punctuation-only quotes fold away and are rejected)`);
        const src = cidPath[q.ref] || (st.snapById[q.ref] ? path.resolve(runDirR, st.snapById[q.ref]) : null);
        let body = null;
        if (src) { try { if (fs.statSync(src).isFile()) body = fs.readFileSync(src, 'utf8'); } catch { body = null; } }
        if (body !== null) {
          const reason = containsQuote(body, q.quote);
          if (reason) die(`evidence.quote FAILS verification against ${q.ref} (${reason}) — "${q.quote.slice(0, 60)}..." — extract ONE contiguous span from ONE blank-line-delimited block with a tool (grep/sed on the file); a passage spanning blank lines is one evidence item per block`);
          checked++;
        }
      }
      // Script-written check stamp (agent value discarded): 'verified' = every quote
      // resolved to a file + passed containsQuote here; 'unresolvable' = some ref had no
      // readable file, so accepted unchecked (read-back settles it). Makes fallback-ACCEPT visible.
      delete e.qcheck;
      if (ev.length) e.qcheck = checked === ev.length ? 'verified' : 'unresolvable';
      const dep = Array.isArray(e.based_on) ? e.based_on : [];
      for (const d of dep) if (!st.recordIds.includes(d)) die(`based_on '${d}' names no existing record`);
      if (dep.length > 0) {
        reqStr(e, 'reasoning');
        // Floor kills single-char stubs only; reasoning QUALITY stays a human judgement.
        if (norm(e.reasoning).length < 10) die("'reasoning' too short (<10 folded chars) — state the actual inference, not a stub");
      }
      e.id = 'a' + (st.recordIds.length + 1);
      assigned = e.id + (e.qcheck ? ` [qcheck: ${e.qcheck}]` : ''); break;
    }
    case 'gap': { reqStr(e, 'what'); break; }
    case 'done': {
      const mr = (st.init.must_read || []).filter((c) => !st.readCids.has(c));
      if (mr.length > 0) die(`cannot seal: must_read items never reached status 'read': ${mr.join(', ')}`);
      e.counts = { ...st.counts }; assigned = JSON.stringify(e.counts); break;
    }
    default: die(`unknown entry type '${e.t}'`);
  }

  e.ts = new Date().toISOString(); // script-stamped, never agent-supplied
  fs.appendFileSync(file, JSON.stringify(e) + '\n', 'utf8');
  process.stdout.write('OK ' + (assigned || e.t) + '\n');
}

// evidence present -> grounded; based_on only -> derived; neither -> assertion (flagged).
function basisOf(r) {
  if (Array.isArray(r.evidence) && r.evidence.length > 0) return 'grounded';
  if (Array.isArray(r.based_on) && r.based_on.length > 0) return 'derived';
  return 'assertion';
}

function assembleObj(file) {
  const lines = readLines(file);
  const st = state(lines);
  if (!st.init) die('journal not initialized');
  return {
    aspect: st.init.aspect,
    sealed: st.sealed,
    counts: st.counts,
    records: lines.filter((l) => l.t === 'record').map((r) => ({ ...r, basis: basisOf(r) })),
    context_ledger: lines.filter((l) => l.t === 'context'),
    sources: lines.filter((l) => l.t === 'source'),
    gaps: lines.filter((l) => l.t === 'gap'),
    log: lines.filter((l) => l.t === 'step'),
  };
}

// Mechanical layout: verbatim fields only — no synthesis, ranking, or reword. CONSULTS
// the read-back gate: reads <run>/readback-verdict.json and, when FRESH (journal-bytes
// sha256 matches), pulls untrusted + tainted records OUT of their tiers into a leading
// UNTRUSTED section. Missing/stale verdicts degrade LOUDLY to shape-only tiers, never to
// silent wrong labels. Render never re-verifies quotes: the gate is the single verifier.
function render(file) {
  const a = assembleObj(file);
  const out = [];
  const runDir = path.resolve(path.dirname(file), '..');
  const slug = path.basename(file).replace(/\.jsonl$/, '');
  let vj = null, vLine = 'NO GATE VERDICT -- run verify-readback.js first; tier labels below are UNVERIFIED';
  try {
    let s = fs.readFileSync(path.join(runDir, 'readback-verdict.json'), 'utf8');
    if (s.charCodeAt(0) === 0xfeff) s = s.slice(1);
    const v = JSON.parse(s);
    const j = v && v.journals && v.journals[slug];
    if (j) {
      const sha = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
      if (sha === j.journalSha256) { vj = j; vLine = `gate verdict: ${v.gate} (verified ${v.ranAt})`; }
      else vLine = 'STALE GATE VERDICT -- journal changed since verify-readback.js ran; re-run the gate; tier labels below are UNVERIFIED';
    }
  } catch { /* no verdict file -> loud default line */ }
  const flag = {}; // record id -> gate annotation (untrusted reason or taint path)
  if (vj) {
    for (const u of vj.untrusted || []) flag[u.id] = `gate: ${(u.reasons || []).join('; ')}`;
    for (const x of vj.tainted || []) flag[x.id] = `tainted via ${x.via}`;
  }
  const tbSet = new Set(vj ? vj.taintedBasis || [] : []);
  const row = (r, extra) => {
    out.push(`- [${r.id}] (${r.class}, ${r.confidence}, step ${r.step}) ${r.claim}`);
    for (const q of r.evidence || []) out.push(`    evidence ${q.ref} @ ${q.loc}: "${q.quote}"`);
    if (r.based_on && r.based_on.length) out.push(`    based_on: ${r.based_on.join(', ')} — ${r.reasoning}`);
    for (const c of r.caveats || []) out.push(`    caveat: ${c}`);
    if (extra) out.push(`    ${extra}`);
  };
  out.push(`# COUNSEL JOURNAL — aspect: ${a.aspect}${a.sealed ? '' : '   [NOT SEALED — incomplete run]'}`);
  out.push(`counts: steps ${a.counts.steps} · records ${a.counts.records} · sources ${a.counts.sources} · gaps ${a.counts.gaps}`);
  out.push(vLine);
  // Zero-grounded is shape-computable, so this warning works with or without a verdict
  // (LH a33); the gate prints its own banner from the same shape facts.
  if (!a.records.some((r) => r.basis === 'grounded')) {
    out.push('ZERO GROUNDED RECORDS -- nothing in this journal was verified against any source; treat every claim as unverified');
  }
  const bad = a.records.filter((r) => flag[r.id]);
  if (bad.length) {
    out.push('', `## UNTRUSTED (read-back gate) -- ${bad.length}`);
    for (const r of bad) row(r, flag[r.id]);
  }
  for (const tier of ['grounded', 'derived', 'assertion']) {
    const rows = a.records.filter((r) => r.basis === tier && !flag[r.id]);
    out.push('', `## ${tier.toUpperCase()} — ${rows.length}`);
    for (const r of rows) {
      // Verified quotes + poisoned basis: evidence stands, inference is caveated (LH a30).
      const via = tbSet.has(r.id) ? (r.based_on || []).find((d) => flag[d]) : null;
      row(r, via ? `CAVEAT: based_on cites untrusted ${via}` : null);
    }
  }
  out.push('', `## CONTEXT LEDGER — ${a.context_ledger.length}`);
  for (const c of a.context_ledger) out.push(`- ${c.cid}: ${c.status}${c.note ? ' — ' + c.note : ''}`);
  out.push('', `## SOURCES REGISTERED — ${a.sources.length}`);
  for (const s of a.sources) out.push(`- ${s.sid}: ${s.title} · ${s.url} · via ${s.via} · snapshot ${s.snapshot}${s.flag ? ` [${s.flag}]` : ''}`);
  out.push('', `## GAPS — ${a.gaps.length}`);
  for (const g of a.gaps) out.push(`- ${g.what}`);
  process.stdout.write(out.join('\n') + '\n');
}

// FIRE-discipline poll target: one line per journal, exit non-zero while any is unsealed
// — masters loop this instead of waiting silently. Lenient parse (corrupt line = unsealed, not a crash).
function status(runDirArg) {
  const jd = path.join(runDirArg, 'journal');
  let files = [];
  try { files = fs.readdirSync(jd).filter((f) => f.endsWith('.jsonl')); } catch { die(`no journal/ dir at ${jd}`); }
  if (files.length === 0) { process.stdout.write('no journals yet\n'); process.exit(1); }
  let unsealed = 0;
  for (const f of files.sort()) {
    let raw = fs.readFileSync(path.join(jd, f), 'utf8');
    if (raw.charCodeAt(0) === 0xfeff) raw = raw.slice(1);
    const ls = raw.split('\n').filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    const st = state(ls);
    if (!st.sealed) unsealed++;
    process.stdout.write(`${st.sealed ? 'SEALED  ' : 'UNSEALED'} ${f.replace('.jsonl', '').padEnd(22)} steps ${st.counts.steps} · records ${st.counts.records} · sources ${st.counts.sources} · gaps ${st.counts.gaps}\n`);
  }
  process.exit(unsealed ? 1 : 0);
}

const [cmd, file, payload] = process.argv.slice(2);
if (!cmd || !file) die('usage: journal.js append <file> [<json>|stdin] | assemble <file> | render <file> | status <run_dir>');
if (cmd === 'append') { append(file, payload != null ? payload : fs.readFileSync(0, 'utf8')); }
else if (cmd === 'assemble') process.stdout.write(JSON.stringify(assembleObj(file), null, 2) + '\n');
else if (cmd === 'render') render(file);
else if (cmd === 'status') status(file);
else die(`unknown command '${cmd}'`);
