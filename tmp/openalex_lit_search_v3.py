#!/usr/bin/env python3
"""
v3: relaxed criteria — Trump 2016 election + cash holdings as DV, ANY design
(DiD not required). Precautionary channel preferred but not mandatory.

Strategy: TITLE-focused search to bypass empty-abstract issue, plus broader
keyword sweep, plus direct title filter on the citing-anchors set we already have.
"""

from __future__ import annotations
import csv
from pathlib import Path
from pyalex import Works, config

config.email = "lit-review@anthropic.local"

OUT_DIR = Path(__file__).resolve().parent
RESULTS_CSV = OUT_DIR / "openalex_v3_results.csv"
TOP_MD = OUT_DIR / "openalex_v3_top.md"

# v3 queries — relaxed (no "DiD" term required) — focus on title-resolved hits
QUERIES = [
    # Trump election + cash
    'trump election cash holdings firm',
    'trump 2016 cash firm policy',
    '"presidential election" "cash holdings" 2016',
    '"2016 election" "cash holdings" U.S.',
    'November 2016 cash corporate',
    # TCJA + cash (relaxed — any design)
    '"Tax Cuts and Jobs Act" "cash holdings"',
    'TCJA cash holdings firm',
    'TCJA repatriation cash holdings',
    # Tariff + cash
    'tariff "cash holdings" firm 2018',
    'trade war cash holdings firm',
    # Political risk + cash + Trump
    '"firm-level political risk" "cash holdings" Trump',
    '"PRisk" "cash holdings" 2016',
    # Reverse: papers in cash-holdings literature that mention Trump
    '"corporate cash holdings" Trump',
    '"cash holdings" "2016 election"',
    '"cash holdings" "TCJA"',
    '"cash holdings" "Tax Cuts and Jobs Act"',
    '"cash holdings" "trade policy uncertainty"',
    '"cash holdings" "tariff"',
]

YEAR_MIN = 2016

def fetch_query(query: str, max_results: int = 50) -> list[dict]:
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
        print(f"  ERROR: {e}")
        return []

def reconstruct_abstract(inverted_index: dict | None) -> str:
    if not inverted_index:
        return ""
    positions = {}
    for word, idx_list in inverted_index.items():
        for idx in idx_list:
            positions[idx] = word
    if not positions:
        return ""
    max_pos = max(positions.keys())
    return " ".join(positions.get(i, "") for i in range(max_pos + 1))

def extract_record(work: dict) -> dict:
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
    print(f"Running {len(QUERIES)} relaxed queries (year >= {YEAR_MIN})...")
    seen_ids: set[str] = set()
    all_records: list[dict] = []

    for q_idx, query in enumerate(QUERIES, 1):
        print(f"\n[{q_idx}/{len(QUERIES)}] {query!r}")
        results = fetch_query(query, max_results=50)
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

    print(f"\nTotal unique: {len(all_records)}")

    # TITLE-based filter — title contains both Trump-era term AND cash term
    def low(s): return (s or "").lower()
    trump_terms_title = ['trump', '2016 election', 'tax cuts and jobs act', 'tcja', 'tariff', 'trade war', 'trade policy']
    cash_terms_title = ['cash holding', 'corporate cash', 'cash reserve', 'cash policy', 'precautionary cash', 'cash position', 'firm liquidity', 'cash-to-asset']

    title_hits = []
    for r in all_records:
        title = low(r['title'])
        ht = any(s in title for s in trump_terms_title)
        hc = any(s in title for s in cash_terms_title)
        if ht and hc:
            title_hits.append(r)

    # ALSO: abstract-based filter for those with abstracts
    abstract_hits = []
    for r in all_records:
        if r in title_hits:
            continue
        ab = low(r['abstract'])
        if not ab:
            continue
        ht = any(s in ab for s in trump_terms_title)
        hc = any(s in ab for s in cash_terms_title)
        if ht and hc:
            abstract_hits.append(r)

    print(f"\nTitle hits (Trump-era + cash IN TITLE): {len(title_hits)}")
    print(f"Abstract-only hits (Trump-era + cash in abstract, not title): {len(abstract_hits)}")

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

    # Write report
    title_hits.sort(key=lambda r: -int(r['cited_by']))
    abstract_hits.sort(key=lambda r: -int(r['cited_by']))

    with TOP_MD.open("w", encoding="utf-8") as f:
        f.write("# OpenAlex v3 — RELAXED criteria (no DiD requirement)\n\n")
        f.write(f"From {len(all_records)} unique results across {len(QUERIES)} relaxed queries.\n\n")
        f.write(f"Trump-era + cash terms in TITLE: {len(title_hits)}\n")
        f.write(f"Trump-era + cash terms in ABSTRACT (not title): {len(abstract_hits)}\n\n")

        f.write("## Title hits — strongest signal\n\n")
        for i, r in enumerate(title_hits, 1):
            f.write(f"### {i}. {r['title']}\n\n")
            f.write(f"- Authors: {r['authors']}\n")
            f.write(f"- {r['year']} | {r['venue']} | {r['cited_by']} cites | OA={r['is_oa']}\n")
            f.write(f"- DOI: {r['doi']}\n")
            f.write(f"- OA URL: {r['oa_url']}\n")
            f.write(f"- Abstract: {r.get('abstract','(none)')}\n\n---\n\n")

        f.write("\n\n## Abstract hits (not in title)\n\n")
        for i, r in enumerate(abstract_hits[:30], 1):
            f.write(f"### {i}. {r['title']} ({r['year']}, {r['cited_by']} cites)\n")
            f.write(f"- {r['venue']} | DOI {r['doi']} | OA={r['is_oa']}\n")
            ab = r.get('abstract', '')
            f.write(f"- Abstract: {ab[:600]}\n\n")

    print(f"Wrote {TOP_MD}")

    # Console — top title hits
    print("\n=== TITLE HITS (strongest, sorted by citations) ===")
    for i, r in enumerate(title_hits, 1):
        print(f"\n[{i}] {r['cited_by']} cites | {r['year']} | {r['venue'][:35]}")
        print(f"    {r['title'][:130]}")
        print(f"    Authors: {r['authors'][:90]}")
        print(f"    DOI: {r['doi']}")
        ab = (r.get('abstract','') or '')[:250]
        print(f"    Abs: {ab}")

    print("\n=== ABSTRACT HITS (top 10 by citations) ===")
    for i, r in enumerate(abstract_hits[:10], 1):
        print(f"\n[{i}] {r['cited_by']} cites | {r['year']} | {r['venue'][:35]}")
        print(f"    {r['title'][:130]}")
        ab = (r.get('abstract','') or '')[:200]
        print(f"    Abs: {ab}")

if __name__ == "__main__":
    main()
