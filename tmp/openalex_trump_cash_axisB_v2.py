"""Axis-B repair (v2) for the Trump/cash/precautionary review.

Root cause of v1 Axis-B failure: anchor resolution used
`filter=title_and_abstract.search:<raw multiword>` -> OpenAlex ANDs every
token, so rare surname combos returned empty or a junk top hit
(Gulen-Ion -> 0-cite paper; "Baker Bloom Davis" -> Pastor-Veronesi).

Fix: resolve anchors via the general `?search=` ranked endpoint, then a
per-anchor GUARD (surname/title tokens that MUST appear in the resolved
display_name+authors) before harvesting forward citations. Mis-resolved or
unresolved anchors are logged, NOT harvested.

Reuse: loads v1 all_scored.json (194 works incl. Axis A + the 2 anchors
that did resolve), merges new screened citations, re-tiers, rewrites report.
Read-only against OpenAlex; writes only into tmp/.
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
V1RAW = ROOT / "openalex_trump_cash_2026-05-18_045753"
TS = datetime.now().strftime("%Y-%m-%d_%H%M%S")
RAW = ROOT / f"openalex_trump_cash_{TS}_B2"
RAW.mkdir(parents=True, exist_ok=True)
REPORT = ROOT / f"openalex_trump_cash_review_{TS}_v2.md"

# anchor: (search query, guard-token-groups). Resolve = top ranked hit whose
# (title+authors).lower() contains >=1 token from EACH group.
ANCHORS = [
    ("Policy Uncertainty and Corporate Investment Gulen Ion",
     [("gulen", "ion"), ("policy uncertainty",),
      ("investment", "corporate")]),
    ("Measuring Economic Policy Uncertainty Baker Bloom Davis",
     [("baker",), ("bloom",), ("davis",)]),
    ("Political uncertainty and investment causal evidence US "
     "gubernatorial elections Jens",
     [("jens",), ("gubernatorial", "political uncertainty"),
      ("investment",)]),
    ("Does policy uncertainty affect mergers and acquisitions "
     "Bonaime Gulen Ion",
     [("bonaime",), ("merger", "acquisition")]),
    ("Policy uncertainty and mergers and acquisitions Nguyen Phan",
     [("nguyen", "phan"), ("merger", "acquisition", "policy uncertainty")]),
    ("Firm-Level Political Risk Measurement and Effects Hassan "
     "Hollander van Lent Tahoun",
     [("hassan", "tahoun", "hollander"), ("political risk",)]),
    ("Political uncertainty and risk premia Pastor Veronesi",
     [("pastor", "pástor", "veronesi"),
      ("political uncertainty", "risk premia")]),
    ("Aggregate risk and the choice between cash and lines of credit "
     "Acharya Almeida Campello",
     [("acharya", "almeida", "campello"),
      ("cash", "lines of credit", "credit")]),
    ("Why do US firms hold so much more cash than they used to "
     "Bates Kahle Stulz",
     [("bates", "stulz", "kahle"), ("cash",)]),
    ("Trump election CEO political uncertainty difference-in-differences "
     "Hu Kang Li Lin",
     [("trump", "2016 election"), ("ceo", "minority", "uncertainty")]),
    ("Economic policy uncertainty and corporate cash holdings Demir Ersan",
     [("policy uncertainty",), ("cash",)]),
    ("Policy uncertainty and corporate cash holdings Duong Nguyen Rhee "
     "Sharma",
     [("policy uncertainty", "cash"), ("cash", "holdings")]),
]
# anchors already correctly harvested in v1 -> skip re-harvest (merge later)
V1_DONE = {"W3037153229"}  # M&A-policy-uncertainty (legit). W3121806304 was
# Pastor-Veronesi mis-tagged as BBD; its 50 kept cites are still valid
# policy-unc->cash forward cites, keep them (already in all_scored).

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


def resolve(query, guards):
    """General ranked search; first hit passing ALL guard groups."""
    q = urllib.parse.quote(query)
    url = (f"{BASE}?search={q}&per-page=15&select={SELECT}"
           f"&sort=relevance_score:desc&mailto={MAILTO}")
    res = get(url).get("results", []) or []
    for w in res:
        hay = ((w.get("display_name") or "") + " " +
               auth(w.get("authorships", []))).lower()
        if all(any(tok in hay for tok in grp) for grp in guards):
            return w, res
    return None, res


def harvest_cites(wid, cap=800):
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
    ev = bool(EVENT_RE.search(txt))
    trump = bool(re.search(r"\btrump\b|2016 (presidential )?election|"
                           r"election surprise", txt))
    return {
        "wid": wid, "year": w.get("publication_year"),
        "cites": w.get("cited_by_count", 0),
        "title": w.get("display_name"),
        "authors": auth(w.get("authorships", [])),
        "venue": ven(w.get("primary_location")),
        "doi": w.get("doi"),
        "axes": {"event": ev, "trump": trump,
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


# ---- load v1 corpus ---------------------------------------------------------
seen = {}
v1 = json.loads((V1RAW / "all_scored.json").read_text(encoding="utf-8"))
for r in v1:
    r["src"] = set(r.get("src", []))
    seen[r["wid"]] = r
print(f"loaded v1 corpus: {len(seen)} works")


def add(w, src):
    wid = w["id"].split("/")[-1]
    if wid in seen:
        seen[wid]["src"] = set(seen[wid]["src"]) | {src}
        return
    r = record(w)
    r["src"] = {src}
    seen[wid] = r


# ---- Axis-B v2: resolve with guard, then harvest ---------------------------
print("\nAXIS B v2 — guarded anchor resolution + forward-cite harvest")
log = []
for query, guards in ANCHORS:
    w, pool = resolve(query, guards)
    if not w:
        tops = "; ".join(f"{x.get('display_name','')[:45]}"
                         f"[{x.get('cited_by_count',0)}c]"
                         for x in pool[:3])
        print(f"  UNRESOLVED  «{query[:46]}»  top3: {tops}")
        log.append({"query": query, "resolved": None,
                    "top3": [x.get("display_name") for x in pool[:3]]})
        time.sleep(0.3)
        continue
    wid = w["id"].split("/")[-1]
    title = w.get("display_name") or ""
    cites = w.get("cited_by_count", 0)
    if wid in V1_DONE:
        print(f"  [{wid}] {title[:52]!r} cited={cites}  (v1-done, skip)")
        log.append({"query": query, "wid": wid, "title": title,
                    "anchor_cites": cites, "note": "v1-done skip"})
        continue
    citing = harvest_cites(wid, cap=800)
    kept = 0
    for c in citing:
        tl = ((c.get("display_name") or "") + " " +
              deinv(c.get("abstract_inverted_index"))).lower()
        if OUTCOME_RE.search(tl) or MECH_RE.search(tl):
            add(c, f"B2:{wid}")
            kept += 1
    print(f"  [{wid}] {title[:52]!r} cited={cites} "
          f"scanned={len(citing)} kept={kept}")
    log.append({"query": query, "wid": wid, "title": title,
                "anchor_cites": cites, "citing_scanned": len(citing),
                "cash_screened_kept": kept})
    time.sleep(0.3)
(RAW / "anchor_log_v2.json").write_text(json.dumps(log, indent=1),
                                        encoding="utf-8")

# ---- re-tier + report -------------------------------------------------------
for r in seen.values():
    r["tier"] = tier(r)
    r["src"] = sorted(r["src"]) if isinstance(r["src"], (set, list)) else []
(RAW / "all_scored_v2.json").write_text(
    json.dumps(list(seen.values()), indent=1), encoding="utf-8")

tiers = {1: [], 2: [], 3: [], 4: [], 0: []}
for r in seen.values():
    tiers[r["tier"]].append(r)
for t in tiers:
    tiers[t].sort(key=lambda x: (-(x["year"] or 0), -(x["cites"] or 0)))

TIER_NAME = {
    1: "TIER 1 — EXACT (Trump 2016 + cash + DiD/quasi-exp [+ precautionary])",
    2: "TIER 2 — STRONG ADJACENT (Trump 2016 + cash; or election-unc + "
       "cash + method + mechanism)",
    3: "TIER 3 — METHOD PRECEDENT (other election / policy-unc shock + "
       "cash + DiD/quasi-exp)",
    4: "TIER 4 — THEORETICAL ANTECEDENT (political/policy uncertainty + "
       "cash, any method)",
}
resolved_n = sum(1 for x in log if x.get("wid"))
lines = [
    "# OpenAlex systematic review v2 — Trump 2016 DiD x cash holdings x "
    "precautionary",
    "",
    f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}  |  unique works "
    f"screened: {len(seen)}  |  Axis-B anchors resolved (guarded): "
    f"{resolved_n}/{len(ANCHORS)}",
    "",
    "v2 fixes the v1 Axis-B anchor-resolution defect (raw AND-search -> "
    "junk/empty) via OpenAlex general `search=` + per-anchor surname/title "
    "guard. v1 Axis-A (194 works) reused unchanged. Tiering is recall-"
    "biased (method/precautionary often body-only) — read abstracts "
    "before citing.",
    "",
    "| Tier | N |",
    "|------|---|",
    f"| 1 exact | {len(tiers[1])} |",
    f"| 2 strong adjacent | {len(tiers[2])} |",
    f"| 3 method precedent | {len(tiers[3])} |",
    f"| 4 theoretical antecedent | {len(tiers[4])} |",
    "",
    "## Axis-B anchor resolution audit",
    "",
]
for x in log:
    if x.get("wid"):
        lines.append(
            f"- OK `{x['wid']}` [{x.get('anchor_cites','?')}c] "
            f"{x.get('title','')[:80]} — kept "
            f"{x.get('cash_screened_kept', x.get('note',''))}")
    else:
        lines.append(f"- UNRESOLVED «{x['query'][:60]}» "
                      f"top3={[ (t or '')[:40] for t in x.get('top3',[])]}")
lines.append("")
for t in (1, 2, 3, 4):
    lines.append(f"## {TIER_NAME[t]}  ({len(tiers[t])})")
    lines.append("")
    if not tiers[t]:
        lines.append("_none_\n")
        continue
    show = tiers[t] if t in (1, 2) else tiers[t][:45]
    for r in show:
        ax = r["axes"]
        flag = "".join(k[0].upper() for k in
                       ("trump", "outcome", "mech", "method") if ax.get(k))
        lines.append(
            f"- **({r['year']})** [{r['cites']}c] {r['title']}  \n"
            f"  {r['authors']} · _{r['venue']}_ · `{r['wid']}` · "
            f"{r['doi'] or ''}  \n"
            f"  axes=[{flag}]  src={list(r['src'])[:2]}  \n"
            f"  abs: {r['abstract'][:340]}")
    if t not in (1, 2) and len(tiers[t]) > 45:
        lines.append(f"\n_(+{len(tiers[t]) - 45} more in "
                      f"{RAW.name}/all_scored_v2.json)_")
    lines.append("")

REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"\nTIER COUNTS v2  T1={len(tiers[1])}  T2={len(tiers[2])}  "
      f"T3={len(tiers[3])}  T4={len(tiers[4])}")
print(f"anchors resolved: {resolved_n}/{len(ANCHORS)}")
print(f"report -> {REPORT}")
print(f"raw    -> {RAW}")
