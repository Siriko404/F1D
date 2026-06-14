# Advisor-mandated SWEEP: propagate the scrutiny reframe to every hit the targeted edit missed.
# Fixes (1) the dangling 2.3->2.2 P5.3 ref, (2) the non-redundancy claim's missing home (add 2.5 P4.4),
# (3) 2.5 P1 + subsection_plan SC2.5.1 still calling scrutiny a 'confound/artifact', (4) residual labels.
# Roadmap + claim_findings_ledger C4 are DEFERRED (non-deliverable) -> separate before-prose touch.
import json
REW = "docs/Thesis/rewrite/"
def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d): open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
def chk(got, exp, where):
    assert got == exp, f"DRIFT at {where}:\n  GOT: {got!r}\n  EXP: {exp!r}"
def sub(s, old, new, where):
    assert old in s, f"SUBSTRING MISSING at {where}: {old!r}"
    return s.replace(old, new)
def repl_item(lst, old, new, where):
    assert old in lst, f"LIST ITEM MISSING at {where}: {old!r}"
    return [new if x == old else x for x in lst]

# ===================== 2.3 (ratified) -- integrity ref-fix + framing word =====================
f23 = REW + "section2.3_paragraph_ledger.json"
d = load(f23)
p25 = d["paragraphs"]["P2"]["propositions"]
assert p25[4]["prop_id"] == "P2.5", "2.3 P2.5 id"
p25[4]["statement"] = sub(p25[4]["statement"], "grounds the scrutiny/tone reconciliation in 2.2 P5.3 and 2.5.",
    "grounds the scrutiny/tone reconciliation in 2.5 P4 (P4.4).", "2.3 P2.5 dangling ref")
p32 = d["paragraphs"]["P3"]["propositions"]
assert p32[1]["prop_id"] == "P3.2", "2.3 P3.2 id"
p32[1]["statement"] = sub(p32[1]["statement"], "real uncertainty and is not a scrutiny artifact",
    "real uncertainty and is not merely a reflection of analyst scrutiny", "2.3 P3.2 artifact")
d["next_action"] = ("[2026-06-13 scrutiny-reframe sweep] integrity fix only: P2.5 ref re-pointed 2.2 P5.3 -> 2.5 P4.4 "
    "(2.2 P5.3 was dropped); P3.2 'scrutiny artifact' -> 'merely analyst scrutiny'. No content change; 2.3 stays RATIFIED. "
    + d["next_action"])
save(f23, d)
print("2.3: dangling ref -> 2.5 P4.4; P3.2 'artifact' reworded. (integrity)")

# ===================== 2.5 -- propagate the reframe + ADD P4.4 (restore non-redundancy) =====================
f25 = REW + "section2.5_paragraph_ledger.json"
d = load(f25)
chk(d["_plan"]["division_of_labor"], "Mostly NEW -- validity is work 2.1 does not do. Presentation/Q&A split = CALLBACK P2. Scrutiny construct = definitional counterpart to the 2.2 P5 hypothesis.", "2.5 div_of_labor")
d["_plan"]["division_of_labor"] = ("Mostly NEW -- validity is work 2.1 does not do. Presentation/Q&A split = CALLBACK P2. "
    "Scrutiny: 2.5 P4 OWNS the construct + the identification motivation (validity table as ground); 2.2 P5 only FLAGS the rival.")

P1 = d["paragraphs"]["P1"]
chk(P1["intent"], "State the two demands the residual must meet before results are trusted: it must move with real uncertainty (convergent) and not be a scrutiny artifact (discriminant + rule-out).", "2.5 P1.intent")
P1["intent"] = ("State the two demands before results are trusted: the residual must (a) move with real uncertainty (convergent) and "
    "(b) be distinct from competing observable channels (discriminant) -- product-market competition (P3), and not merely analyst "
    "scrutiny, a plausible alternative driver tested & rejected as a side analysis (P4 -> 4.1).")
chk(P1["propositions"][0]["statement"], "The residual UncResCEO must satisfy two demands to be a credible measure: (a) convergent -- it moves with established uncertainty constructs; (b) discriminant -- it does not merely capture a confound such as analyst scrutiny.", "2.5 P1.1")
P1["propositions"][0]["statement"] = ("The residual UncResCEO must satisfy two demands to be credible: (a) convergent -- it moves with "
    "established uncertainty constructs; (b) discriminant -- it is distinct from competing observable channels (product-market "
    "competition, P3) and is not merely driven by analyst scrutiny -- a plausible alternative driver we test, and reject, as a side "
    "analysis (P4 -> 4.1).")

P4 = d["paragraphs"]["P4"]
chk(P4["lit_body"], "pre-register the analyst-scrutiny rule-out (forward to 4.1)", "2.5 P4.lit_body")
P4["lit_body"] = "introduce + motivate the analyst-scrutiny identification side-test (construct here; verdict in 4.1)"
P4["guardrails"][4] = sub(P4["guardrails"][4], "the confound IS real (rises pre-announce) but only the underpowered gating test rejects it.",
    "scrutiny genuinely DOES rise pre-announce (which is what makes it a plausible driver), but only the underpowered gating test rejects it.", "2.5 P4 guardrail confound")

# ADD P4.4 -- restores the dropped 2.2 P5.3 non-redundancy claim in its proper home; 2.3 P2.5 now points here.
assert [p["prop_id"] for p in P4["propositions"]] == ["P4.1", "P4.2", "P4.3"], "2.5 P4 prop ids pre-add"
P4["propositions"].append({
    "prop_id": "P4.4",
    "statement": ("CashScrutiny measures the VOLUME/topic of cash questions, distinct from analyst-question uncertainty WORDS (UncQue), "
        "which the residual already nets out by construction (eq-4). So this alternative-driver test targets the question-VOLUME path that "
        "eq-4 does not absorb -- it is non-redundant with the controls already inside the residual (referee-proofing; RULE-COH-8)."),
    "role_in_paragraph": "Non-redundancy: why the scrutiny side-test still bites although eq-4 already controls UncQue (restores the dropped 2.2 P5.3 claim; 2.3 P2.5 points here).",
    "type": "framing-nonverifiable",
    "relation_to_2_1": "NEW",
    "anchor_2_1": [],
    "verification_plan": "Framing; RULE-COH-8; rests on the NLM-verified eq-4 control set (tmp/nlm_dwz_equations.json). CashScrutiny = volume confirmed gen_empire_did_table.py:73. No NLM.",
    "status": "PLANNED"
})
d["next_action"] = "[sweep] 2.5 P1/P1.1 + div_of_labor reframed (confound/artifact -> competing channel / plausible driver); P4 lit_body + guardrail reworded; ADDED P4.4 (non-redundancy, restores dropped 2.2 P5.3; 2.3 P2.5 points here). " + d["next_action"]
save(f25, d)
print("2.5: P1/P1.1/div_of_labor reframed; P4 lit_body+guardrail; ADDED P4.4 non-redundancy.")

# ===================== 2.2 -- residual COH-5 label + P5.1 role =====================
f22 = REW + "section2.2_paragraph_ledger.json"
d = load(f22)
d["_governing"]["coherence_rules_in_force"] = sub(d["_governing"]["coherence_rules_in_force"],
    "COH-5 (scrutiny = confound, not a P7 reading; rule-out != mechanism)",
    "COH-5 (scrutiny = plausible alternative driver tested & rejected in 4.1, flagged in 2.2; not a P7 reading; rejecting != mechanism)", "2.2 coh_rules")
p51 = d["paragraphs"]["P5"]["propositions"][0]
assert p51["prop_id"] == "P5.1", "2.2 P5.1 id"
chk(p51["role_in_paragraph"], "States the rival to be ruled out.", "2.2 P5.1 role")
p51["role_in_paragraph"] = "States the rival (a plausible alternative driver, tested & rejected as a side analysis in 4.1)."
save(f22, d)
print("2.2: COH-5 label + P5.1 role reframed.")

# ===================== subsection_plan -- 2.5 purpose/serves/constraints/SC claims/map + 2.2 constraint =====================
fsp = "tmp/section2_subsection_plan.json"
d = load(fsp)
s25 = d["2.5"]
chk(s25["purpose"], "Validate the construct (convergent + discriminant) and pre-empt the scrutiny confound -- earn trust the residual measures what's claimed BEFORE results.", "sp 2.5 purpose")
s25["purpose"] = ("Validate the construct (convergent + discriminant) and MOTIVATE the scrutiny identification side-test "
    "(our measure -> plausible alternative driver -> tested & rejected in 4.1) -- earn trust the residual measures what's claimed BEFORE results.")
chk(s25["serves"], "Construct credibility; pre-registers the 4.1 scrutiny rule-out; defines remaining key constructs.", "sp 2.5 serves")
s25["serves"] = "Construct credibility; introduces + motivates the scrutiny identification side-test (verdict in 4.1); defines remaining key constructs."
s25["register_constraints"] = repl_item(s25["register_constraints"], "RULE-COH-5 (scrutiny construct; rule-out != mechanism)",
    "RULE-COH-5 (scrutiny = plausible alternative driver tested & rejected; rejecting != mechanism)", "sp 2.5 reg_constraints")
chk(s25["subsection_prop_chain"][0]["claim"], "Two demands on the residual: it must (a) move with real uncertainty (convergent), and (b) not be a scrutiny artifact (discriminant + rule-out).", "sp SC2.5.1")
s25["subsection_prop_chain"][0]["claim"] = ("Two demands on the residual: (a) move with real uncertainty (convergent), and (b) be distinct "
    "from competing observable channels (discriminant) -- competition (SC2.5.3), and not merely analyst scrutiny, a plausible alternative "
    "driver tested & rejected as a side analysis (SC2.5.4 -> 4.1).")
chk(s25["subsection_prop_chain"][3]["claim"], "Pre-register the scrutiny rule-out (4.1 forward-ref): define CashScrutiny / HighCashScrutiny + the three-step logic; frame as 'doesn't account for THIS run-up.'", "sp SC2.5.4")
s25["subsection_prop_chain"][3]["claim"] = ("Introduce + MOTIVATE the scrutiny identification side-test: define CashScrutiny / HighCashScrutiny, "
    "establish its validity (CashRatio->CashScrutiny) + plausibility (rises around cash deals), and pre-register the side-test (verdict in 4.1); "
    "frame the verdict as 'doesn't account for THIS run-up.'")
s25["paragraph_map_provisional"] = sub(s25["paragraph_map_provisional"], "P4 scrutiny-rule-out(SC2.5.4)", "P4 scrutiny motivation + side-test(SC2.5.4)", "sp 2.5 para_map")
d["2.2"]["register_constraints"] = repl_item(d["2.2"]["register_constraints"], "RULE-COH-5 (scrutiny is a confound)",
    "RULE-COH-5 (scrutiny is a plausible alternative driver, flagged in 2.2)", "sp 2.2 reg_constraints")
save(fsp, d)
print("subsection_plan: 2.5 purpose/serves/constraints/SC2.5.1/SC2.5.4/map + 2.2 constraint reframed.")

for p in (f23, f25, f22, fsp): load(p)
print("OK -- all four files re-parse clean.")
