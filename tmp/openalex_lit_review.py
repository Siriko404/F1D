"""Systematic OpenAlex novelty check (read-only).

Q: has anyone studied CEO/managerial SPEECH-BASED uncertainty (DWZ-style
"UncRes") as a determinant/correlate of corporate CASH HOLDINGS?

Precise title+abstract AND-search across axes + DWZ author paper + DWZ
forward-citations intersect cash. Dedupe; print compact candidates for
human relevance judgement. NO conclusions here.
"""
import io
import json
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")

MAILTO = "sinasoleimanipour@gmail.com"
BASE = "https://api.openalex.org/works"
SELECT = ("id,display_name,publication_year,cited_by_count,"
          "authorships,primary_location,abstract_inverted_index")

# title_and_abstract.search: space = AND, "..." = phrase.
TA_QUERIES = [
    '"cash holdings" managerial uncertainty',
    '"cash holdings" CEO uncertainty',
    '"cash holdings" "conference call" uncertainty',
    '"cash holdings" textual uncertainty',
    '"corporate liquidity" CEO uncertainty',
    '"precautionary" managerial uncertainty language',
    '"cash holdings" "earnings call" linguistic',
    '"cash holdings" manager uncertainty disclosure',
    '"cash holdings" CEO speech tone',
    'managerial uncertainty speech "corporate cash"',
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "lit-review"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def snip(inv, n=50):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos)[:n])


def auth(a):
    return ", ".join(x["author"]["display_name"] for x in a[:4]) + \
        (" et al." if len(a) > 4 else "")


def ven(loc):
    if loc and loc.get("source"):
        return loc["source"].get("display_name") or "?"
    return "?"


def ta_search(q, per_page=15, extra=""):
    f = urllib.parse.quote(f"title_and_abstract.search:{q}")
    url = (f"{BASE}?filter={f}&per-page={per_page}&select={SELECT}"
           f"&sort=relevance_score:desc&mailto={MAILTO}{extra}")
    try:
        return get(url).get("results", [])
    except Exception as e:  # noqa
        print(f"  !! {q!r} -> {e}")
        return []


seen = {}
print("=" * 80)
print("AXIS 1 — precise title+abstract AND-search (the two pillars)")
print("=" * 80)
for q in TA_QUERIES:
    res = ta_search(q)
    print(f"\n### [{q}]  ({len(res)} hits)")
    for w in res:
        wid = w["id"].split("/")[-1]
        dup = " (dup)" if wid in seen else ""
        seen.setdefault(wid, w)
        print(f"- ({w.get('publication_year')}) "
              f"[{w.get('cited_by_count',0)}c] {w.get('display_name')}{dup}")
        print(f"    {auth(w.get('authorships',[]))} | "
              f"{ven(w.get('primary_location'))} | {wid}")
        s = snip(w.get('abstract_inverted_index'))
        if s:
            print(f"    abs: {s}")
    time.sleep(0.35)

print("\n" + "=" * 80)
print("AXIS 2 — DWZ paper + forward-citations ∩ cash/liquidity")
print("=" * 80)
for dq in ('Dzielinski Wagner Zeckhauser uncertain',
           'Dzielinski Wagner Zeckhauser managerial uncertainty',
           'Dzielinski "asymmetric attention"'):
    for w in ta_search(dq, per_page=6):
        wid = w["id"].split("/")[-1]
        print(f"\nDWZ? ({w.get('publication_year')}) "
              f"[{w.get('cited_by_count',0)}c] {w.get('display_name')}")
        print(f"  {auth(w.get('authorships',[]))} | {wid}")
        ff = urllib.parse.quote("title_and_abstract.search:cash holdings "
                                "liquidity")
        furl = (f"{BASE}?filter=cites:{wid},{ff}"
                f"&per-page=12&select={SELECT}&mailto={MAILTO}")
        try:
            fwd = get(furl).get("results", [])
        except Exception as e:  # noqa
            fwd = []
            print(f"  !! fwd {e}")
        for x in fwd:
            print(f"   <-cited-by ({x.get('publication_year')}) "
                  f"[{x.get('cited_by_count',0)}c] {x.get('display_name')} | "
                  f"{auth(x.get('authorships',[]))}")
    time.sleep(0.35)

print(f"\n\nunique axis-1 works screened: {len(seen)}")
