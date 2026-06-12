#!/usr/bin/env python3
"""NLM verification for Section 2.1, paragraph P2 -- one pass, one purpose.

Same proven pattern as nlm_p1.py (see docs/Thesis/rewrite/NLM_QUERY_GUIDE.md):
for each P2 proposition, query the notebook scoped to the ONE named paper, atomic
and non-leading, asking NLM to report each supporting quote's page and section;
write the answer (full answer + verbatim cited_text spans + page/section located
quotes) DIRECTLY into the ledger; git commit. No intermediate files.

Run:  python docs/Thesis/rewrite/nlm_p2.py            # capture answers -> ledger
      python docs/Thesis/rewrite/nlm_p2.py --finalize # pin decisive spans + verdicts
"""
import argparse
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
PARA = "P2"
NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")
PREFIX = "Reading only this paper, "
LOCATOR = (" For each sentence you quote in support, report the exact page number "
           "printed in the paper and the section (heading or number) where it appears.")

# prop_id -> (paper named in the query,
#             fixed source_id (when the filename can't be substring-resolved) or None,
#             [title-substring candidates] used only when fixed_id is None,
#             atomic non-leading question)
P2 = {
    # Matsumoto is in the notebook under the opaque, DUPLICATED EBSCO filename
    # 'EBSCO-FullText-06_12_2026.pdf' (uploaded twice) -- no substring resolves it, so we pin
    # the exact source_id, VERIFIED via an NLM identity query (title/authors/journal/year =
    # Matsumoto, Pronk & Roelofsen 2011, The Accounting Review). Newest of the two copies.
    "P2.1": ('"What Makes Conference Calls Useful? The Information Content of Managers\' '
             'Presentations and Analysts\' Discussion Sessions" by Matsumoto, Pronk and '
             'Roelofsen (2011, The Accounting Review)',
             "a1dacc9f-2bee-46ba-9261-496fd687c8e6", None,
             "does it reach a conclusion about whether the analysts' discussion "
             "(question-and-answer) portion of a conference call carries information content "
             "beyond the managers' presentation portion, and which of the two portions it "
             "finds more informative?"),
    "P2.2": ('"When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks" '
             'by Loughran and McDonald (2011, Journal of Finance)',
             None, ["loughran", "liability not a liability", "when is a liability", "01625", "10625"],
             "what does it conclude about whether word lists developed outside of finance "
             "misclassify words when applied to financial text, and does it construct "
             "finance-specific word lists -- including a category capturing uncertainty -- "
             "for classifying financial disclosures?"),
}

# NLM lists each supporting quote (under the LOCATOR clause) as:
#     "quoted sentence ..."   **Page:** 1383   **Section:** I. Introduction
LOC = re.compile(r'"([^"]{20,}?)"[\s\S]{0,120}?\*\*Page:\*\*[ \t]*([^\n]+?)[ \t]*\n'
                 r'[\s\S]{0,60}?\*\*Section:\*\*[ \t]*([^\n]+)')


def run(args, timeout):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def _sources():
    """Parsed notebook source list; fail with a clear message on auth-expiry/error dict."""
    out = run([EXE, "source", "list", "-n", NOTEBOOK, "--json"], 120).stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit("ERROR: could not list notebook sources (no JSON returned).")
    obj = json.loads(out[i:])
    if obj.get("error"):
        sys.exit(f"ERROR: NLM source list failed -- {obj.get('message', 'unknown error')}")
    return obj.get("sources", [])


def source_by_id(sid):
    """Resolve a known (verified) source_id -> (id, title)."""
    for s in _sources():
        if s["id"] == sid:
            return sid, s["title"]
    sys.exit(f"ERROR: source id {sid} not found in notebook.")


def source_id_multi(candidates):
    """First notebook source whose title contains any candidate substring -> (id, title)."""
    srcs = _sources()
    for c in candidates:
        for s in srcs:
            if c.lower() in s["title"].lower():
                return s["id"], s["title"]
    sys.exit(f"ERROR: no notebook source matches any of {candidates} -- check the uploaded title.")


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
    run(["git", "add", str(LEDGER), str(Path(__file__))], 60)
    run(["git", "commit", "-m", message], 60)


def page_section(answer):
    p = re.search(r"\*\*Page:\*\*[ \t]*([^\n*]+)", answer or "")
    s = re.search(r"\*\*Section:\*\*[ \t]*([^\n*]+)", answer or "")
    return (p.group(1).strip() if p else None), (s.group(1).strip() if s else None)


def run_content():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    props = {p["prop_id"]: p for p in ledger["paragraphs"][PARA]["propositions"]}
    for pid, (paper, fixed_id, cands, question) in P2.items():
        if props[pid].get("verification", {}).get("quotes"):
            print(f"{pid}: already captured -- skipped (delete its quotes to redo).")
            continue
        sid, title = source_by_id(fixed_id) if fixed_id else source_id_multi(cands)
        print(f"{pid}: querying NLM -> {title}", flush=True)
        query, j = ask(sid, paper, question)
        answer = j.get("answer", "")
        quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
                   "start_char": x.get("start_char"), "end_char": x.get("end_char"),
                   "chunk_id": x.get("chunk_id")}
                  for x in j.get("references", []) if x.get("cited_text")]
        located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(),
                    "section": m.group(3).strip()} for m in LOC.finditer(answer)]
        props[pid]["verification"] = {
            "method": "NLM", "source": {"id": sid, "title": title}, "query": query,
            "answer": answer, "quotes": quotes, "located": located, "verdict": "PENDING",
        }
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
        commit(f"verify(2.1/P2): {pid} NLM answer -> ledger ({len(quotes)} quotes, {len(located)} located)")
        print(f"  wrote {len(quotes)} verbatim quotes, {len(located)} located; committed")


# --- finalize: POPULATED AFTER reviewing captured spans (substring-audit). For each
#     decisive answer-only quote, one targeted page-pin call; then record the
#     human-adjudicated verdicts. Filled once run_content output is seen.
# (prop_id, fixed source_id or None, [candidates] or None, paper label, decisive verbatim sentence)
PINS = [
    ("P2.1", "a1dacc9f-2bee-46ba-9261-496fd687c8e6", None,
     '"What Makes Conference Calls Useful? The Information Content of Managers\' '
     'Presentations and Analysts\' Discussion Sessions" by Matsumoto, Pronk and '
     'Roelofsen (2011, The Accounting Review)',
     "We find that both presentations and discussions are incrementally informative, but "
     "that discussion periods have greater information content than presentations."),
]
VERDICTS = {
    "P2.1": ("SUPPORTED",
             "Matsumoto, Pronk & Roelofsen (2011): the analysts' discussion (Q&A) segment "
             "carries information content incremental to the managers' presentation, and is "
             "MORE informative than the presentation. Verbatim fragment n6 ('...in the case of "
             "the discussion, over information released...') + the decisive conclusion sentence "
             "round-trip pinned (span_pin, p.1411 VI. Conclusion); empirical result at p.1396 IV."),
    "P2.2": ("SUPPORTED",
             "Loughran & McDonald (2011): word lists from other disciplines misclassify "
             "financial text -- 73.8% of Harvard 'negative' words are not negative in finance "
             "(verbatim span n4, p.36) and 'high misclassification rate and spurious correlations' "
             "(verbatim span n3, p.62 V. Conclusions); LM build finance-specific lists INCLUDING "
             "uncertainty (verbatim span n6, p.37), and the Fin-Unc uncertainty list = 285 words "
             "(verbatim span n8, p.45 III. Textual Analysis and Word Lists). Instrument provenance "
             "bulletproof; 'uncertainty is informative' rides as bonus per design (verdict does not "
             "hinge on it). Decisive spans are themselves verbatim -- no pin needed."),
}


def finalize():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    props = {p["prop_id"]: p for p in ledger["paragraphs"][PARA]["propositions"]}
    for prop_id, fixed_id, cands, label, phrase in PINS:
        sid, title = source_by_id(fixed_id) if fixed_id else source_id_multi(cands)
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
            {"phrase": phrase, "page": page, "section": section, "query": q, "answer": j.get("answer", "")})
        print(f"  {prop_id} -> Page {page}, Section {section}")
    for pid, (verdict, note) in VERDICTS.items():
        props[pid]["verification"]["verdict"] = verdict
        props[pid]["verification"]["verdict_note"] = note
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
    commit(f"verify(2.1/{PARA}): pin decisive spans; record verdicts")
    print("  verdicts recorded; committed")


def audit():
    """Substring-audit: is each located (answer) quote contained in a verbatim cited_text
    span? Prints per-prop match-rate so a decisive answer-only quote is pinned, not trusted.
    NB: this located<-span rate UNDERSTATES strength when a verbatim span is itself decisive
    (then no located round-trip is needed -- read the spans directly)."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    for p in ledger["paragraphs"][PARA]["propositions"]:
        v = p.get("verification", {})
        spans = [q.get("cited_text") or "" for q in v.get("quotes", [])]
        loc = v.get("located", [])
        hits = 0
        print(f"\n{p['prop_id']}: {len(spans)} verbatim spans, {len(loc)} located")
        for L in loc:
            q = L.get("quote", "")
            m = any(q in s for s in spans)
            hits += int(m)
            print(f"  {'OK  ' if m else 'MISS'} p.{L.get('page')}  {q[:72]!r}")
        print(f"  -> {hits}/{len(loc)} located quotes lie inside a verbatim span")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true",
                    help="substring-audit: located (answer) quotes vs verbatim cited_text spans")
    ap.add_argument("--finalize", action="store_true",
                    help="pin decisive answer-only spans and record adjudicated verdicts")
    args = ap.parse_args()
    if args.audit:
        audit()
        return
    if not EXE:
        sys.exit("ERROR: `notebooklm` CLI not found on PATH. Run `notebooklm login` first.")
    if args.finalize:
        finalize()
    else:
        run_content()


if __name__ == "__main__":
    main()
