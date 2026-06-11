#!/usr/bin/env python3
"""Full-text extract + discriminating-keyword grep of Ragozzino & Reuer (2024),
'Implications of M&A for information disclosures in earnings calls' (LRP) ->
docs/papers/1-s2.0-S0024630123001000-main.pdf.

Backstops the NLM 'no uncertainty measure' answer with a programmatic absence
check (advisor: for an absence claim, a clean NLM 'no' is the trigger to grep,
not grounds to skip). Confirms: (a) NO linguistic-uncertainty / tone construct
(LM-uncertainty, DWZ, modal, hedge, fog, vague), (b) measure IS Feldman keyword
intensity.
"""
import sys
from pathlib import Path
import pdfplumber
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PDF = r"docs\papers\1-s2.0-S0024630123001000-main.pdf"
pages = []
with pdfplumber.open(PDF) as pdf:
    for pg in pdf.pages:
        pages.append(pg.extract_text() or '')
full = "\n".join(f"\n===== PAGE {i+1} =====\n{t}" for i, t in enumerate(pages))
Path('tmp/ragozzino_fulltext.txt').write_text(full, encoding='utf-8')
print(f"TOTAL PAGES: {len(pages)}  (full text -> tmp/ragozzino_fulltext.txt)\n")

# absence terms (should be ZERO / incidental) + presence terms (should appear)
KW = ['uncertain', 'loughran', 'mcdonald', 'dzielinski', 'zeckhauser', ' dwz',
      'residual', 'abnormal', 'expected tone', 'fog', 'readab', 'vague', 'hedg',
      'modal', 'ambigu', 'pessimis', 'optimis', 'sentiment', 'tone',
      'feldman', 'henry (2008)', 'keyword', 'dictionary']

low = [t.lower() for t in pages]
for k in KW:
    hits = []
    for i, t in enumerate(low):
        start = 0
        while True:
            j = t.find(k, start)
            if j < 0:
                break
            ctx = pages[i][max(0, j-65):j+95].replace('\n', ' ')
            hits.append((i + 1, ctx))
            start = j + 1
    if hits:
        print(f"### '{k}'  ({len(hits)} hits)")
        for pg, ctx in hits[:5]:
            print(f"   p{pg}: ...{ctx}...")
    else:
        print(f"### '{k}'  -- ZERO hits")
    print()
