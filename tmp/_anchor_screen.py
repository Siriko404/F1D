#!/usr/bin/env python3
"""Read tmp/anchor_pyalex_results.json (already saved) and print a utf-8-safe
screening shortlist per gap. Filters obvious off-topic noise by requiring the
title+abstract to contain at least one on-topic term for that gap, then shows
top-by-citations for hand-screening. No re-querying."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

data = json.loads(Path("tmp/anchor_pyalex_results.json").read_text(encoding="utf-8"))

# on-topic gates (lowercased substring; any-match keeps the work)
GATE = {
    "A_legal_gag": ["disclos", "nonpublic", "non-public", "material information",
                    "insider", "regulation fd", "selective disclosure", "merger negotiation",
                    "confidential", "securities law", "duty to disclose"],
    "B_talk_but_hedge": ["conference call", "earnings call", "analyst", "obfuscat",
                          "evasive", "vague", "ambigu", "withhold", "silence", "tone",
                          "linguistic", "readability", "hedg", "qualitative disclosure",
                          "textual", "manager"],
    "C_cash_vs_stock": ["method of payment", "stock-for-stock", "stock financ", "cash financ",
                         "acquir", "bidder", "merger", "takeover", "overvalu", "disclos",
                         "earnings management", "registration", "exchange ratio", "signal"],
}

TOPN = 14
for gap, works in data.items():
    gates = GATE[gap]
    hits = [w for w in works if any(g in (w["title"] + " " + (w["abstract"] or "")).lower() for g in gates)]
    print(f"\n{'='*80}\n### {gap}  ({len(hits)} on-topic of {len(works)} unique; top {TOPN})\n{'='*80}")
    for w in hits[:TOPN]:
        ab = (w["abstract"] or "").replace("\n", " ")
        doi = (w["doi"] or "").replace("https://doi.org/", "")
        print(f"\n[{w['cited']:>5}c {w['year']}] {w['title'][:115]}")
        print(f"     {w['venue'][:58]}  | {doi}")
        print(f"     {ab[:340]}")
