# -*- coding: utf-8 -*-
"""Final input pre-flight for the one-shot prose harness. Deterministic run-breaker checks on the
16 _final ledgers: evidence coverage, depends_on resolution, prop_id collisions, citation collectability,
clean slate (final_prose empty), register-lock presence. Reports every issue; certifies NOTHING blindly."""
import json, re
from pathlib import Path
RW = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite")
FIN = RW/"_final"
BIB = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\uo-ethesis\bibliography\uo-ethesis.bib")

ledgers = {}
for f in sorted(FIN.glob("section*.json")):
    ledgers[f.stem.replace("_paragraph_ledger","")] = json.load(open(f, encoding="utf-8"))

def props_of(d):
    pl = d["paragraphs"]; items = list(pl.values()) if isinstance(pl, dict) else pl
    for pa in items:
        for pr in (pa.get("propositions", []) or pa.get("proposition_chain", [])):
            if isinstance(pr, dict):
                yield pa, pr

# collect global prop ids as (section, prop_id) and also the Format-B global ids
local_ids = {}   # (sec, pid)
global_ids = set()
for sec, d in ledgers.items():
    for pa, pr in props_of(d):
        pid = pr.get("prop_id")
        local_ids[(sec, pid)] = pr
        global_ids.add(pid)

issues = {}
def add(cat, msg): issues.setdefault(cat, []).append(msg)

# --- 1. EVIDENCE COVERAGE: every prop has >=1 anchor ---
ANCHORS = ["evidence","source","verification","anchor_2_1","relation_to_2_1","depends_on","numbers"]
for sec, d in ledgers.items():
    for pa, pr in props_of(d):
        if not any(pr.get(a) for a in ANCHORS):
            add("no-anchor", f"{sec}:{pr.get('prop_id')}")

# --- 2. DEPENDS_ON resolution (Format-B global ids) ---
for sec, d in ledgers.items():
    for pa, pr in props_of(d):
        for dep in (pr.get("depends_on") or []):
            # global id (has a dash/section prefix) -> must be in global set
            if dep not in global_ids:
                add("dangling-depends_on", f"{sec}:{pr.get('prop_id')} -> {dep}")

# --- 3. PROP_ID collisions (global keying danger) ---
from collections import Counter
gc = Counter(pid for (sec, pid) in local_ids)
dups = {pid: c for pid, c in gc.items() if c > 1}
if dups:
    add("prop_id-not-globally-unique", f"{len(dups)} ids repeat across sections (e.g. {list(dups)[:5]}) -> harness MUST key by (section,prop_id)")

# --- 4. CITATION collectability: every cite key -> a bibitem source ---
bibkeys = set()
if BIB.exists():
    bibkeys = set(re.findall(r"@\w+\{([^,]+),", BIB.read_text(encoding="utf-8", errors="ignore")))
# keys from push_2_1 BIBS + the 2 new §4.5 ones are also available
known_extra = {"bertrand_schoar2003","dye1985","harford1999","hollander2010","keown1981","verrecchia1983","shleifer_vishny2003","louis2004"}
avail = bibkeys | known_extra
used = set()
for sec, d in ledgers.items():
    for pa, pr in props_of(d):
        src = pr.get("source")
        if isinstance(src, dict) and src.get("key"): used.add(src["key"])
        for g in re.findall(r"\\cite[tp]\{([^}]*)\}", pr.get("statement","")):
            used |= {k.strip() for k in g.split(",")}
uncollectable = sorted(used - avail)
print(f"[cites] {len(used)} cite keys used; {len(bibkeys)} in .bib + {len(known_extra)} known; uncollectable: {len(uncollectable)}")
if uncollectable:
    add("uncollectable-cite", f"{uncollectable[:25]}")

# --- 5. CLEAN SLATE: all final_prose empty ---
nonempty = [f"{sec}:{pa.get('para_id') or pa.get('order')}" for sec,d in ledgers.items() for pa,_ in [(pa,None) for pa in (d['paragraphs'].values() if isinstance(d['paragraphs'],dict) else d['paragraphs'])] if pa.get("final_prose","").strip()]
if nonempty: add("prose-not-empty", f"{len(nonempty)} paragraphs already have prose")

# --- 6. REGISTER LOCKS present on result props (Format B) ---
for sec, d in ledgers.items():
    for pa, pr in props_of(d):
        if pr.get("type","").startswith("result") and not pr.get("register_locks"):
            add("result-without-register-lock", f"{sec}:{pr.get('prop_id')}")

# ---- report ----
print("\n"+"="*64)
print("INPUT PRE-FLIGHT — run-breaker checks")
print("="*64)
CHECKS = ["no-anchor","dangling-depends_on","prop_id-not-globally-unique","uncollectable-cite","prose-not-empty","result-without-register-lock"]
clean=True
for c in CHECKS:
    v = issues.get(c, [])
    status = "PASS" if not v else "FLAG"
    if v: clean=False
    print(f"  [{status}] {c}: {len(v)}")
    for m in v[:8]: print(f"          - {m}")
print("="*64)
print(f"props total: {len(local_ids)}")
print("VERDICT: INPUTS AIRTIGHT (0 run-breakers)" if clean else "VERDICT: ISSUES FOUND — fix before run")
