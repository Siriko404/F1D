"""Axis-B v3 — exact title.search resolution for the 7 canonical anchors
that OpenAlex `search=` ranking buried in v2 (Gulen-Ion, BBD, Jens,
Bonaime-Gulen-Ion, Nguyen-Phan, Pastor-Veronesi, Bates-Kahle-Stulz).

Root-cause-aligned tool: `filter=title.search:"<exact known title>"` is
high-precision for KNOWN titles (titles are facts from the cited lineage,
not guessed DOIs). Same surname/title guard; harvest forward cites; merge
into v2 corpus (all_scored_v2.json); re-tier; final report. Read-only API.
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

ROOT = Path(__file__).resolve().parent
V2RAW = ROOT / "openalex_trump_cash_2026-05-18_050911_B2"
TS = datetime.now().strftime("%Y-%m-%d_%H%M%S")
RAW = ROOT / f"openalex_trump_cash_{TS}_B3"
RAW.mkdir(parents=True, exist_ok=True)
REPORT = ROOT / f"openalex_trump_cash_review_{TS}_FINAL.md"

# (exact title phrase, guard groups)
ANCHORS = [
    ("Policy Uncertainty and Corporate Investment",
     [("gulen", "ion"), ("policy uncertainty",)]),
    ("Measuring Economic Policy Uncertainty",
     [("baker",), ("bloom",), ("davis",)]),
    ("Political uncertainty and investment causal evidence from U.S. "
     "gubernatorial elections",
     [("jens",), ("gubernatorial",)]),
    ("Does policy uncertainty affect mergers and acquisitions",
     [("bonaime", "gulen", "ion"), ("merger", "acquisition")]),
    ("Policy Uncertainty and Mergers and Acquisitions",
     [("nguyen", "phan"), ("merger", "acquisition")]),
    ("Political uncertainty and risk premia",
     [("pastor", "pástor", "veronesi"), ("political uncertainty",
                                          "risk premia")]),
    ("Why Do U.S. Firms Hold So Much More Cash than They Used To",
     [("bates", "stulz", "kahle"), ("cash",)]),
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


def resolve(title, guards):
    f = urllib.parse.quote(f'title.search:{title}')
    url = (f"{BASE}?filter={f}&per-page=15&select={SELECT}"
           f"&sort=cited_by_count:desc&mailto={MAILTO}")
    res = get(url).get("results", []) or []
    for w in res:
        hay = ((w.get("display_name") or "") + " " +
               auth(w.get("authorships", []))).lower()
        if all(any(t in hay for t in g) for g in guards):
            return w, res
    return None, res


def harvest(wid, cap=800):
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
           deinv(w.get("abstract_inverted_index"))).lower()
    return {
        "wid": wid, "year": w.get("publication_year"),
        "cites": w.get("cited_by_count", 0),
        "title": w.get("display_name"),
        "authors": auth(w.get("authorships", [])),
        "venue": ven(w.get("primary_location")),
        "doi": w.get("doi"),
        "axes": {
            "event": bool(EVENT_RE.search(txt)),
            "trump": bool(re.search(r"\btrump\b|2016 (presidential )?"
                                    r"election|election surprise", txt)),
            "outcome": bool(OUTCOME_RE.search(txt)),
            "mech": bool(MECH_RE.search(txt)),
            "method": bool(METHOD_RE.search(txt))},
        "abstract": deinv(w.get("abstract_inverted_index"), 120),
    }


def tier(r):
    a = r["axes"]
    if a["trump"] and a["outcome"] and (a["method"] or a["mech"]):
        return 1
    if (a["trump"] and a["outcome"]) or \
       (a["event"] and a["outcome"] and a["method"] and a["mech"]):
        return 2
    if a["event"] and a["outcome"] and (a["method"] or a["mech"]):
        return 3
    if a["event"] and a["outcome"]:
        return 4
    return 0


seen = {}
for r in json.loads((V2RAW / "all_scored_v2.json").read_text("utf-8")):
    r["src"] = set(r.get("src", []))
    seen[r["wid"]] = r
print(f"loaded v2 corpus: {len(seen)} works")


def add(w, src):
    wid = w["id"].split("/")[-1]
    if wid in seen:
        seen[wid]["src"] = set(seen[wid]["src"]) | {src}
        return
    r = record(w)
    r["src"] = {src}
    seen[wid] = r


print("\nAXIS B v3 — exact title.search resolution + harvest")
log = []
for title, guards in ANCHORS:
    w, pool = resolve(title, guards)
    if not w:
        tops = "; ".join(f"{(x.get('display_name') or '')[:42]}"
                         f"[{x.get('cited_by_count',0)}c]"
                         for x in pool[:3])
        print(f"  UNRESOLVED «{title[:42]}» top3: {tops}")
        log.append({"title_q": title, "resolved": None})
        time.sleep(0.3)
        continue
    wid = w["id"].split("/")[-1]
    tt = w.get("display_name") or ""
    cc = w.get("cited_by_count", 0)
    citing = harvest(wid, cap=800)
    kept = 0
    for c in citing:
        tl = ((c.get("display_name") or "") + " " +
              deinv(c.get("abstract_inverted_index"))).lower()
        if OUTCOME_RE.search(tl) or MECH_RE.search(tl):
            add(c, f"B3:{wid}")
            kept += 1
    print(f"  [{wid}] {tt[:54]!r} cited={cc} scanned={len(citing)} "
          f"kept={kept}")
    log.append({"title_q": title, "wid": wid, "resolved_title": tt,
                "anchor_cites": cc, "scanned": len(citing), "kept": kept})
    time.sleep(0.3)
(RAW / "anchor_log_v3.json").write_text(json.dumps(log, indent=1), "utf-8")

for r in seen.values():
    r["tier"] = tier(r)
    r["src"] = sorted(r["src"]) if isinstance(r["src"], (set, list)) else []
(RAW / "all_scored_final.json").write_text(
    json.dumps(list(seen.values()), indent=1), "utf-8")

tiers = {1: [], 2: [], 3: [], 4: [], 0: []}
for r in seen.values():
    tiers[r["tier"]].append(r)
for t in tiers:
    tiers[t].sort(key=lambda x: (-(x["year"] or 0), -(x["cites"] or 0)))

NAME = {
    1: "TIER 1 — EXACT (Trump 2016 + cash + DiD/quasi-exp [+ precaution])",
    2: "TIER 2 — STRONG ADJACENT (Trump 2016 + cash; or election-unc + "
       "cash + method + mechanism)",
    3: "TIER 3 — METHOD PRECEDENT (other election / policy-unc shock + "
       "cash + DiD/quasi-exp)",
    4: "TIER 4 — THEORETICAL ANTECEDENT (political/policy uncertainty + "
       "cash, any method)",
}
res_n = sum(1 for x in log if x.get("wid"))
L = [
    "# OpenAlex systematic review — FINAL — Trump 2016 DiD x cash x "
    "precautionary",
    "",
    f"Generated {datetime.now():%Y-%m-%d %H:%M:%S} | works screened "
    f"{len(seen)} | v3 anchors resolved {res_n}/{len(ANCHORS)} (exact "
    "title.search) | + v2 5/12 (Hassan PRISK, Acharya-Almeida-Campello, "
    "EPU-cash, M&A-policy-unc) | + Axis-A 115 event×outcome TA-searches",
    "",
    "Two independent axes (A: title+abstract event×outcome incl. all "
    "Trump phrasings; B: forward-citations of the policy-uncertainty / "
    "political-risk / precautionary-cash lineage). Tiering recall-biased "
    "(method/precaution often body-only) — abstracts must be read before "
    "citing. NO hand transcription; regex-scored records.",
    "",
    f"| Tier | N |\n|--|--|\n| 1 exact | {len(tiers[1])} |\n"
    f"| 2 strong adjacent | {len(tiers[2])} |\n"
    f"| 3 method precedent | {len(tiers[3])} |\n"
    f"| 4 theoretical antecedent | {len(tiers[4])} |",
    "",
    "## Axis-B v3 resolution audit",
    "",
]
for x in log:
    if x.get("wid"):
        L.append(f"- OK `{x['wid']}` [{x['anchor_cites']}c] "
                 f"{x['resolved_title'][:80]} — scanned {x['scanned']} "
                 f"kept {x['kept']}")
    else:
        L.append(f"- UNRESOLVED «{x['title_q'][:60]}»")
L.append("")
for t in (1, 2, 3, 4):
    L.append(f"## {NAME[t]}  ({len(tiers[t])})\n")
    if not tiers[t]:
        L.append("_none_\n")
        continue
    show = tiers[t] if t in (1, 2) else tiers[t][:45]
    for r in show:
        ax = r["axes"]
        fl = "".join(k[0].upper() for k in
                     ("trump", "outcome", "mech", "method") if ax.get(k))
        L.append(
            f"- **({r['year']})** [{r['cites']}c] {r['title']}  \n"
            f"  {r['authors']} · _{r['venue']}_ · `{r['wid']}` · "
            f"{r['doi'] or ''}  \n  axes=[{fl}]  src={list(r['src'])[:2]}"
            f"  \n  abs: {r['abstract'][:340]}")
    if t not in (1, 2) and len(tiers[t]) > 45:
        L.append(f"\n_(+{len(tiers[t]) - 45} more in "
                 f"{RAW.name}/all_scored_final.json)_")
    L.append("")
REPORT.write_text("\n".join(L), "utf-8")
print(f"\nFINAL TIERS  T1={len(tiers[1])} T2={len(tiers[2])} "
      f"T3={len(tiers[3])} T4={len(tiers[4])}")
print(f"v3 resolved {res_n}/{len(ANCHORS)}")
print(f"report -> {REPORT}")
