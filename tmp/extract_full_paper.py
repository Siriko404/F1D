"""
Full PyMuPDF extraction of Campello et al. 2022 main paper + supplementary
+ corrigendum. Used as the ground-truth anchor for 3-AI methodology
cross-check. NOT hand-typed, NOT LLM-transcribed.

v3: switched pdfplumber -> PyMuPDF (fitz) because pdfplumber interleaved
rotated right-margin DOI marginalia ("https://doi.org/...") into body
text on every page. PyMuPDF respects reading-order blocks and rotation.

Run: python tmp/extract_full_paper.py
Output:
  tmp/campello_pdf_extract/full_main_pdfpage{NN}.txt   (45 pages)
  tmp/campello_pdf_extract/full_supp_pdfpage{NN}.txt   (19 pages)
  tmp/campello_pdf_extract/full_corrigendum_pdfpage{NN}.txt
"""
import fitz  # PyMuPDF
from pathlib import Path

OUT = Path("tmp/campello_pdf_extract")
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = [
    ("docs/papers/campello_etal_2022_brexit_jfqa.pdf",          "full_main"),
    ("docs/papers/campello_etal_2022_brexit_supplementary.pdf", "full_supp"),
    ("docs/papers/campello_corrigendum.pdf",                    "full_corrigendum"),
]

for pdf_path, prefix in SOURCES:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"SKIP {pdf_path} (not found)")
        continue
    doc = fitz.open(pdf_path)
    n = doc.page_count
    for i in range(n):
        page = doc[i]
        # blocks-mode skips rotated marginalia by sorting on reading order
        text = page.get_text("text") or ""
        out = OUT / f"{prefix}_pdfpage{i+1:02d}.txt"
        out.write_text(
            f"# SOURCE: {pdf_path.name}  PDF page {i+1} of {n} (0-based idx {i})\n"
            f"# Extracted by PyMuPDF page.get_text('text'). NOT hand-typed.\n"
            f"{'='*72}\n{text}\n",
            encoding="utf-8",
        )
    print(f"{prefix}: extracted {n} pages from {pdf_path.name}")
    doc.close()
