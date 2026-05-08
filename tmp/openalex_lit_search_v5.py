#!/usr/bin/env python3
"""
v5: REFINED systematic lit review using lessons from 5 NLM verifications.

Refined criteria from v1-v4 + 5 NLM verifications:
1. POSITIVE-polarity shock (uncertainty UP -> cash UP)
2. MACRO or REGIONAL shock (not firm-specific events)
3. DiD with explicit treatment x post (drop OLS-only papers like Graham 2024)
4. US sample (drop China-only / global where measure heterogeneity blocks)
5. Sample period overlapping F1D 2002-2021
6. DV = cash holdings (CHE/AT or close), not valuation-of-cash regressions

Strategy:
A) Refined keyword sweep with shock-event keywords missed in v1-v4
B) New citation anchors: Campello-Brexit JFQA 2022, Bloom 2009 QJE
C) POLARITY-SENTINEL filter (drop opposite-polarity hits like Ghaly Katrina)
D) MECHANISM-FIT sentinel (drop firm-specific shocks like Chen Restatements)
E) Venue-tier ranking (JF/JFE/RFS/JFQA/RAST top, others tier-2)
"""

from __future__ import annotations
import csv
from pathlib import Path
from pyalex import Works, config

config.email = "lit-review@anthropic.local"

OUT_DIR = Path(__file__).resolve().parent
RESULTS_CSV = OUT_DIR / "openalex_v5_results.csv"
TOP_MD = OUT_DIR / "openalex_v5_top.md"

# v5 NEW citation anchors (positive-polarity uncertainty -> cash)
ANCHORS = {
    "CampelloBrexit_JFQA22": "10.1017/S0022109021000600",  # Campello et al 2022 JFQA Brexit
    "Bloom2009_QJE":        "10.3982/ECTA6248",             # Bloom 2009 Econometrica uncertainty shocks
    "ACW2004_JF":           "10.1111/j.1540-6261.2004.00679.x",
    "BKS2009_JF":           "10.1111/j.1540-6261.2009.01492.x",
    "FaulkenderWang2006":   "10.1111/j.1540-6261.2006.00894.x",
    "HHLT2019_QJE":         "10.1093/qje/qjz021",
    "Hasan2022_RQFA":       "10.1007/s11156-022-01049-9",
    "Phan2021_BJM":         "10.1080/13571516.2020.1851140",  # EPU + cash COVID
}

# v5 REFINED queries — focus on positive-polarity + macro/regional + US + DiD
# F1D WINDOW = 2002-01-16 to 2018-12-22. Drop post-2018 shocks.
QUERIES = [
    # ====== Pre-2018 macro shocks (full F1D-overlap power) ======

    # 2011 debt-ceiling crisis (Aug 2011) — clean exogenous fiscal shock
    'debt ceiling 2011 "cash holdings" DiD firm precautionary',
    'debt ceiling crisis "cash holdings" U.S. firms uncertainty',

    # 2013 government shutdown (Oct 2013) — fiscal-policy uncertainty
    'government shutdown 2013 "cash holdings" DiD firm',
    'government shutdown "cash holdings" precautionary U.S. firms',

    # 2013 Fed taper tantrum (May-Jun 2013)
    'Fed taper tantrum "cash holdings" DiD firm',
    'monetary policy taper "cash holdings" DiD U.S. firms',

    # Fiscal cliff (Dec 2012 / Jan 2013)
    'fiscal cliff "cash holdings" U.S. firms DiD precautionary',
    'sequestration "cash holdings" DiD firm uncertainty',

    # Eurozone sovereign debt crisis (2010-2012) — US-firm spillover
    'Eurozone crisis "cash holdings" U.S. firms DiD spillover',
    'European debt crisis "cash holdings" American firms DiD',

    # 2014 oil-price collapse (Nov 2014) — sector-DiD
    'oil price collapse "cash holdings" DiD firm 2014 precautionary',
    'oil shock "cash holdings" DiD U.S. firms precautionary',

    # 2008-2009 financial crisis (start of F1D window)
    'financial crisis 2008 "cash holdings" DiD firm precautionary',
    'TARP "cash holdings" DiD firm precautionary',
    'lehman "cash holdings" DiD firm precautionary',

    # State-level policy shocks (sub-national DiD, valid pre-2018)
    'state-level "minimum wage" "cash holdings" DiD precautionary',
    '"right to work" "cash holdings" DiD firm precautionary',
    'state-level uncertainty "cash holdings" DiD difference',
    'gubernatorial election "cash holdings" DiD precautionary US',

    # Banking + financial shocks (pre-2018)
    'banking deregulation "cash holdings" DiD firm',
    'Dodd-Frank "cash holdings" DiD firm precautionary',
    'banking crisis "cash holdings" DiD firm 2008',

    # Brexit (Jun 2016) — explicitly forward-cite Campello design space
    'Brexit "cash holdings" U.S. firms DiD precautionary',
    'EU referendum "cash holdings" U.S. firms DiD',
    'Brexit uncertainty firm "cash holdings" American',

    # SOX + accounting regulatory (start of F1D)
    'SOX 2002 "cash holdings" DiD precautionary firm',
    'Sarbanes-Oxley "cash holdings" precautionary DiD US',

    # Industry/import-competition — China shock 2001-2010 well-documented
    'China import competition "cash holdings" DiD precautionary U.S.',
    'China shock "cash holdings" DiD U.S. firms',
    'import penetration "cash holdings" DiD precautionary firm U.S.',

    # Climate / disaster (regional, US-only, pre-2018)
    'hurricane Sandy "cash holdings" DiD U.S. firms precautionary',
    'hurricane Katrina "cash holdings" DiD U.S. firms precautionary',
    'wildfire "cash holdings" U.S. firms DiD precautionary',
    'natural disaster "cash holdings" U.S. firms DiD precautionary',
    'flood "cash holdings" U.S. firms DiD precautionary',

    # Local policy uncertainty
    'school finance reform "cash holdings" DiD firm',
    'local political uncertainty "cash holdings" firm DiD',
    'Citizens United "cash holdings" firm DiD',

    # Healthcare / regulatory
    'Affordable Care Act "cash holdings" DiD firm',
    'environmental regulation "cash holdings" DiD U.S. firm precautionary',
    'EPA regulation "cash holdings" U.S. firms DiD',

    # CEO / labor shocks (positive-polarity only)
    'state firing costs "cash holdings" DiD precautionary US',

    # Trump-era 2017-2018 (POWER-LIMITED — only ~4 post quarters in F1D window)
    'Trump tariff 2018 "cash holdings" DiD firm precautionary',
    'TCJA 2017 "cash holdings" DiD firm precautionary',

    # Hassan PRisk forward apps
    '"firm-level political risk" "cash holdings" DiD difference U.S.',

    # 9/11 + early-2000s shocks
    '"September 11" "cash holdings" U.S. firms DiD',
    '"dot-com bust" "cash holdings" DiD precautionary U.S.',

    # Election-event DiDs (other than Trump 2016, which had 0 hits)
    'Bush v. Gore 2000 "cash holdings" firm DiD',
    'presidential election uncertainty "cash holdings" DiD U.S.',
    'election cycle "cash holdings" DiD U.S. firms precautionary',
]

YEAR_MIN = 2010

# =======================================================================
# POLARITY SENTINEL — drop hits where abstract suggests cash DECREASES
# =======================================================================
NEGATIVE_POLARITY_PHRASES = [
    "cash holdings decrease",
    "cash holdings decline",
    "decrease in cash",
    "decline in cash",
    "lower cash holdings",
    "less cash",
    "reduces cash",
    "reduction in cash",
    "fewer cash",
    "reduced cash",
    "cash reduction",
    "cash decline",
    "cash decrease",
    "negative effect on cash",
    "negatively associated with cash",
]

POSITIVE_POLARITY_PHRASES = [
    "cash holdings increase",
    "increase cash holdings",
    "more cash",
    "higher cash",
    "increase in cash",
    "rise in cash",
    "raises cash",
    "raise cash",
    "cash rise",
    "cash increase",
    "positive effect on cash",
    "positively associated with cash",
    "cash savings",
    "hold more cash",
    "save more",
    "additional cash",
]

# =======================================================================
# MECHANISM-FIT SENTINEL — drop firm-specific event-driven shocks
# =======================================================================
FIRM_SPECIFIC_TERMS = [
    "restatement", "earnings management", "fraud",
    "lawsuit", "class action", "securities class",
    "scandal", "ceo turnover", "ceo departure",
    "ceo death", "individual ceo",
    "merger announcement", "acquisition target",
    "spin-off", "spinoff", "bankruptcy filing",
    "credit rating downgrade",
]

MACRO_REGIONAL_SHOCK_TERMS = [
    "tariff", "trade war", "trade policy",
    "covid", "pandemic", "lockdown",
    "brexit", "eu referendum",
    "election", "presidential", "gubernatorial",
    "tax cuts and jobs act", "tcja", "sarbanes-oxley", "sox",
    "dodd-frank", "deregulation",
    "minimum wage", "right to work",
    "hurricane", "wildfire", "flood", "natural disaster",
    "climate policy", "environmental regulation",
    "section 232", "section 301", "import competition",
    "geopolitical", "russia ukraine", "war",
    "economic policy uncertainty", "epu",
    "monetary policy",
    "school finance",
    "wrongful discharge",
]

# =======================================================================
# US-ONLY sentinel
# =======================================================================
NON_US_TERMS = [
    "china", "chinese firms", "a-share",
    "korea", "korean firms",
    "india", "indian firms",
    "europe", "european firms",  # ambiguous — used cautiously
    "japan", "japanese firms",
    "uk firms", "british firms", "australian",
    "global evidence", "international evidence",
    "cross-country",
    "41 countries", "g7",
]

US_TERMS = [
    "u.s.", "us firms", "american firms",
    "united states", "compustat",
]


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
    print("Phase A: refined keyword sweep")
    print("=" * 70)
    for q_idx, query in enumerate(QUERIES, 1):
        print(f"\n[{q_idx}/{len(QUERIES)}] {query!r}")
        results = fetch_query(query, max_results=25)
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
    print("Phase B: citation chase from positive-polarity anchors")
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

    # =====================================================================
    # FILTER FUNNEL
    # =====================================================================
    def low(s): return (s or "").lower()
    def text(r): return low(r.get("abstract", "")) + " " + low(r.get("title", ""))

    cash_terms = ['cash holding', 'corporate cash', 'cash reserve', 'cash policy',
                  'precautionary cash', 'cash position', 'firm liquidity',
                  'cash-to-asset', 'cash savings', 'cash hoarding']
    did_terms = ['difference-in-differences', 'difference in differences',
                 'diff-in-diff', 'natural experiment', 'quasi-experiment',
                 'quasi-natural', 'exogenous shock', 'treatment group',
                 'staggered']
    precaut_terms = ['precautionary', 'precaution', 'hedging needs',
                     'risk management', 'uncertainty', 'cash flow volatility',
                     'financing constraint', 'financing friction',
                     'liquidity buffer']

    def has_any(r, terms): return any(s in text(r) for s in terms)
    def has_neg_polarity(r): return any(s in low(r.get("abstract","")) for s in NEGATIVE_POLARITY_PHRASES)
    def has_pos_polarity(r): return any(s in low(r.get("abstract","")) for s in POSITIVE_POLARITY_PHRASES)
    def has_firm_specific(r): return any(s in text(r) for s in FIRM_SPECIFIC_TERMS)
    def has_macro_shock(r): return any(s in text(r) for s in MACRO_REGIONAL_SHOCK_TERMS)
    def has_non_us(r): return any(s in text(r) for s in NON_US_TERMS)
    def has_us(r): return any(s in text(r) for s in US_TERMS)

    cash_pap = [r for r in all_records if has_any(r, cash_terms)]
    cash_did = [r for r in cash_pap if has_any(r, did_terms)]
    cash_did_prec = [r for r in cash_did if has_any(r, precaut_terms)]

    # Apply NEW v5 filters
    pos_polarity = [r for r in cash_did_prec if has_pos_polarity(r) and not has_neg_polarity(r)]
    macro_shock = [r for r in pos_polarity if has_macro_shock(r) and not has_firm_specific(r)]
    us_only = [r for r in macro_shock if has_us(r) and not has_non_us(r)]

    print(f"\nFilter funnel (v5):")
    print(f"  Mentions cash terms:                          {len(cash_pap)}")
    print(f"  + DiD-style identification:                   {len(cash_did)}")
    print(f"  + precautionary channel:                      {len(cash_did_prec)}")
    print(f"  + POSITIVE polarity (cash UP):                {len(pos_polarity)}")
    print(f"  + MACRO/REGIONAL shock (not firm-specific):   {len(macro_shock)}")
    print(f"  + US-only sample:                             {len(us_only)}")

    # Sort by citations desc
    us_only.sort(key=lambda r: -int(r['cited_by'] or 0))
    macro_shock.sort(key=lambda r: -int(r['cited_by'] or 0))
    pos_polarity.sort(key=lambda r: -int(r['cited_by'] or 0))

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
        f.write("# OpenAlex v5 - REFINED shock-DiD-cash-precautionary search\n\n")
        f.write(f"Total unique works: {len(all_records)}\n\n")
        f.write(f"Filter funnel:\n")
        f.write(f"- Cash + DiD + precautionary: {len(cash_did_prec)}\n")
        f.write(f"- + Positive polarity: {len(pos_polarity)}\n")
        f.write(f"- + Macro/regional shock: {len(macro_shock)}\n")
        f.write(f"- + US-only sample: **{len(us_only)}**\n\n")
        f.write("Ranked by citations.\n\n")

        f.write("## Tier 1: US + macro shock + positive polarity + cash + DiD + precautionary\n\n")
        for i, r in enumerate(us_only[:60], 1):
            f.write(f"### {i}. {r['title']} ({r['year']}, {r['cited_by']} cites)\n\n")
            f.write(f"- Authors: {r['authors']}\n")
            f.write(f"- Venue: {r['venue']}\n")
            f.write(f"- DOI: {r['doi']}\n")
            f.write(f"- OA: {r['is_oa']} | URL: {r.get('oa_url','')}\n")
            f.write(f"- Source: {r['source']}\n\n")
            ab = r.get('abstract', '') or '(none)'
            f.write(f"**Abstract:** {ab}\n\n---\n\n")

        f.write("\n\n## Tier 2: macro shock + positive polarity + cash + DiD + precautionary (no US filter)\n\n")
        non_us_macro = [r for r in macro_shock if r not in us_only]
        for i, r in enumerate(non_us_macro[:30], 1):
            f.write(f"### {i}. {r['title']} ({r['year']}, {r['cited_by']} cites)\n")
            f.write(f"- {r['venue']} | DOI {r['doi']}\n")
            ab = (r.get('abstract','') or '')[:400]
            f.write(f"- Abstract: {ab}\n\n")

    print(f"Wrote {TOP_MD}")

    # Console: top 20 US-only
    print("\n=== TOP 20 US-ONLY (positive-polarity, macro shock, cash+DiD+precautionary) ===")
    for i, r in enumerate(us_only[:20], 1):
        print(f"\n[{i}] {r['cited_by']} cites | {r['year']} | {r['venue'][:35]}")
        print(f"    {r['title'][:130]}")
        print(f"    DOI: {r['doi']}")
        ab = (r.get('abstract','') or '')[:250]
        print(f"    {ab}")


if __name__ == "__main__":
    main()
