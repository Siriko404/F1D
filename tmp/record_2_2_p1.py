# Record the advisor-cleared §2.2 P1 prose into the LEDGER (not the .tex). Ledger-first workflow (user).
import json
p = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
P1 = d["paragraphs"]["P1"]
assert P1["final_prose"] == "", f"P1 final_prose not empty: {P1['final_prose'][:40]!r}"
assert P1["prose_status"] == "BLOCKED", P1["prose_status"]
P1["final_prose"] = (
r"""The preceding section isolates two dimensions of the pattern we expect: an \emph{anticipatory} dimension, in which CEO uncertainty language is elevated while an acquisition remains undisclosed and recedes once it is announced, and a \emph{cash-concentrated} dimension, in which that elevation is stronger for cash acquisitions than for stock. This section turns those dimensions into formal, falsifiable predictions about \emph{where} and \emph{when} the signal appears in a CEO's unscripted answers---not why it appears, a mechanism the framework leaves open. The object of each prediction is the call-varying residual of CEO uncertainty language in the Q\&A---the component that remains once a CEO's persistent speaking style is netted out, which the next section defines formally---and every prediction is read in descriptive, correlational terms. Timing is measured in event time: $e$ counts calendar quarters relative to a firm's first acquisition announcement, so that $e=-1$ denotes the call in the quarter immediately before it. The focal pre-announcement indicator is $\mathrm{PreAnnounceQtr} = \mathbf{1}[e=-1]$, defined for a firm's first acquisition financed at least half in cash. The three hypotheses that follow---H1, H1a, and H1b---are stated here as predictions and confronted with the data by the designs developed below.""")
P1["prose_status"] = "DRAFTED-IN-LEDGER 2026-06-13 (advisor-cleared; .tex push deferred per user)"
P1["prose_gate"]["all_supported"] = True   # P1.1 internal, P1.2 definitional, P1.3 framing -> no NLM
P1["prose_gate"]["unlocked"] = True
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))
print("2.2 P1 prose recorded into section2.2 ledger (final_prose set, gate unlocked).")
