# -*- coding: utf-8 -*-
"""Phase 2 — the packer. Agent-free. Reads the 16 _final ledgers + the 8 v2 rulebooks and
emits one self-contained WRITING BRIEF per section: ordered props (with locked numbers,
register_locks, evidence), the section's type rulebook (verbatim principles), the honesty
floor, and the CLOSED allowed-number / allowed-cite sets the gates enforce. Output: briefs.json
(the .js workflow embeds this). No runtime file reads in the harness (lessons §6)."""
import json, re
from pathlib import Path
PH = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3")
FIN = PH/"docs/Thesis/rewrite/_final"
RB = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")/"docs/papers/style_exemplars/_rulebooks_v2"
OUT = PH/"docs/Thesis/rewrite/_phase5_harness/briefs.json"

SECTYPE = {  # section file stem -> rulebook type (Sina-defaulted; §2.3-2.5 = methods)
 "section_abstract":"abstract","section1":"intro","section2.1":"lit_review","section2.2":"hypotheses",
 "section2.3":"methods","section2.4":"methods","section2.5":"methods","section3.1":"data",
 "section3.2":"results","section3.3":"results","section3.4":"results",
 "section4.1":"results","section4.2":"results","section4.3":"results","section4.4":"results",
 "section4.5":"results","section5":"conclusion"}

COEF = re.compile(r'[+-]?\d?\.\d{3,4}\*{0,3}')   # coefficient-shaped tokens (incl. SEs/derived)
def tokens(pr):
    out=set()
    for ch in [pr.get("statement","")] + (pr.get("numbers",[]) if isinstance(pr.get("numbers"),list) else []):
        out |= set(COEF.findall(ch))
    return sorted(out)
def cites(pr):
    out=set()
    src=pr.get("source")
    if isinstance(src,dict) and src.get("key"): out.add(src["key"])
    for g in re.findall(r"\\cite[tp]\{([^}]*)\}", pr.get("statement","")):
        out |= {k.strip() for k in g.split(",")}
    return sorted(out)

TBL = re.compile(r'Table\s+(\d[\d.]*[A-Za-z]?)')   # hardcoded "Table 5.2" / "Table 1" / "Table 1."
LBL = re.compile(r'tab:[A-Za-z0-9_]+')             # LaTeX \label form (the robust reference)
# author's hardcoded table numbers -> the actual \label (content-matched from captions + 4.5 object-homing;
# robust to compile numbering). Every hardcoded "Table N" the writers see MUST be here (asserted in self-test).
TABLE_XWALK = {"1":"tab:summary_stats", "5.2":"tab:empire_building_did", "5.3":"tab:empire_drop_matched",
               "5.4":"tab:empire_drop_placebo", "5.5":"tab:empire_cashspec"}
def normval(s):   # mirror gates.mjs normVal: drop sign + leading zeros before the dot (".0391")
    return re.sub(r'^0+(?=\.)','', s.strip().lstrip('+-'))
def _blob(pr):
    return " ".join([pr.get("statement","")]
        + (pr.get("numbers",[]) if isinstance(pr.get("numbers"),list) else [])
        + ([json.dumps(pr.get("evidence"))] if pr.get("evidence") else []))
def prop_table_tokens(pr):
    """(tab:labels, hardcoded-numbers) referenced anywhere in this prop."""
    blob=_blob(pr)
    return set(LBL.findall(blob)), {n.rstrip('.') for n in TBL.findall(blob)}
def prop_labels(pr):
    """canonical tab:labels for this prop (direct labels + hardcoded numbers crosswalked)."""
    labs,nums=prop_table_tokens(pr)
    return labs | {TABLE_XWALK[n] for n in nums if n in TABLE_XWALK}
def number_table_pairs(pr):
    """normalized coefficient value -> set(tab:labels) the prop sources it from."""
    labs=prop_labels(pr); out={}
    if not labs: return out
    for s in [pr.get("statement","")] + (pr.get("numbers",[]) if isinstance(pr.get("numbers"),list) else []):
        if not isinstance(s,str): continue
        for tok in COEF.findall(s):
            out.setdefault(normval(tok.replace('*','')), set()).update(labs)
    return out

# rulebooks
rulebooks={}
for t in set(SECTYPE.values()):
    d=json.load(open(RB/f"{t}.json",encoding="utf-8"))
    rulebooks[t]=[{"device":p["device"],"principle":p["principle"]} for p in d["principles"]]

# ALL available bibitem keys (cite-gate allow-list: no \citep may render [?] / abort the compile;
# a wrong-but-defined cite is caught by the citation AUDIT lane, not falsely blocked by the gate).
BIB = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")/"docs/Thesis/uo-ethesis/bibliography/uo-ethesis.bib"
SUPP = PH/"docs/Thesis/_bibitems_supplement.tex"
bibkeys=set()
if BIB.exists(): bibkeys |= set(re.findall(r'@\w+\{([^,]+),', BIB.read_text(encoding="utf-8",errors="ignore")))
if SUPP.exists(): bibkeys |= set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}', SUPP.read_text(encoding="utf-8")))
bibkeys |= {"bertrand_schoar2003","dye1985","harford1999","hollander2010","keown1981","verrecchia1983",
            "shleifer_vishny2003","louis2004","matsumoto2011","lm2011"}   # push_2_1 + §4.5 known set
ALLOWED_CITES_ALL=sorted(bibkeys)

briefs=[]
order = list(SECTYPE)
for i,stem in enumerate(order):
    f=FIN/f"{stem}_paragraph_ledger.json"
    d=json.load(open(f,encoding="utf-8"))
    typ=SECTYPE[stem]
    pl=d["paragraphs"]; items=list(pl.items()) if isinstance(pl,dict) else [(p.get("para_id"),p) for p in pl]
    paras=[]; sec_map={}; sec_labels=set(); sec_nums=set()
    for pid,pa in items:
        props=pa.get("propositions") or pa.get("proposition_chain") or []
        ptoks=set(); pcites=set(); plist=[]
        for pr in props:
            if not isinstance(pr,dict): continue
            tk=tokens(pr); ct=cites(pr); ptoks|=set(tk); pcites|=set(ct)
            for v,ts in number_table_pairs(pr).items(): sec_map.setdefault(v,set()).update(ts)
            _l,_n=prop_table_tokens(pr); sec_labels|=prop_labels(pr); sec_nums|={n for n in _n if n in TABLE_XWALK}
            plist.append({
                "prop_id":pr.get("prop_id"),
                "statement":pr.get("statement"),
                "numbers":pr.get("numbers",[]) if isinstance(pr.get("numbers"),list) else [],
                "register_locks":pr.get("register_locks",[]),
                "evidence":pr.get("evidence") or pr.get("source"),
                "reason":pr.get("reason"),
                "verification":pr.get("verification"),     # theory props carry the NLM verbatim quotes
                "signature": (tk[0] if tk else None),
            })
        ib=json.dumps(pa.get("intent"))   # the paragraph intent is shown to the writer -> harvest its table labels too
        sec_labels|=set(LBL.findall(ib))
        for n in {x.rstrip('.') for x in TBL.findall(ib)}:
            if n in TABLE_XWALK: sec_labels.add(TABLE_XWALK[n]); sec_nums.add(n)
        paras.append({
            "para_id":pid,
            "order":pa.get("order"),
            "intent":pa.get("intent"),
            "thin_claim":pa.get("thin_claim"),
            "serves":pa.get("serves"),
            "guardrails":pa.get("guardrails"),
            "props":plist,
            "allowed_tokens":sorted(ptoks),     # gate: number-trace
            "allowed_cites":sorted(pcites),     # gate: cite-whitelist
        })
    sec_tokens=sorted(set().union(*[set(pa["allowed_tokens"]) for pa in paras])) if paras else []
    briefs.append({
        "section":stem.replace("section_","").replace("section",""),
        "stem":stem, "type":typ, "title":d.get("title"),
        "rulebook":rulebooks[typ],
        "allowed_cites_all":ALLOWED_CITES_ALL,
        "allowed_tokens_all":sec_tokens,   # SECTION-level number set (back-references across paragraphs are legit)
        "number_table_map_all":{k:sorted(v) for k,v in sorted(sec_map.items())},  # gate 1b: value -> allowed tab:labels
        "table_labels":sorted(sec_labels),                              # tables this section cites (render as \ref{label})
        "table_xwalk":{n:TABLE_XWALK[n] for n in sorted(sec_nums)},     # writer crosswalk: hardcoded "Table N" -> \ref{label}
        "bright_lines":d.get("_bright_lines") or d.get("bright_lines") or [],
        "register_global":(d.get("section_context") or {}).get("register_global") if isinstance(d.get("section_context"),dict) else None,
        "paragraphs":paras,
    })

# seams: give each section the neighbours' thin_claims (adjacent context, NOT prior prose)
for i,b in enumerate(briefs):
    b["seam_prev"]=[p.get("thin_claim") for p in briefs[i-1]["paragraphs"]][-1:] if i>0 else []
    b["seam_next"]=[p.get("thin_claim") for p in briefs[i+1]["paragraphs"]][:1] if i+1<len(briefs) else []

json.dump(briefs, open(OUT,"w",encoding="utf-8"), indent=1, ensure_ascii=True)  # ASCII for .js embed (lessons §6)

# ---- test: every brief complete ----
fails=[]
def ck(n,ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}");  fails.append(n) if not ok else None
print("== packer self-test ==")
ck("17 briefs (abstract + 16 numbered)", len(briefs)==17)
ck("every brief has a non-empty rulebook", all(b["rulebook"] for b in briefs))
ck("every brief has paragraphs", all(b["paragraphs"] for b in briefs))
# completeness: NO paragraph where a coefficient actually appears but allowed_tokens is empty
# (design/setup paragraphs legitimately have no coefficients -> not required to have tokens)
# space-join fields so a trailing "." + a 4-digit YEAR (e.g. "2002") can't fuse into a false ".2002"
def has_coef(pa): return any(COEF.search(" ".join([p.get("statement") or ""] + p.get("numbers",[]))) for p in pa["props"])
ck("no coefficient dropped (every numeric paragraph has allowed_tokens)", all(
    pa["allowed_tokens"] for b in briefs for pa in b["paragraphs"] if has_coef(pa)))
ck("ASCII-clean (embeddable)", all(ord(c)<128 for c in OUT.read_text(encoding="utf-8")))
m45=next((b["number_table_map_all"] for b in briefs if b["stem"]=="section4.5"),{})
ck("number->label map populated (4.5 .0391 -> tab:empire_building_did)", "tab:empire_building_did" in m45.get(".0391",[]))
# every hardcoded "Table N" the writers see (statement+numbers) must be crosswalkable -> the \ref instruction can map it
allnums=set()
for b in briefs:
    for pa in b["paragraphs"]:
        allnums|={n.rstrip('.') for n in TBL.findall(json.dumps(pa.get("intent")))}   # writers see intent too
        for pr in pa["props"]:
            allnums|={n.rstrip('.') for n in TBL.findall(" ".join([pr.get("statement") or ""]+(pr.get("numbers") or [])))}
ck("every hardcoded Table N (statement+numbers+intent) is in the crosswalk (no unfixable block)", allnums <= set(TABLE_XWALK))
nprops=sum(len(pa["props"]) for b in briefs for pa in b["paragraphs"])
print(f"  briefs:{len(briefs)}  paragraphs:{sum(len(b['paragraphs']) for b in briefs)}  props:{nprops}")
print("PACKER OK -> briefs.json" if not fails else f"FAILED {fails}")
