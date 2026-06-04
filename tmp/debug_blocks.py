"""Quick dump of PyMuPDF blocks for §IV pages to understand structure."""
import fitz
from pathlib import Path

doc = fitz.open(Path("docs/papers/campello_etal_2022_brexit_jfqa.pdf"))
for pdf_page in [13, 14, 15]:
    page = doc[pdf_page - 1]
    blocks = page.get_text("blocks")
    blocks_sorted = sorted(blocks, key=lambda b: (b[1], b[0]))
    print(f"\n=== PDF page {pdf_page} (printed {pdf_page + 3177}) ===")
    for i, b in enumerate(blocks_sorted):
        text_one = " ".join(b[4].split())
        print(f"  [{i:02d}] y={b[1]:.0f} len={len(text_one):3d} | {text_one[:120]}")
doc.close()
