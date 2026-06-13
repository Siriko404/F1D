#!/usr/bin/env python3
"""Extract ALL equations from DWZ ("Straight Talkers", Dzielinski/Wagner/Zeckhauser)
via NLM, with exact variables -- so the 2.3/2.4 equation gate misses nothing.

Reuses the durable nlm_common engine (resolver + isolated single-source ask + the
page/section LOCATOR). We are still in PLANNING (the 2.3 ledger is not built yet),
so evidence is written to a durable tmp file: tmp/nlm_dwz_equations.json. It folds
into the 2.3 ledger when that ledger is created. Per NLM_QUERY_GUIDE.md:
  - ONE durable committed script; NO ad-hoc gathering; NLM is the SOLE authority.
  - atomic, self-contained, non-leading queries; resolve source id at runtime.
  - resumable: a query already holding cited_text quotes is skipped.
  - ONLY references[].cited_text are admissible verbatim; the answer is context.
  - equations OCR poorly -> we capture answer + spans + located(page/section),
    then a substring audit reports verbatim-confidence honestly.

    python docs/Thesis/rewrite/nlm_dwz_eqs.py            # query + capture + commit
    python docs/Thesis/rewrite/nlm_dwz_eqs.py --audit    # substring audit only
    python docs/Thesis/rewrite/nlm_dwz_eqs.py --show     # print captured evidence
"""
import json
import sys

import nlm_common as nc

OUT = nc.REPO / "tmp" / "nlm_dwz_equations.json"
PAPER_KEY = "dwz2021"
LABEL = 'the paper "Straight Talkers" by Dzielinski, Wagner, and Zeckhauser'

# id -> atomic, non-leading question (LOCATOR is appended by nc.ask)
QUERIES = [
    ("Q1_enumerate",
     "List every numbered equation that appears anywhere in this paper. For each one, "
     "reproduce the equation exactly as printed and then define every variable, "
     "coefficient, and subscript it contains."),
    ("Q2_decomposition",
     "What regression equation is used to separate a CEO's answer-language uncertainty "
     "into a persistent manager-specific component and a time-varying residual? Reproduce "
     "that equation exactly, list all of its right-hand-side variables, and state precisely "
     "how the manager-specific component and the residual component are each defined from it."),
    ("Q3_eq4_controls",
     "In the CEO-clarity estimation -- Equation (4), which regresses CEO answer-language "
     "uncertainty on a CEO fixed effect plus control vectors -- the controls are written as "
     "two groups: speech / linguistic-marker controls and firm-characteristic controls. "
     "Enumerate exactly which individual variables make up each group on the right-hand side "
     "of that regression, listing every control variable by name as the paper defines it."),
]


def _load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding="utf-8"))
    return {"paper": LABEL, "source_key": PAPER_KEY, "captures": {}}


def _save(d):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def _commit(msg):
    nc.run(["git", "add", str(nc.HERE), str(OUT)], 60)
    nc.run(["git", "commit", "-m", msg], 60)


def capture():
    sid, title = nc.require([PAPER_KEY])[PAPER_KEY]   # fail-closed before any quota spend
    data = _load()
    data["source"] = {"id": sid, "title": title}
    for qid, question in QUERIES:
        if data["captures"].get(qid, {}).get("quotes"):
            print(f"{qid}: already captured -- skipped.")
            continue
        print(f"{qid}: querying NLM -> {title[:55]}", flush=True)
        query, j = nc.ask(sid, LABEL, question)
        answer = j.get("answer", "")
        quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
                   "start_char": x.get("start_char"), "end_char": x.get("end_char"),
                   "chunk_id": x.get("chunk_id")}
                  for x in j.get("references", []) if x.get("cited_text")]
        located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(),
                    "section": m.group(3).strip()} for m in nc.LOC.finditer(answer)]
        data["captures"][qid] = {"query": query, "answer": answer,
                                 "quotes": quotes, "located": located}
        _save(data)
        _commit(f"verify(2.3/eq): DWZ {qid} NLM answer -> tmp evidence "
                f"({len(quotes)} quotes, {len(located)} located)")
        print(f"  wrote {len(quotes)} quotes, {len(located)} located; committed")


def audit():
    data = _load()
    for qid, cap in data.get("captures", {}).items():
        spans = [q.get("cited_text") or "" for q in cap.get("quotes", [])]
        loc = cap.get("located", [])
        hits = sum(any(L.get("quote", "") in s for s in spans) for L in loc)
        print(f"\n{qid}: {len(spans)} verbatim spans, {len(loc)} located; "
              f"{hits}/{len(loc)} located lie inside a verbatim span")
        for q in spans:
            print(f"  SPAN: {q[:160]}")


def show():
    data = _load()
    for qid, cap in data.get("captures", {}).items():
        print(f"\n===== {qid} =====")
        print(f"ANSWER (NON-evidence):\n{(cap.get('answer') or '')[:1600]}")
        print("VERBATIM SPANS (admissible cited_text):")
        for q in cap.get("quotes", []):
            ct = (q.get("cited_text") or "").strip()
            if ct:
                print(f"  [n{q.get('n')}] {ct}")


if __name__ == "__main__":
    if "--audit" in sys.argv:
        audit()
    elif "--show" in sys.argv:
        show()
    else:
        capture()
