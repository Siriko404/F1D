# -*- coding: utf-8 -*-
"""Normalize MERGED to canonical Format-B (reorder para+prop keys, insert 6 reason fields),
write back to MERGED (single source of truth), re-run PLACEMENT GATE on MERGED,
then place = EXACT COPY of MERGED -> live section4.5_paragraph_ledger.json.
Pass 'WRITE' to actually write MERGED + place."""
import json, sys, shutil
from pathlib import Path
FIN = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite\_final")
SRC = FIN/"_proposals"/"section4.5_MERGED.json"
DST = FIN/"section4.5_paragraph_ledger.json"
SIB = FIN/"section4.4_paragraph_ledger.json"
WRITE = len(sys.argv) > 1 and sys.argv[1] == "WRITE"

CANON_PARA = ['para_id','order','intent','serves','boundary','thin_claim','guardrails','lit_body',
              'proposition_chain','prose_gate','final_prose','prose_status']
CANON_PROP = ['prop_id','statement','role_in_paragraph','type','reason','evidence','numbers',
              'register_locks','depends_on']
REASONS = {
 '4.5-PARA1-a':"Primary survival evidence leads: the within-firm all-deals table establishes the run-up before the pooled binary form is brought in.",
 '4.5-PARA1-b':"Corroboration follows the table: the pooled forward logit restates the run-up in a different functional form and is placed after the within-firm primary.",
 '4.5-PARA2-a':"Primary timing evidence leads: the matched-universe round-trip on both clocks is stated before the by-payment-type split.",
 '4.5-PARA2-b':"The by-arm split follows the matched universe: it carries the cash-versus-stock asymmetry and so sits after the primary round-trip.",
 '4.5-PARA3-a':"Primary cash-concentration evidence leads: the formal Wald difference is stated first as the linear-restriction test, with the proposed cause alongside as the secondary element.",
 '4.5-PARA3-b':"Corroboration follows the Wald: the pooled cash-versus-stock logit restates the effect in binary form and is placed after the formal primary.",
}

J = json.load(open(SRC, encoding="utf-8"))

def reorder(d, order):
    extra = [k for k in d if k not in order]   # preserve any unexpected keys at end (none expected)
    return {**{k: d[k] for k in order if k in d}, **{k: d[k] for k in extra}}

# transform: insert reason, reorder prop keys, reorder para keys
for para in J["paragraphs"]:
    for p in para["proposition_chain"]:
        if "reason" not in p:
            p["reason"] = REASONS[p["prop_id"]]
    para["proposition_chain"] = [reorder(p, CANON_PROP) for p in para["proposition_chain"]]
J["paragraphs"] = [reorder(para, CANON_PARA) for para in J["paragraphs"]]

# ---- GATE on the (now canonical) J ----
SIBJ = json.load(open(SIB, encoding="utf-8"))
sib_para = list(SIBJ["paragraphs"][0])
sib_prop = list(SIBJ["paragraphs"][0]["proposition_chain"][0])
paras = J["paragraphs"]
props = [p for para in paras for p in para["proposition_chain"]]
fails=[]
def ck(n, ok, det=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}" + (f" -- {det}" if det and not ok else ""))
    if not ok: fails.append(n)

print("== §4.5 PLACEMENT GATE (on normalized MERGED)" + (" + WRITE" if WRITE else " dry-run") + " ==\n")
ck("paragraphs is list of 3", isinstance(paras,list) and len(paras)==3)
ck("6 props (2/para)", len(props)==6 and all(len(p['proposition_chain'])==2 for p in paras))
for i,para in enumerate(paras):
    ck(f"PARA{i+1} keys == 4.4 sibling", list(para)==sib_para, f"{list(para)}")
for p in props:
    ck(f"prop {p['prop_id']} keys == 4.4 sibling", list(p)==sib_prop, f"{list(p)}")

# every prop has a non-empty reason
ck("all 6 props have non-empty reason", all(p.get('reason','').strip() for p in props))

# all final_prose empty
ck("all final_prose empty", all(para.get('final_prose','')=='' for para in paras))

# depends_on resolve in LIVE ledgers
live=set()
for f in FIN.glob("section*.json"):
    if f.name==DST.name: continue
    d=json.load(open(f,encoding='utf-8')); pl=d.get('paragraphs',[])
    if isinstance(pl,dict):
        for _,pa in pl.items():
            for pr in pa.get('propositions',[]):
                if isinstance(pr,dict) and pr.get('prop_id'): live.add(pr['prop_id'])
    else:
        for pa in pl:
            for pr in pa.get('proposition_chain',[]):
                if pr.get('prop_id'): live.add(pr['prop_id'])
deps=sorted({d for p in props for d in p.get('depends_on',[])})
miss=[d for d in deps if d not in live]
ck("all depends_on resolve in LIVE", not miss, f"MISSING {miss}")

# honesty scan: statements + final_prose + the 6 authored reasons
FORBID=["suppress","dampen","strict specificity","detect "]
INTERP=["answer","p5.2","firms up","confirm","mechanism","contamination","feature"]
hv=[]
for p in props:
    for w in FORBID:
        if w in p['statement'].lower(): hv.append(f"{p['prop_id']} stmt:'{w}'")
    for w in FORBID+INTERP:
        if w in p['reason'].lower(): hv.append(f"{p['prop_id']} reason:'{w}'")
for para in paras:
    for w in FORBID:
        if w in para.get('final_prose','').lower(): hv.append(f"{para['para_id']} prose:'{w}'")
ck("0 honesty/interp violations (stmts + 6 reasons + prose)", not hv, str(hv))

# honest meta
ck("honest meta (_derived_from=PROPOSAL, no 74b7a0f8)", "PROPOSAL" in J.get('_derived_from','') and "74b7a0f8" not in J.get('_derived_from',''))
ck("prose_status=PROPOSAL all paras", all('PROPOSAL' in pa.get('prose_status','') for pa in paras))
ck("prose_gate locked all paras", all(pa['prose_gate']['all_supported'] is False and pa['prose_gate']['unlocked'] is False for pa in paras))

# numbers==.tex : stated GATE criterion. Frozen+verified-at-build. Mark honestly.
print("  [NOTE] numbers==.tex: VERIFIED-VERBATIM-AT-BUILD vs rob_4tables.tex (2026-06-23_162451) +")
print("         logit_fullcontrols_results.json; frozen in MERGED (caught CC-1 0.0447** at build). NOT re-parsed here.")

ck("destination is a NEW file (nothing overwritten)", not DST.exists())

print("\n" + "="*52)
if fails:
    print(f"GATE FAILED ({len(fails)}): {fails}\nNO WRITE.")
    sys.exit(1)
print("GATE PASSED.")
if WRITE:
    shutil.copy(SRC, SRC.with_suffix(".json.prereason.bak"))  # safety backup of pre-normalize
    json.dump(J, open(SRC,"w",encoding="utf-8"), indent=2, ensure_ascii=False)   # update source of truth
    json.dump(J, open(DST,"w",encoding="utf-8"), indent=2, ensure_ascii=False)   # place = identical copy
    # verify identical
    a=DST.read_text(encoding='utf-8'); b=SRC.read_text(encoding='utf-8')
    print(f"  MERGED updated + PLACED. MERGED==placed bytes: {a==b}")
    print(f"  -> {DST}")
else:
    print("Dry-run only. Re-run with WRITE.")
