"""Resolve Michal Dzielinski (finance) author entity, enumerate his works,
locate the Dzielinski-Wagner-Zeckhauser CEO-uncertainty paper, screen its
forward citations for a cash-holdings application. Read-only.
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
AU = "https://api.openalex.org/authors"
WK = "https://api.openalex.org/works"
SEL = ("id,display_name,publication_year,cited_by_count,authorships,"
       "primary_location,abstract_inverted_index")


def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "lit-review"})
    with urllib.request.urlopen(r, timeout=45) as x:
        return json.loads(x.read().decode())


def auth(a):
    return ", ".join(p["author"]["display_name"] for p in a[:6]) + \
        (" et al." if len(a) > 6 else "")


def snip(inv, n=55):
    if not inv:
        return ""
    pos = {}
    for w, ix in inv.items():
        for i in ix:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos)[:n])


# 1) resolve author candidates
print("=" * 80)
print("AUTHOR RESOLUTION — Dzielinski")
print("=" * 80)
a = get(f"{AU}?search=Michal%20Dzielinski&per-page=10&mailto={MAILTO}")
fin_id = None
for x in a.get("results", []):
    inst = (x.get("last_known_institutions") or [{}])
    inst = inst[0].get("display_name") if inst else "?"
    tops = ", ".join(c["display_name"]
                     for c in (x.get("x_concepts") or [])[:5])
    print(f"- {x['display_name']} | {x['id'].split('/')[-1]} | "
          f"works={x.get('works_count')} cites={x.get('cited_by_count')} | "
          f"{inst}\n    concepts: {tops}")
    if fin_id is None and any(k in tops.lower() for k in
                              ("financ", "economic", "account")):
        fin_id = x["id"].split("/")[-1]
print(f"\n-> finance author id: {fin_id}")

# 2) all works of that author
print("\n" + "=" * 80)
print("WORKS of finance Dzielinski (flag Wagner/Zeckhauser co-author)")
print("=" * 80)
flagged = []
if fin_id:
    ws = get(f"{WK}?filter=author.id:{fin_id}&per-page=100&select={SEL}"
             f"&mailto={MAILTO}").get("results", [])
    for w in sorted(ws, key=lambda v: -(v.get('cited_by_count') or 0)):
        aus = auth(w.get("authorships", []))
        t = w.get("display_name") or ""
        wid = w["id"].split("/")[-1]
        mark = ""
        if ("zeckhauser" in aus.lower() or "wagner" in aus.lower()):
            mark = "  <<< DWZ CO-AUTHOR"
            flagged.append((wid, t, w.get("cited_by_count", 0)))
        elif any(k in t.lower() for k in
                 ("uncertain", "talk", "clarity", "vague", "ceo",
                  "manager", "communicat", "speak")):
            mark = "  <<< measure-candidate"
            flagged.append((wid, t, w.get("cited_by_count", 0)))
        print(f"- ({w.get('publication_year')}) [{w.get('cited_by_count',0)}c]"
              f" {t}{mark}\n    {aus} | {wid}")

# 3) generic fallback for the trio paper
print("\n" + "=" * 80)
print("GENERIC fallback search: Dzielinski Wagner Zeckhauser")
print("=" * 80)
g = get(f"{WK}?search=Dzielinski%20Wagner%20Zeckhauser%20managerial"
        f"%20uncertainty&per-page=10&select={SEL}&mailto={MAILTO}")
for w in g.get("results", []):
    aus = auth(w.get("authorships", []))
    t = w.get("display_name") or ""
    wid = w["id"].split("/")[-1]
    if any(k in aus.lower() for k in ("zeckhauser", "wagner", "dzielin")):
        print(f"- ({w.get('publication_year')}) [{w.get('cited_by_count',0)}c]"
              f" {t}\n    {aus} | {wid}")
        if wid not in [f[0] for f in flagged]:
            flagged.append((wid, t, w.get("cited_by_count", 0)))

# 4) forward citations of flagged DWZ paper(s) ∩ cash
print("\n" + "=" * 80)
print("FORWARD CITATIONS of DWZ paper(s) ∩ cash/liquidity")
print("=" * 80)
for wid, t, c in flagged:
    print(f"\n### cites:{wid}  «{t[:75]}» ({c}c)")
    allc = get(f"{WK}?filter=cites:{wid}&per-page=200&select={SEL}"
               f"&mailto={MAILTO}").get("results", [])
    hits = [w for w in allc if any(
        k in ((w.get("display_name") or "") + " " +
              snip(w.get("abstract_inverted_index"), 60)).lower()
        for k in ("cash holding", "cash holdings", "corporate cash",
                  "liquidity", "precautionary", "cash policy"))]
    print(f"  citing works scanned: {len(allc)} | cash/liquidity-matched: "
          f"{len(hits)}")
    for w in hits:
        print(f"  <- ({w.get('publication_year')}) "
              f"[{w.get('cited_by_count',0)}c] {w.get('display_name')}")
        print(f"     {auth(w.get('authorships',[]))}")
        s = snip(w.get("abstract_inverted_index"))
        if s:
            print(f"     abs: {s}")
    time.sleep(0.3)
