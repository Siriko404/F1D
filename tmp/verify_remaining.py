# Diligent verification of remaining coherence items J, L, N against the actual ledgers/JSON.
import json, pathlib, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

# --- J: §2.1 ledger status + per-paragraph prose_status (is P7 the odd one out?) ---
l21 = json.loads((ROOT / "docs/Thesis/rewrite/section2.1_paragraph_ledger.json").read_text(encoding="utf-8"))
print("J: 2.1 top status =", str(l21.get("status"))[:90])
for k, para in l21.get("paragraphs", {}).items():
    print(f"   {k}: prose_status = {para.get('prose_status')}")

# --- L: Thewissen P6.1 -- is the 15% tied to stock-for-stock or all M&A? ---
for p in l21["paragraphs"]["P6"]["propositions"]:
    if p["prop_id"] == "P6.1":
        v = p["verification"]
        print("\nL: P6.1 verdict_note:", (v.get("verdict_note") or "")[:300])
        print("L: spans mentioning 15 / stock / M&A:")
        for q in v.get("quotes", []):
            ct = (q.get("cited_text") or "").strip()
            if ct and any(t in ct.lower() for t in ["15", "stock", "m&a", "merger", "tone"]):
                print("  -", ct[:200])

# --- N: DWZ equation numbering (does the paper number them 2/4/5 as the thesis cites?) ---
dwzp = ROOT / "tmp/nlm_dwz_equations.json"
if dwzp.exists():
    dwz = json.loads(dwzp.read_text(encoding="utf-8"))
    s = json.dumps(dwz)
    print("\nN: dwz eq json top keys:", list(dwz.keys())[:12])
    print("N: equation-number mentions in spans/answers:", sorted(set(re.findall(r"[Ee]quation\s*\(?(\d)\)?", s)))[:15])
    print("N: 'Equation (4)' present:", "Equation (4)" in s or "equation (4)" in s)
else:
    print("\nN: tmp/nlm_dwz_equations.json MISSING")
