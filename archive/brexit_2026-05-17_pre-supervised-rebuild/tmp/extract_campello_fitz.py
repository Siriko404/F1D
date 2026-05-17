"""Cleaner re-extract using PyMuPDF (fitz) — handles 2-column academic PDFs without
the character-interleave artifacts seen with pdfplumber on this paper.

Outputs page-anchored markdown for downstream verbatim transcription.
"""
from __future__ import annotations
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import fitz  # PyMuPDF

PDF = Path("docs/papers/campello_etal_2022_brexit_jfqa.pdf")
OUT = Path("tmp/campello_extracted_fitz_2026_05_14.md")

t0 = time.time()
doc = fitz.open(str(PDF))
n = doc.page_count

out_lines = []
out_lines.append(f"# Campello et al. 2022 JFQA — Brexit Paper, Fitz Verbatim Extract")
out_lines.append(f"**Source**: `{PDF.as_posix()}`")
out_lines.append(f"**Method**: PyMuPDF (fitz) get_text('text') per page — cleaner than pdfplumber on column-formatted PDF")
out_lines.append(f"**Pages**: {n}")
out_lines.append(f"**Run**: 2026-05-14")
out_lines.append("\n---\n")

for i in range(n):
    page = doc[i]
    text = page.get_text("text")  # preserves reading order, drops the sidebar character stream
    j_page = 3177 + (i + 1)  # paper starts j.3178
    out_lines.append(f"\n## PDF page {i+1} (journal p.{j_page})\n")
    out_lines.append("```")
    out_lines.append(text.rstrip())
    out_lines.append("```\n")

doc.close()
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(out_lines), encoding="utf-8")
print(f"OK pages={n} bytes={OUT.stat().st_size} elapsed={time.time()-t0:.1f}s out={OUT.as_posix()}")
