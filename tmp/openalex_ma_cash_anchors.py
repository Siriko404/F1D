#!/usr/bin/env python3
"""Verify M&A / empire-building cash-channel literature anchors via OpenAlex.
Print id/doi/year/citations/first-authors so the RIGHT paper is confirmed (no title-mismatch)."""
import pyalex
from pyalex import Works

pyalex.config.email = "sinasoleimanipour@gmail.com"

QUERIES = [
    ("Harford 1999  cash->acquisitions (PRIMARY empirical)", "Corporate Cash Reserves and Acquisitions"),
    ("Jensen 1986  free-cash-flow / empire (THEORY)", "Agency Costs of Free Cash Flow Corporate Finance and Takeovers"),
    ("Almeida-Campello-Hackbarth 2011  liquidity/cash-timed mergers", "Liquidity mergers"),
    ("Harford-Mansi-Maxwell 2008  governance & cash spending", "Corporate governance and firm cash holdings in the US"),
    ("Opler-Pinkowitz-Stulz-Williamson 1999  cash holdings baseline", "The determinants and implications of corporate cash holdings"),
]

def first_authors(w, k=3):
    a = [au["author"]["display_name"] for au in w.get("authorships", [])[:k]]
    return ", ".join(a)

for label, title in QUERIES:
    print(f"\n##### {label}")
    print(f"      query title: {title!r}")
    try:
        hits = Works().search_filter(title=title).sort(cited_by_count="desc").get(per_page=3)
    except Exception as e:
        print(f"      ERROR {e}"); continue
    for w in hits[:3]:
        print(f"  - {w.get('publication_year')}  cites={w.get('cited_by_count'):>6}  "
              f"doi={w.get('doi')}")
        print(f"      title: {w.get('title')}")
        print(f"      authors: {first_authors(w)}  | venue: "
              f"{(w.get('primary_location') or {}).get('source', {}) and (w['primary_location']['source'] or {}).get('display_name')}")
