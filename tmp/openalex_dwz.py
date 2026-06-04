"""Locate the Dzielinski-Wagner-Zeckhauser (DWZ) CEO-speech-uncertainty
paper(s) and screen ALL forward citations for a cash-holdings / liquidity
application. Decisive axis of the novelty check. Read-only.
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
SELECT = ("id,display_name,publication_year,cited_by_count,authorships,"
          "primary_location,abstract_inverted_index")


def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "lit-review"})
    with urllib.request.urlopen(r, timeout=45) as x:
        return json.loads(x.read().decode())


def auth(a):
    return ", ".join(p["author"]["display_name"] for p in a[:5]) + \
        (" et al." if len(a) > 5 else "")


def snip(inv, n=45):
    if not inv:
        return ""
    pos = {}
    for w, ix in inv.items():
        for i in ix:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos)[:n])


def works(filt, pp=50, extra=""):
    u = (f"{BASE}?filter={urllib.parse.quote(filt, safe=':,')}"
         f"&per-page={pp}&select={SELECT}&mailto={MAILTO}{extra}")
    try:
        return get(u).get("results", [])
    except Exception as e:  # noqa
        print(f"  !! {filt} -> {e}")
        return []


# 1) Dzielinski catalogue (rare surname; the trio's anchor author)
print("=" * 80)
print("DWZ — Jan Dzielinski catalogue (author search)")
print("=" * 80)
cat = works("raw_author_name.search:Dzielinski", pp=50)
dwz_ids = []
for w in sorted(cat, key=lambda x: -(x.get("cited_by_count") or 0)):
    wid = w["id"].split("/")[-1]
    aus = auth(w.get("authorships", []))
    title = w.get("display_name") or ""
    print(f"- ({w.get('publication_year')}) [{w.get('cited_by_count',0)}c] "
          f"{title}\n    {aus} | {wid}")
    tl = title.lower()
    if any(k in tl for k in ("uncertain", "talk", "clarity", "vague",
                             "speak", "communicat", "attention", "ceo",
                             "manager", "word")):
        dwz_ids.append((wid, title, w.get("cited_by_count", 0)))
    time.sleep(0.05)

print("\nDWZ candidate measure-papers (title-keyword flagged):")
for wid, t, c in dwz_ids:
    print(f"  * {wid} [{c}c] {t}")

# 2) Forward citations of each candidate, screened for cash/liquidity
print("\n" + "=" * 80)
print("FORWARD CITATIONS ∩ cash/liquidity/precautionary")
print("=" * 80)
CASH = ("cash holding liquidity precautionary corporate cash savings "
        "financial policy")
for wid, t, c in dwz_ids:
    print(f"\n### cites:{wid}  «{t[:70]}» ({c} total cites)")
    f = (f"cites:{wid},"
         f"title_and_abstract.search:{CASH}")
    fwd = works(f, pp=40)
    if not fwd:
        # broader: ALL citing works, we screen titles ourselves
        allc = works(f"cites:{wid}", pp=200)
        hits = [w for w in allc if any(
            k in (w.get("display_name") or "").lower()
            for k in ("cash", "liquid", "precaution", "savings",
                      "financial polic"))]
        print(f"  (no TA-filtered hits; scanned {len(allc)} citing works, "
              f"{len(hits)} title-matched)")
        fwd = hits
    for w in fwd:
        print(f"  <- ({w.get('publication_year')}) "
              f"[{w.get('cited_by_count',0)}c] {w.get('display_name')}")
        print(f"     {auth(w.get('authorships',[]))}")
        s = snip(w.get("abstract_inverted_index"))
        if s:
            print(f"     abs: {s}")
    time.sleep(0.3)

# 3) direct construct phrasings
print("\n" + "=" * 80)
print("DIRECT construct phrasings (title+abstract AND)")
print("=" * 80)
for q in ('"CEO uncertainty" "cash holdings"',
          'CEO "I don\'t know" uncertainty earnings call cash',
          'managerial vagueness uncertainty cash holdings',
          'executive linguistic uncertainty precautionary savings',
          '"uncertain CEO" liquidity cash'):
    rs = works(f"title_and_abstract.search:{q}", pp=10,
               extra="&sort=relevance_score:desc")
    print(f"\n[{q}] ({len(rs)})")
    for w in rs:
        print(f"  - ({w.get('publication_year')}) "
              f"[{w.get('cited_by_count',0)}c] {w.get('display_name')} | "
              f"{auth(w.get('authorships',[]))}")
    time.sleep(0.3)
