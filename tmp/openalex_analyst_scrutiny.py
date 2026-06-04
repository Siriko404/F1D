#!/usr/bin/env python3
"""Anchor the analyst-scrutiny reverse-causality channel:
   high cash -> analysts probe cash -> CEO evasive (UncRes up).

(A) Confirm cash->scrutiny anchors by DOI (Jensen86, Harford99, HMM08).
(B) Topic-search the mechanism literature: managerial silence/evasion in
    conference calls, analyst question-topic attention, payout pressure.
(C) Rank hits by channel relevance: CALL x CASH x EVADE buckets + citations.
Outputs ranked markdown + console summary.
"""
from __future__ import annotations
from pathlib import Path
from pyalex import Works, config

config.email = "lit-review@anthropic.local"
OUT = Path(__file__).resolve().parent
TOP_MD = OUT / "openalex_analyst_scrutiny_top.md"

# (A) cash -> scrutiny / agency anchors (confirm exist + cites)
ANCHORS = {
    "Jensen1986_FCF":      "10.2307/1818789",
    "Harford1999_JF":      "10.1111/0022-1082.00179",
    "HarfordMansiMaxwell2008_JFE": "10.1016/j.jfineco.2007.04.002",
    "DittmarMS2007_JF":    "10.1111/j.1540-6261.2007.01259.x",
}

# (B) topic queries for the MECHANISM (call-level evasion under scrutiny)
QUERIES = [
    "does silence speak conference call disclosure",
    "conference call managers evasive answers analysts",
    "analyst scrutiny cash holdings payout pressure",
    "free cash flow agency monitoring payout analysts",
    "earnings call question answer linguistic uncertainty manager",
    "strategic disclosure obfuscation managers analysts",
    "earnings conference call analyst question topic attention",
    "managerial tone evasion uncertainty earnings call",
]

def recon(inv):
    if not inv: return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs: pos[i] = w
    return " ".join(pos.get(i, "") for i in range(max(pos)+1)) if pos else ""

def rec(w):
    aus = [(a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])[:5]]
    src = ((w.get("primary_location") or {}).get("source") or {})
    return {"title": w.get("title", "") or "", "authors": "; ".join(a for a in aus if a),
            "year": w.get("publication_year", ""), "venue": src.get("display_name", "") or "",
            "cited_by": w.get("cited_by_count", 0) or 0, "doi": w.get("doi", "") or "",
            "id": w.get("id", "") or "", "abstract": recon(w.get("abstract_inverted_index"))}

def safe(s): return str(s).encode("ascii", "replace").decode()

def main():
    # (A) anchors
    print("=== (A) cash -> scrutiny anchors ===")
    for label, doi in ANCHORS.items():
        try:
            a = Works()[f"https://doi.org/{doi}"]
            r = rec(a)
            print(safe(f"{label:<30} {r['year']} {r['cited_by']:>6}c  {r['title'][:60]}"))
        except Exception as e:
            print(f"{label:<30} MISS  {safe(e)}")

    # (B) topic search
    seen, recs = set(), []
    for q in QUERIES:
        try:
            page = Works().search(q).sort(relevance_score="desc").get(per_page=40)
        except Exception as e:
            print("  query ERR", safe(q), safe(e)); continue
        for w in page:
            wid = w.get("id", "")
            if wid in seen: continue
            seen.add(wid); rr = rec(w); rr["q"] = q; recs.append(rr)
    print(f"\n=== (B) unique topic hits: {len(recs)} ===")

    # (C) channel-relevance scoring
    CALL  = ["earnings call", "conference call", "analyst", "q&a", "question-and-answer",
             "investor call", "quarterly call", "earnings conference"]
    CASH  = ["cash holding", "cash reserve", "excess cash", "cash-rich", "liquidity",
             "payout", "dividend", "repurchase", "buyback", "free cash flow", "financial slack"]
    EVADE = ["evasi", "obfuscat", "silence", "withhold", "disclosure choice", "strateg",
             "ambigu", "vague", "uncertain", "hedge", "non-answer", "dodge", "tone",
             "linguistic", "readability", "concealment", "spin"]

    def txt(r): return (r["title"] + " " + r["abstract"]).lower()
    def hit(r, terms): return any(t in txt(r) for t in terms)
    for r in recs:
        r["b_call"] = hit(r, CALL); r["b_cash"] = hit(r, CASH); r["b_evade"] = hit(r, EVADE)
        r["nb"] = int(r["b_call"]) + int(r["b_cash"]) + int(r["b_evade"])
    # all-3 first, then 2-bucket, then citations
    recs.sort(key=lambda r: (-r["nb"], -(r["cited_by"])))

    with TOP_MD.open("w", encoding="utf-8") as f:
        f.write("# Analyst-scrutiny channel — OpenAlex topic search\n\n")
        f.write(f"unique hits {len(recs)}; ranked by CALL/CASH/EVADE buckets + cites\n\n")
        for i, r in enumerate(recs[:40], 1):
            tags = " ".join(t for t, b in [("CALL", r["b_call"]), ("CASH", r["b_cash"]),
                                           ("EVADE", r["b_evade"])] if b)
            f.write(f"## {i}. {r['title']} ({r['year']}, {r['cited_by']} cites) [{tags}]\n")
            f.write(f"- {r['authors']}\n- {r['venue']} | DOI {r['doi']}\n- {r['abstract'][:600]}\n\n")
    print(f"wrote {TOP_MD}")

    print("\n=== top channel hits (>=2 buckets) ===")
    for i, r in enumerate([r for r in recs if r["nb"] >= 2][:24], 1):
        tags = "".join(t for t, b in [("C", r["b_call"]), ("$", r["b_cash"]), ("E", r["b_evade"])] if b)
        print(safe(f"[{i}] {tags:<3} {r['cited_by']:>5}c {r['year']} {r['venue'][:28]:<28} | {r['title'][:80]}"))

if __name__ == "__main__":
    main()
