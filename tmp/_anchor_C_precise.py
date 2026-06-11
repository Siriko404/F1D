#!/usr/bin/env python3
"""Final precise sweep for the gap-C anchor: a paper on PRE-ANNOUNCEMENT acquirer
disclosure / information environment that DIFFERS BY PAYMENT METHOD (cash vs stock)
-- the thing that would explain our stock NULL. Relevance-sorted; abstract-gated to
require BOTH a payment-method term AND a pre-announcement/disclosure/leakage term,
so signaling-at-announcement papers (Travlos etc.) are filtered out. If this is dry
too, C has no clean library anchor -> flag plainly (ours to build)."""
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

QUERIES = [
    "acquirer disclosure before merger announcement method of payment",
    "information leakage merger run-up cash versus stock deal",
    "pre-announcement information environment acquirer cash stock",
    "merger anticipation predictability stock financed cash financed",
    "target run-up rumor cash stock method of payment",
    "acquirer voluntary disclosure prior to acquisition announcement",
    "information asymmetry acquirer disclosure pre-merger payment",
    "bidder earnings management before stock merger announcement",
]

PAY = ["cash", "stock", "equity", "payment", "exchange medium", "medium of exchange",
       "stock-for-stock", "stock financed", "method of payment"]
PRE = ["before announcement", "pre-announcement", "preannounc", "prior to",
       "anticipat", "leakage", "run-up", "runup", "run up", "information environment",
       "disclos", "rumor", "rumour", "pre-merger", "pre-deal", "ahead of"]


def recon(inv):
    if not inv:
        return ""
    pos = {}
    for w, ixs in inv.items():
        for i in ixs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def has(t, terms):
    t = t.lower()
    return any(k in t for k in terms)


seen = {}
for q in QUERIES:
    try:
        try:
            res = Works().search(q).get(per_page=40)
        except TypeError:
            res = Works().search(q).get()
    except Exception as e:
        print("ERR", q, "->", e)
        continue
    for w in res:
        wid = w.get("id")
        if not wid or wid in seen:
            continue
        pl = w.get("primary_location") or {}
        src = pl.get("source") or {}
        ab = recon(w.get("abstract_inverted_index"))
        seen[wid] = {
            "title": w.get("title") or "", "year": w.get("publication_year"),
            "venue": src.get("display_name") or "", "cited": w.get("cited_by_count", 0),
            "doi": w.get("doi"), "abstract": ab,
        }
    time.sleep(0.2)

# precision gate: need a payment term AND a pre-announcement/disclosure term, AND a deal term
works = list(seen.values())
hits = []
for w in works:
    blob = (w["title"] + " " + w["abstract"]).lower()
    if has(blob, PAY) and has(blob, PRE) and has(blob, ["acqui", "merger", "takeover", "bidder", "deal", "m&a"]):
        hits.append(w)
hits.sort(key=lambda x: -x["cited"])

Path("tmp/anchor_C_precise_results.json").write_text(
    json.dumps(hits, indent=1, ensure_ascii=False), encoding="utf-8")

print(f"PRECISE C SWEEP: {len(works)} unique, {len(hits)} pass the payment x pre-announcement x deal gate\n")
for w in hits[:18]:
    ab = (w["abstract"] or "").replace("\n", " ")
    doi = (w["doi"] or "").replace("https://doi.org/", "")
    print(f"[{w['cited']:>5}c {w['year']}] {w['title'][:108]}")
    print(f"     {w['venue'][:56]} | {doi}")
    print(f"     {ab[:360]}\n")
print("DONE -> tmp/anchor_C_precise_results.json")
