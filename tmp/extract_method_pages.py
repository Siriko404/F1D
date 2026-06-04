"""
Extract PDF pages 12-20 (printed pages 3189-3197) from Campello et al. 2022
JFQA paper for methodology cross-check anchor. Solution-free: extract
verbatim text only, no LLM transcription.

Run: python tmp/extract_method_pages.py
Output: tmp/campello_pdf_extract/method_pdfpage{NN}.txt (PDF pages 12-20)
"""
import pdfplumber
from pathlib import Path

PDF = Path("docs/papers/campello_etal_2022_brexit_jfqa.pdf")
OUT_DIR = Path("tmp/campello_pdf_extract")
PAGES = list(range(12, 21))  # PDF pages 12..20 inclusive (0-based 11..19)

OUT_DIR.mkdir(parents=True, exist_ok=True)

with pdfplumber.open(PDF) as doc:
    for pnum in PAGES:
        page = doc.pages[pnum - 1]  # 0-based index
        text = page.extract_text(layout=True) or ""
        out = OUT_DIR / f"method_pdfpage{pnum:02d}.txt"
        out.write_text(
            f"# SOURCE: {PDF.name}  PDF page {pnum} (0-based idx {pnum-1})\n"
            f"# Extracted by pdfplumber.extract_text(layout=True). NOT hand-typed.\n"
            f"{'='*72}\n{text}\n",
            encoding="utf-8",
        )
        print(f"wrote {out}  ({len(text)} chars)")
