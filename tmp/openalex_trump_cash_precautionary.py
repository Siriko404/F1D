"""Systematic OpenAlex lit review (read-only).

Q: Is there a study running a DiD on the Trump 2016 election surprise and
   CORPORATE CASH HOLDINGS via the PRECAUTIONARY channel?

Strategy (advisor-vetted):
  - Axis A: title_and_abstract AND-search over EVENT x OUTCOME (NOT method;
    "DiD"/"difference-in-differences" rarely in title/abstract -> screen
    method from abstract post-hoc). Mechanism added as optional, not forced.
  - Axis B: forward-citation harvest of strong anchors (policy-uncertainty /
    election-DiD / precautionary-cash lineage); screen citations locally for
    cash|liquid|precaution|savings.
  - Dedupe by OpenAlex work id; score keyword presence on title+abstract on
    4 axes (event / outcome / mechanism / method); tier.

Output (raw to sandbox, no hand transcription):
  tmp/openalex_trump_cash_<ts>/raw_*.json   (full records per query/anchor)
  tmp/openalex_trump_cash_review_<ts>.md    (4-tier ranked report)
Stdout: short per-block summary only.
"""
from __future__ import annotations

import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")

MAILTO = "sinasoleimanipour@gmail.com"
BASE = "https://api.openalex.org/works"
SELECT = ("id,display_name,publication_year,cited_by_count,authorships,"
          "primary_location,doi,abstract_inverted_index")

TS = datetime.now().strftime("%Y-%m-%d_%H%M%S")
ROOT = Path(__file__).resolve().parent
RAW = ROOT / f"openalex_trump_cash_{TS}"
RAW.mkdir(parents=True, exist_ok=True)
REPORT = ROOT / f"openalex_trump_cash_review_{TS}.md"

# --- AXIS A: title+abstract AND-search (event x outcome [x mechanism]) ------
# space = AND, "..." = phrase. NO method term ANDed (advisor: silent drop).
EVENT = [
    '"Trump election"', '"2016 election"', '"2016 presidential election"',
    '"presidential election" surprise', '"election surprise"',
    '"Trump shock"', '"Trump victory"', '"Trump presidency"',
    '"Trump administration"', '"economic policy uncertainty"',
    '"policy uncertainty"', '"political uncertainty"',
    '"electoral uncertainty"', '"election uncertainty"',
    '"firm-level political risk"',
]
OUTCOME = [
    '"cash holdings"', '"corporate cash"', '"cash reserves"',
    '"corporate liquidity"', '"cash policy"', '"cash savings"',
    '"precautionary"',
]
# A few high-precision triples (event + outcome + mechanism/method word).
TRIPLES = [
    '"Trump election" "cash holdings"',
    '"2016 election" "cash holdings"',
    '"policy uncertainty" "cash holdings" precautionary',
    '"political uncertainty" "corporate cash" precautionary',
    '"economic policy uncertainty" "cash holdings"',
    '"election" "cash holdings" difference-in-differences',
    '"political uncertainty" "cash holdings" "natural experiment"',
    '"Trump" "precautionary" cash',
    '"2016 presidential election" corporate cash',
    '"firm-level political risk" cash holdings',
]

# --- AXIS B: anchor papers for forward-citation harvest --------------------
# Resolve by title search; harvest citing works; screen cash|liquid|precaution.
ANCHORS = [
    'Gulen Ion policy uncertainty corporate investment',
    'Baker Bloom Davis measuring economic policy uncertainty',
    'Jens political uncertainty investment gubernatorial elections',
    'Bonaime Gulen Ion policy uncertainty mergers acquisitions',
    'Nguyen Phan policy uncertainty mergers acquisitions',
    'Hassan Hollander van Lent Tahoun firm-level political risk',
    'Pastor Veronesi political uncertainty stock returns',
    'Acharya Almeida Campello aggregate risk corporate cash',
    'Hu Kang Li Lin Trump election minority CEO',
    'Bates Kahle Stulz why do US firms hold so much cash',
    'Duong Nguyen policy uncertainty cash holdings',
    'Demir Ersan economic policy uncertainty cash holdings emerging',
]

EVENT_RE = re.compile(
    r"\btrump\b|2016 (presidential )?election|election surprise|"
    r"\bbrexit\b|policy uncertainty|political uncertainty|"
    r"electoral uncertainty|election uncertainty|political risk|"
    r"gubernatorial election|presidential election", re.I)
OUTCOME_RE = re.compile(
    r"cash holding|corporate cash|cash reserve|cash polic|cash saving|"
    r"corporate liquidity|liquid asset|financial slack|\bcash\b", re.I)
MECH_RE = re.compile(r"precaution|hedg|buffer|liquidity management|"
                     r"risk management", re.I)
METHOD_RE = re.compile(
    r"difference[- ]in[- ]difference|diff[- ]in[- ]diff|\bdid\b|"
    r"natural experiment|quasi[- ]experiment|quasi[- ]natural|"
    r"staggered|exogenous shock|triple difference", re.I)


def get(url, tries=3):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "lit-review"})
            with urllib.request.urlopen(req, timeout=50) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa
            last = e
            time.sleep(1.0 + k)
    print(f"  !! GET fail: {last}")
    return {}


def deinv(inv, n=400):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos)[:n])


def auth(a):
    return ", ".join(x["author"]["display_name"] for x in a[:5]) + \
        (" et al." if len(a) > 5 else "")


def ven(loc):
    if loc and loc.get("source"):
        return loc["source"].get("display_name") or "?"
    return "?"


def ta(q, per_page=25):
    f = urllib.parse.quote(f"title_and_abstract.search:{q}")
    url = (f"{BASE}?filter={f}&per-page={per_page}&select={SELECT}"
           f"&sort=relevance_score:desc&mailto={MAILTO}")
    return get(url).get("results", []) or []


def cited_search(q, per_page=5):
    """relevance search to resolve an anchor work id."""
    f = urllib.parse.quote(f"title_and_abstract.search:{q}")
    url = (f"{BASE}?filter={f}&per-page={per_page}&select={SELECT}"
           f"&sort=cited_by_count:desc&mailto={MAILTO}")
    return get(url).get("results", []) or []


def harvest_cites(wid, cap=600):
    """All citing works (paginate via cursor)."""
    out, cur = [], "*"
    while cur and len(out) < cap:
        url = (f"{BASE}?filter=cites:{wid}&per-page=200&select={SELECT}"
               f"&cursor={urllib.parse.quote(cur)}&mailto={MAILTO}")
        d = get(url)
        out.extend(d.get("results", []) or [])
        cur = (d.get("meta") or {}).get("next_cursor")
        time.sleep(0.25)
    return out


def record(w):
    wid = w["id"].split("/")[-1]
    txt = ((w.get("display_name") or "") + " " +
           deinv(w.get("abstract_inverted_index")))
    tl = txt.lower()
    ev = bool(EVENT_RE.search(tl))
    oc = bool(OUTCOME_RE.search(tl))
    me = bool(MECH_RE.search(tl))
    md = bool(METHOD_RE.search(tl))
    trump = bool(re.search(r"\btrump\b|2016 (presidential )?election|"
                           r"election surprise", tl))
    return {
        "wid": wid, "year": w.get("publication_year"),
        "cites": w.get("cited_by_count", 0),
        "title": w.get("display_name"),
        "authors": auth(w.get("authorships", [])),
        "venue": ven(w.get("primary_location")),
        "doi": w.get("doi"),
        "axes": {"event": ev, "trump": trump, "outcome": oc,
                 "mech": me, "method": md},
        "abstract": deinv(w.get("abstract_inverted_index"), 120),
    }


def tier(r):
    a = r["axes"]
    if a["trump"] and a["outcome"] and a["method"] and a["mech"]:
        return 1  # exact: Trump2016 + cash + DiD-method + precautionary
    if a["trump"] and a["outcome"] and (a["method"] or a["mech"]):
        return 1
    if (a["trump"] and a["outcome"]) or \
       (a["event"] and a["outcome"] and a["method"] and a["mech"]):
        return 2  # strong adjacent
    if a["event"] and a["outcome"] and (a["method"] or a["mech"]):
        return 3  # methodological precedent (other shock + cash + DiD)
    if a["event"] and a["outcome"]:
        return 4  # theoretical antecedent (polit/policy unc + cash)
    return 0


seen = {}


def add(w, src):
    wid = w["id"].split("/")[-1]
    if wid in seen:
        seen[wid]["src"].add(src)
        return
    r = record(w)
    r["src"] = {src}
    seen[wid] = r


# ---- AXIS A -----------------------------------------------------------------
print("AXIS A — title+abstract AND-search (event x outcome)")
qa = 0
for ev in EVENT:
    for oc in OUTCOME:
        q = f"{ev} {oc}"
        res = ta(q, per_page=20)
        for w in res:
            add(w, f"A:{q}")
        qa += 1
        if res:
            (RAW / f"rawA_{qa:03d}.json").write_text(
                json.dumps({"q": q, "n": len(res),
                            "ids": [x["id"].split("/")[-1] for x in res]},
                           indent=1), encoding="utf-8")
        time.sleep(0.30)
for q in TRIPLES:
    res = ta(q, per_page=20)
    for w in res:
        add(w, f"A3:{q}")
    time.sleep(0.30)
print(f"  axis-A queries: {qa + len(TRIPLES)} | unique works so far: "
      f"{len(seen)}")

# ---- AXIS B -----------------------------------------------------------------
print("AXIS B — forward-citation harvest of anchors (screen cash/precaution)")
anchor_log = []
for aq in ANCHORS:
    cand = cited_search(aq, per_page=5)
    if not cand:
        anchor_log.append({"anchor": aq, "resolved": None})
        continue
    top = cand[0]
    wid = top["id"].split("/")[-1]
    citing = harvest_cites(wid, cap=600)
    kept = 0
    for w in citing:
        tl = ((w.get("display_name") or "") + " " +
              deinv(w.get("abstract_inverted_index"))).lower()
        if OUTCOME_RE.search(tl) or MECH_RE.search(tl):
            add(w, f"B:{wid}")
            kept += 1
    anchor_log.append({
        "anchor": aq, "resolved_title": top.get("display_name"),
        "wid": wid, "anchor_cites": top.get("cited_by_count"),
        "citing_scanned": len(citing), "cash_screened_kept": kept})
    print(f"  [{wid}] {(top.get('display_name') or '')[:60]!r} "
          f"cited={top.get('cited_by_count')} scanned={len(citing)} "
          f"kept={kept}")
    time.sleep(0.3)
(RAW / "anchor_log.json").write_text(json.dumps(anchor_log, indent=1),
                                     encoding="utf-8")

# ---- TIER + REPORT ----------------------------------------------------------
for wid, r in seen.items():
    r["tier"] = tier(r)
    r["src"] = sorted(r["src"])
(RAW / "all_scored.json").write_text(
    json.dumps(list(seen.values()), indent=1), encoding="utf-8")

tiers = {1: [], 2: [], 3: [], 4: [], 0: []}
for r in seen.values():
    tiers[r["tier"]].append(r)
for t in tiers:
    tiers[t].sort(key=lambda x: (-(x["year"] or 0), -(x["cites"] or 0)))

TIER_NAME = {
    1: "TIER 1 — EXACT (Trump 2016 + cash + DiD/quasi-exp + precautionary)",
    2: "TIER 2 — STRONG ADJACENT (Trump 2016 + cash; or election-unc + "
       "cash + method + mechanism)",
    3: "TIER 3 — METHOD PRECEDENT (other election / policy-unc shock + "
       "cash + DiD/quasi-exp)",
    4: "TIER 4 — THEORETICAL ANTECEDENT (political/policy uncertainty + "
       "cash, any method)",
}
lines = [
    "# OpenAlex systematic review — Trump 2016 DiD x cash holdings x "
    "precautionary",
    "",
    f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}  |  unique works "
    f"screened: {len(seen)}",
    "",
    "Method: axis-A title+abstract AND-search (event x outcome, NO method "
    "ANDed); axis-B forward-citation harvest of "
    f"{len(ANCHORS)} anchors screened on cash/precaution. Tiering by "
    "keyword-presence on title+abstract (event/trump, outcome, mechanism, "
    "method) — see code regexes. Method/precautionary often only in body, "
    "so tiering is recall-biased; read abstracts before citing.",
    "",
    "| Tier | N |",
    "|------|---|",
    f"| 1 exact | {len(tiers[1])} |",
    f"| 2 strong adjacent | {len(tiers[2])} |",
    f"| 3 method precedent | {len(tiers[3])} |",
    f"| 4 theoretical antecedent | {len(tiers[4])} |",
    "",
]
for t in (1, 2, 3, 4):
    lines.append(f"## {TIER_NAME[t]}  ({len(tiers[t])})")
    lines.append("")
    if not tiers[t]:
        lines.append("_none_")
        lines.append("")
        continue
    show = tiers[t] if t in (1, 2) else tiers[t][:40]
    for r in show:
        ax = r["axes"]
        flag = "".join(k[0].upper() for k in
                       ("trump", "outcome", "mech", "method") if ax[k])
        lines.append(
            f"- **({r['year']})** [{r['cites']}c] {r['title']}  \n"
            f"  {r['authors']} · _{r['venue']}_ · `{r['wid']}` · "
            f"{r['doi'] or ''}  \n"
            f"  axes=[{flag}]  src={r['src'][:2]}  \n"
            f"  abs: {r['abstract'][:340]}")
    if t not in (1, 2) and len(tiers[t]) > 40:
        lines.append(f"\n_(+{len(tiers[t]) - 40} more in "
                      f"{RAW.name}/all_scored.json)_")
    lines.append("")

REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"\nTIER COUNTS  T1={len(tiers[1])}  T2={len(tiers[2])}  "
      f"T3={len(tiers[3])}  T4={len(tiers[4])}  "
      f"(unscored={len(tiers[0])})")
print(f"report  -> {REPORT}")
print(f"raw     -> {RAW}")
