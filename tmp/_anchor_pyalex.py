#!/usr/bin/env python3
"""OpenAlex/pyalex DISCOVERY of literature anchors for the three §II the angle gaps
the NLM notebook could NOT cleanly fill (A/B = NONE; C = only Thewissen, rejected).

  A  legal gag      : pending deal = MNPI, selective disclosure barred
  B  talk-but-hedge : gagged manager fields Q&A -> vaguer / hedged / uncertain
  C  cash != stock  : payment method => asymmetric PRE-ANNOUNCEMENT disclosure
                      behavior. STRICT TEST applied at screen time: an anchor must
                      explain the stock NULL (genuinely absent), not only the cash
                      positive -- and must not run the wrong sign (more-contingent
                      stock -> more hedging). Three survivable forms searched:
                      (i) stock manages/pre-discloses; (ii) stock leaks earlier
                      (S-4/vote); (iii) cash deals more secret/less anticipated.

Output: tmp/anchor_pyalex_results.json (full, per gap, with abstracts) + a
screening shortlist to stdout (title / year / citations / venue / abstract head).
Claude hand-screens STRICTLY; no paper is proposed unless its abstract clearly and
strictly hits the gap. If a gap has no clean hit, say so plainly (real gap to flag).
"""
import json
import time
from pathlib import Path
import pyalex
from pyalex import Works

pyalex.config.email = "sinasoleimanipour@gmail.com"  # polite pool
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5
pyalex.config.retry_http_codes = [429, 500, 503]

GAPS = {
    "A_legal_gag": [
        "material nonpublic information merger negotiations disclosure",
        "Regulation Fair Disclosure selective disclosure managers",
        "merger negotiations confidentiality duty to disclose securities",
        "insider trading material information pending acquisition",
        "firms withhold disclose pending merger negotiations",
        "disclosure obligation acquisition negotiations materiality",
    ],
    "B_talk_but_hedge": [
        "earnings conference call managers evasive answers",
        "does silence speak earnings conference call disclosure",
        "managerial obfuscation disclosure language bad news",
        "withholding information conference call linguistic uncertainty",
        "analyst question manager non-answer disclosure call",
        "strategic ambiguity vague disclosure managers earnings call",
        "managers avoid answering questions earnings call information",
    ],
    "C_cash_vs_stock": [
        # form (i): stock manages / pre-discloses
        "method of payment acquisition voluntary disclosure acquirer",
        "stock financed acquisition disclosure management pre-announcement",
        "stock-for-stock merger earnings management acquirer overvaluation",
        "bidder disclosure manipulation method of payment merger",
        # form (ii): stock leaks earlier via filings / votes
        "stock merger registration statement shareholder vote disclosure timing",
        "acquisition method of payment information asymmetry announcement",
        # form (iii): cash deals more secret / less anticipated
        "cash acquisition predictability anticipation market merger",
        "method of payment merger information environment uncertainty",
        # canonical payment-method / signaling lineage (verify what they claim)
        "information asymmetry method of payment mergers acquisitions signaling",
        "stock market driven acquisitions overvaluation Shleifer Vishny",
    ],
}


def recon(inv):
    if not inv:
        return ""
    pos = {}
    for w, ixs in inv.items():
        for i in ixs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


out = {}
for gap, queries in GAPS.items():
    seen = {}
    for q in queries:
        try:
            try:
                res = Works().search(q).get(per_page=40)
            except TypeError:
                res = Works().search(q).get()
        except Exception as e:
            print("ERR", gap, q, "->", e)
            continue
        for w in res:
            wid = w.get("id")
            if not wid:
                continue
            if wid not in seen:
                pl = w.get("primary_location") or {}
                src = pl.get("source") or {}
                seen[wid] = {
                    "id": wid,
                    "title": w.get("title") or "",
                    "year": w.get("publication_year"),
                    "venue": src.get("display_name") or "",
                    "cited": w.get("cited_by_count", 0),
                    "doi": w.get("doi"),
                    "abstract": recon(w.get("abstract_inverted_index")),
                    "queries": [q],
                }
            else:
                seen[wid]["queries"].append(q)
        time.sleep(0.2)
    out[gap] = sorted(seen.values(), key=lambda x: -x["cited"])

Path("tmp").mkdir(exist_ok=True)
Path("tmp/anchor_pyalex_results.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8"
)

for gap, works in out.items():
    print(f"\n{'='*78}\n### {gap}  (n={len(works)} unique; top 15 by citations)\n{'='*78}")
    for w in works[:15]:
        ab = (w["abstract"] or "").replace("\n", " ")
        print(f"\n[{w['cited']:>5}c {w['year']}] {w['title'][:110]}")
        print(f"        venue: {w['venue'][:60]}  doi: {w['doi']}")
        print(f"        {ab[:300]}")

print(f"\n\nDONE -> tmp/anchor_pyalex_results.json")
