# Advisor (100%-clean bar): the §4.1 VERDICT leaked into §2.5. Remove it -- enforce the user's own split
# (verdict lives ONLY in 4.1). P4.3 -> pure pointer (no 'does NOT account'); P1 intent + P1.1 drop '& rejected'.
# Also record the two prose-time overclaim watch-items as write-time flags (don't change substance now).
import json
p = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))

P4 = d["paragraphs"]["P4"]["propositions"]
assert P4[2]["prop_id"] == "P4.3", "P4.3 id"
assert "does NOT account for THIS pre-announcement run-up" in P4[2]["statement"], "P4.3 verdict text drift"
P4[2]["statement"] = ("Pure forward-pointer (NO verdict stated here): the formal scrutiny side-test, its hedged verdict, and the "
    "underpowered caveat are all reported in 4.1, which owns the C4 hedge verbatim. 2.5 states only that the test is run and reported there.")
P4[2]["role_in_paragraph"] = "Pure forward-ref to 4.1 (no verdict content in 2.5; 4.1 owns the verdict + the C4 hedge)."
P4[2]["verification_plan"] = ("2.5 carries ONLY the pure pointer -- no verdict, no direction, no nulls (advisor 100%-clean: keep the §4.1 "
    "verdict out of §2.5). C4 hedge stated VERBATIM in 4.1. Write-time pass.")

P1 = d["paragraphs"]["P1"]
assert "tested & rejected as a side analysis" in P1["intent"], "P1 intent drift"
P1["intent"] = P1["intent"].replace("tested & rejected as a side analysis", "tested as a side analysis")
s11 = P1["propositions"][0]
assert "we test, and reject, as a side analysis" in s11["statement"], "P1.1 drift"
s11["statement"] = s11["statement"].replace("we test, and reject, as a side analysis", "we test as a side analysis")

d["next_action"] = ("[100%-clean fix 2026-06-13] DE-VERDICTED §2.5: P4.3 -> pure pointer (removed 'scrutiny does NOT account for THIS "
    "run-up'); P1 intent + P1.1 dropped '& rejected' -> 'tested' (verdict lives ONLY in 4.1). WRITE-TIME OVERCLAIM FLAGS (advisor, do "
    "NOT change ledger substance now): (a) P4.2 prose say 'tracks cash / behaves as intended', NOT a bald 'it is VALID'; (b) 'rises "
    "around cash-deal announcements' -> 'ahead of / in the quarter before' (0.0408**, tighter + matches the evidence). " + d["next_action"])

open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))
print("2.5 de-verdicted: P4.3 pure pointer; P1/P1.1 'tested' (no reject); 2 write-time overclaim flags recorded.")
