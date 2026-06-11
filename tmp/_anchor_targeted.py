#!/usr/bin/env python3
"""Targeted OpenAlex retrieval of CANDIDATE anchor papers by distinctive title,
then dump their REAL abstracts for strict hand-screening. We do not assert from
memory what these papers claim -- we pull the abstract and check it against the
gap. Candidates come from the advisor's named seeds + domain canon for each gap.

Strict screen (done by Claude after, not here):
  A  must establish: pending deal = MNPI, selective disclosure legally barred
  B  must establish: gagged/constrained manager -> vaguer/hedged/uncertain on calls
  C  must explain the STOCK NULL (genuinely absent), not only the cash positive,
     and not run the wrong sign. Bridge to PRE-ANNOUNCEMENT CALL behavior required;
     if a candidate only does announcement returns / the payment CHOICE, flag it.
"""
import json
import sys
import time
from pathlib import Path
import pyalex
from pyalex import Works

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
pyalex.config.email = "sinasoleimanipour@gmail.com"
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5
pyalex.config.retry_http_codes = [429, 500, 503]

CANDIDATES = [
    # gap, label, distinctive title query
    ("B", "Hollander-Pronk-Roelofsen 2010 (JAR)", "Does silence speak empirical analysis disclosure choices during conference calls"),
    ("B", "Bushee-Gow-Taylor 2018 (JAR)", "Linguistic complexity in firm disclosures obfuscation or information"),
    ("B", "Hollander conference call withholding", "managers withholding information conference calls no comment disclosure"),
    ("B", "Loughran-McDonald 2011 (JF)", "When is a liability not a liability textual analysis dictionaries 10-Ks"),
    ("B", "Mayew-Venkatachalam 2012 (JF)", "power of voice managerial affective states future firm performance conference calls"),
    ("C", "Myers-Majluf 1984 (JFE)", "Corporate financing and investment decisions when firms have information investors do not have"),
    ("C", "Travlos 1987 (JF)", "Corporate takeover bids methods of payment and bidding firms stock returns"),
    ("C", "Shleifer-Vishny 2003 (JFE)", "Stock market driven acquisitions"),
    ("C", "Faccio-Masulis 2005 (JF)", "The choice of payment method in European mergers and acquisitions"),
    ("C", "Fishman 1989 (JF)", "Preemptive bidding and the role of the medium of exchange in acquisitions"),
    ("C", "Eckbo-Giammarino-Heinkel 1990 (RFS)", "Asymmetric information and the medium of exchange in takeovers"),
    ("C", "Hansen 1987 (JB)", "A theory for the choice of exchange medium in mergers and acquisitions"),
    ("A", "Reg FD selective disclosure (Heflin et al)", "Regulation fair disclosure and the financial information environment"),
    ("A", "Verrecchia discretionary disclosure", "Discretionary disclosure withholding information Verrecchia"),
    ("A", "Dye 1985 (JAR)", "Disclosure of nonproprietary information"),
    ("A", "materiality merger negotiations", "disclosure of merger negotiations materiality securities Basic Levinson"),
]


def recon(inv):
    if not inv:
        return ""
    pos = {}
    for w, ixs in inv.items():
        for i in ixs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


out = []
for gap, label, q in CANDIDATES:
    try:
        try:
            res = Works().search(q).get(per_page=4)
        except TypeError:
            res = Works().search(q).get()
    except Exception as e:
        out.append({"gap": gap, "label": label, "query": q, "error": str(e)})
        print(f"ERR {label}: {e}")
        continue
    top = []
    for w in (res or [])[:3]:
        pl = w.get("primary_location") or {}
        src = pl.get("source") or {}
        top.append({
            "title": w.get("title") or "",
            "year": w.get("publication_year"),
            "venue": src.get("display_name") or "",
            "cited": w.get("cited_by_count", 0),
            "doi": w.get("doi"),
            "abstract": recon(w.get("abstract_inverted_index")),
        })
    out.append({"gap": gap, "label": label, "query": q, "candidates": top})
    time.sleep(0.2)

Path("tmp/anchor_targeted_results.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

for e in out:
    print(f"\n{'='*82}\n[{e['gap']}] {e['label']}\n{'='*82}")
    for c in e.get("candidates", []):
        ab = (c["abstract"] or "").replace("\n", " ")
        doi = (c["doi"] or "").replace("https://doi.org/", "")
        print(f"  [{c['cited']:>5}c {c['year']}] {c['title'][:104]}")
        print(f"        {c['venue'][:56]} | {doi}")
        print(f"        {ab[:420]}\n")
    if e.get("error"):
        print("   ERROR:", e["error"])

print("DONE -> tmp/anchor_targeted_results.json")
