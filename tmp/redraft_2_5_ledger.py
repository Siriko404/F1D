# Scrub competition from the 2.5 ledger + record the redrafted prose. Atomic (writes once at end). Fail-closed.
# Keeps keys P1/P2/P4/P5 (P3 deleted, no renumber -> 2.2 P5 / 2.3 P2.5 refs to "2.5 P4/P4.4" stay valid).
import json
LED = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
DRAFT = "tmp/draft_2_5_full.tex"
d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]; pl = d["_plan"]

# 1) delete P3 (competition)
assert "competition" in json.dumps(P["P3"]).lower(), "P3 is not the competition paragraph?"
del P["P3"]

# 2) scrub _plan competition (wholesale field replace, presence-guarded)
assert "discriminant" in pl["section_job"]
pl["section_job"] = "Validate the construct via convergent validity and MOTIVATE the scrutiny identification side-test (plausible alternative driver, tested in 4.1). [competition/discriminant test DROPPED 2026-06-14.]"
assert "discriminant" in pl["spine"]
pl["spine"] = "P1 frame (convergent demand + scrutiny flag) -> P2 convergent (LEAD with the significant association; one-tailed + magnitude secondary) -> P4 scrutiny construct + motivation (verdict in 4.1) -> P5 key constructs. [P3 discriminant/competition DROPPED.]"
assert "discriminant" in pl["thin_claim"]
pl["thin_claim"] = "Convergent = SIGNIFICANT positive association (lead, FD); one-tailed + economic magnitude are honest SECONDARY qualifiers; scrutiny = 'doesn't account for THIS run-up,' not 'never matters.' [discriminant clause removed.]"
assert "hoberg" in pl.get("validity_papers_status", "").lower()
pl["validity_papers_status"] = "hassan2020 (PRisk), baker2016 (US-EPU), davis2016 (GEPU, provisional, fold-as-is) VERIFIED via NLM 2026-06-13. [hoberg2016/hoberg2010/'fluidity' REMOVED 2026-06-14 -- competition test dropped.] C5 numbers from the regression tables (the disregarded summary stats are NOT used; FB magnitude is a PLACEHOLDER)."

# 3) papers: drop hoberg
for k in ["hoberg2016", "hoberg2010"]:
    d["papers"].pop(k, None)

# 4) P1 intent + P1.1: drop discriminant
assert "discriminant" in P["P1"]["intent"]
P["P1"]["intent"] = "Frame the checks: (a) convergent -- the residual moves with established uncertainty measures (P2); (b) the analyst-scrutiny rival -- a plausible alternative driver tested as a side analysis (P4 -> 4.1). [discriminant/competition demand REMOVED 2026-06-14; distinctness rests on the 2.3 net-of-controls floor + the 4.1 rule-out.]"
assert "discriminant" in P["P1"]["propositions"][0]["statement"]
P["P1"]["propositions"][0]["statement"] = "The residual UncResCEO must (a) be convergent -- move with established uncertainty constructs (P2); and is checked against (b) the analyst-scrutiny rival, a plausible alternative driver tested as a side analysis (P4 -> 4.1). By construction it is already net of the scripted presentation and analyst-question wording (2.3)."

# 5) P2 plan-fields: flip 'lead with discriminant' -> lead with significance
p2 = P["P2"]
assert "discriminant" in p2["boundary"]
p2["boundary"] = "Convergent validity only. LEAD with the significant positive association (FD); one-tailed + economic magnitude as honest secondary qualifiers. [no longer 'lead with discriminant'.]"
if "demoted" in p2.get("serves", ""):
    p2["serves"] = "Convergent leg -- now the PRIMARY validity evidence (lead with significance)."
if "Consistent with" in p2.get("thin_claim", ""):
    p2["thin_claim"] = "LEAD with the SIGNIFICANT positive association (one-tailed); keep small-PRisk + economic magnitude as honest secondary notes (FD). Do not over-hedge."

d["_COMPETITION_DROPPED_2026_06_14"] = "User directive (from PDF): product-market competition / discriminant test (old P3) DROPPED COMPLETELY ('disclosable->presentation' logic did not separate it from PRisk/EPU). P3 deleted; hoberg cites removed; P1/P2/_plan reframed; validity = convergent (P2, significant) + 4.1 scrutiny + 2.3 floor. Keys kept P1/P2/P4/P5. FB economic-effect = PLACEHOLDER (summary stats disregarded as wrong)."

# 6) record redrafted prose P1/P2/P4/P5 from draft; INVERTED asserts (competition ABSENT)
parts = open(DRAFT, encoding="utf-8").read().split("%%")
md = dict(zip(parts[1::2], parts[2::2]))
segs = {k: md[k].strip() for k in ["P1", "P2", "P4", "P5"]}
for k, v in segs.items():
    assert "---" not in v and "--" not in v, f"{k} dash"
    low = v.lower()
    assert "hoberg" not in low and "competition" not in low and "discriminant" not in low, f"{k} still has competition content"
assert "PLACEHOLDER-FB" in segs["P2"], "FB placeholder missing"
assert "significantly and positively associated" in segs["P2"], "FD lead missing"
assert "the word list that identifies these turns is reported in the Appendix" in segs["P4"], "FC pointer missing"
NR = "DRAFTED-IN-LEDGER 2026-06-14 (competition DROPPED; FD lead-significance; FB placeholder; FC appendix ptr; dash-free; NOT ratified)"
for k in ["P1", "P2", "P4", "P5"]:
    P[k]["final_prose"] = segs[k]; P[k]["prose_status"] = NR

# atomic write + post-checks
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
dd = json.load(open(LED, encoding="utf-8"))
assert "P3" not in dd["paragraphs"] and list(dd["paragraphs"]) == ["P1", "P2", "P4", "P5"], dd["paragraphs"].keys()
assert "hoberg" not in str(dd["papers"]).lower(), "hoberg still in papers"
for k in ["P1", "P2", "P4", "P5"]:
    assert "competition" not in dd["paragraphs"][k]["final_prose"].lower()
print("2.5 ledger: P3 deleted; _plan/papers/P1/P2 scrubbed; prose P1/P2/P4/P5 recorded (competition absent in prose).")
