#!/usr/bin/env python3
"""
v4: BROAD systematic lit review.
Target: ANY exogenous-shock DiD/quasi-experiment with cash holdings as DV
via precautionary channel — that plausibly fits our CEO speech-uncertainty
story (shock activates precautionary state → both speech UP and cash UP).

Strategy:
A) Keyword search across many shock types (geopolitical, climate, pandemic,
   election, regulatory, trade, financial-crisis, customer-concentration, etc.)
B) Citation chase from foundational precautionary-cash papers:
   - Almeida-Campello-Weisbach 2004 JF (cash flow sensitivity of cash)
   - Bates-Kahle-Stulz 2009 JF (why hold so much cash)
   - Acharya-Almeida-Campello 2007 (hedging needs)
   - Han-Qiu 2007 (CFvol moderator)
   - Hassan-Hollander-vL-Tahoun 2020 JFQA (Brexit uncertainty)
C) Filter: title OR abstract mentions cash + (DiD-style identification term)
"""

from __future__ import annotations
import csv
from pathlib import Path
from pyalex import Works, config

config.email = "lit-review@anthropic.local"

OUT_DIR = Path(__file__).resolve().parent
RESULTS_CSV = OUT_DIR / "openalex_v4_results.csv"
TOP_MD = OUT_DIR / "openalex_v4_top.md"

# Anchor papers for citation chasing (precautionary-cash foundational)
ANCHORS = {
    "ACW2004_JF": "10.1111/j.1540-6261.2004.00679.x",  # Almeida-Campello-Weisbach JF
    "BKS2009_JF": "10.1111/j.1540-6261.2009.01492.x",  # Bates-Kahle-Stulz JF
    "ACW2007_JFE": "10.1016/j.jfineco.2007.04.002",   # Acharya-Almeida-Campello hedging needs
    "HassanBrexit_JFQA": "10.1017/S0022109021000600", # Hassan et al 2020 JFQA Brexit
    "Hasan2022_RQFA": "10.1007/s11156-022-01049-9",   # H1.6 anchor
    "HHLT2019_QJE": "10.1093/qje/qjz021",             # PRisk QJE
}

# v4 broad shock-DiD-cash queries
QUERIES = [
    # Geopolitical / war shocks
    '"cash holdings" "natural experiment" precautionary firm',
    '"cash holdings" "exogenous shock" precautionary',
    '"cash holdings" "quasi-natural experiment" DiD',
    'geopolitical risk "cash holdings" DiD firm',
    '"Russia-Ukraine" "cash holdings" firm',
    '"Brexit" "cash holdings" DiD U.S.',
    # Climate / disaster shocks
    'climate risk "cash holdings" DiD precautionary',
    'natural disaster "cash holdings" firm DiD',
    'hurricane "cash holdings" firm DiD',
    'wildfire flood "cash holdings" firm',
    # Pandemic
    'COVID "cash holdings" precautionary DiD',
    'pandemic "cash holdings" firm DiD',
    # Election uncertainty (general, not just Trump)
    '"election uncertainty" "cash holdings" DiD precautionary',
    'gubernatorial election "cash holdings" DiD',
    '"presidential election" "cash holdings" DiD precautionary',
    # Industry / customer / supplier
    'customer concentration "cash holdings" precautionary firm',
    '"industry shock" "cash holdings" DiD precautionary',
    '"supply chain" "cash holdings" DiD precautionary',
    # Regulatory / litigation
    '"regulatory uncertainty" "cash holdings" DiD',
    'litigation risk "cash holdings" DiD precautionary',
    # Monetary / financial
    '"monetary policy" "cash holdings" DiD precautionary',
    'banking crisis "cash holdings" precautionary firm DiD',
    '"credit supply shock" "cash holdings" DiD firm',
    # CEO turnover (relevant for speech-uncertainty story)
    'CEO turnover "cash holdings" DiD precautionary',
    'CEO death "cash holdings" DiD precautionary',
    # Cybersecurity / breach (CEO speech often mentions)
    'cybersecurity breach "cash holdings" firm DiD',
    'data breach "cash holdings" precautionary',
]

YEAR_MIN = 2010

def fetch_query(query: str, max_results: int = 30) -> list[dict]:
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

def fetch_citing(work_id: str, label: str, max_pages: int = 2) -> list[dict]:
    if not work_id:
        return []
    try:
        all_results = []
        wid_short = work_id.split("/")[-1]
        pager = (
            Works()
            .filter(cites=wid_short)
            .filter(publication_year=">2010")
            .sort(cited_by_count="desc")
        )
        page = 1
        for results in pager.paginate(per_page=200, n_max=max_pages * 200):
            all_results.extend(results)
            page += 1
            if page > max_pages:
                break
        return all_results
    except Exception as e:
        print(f"    ERROR: {e}")
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
    seen_ids: set[str] = set()
    all_records: list[dict] = []

    print("=" * 70)
    print("Phase A: keyword sweep")
    print("=" * 70)
    for q_idx, query in enumerate(QUERIES, 1):
        print(f"\n[{q_idx}/{len(QUERIES)}] {query!r}")
        results = fetch_query(query, max_results=30)
        added = 0
        for w in results:
            wid = w.get("id", "")
            if wid in seen_ids:
                continue
            seen_ids.add(wid)
            rec = extract_record(w)
            rec["source"] = f"query: {query}"
            all_records.append(rec)
            added += 1
        print(f"  +{added} new")

    print(f"\nAfter Phase A: {len(all_records)} unique")

    print("\n" + "=" * 70)
    print("Phase B: citation chase from precautionary-cash anchors")
    print("=" * 70)
    for label, doi in ANCHORS.items():
        print(f"\n--- {label} ({doi}) ---")
        try:
            anchor_work = Works()[f"https://doi.org/{doi}"]
            wid = anchor_work.get("id", "")
            cites = anchor_work.get("cited_by_count", 0)
            print(f"  anchor: {wid} ({cites} cites)")
        except Exception as e:
            print(f"  anchor lookup error: {e}")
            continue

        citing = fetch_citing(wid, label, max_pages=2)
        added = 0
        for w in citing:
            wide = w.get("id", "")
            if wide in seen_ids:
                continue
            seen_ids.add(wide)
            rec = extract_record(w)
            rec["source"] = f"cites: {label}"
            all_records.append(rec)
            added += 1
        print(f"  citing-papers fetched: {len(citing)} | new dedup: {added}")

    print(f"\nTOTAL UNIQUE: {len(all_records)}")

    # Filter
    def low(s): return (s or "").lower()
    def text(r): return low(r.get("abstract", "")) + " " + low(r.get("title", ""))

    cash_terms = ['cash holding', 'corporate cash', 'cash reserve', 'cash policy',
                  'precautionary cash', 'cash position', 'firm liquidity',
                  'cash-to-asset', 'cash savings', 'cash hoarding']
    did_terms = ['difference-in-differences', 'difference in differences',
                 'diff-in-diff', 'natural experiment', 'quasi-experiment',
                 'quasi-natural', 'exogenous shock', 'treatment effect',
                 'instrumental variable', 'regression discontinuity', 'event study',
                 'staggered']
    precaut_terms = ['precautionary', 'precaution', 'hedging needs', 'risk management',
                     'uncertainty', 'cash flow volatility', 'financing constraint',
                     'financing friction', 'liquidity buffer']

    def has_any(r, terms): return any(s in text(r) for s in terms)

    cash_pap = [r for r in all_records if has_any(r, cash_terms)]
    cash_did = [r for r in cash_pap if has_any(r, did_terms)]
    cash_did_prec = [r for r in cash_did if has_any(r, precaut_terms)]

    print(f"\nFilter funnel:")
    print(f"  Mentions cash terms:                          {len(cash_pap)}")
    print(f"  + DiD-style identification:                   {len(cash_did)}")
    print(f"  + precautionary channel:                      {len(cash_did_prec)}")

    # Sort by citations desc
    cash_did_prec.sort(key=lambda r: -int(r['cited_by'] or 0))

    # Write CSV
    fieldnames = ["title", "authors", "year", "venue", "cited_by", "is_oa",
                  "oa_url", "doi", "abstract", "source", "id", "type"]
    with RESULTS_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in all_records:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"\nWrote {RESULTS_CSV}")

    # Markdown candidate report
    with TOP_MD.open("w", encoding="utf-8") as f:
        f.write("# OpenAlex v4 — Broad shock-DiD-cash-precautionary search\n\n")
        f.write(f"Total unique works: {len(all_records)}\n")
        f.write(f"Cash + DiD + precautionary: **{len(cash_did_prec)}**\n\n")
        f.write("Ranked by citations.\n\n")
        for i, r in enumerate(cash_did_prec[:60], 1):
            f.write(f"## {i}. {r['title']} ({r['year']}, {r['cited_by']} cites)\n\n")
            f.write(f"- Authors: {r['authors']}\n")
            f.write(f"- Venue: {r['venue']}\n")
            f.write(f"- DOI: {r['doi']}\n")
            f.write(f"- OA: {r['is_oa']} | URL: {r.get('oa_url','')}\n")
            f.write(f"- Source: {r['source']}\n\n")
            ab = r.get('abstract', '') or '(none)'
            f.write(f"**Abstract:** {ab}\n\n---\n\n")
    print(f"Wrote {TOP_MD}")

    # Console: top 20
    print("\n=== TOP 20 (cash + DiD + precautionary) ===")
    for i, r in enumerate(cash_did_prec[:20], 1):
        print(f"\n[{i}] {r['cited_by']} cites | {r['year']} | {r['venue'][:35]}")
        print(f"    {r['title'][:130]}")
        print(f"    DOI: {r['doi']}")
        ab = (r.get('abstract','') or '')[:200]
        print(f"    {ab}")

if __name__ == "__main__":
    main()
