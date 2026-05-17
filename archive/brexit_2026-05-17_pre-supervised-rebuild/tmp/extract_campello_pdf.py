"""Programmatic verbatim extract of Campello et al. 2022 JFQA Brexit paper.
Uses pdfplumber per F1D locked rule (PDF-first > NLM substance > NLM pages).
"""
from __future__ import annotations
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import pdfplumber

PDF = Path("docs/papers/campello_etal_2022_brexit_jfqa.pdf")
OUT = Path("tmp/campello_extracted_text_2026_05_14.md")

assert PDF.exists(), f"missing {PDF}"

t0 = time.time()
chunks = []
chunks.append(f"# Campello et al. 2022 JFQA — Brexit Paper, Verbatim Programmatic Extract\n")
chunks.append(f"**Source**: `{PDF.as_posix()}` ({PDF.stat().st_size/1024:.1f}KB)")
chunks.append(f"**Method**: pdfplumber.extract_text() per page (no visual/LLM transcription)")
chunks.append(f"**Run**: 2026-05-14")
chunks.append("")

with pdfplumber.open(str(PDF)) as pdf:
    npages = len(pdf.pages)
    chunks.append(f"**Total pages**: {npages}\n\n---\n")
    for i, page in enumerate(pdf.pages, start=1):
        # Journal-page anchor: paper starts at j.3178; PDF p.1 = j.3178.
        j_page = 3177 + i
        text = page.extract_text() or ""
        chunks.append(f"\n## PDF page {i} (journal p.{j_page})\n")
        chunks.append("```\n" + text + "\n```\n")
        # Also extract any tables on this page
        try:
            tables = page.extract_tables()
        except Exception as e:
            tables = []
            chunks.append(f"\n*(table extraction error: {e})*\n")
        for ti, t in enumerate(tables, start=1):
            chunks.append(f"\n### Table {ti} on PDF p.{i}\n")
            chunks.append("```\n")
            for row in t:
                row_clean = [(c if c is not None else "").replace("\n", " | ") for c in row]
                chunks.append(" | ".join(row_clean))
            chunks.append("\n```\n")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(chunks), encoding="utf-8")

elapsed = time.time() - t0
print(f"OK pages={npages} bytes={OUT.stat().st_size} elapsed={elapsed:.1f}s out={OUT.as_posix()}")
