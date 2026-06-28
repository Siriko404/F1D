// gates.mjs — the deterministic safety spine of the prose harness.
// Pure JS, no LLM, no I/O. These functions run INSIDE the workflow between agent layers
// (lessons §3/§8: the JS gate is the anti-hallucination spine; agents never self-grade).
// A paragraph that trips any BLOCK gate cannot move forward. FLAGs are non-fatal (routed to audit).

// ---------- helpers ----------
const normVal = (s) => s.replace(/^[+-]/, "").replace(/^0+(?=\.)/, "").trim(); // sign + leading-zero agnostic
// LaTeX writes significance as ^{***} / $^{**}$ ; collapse to literal stars adjacent to the number
// so prose tokens match the props' literal-star form (this notation trap bit the source-table parse too).
const deLatexStars = (s) => s.replace(/\^\{(\*{1,3})\}/g, "$1").replace(/\^(\*{1,3})/g, "$1").replace(/\$/g, "");
const COEF = /[+-]?\d?\.\d{3,4}(\*{1,3})?/g;     // coefficient-shaped token (3-4 decimals) + optional stars
const splitTok = (t) => {
  const m = t.match(/^([+-]?\d?\.\d{3,4})(\*{1,3})?$/);
  return m ? { val: normVal(m[1]), stars: m[2] || "" } : null;
};
// extract coefficient tokens from prose, LaTeX-star-aware; keep the raw token for readable messages
const coefTokens = (prose) => [...deLatexStars(prose).matchAll(COEF)]
  .map(m => { const s = splitTok(m[0]); return s ? { ...s, raw: m[0] } : null; }).filter(Boolean);

// ---------- GATE 1: number-trace (anti-fabrication) ----------
// every coefficient-shaped token in prose must come from this paragraph's allowed set
// (props' numbers, already source-verified). Magnitude citations (no stars) need only the value.
// allowedTokens = the SECTION's full set (union of all paragraphs' prop numbers), so a paragraph may
// back-reference a number proved elsewhere in the section. exact value+stars -> ok; bare value -> ok
// (magnitude); value-with-extra-stars -> BLOCK (over-claims significance); a rounding/precision variant
// of a real number -> FLAG (the audit/boss restores the exact figure); anything else -> BLOCK (fabricated).
export function gateNumbers(prose, allowedTokens) {
  const exact = new Set(), vals = new Set(), nums = [];
  for (const t of allowedTokens) { const s = splitTok(t); if (s) { exact.add(s.val + s.stars); vals.add(s.val); nums.push(parseFloat(t.replace(/\*/g, ""))); } }
  const blocks = [], flags = [];
  for (const s of coefTokens(prose)) {
    if (exact.has(s.val + s.stars)) continue;
    if (s.stars === "" && vals.has(s.val)) continue;
    if (vals.has(s.val)) { blocks.push(`number "${s.raw}": value present but with WRONG/EXTRA stars (over-claims significance)`); continue; }
    const pf = parseFloat(s.raw.replace(/\*/g, ""));
    const dec = ((s.raw.split(".")[1] || "").replace(/\*/g, "")).length;
    const isRounding = nums.some(n => Math.abs(Number(n.toFixed(dec)) - pf) < 1e-9);
    if (isRounding) flags.push(`number "${s.raw}": rounded/precision variant of a source figure -- restore exact value`);
    else blocks.push(`number "${s.raw}": NOT in this section's allowed set (fabricated/altered)`);
  }
  return { blocks, flags };
}

// ---------- GATE 2: honesty-FORBID (register floor) ----------
const FORBID = [/suppress/i, /dampen/i, /strict specificity/i, /\bwe are the first\b/i,
                /\bto mask\b/i, /manipulat/i, /\bdetect/i, /\bin order to mask\b/i];
export function gateHonesty(prose) {
  const blocks = [];
  for (const re of FORBID) { const m = prose.match(re); if (m) blocks.push(`forbidden phrase "${m[0]}" (honesty floor)`); }
  return blocks;
}

// ---------- GATE 3: citation whitelist ----------
export function gateCites(prose, allowedKeys) {
  const allow = new Set(allowedKeys); const blocks = [];
  for (const m of prose.matchAll(/\\cite[tp]\{([^}]*)\}/g))
    for (const k of m[1].split(",").map(x => x.trim()))
      if (k && !allow.has(k)) blocks.push(`citation key "${k}" not in this paragraph's allowed set`);
  return blocks;
}

// ---------- GATE 4: bijection / completeness ----------
// every prop that carries a signature number must have that number rendered; none silently dropped.
export function gateBijection(prose, props) {
  const flags = [];
  const toks = coefTokens(prose);
  for (const p of props) {
    if (!p.signature) continue;            // conceptual prop (no number) -> can't check here, audit handles
    const s = splitTok(p.signature); if (!s) continue;
    if (!toks.some(q => q.val === s.val)) flags.push(`prop ${p.prop_id}: signature number ${p.signature} not rendered (possibly dropped)`);
  }
  return flags;
}

// ---------- GATE 5: LaTeX-lint (compile safety) ----------
export function gateLatex(prose) {
  const blocks = [];
  const open = (prose.match(/(?<!\\)\{/g) || []).length, close = (prose.match(/(?<!\\)\}/g) || []).length;
  if (open !== close) blocks.push(`unbalanced braces ({=${open}, }=${close}) -> compile break`);
  if (((prose.match(/(?<!\\)\$/g) || []).length) % 2 !== 0) blocks.push(`odd number of $ -> math-mode compile break`);
  const badPct = prose.match(/(?<!\\)%/); if (badPct) blocks.push(`unescaped % -> truncates line in LaTeX`);
  return blocks;
}

// ---------- runner ----------
export function runGates(par) {
  const blocks = [], flags = [];
  const n = gateNumbers(par.prose, par.allowedTokens);
  blocks.push(...n.blocks); flags.push(...n.flags);
  blocks.push(...gateHonesty(par.prose));
  blocks.push(...gateCites(par.prose, par.allowedKeys));
  blocks.push(...gateLatex(par.prose));
  flags.push(...gateBijection(par.prose, par.props || []));
  return { pass: blocks.length === 0, blocks, flags };
}
