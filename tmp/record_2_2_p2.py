# Record §2.2 P2 (H1) prose into the ledger, with the two advisor fixes applied:
# (1) cut the bald motive 'aimed at the share price' -> 'a deliberate adjustment';
# (2) 'cast as a falsifiable claim' -> 'stated as a falsifiable prediction' (flatter register).
import json
p = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
P2 = d["paragraphs"]["P2"]
assert P2["final_prose"] == "", f"P2 final_prose not empty: {P2['final_prose'][:40]!r}"
P2["final_prose"] = (
r"""The first hypothesis, H1, concerns timing: residual Q\&A uncertainty is elevated in a cash acquirer's pre-announcement quarter, relative to that firm's own other quarters---the anticipatory dimension stated as a falsifiable prediction. That the prediction is not mechanical is clear from the nearest evidence, which runs the other way: \citet{thewissen2024} document that acquirers manage the tone of their disclosure ahead of stock-for-stock deals, a deliberate adjustment. H1 predicts a different register in a different setting---not tone managed to move the market, but uncertainty language that surfaces in a cash acquirer's answers while the deal is withheld. Consistent with the bounded reading established earlier, the hypothesis takes no stance on whether that surfacing is compliance-constrained or strategically chosen; it asserts only that the language moves, and when.""")
P2["prose_status"] = "DRAFTED-IN-LEDGER 2026-06-13 (advisor-cleared: motive-cut + flatter clause; .tex push deferred)"
P2["prose_gate"]["all_supported"] = True   # P2.1 internal, P2.2 thewissen CALLBACK (verified 2.1 P6), P2.3 framing
P2["prose_gate"]["unlocked"] = True
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))
print("2.2 P2 (H1) prose recorded into ledger.")
