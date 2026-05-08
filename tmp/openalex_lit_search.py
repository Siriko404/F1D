#!/usr/bin/env python3
"""
Programmatic literature search via OpenAlex API.
Goal: find papers using Trump 2016 election OR Trump-era policy as DiD shock
on firm cash holdings.

Output: tmp/openalex_results.csv + tmp/openalex_top_candidates.md
"""

from __future__ import annotations
import csv
import json
from pathlib import Path
from pyalex import Works, config

# OpenAlex politely asks for a contact email in the User-Agent (not required, but
# unlocks the "polite pool" with faster rate limits). Use a placeholder.
config.email = "lit-review@anthropic.local"

OUT_DIR = Path(__file__).resolve().parent
RESULTS_CSV = OUT_DIR / "openalex_results.csv"
TOP_MD = OUT_DIR / "openalex_top_candidates.md"

# Search queries — comprehensive sweep
QUERIES = [
    # Direct Trump-2016 + cash + DiD
    'trump 2016 election "cash holdings" difference-in-differences',
    'trump 2016 "cash holdings" DiD',
    'trump election "corporate cash" precautionary',
    'trump 2016 "corporate liquidity"',
    # Trump policy levers (TCJA, tariffs)
    '"Tax Cuts and Jobs Act" "cash holdings" difference-in-differences',
    'TCJA repatriation "cash holdings" DiD',
    'trump tariff "cash holdings" firm',
    '"section 301" tariff "cash holdings" firm',
    # Political risk + cash + Trump
    '"firm-level political risk" "cash holdings"',
    '"PRisk" "cash holdings" Trump',
    'Hassan Hollander "cash holdings"',
    # Election uncertainty + cash + DiD
    '"presidential election" "corporate cash holdings" DiD',
    '"election uncertainty" "cash holdings" precautionary firm',
    # Trade war + cash
    '"trade war" 2018 "cash holdings" firm DiD',
    '"trade policy uncertainty" "cash holdings" DiD',
    # Broader catch-alls
    'trump shock "cash holdings" firm',
    '"2016 election" firm "cash" precautionary saving',
]

YEAR_MIN = 2016  # papers must postdate Trump's election

def fetch_query(query: str, max_results: int = 50) -> list[dict]:
    """Run one search query, return up to max_results works."""
    try:
        results = (
            Works()
            .search(query)
            .filter(publication_year=f">{YEAR_MIN-1}")
            .filter(type="article")
            .sort(cited_by_count="desc")
            .get(per_page=min(max_results, 200))
        )
        return results
    except Exception as e:
        print(f"  ERROR for query '{query}': {e}")
        return []

def reconstruct_abstract(inverted_index: dict | None) -> str:
    """OpenAlex stores abstracts as inverted index. Reconstruct plaintext."""
    if not inverted_index:
        return ""
    # Build position -> word map
    positions = {}
    for word, idx_list in inverted_index.items():
        for idx in idx_list:
            positions[idx] = word
    if not positions:
        return ""
    max_pos = max(positions.keys())
    return " ".join(positions.get(i, "") for i in range(max_pos + 1))

def extract_record(work: dict) -> dict:
    """Pull key fields from an OpenAlex work."""
    authors = []
    for au in (work.get("authorships") or [])[:6]:
        author = au.get("author") or {}
        name = author.get("display_name", "")
        if name:
            authors.append(name)
    venue = ""
    primary_loc = work.get("primary_location") or {}
    src = primary_loc.get("source") or {}
    if src:
        venue = src.get("display_name", "")
    oa_loc = work.get("best_oa_location") or {}
    oa_url = oa_loc.get("pdf_url") or oa_loc.get("landing_page_url") or ""
    return {
        "id": work.get("id", ""),
        "doi": work.get("doi", ""),
        "title": work.get("title", ""),
        "authors": "; ".join(authors),
        "year": work.get("publication_year", ""),
        "venue": venue,
        "cited_by": work.get("cited_by_count", 0),
        "type": work.get("type", ""),
        "is_oa": work.get("open_access", {}).get("is_oa", False),
        "oa_url": oa_url,
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
    }

def main():
    print(f"Running {len(QUERIES)} OpenAlex queries (year >= {YEAR_MIN})...")
    seen_ids: set[str] = set()
    all_records: list[dict] = []

    for q_idx, query in enumerate(QUERIES, 1):
        print(f"\n[{q_idx}/{len(QUERIES)}] {query!r}")
        results = fetch_query(query, max_results=30)
        added = 0
        for work in results:
            wid = work.get("id", "")
            if wid in seen_ids:
                continue
            seen_ids.add(wid)
            rec = extract_record(work)
            rec["query"] = query
            all_records.append(rec)
            added += 1
        print(f"  hits returned: {len(results)} | new dedup: {added}")

    print(f"\nTotal unique records: {len(all_records)}")

    # Sort by citations desc
    all_records.sort(key=lambda r: -int(r.get("cited_by") or 0))

    # Write CSV
    fieldnames = ["title", "authors", "year", "venue", "cited_by", "is_oa",
                  "oa_url", "doi", "abstract", "query", "id", "type"]
    with RESULTS_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in all_records:
            row = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(row)
    print(f"Wrote {RESULTS_CSV}")

    # Identify top candidates: those whose abstract mentions BOTH (Trump OR
    # election OR TCJA) AND (cash) AND (difference OR DiD OR treatment)
    def is_candidate(r: dict) -> bool:
        ab = (r.get("abstract") or "").lower()
        title = (r.get("title") or "").lower()
        text = ab + " " + title
        has_trump_era = any(t in text for t in [
            "trump", "2016 election", "presidential election",
            "tax cuts and jobs act", "tcja", "tariff",
            "trade war", "trade policy uncertainty",
            "political risk"
        ])
        has_cash = any(t in text for t in [
            "cash holding", "corporate cash", "cash reserve",
            "cash-to-asset", "cash/asset", "cash savings",
            "precautionary saving", "precautionary cash"
        ])
        has_did = any(t in text for t in [
            "difference-in-differences", "difference in differences",
            "diff-in-diff", "did design", "did analysis",
            "treatment effect", "natural experiment", "quasi-experiment",
            "exogenous shock"
        ])
        return has_trump_era and has_cash and has_did

    candidates = [r for r in all_records if is_candidate(r)]
    print(f"\nTop candidates (Trump-era + cash + DiD): {len(candidates)}")

    # Write candidate markdown report
    with TOP_MD.open("w", encoding="utf-8") as f:
        f.write("# OpenAlex top candidates — Trump-era + cash + DiD\n\n")
        f.write(f"From {len(all_records)} unique results across {len(QUERIES)} queries.\n")
        f.write(f"Filter: abstract+title contains (Trump-era term) AND (cash term) AND (DiD term).\n\n")
        f.write(f"**Candidates found: {len(candidates)}**\n\n")
        for i, r in enumerate(candidates, 1):
            f.write(f"## {i}. {r['title']}\n\n")
            f.write(f"- **Authors:** {r['authors']}\n")
            f.write(f"- **Year:** {r['year']}\n")
            f.write(f"- **Venue:** {r['venue']}\n")
            f.write(f"- **Citations:** {r['cited_by']}\n")
            f.write(f"- **Open access:** {r['is_oa']}\n")
            f.write(f"- **DOI:** {r['doi']}\n")
            if r.get("oa_url"):
                f.write(f"- **OA URL:** {r['oa_url']}\n")
            f.write(f"- **Matched on query:** {r['query']!r}\n\n")
            ab = r.get("abstract", "") or "(no abstract)"
            f.write(f"**Abstract:**\n\n> {ab}\n\n---\n\n")
    print(f"Wrote {TOP_MD}")

    # Console summary of top 5
    print("\n=== TOP 5 CANDIDATES (most cited that match all 3 criteria) ===")
    for i, r in enumerate(candidates[:5], 1):
        print(f"\n[{i}] ({r['cited_by']} cites, {r['year']}, {r['venue']})")
        print(f"    {r['title']}")
        print(f"    Authors: {r['authors'][:80]}")
        ab = (r.get("abstract") or "")[:300]
        print(f"    Abstract: {ab}...")

    return all_records, candidates

if __name__ == "__main__":
    main()
