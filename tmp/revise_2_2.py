# Apply the decided 2.2_QUEUED edits to section2.2_paragraph_ledger.json (programmatic, reversible).
# Edits: P2.2 thewissen -> one-clause callback (drop 15%); P2.3 drop 'involuntary'; P4.2 keown CUT + renumber.
import json

p = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
P = d["paragraphs"]

def prop(par, pid):
    for x in par["propositions"]:
        if x["prop_id"] == pid:
            return x
    raise KeyError(pid)

# --- P2.2: one-clause thewissen callback, drop the 15% re-cite ---
p22 = prop(P["P2"], "P2.2")
p22["statement"] = ("Prior work shows stock bidders deliberately MANAGE disclosure tone before stock-for-stock "
    "deals (callback 2.1 P6); H1 predicts the opposite register -- unmanaged uncertainty, before cash deals.")
p22["verification_plan"] = ("CALLBACK -- the deliberate-tone-management contrast is already SUPPORTED in 2.1 P6. "
    "ONE-CLAUSE callback only; do NOT re-cite the ~15% figure (it belongs to 2.1 P6). No new query.")

# --- P2.3: drop 'involuntary'; align to 2.1 P7's open readings ---
p23 = prop(P["P2"], "P2.3")
p23["statement"] = ("H1 is non-obvious because the literature documents deliberate, strategic tone management, "
    "whereas H1 predicts elevated uncertainty LANGUAGE surfacing under the disclosure bind; consistent with 2.1 P7, "
    "it takes no stance on whether that surfacing is strategic or compliance-constrained.")
p23["verification_plan"] = ("Framing; rests on P2.1+P2.2. DROP 'involuntary' (contradicts 2.1 P7, which holds both "
    "the strategic-silence and compliance-constrained readings open); H1 claims elevated uncertainty LANGUAGE only. "
    "Write-time accuracy pass.")

# P2 guardrail: add the no-15%-re-cite guard
P["P2"]["guardrails"] = [
    "RULE-COH-1: thewissen is a CALLBACK (P6) -> reference the contrast, do not re-review.",
    "RULE-COH-6: 'residual Q&A uncertainty' forward-refs 2.3.",
    "ONE-CLAUSE callback only -- do NOT re-cite the ~15% tone figure (lives in 2.1 P6).",
    "DROP 'involuntary' -- 2.1 P7 holds both readings open; H1 = elevated uncertainty LANGUAGE only."
]

# --- P4: CUT P4.2 (keown price run-up); renumber P4.3 -> P4.2; clean keown refs ---
P["P4"]["lit_body"] = "two clocks (information vs transaction)"
P["P4"]["intent"] = ("State H1b (differential timing): residual Q&A uncertainty resolves at announcement "
    "(information clock), while the acquirer's cash persists to completion (transaction clock).")
P["P4"]["guardrails"] = [
    "RULE-COH-1: the two-clock concept = CALLBACK (P5); formalize into an event-time test, do not re-explain.",
    "C1 caution: do NOT over-read POST (-0.0250*) as a finding.",
    ("GAP discriminator (C1 crux, advisor): the MNPI fingerprint is the DROP at the GAP bin (announced, NOT yet "
     "closed) -> uncertainty ~0 while cash still persists. Do NOT flatten GAP+POST into 'gone post' -- that loses "
     "the discriminator. (empire_drop_test: GAP = MNPI->~0 vs outcome->stays high.)"),
    "keown price run-up CUT from P4 (2026-06-13): it is an ANTICIPATION point (P2/H1), misplaced in a RESOLUTION-clock paragraph; the price-vs-language distinction stays in 2.1 P6."
]
# remove P4.2 (keown), renumber the surviving thin-claim guard P4.3 -> P4.2
P["P4"]["propositions"] = [x for x in P["P4"]["propositions"] if x["prop_id"] != "P4.2"]
for x in P["P4"]["propositions"]:
    if x["prop_id"] == "P4.3":
        x["prop_id"] = "P4.2"

# papers: mark keown1981 dropped from 2.2 (traceability; it remains a 2.1 P6 callback)
if "keown1981" in d.get("papers", {}):
    d["papers"]["keown1981"]["status_2_2"] = "DROPPED from 2.2 plan (P4.2 cut 2026-06-13); price run-up stays in 2.1 P6 only."

d["next_action"] = ("2.2 QUEUED EDITS APPLIED 2026-06-13 (de-queued per user 'revise planning to 100% complete'): "
    "P2.2 thewissen -> one-clause callback (15% dropped); P2.3 'involuntary' dropped (aligns 2.1 P7); P4.2 keown CUT + "
    "P4.3->P4.2 renumber. Plan now FINAL for every 2.2 paragraph. Status PLANNED, prose BLOCKED, NOT ratified. "
    + d["next_action"])

json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(p, encoding="utf-8"))
print("2.2 revised: P2.2 one-clause, P2.3 no-involuntary, P4.2(keown) cut + renumbered; re-parse OK; P4 props ->",
      [x["prop_id"] for x in P["P4"]["propositions"]])
