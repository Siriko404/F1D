"""Extract Boasiako 2020 EFM full text + per-page splits for verbatim audit.

Outputs:
    tmp/boasiako_extracted_text_2026_05_14.md   — full text concatenated
    tmp/boasiako_pages/p01.txt … p24.txt        — per-page splits

Run from F1D project root:
    python tmp/extract_boasiako_pdf.py
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber

SRC = Path("docs/papers/boasiako_oconnor_keefe_2020_databreach_efm.pdf")
OUT_FULL = Path("tmp/boasiako_extracted_text_2026_05_14.md")
OUT_PAGES_DIR = Path("tmp/boasiako_pages")


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"PDF not found: {SRC.resolve()}")

    OUT_PAGES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Opening: {SRC}")
    pages_out = []
    with pdfplumber.open(SRC) as pdf:
        n_pages = len(pdf.pages)
        print(f"Pages: {n_pages}")
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            page_path = OUT_PAGES_DIR / f"p{i:02d}.txt"
            page_path.write_text(text, encoding="utf-8")
            pages_out.append(f"\n\n# === PAGE {i:02d} ===\n\n{text}")
            print(f"  page {i:02d}: {len(text):>5d} chars -> {page_path.name}")

    OUT_FULL.write_text(
        f"# Boasiako-O'Connor Keefe (2020) EFM — verbatim text extraction\n"
        f"# Source: {SRC}\n"
        f"# Pages: {n_pages}\n"
        + "".join(pages_out),
        encoding="utf-8",
    )
    print(f"\nFull text -> {OUT_FULL}")
    print(f"Per-page  -> {OUT_PAGES_DIR}/")


if __name__ == "__main__":
    main()
