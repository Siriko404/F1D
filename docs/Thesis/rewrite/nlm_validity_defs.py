#!/usr/bin/env python3
"""Extract the EXACT definitions of the 2.5 validity-yardstick variables from NLM,
so a yardstick test is only claimed valid once the yardstick itself is established
from its authors' own words. Reuses the durable nlm_common engine.

METHOD = NLM_QUERY_GUIDE.md §3a (content-discovery). The yardstick source files sit
under OPAQUE publisher-code filenames; we do NOT touch the filenames. For each paper we
run an UNSCOPED ask (NO -s, with --new) that NAMES the paper by title+author+year (from
our bib) and asks its definition question. NLM searches ALL sources; references[].source_id
= the source that actually CONTAINS the paper = the id, discovered by content, zero
filename bias. The same query also captures the definition spans. (`clear` before each ask =
best-effort isolation; this CLI build has NO --new flag.)

Evidence -> tmp/nlm_validity_definitions.json (planning; folds into the 2.5 ledger later).
Resumable; one commit per query; ONLY references[].cited_text are admissible verbatim.

  python docs/Thesis/rewrite/nlm_validity_defs.py            # discover + capture (unscoped, by content)
  python docs/Thesis/rewrite/nlm_validity_defs.py --show
"""
import argparse
import json

import nlm_common as nc

OUT = nc.REPO / "tmp" / "nlm_validity_definitions.json"

# Paper labels named IN the query (TITLE + AUTHOR + YEAR, verbatim from thesis_draft.tex bib).
LABELS = {
    "hoberg2016": 'the paper "Text-based network industries and endogenous product '
                  'differentiation" by Hoberg and Phillips (2016, Journal of Political Economy)',
    "hassan2020": 'the paper "Firm-level political risk: Measurement and effects" by Hassan, '
                  'Hollander, van Lent, and Tahoun (2020, The Quarterly Journal of Economics)',
    "baker2016":  'the paper "Measuring economic policy uncertainty" by Baker, Bloom, and '
                  'Davis (2016, The Quarterly Journal of Economics)',
    "davis2016":  'the paper "An index of global economic policy uncertainty" by Davis '
                  '(2016, NBER Working Paper 22740)',
}

# Approved content queries (atomic, non-leading) -> the property each pins.
QUERIES = {
    "hoberg2016": [
        ("Q1_def",
         "How is the text-based total product-market similarity measure (the sum of pairwise "
         "product-market similarities between a firm and other firms, from the Text-Based "
         "Network Industry Classification) defined and constructed from firms' product "
         "descriptions, and what does a higher value indicate about a firm's competitive "
         "environment?"),
        ("Q2_frequency",
         "At what unit of observation and how often is each firm's total-similarity value "
         "computed, and does that value change from year to year for a given firm or remain "
         "fixed over time?"),
    ],
    "hassan2020": [
        ("Q1_def",
         "How is the firm-level political risk measure (PRisk) defined and constructed, what "
         "does it quantify about a firm, and at what unit and frequency is it computed?"),
    ],
    "baker2016": [
        ("Q1_def",
         "How is the Economic Policy Uncertainty index defined and constructed, what does it "
         "measure, and at what frequency and geographic level is it reported?"),
    ],
    "davis2016": [
        ("Q1_def",
         "How is the Global Economic Policy Uncertainty index defined and constructed, and "
         "what does it measure?"),
    ],
}

# Scoped requeries for a CLEAN cited_text span where the unscoped pass left only answer-prose.
# Tokens here are CONTENT-CONFIRMED (the unscoped/--davis pass proved which file each paper is),
# so resolving by title-substring is now safe (identity already established by content).
# (key, confirmed title-token, tag, question phrased to pull verbatim sentences)
REQUERIES = [
    ("hoberg2016", "688176", "Q3_def_direction",
     "Quote verbatim, exactly as printed, the sentence(s) where the paper defines its total "
     "similarity measure (a firm's total product-market similarity) and states what a HIGHER "
     "value of it indicates about the firm's product market or competition. Reproduce each "
     "sentence exactly."),
    ("davis2016", "w22740", "Q2_def_clean",
     "Quote verbatim, exactly as printed, the sentence(s) where the paper defines how the Global "
     "Economic Policy Uncertainty (GEPU) index is constructed (for example as a GDP-weighted "
     "average of national EPU indices). Reproduce each sentence exactly."),
]


def _load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding="utf-8"))
    return {"_purpose": "2.5 validity-yardstick variable definitions (NLM content-discovery, guide §3a)",
            "captures": {}}


def _save(d):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def _commit(msg):
    nc.run(["git", "add", str(nc.HERE), str(OUT)], 60)
    nc.run(["git", "commit", "-m", msg], 60)


def _id_titles():
    """source_id -> title, for REPORTING which source NLM discovered (not for selecting one)."""
    return {s["id"]: (s.get("title") or "") for s in nc._sources()}


def ask_discover(label, question):
    """UNSCOPED (no -s) ask that NAMES the paper; NLM searches all sources and references
    reveal which source_id holds it. `clear` first = best-effort isolation (this build has
    NO --new flag -- it errors). Retries once on timeout/error."""
    q = f"{nc.PREFIX}{label}: {question}{nc.LOCATOR}"
    for _ in (1, 2):
        try:
            nc.run([nc.EXE, "clear"], 60)
        except Exception:
            pass
        out = nc.run([nc.EXE, "ask", "-n", nc.NOTEBOOK, "--json", q], 420).stdout or ""
        i = out.find("{")
        if i >= 0:
            j = json.loads(out[i:])
            if not j.get("error") and (j.get("answer") or j.get("references")):
                return q, j
    return q, {"answer": "", "references": []}


def run_queries():
    titles = _id_titles()
    data = _load()
    for key, qs in QUERIES.items():
        label = LABELS[key]
        data["captures"].setdefault(key, {})
        for qid, question in qs:
            if data["captures"][key].get(qid):          # resumable: any record present -> skip
                print(f"{key}/{qid}: already captured -- skip (delete it to redo)."); continue
            print(f"{key}/{qid}: UNSCOPED discover+capture, naming {key} ...", flush=True)
            query, j = ask_discover(label, question)
            answer = j.get("answer", "")
            refs = j.get("references", [])
            quotes = [{"n": x.get("citation_number"), "source_id": x.get("source_id"),
                       "cited_text": x.get("cited_text"), "start_char": x.get("start_char"),
                       "end_char": x.get("end_char"), "chunk_id": x.get("chunk_id")}
                      for x in refs if x.get("cited_text")]
            disc = sorted({x.get("source_id") for x in refs if x.get("source_id")})
            discovered = [{"source_id": sid, "title": titles.get(sid, "?")} for sid in disc]
            located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(),
                        "section": m.group(3).strip()} for m in nc.LOC.finditer(answer)]
            data["captures"][key][qid] = {"query": query, "answer": answer, "quotes": quotes,
                                          "located": located, "discovered_sources": discovered}
            _save(data)
            _commit(f"verify(2.5/def): {key} {qid} -> {len(discovered)} src discovered, "
                    f"{len(quotes)} spans")
            print(f"  DISCOVERED source(s): {[d['title'][:45] for d in discovered] or 'NONE'}")
            print(f"  {len(quotes)} verbatim spans, {len(located)} located; committed")
    print("\nDONE. Review --show: confirm each paper resolved to ONE coherent source; "
          "any 'NONE' / multi-source = absent or ambiguous -> escalate.")


def davis_followup():
    """Davis GEPU returned no source in the unscoped pass. There IS a 'w22740' file in the
    notebook; CONFIRM by CONTENT whether it is Davis (2016) -- never assume from the name.
    One scoped call: ask the source to state its own identity AND define GEPU. If it self-
    reports Davis + returns GEPU spans -> uploaded, gap closed. Else -> not uploaded."""
    hits = [s for s in nc._sources() if "w22740" in (s.get("title") or "").lower()]
    if not hits:
        print("NO 'w22740' file in the notebook. Davis (2016) NBER WP 22740 not uploaded under that name.")
        return
    sid, title = hits[0]["id"], hits[0]["title"]
    print(f"candidate file = {title} ({sid[:8]}); confirming identity + GEPU def by content ...", flush=True)
    q = ("First state ONLY this source's exact title, authors, series, and year. Then explain how "
         "the Global Economic Policy Uncertainty (GEPU) index is defined and constructed and what "
         "it measures.")
    query, j = nc.ask(sid, "this source", q)
    answer = j.get("answer", "")
    quotes = [{"n": x.get("citation_number"), "source_id": x.get("source_id"),
               "cited_text": x.get("cited_text"), "start_char": x.get("start_char"),
               "end_char": x.get("end_char"), "chunk_id": x.get("chunk_id")}
              for x in j.get("references", []) if x.get("cited_text")]
    located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(),
                "section": m.group(3).strip()} for m in nc.LOC.finditer(answer)]
    data = _load()
    data["captures"].setdefault("davis2016", {})["scoped_w22740"] = {
        "candidate_file": title, "source_id": sid, "query": query,
        "answer": answer, "quotes": quotes, "located": located}
    _save(data)
    _commit(f"verify(2.5/def): davis scoped to w22740 candidate ({len(quotes)} spans)")
    print(f"\nIDENTITY + DEF ANSWER:\n{answer[:700]}")
    print(f"\n{len(quotes)} verbatim spans:")
    for x in quotes:
        ct = (x.get("cited_text") or "").strip()
        if ct:
            print(f"  [n{x.get('n')}] {ct[:170]}")


def requery():
    """One scoped call per REQUERIES item -> a clean verbatim span. Appends under a new tag;
    never overwrites the unscoped capture. Resumable."""
    data = _load()
    for key, token, tag, question in REQUERIES:
        hits = [s for s in nc._sources() if token.lower() in (s.get("title") or "").lower()]
        if len(hits) != 1:
            print(f"{key}: {len(hits)} matches for '{token}' -- skip"); continue
        sid, title = hits[0]["id"], hits[0]["title"]
        data["captures"].setdefault(key, {})
        if data["captures"][key].get(tag):
            print(f"{key}/{tag}: already captured -- skip"); continue
        print(f"{key}/{tag}: scoped requery -> {title}", flush=True)
        query, j = nc.ask(sid, LABELS[key], question)         # scoped -s sid + names paper + LOCATOR
        answer = j.get("answer", "")
        quotes = [{"n": x.get("citation_number"), "source_id": x.get("source_id"),
                   "cited_text": x.get("cited_text"), "start_char": x.get("start_char"),
                   "end_char": x.get("end_char"), "chunk_id": x.get("chunk_id")}
                  for x in j.get("references", []) if x.get("cited_text")]
        located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(),
                    "section": m.group(3).strip()} for m in nc.LOC.finditer(answer)]
        data["captures"][key][tag] = {"source": {"id": sid, "title": title}, "query": query,
                                      "answer": answer, "quotes": quotes, "located": located}
        _save(data)
        _commit(f"verify(2.5/def): {key} {tag} scoped requery ({len(quotes)} spans)")
        print(f"  {len(quotes)} verbatim spans:")
        for x in quotes:
            ct = (x.get("cited_text") or "").strip()
            if ct:
                print(f"    [n{x.get('n')}] {ct[:170]}")


def show():
    data = _load()
    for key, caps in data.get("captures", {}).items():
        for qid, cap in caps.items():
            print(f"\n===== {key}/{qid} =====")
            ds = cap.get("discovered_sources", [])
            print(f"DISCOVERED: {[(d['source_id'][:8], d['title'][:50]) for d in ds] or 'NONE'}")
            print(f"ANSWER (NON-evidence): {(cap.get('answer') or '')[:500]}")
            print("VERBATIM SPANS (admissible cited_text):")
            for q in cap.get("quotes", []):
                ct = (q.get("cited_text") or "").strip()
                if ct:
                    print(f"  [n{q.get('n')} src={(q.get('source_id') or '')[:8]}] {ct}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--davis", action="store_true")
    ap.add_argument("--requery", action="store_true")
    a = ap.parse_args()
    if a.show:
        show()
    elif a.requery:
        if not nc.EXE:
            raise SystemExit("notebooklm CLI not found on PATH; run `notebooklm login` first.")
        requery()
    elif a.davis:
        if not nc.EXE:
            raise SystemExit("notebooklm CLI not found on PATH; run `notebooklm login` first.")
        davis_followup()
    else:
        if not nc.EXE:
            raise SystemExit("notebooklm CLI not found on PATH; run `notebooklm login` first.")
        run_queries()
