# Audit what the §2.1 NLM ledger actually RECORDS per proposition:
# source title, # admissible verbatim spans (cited_text), verdict. Plus the yardstick JSON.
# Firm evidence for "were the 12 verified, and for what".
import json, pathlib
REPO = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
LED = REPO / "docs" / "Thesis" / "rewrite" / "section2.1_paragraph_ledger.json"
VAL = REPO / "tmp" / "nlm_validity_definitions.json"

def spans(v):
    if "parts" in v:
        return sum(len([q for q in p.get("quotes", []) if (q.get("cited_text") or "").strip()]) for p in v["parts"])
    return len([q for q in v.get("quotes", []) if (q.get("cited_text") or "").strip()])

def titles(v):
    if "parts" in v:
        return " | ".join(sorted({(p.get("source", {}).get("title") or "?")[:40] for p in v["parts"]}))
    return (v.get("source", {}).get("title") or "?")[:48]

print("=== section2.1_paragraph_ledger.json ===")
led = json.loads(LED.read_text(encoding="utf-8"))
for para, pdata in led.get("paragraphs", {}).items():
    for p in pdata.get("propositions", []):
        v = p.get("verification")
        if not v:
            print(f"  {para}/{p['prop_id']:6} NO verification block"); continue
        print(f"  {para}/{p['prop_id']:6} verdict={v.get('verdict'):10} spans={spans(v):2}  src={titles(v)}")

print("\n=== tmp/nlm_validity_definitions.json (yardsticks) ===")
if VAL.exists():
    val = json.loads(VAL.read_text(encoding="utf-8"))
    for key, caps in val.get("captures", {}).items():
        for qid, cap in caps.items():
            nq = len([q for q in cap.get("quotes", []) if (q.get("cited_text") or "").strip()])
            ds = [d.get("title","")[:30] for d in cap.get("discovered_sources", [])]
            print(f"  {key:12}/{qid:16} spans={nq:2} discovered={ds}")
else:
    print("  MISSING")
