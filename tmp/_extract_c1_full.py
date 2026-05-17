"""Ad-hoc: extract the ENTIRE Table C.1 from the supplementary PDF, page 8,
FULL page width (no x-crop) to recover the Firm-Quarters column that the
prior x<405 crop clipped (claude-mem #819). Read-only diagnostic.
"""
import sys
from pathlib import Path
import pdfplumber

sys.stdout.reconfigure(encoding="utf-8")

PDF = Path(__file__).resolve().parents[1] / "docs" / "papers" / \
    "campello_etal_2022_brexit_supplementary.pdf"

with pdfplumber.open(str(PDF)) as doc:
    page = doc.pages[7]  # 0-based -> supplementary p.8
    print(f"PAGE bbox: width={page.width:.1f} height={page.height:.1f}")

    print("\n========== extract_text() — VERBATIM, FULL WIDTH ==========")
    print(page.extract_text())

    print("\n========== two-column reconstruction (words by row) ==========")
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    # cluster words into rows by rounded 'top'
    rows: dict[int, list] = {}
    for w in words:
        key = round(w["top"] / 3.0)
        rows.setdefault(key, []).append(w)
    for key in sorted(rows):
        ws = sorted(rows[key], key=lambda d: d["x0"])
        left = " ".join(d["text"] for d in ws if d["x0"] < 405)
        right = " ".join(d["text"] for d in ws if d["x0"] >= 405)
        if left or right:
            print(f"  {left:<78s} | {right}")

    print("\n========== extract_tables() ==========")
    for i, tbl in enumerate(page.extract_tables()):
        print(f"--- table {i} ---")
        for r in tbl:
            print("  ", r)
