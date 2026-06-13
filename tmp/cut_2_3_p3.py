# Cut 2.3 P3 (UncPre over-control threat-paragraph), fold its load-bearing content into P2 (one POSITIVE,
# advisor-corrected sentence + the net-of-UncQue/NegCall grounding), renumber P4->P3, and fix the 2.4/2.5
# cross-refs ("2.3 P4"->"2.3 P3") in the SAME edit (advisor). Programmatic, reversible.
import json

def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    json.load(open(p, encoding="utf-8"))

# ===== 2.3: cut P3, fold into P2, renumber P4->P3 =====
p23 = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
d = load(p23); P = d["paragraphs"]

# fold one POSITIVE framing prop into P2 (advisor wording: 'would' not 'must' + conservative floor + COH-8 grounding + gate)
P["P2"]["propositions"].append({
  "prop_id": "P2.5",
  "statement": ("Following DWZ, UncResCEO is the answer-uncertainty NET OF the scripted presentation (UncPreCEO), "
    "isolating the unscripted, call-specific component where the anticipation of an undisclosed deal WOULD surface; "
    "if any of that anticipation also leaks into the scripted, vetted remarks, the residual UNDERSTATES it (a "
    "conservative floor). By the same construction the residual is also net of analyst-question uncertainty (UncQue) "
    "and call negativity (NegCall), which grounds the scrutiny/tone reconciliation in 2.2 P5.3 and 2.5."),
  "role_in_paragraph": ("Owns the UncPre residualization POSITIVELY (DWZ's isolation design, suggestive) + the "
    "conservative floor + the RULE-COH-8 net-of-UncQue/NegCall grounding -- absorbed here after the old P3 threat-"
    "paragraph was cut (user 'cut it' + DWZ evidence)."),
  "type": "framing-nonverifiable",
  "relation_to_2_1": "FORMALIZES",
  "anchor_2_1": ["P4"],
  "source": {"key": "dwz", "evidence": "tmp/nlm_dwz_uncpre_control.json -- DWZ rationale: presentation = scripted firm-baseline (culture + current conditions); residual isolates the unscripted component."},
  "verification_plan": ("Roadmap Must-do #3 (OWN UncPre, do NOT leave it hanging) satisfied in ONE positive sentence, "
    "SUGGESTIVE register -- NO threat-paragraph. WORDING (advisor): 'would' NOT 'must' -- the signal is not EXCLUSIVELY "
    "in the residual (DWZ say UncPre absorbs 'current business conditions' / 'time-varying uncertainty affecting both "
    "parts'); KEEP the conservative-floor clause. GATE (advisor): the positive 'following DWZ' attribution is "
    "ANSWER-ONLY/PROVISIONAL (tmp/nlm_dwz_uncpre_control.json has NO cited_text span) -> if the write-time verbatim "
    "span does NOT materialize, FALL BACK to the bare hedge ('the residual nets out the scripted part') WITHOUT the "
    "DWZ design-attribution. RULE-COH-8 grounding preserved here. No NLM now.")
})

# delete old P3 (UncPre threat + net-of note); renumber P4 -> P3 (props P4.x -> P3.x)
del P["P3"]
newP3 = P.pop("P4")
newP3["order"] = 3
for x in newP3["propositions"]:
    x["prop_id"] = x["prop_id"].replace("P4.", "P3.")
P["P3"] = newP3
d["paragraphs"] = {k: P[k] for k in ["P1", "P2", "P3"]}  # enforce contiguous order

# _plan updates (drop the P3-threat framing; reflect the positive residual framing)
pl = d["_plan"]
pl["spine"] = ("P1 measure (LM share, UncAns eq-2) -> P2 decomposition (eq-4 -> UncRes; why residual; net of "
    "UncPre/UncQue/NegCall -> DWZ's isolation of the unscripted, call-specific component) -> P3 generated-regressand.")
pl["thin_claim"] = ("Present the residual POSITIVELY as DWZ's isolation of the unscripted component ('would' not "
    "'must'; conservative floor if leakage); own the generated-regressand suggestively; validity is an empirical "
    "question answered in 2.5.")
pl["division_of_labor"] = ("2.1 P4 located the signal in the call-varying residual (conceptually, no equation). 2.3 "
    "ADDS: the formal eq-4 + regressors, the residual's POSITIVE framing as DWZ's isolation of the unscripted call-"
    "specific component (net of UncPre/UncQue/NegCall), and the generated-regressand caveat. It does NOT re-argue the "
    "locating logic (COH-4).")

d["next_action"] = ("2.3 P3 (UncPre over-control THREAT-paragraph) CUT 2026-06-13 (user 'cut it' + DWZ evidence + "
    "advisor): folded into P2.5 as ONE POSITIVE sentence (DWZ's isolation design; 'would' not 'must'; conservative "
    "floor) carrying the RULE-COH-8 net-of-UncQue/NegCall grounding; P4 generated-regressand renumbered -> P3; 2.4/2.5 "
    "cross-refs ('2.3 P4'->'2.3 P3') fixed in the same edit. GATE: the positive DWZ attribution is provisional "
    "(answer-only) -> write-time verbatim span or fall back to the bare hedge. Plan now FINAL for every 2.3 paragraph; "
    "RE-RATIFY. Status PLANNED, prose BLOCKED. " + d["next_action"])
save(p23, d)
print("2.3: P3 cut, folded -> P2.5; P4->P3; props:",
      {k: [x["prop_id"] for x in P[k]["propositions"]] for k in d["paragraphs"]})

# ===== 2.4 + 2.5: fix external cross-refs '2.3 P4' -> '2.3 P3' (text-level; unambiguous substring) =====
for path in ["docs/Thesis/rewrite/section2.4_paragraph_ledger.json",
             "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"]:
    txt = open(path, encoding="utf-8").read()
    n = txt.count("2.3 P4")
    txt2 = txt.replace("2.3 P4", "2.3 P3")
    open(path, "w", encoding="utf-8").write(txt2)
    json.load(open(path, encoding="utf-8"))  # validate
    print(f"{path.split('/')[-1]}: replaced {n} '2.3 P4' -> '2.3 P3'; re-parse OK")
