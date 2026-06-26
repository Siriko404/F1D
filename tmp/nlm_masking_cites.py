#!/usr/bin/env python3
"""PLANNING-mode NLM verification for the 2 NEW masking-pillar cites.

The cloned 2.1 ledger does not exist yet, so per NLM_QUERY_GUIDE.md §14 we capture
verbatim evidence to a durable tmp json (committed per query), to be folded into the
ledger when it is built. Reuses the proven engine helpers (ask/run/LOC) from
nlm_common -- does NOT touch the LOCKED section2.1 ledger.

Papers (ids resolved from `source list`, identity-CONFIRMED via --identity before content):
  shleifer_vishny2003  -> the currency/misvaluation MOTIVE
  louis2004            -> acquirers overstate earnings shortly BEFORE a stock-swap (BEHAVIOR)

Modes:
  python tmp/nlm_masking_cites.py --identity   # §4 self-identity (cheap; before content quota)
  python tmp/nlm_masking_cites.py              # content capture -> tmp json -> commit (resumable)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # F1D-phase3/tmp
FORK = HERE.parents[0]                                  # F1D-phase3
sys.path.insert(0, str(FORK / "docs" / "Thesis" / "rewrite"))
import nlm_common as C                                  # ask / run / LOC / EXE / NOTEBOOK / PREFIX / LOCATOR

OUT = HERE / "nlm_masking_cites.json"

# id = resolved from source list (created 2026-06-26); identity-confirm via --identity BEFORE content.
PAPERS = {
    "shleifer_vishny2003": {
        "id": "f649faef-2fdd-4d68-be04-517447533345",
        "label": '"Stock Market Driven Acquisitions" by Shleifer and Vishny (2003, Journal of Financial Economics)',
        "question": ("what does it conclude about whether acquiring firms use overvalued equity (their own stock) "
                     "as the medium of payment in acquisitions, and whether the relative stock-market valuations of "
                     "the acquirer and the target drive the choice between stock and cash as the method of payment?"),
    },
    "louis2004": {
        "id": "8ed79bba-379c-457f-a87d-e34ca0c27099",
        "label": '"Earnings Management and the Market Performance of Acquiring Firms" by Louis (2004, Journal of Financial Economics)',
        "question": ("what does it find about whether acquiring firms overstate or manage their reported earnings "
                     "in the period shortly before announcing a stock-for-stock (stock-financed) acquisition, and "
                     "what it reports about the timing of any such earnings management relative to the announcement?"),
    },
}


def git(*a):
    subprocess.run(["git", *a], cwd=str(FORK), capture_output=True, text=True)


def identity():
    """§4: ask each source to state its OWN identity (non-leading). Confirm before content quota."""
    for k, p in PAPERS.items():
        q = (C.PREFIX + "this source: state ONLY the exact title, the authors, the journal or working-paper "
             "series, and the year of this document. Do not infer beyond what the document states.")
        try:
            C.run([C.EXE, "clear"], 60)
        except Exception:
            pass
        out = C.run([C.EXE, "ask", "-n", C.NOTEBOOK, "-s", p["id"], "--json", q], 420).stdout or ""
        i = out.find("{")
        ans = json.loads(out[i:]).get("answer", "") if i >= 0 else ""
        print(f"\n===== {k}  (id {p['id']}) =====\n{ans[:700]}")


def capture():
    """Atomic, non-leading, single-source content query + LOCATOR -> verbatim spans + page/section -> tmp json."""
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for k, p in PAPERS.items():
        if data.get(k, {}).get("quotes"):
            print(f"{k}: already captured -- skip (delete its quotes to redo).")
            continue
        print(f"{k}: querying NLM -> {p['id']}", flush=True)
        q, j = C.ask(p["id"], p["label"], p["question"])
        answer = j.get("answer", "")
        quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
                   "start_char": x.get("start_char"), "end_char": x.get("end_char"),
                   "chunk_id": x.get("chunk_id")}
                  for x in j.get("references", []) if x.get("cited_text")]
        located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(), "section": m.group(3).strip()}
                   for m in C.LOC.finditer(answer)]
        data[k] = {"id": p["id"], "label": p["label"], "query": q, "answer": answer,
                   "quotes": quotes, "located": located, "verdict": "PENDING"}
        OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        git("add", str(OUT))
        git("commit", "-m", f"verify(masking-cite): {k} NLM answer -> tmp ({len(quotes)} quotes, {len(located)} located)")
        print(f"  wrote {len(quotes)} verbatim quotes, {len(located)} located; committed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true", help="§4 self-identity check (before content quota)")
    args = ap.parse_args()
    if not C.EXE:
        sys.exit("ERROR: notebooklm CLI not found on PATH. Run `notebooklm login`.")
    identity() if args.identity else capture()
