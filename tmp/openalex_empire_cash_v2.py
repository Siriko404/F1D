#!/usr/bin/env python3
"""v2: PROPER citation chase from confirmed DOIs (v1 anchor-by-title was broken).
Walk citers of Harford 1999, Erel-Jang-Minton-Weisbach 2019, Jensen 1986,
Almeida-Campello-Hackbarth 2011; keep those mentioning cash + acquisition +
DiD/natural-experiment; surface anything about ACCUMULATING/hoarding cash BEFORE.
"""
from __future__ import annotations
import csv
from pathlib import Path
from pyalex import Works, config

config.email = "lit-review@anthropic.local"
OUT = Path(__file__).resolve().parent
TOP_MD = OUT / "openalex_empire_cash_v2_top.md"

ANCHORS = {
    "Harford1999_JF":       "10.1111/0022-1082.00179",
    "ErelJMW2019_JFQA":     "10.1017/s0022109019000978",
    "Jensen1986_AER":       "10.2307/1818789",
    "ACH2011_LiqMergers":   "10.1016/j.jfineco.2011.08.002",  # Liquidity Mergers JFE
    "HMM2008_JFE":          "10.1016/j.jfineco.2007.04.002",  # try; guarded
    "DittmarMS2007_JF":     "10.1111/j.1540-6261.2007.01259.x",
}

def recon(inv):
    if not inv: return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs: pos[i] = w
    return " ".join(pos.get(i,"") for i in range(max(pos)+1)) if pos else ""

def rec(w):
    aus = [(a.get("author") or {}).get("display_name","") for a in (w.get("authorships") or [])[:5]]
    src = ((w.get("primary_location") or {}).get("source") or {})
    return {"title": w.get("title",""), "authors":"; ".join(a for a in aus if a),
            "year": w.get("publication_year",""), "venue": src.get("display_name",""),
            "cited_by": w.get("cited_by_count",0), "doi": w.get("doi",""),
            "id": w.get("id",""), "abstract": recon(w.get("abstract_inverted_index"))}

def citers_of(doi, n_max=600):
    try:
        a = Works()[f"https://doi.org/{doi}"]
    except Exception as e:
        print("  anchor MISS", doi, e); return None, []
    wid = a.get("id","").split("/")[-1]
    out = []
    try:
        for page in Works().filter(cites=wid).sort(cited_by_count="desc").paginate(per_page=200, n_max=n_max):
            out.extend(page)
    except Exception as e:
        print("  citer ERR", e)
    return rec(a), out

def main():
    seen, recs = set(), []
    for label, doi in ANCHORS.items():
        anchor, cit = citers_of(doi)
        if anchor is None: continue
        t = anchor["title"][:55].encode("ascii","replace").decode()
        print(f"{label}: anchor='{t}' ({anchor['year']}, {anchor['cited_by']} cites) -> {len(cit)} citers")
        for w in cit:
            wid = w.get("id","")
            if wid in seen: continue
            seen.add(wid); r = rec(w); r["src"] = label; recs.append(r)

    print(f"\nUnique citing works: {len(recs)}")

    def txt(r): return (r["title"]+" "+r["abstract"]).lower()
    CASH = ["cash holding","cash reserve","excess cash","cash-rich","cash rich","financial slack","cash accumulation","war chest","cash savings","liquidity"]
    ACQ  = ["acquisition","acquire","acquirer","merger","bidder","takeover","empire"]
    DID  = ["difference-in-differences","difference in differences","diff-in-diff","natural experiment","quasi-natural","quasi-experiment","exogenous shock","staggered","instrumental","instrument for","regression discontinuity"]
    BEFORE = ["before","prior to","accumulat","build up","build-up","stockpil","hoard","ex ante","run-up","run up","leading up","in anticipation","precede","pre-acquisition","pre-merger","save up","saving"]

    def hasany(r, terms): return any(t in txt(r) for t in terms)
    flagged = []
    for r in recs:
        r["f_cash"]=hasany(r,CASH); r["f_acq"]=hasany(r,ACQ); r["f_did"]=hasany(r,DID); r["f_before"]=hasany(r,BEFORE)
        if r["f_cash"] and r["f_acq"]:
            flagged.append(r)
    # rank: before-hoarding first, then DiD, then citations
    flagged.sort(key=lambda r: (-int(r["f_before"]), -int(r["f_did"]), -int(r["cited_by"] or 0)))

    with TOP_MD.open("w", encoding="utf-8") as f:
        f.write(f"# v2 citation-chase: cash + acquisition + DiD\n\nciting works {len(recs)}; cash&acq&did {len(flagged)}\n\n")
        for i,r in enumerate(flagged[:50],1):
            tags = " ".join([t for t,b in [("DiD",r["f_did"]),("BEFORE/hoard",r["f_before"])] if b])
            f.write(f"## {i}. {r['title']} ({r['year']}, {r['cited_by']} cites) [{tags}]\n")
            f.write(f"- {r['authors']}\n- {r['venue']} | DOI {r['doi']} | cites:{r['src']}\n- {r['abstract'][:700]}\n\n")
    print(f"wrote {TOP_MD}")

    print(f"\n=== cash&acq&DiD: {len(flagged)} | with BEFORE/hoard signal first ===")
    for i,r in enumerate(flagged[:22],1):
        b = "HOARD" if r["f_before"] else "     "
        line = f"[{i}] {b} {r['cited_by']:>4}c {r['year']} {(r['venue'] or '')[:30]} | {r['title'][:95]}"
        print(line.encode("ascii","replace").decode())

if __name__ == "__main__":
    main()
