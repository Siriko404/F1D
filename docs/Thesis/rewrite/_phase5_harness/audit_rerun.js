export const meta = {
  name: 'thesis-audit-rerun-2',
  description: 'Re-run ONLY the 2 referees that stalled mid-stream on opus-max (methodology, completeness), on opus + HIGH effort (shorter streams, no stall). Each reads only the flat audit file and writes its own JSONL findings file gradually. Identify-only, NEVER fix.',
  phases: [{ title: 'Rerun', detail: 'methodology + completeness only' }],
}

const AUDIT_FILE = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D-phase3/docs/Thesis/_uottawa_rewrite/_thesis_AUDIT.tex'
const REPORT_DIR = 'C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D-phase3/docs/Thesis/rewrite/_phase5_harness/_audit_reports'

const PREAMBLE = (key, panel) =>
  `ULTRATHINK. Reason exhaustively, adversarially, and conservatively -- this is the final, referee-proof ` +
  `audit before submission; a missed flaw is a fatal failure.\n\n` +
  `You are a hostile, meticulous PhD thesis EXAMINER. Read ONLY this one file (one Read call, no other reads): ` +
  `${AUDIT_FILE}\nIt is fully self-contained (prose + all 21 tables + bibliography + appendices + an AUDIT-AIDS ` +
  `comment header mapping every \\ref to its table number, every \\citet to Author(Year), and column maps for ` +
  `multi-panel tables). Resolve everything from inside it. No external lookups.\n\n` +
  `HARD RULES:\n` +
  `- NEVER edit/write/modify the thesis or any file other than your OWN report file. Applying a fix is forbidden.\n` +
  `- Your report file is EXACTLY: ${REPORT_DIR}/${key}_${panel}.jsonl\n` +
  `- Write GRADUALLY: the moment you confirm a finding, append ONE compact single-line JSON object, THEN keep ` +
  `analysing. Do NOT hold everything for a giant final dump. Append with a quoted heredoc (safe for apostrophes):\n` +
  `    cat >> '${REPORT_DIR}/${key}_${panel}.jsonl' <<'J'\n` +
  `    {"kind":"finding","referee":"${key}","panel":"${panel}","aspect":"...","location":"section or table label","severity":"high|medium|low","problem":"...","evidence":["shortest proving phrase"],"best_fix":"...","fix_evidence":["..."],"confidence":"high|medium|low","refutation":"strongest case this is NOT a problem"}\n` +
  `    J\n` +
  `  One JSON object PER LINE (JSONL); keep every string terse (evidence = a few words). For each aspect checked ` +
  `and found SOUND append {"kind":"clean_bill","referee":"${key}","aspect":"...","why":"...","evidence":["..."]}. ` +
  `End with exactly one {"kind":"sweep","referee":"${key}","completeness":"what I might still have missed"}.\n` +
  `- Be EXTRA conservative: when unsure, record a low-confidence finding rather than stay silent.\n\n` +
  `Your final chat reply must be ONE short line (counts only). DIMENSION FOCUS:\n`

const REFEREES = [
  { key: 'completeness', focus:
    `Completeness & hypothesis<->test. Is every hypothesis (H1, H1a, H1b, ...) stated, TESTED, and given a verdict ` +
    `-- none dropped, verdicts consistent? Does every roadmap promise ("we do X in Section Y", "three checks") get ` +
    `delivered? Is every symbol/variable/acronym defined before first use? Any orphan reference, dangling ` +
    `"see Section/Table X", leftover placeholder/TODO, or numbering/TOC mismatch?` },
  { key: 'methodology', focus:
    `Methodology & examiner-defensibility + typesetting. As a skeptical examiner: do the stated caveats actually ` +
    `cover the inferential threats, or is any claim stronger than the design supports? Is robustness coverage ` +
    `adequate; any glaring omission an examiner would demand? Is the limitations section honest and complete? ` +
    `Flag any visible typesetting problem (malformed table, broken math, obviously oversized table).` },
]

phase('Rerun')
const tasks = REFEREES.map(r => () => agent(PREAMBLE(r.key, 'A') + r.focus,
  { label: `${r.key}:A`, phase: 'Rerun', model: 'opus', effort: 'high' }))
const summaries = (await parallel(tasks)).filter(Boolean)
log(`rerun done: ${summaries.length}/2 referees finished`)
return { rerun: REFEREES.map(r => r.key), agent_summaries: summaries }
