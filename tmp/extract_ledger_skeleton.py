# Read the SUBSTANCE of each §2 paragraph ledger (plan + propositions + verdicts + guardrails +
# forward-refs) WITHOUT the verbatim NLM evidence blocks (answer/quotes/located/span_pin) which are
# huge already-verified receipts. Lets me read all four carefully without blowing context.
import json, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite")

def short(s, n=300):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n] + " …"

for sub in ["2.1", "2.3", "2.4", "2.5"]:
    d = json.loads((ROOT / f"section{sub}_paragraph_ledger.json").read_text(encoding="utf-8"))
    print("\n" + "=" * 100)
    print(f"### LEDGER {sub}: {d.get('title')!r}  | status: {short(d.get('status'),120)}")
    pl = d.get("_plan", {})
    for k in ("section_job", "spine", "serves", "boundary", "thin_claim", "division_of_labor", "estimands_to_define"):
        if pl.get(k):
            print(f"  _plan.{k}: {short(pl[k], 360)}")
    paras = d.get("paragraphs", {})
    print(f"  -- {len(paras)} paragraphs --")
    for pk, p in paras.items():
        print(f"\n  [{pk}] intent: {short(p.get('intent'),300)}")
        if p.get("serves"):   print(f"       serves: {short(p['serves'],200)}")
        if p.get("boundary"): print(f"       boundary: {short(p['boundary'],200)}")
        if p.get("thin_claim"): print(f"       thin_claim: {short(p['thin_claim'],200)}")
        for g in p.get("guardrails", []) or []:
            print(f"       guard: {short(g,200)}")
        for prop in p.get("propositions", []) or []:
            v = prop.get("verification", {})
            verdict = v.get("verdict") or prop.get("status") or "?"
            src = (prop.get("source") or {}).get("key", "")
            print(f"       - {prop.get('prop_id')} [{prop.get('type')}|{verdict}|{src}] {short(prop.get('statement'),240)}")
            note = v.get("verdict_note")
            if note: print(f"           note: {short(note,200)}")
    na = d.get("next_action")
    if na: print(f"\n  next_action: {short(na, 400)}")
