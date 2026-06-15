# FIX-PASS EXECUTION PLAN — 2026-06-15 (compaction-safe; supersedes the "what's left" half of _RESUME_2026_06_15.md)

User-locked scope (2026-06-15):
- **§4.3 + §4.4 robustness ARE in scope** → write exhaustively, each with its OWN full 4-bin table.
- **Tables**: TWO full standalone 4-bin tables (mirror tab:empire_drop_matched), prose points to + explains each.
- **Front-matter thread (M1)**: FULL thread — abstract sentence + intro finding + contributions 3→4 + roadmap + conclusion.
- Convention (user reaffirmed 2x): edit JSON ledger prose → **programmatically push** to LaTeX. LaTeX MUST equal ledger. NEVER hand-edit .tex prose.

## Authoritative numbers — `outputs/econometric/robustness_drop_sec43_44/2026-06-15_062647/summary.json` (READ IT; never hand-type)
- Baseline (matched, =§3.3): UncRes PRE1 0.0473***, GAP 0.0018, POST -0.0250*, PRE1-POST 0.0723***, PRE1-GAP 0.0455**. Cash PRE1-POST 0.0216***, GAP-POST 0.0210***, PRE1-GAP 0.0006 ns. N 28,102/1,320.
- §4.3 resolution (withdrawal in POST): UncRes PRE1 0.0479***, GAP 0.0022, POST -0.0208 ns, **PRE1-POST 0.0687*** (p2 .00026)**, PRE1-GAP 0.0457**. Cash PRE1-POST 0.0204***. **N 28,191/1,321 = +89 firm-quarters / +1 firm** (NOT "28 firms" — that was the raw withdrawn count, WRONG for the sample).
- §4.4 static-FE (drop CashRatio_lag): UncRes unchanged (no lag anyway). Cash (no lag) PRE1 0.0116**, GAP 0.0128**, POST -0.0189***, **PRE1-POST 0.0305*** (p2 6e-12)**, GAP-POST 0.0318***, PRE1-GAP -0.0012 ns. N 28,102/1,320.
- Stars two-tailed (matches §3.3): *** p<.01, ** p<.05, * p<.10 — derive from p2 programmatically.

## Calibration locks (advisor-checked earlier; DO NOT relitigate)
- §4.3 = "consistent with / does not overturn", NOT "robust". Disclose +89 fq / +1 firm (low power). Point: POST drop is not a completed-deal-selection artifact.
- §4.4 = KEEP CashRatio_lag in the MAIN spec; frame no-lag only as "the drop does not ride on the dynamic (lagged-DV) term". Nickell bias O(1/T), T~68 → negligible.

## Pipelines
- §3/§4 body: section{3.1,3.2,3.3,3.4,4.1,4.2[,4.3,4.4]}_paragraph_ledger.json → `tmp/build_sec34_body.py` → sec34_body_from_ledgers.tex (\input at uottawa L254).
- intro/abstract/concl: section{1,abstract,5}_paragraph_ledger.json → `tmp/build_introconcl_body.py` → _intro/_abstract/_conclusion_body.tex (\input L151/117/257).
- tables: bible `docs/Draft/thesis_tables.tex` → `tmp/extract_draft_tables.py` (THESIS_TABLES list) → _tables_from_bible.tex (\input L322).
- **§2 = INLINE in uottawa.tex L216-250, NO assembler.** M4 (Nickell, §2.4 P5) + any §2 minor → edit ledger then SURGICAL programmatic push (swap that one paragraph block by exact match). Do NOT regenerate all of §2 (LOCKED §2.1 has em-dashes; ledger may differ).

## PHASES (commit per phase; recompile-verify each)

**P1 — §4.3/4.4 tables (foundation).**
1. Read bible tab:empire_drop_matched block + extract_draft_tables.py THESIS_TABLES.
2. Script reads summary.json → PRINTS two LaTeX table blocks (tab:empire_drop_resolution, tab:empire_drop_staticfe), 4 bins × 2 DV + 3 drops + N/firms, two-tailed stars. Insert into bible via Edit (numbers programmatic, not typed).
3. Register both keys in THESIS_TABLES; run extract. VERIFY numbers == summary.json.

**P2 — §4.3/4.4 ledgers + prose.**
4. Create section4.3 + section4.4 ledgers (proposition chains + final_prose; prose \ref's + explains its table; calibration locks). 4.3 = resolution; 4.4 = static-FE.
5. Register 4.3,4.4 in build_sec34_body.py (+comment). Build. VERIFY prose numbers trace summary.json; ledger==tex.

**P3 — §4.2 fixes.**
6. PARA3 final_prose: drop DWZ "presentation…outsiders respond" clause (M2) → BGT-only. Sync proposition_chain+intent.
7. PARA4 final_prose: remove untested "different audiences"/"asymmetry"; two per-component facts + "no between-component test run" (M3); soften causal verbs "moves/widening" (L1/W1). Build. VERIFY.

**P4 — disclosures.**
8. §2.4 ledger P5: +Nickell sentence (lag+firmFE → dyn-panel bias O(1/T); T~68 negligible; focal coef = treatment not lag; §4.4 confirms). SURGICAL push to uottawa L238 block. VERIFY ledger==tex.
9. §3.3 ledger: PARA1 +completed-only-POST & withdrawn-drop disclosure, foreground PRE1-GAP leg, point to §4.3 (M5). PARA5 drop "independent" (L2). PARA4 attach "information public" to PRE1-GAP 0.0455** not PRE1-POST (L3). Build. VERIFY.

**P5 — M1 full thread.**
10. Read section_abstract, section5, section4.1 ledgers.
11. Abstract: +1 spread/channel-asymmetry sentence.
12. Intro: P9 roadmap → "additional analyses" plural (scrutiny + spread + 2 robustness); P5/P6 +spread finding & fix "four parts" (H1); P7 contributions 3→4 (+outsider-reaction/channel-asymmetry).
13. Conclusion: +1 thread sentence. Build introconcl. VERIFY.

**P6 — cohesion/citation minors (LOWER priority; some touch LOCKED §2.1 — flag before editing).**
- H2 call-level vs call-varying (2.1/2.3); C4 log DWZ repl numbers as ground truth; C5 legal=accept (no-op); C6 thewissen gloss (intro already avoids — check).

**P7 — recompile + verify.**
- Kill Acrobat; pdflatex x3; 0 undefined refs; all new \ref resolve; open PDF. Commit.

## Verify-each rule (Karpathy goal-driven)
After every ledger edit: rerun the matching assembler, then confirm the .tex block == ledger final_prose (the "serious flaw" guard). After every table edit: confirm _tables_from_bible.tex numbers == summary.json / bible. After all: pdflatex 0 undefined refs.
