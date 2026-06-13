#!/usr/bin/env python3
"""Shared NLM verification engine for the Section 2 rewrite.

ONE durable resolver + query + audit + finalize engine, imported by each thin
per-paragraph script (nlm_p3.py .. nlm_p6.py). See NLM_QUERY_GUIDE.md for rules.

Design goal (user, 2026-06-12): fetch each paper's source_id PROGRAMMATICALLY at
runtime from a declarative registry, then append THAT id into THAT paper's queries
(-s <id>) -- each paper its own id -- and FAIL CLOSED on any miss/ambiguity BEFORE
spending a single content-query (so quota is never burned on a wrong source).

Self-test (resolve every registered paper, print the map, exit non-zero on any
unresolved/ambiguous source -- no NLM content calls):
    python docs/Thesis/rewrite/nlm_common.py
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                                  # rewrite -> Thesis -> docs -> F1D
LEDGER = HERE / "section2.1_paragraph_ledger.json"
NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")
PREFIX = "Reading only this paper, "
LOCATOR = (" For each sentence you quote in support, report the exact page number "
           "printed in the paper and the section (heading or number) where it appears.")

# --- THE PAPER REGISTRY: paper_key -> matcher --------------------------------
# matcher: {"token": <case-insensitive substring of the notebook title>}
#          optionally + "dup": "newest"  -> if >1 title matches, take the newest
#                                            by created_at and WARN (duplicate upload)
#          or       {"id": <fixed verified source_id>}  -> opaque/duplicated source
#                                            no substring can safely select; resolver
#                                            only checks the id still exists.
# Resolve ALL needed ids in ONE `source list` call; refuse to guess: 0 matches or
# >1-without-a-dup-policy is a HARD EXIT naming the paper, before any content query.
SOURCES = {
    # -- Section 2.1 P3-P6 (this batch) --
    "hollander2010":       {"token": "hollander - does silence"},
    "bertrand_schoar2003": {"token": "118-4-1169", "dup": "newest"},
    "dwz2021":             {"token": "dzielinski et al. - straight talkers"},
    "harford1999":         {"token": "harford - corporate cash reserves"},
    "thewissen2024":       {"token": "4900453"},
    "ragozzino2024":       {"token": "s0024630123001000"},
    "keown1981":           {"token": "keown - merger announcements"},
    # -- P1/P2 (already SUPPORTED; kept for re-runs / fan-out) --
    "matsumoto2011":       {"id": "a1dacc9f-2bee-46ba-9261-496fd687c8e6"},
    "lm2011":              {"token": "loughran - when is a liability"},
}


def run(args, timeout):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def _sources():
    """Notebook source list; fail with a clear message on auth-expiry/error dict."""
    out = run([EXE, "source", "list", "-n", NOTEBOOK, "--json"], 120).stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit("ERROR: could not list notebook sources (auth? run `notebooklm login`).")
    obj = json.loads(out[i:])
    if obj.get("error"):
        sys.exit(f"ERROR: NLM source list failed -- {obj.get('message', 'unknown error')}")
    return obj.get("sources", [])


def resolve_all(keys):
    """Resolve each requested paper_key -> (id, title) from ONE source list.
    Returns (resolved: {key:(id,title)}, problems: [str]). Never guesses."""
    srcs = _sources()
    resolved, problems = {}, []
    for key in keys:
        m = SOURCES.get(key)
        if not m:
            problems.append(f"{key}: no matcher in SOURCES registry")
            continue
        if "id" in m:
            hit = [s for s in srcs if s["id"] == m["id"]]
            if not hit:
                problems.append(f"{key}: fixed id {m['id']} not present in notebook")
            else:
                resolved[key] = (hit[0]["id"], hit[0]["title"])
            continue
        tok = m["token"].lower()
        hits = [s for s in srcs if tok in (s.get("title") or "").lower()]
        if not hits:
            problems.append(f"{key}: no notebook title contains '{m['token']}'")
        elif len(hits) > 1:
            if m.get("dup") == "newest":
                newest = sorted(hits, key=lambda s: s.get("created_at", ""))[-1]
                resolved[key] = (newest["id"], newest["title"])
                print(f"  WARN {key}: {len(hits)} duplicate copies -> took newest "
                      f"({newest.get('created_at')})")
            else:
                problems.append(f"{key}: AMBIGUOUS ({len(hits)} matches, no dup policy): "
                                + "; ".join(h["title"] for h in hits))
        else:
            resolved[key] = (hits[0]["id"], hits[0]["title"])
    return resolved, problems


def require(keys):
    """Resolve + hard-gate. Prints the map; sys.exit on ANY problem (no quota spent)."""
    resolved, problems = resolve_all(keys)
    print("RESOLVED:")
    for k in keys:
        if k in resolved:
            sid, title = resolved[k]
            print(f"  OK   {k:22} {sid}  {title[:58]}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(f"  XX   {p}")
        sys.exit("Resolution failed -- fix the matcher(s) above before any NLM query.")
    return resolved


def ask(sid, paper, question):
    """One isolated, single-source NLM query (retries once on timeout/error)."""
    q = f"{PREFIX}{paper}: {question}{LOCATOR}"
    for _ in (1, 2):
        try:
            run([EXE, "clear"], 60)
        except Exception:
            pass
        out = run([EXE, "ask", "-n", NOTEBOOK, "-s", sid, "--json", q], 420).stdout or ""
        i = out.find("{")
        if i >= 0:
            j = json.loads(out[i:])
            if not j.get("error") and (j.get("answer") or j.get("references")):
                return q, j
    return q, {"answer": "", "references": []}


def commit(message):
    run(["git", "add", str(HERE)], 60)                 # stage only the rewrite dir
    run(["git", "commit", "-m", message], 60)


LOC = re.compile(r'"([^"]{20,}?)"[\s\S]{0,120}?\*\*Page:\*\*[ \t]*([^\n]+?)[ \t]*\n'
                 r'[\s\S]{0,60}?\*\*Section:\*\*[ \t]*([^\n]+)')


def page_section(answer):
    p = re.search(r"\*\*Page:\*\*[ \t]*([^\n*]+)", answer or "")
    s = re.search(r"\*\*Section:\*\*[ \t]*([^\n*]+)", answer or "")
    return (p.group(1).strip() if p else None), (s.group(1).strip() if s else None)


def _ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _save(ledger):
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")


def capture(para, props_spec):
    """props_spec: [(prop_id, paper_key, paper_label_in_query, question)].
    Resolve all needed ids (fail-closed) -> persist the map to ledger.resolved_sources
    -> per prop: ask scoped to its own id -> write verification -> commit. Resumable:
    skips any prop that already holds quotes."""
    keys = sorted({pk for (_, pk, _, _) in props_spec})
    resolved = require(keys)
    ledger = _ledger()
    ledger.setdefault("resolved_sources", {})
    for k in keys:
        sid, title = resolved[k]
        ledger["resolved_sources"][k] = {"status": "OK", "source_id": sid, "source_title": title}
    _save(ledger)
    commit(f"verify(2.1/{para}): resolve {len(keys)} source ids programmatically -> ledger")
    for pid, pkey, label, question in props_spec:
        ledger = _ledger()
        props = {p["prop_id"]: p for p in ledger["paragraphs"][para]["propositions"]}
        if props[pid].get("verification", {}).get("quotes"):
            print(f"{pid}: already captured -- skipped (delete its quotes to redo).")
            continue
        sid, title = resolved[pkey]
        print(f"{pid}: querying NLM -> {title[:55]}", flush=True)
        query, j = ask(sid, label, question)
        answer = j.get("answer", "")
        quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
                   "start_char": x.get("start_char"), "end_char": x.get("end_char"),
                   "chunk_id": x.get("chunk_id")}
                  for x in j.get("references", []) if x.get("cited_text")]
        located = [{"quote": mm.group(1).strip(), "page": mm.group(2).strip(),
                    "section": mm.group(3).strip()} for mm in LOC.finditer(answer)]
        props[pid]["verification"] = {
            "method": "NLM", "source": {"id": sid, "title": title}, "query": query,
            "answer": answer, "quotes": quotes, "located": located, "verdict": "PENDING"}
        _save(ledger)
        commit(f"verify(2.1/{para}): {pid} NLM answer -> ledger "
               f"({len(quotes)} quotes, {len(located)} located)")
        print(f"  wrote {len(quotes)} quotes, {len(located)} located; committed")


def identity(keys):
    """1 scoped call/paper: confirm the resolved id IS the intended paper
    (title/authors/series/year) BEFORE trusting it for content. Opaque/dup sources."""
    resolved = require(keys)
    for k in keys:
        sid, title = resolved[k]
        q = (f"{PREFIX}this source: state ONLY the exact title, the authors, the journal or "
             "working-paper series, and the year of this document. Do not infer beyond it.")
        print(f"{k}: identity-check -> {title[:48]}", flush=True)
        try:
            run([EXE, "clear"], 60)
        except Exception:
            pass
        out = run([EXE, "ask", "-n", NOTEBOOK, "-s", sid, "--json", q], 420).stdout or ""
        i = out.find("{")
        ans = (json.loads(out[i:]).get("answer", "") if i >= 0 else "")
        print(f"  -> {ans[:320]}\n")


def finalize(para, pins, verdicts):
    """pins: [(prop_id, paper_key, paper_label, decisive_verbatim_sentence)].
    verdicts: {prop_id: (verdict, note)}. Pin = 1 targeted page/section call each."""
    keys = sorted({pk for (_, pk, _, _) in pins})
    resolved = require(keys) if keys else {}
    ledger = _ledger()
    props = {p["prop_id"]: p for p in ledger["paragraphs"][para]["propositions"]}
    for prop_id, pkey, label, phrase in pins:
        existing = {sp.get("phrase") for sp in props[prop_id]["verification"].get("span_pins", [])}
        if phrase in existing:
            print(f"{prop_id}: pin already recorded -- skip (idempotent)")
            continue
        sid, _ = resolved[pkey]
        q = (f"{PREFIX}{label}: on what page (the page number printed in the paper) and in which "
             f'section does this exact sentence appear? Report **Page:** and **Section:**. '
             f'Sentence: "{phrase}"')
        print(f"{prop_id}: pinning decisive span ...", flush=True)
        try:
            run([EXE, "clear"], 60)
        except Exception:
            pass
        out = run([EXE, "ask", "-n", NOTEBOOK, "-s", sid, "--json", q], 420).stdout or ""
        i = out.find("{")
        j = json.loads(out[i:]) if i >= 0 else {"answer": ""}
        page, section = page_section(j.get("answer", ""))
        props[prop_id]["verification"].setdefault("span_pins", []).append(
            {"phrase": phrase, "page": page, "section": section,
             "query": q, "answer": j.get("answer", "")})
        print(f"  {prop_id} -> Page {page}, Section {section}")
    for pid, (verdict, note) in verdicts.items():
        props[pid]["verification"]["verdict"] = verdict
        props[pid]["verification"]["verdict_note"] = note
    _save(ledger)
    commit(f"verify(2.1/{para}): pin decisive spans; record verdicts")
    print("  verdicts recorded; committed")


def requery(para, prop_id, paper_key, paper_label, question):
    """Targeted RE-query of ONE source to attempt a CLEAN verbatim cited_text span for a
    specific claim, when the first capture chunked into fragments. Prints the answer + any
    new spans; appends them to the prop's verification['requery'] (never overwrites the
    original capture). One attempt -- if still no clean span, fix the verdict NOTE instead."""
    sid, title = require([paper_key])[paper_key]
    print(f"requery {prop_id} -> {title[:55]}", flush=True)
    q, j = ask(sid, paper_label, question)
    quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
               "start_char": x.get("start_char"), "end_char": x.get("end_char"),
               "chunk_id": x.get("chunk_id")}
              for x in j.get("references", []) if x.get("cited_text")]
    print(f"ANSWER: {(j.get('answer') or '')[:600]}")
    print("NEW VERBATIM SPANS:")
    for qq in quotes:
        print(f"  [n{qq['n']}] {qq['cited_text']}")
    ledger = _ledger()
    props = {p["prop_id"]: p for p in ledger["paragraphs"][para]["propositions"]}
    props[prop_id]["verification"].setdefault("requery", []).append(
        {"query": q, "answer": j.get("answer", ""), "quotes": quotes})
    _save(ledger)
    commit(f"verify(2.1/{para}): requery {prop_id} for a clean verbatim span")
    return quotes


def record_verdicts(para, verdicts):
    """Record/refresh human-adjudicated verdicts + notes only (no pins, no NLM call)."""
    ledger = _ledger()
    props = {p["prop_id"]: p for p in ledger["paragraphs"][para]["propositions"]}
    for pid, (verdict, note) in verdicts.items():
        props[pid]["verification"]["verdict"] = verdict
        props[pid]["verification"]["verdict_note"] = note
    _save(ledger)
    commit(f"verify(2.1/{para}): refresh verdict notes (no re-pin)")
    print("  verdict notes refreshed; committed")


def audit(para):
    """Substring-audit: is each located (answer) quote inside a verbatim cited_text span?
    Match-rate = verbatim-confidence. <100% on a decisive quote -> pin it."""
    ledger = _ledger()
    for p in ledger["paragraphs"][para]["propositions"]:
        v = p.get("verification", {})
        spans = [q.get("cited_text") or "" for q in v.get("quotes", [])]
        loc = v.get("located", [])
        hits = 0
        print(f"\n{p['prop_id']}: {len(spans)} verbatim spans, {len(loc)} located")
        for entry in loc:
            q = entry.get("quote", "")
            m = any(q in s for s in spans)
            hits += int(m)
            print(f"  {'OK  ' if m else 'MISS'} p.{entry.get('page')}  {q[:64]!r}")
        print(f"  -> {hits}/{len(loc)} located quotes lie inside a verbatim span")


def show(para):
    """Print each prop's verdict, NLM answer (context), verbatim cited_text spans,
    located answer-quotes (page/section), and span_pins WITH their pin-answers -- the
    full evidence record for verdict review. E3.5: ONLY cited_text spans are admissible;
    a span_pin's page is answer-sourced (NOT an independent verbatim guarantee)."""
    ledger = _ledger()
    for p in ledger["paragraphs"][para]["propositions"]:
        v = p.get("verification", {})
        if not (v.get("quotes") or v.get("answer") or v.get("span_pins")):
            continue
        print(f"\n===== {p['prop_id']}  [verdict: {v.get('verdict')}] =====")
        print(f"ANSWER (NON-evidence): {(v.get('answer') or '')[:600]}")
        print("VERBATIM SPANS (admissible cited_text):")
        for q in v.get("quotes", []):
            ct = (q.get("cited_text") or "").strip()
            if ct:
                print(f"  [n{q.get('n')}] {ct}")
        loc = v.get("located", [])
        if loc:
            print("LOCATED (answer-quote -> page):")
            for L in loc:
                print(f"  p.{L.get('page')} | {(L.get('quote') or '')[:100]}")
        for sp in v.get("span_pins", []):
            print(f"PIN phrase={sp.get('phrase')!r} -> page={sp.get('page')} sec={sp.get('section')}")
            print(f"  PIN-ANSWER: {(sp.get('answer') or '')[:280]}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "show":
        show(sys.argv[2])
    else:
        # Self-test: resolve every registered paper, print the map, exit on any problem.
        require(list(SOURCES.keys()))
        print("\nAll registered sources resolved cleanly.")
