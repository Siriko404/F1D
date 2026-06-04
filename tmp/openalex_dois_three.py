#!/usr/bin/env python3
"""Get DOI + landing page + any OA PDF for the 3 minimal anchors."""
from __future__ import annotations
from pyalex import Works, config
config.email = "lit-review@anthropic.local"

TARGETS = {
    "Jensen1986_AER":   ("id",    "W3121131820"),
    "Hassan2019_QJE":   ("title", "Firm-Level Political Risk Measurement and Effects"),
    "Hollander2010_JAR":("title", "Does Silence Speak Disclosure Choices During Conference Calls"),
}

def safe(s): return str(s).encode("ascii", "replace").decode()

def show(label, w):
    loc = (w.get("primary_location") or {})
    best = (w.get("best_oa_location") or {})
    src = (loc.get("source") or {})
    print(f"\n### {label}")
    print(safe(f"  {w.get('title','')}"))
    print(safe(f"  {w.get('publication_year','')} | {src.get('display_name','')}"))
    print(safe(f"  DOI : {w.get('doi','')}"))
    print(safe(f"  land: {loc.get('landing_page_url','')}"))
    print(safe(f"  PDF : {best.get('pdf_url','') or loc.get('pdf_url','')}"))

for label, (kind, val) in TARGETS.items():
    try:
        if kind == "id":
            w = Works()[val]
        else:
            w = Works().search(val).sort(cited_by_count="desc").get(per_page=1)[0]
        show(label, w)
    except Exception as e:
        print(f"\n### {label}  ERR {safe(e)}")
