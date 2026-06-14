#!/usr/bin/env python3
"""Bib-metadata IDENTITY verification (convention: NLM -> ledger; NLM_QUERY_GUIDE.md S4).

A successful CONTENT query verifies a paper's CLAIM; it does NOT verify the typed
bibitem strings -- it NAMES the authors from our own bib (guide S2). To recover/confirm
the title-page authorship/title/journal/year, run the S4 self-identity query (the source
states ITS OWN identity, non-leading) and persist it into the relevant subsection ledger.

Scope (user, 2026-06-14): keown1981 only -- fix its missing author initials.
Verifies: author / title / journal / year. NOT volume/pages (no in-channel authority).

Auth: requires a live `notebooklm login` (token expires across sessions). Resumable:
skips a key already captured. Verdict is HUMAN (guide S9) -- recorded separately after review.

  python docs/Thesis/rewrite/nlm_bib_identity.py            # identity capture -> ledger
  python docs/Thesis/rewrite/nlm_bib_identity.py --show
"""
import argparse
import json
import sys

import nlm_common as C

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LEDGER = C.LEDGER  # docs/Thesis/rewrite/section2.1_paragraph_ledger.json (Keown lives in 2.1, P6.3)
TARGETS = ["keown1981"]

# S4 identity query: non-leading, "this source" (do NOT name the paper -> would be leading).
# Ask for FULL author names/initials as printed, to recover the bib's missing initials.
IDENTITY_Q = (C.PREFIX + "this source: state ONLY the exact title; the authors "
              "(list every author, with full first names or initials exactly as printed on "
              "the document); the journal or working-paper series; and the year of this "
              "document. Do not infer beyond what the document itself states.")


def capture():
    resolved = C.require(TARGETS)                       # fail-closed (auth/resolve)
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    bid = ledger.setdefault("bib_identity", {})
    for key in TARGETS:
        if bid.get(key, {}).get("answer"):
            print(f"{key}: already captured -- skip (delete its entry to redo).")
            continue
        sid, title = resolved[key]
        print(f"{key}: NLM identity query -> {title[:55]}", flush=True)
        try:
            C.run([C.EXE, "clear"], 60)
        except Exception:
            pass
        out = C.run([C.EXE, "ask", "-n", C.NOTEBOOK, "-s", sid, "--json", IDENTITY_Q], 420).stdout or ""
        i = out.find("{")
        j = json.loads(out[i:]) if i >= 0 else {"answer": "", "references": []}
        quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
                   "start_char": x.get("start_char"), "end_char": x.get("end_char"),
                   "chunk_id": x.get("chunk_id")}
                  for x in j.get("references", []) if x.get("cited_text")]
        bid[key] = {"method": "NLM-identity", "source": {"id": sid, "title": title},
                    "query": IDENTITY_Q, "answer": j.get("answer", ""),
                    "quotes": quotes, "verdict": "PENDING"}
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
        C.commit(f"verify(2.1/bib): {key} NLM identity -> ledger ({len(quotes)} spans)")
        print(f"  ANSWER: {(j.get('answer') or '')[:400]}")
        for q in quotes:
            ct = (q.get("cited_text") or "").strip()
            if ct:
                print(f"  [n{q.get('n')}] {ct[:160]}")
        print("  committed.")


def show():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    for key, rec in ledger.get("bib_identity", {}).items():
        print(f"\n===== {key} [verdict: {rec.get('verdict')}] =====")
        print(f"ANSWER: {rec.get('answer', '')}")
        for q in rec.get("quotes", []):
            ct = (q.get("cited_text") or "").strip()
            if ct:
                print(f"  [n{q.get('n')}] {ct}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--verdict", nargs=2, metavar=("KEY", "VERDICT"),
                    help="record a HUMAN-adjudicated verdict for a bib_identity key (guide S9)")
    ap.add_argument("--note", default="", help="verdict note")
    a = ap.parse_args()
    if a.show:
        show()
    elif a.verdict:
        key, verdict = a.verdict
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        ledger["bib_identity"][key]["verdict"] = verdict
        ledger["bib_identity"][key]["verdict_note"] = a.note
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
        C.commit(f"verify(2.1/bib): {key} verdict {verdict}")
        print(f"recorded {key} -> {verdict}")
    else:
        if not C.EXE:
            raise SystemExit("notebooklm CLI not found on PATH; run `notebooklm login` first.")
        capture()
