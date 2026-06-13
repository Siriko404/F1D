# Print the locked 2.1 final_prose, paragraph by paragraph (read-only).
import json
d = json.load(open("docs/Thesis/rewrite/section2.1_paragraph_ledger.json", encoding="utf-8"))
for k, p in d["paragraphs"].items():
    fp = (p.get("final_prose") or "").strip()
    print(f"\n===== {k}  [{p.get('prose_status','?')}]  intent: {(p.get('intent') or '')[:90]}")
    print(fp if fp else "(final_prose EMPTY)")
