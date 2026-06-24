#!/usr/bin/env python3
"""pyalex DISCOVERY: how the literature predicts M&A deal COMPLETION PROBABILITY
ex-ante, and which deal characteristics it uses. Goal: adopt the standard
completion-prediction feature set (don't reinvent) for a materiality = prob x
magnitude proxy. Also grounds the prob x magnitude materiality construct itself.

Output: tmp/lit_completion_prob_results.json + screening shortlist to stdout.
Hand-screen STRICTLY: a paper must actually model/predict deal completion (or
define merger-negotiation materiality), not merely mention mergers.
"""
import json, time
from pathlib import Path
import pyalex
from pyalex import Works

pyalex.config.email = "sinasoleimanipour@gmail.com"
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5
pyalex.config.retry_http_codes = [429, 500, 503]

GAPS = {
    "A_completion_determinants": [
        "determinants of merger completion probability",
        "likelihood takeover success completed withdrawn determinants",
        "predicting deal completion mergers acquisitions characteristics",
        "what determines whether a merger is completed or withdrawn",
        "probability of deal completion target firm characteristics",
        "takeover success failure logit acquirer target attitude",
        "merger outcome completion abandoned bid determinants",
    ],
    "B_merger_arbitrage_prob": [
        "merger arbitrage probability of completion estimation",
        "risk arbitrage deal completion probability model",
        "predicting merger success risk arbitrage spread",
        "implied probability merger completion announcement spread",
        "merger arbitrage returns deal resolution completion likelihood",
    ],
    "C_payment_attitude_size_completion": [
        "method of payment cash stock merger completion likelihood",
        "hostile friendly attitude takeover completion probability",
        "relative deal size acquirer target completion merger",
        "tender offer versus merger completion success rate",
        "public private target acquisition completion likelihood",
        "toehold competing bids merger completion probability",
        "termination fee lockup merger completion likelihood",
        "regulatory antitrust review merger completion probability",
        "cross-border domestic acquisition completion likelihood",
    ],
    "D_materiality_prob_magnitude": [
        "materiality merger negotiations probability magnitude disclosure",
        "Basic v Levinson materiality preliminary merger negotiations",
        "material nonpublic information pending acquisition probability magnitude",
        "economic significance materiality acquisition relative size disclosure",
        "when is a pending merger material to disclose",
    ],
    "E_relative_size_acquirer_reaction": [
        "relative size acquisition acquirer announcement returns",
        "deal size materiality acquirer market reaction merger",
        "large acquisitions relative to acquirer value information",
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


KW = ("merg", "acquisi", "acquir", "takeover", "tender", "bidder", "bid ",
      "target firm", "deal ", "withdrawn", "completion", "abandon", "materialit",
      "nonpublic", "payment", "toehold", "arbitrage")


def on_topic(title, ab):
    t = (title + " " + ab).lower()
    return any(k in t for k in KW)


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
        for rank, w in enumerate(res):          # res is relevance-ranked by OpenAlex
            wid = w.get("id")
            if not wid:
                continue
            title = w.get("title") or ""
            ab = recon(w.get("abstract_inverted_index"))
            if not on_topic(title, ab):         # drop tangential megahits
                continue
            if wid not in seen:
                pl = w.get("primary_location") or {}
                src = pl.get("source") or {}
                seen[wid] = {
                    "id": wid, "title": title,
                    "year": w.get("publication_year"),
                    "venue": src.get("display_name") or "",
                    "cited": w.get("cited_by_count", 0),
                    "doi": w.get("doi"),
                    "abstract": ab,
                    "queries": [q], "best_rank": rank,
                }
            else:
                seen[wid]["queries"].append(q)
                seen[wid]["best_rank"] = min(seen[wid]["best_rank"], rank)
        time.sleep(0.2)
    # surface papers that match MANY queries with high relevance; citations as tiebreak
    out[gap] = sorted(seen.values(),
                      key=lambda x: (-len(x["queries"]), x["best_rank"], -x["cited"]))

Path("tmp").mkdir(exist_ok=True)
Path("tmp/lit_completion_prob_results.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

def asc(x):
    return (x or "").encode("ascii", "ignore").decode()      # cp1252-safe stdout

for gap, works in out.items():
    print(f"\n{'='*78}\n### {gap}  (n={len(works)} unique; top 12 by query-overlap+relevance)\n{'='*78}")
    for w in works[:12]:
        ab = asc((w["abstract"] or "").replace("\n", " "))
        print(f"\n[{w['cited']:>5}c {w['year']}] nq={len(w['queries'])} {asc(w['title'])[:105]}")
        print(f"        venue: {asc(w['venue'])[:60]}  doi: {w['doi']}")
        print(f"        {ab[:280]}")
print(f"\n\nDONE -> tmp/lit_completion_prob_results.json")
