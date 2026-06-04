"""Programmatic extraction of the Campello (2022 JFQA) SUPPLEMENTARY pdf.

Sina 2026-05-17: the corrigendum (already extracted, corrigendum.txt
L100-101) states appendices A and B were MISSING from the original article
and the supplementary material "has since been updated" — so the
authoritative variable-definition appendix may live here and could
resolve the Table-1 vs Table-8 CASH-denominator conflict.

NO hand transcription: every character is pdfplumber output.
Outputs (tmp/campello_pdf_extract/):
  supp_FULL.txt              — every page: layout text + extract_tables()
  supp_HITS.txt              — pages matching CASH/definition/appendix/
                               winsor markers, with context
  supp_INDEX.txt             — page count + which pages matched
"""
from __future__ import annotations

import sys
from pathlib import Path

import pdfplumber

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
SUPP = ROOT / "docs" / "papers" / "campello_etal_2022_brexit_supplementary.pdf"
OUT = ROOT / "tmp" / "campello_pdf_extract"
OUT.mkdir(parents=True, exist_ok=True)

MARKERS = [
    "cash is defined", "lagged total assets", "net of cash",
    "total cash holdings", "cash and short-term", "winsor",
    "appendix a", "appendix b", "variable definition", "definition of",
    "cheq", "che ", "tobin", "consensus", "standardized", "table a",
    "table b", "table c1", "table c.1",
]


def _ptext(page) -> str:
    try:
        return page.extract_text(layout=True) or ""
    except Exception:
        return page.extract_text() or ""


def _tables(page) -> str:
    out = []
    try:
        for ti, tbl in enumerate(page.extract_tables()):
            out.append(f"\n--- extract_tables() table {ti} ---")
            for row in tbl:
                out.append(" | ".join("" if c is None else str(c)
                                      for c in row))
    except Exception as e:  # noqa: BLE001
        out.append(f"[extract_tables error: {e}]")
    return "\n".join(out)


def main() -> None:
    if not SUPP.exists():
        sys.exit(f"MISSING supplementary pdf: {SUPP}")
    full, hits, idx = [], [], []
    with pdfplumber.open(SUPP) as pdf:
        npg = len(pdf.pages)
        idx.append(f"{SUPP.name}: {npg} pages")
        for i, page in enumerate(pdf.pages):
            txt = _ptext(page)
            tbl = _tables(page)
            block = (f"\n===== SUPP PDF page {i+1}/{npg} "
                     f"(0-based idx {i}) =====\n{txt}\n{tbl}\n")
            full.append(block)
            low = txt.lower()
            matched = [m for m in MARKERS if m in low]
            if matched:
                hits.append(f"\n##### page {i+1}  matched: "
                            f"{', '.join(sorted(set(matched)))}\n{block}")
                idx.append(f"  page {i+1}: {', '.join(sorted(set(matched)))}")
    (OUT / "supp_FULL.txt").write_text(
        f"# SOURCE: {SUPP.name}  pdfplumber layout text. NOT hand-typed.\n"
        + "\n".join(full), encoding="utf-8")
    (OUT / "supp_HITS.txt").write_text(
        f"# SOURCE: {SUPP.name}  marker-matched pages. NOT hand-typed.\n"
        + "\n".join(hits) if hits else "# no marker hits\n",
        encoding="utf-8")
    (OUT / "supp_INDEX.txt").write_text("\n".join(idx) + "\n",
                                        encoding="utf-8")
    print("\n".join(idx))
    print(f"\nfull → {OUT/'supp_FULL.txt'}")
    print(f"hits → {OUT/'supp_HITS.txt'}  ({len(hits)} pages)")


if __name__ == "__main__":
    main()
