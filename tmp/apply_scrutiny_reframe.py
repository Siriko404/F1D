# Apply the user-approved SCRUTINY REFRAME to the LOCKED plans, programmatically + fail-closed.
# Reframe: scrutiny = PLAUSIBLE ALTERNATIVE DRIVER (identification threat, motivated by validity 0.7530***
# + co-movement with cash deals) -> tested as a SIDE analysis -> REJECTED in 4.1.
#   - 2.5 P4 OWNS the motivation (tables as ID ground); nulls + verdict + 0.0408** magnitude -> 4.1 only.
#   - 2.2 P5 SHRINKS to a flag (drop P5.3 volume-vs-UncQue + P5.4 matsumoto -> covered by 2.5).
#   - RULE-COH-5 (subsection_plan + the two SC register-notes) reworded confound -> plausible driver.
# Every change asserts the CURRENT value first; any mismatch aborts with no partial write.
import json

REW = "docs/Thesis/rewrite/"
def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d): open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
def chk(got, exp, where):
    assert got == exp, f"DRIFT at {where}:\n  GOT: {got!r}\n  EXP: {exp!r}"

# ============================== 2.2 ledger ==============================
f22 = REW + "section2.2_paragraph_ledger.json"
d = load(f22)
P5 = d["paragraphs"]["P5"]

chk(P5["intent"], "State the competing analyst-scrutiny reading formally as the rival 4.1 tests and rules out -- positioned as a confound, not a P7 reading, and not a mechanism claim.", "2.2 P5.intent")
P5["intent"] = ("Briefly FLAG the alternative analyst-scrutiny reading and position it -- an identification threat "
    "DEVELOPED + motivated in 2.5 P4 (our measure, its validity, why plausible) and tested & REJECTED as a side "
    "analysis in 4.1. 2.2 only flags it; it does NOT own the table-pointing motivation (advisor: no double-intro).")

chk(P5["serves"], "Gives the 4.1 rule-out a home; pairs with the 2.5.4 scrutiny construct.", "2.2 P5.serves")
P5["serves"] = "Flags the rival inside the hypothesis set; the construct + motivation live in 2.5 P4, the test/verdict in 4.1."

chk(P5["boundary"], "State the rival hypothesis only; the construct definition lives in 2.5, the test/results in 4.1; NOT a 4th estimating equation in 2.4.", "2.2 P5.boundary")
P5["boundary"] = ("FLAG the rival only (one or two clauses); the construct definition + plausibility motivation live in 2.5 P4, "
    "the test/verdict in 4.1; NOT a 4th estimating equation in 2.4. Do NOT restate the validation/run-up tables here (2.5 owns them).")

chk(P5["thin_claim"], "Real competing hypothesis (not a strawman); ruling it out does NOT establish our mechanism.", "2.2 P5.thin_claim")
P5["thin_claim"] = "A plausible alternative driver (not a strawman), tested and rejected as a side identification check; rejecting it does NOT establish our mechanism."

chk(P5["guardrails"], [
    "RULE-COH-5: scrutiny is a CONFOUND, distinct from P7's two equivalent readings; rule-out != mechanism.",
    "RULE-COH-8: scrutiny (CashScrutiny = cash-question VOLUME) is distinct from UncQue (question-language uncertainty, already an eq-4 control)."
], "2.2 P5.guardrails")
P5["guardrails"] = [
    "RULE-COH-5: scrutiny is a PLAUSIBLE ALTERNATIVE DRIVER (identification threat we test, motivated in 2.5 P4), tested & REJECTED in 4.1 -- NOT a P7 reading; rejecting it != establishing a mechanism.",
    "NO DOUBLE-INTRO (advisor): 2.2 only FLAGS the rival; the why-plausible + the tables + the construct are 2.5 P4's job. Keep 2.2 P5 lean.",
    "Verdict (the nulls + 'rejected') belongs to 4.1 -- do NOT state it as established here."
]

props = P5["propositions"]
chk([p["prop_id"] for p in props], ["P5.1", "P5.2", "P5.3", "P5.4"], "2.2 P5 prop ids")
chk(props[1]["statement"], "This scrutiny channel is a confound the 4.1 design tests and rules out; it is distinct from the two observationally-equivalent readings of 2.1 (compliance-constrained vs strategic silence), and ruling it out does not establish a mechanism.", "2.2 P5.2.statement")
props[1]["statement"] = ("This scrutiny channel is an identification threat -- developed + motivated in 2.5 P4 and tested as a side analysis "
    "in 4.1, where it is rejected; it is distinct from the two observationally-equivalent readings of 2.1 (compliance-constrained "
    "vs strategic silence), and rejecting it does not establish a mechanism.")
props[1]["role_in_paragraph"] = "Positions the rival (flag): an identification threat owned by 2.5, tested/rejected in 4.1."
# Drop P5.3 (volume-vs-UncQue -> covered by 2.5 P4.1 + RULE-COH-8 guardrail) and P5.4 (matsumoto plausibility -> 2.5 owns plausibility via our co-movements).
P5["propositions"] = [props[0], props[1]]

d["status"] = "REFRAME APPLIED 2026-06-13 -- RE-RATIFY (was RATIFIED 2026-06-13; scrutiny P5 leaned to a flag, P5.3/P5.4 dropped -> folded into 2.5)."
d["_schema"]["status"] = "RATIFIED 2026-06-13 then SCRUTINY-REFRAME APPLIED 2026-06-13 -> RE-RATIFY 2.2. Prose still BLOCKED."
d["next_action"] = ("SCRUTINY REFRAME APPLIED 2026-06-13 (user-approved + advisor): 2.2 P5 leaned to a FLAG -- P5.1 (rival reading) + "
    "P5.2 (positioned as an identification threat developed in 2.5 P4, tested/rejected in 4.1); P5.3 (volume-vs-UncQue) + P5.4 "
    "(matsumoto plausibility) DROPPED from 2.2 (covered by 2.5 P4.1 + RULE-COH-8 + the co-movement motivation; matsumoto demoted "
    "to an optional 2.1 callback). RULE-COH-5 reworded confound -> plausible alternative driver. RE-RATIFY 2.2 from the beginning, "
    "then ratify 2.5. Status: reframe applied, prose BLOCKED, NOT re-ratified.")
save(f22, d)
print("2.2: P5 leaned to flag (P5.1+P5.2); P5.3/P5.4 dropped; guardrails+plan fields reframed.")

# ============================== 2.5 ledger ==============================
f25 = REW + "section2.5_paragraph_ledger.json"
d = load(f25)
pl, gov = d["_plan"], d["_governing"]

chk(pl["section_job"], "Validate the construct (convergent + discriminant) and pre-empt the scrutiny confound -- earn trust the residual measures what's claimed BEFORE results.", "2.5 _plan.section_job")
pl["section_job"] = ("Validate the construct (convergent + discriminant) and MOTIVATE the scrutiny identification side-test "
    "(our measure -> plausible alternative driver -> tested & rejected in 4.1) -- earn trust the residual measures what's claimed BEFORE results.")

chk(pl["spine"], "P1 two demands -> P2 convergent ('consistent with', hedged) -> P3 discriminant (decisive; lead) -> P4 scrutiny rule-out pre-registration -> P5 define remaining key constructs.", "2.5 _plan.spine")
pl["spine"] = ("P1 two demands -> P2 convergent ('consistent with', hedged) -> P3 discriminant (decisive; lead) -> "
    "P4 scrutiny: our measure + why plausible (validity table as ID ground) + side-test motivation (verdict in 4.1) -> P5 define remaining key constructs.")

chk(pl["serves"], "Construct credibility; pre-registers the 4.1 scrutiny rule-out; defines key non-main constructs.", "2.5 _plan.serves")
pl["serves"] = "Construct credibility; introduces + motivates the scrutiny identification side-test (verdict in 4.1); defines key non-main constructs."

chk(gov["coherence_rules_in_force"], "RULE-COH-5 (scrutiny construct here is the definitional counterpart to the 2.2 P5 hypothesis; rule-out != mechanism), RULE-COH-8 (CashScrutiny = cash-question VOLUME, distinct from UncQue word-uncertainty -- confirmed in code, gen_empire_did_table.py:73). Boundary: scrutiny RESULTS -> 4.1; presentation-contrast RESULTS -> 4.2 (do not preview).", "2.5 _governing.coh")
gov["coherence_rules_in_force"] = ("RULE-COH-5 (scrutiny = PLAUSIBLE ALTERNATIVE DRIVER / identification threat tested & rejected in 4.1; "
    "2.5 P4 OWNS the motivation, 2.2 P5 only flags; rejecting != mechanism), RULE-COH-8 (CashScrutiny = cash-question VOLUME, distinct "
    "from UncQue word-uncertainty -- confirmed in code, gen_empire_did_table.py:73). Boundary: scrutiny VERDICT/RESULTS -> 4.1; "
    "presentation-contrast RESULTS -> 4.2 (do not preview).")

P4 = d["paragraphs"]["P4"]
chk(P4["intent"], "FOREGROUND CashScrutiny as OUR OWN constructed measure with its own validity (CashRatio predicts it, 0.7530***/0.8519***), distinct from the external yardsticks; THEN pre-register the three-step rule-out, framed as 'doesn't account for THIS run-up.'", "2.5 P4.intent")
P4["intent"] = ("Introduce CashScrutiny as OUR OWN constructed measure and MOTIVATE the identification side-test: (a) it is VALID -- "
    "CashRatio predicts it (0.7530***/0.8519***), the same validity class as the other 2.5 yardsticks; (b) it is a PLAUSIBLE alternative "
    "DRIVER -- it itself rises around cash-deal announcements -- so it could mechanically generate the run-up. We therefore test, as a "
    "SIDE analysis in 4.1, whether scrutiny (not the disclosure bind) accounts for the run-up. 2.5 owns this motivation (2.2 only flags); "
    "the REJECTION verdict is reported in 4.1, not here.")

chk(P4["serves"], "The definitional counterpart to the 2.2 P5 hypothesis; routes the test to 4.1.", "2.5 P4.serves")
P4["serves"] = "Owns the scrutiny construct + the identification motivation (validity table as ground); the 2.2 P5 flag points here; the test/verdict is 4.1."

chk(P4["thin_claim"], "Keep EXACTLY as hedged: 'does not account for THIS run-up; not that scrutiny never matters' (C4, NULL-only, underpowered).", "2.5 P4.thin_claim")
P4["thin_claim"] = ("Keep the hedge EXACTLY when stated (in 4.1): 'does not account for THIS run-up; not that scrutiny never matters' "
    "(C4, NULL-only, underpowered). In 2.5: MOTIVATE + pre-register only; do NOT assert the rejection as established here.")

chk(P4["guardrails"], [
    "RULE-COH-8: CashScrutiny = % of analyst Q&A turns on cash/liquidity (VOLUME), distinct from UncQue word-uncertainty (confirmed gen_empire_did_table.py:73).",
    "RULE-COH-5: rule-out != mechanism; this is a confound check, not one of P7's two readings.",
    "Keep C4 hedge VERBATIM; the confound IS real (HighCashScrutiny rises pre-announce) -- only the gating interaction kills it, and it is underpowered.",
    "Results -> 4.1 (do not state them as established here beyond pre-registration).",
    "FOREGROUND CashScrutiny as our constructed measure + its validity (step-(i) CashRatio->CashScrutiny) BEFORE the rule-out chain -- not buried inside it."
], "2.5 P4.guardrails")
P4["guardrails"] = [
    "RULE-COH-8: CashScrutiny = % of analyst Q&A turns on cash/liquidity (VOLUME), distinct from UncQue word-uncertainty (confirmed gen_empire_did_table.py:73).",
    "RULE-COH-5: scrutiny is a PLAUSIBLE ALTERNATIVE DRIVER (identification threat) tested & REJECTED in 4.1 -- NOT one of P7's two readings; rejecting it != establishing a mechanism.",
    "NUMBER SPLIT (advisor): 0.7530***/0.8519*** (validity) STAYS in 2.5; 'rises around cash deals' is QUALITATIVE here -- the 0.0408** magnitude + the -0.0000/-0.0056 nulls + the rejection verdict are 4.1's, NOT previewed in 2.5.",
    "BUILD home: how it's built (spec/definition) lives HERE in 2.5 (user); do not strip the deeper data-pipeline mechanics from 3.1 where every variable's mechanics sit.",
    "C4 hedge stays VERBATIM where stated (4.1); in 2.5, motivate + pre-register only -- the confound IS real (rises pre-announce) but only the underpowered gating test rejects it."
]

p4 = P4["propositions"]
chk([p["prop_id"] for p in p4], ["P4.1", "P4.2", "P4.3"], "2.5 P4 prop ids")
p4[0]["role_in_paragraph"] = "The scrutiny construct definition (the BUILD/spec home is 2.5, per user)."

chk(p4[1]["statement"], "Pre-register the three-step rule-out (executed in 4.1): (i) the measure is valid -- CashRatio predicts CashScrutiny (0.7530***/0.8519***); (ii) the channel is absent -- CashScrutiny->UncRes is null (~ -0.0000 n.s.); (iii) scrutiny does not gate the run-up -- the PreAnnounceQtr x scrutiny interaction is null (-0.0056 n.s.).", "2.5 P4.2.statement")
p4[1]["statement"] = ("Motivate the side-test: CashScrutiny is (a) VALID -- CashRatio predicts it (0.7530***/0.8519***) -- and (b) a PLAUSIBLE "
    "alternative driver -- it itself rises around cash-deal announcements. Because it co-moves with both cash and the event, it could "
    "mechanically generate the pre-announcement run-up (a textbook identification threat). We therefore test, as a side analysis in 4.1, "
    "whether scrutiny rather than the disclosure bind accounts for the run-up. (The test's null magnitudes and verdict are reported in 4.1, not previewed here.)")
p4[1]["role_in_paragraph"] = "The plausibility motivation (validity 0.7530*** + qualitative co-movement) + the pre-registered side-test."
p4[1]["verification_plan"] = ("0.7530***/0.8519*** validity bible-verbatim (C4; bible cross-check at write-time); co-movement stated QUALITATIVELY "
    "('rises around cash deals') -- the 0.0408** magnitude + the nulls live in 4.1. Framed as motivation + pre-registration. No NLM.")

chk(p4[2]["statement"], "The conclusion is hedged exactly: the rule-out shows analyst scrutiny does not account for THIS pre-announcement run-up -- NOT that scrutiny never matters. The confound is genuine (HighCashScrutiny itself rises pre-announcement, 0.0408**); only the gating interaction rules it out, and that test is underpowered (absence of evidence, not equivalence).", "2.5 P4.3.statement")
p4[2]["statement"] = ("Forward-pointer only: the side-test's verdict -- that analyst scrutiny does NOT account for THIS pre-announcement run-up "
    "(not that scrutiny never matters) -- is reported in 4.1, hedged exactly per C4 and flagged as underpowered (absence of evidence, not "
    "equivalence). 2.5 does not assert it as established.")
p4[2]["role_in_paragraph"] = "Forward-ref to the 4.1 verdict (the C4 hedge is owned and stated there)."
p4[2]["verification_plan"] = "C4 hedge VERBATIM in 4.1; 2.5 carries only the forward-ref (no nulls, no established-rejection). Write-time pass."

d["next_action"] = ("SCRUTINY REFRAME APPLIED 2026-06-13 (user-approved + advisor): P4 now MOTIVATES (our measure -> plausible alternative "
    "driver; validity 0.7530***/0.8519*** STAYS, co-movement QUALITATIVE) -> side-test -> verdict in 4.1 (the 0.0408** magnitude, the "
    "-0.0000/-0.0056 nulls, and the rejection + C4 hedge are 4.1's, NOT previewed). 2.2 P5 leaned to a flag. RE-RATIFY 2.2 first, then "
    "ratify 2.5. " + d["next_action"])
save(f25, d)
print("2.5: P4 reframed to motivation+forward-ref; nulls/verdict -> 4.1; plan fields + COH-5 updated.")

# ============================== subsection_plan RULE-COH-5 + the two SC register-notes ==============================
fsp = "tmp/section2_subsection_plan.json"
d = load(fsp)
ccr = d["coherence_pass_2_1"]["cross_cutting_rules_derived"]
chk(ccr[4], "RULE-COH-5 (scrutiny is a confound, not a P7 reading): the analyst-scrutiny channel introduced in 2.2/2.5 is a separate CONFOUND ruled out empirically in 4.1 -- it is NOT one of P7's two observationally-equivalent readings, and ruling it out does NOT establish a mechanism (P7 stays open).", "COH-5 def")
ccr[4] = ("RULE-COH-5 (scrutiny is a PLAUSIBLE ALTERNATIVE DRIVER, not a P7 reading): the analyst-scrutiny channel is a plausible "
    "alternative driver of the run-up -- an identification threat (motivated in 2.5 P4 by its validity 0.7530*** + its co-movement with "
    "cash deals) that we TEST as a side analysis and REJECT in 4.1. It is NOT one of P7's two observationally-equivalent readings, and "
    "rejecting it does NOT establish a mechanism (P7 stays open). 2.5 P4 OWNS the motivation (tables as ground); 2.2 P5 only FLAGS it.")

sc225 = d["2.2"]["subsection_prop_chain"][4]  # SC2.2.5
assert sc225["id"] == "SC2.2.5", f"SC2.2.5 id drift: {sc225['id']}"
chk(sc225["register_note"], "RULE-COH-5: this is a CONFOUND to rule out, NOT one of P7's two equivalent readings; ruling it out does NOT establish our mechanism. Spec home: stated as a hypothesis here (2.2), construct pre-registered in 2.5.4, executed in 4.1 -- it is NOT a 4th estimating equation in 2.4. RULE-COH-8: scrutiny (cash-question VOLUME) is distinct from UncQue (question uncertainty WORDS, already an eq-4 control) -> rule-out is non-redundant.", "SC2.2.5 register_note")
sc225["register_note"] = ("RULE-COH-5: a PLAUSIBLE ALTERNATIVE DRIVER (identification threat), tested & REJECTED in 4.1 -- NOT one of P7's two "
    "equivalent readings; rejecting it does NOT establish our mechanism. Homes: 2.2 P5 FLAGS it; 2.5 P4 OWNS the construct + motivation "
    "(validity 0.7530*** + co-movement); test/verdict in 4.1 -- NOT a 4th estimating equation in 2.4. RULE-COH-8: scrutiny (cash-question "
    "VOLUME) is distinct from UncQue (question uncertainty WORDS, already an eq-4 control) -> the test is non-redundant.")

sc254 = d["2.5"]["subsection_prop_chain"][3]  # SC2.5.4
assert sc254["id"] == "SC2.5.4", f"SC2.5.4 id drift: {sc254['id']}"
chk(sc254["register_note"], "RULE-COH-5: definitional counterpart to the 2.2.5 hypothesis; rule-out does NOT establish mechanism. RULE-COH-8: define CashScrutiny as cash-question VOLUME/topic, explicitly distinct from UncQue (question-language uncertainty, already netted in eq-4); note the DV is by construction net of UncQue+NegCall (strengthens, does not replace, the rule-out).", "SC2.5.4 register_note")
sc254["register_note"] = ("RULE-COH-5: 2.5 P4 OWNS the scrutiny motivation -- introduce our measure, its validity (0.7530***), and why it is a "
    "PLAUSIBLE alternative driver (co-moves with cash deals); the side-test is REJECTED in 4.1 (verdict + nulls there, not here); rejecting "
    "does NOT establish mechanism. RULE-COH-8: define CashScrutiny as cash-question VOLUME/topic, explicitly distinct from UncQue (already "
    "netted in eq-4); the DV is by construction net of UncQue+NegCall (strengthens, does not replace, the test).")
save(fsp, d)
print("subsection_plan: RULE-COH-5 + SC2.2.5 + SC2.5.4 register-notes reworded confound -> plausible driver.")

# ============================== validate all re-parse ==============================
for p in (f22, f25, fsp): load(p)
print("OK -- all three files re-parse clean.")
