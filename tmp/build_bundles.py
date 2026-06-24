"""
Sec-1 input builder: per-TYPE bundles = exemplar prose (by type) + OUR slim ledger projection.
Receipts STRIPPED. One bundle per type -> the exact input handed to an analysis agent.
Outputs: docs/papers/style_exemplars/bundles/<type>.json  + a size report.
"""
import json, re, glob
from pathlib import Path

ROOT   = Path(".").resolve()
EXTR   = ROOT/"docs/papers/style_exemplars/extracted"
LEDG   = ROOT/"docs/Thesis/rewrite"
OUT    = ROOT/"docs/papers/style_exemplars/bundles"
OUT.mkdir(parents=True, exist_ok=True)

VENUE = {"dwz":"working(FWP)","thewissen2024":"working(SSRN)","ragozzino2024":"journal(LRP)",
         "bushee2018":"JAR","lm2011":"JF","hollander2010":"JAR","harford1999":"JF",
         "bertrand_schoar2003":"QJE"}

# our ledger -> our type
OUR_TYPE = {
    "section_abstract":"abstract","section1":"intro","section2.1":"lit_review",
    "section2.2":"hypotheses","section2.3":"methods","section2.4":"methods","section2.5":"methods",
    "section3.1":"data","section3.2":"results","section3.3":"results","section3.4":"results",
    "section4.1":"results","section4.2":"results","section4.3":"results","section4.4":"results",
    "section5":"conclusion",
}
# exemplar type -> our-type bucket (discussion->conclusion; untitled=headless opening->intro)
EX_MAP = {"abstract":"abstract","intro":"intro","lit_review":"lit_review","hypotheses":"hypotheses",
          "data":"data","methods":"methods","results":"results","discussion":"conclusion",
          "conclusion":"conclusion","untitled":"intro"}
# consciously NOT bundled (logged in coverage report): appendix(tech notes), artifact(watermarks), other(empty dividers)

def words(s): return len(re.findall(r"\S+", s or ""))

def find_units(obj, out):
    if isinstance(obj, dict):
        if "final_prose" in obj: out.append(obj)
        for v in obj.values(): find_units(v, out)
    elif isinstance(obj, list):
        for v in obj: find_units(v, out)

def slim_unit(u, pid):
    props = [p.get("statement","") for p in (u.get("proposition_chain") or u.get("propositions") or []) if isinstance(p,dict)]
    naud  = u.get("number_audit")
    if not naud:  # fallback: gather numbers embedded in props
        nums=[]
        for p in (u.get("proposition_chain") or u.get("propositions") or []):
            if isinstance(p,dict): nums += p.get("numbers",[]) or []
        naud = [{"number":n} for n in nums]
    return {"para_id": u.get("para_id") or pid,
            "final_prose": u.get("final_prose",""),
            "propositions": props,
            "guardrails": u.get("guardrails") or u.get("register_locks") or [],
            "number_audit": naud}

# ---- exemplars by type (+ coverage tracking) ----
ex_by_type = {}
extracted_words = 0          # all prose words across all extracted sections
dropped_words = {}           # original-type -> words consciously NOT bundled
for f in sorted(glob.glob(str(EXTR/"*.json"))):
    if f.endswith(".tei.xml"): continue
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    key = d.get("key")
    if not key: continue
    for s in d.get("sections",[]):
        sw = sum(words(p) for p in s.get("paragraphs",[]))
        extracted_words += sw
        t = EX_MAP.get(s.get("type"))
        if not t or not s.get("paragraphs"):
            if sw: dropped_words[s.get("type") or "untitled"] = dropped_words.get(s.get("type") or "untitled",0)+sw
            continue
        ex_by_type.setdefault(t,[]).append(
            {"paper":key,"venue":VENUE.get(key,"?"),"head":s.get("head",""),"paragraphs":s["paragraphs"]})

# ---- our slim ledger by type ----
our_by_type = {}
for f in sorted(glob.glob(str(LEDG/"section*_paragraph_ledger.json"))):
    name = Path(f).name.replace("_paragraph_ledger.json","")
    t = OUR_TYPE.get(name)
    if not t: continue
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    units=[]; find_units(d, units)
    for i,u in enumerate(units):
        our_by_type.setdefault(t,[]).append({"ledger":name, **slim_unit(u, f"{name}-U{i+1}")})

# ---- write bundles + report ----
TYPES = ["abstract","intro","lit_review","hypotheses","data","methods","results","conclusion"]
print(f"{'type':<12}{'ex_paras':>9}{'ex_words':>9}{'our_units':>10}{'our_words':>10}{'~tokens':>9}")
print("-"*70)
for t in TYPES:
    ex = ex_by_type.get(t,[]); ours = our_by_type.get(t,[])
    exw = sum(words(p) for s in ex for p in s["paragraphs"])
    ouw = sum(words(u["final_prose"]) + sum(words(x) for x in u["propositions"]) for u in ours)
    bundle = {"type":t,"exemplars":ex,"ours":ours}
    (OUT/f"{t}.json").write_text(json.dumps(bundle,indent=2,ensure_ascii=False),encoding="utf-8")
    extra = sum(len(u["guardrails"])*6 + len(u["number_audit"])*8 for u in ours)
    tok = int((exw+ouw+extra)*1.3)
    print(f"{t:<12}{sum(len(s['paragraphs']) for s in ex):>9}{exw:>9}{len(ours):>10}{ouw:>10}{tok:>9,}")
print("-"*70)
print(f"wrote {len(TYPES)} bundles to {OUT}")

# ---- coverage report (no silent caps) ----
bundled_words = sum(words(p) for t in TYPES for s in ex_by_type.get(t,[]) for p in s["paragraphs"])
print(f"\nCOVERAGE: bundled {bundled_words:,} / extracted {extracted_words:,} exemplar prose words "
      f"= {bundled_words/max(1,extracted_words):.1%}")
if dropped_words:
    print("CONSCIOUSLY DROPPED (not bundled):")
    for t,w in sorted(dropped_words.items(), key=lambda x:-x[1]):
        print(f"  {t:<12} {w:>6,} words")
