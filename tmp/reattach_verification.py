# -*- coding: utf-8 -*-
"""Re-attach the stripped theory-verification evidence (NLM query + verdict + the VERBATIM
appendix quotes) from corpus_audited.json onto the live _final §2.1 / §2.2 props. Inlines the
appendix answer into verification['evidence_quotes'] so each prop is self-contained for the
harness audit. Touches NO statement / number / other field. WRITE arg to apply."""
import json, sys, copy
from pathlib import Path
RW = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite")
CA = json.load(open(RW/"_audit"/"corpus_audited.json", encoding="utf-8"))
WRITE = len(sys.argv) > 1 and sys.argv[1] == "WRITE"
appendix = CA["appendix"]   # {prop_id: {answer: verbatim...}}

def paras(s):
    p = s.get("paragraphs", {})
    return list(p.values()) if isinstance(p, dict) else (p or [])

# 1. collect verification objects (+ inlined quotes) from corpus, by (section_id, prop_id)
want = {}   # (sec_id, prop_id) -> verification dict (with evidence_quotes)
for s in CA["sections"]:
    sid = str(s.get("section_id") or s.get("id") or "")
    if sid not in ("2.1", "2.2"): continue
    for pa in paras(s):
        for pr in pa.get("propositions", []):
            if not isinstance(pr, dict): continue
            if "verification" in pr:
                v = copy.deepcopy(pr["verification"])
                pid = pr.get("prop_id")
                # inline the verbatim appendix answer
                ref = v.get("_evidence_ref", "")
                akey = ref.split(":")[-1] if ":" in ref else pid
                if akey in appendix and isinstance(appendix[akey], dict) and appendix[akey].get("answer"):
                    v["evidence_quotes"] = appendix[akey]["answer"]
                if "nlm_query_draft" in pr and "query" not in v:
                    v["query"] = pr["nlm_query_draft"]
                want[(sid, pid)] = v
print(f"corpus verification objects to re-attach: {len(want)}  ({sum(1 for v in want.values() if 'evidence_quotes' in v)} carry verbatim quotes)")

fails = []
def ck(n, ok, d=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}" + (f" -- {d}" if d and not ok else ""))
    if not ok: fails.append(n)

# 2. apply to the two live ledgers
targets = {"2.1": RW/"_final"/"section2.1_paragraph_ledger.json",
           "2.2": RW/"_final"/"section2.2_paragraph_ledger.json"}
written = {}
for sid, path in targets.items():
    d = json.load(open(path, encoding="utf-8"))
    pre = copy.deepcopy(d)
    pl = d["paragraphs"]; items = list(pl.values()) if isinstance(pl, dict) else pl
    stmts_before = {}
    attached = 0
    for pa in items:
        for pr in pa.get("propositions", []) or pa.get("proposition_chain", []):
            if not isinstance(pr, dict): continue
            pid = pr.get("prop_id"); stmts_before[pid] = pr.get("statement")
            key = (sid, pid)
            if key in want:
                pr["verification"] = want[key]; attached += 1
    # invariants
    exp = sum(1 for (s2, _) in want if s2 == sid)
    ck(f"§{sid}: attached {attached} == corpus {exp}", attached == exp)
    # statements unchanged
    pl2 = d["paragraphs"]; items2 = list(pl2.values()) if isinstance(pl2, dict) else pl2
    same = all(pr.get("statement") == stmts_before.get(pr.get("prop_id"))
               for pa in items2 for pr in (pa.get("propositions", []) or pa.get("proposition_chain", [])) if isinstance(pr, dict))
    ck(f"§{sid}: all statements byte-identical", same)
    # only 'verification' key added anywhere (no other field changed)
    def strip_ver(o):
        o = copy.deepcopy(o)
        for pa in (o["paragraphs"].values() if isinstance(o["paragraphs"], dict) else o["paragraphs"]):
            for pr in pa.get("propositions", []) or pa.get("proposition_chain", []):
                if isinstance(pr, dict): pr.pop("verification", None)
        return o
    ck(f"§{sid}: nothing but 'verification' changed", strip_ver(d) == strip_ver(pre))
    json.loads(json.dumps(d))  # valid
    written[path] = d

print("="*50)
if fails:
    print("GATE FAILED:", fails); sys.exit(1)
print("GATE PASSED.")
if WRITE:
    for path, d in written.items():
        json.dump(d, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print("wrote", path.name)
else:
    print("dry-run. Re-run with WRITE.")
