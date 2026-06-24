"""
DWZ extraction pilot — gates the multi-tool stack before wiring all 8 papers.
Stack: GROBID(CRF) = structure;  PyMuPDF/pdftotext/pdfplumber = coverage cross-check;  regex = glyph scan.
Run AFTER the GROBID container is up on :8070.

Outputs:
  - docs/papers/style_exemplars/extracted/dwz.json
  - a PILOT REPORT to stdout (sections, head->type map, coverage, glyph flags) for human eyeball.
"""
import json, re, sys, time, subprocess
from pathlib import Path

import requests
import fitz                      # PyMuPDF
from lxml import etree

ROOT   = Path(".").resolve()
PDF    = ROOT / "docs/papers/style_exemplars/FWP_2017_02_v2.pdf"
OUTDIR = ROOT / "docs/papers/style_exemplars/extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)
GROBID = "http://localhost:8070"
TEI    = {"t": "http://www.tei-c.org/ns/1.0"}

# ---------- helpers ----------
def wait_for_grobid(timeout=90):
    for _ in range(timeout):
        try:
            if requests.get(GROBID + "/api/isalive", timeout=3).text.strip() == "true":
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def grobid_fulltext(pdf):
    with open(pdf, "rb") as f:
        r = requests.post(
            GROBID + "/api/processFulltextDocument",
            files={"input": (pdf.name, f, "application/pdf")},
            data={"consolidateHeader": "0", "consolidateCitations": "0", "segmentSentences": "0"},
            timeout=300,
        )
    r.raise_for_status()
    return r.text

def _txt(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()

def parse_tei(xml):
    root = etree.fromstring(xml.encode("utf-8"))
    t = root.find(".//t:titleStmt/t:title", TEI)
    title = _txt(t) if t is not None else None
    secs = []
    abs = root.find(".//t:profileDesc/t:abstract", TEI)
    if abs is not None:
        ap = [_txt(p) for p in abs.findall(".//t:p", TEI) if _txt(p)]
        if ap:
            secs.append({"head": "Abstract", "paragraphs": ap})
    body = root.find(".//t:text/t:body", TEI)
    if body is not None:
        for div in body.findall("t:div", TEI):
            h = div.find("t:head", TEI)
            head = _txt(h) if h is not None else ""
            paras = [_txt(p) for p in div.findall("t:p", TEI) if _txt(p)]
            if paras or head:
                secs.append({"head": head, "paragraphs": paras})
    return title, secs

# heading -> coarse type (order matters; first match wins). Rough on purpose: human eyeballs the map.
TYPE_RULES = [
    ("abstract",   r"abstract"),
    ("intro",      r"introduc"),
    ("hypotheses", r"hypothes|predict"),
    ("lit_review", r"literature|related work|prior (research|work|literature)|background|theor"),
    ("data",       r"\bdata\b|sample|descriptive|summary stat|variable construction"),
    ("methods",    r"method|model|empirical (strateg|design|specif)|estimat|identif|research design|measur|variable"),
    ("results",    r"result|finding|evidence|main analys|empirical (result|analys)|robust|additional|test"),
    ("discussion", r"discuss|implicat|mechanism|interpret"),
    ("conclusion", r"conclu"),
]
def classify(head):
    h = head.lower()
    for typ, pat in TYPE_RULES:
        if re.search(pat, h):
            return typ
    return "other"

def norm_tokens(t):
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", t.lower()).split() if w]

def glyph_flags(t):
    return {"cid": len(re.findall(r"\(cid:", t)), "ufffd": t.count("�")}

def raw_pymupdf(pdf):
    doc = fitz.open(pdf)
    return " ".join(p.get_text("text") for p in doc), doc.page_count

# ---------- run ----------
def main():
    if not PDF.exists():
        sys.exit(f"PDF not found: {PDF}")
    if not wait_for_grobid():
        sys.exit("GROBID not alive on :8070 — start the container first.")

    xml = grobid_fulltext(PDF)
    (OUTDIR / "dwz.tei.xml").write_text(xml, encoding="utf-8")
    title, secs = parse_tei(xml)

    for s in secs:
        s["type"] = classify(s["head"])

    grobid_text = " ".join(p for s in secs for p in s["paragraphs"])
    raw_text, npages = raw_pymupdf(PDF)

    g_tok = norm_tokens(grobid_text)
    r_tok = norm_tokens(raw_text)
    r_set = set(r_tok)
    covered = sum(1 for w in set(g_tok) if w in r_set)
    coverage = round(len(g_tok) / max(1, len(r_tok)), 3)          # body words / all raw words
    vocab_overlap = round(covered / max(1, len(set(g_tok))), 3)   # grobid vocab found in raw

    verify = {
        "pages": npages,
        "grobid_body_words": len(g_tok),
        "raw_pymupdf_words": len(r_tok),
        "coverage_ratio_body_over_raw": coverage,
        "grobid_vocab_in_raw": vocab_overlap,
        "glyph_grobid": glyph_flags(grobid_text),
        "glyph_raw": glyph_flags(raw_text),
    }
    doc = {"key": "dwz", "title": title, "source_pdf": str(PDF.relative_to(ROOT)),
           "sections": secs, "verify": verify}
    (OUTDIR / "dwz.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------- report ----------
    print("=" * 72)
    print("DWZ EXTRACTION PILOT REPORT")
    print("=" * 72)
    print(f"title (GROBID): {title}")
    print(f"pages={npages}  sections={len(secs)}")
    print(f"\n{'#':>2}  {'TYPE':<11} {'#par':>4} {'#words':>7}  HEAD")
    print("-" * 72)
    for i, s in enumerate(secs):
        w = sum(len(norm_tokens(p)) for p in s["paragraphs"])
        head = (s["head"][:46] or "(no head)")
        print(f"{i:>2}  {s['type']:<11} {len(s['paragraphs']):>4} {w:>7}  {head}")
    print("-" * 72)
    print(f"coverage (grobid body words / raw words) = {coverage}   "
          f"[<<1 expected: raw incl. refs/heads/footnotes]")
    print(f"grobid vocab found in raw                 = {vocab_overlap}   [want ~1.0]")
    print(f"glyph flags  grobid={verify['glyph_grobid']}  raw={verify['glyph_raw']}")
    empties = [i for i, s in enumerate(secs) if not s["paragraphs"]]
    print(f"empty-paragraph sections: {empties if empties else 'none'}")
    print(f"\nwrote {OUTDIR/'dwz.json'}")
    print("EYEBALL: (1) does TYPE map look right?  (2) any real section missing/empty?  "
          "(3) vocab_in_raw ~1.0 (no scramble)?  (4) glyphs clean?")

if __name__ == "__main__":
    main()
