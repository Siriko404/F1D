# Apply the decided 2.3_QUEUED edits to section2.3_paragraph_ledger.json (programmatic, reversible).
# Edits: CUT P3.2 (FirmChars bad-control) + renumber P3.3->P3.2; retone P3.1 (UncPre) + P4.1 (generated-regressand)
# to SUGGESTIVE-not-scrutinizing (we ADOPT DWZ's spec; never label it 'bad'/'over-controlled').
import json

p = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
P = d["paragraphs"]

def prop(par, pid):
    for x in par["propositions"]:
        if x["prop_id"] == pid:
            return x
    raise KeyError(pid)

# --- _plan: drop FirmChars from spine / thin_claim / division_of_labor ---
pl = d["_plan"]
pl["spine"] = ("P1 measure (LM share, UncAns eq-2) -> P2 decomposition (eq-4 -> UncRes; why residual; operationalizes P4) "
    "-> P3 control-set note (UncPre over-control; residual net of UncQue/NegCall) -> P4 generated-regressand.")
pl["thin_claim"] = ("Disclose the generated-regressand and the UncPre-control tension HONESTLY but in a SUGGESTIVE register "
    "(never scrutinizing -- we adopt DWZ's spec): frame UncPre as a property of repurposing DWZ's residual for an "
    "anticipatory question; note the residual is net of UncQue/NegCall; validity is an empirical question answered in 2.5.")
pl["division_of_labor"] = ("2.1 P4 located the signal in the call-varying residual (conceptually, no equation) and deferred "
    "isolation to 'the design that follows'. 2.3 ADDS: the formal eq-4 + regressors, and the two honest threats (UncPre "
    "over-control, generated-regressand). It does NOT re-argue the locating logic (COH-4).")

# --- P3: cut FirmChars; retone to suggestive ---
P["P3"]["lit_body"] = "control-set note: UncPre over-control (C3); residual net of UncQue/NegCall"
P["P3"]["intent"] = ("Own the UncPre over-control tension HONESTLY but SUGGESTIVELY (not scrutinizing): it is a property of "
    "repurposing DWZ's residual for an anticipatory question. Note the residual is already net of UncQue/NegCall.")
P["P3"]["thin_claim"] = ("Suggestive, not scrutinizing: surface the UncPre-control tension as a repurposing property, NEVER as "
    "'DWZ over-controlled'; note the residual is net of UncQue/NegCall.")
P["P3"]["guardrails"] = [
    "Numbers bible-verbatim only (claim_findings_ledger C3).",
    "RULE-COH-8: state the residual is net of UncQue + NegCall (grounds 2.2 P5.3 / 2.5.4).",
    "No cause.",
    "TONE = suggestive, NOT scrutinizing: frame UncPre as a property of REPURPOSING DWZ's residual for an anticipatory question, never 'DWZ over-controlled'.",
    "FirmChars 'bad-control' CUT 2026-06-13 (user): we ADOPT DWZ's spec -> do not label its controls 'bad'; the drop-FirmChars rerun, if run, is a robustness column, not a 2.3 threat."
]

# retone P3.1 (UncPre)
p31 = prop(P["P3"], "P3.1")
p31["statement"] = ("UncPreCEO is an eq-4 control, yet prepared-remarks uncertainty itself carries signal (shown in 4.2) and "
    "the UncPre->UncRes association is significant (0.0111**/0.0230**, tab:h23). This is a property of REPURPOSING DWZ's "
    "residual for an anticipatory question: prepared remarks are drafted and vetted in advance, so the residual deliberately "
    "isolates the live-Q&A shock. We note robustness to dropping UncPre and/or disclose it -- suggestively, not as a critique "
    "of DWZ's adopted spec.")
p31["verification_plan"] = ("Numbers bible-verbatim (claim ledger C3). Reconciliation = write-time, SUGGESTIVE register "
    "(repurposing property, not 'DWZ over-controlled'). UncPre in-eq-4 confirmed from the NLM-verified control set (Q3).")

# CUT P3.2 (FirmChars), renumber P3.3 -> P3.2
P["P3"]["propositions"] = [x for x in P["P3"]["propositions"] if x["prop_id"] != "P3.2"]
for x in P["P3"]["propositions"]:
    if x["prop_id"] == "P3.3":
        x["prop_id"] = "P3.2"

# --- P4: retone generated-regressand suggestive ---
P["P4"]["intent"] = ("Note the generated-regressand property SUGGESTIVELY: UncResCEO is a first-stage residual used as the "
    "downstream DV -- a standard two-step setting (DWZ themselves use UncRes as a regressor), not a flaw unique to this paper.")
P["P4"]["thin_claim"] = "State why inference holds or flag the two-step-SE concern -- suggestive, not scrutinizing; do not hand-wave."
p41 = prop(P["P4"], "P4.1")
p41["statement"] = ("UncResCEO is a generated regressand -- a first-stage residual used as the downstream dependent variable -- "
    "a standard two-step setting (DWZ themselves use UncRes as a regressor in their Eq(5)), so conventional standard errors may "
    "be understated without a two-step correction. We note this property and either argue inference is unaffected or flag the "
    "two-step-SE concern (and the bootstrap remedy) -- suggestively, not as a critique.")
p41["verification_plan"] = ("Cross-cutting risk R3 (claim ledger). pagan1984 cite VERIFIED at write-time (post-ratification "
    "upload). Argument/remedy decided at write-time, SUGGESTIVE register (standard two-step property + DWZ's own Eq(5) use).")

# papers: mark keown1981 dropped from 2.3 (FirmChars cut)
if "keown1981" in d.get("papers", {}):
    d["papers"]["keown1981"]["status_2_3"] = "DROPPED from 2.3 plan (FirmChars P3.2 cut 2026-06-13); remains a 2.1 P6 callback."

d["next_action"] = ("2.3 QUEUED EDITS APPLIED 2026-06-13 (de-queued per user 'revise planning to 100% complete'): "
    "P3.2 FirmChars bad-control CUT (we adopt DWZ's spec; don't scrutinize) + P3.3->P3.2 renumber; P3.1 UncPre + P4.1 "
    "generated-regressand RETONED suggestive (repurposing property / standard two-step, NOT a DWZ critique). Plan now FINAL "
    "for every 2.3 paragraph. Status PLANNED, prose BLOCKED, NOT ratified. " + d["next_action"])

json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(p, encoding="utf-8"))
print("2.3 revised: P3.2(FirmChars) cut + renumbered, P3.1/P4.1 retoned suggestive; re-parse OK; P3 props ->",
      [x["prop_id"] for x in P["P3"]["propositions"]])
