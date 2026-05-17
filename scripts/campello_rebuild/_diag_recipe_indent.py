"""DIAG (read-only): is there a clean first-line-indent signal for
paragraph detection on the Campello recipe pages?

Decides advisor Option A (geometric paragraph extraction) vs Option B
(heading-anchored coarse chunks). Same crop/tolerances as
extract_paper_pdf.py so the geometry matches the verbatim dump.

Prints, per sampled page: each text line's (top, first-word x0,
min font size, first 7 words) + an x0 histogram to expose
body-vs-indent bimodality. NO extraction, NO fix.
"""
import sys
from collections import Counter
from pathlib import Path

import pdfplumber

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "docs" / "papers" / "campello_etal_2022_brexit_jfqa.pdf"
PAGES = [13, 21, 31]  # 1-indexed: IV.A start / Table 1 note / Table 8 caption


def lines_of(page):
    """Group words into visual lines by rounded 'top'; deterministic."""
    words = page.extract_words(
        x_tolerance=1.0, y_tolerance=3, extra_attrs=["size"]
    )
    buckets: dict[int, list] = {}
    for w in words:
        buckets.setdefault(round(w["top"]), []).append(w)
    out = []
    for top in sorted(buckets):
        ws = sorted(buckets[top], key=lambda w: w["x0"])
        out.append((top, ws))
    return out


with pdfplumber.open(str(PDF)) as pdf:
    for pno in PAGES:
        raw = pdf.pages[pno - 1]
        page = raw.crop((0, 0, 405, raw.height))
        rows = lines_of(page)
        x0hist: Counter = Counter()
        print(f"\n{'='*72}\nPAGE {pno}  ({len(rows)} lines)\n{'='*72}")
        for top, ws in rows:
            x0 = round(ws[0]["x0"], 1)
            sz = round(min(w["size"] for w in ws), 1)
            x0hist[round(x0)] += 1
            txt = " ".join(w["text"] for w in ws[:7])
            print(f"  top={top:>4}  x0={x0:>6}  sz={sz:>4}  {txt[:64]}")
        print(f"  -- x0 histogram (rounded): "
              f"{dict(sorted(x0hist.items()))}")
