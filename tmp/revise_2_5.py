# Apply ALL decided 2.5 edits to section2.5_paragraph_ledger.json (programmatic, reversible).
# F1 content-location reframe (kill 'persistent'); fold the 4 NLM-verified yardstick defs; foreground CashScrutiny;
# audit F2 (flag-not-drop hoberg2010/fluidity), F3 (time-varying strengthens P3.3), F4 (convergent identification basis),
# F5 (Hassan cite-year flag). Evidence: tmp/nlm_validity_definitions.json + variable_ledger h11/h23/h24/h24b.
import json

p = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
P = d["paragraphs"]

def prop(par, pid):
    for x in par["propositions"]:
        if x["prop_id"] == pid:
            return x
    raise KeyError(pid)

# --- _governing.hard_rules: the 'NOT verified' bullet is now stale ---
d["_governing"]["hard_rules"][2] = ("Validity yardsticks VERIFIED via NLM 2026-06-13 (tmp/nlm_validity_definitions.json): "
    "hassan2020 (PRisk), baker2016 (US-EPU), hoberg2016 (TNIC total similarity = competition) LOCKED; davis2016 (GEPU) "
    "PROVISIONAL (fold as-is). STILL UNVERIFIED -> write-time flag: hoberg2010 + the word 'fluidity' (our variable is total "
    "similarity, NOT fluidity).")

# --- _plan.validity_papers_status ---
d["_plan"]["validity_papers_status"] = ("hassan2020 (PRisk), baker2016 (US-EPU), hoberg2016 (TNIC total similarity = "
    "competition) VERIFIED via NLM 2026-06-13 (LOCKED); davis2016 (GEPU) VERIFIED PROVISIONAL (fold as-is) -- all in "
    "tmp/nlm_validity_definitions.json. hoberg2010 + the word 'fluidity' STILL UNVERIFIED -> write-time NLM flag (F2); our "
    "competition variable is z_log_TotalSimilarity = total similarity (hoberg2016), NOT fluidity. F5: variable_ledger cites "
    "'Hassan et al. 2019' (WP) vs QJE 2020 -> reconcile cite year vs .bib at write-time. Regression NUMBERS bible-verbatim "
    "(C3/C4/C5; bible cross-check at write-time).")

# --- papers block: statuses -> verified ---
pap = d["papers"]
pap["hassan2020"]["status"] = ("VERIFIED 2026-06-13 (LOCKED, tmp/nlm_validity_definitions.json). PRisk = weighted share of a "
    "firm's QUARTERLY earnings call devoted to political risk, capped 99th pct + standardized; firm-quarter; 'proxy for the "
    "political risk AND uncertainty individual firms face' (Hassan, Hollander, van Lent, Tahoun, QJE; NLM source qjz021). Role: "
    "convergent (firm-level -> cleanest unit match to UncRes). F5: variable_ledger says 'Hassan et al. 2019' (WP) vs QJE 2020 "
    "-> reconcile cite year at write-time.")
pap["baker2016"]["status"] = ("VERIFIED 2026-06-13 (LOCKED). US-EPU = newspaper-frequency index (trio: economy + uncertainty + "
    "policy terms), 10 US papers, MONTHLY, US national; 'proxies for movements in policy-related economic uncertainty' (Baker, "
    "Bloom, Davis, QJE; NLM source qjw024). Role: convergent (macro -> weak).")
pap["davis2016"]["status"] = ("VERIFIED 2026-06-13 (PROVISIONAL per guide sec9 -- def answer-located + identity self-confirmed; "
    "acceptable, FOLD AS-IS, do not re-query). GEPU = GDP-weighted average of national EPU indices for 16 countries (~2/3 of "
    "global output), MONTHLY (Davis, NBER WP 22740; NLM source w22740). Role: convergent (global macro -> weakest).")
pap["hoberg2016"]["status"] = ("VERIFIED 2026-06-13 (LOCKED). = TNIC3 total similarity = sum of pairwise text-based "
    "product-market similarity to all rivals in the given year = our z_log_TotalSimilarity (variable_ledger); higher = more "
    "competition. TIME-VARYING firm-year (Hoberg verbatim: 'Because firms update their 10-Ks annually, Mt is time varying'; "
    "'classifications that change over time'). Role: discriminant (LEAD). Hoberg & Phillips, JPE; NLM source 688176.pdf.")
pap["hoberg2010"]["status"] = ("NOT verified (absent from the NLM yardstick evidence). Candidate cite for 'competition/"
    "fluidity'. F2 (advisor): our variable is total similarity (= hoberg2016), NOT fluidity -> do NOT assert-drop from memory; "
    "FLAG for write-time NLM-verify (alongside pagan/opler). May be dropped at write-time if it does not match our variable.")

# --- P2 convergent: fold verified defs + identification basis (F4) ---
P["P2"]["intent"] = ("Show the residual is 'consistent with' established uncertainty measures -- honestly hedged (one-tailed; "
    "PRisk firm-quarter but economically trivial; US-EPU/GEPU = aggregate macro co-movement, marginal).")
P["P2"]["guardrails"] = [
    "Keep 'consistent with' VERBATIM (C5).",
    "Numbers bible-verbatim (bible cross-check at write-time).",
    "hassan2020/baker2016/davis2016 VERIFIED 2026-06-13 (tmp/nlm_validity_definitions.json) -- davis2016 provisional, fold as-is.",
    ("IDENTIFICATION BASIS (F4, the validity justification the user mandated): PRisk = firm-quarter (h11 Year FE -> within-year "
     "FIRM-LEVEL variation, cleanest match to UncRes); US-EPU/GEPU = MACRO monthly index matched to quarter (h24/h24b Cal-Year FE "
     "+ two-way cluster -> within-year AGGREGATE co-movement, every firm one value per period, weakest).")
]
p2_1 = prop(P["P2"], "P2.1")
p2_1["verification_plan"] = ("Numbers bible-verbatim (bible cross-check at write-time). Benchmarks VERIFIED 2026-06-13 "
    "(tmp/nlm_validity_definitions.json): PRisk = firm-quarter weighted share of the earnings call on political risk, "
    "standardized, a proxy for 'political risk AND uncertainty' (hassan2020 QJE); US-EPU = monthly US newspaper-frequency "
    "policy-uncertainty index (baker2016 QJE); GEPU = monthly GDP-weighted 16-country EPU (davis2016, provisional). Carry each as "
    "a one-clause 'what+whose'.")
p2_2 = prop(P["P2"], "P2.2")
p2_2["statement"] = ("This is reported as 'consistent with' established measures, not as establishing the construct: the tests "
    "are one-tailed; PRisk (firm-quarter, the cleanest unit match to UncRes) is economically trivial; and US-EPU/GEPU are MACRO "
    "monthly indices -- every firm shares one value per period, entering under calendar-year FE, so they are identified only off "
    "WITHIN-YEAR AGGREGATE co-movement (an aggregate co-movement check, not a firm-level one). The convergent leg is supportive but weak.")
p2_2["verification_plan"] = ("Hedge ('consistent with') VERBATIM from C5. Identification basis from variable_ledger h11 (Year FE) "
    "/ h24-h24b (Cal-Year FE + two-way cluster) = the validity justification (F4). Bible cross-check the numbers at write-time.")

# --- P3 discriminant: F1 content-location reframe (kill 'persistent') + F3 strengthening ---
P["P3"]["intent"] = ("Lead with the decisive validity result: a (time-varying) product-market competition measure surfaces in "
    "the scripted presentation -- where the firm narrates its competitive landscape -- but NOT in the call-varying residual the design uses.")
P["P3"]["guardrails"] = [
    "Numbers bible-verbatim (C3).",
    ("hoberg2016 VERIFIED 2026-06-13 = TNIC3 total similarity (sum of pairwise text-based product-market similarity to all rivals, "
     "given year) = our z_log_TotalSimilarity = competition; TIME-VARYING firm-year (Hoberg verbatim: 'the network is time varying'). "
     "hoberg2010 + 'fluidity' UNVERIFIED -> write-time NLM flag (F2); our variable is total similarity, NOT fluidity -- do not "
     "assert-drop, park alongside pagan/opler."),
    ("F1 REFRAME: NEVER call competition a 'persistent industry trait/condition' (contradicts the verified time-varying TNIC). "
     "Frame as CONTENT-LOCATION: a standing, describable competitive condition the firm narrates in prepared remarks, vs the "
     "unscripted call-specific residual. The discriminant CLAIM rides the regression result + the time-varying property; the "
     "'why' = ONE hedged interpretive clause."),
    ("CONSTRUCTION (advisor-resolved, P3.3): the near-zero is NOT an artifact -- competition is not an eq-4 control; the test "
     "sample is one where UncRes is not mechanically orthogonal to UncPre (in-table UncPre->UncRes 0.0111**); AND competition is "
     "time-varying firm-year so firm FE does not absorb it (F3). Frame as a genuine discriminant result; do NOT write 'partly "
     "expected by construction'."),
    "RULE-COH boundary (subtlest in S2): this is VALIDITY (presentation vs residual LOCUS), distinct from the 4.2 two-audiences RESULT -- never blur them."
]
p3_1 = prop(P["P3"], "P3.1")
p3_1["verification_plan"] = ("Numbers bible-verbatim. hoberg2016 VERIFIED = TNIC3 total similarity = competition, time-varying "
    "firm-year (tmp/nlm_validity_definitions.json). hoberg2010 + 'fluidity' = write-time NLM flag (F2); our variable is total similarity.")
p3_2 = prop(P["P3"], "P3.2")
p3_2["statement"] = ("This is the cleanest validity evidence and leads the validity story: a standing, describable competitive "
    "condition surfaces where the firm narrates its business landscape (the prepared presentation), not in the call-varying "
    "residual reserved for the unscripted, deal-specific signal. Content-location, NOT persistence -- competition (TNIC total "
    "similarity) is time-varying firm-year.")
p3_2["verification_plan"] = ("Framing; C3 = cleanest. F1 REFRAME: content-location not persistence (verified time-varying TNIC); "
    "the 'why' stays ONE hedged clause; the claim rides the regression result. Write-time pass.")
p3_3 = prop(P["P3"], "P3.3")
p3_3["statement"] = ("The near-zero competition->UncRes is a genuine discriminant result, not a construction artifact: competition "
    "is NOT an eq-4 control, and the discriminant test runs on a different, smaller sample in which UncRes is not mechanically "
    "orthogonal to the netted controls (UncPre->UncRes is itself 0.0111**/0.0230** in that very table). Moreover, because "
    "competition is time-varying firm-year (hoberg2016 verified, not firm-constant), firm fixed effects do not absorb it -- the "
    "firm-FE presentation column is estimable and significant (0.0302***) -- so the firm-FE competition->UncRes null (0.0023 n.s.) "
    "is a genuine null, not FE-absorption. Presentation uncertainty remains a related channel, noted in one honest clause; the "
    "result is supportive without claiming full independence.")
p3_3["source"]["note"] = ("competition not in eq-4 controls; UncPre->UncRes = 0.0111**/0.0230** in tab:h23 proves NON-orthogonality "
    "in that sample; AND competition is time-varying firm-year (hoberg2016 verified) -> NOT firm-constant -> firm FE does not "
    "absorb it -> firm-FE UncPre col 0.0302*** estimable -> firm-FE UncRes null genuine (F3). Both -> not an artifact (claim ledger C3 risk).")
p3_3["verification_plan"] = ("Reframed (advisor) + F3: the in-table 0.0111** proves non-orthogonality AND the verified time-varying "
    "property proves firm FE does not absorb competition -> NOT an artifact. Do not write 'partly expected by construction' "
    "(understates) nor 'fully independent' (overclaims). Write-time check: confirm tab:h23 sample != the residual-estimation sample. No NLM.")

# --- P4: foreground CashScrutiny as OUR constructed measure ---
P["P4"]["intent"] = ("FOREGROUND CashScrutiny as OUR OWN constructed measure with its own validity (CashRatio predicts it, "
    "0.7530***/0.8519***), distinct from the external yardsticks; THEN pre-register the three-step rule-out, framed as "
    "'doesn't account for THIS run-up.'")
P["P4"]["guardrails"].append("FOREGROUND CashScrutiny as our constructed measure + its validity (step-(i) CashRatio->CashScrutiny) "
    "BEFORE the rule-out chain -- not buried inside it.")

d["next_action"] = ("2.5 ALL DECIDED EDITS APPLIED 2026-06-13 (per user 'revise planning to 100% complete'): F1 content-location "
    "reframe (killed 'persistent industry trait/condition' in P3 intent + P3.2); folded the 4 NLM-verified yardstick defs "
    "(papers block + P2/P3 verification_plans); F3 time-varying strengthening into P3.3; F4 convergent identification basis into "
    "P2; foregrounded CashScrutiny (P4); F2 (hoberg2010/'fluidity' flag-not-drop) + F5 (Hassan cite-year) recorded as write-time "
    "flags. Plan now FINAL for every 2.5 paragraph. Status PLANNED, prose BLOCKED, NOT ratified. WRITE-TIME FLAGS: F2, F5, and the "
    "same 'persistent' defect in variable_ledger.json L188. " + d["next_action"])

json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(p, encoding="utf-8"))
print("2.5 revised: papers verified, P2 identification-basis (F4), P3 content-location reframe (F1)+F3, P4 foreground; re-parse OK")
