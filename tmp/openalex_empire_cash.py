#!/usr/bin/env python3
"""Find lit: empire-building / agency acquisitions where firms ACCUMULATE cash
before acquiring (war-chest), ideally via DiD / natural experiment.

Adapts tmp/openalex_lit_search_v5.py infrastructure (pyalex keyword sweep +
citation-chase + inverted-index abstract reconstruction).
"""
from __future__ import annotations
import csv
from pathlib import Path
from pyalex import Works, config

config.email = "lit-review@anthropic.local"
OUT = Path(__file__).resolve().parent
RESULTS_CSV = OUT / "openalex_empire_cash_results.csv"
TOP_MD = OUT / "openalex_empire_cash_top.md"

QUERIES = [
    "empire building cash holdings acquisitions free cash flow",
    "corporate cash reserves acquisitions value-destroying",
    "free cash flow hypothesis acquisitions managerial empire building",
    "war chest cash accumulation acquisitions bidder",
    "financial slack acquisitions accumulate cash before",
    "cash holdings mergers difference-in-differences natural experiment",
    "excess cash acquisitions overinvestment agency",
    "managerial entrenchment cash holdings acquisitions spending",
    "cash windfall acquisitions overinvestment natural experiment",
    "precautionary versus agency motive cash holdings acquisitions",
    "governance cash holdings spending acquisitions value of cash",
    "cash-rich firms bidders acquisition announcement returns",
    "pre-acquisition cash accumulation acquirer war chest",
    "liquidity mergers cash accumulate acquire distressed",
    "cash holdings firm acquisitiveness likelihood logit",
    "repatriation tax holiday cash acquisitions investment",
    "free cash flow agency overinvestment difference-in-differences",
    "cash savings prior to acquisition merger timing",
]

# Anchors fetched by TITLE (avoid DOI guessing); top hit chased for citations.
ANCHOR_TITLES = [
    "Corporate Cash Reserves and Acquisitions",                 # Harford 1999 JF
    "Corporate governance and firm cash holdings in the US",    # Harford Mansi Maxwell 2008 JFE
    "Liquidity Mergers",                                        # Almeida Campello Hackbarth 2011 JFE
    "The Agency Costs of Free Cash Flow",                       # Jensen 1986
]

YEAR_MIN = 1990


def reconstruct_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    if not pos:
        return ""
    return " ".join(pos.get(i, "") for i in range(max(pos) + 1))


def rec(w):
    aus = [ (a.get("author") or {}).get("display_name","") for a in (w.get("authorships") or [])[:5] ]
    ploc = w.get("primary_location") or {}
    src = (ploc.get("source") or {})
    return {
        "title": w.get("title",""),
        "authors": "; ".join([a for a in aus if a]),
        "year": w.get("publication_year",""),
        "venue": src.get("display_name",""),
        "cited_by": w.get("cited_by_count",0),
        "doi": w.get("doi",""),
        "id": w.get("id",""),
        "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
    }


def fetch_query(q, n=30):
    try:
        return (Works().search(q)
                .filter(publication_year=f">{YEAR_MIN-1}")
                .filter(type="article")
                .sort(cited_by_count="desc")
                .get(per_page=n))
    except Exception as e:
        print("  ERR", e); return []


def fetch_anchor_and_citers(title, n_cite_pages=1):
    try:
        hits = Works().search(title).sort(cited_by_count="desc").get(per_page=3)
    except Exception as e:
        print("  anchor ERR", e); return None, []
    if not hits:
        return None, []
    anchor = hits[0]
    wid = anchor.get("id","").split("/")[-1]
    citers = []
    try:
        for page in (Works().filter(cites=wid).sort(cited_by_count="desc")
                     .paginate(per_page=200, n_max=n_cite_pages*200)):
            citers.extend(page)
    except Exception as e:
        print("  citer ERR", e)
    return anchor, citers


def main():
    seen, all_recs = set(), []
    print("== keyword sweep ==")
    for i, q in enumerate(QUERIES, 1):
        res = fetch_query(q)
        add = 0
        for w in res:
            wid = w.get("id","")
            if wid in seen: continue
            seen.add(wid); r = rec(w); r["src"] = f"q:{q[:30]}"; all_recs.append(r); add += 1
        print(f"[{i}/{len(QUERIES)}] +{add}  {q[:50]}")

    print("\n== citation chase ==")
    for t in ANCHOR_TITLES:
        anchor, citers = fetch_anchor_and_citers(t)
        if anchor:
            ar = rec(anchor)
            print(f"  anchor: {ar['title'][:55]} ({ar['year']}, {ar['cited_by']} cites) -> {len(citers)} citers")
            if anchor.get("id","") not in seen:
                seen.add(anchor.get("id","")); ar["src"]=f"anchor:{t[:20]}"; all_recs.append(ar)
        add = 0
        for w in citers:
            wid = w.get("id","")
            if wid in seen: continue
            seen.add(wid); r = rec(w); r["src"]=f"cites:{t[:20]}"; all_recs.append(r); add += 1
        print(f"    +{add} new citers")

    print(f"\nTOTAL UNIQUE: {len(all_recs)}")

    def txt(r): return (r["title"]+" "+r["abstract"]).lower()
    cash = ["cash holding","cash reserve","cash policy","corporate cash","excess cash",
            "cash-rich","financial slack","liquidity","cash accumulation","war chest","cash savings"]
    acq  = ["acquisition","acquire","merger","bidder","takeover","empire","overinvest"]
    did  = ["difference-in-differences","difference in differences","natural experiment",
            "quasi-natural","exogenous","staggered","instrument","treatment"]

    def hasany(r, terms): return any(t in txt(r) for t in terms)
    flagged = []
    for r in all_recs:
        r["f_cash"] = hasany(r, cash); r["f_acq"] = hasany(r, acq); r["f_did"] = hasany(r, did)
        if r["f_cash"] and r["f_acq"]:
            flagged.append(r)
    flagged.sort(key=lambda r: -int(r["cited_by"] or 0))

    with RESULTS_CSV.open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["title","authors","year","venue","cited_by","doi","f_cash","f_acq","f_did","src","abstract","id"], quoting=csv.QUOTE_ALL)
        wr.writeheader()
        for r in all_recs:
            wr.writerow({k: r.get(k,"") for k in wr.fieldnames})

    with TOP_MD.open("w", encoding="utf-8") as f:
        f.write(f"# Empire-building cash-hoarding lit search\n\nUnique works: {len(all_recs)}; cash&acq: {len(flagged)}\n\n")
        for i, r in enumerate(flagged[:40], 1):
            tag = "DiD" if r["f_did"] else ""
            f.write(f"## {i}. {r['title']} ({r['year']}, {r['cited_by']} cites) {tag}\n")
            f.write(f"- {r['authors']}\n- {r['venue']} | DOI {r['doi']}\n- src:{r['src']}\n")
            f.write(f"- {r['abstract'][:600]}\n\n")
    print(f"wrote {TOP_MD}")

    print("\n=== TOP 25 (cash & acquisition), * = DiD-flag ===")
    for i, r in enumerate(flagged[:25], 1):
        star = "*" if r["f_did"] else " "
        print(f"\n[{i}]{star} {r['cited_by']:>5} cites | {r['year']} | {(r['venue'] or '')[:34]}")
        print(f"     {r['title'][:120]}")
        print(f"     {r['authors'][:80]}")
        print(f"     {(r['abstract'] or '')[:240]}")


if __name__ == "__main__":
    main()
