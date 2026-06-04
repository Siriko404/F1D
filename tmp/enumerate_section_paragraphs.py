"""
Enumerate §IV paragraphs from Campello et al. 2022 main paper using PyMuPDF
blocks mode (paragraph-aware bounding box grouping). Ground-truth anchor for
the paragraph numbering disagreement between NLM and Claude-web in Round 1b.
"""
import fitz
import re
from pathlib import Path

PDF = Path("docs/papers/campello_etal_2022_brexit_jfqa.pdf")
OUT = Path("tmp/campello_paragraph_index_2026_05_26.md")
PAGES = list(range(13, 21))  # printed 3190-3197

doc = fitz.open(PDF)
raw_blocks = []
for pdf_page in PAGES:
    page = doc[pdf_page - 1]
    blocks = page.get_text("blocks")
    blocks_sorted = sorted(blocks, key=lambda b: (b[1], b[0]))
    for b in blocks_sorted:
        text = b[4].strip()
        if not text:
            continue
        text_one = re.sub(r"\s+", " ", text).strip()
        if not text_one:
            continue
        raw_blocks.append({
            "pdf_page": pdf_page,
            "printed_page": pdf_page + 3177,
            "y0": b[1],
            "raw_text": text,
            "text_one": text_one,
        })
doc.close()

# Classify each block
def classify(b):
    t = b["text_one"]
    # Marginalia / page header / DOI
    if "https://doi.org" in t or "Cambridge University Press" in t:
        return "marginalia"
    if re.match(r"^\d+\s+Journal of Financial", t) or re.match(r"^Campello.*Almeida", t):
        return "header"
    if re.match(r"^\d+$", t):
        return "pagenum"
    # Footnote (starts with number-prefix directly attached to letter, no space)
    if re.match(r"^\d{1,3}[A-Z]", t):
        return "footnote"
    # Section headings (CHECKED BEFORE label filter since headings are short)
    if re.match(r"^IV\.\s+[A-Z]", t) and len(t) < 60:
        return ("heading", "section", "IV")
    m = re.match(r"^([A-Z])\.\s+[A-Z]", t)
    if m and len(t) < 60:
        return ("heading", "subsection", f"IV.{m.group(1)}")
    m = re.match(r"^(\d+)\.\s+[A-Z]", t)
    if m and len(t) < 80:
        return ("heading", "subsubsection", m.group(1))
    # Figure/table label fragment (very short, no real prose)
    if len(t) < 80 or len(t.split()) < 8:
        return "label_or_fragment"
    # Equation blocks (typically short, with parenthesized eq number)
    if re.search(r"\(\d{1,2}\)\s*$", t) and len(t) < 200:
        return "equation"
    # Table titles
    if t.startswith("TABLE ") or t.startswith("Table "):
        return "tabletitle"
    # Body paragraph
    return "body"

# Walk blocks; track section state
current_subsection = None
current_subsubsection = None
para_counter = {}
rows = []

for i, b in enumerate(raw_blocks):
    kind = classify(b)
    if isinstance(kind, tuple):
        _, level, value = kind
        if level == "section":
            current_subsection = None
            current_subsubsection = None
        elif level == "subsection":
            current_subsection = value
            current_subsubsection = None
            para_counter[current_subsection] = 0
        elif level == "subsubsection":
            current_subsubsection = f"{current_subsection}.{value}"
            para_counter[current_subsubsection] = 0
        continue
    if kind != "body":
        continue
    key = current_subsubsection or current_subsection
    if not key:
        continue
    para_counter[key] = para_counter.get(key, 0) + 1
    text_one = b["text_one"]
    rows.append({
        "section": key,
        "para_position": para_counter[key],
        "pdf_page": b["pdf_page"],
        "printed_page": b["printed_page"],
        "first_8_words": " ".join(text_one.split()[:8]),
        "last_8_words": " ".join(text_one.split()[-8:]),
        "len_chars": len(text_one),
    })

lines = [
    "# Campello §IV — Paragraph Index (PyMuPDF blocks-mode ground truth)",
    "",
    f"Source: PyMuPDF `page.get_text('blocks')` on `docs/papers/campello_etal_2022_brexit_jfqa.pdf` PDF pages 13-20 (printed 3190-3197).",
    f"Generated: 2026-05-26 by `tmp/enumerate_section_paragraphs.py`",
    "",
    "Per-section paragraph numbering counts from the section heading. Filters applied: skip marginalia (DOI band), running headers, page numbers, footnotes (start `\\d+[A-Z]`), display equations (short blocks ending `(NN)`), table titles.",
    "",
    "| § | ¶ | PDF pg | Printed pg | First 8 words | Last 8 words | Chars |",
    "|---|---|---|---|---|---|---|",
]
for r in rows:
    f8 = r["first_8_words"].replace("|", "\\|")
    l8 = r["last_8_words"].replace("|", "\\|")
    lines.append(f"| {r['section']} | {r['para_position']} | {r['pdf_page']} | {r['printed_page']} | {f8} | {l8} | {r['len_chars']} |")

OUT.write_text("\n".join(lines), encoding="utf-8")
# encode-safe print
print(f"Wrote {OUT} ({len(rows)} paragraphs in IV)")
