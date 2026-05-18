"""Programmatic extraction of Campello (2022 JFQA) Table 1 / Table 8 +
the corrigendum, straight from the source PDFs. NO hand transcription:
every character written here is pdfplumber's output, not typed by a model.

Outputs (tmp/campello_pdf_extract/):
  table1_pXX.txt   — layout text + extract_tables() for each page that
                      contains the Table 1 definitional note / stats.
  table8_pXX.txt   — same for Table 8.
  corrigendum.txt  — full corrigendum text (may correct defs/values).
  INDEX.txt        — which PDF page each artifact came from.

Run: python scripts/campello_rebuild/_extract_campello_tables.py
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
PAPERS = ROOT / "docs" / "papers"
MAIN = PAPERS / "campello_etal_2022_brexit_jfqa.pdf"
CORRIG = PAPERS / "campello_corrigendum.pdf"
SUPP = PAPERS / "campello_etal_2022_brexit_supplementary.pdf"
OUT = ROOT / "tmp" / "campello_pdf_extract"
OUT.mkdir(parents=True, exist_ok=True)

# Markers that identify the pages we need (case-insensitive substring).
T1_MARKERS = ["summary statistics", "is defined as cash and short-term",
              "TABLE 1", "consensus_earnings_forecast"]
T8_MARKERS = ["net of cash holdings", "TABLE 8",
              "impact of the brexit vote on cash holdings"]
# βᵁᴷ first-stage eq-(13): regress firm return vol on FTSE/SP500/FX vol.
BUK_MARKERS = ["equation (13)", "(13)", "FTSE", "vol(", "βUK", "β U K",
               "rolling", "first-stage", "first stage",
               "U.K. exposure", "exchange rate volatility"]


def _page_text(page) -> str:
    # layout=True preserves column alignment for the numeric stat tables.
    try:
        return page.extract_text(layout=True) or ""
    except Exception:
        return page.extract_text() or ""


def _dump_tables(page) -> str:
    out = []
    try:
        for ti, tbl in enumerate(page.extract_tables()):
            out.append(f"\n--- extract_tables() table {ti} ---")
            for row in tbl:
                out.append(" | ".join("" if c is None else str(c)
                                      for c in row))
    except Exception as e:
        out.append(f"[extract_tables error: {e}]")
    return "\n".join(out)


def _scan(pdf_path: Path, markers, tag: str, index_lines: list[str]) -> None:
    with pdfplumber.open(pdf_path) as pdf:
        index_lines.append(f"{pdf_path.name}: {len(pdf.pages)} pages")
        for i, page in enumerate(pdf.pages):
            txt = _page_text(page)
            low = txt.lower()
            if any(m.lower() in low for m in markers):
                fp = OUT / f"{tag}_pdfpage{i+1:02d}.txt"
                fp.write_text(
                    f"# SOURCE: {pdf_path.name}  PDF page {i+1} "
                    f"(0-based idx {i})\n"
                    f"# Extracted by pdfplumber.extract_text(layout=True). "
                    f"NOT hand-typed.\n"
                    f"{'='*72}\n{txt}\n{'='*72}\n"
                    f"{_dump_tables(page)}\n",
                    encoding="utf-8")
                index_lines.append(
                    f"  {tag}: matched PDF page {i+1} -> {fp.name}")


def main() -> None:
    idx: list[str] = []
    for p in (MAIN, CORRIG, SUPP):
        if not p.exists():
            idx.append(f"MISSING: {p}")
    _scan(MAIN, T1_MARKERS, "table1", idx)
    _scan(MAIN, T8_MARKERS, "table8", idx)
    _scan(MAIN, BUK_MARKERS, "buk", idx)

    # Corrigendum: dump in full (short; may correct defs/values).
    if CORRIG.exists():
        with pdfplumber.open(CORRIG) as pdf:
            buf = [f"# SOURCE: {CORRIG.name} ({len(pdf.pages)} pp). "
                   f"pdfplumber layout text. NOT hand-typed.\n"]
            for i, page in enumerate(pdf.pages):
                buf.append(f"\n===== corrigendum PDF page {i+1} =====\n")
                buf.append(_page_text(page))
                buf.append(_dump_tables(page))
            (OUT / "corrigendum.txt").write_text("\n".join(buf),
                                                 encoding="utf-8")
            idx.append(f"  corrigendum: {len(pdf.pages)} pp -> corrigendum.txt")

    (OUT / "INDEX.txt").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print("\n".join(idx))
    print(f"\nAll artifacts -> {OUT}")


if __name__ == "__main__":
    main()
