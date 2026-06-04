"""
Round 1b 3-AI cross-check: paragraph-level reconciliation.

Inputs:
- tmp/process_prompt_01b_paragraph_reverify_2026_05_26.md (NLM + Claude-web responses)
- tmp/campello_paragraph_index_2026_05_26.md (anchor enumeration of §IV paragraphs)
- PyMuPDF anchor pages 13-20

Goal: for each of the 9 PARA_NN targets, determine which anchor paragraph
each AI returned, then mark LOCKED (both agree on same anchor paragraph
with matching verbatim) vs DRIFT (AIs returned different paragraphs).

Output: tmp/campello_para_crosscheck_v1_2026_05_26.md
"""
import re
import unicodedata
import difflib
from pathlib import Path

PROMPT_FILE = Path("tmp/process_prompt_01b_paragraph_reverify_2026_05_26.md")
EXTRACT_DIR = Path("tmp/campello_pdf_extract")
OUT = Path("tmp/campello_para_crosscheck_v1_2026_05_26.md")

def normalize(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in [("'", "'"), ("'", "'"), ('"', '"'), ('"', '"'),
                 ("–", "-"), ("—", "-"), ("\xa0", " ")]:
        s = s.replace(a, b)
    s = re.sub(r"-\s+", "-", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def strip_math_lite(s):
    """Light math strip for content matching — drop common Greek + subscripts."""
    s = re.sub(r"\b(β_?i\^?(\{?UK\}?)?|β_?i|βUK|σ_?ε|θ|α_?i|ε_?it)\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\bvol\([^)]+\)", "", s)
    s = re.sub(r"\([0-9]{1,2}\)", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Parse PARA blocks
PARA_RE = re.compile(
    r"PARA_(\d+):\s*\n"
    r"(.*?)(?=\nPARA_\d+:|\nTOTAL_PARAGRAPHS|\n/{3,}|\Z)",
    re.DOTALL,
)
FIELD_RE = re.compile(r"^\s*(\w+):\s*(.*?)(?=\n\s*\w+:|\Z)", re.DOTALL | re.MULTILINE)

def parse_para_blocks(section_text):
    blocks = []
    for m in PARA_RE.finditer(section_text):
        no = int(m.group(1))
        body = m.group(2)
        fields = {}
        # Custom extraction because YAML-ish
        fw = re.search(r"first_word_verbatim:\s*\"([^\"]*)\"", body)
        lw = re.search(r"last_word_verbatim:\s*\"([^\"]*)\"", body)
        section = re.search(r"section:\s*(.+?)\s*\n", body)
        ppos = re.search(r"paragraph_position:\s*(\d+)", body)
        page = re.search(r"page:\s*(.+?)\s*\n", body)
        # paragraph_text_verbatim is a block; grab everything between `|` and the next field
        ptext = re.search(
            r"paragraph_text_verbatim:\s*\|\s*\n(.*?)(?=\n\s*contains_equation:|\n\s*contains_footnote_anchor:|\Z)",
            body, re.DOTALL
        )
        blocks.append({
            "para_no": no,
            "section": section.group(1).strip() if section else "",
            "para_position": int(ppos.group(1)) if ppos else 0,
            "page": page.group(1).strip() if page else "",
            "first_word": fw.group(1) if fw else "",
            "last_word": lw.group(1) if lw else "",
            "paragraph_text": (ptext.group(1).strip() if ptext else "").strip(),
        })
    return blocks

text = PROMPT_FILE.read_text(encoding="utf-8")
chunks = re.split(r"/{5,}\s*\n", text)
nlm_text = ""
cw_text = ""
for i, c in enumerate(chunks):
    s = c.strip()
    # Match label-only chunks (not the prompt text that mentions "NLM" in its body)
    if s == "NLM" and i + 1 < len(chunks):
        nlm_text = chunks[i + 1]
    elif re.match(r"^Claude\s*web\s*$", s, re.IGNORECASE) and i + 1 < len(chunks):
        cw_text = chunks[i + 1]
nlm_paras = parse_para_blocks(nlm_text)
cw_paras = parse_para_blocks(cw_text)
print(f"NLM PARAs parsed: {len(nlm_paras)}")
print(f"Claude-web PARAs parsed: {len(cw_paras)}")

# Load anchor paragraph index
def load_anchor_paragraphs():
    """Read the index md, parse table rows. Also load full body text for each
    paragraph by re-extracting from PyMuPDF."""
    import fitz
    doc = fitz.open(Path("docs/papers/campello_etal_2022_brexit_jfqa.pdf"))
    anchor_paras = []
    # Re-enumerate (same logic) to get full block text
    for pdf_page in range(13, 21):
        page = doc[pdf_page - 1]
        for b in sorted(page.get_text("blocks"), key=lambda x: (x[1], x[0])):
            t = re.sub(r"\s+", " ", b[4]).strip()
            if not t:
                continue
            if "https://doi.org" in t or "Cambridge University" in t:
                continue
            if re.match(r"^\d+\s+Journal", t):
                continue
            if re.match(r"^\d+$", t):
                continue
            if re.match(r"^\d{1,3}[A-Z]", t):
                continue  # footnote body
            if re.match(r"^IV\.\s", t) and len(t) < 60:
                continue
            if re.match(r"^[A-Z]\.\s+[A-Z]", t) and len(t) < 60:
                continue
            if re.match(r"^\d+\.\s+[A-Z]", t) and len(t) < 80:
                continue
            if len(t) < 80 or len(t.split()) < 8:
                continue
            anchor_paras.append({
                "pdf_page": pdf_page,
                "printed_page": pdf_page + 3177,
                "text": t,
                "norm": normalize(t),
            })
    doc.close()
    return anchor_paras

anchor = load_anchor_paragraphs()
print(f"Anchor paragraphs: {len(anchor)}")

# Map each AI's PARA to its best-matching anchor paragraph (by content overlap)
def map_to_anchor(para_text):
    if not para_text or len(para_text) < 30:
        return (None, 0.0)
    qnorm = normalize(strip_math_lite(para_text))[:200]  # first 200 chars
    best = (None, 0.0)
    for i, a in enumerate(anchor):
        a_search = strip_math_lite(a["norm"])
        if not a_search:
            continue
        # Try substring first
        if qnorm[:80] in a_search:
            return (i, 1.0)
        sm = difflib.SequenceMatcher(None, qnorm, a_search, autojunk=False)
        m = sm.find_longest_match(0, len(qnorm), 0, len(a_search))
        ratio = m.size / max(1, len(qnorm))
        if ratio > best[1]:
            best = (i, ratio)
    return best

results = []
for i in range(1, 10):
    nlm_p = next((p for p in nlm_paras if p["para_no"] == i), None)
    cw_p = next((p for p in cw_paras if p["para_no"] == i), None)
    nlm_anchor_idx, nlm_ratio = map_to_anchor(nlm_p["paragraph_text"]) if nlm_p else (None, 0.0)
    cw_anchor_idx, cw_ratio = map_to_anchor(cw_p["paragraph_text"]) if cw_p else (None, 0.0)
    same_anchor = nlm_anchor_idx is not None and nlm_anchor_idx == cw_anchor_idx
    nlm_incomplete = nlm_p and "INCOMPLETE" in nlm_p.get("paragraph_text", "")
    if same_anchor:
        status = "LOCKED"
    elif nlm_incomplete and cw_anchor_idx is not None:
        status = "CW_ONLY"
    elif nlm_anchor_idx is not None and cw_anchor_idx is not None:
        status = "DRIFT"
    else:
        status = "UNRESOLVED"
    results.append({
        "para_no": i,
        "nlm": nlm_p, "cw": cw_p,
        "nlm_anchor": nlm_anchor_idx, "nlm_ratio": nlm_ratio,
        "cw_anchor": cw_anchor_idx, "cw_ratio": cw_ratio,
        "status": status,
    })

# Render
lines = [
    "# Campello §IV — Round 1b Paragraph-level Cross-Check",
    "",
    f"Generated: 2026-05-26 by `tmp/para_crosscheck_v1.py`",
    f"Sources: NLM + Claude-web responses in `process_prompt_01b_paragraph_reverify_2026_05_26.md`; anchor from `enumerate_section_paragraphs.py`",
    "",
    "## Summary",
    "| Status | Count | Meaning |",
    "|---|---|---|",
    f"| LOCKED | {sum(1 for r in results if r['status']=='LOCKED')} | NLM + Claude-web returned the SAME anchor paragraph with matching content |",
    f"| DRIFT | {sum(1 for r in results if r['status']=='DRIFT')} | NLM + Claude-web returned DIFFERENT anchor paragraphs (paragraph-numbering disagreement; both real paragraphs from the paper, just labeled differently) |",
    f"| CW_ONLY | {sum(1 for r in results if r['status']=='CW_ONLY')} | NLM returned INCOMPLETE/mojibake; Claude-web returned a real paragraph |",
    f"| UNRESOLVED | {sum(1 for r in results if r['status']=='UNRESOLVED')} | Couldn't map either AI's response to the anchor |",
    "",
    "## Per-PARA mapping table",
    "",
    "| PARA | NLM section/¶ | NLM→anchor | CW section/¶ | CW→anchor | Status |",
    "|---|---|---|---|---|---|",
]
for r in results:
    n_sec = f"{r['nlm']['section']}/¶{r['nlm']['para_position']}" if r['nlm'] else "—"
    c_sec = f"{r['cw']['section']}/¶{r['cw']['para_position']}" if r['cw'] else "—"
    n_anch = f"a[{r['nlm_anchor']}] (r={r['nlm_ratio']:.2f})" if r['nlm_anchor'] is not None else "—"
    c_anch = f"a[{r['cw_anchor']}] (r={r['cw_ratio']:.2f})" if r['cw_anchor'] is not None else "—"
    lines.append(f"| {r['para_no']:02d} | {n_sec} | {n_anch} | {c_sec} | {c_anch} | {r['status']} |")

lines += [
    "",
    "## Anchor paragraph reference (first 8 words by index)",
    "",
]
for i, a in enumerate(anchor):
    f8 = " ".join(a["text"].split()[:10])
    lines.append(f"- **a[{i}]** (pdf {a['pdf_page']}, printed {a['printed_page']}): {f8}…")

lines += [
    "",
    "## DRIFT detail",
    "",
]
for r in results:
    if r["status"] != "DRIFT":
        continue
    lines.append(f"### PARA_{r['para_no']:02d} — DRIFT")
    lines.append(f"- NLM said: section {r['nlm']['section']}, ¶{r['nlm']['para_position']}, page {r['nlm']['page']}")
    lines.append(f"  - First words: \"{r['nlm']['first_word']}\"… → maps to anchor a[{r['nlm_anchor']}]")
    lines.append(f"- Claude-web said: section {r['cw']['section']}, ¶{r['cw']['para_position']}, page {r['cw']['page']}")
    lines.append(f"  - First words: \"{r['cw']['first_word']}\"… → maps to anchor a[{r['cw_anchor']}]")
    lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT}")
