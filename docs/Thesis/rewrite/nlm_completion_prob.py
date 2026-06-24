#!/usr/bin/env python3
"""Confirm, via NLM, which uploaded paper best supports a DEAL-COMPLETION-PROBABILITY
model whose predictors overlap our SDC fields (payment, target public/private,
attitude, relative size) -- to anchor the materiality = prob x magnitude test.

Three candidates uploaded by the user:
  baker_savasoglu2002  Limited Arbitrage in M&A (JFE 2002)
  mitchell_pulvino2001 Characteristics of Risk and Return in Risk Arbitrage (JF 2001)
  officer2003          Termination Fees in M&A (JFE 2003)

Reuses the durable nlm_common engine (resolver + scoped ask + LOCATOR). We are in
PLANNING (no target ledger yet), so evidence -> tmp/nlm_completion_prob.json, one
git commit per query. Per NLM_QUERY_GUIDE.md: ONE durable script; NO ad-hoc gather;
atomic, self-contained, non-leading queries; identity-confirm opaque filenames (§4)
BEFORE content quota; ONLY references[].cited_text admissible verbatim.

  python docs/Thesis/rewrite/nlm_completion_prob.py --list      # print notebook sources (pick tokens)
  python docs/Thesis/rewrite/nlm_completion_prob.py --identity  # §4 self-identity each source
  python docs/Thesis/rewrite/nlm_completion_prob.py             # capture content + commit (resumable)
  python docs/Thesis/rewrite/nlm_completion_prob.py --audit     # substring verbatim audit
  python docs/Thesis/rewrite/nlm_completion_prob.py --show      # print evidence record
"""
import json
import sys

import nlm_common as nc

OUT = nc.REPO / "tmp" / "nlm_completion_prob.json"

# paper_key -> (query label with title/author/year, atomic non-leading question)
PAPERS = {
    "baker_savasoglu2002": (
        '"Limited Arbitrage in Mergers and Acquisitions" by Malcolm Baker and '
        'Serkan Savasoglu (2002, Journal of Financial Economics)',
        "Does the paper estimate or model the probability that an announced merger "
        "or acquisition is successfully completed? If it does, state the exact model "
        "and list every explanatory variable that enters it -- in particular whether "
        "payment method (cash versus stock), target attitude or hostility, target "
        "public versus private status, and relative deal size are among the predictors, "
        "and report the estimated sign of each."),
    "mitchell_pulvino2001": (
        '"Characteristics of Risk and Return in Risk Arbitrage" by Mark Mitchell and '
        'Todd Pulvino (2001, Journal of Finance)',
        "Does the paper estimate the probability that an announced deal is completed "
        "versus terminated as a function of deal characteristics? If so, list the "
        "characteristics or variables it uses to predict completion or failure."),
    "officer2003": (
        '"Termination Fees in Mergers and Acquisitions" by Micah Officer (2003, '
        'Journal of Financial Economics)',
        "Does the paper model the probability of deal completion as a function of deal "
        "characteristics? If so, list every variable in that completion model -- "
        "including whether termination fees, payment method, target attitude, target "
        "public/private status, and relative size enter -- and the sign of each."),
}

# tokens are case-insensitive substrings of the NOTEBOOK TITLE (filename). Fill from
# --list. A token only LOCATES the source; identity is confirmed by NLM (§4), never
# decoded from the filename.
TOKENS = {
    "baker_savasoglu2002": "s0304405x02000727",                                  # PII locates; identity via NLM (§4)
    "mitchell_pulvino2001": "mitchell - characteristics of risk and return in risk arbitrage",
    "officer2003": "s0304405x03001193",
}
for _k, _t in TOKENS.items():
    nc.SOURCES[_k] = {"token": _t}

KEYS = list(PAPERS.keys())


def _load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding="utf-8"))
    return {"purpose": "completion-probability anchor selection", "captures": {}}


def _save(d):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def _commit(msg):
    nc.run(["git", "add", str(nc.HERE), str(OUT)], 60)
    nc.run(["git", "commit", "-m", msg], 60)


def list_sources():
    for s in nc._sources():
        print(f"{s['id']}  |  {s.get('title')}")


def capture():
    resolved = nc.require(KEYS)                          # fail-closed before any quota
    data = _load()
    for key in KEYS:
        label, question = PAPERS[key]
        if data["captures"].get(key, {}).get("quotes"):
            print(f"{key}: already captured -- skipped.")
            continue
        sid, title = resolved[key]
        print(f"{key}: querying NLM -> {title[:55]}", flush=True)
        query, j = nc.ask(sid, label, question)
        answer = j.get("answer", "")
        quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
                   "start_char": x.get("start_char"), "end_char": x.get("end_char"),
                   "chunk_id": x.get("chunk_id")}
                  for x in j.get("references", []) if x.get("cited_text")]
        located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(),
                    "section": m.group(3).strip()} for m in nc.LOC.finditer(answer)]
        data["captures"][key] = {"source": {"id": sid, "title": title},
                                 "query": query, "answer": answer,
                                 "quotes": quotes, "located": located}
        _save(data)
        _commit(f"verify(materiality): {key} completion-prob NLM answer -> tmp "
                f"({len(quotes)} quotes, {len(located)} located)")
        print(f"  wrote {len(quotes)} quotes, {len(located)} located; committed")


def audit():
    data = _load()
    for key, cap in data.get("captures", {}).items():
        spans = [q.get("cited_text") or "" for q in cap.get("quotes", [])]
        loc = cap.get("located", [])
        hits = sum(any(L.get("quote", "") in s for s in spans) for L in loc)
        print(f"\n{key}: {len(spans)} verbatim spans, {len(loc)} located; "
              f"{hits}/{len(loc)} located inside a span")
        for s in spans:
            print(f"  SPAN: {s[:150]}")


def show():
    data = _load()
    for key, cap in data.get("captures", {}).items():
        print(f"\n===== {key} =====")
        print(f"ANSWER (NON-evidence):\n{(cap.get('answer') or '')[:1800]}")
        print("VERBATIM SPANS (admissible cited_text):")
        for q in cap.get("quotes", []):
            ct = (q.get("cited_text") or "").strip()
            if ct:
                print(f"  [n{q.get('n')}] {ct}")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_sources()
    elif "--identity" in sys.argv:
        nc.identity(KEYS)
    elif "--audit" in sys.argv:
        audit()
    elif "--show" in sys.argv:
        show()
    else:
        capture()
