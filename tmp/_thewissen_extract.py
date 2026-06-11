#!/usr/bin/env python3
"""Full-text extract + discriminating-keyword search of the Thewissen et al (2024)
stock-for-stock tone paper (ssrn-4900453.pdf) — the closest potential prior.

Certainty questions:
  (1) measure = does it EVER use an UNCERTAINTY measure (LM uncertainty / DWZ /
      residual), or only TONE (Henry pos-neg)?
  (2) channel = earnings CALLS / Q&A, or only earnings PRESS RELEASES?
  (3) treatment = does it test CASH deals (or only stock-for-stock; cash=control)?
"""
import sys
from pathlib import Path
import pdfplumber
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PDF = r"C:\Users\sinas\Downloads\ssrn-4900453.pdf"
pages = []
with pdfplumber.open(PDF) as pdf:
    for pg in pdf.pages:
        pages.append(pg.extract_text() or '')
full = "\n".join(f"\n===== PAGE {i+1} =====\n{t}" for i, t in enumerate(pages))
Path('tmp/thewissen_fulltext.txt').write_text(full, encoding='utf-8')
print(f"TOTAL PAGES: {len(pages)}  (full text -> tmp/thewissen_fulltext.txt)\n")

KW = ['uncertain', 'conference call', 'earnings call', 'q&a', 'question and answer',
      'loughran', 'mcdonald', 'dzielinski', 'zeckhauser', ' dwz', 'residual',
      'cash deal', 'cash bidder', 'cash acquir', 'cash-financed', 'cash payment',
      'method of payment', 'cash offer', 'fog', 'readability', 'vague', 'hedg',
      'press release', 'henry (2008)', 'henry and leone']

low = [t.lower() for t in pages]
for k in KW:
    hits = []
    for i, t in enumerate(low):
        start = 0
        while True:
            j = t.find(k, start)
            if j < 0:
                break
            ctx = pages[i][max(0, j-70):j+90].replace('\n', ' ')
            hits.append((i+1, ctx))
            start = j + 1
    if hits:
        print(f"### '{k}'  ({len(hits)} hits)")
        for pg, ctx in hits[:6]:
            print(f"   p{pg}: …{ctx}…")
    else:
        print(f"### '{k}'  -- ZERO hits")
    print()
