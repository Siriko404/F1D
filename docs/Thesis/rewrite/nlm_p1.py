#!/usr/bin/env python3
"""NLM verification for Section 2.1, paragraph P1 -- one pass, one purpose.

For each P1 proposition verified through NLM, this script:
  1. queries the notebook -- scoped to the one named paper, atomic and non-leading,
     and asking NLM to report the page number and section of every supporting quote;
  2. writes the answer DIRECTLY into the ledger (the full answer, the verbatim
     quotes with their char-span/chunk, and the page+section located quotes);
  3. git commits.
No intermediate files, no extra modes. Run:  python docs/Thesis/rewrite/nlm_p1.py
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
NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")
PREFIX = "Reading only this paper, "
LOCATOR = (" For each sentence you quote in support, report the exact page number "
           "printed in the paper and the section (heading or number) where it appears.")

# P1's NLM propositions: prop_id -> (paper named in the query,
#                                    title substring that finds its notebook source,
#                                    atomic non-leading question)
P1 = {
    "P1.1": ('"Discretionary Disclosure" by Verrecchia (1983, Journal of Accounting and Economics)',
             "0165410183900113",
             "under what conditions, if any, does it conclude that a manager who possesses "
             "private information will choose not to disclose that information?"),
    "P1.2": ('"Disclosure of Nonproprietary Information" by Dye (1985, Journal of Accounting Research)',
             "dye-disclosurenonproprietary",
             "what determines whether a manager discloses or withholds the information it may "
             "have, and what role does the possibility that the manager is uninformed play in "
             "sustaining non-disclosure?"),
}

# NLM lists each supporting quote (under the LOCATOR clause) as:
#     "quoted sentence ..."   **Page:** 182   **Section:** 1. Introduction
LOC = re.compile(r'"([^"]{20,}?)"[\s\S]{0,120}?\*\*Page:\*\*[ \t]*([^\n]+?)[ \t]*\n'
                 r'[\s\S]{0,60}?\*\*Section:\*\*[ \t]*([^\n]+)')


def run(args, timeout):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def source_id(match):
    """Find the notebook source whose title contains `match`; return (id, title)."""
    out = run([EXE, "source", "list", "-n", NOTEBOOK, "--json"], 120).stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit("ERROR: could not list notebook sources.")
    for s in json.loads(out[i:])["sources"]:
        if match.lower() in s["title"].lower():
            return s["id"], s["title"]
    sys.exit(f"ERROR: no notebook source matches '{match}'.")


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


# --- finalize step: pin the one decisive verbatim span that lacks a page, and
#     record the adjudicated verdicts (both SUPPORTED by guaranteed-verbatim spans).
DYE_LABEL = P1["P1.2"][0]
DYE_PIN_PHRASE = ("a policy of complete disclosure corresponds to x = 0, which (as was "
                  "noted above) does not satisfy (2), and is hence not an equilibrium")
VERDICTS = {
    "P1.1": ("SUPPORTED",
             "Verbatim spans n=5/n=6/n=8: an informed manager withholds below a threshold when a "
             "proprietary (disclosure) cost exists (p.182 §1; p.190 §4; p.192 §5)."),
    "P1.2": ("SUPPORTED",
             "Verbatim span n=8 ('a policy of complete disclosure ... is hence not an equilibrium') "
             "+ n=4 (manager informed only with prob (1-p)): non-disclosure is sustained because "
             "investors cannot tell an uninformed manager from one withholding."),
}


def page_section(answer):
    p = re.search(r"\*\*Page:\*\*[ \t]*([^\n*]+)", answer or "")
    s = re.search(r"\*\*Section:\*\*[ \t]*([^\n*]+)", answer or "")
    return (p.group(1).strip() if p else None), (s.group(1).strip() if s else None)


def run_content():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    props = {p["prop_id"]: p for p in ledger["paragraphs"]["P1"]["propositions"]}
    for pid, (paper, match, question) in P1.items():
        if props[pid].get("verification", {}).get("quotes"):
            print(f"{pid}: already captured -- skipped (delete its verification to redo).")
            continue
        sid, title = source_id(match)
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
        commit(f"verify(2.1/P1): {pid} NLM answer -> ledger ({len(quotes)} quotes, {len(located)} located)")
        print(f"  wrote {len(quotes)} verbatim quotes, {len(located)} located; committed")


def finalize():
    """One targeted NLM call to pin the decisive Dye verbatim span's page+section,
    then record both adjudicated verdicts. Writes to ledger and commits."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    props = {p["prop_id"]: p for p in ledger["paragraphs"]["P1"]["propositions"]}
    sid, title = source_id("dye-disclosurenonproprietary")
    q = (f"{PREFIX}{DYE_LABEL}: on what page (the page number printed in the paper) and in which "
         f'section does this exact sentence appear? Report **Page:** and **Section:**. Sentence: '
         f'"{DYE_PIN_PHRASE}"')
    print("pinning Dye decisive span (page+section) ...", flush=True)
    try:
        run([EXE, "clear"], 60)
    except Exception:
        pass
    out = run([EXE, "ask", "-n", NOTEBOOK, "-s", sid, "--json", q], 420).stdout or ""
    i = out.find("{")
    j = json.loads(out[i:]) if i >= 0 else {"answer": ""}
    page, section = page_section(j.get("answer", ""))
    props["P1.2"]["verification"]["span_pin"] = {
        "phrase": DYE_PIN_PHRASE, "page": page, "section": section,
        "query": q, "answer": j.get("answer", ""),
    }
    print(f"  Dye decisive span -> Page {page}, Section {section}")
    for pid, (verdict, note) in VERDICTS.items():
        props[pid]["verification"]["verdict"] = verdict
        props[pid]["verification"]["verdict_note"] = note
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
    commit("verify(2.1/P1): pin Dye decisive-span page+section; record P1.1/P1.2 SUPPORTED")
    print("  verdicts P1.1/P1.2 = SUPPORTED; committed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--finalize", action="store_true",
                    help="pin the Dye decisive-span page+section and record verdicts")
    args = ap.parse_args()
    if not EXE:
        sys.exit("ERROR: `notebooklm` CLI not found on PATH. Run `notebooklm login` first.")
    if args.finalize:
        finalize()
    else:
        run_content()


if __name__ == "__main__":
    main()
