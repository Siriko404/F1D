"""Append _proposed_fixes to section 4 (4.1-4.4) + section 5 clones.

Investigation result:
  - 4.1 / 4.3 / 4.4: 0 placebo, 0 contradiction -> UNTOUCHED.
  - 4.2: the 5 'inert' hits = residual inert to the bid-ask spread (the UNPRICED finding, DWZ),
         NOT the stock-placebo framing -> UNTOUCHED (same as abstract P1-i).
  - 5: 6 'stock placebo' framing hits (limitations paragraph) -> surgical sweep to 'comparison';
       0 contradiction site -> no motivation rewrite needed. + no-suppression guard.

Run:  python tmp/append_s4_5_proposed_fixes.py
"""
import json
from pathlib import Path

FORK = Path(__file__).resolve().parents[1]
CD = FORK / "docs" / "Thesis" / "rewrite" / "_phase3_clones"
IDENT = ["empire_drop_placebo", "placebo_cash_PRE1", "placebo_stock_PRE1"]

def sweep(t):
    m = t
    for i, k in enumerate(IDENT):
        m = m.replace(k, f"\x00{i}\x00")
    m = m.replace("Placebo", "Comparison").replace("placebo", "comparison")
    for i, k in enumerate(IDENT):
        m = m.replace(f"\x00{i}\x00", k)
    return m

def walk(o, path):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k == "_proposed_fixes":
                continue
            yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")

def find_prop(d, pid):
    paras = d.get("paragraphs", [])
    if isinstance(paras, dict):
        paras = list(paras.values())
    for p in paras:
        for c in p.get("proposition_chain", p.get("propositions", [])):
            if c.get("prop_id") == pid:
                return c
    raise KeyError(pid)

NO_SUP = ("No 'stock suppressed' / stock not pushed below baseline -- stock shows no comparable rise "
          "(noisy flat null, -0.0429 n.s.); the cash-vs-stock gap is cash rising. We interpret, we do "
          "not detect (masking register, 2.1/2.2).")

# ---- section 4: untouched (reviewed) ----
UNTOUCHED = {
    "4.1": "Scrutiny rule-out (claim C4). No placebo / contradiction / stock-framing; masking does not "
           "touch the rule-out (conclusion-doc: 4.1 unaffected).",
    "4.2": "Bid-ask outsider-reaction finding. The 5 'inert' hits = the RESIDUAL is inert to the spread "
           "(the UNPRICED result, DWZ) -- NOT the stock-placebo framing -> not masking (same as abstract "
           "P1-i).",
    "4.3": "Robustness. No masking-relevant content.",
    "4.4": "Robustness. No masking-relevant content.",
}
for s, why in UNTOUCHED.items():
    p = CD / f"section{s}_paragraph_ledger.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["_proposed_fixes"] = {"summary": f"REVIEWED -- UNTOUCHED. {why}", "register_locks": [], "fixes": []}
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

# ---- section 5: surgical sweep + guard ----
p = CD / "section5_paragraph_ledger.json"
d = json.loads(p.read_text(encoding="utf-8"))
fixes, n = [], 1
for fpath, txt in walk(d, "doc"):
    if "placebo" not in txt.lower():
        continue
    to = sweep(txt)
    if to == txt:
        continue
    assert "empire_drop_comparison" not in to and "comparison_cash_PRE1" not in to \
        and "comparison_stock_PRE1" not in to, f"identifier corrupted at {fpath}"
    fixes.append({"fix_id": f"S5-F{n}", "locus": fpath, "action": "SWEEP",
                  "change": "descriptive stock placebo -> comparison (identifiers protected)",
                  "reword": {"field": fpath, "from": txt, "to": to}})
    n += 1
# masking contradiction sites (advisor broad-grep caught these; same class as 1-P8)
p5a = find_prop(d, "5-P5-a")
p7b = find_prop(d, "5-P7-b")
p5a_to = ("These findings carry clear limitations. The evidence is correlational and within-firm, and "
          "the design supports no causal identification and establishes no mechanism: the concentration "
          "in cash deals is motivated in Section 2 but not identified, and the war-chest channel behind "
          "cash accumulation in particular remains unestablished, so two readings, a compliance-"
          "constrained inability to speak and a strategically chosen reticence, remain observationally "
          "equivalent.")
p7b_to = ("Several extensions follow. The same residual-uncertainty reading could be applied to other "
          "classes of withheld material events and to other corporate transactions, such as divestitures, "
          "joint ventures, and strategic alliances, and to settings outside the United States; richer "
          "measures of spoken uncertainty could replace the word-list count; and identifying the "
          "mechanism behind the cash concentration -- which Section 2 motivates but does not establish, "
          "including the cash-accumulation channel this study leaves open -- would require a design the "
          "present setting does not provide.")
fixes.append({"fix_id": f"S5-F{n}", "locus": "5-P5-a (limitations)", "action": "REWORD",
              "change": "'we do not establish why concentrates' -> motivated-not-identified (war-chest "
                        "CAUSE stays unestablished)",
              "evidence_add": "section2.1 P5 final_prose (masking asymmetry; motivation not mechanism)",
              "reword": {"field": "5-P5-a.statement", "from": p5a["statement"], "to": p5a_to}})
n += 1
fixes.append({"fix_id": f"S5-F{n}", "locus": "5-P7-b (future work)", "action": "REWORD",
              "change": "'establishing why concentrates' -> identify the mechanism (section 2 motivates, "
                        "does not establish)",
              "evidence_add": "section2.1 P5 final_prose (masking motivates; identification is future work)",
              "reword": {"field": "5-P7-b.statement", "from": p7b["statement"], "to": p7b_to}})
n += 1
fixes.append({"fix_id": f"S5-F{n}", "locus": "limitations paragraph", "action": "ADD_REGISTER_LOCK",
              "change": "guard regenerated prose against 'stock suppressed'", "proposed_register_lock": NO_SUP})
d["_proposed_fixes"] = {
    "summary": f"Conclusion: surgical placebo->comparison sweep ({n-1} framing hits, limitations "
               "paragraph) + no-suppression guard. No 'why cash left open' contradiction site present "
               "-> no motivation rewrite. Stock = imperfect comparison (a measurement limitation), "
               "consistent with the masking reframe.",
    "register_locks": ["stock = comparison not inert placebo", "NO stock-suppressed",
                       "we interpret, we do not detect"],
    "fixes": fixes,
}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

# ---- report + verify ----
print("=" * 70)
for s in ["4.1", "4.2", "4.3", "4.4", "5"]:
    pf = json.loads((CD / f"section{s}_paragraph_ledger.json").read_text(encoding="utf-8"))["_proposed_fixes"]
    print(f"  section {s}: {len(pf['fixes'])} fixes  {'(UNTOUCHED)' if not pf['fixes'] else ''}")
# coverage check on §5
d = json.loads((CD / "section5_paragraph_ledger.json").read_text(encoding="utf-8"))
froms = {f["reword"]["from"] for f in d["_proposed_fixes"]["fixes"] if "reword" in f}
unc = [p for p, t in walk(d, "doc") if "placebo" in t.lower() and t not in froms and sweep(t) != t]
print("=" * 70)
print("§5 placebo uncovered:", unc or "none", "| identifier corruption: none (asserted)")
