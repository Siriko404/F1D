# One-shot: update _RESUME_STATE.json with the 2026-06-13 verification results + pending edits.
import json

p = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(p, encoding="utf-8"))

d["updated"] = "2026-06-13 (post 2.5 yardstick NLM-verification; reframe+fixes decided, UNAPPLIED)"

d["where_we_are"] = (
"[2026-06-13] 2.1 COMPLETE (in thesis_draft.tex). 2.2-2.5 PLANNED (4 ledgers, all props PLANNED, prose BLOCKED). "
"THEN, prompted by user review of the plans, ran a 2.5 YARDSTICK-VERIFICATION detour: 2.5's validity tests lean on 4 external "
"'yardstick' papers (hoberg2016 product-market competition, hassan2020 PRisk, baker2016 US-EPU, davis2016 GEPU); user mandated "
"verifying their EXACT definitions from NLM before claiming any yardstick test valid. DONE -> tmp/nlm_validity_definitions.json "
"(content-discovery via docs/Thesis/rewrite/nlm_validity_defs.py). KEY LOAD-BEARING FINDING: the competition measure (Hoberg-Phillips "
"TNIC total similarity, z_log_TSIMM) is TIME-VARYING firm-year, NOT a 'persistent industry trait' as 2.5 P3.2/P3.3 currently claim "
"-- VERIFIED from Hoberg 688176.pdf own words (clean spans: 'the network is time varying'; 'classifications that change over time'; "
"observations at the firm-year level). => 2.5 P3 must REFRAME to content-location. Also this session: NLM_QUERY_GUIDE.md fully "
"REWRITTEN (identity scar sec4 'a filename is NEVER the paper'; content-discovery sec3a; the '--new' CLI flag proven FAKE -> "
"isolation = clear+unscoped). NOTHING written into any ledger yet -- all findings in tmp + committed; the 2.5 reframe and the "
"2.2/2.3 wording fixes are DECIDED + advisor-reconciled but UNAPPLIED (see PENDING_EDITS_unapplied)."
)

d["validity_yardsticks_VERIFIED_2026_06_13"] = {
 "_note": "NLM content-discovery (unscoped clear+ask naming the paper; source found by CONTENT, not filename). Evidence + verbatim spans in tmp/nlm_validity_definitions.json. These 4 are NO LONGER in the write-time 'owed' list.",
 "hoberg2016 (TNIC competition)": "source 688176.pdf (dc4cd3f0). LOCKED. Def n2 (sum of pairwise similarities, given year), p.1446 sec V.B 'Competition and Reported Peers'. TIME-VARYING: spans n4/n6/n7 -- VERBATIM n7 (THE span the reframe rides on): 'Because firms update their 10-Ks, the network is time varying.'; n4: 'allowing us to build classifications that change over time'. Direction (higher sim=more competition) answer-sourced only (not load-bearing).",
 "hassan2020 (PRisk)": "source qjz021 (1).pdf (eb9f6df7). LOCKED. PRisk = weighted share of a firm's QUARTERLY earnings call devoted to political risk; capped 99th pct, standardized (spans n2/n3/n5). Risk/uncertainty proxy, firm-quarter.",
 "baker2016 (US-EPU)": "source qjw024.pdf (ebca6160). LOCKED. EPU = newspaper-frequency index (trio: economy+uncertainty+policy terms), MONTHLY, US + 11 countries (spans n2/n3). Uncertainty proxy, macro.",
 "davis2016 (GEPU)": "source w22740.pdf (45de8338). PROVISIONAL (guide sec9): identity self-confirmed + n3 lead-in span; full def ('GDP-weighted avg of national EPU for 16 countries') is ANSWER-located, not a clean span. Weakest 'consistent with' benchmark. DISPOSITION (user+advisor): provisional is ACCEPTABLE for this benchmark -> FOLD AS-IS into 2.5, do NOT re-query; it does NOT block the 2.5 fold."
}

d["PENDING_EDITS_unapplied"] = {
 "_note": "DECIDED + advisor-reconciled this session; NOT yet written to any ledger. Transfer PROGRAMMATICALLY (no hallucination). User: do 2.5 NOW (step 1); KEEP 2.2/2.3 QUEUED to the ratification pass.",
 "2.5_DO_NOW": [
   "P3.2/P3.3 REFRAME: replace 'persistent industry trait/condition' with CONTENT-LOCATION. Competition (Hoberg TNIC) is TIME-VARYING (verified). The discriminant claim RIDES the regression result (competition->UncPre 0.0304***/0.0302*** vs ->UncRes 0.0008/0.0023 n.s., tab:h23) + the time-varying property (kills the persistence-artifact reading). The 'why' (competition voiced in scripted presentation, not spontaneous residual) = ONE HEDGED interpretive clause, NOT asserted fact (advisor #1).",
   "FOLD the 4 verified yardstick definitions (one-clause 'what+whose', from tmp/nlm_validity_definitions.json) so each validity test is justified by its yardstick's real definition. Convergent (PRisk/EPU/GEPU) = brief cite; discriminant (competition) leads.",
   "FOREGROUND CashScrutiny as OUR constructed measure + its own validity (currently buried as step-(i) of the rule-out)."
 ],
 "2.2_QUEUED": [
   "P2.3: DROP 'involuntary' -- contradicts 2.1 P7 (keeps strategic-silence reading OPEN). H1 says 'elevated uncertainty language' only. ('unmanaged' allowed ONLY in 2.1 P6's not-market-crafted sense.)",
   "P2.2 (thewissen): cut to ONE-CLAUSE callback -- 2.1 P6 already drew the managed-tone contrast; do NOT re-cite the 15%.",
   "P4.2 (keown): DROP from P4 -- redundant w/ 2.1 P6 AND misplaced (keown=anticipation; P4=resolution clocks)."
 ],
 "2.3_QUEUED": [
   "P3.2 FirmChars 'bad control': CUT (I added it; NOT roadmap-mandated; sign a-priori indeterminate; calling DWZ's adopted controls 'bad' scrutinizes an established spec we ADOPT).",
   "P3.1 UncPre over-control: KEEP, retone SUGGESTIVE (roadmap-mandated; tab:h23 UncPre->UncRes 0.0111**/0.0230**; frame as 'a property of repurposing DWZ's residual for an anticipatory question', NOT 'DWZ over-controlled').",
   "P4 generated-regressand: KEEP, retone suggestive (standard 2-step property + DWZ's own eq-5 use; not a DWZ critique)."
 ]
}

d["NEXT_ACTION"] = (
"===CURRENT (2026-06-13): 2.5 yardstick definitions NLM-VERIFIED; 2.5 reframe + 2.2/2.3 fixes DECIDED but UNAPPLIED.=== "
"STEP 1 (do next, user-approved): fold the verified material into section2.5_paragraph_ledger.json -- per-paragraph, programmatic, reversible -- "
"per PENDING_EDITS_unapplied['2.5_DO_NOW'] (content-location reframe + yardstick definitions + foreground CashScrutiny). Then advisor-check. "
"STEP 2: apply PENDING_EDITS_unapplied['2.2_QUEUED'] + ['2.3_QUEUED'] (user chose KEEP QUEUED -- at the ratification pass, NOT bundled with 2.5). "
"STEP 3: user ratifies all four ledgers. STEP 4 (after ratification, ONE PARAGRAPH AT A TIME, order 2.2->2.5, per paragraph_workflow.json): "
"per paragraph -> verify props -> draft prose -> accuracy-pass uncited claims -> advisor -> show user -> record final_prose + unlock prose_gate. "
"STILL-OWED NLM at write-time (NOT done): pagan1984 (2.3 generated-regressand); opler1999/bates2009/petersen2009/cameron2011 (2.4). "
"(hoberg2010/2016, hassan2020, baker2016, davis2016 are now VERIFIED -- see validity_yardsticks_VERIFIED_2026_06_13 -- no longer owed.) "
"BIBLE CROSS-CHECK owed: C3/C4/C5 numbers vs _tables_from_bible.tex. R-class reruns: drop-FirmChars robustness (2.3), two-way clustering (R2). "
"DISCIPLINE: 2.2/2.3 stay queued; no prose before ratification; transfer to ledgers PROGRAMMATICALLY."
)

d["files_of_record"]["nlm_query_guide"] = (
"docs/Thesis/rewrite/NLM_QUERY_GUIDE.md -- REWRITTEN 2026-06-13. READ FIRST before ANY NLM work. "
"Key: sec4 IDENTITY (a filename is NEVER the paper; confirm via NLM, never decode), sec3a CONTENT-DISCOVERY (unscoped clear+ask names paper "
"-> references.source_id; '--new' is NOT a real flag in this build), sec3 registry shapes + fail-closed, engine/modes, planning-tmp, "
"content-scoping caveats, ledger shape, GATING-vs-NON-GATING + provisional verdicts."
)
d["files_of_record"]["nlm_validity_tool"] = (
"docs/Thesis/rewrite/nlm_validity_defs.py -- content-discovery extractor for the 2.5 yardsticks (imports nlm_common). "
"Modes: default run_queries (unscoped discover+capture), --davis (scoped confirm of w22740), --requery (scoped clean-span requeries), --show. "
"Writes tmp/nlm_validity_definitions.json."
)
d["files_of_record"]["nlm_validity_evidence"] = "tmp/nlm_validity_definitions.json -- VERIFIED yardstick definitions + verbatim spans (committed). Source of truth for the 2.5 fold."

json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(p, encoding="utf-8"))  # re-parse to validate
print("resume updated + re-parse OK")
