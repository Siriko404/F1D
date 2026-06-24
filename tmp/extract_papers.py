"""
Extract all 8 style-exemplar PDFs -> one JSON each (GROBID structure + PyMuPDF coverage/glyph cross-check).
GROBID must be running on :8070. Writes per-paper JSON + a consolidated heading->type map for human review.
"""
import json, re, time
from pathlib import Path
import requests, fitz
from lxml import etree

ROOT   = Path(".").resolve()
SRC    = ROOT / "docs/papers/style_exemplars"
OUTDIR = SRC / "extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)
GROBID = "http://localhost:8070"
TEI    = {"t": "http://www.tei-c.org/ns/1.0"}

# key -> filename substring (robust to spaces/unicode)
PAPERS = [
    ("dwz",                "FWP_2017_02_v2"),
    ("thewissen2024",      "ssrn-4900453"),
    ("ragozzino2024",      "S0024630123001000"),
    ("bushee2018",         "BUSHEE"),
    ("lm2011",             "LOUGHRAN"),
    ("hollander2010",      "HOLLANDER"),
    ("harford1999",        "Harford"),
    ("bertrand_schoar2003","118-4-1169"),
]

TYPE_RULES = [
    ("abstract",   r"abstract"),
    ("intro",      r"introduc"),
    ("hypotheses", r"hypothes|predict|^h\d|development of|as a matter of"),
    ("lit_review", r"literature|related (work|research)|prior (research|work|literature)|background|theor|information economics|why should|managers? matter"),
    ("data",       r"\bdata\b|sample|transcript|word ?list|uncertainty words|variable construc|descriptive|summary statistic|measurement|\bmeasure|parsing|term weight|fog index|readability|press release|collection of|earnings press"),
    ("methods",    r"method|model|empirical (strateg|design|specif|approach)|estimat|identif|research design|overview of the approach|intuitive argument|specification|textual analysis|propensity|entropy|instrumental variable|control function|matching|monte carlo|placebo|derivation|perl|technical note|experimental design"),
    ("results",    r"result|finding|evidence|main analys|empirical (result|analys)|robust|additional|\btest\b|correlat|affect|response|firm value|\breturns|earnings response|bidder|merger|acquisition|cash[- ]rich|cash (holding|stockpil)|stockpil|tone management|disclosure|logit|logistic|probit|regression|univariate|multivariate|volatilit|guidance|validation|operating performance|market reaction|class action|unexpected earnings|moderat|deal size|firm performance|monitoring|sorting|magnitude|fixed effect|composition"),
    ("discussion", r"discuss|implicat|mechanism|interpret|contribution"),
    ("conclusion", r"conclu"),
    ("appendix",   r"appendix|^ia[\s.\-]|internet appendix"),
]
# strip leading enumerators: "II.", "IV.D.", "A.2.", "3." before keyword match
ENUM = re.compile(r"^\s*(?:[ivx]+|[a-z]|\d+)(?:\.\d+|\.[a-z])*\.?\s+", re.I)
ARTIFACT = [
    r"p\s*r\s*e\s*p\s*r\s*i\s*n\s*t",        # spaced-out watermark "Preprint..."
    r"p\s*e\s*e\s*r\s*\s*r\s*e\s*v\s*i\s*e\s*w",
    r"^\W*\d+\W*$",                            # pure page-number heading "12"
    r"^~\s*\d",                               # "~1!" figure/table note artifact
    r"^[a-z][a-z .'\-]+(\([^)]*\))?\s*:$",    # speaker label "Eli Lustgarten:" / "Ron Brown (CEO):"
]
def classify(head):
    h0 = head.strip()
    if not h0:
        return "untitled"
    low = h0.lower()
    for pat in ARTIFACT:
        if re.search(pat, low):
            return "artifact"
    h = ENUM.sub("", h0).lower().strip()
    for typ, pat in TYPE_RULES:
        if re.search(pat, h):
            return typ
    return "other"

# deterministic per-paper head-substring overrides (head.lower() contains key -> type).
# resolves the residual 'other' by human judgment, written straight into the JSON on run.
OVERRIDES = {
    "thewissen2024": {
        "stock-for-stock m&as and earnings management": "lit_review",
        "endogeneity concerns": "methods",
        "pseudo-event study": "methods",
    },
    "ragozzino2024": {"the role of earnings calls for information delivery": "lit_review"},
    "bushee2018": {
        "linguistic complexity and information asymmetry": "results",
        "latent components of linguistic complexity and earnings": "results",
        "effect of obfuscation in linguistic complexity": "results",
    },
    "lm2011": {"d. variables": "data", "10-b5 filings and material weakness": "results"},
    "hollander2010": {
        "proprietary information": "methods", "litigation risk": "methods",
        "control variables": "methods", "company size": "methods", "company age": "methods",
        "analyst participation and involvement": "methods", "institutional ownership": "methods",
        "no recent ceo change": "methods", "irregular items": "methods",
        "issuance of debt or equity": "methods", "wouldn't obfuscation better serve": "results",
        "uncertainty of information arrival": "methods",
    },
    "harford1999": {"table v analysis of bids": "results", "further tests": "results"},
    "bertrand_schoar2003": {
        "management styles": "results", "governance, compensation, and style": "results",
        "observable managerial characteristics": "results",
    },
}
def apply_override(key, head, auto):
    hl = head.lower()
    for sub, ty in OVERRIDES.get(key, {}).items():
        if sub in hl:
            return ty
    return auto

def wait_grobid(timeout=90):
    for _ in range(timeout):
        try:
            if requests.get(GROBID+"/api/isalive", timeout=3).text.strip()=="true": return True
        except Exception: pass
        time.sleep(1)
    return False

def grobid(pdf):
    with open(pdf,"rb") as f:
        r = requests.post(GROBID+"/api/processFulltextDocument",
            files={"input":(pdf.name,f,"application/pdf")},
            data={"consolidateHeader":"0","consolidateCitations":"0","segmentSentences":"0"},
            timeout=300)
    r.raise_for_status(); return r.text

def _t(el): return re.sub(r"\s+"," ","".join(el.itertext())).strip()

def parse(xml):
    root = etree.fromstring(xml.encode("utf-8"))
    t = root.find(".//t:titleStmt/t:title", TEI)
    title = _t(t) if t is not None else None
    secs=[]
    abs = root.find(".//t:profileDesc/t:abstract", TEI)
    if abs is not None:
        ap=[_t(p) for p in abs.findall(".//t:p",TEI) if _t(p)]
        if ap: secs.append({"head":"Abstract","paragraphs":ap})
    body = root.find(".//t:text/t:body", TEI)
    if body is not None:
        for div in body.findall("t:div",TEI):
            h=div.find("t:head",TEI); head=_t(h) if h is not None else ""
            paras=[_t(p) for p in div.findall("t:p",TEI) if _t(p)]
            if paras or head: secs.append({"head":head,"paragraphs":paras})
    return title, secs

def toks(s): return [w for w in re.sub(r"[^a-z0-9 ]"," ",s.lower()).split() if w]
def glyphs(s): return {"cid":len(re.findall(r"\(cid:",s)),"ufffd":s.count("�")}

def find_pdf(sub):
    for p in SRC.glob("*.pdf"):
        if sub.lower() in p.name.lower(): return p
    return None

def main():
    assert wait_grobid(), "GROBID not alive on :8070"
    summary=[]; maprows=[]
    for key, sub in PAPERS:
        pdf = find_pdf(sub)
        if not pdf:
            summary.append((key,"MISSING",0,0,0,0,0)); continue
        try:
            xml = grobid(pdf)
            (OUTDIR/f"{key}.tei.xml").write_text(xml,encoding="utf-8")
            title, secs = parse(xml)
            for i,s in enumerate(secs):
                s["type"]=apply_override(key, s["head"], classify(s["head"]))
                w=sum(len(toks(p)) for p in s["paragraphs"])
                maprows.append((key,i,s["type"],len(s["paragraphs"]),w,s["head"][:60]))
            gtext=" ".join(p for s in secs for p in s["paragraphs"])
            doc=fitz.open(pdf); raw=" ".join(pg.get_text("text") for pg in doc)
            gt,rt=toks(gtext),toks(raw); rset=set(rt)
            cov=round(len(gt)/max(1,len(rt)),3)
            voc=round(sum(1 for w in set(gt) if w in rset)/max(1,len(set(gt))),3)
            verify={"pages":doc.page_count,"grobid_body_words":len(gt),"raw_words":len(rt),
                    "coverage":cov,"vocab_in_raw":voc,"glyph_grobid":glyphs(gtext),"glyph_raw":glyphs(raw)}
            (OUTDIR/f"{key}.json").write_text(json.dumps(
                {"key":key,"title":title,"source_pdf":pdf.name,"sections":secs,"verify":verify},
                indent=2,ensure_ascii=False),encoding="utf-8")
            nother=sum(1 for s in secs if s["type"]=="other")
            summary.append((key,doc.page_count,len(secs),cov,voc,
                            verify["glyph_grobid"]["cid"]+verify["glyph_grobid"]["ufffd"],nother))
        except Exception as e:
            summary.append((key,f"ERR {e}",0,0,0,0,0))

    # consolidated map file (full, for eyeball)
    lines=["key\tidx\tauto_type\tnpar\tnwords\thead"]
    lines+= ["\t".join(map(str,r)) for r in maprows]
    (OUTDIR/"_headings_map.tsv").write_text("\n".join(lines),encoding="utf-8")

    print("="*80); print("EXTRACTION SUMMARY (all 8)"); print("="*80)
    print(f"{'key':<20}{'pages':>6}{'secs':>5}{'cov':>6}{'vocab':>6}{'glyph':>6}{'#other':>7}")
    print("-"*80)
    for k,pg,sc,cov,voc,gl,no in summary:
        if isinstance(pg,int):
            print(f"{k:<20}{pg:>6}{sc:>5}{cov:>6}{voc:>6}{gl:>6}{no:>7}")
        else:
            print(f"{k:<20}  {pg}")
    print("-"*80)
    print(f"wrote {len(summary)} JSONs + _headings_map.tsv to {OUTDIR}")
    # show the 'other' headings (the ones needing a human type decision)
    print("\n'OTHER' HEADINGS NEEDING A TYPE (eyeball these):")
    for k,i,ty,npar,w,head in maprows:
        if ty=="other" and (npar>0 or w>0):
            print(f"  {k:<18} [{i:>2}] ({w:>4}w) {head}")

if __name__=="__main__":
    main()
