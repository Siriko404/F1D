# Resolve the §2 number-claims against the COMMITTED NLM spans (advisor: resolve, don't hand homework).
# Searches each prop's admissible cited_text spans (+ answer as fallback) for the prose figures.
import json, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
led = json.loads((ROOT/"docs/Thesis/rewrite/section2.1_paragraph_ledger.json").read_text(encoding="utf-8"))
valp = ROOT/"tmp/nlm_validity_definitions.json"
val = json.loads(valp.read_text(encoding="utf-8")) if valp.exists() else {"captures":{}}

def get(para, prop):
    for p in led["paragraphs"][para]["propositions"]:
        if p["prop_id"] == prop:
            v = p.get("verification", {})
            spans = []
            if "parts" in v:
                for pt in v["parts"]:
                    spans += [q.get("cited_text") or "" for q in pt.get("quotes", [])]
            spans += [q.get("cited_text") or "" for q in v.get("quotes", [])]
            for rq in v.get("requery", []):
                spans += [q.get("cited_text") or "" for q in rq.get("quotes", [])]
            return [s for s in spans if s], (v.get("answer") or "")
    return [], ""

def chk(label, para, prop, toks):
    spans, ans = get(para, prop)
    print(f"\n### {label}  ({para}/{prop}, {len(spans)} spans)")
    for t in toks:
        hit = next((s for s in spans if t.lower() in s.lower()), None)
        if hit:
            i = hit.lower().find(t.lower()); print(f"  SPAN  '{t}': ...{hit[max(0,i-45):i+55]}...")
        elif t.lower() in ans.lower():
            i = ans.lower().find(t.lower()); print(f"  ANS   '{t}' (answer-only): ...{ans[max(0,i-45):i+55]}...")
        else:
            print(f"  MISS  '{t}'  <-- not in any span or answer")

chk("LM uncertainty 285 / Harvard 3/4", "P2", "P2.2", ["285", "three-quarter", "73", "74", "75"])
chk("Hollander six-of-ten", "P3", "P3.1", ["six", "60 ", "sixty", "0.6"])
chk("Thewissen 15%", "P6", "P6.1", ["15", "fifteen"])
chk("Ragozzino 9% / 7.2%", "P6", "P6.2", ["9", "7.2", "nine"])

print("\n### Hollander P3.1 — ALL spans (six-of-ten figure check)")
_sp, _ = get("P3", "P3.1")
for s in _sp:
    print("  -", s[:260])

print("\n### Hassan PRisk definition spans (validity) — reconcile 'share' vs scale")
for qid, cap in val.get("captures", {}).get("hassan2020", {}).items():
    for q in cap.get("quotes", []):
        ct = (q.get("cited_text") or "").strip()
        if ct:
            print(f"  [{qid} n{q.get('n')}] {ct[:220]}")
