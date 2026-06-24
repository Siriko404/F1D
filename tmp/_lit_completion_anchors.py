#!/usr/bin/env python3
"""Targeted confirmation of the CANONICAL deal-completion-prediction papers,
to adopt their ex-ante feature set (don't reinvent). Title search -> top hit
with DOI + abstract, so we can cite + read the determinants each uses.
"""
import time
from pathlib import Path
import pyalex
from pyalex import Works

pyalex.config.email = "sinasoleimanipour@gmail.com"
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5
pyalex.config.retry_http_codes = [429, 500, 503]

TARGETS = [
    "Predicting tender offer success a logistic regression analysis",   # Walkling 1985 JFQA
    "Hostility in takeovers in the eyes of the beholder",               # Schwert 2000 JF
    "Termination fees in mergers and acquisitions",                     # Officer 2003 JFE
    "Breaking up is hard to do termination fee provisions merger outcomes",  # Bates-Lemmon 2003 JFE
    "Merger negotiations and the toehold puzzle",                       # Betton Eckbo Thorburn 2008 JFE
    "Toeholds bid jumps and expected payoffs in takeovers",            # Betton Eckbo 2000 RFS
    "Why do some merger and acquisitions deals fail global perspective",  # 2020
    "Probability of mergers and acquisitions deal failure",            # 2020 JFEP
    "The role of termination fees lockups completion mergers",
    "Anticipation in merger arbitrage probability of completion",
]


def recon(inv):
    if not inv:
        return ""
    pos = {}
    for w, ixs in inv.items():
        for i in ixs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def asc(x):
    return (x or "").encode("ascii", "ignore").decode()


for q in TARGETS:
    try:
        res = Works().search(q).get(per_page=3)
    except Exception as e:
        print("ERR", q, e); continue
    print(f"\n{'='*80}\nQUERY: {q}")
    for w in res[:2]:
        pl = w.get("primary_location") or {}
        src = (pl.get("source") or {}).get("display_name") or ""
        ab = asc(recon(w.get("abstract_inverted_index")))
        print(f"  [{w.get('cited_by_count',0)}c {w.get('publication_year')}] {asc(w.get('title',''))[:95]}")
        print(f"     venue: {asc(src)[:55]}  doi: {w.get('doi')}")
        if ab:
            print(f"     {ab[:340]}")
    time.sleep(0.25)
print("\nDONE")
