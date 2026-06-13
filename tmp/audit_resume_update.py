# One-shot: ADD the 2026-06-13 NLM-conflict-audit record to _RESUME_STATE.json
# (additive only -- load/mutate/dump; does NOT touch other fields). Programmatic per no-hallucination rule.
import json

p = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(p, encoding="utf-8"))

d["nlm_conflict_audit_2026_06_13"] = {
  "_what": "Diligent ULTRATHINK cross-check of the 2.2-2.5 PLAN ledgers vs the verified NLM yardstick defs (tmp/nlm_validity_definitions.json). Advisor-reviewed + corrected. Evidence = primary-source reads: variable_ledger.json entries h11/h23/h24/h24b + z_log_TotalSimilarity/US_EPU_log/GEPU_log/PRisk, and Hoberg2016 verbatim spans.",
  "scope_result": "ALL yardstick conflicts localize to 2.5. 2.2/2.3/2.4 reference NONE of the 4 yardsticks (hassan/baker/davis/hoberg) -> CLEAN. DWZ-eq usage in 2.3/2.4 unchanged + already Catch-3-closed -> no new conflict there.",
  "F1_HARD_persistent": "2.5 P3 intent + P3.2 label competition a 'persistent industry trait/condition'. CONTRADICTED by Hoberg2016 verbatim ('the network is time varying' / 'classifications that change over time') AND our own variable_ledger L192 ('competition (TNIC) is annual'). -> content-location reframe (already in PENDING 2.5_DO_NOW). LEAK: the SAME 'persistent' defect also sits in variable_ledger.json L188 (role_in_thesis) -- outside the 2.2-2.5 plans, but prose pulls from it -> fix at write-time.",
  "F2_CITE_flag_not_drop": "2.5 papers L38 + P3 guardrails cite hoberg2010 + 'fluidity'. FIRM conclusion (primary source): our variable z_log_TotalSimilarity = Hoberg-Phillips TNIC3 total similarity = hoberg2016 JPE = COMPETITION (verified). hoberg2010 + 'fluidity' are NOT verified and NOT confirmed to match our variable -> PARK in the write-time NLM-verify bucket (alongside pagan/opler); do NOT assert-drop from memory (advisor catch: 'unverified != wrong').",
  "F3_NEW_strengthen_P3.3": "time-varying is an ASSET for the P3.3 anti-artifact argument: because competition is time-varying firm-year (NOT firm-constant), firm FE does NOT absorb it -> the firm-FE column is estimable (UncPre 0.0302*** is non-degenerate) -> competition->UncRes null (0.0023 n.s., firm FE) is a GENUINE null, not FE-absorption. Fold into P3.3 next to the existing 'competition is not an eq-4 control' point.",
  "F4_convergent_identification_basis": "Per the yardstick-validity mandate, the P2 convergent fold must carry each benchmark's UNIT + the table's IDENTIFICATION basis (evidence: variable_ledger h11/h24/h24b design blocks): (a) PRisk (h11): firm-quarter (merge gvkey,cal_q) <-> firm-quarter call DV; Year FE -> identified off WITHIN-YEAR FIRM-LEVEL PRisk variation -> CLEANEST (firm-level match). Hassan = firm-quarter, whole-call, standardized, 'political risk AND uncertainty'. (b) US-EPU (h24) + GEPU (h24b): MACRO monthly index matched to quarter; Calendar-YEAR FE + two-way cluster (firm, cal-qtr) + Lagged_DV -> annual level absorbed, coefficient identified off WITHIN-YEAR ACROSS-QUARTER AGGREGATE co-movement (every firm same value/period) -> WEAKEST -> this grounds the C5 'consistent with'/marginal hedge. Mapping CONFIRMED: baker2016=US_EPU_log (QJE), davis2016=GEPU_log (NBER WP 22740).",
  "F5_cite_year_flag": "variable_ledger L926/L930 cites 'Hassan et al. 2019'; the 2.5 ledger + the NLM-verified source (qjz021 = QJE) use 2020. WP(2019)-vs-published(2020) year split -> reconcile the cite year at write-time against the .bib; do NOT fix from memory.",
  "blocks_fold": "NO. F1 reframe + F3 strengthening are fold-ready now. F2 = soften to flag-not-drop. F4 = add the (now evidence-backed) identification-basis clauses. F5 + variable_ledger-L188 = write-time flags.",
  "advisor_note": "Advisor reviewed the audit; caught F2 (from-memory cite-drop) + F4 (asserted an internal UncRes unit I had not read). Both corrected via primary-source reads of variable_ledger h11/h24/h24b. F1 + F3 confirmed sound."
}

# Append the actionable refinements to the existing 2.5 fold list (additive; guarded).
pe = d.setdefault("PENDING_EDITS_unapplied", {})
fold = pe.setdefault("2.5_DO_NOW", [])
fold.extend([
  "AUDIT-F2 (advisor): hoberg2010 + 'fluidity' -> FLAG for write-time NLM-verify (do NOT drop from memory); the only firm cite is hoberg2016 = TNIC3 total similarity = our z_log_TotalSimilarity = competition.",
  "AUDIT-F3 (advisor): strengthen P3.3 with the time-varying -> non-FE-absorbed argument (firm-FE UncPre col 0.0302*** estimable => competition->UncRes null is a genuine null, not FE-absorption).",
  "AUDIT-F4: P2 convergent must carry the IDENTIFICATION BASIS, not just the variable def -- PRisk = firm-quarter (Year FE -> within-year firm-level, cleanest); US-EPU/GEPU = macro monthly->quarter (Cal-Year FE + two-way cluster -> within-year aggregate co-movement, weakest). This IS the yardstick-validity justification the user mandated.",
  "AUDIT-F5: reconcile Hassan cite year at write-time (variable_ledger says 2019; 2.5 ledger + NLM/QJE say 2020) vs the .bib; do NOT fix from memory.",
  "AUDIT-F1-leak: the 'persistent industry condition' defect ALSO lives in variable_ledger.json L188 (role_in_thesis) -> fix when prose draws from it (write-time)."
])

json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(p, encoding="utf-8"))  # re-parse to validate
print("audit record added + 2.5_DO_NOW extended + re-parse OK")
