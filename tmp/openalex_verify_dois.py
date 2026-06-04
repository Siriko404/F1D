#!/usr/bin/env python3
"""Verify candidate DOIs resolve to the RIGHT papers (title must match)."""
from __future__ import annotations
from pyalex import Works, config
config.email = "lit-review@anthropic.local"

CANDIDATES = {
    "Hassan2019_QJE":    "10.1093/qje/qjz021",
    "Hollander2010_JAR": "10.1111/j.1475-679x.2010.00368.x",
}
def safe(s): return str(s).encode("ascii", "replace").decode()

for label, doi in CANDIDATES.items():
    try:
        w = Works()[f"https://doi.org/{doi}"]
        loc = (w.get("primary_location") or {}); src = (loc.get("source") or {})
        print(f"\n### {label}")
        print(safe(f"  TITLE: {w.get('title','')}"))
        print(safe(f"  {w.get('publication_year','')} | {src.get('display_name','')} | {w.get('cited_by_count',0)}c"))
        print(safe(f"  DOI  : https://doi.org/{doi}"))
        print(safe(f"  land : {loc.get('landing_page_url','')}"))
    except Exception as e:
        print(f"\n### {label}  ERR {safe(e)}")
