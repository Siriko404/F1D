#!/usr/bin/env python3
"""Resolve the two unconfirmed anchors by title (DOI route failed):
   Jensen 1986 FCF agency; Dittmar & Mahrt-Smith 2007 value of cash.
Print top candidates so we cite verified records, not memory.
"""
from __future__ import annotations
from pyalex import Works, config

config.email = "lit-review@anthropic.local"

QUERIES = {
    "Jensen1986_FCF": "Agency Costs of Free Cash Flow Corporate Finance and Takeovers",
    "DittmarMahrtSmith2007": "Corporate governance and the value of cash holdings",
}

def recon(inv):
    if not inv: return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs: pos[i] = w
    return " ".join(pos.get(i, "") for i in range(max(pos)+1)) if pos else ""

def safe(s): return str(s).encode("ascii", "replace").decode()

for label, q in QUERIES.items():
    print(f"\n=== {label}: '{q}' ===")
    try:
        hits = Works().search(q).sort(cited_by_count="desc").get(per_page=5)
    except Exception as e:
        print("  ERR", safe(e)); continue
    for w in hits[:5]:
        aus = [(a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])[:4]]
        src = ((w.get("primary_location") or {}).get("source") or {})
        print(safe(f"  {w.get('publication_year','')} {w.get('cited_by_count',0):>6}c "
                   f"| {(w.get('title','') or '')[:70]}"))
        print(safe(f"      {'; '.join(a for a in aus if a)} | {src.get('display_name','')}"))
        print(safe(f"      DOI {w.get('doi','')}  id {w.get('id','')}"))
