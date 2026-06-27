"""Append _proposed_fixes to section 1 + abstract clones.

Two layers:
  A. SURGICAL placebo->comparison sweep (whole-doc, identifier-protected) -- same as section 3.
  B. AUTHORED masking-motivation rewords (the contradiction sites where the intro/abstract
     promised 'why cash is left open', which section 2 now MOTIVATES):
       - 1-P8-a: 'leaves open why concentrates in cash' -> consistent-with-masking (motivation,
                 NOT identification); the SOURCE mechanism (compliance vs strategic) stays open.
       - abstract-P1-g: + one citation-free motivation clause.
     Evidence = POINTER callbacks to section 2.1's verified props (S-V/Louis/thewissen live in 2.1);
     NO new NLM verbatim is copied here.
  + no-suppression register-lock on 1-P8 and the abstract.

Run:  python tmp/append_s1abs_proposed_fixes.py
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

def do_sweeps(d, tag):
    fixes, n = [], 1
    for fpath, txt in walk(d, "doc"):
        if "placebo" not in txt.lower():
            continue
        to = sweep(txt)
        if to == txt:
            continue
        assert "empire_drop_comparison" not in to and "comparison_cash_PRE1" not in to \
            and "comparison_stock_PRE1" not in to, f"identifier corrupted at {fpath}"
        fixes.append({"fix_id": f"{tag}-F{n}", "locus": fpath, "action": "SWEEP",
                      "change": "descriptive stock placebo -> comparison",
                      "reword": {"field": fpath, "from": txt, "to": to}})
        n += 1
    return fixes, n

# ========================= section 1 =========================
d = json.loads((CD / "section1_paragraph_ledger.json").read_text(encoding="utf-8"))
fixes, n = do_sweeps(d, "S1")
p8 = find_prop(d, "1-P8-a")
p8_to = ("Throughout, we read these patterns as correlational and within-firm: the design supports no "
         "causal identification and establishes no mechanism. The concentration in cash deals is "
         "consistent with stock acquirers' incentive to manage their pre-deal narrative (developed in "
         "Section 2), an incentive cash acquirers lack -- offered as motivation, not identification -- "
         "while the source "
         "of the uncertainty, compliance-constrained inability to speak versus strategically chosen "
         "reticence, remains observationally equivalent.")
fixes.append({"fix_id": f"S1-F{n}", "locus": "1-P8-a", "action": "REWORD",
              "change": "'leaves open why language concentrates in cash' -> masking MOTIVATION (motivation "
                        "NOT identification); source mechanism stays open",
              "register_locks": ["masking = motivation not mechanism", "no-identification",
                                 "source (compliance vs strategic) stays open", "NO stock-suppressed"],
              "evidence_add": "section2.1 P5 final_prose (masking asymmetry: Shleifer-Vishny currency "
                              "motive + Louis pre-deal earnings behavior + thewissen tone; motivation, "
                              "not mechanism)",
              "reword": {"field": "1-P8-a.statement", "from": p8["statement"], "to": p8_to}})
n += 1
# sibling fields of 1-P8 carry the same 'leaves open why concentrates' framing -> reword too
para8 = d["paragraphs"][7]
intent_to = ("Deliver Move 3's explicit honesty caveat as its own short paragraph: state plainly that "
             "throughout these patterns are read as correlational and within-firm, that the design "
             "supports no causal identification and establishes no mechanism, and that the concentration "
             "in cash deals is consistent with stock acquirers' pre-deal management incentive (developed "
             "in Section 2) that cash acquirers lack -- motivation, not identification -- while the source of the "
             "uncertainty (compliance-constrained inability to speak versus strategically chosen "
             "reticence) remains observationally equivalent (IN.13).")
thin_to = ("The patterns are correlational and within-firm; no causal identification, no established "
           "mechanism; the concentration in cash deals is motivated (the masking asymmetry developed in "
           "Section 2; not identification), while the source -- compliance-constrained versus "
           "strategic-reticence readings -- stays observationally equivalent.")
fixes.append({"fix_id": f"S1-F{n}", "locus": "1-P8.intent.statement", "action": "REWORD",
              "change": "sibling field: 'leaves open why concentrates' -> motivated (matches 1-P8-a)",
              "reword": {"field": "paragraphs[7].intent.statement", "from": para8["intent"]["statement"],
                         "to": intent_to}})
n += 1
fixes.append({"fix_id": f"S1-F{n}", "locus": "1-P8.thin_claim", "action": "REWORD",
              "change": "sibling field: 'why concentrates is open' -> motivated (matches 1-P8-a)",
              "reword": {"field": "paragraphs[7].thin_claim", "from": para8["thin_claim"], "to": thin_to}})
n += 1
fixes.append({"fix_id": f"S1-F{n}", "locus": "1-P8", "action": "ADD_REGISTER_LOCK",
              "change": "guard regenerated prose against 'stock suppressed'", "proposed_register_lock": NO_SUP})
d["_proposed_fixes"] = {
    "summary": "Intro: sweep stock placebo->comparison; rewrite 1-P8-a so the 'why cash concentrates' "
               "promise is MOTIVATED (masking, motivation not id) rather than 'left open' -- the section-2 "
               "contradiction site. 1-P6 cash-accumulation-CAUSE stays open; 1-P1 source stays open.",
    "register_locks": ["stock = comparison not inert placebo", "masking = motivation not mechanism",
                       "no-identification", "source stays open", "NO stock-suppressed"],
    "fixes": fixes,
}
(CD / "section1_paragraph_ledger.json").write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
s1_fixes = fixes

# ========================= abstract =========================
d = json.loads((CD / "section_abstract_paragraph_ledger.json").read_text(encoding="utf-8"))
fixes, n = do_sweeps(d, "ABS")
fixes.append({"fix_id": f"ABS-F{n}", "locus": "abstract-P1", "action": "ADD_REGISTER_LOCK",
              "change": "guard regenerated prose against 'stock suppressed'", "proposed_register_lock": NO_SUP})
d["_proposed_fixes"] = {
    "summary": "Abstract: sweep stock placebo->comparison ONLY (+ no-suppression lock). Motivation clause "
               "DROPPED (advisor): in the zero-caveat abstract, 'concentrates in cash not stock' + 'stock "
               "manages' invites the suppression misread; C1 carries the paper, so the abstract stays "
               "findings-pure. P1-i (residual inert to spread = 4.2 unpriced) is NOT masking -> untouched.",
    "register_locks": ["abstract stays findings-pure", "NO stock-suppressed"],
    "fixes": fixes,
}
(CD / "section_abstract_paragraph_ledger.json").write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

# ---- report ----
print("=" * 74)
for tag, fx in [("section1", s1_fixes), ("abstract", fixes)]:
    sw = sum(1 for f in fx if f["action"] == "SWEEP")
    rw = sum(1 for f in fx if f["action"] == "REWORD")
    lk = sum(1 for f in fx if f["action"] == "ADD_REGISTER_LOCK")
    print(f"{tag:10}: {sw} sweeps, {rw} motivation rewords, {lk} no-suppress lock")
print("=" * 74)
print("AUTHORED §1 motivation rewords (the contradiction site, x3 sibling fields):")
print("\n[1-P8-a] TO:\n ", p8_to)
print("\n[1-P8.intent] TO:\n ", intent_to)
print("\n[1-P8.thin_claim] TO:\n ", thin_to)
print("\n[abstract] motivation clause DROPPED -> sweep + lock only.")
