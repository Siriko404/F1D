#!/usr/bin/env python3
"""
v2: targeted search using citation chasing + alt phrasings.
The default keyword search proved too loose. v2 strategy:

1. Find papers that CITE the foundational PRisk paper (Hassan 2019) AND mention cash
2. Find papers that CITE the H1.6 anchor (Hasan 2022) AND mention Trump
3. Find papers that CITE Hu et al 2024 RAST AND mention cash
4. Strict abstract filter on the results

Output: tmp/openalex_v2_results.csv + tmp/openalex_v2_top.md
"""

from __future__ import annotations
import csv
from pathlib import Path
from pyalex import Works, config

config.email = "lit-review@anthropic.local"

OUT_DIR = Path(__file__).resolve().parent
RESULTS_CSV = OUT_DIR / "openalex_v2_results.csv"
TOP_MD = OUT_DIR / "openalex_v2_top.md"

# Anchor paper OpenAlex IDs (look up by DOI)
ANCHORS = {
    "Hassan2019_PRisk": "10.1093/qje/qjz021",        # Firm-Level Political Risk QJE
    "Hasan2022_redist": "10.1007/s11156-022-01049-9", # Does firm-level political risk affect cash holdings RQFA
    "Hu2024_minorityCEO": "10.1007/s11142-024-09843-7", # Hu Kang Li Lin RAST
    "Wagner2018_JFE":   "10.1016/j.jfineco.2018.06.013", # Wagner-Zeckhauser-Ziegler JFE
}

def find_anchor_ids() -> dict[str, str]:
    """Lookup OpenAlex Work IDs from DOIs."""
    out = {}
    for name, doi in ANCHORS.items():
        try:
            w = Works()[f"https://doi.org/{doi}"]
            wid = w.get("id", "")
            out[name] = wid
            ttl = (w.get("title", "") or "")[:80]
            cites = w.get("cited_by_count", 0)
            print(f"  {name}: id={wid} ({cites} cites) - {ttl}")
        except Exception as e:
            print(f"  {name}: ERROR - {e}")
            out[name] = ""
    return out

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

def fetch_citing(work_id: str, label: str, max_pages: int = 3) -> list[dict]:
    """Get papers that CITE the given work, paginated."""
    if not work_id:
        return []
    try:
        all_results = []
        # cites filter: papers that cite this work
        # work_id format: https://openalex.org/W12345 -> use just W12345
        wid_short = work_id.split("/")[-1]
        pager = Works().filter(cites=wid_short).filter(publication_year=">2015").sort(cited_by_count="desc")
        page = 1
        for results in pager.paginate(per_page=200, n_max=max_pages * 200):
            all_results.extend(results)
            print(f"    [{label}] page {page}: +{len(results)} (total {len(all_results)})")
            page += 1
            if page > max_pages:
                break
        return all_results
    except Exception as e:
        print(f"    [{label}] ERROR: {e}")
        return []

def main():
    print("=" * 70)
    print("Phase A: lookup anchor paper OpenAlex IDs")
    print("=" * 70)
    anchor_ids = find_anchor_ids()

    print("\n" + "=" * 70)
    print("Phase B: fetch papers citing each anchor")
    print("=" * 70)
    seen_ids: set[str] = set()
    all_records: list[dict] = []

    for label, wid in anchor_ids.items():
        if not wid:
            continue
        print(f"\n--- Citing {label} ---")
        citing = fetch_citing(wid, label, max_pages=3)
        for w in citing:
            wide = w.get("id", "")
            if wide in seen_ids:
                continue
            seen_ids.add(wide)
            rec = extract_record(w)
            rec["citing_anchor"] = label
            all_records.append(rec)

    print(f"\nTotal unique citing-papers: {len(all_records)}")

    # Filter: must mention cash AND must mention (Trump OR election OR TCJA OR tariff)
    def low(s): return (s or "").lower()
    def text(r): return low(r.get("abstract", "")) + " " + low(r.get("title", ""))

    def is_trump_era(r):
        t = text(r)
        return any(s in t for s in [
            "trump", "2016 election", "presidential election",
            "tax cuts and jobs act", "tcja", "tariff",
            "trade war", "trade policy uncertainty", "section 301"
        ])

    def is_cash(r):
        t = text(r)
        return any(s in t for s in [
            "cash holding", "corporate cash", "cash reserve",
            "precautionary saving", "precautionary cash",
            "cash to asset", "cash-to-asset", "cash/asset"
        ])

    def is_did(r):
        t = text(r)
        return any(s in t for s in [
            "difference-in-differences", "difference in differences",
            "diff-in-diff", "did design", "natural experiment",
            "quasi-experiment", "exogenous shock", "treatment group"
        ])

    cash_papers = [r for r in all_records if is_cash(r)]
    trump_papers = [r for r in all_records if is_trump_era(r)]
    cash_and_trump = [r for r in all_records if is_cash(r) and is_trump_era(r)]
    cash_and_did = [r for r in all_records if is_cash(r) and is_did(r)]
    full_match = [r for r in all_records if is_cash(r) and is_trump_era(r) and is_did(r)]

    print(f"\nFilter diagnostic on {len(all_records)} citing papers:")
    print(f"  Mentions cash: {len(cash_papers)}")
    print(f"  Mentions Trump-era: {len(trump_papers)}")
    print(f"  Mentions cash AND Trump-era: {len(cash_and_trump)}")
    print(f"  Mentions cash AND DiD: {len(cash_and_did)}")
    print(f"  Mentions cash AND Trump-era AND DiD: {len(full_match)}")

    # Sort by citations
    full_match.sort(key=lambda r: -int(r.get("cited_by") or 0))
    cash_and_trump.sort(key=lambda r: -int(r.get("cited_by") or 0))

    # Write CSV
    fieldnames = ["title", "authors", "year", "venue", "cited_by", "is_oa",
                  "oa_url", "doi", "abstract", "citing_anchor", "id", "type"]
    with RESULTS_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in all_records:
            row = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(row)
    print(f"\nWrote all results to {RESULTS_CSV}")

    # Write candidate report
    with TOP_MD.open("w", encoding="utf-8") as f:
        f.write("# OpenAlex v2 — Citation-chase candidates\n\n")
        f.write(f"Searched: papers citing 4 anchor works (Hassan 2019 PRisk, Hasan 2022 redist, ")
        f.write(f"Hu et al 2024 RAST, Wagner et al 2018 JFE).\n\n")
        f.write(f"Total citing papers: {len(all_records)}\n\n")
        f.write(f"**Full match (cash + Trump-era + DiD): {len(full_match)}**\n\n")
        for i, r in enumerate(full_match[:30], 1):
            f.write(f"## {i}. {r['title']}\n\n")
            f.write(f"- Authors: {r['authors']}\n")
            f.write(f"- {r['year']} | {r['venue']} | {r['cited_by']} cites | OA={r['is_oa']}\n")
            f.write(f"- DOI: {r['doi']}\n")
            f.write(f"- OA URL: {r.get('oa_url','')}\n")
            f.write(f"- Citing anchor: {r['citing_anchor']}\n\n")
            f.write(f"**Abstract:** {r.get('abstract','(none)')}\n\n---\n\n")
        f.write(f"\n\n## Cash AND Trump-era (lower bar — no DiD requirement)\n\n")
        f.write(f"**Total: {len(cash_and_trump)}**\n\n")
        for i, r in enumerate(cash_and_trump[:50], 1):
            f.write(f"### {i}. {r['title']} ({r['year']}, {r['cited_by']} cites)\n")
            f.write(f"- {r['venue']} | DOI {r['doi']}\n")
            f.write(f"- Citing: {r['citing_anchor']}\n")
            ab = (r.get('abstract','') or '')[:500]
            f.write(f"- Abstract excerpt: {ab}\n\n")
    print(f"Wrote candidate report to {TOP_MD}")

    # Console summary
    print("\n=== FULL MATCH (cash + Trump-era + DiD) ===")
    for i, r in enumerate(full_match[:10], 1):
        print(f"\n[{i}] ({r['cited_by']} cites, {r['year']}, {r['venue']})")
        print(f"    {r['title'][:100]}")
        print(f"    Citing: {r['citing_anchor']}")
        print(f"    DOI: {r['doi']}")
        ab = (r.get('abstract','') or '')[:250]
        print(f"    Abs: {ab}...")

    print("\n=== CASH AND TRUMP-ERA (top 15, no DiD requirement) ===")
    for i, r in enumerate(cash_and_trump[:15], 1):
        print(f"\n[{i}] ({r['cited_by']} cites, {r['year']}) {r['title'][:90]}")
        print(f"    Citing: {r['citing_anchor']} | DOI: {r['doi']}")

if __name__ == "__main__":
    main()
