#!/usr/bin/env python3
"""Hunt a paper that CONSTRUCTS a cash/liquidity bag-of-words / dictionary.
Topic search + citation-chase of LM(2011). Rank by CASH x METHOD(word-list) x SRC.
"""
from __future__ import annotations
from pathlib import Path
from pyalex import Works, config
config.email = "lit-review@anthropic.local"
OUT = Path(__file__).resolve().parent / "openalex_cash_lexicon_top.md"

QUERIES = [
    "cash holdings textual analysis word list dictionary",
    "liquidity keywords dictionary corporate disclosure text",
    "cash topic earnings conference call measure keywords",
    "dictionary cash payout dividend text 10-K word count",
    "word list cash liquidity disclosure lexicon",
    "measuring corporate cash policy text-based keyword",
    "bag of words cash liquidity firm disclosure",
]
# citation-chase anchors (method papers that publish finance word lists)
CHASE = {
    "LM2011_liability": "10.1111/j.1540-6261.2010.01625.x",   # Loughran-McDonald JF
    "BLM2015_constraint": "10.1017/s0022109015000411",        # Bodnaruk-LM JFQA (guarded)
}

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
    seen, recs = set(), []
    # topic search
    for q in QUERIES:
        try:
            for w in Works().search(q).sort(relevance_score="desc").get(per_page=40):
                wid = w.get("id", "")
                if wid in seen: continue
                seen.add(wid); recs.append(rec(w))
        except Exception as e:
            print("q ERR", safe(q), safe(e))
    # citation chase
    for label, doi in CHASE.items():
        try:
            a = Works()[f"https://doi.org/{doi}"]; wid = a.get("id", "").split("/")[-1]
            for page in Works().filter(cites=wid).sort(cited_by_count="desc").paginate(per_page=200, n_max=400):
                for w in page:
                    i = w.get("id", "")
                    if i in seen: continue
                    seen.add(i); recs.append(rec(w))
        except Exception as e:
            print("chase MISS", label, safe(e))
    print(f"pool: {len(recs)}")

    CASH = ["cash holding", "cash reserve", "excess cash", "cash-rich", "cash rich", "liquidity",
            "payout", "dividend", "repurchase", "buyback", "cash policy", "corporate cash", "cash balance"]
    METHOD = ["word list", "wordlist", "dictionary", "lexicon", "bag of words", "bag-of-words",
              "keyword", "word count", "term list", "textual", "content analysis", "diction"]
    SRC = ["10-k", "10k", "conference call", "earnings call", "transcript", "disclosure", "md&a",
           "annual report", "filing"]

    def txt(r): return (r["title"] + " " + r["abstract"]).lower()
    def hit(r, T): return any(t in txt(r) for t in T)
    for r in recs:
        r["c"] = hit(r, CASH); r["m"] = hit(r, METHOD); r["s"] = hit(r, SRC)
    # want CASH & METHOD; SRC and cites as tiebreak
    flag = [r for r in recs if r["c"] and r["m"]]
    flag.sort(key=lambda r: (-int(r["s"]), -r["cited_by"]))

    with OUT.open("w", encoding="utf-8") as f:
        f.write(f"# Cash-lexicon hunt: CASH & METHOD hits = {len(flag)} (of {len(recs)})\n\n")
        for i, r in enumerate(flag[:40], 1):
            f.write(f"## {i}. {r['title']} ({r['year']}, {r['cited_by']}c)\n")
            f.write(f"- {r['authors']}\n- {r['venue']} | DOI {r['doi']}\n- {r['abstract'][:600]}\n\n")
    print(f"wrote {OUT}")
    print(f"\n=== CASH & word-list/dictionary hits: {len(flag)} ===")
    for i, r in enumerate(flag[:25], 1):
        tag = "SRC" if r["s"] else "   "
        print(safe(f"[{i}] {tag} {r['cited_by']:>5}c {r['year']} {r['venue'][:26]:<26} | {r['title'][:74]}"))

if __name__ == "__main__":
    main()
