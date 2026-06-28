export const meta = {
  name: 'thesis-final-audit',
  description: 'Referee-proof thesis audit: ONE panel of 7 opus referees (max effort), each reads only the single flat audit file and writes its OWN findings file GRADUALLY (one JSONL line per finding) -- no giant output, no max_tokens. Identify-only, NEVER fix. Merge is programmatic.',
  phases: [{ title: 'Audit', detail: '7 referees, one per dimension, writing their own report files' }],
}

const AUDIT_FILE = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D-phase3/docs/Thesis/_uottawa_rewrite/_thesis_AUDIT.tex'
const REPORT_DIR = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D-phase3/docs/Thesis/rewrite/_phase5_harness/_audit_reports'
const PANELS = ['A']   // one panel (Sina). Gradual per-agent file writes are the real max_tokens fix.

const FLOOR = [
  'Correlational, NOT causal -- no causal verb may sneak in.',
  'Identification is within-firm; the design identifies no cause.',
  'Concentration in cash deals, NOT strict cash-specificity.',
  'Mechanism is OPEN / unestablished (the war-chest channel is not shown).',
  'Findings are supportive, NOT definitive; "we interpret, we do not detect".',
  'The stock arm is a NOISY FLAT NULL -- never "suppressed" or "dampened".',
  'Cash accumulates as a BY-PRODUCT of retained free cash flow -- never a deliberate "war chest".',
  'Novelty is hedged ("to our knowledge"); never claim to be the "first".',
].map((s, i) => `  ${i + 1}. ${s}`).join('\n')

const PREAMBLE = (key, panel) =>
  `ULTRATHINK. Reason exhaustively, adversarially, and conservatively at MAXIMUM effort -- this is the final, ` +
  `referee-proof audit before submission; a missed flaw is a fatal failure.\n\n` +
  `You are a hostile, meticulous PhD thesis EXAMINER. Read ONLY this one file (one Read call, no other reads): ` +
  `${AUDIT_FILE}\nIt is fully self-contained (prose + all 21 tables + bibliography + appendices + an AUDIT-AIDS ` +
  `comment header that maps every \\ref to its table number, every \\citet to Author(Year), and gives column ` +
  `maps for multi-panel tables). Resolve everything from inside it. Make NO external lookups.\n\n` +
  `HARD RULES:\n` +
  `- NEVER edit, write, or modify the thesis or any file other than your OWN report file. Applying a fix is ` +
  `strictly forbidden -- you only identify, evidence, and propose.\n` +
  `- Your report file is EXACTLY: ${REPORT_DIR}/${key}_${panel}.jsonl\n` +
  `- Write it GRADUALLY: the moment you confirm a finding, append ONE compact single-line JSON object to that ` +
  `file, THEN continue analysing. Never accumulate everything for one giant final dump. Append with a quoted ` +
  `heredoc so apostrophes/quotes are safe, e.g.:\n` +
  `    cat >> '${REPORT_DIR}/${key}_${panel}.jsonl' <<'J'\n` +
  `    {"kind":"finding","referee":"${key}","panel":"${panel}","aspect":"...","location":"section or table label","severity":"high|medium|low","problem":"...","evidence":["shortest proving phrase, a few words"],"best_fix":"...","fix_evidence":["..."],"confidence":"high|medium|low","refutation":"strongest case this is NOT a problem"}\n` +
  `    J\n` +
  `  One JSON object PER LINE (JSONL). Keep every string terse (evidence = a few words, never a whole sentence). ` +
  `For each aspect you checked and found SOUND, append {"kind":"clean_bill","referee":"${key}","aspect":"...","why":"...","evidence":["..."]}. ` +
  `When done, append exactly one {"kind":"sweep","referee":"${key}","completeness":"what in my dimension I might still have missed"}.\n` +
  `- Be EXTRA conservative: when unsure, record it as a low-confidence finding rather than stay silent.\n\n` +
  `Your final chat reply must be ONE short line: how many findings + clean-bills you appended. Do NOT dump the ` +
  `findings into the chat -- they live in your file.\n\nDIMENSION FOCUS (your charter):\n`

const REFEREES = [
  { key: 'numbers', focus:
    `Numbers & Tables. For EVERY numeric claim in the prose: does it match the EXACT cited table cell (value, ` +
    `sign, standard error, significance/stars, N, R^2)? Recompute derived numbers (economic effects = coef/SD ` +
    `and %-of-mean; bin drops = differences; Wald = beta_c - beta_s). Does the prose DIRECTION match the sign ` +
    `("rises" => positive coef)? Do significance words match the table stars and the stated tail (one/two-tailed)? ` +
    `Table-internal sanity (columns match headers, bold == significant).` },
  { key: 'honesty', focus:
    `Honesty floor / overclaiming. The thesis has a LOCKED honesty floor -- verify it holds in EVERY section, ` +
    `flag any breach, AND flag if de-hedging left a section UNDER-hedged:\n${FLOOR}\n` +
    `Flag any sentence stronger than the design supports; any causal slip; any "first/proves/establishes/detects".` },
  { key: 'coherence', focus:
    `Coherence, cohesion & narrative. Does the argument arc hold (motivation -> hypotheses -> method -> results ` +
    `-> interpretation -> conclusion)? Does the ABSTRACT match the body and the CONCLUSION (every abstract claim ` +
    `delivered; conclusion summarises only what is shown)? Any cross-section CONTRADICTION, broken transition, or ` +
    `non-sequitur?` },
  { key: 'completeness', focus:
    `Completeness & hypothesis<->test. Is every hypothesis (H1, H1a, H1b, ...) stated, TESTED, and given a verdict ` +
    `-- none dropped, verdicts consistent? Does every roadmap promise ("we do X in Section Y", "three checks") get ` +
    `delivered? Is every symbol/variable/acronym defined before first use? Any orphan reference, dangling ` +
    `"see Section/Table X", leftover placeholder/TODO, or numbering/TOC mismatch?` },
  { key: 'citations', focus:
    `Citations & attribution. Does every \\citet/\\citep resolve to a bibitem (use the header map)? Is every ` +
    `borrowed method/claim cited? Is in-text author/year internally consistent? SEPARATELY, for EVERY claim the ` +
    `prose attributes to a specific paper ("DWZ report ...", "BGT find ..."), append a low-severity finding with ` +
    `aspect "external-attribution" quoting it -- a checklist to verify against sources later (you cannot verify ` +
    `external accuracy from this file).` },
  { key: 'style', focus:
    `Style, notation & terminology. Is notation uniform after the recent revision (p-values as $p<.01$ etc., ` +
    `standard-error format, no-leading-zero, dashes, math)? Is the plain-language register consistent and jargon ` +
    `explained at first use? Is terminology stable (no synonym drift for one construct, e.g. UncResCEO)? Any ` +
    `tense/voice inconsistency or LaTeX artifact leaking into rendered text?` },
  { key: 'methodology', focus:
    `Methodology & examiner-defensibility + typesetting. As a skeptical examiner: do the stated caveats actually ` +
    `cover the inferential threats, or is any claim stronger than the design supports? Is robustness coverage ` +
    `adequate; any glaring omission an examiner would demand? Is the limitations section honest and complete? ` +
    `Flag any visible typesetting problem (malformed table, broken math, obviously oversized table).` },
]

phase('Audit')
const ONLY = (args && args.only) ? args.only : null          // re-run only a subset of referees if given
const EFFORT = (args && args.effort) ? args.effort : 'max'   // default max; reruns use 'high' to avoid mid-stream stalls
const tasks = []
for (const panel of PANELS) {
  for (const r of REFEREES) {
    if (ONLY && !ONLY.includes(r.key)) continue
    tasks.push(() => agent(PREAMBLE(r.key, panel) + r.focus,
      { label: `${r.key}:${panel}`, phase: 'Audit', model: 'opus', effort: EFFORT }))
  }
}
const summaries = (await parallel(tasks)).filter(Boolean)
log(`all ${summaries.length}/${PANELS.length * REFEREES.length} referees finished; reports written to ${REPORT_DIR}`)
return { panels: PANELS, referees: REFEREES.map(r => r.key), report_dir: REPORT_DIR, agent_summaries: summaries }
