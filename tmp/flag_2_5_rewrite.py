# Record the user's 4 rewrite directives for 2.5 (2026-06-14, from PDF review). Flags only -- the rewrite executes next.
import json
LED = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
RES = "docs/Thesis/rewrite/_RESUME_STATE.json"
CF  = "docs/Thesis/rewrite/claim_findings_ledger.json"

flags = {
  "_what": "User directives 2026-06-14 (emphatic, from PDF). These OVERRIDE prior 2.5 framing where they conflict. Rewrite 2.5 to satisfy ALL FOUR, then re-push.",
  "FA_DROP_COMPETITION_completely": ("DROP the discriminant / competition test (P3) COMPLETELY from 2.5. Reason: the 'known/disclosable -> "
    "prepared remarks -> presentation' rationale is BROKEN (PRisk and EPU are also disclosable; PRisk is measured from the SAME earnings call). "
    "Remove P3, the hoberg2016 usage in 2.5, and rewrite P1 (no longer 'two demands' -- discriminant is gone). CONSEQUENCE (flagged for user): the "
    "validity case then rests on convergent (P2) + the scrutiny rule-out (P4) + the 2.3 net-of-controls conservative floor. This drops what "
    "claim_findings called C3 'the single cleanest validity result' -- per explicit user instruction."),
  "FB_report_ECONOMIC_effect": ("P2 must report the ECONOMIC magnitude for each convergent measure: a one-standard-deviation increase in PRisk / "
    "US-EPU / GEPU raises UncRes by X (express in UncRes standard deviations or % of its SD). COMPUTE at write-time from the bible / variable_ledger "
    "SDs -- do NOT fabricate. This replaces the vague 'economically trivial' with an actual number per measure."),
  "FC_CashScrutiny_words_to_APPENDIX": ("Disclose the CashScrutiny cash/liquidity WORD LIST (the dictionary that flags cash-topic Q&A turns) in an "
    "APPENDIX; P4 forward-references it. Source = the cash-topic scorer (scripts/gen_empire_did_table.py / tmp/_cash_stock_score_call.parquet pipeline); "
    "transcribe the actual word list from code at write-time (no memory)."),
  "FD_LANGUAGE_lead_with_SIGNIFICANCE": ("P2 LANGUAGE SHIFT (emphatic): LEAD with 'the residual is significantly and positively associated with all "
    "three established uncertainty measures (PRisk, US-EPU, GEPU), at varying significance levels.' STOP leading with 'weak / supportive-not-decisive / "
    "consistent-with / economically trivial'. KEEP the honest qualifiers (the tests are one-tailed; the per-measure economic magnitudes from FB) but make "
    "them SECONDARY, not the headline. NOTE: this OVERRIDES the locked claim_findings C5 ('consistent with', 'demote convergent', 'lean on discriminant') "
    "-> claim_findings C5 flagged for update. Honesty guard: the lead must still carry the 'one-tailed' qualifier (some go n.s. two-tailed).")
}

d = json.load(open(LED, encoding="utf-8"))
d["PENDING_REWRITE_FLAGS_2026_06_14"] = flags
d["paragraphs"]["P3"]["prose_status"] = "FLAGGED FOR DROP 2026-06-14 (user: drop the competition/discriminant test completely; see PENDING_REWRITE_FLAGS_2026_06_14.FA)"
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))

r = json.load(open(RES, encoding="utf-8"))
r["prose_progress_2026_06_13"]["status"]["2.5 (whole)"] = ("PUSHED to PDF but NOT ratified; user returned 4 REWRITE FLAGS 2026-06-14 "
  "(section2.5 ledger PENDING_REWRITE_FLAGS_2026_06_14): FA drop competition/P3 completely; FB report economic effect (1-SD -> X); "
  "FC CashScrutiny word list to Appendix; FD language LEAD with 'significantly associated' (stop over-hedging the 3 convergent results), keep one-tailed "
  "+ magnitude as secondary. -> REWRITE 2.5, re-push.")
r["NEXT_ACTION"] = ("=== REWRITE 2.5 per section2.5 ledger PENDING_REWRITE_FLAGS_2026_06_14 (FA drop P3 competition; FB economic effect [compute 1-SD "
  "from bible/variable_ledger SDs]; FC CashScrutiny word list -> Appendix [transcribe from code]; FD P2 lead with significant association, keep "
  "one-tailed+magnitude secondary). Update P1 (discriminant gone). Then re-record -> re-push(replace) -> recompile -> user re-reads 2.5. Also update "
  "claim_findings C5 (override the 'consistent with/demote convergent/lean on discriminant' framing). 2.2 ratified+committed; 2.3/2.4 still awaiting "
  "ratification. After 2.5 settled + 2.3/2.4 ratified -> whole-§2 pass + 2.1-P7 softening. DISCIPLINE: programmatic transfer w/ asserts; numbers "
  "bible-verbatim; SHOW/ratify in PDF; no '---'/'--'.")
open(RES, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
json.load(open(RES, encoding="utf-8"))

c = json.load(open(CF, encoding="utf-8"))
c["_USER_OVERRIDE_2026_06_14"] = ("C3 (discriminant/competition) and C5 (convergent) framing OVERRIDDEN by user from PDF review: DROP the "
  "competition/discriminant test entirely (C3 no longer used in 2.5); and 2.5 must LEAD with the SIGNIFICANT positive association of the residual with "
  "PRisk/US-EPU/GEPU (all significant, varying levels), with one-tailed + economic-magnitude as secondary caveats -- NOT lead with 'consistent with/weak'. "
  "Update C5 thinnest_claim accordingly at the 2.5 rewrite. (Recorded as a flag; C5/C3 numbers unchanged.)")
open(CF, "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
json.load(open(CF, encoding="utf-8"))
print("recorded 4 rewrite flags -> 2.5 ledger + resume + claim_findings override note. P3 marked FOR DROP.")
